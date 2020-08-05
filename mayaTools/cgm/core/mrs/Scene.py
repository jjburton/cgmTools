import maya.cmds as mc
import maya.mel as mel
import pprint
from functools import partial
import os
import time
from datetime import datetime
import json

from shutil import copyfile
#import fnmatch
import cgm.lib.pyui as pyui
#import subprocess
import re
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.lib import asset_utils as ASSET
from cgm.core.tools import Project as Project
from cgm.core.mrs.lib import batch_utils as BATCH
from cgm.core import cgm_General as cgmGEN
from cgm.core.lib import math_utils as MATH

import Red9.core.Red9_General as r9General

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

import cgm.core.cgmPy.path_Utils as PATHS
import cgm.images as cgmImages

mImagesPath = PATHS.Path(cgmImages.__path__[0])

#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================


#>>> Root settings =============================================================
__version__ = "1.1.2020.06.12"
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
		self.categoryList                = ["Character", "Environment", "Props"]
		self.categoryIndex               = 0

		self.subTypes                    = ['animation']
		self.subTypeIndex                = 0

		self.optionVarProjectStore       = cgmMeta.cgmOptionVar("cgmVar_projectCurrent", varType = "string")
		self.optionVarLastAssetStore     = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_asset", varType = "string")
		self.optionVarLastAnimStore      = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_animation", varType = "string")
		self.optionVarLastVariationStore = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_variation", varType = "string")
		self.optionVarLastVersionStore   = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_version", varType = "string")
		self.showAllFilesStore           = cgmMeta.cgmOptionVar("cgmVar_sceneUI_show_all_files", defaultValue = 0)
		self.removeNamespaceStore        = cgmMeta.cgmOptionVar("cgmVar_sceneUI_remove_namespace", defaultValue = 0)
		self.zeroRootStore               = cgmMeta.cgmOptionVar("cgmVar_sceneUI_zero_root", defaultValue = 0)
		self.useMayaPyStore              = cgmMeta.cgmOptionVar("cgmVar_sceneUI_use_mayaPy", defaultValue = 0)
		self.categoryStore               = cgmMeta.cgmOptionVar("cgmVar_sceneUI_category", defaultValue = 0)
		self.subTypeStore                = cgmMeta.cgmOptionVar("cgmVar_sceneUI_subType", defaultValue = 0)
		self.alwaysSendReferenceFiles    = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_version", defaultValue = 0)
		self.showDirectoriesStore        = cgmMeta.cgmOptionVar("cgmVar_sceneUI_show_directories", defaultValue = 0)
		self.displayDetailsStore         = cgmMeta.cgmOptionVar("cgmVar_sceneUI_display_details", defaultValue = 1)
		self.bakeSet                     = cgmMeta.cgmOptionVar('cgm_bake_set', varType="string",defaultValue = 'bake_tdSet')
		self.deleteSet                   = cgmMeta.cgmOptionVar('cgm_delete_set', varType="string",defaultValue = 'delete_tdSet')
		self.exportSet                   = cgmMeta.cgmOptionVar('cgm_export_set', varType="string",defaultValue = 'export_tdSet') 

		## sizes
		self.__itemHeight                = 35
		self.__cw1                       = 125

		# UI elements
		self.assetList                   = None #pyui.SearchableList()
		self.subTypeSearchList           = None #pyui.SearchableList()
		self.variationList               = None #pyui.SearchableList()
		self.versionList                 = None #pyui.SearchableList()
		self.queueTSL                    = None #pyui.UIList()
		self.updateCB                    = None
		self.menuBarLayout               = None
		self.uiMenu_FileMenu             = None
		self.uiMenu_ToolsMenu            = None
		self.uiMenu_OptionsMenu          = None
		self.categoryBtn                 = None
		self.subTypeBtn                  = None
		self.exportQueueFrame            = None
		self.categoryMenu                = None
		self.categoryMenuItemList        = []
		self.subTypeMenuItemList         = []
		self.sendToProjectMenuItemList   = []
		self.assetRigMenuItemList        = []
		self.assetReferenceRigMenuItemList  = []
		self.sendToProjectMenu           = None

		self.project                     = None
		self.assetMetaData               = {}

		self.exportCommand               = ""

		self.showAllFilesOption          = None
		self.removeNamespaceOption       = None
		self.zeroRootOption              = None
		self.useMayaPyOption             = None
		self.showDirectoriesOption       = None
		
		self.showDirectories             = self.showDirectoriesStore.getValue()
		self.displayDetails              = self.displayDetailsStore.getValue()

		self.showAllFiles                = self.showAllFilesStore.getValue()
		self.removeNamespace             = self.removeNamespaceStore.getValue()
		self.zeroRoot                    = self.zeroRootStore.getValue()
		self.useMayaPy                   = self.useMayaPyStore.getValue()

		self.fileListMenuItems           = []
		self.batchExportItems            = []

		self.exportDirectory             = None

		self.v_bgc                       = [.6,.3,.3]


	def post_init(self,*args,**kws):
		if self.optionVarProjectStore.getValue():
			self.LoadProject(self.optionVarProjectStore.getValue())
		else:
			mPathList = cgmMeta.pathList('cgmProjectPaths')
			self.LoadProject(mPathList.mOptionVar.value[0])

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
	def selectedAsset(self):
		return self.assetList['scrollList'].getSelectedItem()

	@property
	def assetDirectory(self):
		return os.path.normpath(os.path.join( self.categoryDirectory, self.assetList['scrollList'].getSelectedItem() )) if self.assetList['scrollList'].getSelectedItem() else None
	
	@property
	def selectedSubType(self):
		return self.subTypeSearchList['scrollList'].getSelectedItem()	

	@property
	def subTypeDirectory(self):
		if self.hasSub:
			if self.subTypeSearchList['scrollList'].getSelectedItem():
				return os.path.normpath(os.path.join( self.assetDirectory, self.subType, self.subTypeSearchList['scrollList'].getSelectedItem() ))
			else:
				return None
		else:
			return os.path.normpath(os.path.join( self.assetDirectory, self.subType ))

	@property
	def selectedVariation(self):
		return self.variationList['scrollList'].getSelectedItem()

	@property
	def variationDirectory(self):
		return os.path.normpath(os.path.join( self.subTypeDirectory, self.variationList['scrollList'].getSelectedItem() )) if self.variationList['scrollList'].getSelectedItem() else None

	@property
	def selectedVersion(self):
		return self.versionList['scrollList'].getSelectedItem()

	@property
	def versionFile(self):
		if self.hasSub:
			if self.hasVariant:
				return os.path.normpath(os.path.join( self.variationDirectory, self.versionList['scrollList'].getSelectedItem() )) if self.versionList['scrollList'].getSelectedItem() else None
			else:
				return os.path.normpath(os.path.join( self.subTypeDirectory, self.versionList['scrollList'].getSelectedItem() )) if self.versionList['scrollList'].getSelectedItem() else None
		else:
			return os.path.normpath(os.path.join( self.subTypeDirectory, self.subTypeSearchList['scrollList'].getSelectedItem() )) if self.subTypeSearchList['scrollList'].getSelectedItem() else None

	@property
	def exportFileName(self):
		if self.hasSub:
			if self.hasVariant:
				return '{0}_{1}_{2}.fbx'.format(self.assetList['scrollList'].getSelectedItem(), self.subTypeSearchList['scrollList'].getSelectedItem(), self.variationList['scrollList'].getSelectedItem())
			else:
				return '{0}_{1}.fbx'.format(self.assetList['scrollList'].getSelectedItem(), self.subTypeSearchList['scrollList'].getSelectedItem())
		else:
			return '{0}_{1}.fbx'.format(self.assetList['scrollList'].getSelectedItem(), self.subType)
		

	@property
	def category(self):
		return self.categoryList[self.categoryIndex] if len(self.categoryList) > self.categoryIndex else self.categoryList[0]

	@property
	def subType(self):
		return self.subTypes[min(self.subTypeIndex, len(self.subTypes)-1)] if self.subTypes else None
	
	@property
	def hasSub(self):
		try:
			r = self.project.assetType_get(self.category)['content'][self.subTypeIndex].get('hasSub', False)
			return r
		except:
			return True
	
	@property
	def hasVariant(self):
		try:
			r = self.project.assetType_get(self.category)['content'][self.subTypeIndex].get('hasVariant', False)
			return r
		except:
			return True
	
	def HasSub(self, category, subType):
		try:
			hasSub = True
			for sub in self.project.assetType_get(category)['content']:
				if sub['n'] == subType:
					hasSub = sub.get('hasSub', True)
			return hasSub
		except:
			return True
	
	def LoadOptions(self, *args):
		self.showAllFiles    = bool(self.showAllFilesStore.getValue())
		self.categoryIndex   = int(self.categoryStore.getValue())
		self.subTypeIndex    = int(self.subTypeStore.getValue())
		self.removeNamespace = bool(self.removeNamespaceStore.getValue())
		self.zeroRoot        = bool(self.zeroRootStore.getValue())
		self.useMayaPy       = bool(self.useMayaPyStore.getValue())
		self.showDirectories = bool(self.showDirectoriesStore.getValue())
		self.displayDetails  = bool(self.displayDetailsStore.getValue())

		if self.showAllFilesOption:
			self.showAllFilesOption(e=True, checkBox = self.showAllFiles)
		if self.removeNamespaceOption:
			self.removeNamespaceOption(e=True, checkBox = self.removeNamespace)
		if self.zeroRootOption:
			self.zeroRootOption(e=True, checkBox = self.zeroRoot)
			
		self.SetSubType(self.subTypeIndex)
		self.buildMenu_subTypes()
		self.SetCategory(self.categoryIndex)
		self.LoadPreviousSelection()
		self.uiFunc_showDirectories(self.showDirectories)	
		self.uiFunc_displayDetails(self.displayDetails)
			
		self.setTitle('%s - %s' % (self.WINDOW_TITLE, self.project.d_project['name']))

	def SaveOptions(self, *args):
		log.info( "Saving options" )
		self.showAllFiles = self.showAllFilesOption( q=True, checkBox=True ) if self.showAllFilesOption else False
		self.removeNamespace = self.removeNamespaceOption( q=True, checkBox=True ) if self.removeNamespaceOption else False
		self.zeroRoot = self.zeroRootOption( q=True, checkBox=True ) if self.zeroRootOption else False

		self.useMayaPy = self.useMayaPyOption( q=True, checkBox=True ) if self.useMayaPyOption else False
		self.showDirectories = self.showDirectoriesOption( q=True, checkBox=True ) if self.showDirectoriesOption else False

		self.showAllFilesStore.setValue(self.showAllFiles)
		self.removeNamespaceStore.setValue(self.removeNamespace)
		self.zeroRootStore.setValue(self.zeroRoot)
		self.useMayaPyStore.setValue(self.useMayaPy)
		self.showDirectoriesStore.setValue(self.showDirectories)
		self.displayDetailsStore.setValue(self.displayDetails)
		
		# self.optionVarExportDirStore.setValue( self.exportDirectory )
		self.categoryStore.setValue( self.categoryIndex )
		self.subTypeStore.setValue( self.subTypeIndex )
		self.uiFunc_showDirectories( self.showDirectories )
		self.uiFunc_displayDetails( self.displayDetails )

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
		log.info( "Setting delete set to: %s" % deleteSet )
		self.deleteSet.setValue(deleteSet)

	def SetBakeSet(self, *args):
		sel = mc.ls(sl=True)
		bakeSet = sel[0].split(':')[-1]
		log.info( "Setting bake set to: %s" % bakeSet )
		self.bakeSet.setValue(bakeSet)

	def SetExportSet(self, *args):
		sel = mc.ls(sl=True)
		exportSet = sel[0].split(':')[-1]
		log.info( "Setting geo set to: %s" % exportSet )
		self.exportSet.setValue(exportSet)

	def build_layoutWrapper(self,parent):

		_ParentForm = mUI.MelFormLayout(self,ut='cgmUISubTemplate')

		_headerColumn = mUI.MelColumnLayout(_ParentForm,useTemplate = 'cgmUISubTemplate')

		_imageFailPath = os.path.join(mImagesPath.asFriendly(),'cgm_project.png')
		imageRow = mUI.MelHRowLayout(_headerColumn,bgc=self.v_bgc)

		#mUI.MelSpacer(imageRow,w=10)
		self.uiImage_ProjectRow = imageRow
		self.uiImage_Project= mUI.MelImage(imageRow,w=350, h=50)
		self.uiImage_Project.setImage(_imageFailPath)
		#mUI.MelSpacer(imageRow,w=10)	
		imageRow.layout()

		self._detailsColumn = mUI.MelScrollLayout(_ParentForm,useTemplate = 'cgmUISubTemplate', w=294)
			
		_MainForm = mUI.MelFormLayout(_ParentForm,ut='cgmUITemplate')

		##############################
		# Top Column Layout 
		##############################
	
		self._detailsToggleBtn = mUI.MelButton(_MainForm, ut = 'cgmUITemplate', label="<", w=15, bgc=(1.0, .445, .08), c = lambda *a:mc.evalDeferred(self.uiFunc_toggleDisplayInfo,lp=True))	
	
		_directoryColumn = mUI.MelColumnLayout(_MainForm,useTemplate = 'cgmUISubTemplate')
		
		self._uiRow_dir = mUI.MelHSingleStretchLayout(_directoryColumn)

		mUI.MelLabel(self._uiRow_dir,l='Directory', w=100)
		self.directoryTF = mUI.MelTextField(self._uiRow_dir, editable = False, bgc=(.8,.8,.8))
		self.directoryTF.setValue( self.directory )

		mUI.MelSpacer(self._uiRow_dir,w=5)

		self._uiRow_dir.setStretchWidget(self.directoryTF)
		self._uiRow_dir.layout()

		self._uiRow_export = mUI.MelHSingleStretchLayout(_directoryColumn)
		
		mUI.MelLabel(self._uiRow_export,l='Export Dir', w=100)
		self.exportDirectoryTF = mUI.MelTextField(self._uiRow_export, editable = False, bgc=(.8,.8,.8))
		self.exportDirectoryTF.setValue( self.exportDirectory )

		mUI.MelSpacer(self._uiRow_export,w=5)                      

		self._uiRow_export.setStretchWidget(self.exportDirectoryTF)

		self._uiRow_export.layout()

		self._uiRow_export(e=True, vis=self.showDirectories)
		self._uiRow_dir(e=True, vis=self.showDirectories)

		##############################
		# Main Asset Lists 
		##############################
		self._assetsForm = mUI.MelFormLayout(_MainForm,ut='cgmUISubTemplate', numberOfDivisions=100) #mc.columnLayout(adjustableColumn=True)

		# Category
		_catForm = mUI.MelFormLayout(self._assetsForm,ut='cgmUISubTemplate')
		self.categoryBtn = mUI.MelButton(_catForm,
		                                  label=self.category,ut='cgmUITemplate',
		                                  ann='Select the asset category')

		self.categoryMenu = mUI.MelPopupMenu(self.categoryBtn, button=1 )
		# for i,category in enumerate(self.categoryList):
		# 	self.categoryMenuItemList.append( mUI.MelMenuItem(self.categoryMenu, label=category, c=partial(self.SetCategory,i)) )
		# 	if i == self.categoryIndex:
		# 		self.categoryMenuItemList[i]( e=True, enable=False)

		self.assetList = self.build_searchable_list(_catForm, sc=self.LoadSubTypeList)

		self.assetTSLpum = mUI.MelPopupMenu(self.assetList['scrollList'], pmc=self.UpdateAssetTSLPopup)

		self.assetButton = mUI.MelButton(_catForm, ut='cgmUITemplate', label="New Asset", command=self.CreateAsset)

		_catForm( edit=True, 
		          attachForm=[
		              (self.categoryBtn, 'top', 0), 
		                      (self.categoryBtn, 'left', 0), 
		                    (self.categoryBtn, 'right', 0), 
		                        (self.assetList['formLayout'], 'left', 0),
		                        (self.assetList['formLayout'], 'right', 0),
		                        (self.assetButton, 'bottom', 0), 
		                        (self.assetButton, 'right', 0), 
		                        (self.assetButton, 'left', 0)], 
		          attachControl=[
		                      (self.assetList['formLayout'], 'top', 0, self.categoryBtn),
		                    (self.assetList['formLayout'], 'bottom', 0, self.assetButton)] )


		# SubTypes
		_animForm = mUI.MelFormLayout(self._assetsForm,ut='cgmUISubTemplate')
		self.subTypeBtn = mUI.MelButton( _animForm,
		                         label=self.subType,ut='cgmUITemplate',
		                         ann='Select the sub type', en=True )
		
		self.subTypeMenu = mUI.MelPopupMenu(self.subTypeBtn, button=1 )
		# for i,subType in enumerate(self.subTypes):
		# 	self.subTypeMenuItemList.append( mUI.MelMenuItem(self.subTypeMenu, label=subType, c=partial(self.SetSubType,i)) )
		# 	if i == self.subTypeIndex:
		# 		self.subTypeMenuItemList[i]( e=True, enable=False)


		self.subTypeSearchList = self.build_searchable_list(_animForm, sc=self.LoadVariationList)

		pum = mUI.MelPopupMenu(self.subTypeSearchList['scrollList'])
		mUI.MelMenuItem(pum, label="Open In Explorer", command=self.OpenSubTypeDirectory )
		mUI.MelMenuItem( pum, label="Send Last To Queue", command=self.AddLastToExportQueue )
		self._referenceSubTypePUM = mUI.MelMenuItem(pum, label="Reference File", command=self.ReferenceFile, en=False )
		
		self.subTypeButton = mUI.MelButton(_animForm, ut='cgmUITemplate', label="New Animation", command=self.CreateSubAsset)

		_animForm( edit=True, 
		           attachForm=[
		               (self.subTypeBtn, 'top', 0), 
		                       (self.subTypeBtn, 'left', 0), 
		                    (self.subTypeBtn, 'right', 0), 
		                        (self.subTypeSearchList['formLayout'], 'left', 0),
		                        (self.subTypeSearchList['formLayout'], 'right', 0),
		                        (self.subTypeButton, 'bottom', 0), 
		                        (self.subTypeButton, 'right', 0), 
		                        (self.subTypeButton, 'left', 0)], 
		           attachControl=[
		                       (self.subTypeSearchList['formLayout'], 'top', 0, self.subTypeBtn),
		                    (self.subTypeSearchList['formLayout'], 'bottom', 0, self.subTypeButton)] )

		# Variation
		_variationForm = mUI.MelFormLayout(self._assetsForm,ut='cgmUISubTemplate')
		_variationBtn = mUI.MelButton(_variationForm,
		                              label='Variation',ut='cgmUITemplate',
		                              ann='Select the asset variation', en=False)

		self.variationList = self.build_searchable_list(_variationForm, sc=self.LoadVersionList)

		pum = mUI.MelPopupMenu(self.variationList['scrollList'])
		mUI.MelMenuItem(pum, label="Open In Explorer", command=self.OpenVariationDirectory )
		mUI.MelMenuItem( pum, label="Send Last To Queue", command=self.AddLastToExportQueue )

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
		_versionForm = mUI.MelFormLayout(self._assetsForm,ut='cgmUISubTemplate')
		_versionBtn = mUI.MelButton(_versionForm,
		                            label='Version',ut='cgmUITemplate',
		                            ann='Select the asset version', en=False)

		self.versionList = self.build_searchable_list(_versionForm, sc=self.uiFunc_selectVersionList)

		pum = mUI.MelPopupMenu(self.versionList['scrollList'], pmc=self.UpdateVersionTSLPopup)
		mUI.MelMenuItem(pum, label="Open In Explorer", command=self.OpenVersionDirectory )
		mUI.MelMenuItem(pum, label="Reference File", command=self.ReferenceFile )
		self.sendToProjectMenu = mUI.MelMenuItem(pum, label="Send To Project", subMenu=True )		
		mUI.MelMenuItem( pum, label="Send Last To Queue", command=self.AddLastToExportQueue )
		
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


		self._subForms = [_catForm,_animForm,_variationForm,_versionForm]

		self.buildAssetForm()


		##############################
		# Bottom 
		##############################
		_bottomColumn    = mUI.MelColumnLayout(_MainForm,useTemplate = 'cgmUISubTemplate', adjustableColumn=True)#mc.columnLayout(adjustableColumn = True)

		mc.setParent(_bottomColumn)
		cgmUI.add_LineSubBreak()

		_row = mUI.MelHSingleStretchLayout(_bottomColumn,ut='cgmUISubTemplate',padding = 5)

		#mUI.MelSpacer(_row,w=0)
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

		#mUI.MelSpacer(_row,w=0)

		_row.layout()

		mc.setParent(_bottomColumn)
		cgmUI.add_LineSubBreak()

		#_row = mUI.MelHSingleStretchLayout(_bottomColumn,ut='cgmUISubTemplate',padding = 5)
		_row = mUI.MelColumnLayout(_bottomColumn,useTemplate = 'cgmUISubTemplate') 
		#mUI.MelSpacer(_row,w=5)
		
		self.loadBtn = mUI.MelButton(_row, ut = 'cgmUITemplate', label="Load File", c=self.LoadFile, h=self.__itemHeight)
		#_row.setStretchWidget( self.loadBtn )

		#mUI.MelSpacer(_row,w=5)

		#_row.layout()

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

		_footer = cgmUI.add_cgmFooter(_ParentForm)            

		_MainForm( edit=True, 
		           attachForm=[
		                        (_directoryColumn, 'top', 0), 
		                        (_directoryColumn, 'left', 0), 
		                        (_bottomColumn, 'left', 0),
								(_bottomColumn, 'bottom', 0),
		                        (self._assetsForm, 'left', 0),
		                        
								(self._detailsToggleBtn, 'right', 0),
								(self._detailsToggleBtn, 'top', 0),
								(self._detailsToggleBtn, 'bottom', 0)], 
		           attachControl=[
		                        (self._assetsForm, 'top', 0, _directoryColumn),
		                        (self._assetsForm, 'bottom', 0, _bottomColumn),
								(self._assetsForm, 'right', 0, self._detailsToggleBtn),
								(_bottomColumn, 'right', 0, self._detailsToggleBtn),
								(_directoryColumn, 'right', 0, self._detailsToggleBtn)])

		_ParentForm( edit=True,
					 attachForm=[						 
		                        (_headerColumn, 'left', 0),
		                        (_headerColumn, 'right', 0),
		                        (_headerColumn, 'top', 0),
								(self._detailsColumn, 'right', 0),
								(_MainForm, 'left', 0),
						        (_footer, 'left', 0),
		                        (_footer, 'right', 0),
		                        (_footer, 'bottom', 0)],
					 attachControl=[(_MainForm, 'top', 0, _headerColumn),
									(_MainForm, 'bottom', 0, _footer),
									(_MainForm, 'right', 0, self._detailsColumn),
									(self._detailsColumn, 'top', 0, _headerColumn),
									(self._detailsColumn, 'bottom', 1, _footer)])
	def show( self ):		
		self.setVisibility( True )
		self.buildMenu_options()
		self.buildDetailsColumn()


	#=========================================================================
	# Menu Building
	#=========================================================================
	def buildAssetForm(self):
		attachForm = []
		attachControl = []
		attachPosition = []

		attachedForms = []

		for form in self._subForms:
			vis = mc.formLayout(form, q=True, visible=True)
			if vis:
				attachedForms.append(form)

		for i,form in enumerate(attachedForms):
			if i == 0:
				attachForm.append( (form, 'left', 1) )
			else:
				attachControl.append( (form, 'left', 5, attachedForms[i-1]) )

			attachForm.append((form, 'top', 0))
			attachForm.append((form, 'bottom', 5))

			if i == len(attachedForms)-1:
				attachForm.append( (form, 'right', 1) )
			else:
				attachPosition.append( (form, 'right', 5, (100 / len(attachedForms)) * (i+1)) )

		self._assetsForm( edit=True, attachForm = attachForm, attachControl = attachControl, attachPosition = attachPosition)

	def build_menus(self):
		_str_func = 'build_menus[{0}]'.format(self.__class__.TOOLNAME)            
		log.info("|{0}| >>...".format(_str_func))   

		self.uiMenu_FileMenu = mUI.MelMenu( l='Projects', pmc=self.buildMenu_file)		        
		self.uiMenu_OptionsMenu = mUI.MelMenu( l='Options', pmc=self.buildMenu_options)
		self.uiMenu_ToolsMenu = mUI.MelMenu( l='Tools', pmc=self.buildMenu_tools)  
		self.uiMenu_HelpMenu = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)   

	def buildMenu_help( self, *args):
		self.uiMenu_HelpMenu.clear()

		_log = mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Logs:",subMenu=True)


		mUI.MelMenuItem( _log, l="Dat",
		                 c=lambda *a: self.project.log_self())

		mc.menuItem(parent=self.uiMenu_HelpMenu,
		            l = 'Get Help',
		            c='import webbrowser;webbrowser.open("https://http://docs.cgmonks.com/mrs.html");',                        
		                    rp = 'N')    
		mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Log Self",
		                 c=lambda *a: cgmUI.log_selfReport(self) )
	
	#@cgmGEN.Timer
	def buildMenu_file( self, *args):
		self.uiMenu_FileMenu.clear()
		#>>> Reset Options			

		mPathList = cgmMeta.pathList('cgmProjectPaths')

		project_names = []
		for i,p in enumerate(mPathList.mOptionVar.value):
			proj = Project.data(filepath=p)
			name = proj.d_project['name']
			project_names.append(name)
			en = False
			_path = proj.userPaths_get().get('content') or False
			if _path and os.path.exists(_path):
				en=True
			else:
				log.warning("'{0}' Missing content path".format(name))
			mUI.MelMenuItem( self.uiMenu_FileMenu, en=en, l=name if project_names.count(name) == 1 else '%s {%i}' % (name,project_names.count(name)-1),
			                 c = partial(self.LoadProject,p))

		mUI.MelMenuItemDiv( self.uiMenu_FileMenu )

		mUI.MelMenuItem( self.uiMenu_FileMenu, l="MRSProject",
		                 c = lambda *a:mc.evalDeferred(Project.ui,lp=True))                         

	def buildMenu_options( self, *args):
		self.uiMenu_OptionsMenu.clear()
		#>>> Reset Options		

		self.showAllFilesOption = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Show all files",
		                                        checkBox=self.showAllFiles,
		                                        c = lambda *a:mc.evalDeferred(self.uiFunc_showAllFiles,lp=True))
		self.removeNamespaceOption = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Remove namespace upon export",
		                                              checkBox=self.removeNamespace,
		                                              c = lambda *a:mc.evalDeferred(self.SaveOptions,lp=True))
		self.zeroRootOption = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Zero root upon export",
		                                              checkBox=self.zeroRoot,
		                                              c = lambda *a:mc.evalDeferred(self.SaveOptions,lp=True))
		self.useMayaPyOption =  mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Use MayaPy",
		                                         checkBox=self.useMayaPy,
		                                         c = lambda *a:mc.evalDeferred(self.SaveOptions,lp=True))
		self.showDirectoriesOption =  mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Show Directories",
		                                         checkBox=self.showDirectories,
		                                         c = lambda *a:mc.evalDeferred(self.SaveOptions,lp=True))
	
	def uiFunc_showAllFiles(self):
		self.SaveOptions()
		self.LoadVersionList()
		
	def uiFunc_selectVersionList(self):
		self.assetMetaData = self.getMetaDataFromFile()
		self.buildDetailsColumn()
		self.StoreCurrentSelection()
	
	def buildDetailsColumn(self):
		if not self._detailsColumn(q=True, vis=True):
			log.info("details column isn't visible")
			return
			
		self._detailsColumn.clear()
		
		mc.setParent(self._detailsColumn)
		
		mUI.MelLabel(self._detailsColumn,l='Details', h=15, ut = 'cgmUIHeaderTemplate')
		
		mc.setParent(self._detailsColumn)
		cgmUI.add_LineSubBreak()		
		
		thumb = self.getThumbnail()
		
		self.uiImage_Thumb = mUI.MelImage( self._detailsColumn, w=130, h=150 )
		self.uiImage_Thumb(e=True, vis=(thumb != None))

		if thumb:
			self.uiImage_Thumb.setImage(thumb)
			
		pum = mUI.MelPopupMenu(self.uiImage_Thumb)
		mUI.MelMenuItem(pum, label="Remake Thumbnail", command=cgmGEN.Callback(self.makeThumbnail) )		

		self.uiButton_MakeThumb = mUI.MelButton(self._detailsColumn, ut = 'cgmUITemplate', h=150, label="Make Thumbnail", c=cgmGEN.Callback(self.makeThumbnail), vis=(thumb == None))

		mc.setParent(self._detailsColumn)
		cgmUI.add_LineSubBreak()
		
		mUI.MelButton(self._detailsColumn, ut = 'cgmUITemplate', h=15, label="Refresh MetaData", c=cgmGEN.Callback(self.refreshMetaData) )
		
		mc.setParent(self._detailsColumn)
		cgmUI.add_LineSubBreak()	
		
		_row = mUI.MelHSingleStretchLayout(self._detailsColumn)
			
		mUI.MelLabel(_row,l='Asset', w=70)
		_row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('asset', ""), editable = False, bgc=(.8,.8,.8)))	
		mUI.MelSpacer(_row,w=5)

		_row.layout()

		_row = mUI.MelHSingleStretchLayout(self._detailsColumn)
			
		mUI.MelLabel(_row,l='Type', w=70)
		_row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('type', ""), editable = False, bgc=(.8,.8,.8)))	
		mUI.MelSpacer(_row,w=5)

		_row.layout()

		_row = mUI.MelHSingleStretchLayout(self._detailsColumn)
			
		mUI.MelLabel(_row,l='SubType', w=70)
		_row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('subType', ""), editable = False, bgc=(.8,.8,.8)))	
		mUI.MelSpacer(_row,w=5)

		_row.layout()
		
		if self.assetMetaData.get('subTypeAsset', None):
			_row = mUI.MelHSingleStretchLayout(self._detailsColumn)
				
			mUI.MelLabel(_row,l='SubAsset', w=70)
			_row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('subTypeAsset', ""), editable = False, bgc=(.8,.8,.8)))	
			mUI.MelSpacer(_row,w=5)
	
			_row.layout()	
		
		if self.assetMetaData.get('variation', None):
			_row = mUI.MelHSingleStretchLayout(self._detailsColumn)
				
			mUI.MelLabel(_row,l='Variation', w=70)
			_row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('variation', ""), editable = False, bgc=(.8,.8,.8)))	
			mUI.MelSpacer(_row,w=5)
	
			_row.layout()	

		_row = mUI.MelHSingleStretchLayout(self._detailsColumn)
			
		mUI.MelLabel(_row,l='User', w=70)
		_row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('user', ""), editable = False, bgc=(.8,.8,.8)))	
		mUI.MelSpacer(_row,w=5)

		_row.layout()	

		mUI.MelLabel(self._detailsColumn,l='Notes', w=70)
		
		_row = mUI.MelHSingleStretchLayout(self._detailsColumn)
		mUI.MelSpacer(_row,w=5)		
		noteField = mUI.MelScrollField(_row, h=150, text=self.assetMetaData.get('notes', ""), wordWrap=True, editable=True, bgc=(.8,.8,.8))
		noteField(e=True, changeCommand=cgmGEN.Callback( self.saveMetaNote,noteField ) )
		_row.setStretchWidget(noteField)
		mUI.MelSpacer(_row,w=5)
		_row.layout()
		
		if self.assetMetaData.get('references', None):
			mUI.MelLabel(self._detailsColumn,l='References', w=50)
			
			for ref in self.assetMetaData.get('references', []):
				_row = mUI.MelHSingleStretchLayout(self._detailsColumn)
				mUI.MelSpacer(_row,w=5)		
				_row.setStretchWidget(mUI.MelTextField(_row, text=ref, editable = False, bgc=(.8,.8,.8)))
				mUI.MelSpacer(_row,w=5)
				_row.layout()			

		if self.assetMetaData.get('shots', None):
			mUI.MelLabel(self._detailsColumn,l='Shots', w=50)
			
			for shot in self.assetMetaData.get('shots', []):
				_row = mUI.MelHRowLayout(self._detailsColumn, w=150)
				mUI.MelSpacer(_row,w=5)
				mUI.MelTextField(_row, text=shot[0], editable = False, bgc=(.8,.8,.8), w = 80)
				mUI.MelTextField(_row, text=shot[1][0], editable = False, bgc=(.8,.8,.8), w=40)
				mUI.MelTextField(_row, text=shot[1][1], editable = False, bgc=(.8,.8,.8), w=40)
				mUI.MelTextField(_row, text=shot[1][2], editable = False, bgc=(.8,.8,.8), w=40)
				mUI.MelSpacer(_row,w=5)
				_row.layout()

	def makeThumbnail(self):
		if self.versionFile:
			path, filename = os.path.split(self.versionFile)
			basefile = os.path.splitext(filename)[0]
			
			metaDir = os.path.join(path, 'meta')
			if not os.path.exists(metaDir):
				os.mkdir( os.path.join(path, 'meta') )
			
			thumbFile = os.path.join(path, 'meta', '{0}.bmp'.format(basefile))
			r9General.thumbNailScreen(thumbFile, 256, 256)		
			self.uiButton_MakeThumb(e=True, vis=False)
			self.uiImage_Thumb.setImage(thumbFile)
			self.uiImage_Thumb(e=True, vis=True)
	
	def getThumbnail(self):
		thumbFile = None
		
		if self.versionFile:
			path, filename = os.path.split(self.versionFile)
			basefile = os.path.splitext(filename)[0]
			thumbFile = os.path.join(path, 'meta', '{0}.bmp'.format(basefile))
			if not os.path.exists(thumbFile):
				thumbFile = None
		
		return thumbFile

	def getMetaDataFromCurrent(self):
		from cgm.core.mrs.Shots import AnimList
		import getpass
		
		#if os.path.normpath(self.versionFile) != os.path.normpath(mc.file(q=True, loc=True)):
			#mc.confirmDialog(title="No. Just no.", message="The open file doesn't match the selected file. I refuse to refresh this metaData with the wrong file. It just wouldn't feel right.", button=["Cancel", "Sorry"])
			#return
		
		data = {}
		data['asset'] = self.assetList['scrollList'].getSelectedItem()
		data['type'] = self.category
		data['subType'] = self.subType
		data['subTypeAsset'] = self.subTypeSearchList['scrollList'].getSelectedItem() if self.hasSub else ""
		data['variation'] = self.variationList['scrollList'].getSelectedItem() if self.hasVariant else ""
		data['user'] = getpass.getuser()

		data['saved'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
		data['notes'] = ""
		
		data['references'] = [os.path.normpath(x).replace(os.path.normpath(self.directory), "") for x in mc.file(q=True, r=True)]
		
		data['startTime'] = mc.playbackOptions(q=True, min=True)
		data['endTime'] = mc.playbackOptions(q=True, max=True)
		
		l = AnimList()
		data['shots'] = l.SortedList(1)
		
		return data

	def getMetaDataFromFile(self):
		_func_str = 'Scene.getMetaDataFromFile'
		
		metaFile = None
		
		data = {}
		
		if self.versionFile:
			path, filename = os.path.split(self.versionFile)
			basefile = os.path.splitext(filename)[0]
			metaFile = os.path.join(path, 'meta', '{0}.dat'.format(basefile))
			if not os.path.exists(metaFile):
				log.info("{0} | No meta file found".format(_func_str))
				metaFile = None
			else:
				f = open(metaFile, 'r')
				data = json.loads(f.read())
		else:
			log.info("{0} | No version file found".format(_func_str))
		return data

	def refreshMetaData(self):
		if os.path.normpath(self.versionFile) != os.path.normpath(mc.file(q=True, loc=True)):
			mc.confirmDialog(title="No. Just no.", message="The open file doesn't match the selected file. I refuse to refresh this metaData with the wrong file. It just wouldn't feel right.", button=["Cancel", "Sorry"])
			return
		
		notes = self.assetMetaData.get('notes', "")
		self.assetMetaData = self.getMetaDataFromCurrent()
		self.assetMetaData['notes'] = notes
		
		self.buildDetailsColumn()
		self.saveMetaData()
	
	def saveMetaNote(self, field):
		self.assetMetaData['notes'] = field.getValue()
		self.saveMetaData()
		
	def saveMetaData(self):
		if self.versionFile:
			path, filename = os.path.split(self.versionFile)
			basefile = os.path.splitext(filename)[0]
			
			metaDir = os.path.join(path, 'meta')
			if not os.path.exists(metaDir):
				os.mkdir( os.path.join(path, 'meta') )
			
			metaFile = os.path.join(path, 'meta', '{0}.dat'.format(basefile))
			f = open(metaFile, 'w')
			f.write( json.dumps(self.assetMetaData) )
			f.close()
			
			log.info('wrote file: {0}'.format(metaFile))
	
	def uiFunc_showDirectories(self, val):
		self._uiRow_dir(e=True, vis=val)
		self._uiRow_export(e=True, vis=val)
	
	def uiFunc_toggleDisplayInfo(self):
		self.displayDetails = not self.displayDetails
		self.SaveOptions()
	
	def uiFunc_displayDetails(self, val):
		self._detailsColumn(e=True, vis=val)
		self._detailsToggleBtn(e=True, label='>' if val else '<')
		
		if val:
			self.buildDetailsColumn()
		
	def buildMenu_tools( self, *args):
		self.uiMenu_ToolsMenu.clear()
		#>>> Reset Options		

		mUI.MelMenuItem( self.uiMenu_ToolsMenu, l="Set Export Sets",
		                 c = lambda *a:mc.evalDeferred(self.SetExportSets,lp=True))

		mUI.MelMenuItem( self.uiMenu_ToolsMenu, l="Update Selected Rigs",
		                 c = lambda *a:mc.evalDeferred(self.UpdateToLatestRig,lp=True))

		mUI.MelMenuItem( self.uiMenu_ToolsMenu, l="Remap Unlinked Textures",
		                 c = lambda *a:mc.evalDeferred(self.RemapTextures,lp=True))

		mUI.MelMenuItem( self.uiMenu_ToolsMenu, l="Verify Asset Dirs",
		                 c = cgmGEN.Callback(self.VerifyAssetDirs) )



	def RemapTextures(self, *args):
		import cgm.tools.findTextures as findTextures

		findTextures.FindAndRemapTextures()

	def buildMenu_category(self, *args):
		self.categoryMenu.clear()
		self.categoryMenuItemList = []

		for i,category in enumerate(self.categoryList):
			self.categoryMenuItemList.append( mUI.MelMenuItem(self.categoryMenu, label=category, c=partial(self.SetCategory,i)) )
			if i == self.categoryIndex:
				self.categoryMenuItemList[i]( e=True, enable=False)

	def buildMenu_subTypes(self, *args):
		self.subTypeMenu.clear()
		# for item in self.subTypeMenuItemList:
		# 	if mc.menuItem(item, q=True, exists=True):
		# 		mc.deleteUI(item)

		self.subTypeMenuItemList = []

		mc.setParent(self.subTypeMenu, menu=True)

		for i,subType in enumerate(self.subTypes):
			# mc.menuItem(label=subType, c=cgmGEN.Callback(self.SetSubType,i))
			self.subTypeMenuItemList.append( mc.menuItem(label=subType, enable=i!=self.subTypeIndex, c=cgmGEN.Callback(self.SetSubType,i)) ) #mUI.MelMenuItem(self.subTypeMenu, label=subType, c=partial(self.SetSubType,i)) )

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
		log.info( "Clearing search filter for %s with search term %s" % (searchableList['scrollList'], searchableList['searchField'].getValue()) )
		searchableList['searchField'].setValue("")
		selected = searchableList['scrollList'].getSelectedItem()
		searchableList['scrollList'].setItems(searchableList['items'])
		searchableList['scrollList'].selectByValue(selected)

	def SetCategory(self, index, *args):
		self.categoryIndex = index

		mc.button( self.categoryBtn, e=True, label=self.category )
		for i,category in enumerate(self.categoryMenuItemList):
			if i == self.categoryIndex:
				self.categoryMenuItemList[i]( e=True, enable=False)
			else:
				self.categoryMenuItemList[i]( e=True, enable=True)

		self.LoadCategoryList(self.directory)
	
		self.categoryStore.setValue(self.categoryIndex)

		# Set SubType
		try:
			self.subTypes = [x['n'] for x in self.project.assetType_get(self.category)['content']]
		except:
			self.subTypes = ['animation']

		if self.subTypeBtn(q=True, label=True) in self.subTypes:
			self.subTypeIndex = self.subTypes.index(self.subTypeBtn(q=True, label=True))
		else:
			self.subTypeIndex = min(self.subTypeIndex, len(self.subTypes)-1)
		self.SetSubType(self.subTypeIndex)
		self.buildMenu_subTypes()

	def LoadCategoryList(self, directory="", *args):
		if directory:		
			self.directory = directory

		charList = []

		categoryDirectory = os.path.join(self.directory, self.category)
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

		self.subTypeSearchList['items'] = []
		self.subTypeSearchList['scrollList'].clear()

		self.variationList['items'] = []
		self.variationList['scrollList'].clear()

		self.versionList['items'] = []
		self.versionList['scrollList'].clear()

		self.StoreCurrentSelection()

	def SetSubType(self, index, *args):
		self.subTypeIndex = index

		self.subTypeBtn( e=True, label=self.subType )

		if self.hasSub:
			self.subTypeButton(edit=True, label="New {0}".format(self.subType.capitalize()), command=self.CreateSubAsset)
		else:
			self.subTypeButton(edit=True, label="Save New Version", command=self.SaveVersion)

		self.LoadSubTypeList()

		self.subTypeStore.setValue(self.subTypeIndex)

		for i,item in enumerate(self.subTypeMenuItemList):
			mc.menuItem(item, e=True, enable= i != self.subTypeIndex)

		mc.formLayout( self._subForms[2], e=True, vis=self.hasVariant and self.hasSub )
		mc.formLayout( self._subForms[3], e=True, vis=self.hasSub )
		self.buildAssetForm()

	def LoadSubTypeList(self, *args):
		if not self.hasSub:
			self.LoadVersionList()
			self._referenceSubTypePUM(e=True, en=True)
			return
		
		self._referenceSubTypePUM(e=True, en=False)
		
		animList = []

		if self.categoryDirectory and self.assetList['scrollList'].getSelectedItem():
			charDir = os.path.normpath(os.path.join( self.categoryDirectory, self.assetList['scrollList'].getSelectedItem(), self.subType ))

			if os.path.exists(charDir):
				for d in os.listdir(charDir):
					#for ext in fileExtensions:
					#	if os.path.splitext(f)[-1].lower() == ".%s" % ext :
					if d[0] == '_' or d[0] == '.':
						continue

					animDir = os.path.normpath(os.path.join(charDir, d))
					if os.path.isdir(animDir):
						animList.append(d)

		self.subTypeSearchList['items'] = animList
		self.subTypeSearchList['scrollList'].clear()
		self.subTypeSearchList['scrollList'].setItems(animList)

		self.variationList['items'] = []
		self.variationList['scrollList'].clear()

		self.versionList['items'] = []
		self.versionList['scrollList'].clear()

		self.StoreCurrentSelection()

	def LoadVariationList(self, *args):
		if not self.hasSub:
			self.uiFunc_selectVersionList()
			return
		if not self.hasVariant:
			self.LoadVersionList()
			return

		variationList = []

		selectedVariation = self.variationList['scrollList'].getSelectedItem()

		self.variationList['items'] = []
		self.variationList['scrollList'].clear()

		if self.categoryDirectory and self.assetList['scrollList'].getSelectedItem() and self.subTypeSearchList['scrollList'].getSelectedItem():
			animationDir = self.subTypeDirectory

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

		self.variationList['scrollList'].selectByValue(selectedVariation) # if selectedVariation else variationList[0]

		self.versionList['items'] = []
		self.versionList['scrollList'].clear()

		self.LoadVersionList()

		if len(self.versionList['items']) > 0:
			self.versionList['scrollList'].selectByIdx( len(self.versionList['items'])-1 )

		self.StoreCurrentSelection()

	def LoadVersionList(self, *args):
		_str_func = 'Scene.LoadVersionList'
				
		searchDir = os.path.join(self.assetDirectory if self.assetDirectory else self.categoryDirectory, self.subType if self.subType else "")
		searchList = self.subTypeSearchList
		if self.hasSub:
			searchDir = self.subTypeDirectory
			searchList = self.versionList
		if self.hasVariant and self.hasSub:
			searchDir = self.variationDirectory

		if not searchDir:
			return
		
		versionList = []
		anims = []

		# populate animation info list
		fileExtensions = ['mb', 'ma']

		#log.info('{0} >> searchDir: {1}'.format(_str_func, searchDir))
		if os.path.exists(searchDir):
			# animDir = (self.variationDirectory if self.hasVariant else self.subTypeDirectory) if self.hasSub else self.categoryDirectory

			# if os.path.exists(animDir):
			for d in os.listdir(searchDir):
				if d[0] == '_' or d[0] == '.':
					continue
				
				if self.showAllFiles:
					anims.append(d)
				elif os.path.splitext(d)[-1].lower()[1:] in fileExtensions:
					if self.hasSub:
						if self.hasVariant:
							if '{0}_{1}_{2}_'.format(self.selectedAsset, self.selectedSubType, self.selectedVariation) in d:
								anims.append(d)
						else:
							if '{0}_{1}_'.format(self.selectedAsset, self.selectedSubType) in d:
								anims.append(d)							
					else:
						if '{0}_{1}_'.format(self.selectedAsset, self.subType) in d:
							anims.append(d)
							
		searchList['items'] = anims
		searchList['scrollList'].clear()
		searchList['scrollList'].setItems(anims)

		self.StoreCurrentSelection()

	def LoadFile(self, *args):
		if not self.assetList['scrollList'].getSelectedItem():
			log.warning( "No asset selected" )
			return
		if not self.subTypeSearchList['scrollList'].getSelectedItem():
			print "No animation selected"
			return
		if not self.versionList['scrollList'].getSelectedItem() and self.hasSub:
			print "No version selected"
			return

		mc.file(self.versionFile, o=True, f=True, ignoreVersion=True)

	def SetAnimationDirectory(self, *args):
		basicFilter = "*"
		x = mc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, fm=3)
		if x:
			self.LoadCategoryList(x[0])

	def GetPreviousDirectories(self, *args):
		if type(self.optionVarDirStore.getValue()) is list:
			return self.optionVarDirStore.getValue()
		else:
			return []

	def UpdateAssetList(self, charList):
		self.assetList['items'] = charList
		self.assetList['scrollList'].setItems(charList)

	# def GetPreviousDirectory(self, *args):
	# 	if self.optionVarLastDirStore.getValue():
	# 		return self.optionVarLastDirStore.getValue()
	# 	else:
	# 		return None

	def StoreCurrentSelection(self, *args):
		if self.assetList['scrollList'].getSelectedItem():
			self.optionVarLastAssetStore.setValue(self.assetList['scrollList'].getSelectedItem())
		#else:
		#	mc.optionVar(rm=self.optionVarLastAssetStore)

		if self.subTypeSearchList['scrollList'].getSelectedItem():
			self.optionVarLastAnimStore.setValue(self.subTypeSearchList['scrollList'].getSelectedItem())
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

		self.LoadSubTypeList()

		if self.optionVarLastAnimStore.getValue():
			self.subTypeSearchList['scrollList'].selectByValue( self.optionVarLastAnimStore.getValue() )
		
		self.LoadVariationList()
		
		if not self.hasSub:
			self.assetMetaData = self.getMetaDataFromFile()		
			return

		if self.optionVarLastVariationStore.getValue():
			self.variationList['scrollList'].selectByValue( self.optionVarLastVariationStore.getValue() )

		self.LoadVersionList()

		if self.optionVarLastVersionStore.getValue():
			self.versionList['scrollList'].selectByValue( self.optionVarLastVersionStore.getValue() )

		self.assetMetaData = self.getMetaDataFromFile()	

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
				for subType in self.subTypes:
					os.mkdir(os.path.normpath(os.path.join(charPath, subType)))

			self.LoadCategoryList(self.directory)

			self.assetList['scrollList'].selectByValue(charName)

	def CreateSubAsset(self, *args):
		if not self.assetDirectory:
			log.error("No asset selected.")
			return
		
		result = mc.promptDialog(
		    title='New {0}'.format(self.subType.capitalize()),
		    message='{0} Name:'.format(self.subType.capitalize()),
		            button=['OK', 'Cancel'],
		                        defaultButton='OK',
		                        cancelButton='Cancel',
		                        dismissString='Cancel')

		if result == 'OK':
			subTypeName = mc.promptDialog(query=True, text=True)
			subTypeDir = os.path.normpath(os.path.join(self.assetDirectory, self.subType)) if self.hasSub else os.path.normpath(self.assetDirectory)
			if not os.path.exists(subTypeDir):
				os.mkdir(subTypeDir)

			subTypePath = os.path.normpath(os.path.join(subTypeDir, subTypeName))
			if not os.path.exists(subTypePath):
				os.mkdir(subTypePath)

			self.LoadSubTypeList()
			
			self.subTypeSearchList['scrollList'].clearSelection()
			self.subTypeSearchList['scrollList'].selectByValue( subTypeName )

			if not self.hasVariant:
				self.CreateStartingFile()
				self.LoadVersionList()
	
	def CreateStartingFile(self):
		createPrompt = mc.confirmDialog(
			title='Create?',
			message='Save Current File Here?',
						button=['Yes', 'No'],
							defaultButton='No',
							cancelButton='No',
							dismissString='No')

		if createPrompt == "Yes":
			self.SaveVersion()
		
	def CreateVariation(self, *args):
		result = mc.promptDialog(
		    title='New Variation',
		    message='Variation Name:',
		            button=['OK', 'Cancel'],
		                        defaultButton='OK',
		                        cancelButton='Cancel',
		                        dismissString='Cancel')

		if result == 'OK':
			variationName = mc.promptDialog(query=True, text=True)
			variationDir = os.path.normpath( os.path.join(self.subTypeDirectory, variationName) )
			if not os.path.exists(variationDir):
				os.mkdir(variationDir)
				
				self.LoadVariationList()
				self.variationList['scrollList'].clearSelection()
				self.variationList['scrollList'].selectByValue(variationName)
				
				self.CreateStartingFile()
				
				self.LoadVersionList()

	def SaveVersion(self, *args):
		if not self.assetDirectory:
			log.error("No asset selected")
			return
		
		versionList = self.versionList if self.hasSub else self.subTypeSearchList
		existingFiles = versionList['items']

		#animationName = self.subTypeSearchList['scrollList'].getSelectedItem()
		wantedName = "%s_%s" % (self.assetList['scrollList'].getSelectedItem(), self.subTypeSearchList['scrollList'].getSelectedItem() if self.hasSub else self.subType)
		if self.hasVariant:
			wantedName = "%s_%s" % (wantedName, self.variationList['scrollList'].getSelectedItem())
		if len(existingFiles) == 0:
			wantedName = "%s_%02d.mb" % (wantedName, 1)
		else:
			currentFile = mc.file(q=True, loc=True)
			if not os.path.exists(currentFile):
				currentFile = "%s_%02d.mb" % (wantedName, 1)

			baseFile = os.path.split(currentFile)[-1]
			baseName, ext = baseFile.split('.')

			wantedBasename = wantedName #"%s_%s" % (self.assetList['scrollList'].getSelectedItem(), self.subTypeSearchList['scrollList'].getSelectedItem())
			if not wantedBasename in baseName:
				baseName = "%s_%02d" % (wantedBasename, 1)

			noVersionName = '_'.join(baseName.split('_')[:-1])
			version = int(baseName.split('_')[-1])

			versionFiles = []
			versions = []
			for item in existingFiles:
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

		saveLocation = os.path.join(self.assetDirectory, self.subType)
		if self.hasSub:
			saveLocation = self.subTypeDirectory
		if self.hasSub and self.hasVariant:
			saveLocation = self.variationDirectory

		saveFile = os.path.normpath(os.path.join(saveLocation, wantedName) ) 
		log.info( "Saving file: %s" % saveFile )
		mc.file( rename=saveFile )
		mc.file( save=True )
			
		self.LoadVersionList()
		
		versionList['scrollList'].selectByValue( wantedName )
		self.StoreCurrentSelection()
		
		self.refreshMetaData()

	def OpenDirectory(self, path):
		if os.path.exists(path):
			os.startfile(path)
		else:
			log.warning("Path not found - {0}".format(path))

	def LoadProject(self, path, *args):
		if not os.path.exists(path):
			mel.eval('warning "No Project Set"')
		
		self.project = Project.data(filepath=path)
		_bgColor = self.v_bgc
		try:
			_bgColor = self.project.d_colors['project']
		except Exception,err:
			log.warning("No project color stored | {0}".format(err))

		try:self.uiImage_ProjectRow(edit=True, bgc = _bgColor)
		except Exception,err:
			log.warning("Failed to set bgc: {0} | {1}".format(_bgColor,err))

		try:
			self._detailsToggleBtn(edit=True, bgc=[MATH.Clamp(1.8 * v,None,1.0) for v in _bgColor])
		except:
			self._detailsToggleBtn(edit=True, bgc=(1.0, .445, .08))
			
			
		d_userPaths = self.project.userPaths_get()
		
		if not d_userPaths.get('content'):
			log.error("No Content path found")
			return False
		if not d_userPaths.get('export'):
			log.error("No Export path found")
			return False
			

		if os.path.exists(d_userPaths['content']):
			self.optionVarProjectStore.setValue( path )

			self.LoadCategoryList(d_userPaths['content'])

			self.exportDirectory = d_userPaths['export']

			self.exportDirectoryTF.setValue( self.exportDirectory )
			# self.optionVarExportDirStore.setValue( self.exportDirectory )

			self.categoryList = self.project.assetTypes_get() if self.project.assetTypes_get() else self.project.d_structure.get('assetTypes', [])

			self.subTypes = [x['n'] for x in self.project.assetType_get(self.category).get('content', [{'n':'animation'}])]

			if d_userPaths.get('image') and os.path.exists(d_userPaths.get('image')):
				self.uiImage_Project.setImage(d_userPaths['image'])
			else:
				_imageFailPath = os.path.join(mImagesPath.asFriendly(),
				                              'cgm_project_{0}.png'.format(self.project.d_project.get('type','unity')))
				self.uiImage_Project.setImage(_imageFailPath)

			self.buildMenu_category()

			#self.buildMenu_subTypes()

			mc.workspace( d_userPaths['content'], openWorkspace=True )

			self.assetMetaData = {}

			self.LoadOptions()
		else:
			mel.eval('error "Project path does not exist"')
		return True

	def RenameAsset(self, *args):
		result = mc.promptDialog(
		    title='Rename Object',
		    message='Enter Name:',
		            button=['OK', 'Cancel'],
		                        defaultButton='OK',
		                        cancelButton='Cancel',
		                        dismissString='Cancel')

		if result == 'OK':
			newName = mc.promptDialog(query=True, text=True)
			log.info( 'Renaming %s to %s' % (self.selectedAsset, newName) )

			originalAssetName = self.selectedAsset

			# rename animations
			for animation in os.listdir(os.path.join(self.assetDirectory, self.subType)):
				for variation in os.listdir(os.path.join(self.assetDirectory, self.subType, animation)):
					for version in os.listdir(os.path.join(self.assetDirectory, self.subType, animation, variation)):
						if originalAssetName in version:
							originalPath = os.path.join(self.assetDirectory, self.subType, animation, variation, version)
							newPath = os.path.join(self.assetDirectory, self.subType, animation, variation, version.replace(originalAssetName, newName))
							os.rename(originalPath, newPath)

			# rename rigs
			for baseFile in os.listdir(self.assetDirectory):
				if os.path.isfile(os.path.join(self.assetDirectory, baseFile)):
					if originalAssetName in baseFile:
						originalPath = os.path.join(self.assetDirectory, baseFile)
						newPath = os.path.join(self.assetDirectory, baseFile.replace(originalAssetName, newName))
						os.rename(originalPath, newPath)

			# rename folder
			os.rename(self.assetDirectory, self.assetDirectory.replace(originalAssetName, newName))

			self.LoadCategoryList(self.directory)
			self.assetList['scrollList'].selectByValue( newName )

			self.LoadSubTypeList()

			if self.optionVarLastAnimStore.getValue():
				self.subTypeSearchList['scrollList'].selectByValue( self.optionVarLastAnimStore.getValue() )

			self.LoadVariationList()

			if self.optionVarLastVariationStore.getValue():
				self.variationList['scrollList'].selectByValue( self.optionVarLastVariationStore.getValue() )

			self.LoadVersionList()

			if self.optionVarLastVersionStore.getValue():
				self.versionList['scrollList'].selectByValue( self.optionVarLastVersionStore.getValue() )



	def OpenAssetDirectory(self, *args):
		if self.selectedAsset:
			self.OpenDirectory( os.path.join(self.categoryDirectory, self.selectedAsset) )
		else:
			self.OpenDirectory( self.categoryDirectory )

	def uiPath_mayaOpen(self,path=None):
		_res = mc.fileDialog2(fileMode=1, dir=path)
		if _res:
			log.warning("Opening: {0}".format(_res[0]))
			mc.file(_res[0], o=True, f=True, pr=True)

	def OpenSubTypeDirectory(self, *args):
		if self.assetDirectory:
			self.OpenDirectory( os.path.normpath(os.path.join(self.assetDirectory, self.subType) ))
		else:
			log.warning("Asset path doesn't exist")

	def OpenVariationDirectory(self, *args):
		self.OpenDirectory(self.subTypeDirectory)

	def OpenVersionDirectory(self, *args):
		self.OpenDirectory(self.variationDirectory)

	def ReferenceFile(self, *args):
		#if not self.assetList['scrollList'].getSelectedItem():
			#log.info( "No asset selected" )
			#return
		#if not self.subTypeSearchList['scrollList'].getSelectedItem():
			#log.info( "No animation selected" )
			#return
		#if not self.versionList['scrollList'].getSelectedItem():
			#log.info( "No version selected" )
			#return

		filePath = self.versionFile
		if os.path.exists(self.versionFile):
			mc.file(filePath, r=True, ignoreVersion=True, namespace=self.versionList['scrollList'].getSelectedItem() if self.hasSub else self.selectedAsset)
		else:
			log.info( "Version file doesn't exist" )

	def UpdateAssetTSLPopup(self, *args):
		self.assetTSLpum.clear()
		
		renameAssetMB = mUI.MelMenuItem(self.assetTSLpum, label="Rename Asset", command=self.RenameAsset )
		openInExplorerMB = mUI.MelMenuItem(self.assetTSLpum, label="Open In Explorer", command=self.OpenAssetDirectory )
		openMayaFileHereMB = mUI.MelMenuItem(self.assetTSLpum, label="Open In Maya", command=lambda *a:self.uiPath_mayaOpen( os.path.join(self.categoryDirectory, self.selectedAsset) ))
		
		for item in self.assetRigMenuItemList:
			mc.deleteUI(item, menuItem=True)
		for item in self.assetReferenceRigMenuItemList:
			mc.deleteUI(item, menuItem=True)

		self.assetRigMenuItemList = []
		self.assetReferenceRigMenuItemList = []

		openMB = mUI.MelMenuItem(self.assetTSLpum, label="Open", subMenu=True )
		referenceMB = mUI.MelMenuItem(self.assetTSLpum, label="Reference", subMenu=True )
		
		hasItems = False
		
		for subType in self.subTypes:
			if self.HasSub(self.category, subType):
				continue
			
			subDir = os.path.join(self.assetDirectory, subType)
			if not os.path.exists(subDir):
				continue
			
			assetList = ASSET.AssetDirectory(subDir, self.selectedAsset, subType)
			directoryList = assetList.GetFullPaths()
			
			if len(assetList.versions) == 0:
				continue
			
			openRigMB = mUI.MelMenuItem(openMB, label=subType, subMenu=True )
			referenceRigMB = mUI.MelMenuItem(referenceMB, label=subType, subMenu=True )
								
			#rigPath = #os.path.normpath(os.path.join(self.assetDirectory, "%s_rig.mb" % self.assetList['scrollList'].getSelectedItem() ))
			#if len(assetList.versions) > 0:
				#mc.menuItem( openRigMB, e=True, enable=True )
				#mc.menuItem( referenceRigMB, e=True, enable=True )
			#else:
				#mc.menuItem( openRigMB, e=True, enable=False )
				#mc.menuItem( referenceRigMB, e=True, enable=False )

			for i,rig in enumerate(assetList.versions):
				item = mUI.MelMenuItem( openRigMB, l=rig,
				                        c = cgmGEN.Callback(self.OpenRig,directoryList[i]))
				self.assetRigMenuItemList.append(item)

				item = mUI.MelMenuItem( referenceRigMB, l=rig,
				                        c = cgmGEN.Callback(self.ReferenceRig,directoryList[i], self.selectedAsset))
				self.assetReferenceRigMenuItemList.append(item)
				
				hasItems = True
		
		if not hasItems:
			openMB(e=True, en=False)
			referenceMB(e=True, en=False)
						

		self.refreshAssetListMB = mUI.MelMenuItem(self.assetTSLpum, label="Refresh", command=self.LoadCategoryList )

	def UpdateVersionTSLPopup(self, *args):	
		for item in self.sendToProjectMenuItemList:
			mc.deleteUI(item, menuItem=True)

		self.sendToProjectMenuItemList = []

		asset = self.versionFile

		mPathList = cgmMeta.pathList('cgmProjectPaths')

		project_names = []
		for i,p in enumerate(mPathList.mOptionVar.value):
			proj = Project.data(filepath=p)
			name = proj.d_project['name']
			project_names.append(name)

			if self.project.userPaths_get()['content'] == proj.userPaths_get()['content']:
				continue

			item = mUI.MelMenuItem( self.sendToProjectMenu, l=name if project_names.count(name) == 1 else '%s {%i}' % (name,project_names.count(name)-1),
			                        c = partial(self.SendVersionFileToProject,{'filename':asset,'project':p}))
			self.sendToProjectMenuItemList.append(item)

	def SendVersionFileToProject(self, infoDict, *args):
		newProject = Project.data(filepath=infoDict['project'])

		newFilename = os.path.normpath(infoDict['filename']).replace(os.path.normpath(self.project.userPaths_get()['content']), os.path.normpath(newProject.userPaths_get()['content']))

		if os.path.exists(newFilename):
			result = mc.confirmDialog(
			    title='Destination file exists!',
			    message='The destination file already exists. Would you like to overwrite it?',
			                button=['Yes', 'Cancel'],
			                            defaultButton='Yes',
			                            cancelButton='Cancel',
			                            dismissString='Cancel')

			if result != 'Yes':
				return False

		if not os.path.exists(os.path.dirname(newFilename)):
			os.makedirs(os.path.dirname(newFilename))

		copyfile(infoDict['filename'], newFilename)

		if os.path.exists(newFilename) and os.path.normpath(mc.file(q=True, loc=True)) == os.path.normpath(infoDict['filename']):
			result = 'Cancel'
			if not self.alwaysSendReferenceFiles.getValue():
				result = mc.confirmDialog(
				    title='Send Missing References?',
				    message='Copy missing references as well?',
				                    button=['Yes', 'Yes and Stop Asking', 'Cancel'],
				                                defaultButton='Yes',
				                                cancelButton='No',
				                                dismissString='No')

			if result == 'Yes and Stop Asking':
				self.alwaysSendReferenceFiles.setValue(1)

			if result == 'Yes' or self.alwaysSendReferenceFiles.getValue():
				for refFile in mc.file(query=True, reference=True):
					if not os.path.exists(refFile):
						continue
					
					newRefFilename = os.path.normpath(refFile).replace(os.path.normpath(self.project.userPaths_get()['content']), os.path.normpath(newProject.userPaths_get()['content']))
					
					if not os.path.exists(newRefFilename):
						if not os.path.exists(os.path.dirname(newRefFilename)):
							os.makedirs(os.path.dirname(newRefFilename))
						copyfile(refFile, newRefFilename)

			result = mc.confirmDialog(
			    title='Change Project?',
			    message='Change to the new project?',
			                button=['Yes', 'No'],
			                            defaultButton='Yes',
			                            cancelButton='No',
			                            dismissString='No')

			if result == 'Yes':
				if self.LoadProject(infoDict['project']):
					self.LoadOptions()

	def SendLatestRigToProject():
		pass

	def OpenRig(self, filename, *args):
		rigPath = filename #os.path.normpath(os.path.join(self.assetDirectory, "%s_rig.mb" % self.assetList['scrollList'].getSelectedItem() ))
		if os.path.exists(rigPath):
			mc.file(rigPath, o=True, f=True, ignoreVersion=True)

	def ReferenceRig(self, filename, assetName, *args):
		_str_func = 'Scene.ReferenceRig'
		rigPath = filename #os.path.normpath(os.path.join(self.assetDirectory, "%s_rig.mb" % self.assetList['scrollList'].getSelectedItem() ))

		log.info( '{0} | Referencing file : {1}'.format(_str_func, rigPath) )

		if os.path.exists(rigPath):
			mc.file(rigPath, r=True, ignoreVersion=True, gl=True, mergeNamespacesOnClash=False, namespace=assetName)
	
	def VerifyAssetDirs(self):
		_str_func = 'Scene.VerifyAssetDirs'
		assetName = self.selectedAsset
		assetPath = os.path.normpath(os.path.join(self.categoryDirectory, assetName))
		#subTypes = [x['n'] for x in self.project.assetType_get(category).get('content', [{'n':'animation'}])]
		
		if not os.path.exists(assetPath):
			os.mkdir(charPath)
			log.info('{0}>> Path not found. Appending: {1}'.format(_str_func, assetPath))		
		for subType in self.subTypes:
			subPath = os.path.normpath(os.path.join(assetPath, subType))
			if not os.path.exists(subPath):
				os.mkdir(subPath)
				log.info('{0}>> Path not found. Appending: {1}'.format(_str_func, subPath))

	def AddLastToExportQueue(self, *args):
		if self.variationList != None:
			self.batchExportItems.append( {"category":self.category,"asset":self.assetList['scrollList'].getSelectedItem(),"animation":self.subTypeSearchList['scrollList'].getSelectedItem(),"variation":self.variationList['scrollList'].getSelectedItem(),"version":self.versionList['scrollList'].getItems()[-1]} )

		self.RefreshQueueList()

	def AddToExportQueue(self, *args):
		if self.versionList['scrollList'].getSelectedItem() != None:
			self.batchExportItems.append( {"category":self.category,"asset":self.assetList['scrollList'].getSelectedItem(),"animation":self.subTypeSearchList['scrollList'].getSelectedItem(),"variation":self.variationList['scrollList'].getSelectedItem(),"version":self.versionList['scrollList'].getSelectedItem()} )
		elif self.variationList != None:
			self.batchExportItems.append( {"category":self.category,"asset":self.assetList['scrollList'].getSelectedItem(),"animation":self.subTypeSearchList['scrollList'].getSelectedItem(),"variation":self.variationList['scrollList'].getSelectedItem(),"version":self.versionList['scrollList'].getItems()[-1]} )

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
		if self.useMayaPy:
			#reload(BATCH)
			log.info('Maya Py!')

			bakeSetName = self.bakeSet.getValue()
			deleteSetName = self.deleteSet.getValue()
			exportSetName = self.exportSet.getValue()

			#if(mc.optionVar(exists='cgm_bake_set')):
				#bakeSetName = mc.optionVar(q='cgm_bake_set')    
			#if(mc.optionVar(exists='cgm_delete_set')):
				#deleteSetName = mc.optionVar(q='cgm_delete_set')
			#if(mc.optionVar(exists='cgm_export_set')):
				#exportSetName = mc.optionVar(q='cgm_export_set')                

			l_dat = []
			d_base = {'removeNamespace' : self.removeNamespace,
			          'bakeSetName':bakeSetName,
			          'exportSetName':exportSetName,
			          'deleteSetName':deleteSetName,
					  'zeroRoot' : self.zeroRoot}

			for animDict in self.batchExportItems:
				# self.assetList['scrollList'].selectByValue( animDict["asset"] )
				# self.LoadSubTypeList()
				# self.subTypeSearchList['scrollList'].selectByValue( animDict["animation"])
				# self.LoadVariationList()
				# self.variationList['scrollList'].selectByValue( animDict["variation"])
				# self.LoadVersionList()
				# self.versionList['scrollList'].selectByValue( animDict["version"])

				#mc.file(self.versionFile, o=True, f=True, ignoreVersion=True)

				# masterNode = None
				# for item in mc.ls("*:master", r=True):
				# 	if len(item.split(":")) == 2:
				# 		masterNode = item

				# 	if mc.checkBox(self.updateCB, q=True, v=True):
				# 		rig = ASSET.Asset(item)
				# 		if rig.UpdateToLatest():
				# 			self.SaveVersion()

				# if masterNode is None:
				# 	objs = []
				# else:
				# 	objs = [masterNode]
				categoryDirectory = os.path.normpath(os.path.join( self.directory, animDict["category"] ))
				assetDirectory = os.path.normpath(os.path.join( categoryDirectory, animDict["asset"] ))
				subTypeDirectory = os.path.normpath(os.path.join( assetDirectory, self.subType, animDict["animation"] ))
				variationDirectory = os.path.normpath(os.path.join( subTypeDirectory, animDict["variation"] ))
				versionFile = os.path.normpath(os.path.join( variationDirectory, animDict["version"] ))
				
				categoryExportPath = os.path.normpath(os.path.join( self.exportDirectory, animDict["category"]))
				exportAssetPath = os.path.normpath(os.path.join( categoryExportPath, animDict["asset"]))
				exportAnimPath = os.path.normpath(os.path.join(exportAssetPath, self.subType))                

				exportFileName = '%s_%s_%s.fbx' % (animDict["asset"], animDict["animation"], animDict["variation"])

				d = {
					'file':PATHS.Path(versionFile).asString(),
					#'objs':objs,
					'mode':-1, #Probably needs to be able to specify this
					'exportName':exportFileName,
					'animationName':animDict["animation"],
					'exportAssetPath' : PATHS.Path(exportAssetPath).split(),
					'categoryExportPath' : PATHS.Path(categoryExportPath).split(),
					'exportAnimPath' : PATHS.Path(exportAnimPath).split(),
					'updateAndIncrement' : int(mc.checkBox(self.updateCB, q=True, v=True))
				}                

				d.update(d_base)

				l_dat.append(d)



			pprint.pprint(l_dat)

			BATCH.create_Scene_batchFile(l_dat)
			return





		for animDict in self.batchExportItems:
			self.assetList['scrollList'].selectByValue( animDict["asset"] )
			self.LoadSubTypeList()
			self.subTypeSearchList['scrollList'].selectByValue( animDict["animation"])
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
					rig = ASSET.Asset(item)
					if rig.UpdateToLatest():
						self.SaveVersion()

			mc.select(masterNode)

			#mc.confirmDialog(message="exporting %s from %s" % (masterNode, mc.file(q=True, loc=True)))
			self.RunExportCommand(1)


	def RefreshQueueList(self, *args):
		self.queueTSL.clear()
		for item in self.batchExportItems:
			self.queueTSL.append( "%s - %s - %s - %s - %s" % (item["category"], item["asset"],item["animation"],item["variation"],item["version"]))

		if len(self.batchExportItems) > 0:
			mc.frameLayout(self.exportQueueFrame, e=True, collapse=False)
		else:
			mc.frameLayout(self.exportQueueFrame, e=True, collapse=True)

	# args[0]:
	# 0 is bake and prep, don't export
	# 1 is export as a regular asset
	#   - export the asset into the asset/animation directory
	# 2 is export as a cutscene 
	#   - cutscene means it adds the namespace to the 
	#   - asset and exports all of the assets into the
	#   - same directory
	# 3 is export as a rig
	#   - export into the base asset directory with
	#   - just the asset name
	def RunExportCommand(self, *args):
		categoryExportPath = os.path.normpath(os.path.join( self.exportDirectory, self.category))
		exportAssetPath = os.path.normpath(os.path.join( categoryExportPath, self.assetList['scrollList'].getSelectedItem()))
		exportAnimPath = os.path.normpath(os.path.join(exportAssetPath, self.subType))

		d_userPaths = self.project.userPaths_get()

		if self.useMayaPy:
			#reload(BATCH)
			log.info('Maya Py!')
			
			bakeSetName = self.bakeSet.getValue()
			deleteSetName = self.deleteSet.getValue()
			exportSetName = self.exportSet.getValue()             

			d = {
			'file':mc.file(q=True, sn=True),
			'objs':mc.ls(sl=1),
			'mode':args[0],
			'exportName':self.exportFileName,
			'exportAssetPath' : PATHS.Path(exportAssetPath).split(),
			'categoryExportPath' : PATHS.Path(categoryExportPath).split(),
			'subType' : self.subType,
			'exportAnimPath' : PATHS.Path(exportAnimPath).split(),
			'removeNamespace' : self.removeNamespace,
			'zeroRoot' : self.zeroRoot,
			'bakeSetName':bakeSetName,
			'exportSetName':exportSetName,
			'deleteSetName':deleteSetName,
            'animationName':self.selectedSubType,
            'workspace':d_userPaths['content']
			}

			#pprint.pprint(d)

			BATCH.create_Scene_batchFile([d])
			return


		ExportScene(mode = args[0],
		            exportObjs = None,
		            exportName = self.exportFileName,
		            exportAssetPath = exportAssetPath,
		            subType = self.subType,
		            categoryExportPath = categoryExportPath,
		            exportAnimPath = exportAnimPath,
		            removeNamespace = self.removeNamespace,
					zeroRoot = self.zeroRoot,
                    animationName = self.selectedSubType,
                    workspace=d_userPaths['content']
		            )        

		return True





def BatchExport(dataList = []):
	_str_func = 'BatchExport'
	#cgmGEN.log_start(_str_func)
	t1 = time.time()


	for fileDat in dataList:
		_d = {}

		_d['categoryExportPath'] = PATHS.NICE_SEPARATOR.join(fileDat.get('categoryExportPath'))
		_d['exportAnimPath'] = PATHS.NICE_SEPARATOR.join(fileDat.get('exportAnimPath'))
		_d['exportAssetPath'] = PATHS.NICE_SEPARATOR.join(fileDat.get('exportAssetPath'))
		_d['subType'] = fileDat.get('subType')
		_d['exportName'] = fileDat.get('exportName')
		mFile = PATHS.Path(fileDat.get('file'))
		_d['mode'] = int(fileDat.get('mode'))
		_d['exportObjs'] = fileDat.get('objs')
		_removeNamespace =  fileDat.get('removeNamespace', "False")
		_d['removeNamespace'] = False if _removeNamespace == "False" else True
		_zeroRoot =  fileDat.get('zeroRoot', "False")
		_d['zeroRoot'] = False if _zeroRoot == "False" else True
		_d['deleteSetName'] = fileDat.get('deleteSetName')
		_d['exportSetName'] = fileDat.get('exportSetName')
		_d['bakeSetName'] = fileDat.get('bakeSetName')
		_d['animationName'] = fileDat.get('animationName')
		_d['workspace'] = fileDat.get('workspace')
		_d['updateAndIncrement'] = fileDat.get('updateAndIncrement')

		log.info(mFile)
		pprint.pprint(_d)


		_path = mFile.asString()
		if not mFile.exists():
			log.error("Invalid file: {0}".format(_path))
			continue

		mc.file(_path, open = 1, f = 1, iv = 1)

		# if not _d['exportObjs']:
		# 	log.info(cgmGEN.logString_sub(_str_func,"Trying to find masters..."))

		# 	l_masters = []
		# 	for item in mc.ls("*:master", r=True):
		# 		if len(item.split(":")) == 2:
		# 			masterNode = item
		# 			l_masters.append(item)

		# 		#if mc.checkBox(self.updateCB, q=True, v=True):
		# 			#rig = ASSET.Asset(item)
		# 			#if rig.UpdateToLatest():
		# 				#self.SaveVersion()

		# 	if l_masters:
		# 		log.info(cgmGEN.logString_msg(_str_func,"Found..."))
		# 		pprint.pprint(l_masters)

		# 		_d['exportObjs'] = l_masters


		#if _objs:
		#    mc.select(_objs)
		ExportScene(**_d)        

	t2 = time.time()
	log.info("|{0}| >> Total Time >> = {1} seconds".format(_str_func, "%0.4f"%( t2-t1 )))         

	return

	mFile = PATHS.Path(f)

	if not mFile.exists():
		raise ValueError,"Invalid file: {0}".format(f)

	_path = mFile.asFriendly()

	log.info("Good Path: {0}".format(_path))
	"""
    if 'template' in _path:
        _newPath = _path.replace('template','build')
    else:"""
	_name = mFile.name()
	_d = mFile.up().asFriendly()
	log.debug(cgmGEN.logString_msg(_str_func,_name))
	_newPath = os.path.join(_d,_name+'_BUILD.{0}'.format(mFile.getExtension()))        

	log.info("New Path: {0}".format(_newPath))

	#cgmGEN.logString_msg(_str_func,'File Open...')
	mc.file(_path, open = 1, f = 1)

	#cgmGEN.logString_msg(_str_func,'Process...')
	t1 = time.time()

	try:
		if not blocks:
			#cgmGEN.logString_sub(_str_func,'No blocks arg')

			ml_masters = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',
			                                 nTypes=['transform','network'],
			                                 mAttrs='blockType=master')

			for mMaster in ml_masters:
				#cgmGEN.logString_sub(_str_func,mMaster)

				RIGBLOCKS.contextual_rigBlock_method_call(mMaster, 'below', 'atUtils','changeState','rig',forceNew=False)

				ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(mMaster,'below',True,False)
				l_fails = []

				for mSubBlock in ml_context:
					_state =  mSubBlock.getState(False)
					if _state != 4:
						l_fails.append(mSubBlock)

				if l_fails:
					log.info('The following failed...')
					pprint.pprint(l_fails)
					raise ValueError,"Modules failed to rig: {0}".format(l_fails)

				log.info("Begin Rig Prep cleanup...")
				'''

                Begin Rig Prep process

                '''
				mPuppet = mMaster.moduleTarget#...when mBlock is your masterBlock

				if postProcesses:
					log.info('mirror_verify...')
					mPuppet.atUtils('mirror_verify')
					log.info('collect worldSpace...')                        
					mPuppet.atUtils('collect_worldSpaceObjects')
					log.info('qss...')                        
					mPuppet.atUtils('qss_verify',puppetSet=1,bakeSet=1,deleteSet=1,exportSet=1)
					log.info('proxyMesh...')
					mPuppet.atUtils('proxyMesh_verify')
					log.info('ihi...')                        
					mPuppet.atUtils('rigNodes_setAttr','ihi',0)
					log.info('rig connect...')                        
					mPuppet.atUtils('rig_connectAll')
	except Exception,err:
		log.error(err)


	t2 = time.time()
	log.info("|{0}| >> Total Time >> = {1} seconds".format(_str_func, "%0.4f"%( t2-t1 ))) 


	#cgmGEN.logString_msg(_str_func,'File Save...')
	newFile = mc.file(rename = _newPath)
	mc.file(save = 1)            





# args[0]:
# -1 is unknown mode
# 0 is bake and prep, don't export
# 1 is export as a regular asset
#   - export the asset into the asset/animation directory
# 2 is export as a cutscene 
#   - cutscene means it adds the namespace to the 
#   - asset and exports all of the assets into the
#   - same directory
# 3 is export as a rig
#   - export into the base asset directory with
#   - just the asset name

def ExportScene(mode = -1,
                exportObjs = None,
                exportName = None,
                categoryExportPath = None,
                subType = None,
                exportAssetPath = None,
                exportAnimPath = None,
                removeNamespace = False,
				zeroRoot = False,
                bakeSetName = None,
                exportSetName = None,
                deleteSetName = None,
                animationName = None,
                workspace = None,
                updateAndIncrement = False
                ):

	if workspace:
		mc.workspace( workspace, openWorkspace=True )

	#exec(self.exportCommand)
	import cgm.core.tools.bakeAndPrep as bakeAndPrep
	#reload(bakeAndPrep)
	import cgm.core.mrs.Shots as SHOTS
	_str_func = 'ExportScene'

	if not exportObjs:
		exportObjs = mc.ls(sl=True)

	cameras = []
	exportCams = []

	for obj in exportObjs:
		log.info("Checking: {0}".format(obj))
		if mc.listRelatives(obj, shapes=True, type='camera'):
			cameras.append(obj)
			exportCams.append( bakeAndPrep.MakeExportCam(obj) )
			exportObjs.remove(obj)

	exportObjs += exportCams

	addNamespaceSuffix = False
	exportFBXFile = False
	exportAsRig = False
	exportAsCutscene = False


	log.info("mode check...")
	if mode == -1:
		log.info("unknown mode, attempting to auto detect")
		if not exportObjs:
			exportObjs = []
			wantedSets = []
			for set in mc.ls('*%s' % exportSetName, r=True):
				if len(set.split(':')) == 2:
					ns = set.split(':')[0]
					for p in mc.ls(mc.sets(set,q=True)[0], l=True)[0].split('|'):
						if mc.objExists(p) and ns in p:
							exportObjs.append(p)
							break
				if len(set.split(':')) == 1:
					objName = set.replace('_%s' % exportSetName, '')
					if mc.objExists(objName):
						exportObjs.append(objName)

		if len(exportObjs) > 1:
			log.info("More than one export obj found, setting cutscene mode: 2")
			mode = 2
		elif len(exportObjs) == 1:
			log.info("One export obj found, setting regular asset mode: 1")
			mode = 1
		else:
			log.info("Auto detection failed. Exiting.")
			return

	if mode > 0:
		exportFBXFile = True

	if len(exportObjs) > 1 and mode != 2:
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

	if mode== 2:
		addNamespaceSuffix = True
		exportAsCutscene = True
	if mode == 3:
		exportAsRig = True

	# make the relevant directories if they dont exist
	#categoryExportPath = os.path.normpath(os.path.join( self.exportDirectory, self.category))

	log.info("category path...")
	if not os.path.exists(categoryExportPath):
		os.mkdir(categoryExportPath)
	#exportAssetPath = os.path.normpath(os.path.join( categoryExportPath, self.assetList['scrollList'].getSelectedItem()))

	log.info("asset path...")

	if not os.path.exists(exportAssetPath):
		os.mkdir(exportAssetPath)
	exportAnimPath = os.path.normpath(os.path.join(exportAssetPath, subType))

	if not os.path.exists(exportAnimPath):
		log.info("making export anim path...")

		os.mkdir(exportAnimPath)
		# create empty file so folders are checked into source control
		f = open(os.path.join(exportAnimPath, "filler.txt"),"w")
		f.write("filler file")
		f.close()

	if exportAsCutscene:
		log.info("export as cutscene...")

		exportAnimPath = os.path.normpath(os.path.join(exportAnimPath, animationName))
		if not os.path.exists(exportAnimPath):
			os.mkdir(exportAnimPath)

	exportFiles = []

	log.info("bake start...")

	# rename for safety
	loc = mc.file(q=True, loc=True)
	base, ext = os.path.splitext(loc)
	bakedLoc = "%s_baked%s" % (base, ext)

	mc.file(rn=bakedLoc)

	if not bakeSetName:
		bakeSetName = cgmMeta.cgmOptionVar('cgm_bake_set', varType="string",defaultValue = 'bake_tdSet').getValue()
	if not deleteSetName:
		deleteSetName = cgmMeta.cgmOptionVar('cgm_delete_set', varType="string",defaultValue = 'delete_tdSet').getValue()
	if not exportSetName:
		exportSetName = cgmMeta.cgmOptionVar('cgm_export_set', varType="string",defaultValue = 'export_tdSet').getValue()  

	animList = SHOTS.AnimList()
	#find our minMax
	l_min = []
	l_max = []

	for shot in animList.shotList:
		l_min.append(min(shot[1]))
		l_max.append(max(shot[1]))

	if l_min:
		_start = min(l_min)
	else:
		_start = None

	if l_max:
		_end = max(l_max)
	else:
		_end = None

	log.info( cgmGEN.logString_sub(_str_func,'Bake | start: {0} | end: {1}'.format(_start,_end)) )

	bakeAndPrep.Bake(exportObjs,bakeSetName,startFrame= _start, endFrame= _end)

	mc.loadPlugin("fbxmaya")

	for obj in exportObjs:			
		log.info( cgmGEN.logString_sub(_str_func,'On: {0}'.format(obj)) )
		
		cgmObj = cgmMeta.asMeta(obj)
		mc.select(obj)

		assetName = obj.split(':')[0].split('|')[-1]

		exportFile = os.path.normpath(os.path.join(exportAnimPath, exportName) )

		if( addNamespaceSuffix ):
			exportFile = exportFile.replace(".fbx", "_%s.fbx" % assetName )
		if( exportAsRig ):
			exportFile = os.path.normpath(os.path.join(exportAssetPath, '{}_rig.fbx'.format( assetName )))

		bakeAndPrep.Prep(removeNamespace=removeNamespace, deleteSetName=deleteSetName,exportSetName=exportSetName, zeroRoot=zeroRoot)

		exportTransforms = mc.ls(sl=True)

		mc.select(exportTransforms, hi=True)		

		log.info("Heirarchy...")

		for i,o in enumerate(mc.ls(sl=1)):
			log.info("{0} | {1}".format(i,o))

		if(exportFBXFile):
			mel.eval('FBXExportSplitAnimationIntoTakes -c')
			for shot in animList.shotList:
				log.info( cgmGEN.logString_msg(_str_func, "shot..."))
				log.info(shot)
				mel.eval('FBXExportSplitAnimationIntoTakes -v \"{}\" {} {}'.format(shot[0], shot[1][0], shot[1][1]))

			#mc.file(exportFile, force=True, options="v=0;", exportSelected=True, pr=True, type="FBX export")
			log.info('Export Command: FBXExport -f \"{}\" -s'.format(exportFile))
			mel.eval('FBXExport -f \"{}\" -s'.format(exportFile.replace('\\', '/')))
			#mc.FBXExport(f= exportFile)

			if len(exportObjs) > 1 and removeNamespace:
				# Deleting the exported transforms in case another file has duplicate export names
				mc.delete(cgmObj.mNode)
				try:
					mc.delete(exportTransforms)
				except:
					pass

	return True



def PurgeData():

	optionVarProjectStore       = cgmMeta.cgmOptionVar("cgmVar_projectCurrent", varType = "string")
	optionVarProjectStore.purge()

	optionVarLastAssetStore     = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_asset", varType = "string")
	optionVarLastAssetStore.purge()

	optionVarLastAnimStore      = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_animation", varType = "string")
	optionVarLastAnimStore.purge()

	optionVarLastVariationStore = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_variation", varType = "string")
	optionVarLastVariationStore.purge()

	optionVarLastVersionStore   = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_version", varType = "string")
	optionVarLastVersionStore.purge()

	showAllFilesStore           = cgmMeta.cgmOptionVar("cgmVar_sceneUI_show_all_files", defaultValue = 0)
	showAllFilesStore.purge()

	removeNamespaceStore        = cgmMeta.cgmOptionVar("cgmVar_sceneUI_remove_namespace", defaultValue = 0)
	removeNamespaceStore.purge()

	categoryStore               = cgmMeta.cgmOptionVar("cgmVar_sceneUI_category", defaultValue = 0)
	categoryStore.purge()

	alwaysSendReferenceFiles    = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_version", defaultValue = 0)
	alwaysSendReferenceFiles.purge()