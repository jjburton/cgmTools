#=================================================================================================================================================
#=================================================================================================================================================
#	cgm.thingamarig - a part of cgmTools
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
__version__ = '0.1.07052012'

from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.lib.classes.OptionVarFactory import *
from cgm.lib.classes.CharacterFactory import *

import maya.mel as mel
import maya.cmds as mc

from cgm.tools.lib import (thingamarigLib)
from cgm.lib import (search,guiFactory,modules)

from cgm.lib import guiFactory

reload(thingamarigLib)
reload(guiFactory)
reload(modules)

def run():
	cgmThingamarigWin = thingamarigClass()
		
class thingamarigClass(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_Template = 'cgmUITemplate'
	
	WINDOW_NAME = 'cgmThingamarigWindow'
	WINDOW_TITLE = 'cgm.thingamarig'
	DEFAULT_SIZE = 250, 400
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = False  #always resets the size of the window when its re-created

	def __init__( self):		
		self.toolName = 'cgm.thingamarig'
		self.description = 'This is a series of tools for working with cgm Sets'
		self.author = 'Josh Burton'
		self.owner = 'CG Monks'
		self.website = 'www.cgmonks.com'
		self.version =  __version__ 
		self.optionVars = []
		self.scenePuppets = []
		self.puppetInstance = False
		self.puppetStateOptions = ['Define','Template','Skeleton','Rig']
		self.addModules = ['Spine','Leg','Arm','Limb','Finger','Foot','Neck','Head','Spine']
				
		self.setTypes = ['NONE',
		                 'animation',
		                 'layout',
		                 'modeling',
		                 'td',
		                 'fx',
		                 'lighting']
		
		
		self.setModes = ['<<< All Loaded Sets >>>','<<< Active Sets >>>']
		self.scenePuppets = modules.returnMasterObjects()		
		
		self.showHelp = False
		self.helpBlurbs = []
		self.oldGenBlurbs = []
		
		self.objectSets = []

		#Menu
		self.setupVariables()
		self.setMode = self.SetToolsModeOptionVar.value		
		
		self.UI_PuppetMenu = MelMenu( l='Puppet', pmc=self.buildPuppetMenu)
		self.UI_AddModulesMenu = MelMenu( l='Add', pmc=self.buildAddModulesMenu)
		self.UI_OptionsMenu = MelMenu( l='Options', pmc=self.buildOptionsMenu)		
		self.UI_HelpMenu = MelMenu( l='Help', pmc=self.buildHelpMenu)
		
		self.ShowHelpOption = mc.optionVar( q='cgmVar_AnimToolsShowHelp' )
		
		#GUI
		
		self.Main_buildLayout(self)
		
		if self.scenePuppets:
			thingamarigLib.activatePuppet(self,self.scenePuppets[0])

		
		self.show()
		
	def setupVariables(self):
		self.PuppetModeOptionVar = OptionVarFactory('cgmVar_PuppetCreateMode',defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.PuppetModeOptionVar.name)
		
		self.ActiveObjectSetsOptionVar = OptionVarFactory('cgmVar_activeObjectSets',defaultValue = [''])
		self.ActiveRefsOptionVar = OptionVarFactory('cgmVar_activeRefs',defaultValue = [''])
		self.ActiveTypesOptionVar = OptionVarFactory('cgmVar_activeTypes',defaultValue = [''])
		self.SetToolsModeOptionVar = OptionVarFactory('cgmVar_thingamarigMode', defaultValue = 0)
		self.KeyTypeOptionVar = OptionVarFactory('cgmVar_KeyType', defaultValue = 0)
		self.ShowHelpOptionVar = OptionVarFactory('cgmVar_thingamarigShowHelp', defaultValue = 0)
		self.MaintainLocalSetGroupOptionVar = OptionVarFactory('cgmVar_MaintainLocalSetGroup', defaultValue = 1)
		self.HideSetGroupOptionVar = OptionVarFactory('cgmVar_HideSetGroups', defaultValue = 1)
		self.HideAnimLayerSetsOptionVar = OptionVarFactory('cgmVar_HideAnimLayerSets', defaultValue = 1)
		self.HideMayaSetsOptionVar = OptionVarFactory('cgmVar_HideMayaSets', defaultValue = 1)
		
		
		guiFactory.appendOptionVarList(self,self.ActiveObjectSetsOptionVar.name)
		guiFactory.appendOptionVarList(self,self.ActiveRefsOptionVar.name)
		guiFactory.appendOptionVarList(self,self.ActiveTypesOptionVar.name)
		guiFactory.appendOptionVarList(self,self.SetToolsModeOptionVar.name)
		guiFactory.appendOptionVarList(self,self.ShowHelpOptionVar.name)
		guiFactory.appendOptionVarList(self,self.KeyTypeOptionVar.name)
		guiFactory.appendOptionVarList(self,self.HideSetGroupOptionVar.name)
		guiFactory.appendOptionVarList(self,self.MaintainLocalSetGroupOptionVar.name)
		guiFactory.appendOptionVarList(self,self.HideAnimLayerSetsOptionVar.name)
		guiFactory.appendOptionVarList(self,self.HideMayaSetsOptionVar.name)

		
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Menus
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildPuppetMenu( self, *a ):
		self.UI_PuppetMenu.clear()
		MelMenuItem( self.UI_PuppetMenu, l="New",
	                 c=lambda *a:thingamarigLib.activatePuppet(self))
		
		#Build load menu
		self.scenePuppets = modules.returnMasterObjects()		
		loadMenu = MelMenuItem( self.UI_PuppetMenu, l='Pick Puppet:', subMenu=True)
		
		if self.scenePuppets:
			for i,m in enumerate(self.scenePuppets):
				MelMenuItem( loadMenu, l="%s"%m,
					         c= Callback(thingamarigLib.activatePuppet,self,m))		
		else:
			MelMenuItem( loadMenu, l="None found")	

		#>>> Reset Options		
		MelMenuItemDiv( self.UI_PuppetMenu )
		MelMenuItem( self.UI_PuppetMenu, l="Reload",
			         c=lambda *a: self.reload())		
		MelMenuItem( self.UI_PuppetMenu, l="Reset",
			         c=lambda *a: self.reset())
	
	def buildAddModulesMenu( self, *a ):
		self.UI_AddModulesMenu.clear()
		for i,m in enumerate(self.addModules):
			MelMenuItem( self.UI_AddModulesMenu, l="%s"%m,
				         c="print '%s'"%m)

		MelMenuItemDiv( self.UI_AddModulesMenu )
		
	def buildOptionsMenu( self, *a ):
		self.UI_OptionsMenu.clear()
		

		
	def reset(self):	
		Callback(guiFactory.resetGuiInstanceOptionVars(self.optionVars,run))
		
	def reload(self):	
		run()
		

	def buildHelpMenu( self, *a ):
		self.UI_HelpMenu.clear()
		MelMenuItem( self.UI_HelpMenu, l="Show Help",
				     cb=self.ShowHelpOptionVar.value,
				     c= lambda *a: self.do_showHelpToggle())
		
		MelMenuItem( self.UI_HelpMenu, l="Print Set Report",
				     c=lambda *a: self.printReport() )
		MelMenuItem( self.UI_HelpMenu, l="Print Tools Help",
				     c=lambda *a: self.printHelp() )

		MelMenuItemDiv( self.UI_HelpMenu )
		MelMenuItem( self.UI_HelpMenu, l="About",
				     c=lambda *a: self.showAbout() )

	def do_showHelpToggle( self):
		guiFactory.toggleMenuShowState(self.ShowHelpOptionVar.value,self.helpBlurbs)
		self.ShowHelpOptionVar.toggle()


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
		guiFactory.doButton('Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://www.cgmonks.com/tools/maya-tools/thingamarig/")')
		guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
		mc.setParent( '..' )
		mc.showWindow( window )

	def printHelp(self):
		help(thingamarigLib)
		
	def printReport(self):
		thingamarigLib.printReport(self)


	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Layouts
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	
	def Main_buildLayout(self,parent):
		def modeSet( item ):
			i =  self.setModes.index(item)
			self.SetToolsModeOptionVar.set( i )
			self.setMode = i
		
		MainForm = MelFormLayout(parent)
		TopSection = MelColumnLayout(MainForm)	
		SetHeader = guiFactory.header('Puppet')
		
		#>>>  Top Section
		#Report
		self.puppetReport = MelLabel(TopSection,
				                     bgc = dictionary.returnStateColor('help'),
				                     align = 'center',
				                     label = '...',
				                     h=20)
		MelSeparator(TopSection,ut='cgmUITemplate',h=5)
		
		#Edit name and state mode buttons
		MasterPuppetRow = MelHSingleStretchLayout(TopSection,padding = 5)
		MelSpacer(MasterPuppetRow,w=5)
		self.MasterPuppetTF = MelTextField(MasterPuppetRow,
		                                   bgc = [1,1,1],
		                                   ec = lambda *a:thingamarigLib.updatePuppetName(self))
		MasterPuppetRow.setStretchWidget(self.MasterPuppetTF)
		
		self.puppetStateButtonsDict = {}
		for i,s in enumerate(self.puppetStateOptions):
			self.puppetStateButtonsDict[i] = guiFactory.doButton2(MasterPuppetRow,list(s)[0],
			                                                      "print '%s'"%s,
			                                                      enable = False)
		MelSpacer(MasterPuppetRow,w=20)
		
		MasterPuppetRow.layout()
		MelSeparator(TopSection,ut='cgmUITemplate',h=5)
		
		#Initial State Button Row
		self.InitialStateButtonRow = MelHLayout(TopSection, h = 20,vis=False,padding = 5)
		guiFactory.doButton2(self.InitialStateButtonRow,'Add Geo',
		                     lambda *a:thingamarigLib.doAddGeo(self))
		guiFactory.doButton2(self.InitialStateButtonRow,'Build Size Template',
		                     lambda *a:thingamarigLib.doBuildSizeTemplate(self))
		
		self.InitialStateButtonRow.layout()
		
		#Initial State Mode Row
		self.PuppetModeCollection = MelRadioCollection()
		self.PuppetModeCollectionChoices = []			
		
		self.InitialStateModeRow = MelHSingleStretchLayout(TopSection,padding = 2,vis=False)	
		MelSpacer(self.InitialStateModeRow,w=5)				
		MelLabel(self.InitialStateModeRow,l='Modes')
		Spacer = MelSeparator(self.InitialStateModeRow,w=10)						
		for i,item in enumerate(CharacterTypes):
			self.PuppetModeCollectionChoices.append(self.PuppetModeCollection.createButton(self.InitialStateModeRow,label=item,
			                                                                               onCommand = Callback(thingamarigLib.setPuppetBaseMode,self,i)))
			MelSpacer(self.InitialStateModeRow,w=3)
		self.InitialStateModeRow.setStretchWidget( Spacer )
		MelSpacer(self.InitialStateModeRow,w=2)		
		self.InitialStateModeRow.layout()	
		
		mc.radioCollection(self.PuppetModeCollection ,edit=True,sl= (self.PuppetModeCollectionChoices[ (self.PuppetModeOptionVar.value) ]))
		
		#>>>  All Sets menu
		AllSetsRow = MelFormLayout(MainForm,height = 20)
		activeState = True
		i = 1
		if self.objectSets:
			for b in self.objectSets:
				if b not in self.ActiveObjectSetsOptionVar.value:
					activeState = False
		else:
			activeState = False
			
		tmpActive = MelCheckBox(AllSetsRow,
	                            annotation = 'Sets all sets active',
	                            value = activeState,
	                            onCommand =  Callback(thingamarigLib.doSetAllSetsAsActive,self),
	                            offCommand = Callback(thingamarigLib.doSetAllSetsAsInactive,self))
		
		tmpSel = guiFactory.doButton2(AllSetsRow,
		                              ' s ',
		                              lambda *a:thingamarigLib.doSelectMultiSets(self,self.SetToolsModeOptionVar.value),
		                              'Select All Loaded/Active Sets')
						
		# Mode toggle box
		self.SetModeOptionMenu = MelOptionMenu(AllSetsRow,
		                                       cc = modeSet)
		for o in self.setModes:
			self.SetModeOptionMenu.append(o)
			
		self.SetModeOptionMenu.selectByIdx(self.setMode,False)
			
		tmpKey = guiFactory.doButton2(AllSetsRow,
	                                  ' k ',
		                              lambda *a:thingamarigLib.doKeyMultiSets(self,self.SetToolsModeOptionVar.value),
		                              'Key All Sets')
		tmpDeleteKey = guiFactory.doButton2(AllSetsRow,
	                                    ' d ',
		                                lambda *a:thingamarigLib.doDeleteMultiCurrentKeys(self,self.SetToolsModeOptionVar.value),
	                                    'Delete All Set Keys')	
		tmpReset = guiFactory.doButton2(AllSetsRow,
	                                    ' r ',
		                                lambda *a:thingamarigLib.doResetMultiSets(self,self.SetToolsModeOptionVar.value),		                                
	                                    'Reset All Set Keys')	
		
		mc.formLayout(AllSetsRow, edit = True,
	                  af = [(tmpActive, "left", 10),
	                        (tmpReset,"right",10)],
	                  ac = [(tmpSel,"left",0,tmpActive),
	                        (self.SetModeOptionMenu,"left",4,tmpSel),
	                        (self.SetModeOptionMenu,"right",4,tmpKey),
	                        (tmpKey,"right",2,tmpDeleteKey),
		                    (tmpDeleteKey,"right",2,tmpReset)
		                    ])
		
		#>>> Sets building section
		allPopUpMenu = MelPopupMenu(self.SetModeOptionMenu ,button = 3)
		
		allCategoryMenu = MelMenuItem(allPopUpMenu,
	                               label = 'Make Type:',
	                               sm = True)
		#Mulit set type
		for n in self.setTypes:
			MelMenuItem(allCategoryMenu,
		                label = n,
		                c = Callback(thingamarigLib.doMultiSetType,self,self.SetToolsModeOptionVar.value,n))
		
		
		
		
		#>>> Sets building section
		SetListScroll = MelScrollLayout(MainForm,cr = 1, ut = 'cgmUISubTemplate')
		SetMasterForm = MelFormLayout(SetListScroll)
		SetListColumn = MelColumnLayout(SetMasterForm, adj = True, rowSpacing = 3)
		
		self.helpInfo = MelLabel(MainForm,
		                         l = " Set buffer options: Set active, select, change name,add,remove,key,purge",
		                         ut = 'cgmUIInstructionsTemplate',
		                         al = 'center',
		                         ww = True,vis = self.ShowHelpOptionVar.value)
		self.helpBlurbs.extend([self.helpInfo ])
		
		VerifyRow = guiFactory.doButton2(MainForm,
		                                'Check Puppet',
		                                lambda *a:thingamarigLib.doCreateSet(self),
		                                'Create new buffer from selected buffer')	
			
		SetMasterForm(edit = True,
		                 af = [(SetListColumn,"top",0),
		                       (SetListColumn,"left",0),
		                       (SetListColumn,"right",0),
		                       (SetListColumn,"bottom",0)])
		
		
	
		
		
		
		MainForm(edit = True,
		         af = [(TopSection,"top",0),	
		               (TopSection,"left",0),
		               (TopSection,"right",0),		               
		               (AllSetsRow,"left",0),
		               (AllSetsRow,"right",0),
		               (SetListScroll,"left",0),
		               (SetListScroll,"right",0),
		               (SetListScroll,"left",0),
		               (SetListScroll,"right",0),				       
		               (self.helpInfo,"left",0),
		               (self.helpInfo,"right",0),
		               (VerifyRow,"left",4),
		               (VerifyRow,"right",4),		               
		               (VerifyRow,"bottom",4)],
		         ac = [(AllSetsRow,"top",2,TopSection),
		               (SetListScroll,"top",2,AllSetsRow),
		               (SetListScroll,"bottom",0,self.helpInfo),
		               (self.helpInfo,"bottom",0,VerifyRow)],
		         attachNone = [(VerifyRow,"top")])	
		

