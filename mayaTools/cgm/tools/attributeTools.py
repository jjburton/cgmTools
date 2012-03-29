#=================================================================================================================================================
#=================================================================================================================================================
#	attributeTools - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Large collection of rigging tools
#
# REQUIRES:
#   Maya
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1.12072011 - First version
#	0.1.12132011 - master control maker implemented, snap move tools added
#	0.1.01092012 - Rewrote with Hamish's stuff
#	0.1.01102012 - Added abililty to set default color, default color now carries across instances of tool. Added ability to
#                      to create multiple text curves at once with ';' between them. Added snap to surface basic implementation
#                      Added first pass of grid layout
#	0.1.01112012 - Added Attribute Tab - cgmNameToFloat. Added Info Tab - countSelected. Grid layout- added ability arrange by name
#	0.1.01113012 - Started skin cluster utilities, added find verts with excess influence
#
#=================================================================================================================================================
__version__ = '0.1.01102012'


import maya.mel as mel
import maya.cmds as mc

from cgm.lib.cgmBaseMelUI import *

from cgm.lib import (guiFactory,
                     dictionary,
                     search)

from cgm.tools import (tdToolsLib,
                       locinatorLib)

from cgm.tools.lib import (attributeToolsLib)

reload(tdToolsLib)
reload(attributeToolsLib)

def run():
	attributeToolsClass()
	#mel.eval('python("import maya.cmds as mc;from cgm.tools import namingTools;from cgm.tools import tdToolsLib;from cgm.lib import guiFactory;attributeTools = attributeTools.attributeToolsClass()")')

	"""
	Hamish, the reason I did this was a few reasons

	1) because I need to know what the name of my ui window is which
	I'm declaring in this mel.eval do you know a better way to do this?

	2) I get an mc error otherwise

	3) issue with the gui templates note initializing otherwise. Also it looks like your revision to zooPy's baseMelUI
	borked the template initialize stuff. Took me a bit to realized you'd removed all of that. Can we do a code compare to see what I changed to
	see if we can roll that into your code so everything works again or tell me another way to get them working together?


	your code:
	tdToolsClass()
	"""

class attributeToolsClass(BaseMelWindow):
	WINDOW_NAME = 'attributeTools'
	WINDOW_TITLE = 'cgm.attributeTools'
	DEFAULT_SIZE = 300, 400
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created
	guiFactory.initializeTemplates()

	def __init__( self):
		import maya.mel as mel
		import maya.cmds as mc

		from cgm.lib import (guiFactory,
				             search)
		from cgm.tools import (tdToolsLib,
				               locinatorLib)


		# Maya version check
		if mayaVer >= 2011:
			self.currentGen = True
		else:
			self.currentGen = False
		# Basic variables
		self.window = ''
		self.activeTab = ''
		self.toolName = 'attributeTools'
		self.module = 'tdTools'
		self.winName = 'attributeToolsWin'

		self.showHelp = False
		self.helpBlurbs = []
		self.oldGenBlurbs = []

		self.showTimeSubMenu = False
		self.timeSubMenu = []

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




	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Menus
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildHelpMenu(self, *a ):
		self.UI_HelpMenu.clear()
		ShowHelpOption = mc.optionVar( q='cgmVarTDToolsShowHelp' )
		MelMenuItem( self.UI_HelpMenu, l="Show Help",
				     cb=ShowHelpOption,
				     c= lambda *a: self.do_showHelpToggle())
		MelMenuItem( self.UI_HelpMenu, l="Print Tools Help",
				     c=lambda *a: self.printHelp() )

		MelMenuItemDiv( self.UI_HelpMenu )
		MelMenuItem( self.UI_HelpMenu, l="About",
				     c=lambda *a: self.showAbout() )

	def do_showHelpToggle(self):
		ShowHelpOption = mc.optionVar( q='cgmVarTDToolsShowHelp' )
		guiFactory.toggleMenuShowState(ShowHelpOption,self.helpBlurbs)
		mc.optionVar( iv=('cgmVarTDToolsShowHelp', not ShowHelpOption))


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
		OptionList = ['Tools','Manager']
		cgmVarName = 'cgmAttributeMode'
		RadioCollectionName ='AttributeMode'
		RadioOptionList = 'AttributeModeSelectionChoicesList'

		ShowHelpOption = mc.optionVar( q='cgmVarTDToolsShowHelp' )
		
		if not mc.optionVar( ex=cgmVarName ):
			mc.optionVar( sv=(cgmVarName, OptionList[0]) )
		
		
		#Mode Change row 
		ModeSetRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
		MelLabel(ModeSetRow, label = 'Choose Mode: ',align='right')
		self.RadioCollectionName = MelRadioCollection()
		self.RadioOptionList = []		

		#build our sub section options
		self.ContainerList = []

		self.ContainerList.append( self.buildAttributeEditingTool(parent,vis=False) )
		self.ContainerList.append( self.buildAttributeManagerTool( parent,vis=False) )

		for item in OptionList:
			self.RadioOptionList.append(self.RadioCollectionName.createButton(ModeSetRow,label=item,
						                                                      onCommand = Callback(guiFactory.toggleModeState,item,OptionList,cgmVarName,self.ContainerList)))
		ModeSetRow.layout()


		mc.radioCollection(self.RadioCollectionName,edit=True, sl=self.RadioOptionList[OptionList.index(mc.optionVar(q=cgmVarName))])

		
		
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
		                                       annotation = "Text for the text object. Create multiple with a ';'. \n For example: 'Test1;Test2;Test3'")
		guiFactory.doButton2(attrCreateRow,'Create',
		                     "print 'yes'",
		                     "Create")

		attrCreateRow.setStretchWidget(self.AttrNamesTextField)
		attrCreateRow.layout()
		
		
		#>>> asf
		attrTypes = ['string','vector','int','bool','enum','message']
		self.CreateAttrTypeRadioCollection = MelRadioCollection()
		self.CreateAttrTypeRadioOptionList = []		
		
		#build our sub section options
		AttrTypeRow = MelHLayout(self.containerName,ut='cgmUISubTemplate',padding =15)
		for item in attrTypes:
			self.CreateAttrTypeRadioCollection.createButton(AttrTypeRow,label='')

		#mc.radioCollection(self.RadioCollectionName,edit=True, sl=self.RadioOptionList[attrTypes.index(mc.optionVar(q=cgmVarName))])

		AttrTypeRow.layout()
		
		
		AttrLabelRow = MelHLayout(self.containerName,ut='cgmUISubTemplate',padding = 5)
		for item in attrTypes:
			MelLabel(AttrLabelRow,label=item)
		AttrLabelRow.layout()
		
		
		
		###Modify
		mc.setParent(self.containerName)
		guiFactory.header('Modify')
		guiFactory.lineSubBreak()
		
		#>>> Load To Field
		#clear our variables
		if not mc.optionVar( ex='cgmVarAttributeSourceObject' ):
			mc.optionVar( sv=('cgmVarAttributeSourceObject', '') )
	
		LoadAttributeObjectRow = MelHSingleStretchLayout(self.containerName ,ut='cgmUISubTemplate',padding = 5)
	
		MelSpacer(LoadAttributeObjectRow,w=5)
		
		self.SourceObjectField = MelTextField(LoadAttributeObjectRow, w= 125, ut = 'cgmUIReservedTemplate', editable = False)

	
		guiFactory.doButton2(LoadAttributeObjectRow,'<<',
	                        lambda *a:attributeToolsLib.uiLoadSourceObject(self),
	                         'Load to field')
	
		LoadAttributeObjectRow.setStretchWidget(self.SourceObjectField  )
		
		MelLabel(LoadAttributeObjectRow, l=' . ')
		self.ObjectAttributesOptionMenu = MelOptionMenu(LoadAttributeObjectRow)
	

	
		MelSpacer(LoadAttributeObjectRow,w=5)
	
		LoadAttributeObjectRow.layout()
	
	
		mc.setParent(self.containerName)
		guiFactory.lineSubBreak()


		#>>> Tag Labels
		TagLabelsRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
		MelLabel(TagLabelsRow,label = 'Position')
		MelLabel(TagLabelsRow,label = 'Direction')
		MelLabel(TagLabelsRow,label = 'Name')
		MelLabel(TagLabelsRow,label = 'Type')
	
		TagLabelsRow.layout()
		
		#>>> Tags
		mc.setParent(self.containerName )
		TagsRow = MelHLayout(self.containerName,ut='cgmUISubTemplate',padding = 3)
		self.PositionTagField = MelTextField(TagsRow,
	                                     enable = False,
	                                     bgc = dictionary.returnStateColor('normal'),
	                                     ec = lambda *a: tdToolsLib.uiUpdateAutoNameTag(self,'cgmPosition'),
	                                     w = 75)
		self.DirectionTagField = MelTextField(TagsRow,
	                                     enable = False,
	                                     bgc = dictionary.returnStateColor('normal'),
	                                     ec = lambda *a: tdToolsLib.uiUpdateAutoNameTag(self,'cgmDirection'),
	                                     w = 75)
		self.NameTagField = MelTextField(TagsRow,
	                                     enable = False,
	                                     bgc = dictionary.returnStateColor('normal'),
	                                     ec = lambda *a: tdToolsLib.uiUpdateAutoNameTag(self,'cgmName'),
	                                     w = 75)
		"""
		self.NameTagFieldPopUp = MelPopupMenu(self.NameTagField,button = 3)
		self.NameTagLoadParentPopUp = MelMenuItem(self.NameTagFieldPopUp ,
												  label = 'Select parent name object',
												  enable = False)
		"""
		self.ObjectTypeTagField = MelTextField(TagsRow,
	                                     enable = False,
	                                     bgc = dictionary.returnStateColor('normal'),
	                                     ec = lambda *a: tdToolsLib.uiUpdateAutoNameTag(self,'cgmType'),
	                                     w = 75)
		
		TagsRow.layout()
		mc.setParent(self.containerName )
		guiFactory.lineSubBreak()
		
		#>>> ModifierTags
		mc.setParent(self.containerName )
		TagModifiersRow = MelHLayout(self.containerName,ut='cgmUISubTemplate',padding = 3)
		MelLabel(TagModifiersRow,align = 'right', label = 'Modifiers ------->',w = 75)
		self.DirectionModifierTagField = MelTextField(TagModifiersRow,
	                                     enable = False,
	                                     bgc = dictionary.returnStateColor('normal'),
	                                     ec = lambda *a: tdToolsLib.uiUpdateAutoNameTag(self,'cgmDirectionModifier'),
	                                     w = 75)
		self.NameModifierTagField = MelTextField(TagModifiersRow,
	                                     enable = False,
	                                     bgc = dictionary.returnStateColor('normal'),
	                                     ec = lambda *a: tdToolsLib.uiUpdateAutoNameTag(self,'cgmNameModifier'),
	                                     w = 75)
		self.ObjectTypeModifierTagField = MelTextField(TagModifiersRow,
	                                     enable = False,
	                                     bgc = dictionary.returnStateColor('normal'),
	                                     ec = lambda *a: tdToolsLib.uiUpdateAutoNameTag(self,'cgmTypeModifier'),
	                                     w = 75)
		
		TagModifiersRow.layout()
		
		
		
		mc.setParent(self.containerName )
		guiFactory.lineSubBreak()
		guiFactory.lineBreak()
		
		#>>> Basic
		mc.setParent(self.containerName )
		guiFactory.header('Connect')
		guiFactory.lineSubBreak()

			
		return self.containerName
	
	
		
	def buildAttributeManagerTool(self,parent, vis=True):
		containerName = 'Attributes Constainer'
		self.containerName = MelColumn(parent,vis=vis)

		#>>> Tag Labels
		TagLabelsRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
		MelLabel(TagLabelsRow,label = 'Not done yet...')
		TagLabelsRow.layout()
		
		if mc.optionVar( q = 'cgmVarAttributeSourceObject'):
			self.SourceObjectField(edit=True,text = mc.optionVar( q = 'cgmVarAttributeSourceObject'))
			attributeToolsLib.uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu)

		return self.containerName