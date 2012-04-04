
from baseSkeletonBuilder import *


class Spine(SkeletonPart):
	HAS_PARITY = False

	@classmethod
	def _build( cls, parent=None, count=3, direction='y', **kw ):
		idx = kw[ 'idx' ]
		partScale = kw[ 'partScale' ]

		parent = getParent( parent )
		directionAxis = Axis.FromName( direction )

		allJoints = []
		prevJoint = str( parent )
		posInc = float( partScale ) / 2 / (count + 2)
		moveList = list( directionAxis.asVector() * posInc )
		for n in range( count ):
			j = createJoint( 'spine%s%d' % ('' if idx == 0 else '%d_' % idx, n+1) )
			cmd.parent( j, prevJoint, relative=True )
			move( moveList[0], moveList[1], moveList[2], j, r=True, ws=True )
			allJoints.append( j )
			prevJoint = j

		jointSize( j, 2 )

		return allJoints
	def _align( self, _initialAlign=False ):
		for n, item in enumerate( self[ :-1 ] ):
			alignAimAtItem( item, self[ n+1 ] )

		#if there is a head part parented to this part, then use it as a look at for the end joint
		childParts = self.getChildParts()
		hasHeadPartAsChild = False
		headPart = None

		HeadCls = SkeletonPart.GetNamedSubclass( 'Head' ) or type( None )
		for p in childParts:
			if isinstance( p, HeadCls ):
				headPart = p
				break

		if headPart is None:
			autoAlignItem( self.end )
		else:
			alignAimAtItem( self.end, headPart.base )


#end
