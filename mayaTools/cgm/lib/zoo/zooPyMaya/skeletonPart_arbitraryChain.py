
from baseSkeletonBuilder import *


class ArbitraryChain(SkeletonPart):
	HAS_PARITY = False

	@classmethod
	def _build( cls, parent=None, partName='', jointCount=5, direction='-z', **kw ):
		if not partName:
			partName = cls.__name__

		idx = Parity( kw[ 'idx' ] )
		partScale = kw[ 'partScale' ]

		partName = '%s%s' % (partName, idx)

		parent = getParent( parent )

		dirMult = cls.ParityMultiplier( idx ) if cls.HAS_PARITY else 1
		length = partScale
		lengthInc = dirMult * length / jointCount

		directionAxis = rigUtils.Axis.FromName( direction )
		directionVector = directionAxis.asVector() * lengthInc
		directionVector = list( directionVector )
		otherIdx = directionAxis.otherAxes()[ 1 ]

		parityStr = idx.asName() if cls.HAS_PARITY else ''
		allJoints = []
		prevParent = parent
		half = jointCount / 2
		for n in range( jointCount ):
			j = createJoint( '%s_%d%s' % (partName, n, parityStr) )
			cmd.parent( j, prevParent, r=True )

			moveVector = directionVector + [ j ]
			moveVector[ otherIdx ] = dirMult * n * lengthInc / jointCount / 5.0
			move( moveVector[0], moveVector[1], moveVector[2], j, r=True, ws=True )
			allJoints.append( j )
			prevParent = j

		return allJoints
	def _align( self, _initialAlign=False ):
		parity = Parity( 0 )
		if self.hasParity():
			parity = self.getParity()

		num = len( self )
		if num == 1:
			autoAlignItem( self[ 0 ], parity )
		elif num == 2:
			for i in self.selfAndOrphans(): autoAlignItem( i, parity )
		else:
			#in this case we want to find a plane that roughly fits the chain.
			#for the sake of simplicity take the first, last and some joint in
			#the middle and fit a plane to them, and use it's normal for the upAxis
			midJoint = self[ num / 2 ]
			defaultUpVector = rigUtils.getObjectBasisVectors( self[ 0 ] )[ BONE_OTHER_AXIS ]
			normal = getPlaneNormalForObjects( self.base, midJoint, self.end, defaultUpVector )
			normal *= parity.asMultiplier()

			for n, i in enumerate( self[ :-1 ] ):
				alignAimAtItem( i, self[ n+1 ], parity, worldUpVector=normal )

			autoAlignItem( self[ -1 ], parity, worldUpVector=normal )

			#should we align the orphans?
			rigKwargs = self.getRigKwargs()
			if 'rigOrphans' in rigKwargs:
				if rigKwargs[ 'rigOrphans' ]:
					for i in self.getOrphanJoints():
						autoAlignItem( i, parity, worldUpVector=normal )

		# read just the rotations to be inline with the parent joint -- wish we didn't have to do this
		endPlacer = self.endPlacer
		if endPlacer:
			setAttr( '%s.r' % endPlacer, 0, 0, 0 )
	def visualize( self ):
		scale = self.getBuildScale() / 10.0
		midJoint = self[ len( self ) / 2 ]


class ArbitraryParityChain(ArbitraryChain):
	HAS_PARITY = True


#end
