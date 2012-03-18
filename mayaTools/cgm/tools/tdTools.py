#=================================================================================================================================================
#=================================================================================================================================================
#	cgmTDTools - a part of rigger
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
#	http://www.joshburton.com
# 	Copyright 2011 Josh Burton - All Rights Reserved.
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

reload(tdToolsLib)


def run():
	mel.eval('python("import maya.cmds as mc;from cgm.tools import tdTools;from cgm.tools import tdToolsLib;from cgm.lib import guiFactory;cgmTDToolsWin = tdTools.tdToolsClass()")')

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

class tdToolsClass(BaseMelWindow):
	WINDOW_NAME = 'TDTools'
	WINDOW_TITLE = 'TDTools >>> cg{monks}'
	DEFAULT_SIZE = 550, 400
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created
	guiFactory.initializeTemplates()

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
		self.toolName = 'cgmTDTools'
		self.module = 'cgmTDTools'
		self.winName = 'cgmTDToolsWin'

		self.showHelp = False
		self.helpBlurbs = []
		self.oldGenBlurbs = []

		self.showTimeSubMenu = False
		self.timeSubMenu = []

		# About Window
		self.description = 'A large series of tools for general rigging purposes including: Curves, Naming, Positioning,Deformers'
		self.author = 'Josh Burton'
		self.owner = 'CG Monks'
		self.website = 'www.joshburton.com'
		self.version = __version__

		# About Window
		self.sizeOptions = ['Object','Average','Input Size','First Object']
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
		self.curveOptionList = 	['circle','square','squareRounded','squareDoubleRounded','semiSphere','sphere','cube','pyramid','cross','fatCross','arrowSingle','arrowSingleFat','arrowDouble','arrowDoubleFat','arrow4','arrow4Fat','arrow8','arrowsOnBall','nail','nail2','nail4','eye','teeth','foot','gear','dumcgmell','locator','arrowsLocator','arrowsPointCenter','arrowForm','arrowDirectionBall','arrowRotate90','arrowRotate90Fat','arrowRotate180','arrowRotate180Fat','circleArrow','circleArrow1','cirlceArrow2','circleArrow3','circleArrow1Interior','circleArrow2Axis','masterAnim']

		self.uiCurveAxisOptionGroup = ''
		self.uiCurveAxis = 'z+'

		self.uiCurveNameField = ''
		self.uiCurveName = ''

		self.makeMasterControl = False
		self.makeMasterControlVis = False
		self.makeMasterControlSettings = False

		# Colors
		self.defaultOverrideColor = 6

		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# Build
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

		#Menu
		self.setupVariables
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
		for tab in 'Curves','Position','Info','Attribute','Deformer','Naming':
			tabs.setLabel(n,tab)
			n+=1

		self.buildCurvesTab(TabCurves)
		self.buildPositionTab(TabPosition)
		self.buildInfoTab(TabInfo)
		self.buildAttributeTab(TabAttribute)
		self.buildDeformerTab(TabDeformer)
		self.buildNamingTab(TabNaming)

		self.show()

	def setupVariables():
		if not mc.optionVar( ex='cgmTDToolsWinActiveTab' ):
			mc.optionVar( iv=('cgmTDToolsWinActiveTab', 1) )

		if not mc.optionVar( ex='cgmVarForceBoundingBoxState' ):
			mc.optionVar( iv=('cgmVarForceBoundingBoxState', 0) )
		if not mc.optionVar( ex='cgmVarForceEveryFrame' ):
			mc.optionVar( iv=('cgmVarForceEveryFrame', 0) )
		if not mc.optionVar( ex='cgmVarLocinatorShowHelp' ):
			mc.optionVar( iv=('cgmVarLocinatorShowHelp', 0) )
		if not mc.optionVar( ex='cgmVarFontOption' ):
			mc.optionVar( sv=('cgmVarFontOption', self.textObjectFont) )
		if not mc.optionVar( ex='cgmVarSizeMode' ):
			mc.optionVar( iv=('cgmVarSizeMode', 0) )
		if not mc.optionVar( ex='cgmVarRenameOnUpdate' ):
			mc.optionVar( iv=('cgmVarRenameOnUpdate', 1) )
		if not mc.optionVar( ex='cgmVarDefaultOverrideColor' ):
			mc.optionVar( iv=('cgmVarDefaultOverrideColor', 6) )


	def updateCurrentTab(self,optionVar):
		mc.optionVar( iv=(optionVar, self.getSelectedTabIdx()) )



	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Menus
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildOptionsMenu( self, *a ):
		self.UI_OptionsMenu.clear()

		# Font Menu
		FontMenu = MelMenuItem( self.UI_OptionsMenu, l='Font', subMenu=True)
		FontMenuCollection = MelRadioMenuCollection()

		fontOption = mc.optionVar( q='cgmVarFontOption' )
		if mc.optionVar( q='cgmVarFontOption' ) not in self.fontList:
			pickedFontState = True
		else:
			pickedFontState = False

		for font in self.fontList:
			if not pickedFontState:
				if mc.optionVar( q='cgmVarFontOption' ) == font:
					fontState = True
				else:
					fontState = False
			else:
				fontState = False
			FontMenuCollection.createButton(FontMenu,l=font,
						                    c=('%s%s%s' %("mc.optionVar( sv=('cgmVarFontOption','",font,"'))")),
						                    rb = fontState)

		MelMenuItemDiv( FontMenu )
		FontMenuCollection.createButton(FontMenu,l='Custom',
				                        c=lambda *a: mc.optionVar( sv=('cgmVarFontOption', guiFactory.doReturnFontFromDialog(fontOption))),
				                        rb = pickedFontState)

		# Size Menu
		SizeMenu = MelMenuItem( self.UI_OptionsMenu, l='Size', subMenu=True)
		SizeMenuCollection = MelRadioMenuCollection()

		for item in self.sizeOptions :
			cnt = self.sizeOptions.index(item)
			if mc.optionVar( q='cgmVarSizeMode' ) == cnt:
				sizeModeState = True
			else:
				sizeModeState = False
			SizeMenuCollection.createButton(SizeMenu,l=item,
						                    c= ("mc.optionVar( iv=('cgmVarSizeMode',%i))" % cnt),
						                    rb = sizeModeState)


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

		# Updating Options Menu
		UpdatingMenu = MelMenuItem( self.UI_OptionsMenu, l='Updating', subMenu=True)

		RenameOnUpdateState = mc.optionVar( q='cgmVarRenameOnUpdate' )

		MelMenuItem( UpdatingMenu, l="Rename on Update",
				     cb=RenameOnUpdateState,
				     c= lambda *a: guiFactory.doToggleIntOptionVariable('cgmVarRenameOnUpdate'))

		MelMenuItemDiv( self.UI_OptionsMenu )

	def buildAxisMenu(self, *a ):
		if not mc.optionVar( ex='cgmVarObjectUpAxis' ):
			mc.optionVar( sv=('cgmVarObjectUpAxis', 'x+') )
		if not mc.optionVar( ex='cgmVarObjectAimAxis' ):
			mc.optionVar( sv=('cgmVarObjectAimAxis', 'x+') )
		if not mc.optionVar( ex='cgmVarWorldUpAxis' ):
			mc.optionVar( sv=('cgmVarWorldUpAxis', 'y+') )


		self.UI_AxisMenu.clear()

		# Object Aim Menu
		ObjectAimMenu = MelMenuItem( self.UI_AxisMenu, l='Object Aim', subMenu=True)
		ObjectAimCollection = MelRadioMenuCollection()

		for axis in self.axisOptions :
			if mc.optionVar( q='cgmVarObjectAimAxis' ) == axis:
				checkState = True
			else:
				checkState = False
			ObjectAimCollection.createButton(ObjectAimMenu,l=axis,
						                     c= ('%s%s%s' %("mc.optionVar( sv=('cgmVarObjectAimAxis','",axis,"'))")),
						                     rb = checkState)

		# Object Up Menu
		ObjectUpMenu = MelMenuItem( self.UI_AxisMenu, l='Object Up', subMenu=True)
		ObjectUpCollection = MelRadioMenuCollection()

		for axis in self.axisOptions :
			if mc.optionVar( q='cgmVarObjectUpAxis' ) == axis:
				checkState = True
			else:
				checkState = False
			ObjectUpCollection.createButton(ObjectUpMenu,l=axis,
						                    c= ('%s%s%s' %("mc.optionVar( sv=('cgmVarObjectUpAxis','",axis,"'))")),
						                    rb = checkState)

		# World Up Menu
		WorldUpMenu = MelMenuItem( self.UI_AxisMenu, l='World Up', subMenu=True)
		WorldUpCollection = MelRadioMenuCollection()

		for axis in self.axisOptions :
			if mc.optionVar( q='cgmVarWorldUpAxis' ) == axis:
				checkState = True
			else:
				checkState = False
			WorldUpCollection.createButton(WorldUpMenu,l=axis,
						                   c= ('%s%s%s' %("mc.optionVar( sv=('cgmVarWorldUpAxis','",axis,"'))")),
						                   rb = checkState)



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
		mc.text(label='>>>A Part of the cgmThingamarig Collection<<<', ut = 'cgmUIInstructionsTemplate')
		guiFactory.headerBreak()
		guiFactory.lineBreak()
		descriptionBlock = guiFactory.textBlock(self.description)

		guiFactory.lineBreak()
		mc.text(label=('%s%s' %('Written by: ',self.author)))
		mc.text(label=('%s%s%s' %('Copyright ',self.owner,', 2011')))
		guiFactory.lineBreak()
		mc.text(label='Version: %s' % self.version)
		mc.text(label='')
		guiFactory.doButton('Visit Website', 'import webbrowser;webbrowser.open("http://www.joshburton.com")')
		guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
		mc.setParent( '..' )
		mc.showWindow( window )

	def printHelp(self):
		import tdToolsLib
		help(tdToolsLib)


	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Tab Layouts
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildCurvesTab(self,parent):
		ShowHelpOption = mc.optionVar( q='cgmVarTDToolsShowHelp' )

		#>>>Main Form
		curvesMainFormLayout = MelFormLayout(parent)


		curvesLeftColumn = self.buildBasicLeftColumn(curvesMainFormLayout)
		curvesRightColumn = MelColumnLayout(curvesMainFormLayout)

		self.buildCurveCreator(curvesRightColumn)
		self.buildTextObjectCreator(curvesRightColumn)
		self.buildCurveUtilities(curvesRightColumn)
		self.buildSnapMoveTool(curvesRightColumn)


		#>> Defining Main Form Layout
		curvesMainFormLayout(edit = True,
				             attachForm = [(curvesLeftColumn,'left',0),
				                           (curvesLeftColumn,'top',0),
				                           (curvesRightColumn,'right',0),
				                           (curvesRightColumn,'top',0),
				                           ],
				             attachControl = [(curvesRightColumn,'left',0,curvesLeftColumn)]

				             )

	def buildPositionTab(self,parent):
		#>>>Main Form
		positionMainFormLayout = MelFormLayout(parent)


		positionLeftColumn = self.buildBasicLeftColumn(positionMainFormLayout)
		positionRightColumn = MelColumnLayout(positionMainFormLayout)

		self.buildSnapMoveTool(positionRightColumn)
		self.buildSnapAimTool(positionRightColumn)

		self.buildSnapToSurfaceTool(positionRightColumn)

		self.buildGridLayoutTool(positionRightColumn)

		#>> Defining Main Form Layout
		positionMainFormLayout(edit = True,
				               attachForm = [(positionLeftColumn,'left',0),
				                             (positionLeftColumn,'top',0),
				                             (positionRightColumn,'right',0),
				                             (positionRightColumn,'top',0),
				                             ],
				               attachControl = [(positionRightColumn,'left',0,positionLeftColumn)]

				               )

	def buildInfoTab(self,parent):
		ShowHelpOption = mc.optionVar( q='cgmVarTDToolsShowHelp' )

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

	def buildAttributeTab(self,parent):
		ShowHelpOption = mc.optionVar( q='cgmVarTDToolsShowHelp' )

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

	def buildDeformerTab(self,parent):
		#Options
		OptionList = ['skinCluster','blendshape','utilities']
		cgmVarName = 'cgmVarDeformerMode'
		RadioCollectionName ='DeformerMode'
		RadioOptionList = 'DeformerModeSelectionChoicesList'
		ModeSetRow = 'DeformerModeSetRow'

		ShowHelpOption = mc.optionVar( q='cgmVarTDToolsShowHelp' )
		if not mc.optionVar( ex=cgmVarName ):
			mc.optionVar( sv=(cgmVarName, OptionList[0]) )


		#self.buildModeSetUtilityRow(parent,'DeformerMode','DeformerModeChoices', SectionLayoutCommands, 'cgmVarDeformerMode',modesToToggle, labelText = 'Choose Mode: ')

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

		self.ContainerList.append( self.buildSkinClusterTool(parent,vis=False) )
		self.ContainerList.append( self.buildBlendshapeTool( parent,vis=False) )
		self.ContainerList.append( self.buildUtilitiesTool( parent,vis=False) )

		for item in OptionList:
			self.RadioOptionList.append(self.RadioCollectionName.createButton(ModeSetRow,label=item,
						                                                      onCommand = Callback(guiFactory.toggleModeState,item,OptionList,cgmVarName,self.ContainerList)))
		ModeSetRow.layout()


		mc.radioCollection(self.RadioCollectionName,edit=True, sl=self.RadioOptionList[OptionList.index(mc.optionVar(q=cgmVarName))])


	def buildNamingTab(self,parent):
		#Options
		OptionList = ['autoname','standard']
		cgmVarName = 'cgmVarNamingMode'
		RadioCollectionName ='NamingMode'
		RadioOptionList = 'NamingModeSelectionChoicesList'
		ModeSetRow = 'DeformerModeSetRow'

		ShowHelpOption = mc.optionVar( q='cgmVarTDToolsShowHelp' )
		if not mc.optionVar( ex=cgmVarName ):
			mc.optionVar( sv=(cgmVarName, OptionList[0]) )


		#Start layout
		ModeSetRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
		MelLabel(ModeSetRow, label = 'Choose Mode: ',align='right')
		self.RadioCollectionName = MelRadioCollection()
		self.RadioOptionList = []

		#build our sub sesctions
		self.ContainerList = []

		self.ContainerList.append( self.buildAutoNameTool(parent,vis=False) )
		self.ContainerList.append( self.buildUtilitiesTool(parent,vis=False) )

		for item in OptionList:
			self.RadioOptionList.append(self.RadioCollectionName.createButton(ModeSetRow,label=item,
						                                                      onCommand = Callback(guiFactory.toggleModeState,item,OptionList,cgmVarName,self.ContainerList)))
		ModeSetRow.layout()

		mc.radioCollection(self.RadioCollectionName,edit=True, sl=self.RadioOptionList[OptionList.index(mc.optionVar(q=cgmVarName))])



	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Sections of gui stuff
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildBasicLeftColumn(self,parent):
		ShowHelpOption = mc.optionVar( q='cgmVarTDToolsShowHelp' )
		LeftColumn = MelColumnLayout(parent, cw = 100)
		guiFactory.header('Set Color')

		mc.columnLayout(columnAttach = ('both',5),backgroundColor = [.2,.2,.2])
		colorSwatchMenu = mc.gridLayout(aec = False, numberOfRowsColumns=(10,3), cwh = (30,15),backgroundColor = [.2,.2,.2])
		colorSwatchesList = [1,2,3,11,24,21,12,10,25,4,13,20,8,30,9,5,6,18,15,29,28,7,27,19,23,26,14,17,22,16]
		for i in colorSwatchesList:
			colorBuffer = mc.colorIndex(i, q=True)
			mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=colorBuffer,
					  pc = ('%s%i%s' %("tdToolsLib.doSetCurveColorByIndex(",i,")")),
					  annotation = 'Sets the color of the object to this')
			mc.popupMenu(button = 3)
			mc.menuItem(label = 'Set as default',
						c = ('%s%i%s' %("mc.optionVar( iv=('cgmVarDefaultOverrideColor',",i,"))")))

		mc.setParent('..')
		mc.setParent('..')

		guiFactory.header('Transforms')

		guiFactory.lineSubBreak()
		guiFactory.doButton2(LeftColumn,'Group Me',
				             'from cgm.lib import rigging;rigging.groupMe()',
				             "Groups selected under a tranform at their current position")

		guiFactory.doButton2(LeftColumn,'Group In place', 
				             'tdToolsLib.doGroupMeInPlace()',
				             "Groups an object while maintaining its parent\n if it has one")

		guiFactory.lineSubBreak()
		guiFactory.doButton2(LeftColumn,'Zero Me',
				             'tdToolsLib.zeroGroupMe()',
				             'Zeros out object under group')

		guiFactory.lineSubBreak()
		guiFactory.doButton2(LeftColumn,'Transform Here',
				             'tdToolsLib.makeTransformHere()',
				             'Create transform matching object')

		guiFactory.lineSubBreak()
		guiFactory.doButton2(LeftColumn,'Copy Pivot',
				             'tdToolsLib.doCopyPivot()',
				             'Copy pivot from first selection to all other objects')

		guiFactory.lineSubBreak()
		guiFactory.doButton2(LeftColumn,'Loc Me',
				             'from cgm.tools import locinatorLib;locinatorLib.doLocMe(cgmTDToolsWin)',
				             'Creates loc at object, matching trans,rot and rotOrd')

		guiFactory.lineSubBreak()
		guiFactory.doButton2(LeftColumn,'updateLoc',
				             'from cgm.tools import locinatorLib;locinatorLib.doUpdateLoc(cgmTDToolsWin,True)',
				             'Updates loc or object connected to loc base don selection. See cgmLocinator for more options')
		return LeftColumn

	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Curve Stuff
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildCurveCreator(self,parent):
		makeCurvesContainer = MelColumnLayout(parent, ut='cgmUISubTemplate')
		guiFactory.header('Curve Creation')
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
		mc.checkBoxGrp(numberOfCheckBoxes=3, label='Master Control:', labelArray3=['Master','Vis', 'Settings'],
				       onCommand1 = ('cgmTDToolsWin.makeMasterControl = True'),
				       onCommand2 = ('cgmTDToolsWin.makeMasterControlVis = True'),
				       onCommand3 = ('cgmTDToolsWin.makeMasterControlSettings = True'),
				       offCommand1 = ('cgmTDToolsWin.makeMasterControl = False'),
				       offCommand2 = ('cgmTDToolsWin.makeMasterControlVis = False'),
				       offCommand3 = ('cgmTDToolsWin.makeMasterControlSettings = False'))



		buttonRow = MelHLayout(makeCurvesContainer,ut='cgmUISubTemplate',padding = 2)
		guiFactory.doButton2(buttonRow,'Create',
				             'tdToolsLib.doCreateCurveControl(cgmTDToolsWin)',
				             'Create Curve Object with Settings',w=50)

		buttonRow.layout()

		mc.setParent(parent)
		guiFactory.lineSubBreak()


	def buildTextObjectCreator(self,parent):
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
		self.textCurrentObjectField = MelTextField(currentObjectRow, ut = 'cgmUIReservedTemplate', editable = False)
		guiTextObjLoadButton = guiFactory.doButton2(currentObjectRow,'<<<',
				                                    'tdToolsLib.doLoadTexCurveObject(cgmTDToolsWin)',
				                                    'Load to field')

		MelSpacer(currentObjectRow)

		currentObjectRow.setStretchWidget(self.textCurrentObjectField)
		currentObjectRow.layout()

		mc.setParent(textObjectColumn)
		guiFactory.lineSubBreak()

		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# Line 3
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

		buttonRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)
		guiTextObjUpdateButton = guiFactory.doButton2(buttonRow,'Update Current',
				                                      'tdToolsLib.doUpdateTexCurveObject(cgmTDToolsWin)',
				                                      'Updates a current text object')
		guiTextObjUpdateButton = guiFactory.doButton2(buttonRow,'Create',
				                                      'tdToolsLib.doCreateTextCurveObject(cgmTDToolsWin)',
				                                      'Create a text object with the provided settings')
		buttonRow.layout()

		mc.setParent(parent)
		guiFactory.lineSubBreak()


	def buildCurveUtilities(self,parent):
		mc.setParent(parent)
		guiFactory.header('Curve Utilities')
		guiFactory.lineSubBreak()

		curveUtilitiesRow1 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)

		guiFactory.doButton2(curveUtilitiesRow1,'Objects to Crv',
				             'tdToolsLib.doCreateCurveFromObjects()',
				             'Creates a curve through the pivots of objects')
		guiFactory.doButton2(curveUtilitiesRow1,'shpPrnt',
				             'tdToolsLib.doShapeParent()',
				             "Maya's standard shape parent")
		guiFactory.doButton2(curveUtilitiesRow1,'shpPrnt in Place',
				             'tdToolsLib.doShapeParentInPlace()',
				             'shapeParents a curve in place')


		curveUtilitiesRow1.layout()

		mc.setParent(parent)
		guiFactory.lineSubBreak()


		curveUtilitiesRow2 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)
		guiFactory.doButton2(curveUtilitiesRow2,'What am I',
				             'tdToolsLib.doReportObjectType()',
				             'Reports what cgmThinga thinks the object is')
		guiFactory.doButton2(curveUtilitiesRow2,'Crv to Python',
				             'tdToolsLib.doCurveToPython()',
				             'Creates a python command to recreate a curve')
		guiFactory.doButton2(curveUtilitiesRow2,'Combine Curves',
				             'tdToolsLib.doCombineCurves()',
				             'Combines curves')

		curveUtilitiesRow2.layout()

		mc.setParent(parent)
		guiFactory.lineSubBreak()

		curveUtilitiesRow3 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)
		guiFactory.doButton2(curveUtilitiesRow3,'Loc CVs of curve',
				             'cgmLocinatorLib.doLocCVsOfObject()',
				             "Locs the CVs at the cv coordinates")

		guiFactory.doButton2(curveUtilitiesRow3,'Loc CVs on the curve',
				             'cgmLocinatorLib.doLocCVsOnObject()',
				             "Locs CVs at closest point on the curve")


		mc.setParent(parent)
		guiFactory.lineSubBreak()

		curveUtilitiesRow3.layout()

	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Position Tools
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildSnapMoveTool(self,parent):
		mc.setParent(parent)
		guiFactory.header('Snap Move')
		guiFactory.lineSubBreak()

		snapMoveRow1 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)

		guiFactory.doButton2(snapMoveRow1,'Parent',
				             'tdToolsLib.doParentSnap()',
				             'Parent snap one objects to a target')
		guiFactory.doButton2(snapMoveRow1,'Point',
				             'tdToolsLib.doPointSnap()',
				             "Point snap one objects to a target")
		guiFactory.doButton2(snapMoveRow1,'Orient',
				             'tdToolsLib.doOrientSnap()',
				             'Orient snap one objects to a target')

		mc.setParent(parent)
		guiFactory.lineSubBreak()

		snapMoveRow1.layout()

	def buildSnapAimTool(self,parent):
		mc.setParent(parent)
		guiFactory.header('Snap Aim')
		guiFactory.lineSubBreak()


		snapAimButton = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)


		MelButton(snapAimButton,l='One to Next',ut = 'cgmUITemplate',
				  c='tdToolsLib.doAimSnapOneToNext()',
				  annotation = 'Aims a list of objects one to the /n next in a parsed list of pairs')
		MelButton(snapAimButton,l='All to Last',ut = 'cgmUITemplate',
				  c='tdToolsLib.doAimSnapToOne()',
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
				             'tdToolsLib.doSnapClosestPointToSurface(False)',
				             'Aims a list of objects one to the /n next in a parsed list of pairs')
		guiFactory.doButton2(snapToSurfaceButton,'Snap and Aim',
				             'tdToolsLib.doSnapClosestPointToSurface()',
				             'Aims a list of objects one to the /n next in a parsed list of pairs')


		mc.setParent(parent)
		guiFactory.lineSubBreak()

		snapToSurfaceButton.layout()

	def buildGridLayoutTool(self,parent):
		mc.setParent(parent)
		guiFactory.header('Grid Layout')
		guiFactory.lineSubBreak()

		self.buildRowColumnUIRow(parent)

		mc.setParent(parent)
		guiFactory.lineSubBreak()

		GridLayoutButtonRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)

		guiFactory.doButton2(GridLayoutButtonRow,'Do it!',
				             ("tdToolsLib.doLayoutByRowsAndColumns(cgmTDToolsWin)"),
				             'Lays out the selected in a grid format /n by the number of columns input')


		GridLayoutButtonRow.layout()



	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Info Tools
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildBasicInfoTools(self,parent):
		mc.setParent(parent)
		guiFactory.header('Basic Info')
		guiFactory.lineSubBreak()

		BasicInfoRow1 = MelHLayout(parent,ut='cgmUISubTemplate',padding = 2)

		guiFactory.doButton2(BasicInfoRow1,'What am I',
				             'tdToolsLib.doReportObjectType()',
				             'Reports what cgmThinga thinks the object is')
		guiFactory.doButton2(BasicInfoRow1,'Count Selected',
				             'tdToolsLib.doReportSelectionCount()',
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
				             'tdToolsLib.docgmNameToFloat()',
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
		guiFactory.doButton2(sdkRow,'Select Driven Joints',
				             'tdToolsLib.doSelectDrivenJoints(cgmTDToolsWin)',
				             "Selects driven joints from an sdk attribute")


		sdkRow.layout()
		mc.setParent(parent)
		guiFactory.lineSubBreak()


	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Deformer Tools
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildSkinClusterTool(self,parent, vis=True):
		containerName = 'SkinClusterContainer'
		self.containerName = MelColumn(parent,vis=vis)

		mc.setParent(self.containerName)
		guiFactory.header('Query')
		guiFactory.lineSubBreak()


		#>>> Find excess weights Tool
		if not mc.optionVar( ex='cgmVarMaxInfluenceVerts' ):
			mc.optionVar( iv=('cgmVarMaxInfluenceVerts', 3) )

		FindExcessVertsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5)
		MelSpacer(FindExcessVertsRow,w=10)
		MelLabel(FindExcessVertsRow,l='Find verts with excess influence',align='left')

		FindExcessVertsRow.setStretchWidget(MelLabel(FindExcessVertsRow,l='>>>'))

		MelLabel(FindExcessVertsRow,l='Max Verts:')

		self.MaxVertsField = MelIntField(FindExcessVertsRow, w= 50, v=mc.optionVar(q='cgmVarMaxInfluenceVerts'))

		guiFactory.doButton2(FindExcessVertsRow,'Find em!',
				             'mc.optionVar(iv=("cgmVarMaxInfluenceVerts",cgmTDToolsWin.MaxVertsField(q=True,v=True)));tdToolsLib.doReturnExcessInfluenceVerts()',
				             'Prioritizes a loaded source object. If none is loaded. Attempts to use selected')
		MelSpacer(FindExcessVertsRow,w=10)
		FindExcessVertsRow.layout()

		mc.setParent(self.containerName)
		guiFactory.lineSubBreak()

		#>>> Influence tools
		InfluencesRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
		guiFactory.doButton2(InfluencesRow,'Select Influences',
				             'tdToolsLib.doSelectInfluenceJoints()',
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
				             'tdToolsLib.doCopyWeightsFromFirstToOthers()',
				             "Copies the weights from one vert to another.")
		guiFactory.doButton2(SkinWeightsCopyRow,'Vert from closest', 
				             'tdToolsLib.doCopySkinningToVertFromSource()',
				             "Copies the weights to a vert from \n the closest vert on the source.")
		guiFactory.doButton2(SkinWeightsCopyRow,'Object to objects', 
				             'tdToolsLib.doTransferSkinning()',
				             "Copies the weights from one object to others.")

		SkinWeightsCopyRow.layout()
		mc.setParent(self.containerName)
		guiFactory.lineSubBreak()




		return self.containerName

	def buildBlendshapeTool(self,parent, vis=True):
		containerName = 'BlendShapeContainer'
		self.containerName = MelColumn(parent,vis=vis)

		#clear our variables
		if not mc.optionVar( ex='cgmVarBSBakeInbetweens' ):
			mc.optionVar( iv=('cgmVarBSBakeInbetweens', 0) )
		if not mc.optionVar( ex='cgmVarBSBakeTransferConnections' ):
			mc.optionVar( iv=('cgmVarBSBakeTransferConnections', 0) )
		if not mc.optionVar( ex='cgmVarBSBakeCombine' ):
			mc.optionVar( iv=('cgmVarBSBakeCombine', 0) )


		mc.setParent(self.containerName)
		guiFactory.header('Baker')
		guiFactory.lineSubBreak()

		#>>> Baker Option Row
		BakerSettingsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5)
		MelSpacer(BakerSettingsRow,w=5)

		self.uiBlendShapeBakeInbetweensOptionCB = MelCheckBox(BakerSettingsRow,l='Inbetweens',
				                                              onCommand = lambda *a: mc.optionVar(iv=('cgmVarBSBakeInbetweens',1)),
				                                              offCommand = lambda *a: mc.optionVar(iv=('cgmVarBSBakeInbetweens',0)),
				                                              annotation = "Do inbetween targets as well",
				                                              v = (mc.optionVar(query='cgmVarBSBakeInbetweens')))

		self.uiBlendShapeBakeTransferConnectionsCB = MelCheckBox(BakerSettingsRow,l='Transfer Connections',
				                                                 onCommand = lambda *a: mc.optionVar(iv=('cgmVarBSBakeTransferConnections',1)),
				                                                 offCommand = lambda *a: mc.optionVar(iv=('cgmVarBSBakeTransferConnections',0)),
				                                                 annotation = "Creates a blendShape node on the target object(s)\n Attempts to transfer the connections for\n the bake blendshape node to the new one",
				                                                 v = (mc.optionVar(query='cgmVarBSBakeTransferConnections')))
		self.uiBlendShapeBakeCombineOptionCB = MelCheckBox(BakerSettingsRow,l='Combine',
				                                           onCommand = lambda *a: mc.optionVar(iv=('cgmVarBSBakeCombine',1)),
				                                           offCommand = lambda *a: mc.optionVar(iv=('cgmVarBSBakeCombine',0)),
				                                           v = (mc.optionVar(query='cgmVarBSBakeCombine')),
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
				             'tdToolsLib.doBakeBlendShapeTargetsFromSource(cgmTDToolsWin)',
				             "Bakes out the targets of an object's blendshape node.")
		guiFactory.doButton2(BakerButtonsRow,'Bake to Target(s)',
				             'tdToolsLib.doBakeBlendShapeTargetsToTargetsFromSource(cgmTDToolsWin)',
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
		if not mc.optionVar( ex='cgmVarPoseBufferTransferConnections' ):
			mc.optionVar( iv=('cgmVarPoseBufferTransferConnections', 1) )
		if not mc.optionVar( ex='cgmVarPoseBufferDoConnect' ):
			mc.optionVar( iv=('cgmVarPoseBufferDoConnect', 1) )
		if not mc.optionVar( ex='cgmVarPoseBufferDoRemoveMissing' ):
			mc.optionVar( iv=('cgmVarPoseBufferDoRemoveMissing', 1) )

		#>>> Option Row
		PoseBufferSettingsRow = MelHSingleStretchLayout(self.containerName,ut='cgmUISubTemplate',padding = 5)
		MelSpacer(PoseBufferSettingsRow,w='5')
		MelLabel(PoseBufferSettingsRow,l='Options: ', align = 'right')
		PoseBufferSettingsRow.setStretchWidget(MelSpacer(PoseBufferSettingsRow))
		self.uiPoseBufferDoConnectOptionCB = MelCheckBox(PoseBufferSettingsRow,l='Connect',
				                                         onCommand = lambda *a: mc.optionVar(iv=('cgmVarPoseBufferDoConnect',1)),
				                                         offCommand = lambda *a: mc.optionVar(iv=('cgmVarPoseBufferDoConnect',0)),
				                                         annotation = 'Connects blendShape channels to corresponding \n buffer channels',
				                                         v = (mc.optionVar(query='cgmVarPoseBufferDoConnect')) )

		self.uiPoseBufferTransferConnectionsCB = MelCheckBox(PoseBufferSettingsRow,l='Transfer Connections',
				                                             onCommand = lambda *a: mc.optionVar(iv=('cgmVarPoseBufferTransferConnections',1)),
				                                             offCommand = lambda *a: mc.optionVar(iv=('cgmVarPoseBufferTransferConnections',0)),
				                                             annotation = "Transfers sdk or expression \n connections driving the blendshape \nchannels to the buffer",
				                                             v = (mc.optionVar(query='cgmVarPoseBufferTransferConnections')))

		self.uiPoseBufferDoRemoveMissing = MelCheckBox(PoseBufferSettingsRow,l='Remove Missing',
				                                       onCommand = lambda *a: mc.optionVar(iv=('cgmVarPoseBufferDoRemoveMissing',1)),
				                                       offCommand = lambda *a: mc.optionVar(iv=('cgmVarPoseBufferDoRemoveMissing',0)),
				                                       annotation = "Removes bs channels that have been deleted from the buffer",
				                                       v = (mc.optionVar(query='cgmVarPoseBufferDoRemoveMissing')) )

		PoseBufferSettingsRow.layout()

		mc.setParent(self.containerName)
		guiFactory.lineSubBreak()

		#>>> Pose Buffer Buttons Row
		mc.setParent(self.containerName)
		guiFactory.lineSubBreak()

		PoseBufferButtonsRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
		guiFactory.doButton2(PoseBufferButtonsRow,'Load',
				             'tdToolsLib.doLoadBlendShapePoseBuffer(cgmTDToolsWin)',
				             "Loads blendshape information from an object",
				             enable = True)

		guiFactory.doButton2(PoseBufferButtonsRow,'Create', 
				             'tdToolsLib.doCreatePoseBuffer(cgmTDToolsWin)',
				             "Creates a pose buffer",
				             enable = True)
		guiFactory.doButton2(PoseBufferButtonsRow,'Update', 
				             'tdToolsLib.doUpdatePoseBuffer(cgmTDToolsWin)',
				             "Updates a blendshape poseBuffer if you've added or removed blendshapeChannels")


		PoseBufferButtonsRow.layout()


		mc.setParent(self.containerName)
		guiFactory.lineSubBreak()
		guiFactory.lineBreak()



		return self.containerName


	def buildUtilitiesTool(self,parent, vis=True):
		containerName = 'DeformerUtilitiesContainer'

		self.containerName = MelColumn(parent,vis=vis)
		mc.setParent(self.containerName )
		guiFactory.header('Shrink wrap')
		guiFactory.lineSubBreak()

		ShrinkWrapRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)

		guiFactory.doButton2(ShrinkWrapRow,'Shrink wrap to source',
				             'tdToolsLib.doShrinkWrapToSource()',
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
				             'tdToolsLib.doLoadPolyUnite(cgmTDToolsWin)',
				             "Attempts to load polyUnite and select the source shapes")
		guiFactory.doButton2(PolyUniteRow,'Build polyUnite',
				             'tdToolsLib.doBuildPolyUnite(cgmTDToolsWin)',
				             "Builds a poly unite geo node from target or \n selected objects (checks for mesh types_")
		guiFactory.doButton2(PolyUniteRow,'Remove polyUnite',
				             'tdToolsLib.doDeletePolyUniteNode(cgmTDToolsWin)',
				             "Builds a poly unite geo node from target or \n selected objects (checks for mesh types_")

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
				             'tdToolsLib.doDeformerKeyableAttributesConnect(cgmTDToolsWin)',
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
		if not mc.optionVar( ex='cgmVarAutoNameObject' ):
			mc.optionVar( sv=('cgmVarAutoNameObject', '') )

		LoadAutoNameObjectRow = MelHSingleStretchLayout(self.containerName ,ut='cgmUISubTemplate',padding = 5)

		MelSpacer(LoadAutoNameObjectRow,w=5)

		MelLabel(LoadAutoNameObjectRow,l='Object:',align='right')

		self.AutoNameObjectField = MelTextField(LoadAutoNameObjectRow, w= 125, ut = 'cgmUIReservedTemplate', editable = False)
		if mc.optionVar( q = 'cgmVarAutoNameObject'):
			self.SourceObjectField(edit=True,text = mc.optionVar( q = 'cgmVarAutoNameObject'))

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
		
		#>>> Multitag
		mc.setParent(self.containerName )
		guiFactory.header('Selection based tools')
		guiFactory.lineSubBreak()

		multiTagRow = MelHLayout(self.containerName ,ut='cgmUISubTemplate',padding = 2)
		
		MelSpacer(multiTagRow,w=5)
		MelLabel(multiTagRow,label = 'Multi tag>>>>')

		self.multiTagInfoField = MelTextField(multiTagRow,
		                                      enable = True,
		                                      bgc = dictionary.returnStateColor('normal'),
		                                      ec = lambda *a: tdToolsLib.uiMultiTagObjects(self),
		                                      w = 75)
		

		self.cgmMultiTagOptions = MelOptionMenu(multiTagRow,l = 'Pick a tag:')
		
		for tag in 'Name','Type','Direction','Position','NameModifier','TypeModifier','DirectionModifier':
			self.cgmMultiTagOptions.append(tag)
			
		self.cgmMultiTagOptions(edit = True, select = 1)

		MelSpacer(multiTagRow,w=5)

		"""
		ec = lambda *a: tdToolsLib.uiUpdateAutoNameTag(self,'cgmDirectionModifier'),

		"""

		multiTagRow.layout()
		mc.setParent(self.containerName )
		guiFactory.lineSubBreak()

		
		
		
		#>>> Basic
		mc.setParent(self.containerName )

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
				             "guiFactory.doLoadSingleObjectToTextField(cgmTDToolsWin.SourceObjectField,'cgmVarSourceObject')",
				             'Load to field')


		MelLabel(LoadObjectTargetUtilityRow,l='Target:',align='right')
		self.TargetObjectField = MelTextField(LoadObjectTargetUtilityRow, w=125, ut = 'cgmUIReservedTemplate', editable = False)

		LoadObjectTargetUtilityRow.setStretchWidget(self.BaseNameField )

		guiFactory.doButton2(LoadObjectTargetUtilityRow,'<<',
				             "guiFactory.doLoadMultipleObjectsToTextField(cgmTDToolsWin.TargetObjectField,False,'cgmVarTargetObjects')",
				             'Load to field')

		MelSpacer(LoadObjectTargetUtilityRow,w=5)

		LoadObjectTargetUtilityRow.layout()


		mc.setParent(parent)
		guiFactory.lineSubBreak()
	
	def buildLoadObjectTargetTool(self,parent,baseNameField=True):
		#clear our variables
		if not mc.optionVar( ex='cgmVarSourceObject' ):
			mc.optionVar( sv=('cgmVarSourceObject', '') )
		if not mc.optionVar( ex='cgmVarTargetObjects' ):
			mc.optionVar( sv=('cgmVarTargetObjects', '') )


		LoadObjectTargetUtilityRow = MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

		MelSpacer(LoadObjectTargetUtilityRow,w=5)

		if baseNameField:
			MelLabel(LoadObjectTargetUtilityRow,l='Base Name:',align='right')
			self.BaseNameField = MelTextField(LoadObjectTargetUtilityRow,backgroundColor = [1,1,1],w=60,
						                      annotation = "Base name for our various tools to use")

		MelLabel(LoadObjectTargetUtilityRow,l='Source:',align='right')

		self.SourceObjectField = MelTextField(LoadObjectTargetUtilityRow, w= 125, ut = 'cgmUIReservedTemplate', editable = False)
		if mc.optionVar( q = 'cgmVarSourceObject'):
			self.SourceObjectField(edit=True,text = mc.optionVar( q = 'cgmVarSourceObject'))

		guiFactory.doButton2(LoadObjectTargetUtilityRow,'<<',
				             "guiFactory.doLoadSingleObjectToTextField(cgmTDToolsWin.SourceObjectField,'cgmVarSourceObject')",
				             'Load to field')


		MelLabel(LoadObjectTargetUtilityRow,l='Target:',align='right')
		self.TargetObjectField = MelTextField(LoadObjectTargetUtilityRow, w=125, ut = 'cgmUIReservedTemplate', editable = False)

		LoadObjectTargetUtilityRow.setStretchWidget(self.BaseNameField )

		guiFactory.doButton2(LoadObjectTargetUtilityRow,'<<',
				             "guiFactory.doLoadMultipleObjectsToTextField(cgmTDToolsWin.TargetObjectField,False,'cgmVarTargetObjects')",
				             'Load to field')

		MelSpacer(LoadObjectTargetUtilityRow,w=5)

		LoadObjectTargetUtilityRow.layout()


		mc.setParent(parent)
		guiFactory.lineSubBreak()


	def buildModeSetUtilityRow(self,parent,RadioCollectionName,ModeSelectionChoicesList, SectionLayoutCommands, cgmVarName,OptionList,labelText = 'Choose: '):
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# General purpose mode setter
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		if not mc.optionVar( ex=cgmVarName ):
			mc.optionVar( sv=(cgmVarName, OptionList[0]) )

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
						                                                               onCommand = lambda *a: guiFactory.toggleModeState(item,OptionList,cgmVarName,ContainerList)))

		"""
        for item in OptionList:
            self.ModeSelectionChoicesList.append(self.RadioCollectionName.createButton(ModeSetRow,label=item,
                                                                                 onCommand = ('%s%s%s%s%s' %("mc.optionVar( sv=('",cgmVarName,"','",item,"'))"))))
        """

		mc.radioCollection(self.RadioCollectionName,edit=True, sl=self.ModeSelectionChoicesList[OptionList.index(mc.optionVar(q=cgmVarName))])
		ModeSetRow.layout()


	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Position Components
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildRowColumnUIRow(self,parent):
		if not mc.optionVar( ex='cgmVarRowColumnCount' ):
			mc.optionVar( iv=('cgmVarRowColumnCount', 3) )
		if not mc.optionVar( ex='cgmVarOrderByName' ):
			mc.optionVar( iv=('cgmVarOrderByName', 0) )

		self.RowColumnLayoutModes = ['Column','Row']

		RowColumnLayoutModeRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 20)

		MelLabel(RowColumnLayoutModeRow, l='Number of Columns:',w=30)
		self.RowColumnIntField = MelIntField(RowColumnLayoutModeRow,w=30,v=(mc.optionVar(q='cgmVarRowColumnCount')))

		self.OrderByNameCheckBox = MelCheckBox(RowColumnLayoutModeRow,l = 'Arrange by Name',
				                               onCommand = lambda *a: mc.optionVar(sv=('cgmVarOrderByName',1)),
				                               offCommand = lambda *a: mc.optionVar(sv=('cgmVarOrderByName',0)))


		RowColumnLayoutModeRow.layout()

		#mc.radioCollection(self.uiRowColumnLayoutModeOptionGroup ,edit=True,sl= self.RowColumnLayoutModeCollectionChoices[ mc.optionVar(q='cgmRowColumnLayoutMode') ] )




	def buildSurfaceSnapAimRow(self,parent):
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		# World Up Axis
		#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		if not mc.optionVar( ex='cgmVarSurfaceSnapAimMode' ):
			mc.optionVar( iv=('cgmVarSurfaceSnapAimMode', 0) )

		self.surfaceSnapAimModes = ['Normal','Start Pos']

		surfaceSnapAimModeRow = MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
		MelLabel(surfaceSnapAimModeRow, label = 'Orient to: ')
		self.uiSurfaceSnapAimModeOptionGroup = MelRadioCollection()
		self.surfaceSnapAimModeCollectionChoices = []
		for item in self.surfaceSnapAimModes:
			cnt = self.surfaceSnapAimModes.index(item)
			if mc.optionVar( q='cgmVarSurfaceSnapAimMode' ) == cnt:
				checkState = True
			else:
				checkState = False
			self.surfaceSnapAimModeCollectionChoices.append(self.uiSurfaceSnapAimModeOptionGroup.createButton(surfaceSnapAimModeRow,label=item,
						                                                                                      onCommand = ("mc.optionVar( iv=('cgmVarSurfaceSnapAimMode',%i))" % cnt)))

		mc.radioCollection(self.uiSurfaceSnapAimModeOptionGroup ,edit=True,sl= self.surfaceSnapAimModeCollectionChoices[ mc.optionVar(q='cgmVarSurfaceSnapAimMode') ] )
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
						                                                                          onCommand = ('%s%s%s' %("mc.optionVar( sv=('cgmVarObjectUpAxis','",item,"'))"))))

		mc.radioCollection(self.uiObjectUpAxisOptionGroup ,edit=True,sl= (self.objectUpAxisCollectionChoices[ self.axisOptions.index(mc.optionVar(q='cgmVarObjectUpAxis')) ]))
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
						                                                                            onCommand = ('%s%s%s' %("mc.optionVar( sv=('cgmVarObjectAimAxis','",item,"'))"))))

		mc.radioCollection(self.uiObjectAimAxisOptionGroup ,edit=True,sl= (self.objectAimAxisCollectionChoices[ self.axisOptions.index(mc.optionVar(q='cgmVarObjectAimAxis')) ]))
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
						                                                                        onCommand = ('%s%s%s' %("mc.optionVar( sv=('cgmVarWorldUpAxis','",item,"'))"))))

		mc.radioCollection(self.uiWorldUpAxisOptionGroup ,edit=True,sl= (self.worldUpAxisCollectionChoices[ self.axisOptions.index(mc.optionVar(q='cgmVarWorldUpAxis')) ]))
		worldUpRow.layout()