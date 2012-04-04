
from baseSkeletonBuilder import *


class Head(SkeletonPart):
	HAS_PARITY = False

	@property
	def head( self ): return self[ -1 ]
	@classmethod
	def _build( cls, parent=None, neckCount=1, **kw ):
		idx = kw[ 'idx' ]
		partScale = kw[ 'partScale' ]

		parent = getParent( parent )

		posInc = partScale / 25.0

		head = createJoint( 'head' )
		if not neckCount:
			cmd.parent( head, parent, relative=True )
			return [ head ]

		allJoints = []
		prevJoint = parent

		for n in range( neckCount ):
			j = createJoint( 'neck%d' % (n+1) )
			cmd.parent( j, prevJoint, relative=True )
			move( 0, posInc, posInc, j, r=True, ws=True )
			allJoints.append( j )
			prevJoint = j

		#move the first neck joint up a bunch
		move( 0, partScale / 10.0, 0, allJoints[ 0 ], r=True, ws=True )

		#parent the head appropriately
		cmd.parent( head, allJoints[ -1 ], relative=True )
		move( 0, posInc, posInc, head, r=True, ws=True )
		allJoints.append( head )

		jointSize( head, 2 )

		return allJoints
	def _align( self, _initialAlign=False ):

		#aim all neck joints at the next neck joint
		for n, item in enumerate( self[ :-1 ] ):
			alignAimAtItem( item, self[ n+1 ] )

		if _initialAlign:
			alignItemToWorld( self.head )
		else:
			alignPreserve( self.head )
	def visualize( self ):
		scale = self.getBuildScale() / 10.0

		plane = polyCreateFacet( ch=False, tx=True, s=1, p=((0, -scale, 0), (0, scale, 0), (self.getParityMultiplier() * 2 * scale, 0, 0)) )
		cmd.parent( plane, self.head, relative=True )

		cmd.parent( listRelatives( plane, shapes=True, pa=True ), self.head, add=True, shape=True )
		delete( plane )
	def buildItemVolume( self, item, size, centre ):
		chainLength = rigUtils.chainLength( self.base, self.end )

		height = float( size[0] )
		width = chainLength / 2.0  #denominator is arbitrary - tune it to whatever...

		if rigUtils.apiExtensions.cmpNodes( item, self.end ):  #if the item is the head (ie the last joint in the part's chain) handle it differently
			w, h, d = width, width*1.2, width*1.3
			geo = polySphere( r=0.1, ax=BONE_AIM_VECTOR, sx=8, sy=4, ch=True )[0]
			setAttr( '%s.t' % geo, w, 0, d )
		else:
			geo = polyCylinder( h=height * 0.95, r=0.01, ax=BONE_AIM_VECTOR, sx=self.AUTO_VOLUME_SIDES, sy=round( height/width ), ch=True )[0]
			setAttr( '%s.t' % geo, *centre )

			#finally remove the top and bottom cylinder caps - they're always the last 2 faces
			numFaces = meshUtils.numFaces( geo )
			delete( '%s.f[ %d:%d ]' % (geo, numFaces-2, numFaces-1) )

		parent( geo, item, r=True )

		return [geo]


#end
