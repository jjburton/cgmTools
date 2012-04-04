
from zooPy import strUtils
from apiExtensions import *


def findItem( itemName ):
	itemName = str( itemName )
	if cmd.objExists( itemName ):
		return itemName

	match = matchNames( itemName, cmd.ls( type='transform' ) )[ 0 ]
	if match:
		return match

	return None


def resolveMappingToScene( mapping ):
	'''
	takes a mapping and returns a mapping with actual scene objects
	'''
	assert isinstance( mapping, strUtils.Mapping )
	return matchNames( mapping.srcs, mapping.tgts )


def getNamespacesFromStrings( theStrs ):
	'''
	returns list of all the namespaces found in the given list of strings
	'''
	namespaces = set()
	for aStr in theStrs:
		namespaces.add( ':'.join( aStr.split( '|' )[-1].split( ':' )[ :-1 ] ) )

	return list( namespaces )


def matchNames( srcObjs, tgtObjs ):
	namespaces = getNamespacesFromStrings( tgtObjs )
	tgtObjsSet = set( tgtObjs )
	mappedTgts = []

	namespacesToTest = []
	for namespace in namespaces:
		namespaceToks = [ tok for tok in namespace.split( '|' )[-1].split( ':' ) if tok ]
		for n, tok in enumerate( namespaceToks ):
			namespacesToTest.append( ':'.join( namespaceToks[ :n+1 ] ) )

	for srcObj in srcObjs:

		#see if the exact source is in the target list
		if srcObj in tgtObjsSet:
			mappedTgts.append( srcObj )

		#if not see if we're able to prepend the given namespace
		else:
			sourceNodeToks = srcObj.split( '|' )[-1].split( ':' )
			nodeName = sourceNodeToks[-1]
			foundCandidate = False
			for candidateNamespace in namespacesToTest:
				candidate = '%s:%s' % (candidateNamespace, nodeName)
				if candidate in tgtObjsSet:
					mappedTgts.append( candidate )
					foundCandidate = True
					break

			if not foundCandidate:
				if nodeName in tgtObjsSet:
					mappedTgts.append( nodeName )
				else:
					mappedTgts.append( '' )

	return strUtils.Mapping( srcObjs, mappedTgts )


#end
