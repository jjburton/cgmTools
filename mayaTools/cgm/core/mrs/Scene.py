import maya.cmds as mc
import maya.mel as mel
from functools import partial
import os
import fnmatch
import cgm.lib.pyui as pyui
import subprocess
import re
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.lib import asset_utils as ASSET

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================


#>>> Root settings =============================================================
__version__ = '1.5.09072019'
__toolname__ ='MRSScene'

_subLineBGC = [.75,.75,.75]

class ui(cgmUI.cgmGUI):
	'''
Animation Importer UI class.

Loads the Animation Importer UI.

| outputs AnimationImporter

example:
.. python::

	import cgm.core.mrs.Scene as SCENE
	x = SCENE.SceneUI()

	# returns loaded directory
	print x.directory

	# prints the names of all of the loaded assets
	print x.assetList
	'''

	WINDOW_NAME = 'cgmScene'
	DEFAULT_SIZE = 700, 400

	TOOLNAME = 'cgmScene'
	WINDOW_TITLE = '%s - %s'%(TOOLNAME,__version__)    

	def insert_init(self,*args,**kws):
		#self.window                      = None
		
		self.categoryList                = ["Character", "Environment", "Vehicles", "Props", "Interactables", "Level", "Prototype", "Cutscene"]
		self.categoryIndex               = 0

		#self.create_guiOptionVar('matchFrameCollapse',defaultValue = 0)

		self.optionVarDirStore           = cgmMeta.cgmOptionVar("cgmVar_sceneUI_directory_list", varType = "string")
		self.optionVarLastDirStore       = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_directory", varType = "string")
		self.optionVarLastAssetStore     = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_asset", varType = "string")
		self.optionVarLastAnimStore      = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_animation", varType = "string")
		self.optionVarLastVariationStore = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_variation", varType = "string")
		self.optionVarLastVersionStore   = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_version", varType = "string")
		self.optionVarExportDirStore     = cgmMeta.cgmOptionVar("cgmVar_sceneUI_export_directory", varType = "string")
		self.showBakedStore              = cgmMeta.cgmOptionVar("cgmVar_sceneUI_show_baked", defaultValue = 0)
		self.categoryStore               = cgmMeta.cgmOptionVar("cgmVar_sceneUI_category", defaultValue = 0)
		
		## sizes
		self.__itemHeight                = 35
		self.__cw1                       = 125
		
		# UI elements
		self.assetList                   = None #pyui.SearchableList()
		self.animationList               = None #pyui.SearchableList()
		self.variationList               = None #pyui.SearchableList()
		self.versionList                 = None #pyui.SearchableList()
		self.queueTSL                    = None #pyui.UIList()
		self.updateCB                    = None
		self.menuBarLayout               = None
		self.fileMenu                    = None
		self.toolsMenu                   = None
		self.optionsMenu                 = None
		self.categoryText                = None
		self.openRigMB                   = None
		self.importRigMB                 = None
		self.exportQueueFrame            = None
		self.categoryMenuItemList        = []

		self.exportCommand               = ""

		self.showBakedOption             = None
		#self.recursiveAnimListOption    = None
		
		self.showBaked                   = False
		#self.recursiveAnimList          = False
		
		self.fileListMenuItems           = []
		self.batchExportItems            = []

		self.previousDirectoryList       = self.GetPreviousDirectories()
		self.previousLoadedDirectory     = self.GetPreviousDirectory()
		self.exportDirectory             = None

		self.LoadOptions()
		# self.CreateWindow()

	@property
	def directory(self):
		return self.directoryTF.getValue()

	@directory.setter
	def directory(self, directory):
		self.directoryTF.setValue( directory )

	@property
	def categoryDirectory(self):
		return os.path.normpath(os.path.join( self.directory, self.category ))
	
	@property
	def assetDirectory(self):
		return os.path.normpath(os.path.join( self.categoryDirectory, self.assetList['scrollList'].getSelectedItem() ))

	@property
	def animationDirectory(self):
		return os.path.normpath(os.path.join( self.assetDirectory, 'animation', self.animationList['scrollList'].getSelectedItem() ))

	@property
	def variationDirectory(self):
		return os.path.normpath(os.path.join( self.animationDirectory, self.variationList['scrollList'].getSelectedItem() ))

	@property
	def versionFile(self):
		return os.path.normpath(os.path.join( self.variationDirectory, self.versionList['scrollList'].getSelectedItem() ))

	@property
	def exportFileName(self):
		return '%s_%s_%s.fbx' % (self.assetList['scrollList'].getSelectedItem(), self.animationList['scrollList'].getSelectedItem(), self.variationList['scrollList'].getSelectedItem())

	@property
	def category(self):
		return self.categoryList[self.categoryIndex]

	def LoadOptions(self, *args):
		self.showBaked     = bool(self.showBakedStore.getValue())
		self.categoryIndex = int(self.categoryStore.getValue())
		
		self.exportDirectory = self.optionVarExportDirStore.getValue() if self.optionVarExportDirStore.getValue() else ""
		#self.exportCommand   = mc.optionVar(q=self.exportCommandStore) if mc.optionVar(exists=self.exportCommandStore) else ""

	def SaveOptions(self, *args):
		self.showBaked = self.showBakedOption( q=True, checkBox=True ) if self.showBakedOption else False
		
		self.showBakedStore.setValue(self.showBaked)
		self.optionVarExportDirStore.setValue( self.exportDirectory )
		self.categoryStore.setValue( self.categoryIndex )
		#mc.optionVar( stringValue = [self.exportCommandStore, self.exportCommand] )
		
		#self.LoadVersionList()

	def TagAsset(self, *args):
		pass

	def UpdateToLatestRig(self, *args):
		for obj in mc.ls(sl=True):
			myAsset = ASSET.Asset(obj)
			myAsset.UpdateToLatest()

	def SetExportSets(self, *args):
		mc.window( width=150 )
		col = mc.columnLayout( adjustableColumn=True )
		#mc.button( label='Set Bake Set', command=self.SetBakeSet )
		cgmUI.add_Button(col,'Set Bake Set', lambda *a: self.SetBakeSet())

		#mc.button( label='Set Delete Set', command=self.SetDeleteSet )
		cgmUI.add_Button(col,'Set Delete Set', lambda *a: self.SetDeleteSet())

		# mc.button( label='Set Export Set', command=self.SetExportSet )
		cgmUI.add_Button(col,'Set Export Set', lambda *a: self.SetExportSet())

		mc.showWindow()

	def SetDeleteSet(self, *args):
		sel = mc.ls(sl=True)
		deleteSet = sel[0].split(':')[-1]
		print "Setting delete set to: %s" % deleteSet 
		cgmMeta.cgmOptionVar('cgm_delete_set', varType="string").setValue(deleteSet)

	def SetBakeSet(self, *args):
		sel = mc.ls(sl=True)
		bakeSet = sel[0].split(':')[-1]
		print "Setting bake set to: %s" % bakeSet 
		cgmMeta.cgmOptionVar('cgm_bake_set', varType="string").setValue(bakeSet)

	def SetExportSet(self, *args):
		sel = mc.ls(sl=True)
		exportSet = sel[0].split(':')[-1]
		print "Setting geo set to: %s" % exportSet 
		cgmMeta.cgmOptionVar('cgm_export_set', varType="string").setValue(exportSet)

	def build_layoutWrapper(self,parent):
		# if mc.window("cgmSceneUI", q=True, exists=True):
		# 	mc.deleteUI("cgmSceneUI")

		# self.window = mc.window( "cgmSceneUI", title="cgmScene", iconName='cgmScene' )
		
		#self.menuBarLayout = mc.menuBarLayout()
		#self.buildMenu_file()

		_MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')


		##############################
		# Top Column Layout 
		##############################
		_directoryColumn = mUI.MelColumnLayout(_MainForm,useTemplate = 'cgmUISubTemplate') #mc.columnLayout(adjustableColumn=True)
		
		cgmUI.add_LineSubBreak()

		_uiRow_dir = mUI.MelHSingleStretchLayout(_directoryColumn, height = 27)
		mUI.MelLabel(_uiRow_dir,l='Directory', w=100)
		self.directoryTF = mUI.MelTextField(_uiRow_dir, changeCommand=self.ChangeAnimationDirectory)
		self.directoryTF.setValue( self.directory )

		mUI.MelButton(_uiRow_dir, label='set', ut = 'cgmUITemplate', command=self.SetAnimationDirectory, width=100)

		mUI.MelSpacer(_uiRow_dir,w=5)

		_uiRow_dir.setStretchWidget(self.directoryTF)
		_uiRow_dir.layout()

		_uiRow_export = mUI.MelHSingleStretchLayout(_directoryColumn, height = 27)
		mUI.MelLabel(_uiRow_export,l='Export Dir', w=100)
		self.exportDirectoryTF = mUI.MelTextField(_uiRow_export, changeCommand=self.ChangeExportDirectory)
		self.exportDirectoryTF.setValue( self.exportDirectory )
		mUI.MelButton(_uiRow_export, label='set', ut = 'cgmUITemplate', command=self.SetExportDirectory, width=100)

		mUI.MelSpacer(_uiRow_export,w=5)                      

		_uiRow_export.setStretchWidget(self.exportDirectoryTF)

		_uiRow_export.layout()

		mc.setParent(_MainForm)

		##############################
		# Main Asset Lists 
		##############################
		_assetsForm = mUI.MelFormLayout(_MainForm,ut='cgmUISubTemplate', numberOfDivisions=4) #mc.columnLayout(adjustableColumn=True)

		# Category
		_catForm = mUI.MelFormLayout(_assetsForm,ut='cgmUISubTemplate')
		self.categoryText = mUI.MelButton(_catForm,
								   label=self.category,ut='cgmUITemplate',
								   ann='Select the asset category')

		_category_menu = mUI.MelPopupMenu(self.categoryText, button=1 )
		for i,category in enumerate(self.categoryList):
			self.categoryMenuItemList.append( mUI.MelMenuItem(_category_menu, label=category, c=partial(self.SetCategory,i)) )
			if i == self.categoryIndex:
				self.categoryMenuItemList[i]( e=True, enable=False)
		
		self.assetList = self.build_searchable_list(_catForm, sc=self.LoadAnimationList)

		pum = mUI.MelPopupMenu(self.assetList['scrollList'], pmc=self.UpdateCharTSLPopup)
		mUI.MelMenuItem(pum, label="Open In Explorer", command=self.OpenAssetDirectory )
		self.openRigMB = mUI.MelMenuItem(pum, label="Open Rig", command=self.OpenRig )
		self.importRigMB = mUI.MelMenuItem(pum, label="Import Rig", command=self.ImportRig )

		self.assetButton = mUI.MelButton(_catForm, ut='cgmUITemplate', label="New Asset", command=self.CreateAsset)

		_catForm( edit=True, 
			attachForm=[
				(self.categoryText, 'top', 0), 
				(self.categoryText, 'left', 0), 
				(self.categoryText, 'right', 0), 
				(self.assetList['formLayout'], 'left', 0),
				(self.assetList['formLayout'], 'right', 0),
				(self.assetButton, 'bottom', 0), 
				(self.assetButton, 'right', 0), 
				(self.assetButton, 'left', 0)], 
			attachControl=[
				(self.assetList['formLayout'], 'top', 0, self.categoryText),
				(self.assetList['formLayout'], 'bottom', 0, self.assetButton)] )


		# Animation
		_animForm = mUI.MelFormLayout(_assetsForm,ut='cgmUISubTemplate')
		_animBtn = mUI.MelButton(_animForm,
								   label='Animation',ut='cgmUITemplate',
								   ann='Select the asset type', en=False)
	
		self.animationList = self.build_searchable_list(_animForm, sc=self.LoadVariationList)

		pum = mUI.MelPopupMenu(self.animationList['scrollList'], pmc=self.UpdateCharTSLPopup)
		mUI.MelMenuItem(pum, label="Open In Explorer", command=self.OpenAnimationDirectory )

		self.animationButton = mUI.MelButton(_animForm, ut='cgmUITemplate', label="New Animation", command=self.CreateAnimation)

		_animForm( edit=True, 
			attachForm=[
				(_animBtn, 'top', 0), 
				(_animBtn, 'left', 0), 
				(_animBtn, 'right', 0), 
				(self.animationList['formLayout'], 'left', 0),
				(self.animationList['formLayout'], 'right', 0),
				(self.animationButton, 'bottom', 0), 
				(self.animationButton, 'right', 0), 
				(self.animationButton, 'left', 0)], 
			attachControl=[
				(self.animationList['formLayout'], 'top', 0, _animBtn),
				(self.animationList['formLayout'], 'bottom', 0, self.animationButton)] )
	
		# Variation
		_variationForm = mUI.MelFormLayout(_assetsForm,ut='cgmUISubTemplate')
		_variationBtn = mUI.MelButton(_variationForm,
								   label='Variation',ut='cgmUITemplate',
								   ann='Select the asset variation', en=False)
	
		self.variationList = self.build_searchable_list(_variationForm, sc=self.LoadVersionList)

		pum = mUI.MelPopupMenu(self.variationList['scrollList'], pmc=self.UpdateCharTSLPopup)
		mUI.MelMenuItem(pum, label="Open In Explorer", command=self.OpenVariationDirectory )

		self.variationButton = mUI.MelButton(_variationForm, ut='cgmUITemplate', label="New Variation", command=self.CreateVariation)

		_variationForm( edit=True, 
			attachForm=[
				(_variationBtn, 'top', 0), 
				(_variationBtn, 'left', 0), 
				(_variationBtn, 'right', 0), 
				(self.variationList['formLayout'], 'left', 0),
				(self.variationList['formLayout'], 'right', 0),
				(self.variationButton, 'bottom', 0), 
				(self.variationButton, 'right', 0), 
				(self.variationButton, 'left', 0)], 
			attachControl=[
				(self.variationList['formLayout'], 'top', 0, _variationBtn),
				(self.variationList['formLayout'], 'bottom', 0, self.variationButton)] )
	

		# Version
		_versionForm = mUI.MelFormLayout(_assetsForm,ut='cgmUISubTemplate')
		_versionBtn = mUI.MelButton(_versionForm,
								   label='Version',ut='cgmUITemplate',
								   ann='Select the asset version', en=False)
	
		self.versionList = self.build_searchable_list(_versionForm, sc=self.StoreCurrentSelection)

		pum = mUI.MelPopupMenu(self.versionList['scrollList'], pmc=self.UpdateCharTSLPopup)
		mUI.MelMenuItem(pum, label="Open In Explorer", command=self.OpenVersionDirectory )
		mUI.MelMenuItem(pum, label="Reference File", command=self.ReferenceFile )

		self.versionButton = mUI.MelButton(_versionForm, ut='cgmUITemplate', label="Save New Version", command=self.SaveVersion)

		_versionForm( edit=True, 
			attachForm=[
				(_versionBtn, 'top', 0), 
				(_versionBtn, 'left', 0), 
				(_versionBtn, 'right', 0), 
				(self.versionList['formLayout'], 'left', 0),
				(self.versionList['formLayout'], 'right', 0),
				(self.versionButton, 'bottom', 0), 
				(self.versionButton, 'right', 0), 
				(self.versionButton, 'left', 0)], 
			attachControl=[
				(self.versionList['formLayout'], 'top', 0, _versionBtn),
				(self.versionList['formLayout'], 'bottom', 0, self.versionButton)] )
	

		attachForm = []
		attachControl = []
		attachPosition = []

		_subForms = [_catForm,_animForm,_variationForm,_versionForm]

		for i,form in enumerate(_subForms):
			if i == 0:
				attachForm.append( (form, 'left', 5) )
			else:
				attachControl.append( (form, 'left', 5, _subForms[i-1]) )
				
			attachForm.append((form, 'top', 5))
			attachForm.append((form, 'bottom', 5))
			
			if i == len(_subForms)-1:
				attachForm.append( (form, 'right', 5) )
			else:
				attachPosition.append( (form, 'right', 5, i+1) )

		_assetsForm( edit=True, attachForm = attachForm, attachControl = attachControl, attachPosition = attachPosition)



		##############################
		# Bottom 
		##############################
		_bottomColumn    = mUI.MelColumnLayout(_MainForm,useTemplate = 'cgmUISubTemplate', adjustableColumn=True)#mc.columnLayout(adjustableColumn = True)
		
		mc.setParent(_bottomColumn)
		cgmUI.add_LineSubBreak()

		_row = mUI.MelHSingleStretchLayout(_bottomColumn,ut='cgmUISubTemplate',padding = 5)
		
		mUI.MelSpacer(_row,w=5)
		self.exportButton = mUI.MelButton(_row, label="Export", ut = 'cgmUITemplate', c=partial(self.RunExportCommand,1), h=self.__itemHeight)
		mc.popupMenu()
		mc.menuItem( l="Bake Without Export", c=partial(self.RunExportCommand,0))
		mc.menuItem( l="Export Rig", c=partial(self.RunExportCommand,3))
		mc.menuItem( l="Force Export As Cutscene", c=partial(self.RunExportCommand,2))
		
		mUI.MelButton(_row, ut = 'cgmUITemplate', label="Bake Without Export", c=partial(self.RunExportCommand,0), h=self.__itemHeight)
		mUI.MelButton(_row, ut = 'cgmUITemplate', label="Export Rig", c=partial(self.RunExportCommand,3), h=self.__itemHeight)
		mUI.MelButton(_row, ut = 'cgmUITemplate', label="Export Cutscene", c=partial(self.RunExportCommand,2), h=self.__itemHeight)

		mUI.MelButton(_row, ut = 'cgmUITemplate', label="Add To Export Queue", w=200, c=partial(self.AddToExportQueue), h=self.__itemHeight)

		_row.setStretchWidget(self.exportButton)
		
		mUI.MelSpacer(_row,w=5)
		
		_row.layout()

		mc.setParent(_bottomColumn)
		cgmUI.add_LineSubBreak()

		_row = mUI.MelHSingleStretchLayout(_bottomColumn,ut='cgmUISubTemplate',padding = 5)

		mUI.MelSpacer(_row,w=5)

		_row.setStretchWidget( mUI.MelButton(_row, ut = 'cgmUITemplate', label="Load Animation", c=self.LoadAnimation, h=self.__itemHeight))
		
		mUI.MelSpacer(_row,w=5)

		_row.layout()

		mc.setParent(_bottomColumn)
		cgmUI.add_LineSubBreak()

		self.exportQueueFrame = mUI.MelFrameLayout(_bottomColumn, label="Export Queue", collapsable=True, collapse=True)
		_rcl = mUI.MelFormLayout(self.exportQueueFrame,ut='cgmUITemplate')

		self.queueTSL = cgmUI.cgmScrollList(_rcl)
		self.queueTSL.allowMultiSelect(True)

		_col = mUI.MelColumnLayout(_rcl,width=200,adjustableColumn=True,useTemplate = 'cgmUISubTemplate')#mc.columnLayout(width=200,adjustableColumn=True)
		
		cgmUI.add_LineSubBreak()
		mUI.MelButton(_col, label="Add", ut = 'cgmUITemplate', command=partial(self.AddToExportQueue))
		cgmUI.add_LineSubBreak()
		mUI.MelButton(_col, label="Remove", ut = 'cgmUITemplate', command=partial(self.RemoveFromQueue, 0))
		cgmUI.add_LineSubBreak()
		mUI.MelButton(_col, label="Remove All", ut = 'cgmUITemplate', command=partial(self.RemoveFromQueue, 1))
		cgmUI.add_LineSubBreak()
		mUI.MelButton(_col, label="Batch Export", ut = 'cgmUITemplate', command=partial(self.BatchExport))
		cgmUI.add_LineSubBreak()

		_options_fl = mUI.MelFrameLayout(_col, label="Options", collapsable=True)

		_c2 = mUI.MelColumnLayout(_options_fl, adjustableColumn=True)
		self.updateCB = mUI.MelCheckBox(_c2, label="Update and Save Increment", v=False)

		_rcl( edit=True, 
			attachForm=[
				(self.queueTSL, 'top', 0), 
				(self.queueTSL, 'left', 0), 
				(self.queueTSL, 'bottom', 0), 
				(_col, 'bottom', 0), 
				(_col, 'top', 0), 
				(_col, 'right', 0)], 
			attachControl=[
				(self.queueTSL, 'right', 0, _col)] )

		##############################
		# Layout form
		##############################

		_footer = cgmUI.add_cgmFooter(_MainForm)            

		_MainForm( edit=True, 
			attachForm=[
				(_directoryColumn, 'top', 0), 
				(_directoryColumn, 'left', 0), 
				(_directoryColumn, 'right', 0), 
				(_bottomColumn, 'right', 0), 
				(_bottomColumn, 'left', 0),
				(_assetsForm, 'left', 0),
				(_assetsForm, 'right', 0),
				(_footer, 'left', 0),
				(_footer, 'right', 0),
				(_footer, 'bottom', 0)], 
			attachControl=[
				(_bottomColumn, 'bottom', 0, _footer),
				(_assetsForm, 'top', 0, _directoryColumn),
				(_assetsForm, 'bottom', 0, _bottomColumn)] )
	

		# _MainForm( edit=True, 

		# 	attachForm =
		# 	[(_directoryColumn,'top', 0), 
		# 	(_directoryColumn,'left', 0), 
		# 	(_directoryColumn,'right', 0), 
		# 	(_assetsForm, 'left', 0), 
		# 	(c4_upperColumn, 'right', 0), 
		# 	(self.assetList['scrollList'], 'left', 0), 
		# 	(_bottomColumn, 'left', 0), 
		# 	(_bottomColumn, 'bottom', 0), 
		# 	(_bottomColumn, 'right', 0), 
		# 	(self.versionList.textScrollList, 'right', 0),
		# 	(self.assetButton, 'left', 0), 
		# 	(self.versionButton, 'right', 0) ], 

		# 	attachControl =
		# 	[(_assetsForm, 'top', 0, _directoryColumn), 
		# 	(c2_upperColumn, 'top', 0, _directoryColumn), 
		# 	(c2_upperColumn, 'right', 0, c3_upperColumn), 
		# 	(c3_upperColumn, 'top', 0, _directoryColumn), 
		# 	(c3_upperColumn, 'right', 0, c4_upperColumn), 
		# 	(c4_upperColumn, 'top', 0, _directoryColumn), 
		# 	(self.assetList['scrollList'], 'bottom', 0, self.assetButton), 
		# 	(self.assetList['scrollList'], 'top', 0, _assetsForm),
		# 	(self.animationList['scrollList'], 'bottom', 0, self.animationButton), 
		# 	(self.animationList['scrollList'], 'left', 0, _assetsForm), 
		# 	(self.animationList['scrollList'], 'right', 4, self.variationList.textScrollList),
		# 	(self.animationList['scrollList'], 'top', 0, c3_upperColumn),
		# 	(self.variationList.textScrollList, 'left', 5, c2_upperColumn),
		# 	(self.variationList.textScrollList, 'right', 4, self.versionList.textScrollList),
		# 	(self.variationList.textScrollList, 'bottom', 0, self.versionButton), 
		# 	(self.variationList.textScrollList, 'top', 0, c2_upperColumn),
		# 	(self.versionList.textScrollList, 'left', 5, c3_upperColumn),
		# 	(self.versionList.textScrollList, 'bottom', 0, self.versionButton), 
		# 	(self.versionList.textScrollList, 'top', 0, c3_upperColumn),
		# 	(self.assetButton, 'bottom', 3, _bottomColumn),
		# 	(self.assetButton, 'right', 5, c2_upperColumn),
		# 	(self.animationButton, 'bottom', 3, _bottomColumn),
		# 	(self.animationButton, 'left', 5, _assetsForm),
		# 	(self.animationButton, 'right', 5, c3_upperColumn),
		# 	(self.variationButton, 'bottom', 3, _bottomColumn),
		# 	(self.variationButton, 'left', 5, c2_upperColumn),
		# 	(self.variationButton, 'right', 5, c4_upperColumn),
		# 	(self.versionButton, 'bottom', 3, _bottomColumn),
		# 	(self.versionButton, 'left', 5, c3_upperColumn)], 

		# 	attachPosition =
		# 	[(self.assetList['scrollList'], 'right', 2, 25),
		# 	(self.animationList['scrollList'], 'left', 2, 25),
		# 	(c4_upperColumn, 'left', 2, 75),
		# 	(_assetsForm, 'right', 2, 25), 
		# 	(c2_upperColumn, 'left', 2, 25), 
		# 	(c2_upperColumn, 'right', 2, 50),
		# 	(c3_upperColumn, 'left', 2, 50), 
		# 	(c3_upperColumn, 'right', 2, 75)], 

		# 	attachNone=(_bottomColumn, 'top') )

		# mc.showWindow( self.window )

	def show( self ):
		if self.previousLoadedDirectory:
			self.LoadCategoryList(self.previousLoadedDirectory)

		self.LoadPreviousSelection()
		
		self.setVisibility( True )


	#=========================================================================
	# Menu Building
	#=========================================================================
	def build_menus(self):
		_str_func = 'build_menus[{0}]'.format(self.__class__.TOOLNAME)            
		log.info("|{0}| >>...".format(_str_func))   
		
		self.uiMenu_FileMenu = mUI.MelMenu( l='File', pmc=self.buildMenu_file)		        
		self.uiMenu_OptionsMenu = mUI.MelMenu( l='Options', pmc=self.buildMenu_options)		
		self.uiMenu_ToolsMenu = mUI.MelMenu( l='Tools', pmc=self.buildMenu_tools)  
		self.uiMenu_HelpMenu = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)   

	def buildMenu_file( self, *args):
		self.uiMenu_FileMenu.clear()
		#>>> Reset Options			
		mUI.MelMenuItem( self.uiMenu_FileMenu, l="Open",
						 #en = _b_reload,
						 c = lambda *a:mc.evalDeferred(self.OpenDirectory,lp=True))
						 #c=cgmGEN.Callback(reloadUI,self.__class__,self.WINDOW_NAME))
						 #c=lambda *a: reloadUI(self.__class__,self.WINDOW_NAME))		
		
		mUI.MelMenuItemDiv( self.uiMenu_FileMenu )

		mUI.MelMenuItem( self.uiMenu_FileMenu, l="Clear List",
						 #en = _b_reload,
						 #c = cgmGEN.Callback(resetUI(str(self.WINDOW_NAME))))
						 c = lambda *a:mc.evalDeferred(self.ClearPreviousDirectories,lp=True))                         
						 #c=cgmGEN.Callback( resetUI,self.__class__, self.WINDOW_NAME, self.l_optionVars))                         
						 #c=lambda *a: resetUI(self.__class__, self.WINDOW_NAME, self.l_optionVars))    

		# self.fileListMenuItems.append(mc.menuItem( label='Open', c=self.OpenDirectory ))
		# self.fileListMenuItems.append(mc.menuItem( d=True ))
		
		# for d in self.GetPreviousDirectories():
		# 	self.fileListMenuItems.append(mc.menuItem(label=d, c=partial(self.LoadCategoryList,d)))
		
		# self.fileListMenuItems.append(mc.menuItem( label='Clear List', c=self.ClearPreviousDirectories ))

	def buildMenu_options( self, *args):
		self.uiMenu_OptionsMenu.clear()
		#>>> Reset Options		

		self.showBakedOption = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Show baked versions",
						 #en = _b_reload,
						 checkBox=self.showBaked,
						 c = lambda *a:mc.evalDeferred(self.SaveOptions,lp=True))
						 #c=cgmGEN.Callback(reloadUI,self.__class__,self.WINDOW_NAME))
						 #c=lambda *a: reloadUI(self.__class__,self.WINDOW_NAME))	

		# self.showBakedOption    = mc.menuItem( label='Show baked versions', checkBox=self.showBaked, c=self.SaveOptions )
	
	def buildMenu_tools( self, *args):
		self.uiMenu_ToolsMenu.clear()
		#>>> Reset Options		
	
		mUI.MelMenuItem( self.uiMenu_ToolsMenu, l="Tag As Current Asset",
						 c = lambda *a:mc.evalDeferred(self.TagAsset,lp=True))
		
		mUI.MelMenuItem( self.uiMenu_ToolsMenu, l="Set Export Sets",
						 c = lambda *a:mc.evalDeferred(self.SetExportSets,lp=True))

		mUI.MelMenuItem( self.uiMenu_ToolsMenu, l="Update Selected Rigs",
						 c = lambda *a:mc.evalDeferred(self.UpdateToLatestRig,lp=True))




	# def ConstructMenuBar(self, *args):
	# 	if self.fileMenu:
	# 		mc.deleteUI(self.fileMenu, control=True)
	# 		self.fileMenu = None
	# 		self.fileListMenuItems = []
	# 	if self.optionsMenu:
	# 		mc.deleteUI(self.optionsMenu, control=True)
	# 		self.optionsMenu = None
	# 	if self.toolsMenu:
	# 		mc.deleteUI(self.toolsMenu, control=True)
	# 		self.toolsMenu = None

	# 	mc.setParent(self.menuBarLayout)

	# 	self.fileMenu = mc.menu( label='File' )

	# 	self.optionsMenu = mc.menu( label='Options' )
	# 	#self.setExportCommandMI = mc.menuItem( label='Custom Export Command', c=self.SetExportCommand )

	# 	self.toolsMenu = mc.menu( label='Tools' )


	#####
	## Searchable Lists
	#####
	def build_searchable_list(self, parent = None, sc=None):
		_margin = 0

		if not parent:
			parent = self

		form = mUI.MelFormLayout(parent,ut='cgmUITemplate')

		rcl = mc.rowColumnLayout(numberOfColumns=2, adjustableColumn=1)

		tx = mUI.MelTextField(rcl)
		b = mUI.MelButton(rcl, label='clear', ut='cgmUISubTemplate')

		tsl = cgmUI.cgmScrollList(form)
		tsl.allowMultiSelect(False)

		if sc != None:
			tsl(edit = True, sc=sc)

		form( edit=True, attachForm=[(rcl, 'top', _margin), (rcl, 'left', _margin), (rcl, 'right', _margin), (tsl, 'bottom', _margin), (tsl, 'right', _margin), (tsl, 'left', _margin)], attachControl=[(tsl, 'top', _margin, rcl)] )

		searchableList = {'formLayout':form, 'scrollList':tsl, 'searchField':tx, 'searchButton':b, 'items':[], 'selectCommand':sc}

		tx(edit=True, tcc=partial(self.process_search_filter, searchableList))
		b(edit=True, command=partial(self.clear_search_filter, searchableList))

		return searchableList

	def process_search_filter(self, searchableList, *args):
		#print "processing search for %s with search term %s" % (searchableList['scrollList'], searchableList['searchField'].getValue())
		if not searchableList['searchField'].getValue():
			searchableList['scrollList'].setItems(searchableList['items'])
		else:
			searchTerms = searchableList['searchField'].getValue().lower().strip().split(' ')  #set(searchableList['searchField'].getValue().replace(' ', '').lower())
			listItems = []
			for item in searchableList['items']:
				hasAllTerms = True
				for term in searchTerms:
					if not term in item.lower():
						hasAllTerms = False
				if hasAllTerms:
					listItems.append(item)
			searchableList['scrollList'].setItems(listItems)

		searchableList['selectCommand']

	def clear_search_filter(self, searchableList, *args):
		print "Clearing search filter for %s with search term %s" % (searchableList['scrollList'], searchableList['searchField'].getValue())
		searchableList['searchField'].setValue("")
		selected = searchableList['scrollList'].getSelectedItem()
		searchableList['scrollList'].setItems(searchableList['items'])
		searchableList['scrollList'].selectByValue(selected)

	def SetCategory(self, index, *args):
		self.categoryIndex = index
		mc.button( self.categoryText, e=True, label=self.category )
		for i,category in enumerate(self.categoryMenuItemList):
			if i == self.categoryIndex:
				self.categoryMenuItemList[i]( e=True, enable=False)
			else:
				self.categoryMenuItemList[i]( e=True, enable=True)

		self.LoadCategoryList(self.directory)
		self.SaveOptions()

	def LoadCategoryList(self, directory="", *args):
		p = self.GetPreviousDirectories()
		if len(p) >= 10:
			for i in range(len(p) - 9):
				self.optionVarDirStore.removeIndex(0)

		if directory not in p:
			self.optionVarDirStore.append(directory)

		self.directory = directory

		self.buildMenu_file()

		# populate animation info list
		#fileExtensions = ['mb', 'ma']

		charList = []

		categoryDirectory = os.path.join(directory, self.category)
		if os.path.exists(categoryDirectory):
			for d in os.listdir(categoryDirectory):
				#for ext in fileExtensions:
				#	if os.path.splitext(f)[-1].lower() == ".%s" % ext :
				if d[0] == '_' or d[0] == '.':
					continue

				charDir = os.path.normpath(os.path.join(categoryDirectory, d))
				if os.path.isdir(charDir):
					charList.append(d)

		charList = sorted(charList, key=lambda v: v.upper())

		self.UpdateAssetList(charList)

		self.StoreCurrentDirectory()
		
		self.animationList['items'] = []
		self.animationList['scrollList'].clear()
		
		self.variationList['items'] = []
		self.variationList['scrollList'].clear()
		
		self.versionList['items'] = []
		self.versionList['scrollList'].clear()

		self.StoreCurrentSelection()

	def LoadAnimationList(self, *args):
		animList = []
		
		if self.categoryDirectory and self.assetList['scrollList'].getSelectedItem():
			charDir = os.path.normpath(os.path.join( self.categoryDirectory, self.assetList['scrollList'].getSelectedItem(), 'animation' ))

			if os.path.exists(charDir):
				for d in os.listdir(charDir):
					#for ext in fileExtensions:
					#	if os.path.splitext(f)[-1].lower() == ".%s" % ext :
					if d[0] == '_' or d[0] == '.':
						continue

					animDir = os.path.normpath(os.path.join(charDir, d))
					if os.path.isdir(animDir):
						animList.append(d)

		self.animationList['items'] = animList
		self.animationList['scrollList'].setItems(animList)

		self.variationList['items'] = []
		self.variationList['scrollList'].clear()

		self.versionList['items'] = []
		self.versionList['scrollList'].clear()

		self.StoreCurrentSelection()

	def LoadVariationList(self, *args):
		variationList = []

		selectedVariation = self.variationList['scrollList'].getSelectedItem()

		self.variationList['items'] = []
		self.variationList['scrollList'].clear()

		if self.categoryDirectory and self.assetList['scrollList'].getSelectedItem() and self.animationList['scrollList'].getSelectedItem():
			animationDir = self.animationDirectory

			if os.path.exists(animationDir):
				for d in os.listdir(animationDir):
					#for ext in fileExtensions:
					#	if os.path.splitext(f)[-1].lower() == ".%s" % ext :
					if d[0] == '_' or d[0] == '.':
						continue

					animDir = os.path.normpath(os.path.join(animationDir, d))
					if os.path.isdir(animDir):
						variationList.append(d)

		self.variationList['items'] = variationList
		self.variationList['scrollList'].setItems(variationList)

		self.variationList['scrollList'].selectByValue(selectedVariation)

		self.versionList['items'] = []
		self.versionList['scrollList'].clear()

		self.LoadVersionList()

		if len(self.versionList['items']) > 0:
			self.versionList['scrollList'].selectByIdx(0)

		self.StoreCurrentSelection()

	def LoadVersionList(self, *args):
		if not self.assetList['scrollList'].getSelectedItem() or not self.animationList['scrollList'].getSelectedItem():
			return

		versionList = []
		anims = []

		# populate animation info list
		fileExtensions = ['mb', 'ma']

		if self.categoryDirectory and self.assetList['scrollList'].getSelectedItem() and self.animationList['scrollList'].getSelectedItem() and self.variationList['scrollList'].getSelectedItem():
			animDir = self.variationDirectory
			
			if os.path.exists(animDir):
				for d in os.listdir(animDir):
					if d[0] == '_' or d[0] == '.':
						continue

					for ext in fileExtensions:
						if os.path.splitext(d)[-1].lower() == ".%s" % ext :
							if not "_baked" in d or self.showBaked:
								anims.append(d)

		self.versionList['items'] = anims
		self.versionList['scrollList'].setItems(anims)

		self.StoreCurrentSelection()

	def LoadAnimation(self, *args):
		if not self.assetList['scrollList'].getSelectedItem():
			print "No asset selected"
			return
		if not self.animationList['scrollList'].getSelectedItem():
			print "No animation selected"
			return
		if not self.versionList['scrollList'].getSelectedItem():
			print "No version selected"
			return

		mc.file(self.versionFile, o=True, f=True, ignoreVersion=True)

	def SetAnimationDirectory(self, *args):
		basicFilter = "*"
		x = mc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, fm=3)
		if x:
			self.LoadCategoryList(x[0])

	def ChangeAnimationDirectory(self, *args):
		newPath = self.directory
		if os.path.exists(newPath):
			self.LoadCategoryList(newPath)

	def SetExportDirectory(self, *args):
		basicFilter = "*"
		x = mc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, fm=3)
		if x:
			self.exportDirectory = x[0]

		self.exportDirectoryTF.setValue( self.exportDirectory )
		self.optionVarExportDirStore.setValue( self.exportDirectory )
		#self.SaveOptions()

	def ChangeExportDirectory(self, *args):
		newPath = self.exportDirectory
		if os.path.exists(newPath):
			#self.LoadCategoryList(newPath)
			self.exportDirectory = newPath
			self.SaveOptions()

	def GetPreviousDirectories(self, *args):
		if type(self.optionVarDirStore.getValue()) is list:
			return self.optionVarDirStore.getValue()
		else:
			return []

	def UpdateAssetList(self, charList):
		self.assetList['items'] = charList
		self.assetList['scrollList'].setItems(charList)

	def GetPreviousDirectory(self, *args):
		if self.optionVarLastDirStore.getValue():
			return self.optionVarLastDirStore.getValue()
		else:
			return None

	def StoreCurrentDirectory(self, *args):
		self.optionVarLastDirStore.setValue(self.directory)

	def StoreCurrentSelection(self, *args):
		if self.assetList['scrollList'].getSelectedItem():
			self.optionVarLastAssetStore.setValue(self.assetList['scrollList'].getSelectedItem())
		#else:
		#	mc.optionVar(rm=self.optionVarLastAssetStore)

		if self.animationList['scrollList'].getSelectedItem():
			self.optionVarLastAnimStore.setValue(self.animationList['scrollList'].getSelectedItem())
		#else:
		#	mc.optionVar(rm=self.optionVarLastAnimStore)

		if self.variationList['scrollList'].getSelectedItem():
			self.optionVarLastVariationStore.setValue(self.variationList['scrollList'].getSelectedItem())
		#else:
		#	mc.optionVar(rm=self.optionVarLastVariationStore)

		if self.versionList['scrollList'].getSelectedItem():
			self.optionVarLastVersionStore.setValue( self.versionList['scrollList'].getSelectedItem() )
		#else:
		#	mc.optionVar(rm=self.optionVarLastVersionStore)

	def LoadPreviousSelection(self, *args):
		if self.optionVarLastAssetStore.getValue():
			self.assetList['scrollList'].selectByValue( self.optionVarLastAssetStore.getValue() )

		self.LoadAnimationList()

		if self.optionVarLastAnimStore.getValue():
			self.animationList['scrollList'].selectByValue( self.optionVarLastAnimStore.getValue() )

		self.LoadVariationList()

		if self.optionVarLastVariationStore.getValue():
			self.variationList['scrollList'].selectByValue( self.optionVarLastVariationStore.getValue() )

		self.LoadVersionList()

		if self.optionVarLastVersionStore.getValue():
			self.versionList['scrollList'].selectByValue( self.optionVarLastVersionStore.getValue() )

	
	def ClearPreviousDirectories(self, *args):		
		self.optionVarDirStore.clear()
		self.buildMenu_file()

	def CreateAsset(self, *args):
		result = mc.promptDialog(
				title='New Asset',
				message='Asset Name:',
				button=['OK', 'Cancel'],
				defaultButton='OK',
				cancelButton='Cancel',
				dismissString='Cancel')

		if result == 'OK':
			charName = mc.promptDialog(query=True, text=True)
			charPath = os.path.normpath(os.path.join(self.categoryDirectory, charName))
			if not os.path.exists(charPath):
				os.mkdir(charPath)
				os.mkdir(os.path.normpath(os.path.join(charPath, 'animation')))

			self.LoadCategoryList(self.directory)

			self.assetList['scrollList'].selectByValue(charName)

	def CreateAnimation(self, *args):
		result = mc.promptDialog(
				title='New Animation',
				message='Animation Name:',
				button=['OK', 'Cancel'],
				defaultButton='OK',
				cancelButton='Cancel',
				dismissString='Cancel')

		if result == 'OK':
			animName = mc.promptDialog(query=True, text=True)
			animationDir = os.path.normpath(os.path.join(self.assetDirectory, 'animation'))
			if not os.path.exists(animationDir):
				os.mkdir(animationDir)

			animPath = os.path.normpath(os.path.join(animationDir, animName))
			if not os.path.exists(animPath):
				os.mkdir(animPath)

			variationPath = os.path.normpath(os.path.join(animPath, '01'))
			if not os.path.exists(variationPath):
				os.mkdir(variationPath)

			self.LoadAnimationList()

			self.animationList['scrollList'].selectByValue( animName)
			#self.LoadAnimationList()
			self.LoadVariationList()
			#self.LoadVariationList()
			
			self.variationList['scrollList'].selectByValue( '01')
			#self.LoadVersionList()
			self.LoadVersionList()

			createPrompt = mc.confirmDialog(
				title='Create?',
				message='Create starting file?',
				button=['Yes', 'No'],
				defaultButton='No',
				cancelButton='No',
				dismissString='No')

			if createPrompt == "Yes":
				self.OpenRig()
				self.SaveVersion()

	def CreateVariation(self, *args):
		lastVariation = 0
		for x in os.listdir(self.animationDirectory):
			if int(x) > lastVariation:
				lastVariation = int(x)

		newVariation = lastVariation + 1

		os.mkdir(os.path.normpath(os.path.join(self.animationDirectory, '%02d' % newVariation)))

		self.LoadVariationList()
		self.variationList['scrollList'].selectByValue('%02d' % newVariation)

		self.LoadVersionList()

	def SaveVersion(self, *args):
		animationFiles = self.versionList['items']

		animationName = self.animationList['scrollList'].getSelectedItem()
		wantedName = "%s_%s" % (self.assetList['scrollList'].getSelectedItem(), self.animationList['scrollList'].getSelectedItem())

		if len(animationFiles) == 0:
			wantedName = "%s_%02d.mb" % (wantedName, 1)
		else:
			currentFile = mc.file(q=True, loc=True)
			if not os.path.exists(currentFile):
				currentFile = "%s_%02d.mb" % (wantedName, 1)

			baseFile = os.path.split(currentFile)[-1]
			baseName, ext = baseFile.split('.')

			wantedBasename = "%s_%s" % (self.assetList['scrollList'].getSelectedItem(), self.animationList['scrollList'].getSelectedItem())
			if not wantedBasename in baseName:
				baseName = "%s_%02d" % (wantedBasename, 1)

			noVersionName = '_'.join(baseName.split('_')[:-1])
			version = int(baseName.split('_')[-1])

			versionFiles = []
			versions = []
			for item in self.versionList['items']:
				matchString = "^(%s_)[0-9]+\.m." % noVersionName
				pattern = re.compile(matchString)
				if pattern.match(item):
					versionFiles.append(item)
					versions.append( int(item.split('.')[0].split('_')[-1]) )

			versions.sort()

			if len(versions) > 0:
				newVersion = versions[-1]+1
			else:
				newVersion = 1

			wantedName = "%s_%02d.%s" % (noVersionName, newVersion, ext)

		saveFile = os.path.normpath(os.path.join(self.variationDirectory, wantedName) )
		print "Saving file: %s" % saveFile
		mc.file( rename=saveFile )
		mc.file( save=True )

		self.LoadVersionList()

	def OpenDirectory(self, path):
		#subprocess.Popen('explorer %s' % path)
		os.startfile(path)

	def OpenAssetDirectory(self, *args):
		self.OpenDirectory(self.categoryDirectory)

	def OpenAnimationDirectory(self, *args):
		self.OpenDirectory( os.path.normpath(os.path.join(self.assetDirectory, 'animation') ))

	def OpenVariationDirectory(self, *args):
		self.OpenDirectory(self.animationDirectory)

	def OpenVersionDirectory(self, *args):
		self.OpenDirectory(self.variationDirectory)

	def ReferenceFile(self, *args):
		if not self.assetList['scrollList'].getSelectedItem():
			print "No asset selected"
			return
		if not self.animationList['scrollList'].getSelectedItem():
			print "No animation selected"
			return
		if not self.versionList['scrollList'].getSelectedItem():
			print "No version selected"
			return

		filePath = self.versionFile
		mc.file(filePath, r=True, ignoreVersion=True, namespace=self.versionList['scrollList'].getSelectedItem())

	def UpdateCharTSLPopup(self, *args):
		rigPath = os.path.normpath(os.path.join(self.assetDirectory, "%s_rig.mb" % self.assetList['scrollList'].getSelectedItem() ))
		if os.path.exists(rigPath):
			mc.menuItem( self.openRigMB, e=True, enable=True )
			mc.menuItem( self.importRigMB, e=True, enable=True )
		else:
			mc.menuItem( self.openRigMB, e=True, enable=False )
			mc.menuItem( self.importRigMB, e=True, enable=False )

	def OpenRig(self, *args):
		rigPath = os.path.normpath(os.path.join(self.assetDirectory, "%s_rig.mb" % self.assetList['scrollList'].getSelectedItem() ))
		if os.path.exists(rigPath):
			mc.file(rigPath, o=True, f=True, ignoreVersion=True)

	def ImportRig(self, *args):
		rigPath = os.path.normpath(os.path.join(self.assetDirectory, "%s_rig.mb" % self.assetList['scrollList'].getSelectedItem() ))
		if os.path.exists(rigPath):
			mc.file(rigPath, i=True, f=True, pr=True)

	# def SetExportCommand(self, *args):
	# 	result = mc.promptDialog(
	# 		title='Set Export Command',
	# 		message='Command:',
	# 		scrollableField=True,
	# 		text=self.exportCommand,
	# 		button=['OK', 'Cancel'],
	# 		defaultButton='OK',
	# 		cancelButton='Cancel',
	# 		dismissString='Cancel')

	# 	if result == 'OK':
	# 		self.exportCommand = mc.promptDialog(query=True, text=True)
	# 		mc.button( self.exportButton, e=True, en=True if self.exportCommand != "" else False )

	# 	self.SaveOptions()

	def AddToExportQueue(self, *args):
		if self.versionList['scrollList'].getSelectedItem() != None:
			self.batchExportItems.append( {"asset":self.assetList['scrollList'].getSelectedItem(),"animation":self.animationList['scrollList'].getSelectedItem(),"variation":self.variationList['scrollList'].getSelectedItem(),"version":self.versionList['scrollList'].getSelectedItem()} )
		elif self.variationList != None:
			self.batchExportItems.append( {"asset":self.assetList['scrollList'].getSelectedItem(),"animation":self.animationList['scrollList'].getSelectedItem(),"variation":self.variationList['scrollList'].getSelectedItem(),"version":self.versionList['scrollList'].getItems()[-1]} )
		
		self.RefreshQueueList()

	def RemoveFromQueue(self, *args):
		if args[0] == 0:
			idxes = self.queueTSL.getSelectedIdxs()
			idxes.reverse()

			for idx in idxes:
				del self.batchExportItems[idx-1]
		elif args[0] == 1:
			self.batchExportItems = []

		self.RefreshQueueList()

	def BatchExport(self, *args):
		import pyunify.pipe.asset as asset

		for animDict in self.batchExportItems:
			self.assetList['scrollList'].selectByValue( animDict["asset"] )
			self.LoadAnimationList()
			self.animationList['scrollList'].selectByValue( animDict["animation"])
			self.LoadVariationList()
			self.variationList['scrollList'].selectByValue( animDict["variation"])
			self.LoadVersionList()
			self.versionList['scrollList'].selectByValue( animDict["version"])

			mc.file(self.versionFile, o=True, f=True, ignoreVersion=True)

			masterNode = None
			for item in mc.ls("*:master", r=True):
				if len(item.split(":")) == 2:
					masterNode = item

				if mc.checkBox(self.updateCB, q=True, v=True):
					rig = asset.Asset(item)
					if rig.UpdateToLatest():
						self.SaveVersion()

			mc.select(masterNode)

			#mc.confirmDialog(message="exporting %s from %s" % (masterNode, mc.file(q=True, loc=True)))
			self.RunExportCommand(1)

	def RefreshQueueList(self, *args):
		self.queueTSL.clear()
		for item in self.batchExportItems:
			self.queueTSL.append( "%s - %s - %s - %s" % (item["asset"],item["animation"],item["variation"],item["version"]))

		if len(self.batchExportItems) > 0:
			mc.frameLayout(self.exportQueueFrame, e=True, collapse=False)
		else:
			mc.frameLayout(self.exportQueueFrame, e=True, collapse=True)

	# arg 1:
	# 0 is 
	def RunExportCommand(self, *args):
		print "args = {}".format(args)

		#exec(self.exportCommand)
		import cgm.core.tools.bakeAndPrep as bakeAndPrep
		import cgm.core.mrs.Shots as SHOTS

		exportObjs = mc.ls(sl=True)

		addNamespaceSuffix = False
		exportFBXFile = False
		exportAsRig = False
		exportAsCutscene = False

		if(args[0] > 0):
			exportFBXFile = True

		if( len(exportObjs) > 1 ):
			result = mc.confirmDialog(
					title='Multiple Object Selected',
					message='Will export in cutscene mode, is this what you intended? If not, hit Cancel, select one object and try again.',
					button=['Yes', 'Cancel'],
					defaultButton='Yes',
					cancelButton='Cancel',
					dismissString='Cancel')

			if result != 'Yes':
				return False

			addNamespaceSuffix = True
			exportAsCutscene = True

		if(args[0] == 2):
			addNamespaceSuffix = True
			exportAsCutscene = True
		if(args[0] == 3):
			exportAsRig = True

		# make the relevant directories if they dont exist
		categoryExportPath = os.path.normpath(os.path.join( self.exportDirectory, self.category))
		if not os.path.exists(categoryExportPath):
			os.mkdir(categoryExportPath)
		exportAssetPath = os.path.normpath(os.path.join( categoryExportPath, self.assetList['scrollList'].getSelectedItem()))
		if not os.path.exists(exportAssetPath):
			os.mkdir(exportAssetPath)
		exportAnimPath = os.path.normpath(os.path.join(exportAssetPath, 'animation'))
		if not os.path.exists(exportAnimPath):
			os.mkdir(exportAnimPath)
			# create empty file so folders are checked into source control
			f = open(os.path.join(exportAnimPath, "filler.txt"),"w")
			f.write("filler file")
			f.close()
		if exportAsCutscene:
			exportAnimPath = os.path.normpath(os.path.join(exportAnimPath, self.animationList['scrollList'].getSelectedItem()))
			if not os.path.exists(exportAnimPath):
				os.mkdir(exportAnimPath)

		exportFiles = []

		# rename for safety
		loc = mc.file(q=True, loc=True)
		base, ext = os.path.splitext(loc)
		bakedLoc = "%s_baked%s" % (base, ext)

		mc.file(rn=bakedLoc)

		for obj in exportObjs:
			mc.select(obj)
			bakeAndPrep.Bake()

		for obj in exportObjs:
			mc.select(obj)

			#assetName = metaTag.GetTag(node.Node(obj), "assetName")
			#if not assetName:
			#	assetName = obj.split(':')[0].split('|')[-1]
			assetName = obj.split(':')[0].split('|')[-1]
			
			exportFile = os.path.normpath(os.path.join(exportAnimPath, self.exportFileName) )

			if( addNamespaceSuffix ):
				exportFile = exportFile.replace(".fbx", "_%s.fbx" % assetName )
			if( exportAsRig ):
				exportFile = os.path.normpath(os.path.join(exportAssetPath, '{}_rig.fbx'.format( assetName )))

			bakeAndPrep.Prep()

			exportObjs = mc.ls(sl=True)

			# topExportObjs = []
			# for obj in exportObjs:
			# 	longName = mc.ls(obj, l=True)[0]
			# 	memberOfHeirarchy = False
			# 	for compareObj in exportObjs:
			# 		if obj == compareObj:
			# 			continue
			# 		if compareObj in longName:
			# 			memberOfHeirarchy = True
			# 			break
			# 	if not memberOfHeirarchy:
			# 		topExportObjs.append(obj)

			# mc.select(topExportObjs)
			for obj in exportObjs:
				try:
					mc.parent(obj, w=True)
				except:
					print "%s already a child of 'world'" % obj
			
			mc.select(exportObjs, hi=True)
			
			'''
			if os.path.exists(self.exportFile):
				result = mc.confirmDialog(
						title='File Exists',
						message='Overwrite?',
						button=['Yes', 'Cancel'],
						defaultButton='Yes',
						cancelButton='Cancel',
						dismissString='Cancel')

				if result != 'Yes':
					return False
			'''
			
			if(exportFBXFile):
				mel.eval('FBXExportSplitAnimationIntoTakes -c')
				animList = SHOTS.AnimList()
				for shot in animList.shotList:
					mel.eval('FBXExportSplitAnimationIntoTakes -v \"{}\" {} {}'.format(shot[0], shot[1][0], shot[1][1]))

				#mc.file(exportFile, force=True, options="v=0;", exportSelected=True, pr=True, type="FBX export")
				print 'FBXExport -f \"{}\" -s'.format(exportFile)
				mel.eval('FBXExport -f \"{}\" -s'.format(exportFile.replace('\\', '/')))
			
		return True

def PurgeData():
	optionVarDirStore           = cgmMeta.cgmOptionVar("cgmVar_sceneUI_directory_list", varType = "string")
	optionVarDirStore.purge()
	optionVarLastDirStore       = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_directory", varType = "string")
	optionVarLastDirStore.purge()
	optionVarLastAssetStore     = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_asset", varType = "string")
	optionVarLastAssetStore.purge()
	optionVarLastAnimStore      = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_animation", varType = "string")
	optionVarLastAnimStore.purge()
	optionVarLastVariationStore = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_variation", varType = "string")
	optionVarLastVariationStore.purge()
	optionVarLastVersionStore   = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_version", varType = "string")
	optionVarLastVersionStore.purge()
	optionVarExportDirStore     = cgmMeta.cgmOptionVar("cgmVar_sceneUI_export_directory", varType = "string")
	optionVarExportDirStore.purge()
	showBakedStore              = cgmMeta.cgmOptionVar("cgmVar_sceneUI_show_baked", defaultValue = 0)
	showBakedStore.purge()
	categoryStore               = cgmMeta.cgmOptionVar("cgmVar_sceneUI_category", defaultValue = 0)
	categoryStore.purge()
	