"""
------------------------------------------
GuiFactory: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Class based ui builder for cgmTools
================================================================
"""
#>>> Root settings =============================================================
__version__ = '0.1.01242013'
__toolName__ = 'cgmGUI'
__toolURL__ = 'www.cgmonks.com'
__author__ = 'Josh Burton'
__owner__ = 'CG Monks'
__website__ = 'www.cgmonks.com'

#These feed to Hamish's basemel ui stuff
USE_Template = 'cgmUITemplate'
WINDOW_NAME = 'cgmGUI'
WINDOW_TITLE = '%s - %s'%(__toolName__,__version__)
DEFAULT_SIZE = 250, 400
DEFAULT_MENU = None
RETAIN = True
MIN_BUTTON = True
MAX_BUTTON = False
FORCE_DEFAULT_SIZE = False  #always resets the size of the window when its re-created


#>>> From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel
import copy

#>>> From cgm ==============================================================
from cgm.lib.classes import NameFactory as nFactory
reload(nFactory)
from cgm.core import cgm_Meta as cgmMeta

from cgm.lib import (search,
                     guiFactory,
                     dictionary)

from cgm.lib.zoo.zooPyMaya.baseMelUI import *

#>>> From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

#def run():
    #cgmMorphyMakerWin = morphyMakerClass()

class cgmGUI(BaseMelWindow):
    """
    Base CG Monks core gui
    """
    USE_Template = USE_Template
    WINDOW_NAME = WINDOW_NAME
    WINDOW_TITLE = WINDOW_TITLE
    DEFAULT_SIZE = DEFAULT_SIZE
    DEFAULT_MENU = DEFAULT_MENU
    RETAIN = RETAIN
    MIN_BUTTON =MIN_BUTTON
    MAX_BUTTON =MAX_BUTTON
    FORCE_DEFAULT_SIZE = FORCE_DEFAULT_SIZE
    def __init__( self,*args,**kws):
        log.info(">>> cgmGUI.__init__")
        if kws:log.info("kws: %s"%str(kws))
        if args:log.info("args: %s"%str(args))
        initializeTemplates() 
        __toolName__ = 'cgmGUI'
        self.description = 'This is a series of tools for working with cgm Sets'
        self.dockCnt = '%sDock'%__toolName__			
        self.optionVars = []
        self.showHelp = False
        self.helpBlurbs = []
        self.oldGenBlurbs = []

        #>>>Menu
        #====================
        self.buildMenus()
        #self.ShowHelpOption = mc.optionVar( q='cgmVar_AnimToolsShowHelp' )
        
        #>>>Body
        #====================        
        self.layout_wapper(self)
        
        #====================
        # Show and Dock
        #====================
        #Maya2011 QT docking - from Red9's examples
        try:
            #'Maya2011 dock delete'
            if mc.dockControl(self.dockCnt, exists=True):
                mc.deleteUI(self.dockCnt, control=True)  
        except:
            pass
        
        log.info(self.ov_Dock.value)
        if self.ov_Dock.value:
            allowedAreas = ['right', 'left']
            mc.dockControl(self.dockCnt, area='right', label=self.WINDOW_TITLE, content=self.WINDOW_NAME, floating=False, allowedArea=allowedAreas, width=400)
            #except:
                #Dock failed, opening standard Window	
                #log.warning('Failed to dock')
                #self.show()
        else:self.show()


    def setupVariables(self):
        self.doCreateGuiOptionVar('ShowHelp',defaultValue = 0)
        self.doCreateGuiOptionVar('Dock',defaultValue = 1)
        self.doCreateGuiOptionVar('DebugMode',defaultValue = 0)
 	
    def doCreateGuiOptionVar(self,varName,*args,**kws):
        fullName = "cgmVar_%s%s"%(__toolName__,varName)
        if args:args[0] = fullName
        if kws and 'varName' in kws.keys():kws.pop('varName')
        self.__dict__['ov_%s'%varName] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        log.info('ov_%s'%varName)
        if fullName not in self.optionVars:
            self.optionVars.append(fullName)
            
    #=========================================================================
    # Menu Building
    #=========================================================================
    def buildMenus(self):
        self.setupVariables()
        self.UI_OptionsMenu = MelMenu( l='Options', pmc=self.buildOptionsMenu)		
        self.UI_HelpMenu = MelMenu( l='Help', pmc=self.buildHelpMenu)   
        
        
    def buildOptionsMenu( self, *a ):
        self.UI_OptionsMenu.clear()
        MelMenuItem( self.UI_OptionsMenu, l="Force module menu reload",
                     c=lambda *a:morphyMakerLib.uiForceModuleUpdateUI(self))		

    def buildHelpMenu( self, *a ):
        self.UI_HelpMenu.clear()
        MelMenuItem( self.UI_HelpMenu, l="Show Help",
                     cb=self.ov_ShowHelp.value,
                     c= lambda *a: self.do_showHelpToggle())

        MelMenuItem( self.UI_HelpMenu, l="Print Tools Help",
                     c=lambda *a: self.printHelp() )

        MelMenuItemDiv( self.UI_HelpMenu )
        MelMenuItem( self.UI_HelpMenu, l="About",
                     c=lambda *a: self.showAbout() )
        MelMenuItem( self.UI_HelpMenu, l="Debug",
                     cb=self.ov_DebugMode.value,
                     c= lambda *a: self.ov_DebugMode.toggle())			

    #>> Menu Functions
    #=========================================================================    
    def reset(self):	
        Callback(guiFactory.resetGuiInstanceOptionVars(self.optionVars,run))

    def reload(self):	
        run()
        
    def do_dockToggle( self):
        self.ov_Dock.toggle()
        
    def do_showHelpToggle( self):
        guiFactory.toggleMenuShowState(self.ov_ShowHelp.value,self.helpBlurbs)
        self.ov_ShowHelp.toggle()

    def showAbout(self):
        window = mc.window( title="About", iconName='About', ut = 'cgmUITemplate',resizeToFitChildren=True )
        mc.columnLayout( adjustableColumn=True )
        guiFactory.header(__toolName__,overrideUpper = True)
        mc.text(label='>>>A Part of the cgmTools Collection<<<', ut = 'cgmUIInstructionsTemplate')
        guiFactory.headerBreak()
        guiFactory.lineBreak()
        descriptionBlock = guiFactory.textBlock(self.description)

        guiFactory.lineBreak()
        mc.text(label=('%s%s' %('Written by: ',__author__)))
        mc.text(label=('%s%s%s' %('Copyright ',__owner__,', 2011')))
        guiFactory.lineBreak()
        mc.text(label='Version: %s' % __version__)
        mc.text(label='')
        guiFactory.doButton('Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://www.cgmonks.com/tools/maya-tools/morphyMaker/")')
        guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
        mc.setParent( '..' )
        mc.showWindow( window )

    def printHelp(self):pass
        #help(morphyMakerLib)

    def printReport(self):pass
        #morphyMakerLib.printReport(self)
    
    #=========================================================================
    # Layouts
    #=========================================================================
    def layout_wapper(self,parent):
        def modeSet( item ):
            i =  self.setModes.index(item)
            self.SetToolsModeOptionVar.set( i )
            self.setMode = i

        MainForm = MelColumnLayout(parent)
        SetHeader = guiFactory.header('HI')


#=========================================================================
# Define our Colors
#=========================================================================
def setBGColorState(textFieldToChange, newState):
    mc.textField(textFieldToChange,edit = True, bgc = dictionary.returnStateColor(newState))
#=========================================================================
# Define our Templates
#=========================================================================
def initializeTemplates():
    guiBackgroundColor = [.45,.45,.45]
    guiTextFieldColor = [.4,.4,.4]    
    guiHeaderColor = [.25,.25,.25]
    guiSubMenuColor = [.65,.65,.65]
    guiButtonColor = [.35,.35,.35]
    guiHelpBackgroundColor = [0.8, 0.8, 0.8]
    guiHelpBackgroundReservedColor = [0.411765 , 0.411765 , 0.411765]
    guiHelpBackgroundLockedColor = [0.837, 0.399528, 0.01674]

    if mc.uiTemplate( 'cgmUITemplate', exists=True ):
        mc.deleteUI( 'cgmUITemplate', uiTemplate=True )
    mc.uiTemplate('cgmUITemplate')
    mc.separator(dt='cgmUITemplate', height = 10, style = 'none')
    mc.button(dt = 'cgmUITemplate', height = 15, backgroundColor = guiButtonColor,align = 'center')
    mc.window(dt = 'cgmUITemplate', backgroundColor = guiBackgroundColor)
    mc.optionMenu(dt='cgmUITemplate',backgroundColor = guiButtonColor)
    mc.optionMenuGrp(dt ='cgmUITemplate', backgroundColor = guiButtonColor)
    mc.textField(dt = 'cgmUITemplate',backgroundColor = [1,1,1],h=20)
    mc.formLayout(dt='cgmUITemplate', backgroundColor = guiBackgroundColor)    
    mc.textScrollList(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 
    mc.frameLayout(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 

    # Define our header template
    if mc.uiTemplate( 'cgmUIHeaderTemplate', exists=True ):
        mc.deleteUI( 'cgmUIHeaderTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUIHeaderTemplate')
    mc.text(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
    mc.separator(dt='cgmUIHeaderTemplate', height = 5, style = 'none',backgroundColor = guiHeaderColor)
    mc.formLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)    
    mc.rowLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
    mc.rowColumnLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
    mc.columnLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)  
    mc.textScrollList(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor) 
    mc.frameLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor) 

    # Define our sub template
    if mc.uiTemplate( 'cgmUISubTemplate', exists=True ):
        mc.deleteUI( 'cgmUISubTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUISubTemplate')
    mc.formLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.text(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.separator(dt='cgmUISubTemplate', height = 2, style = 'none', backgroundColor = guiSubMenuColor)
    mc.rowLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.rowColumnLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.columnLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.scrollLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.textField(dt = 'cgmUISubTemplate',backgroundColor = [1,1,1],h=20)
    mc.textScrollList(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 
    mc.frameLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 


    # Define our instructional template
    if mc.uiTemplate( 'cgmUIInstructionsTemplate', exists=True ):
        mc.deleteUI( 'cgmUIInstructionsTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUIInstructionsTemplate')
    mc.text(dt = 'cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
    mc.formLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)    
    mc.rowLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
    mc.rowColumnLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
    mc.columnLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)    
    mc.textField(dt = 'cgmUIInstructionsTemplate',backgroundColor = [1,1,1],h=20)
    mc.textScrollList(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor) 
    mc.frameLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor) 

    # Define our Reserved
    if mc.uiTemplate( 'cgmUIReservedTemplate', exists=True ):
        mc.deleteUI( 'cgmUIReservedTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUIReservedTemplate')
    mc.textField(dt = 'cgmUIReservedTemplate', backgroundColor = guiTextFieldColor,h=20)
    mc.formLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)    
    mc.rowLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)
    mc.rowColumnLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)
    mc.columnLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)  
    mc.frameLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor) 

    # Define our Locked
    if mc.uiTemplate( 'cgmUILockedTemplate', exists=True ):
        mc.deleteUI( 'cgmUILockedTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUILockedTemplate')
    mc.textField(dt = 'cgmUILockedTemplate', backgroundColor = guiHelpBackgroundLockedColor, h=20)
    mc.frameLayout(dt='cgmUILockedTemplate', backgroundColor = guiHelpBackgroundLockedColor) 

def resetGuiInstanceOptionVars(optionVarHolder,commandToRun = False):
    if optionVarHolder:
        purgeOptionVars(optionVarHolder)
    if commandToRun:    
        commandToRun()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Standard functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>