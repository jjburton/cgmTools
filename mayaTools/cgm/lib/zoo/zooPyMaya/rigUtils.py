'''
this module is simply a miscellaneous module for rigging support code - most of it is maya specific convenience code
for determining things like aimAxes, aimVectors, rotational offsets for controls etc...
'''

import random

import maya.cmds as cmd
from maya.cmds import *
from maya import OpenMaya

from zooPy.vectors import *
from zooPy import vectors

from melUtils import mel

import apiExtensions
import meshUtils

SPACES = SPACE_WORLD, SPACE_LOCAL, SPACE_OBJECT = range(3)

ENGINE_FWD   = MAYA_SIDE  = MAYA_X = Vector((1, 0, 0))
ENGINE_UP    = MAYA_FWD   = MAYA_Z = Vector((0, 0, 1))
ENGINE_SIDE  = MAYA_UP    = MAYA_Y = Vector((0, 1, 0))

#pull in some globals...
MPoint = OpenMaya.MPoint
MVector = OpenMaya.MVector
MMatrix = OpenMaya.MMatrix
MTransformationMatrix = OpenMaya.MTransformationMatrix
MBoundingBox = OpenMaya.MBoundingBox

MSpace = OpenMaya.MSpace
kWorld = MSpace.kWorld
kTransform = MSpace.kTransform
kObject = MSpace.kObject

Axis = vectors.Axis
AXES = Axis.BASE_AXES

#these are the enum values for the rotation orders for transform nodes in maya
MAYA_ROTATION_ORDERS = ROO_XYZ, ROO_YZX, ROO_ZXY, ROO_XZY, ROO_YXZ, ROO_ZYX = range( 6 )
MATRIX_ROTATION_ORDER_CONVERSIONS_FROM = Matrix.FromEulerXYZ, Matrix.FromEulerYZX, Matrix.FromEulerZXY, Matrix.FromEulerXZY, Matrix.FromEulerYXZ, Matrix.FromEulerZYX
MATRIX_ROTATION_ORDER_CONVERSIONS_TO = Matrix.ToEulerXYZ, Matrix.ToEulerYZX, Matrix.ToEulerZXY, Matrix.ToEulerXZY, Matrix.ToEulerYXZ, Matrix.ToEulerZYX

ROT_ORDER_STRS = 'xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx'


def alignFast( objToAlign, dest ):
	if getAttr( '%s.t' % objToAlign, se=True ):
		pos = xform( dest, q=True, ws=True, rp=True )
		move( pos[0], pos[1], pos[2], objToAlign, a=True, ws=True, rpr=True )

	if getAttr( '%s.r' % objToAlign, se=True ):

		#rotation is a bit special because when querying the rotation we get back xyz world rotations - so we need to change the rotation order to xyz, set the global rotation then modify the rotation order while preserving orientation
		initialRo = getAttr( '%s.ro' % objToAlign )
		setAttr( '%s.ro' % objToAlign, 0 )

		rot = xform( dest, q=True, ws=True, ro=True )
		rotate( rot[0], rot[1], rot[2], objToAlign, a=True, ws=True )

		xform( objToAlign, p=True, roo=ROT_ORDER_STRS[ initialRo ] )


def cleanDelete( node ):
	'''
	will disconnect all connections made to and from the given node before deleting it
	'''
	if not objExists( node ):
		return

	connections = listConnections( node, connections=True, plugs=True )
	connectionsIter = iter( connections )
	for srcConnection in connectionsIter:
		tgtConnection = connectionsIter.next()

		#we need to test if the connection is valid because a previous disconnection may have affected this one
		if isConnected( srcConnection, tgtConnection ):
			try:
				#this may fail if the dest attr is locked - in which case just skip and hope deleting the node doesn't screw up the attribute value...
				disconnectAttr( srcConnection, tgtConnection )
			except RuntimeError: pass

	cmd.delete( node )


def getObjectBasisVectors( obj ):
	'''
	returns 3 world space orthonormal basis vectors that represent the orientation of the given object
	'''
	worldMatrix = Matrix( cmd.getAttr( '%s.worldMatrix' % obj ), size=4 )

	return Vector( worldMatrix[0][:3] ), Vector( worldMatrix[1][:3] ), Vector( worldMatrix[2][:3] )


def getLocalBasisVectors( obj ):
	'''
	returns 3 world space orthonormal basis vectors that represent the local coordinate system of the given object
	'''
	localMatrix = Matrix( cmd.getAttr( '%s.matrix' % obj ), size=4 )

	return Vector( localMatrix[0][:3] ), Vector( localMatrix[1][:3] ), Vector( localMatrix[2][:3] )


def getPlaneNormalForObjects( objA, objB, objC, defaultVector=MAYA_UP ):
	posA = Vector( xform( objA, q=True, ws=True, rp=True ) )
	posB = Vector( xform( objB, q=True, ws=True, rp=True ) )
	posC = Vector( xform( objC, q=True, ws=True, rp=True ) )

	vecA, vecB = posA - posB, posA - posC
	normal = vecA.cross( vecB )

	#if the normal is too small, just return the given default axis
	if normal.magnitude() < 1e-2:
		normal = defaultVector

	return normal.normalize()


def findPolePosition( end, mid=None, start=None, distanceMultiplier=1 ):

	if not objExists( end ):
		return Vector.Zero()

	try:
		if mid is None:
			mid = listRelatives( end, p=True, pa=True )[0]
		if start is None:
			start = listRelatives( mid, p=True, pa=True )[0]
	except TypeError:
		return Vector.Zero()

	joint0, joint1, joint2 = start, mid, end

	pos0 = Vector( xform( joint0, q=True, ws=True, rp=True ) )
	pos1 = Vector( xform( joint1, q=True, ws=True, rp=True ) )
	pos2 = Vector( xform( joint2, q=True, ws=True, rp=True ) )

	#this is the rough length of the presumably "limb" we're finding the pole vector position for
	lengthFactor = (pos1-pos0).length() + (pos2-pos1).length()

	#get the vectors from 0 to 1, and 0 to 2
	vec0_1 = pos1 - pos0
	vec0_2 = pos2 - pos0

	#project vec0_1 on to vec0_2
	projA_B = vec0_2.normalize() * ( (vec0_1 * vec0_2) / vec0_2.length() )

	#get the vector from the projected vector above, to the mid pos
	sub = vec0_1 - projA_B

	#if the magnitude is really small just return the position of the mid object
	if sub.length() < 1e-4:
		return pos1

	sub = sub.normalize()
	polePos = pos0 + projA_B + (sub * lengthFactor)

	return polePos


def largestT( obj ):
	'''
	returns the index of the translation axis with the highest absolute value
	'''
	pos = getAttr( '%s.t' % obj )[0]
	idx = indexOfLargest( pos )
	if pos[ idx ] < 0:
		idx += 3

	return idx


def indexOfLargest( iterable ):
	'''
	returns the index of the largest absolute valued component in an iterable
	'''
	iterable = [(x, n) for n, x in enumerate( map(abs, iterable) )]
	iterable.sort()

	return Axis( iterable[-1][1] )


def betweenVector( obj1, obj2 ):
	'''
	returns the vector between two objects
	'''
	posA = Vector( xform( obj1, q=True, ws=True, rp=True ) )
	posB = Vector( xform( obj2, q=True, ws=True, rp=True ) )

	return posB - posA


def getAimVector( obj ):
	children = cmd.listRelatives( obj, path=True, typ='transform' ) or []
	if len( children ) == 1:
		return betweenVector(obj, children[0])
	else:
		axisIdx = largestT( obj )
		axisVector = Axis( axisIdx ).asVector()

		#now just return the axis vector in world space
		mat = Matrix( cmd.getAttr( '%s.worldMatrix' % obj ) )

		return multVectorMatrix( axisVector, mat )


def getObjectAxisInDirection( obj, compareVector, defaultAxis=Axis(0) ):
	'''
	returns the axis (an Axis instance) representing the closest object axis to
	the given vector

	the defaultAxis is returned if the compareVector is zero or too small to provide
	meaningful directionality
	'''

	if not isinstance( compareVector, Vector ):
		compareVector = Vector( compareVector )

	xPrime, yPrime, zPrime = getObjectBasisVectors( obj )
	try:
		dots = compareVector.dot( xPrime, True ), compareVector.dot( yPrime, True ), compareVector.dot( zPrime, True )
	except ZeroDivisionError:
		return defaultAxis

	idx = indexOfLargest( dots )
	if dots[ idx ] < 0: idx += 3

	return Axis( idx )


def getLocalAxisInDirection( obj, compareVector ):
	xPrime, yPrime, zPrime = getLocalBasisVectors( obj )
	dots = compareVector.dot( xPrime, True ), compareVector.dot( yPrime, True ), compareVector.dot( zPrime, True )

	idx = indexOfLargest( dots )
	if dots[ idx ] < 0: idx += 3

	return Axis( idx )


def getAnkleToWorldRotation( obj, fwdAxisName='z', performRotate=False ):
	'''
	ankles are often not world aligned and cannot be world aligned on all axes, as the ankle needs to aim toward
	toe joint.  for the purposes of rigging however, we usually want the foot facing foward (or along one of the primary axes
	'''
	fwd = Vector.Axis( fwdAxisName )
	fwdAxis = getObjectAxisInDirection( obj, fwd )
	basisVectors = getObjectBasisVectors( obj )
	fwdVector = basisVectors[ abs( fwdAxis ) ]

	#determine the directionality of the rotation
	direction = -1 if fwdAxis.isNegative() else 1

	#flatten aim vector into the x-z plane
	fwdVector[ AX_Y ] = 0
	fwdVector = fwdVector.normalize() * direction

	#now determine the rotation between the flattened aim vector, and the fwd axis
	angle = fwdVector.dot( fwd )
	angle = Angle( math.acos( angle ), radian=True ).degrees * -direction

	#do the rotation...
	if performRotate:
		cmd.rotate(0, angle, 0, obj, r=True, ws=True)

	return (0, angle, 0)


def getWristToWorldRotation( wrist, performRotate=False ):
	'''
	returns the world space rotation values to align the given object to world axes.  If
	performRotate is True the object will be rotated to this alignment.  The rotation
	values are returned as euler rotation values in degrees
	'''
	worldMatrix, worldScale = Matrix( getAttr( '%s.worldMatrix' % wrist ) ).decompose()
	bases = x, y, z = map( Vector, worldMatrix.crop( 3 ) )

	newBases = []
	allAxes = range( 3 )
	for basis in bases:
		largestAxisValue = -2  #values will never be smaller than this, so the code below will always get run
		largestAxis = 0

		#find which world axis this basis vector best approximates - we want to world align the basis vectors
		for n in range( 3 ):
			absAxisValue = abs( basis[n] )
			if absAxisValue > largestAxisValue:
				largestAxisValue = absAxisValue
				largestAxis = n+3 if basis[n] < 0 else n  #if the dot is negative, shift the axis index by 3 (which makes it negative)

		#track the largestAxisValue too - we want to use it as a measure of closeness
		newBases.append( Axis( largestAxis ).asVector() )

	newBases = map( list, newBases )
	matrixValues = newBases[0] + newBases[1] + newBases[2]
	worldRotMatrix = Matrix( matrixValues, 3 )
	rots = worldRotMatrix.ToEulerXYZ( True )

	if performRotate:
		rotate( rots[0], rots[1], rots[2], wrist, a=True, ws=True )

	return tuple( rots )


def isVisible( dag ):
	'''
	returns whether a dag item is visible or not - it walks up the hierarchy and checks both parent visibility
	as well as layer visibility
	'''
	parent = dag
	while True:
		if not getAttr( '%s.v' % parent ):
			return False

		#check layer membership
		layers = listConnections( parent, t='displayLayer' )
		if layers is not None:
			for l in layers:
				if not getAttr( '%s.v' % l ):
					return False

		try:
			parent = listRelatives( parent, p=True, pa=True )[0]
		except TypeError:
			break

	return True


def areSameObj( objA, objB ):
	'''
	given two objects, returns whether they're the same object or not - object path names make this tricker than it seems
	'''
	try:
		return cmd.ls( objA ) == cmd.ls( objB )
	except TypeError:
		return False


def getBounds( objs ):
	minX, minY, minZ = [], [], []
	maxX, maxY, maxZ = [], [], []

	for obj in objs:
		tempMN = cmd.getAttr( '%s.bbmn' % obj )[ 0 ]
		tempMX = cmd.getAttr( '%s.bbmx' % obj )[ 0 ]
		minX.append( tempMN[ 0 ] )
		minY.append( tempMN[ 1 ] )
		minZ.append( tempMN[ 2 ] )
		maxX.append( tempMX[ 0 ] )
		maxY.append( tempMX[ 1 ] )
		maxZ.append( tempMX[ 2 ] )

	minX.sort()
	minY.sort()
	minZ.sort()
	maxX.sort()
	maxY.sort()
	maxZ.sort()

	return minX[ 0 ], minY[ 0 ], minZ[ 0 ], maxX[ -1 ], maxY[ -1 ], maxZ[ -1 ]


def getTranslationExtents( objs ):
	ts = [ xform( i, q=True, ws=True, rp=True ) for i in objs ]
	xs, ys, zs = [ t[0] for t in ts ], [ t[1] for t in ts ], [ t[2] for t in ts ]
	mnx, mxx = min( xs ), max( xs )
	mny, mxy = min( ys ), max( ys )
	mnz, mxz = min( zs ), max( zs )

	return mnx, mny, mnz, mxx, mxy, mxz


def getObjsScale( objs ):
	mnX, mnY, mnZ, mxX, mxY, mxZ = getBounds( objs )
	x = abs( mxX - mnX )
	y = abs( mxY - mnY )
	z = abs( mxZ - mnZ )

	return (x + y + z) / 3.0 * 0.75  #this is kinda arbitrary


def getJointBounds( joints, threshold=0.65, space=SPACE_OBJECT ):
	'''
	if the joints are skinned, then the influenced verts that have weights greater than the given
	influenced are transformed into the space specified (if SPACE_OBJECT is used, the space of the
	first joint is used), and the bounds of the verts in this space are returned as a 2-tuple of
	bbMin, bbMax
	'''

	global MVector, MTransformationMatrix, Vector

	if not isinstance( joints, (list, tuple) ):
		joints = [ joints ]

	theJoint = joints[ 0 ]
	verts = []

	for j in joints:
		verts += meshUtils.jointVertsForMaya( j, threshold )

	jointDag = apiExtensions.asMDagPath( theJoint )

	if space == SPACE_OBJECT:
		jointMatrix = jointDag.inclusiveMatrix()
	elif space == SPACE_LOCAL:
		jointMatrix = jointDag.exclusiveMatrix()
	elif space == SPACE_WORLD:
		jointMatrix = OpenMaya.MMatrix()
	else: raise TypeError( "Invalid space specified" )

	vJointPos = MTransformationMatrix( jointMatrix ).rotatePivot( kWorld ) + MTransformationMatrix( jointMatrix ).getTranslation( kWorld )
	vJointPos = Vector( [vJointPos.x, vJointPos.y, vJointPos.z] )

	vJointBasisX = MVector(-1,0,0) * jointMatrix
	vJointBasisY = MVector(0,-1,0) * jointMatrix
	vJointBasisZ = MVector(0,0,-1) * jointMatrix

	bbox = MBoundingBox()
	for vert in verts:
		#get the position relative to the joint in question
		vPos = Vector( xform( vert, query=True, ws=True, t=True ) )
		vPos = vJointPos - vPos

		#now transform the joint relative position into the coordinate space of that joint
		#we do this so we can get the width, height and depth of the bounds of the verts
		#in the space oriented along the joint
		vPosInJointSpace = Vector( vPos )
		vPosInJointSpace = vPosInJointSpace.change_space( vJointBasisX, vJointBasisY, vJointBasisZ )

		bbox.expand( MPoint( *vPosInJointSpace ) )

	bbMin, bbMax = bbox.min(), bbox.max()
	bbMin = Vector( [bbMin.x, bbMin.y, bbMin.z] )
	bbMax = Vector( [bbMax.x, bbMax.y, bbMax.z] )

	return bbMin, bbMax


def getJointSizeAndCentre( joints, threshold=0.65, space=SPACE_OBJECT, ignoreSkinning=False ):
	if ignoreSkinning:
		vec = Vector.Zero()
	else:
		minB, maxB = getJointBounds( joints, threshold, space )
		vec = maxB - minB

	#if the bounding box is a point then lets see if we can derive a useful size for the joint based on existing children
	if not vec:

		#make sure we're dealing with a list of joints...
		if not isinstance( joints, (list, tuple) ):
			joints = [ joints ]

		children = listRelatives( joints, pa=True, typ='transform' ) or []

		#if there are no children then we fall back on averaging the "radius" attribute for all given joints...
		if not children:
			radSum = sum( getAttr( '%s.radius' % j ) for j in joints )
			s = float( radSum ) / len( joints ) * 5  #5 is an arbitrary number - tune it as required...

			return Vector( (s, s, s) ), Vector( (0, 0, 0) )

		theJoint = joints[ 0 ]
		theJointPos = Vector( xform( theJoint, q=True, ws=True, rp=True ) )

		#determine the basis vectors for <theJoint>.  we want to transform the joint's size into the appropriate space
		if space == SPACE_OBJECT:
			theJointBasisVectors = getObjectBasisVectors( theJoint )
		elif space == SPACE_LOCAL:
			theJointBasisVectors = getLocalBasisVectors( theJoint )
		elif space == SPACE_WORLD:
			theJointBasisVectors = Vector( (1,0,0) ), Vector( (0,1,0) ), Vector( (0,0,1) )
		else: raise TypeError( "Invalid space specified" )

		bbox = MBoundingBox()
		bbox.expand( MPoint( 0, 0, 0 ) )  #make sure zero is included in the bounding box - zero is the position of <theJoint>
		for j in joints[ 1: ] + children:
			pos = Vector( xform( j, q=True, ws=True, rp=True ) ) - theJointPos
			pos = pos.change_space( *theJointBasisVectors )
			bbox.expand( MPoint( *pos ) )

		minB, maxB = bbox.min(), bbox.max()
		minB = Vector( (minB.x, minB.y, minB.z) )
		maxB = Vector( (maxB.x, maxB.y, maxB.z) )
		vec = maxB - minB

	centre = (minB + maxB) / 2.0

	return Vector( map( abs, vec ) ), centre

getJointSizeAndCenter = getJointSizeAndCentre  #for spelling n00bs


def getJointSize( joints, threshold=0.65, space=SPACE_OBJECT ):
	return getJointSizeAndCentre( joints, threshold, space )[ 0 ]


def ikSpringSolver( start, end, **kw ):
	'''
	creates an ik spring solver - this is wrapped simply because its not default
	maya functionality, and there is potential setup work that needs to be done
	to ensure its possible to create an ik chain using the spring solver
	'''

	mel.ikSpringSolver()
	kw[ 'solver' ] = 'ikSpringSolver'

	handle, effector = cmd.ikHandle( '%s.rotatePivot' % start, '%s.rotatePivot' % end, **kw )

	#now we want to ensure a sensible pole vector - so set that up
	jointChain = getChain( start, end )
	poleVectorAttrVal = xform( jointChain[1], q=True, ws=True, rp=True )
	restPoleVector = betweenVector( jointChain[0], jointChain[1] )

	setAttr( '%s.springRestPoleVector' % handle, *restPoleVector )
	setAttr( '%s.poleVector' % handle, *poleVectorAttrVal )

	return handle, effector


def resetSkinCluster( skinCluster ):
	'''
	splats the current pose of the skeleton into the skinCluster - ie whatever
	the current pose is becomes the bindpose
	'''

	skinInputMatrices = listConnections( '%s.matrix' % skinCluster, plugs=True, connections=True, destination=False )

	#this happens if the skinCluster is bogus - its possible for deformers to become orphaned in the scene
	if skinInputMatrices is None:
		return

	#get a list of dag pose nodes connected to the skin cluster
	dagPoseNodes = listConnections( skinCluster, d=False, type='dagPose' ) or []

	iterInputMatrices = iter( skinInputMatrices )
	for dest in iterInputMatrices:
		src = iterInputMatrices.next()
		srcNode = src.split( '.' )[ 0 ]
		idx = dest[ dest.rfind( '[' )+1:-1 ]
		matrixAsStr = ' '.join( map( str, cmd.getAttr( '%s.worldInverseMatrix' % srcNode ) ) )
		melStr = 'setAttr -type "matrix" %s.bindPreMatrix[%s] %s' % (skinCluster, idx, matrixAsStr)
		mel.eval( melStr )

		#reset the stored pose in any dagposes that are conn
		for dPose in dagPoseNodes:
			dagPose( srcNode, reset=True, n=dPose )


def enableSkinClusters():
	for c in ls( type='skinCluster' ):
		resetSkinCluster( c )
		setAttr( '%s.nodeState' % c, 0 )


def disableSkinClusters():
	for c in ls( type='skinCluster' ):
		setAttr( '%s.nodeState' % c, 1 )


def getSkinClusterEnableState():
	for c in ls( type='skinCluster' ):
		if getAttr( '%s.nodeState' % c ) == 1:
			return False

	return True


def buildMeasure( startNode, endNode ):
	measure = createNode( 'distanceDimShape', n='%s_to_%s_measureShape#' % (startNode, endNode) )
	measureT = listRelatives( measure, p=True, pa=True )[ 0 ]

	locA = spaceLocator()[ 0 ]
	locB = spaceLocator()[ 0 ]
	cmd.parent( locA, startNode, r=True )
	cmd.parent( locB, endNode, r=True )

	locAShape = listRelatives( locA, s=True, pa=True )[ 0 ]
	locBShape = listRelatives( locB, s=True, pa=True )[ 0 ]

	connectAttr( '%s.worldPosition[ 0 ]' % locAShape, '%s.startPoint' % measure, f=True )
	connectAttr( '%s.worldPosition[ 0 ]' % locBShape, '%s.endPoint' % measure, f=True )

	return measureT, measure, locA, locB


def buildAnnotation( obj, text='' ):
	'''
	like the distance command above, this is a simple wrapper for creating annotation nodes,
	and having the nodes you actually want returned to you.  whoever wrote these commands
	should be shot.  with a large gun

	returns a 3 tuple containing the start transform, end transform, and annotation shape node
	'''
	obj = str( obj )  #cast as string just in case we've been passed a PyNode instance

	rand = random.randint
	end = spaceLocator()[ 0 ]
	shape = annotate( end, p=(rand(0, 1000000), rand(1000000, 2000000), 2364), tx=text )

	start = listRelatives( shape, p=True, pa=True )[ 0 ]
	endShape = listRelatives( end, s=True, pa=True )[ 0 ]

	delete( parentConstraint( obj, end ) )
	for ax in Axis.AXES[ :3 ]:
		setAttr( '%s.t%s' % (start, ax), 0 )

	setAttr( '%s.v' % endShape, 0 )
	setAttr( '%s.v' % endShape, lock=True )
	cmd.parent( end, obj )

	return start, end, shape


def getChain( startNode, endNode ):
	'''
	returns a list of all the joints from the given start to the end inclusive
	'''
	chainNodes = [ endNode ]
	for p in apiExtensions.iterParents( endNode ):
		if not p:
			raise ValueError( "Chain terminated before reaching the end node!" )

		chainNodes.append( p )
		if apiExtensions.cmpNodes( p, startNode ):  #cmpNodes is more reliable than just string comparing - cmpNodes casts to MObjects and compares object handles
			break

	chainNodes.reverse()

	return chainNodes


def chainLength( startNode, endNode ):
	'''
	measures the length of the chain were it to be straightened out
	'''
	length = 0
	curNode = endNode
	for p in apiExtensions.iterParents( endNode ):
		curPos = Vector( xform( curNode, q=True, ws=True, rp=True ) )
		parPos = Vector( xform( p, q=True, ws=True, rp=True ) )
		dif = curPos - parPos
		length += dif.get_magnitude()

		if apiExtensions.cmpNodes( p, startNode ):  #cmpNodes is more reliable than just string comparing - cmpNodes casts to MObjects and compares object handles
			break

		curNode = p

	return length


def switchToFK( control, ikHandle=None, onCmd=None, offCmd=None ):
	'''
	this proc will align the bones controlled by an ik chain to the fk chain

		ikHandle  this flag specifies the name of the ikHandle to work on
		onCmd     this flag tells the script what command to run to turn the ik handle on - it is often left blank because its assumed we're already in ik mode
		offCmd    this flag holds the command to turn the ik handle off, and switch to fk mode

	NOTE: if the offCmd isn't specified, it defaults to:  lambda c, ik: setAttr( '%s.ikBlend' % c, 0 )

	both on and off callbacks take 2 args - the control and the ikHandle

	example:
	switchToFK( ikHandle1, onCmd=lambda ctrl, ik: setAttr( '%s.ikBlend' % ik, 1 ), offCmd=lambda c, ik: setAttr( '%s.ikBlend' % ik, 0 ) )
	'''
	if ikHandle is None:
		ikHandle = control

	if onCmd is None:
		onCmd = lambda c, ik: setAttr( '%s.ikBlend' % c, 0 )

	if callable( onCmd ):
		onCmd( control, ikHandle )

	joints = cmd.ikHandle( ikHandle, q=True, jl=True )
	effector = cmd.ikHandle( ikHandle, q=True, ee=True )
	effectorCtrl = listConnections( '%s.tx' % effector, d=False )[ 0 ]
	jRotations = [ getAttr( '%s.r' % j ) for j in joints ]

	if callable( offCmd ):
		offCmd( control, ikHandle )

	for j, rot in zip( joints, jRotations ):
		if getAttr( '%s.rx' % j, settable=True ): setAttr( '%s.rx' % j, rot[ 0 ] )
		if getAttr( '%s.ry' % j, settable=True ): setAttr( '%s.ry' % j, rot[ 1 ] )
		if getAttr( '%s.rz' % j, settable=True ): setAttr( '%s.rz' % j, rot[ 2 ] )


def switchToIK( control, ikHandle=None, poleControl=None, onCmd=None, offCmd=None ):
	'''
	this proc will align the IK controller to its fk chain
	flags used:
	-control   this is the actual control being used to move the ikHandle - it is assumed to be the same object as the ikHandle, but if its different (ie if the ikHandle is constrained to a controller) use this flag
	-pole      tells the script the name of the pole controller - if there is no pole vector control, leave this flag out
	-ikHandle  this flag specifies the name of the ikHandle to work on
	-onCmd     this flag tells the script what command to run to turn the ik handle on - it is often left blank because its assumed we're already in ik mode
	-offCmd    this flag holds the command to turn the ik handle off, and switch to fk mode
	NOTE: if the offCmd isn't specified, it defaults to:  if( `getAttr -se ^.ikb` ) setAttr ^.ikb 1;

	symbols to use in cmd strings:
	 ^  refers to the ikHandle
	 #  refers to the control object

	example:
	zooAlignIK "-control somObj -ikHandle ikHandle1 -offCmd setAttr #.fkMode 0";
	'''
	if ikHandle is None:
		ikHandle = control

	if callable( onCmd ):
		onCmd( control, ikHandle, poleControl )

	joints = cmd.ikHandle( ikHandle, q=True, jl=True )
	effector = cmd.ikHandle( ikHandle, q=True, ee=True )
	effectorCtrl = listConnections( '%s.tx' % effector, d=False )[ 0 ]

	mel.zooAlign( "-src %s -tgt %s" % (effectorCtrl, control) )
	if poleControl is not None and objExists( poleControl ):
		pos = mel.zooFindPolePosition( "-start %s -mid %s -end %s" % (joints[ 0 ], joints[ 1 ], effectorCtrl) )
		move( pos[0], pos[1], pos[2], poleControl, a=True, ws=True, rpr=True )

	if callable( offCmd ):
		offCmd( control, ikHandle, poleControl )


def replaceConstraintTarget( constraint, newTarget, targetIndex=0 ):
	'''
	replaces the target at "targetIndex" with the new target
	'''
	newTarget = apiExtensions.asMObject( str( newTarget ) )

	for attr in attributeQuery( 'target', node=constraint, listChildren=True ):
		for connection in listConnections( '%s.target[%s].%s' % (constraint, targetIndex, attr), p=True, type='transform', d=False ) or []:
			toks = connection.split( '.' )
			node = toks[ 0 ]

			if not apiExtensions.cmpNodes( node, newTarget ):
				toks[ 0 ] = str( newTarget )
				connectAttr( '.'.join( toks ), '%s.target[%s].%s' % (constraint, targetIndex, attr), f=True )


def replaceGivenConstraintTarget( constraint, targetToReplace, newTarget ):
	'''
	replaces targetToReplace transform on the given constraint with the newTarget transform
	'''
	targetToReplace = apiExtensions.asMObject( targetToReplace )
	newTarget = apiExtensions.asMObject( newTarget )

	#nothing to do if the nodes are the same...
	if apiExtensions.cmpNodes( targetToReplace, newTarget ):
		return

	usedTargetIndices = getAttr( '%s.target' % constraint, multiIndices=True )
	for idx in usedTargetIndices:
		for attr in attributeQuery( 'target', node=constraint, listChildren=True ):
			for connection in listConnections( '%s.target[%s].%s' % (constraint, idx, attr), p=True, type='transform', d=False ) or []:
				toks = connection.split( '.' )
				node = toks[ 0 ]

				if apiExtensions.cmpNodes( node, targetToReplace ):
					toks[ 0 ] = str( newTarget )
					connectAttr( '.'.join( toks ), '%s.target[%s].%s' % (constraint, idx, attr), f=True )


def setupBaseLimbTwister( joint, aimObject, upObject, aimAxis ):
	'''
	Builds a bicep twist rig.

	Bicep twist joints are basically joints that sit next to the bicep (humerous) in the hierarchy and take
	all the weighting of the deltoid and upper triceps.  Bicep twists don't rotate on their twist axis, but
	aim at the elbow, so they basically do exactly as the humerous does but don't twist.
	'''
	if not isinstance( aimAxis, Axis ):
		aimAxis = Axis.FromName( aimAxis )

	upAxes = [ ax.asVector() for ax in aimAxis.otherAxes() ]

	joint = apiExtensions.asMObject( joint )
	upObject = apiExtensions.asMObject( upObject )

	jWorldMatrix = joint.getWorldMatrix()
	upVectorsWorld = [ ax * jWorldMatrix for ax in upAxes ]

	upWorldInvMatrix = upObject.getWorldInverseMatrix()

	#we want to transform the aimObject's two different axes into the space of the up object
	upVectorsLocal = [ upVectorsWorld[0] * upWorldInvMatrix,
	                   upVectorsWorld[1] * upWorldInvMatrix ]

	matrixMult = createNode( 'pointMatrixMult', n='bicepTwister_primaryUpAxis' )
	setAttr( '%s.inPoint' % matrixMult, *upVectorsLocal[0] )
	setAttr( '%s.vectorMultiply' % matrixMult, True )
	connectAttr( '%s.worldMatrix[0]' % upObject, '%s.inMatrix' % matrixMult )

	vectorProduct = createNode( 'vectorProduct' )
	connectAttr( '%s.output' % matrixMult, '%s.input1' % vectorProduct )
	setAttr( '%s.operation' % vectorProduct, 1 )

	aimNode = aimConstraint( aimObject, joint, aim=aimAxis.asVector(), wuo=upObject, wut='objectrotation' )[0]
	addAttr( aimNode, ln='upAndAimDot', at='double' )

	#create an expression to normalize the constraintVector attribute coming out of the aimConstraint node - its not normalized, and the vector product node doesn't normalize inputs (wtf?!)
	expressionStr = '''float $mag = sqrt( (%(aimNode)s.constraintVectorX * %(aimNode)s.constraintVectorX) + (%(aimNode)s.constraintVectorY * %(aimNode)s.constraintVectorY) + (%(aimNode)s.constraintVectorZ * %(aimNode)s.constraintVectorZ) ) + 1;
float $normX = %(aimNode)s.constraintVectorX / $mag;
float $normY = %(aimNode)s.constraintVectorY / $mag;
float $normZ = %(aimNode)s.constraintVectorZ / $mag;
%(vectorProduct)s.input2X = %(matrixMult)s.outputX * $normX;
%(vectorProduct)s.input2Y = %(matrixMult)s.outputX * $normY;
%(vectorProduct)s.input2Z = %(matrixMult)s.outputX * $normZ;''' % locals()

	expression( s=expressionStr )

	sdkDriver = '%s.outputX' % vectorProduct
	connectAttr( sdkDriver, '%s.upAndAimDot' % aimNode )

	for upAxis, upVector, driverValues in zip( upAxes, upVectorsLocal, ((0, 0.1), (0.9, 1)) ):
		for driverValue in driverValues:
			for upAxisValue, upVectorValue, axisName in zip( upAxis, upVector, Axis.BASE_AXES ):
				axisName = axisName.upper()
				setDrivenKeyframe( '%s.upVector%s' % (aimNode, axisName), value=upAxisValue,
					               currentDriver=sdkDriver, driverValue=driverValue, itt='linear', ott='linear' )

				setDrivenKeyframe( '%s.worldUpVector%s' % (aimNode, axisName), value=upVectorValue,
					               currentDriver=sdkDriver, driverValue=driverValue, itt='linear', ott='linear' )

	for axisName in Axis.BASE_AXES:
		axisName = axisName.upper()
		setInfinity( '%s.upVector%s' % (aimNode, axisName), pri='oscillate', poi='oscillate' )
		setInfinity( '%s.worldUpVector%s' % (aimNode, axisName), pri='oscillate', poi='oscillate' )


def reorderAttrs( obj, newAttribOrder ):
	for attr in newAttribOrder:
		objAttrpath = '%s.%s' % (obj, attr)

		#if the attribute is locked, we'll need to unlock it to rename it
		isAttrLocked = getAttr( objAttrpath, l=True )
		if isAttrLocked:
			setAttr( objAttrpath, l=False )

		#rename the attribute to a temporary name.  You can't rename it to its own name, so we need to rename it to a proxy name, and then back again
		tempAttrname = '_temp__123xx'
		while objExists( '%s.%s' % (obj, tempAttrname) ):
			tempAttrname += '_1'

		tempAttrib = renameAttr( objAttrpath, tempAttrname )
		renameAttr( '%s.%s' % (obj, tempAttrname), attr )

		#if the attribute WAS locked, lock it again, in order to maximise transparency
		if isAttrLocked:
			setAttr( objAttrpath, l=True )


def dumpNodeAttrs( node ):
	'''
	simple debug function - you can use this to dump out attributes for nodes, stick em in a text file and do a diff
	can be useful for tracking down how various undocumented nodes mysteriously work
	'''
	attrs = listAttr( node )
	for attr in attrs:
		try:
			print attr, getAttr( '%s.%s' % (node, attr) )
			if attributeQuery( attr, n=node, multi=True ):
				indices = getAttr( '%s.%s' % (node, attr), multiIndices=True ) or []
				for idx in indices:
					print '\t%d %s' % (idx, getAttr( '%s.%s[%d]' % (node, attr, idx) ))
		except RuntimeError:
			print attr
		except TypeError:
			print attr


del( control )


#end
