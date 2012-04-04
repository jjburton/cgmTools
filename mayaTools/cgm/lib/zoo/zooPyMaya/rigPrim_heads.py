
from baseRigPrimitive import *


class Head(PrimaryRigPart):
	__version__ = 0
	SKELETON_PRIM_ASSOC = ( SkeletonPart.GetNamedSubclass( 'Head' ), )
	CONTROL_NAMES = 'control', 'gimbal', 'neck'

	def _build( self, skeletonPart, translateControls=False, **kw ):
		return self.doBuild( skeletonPart.head, translateControls=translateControls, **kw )
	def doBuild( self, head, neckCount=1, translateControls=False, **kw ):
		scale = self.scale
		partParent, rootControl = getParentAndRootControl( head )

		colour = ColourDesc( 'blue' )
		lightBlue = ColourDesc( 'lightblue' )


		#build the head controls - we always need them
		headControl = buildControl( "headControl", head,
			                        shapeDesc=Shape_Skin( [head] + (listRelatives( head, ad=True, type='joint' ) or []) ),
			                        colour=colour, scale=scale )

		headControlSpace = getNodeParent( headControl )
		headGimbal = buildControl( "head_gimbalControl", head, shapeDesc=ShapeDesc( None, 'starCircle' ), colour=colour, oriented=False, scale=scale, autoScale=True, parent=headControl, niceName='Head' )


		#now find the neck joints
		neckJoints = []
		curParent = head
		for n in range( neckCount ):
			curParent = getNodeParent( curParent )
			neckJoints.append( curParent )

		neckJoints.reverse()


		#determine an offset amount for the neck controls based on the geometry skinned to the necks and head joint
		neckOffset = AX_Z.asVector() * getAutoOffsetAmount( head, neckJoints )


		#build the controls for them
		neckControls = []
		theParent = partParent
		for n, j in enumerate( neckJoints ):
			c = buildControl( 'neck_%d_Control' % n, j, PivotModeDesc.BASE, ShapeDesc( 'pin', axis=AX_Z ), colour=lightBlue, scale=scale*1.5, offset=neckOffset, parent=theParent, niceName='Neck %d' % n )
			if not translateControls:
				attrState( c, 't', *LOCK_HIDE )

			theParent = c
			neckControls.append( c )

		if neckCount == 1:
			neckControls[ 0 ] = rename( neckControls[ 0 ], 'neckControl' )
			setNiceName( neckControls[ 0 ], 'Neck' )
		elif neckCount >= 2:
			setNiceName( neckControls[ 0 ], 'Neck Base' )
			setNiceName( neckControls[ -1 ], 'Neck End' )

		if neckCount:
			parent( headControlSpace, neckControls[ -1 ] )
		else:
			parent( headControlSpace, partParent )


		#build space switching
		if neckControls:
			spaceSwitching.build( headControl,
				                  (neckControls[ 0 ], partParent, rootControl, self.getWorldControl()),
				                  space=headControlSpace, **spaceSwitching.NO_TRANSLATION )

		for c in neckControls:
			spaceSwitching.build( c,
				                  (partParent, rootControl, self.getWorldControl()),
				                  **spaceSwitching.NO_TRANSLATION )


		#add right click menu to turn on the gimbal control
		gimbalIdx = Trigger( headControl ).connect( headGimbal )
		Trigger.CreateMenu( headControl,
			                "toggle gimbal control",
			                "string $shapes[] = `listRelatives -f -s %%%d`;\nint $vis = `getAttr ( $shapes[0] +\".v\" )`;\nfor( $s in $shapes ) setAttr ( $s +\".v\" ) (!$vis);" % gimbalIdx )


		#turn unwanted transforms off, so that they are locked, and no longer keyable, and set rotation orders
		gimbalShapes = listRelatives( headGimbal, s=True )
		for s in gimbalShapes:
			setAttr( '%s.v' % s, 0 )

		setAttr( '%s.ro' % headControl, 3 )
		setAttr( '%s.ro' % headGimbal, 3 )

		if not translateControls:
			attrState( (headControl, headGimbal), 't', *LOCK_HIDE )

		controls = [ headControl, headGimbal ] + neckControls

		return controls, ()


#end
