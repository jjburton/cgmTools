
from maya.OpenMaya import *
from zooPy.vectors import Vector, Matrix

import sys
import maya.cmds as cmd
import time

getAttr = cmd.getAttr
setAttr = cmd.setAttr


MObject.__MPlug__ = None

def asMObject( otherMobject ):
	'''
	tries to cast the given obj to an mobject - it can be string
	'''
	if isinstance( otherMobject, basestring ):
		sel = MSelectionList()
		sel.add( otherMobject )

		if '.' in otherMobject:
			plug = MPlug()
			sel.getPlug( 0, plug )
			tmp = plug.asMObject()
			tmp.__MPlug__ = plug
		else:
			tmp = MObject()
			sel.getDependNode( 0, tmp )

		return tmp

	if isinstance( otherMobject, (MObject, MObjectHandle) ):
		return otherMobject


def asMDagPath( otherMobject ):
	return asMObject( otherMobject ).dagPath()


def asMPlug( otherMobject ):
	if '.' in otherMobject:
		sel = MSelectionList()
		sel.add( otherMobject )

		plug = MPlug()
		sel.getPlug( 0, plug )

		return plug


def _asDependencyNode( self ):
	if not self.hasFn( MFn.kDependencyNode ):
		return None

	if self.__MDependencyNode__ is None:
		self.__MDependencyNode__ = dep = MFnDependencyNode( self )
		return dep
	else:
		return self.__MDependencyNode__

MObject.__MDependencyNode__ = None
MObject.dependencyNode = _asDependencyNode

def _asDag( self ):
	if not self.hasFn( MFn.kDagNode ):
		return None

	if self.__MDagPath__ is None:
		self.__MDagPath__ = dag = MDagPath()
		MDagPath.getAPathTo( self, dag )

		return dag
	else:
		return self.__MDagPath__

MObject.__MDagPath__ = None
MObject.dagPath = _asDag


def partialPathName( self ):
	'''
	returns the partial name of the node
	'''
	if self.isNull():
		return unicode()

	if isinstance( self, MObjectHandle ):
		self = self.object()

	dagPath = self.dagPath()
	if dagPath is not None:
		return dagPath.partialPathName()  #already a unicode instance

	if self.hasFn( MFn.kDependencyNode ):
		return MFnDependencyNode( self ).name()
	elif self.hasFn( MFn.kAttribute ):
		sel = MSelectionList()
		sel.add( self )
		node = MObject()
		self.getDependNode( 0, node )

		return unicode( MPlug( node, self ) )

	return u'<instance of %s>' % self.__class__

def __repr( self ):
	return repr( self.partialPathName() )

MObject.__str__ = MObjectHandle.__str__ = partialPathName
MObject.__repr__ = MObjectHandle.__repr__ = __repr
MObject.__unicode__ = MObjectHandle.__unicode__ = partialPathName
MObject.partialPathName = MObjectHandle.partialPathName = partialPathName
MObject.this = None  #stops __getattr__ from being called


def isNotEqual( self, other ):
	return not self == other

#override the default __eq__ operator on MObject.  NOTE: because the original __eq__ method is cached above,
#reloading this module can result in funkiness because the __eq__ gets cached on reload.  the alternative is
#to have an "originalMethods" script that never gets reloaded and stores original overridable methods
MObject.__ne__ = isNotEqual


def shortName( self ):
	return partialPathName( self ).split( '|' )[-1]

MObject.shortName = MObjectHandle.shortName = shortName


def _hash( self ):
	return MObjectHandle( self ).hashCode()

MObject.__hash__ = _hash


def _hash( self ):
	return self.hashCode()

MObjectHandle.__hash__ = _hash


def cmpNodes( a, b ):
	'''
	compares two nodes and returns whether they're equivalent or not - the compare is done on MObjects
	not strings so passing the fullname and a partial name to the same dag will still return True
	'''

	if a is b:
		return True

	#make sure the objects are valid types...
	if b is None:
		return False

	if isinstance( a, basestring ):
		a = asMObject( a )

	if isinstance( b, basestring ):
		b = asMObject( b )

	if not isinstance( a, MObject ):
		return False

	if not isinstance( b, MObject ):
		return False

	return a == b


def __eq( self, other ):
	if isinstance( other, basestring ):
		other = asMObject( other )

	return MObjectOriginalEquivalenceMethod( self, other )

#check to see if __eq__ has been setup already - if it has, the sys._MObjectOriginalEquivalenceMethod attribute will exist
if not hasattr( sys, '_MObjectOriginalEquivalenceMethod' ):
	sys._MObjectOriginalEquivalenceMethod = MObjectOriginalEquivalenceMethod = MObject.__eq__  #store on sys so that it doesn't get garbage collected when flush is called
	MObject.__eq__ = __eq
else:
	MObjectOriginalEquivalenceMethod = sys._MObjectOriginalEquivalenceMethod
	MObject.__eq__ = __eq
	print "mobject __eq__ already setup!"


#preGetAttr = MObject.__getattr__
def __getattr__( self, attr ):
	return MFnDependencyNode( self ).findPlug( attr )

#MObject.__getattr__ = __getattr__  #woah!  this can really really slow maya down...
MObject.getAttr = __getattr__


def iterAttrs( self, attrNamesToSkip=() ):
	'''
	iterates over all MPlugs belonging to this assumed to be dependency node
	'''

	depFn = MFnDependencyNode( self )
	for n in range( depFn.attributeCount() ):
		mattr = depFn.attribute( n )
		if mattr.isNull():
			continue

		mPlug = MPlug( self, mattr )
		mPlugName = mPlug.longName()

		skipAttr = False
		for skipName in attrNamesToSkip:
			if mPlugName == skipName:
				skipAttr = True
			elif mPlugName.startswith( skipName +'[' ) or mPlugName.startswith( skipName +'.' ):
				skipAttr = True

		if skipAttr:
			continue

		yield mPlug

MObject.iterAttrs = iterAttrs


def hasAttribute( self, attr ):
	return MFnDependencyNode( self ).hasAttribute( attr )

MObject.hasAttribute = hasAttribute


def getParent( self ):
	'''
	returns the parent of this node as an mobject
	'''
	if self.hasFn( MFn.kDagNode ):
		dagPath = MDagPath()
		MDagPath.getAPathTo( self, dagPath )
		dagNode = MFnDagNode( dagPath ).parent( 0 )
		if dagNode.apiType() == MFn.kWorld:
			return None

		return dagNode

def setParent( self, newParent, relative=False ):
	'''
	sets the parent of this node - newParent can be either another mobject or a node name
	'''
	dagMod = MDagModifier()
	dagMod.reparentNode( self, asMObject( newParent ) )
	dagMod.doIt()
	#cmd.parent( str( self ), str( newParent ), r=relative )

MObject.getParent = getParent
MObject.setParent = setParent


def hasUniqueName( self ):
	return MFnDependencyNode( self ).hasUniqueName()

MObject.hasUniqueName = hasUniqueName


def _rename( self, newName ):
	'''
	renames the node
	'''
	return cmd.rename( self, newName )

MObject.rename = _rename


def cleanShortName( self ):
	if not isinstance( self, basestring ):
		self = unicode( self )

	return self.split( ':' )[-1].split( '|' )[-1]

MObject.cleanShortName = cleanShortName


def getObjectMatrix( self ):
	dag = self.dagPath()
	if dag is None:
		return None

	return dag.getObjectMatrix()

MObject.getObjectMatrix = getObjectMatrix


def getWorldMatrix( self ):
	dag = self.dagPath()
	if dag is None:
		return None

	return dag.getWorldMatrix()

MObject.getWorldMatrix = getWorldMatrix


def getWorldInverseMatrix( self ):
	dag = self.dagPath()
	if dag is None:
		return None

	return dag.getWorldInverseMatrix()

MObject.getWorldInverseMatrix = getWorldInverseMatrix


def getParentMatrix( self ):
	dag = self.dagPath()
	if dag is None:
		return None

	return dag.getParentMatrix()

MObject.getParentMatrix = getParentMatrix


def getParentInverseMatrix( self ):
	dag = self.dagPath()
	if dag is None:
		return None

	return dag.getParentInverseMatrix()

MObject.getParentInverseMatrix = getParentInverseMatrix


### MDAGPATH CUSTOMIZATIONS ###

MDagPath.__str__ = MDagPath.partialPathName
MDagPath.__repr__ = MDagPath.partialPathName
MDagPath.__unicode__ = MDagPath.partialPathName
MDagPath.this = None


def getObjectMatrix( self ):
	return MFnTransform( self ).transformation().asMatrix().asNice()

MDagPath.getObjectMatrix = getObjectMatrix


def getWorldMatrix( self ):
	return self.inclusiveMatrix().asNice()

MDagPath.getWorldMatrix = getWorldMatrix


def getWorldInverseMatrix( self ):
	return self.inclusiveMatrixInverse().asNice()

MDagPath.getWorldInverseMatrix = getWorldInverseMatrix


def getParentMatrix( self ):
	return self.exclusiveMatrix().asNice()

MDagPath.getParentMatrix = getParentMatrix


def getParentInverseMatrix( self ):
	return self.exclusiveMatrixInverse().asNice()

MDagPath.getParentInverseMatrix = getParentInverseMatrix


### MPLUG CUSTOMIZATIONS ###

def __unicode__( self ):
	return self.name().replace( '[-1]', '[0]' )

MPlug.__str__ = __unicode__
MPlug.__repr__ = __unicode__
MPlug.__unicode__ = __unicode__
#MPlug.this = None  #stops __getattr__ from being called


def __getattr__( self, attr ):
	'''
	for getting child attributes
	'''
	if self.numChildren():
		return [ self.child(idx) for idx in range( self.numChildren() ) ]

def __getitem__( self, idx ):
	'''
	for getting indexed attributes
	'''
	if self.isArray():
		return self.elementByLogicalIndex( idx )

	raise TypeError( "Attribute %s isn't indexable" % self )

#MPlug.__getattr__ = __getattr__
#MPlug.__getitem__ = __getitem__
MPlug.asMObject = MPlug.attribute


def _set( self, value ):
	if isinstance( value, (list, tuple) ):
		setAttr( str(self), *value )
	else:
		setAttr( str(self), value )

def _get( self ):
	"""#WOW!  the api is SUPER dumb if you want to figure out how to get the value of an attribute...
	mobject = self.attribute()
	apiType = mobject.apiType()

	if mobject.hasFn( MFn.kNumericData ):
		dFn = MFnNumericData( mobject )
		dFnType = dFn.type()
		if dFnType == MFnNumericData.kBoolean:
			return self.asBool()
		elif dFnType in ( MFnNumericData.kInt, MFnNumericData.kShort, MFnNumericData.kLong ):
			return self.asInt()
		elif dFnType in ( MFnNumericData.kFloat, MFnNumericData.kDouble ):
			return self.asFloat()
	elif mobject.hasFn( MFn.kStringData ):
		if dFnType == MFnStringData.kString:
			return self.asString()
	"""
	val = getAttr( str(self) )  #use mel instead!
	if isinstance( val, list ):
		return val[ 0 ]

	return val

MPlug.GetValue = _get
MPlug.SetValue = _set


def _hash( self ):
	'''
	get the node hash, and add the hash of the  attribute name
	ie: the name of the attribute, not the path to the attribute
	'''
	return hash( self.node() ) + hash( '.'.join( self.name().split( '.' )[ 1: ] ) )

MPlug.__hash__ = _hash


def _longName( self ):
	return self.partialName( False, False, False, False, False, True )

MPlug.longName = _longName
MPlug.shortName = MPlug.partialName


def _aliasName( self ):
	#definedAliass = cmd.aliasAttr( self.node(), q=True )
	#longName = self.longName()
	#shortName = self.shortName()

	#if longName in definedAliass or shortName in definedAliass:
		#return self.partialName( False, False, False, True )

	#return longName
	return '.'.join( self.name().split( '.' )[ 1: ] )

MPlug.alias = _aliasName


def _isHidden( self ):
	if self.isElement():
		return bool( cmd.attributeQuery( self.array().longName(), n=self.node(), hidden=True ) )

	return bool( cmd.attributeQuery( self.longName(), n=self.node(), hidden=True ) )

MPlug.isHidden = _isHidden


### MVECTOR, MMATRIX CUSTOMIZATIONS ###

def __asNice( self ):
	return Vector( [self.x, self.y, self.z] )

MVector.asNice = __asNice
MPoint.asNice = __asNice


def __asNice( self ):
	values = []
	for i in range( 4 ):
		for j in range( 4 ):
			values.append( self(i, j) )

	return Matrix( values )

MMatrix.asNice = __asNice


def __str( self ):
	return str( self.asNice() )

MVector.__str__ = __str
MVector.__repr__ = __str
MVector.__unicode__ = __str

MPoint.__str__ = __str
MPoint.__repr__ = __str
MPoint.__unicode__ = __str


def _asPy( self ):
	return Vector( (self.x, self.y, self.z) )

MVector.asPy = _asPy


def __str( self ):
	return str( self.asNice() )

MMatrix.__str__ = __str
MMatrix.__repr__ = __str
MMatrix.__unicode__ = __str


def _asPy( self, size=4 ):
	values = []
	for i in range( size ):
		for j in range( size ):
			values.append( self( i, j ) )

	return Matrix( values, size )

MMatrix.asPy = _asPy


def __asMaya( self ):
	return MVector( *self )

Vector.asMaya = __asMaya


### UTILITIES ###

def castToMObjects( items ):
	'''
	is a reasonably efficient way to map a list of nodes to mobjects
	NOTE: this returns a generator - use list( castToMObjects( nodes ) ) to collapse the generator
	'''
	sel = MSelectionList()

	newItems = []
	for n, item in enumerate( items ):
		sel.add( item )
		mobject = MObject()
		sel.getDependNode( n, mobject )
		newItems.append( mobject )

	return newItems


def getSelected():
	items = []

	sel = MSelectionList()
	MGlobal.getActiveSelectionList( sel )

	for n in range( sel.length() ):
		mobject = MObject()
		sel.getDependNode( n, mobject )
		items.append( mobject )

	return items


def iterAll():
	'''
	returns a fast generator that visits all nodes of this class's type in the scene
	'''
	iterNodes = MItDependencyNodes()
	getItem = iterNodes.thisNode
	next = iterNodes.next  #cache next method for faster access inside the generator
	while not iterNodes.isDone():
		yield getItem()
		next()


def lsAll():

	return list( iterAll() )


def ls_( *a, **kw ):
	'''
	wraps the ls mel command so that it returns mobject instances instead of strings
	'''
	return castToMObjects( cmd.ls( *a, **kw ) or [] )


def filterByType( items, apiTypes ):
	'''
	returns a generator that will yield all items in the given list that match the given apiType enums
	'''
	if not isinstance( apiTypes, (list, tuple) ):
		apiTypes = [ apiTypes ]

	for item in items:
		if item.apiType() in apiTypes:
			yield item


def getNodesCreatedBy( function, *args, **kwargs ):
	'''
	returns a 2-tuple containing all the nodes created by the passed function, and
	the return value of said function
	'''

	#construct the node created callback
	newNodeHandles = []
	def newNodeCB( newNode, data ):
		newNodeHandles.append( MObjectHandle( newNode ) )

	def remNodeCB( remNode, data ):
		remNodeHandle = MObjectHandle( remNode )
		if remNodeHandle in newNodeHandles:
			newNodeHandles.remove( remNodeHandle )

	newNodeCBMsgId = MDGMessage.addNodeAddedCallback( newNodeCB )
	remNodeCBMsgId = MDGMessage.addNodeRemovedCallback( remNodeCB )

	ret = function( *args, **kwargs )
	MMessage.removeCallback( newNodeCBMsgId )
	MMessage.removeCallback( remNodeCBMsgId )

	newNodes = [ h.object() for h in newNodeHandles ]

	return newNodes, ret


def iterTopNodes( nodes ):
	kDagNode = MFn.kDagNode
	for node in castToMObjects( nodes ):
		if node.hasFn( kDagNode ):
			if node.getParent() is None:
				yield node


def iterParents( obj ):
	parent = cmd.listRelatives( obj, p=True, pa=True )
	while parent is not None:
		yield parent[ 0 ]
		parent = cmd.listRelatives( parent[ 0 ], p=True, pa=True )


def sortByHierarchy( objs ):
	sortedObjs = []
	for o in objs:
		pCount = len( list( iterParents( o ) ) )
		sortedObjs.append( (pCount, o) )

	sortedObjs.sort()

	return [ o[ 1 ] for o in sortedObjs ]


def stripTrailingDigits( name ):
	trailingDigits = []
	if name[ -1 ].isdigit():
		for idx, char in enumerate( reversed( name ) ):
			if not char.isdigit():
				return name[ :-idx ]

	return name


def iterNonUniqueNames():
	iterNodes = MItDag()  #type=MFn.kTransform )  #NOTE: only dag objects can have non-unique names...  despite the fact that the hasUniqueName method lives on MFnDependencyNode (wtf?!)
	while not iterNodes.isDone():
		mobject = iterNodes.currentItem()
		if not MFnDependencyNode( mobject ).hasUniqueName():  #thankfully instantiating MFn objects isn't slow - just MObject and MDagPath
			yield mobject

		iterNodes.next()


def fixNonUniqueNames():
	rename = cmd.rename
	for dagPath in iterNonUniqueNames():
		name = dagPath.partialPathName()
		newName = rename( name, stripTrailingDigits( name.split( '|' )[ -1 ] ) +'#' )
		print 'RENAMED:', name, newName


def selectNonUniqueNames():
	cmd.select( cl=True )
	theNodes = map( str, iterNonUniqueNames() )
	if theNodes:
		cmd.select( theNodes )


#end
