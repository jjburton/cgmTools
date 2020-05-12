#=================================================================================================================================================
#=================================================================================================================================================
#	cgmLocinator - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Tool for making locators and other stuffs
#
# ARGUMENTS:
#   Maya
#   distance
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1.11292011 - First version
#	0.1.12012011 - Closest object working, update selected, just loc selected working
#	0.1.12022011 - Got most things working now except for the stuff in time, tabs added, honoring postion option now
#	0.1.12032011 - Made hide info hideable, work on templates. Update locator over time working. Adding match tab
#	0.1.12062011 - Rewrite to work with maya 2010 and below, pushing most things through guiFactory now
#	0.1.12082011 - Reworked some progress bar stuff and added a purge cgm attrs tool to keep stuff clean for pipelines
#	0.1.12112011 - Simplified gui, cleaned up a few things
#	0.1.01052012 - Rewrote using Hammish's baseMelUI, adds the ability to save between tool instances, weirdness with
#                      some stuff not being visible when you show the
#	0.2.06172012 - Added buffer ability and modes
#
#=================================================================================================================================================
__version__ = '0.2.10122012'

from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.lib.classes.OptionVarFactory import *

import maya.mel as mel
import maya.cmds as mc
import cgm.core
from cgm.tools.lib import locinatorLib
#reload(locinatorLib)
from cgm.lib import (search,guiFactory)

def run():
	cgmLocinatorWin = locinatorClass()

class locinatorClass(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_Template = 'cgmUITemplate'
	
	WINDOW_NAME = 'cgmLocinatorWindow'
	WINDOW_TITLE = 'cgm.locinator - %s'%__version__
	DEFAULT_SIZE = 180, 275
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created


	def __init__(self):

		self.toolName = 'cgm.locinator'
		self.description = 'This tool makes locators based on selection types and provides ways to update those locators over time'
		self.author = 'Josh Burton'
		self.owner = 'CG Monks'
		self.website = 'www.cgmonks.com'
		self.version =  __version__ 
		self.optionVars = []

		self.currentFrameOnly = True
		self.startFrame = ''
		self.endFrame = ''
		self.startFrameField = ''
		self.endFrameField = ''
		self.forceBoundingBoxState = False
		self.forceEveryFrame = False
		self.showHelp = False
		self.helpBlurbs = []
		self.oldGenBlurbs = []

		self.showTimeSubMenu = False
		self.timeSubMenu = []
		

		#Menu
		self.setupVariables()
		self.UI_OptionsMenu = MelMenu( l='Options', pmc=self.buildOptionsMenu)
		self.UI_BufferMenu = MelMenu( l = 'Buffer', pmc=self.buildBufferMenu)
		self.UI_HelpMenu = MelMenu( l='Help', pmc=self.buildHelpMenu)
		
		self.ShowHelpOption = mc.optionVar( q='cgmVar_LocinatorShowHelp' )
		
		#Tabs
		tabs = MelTabLayout( self )
		TabBasic = MelColumnLayout(tabs)
		TabSpecial = MelColumnLayout( tabs )
		TabMatch = MelColumnLayout( tabs )
		n = 0
		for tab in 'Basic','Special','Match':
			tabs.setLabel(n,tab)
			n+=1

		self.buildBasicLayout(TabBasic)
		self.buildSpecialLayout(TabSpecial)
		self.buildMatchLayout(TabMatch)
		

		self.show()

	def setupVariables(self):
		self.LocinatorUpdateObjectsOptionVar = OptionVarFactory('cgmVar_LocinatorUpdateMode',defaultValue = 0)
		guiFactory.appendOptionVarList(self,'cgmVar_LocinatorUpdateMode')
		
		self.LocinatorUpdateObjectsBufferOptionVar = OptionVarFactory('cgmVar_LocinatorUpdateObjectsBuffer',defaultValue = [''])
		guiFactory.appendOptionVarList(self,'cgmVar_LocinatorUpdateObjectsBuffer')	
		
		self.DebugModeOptionVar = OptionVarFactory('cgmVar_LocinatorDebug',defaultValue=0)
		guiFactory.appendOptionVarList(self,self.DebugModeOptionVar.name)	
		
		self.SnapModeOptionVar = OptionVarFactory('cgmVar_SnapMatchMode',defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.SnapModeOptionVar.name)		
		
		#Old method...clean up at some point
		if not mc.optionVar( ex='cgmVar_ForceBoundingBoxState' ):
			mc.optionVar( iv=('cgmVar_ForceBoundingBoxState', 0) )
		if not mc.optionVar( ex='cgmVar_LocinatorShowHelp' ):
			mc.optionVar( iv=('cgmVar_LocinatorShowHelp', 0) )
		if not mc.optionVar( ex='cgmVar_LocinatorCurrentFrameOnly' ):
			mc.optionVar( iv=('cgmVar_LocinatorCurrentFrameOnly', 0) )
			
		if not mc.optionVar( ex='cgmVar_LocinatorBakingMode' ):
			mc.optionVar( iv=('cgmVar_LocinatorBakingMode', 0) )
			
		guiFactory.appendOptionVarList(self,'cgmVar_LocinatorShowHelp')	


	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Menus
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildOptionsMenu( self, *a ):
		self.UI_OptionsMenu.clear()
		
		#>>>Match Mode
		MatchModeMenu = MelMenuItem( self.UI_OptionsMenu, l='Match Mode', subMenu=True)		
		self.MatchModeOptions = ['parent','point','orient']
		
		self.MatchModeCollection = MelRadioMenuCollection()
		self.MatchModeCollectionChoices = []
		
		self.SnapModeOptionVar.update()#Incase another tool changed			
		
		self.matchMode = self.SnapModeOptionVar.value
		for c,item in enumerate(self.MatchModeOptions):
			if self.matchMode == c:
				rbValue = True
			else:
				rbValue = False
			self.MatchModeCollectionChoices.append(self.MatchModeCollection.createButton(MatchModeMenu,label=item,
			                                                                             rb = rbValue,
			                                                                             command = Callback(self.SnapModeOptionVar.set,c)))		

		# Placement Menu
		PlacementMenu = MelMenuItem( self.UI_OptionsMenu, l='Placement', subMenu=True)
		PlacementMenuCollection = MelRadioMenuCollection()

		if mc.optionVar( q='cgmVar_ForceBoundingBoxState' ) == 0:
			cgmOption = False
			pivotOption = True
		else:
			cgmOption = True
			pivotOption = False

		PlacementMenuCollection.createButton(PlacementMenu,l='Bounding Box Center',
				                             c=lambda *a: mc.optionVar( iv=('cgmVar_ForceBoundingBoxState', 1)),
				                             rb=cgmOption )
		PlacementMenuCollection.createButton(PlacementMenu,l='Pivot',
				                             c=lambda *a: mc.optionVar( iv=('cgmVar_ForceBoundingBoxState', 0)),
				                             rb=pivotOption )
		# Tagging options
		AutoloadMenu = MelMenuItem( self.UI_OptionsMenu, l='Tagging', subMenu=True)
		if not mc.optionVar( ex='cgmVar_TaggingUpdateRO' ):
			mc.optionVar( iv=('cgmVar_TaggingUpdateRO', 1) )
		guiFactory.appendOptionVarList(self,'cgmVar_TaggingUpdateRO')	
	  
		RenameOnUpdateState = mc.optionVar( q='cgmVar_TaggingUpdateRO' )
		MelMenuItem( AutoloadMenu, l="Update Rotation Order",
	                 cb= mc.optionVar( q='cgmVar_TaggingUpdateRO' ),
	                 c= lambda *a: guiFactory.doToggleIntOptionVariable('cgmVar_TaggingUpdateRO'))
		
		# Update Mode
		UpdateMenu = MelMenuItem( self.UI_OptionsMenu, l='Update Mode', subMenu=True)
		UpdateMenuCollection = MelRadioMenuCollection()

		if self.LocinatorUpdateObjectsOptionVar.value == 0:
			slMode = True
			bufferMode = False
		else:
			slMode = False
			bufferMode = True

		UpdateMenuCollection.createButton(UpdateMenu,l='Selected',
				                             c=lambda *a: self.LocinatorUpdateObjectsOptionVar.set(0),
				                             rb=slMode )
		UpdateMenuCollection.createButton(UpdateMenu,l='Buffer',
				                             c=lambda *a:self.LocinatorUpdateObjectsOptionVar.set(1),
				                             rb=bufferMode )
		

			                    
		MelMenuItemDiv( self.UI_OptionsMenu )
		MelMenuItem( self.UI_OptionsMenu, l="Reset",
			         c=lambda *a: self.reset())	
		
	def reset(self):	
		Callback(guiFactory.resetGuiInstanceOptionVars(self.optionVars,run))
		
	def reload(self):	
		run()
		
	def buildBufferMenu( self, *a ):
		self.UI_BufferMenu.clear()
		
		MelMenuItem( self.UI_BufferMenu, l="Define",
		             c= lambda *a: locinatorLib.defineObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
		
		MelMenuItem( self.UI_BufferMenu, l="Add Selected",
		             c= lambda *a: locinatorLib.addSelectedToObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
		
		MelMenuItem( self.UI_BufferMenu, l="Remove Selected",
		             c= lambda *a: locinatorLib.removeSelectedFromObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
		
		MelMenuItemDiv( self.UI_BufferMenu )
		MelMenuItem( self.UI_BufferMenu, l="Select Members",
				     c= lambda *a: locinatorLib.selectObjBufferMembers(self.LocinatorUpdateObjectsBufferOptionVar))
		MelMenuItem( self.UI_BufferMenu, l="Clear",
		             c= lambda *a: locinatorLib.clearObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
		
	def buildHelpMenu( self, *a ):
		self.UI_HelpMenu.clear()
		MelMenuItem( self.UI_HelpMenu, l="Show Help",
				     cb=self.ShowHelpOption,
				     c= lambda *a: self.do_showHelpToggle())
		MelMenuItem( self.UI_HelpMenu, l="Print Tools Help",
				     c=lambda *a: self.printHelp() )

		MelMenuItemDiv( self.UI_HelpMenu )
		MelMenuItem( self.UI_HelpMenu, l="About",
				     c=lambda *a: self.showAbout() )
		MelMenuItem( self.UI_HelpMenu, l="Debug",
				     cb=self.DebugModeOptionVar.value,
				     c= lambda *a: self.DebugModeOptionVar.toggle())	
		
	def do_showHelpToggle( self):
		guiFactory.toggleMenuShowState(self.ShowHelpOption,self.helpBlurbs)
		mc.optionVar( iv=('cgmVar_LocinatorShowHelp', not self.ShowHelpOption))
		self.ShowHelpOption = mc.optionVar( q='cgmVar_LocinatorShowHelp' )

	def do_showTimeSubMenuToggleOn( self):
		guiFactory.toggleMenuShowState(1,self.timeSubMenu)
		mc.optionVar( iv=('cgmVar_LocinatorCurrentFrameOnly', 1))

	def do_showTimeSubMenuToggleOff( self):
		guiFactory.toggleMenuShowState(0,self.timeSubMenu)
		mc.optionVar( iv=('cgmVar_LocinatorCurrentFrameOnly', 0))


	def showAbout(self):
		window = mc.window( title="About", iconName='About', ut = 'cgmUITemplate',resizeToFitChildren=True )
		mc.columnLayout( adjustableColumn=True )
		guiFactory.header(self.toolName,overrideUpper = True)
		mc.text(label='>>>A Part of the cgmTools Collection<<<', ut = 'cgmUIInstructionsTemplate')
		guiFactory.headerBreak()
		guiFactory.lineBreak()
		descriptionBlock = guiFactory.textBlock(self.description)

		guiFactory.lineBreak()
		mc.text(label=('%s%s' %('Written by: ',self.author)))
		mc.text(label=('%s%s%s' %('Copyright ',self.owner,', 2011')))
		guiFactory.lineBreak()
		mc.text(label='Version: %s' % self.version)
		mc.text(label='')
		guiFactory.doButton('Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://www.cgmonks.com/tools/maya-tools/locinator/")')
		guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
		mc.setParent( '..' )
		mc.showWindow( window )

	def printHelp(self):
		import locinatorLib
		help(locinatorLib)

	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Layouts
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildPlaceHolder(self,parent):
		self.containerName = MelColumnLayout(parent,ut='cgmUISubTemplate')
		return self.containerName
	
	def buildTimeSubMenu(self,parent):
		self.containerName = MelColumnLayout(parent,ut='cgmUISubTemplate')
		# Time Submenu
		mc.setParent(self.containerName)
		self.helpBlurbs.extend(guiFactory.instructions(" Set your time range",vis = self.ShowHelpOption))

		timelineInfo = search.returnTimelineInfo()


		# TimeInput Row
		TimeInputRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate')
		self.timeSubMenu.append( TimeInputRow )
		MelSpacer(TimeInputRow)
		MelLabel(TimeInputRow,l='start')

		self.startFrameField = MelIntField(TimeInputRow,'cgmLocWinStartFrameField',
	                                       width = 40,
	                                       value= timelineInfo['rangeStart'])
		TimeInputRow.setStretchWidget( MelSpacer(TimeInputRow) )
		MelLabel(TimeInputRow,l='end')

		self.endFrameField = MelIntField(TimeInputRow,'cgmLocWinEndFrameField',
	                                     width = 40,
	                                     value= timelineInfo['rangeEnd'])

		MelSpacer(TimeInputRow)
		TimeInputRow.layout()

		MelSeparator(self.containerName,ut = 'cgmUISubTemplate',style='none',height = 5)
		

		# Button Row
		TimeButtonRow = MelHSingleStretchLayout(self.containerName,padding = 1, ut='cgmUISubTemplate')
		MelSpacer(TimeButtonRow,w=2)
		currentRangeButton = guiFactory.doButton2(TimeButtonRow,'Current Range',
	                                              lambda *a: locinatorLib.setGUITimeRangeToCurrent(self),
	                                              'Sets the time range to the current slider range')
		TimeButtonRow.setStretchWidget( MelSpacer(TimeButtonRow,w=2) )
		sceneRangeButton = guiFactory.doButton2(TimeButtonRow,'Scene Range',
	                                            lambda *a: locinatorLib.setGUITimeRangeToScene(self),
	                                            'Sets the time range to the current slider range')
		MelSpacer(TimeButtonRow,w=2)
		
		TimeButtonRow.layout()

		
		#>>> Base Settings Flags
		self.KeyingModeCollection = MelRadioCollection()
		self.KeyingModeCollectionChoices = []		
		if not mc.optionVar( ex='cgmVar_LocinatorKeyingMode' ):
			mc.optionVar( iv=('cgmVar_LocinatorKeyingMode', 0) )
		guiFactory.appendOptionVarList(self,'cgmVar_LocinatorKeyingMode')	
			
		
		KeysSettingsFlagsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 2)
		MelSpacer(KeysSettingsFlagsRow,w=2)	
		KeysSettingsFlagsRow.setStretchWidget( MelLabel(KeysSettingsFlagsRow,l='Anim Option: ',align='right') )
		self.keyingOptions = ['Keys','All']
		for item in self.keyingOptions:
			cnt = self.keyingOptions.index(item)
			self.KeyingModeCollectionChoices.append(self.KeyingModeCollection.createButton(KeysSettingsFlagsRow,label=self.keyingOptions[cnt],
			                                                                               onCommand = Callback(guiFactory.toggleOptionVarState,self.keyingOptions[cnt],self.keyingOptions,'cgmVar_LocinatorKeyingMode',True)))
			MelSpacer(KeysSettingsFlagsRow,w=5)
		mc.radioCollection(self.KeyingModeCollection ,edit=True,sl= (self.KeyingModeCollectionChoices[ (mc.optionVar(q='cgmVar_LocinatorKeyingMode')) ]))
		
		KeysSettingsFlagsRow.layout()

		#>>> Base Settings Flags
		self.KeyingTargetCollection = MelRadioCollection()
		self.KeyingTargetCollectionChoices = []		
		if not mc.optionVar( ex='cgmVar_LocinatorKeyingTarget' ):
			mc.optionVar( iv=('cgmVar_LocinatorKeyingTarget', 0) )
		guiFactory.appendOptionVarList(self,'cgmVar_LocinatorKeyingTarget')	
			
		
		BakeSettingsFlagsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 2)
		MelSpacer(BakeSettingsFlagsRow,w=2)	
		BakeSettingsFlagsRow.setStretchWidget( MelLabel(BakeSettingsFlagsRow,l='From: ',align='right') )
		MelSpacer(BakeSettingsFlagsRow)
		self.keyTargetOptions = ['source','self']
		for item in self.keyTargetOptions:
			cnt = self.keyTargetOptions.index(item)
			self.KeyingTargetCollectionChoices.append(self.KeyingTargetCollection.createButton(BakeSettingsFlagsRow,label=self.keyTargetOptions[cnt],
		                                                                                       onCommand = Callback(guiFactory.toggleOptionVarState,self.keyTargetOptions[cnt],self.keyTargetOptions,'cgmVar_LocinatorKeyingTarget',True)))
			MelSpacer(BakeSettingsFlagsRow,w=5)
		mc.radioCollection(self.KeyingTargetCollection ,edit=True,sl= (self.KeyingTargetCollectionChoices[ (mc.optionVar(q='cgmVar_LocinatorKeyingTarget')) ]))
		
		BakeSettingsFlagsRow.layout()
		
		return self.containerName
	
	def buildBasicLayout(self,parent):
		mc.setParent(parent)
		guiFactory.header('Update')

		#>>>Time Section
		UpdateOptionRadioCollection = MelRadioCollection()
		EveryFrameOption = mc.optionVar( q='cgmVar_LocinatorBakeState' )
		mc.setParent(parent)
		guiFactory.lineSubBreak()
		
		#>>> Time Menu Container
		self.BakeModeOptionList = ['Current Frame','Bake']
		cgmVar_Name = 'cgmVar_LocinatorBakeState'
		guiFactory.appendOptionVarList(self,'cgmVar_LocinatorBakeState')	
		
		if not mc.optionVar( ex=cgmVar_Name ):
			mc.optionVar( iv=(cgmVar_Name, 0) )
		
		#build our sub section options
		self.ContainerList = []
		
		#Mode Change row 
		ModeSetRow = MelHSingleStretchLayout(parent,ut='cgmUISubTemplate')
		self.BakeModeRadioCollection = MelRadioCollection()
		self.BakeModeChoiceList = []	
		MelSpacer(ModeSetRow,w=2)

		self.BakeModeChoiceList.append(self.BakeModeRadioCollection.createButton(ModeSetRow,label=self.BakeModeOptionList[0],
	                                                                      onCommand = Callback(guiFactory.toggleModeState,self.BakeModeOptionList[0],self.BakeModeOptionList,cgmVar_Name,self.ContainerList,True)))
		
		ModeSetRow.setStretchWidget( MelSpacer(ModeSetRow) )
		
		self.BakeModeChoiceList.append(self.BakeModeRadioCollection.createButton(ModeSetRow,label=self.BakeModeOptionList[1],
	                                                                      onCommand = Callback(guiFactory.toggleModeState,self.BakeModeOptionList[1],self.BakeModeOptionList,cgmVar_Name,self.ContainerList,True)))
		
		ModeSetRow.layout()
		
		
		#>>>
		self.ContainerList.append( self.buildPlaceHolder(parent) )
		self.ContainerList.append( self.buildTimeSubMenu( parent) )
		
		mc.radioCollection(self.BakeModeRadioCollection,edit=True, sl=self.BakeModeChoiceList[mc.optionVar(q=cgmVar_Name)])
		#>>>
		
		mc.setParent(parent)

		guiFactory.doButton2(parent,'Do it!',
	                         lambda *a: locinatorLib.doUpdateLoc(self),
	                         'Update a locator at a particular frame or through a timeline')

		guiFactory.lineSubBreak()



		#>>>  Loc Me Section
		guiFactory.lineBreak()
		guiFactory.lineSubBreak()
		guiFactory.doButton2(parent,'Just Loc Selected',
			                 lambda *a: locinatorLib.doLocMe(self),
			                 'Create an updateable locator based off the selection and options')



	def buildSpecialLayout(self,parent):
		SpecialColumn = MelColumnLayout(parent)

		#>>>  Center Section
		guiFactory.lineSubBreak()
		guiFactory.doButton2(SpecialColumn,'Locate Center',
		                     lambda *a: locinatorLib.doLocCenter(self),
				             'Find the center point from a selection set')


		#>>>  Closest Point Section
		guiFactory.lineSubBreak()
		guiFactory.doButton2(SpecialColumn,'Locate Closest Point',
		                     lambda *a: locinatorLib.doLocClosest(self),
				             'Select the proximity object(s), then the object to find point on. Accepted target object types are - nurbsCurves and surfaces and poly objects')

		#>>>  Curves Section
		guiFactory.lineSubBreak()
		guiFactory.doButton2(SpecialColumn,'Loc CVs of curve',
		                     lambda *a: locinatorLib.doLocCVsOfObject(),
				             "Locs the cv's at the cv coordinates")

		guiFactory.lineSubBreak()
		guiFactory.doButton2(SpecialColumn,'Loc CVs on the curve',
		                     lambda *a: locinatorLib.doLocCVsOnObject(),
				             "Locs cv's at closest point on the curve")

		guiFactory.lineBreak()

		#>>> Update Section
		guiFactory.lineSubBreak()
		guiFactory.doButton2(SpecialColumn,'Update Selected',
		                     lambda *a: locinatorLib.doUpdateLoc(self),
				             "Only works with locators created with this tool")


	def buildMatchLayout(self,parent):

		MatchColumn = MelColumnLayout(parent)

		#>>>  Tag Section
		guiFactory.lineSubBreak()
		guiFactory.doButton2(MatchColumn,'Tag it',
		                     lambda *a: locinatorLib.doTagObjects(self),
				             "Tag the selected objects to the first locator in the selection set. After this relationship is set up, you can match objects to that locator.")


		#>>>  Purge Section
		guiFactory.lineSubBreak()
		self.helpBlurbs.extend(guiFactory.instructions("  Purge all traces of cgmThinga tools from the object",vis = self.ShowHelpOption))
		guiFactory.doButton2(MatchColumn,'Purge it',
		                     lambda *a: locinatorLib.doPurgeCGMAttrs(self),
				             "Clean it")

		guiFactory.lineBreak()

		#>>> Update Section
		guiFactory.lineSubBreak()
		guiFactory.doButton2(MatchColumn,'Update Selected',
		                     lambda *a: locinatorLib.doUpdateLoc(self),
				             "Only works with locators created with this tool")