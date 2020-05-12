#=================================================================================================================================================
#=================================================================================================================================================
#	cgm.animTools - a part of cgmTools
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
#=================================================================================================================================================
__version__ = '0.1.11.29.2012'

from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.lib.classes.OptionVarFactory import *

import maya.mel as mel
import maya.cmds as mc

from cgm.tools.lib import (animToolsLib,
                           tdToolsLib,
                           locinatorLib)
from cgm.lib import guiFactory

#reload(animToolsLib)
#reload(guiFactory)
#reload(locinatorLib)

from cgm.lib import (search,guiFactory)


def run():
	cgmAnimToolsWin = animToolsClass()

class animToolsClass(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_Template = 'cgmUITemplate'
	
	WINDOW_NAME = 'cgmAnimToolsWindow'
	WINDOW_TITLE = 'cgm.animTools - %s'%__version__
	DEFAULT_SIZE = 180, 350
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created


	def __init__( self):

		self.toolName = 'cgm.animTools'
		self.description = 'This is a series of tools for basic animation functions'
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
		
		self.ShowHelpOption = mc.optionVar( q='cgmVar_AnimToolsShowHelp' )
		
		#Tabs
		tabs = MelTabLayout( self )
		MatchTab = MelColumnLayout(tabs)
		SnapTab = MelColumnLayout( tabs )
		KeysTab = MelColumnLayout( tabs )

		n = 0
		for tab in 'Match','Snap','Keys':
			tabs.setLabel(n,tab)
			n+=1

		self.Match_buildLayout(MatchTab)
		self.Snap_buildLayout(SnapTab)
		self.Keys_buildLayout(KeysTab)

		self.show()

	def setupVariables(self):
		self.LocinatorUpdateObjectsOptionVar = OptionVarFactory('cgmVar_AnimToolsUpdateMode',defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.LocinatorUpdateObjectsOptionVar.name)
		
		self.LocinatorUpdateObjectsBufferOptionVar = OptionVarFactory('cgmVar_LocinatorUpdateObjectsBuffer',defaultValue = [''])
		guiFactory.appendOptionVarList(self,self.LocinatorUpdateObjectsBufferOptionVar.name)	
		
		self.DebugModeOptionVar = OptionVarFactory('cgmVar_AnimToolsDebug',defaultValue=0)
		guiFactory.appendOptionVarList(self,self.DebugModeOptionVar.name)		
		
		#Old method...clean up at some point
		if not mc.optionVar( ex='cgmVar_ForceBoundingBoxState' ):
			mc.optionVar( iv=('cgmVar_ForceBoundingBoxState', 0) )
		if not mc.optionVar( ex='cgmVar_ForceEveryFrame' ):
			mc.optionVar( iv=('cgmVar_ForceEveryFrame', 0) )
		if not mc.optionVar( ex='cgmVar_animToolsShowHelp' ):
			mc.optionVar( iv=('cgmVar_animToolsShowHelp', 0) )
		if not mc.optionVar( ex='cgmVar_CurrentFrameOnly' ):
			mc.optionVar( iv=('cgmVar_CurrentFrameOnly', 0) )
		if not mc.optionVar( ex='cgmVar_animToolsShowHelp' ):
			mc.optionVar( iv=('cgmVar_animToolsShowHelp', 0) )
			
		guiFactory.appendOptionVarList(self,'cgmVar_animToolsShowHelp')
		
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Menus
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildOptionsMenu( self, *a ):
		self.UI_OptionsMenu.clear()

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
			         c=lambda *a: guiFactory.resetGuiInstanceOptionVars(self.optionVars,run))

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
		mc.optionVar( iv=('cgmVar_animToolsShowHelp', not self.ShowHelpOption))
		self.ShowHelpOption = mc.optionVar( q='cgmVar_animToolsShowHelp' )

	def do_showTimeSubMenuToggleOn( self):
		guiFactory.toggleMenuShowState(1,self.timeSubMenu)
		mc.optionVar( iv=('cgmVar_CurrentFrameOnly', 1))

	def do_showTimeSubMenuToggleOff( self):
		guiFactory.toggleMenuShowState(0,self.timeSubMenu)
		mc.optionVar( iv=('cgmVar_CurrentFrameOnly', 0))


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
		guiFactory.doButton('Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://www.cgmonks.com/tools/maya-tools/animTools/")')
		guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
		mc.setParent( '..' )
		mc.showWindow( window )

	def printHelp(self):
		import animToolsLib
		help(animToolsLib)

	def do_everyFrameToggle( self):
		EveryFrameOption = mc.optionVar( q='cgmVar_ForceEveryFrame' )
		guiFactory.toggleMenuShowState(EveryFrameOption,self.timeSubMenu)
		mc.optionVar( iv=('cgmVar_ForceEveryFrame', not EveryFrameOption))



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
		if not mc.optionVar( ex='cgmVar_AnimToolsKeyingMode' ):
			mc.optionVar( iv=('cgmVar_AnimToolsKeyingMode', 0) )
		guiFactory.appendOptionVarList(self,'cgmVar_AnimToolsKeyingMode')
		
		KeysSettingsFlagsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 2)
		MelSpacer(KeysSettingsFlagsRow,w=2)	
		KeysSettingsFlagsRow.setStretchWidget( MelLabel(KeysSettingsFlagsRow,l='Anim Option: ',align='right') )
		self.keyingOptions = ['Keys','All']
		for item in self.keyingOptions:
			cnt = self.keyingOptions.index(item)
			self.KeyingModeCollectionChoices.append(self.KeyingModeCollection.createButton(KeysSettingsFlagsRow,label=self.keyingOptions[cnt],
			                                                                               onCommand = Callback(guiFactory.toggleOptionVarState,self.keyingOptions[cnt],self.keyingOptions,'cgmVar_AnimToolsKeyingMode',True)))
			MelSpacer(KeysSettingsFlagsRow,w=5)
		mc.radioCollection(self.KeyingModeCollection ,edit=True,sl= (self.KeyingModeCollectionChoices[ (mc.optionVar(q='cgmVar_AnimToolsKeyingMode')) ]))
		
		KeysSettingsFlagsRow.layout()

		#>>> Base Settings Flags
		self.KeyingTargetCollection = MelRadioCollection()
		self.KeyingTargetCollectionChoices = []		
		if not mc.optionVar( ex='cgmVar_AnimToolsKeyingTarget' ):
			mc.optionVar( iv=('cgmVar_AnimToolsKeyingTarget', 0) )
		guiFactory.appendOptionVarList(self,'cgmVar_AnimToolsKeyingTarget')
		
		BakeSettingsFlagsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 2)
		MelSpacer(BakeSettingsFlagsRow,w=2)	
		BakeSettingsFlagsRow.setStretchWidget( MelLabel(BakeSettingsFlagsRow,l='From: ',align='right') )
		MelSpacer(BakeSettingsFlagsRow)
		self.keyTargetOptions = ['source','self']
		for item in self.keyTargetOptions:
			cnt = self.keyTargetOptions.index(item)
			self.KeyingTargetCollectionChoices.append(self.KeyingTargetCollection.createButton(BakeSettingsFlagsRow,label=self.keyTargetOptions[cnt],
		                                                                                       onCommand = Callback(guiFactory.toggleOptionVarState,self.keyTargetOptions[cnt],self.keyTargetOptions,'cgmVar_AnimToolsKeyingTarget',True)))
			MelSpacer(BakeSettingsFlagsRow,w=5)
		mc.radioCollection(self.KeyingTargetCollection ,edit=True,sl= (self.KeyingTargetCollectionChoices[ (mc.optionVar(q='cgmVar_AnimToolsKeyingTarget')) ]))
		
		BakeSettingsFlagsRow.layout()
		
		return self.containerName
	
	def Match_buildLayout(self,parent):
		mc.setParent(parent)
		guiFactory.header('Update')

		#>>>Match Mode
		self.MatchModeCollection = MelRadioCollection()
		self.MatchModeCollectionChoices = []		
		if not mc.optionVar( ex='cgmVar_AnimToolsMatchMode' ):
			mc.optionVar( iv=('cgmVar_AnimToolsMatchMode', 0) )	
			
		guiFactory.appendOptionVarList(self,'cgmVar_AnimToolsMatchMode')
			
		#MatchModeFlagsRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)	
		MatchModeFlagsRow = MelHSingleStretchLayout(parent,ut='cgmUIReservedTemplate',padding = 2)	
		MelSpacer(MatchModeFlagsRow,w=2)				
		self.MatchModeOptions = ['parent','point','orient']
		for item in self.MatchModeOptions:
			cnt = self.MatchModeOptions.index(item)
			self.MatchModeCollectionChoices.append(self.MatchModeCollection.createButton(MatchModeFlagsRow,label=self.MatchModeOptions[cnt],
			                                                                             onCommand = Callback(guiFactory.toggleOptionVarState,self.MatchModeOptions[cnt],self.MatchModeOptions,'cgmVar_AnimToolsMatchMode',True)))
			MelSpacer(MatchModeFlagsRow,w=3)
		MatchModeFlagsRow.setStretchWidget( self.MatchModeCollectionChoices[-1] )
		MelSpacer(MatchModeFlagsRow,w=2)		
		MatchModeFlagsRow.layout()	
		
		mc.radioCollection(self.MatchModeCollection ,edit=True,sl= (self.MatchModeCollectionChoices[ (mc.optionVar(q='cgmVar_AnimToolsMatchMode')) ]))
		
		#>>>Time Section
		UpdateOptionRadioCollection = MelRadioCollection()
		
		#>>> Time Menu Container
		self.BakeModeOptionList = ['Current Frame','Bake']
		cgmVar_Name = 'cgmVar_AnimToolsBakeState'
		if not mc.optionVar( ex=cgmVar_Name ):
			mc.optionVar( iv=(cgmVar_Name, 0) )
			
		EveryFrameOption = mc.optionVar( q='cgmVar_AnimToolsBakeState' )
		guiFactory.appendOptionVarList(self,'cgmVar_AnimToolsBakeState')
		
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
	                         'Update an obj or locator at a particular frame or through a timeline')

		guiFactory.lineSubBreak()


		#>>>  Loc Me Section
		guiFactory.lineBreak()
		guiFactory.lineSubBreak()
		guiFactory.doButton2(parent,'Just Loc Selected',
			                 lambda *a: locinatorLib.doLocMe(self),
			                 'Create an updateable locator based off the selection and options')


		#>>>  Tag Section
		guiFactory.lineSubBreak()
		guiFactory.doButton2(parent,'Tag it',
		                     lambda *a: locinatorLib.doTagObjects(self),
				             "Tag the selected objects to the first locator in the selection set. After this relationship is set up, you can match objects to that locator.")



	def Keys_buildLayout(self,parent):
		SpecialColumn = MelColumnLayout(parent)

		#>>>  Center Section
		guiFactory.header('Tangents')		
		guiFactory.lineSubBreak()
		guiFactory.doButton2(SpecialColumn,'autoTangent',
		                     lambda *a: mel.eval('autoTangent'),
				             'Fantastic script courtesy of Michael Comet')
		
		guiFactory.lineBreak()		
		guiFactory.header('Breakdowns')
		guiFactory.lineSubBreak()
		guiFactory.doButton2(SpecialColumn,'tweenMachine',
		                     lambda *a: mel.eval('tweenMachine'),
				             'Breakdown tool courtesy of Justin Barrett')
		guiFactory.lineSubBreak()		
		guiFactory.doButton2(SpecialColumn,'breakdownDragger',
		                     lambda *a: animToolsLib.ml_breakdownDraggerCall(),
				             'Breakdown tool courtesy of Morgan Loomis')
		
		guiFactory.lineBreak()		
		guiFactory.header('Utilities')
		guiFactory.lineSubBreak()		
		guiFactory.doButton2(SpecialColumn,'arcTracr',
		                     lambda *a: animToolsLib.ml_arcTracerCall(),
				             'Path tracing tool courtesy of Morgan Loomis')
		guiFactory.lineSubBreak()				
		guiFactory.doButton2(SpecialColumn,'copy Anim',
		                     lambda *a: animToolsLib.ml_copyAnimCall(),
				             'Animation copy tool courtesy of Morgan Loomis')
		guiFactory.lineSubBreak()				
		guiFactory.doButton2(SpecialColumn,'convert Rotation Order',
		                     lambda *a: animToolsLib.ml_convertRotationOrderCall(),
				             'Rotation Order Conversion tool courtesy of Morgan Loomis')
		guiFactory.lineSubBreak()				
		guiFactory.doButton2(SpecialColumn,'stopwatch',
		                     lambda *a: animToolsLib.ml_stopwatchCall(),
				             'Stop Watch tool courtesy of Morgan Loomis')

	def Snap_buildLayout(self,parent):

		SnapColumn = MelColumnLayout(parent)

		#>>>  Snap Section
		guiFactory.lineSubBreak()
		guiFactory.doButton2(SnapColumn,'Parent Snap',
		                     lambda *a: tdToolsLib.doParentSnap(),
				             "Basic Parent Snap")
		
		guiFactory.lineSubBreak()
		guiFactory.doButton2(SnapColumn,'Point Snap',
		                     lambda *a: tdToolsLib.doPointSnap(),
				             "Basic Point Snap")
		
		guiFactory.lineSubBreak()
		guiFactory.doButton2(SnapColumn,'Orient Snap',
		                     lambda *a: tdToolsLib.doOrientSnap(),
				             "Basic Orient Snap")