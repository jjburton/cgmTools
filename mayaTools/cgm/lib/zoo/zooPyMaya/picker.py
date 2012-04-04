
from __future__ import with_statement

import re

from maya import mel
from maya.cmds import *

from zooPy import names
from zooPy import colours

from zooPy import presets
from zooPy.path import Path
from zooPy.vectors import Vector, Colour

from baseMelUI import *
from melUtils import printErrorStr, printWarningStr
from mayaDecorators import d_unifyUndo
from apiExtensions import asMObject, sortByHierarchy
from cmdStrResolver import resolve
from triggered import Trigger

import presetsUI

eval = __builtins__[ 'eval' ]  #otherwise this gets clobbered by the eval in maya.cmds

TOOL_NAME = 'zooPicker'
TOOL_EXTENSION = presets.DEFAULT_XTN
TOOL_CMD_EXTENSION = 'cmdPreset'
VERSION = 0

MODIFIERS = SHIFT, CAPS, CTRL, ALT = 2**0, 2**1, 2**2, 2**3
ADDITIVE = CTRL | SHIFT


def isValidMayaNodeName( theStr ):
	validChars = 'abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
	for char in theStr:
		if char not in validChars:
			return False

	return True


def getLabelWidth( theString ):
	'''
	some guestimate code to determine the width of a given string when displayed as
	text on a ButtonUI instance
	'''
	wideLetters = 'abcdeghkmnopqrsuvwxyz_ '

	width = 0
	for char in theString:
		if char in wideLetters:
			width += 7
		else:
			width += 3

	return width


def removeRefEdits( objs, cmd=None ):
	'''
	removes reference edits from a list of objects.  if the $cmd arg is an empty string
	then ALL commands are removed.  if $cmd is a valid reference edit command, only those
	commands are removed from the list of objects supplied
	'''
	refNodeLoadStateDict = {}
	for obj in objs:
		if referenceQuery( obj, inr=True ):
			refNode = referenceQuery( obj, rfn=True )
			loadState = bool( referenceQuery( refNode, n=True ) )
			refNodeLoadStateDict[ refNode ] = loadState

	#now unload all references so we can remove edits
	for node in refNodeLoadStateDict:
		file( unloadReference=node )

	#remove failed edits
	for obj in objs:
		referenceEdit( obj, failedEdits=True, successfulEdits=False, removeEdits=True )

	#remove specified edits for the objects
	for obj in objs:
		if cmd is None:
			referenceEdit( obj, failedEdits=True, successfulEdits=True, removeEdits=True )
		else:
			referenceEdit( obj, failedEdits=True, successfulEdits=True, editCommand=cmd, removeEdits=True )

	#now set the refs to their initial load state
	for node, loadState in refNodeLoadStateDict.iteritems():
		if loadState:
			file( loadReference=node )

	select( objs )


def getTopPickerSet():
	existing = [ node for node in ls( type='objectSet', r=True ) or [] if sets( node, q=True, text=True ) == TOOL_NAME ]

	if existing:
		return existing[ 0 ]
	else:
		pickerNode = createNode( 'objectSet', n='picker' )
		sets( pickerNode, e=True, text=TOOL_NAME )

		return pickerNode


class Button(object):
	'''
	A Button instance is a "container" for a button within a picker.  To instantiate a button you need to pass the set node
	that contains the button data.  You can create a new set node using Button.Create.

	A button, when pressed, by default selects the contents of the set based on the keyboard modifiers pressed.  But a button
	can also define its own press command.  Button press commands are stored on the cmdStr string attribute on the set node
	and can be most easily edited using the editor tab created by the PickerLayout UI.
	'''

	SELECTION_STATES = NONE, PARTIAL, COMPLETE = range( 3 )
	CMD_MODES = MODE_SELECTION_FIRST, MODE_CMD_FIRST, MODE_CMD_ONLY = range( 3 )
	CMD_MODES_NAMES = 'selection first', 'cmd first', 'cmd only'
	MIN_SIZE, MAX_SIZE = 5, 100
	DEFAULT_SIZE = 14, 14
	DEFAULT_COLOUR = tuple( Colour( (0.25, 0.25, 0.3) ).asRGB() )
	AUTO_COLOUR = None
	COLOUR_PARTIAL, COLOUR_COMPLETE = (1, 0.6, 0.5), Colour( 'white' ).asRGB()

	DEFAULT_ATTRS = ( { 'ln': 'posSize', 'dt': 'string' },  #stuff pos and size into a single str attr - so lazy...
	                  { 'ln': 'colour', 'dt': 'string' },
	                  { 'ln': 'label', 'dt': 'string' },
	                  { 'ln': 'cmdStr', 'dt': 'string' },
	                  { 'ln': 'cmdIsPython', 'at': 'bool', 'dv': False },
	                  { 'ln': 'cmdMode', 'at': 'enum', 'enumName': ':'.join( CMD_MODES_NAMES ), 'dv': MODE_SELECTION_FIRST }
	                  )

	@classmethod
	def Create( cls, character, pos, size=DEFAULT_SIZE, colour=AUTO_COLOUR, label=None, objs=(), cmdStr=None, cmdIsPython=False ):
		node = sets( em=True, text='zooPickerButton' )
		sets( node, e=True, add=character.getNode() )

		cls.ValidateNode( node )

		self = cls( node )
		self.setPosSize( pos, size )
		self.setLabel( label )
		self.setObjs( objs )
		self.setCmdStr( cmdStr )
		self.setCmdIsPython( cmdIsPython )

		#if the colour is set to "AUTO_COLOUR" then try to determine the button colour based off the object's colour
		if colour is cls.AUTO_COLOUR:
			self.setColour( cls.DEFAULT_COLOUR )
			self.setAutoColour()
		else:
			self.setColour( colour )

		return self
	@classmethod
	def ValidateNode( cls, node ):
		for addAttrKw in cls.DEFAULT_ATTRS:
			if not objExists( '%s.%s' % (node, addAttrKw[ 'ln' ]) ):
				addAttr( node, **addAttrKw )

	def __init__( self, node ):
		self.__node = asMObject( node )
	def __repr__( self ):
		return "%s( '%s' )" % (type( self ).__name__, self.getNode())
	__str__ = __repr__
	def __eq__( self, other ):
		'''
		two buttons are equal on if all their attributes are the same
		'''
		return self.getCharacter() == other.getCharacter() and \
		       self.getPos() == other.getPos() and \
		       self.getSize() == other.getSize() and \
		       self.getColour() == other.getColour() and \
		       self.getLabel() == other.getLabel() and \
		       self.getObjs() == other.getObjs() and \
		       self.getCmdStr() == other.getCmdStr() and \
		       self.getCmdIsPython() == other.getCmdIsPython()
	def __ne__( self, other ):
		return not self.__eq__( other )
	def __hash__( self ):
		return hash( self.getNode() )
	def getNode( self ):
		return unicode( self.__node )
	def getCharacter( self ):
		cons = listConnections( self.getNode(), type='objectSet', s=False )
		if cons:
			return Character( cons[0] )
	def getPosSize( self ):
		valStr = getAttr( '%s.posSize' % self.getNode() )
		if valStr is None:
			return Vector( (0,0,0) ), self.DEFAULT_SIZE

		posStr, sizeStr = valStr.split( ';' )

		pos = Vector( [ int( p ) for p in posStr.split( ',' ) ] )
		size = Vector( [ int( p ) for p in sizeStr.split( ',' ) ] )

		return pos, size
	def getPos( self ): return self.getPosSize()[0]
	def getSize( self ): return self.getPosSize()[1]
	def getColour( self ):
		rgbStr = getAttr( '%s.colour' % self.getNode() )
		if rgbStr is None:
			return self.DEFAULT_COLOUR

		rgb = rgbStr.split( ',' )
		rgb = map( float, rgb )

		return Colour( rgb )
	def getLabel( self ):
		return getAttr( '%s.label' % self.getNode() )
	def getNiceLabel( self ):
		labelStr = self.getLabel()

		#if there is no label AND the button has objects, communicate this to the user
		if not labelStr:
			if len( self.getObjs() ) > 1:
				return '+'

		return labelStr
	def getObjs( self ):
		return sets( self.getNode(), q=True ) or []
	def getCmdStr( self ): return getAttr( '%s.cmdStr' % self.getNode() )
	def getCmdIsPython( self ): return getAttr( '%s.cmdIsPython' % self.getNode() )
	def getCmdMode( self ):
		try:
			return getAttr( '%s.cmdMode' % self.getNode() )
		except TypeError:
			self.ValidateNode( self.getNode() )

			return getAttr( '%s.cmdMode' % self.getNode() )
	def getResolvedCmdStr( self ):
		cmdStr = self.getCmdStr()
		if self.getCmdIsPython():
			return cmdStr % locals()
		else:
			return resolve( cmdStr, self.getNode(), self.getObjs() )
	def setPosSize( self, pos, size ):

		#make sure the pos/size values are ints...
		pos = map( int, map( round, pos ) )
		size = map( int, map( round, size ) )

		posStr = ','.join( map( str, pos ) )
		sizeStr = ','.join( map( str, size ) )

		valStr = setAttr( '%s.posSize' % self.getNode(), '%s;%s' % (posStr, sizeStr), type='string' )
	def setPos( self, val ):
		if not isinstance( val, Vector ):
			val = Vector( val )

		p, s = self.getPosSize()
		self.setPosSize( val, s )
	def setSize( self, val ):
		if not isinstance( val, Vector ):
			val = Vector( val )

		p, s = self.getPosSize()
		self.setPosSize( p, val )
	def setColour( self, val ):
		if val is None:
			val = self.DEFAULT_COLOUR

		valStr = ','.join( map( str, val ) )
		setAttr( '%s.colour' % self.getNode(), valStr, type='string' )
	def setLabel( self, val ):
		if val is None:
			val = ''

		setAttr( '%s.label' % self.getNode(), val, type='string' )

		#rename the node to reflect the label
		try:
			if val and isValidMayaNodeName( val ):
				rename( self.getNode(), val )
			else:
				objs = self.getObjs()
				if objs:
					rename( self.getNode(), '%s_picker' % objs[0] )
				else:
					rename( self.getNode(), 'picker' )

		#this generally happens if the node is referenced...  its no big deal if the rename fails - renaming just happens to make the sets slightly more comprehendible when outliner surfing
		except RuntimeError: pass
	def setObjs( self, val ):
		if isinstance( val, basestring ):
			val = [ val ]

		if not val:
			return

		sets( e=True, clear=self.getNode() )
		sets( val, e=True, add=self.getNode() )
	def setCmdStr( self, val ):
		if val is None:
			val = ''

		setAttr( '%s.cmdStr' % self.getNode(), val, type='string' )
	def setCmdIsPython( self, val ):
		setAttr( '%s.cmdIsPython' % self.getNode(), val )
	def setCmdMode( self, val ):
		setAttr( '%s.cmdMode' % self.getNode(), val )
	def setAutoColour( self, defaultColour=None ):
		objs = self.getObjs()
		for obj in objs:
			colour = colours.getObjColour( obj )
			if colour:
				self.setColour( colour )
				return

		if defaultColour is not None:
			self.setColour( defaultColour )
	def select( self, forceModifiers=None, executeCmd=True ):
		'''
		this is what happens when a user "clicks" or "selects" this button.  It handles executing the button
		command in the desired order and handling object selection
		'''
		cmdMode = self.getCmdMode()

		#if we're executing the command only, execute it and bail
		if cmdMode == self.MODE_CMD_ONLY:
			if executeCmd:
				self.executeCmd()
				return

		#if we're executing the command first - do it
		if cmdMode == self.MODE_CMD_FIRST:
			if executeCmd:
				self.executeCmd()

		if forceModifiers is None:
			mods = getModifiers()
		else:
			mods = forceModifiers

		objs = self.getObjs()
		if objs:
			if mods & SHIFT and mods & CTRL:
				select( objs, add=True )
			elif mods & SHIFT:
				select( objs, toggle=True )
			elif mods & CTRL:
				select( objs, deselect=True )
			else:
				select( objs )

		if cmdMode == self.MODE_SELECTION_FIRST:
			if executeCmd:
				self.executeCmd()
	def selectedState( self ):
		'''
		returns whether this button is partially or fully selected - return values are one of the
		values in self.SELECTION_STATES
		'''
		objs = self.getObjs()
		sel = ls( objs, sl=True )

		if not sel:
			return self.NONE
		elif len( objs ) == len( sel ):
			return self.COMPLETE

		return self.PARTIAL
	def moveBy( self, offset ):
		pos = self.getPos()
		self.setPos( pos + offset )
	def exists( self ):
		return objExists( self.getNode() )
	def isEmpty( self ):
		return not bool( self.getObjs() )
	def executeCmd( self ):
		'''
		executes the command string for this button
		'''
		cmdStr = self.getResolvedCmdStr()
		if cmdStr:
			try:
				if self.getCmdIsPython():
					return eval( cmdStr )
				else:
					return maya.mel.eval( "{%s;}" % cmdStr )
			except:
				printErrorStr( 'Executing command "%s" on button "%s"' % (cmdStr, self.getNode()) )
	def duplicate( self ):
		dupe = self.Create( self.getCharacter(), self.getPos(), self.getSize(),
		                    self.getColour(), self.getLabel(), self.getObjs(),
		                    self.getCmdStr(), self.getCmdIsPython() )

		return dupe
	def mirrorObjs( self ):
		'''
		replaces the objects in this button with their name based opposites - ie if this button contained the
		object ctrl_L, this method would replace the objects with ctrl_R.  It uses names.swapParity
		'''
		oppositeObjs = []
		for obj in self.getObjs():
			opposite = names.swapParity( obj )
			if opposite:
				oppositeObjs.append( opposite )

		self.setObjs( oppositeObjs )
	def delete( self ):
		delete( self.getNode() )


class Character(object):
	'''
	A Character is made up of many Button instances to select the controls or groups of controls that
	comprise a puppet rig.  A Character is also stored as a set node in the scene.  New Character nodes
	can be created using Character.Create, or existing ones instantiated by passing the set node to
	Character.
	'''

	DEFAULT_BG_IMAGE = 'pickerGrid.bmp'

	@classmethod
	def IterAll( cls ):
		for node in ls( type='objectSet' ):
			if sets( node, q=True, text=True ) == 'zooPickerCharacter':
				yield cls( node )
	@classmethod
	def Create( cls, name ):
		'''
		creates a new character for the picker tool
		'''
		node = sets( em=True, text='zooPickerCharacter' )
		node = rename( node, name )

		sets( node, e=True, add=getTopPickerSet() )

		addAttr( node, ln='version', at='long' )
		addAttr( node, ln='name', dt='string' )
		addAttr( node, ln='bgImage', dt='string' )
		addAttr( node, ln='bgColour', dt='string' )
		addAttr( node, ln='filepath', dt='string' )

		setAttr( '%s.version' % node, VERSION )
		setAttr( '%s.name' % node, name, type='string' )
		setAttr( '%s.bgImage' % node, cls.DEFAULT_BG_IMAGE, type='string' )
		setAttr( '%s.bgColour' % node, '0,0,0', type='string' )

		#lock the node - this stops maya from auto-deleting it if all buttons are removed
		lockNode( node )

		self = cls( node )
		allButton = self.createButton( (5, 5), (25, 14), (1, 0.65, 0.25), 'all', [], '%(self)s.getCharacter().selectAllButtonObjs()', True )

		return self

	def __init__( self, node ):
		self.__node = asMObject( node )
	def __repr__( self ):
		return "%s( '%s' )" % (type( self ).__name__, self.getNode())
	__str__ = __repr__
	def __eq__( self, other ):
		return self.getNode() == other.getNode()
	def __ne__( self, other ):
		return not self.__eq__( other )
	def getNode( self ):
		return unicode( self.__node )
	def getButtons( self ):
		buttonNodes = sets( self.getNode(), q=True ) or []

		return [ Button( node ) for node in buttonNodes ]
	def getName( self ):
		return getAttr( '%s.name' % self.getNode() )
	def getBgImage( self ):
		return getAttr( '%s.bgImage' % self.getNode() )
	def getBgColour( self ):
		colStr = getAttr( '%s.bgColour' % self.getNode() )

		return Colour( [ float( c ) for c in colStr.split( ',' ) ] ).asRGB()
	def getFilepath( self ):
		return getAttr( '%s.filepath' % self.getNode() )
	def setName( self, val ):
		setAttr( '%s.name' % self.getNode(), str( val ), type='string' )
		lockNode( self.getNode(), lock=False )
		rename( self.getNode(), val )
		lockNode( self.getNode(), lock=True )
	def setBgImage( self, val ):
		setAttr( '%s.bgImage' % self.getNode(), val, type='string' )
	def setBgColour( self, val ):
		valStr = ','.join( map( str, val ) )
		setAttr( '%s.bgColour' % self.getNode(), valStr, type='string' )
	def setFilepath( self, filepath ):
		setAttr( '%s.filepath' % self.getNode(), filepath, type='string' )
	def createButton( self, pos, size, colour=None, label=None, objs=(), cmdStr=None, cmdIsPython=False ):
		'''
		appends a new button to the character - a new Button instance is returned
		'''
		return Button.Create( self, pos, size, colour, label, objs, cmdStr, cmdIsPython )
	def removeButton( self, button, delete=True ):
		'''
		given a Button instance, will remove it from the character
		'''
		for aButton in self.getButtons():
			if button == aButton:
				sets( button.getNode(), e=True, remove=self.getNode() )
				if delete:
					button.delete()

				return
	def breakoutButton( self, button, direction, padding=5, colour=None ):
		'''
		doing a "breakout" on a button will basically take each object in the button and
		create a new button for it in the given direction
		'''
		buttonPos, buttonSize = button.getPosSize()
		colour = button.getColour()

		posIncrement = Vector( direction ).normalize()
		posIncrement[0] *= buttonSize[0] + padding
		posIncrement[1] *= buttonSize[1] + padding

		newButtons = []
		objs = button.getObjs()

		#figure out which axis to use to sort the objects - basically figure out which axis has the highest delta between smallest and largest
		posObjs = [ (Vector( xform( obj, q=True, ws=True, rp=True ) ), obj) for obj in objs ]
		bestDelta, bestSorting = 0, []
		for n in range( 3 ):
			sortedByN = [ (objPos[n], obj) for objPos, obj in posObjs ]
			sortedByN.sort()
			delta = abs( sortedByN[-1][0] - sortedByN[0][0] )
			if delta > bestDelta:
				bestDelta, bestSorting = delta, sortedByN

		#now we've figured out which axis is the most appropriate axis and have the best sorting, build the buttons
		objs = [ obj for objPosN, obj in bestSorting ]

		#if the direction is positive (which is down the screen in the picker), then we want to breakout the buttons in ascending hierarchical fashion
		ascending = True
		if direction[0] < 0 or direction[1] < 0:
			ascending = False

		if ascending:
			objs.reverse()

		for obj in objs:
			buttonPos += posIncrement
			button = self.createButton( buttonPos, buttonSize, objs=[ obj ] )
			button.setAutoColour( colour )
			newButtons.append( button )

		return newButtons
	def selectAllButtonObjs( self ):
		for button in self.getButtons():
			button.select( ADDITIVE, False )
	def isEmpty( self ):
		if objExists( self.getNode() ):
			return not self.getButtons()

		return False
	def delete( self ):
		for button in self.getButtons():
			button.delete()

		node = self.getNode()
		lockNode( node, lock=False )
		delete( node )
	def saveToPreset( self, filepath ):
		'''
		stores this picker character out to disk
		'''
		filepath = Path( filepath )
		if filepath.exists():
			filepath.editoradd()

		with open( filepath, 'w' ) as fOpen:
			infoDict = {}
			infoDict[ 'version' ] = VERSION
			infoDict[ 'name' ] = self.getName()
			infoDict[ 'bgImage' ] = self.getBgImage() or ''
			infoDict[ 'bgColour' ] = tuple( self.getBgColour() )
			fOpen.write( str( infoDict ) )
			fOpen.write( '\n' )

			#the preset just needs to contain a list of buttons
			for button in self.getButtons():
				buttonDict = {}
				pos, size = button.getPosSize()
				buttonDict[ 'pos' ] = tuple( pos )
				buttonDict[ 'size' ] = tuple( size )
				buttonDict[ 'colour' ] = tuple( button.getColour() )
				buttonDict[ 'label' ] = button.getLabel()
				buttonDict[ 'objs' ] = button.getObjs()
				buttonDict[ 'cmdStr' ] = button.getCmdStr()
				buttonDict[ 'cmdIsPython' ] = button.getCmdIsPython()
				buttonDict[ 'cmdMode' ] = button.getCmdMode()

				fOpen.write( str( buttonDict ) )
				fOpen.write( '\n' )

		#store the filepath on the character node
		self.setFilepath( filepath.unresolved() )

	@classmethod
	def LoadFromPreset( cls, filepath, namespaceHint=None ):
		'''
		'''
		filepath = Path( filepath )

		#make sure the namespaceHint - if we have one - doesn't end in a semi-colon
		if namespaceHint:
			if namespaceHint.endswith( ':' ):
				namespaceHint = namespaceHint[ :-1 ]

		buttonDicts = []
		with open( filepath ) as fOpen:
			lineIter = iter( fOpen )
			try:
				infoLine = lineIter.next()
				infoDict = eval( infoLine.strip() )
				while True:
					buttonLine = lineIter.next()
					buttonDict = eval( buttonLine.strip() )
					buttonDicts.append( buttonDict )
			except StopIteration: pass

		version = infoDict.pop( 'version', 0 )

		newCharacter = cls.Create( infoDict.pop( 'name', 'A Picker' ) )
		newCharacter.setBgImage( infoDict.pop( 'bgImage', cls.DEFAULT_BG_IMAGE ) )
		newCharacter.setBgColour( infoDict.pop( 'bgColour', (0, 0, 0) ) )

		#if there is still data in the infoDict print a warning - perhaps new data was written to the file that was handled when loading the preset?
		if infoDict:
			printWarningStr( 'Not all info was loaded from %s on to the character: %s still remains un-handled' % (filepath, infoDict) )

		for buttonDict in buttonDicts:
			newButton = Button.Create( newCharacter, buttonDict.pop( 'pos' ),
			                           buttonDict.pop( 'size' ),
			                           buttonDict.pop( 'colour', Button.DEFAULT_COLOUR ),
			                           buttonDict.pop( 'label', '' ) )

			newButton.setCmdStr( buttonDict.pop( 'cmdStr', '' ) )
			newButton.setCmdIsPython( buttonDict.pop( 'cmdIsPython', False ) )
			newButton.setCmdMode( buttonDict.pop( 'cmdMode', Button.MODE_SELECTION_FIRST ) )

			#now handle objects - this is about the only tricky part - we want to try to match the objects stored to file to objects in this scene as best we can
			objs = buttonDict.pop( 'objs', [] )
			realObjs = []
			for obj in objs:

				#does the exact object exist?
				if objExists( obj ):
					realObjs.append( obj )
					continue

				#how about inserting a namespace in-between any path tokens?
				pathToks = obj.split( '|' )
				if namespaceHint:
					objNs = '|'.join( '%s:%s' % (namespaceHint, tok) for tok in pathToks )
					if objExists( objNs ):
						realObjs.append( objNs )
						continue

				#how about ANY matches on the leaf path token?
				anyMatches = ls( pathToks[-1] )
				if anyMatches:
					realObjs.append( anyMatches[0] )
					if not namespaceHint:
						namespaceHint = ':'.join( anyMatches[0].split( ':' )[ :-1 ] )

			newButton.setObjs( realObjs )

			#print a warning if there is still data in the buttonDict - perhaps new data was written to the file that was handled when loading the preset?
			if buttonDict:
				printWarningStr( 'Not all info was loaded from %s on to the character: %s still remains un-handled' % (filepath, infoDict) )

		return newCharacter


def _drag( *a ):
	'''
	passes the local coords the widget is being dragged from
	'''
	return [a[-3], a[-2]]


def _drop( src, tgt, msgs, x, y, mods ):
	'''
	this is the drop handler used by everything in this module
	'''
	src = BaseMelUI.FromStr( src )
	tgt = BaseMelUI.FromStr( tgt )

	#if dragging an existing button around on the form, interpret it as a move
	if isinstance( src, ButtonUI ) and isinstance( tgt, DragDroppableFormLayout ):
		srcX, srcY = map( int, msgs )
		x -= srcX
		y -= srcY

		#figure out the delta moved
		curX, curY = src.button.getPos()
		delta = x - curX, y - curY

		charUI = src.getParentOfType( CharacterUI )
		buttonsToMove = charUI.getSelectedButtonUIs()

		#if the button dragged isn't in the selection - add it to the selection
		if src not in buttonsToMove:
			buttonsToMove.insert( 0, src )
			charUI.setSelectedButtonUIs( buttonsToMove )

		#now move all the buttons by the given delta
		for buttonUI in buttonsToMove:
			buttonUI.button.moveBy( delta )
			buttonUI.updateGeometry( False )

		#finally, refresh the BG image
		charUI.refreshImage()

	#if dragging from the form to the form, or dragging from the creation button, interpret it as a create new button
	elif isinstance( src, CreatePickerButton ) and isinstance( tgt, DragDroppableFormLayout ) or \
	     isinstance( src, DragDroppableFormLayout ) and isinstance( tgt, DragDroppableFormLayout ):

		characterUI = tgt.getParentOfType( CharacterUI )
		if characterUI:
			newButton = characterUI.createButton( (x, y) )


class ButtonUI(MelIconButton):
	def __init__( self, parent, button ):
		MelIconButton.__init__( self, parent )
		self.setColour( button.getColour() )

		assert isinstance( button, Button )
		self.button = button
		self.state = Button.NONE

		self( e=True, dgc=_drag, dpc=_drop, style='textOnly', c=self.on_press )
		self.POP_menu = MelPopupMenu( self, pmc=self.buildMenu )

		self._hashGeo = 0
		self._hashApp = 0

		self.update()
	def buildMenu( self, *a ):
		menu = self.POP_menu

		isEditorOpen = EditorWindow.Exists()

		menu.clear()
		editButtonKwargs = { 'l': 'edit this button',
		                     'c': self.on_edit,
		                     'ann': 'opens the button editor which allows you to edit properties of this button - colour, size, position etc...' }
		if isEditorOpen:
			MelMenuItem( menu, l='ADD selection to button', c=self.on_add, ann='adds the selected scene objects to this button' )
			MelMenuItem( menu, l='REPLACE button with selection', c=self.on_replace, ann="replaces this button's objects with the selected scene objects" )
			MelMenuItem( menu, l='REMOVE selection from button', c=self.on_remove, ann='removes the selected scene objects from this button' )
			MelMenuItemDiv( menu )
			MelMenuItem( menu, l='mirror duplicate button', c=self.on_mirrorDupe )
			MelMenuItem( menu, l='move to mirror position', c=self.on_mirrorThis )
			MelMenuItemDiv( menu )
			MelMenuItem( menu, **editButtonKwargs )
			MelMenuItem( menu, l='select highlighted buttons', c=self.on_selectHighlighted, ann='selects all buttons that are highlighted (ie are %s)' % Colour.ColourToName( Button.COLOUR_COMPLETE ) )
			MelMenuItemDiv( menu )
			MelMenuItem( menu, l='breakout UP', c=self.on_breakoutUp, ann='for each object in this button, creates a button above this one' )
			MelMenuItem( menu, l='breakout DOWN', c=self.on_breakoutDown, ann='for each object in this button, creates a button below this one' )
			MelMenuItem( menu, l='<-- breakout LEFT', c=self.on_breakoutLeft, ann='for each object in this button, creates a button to the left of this one' )
			MelMenuItem( menu, l='breakout RIGHT -->', c=self.on_breakoutRight, ann='for each object in this button, creates a button to the right of this one' )
			MelMenuItemDiv( menu )
			MelMenuItem( menu, l='DELETE this button', c=self.on_delete, ann='deletes the button being right clicked on' )
			MelMenuItem( menu, l='DELETE selected buttons', c=self.on_deleteSelected, ann='deletes all selected buttons.  NOTE: this is not necessarily the highlighted buttons - look in the button editor for the list of buttons that are selected' )
		else:
			class Callback(object):
				def __init__( self, func, *a ):
					self.f = func
					self.a = a
				def __call__( self, *a ):
					return self.f( *self.a )

			buttonObjs = self.button.getObjs()
			if len( buttonObjs ) == 1:
				objTrigger = Trigger( buttonObjs[0] )
				for slot, menuName, menuCmd in objTrigger.iterMenus( True ):
					MelMenuItem( menu, l=menuName, c=Callback( mel.eval, menuCmd ) )

				MelMenuItemDiv( menu )

			MelMenuItem( menu, **editButtonKwargs )
	def updateHighlightState( self ):
		selectedState = self.button.selectedState()
		if self.state == selectedState:
			return

		if selectedState == Button.PARTIAL:
			self.setColour( Button.COLOUR_PARTIAL )
		elif selectedState == Button.COMPLETE:
			self.setColour( Button.COLOUR_COMPLETE )
		else:
			self.setColour( self.button.getColour() )

		self.state = selectedState
	def isButtonHighlighted( self ):
		return self.button.selectedState()
	def update( self ):
		self.updateGeometry()
		self.updateAppearance()
		self.updateHighlightState()
	def updateGeometry( self, refreshUI=True ):
		posSize = pos, size = self.button.getPosSize()
		x, y = pos

		#check against the stored hash - early out if they match
		if hash( posSize ) == self._hashGeo:
			return

		#clamp the pos to the size of the parent
		parent = self.getParent()
		maxX, maxY = parent.getSize()
		#x = min( max( x, 0 ), maxX )  #NOTE: this is commented out because it seems maya reports the size of the parent to be 0, 0 until there are children...
		#y = min( max( y, 0 ), maxY )

		parent( e=True, ap=((self, 'top', y, 0), (self, 'left', x, 0)) )

		self.setSize( size )

		#store the hash - geo hashes are stored so that we can do lazy refreshes
		self._hashGeo = hash( posSize )

		if refreshUI:
			self.sendEvent( 'refreshImage' )
	def updateAppearance( self ):
		niceLabel = self.button.getNiceLabel()
		if hash( niceLabel ) == self._hashApp:
			return

		self.setLabel( niceLabel )
		self._hashApp = hash( niceLabel )
	def mirrorDuplicate( self ):
		dupe = self.button.duplicate()
		dupe.mirrorObjs()
		dupe.setAutoColour( self.button.getColour() )

		self.mirrorPosition( dupe )

		#if the button has a label - see if it has a parity and if so, reverse it
		label = self.button.getLabel()
		if label:
			newLabel = names.swapParity( label )
			dupe.setLabel( newLabel )

		self.sendEvent( 'appendButton', dupe, True )
	def mirrorPosition( self, button=None ):
		if button is None:
			button = self.button

		pickerLayout = self.getParentOfType( PickerLayout )
		pickerWidth = pickerLayout( q=True, w=True )

		pos, size = button.getPosSize()
		buttonCenterX = pos.x + (size.x / 2)

		newPosX = pickerWidth - buttonCenterX - size.x
		newPosX = min( max( newPosX, 0 ), pickerWidth )
		button.setPos( (newPosX, pos.y) )

	### EVENT HANDLERS ###
	def on_press( self, *a ):
		self.button.select()
		self.sendEvent( 'buttonSelected', self )
	def on_add( self, *a ):
		objs = self.button.getObjs()
		objs += ls( sl=True ) or []
		self.button.setObjs( objs )
	def on_replace( self, *a ):
		self.button.setObjs( ls( sl=True ) or [] )
	def on_remove( self, *a ):
		objs = self.button.getObjs()
		objs += ls( sl=True ) or []
		self.button.setObjs( objs )
	def on_mirrorDupe( self, *a ):
		self.mirrorDuplicate()
	def on_mirrorThis( self, *a ):
		self.mirrorPosition()
		self.updateGeometry()
	def on_edit( self, *a ):
		self.sendEvent( 'buttonSelected', self )
		self.sendEvent( 'on_showEditor' )
	def on_selectHighlighted( self, *a ):
		self.sendEvent( 'selectHighlightedButtons' )
	def on_breakoutUp( self, *a ):
		self.sendEvent( 'breakoutButton', self, (0, -1) )
	def on_breakoutDown( self, *a ):
		self.sendEvent( 'breakoutButton', self, (0, 1) )
	def on_breakoutLeft( self, *a ):
		self.sendEvent( 'breakoutButton', self, (-1, 0) )
	def on_breakoutRight( self, *a ):
		self.sendEvent( 'breakoutButton', self, (1, 0) )
	def on_delete( self, *a ):
		self.delete()
		self.button.delete()
		self.sendEvent( 'refreshImage' )
		self.sendEvent( 'updateButtonList' )
	def on_deleteSelected( self, *a ):
		self.sendEvent( 'deleteSelectedButtons' )


class MelPicture(BaseMelWidget):
	WIDGET_CMD = picture

	def getImage( self ):
		return self( q=True, i=True )
	def setImage( self, image ):
		self( e=True, i=image )


class DragDroppableFormLayout(MelFormLayout):
	def __init__( self, parent, **kw ):
		MelFormLayout.__init__( self, parent, **kw )
		self( e=True, dgc=_drag, dpc=_drop )


class CharacterUI(MelHLayout):
	def __init__( self, parent, character ):
		self.character = character
		self._selectedButtonUIs = []

		self.UI_picker = MelPicture( self, en=False, dgc=_drag, dpc=_drop )
		self.UI_picker.setImage( character.getBgImage() )
		self.layout()

		self.UI_buttonLayout = UI_buttonLayout = DragDroppableFormLayout( self )
		self( e=True, af=((UI_buttonLayout, 'top', 0), (UI_buttonLayout, 'left', 0), (UI_buttonLayout, 'right', 0), (UI_buttonLayout, 'bottom', 0)) )

		self.populate()
		self.highlightButtons()

		self.setDeletionCB( self.on_close )
	def populate( self ):
		for button in self.character.getButtons():
			self.appendButton( button )
	def updateEditor( self ):
		self.sendEvent( 'updateEditor' )
	def updateButtonList( self ):
		self.sendEvent( 'updateButtonList' )
	def createButton( self, pos, size=Button.DEFAULT_SIZE, colour=Button.AUTO_COLOUR, label='', objs=None ):
		if objs is None:
			objs = ls( sl=True, type='transform' )

		newButton = Button.Create( self.character, pos, size, colour, label, objs )

		#we want the drop position to be the centre of the button, not its edge - so we need to factor out the size, which we can only do after instantiating the button so we can query its size
		sizeHalf = newButton.getSize() / 2.0
		newButton.setPos( Vector( pos ) - sizeHalf )

		self.appendButton( newButton, True )

		#tell the editor to update the button list
		self.sendEvent( 'updateButtonList' )

		return newButton
	def appendButton( self, button, select=False ):
		ui = ButtonUI( self.UI_buttonLayout, button )
		if select:
			self.buttonSelected( ui )

		self.updateButtonList()

		return ui
	def highlightButtons( self ):
		for buttonUI in self.getButtonUIs():
			buttonUI.updateHighlightState()
	def getSelectedButtonUIs( self ):
		selButtonUIs = []
		for buttonUI in self._selectedButtonUIs:
			if buttonUI.button.exists():
				selButtonUIs.append( buttonUI )

		return selButtonUIs
	def setSelectedButtonUIs( self, buttonUIs ):
		self._selectedButtonUIs = buttonUIs[:]
		self.updateEditor()
	def selectHighlightedButtons( self ):
		currentSelection = []
		for buttonUI in self.getButtonUIs():
			if buttonUI.isButtonHighlighted() == Button.COMPLETE:
				currentSelection.append( buttonUI )

		self.setSelectedButtonUIs( currentSelection )
	def breakoutButton( self, buttonUI, direction ):
		buttons = self.character.breakoutButton( buttonUI.button, direction )
		for button in buttons:
			self.appendButton( button )
	def refreshImage( self ):
		self.UI_picker.setVisibility( False )
		self.UI_picker.setVisibility( True )
		self.updateEditor()
	def buttonSelected( self, button ):
		mods = getModifiers()
		if mods & SHIFT and mods & CTRL:
			if button not in self._selectedButtonUIs:
				self._selectedButtonUIs.append( button )
		elif mods & CTRL:
			if button in self._selectedButtonUIs:
				self._selectedButtonUIs.remove( button )
		elif mods & SHIFT:
			if button in self._selectedButtonUIs:
				self._selectedButtonUIs.remove( button )
			else:
				self._selectedButtonUIs.append( button )
		else:
			self._selectedButtonUIs = [ button ]

		self.updateEditor()
	def getButtonUIs( self ):
		return self.UI_buttonLayout.getChildren()
	def clearEmptyButtons( self ):
		needToRefresh = False
		for buttonUI in self.getButtonUIs():
			if buttonUI.button.isEmpty():
				buttonUI.button.delete()
				buttonUI.delete()
				needToRefresh = True

		if needToRefresh:
			self.refreshImage()
	def delete( self ):
		self.character.delete()
		MelHLayout.delete( self )
	def deleteSelectedButtons( self ):
		selectedButtonUIs = self.getSelectedButtonUIs()
		for buttonUI in selectedButtonUIs:
			buttonUI.button.delete()
			buttonUI.delete()

		self.refreshImage()
		self.updateButtonList()

	### EVENT HANDLERS ###
	def on_close( self, *a ):
		CmdEditorWindow.Close()


class CreatePickerButton(MelButton):
	'''
	this class exists purely so we can test for it instead of having to test against
	a more generic "MelButton" instance when handling drop callbacks
	'''
	pass


class MelColourSlider(BaseMelWidget):
	WIDGET_CMD = colorSliderGrp
	KWARG_VALUE_NAME = 'rgb'
	KWARG_VALUE_LONG_NAME = 'rgbValue'


class CmdEditorLayout(MelVSingleStretchLayout):
	def __init__( self, parent, buttonUIs ):
		self.UI_cmd = MelTextScrollField( self )

		#add the popup menu to the cmd editor
		MelPopupMenu( self.UI_cmd, pmc=self.buildMenu )

		hLayout = MelHLayout( self )
		self.UI_isPython = MelCheckBox( hLayout, l='Command is Python' )
		self.UI_cmdMode = MelOptionMenu( hLayout, l='Command Mode' )
		for modeStr in Button.CMD_MODES_NAMES:
			self.UI_cmdMode.append( modeStr )

		hLayout.layout()

		hLayout = MelHLayout( self )
		self.UI_save = MelButton( hLayout, l='Save and Close', c=self.on_saveClose )
		self.UI_delete = MelButton( hLayout, l='Delete and Close', c=self.on_deleteClose )
		self.UI_cancel = MelButton( hLayout, l='Cancel', c=self.on_cancel )
		hLayout.layout()

		self.setStretchWidget( self.UI_cmd )
		self.layout()

		self.setButtons( buttonUIs )
	def buildMenu( self, menu, menuParent ):
		cmd.menu( menu, e=True, dai=True )

		MelMenuItem( menu, l='save preset', en=bool( self.UI_cmd.getValue() ), c=self.on_savePreset )
		presetMenu = MelMenuItem( menu, l='load preset', sm=True )

		presetManager = presets.PresetManager( TOOL_NAME, TOOL_CMD_EXTENSION )
		for locale, presets in presetManager.listAllPresets().iteritems():
			for p in presets:
				MelMenuItem( presetMenu, l=p.name(), c=Callback( self.loadPreset, p ) )

		MelMenuItemDiv( menu )
		MelMenuItem( menu, l='manage presets', c=lambda *a: presetsUI.load( TOOL_NAME, ext=TOOL_CMD_EXTENSION ) )
	def loadPreset( self, preset, *a ):
		cmdStrLines = Path( preset ).read()
		firstLine = cmdStrLines.pop( 0 )

		cmdIsPython = 'python' in firstLine

		self.UI_cmd.setValue( '\n'.join( cmdStrLines ) )
		self.UI_isPython.setValue( cmdIsPython )
	def savePreset( self ):
		BUTTONS = OK, CANCEL = 'Ok', 'Cancel'
		ret = promptDialog( t='Preset Name', m='Enter the preset name', b=BUTTONS, db=OK )
		if ret == OK:
			name = promptDialog( q=True, tx=True )
			if name:
				cmdStrLines = [ '//'+ ('python' if self.UI_isPython.getValue() else 'mel') ]
				cmdStrLines.append( self.UI_cmd.getValue() )

				preset = presets.Preset( presets.GLOBAL, TOOL_NAME, name, TOOL_CMD_EXTENSION )
				preset.path().write( '\n'.join( cmdStrLines ) )
	def setButtons( self, buttonUIs ):
		self.buttonUIs = buttonUIs
		self.update()
	def update( self ):
		button = self.buttonUIs[0].button
		self.UI_cmd.setValue( button.getCmdStr() or '' )
		self.UI_isPython.setValue( button.getCmdIsPython() )
		self.UI_cmdMode.selectByIdx( button.getCmdMode() )

	### EVENT HANDLERS ###
	def on_savePreset( self, *a ):
		self.savePreset()
	@d_unifyUndo
	def on_saveClose( self, *a ):
		for buttonUI in self.buttonUIs:
			buttonUI.button.setCmdStr( self.UI_cmd.getValue() )
			buttonUI.button.setCmdIsPython( self.UI_isPython.getValue() )
			buttonUI.button.setCmdMode( self.UI_cmdMode.getSelectedIdx() )

		for ui in PickerLayout.IterInstances():
			ui.updateEditor()

		self.sendEvent( 'delete' )
	@d_unifyUndo
	def on_deleteClose( self, *a ):
		for buttonUI in self.buttonUIs:
			buttonUI.button.setCmdStr( None )

		for ui in PickerLayout.IterInstances():
			ui.updateEditor()

		self.sendEvent( 'delete' )
	def on_cancel( self, *a ):
		self.sendEvent( 'delete' )


class CmdEditorWindow(BaseMelWindow):
	WINDOW_NAME = 'PickerButtonCommandEditor'
	WINDOW_TITLE = 'Command Editor'

	DEFAULT_MENU = None
	DEFAULT_SIZE = 450, 200
	FORCE_DEFAULT_SIZE = True

	def __init__( self, button ):
		self.UI_editor = CmdEditorLayout( self, button )
		self.show()


class ButtonList(MelObjectScrollList):
	def itemAsStr( self, item ):
		return item.button.getNode().split( ':' )[-1].split( '|' )[-1].replace( '_picker', '' )


class EditorLayout(MelVSingleStretchLayout):
	DIRECTIONS = DIR_H, DIR_V = range( 2 )

	def __init__( self, parent, pickerUI ):
		self.pickerUI = pickerUI
		self.expand = True
		self.padding = 0

		lblWidth = 40
		self.UI_buttonLbl = MelLabel( self, align='center' )
		self.UI_new = CreatePickerButton( self, l='Create Button: middle drag to place', dgc=_drag, dpc=_drop )
		MelSeparator( self, h=16 )

		hLayout = MelHSingleStretchLayout( self )
		hLayout.expand = True

		vLayout = MelVSingleStretchLayout( hLayout )
		self.UI_buttons = ButtonList( vLayout, w=100, ams=True, sc=self.on_selectButtonFromList, dcc=self.on_doubleClickButton )
		self.UI_selectHighlighted = MelButton( vLayout, l='select highlighted', c=self.on_selectHighlighted )

		vLayout.padding = 0
		vLayout.setStretchWidget( self.UI_buttons )
		vLayout.layout()

		selLayout = MelVSingleStretchLayout( hLayout )
		selLayout.padding = 0

		#UI for label
		SZ_lblLabel = MelHSingleStretchLayout( selLayout )
		lbl = MelLabel( SZ_lblLabel, l='label:', w=lblWidth )
		SZ_label = MelHSingleStretchLayout( SZ_lblLabel )
		self.UI_selectedLabel = MelTextField( SZ_label )
		self.UI_autoSize = MelButton( SZ_label, l='fit to label', c=self.on_autoSize )

		SZ_label.setStretchWidget( self.UI_selectedLabel )
		SZ_label.layout()

		SZ_lblLabel.setStretchWidget( SZ_label )
		SZ_lblLabel.layout()

		#UI for colour
		self.UI_selectedColour = MelColourSlider( selLayout, label='colour:', cw=(1, lblWidth + 7), columnAttach=((1, 'left', 0), (2, 'left', 0), (3, 'left', 0)), adj=3 )

		#UI for position
		SZ_lblPos = MelHSingleStretchLayout( selLayout )
		lbl = MelLabel( SZ_lblPos, l='pos:', w=lblWidth )
		SZ_pos = MelHLayout( SZ_lblPos )
		SZ_lblPos.setStretchWidget( SZ_pos )
		SZ_lblPos.layout()

		SZ_X = MelHSingleStretchLayout( SZ_pos )
		self.UI_selectedPosX = MelIntField( SZ_X, min=0, max=640, step=1, cc=self.on_savePosX )
		self.UI_selectedNudgeXL = MelButton( SZ_X, l='<', c=self.on_nudgeXL )
		self.UI_selectedNudgeXR = MelButton( SZ_X, l='>', c=self.on_nudgeXR )
		SZ_X.setStretchWidget( self.UI_selectedPosX )

		SZ_Y = MelHSingleStretchLayout( SZ_pos )
		self.UI_selectedPosY = MelIntField( SZ_Y, min=0, max=640, step=1, cc=self.on_savePosY )
		self.UI_selectedNudgeYU = MelButton( SZ_Y, l='^', c=self.on_nudgeYU )
		self.UI_selectedNudgeYD = MelButton( SZ_Y, l='v', c=self.on_nudgeYD )
		SZ_Y.setStretchWidget( self.UI_selectedPosY )

		SZ_X.padding = 0
		SZ_Y.padding = 0
		SZ_X.layout()
		SZ_Y.layout()

		SZ_pos.layout()

		#UI for align buttons
		thinButton = 18
		SZ_lblAlignX = MelHSingleStretchLayout( selLayout )
		MelLabel( SZ_lblAlignX, l='align:', w=lblWidth )
		SZ_alignX = MelHLayout( SZ_lblAlignX )
		SZ_lblAlignX.setStretchWidget( SZ_alignX )
		SZ_lblAlignX.layout()

		MelButton( SZ_alignX, l='horiz', h=thinButton, c=self.on_alignH )
		MelButton( SZ_alignX, l='vert', h=thinButton, c=self.on_alignV )
		SZ_alignX.layout()

		#UI for size
		SZ_lblSize = MelHSingleStretchLayout( selLayout )
		lbl = MelLabel( SZ_lblSize, l='scale:', w=lblWidth )
		SZ_size = MelHLayout( SZ_lblSize )
		SZ_lblSize.setStretchWidget( SZ_size )
		SZ_lblSize.layout()

		self.UI_selectedScaleX = MelIntField( SZ_size, min=Button.MIN_SIZE, max=Button.MAX_SIZE, step=1, v=Button.MIN_SIZE, cc=self.on_saveScaleX )
		self.UI_selectedScaleY = MelIntField( SZ_size, min=Button.MIN_SIZE, max=Button.MAX_SIZE, step=1, v=Button.MIN_SIZE, cc=self.on_saveScaleY )
		SZ_size.layout()

		#setup change callbacks
		self.UI_selectedLabel.setChangeCB( self.on_saveLabel )
		self.UI_selectedColour.setChangeCB( self.on_saveColour )

		#add UI to edit the button set node
		self.UI_selectedObjects = MelSetMemebershipList( selLayout, h=75 )
		self.UI_selectedCmdButton = MelButton( selLayout, l='', c=self.on_editCmd )

		hLayout.setStretchWidget( selLayout )
		hLayout.layout()

		selLayout.setStretchWidget( self.UI_selectedObjects )
		selLayout.layout()

		self.setStretchWidget( hLayout )
		self.layout()

		self.setDeletionCB( self.on_delete )
	def getCurrentCharacterUI( self ):
		return self.pickerUI.getCurrentCharacterUI()
	def getSelectedButtonUIs( self ):
		return self.pickerUI.getSelectedButtonUIs()
	def updateButtonList( self ):
		currentCharacterUI = self.getCurrentCharacterUI()
		if currentCharacterUI is None:
			return

		self.UI_buttons.setItems( currentCharacterUI.getButtonUIs() )
	def update( self, selectInList=True ):
		currentCharacterUI = self.getCurrentCharacterUI()
		if not currentCharacterUI:
			self.UI_buttonLbl.setLabel( 'create a character first!' )
			self.UI_new.setEnabled( False )
			return

		self.UI_new.setEnabled( True )

		#make sure the selected buttons exist
		selectedButtonUIs = self.getSelectedButtonUIs()
		existingButtonUIs = []
		for buttonUI in selectedButtonUIs:
			if buttonUI.button.exists():
				existingButtonUIs.append( buttonUI )

		#if there buttons selected...
		if existingButtonUIs:
			button = existingButtonUIs[0].button
			pos, size = button.getPosSize()

			self.UI_buttonLbl.setLabel( 'editing button "%s"' % button.getNode() )
			self.UI_selectedLabel.setValue( button.getLabel(), False )
			self.UI_selectedPosX.setValue( pos.x, False )
			self.UI_selectedPosY.setValue( pos.y, False )
			self.UI_selectedScaleX.setValue( size.x, False )
			self.UI_selectedScaleY.setValue( size.y, False )
			self.UI_selectedColour.setValue( button.getColour(), False )

			#set set editor edits sets for ALL selected buttons
			self.UI_selectedObjects.setSets( [ b.button.getNode() for b in existingButtonUIs ] )

			#update the auto size from label button
			self.UI_autoSize.enable( bool( button.getLabel() ) )

			#update the command editor button
			self.UI_selectedCmdButton.setEnabled( bool( existingButtonUIs ) )
			cmdStr = button.getCmdStr()
			if cmdStr:
				self.UI_selectedCmdButton.setLabel( '***EDIT*** Press Command' )
			else:
				self.UI_selectedCmdButton.setLabel( 'CREATE Press Command' )

			#update the selected buttons lists
			if selectInList:
				self.UI_buttons.clearSelection()
				self.UI_buttons.selectItems( existingButtonUIs )
		else:
			self.UI_buttonLbl.setLabel( 'no button selected!' )
	def nudge( self, buttonUI, vectorIdx, direction=1 ):
		mods = getModifiers()
		increment = 5

		if mods & SHIFT:
			increment += 5
		elif mods & CTRL:
			increment = 5
		elif mods & ALT:
			increment = 1

		pos = buttonUI.button.getPos()
		pos[ vectorIdx ] += direction * increment
		buttonUI.button.setPos( pos )
		buttonUI.update()
	def align( self, buttonUI, side=DIR_H ):
		pos, size = buttonUI.button.getPosSize()

		midHSide = pos[0] + (size[0] / 2.0)
		midVSide = pos[1] + (size[1] / 2.0)
		for b in self.getSelectedButtonUIs():
			if b is buttonUI:
				continue

			if side == self.DIR_H:
				pos, size = b.button.getPosSize()
				pos[0] = midHSide - (size[0] / 2.0)
				b.button.setPos( pos )
			elif side == self.DIR_V:
				pos, size = b.button.getPosSize()
				pos[1] = midVSide - (size[1] / 2.0)
				b.button.setPos( pos )

			b.update()

	### EVENT HANDLERS ###
	def on_selectButtonFromList( self, *a ):
		charUI = self.pickerUI.getCurrentCharacterUI()
		if charUI:
			selectedButtonUIs = self.UI_buttons.getSelectedItems()
			self.pickerUI.getCurrentCharacterUI().setSelectedButtonUIs( selectedButtonUIs )

			for buttonUI in selectedButtonUIs:
				buttonUI.button.select( CTRL | SHIFT )

			self.update( False )
			charUI.highlightButtons()
	@d_unifyUndo
	def on_doubleClickButton( self, *a ):
		pass
	@d_unifyUndo
	def on_selectHighlighted( self, *a ):
		currentCharacterUI = self.getCurrentCharacterUI()
		if currentCharacterUI:
			currentCharacterUI.selectHighlightedButtons()
	@d_unifyUndo
	def on_autoSize( self, *a ):
		minHeight = 14
		extraPadding = 15
		for buttonUI in self.getSelectedButtonUIs():
			button = buttonUI.button
			label = button.getLabel()
			if label:
				curSize = button.getSize()
				width = getLabelWidth( label ) + extraPadding
				height = max( minHeight, curSize[1] )
				button.setSize( (width, height) )
				buttonUI.updateGeometry()

		self.update()
	@d_unifyUndo
	def on_nudgeXL( self, *a ):
		for buttonUI in self.getSelectedButtonUIs():
			self.nudge( buttonUI, 0, -1 )
	@d_unifyUndo
	def on_nudgeXR( self, *a ):
		for buttonUI in self.getSelectedButtonUIs():
			self.nudge( buttonUI, 0, 1 )
	@d_unifyUndo
	def on_nudgeYU( self, *a ):
		for buttonUI in self.getSelectedButtonUIs():
			self.nudge( buttonUI, 1, -1 )
	@d_unifyUndo
	def on_nudgeYD( self, *a ):
		for buttonUI in self.getSelectedButtonUIs():
			self.nudge( buttonUI, 1, 1 )
	@d_unifyUndo
	def on_alignH( self, *a ):
		self.align( self.getSelectedButtonUIs()[0], self.DIR_H )
	@d_unifyUndo
	def on_alignV( self, *a ):
		self.align( self.getSelectedButtonUIs()[0], self.DIR_V )
	@d_unifyUndo
	def on_saveLabel( self, *a ):
		label = self.UI_selectedLabel.getValue()
		for buttonUI in self.getSelectedButtonUIs():
			buttonUI.button.setLabel( label )
			buttonUI.update()

		self.UI_buttons.update()
	@d_unifyUndo
	def on_saveColour( self, *a ):
		colour = self.UI_selectedColour.getValue()
		for buttonUI in self.getSelectedButtonUIs():
			buttonUI.button.setColour( colour )
			buttonUI.update()
	@d_unifyUndo
	def on_savePosX( self, *a ):
		poxX = self.UI_selectedPosX.getValue()
		for buttonUI in self.getSelectedButtonUIs():
			pos = buttonUI.button.getPos()
			pos[0] = poxX
			buttonUI.button.setPos( pos )
			buttonUI.update()
	@d_unifyUndo
	def on_savePosY( self, *a ):
		posY = self.UI_selectedPosY.getValue()
		for buttonUI in self.getSelectedButtonUIs():
			pos = buttonUI.button.getPos()
			pos[1] = posY
			buttonUI.button.setPos( pos )
			buttonUI.update()
	@d_unifyUndo
	def on_saveScaleX( self, *a ):
		sizeX = self.UI_selectedScaleX.getValue()
		for buttonUI in self.getSelectedButtonUIs():
			size = buttonUI.button.getSize()
			size[0] = sizeX
			buttonUI.button.setSize( size )
			buttonUI.update()
	@d_unifyUndo
	def on_saveScaleY( self, *a ):
		sizeY = self.UI_selectedScaleY.getValue()
		for buttonUI in self.getSelectedButtonUIs():
			size = buttonUI.button.getSize()
			size[1] = sizeY
			buttonUI.button.setSize( size )
			buttonUI.update()
	def on_editCmd( self, *a ):
		CmdEditorWindow( self.getSelectedButtonUIs() )
	def on_delete( self, *a ):
		CmdEditorWindow.Close()


class EditorWindow(BaseMelWindow):
	WINDOW_NAME = 'pickerEditorWindow'
	WINDOW_TITLE = 'Picker Editor'

	DEFAULT_SIZE = 450, 400
	DEFAULT_MENU = None
	FORCE_DEFAULT_SIZE = True

	def __init__( self, pickerUI ):
		self.pickerUI = pickerUI
		self.UI_editor = EditorLayout( self, pickerUI )

		#kill the window when the scene changes
		self.setSceneChangeCB( self.on_sceneChange )
		self.show()
	def update( self ):
		self.UI_editor.update()
	def updateButtonList( self ):
		self.UI_editor.updateButtonList()

	### EVENT HANDLERS ###
	def on_sceneChange( self ):
		self.close()


class PickerLayout(MelVSingleStretchLayout):
	def __init__( self, parent ):
		self.UI_tabs = tabs = MelTabLayout( self )
		self.UI_tabs.setChangeCB( self.on_tabChange )

		self.UI_showEditorButton = MelButton( self, l='Show Editor', c=self.on_showEditor )

		self.padding = 0
		self.setStretchWidget( tabs )
		self.layout()

		#build an editor - but keep it hidden
		self.UI_editor = None

		#setup up the UI
		self.populate()

		#update button state when the selection changes
		self.setSelectionChangeCB( self.on_selectionChange )

		#make sure the UI gets updated when the scene changes
		self.setSceneChangeCB( self.on_sceneChange )

		#hook up an undo callback to undo button changes and update the UI
		self.setUndoCB( self.on_undo )

		#hook up a deletion callback
		self.setDeletionCB( self.on_delete )
	def setUndoCbState( self, state ):
		if state:
			self.setUndoCB( self.on_undo )
		else:
			self.setUndoCB( None )
	def populate( self ):
		self.UI_tabs.clear()
		for character in Character.IterAll():
			self.appendCharacter( character )
	def appendCharacter( self, character ):
		idx = len( self.UI_tabs.getChildren() )
		ui = CharacterUI( self.UI_tabs, character )
		self.UI_tabs.setLabel( idx, character.getName() )
	def getCurrentCharacterUI( self ):
		selUI = self.UI_tabs.getSelectedTab()
		if selUI:
			return CharacterUI.FromStr( selUI )

		return None
	def getSelectedButtonUIs( self ):
		selectedTab = self.UI_tabs.getSelectedTab()
		if selectedTab:
			currentCharacter = CharacterUI.FromStr( selectedTab )
			if currentCharacter:
				return currentCharacter.getSelectedButtonUIs()

		return []
	def selectCharacter( self, character ):
		for idx, ui in enumerate( self.UI_tabs.getChildren() ):
			if ui.character == character:
				self.UI_tabs.setSelectedTabIdx( idx )
	def isEditorOpen( self ):
		if self.UI_editor is None:
			return False

		return self.UI_editor.exists()
	def updateEditor( self ):
		if self.isEditorOpen():
			self.UI_editor.update()
	def updateButtonList( self ):
		if self.isEditorOpen():
			self.UI_editor.updateButtonList()
	def loadPreset( self, preset, *a ):  #*a exists only because this gets directly called by a menuItem - and menuItem's always pass a bool arg for some reason...  check state maybe?
		namespaceHint = None

		#if there is a selection, use any namespace on the selection as the namespace hint
		sel = ls( sl=True, type='transform' )
		if sel:
			namespaceHint = sel[0].split( ':' )[0]

		newCharacter = Character.LoadFromPreset( preset, namespaceHint )
		if newCharacter:
			self.appendCharacter( newCharacter )
		else:
			printWarningStr( 'No character was created!' )
	def renameCurrentCharacter( self, newName ):
		charUIStr = self.UI_tabs.getSelectedTab()
		if charUIStr:
			charUI = CharacterUI.FromStr( charUIStr )
			if charUI:
				charUI.character.setName( newName )
				charUIIdx = self.UI_tabs.getSelectedTabIdx()
				self.UI_tabs.setLabel( charUIIdx, charUI.character.getName() )
	def clearEmptyButtons( self ):
		charUI = self.getCurrentCharacterUI()
		if charUI:
			charUI.clearEmptyButtons()

	### EVENT HANDLERS ###
	def on_showEditor( self, *a ):
		if not self.isEditorOpen():
			self.UI_editor = EditorWindow( self )

		self.updateButtonList()
		self.updateEditor()
	def on_tabChange( self, *a ):
		if self.isEditorOpen():
			self.UI_editor.updateButtonList()

		self.on_selectionChange()
	def on_sceneChange( self, *a ):
		self.populate()
	def on_selectionChange( self, *a ):
		charUIStr = self.UI_tabs.getSelectedTab()
		if charUIStr:
			charUI = CharacterUI.FromStr( charUIStr )
			charUI.highlightButtons()
	def on_undo( self, *a ):

		#check to see if the user only wants the undo to work if the editor is open
		undoOnlyIfEditorOpen = optionVar( q='zooUndoOnlyIfEditorOpen' )
		if undoOnlyIfEditorOpen:
			if not self.isEditorOpen():
				return

		charUI = self.getCurrentCharacterUI()
		if charUI:
			self.updateEditor()
			self.updateButtonList()
			for buttonUI in charUI.getButtonUIs():
				buttonUI.updateGeometry()
				buttonUI.updateAppearance()
	def on_delete( self, *a ):
		EditorWindow.Close()


class PickerWindow(BaseMelWindow):
	WINDOW_NAME = 'zooPicker'
	WINDOW_TITLE = 'Picker Tool'

	DEFAULT_SIZE = 275, 525
	DEFAULT_MENU = 'File'
	DEFAULT_MENU_IS_HELP = False

	FORCE_DEFAULT_SIZE = True

	HELP_MENU = 'hamish@macaronikazoo.com', TOOL_NAME, None

	def __init__( self ):
		fileMenu = self.getMenu( 'File' )
		fileMenu( e=True, pmc=self.buildFileMenu )

		self.UI_editor = PickerLayout( self )
		self.show()
	def buildFileMenu( self, *a ):
		menu = self.getMenu( 'File' )
		menu.clear()

		currentCharUI = self.UI_editor.getCurrentCharacterUI()
		charSelected = bool( currentCharUI )
		charSelectedIsReferenced = True
		if charSelected:
			charSelectedIsReferenced = referenceQuery( currentCharUI.character.getNode(), inr=True )

		MelMenuItem( menu, l='New Picker Tab', c=self.on_create )
		MelMenuItem( menu, en=charSelected, l='Rename Current Picker Tab', c=self.on_rename )
		MelMenuItem( menu, en=not charSelectedIsReferenced, l='Remove Current Picker Tab', c=self.on_remove )
		MelMenuItemDiv( menu )

		MelMenuItem( menu, en=not charSelectedIsReferenced, l='Remove Empty Buttons', c=self.on_clearEmpty )
		MelMenuItem( menu, en=charSelectedIsReferenced, l='Remove Edits To Referenced Picker', c=self.on_clearRefEdits )
		MelMenuItemDiv( menu )

		MelMenuItem( menu, en=charSelected, l='Save Picker Preset', c=self.on_save )
		self.SUB_presets = MelMenuItem( menu, l='Load Picker Preset', sm=True, pmc=self.buildLoadablePresets )

		undoOnlyIfEditorOpen = optionVar( q='zooUndoOnlyIfEditorOpen' )
		MelMenuItemDiv( menu )
		MelMenuItem( menu, l='Only Refresh On Undo If Editor Open', cb=undoOnlyIfEditorOpen, c=self.on_undoPrefChange )
	def buildLoadablePresets( self, *a ):
		menu = self.SUB_presets

		man = presets.PresetManager( TOOL_NAME, TOOL_EXTENSION )
		presets = man.listAllPresets()
		for loc, locPresets in presets.iteritems():
			for p in locPresets:
				pName = p.name()
				MelMenuItem( menu, l=pName, c=Callback( self.UI_editor.loadPreset, p ) )

		MelMenuItemDiv( menu )
		MelMenuItem( menu, l='manage presets', c=self.on_loadPresetManager )

	### EVENT HANDLERS ###
	def on_create( self, *a ):
		BUTTONS = OK, CANCEL = 'Ok', 'Cancel'

		defaultName = Path( file( q=True, sn=True ) ).name()
		ret = promptDialog( t='Create Picker Tab', m='Enter a name for the new picker tab:', text=defaultName, b=BUTTONS, db=OK )

		if ret == OK:
			name = promptDialog( q=True, text=True )
			if name:
				newCharacter = Character.Create( name )
				self.UI_editor.populate()
				self.UI_editor.selectCharacter( newCharacter )
				self.UI_editor.on_showEditor()
	def on_rename( self, *a ):
		currentCharacterUI = self.UI_editor.getCurrentCharacterUI()
		if currentCharacterUI:
			BUTTONS = OK, CANCEL = 'Ok', 'Cancel'
			ret = promptDialog( t='New Name', m='Enter the new name for the picker', tx=currentCharacterUI.character.getName(), b=BUTTONS, db=OK )
			if ret == OK:
				newName = promptDialog( q=True, tx=True )
				if not newName:
					printWarningStr( "You must enter a name!" )
					return

				self.UI_editor.renameCurrentCharacter( newName )
	def on_remove( self, *a ):
		currentCharacterUI = self.UI_editor.getCurrentCharacterUI()
		if currentCharacterUI:
			currentCharacterUI.delete()
	def on_clearEmpty( self, *a ):
		self.UI_editor.clearEmptyButtons()
	def on_clearRefEdits( self, *a ):
		currentCharacterUI = self.UI_editor.getCurrentCharacterUI()
		if currentCharacterUI:
			objs = [ currentCharacterUI.character.getNode() ]
			objs += [ button.getNode() for button in currentCharacterUI.character.getButtons() ]
			removeRefEdits( objs )
			self.UI_editor.populate()
	def on_save( self, *a ):
		currentChar = self.UI_editor.getCurrentCharacterUI()
		if currentChar:
			BUTTONS = OK, CANCEL = 'Ok', 'Cancel'
			ret = promptDialog( t='Preset Name', m='enter the name of the preset', tx=currentChar.character.getName(), b=BUTTONS, db=OK )
			if ret == OK:
				presetName = promptDialog( q=True, tx=True )
				if presetName:
					currentChar.character.saveToPreset( presets.Preset( presets.GLOBAL, TOOL_NAME, presetName, TOOL_EXTENSION ) )
	def on_loadPresetManager( self, *a ):
		presetsUI.load( TOOL_NAME, ext=TOOL_EXTENSION )
	def on_undoPrefChange( self, *a ):
		undoOnlyIfEditorOpen = optionVar( iv=('zooUndoOnlyIfEditorOpen', int( a[0] )) )


#end
