
from maya.cmds import *

from zooPy.misc import removeDupes
from zooPy.binarySearchTree import BinarySearchTree
from zooPy import presets

from skinWeightsBase import *
from mayaDecorators import d_unifyUndo, d_progress, d_showWaitCursor
from melUtils import mel, printWarningStr

import maya.cmds as cmd
import apiExtensions

iterParents = apiExtensions.iterParents
VertSkinWeight = MayaVertSkinWeight


def getAllParents( obj ):
	allParents = []
	parent = [ obj ]
	while parent is not None:
		allParents.append( parent[ 0 ] )
		parent = cmd.listRelatives( parent, p=True, pa=True )

	return allParents[ 1: ]


def getDefaultPath():
	scenePath = cmd.file(q=True, sn=True)
	if not scenePath:
		return DEFAULT_PATH

	scenePath = Path( scenePath )
	scenePath = scenePath.setExtension( EXTENSION )

	return scenePath


kAPPEND = 0
kREPLACE = 1
@d_showWaitCursor
def saveWeights( geos, filepath=None ):
	start = time.clock()
	miscData = {}

	#if filepath is None, then generate a default filepath based on the location of the file
	if filepath is None:
		filepath = getDefaultPath()
	else: filepath = Path(filepath)

	geoAndData = {}
	skinPercent = cmd.skinPercent
	xform = cmd.xform

	#define teh data we're gathering
	masterJointList = []
	weightData = []

	#data gathering time!
	rigidBindObjects = []
	for geo in geos:
		skinClusters = cmd.ls( cmd.listHistory( geo ), type='skinCluster' )
		if len( skinClusters ) > 1:
			printWarningStr( "more than one skinCluster found on %s" % geo )
			continue

		#so the geo isn't skinned in the traditional way - check to see if it is parented to a joint.  if so,
		#stuff it into the rigid bind list to be dealt with outside this loop, and continue
		if not skinClusters:
			dealtWith = False
			for p in iterParents( geo ):
				if cmd.nodeType( p ) == 'joint':
					rigidBindObjects.append( (geo, p) )
					masterJointList.append( p )
					masterJointList = removeDupes( masterJointList )
					dealtWith = True
					break

			if not dealtWith:
				msg = "cannot find a skinCluster for %s" % geo
				printWarningStr( msg )

			continue

		skinCluster = skinClusters[ 0 ]
		masterJointList += cmd.skinCluster( skinCluster, q=True, inf=True )
		masterJointList = removeDupes( masterJointList )

		verts = cmd.ls(cmd.polyListComponentConversion(geo, toVertex=True), fl=True)
		for idx, vert in enumerate(verts):
			jointList = skinPercent(skinCluster, vert, ib=1e-4, q=True, transform=None)
			weightList = skinPercent(skinCluster, vert, ib=1e-4, q=True, value=True)
			if jointList is None:
				raise SkinWeightException("I can't find any joints - sorry.  do you have any post skin cluster history???")

			pos = xform(vert, q=True, ws=True, t=True)
			vertData = VertSkinWeight( pos )
			vertData.populate( geo, idx, [ masterJointList.index( j ) for j in jointList ], weightList )
			weightData.append( vertData )


	#deal with rigid bind objects
	for geo, j in rigidBindObjects:

		verts = cmd.ls( cmd.polyListComponentConversion(geo, toVertex=True), fl=True )
		for idx, vert in enumerate( verts ):
			jIdx = masterJointList.index( j )

			pos = xform( vert, q=True, ws=True, t=True )
			vertData = VertSkinWeight( pos )
			vertData.populate( geo, idx, [jIdx], [1] )
			weightData.append( vertData )


	#sort the weightData by ascending x values so we can search faster
	weightData.sort()

	#turn the masterJointList into a dict keyed by index
	joints = {}
	for n, j in enumerate( masterJointList ):
		joints[ n ] = j

	#generate joint hierarchy data - so if joints are missing on load we can find the best match
	jointHierarchies = {}
	for n, j in joints.iteritems():
		jointHierarchies[ n ] = getAllParents( j )

	toWrite = miscData, joints, jointHierarchies, weightData

	filepath = Path( filepath )
	filepath.pickle( toWrite)
	print 'Weights Successfully Saved to %s: time taken %.02f seconds' % (filepath, time.clock()-start)

	return filepath


@d_progress(t='initializing...', status='initializing...', isInterruptable=True)
@d_unifyUndo
def loadWeights( objects, filepath=None, usePosition=True, tolerance=TOL, axisMult=None, swapParity=True, averageVerts=True, doPreview=False, meshNameRemapDict=None, jointNameRemapDict=None ):
	'''
	loads weights back on to a model given a file
	'''

	#nothing to do...
	if not objects:
		print 'No objects given...'
		return

	if filepath is None:
		filepath = getDefaultPath()

	if not filepath.exists():
		print 'File does not exist %s' % filepath
		return

	start = time.clock()


	#setup the mappings
	VertSkinWeight.MESH_NAME_REMAP_DICT = meshNameRemapDict
	VertSkinWeight.JOINT_NAME_REMAP_DICT = jointNameRemapDict


	#cache heavily access method objects as locals...
	skinPercent = cmd.skinPercent
	progressWindow = cmd.progressWindow
	xform = cmd.xform


	#now get a list of all weight files that are listed on the given objects - and
	#then load them one by one and apply them to the appropriate objects
	objItemsDict = {}
	for obj in objects:
		items = []  #this holds the vert list passed in IF any
		if obj.find('.') != -1:
			items = [obj]
			obj = obj.split('.')[0]

		try: objItemsDict[obj].extend( items )
		except KeyError: objItemsDict[obj] = items


	numItems = len(objItemsDict)
	curItem = 1
	progressWindow(e=True, title='loading weights from file %d items' % numItems)


	#load the data from the file
	miscData, joints, jointHierarchies, weightData = Path( filepath ).unpickle()


	#build the search tree
	tree = BinarySearchTree( weightData )
	findMethod = tree.getWithin
	findMethodKw = { 'tolerance': tolerance }

	if averageVerts:
		findMethod = tree.getWithinRatio
		findMethodKw = { 'ratio': tolerance }


	#remap joint names in the saved file to joint names that are in the scene - they may be namespace differences...
	missingJoints = set()
	for n, j in joints.iteritems():
		if not cmd.objExists(j):
			#see if the joint with the same leaf name exists in the scene
			idxA = j.rfind(':')
			idxB = j.rfind('|')
			idx = max(idxA, idxB)
			if idx != -1:
				leafName = j[idx + 1:]
				if objExists( leafName ):
					joints[n] = leafName
				else:
					search = cmd.ls('%s*' % leafName, r=True, type='joint')
					if search:
						joints[n] = search[0]
						print '%s remapped to %s' % (j, search[0])


	#now that we've remapped joint names, we go through the joints again and remap missing joints to their nearest parent
	#joint in the scene - NOTE: this needs to be done after the name remap so that parent joint names have also been remapped
	for n, j in joints.iteritems():
		if not cmd.objExists(j):
			dealtWith = False
			for jp in jointHierarchies[n]:
				if cmd.objExists( jp ):
					joints[n] = jp
					dealtWith = True
					break

			if dealtWith:
				print '%s remapped to %s' % (j, jp)
				continue

			missingJoints.add(n)

	#now remove them from the list
	[ joints.pop(n) for n in missingJoints ]


	#axisMults can be used to alter the positions of verts saved in the weightData array - this is mainly useful for applying
	#weights to a mirrored version of a mesh - so weights can be stored on meshA, meshA duplicated to meshB, and then the
	#saved weights can be applied to meshB by specifying an axisMult=(-1,1,1) OR axisMult=(-1,)
	if axisMult is not None:
		for data in weightData:
			for n, mult in enumerate(axisMult): data[n] *= mult

		#we need to re-sort the weightData as the multiplication could have potentially reversed things...  i could probably
		#be a bit smarter about when to re-order, but its not a huge hit...  so, meh
		weightData = sorted(weightData)

		#using axisMult for mirroring also often means you want to swap parity tokens on joint names - if so, do that now.
		#parity needs to be swapped in both joints and jointHierarchies
		if swapParity:
			for joint, target in joints.iteritems():
				joints[joint] = str( names.Name(target).swap_parity() )
			for joint, parents in jointHierarchies.iteritems():
				jointHierarchies[joint] = [str( names.Name(p).swap_parity() ) for p in parents]


	for geo, items in objItemsDict.iteritems():
		#if the geo is None, then check for data in the verts arg - the user may just want weights
		#loaded on a specific list of verts - we can get the geo name from those verts
		skinCluster = ''
		verts = cmd.ls(cmd.polyListComponentConversion(items if items else geo, toVertex=True), fl=True)


		#do we have a skinCluster on the geo already?  if not, build one
		skinCluster = cmd.ls(cmd.listHistory(geo), type='skinCluster')
		if not skinCluster:
			skinCluster = cmd.skinCluster(geo,joints.values())[0]
			verts = cmd.ls(cmd.polyListComponentConversion(geo, toVertex=True), fl=True)
		else: skinCluster = skinCluster[0]


		#if we're using position, the restore weights path is quite different
		vertJointWeightData = []
		if usePosition:
			progressWindow( e=True, status='searching by position: %s (%d/%d)' % (geo, curItem, numItems), maxValue=len( verts ) )

			vCount = -1
			for vert in verts:
				vCount += 1
				pos = Vector( xform(vert, q=True, ws=True, t=True) )
				foundVerts = findMethod( pos, **findMethodKw )


				#accumulate found verts
				jointWeightDict = {}
				for v in foundVerts:
					for joint, weight in zip( v.joints, v.weights ):
						actualJoint = joints[ joint ]
						weight += jointWeightDict.get( actualJoint, 0 )
						jointWeightDict[ actualJoint ] = weight


				#normalize the weights
				weightSum = float( sum( jointWeightDict.values() ) )
				if weightSum != 1:
					for joint, weight in jointWeightDict.iteritems():
						jointWeightDict[ joint ] = weight / weightSum


				#append the data
				vertJointWeightData.append( (vert, jointWeightDict.items()) )


				#deal with the progress window - this isn't done EVERY vert because its kinda slow...
				if vCount % 50 == 0:
					progressWindow( e=True, progress=vCount )

					#bail if we've been asked to cancel
					if progressWindow( q=True, isCancelled=True ):
						progressWindow( ep=True )
						return

			progressWindow( e=True, status='maya is setting skin weights...' )
			setSkinWeights( skinCluster, vertJointWeightData )

		#otherwise simply restore by id
		else:
			progressWindow( e=True, status='searching by vert name: %s (%d/%d)' % (geo, curItem, numItems), maxValue=len( verts ) )

			#rearrange the weightData structure so its ordered by vertex name
			weightDataById = {}
			[ weightDataById.setdefault(i.getVertName(), (i.joints, i.weights)) for i in weightData ]

			for vert in verts:
				#progressWindow(edit=True, progress=cur / num * 100.0)
				#if progressWindow(q=True, isCancelled=True):
					#progressWindow(ep=True)
					#return

				#cur += 1
				try:
					jointList, weightList = weightDataById[vert]
				except KeyError:
					#in this case, the vert doesn't exist in teh file...
					print '### no point found for %s' % vert
					continue
				else:
					jointList = [ joints[ j ] for j in jointList ]
					jointsAndWeights = zip(jointList, weightList)
					skinPercent(skinCluster, vert, tv=jointsAndWeights)

		#remove unused influences from the skin cluster
		cmd.skinCluster( skinCluster, edit=True, removeUnusedInfluence=True )
		curItem += 1

	end = time.clock()
	print 'time for weight load %.02f secs' % (end-start)


from maya.OpenMayaAnim import MFnSkinCluster
from maya.OpenMaya import MIntArray, MDagPathArray

@d_unifyUndo
def setSkinWeights( skinCluster, vertJointWeightData ):
	'''
	vertJointWeightData is a list of 2-tuples containing the vertex component name, and a list of 2-tuples
	containing the joint name and weight.  ie it looks like this:
	[ ('someMesh.vtx[0]', [('joint1', 0.25), 'joint2', 0.75)]),
	  ('someMesh.vtx[1]', [('joint1', 0.2), 'joint2', 0.7, 'joint3', 0.1)]),
	  ... ]
	'''

	#convert the vertex component names into vertex indices
	idxJointWeight = []
	for vert, jointsAndWeights in vertJointWeightData:
		idx = int( vert[ vert.rindex( '[' )+1:-1 ] )
		idxJointWeight.append( (idx, jointsAndWeights) )

	#get an MObject for the skin cluster node
	skinCluster = apiExtensions.asMObject( skinCluster )
	skinFn = MFnSkinCluster( skinCluster )

	#construct a dict mapping joint names to joint indices
	jApiIndices = {}
	_tmp = MDagPathArray()
	skinFn.influenceObjects( _tmp )
	for n in range( _tmp.length() ):
		jApiIndices[ str( _tmp[n].node() ) ] = skinFn.indexForInfluenceObject( _tmp[n] )

	weightListP = skinFn.findPlug( "weightList" )
	weightListObj = weightListP.attribute()
	weightsP = skinFn.findPlug( "weights" )

	tmpIntArray = MIntArray()
	baseFmtStr = str( skinCluster ) +'.weightList[%d]'  #pre build this string: fewer string ops == faster-ness!

	for vertIdx, jointsAndWeights in idxJointWeight:

		#we need to use the api to query the physical indices used
		weightsP.selectAncestorLogicalIndex( vertIdx, weightListObj )
		weightsP.getExistingArrayAttributeIndices( tmpIntArray )

		weightFmtStr = baseFmtStr % vertIdx +'.weights[%d]'

		#clear out any existing skin data - and awesomely we cannot do this with the api - so we need to use a weird ass mel command
		for n in range( tmpIntArray.length() ):
			removeMultiInstance( weightFmtStr % tmpIntArray[n] )

		#at this point using the api or mel to set the data is a moot point...  we have the strings already so just use mel
		for joint, weight in jointsAndWeights:
			if weight:
				try:
					infIdx = jApiIndices[ joint ]
				except KeyError:
					try:
						infIdx = jApiIndices[ joint.split( '|' )[0] ]
					except KeyError: continue

				setAttr( weightFmtStr % infIdx, weight )


def mirrorWeightsOnSelected( tolerance=TOL ):
	selObjs = cmd.ls(sl=True, o=True)

	#so first we need to grab the geo to save weights for - we save geo for all objects which have
	#verts selected
	saveWeights( selObjs, Path('%TEMP%/tmp.weights'), mode=kREPLACE )
	loadWeights( cmd.ls(sl=True), Path( '%TEMP%/tmp.weights' ), True, 2, (-1,), True )


def autoSkinToVolumeMesh( mesh, skeletonMeshRoot ):
	'''
	given a mesh and the root node for a hierarchy mesh volumes, this function will create
	a skeleton with the same hierarchy and skin the mesh to this skeleton using the mesh
	volumes to determine skin weights
	'''

	#grab a list of meshes under the hierarchy - we need to grab this geo, parent it to a skeleton and transfer defacto weighting to the given mesh
	volumes = listRelatives( skeletonMeshRoot, ad=True, type='mesh', pa=True )

	#now generate the skeleton
	transforms = removeDupes( listRelatives( volumes, p=True, type='transform', pa=True ) or [] )
	jointRemap = {}
	for t in transforms:
		select( cl=True )
		jName = '%s_joint' % t
		if objExists( jName ):
			jName += '#'

		j = joint( n=jName )
		jointRemap[ t ] = j

	#now do parenting
	for t, j in jointRemap.iteritems():
		tParent = listRelatives( t, p=True, pa=True )
		if tParent:
			tParent = tParent[0]
			jParent = jointRemap.get( tParent, None )
		else:
			jParent = None

		if jParent is not None:
			parent( j, jParent )

	#now do positioning
	for t in apiExtensions.sortByHierarchy( transforms ):
		j = jointRemap[ t ]
		pos = xform( t, q=True, ws=True, rp=True )
		move( pos[0], pos[1], pos[2], j, ws=True, rpr=True )

	#duplicate the geometry and parent the geo to the joints in the skeleton we just created - store the duplicates so we can delete them later
	dupes = []
	for t, j in jointRemap.iteritems():
		dupe = apiExtensions.asMObject( duplicate( t, returnRootsOnly=True, renameChildren=True )[0] )
		children = listRelatives( dupe, type='transform', pa=True ) or []
		if children:
			delete( children )

		parent( dupe, j )
		dupes.append( dupe )

	f = saveWeights( map( str, dupes ) )

	loadWeights( [mesh], f, usePosition=True, tolerance=0.5, averageVerts=True, jointNameRemapDict=jointRemap )

	delete( dupes )

	return jointRemap


def transferSkinning( sourceMesh, targetMesh ):
	sourceSkinCluster = mel.findRelatedSkinCluster( sourceMesh )
	if not sourceSkinCluster:
		raise SkeletonError( "Cannot find a skin cluster on %s" % sourceMesh )

	#if there isn't a skin cluster already, create one
	targetSkinCluster = mel.findRelatedSkinCluster( targetMesh )
	if not targetSkinCluster:
		influences = skinCluster( sourceSkinCluster, q=True, inf=True )
		targetSkinCluster = skinCluster( targetMesh, influences, toSelectedBones=True )[0]

	copySkinWeights( sourceSkin=sourceSkinCluster, destinationSkin=targetSkinCluster, noMirror=True, surfaceAssociation='closestPoint', smooth=True )

	return targetSkinCluster


#end
