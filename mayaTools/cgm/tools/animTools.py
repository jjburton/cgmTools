#=================================================================================================================================================
#=================================================================================================================================================
#	cgm.animTools - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Tool for making locators and other stuffs
#
# REQUIRES:
#   Maya
#   distance
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
#=================================================================================================================================================
__version__ = '0.1.04182012'

from cgm.lib.zoo.zooPyMaya.baseMelUI import *

import maya.mel as mel
import maya.cmds as mc

from cgm.tools.lib import (animToolsLib,
                           tdToolsLib,
                           locinatorLib,
                           )
from cgm.lib import guiFactory

reload(animToolsLib)
reload(guiFactory)
from cgm.lib import (search,guiFactory)


def run():
	cgmAnimToolsWin = animToolsClass()

class animToolsClass(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_Template = 'cgmUITemplate'
	
	WINDOW_NAME = 'cgmAnimToolsWindow'
	WINDOW_TITLE = 'cgm.animTools'
	DEFAULT_SIZE = 180, 260
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created


	def __init__( self):

		self.toolName = 'animTools'
		self.description = 'This tool makes locators based on selection types and provides ways to update those locators over time'
		self.author = 'Josh Burton'
		self.owner = 'CG Monks'
		self.website = 'www.cgmonks.com'
		self.version = __version__

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
		self.setupVariables
		self.UI_OptionsMenu = MelMenu( l='Options', pmc=self.buildOptionsMenu)
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

	def setupVariables():
		if not mc.optionVar( ex='cgmVar_ForceBoundingBoxState' ):
			mc.optionVar( iv=('cgmVar_ForceBoundingBoxState', 0) )
		if not mc.optionVar( ex='cgmVar_ForceEveryFrame' ):
			mc.optionVar( iv=('cgmVar_ForceEveryFrame', 0) )
		if not mc.optionVar( ex='cgmVar_animToolsShowHelp' ):
			mc.optionVar( iv=('cgmVar_animToolsShowHelp', 0) )
		if not mc.optionVar( ex='cgmCurrentFrameOnly' ):
			mc.optionVar( iv=('cgmCurrentFrameOnly', 0) )
		if not mc.optionVar( ex='cgmVar_animToolsShowHelp' ):
			mc.optionVar( iv=('cgmVar_animToolsShowHelp', 0) )
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

	def do_showHelpToggle( self):
		guiFactory.toggleMenuShowState(self.ShowHelpOption,self.helpBlurbs)
		mc.optionVar( iv=('cgmVar_animToolsShowHelp', not self.ShowHelpOption))
		self.ShowHelpOption = mc.optionVar( q='cgmVar_animToolsShowHelp' )

	def do_showTimeSubMenuToggleOn( self):
		guiFactory.toggleMenuShowState(1,self.timeSubMenu)
		mc.optionVar( iv=('cgmCurrentFrameOnly', 1))

	def do_showTimeSubMenuToggleOff( self):
		guiFactory.toggleMenuShowState(0,self.timeSubMenu)
		mc.optionVar( iv=('cgmCurrentFrameOnly', 0))


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
	                                              lambda *a: animToolsLib.setGUITimeRangeToCurrent(self),
	                                              'Sets the time range to the current slider range')
		TimeButtonRow.setStretchWidget( MelSpacer(TimeButtonRow,w=2) )
		sceneRangeButton = guiFactory.doButton2(TimeButtonRow,'Scene Range',
	                                            lambda *a: animToolsLib.setGUITimeRangeToScene(self),
	                                            'Sets the time range to the current slider range')
		MelSpacer(TimeButtonRow,w=2)
		
		TimeButtonRow.layout()

		
		#>>> Base Settings Flags
		self.KeyingModeCollection = MelRadioCollection()
		self.KeyingModeCollectionChoices = []		
		if not mc.optionVar( ex='cgmVar_KeyingMode' ):
			mc.optionVar( iv=('cgmVar_KeyingMode', 0) )
		
		KeysSettingsFlagsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 2)
		MelSpacer(KeysSettingsFlagsRow,w=2)	
		KeysSettingsFlagsRow.setStretchWidget( MelLabel(KeysSettingsFlagsRow,l='Anim Option: ',align='right') )
		self.keyingOptions = ['Keys','All']
		for item in self.keyingOptions:
			cnt = self.keyingOptions.index(item)
			self.KeyingModeCollectionChoices.append(self.KeyingModeCollection.createButton(KeysSettingsFlagsRow,label=self.keyingOptions[cnt],
			                                                                               onCommand = Callback(guiFactory.toggleOptionVarState,self.keyingOptions[cnt],self.keyingOptions,'cgmVar_KeyingMode',True)))
			MelSpacer(KeysSettingsFlagsRow,w=5)
		mc.radioCollection(self.KeyingModeCollection ,edit=True,sl= (self.KeyingModeCollectionChoices[ (mc.optionVar(q='cgmVar_KeyingMode')) ]))
		
		KeysSettingsFlagsRow.layout()

		#>>> Base Settings Flags
		self.KeyingTargetCollection = MelRadioCollection()
		self.KeyingTargetCollectionChoices = []		
		if not mc.optionVar( ex='cgmVar_KeyingTarget' ):
			mc.optionVar( iv=('cgmVar_KeyingTarget', 0) )
		
		BakeSettingsFlagsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 2)
		MelSpacer(BakeSettingsFlagsRow,w=2)	
		BakeSettingsFlagsRow.setStretchWidget( MelLabel(BakeSettingsFlagsRow,l='From: ',align='right') )
		MelSpacer(BakeSettingsFlagsRow)
		self.keyTargetOptions = ['source','self']
		for item in self.keyTargetOptions:
			cnt = self.keyTargetOptions.index(item)
			self.KeyingTargetCollectionChoices.append(self.KeyingTargetCollection.createButton(BakeSettingsFlagsRow,label=self.keyTargetOptions[cnt],
		                                                                                       onCommand = Callback(guiFactory.toggleOptionVarState,self.keyTargetOptions[cnt],self.keyTargetOptions,'cgmVar_KeyingTarget',True)))
			MelSpacer(BakeSettingsFlagsRow,w=5)
		mc.radioCollection(self.KeyingTargetCollection ,edit=True,sl= (self.KeyingTargetCollectionChoices[ (mc.optionVar(q='cgmVar_KeyingTarget')) ]))
		
		BakeSettingsFlagsRow.layout()
		
		return self.containerName
	
	def Match_buildLayout(self,parent):
		mc.setParent(parent)
		guiFactory.lineSubBreak()

		#>>>Match Mode
		self.MatchModeCollection = MelRadioCollection()
		self.MatchModeCollectionChoices = []		
		if not mc.optionVar( ex='cgmVar_MatchMode' ):
			mc.optionVar( iv=('cgmVar_MatchMode', 0) )	
			
		#MatchModeFlagsRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)	
		MatchModeFlagsRow = MelHSingleStretchLayout(parent,ut='cgmUIReservedTemplate',padding = 2)	
		MelSpacer(MatchModeFlagsRow,w=2)				
		self.MatchModeOptions = ['parent','point','orient']
		for item in self.MatchModeOptions:
			cnt = self.MatchModeOptions.index(item)
			self.MatchModeCollectionChoices.append(self.MatchModeCollection.createButton(MatchModeFlagsRow,label=self.MatchModeOptions[cnt],
			                                                                             onCommand = Callback(guiFactory.toggleOptionVarState,self.MatchModeOptions[cnt],self.MatchModeOptions,'cgmVar_MatchMode',True)))
			MelSpacer(MatchModeFlagsRow,w=3)
		MatchModeFlagsRow.setStretchWidget( self.MatchModeCollectionChoices[-1] )
		MelSpacer(MatchModeFlagsRow,w=2)		
		MatchModeFlagsRow.layout()	
		
		mc.radioCollection(self.MatchModeCollection ,edit=True,sl= (self.MatchModeCollectionChoices[ (mc.optionVar(q='cgmVar_MatchMode')) ]))
		
		#>>>Time Section
		UpdateOptionRadioCollection = MelRadioCollection()
		EveryFrameOption = mc.optionVar( q='cgmVar_AnimToolsBakeState' )
		
		#>>> Time Menu Container
		self.BakeModeOptionList = ['Current Frame','Bake']
		cgmVar_Name = 'cgmVar_AnimToolsBakeState'
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
	                         lambda *a: animToolsLib.doUpdateLoc(self),
	                         'Update a locator at a particular frame or through a timeline')

		guiFactory.lineSubBreak()



		#>>>  Loc Me Section
		guiFactory.lineBreak()
		guiFactory.lineSubBreak()
		guiFactory.doButton2(parent,'Just Loc Selected',
			                 lambda *a: animToolsLib.doLocMe(self),
			                 'Create an updateable locator based off the selection and options')



	def Keys_buildLayout(self,parent):
		SpecialColumn = MelColumnLayout(parent)

		#>>>  Center Section
		guiFactory.lineSubBreak()
		guiFactory.doButton2(SpecialColumn,'autoTangent',
		                     lambda *a: mel.eval('autoTangent'),
				             'Fantastic script courtesy of Michael Comet')


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
		                     lambda *a: tdToolsLib.doPointSnap(),
				             "Basic Orient Snap")