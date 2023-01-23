
from baseRigPrimitive import *


class Root(PrimaryRigPart):
	__version__ = 0
	SKELETON_PRIM_ASSOC = ( skeletonBuilder.Root, )
	CONTROL_NAMES = 'control', 'gimbal', 'hips'

	def _build( self, skeletonPart, buildHips=True, **kw ):
		root = skeletonPart.base

		#deal with colours
		colour = ColourDesc( 'blue' )
		darkColour = colour.darken( 0.5 )
		lightColour = colour.lighten( 0.5 )


		#hook up the scale from the main control
		connectAttr( '%s.scale' % self.getWorldControl(), '%s.scale' % root )
		partParent, altRootControl = getParentAndRootControl( root )


		#try to determine a sensible size for the root control - basically grab teh autosize of the root joint, and take the x-z plane values
		size = control.getJointSize( [root], 0.5, SPACE_WORLD )
		ringSize = Vector( (size[0], size[0] + size[2] / 3.0, size[2]) )


		#create the controls, and parent them
		rootControl = buildControl( 'upperBodyControl', (root, PlaceDesc.WORLD), shapeDesc=ShapeDesc( 'band', axis=AX_Y ), colour=colour, constrain=False, size=size, parent=partParent )
		rootGimbal = buildControl( 'gimbalControl', (root, PlaceDesc.WORLD), shapeDesc=ShapeDesc( 'ring', axis=AX_Y ), colour=darkColour, oriented=False, offset=(0, size.y/2, 0), size=ringSize, parent=rootControl, niceName='Upper Body Control' )
		hipsControl = buildControl( 'hipsControl', (root, PlaceDesc.WORLD), shapeDesc=ShapeDesc( 'ring', axis=AX_Y ), colour=lightColour, constrain=False, oriented=False, offset=(0, -size.y/2, 0), size=ringSize, parent=rootGimbal )
		rootSpace = listRelatives( rootControl, p=True, pa=True )


		#delete the connections to rotation so we can put an orient constraint on the root joint to teh hips control
		for ax in AXES:
			delete( '%s.r%s' % (root, ax), icn=True )

		orientConstraint( hipsControl, root, mo=True )

		attrState( hipsControl, 't', *LOCK_HIDE )


		#turn unwanted transforms off, so that they are locked, and no longer keyable
		attrState( (rootGimbal, hipsControl), 't', *LOCK_HIDE )

		for s in listRelatives( rootGimbal, s=True, pa=True ):
			setAttr( '%s.visibility' % s, False )

		xform( rootControl, p=1, roo='xzy' )
		xform( rootGimbal, p=1, roo='zxy' )


		#add right click menu to turn on the gimbal control
		Trigger.CreateMenu( rootControl,
			                "toggle gimbal control",
			                "{\nstring $kids[] = `listRelatives -pa -type transform #`;\n$kids = `listRelatives -s $kids[0]`;\nint $vis = `getAttr ( $kids[0] +\".v\" )`;\nfor( $k in $kids ) setAttr ( $k +\".v\" ) (!$vis);\n}" )

		Trigger.CreateMenu( rootGimbal,
			                "toggle gimbal control",
			                "{\nstring $kids[] = `listRelatives -pa -s #`;\nint $vis = `getAttr ( $kids[0] +\".v\" )`;\nfor( $k in $kids ) setAttr ( $k +\".v\" ) (!$vis);\nselect `listRelatives -p`;\n}" )

		controls = rootControl, rootGimbal, hipsControl

		return controls, ()
	def setupMirroring( self ):
		for control in self:
			pair = poseSym.ControlPair.Create( control )
			pair.setFlips( 0 )


#end
