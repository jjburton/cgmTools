
from baseSkeletonBuilder import *


class Arm(SkeletonPart):
	HAS_PARITY = True

	@classmethod
	def _build( cls, parent=None, buildClavicle=True, **kw ):
		idx = Parity( kw[ 'idx' ] )
		partScale = kw[ 'partScale' ]

		parent = getParent( parent )

		allJoints = []
		dirMult = idx.asMultiplier()
		parityName = idx.asName()
		if buildClavicle:
			clavicle = createJoint( 'clavicle%s' % parityName )
			cmd.parent( clavicle, parent, relative=True )
			move( dirMult * partScale / 50.0, partScale / 10.0, partScale / 25.0, clavicle, r=True, ws=True )
			allJoints.append( clavicle )
			parent = clavicle

		bicep = createJoint( 'bicep%s' % parityName )
		cmd.parent( bicep, parent, relative=True )
		move( dirMult * partScale / 10.0, 0, 0, bicep, r=True, ws=True )

		elbow = createJoint( 'elbow%s' % parityName )
		cmd.parent( elbow, bicep, relative=True )
		move( dirMult * partScale / 5.0, 0, -partScale / 20.0, elbow, r=True, ws=True )

		wrist = createJoint( 'wrist%s' % parityName )
		cmd.parent( wrist, elbow, relative=True )
		move( dirMult * partScale / 5.0, 0, partScale / 20.0, wrist, r=True, ws=True )

		setAttr( '%s.rz' % bicep, dirMult * 45 )

		jointSize( bicep, 2 )
		jointSize( wrist, 2 )

		return allJoints + [ bicep, elbow, wrist ]
	def _buildPlacers( self ):
		return []
	def visualize( self ):
		scale = self.getBuildScale() / 10.0

		plane = polyCreateFacet( ch=False, tx=True, s=1, p=((0, 0, -scale), (0, 0, scale), (self.getParityMultiplier() * 2 * scale, 0, 0)) )
		cmd.parent( plane, self.wrist, relative=True )

		cmd.parent( listRelatives( plane, shapes=True, pa=True ), self.wrist, add=True, shape=True )
		delete( plane )
	@property
	def clavicle( self ): return self[ 0 ] if len( self ) > 3 else None
	@property
	def bicep( self ): return self[ -3 ]
	@property
	def elbow( self ): return self[ -2 ]
	@property
	def wrist( self ): return self[ -1 ]
	def _align( self, _initialAlign=False ):
		parity = self.getParity()

		normal = getPlaneNormalForObjects( self.bicep, self.elbow, self.wrist )
		normal *= parity.asMultiplier()

		if self.clavicle:
			parent = getNodeParent( self.clavicle )
			if parent: alignAimAtItem( self.clavicle, self.bicep, parity, upType='objectrotation', worldUpObject=parent, worldUpVector=MAYA_FWD  )

		alignAimAtItem( self.bicep, self.elbow, parity, worldUpVector=normal )
		alignAimAtItem( self.elbow, self.wrist, parity, worldUpVector=normal )

		if _initialAlign:
			autoAlignItem( self.wrist, parity, worldUpVector=normal )
		else:
			alignPreserve( self.wrist )

		for i in self.getOrphanJoints():
			alignItemToLocal( i )
	def getIkFkItems( self ):
		return self.bicep, self.elbow, self.wrist


#end
