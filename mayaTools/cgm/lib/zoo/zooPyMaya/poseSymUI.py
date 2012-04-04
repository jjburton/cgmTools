
import os

import maya.cmds as cmd

from baseMelUI import *
from zooPy.path import Path

import poseSym
import mayaDecorators


class PoseSymLayout(MelVSingleStretchLayout):

	ICONS = ICON_SWAP, ICON_MIRROR, ICON_MATCH = ( Path(__file__).up() / 'poseSym_swap.png',
	                                               Path(__file__).up() / 'poseSym_mirror.png',
	                                               Path(__file__).up() / 'poseSym_match.png' )

	def __init__( self, parent ):
		self.UI_swap = swap = MelIconButton( self, label='swap pose', style='iconAndTextCentered', align='left', h=30, c=self.on_swap )
		swap.setImage( self.ICON_SWAP )

		self.UI_mirror = mirror = MelIconButton( self, label='mirror pose', style='iconAndTextCentered', align='left', h=30, c=self.on_mirror )
		mirror.setImage( self.ICON_MATCH )

		spacer = MelSpacer( self )

		hLayout = MelHLayout( self )
		MelLabel( hLayout, l='mirror: ' )
		self.UI_mirror_t = MelCheckBox( hLayout, l='translate', v=1 )
		self.UI_mirror_r = MelCheckBox( hLayout, l='rotate', v=1 )
		self.UI_mirror_other = MelCheckBox( hLayout, l='other', v=1 )
		hLayout.layout()

		self.setStretchWidget( spacer )
		self.layout()

	### EVENT HANDLERS ###
	@mayaDecorators.d_unifyUndo
	def on_swap( self, *a ):
		cmdStack = poseSym.CommandStack()
		for pair, obj in poseSym.iterPairAndObj( cmd.ls( sl=True ) ):
			pair.swap( t=self.UI_mirror_t.getValue(), r=self.UI_mirror_r.getValue(), other=self.UI_mirror_other.getValue(), cmdStack=cmdStack )

		cmdStack.execute()
	@mayaDecorators.d_unifyUndo
	def on_mirror( self, *a ):
		for pair, obj in poseSym.iterPairAndObj( cmd.ls( sl=True ) ):
			pair.mirror( obj==pair.controlA, t=self.UI_mirror_t.getValue(), r=self.UI_mirror_r.getValue(), other=self.UI_mirror_other.getValue() )
	@mayaDecorators.d_unifyUndo
	def on_match( self, *a ):
		for pair, obj in poseSym.iterPairAndObj( cmd.ls( sl=True ) ):
			pair.match( obj==pair.controlA, t=self.UI_mirror_t.getValue(), r=self.UI_mirror_r.getValue(), other=self.UI_mirror_other.getValue() )


class PoseSymWindow(BaseMelWindow):
	WINDOW_NAME = 'PoseSymTool'
	WINDOW_TITLE = 'Pose Symmetry Tool'

	DEFAULT_SIZE = 250, 130
	DEFAULT_MENU = 'Setup'

	HELP_MENU = 'zooPoseSym', None, 'http://www.macaronikazoo.com/?page_id=824'

	FORCE_DEFAULT_SIZE = True

	def __init__( self ):
		self.editor = PoseSymLayout( self )
		self.setupMenu()
		self.show()
	def setupMenu( self ):
		menu = self.getMenu( 'Setup' )

		menu.clear()

		MelMenuItem( menu, l='Create Paired Relationship', ann='Will put the two selected objects into a "paired" relationship - they will know how to mirror/exchange poses with one another', c=self.on_setupPair )
		MelMenuItem( menu, l='Create Singular Relationship On Selected', ann='Will setup each selected control with a mirror node so it knows how to mirror poses on itself', c=self.on_setupSingle )
		MelMenuItemDiv( menu )
		MelMenuItem( menu, l='Auto Setup Skeleton Builder', ann='Tries to determine mirroring relationships from skeleton builder', c=self.on_setupSingle )

	### EVENT HANDLERS ###
	def on_setupPair( self, *a ):
		sel = cmd.ls( sl=True, type='transform' )
		if len( sel ) == 1:
			pair = poseSym.ControlPair.Create( sel[0] )
			cmd.select( pair.node )
		elif len( sel ) >= 2:
			pair = poseSym.ControlPair.Create( sel[0], sel[1] )
			cmd.select( pair.node )
	def on_setupSingle( self, *a ):
		sel = cmd.ls( sl=True, type='transform' )
		nodes = []
		for s in sel:
			pair = poseSym.ControlPair.Create( s )
			nodes.append( pair.node )

		cmd.select( nodes )
	def on_setupSkeletonBuilder( self, *a ):
		import rigPrimitives
		rigPrimitives.setupMirroring()


#end
