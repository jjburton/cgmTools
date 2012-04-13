#=================================================================================================================================================
#=================================================================================================================================================
#	cgmLocinator - a part of cgmTools
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
#
#=================================================================================================================================================
from cgm.lib.zoo.zooPyMaya.baseMelUI import *

import maya.mel as mel
import maya.cmds as mc

from cgm.tools.lib import locinatorLib
reload(locinatorLib)
from cgm.lib import (search,guiFactory)


def run():
	cgmLocinatorWin = locinatorClass()

class locinatorClass(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_Template = 'cgmUITemplate'
	
	WINDOW_NAME = 'cgmLocinatorWindow'
	WINDOW_TITLE = 'cgm.locinator'
	DEFAULT_SIZE = 175, 260
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created


	def __init__( self):

		self.toolName = 'Locinator'
		self.description = 'This tool makes locators based on selection types and provides ways to update those locators over time'
		self.author = 'Josh Burton'
		self.owner = 'CG Monks'
		self.website = 'www.cgmonks.com'
		self.version = '0.1.12112011'

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
		
		self.ShowHelpOption = mc.optionVar( q='cgmVarLocinatorShowHelp' )
		
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

	def setupVariables():
		if not mc.optionVar( ex='cgmVarForceBoundingBoxState' ):
			mc.optionVar( iv=('cgmVarForceBoundingBoxState', 0) )
		if not mc.optionVar( ex='cgmVarForceEveryFrame' ):
			mc.optionVar( iv=('cgmVarForceEveryFrame', 0) )
		if not mc.optionVar( ex='cgmVarLocinatorShowHelp' ):
			mc.optionVar( iv=('cgmVarLocinatorShowHelp', 0) )
		if not mc.optionVar( ex='cgmCurrentFrameOnly' ):
			mc.optionVar( iv=('cgmCurrentFrameOnly', 0) )
		if not mc.optionVar( ex='cgmVarLocinatorShowHelp' ):
			mc.optionVar( iv=('cgmVarLocinatorShowHelp', 0) )
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Menus
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildOptionsMenu( self, *a ):
		self.UI_OptionsMenu.clear()

		# Placement Menu
		PlacementMenu = MelMenuItem( self.UI_OptionsMenu, l='Placement', subMenu=True)
		PlacementMenuCollection = MelRadioMenuCollection()

		if mc.optionVar( q='cgmVarForceBoundingBoxState' ) == 0:
			cgmOption = False
			pivotOption = True
		else:
			cgmOption = True
			pivotOption = False

		PlacementMenuCollection.createButton(PlacementMenu,l='Bounding Box Center',
				                             c=lambda *a: mc.optionVar( iv=('cgmVarForceBoundingBoxState', 1)),
				                             rb=cgmOption )
		PlacementMenuCollection.createButton(PlacementMenu,l='Pivot',
				                             c=lambda *a: mc.optionVar( iv=('cgmVarForceBoundingBoxState', 0)),
				                             rb=pivotOption )
		"""
		# Anim Menu
		AnimMenu = MelMenuItem( self.UI_OptionsMenu, l='Anim', subMenu=True)
		AnimMenuCollection = MelRadioMenuCollection()

		if mc.optionVar( q='cgmVarForceEveryFrame' ) == 0:
			EveryFrameOption = False
			KeysOnlyOption = True
		else:
			EveryFrameOption = True
			KeysOnlyOption = False

		AnimMenuCollection.createButton(AnimMenu,l='Every Frame',
				                        c=lambda *a: mc.optionVar( iv=('cgmVarForceEveryFrame', 1)),
				                        rb=EveryFrameOption )
		AnimMenuCollection.createButton(AnimMenu,l='Keys Only',
				                        c=lambda *a: mc.optionVar( iv=('cgmVarForceEveryFrame', 0)),
				                        rb=KeysOnlyOption )

		MelMenuItemDiv( self.UI_OptionsMenu )
		"""

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
		self.ShowHelpOption = mc.optionVar( q='cgmVarLocinatorShowHelp' )
		guiFactory.toggleMenuShowState(self.ShowHelpOption,self.helpBlurbs)
		mc.optionVar( iv=('cgmVarLocinatorShowHelp', not self.ShowHelpOption))

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
		guiFactory.doButton('Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://www.cgmonks.com/tools/maya-tools/locinator/")')
		guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
		mc.setParent( '..' )
		mc.showWindow( window )

	def printHelp(self):
		import locinatorLib
		help(locinatorLib)

	def do_everyFrameToggle( self):
		EveryFrameOption = mc.optionVar( q='cgmVarForceEveryFrame' )
		guiFactory.toggleMenuShowState(EveryFrameOption,self.timeSubMenu)
		mc.optionVar( iv=('cgmVarForceEveryFrame', not EveryFrameOption))



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
		if not mc.optionVar( ex='cgmKeyingMode' ):
			mc.optionVar( iv=('cgmKeyingMode', 0) )
		
		KeysSettingsFlagsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 2)
		MelSpacer(KeysSettingsFlagsRow,w=2)	
		KeysSettingsFlagsRow.setStretchWidget( MelLabel(KeysSettingsFlagsRow,l='Option: ',align='right') )
		self.keyingOptions = ['Keys','All']
		for item in self.keyingOptions:
			cnt = self.keyingOptions.index(item)
			self.KeyingModeCollectionChoices.append(self.KeyingModeCollection.createButton(KeysSettingsFlagsRow,label=self.keyingOptions[cnt],
			                                                                               onCommand = Callback(guiFactory.toggleOptionVarState,self.keyingOptions[cnt],self.keyingOptions,'cgmKeyingMode',True)))
			MelSpacer(KeysSettingsFlagsRow,w=5)
		mc.radioCollection(self.KeyingModeCollection ,edit=True,sl= (self.KeyingModeCollectionChoices[ (mc.optionVar(q='cgmKeyingMode')) ]))
		
		KeysSettingsFlagsRow.layout()

		#>>> Base Settings Flags
		self.KeyingTargetCollection = MelRadioCollection()
		self.KeyingTargetCollectionChoices = []		
		if not mc.optionVar( ex='cgmKeyingTarget' ):
			mc.optionVar( iv=('cgmKeyingTarget', 0) )
		
		BakeSettingsFlagsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 2)
		MelSpacer(BakeSettingsFlagsRow,w=2)	
		BakeSettingsFlagsRow.setStretchWidget( MelLabel(BakeSettingsFlagsRow,l='Keys: ',align='right') )
		MelSpacer(BakeSettingsFlagsRow)
		self.keyTargetOptions = ['source','self']
		for item in self.keyTargetOptions:
			cnt = self.keyTargetOptions.index(item)
			self.KeyingTargetCollectionChoices.append(self.KeyingTargetCollection.createButton(BakeSettingsFlagsRow,label=self.keyTargetOptions[cnt],
		                                                                                       onCommand = Callback(guiFactory.toggleOptionVarState,self.keyTargetOptions[cnt],self.keyTargetOptions,'cgmKeyingTarget',True)))
			MelSpacer(BakeSettingsFlagsRow,w=5)
		mc.radioCollection(self.KeyingTargetCollection ,edit=True,sl= (self.KeyingTargetCollectionChoices[ (mc.optionVar(q='cgmKeyingTarget')) ]))
		
		BakeSettingsFlagsRow.layout()
		
		return self.containerName
	
	def buildBasicLayout(self,parent):

		#>>>Time Section
		UpdateOptionRadioCollection = MelRadioCollection()
		EveryFrameOption = mc.optionVar( q='cgmLocinatorBakeState' )
		mc.setParent(parent)
		guiFactory.lineSubBreak()
		guiFactory.header('Update')
		
		#>>> Time Menu Container
		self.BakeModeOptionList = ['Current Frame','Bake']
		cgmVarName = 'cgmLocinatorBakeState'
		
		if not mc.optionVar( ex=cgmVarName ):
			mc.optionVar( iv=(cgmVarName, 0) )
		
		#build our sub section options
		self.ContainerList = []
		
		#Mode Change row 
		ModeSetRow = MelHSingleStretchLayout(parent,ut='cgmUISubTemplate')
		self.BakeModeRadioCollection = MelRadioCollection()
		self.BakeModeChoiceList = []	
		MelSpacer(ModeSetRow,w=2)

		self.BakeModeChoiceList.append(self.BakeModeRadioCollection.createButton(ModeSetRow,label=self.BakeModeOptionList[0],
	                                                                      onCommand = Callback(guiFactory.toggleModeState,self.BakeModeOptionList[0],self.BakeModeOptionList,cgmVarName,self.ContainerList,True)))
		
		ModeSetRow.setStretchWidget( MelSpacer(ModeSetRow) )
		
		self.BakeModeChoiceList.append(self.BakeModeRadioCollection.createButton(ModeSetRow,label=self.BakeModeOptionList[1],
	                                                                      onCommand = Callback(guiFactory.toggleModeState,self.BakeModeOptionList[1],self.BakeModeOptionList,cgmVarName,self.ContainerList,True)))
		
		ModeSetRow.layout()
		
		
		#>>>
		self.ContainerList.append( self.buildPlaceHolder(parent) )
		self.ContainerList.append( self.buildTimeSubMenu( parent) )
		
		mc.radioCollection(self.BakeModeRadioCollection,edit=True, sl=self.BakeModeChoiceList[mc.optionVar(q=cgmVarName)])
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
		                     lambda *a: locinatorLib.doLocClosest(),
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