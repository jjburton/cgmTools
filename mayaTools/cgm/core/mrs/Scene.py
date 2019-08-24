import maya.cmds as mc
import maya.mel as mel
from functools import partial
import os
import fnmatch
import cgm.lib.pyui as pyui
import subprocess
import re

class SceneUI(object):
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
	def __init__(self):
		self.window                      = None
		
		self.categoryList                = ["Character", "Environment", "Vehicles", "Props", "Interactables", "Level"]
		self.categoryIndex               = 0

		self.optionVarDirStore           = "cgm_fileUI_importer_directory_list"
		self.optionVarLastDirStore       = "cgm_fileUI_importer_last_directory"
		self.optionVarLastAssetStore     = "cgm_fileUI_importer_last_asset"
		self.optionVarLastAnimStore      = "cgm_fileUI_importer_last_animation"
		self.optionVarLastVariationStore = "cgm_fileUI_importer_last_variation"
		self.optionVarLastVersionStore   = "cgm_fileUI_importer_last_version"
		self.optionVarExportDirStore     = "cgm_fileUI_importer_export_directory"
		self.showBakedStore              = "cgm_fileUI_show_baked"
		self.categoryStore               = "cgm_fileUI_category"
		
		## sizes
		self.width                       = 400
		self.height                      = 700
		self.__itemHeight                = 35
		self.__cw1                       = 125
		
		# UI elements
		self.assetList                   = pyui.SearchableList()
		self.animationList               = pyui.SearchableList()
		self.variationList               = pyui.SearchableList()
		self.versionList                 = pyui.SearchableList()
		self.queueTSL                    = pyui.UIList()
		self.updateCB                    = None
		self.bottomColumn                = None
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
		self.CreateWindow()			

		if self.previousLoadedDirectory:
			self.LoadCategoryList(self.previousLoadedDirectory)

		self.LoadPreviousSelection()

	@property
	def directory(self):
		return self.directoryTFG.text

	@directory.setter
	def directory(self, directory):
		self.directoryTFG.text = directory

	@property
	def categoryDirectory(self):
		return os.path.normpath(os.path.join( self.directory, self.category ))
	
	@property
	def assetDirectory(self):
		return os.path.normpath(os.path.join( self.categoryDirectory, self.assetList.selectedItem ))

	@property
	def animationDirectory(self):
		return os.path.normpath(os.path.join( self.assetDirectory, 'animation', self.animationList.selectedItem ))

	@property
	def variationDirectory(self):
		return os.path.normpath(os.path.join( self.animationDirectory, self.variationList.selectedItem ))

	@property
	def versionFile(self):
		return os.path.normpath(os.path.join( self.variationDirectory, self.versionList.selectedItem ))

	@property
	def exportFileName(self):
		return '%s_%s_%s.fbx' % (self.assetList.selectedItem, self.animationList.selectedItem, self.variationList.selectedItem)

	@property
	def category(self):
		return self.categoryList[self.categoryIndex]

	def LoadOptions(self, *args):
		self.showBaked     = bool(mc.optionVar(q=self.showBakedStore)) if mc.optionVar(exists=self.showBakedStore) else False
		self.categoryIndex = int(mc.optionVar(q=self.categoryStore)) if mc.optionVar(exists=self.categoryStore) else 0
		
		self.exportDirectory = mc.optionVar(q=self.optionVarExportDirStore) if mc.optionVar(exists=self.optionVarExportDirStore) else ""
		#self.exportCommand   = mc.optionVar(q=self.exportCommandStore) if mc.optionVar(exists=self.exportCommandStore) else ""

	def SaveOptions(self, *args):
		self.showBaked     = mc.menuItem(self.showBakedOption, q=True, checkBox=True)
		
		mc.optionVar( intValue =[self.showBakedStore, self.showBaked] )
		mc.optionVar( stringValue = [self.optionVarExportDirStore, self.exportDirectory] )
		mc.optionVar( intValue = [self.categoryStore, self.categoryIndex])
		#mc.optionVar( stringValue = [self.exportCommandStore, self.exportCommand] )
		
		self.LoadVersionList()

	def TagAsset(self, *args):
		pass

	def UpdateToLatestRig(self, *args):
		pass

	def SetExportSets(self, *args):
		mc.window( width=150 )
		mc.columnLayout( adjustableColumn=True )
		mc.button( label='Set Bake Set', command=self.SetBakeSet )
		mc.button( label='Set Delete Set', command=self.SetDeleteSet )
		mc.button( label='Set Export Set', command=self.SetExportSet )
		mc.showWindow()

	def SetDeleteSet(self, *args):
		sel = mc.ls(sl=True)
		deleteSet = sel[0].split(':')[-1]
		print "Setting delete set to: %s" % deleteSet 
		mc.optionVar(sv=('cgm_delete_set', deleteSet))

	def SetBakeSet(self, *args):
		sel = mc.ls(sl=True)
		bakeSet = sel[0].split(':')[-1]
		print "Setting bake set to: %s" % bakeSet 
		mc.optionVar(sv=('cgm_bake_set', bakeSet))

	def SetExportSet(self, *args):
		sel = mc.ls(sl=True)
		exportSet = sel[0].split(':')[-1]
		print "Setting geo set to: %s" % exportSet 
		mc.optionVar(sv=('cgm_export_set', exportSet))

	def CreateWindow(self, *args):
		if mc.window("cgmSceneUI", q=True, exists=True):
			mc.deleteUI("cgmSceneUI")

		self.window = mc.window( "cgmSceneUI", title="cgmScene", iconName='cgmScene' )
		
		self.menuBarLayout = mc.menuBarLayout()
		self.ConstructMenuBar()

		mainForm = mc.formLayout(numberOfDivisions=100)

		directoryColumn = mc.columnLayout(adjustableColumn=True)
		self.directoryTFG = pyui.TextFieldButtonGrp()
		self.directoryTFG.label='Directory'
		self.directoryTFG.cw3=(self.__cw1*.5, self.width*.6, self.__cw1*.5)
		self.directoryTFG.buttonLabel="Set"
		self.directoryTFG.buttonCommand=self.SetAnimationDirectory #, h=self.__itemHeight
		self.directoryTFG.changeCommand=self.ChangeAnimationDirectory #, h=self.__itemHeight

		self.exportDirectoryTFG = pyui.TextFieldButtonGrp()
		self.exportDirectoryTFG.label='Export Dir'
		self.exportDirectoryTFG.cw3=(self.__cw1*.5, self.width*.6, self.__cw1*.5)
		self.exportDirectoryTFG.buttonLabel="Set"
		self.exportDirectoryTFG.buttonCommand=self.SetExportDirectory #, h=self.__itemHeight
		self.exportDirectoryTFG.changeCommand=self.ChangeExportDirectory #, h=self.__itemHeight
		self.exportDirectoryTFG.text = self.exportDirectory

		mc.setParent('..')

		# Upper Labels
		c1_upperColumn = mc.columnLayout(adjustableColumn=True)
		self.categoryText = mc.button(self.category, h=self.__itemHeight)
		mc.popupMenu( button=1 )
		for i,category in enumerate(self.categoryList):
			self.categoryMenuItemList.append( mc.menuItem(label=category, c=partial(self.SetCategory,i)) )
			if i == self.categoryIndex:
				mc.menuItem(self.categoryMenuItemList[i], e=True, enable=False)
		self.assetList.CreateSearchField()
		mc.setParent('..')
		c2_upperColumn = mc.columnLayout(adjustableColumn=True)
		mc.text("Animation", h=self.__itemHeight)
		self.animationList.CreateSearchField()
		mc.setParent('..')
		c3_upperColumn = mc.columnLayout(adjustableColumn=True)
		mc.text("Variation", h=self.__itemHeight)
		self.variationList.CreateSearchField()
		mc.setParent('..')	
		c4_upperColumn = mc.columnLayout(adjustableColumn=True)
		mc.text("Version", h=self.__itemHeight)
		self.versionList.CreateSearchField()
		mc.setParent('..')		

		# Text Scroll Lists
		self.assetList.CreateTSL()
		mc.popupMenu(pmc=self.UpdateCharTSLPopup)
		mc.menuItem(label="Open In Explorer", command=self.OpenAssetDirectory )
		self.openRigMB = mc.menuItem(label="Open Rig", command=self.OpenRig )
		self.importRigMB = mc.menuItem(label="Import Rig", command=self.ImportRig )

		self.animationList.CreateTSL()
		mc.popupMenu()
		mc.menuItem(label="Open In Explorer", command=self.OpenAnimationDirectory )

		self.variationList.CreateTSL()
		mc.popupMenu()
		mc.menuItem(label="Open In Explorer", command=self.OpenVariationDirectory )

		self.versionList.CreateTSL()
		mc.popupMenu()
		mc.menuItem(label="Open In Explorer", command=self.OpenVersionDirectory )
		mc.menuItem(label="Reference File", command=self.ReferenceFile )

		mc.textScrollList( self.assetList.textScrollList, e=True, sc=self.LoadAnimationList )
		mc.textScrollList( self.animationList.textScrollList, e=True, sc=self.LoadVariationList )
		mc.textScrollList( self.variationList.textScrollList, e=True, sc=self.LoadVersionList )
		mc.textScrollList( self.versionList.textScrollList, e=True, sc=self.StoreCurrentSelection )


		self.assetButton = mc.button(label="New Asset", command=self.CreateAsset, h=self.__itemHeight)
		self.animationButton = mc.button(label="New Animation", command=self.CreateAnimation, h=self.__itemHeight)
		self.variationButton = mc.button(label="New Variation", command=self.CreateVariation, h=self.__itemHeight)
		self.versionButton   = mc.button(label="Save New Version", command=self.SaveVersion, h=self.__itemHeight)
		
		# Bottom Column
		self.bottomColumn    = mc.columnLayout(adjustableColumn = True)
		
		# Import button
		mc.rowColumnLayout(numberOfColumns=7, columnWidth=[(1, 200), (2, 200),(3, 200), (4, 200),(5, 200)], adjustableColumn = 1, columnSpacing=[(2,5),(3,5),(4,5),(5,5)])
		self.exportButton    = mc.button(label="Export", c=partial(self.RunExportCommand,1), h=self.__itemHeight)
		mc.popupMenu()
		mc.menuItem( l="Bake Without Export", c=partial(self.RunExportCommand,0))
		mc.menuItem( l="Export Rig", c=partial(self.RunExportCommand,3))
		mc.menuItem( l="Force Export As Cutscene", c=partial(self.RunExportCommand,2))
		
		mc.button(label="Bake Without Export", c=partial(self.RunExportCommand,0), h=self.__itemHeight)
		mc.button(label="Export Rig", c=partial(self.RunExportCommand,3), h=self.__itemHeight)
		mc.button(label="Export Cutscene", c=partial(self.RunExportCommand,2), h=self.__itemHeight)

		mc.button(label="Add To Export Queue", w=200, c=partial(self.AddToExportQueue), h=self.__itemHeight)
		mc.setParent('..')
		mc.button(label="Load Animation", c=self.LoadAnimation, h=self.__itemHeight)
		
		self.exportQueueFrame = mc.frameLayout(label="Export Queue", collapsable=True, collapse=True)
		mc.rowColumnLayout(numberOfColumns=2, adjustableColumn=1, columnWidth=[(1,100),(1,200)])
		self.queueTSL.CreateTSL()
		mc.textScrollList(self.queueTSL.textScrollList, e=True, allowMultiSelection=True)
		mc.columnLayout(width=200,adjustableColumn=True)
		mc.button(label="Add", command=partial(self.AddToExportQueue), height=self.__itemHeight)
		mc.button(label="Remove", command=partial(self.RemoveFromQueue, 0), height=self.__itemHeight)
		mc.button(label="Remove All", command=partial(self.RemoveFromQueue, 1), height=self.__itemHeight)
		mc.button(label="Batch Export", command=partial(self.BatchExport), height=self.__itemHeight)
		mc.frameLayout(label="Options", collapsable=True)
		mc.rowColumnLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[(1,10), (2,80)])
		mc.text(label="")
		self.updateCB = mc.checkBox(label="Update and Save Increment", v=False)
		mc.setParent('..')
		mc.setParent('..')
		mc.setParent("..")
		mc.setParent("..")

		mc.setParent("..")

		mc.formLayout( mainForm, edit=True, 

			attachForm =
			[(directoryColumn,'top', 0), 
			(directoryColumn,'left', 0), 
			(directoryColumn,'right', 0), 
			(c1_upperColumn, 'left', 0), 
			(c4_upperColumn, 'right', 0), 
			(self.assetList.textScrollList, 'left', 0), 
			(self.bottomColumn, 'left', 0), 
			(self.bottomColumn, 'bottom', 0), 
			(self.bottomColumn, 'right', 0), 
			(self.versionList.textScrollList, 'right', 0),
			(self.assetButton, 'left', 0), 
			(self.versionButton, 'right', 0) ], 

			attachControl =
			[(c1_upperColumn, 'top', 0, directoryColumn), 
			(c2_upperColumn, 'top', 0, directoryColumn), 
			(c2_upperColumn, 'right', 0, c3_upperColumn), 
			(c3_upperColumn, 'top', 0, directoryColumn), 
			(c3_upperColumn, 'right', 0, c4_upperColumn), 
			(c4_upperColumn, 'top', 0, directoryColumn), 
			(self.assetList.textScrollList, 'bottom', 0, self.assetButton), 
			(self.assetList.textScrollList, 'top', 0, c1_upperColumn),
			(self.animationList.textScrollList, 'bottom', 0, self.animationButton), 
			(self.animationList.textScrollList, 'left', 0, c1_upperColumn), 
			(self.animationList.textScrollList, 'right', 4, self.variationList.textScrollList),
			(self.animationList.textScrollList, 'top', 0, c3_upperColumn),
			(self.variationList.textScrollList, 'left', 5, c2_upperColumn),
			(self.variationList.textScrollList, 'right', 4, self.versionList.textScrollList),
			(self.variationList.textScrollList, 'bottom', 0, self.versionButton), 
			(self.variationList.textScrollList, 'top', 0, c2_upperColumn),
			(self.versionList.textScrollList, 'left', 5, c3_upperColumn),
			(self.versionList.textScrollList, 'bottom', 0, self.versionButton), 
			(self.versionList.textScrollList, 'top', 0, c3_upperColumn),
			(self.assetButton, 'bottom', 3, self.bottomColumn),
			(self.assetButton, 'right', 5, c2_upperColumn),
			(self.animationButton, 'bottom', 3, self.bottomColumn),
			(self.animationButton, 'left', 5, c1_upperColumn),
			(self.animationButton, 'right', 5, c3_upperColumn),
			(self.variationButton, 'bottom', 3, self.bottomColumn),
			(self.variationButton, 'left', 5, c2_upperColumn),
			(self.variationButton, 'right', 5, c4_upperColumn),
			(self.versionButton, 'bottom', 3, self.bottomColumn),
			(self.versionButton, 'left', 5, c3_upperColumn)], 

			attachPosition =
			[(self.assetList.textScrollList, 'right', 2, 25),
			(self.animationList.textScrollList, 'left', 2, 25),
			(c4_upperColumn, 'left', 2, 75),
			(c1_upperColumn, 'right', 2, 25), 
			(c2_upperColumn, 'left', 2, 25), 
			(c2_upperColumn, 'right', 2, 50),
			(c3_upperColumn, 'left', 2, 50), 
			(c3_upperColumn, 'right', 2, 75)], 

			attachNone=(self.bottomColumn, 'top') )

		mc.showWindow( self.window )

	def ConstructMenuBar(self, *args):
		if self.fileMenu:
			mc.deleteUI(self.fileMenu, control=True)
			self.fileMenu = None
			self.fileListMenuItems = []
		if self.optionsMenu:
			mc.deleteUI(self.optionsMenu, control=True)
			self.optionsMenu = None
		if self.toolsMenu:
			mc.deleteUI(self.toolsMenu, control=True)
			self.toolsMenu = None

		mc.setParent(self.menuBarLayout)

		self.fileMenu = mc.menu( label='File' )
		self.fileListMenuItems.append(mc.menuItem( label='Open', c=self.OpenDirectory ))
		self.fileListMenuItems.append(mc.menuItem( d=True ))
		
		for d in self.GetPreviousDirectories():
			self.fileListMenuItems.append(mc.menuItem(label=d, c=partial(self.LoadCategoryList,d)))
		
		self.fileListMenuItems.append(mc.menuItem( label='Clear List', c=self.ClearPreviousDirectories ))

		self.optionsMenu = mc.menu( label='Options' )
		self.showBakedOption    = mc.menuItem( label='Show baked versions', checkBox=self.showBaked, c=self.SaveOptions )
		#self.setExportCommandMI = mc.menuItem( label='Custom Export Command', c=self.SetExportCommand )

		self.toolsMenu = mc.menu( label='Tools' )
		self.tagSelected = mc.menuItem( label='Tag As Current Asset', c=self.TagAsset )
		self.tagSelected = mc.menuItem( label='Set Export Sets', c=self.SetExportSets )

	def SetCategory(self, index, *args):
		self.categoryIndex = index
		mc.button( self.categoryText, e=True, label=self.category )
		for i,category in enumerate(self.categoryMenuItemList):
			if i == self.categoryIndex:
				mc.menuItem(self.categoryMenuItemList[i], e=True, enable=False)
			else:
				mc.menuItem(self.categoryMenuItemList[i], e=True, enable=True)

		self.LoadCategoryList(self.directory)
		self.SaveOptions()

	def LoadCategoryList(self, directory="", *args):
		p = self.GetPreviousDirectories()
		if len(p) >= 10:
			for i in range(len(p) - 9):
				mc.optionVar(rfa=[self.optionVarDirStore, 0])

		if directory not in p:
			mc.optionVar(stringValueAppend=[self.optionVarDirStore, directory])

		self.directory = directory

		self.ConstructMenuBar()

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

		self.animationList.ClearList()
		self.variationList.ClearList()
		self.versionList.ClearList()

		self.StoreCurrentSelection()

	def LoadAnimationList(self, *args):
		animList = []
		
		if self.categoryDirectory and self.assetList.selectedItem:
			charDir = os.path.normpath(os.path.join( self.categoryDirectory, self.assetList.selectedItem, 'animation' ))

			if os.path.exists(charDir):
				for d in os.listdir(charDir):
					#for ext in fileExtensions:
					#	if os.path.splitext(f)[-1].lower() == ".%s" % ext :
					if d[0] == '_' or d[0] == '.':
						continue

					animDir = os.path.normpath(os.path.join(charDir, d))
					if os.path.isdir(animDir):
						animList.append(d)

		self.animationList.SetItems(animList)

		self.variationList.ClearList()
		self.versionList.ClearList()

		self.StoreCurrentSelection()

	def LoadVariationList(self, *args):
		variationList = []

		self.variationList.ClearList()

		if self.categoryDirectory and self.assetList.selectedItem and self.animationList.selectedItem:
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

		self.variationList.SetItems(variationList)

		self.versionList.ClearList()

		if self.variationList.displayItems != None:
			self.variationList.selectedIndex = 1

		self.LoadVersionList()

		self.StoreCurrentSelection()

	def LoadVersionList(self, *args):
		if not self.assetList.selectedItem or not self.animationList.selectedItem:
			return

		versionList = []
		anims = []

		# populate animation info list
		fileExtensions = ['mb', 'ma']

		if self.categoryDirectory and self.assetList.selectedItem and self.animationList.selectedItem and self.variationList.selectedItem:
			animDir = self.variationDirectory
			
			if os.path.exists(animDir):
				for d in os.listdir(animDir):
					if d[0] == '_' or d[0] == '.':
						continue

					for ext in fileExtensions:
						if os.path.splitext(d)[-1].lower() == ".%s" % ext :
							if not "_baked" in d or self.showBaked:
								anims.append(d)

		self.versionList.SetItems(anims)

		self.StoreCurrentSelection()

	def LoadAnimation(self, *args):
		if not self.assetList.selectedItem:
			print "No asset selected"
			return
		if not self.animationList.selectedItem:
			print "No animation selected"
			return
		if not self.versionList.selectedItem:
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

		self.exportDirectoryTFG.text = self.exportDirectory

		self.SaveOptions()

	def ChangeExportDirectory(self, *args):
		newPath = self.exportDirectory
		if os.path.exists(newPath):
			#self.LoadCategoryList(newPath)
			self.exportDirectory = newPath
			self.SaveOptions()

	def GetPreviousDirectories(self, *args):
		if mc.optionVar(exists=self.optionVarDirStore):
			return mc.optionVar(q=self.optionVarDirStore)
		else:
			return []

	def UpdateAssetList(self, charList):
		self.assetList.SetItems(charList)

	def GetPreviousDirectory(self, *args):
		if mc.optionVar(exists=self.optionVarDirStore):
			return mc.optionVar(q=self.optionVarLastDirStore)
		else:
			return None

	def StoreCurrentDirectory(self, *args):
		mc.optionVar(stringValue=[self.optionVarLastDirStore, self.directory])

	def StoreCurrentSelection(self, *args):
		if self.assetList.selectedItem:
			mc.optionVar(stringValue=[self.optionVarLastAssetStore, self.assetList.selectedItem])
		#else:
		#	mc.optionVar(rm=self.optionVarLastAssetStore)

		if self.animationList.selectedItem:
			mc.optionVar(stringValue=[self.optionVarLastAnimStore, self.animationList.selectedItem])
		#else:
		#	mc.optionVar(rm=self.optionVarLastAnimStore)

		if self.variationList.selectedItem:
			mc.optionVar(stringValue=[self.optionVarLastVariationStore, self.variationList.selectedItem])
		#else:
		#	mc.optionVar(rm=self.optionVarLastVariationStore)

		if self.versionList.selectedItem:
			mc.optionVar(stringValue=[self.optionVarLastVersionStore, self.versionList.selectedItem])
		#else:
		#	mc.optionVar(rm=self.optionVarLastVersionStore)

	def LoadPreviousSelection(self, *args):
		if mc.optionVar(exists=self.optionVarLastAssetStore):
			self.assetList.selectedItem = mc.optionVar(q=self.optionVarLastAssetStore)

		self.LoadAnimationList()

		if mc.optionVar(exists=self.optionVarLastAnimStore):
			self.animationList.selectedItem = mc.optionVar(q=self.optionVarLastAnimStore)

		self.LoadVariationList()

		if mc.optionVar(exists=self.optionVarLastVariationStore):
			self.variationList.selectedItem = mc.optionVar(q=self.optionVarLastVariationStore)

		self.LoadVersionList()

		if mc.optionVar(exists=self.optionVarLastVersionStore):
			self.versionList.selectedItem = mc.optionVar(q=self.optionVarLastVersionStore)

	
	def ClearPreviousDirectories(self, *args):		
		mc.optionVar(rm=self.optionVarDirStore)
		self.ConstructMenuBar()

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

			self.animationList.selectedItem = animName
			self.LoadAnimationList()
			self.LoadVersionList()
			self.LoadVariationList()
			
			self.versionList.selectedItem = '01'
			self.LoadVersionList()
			self.LoadVariationList()

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

	def SaveVersion(self, *args):
		animationFiles = self.versionList.listItems

		animationName = self.animationList.selectedItem
		wantedName = "%s_%s" % (self.assetList.selectedItem, self.animationList.selectedItem)

		if len(animationFiles) == 0:
			wantedName = "%s_%02d.mb" % (wantedName, 1)
		else:
			currentFile = mc.file(q=True, loc=True)
			if not os.path.exists(currentFile):
				currentFile = "%s_%02d.mb" % (wantedName, 1)

			baseFile = os.path.split(currentFile)[-1]
			baseName, ext = baseFile.split('.')

			wantedBasename = "%s_%s" % (self.assetList.selectedItem, self.animationList.selectedItem)
			if not wantedBasename in baseName:
				baseName = "%s_%02d" % (wantedBasename, 1)

			noVersionName = '_'.join(baseName.split('_')[:-1])
			version = int(baseName.split('_')[-1])

			versionFiles = []
			versions = []
			for item in self.versionList.listItems:
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
		if not self.assetList.selectedItem:
			print "No asset selected"
			return
		if not self.animationList.selectedItem:
			print "No animation selected"
			return
		if not self.versionList.selectedItem:
			print "No version selected"
			return

		filePath = self.versionFile
		mc.file(filePath, r=True, ignoreVersion=True, namespace=self.versionList.selectedItem)

	def UpdateCharTSLPopup(self, *args):
		rigPath = os.path.normpath(os.path.join(self.assetDirectory, "%s_rig.mb" % self.assetList.selectedItem ))
		if os.path.exists(rigPath):
			mc.menuItem( self.openRigMB, e=True, enable=True )
			mc.menuItem( self.importRigMB, e=True, enable=True )
		else:
			mc.menuItem( self.openRigMB, e=True, enable=False )
			mc.menuItem( self.importRigMB, e=True, enable=False )

	def OpenRig(self, *args):
		rigPath = os.path.normpath(os.path.join(self.assetDirectory, "%s_rig.mb" % self.assetList.selectedItem ))
		if os.path.exists(rigPath):
			mc.file(rigPath, o=True, f=True, ignoreVersion=True)

	def ImportRig(self, *args):
		rigPath = os.path.normpath(os.path.join(self.assetDirectory, "%s_rig.mb" % self.assetList.selectedItem ))
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
		if self.versionList.selectedItem != None:
			self.batchExportItems.append( {"asset":self.assetList.selectedItem,"animation":self.animationList.selectedItem,"variation":self.variationList.selectedItem,"version":self.versionList.selectedItem} )
		elif self.variationList != None:
			self.batchExportItems.append( {"asset":self.assetList.selectedItem,"animation":self.animationList.selectedItem,"variation":self.variationList.selectedItem,"version":self.versionList.displayItems[-1]} )
		
		self.RefreshQueueList()

	def RemoveFromQueue(self, *args):
		if args[0] == 0:
			idxes = self.queueTSL.selectedIndexes
			idxes.reverse()

			for idx in idxes:
				del self.batchExportItems[idx-1]
		elif args[0] == 1:
			self.batchExportItems = []

		self.RefreshQueueList()

	def BatchExport(self, *args):
		import pyunify.pipe.asset as asset

		for animDict in self.batchExportItems:
			self.assetList.selectedItem = animDict["asset"]
			self.LoadAnimationList()
			self.animationList.selectedItem = animDict["animation"]
			self.LoadVariationList()
			self.variationList.selectedItem = animDict["variation"]
			self.LoadVersionList()
			self.versionList.selectedItem = animDict["version"]

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
		self.queueTSL.ClearList()
		for item in self.batchExportItems:
			self.queueTSL.AddItem( "%s - %s - %s - %s" % (item["asset"],item["animation"],item["variation"],item["version"]))

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
		exportAssetPath = os.path.normpath(os.path.join( categoryExportPath, self.assetList.selectedItem))
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
			exportAnimPath = os.path.normpath(os.path.join(exportAnimPath, self.animationList.selectedItem))
			if not os.path.exists(exportAnimPath):
				os.mkdir(exportAnimPath)

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

			bakeAndPrep.BakeAndPrep()

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
