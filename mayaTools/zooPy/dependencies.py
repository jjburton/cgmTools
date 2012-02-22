
import subprocess
import marshal
import inspect
import pickle
import time
import imp
import sys
import os
import gc

from zlib import crc32
from modulefinder import ModuleFinder

from path import Path
from misc import removeDupes

_MODULE_TYPE = type( os )


def getPythonStdLibDir():
	'''
	returns the root directory of the current python interpreter's root directory
	'''
	return Path( inspect.getfile( os ) ).up()

_LIB_PATHS = ( getPythonStdLibDir(), )


def logMessage( *a ):
	print ' '.join( map( str, a ) )


logWarning = logMessage


def getDeps( aModule ):
	if not isinstance( aModule, _MODULE_TYPE ):
		raise TypeError( "must specify a module object" )

	dependencySet = set()

	getfile = inspect.getfile
	def _getDeps( module ):
		#grab module dependencies
		for n, o in aModule.__dict__.iteritems():
			try:
				objectFile = Path( getfile( o ) )
			#this happens on builtins...  so skip em
			except TypeError:
				continue

			if isinstance( o, _MODULE_TYPE ):
				if objectFile in dependencySet:
					continue

				dependencySet.add( objectFile )
				_getDeps( o )  #recurse
			else:
				dependencySet.add( objectFile )

	_getDeps( aModule )

	return dependencySet


def isScriptInSuperiorBranch( scriptPath ):
	'''
	returns whether the given scriptPath can be found in a directory searched before
	the given script.  Ie, if the following paths are in sys.path:
	sys.path = [ 'd:/somePath', 'd:/otherPath' ]

	isScriptInSuperiorBranch( 'd:/otherPath/someScript.py' )

	if there is a someScript.py in d:/somePath, this function will return True
	'''
	if not isinstance( scriptPath, Path ):
		scriptPath = Path( scriptPath )

	originalPath = scriptPath
	for p in sys.path:
		if scriptPath.isUnder( p ):
			scriptPath = scriptPath - p
			break

	for p in sys.path:
		possibleSuperiorPath = p / scriptPath
		if possibleSuperiorPath.exists():
			if possibleSuperiorPath == originalPath:
				return None

			return possibleSuperiorPath


class DependencyNode(dict):
	def addDepedency( self, callerScriptPaths ):
		curDepNode = self
		for callScript in callerScriptPaths[ 1: ]:  #skip the first item - its always the script being walked for dependencies

			#builtins have None for their paths as do modules in the stdlib if they're in a zip file, so break
			#because at this point we don't care about downstream deps because we don't change the stdlib
			if callScript is None:
				break

			curDepNode = curDepNode.setdefault( Path( callScript ), DependencyNode() )

		return curDepNode
	def findDependents( self, changedScriptPath ):
		affected = []
		for srcFile, depNode in self.iteritems():
			if srcFile == changedScriptPath:
				continue

			if changedScriptPath in depNode:
				affected.append( srcFile )
			else:
				if depNode:  #no point recursing if the depNode is empty
					affected += depNode.findDependents( changedScriptPath )

		return affected


class DepFinder(ModuleFinder):
	'''
	simple wrapper to ModuleFinder class to discover dependencies for a given script path

	NOTE: the script doesn't get executed, modulefinder just walks through the script bytecode,
	looks for imports that happen, and then asks python to resolve them to locations on disk
	'''

	#depth of the dependency tree - by default its just a single import deep - ie it only records immediate dependencies.
	#change this to None to make it arbitrary depth
	#NOTE: a depth of 1 is sufficient for deep dependency parsing because the DependencyTree has a 1-depth node for each script
	_DEPTH = 1

	def __init__( self, scriptPath, additionalPaths=(), depth=_DEPTH, *a, **kw ):
		self._depth = depth
		self._depNode = DependencyNode()
		self._callerStack = []

		ModuleFinder.__init__( self, *a, **kw )

		#add in the additional paths
		preSysPath = sys.path[:]
		for p in reversed( additionalPaths ):
			sys.path.insert( 0, str( p ) )

		#insert the path of the script
		sys.path.insert( 0, str( Path( scriptPath ).up() ) )

		try:
			self.run_script( scriptPath )
		except SyntaxError: pass
		finally:
			#restore the original sys.path
			sys.path = preSysPath
	def __contains__( self, item ):
		return item in self._depNode
	def __getitem__( self, item ):
		return self._depNode[ item ]
	def __setitem__( self, item, value ):
		self._depNode[ item ] = value
	def load_module( self, fqname, fp, pathname, file_info ):
		if pathname:
			if not isinstance( pathname, Path ):
				pathname = Path( pathname )

			if pathname.hasExtension( 'cmd' ):
				line = fp.readline().strip()
				suffix, mode, type = file_info[0], file_info[1], imp.PY_SOURCE  #pretend the cmd script is a py file
				assert '@setlocal' in line and '& python' in line, "Doesn't seem to be a python cmd script!"

		return ModuleFinder.load_module( self, fqname, fp, pathname, file_info )
	def import_hook( self, name, caller=None, fromlist=None, level=None ):
		if caller is None:
			return None

		try:
			self._callerStack.append( caller.__file__ )

			return ModuleFinder.import_hook( self, name, caller, fromlist )
		finally:
			self._callerStack.pop()
	def import_module( self, partnam, fqname, parent ):
		depth = self._depth
		if depth is None or len( self._callerStack ) <= depth:
			r = ModuleFinder.import_module( self, partnam, fqname, parent )
			if r is not None:
				self._depNode.addDepedency( self._callerStack +[ r.__file__ ] )

			return r
	def getDependencyNode( self ):
		return self._depNode
	def findDependents( self, changedScriptPath ):
		return self._depNode.findDependents( changedScriptPath )


def generateFileCRC( filePath ):
	with file( filePath, 'rb' ) as f:
		return crc32( f.read() )


class DependencyTree(DependencyNode):
	_VERSION = 0
	_CACHE_PATH = Path( '~/_py_dep_cache' )

	@classmethod
	def _convertDictDataTo( cls, theDict, keyCastMethod ):
		def convToDict( theDict ):
			for key in theDict.keys():
				value = theDict.pop( key )
				key = keyCastMethod( key )
				theDict[ key ] = value

				if isinstance( value, dict ):
					convToDict( value )

		convToDict( theDict )

		return theDict
	@classmethod
	def ToSimpleDict( cls, theDict ):
		cls._convertDictDataTo( theDict, str )
	@classmethod
	def FromSimpleDict( cls, theDict ):
		cls._convertDictDataTo( theDict, Path )

	def __new__( cls, dirsToWalk=(), dirsToExclude=(), extraSearchPaths=(), rebuildCache=False, skipLib=True ):
		'''
		constructs a new dependencyTree dictionary or loads an existing one from a disk cache, and
		strips out files that no longer exist
		'''
		if not dirsToWalk:
			dirsToWalk = sys.path[:]

		dirsToWalk = map( Path, dirsToWalk )
		dirsToExclude = map( Path, dirsToExclude )
		if skipLib:
			dirsToExclude += _LIB_PATHS

		cache = Path( cls._CACHE_PATH )

		self = None
		if cache.exists() and not rebuildCache:
			try:
				with file( cache, 'r' ) as f:
					version, self = pickle.load( f )
			except: pass
			else:
				if version == cls._VERSION:
					cls.FromSimpleDict( self )  #keys are converted to strings before pickling - so convert them back to Path instances
					cls.FromSimpleDict( self._crcs )
					cls.FromSimpleDict( self._stats )

					#remove any files from the cache that don't exist
					for f in self.keys():
						if not f.exists():
							self.pop( f )
				else:
					self = None
					logWarning( 'VERSION UPDATE: forcing rebuild' )

		if self is None:
			self = dict.__new__( cls )
			self._crcs = {}
			self._stats = {}

		self._dirs = dirsToWalk
		self._dirsExclude = dirsToExclude
		self._extraPaths = extraSearchPaths
		self.freshenDependencies()

		return self
	def __init__( self, dirsToWalk=(), dirsToExclude=(), extraSearchPaths=(), rebuildCache=False, skipLib=True ):
		dict.__init__( self )
	def getFiles( self ):
		files = []
		for d in self._dirs:
			skipDir = False
			for dd in self._dirsExclude:
				if d.isUnder( dd ):
					skipDir = True
					break

			if skipDir:
				continue

			for dirPath, dirNames, fileNames in os.walk( d ):
				dirPath = Path( dirPath )

				skipDir = False
				for d in self._dirsExclude:
					if dirPath.isUnder( d ):
						skipDir = True
						break

				if skipDir:
					continue

				for f in fileNames:
					f = dirPath / f
					if f.hasExtension( 'py' ):
						files.append( f )

					#if the cmd script looks like its a python cmd script, then add it to the list - the DepFinder class knows how to deal with these files
					elif f.hasExtension( 'cmd' ):
						with file( f ) as fopen:
							line = fopen.readline().strip()
							if '@setlocal ' in line and '& python' in line:
								files.append( f )

		return files
	def freshenDependencies( self ):
		'''
		freshens the dependency tree with new files - deleted files are cleaned out of
		the cache at load time, see the __new__ method for details
		'''
		padding = 15

		start = time.clock()
		files = self.getFiles()

		extraSearchPaths = self._extraPaths
		stats = self._stats
		crcs = self._crcs
		for f in files:

			#do we need to re-parse dependencies?  first we check the data in the file stat
			checkCrc = False
			currentStat = os.stat( f ).st_mtime
			cachedStat = stats.get( f, None )
			if cachedStat == currentStat:
				continue

			#store the mod time
			stats[ f ] = currentStat

			#if they don't match, check the crc
			currentCrc = generateFileCRC( f )
			cachedCrc = crcs.get( f, 0 )
			if cachedCrc == currentCrc:
				continue
			elif cachedCrc == 0:
				logMessage( 'new file:'.ljust( padding ), f )
			else:
				logMessage( 'stale file:'.ljust( padding ), f )

			finder = DepFinder( f, extraSearchPaths )
			self[ f ] = finder.getDependencyNode()
			crcs[ f ] = currentCrc

		self.writeCache()
		logMessage( 'Time to update cache: %0.2g' % (time.clock()-start) )
		logMessage()
	def findDependents( self, changedScriptPath ):
		'''
		returns a 2-tuple of scripts that immediately rely on changedScriptPath.  ie: the scripts that directly
		import the queried script, and those that import the queried script by proxy.  Secondary scripts are any
		downstream script that imports the one in question - regardless of how far down the dependency chain it is.

		ie: given scriptA, scriptB, scriptC
		scriptA imports scriptB
		scriptB imports scriptC

		calling findDependents( scriptC ) will return scriptB as an immediate dependent, and scriptA as a
		secondary dependent
		'''
		changedScriptPath = Path( changedScriptPath )

		#make sure the script in question doesn't have a superior script
		hasSuperior = isScriptInSuperiorBranch( changedScriptPath )
		if hasSuperior is not None:
			logWarning( 'WARNING - a superior script was found: %s.  Using it for dependency query instead!' % hasSuperior )
			changedScriptPath = hasSuperior

		primaryAffected = set()
		secondaryAffected = set()

		#add the primary affected dependencies
		for script, depNode in self.iteritems():
			if script == changedScriptPath:
				continue

			#if the changedScript is in this dependency node, add the script to the list of affected
			if changedScriptPath in depNode:
				primaryAffected.add( script )

		#don't even start looking for secondary deps if there are no primary deps...
		if primaryAffected:
			#returns whether it has found any new dependencies
			def gatherSecondaryDependencies( theDepNode ):
				stillAdding = False
				for script, depNode in theDepNode.iteritems():
					if script == changedScriptPath:
						continue

					if script in primaryAffected or script in secondaryAffected:
						continue

					#if its not, we had better recurse and see if it is somewhere deeper in the dependency tree for this script
					else:
						for sub_script in depNode.iterkeys():
							if sub_script in primaryAffected or sub_script in secondaryAffected:
								secondaryAffected.add( script )
								stillAdding = True

				return stillAdding

			#keep calling gatherSecondaryDependencies until it returns False
			while gatherSecondaryDependencies( self ): pass

		return primaryAffected, secondaryAffected
	def findDependencies( self, scriptPath, depth=None, includeFilesFromExcludedDirs=True ):
		'''
		returns a list of dependencies for scriptPath
		'''
		scriptPath = Path( scriptPath )

		#make sure the script in question doesn't have a superior script
		hasSuperior = isScriptInSuperiorBranch( scriptPath )
		if hasSuperior is not None:
			logWarning( 'WARNING - a superior script was found: %s.  Using it for dependency query instead!' % hasSuperior )
			scriptPath = hasSuperior

		deps = set()

		maxDepth = depth
		def getDeps( script, depth=0 ):
			if maxDepth is not None and depth >= maxDepth:
				return

			if script in self:
				for ss in self[ script ]:
					if ss in deps:
						continue

					deps.add( ss )
					getDeps( ss, depth+1 )

		getDeps( scriptPath )

		#if we're not including files from excluded directories, go through the list of deps and remove files that are under any of the exlude dirs
		if not includeFilesFromExcludedDirs:
			depsWithoutExcludedFiles = []
			for dep in deps:
				shouldFileBeIncluded = True
				for excludeDir in self._dirsExclude:
					if dep.isUnder( excludeDir ):
						shouldFileBeIncluded = False
						break

				if shouldFileBeIncluded:
					depsWithoutExcludedFiles.append( dep )

			deps = depsWithoutExcludedFiles

		return list( sorted( deps ) )
	def writeCache( self ):
		self.ToSimpleDict( self )
		self.ToSimpleDict( self._crcs )
		self.ToSimpleDict( self._stats )

		with open( self._CACHE_PATH, 'w' ) as f:
			pickle.dump( (self._VERSION, self), f )

		self.FromSimpleDict( self )
		self.FromSimpleDict( self._crcs )
		self.FromSimpleDict( self._stats )
	def moduleNameToScript( self, moduleName ):
		modulePathFragment = Path( moduleName.replace( '.', '/' ) )
		moduleLeafName = modulePathFragment.name()
		for scriptPath in self:
			if scriptPath.name() == moduleLeafName or moduleLeafName in scriptPath:
				if makeScriptPathRelative( scriptPath ).setExtension() == modulePathFragment:
					return scriptPath

		raise ValueError( "Module cannot be mapped to any script" )


def _depTreeStr( scriptPath, dependencyTree, depth=None ):
	if not isinstance( scriptPath, Path ):
		scriptPath = Path( scriptPath )

	indent = '   '  #the string used to "indent" dependencies in the tree

	maxDepth = depth
	alreadySerialized = set()

	def genLines( script, depth=0 ):
		lines = []
		depthPrefix = indent * depth
		if maxDepth and depth >= maxDepth:
			return lines

		try:
			scriptDeps = dependencyTree[ script ]
		except KeyError:
			return lines

		alreadySerialized.add( script )
		for s in scriptDeps:
			lines.append( '%s%s' % (depthPrefix, s) )

			if s in alreadySerialized:
				continue

			alreadySerialized.add( s )
			lines += genLines( s, depth+1 )

		return lines

	lines = [ scriptPath ]
	lines += genLines( scriptPath, 1 )

	return '\n'.join( lines )


def printDepTree( scriptPath, dependencyTree, depth=None ):
	logMessage( _depTreeStr( scriptPath, dependencyTree, depth ) )


def generateDepTree( rebuildCache=False ):
	return DependencyTree( rebuildCache=rebuildCache )


def makeScriptPathRelative( scriptFilepath ):
	'''
	will attempt to transform the name of the given script into the shortest possible path relative
	to the python search paths defined in sys.path.

	For example, just say you have a package called "foo"
	this package contains the script: "bar.py"

	given the full path to bar.py this function will return:
	"foo/bar.py"
	'''
	scriptFilepath = Path( scriptFilepath )

	sysPaths = map( Path, sys.path )
	bestFitPath = None
	for p in sysPaths:
		if scriptFilepath.isUnder( p ) or len( p ) > len( bestFitPath ):
			if bestFitPath is None:
				bestFitPath = p

	if bestFitPath is None:
		raise ValueError( "Cannot find a path under any of the paths in sys.path!" )

	shortestPath = scriptFilepath - bestFitPath

	return shortestPath


def packageScripts( scriptFilesToPackage, destPackageFilepath, dependencyTree ):
	'''
	will package all given files and import dependencies into a single zip file
	'''
	destPackageFilepath = Path( destPackageFilepath ).setExtension( 'zip' )
	if destPackageFilepath.exists():
		destPackageFilepath.delete()

	filesToPackage = map( Path, scriptFilesToPackage )
	for f in scriptFilesToPackage:
		filesToPackage += dependencyTree.findDependencies( f, None, False )

	if not filesToPackage:
		return None

	#remove any duplicate files...
	filesToPackage = removeDupes( filesToPackage )

	#this is a little hacky - but we don't want to re-distribute wingdbstub so lets check to see if its in the list of files
	for f in filesToPackage:
		if f.name() == 'wingdbstub':
			filesToPackage.remove( f )
			break

	#now build the zip file
	import zipfile
	with zipfile.ZipFile( str( destPackageFilepath ), 'w' ) as thePackage:
		for f in filesToPackage:
			thePackage.write( str( f ), str( makeScriptPathRelative( f ) ) )

	return destPackageFilepath


def getScriptTests( scriptFilepath, depTree=None ):
	if not isinstance( scriptFilepath, Path ):
		scriptFilepath = Path( scriptFilepath )

	if depTree is None:
		depTree = generateDepTree()

	testDependencyDict = {}
	for script in depTree:
		if script.name().startswith( 'devTest_' ):
			testDependencyDict[ script ] = depTree.findDependencies( script )

	scriptTestCandidates = []

	for test, testDependencies in testDependencyDict.iteritems():
		if scriptFilepath in testDependencies:
			scriptTestCandidates.append( test )

	return scriptTestCandidates


def flush( dirsNeverToFlush=() ):
	'''
	flushes all loaded modules from sys.modules which causes them to be reloaded
	when next imported...  super useful for developing crap within a persistent
	python environment

	dirsNeverToFlush should be a list - scripts under any of directories in this
	list won't be flushed
	'''

	dirsNeverToFlush = list( dirsNeverToFlush )  #these dirs never get flushed

	keysToDelete = []

	dirsNeverToFlush.extend( _LIB_PATHS )
	flushableExtensions = 'py', 'pyc', 'pyo'
	builtin_module_names = set( sys.builtin_module_names )
	while True:
		try:
			for modName, mod in sys.modules.items():
				try:
					modPath = Path( mod.__file__ )
				except AttributeError: continue

				#if its in the list of builtin module names, skip it - no point flushing builtins
				if modName in builtin_module_names:
					continue

				#only flush the module if has a valid extension - binary modules don't unload properly in CPython
				if modPath.getExtension() not in flushableExtensions:
					continue

				doFlush = True
				for ignoreDir in dirsNeverToFlush:
					if modPath.isUnder( ignoreDir ):
						doFlush = False
						break

				if doFlush:
					keysToDelete.append( modName )

			break

		#sometimes the sys.modules dict changes while the above loop is happening which causes a runtimeerror to be thrown.  so just try again if it happens...
		except RuntimeError:
			continue

	for keyToDelete in keysToDelete:
		try:
			del( sys.modules[ keyToDelete ] )
		except KeyError: continue

	#force a garbage collection
	gc.collect()


#end
