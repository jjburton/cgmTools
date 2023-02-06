
from baseSkeletonBuilder import *


class _QuadCommon(object):
	AVAILABLE_IN_UI = False

	def _buildPlacers( self ):
		assert isinstance( self, SkeletonPart )

		parity = self.getParity()
		parityMultiplier = parity.asMultiplier()
		scale = self.getBuildScale() / 30

		toeTipPlacer = buildEndPlacer()
		heelPlacer = buildEndPlacer()
		innerRollPlacer = buildEndPlacer()
		outerRollPlacer = buildEndPlacer()

		placers = toeTipPlacer, heelPlacer, innerRollPlacer, outerRollPlacer
		cmd.parent( placers, self.end, r=True )

		fwd = MAYA_SIDE
		side = MAYA_UP

		setAttr( '%s.t' % toeTipPlacer, *(fwd * 2 * scale) )
		setAttr( '%s.t' % heelPlacer, *(-fwd * scale) )
		setAttr( '%s.t' % innerRollPlacer, *(side * scale * parityMultiplier) )
		setAttr( '%s.t' % outerRollPlacer, *(-side * scale * parityMultiplier) )

		return placers
	def visualize( self ):
		pass


class QuadrupedFrontLeg(_QuadCommon, SkeletonPart.GetNamedSubclass('Arm')):
	'''
	A quadruped's front leg is more like a biped's arm as it has clavicle/shoulder
	blade functionality, but is generally positioned more like a leg.  It is a separate
	part because it is rigged quite differently from either a bipedal arm or a bipedal
	leg.
	'''

	AVAILABLE_IN_UI = True
	PLACER_NAMES = 'toeTip', 'innerRoll', 'outerRoll', 'heelRoll'

	@classmethod
	def _build( cls, parent=None, **kw ):
		idx = Parity( kw[ 'idx' ] )
		partScale = kw[ 'partScale' ]

		parent = getParent( parent )
		height = xform( parent, q=True, ws=True, rp=True )[ 1 ]

		dirMult = idx.asMultiplier()
		parityName = idx.asName()

		clavicle = createJoint( 'quadClavicle%s' % parityName )
		cmd.parent( clavicle, parent, relative=True )
		move( dirMult * partScale / 10.0, -partScale / 10.0, partScale / 6.0, clavicle, r=True, ws=True )

		bicep = createJoint( 'quadHumerous%s' % parityName )
		cmd.parent( bicep, clavicle, relative=True )
		move( 0, -height / 3.0, -height / 6.0, bicep, r=True, ws=True )

		elbow = createJoint( 'quadElbow%s' % parityName )
		cmd.parent( elbow, bicep, relative=True )
		move( 0, -height / 3.0, height / 10.0, elbow, r=True, ws=True )

		wrist = createJoint( 'quadWrist%s' % parityName )
		cmd.parent( wrist, elbow, relative=True )
		move( 0, -height / 3.0, 0, wrist, r=True, ws=True )

		jointSize( clavicle, 2 )
		jointSize( wrist, 2 )

		return [ clavicle, bicep, elbow, wrist ]


class QuadrupedBackLeg(_QuadCommon, SkeletonPart.GetNamedSubclass( 'Arm' )):
	'''
	The creature's back leg is more like a biped's leg in terms of the joints it contains.
	However, like the front leg, the creature stands on his "tip toes" at the back as well.
	'''

	AVAILABLE_IN_UI = False

	@classmethod
	def _build( cls, parent=None, **kw ):
		idx = Parity( kw[ 'idx' ] )
		partScale = kw[ 'partScale' ]

		parent = getParent( parent )
		height = xform( parent, q=True, ws=True, rp=True )[ 1 ]

		dirMult = idx.asMultiplier()
		parityName = idx.asName()

		kneeFwdMove = height / 10.0

		thigh = createJoint( 'quadThigh%s' % parityName )
		thigh = cmd.parent( thigh, parent, relative=True )[ 0 ]
		move( dirMult * partScale / 10.0, -partScale / 10.0, -partScale / 5.0, thigh, r=True, ws=True )

		knee = createJoint( 'quadKnee%s' % parityName )
		knee = cmd.parent( knee, thigh, relative=True )[ 0 ]
		move( 0, -height / 3.0, kneeFwdMove, knee, r=True, ws=True )

		ankle = createJoint( 'quadAnkle%s' % parityName )
		ankle = cmd.parent( ankle, knee, relative=True )[ 0 ]
		move( 0, -height / 3.0, -kneeFwdMove, ankle, r=True, ws=True )

		toe = createJoint( 'quadToe%s' % parityName )
		toe = cmd.parent( toe, ankle, relative=True )[ 0 ]
		move( 0, -height / 3.0, 0, toe, r=True, ws=True )

		jointSize( thigh, 2 )
		jointSize( ankle, 2 )
		jointSize( toe, 1.5 )

		return [ thigh, knee, ankle, toe ]


class SatyrLeg(_QuadCommon, SkeletonPart.GetNamedSubclass('Leg')):
	AVAILABLE_IN_UI = True
	PLACER_NAMES = 'toeTip', 'innerRoll', 'outerRoll', 'heelRoll'

	@property
	def thigh( self ): return self[ 0 ]
	@property
	def knee( self ): return self[ 1 ]
	@property
	def ankle( self ): return self[ 2 ]
	@property
	def toe( self ): return self[ 3 ] if len( self ) > 3 else None
	@classmethod
	def _build( cls, parent=None, **kw ):
		idx = Parity( kw[ 'idx' ] )
		partScale = kw[ 'partScale' ]

		parent = getParent( parent )
		height = xform( parent, q=True, ws=True, rp=True )[ 1 ]

		dirMult = idx.asMultiplier()
		parityName = idx.asName()

		legDrop = partScale / 12.0
		sectionDist = (height - legDrop) / 3.0
		kneeFwdMove = (height - legDrop) / 3.0

		thigh = createJoint( 'thigh%s' % parityName )
		thigh = cmd.parent( thigh, parent, relative=True )[ 0 ]
		move( dirMult * partScale / 10.0, -legDrop, 0, thigh, r=True, ws=True )

		knee = createJoint( 'knee%s' % parityName )
		knee = cmd.parent( knee, thigh, relative=True )[ 0 ]
		move( 0, -sectionDist, kneeFwdMove, knee, r=True, ws=True )

		ankle = createJoint( 'ankle%s' % parityName )
		ankle = cmd.parent( ankle, knee, relative=True )[ 0 ]
		move( 0, -sectionDist, -kneeFwdMove, ankle, r=True, ws=True )

		toe = createJoint( 'toeBall%s' % parityName )
		toe = cmd.parent( toe, ankle, relative=True )[ 0 ]
		move( 0, -sectionDist, kneeFwdMove / 2.0, toe, r=True, ws=True )

		jointSize( thigh, 2 )
		jointSize( ankle, 2 )
		jointSize( toe, 1.5 )

		return [ thigh, knee, ankle, toe ]
	def _align( self, _initialAlign=False ):
		upperNormal = getPlaneNormalForObjects( self.thigh, self.knee, self.ankle )
		upperNormal *= self.getParityMultiplier()

		parity = self.getParity()

		alignAimAtItem( self.thigh, self.knee, parity, worldUpVector=upperNormal )
		alignAimAtItem( self.knee, self.ankle, parity, worldUpVector=upperNormal )

		if self.toe:
			lowerNormal = getPlaneNormalForObjects( self.knee, self.ankle, self.toe )
			lowerNormal *= self.getParityMultiplier()

			alignAimAtItem( self.ankle, self.toe, parity, worldUpVector=upperNormal )

		for i in self.getOrphanJoints():
			alignItemToLocal( i )


#end
