
from __future__ import with_statement

import os
import re
import sys
import time
import marshal
import datetime
import subprocess
import tempfile

import path

from path import *
from misc import iterBy

### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
### IMPORTANT: perforce is disabled by default - to enable call enablePerforce()
### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def getDefaultWorkingDir():
	'''
	perforce can be setup to use p4config files - if a user has done this, then setting the working
	directory properly becomes critically important.  This function gets called before spawning the
	p4 processes to set the working directory.  Implement the appropriate logic here for your
	particular environment
	'''
	return None


class FinishedP4Operation(Exception): pass
class TimedOutP4Operation(Exception): pass


class P4Exception(Exception): pass


def _p4fast( *args ):
	p = subprocess.Popen( 'p4 -G '+ ' '.join( args ), cwd=getDefaultWorkingDir(), shell=True, stdout=subprocess.PIPE )

	results = []
	try:
		while True:
			results.append( marshal.loads( p.stdout.read() ) )
	except EOFError: pass

	p.wait()

	return results


class P4Output(dict):
	EXIT_PREFIX = 'exit:'
	ERROR_PREFIX = 'error:'

	#
	START_DIGITS = re.compile( '(^[0-9]+)(.*)' )
	END_DIGITS = re.compile( '(.*)([0-9]+$)' )

	def __init__( self, outStr, keysColonDelimited=False ):
		EXIT_PREFIX = self.EXIT_PREFIX
		ERROR_PREFIX = self.ERROR_PREFIX

		self.errors = []

		if isinstance( outStr, basestring ):
			lines = outStr.split( '\n' )
		elif isinstance( outStr, (list, tuple) ):
			lines = outStr
		else:
			print outStr
			raise P4Exception( "unsupported type (%s) given to %s" % (type( outStr ), self.__class__.__name__) )

		delimiter = (' ', ':')[ keysColonDelimited ]
		for line in lines:
			line = line.strip()

			if not line:
				continue

			if line.startswith( EXIT_PREFIX ):
				break
			elif line.startswith( ERROR_PREFIX ):
				self.errors.append( line )
				continue

			idx = line.find( delimiter )
			if idx == -1:
				prefix = line
				data = True
			else:
				prefix = line[ :idx ].strip()
				data = line[ idx + 1: ].strip()
				if data.isdigit():
					data = int( data )

			if keysColonDelimited:
				prefix = ''.join( [ (s, s.capitalize())[ n ] for n, s in enumerate( prefix.lower().split() ) ] )
			else:
				prefix = prefix[ 0 ].lower() + prefix[ 1: ]

			self[ prefix ] = data

		#finally, if there are prefixes which have a numeral at the end, strip it and pack the data into a list
		multiKeys = {}
		for k in self.keys():
			m = self.END_DIGITS.search( k )
			if m is None:
				continue

			prefix, idx = m.groups()
			idx = int( idx )

			data = self.pop( k )
			try:
				multiKeys[ prefix ].append( (idx, data) )
			except KeyError:
				multiKeys[ prefix ] = [ (idx, data) ]

		for prefix, dataList in multiKeys.iteritems():
			try:
				self.pop( prefix )
			except KeyError: pass

			dataList.sort()
			self[ prefix ] = [ d[ 1 ] for d in dataList ]
	def __unicode__( self ):
		return self.__str__()
	def __getattr__( self, attr ):
		return self[ attr ]
	def asStr( self ):
		if self.errors:
			return '\n'.join( self.errors )

		return '\n'.join( '%s:  %s' % items for items in self.iteritems() )


INFO_PREFIX_RE = re.compile( '^info([0-9]*): ' )

def _p4run( *args ):
	if not isPerforceEnabled():
		return False

	global INFO_PREFIX_RE
	if '-s' not in args:  #if the -s flag is in the global flags, perforce sends all data to the stdout, and prefixes all errors with "error:"
		args = ('-s',) + args

	cmdStr = 'p4 '+ ' '.join( map( str, args ) )
	with tempfile.TemporaryFile() as tmpFile:
		try:
			p4Proc = subprocess.Popen( cmdStr, cwd=getDefaultWorkingDir(), shell=True, stdout=tmpFile.fileno() )
		except OSError:
			P4File.USE_P4 = False
			return False

		p4Proc.wait()
		tmpFile.seek( 0 )

		return [ INFO_PREFIX_RE.sub( '', line ) for line in tmpFile.readlines() ]


def p4run( *args, **kwargs ):
	ret = _p4run( *args )
	if ret is False:
		return False

	return P4Output( ret, **kwargs )


P4INFO = None
def p4Info():
	global P4INFO

	if P4INFO:
		return P4INFO

	P4INFO = p4run( 'info', keysColonDelimited=True )
	if not P4INFO:
		disablePerforce()

	return P4INFO


def populateChange( change ):
		changeNum = change[ 'change' ]
		if isinstance( changeNum, int ) and changeNum:
			fullChange = P4Change.FetchByNumber( changeNum )
			for key, value in fullChange.iteritems():
				change[ key ] = value


class P4Change(dict):
	def __init__( self ):
		self[ 'user' ] = ''
		self[ 'change' ] = None
		self[ 'description' ] = ''
		self[ 'files' ] = []
		self[ 'actions' ] = []
		self[ 'revisions' ] = []
	def __setattr__( self, attr, value ):
		if isinstance( value, basestring ):
			if value.isdigit():
				value = int( value )

		self[ attr ] = value
	def __getattr__( self, attr ):
		'''
		if the value of an attribute is the populateChanges function (in the root namespace), then
		the full changelist data is queried.  This is useful for commands like the p4 changes command
		(wrapped by the FetchChanges class method) which lists partial changelist data.  The method
		returns P4Change objects with partial data, and when more detailed data is required, a full
		query can be made.  This ensures minimal server interaction.
		'''
		value = self[ attr ]
		if value is populateChange:
			populateChange( self )
			value = self[ attr ]

		return value
	def __str__( self ):
		return str( self.change )
	def __int__( self ):
		return self[ 'change' ]
	__hash__ = __int__
	def __lt__( self, other ):
		return self.change < other.change
	def __le__( self, other ):
		return self.change <= other.change
	def __eq__( self, other ):
		return self.change == other.change
	def __ne__( self, other ):
		return self.change != other.change
	def __gt__( self, other ):
		return self.change > other.change
	def __ge__( self, other ):
		return self.change >= other.change
	def __len__( self ):
		return len( self.files )
	def __eq__( self, other ):
		if isinstance( other, int ):
			return self.change == other
		elif isinstance( other, basestring ):
			if other == 'default':
				return self.change == 0

		return self.change == other.change
	def __iter__( self ):
		return zip( self.files, self.revisions, self.actions )
	@classmethod
	def Create( cls, description, files=None ):

		#clean the description line
		description = '\n\t'.join( [ line.strip() for line in description.split( '\n' ) ] )
		info = p4Info()
		contents = '''Change:\tnew\n\nClient:\t%s\n\nUser:\t%s\n\nStatus:\tnew\n\nDescription:\n\t%s\n''' % (info.clientName, info.userName, description)

		global INFO_PREFIX_RE

		p4Proc = subprocess.Popen( 'p4 -s change -i', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
		stdout, stderr = p4Proc.communicate( contents )
		p4Proc.wait()
		stdout = [ INFO_PREFIX_RE.sub( '', line ) for line in stdout.split( '\n' ) ]

		output = P4Output( stdout )
		changeNum = int( P4Output.START_DIGITS.match( output.change ).groups()[ 0 ] )

		new = cls()
		new.description = description
		new.change = changeNum

		if files is not None:
			p4run( 'reopen -c', changeNum, *files )

		return new
	@classmethod
	def FetchByNumber( cls, number ):
		lines = _p4run( 'describe', number )
		if not lines:
			return None

		change = cls()
		change.change = number

		toks = lines[ 0 ].split()
		if 'by' in toks:
			idx = toks.index( 'by' )
			change.user = toks[ idx+1 ]

		change.description = ''
		lineIter = iter( lines[ 2: ] )
		try:
			prefix = 'text:'
			PREFIX_LEN = len( prefix )

			line = lineIter.next()
			while line.startswith( prefix ):
				line = line[ PREFIX_LEN: ].lstrip()

				if line.startswith( 'Affected files ...' ):
					break

				change.description += line
				line = lineIter.next()

			lineIter.next()
			line = lineIter.next()
			while not line.startswith( prefix ):
				idx = line.rfind( '#' )
				depotFile = Path( line[ :idx ] )

				revAndAct = line[ idx + 1: ].split()
				rev = int( revAndAct[ 0 ] )
				act = revAndAct[ 1 ]

				change.files.append( depotFile )
				change.actions.append( act )
				change.revisions.append( rev )

				line = lineIter.next()
		except StopIteration:
			pass

		return change
	@classmethod
	def FetchByDescription( cls, description, createIfNotFound=False ):
		'''
		fetches a changelist based on a given description from the list of pending changelists
		'''
		cleanDesc = ''.join( [ s.strip() for s in description.lower().strip().split( '\n' ) ] )
		for change in cls.IterPending():
			thisDesc = ''.join( [ s.strip() for s in change.description.lower().strip().split( '\n' ) ] )
			if thisDesc == cleanDesc:
				return change

		if createIfNotFound:
			return cls.Create( description )
	@classmethod
	def FetchChanges( cls, *args ):
		'''
		effectively runs the command:
		p4 changes -l *args

		a list of P4Change objects is returned
		'''
		lines = _p4run( 'changes -l %s' % ' '.join( args ) )
		changes = []
		if lines:
			lineIter = iter( lines )
			curChange = None
			try:
				while True:
					line = lineIter.next()
					if line.startswith( 'Change' ):
						curChange = cls()
						changes.append( curChange )
						toks = line.split()
						curChange.change = int( toks[ 1 ] )
						curChange.user = toks[ -1 ]
						curChange.date = datetime.date( *list( map( int, toks[ 3 ].split( '/' ) ) ) )
						curChange.description = ''

						#setup triggers for other data in the changelist that doesn't get returned by the changes command - see the __getattr__ doc for more info
						curChange.files = populateChange
						curChange.actions = populateChange
						curChange.revisions = populateChange
					elif curChange is not None:
						curChange.description += line
			except StopIteration:
				return changes
	@classmethod
	def IterPending( cls ):
		'''
		iterates over pending changelists
		'''
		info = p4Info()
		for line in _p4run( 'changes -u %s -s pending -c %s' % (info.userName, info.clientName) ):
			toks = line.split()
			try:
				changeNum = int( toks[ 1 ] )
			except IndexError: continue

			yield cls.FetchByNumber( changeNum )


#the number of the default changelist
P4Change.CHANGE_NUM_DEFAULT = P4Change()
P4Change.CHANGE_NUM_DEFAULT.change = 0

#the object to represent invalid changelist numbers
P4Change.CHANGE_NUM_INVALID = P4Change()

#all opened perforce files get added to a changelist with this description by default
DEFAULT_CHANGE = 'default auto-checkout'

#gets called when a perforce command takes too long (defined by P4File.TIMEOUT_PERIOD)
P4_LENGTHY_CALLBACK = None

#gets called when a lengthy perforce command finally returns
P4_RETURNED_CALLBACK = None

class P4File(Path):
	'''
	provides a more convenient way of interfacing with perforce.  NOTE: where appropriate all actions
	are added to the changelist with the description DEFAULT_CHANGE
	'''
	USE_P4 = False

	#the default change description for instances
	DEFAULT_CHANGE = DEFAULT_CHANGE

	BINARY = 'binary'
	XBINARY = 'xbinary'

	TIMEOUT_PERIOD = 5

	def run( self, *args, **kwargs ):
		return p4run( *args, **kwargs )
	def getFile( self, f=None ):
		if f is None:
			return self

		return Path( f )
	def getFileStr( self, f=None, allowMultiple=False, verifyExistence=True ):
		if f is None:
			return '"%s"' % self

		if isinstance( f, (list, tuple) ):
			if verifyExistence: return '"%s"' % '" "'.join( [ anF for anF in f if Path( anF ).exists() ] )
			else: return '"%s"' % '" "'.join( f )

		return '"%s"' % Path( f )
	def getStatus( self, f=None ):
		'''
		returns the status dictionary for the instance.  if the file isn't managed by perforce,
		None is returned
		'''
		if not self.USE_P4:
			return None

		f = self.getFile( f )
		try:
			return self.run( 'fstat', f )
		except Exception: return None
	def isManaged( self, f=None ):
		'''
		returns True if the file is managed by perforce, otherwise False
		'''
		if not self.USE_P4:
			return False

		f = self.getFile( f )
		stat = self.getStatus( f )
		if stat:
			#if the file IS managed - only return true if the head action isn't delete - which effectively means the file
			#ISN'T managed...
			try:
				return stat[ 'headAction' ] != 'delete'
			except KeyError:
				#this can happen if the file is a new file and is opened for add
				return True
		return False
	managed = isManaged
	def isUnderClient( self, f=None ):
		'''
		returns whether the file is in the client's root
		'''
		if not self.USE_P4:
			return False

		f = self.getFile( f )
		results = _p4fast( 'fstat', f )
		if results:
			fstatDict = results[0]
			if 'code' in fstatDict:
				if fstatDict[ 'code' ] == 'error':
					phrases = [ "not in client view", "not under" ]

					dataStr = fstatDict[ 'data' ].lower()
					for ph in phrases:
						if ph in dataStr:
							return False

		return True
	def getAction( self, f=None ):
		'''
		returns the head "action" of the file - if the file isn't in perforce None is returned...
		'''
		if not self.USE_P4:
			return None

		f = self.getFile( f )
		data = self.getStatus( f )

		try:
			return data.get( 'action', None )
		except AttributeError: return None
	action = property( getAction )
	def getHaveHead( self, f=None ):
		if not self.USE_P4:
			return False

		f = self.getFile( f )
		data = self.getStatus( f )

		try:
			return data[ 'haveRev' ], data[ 'headRev' ]
		except (AttributeError, TypeError, KeyError):
			return None, None
	def isEdit( self, f=None ):
		if not self.USE_P4:
			return False

		editActions = [ 'add', 'edit' ]
		action = self.getAction( f )

		#if the action is none, the file may not be managed - check
		if action is None:
			if not self.getStatus( f ):
				return None

		return action in editActions
	def isLatest( self, f=None ):
		'''
		returns True if the user has the latest version of the file, otherwise False
		'''

		#if no p4 integration, always say everything is the latest to prevent complaints from tools
		if not self.USE_P4:
			return True

		status = self.getStatus( f )
		if not status:
			return None

		#if there is any action on the file then always return True
		if 'action' in status:
			return True

		#otherwise check revision numbers
		try:
			headRev, haveRev = status[ 'headRev' ], status[ 'haveRev' ]

			return headRev == haveRev
		except KeyError:
			return False
	def add( self, f=None, type=None ):
		if not self.USE_P4:
			return False

		try:
			args = [ 'add', '-c', self.getOrCreateChange() ]
		except:
			return False

		#if the type has been specified, add it to the add args
		if type is not None:
			args += [ '-t', type ]

		args.append( self.getFile( f ) )

		ret = p4run( *args )
		if ret.errors:
			return False

		return True
	def edit( self, f=None ):
		f = self.getFile( f )
		if not isPerforceEnabled():

			#if p4 is disabled but the file is read-only, set it to be writeable...
			if not f.getWritable():
				f.setWritable()

			return False

		#if the file is already writeable, assume its checked out already
		if f.getWritable():
			return True

		try:
			ret = p4run( 'edit', '-c', self.getOrCreateChange(), self.getFile( f ) )
		except:
			return False

		if ret.errors:
			return False

		return True
	def editoradd( self, f=None ):
		if self.edit( f ):
			return True

		if self.add( f ):
			return True

		return False
	def revert( self, f=None ):
		if not self.USE_P4:
			return False

		return self.run( 'revert', self.getFile( f ) )
	def sync( self, f=None, force=False, rev=None, change=None ):
		'''
		rev can be a negative number - if it is, it works as previous revisions - so rev=-1 syncs to
		the version prior to the headRev.  you can also specify the change number using the change arg.
		if both a rev and a change are specified, the rev is used
		'''
		if not self.USE_P4:
			return False

		f = self.getFile( f )

		#if file is a directory, then we want to sync to the dir
		f = str( f.asfile() )
		if not f.startswith( '//' ):  #depot paths start with // - but windows will try to poll the network for a computer with the name, so if it starts with //, assume its a depot path
			if os.path.isdir( f ):
				f = '%s/...' % f

		if rev is not None:
			if rev == 0: f += '#none'
			elif rev < 0:
				status = self.getStatus()
				headRev = status[ 'headRev' ]
				rev += int( headRev )
				if rev <= 0: rev = 'none'
				f += '#%s' % rev
			else: f += '#%s' % rev
		elif change is not None:
			f += '@%s' % change

		if force: return self.run( 'sync', '-f', f )
		else: return self.run( 'sync', f )
	def delete( self, f=None ):
		if not self.USE_P4:
			return False

		f = self.getFile( f )
		action = self.getAction( f )
		if action is None and self.managed( f ):
			return self.run( 'delete', '-c', self.getOrCreateChange(), f )
	def remove( self, f=None ):
		if not self.USE_P4:
			return False

		self.sync( f, rev=0 )
	def rename( self, newName, f=None ):
		if not self.USE_P4:
			return False

		f = self.getFile( f )

		try:
			action = self.getAction( f )
			if action is None and self.managed( f ):
				self.run( 'integrate', '-c', self.getOrCreateChange(), f, str( newName ) )
				return self.run( 'delete', '-c', self.getOrCreateChange(), f )
		except Exception: pass
		return False
	def copy( self, newName, f=None ):
		if not self.USE_P4:
			return False

		f = self.getFile( f )
		newName = self.getFile( newName )
		action = self.getAction( f )

		if self.managed( f ):
			return self.run( 'integrate', '-c', self.getOrCreateChange(), f, newName )

		return False
	def submit( self, change=None ):
		if not self.USE_P4:
			return

		if change is None:
			change = self.getChange().change

		self.run( 'submit', '-c', change )
	def getChange( self, f=None ):
		if not self.USE_P4:
			return P4Change.CHANGE_NUM_INVALID

		f = self.getFile( f )
		stat = self.getStatus( f )
		try:
			return stat.get( 'change', P4Change.CHANGE_NUM_DEFAULT )
		except (AttributeError, ValueError): return P4Change.CHANGE_NUM_DEFAULT
	def setChange( self, newChange=None, f=None ):
		'''
		sets the changelist the file belongs to. the changelist can be specified as either a changelist
		number, a P4Change object, or a description. if a description is given, the existing pending
		changelists are searched for a matching description.  use 0 for the default changelist.  if
		None is passed, then the changelist as described by self.DEFAULT_CHANGE is used
		'''
		if not self.USE_P4:
			return

		if isinstance( newChange, (int, long) ):
			change = newChange
		elif isinstance( newChange, P4Change ):
			change = newChange.change
		else:
			change = P4Change.FetchByDescription( newChange, True ).change

		f = self.getFile( f )
		self.run( 'reopen', '-c', change, f )
	def getOtherOpen( self, f=None ):
		f = self.getFile( f )
		statusDict = self.getStatus( f )
		try:
			return statusDict[ 'otherOpen' ]
		except (KeyError, TypeError):
			return []
	def getOrCreateChange( self, f=None ):
		'''
		if the file isn't already in a changelist, this will create one.  returns the change number
		'''
		if not self.USE_P4:
			return P4Change.CHANGE_NUM_INVALID

		f = self.getFile( f )
		ch = self.getChange( f )
		if ch == P4Change.CHANGE_NUM_DEFAULT:
			return P4Change.FetchByDescription( self.DEFAULT_CHANGE, True ).change

		return ch
	def getChangeNumFromDesc( self, description=None, createIfNotFound=True ):
		if description is None:
			description = self.DEFAULT_CHANGE

		return P4Change.FetchByDescription( description, createIfNotFound ).change
	def allPaths( self, f=None ):
		'''
		returns all perforce paths for the file (depot path, workspace path and disk path)
		'''
		if not self.USE_P4:
			return None

		f = self.getFile( f )

		return toDepotAndDiskPaths( [f] )[ 0 ]
	def toDepotPath( self, f=None ):
		'''
		returns the depot path to the file
		'''
		if not self.USE_P4:
			return None

		return self.allPaths( f )[ 0 ]
	def toDiskPath( self, f=None ):
		'''
		returns the disk path to a depot file
		'''
		if not self.USE_P4:
			return None

		return self.allPaths( f )[ 1 ]


P4Data = P4File  #used to be called P4Data - this is just for any legacy references...

path.P4File = P4File  #insert the class into the path script...  HACKY!


###--- Add Perforce Integration To Path Class ---###

def asP4( self ):
	'''
	returns self as a P4File instance - the instance is cached so repeated calls to this
	method will result in the same P4File instance being returned.

	NOTE: the caching is done within the method, it doesn't rely on the cache decorators
	used elsewhere in this class, so it won't get blown away on cache flush
	'''
	try:
		return self.p4
	except AttributeError:
		self.p4 = P4File(self)
		return self.p4

def edit( self ):
	'''
	if the file exists and is in perforce, this will open it for edit - if the file isn't in perforce
	AND exists then this will open the file for add, otherwise it does nothing
	'''
	if self.exists():
		return self.asP4().editoradd()

	return False

editoradd = edit
def add( self, type=None ):
	return self.asP4().add()

def revert( self ):
	return self.asP4().revert()

def asDepot( self ):
	'''
	returns this instance as a perforce depot path
	'''
	return self.asP4().toDepotPath()


#now wrap existing methods on the Path class - like write, delete, copy etc so that they work nicely with perforce
pathWrite = Path.write
def _p4write( filepath, contentsStr, doP4=True ):
	'''
	wraps Path.write:  if doP4 is true, the file will be either checked out of p4 before writing or add to perforce
	after writing if its not managed already
	'''

	assert isinstance( filepath, Path )
	if doP4 and isPerforceEnabled():

		hasBeenHandled = False

		isUnderClient = P4File().isUnderClient( filepath )
		if filepath.exists():
			#assume if its writeable that its open for edit already
			if not filepath.getWritable():
				_p4fast( 'edit', filepath )
				if not filepath.getWritable():
					filepath.setWritable()

				hasBeenHandled = True

		ret = pathWrite( filepath, contentsStr )

		if isUnderClient and not hasBeenHandled:
			_p4fast( 'add', filepath )

		return ret

	return pathWrite( filepath, contentsStr )


pathPickle = Path.pickle
def _p4Pickle( filepath, toPickle, doP4=True ):
	assert isinstance( filepath, Path )
	if doP4 and isPerforceEnabled():

		hasBeenHandled = False

		isUnderClient = P4File().isUnderClient( filepath )
		if filepath.exists():
			if not filepath.getWritable():
				_p4fast( 'edit', filepath )
				if not filepath.getWritable():
					filepath.setWritable()

				hasBeenHandled = True

		ret = pathPickle( filepath, toPickle )

		if isUnderClient and not hasBeenHandled:
			#need to explicitly add pickled files as binary type files, otherwise p4 mangles them
			_p4fast( 'add -t binary', filepath )

		return ret

	return pathPickle( filepath, toPickle )


pathDelete = Path.delete
def _p4Delete( filepath, doP4=True ):
	if doP4 and isPerforceEnabled():
		try:
			asP4 = P4File( filepath )
			if asP4.managed():
				if asP4.action is None:
					asP4.delete()
					if not filepath.exists():
						return
				else:
					asP4.revert()
					asP4.delete()

					#only return if the file doesn't exist anymore - it may have been open for add in
					#which case we still need to do a normal delete...
					if not filepath.exists():
						return
		except Exception, e: pass

	return pathDelete( filepath )


pathRename = Path.rename
def _p4Rename( filepath, newName, nameIsLeaf=False, doP4=True ):
	'''
	it is assumed newPath is a fullpath to the new dir OR file.  if nameIsLeaf is True then
	newName is taken to be a filename, not a filepath.  the instance is modified in place.
	if the file is in perforce, then a p4 rename (integrate/delete) is performed
	'''

	newPath = Path( newName )
	if nameIsLeaf:
		newPath = filepath.up() / newName

	if filepath.isfile():
		tgtExists = newPath.exists()
		if doP4 and isPerforceEnabled():
			reAdd = False
			change = None
			asP4 = P4File( filepath )

			#if its open for add, revert - we're going to rename the file...
			if asP4.action == 'add':
				asP4.revert()
				change = asP4.getChange()
				reAdd = True

			#so if we're managed by p4 - try a p4 rename, and return on success.  if it
			#fails however, then just do a normal rename...
			if asP4.managed():
				asP4.rename( newPath )
				return newPath

			#if the target exists and is managed by p4, make sure its open for edit
			if tgtExists and asP4.managed( newPath ):
				_p4fast( 'edit', newPath )

			#now perform the rename
			ret = pathRename( filepath, newName, nameIsLeaf )

			if reAdd:
				_p4fast( 'add', newPath )
				asP4.setChange( change, newPath )

			return ret
	elif filepath.isdir():
		raise NotImplementedError( 'dir renaming not implemented yet...' )

	return pathRename( filepath, newName, nameIsLeaf )


pathCopy = Path.copy
def _p4Copy( filepath, target, nameIsLeaf=False, doP4=True ):
	'''
	same as rename - except for copying.  returns the new target name
	'''
	if filepath.isfile():
		target = Path( target )
		if nameIsLeaf:
			target = filepath.up() / target

		if doP4 and isPerforceEnabled():
			try:
				asP4 = P4File( filepath )
				tgtAsP4 = P4File( target )
				if asP4.managed() and tgtAsP4.isUnderClient():
					#so if we're managed by p4 - try a p4 rename, and return on success.  if it
					#fails however, then just do a normal rename...
					asP4.copy( target )

					return target
			except: pass

	return pathCopy( filepath )


def lsP4( queryStr, includeDeleted=False ):
	'''
	returns a list of dict's containing the clientFile, depotFile, headRev, headChange and headAction
	'''
	filesAndDicts = []
	queryLines = _p4run( 'files', queryStr )
	for line in queryLines:
		fDict = {}

		toks = line.split( ' ' )

		#deal with error lines, or exit lines (an exit prefix may not actually mean the end of the data - the query may have been broken into batches)
		if line.startswith( 'exit' ):
			continue

		if line.startswith( 'error' ):
			continue

		fData = toks[ 0 ]
		idx = fData.index( '#' )
		f = Path( fData[ :idx ] )
		fDict[ 'depotPath' ] = f

		rev = int( fData[ idx+1: ] )
		fDict[ 'headRev' ] = rev

		action = toks[ 2 ]
		fDict[ 'headAction' ] = action

		if action == 'delete' and not includeDeleted:
			continue

		fDict[ 'headChange' ] = toks[ 4 ]

		filesAndDicts.append( (f, fDict) )

	diskPaths = toDiskPaths( [f[0] for f in filesAndDicts] )

	lsResult = []
	for diskPath, (f, fDict) in zip( diskPaths, filesAndDicts ):
		fDict[ 'clientFile' ] = diskPath
		lsResult.append( fDict )

	return lsResult


def toDepotAndDiskPaths( files ):
	caseMatters = Path.DoesCaseMatter()

	lines = []
	for filesChunk in iterBy( files, 15 ):
		lines += _p4run( 'where', *filesChunk )[ :-1 ]  #last line is the "exit" line...

	paths = []
	for f, line in zip( map( Path, files ), lines ):
		fName = f[ -1 ]
		fNameLen = len( fName )

		manipLine = line

		if not caseMatters:
			manipLine = line.lower()
			fName = fName.lower()

		#I'm not entirely sure this is bullet-proof...  but basically the return string for this command
		#is a simple space separated string, with three values.  i guess I could try to match //HOSTNAME
		#and the client's depot root to find the start of files, but for now its simply looking for the
		#file name substring three times
		depotNameIdx = manipLine.find( fName ) + fNameLen
		depotName = P4File( line[ :depotNameIdx ], caseMatters )

		workspaceNameIdx = manipLine.find( fName, depotNameIdx ) + fNameLen
		#workspaceName = P4File( line[ depotNameIdx + 1:workspaceNameIdx ], caseMatters )

		diskNameIdx = manipLine.find( fName, workspaceNameIdx ) + fNameLen
		diskName = P4File( line[ workspaceNameIdx + 1:diskNameIdx ], caseMatters )

		paths.append( (depotName, diskName) )

	return paths


def toDepotPaths( files ):
	'''
	return the depot paths for the given list of disk paths
	'''
	return [ depot for depot, disk in toDepotAndDiskPaths( files ) ]


def toDiskPaths( files ):
	'''
	return the depot paths for the given list of disk paths
	'''
	return [ disk for depot, disk in toDepotAndDiskPaths( files ) ]


def isPerforceEnabled():
	return P4File.USE_P4


def enablePerforce( state=True ):
	'''
	sets the enabled state of perforce
	'''
	P4File.USE_P4 = bool( state )

	#hook up various convenience functions on the Path class, and plug in the overrides for operations
	#such as write, delete, rename etc...  This makes using perforce in conjunction with the Path class
	#transparent to the programmer
	if state:
		Path.asP4 = asP4
		Path.edit = edit
		Path.editoradd = edit
		Path.add = add
		Path.revert = revert
		Path.asDepot = asDepot

		Path.write = _p4write
		Path.pickle = _p4Pickle

		Path.delete = _p4Delete
		Path.rename = _p4Rename
		Path.copy = _p4Copy

	#restore the overridden methods on the Path class and delete any of the convenience methods added
	else:
		try:
			del( Path.asP4 )
			del( Path.edit )
			del( Path.editoradd )
			del( Path.add )
			del( Path.revert )
			del( Path.asDepot )

		#if any of the above throw an Attribute error, presumably perforce hasn't been setup yet so assume none are present and just pass
		except AttributeError: pass

		#if perforce hasn't been setup already, doing this is harmless...
		Path.write = pathWrite
		Path.pickle = pathPickle

		Path.delete = pathDelete
		Path.rename = pathRename
		Path.copy = pathCopy


def disablePerforce():
	'''
	alias for enablePerforce( False )
	'''
	enablePerforce( False )


def d_preserveDefaultChange(f):
	'''
	decorator to preserve the default changelist
	'''
	def newF( *a, **kw ):
		global DEFAULT_CHANGE
		preChange = DEFAULT_CHANGE
		try: f( *a, **kw )
		except:
			DEFAULT_CHANGE = preChange
			raise

		DEFAULT_CHANGE = preChange

	newF.__doc__ = f.__doc__
	newF.__name__ = f.__name__

	return newF


def syncFiles( files, force=False, rev=None, change=None ):
	'''
	syncs a given list of files to either the headRev (default) or a given changelist,
	or a given revision number
	'''
	p4 = P4File()
	if rev is not None:
		ret = []
		for f in files:
			if force:
				r = p4.sync( '-f', f, rev )
			else:
				r = p4.sync( f, rev )

			ret.append( r )

		return ret
	elif change is not None:
		args = [ 'sync' ]
		if force:
			args.append( '-f' )

		args += [ '%s@%d' % (f, change) for f in files ]

		return p4run( *args )
	else:
		args = files
		if force:
			args = [ '-f' ] + args

		return p4.run( 'sync', *args )


def findStaleFiles( fileList ):
	'''
	given a list of files (can be string paths or Path instances) returns a list of "stale" files.  stale files are simply
	files that aren't at head revision
	'''
	p4 = P4File()
	stale = []
	for f in fileList:
		latest = p4.isLatest( f )
		if latest is None:
			continue

		if not latest:
			stale.append( f )

	return stale


def gatherFilesIntoChange( files, change=None ):
	'''
	gathers the list of files into a single changelist - if no change is specified, then the
	default change is used
	'''
	p4 = P4File()
	filesGathered = []
	for f in files:
		if not isinstance( f, Path ): f = Path( f )

		try:
			stat = p4.getStatus( f )
		except IndexError: continue

		if not stat:
			try:
				if not f.exists():
					continue
			except TypeError: continue

			#in this case, the file isn't managed by perforce - so add it
			print 'adding file:', f
			p4.add( f )
			p4.setChange(change, f)
			filesGathered.append( f )
			continue

		#otherwise, see what the action is on the file - if there is no action then the user hasn't
		#done anything to the file, so move on...
		try:
			action = stat[ 'action' ]
			p4.setChange( change, f )
			filesGathered.append( f )
		except KeyError: continue

	return filesGathered


def cleanEmptyChanges():
	p4 = P4File()
	for change in P4Change.IterPending():
		deleteIt = False
		try:
			deleteIt = not change.files
		except KeyError: deleteIt = True

		if deleteIt:
			p4run( 'change -d', str( change ) )


def findRedundantPYCs( rootDir=None, recursive=True ):
	'''
	lists all orphaned files under a given directory.  it does this by looking at the pyc/pyo file and seeing if its corresponding
	py file exists on disk, or in perforce in any form.  if it does, it deletes the file...
	'''
	if rootDir is None:
		rootDir = tools()

	bytecodeExtensions = [ 'pyc', 'pyo' ]
	exceptions = [ 'p4' ]

	rootDir = Path( rootDir )
	orphans = []
	if rootDir.exists():
		p4 = P4File()
		files = rootDir.files( recursive=recursive )
		bytecodeFiles = []
		for f in files:
			for byteXtn in bytecodeExtensions:
				if f.hasExtension( byteXtn ):
					if f.name().lower() in exceptions:
						continue

					bytecodeFiles.append( f )

		for f in bytecodeFiles:
			pyF = Path( f ).setExtension( 'py' )

			#is there a corresponding py script for this file?  if it does, the pyc is safe to delete - so delete it
			if pyF.exists():
				f.reason = 'corresponding py script found'
				orphans.append( f )
				continue

			#if no corresponding py file exists for the pyc, then see if there is/was one in perforce...  if the
			#corresponding py file is in perforce in any way, shape or form, then delete the .pyc file - its derivative and
			#can/will be re-generated when needed
			stat = p4.getStatus( pyF )
			if stat is None:
				continue

			f.reason = 'corresponding py file in perforce'
			orphans.append( f )

	return rootDir, orphans


def deleteRedundantPYCs( rootDir=None, recursive=True, echo=False ):
	'''
	does a delete on orphaned pyc/pyo files
	'''
	rootDir, orphans = findRedundantPYCs( rootDir, recursive )

	for f in orphans:
		if echo:
			try:
				print f - rootDir, f.reason
			except AttributeError:
				pass

		f.delete()


