#=================================================================================================================================================
#=================================================================================================================================================
#	attrTools - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Gui Tool for attribute tools
#
# ARGUMENTS:
#   Maya
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
#
#=================================================================================================================================================
__version__ = '0.2.10162012'

from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.lib.classes.OptionVarFactory import *

import maya.cmds as mc
import maya.mel as mel

from cgm.lib import (guiFactory,
                     dictionary,
                     search)

from cgm.tools.lib import (tdToolsLib,
                           locinatorLib,
                           attrToolsLib)

#reload(tdToolsLib)
#reload(attrToolsLib)
#reload(guiFactory)

def run():
	cgmAttrToolsWin = attrToolsClass()

class attrToolsClass(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_Template = 'cgmUITemplate'
	
	WINDOW_NAME = 'attrTools'
	WINDOW_TITLE = 'cgm.attrTools - %s'%__version__
	DEFAULT_SIZE = 375, 350
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created

	def __init__( self):	

		# Basic variables
		self.window = ''
		self.activeTab = ''
		self.toolName = 'attrTools'
		self.module = 'tdTools'
		self.winName = 'attrToolsWin'
		self.optionVars = []

		self.showHelp = False
		self.helpBlurbs = []
		self.oldGenBlurbs = []

		self.showTimeSubMenu = False
		self.timeSubMenu = []
		
		self.setupVariables()
		self.loadAttrs = []

		# About Window
		self.description = 'Tools for working with attributes'
		self.author = 'Josh Burton'
		self.owner = 'CG Monks'
		self.website = 'www.cgmonks.com'
		self.version = __version__

		# About Window

		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# Build
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

		#Menu
		self.UI_OptionsMenu = MelMenu( l='Options', pmc=self.buildOptionsMenu)
		self.UI_HelpMenu = MelMenu( l='Help', pmc=self.buildHelpMenu)
		

		WindowForm = MelColumnLayout(self)
		           
		self.buildAttributeTool(WindowForm)
		
		if mc.ls(sl=True):
			attrToolsLib.uiLoadSourceObject(self)
		
		self.show()


	def setupVariables(self):
		self.SortModifyOptionVar = OptionVarFactory('cgmVar_attrToolsSortModfiy', defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.SortModifyOptionVar.name)
		
		self.HideTransformsOptionVar = OptionVarFactory('cgmVar_attrToolsHideTransform', defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.HideTransformsOptionVar.name)
		
		self.HideUserDefinedOptionVar = OptionVarFactory('cgmVar_attrToolsHideUserDefined', defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.HideUserDefinedOptionVar.name)		
		
		self.HideParentAttrsOptionVar = OptionVarFactory('cgmVar_attrToolsHideParentAttrs', defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.HideParentAttrsOptionVar.name)
		
		self.HideCGMAttrsOptionVar = OptionVarFactory('cgmVar_attrToolsHideCGMAttrs', defaultValue = 1)
		guiFactory.appendOptionVarList(self,self.HideCGMAttrsOptionVar.name)
		
		self.HideNonstandardOptionVar = OptionVarFactory('cgmVar_attrToolsHideNonStandard', defaultValue = 1)
		guiFactory.appendOptionVarList(self,self.HideNonstandardOptionVar.name)			

		self.ShowHelpOptionVar = OptionVarFactory('cgmVar_attrToolsShowHelp', defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.ShowHelpOptionVar.name)
		
		self.SourceObjectOptionVar = OptionVarFactory('cgmVar_AttributeSourceObject', defaultValue= '')
		guiFactory.appendOptionVarList(self,self.SourceObjectOptionVar.name)
		
		self.CopyAttrModeOptionVar = OptionVarFactory('cgmVar_CopyAttributeMode', defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.CopyAttrModeOptionVar.name)	
		
		self.CopyAttrOptionsOptionVar = OptionVarFactory('cgmVar_CopyAttributeOptions', defaultValue = 1)
		guiFactory.appendOptionVarList(self,self.CopyAttrOptionsOptionVar.name)	
		
		self.TransferValueOptionVar = OptionVarFactory('cgmVar_AttributeTransferValueState', defaultValue = 1)
		guiFactory.appendOptionVarList(self,self.TransferValueOptionVar.name)	
		
		self.TransferIncomingOptionVar = OptionVarFactory('cgmVar_AttributeTransferInConnectionState', defaultValue = 1)
		guiFactory.appendOptionVarList(self,self.TransferIncomingOptionVar.name)		
		
		self.TransferOutgoingOptionVar = OptionVarFactory('cgmVar_AttributeTransferOutConnectionState', defaultValue = 1)
		guiFactory.appendOptionVarList(self,self.TransferOutgoingOptionVar.name)	
		
		self.TransferKeepSourceOptionVar = OptionVarFactory('cgmVar_AttributeTransferKeepSourceState', defaultValue = 1)
		guiFactory.appendOptionVarList(self,self.TransferKeepSourceOptionVar.name)	
		
		self.TransferConvertStateOptionVar = OptionVarFactory('cgmVar_AttributeTransferConvertState', defaultValue = 1)
		guiFactory.appendOptionVarList(self,self.TransferConvertStateOptionVar.name)
		
		self.TransferDriveSourceStateOptionVar = OptionVarFactory('cgmVar_AttributeTransferConnectToSourceState', defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.TransferDriveSourceStateOptionVar.name)	
		
		self.CreateAttrTypeOptionVar = OptionVarFactory('cgmVar_AttrCreateType',defaultValue='')
		guiFactory.appendOptionVarList(self,self.CreateAttrTypeOptionVar.name)	
		
		self.DebugModeOptionVar = OptionVarFactory('cgmVar_AttrToolsDebug',defaultValue=0)
		guiFactory.appendOptionVarList(self,self.DebugModeOptionVar.name)			
		
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Menus
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildHelpMenu(self, *a ):
		self.UI_HelpMenu.clear()		
		MelMenuItem( self.UI_HelpMenu, l="Print Tools Help",
				     c=lambda *a: self.printHelp() )
		MelMenuItem( self.UI_HelpMenu, l="About",
				     c=lambda *a: self.showAbout() )
		MelMenuItemDiv( self.UI_HelpMenu )
		
		MelMenuItem( self.UI_HelpMenu, l="Debug",
				     cb=self.DebugModeOptionVar.value,
				     c= lambda *a: self.DebugModeOptionVar.toggle())		
		
	def buildOptionsMenu( self, *a ):
		self.UI_OptionsMenu.clear()
		
		#>>> Grouping Options
		HidingMenu = MelMenuItem( self.UI_OptionsMenu, l='Autohide:', subMenu=True)
		MelMenuItem( self.UI_OptionsMenu, l="Sort Modify",
			         cb=self.SortModifyOptionVar.value,
		             annotation = "Sort the list of attributes in/nthe modify section alphabetically",
		             c = lambda *a: attrToolsLib.uiToggleOptionCB(self,self.SortModifyOptionVar))	
		
		#guiFactory.appendOptionVarList(self,'cgmVar_MaintainLocalSetGroup')			
		MelMenuItem( HidingMenu, l="Transforms",
	                 cb= self.HideTransformsOptionVar.value,
	                 c= lambda *a: attrToolsLib.uiToggleOptionCB(self,self.HideTransformsOptionVar))
		
		MelMenuItem( HidingMenu, l="User Defined",
	                 cb= self.HideUserDefinedOptionVar.value,
	                 c= lambda *a: attrToolsLib.uiToggleOptionCB(self,self.HideUserDefinedOptionVar))		
		
		MelMenuItem( HidingMenu, l="Parent Attributes",
	                 cb= self.HideParentAttrsOptionVar.value,
	                 c= lambda *a: attrToolsLib.uiToggleOptionCB(self,self.HideParentAttrsOptionVar))
		
		MelMenuItem( HidingMenu, l="CGM Attributes",
	                 cb= self.HideCGMAttrsOptionVar.value,
	                 c= lambda *a: attrToolsLib.uiToggleOptionCB(self,self.HideCGMAttrsOptionVar))		
		
		MelMenuItem( HidingMenu, l="Nonstandard",
	                 cb= self.HideNonstandardOptionVar.value,
	                 c= lambda *a: attrToolsLib.uiToggleOptionCB(self,self.HideNonstandardOptionVar))
		
		
		#>>> Reset Options		
		MelMenuItemDiv( self.UI_OptionsMenu )
		MelMenuItem( self.UI_OptionsMenu, l="Reload",
			         c=lambda *a: self.reload())		
		MelMenuItem( self.UI_OptionsMenu, l="Reset",
			         c=lambda *a: self.reset())
		

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
		guiFactory.doButton('Visit Website', 'import webbrowser;webbrowser.open("http://www.cgmonks.com/tools/maya-tools/attrtools/")')
		guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
		mc.setParent( '..' )
		mc.showWindow( window )

	def printHelp(self):
		from cgm.tools.lib import attrToolsLib
		help(attrToolsLib)

	def reset(self):	
		Callback(guiFactory.resetGuiInstanceOptionVars(self.optionVars,run))
		
	def reload(self):	
		run()
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Tools
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildAttributeTool(self,parent,vis=True):
		OptionList = ['Tools','Manager','Utilities']
		RadioCollectionName ='AttributeMode'
		RadioOptionList = 'AttributeModeSelectionChoicesList'

		ShowHelpOption = mc.optionVar( q='cgmVar_TDToolsShowHelp' )
		
		self.AttributeModeOptionVar = OptionVarFactory( 'cgmVar_AttributeMode',defaultValue = OptionList[0])
		
		MelSeparator(parent,ut = 'cgmUIHeaderTemplate',h=5)
		
		#Mode Change row 
		self.ModeSetRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 0)
		MelLabel(self.ModeSetRow, label = 'Choose Mode: ',align='right')
		self.RadioCollectionName = MelRadioCollection()
		self.RadioOptionList = []		

		#build our sub section options
		self.ContainerList = []

		self.ContainerList.append( self.buildAttributeEditingTool(parent,vis=False) )
		self.ContainerList.append( self.buildAttributeManagerTool( parent,vis=False) )
		self.ContainerList.append( self.buildAttributeUtilitiesTool( parent,vis=False) )
		
		for item in OptionList:
			self.RadioOptionList.append(self.RadioCollectionName.createButton(self.ModeSetRow,label=item,
						                                                      onCommand = Callback(guiFactory.toggleModeState,item,OptionList,self.AttributeModeOptionVar.name,self.ContainerList)))
		self.ModeSetRow.layout()


		mc.radioCollection(self.RadioCollectionName,edit=True, sl=self.RadioOptionList[OptionList.index(self.AttributeModeOptionVar.value)])

		
	def buildAttributeEditingTool(self,parent, vis=True):
		#Container
		containerName = 'Attributes Constainer'
		self.containerName = MelColumn(parent,vis=vis)
		
		###Create
		mc.setParent(self.containerName)
		guiFactory.header('Create')
		guiFactory.lineSubBreak()
		
		#>>>Create Row
		attrCreateRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5)
		MelSpacer(attrCreateRow)

		MelLabel(attrCreateRow,l='Names:',align='right')
		self.AttrNamesTextField = MelTextField(attrCreateRow,backgroundColor = [1,1,1],h=20,
		                                       ec = lambda *a: attrToolsLib.doAddAttributesToSelected(self),
		                                       annotation = "Names for the attributes. Create multiple with a ';'. \n Message nodes try to connect to the last object in a selection \n For example: 'Test1;Test2;Test3'")
		guiFactory.doButton2(attrCreateRow,'Add',
		                     lambda *a: attrToolsLib.doAddAttributesToSelected(self),
		                     "Add the attribute names from the text field")
		MelSpacer(attrCreateRow,w=2)

		attrCreateRow.setStretchWidget(self.AttrNamesTextField)
		attrCreateRow.layout()
		
		
		#>>> modify Section
		self.buildAttrTypeRow(self.containerName)
		MelSeparator(self.containerName,ut = 'cgmUIHeaderTemplate',h=2)
		MelSeparator(self.containerName,ut = 'cgmUITemplate',h=10)
		
		###Modify
		mc.setParent(self.containerName)
		guiFactory.header('Modify')

		
		AttrReportRow = MelHLayout(self.containerName ,ut='cgmUIInstructionsTemplate',h=20)
		self.AttrReportField = MelLabel(AttrReportRow,
		                                bgc = dictionary.returnStateColor('help'),
		                                align = 'center',
		                                label = '...',
		                                h=20)
		AttrReportRow.layout()
			
		MelSeparator(self.containerName,ut = 'cgmUISubTemplate',h=5)
		
		#>>> Load To Field
		LoadAttributeObjectRow = MelHSingleStretchLayout(self.containerName ,ut='cgmUISubTemplate',padding = 5)
	
		MelSpacer(LoadAttributeObjectRow,w=5)
		
		guiFactory.doButton2(LoadAttributeObjectRow,'>>',
	                        lambda *a:attrToolsLib.uiLoadSourceObject(self),
	                         'Load to field')
		
		self.SourceObjectField = MelTextField(LoadAttributeObjectRow, w= 125, h=20, ut = 'cgmUIReservedTemplate', editable = False)
	
		LoadAttributeObjectRow.setStretchWidget(self.SourceObjectField  )
		
		MelLabel(LoadAttributeObjectRow, l=' . ')
		self.ObjectAttributesOptionMenu = MelOptionMenu(LoadAttributeObjectRow, w = 100)
	
		self.DeleteAttrButton = guiFactory.doButton2(LoadAttributeObjectRow,'X',
		                                             lambda *a:attrToolsLib.uiDeleteAttr(self,self.ObjectAttributesOptionMenu),
		                                             'Delete attribute',
		                                             w = 25,
		                                             en = False)
	
		MelSpacer(LoadAttributeObjectRow,w=5)
	
		LoadAttributeObjectRow.layout()
		
	
		#>>> Standard Flags
		BasicAttrFlagsRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
		MelSpacer(BasicAttrFlagsRow,w=5)
		self.KeyableAttrCB = MelCheckBox(BasicAttrFlagsRow,label = 'Keyable',en=False)
		MelSpacer(BasicAttrFlagsRow,w=5)
		self.HiddenAttrCB = MelCheckBox(BasicAttrFlagsRow,label = 'Hidden',en=False)
		MelSpacer(BasicAttrFlagsRow,w=5)
		self.LockedAttrCB = MelCheckBox(BasicAttrFlagsRow,label = 'Locked',en=False)
		MelSpacer(BasicAttrFlagsRow,w=5)
		BasicAttrFlagsRow.layout()
		
		
		#>>> Name Row
		self.EditNameSettingsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate')
		self.EditNameSettingsRow.setStretchWidget(MelSpacer(self.EditNameSettingsRow,w=5))
		
		NameLabel = MelLabel(self.EditNameSettingsRow,label = 'Name: ')
		self.NameField = MelTextField(self.EditNameSettingsRow,en = False,
		                              bgc = dictionary.returnStateColor('normal'),
		                              ec = lambda *a: attrToolsLib.uiRenameAttr(self),
		                              h=20,
		                              w = 75)

		NiceNameLabel = MelLabel(self.EditNameSettingsRow,label = 'Nice: ')		
		self.NiceNameField = MelTextField(self.EditNameSettingsRow,en = False,
		                             bgc = dictionary.returnStateColor('normal'),
		                             ec = lambda *a: attrToolsLib.uiUpdateNiceName(self),		                             
		                             h=20,
		                             w = 75)
		AliasLabel = MelLabel(self.EditNameSettingsRow,label = 'Alias: ')		
		self.AliasField = MelTextField(self.EditNameSettingsRow,en = False,
		                                 bgc = dictionary.returnStateColor('normal'),
		                                 ec = lambda *a: attrToolsLib.uiUpdateAlias(self),		                                 
		                                 h=20,
		                                 w = 75)
		MelSpacer(self.EditNameSettingsRow,w=5)
		self.EditNameSettingsRow.layout()
		"""mc.formLayout(self.EditNameSettingsRow, edit = True,
	                  af = [(NameLabel, "left", 5),
	                        (self.AliasField,"right",5)],
	                  ac = [(self.NameField,"left",2,NameLabel),
	                        (NiceNameLabel,"left",2,self.NameField),
	                        (self.NiceNameField,"left",2,NiceNameLabel),
	                        (AliasLabel,"left",2,self.NiceNameField),
		                    (self.AliasField,"left",2,AliasLabel),
		                    ])"""
		
		#>>> Int Row
		#self.EditDigitSettingsRow = MelFormLayout(self.containerName,ut='cgmUISubTemplate',vis = False)
		self.EditDigitSettingsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',vis = False)
		self.EditDigitSettingsRow.setStretchWidget(MelSpacer(self.EditDigitSettingsRow,w=5))
		MinLabel = MelLabel(self.EditDigitSettingsRow,label = 'Min:')
		self.MinField = MelTextField(self.EditDigitSettingsRow,
		                             bgc = dictionary.returnStateColor('normal'),
		                             ec = lambda *a: attrToolsLib.uiUpdateMinValue(self),
		                             h = 20, w = 35)
		
		MaxLabel = MelLabel(self.EditDigitSettingsRow,label = 'Max:')		
		self.MaxField = MelTextField(self.EditDigitSettingsRow,
		                             bgc = dictionary.returnStateColor('normal'),
		                             ec = lambda *a: attrToolsLib.uiUpdateMaxValue(self),	
		                             h = 20, w = 35)
		
		DefaultLabel = MelLabel(self.EditDigitSettingsRow,label = 'dv:')		
		self.DefaultField = MelTextField(self.EditDigitSettingsRow,
		                                 bgc = dictionary.returnStateColor('normal'),
		                                 ec = lambda *a: attrToolsLib.uiUpdateDefaultValue(self),	
		                                 h = 20, w = 35)
		SoftMinLabel = MelLabel(self.EditDigitSettingsRow,label = 'sMin:')				
		self.SoftMinField = MelTextField(self.EditDigitSettingsRow,
		                                 bgc = dictionary.returnStateColor('normal'),
		                                 ec = lambda *a: attrToolsLib.uiUpdateSoftMinValue(self),	
		                                 h = 20, w = 35)
		
		SoftMaxLabel = MelLabel(self.EditDigitSettingsRow,label = 'sMax:')				
		self.SoftMaxField = MelTextField(self.EditDigitSettingsRow,
		                                 bgc = dictionary.returnStateColor('normal'),
		                                 ec = lambda *a: attrToolsLib.uiUpdateSoftMaxValue(self),	
		                                 h = 20, w = 35)
		
		MelSpacer(self.EditDigitSettingsRow,w=5)
		self.EditDigitSettingsRow.layout()
		
		"""mc.formLayout(self.EditDigitSettingsRow, edit = True,
	                  af = [(MinLabel, "left", 20),
	                        (self.SoftMinField,"right",20)],
	                  ac = [(self.MinField,"left",2,MinLabel),
	                        (MaxLabel,"left",2,self.MinField),
	                        (self.MaxField,"left",2,MaxLabel),
	                        (DefaultLabel,"left",2,self.MaxField),
		                    (self.DefaultField,"left",2,DefaultLabel),
		                    (SoftMaxLabel,"left",2,self.DefaultField),
		                    (self.SoftMaxField,"left",2,SoftMaxLabel),
		                    (SoftMinLabel,"left",2,self.SoftMaxField),		                    		                    
		                    (self.SoftMinField,"left",2,SoftMinLabel)		                    
		                    ])"""
		
		#>>> Enum
		self.EditEnumRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5, vis = False)
		MelSpacer(self.EditEnumRow,w=10)
		MelLabel(self.EditEnumRow,label = 'Enum: ')
		self.EnumField = MelTextField(self.EditEnumRow,
				                      annotation = "Options divided by ':'. \n Set values with '=' \n For example: 'off:on=1:maybe=23'",
		                              bgc = dictionary.returnStateColor('normal'),
		                              h = 20, w = 75)
		MelSpacer(self.EditEnumRow,w=10)
		self.EditEnumRow.setStretchWidget(self.EnumField)
		
		self.EditEnumRow.layout()
		
		#>>> String
		self.EditStringRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5, vis = False)
		MelSpacer(self.EditStringRow,w=10)
		MelLabel(self.EditStringRow,label = 'String: ')
		self.StringField = MelTextField(self.EditStringRow,
		                                h=20,
		                                bgc = dictionary.returnStateColor('normal'),
		                                w = 75)
		MelSpacer(self.EditStringRow,w=10)
		self.EditStringRow.setStretchWidget(self.StringField)
		
		self.EditStringRow.layout()
		
		#>>> Message
		self.EditMessageRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5, vis = False)
		MelSpacer(self.EditMessageRow,w=10)
		MelLabel(self.EditMessageRow,label = 'Message: ')
		self.MessageField = MelTextField(self.EditMessageRow,
		                                 h=20,
		                                 enable = False,
		                                 bgc = dictionary.returnStateColor('locked'),
		                                 ec = lambda *a: tdToolsLib.uiUpdateAutoNameTag(self,'cgmPosition'),
		                                 w = 75)
		self.LoadMessageButton = guiFactory.doButton2(self.EditMessageRow,'<<',
		                                              lambda *a:attrToolsLib.uiUpdateMessage(self),
		                                              'Load to message')
		MelSpacer(self.EditMessageRow,w=10)
		self.EditMessageRow.setStretchWidget(self.MessageField)

		self.EditMessageRow.layout()
		
		#>>> Conversion
		self.buildAttrConversionRow(self.containerName)
		self.AttrConvertRow(e=True, vis = False)
		


		#>>> Connect Report
		self.ConnectionReportRow = MelHLayout(self.containerName ,ut='cgmUIInstructionsTemplate',h=20,vis=False)
		self.ConnectionReportField = MelLabel(self.ConnectionReportRow,vis=False,
		                                bgc = dictionary.returnStateColor('help'),
		                                align = 'center',
		                                label = '...',
		                                h=20)	
		self.ConnectionReportRow.layout()	
		
		self.ConnectedPopUpMenu = MelPopupMenu(self.ConnectionReportRow,button = 3)
		
		MelSeparator(self.containerName,ut = 'cgmUIHeaderTemplate',h=2)
		
		mc.setParent(self.containerName )
		guiFactory.lineBreak()
		
		return self.containerName
	
	def buildAttrTypeRow(self,parent):	
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# Attr type row
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		self.attrTypes = ['string','float','int','double3','bool','enum','message']
		attrShortTypes = ['str','float','int','[000]','bool','enum','msg']

		self.CreateAttrTypeRadioCollection = MelRadioCollection()
		self.CreateAttrTypeRadioCollectionChoices = []		
			
		#build our sub section options
		AttrTypeRow = MelHLayout(self.containerName,ut='cgmUISubTemplate',padding = 5)
		for cnt,item in enumerate(self.attrTypes):
			self.CreateAttrTypeRadioCollectionChoices.append(self.CreateAttrTypeRadioCollection.createButton(AttrTypeRow,label=attrShortTypes[cnt],
			                                                                                                 onCommand = Callback(self.CreateAttrTypeOptionVar.set,item)))
			MelSpacer(AttrTypeRow,w=2)
		
		if self.CreateAttrTypeOptionVar.value:
			mc.radioCollection(self.CreateAttrTypeRadioCollection ,edit=True,sl= (self.CreateAttrTypeRadioCollectionChoices[ self.attrTypes.index(self.CreateAttrTypeOptionVar.value) ]))
		
		AttrTypeRow.layout()
		
	def buildAttrConversionRow(self,parent):	
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# Attr type row
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		self.attrConvertTypes = ['string','float','int','bool','enum','message']
		self.attrConvertShortTypes = ['str','float','int','bool','enum','msg']

		self.ConvertAttrTypeRadioCollection = MelRadioCollection()
		self.ConvertAttrTypeRadioCollectionChoices = []	
		
		self.ConvertAttrTypeOptionVar = OptionVarFactory('cgmVar_ActiveAttrConversionState','int')
		guiFactory.appendOptionVarList(self,self.ConvertAttrTypeOptionVar.name)
		self.ConvertAttrTypeOptionVar.set(0)
			
		#build our sub section options
		self.AttrConvertRow = MelHLayout(self.containerName,ut='cgmUISubTemplate',padding = 5)
		for cnt,item in enumerate(self.attrConvertTypes):
			self.ConvertAttrTypeRadioCollectionChoices.append(self.ConvertAttrTypeRadioCollection.createButton(self.AttrConvertRow,label=self.attrConvertShortTypes[cnt],
			                                                                                                   onCommand = Callback(attrToolsLib.uiConvertLoadedAttr,self,item)))
			MelSpacer(self.AttrConvertRow,w=2)

		self.AttrConvertRow.layout()

		
	def buildAttributeManagerTool(self,parent, vis=True):
		self.ManageForm = MelFormLayout(self.Get(),ut='cgmUITemplate')
		
		ManageHeader = guiFactory.header('Manage Attributes')

		#>>> Manager load frow
		ManagerLoadObjectRow = MelHSingleStretchLayout(self.ManageForm ,padding = 5)
	
		MelSpacer(ManagerLoadObjectRow,w=5)
		
		guiFactory.doButton2(ManagerLoadObjectRow,'>>',
	                        lambda *a:attrToolsLib.uiLoadSourceObject(self),
	                         'Load to field')
		
		self.ManagerSourceObjectField = MelTextField(ManagerLoadObjectRow, w= 125, h=20, ut = 'cgmUIReservedTemplate', editable = False)
	
		ManagerLoadObjectRow.setStretchWidget(self.ManagerSourceObjectField  )
		
	
		MelSpacer(ManagerLoadObjectRow,w=5)
	
		ManagerLoadObjectRow.layout()


		#>>> Attribute List
		self.ManageAttrList = MelObjectScrollList(self.ManageForm, allowMultiSelection=True )
		
		#>>> Reorder Button
		ReorderButtonsRow = MelHLayout(self.ManageForm,padding = 5)
		guiFactory.doButton2(ReorderButtonsRow,
		                     'Move Up',
		                     lambda *a: attrToolsLib.uiReorderAttributes(self,0),
		                     'Create new buffer from selected buffer')	
		guiFactory.doButton2(ReorderButtonsRow,
		                     'Move Down',
		                     lambda *a: attrToolsLib.uiReorderAttributes(self,1),
		                     'Create new buffer from selected buffer')	
		ReorderButtonsRow.layout()





		#>>>Transfer Options
		self.TransferModeCollection = MelRadioCollection()
		self.TransferModeCollectionChoices = []	
		
		TransferModeFlagsRow = MelHSingleStretchLayout(self.ManageForm,padding = 2)	
		MelLabel(TransferModeFlagsRow,l='Modes')
		Spacer = MelSeparator(TransferModeFlagsRow,w=10)						
		self.TransferModeOptions = ['Connect','Copy','Transfer']
		for i,item in enumerate(self.TransferModeOptions):
			self.TransferModeCollectionChoices.append(self.TransferModeCollection.createButton(TransferModeFlagsRow,label=item,
			                                                                             onCommand = Callback(self.CopyAttrModeOptionVar.set,i)))
			MelSpacer(TransferModeFlagsRow,w=3)
		TransferModeFlagsRow.setStretchWidget( Spacer )
		MelSpacer(TransferModeFlagsRow,w=2)		
		TransferModeFlagsRow.layout()	
		
		mc.radioCollection(self.TransferModeCollection ,edit=True,sl= (self.TransferModeCollectionChoices[ (self.CopyAttrModeOptionVar.value) ]))
		
		
		#>>>Transfer Options
		self.TransferOptionsCollection = MelRadioCollection()
		self.TransferOptionsCollectionChoices = []	
		
		TransferOptionsFlagsRow = MelHSingleStretchLayout(self.ManageForm,padding = 0)	
		Spacer = MelSpacer(TransferOptionsFlagsRow)						
		TransferOptionsFlagsRow.setStretchWidget( Spacer )
		
		self.ConvertCB = MelCheckBox(TransferOptionsFlagsRow,label = 'Convert',
				                           annotation = "Converts if necessary to finish the copy process",		                           
				                           value = self.TransferConvertStateOptionVar.value,
				                           onCommand = Callback(self.TransferConvertStateOptionVar.set,1),
				                           offCommand = Callback(self.TransferConvertStateOptionVar.set,0))

		self.ValueCB = MelCheckBox(TransferOptionsFlagsRow,label = 'Value',
		                           annotation = "Copy values",		                           
		                           value = self.TransferValueOptionVar.value,
		                           onCommand = Callback(self.TransferValueOptionVar.set,1),
		                           offCommand = Callback(self.TransferValueOptionVar.set,0))
		
		self.IncomingCB = MelCheckBox(TransferOptionsFlagsRow,label = 'In',
				                      annotation = "Copy or transfer incoming connections",		                              
		                              value = self.TransferIncomingOptionVar.value,
		                              onCommand = Callback(self.TransferIncomingOptionVar.set,1),
		                              offCommand = Callback(self.TransferIncomingOptionVar.set,0))

		self.OutgoingCB = MelCheckBox(TransferOptionsFlagsRow,label = 'Out',
		                              annotation = "Copy or transfer incoming connections",		                              
		                              value = self.TransferOutgoingOptionVar.value,
		                              onCommand = Callback(self.TransferOutgoingOptionVar.set,1),
		                              offCommand = Callback(self.TransferOutgoingOptionVar.set,0))	

		self.KeepSourceCB = MelCheckBox(TransferOptionsFlagsRow,label = 'Keep',
		                                annotation = "Keep source connections when copying",		                                
		                                value = self.TransferKeepSourceOptionVar.value,
		                                onCommand = Callback(self.TransferKeepSourceOptionVar.set,1),
		                                offCommand = Callback(self.TransferKeepSourceOptionVar.set,0))
		
		self.DriveSourceCB = MelCheckBox(TransferOptionsFlagsRow,label = 'Drive',
		                                annotation = "Connect the source attr \nto selected or created attribute",		                                
		                                value = self.TransferDriveSourceStateOptionVar.value,
		                                onCommand = Callback(self.TransferDriveSourceStateOptionVar.set,1),
		                                offCommand = Callback(self.TransferDriveSourceStateOptionVar.set,0))
		
		self.AttrOptionsCB = MelCheckBox(TransferOptionsFlagsRow,label = 'Options',
		                                annotation = "Copies the attributes basic flags\n(locked,keyable,hidden)",		                                
		                                value = self.CopyAttrOptionsOptionVar.value,
		                                onCommand = Callback(self.CopyAttrOptionsOptionVar.set,1),
		                                offCommand = Callback(self.TransferDriveSourceStateOptionVar.set,0))
		
		TransferOptionsFlagsRow.layout()	


		BottomButtonRow = guiFactory.doButton2(self.ManageForm,
		                                       'Connect/Copy/Transfer',
		                                       lambda *a: attrToolsLib.uiTransferAttributes(self),
		                                       'Create new buffer from selected buffer')	

		self.ManageForm(edit = True,
		         af = [(ManageHeader,"top",0),
		               (ManageHeader,"left",0),
		               (ManageHeader,"right",0),
		               (self.ManageAttrList,"left",0),
		               (self.ManageAttrList,"right",0),
		               (ManagerLoadObjectRow,"left",5),
		               (ManagerLoadObjectRow,"right",5),
		               (ReorderButtonsRow,"left",0),
		               (ReorderButtonsRow,"right",0),	
		               (TransferModeFlagsRow,"left",5),
		               (TransferModeFlagsRow,"right",5),
		               (BottomButtonRow,"left",5),
		               (BottomButtonRow,"right",5),		               
		               (TransferOptionsFlagsRow,"left",2),
		               (TransferOptionsFlagsRow,"right",2),
		               (TransferOptionsFlagsRow,"bottom",4)],
		         ac = [(ManagerLoadObjectRow,"top",5,ManageHeader),
		               (self.ManageAttrList,"top",5,ManagerLoadObjectRow),
		               (self.ManageAttrList,"bottom",5,ReorderButtonsRow),
		               (ReorderButtonsRow,"bottom",5,BottomButtonRow),		               
		               (BottomButtonRow,"bottom",5,TransferModeFlagsRow),
		               (TransferModeFlagsRow,"bottom",5,TransferOptionsFlagsRow)],
		         attachNone = [(TransferOptionsFlagsRow,"top")])	
		



		#Build pop up for attribute list field
		popUpMenu = MelPopupMenu(self.ManageAttrList,button = 3)
				
			
		MelMenuItem(popUpMenu ,
	                label = 'Make Keyable',
	                c = lambda *a: attrToolsLib.uiManageAttrsKeyable(self))
		
		MelMenuItem(popUpMenu ,
	                label = 'Make Unkeyable',
		            c = lambda *a: attrToolsLib.uiManageAttrsUnkeyable(self))
		
		MelMenuItemDiv(popUpMenu)
		
		MelMenuItem(popUpMenu ,
	                label = 'Hide',
		            c = lambda *a: attrToolsLib.uiManageAttrsHide(self))
		
		MelMenuItem(popUpMenu ,
	                label = 'Unhide',
		            c = lambda *a: attrToolsLib.uiManageAttrsUnhide(self))
		
		MelMenuItemDiv(popUpMenu)
		MelMenuItem(popUpMenu ,
	                label = 'Lock',
		            c = lambda *a: attrToolsLib.uiManageAttrsLocked(self))
		
		MelMenuItem(popUpMenu ,
	                label = 'Unlock',
		            c = lambda *a: attrToolsLib.uiManageAttrsUnlocked(self))
		
		MelMenuItemDiv(popUpMenu)
		MelMenuItem(popUpMenu ,
	                label = 'Delete',
		            c = lambda *a: attrToolsLib.uiManageAttrsDelete(self))


		return self.ManageForm
	

	
	def buildAttributeUtilitiesTool(self,parent, vis=True):
		containerName = 'Utilities Container'
		self.containerName = MelColumn(parent,vis=vis)

		#>>> Tag Labels
		mc.setParent(self.containerName)
		guiFactory.header('Short cuts')
		guiFactory.lineSubBreak()
		
		AttributeUtilityRow1 = MelHLayout(self.containerName,ut='cgmUISubTemplate',padding = 2)
	
		guiFactory.doButton2(AttributeUtilityRow1,'cgmName to Float',
			                 lambda *a:tdToolsLib.doCGMNameToFloat(),
			                 'Makes an animatalbe float attribute using the cgmName tag')
	
		mc.setParent(self.containerName)
		guiFactory.lineSubBreak()
	
		AttributeUtilityRow1.layout()
	
		#>>> SDK tools
		mc.setParent(self.containerName)
		guiFactory.lineBreak()
		guiFactory.header('SDK Tools')
		guiFactory.lineSubBreak()
	
	
		sdkRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
		guiFactory.doButton2(sdkRow,'Select Driven Joints',
			                 lambda *a:tdToolsLib.doSelectDrivenJoints(self),
			                 "Selects driven joints from an sdk attribute")
	
	
		sdkRow.layout()
		mc.setParent(self.containerName)
		guiFactory.lineSubBreak()
		

		return self.containerName
	


