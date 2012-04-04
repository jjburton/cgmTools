
from baseSkeletonBuilder import *


class Hand(SkeletonPart):
	HAS_PARITY = True

	AUTO_NAME = False  #this part will handle its own naming...

	#odd indices are left sided, even are right sided
	FINGER_IDX_NAMES = ( 'Thumb', 'Index', 'Mid', 'Ring', 'Pinky',
		                 'Sixth' 'Seventh', 'Eighth', 'Ninth', 'Tenth' )

	PLACER_NAMES = FINGER_IDX_NAMES

	def getParity( self ):
		'''
		the parity of a hand comes from the limb its parented to, not the idx of
		the finger part itself...
		'''

		parent = self.getParent()
		try:
			#if the parent has parity use it
			parentPart = SkeletonPart.InitFromItem( parent )

		except SkeletonError:
			#otherwise use the instance's index for parity...
			return super( self, Hand ).getParity()

		return Parity( parentPart.getParity() )
	def iterFingerChains( self ):
		'''
		iterates over each finger chain in the hand - a chain is simply a list of
		joint names ordered hierarchically
		'''
		for base in self.bases:
			children = listRelatives( base, ad=True, path=True, type='joint' ) or []
			children = [ base ] + sortByHierarchy( children )
			yield children
	@classmethod
	def _build( cls, parent=None, fingerCount=5, fingerJointCount=3, **kw ):
		idx = Parity( kw[ 'idx' ] )
		partScale = kw[ 'partScale' ]

		parent = getParent( parent )
		parentPart = SkeletonPart.InitFromItem( parent )

		#try to determine a "parity index" based on the parent part.  Ideally we want to inherit the parity of the parent part
		#instead of from this part's index
		limbIdx = 0
		if parentPart.hasParity():
			limbIdx = parentPart.getParity()

		#if the parent part has no parity, then use the instance's index for parity...
		else:
			limbIdx = self.getParity()

		#for the first two hands this is an empty string - but for each additional hand pair, this is incremented.  ie the
		#second two hands are called Hand1, the next two hands are called Hand2 etc...
		typePairCountStr = str( idx/2 ) if idx > 1 else ''

		minPos, maxPos = -cls.PART_SCALE / 25.0, cls.PART_SCALE / 25.0
		posRange = float( maxPos - minPos )
		allJoints = []

		length = partScale / 3 / fingerJointCount
		lengthInc = cls.ParityMultiplier( limbIdx ) * (length / fingerJointCount)

		limbName = Parity.NAMES[ limbIdx ]
		for nameIdx in range( fingerCount ):
			fingerName = cls.FINGER_IDX_NAMES[ nameIdx ]
			prevParent = parent
			for n in range( fingerJointCount ):
				j = createJoint( '%s%s_%d%s' % (fingerName, typePairCountStr, n, limbName) )
				cmd.parent( j, prevParent, r=True )
				move( lengthInc, 0, 0, j, r=True, os=True )

				if n == 0:
					move( lengthInc, 0, -maxPos + (posRange * nameIdx / (fingerCount - 1)), j, r=True, os=True )
				else:
					setAttr( '%s.ty' % j, lock=True )

				allJoints.append( j )
				prevParent = j

		return allJoints
	def visualize( self ):
		scale = self.getActualScale() / 1.5

		for base in self.bases:
			plane = polyPlane( w=scale, h=scale / 2.0, sx=1, sy=1, ax=(0, 1, 0), cuv=2, ch=False )[ 0 ]
			cmd.parent( plane, base, relative=True )

			setAttr( '%s.tx' % plane, self.getParityMultiplier() * scale / 2 )
			makeIdentity( plane, a=True, t=True )

			cmd.parent( listRelatives( plane, shapes=True, pa=True ), base, add=True, shape=True )
			delete( plane )
	def _align( self, _initialAlign=False ):
		parity = self.getParity()
		wrist = self.getParent()

		parityMult = self.getParityMultiplier()

		defactoUpVector = rigUtils.getObjectBasisVectors( wrist )[ 2 ]
		for chain in self.iterFingerChains():
			upVector = defactoUpVector

			#if there are three joints or more in teh chain, try to determine the normal to the plane they live on
			if len( chain ) >= 3:
				midJoint = chain[ len( chain ) / 2 ]
				upVector = getPlaneNormalForObjects( chain[ 0 ], midJoint, chain[ -1 ], defactoUpVector )

			#otherwise assume the user has aligned the base joint properly
			else:
				upVector = rigUtils.getObjectBasisVectors( chain[ 0 ] )[ BONE_ROTATE_AXIS ]

			upVector = upVector * parityMult
			for n, item in enumerate( chain[ :-1 ] ):
				alignAimAtItem( item, chain[ n+1 ], parity, worldUpVector=upVector )

			autoAlignItem( chain[ -1 ], parity, worldUpVector=upVector )


#end
