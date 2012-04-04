
import inspect

import maya.cmds as cmd
from maya.cmds import *

from zooPy import names
from zooPy import typeFactories
from zooPy.names import Parity, Name, camelCaseToNice
from zooPy.vectors import Vector, Colour, Axis
from zooPy.path import Path
from zooPy.misc import removeDupes

import meshUtils
import rigUtils

from control import attrState, NORMAL, HIDE, LOCK_HIDE, NO_KEY
from apiExtensions import asMObject, castToMObjects, cmpNodes
from mayaDecorators import d_unifyUndo, d_maintainSceneSelection, d_showWaitCursor
from referenceUtils import ReferencedNode
from melUtils import mel, printErrorStr, mayaVar
from rigUtils import ENGINE_FWD, ENGINE_UP, ENGINE_SIDE
from rigUtils import MAYA_SIDE, MAYA_FWD, MAYA_UP
from rigUtils import Axis, resetSkinCluster

AXES = Axis.BASE_AXES

eval = __builtins__[ 'eval' ]  #restore the eval function to point to python's eval

TOOL_NAME = 'skeletonBuilder'

CHANNELS = ('x', 'y', 'z')
TYPICAL_HEIGHT = 70  #maya units

HUD_NAME = 'skeletonBuilderJointCountHUD'


#these are the symbols to use as standard rotation axes on bones...
BONE_AIM_VECTOR = ENGINE_FWD			#this is the axis the joint should bank around, in general the axis the "aims" at the child joint
BONE_ROTATE_VECTOR = ENGINE_SIDE		#this is the axis of "primary rotation" for the joint.  for example, the elbow would rotate primarily in this axis, as would knees and fingers

BONE_AIM_AXIS = Axis.FromVector( BONE_AIM_VECTOR )
BONE_ROTATE_AXIS = Axis.FromVector( BONE_ROTATE_VECTOR )

_tmp = BONE_AIM_AXIS.otherAxes()
_tmp.remove( BONE_ROTATE_AXIS )
BONE_OTHER_AXIS = _tmp[0]				#this is the "other" axis - ie the one thats not either BONE_AIM_AXIS or BONE_ROTATE_AXIS
BONE_OTHER_VECTOR = BONE_OTHER_AXIS.asVector()

del( _tmp )


getLocalAxisInDirection = rigUtils.getLocalAxisInDirection
getPlaneNormalForObjects = rigUtils.getPlaneNormalForObjects

#try to load the zooMirror.py plugin
try:
	loadPlugin( 'zooMirror.py', quiet=True )
except:
	import zooToolbox
	zooToolbox.loadZooPlugin( 'zooMirror.py' )


def getScaleFromMeshes():
	'''
	determines a scale based on the visible meshes in the scene.  If no visible
	meshes are found, the TYPICAL_HEIGHT value is returend
	'''
	def isVisible( node ):
		if not getAttr( '%s.v' % node ):
			return False

		for p in iterParents( node ):
			if not getAttr( '%s.v' % p ): return False

		return True

	visibleMeshes = [ m for m in (ls( type='mesh' ) or []) if isVisible( m ) ]
	if not visibleMeshes:
		return TYPICAL_HEIGHT

	return rigUtils.getObjsScale( visibleMeshes )


def getScaleFromSkeleton():

	#lets see if there is a Root part already
	scale = 0
	for root in Root.IterAllParts():
		t = Vector( getAttr( '%s.t' % root[0] )[0] )
		scale = t.y

	scale *= 1.75  #the root is roughly 4 head heights from the ground and the whole body is about 7 head heights - hence 1.75 (7/4)

	#lets see if there is a spine part - between the root and the spine, we can get a
	#pretty good idea of the scale for most anatomy types
	scaleFromSpine = 0
	spineCls = SkeletonPart.GetNamedSubclass( 'Spine' )
	if spineCls is not None:
		numSpines = 0
		for spine in spineCls.IterAllParts():
			items = spine.items
			items.append( spine.getParent() )
			mnx, mny, mnz, mxx, mxy, mxz = rigUtils.getTranslationExtents( items )
			XYZ = mxx-mnx, mxy-mny, mxz-mnz
			maxLen = max( XYZ ) * 1.5
			scaleFromSpine += maxLen
			numSpines += 1

		#if there were spine parts found, average their scales, add them to the root scale and average them again
		if numSpines:
			scaleFromSpine /= float( numSpines )
			scaleFromSpine *= 2.3  #ths spine is roughly 3 head heights, while the whole body is roughly 7 head heights - hence 2.3 (7/3)
			scale += scaleFromSpine
			scale /= 2.0

	if not scale:
		return getScaleFromMeshes()

	return scale


def getItemScale( item ):
	'''
	returns the non-skinned "scale" of a joint (or skeleton part "item")
	This scale uses a few metrics to determine the scale - first, the
	bounds of any children are calculated and the max side of the bounding
	box is found, and if non-zero returned.  If the item has no children
	then the radius of the joint is used (if it exists) otherwise the
	magnitude of the joint translation is used.

	If all the above tests fail, 1 is returned.
	'''
	scale = 0

	children = listRelatives( item, type='transform' )
	if children:
		scales = []
		bb = rigUtils.getTranslationExtents( children )
		XYZ = bb[3]-bb[0], bb[4]-bb[1], bb[5]-bb[2]
		scale = max( XYZ )

	if not scale:
		if objExists( '%s.radius' % item ):
			scale = getAttr( '%s.radius' % item )

	if not scale:
		pos = Vector( getAttr( '%s.t' % item )[0] )
		scale = pos.get_magnitude()

	return scale or 1


def getNodeParent( obj ):
	parent = listRelatives( obj, p=True, pa=True )
	if parent is None:
		return None

	return parent[ 0 ]


def iterParents( obj, until=None ):
	parent = getNodeParent( obj )
	while parent is not None:
		yield parent
		if until is not None:
			if parent == until:
				return

		parent = getNodeParent( parent )


def sortByHierarchy( objs ):
	sortedObjs = []
	for o in objs:
		pCount = len( list( iterParents( o ) ) )
		sortedObjs.append( (pCount, o) )

	sortedObjs.sort()

	return [ o[ 1 ] for o in sortedObjs ]


def getAlignSkipState( item ):
	attrPath = '%s._skeletonPartSkipAlign' % item
	if not objExists( attrPath ):
		return False

	return getAttr( attrPath )


def setAlignSkipState( item, state ):
	'''
	will flag a joint as user aligned - which means it will get skipped
	by the alignment functions
	'''
	attrPath = '%s._skeletonPartSkipAlign' % item
	if state:
		if not objExists( attrPath ):
			addAttr( item, ln='_skeletonPartSkipAlign', at='bool' )

		setAttr( attrPath, True )
	else:
		deleteAttr( attrPath )


def d_restoreLocksAndNames(f):
	'''
	this decorator is for the alignment functions - it basically takes care of ensuring the children
	are unparented before alignment happens, re-parented after the fact, channel unlocking and re-locking,
	freezing transforms etc...

	NOTE: this function gets called a lot.  basically this decorator wraps all alignment functions, and
	generally each joint in the skeleton has at least one alignment function run on it.  Beware!
	'''
	def newF( item, *args, **kwargs ):
		if getAlignSkipState( item ):
			return

		attrs = 't', 'r', 'ra'

		#unparent and children in place, and store the original name, and lock
		#states of attributes - we need to unlock attributes as this item will
		#most likely change its orientation
		children = castToMObjects( listRelatives( item, typ='transform', pa=True ) or [] )  #cast to mobjects as re-parenting can change and thus invalidate node name strings...
		childrenPreStates = {}
		for child in [ item ] + children:
			lockStates = []
			for a in attrs:
				for c in CHANNELS:
					attrPath = '%s.%s%s' % (child, a, c)

					lockStates.append( (attrPath, getAttr( attrPath, lock=True )) )
					try:
						setAttr( attrPath, lock=False )
					except: pass

			originalChildName = str( child )
			if not cmpNodes( child, item ):
				child = cmd.parent( child, world=True )[0]

			childrenPreStates[ child ] = originalChildName, lockStates

		#make sure the rotation axis attribute is zeroed out - NOTE: we need to do this after children have been un-parented otherwise it could affect their positions
		for c in CHANNELS:
			setAttr( '%s.ra%s' % (item, c), 0 )

		f( item, children=children, *args, **kwargs )
		makeIdentity( item, a=True, r=True )

		#now re-parent children
		for child, (originalName, lockStates) in childrenPreStates.iteritems():
			if child != item:
				child = cmd.parent( child, item )[0]
				child = rename( child, originalName.split( '|' )[-1] )

			for attrPath, lockState in lockStates:
				try:
					setAttr( attrPath, lock=lockState )
				except: pass

	newF.__name__ = f.__name__
	newF.__doc__ = f.__doc__

	return newF


@d_restoreLocksAndNames
def autoAlignItem( item, invertAimAndUp=False, upVector=BONE_ROTATE_VECTOR, worldUpVector=MAYA_SIDE, worldUpObject='', upType='vector', children=None, debug=False ):
	'''
	for cases where there is no strong preference about how the item is aligned, this function will determine the best course of action
	'''

	numChildren = len( children )

	#if there is more than one child, see if there is only one JOINT child...
	childJoints = ls( children, type='joint' )
	if len( childJoints ) == 1:
		children = childJoints

	#if there is only one child, aim the x-axis at said child, and aim the z-axis toward scene-up
	### WARNING :: STILL NEED TO DEAL WITH CASE WHERE JOINT IS CLOSE TO AIMING AT SCENE UP
	invertMult = -1 if invertAimAndUp else 1
	if len( children ) == 1:
		kw = { 'aimVector': BONE_AIM_VECTOR * invertMult,
		       'upVector': upVector * invertMult,
		       'worldUpVector': worldUpVector,
		       'worldUpType': upType }

		if worldUpObject:
			kw[ 'worldUpObject' ] = worldUpObject

		c = aimConstraint( children[ 0 ], item, **kw )
		if not debug: delete( c )
	else:
		for a in [ 'jo', 'r' ]:
			for c in CHANNELS:
				attrPath = '%s.%s%s' % (item, a, c)
				if not getAttr( attrPath, settable=True ):
					continue

				setAttr( attrPath, 0 )


@d_restoreLocksAndNames
def alignAimAtItem( item, aimAtItem, invertAimAndUp=False, upVector=BONE_ROTATE_VECTOR, worldUpVector=MAYA_SIDE, worldUpObject='', upType='vector', children=None, debug=False ):
	'''
	aims the item at a specific transform in the scene.  the aim axis is always BONE_AIM_VECTOR, but the up axis can be set to whatever is required
	'''
	invertMult = -1 if invertAimAndUp else 1
	kw = { 'aimVector': BONE_AIM_VECTOR * invertMult,
           'upVector': upVector * invertMult,
           'worldUpVector': worldUpVector,
           'worldUpType': upType }

	if worldUpObject:
		kw[ 'worldUpObject' ] = worldUpObject

	c = aimConstraint( aimAtItem, item, **kw )
	if debug: raise Exception
	if not debug: delete( c )


@d_restoreLocksAndNames
def alignItemToWorld( item, children=None, skipX=False, skipY=False, skipZ=False ):
	'''
	aligns the item to world space axes, optionally skipping individual axes
	'''
	rotate( -90, -90, 0, item, a=True, ws=True )

	if skipX: rotate( 0, 0, 0, item, a=True, os=True, rotateX=True )
	if skipY: rotate( 0, 0, 0, item, a=True, os=True, rotateY=True )
	if skipZ: rotate( 0, 0, 0, item, a=True, os=True, rotateZ=True )


@d_restoreLocksAndNames
def alignItemToLocal( item, children=None, skipX=False, skipY=False, skipZ=False ):
	'''
	aligns the item to local space axes, optionally skipping individual axes
	'''
	for skip, axis in zip( (skipX, skipY, skipZ), CHANNELS ):
		if skipX:
			setAttr( '%s.r%s' % (item, axis), 0 )
			setAttr( '%s.jo%s' % (item, axis), 0 )


@d_restoreLocksAndNames
def alignPreserve( item, children=None ):
	pass


def getCharacterMeshes():
	'''
	returns all "character meshes" found in the scene.  These are basically defined as meshes that aren't
	parented to a joint - where joints are
	'''
	meshes = ls( type='mesh', r=True )
	meshes = set( listRelatives( meshes, p=True, pa=True ) )  #removes duplicates...

	characterMeshes = set()
	for mesh in meshes:
		isUnderJoint = False
		for parent in iterParents( mesh ):
			if nodeType( parent ) == 'joint':
				isUnderJoint = True
				break

		if not isUnderJoint:
			characterMeshes.add( mesh )

	return list( characterMeshes )


class SkeletonError(Exception): pass
class NotFinalizedError(SkeletonError): pass
class SceneNotSavedError(SkeletonError): pass


def getSkeletonSet():
	'''
	returns the "master" set used for storing skeleton parts in the scene - this isn't actually used for
	anything but organizational purposes - ie the skeleton part sets are members of _this_ set, but at
	no point does the existence or non-existence of this make any functional difference
	'''
	existing = [ node for node in ls( type='objectSet', r=True ) or [] if sets( node, q=True, text=True ) == TOOL_NAME ]

	if existing:
		return existing[ 0 ]
	else:
		skeletonParts = createNode( 'objectSet', n='skeletonParts' )
		sets( skeletonParts, e=True, text=TOOL_NAME )

		return skeletonParts


def createSkeletonPartContainer( name ):
	'''
	'''
	theSet = sets( em=True, n=name, text='skeletonPrimitive' )
	sets( theSet, e=True, add=getSkeletonSet() )

	return theSet


def isSkeletonPartContainer( node ):
	'''
	tests whether the given node is a skeleton part container or not
	'''
	if objectType( node, isType='objectSet' ):
		return sets( node, q=True, text=True ) == 'skeletonPrimitive'

	return False


def getSkeletonPartContainers():
	'''
	returns a list of all skeleton part containers in the scene
	'''
	return [ node for node in ls( type='objectSet', r=True ) or [] if sets( node, q=True, text=True ) == 'skeletonPrimitive' ]


def buildSkeletonPartContainer( typeClass, kwDict, items ):
	'''
	builds a container for the given skeleton part items, and tags it with the various attributes needed
	to track the state for a skeleton part.
	'''

	#if typeClass is an instance, then set its container attribute, otherwise instantiate an instance and return it
	if isinstance( typeClass, SkeletonPart ):
		theInstance = typeClass
		typeClass = type( typeClass )

	#build the container, and add the special attribute to it to
	if 'idx' in kwDict:
		idx = kwDict[ 'idx' ]
	else:
		kwDict[ 'idx' ] = idx = typeClass.GetUniqueIdx()

	theContainer = createSkeletonPartContainer( 'a%sPart_%s' % (typeClass.__name__, idx) )

	addAttr( theContainer, ln='_skeletonPrimitive', attributeType='compound', numberOfChildren=7 )
	addAttr( theContainer, ln='typeName', dt='string', parent='_skeletonPrimitive' )
	addAttr( theContainer, ln='version', at='long', parent='_skeletonPrimitive' )
	addAttr( theContainer, ln='script', dt='string', parent='_skeletonPrimitive' )
	addAttr( theContainer, ln='buildKwargs', dt='string', parent='_skeletonPrimitive' )  #stores the kwarg dict used to build this part
	addAttr( theContainer, ln='rigKwargs', dt='string', parent='_skeletonPrimitive' )  #stores the kwarg dict to pass to the rig method
	addAttr( theContainer, ln='items',
	         multi=True,
	         indexMatters=False,
	         attributeType='message',
	         parent='_skeletonPrimitive' )
	addAttr( theContainer, ln='placers',
	         multi=True,
	         indexMatters=False,
	         attributeType='message',
	         parent='_skeletonPrimitive' )


	#now set the attribute values...
	setAttr( '%s._skeletonPrimitive.typeName' % theContainer, typeClass.__name__, type='string' )
	setAttr( '%s._skeletonPrimitive.version' % theContainer, typeClass.__version__ )
	setAttr( '%s._skeletonPrimitive.script' % theContainer, inspect.getfile( typeClass ), type='string' )
	setAttr( '%s._skeletonPrimitive.buildKwargs' % theContainer, str( kwDict ), type='string' )


	#now add all the items
	items = map( str, items )
	for item in set( items ):

		if nodeType( item ) == 'joint':
			sets( item, e=True, add=theContainer )

		#if the node is a rig part container add it to this container otherwise skip it
		elif objectType( item, isAType='objectSet' ):
			if isSkeletonPartContainer( item ):
				sets( item, e=True, add=theContainer )


	#and now hook up all the controls
	for idx, item in enumerate( items ):
		if item is None:
			continue

		connectAttr( '%s.message' % item, '%s._skeletonPrimitive.items[%d]' % (theContainer, idx), f=True )


	return theContainer


def d_disconnectJointsFromSkinning( f ):
	'''
	Will unhook all skinning before performing the decorated method - and re-hooks it up after the
	fact.  Basically decorating anything with this function will allow you do perform operations
	that would otherwise cause maya to complain about skin clusters being attached
	'''
	def new( *a, **kw ):
		#for all skin clusters iterate through all their joints and detach them
		#so we can freeze transforms - make sure to store initial state so we can
		#restore connections afterward
		skinClustersConnections = []
		skinClusters = ls( typ='skinCluster' ) or []
		for c in skinClusters:
			cons = listConnections( c, destination=False, plugs=True, connections=True )
			if cons is None:
				print 'WARNING - no connections found on the skinCluster %s' % c
				continue

			conIter = iter( cons )
			for tgtConnection in conIter:
				srcConnection = conIter.next()  #cons is a list of what should be tuples, but maya just returns a flat list - basically every first item is the destination plug, and every second is the source plug

				#if the connection is originating from a joint delete the connection - otherwise leave it alone - we only want to disconnect joints from the skin cluster
				node = srcConnection.split( '.' )[0]
				if nodeType( node ) == 'joint':
					disconnectAttr( srcConnection, tgtConnection )
					skinClustersConnections.append( (srcConnection, tgtConnection) )

		try:
			f( *a, **kw )

		#ALWAYS restore connections...
		finally:

			#re-connect all joints to skinClusters, and reset them
			for srcConnection, tgtConnection in skinClustersConnections:
				connectAttr( srcConnection, tgtConnection, f=True )

			if skinClustersConnections:
				for skinCluster in skinClusters:
					resetSkinCluster( skinCluster )

	new.__name__ = f.__name__
	new.__doc__ = f.__doc__

	return new


def d_disableDrivingRelationships( f ):
	'''
	tries to unhook all driver/driven relationships first, and re-hook them up afterwards

	NOTE: needs to wrap a SkeletonPart method
	'''
	def new( self, *a, **kw ):

		#store any driving or driven part, so when we're done we can restore the relationships
		driver = self.getDriver()
		drivenParts = self.getDriven()

		#break driving relationships
		self.breakDriver()
		for part in drivenParts:
			part.breakDriver()

		try:
			f( self, *a, **kw )

		#restore driver/driven relationships...
		finally:

			#restore any up/downstream relationships if any...
			if driver:
				driver.driveOtherPart( self )

			for part in drivenParts:
				try:
					self.driveOtherPart( part )
				except AssertionError: continue  #the parts may have changed size since the initial connection, so if they differ in size just ignore the assertion...

	new.__name__ = f.__name__
	new.__doc__ = f.__doc__

	return new


def d_performInSkeletonPartScene( f ):
	def new( self, *a, **kw ):
		assert isinstance( self, SkeletonPart )

		#if the part isn't referenced - nothing to do!  execute the function as usual
		if not self.isReferenced():
			return f( self, *a, **kw )

		partContainerFilepath = Path( referenceQuery( self.getContainer(), filename=True ) )
		curScene = Path( file( q=True, sn=True ) )
		if not curScene.exists():
			raise TypeError( "This scene isn't saved!  Please save this scene somewhere before executing the decorated method!" )

		initialContainer = ReferencedNode( self.getContainer() )
		self.setContainer( initialContainer.getUnreferencedNode() )
		if not curScene.getWritable():
			curScene.edit()

		file( save=True, f=True )
		file( partContainerFilepath, open=True, f=True )

		try:
			return f( self, *a, **kw )
		finally:
			self.setContainer( initialContainer.getNode() )
			if not partContainerFilepath.getWritable():
				partContainerFilepath.edit()

			file( save=True, f=True )
			file( curScene, open=True, f=True )

	new.__name__ = f.__name__
	new.__doc__ = f.__doc__

	return new


class SkeletonPart(typeFactories.trackableClassFactory()):
	__version__ = 0

	#parity is "sided-ness" of the part.  Ie if the part can exist on the left OR right side of the skeleton, the part has parity.  the spine
	#is an example of a part that has no parity, as is the head
	HAS_PARITY = True

	PART_SCALE = TYPICAL_HEIGHT

	AUTO_NAME = True
	AVAILABLE_IN_UI = True  #determines whether this part should appear in the UI or not...

	#some variables generally used by the auto volume creation methods
	AUTO_VOLUME_SIDES = 8  #number of cylinder sides

	#this list should be overridden for sub classes require named end placers such as feet
	PLACER_NAMES = []

	RigTypes = ()

	def __new__( cls, partContainer ):
		if cls is SkeletonPart:
			clsName = getAttr( '%s._skeletonPrimitive.typeName' % partContainer )
			cls = cls.GetNamedSubclass( clsName )
			if cls is None:
				raise TypeError( "Cannot determine the part class for the given part container!" )

		return object.__new__( cls, partContainer )
	def __init__( self, partContainer ):
		if partContainer is not None:
			assert isSkeletonPartContainer( partContainer ), "Must pass a valid skeleton part container! (received %s - a %s)" % (partContainer, nodeType( partContainer ))

		self._container = partContainer
		self._items = None
	def __unicode__( self ):
		return u"%s( %r )" % (self.__class__.__name__, self._container)
	__str__ = __unicode__
	def __repr__( self ):
		return repr( unicode( self ) )
	def __hash__( self ):
		return hash( self._container )
	def __eq__( self, other ):
		return self._container == other.getContainer()
	def __neq__( self, other ):
		return not self == other
	def __getitem__( self, idx ):
		return self.getItems().__getitem__( idx )
	def __getattr__( self, attr ):
		if attr in self.__dict__:
			return self.__dict__[ attr ]

		if attr not in self.PLACER_NAMES:
			raise AttributeError( "No such attribute %s" % attr )

		idx = list( self.PLACER_NAMES ).index( attr )
		cons = listConnections( '%s._skeletonPrimitive.placers[%d]' % (self.base, n), d=False )
		if cons:
			return cons[ 0 ]

		return None
	def __len__( self ):
		return len( self.getItems() )
	def __iter__( self ):
		return iter( self.getItems() )
	def getContainer( self ):
		return self._container
	def setContainer( self, container ):
		self._container = container
		self._items = None
	def getItems( self ):
		if self._items is not None:
			return self._items[:]

		self._items = items = []
		idxs = getAttr( '%s._skeletonPrimitive.items' % self._container, multiIndices=True ) or []
		for idx in idxs:
			cons = listConnections( '%s._skeletonPrimitive.items[%d]' % (self._container, idx), d=False )
			if cons:
				assert len( cons ) == 1, "More than one joint was found!!!"
				items.append( cons[ 0 ] )

		#items = castToMObjects( items )

		return items[:]  #return a copy...
	items = property( getItems )
	@property
	def version( self ):
		try:
			return getAttr( '%s._skeletonPrimitive.version' % self._container )
		except: return None
	def isDisabled( self ):
		'''
		returns whether the part has been disabled for rigging or not
		'''
		rigKwargs = self.getRigKwargs()

		return 'disable' in rigKwargs
	def getPlacers( self ):
		placerAttrpath = '%s._skeletonPrimitive.placers' % self._container
		if not objExists( placerAttrpath ):
			return []

		placers = []
		placerIdxs = getAttr( placerAttrpath, multiIndices=True )
		if placerIdxs:
			for idx in placerIdxs:
				cons = listConnections( '%s[%d]' % (placerAttrpath, idx), d=False )
				if cons:
					placers.append( cons[ 0 ] )

		return placers
	def verifyPart( self ):
		'''
		this is merely a "hook" that can be used to fix anything up should the way
		skeleton parts are defined change
		'''

		#make sure all items have the appropriate attributes on them
		baseItem = self[ 0 ]
		for n, item in enumerate( self ):
			delete( '%s.inverseScale' % item, icn=True )  #remove the inverse scale relationship...

			setAttr( '%s.segmentScaleCompensate' % item, False )
			if not objExists( '%s._skeletonPartName' % item ):
				addAttr( item, ln='_skeletonPartName', dt='string' )

			if not objExists( '%s._skeletonPartArgs' % item ):
				addAttr( item, ln='_skeletonPartArgs', dt='string' )

			if n:
				if not isConnected( '%s._skeletonPartName' % baseItem, '%s._skeletonPartName' % item ):
					connectAttr( '%s._skeletonPartName' % baseItem, '%s._skeletonPartName' % item, f=True )

				if not isConnected( '%s._skeletonPartArgs' % baseItem, '%s._skeletonPartArgs' % item ):
					connectAttr( '%s._skeletonPartArgs' % baseItem, '%s._skeletonPartArgs' % item, f=True )
	def convert( self, buildKwargs ):
		'''
		called when joints built outside of skeleton builder are converted to a skeleton builder part
		'''

		if not buildKwargs:
			for argName, value in self.GetDefaultBuildKwargList():
				buildKwargs[ argName ] = value

		if 'idx' not in buildKwargs:
			idx = self.GetUniqueIdx()
			buildKwargs[ 'idx' ] = idx

		if 'parent' in buildKwargs:
			buildKwargs.pop( 'parent' )

		self.setBuildKwargs( buildKwargs )

		#lock scale
		attrState( self.items, ['s'], lock=True, keyable=False, show=True )

		#lock rotate axis
		attrState( self.items, ['rotateAxis'], lock=True, keyable=False, show=False )

		#build placers...
		self.buildPlacers()
	def hasParity( self ):
		return self.HAS_PARITY
	def isReferenced( self ):
		return referenceQuery( self._container, inr=True )
	@classmethod
	def ParityMultiplier( cls, idx ):
		return Parity( idx ).asMultiplier()
	@classmethod
	def GetPartName( cls ):
		'''
		can be used to get a "nice" name for the part class
		'''
		return camelCaseToNice( cls.__name__ )
	def getIdx( self ):
		'''
		returns the index of the part - all parts have a unique index associated
		with them
		'''
		return self.getBuildKwargs()[ 'idx' ]
	def getBuildScale( self ):
		return self.getBuildKwargs().get( 'partScale', self.PART_SCALE )
	def getParity( self ):
		return Parity( self.getIdx() )
	def getParityColour( self ):
		parity = self.getParity()
		if parity == Parity.LEFT:
			return Colour( 'green' )

		if parity == Parity.RIGHT:
			return Colour( 'red' )

		if parity == Parity.NONE:
			return Colour( 'darkblue' )

		return Colour( 'black' )
	getParityColor = getParityColour
	def getParityMultiplier( self ):
		return self.getParity().asMultiplier()
	def getOppositePart( self ):
		'''
		Finds the opposite part - if any - in the scene to this part. If no opposite part is found None is returned.

		The opposite part is defined as the part that has opposite parity - the part with the closest index is
		returned if there are multiple parts with opposite parity in the scene.

		If this part has no parity None is returned.
		'''

		#is this a parity part?  if not then there is no such thing as an opposite part...
		if not self.hasParity():
			return None

		#get some data about this part
		thisIdx = self.getIdx()
		thisParity = self.getParity()

		#is this a left or right parity part?
		isLeft = thisIdx == Parity.LEFT

		possibleMatches = []
		for part in self.IterAllParts( True ):
			parity = part.getParity()
			if parity.isOpposite( thisParity ):
				idx = part.getIdx()

				#if "self" is a left part then its exact opposite will be self.getIdx() + 1, otherwise if "self" is a right
				#sided part then its exact opposite will be self.getIdx() - 1.  So figure out the "index delta" and use it
				#as a sort metric to find the most appropriate match for the cases where there are multiple, non-ideal matches
				idxDelta = 0
				if isLeft:
					idxDelta = idx - thisIdx
				else:
					idxDelta = thisIdx - idx

				if idxDelta == 1:
					return part

				possibleMatches.append( (idxDelta, part) )

		possibleMatches.sort()
		if possibleMatches:
			return possibleMatches[0][1]

		return None
	@property
	def base( self ):
		return self[ 0 ]
	@property
	def bases( self ):
		'''
		returns all the bases for this part - bases are joints with parents who don't belong to this part
		'''
		allItems = set( self )

		bases = []
		for item in self:
			itemParent = getNodeParent( item )
			if itemParent not in allItems:
				bases.append( item )

		return bases
	@property
	def end( self ):
		return self[ -1 ]
	@property
	def ends( self ):
		'''
		returns all the ends for the part - ends are joints that either have no children, or have children
		that don't belong to this part
		'''
		allItems = set( self )
		ends = []
		for item in self:
			itemChildren = listRelatives( item, pa=True )

			#so if the item has children, see if any of them are in allItems - if not, its an end
			if itemChildren:
				childrenInAllItems = allItems.intersection( set( itemChildren ) )
				if not childrenInAllItems:
					ends.append( item )

			#if it has no children, its an end
			else:
				ends.append( item )

		return ends
	@property
	def chains( self ):
		'''
		returns a list of hierarchy "chains" in the current part - parts that have
		more than one base are comprised of "chains": ie hierarchies that don't have
		a parent as a member of this part

		For a hand part for example, this method will return a list of finger
		hierarchies

		NOTE: the chains are ordered hierarchically
		'''
		bases = set( self.bases )

		chains = []
		for end in self.ends:
			currentChain = [ end ]
			p = getNodeParent( end )
			while p:
				currentChain.append( p )
				if p in bases:
					break

				p = getNodeParent( p )

			currentChain.reverse()
			chains.append( currentChain )

		return chains
	@property
	def endPlacer( self ):
		try:
			return self.getPlacers()[ 0 ]
		except IndexError:
			return None
	@classmethod
	def GetIdxStr( cls, idx ):
		'''
		returns an "index string".  For parts with parity this index string increments
		with pairs (ie a left and a right) while non-parity parts always increment
		'''
		#/2 because parts are created in pairs so arm 2 and 3 are prefixed with "Arm1", and the first arm is simply "Arm"
		if cls.HAS_PARITY:
			return str( idx / 2 ) if idx > 1 else ''

		return str( idx ) if idx else ''
	def getBuildKwargs( self ):
		'''
		returns the kwarg dict that was used to create this particular part
		'''

		buildFunc = self.GetBuildFunction()

		#get the default build kwargs for the part
		argNames, vArgs, vKwargs, defaults = inspect.getargspec( buildFunc )
		if defaults is None:
			defaults = []

		argNames = argNames[ 1: ]  #strip the first arg - which is the class arg (usually cls)

		kw = {}
		for argName, default in zip( argNames, defaults ):
			kw[ argName ] = default

		#now update the default kwargs with the actual kwargs
		argStr = getAttr( '%s._skeletonPrimitive.buildKwargs' % self._container )
		kw.update( eval( argStr ) )

		return kw
	def setBuildKwargs( self, kwargs ):
		'''
		returns the kwarg dict that was used to create this particular part
		'''
		setAttr( '%s._skeletonPrimitive.buildKwargs' % self._container, str( kwargs ), type='string' )
	def getRigKwargs( self ):
		'''
		returns the kwarg dict that should be used to create the rig for this part
		'''
		try:
			argStr = getAttr( '%s._skeletonPrimitive.rigKwargs' % self._container )
		except:
			return {}

		if argStr is None:
			return {}

		kw = eval( argStr )

		return kw
	def setRigKwargs( self, kwargs ):
		setAttr( '%s._skeletonPrimitive.rigKwargs' % self._container, str( kwargs ), type='string' )
	def updateRigKwargs( self, **kw ):
		currentKwargs = self.getRigKwargs()
		currentKwargs.update( kw )
		self.setRigKwargs( currentKwargs )
	def getPartName( self ):
		idx = self.getIdx()
		if self.hasParity():
			parityStr = 'Left ' if self.getParity() == Parity.LEFT else 'Right '
			idxStr = '' if idx < 2 else ' %d' % idx
		else:
			parityStr = ''
			idxStr = ' %d' % idx if idx else ''

		name = camelCaseToNice( self.getBuildKwargs().get( 'partName', '' ) )
		clsName = camelCaseToNice( type( self ).__name__ )

		return '%s%s %s%s' % (parityStr, name, clsName, idxStr)
	def getActualScale( self ):
		return rigUtils.getObjsScale( self )
	def getParent( self ):
		'''
		returns the parent of the part - the actual node name.  use getParentPart
		to query the part this part is parented to (if any)
		'''
		return getNodeParent( self.base )
	def setParent( self, parent ):
		'''
		parents the part to a new object in the scene - if parent is None, the
		part is parented to the world
		'''
		if parent is None:
			cmd.parent( self.base, w=True )
		else:
			cmd.parent( self.base, parent )
	def getParentPart( self ):
		'''
		returns the part this part is parented to - if any.  if this part isn't
		parented to a part, None is returned.

		NOTE: this part may be parented to something that isn't a member of a
		part, so a result of None from this query doesn't mean the part has no
		parent, just that its parent isn't a member of a part
		'''
		parent = self.getParent()
		if parent is None:
			return None

		return self.InitFromItem( parent )
	@classmethod
	def GetBuildFunction( cls ):
		'''
		returns the build function for the part
		'''
		buildFunc = getattr( cls, '_build', None )
		if buildFunc is None:
			raise SkeletonError( 'no such part type' )

		return buildFunc
	@classmethod
	def GetDefaultBuildKwargList( cls ):
		'''
		returns a list of 2 tuples: argName, defaultValue
		'''
		buildFunc = cls.GetBuildFunction()
		spec = inspect.getargspec( buildFunc )

		argNames = spec[ 0 ][ 1: ]  #strip the first item because the _build method is a bound method - so the first item is always the class arg (usually called cls)
		defaults = spec[ 3 ]

		if defaults is None:
			defaults = []

		assert len( argNames ) == len( defaults ), "%s has no default value set for one of its args - this is not allowed" % cls

		kwargList = []
		for argName, default in zip( argNames, defaults ):
			kwargList.append( (argName, default) )

		return kwargList
	@classmethod
	def InitFromItem( cls, item ):
		'''
		will instantiate a SkeletonPart from an item of a previously built part.
		if an item is given that isn't involved in a part None is returned
		'''

		if isSkeletonPartContainer( item ):
			typeClassStr = getAttr( '%s._skeletonPrimitive.typeName' % item )
			typeClass = SkeletonPart.GetNamedSubclass( typeClassStr )

			return typeClass( item )

		cons = listConnections( '%s.message' % item, s=False, type='objectSet' )
		if not cons:
			raise SkeletonError( "Cannot find a skeleton part container for %s" % item )

		for con in cons:
			if isSkeletonPartContainer( con ):
				typeClassStr = getAttr( '%s._skeletonPrimitive.typeName' % con )
				typeClass = SkeletonPart.GetNamedSubclass( typeClassStr )

				return typeClass( con )

		raise SkeletonError( "Cannot find a skeleton container for %s" % item )

	### CREATION ###
	def buildPlacers( self ):
		'''
		Don't override this method - instead override the _buildPlacers method.  This method handles
		connecting the placers to the part appropriately
		'''
		try:
			buildPlacers = self._buildPlacers
		except AttributeError: return []

		placers = buildPlacers()
		if not placers:
			return

		container = self._container

		idx = self.getIdx()
		idxStr = self.GetIdxStr( idx )
		parityStr = Parity( idx % 2 ).asName() if self.hasParity() else ''
		for n, placer in enumerate( placers ):
			connectAttr( '%s.message' % placer, '%s._skeletonPrimitive.placers[%d]' % (container, n), f=True )

			#name the placer appropriately
			try:
				placerName = self.PLACER_NAMES[ n ]
			except IndexError:
				proposedName = '%s%s_plc%d%s' % (type( self ).__name__, idxStr, idx, parityStr)
			else:
				proposedName = '%s%s_plc%d%s' % (placerName, idxStr, idx, parityStr)

			if objExists( proposedName ):
				proposedName = proposedName +'#'

			placer = rename( placer, proposedName )

		return placers
	def _buildPlacers( self ):
		'''
		the default placer building method just creates a placer at teh end of every
		joint chain in the part
		'''
		placers = []
		for end in self.ends:
			placer = buildEndPlacer()
			setAttr( '%s.t' % placer, *getAttr( '%s.t' % end )[0] )
			placer = parent( placer, end, r=True )[ 0 ]
			placers.append( placer )

		return placers
	#NOTE!!!  this method gets decorated below !!!
	def Create( cls, *a, **kw ):
		'''
		this is the primary way to create a skeleton part.  build functions are
		defined outside the class and looked up by name.  this method ensures
		that all build methods (a build method is only required to return the
		list of nodes that define it) register nodes properly, and encode data
		about how the part was built into the part so that the part can be
		re-instantiated at a later date
		'''

		partScale = kw.setdefault( 'partScale', cls.PART_SCALE )


		#grab any kwargs out of the dict that shouldn't be there
		visualize = kw.pop( 'visualize', True )
		autoMirror = kw.pop( 'autoMirror', True )


		#now turn the args passed in are a single kwargs dict
		buildFunc = cls.GetBuildFunction()
		argNames, vArgs, vKwargs, defaults = inspect.getargspec( buildFunc )
		if defaults is None:
			defaults = []

		argNames = argNames[ 1: ]  #strip the first arg - which is the class arg (usually cls)
		if vArgs is not None:
			raise SkeletonError( 'cannot have *a in skeleton build functions' )

		for argName, value in zip( argNames, a ):
			kw[ argName ] = value

		#now explicitly add the defaults
		for argName, default in zip( argNames, defaults ):
			kw.setdefault( argName, default )


		#generate an index for the part - each part must have a unique index
		idx = cls.GetUniqueIdx()
		kw[ 'idx' ] = idx


		#run the build function and remove the parent from the kw dict - we don't need to serialize this...
		items = buildFunc( **kw )
		kw.pop( 'parent', None )
		partContainer = buildSkeletonPartContainer( cls, kw, items )


		#now rename all the joints appropriately if we're supposed to...
		if cls.AUTO_NAME:
			partName = kw.get( 'partName', cls.__name__ )
			if not partName:
				partName = cls.__name__

			partName = partName[0].upper() + partName[ 1: ]  #capitalize the first letter always...
			kw[ 'partName' ] = partName

			renamedItems = []

			idxStr = cls.GetIdxStr( idx )
			parityStr = Parity( idx % 2 ).asName() if cls.HAS_PARITY else ''
			for n, item in enumerate( items ):
				renamedItems.append( rename( item, '%s%s_%s%s' % (partName, idxStr, n, parityStr) ) )

			items = renamedItems


		#instantiate the part and align
		newPart = cls( partContainer )
		newPart.convert( kw )
		newPart._align( _initialAlign=True )


		#are we doing visualizations?
		if visualize:
			newPart.visualize()

		return newPart
	#in 2009 wrapping the Create with d_unifyUndo will crash maya...  :(
	if mayaVar >= 2011:
		Create = classmethod( d_unifyUndo( Create ) )
	else:
		Create = classmethod( d_unifyUndo( Create ) )
	def rebuild( self, **newBuildKwargs ):
		'''
		rebuilds the part by storing all the positions of the existing members,
		re-creating the part with optionally changed build args, positioning
		re-created joints as best as possible, and re-parenting child parts
		'''

		#grab the build kwargs used to create this part, and update it with the new kwargs passed in
		buildKwargs = self.getBuildKwargs()
		buildKwargs.update( newBuildKwargs )
		buildKwargs[ 'parent' ] = getNodeParent( self )

		self.unvisualize()

		posRots = []
		attrs = 't', 'r'
		for item in self:
			pos = xform( item, q=True, ws=True, rp=True )
			rot = xform( item, q=True, ws=True, ro=True )
			posRots.append( (item, pos, rot) )

		childParts = self.getChildParts()
		childParents = []
		childPartDrivers = []
		for part in childParts:
			childParents.append( part.getParent() )
			childPartDrivers.append( part.getDriver() )
			part.breakDriver()
			part.setParent( None )

		orphans = self.getOrphanJoints()
		orphanParents = []
		for orphan in orphans:
			orphanParents.append( getNodeParent( orphan ) )
			cmd.parent( orphan, w=True )

		delete( self.items )
		newPart = self.Create( **buildKwargs )

		oldToNewNameMapping = {}
		for (oldItemName, pos, rot), item in zip( posRots, newPart.items ):
			move( pos[ 0 ], pos[ 1 ], pos[ 2 ], item, ws=True, a=True, rpr=True )
			rotate( rot[ 0 ], rot[ 1 ], rot[ 2 ], item, ws=True, a=True )
			oldToNewNameMapping[ oldItemName ] = item

		#reparent child parts
		for childPart, childParent in zip( childParts, childParents ):
			childParent = oldToNewNameMapping.get( childParent, childParent )
			childPart.setParent( childParent )

		#re-setup driver/driven relationships (should be done after re-parenting is done)
		for childPart, childDriver in zip( childParts, childPartDrivers ):
			if childDriver is not None:
				childDriver.driveOtherPart( childPart )

		#reparent orphans
		for orphan, orphanParent in zip( orphans, orphanParents ):
			orphanParent = oldToNewNameMapping.get( orphanParent, orphanParent )
			cmd.parent( orphan, orphanParent )

		newPart.visualize()

		return newPart

	### REDISCOVERY ###
	@classmethod
	def IterAllParts( cls, exactType=False ):
		'''
		iterates over all SkeletonParts in the current scene
		'''
		for partContainer in getSkeletonPartContainers():
			thisPartCls = SkeletonPart.GetNamedSubclass( getAttr( '%s._skeletonPrimitive.typeName' % partContainer ) )

			#if the user only wants the exact type then compare the classes - if they're not the same keep loopin
			if exactType:
				if cls is not thisPartCls:
					continue

			#otherwise test to see if this part's class is a subclass of
			else:
				if not issubclass( thisPartCls, cls ):
					continue

			yield thisPartCls( partContainer )
	@classmethod
	def IterAllPartsInOrder( cls ):
		allParts = [ part for part in cls.IterAllParts() ]
		allParts = sortPartsByHierarchy( allParts )

		return iter( allParts )
	@classmethod
	def FindParts( cls, partClass, withKwargs=None ):
		'''
		given a part name and a kwargs dict (may be a partial dict) this method
		will return all matching parts in the current scene.  so if you wanted to
		get a list of all the finger parts with 3 joints you would do:

		SkeletonPart.FindParts( finger, { 'fingerJointCount': 3 } )
		'''
		withKwargs = withKwargs or {}

		matches = []
		for part in cls.IterAllParts( partClass ):
			partKwargs = part.getBuildKwargs()
			match = True
			for argName, argValue in withKwargs.iteritems():
				try:
					if partKwargs[ argName ] != argValue:
						match = False
						break
				except KeyError: continue

			if match: matches.append( part )

		return matches
	@classmethod
	def GetUniqueIdx( cls ):
		'''
		returns a unique index (unique against the universe of existing indices
		in the scene) for the current part class
		'''
		allPartContainers = getSkeletonPartContainers()

		thisTypeName = cls.__name__

		existingIdxs = set()
		for container in allPartContainers:
			typeStr = getAttr( '%s._skeletonPrimitive.typeName' % container )
			typeCls = SkeletonPart.GetNamedSubclass( typeStr )

			if typeCls is cls:
				attrPath = '%s._skeletonPrimitive.buildKwargs' % container
				attrStr = getAttr( attrPath )
				if attrStr:
					buildArgs = eval( getAttr( attrPath ) )
					existingIdxs.add( buildArgs[ 'idx' ] )

		existingIdxs = list( sorted( existingIdxs ) )

		#return the first, lowest, available index
		for orderedIdx, existingIdx in enumerate( existingIdxs ):
			if existingIdx != orderedIdx:
				return orderedIdx

		if existingIdxs:
			return existingIdxs[ -1 ] + 1

		return 0
	@classmethod
	def GetRigMethod( cls, methodName ):
		for method in cls.RigTypes:
			if method.__name__ == methodName:
				return method

		return None
	def getChildParts( self ):
		'''
		returns a list of all the parts parented directly to a member of this part
		'''

		#first get a list of all the joints directly parented to a memeber of this part
		selfItems = self.getItems() + self.getPlacers()
		allChildren = listRelatives( selfItems, typ='transform', pa=True )
		if not allChildren:
			return

		#subtract all the items of this part from the children - to give us all the children of this part that don't belong to this part
		allChildren = set( allChildren ).difference( set( selfItems ) )

		return getPartsFromObjects( allChildren )
	def getOrphanJoints( self ):
		'''
		orphan joints are joints parented to a member of this part, but don't
		belong to a part.  orphan joints get aligned using the same alignment
		method used by their parent part
		'''

		#first get a list of all the joints directly parented to a memeber of this part
		allChildren = listRelatives( self, typ='joint', pa=True )
		if not allChildren:
			return []

		childPartItems = []
		for part in self.getChildParts():
			childPartItems += list( part )

		jointsInSomePart = set( childPartItems + self.items )
		orphanChildren = set( allChildren ).difference( jointsInSomePart )
		orphanChildren = list( orphanChildren )

		childrenOfChildren = []
		for i in orphanChildren:
			iChildren = listRelatives( i, typ='joint', pa=True )
			if not iChildren: continue
			for c in iChildren:
				if objExists( '%s._skeletonPartName' % c ): continue
				childrenOfChildren.append( c )

		return orphanChildren + childrenOfChildren
	def selfAndOrphans( self ):
		return list( self ) + self.getOrphanJoints()
	@d_unifyUndo
	def delete( self ):
		if self.isRigged():
			self.deleteRig()

		for node in self.items:
			rigUtils.cleanDelete( node )

		if objExists( self._container ):
			delete( self._container )

	### ALIGNMENT ###
	@d_unifyUndo
	@d_disableDrivingRelationships
	@d_disconnectJointsFromSkinning
	def align( self, _initialAlign=False ):
		self._align( _initialAlign )
	def _align( self, _initialAlign=False ):
		for item in self.selfAndOrphans():
			autoAlignItem( item )
	@d_unifyUndo
	@d_disableDrivingRelationships
	@d_disconnectJointsFromSkinning
	def freeze( self ):
		'''
		freezes the transforms for all joints in this part
		'''
		makeIdentity( self.items, a=True, t=True, r=True )

	### VISUALIZATION ###
	@d_unifyUndo
	def visualize( self ):
		'''
		can be used to create visualization for item orientation or whatever else.

		NOTE: visualizations should never add joints, but can use any other node
		machinery available.
		'''
		pass
	@d_unifyUndo
	def unvisualize( self ):
		'''
		removes any visualization on the part
		'''
		for i in self.selfAndOrphans():
			children = listRelatives( i, shapes=True, pa=True ) or []
			for c in children:
				try:
					if nodeType( c ) == 'joint': continue
					delete( c )
				#this can happen if the deletion of a previous child causes some other child to also be deleted - its a fringe case but possible (i think)
				except TypeError: continue

	### SYMMETRICAL SKELETON BUILDING ###
	def driveOtherPart( self, otherPart ):
		'''
		drives the specified part with this part - meaning that all translations
		and rotations of items in this part will drive the corresponding items in
		the other part.  attributes are hooked up for the most part using direct
		connections, but some attributes are driven via an expression
		'''
		assert isinstance( otherPart, SkeletonPart )  #this is just for WING...

		if type( self ) is not type( otherPart ):
			raise SkeletonError( "Sorry, you cannot connect different types together" )

		if len( self ) != len( otherPart ):
			raise SkeletonError( "Sorry, seems the two parts are different sizes (%d, %d) - not sure what to do" % (len( self ), len( otherPart )) )

		attrs = 't', 'r'

		#first unlock trans and rot channels
		attrState( otherPart.items, attrs, False )

		#if the parts have parity AND differing parities, we may have to deal with mirroring differently
		if self.hasParity() and self.getParity() != otherPart.getParity():
			selfItems = self.items + self.getPlacers()
			otherItems = otherPart.items + otherPart.getPlacers()

			for thisItem, otherItem in zip( selfItems, otherItems ):
				rotNode = cmd.rotationMirror( thisItem, otherItem, ax=BONE_AIM_AXIS.asName() )  #access via cmd namespace as the plugin may or may not have been loaded when all was imported from maya.cmds

				#if the joints have the same parent, reverse position
				if getNodeParent( thisItem ) == getNodeParent( otherItem ):
					setAttr( '%s.mirrorTranslation' % rotNode, 2 )
				else:
					setAttr( '%s.mirrorTranslation' % rotNode, 1 )

		#otherwise setting up the driven relationship is straight up attribute connections...
		else:
			for thisItem, otherItem in zip( self.items, otherPart.items ):
				for attr in attrs:
					for c in CHANNELS:
						connectAttr( '%s.%s%s' % (thisItem, attr, c), '%s.%s%s' % (otherItem, attr, c), f=True )
	def breakDriver( self ):
		attrs = 't', 'r'

		for item in (self.items + self.getPlacers()):
			for a in attrs:
				attrPaths = [ a ] + [ '%s%s' % (a, c) for c in CHANNELS ]

				for attrPath in attrPaths:
					attrPath = '%s.%s' % (item, attrPath)
					isLocked = getAttr( attrPath, lock=True )
					if isLocked:
						setAttr( attrPath, lock=False )  #need to make sure attributes are unlocked before trying to break a connection - regardless of whether the attribute is the source or destination...  8-o

					delete( attrPath, inputConnectionsAndNodes=True )
					if isLocked:
						setAttr( attrPath, lock=True )
	def getDriver( self ):
		'''
		returns the part driving this part if any, otherwise None is returned
		'''
		attrs = 't', 'r'

		for item in self:
			for attr in attrs:
				for c in CHANNELS:
					cons = listConnections( '%s.%s%s' % (item, attr, c), destination=False, skipConversionNodes=True, t='joint' )
					if cons:
						for c in cons:
							part = SkeletonPart.InitFromItem( c )
							if part: return part
	def getDriven( self ):
		'''
		returns a list of driven parts if any, otherwise an empty list is returned
		'''
		attrs = 't', 'r'

		allOutConnections = []
		for item in self:
			for attr in attrs:
				for c in CHANNELS:
					allOutConnections += listConnections( '%s.%s%s' % (item, attr, c), source=False, skipConversionNodes=True, t='joint' ) or []

		if allOutConnections:
			allOutConnections = removeDupes( allOutConnections )
			return getPartsFromObjects( allOutConnections )

		return []

	### FINALIZATION ###
	def generateItemHash( self, item ):
		'''
		creates a hash for the position and orientation of the joint so we can ensure
		the state is still the same at a later date
		'''
		tHashAccum = 0
		joHashAccum = 0
		tChanValues = []
		joChanValues = []
		for c in CHANNELS:
			#we hash the rounded string of the float to eliminate floating point error
			t = getAttr( '%s.t%s' % (item, c) )
			jo = getAttr( '%s.jo%s' % (item, c) )
			val = '%0.4f %0.4f' % (t, jo)

			tHashAccum += hash( val )

			tChanValues.append( t )
			joChanValues.append( jo )

		iParent = getNodeParent( item )

		return iParent, tHashAccum, tChanValues, joChanValues
	@d_performInSkeletonPartScene
	def finalize( self ):
		'''
		performs some finalization on the skeleton - ensures everything is aligned,
		and then stores a has of the orientations into the skeleton so that we can
		later compare the skeleton orientation with the stored state
		'''

		#early out if finalization is valid
		if self.compareAgainstHash():
			return

		#make sure any driver relationship is broken
		self.breakDriver()

		#make sure the part has been aligned
		self.align()

		#remove any visualizations
		self.unvisualize()

		#unlock all channels and make keyable - we cannot change lock/keyability
		#state once the skeleton is referenced into the rig, and we need them to
		#be in such a state to build the rig
		attrState( self.selfAndOrphans(), ('t', 'r'), False, True, True )
		attrState( self.selfAndOrphans(), ('s', 'v'), False, False, True )

		#create a hash for the position and orientation of the joint so we can ensure the state is still the same at a later date
		for i in self.selfAndOrphans():
			if not objExists( '%s._skeletonFinalizeHash' % i ):
				addAttr( i, ln='_skeletonFinalizeHash', dt='string' )

			setAttr( '%s._skeletonFinalizeHash' % i, str( self.generateItemHash( i ) ), type='string' )
	def compareAgainstHash( self ):
		'''
		compares the current orientation of the partto the stored state hash when
		the part was last finalized.  if the part has differing

		a bool indicating whether the current state matches the stored finalization
		state is returned
		'''

		#if the part is rigged, then return True - if its been rigged then it should have been properly finalized so we should be good
		if self.isRigged():
			return True

		#create a hash for the position and orientation of the joint so we can ensure the state is still the same at a later date
		for i in self.selfAndOrphans():

			#if the joint is marked with the align skip state, skip the finalization check
			if getAlignSkipState( i ):
				continue

			#if it doesn't have the finalization hash attribute it can't possibly be finalized
			if not objExists( '%s._skeletonFinalizeHash' % i ):
				return False

			#figure out what the hash should be and compare it to the one that is stored
			iParent, xformHash, xxa, yya = self.generateItemHash( i )
			try: storedParent, stored_xHash, xxb, yyb = eval( getAttr( '%s._skeletonFinalizeHash' % i ) )
			except:
				print 'stored hash differs from the current hashing routine - please re-finalize'
				return False

			#if the stored parent is different from the current parent, there may only be a namespace conflict - so strip namespace prefixes and redo the comparison
			if iParent != storedParent:
				if Name( iParent ).strip() != Name( storedParent ).strip():
					print 'parenting mismatch on %s since finalization (%s vs %s)' % (i, iParent, storedParent)
					return False

			TOLERANCE = 1e-6  #tolerance used to compare floats
			def doubleCheckValues( valuesA, valuesB ):
				for va, vb in zip( valuesA, valuesB ):
					va, vb = float( va ), float( vb )
					if va - vb > TOLERANCE:
						return False

				return True

			if xformHash != stored_xHash:
				#so did we really fail?  sometimes 0 gets stored as -0 or whatever, so make sure the values are actually different
				if not doubleCheckValues( xxa, xxb ):
					print 'the translation on %s changed since finalization (%s vs %s)' % (i, xxa, xxb)
					return False

				if not doubleCheckValues( yya, yyb ):
					print 'joint orienatation on %s changed since finalization (%s vs %s)' % (i, yya, yyb)
					return False

		return True

	### RIGGING ###
	@d_unifyUndo
	def rig( self, **kw ):
		'''
		constructs the rig for this part
		'''

		#check the skeleton part to see if it already has a rig
		rigContainerAttrname = 'rigContainer'
		rigContainerAttrpath = '%s.%s' % (self._container, rigContainerAttrname)
		if not objExists( rigContainerAttrpath ):
			addAttr( self._container, ln=rigContainerAttrname, at='message' )

		#check to see if there is already a rig built
		if listConnections( rigContainerAttrpath, d=False ):
			print 'Rig already built for %s - skipping' % self
			return

		#update the kw dict for the part
		rigKw = self.getBuildKwargs()
		rigKw.update( self.getRigKwargs() )
		rigKw.update( kw )
		kw = rigKw

		if kw.get( 'disable', False ):
			print 'Rigging disabled for %s - skipping' % self
			return

		#pop the rig method name out of the kwarg dict, and look it up
		try: rigMethodName = kw.pop( 'rigMethodName', self.RigTypes[ 0 ].__name__ )
		except IndexError:
			print "No rig method defined for %s" % self
			return

		#make sure to break drivers before we rig
		self.breakDriver()

		#discover the rigging method
		rigType = self.GetRigMethod( rigMethodName )
		if rigType is None:
			print 'ERROR :: there is no such rig method with the name %s' % rigMethodName
			return

		#bulid the rig and connect it to the part
		theRig = rigType.Create( self, **kw )
		if theRig is None:
			printErrorStr( "Failed to create the rig for part %s" % self )
			return

		connectAttr( '%s.message' % theRig.getContainer(), '%s.rigContainer' % self._container, f=True )
	def isRigged( self ):
		'''
		returns whether this skeleton part is rigged or not
		'''
		return self.getRigContainer() is not None

	### VOLUME CREATION ###
	def buildVolumes( self ):
		'''
		attempts to create volumes for the skeleton that reasonably tightly fits the character mesh.  these
		volumes can then be modified quickly using standard modelling tools, and can be then used to generate
		a fairly good skinning solution for the character mesh
		'''

		#remove any visualization - this can confuse the volume removal code as it can't tell what is a volume mesh and what is a visualization mesh
		self.unvisualize()

		#remove any existing volumes
		self.removeVolumes()

		#get the list of character meshes
		characterMeshes = getCharacterMeshes()

		for item in self:
			size, centre = rigUtils.getJointSizeAndCentre( item, ignoreSkinning=True )

			#we just want to move the joint to the centre of the primary bone axis - not all axes...
			otherAxes = BONE_AIM_AXIS.otherAxes()
			centre[ otherAxes[0] ] = 0
			centre[ otherAxes[1] ] = 0

			volumes = self.buildItemVolume( item, size, centre )
			for v in volumes:
				v = rename( v, '%s__sbVolume#' % item )
				makeIdentity( v, a=True, t=True, r=True, s=True )
				shrinkWrap( v, characterMeshes )
	def iterItemVolumes( self ):
		'''
		generator to yield a 2-tuple of each part item, and the list of volumes associated with it
		'''
		for item in self:
			children = listRelatives( item, pa=True )
			if children:
				childMeshes = listRelatives( children, pa=True, type='mesh' )

				if childMeshes:
					meshParents = [ m for m in listRelatives( childMeshes, p=True, pa=True ) if nodeType( m ) != 'joint' ]  #make sure not to remove joints...
					yield item, meshParents
	def removeVolumes( self ):
		'''
		handles removing any existing volumes on the skeleton
		'''
		for item, volumes in self.iterItemVolumes():
			if volumes:
				delete( volumes )
	def buildItemVolume( self, item, size, centre ):
		'''
		handles creation of the actual volume - generally if you want control over volume creation for a part
		you'll just need to override this method.  It gets given the joint's "size" and its "centre" and you're
		then free to build geometry accordingly
		'''
		sides = self.AUTO_VOLUME_SIDES

		height = float( size[ BONE_AIM_AXIS ] )

		geo = polyCylinder( h=height * 0.95, r=0.01, ax=BONE_AIM_VECTOR, sx=sides, sy=round( height/2.0 ), ch=False )[0]
		parent( geo, item, r=True )

		setAttr( '%s.t' % geo, *centre )

		#finally remove the top and bottom cylinder caps - they're always the last 2 faces
		numFaces = meshUtils.numFaces( geo )
		delete( '%s.f[ %d:%d ]' % (geo, numFaces-2, numFaces-1) )

		return [geo]


def createRotationCurves( theJoint ):
	"""
	create the UI widget for each rotGUI
	"""

	rotGuiOverRideColor = [ 13 , 14 , 6 ]
	rotGuiCurves = []

	c = curve( d=1, p=((0.000000, -0.000000, -1.000000),
	                   (-0.000000, 0.500000, -0.866025),
	                   (-0.000000, 0.866025, -0.500000),
	                   (-0.000000, 1.000000, -0.000000),
	                   (-0.000000, 0.350000, 0.000000),
	                   (-0.116667, 0.116667, -0.116667),
	                   (-0.000000, 0.000000, -0.350000),
	                   (0.000000, -0.436239, -0.464331),
	                   (0.000000, -0.866025, -0.350000),
	                   (0.000000, -1.000000, 0.000000),
	                   (0.000000, -0.866025, -0.500000),
	                   (0.000000, -0.500000, -0.866025),
	                   (0.000000, -0.000000, -1.000000)) )

	rotGuiCurves.append( c )
	c = curve( d=1, p=((0.000000, 0.000000, -1.000000),
	                   (-0.500000, 0.000000, -0.866025),
	                   (-0.866025, 0.000000, -0.500000),
	                   (-1.000000, 0.000000, -0.000000),
	                   (-0.350000, -0.000000, -0.000000),
	                   (-0.116667, 0.116666, -0.116667),
	                   (-0.000000, -0.000000, -0.350000),
	                   (0.436239, -0.000000, -0.464331),
	                   (0.866025, -0.000000, -0.350000),
	                   (1.000000, -0.000000, 0.000000),
	                   (0.866025, 0.000000, -0.500000),
	                   (0.500000, 0.000000, -0.866025),
	                   (0.000000, 0.000000, -1.000000)) )

	rotGuiCurves.append( c )
	c = curve( d=1, p=((0.000000, 1.000000, -0.000000),
	                   (-0.500000, 0.866025, -0.000000),
	                   (-0.866025, 0.500000, -0.000000),
	                   (-1.000000, 0.000000, -0.000000),
	                   (-0.350000, -0.000000, -0.000000),
	                   (-0.116667, 0.116667, -0.116666),
	                   (-0.000000, 0.350000, 0.000000),
	                   (0.436239, 0.464331, -0.000000),
	                   (0.866025, 0.350000, -0.000000),
	                   (1.000000, -0.000000, 0.000000),
	                   (0.866025, 0.500000, -0.000000),
	                   (0.500000, 0.866025, -0.000000),
	                   (0.000000, 1.000000, -0.000000)) )

	rotGuiCurves.append( c )
	for i, theCurve in enumerate( rotGuiCurves ):
		theScale = 3
		setAttr( '%s.sx' % theCurve, theScale )
		setAttr( '%s.sy' % theCurve, theScale )
		setAttr( '%s.sz' % theCurve, theScale )

		makeIdentity( theCurve, a=True, s=True )
		theCurveShape = listRelatives( theCurve, s=True, pa=True )[ 0 ]

		setAttr( '%s.overrideEnabled' % theCurveShape, 1 )
		setAttr( '%s.overrideDisplayType' % theCurveShape, 0 )
		setAttr( '%s.overrideColor' % theCurveShape, rotGuiOverRideColor[i] )

		parent( theCurveShape, theJoint, add=True, shape=True )
		delete( theCurve )


def kwargsToOptionStr( kwargDict ):
	toks = []
	for k, v in kwargDict.iteritems():
		if isinstance( v, (list, tuple) ):
			v = ' '.join( v )
		elif isinstance( v, bool ):
			v = int( v )

		toks.append( '-%s %s' % (k, v) )

	return ' '.join( toks )


def createJoint( name=None ):
	'''
	simple wrapper to deal with joint creation - mainly provides a hook to control joint creation should that be needed
	'''
	if name:
		if objExists( name ):
			name = name +'#'

		return createNode( 'joint', n=name )

	return createNode( 'joint' )


def buildEndPlacer():
	'''
	builds a placer for the end of a chain.  This is generally useful for aligning the last joint in a chain
	but can also be useful for marking up interesting pivots on parts such as feet with foot edges etc...
	'''
	transform = createNode( 'transform' )
	setAttr( '%s.displayHandle' % transform, True )

	return transform


def jointSize( jointName, size ):
	'''
	convenience function to set the size of a joint
	'''
	setAttr( '%s.radius' % jointName, size )


def getRoot():
	joints = ls( typ='joint' )
	for j in joints:
		if objExists( '%s.%s' % (j, TOOL_NAME) ):
			return j

	return None


class Root(SkeletonPart):
	HAS_PARITY = False

	@classmethod
	def _build( cls, **kw ):
		idx = kw[ 'idx' ]
		partScale = kw[ 'partScale' ]

		root = createJoint()
		root = rename( root, 'root' )
		move( 0, partScale / 1.75, 0, root, ws=True )
		jointSize( root, 3 )

		#tag the root joint with the tool name only if its the first root created - having multiple roots in a scene/skeleton is entirely valid
		if idx == 0:
			cmd.addAttr( ln=TOOL_NAME, at='message' )

		#the root can only have a parent if its not the first root created
		if idx:
			move( 0, 0, -partScale / 2, root, r=True )

		return [ root ]
	def _buildPlacers( self ):
		return []
	def _align( self, _initialAlign=False ):
		for i in self.selfAndOrphans():
			alignItemToWorld( self[ 0 ] )
	def finalize( self ):
		#make sure the scale is unlocked on the base joint of the root part...
		attrState( self.base, 's', False, False, True )
		super( self.__class__, Root ).finalize( self )
	def buildItemVolume( self, item, size, centre ):
		height = size[2] / 3
		width = max( size[0], size[1] ) / 3

		geo = polyCube( w=width, h=height, d=width, sx=3, sy=3, sz=2, ax=(0, 0, 1), ch=True )[0]
		parent( geo, item, r=True )
		setAttr( '%s.t' % geo, *centre )

		return [geo]


def getParent( parent=None ):
	if parent is None:

		#grab the selection and walk up till we find a joint
		sel = ls( sl=True, type='transform' )
		if sel:
			obj = sel[0]
			while nodeType( obj ) != 'joint':
				obj = getNodeParent( obj )
				if obj is None:
					break

			return obj

		existingRoot = getRoot()

		return existingRoot or Root.Create().base

	if isinstance( parent, SkeletonPart ):
		return parent.end

	if objExists( parent ):
		return parent

	return getRoot() or Root.Create().base


def sortPartsByHierarchy( parts ):
	'''
	returns a list of the given parts in a list sorted by hierarchy
	'''
	sortedParts = sortByHierarchy( [ p.base for p in parts ] )
	return [ SkeletonPart.InitFromItem( p ) for p in sortedParts ]


def getPartsFromObjects( objs ):
	'''
	returns a list of parts that have at least one of their items selected
	'''
	parts = []
	for o in objs:
		try:
			parts.append( SkeletonPart.InitFromItem( o ) )
		except SkeletonError: continue

	selectedParts = removeDupes( parts )

	return selectedParts


@d_unifyUndo
@d_maintainSceneSelection
def realignSelectedParts():
	'''
	re-aligns all selected parts
	'''
	sel = ls( sl=True )
	selectedParts = sortPartsByHierarchy( getPartsFromObjects( sel ) )

	for part in selectedParts:
		part.align()


@d_unifyUndo
@d_maintainSceneSelection
def realignAllParts():
	'''
	re-aligns all parts in the current scene
	'''

	for part in SkeletonPart.IterAllPartsInOrder():
		try:
			part.align()
		except:
			print 'ERROR: %s failed to align properly' % part
			continue


@d_unifyUndo
@d_maintainSceneSelection
def finalizeAllParts():

	#do a pre-pass on the skin clusters to remove un-used influences - this can speed up the speed of the alignment code
	#is directly impacted by the number of joints involved in the skin cluster
	skinClusters = ls( typ='skinCluster' )
	for s in skinClusters:
		skinCluster( s, e=True, removeUnusedInfluence=True )

	failedParts = []
	for part in sortPartsByHierarchy( part for part in SkeletonPart.IterAllParts() ):
		part.breakDriver()
		if not part.compareAgainstHash():
			try:
				part.finalize()
			except:
				failedParts.append( part )
				print 'ERROR: %s failed to finalize properly!' % part
				continue

	return failedParts


@d_unifyUndo
def freezeAllParts():
	for part in SkeletonPart.IterAllParts():
		part.freeze()


@d_unifyUndo
def setupAutoMirror():
	partsInMirrorRelationship = set()
	for part in SkeletonPart.IterAllParts():
		if part in partsInMirrorRelationship:
			continue

		if part.hasParity():
			idx = part.getIdx()
			parity = part.getParity()

			#if we have a left, look for a right
			if parity == Parity.LEFT:
				partToDrive = None

				#try to find a matching part with the next index
				for partOfType in part.IterAllParts():
					if partOfType.getIdx() == idx + 1:
						partToDrive = partOfType
						break

				#if we can't find a part with an incremented index, look for a part with the opposing parity
				if not partToDrive:
					for partOfType in part.IterAllParts():
						if partOfType.getParity() == Parity.RIGHT:
							partToDrive = partOfType
							break

				#if an appropriate part was found, setup the driven relationship
				if partToDrive:
					try:
						part.driveOtherPart( partToDrive )

					#if a skeleton error is thrown, ignore it (it means the parts are incompatible) but add the part to the partsInMirrorRelationship set
					except SkeletonError: pass

					partsInMirrorRelationship.add( part )
					partsInMirrorRelationship.add( partToDrive )


def getNamespaceFromReferencing( node ):
	'''
	returns the namespace contribution from referencing.  this is potentially
	different from just querying the namespace directly from the node because the
	node in question may have had a namespace before it was referenced
	'''
	if referenceQuery( node, isNodeReferenced=True ):
		refNode = referenceQuery( node, referenceNode=True )
		namespace = cmd.file( cmd.referenceQuery( refNode, filename=True ), q=True, namespace=True )

		return '%s:' % namespace

	return ''


@d_unifyUndo
@d_showWaitCursor
@d_maintainSceneSelection
def buildAllVolumes():

	#align all parts first
	for part in SkeletonPart.IterAllParts():
		if not part.compareAgainstHash():
			part.align()

	for part in SkeletonPart.IterAllParts():
		part.buildVolumes()


@d_unifyUndo
def removeAllVolumes():
	for part in SkeletonPart.IterAllParts():
		part.removeVolumes()


def shrinkWrap( obj, shrinkTo=None, performReverse=False ):
	if shrinkTo is None:
		shrinkTo = getCharacterMeshes()

	if not isinstance( shrinkTo, (list, tuple) ):
		shrinkTo = [ shrinkTo ]

	from maya.OpenMaya import MFnMesh, MFloatPointArray, MFloatArray, MPoint, MFloatPoint, MVector, MFloatVector, MItMeshVertex, MDagPath, MSpace
	kWorld = MSpace.kWorld
	kTransform = MSpace.kTransform

	obj = asMObject( obj )
	shrinkTo = map( asMObject, shrinkTo )

	#get the shape nodes...
	dagObj = MDagPath.getAPathTo( obj )
	dagObj.extendToShape()

	#NOTE: we use the exclusive matrix because we want the object's parent - which is assumed to be the joint
	dagWorldMatrix = dagObj.exclusiveMatrix()
	dagWorldMatrixInv = dagObj.exclusiveMatrixInverse()

	dagShinkTo = map( MDagPath.getAPathTo, shrinkTo )
	for dag in dagShinkTo:
		dag.extendToShape()

	fnObj = MFnMesh( dagObj )
	fnShrinkTo = map( MFnMesh, dagShinkTo )

	aimIdx = BONE_AIM_AXIS
	otherIdxs = idxA, idxB = BONE_AIM_AXIS.otherAxes()

	#construct the MMeshIntersector instances
	accellerators = []
	for fnShrink in fnShrinkTo:
		a = MFnMesh.autoUniformGridParams()
		accellerators.append( a )

	#now iterate over the verts in the obj, shoot rays outward in the direction of the normal and try to fit as best as
	#possible to the given shrink meshes
	itObjVerts = MItMeshVertex( dagObj )
	vertPositions = []
	while not itObjVerts.isDone():
		intersects = []

		pos = itObjVerts.position( kWorld )
		actualPos = Vector( (pos.x, pos.y, pos.z) )

		normal = MVector()
		itObjVerts.getNormal( normal, kWorld )

		#holy BAWLS maya is shite...  MVector and MFloatVector are COMPLETELY different classes, and you can't construct one from the other?!  What kind of retard wrote this API
		pos = MFloatPoint( pos.x, pos.y, pos.z )
		normal = MFloatVector( normal.x, normal.y, normal.z )
		normal.normalize()

		#now get ray intersections with the shrinkTo meshes
		for fnShrinkMesh, accel in zip( fnShrinkTo, accellerators ):
			hitPoints = MFloatPointArray()

			def go( rev=False ):
				fnShrinkMesh.allIntersections( pos, normal,						#raySource, rayDirection
					                           None, None, False,				#faceIds, triIds, idsSorted

					                           kWorld, 1000, rev,				#space, maxParam, testBothDirs
					                           accel, True,						#accelParams, sortHits

					                           hitPoints, #this is all we really care about...
					                           None, None, None, None, None )

			go()
			if performReverse and not hitPoints.length():
				go( performReverse )

			for n in range( hitPoints.length() ):
				p = hitPoints[ n ]
				intersects.append( Vector( (p.x, p.y, p.z) ) )  #deal with native vectors for now...

		#if there is just one intersection, easy peasy
		if len( intersects ) == 1:
			newPosition = intersects[0]

		#otherwise we need to figure out which one is the best match...
		elif intersects:
			#first sort them by their distance to the vert - I think they should be sorted already, but...
			sortByDist = [ ((p-actualPos).get_magnitude(), p) for p in intersects ]
			sortByDist.sort()

			#not sure how much guesswork to do here - so just use the closest...
			newPosition = sortByDist[0][1]

		#if there are no matches just use the actual vert position so we don't have to handle this case below...
		else:
			newPosition = actualPos

		vertPositions.append( (actualPos, newPosition) )

		vert = itObjVerts.next()

	#now we have a list of vertex positions, figure out the average delta and clamp deltas that are too far away from this average
	deltaSum = 0
	numZeroDeltas = 0
	for pos, newPos in vertPositions:
		delta = (pos - newPos).get_magnitude()
		if not delta:
			numZeroDeltas += 1

		deltaSum += delta

	#if all deltas are zero, there is nothing to do... bail!
	if len( vertPositions ) == numZeroDeltas:
		return

	deltaAverage = float( deltaSum ) / (len( vertPositions ) - numZeroDeltas)  #don't count deltas that are zero...
	clampedVertPositions = []

	MAX_DIVERGENCE = 1.1  #the maximum allowable variance from the average delta

	acceptableDelta = deltaAverage * MAX_DIVERGENCE
	for pos, newPos in vertPositions:
		if newPos is None:
			clampedVertPositions.append( None )
			continue

		delta = (pos - newPos).get_magnitude()

		#if the magnitude of the delta is too far from the average, scale down the magnitude
		if delta > acceptableDelta:
			deltaVector = newPos - pos
			deltaVector = deltaVector * (acceptableDelta / delta)
			clampedVertPositions.append( pos + deltaVector )
		else:
			clampedVertPositions.append( newPos )

	#now set the vert positions
	n = 0
	itObjVerts.reset()
	while not itObjVerts.isDone():
		newPos = clampedVertPositions[ n ]

		position = MPoint( *newPos )
		itObjVerts.setPosition( position, kWorld )

		n += 1
		vert = itObjVerts.next()


def shrinkWrapSelection( shrinkTo=None ):
	for obj in ls( sl=True, type=('mesh', 'transform') ):
		makeIdentity( obj, a=True, t=True, r=True, s=True )
		shrinkWrap( obj, shrinkTo )


def volumesToSkinning():
	#first grab all the volumes and combine them into a single mesh, then generate weights from the original volumes (this should
	#result in the duplicates being rigidly skinned to the skeleton) then transfer the weights from the combined mesh to the
	#character meshes
	allVolumes = []
	for part in SkeletonPart.IterAllParts():
		for item, volumes in part.iterItemVolumes():
			allVolumes += volumes

	#get the character meshes before we build the temp transfer surface
	charMeshes = getCharacterMeshes()

	import skinWeights

	#combine them all
	duplicateVolumes = duplicate( allVolumes, renameChildren=True )
	makeIdentity( duplicateVolumes, a=True, t=True, r=True, s=True )
	combinedVolumes = polyUnite( duplicateVolumes, ch=False )[0]

	#generate weights
	skinWeights.saveWeights( allVolumes )
	skinWeights.loadWeights( [combinedVolumes], tolerance=2 )

	#now transfer weights to the character meshes
	for charMesh in charMeshes:
		targetSkinCluster = skinWeights.transferSkinning( combinedVolumes, charMesh )

		#now lets do a little smoothing
		#skinCluster( targetSkinCluster, e=True, smoothWeights=0.65 )

	"""
	#JESUS!!!  for some weird as piss reason maya doesn't like this python command: skinCluster( targetSkinCluster, q=True, smoothWeights=0.75 )
	#nor this mel command: skinCluster -q -smoothWeights 0.75 targetSkinCluster
	#you NEED to run this mel command: skinCluster -smoothWeights 0.75 -q targetSkinCluster
	#which makes no goddamn sense - fuuuuuuuuuuuuuu alias!
	#not to mention that the stupid as piss command returns vert indices, not components...  what a bullshit api.
	vertIdxs = mel.eval( "skinCluster -smoothWeights 0.5 -q %s" % targetSkinCluster )

	baseStr = targetMesh +'.vtx[%d]'
	select( [ baseStr % idx for idx in vertIdxs ] )
	polySelectConstraint( pp=1, t=0x0001 )  #expand the selection

	skinCluster( targetSkinCluster, e=True, smoothWeights=0.7, smoothWeightsMaxIterations=1 )
	"""

	#delete the combined meshes - we're done with them
	delete( combinedVolumes )


def getSkeletonBuilderJointCount():
	'''
	returns a 2-tuple containing the total skeleton builder joint count, and the total number of
	joints that are involved in a skin cluster
	'''

	#get the root joint and get a list of all joints under it
	skeletonBuilderJoints = []
	for rootPart in Root.IterAllParts():
		skeletonBuilderJoints += rootPart.items
		skeletonBuilderJoints += listRelatives( rootPart.items, ad=True, type='joint' ) or []

	#generate a list of joints involved in skinning
	skinnedJoints = []
	for mesh in ls( type='mesh' ):
		skinCluster = mel.findRelatedSkinCluster( mesh )
		if skinCluster:
			skinnedJoints += mel.eval( 'skinPercent -ib 0.001 -q -t %s "%s.vtx[*]"' % (skinCluster, mesh) )

	#now get the intersection of the two lists - these are the joints on the character that are skinned
	skinnedSkeletonBuilderJoints = set( skeletonBuilderJoints ).intersection( set( skinnedJoints ) )

	return len( skeletonBuilderJoints ), len( skinnedSkeletonBuilderJoints )


def displaySkeletonBuilderJointCount():
	totalJoints, skinnedJoints = getSkeletonBuilderJointCount()
	return '%d skinned / %d total' % (skinnedJoints, totalJoints)


def setupSkeletonBuilderJointCountHUD():
	if headsUpDisplay( HUD_NAME, ex=True ):
		headsUpDisplay( HUD_NAME, rem=True )

	else:
		jointbb = headsUpDisplay( nfb=0 )
		headsUpDisplay( HUD_NAME, section=0, block=jointbb, blockSize="small", label="Joint Count:", labelFontSize="small", command=displaySkeletonBuilderJointCount, event="SelectionChanged" )  #, nodeChanges="attributeChange"


#end
