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
__description__ = "This is a default cgm gui example"
__author__ = 'Josh Burton'
__owner__ = 'CG Monks'
__website__ = 'www.cgmonks.com'
__defaultSize__ = 200, 300

#>>> From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel
import copy
from cgm.core import cgm_General as cgmGeneral

mayaVersion = int( mel.eval( 'getApplicationVersionAsFloat' ) )

# Maya version check
if mayaVersion >= 2011:
    currentGenUI = True
else:
    currentGenUI = False

#>>> From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib import (search,
                     guiFactory,
                     dictionary)

from cgm.lib.zoo.zooPyMaya import baseMelUI as mUI

#>>> From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

def run():
    win = cgmGUI()

class cgmGUI(mUI.BaseMelWindow):
    """
    Base CG Monks core gui
    """
    #These feed to Hamish's basemel ui stuff
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = __toolName__
    WINDOW_TITLE = '%s - %s'%(__toolName__,__version__)
    DEFAULT_SIZE = __defaultSize__
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created

    def __init__( self,*args,**kws):
        #Check our tool option var for debug mode to set logger level if so
        if mc.optionVar(exists = "cgmVar_guiDebug") and mc.optionVar(q="cgmVar_guiDebug"):
            log.setLevel(logging.DEBUG)	

        #>>> Standard cgm variables
        #====================	    
        self.l_optionVars = []
        self.l_helpElements = []
        self.l_oldGenElements = []
        self.description = __description__

        self.initializeTemplates() 

        #>>> Insert our init, overloaded for other tools
        self.insert_init(*args,**kws)

        #>>> Menu
        self.setup_Variables()	
        self.build_menus()

        #>>> Body
        #====================        
        self.build_layoutWrapper(self)

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

        self.show()
        #log.info(self.l_allowedDockAreas[self.var_DockSide.value])
        if self.var_Dock.value:
            try:mc.dockControl(self.dockCnt, area=self.l_allowedDockAreas[self.var_DockSide.value], label=self.WINDOW_TITLE, content=self.WINDOW_NAME, floating=not self.var_Dock.value, allowedArea=self.l_allowedDockAreas, width=self.DEFAULT_SIZE[0])
            except:
                log.warning('Failed to dock')

    def insert_init(self,*args,**kws):
        """ This is meant to be overloaded per gui """
        log.debug(">>> cgmGUI.__init__")	
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        log.debug(self.__call__(q=True, title=True))
        log.info("WINDOW_NAME: '%s'"%cgmGUI.WINDOW_NAME)
        log.info("WINDOW_TITLE: '%s'"%cgmGUI.WINDOW_TITLE)
        log.info("DEFAULT_SIZE: %s"%str(cgmGUI.DEFAULT_SIZE))
        self.description = 'This is a series of tools for working with cgm Sets'
        self.__version__ = __version__
        self.dockCnt = '%sDock'%__toolName__	
        self.__toolName__ = __toolName__		
        self.l_allowedDockAreas = ['right', 'left']
        self.WINDOW_NAME = cgmGUI.WINDOW_NAME
        self.WINDOW_TITLE = cgmGUI.WINDOW_TITLE
        self.DEFAULT_SIZE = cgmGUI.DEFAULT_SIZE

    def setup_Variables(self):
        self.create_guiOptionVar('ShowHelp',defaultValue = 0)
        self.create_guiOptionVar('Dock',defaultValue = 1)
        self.create_guiOptionVar('DockSide',defaultValue = 0)	
        self.create_cgmDebugOptionVar(defaultValue = 0)

    def create_guiOptionVar(self,varName,*args,**kws):
        fullName = "cgmVar_%s%s"%(self.__toolName__,varName)
        if args:args[0] = fullName
        if kws and 'varName' in kws.keys():kws.pop('varName')
        self.__dict__['var_%s'%varName] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        log.debug('var_%s'%varName)
        if fullName not in self.l_optionVars:
            self.l_optionVars.append(fullName)
        return fullName

    def create_cgmDebugOptionVar(self,*args,**kws):
        fullName = "cgmVar_guiDebug"
        self.__dict__['var_DebugMode'] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        if fullName not in self.l_optionVars:
            self.l_optionVars.append(fullName)
    #=========================================================================
    # Menu Building
    #=========================================================================
    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu( l='Root', pmc=self.buildMenu_first)		        
        self.uiMenu_OptionsMenu = mUI.MelMenu( l='Options', pmc=self.buildMenu_options)		
        self.uiMenu_HelpMenu = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)   

    def buildMenu_first( self, *args):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c=lambda *a: self.reload())		
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c=lambda *a: self.reset())    

    def buildMenu_options( self, *args):
        self.uiMenu_OptionsMenu.clear()
        #>>> Reset Options				
        mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Dock",
                         cb=self.var_Dock.value,
                         c= lambda *a: self.do_dockToggle())	      

    def buildMenu_help( self, *args):
        self.uiMenu_HelpMenu.clear()
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Show Help",
                         cb=self.var_ShowHelp.value,
                         c= lambda *a: self.do_showHelpToggle())

        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Print Tools Help",
                         c=lambda *a: self.printHelp() )

        mUI.MelMenuItemDiv( self.uiMenu_HelpMenu )
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="About",
                         c=lambda *a: self.showAbout() )

        # Update Mode
        iMenu_loggerMaster = mUI.MelMenuItem( self.uiMenu_HelpMenu, l='Logger Level', subMenu=True)
        mUI.MelMenuItem( iMenu_loggerMaster, l='Info',
                         c=lambda *a: self.set_loggingInfo())
        mUI.MelMenuItem( iMenu_loggerMaster, l='Debug',
                         c=lambda *a: self.set_loggingDebug())

    def set_loggingInfo(self):
        self.var_DebugMode.value = 0
        log.setLevel(logging.INFO)
    def set_loggingDebug(self):
        self.var_DebugMode.value = 1
        log.setLevel(logging.DEBUG)    

    #>> Menu Functions
    #=========================================================================    
    def reset(self):	
        Callback(do_resetGuiInstanceOptionVars(self.l_optionVars,run))

    def reload(self):	
        run()

    def do_dockToggle( self):
        self.var_Dock.toggle()
        if self.var_Dock.value:
            mc.dockControl(self.dockCnt, area=self.l_allowedDockAreas[self.var_DockSide.value], label=self.WINDOW_TITLE, content=self.WINDOW_NAME, floating=not self.var_Dock.value, allowedArea=self.l_allowedDockAreas, width=self.DEFAULT_SIZE[0])
        else:
            self.reload()            

    def do_showHelpToggle( self):
        doToggleInstancedUIItemsShowState(self.var_ShowHelp.value,self.l_helpElements)
        self.var_ShowHelp.toggle()

    def do_DebugModeToggle( self):
        self.var_DebugMode.toggle()	
        if self.var_DebugMode.value:
            log.setLevel(logging.DEBUG)	
            #self.log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
            #self.log.setLevel(logging.INFO)

    def showAbout(self):
        window = mc.window( title="About", iconName='About', ut = 'cgmUITemplate',resizeToFitChildren=True)
        column = mc.columnLayout( adjustableColumn=True )
        add_Header(self.__toolName__,overrideUpper = True)
        mc.text(label='>>>A Part of the cgmTools Collection<<<', ut = 'cgmUIInstructionsTemplate')
        add_HeaderBreak()

        add_TextBlock(self.description)

        add_LineBreak()
        mc.text(label=('%s%s' %('Written by: ',__author__)))
        mc.text(label=('%s%s%s' %('Copyright ',__owner__,', 2011')))
        add_LineBreak()
        mc.text(label='Version: %s' % self.__version__)
        mc.text(label='')
        add_Button(column,'Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://www.cgmonks.com/tools/maya-tools/morphyMaker/")')
        add_Button(column,'Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
        mc.setParent( '..' )
        mc.showWindow( window )

    def printHelp(self):pass
        #help(morphyMakerLib)

    def do_DebugEchoTest(self):
        log.info('#'+'='*25)
        log.info('Tool: %s'%self.__toolName__)	
        log.info("Info call")
        log.debug("Debug call")
        log.warning("warning call")


    #=========================================================================
    # Layouts
    #=========================================================================
    def build_layoutWrapper(self,parent):
        def modeSet( item ):
            i =  self.setModes.index(item)
            self.SetToolsModeOptionVar.set( i )
            self.setMode = i

        MainForm = mUI.MelColumnLayout(parent)
        SetHeader = add_Header('HI')

        self.l_helpElements.extend(add_InstructionBlock(MainForm,"Purge all traces of cgmThinga tools from the object and so and so forth forever, amen.",vis = self.var_ShowHelp.value))        
        add_Button(MainForm)
        add_Button(MainForm,'Debug test', lambda *a: self.do_DebugEchoTest())
        add_MelLabel(MainForm,'asdfasdfasdf')

    def initializeTemplates(self):
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

#=========================================================================
# OptionVars
#=========================================================================
def do_resetGuiInstanceOptionVars(optionVarHolder,commandToRun = False):
    if optionVarHolder:
        do_purgeOptionVars(optionVarHolder)
    if commandToRun:    
        commandToRun()

def do_purgeOptionVars(varHolder):
    """
    Typically self.l_optionVars
    """
    sceneOptionVars = mc.optionVar(list=True)
    if varHolder:
        for var in varHolder:
            if var in sceneOptionVars:
                do_purgeOptionVar(var)

def do_purgeOptionVar(varName):
    if mc.optionVar(exists = varName):    
        mc.optionVar( remove=varName )
        print "'%s' removed"%varName
        return True
    return False
#=========================================================================
# Standard Layout stuff
#=========================================================================
def add_Button(parent, labelText = 'text', commandText = 'mc.warning("Fix this")',annotationText = '',*a,**kw):
    if currentGenUI:
        return 	mUI.MelButton(parent,l=labelText,ut = 'cgmUITemplate',
                                     c= commandText,
                                     height = 20,
                                     align = 'center',
                                     annotation = annotationText,*a,**kw)
    else:
        return mUI.MelButton(parent,l=labelText, backgroundColor = [.75,.75,.75],
                             c= commandText,
                             height = 20,
                             align = 'center',
                             annotation = annotationText,*a,**kw)

def add_Header(text = 'test', align = 'center',overrideUpper = False):
    if not overrideUpper:
        text = text.upper()
    if currentGenUI:
        return mc.text(text, al = align, ut = 'cgmUIHeaderTemplate')
    else:
        return mc.text(('%s%s%s' %('>>> ',text,' <<<')), al = align)

def add_HeaderBreak():
    if currentGenUI:
        return mc.separator(ut='cgmUIHeaderTemplate')
    else:
        return mc.separator(style='double')

def add_LineBreak():
    if currentGenUI:
        return mc.separator(ut='cgmUITemplate')
    else:
        return mc.separator(ut='cgmUITemplate')

def add_LineSubBreak(vis=True):
    if currentGenUI:
        return mc.separator(ut='cgmUISubTemplate',vis=vis)
    else:
        return mc.separator(style='single',vis=vis)

def add_SectionBreak():
    if currentGenUI:
        return mc.separator(ut='cgmUISubTemplate')
    else:
        return mc.separator(style='single')

def add_CheckBox(self,parent,optionVarName,*a,**kw):
    fullName = self.create_guiOptionVar(optionVarName)    

    return mUI.MelCheckBox(parent,
                           v = mc.optionVar(q=fullName),
                           onCommand = lambda *a: mc.optionVar(iv=(fullName,1)),
                           offCommand = lambda *a: mc.optionVar(iv=(fullName,0)),
                           *a,**kw)

def add_MelLabel(parent,text,**kws):
    return mUI.MelLabel(parent,label = text,ut = 'cgmUIInstructionsTemplate',al = 'center', ww = True,**kws)

def add_InstructionBlock(parent,text, align = 'center', vis = False, maxLineLength = 35, **kws):
    # yay, accounting for word wrap...
    if currentGenUI:
        return [mUI.MelLabel(parent,label= text, ut = 'cgmUIInstructionsTemplate',al = 'center', ww = True, visible = vis,**kws)]

    else:
        instructions = []
        textLines = return_SplitLines(text, maxLineLength)
        instructions.append(mUI.MelSeparator(parent,style='single', visible = vis))
        for line in textLines:
            instructions.append(mUI.MelLabel(parent,label = line, h = 15, al = align, visible = vis))
        instructions.append(mUI.MelSeparator(parent,style='single', visible = vis))

        return instruction

def add_InstructionBlockOLD(text, align = 'center', vis = False, maxLineLength = 35):

    # yay, accounting for word wrap...
    if currentGenUI:
        return [mc.text(text, ut = 'cgmUIInstructionsTemplate',al = 'center', ww = True, visible = vis)]

    else:
        instructions = []
        textLines = return_SplitLines(text, maxLineLength)
        instructions.append(mc.separator(style='single', visible = vis))
        for line in textLines:
            instructions.append(mc.text(line, h = 15, al = align, visible = vis))
        instructions.append(mc.separator(style='single', visible = vis))

        return instructions

def add_TextBlock(text, align = 'center'):
    # yay, accounting for word wrap...
    if currentGenUI:
        return [mc.text(text,al = 'center', ww = True, visible = True)]
    else:
        textBlock = []
        textLines = return_SplitLines(text, 50)
        textBlock.append(mc.separator(style = 'single', visible = True))
        for line in textLines:
            textBlock.append(mc.text(line, al = align, visible = True))
        textBlock.append(mc.separator(style = 'single', visible = True))
        return textBlock

def return_SplitLines(text, size):
    lineList = []
    wordsList = text.split(' ')
    baseCnt = 0
    cnt = 0
    max = len(wordsList)
    while cnt < max:
        buffer = ' '.join(wordsList[baseCnt:cnt + 1])
        if len(buffer) < size:
            cnt+=1
        else:
            baseCnt = cnt+1
            cnt = baseCnt
            lineList.append(buffer)
    if baseCnt < max:
        lineList.append(' '.join(wordsList[baseCnt:]))
    return lineList
#=========================================================================
# OptionVars
#=========================================================================
def doToggleInstancedUIItemsShowState(stateToggle,instanceList = None):
    newstate = not stateToggle
    for i_item in instanceList:
        try:
            i_item(edit = True, visible = newstate)
        except:
            log.warning("'%s' failed to doToggleInstancedUIItemsShowState"%i_item)
    return newstate

def doSetInstancedUIItemsEnableState(state = None,instanceList = None):
    if state is None:
        log.warning("'%s' not a valid argument for doSetInstancedUIItemsEnableState"%str(state))	
        return 
    for i_item in instanceList:
        try:
            i_item(edit = True, enable = state)
        except:
            log.warning("'%s' failed to doSetInstancedUIItemsEnableState"%i_item)
    return state

def doToggleMenuShowState(stateToggle, listOfItems):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Toggle for turning off and on the visibility of a menu section

    ARGUMENTS:
    stateToggle(string) - this should point to the variable holding a (bool) value
    listOfItems(list) - list of menu item names to change

    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if stateToggle:
        newState = False
    else:
        newState = True

    for item in listOfItems:
        uiType = mc.objectTypeUI(item)
        if uiType == 'staticText':
            mc.text(item, edit = True, visible = newState)
        elif uiType == 'separator':
            mc.separator(item, edit = True, visible = newState)
        elif uiType == 'rowLayout':
            mc.rowLayout(item, edit = True, visible = newState)
        elif uiType == 'rowColumnLayout':
            mc.rowColumnLayout(item, edit = True, visible = newState)
        elif uiType == 'columnLayout':
            mc.columnLayout(item, edit = True, visible = newState)
        elif uiType == 'formLayout':
            mc.formLayout(item, edit = True, visible = newState)
            #print ('%s%s%s%s%s%s%s' % ('"python(mc.',uiType,"('",item,"', edit = True, visible = ",newState,'))"'))
            #mel.eval(('%s%s%s%s%s%s%s' % ('"python(mc.',uiType,"('",item,"', edit = True, visible = ",newState,'))"')))
            #mc.separator(item, edit = True, visible = newState)
        else:
            warning('%s%s%s' %('No idea what ', item, ' is'))
    return newState

def doToggleModeState(OptionSelection,OptionList,OptionVarName,ListOfContainers,forceInt = False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    This connects to a cgm rework of tabs in maya gui's. Mainly to be used with a form layout is needed
    with tabs. Tabs and form layouts don't work well together. This is a work around

    ARGUMENTS:
    optionSelection(string) - this should point to the variable holding a (int) value
    optionList(list) - the option selection must be in the optionList
    OptionVarName(string)
    ListOfContainers(list) -- list of containers
    forceInt -- forces the optionVar to set

    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    visOn = OptionList.index(OptionSelection)
    if forceInt:
        mc.optionVar(iv=(OptionVarName,int(visOn)))
    else:
        mc.optionVar(sv=(OptionVarName,OptionSelection))

    for cnt,Container in enumerate(ListOfContainers):
        if cnt == visOn:
            Container(e=True,vis=True)
            #doToggleMenuShowState(Container,True)
        else:
            Container(e=True,vis=False)
            #doToggleMenuShowState(Container,False)
        cnt+=1

def doStartMayaProgressBar(stepMaxValue = 100, statusMessage = 'Calculating....',interruptableState = True):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Tools to do a maya progress bar. This function and doEndMayaProgressBar are a part of a set. Example
    usage:

    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(int(number))
    for n in range(int(number)):
    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
    break
    mc.progressBar(mayaMainProgressBar, edit=True, status = (n), step=1)

    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

    ARGUMENTS:
    stepMaxValue(int) - max number of steps (defualt -  100)
    statusMessage(string) - starting status message
    interruptableState(bool) - is it interuptible or not (default - True)

    RETURNS:
    mayaMainProgressBar(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    mayaMainProgressBar = mel.eval('$tmp = $gMainProgressBar');
    mc.progressBar( mayaMainProgressBar,
                    edit=True,
                    beginProgress=True,
                    isInterruptable=interruptableState,
                    status=statusMessage,
                    minValue = 0,
                    maxValue= stepMaxValue )
    return mayaMainProgressBar

def doEndMayaProgressBar(mayaMainProgressBar):
    mc.progressBar(mayaMainProgressBar, edit=True, endProgress=True)

def log_selfReport(self):
    try:
        log.info("="*100)		
        log.info("{0} GUI = {1} {0}".format(cgmGeneral._str_headerDiv, self))
        log.info("="*100)	
        l_keys = self.__dict__.keys()
        l_keys.sort()		    
        log.info(" Self Stored: " + cgmGeneral._str_subLine)
        for i,str_k in enumerate(l_keys):
            try:
                buffer = self.__dict__[str_k]
                #type(buffer)
                bfr_type = type(buffer)
                if bfr_type in [bool,str,list,tuple]:
                    log.info(cgmGeneral._str_baseStart * 2 + "[{0}] : {1} ".format(str_k,buffer))
                if 'var_' in str_k:
                    log.info(cgmGeneral._str_baseStart * 2 + "[{0}] | type: {1} | value: {2}".format(buffer.name,buffer.varType,buffer.value))		
                #log.info(cgmGeneral._str_baseStart * 4 + "Type: {0}".format(type(buffer)))
            except Exception,error:
                log.error("log_selfReport >> '{0}' key fail | error: {1}".format(str_k,error))
    except Exception,error:
        log.error("log_self fail | error: {0}".format(error))