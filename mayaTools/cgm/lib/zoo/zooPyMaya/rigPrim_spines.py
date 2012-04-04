
from rigPrim_curves import *
from spaceSwitching import build, NO_TRANSLATION, NO_ROTATION


class FkSpine(PrimaryRigPart):
	__version__ = 0
	SKELETON_PRIM_ASSOC = ( SkeletonPart.GetNamedSubclass( 'Spine' ), )

	def _build( self, skeletonPart, translateControls=True, **kw ):
		spineBase, spineEnd = skeletonPart.base, skeletonPart.end
		partParent, rootControl = getParentAndRootControl( spineBase )

		#build a list of all spine joints - start from the bottom of the heirarchy, and work up - a joint only has one parent
		spines = [ spineEnd ]
		if spineBase != spineEnd:
			while True:
				p = getNodeParent( spines[ -1 ] )
				spines.append( p )
				if p == spineBase: break

			spines.reverse()

		#try to figure out a sensible offset for the spine controls - this is basically just an average of the all offsets for all spine joints
		spineOffset = AX_Z.asVector() * getAutoOffsetAmount( spines[ 0 ], spines )

		#create the controls, and parent them
		#determine what axis to draw the spine controls - assume they're all the same as the spine base
		controlSpaces = []
		controllers = []
		startColour = ColourDesc( (1, 0.3, 0, 0.65) )
		endColour = ColourDesc( (0.8, 1, 0, 0.65) )
		spineColour = startColour
		colourInc = (endColour - startColour) / float( len( spines ) )

		for n, j in enumerate( spines ):
			c = buildControl( "spine_%d_fkControl" % n, j, PivotModeDesc.BASE, ShapeDesc( 'pin', axis=AX_Z ), colour=spineColour, offset=spineOffset, scale=self.scale*1.5, niceName='Spine %d Control' % n )
			cSpace = getNodeParent( c )

			jParent = partParent
			if n: jParent = controllers[ -1 ]

			controllers.append( c )
			controlSpaces.append( cSpace )

			parent( cSpace, jParent )
			spineColour += colourInc

		setNiceName( controllers[ 0 ], 'Spine Base' )
		setNiceName( controllers[ -1 ], 'Spine End' )

		#create the space switching
		for j, c in zip( spines, controllers ):
			buildDefaultSpaceSwitching( j, c, **spaceSwitching.NO_TRANSLATION )


		#create line of action commands
		createLineOfActionMenu( spines, controllers )


		#turn unwanted transforms off, so that they are locked, and no longer keyable
		if not translateControls:
			attrState( controllers, 't', *LOCK_HIDE )


		return controllers, ()


class IKFKSpine(PrimaryRigPart):
	__version__ = 0
	PRIORITY = 10  #make this a lower priority than the simple FK spine rig
	SKELETON_PRIM_ASSOC = ( SkeletonPart.GetNamedSubclass( 'Spine' ), )

	@classmethod
	def CanRigThisPart( cls, skeletonPart ):
		return len( skeletonPart ) >= 3
	def _build( self, skeletonPart, squish=True, **kw ):
		objs = skeletonPart.items

		parentControl, rootControl = getParentAndRootControl( objs[0] )

		fittedCurve, linearCurve, proxies, fixedLengthProxies, controls, splineIkHandle, halfIdx = buildControls( objs, parentControl, name='spineControl', **kw )
		buildDefaultSpaceSwitching( objs[0], controls[-1] )

		parent( proxies, self.getPartsNode() )
		parent( fittedCurve, linearCurve, self.getPartsNode() )
		if splineIkHandle:
			parent( splineIkHandle, self.getPartsNode() )

		if fixedLengthProxies:
			parent( fixedLengthProxies[0], self.getPartsNode() )

		return controls, ()


#end
