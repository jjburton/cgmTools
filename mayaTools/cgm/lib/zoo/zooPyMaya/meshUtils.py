'''
this script contains a bunch of useful poly mesh functionality.  at this stage its not really
much more than a bunch of functional scripts - there hasn't been any attempt to objectify any
of this stuff yet.  as it grows it may make sense to step back a bit and think about how to
design this a little better
'''

from maya.cmds import *
from maya.OpenMayaAnim import MFnSkinCluster

import maya.cmds as cmd
import maya.OpenMaya as OpenMaya

from zooPy.vectors import Vector, Matrix
from zooPy.path import Path

from mayaDecorators import d_progress

import apiExtensions

kMAX_INF_PER_VERT = 3
kMIN_SKIN_WEIGHT_VALUE = 0.05


def getASelection():
	'''
	returns the first object selected or None if no selection - saves having to write this logic over and over
	'''
	sel = ls( sl=True )
	if not sel:
		return None

	return sel[0]


def numVerts( mesh ):
	return len( cmd.ls("%s.vtx[*]" % mesh, fl=True) )


def numFaces( mesh ):
	return len( cmd.ls("%s.f[*]" % mesh, fl=True) )


def selectFlipped():
	sel = cmd.ls(selection=True)
	cmd.select(clear=True)
	flipped = findFlipped(sel)
	if len(flipped):
		cmd.select(flipped,add=True)


def findFlipped( obj ):
	flipped = []
	faces = cmd.polyListComponentConversion( obj, toFace=True )
	if not faces:
		return flipped

	faces = cmd.ls( faces, flatten=True )
	for face in faces:
		uvNormal = getUVFaceNormal(face)

		#if the uv face normal is facing into screen then its flipped - add it to the list
		if uvNormal * Vector([0, 0, 1]) < 0:
			flipped.append(face)

	return flipped


def getWindingOrder( facepath, doUvs=True ):
	'''will return the uvs or verts of a face in their proper 'winding order'.  this can be used to determine
	things like uv face normals and...  well, pretty much that'''
	toReturn = []
	vtxFaces = cmd.ls(cmd.polyListComponentConversion(facepath,toVertexFace=True),flatten=True)
	for vtxFace in vtxFaces:
		if doUvs:
			uvs = cmd.polyListComponentConversion(vtxFace,fromVertexFace=True,toUV=True)
			toReturn.append( uvs[0] )
		else:
			vtx = cmd.polyListComponentConversion(vtxFace,fromVertexFace=True,toVertex=True)
			toReturn.append( vtx[0] )

	return toReturn


def getUVFaceNormal( facepath ):
	uvs = getWindingOrder(facepath)

	if len(uvs) < 3: return (1,0,0) #if there are less than 3 uvs we have no uv area so bail

	#get edge vectors and cross them to get the uv face normal
	uvAPos = cmd.polyEditUV(uvs[0], query=True, uValue=True, vValue=True)
	uvBPos = cmd.polyEditUV(uvs[1], query=True, uValue=True, vValue=True)
	uvCPos = cmd.polyEditUV(uvs[2], query=True, uValue=True, vValue=True)
	uvAB = Vector( [uvBPos[0]-uvAPos[0], uvBPos[1]-uvAPos[1], 0] )
	uvBC = Vector( [uvCPos[0]-uvBPos[0], uvCPos[1]-uvBPos[1], 0] )
	uvNormal = uvAB.cross( uvBC ).normalize()

	return uvNormal


def getFaceNormal( facepath ):
	verts = getWindingOrder(facepath,False)

	if len(verts) < 3: return (1, 0, 0) #if there are less than 3 verts we have no uv area so bail

	#get edge vectors and cross them to get the uv face normal
	vertAPos = Vector(cmd.xform(verts[0], query=True, worldSpace=True, absolute=True, translation=True))
	vertBPos = Vector(cmd.xform(verts[1], query=True, worldSpace=True, absolute=True, translation=True))
	vertCPos = Vector(cmd.xform(verts[2], query=True, worldSpace=True, absolute=True, translation=True))
	vecAB = vertBPos - vertAPos
	vecBC = vertCPos - vertBPos
	faceNormal = (vecAB ^ vecBC).normalize()

	return faceNormal


def extractFaces( faceList, delete=False ):
	'''
	extracts the given faces into a separate object - unlike the maya function, this is actually
	useful...  the given faces are extracted to a separate object, and can be optionally deleted from
	the original mesh if desired, or just duplicated out.
	'''
	newMeshes = []

	#get a list of meshes present in the facelist
	cDict = componentListToDict( faceList )
	for mesh, faces in cDict.iteritems():
		#is the mesh a shape or a transform - if its a shape, get its transform
		if cmd.nodeType( mesh ) == 'mesh':
			mesh = cmd.listRelatives( mesh, pa=True, p=True )[ 0 ]

		dupeMesh = cmd.duplicate( mesh, renameChildren=True )[ 0 ]
		children = cmd.listRelatives( dupeMesh, pa=True, typ='transform' )
		if children:
			cmd.delete( children )

		#unlock transform channels - if possible anyway
		try:
			for c in ('t', 'r', 's'):
				setAttr( '%s.%s' % (dupeMesh, c), l=False )
				for ax in ('x', 'y', 'z'):
					setAttr( '%s.%s%s' % (dupeMesh, c, ax), l=False )
		except RuntimeError: pass

		#now delete all faces except those we want to keep
		cmd.select( [ '%s.f[%d]' % (dupeMesh, idx) for idx in range( numFaces( dupeMesh ) ) ] )
		cmd.select( [ '%s.f[%d]' % (dupeMesh, idx) for idx in faces ], deselect=True )
		cmd.delete()

		newMeshes.append( dupeMesh )

	if delete:
		cmd.delete( faceList )

	return newMeshes


def extractMeshForEachJoint( joints, tolerance=1e-4 ):
	extractedMeshes = []
	for j in joints:
		meshes = extractFaces( jointFacesForMaya( j, tolerance ) )
		extractedMeshes += meshes
		for m in meshes:
			#unlock all xform attrs
			for at in 't', 'r', 's':
				cmd.setAttr( '%s.%s' % (m, at), l=False )
				for ax in 'x', 'y', 'z':
					cmd.setAttr( '%s.%s%s' % (m, at, ax), l=False )

			cmd.parent( m, j )
			args = cmd.xform( j, q=True, ws=True, rp=True ) + [ '%s.rotatePivot' % m, '%s.scalePivot' % m ]
			cmd.move( *args )
			cmd.makeIdentity( m, a=True, t=True, r=True, s=True )
			cmd.parent( m, world=True )

	return extractedMeshes


def extractMeshForJoints( joints, tolerance=0.25, expand=0 ):
	'''
	given a list of joints this will extract the mesh influenced by these joints into
	a separate object.  the default tolerance is high because verts are converted to
	faces which generally results in a larger than expected set of faces
	'''
	faces = []
	joints = map( str, joints )
	for j in joints:
		faces += jointFacesForMaya( j, tolerance, False )

	if not faces:
		return None

	theJoint = joints[ 0 ]

	meshes = extractFaces( faces )
	grp = cmd.group( em=True, name='%s_mesh#' % theJoint )
	cmd.delete( cmd.parentConstraint( theJoint, grp ) )

	for m in meshes:
		#unlock all xform attrs
		for at in 't', 'r', 's':
			cmd.setAttr( '%s.%s' % (m, at), l=False )
			for ax in 'x', 'y', 'z':
				cmd.setAttr( '%s.%s%s' % (m, at, ax), l=False )

		if expand > 0:
			cmd.polyMoveFacet( "%s.vtx[*]" % m, ch=False, ltz=expand )

		#parent to the grp and freeze transforms to ensure the shape's space is the same as its new parent
		cmd.parent( m, grp )
		cmd.makeIdentity( m, a=True, t=True, r=True, s=True )

		#parent all shapes to the grp
		cmd.parent( cmd.listRelatives( m, s=True, pa=True ), grp, add=True, s=True )

		#delete the mesh transform
		cmd.delete( m )

	#remove any intermediate objects...
	for shape in listRelatives( grp, s=True, pa=True ):
		if getAttr( '%s.intermediateObject' % shape ):
			delete( shape )

	return grp


def autoGenerateRagdollForEachJoint( joints, threshold=0.65 ):
	convexifiedMeshes = []
	for j in joints:
		meshes = extractMeshForEachJoint( [ j ], threshold )
		if len( meshes ) > 1:
			mesh = cmd.polyUnite( meshes, ch=False )[ 0 ]
			cmd.delete( meshes )
			meshes = [ mesh ]
		else: mesh = meshes[ 0 ]

		convexifiedMesh = convexifyObjects( mesh )[ 0 ]
		convexifiedMesh = cmd.rename( convexifiedMesh, j +'_ragdoll' )
		cmd.skinCluster( [ j ], convexifiedMesh )

		cmd.delete( meshes )

		convexifiedMeshes.append( convexifiedMesh )

	return convexifiedMeshes


def isPointInCube( point, volumePos, volumeScale, volumeBasis ):
	'''
	'''
	x, y, z = volumeScale

	#make the point's position relative to the volume, and transform it to the volume's local orientation
	pointRel = point - volumePos
	pointRel = pointRel.change_space( *volumeBasis )

	if -x<= pointRel.x <=x  and  -y<= pointRel.y <=y  and  -z<= pointRel.z <=z:
		acc = 0
		for x, px in zip((x, y, z), (point.x, point.y, point.z)):
			try: acc += x/px
			except ZeroDivisionError: acc += 1
		weight = 1 -(acc/3)
		return True, weight

	return False


def isPointInSphere( point, volumePos, volumeScale, volumeBasis ):
	'''
	returns whether a given point is contained within a scaled sphere
	'''
	x, y, z = volumeScale

	#make the point's position relative to the volume, and transform it to the volume's local orientation
	pointRel = point - volumePos
	pointRel = pointRel.change_space(*volumeBasis)

	if -x<= pointRel.x <=x  and  -y<= pointRel.y <=y  and  -z<= pointRel.z <=z:
		pointN = vectors.Vector(pointRel)
		pointN.x /= x
		pointN.y /= y
		pointN.z /= z
		pointN = pointN.normalize()
		pointN.x *= x
		pointN.y *= y
		pointN.z *= z

		if pointRel.magnitude() <= pointN.mag:
			weight = 1 -(pointRel.magnitude() / pointN.magnitude())
			return True, weight

	return False


def isPointInUniformSphere( point, volumePos, volumeRadius, UNUSED_BASIS=None ):
	pointRel = point - volumePos
	radius = volumeRadius[0]
	if -radius<= pointRel.x <=radius  and  -radius<= pointRel.y <=radius  and  -radius<= pointRel.z <=radius:
		if pointRel.magnitude() <= radius:
			weight = 1 -(pointRel.magnitude() / radius)
			return True, weight

	return False


def findFacesInVolumeForMaya( meshes, volume, contained=False ):
	'''
	does the conversion from useful dict to maya selection string - generally only useful to mel trying
	to interface with this functionality
	'''
	objFacesDict = findFacesInVolume(meshes, volume, contained)
	allFaces = []
	for mesh, faces in objFacesDict.iteritems():
		allFaces.extend( ['%s.%s' % (mesh, f) for f in faces] )

	return allFaces


def findVertsInVolumeForMaya( meshes, volume ):
	'''
	does the conversion from useful dict to maya selection string - generally only useful to mel trying
	to interface with this functionality
	'''
	objVertDict = findVertsInVolume(meshes, volume)
	allVerts = []
	for mesh, verts in objVertDict.iteritems():
		allVerts.extend( ['%s.vtx[%s]' % (mesh, v.id) for v in verts] )
	return allVerts


def findFacesInVolume( meshes, volume, contained=False ):
	'''
	returns a dict containing the  of faces within a given volume.  if contained is True, then only faces wholly contained
	by the volume are returned
	'''
	meshVertsWithin = findVertsInVolume(meshes, volume)
	meshFacesWithin = {}
	for mesh,verts in meshVertsWithin.iteritems():
		if not verts: continue
		meshFacesWithin[mesh] = []
		vertNames = ['%s.vtx[%d]' % (mesh, v.id) for v in verts]

		if contained:
			faces = set(cmd.ls(cmd.polyListComponentConversion(vertNames, toFace=True), fl=True))
			[faces.remove(f) for f in cmd.ls(cmd.polyListComponentConversion(vertNames, toFace=True, border=True), fl=True)]
			meshFacesWithin[mesh] = [f.split('.')[1] for f in faces]
		else:
			faces = cmd.ls(cmd.polyListComponentConversion(vertNames, toFace=True), fl=True)
			meshFacesWithin[mesh] = [f.split('.')[1] for f in faces]

	return meshFacesWithin


def findVertsInVolume( meshes, volume ):
	'''
	returns a dict containing meshes and the list of vert attributes contained
	within the given <volume>
	'''
	#define a super simple vector class to additionally record vert id with position...
	class VertPos(Vector):
		def __init__( self, x, y, z, vertIdx=None ):
			Vector.__init__(self, [x, y, z])
			self.id = vertIdx

	#this dict provides the functions used to determine whether a point is inside a volume or not
	insideDeterminationMethod = {ExportManager.kVOLUME_SPHERE: isPointInSphere,
								 ExportManager.kVOLUME_CUBE: isPointInCube}

	#if there are any uniform overrides for the contained method (called if the volume's scale is
	#unity) it can be registered here
	insideDeterminationIfUniform = {ExportManager.kVOLUME_SPHERE: isPointInUniformSphere,
									ExportManager.kVOLUME_CUBE: isPointInCube}

	#grab any data we're interested in for the volume
	volumePos = Vector( cmd.xform(volume, q=True, ws=True, rp=True) )
	volumeScale = map(abs, cmd.getAttr('%s.s' % volume)[0])
	volumeBasis = rigUtils.getObjectBasisVectors( volume )

	#make sure the basis is normalized
	volumeBasis = [v.normalize() for v in volumeBasis]

	#now lets determine the volume type
	type = ExportManager.kVOLUME_SPHERE
	try: type = int( cmd.getAttr('%s.exportVolume' % volume) )
	except TypeError: pass

	isContainedMethod = insideDeterminationMethod[type]
	print 'method for interior volume determination', isContainedMethod.__name__
	sx = volumeScale[0]
	if Vector(volumeScale).within((sx, sx, sx)):
		try: isContainedMethod = insideDeterminationIfUniform[type]
		except KeyError: pass

	#now lets iterate over the geometry
	meshVertsWithin = {}
	for mesh in meshes:
		#its possible to pass not a mesh but a component in - this is totally valid, as the polyListComponentConversion
		#should make sure we're always dealing with verts no matter what, but we still need to make sure the dict key is
		#the actual name of the mesh - hence this bit of jiggery pokery
		dotIdx = mesh.rfind('.')
		meshName = mesh if dotIdx == -1 else mesh[:dotIdx]

		meshPositions = []
		meshVertsWithin[meshName] = meshPositions

		#this gives us a huge list of floats - each sequential triple is the position of a vert
		try:
			#if this complains its most likely coz the geo is bad - so skip it...
			vertPosList = cmd.xform(cmd.ls(cmd.polyListComponentConversion(mesh, toVertex=True), fl=True), q=True, t=True, ws=True)
		except TypeError: continue
		count = len(vertPosList)/3

		for idx in xrange(count):
			pos = VertPos(vertPosList.pop(0), vertPosList.pop(0), vertPosList.pop(0), idx)
			contained = isContainedMethod(pos, volumePos, volumeScale, volumeBasis)
			if contained:
				pos.weight = contained[1]
				meshPositions.append( pos )

	return meshVertsWithin


def isNodeVisible( node ):
	'''
	its actually a bit tricky to determine whether a node is visible or not.  A node is hidden if any parent is hidden
	by either having a zero visibility attribute.  It could also be in a layer or be parented to a node in a layer that
	is turned off...

	This function will sort all that crap out and return a bool representing the visibility of the given node
	'''

	def isVisible( n ):
		#obvious check first
		if not getAttr( '%s.v' % node ):
			return False

		#now check the layer
		displayLayer = listConnections( '%s.drawOverride' % n, d=False, type='displayLayer' )
		if displayLayer:
			if not getAttr( '%s.v' % displayLayer[0] ):
				return False

		return True

	#check the given node
	if not isVisible( node ):
		return False

	#now walk up the DAG and check visibility on parents
	parent = listRelatives( node, p=True, pa=True )
	while parent:
		if not isVisible( parent[0] ):
			return False

		parent = listRelatives( parent, p=True, pa=True )

	return True


def jointVerts( joint, tolerance=1e-4, onlyVisibleMeshes=True ):
	'''
	returns a dict containing data about the verts influences by the given joint - dict keys are mesh names the
	joint affects.  each dict value is a list of tuples containing (weight, idx) for the verts affected by the joint
	'''
	newObjs = []
	meshVerts = {}

	joint = apiExtensions.asMObject( joint )
	jointMDag = joint.dagPath()
	try:
		skins = list( set( listConnections( joint, s=0, type='skinCluster' ) ) )
	except TypeError:
		return meshVerts

	MObject = OpenMaya.MObject
	MDagPath = OpenMaya.MDagPath
	MDoubleArray = OpenMaya.MDoubleArray
	MSelectionList = OpenMaya.MSelectionList
	MIntArray = OpenMaya.MIntArray
	MFnSingleIndexedComponent = OpenMaya.MFnSingleIndexedComponent
	for skin in skins:
		skin = apiExtensions.asMObject( skin )
		mfnSkin = MFnSkinCluster( skin )

		mSel = MSelectionList()
		mWeights = MDoubleArray()
		mfnSkin.getPointsAffectedByInfluence( jointMDag, mSel, mWeights )

		for n in range( mSel.length() ):
			mesh = MDagPath()
			component = MObject()
			mSel.getDagPath( n, mesh, component )

			#if we only want visible meshes - check to see that this mesh is visible
			if onlyVisibleMeshes:
				if not isNodeVisible( mesh ):
					continue

			c = MFnSingleIndexedComponent( component )
			idxs = MIntArray()
			c.getElements( idxs )

			meshVerts[ mesh.partialPathName() ] = [ (w, idx) for idx, w in zip( idxs, mWeights ) if w > tolerance ]

	return meshVerts


def jointVertsForMaya( joint, tolerance=1e-4, onlyVisibleMeshes=True ):
	'''
	converts the dict returned by jointVerts into maya useable component names
	'''
	items = []
	for mesh, data in jointVerts( joint, tolerance, onlyVisibleMeshes ).iteritems():
		items.extend( ['%s.vtx[%d]' % (mesh, n) for w, n in data] )

	return items


def jointFacesForMaya( joint, tolerance=1e-4, contained=True ):
	'''
	returns a list containing the faces influences by the given joint
	'''
	verts = jointVertsForMaya( joint, tolerance )
	if not verts:
		return []

	if contained:
		faceList = cmd.polyListComponentConversion( verts, toFace=True )
		if faceList:
			faceList = set( cmd.ls( faceList, fl=True ) )
			for f in cmd.ls( cmd.polyListComponentConversion( verts, toFace=True, border=True ), fl=True ):
				faceList.remove( f )

		jointFaces = list( faceList )
	else:
		jointFaces = cmd.ls( cmd.polyListComponentConversion( verts, toFace=True ), fl=True )

	return jointFaces


def jointFaces( joint, tolerance=1e-4, contained=True ):
	'''
	takes the list of maya component names from jointFacesForMaya and converts them to a dict with teh same format
	as jointVerts().  this is backwards for faces simply because its based on grabbing the verts, and transforming
	them to faces, and then back to a dict...
	'''
	return componentListToDict( jointFacesForMaya( joint, tolerance, contained ) )


def componentListToDict( componentList ):
	componentDict = {}
	if not componentList:
		return componentDict

	#detect the prefix type
	suffix = componentList[ 0 ].split( '.' )[ 1 ]
	componentPrefix = suffix[ :suffix.find( '[' ) ]

	prefixLen = len( componentPrefix ) + 1  #add one because there is always a "[" after the component str
	for face in componentList:
		mesh, idStr = face.split( '.' )
		idx = int( idStr[ prefixLen:-1 ] )

		try: componentDict[ mesh ].append( idx )
		except KeyError: componentDict[ mesh ] = [ idx ]

	return componentDict


def stampVolumeToJoint( joint, volume, amount=0.1 ):
	meshes = cmd.ls(cmd.listHistory(joint, f=True, interestLevel=2), type='mesh')
	assert meshes

	jointPos = Vector(cmd.xform(joint, q=True, ws=True, rp=True))
	vertsDict = findVertsInVolume(meshes, volume)
	for mesh, verts in vertsDict.iteritems():
		skinCluster = cmd.ls(cmd.listHistory(mesh), type='skinCluster')[0]
		for vert in verts:
			vertName = '%s.vtx[%s]' % (mesh, vert.id)
			weight = vert.weight
			#print weight, vertName
			#print cmd.skinPercent(skinCluster, vertName, q=True, t=joint, v=True)
			currentWeight = cmd.skinPercent(skinCluster, vertName, q=True, t=joint, v=True)
			currentWeight += weight * amount
			#cmd.skinPercent(skinCluster, vertName, t=joint, v=currentWeight)
			print vertName, currentWeight


@d_progress(t='clamping influence count', st='clamping vert influences to %d' % kMAX_INF_PER_VERT)
def clampVertInfluenceCount( geos=None ):
	'''
	'''
	global kMAX_INF_PER_VERT, kMIN_SKIN_WEIGHT_VALUE
	progressWindow = cmd.progressWindow
	skinPercent = cmd.skinPercent

	halfMin = kMIN_SKIN_WEIGHT_VALUE / 2.0

	if geos is None:
		geos = cmd.ls(sl=True)

	for geo in geos:
		skin = cmd.ls(cmd.listHistory(geo), type='skinCluster')[0]
		verts = cmd.ls(cmd.polyListComponentConversion(geo, toVertex=True), fl=True)

		inc = 100.0 / len( verts )
		progress = 0
		vertsFixed = []
		for vert in verts:
			progress += inc
			progressWindow(e=True, progress=progress)

			reapplyWeights = False
			weightList = skinPercent(skin, vert, ib=1e-5, q=True, value=True)

			if len(weightList) > kMAX_INF_PER_VERT:
				jointList = skinPercent(skin, vert, ib=halfMin, q=True, transform=None)
				sorted = zip(weightList, jointList)
				sorted.sort()

				#now clamp to the highest kMAX_INF_PER_VERT number of weights, and re-normalize
				sorted = sorted[ -kMAX_INF_PER_VERT: ]
				weightSum = sum( [ a for a, b in sorted ] )

				t_values = [ (b, a/weightSum) for a, b in sorted ]
				reapplyWeights = True

			else:
				for n, v in enumerate( weightList ):
					if v <= kMIN_SKIN_WEIGHT_VALUE:
						jointList = skinPercent( skin, vert, ib=halfMin, q=True, transform=None )
						t_values = [ (a, b) for a, b in zip( jointList, weightList ) if b > halfMin ]
						reapplyWeights = True
						break

			if reapplyWeights:
				js = [ a for a, b in t_values ]
				vs = renormalizeWithMinimumValue( [ b for a, b in t_values ] )
				t_values = zip( js, vs )

				skinPercent( skin, vert, tv=t_values )
				vertsFixed.append( vert )

		#turn on limiting in the skinCluster
		cmd.setAttr('%s.maxInfluences' % skin, kMAX_INF_PER_VERT)
		cmd.setAttr('%s.maintainMaxInfluences' % skin, 1)

		print 'fixed skin weights on %d verts' % len( vertsFixed )
		#print '\n'.join( vertsFixed )


def renormalizeWithMinimumValue( values, minValue=kMIN_SKIN_WEIGHT_VALUE ):
	minCount = sum( 1 for v in values if v <= minValue )
	toAlter = [ n for n, v in enumerate( values ) if v > minValue ]
	modValues = [ max( minValue, v ) for v in values ]

	toAlterSum = sum( [ values[ n ] for n in toAlter ] )
	for n in toAlter:
		modValues[ n ] /= toAlterSum

	modifier = 1.0035 + ( float( minCount ) * minValue )
	for n in toAlter:
		modValues[ n ] /= modifier

	return modValues


def getBoundsForJoint( joint ):
	'''
	returns bounding box data (as a 6-tuple: xmin, xmax, ymin etc...) for the geometry influenced by a given joint
	'''
	verts = jointVertsForMaya(joint, 0.01)
	Xs, Ys, Zs = [], [], []
	for v in verts:
		x, y, z = cmd.xform(v, q=True, ws=True, t=True)
		Xs.append(x)
		Ys.append(y)
		Zs.append(z)

	Xs.sort()
	Ys.sort()
	Zs.sort()

	try:
		return Xs[0], Xs[-1], Ys[0], Ys[-1], Zs[0], Zs[-1]
	except IndexError:
		drawSize = cmd.getAttr('%s.radius' % joint)
		drawSize /= 2
		return -drawSize, drawSize, -drawSize, drawSize, -drawSize, drawSize


def getAlignedBoundsForJoint( joint, threshold=0.65, onlyVisibleMeshes=True ):
	'''
	looks at the verts the given joint/s and determines a local space (local to the first joint
	in the list if multiple are given) bounding box of the verts, and positions the hitbox
	accordingly

	if onlyVisibleMeshes is True, then only meshes that are visible in the viewport will
	contribute to the bounds
	'''
	theJoint = joint
	verts = []

	#so this is just to deal with the input arg being a tuple, list or string.  you can pass in a list
	#of joint names and the verts affected just get accumulated into a list, and the resulting bound
	#should be the inclusive bounding box for the given joints
	if isinstance( joint, (tuple,list) ):
		theJoint = joint[0]
		for joint in joint:
			verts += jointVertsForMaya( joint, threshold, onlyVisibleMeshes )
	else:
		verts += jointVertsForMaya( joint, threshold, onlyVisibleMeshes )

	jointDag = apiExtensions.asMDagPath( theJoint )
	jointMatrix = jointDag.inclusiveMatrix()
	vJointPos = OpenMaya.MTransformationMatrix( jointMatrix ).rotatePivot( OpenMaya.MSpace.kWorld ) + OpenMaya.MTransformationMatrix( jointMatrix ).getTranslation( OpenMaya.MSpace.kWorld )
	vJointPos = Vector( [vJointPos.x, vJointPos.y, vJointPos.z] )
	vJointBasisX = OpenMaya.MVector(-1,0,0) * jointMatrix
	vJointBasisY = OpenMaya.MVector(0,-1,0) * jointMatrix
	vJointBasisZ = OpenMaya.MVector(0,0,-1) * jointMatrix

	bbox = OpenMaya.MBoundingBox()
	for vert in verts:
		#get the position relative to the joint in question
		vPos = Vector( xform(vert, query=True, ws=True, t=True) )
		vPos = vJointPos - vPos

		#now transform the joint relative position into the coordinate space of that joint
		#we do this so we can get the width, height and depth of the bounds of the verts
		#in the space oriented along the joint
		vPosInJointSpace = Vector( (vPos.x, vPos.y, vPos.z) )
		vPosInJointSpace = vPosInJointSpace.change_space( vJointBasisX, vJointBasisY, vJointBasisZ )
		bbox.expand( OpenMaya.MPoint( *vPosInJointSpace ) )

	minB, maxB = bbox.min(), bbox.max()

	return minB[0], minB[1], minB[2], maxB[0], maxB[1], maxB[2]


def getJointScale( joint ):
	'''
	basically just returns the average bounding box side length...  is useful to use as an approximation for a
	joint's "size"
	'''
	xmn, xmx, ymn, ymx, zmn, zmx = getBoundsForJoint(joint)
	x = xmx - xmn
	y = ymx - ymn
	z = zmx - zmn

	return (x + y + z) / 3


#end