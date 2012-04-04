'''
Referencing in maya kinda sucks.  Getting reference information from nodes/files is split across at least
3 different mel commands in typically awkward autodesk fashion, and there is a bunch of miscellaneous
functionality that just doesn't exist at all.  So this module is supposed to be a collection of
functionality that alleviates this somewhat...
'''

from maya.cmds import *
from zooPy.path import Path


def isFileReferenced( filepath ):
	return ReferencedFile.IsFilepathReferenced( filepath )


def stripNamespaceFromNamePath( name, namespace ):
	'''
	strips out the given namespace from a given name path.

	example:
	stripNamespaceFromNamePath( 'moar:ns:wow:some|moar:ns:wow:name|moar:ns:wow:path', 'ns' )

	returns:
	'wow:some|wow:name|wow:path'
	'''
	if namespace.endswith( ':' ):
		namespace = namespace[ :-1 ]

	cleanPathToks = []
	for pathTok in name.split( '|' ):
		namespaceToks = pathTok.split( ':' )
		if namespace in namespaceToks:
			idx = namespaceToks.index( namespace )
			namespaceToks = namespaceToks[ idx+1: ]

		cleanPathToks.append( ':'.join( namespaceToks ) )

	return '|'.join( cleanPathToks )


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


class ReferencedFile(object):

	@classmethod
	def IterAll( cls ):
		for referenceNode in ls( type='reference' ):
			try:
				referenceFilepath = Path( referenceQuery( referenceNode, filename=True ) )

			#maya throws an exception on "shared" references - whatever the F they are.  so catch and skip when this happens
			except RuntimeError: continue

			yield referenceFilepath
	@classmethod
	def IsFilepathReferenced( cls, filepath ):
		for refFilepath in cls.IterAll():
			if refFilepath == filepath:
				return True

		return False

	def __init__( self, filepath ):
		self._filepath = filepath
	def getReferenceNode( self ):
		return file( self._filepath, q=True, referenceNode=True )
	def getReferenceNamespace( self ):
		'''
		returns the namespace for this reference - this doesn't include referenced namespaces if this reference is nested
		'''
		return file( self._filepath, q=True, namespace=True )
	def isNested( self ):
		'''
		returns whether this reference is nested
		'''
		return referenceQuery( self.getReferenceNode(), inr=True )
	def load( self ):
		raise NotImplemented
	def unload( self ):
		raise NotImplemented


class ReferencedNode(object):
	def __init__( self, node ):
		self._node = node
		self._isReferenced = referenceQuery( node, inr=True )
	def isReferenced( self ):
		return self._isReferenced
	def getFilepath( self, copyNumber=False ):
		'''
		will return the filepath to the scene file this node comes from.  If copyNumber=True then the "copy number" will
		be included in the filepath - see the docs for the referenceQuery mel command for more information
		'''
		if not self._isReferenced:
			return None

		return Path( referenceQuery( self._node, filename=True, withoutCopyNumber=not copyNumber ) )
	def getReferencedFile( self, copyNumber=False ):
		return ReferencedFile( self.getFilepath() )
	def getReferenceNode( self ):
		if not self._isReferenced:
			return None

		return file( self.getFilepath(), q=True, referenceNode=True )
	def getNamespace( self ):
		raise NotImplemented
	def getReferenceNamespace( self ):
		'''
		returns the namespace for this reference - this doesn't include referenced namespaces if this reference is nested
		'''
		return file( self.getFilepath( True ), q=True, namespace=True )
	def getNode( self ):
		return self._node
	def getUnreferencedNode( self ):
		'''
		returns the node name as it would be in the scene the node comes from
		'''
		refNode = self.getReferenceNode()

		return stripNamespaceFromNamePath( self._node, self.getReferenceNamespace() )
	def removeEdits( self ):
		raise NotImplemented


#end
