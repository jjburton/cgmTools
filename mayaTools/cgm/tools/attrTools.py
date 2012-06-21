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
__version__ = '0.1.06192012'
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

reload(tdToolsLib)
reload(attrToolsLib)

def run():
	cgmAttrToolsWin = attrToolsClass()

class attrToolsClass(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_Template = 'cgmUITemplate'
	
	WINDOW_NAME = 'attrTools'
	WINDOW_TITLE = 'cgm.attrTools'
	DEFAULT_SIZE = 350, 400
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
		self.UI_HelpMenu = MelMenu( l='Help', pmc=self.buildHelpMenu)

		MainColumn = MelColumnLayout(self)

		self.buildAttributeTool(MainColumn)
		
		self.show()


	def setupVariables(self):
		self.ShowHelpOptionVar = OptionVarFactory('cgmVar_attrToolsShowHelp', defaultValue = 0)

		self.ActiveObjectSetsOptionVar = OptionVarFactory('cgmVar_activeObjectSets',defaultValue = [''])

		guiFactory.appendOptionVarList(self,self.ShowHelpOptionVar.name)


	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Menus
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildHelpMenu(self, *a ):
		self.UI_HelpMenu.clear()
		MelMenuItem( self.UI_HelpMenu, l="Show Help",
				     cb=self.ShowHelpOptionVar.value,
				     c= lambda *a: self.do_showHelpToggle())
		MelMenuItem( self.UI_HelpMenu, l="Print Tools Help",
				     c=lambda *a: self.printHelp() )

		MelMenuItemDiv( self.UI_HelpMenu )
		MelMenuItem( self.UI_HelpMenu, l="About",
				     c=lambda *a: self.showAbout() )

	def do_showHelpToggle(self):
		guiFactory.toggleMenuShowState(ShowHelpOption,self.helpBlurbs)
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
		guiFactory.doButton('Visit Website', 'import webbrowser;webbrowser.open("http://www.cgmonks.com")')
		guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
		mc.setParent( '..' )
		mc.showWindow( window )

	def printHelp(self):
		import tdToolsLib
		help(tdToolsLib)

	
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Tools
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildAttributeTool(self,parent,vis=True):
		OptionList = ['Tools','Manager','Utilities']
		cgmVar_Name = 'cgmVar_AttributeMode'
		RadioCollectionName ='AttributeMode'
		RadioOptionList = 'AttributeModeSelectionChoicesList'

		ShowHelpOption = mc.optionVar( q='cgmVar_TDToolsShowHelp' )
		
		if not mc.optionVar( ex=cgmVar_Name ):
			mc.optionVar( sv=(cgmVar_Name, OptionList[0]) )
		
		MelSeparator(parent,ut = 'cgmUIHeaderTemplate',h=5)
		
		#Mode Change row 
		ModeSetRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
		MelLabel(ModeSetRow, label = 'Choose Mode: ',align='right')
		self.RadioCollectionName = MelRadioCollection()
		self.RadioOptionList = []		

		#build our sub section options
		self.ContainerList = []

		self.ContainerList.append( self.buildAttributeEditingTool(parent,vis=False) )
		self.ContainerList.append( self.buildAttributeManagerTool( parent,vis=False) )
		self.ContainerList.append( self.buildAttributeUtilitiesTool( parent,vis=False) )
		
		for item in OptionList:
			self.RadioOptionList.append(self.RadioCollectionName.createButton(ModeSetRow,label=item,
						                                                      onCommand = Callback(guiFactory.toggleModeState,item,OptionList,cgmVar_Name,self.ContainerList)))
		ModeSetRow.layout()


		mc.radioCollection(self.RadioCollectionName,edit=True, sl=self.RadioOptionList[OptionList.index(mc.optionVar(q=cgmVar_Name))])

		
		
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
		self.AttrNamesTextField = MelTextField(attrCreateRow,backgroundColor = [1,1,1],
		                                       annotation = "Names for the attributes. Create multiple with a ';'. \n Message nodes try to connect to the last object in a selection \n For example: 'Test1;Test2;Test3'")
		guiFactory.doButton2(attrCreateRow,'Add',
		                     lambda *a: attrToolsLib.doAddAttributesToSelected(self),
		                     "Add the attribute names from the text field")
		MelSpacer(attrCreateRow,w=2)

		attrCreateRow.setStretchWidget(self.AttrNamesTextField)
		attrCreateRow.layout()
		
		
		#>>> asf
		self.buildAttrTypeRow(self.containerName)
		MelSeparator(self.containerName,ut = 'cgmUIHeaderTemplate',h=3)
		MelSeparator(self.containerName,ut = 'cgmUITemplate',h=10)
		
		###Modify
		mc.setParent(self.containerName)
		guiFactory.header('Modify')
		guiFactory.lineSubBreak()
		
		#>>> Load To Field
		#clear our variables
		if not mc.optionVar( ex='cgmVar_AttributeSourceObject' ):
			mc.optionVar( sv=('cgmVar_AttributeSourceObject', '') )
	
		LoadAttributeObjectRow = MelHSingleStretchLayout(self.containerName ,ut='cgmUISubTemplate',padding = 5)
	
		MelSpacer(LoadAttributeObjectRow,w=5)
		
		guiFactory.doButton2(LoadAttributeObjectRow,'>>',
	                        lambda *a:attrToolsLib.uiLoadSourceObject(self),
	                         'Load to field')
		
		self.SourceObjectField = MelTextField(LoadAttributeObjectRow, w= 125, ut = 'cgmUIReservedTemplate', editable = False)
	
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
	
	
		mc.setParent(self.containerName)
		guiFactory.lineSubBreak()


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
		
		#>>> Int Row
		self.EditDigitSettingsRow = MelFormLayout(self.containerName,ut='cgmUISubTemplate',vis = False)
		MinLabel = MelLabel(self.EditDigitSettingsRow,label = 'Min: ')
		self.MinField = MelTextField(self.EditDigitSettingsRow,
		                             bgc = dictionary.returnStateColor('normal'),
		                             ec = lambda *a: attrToolsLib.uiUpdateMinValue(self),		                             
		                             w = 70)
		MaxLabel = MelLabel(self.EditDigitSettingsRow,label = 'Max: ')		
		self.MaxField = MelTextField(self.EditDigitSettingsRow,
		                             bgc = dictionary.returnStateColor('normal'),
		                             ec = lambda *a: attrToolsLib.uiUpdateMaxValue(self),		                             		                             
		                             w = 70)
		DefaultLabel = MelLabel(self.EditDigitSettingsRow,label = 'Default: ')		
		self.DefaultField = MelTextField(self.EditDigitSettingsRow,
		                                 bgc = dictionary.returnStateColor('normal'),
		                                 ec = lambda *a: attrToolsLib.uiUpdateDefaultValue(self),		                             		                                 
		                                 w = 70)
		
		mc.formLayout(self.EditDigitSettingsRow, edit = True,
	                  af = [(MinLabel, "left", 20),
	                        (self.DefaultField,"right",20)],
	                  ac = [(self.MinField,"left",2,MinLabel),
	                        (MaxLabel,"left",2,self.MinField),
	                        (self.MaxField,"left",2,MaxLabel),
	                        (DefaultLabel,"left",2,self.MaxField),
		                    (self.DefaultField,"left",2,DefaultLabel),
		                    ])
		#>>> Enum
		MelSeparator(self.containerName,ut='cgmUISubTemplate',h=5)
		self.EditEnumRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5, vis = False)
		MelSpacer(self.EditEnumRow,w=10)
		MelLabel(self.EditEnumRow,label = 'Enum: ')
		self.EnumField = MelTextField(self.EditEnumRow,
				                      annotation = "Options divided by ':'. \n Set values with '=' \n For example: 'off:on=1:maybe:23'",
		                              bgc = dictionary.returnStateColor('normal'),
		                              w = 75)
		MelSpacer(self.EditEnumRow,w=10)
		self.EditEnumRow.setStretchWidget(self.EnumField)
		
		self.EditEnumRow.layout()
		
		#>>> String
		self.EditStringRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5, vis = False)
		MelSpacer(self.EditStringRow,w=10)
		MelLabel(self.EditStringRow,label = 'String: ')
		self.StringField = MelTextField(self.EditStringRow,
		                                bgc = dictionary.returnStateColor('normal'),
		                                w = 75)
		MelSpacer(self.EditStringRow,w=10)
		self.EditStringRow.setStretchWidget(self.StringField)
		
		self.EditStringRow.layout()
		
		#>>> Message
		MelSeparator(self.containerName,ut='cgmUISubTemplate',h=5)
		self.EditMessageRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5, vis = False)
		MelSpacer(self.EditMessageRow,w=10)
		MelLabel(self.EditMessageRow,label = 'Message: ')
		self.MessageField = MelTextField(self.EditMessageRow,
		                                enable = False,
		                                bgc = dictionary.returnStateColor('locked'),
		                                ec = lambda *a: tdToolsLib.uiUpdateAutoNameTag(self,'cgmPosition'),
		                                w = 75)
		self.LoadMessageButton = guiFactory.doButton2(self.EditMessageRow,'<<',
		                                              lambda *a:attrToolsLib.uiLoadSourceObject(self),
		                                               'Load to message')
		MelSpacer(self.EditMessageRow,w=10)
		self.EditMessageRow.setStretchWidget(self.MessageField)

		self.EditMessageRow.layout()
		
		
		mc.setParent(self.containerName )
		guiFactory.lineSubBreak()
		guiFactory.lineBreak()

		
		#>>> Basic
		mc.setParent(self.containerName )
		guiFactory.header('Connect')
		guiFactory.doButton2(self.containerName,'Select an attr',
	                        lambda *a: attrToolsLib.uiSelectAttrMenu(self,'test'),
		                    'Delete attribute')		
		guiFactory.lineSubBreak()

			
		return self.containerName
	
	def buildAttrTypeRow(self,parent):	
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# Attr type row
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		attrTypes = ['string','float','int','vector','bool','enum','message']
		attrShortTypes = ['str','float','int','[000]','bool','enum','msg']

		self.CreateAttrTypeRadioCollection = MelRadioCollection()
		self.CreateAttrTypeRadioCollectionChoices = []		
		
		self.CreateAttrTypeOptionVar = OptionVarFactory('cgmVar_AttrCreateType','string')
		guiFactory.appendOptionVarList(self,self.CreateAttrTypeOptionVar.name)
			
		#build our sub section options
		AttrTypeRow = MelHLayout(self.containerName,ut='cgmUISubTemplate',padding = 5)
		for cnt,item in enumerate(attrTypes):
			self.CreateAttrTypeRadioCollectionChoices.append(self.CreateAttrTypeRadioCollection.createButton(AttrTypeRow,label=attrShortTypes[cnt],
			                                                                                                 onCommand = Callback(self.CreateAttrTypeOptionVar.set,item)))
			MelSpacer(AttrTypeRow,w=2)
		
		if self.CreateAttrTypeOptionVar.value != '':
			mc.radioCollection(self.CreateAttrTypeRadioCollection ,edit=True,sl= (self.CreateAttrTypeRadioCollectionChoices[ attrTypes.index(self.CreateAttrTypeOptionVar.value) ]))
		
		AttrTypeRow.layout()
		"""
		AttrLabelRow = MelHLayout(self.containerName,ut='cgmUISubTemplate')
		for item in attrTypes:
			MelLabel(AttrLabelRow,label=item)
		AttrLabelRow.layout()
		"""

		
	def buildAttributeManagerTool(self,parent, vis=True):
		containerName = 'Attributes Constainer'
		self.containerName = MelColumn(parent,vis=vis)

		#>>> Tag Labels
		TagLabelsRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
		MelLabel(TagLabelsRow,label = 'Not done yet...')
		TagLabelsRow.layout()
		
		if mc.optionVar( q = 'cgmVar_AttributeSourceObject'):
			self.SourceObjectField(edit=True,text = mc.optionVar( q = 'cgmVar_AttributeSourceObject'))
			attrToolsLib.uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu)

		return self.containerName
	
	
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
	


