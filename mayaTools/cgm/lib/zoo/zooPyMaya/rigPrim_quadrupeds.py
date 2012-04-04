
from rigPrim_ikFkBase import *
from rigPrim_stretchy import StretchRig


class QuadrupedIkFkLeg(IkFkBase):
	__version__ = 0
	SKELETON_PRIM_ASSOC = ( SkeletonPart.GetNamedSubclass( 'QuadrupedFrontLeg' ), SkeletonPart.GetNamedSubclass( 'QuadrupedBackLeg' ) )
	CONTROL_NAMES = 'control', 'poleControl', 'clavicle'

	DISPLAY_NAME = 'Quadruped Leg'

	def _build( self, skeletonPart, **kw ):

		#this bit of zaniness is so we don't have to call the items by name, which makes it work with Arm or Leg skeleton primitives
		items = list( skeletonPart )[ :3 ]

		if len( skeletonPart ) == 4:
			items = list( skeletonPart )[ 1:4 ]
			items.append( skeletonPart[ 0 ] )

		return self.doBuild( *items, **kw )
	def doBuild( self, thigh, knee, ankle, clavicle, **kw ):
		idx = kw[ 'idx' ]
		scale = kw[ 'scale' ]

		parity = Parity( idx )
		parityMult = parity.asMultiplier()

		nameMod = kw.get( 'nameMod', 'front' )
		nameSuffix = '%s%s' % (nameMod.capitalize(), parity.asName())
		colour = self.getParityColour()

		#determine the root
		partParent, rootControl = getParentAndRootControl( clavicle )

		#build out the control for the clavicle
		clavCtrl = buildControl( 'quadClavicle%s' % nameSuffix,
			                     PlaceDesc( clavicle ),
			                     PivotModeDesc.BASE,
			                     ShapeDesc( 'cylinder', axis=-AIM_AXIS if parity else AIM_AXIS ),
			                     colour, scale=scale )

		clavCtrlSpace = getNodeParent( clavCtrl )
		setAttr( '%s.rotateOrder' % clavCtrl, 1 )

		cmd.parent( clavCtrlSpace, partParent )


		#build the leg rig primitive
		self.buildBase( LEG_NAMING_SCHEME )
		legCtrl = self.control
		legFkSpace = self.fkSpace

		parent( legFkSpace, clavCtrl )

		poleSpace = getNodeParent( self.poleControl )
		pointConstraint( legFkSpace, legCtrl, poleSpace )


		### SETUP CLAVICLE AIM ###
		dummyGrp = group( em=True )
		delete( pointConstraint( clavicle, dummyGrp ) )
		parent( dummyGrp, rootControl )

		aimVector = BONE_AIM_VECTOR * parityMult
		sideClavAxis = getObjectAxisInDirection( clavCtrlSpace, BONE_AIM_VECTOR ).asVector()
		sideCtrlAxis = getObjectAxisInDirection( legCtrl, BONE_AIM_VECTOR ).asVector()

		aim = aimConstraint( legCtrl, clavCtrlSpace, aimVector=BONE_AIM_VECTOR, upVector=sideClavAxis, worldUpVector=sideCtrlAxis, worldUpObject=legCtrl, worldUpType='objectrotation', mo=True )[ 0 ]
		aimNode = aimConstraint( dummyGrp, clavCtrlSpace, weight=0, aimVector=BONE_AIM_VECTOR )[ 0 ]

		revNode = createNode( 'reverse' )
		addAttr( clavCtrl, ln='autoMotion', at='float', min=0, max=1, dv=1 )
		setAttr( '%s.autoMotion' % clavCtrl, keyable=True )

		connectAttr( '%s.autoMotion' % clavCtrl, '%s.target[0].targetWeight' % aimNode, f=True )
		connectAttr( '%s.autoMotion' % clavCtrl, '%s.inputX' % revNode, f=True )
		connectAttr( '%s.outputX' % revNode, '%s.target[1].targetWeight' % aimNode, f=True )


		### HOOK UP A FADE FOR THE AIM OFFSET
		mt, measure, la, lb = buildMeasure( str( clavCtrlSpace ), str( legCtrl ) )
		maxLen = chainLength( clavicle, ankle )
		curLen = getAttr( '%s.distance' % measure )

		cmd.parent( la, rootControl )
		cmd.parent( mt, rootControl )

		for c in [ mt, la, lb ]:
			setAttr( '%s.v' % c, False )
			setAttr( '%s.v' % c, lock=True )

		controls = legCtrl, self.poleControl, clavCtrl

		return controls, ()


def duplicateChain( start, end ):
	chainNodes = getChain( start, end )

	dupeJoints = []
	for j in chainNodes:
		dupe = duplicate( j, rr=True )[0]
		children = listRelatives( dupe, pa=True )
		if children:
			delete( children )

		if dupeJoints:
			parent( dupe, dupeJoints[-1] )

		dupeJoints.append( dupe )

	return dupeJoints


class SatyrLeg(PrimaryRigPart, SwitchableMixin):
	__version__ = 0
	SKELETON_PRIM_ASSOC = ( SkeletonPart.GetNamedSubclass( 'SatyrLeg' ), )
	CONTROL_NAMES = 'control', 'poleControl', 'anklePoleControl'
	NAMED_NODE_NAMES = 'ikSpace', 'fkSpace', 'ikHandle', 'poleTrigger'

	DISPLAY_NAME = 'Satyr Leg Rig'

	def getFkJoints( self ):
		part = self.getSkeletonPart()

		return part[ :4 ]
	def getFkControls( self ):
		allControls = list( self )

		return allControls[ -4: ]
	@d_unifyUndo
	def switchToFk( self ):
		fkJoints = self.getFkJoints()
		fkControls = self.getFkControls()

		for j, c in zip( fkJoints, fkControls ):
			alignFast( c, j )

		control = self.getControl( 'control' )
		setAttr( '%s.ikBlend' % control, 0 )

		select( fkControls[-1] )
	@d_unifyUndo
	def switchToIk( self ):
		fkJoints = self.getFkJoints()
		control = self.getControl( 'control' )
		poleControl = self.getControl( 'poleControl' )
		anklePoleControl = self.getControl( 'anklePoleControl' )

		polePos = findPolePosition( fkJoints[2], fkJoints[1], fkJoints[0] )
		move( polePos[0], polePos[1], polePos[2], poleControl, ws=True, a=True, rpr=True )

		alignFast( control, fkJoints[-1] )
		alignFast( anklePoleControl, fkJoints[-2] )

		setAttr( '%s.ikBlend' % control, 1 )
		select( control )
	def _build( self, skeletonPart, stretchy=True, **kw ):
		scale = kw[ 'scale' ]

		parity = self.getParity()
		parityMult = parity.asMultiplier()

		nameMod = kw.get( 'nameMod', 'front' )
		nameSuffix = '_%s%s' % (nameMod.capitalize(), parity.asName())

		colour = self.getParityColour()

		originalJoints = originalThighJoint, originalKneeJoint, originalAnkleJoint, originalToeJoint = skeletonPart[:4]
		getWristToWorldRotation( originalToeJoint, True )

		#create a duplicate chain for the ik leg - later we create another chain for fk and constrain the original joints between them for ik/fk switching
		ikJoints = ikThighJoint, ikKneeJoint, ikAnkleJoint, ikToeJoint = duplicateChain( originalThighJoint, originalToeJoint )

		### IK CHAIN SETUP

		#determine the root
		partParent, rootControl = getParentAndRootControl( ikThighJoint )

		parent( ikThighJoint, partParent )
		setAttr( '%s.v' % ikThighJoint, 0 )

		ikHandle = cmd.ikHandle( fs=1, sj=ikThighJoint, ee=ikAnkleJoint, solver='ikRPsolver' )[ 0 ]
		footCtrl = buildControl( 'Foot%s' % nameSuffix,
		                         #PlaceDesc( ikToeJoint, PlaceDesc.WORLD ),
		                         ikToeJoint,
		                         PivotModeDesc.MID,
			                     ShapeDesc( 'cube', axis=-AIM_AXIS if parity else AIM_AXIS ),
			                     colour, scale=scale )

		footCtrlSpace = getNodeParent( footCtrl )
		setAttr( '%s.rotateOrder' % footCtrl, 1 )
		setAttr( '%s.v' % ikHandle, 0 )
		attrState( ikHandle, 'v', *LOCK_HIDE )

		#build the pivots for the foot roll/rock attributes
		placers = skeletonPart.getPlacers()
		if placers:
			footRock_fwd = buildNullControl( 'footRock_forward_null', placers[0], parent=footCtrlSpace )
			footRock_back = buildNullControl( 'footRock_backward_null', placers[1], parent=footRock_fwd )
			footRoll_inner = buildNullControl( 'footRoll_inner_null', placers[2], parent=footRock_back )
			footRoll_outer = buildNullControl( 'footRoll_outer_null', placers[3], parent=footRoll_inner )
		else:
			footRock_fwd = buildNullControl( 'footRock_forward_null', ikToeJoint, parent=footCtrlSpace )
			footRock_back = buildNullControl( 'footRock_backward_null', ikToeJoint, parent=footCtrlSpace )
			footRoll_inner = buildNullControl( 'footRoll_inner_null', ikToeJoint, parent=footCtrlSpace )
			footRoll_outer = buildNullControl( 'footRoll_outer_null', ikToeJoint, parent=footCtrlSpace )
			toePos = xform( ikToeJoint, q=True, ws=True, rp=True )
			moveIncrement = scale / 2
			move( 0, -toePos[1], moveIncrement, footRock_fwd, r=True, ws=True )
			move( 0, -toePos[1], -moveIncrement, footRock_back, r=True, ws=True )
			move( -moveIncrement * parityMult, -toePos[1], 0, footRoll_inner, r=True, ws=True )
			move( moveIncrement * parityMult, -toePos[1], 0, footRoll_outer, r=True, ws=True )
			cmd.parent( footRock_back, footRock_fwd )
			cmd.parent( footRoll_inner, footRock_back )
			cmd.parent( footRoll_outer, footRoll_inner )

		cmd.parent( footCtrl, footRoll_outer )
		makeIdentity( footCtrl, a=True, t=True )

		addAttr( footCtrl, ln='footRock', at='double', dv=0, min=-10, max=10 )
		attrState( footCtrl, 'footRock', *NORMAL )

		setDrivenKeyframe( '%s.ry' % footRock_fwd, cd='%s.footRock' % footCtrl, dv=0, v=0 )
		setDrivenKeyframe( '%s.ry' % footRock_fwd, cd='%s.footRock' % footCtrl, dv=10, v=90 )
		setDrivenKeyframe( '%s.ry' % footRock_back, cd='%s.footRock' % footCtrl, dv=0, v=0 )
		setDrivenKeyframe( '%s.ry' % footRock_back, cd='%s.footRock' % footCtrl, dv=-10, v=-90 )

		addAttr( footCtrl, ln='bank', at='double', dv=0, min=-10, max=10 )
		attrState( footCtrl, 'bank', *NORMAL )

		setDrivenKeyframe( '%s.rx' % footRoll_inner, cd='%s.bank' % footCtrl, dv=0, v=0 )
		setDrivenKeyframe( '%s.rx' % footRoll_inner, cd='%s.bank' % footCtrl, dv=10, v=-90 )
		setDrivenKeyframe( '%s.rx' % footRoll_outer, cd='%s.bank' % footCtrl, dv=0, v=0 )
		setDrivenKeyframe( '%s.rx' % footRoll_outer, cd='%s.bank' % footCtrl, dv=-10, v=90 )

		#setup the auto ankle
		grpA = buildControl( 'ankle_auto_null', PlaceDesc( ikToeJoint, ikAnkleJoint ), shapeDesc=SHAPE_NULL, constrain=False, parent=footCtrl )
		grpB = buildAlignedNull( ikAnkleJoint, 'ankle_orientation_null', parent=grpA )

		orientConstraint( grpB, ikAnkleJoint )
		for ax in AXES:
			delete( '%s.t%s' % (ikToeJoint, ax), icn=True )

		cmd.parent( ikHandle, grpA )
		cmd.parent( footCtrlSpace, self.getWorldControl() )

		grpASpace = getNodeParent( grpA )
		grpAAutoNull = buildAlignedNull( PlaceDesc( ikToeJoint, ikAnkleJoint ), '%sauto_on_ankle_null%s' % (nameMod, nameSuffix), parent=footCtrl )
		grpAAutoOffNull = buildAlignedNull( PlaceDesc( ikToeJoint, ikAnkleJoint ), '%sauto_off_ankle_null%s' % (nameMod, nameSuffix), parent=footCtrl )
		grpA_knee_aimVector = betweenVector( grpAAutoNull, ikKneeJoint )
		grpA_knee_aimAxis = getObjectAxisInDirection( grpAAutoNull, grpA_knee_aimVector )
		grpA_knee_upAxis = getObjectAxisInDirection( grpAAutoNull, (1, 0, 0) )
		grpA_knee_worldAxis = getObjectAxisInDirection( footCtrl, (1, 0, 0) )
		aimConstraint( ikThighJoint, grpAAutoNull, mo=True, aim=grpA_knee_aimAxis.asVector(), u=grpA_knee_upAxis.asVector(), wu=grpA_knee_worldAxis.asVector(), wuo=footCtrl, wut='objectrotation' )

		autoAimConstraint = orientConstraint( grpAAutoNull, grpAAutoOffNull, grpASpace )[0]
		addAttr( footCtrl, ln='autoAnkle', at='double', dv=1, min=0, max=1 )
		attrState( footCtrl, 'autoAnkle', *NORMAL )

		cAttrs = listAttr( autoAimConstraint, ud=True )
		connectAttr( '%s.autoAnkle' % footCtrl, '%s.%s' % (autoAimConstraint, cAttrs[0]), f=True )
		connectAttrReverse( '%s.autoAnkle' % footCtrl, '%s.%s' % (autoAimConstraint, cAttrs[1]), f=True )

		poleCtrl = buildControl( 'Pole%s' % nameSuffix,
		                         PlaceDesc( ikKneeJoint, PlaceDesc.WORLD ), PivotModeDesc.MID,
		                         shapeDesc=ShapeDesc( 'sphere', axis=-AIM_AXIS if parity else AIM_AXIS ),
		                         colour=colour, constrain=False, scale=scale, parent=self.getPartsNode() )

		poleCtrlSpace = getNodeParent( poleCtrl )
		polePos = findPolePosition( ikAnkleJoint )
		move( polePos[0], polePos[1], polePos[2], poleCtrlSpace, ws=True, rpr=True, a=True )
		pointConstraint( ikThighJoint, footCtrl, poleCtrlSpace, mo=True )

		poleVectorConstraint( poleCtrl, ikHandle )

		#build the ankle aim control - its acts kinda like a secondary pole vector
		anklePoleControl = buildControl( 'Ankle%s' % nameSuffix, ikAnkleJoint, shapeDesc=ShapeDesc( 'sphere' ), colour=colour, scale=scale, constrain=False, parent=grpASpace )

		ankleAimVector = betweenVector( grpA, anklePoleControl )
		ankleAimAxis = getObjectAxisInDirection( grpA, ankleAimVector )
		ankleUpAxis = getObjectAxisInDirection( grpA, (1, 0, 0) )
		ankleWorldUpAxis = getObjectAxisInDirection( anklePoleControl, (1, 0, 0) )
		aimConstraint( anklePoleControl, grpA, aim=ankleAimAxis.asVector(), u=ankleUpAxis.asVector(), wu=ankleWorldUpAxis.asVector(), wuo=anklePoleControl, wut='objectrotation' )

		### FK CHAIN SETUP
		fkThighControl = buildControl( 'fkThigh%s' % nameSuffix, originalThighJoint, PivotModeDesc.MID, 'sphere', colour, False, scale=scale, parent=partParent )
		fkKneeControl = buildControl( 'fkKnee%s' % nameSuffix, originalKneeJoint, PivotModeDesc.MID, 'sphere', colour, False, scale=scale, parent=fkThighControl )
		fkAnkleControl = buildControl( 'fkAnkle%s' % nameSuffix, originalAnkleJoint, PivotModeDesc.MID, 'sphere', colour, False, scale=scale, parent=fkKneeControl )
		fkToeControl = buildControl( 'fkToe%s' % nameSuffix, originalToeJoint, PivotModeDesc.MID, 'sphere', colour, False, scale=scale, parent=fkAnkleControl )
		fkControls = fkThighControl, fkKneeControl, fkAnkleControl, fkToeControl

		setItemRigControl( originalThighJoint, fkThighControl )
		setItemRigControl( originalKneeJoint, fkKneeControl )
		setItemRigControl( originalAnkleJoint, fkAnkleControl )

		addAttr( footCtrl, ln='ikBlend', at='float', min=0, max=1, dv=1, keyable=True )
		for ikJ, fkC, orgJ in zip( ikJoints, fkControls, originalJoints ):
			constraintNode = parentConstraint( ikJ, orgJ, w=1, mo=True )[0]
			constraintNode = parentConstraint( fkC, orgJ, w=0, mo=True )[0]
			ikAttr, fkAttr = listAttr( constraintNode, ud=True )
			connectAttr( '%s.ikBlend' % footCtrl, '%s.%s' % (constraintNode, ikAttr) )
			connectAttrReverse( '%s.ikBlend' % footCtrl, '%s.%s' % (constraintNode, fkAttr) )

		ikControls = footCtrl, poleCtrl, anklePoleControl
		setupIkFkVisibilityConditions( '%s.ikBlend' % footCtrl, ikControls, fkControls )

		#now we need to setup right mouse button menus for ik/fk switching
		footTrigger = Trigger( footCtrl )
		footTrigger.createMenu( 'switch to FK', '''python( "from zooPyMaya import rigPrimitives; rigPrimitives.RigPart.InitFromItem('#').switchToFk()" )''' )

		for c in fkControls:
			t = Trigger( c )
			t.createMenu( 'switch to IK', '''python( "from zooPyMaya import rigPrimitives; rigPrimitives.RigPart.InitFromItem('#').switchToIk()" )''' )

		#setup stretch as appropriate
		if stretchy:
			StretchRig.Create( self._skeletonPart, footCtrl, (ikThighJoint, ikKneeJoint, ikAnkleJoint, ikToeJoint), '%s.ikBlend' % ikHandle, parity=parity, connectEndJoint=True )
			for ax in CHANNELS:
				delete( '%s.t%s' % (ikToeJoint, ax), icn=True )

			pointConstraint( footCtrl, ikToeJoint )

		buildDefaultSpaceSwitching( originalThighJoint, footCtrl, reverseHierarchy=True, space=footCtrlSpace )
		buildDefaultSpaceSwitching( originalThighJoint, fkThighControl )
		buildDefaultSpaceSwitching( originalToeJoint, fkToeControl, **spaceSwitching.NO_ROTATION )

		controls = ikControls + fkControls
		namedNodes = None, None, ikHandle, None

		return controls, namedNodes


#end
