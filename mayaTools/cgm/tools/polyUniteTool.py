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
__version__ = '0.1.03192012'


import maya.mel as mel
import maya.cmds as mc

from cgm.lib.zoo.zooPyMaya.baseMelUI import *

from cgm.lib import (guiFactory,
                     dictionary,
                     search)

from cgm.tools.lib import  (tdToolsLib,
                            locinatorLib,
                            namingToolsLib)

#reload(tdToolsLib)


def run():
	#mel.eval('python("import maya.cmds as mc;from cgm.tools import polyUniteTool;from cgm.tools.lib import tdToolsLib;from cgm.lib import guiFactory;cgmPolyUniteWin = polyUniteTool.polyUniteClass()")')
	polyUniteWin = polyUniteClass()

class polyUniteClass(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_TEMPLATE = 'cgmUITemplate'
	
	WINDOW_NAME = 'PolyUniteTool'
	WINDOW_TITLE = 'cgm.polyUniteTool - %s'%__version__
	DEFAULT_SIZE = 250, 150
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created

	def __init__( self):


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
		self.toolName = 'cgmTDTools'
		self.module = 'cgmTDTools'
		self.winName = 'cgmTDToolsWin'
		self.optionVars = []

		self.showHelp = False
		self.helpBlurbs = []
		self.oldGenBlurbs = []

		self.showTimeSubMenu = False
		self.timeSubMenu = []

		# About Window
		self.description = 'Standalone PolyUnite tool'
		self.author = 'Josh Burton'
		self.owner = 'CG Monks'
		self.website = 'www.cgmonks.com'
		self.version = __version__


		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# Build
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

		#Menu	
		
		PolyUniteWindowColumn = MelColumn(self)
		self.buildPolyUniteTool(PolyUniteWindowColumn)

		self.show()



	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Tab Layouts
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildPolyUniteTool(self,parent):
		#Options
		#clear our variables
		if not mc.optionVar( ex='cgmVar_SourceObject' ):
			mc.optionVar( sv=('cgmVar_SourceObject', '') )

		mc.setParent(parent)
		guiFactory.header('PolyUnite')

		PolyUniteColumn = MelColumn(parent)
		
		LoadObjectUtilityRow = MelHSingleStretchLayout(PolyUniteColumn,ut='cgmUISubTemplate',padding = 5)
		MelSpacer(LoadObjectUtilityRow)
		MelLabel(LoadObjectUtilityRow,l='Base Name:',align='right')
		self.BaseNameField = MelTextField(LoadObjectUtilityRow,backgroundColor = [1,1,1],w=60,
	                                      annotation = "Base name for our various tools to use")
		LoadObjectUtilityRow.setStretchWidget(self.BaseNameField )
		MelSpacer(LoadObjectUtilityRow,w=5)

		LoadObjectUtilityRow.layout()
		
		mc.setParent(PolyUniteColumn)
		guiFactory.lineSubBreak()
		
		#Start LoadToField
		LoadObjectTargetUtilityRow = MelHSingleStretchLayout(PolyUniteColumn,ut='cgmUISubTemplate',padding = 5)

		MelSpacer(LoadObjectTargetUtilityRow,w=5)


		MelLabel(LoadObjectTargetUtilityRow,l='Source:',align='right')

		self.SourceObjectField = MelTextField(LoadObjectTargetUtilityRow, w= 125, ut = 'cgmUIReservedTemplate', editable = False)

		MelSpacer(LoadObjectTargetUtilityRow,w=5)

		LoadObjectTargetUtilityRow.layout()


		mc.setParent(PolyUniteColumn)
		guiFactory.lineSubBreak()
		
		
		# Buttons
		guiFactory.doButton2(PolyUniteColumn,'Load to Source',
		                     lambda *a:tdToolsLib.doLoadPolyUnite(self),
				             "Attempts to load polyUnite and select the source shapes")
		guiFactory.doButton2(PolyUniteColumn,'Build polyUnite',
		                     lambda *a:tdToolsLib.doBuildPolyUnite(self),
				             "Builds a poly unite geo node from or \n selected objects (checks for mesh types)")
		guiFactory.doButton2(PolyUniteColumn,'Remove polyUnite node',
		                     lambda *a:tdToolsLib.doDeletePolyUniteNode(self),
				             "If a polyUnite node is loaded \n removes the polyUnite node but leaves \n the united geo")




	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Components
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildLoadObjectField(self,parent, optionVar):
		#clear our variables
		if not mc.optionVar( ex=optionVar ):
			mc.optionVar( sv=(optionVar, '') )

		LoadObjectTargetUtilityRow = MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

		MelSpacer(LoadObjectTargetUtilityRow,w=5)


		MelLabel(LoadObjectTargetUtilityRow,l='Object:',align='right')

		self.SourceObjectField = MelTextField(LoadObjectTargetUtilityRow, w= 125, ut = 'cgmUIReservedTemplate', editable = False)
		if mc.optionVar( q = optionVar):
			self.SourceObjectField(edit=True,text = mc.optionVar( q = optionVar))

		guiFactory.doButton2(LoadObjectTargetUtilityRow,'<<',
				             "guiFactory.doLoadSingleObjectToTextField(cgmTDToolsWin.SourceObjectField,'cgmVar_SourceObject')",
				             'Load to field')


		MelLabel(LoadObjectTargetUtilityRow,l='Target:',align='right')
		self.TargetObjectField = MelTextField(LoadObjectTargetUtilityRow, w=125, ut = 'cgmUIReservedTemplate', editable = False)

		LoadObjectTargetUtilityRow.setStretchWidget(self.BaseNameField )

		guiFactory.doButton2(LoadObjectTargetUtilityRow,'<<',
				             "guiFactory.doLoadMultipleObjectsToTextField(cgmTDToolsWin.TargetObjectField,False,'cgmVar_TargetObjects')",
				             'Load to field')

		MelSpacer(LoadObjectTargetUtilityRow,w=5)

		LoadObjectTargetUtilityRow.layout()


		mc.setParent(parent)
		guiFactory.lineSubBreak()
	
	def buildLoadObjectTargetTool(self,parent,baseNameField=True):
		#clear our variables
		if not mc.optionVar( ex='cgmVar_SourceObject' ):
			mc.optionVar( sv=('cgmVar_SourceObject', '') )
		if not mc.optionVar( ex='cgmVar_TargetObjects' ):
			mc.optionVar( sv=('cgmVar_TargetObjects', '') )


		LoadObjectTargetUtilityRow = MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

		MelSpacer(LoadObjectTargetUtilityRow,w=5)

		if baseNameField:
			MelLabel(LoadObjectTargetUtilityRow,l='Base Name:',align='right')
			self.BaseNameField = MelTextField(LoadObjectTargetUtilityRow,backgroundColor = [1,1,1],w=60,
						                      annotation = "Base name for our various tools to use")

		MelLabel(LoadObjectTargetUtilityRow,l='Source:',align='right')

		self.SourceObjectField = MelTextField(LoadObjectTargetUtilityRow, w= 125, ut = 'cgmUIReservedTemplate', editable = False)
		if mc.optionVar( q = 'cgmVar_SourceObject'):
			self.SourceObjectField(edit=True,text = mc.optionVar( q = 'cgmVar_SourceObject'))

		guiFactory.doButton2(LoadObjectTargetUtilityRow,'<<',
				             "guiFactory.doLoadSingleObjectToTextField(cgmTDToolsWin.SourceObjectField,'cgmVar_SourceObject')",
				             'Load to field')


		MelLabel(LoadObjectTargetUtilityRow,l='Target:',align='right')
		self.TargetObjectField = MelTextField(LoadObjectTargetUtilityRow, w=125, ut = 'cgmUIReservedTemplate', editable = False)

		LoadObjectTargetUtilityRow.setStretchWidget(self.BaseNameField )

		guiFactory.doButton2(LoadObjectTargetUtilityRow,'<<',
				             "guiFactory.doLoadMultipleObjectsToTextField(cgmTDToolsWin.TargetObjectField,False,'cgmVar_TargetObjects')",
				             'Load to field')

		MelSpacer(LoadObjectTargetUtilityRow,w=5)

		LoadObjectTargetUtilityRow.layout()


		mc.setParent(parent)
		guiFactory.lineSubBreak()


