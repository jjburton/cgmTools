
from baseSkeletonBuilder import *


class Leg(SkeletonPart):
	HAS_PARITY = True

	PLACER_NAMES = 'footTip', 'footInner', 'footOuter', 'heel'

	@property
	def thigh( self ): return self[ 0 ]
	@property
	def knee( self ): return self[ 1 ]
	@property
	def ankle( self ): return self[ 2 ]
	@property
	def toe( self ): return self[ 3 ] if len( self ) > 3 else None
	@classmethod
	def _build( cls, parent=None, buildToe=True, toeCount=0, **kw ):
		idx = Parity( kw[ 'idx' ] )
		partScale = kw[ 'partScale' ]

		parent = getParent( parent )

		root = getRoot()
		height = xform( root, q=True, ws=True, rp=True )[ 1 ]

		dirMult = idx.asMultiplier()
		parityName = idx.asName()

		sidePos = dirMult * partScale / 10.0
		upPos = partScale / 20.0
		fwdPos = -(idx / 2) * partScale / 5.0

		footHeight = height / 15.0 if buildToe else 0
		kneeOutMove = dirMult * partScale / 35.0
		kneeFwdMove = partScale / 20.0

		thigh = createJoint( 'thigh%s' % parityName )
		cmd.parent( thigh, parent, relative=True )
		move( sidePos, -upPos, fwdPos, thigh, r=True, ws=True )

		knee = createJoint( 'knee%s' % parityName )
		cmd.parent( knee, thigh, relative=True )
		move( 0, -(height - footHeight) / 2.0, kneeFwdMove, knee, r=True, ws=True )

		ankle = createJoint( 'ankle%s' % parityName )
		cmd.parent( ankle, knee, relative=True )
		move( 0, -(height - footHeight) / 2.0, -kneeFwdMove, ankle, r=True, ws=True )

		jointSize( thigh, 2 )
		jointSize( ankle, 2 )

		allJoints = []
		if buildToe:
			toe = createJoint( 'toeBase%s' % parityName )
			cmd.parent( toe, ankle, relative=True )
			move( 0, -footHeight, footHeight * 3, toe, r=True, ws=True )
			allJoints.append( toe )

			jointSize( toe, 1.5 )

			for n in range( toeCount ):
				toeN = createJoint( 'toe_%d_%s' % (n, parityName) )
				allJoints.append( toeN )
				#move( dirMult * partScale / 50.0, 0, partScale / 25.0, toeN, ws=True )
				cmd.parent( toeN, toe, relative=True )

		rotate( 0, dirMult * 15, 0, thigh, r=True, ws=True )

		return [ thigh, knee, ankle ] + allJoints
	def _buildPlacers( self ):
		placers = []

		scale = getItemScale( self.ankle )

		p = buildEndPlacer()
		p = parent( p, self.toe, r=True )[0]
		move( 0, 0, scale/3, p, r=True )
		move( 0, 0, 0, p, moveY=True, a=True, ws=True )
		placers.append( p )

		p = buildEndPlacer()
		p = parent( p, self.ankle, r=True )[0]
		setAttr( '%s.ty' % p, -scale/1.5 )
		move( 0, 0, 0, p, moveY=True, a=True, ws=True )
		placers.append( p )

		p = buildEndPlacer()
		p = parent( p, self.ankle, r=True )[0]
		setAttr( '%s.ty' % p, scale/1.5 )
		move( 0, 0, 0, p, moveY=True, a=True, ws=True )
		placers.append( p )

		p = buildEndPlacer()
		p = parent( p, self.ankle, r=True )[0]
		move( 0, 0, -scale/3, p, r=True )
		move( 0, 0, 0, p, moveY=True, a=True, ws=True )
		placers.append( p )

		return placers
	def _align( self, _initialAlign=False ):
		normal = getPlaneNormalForObjects( self.thigh, self.knee, self.ankle )
		normal *= self.getParityMultiplier()

		parity = self.getParity()

		alignAimAtItem( self.thigh, self.knee, parity, worldUpVector=normal )
		alignAimAtItem( self.knee, self.ankle, parity, worldUpVector=normal )

		if self.toe:
			alignAimAtItem( self.ankle, self.toe, parity, upVector=ENGINE_UP, upType='scene' )
		else:
			autoAlignItem( self.ankle, parity, upVector=ENGINE_UP, upType='scene' )

		for i in self.getOrphanJoints():
			alignItemToLocal( i )
	def visualize( self ):
		pass
	def getIkFkItems( self ):
		return self.thigh, self.knee, self.ankle


#end
