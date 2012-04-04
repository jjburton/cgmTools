
from maya.cmds import *


def getNamespaceTokensFromReference( node ):
	'''
	returns a list of namespaces added to the given node via referencing
	'''
	if not referenceQuery( node, inr=True ):
		return []

	theReferenceFilepath = referenceQuery( node, filename=True )
	theReferenceNode = file( theReferenceFilepath, q=True, referenceNode=True )

	theReferenceNamespace = file( theReferenceFilepath, q=True, namespace=True )

	#now get the parent namespaces for the reference - these are the namespaces found on the reference node
	namespaces = theReferenceNode.split( ':' )

	#pop the last token - its the name of the reference node
	namespaces.pop()
	namespaces.append( theReferenceNamespace )

	return namespaces


def stripReferenceNamespaceFromNode( node ):
	'''
	strips off any namespaces from the given node that were added due to referencing
	'''
	referenceNamespaceToks = getNamespaceTokensFromReference( node )

	return stripNamespaceFromNode( node, referenceNamespaceToks )


def stripNamespaceFromNode( node, namespace ):
	'''
	Strips off the given namespace from the given node if possible

	If not possible, the original node name is returned
	'''
	if namespace.endswith( ':' ):
		namespace = namespace[ :-1 ]

	return stripNamespaceTokensFromNode( namespace.split( ':' ) )


def stripNamespaceTokensFromNode( node, namespaceToks ):
	'''
	Strips off the given namespace tokens from the given node if possible

	If not possible, the original node name is returned
	'''
	numNamespaceToks = len( namespaceToks )

	if not namespaceToks:
		return node

	#if the node name is a name path, we'll need to remove the referenced namespace tokens from each name path...
	pathToks = node.split( '|' )
	newPathToks = []
	for pathTok in pathToks:
		pathNamespaceToks = pathTok.split( ':' )
		if pathNamespaceToks[ :numNamespaceToks ] == namespaceToks:
			newPathToks.append( ':'.join( pathNamespaceToks[ numNamespaceToks: ] ) )
		else:
			newPathToks.append( pathTok )

	return '|'.join( newPathToks )


def addNamespaceTokNamePath( name, namespace ):
	'''
	adds the given namespace to a name path.

	example:
	addNamespaceTokNamePath( 'some|name|path', 'ns' )

	returns:
	'ns:some|ns:name|ns:path'
	'''
	if namespace.endswith( ':' ):
		namespace = namespace[ :-1 ]

	namespacedToks = []
	for pathTok in name.split( name, '|' ):
		namespacedToks.append( '%s:%s' % (namespace, name) )

	return '|'.join( namespacedToks )


#end
