
from maya.cmds import *

import re
import maya.cmds as cmd

from zooPy import events
from zooPy import typeFactories

import melUtils
import apiExtensions
from cmdStrResolver import resolve

mel = melUtils.mel

eventManager = events.EventManager()

#listen to these events to act on load/unload events.  A boolean argument is passed to callbacks when triggered.  True
#when triggered has been loaded, False when it has been unloaded
#example:
#def informUserIfUnloaded( state ):
#	if not state: print "TRIGGERED HAS BEEN UNLOADED!"
#eventManager.addCallback( EVT_LOAD_STATE_CHANGE, informUserIfUnloaded )
EVT_LOAD_STATE_CHANGE = eventManager.createEventId()


class Trigger(object):
	'''
	provides an interface to a trigger item
	'''
	INVALID = '<invalid connect>'
	DEFAULT_MENU_NAME = '<empty>'
	DEFAULT_CMD_STR = '//write trigger cmd here'

	PRESET_SELECT_CONNECTED = "select -d #;\nselect -add @;"
	PRESET_KEY_CONNECTED = "select -d #;\nsetKeyframe @;"
	PRESET_TOGGLE_CONNECTED = "string $sel[] = `ls -sl`;\nint $vis = !`getAttr %1.v`;\nfor($obj in @) setAttr ($obj +\".v\") $vis;\nif( `size $sel` ) select $sel;"
	PRESET_TOOL_TO_MOVE = "setToolTo $gMove;"
	PRESET_TOOL_TO_ROTATE = "setToolTo $gRotate;"

	def __init__( self, obj ):
		if isinstance( obj, Trigger ):
			obj = obj.obj

		self.obj = obj
	@classmethod
	def CreateTrigger( cls, object, cmdStr=DEFAULT_CMD_STR, connects=None ):
		'''
		creates a trigger and returns a new trigger instance
		'''
		new = cls(object)
		new.setCmd(cmdStr)

		if connects:
			for c in connects:
				new.connect( str( c ) )

		return new
	@classmethod
	def CreateMenu( cls, object, name=DEFAULT_MENU_NAME, cmdStr=DEFAULT_CMD_STR, slot=None ):
		'''
		creates a new menu (optionally forces it to a given slot) and returns a new trigger instance
		'''
		new = cls(object)
		new.setMenuInfo(slot, name, cmdStr)

		return new
	@classmethod
	def All( cls, selectCmds=True, menuCmds=False ):
		triggers = set()
		if selectCmds:
			attrpaths = cmd.ls( '*.zooTrigCmd0' ) or []
			for attrpath in attrpaths:
				triggers.add( attrpath.split('.')[0] )

		if menuCmds:
			transforms = cmd.ls( type='transform' )
			for transform in transforms:
				if transform in triggers:
					continue

				for attr in cmd.listAttr( transform, ud=True ) or []:
					if attr.startswith( 'zooCmd' ):
						triggers.add( transform )

		return [ cls( t ) for t in triggers ]
	def __str__( self ):
		return str( self.obj )
	def __eq__( self, other ):
		return self.obj == other.obj
	def __ne__( self, other ):
		return not self.__eq__( other )
	def __unicode__( self ):
		return unicode( self.obj )
	def __repr__( self ):
		return repr( self.__unicode__() )
	def __getitem__( self, slot ):
		'''
		returns the connect at index <slot>
		'''
		if slot == 0: return self.obj

		slotPrefix = 'zooTrig'
		attrPath = "%s.zooTrig%d" % ( self.obj, slot )
		try:
			objPath = cmd.connectionInfo( attrPath, sfd=True )
			if objPath: return objPath.split('.')[0]
		except TypeError:
			#in this case there is no attribute - so pass and look to the connect cache
			pass

		attrPathCached = "%scache" % attrPath
		try:
			obj = cmd.getAttr( attrPathCached )
			if cmd.objExists(obj): return obj
		except TypeError: pass

		raise IndexError('no such connect exists')
	def __len__( self ):
		'''
		returns the number of connects
		'''
		return len(self.connects())
	def iterConnects( self ):
		'''
		iterator that returns connectObj, connectIdx
		'''
		return iter( self.connects()[1:] )
	def iterMenus( self, resolve=False ):
		'''
		iterator that returns slot, name, cmd
		'''
		return iter( self.menus(resolve) )
	def getCmd( self, resolve=False, optionals=[] ):
		attrPath = '%s.zooTrigCmd0' % self.obj
		if objExists( attrPath  ):
			cmdStr = cmd.getAttr(attrPath)
			if resolve: return self.resolve(cmdStr,optionals)
			return cmdStr
		return None
	def setCmd( self, cmdStr=DEFAULT_CMD_STR ):
		cmdAttr = "zooTrigCmd0"
		if not objExists( "%s.%s" % ( self.obj, cmdAttr ) ):
			cmd.addAttr(self.obj, ln=cmdAttr, dt="string")

		if not cmdStr:
			cmd.deleteAttr(self.obj, at=cmdAttr)
			return

		cmd.setAttr('%s.%s' % ( self.obj, cmdAttr ), cmdStr, type='string')
	def getMenuCmd( self, slot, resolve=False ):
		cmdInfo = cmd.getAttr( "%s.zooCmd%d" % ( self.obj, slot ) ) or ''
		idx = cmdInfo.find('^')
		if resolve: return self.resolve(cmdInfo[idx+1:])
		return cmdInfo[idx+1:]
	def setMenuCmd( self, slot, cmdStr ):
		newCmdInfo = '%s^%s' % ( self.getMenuName(slot), cmdStr )
		cmd.setAttr("%s.zooCmd%d" % ( self.obj, slot ), newCmdInfo, type='string')
	def setMenuInfo( self, slot=None, name=DEFAULT_MENU_NAME, cmdStr=DEFAULT_CMD_STR ):
		'''
		sets both the name and the command of a given menu item.  if slot is None, then a new slot will be
		created and its values set accordingly
		'''
		if slot is None: slot = self.nextMenuSlot()
		if name == '': name = self.DEFAULT_MENU_NAME

		#try to add the attr - if this complains then we already have the attribute...
		try: cmd.addAttr(self.obj, ln='zooCmd%d' % slot, dt='string')
		except RuntimeError: pass

		cmd.setAttr("%s.zooCmd%d" % ( self.obj, slot ), '%s^%s' % (name, cmdStr), type='string')

		self.setKillState( True )

		return slot
	def createMenu( self, name=DEFAULT_MENU_NAME, cmdStr=DEFAULT_CMD_STR ):
		return self.setMenuInfo( None, name, cmdStr )
	def getMenuName( self, slot ):
		cmdInfo = cmd.getAttr( "%s.zooCmd%d" % ( self.obj, slot ) ) or ''
		idx = cmdInfo.find('^')

		return cmdInfo[:idx]
	def setMenuName( self, slot, name ):
		newCmdInfo = '%s^%s' % ( name, self.getMenuCmd(slot) )
		cmd.setAttr("%s.zooCmd%d" % ( self.obj, slot ), newCmdInfo, type='string')
	def getMenuInfo( self, slot, resolve=False ):
		cmdInfo = cmd.getAttr( "%s.zooCmd%d" % ( self.obj, slot ) ) or ''
		idx = cmdInfo.find('^')
		if resolve: return cmdInfo[:idx],self.resolve(cmdInfo[idx+1:])
		return cmdInfo[:idx],cmdInfo[idx+1:]
	def menus( self, resolve=False ):
		'''
		returns a list of tuples containing the slot,name,cmdStr for all menus on the trigger.  if resolve
		is True, then all menu commands are returned with their symbols resolved
		'''
		attrs = cmd.listAttr(self.obj,ud=True)
		slotPrefix = 'zooCmd'
		prefixSize = len(slotPrefix)
		data = []

		if attrs is None:
			return data

		for attr in attrs:
			try: slot = attr[prefixSize:]
			except IndexError: continue

			if attr.startswith(slotPrefix) and slot.isdigit():
				menuData = cmd.getAttr('%s.%s' % (self.obj,attr)) or ''
				idx = menuData.find('^')
				menuName = menuData[:idx]
				menuCmd = menuData[idx+1:]
				if resolve: menuCmd = self.resolve(menuCmd)
				data.append( ( int(slot), menuName, menuCmd ) )

		data.sort()

		return data
	def connects( self ):
		'''
		returns a list of tuples with the format: (nodeName,connectIdx)
		'''
		connects = [(self.obj,0)]
		attrs = cmd.listAttr(self.obj, ud=True) or []
		slotPrefix = 'zooTrig'
		prefixSize = len(slotPrefix)

		#so go through the attributes and make sure they're triggered attributes
		for attr in attrs:
			try: slot = attr[prefixSize:]
			except IndexError: continue

			if attr.startswith(slotPrefix) and slot.isdigit():
				slot = int(slot)

				#now that we've determined its a triggered attribute, trace the connect if it exists
				objPath = cmd.connectionInfo( "%s.%s" % ( self.obj, attr ), sfd=True )

				#append the object name to the connects list and early out
				if objExists(objPath):
					connects.append( (objPath.split('.')[0],slot) )
					continue

				#if there is no connect, then check to see if there is a name cache, and query it - no need to
				#check for its existence as we're already in a try block and catching the appropriate exception
				#should the attribute not exist...
				cacheAttrpath = "%s.%s%dcache" % ( self.obj, slotPrefix, slot )
				if objExists( cacheAttrpath ):
					cacheValue = cmd.getAttr( cacheAttrpath )
					if objExists( cacheValue ):
						self.connect( cacheValue, slot )  #add the object to the connect slot
						connects.append( (cacheValue, slot) )

		return connects
	def listAllConnectSlots( self, connects=None, emptyValue=None ):
		'''
		returns a non-sparse list of connects - unlike the connects method output, this is just a list of
		names.  slots that have no connect attached to them have <emptyValue> as their value
		'''
		if connects is None:
			connects = self.connects()

		#build the non-sparse connects list -first we need to find the largest connect idx, and then build a non-sparse list
		biggest = max( [c[1] for c in connects] ) + 1
		newConnects = [emptyValue]*biggest
		for name, idx in connects:
			newConnects[idx] = str( name )

		return newConnects
	def getConnectSlots( self, obj ):
		'''
		return a list of the connect slot indicies the given obj is connected to
		'''
		if apiExtensions.cmpNodes( self.obj, obj ):
			return [0]

		conPrefix = 'zooTrig'
		prefixSize = len( conPrefix )

		slots = set()

		connections = cmd.listConnections( obj +'.msg', s=False, p=True ) or []
		for con in connections:
			obj, attr = con.split('.')
			if not apiExtensions.cmpNodes( obj, self.obj ):
				continue

			slot = attr[ prefixSize: ]
			if attr.startswith(conPrefix) and slot.isdigit():
				slots.add( int(slot) )

		#we need to check against all the cache attributes to see if the object exists but has been disconnected somehow
		allSlots = self.connects()
		getAttr = cmd.getAttr
		for connect, slot in allSlots:
			cacheAttrpath = '%s.%s%dcache' % (self.obj, conPrefix, slot)
			if objExists( cacheAttrpath ):
				cacheValue = getAttr( cacheAttrpath )
				if cacheValue == obj:
					slots.add( slot )

		slots = list( slots )
		slots.sort()

		return slots
	def isConnected( self, object ):
		'''
		returns whether a given <object> is connected as a connect to this trigger
		'''
		object = str( object )
		if not objExists(object):
			return []

		conPrefix = 'zooTrig'
		cons = listConnections( '%s.message' % object, s=False, p=True ) or []
		for con in cons:
			splits = con.split( '.' )
			obj = splits[0]
			if obj == self.obj:
				if splits[1].startswith( conPrefix ):
					return True

		return False
	def connect( self, obj, slot=None ):
		'''
		performs the actual connection of an object to a connect slot
		'''
		if not cmd.objExists(obj):
			return -1

		#if the user is trying to connect the trigger to itself, return zero which is the reserved slot for the trigger
		if apiExtensions.cmpNodes( self.obj, obj ):
			return 0

		if slot is None:
			slot = self.nextSlot()

		if slot <= 0:
			return 0

		#make sure the connect isn't already connected - if it is, return the slot number
		existingSlots = self.isConnected(obj)
		if existingSlots:
			return self.getConnectSlots(obj)[0]

		conPrefix = 'zooTrig'
		prefixSize = len(conPrefix)

		slotPath = "%s.%s%d" % (self.obj, conPrefix, slot)
		if not objExists( slotPath ):
			cmd.addAttr(self.obj,ln= "%s%d" % (conPrefix, slot), at='message')

		cmd.connectAttr( "%s.msg" % obj, slotPath, f=True )
		self.cacheConnect( slot )

		return slot
	def disconnect( self, objectOrSlot ):
		'''
		removes either the specified object from all slots it is connected to, or deletes the given slot index
		'''
		if isinstance(objectOrSlot,basestring):
			slots = self.getConnectSlots(objectOrSlot)
			for slot in slots:
				try: cmd.deleteAttr( '%s.zooTrig%d' % ( self.obj, slot ))
				except TypeError: pass

				try: cmd.deleteAttr( '%s.zooTrig%dcache' % ( self.obj, slot ))
				except TypeError: pass
		elif isinstance(objectOrSlot,(int,float)):
			try: cmd.deleteAttr( '%s.zooTrig%d' % ( self.obj, int(objectOrSlot) ))
			except TypeError: pass

			try: cmd.deleteAttr( '%s.zooTrig%dcache' % ( self.obj, int(objectOrSlot) ))
			except TypeError: pass
	def resolve( self, cmdStr, optionals=[] ):
		return resolve( cmdStr, self.obj, self.listAllConnectSlots( emptyValue=self.INVALID ), optionals )
	def unresolve( self, cmdStr, optionals=[] ):
		'''
		given a cmdStr this method will go through it looking to resolve any names into connect tokens.  it only looks
		for single cmd tokens and optionals - it doesn't attempt to unresolve arrays
		'''
		connects = self.connects()

		for connect,idx in connects:
			connectRE = re.compile( r'([^a-zA-Z_|]+)(%s)([^a-zA-Z0-9_|]+)' % connect.replace('|','\\|') )
			def tmp(match):
				start,middle,end = match.groups()
				return '%s%s%d%s' % (start,'%',idx,end)
			cmdStr = connectRE.sub(tmp,cmdStr)

		return cmdStr
	def replaceConnectToken( self, cmdStr, searchReplaceDict ):
		'''
		returns a resolved cmd string.  the cmd string can be either passed in, or if you specify the slot number
		the the cmd string will be taken as the given slot's menu command
		'''
		if cmdStr is None:
			return None

		cmdStr = cmdStr.replace( '#', '%0' )

		#replace with a temporary token - the reason is for the cases like this:
		#replaceConnectToken( "%1 %2 %3", {1:3, 3:2} )
		#the 1 will get replaced by a 3, but when the 3 is replaced there will be two occurances...  so by using an
		#intermediate token we can stop this from happening...
		connectRE = re.compile( '%([0-9]+)([^0-9])' )
		def tokenRep( matchobj ):
			idx,trailingChar = matchobj.groups()
			idx = int( idx )
			if idx in searchReplaceDict:
				return '%%!%s%s' % ( searchReplaceDict[idx], trailingChar )
			return '%%%s%s' % ( idx, trailingChar )

		cmdStr = connectRE.sub(tokenRep,cmdStr)

		#replace the temporary tokens with the real ones
		connectRE = re.compile( '%!([0-9]+)([^0-9])' )
		def tokenRep( matchobj ):
			connectIdx,trailingChar = matchobj.groups()
			return '%%%s%s' % ( connectIdx, trailingChar )

		cmdStr = connectRE.sub(tokenRep,cmdStr)

		#finally, replace %0 with # symbols
		connectRE = re.compile( '%([0]+)([^0-9])' )
		def tokenRep( matchobj ):
			_,trailingChar = matchobj.groups()
			return '#%s' % trailingChar

		return connectRE.sub(tokenRep,cmdStr)
	def replaceConnectInCmd( self, searchReplaceDict ):
		cmdStr = self.getCmd()
		if cmdStr:
			self.setCmd( self.replaceConnectToken( cmdStr, searchReplaceDict ) )
	def replaceConnectInMenuCmd( self, slot, searchReplaceDict ):
		newCmdStr = self.replaceConnectToken( self.getMenuCmd(slot), searchReplaceDict )
		self.setMenuCmd( slot, newCmdStr )
	def replaceConnectInMenuCmds( self, searchReplaceDict ):
		for menuIdx, _n, _c in self.menus():
			self.replaceConnectInMenuCmd( menuIdx, searchReplaceDict )
	def getConnectsUsedByCmd( self, cmdStr ):
		'''
		returns the connect indices that get used by the given command string
		'''
		connectsInCmd = []
		if cmdStr is not None:
			cmdStr = cmdStr.replace( '#', '%0' )
			connectRE = re.compile( '%([0-9]+)[^0-9]' )
			s = connectRE.findall( cmdStr )
			if s:
				connectsInCmd = sorted( set( map( int, s ) ) )

		return connectsInCmd
	def scrub( self, cmdStr ):
		'''
		will scrub any lines that contain invalid connects from the cmdStr
		'''
		#so build the set of missing connects
		allSlots = self.listAllConnectSlots(emptyValue=None)
		numAllSlots = len(allSlots)
		missingSlots = set( [idx for idx,val in enumerate(allSlots) if val is None] )

		#now build the list of connect tokens used in the cmd and compare it with the connects
		#that are valid - in the situation where there are connects in the cmdStr that don't
		#exist on the trigger, we want to scrub these
		singleRE = re.compile('%([0-9]+)')
		subArrayRE = re.compile('@([0-9]+),(-*[0-9]+)')

		nonexistantSlots = set( map(int, singleRE.findall(cmdStr)) )
		for start,end in subArrayRE.findall(cmdStr):
			start = int(start)
			end = int(end)
			if end < 0: end += numAllSlots
			else: end += 1
			[nonexistantSlots.add(slot) for slot in xrange( start, end )]

		[nonexistantSlots.discard( slot ) for slot,connect in enumerate(allSlots)]
		missingSlots = missingSlots.union( nonexistantSlots )  #now add the nonexistantSlots to the missingSlots

		#early out if we can
		if not missingSlots: return cmdStr

		#otherwise iterate over the list of slots and remove any line that has that slot token in it
		for slot in missingSlots:
			missingRE = re.compile(r'''^(.*)(%-*'''+ str(slot) +')([^0-9].*)$\n',re.MULTILINE)
			cmdStr = missingRE.sub('',cmdStr)

		def replaceSubArray( matchObj ):
			junk1,start,end,junk2 = matchObj.groups()
			start = int(start)
			end = int(end)
			if end<0: end = start+end
			else: end += 1
			subArrayNums = set(range(start,end))
			common = subArrayNums.intersection( missingSlots )
			if common: return ''
			return matchObj.string[matchObj.start():matchObj.end()]

		subArrayRE = re.compile('^(.*@)([0-9]+),(-*[0-9]+)([^0-9].*)$\n',re.MULTILINE)
		cmdStr = subArrayRE.sub(replaceSubArray,cmdStr)

		return cmdStr
	def scrubCmd( self ):
		'''
		convenience method for performing self.scrub on the trigger command
		'''
		self.setCmd( self.scrub( self.getCmd() ))
	def scrubMenuCmd( self, slot ):
		'''
		convenience method for performing self.scrub on a given menu command
		'''
		self.setMenuCmd(slot, self.scrub( self.getMenuCmd(slot) ))
	def scrubMenuCmds( self ):
		'''
		convenience method for performing self.scrub on all menu commands
		'''
		for slot,name,cmdStr in self.menus(): self.scrubMenuCmd(slot)
	def collapseMenuCmd( self, slot ):
		'''
		resolves a menu item's command string and writes it back to the menu item - this is most useful when connects are being re-shuffled
		and you don't want to have to re-write command strings.  there is the counter function - uncollapseMenuCmd that undoes the results
		'''
		self.setMenuCmd(slot, self.getMenuCmd(slot,True) )
	def uncollapseMenuCmd( self, slot ):
		self.setMenuCmd(slot, self.unresolve( self.getMenuCmd(slot) ) )
	def eval( self, cmdStr, optionals=[] ):
		return mel.eval( self.resolve(cmdStr,optionals) )
	def evalCmd( self ):
		return self.eval( self.getCmd() )
	def evalMenu( self, slot ):
		return self.eval( self.getMenuCmd(slot) )
	def evalCareful( self, cmdStr, optionals=[] ):
		'''
		does an eval on a line by line basis, catching errors as they happen - its most useful for
		when you have large cmdStrs with only a small number of errors
		'''
		lines = cmdStr.split('\n')
		evalMethod = mel.eval
		validLines = []

		for line in lines:
			try:
				cmd.select(cl=True)  #selection is cleared so any missing connects don't work on selection instead of specified objects
				resolvedLine = self.resolve(line,optionals)
				evalMethod(resolvedLine)
			except RuntimeError: continue
			validLines.append( line )
		return '\n'.join(validLines)
	def evalForConnectsOnly( self, cmdStr, connectIdxs, optionals=[] ):
		'''
		will do an eval only if one of the connects in the given a list of connects is contained
		in the command string
		'''
		return self.eval( self.filterConnects( cmdStr, connectIdxs ), optionals )
	def trigger( self ):
		cmdStr = self.getCmd( True )
		if cmdStr is None:
			return

		try:
			self.eval( cmdStr )
		except:
			print "ERROR: executing triggered! command on %s" % self.obj
	def filterConnects( self, cmdStr, connectIdxs ):
		'''
		will return the lines of a command string that refer to connects contained in the given list
		'''
		connectIdxs = set(connectIdxs)

		allSlots = self.listAllConnectSlots(emptyValue=None)
		numAllSlots = len(allSlots)
		lines = cmdStr.split('\n')
		singleRE = re.compile('%([0-9]+)')
		subArrayRE = re.compile('@([0-9]+),(-*[0-9]+)')

		validLines = []
		for line in lines:
			#are there any singles in the line?
			singles = set( map(int, singleRE.findall(line)) )
			if connectIdxs.intersection(singles):
				validLines.append(line)
				continue

			#check if there are any sub arrays which span the any of the connects?
			subArrays = subArrayRE.findall(line)
			for sub in subArrays:
				start = int(sub[0])
				end = int(sub[1])
				if end < 0: end += numAllSlots
				else: end += 1
				subRange = set( range(start,end) )
				if connectIdxs.intersection(subRange):
					validLines.append(line)
					break

			#finally check to see if there are any single array tokens - these are always added
			#NOTE: this check needs to happen AFTER the subarray check - at least in its current state - simply because its such a simple (ie fast) test
			if line.find('@') >= 0:
				validLines.append(line)
				continue

		return '\n'.join(validLines)
	def removeCmd( self, removeConnects=False ):
		'''
		removes the triggered cmd from self - can optionally remove all the connects as well
		'''
		try:
			#catches the case where there is no trigger cmd...  faster than a object existence test
			cmd.deleteAttr( '%s.zooTrigCmd0' % self.obj )
			if removeConnects:
				for connect,slot in self.connects():
					self.disconnect(slot)
		except TypeError: pass
	def removeMenu( self, slot, removeConnects=False ):
		'''
		removes a given menu slot - if removeConnects is True, all connects will be removed ONLY if there are no other menu cmds
		'''
		attrpath = '%s.zooCmd%d' % ( self.obj, slot )
		try:
			cmd.deleteAttr( '%s.zooCmd%d' % ( self.obj, slot ))
			if removeConnects and not self.menus():
				for connect,slot in self.connects():
					self.disconnect(slot)
		except TypeError: pass
	def removeAll( self, removeConnects=False ):
		'''
		removes all triggered data from self
		'''
		self.removeCmd(removeConnects)
		for idx,name,cmd in self.menus():
			self.removeMenu(idx)
	def nextSlot( self ):
		'''
		returns the first available slot index
		'''
		slots = self.listAllConnectSlots(emptyValue=None)
		unused = [con for con,obj in enumerate(slots) if obj is None]
		next = 1

		if unused: return unused[0]
		elif slots: return len(slots)

		return next
	def nextMenuSlot( self ):
		'''
		returns the first available menu slot index
		'''
		slots = self.menus()
		next = 0

		if slots: return slots[-1][0] + 1
		return next
	def cacheConnect( self, slot ):
		'''caches the objectname of a slot connection'''
		try: connectName = self[ slot ]
		except IndexError: return None

		slotPrefix = 'zooTrig'
		cacheAttrName = '%s%dcache' % ( slotPrefix, slot )
		cacheAttrPath = '%s.%s' % ( self.obj, cacheAttrName )

		if not cmd.objExists( cacheAttrPath ):
			cmd.addAttr( self.obj, ln=cacheAttrName, dt='string' )

		cmd.setAttr( cacheAttrPath, connectName, type='string' )
	def validateConnects( self ):
		'''
		connects maintain a cache which "remembers" the last object that was plugged into them.  this method will
		run over all connects and for those unconnected ones, it will look for the object that it USED to be connected to
		and connect it, and for those that ARE connected, it will make sure the cache is valid.  the cache can become
		invalid if a connected object's name changes after it was connected
		'''
		slotPrefix = 'zooTrig'

		for connect,slot in self.iterConnects():
			attrpath = '%s.%s%d' % ( self.obj, slotPrefix, slot )
			objPath = cmd.connectionInfo(attrpath, sfd=True)
			if not cmd.objExists( objPath ):
				#get the cached connect and attach it
				cachedValue = cmd.getAttr('%scache' % attrpath)
				if cmd.objExists(cachedValue):
					self.connect(cachedValue,slot)
	def setKillState( self, state ):
		'''so the kill state tells the objMenu build script to stop after its build all menu items listed on the object - this method
		provides an interface to enabling/disabling that setting'''
		attr = 'zooObjMenuDie'
		attrpath = '%s.%s' % ( self.obj, attr )
		if state:
			if not objExists( attrpath ): cmd.addAttr(self.obj, at="bool", ln=attr)
			cmd.setAttr(attrpath, 1)
		else:
			if objExists( attrpath ):
				cmd.deleteAttr(attrpath)
	def getKillState( self ):
		attrpath = "%s.zooObjMenuDie" % self.obj
		if objExists( attrpath ): return bool( cmd.getAttr(attrpath) )

		return False
	killState = property(getKillState,setKillState)
	def getConnectIndiciesForObjects( self, objects=None ):
		'''
		returns a list of connection indicies for the given list of objects
		'''
		if objects is None: objects = cmd.ls(sl=True)
		cons = []
		for obj in objects:
			cons.extend( self.getConnectSlots(obj) )

		return cons


def setKillState( obj, state ):
	return Trigger( obj ).setKillState( state )


def getKillState( obj ):
	return Trigger( obj ).getKillState()


class Triggered(object):
	__metaclass__ = typeFactories.SingletonType

	def __init__( self ):
		self._jobId = None
	def load( self ):
		if self._jobId is None:
			self._jobId = cmd.scriptJob( cu=True, e=('SelectionChanged', self.triggerSelection) )
			eventManager.triggerEvent( EVT_LOAD_STATE_CHANGE, True )
	def unload( self ):
		if self._jobId is not None:
			cmd.scriptJob( k=self._jobId )
			self._jobId = None
			eventManager.triggerEvent( EVT_LOAD_STATE_CHANGE, False )
	def state( self ):
		return self._jobId is not None
	def triggerSelection( self ):
		'''
		this proc is fired off when the selection is changed - it basically just sets off the triggers for each object in
		the trigger list
		'''
		sel = cmd.ls( sl=True )
		highlight = cmd.optionVar( q='zooTrigHighlighting' )

		for a in sel:
			#make sure the current object isn't an attribute, or a component
			if '.' in a or '[' in a:
				continue

			trigger = Trigger( a )
			trigger.trigger()

			if highlight:
				self.highlightConnectedTriggers( trigger )
	def highlightConnectedTriggers( self, trigger ):
		for nodeName, connectIdx in trigger.connects():
			self.highlightTrigger( nodeName )
	def _setHighlightValues( self, node, oe, oc ):
		attrpath = '%s.overrideEnabled' % node
		if cmd.getAttr( attrpath, se=True ):
			try: cmd.setAttr( attrpath, 1 )
			except: pass

		attrpath = '%s.overrideColor' % node
		if cmd.getAttr( attrpath, se=True ):
			try: cmd.setAttr( attrpath, 17 )
			except: pass
	def highlightTrigger( self, node ):
		self._setHighlightValues( node, 1, 17 )
	def unhighlightTrigger( self, node ):
		self._setHighlightValues( node, 0, 17 )
	def unhighlightAllTriggers( self ):
		for trigger in Trigger.All():
			self.unhighlightTrigger( trigger )


#end
