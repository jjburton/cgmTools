"""
------------------------------------------
path_Utils: cgm.core.cgmPy
Authors: Hamish McKenzie & Josh Burton

Website : http://www.cgmonks.com
------------------------------------------
This is a rewrite of zoo.py.path because:
1) Maya 2017's version of python broke path and simple patching proved unsucessful
2) Hamish is no longer developing zoo

The main change is converting path from a subclass of string to one of object. This is where the 2017 issues stemmed from
================================================================
"""
#from __future__ import with_statement
#from cacheDecorators import *

import os
import re
import sys
import stat
import shutil
import cPickle
import datetime

DEFAULT_AUTHOR = 'default_username@your_domain.com'

#set the pickle protocol to use
PICKLE_PROTOCOL = 2

#set some variables for separators
NICE_SEPARATOR = '/'
NASTY_SEPARATOR = '\\'
NATIVE_SEPARATOR = (NICE_SEPARATOR, NASTY_SEPARATOR)[ os.name == 'nt' ]
PATH_SEPARATOR = '/' #(NICE_SEPARATOR, NASTY_SEPARATOR)[ os.name == 'nt' ]
OTHER_SEPARATOR = '\\' #(NASTY_SEPARATOR, NICE_SEPARATOR)[ os.name == 'nt' ]
UNC_PREFIX = PATH_SEPARATOR * 2


def cleanPath( pathString ):
    '''
    will clean out all nasty crap that gets into pathnames from various sources.
    maya will often put double, sometimes triple slashes, different slash types etc
    '''
    pathString = os.path.expanduser( str( pathString ) )
    path = pathString.strip().doReplace( OTHER_SEPARATOR, PATH_SEPARATOR )
    isUNC = path.startswith( UNC_PREFIX )
    while UNC_PREFIX in path:
        path = path.doReplace( UNC_PREFIX, PATH_SEPARATOR )

    if isUNC:
        path = PATH_SEPARATOR + path
    return path


ENV_REGEX = re.compile( "\%[^%]+\%" )
findall = re.findall

def resolveAndSplit( path, envDict=None, raiseOnMissing=False ):
    '''
    recursively expands all environment variables and '..' tokens in a pathname
    '''
    if envDict is None:
        envDict = os.environ

    path = os.path.expanduser( str( path ) )

    #first resolve any env variables
    if '%' in path:  #performing this check is faster than doing the regex
        matches = findall( ENV_REGEX, path )
        missingVars = set()
        while matches:
            for match in matches:
                try:
                    path = path.replace( match, envDict[ match[ 1:-1 ] ] )
                except KeyError:
                    if raiseOnMissing:
                        raise

                    missingVars.add( match )

            matches = set( findall( ENV_REGEX, path ) )

            #remove any variables that have been found to be missing...
            for missing in missingVars:
                matches.remove( missing )

    #now resolve any subpath navigation
    if OTHER_SEPARATOR in path:  #believe it or not, checking this first is faster
        path = path.replace( OTHER_SEPARATOR, PATH_SEPARATOR )

    #is the path a UNC path?
    isUNC = path[ :2 ] == UNC_PREFIX
    if isUNC:
        path = path[ 2: ]

    #remove duplicate separators
    duplicateSeparator = UNC_PREFIX
    while duplicateSeparator in path:
        path = path.replace( duplicateSeparator, PATH_SEPARATOR )

    pathToks = path.split( PATH_SEPARATOR )
    pathsToUse = []
    pathsToUseAppend = pathsToUse.append
    for n, tok in enumerate( pathToks ):
        if tok == "..":
            try: pathsToUse.pop()
            except IndexError:
                if raiseOnMissing:
                    raise

                pathsToUse = pathToks[ n: ]
                break
        else:
            pathsToUseAppend( tok )

    #finally convert it back into a path and pop out the last token if its empty
    path = PATH_SEPARATOR.join( pathsToUse )
    #path = os.path.join( pathsToUse )
    if not pathsToUse[-1]:
        pathsToUse.pop()

    #if its a UNC path, stick the UNC prefix
    if isUNC:
        return UNC_PREFIX + path, pathsToUse, True

    return path, pathsToUse, isUNC


def resolve( path, envDict=None, raiseOnMissing=False ):
    return resolveAndSplit( path, envDict, raiseOnMissing )[0]

resolvePath = resolve

sz_BYTES = 0
sz_KILOBYTES = 1
sz_MEGABYTES = 2
sz_GIGABYTES = 3

class Path(str):
    __CASE_MATTERS = os.name != 'nt'

    @classmethod
    def SetCaseMatter( cls, state ):
        cls.__CASE_MATTERS = state
    @classmethod
    def DoesCaseMatter( cls ):
        return cls.__CASE_MATTERS
    @classmethod
    def Join( cls, *toks, **kw ):
        return cls( '/'.join( toks ), **kw )

    def __new__( cls, path='', caseMatters=None, envDict=None ):
        '''
        if case doesn't matter for the path instance you're creating, setting caseMatters
        to False will do things like caseless equality testing, caseless hash generation
        '''
        #early out if we've been given a Path instance - paths are immutable so there is no reason not to just return what was passed in
        if isinstance( path, cls ):
            return path
        
        #set to an empty string if we've been init'd with None
        if path is None:
            path = ''

        resolvedPath, pathTokens, isUnc = resolveAndSplit( path, envDict )
        new = str.__new__( cls, resolvedPath )
        #new = super(cls.__class__, cls).__new__(cls)
        new.isUNC = isUnc
        new.hasTrailing = resolvedPath.endswith( PATH_SEPARATOR )
        new._splits = tuple( pathTokens )
        new._passed = path
        new._resolved = resolvedPath

        #case sensitivity, if not specified, defaults to system behaviour
        if caseMatters is not None:
            new.__CASE_MATTERS = caseMatters
        else:
            new.__CASE_MATTERS = caseMatters

        return new
    @classmethod
    def Temp( cls ):
        '''
        returns a temporary filepath - the file should be unique (i think) but certainly the file is guaranteed
        to not exist
        '''
        import datetime, random
        def generateRandomPathName():
            now = datetime.datetime.now()
            rnd = '%06d' % (abs(random.gauss(0.5, 0.5)*10**6))
            return '%TEMP%'+ PATH_SEPARATOR +'TMP_FILE_%s%s%s%s%s%s%s%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond, rnd)

        randomPathName = cls( generateRandomPathName() )
        while randomPathName.exists():
            randomPathName = cls( generateRandomPathName() )

        return randomPathName
    def __nonzero__( self ):
        '''
        a Path instance is "non-zero" if its not '' or '/'  (although I guess '/' is actually a valid path on *nix)
        '''
        selfStripped = self.strip()
        if selfStripped == '':
            return False

        if selfStripped == PATH_SEPARATOR:
            return False

        return True
    def __add__( self, other ):
        return self.__class__( '%s%s%s' % (self, PATH_SEPARATOR, other), self.__CASE_MATTERS )
    #the / or + operator both concatenate path tokens
    __div__ = __add__
    def __radd__( self, other ):
        return self.__class__( other, self.__CASE_MATTERS ) + self
    __rdiv__ = __radd__
    def __getitem__( self, item ):
        return self._splits[ item ]
    def __getslice__( self, a, b ):
        isUNC = self.isUNC
        if a:
            isUNC = False

        return self._toksToPath( self._splits[ a:b ], isUNC, self.hasTrailing )
    def __len__( self ):
        if not self:
            return 0

        return len( self._splits )
    def __contains__( self, item ):
        if not self.__CASE_MATTERS:
            return item.lower() in [ s.lower() for s in self._splits ]

        return item in list( self._splits )
    def __hash__( self ):
        '''
        the hash for two paths that are identical should match - the most reliable way to do this
        is to use a tuple from self.split to generate the hash from
        '''
        if not self.__CASE_MATTERS:
            return hash( tuple( [ s.lower() for s in self._splits ] ) )

        return hash( tuple( self._splits ) )
    def _toksToPath( self, toks, isUNC=False, hasTrailing=False ):
        '''
        given a bunch of path tokens, deals with prepending and appending path
        separators for unc paths and paths with trailing separators
        '''
        toks = list( toks )
        if isUNC:
            toks = ['', ''] + toks

        if hasTrailing:
            toks.append( '' )

        return self.__class__( PATH_SEPARATOR.join( toks ), self.__CASE_MATTERS )
    def resolve( self, envDict=None, raiseOnMissing=False ):
        '''
        will re-resolve the path given a new envDict
        '''
        if envDict is None:
            return self
        else:
            return Path( self._passed, self.__CASE_MATTERS, envDict )
    def unresolved( self ):
        '''
        returns the un-resolved path - this is the exact string that the path was instantiated with
        '''
        return self._passed
    def isEqual( self, other ):
        '''
        compares two paths after all variables have been resolved, and case sensitivity has been
        taken into account - the idea being that two paths are only equal if they refer to the
        same filesystem object.  NOTE: this doesn't take into account any sort of linking on *nix
        systems...
        '''
        if not isinstance( other, Path ):
            other = Path( other, self.__CASE_MATTERS )

        selfStr = str( self.asFile() )
        otherStr = str( other.asFile() )
        if not self.__CASE_MATTERS:
            selfStr = selfStr.lower()
            otherStr = otherStr.lower()

        return selfStr == otherStr
    __eq__ = isEqual
    def __ne__( self, other ):
        return not self.isEqual( other )
    def doesCaseMatter( self ):
        return self.__CASE_MATTERS
    def __repr__( self ):
        return str(self._resolved) 
    def asString(self):
        return str(self._resolved)         
    @classmethod
    def getcwd( cls ):
        '''
        returns the current working directory as a path object
        '''
        return cls( os.getcwd() )
    @classmethod
    def setcwd( cls, path ):
        '''
        simply sets the current working directory - NOTE: this is a class method so it can be called
        without first constructing a path object
        '''
        newPath = cls( path )
        try:
            os.chdir( newPath )
        except WindowsError: return None

        return newPath
    putcwd = setcwd
    def getStat( self ):
        try:
            return os.stat( self )
        except:
            #return a null stat_result object
            return os.stat_result( [ 0 for n in range( os.stat_result.n_sequence_fields ) ] )
    stat = property( getStat )
    def isAbs( self ):
        try:
            return os.path.isabs( str( self ) )
        except: return False
    def abs( self ):
        '''
        returns the absolute path as is reported by os.path.abspath
        '''
        return self.__class__( os.path.abspath( str( self ) ) )
    def split( self ):
        '''
        returns the splits tuple - ie the path tokens
        '''
        return list( self._splits )
    
    def asTruncate(self,startCull = 1,endCull=1,sep='|'):
        _l = self.split()
        try:
            return "{0} ... {1}".format(sep.join(_l[:startCull]),sep.join(_l[-endCull:]))
        except:
            return self.asString()
        
    def asDir( self ):
        '''
        makes sure there is a trailing / on the end of a path
        '''
        if self.hasTrailing:
            return self

        return self.__class__( '%s%s' % (self._passed, PATH_SEPARATOR), self.__CASE_MATTERS )
    asdir = asDir
    def asFile( self ):
        '''
        makes sure there is no trailing path separators
        '''
        if not self.hasTrailing:
            return self

        return self.__class__( str( self )[ :-1 ], self.__CASE_MATTERS )
    asfile = asFile
    def isDir( self ):
        '''
        bool indicating whether the path object points to an existing directory or not.  NOTE: a
        path object can still represent a file that refers to a file not yet in existence and this
        method will return False
        '''
        return os.path.isdir( self )
    isdir = isDir
    def isFile( self ):
        '''
        see isdir notes
        '''
        return os.path.isfile( self )
    isfile = isFile
    def getReadable( self ):
        '''
        returns whether the current instance's file is readable or not.  if the file
        doesn't exist False is returned
        '''
        try:
            s = os.stat( self )
            return s.st_mode & stat.S_IREAD
        except:
            #i think this only happens if the file doesn't exist
            return False
    def setWritable( self, state=True ):
        '''
        sets the writeable flag (ie: !readonly)
        '''
        try:
            setTo = stat.S_IREAD
            if state:
                setTo = stat.S_IWRITE

            os.chmod(self, setTo)
        except: pass
    def getWritable( self ):
        '''
        returns whether the current instance's file is writeable or not.  if the file
        doesn't exist True is returned
        '''
        try:
            s = os.stat( self )
            return s.st_mode & stat.S_IWRITE
        except:
            #i think this only happens if the file doesn't exist - so return true
            return True
    def getExtension( self ):
        '''
        returns the extension of the path object - an extension is defined as the string after a
        period (.) character in the final path token
        '''
        try:
            endTok = self[ -1 ]
        except IndexError:
            return ''

        idx = endTok.rfind( '.' )
        if idx == -1:
            return ''

        return endTok[ idx+1: ] #add one to skip the period
    def setExtension( self, xtn=None, renameOnDisk=False ):
        '''
        sets the extension the path object.  deals with making sure there is only
        one period etc...

        if the renameOnDisk arg is true, the file on disk (if there is one) is
        renamed with the new extension
        '''
        if xtn is None:
            xtn = ''

        #make sure there is are no start periods
        while xtn.startswith( '.' ):
            xtn = xtn[ 1: ]

        toks = list( self.split() )
        try:
            endTok = toks.pop()
        except IndexError:
            endTok = ''

        idx = endTok.rfind( '.' )
        name = endTok
        if idx >= 0:
            name = endTok[ :idx ]

        if xtn:
            newEndTok = '%s.%s' % (name, xtn)
        else:
            newEndTok = name

        if renameOnDisk:
            self.rename( newEndTok, True )
        else:
            toks.append( newEndTok )

        return self._toksToPath( toks, self.isUNC, self.hasTrailing )
    extension = property(getExtension, setExtension)
    def hasExtension( self, extension ):
        '''
        returns whether the extension is of a certain value or not
        '''
        ext = self.getExtension()
        if not self.__CASE_MATTERS:
            ext = ext.lower()
            extension = extension.lower()

        return ext == extension
    isExtension = hasExtension
    def name( self, stripExtension=True, stripAllExtensions=False ):
        '''
        returns the filename by itself - by default it also strips the extension, as the actual filename can
        be easily obtained using self[-1], while extension stripping is either a multi line operation or a
        lengthy expression
        '''
        try:
            name = self[ -1 ]
        except IndexError:
            return ''

        if stripExtension:
            pIdx = -1
            if stripAllExtensions:
                pIdx = name.find('.')
            else:
                pIdx = name.rfind('.')

            if pIdx != -1:
                return name[ :pIdx ]

        return name
    def up( self, levels=1 ):
        '''
        returns a new path object with <levels> path tokens removed from the tail.
        ie: Path("a/b/c/d").up(2) returns Path("a/b")
        '''
        if not levels:
            return self

        toks = list( self._splits )
        levels = max( min( levels, len(toks)-1 ), 1 )
        toksToJoin = toks[ :-levels ]
        if self.hasTrailing:
            toksToJoin.append( '' )

        return self._toksToPath( toksToJoin, self.isUNC, self.hasTrailing )
    
    def doReplace( self, search, replace='', caseMatters=None ):
        '''
        a simple search replace method - works on path tokens.  if caseMatters is None, then the system
        default case sensitivity is used
        '''
        print('path.doReplace...')
        idx = self.doFind( search, caseMatters )
        toks = list( self.split() )
        toks[ idx ] = replace

        return self._toksToPath( toks, self.isUNC, self.hasTrailing )
    
    def doFind( self, search, caseMatters=None ):
        '''
        returns the index of the given path token
        '''
        try:
            print('path.doFind...')            
            _bfr = str(self)
            if caseMatters is None:
                #in this case assume system case sensitivity - ie sensitive only on *nix platforms
                caseMatters = self.__CASE_MATTERS

            if not caseMatters:
                toks = [ s.lower() for s in self.split() ]
                search = search.lower()
            else:
                toks = self.split()

            idx = toks.index( search )

            return idx
        except:
            raise ValueError,"find Failure. {0} | search: {1} | caseMatters: {2}".format(_bfr,search,caseMatters)
    #index = find
    def exists( self ):
        '''
        returns whether the file exists on disk or not
        '''
        return os.path.exists( self )
    def matchCase( self ):
        '''
        If running under an env where file case doesn't matter, this method will return a Path instance
        whose case matches the file on disk.  It assumes the file exists
        '''
        if self.doesCaseMatter():
            return self

        for f in self.up().files():
            if f == self:
                return f
    def getSize( self, units=sz_MEGABYTES ):
        '''
        returns the size of the file in mega-bytes
        '''
        div = float( 1024 ** units )
        return os.path.getsize( self ) / div
    def create( self ):
        '''
        if the directory doesn't exist - create it
        '''
        if not self.exists():
            os.makedirs( str( self ) )
    def delete( self ):
        '''
        WindowsError is raised if the file cannot be deleted
        '''
        if self.isfile():
            selfStr = str( self )
            try:
                os.remove( selfStr )
            except WindowsError, e:
                os.chmod( selfStr, stat.S_IWRITE )
                os.remove( selfStr )
        elif self.isdir():
            selfStr = str( self.asDir() )
            for f in self.files( recursive=True ):
                f.delete()

            os.chmod( selfStr, stat.S_IWRITE )
            shutil.rmtree( selfStr, True )
    remove = delete
    def rename( self, newName, nameIsLeaf=False ):
        '''
        it is assumed newPath is a fullpath to the new dir OR file.  if nameIsLeaf is True then
        newName is taken to be a filename, not a filepath.  the fullpath to the renamed file is
        returned
        '''
        newPath = Path( newName )
        if nameIsLeaf:
            newPath = self.up() / newName

        if self.isfile():
            if newPath != self:
                if newPath.exists():
                    newPath.delete()

            #now perform the rename
            os.rename( self, newPath )
        elif self.isdir():
            raise NotImplementedError( 'dir renaming not implemented yet...' )

        return newPath
    move = rename
    def copy( self, target, nameIsLeaf=False ):
        '''
        same as rename - except for copying.  returns the new target name
        '''
        if self.isfile():
            target = Path( target )
            if nameIsLeaf:
                asPath = self.up() / target
                target = asPath

            if self == target:
                return target

            shutil.copy2( str( self ), str( target ) )

            return target
        elif self.isdir():
            shutil.copytree( str(self), str(target) )
    def read( self, strip=True ):
        '''
        returns a list of lines contained in the file. NOTE: newlines are stripped from the end but whitespace
        at the head of each line is preserved unless strip=False
        '''
        if self.exists() and self.isfile():
            fileId = file( self )
            if strip:
                lines = [line.rstrip() for line in fileId.readlines()]
            else:
                lines = fileId.read()
            fileId.close()

            return lines
    def write( self, contentsStr ):
        '''
        writes a given string to the file defined by self
        '''

        #make sure the directory to we're writing the file to exists
        self.up().create()

        with open( self, 'w' ) as f:
            f.write( str(contentsStr) )
    def pickle( self, toPickle ):
        '''
        similar to the write method but pickles the file
        '''
        self.up().create()

        with open( self, 'w' ) as f:
            cPickle.dump( toPickle, f, PICKLE_PROTOCOL )
    def unpickle( self ):
        '''
        unpickles the file
        '''
        fileId = file( self, 'rb' )
        data = cPickle.load(fileId)
        fileId.close()

        return data
    def relativeTo( self, other ):
        '''
        returns self as a path relative to another
        '''

        if not self:
            return None

        path = self
        other = Path( other )

        pathToks = path.split()
        otherToks = other.split()

        caseMatters = self.__CASE_MATTERS
        if not caseMatters:
            pathToks = [ t.lower() for t in pathToks ]
            otherToks = [ t.lower() for t in otherToks ]

        #if the first path token is different, early out - one is not a subset of the other in any fashion
        if otherToks[0] != pathToks[0]:
            return None

        lenPath, lenOther = len( path ), len( other )
        if lenPath < lenOther:
            return None

        newPathToks = []
        pathsToDiscard = lenOther
        for pathN, otherN in zip( pathToks[ 1: ], otherToks[ 1: ] ):
            if pathN == otherN:
                continue
            else:
                newPathToks.append( '..' )
                pathsToDiscard -= 1

        newPathToks.extend( path[ pathsToDiscard: ] )
        path = Path( PATH_SEPARATOR.join( newPathToks ), self.__CASE_MATTERS )

        return path
    __sub__ = relativeTo
    def __rsub__( self, other ):
        return self.__class__( other, self.__CASE_MATTERS ).relativeTo( self )
    def inject( self, other, envDict=None ):
        '''
        injects an env variable into the path - if the env variable doesn't
        resolve to tokens that exist in the path, a path string with the same
        value as self is returned...

        NOTE: a string is returned, not a Path instance - as Path instances are
        always resolved

        NOTE: this method is alias'd by __lshift__ and so can be accessed using the << operator:
        d:/main/content/mod/models/someModel.ma << '%VCONTENT%' results in %VCONTENT%/mod/models/someModel.ma
        '''

        toks = toksLower = self._splits
        otherToks = Path( other, self.__CASE_MATTERS, envDict=envDict ).split()
        newToks = []
        n = 0
        if not self.__CASE_MATTERS:
            toksLower = [ t.lower() for t in toks ]
            otherToks = [ t.lower() for t in otherToks ]

        while n < len( toks ):
            tok, tokLower = toks[ n ], toksLower[ n ]
            if tokLower == otherToks[ 0 ]:
                allMatch = True
                for tok, otherTok in zip( toksLower[ n + 1: ], otherToks[ 1: ] ):
                    if tok != otherTok:
                        allMatch = False
                        break

                if allMatch:
                    newToks.append( other )
                    n += len( otherToks ) - 1
                else:
                    newToks.append( toks[ n ] )
            else:
                newToks.append( tok )
            n += 1

        return PATH_SEPARATOR.join( newToks )
    __lshift__ = inject
    def findNearest( self ):
        '''
        returns the longest path that exists on disk
        '''
        path = self
        while not path.exists() and len( path ) > 1:
            path = path.up()

        if not path.exists():
            raise IOError( "Cannot find any path above this one" )

        return path
    getClosestExisting = findNearest
    nearest = findNearest
    def asFriendly( self ):
        '''
        returns a string with system native path separators
        '''
        return str( self ).replace( PATH_SEPARATOR, NATIVE_SEPARATOR )
    def osPath( self ):
        return str( self ).replace( PATH_SEPARATOR, os.path.sep )
    
    def startswith( self, other ):
        '''
        returns whether the current instance begins with a given path fragment.  ie:
        Path('d:/temp/someDir/').startswith('d:/temp') returns True
        '''
        if not isinstance( other, type( self ) ):
            other = Path( other, self.__CASE_MATTERS )

        otherToks = other.split()
        selfToks = self.split()
        if not self.__CASE_MATTERS:
            otherToks = [ t.lower() for t in otherToks ]
            selfToks = [ t.lower() for t in selfToks ]

        if len( otherToks ) > len( selfToks ):
            return False

        for tokOther, tokSelf in zip(otherToks, selfToks):
            if tokOther != tokSelf: return False

        return True
    isUnder = startswith
    def endswith( self, other ):
        '''
        determines whether self ends with the given path - it can be a string
        '''
        #copies of these objects NEED to be made, as the results from them are often cached - hence modification to them
        #would screw up the cache, causing really hard to track down bugs...  not sure what the best answer to this is,
        #but this is clearly not it...  the caching decorator could always return copies of mutable objects, but that
        #sounds wasteful...  for now, this is a workaround
        otherToks = list( Path( other ).split() )
        selfToks = list( self._splits )
        otherToks.reverse()
        selfToks.reverse()
        if not self.__CASE_MATTERS:
            otherToks = [ t.lower() for t in otherToks ]
            selfToks = [ t.lower() for t in selfToks ]

        for tokOther, tokSelf in zip(otherToks, selfToks):
            if tokOther != tokSelf:
                return False

        return True
    def _list_filesystem_items( self, itemtest, namesOnly=False, recursive=False ):
        '''
        does all the listing work - itemtest can generally only be one of os.path.isfile or
        os.path.isdir.  if anything else is passed in, the arg given is the full path as a
        string to the filesystem item
        '''
        if not self.exists():
            return
        if recursive:
            walker = os.walk( self.osPath() )
            for path, subs, files in walker:
                path = Path( path, self.__CASE_MATTERS )

                for sub in subs:
                    p = path / sub
                    if itemtest( p ):
                        if namesOnly:
                            p = p.name()

                        yield p
                    else: break  #if this doesn't match, none of the other subs will

                for item in files:
                    p = path / item
                    if itemtest( p ):
                        if namesOnly:
                            p = p.name()

                        yield p
                    else: break  #if this doesn't match, none of the other items will
        else:
            for item in os.listdir( self ):
                p = self / item
                if itemtest( p ):
                    if namesOnly:
                        p = p.name()

                    yield p
    def dirs( self, namesOnly=False, recursive=False ):
        '''
        returns a generator that lists all sub-directories.  If namesOnly is True, then only directory
        names (relative to the current dir) are returned
        '''
        return self._list_filesystem_items( os.path.isdir, namesOnly, recursive )
    def files( self, namesOnly=False, recursive=False ):
        '''
        returns a generator that lists all files under the path (assuming its a directory).  If namesOnly
        is True, then only directory names (relative to the current dir) are returned
        '''
        return self._list_filesystem_items( os.path.isfile, namesOnly, recursive )


def findFirstInPaths( filename, paths ):
    '''
    given a filename or path fragment, this will return the first occurance of a file with that name
    in the given list of search paths
    '''
    for p in map( Path, paths ):
        loc = p / filename
        if loc.exists():
            return loc

    raise Exception( "The file %s cannot be found in the given paths" % filename )


def findFirstInEnv( filename, envVarName ):
    '''
    given a filename or path fragment, will return the full path to the first matching file found in
    the given env variable
    '''
    return findFirstInPaths( filename, os.environ[ envVarName ].split( os.pathsep ) )


def findFirstInPath( filename ):
    '''
    given a filename or path fragment, will return the full path to the first matching file found in
    the PATH env variable
    '''
    return findFirstInEnv( filename, 'PATH' )


def findInPyPath( filename ):
    '''
    given a filename or path fragment, will return the full path to the first matching file found in
    the sys.path variable
    '''
    return findFirstInPaths( filename, sys.path )

#end
