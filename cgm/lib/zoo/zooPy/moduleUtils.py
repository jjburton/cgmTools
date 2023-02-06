
import sys

from path import Path


def iterModuleNamesFromFilepath( filepath ):
	'''
	generator function that yields all possible top-level module names for the given filepath

	The first yielded is the first module name to the given filepath
	'''
	filepath = Path( filepath )
	dirpath = filepath.up()

	for p in sys.path:
		p = Path( p )
		if filepath.isUnder( p ):
			relpath = (filepath - p).setExtension()
			yield str( relpath ).replace( '/', '.' )


def sortByLength( strs ):
	return sorted( strs, cmp=lambda a, b: cmp( len(a), len(b) ) )


def getFirstModuleNameFromFilepath( filepath ):
	for moduleName in iterModuleNamesFromFilepath( filepath ):
		return moduleName

	raise ValueError( "The given filepath isn't discoverable given the current sys.path!" )


def getShortestModuleNameFromFilepath( filepath ):
	moduleNames = sortByLength( iterModuleNamesFromFilepath( filepath ) )
	return moduleNames[0]


def getLongestModuleNameFromFilepath( filepath ):
	moduleNames = sortByLength( iterModuleNamesFromFilepath( filepath ) )
	return moduleNames[-1]


#end
