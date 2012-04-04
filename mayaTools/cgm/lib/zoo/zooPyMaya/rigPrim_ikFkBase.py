
from zooPy.typeFactories import interfaceTypeFactory
from baseRigPrimitive import *
from apiExtensions import cmpNodes

ARM_NAMING_SCHEME = 'arm', 'bicep', 'elbow', 'wrist'
LEG_NAMING_SCHEME = 'leg', 'thigh', 'knee', 'ankle'


class SwitchableMixin(object):
	'''
	NOTE: we can't make this an interface class because rig part classes already have a pre-defined
	metaclass...  :(
	'''
	def __notimplemented( self ):
		raise NotImplemented( "This baseclass method hasn't been implemented on the %s class" % type( self ).__name__ )
	def switchToFk( self, key=False ):
		'''
		should implement the logic to switch this chain from IK to FK
		'''
		self.__notimplemented()
	def switchToIk( self, key=False, _isBatchMode=False ):
		'''
		should implement the logic to switch this chain from FK to IK
		'''
		self.__notimplemented()


def setupIkFkVisibilityConditions( ikBlendAttrpath, ikControls, fkControls ):
	ikControl = ikBlendAttrpath.split( '.' )[0]
	visCondFk = createNode( 'condition' )
	visCondFk = rename( visCondFk, '%s_fkVis#' % ikControl )

	visCondIk = createNode( 'condition' )
	visCondIk = rename( visCondIk, '%s_ikVis#' % ikControl )

	connectAttr( ikBlendAttrpath, '%s.firstTerm' % visCondFk )
	connectAttr( ikBlendAttrpath, '%s.firstTerm' % visCondIk )
	setAttr( '%s.secondTerm' % visCondFk, 1 )
	setAttr( '%s.secondTerm' % visCondIk, 0 )
	setAttr( '%s.operation' % visCondFk, 3 )  #this is the >= operator
	setAttr( '%s.operation' % visCondIk, 5 )  #this is the <= operator

	for c in fkControls:
		connectAttr( '%s.outColorR' % visCondFk, '%s.v' % c )

	for c in ikControls:
		connectAttr( '%s.outColorR' % visCondIk, '%s.v' % c )


class IkFkBase(PrimaryRigPart, SwitchableMixin):
	'''
	super class functionality for biped limb rigs - legs, arms and even some quadruped rigs inherit
	from this class
	'''
	NAMED_NODE_NAMES = 'ikSpace', 'fkSpace', 'ikHandle', 'endOrient', 'poleTrigger'

	def buildBase( self, nameScheme=ARM_NAMING_SCHEME, alignEnd=False ):
		self.nameScheme = nameScheme
		self.alignEnd = alignEnd

		self.bicep, self.elbow, self.wrist = bicep, elbow, wrist = self.getSkeletonPart().getIkFkItems()
		colour = self.getParityColour()

		suffix = self.getSuffix()

		#build the fk controls
		self.fkSpace = buildAlignedNull( bicep, "fk_%sSpace%s" % (nameScheme[ 0 ], suffix) )
		self.driverUpper = buildControl( "fk_%sControl%s" % (nameScheme[ 1 ], suffix), bicep, PivotModeDesc.MID, shapeDesc=ShapeDesc( 'sphere' ), colour=colour, asJoint=True, oriented=False, scale=self.scale, parent=self.fkSpace )
		self.driverMid = buildControl( "fk_%sControl%s" % (nameScheme[ 2 ], suffix), elbow, PivotModeDesc.MID, shapeDesc=ShapeDesc( 'sphere' ), colour=colour, asJoint=True, oriented=False, scale=self.scale, parent=self.driverUpper )
		self.driverLower = buildControl( "fk_%sControl%s" % (nameScheme[ 3 ], suffix), PlaceDesc( wrist, wrist if alignEnd else None ), shapeDesc=ShapeDesc( 'sphere' ), colour=colour, asJoint=True, oriented=False, constrain=False, scale=self.scale, parent=self.driverMid )
		self.fkControls = self.driverUpper, self.driverMid, self.driverLower
		attrState( self.fkControls, ('t', 'radi'), *LOCK_HIDE )

		#build the ik controls
		self.ikSpace = buildAlignedNull( self.wrist, "ik_%sSpace%s" % (self.nameScheme[ 0 ], suffix), parent=self.getWorldControl() )
		self.ikHandle = asMObject( cmd.ikHandle( fs=1, sj=self.driverUpper, ee=self.driverLower, solver='ikRPsolver' )[0] )
		self.control = limbControl = buildControl( '%sControl%s' % (self.nameScheme[ 0 ], suffix), PlaceDesc( self.wrist, self.wrist if self.alignEnd else None ), shapeDesc=ShapeDesc( 'cube' ), colour=colour, scale=self.scale, constrain=False, parent=self.ikSpace )

		rename( self.ikHandle, '%sIkHandle%s' % (self.nameScheme[0], suffix) )
		xform( self.control, p=True, rotateOrder='yzx' )
		setAttr( '%s.snapEnable' % self.ikHandle, False )
		setAttr( '%s.v' % self.ikHandle, False )

		addAttr( self.control, ln='ikBlend', shortName='ikb', dv=1, min=0, max=1, at='double' )
		setAttr( '%s.ikBlend' % self.control, keyable=True )
		connectAttr( '%s.ikBlend' % self.control, '%s.ikBlend' % self.ikHandle )

		attrState( self.ikHandle, 'v', *LOCK_HIDE )
		parent( self.ikHandle, self.getPartsNode() )
		parentConstraint( self.control, self.ikHandle )

		#build the pole control
		polePos = rigUtils.findPolePosition( self.driverLower, self.driverMid, self.driverUpper, 5 )
		self.poleControl = buildControl( "%s_poleControl%s" % (self.nameScheme[ 0 ], suffix), PlaceDesc( self.elbow, PlaceDesc.WORLD ), shapeDesc=ShapeDesc( 'sphere', None ), colour=colour, constrain=False, parent=self.getWorldControl(), scale=self.scale*0.5 )
		self.poleControlSpace = getNodeParent( self.poleControl )
		attrState( self.poleControlSpace, 'v', lock=False, show=True )

		move( polePos[0], polePos[1], polePos[2], self.poleControlSpace, a=True, ws=True, rpr=True )
		move( polePos[0], polePos[1], polePos[2], self.poleControl, a=True, ws=True, rpr=True )
		makeIdentity( self.poleControlSpace, a=True, t=True )
		setAttr( '%s.v' % self.poleControl, True )

		poleVectorConstraint( self.poleControl, self.ikHandle )

		#build the pole selection trigger
		self.lineNode = buildControl( "%s_poleSelectionTrigger%s" % (self.nameScheme[ 0 ], suffix), shapeDesc=ShapeDesc( 'sphere', None ), colour=ColourDesc( 'darkblue' ), scale=self.scale, constrain=False, oriented=False, parent=self.ikSpace )
		self.lineStart, self.lineEnd, self.lineShape = buildAnnotation( self.lineNode )

		parent( self.lineStart, self.poleControl )
		delete( pointConstraint( self.poleControl, self.lineStart ) )
		pointConstraint( self.elbow, self.lineNode )
		attrState( self.lineNode, ('t', 'r'), *LOCK_HIDE )

		setAttr( '%s.template' % self.lineStart, 1 )  #make the actual line unselectable

		#setup constraints to the wrist - it is handled differently because it needs to blend between the ik and fk chains (the other controls are handled by maya)
		self.endOrientParent = buildAlignedNull( self.wrist, "%s_follow%s_space" % (self.nameScheme[ 3 ], suffix), parent=self.getPartsNode() )
		self.endOrient = buildAlignedNull( self.wrist, "%s_follow%s" % (self.nameScheme[ 3 ], suffix), parent=self.endOrientParent )

		pointConstraint( self.driverLower, self.wrist )
		orientConstraint( self.endOrient, self.wrist, mo=True )
		setItemRigControl( self.wrist, self.endOrient )
		setNiceName( self.endOrient, 'Fk %s' % self.nameScheme[3] )
		self.endOrientSpaceConstraint = parentConstraint( self.control, self.endOrientParent, weight=0, mo=True )[ 0 ]
		self.endOrientSpaceConstraint = parentConstraint( self.driverLower, self.endOrientParent, weight=0, mo=True )[ 0 ]

		#constraints to drive the "wrist follow" mode
		self.endOrientConstraint = parentConstraint( self.endOrientParent, self.endOrient )[0]
		self.endOrientConstraint = parentConstraint( self.driverLower, self.endOrient, mo=True )[0]

		addAttr( self.control, ln='orientToIk', at='double', min=0, max=1, dv=1 )
		attrState( self.control, 'orientToIk', keyable=True, show=True )

		endOrientAttrs = listAttr( self.endOrientConstraint, ud=True )
		expression( s='%s.%s = %s.orientToIk;\n%s.%s = 1 - %s.orientToIk;' % (self.endOrientConstraint, endOrientAttrs[0], self.control, self.endOrientConstraint, endOrientAttrs[1], self.control), n='endOrientConstraint_on_off' )

		endOrientSpaceAttrs = listAttr( self.endOrientSpaceConstraint, ud=True )
		expression( s='%s.%s = %s.ikBlend;\n%s.%s = 1 - %s.ikBlend;' % (self.endOrientSpaceConstraint, endOrientSpaceAttrs[0], self.control, self.endOrientSpaceConstraint, endOrientSpaceAttrs[1], self.control), n='endOrientSpaceConstraint_on_off' )

		#build expressions for fk blending and control visibility
		self.fkVisCond = fkVisCond = shadingNode( 'condition', asUtility=True )
		self.poleVisCond = poleVisCond = shadingNode( 'condition', asUtility=True )
		connectAttr( '%s.ikBlend' % self.control, '%s.firstTerm' % self.fkVisCond, f=True )
		connectAttr( '%s.ikBlend' % self.control, '%s.firstTerm' % self.poleVisCond, f=True )
		connectAttr( '%s.outColorG' % self.poleVisCond, '%s.v' % self.lineNode, f=True )
		connectAttr( '%s.outColorG' % self.poleVisCond, '%s.v' % self.poleControlSpace, f=True )
		connectAttr( '%s.outColorG' % self.poleVisCond, '%s.v' % self.control, f=True )
		setAttr( '%s.secondTerm' % self.fkVisCond, 1 )

		driverUpper, driverMid, driverLower = self.driverUpper, self.driverMid, self.driverLower
		expression( s='if ( %(limbControl)s.ikBlend > 0 && %(limbControl)s.orientToIk < 1 ) %(driverLower)s.visibility = 1;\nelse %(driverLower)s.visibility = %(fkVisCond)s.outColorG;' % locals(), n='wrist_visSwitch' )
		for driver in (self.driverUpper, self.driverMid):
			for shape in listRelatives( driver, s=True, pa=True ):
				connectAttr( '%s.outColorR' % self.fkVisCond, '%s.v' % shape, f=True )

		#add set pole to fk pos command to pole control
		poleTrigger = Trigger( self.poleControl )
		poleConnectNums = [ poleTrigger.connect( c ) for c in self.fkControls ]

		idx_toFK = poleTrigger.setMenuInfo( None, "move to FK position",
		                                    'zooVectors;\nfloat $pos[] = `zooFindPolePosition "-start %%%s -mid %%%s -end %%%s"`;\nmove -rpr $pos[0] $pos[1] $pos[2] #;' % tuple( poleConnectNums ) )
		poleTrigger.setMenuInfo( None, "move to FK pos for all keys",
		                         'source zooKeyCommandsWin;\nzooSetKeyCommandsWindowCmd "eval(zooPopulateCmdStr(\\\"#\\\",(zooGetObjMenuCmdStr(\\\"#\\\",%%%d)),{}))";' % idx_toFK )

		limbTrigger = Trigger( self.control )
		handleNum = limbTrigger.connect( self.ikHandle )
		poleNum = limbTrigger.connect( self.poleControl )
		lowerNum = limbTrigger.connect( self.driverLower )
		fkIdx = limbTrigger.createMenu( "switch to FK",
			                            "zooAlign \"\";\nzooAlignFK \"-ikHandle %%%d -offCmd setAttr #.ikBlend 0\";\nselect %%%d;" % (handleNum, lowerNum) )
		limbTrigger.createMenu( "switch to FK for all keys",
			                    'source zooKeyCommandsWin;\nzooSetKeyCommandsWindowCmd "eval(zooPopulateCmdStr(\\\"#\\\",(zooGetObjMenuCmdStr(\\\"#\\\",%%%d)),{}))";' % fkIdx )
		ikIdx = limbTrigger.createMenu( "switch to IK",
			                            'zooAlign "";\nzooAlignIK "-ikHandle %%%d -pole %%%d -offCmd setAttr #.ikBlend 1;";' % (handleNum, poleNum) )
		limbTrigger.createMenu( "switch to IK for all keys",
			                    'source zooKeyCommandsWin;\nzooSetKeyCommandsWindowCmd "eval(zooPopulateCmdStr(\\\"#\\\",(zooGetObjMenuCmdStr(\\\"#\\\",%%%d)),{}))";' % ikIdx )

		#add all zooObjMenu commands to the fk controls
		for fk in self.fkControls:
			fkTrigger = Trigger( fk )
			c1 = fkTrigger.connect( self.ikHandle )
			c2 = fkTrigger.connect( self.poleControl )

			fkTrigger.createMenu( 'switch to IK',
				                  'zooAlign "";\nstring $cs[] = `listConnections %%%d.ikBlend`;\nzooAlignIK ("-ikHandle %%%d -pole %%%d -control "+ $cs[0] +" -offCmd setAttr "+ $cs[0] +".ikBlend 1;" );' % (c1, c1, c2) )

		createLineOfActionMenu( [self.control] + list( self.fkControls ), (self.elbow, self.wrist) )

		#add trigger commands
		Trigger.CreateTrigger( self.lineNode, Trigger.PRESET_SELECT_CONNECTED, [ self.poleControl ] )
		setAttr( '%s.displayHandle' % self.lineNode, True )

		#turn unwanted transforms off, so that they are locked, and no longer keyable
		attrState( self.poleControl, 'r', *LOCK_HIDE )
	def buildAllPurposeLocator( self, nodePrefix ):
		allPurposeObj = spaceLocator( name="%s_all_purpose_loc%s" % (nodePrefix, self.getSuffix()) )[ 0 ]
		attrState( allPurposeObj, 's', *LOCK_HIDE )
		attrState( allPurposeObj, 'v', *HIDE )
		parent( allPurposeObj, self.getWorldControl() )

		return allPurposeObj
	def getFkControls( self ):
		return self.getControl( 'fkUpper' ), self.getControl( 'fkMid' ), self.getControl( 'fkLower' )
	def getIkControls( self ):
		return self.getControl( 'control' ), self.getControl( 'poleControl' ), self.getControl( 'ikHandle' )
	@d_unifyUndo
	def switchToFk( self, key=False ):
		control, poleControl, handle = self.getIkControls()
		attrName = 'ikBlend'
		onValue = 1
		offValue = 0
		joints = self.getFkControls()

		if handle is None or not objExists( handle ):
			printWarningStr( "no ikHandle specified" )
			return

		#make sure ik is on before querying rotations
		setAttr( '%s.%s' % (control, attrName), onValue )
		rots = []
		for j in joints:
			rot = getAttr( "%s.r" % j )[0]
			rots.append( rot )

		#now turn ik off and set rotations for the joints
		setAttr( '%s.%s' % (control, attrName), offValue )
		for j, rot in zip( joints, rots ):
			for ax, r in zip( ('x', 'y', 'z'), rot ):
				if getAttr( '%s.r%s' % (j, ax), se=True ):
					setAttr( '%s.r%s' % (j, ax), r )

		alignFast( joints[2], handle )
		if key:
			setKeyframe( joints )
			setKeyframe( '%s.%s' % (control, attrName) )
	@d_unifyUndo
	def switchToIk( self, key=False, _isBatchMode=False ):
		control, poleControl, handle = self.getIkControls()
		attrName = 'ikBlend'
		onValue = 1
		joints = self.getFkControls()

		if handle is None or not objExists( handle ):
			printWarningStr( "no ikHandle specified" )
			return

		alignFast( control, joints[2] )
		if poleControl:
			if objExists( poleControl ):
				pos = findPolePosition( joints[2], joints[1], joints[0] )
				move( pos[0], pos[1], pos[2], poleControl, a=True, ws=True, rpr=True )
				setKeyframe( poleControl )

		setAttr( '%s.%s' % (control, attrName), onValue )
		if key:
			setKeyframe( control, at=('t', 'r') )
			if not _isBatchMode:
				setKeyframe( control, at=attrName )


#end
