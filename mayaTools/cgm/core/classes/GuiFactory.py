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
__defaultSize__ = 250, 300

#>>> From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel
import copy

mayaVersion = int( mel.eval( 'getApplicationVersionAsFloat' ) )

# Maya version check
if mayaVersion >= 2011:
    currentGenUI = True
else:
    currentGenUI = False
    
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

def run():
    win = cgmGUI()
    
class cgmGUI(BaseMelWindow):
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
	#if mc.optionVar(exists = "cgmVar_%sDebugMode"%(__toolName__)) and mc.optionVar(q="cgmVar_%sDebugMode"%(__toolName__)):
	    #log.setLevel(logging.DEBUG)	    
	    
        #log.debug(">>> %s.__init__"%__toolName__)
        log.debug(">>> cgmGUI.__init__")	
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
	log.debug(self.__call__(q=True, title=True))
	log.info("WINDOW_NAME: '%s'"%cgmGUI.WINDOW_NAME)
	log.info("WINDOW_TITLE: '%s'"%cgmGUI.WINDOW_TITLE)
	log.info("DEFAULT_SIZE: %s"%str(cgmGUI.DEFAULT_SIZE))
	
        self.initializeTemplates() 
        self.description = 'This is a series of tools for working with cgm Sets'
        self.dockCnt = '%sDock'%__toolName__	
	self.__toolName__ = __toolName__		
        self.l_optionVars = []
        self.l_helpElements = []
        self.l_oldGenElements = []
	self.l_allowedDockAreas = ['right', 'left']
	self.WINDOW_NAME = cgmGUI.WINDOW_NAME
	self.WINDOW_TITLE = cgmGUI.WINDOW_TITLE
	self.DEFAULT_SIZE = cgmGUI.DEFAULT_SIZE
	
        #>>> Menu
        #====================
        self.build_menus()
        #self.ShowHelpOption = mc.optionVar( q='cgmVar_AnimToolsShowHelp' )

        #>>> Body
        #====================        
        self.build_layoutWrapper(self)
	
	if self.var_DebugMode.value:
	    log.setLevel(logging.DEBUG)	
	else:
	    log.setLevel(logging.INFO)
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

        if self.var_Dock.value:
            try:mc.dockControl(self.dockCnt, area='right', label=self.WINDOW_TITLE, content=self.WINDOW_NAME, floating=not self.var_Dock.value, allowedArea=self.l_allowedDockAreas, width=__defaultSize__[0])
            except:
                log.warning('Failed to dock')
            
    def setupVariables(self):
        self.create_guiOptionVar('ShowHelp',defaultValue = 0)
        self.create_guiOptionVar('Dock',defaultValue = 1)
        self.create_cgmDebugOptionVar(defaultValue = 0)

    def create_guiOptionVar(self,varName,*args,**kws):
        fullName = "cgmVar_%s%s"%(self.__toolName__,varName)
        if args:args[0] = fullName
        if kws and 'varName' in kws.keys():kws.pop('varName')
        self.__dict__['var_%s'%varName] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        log.info('var_%s'%varName)
        if fullName not in self.l_optionVars:
            self.l_optionVars.append(fullName)
	    
    def create_cgmDebugOptionVar(self,*args,**kws):
        fullName = "cgmVar_guiDebug"
        self.__dict__['var_DebugMode'] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        if fullName not in self.l_optionVars:
            self.l_optionVars.append(fullName)
    #=========================================================================
    # Menu Building
    #=========================================================================
    def build_menus(self):
        self.setupVariables()
        self.UI_FirstMenu = MelMenu( l='Root', pmc=self.build_firstMenu)		        
        self.UI_OptionsMenu = MelMenu( l='Options', pmc=self.build_optionsMenu)		
        self.UI_HelpMenu = MelMenu( l='Help', pmc=self.build_helpMenu)   

    def build_firstMenu( self, *a ):
        self.UI_FirstMenu.clear()
        #>>> Reset Options		
        MelMenuItemDiv( self.UI_FirstMenu )
        MelMenuItem( self.UI_FirstMenu, l="Reload",
                     c=lambda *a: self.reload())		
        MelMenuItem( self.UI_FirstMenu, l="Reset",
                     c=lambda *a: self.reset())    
        
    def build_optionsMenu( self, *a ):
        self.UI_OptionsMenu.clear()
        #>>> Reset Options				
        MelMenuItem( self.UI_OptionsMenu, l="Dock",
                     cb=self.var_Dock.value,
                     c= lambda *a: self.do_dockToggle())	      

    def build_helpMenu( self, *a ):
        self.UI_HelpMenu.clear()
        MelMenuItem( self.UI_HelpMenu, l="Show Help",
                     cb=self.var_ShowHelp.value,
                     c= lambda *a: self.do_showHelpToggle())

        MelMenuItem( self.UI_HelpMenu, l="Print Tools Help",
                     c=lambda *a: self.printHelp() )

        MelMenuItemDiv( self.UI_HelpMenu )
        MelMenuItem( self.UI_HelpMenu, l="About",
                     c=lambda *a: self.showAbout() )
	
	# Update Mode
	iMenu_loggerMaster = MelMenuItem( self.UI_HelpMenu, l='Logger Level', subMenu=True)
	MelMenuItem( iMenu_loggerMaster, l='Info',
	             c=lambda *a: self.set_loggingInfo())
	MelMenuItem( iMenu_loggerMaster, l='Debug',
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
            mc.dockControl(self.dockCnt, area='right', label=self.WINDOW_TITLE, content=self.WINDOW_NAME, floating=not self.var_Dock.value, allowedArea=self.l_allowedDockAreas, width=self.DEFAULT_SIZE[0])
        else:
            self.reload()            
  
    def do_showHelpToggle( self):
        doToggleMenuShowState(self.var_ShowHelp.value,self.l_helpElements)
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
        window = mc.window( title="About", iconName='About', ut = 'cgmUITemplate',resizeToFitChildren=True )
        column = mc.columnLayout( adjustableColumn=True )
        add_Header(self.__toolName__,overrideUpper = True)
        mc.text(label='>>>A Part of the cgmTools Collection<<<', ut = 'cgmUIInstructionsTemplate')
        add_HeaderBreak()
        
        add_TextBlock(self.description)
        
        add_LineBreak()
        mc.text(label=('%s%s' %('Written by: ',__author__)))
        mc.text(label=('%s%s%s' %('Copyright ',__owner__,', 2011')))
        add_LineBreak()
        mc.text(label='Version: %s' % __version__)
        mc.text(label='')
        add_Button(column,'Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://www.cgmonks.com/tools/maya-tools/morphyMaker/")')
        add_Button(column,'Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
        mc.setParent( '..' )
        mc.showWindow( window )

    def printHelp(self):pass
        #help(morphyMakerLib)

    def printReport(self):pass
        #morphyMakerLib.printReport(self)
    
    def doDebugEchoTest(self):
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

        MainForm = MelColumnLayout(parent)
        SetHeader = add_Header('HI')
        
	self.l_helpElements.extend(add_InstructionBlock("Purge all traces of cgmThinga tools from the object and so and so forth forever, amen.",vis = self.var_ShowHelp.value))        
        add_Button(MainForm)
        add_Button(MainForm,'Debug test', lambda *a: self.doDebugEchoTest())
	
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
        do_do_purgeOptionVars(optionVarHolder)
    if commandToRun:    
        commandToRun()

def do_do_purgeOptionVars(varHolder):
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
        return 	MelButton(parent,l=labelText,ut = 'cgmUITemplate',
                                 c= commandText,
                                 height = 20,
                                 align = 'center',
                                 annotation = annotationText,*a,**kw)
    else:
        return MelButton(parent,l=labelText, backgroundColor = [.75,.75,.75],
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

def add_InstructionBlock(text, align = 'center', vis = False, maxLineLength = 35):
    # yay, accounting for word wrap...
    if currentGenUI:
        buffer = mc.text(text, ut = 'cgmUIInstructionsTemplate',al = 'center', ww = True, visible = vis)
        return [buffer]
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