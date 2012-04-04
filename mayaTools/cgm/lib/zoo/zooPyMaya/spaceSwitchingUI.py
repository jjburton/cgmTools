
from maya.cmds import *
from maya import cmds as cmd
from baseMelUI import *

from zooPy import names

import control
import baseMelUI
import spaceSwitching


class ParentsScrollList(MelObjectScrollList):
	def itemAsStr( self, item ):
		return '%s :: %s' % tuple( item )


class SpaceSwitchingLayout(MelVSingleStretchLayout):
	def __init__( self, parent, *a, **kw ):
		MelVSingleStretchLayout.__init__( self, parent, expand=True, *a, **kw )


		w = 130
		hLayout = MelHSingleStretchLayout( self )
		self.UI_controlBtn = UI_controlBtn = MelButton( hLayout, l='obj to space switch ->', w=w, c=self.on_loadControl )
		self.UI_control = UI_control = MelNameField( hLayout )
		hLayout.setStretchWidget( UI_control )
		hLayout.layout()


		hLayout = MelHSingleStretchLayout( self )
		self.UI_spaceBtn = UI_spaceBtn = MelButton( hLayout, l='obj to constrain ->', w=w, c=self.on_loadSpace )
		self.UI_space = UI_space = MelNameField( hLayout )
		hLayout.setStretchWidget( UI_space )
		hLayout.layout()


		hLayout = MelHLayout( self )
		self.UI_constrainT = UI_constrainT = MelCheckBox( hLayout, l='constrain translation', v=True, cc=self.on_constrainChange )
		self.UI_constrainR = UI_constrainR = MelCheckBox( hLayout, l='constrain rotation', v=True, cc=self.on_constrainChange )
		self.UI_constraintType = UI_constraintType = MelOptionMenu( hLayout )
		hLayout.layout()


		#populate the option menu with the constraint types
		for constraintType in spaceSwitching.CONSTRAINT_TYPES:
			UI_constraintType.append( constraintType )


		### PARENTS LIST ###
		self.UI_parentsLbl = UI_parentsLbl = MelLabel( self, l='Parents  (double click to rename)', align='center' )

		hLayout = MelHSingleStretchLayout( self, expand=True )
		self.UI_parents = UI_parents = ParentsScrollList( hLayout, dcc=self.on_renameParent )

		upDnLayout = MelVLayout( hLayout )
		self.UI_up = UI_up = MelButton( upDnLayout, l='up', c=self.on_up )
		self.UI_dn = UI_dn = MelButton( upDnLayout, l='dn', c=self.on_dn )
		upDnLayout.layout()

		hLayout.setStretchWidget( UI_parents )
		hLayout.layout()

		self.setStretchWidget( hLayout )


		### ADD/REMOVE PARENTS BUTTONS ###
		hLayout = MelHLayout( self )
		self.UI_addParent = UI_addParent = MelButton( hLayout, l='add parent', c=self.on_addParent )
		self.UI_remParent = UI_remParent = MelButton( hLayout, l='remove parent', c=self.on_removeParent )
		self.UI_removeAll = UI_removeAll = MelButton( hLayout, l='remove all', c=self.on_removeAll )
		hLayout.layout()

		self.UI_build = UI_build = MelButton( self, l='build space switch', c=self.on_build )


		### DO FINAL LAYOUT ###
		self.layout()
		self.setSceneChangeCB( self.on_sceneChange )
		self.update()
	def update( self ):
		setEnabled = bool( self.getControl() and self.getSpace() )

		self.UI_addParent.enable( setEnabled )
		self.UI_remParent.enable( setEnabled )
		self.UI_removeAll.enable( setEnabled )

		self.UI_build.enable( setEnabled )

		if not self.UI_constrainT.getValue() and not self.UI_constrainR.getValue():
			self.UI_build.enable( False )

		if not self.UI_parents.getItems():
			self.UI_build.enable( False )
	def setControl( self, control ):
		self.UI_space.clear()
		self.UI_control.setObj( control )
		self.UI_parents.clear()

		self.update()
	def getControl( self ):
		return self.UI_control.getObj()
	def setSpace( self, space ):
		self.UI_space.setObj( space )
		self.update()
	def getSpace( self ):
		return self.UI_space.getObj()
	def addParent( self, parent, name=None ):
		#sanity check - make sure the parent isn't either the control, the space, already in the list or a child of either the control or space
		if parent == self.getControl():
			return
		elif parent == self.getSpace():
			return

		if name is None:
			name = spaceSwitching.getSpaceName( self.getControl(), parent )
			if name is None:
				name = names.camelCaseToNice( str( parent ) )

		self.UI_parents.append( [parent, name] )

	### EVENT HANDLERS ###
	def on_loadControl( self, *a ):
		selected = ls( sl=True )
		if selected:
			theControl = selected[ 0 ]

			self.setControl( theControl )

			space = spaceSwitching.findSpace( theControl )

			#if there is an existing space for the control, use it - otherwise try to guess one
			if space:
				self.setSpace( space )
			else:
				space = listRelatives( theControl, p=True, pa=True )
				if space:
					self.setSpace( space[0] )

			parents, names = spaceSwitching.getSpaceTargetsNames( theControl )
			for parent, name in zip( parents, names ):
				self.addParent( parent, name )

		self.update()
	def on_loadSpace( self, *a ):
		selected = ls( sl=True )
		if selected:
			theSpace = selected[ 0 ]
			self.setSpace( theSpace )

		self.update()
	def on_constrainChange( self, *a ):
		self.update()
	def on_addParent( self, *a ):
		selected = ls( sl=True )
		for item in selected:
			self.addParent( item )

		self.update()
	def on_removeParent( self, *a ):
		self.UI_parents.removeSelectedItems()
		self.update()
	def on_removeAll( self, *a ):
		self.UI_parents.clear()
		self.update()
	def on_renameParent( self, *a ):
		selItems = self.UI_parents.getSelectedItems()
		if selItems:
			theItem = selItems[ 0 ]
			ret = cmd.promptDialog( t='Enter a name', m='Enter the name you want the parent to appear as', tx=theItem[1], b=('OK', 'Cancel'), db='OK' )
			if ret == 'OK':
				theItem[ 1 ] = cmd.promptDialog( q=True, tx=True )
				self.UI_parents.update()
	def on_up( self, *a ):
		self.UI_parents.moveSelectedItemsUp()
	def on_dn( self, *a ):
		self.UI_parents.moveSelectedItemsDown()
	def on_sceneChange( self, *a ):
		self.UI_control.clear()
		self.UI_space.clear()
		self.UI_parents.clear()
		self.update()
	def on_build( self, *a ):
		theControl = self.getControl()
		theSpace = self.getSpace()

		for parent, name in self.UI_parents.getItems():
			spaceSwitching.add( theControl, parent,
			                    name=name, space=theSpace,
			                    skipTranslationAxes=() if self.UI_constrainT.getValue() else ('x', 'y', 'z'),
			                    skipRotationAxes=() if self.UI_constrainR.getValue() else ('x', 'y', 'z'),
			                    constraintType=self.UI_constraintType.getValue() )
		#spaceSwitching.build( self.getControl(), parents, names=parentNames, space=self.getSpace() )


class SpaceSwitchingWindow(BaseMelWindow):
	WINDOW_NAME = 'spaceSwitchingWindow'
	WINDOW_TITLE = 'Space Switching'

	DEFAULT_SIZE = 400, 350
	DEFAULT_MENU = None
	#HELP_MENU = 'spaceSwitching', 'hamish@macaronikazoo.com', None

	FORCE_DEFAULT_SIZE = True

	def __init__( self ):
		self.editor = SpaceSwitchingLayout( self )
		self.show()


#end
