
from zooPy.vectors import Matrix, Vector, Axis
from zooPy import vectors

import maya.cmds as cmd
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

from zooPyMaya import apiExtensions

from maya.OpenMaya import MObject, MFnMatrixAttribute, MFnCompoundAttribute, MFnMessageAttribute, MGlobal, \
     MFnEnumAttribute, MFnNumericAttribute, MFnNumericData, MFnUnitAttribute, MFnDependencyNode, \
     MPoint, MVector, MSyntax, MArgDatabase

from maya.OpenMayaMPx import MPxNode

MPxCommand = OpenMayaMPx.MPxCommand
kUnknownParameter = OpenMaya.kUnknownParameter

#this list simply maps the rotation orders as found on the rotateOrder enum attribute, to the matrix methods responsible for converting a rotation matrix to euler values
mayaRotationOrders = Matrix.ToEulerXYZ, Matrix.ToEulerYZX, Matrix.ToEulerZXY, Matrix.ToEulerXZY, Matrix.ToEulerYXZ, Matrix.ToEulerZYX
assert len( mayaRotationOrders ) == len( set( mayaRotationOrders ) )  #sanity check


class MirrorNode(MPxNode):

	NODE_ID = OpenMaya.MTypeId( 0x00115940 )
	NODE_TYPE_NAME = "rotationMirror"

	inWorldMatrix = MObject()  #this is the input world matrix; the one we want mirrored
	inParentMatrixInv = MObject()  #this is the input parent inverse matrix. ie the parent inverse matrix of the transform we want mirrored

	mirrorAxis = MObject()  #which axis are we mirroring on?
	mirrorTranslation = MObject()  #boolean to determine whether translation mirroring happens in world space or local space

	targetJointOrient = MObject()  #this is the joint orient attribute for the target joint - so it can be compensated for
	targetJointOrientX = MObject()
	targetJointOrientY = MObject()
	targetJointOrientZ = MObject()

	targetParentMatrixInv = MObject()  #this is the parent inverse matrix for the target transform
	targetRotationOrder = MObject()  #the rotation order on the target

	outTranslate = MObject()  #the output translation
	outTranslateX = MObject()
	outTranslateY = MObject()
	outTranslateZ = MObject()

	outRotate = MObject()  #the output rotation
	outRotateX = MObject()
	outRotateY = MObject()
	outRotateZ = MObject()

	MIRROR_MODES = M_COPY, M_INVERT, M_MIRROR = range( 3 )
	MIRROR_MODE_NAMES = 'copy', 'invert', 'mirror'
	MIRROR_DEFAULT = M_MIRROR

	@classmethod
	def Creator( cls ):
		return OpenMayaMPx.asMPxPtr( cls() )
	@classmethod
	def Init( cls ):
		attrInWorldMatrix = MFnMatrixAttribute()
		attrInParentMatrixInv = MFnMatrixAttribute()

		attrMirrorAxis = MFnEnumAttribute()
		attrMirrorTranslation = MFnEnumAttribute()

		attrTargetParentMatrixInv = MFnMatrixAttribute()
		targetRotationOrder = MFnNumericAttribute()

		attrOutTranslate = MFnNumericAttribute()
		attrOutTranslateX = MFnUnitAttribute()
		attrOutTranslateY = MFnUnitAttribute()
		attrOutTranslateZ = MFnUnitAttribute()

		attrOutRotate = MFnNumericAttribute()
		attrOutRotateX = MFnUnitAttribute()
		attrOutRotateY = MFnUnitAttribute()
		attrOutRotateZ = MFnUnitAttribute()

		attrTargetJointOrient = MFnNumericAttribute()
		attrTargetJointOrientX = MFnUnitAttribute()
		attrTargetJointOrientY = MFnUnitAttribute()
		attrTargetJointOrientZ = MFnUnitAttribute()

		#create the world matrix
		cls.inWorldMatrix = attrInWorldMatrix.create( "inWorldMatrix", "iwm" )

		cls.addAttribute( cls.inWorldMatrix )


		#create the local matrix
		cls.inParentMatrixInv = attrInWorldMatrix.create( "inParentInverseMatrix", "ipmi" )

		cls.addAttribute( cls.inParentMatrixInv )


		#create the mirror axis
		cls.mirrorAxis = attrMirrorAxis.create( "mirrorAxis", "m" )
		attrMirrorAxis.addField( 'x', 0 )
		attrMirrorAxis.addField( 'y', 1 )
		attrMirrorAxis.addField( 'z', 2 )
		attrMirrorAxis.setDefault( 'x' )
		attrMirrorAxis.setKeyable( False )
		attrMirrorAxis.setChannelBox( True )

		cls.addAttribute( cls.mirrorAxis )


		#create the mirror axis
		cls.mirrorTranslation = attrMirrorTranslation.create( "mirrorTranslation", "mt" )
		for modeName, modeIdx in zip( cls.MIRROR_MODE_NAMES, cls.MIRROR_MODES ):
			attrMirrorTranslation.addField( modeName, modeIdx )

		attrMirrorTranslation.setDefault( cls.MIRROR_DEFAULT )
		attrMirrorTranslation.setKeyable( False )
		attrMirrorTranslation.setChannelBox( True )

		cls.addAttribute( cls.mirrorTranslation )


		#create the out world matrix inverse
		cls.targetParentMatrixInv = attrTargetParentMatrixInv.create( "targetParentInverseMatrix", "owm" )
		cls.addAttribute( cls.targetParentMatrixInv )


		#create the target rotation order attribute
		cls.targetRotationOrder = targetRotationOrder.create( "targetRotationOrder", "troo", MFnNumericData.kInt )
		cls.addAttribute( cls.targetRotationOrder )


		#create the joint orient compensation attributes
		cls.targetJointOrientX = attrTargetJointOrientX.create( "targetJointOrientX", "tjox", MFnUnitAttribute.kAngle )
		cls.targetJointOrientY = attrTargetJointOrientY.create( "targetJointOrientY", "tjoy", MFnUnitAttribute.kAngle )
		cls.targetJointOrientZ = attrTargetJointOrientZ.create( "targetJointOrientZ", "tjoz", MFnUnitAttribute.kAngle )
		cls.targetJointOrient = attrTargetJointOrient.create( "targetJointOrient", "tjo", cls.targetJointOrientX, cls.targetJointOrientY, cls.targetJointOrientZ )
		cls.addAttribute( cls.targetJointOrient )


		#create the out translate attributes
		cls.outTranslateX = attrOutTranslateX.create( "outTranslateX", "otx", MFnUnitAttribute.kDistance )
		cls.outTranslateY = attrOutTranslateY.create( "outTranslateY", "oty", MFnUnitAttribute.kDistance )
		cls.outTranslateZ = attrOutTranslateZ.create( "outTranslateZ", "otz", MFnUnitAttribute.kDistance )
		cls.outTranslate = attrOutTranslate.create( "outTranslate", "ot", cls.outTranslateX, cls.outTranslateY, cls.outTranslateZ )
		cls.addAttribute( cls.outTranslate )


		#create the out rotation attributes
		cls.outRotateX = attrOutRotateX.create( "outRotateX", "orx", MFnUnitAttribute.kAngle )
		cls.outRotateY = attrOutRotateY.create( "outRotateY", "ory", MFnUnitAttribute.kAngle )
		cls.outRotateZ = attrOutRotateZ.create( "outRotateZ", "orz", MFnUnitAttribute.kAngle )
		cls.outRotate = attrOutRotate.create( "outRotate", "or", cls.outRotateX, cls.outRotateY, cls.outRotateZ )
		cls.addAttribute( cls.outRotate )


		#setup attribute dependency relationships
		cls.attributeAffects( cls.inWorldMatrix, cls.outTranslate )
		cls.attributeAffects( cls.inWorldMatrix, cls.outRotate )

		cls.attributeAffects( cls.inParentMatrixInv, cls.outTranslate )
		cls.attributeAffects( cls.inParentMatrixInv, cls.outRotate )

		cls.attributeAffects( cls.mirrorAxis, cls.outTranslate )
		cls.attributeAffects( cls.mirrorAxis, cls.outRotate )

		cls.attributeAffects( cls.mirrorTranslation, cls.outTranslate )
		cls.attributeAffects( cls.mirrorTranslation, cls.outRotate )

		cls.attributeAffects( cls.targetParentMatrixInv, cls.outTranslate )
		cls.attributeAffects( cls.targetParentMatrixInv, cls.outRotate )

		cls.attributeAffects( cls.targetRotationOrder, cls.outTranslate )
		cls.attributeAffects( cls.targetRotationOrder, cls.outRotate )

		cls.attributeAffects( cls.targetJointOrient, cls.outRotate )

	def compute( self, plug, dataBlock ):
		dh_mirrorTranslation = dataBlock.inputValue( self.mirrorTranslation )
		mirrorTranslation = Axis( dh_mirrorTranslation.asShort() )

		inWorldMatrix = dataBlock.inputValue( self.inWorldMatrix ).asMatrix()
		inParentInvMatrix = dataBlock.inputValue( self.inParentMatrixInv ).asMatrix()

		dh_mirrorAxis = dataBlock.inputValue( self.mirrorAxis )
		axis = Axis( dh_mirrorAxis.asShort() )

		### DEAL WITH ROTATION AND POSITION SEPARATELY ###
		R, S = inWorldMatrix.asPy( 3 ).decompose()  #this gets just the 3x3 rotation and scale matrices
		x, y, z = R  #extract basis vectors

		#mirror the rotation axes and construct the mirrored rotation matrix
		idxA, idxB = axis.otherAxes()
		x[ idxA ] = -x[ idxA ]
		x[ idxB ] = -x[ idxB ]

		y[ idxA ] = -y[ idxA ]
		y[ idxB ] = -y[ idxB ]

		z[ idxA ] = -z[ idxA ]
		z[ idxB ] = -z[ idxB ]

		#factor scale back into the matrix
		mirroredMatrix = Matrix( x + y + z, 3 ) * S
		mirroredMatrix = mirroredMatrix.expand( 4 )

		#now put the rotation matrix in the space of the target object
		dh_targetParentMatrixInv = dataBlock.inputValue( self.targetParentMatrixInv )
		tgtParentMatrixInv = dh_targetParentMatrixInv.asMatrix()
		matInv = tgtParentMatrixInv.asPy()

		#put the rotation in the space of the target's parent
		mirroredMatrix = mirroredMatrix * matInv

		#if there is a joint orient, make sure to compensate for it
		tgtJoX = dataBlock.inputValue( self.targetJointOrientX ).asDouble()
		tgtJoY = dataBlock.inputValue( self.targetJointOrientY ).asDouble()
		tgtJoZ = dataBlock.inputValue( self.targetJointOrientZ ).asDouble()

		jo = Matrix.FromEulerXYZ( tgtJoX, tgtJoY, tgtJoZ )
		joInv = jo.inverse()
		joInv = joInv.expand( 4 )
		mirroredMatrix = mirroredMatrix * joInv

		#grab the rotation order of the target
		rotOrderIdx = dataBlock.inputValue( self.targetRotationOrder ).asInt()

		#grab euler values
		R, S = mirroredMatrix.decompose()  #we need to decompose again to extract euler angles...
		eulerXYZ = outX, outY, outZ = mayaRotationOrders[ rotOrderIdx ]( R )  #R.ToEulerYZX()

		dh_outRX = dataBlock.outputValue( self.outRotateX )
		dh_outRY = dataBlock.outputValue( self.outRotateY )
		dh_outRZ = dataBlock.outputValue( self.outRotateZ )

		#set the rotation
		dh_outRX.setDouble( outX )
		dh_outRY.setDouble( outY )
		dh_outRZ.setDouble( outZ )

		dataBlock.setClean( plug )


		### NOW DEAL WITH POSITION ###

		#set the position
		if mirrorTranslation == self.M_COPY:
			inLocalMatrix = inWorldMatrix * inParentInvMatrix
			pos = MPoint( inLocalMatrix(3,0), inLocalMatrix(3,1), inLocalMatrix(3,2) )
		elif mirrorTranslation == self.M_INVERT:
			inLocalMatrix = inWorldMatrix * inParentInvMatrix
			pos = MPoint( -inLocalMatrix(3,0), -inLocalMatrix(3,1), -inLocalMatrix(3,2) )
		elif mirrorTranslation == self.M_MIRROR:
			pos = MPoint( inWorldMatrix(3,0), inWorldMatrix(3,1), inWorldMatrix(3,2) )
			pos = [ pos.x, pos.y, pos.z ]
			pos[ axis ] = -pos[ axis ]
			pos = MPoint( *pos )
			pos = pos * tgtParentMatrixInv

		else:
			return

		dh_outTX = dataBlock.outputValue( self.outTranslateX )
		dh_outTY = dataBlock.outputValue( self.outTranslateY )
		dh_outTZ = dataBlock.outputValue( self.outTranslateZ )

		dh_outTX.setDouble( pos[0] )
		dh_outTY.setDouble( pos[1] )
		dh_outTZ.setDouble( pos[2] )


class ControlPairNode(MPxNode):
	'''
	is used by the poseSym tool for storing control pair relationships
	'''

	NODE_ID = OpenMaya.MTypeId( 0x00115941 )
	NODE_TYPE_NAME = "controlPair"

	controlA = MObject()
	controlB = MObject()

	axis = MObject()  #this is the axis which things get mirrored across
	flipAxes = MObject()

	neverDoT = MObject()  #if this is true then translation won't get mirrored/swapped
	neverDoR = MObject()  #if this is true then rotation won't get mirrored/swapped
	neverDoOther = MObject()  #if this is true then other keyable attributes won't get mirrored/swapped

	worldSpace = MObject()  #if this is true mirroring is done in world space - otherwise local spaces

	#these are the values for the flip axes
	FLIP_AXES = (), (vectors.AX_X, vectors.AX_Y), (vectors.AX_X, vectors.AX_Z), (vectors.AX_Y, vectors.AX_Z)

	@classmethod
	def Creator( cls ):
		return OpenMayaMPx.asMPxPtr( cls() )
	@classmethod
	def Init( cls ):
		attrMsg = MFnMessageAttribute()

		cls.controlA = attrMsg.create( "controlA", "ca" )
		cls.controlB = attrMsg.create( "controlB", "cb" )
		cls.addAttribute( cls.controlA )
		cls.addAttribute( cls.controlB )

		attrEnum = MFnEnumAttribute()
		cls.axis = attrEnum.create( "axis", "ax" )
		attrEnum.addField( 'x', 0 )
		attrEnum.addField( 'y', 1 )
		attrEnum.addField( 'z', 2 )
		attrEnum.setDefault( 'x' )
		attrEnum.setKeyable( False )
		attrEnum.setChannelBox( True )

		cls.addAttribute( cls.axis )

		cls.axis = attrEnum.create( "flipAxes", "flax" )
		for n, thisAxes in enumerate( cls.FLIP_AXES ):
			if thisAxes:
				enumStr = ''.join( [ ax.asName() for ax in thisAxes ] )
			else:
				enumStr = 'none'

			attrEnum.addField( enumStr, n )

		attrEnum.setKeyable( False )
		attrEnum.setChannelBox( True )

		cls.addAttribute( cls.axis )

		numAttr = MFnNumericAttribute()
		cls.neverDoT = numAttr.create( "neverDoT", "nvt", MFnNumericData.kBoolean )
		cls.neverDoR = numAttr.create( "neverDoR", "nvr", MFnNumericData.kBoolean )
		cls.neverDoOther = numAttr.create( "neverDoOther", "nvo", MFnNumericData.kBoolean )

		cls.addAttribute( cls.neverDoT )
		cls.addAttribute( cls.neverDoR )
		cls.addAttribute( cls.neverDoOther )

		cls.worldSpace = numAttr.create( "worldSpace", "ws", MFnNumericData.kBoolean, True )
		cls.addAttribute( cls.worldSpace )


class CreateMirrorNode(MPxCommand):
	CMD_NAME = 'rotationMirror'
	_ARG_SPEC = [ ('-h', '-help', MSyntax.kNoArg, 'prints help'),
	              ('-ax', '-axis', MSyntax.kString, 'the axis to mirror across (defaults to x)'),
	              ('-m', '-translationMode', MSyntax.kString, 'the mode in which translation is mirrored - %s (defaults to %s)' % (' '.join( MirrorNode.MIRROR_MODE_NAMES ), MirrorNode.MIRROR_MODE_NAMES[ MirrorNode.MIRROR_DEFAULT ])),
	              ('-d', '-dummy', MSyntax.kNoArg, "builds the node but doesn't hook it up to the target - this can be useful if you want to query what would be mirrored transform"),
	              #('-s', '-space', MSyntax.kString, 'which space to mirror in - world or local (defaults to world)') ]
	              ]

	kFlagHelp = _ARG_SPEC[ 0 ][ 0 ]
	kFlagAxis = _ARG_SPEC[ 1 ][ 0 ]
	kFlagMode = _ARG_SPEC[ 2 ][ 0 ]
	kFlagDummy = _ARG_SPEC[ 3 ][ 0 ]

	@classmethod
	def SyntaxCreator( cls ):
		syntax = OpenMaya.MSyntax()

		for shortFlag, longFlag, syntaxType, h in cls.IterArgSpec():
			syntax.addFlag( shortFlag, longFlag, syntaxType )

		syntax.useSelectionAsDefault( True )
		syntax.setObjectType( MSyntax.kSelectionList, 1, 3 )

		syntax.enableQuery( True )
		syntax.enableEdit( True )

		return syntax
	@classmethod
	def Creator( cls ):
		return OpenMayaMPx.asMPxPtr( cls() )
	@classmethod
	def IterArgSpec( cls ):
		for data in cls._ARG_SPEC:
			if len( data ) != 4:
				yield data + ('<no help available>',)
			else:
				yield data

	def grabArgDb( self, mArgs ):
		try:
			argData = MArgDatabase( self.syntax(), mArgs )
		except RuntimeError:
			return True, None

		if argData.isFlagSet( self.kFlagHelp ):
			self.printHelp()
			return True, None

		return False, argData
	def printHelp( self ):
		longestFlag = 5
		for shortFlag, longFlag, syntaxType, h in self.IterArgSpec():
			longestFlag = max( longestFlag, len(longFlag) )

		self.displayInfo( '%s - USAGE' % self.CMD_NAME )

		printStr = '*%5s  %'+ str( longestFlag ) +'s: %s'
		for shortFlag, longFlag, syntaxType, h in self.IterArgSpec():
			self.displayInfo( printStr % (shortFlag, longFlag, h) )
	def doIt( self, mArgs ):
		ret, argData = self.grabArgDb( mArgs )
		if ret:
			return

		sel = OpenMaya.MSelectionList()
		argData.getObjects( sel )

		objs = []
		for n in range( sel.length() ):
			obj = MObject()
			sel.getDependNode( n, obj )
			objs.append( obj )

		#
		if argData.isQuery():
			rotNode = objs[0]

			if argData.isFlagSet( self.kFlagAxis ):
				self.setResult( cmd.getAttr( '%s.mirrorAxis' % rotNode ) )

			elif argData.isFlagSet( self.kFlagMode ):
				self.setResult( cmd.getAttr( '%s.mirrorTranslation' % rotNode ) )

			return

		#if we're in edit mode, find the node
		elif argData.isEdit():
			rotNode = objs[0]

		#otherwise we're in creation mode - so build the node and connect things up
		else:
			obj, tgt = objs

			#is dummy mode set?
			isDummyMode = argData.isFlagSet( self.kFlagDummy ) or argData.isFlagSet( self.kFlagDummy )

			#see if there is already a node connected
			existing = cmd.listConnections( '%s.t' % tgt, '%s.r' % tgt, type=MirrorNode.NODE_TYPE_NAME )
			if existing:
				self.displayWarning( "There is a %s node already connected - use edit mode!" % MirrorNode.NODE_TYPE_NAME )
				self.setResult( existing[ 0 ] )

				return
			else:
				rotNode = cmd.createNode( 'rotationMirror' )
				cmd.connectAttr( '%s.worldMatrix' % obj, '%s.inWorldMatrix' % rotNode )
				cmd.connectAttr( '%s.parentInverseMatrix' % obj, '%s.inParentInverseMatrix' % rotNode )

				cmd.connectAttr( '%s.parentInverseMatrix' % tgt, '%s.targetParentInverseMatrix' % rotNode )

				joAttrpath = '%s.jo' % tgt
				if cmd.objExists( joAttrpath ):
					cmd.connectAttr( joAttrpath, '%s.targetJointOrient' % rotNode )

				cmd.connectAttr( '%s.rotateOrder' % tgt, '%s.targetRotationOrder' % rotNode )

				if not isDummyMode:
					cmd.connectAttr( '%s.outTranslate' % rotNode, '%s.t' % tgt )
					cmd.connectAttr( '%s.outRotate' % rotNode, '%s.r' % tgt )

				cmd.select( obj )

		#set the result to the node created...
		self.setResult( rotNode )

		#set any attributes passed in from the command-line
		if argData.isFlagSet( self.kFlagAxis ):
			axisInt = Axis.FromName( argData.flagArgumentString( self.kFlagAxis, 0 ) )
			cmd.setAttr( '%s.mirrorAxis' % rotNode, axisInt )

		if argData.isFlagSet( self.kFlagMode ):
			modeStr = argData.flagArgumentString( self.kFlagMode, 0 )
			modeIdx = list( MirrorNode.MIRROR_MODE_NAMES ).index( modeStr )
			cmd.setAttr( '%s.mirrorTranslation' % rotNode, modeIdx )
	def undoIt( self ):
		pass
	def isUndoable( self ):
		return True


def initializePlugin( mobject ):
	mplugin = OpenMayaMPx.MFnPlugin( mobject, 'macaronikazoo', '1' )

	try:
		mplugin.registerNode( MirrorNode.NODE_TYPE_NAME, MirrorNode.NODE_ID, MirrorNode.Creator, MirrorNode.Init )
		mplugin.registerNode( ControlPairNode.NODE_TYPE_NAME, ControlPairNode.NODE_ID, ControlPairNode.Creator, ControlPairNode.Init )

		mplugin.registerCommand( CreateMirrorNode.CMD_NAME, CreateMirrorNode.Creator, CreateMirrorNode.SyntaxCreator )
		mplugin.registerCommand( CreateMirrorNode.CMD_NAME.lower(), CreateMirrorNode.Creator, CreateMirrorNode.SyntaxCreator )
	except:
		MGlobal.displayError( "Failed to load zooMirror plugin:" )
		raise


def uninitializePlugin( mobject ):
	mplugin = OpenMayaMPx.MFnPlugin( mobject )

	try:
		mplugin.deregisterNode( MirrorNode.NODE_ID )
		mplugin.deregisterNode( ControlPairNode.NODE_ID )

		mplugin.deregisterCommand( CreateMirrorNode.CMD_NAME )
		mplugin.deregisterCommand( CreateMirrorNode.CMD_NAME.lower() )
	except:
		MGlobal.displayError( "Failed to unload zooMirror plugin:" )
		raise


#end
