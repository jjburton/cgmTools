
import maya.cmds as cmd

from zooPy import events
from zooPy.misc import removeDupes, Callback
from zooPy.vectors import Colour

from triggered import *
from baseMelUI import *

import triggered
import triggeredPresets
import spaceSwitching
import posesToSliders


def buildMenuItems( parent, obj ):
	'''
	build the menuItems in the dagProcMenu - it is possible to set a "kill menu" attribute
	on an object now that will stop the dagMenu building after the objMenu items have been
	added
	'''

	defaultCmdName = "<empty cmd>"
	menusFromConnects = False
	killState = False

	objs = [ obj ] + (listRelatives( obj, pa=True, s=True ) or [])

	#the showMenusFromConnects attribute determines whether the object in question should show right click menus from any items connected to this one via triggered connects
	if objExists( '%s.showMenusFromConnects' % obj ):
		menusFromConnects = getAttr( '%s.showMenusFromConnects' % obj )

	if menusFromConnects:
		connects = Trigger( obj ).connects()
		for connectObj, connectIdx in connects:
			objs.append( connectObj )

	objs = removeDupes( objs )

	#now get a list of objs that have menus - if there are more than one, build section labels, otherwise skip labels
	objsWithMenus = []
	for obj in objs:
		obj = Trigger( obj )
		if obj.menus():
			objsWithMenus.append( obj )

	doLabels = len( objsWithMenus ) > 1

	setParent( parent, m=True )
	for obj in objsWithMenus:

		#if ANY of the objs have the kill state set, turn it on
		if getKillState( obj ):
			killState = True

		tgts, names = spaceSwitching.getSpaceTargetsNames( obj )
		names = [ 'parent to %s' % name for name in names ]
		if objExists( '%s.parent' % obj ):
			curIdx = getAttr( '%s.parent' % obj )
		else: curIdx = None

		if doLabels:
			menuItem( l='---%s Menus---' % str( obj ).split( '|' )[-1].split( ':' )[-1], en=False )

		for idx, cmdName, cmdStr in obj.menus( True ):

			#we need to construct the menu item using mel - because the tool was originally mel and all existing obj menu commands are written in mel
			#so you have to construct the menu item in mel otherwise its assumed the command is python...
			menuCmdToks = [ 'menuItem -l "%s"' % (cmdName or defaultCmdName) ]

			#so if the menu name starts with "parent to " then it assumed to be a menu item built by zooSpaceSwitching
			if cmdStr.startswith( "^parent to " ):
				if curIdx is not None:
					if idx == curIdx:
						menuCmdToks( '-cb 1' )

			if cmdStr:
				menuCmdToks.append( '-c "%s"' % encodeString(cmdStr) )

			mel.eval( ' '.join( menuCmdToks ) )

	#should we die after menu build?
	if not killState:
		menuItem( d=True )
		menuItem( d=True )

	return killState


CMD_PRESETS = { 'selectConnected': "select -d #;\nselect -add @;",
                'keyConnected': "select -d #;\nsetKeyframe @;",
                'toggleConnected': "string $sel[] = `ls -sl`;\nint $vis = !`getAttr %1.v`;\nfor($obj in @) setAttr ($obj +\".v\") $vis;\nif( `size $sel` ) select $sel;",
                'toolToMove': "setToolTo $gMove;",
                'toolToRotate': "setToolTo $gRotate;", }


def writeSetAttrCmd( trigger, connectIdxs=None ):
	cmdToks = []
	assert isinstance( trigger, Trigger )

	if connectIdxs is None:
		connectIdxs = [ idx for _,idx in trigger.connects() ]

	#make sure the zeroth connect isn't in the list and remove duplicates
	connectIdxs = removeDupes( connectIdxs )
	if 0 in connectIdxs:
		connectIdxs.remove( 0 )

	for connectIdx in connectIdxs:
		obj = trigger[connectIdx]
		attrs = cmd.listAttr( obj, k=True, s=True, v=True, m=True ) or []
		objTrigger = Trigger( obj )
		for a in attrs:
			attrPath = '%s.%s' % (obj, a)
			attrType = cmd.getAttr( attrPath, type=True )
			attrValue = cmd.getAttr( attrPath )
			if attrType.startswith( 'double' ):
				cmdToks.append( "setAttr %%%d.%s %0.5f;" % (connectIdx, a, attrValue) )
			else:
				cmdToks.append( "setAttr %%%d.%s %d;" % (connectIdx, a, attrValue) )

	return '\n'.join( cmdToks )


class MenuList(MelObjectScrollList):
	def itemAsStr( self, item ):
		menuName, menuCmd = self._trigger.getMenuInfo( item )
		return menuName
	def setTrigger( self, trigger ):
		self._trigger = trigger
		self.clear()
		self.update()
	def update( self ):
		if self._trigger is None:
			return

		items = [ mIdx for mIdx, mName, mCmd in self._trigger.menus() ]
		preSelection = self.getSelectedItems()
		self.setItems( items )
		if preSelection:
			self.selectByValue( preSelection[0] )
		elif items:
			self.selectByIdx( 0, True )


class TriggeredWindow(BaseMelWindow):
	WINDOW_NAME = 'zooTriggeredWindow'
	WINDOW_TITLE = 'zooTriggered!    ::macaroniKazoo::'

	DEFAULT_SIZE = 700, 450

	def __init__( self ):
		mainLayout = MelVSingleStretchLayout( self )
		mainLayout.setPadding( 1 )

		hLayout = MelHRowLayout( mainLayout )

		h, w = 18, 85
		MelButton( hLayout, l='load', height=h, width=w, c=lambda *a: triggered.Triggered().load() )
		MelButton( hLayout, l='unload', height=18, width=w, c=lambda *a: triggered.Triggered().unload() )
		MelLabel( hLayout, l='load status ->', height=h, width=w, align='center' )
		self.UI_state = MelPalette( hLayout, ed=False, height=h, width=w, dim=(1, 1) )
		hLayout.layout()

		paneLayout = MelPaneLayout( mainLayout, MelPaneLayout.CFG_HORIZ2 )
		mainLayout.setStretchWidget( paneLayout )

		hLayout = MelHLayout( paneLayout )
		vLayout = MelVSingleStretchLayout( hLayout )
		triggerLbl = MelLabel( vLayout, l='triggers:' )

		self.UI_triggerList = MelObjectScrollList( vLayout, ams=False, sc=self.on_triggerHighlighted )

		hTriggerLayout = MelHLayout( vLayout )
		self.UI_highlightTrigger = MelButton( hTriggerLayout, l='highlight', c=self.on_highlightSelected )
		self.UI_createTrigger = MelButton( hTriggerLayout, l='create', c=self.on_createTrigger )
		self.UI_removeTrigger = MelButton( hTriggerLayout, l='remove', en=False, c=self.on_removeTrigger )
		hTriggerLayout.layout()

		vLayout.setStretchWidget( self.UI_triggerList )
		vLayout.setPadding( 1 )
		vLayout.layout()

		vLayout = MelVSingleStretchLayout( hLayout )
		MelLabel( vLayout, l='connects:' )

		self.UI_connectsList = MelObjectScrollList( vLayout, ams=True, sc=self.on_connectHighlighted )
		self.MENU_connects = MelPopupMenu( self.UI_connectsList, pmc=self.buildConnectsMenu )

		hTriggerLayout = MelHLayout( vLayout )
		self.UI_highlightConnect = MelButton( hTriggerLayout, l='highlight', c=self.on_highlightConnect )
		self.UI_createConnect = MelButton( hTriggerLayout, l='connect', c=self.on_createConnect )
		self.UI_removeConnect = MelButton( hTriggerLayout, l='disconnect', en=False, c=self.on_removeConnect )
		hTriggerLayout.layout()

		vLayout.setStretchWidget( self.UI_connectsList )
		vLayout.setPadding( 1 )
		vLayout.layout()

		hLayout.setExpand( True )
		hLayout.setPadding( 0 )
		hLayout.layout()

		hLayout = MelHSingleStretchLayout( paneLayout )
		hLayout.setExpand( True )
		self.UI_menuListLayout = vMenuLayout = MelVSingleStretchLayout( hLayout )

		self.UI_menuList = MenuList( vMenuLayout, sc=self.on_menuHighlighted, w=185 )

		hMenuButtonLayout = MelHLayout( vMenuLayout )
		self.UI_createMenu = MelButton( hMenuButtonLayout, l='create', c=self.on_createMenu )
		self.UI_createMenu = MelButton( hMenuButtonLayout, l='delete', c=self.on_deleteMenu )
		hMenuButtonLayout.setPadding( 0 )
		hMenuButtonLayout.layout()

		vMenuLayout.setStretchWidget( self.UI_menuList )
		vMenuLayout.setPadding( 0 )
		vMenuLayout.layout()

		vLayout = MelVSingleStretchLayout( hLayout )
		self.UI_menuNameLayout = hMenuLayout = MelHSingleStretchLayout( vLayout )
		self.UI_menuNameLbl = MelLabel( hMenuLayout, l='menu name:' )
		self.UI_menuName = MelTextField( hMenuLayout, cc=self.on_editMenuName )
		self.UI_killState = MelCheckBox( hMenuLayout, l='minimal menu', cc=self.on_killState )
		hMenuLayout.setStretchWidget( self.UI_menuName )
		hMenuLayout.layout()

		self.UI_cmdEditor = MelScrollField( vLayout, ed=True, nl=6, cc=self.on_editCmd, ec=self.on_editCmd )
		self.MENU_cmdEditor = MelPopupMenu( self.UI_cmdEditor, pmc=self.buildCmdEditorMenu )

		hChecksLayout = MelHRowLayout( vLayout )
		self.UI_previewCheck = MelCheckBox( hChecksLayout, l='preview command string', cc=self.on_preview )
		#self.UI_filteredCheck = MelCheckBox( hChecksLayout, l='show cmd relevant to selected connects', cc=self.on_filterCmd )
		hChecksLayout.layout()

		vLayout.setStretchWidget( self.UI_cmdEditor )
		vLayout.setPadding( 2 )
		vLayout.layout()

		hLayout.setStretchWidget( vLayout )
		hLayout.layout()

		mainLayout.layout()

		self.on_sceneSelectionChange()

		#register callbacks as appropriate
		self.setSelectionChangeCB( self.on_sceneSelectionChange )
		self.setSceneChangeCB( self.on_sceneChange )

		#update the UI and populate it with stuff
		self.buildMainMenus()
		self.updateLayout()
		self.updateLoadState()
		self.populateTriggers()

		self.show()
	def buildMainMenus( self ):
		viewMenu = self.getMenu( 'View' )
		viewMenu( e=True, pmc=self.buildViewMenu )

		presetsMenu = self.getMenu( 'Presets' )
		MelMenuItem( presetsMenu, l='export trigger preset', c=self.on_exportTrigger )
		MelMenuItemDiv( presetsMenu )
		self.MENU_import = MelMenuItem( presetsMenu, l='import trigger preset', sm=True, pmc=self.buildImportPresetMenu )
	def clear( self ):
		self.UI_connectsList.clear()
		self.UI_menuList.clear()
		self.UI_cmdEditor.clear( False )
		self.UI_menuName.clear( False )
		self.UI_killState.setValue ( False, False )
	def updateLayout( self ):
		cmdViewMode = cmd.optionVar( q='zooTrigViewMode' )
		if cmdViewMode == 0:
			triggers = Trigger.All( True, False )
			self.UI_menuListLayout.setVisibility( False )
			self.UI_menuNameLayout.setVisibility( False )
		elif cmdViewMode == 1:
			self.UI_menuListLayout.setVisibility( True )
			self.UI_menuNameLayout.setVisibility( True )
	def updateCmds( self ):
		selTrigger = self.UI_triggerList.getSelectedItems()
		if selTrigger:
			selTrigger = selTrigger[0]
			cmdViewMode = cmd.optionVar( q='zooTrigViewMode' )
			self.UI_killState.setValue( selTrigger.getKillState() )

			preview = self.UI_previewCheck.getValue()
			self.UI_cmdEditor.setEditable( not preview )

			if cmdViewMode == 0:
				cmdStr = selTrigger.getCmd( resolve=preview )
				self.UI_cmdEditor.setValue( cmdStr )
			elif cmdViewMode == 1:
				menuIdxs = self.UI_menuList.getSelectedItems()
				if menuIdxs:
					cmdStr = selTrigger.getMenuCmd( menuIdxs[0], resolve=preview )
					self.UI_cmdEditor.setValue( cmdStr )
					self.UI_menuName.setValue( selTrigger.getMenuName( menuIdxs[0] ) )

		else:
			self.UI_cmdEditor.setValue( '' )
	def updateLoadState( self ):
		state = Triggered().state()
		if state:
			self.UI_state.setColour( Colour( 'green' ) )
		else:
			self.UI_state.setColour( Colour( 'grey' ) )
	def populateTriggers( self ):
		cmdViewMode = cmd.optionVar( q='zooTrigViewMode' )
		if cmdViewMode == 0:
			triggers = Trigger.All( True, False )
		elif cmdViewMode == 1:
			triggers = Trigger.All( False, True )

		preSelection = self.UI_triggerList.getSelectedItems()
		self.UI_triggerList.setItems( triggers )
		if triggers:
			if preSelection:
				self.UI_triggerList.selectByValue( preSelection[0], True )
			else:
				self.UI_triggerList.selectByIdx( 0, True )
		else:
			self.populateConnects()
			self.updateCmds()
	def populateConnects( self ):
		selTrigger = self.UI_triggerList.getSelectedItems()
		if selTrigger:
			preSelection = self.UI_connectsList.getSelectedItems()

			selTrigger = selTrigger[0]
			self.UI_connectsList.setItems( [ nodeName for nodeName, connectIdx in selTrigger.connects()[1:] ] )
			for s in preSelection:
				self.UI_connectsList.selectByValue( s, False )
	def populateMenus( self ):
		self.UI_menuList.update()
	def getHighlightedTrigger( self ):
		selTrigger = self.UI_triggerList.getSelectedItems()
		if selTrigger:
			return selTrigger[0]

		return None
	def buildViewMenu( self, *a ):
		cmdViewMode = cmd.optionVar( q='zooTrigViewMode' )
		highlightMode = cmd.optionVar( q='zooTrigHighlighting' )

		viewMenu = self.getMenu( 'View' )
		viewMenu.clear()

		MelMenuItem( viewMenu, l='edit zooTriggered command', cb=not cmdViewMode, c=self.on_switchToTriggered )
		MelMenuItem( viewMenu, l='edit zooObjMenu commands', cb=cmdViewMode, c=self.on_switchToObjMenu )
		MelMenuItem( viewMenu, l='trigger highlighting', cb=highlightMode, c=self.on_highlightModeChange )
	def buildImportPresetMenu( self, *a ):
		cmd.menu( self.MENU_import, e=True, dai=True )
		presetDict = triggeredPresets.listPresets()
		for locale, presets in presetDict.iteritems():
			for preset in presets:
				MelMenuItem( self.MENU_import, l=preset.name(), c=Callback( self.importFilepath, preset.path() ) )
	def buildConnectsMenu( self, *a ):
		selTrigger = self.getHighlightedTrigger()
		if selTrigger:
			cmd.menu( self.MENU_connects, e=True, dai=True )
			MelMenuItem( self.MENU_connects, l='poses to sliders', c=lambda *a: posesToSliders.create( selTrigger ) )
			MelMenuItem( self.MENU_connects, l='poses to sliders (preserve)', c=lambda *a: posesToSliders.create( selTrigger, preserve=True ) )
	def buildCmdEditorMenu( self, *a ):
		previewMode = self.UI_previewCheck.getValue()
		selTrigger = self.getHighlightedTrigger()
		if selTrigger:
			cmd.menu( self.MENU_cmdEditor, e=True, dai=True )
			for presetName, presetContents in CMD_PRESETS.iteritems():
				MelMenuItem( self.MENU_cmdEditor, l=presetName, en=not previewMode, c=Callback( self.UI_cmdEditor.setValue, presetContents ) )

			MelMenuItem( self.MENU_cmdEditor, l='setAttr cmd', en=not previewMode, c=lambda *a: self.UI_cmdEditor.setValue( writeSetAttrCmd( selTrigger ) ) )
	def importFilepath( self, filepath ):
		triggeredPresets.loadFromFilepath( filepath )
		self.populateTriggers()
	def saveCmd( self ):
		selTrigger = self.UI_triggerList.getSelectedItems()
		if selTrigger:
			selTrigger = selTrigger[0]

			cmdViewMode = cmd.optionVar( q='zooTrigViewMode' )
			cmdStr = self.UI_cmdEditor.getValue()
			if cmdViewMode == 0:
				selTrigger.setCmd( cmdStr )
			elif cmdViewMode == 1:
				menuIdx = self.UI_menuList.getSelectedItems()[0]
				selTrigger.setMenuCmd( menuIdx, cmdStr )

	### EVENT HANDLERS ###
	def on_switchToTriggered( self, *a ):
		cmd.optionVar( iv=('zooTrigViewMode', 0) )
		self.updateLayout()
		self.populateTriggers()
	def on_switchToObjMenu( self, *a ):
		cmd.optionVar( iv=('zooTrigViewMode', 1) )
		self.updateLayout()
		self.populateTriggers()
	def on_exportTrigger( self, *a ):
		BUTTONS = OK, CANCEL = 'Ok', 'Cancel'
		ret = cmd.promptDialog( t='Enter preset name', m='Enter a name for the preset file', b=BUTTONS, db=OK )
		if ret == OK:
			name = cmd.promptDialog( q=True, tx=True )
			if name:
				triggeredPresets.writeToPreset( name )
	def on_highlightModeChange( self, *a ):
		highlightMode = cmd.optionVar( q='zooTrigHighlighting' )
		cmd.optionVar( iv=('zooTrigHighlighting', not highlightMode) )
		if highlightMode:
			pass
		else:
			triggered.Triggered().unhighlightAllTriggers()
	def on_editCmd( self, *a ):

		#never save a command if we're in preview mode
		if self.UI_previewCheck.getValue():
			return

		self.saveCmd()
	def on_editMenuName( self, *a ):
		selTrigger = self.UI_triggerList.getSelectedItems()[0]
		menuIdx = self.UI_menuList.getSelectedItems()[0]
		menuName = self.UI_menuName.getValue()
		selTrigger.setMenuName( menuIdx, menuName )
		self.UI_menuList.update()
	def on_triggerHighlighted( self, *a ):
		self.clear()

		selTrigger = self.getHighlightedTrigger()
		self.UI_menuList.setTrigger( selTrigger )
		if selTrigger:
			self.UI_killState.setValue( selTrigger.getKillState() )

		self.populateConnects()
		self.updateCmds()

		highlighted = bool( self.UI_triggerList.getSelectedItems() )
		self.UI_removeTrigger.setEnabled( highlighted )
	def on_connectHighlighted( self, *a ):
		#if self.UI_filteredCheck.getValue():
			#self.updateCmds()

		highlighted = bool( self.UI_triggerList.getSelectedItems() )
		self.UI_removeConnect.setEnabled( highlighted )
	def on_menuHighlighted( self, *a ):
		self.updateCmds()
	def on_createMenu( self, *a ):
		selTrigger = self.getHighlightedTrigger()
		if selTrigger:
			menuIdx = selTrigger.createMenu()
			self.UI_menuList.setTrigger( selTrigger )
			self.UI_menuList.selectByValue( menuIdx, True )
	def on_deleteMenu( self, *a ):
		selTrigger = self.getHighlightedTrigger()
		if selTrigger:
			selMenu = self.UI_menuList.getSelectedItems()
			if selMenu:
				selTrigger.removeMenu( selMenu[0] )
				self.UI_menuList.setTrigger( selTrigger )
				self.updateCmds()
	def on_preview( self, state ):

		#if we're switching into preview mode, force a save of the current command!
		if state:
			self.saveCmd()

		self.updateCmds()
	def on_filterCmd( self, *a ):
		pass
	def on_killState( self, *a ):
		selTrigger = self.UI_triggerList.getSelectedItems()[0]
		selTrigger.setKillState( self.UI_killState.getValue() )
	def on_sceneSelectionChange( self, *a ):
		sel = bool( cmd.ls( sl=True ) )
		self.UI_highlightTrigger.setEnabled( sel )
		self.UI_createTrigger.setEnabled( sel )
		self.UI_highlightConnect.setEnabled( sel )
		self.UI_createConnect.setEnabled( sel )
	def on_sceneChange( self, *a ):
		self.clear()
		self.populateTriggers()
	def on_highlightSelected( self, *a ):
		sel = cmd.ls( sl=True )
		if sel:
			self.UI_triggerList.clearSelection()
			selTrigger = self.UI_triggerList.selectByValue( Trigger( sel[0] ), True )
	def on_createTrigger( self, *a ):
		sel = cmd.ls( sl=True ) or []
		cmdViewMode = cmd.optionVar( q='zooTrigViewMode' )
		for s in sel:
			t = Trigger( s )
			if cmdViewMode == 0:
				t.setCmd()
			elif cmdViewMode == 1:
				t.createMenu()

		self.populateTriggers()
	def on_removeTrigger( self, *a ):
		selTrigger = self.getHighlightedTrigger()
		if selTrigger:
			BUTTONS = YES, NO, CANCEL = 'Yes', 'No', 'Cancel'
			ret = cmd.confirmDialog( t='Remove connects as well?', m='Do you want to remove all disconnects as well?', b=BUTTONS, db=CANCEL )
			if ret == CANCEL:
				return
			elif ret == YES:
				for nodeName,connectIdx in selTrigger.connects():
					selTrigger.disconnect(connectIdx)

			cmdViewMode = cmd.optionVar( q='zooTrigViewMode' )
			cmdStr = self.UI_cmdEditor.getValue()
			if cmdViewMode == 0:
				selTrigger.removeCmd()
			elif cmdViewMode == 1:
				for idx,_a,_b in selTrigger.menus():
					selTrigger.removeMenu(idx)

			self.populateTriggers()
	def on_highlightConnect( self, *a ):
		sel = cmd.ls( sl=True )
		if sel:
			self.UI_connectsList.clearSelection()
			for s in sel:
				selTrigger = self.UI_connectsList.selectByValue( s, True )
	def on_createConnect( self, *a ):
		selTrigger = self.getHighlightedTrigger()
		if selTrigger:
			sel = cmd.ls( sl=True ) or []
			for s in sel:
				selTrigger.connect( s )

			self.populateConnects()
	def on_removeConnect( self, *a ):
		selTrigger = self.getHighlightedTrigger()
		if selTrigger:
			selConnects = self.UI_connectsList.getSelectedItems()
			for c in selConnects:
				selTrigger.disconnect( c )

			self.populateConnects()


def getShelfButtonsWithTag( tag ):
	buttons = []
	shelves = cmd.lsUI( cl=True, type='shelfLayout' ) or []
	for shelf in shelves:
		if not cmd.shelfLayout( shelf, ex=True ):
			continue

		shelfButtons = cmd.shelfLayout( shelf, q=True, ca=True ) or []
		for button in shelfButtons:
			if cmd.control( button , ex=True ):
				if control( button, q=True, docTag=True ) == buttonTag:
					buttons.append( button )

	return buttons


def updateLoadState( state ):
	existingWin = TriggeredWindow.Get()
	if existingWin:
		existingWin.updateLoadState()

	shelfButtons = getShelfButtonsWithTag( 'zooTriggered' )
	for button in shelfButtons:
		cmd.shelfButton( button, e=True, image1="zooTriggered_%d.xpm" % state )


events.EventManager().addEventCallback( EVT_LOAD_STATE_CHANGE, updateLoadState )


#end
