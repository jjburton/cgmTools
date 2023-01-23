
from maya import standalone
standalone.initialize()

from maya.cmds import *

from devTest_base import d_makeNewScene, BaseTest

import skeletonBuilder
import skeletonBuilderUI

import rigPrimitives

__all__ = [ 'TestSkeletonBuilder' ]

#PERFORM_RELOAD = False

SkeletonPart = skeletonBuilder.SkeletonPart
Root = SkeletonPart.GetNamedSubclass( 'Root' )
Spine = SkeletonPart.GetNamedSubclass( 'Spine' )
Head = SkeletonPart.GetNamedSubclass( 'Head' )
Arm = SkeletonPart.GetNamedSubclass( 'Arm' )
Hand = SkeletonPart.GetNamedSubclass( 'Hand' )
Leg = SkeletonPart.GetNamedSubclass( 'Leg' )
QuadrupedFrontLeg = SkeletonPart.GetNamedSubclass( 'QuadrupedFrontLeg' )
ArbitraryChain = SkeletonPart.GetNamedSubclass( 'ArbitraryChain' )
ArbitraryParityChain = SkeletonPart.GetNamedSubclass( 'ArbitraryParityChain' )


class TestSkeletonBuilder(BaseTest):
	def runTest( self ):
		self.testUberSkeleton()
		self.testUberSkeletonAndReferencing()
		self.testUI()
	def _buildTestSkeleton( self ):
		allPartClasses = [ part for part in SkeletonPart.GetSubclasses() if part.AVAILABLE_IN_UI ]

		#now remove the ones we're going to create manually
		for part in (Root, Spine, Head, Arm, Leg):
			allPartClasses.remove( part )

		scale = 100

		root = Root.Create( partScale=scale )

		theSpine = Spine.Create( root, 5, partScale=scale )
		theHead = Head.Create( theSpine.end, 2, partScale=scale )
		armL = Arm.Create( theSpine.end, partScale=scale )
		armR = Arm.Create( theSpine.end, partScale=scale )
		legL = Leg.Create( root, partScale=scale )
		legR = Leg.Create( root, partScale=scale )

		armL.driveOtherPart( armR )
		legL.driveOtherPart( legR )

		handL = Hand.Create( armL.wrist )
		handR = Hand.Create( armR.wrist )

		quadSpine = ArbitraryChain.Create( root, 'quadSpine', 6, '-z' )
		ArbitraryChain.Create( theHead.end, 'hair1', 3, 'x' )
		ArbitraryChain.Create( theHead.end, 'hair2', 3, '-x' )

		backlegA = QuadrupedFrontLeg.Create( quadSpine[-1] )
		backlegB = QuadrupedFrontLeg.Create( quadSpine[-1] )

		quadSpine = ArbitraryChain.Create( quadSpine[-1], 'tail', 4, '-z' )

		#make sure skeleton builder can now enumerate the parts it just created
		partsCreated = list( SkeletonPart.IterAllParts() )
		assert len( partsCreated ) == 15, "Iterating over parts just created failed!"
	def testUberSkeleton( self ):
		'''
		Test that a simple scene gets setup and exports properly
		'''
		self.new()
		self._buildTestSkeleton()
		skeletonBuilder.finalizeAllParts()
		rigPrimitives.buildRigForAllParts()  #build the rig within the current scene
	@d_makeNewScene( 'testUberSkeleton_mesh' )
	def testUberSkeletonAndReferencing( self ):
		'''
		Test that a simple scene gets setup and exports properly
		'''
		self._buildTestSkeleton()
		rigScene = rigPrimitives.buildRigForModel()  #build the model in a referenced scene

		assert rigScene.exists(), "Cannot find the rig scene!"
		rigScene.delete()
	def testUI( self ):
		'''
		Test that a simple scene gets setup and exports properly
		'''

		#can't test the UI in batch mode...
		if about( batch=True ):
			return

		self.new()
		self._buildTestSkeleton()

		#test the UI - make sure it loads and doesn't error with the built skeleton in the scene
		ui = skeletonBuilderUI.SkeletonBuilderUI()
		tabs = skeletonBuilderUI.CreateEditRigTabLayout.IterInstances().next()

		#walk through the tabs
		for n in range( len( tabs ) ):
			tabs.setSelectedTabIdx( n )


#end
