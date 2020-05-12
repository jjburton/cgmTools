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
#=================================================================================================================================================
__version__ = '0.2.11022012'
from cgm.lib.zoo.zooPyMaya.baseMelUI import *

from cgm.lib.classes import OptionVarFactory 
#reload(OptionVarFactory)

from cgm.lib.classes.OptionVarFactory import *

import maya.mel as mel
import maya.cmds as mc

mayaVersion = int( mel.eval( 'getApplicationVersionAsFloat' ) )

from cgm.lib import (guiFactory,
                     dictionary,
                     search
                     )
from cgm.tools.lib import  (tdToolsLib,
                            locinatorLib,
                            namingToolsLib)

#reload(tdToolsLib)
reload(namingToolsLib)

def run():
    tdTools = tdToolsClass()

class tdToolsClass(BaseMelWindow):
    from  cgm.lib import guiFactory
    guiFactory.initializeTemplates()
    USE_Template = 'cgmUITemplate'

    WINDOW_NAME = 'TDTools'
    WINDOW_TITLE = ('cgm.tdTools - %s'%__version__) 
    DEFAULT_SIZE = 550, 400
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created

    def __init__( self):	
	# Basic variables
	self.window = ''
	self.activeTab = ''
	self.toolName = 'cgmTDTools'
	self.module = 'cgmTDTools'
	self.winName = 'cgmTDToolsWin'
	self.version = __version__
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


	# About Window
	self.sizeOptions = ['Object','Size+','1/2 Size','Average','Input Size','First Object']
	self.sizeMode = 0
	self.forceBoundingBoxState = False

	# Text Objects
	self.textObjectText = 'Text'
	self.textObjectSize = 1
	self.fontList = ['Arial','Times']
	self.textObjectFont= 'Arial'
	self.textCurrentObject= ''
	self.renameObjectOnUpdate = False

	self.textObjectTextField = ''
	self.textObjectSizeField = ''
	self.textObjectFontField = ''
	self.textCurrentObjectField = ''

	self.axisOptions = ['x+', 'y+', 'z+','x-', 'y-', 'z-']

	# Curves
	self.uiCurveSelector = ''
	self.controlCurveShape = 'cube'
	self.curveOptionList = 	['circle','square','squareRounded','squareDoubleRounded',
	                                'semiSphere','sphere','cube','pyramid',
	                                'cross','fatCross',
	                                'arrowSingle','arrowSingleFat','arrowDouble','arrowDoubleFat','arrow4','arrow4Fat','arrow8','arrowsOnBall',
	                                'nail','nail2','nail4',
	                                'eye','teeth','foot','gear','dumbell','locator',
	                                'arrowsLocator','arrowsPointCenter','arrowForm','arrowDirectionBall',
	                                'arrowRotate90','arrowRotate90Fat','arrowRotate180','arrowRotate180Fat',
	                                'circleArrow','circleArrow1','circleArrow2','circleArrow3','circleArrow1Interior','circleArrow2Axis',
	                                'masterAnim']

	self.uiCurveAxisOptionGroup = ''
	self.uiCurveAxis = 'z+'

	self.uiCurveNameField = ''
	self.uiCurveName = ''

	self.makeMasterControl = False
	self.makeMasterControlVis = False
	self.makeMasterControlSettings = False

	# Colors
	self.defaultOverrideColor = 6
	
	# Click Mesh
	self.ClickMeshTool = False

	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Build
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

	#Menu
	self.setupVariables()
	self.UI_OptionsMenu = MelMenu( l='Options', pmc=self.buildOptionsMenu)
	self.UI_AxisMenu = MelMenu( l='Axis', pmc=self.buildAxisMenu)
	self.UI_HelpMenu = MelMenu( l='Help', pmc=self.buildHelpMenu)

	#Tabs
	tabs = MelTabLayout( self )

	TabCurves = MelColumnLayout(tabs)
	TabPosition = MelColumnLayout(tabs)
	TabInfo = MelColumnLayout(tabs)
	TabAttribute = MelColumnLayout(tabs)
	TabDeformer = MelColumnLayout(tabs)
	TabNaming = MelColumnLayout(tabs)

	#tabs.setCB(lambda *a:self.updateCurrentTab(tabs,'cgmTDToolsWinActiveTab'))
	#tabs.setCB(self.updateCurrentTab(tabs,'cgmTDToolsWinActiveTab'))

	n = 0
	tabList = ['Curves','Position','Joints','Attribute','Deformer','Naming']
	for tab in tabList:
	    tabs.setLabel(n,tab)
	    n+=1
	
	tabsToBuild = [self.buildTab_Curves(TabCurves),
	               self.buildTab_Position(TabPosition),
	               self.buildTab_Joints(TabInfo),
	               self.buildTab_Attributes(TabAttribute),
	               self.buildTab_Deformer(TabDeformer),
	               self.buildTab_Naming(TabNaming)]

	mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(tabsToBuild))
	for t in tabsToBuild:
	    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
		    break
	    mc.progressBar(mayaMainProgressBar, edit=True, status = ("Building '%s'"%tabList[tabsToBuild.index(t)]), step=1)
	    t
	
	guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
	
	#Trying a preload from selected
	tdToolsLib.loadGUIOnStart(self)

	self.show()

    def setupVariables(self):
	if not mc.optionVar( ex='cgmTDToolsWinActiveTab' ):
	    mc.optionVar( iv=('cgmTDToolsWinActiveTab', 1) )

	if not mc.optionVar( ex='cgmVar_ForceBoundingBoxState' ):
	    mc.optionVar( iv=('cgmVar_ForceBoundingBoxState', 0) )
	if not mc.optionVar( ex='cgmVar_ForceEveryFrame' ):
	    mc.optionVar( iv=('cgmVar_ForceEveryFrame', 0) )
	if not mc.optionVar( ex='cgmVar_LocinatorShowHelp' ):
	    mc.optionVar( iv=('cgmVar_LocinatorShowHelp', 0) )
	if not mc.optionVar( ex='cgmVar_SizeMode' ):
	    mc.optionVar( iv=('cgmVar_SizeMode', 0) )
	if not mc.optionVar( ex='cgmVar_RenameOnUpdate' ):
	    mc.optionVar( iv=('cgmVar_RenameOnUpdate', 1) )
	if not mc.optionVar( ex='cgmVar_DefaultOverrideColor' ):
	    mc.optionVar( iv=('cgmVar_DefaultOverrideColor', 6) )
	       
	    
	guiFactory.appendOptionVarList(self,'cgmVar_DefaultOverrideColor')	
	guiFactory.appendOptionVarList(self,'cgmVar_RenameOnUpdate')	
	guiFactory.appendOptionVarList(self,'cgmVar_SizeMode')	
	guiFactory.appendOptionVarList(self,'cgmTDToolsWinActiveTab')
	
	#Click Surface
	self.ClickMeshBuildOptionVar = OptionVarFactory('cgmVar_ClickMeshBuild', defaultValue = 0)
	self.ClickMeshModeOptionVar = OptionVarFactory('cgmVar_ClickMeshMode', defaultValue = 0)
	self.ClickMeshClampOptionVar = OptionVarFactory('cgmVar_ClickMeshClamp', defaultValue = 0)
	self.ClickMeshTargetOptionVar = OptionVarFactory('cgmVar_ClickMeshTarget', defaultValue = [''])
	self.ClickMeshDragStoreOptionVar = OptionVarFactory('cgmVar_ClickMeshDragStore', defaultValue = 0)
	
	guiFactory.appendOptionVarList(self,self.ClickMeshBuildOptionVar.name)	
	guiFactory.appendOptionVarList(self,self.ClickMeshModeOptionVar.name)	
	guiFactory.appendOptionVarList(self,self.ClickMeshClampOptionVar.name)	
	guiFactory.appendOptionVarList(self,self.ClickMeshTargetOptionVar.name)	
	guiFactory.appendOptionVarList(self,self.ClickMeshDragStoreOptionVar.name)	

	
	#>>> Font Menu
	if not mc.optionVar( ex='cgmVar_FontOption' ):
	    mc.optionVar( sv=('cgmVar_FontOption', self.textObjectFont) )	
	if not mc.optionVar( ex='cgmVar_CustomFontOption' ):
	    mc.optionVar( sv=('cgmVar_CustomFontOption', self.textObjectFont) )	
	if not mc.optionVar( ex='cgmVar_ChangeFontOnUpdate' ):
	    mc.optionVar( iv=('cgmVar_ChangeFontOnUpdate', 1) )
		
	guiFactory.appendOptionVarList(self,'cgmVar_ChangeFontOnUpdate')	
	guiFactory.appendOptionVarList(self,'cgmVar_FontOption')	
	guiFactory.appendOptionVarList(self,'cgmVar_CustomFontOption')	
	
	#>>> axis variables
	if not mc.optionVar( ex='cgmVar_ObjectUpAxis' ):
	    mc.optionVar( sv=('cgmVar_ObjectUpAxis', 'y+') )
	if not mc.optionVar( ex='cgmVar_ObjectAimAxis' ):
	    mc.optionVar( sv=('cgmVar_ObjectAimAxis', 'z+') )
	if not mc.optionVar( ex='cgmVar_WorldUpAxis' ):
	    mc.optionVar( sv=('cgmVar_WorldUpAxis', 'y+') )
	    
	guiFactory.appendOptionVarList(self,'cgmVar_ObjectUpAxis')	
	guiFactory.appendOptionVarList(self,'cgmVar_ObjectAimAxis')	
	guiFactory.appendOptionVarList(self,'cgmVar_WorldUpAxis')

	self.uiCurveAxis = mc.optionVar(q='cgmVar_ObjectAimAxis')		


    def updateCurrentTab(self,optionVar):
	mc.optionVar( iv=(optionVar, self.getSelectedTabIdx()) )



    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Menus
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildOptionsMenu( self, *a ):
	self.UI_OptionsMenu.clear()
	
	FontMenu = MelMenuItem( self.UI_OptionsMenu, l='Font', subMenu=True)
	FontMenuCollection = MelRadioMenuCollection()

	fontOption = mc.optionVar( q='cgmVar_FontOption' )
	if mc.optionVar( q='cgmVar_FontOption' ) not in self.fontList:
	    pickedFontState = True
	else:
	    pickedFontState = False

	for font in self.fontList:
	    if not pickedFontState:
		if mc.optionVar( q='cgmVar_FontOption' ) == font:
		    fontState = True
		else:
		    fontState = False
	    else:
		fontState = False
	    FontMenuCollection.createButton(FontMenu,l=font,
	                                    c=('%s%s%s' %("mc.optionVar( sv=('cgmVar_FontOption','",font,"'))")),
	                                    rb = fontState)
	
	if mc.optionVar( q='cgmVar_FontOption' ) not in self.fontList:
	    customState = True
	else:
	    customState = False
	self.CustomFontButton = FontMenuCollection.createButton(FontMenu,l='Custom',
	                                                        c=('%s%s%s' %("mc.optionVar( sv=('cgmVar_FontOption','",mc.optionVar(q='cgmVar_CustomFontOption'),"'))")),
	                                                        rb = customState)	
	MelMenuItemDiv( FontMenu )
	MelMenuItem(FontMenu,l='Set Custom',
	            c=lambda *a: mc.optionVar( sv=('cgmVar_FontOption', guiFactory.doReturnFontFromDialog(fontOption))),
	            )

	# Size Menu
	SizeMenu = MelMenuItem( self.UI_OptionsMenu, l='Size', subMenu=True)
	SizeMenuCollection = MelRadioMenuCollection()

	for item in self.sizeOptions :
	    cnt = self.sizeOptions.index(item)
	    if mc.optionVar( q='cgmVar_SizeMode' ) == cnt:
		sizeModeState = True
	    else:
		sizeModeState = False
	    SizeMenuCollection.createButton(SizeMenu,l=item,
	                                    c= ("mc.optionVar( iv=('cgmVar_SizeMode',%i))" % cnt),
	                                    rb = sizeModeState)


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


	# Anim Menu
	AnimMenu = MelMenuItem( self.UI_OptionsMenu, l='Anim', subMenu=True)
	AnimMenuCollection = MelRadioMenuCollection()

	if mc.optionVar( q='cgmVar_ForceEveryFrame' ) == 0:
	    EveryFrameOption = False
	    KeysOnlyOption = True
	else:
	    EveryFrameOption = True
	    KeysOnlyOption = False

	AnimMenuCollection.createButton(AnimMenu,l='Every Frame',
	                                c=lambda *a: mc.optionVar( iv=('cgmVar_ForceEveryFrame', 1)),
	                                rb=EveryFrameOption )
	AnimMenuCollection.createButton(AnimMenu,l='Keys Only',
	                                c=lambda *a: mc.optionVar( iv=('cgmVar_ForceEveryFrame', 0)),
	                                rb=KeysOnlyOption )

	# Updating Options Menu
	UpdatingMenu = MelMenuItem( self.UI_OptionsMenu, l='Updating', subMenu=True)

	RenameOnUpdateState = mc.optionVar( q='cgmVar_RenameOnUpdate' )
	MelMenuItem( UpdatingMenu, l="Rename on Update",
	             cb=RenameOnUpdateState,
	             c= lambda *a: guiFactory.doToggleIntOptionVariable('cgmVar_RenameOnUpdate'))

	# Change font    
	ChangeFontOnUpdateState = mc.optionVar( q='cgmVar_ChangeFontOnUpdate' )		
	MelMenuItem( UpdatingMenu, l="Change font",
	             cb=ChangeFontOnUpdateState,
	             c= lambda *a: guiFactory.doToggleIntOptionVariable('cgmVar_ChangeFontOnUpdate'))

	
	# Autoloading options
	AutoloadMenu = MelMenuItem( self.UI_OptionsMenu, l='Auto Loading', subMenu=True)
	if not mc.optionVar( ex='cgmVar_AutoloadAutoname' ):
	    mc.optionVar( iv=('cgmVar_AutoloadAutoname', 0) )
	guiFactory.appendOptionVarList(self,'cgmVar_AutoloadAutoname')	
  
	RenameOnUpdateState = mc.optionVar( q='cgmVar_AutoloadAutoname' )
	MelMenuItem( AutoloadMenu, l="Autoname",
	             cb= mc.optionVar( q='cgmVar_AutoloadAutoname' ),
	             c= lambda *a: guiFactory.doToggleIntOptionVariable('cgmVar_AutoloadAutoname'))
	
	if not mc.optionVar( ex='cgmVar_AutoloadTextObject' ):
	    mc.optionVar( iv=('cgmVar_AutoloadTextObject', 0) )
	guiFactory.appendOptionVarList(self,'cgmVar_AutoloadTextObject')	

	RenameOnUpdateState = mc.optionVar( q='cgmVar_AutoloadTextObject' )
	MelMenuItem( AutoloadMenu, l="Text Objects",
	             cb= mc.optionVar( q='cgmVar_AutoloadTextObject' ),
	             c= lambda *a: guiFactory.doToggleIntOptionVariable('cgmVar_AutoloadTextObject'))

	MelMenuItemDiv( self.UI_OptionsMenu )
	
	MelMenuItemDiv( self.UI_OptionsMenu )
	MelMenuItem( self.UI_OptionsMenu, l="Reset",
	             c=lambda *a: guiFactory.resetGuiInstanceOptionVars(self.optionVars,run))
	
    def buildAxisMenu(self, *a ):
	self.UI_AxisMenu.clear()		

	# Object Aim Menu
	ObjectAimMenu = MelMenuItem( self.UI_AxisMenu, l='Object Aim', subMenu=True)
	self.ObjectAimCollection = MelRadioMenuCollection()

	for axis in self.axisOptions :
	    if mc.optionVar( q='cgmVar_ObjectAimAxis' ) == axis:
		checkState = True
	    else:
		checkState = False
	    self.ObjectAimCollection.createButton(ObjectAimMenu,l=axis,
	                                          c= ('%s%s%s' %("mc.optionVar( sv=('cgmVar_ObjectAimAxis','",axis,"'))")),
	                                          rb = checkState)

	# Object Up Menu
	ObjectUpMenu = MelMenuItem( self.UI_AxisMenu, l='Object Up', subMenu=True)
	self.ObjectUpCollection = MelRadioMenuCollection()

	for axis in self.axisOptions :
	    if mc.optionVar( q='cgmVar_ObjectUpAxis' ) == axis:
		checkState = True
	    else:
		checkState = False
	    self.ObjectUpCollection.createButton(ObjectUpMenu,l=axis,
	                                         c= ('%s%s%s' %("mc.optionVar( sv=('cgmVar_ObjectUpAxis','",axis,"'))")),
	                                         rb = checkState)

	# World Up Menu
	WorldUpMenu = MelMenuItem( self.UI_AxisMenu, l='World Up', subMenu=True)
	self.WorldUpCollection = MelRadioMenuCollection()

	for axis in self.axisOptions :
	    if mc.optionVar( q='cgmVar_WorldUpAxis' ) == axis:
		checkState = True
	    else:
		checkState = False
	    self.WorldUpCollection.createButton(WorldUpMenu,l=axis,
	                                        c= ('%s%s%s' %("mc.optionVar( sv=('cgmVar_WorldUpAxis','",axis,"'))")),
	                                        rb = checkState)
	MelMenuItem(self.UI_AxisMenu, l = 'Guess from selected', c = lambda *a: tdToolsLib.uiSetGuessOrientation(self))



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
    # Tab Layouts
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildTab_Curves(self,parent):
	ShowHelpOption = mc.optionVar( q='cgmVar_TDToolsShowHelp' )

	#>>>Main Form
	curvesMainFormLayout = MelFormLayout(parent)


	curvesLeftColumn = self.buildBasicLeftColumn(curvesMainFormLayout)
	curvesRightColumn = MelColumnLayout(curvesMainFormLayout)

	self.buildTool_TextObjectCreator(curvesRightColumn)
	self.buildTool_CurveCreator(curvesRightColumn)
	self.buildTool_CurveUtilities(curvesRightColumn)

	#>> Defining Main Form Layout
	curvesMainFormLayout(edit = True,
	                     attachForm = [(curvesLeftColumn,'left',0),
	                                   (curvesLeftColumn,'top',0),
	                                   (curvesRightColumn,'right',0),
	                                   (curvesRightColumn,'top',0),
	                                   ],
	                     attachControl = [(curvesRightColumn,'left',0,curvesLeftColumn)]

	                     )

    def buildTab_Position(self,parent):
	#>>>Main Form
	positionMainFormLayout = MelFormLayout(parent)


	positionLeftColumn = self.buildBasicLeftColumn(positionMainFormLayout)
	positionRightColumn = MelColumnLayout(positionMainFormLayout)
	
	self.buildTool_ClickMesh(positionRightColumn)

	self.buildTool_MoveTool(positionRightColumn)
	
	self.buildSnapAimTool(positionRightColumn)

	self.buildSnapToSurfaceTool(positionRightColumn)

	self.buildTool_GridLayout(positionRightColumn)
	
	self.buildTool_Constraints(positionRightColumn)

	#>> Defining Main Form Layout
	positionMainFormLayout(edit = True,
	                       attachForm = [(positionLeftColumn,'left',0),
	                                     (positionLeftColumn,'top',0),
	                                     (positionRightColumn,'right',0),
	                                     (positionRightColumn,'top',0),
	                                     ],
	                       attachControl = [(positionRightColumn,'left',0,positionLeftColumn)]

	                       )

    def buildTab_Info(self,parent):
	ShowHelpOption = mc.optionVar( q='cgmVar_TDToolsShowHelp' )

	#>>>Main Form
	InfoMainFormLayout = MelFormLayout(parent)


	InfoLeftColumn = self.buildBasicLeftColumn(InfoMainFormLayout)
	InfoRightColumn = MelColumnLayout(InfoMainFormLayout)

	self.buildBasicInfoTools(InfoRightColumn)

	#>> Defining Main Form Layout
	InfoMainFormLayout(edit = True,
	                   attachForm = [(InfoLeftColumn,'left',0),
	                                 (InfoLeftColumn,'top',0),
	                                 (InfoRightColumn,'right',0),
	                                 (InfoRightColumn,'top',0),
	                                 ],
	                   attachControl = [(InfoRightColumn,'left',0,InfoLeftColumn)]

	                   )
    def buildTab_Joints(self,parent):
	ShowHelpOption = mc.optionVar( q='cgmVar_TDToolsShowHelp' )

	#>>>Main Form
	JointsMainFormLayout = MelFormLayout(parent)


	JointsLeftColumn = self.buildBasicLeftColumn(JointsMainFormLayout)
	JointsRightColumn = MelColumnLayout(JointsMainFormLayout)

	self.buildTools_Joints(JointsRightColumn)

	#>> Defining Main Form Layout
	JointsMainFormLayout(edit = True,
	                   attachForm = [(JointsLeftColumn,'left',0),
	                                 (JointsLeftColumn,'top',0),
	                                 (JointsRightColumn,'right',0),
	                                 (JointsRightColumn,'top',0),
	                                 ],
	                   attachControl = [(JointsRightColumn,'left',0,JointsLeftColumn)]

	                   )
	
    def buildTab_Attributes(self,parent):
	ShowHelpOption = mc.optionVar( q='cgmVar_TDToolsShowHelp' )

	#>>>Main Form
	AttributeMaAttributermLayout = MelFormLayout(parent)


	AttributeLeftColumn = self.buildBasicLeftColumn(AttributeMaAttributermLayout)
	AttributeRightColumn = MelColumnLayout(AttributeMaAttributermLayout)

	self.buildAttributeUtilityTools(AttributeRightColumn)

	#>> Defining Main Form Layout
	AttributeMaAttributermLayout(edit = True,
	                             attachForm = [(AttributeLeftColumn,'left',0),
	                                           (AttributeLeftColumn,'top',0),
	                                           (AttributeRightColumn,'right',0),
	                                           (AttributeRightColumn,'top',0),
	                                           ],
	                             attachControl = [(AttributeRightColumn,'left',0,AttributeLeftColumn)]

	                             )

    def buildTab_Deformer(self,parent):
	#Options
	OptionList = ['skinCluster','blendshape','utilities']
	cgmVar_Name = 'cgmVar_DeformerMode'
	guiFactory.appendOptionVarList(self,'cgmVar_DeformerMode')	
	
	RadioCollectionName ='DeformerMode'
	RadioOptionList = 'DeformerModeSelectionChoicesList'
	ModeSetRow = 'DeformerModeSetRow'

	ShowHelpOption = mc.optionVar( q='cgmVar_TDToolsShowHelp' )
	if not mc.optionVar( ex=cgmVar_Name ):
	    mc.optionVar( sv=(cgmVar_Name, OptionList[0]) )


	#self.buildModeSetUtilityRow(parent,'DeformerMode','DeformerModeChoices', SectionLayoutCommands, 'cgmVar_DeformerMode',modesToToggle, labelText = 'Choose Mode: ')

	#Start layout
	mc.setParent(parent)
	guiFactory.header('What are we workin with?')
	guiFactory.lineSubBreak()

	ModeSetRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
	MelLabel(ModeSetRow, label = 'Choose Mode: ',align='right')
	self.RadioCollectionName = MelRadioCollection()
	self.RadioOptionList = []

	#Start actual layout
	self.buildLoadObjectTargetTool(parent)

	#build our sub sesctions
	self.ContainerList = []

	self.ContainerList.append( self.buildTool_SkinCluster(parent,vis=False) )
	self.ContainerList.append( self.buildBlendshapeTool( parent,vis=False) )
	self.ContainerList.append( self.buildUtilitiesTool( parent,vis=False) )

	for item in OptionList:
	    self.RadioOptionList.append(self.RadioCollectionName.createButton(ModeSetRow,label=item,
	                                                                      onCommand = Callback(guiFactory.toggleModeState,item,OptionList,cgmVar_Name,self.ContainerList)))
	ModeSetRow.layout()


	mc.radioCollection(self.RadioCollectionName,edit=True, sl=self.RadioOptionList[OptionList.index(mc.optionVar(q=cgmVar_Name))])


    def buildTab_Naming(self,parent):
	#Options
	OptionList = ['autoname','standard']
	guiFactory.appendOptionVarList(self,'cgmVar_NamingMode')	

	cgmVar_Name = 'cgmVar_NamingMode'
	RadioCollectionName ='NamingMode'
	RadioOptionList = 'NamingModeSelectionChoicesList'
	ModeSetRow = 'DeformerModeSetRow'

	ShowHelpOption = mc.optionVar( q='cgmVar_TDToolsShowHelp' )
	if not mc.optionVar( ex=cgmVar_Name ):
	    mc.optionVar( sv=(cgmVar_Name, OptionList[0]) )


	#Start layout
	ModeSetRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
	MelLabel(ModeSetRow, label = 'Choose Mode: ',align='right')
	self.RadioCollectionName = MelRadioCollection()
	self.RadioOptionList = []

	#build our sub sesctions
	self.ContainerList = []

	self.ContainerList.append( self.buildAutoNameTool(parent,vis=False) )
	self.ContainerList.append( self.buildStandardNamingTool(parent,vis=False) )

	for item in OptionList:
	    self.RadioOptionList.append(self.RadioCollectionName.createButton(ModeSetRow,label=item,
	                                                                      onCommand = Callback(guiFactory.toggleModeState,item,OptionList,cgmVar_Name,self.ContainerList)))
	ModeSetRow.layout()

	mc.radioCollection(self.RadioCollectionName,edit=True, sl=self.RadioOptionList[OptionList.index(mc.optionVar(q=cgmVar_Name))])



    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Sections of gui stuff
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildBasicLeftColumn(self,parent):
	ShowHelpOption = mc.optionVar( q='cgmVar_TDToolsShowHelp' )
	LeftColumn = MelColumnLayout(parent, cw = 100)
	guiFactory.header('Set Color')

	mc.columnLayout(columnAttach = ('both',5),backgroundColor = [.2,.2,.2])
	colorSwatchMenu = mc.gridLayout(aec = False, numberOfRowsColumns=(10,3), cwh = (30,14),backgroundColor = [.2,.2,.2])
	colorSwatchesList = [1,2,3,11,24,21,12,10,25,4,13,20,8,30,9,5,6,18,15,29,28,7,27,19,23,26,14,17,22,16]
	for i in colorSwatchesList:
	    colorBuffer = mc.colorIndex(i, q=True)
	    mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=colorBuffer,
	              pc = ('%s%i%s' %("from cgm.tools.lib import tdToolsLib;tdToolsLib.doSetCurveColorByIndex(",i,")")),
	              annotation = 'Sets the color of the object to this')
	    mc.popupMenu(button = 3)
	    mc.menuItem(label = 'Set as default',
	                c = ('%s%i%s' %("mc.optionVar( iv=('cgmVar_DefaultOverrideColor',",i,"))")))

	mc.setParent('..')
	mc.setParent('..')

	guiFactory.header('Transforms')

	guiFactory.lineSubBreak()
	guiFactory.doButton2(LeftColumn,'Group Me',
	                     'from cgm.lib import rigging;rigging.groupMe()',
	                     "Groups selected under a tranform at their current position")

	guiFactory.doButton2(LeftColumn,'Group In place', 
	                     lambda *a:tdToolsLib.doGroupMeInPlace(),
	                     "Groups an object while maintaining its parent\n if it has one")

	guiFactory.doButton2(LeftColumn,'Zero Me',
	                     lambda *a:tdToolsLib.zeroGroupMe(),
	                     'Zeros out object under group')

	guiFactory.doButton2(LeftColumn,'Transform Here',
	                     lambda *a:tdToolsLib.makeTransformHere(),
	                     'Create transform matching object')

	guiFactory.lineSubBreak()
	guiFactory.doButton2(LeftColumn,'Parent Selected',
	                     lambda *a:tdToolsLib.doParentSelected(),
	                     'Parents a list in order')
	
	guiFactory.lineSubBreak()
	guiFactory.doButton2(LeftColumn,'Copy Pivot',
	                     lambda *a:tdToolsLib.doCopyPivot(),
	                     'Copy pivot from first selection to all other objects')

	guiFactory.lineSubBreak()
	guiFactory.doButton2(LeftColumn,'Loc Me',
	                     lambda *a:locinatorLib.doLocMe(self),
	                     'Creates loc at object, matching trans,rot and rotOrd')

	guiFactory.lineSubBreak()
	"""
		guiFactory.doButton2(LeftColumn,'updateLoc',
		                     lambda *a:locinatorLib.doUpdateLoc(self,True),
				             'Updates loc or object connected to loc base don selection. See cgmLocinator for more options')
		"""
	return LeftColumn

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Curve Stuff
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildCurveControlOptionsRow(self,parent):	
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Connection Types
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>	
	self.HeirBuildTypes = ['match','maintain']
	self.HeirBuildTypesRadioCollection = MelRadioCollection()
	self.HeirBuildTypesRadioCollectionChoices = []	
	if not mc.optionVar( ex='cgmVar_HeirBuildType' ):
	    mc.optionVar( iv=('cgmVar_HeirBuildType', 0) )
	guiFactory.appendOptionVarList(self,'cgmVar_HeirBuildType')	
	    
	#build our sub section options
	CurveControlOptionsTypeRow = MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 2)
	#CurveControlOptionsTypeRow.setStretchWidget( MelSpacer(CurveControlOptionsTypeRow,w=5) )
	#MelLabel(CurveControlOptionsTypeRow,l='Options: ',align='right')
	#CurveControlOptionsTypeRow.setStretchWidget( MelLabel(CurveControlOptionsTypeRow,l='Options: ',align='right') )
	MelSpacer(CurveControlOptionsTypeRow,w=10)
	self.controlCurveRotateOrderCB = guiFactory.doCheckBox(self,CurveControlOptionsTypeRow,'cgmVar_RotationOrderCurveControlOptionState',label = 'Rotate Order')
	
	MelSpacer(CurveControlOptionsTypeRow,w=2)   
	self.CurveControlExtraGroupCB = guiFactory.doCheckBox(self,CurveControlOptionsTypeRow,'cgmVar_ExtraGroupCurveControlOptionState',label = '+Group')
	
	MelSpacer(CurveControlOptionsTypeRow,w=2)   
	self.CurveControlLockNHideCB = guiFactory.doCheckBox(self,CurveControlOptionsTypeRow,'cgmVar_LockNHideControlOptionState',label = 'LockNHide')
	
	CurveControlOptionsTypeRow.setStretchWidget( MelSpacer(CurveControlOptionsTypeRow) )	
	
	self.CurveControlHeirarchyCB = guiFactory.doCheckBox(self,CurveControlOptionsTypeRow,'cgmVar_MaintainHeirarchyCurveControlOptionState',label = 'Heir: ')
	
	for item in self.HeirBuildTypes:
	    cnt = self.HeirBuildTypes.index(item)
	    self.HeirBuildTypesRadioCollectionChoices.append(self.HeirBuildTypesRadioCollection.createButton(CurveControlOptionsTypeRow,
	                                                                                                     label=self.HeirBuildTypes[cnt],
	                                                                                                     onCommand = ('%s%i%s' %("mc.optionVar( iv=('cgmVar_HeirBuildType',",cnt,"))"))))
	    

	MelSpacer(CurveControlOptionsTypeRow,w=8)	
	CurveControlOptionsTypeRow.layout()
	
	mc.radioCollection(self.HeirBuildTypesRadioCollection,edit=True,
	                   sl= (self.HeirBuildTypesRadioCollectionChoices[ mc.optionVar(q='cgmVar_HeirBuildType') ]))
    
    def buildConstraintTypeRow(self,parent):	
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Connection Types
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	self.ConstraintTypes = ['parent','point/orient','point','orient']
	self.containerName = MelColumn(parent)	
	self.CreateConstraintTypeRadioCollection = MelRadioCollection()
	self.CreateConstraintTypeRadioCollectionChoices = []		
	if not mc.optionVar( ex='cgmVar_ControlConstraintType' ):
	    mc.optionVar( iv=('cgmVar_ControlConstraintType', 0) )
	    
	guiFactory.appendOptionVarList(self,'cgmVar_ControlConstraintType')	

	#build our sub section options
	ConstraintTypeRow = MelHSingleStretchLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
	ConstraintTypeRow.setStretchWidget(MelLabel(ConstraintTypeRow,l='Constraint: ',align='right'))
	for item in self.ConstraintTypes:
	    cnt = self.ConstraintTypes.index(item)
	    self.CreateConstraintTypeRadioCollectionChoices.append(self.CreateConstraintTypeRadioCollection.createButton(ConstraintTypeRow,label=self.ConstraintTypes[cnt],
	                                                                                                                 onCommand = ('%s%i%s' %("mc.optionVar( iv=('cgmVar_ControlConstraintType',",cnt,"))"))))
	    MelSpacer(ConstraintTypeRow,w=5)
	self.ScaleConstraintCB = guiFactory.doCheckBox(self,ConstraintTypeRow,'cgmVar_ScaleConstratingState',label = 'scale')	                                    
	MelSpacer(ConstraintTypeRow,w=25) 
	
	ConstraintTypeRow.layout()
	
	
	mc.radioCollection(self.CreateConstraintTypeRadioCollection ,edit=True,sl= (self.CreateConstraintTypeRadioCollectionChoices[ mc.optionVar(q='cgmVar_ControlConstraintType') ]))


    def buildConnectionTypeRow(self,parent):	
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Connection Types
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	self.ConnectionTypes = ['Constrain','ShapeParent','Parent','ChildOf']
	self.containerName = MelColumn(parent)	
	self.CreateConnectionTypeRadioCollection = MelRadioCollection()
	self.CreateConnectionTypeRadioCollectionChoices = []		
	if not mc.optionVar( ex='cgmVar_ControlConnectionType' ):
	    mc.optionVar( iv=('cgmVar_ControlConnectionType', 0) )
	guiFactory.appendOptionVarList(self,'cgmVar_ControlConnectionType')	

	#build our sub section options
	ConnectionTypeRow = MelHSingleStretchLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
	ConnectionTypeRow.setStretchWidget(MelLabel(ConnectionTypeRow,l='Mode: ',align='right'))
	for item in self.ConnectionTypes:
	    cnt = self.ConnectionTypes.index(item)
	    self.CreateConnectionTypeRadioCollectionChoices.append(self.CreateConnectionTypeRadioCollection.createButton(ConnectionTypeRow,label=self.ConnectionTypes[cnt],
	                                                                                                                 onCommand = ('%s%i%s' %("mc.optionVar( iv=('cgmVar_ControlConnectionType',",cnt,"))"))))
	    MelSpacer(ConnectionTypeRow,w=5)
	MelSpacer(ConnectionTypeRow,w=50)
	
	ConnectionTypeRow.layout()
	
	
	mc.radioCollection(self.CreateConnectionTypeRadioCollection ,edit=True,sl= (self.CreateConnectionTypeRadioCollectionChoices[ mc.optionVar(q='cgmVar_ControlConnectionType') ]))




    def buildTool_CurveCreator(self,parent):
	makeCurvesContainer = MelColumnLayout(parent, ut='cgmUISubTemplate')
	guiFactory.header('Curve Controls')
	guiFactory.lineSubBreak()

	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Line 1
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	OptionsRow = MelHSingleStretchLayout(makeCurvesContainer,padding = 5)
	MelSpacer(OptionsRow)
	MelLabel(OptionsRow, l='Name')
	self.uiCurveNameField = MelTextField(OptionsRow)

	MelLabel(OptionsRow, l='Pick Shape')
	self.shapeOptions = MelOptionMenu(OptionsRow)
	for item in self.curveOptionList:
	    self.shapeOptions.append(item)


	MelSpacer(OptionsRow)

	OptionsRow.setStretchWidget(self.uiCurveNameField)
	OptionsRow.layout()


	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Line 3
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	mc.setParent(makeCurvesContainer)
	MasterControlSettingsRow = MelHLayout(makeCurvesContainer,ut='cgmUISubTemplate',padding = 2)

	MelLabel(MasterControlSettingsRow,label = 'Master Control:',align='right')
	
	self.MakeMasterControlCB = guiFactory.doCheckBox(self,MasterControlSettingsRow,'cgmVar_MakeMasterControl',label = 'Master')
	self.MakeVisControlCB = guiFactory.doCheckBox(self,MasterControlSettingsRow,'cgmVar_MakeMasterSettings',label = 'Vis')
	self.MakeSettingsControlCB = guiFactory.doCheckBox(self,MasterControlSettingsRow,'cgmVar_MakeMasterVis',label = 'Settings')
	self.MakeGroupsCB = guiFactory.doCheckBox(self,MasterControlSettingsRow,'cgmVar_MakeMasterGroups',label = 'Groups')
	
	MasterControlSettingsRow.layout()


	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Line 3 - Connect
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	self.buildConnectionTypeRow(makeCurvesContainer)
	self.buildConstraintTypeRow(makeCurvesContainer)
	self.buildCurveControlOptionsRow(makeCurvesContainer)
	
	buttonRow = MelHLayout(makeCurvesContainer,ut='cgmUISubTemplate',padding = 2)
	guiFactory.doButton2(buttonRow,'Create',
	                     lambda *a:tdToolsLib.curveControlCreate(self),
	                     'Create Curve Object with Settings',w=50)

	guiFactory.doButton2(buttonRow,'Connect',
	                     lambda *a:tdToolsLib.curveControlConnect(self),
	                     'Connects our control')
	guiFactory.doButton2(buttonRow,'Create one of each',
	                     lambda *a:tdToolsLib.doCreateOneOfEachCurve(self),
	                     'Creates one of each curve in the library')
	buttonRow.layout()


	mc.setParent(makeCurvesContainer)
	guiFactory.lineSubBreak()


    def buildTool_TextObjectCreator(self,parent):
	guiFactory.header('Text Objects')
	textObjectColumn = MelColumnLayout(parent, ut='cgmUISubTemplate', cw = 100)
	guiFactory.lineSubBreak()

	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Line 1
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	TextInfoRow = MelHSingleStretchLayout(textObjectColumn,padding = 5)
	MelSpacer(TextInfoRow)

	MelLabel(TextInfoRow,l='Text')
	self.textObjectTextField = MelTextField(TextInfoRow,backgroundColor = [1,1,1],
	                                        annotation = "Text for the text object. Create multiple with a ';'. \n For example: 'Test1;Test2;Test3'")
	MelLabel(TextInfoRow,l='Size')
	self.textObjectSizeField = MelFloatField(TextInfoRow,width = 50, min = 0,value=1,backgroundColor = [1,1,1])
	MelSpacer(TextInfoRow)

	TextInfoRow.setStretchWidget(self.textObjectTextField)
	TextInfoRow.layout()

	mc.setParent(textObjectColumn)
	guiFactory.lineBreak()
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Line 2
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	currentObjectRow = MelHSingleStretchLayout(textObjectColumn,padding = 5)
	MelSpacer(currentObjectRow)
	guiTextObjLoadButton = guiFactory.doButton2(currentObjectRow,'>>',
	                                            lambda *a:tdToolsLib.TextCurveObjectdoLoad(self),
	                                            'Load to field')
	self.textCurrentObjectField = MelTextField(currentObjectRow, ut = 'cgmUIReservedTemplate', editable = False)

	guiTextObjUpdateButton = guiFactory.doButton2(currentObjectRow,'Update',
	                                              lambda *a:tdToolsLib.TextCurveObjectdoUpdate(self),
	                                              'Updates selected text curve objects\n or the loaded text curve object')
	guiTextObjUpdateButton = guiFactory.doButton2(currentObjectRow,'Create',
	                                              lambda *a:tdToolsLib.TextCurveObjectCreate(self),
	                                              'Create a text object with the provided settings')
	
	MelSpacer(currentObjectRow,w=5)
	currentObjectRow.setStretchWidget(self.textCurrentObjectField)
	currentObjectRow.layout()

	mc.setParent(textObjectColumn)
	guiFactory.lineSubBreak()

	mc.setParent(parent)
	guiFactory.lineSubBreak()


    def buildTool_CurveUtilities(self,parent):
	mc.setParent(parent)
	guiFactory.header('Curve Utilities')
	guiFactory.lineSubBreak()

	curveUtilitiesRow1 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(curveUtilitiesRow1,'shpPrnt',
	                     lambda *a:tdToolsLib.doShapeParent(),
	                     "Maya's standard shape parent")
	guiFactory.doButton2(curveUtilitiesRow1,'shpPrnt in Place',
	                     lambda *a:tdToolsLib.doShapeParentInPlace(),
	                     'shapeParents a curve in place/nFrom to relationship')
	guiFactory.doButton2(curveUtilitiesRow1,'Replace Shapes',
	                     lambda *a:tdToolsLib.doReplaceCurveShapes(),
	                     'Replaces the shapes of the last object with those\nof the other objects')


	curveUtilitiesRow1.layout()

	mc.setParent(parent)
	guiFactory.lineSubBreak()


	curveUtilitiesRow2 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)
	guiFactory.doButton2(curveUtilitiesRow2,'Objects to Crv',
	                     lambda *a:tdToolsLib.doCreateCurveFromObjects(),
	                     'Creates a curve through the pivots of objects')
	guiFactory.doButton2(curveUtilitiesRow2,'Crv to Python',
	                     lambda *a:tdToolsLib.doCurveToPython(),
	                     'Creates a python command to recreate a curve')
	guiFactory.doButton2(curveUtilitiesRow2,'Combine Curves',
	                     lambda *a:tdToolsLib.doCombineCurves(),
	                     'Combines curves')

	curveUtilitiesRow2.layout()

	mc.setParent(parent)
	guiFactory.lineSubBreak()

	curveUtilitiesRow3 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)
	guiFactory.doButton2(curveUtilitiesRow3,'Loc CVs of curve',
	                     lambda *a:locinatorLib.doLocCVsOfObject(),
	                     "Locs the CVs at the cv coordinates")

	guiFactory.doButton2(curveUtilitiesRow3,'Loc CVs on the curve',
	                     lambda *a:locinatorLib.doLocCVsOnObject(),
	                     "Locs CVs at closest point on the curve")


	mc.setParent(parent)
	guiFactory.lineSubBreak()

	curveUtilitiesRow3.layout()

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Position Tools
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildTool_MoveTool(self,parent):
	mc.setParent(parent)
	guiFactory.header('Snap Move')
	guiFactory.lineSubBreak()

	snapMoveRow1 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(snapMoveRow1,'Parent',
	                     lambda *a:tdToolsLib.doParentSnap(),
	                     'Parent snap one objects to a target')
	guiFactory.doButton2(snapMoveRow1,'Point',
	                     lambda *a:tdToolsLib.doPointSnap(),
	                     "Point snap one objects to a target")
	guiFactory.doButton2(snapMoveRow1,'Orient',
	                     lambda *a:tdToolsLib.doOrientSnap(),
	                     'Orient snap one objects to a target')

	mc.setParent(parent)
	guiFactory.lineSubBreak()

	snapMoveRow1.layout()
	
    def buildTool_ClickMesh(self,parent):
	mc.setParent(parent)
	guiFactory.header('Click Mesh')
	guiFactory.lineSubBreak()
	
	#>>>Click Mode
	self.ClickMeshCreateModeCollection = MelRadioCollection()
	self.ClickMeshCreateModeCollectionChoices = []	
	
	ClickMeshCreateModeOptionsRow = MelHSingleStretchLayout(parent,padding = 2,ut='cgmUISubTemplate')
	MelSpacer(ClickMeshCreateModeOptionsRow,w=2)	
	MelLabel(ClickMeshCreateModeOptionsRow,l='Mode')
	Spacer = MelSeparator(ClickMeshCreateModeOptionsRow,w=2)						
	self.ClickMeshOptions = ['surface','bisect','midPoint']
	for i,item in enumerate(self.ClickMeshOptions):
	    self.ClickMeshCreateModeCollectionChoices.append(self.ClickMeshCreateModeCollection.createButton(ClickMeshCreateModeOptionsRow,label=item,                                                                                           
	                                                                                                           onCommand = Callback(tdToolsLib.uiClickMesh_changeMode,self,i)))
	    #MelSpacer(ClickMeshCreateModeOptionsRow,w=3)
	ClickMeshCreateModeOptionsRow.setStretchWidget( Spacer )

	self.ClickMeshDragCB = MelCheckBox(ClickMeshCreateModeOptionsRow,
	                                   label = 'Drag:',
	                                   annotation = "Stores drag data rather than just clicks",		                           
	                                   value = self.ClickMeshDragStoreOptionVar.value,
	                                   onCommand = lambda *a: tdToolsLib.uiClickMesh_setDragStore(self,1),
	                                   offCommand = lambda *a: tdToolsLib.uiClickMesh_setDragStore(self,0))
	

	MelLabel(ClickMeshCreateModeOptionsRow,l='Clamp:')
	
	self.ClickMeshClampIntField = MelIntField(ClickMeshCreateModeOptionsRow,
	                                          cc = lambda *a: tdToolsLib.uiClickMesh_setClamp(self))	

	tdToolsLib.uiUpdate_ClickMeshClampField(self) #update the field with a value if we have it
	
	MelSpacer(ClickMeshCreateModeOptionsRow,w=2)		
	ClickMeshCreateModeOptionsRow.layout()	
	
	mc.radioCollection(self.ClickMeshCreateModeCollection ,edit=True,sl= (self.ClickMeshCreateModeCollectionChoices[ (self.ClickMeshModeOptionVar.value) ]))
	
	#>>>Create Options
	self.ClickMeshBuildCollection = MelRadioCollection()
	self.ClickMeshBuildCollectionChoices = []	
	
	ClickMeshBuildOptionsRow = MelHSingleStretchLayout(parent,padding = 2,ut='cgmUISubTemplate')
	MelSpacer(ClickMeshBuildOptionsRow,w=3)	
	MelLabel(ClickMeshBuildOptionsRow,l='Create')
	Spacer = MelSeparator(ClickMeshBuildOptionsRow,w=10)						
	self.ClickMeshOptions = ['locator','joint','jointChain','curve','follicle','group']
	for i,item in enumerate(self.ClickMeshOptions):
		self.ClickMeshBuildCollectionChoices.append(self.ClickMeshBuildCollection.createButton(ClickMeshBuildOptionsRow,label=item,                                                                                           
		                                                                                       onCommand = Callback(tdToolsLib.uiClickMesh_changeCreateMode,self,i)))
		MelSpacer(ClickMeshBuildOptionsRow,w=3)
	ClickMeshBuildOptionsRow.setStretchWidget( Spacer )
	MelSpacer(ClickMeshBuildOptionsRow,w=2)		
	ClickMeshBuildOptionsRow.layout()	
	
	mc.radioCollection(self.ClickMeshBuildCollection ,edit=True,sl= (self.ClickMeshBuildCollectionChoices[ (self.ClickMeshBuildOptionVar.value) ]))
	
	
	#>>> Manager load frow
	ClickMeshLoadObjectRow = MelHSingleStretchLayout(parent ,padding = 5,ut='cgmUISubTemplate')

	MelSpacer(ClickMeshLoadObjectRow,w=5)
	
	guiFactory.doButton2(ClickMeshLoadObjectRow,'>>',
                        lambda *a:tdToolsLib.uiLoadClickMeshTargets(self),
	                'Load to field')
	
	self.ClickMeshTargetsField = MelTextField(ClickMeshLoadObjectRow, w= 125, h=20, ut = 'cgmUIReservedTemplate', editable = False,
	                                             ann = 'Target for tool. Objects must be mesh')

	tdToolsLib.uiUpdate_ClickMeshTargetField(self) #update the field with a value if we have it
	
	ClickMeshLoadObjectRow.setStretchWidget(self.ClickMeshTargetsField  )
	
	guiFactory.doButton2(ClickMeshLoadObjectRow,'Start',
	                     lambda *a:tdToolsLib.uiClickMeshToolLaunch(self))
	
	guiFactory.doButton2(ClickMeshLoadObjectRow,'Drop',
	                     lambda *a:tdToolsLib.uiClickMesh_dropTool(self),
	                     "Drop the tool. 'Q' should work on default hotkey setups")
	
	MelSpacer(ClickMeshLoadObjectRow,w=5)

	ClickMeshLoadObjectRow.layout()
	
	

	mc.setParent(parent)
	guiFactory.lineSubBreak()

	
    def buildSnapAimTool(self,parent):
	mc.setParent(parent)
	guiFactory.header('Snap Aim')
	guiFactory.lineSubBreak()


	snapAimButton = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)


	MelButton(snapAimButton,l='One to Next',ut = 'cgmUITemplate',
	          c = lambda *a:tdToolsLib.doAimSnapOneToNext(),
	          annotation = 'Aims a list of objects one to the /n next in a parsed list of pairs')
	MelButton(snapAimButton,l='All to Last',ut = 'cgmUITemplate',
	          c=lambda *a:tdToolsLib.doAimSnapToOne(),
	          annotation = "Aims all of the objects in a selection set/n to the last object")


	mc.setParent(parent)
	guiFactory.lineSubBreak()

	snapAimButton.layout()


    def buildSnapToSurfaceTool(self,parent):
	mc.setParent(parent)
	guiFactory.header('Snap To Surface')
	guiFactory.lineSubBreak()

	self.buildSurfaceSnapAimRow(parent)

	snapToSurfaceButton = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(snapToSurfaceButton,'Just Snap',
	                     lambda *a:tdToolsLib.doSnapClosestPointToSurface(False),
	                     'Aims a list of objects one to the /n next in a parsed list of pairs')
	guiFactory.doButton2(snapToSurfaceButton,'Snap and Aim',
	                     lambda *a:tdToolsLib.doSnapClosestPointToSurface(),
	                     'Aims a list of objects one to the /n next in a parsed list of pairs')


	mc.setParent(parent)
	guiFactory.lineSubBreak()

	snapToSurfaceButton.layout()

    def buildTool_GridLayout(self,parent):
	mc.setParent(parent)
	guiFactory.header('Grid Layout')
	guiFactory.lineSubBreak()

	self.buildRowColumnUIRow(parent)

	mc.setParent(parent)
	guiFactory.lineSubBreak()

	GridLayoutButtonRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(GridLayoutButtonRow,'Do it!',
	                     lambda *a:tdToolsLib.doLayoutByRowsAndColumns(self),
	                     'Lays out the selected in a grid format\nby the number of columns input\nfrom the position of the last object selected')


	GridLayoutButtonRow.layout()

    def buildTool_Constraints(self,parent):
	mc.setParent(parent)
	guiFactory.header('Constraints')
	guiFactory.lineSubBreak()


	ConstraintsButtonRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(ConstraintsButtonRow,'JTD Dynamic Parent Constraint GUI',
	                     lambda *a:tdToolsLib.loadJTDDynamicParent(),
	                     'Dynamic Constraint Tool\n by John Doublestein')


	ConstraintsButtonRow.layout()
	mc.setParent(parent)
	guiFactory.lineSubBreak()	

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Info Tools
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildTools_Joints(self,parent):
	mc.setParent(parent)
	guiFactory.header('Joint Utilities')
	guiFactory.lineSubBreak()

	Row1 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)
	guiFactory.doButton2(Row1,'move Mirror Selected Joints TEMP',
	                     lambda *a: mel.eval('jbMirrorSelectedJoints'),
	                     "Temporary mirror joint tool")

	guiFactory.doButton2(Row1,'cometJointOrient',
	                     lambda *a: mel.eval('cometJointOrient'),
	                     "General Joint orientation tool\n by Michael Comet")

	mc.setParent(parent)
	guiFactory.lineSubBreak()

	Row1.layout()
	
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Joint Tools
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def buildBasicInfoTools(self,parent):
	mc.setParent(parent)
	guiFactory.header('Basic Info')
	guiFactory.lineSubBreak()

	BasicInfoRow1 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(BasicInfoRow1,'What am I',
	                     lambda *a:tdToolsLib.doReportObjectType(),
	                     'Reports what cgmThinga thinks the object is')
	guiFactory.doButton2(BasicInfoRow1,'Count Selected',
	                     lambda *a:tdToolsLib.doReportSelectionCount(),
	                     'Reports what cgmThinga thinks the object is')

	mc.setParent(parent)
	guiFactory.lineSubBreak()

	BasicInfoRow1.layout()

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Attribute Tools
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildAttributeUtilityTools(self,parent):
	mc.setParent(parent)
	guiFactory.header('Attribute Utilities')
	guiFactory.lineSubBreak()

	AttributeUtilityRow1 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(AttributeUtilityRow1,'cgmName to Float',
	                     lambda *a:tdToolsLib.doCGMNameToFloat(),
	                     'Makes an animatalbe float attribute using the cgmName tag')


	mc.setParent(parent)
	guiFactory.lineSubBreak()

	AttributeUtilityRow1.layout()

	#>>> SDK tools
	mc.setParent(parent)
	guiFactory.lineBreak()
	guiFactory.header('SDK Tools')
	guiFactory.lineSubBreak()


	sdkRow = MelHLayout(parent ,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(sdkRow,'Graph SDK Attr',
	                     lambda *a: mel.eval('jbGraphSetDrivenAttribute'),
	                     "Loads an SDK to the graph editor")
	
	guiFactory.doButton2(sdkRow,'Select Driven Joints',
	                     lambda *a:tdToolsLib.doSelectDrivenJoints(self),
	                     "Selects driven joints from an sdk attribute")

	guiFactory.doButton2(sdkRow,'seShapeTaper',
	                     lambda *a: mel.eval('seShapeTaper'),
	                     "Mirror splits of joint poses for joint based facial\n by Scott Englert")

	sdkRow.layout()
	mc.setParent(parent)
	guiFactory.lineSubBreak()


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Deformer Tools
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildTool_SkinCluster(self,parent, vis=True):
	containerName = 'SkinClusterContainer'
	self.containerName = MelColumn(parent,vis=vis)

	mc.setParent(self.containerName)
	guiFactory.header('Query')
	guiFactory.lineSubBreak()


	#>>> Find excess weights Tool
	FindExcessVertsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5)
	MelSpacer(FindExcessVertsRow,w=10)
	MelLabel(FindExcessVertsRow,l='Find verts with excess influence',align='left')

	FindExcessVertsRow.setStretchWidget(MelLabel(FindExcessVertsRow,l='>>>'))

	MelLabel(FindExcessVertsRow,l='Max Verts:')

	self.MaxVertsField = MelIntField(FindExcessVertsRow, w= 50, v=3)

	guiFactory.doButton2(FindExcessVertsRow,'Find em!',
	                     lambda *a: tdToolsLib.doReturnExcessInfluenceVerts(self),
	                     'Finds excess vertices')
	MelSpacer(FindExcessVertsRow,w=10)
	FindExcessVertsRow.layout()

	mc.setParent(self.containerName)
	guiFactory.lineSubBreak()

	#>>> Influence tools
	InfluencesRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
	guiFactory.doButton2(InfluencesRow,'Select Influences',
	                     lambda *a:tdToolsLib.doSelectInfluenceJoints(),
	                     "Selects the influences of selected objects with skin clusters.")
	InfluencesRow.layout()
	mc.setParent(self.containerName)
	guiFactory.lineSubBreak()

	#>>> Weight Copying tools
	mc.setParent(self.containerName)
	guiFactory.header('Copy')
	guiFactory.lineSubBreak()


	SkinWeightsCopyRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
	guiFactory.doButton2(SkinWeightsCopyRow,'First component to others',
	                     lambda *a:tdToolsLib.doCopyWeightsFromFirstToOthers(),
	                     "Copies the weights from one vert to another.")
	guiFactory.doButton2(SkinWeightsCopyRow,'Vert from closest', 
	                     lambda *a:tdToolsLib.doCopySkinningToVertFromSource(),
	                     "Copies the weights to a vert from \n the closest vert on the source.")
	guiFactory.doButton2(SkinWeightsCopyRow,'Object to objects', 
	                     lambda *a:tdToolsLib.doTransferSkinning(),
	                     "Copies the weights from one object to others.")

	SkinWeightsCopyRow.layout()
	mc.setParent(self.containerName)
	guiFactory.lineSubBreak()
	guiFactory.lineBreak()

	#>>> Weight Utility tools
	mc.setParent(self.containerName)
	guiFactory.header('Utilities')
	guiFactory.lineSubBreak()


	SkinWeightsUtilitiesRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(SkinWeightsUtilitiesRow,'abWeightLifter',
	                     lambda *a: mel.eval('abWeightLifter'),
	                     "Tool for working with influences\n by Brendan Ross")
	
	guiFactory.doButton2(SkinWeightsUtilitiesRow,'zoo.SkinPropagationTool',
	                     lambda *a: tdToolsLib.loadZooSkinPropagation(),
	                     "For sending weighting from a referenced file back to the original file\n by Hamish McKenzie")


	SkinWeightsUtilitiesRow.layout()
	mc.setParent(self.containerName)
	guiFactory.lineSubBreak()


	return self.containerName

    def buildBlendshapeTool(self,parent, vis=True):
	containerName = 'BlendShapeContainer'
	self.containerName = MelColumn(parent,vis=vis)

	#clear our variables
	if not mc.optionVar( ex='cgmVar_BSBakeInbetweens' ):
	    mc.optionVar( iv=('cgmVar_BSBakeInbetweens', 0) )
	if not mc.optionVar( ex='cgmVar_BSBakeTransferConnections' ):
	    mc.optionVar( iv=('cgmVar_BSBakeTransferConnections', 0) )
	if not mc.optionVar( ex='cgmVar_BSBakeCombine' ):
	    mc.optionVar( iv=('cgmVar_BSBakeCombine', 0) )

	guiFactory.appendOptionVarList(self,'cgmVar_BSBakeInbetweens')	
	guiFactory.appendOptionVarList(self,'cgmVar_BSBakeTransferConnections')	
	guiFactory.appendOptionVarList(self,'cgmVar_BSBakeCombine')	

	mc.setParent(self.containerName)
	guiFactory.header('Baker')
	guiFactory.lineSubBreak()

	#>>> Baker Option Row
	BakerSettingsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5)
	MelSpacer(BakerSettingsRow,w=5)

	self.uiBlendShapeBakeInbetweensOptionCB = MelCheckBox(BakerSettingsRow,l='Inbetweens',
	                                                      onCommand = lambda *a: mc.optionVar(iv=('cgmVar_BSBakeInbetweens',1)),
	                                                      offCommand = lambda *a: mc.optionVar(iv=('cgmVar_BSBakeInbetweens',0)),
	                                                      annotation = "Do inbetween targets as well",
	                                                      v = (mc.optionVar(query='cgmVar_BSBakeInbetweens')))

	self.uiBlendShapeBakeTransferConnectionsCB = MelCheckBox(BakerSettingsRow,l='Transfer Connections',
	                                                         onCommand = lambda *a: mc.optionVar(iv=('cgmVar_BSBakeTransferConnections',1)),
	                                                         offCommand = lambda *a: mc.optionVar(iv=('cgmVar_BSBakeTransferConnections',0)),
	                                                         annotation = "Creates a blendShape node on the target object(s)\n Attempts to transfer the connections for\n the bake blendshape node to the new one",
	                                                         v = (mc.optionVar(query='cgmVar_BSBakeTransferConnections')))
	self.uiBlendShapeBakeCombineOptionCB = MelCheckBox(BakerSettingsRow,l='Combine',
	                                                   onCommand = lambda *a: mc.optionVar(iv=('cgmVar_BSBakeCombine',1)),
	                                                   offCommand = lambda *a: mc.optionVar(iv=('cgmVar_BSBakeCombine',0)),
	                                                   v = (mc.optionVar(query='cgmVar_BSBakeCombine')),
	                                                   enable = True)

	MelLabel(BakerSettingsRow,l='Search Terms:')
	self.BlendShapeCombineTermsField = MelTextField(BakerSettingsRow,backgroundColor = [1,1,1],w=60,
	                                                annotation = "Terms to search for to combine\n For example: 'left,right'",
	                                                enable = True)
	BakerSettingsRow.setStretchWidget(self.BlendShapeCombineTermsField )
	MelSpacer(BakerSettingsRow,w=5)
	BakerSettingsRow.layout()

	#>>> Baking Buttons Row
	mc.setParent(self.containerName)
	guiFactory.lineSubBreak()

	BakerButtonsRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
	guiFactory.doButton2(BakerButtonsRow,'Bake shapes from Source',
	                     lambda *a:tdToolsLib.doBakeBlendShapeTargetsFromSource(self),
	                     "Bakes out the targets of an object's blendshape node.")
	guiFactory.doButton2(BakerButtonsRow,'Bake to Target(s)',
	                     lambda *a:tdToolsLib.doBakeBlendShapeTargetsToTargetsFromSource(self),
	                     "Bakes the targets of a a source object's \n blendshape node to target object(s)")


	BakerButtonsRow.layout()


	mc.setParent(self.containerName)
	guiFactory.lineSubBreak()
	guiFactory.lineBreak()




	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Pose Buffer
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	mc.setParent(self.containerName)
	guiFactory.header('Pose Buffer')
	guiFactory.lineSubBreak()

	#clear our variables
	if not mc.optionVar( ex='cgmVar_PoseBufferTransferConnections' ):
	    mc.optionVar( iv=('cgmVar_PoseBufferTransferConnections', 1) )
	if not mc.optionVar( ex='cgmVar_PoseBufferDoConnect' ):
	    mc.optionVar( iv=('cgmVar_PoseBufferDoConnect', 1) )
	if not mc.optionVar( ex='cgmVar_PoseBufferDoRemoveMissing' ):
	    mc.optionVar( iv=('cgmVar_PoseBufferDoRemoveMissing', 1) )
	    
	guiFactory.appendOptionVarList(self,'cgmVar_PoseBufferTransferConnections')	
	guiFactory.appendOptionVarList(self,'cgmVar_PoseBufferDoConnect')	
	guiFactory.appendOptionVarList(self,'cgmVar_PoseBufferDoRemoveMissing')	

	#>>> Option Row
	PoseBufferSettingsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5)
	MelSpacer(PoseBufferSettingsRow,w='5')
	MelLabel(PoseBufferSettingsRow,l='Options: ', align = 'right')
	PoseBufferSettingsRow.setStretchWidget(MelSpacer(PoseBufferSettingsRow))
	self.uiPoseBufferDoConnectOptionCB = MelCheckBox(PoseBufferSettingsRow,l='Connect',
	                                                 onCommand = lambda *a: mc.optionVar(iv=('cgmVar_PoseBufferDoConnect',1)),
	                                                 offCommand = lambda *a: mc.optionVar(iv=('cgmVar_PoseBufferDoConnect',0)),
	                                                 annotation = 'Connects blendShape channels to corresponding \n buffer channels',
	                                                 v = (mc.optionVar(query='cgmVar_PoseBufferDoConnect')) )

	self.uiPoseBufferTransferConnectionsCB = MelCheckBox(PoseBufferSettingsRow,l='Transfer Connections',
	                                                     onCommand = lambda *a: mc.optionVar(iv=('cgmVar_PoseBufferTransferConnections',1)),
	                                                     offCommand = lambda *a: mc.optionVar(iv=('cgmVar_PoseBufferTransferConnections',0)),
	                                                     annotation = "Transfers sdk or expression \n connections driving the blendshape \nchannels to the buffer",
	                                                     v = (mc.optionVar(query='cgmVar_PoseBufferTransferConnections')))

	self.uiPoseBufferDoRemoveMissing = MelCheckBox(PoseBufferSettingsRow,l='Remove Missing',
	                                               onCommand = lambda *a: mc.optionVar(iv=('cgmVar_PoseBufferDoRemoveMissing',1)),
	                                               offCommand = lambda *a: mc.optionVar(iv=('cgmVar_PoseBufferDoRemoveMissing',0)),
	                                               annotation = "Removes bs channels that have been deleted from the buffer",
	                                               v = (mc.optionVar(query='cgmVar_PoseBufferDoRemoveMissing')) )

	PoseBufferSettingsRow.layout()

	mc.setParent(self.containerName)
	guiFactory.lineSubBreak()

	#>>> Pose Buffer Buttons Row
	mc.setParent(self.containerName)
	guiFactory.lineSubBreak()

	PoseBufferButtonsRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
	guiFactory.doButton2(PoseBufferButtonsRow,'Load',
	                     lambda *a:tdToolsLib.doLoadBlendShapePoseBuffer(self),
	                     "Loads blendshape information from an object",
	                     enable = True)

	guiFactory.doButton2(PoseBufferButtonsRow,'Create', 
	                     lambda *a:tdToolsLib.doCreatePoseBuffer(self),
	                     "Creates a pose buffer",
	                     enable = True)
	guiFactory.doButton2(PoseBufferButtonsRow,'Update', 
	                     lambda *a:tdToolsLib.doUpdatePoseBuffer(self),
	                     "Updates a blendshape poseBuffer if you've added or removed blendshapeChannels")


	PoseBufferButtonsRow.layout()


	mc.setParent(self.containerName)
	guiFactory.lineSubBreak()
	guiFactory.lineBreak()


	#>>> Blendshape Utility tools
	mc.setParent(self.containerName)
	guiFactory.header('Utilities')
	guiFactory.lineSubBreak()


	BlendshapeUtilitiesRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(BlendshapeUtilitiesRow,'abSymMesh',
	                     lambda *a: mel.eval('abSymMesh'),
	                     "Tool for working geo for blendshapes\n by Brendan Ross")
	guiFactory.doButton2(BlendshapeUtilitiesRow,'abTwoFace',
	                     lambda *a: mel.eval('abTwoFace'),
	                     "Tool for splitting geo for blendshapes\n by Brendan Ross")


	BlendshapeUtilitiesRow.layout()
	mc.setParent(self.containerName)
	guiFactory.lineSubBreak()



	return self.containerName


    def buildUtilitiesTool(self,parent, vis=True):
	containerName = 'DeformerUtilitiesContainer'

	self.containerName = MelColumn(parent,vis=vis)
	mc.setParent(self.containerName )
	guiFactory.header('Shrink wrap')
	guiFactory.lineSubBreak()

	ShrinkWrapRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(ShrinkWrapRow,'Shrink wrap to source',
	                     lambda *a:tdToolsLib.doShrinkWrapToSource(),
	                     'Snaps vertices of a target object to the closest point on the source')

	ShrinkWrapRow.layout()
	mc.setParent(self.containerName )
	guiFactory.lineSubBreak()
	guiFactory.lineBreak()


	#>>> PolyUnite
	mc.setParent(self.containerName )
	guiFactory.header('Poly Unite')
	guiFactory.lineSubBreak()

	PolyUniteRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(PolyUniteRow,'Load to Source',
	                     lambda *a:tdToolsLib.doLoadPolyUnite(self),
	                     "Attempts to load polyUnite and select the source shapes")
	guiFactory.doButton2(PolyUniteRow,'Build polyUnite',
	                     lambda *a:tdToolsLib.doBuildPolyUnite(self),
	                     "Builds a poly unite geo node from target or \n selected objects (checks for mesh types_")
	guiFactory.doButton2(PolyUniteRow,'Remove polyUnite node',
	                     lambda *a:tdToolsLib.doDeletePolyUniteNode(self),
	                     "Removes a polyUnite node and connections \n as cleanly as possible")

	PolyUniteRow.layout()
	mc.setParent(self.containerName )
	guiFactory.lineSubBreak()
	guiFactory.lineBreak()


	#>>> GeneralUtilities
	mc.setParent(self.containerName )
	guiFactory.header('General')
	guiFactory.lineSubBreak()

	GeneralUtilitiesRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)

	guiFactory.doButton2(GeneralUtilitiesRow,'Deformer Keyable Attr Connect',
	                     lambda *a:tdToolsLib.doDeformerKeyableAttributesConnect(self),
	                     "Copies the keyable attribues from a \n deformer to another control and connects them")
	GeneralUtilitiesRow.layout()
	mc.setParent(self.containerName )
	guiFactory.lineSubBreak()



	return self.containerName

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
	    
	guiFactory.appendOptionVarList(self,'cgmVar_AutoNameObject')	

	LoadAutoNameObjectRow = MelHSingleStretchLayout(self.containerName ,ut='cgmUISubTemplate',padding = 5)

	MelSpacer(LoadAutoNameObjectRow,w=5)

	MelLabel(LoadAutoNameObjectRow,l='Object:',align='right')

	self.AutoNameObjectField = MelTextField(LoadAutoNameObjectRow, w= 125, ut = 'cgmUIReservedTemplate', editable = False)

	guiFactory.doButton2(LoadAutoNameObjectRow,'<<',
	                     lambda *a:namingToolsLib.uiLoadAutoNameObject(self),
	                     'Load to field')

	LoadAutoNameObjectRow.setStretchWidget(self.AutoNameObjectField  )

	guiFactory.doButton2(LoadAutoNameObjectRow,'Up',
	                     lambda *a:namingToolsLib.uiAutoNameWalkUp(self),
	                     'Load parent')

	guiFactory.doButton2(LoadAutoNameObjectRow,'Down',
	                     lambda *a:namingToolsLib.uiAutoNameWalkDown(self),
	                     'Load child')

	guiFactory.doButton2(LoadAutoNameObjectRow,'Name it',
	                     lambda *a:namingToolsLib.uiNameLoadedAutoNameObject(self),
	                     'Name the loaded object')
	guiFactory.doButton2(LoadAutoNameObjectRow,'Name Children',
	                     lambda *a:namingToolsLib.uiNameLoadedAutoNameObjectChildren(self),
	                     'Load to field')

	MelSpacer(LoadAutoNameObjectRow,w=5)

	LoadAutoNameObjectRow.layout()


	mc.setParent(self.containerName )
	guiFactory.lineSubBreak()

	#>>> Tag Labels
	TagLabelsRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
	MelLabel(TagLabelsRow,label = 'Position/Iterator')
	MelLabel(TagLabelsRow,label = 'Direction/Modifier')
	MelLabel(TagLabelsRow,label = 'Name/Modifier')
	MelLabel(TagLabelsRow,label = 'Type/Modifier')

	TagLabelsRow.layout()

	#>>> Tags
	mc.setParent(self.containerName )
	TagsRow = MelHLayout(self.containerName,ut='cgmUISubTemplate',padding = 3)
	self.PositionTagField = MelTextField(TagsRow,
	                                     enable = False,
	                                     bgc = dictionary.returnStateColor('normal'),
	                                     ec = lambda *a: namingToolsLib.uiUpdateAutoNameTag(self,'cgmPosition'),
	                                     w = 75)
	self.DirectionTagField = MelTextField(TagsRow,
	                                      enable = False,
	                                      bgc = dictionary.returnStateColor('normal'),
	                                      ec = lambda *a: namingToolsLib.uiUpdateAutoNameTag(self,'cgmDirection'),
	                                      w = 75)
	self.NameTagField = MelTextField(TagsRow,
	                                 enable = False,
	                                 bgc = dictionary.returnStateColor('normal'),
	                                 ec = lambda *a: namingToolsLib.uiUpdateAutoNameTag(self,'cgmName'),
	                                 w = 75)

	self.ObjectTypeTagField = MelTextField(TagsRow,
	                                       enable = False,
	                                       bgc = dictionary.returnStateColor('normal'),
	                                       ec = lambda *a: namingToolsLib.uiUpdateAutoNameTag(self,'cgmType'),
	                                       w = 75)

	TagsRow.layout()
	mc.setParent(self.containerName )
	guiFactory.lineSubBreak()

	#>>> ModifierTags
	mc.setParent(self.containerName )
	TagModifiersRow = MelHLayout(self.containerName,ut='cgmUISubTemplate',padding = 3)
	self.IteratorTagField = MelTextField(TagModifiersRow,
	                                     enable = False,
	                                     bgc = dictionary.returnStateColor('normal'),
	                                     ec = lambda *a: namingToolsLib.uiUpdateAutoNameTag(self,'cgmIterator'),
	                                     w = 75)
	self.DirectionModifierTagField = MelTextField(TagModifiersRow,
	                                              enable = False,
	                                              bgc = dictionary.returnStateColor('normal'),
	                                              ec = lambda *a: namingToolsLib.uiUpdateAutoNameTag(self,'cgmDirectionModifier'),
	                                              w = 75)
	self.NameModifierTagField = MelTextField(TagModifiersRow,
	                                         enable = False,
	                                         bgc = dictionary.returnStateColor('normal'),
	                                         ec = lambda *a: namingToolsLib.uiUpdateAutoNameTag(self,'cgmNameModifier'),
	                                         w = 75)
	self.ObjectTypeModifierTagField = MelTextField(TagModifiersRow,
	                                               enable = False,
	                                               bgc = dictionary.returnStateColor('normal'),
	                                               ec = lambda *a: namingToolsLib.uiUpdateAutoNameTag(self,'cgmTypeModifier'),
	                                               w = 75)

	TagModifiersRow.layout()



	mc.setParent(self.containerName )
	guiFactory.lineSubBreak()
	guiFactory.lineBreak()

	#>>> Multitag
	mc.setParent(self.containerName )
	guiFactory.header('Selection based tools')
	guiFactory.lineSubBreak()

	multiTagRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)

	MelSpacer(multiTagRow,w=5)
	MelLabel(multiTagRow,label = 'Multi tag >>>')

	self.multiTagInfoField = MelTextField(multiTagRow,
	                                      enable = True,
	                                      bgc = dictionary.returnStateColor('normal'),
	                                      ec = lambda *a: namingToolsLib.uiMultiTagObjects(self),
	                                      w = 75)


	self.cgmMultiTagOptions = MelOptionMenu(multiTagRow,l = 'Pick a tag:')

	for tag in 'Name','Type','Direction','Position','Iterator','NameModifier','TypeModifier','DirectionModifier':
	    self.cgmMultiTagOptions.append(tag)

	self.cgmMultiTagOptions(edit = True, select = 1)

	MelSpacer(multiTagRow,w=5)


	multiTagRow.layout()
	mc.setParent(self.containerName )
	guiFactory.lineSubBreak()

	#>>> Copy/Swap
	mc.setParent(self.containerName )

	SwapRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
	guiFactory.doButton2(SwapRow,'Copy Tags',
	                     lambda *a: namingToolsLib.uiCopyTags(self),
	                     "Copies the tags from the first object to all other objects in selection set")
	guiFactory.doButton2(SwapRow,'Swap Tags',
	                     lambda *a: namingToolsLib.uiSwapTags(self),
	                     "Swaps the tags between two objects")
	guiFactory.doButton2(SwapRow,'Clear Tags',
	                     lambda *a: namingToolsLib.uiClearTags(self),
	                     "Removes the selected tags from the selected objects")

	SwapRow.layout()


	mc.setParent(self.containerName )
	guiFactory.lineSubBreak()

	#>>> Basic
	mc.setParent(self.containerName )

	BasicRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
	guiFactory.doButton2(BasicRow,'Name Object',
	                     lambda *a:namingToolsLib.uiNameObject(self,False),
	                     "Attempts to name an object")	
	guiFactory.doButton2(BasicRow,'Name Heirarchy',
	                     lambda *a:namingToolsLib.doNameHeirarchy(self,False),
	                     "Attempts to intelligently name a  \n heirarchy of objects")
	guiFactory.doButton2(BasicRow,'Unique Name Object',
	                     lambda *a:namingToolsLib.uiNameObject(self,True),
	                     "Attempts to name an object\n while verifying no scene duplicates")	
	guiFactory.doButton2(BasicRow,'Unique Name Heirarchy',
	                     lambda *a:namingToolsLib.doNameHeirarchy(self,True,False),
	                     "Attempts to intelligently name a  \n heirarchy of objects\n while verifying no scene duplicates")




	BasicRow.layout()
	mc.setParent(self.containerName )
	guiFactory.lineSubBreak()

	#>>> Utilities
	mc.setParent(self.containerName )

	UtilitiesRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)	
	guiFactory.doButton2(UtilitiesRow,'Update Name',
	                     lambda *a:namingToolsLib.doUpdateObjectName(self),
	                     "Takes the name you've manually changed the object to, \n stores that to the cgmName tag then \n renames the object")
	guiFactory.doButton2(UtilitiesRow,'Report Object Name Dict',
	                     lambda *a:namingToolsLib.uiReturnFastName(self),
	                     "Get's object's naming factory info ")
	guiFactory.doButton2(UtilitiesRow,'Report object info',
	                     lambda *a:namingToolsLib.uiGetObjectInfo(self),
	                     "Get's object's naming factory info ")


	UtilitiesRow.layout()
	mc.setParent(self.containerName )
	guiFactory.lineSubBreak()
	guiFactory.lineBreak()

	return self.containerName


    def buildStandardNamingTool(self,parent, vis=True):
	containerName = 'Standard Naming Container'
	self.containerName = MelColumn(parent,vis=vis)

	#>>> Tag Labels
	TagLabelsRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
	MelLabel(TagLabelsRow,label = 'Not done yet...')
	TagLabelsRow.layout()


	return self.containerName

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Components
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildLoadObjectField(self,parent, optionVar):
	#clear our variables
	if not mc.optionVar( ex=optionVar ):
	    mc.optionVar( sv=(optionVar, '') )
	    
	guiFactory.appendOptionVarList(self,optionVar)	

	LoadObjectTargetUtilityRow = MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

	MelSpacer(LoadObjectTargetUtilityRow,w=5)


	MelLabel(LoadObjectTargetUtilityRow,l='Object:',align='right')

	self.SourceObjectField = MelTextField(LoadObjectTargetUtilityRow, w= 125, ut = 'cgmUIReservedTemplate', editable = False)
	if mc.optionVar( q = optionVar):
	    self.SourceObjectField(edit=True,text = mc.optionVar( q = optionVar))

	guiFactory.doButton2(LoadObjectTargetUtilityRow,'<<',
	                     lambda *a:guiFactory.doLoadSingleObjectToTextField(self.SourceObjectField,'cgmVar_SourceObject'),
	                     'Load to field')


	MelLabel(LoadObjectTargetUtilityRow,l='Target:',align='right')
	self.TargetObjectField = MelTextField(LoadObjectTargetUtilityRow, w=125, ut = 'cgmUIReservedTemplate', editable = False)

	LoadObjectTargetUtilityRow.setStretchWidget(self.BaseNameField )

	guiFactory.doButton2(LoadObjectTargetUtilityRow,'<<',
	                     lambda *a:guiFactory.doLoadMultipleObjectsToTextField(self.TargetObjectField,False,'cgmVar_TargetObjects'),
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

	guiFactory.appendOptionVarList(self,'cgmVar_SourceObject')	
	guiFactory.appendOptionVarList(self,'cgmVar_TargetObjects')	
	

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
	                     lambda *a:guiFactory.doLoadSingleObjectToTextField(self.SourceObjectField,'cgmVar_SourceObject'),
	                     'Load to field')


	MelLabel(LoadObjectTargetUtilityRow,l='Target:',align='right')
	self.TargetObjectField = MelTextField(LoadObjectTargetUtilityRow, w=125, ut = 'cgmUIReservedTemplate', editable = False)

	LoadObjectTargetUtilityRow.setStretchWidget(self.BaseNameField )

	guiFactory.doButton2(LoadObjectTargetUtilityRow,'<<',
	                     lambda *a:guiFactory.doLoadMultipleObjectsToTextField(self.TargetObjectField,False,'cgmVar_TargetObjects'),
	                     'Load to field')

	MelSpacer(LoadObjectTargetUtilityRow,w=5)

	LoadObjectTargetUtilityRow.layout()


	mc.setParent(parent)
	guiFactory.lineSubBreak()


    def buildModeSetUtilityRow(self,parent,RadioCollectionName,ModeSelectionChoicesList, SectionLayoutCommands, cgmVar_Name,OptionList,labelText = 'Choose: '):
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# General purpose mode setter
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	if not mc.optionVar( ex=cgmVar_Name ):
	    mc.optionVar( sv=(cgmVar_Name, OptionList[0]) )
	guiFactory.appendOptionVarList(self,cgmVar_Name)	

	ModeSetRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
	MelLabel(ModeSetRow, label = labelText,align='right')
	self.RadioCollectionName = MelRadioCollection()
	self.ModeSelectionChoicesList = []

	#build our sub sesctions
	ContainersListName = (RadioCollectionName+'Containers')
	self.ContainersListName = []
	for LayoutCommand in SectionLayoutCommands:
	    print LayoutCommand
	    self.ContainersListName.append( [self.LayoutCommand(parent,vis=True) ])


	for item in OptionList:
	    self.ModeSelectionChoicesList.append(self.RadioCollectionName.createButton(ModeSetRow,label=item,
	                                                                               onCommand = lambda *a: guiFactory.toggleModeState(item,OptionList,cgmVar_Name,ContainerList)))

	"""
        for item in OptionList:
            self.ModeSelectionChoicesList.append(self.RadioCollectionName.createButton(ModeSetRow,label=item,
                                                                                 onCommand = ('%s%s%s%s%s' %("mc.optionVar( sv=('",cgmVar_Name,"','",item,"'))"))))
        """

	mc.radioCollection(self.RadioCollectionName,edit=True, sl=self.ModeSelectionChoicesList[OptionList.index(mc.optionVar(q=cgmVar_Name))])
	ModeSetRow.layout()


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Position Components
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildRowColumnUIRow(self,parent):
	if not mc.optionVar( ex='cgmVar_RowColumnCount' ):
	    mc.optionVar( iv=('cgmVar_RowColumnCount', 3) )
	if not mc.optionVar( ex='cgmVar_OrderByName' ):
	    mc.optionVar( iv=('cgmVar_OrderByName', 0) )
	
	guiFactory.appendOptionVarList(self,'cgmVar_RowColumnCount')	
	guiFactory.appendOptionVarList(self,'cgmVar_OrderByName')	

	self.RowColumnLayoutModes = ['Column','Row']

	RowColumnLayoutModeRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 20)

	MelLabel(RowColumnLayoutModeRow, l='Number of Columns:',w=30)
	self.RowColumnIntField = MelIntField(RowColumnLayoutModeRow,w=30,v=(mc.optionVar(q='cgmVar_RowColumnCount')))

	self.OrderByNameCheckBox = MelCheckBox(RowColumnLayoutModeRow,l = 'Arrange by Name',
	                                       v = (mc.optionVar(query='cgmVar_OrderByName')),
	                                       onCommand = lambda *a: mc.optionVar(iv=('cgmVar_OrderByName',1)),
	                                       offCommand = lambda *a: mc.optionVar(iv=('cgmVar_OrderByName',0)))


	RowColumnLayoutModeRow.layout()




    def buildSurfaceSnapAimRow(self,parent):
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# World Up Axis
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	if not mc.optionVar( ex='cgmVar_SurfaceSnapAimMode' ):
	    mc.optionVar( iv=('cgmVar_SurfaceSnapAimMode', 0) )
	    
	guiFactory.appendOptionVarList(self,'cgmVar_SurfaceSnapAimMode')	

	self.surfaceSnapAimModes = ['Normal','Start Pos']

	surfaceSnapAimModeRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
	MelLabel(surfaceSnapAimModeRow, label = 'Orient to: ')
	self.uiSurfaceSnapAimModeOptionGroup = MelRadioCollection()
	self.surfaceSnapAimModeCollectionChoices = []
	for item in self.surfaceSnapAimModes:
	    cnt = self.surfaceSnapAimModes.index(item)
	    if mc.optionVar( q='cgmVar_SurfaceSnapAimMode' ) == cnt:
		checkState = True
	    else:
		checkState = False
	    self.surfaceSnapAimModeCollectionChoices.append(self.uiSurfaceSnapAimModeOptionGroup.createButton(surfaceSnapAimModeRow,label=item,
	                                                                                                      onCommand = ("mc.optionVar( iv=('cgmVar_SurfaceSnapAimMode',%i))" % cnt)))

	mc.radioCollection(self.uiSurfaceSnapAimModeOptionGroup ,edit=True,sl= self.surfaceSnapAimModeCollectionChoices[ mc.optionVar(q='cgmVar_SurfaceSnapAimMode') ] )
	surfaceSnapAimModeRow.layout()


    def buildObjectUpRow(self,parent):
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Object Up Axis
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	objectUpRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
	MelLabel(objectUpRow, label = 'Object Up: ')
	self.uiObjectUpAxisOptionGroup = MelRadioCollection()
	self.objectUpAxisCollectionChoices = []
	for item in self.axisOptions:
	    self.objectUpAxisCollectionChoices.append(self.uiObjectUpAxisOptionGroup.createButton(objectUpRow,label=item,
	                                                                                          onCommand = ('%s%s%s' %("mc.optionVar( sv=('cgmVar_ObjectUpAxis','",item,"'))"))))

	mc.radioCollection(self.uiObjectUpAxisOptionGroup ,edit=True,sl= (self.objectUpAxisCollectionChoices[ self.axisOptions.index(mc.optionVar(q='cgmVar_ObjectUpAxis')) ]))
	objectUpRow.layout()

    def buildObjectAimRow(self,parent):
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Object Aim Axis
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	objectAimRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
	MelLabel(objectAimRow, label = 'Object Aim: ')
	self.uiObjectAimAxisOptionGroup = MelRadioCollection()
	self.objectAimAxisCollectionChoices = []
	for item in self.axisOptions:
	    self.objectAimAxisCollectionChoices.append(self.uiObjectAimAxisOptionGroup.createButton(objectAimRow,label=item,
	                                                                                            onCommand = ('%s%s%s' %("mc.optionVar( sv=('cgmVar_ObjectAimAxis','",item,"'))"))))

	mc.radioCollection(self.uiObjectAimAxisOptionGroup ,edit=True,sl= (self.objectAimAxisCollectionChoices[ self.axisOptions.index(mc.optionVar(q='cgmVar_ObjectAimAxis')) ]))
	objectAimRow.layout()

    def buildWorldUpRow(self,parent):
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# World Up Axis
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	worldUpRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
	MelLabel(worldUpRow, label = 'World Up: ')
	self.uiWorldUpAxisOptionGroup = MelRadioCollection()
	self.worldUpAxisCollectionChoices = []
	for item in self.axisOptions:
	    self.worldUpAxisCollectionChoices.append(self.uiWorldUpAxisOptionGroup.createButton(worldUpRow,label=item,
	                                                                                        onCommand = ('%s%s%s' %("mc.optionVar( sv=('cgmVar_WorldUpAxis','",item,"'))"))))

	mc.radioCollection(self.uiWorldUpAxisOptionGroup ,edit=True,sl= (self.worldUpAxisCollectionChoices[ self.axisOptions.index(mc.optionVar(q='cgmVar_WorldUpAxis')) ]))
	worldUpRow.layout()