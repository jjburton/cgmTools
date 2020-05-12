#=================================================================================================================================================
#=================================================================================================================================================
#	cgmTDTools - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Large collection of rigging tools
#
# ARGUMENTS:
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

from cgm.lib.zoo.zooPyMaya.baseMelUI import *

from cgm.lib import (guiFactory,
                     dictionary,
                     search)

from cgm.tools.lib import (tdToolsLib,
                           locinatorLib)

#reload(tdToolsLib)


def run():
	mel.eval('python("import maya.cmds as mc;from cgm.tools import namingTools;from cgm.tools.lib import tdToolsLib;from cgm.lib import guiFactory;cgmNamingToolsWin = namingTools.namingToolsClass()")')

class namingToolsClass(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_TEMPLATE = 'cgmUITemplate'
	
	WINDOW_NAME = 'namingTools'
	WINDOW_TITLE = 'cgm.namingTools'
	DEFAULT_SIZE = 550, 400
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created

	def __init__( self):
		""" Hamish, why is this import necessary? It errors out if it isn't here....
		I guess I had it it in the mel.eval call before which is what locinator id doing
		from cgm.lib import guiFactory
		guiFactory.initializeTemplates()
		"""

		import maya.mel as mel
		import maya.cmds as mc

		from cgm.lib import (guiFactory,
				             search)
		from cgm.tools.lib import  (tdToolsLib,
		                            locinatorLib)


		# Maya version check
		if mayaVer >= 2011:
			self.currentGen = True
		else:
			self.currentGen = False
		# Basic variables
		self.window = ''
		self.activeTab = ''
		self.toolName = 'namingTools'
		self.module = 'tdTools'
		self.winName = 'NamingToolsWin'
		self.optionVars = []

		self.showHelp = False
		self.helpBlurbs = []
		self.oldGenBlurbs = []

		self.showTimeSubMenu = False
		self.timeSubMenu = []

		# About Window
		self.description = 'A large series of tools for general rigging purposes including: Curves, Naming, Positioning,Deformers'
		self.author = 'Josh Burton'
		self.owner = 'CG Monks'
		self.website = 'www.cgmonks.com'
		self.version =  __version__ 

		# About Window
		self.sizeOptions = ['Object','Average','Input Size','First Object']
		self.sizeMode = 0
		self.forceBoundingBoxState = False


		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# Build
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

		#Menu
		self.UI_HelpMenu = MelMenu( l='Help', pmc=self.buildHelpMenu)

		#Tabs
		tabs = MelTabLayout( self )

		TabAuto = MelColumnLayout(tabs)
		TabStandard = MelColumnLayout(tabs)


		#tabs.setCB(lambda *a:self.updateCurrentTab(tabs,'cgmTDToolsWinActiveTab'))
		#tabs.setCB(self.updateCurrentTab(tabs,'cgmTDToolsWinActiveTab'))

		n = 0
		for tab in 'Auto','Standard':
			tabs.setLabel(n,tab)
			n+=1

		self.buildAutoNameTool(TabAuto)
		self.buildAutoNameTool(TabStandard)
		
		
		self.show()




	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Menus
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildHelpMenu(self, *a ):
		self.UI_HelpMenu.clear()
		ShowHelpOption = mc.optionVar( q='cgmVar_TDToolsShowHelp' )
		MelMenuItem( self.UI_HelpMenu, l="Show Help",
				     cb=ShowHelpOption,
				     c= lambda *a: self.do_showHelpToggle())
		MelMenuItem( self.UI_HelpMenu, l="Print Tools Help",
				     c=lambda *a: self.printHelp() )

		MelMenuItemDiv( self.UI_HelpMenu )
		MelMenuItem( self.UI_HelpMenu, l="About",
				     c=lambda *a: self.showAbout() )

	def do_showHelpToggle(self):
		ShowHelpOption = mc.optionVar( q='cgmVar_TDToolsShowHelp' )
		guiFactory.toggleMenuShowState(ShowHelpOption,self.helpBlurbs)
		mc.optionVar( iv=('cgmVar_TDToolsShowHelp', not ShowHelpOption))


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
	def buildAutoNameTool(self,parent, vis=True):
		containerName = 'AutoNameContainer'
		self.containerName = MelColumn(parent,vis=vis)
		
		#>>> Begin the section
		mc.setParent(self.containerName )
		guiFactory.header('Tag and Release')
		guiFactory.lineSubBreak()
		
		#>>> Guessed Name
		GenratedNameRow = MelHLayout(self.containerName ,ut='cgmUIInstructionsTemplate')
		self.GeneratedNameField = MelLabel(GenratedNameRow,
	                                       bgc = dictionary.returnStateColor('help'),
	                                       align = 'center',
	                                       label = 'Name will preview here...')
		
		GenratedNameRow.layout()
		mc.setParent(self.containerName )
		guiFactory.lineSubBreak()
		guiFactory.lineSubBreak()
	
		#>>> Load To Field
		#clear our variables
		if not mc.optionVar( ex='cgmVar_AutoNameObject' ):
			mc.optionVar( sv=('cgmVar_AutoNameObject', '') )
	
		LoadAutoNameObjectRow = MelHSingleStretchLayout(self.containerName ,ut='cgmUISubTemplate',padding = 5)
	
		MelSpacer(LoadAutoNameObjectRow,w=5)
	
		MelLabel(LoadAutoNameObjectRow,l='Object:',align='right')
	
		self.AutoNameObjectField = MelTextField(LoadAutoNameObjectRow, w= 125, ut = 'cgmUIReservedTemplate', editable = False)
		if mc.optionVar( q = 'cgmVar_AutoNameObject'):
			self.AutoNameObjectField(edit=True,text = mc.optionVar( q = 'cgmVar_AutoNameObject'))
	
		guiFactory.doButton2(LoadAutoNameObjectRow,'<<',
	                        'tdToolsLib.uiLoadAutoNameObject(cgmTDToolsWin)',
	                         'Load to field')
	
		LoadAutoNameObjectRow.setStretchWidget(self.AutoNameObjectField  )
	
		guiFactory.doButton2(LoadAutoNameObjectRow,'Up',
	                         lambda *a:tdToolsLib.uiAutoNameWalkUp(self),
	                         'Load to field')
		
		guiFactory.doButton2(LoadAutoNameObjectRow,'Down',
	                         lambda *a:tdToolsLib.uiAutoNameWalkDown(self),
	                         'Load to field')
	
		guiFactory.doButton2(LoadAutoNameObjectRow,'Name it',
	                         lambda *a:tdToolsLib.uiNameLoadedAutoNameObject(self),
	                         'Load to field')
		guiFactory.doButton2(LoadAutoNameObjectRow,'Name Children',
	                         lambda *a:tdToolsLib.uiNameLoadedAutoNameObjectChildren(self),
	                         'Load to field')
	
		MelSpacer(LoadAutoNameObjectRow,w=5)
	
		LoadAutoNameObjectRow.layout()
	
	
		mc.setParent(self.containerName )
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
		guiFactory.header('On Selection')
		guiFactory.lineSubBreak()
	
		BasicRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
		guiFactory.doButton2(BasicRow,'Name Object',
	                         'tdToolsLib.uiNameObject(cgmTDToolsWin)',
	                         "Attempts to name an object")
		guiFactory.doButton2(BasicRow,'Update Name',
	                         'tdToolsLib.doUpdateObjectName(cgmTDToolsWin)',
	                         "Takes the name you've manually changed the object to, \n stores that to the cgmName tag then \n renames the object")
		guiFactory.doButton2(BasicRow,'Name Heirarchy',
	                         'tdToolsLib.doNameHeirarchy(cgmTDToolsWin)',
	                         "Attempts to intelligently name a  \n heirarchy of objects")
	
		BasicRow.layout()
		
		
		mc.setParent(self.containerName )
		guiFactory.lineSubBreak()
		guiFactory.lineBreak()
	
	
		return self.containerName
