import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx


AUTHOR = '-:macaroniKazoo:-'
VERSION = '1.0'
NODE_NAME = 'twister'
ID = OpenMaya.MTypeId( 0x43899 )


class twister( OpenMayaMPx.MPxNode ):
	aInWorldMatrixA = OpenMaya.MObject()
	aInWorldMatrixB = OpenMaya.MObject()
	aAxisA = OpenMaya.MObject()
	aAxisB = OpenMaya.MObject()
	aDivider = OpenMaya.MObject()
	aOutRotate = OpenMaya.MObject()
	aOutRotateX = OpenMaya.MObject()
	aOutRotateY = OpenMaya.MObject()
	aOutRotateZ = OpenMaya.MObject()
	def __init__( self ):
		OpenMayaMPx.MPxNode.__init__(self)
	def compute( self, plug, data ):
		if plug == self.aOutRotate or plug == self.aOutRotateX or plug == self.aOutRotateY or plug == self.aOutRotateZ:
			#get handles to the attributes
			hInWorldMatrixA = data.inputValue(self.aInWorldMatrixA)
			matWorldA = hInWorldMatrixA.asMatrix()
			matWorldAinv = matWorldA.inverse()

			hInWorldMatrixB = data.inputValue(self.aInWorldMatrixB)
			matWorldB = hInWorldMatrixB.asMatrix()

			hAxisA = data.inputValue(self.aAxisA)
			nAxisA = hAxisA.asShort()

			hAxisB = data.inputValue(self.aAxisB)
			nAxisB = hAxisB.asShort()

			hDivider = data.inputValue(self.aDivider)
			dDivider = hDivider.asDouble()

			#build the vectors to compare
			axes = OpenMaya.MVector(1,0,0),OpenMaya.MVector(0,1,0),OpenMaya.MVector(0,0,1)

			#any index above 2 is just one of the first 3 axes negated - so deal with it
			vVecA = OpenMaya.MVector( axes[nAxisA%3] )  #make a copy of the vectors
			vVecB = OpenMaya.MVector( axes[nAxisB%3] )
			if nAxisA > 2: vVecA *= -1
			if nAxisB > 2: vVecB *= -1

			#put the B vector into the space of inputA so we can meaningfully compare them to get an angle between
			vVecB *= matWorldB
			vVecB *= matWorldAinv

			#finally grab the rotation between them and push it out to outRotate
			qRotBetween = OpenMaya.MQuaternion(vVecA,vVecB,(1/dDivider))
			asEuler = qRotBetween.asEulerRotation()

			#grab the output attribute handles and set their values
			hOutRotateX = data.outputValue( self.aOutRotateX )
			hOutRotateY = data.outputValue( self.aOutRotateY )
			hOutRotateZ = data.outputValue( self.aOutRotateZ )

			hOutRotateX.setDouble( asEuler.x )
			hOutRotateY.setDouble( asEuler.y )
			hOutRotateZ.setDouble( asEuler.z )

			#mark all attributes as clean
			data.setClean(self.aOutRotate)
			data.setClean(self.aOutRotateX)
			data.setClean(self.aOutRotateY)
			data.setClean(self.aOutRotateZ)
		else:
			return OpenMaya.MStatus.kUnknownParameter

		return OpenMaya.MStatus.kSuccess


def initializePlugin( mObject ):
	mPlugin = OpenMayaMPx.MFnPlugin( mObject, AUTHOR, VERSION, "Any" )
	mPlugin.registerNode( NODE_NAME, ID, nodeCreator, nodeInitializer )


def uninitializePlugin( mObject ):
	plugin = OpenMayaMPx.MFnPlugin( mObject )
	plugin.deregisterNode( ID )


def nodeCreator():
	return OpenMayaMPx.asMPxPtr( twister() )


def nodeInitializer():
	nAttr = OpenMaya.MFnNumericAttribute()
	mAttr = OpenMaya.MFnMatrixAttribute()
	eAttr = OpenMaya.MFnEnumAttribute()
	cAttr = OpenMaya.MFnCompoundAttribute()

	twister.aInWorldMatrixA = mAttr.create( "inWorldMatrixA", "iwma" )
	twister.aInWorldMatrixB = mAttr.create( "inWorldMatrixB", "iwmb" )

	twister.aAxisA = eAttr.create("axisA", "axa", 0 )
	eAttr.setChannelBox(True)
	eAttr.setKeyable(True)
	eAttr.addField( "X", 0 )
	eAttr.addField( "Y", 1 )
	eAttr.addField( "Z", 2 )
	eAttr.addField( "-X", 3 )
	eAttr.addField( "-Y", 4 )
	eAttr.addField( "-Z", 5 )

	twister.aAxisB = eAttr.create("axisB", "axb", 0 )
	eAttr.setChannelBox(True)
	eAttr.setKeyable(True)
	eAttr.addField( "X", 0 )
	eAttr.addField( "Y", 1 )
	eAttr.addField( "Z", 2 )
	eAttr.addField( "-X", 3 )
	eAttr.addField( "-Y", 4 )
	eAttr.addField( "-Z", 5 )

	twister.aDivider = nAttr.create( "divider", "div", OpenMaya.MFnNumericData.kDouble, 1 )
	nAttr.setMin(0.001)
	nAttr.setChannelBox(True)
	nAttr.setKeyable(True)

	twister.aOutRotateX = nAttr.create( "outRotateX", "orx", OpenMaya.MFnNumericData.kDouble, 0.0 )
	twister.aOutRotateY = nAttr.create( "outRotateY", "ory", OpenMaya.MFnNumericData.kDouble, 0.0 )
	twister.aOutRotateZ = nAttr.create( "outRotateZ", "orz", OpenMaya.MFnNumericData.kDouble, 0.0 )
	twister.aOutRotate = cAttr.create( "outRotate", "or")
	cAttr.addChild( twister.aOutRotateX )
	cAttr.addChild( twister.aOutRotateY )
	cAttr.addChild( twister.aOutRotateZ )

	twister.addAttribute( twister.aInWorldMatrixA )
	twister.addAttribute( twister.aInWorldMatrixB )
	twister.addAttribute( twister.aAxisA )
	twister.addAttribute( twister.aAxisB )
	twister.addAttribute( twister.aDivider )
	twister.addAttribute( twister.aOutRotate )

	#setup dependency relationships
	twister.attributeAffects( twister.aInWorldMatrixA, twister.aOutRotate )
	twister.attributeAffects( twister.aInWorldMatrixB, twister.aOutRotate )
	twister.attributeAffects( twister.aDivider, twister.aOutRotate )
	twister.attributeAffects( twister.aAxisB, twister.aOutRotate )
	twister.attributeAffects( twister.aAxisB, twister.aOutRotate )