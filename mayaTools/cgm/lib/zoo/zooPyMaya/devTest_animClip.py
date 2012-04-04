
from maya.cmds import *

import devTest_base

from zooPy import strUtils
from zooPy import vectors

import mayaDecorators
import animClip

#world space keyTime/translation/rotation data for creating the animated test data
KEY_DATA = ( (0, (1,1,1), (-10, 15, 45)),
             (10, (2,3,4), (39,64,72)),
             (12, (3,3,6), (62,73,65)),
             (15, (4,5,6), (35,79,42)),
             (17, (6,7,8), (12,134,9)),
             (23, (3,3,1), (-5,154,-12)),
             (29, (3,4,4), (-15,104,-8)),
             (35, (5,5,6), (-3,99,-3)),
             (43, (3,6,4), (0,42,-1)),
             (56, (4,2,0), (-2,63,-2)),
             )


class TestAnimClip(devTest_base.BaseTest):
	def runTest( self ):
		self.testTracer()
	def testTracer( self ):
		sphere = self.createAnimatedSphere()
		cube = self.createCube()

		tracer = animClip.Tracer()
		mapping = strUtils.Mapping( [sphere], [cube] )
		tracer.apply( mapping )

		keyServer = animClip.NodeKeyServer( [sphere, cube] )
		for keyTime in keyServer:
			if keyTime is None:
				continue

			nodes = keyServer.getNodes()
			assert sphere in nodes and cube in nodes

			#cast to vectors as the vector comparison test deals with floating point shinanigans
			posA = vectors.Vector( xform( sphere, q=True, ws=True, rp=True ) )
			posB = vectors.Vector( xform( cube, q=True, ws=True, rp=True ) )
			assert posA == posB
	def testPoseClip( self ): pass
	def testAnimClip( self ): pass
	def testChannelsClip( self ): pass
	def testTransformClip( self ): pass
	def testCurveDuplicator( self ): pass
	@mayaDecorators.d_noAutoKey
	def applyAnimationData( self, node ):
		for keyTime, pos, rot in KEY_DATA:
			currentTime( keyTime )
			move( pos[0], pos[1], pos[2], node, a=True, ws=True )
			rotate( rot[0], rot[1], rot[2], node, a=True, ws=True )
			setKeyframe( node, at=('t', 'r') )
	def createAnimatedSphere( self ):
		theSphere = sphere()[0]
		self.applyAnimationData( theSphere )

		return theSphere
	def createCube( self ):
		theCube = polyCube( ch=False )[0]
		move( 1, -1, 2, theCube )
		makeIdentity( theCube, a=True, t=True, r=True )

		return theCube


#end
