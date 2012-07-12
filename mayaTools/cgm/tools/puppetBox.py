#=================================================================================================================================================
#=================================================================================================================================================
#	cgm.puppetBox - a part of cgmTools
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
from cgm.rigger.PuppetFactory import *

import maya.mel as mel
import maya.cmds as mc

from cgm.tools.lib import (puppetBoxLib)
from cgm.lib import (search,guiFactory,modules)

from cgm.lib import guiFactory,dictionary

reload(puppetBoxLib)
reload(guiFactory)
reload(modules)

def run():
	cgmPuppetBoxWin = puppetBoxClass()
		
class puppetBoxClass(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_Template = 'cgmUITemplate'
	
	WINDOW_NAME = 'cgmPuppetBoxWindow'
	WINDOW_TITLE = 'cgm.puppetBox'
	DEFAULT_SIZE = 250, 400
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = False  #always resets the size of the window when its re-created

	def __init__( self):		
		self.toolName = 'cgm.puppetBox'
		self.description = 'This is a series of tools for working with cgm Sets'
		self.author = 'Josh Burton'
		self.owner = 'CG Monks'
		self.website = 'www.cgmonks.com'
		self.version =  __version__ 
		self.optionVars = []
		self.scenePuppets = []
		self.puppetInstance = False
		self.puppetStateOptions = ['Define','Template','Skeleton','Rig']
		#self.addModules = ['Spine','Leg','Arm','Limb','Finger','Foot','Neck','Head','Spine']
		self.addModules = ['Segment']
		self.moduleRows = {}
		
		self.setTypes = ['NONE',
		                 'animation',
		                 'layout',
		                 'modeling',
		                 'td',
		                 'fx',
		                 'lighting']
		
		
		self.setModes = ['<<< All Loaded Sets >>>','<<< Active Sets >>>']
		self.scenePuppets = modules.returnPuppetObjects()
		self.UI_StateRows = {'define':[],'template':[],'skeleton':[],'rig':[]}
		
		self.showHelp = False
		self.helpBlurbs = []
		self.oldGenBlurbs = []
		
		#Menu
		self.setupVariables()
		
		self.UI_PuppetMenu = MelMenu( l='Puppet', pmc=self.buildPuppetMenu)
		self.UI_AddModulesMenu = MelMenu( l='Add', pmc=self.buildAddModulesMenu)
		self.UI_OptionsMenu = MelMenu( l='Options', pmc=self.buildOptionsMenu)		
		self.UI_HelpMenu = MelMenu( l='Help', pmc=self.buildHelpMenu)
		
		self.ShowHelpOption = mc.optionVar( q='cgmVar_AnimToolsShowHelp' )
		
		#GUI
				
		if self.scenePuppets:
			puppetBoxLib.activatePuppet(self,self.scenePuppets[0])
			
		self.Main_buildLayout(self)
		
		if self.puppetInstance:
			puppetBoxLib.updateUIPuppet(self)
			self.updateModulesUI()
		
		self.show()
		
	def setupVariables(self):
		self.PuppetModeOptionVar = OptionVarFactory('cgmVar_PuppetCreateMode',defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.PuppetModeOptionVar.name)
		
		self.PuppetAimOptionVar = OptionVarFactory('cgmVar_PuppetAimAxis',defaultValue = 2)
		guiFactory.appendOptionVarList(self,self.PuppetAimOptionVar.name)		
		self.PuppetUpOptionVar = OptionVarFactory('cgmVar_PuppetUpAxis',defaultValue = 1)
		guiFactory.appendOptionVarList(self,self.PuppetUpOptionVar.name)	
		self.PuppetOutOptionVar = OptionVarFactory('cgmVar_PuppetOutAxis',defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.PuppetOutOptionVar.name)			
		
		
		self.ActiveObjectSetsOptionVar = OptionVarFactory('cgmVar_activeObjectSets',defaultValue = [''])
		self.ActiveRefsOptionVar = OptionVarFactory('cgmVar_activeRefs',defaultValue = [''])
		self.ActiveTypesOptionVar = OptionVarFactory('cgmVar_activeTypes',defaultValue = [''])
		self.SetToolsModeOptionVar = OptionVarFactory('cgmVar_puppetBoxMode', defaultValue = 0)
		self.KeyTypeOptionVar = OptionVarFactory('cgmVar_KeyType', defaultValue = 0)
		self.ShowHelpOptionVar = OptionVarFactory('cgmVar_puppetBoxShowHelp', defaultValue = 0)
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

	def updateModulesUI(self):
		#deleteExisting
		if self.moduleRows:
			for k in self.moduleRows.keys():
				mc.deleteUI(self.moduleRows.get(k))
						
		if self.puppetInstance:
			self.modulesDict = {}
			self.activeModulesCBDict = {}		
			self.moduleRows = {}
			
			for i,b in enumerate(self.puppetInstance.ModulesBuffer.bufferList):
				#Store the info to a dict
				self.modulesDict[i] = b
				#s = SetFactory(b)

				#tmpSetRow = MelFormLayout(self.ModuleListColumn,height = 20)
				# NEED to get colors
				
				#Build label for Frame
				buffer = [b]
				#buffer.append()
				
				self.moduleRows[i] = MelFrameLayout(self.ModuleListColumn,l=b,
				                                    collapse=True,
				                                    collapsable=True,
				                                    bgc = [0.971679, 1, 0])
				
				MelLabel(self.moduleRows[i],l='asfasfasdfasdfasdf')
				
				#Get check box state
 
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Menus
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildPuppetMenu( self, *a ):
		self.UI_PuppetMenu.clear()
		
		#>>> Puppet Options	
		"""
		if self.puppetInstance:		
			
			MelMenuItem( self.UI_PuppetMenu,l=('%s'%self.puppetInstance.nameBase),en=False)
			
			aimAxisMenu = MelMenuItem( self.UI_PuppetMenu, l='Aim Axis:', subMenu=True)
			aimAxisMenuCollection = MelRadioMenuCollection()
			
			for i,a in enumerate(self.puppetInstance.aAimAxis.enum.split(':')):
				aimRBState = False
				if i == self.puppetInstance.aAimAxis.value:
					aimRBState = True				
				aimAxisMenuCollection.createButton( aimAxisMenu, l="%s"%a,
				                                    rb = aimRBState,
				                                    c= Callback(self.puppetInstance.doSetAimAxis,i))	
			
			
			upAxisMenu = MelMenuItem( self.UI_PuppetMenu, l='Up Axis:', subMenu=True)
			upAxisMenuCollection = MelRadioMenuCollection()
			
			for i,a in enumerate(self.puppetInstance.aUpAxis.enum.split(':')):
				upRBState = False
				if i == self.puppetInstance.aUpAxis.value:
					upRBState = True
				upAxisMenuCollection.createButton( upAxisMenu, l="%s"%a,
				                                   rb = upRBState,
				                                   c= Callback(self.puppetInstance.doSetUpAxis,i))	
				
			outAxisMenu = MelMenuItem( self.UI_PuppetMenu, l='Out Axis:', subMenu=True)
			outAxisMenuCollection = MelRadioMenuCollection()
			
			for i,a in enumerate(self.puppetInstance.aOutAxis.enum.split(':')):
				outRBState = False
				if i == self.puppetInstance.aOutAxis.value:
					outRBState = True
				outAxisMenuCollection.createButton( outAxisMenu, l="%s"%a,
			                                       rb = outRBState,
			                                       c= Callback(self.puppetInstance.doSetOutAxis,i))	
				
		



			MelMenuItemDiv( self.UI_PuppetMenu )
		
		"""
		MelMenuItem( self.UI_PuppetMenu, l="New",
	                 c=lambda *a:puppetBoxLib.activeAndUpdatePuppet(self))
		
		#Build load menu
		self.scenePuppets = modules.returnPuppetObjects()		
		loadMenu = MelMenuItem( self.UI_PuppetMenu, l='Pick Puppet:', subMenu=True)
		
		if self.scenePuppets:
			for i,m in enumerate(self.scenePuppets):
				MelMenuItem( loadMenu, l="%s"%m,
					         c= Callback(puppetBoxLib.activeAndUpdatePuppet,self,m))		
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
				         c=lambda *a:puppetBoxLib.addModule(self,m))

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
		guiFactory.doButton('Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://www.cgmonks.com/tools/maya-tools/puppetBox/")')
		guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
		mc.setParent( '..' )
		mc.showWindow( window )

	def printHelp(self):
		help(puppetBoxLib)
		
	def printReport(self):
		puppetBoxLib.printReport(self)


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
		                                   ec = lambda *a:puppetBoxLib.updatePuppetName(self))
		MasterPuppetRow.setStretchWidget(self.MasterPuppetTF)
		
		self.puppetStateButtonsDict = {}
		for i,s in enumerate(self.puppetStateOptions):
			self.puppetStateButtonsDict[i] = guiFactory.doButton2(MasterPuppetRow,list(s)[0],
			                                                      "print '%s'"%s,
			                                                      enable = False)
		MelSpacer(MasterPuppetRow,w=20)
		
		MasterPuppetRow.layout()
		#MelSeparator(TopSection,ut='cgmUITemplate',h=2)
		
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# Define State Rows
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>		
		#Initial State Mode Row
		self.PuppetModeCollection = MelRadioCollection()
		self.PuppetModeCollectionChoices = []			
		
		self.InitialStateModeRow = MelHSingleStretchLayout(TopSection,padding = 2,vis=False)	
		MelSpacer(self.InitialStateModeRow,w=5)				
		MelLabel(self.InitialStateModeRow,l='Template Modes')
		Spacer = MelSeparator(self.InitialStateModeRow,w=10)						
		for i,item in enumerate(CharacterTypes):
			self.PuppetModeCollectionChoices.append(self.PuppetModeCollection.createButton(self.InitialStateModeRow,label=item,
			                                                                               onCommand = Callback(puppetBoxLib.setPuppetBaseMode,self,i)))
			MelSpacer(self.InitialStateModeRow,w=3)
		self.InitialStateModeRow.setStretchWidget( Spacer )
		MelSpacer(self.InitialStateModeRow,w=2)		
		self.InitialStateModeRow.layout()	
		
		mc.radioCollection(self.PuppetModeCollection ,edit=True,sl= (self.PuppetModeCollectionChoices[ (self.PuppetModeOptionVar.value) ]))
		self.UI_StateRows['define'].append(self.InitialStateModeRow)
		
		
		self.AxisFrame = MelFrameLayout(TopSection,label = 'Axis',vis=False,
		                                collapse=True,
		                                collapsable=True,
		                                ut = 'cgmUIHeaderTemplate')
		self.UI_StateRows['define'].append(self.AxisFrame)
		MelSeparator(TopSection,style='none',h=5)						
		
		#Aim Axis Mode Row
		self.AimAxisCollection = MelRadioCollection()
		self.AimAxisCollectionChoices = []			
		
		self.AimAxisRow = MelHSingleStretchLayout(self.AxisFrame,padding = 2,vis=False)	
		MelSpacer(self.AimAxisRow,w=5)				
		MelLabel(self.AimAxisRow,l='Aim ')
		Spacer = MelSeparator(self.AimAxisRow,w=10)						
		for i,item in enumerate(axisDirections):
			self.AimAxisCollectionChoices.append(self.AimAxisCollection.createButton(self.AimAxisRow,label=item,
			                                                                         onCommand = Callback(puppetBoxLib.setPuppetAxisAim,self,i)))
			MelSpacer(self.AimAxisRow,w=3)
		self.AimAxisRow.setStretchWidget( Spacer )
		MelSpacer(self.AimAxisRow,w=2)		
		self.AimAxisRow.layout()	
		
		mc.radioCollection(self.AimAxisCollection ,edit=True,sl= (self.AimAxisCollectionChoices[ (self.PuppetAimOptionVar.value) ]))
		
		#Up Axis Mode Row
		self.UpAxisCollection = MelRadioCollection()
		self.UpAxisCollectionChoices = []			
		
		self.UpAxisRow = MelHSingleStretchLayout(self.AxisFrame,padding = 2,vis=False)	
		MelSpacer(self.UpAxisRow,w=5)				
		MelLabel(self.UpAxisRow,l='Up ')
		Spacer = MelSeparator(self.UpAxisRow,w=10)						
		for i,item in enumerate(axisDirections):
			self.UpAxisCollectionChoices.append(self.UpAxisCollection.createButton(self.UpAxisRow,label=item,
			                                                                         onCommand = Callback(puppetBoxLib.setPuppetAxisUp,self,i)))
			MelSpacer(self.UpAxisRow,w=3)
		self.UpAxisRow.setStretchWidget( Spacer )
		MelSpacer(self.UpAxisRow,w=2)		
		self.UpAxisRow.layout()	
		
		mc.radioCollection(self.UpAxisCollection ,edit=True,sl= (self.UpAxisCollectionChoices[ (self.PuppetUpOptionVar.value) ]))
		
		#Out Axis Mode Row
		self.OutAxisCollection = MelRadioCollection()
		self.OutAxisCollectionChoices = []			
		
		self.OutAxisRow = MelHSingleStretchLayout(self.AxisFrame,padding = 2,vis=False)	
		MelSpacer(self.OutAxisRow,w=5)				
		MelLabel(self.OutAxisRow,l='Out ')
		Spacer = MelSeparator(self.OutAxisRow,w=10)						
		for i,item in enumerate(axisDirections):
			self.OutAxisCollectionChoices.append(self.OutAxisCollection.createButton(self.OutAxisRow,label=item,
			                                                                         onCommand = Callback(puppetBoxLib.setPuppetAxisOut,self,i)))
			MelSpacer(self.OutAxisRow,w=3)
		self.OutAxisRow.setStretchWidget( Spacer )
		MelSpacer(self.OutAxisRow,w=2)		
		self.OutAxisRow.layout()	
		
		mc.radioCollection(self.OutAxisCollection ,edit=True,sl= (self.OutAxisCollectionChoices[ (self.PuppetOutOptionVar.value) ]))
		
		
		#Initial State Button Row
		self.InitialStateButtonRow = MelHLayout(TopSection, h = 20,vis=False,padding = 5)
		guiFactory.doButton2(self.InitialStateButtonRow,'Add Geo',
		                     lambda *a:puppetBoxLib.doAddGeo(self))
		guiFactory.doButton2(self.InitialStateButtonRow,'Build Size Template',
		                     lambda *a:puppetBoxLib.doBuildSizeTemplate(self))
		
		self.InitialStateButtonRow.layout()
		self.UI_StateRows['define'].append(self.InitialStateButtonRow)
		
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# Multi Module
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

		#>>>  All Sets menu
		AllModulesRow = MelFormLayout(MainForm,height = 20)
		activeState = True
		i = 1
			
		tmpActive = MelCheckBox(AllModulesRow,
	                            annotation = 'Sets all sets active',
	                            value = activeState,
	                            onCommand =  Callback(puppetBoxLib.doSetAllSetsAsActive,self),
	                            offCommand = Callback(puppetBoxLib.doSetAllSetsAsInactive,self))
		
		tmpSel = guiFactory.doButton2(AllModulesRow,
		                              ' s ',
		                              'Select All Loaded/Active Sets')
						
		# Mode toggle box
		self.ModuleModeOptionMenu = MelOptionMenu(AllModulesRow,
		                                       cc = modeSet)
			
			
		tmpKey = guiFactory.doButton2(AllModulesRow,
	                                  ' k ',
		                              'Key All Sets')
		tmpDeleteKey = guiFactory.doButton2(AllModulesRow,
	                                    ' d ',
	                                    'Delete All Set Keys')	
		tmpReset = guiFactory.doButton2(AllModulesRow,
	                                    ' r ',
	                                    'Reset All Set Keys')	
		
		mc.formLayout(AllModulesRow, edit = True,
	                  af = [(tmpActive, "left", 10),
	                        (tmpReset,"right",10)],
	                  ac = [(tmpSel,"left",0,tmpActive),
	                        (self.ModuleModeOptionMenu,"left",4,tmpSel),
	                        (self.ModuleModeOptionMenu,"right",4,tmpKey),
	                        (tmpKey,"right",2,tmpDeleteKey),
		                    (tmpDeleteKey,"right",2,tmpReset)
		                    ])
		
		#>>> Sets building section
		allPopUpMenu = MelPopupMenu(self.ModuleModeOptionMenu ,button = 3)
		
		allCategoryMenu = MelMenuItem(allPopUpMenu,
	                               label = 'Make Type:',
	                               sm = True)

			
		
		
		#>>> Sets building section
		ModuleListScroll = MelScrollLayout(MainForm,cr = 1, ut = 'cgmUISubTemplate')
		ModuleMasterForm = MelFormLayout(ModuleListScroll)
		self.ModuleListColumn = MelColumnLayout(ModuleMasterForm, adj = True, rowSpacing = 3)
		
		
		
		#self.ModulesBuffer.bufferList
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# Modules
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>	
		"""
		self.modulesDict = {}
		self.activeModulesCBDict = {}		
		
		if self.puppetInstance:	
			print '>>>>>>>>>>>>>>>>>>>>>>>>>yes'
			for i,b in enumerate(self.puppetInstance.ModulesBuffer.bufferList):
				#Store the info to a dict
				self.modulesDict[i] = b
				#s = SetFactory(b)
				
				#tmpSetRow = MelFormLayout(self.ModuleListColumn,height = 20)
				MelLabel(self.ModuleListColumn,l=b)
				#Get check box state
				activeState = False
				if b in self.ActiveObjectSetsOptionVar.value:
					activeState = True
				
				tmpActive = MelCheckBox(tmpSetRow,
					                    annotation = 'Set Module as active',
					                    value = activeState,
					                    onCommand =  Callback(setToolsLib.doSetSetAsActive,self,i),
					                    offCommand = Callback(setToolsLib.doSetSetAsInactive,self,i))
				self.activeModulesCBDict[i] = tmpActive
				
				tmpSel = guiFactory.doButton2(tmpSetRow,
					                          ' s ',
					                          Callback(setToolsLib.doSelectSetObjects,self,i),
					                          'Select the set objects')
					
	
				tmpName = MelTextField(tmpSetRow, w = 100,ut = 'cgmUIReservedTemplate', text = b,
					                   en = not s.refState)
				
				tmpName(edit = True,
					    ec = Callback(setToolsLib.doUpdateSetName,self,tmpName,i)	)
				
	
				tmpAdd = guiFactory.doButton2(tmpSetRow,
					                           '+',
					                           Callback(setToolsLib.doAddSelected,self,i),
					                           'Add selected  to the set',
					                           en = not s.refState)
				tmpRem= guiFactory.doButton2(tmpSetRow,
					                         '-',
					                         Callback(setToolsLib.doRemoveSelected,self,i),
					                         'Remove selected  to the set',
					                         en = not s.refState)
				tmpKey = guiFactory.doButton2(tmpSetRow,
					                          'k',
					                          Callback(setToolsLib.doKeySet,self,i),			                              
					                          'Key set')
				tmpDeleteKey = guiFactory.doButton2(tmpSetRow,
					                            'd',
					                            Callback(setToolsLib.doDeleteCurrentSetKey,self,i),			                              			                                
					                            'delete set key')	
				
				tmpReset = guiFactory.doButton2(tmpSetRow,
					                            'r',
					                            Callback(setToolsLib.doResetSet,self,i),			                              			                                
					                            'Reset Set')
				mc.formLayout(tmpSetRow, edit = True,
					          af = [(tmpActive, "left", 4),
					                (tmpReset,"right",2)],
					          ac = [(tmpSel,"left",0,tmpActive),
					                (tmpName,"left",2,tmpSel),
					                (tmpName,"right",4,tmpAdd),
					                (tmpAdd,"right",2,tmpRem),
					                (tmpRem,"right",2,tmpKey),
					                (tmpKey,"right",2,tmpDeleteKey),
					                (tmpDeleteKey,"right",2,tmpReset)
					                ])"""
		
		
		
		self.helpInfo = MelLabel(MainForm,
		                         h=20,
		                         l = "Add a Puppet",
		                         ut = 'cgmUIInstructionsTemplate',
		                         al = 'center',
		                         ww = True,vis = self.ShowHelpOptionVar.value)
		self.helpBlurbs.extend([self.helpInfo ])
		
		VerifyRow = guiFactory.doButton2(MainForm,
		                                'Check Puppet',
		                                'Create new buffer from selected buffer')	
			
		ModuleMasterForm(edit = True,
		                 af = [(self.ModuleListColumn,"top",0),
		                       (self.ModuleListColumn,"left",0),
		                       (self.ModuleListColumn,"right",0),
		                       (self.ModuleListColumn,"bottom",0)])
		
		
	
		
		
		
		MainForm(edit = True,
		         af = [(TopSection,"top",0),	
		               (TopSection,"left",0),
		               (TopSection,"right",0),		               
		               (AllModulesRow,"left",0),
		               (AllModulesRow,"right",0),
		               (ModuleListScroll,"left",0),
		               (ModuleListScroll,"right",0),
		               (ModuleListScroll,"left",0),
		               (ModuleListScroll,"right",0),				       
		               (self.helpInfo,"left",8),
		               (self.helpInfo,"right",8),
		               (VerifyRow,"left",4),
		               (VerifyRow,"right",4),		               
		               (VerifyRow,"bottom",4)],
		         ac = [(AllModulesRow,"top",2,TopSection),
		               (ModuleListScroll,"top",2,AllModulesRow),
		               (ModuleListScroll,"bottom",0,self.helpInfo),
		               (self.helpInfo,"bottom",0,VerifyRow)],
		         attachNone = [(VerifyRow,"top")])	
		

