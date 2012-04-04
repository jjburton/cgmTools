
from rigPrim_ikFkBase import *
from rigPrim_stretchy import StretchRig


class IkFkArm(IkFkBase):
	__version__ = 3 + IkFkBase.__version__  #factor in the version of the ikfk sub rig part
	SKELETON_PRIM_ASSOC = ( SkeletonPart.GetNamedSubclass( 'Arm' ), )
	CONTROL_NAMES = 'control', 'fkBicep', 'fkElbow', 'fkWrist', 'poleControl', 'clavicle', 'allPurpose'

	def getFkControls( self ):
		return self.getControl( 'fkBicep' ), self.getControl( 'fkElbow' ), self.getControl( 'fkWrist' )
	def getIkHandle( self ):
		ikCons = listConnections( '%s.message' % self.getControl( 'fkBicep' ), s=False, type='ikHandle' )
		if ikCons:
			return ikCons[0]
	def _build( self, skeletonPart, translateClavicle=True, stretchy=True, **kw ):
		return self.doBuild( skeletonPart.bicep, skeletonPart.elbow, skeletonPart.wrist, skeletonPart.clavicle, translateClavicle, stretchy, **kw )
	def doBuild( self, bicep, elbow, wrist, clavicle=None, translateClavicle=True, stretchy=False, **kw ):
		getWristToWorldRotation( wrist, True )

		colour = self.getParityColour()
		wireColor = 14 if self.getParity() == Parity.LEFT else 13
		parentControl, rootControl = getParentAndRootControl( clavicle or bicep )

		#build the base controls
		self.buildBase( ARM_NAMING_SCHEME )

		#create variables for each control used
		ikHandle = self.ikHandle
		ikArmSpace, fkArmSpace = self.ikSpace, self.fkSpace
		fkControls = driverBicep, driverElbow, driverWrist = self.driverUpper, self.driverMid, self.driverLower
		elbowControl = self.poleControl

		#build the clavicle
		if clavicle:
			clavOffset = AX_Y.asVector() * getAutoOffsetAmount( clavicle, listRelatives( clavicle, pa=True ), AX_Y )
			clavControl = buildControl( 'clavicleControl%s' % self.getParity().asName(), PlaceDesc( bicep, clavicle, clavicle ), shapeDesc=ShapeDesc( 'sphere' ), scale=self.scale*1.25, offset=clavOffset, offsetSpace=SPACE_WORLD, colour=colour )
			clavControlOrient = getNodeParent( clavControl )

			parent( clavControlOrient, parentControl )
			parent( fkArmSpace, clavControl )
			if not translateClavicle:
				attrState( clavControl, 't', *LOCK_HIDE )
		else:
			clavControl = None
			parent( fkArmSpace, parentControl )

		#build space switching
		allPurposeObj = self.buildAllPurposeLocator( 'arm' )
		buildDefaultSpaceSwitching( bicep, elbowControl, **spaceSwitching.NO_ROTATION )
		buildDefaultSpaceSwitching( bicep, self.control, [ allPurposeObj ], [ 'All Purpose' ], True )
		buildDefaultSpaceSwitching( bicep, driverBicep, **spaceSwitching.NO_TRANSLATION )

		#make the limb stretchy?
		if stretchy:
			StretchRig.Create( self.getSkeletonPart(), self.control, fkControls, '%s.ikBlend' % ikHandle, parity=self.getParity() )

		controls = self.control, driverBicep, driverElbow, driverWrist, elbowControl, clavControl, allPurposeObj
		namedNodes = self.ikSpace, self.fkSpace, self.ikHandle, self.endOrient, self.lineNode

		return controls, namedNodes


class IkFkLeg(IkFkBase):
	__version__ = 2 + IkFkBase.__version__  #factor in the version of the ikfk sub rig part
	SKELETON_PRIM_ASSOC = ( SkeletonPart.GetNamedSubclass( 'Leg' ), )
	CONTROL_NAMES = 'control', 'fkThigh', 'fkKnee', 'fkAnkle', 'poleControl', 'allPurpose'

	def getFkControls( self ):
		return self.getControl( 'fkThigh' ), self.getControl( 'fkKnee' ), self.getControl( 'fkAnkle' )
	def getIkHandle( self ):
		ikCons = listConnections( '%s.message' % self.getControl( 'fkThigh' ), s=False, type='ikHandle' )
		if ikCons:
			return ikCons[0]
	def _build( self, skeletonPart, stretchy=True, **kw ):
		return self.doBuild( skeletonPart.thigh, skeletonPart.knee, skeletonPart.ankle, stretchy=stretchy, **kw )
	def doBuild( self, thigh, knee, ankle, stretchy=True, **kw ):
		partParent, rootControl = getParentAndRootControl( thigh )

		#first rotate the foot so its aligned to a world axis
		footCtrlRot = Vector( getAnkleToWorldRotation( str( ankle ), 'z', True ) )
		footCtrlRot = (0, -footCtrlRot.y, 0)

		#build the base controls
		self.buildBase( LEG_NAMING_SCHEME )

		#if the legs are parented to a root part - which is usually the case but not always - grab the hips and parent the fk control space to the hips
		hipsControl = partParent
		partParentRigPart = RigPart.InitFromItem( partParent )
		if isinstance( partParentRigPart.getSkeletonPart(), Root ):
			hipsControl = partParentRigPart.getControl( 'hips' )

		#if the part parent in a Root primitive, grab the hips control instead of the root gimbal - for the leg parts this is preferable
		parentRigPart = RigPart.InitFromItem( partParent )
		if isinstance( parentRigPart, Root ):
			partParent = parentRigPart.getControl( 'hips' )

		#create variables for each control used
		legControl = self.control
		legControlSpace = getNodeParent( legControl )

		ikLegSpace, fkLegSpace = self.ikSpace, self.fkSpace
		driverThigh, driverKnee, driverAnkle = self.driverUpper, self.driverMid, self.driverLower
		fkControls = driverThigh, driverKnee, driverAnkle

		kneeControl = self.poleControl
		kneeControlSpace = getNodeParent( kneeControl )
		parent( kneeControlSpace, partParent )

		toe = listRelatives( ankle, type='joint', pa=True ) or None
		toeTip = None

		if toe:
			toe = toe[0]

		#if the toe doesn't exist, build a temp one
		if not toe:
			toe = group( em=True )
			parent( toe, ankle, r=True )
			move( 0, -self.scale, self.scale, toe, r=True, ws=True )

		toeTip = self.getSkeletonPart().endPlacer
		if not toeTip:
			possibleTips = listRelatives( toe, type='joint', pa=True )
			if possibleTips:
				toeTip = possibleTips[ 0 ]

		#build the objects to control the foot
		suffix = self.getSuffix()
		footControlSpace = buildNullControl( "foot_controlSpace"+ suffix, ankle, parent=legControl )
		heelRoll = buildNullControl( "heel_roll_piv"+ suffix, ankle, offset=(0, 0, -self.scale), parent=footControlSpace )
		select( heelRoll )  #move command doesn't support object naming when specifying a single axis move, so we must selec the object first
		move( 0, 0, 0, rpr=True, y=True )

		if toeTip:
			toeRoll = buildNullControl( "leg_toe_roll_piv"+ suffix, toeTip, parent=heelRoll )
		else:
			toeRoll = buildNullControl( "leg_toe_roll_piv"+ suffix, toe, parent=heelRoll, offset=(0, 0, self.scale) )

		footBankL = buildNullControl( "bank_in_piv"+ suffix, toe, parent=toeRoll )
		footBankR = buildNullControl( "bank_out_piv"+ suffix, toe, parent=footBankL )
		footRollControl = buildNullControl( "roll_piv"+ suffix, toe, parent=footBankR )

		#move bank pivots to a good spot on the ground
		placers = self.getSkeletonPart().getPlacers()
		numPlacers = len( placers )
		if placers:
			toePos = Vector( xform( toe, q=True, ws=True, rp=True ) )
			if numPlacers >= 2:
				innerPlacer = Vector( xform( placers[1], q=True, ws=True, rp=True ) )
				move( innerPlacer[0], innerPlacer[1], innerPlacer[2], footBankL, a=True, ws=True, rpr=True )

			if numPlacers >= 3:
				outerPlacer = Vector( xform( placers[2], q=True, ws=True, rp=True ) )
				move( outerPlacer[0], outerPlacer[1], outerPlacer[2], footBankR, a=True, ws=True, rpr=True )

			if numPlacers >= 4:
				heelPlacer = Vector( xform( placers[3], q=True, ws=True, rp=True ) )
				move( heelPlacer[0], heelPlacer[1], heelPlacer[2], heelRoll, a=True, ws=True, rpr=True )


		#move the knee control so its inline with the leg
		rotate( footCtrlRot[0], footCtrlRot[1], footCtrlRot[2], kneeControlSpace, p=xform( thigh, q=True, ws=True, rp=True ), a=True, ws=True )
		makeIdentity( kneeControl, apply=True, t=True )

		#add attributes to the leg control, to control the pivots
		addAttr( legControl, ln='rollBall', at='double', min=0, max=10, k=True )
		addAttr( legControl, ln='rollToe', at='double', min=-10, max=10, k=True )
		addAttr( legControl, ln='twistFoot', at='double', min=-10, max=10, k=True )
		addAttr( legControl, ln='bank', at='double', min=-10, max=10, k=True )

		#replace the legControl as a target to the parent constraint on the endOrient transform so the ikHandle respects the foot slider controls
		footFinalPivot = buildNullControl( "final_piv"+ suffix, ankle, parent=footRollControl )
		delete( parentConstraint( footFinalPivot, self.ikHandle, mo=True ) )
		parent( self.ikHandle, footFinalPivot )
		replaceGivenConstraintTarget( self.endOrientSpaceConstraint, legControl, footFinalPivot )

		#build the SDK's to control the pivots
		setDrivenKeyframe( '%s.rx' % footRollControl, cd='%s.rollBall' % legControl, dv=0, v=0 )
		setDrivenKeyframe( '%s.rx' % footRollControl, cd='%s.rollBall' % legControl, dv=10, v=90 )
		setDrivenKeyframe( '%s.rx' % footRollControl, cd='%s.rollBall' % legControl, dv=-10, v=-90 )

		setDrivenKeyframe( '%s.rx' % toeRoll, cd='%s.rollToe' % legControl, dv=0, v=0 )
		setDrivenKeyframe( '%s.rx' % toeRoll, cd='%s.rollToe' % legControl, dv=10, v=90 )
		setDrivenKeyframe( '%s.rx' % toeRoll, cd='%s.rollToe' % legControl, dv=0, v=0 )
		setDrivenKeyframe( '%s.rx' % toeRoll, cd='%s.rollToe' % legControl, dv=-10, v=-90 )
		setDrivenKeyframe( '%s.ry' % toeRoll, cd='%s.twistFoot' % legControl, dv=-10, v=-90 )
		setDrivenKeyframe( '%s.ry' % toeRoll, cd='%s.twistFoot' % legControl, dv=10, v=90 )

		min = -90 if self.getParity() == Parity.LEFT else 90
		max = 90 if self.getParity() == Parity.LEFT else -90
		setDrivenKeyframe( '%s.rz' % footBankL, cd='%s.bank' % legControl, dv=0, v=0 )
		setDrivenKeyframe( '%s.rz' % footBankL, cd='%s.bank' % legControl, dv=10, v=max )
		setDrivenKeyframe( '%s.rz' % footBankR, cd='%s.bank' % legControl, dv=0, v=0 )
		setDrivenKeyframe( '%s.rz' % footBankR, cd='%s.bank' % legControl, dv=-10, v=min )

		#setup the toe if we have one
		if toe:
			toeSDK = buildControl( "toeSDK%s" % suffix, toe, shapeDesc=SHAPE_NULL, parent=footBankR, scale=self.scale, colour=self.getParityColour() )
			toeConstraint = parentConstraint( driverAnkle, toe, w=0, mo=True )[0]
			toeConstraintAttrs = listAttr( toeConstraint, ud=True )
			expression( s='%s.%s = %s.ikBlend;\n%s.%s = 1 - %s.ikBlend;' % (toeConstraint, toeConstraintAttrs[ 0 ], self.control,
			                                                                toeConstraint, toeConstraintAttrs[ 1 ], self.control), n='toe_parentingConstraintSwitch' )

			addAttr( legControl, ln='toe', at='double', min=-10, max=10, k=True )
			setDrivenKeyframe( '%s.r%s' % (toeSDK, ROT_AXIS.asCleanName()), cd='%s.toe' % legControl, dv=-10, v=90 )
			setDrivenKeyframe( '%s.r%s' % (toeSDK, ROT_AXIS.asCleanName()), cd='%s.toe' % legControl, dv=10, v=-90 )

		#build space switching
		parent( fkLegSpace, hipsControl )
		allPurposeObj = self.buildAllPurposeLocator( 'leg' )
		spaceSwitching.build( legControl, (self.getWorldControl(), hipsControl, rootControl, allPurposeObj), ('World', None, 'Root', 'All Purpose'), space=legControlSpace )
		spaceSwitching.build( kneeControl, (legControl, partParent, rootControl, self.getWorldControl()), ("Leg", None, "Root", "World"), **spaceSwitching.NO_ROTATION )
		spaceSwitching.build( driverThigh, (hipsControl, rootControl, self.getWorldControl()), (None, 'Root', 'World'), **spaceSwitching.NO_TRANSLATION )
		spaceSwitching.build( kneeControl, (self.getWorldControl(), hipsControl, rootControl), ('World', None, 'Root'), **spaceSwitching.NO_ROTATION )

		#make the limb stretchy
		if stretchy:
			StretchRig.Create( self.getSkeletonPart(), legControl, fkControls, '%s.ikBlend' % self.ikHandle, parity=self.getParity() )
			if objExists( '%s.elbowPos' % legControl ):
				renameAttr( '%s.elbowPos' % legControl, 'kneePos' )


		controls = legControl, driverThigh, driverKnee, driverAnkle, kneeControl, allPurposeObj
		namedNodes = self.ikSpace, self.fkSpace, self.ikHandle, self.endOrient, self.lineNode

		return controls, namedNodes


#end
