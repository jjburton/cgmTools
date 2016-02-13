"""
------------------------------------------
HotkeyFactory: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
Issues:
-runtime command only available in mel
================================================================
"""
# From Python =============================================================
import copy
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgm_General as cgmGeneral
import cgm.core.classes.GuiFactory as cgmUI
import cgm.lib.zoo.zooPyMaya.baseMelUI as zooUI

mayaVersion = int( mel.eval( 'getApplicationVersionAsFloat' ) )

#>>> Root settings =============================================================
__version__ = '02.12.2016'
__toolName__ = 'cgmHotkeyer'
__description__ = "This is the Morpheus Rig 2.0 asset generator"
__toolURL__ = 'www.cgmonks.com'
__author__ = 'Josh Burton'
__owner__ = 'CG Monks'
__website__ = 'www.cgmonks.com'
__defaultSize__ = 200, 100


class cgmHotkeyer(object):
    '''
    Class to handle hot key setup. A hotkey setup is comprised of a key being pressed and a runTime command being executed.
    
    :param name: Name for the runtime command. Will be prefaced with 'cgmHK_'
    :param defaultKey: Mesh to import data to
    :param pressCmd: Command to execute on press
    :param releaseCmd: Command to execute on release
    :optionStr
    
    '''    
    _l_modifierOptions = ['none','alt','ctrl']
    
    def __init__(self, name = None, hotKey = None,
                 annotation = None,
                 pressCmd = None, releaseCmd = None,
                 showGui = True,
                 modifier = None, defaultKey = None,
                 commandLanguage = 'mel', **kws):
        
        self._name = name
        self._str_name = name 
        self._defaultKey = defaultKey
        self._modifier = modifier
        self._str_hotKeyToUse = hotKey
        
        self._valid_cmdPress = None
        self._valid_cmdRelease = None
        
        #if showGui:cgmHotkeyer.ui(self)#Pass to the gui for input
        
        #Validate and build
        if pressCmd is not None:
            self._valid_cmdPress = self.setup_runTime(pressCmd, commandLanguage, annotation,'_prs')
            log.info("cmdPress: {0}".format(self._valid_cmdPress))
        if releaseCmd is not None:
            self._valid_cmdRelease = self.setup_runTime(releaseCmd, commandLanguage, annotation,'_rls')
            log.info("cmdRelease: {0}".format(self._valid_cmdRelease)) 
            
        self.setup_hotKey()
            
    def setup_hotKey(self):
        #hotkey -keyShortcut "t" -name "cgmSnapMMPrs" -releaseName "cgmSnapMMRel";
        if mayaVersion >= 2016:
            _str_hotKeySet = 'cgmHotkeySet'
            log.info("hotkeySet setup mode...")
            if mc.hotkeySet(q=True, current=True) == "Maya_Default":
                #...if it's another set, it'll use whatever your current set is
                log.error("Current maya default hot key set is active. Creating new one as maya's is unchangable")
                if mc.hotkeySet(_str_hotKeySet, q=True, exists =True):#...if our name exists, make it current
                    log.info("cgm default set exists..changing to that...")
                    mc.hotkeySet(_str_hotKeySet,e = True, current = True)                    
                else:#...else, make it
                    mc.hotkeySet(_str_hotKeySet, source = 'Maya_Default', current = True)

        #_str_currentCmd = mc.hotkey( k = self._str_hotKeyToUse, query=True )
              
        _press = ''
        if self._valid_cmdPress:
            #_press = mc.nameCommand( self._valid_cmdPress + 'COMMAND', annotation=self._valid_cmdPress, command=self._valid_cmdPress) 
            _press = self._valid_cmdPress
            
        _release = ''
        if self._valid_cmdRelease:
            #_release = mc.nameCommand( self._valid_cmdRelease + 'COMMAND', annotation=self._valid_cmdRelease, command=self._valid_cmdRelease) 
            _release = self._valid_cmdRelease
        mc.hotkey(k = self._str_hotKeyToUse, name = _press, releaseName = _release)
        mc.savePrefs(hk = True)#...have to save prefs after setup or it won't keep        
        
    def setup_runTime(self, command = None, commandLanguage = 'mel', annotation = None, suffix = '_prs'):
        _str_runTime_cmd = self._str_name + suffix#...build name string
        
        #If our command name exists, we're gonna modify it
        if mel.eval('runTimeCommand -ex {0};'.format(_str_runTime_cmd)):
            log.info("{0} command exists, editing...".format(_str_runTime_cmd))
            _l_buildArg = ['runTimeCommand -edit']
        else:
            _l_buildArg = ['runTimeCommand']
            
        if annotation is not None:
            _l_buildArg.append('-ann "{0}"'.format(annotation)) 
            
        _l_buildArg.extend(['-cat User','-commandLanguage {0}'.format(commandLanguage),
                           '-c "{0}"'.format(command),
                           _str_runTime_cmd,';'])
        
        _str_runTimeArg = ' '.join(_l_buildArg)
        try:
            mel.eval(_str_runTimeArg)#...evaluate the runTime call
            return mc.nameCommand( _str_runTime_cmd + 'COMMAND', annotation=_str_runTime_cmd, command=_str_runTime_cmd)                        
            #return _str_runTime_cmd
        except Exception,error:
            log.error("runTime arg failure..." + cgmGeneral._str_hardBreak)
            print _str_runTimeArg
            log.error(error)
            log.error(cgmGeneral._str_hardBreak)
            return False
            
        
    class ui(zooUI.BaseMelWindow):
        USE_Template = 'cgmUITemplate'
        WINDOW_NAME = __toolName__
        WINDOW_TITLE = '%s - %s'%(__toolName__,__version__)
        DEFAULT_SIZE = __defaultSize__
        DEFAULT_MENU = None
        RETAIN = True
        MIN_BUTTON = False
        MAX_BUTTON = False
        FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created
    
        def __init__( self,mi_cgmHotkeyer,*args,**kws):
            #Check our tool option var for debug mode to set logger level if so
            if mc.optionVar(exists = "cgmVar_guiDebug") and mc.optionVar(q="cgmVar_guiDebug"):
                log.setLevel(logging.DEBUG)	
            self.mi_cgmHotkeyer = mi_cgmHotkeyer
            self.__toolName__ = __toolName__		
            self.l_allowedDockAreas = ['right', 'left']
            self.WINDOW_NAME = cgmSimpleUI.WINDOW_NAME
            self.WINDOW_TITLE = cgmSimpleUI.WINDOW_TITLE
            self.DEFAULT_SIZE = cgmSimpleUI.DEFAULT_SIZE
            
            #>>> Standard cgm variables
            #====================	    
            cgmUI.initializeTemplates() 
         
            self.build_layoutWrapper(self)
    
            self.show()
            
        def build_layoutWrapper(self,parent):
            uiColumn_main = zooUI.MelColumnLayout(parent)
            cgmUI.add_Header('Setup Hotkey')
            cgmUI.add_TextBlock(self.mi_cgmHotkeyer._name)
            
            #>>>Modifier row ------------------------------------------------------------------------------------
            self.uiRow_Modifier = zooUI.MelHSingleStretchLayout(uiColumn_main,ut='cgmUISubTemplate',padding = 2)
            zooUI.MelSpacer(self.uiRow_Modifier,w=5)
            zooUI.MelLabel(self.uiRow_Modifier, label = 'Modifier: ',align='right')
            self.uiRow_Modifier.setStretchWidget( zooUI.MelSeparator(self.uiRow_Modifier) )		
            self.uiRow_Modifier.layout()

            self.uiRadioCollection_modifier = zooUI.MelRadioCollection()
            self.uiOptions_modifier = []		

            for i,item in enumerate(cgmHotkeyer._l_modifierOptions):
                self.uiOptions_modifier.append(self.uiRadioCollection_modifier.createButton(self.uiRow_Modifier,label=item))
            self.uiRow_Modifier.layout()
            mc.radioCollection(self.uiRadioCollection_modifier,edit=True, sl=self.uiOptions_modifier[0])
            
            #>>>Text row ------------------------------------------------------------------------------------
            
            
            uiRow_key = zooUI.MelHLayout(uiColumn_main,ut='cgmUISubTemplate',padding = 15)            
            self.uiText_key = zooUI.MelTextField(uiRow_key,backgroundColor = [1,1,1],h=20,
                                                 text = self.mi_cgmHotkeyer._defaultKey,
                                                 ut = 'cgmUITemplate',
                                                 #ec = lambda *a:self._UTILS.puppet_doChangeName(self),
                                                 annotation = "Hotkey to use")   
            uiRow_key.layout()
            
            #>>> Button row
            mc.setParent(uiColumn_main)
            cgmUI.add_LineSubBreak()                                             

            cgmUI.add_Button(uiColumn_main,'Go',commandText = lambda *a:self.buttonPress_go(),
                             annotationText="Set it up")
            
            #mc.radioCollection(self.uiRadioCollection_modifier,edit=True, sl=self.uiOptions_main[self._l_tabOptions.index(self.var_Mode.value)])
        def buttonPress_go(self):
            log.info("Modifier from gui: {0}".format(self.uiRadioCollection_modifier.getSelectedIndex()))           
            log.info("Hotkey from gui arg: {0}".format(self.uiText_key.getValue()))
            self.mi_cgmHotkeyer._str_hotKeyToUse = self.uiText_key.getValue()
            self.mi_cgmHotkeyer._modifier = self.uiRadioCollection_modifier.getSelectedIndex()

            
        def do_DebugEchoTest(self):
            log.info('#'+'='*25)
            log.info('Tool: %s'%self.__toolName__)	
            log.info("Info call")
            log.debug("Debug call")
            log.warning("warning call")
        
class cgmSimpleUI(zooUI.BaseMelWindow):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = __toolName__
    WINDOW_TITLE = '%s - %s'%(__toolName__,__version__)
    DEFAULT_SIZE = __defaultSize__
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created

    def __init__( self,*args,**kws):
        #Check our tool option var for debug mode to set logger level if so
        if mc.optionVar(exists = "cgmVar_guiDebug") and mc.optionVar(q="cgmVar_guiDebug"):
            log.setLevel(logging.DEBUG)	
        self.__toolName__ = __toolName__		
        self.l_allowedDockAreas = ['right', 'left']
        self.WINDOW_NAME = cgmSimpleUI.WINDOW_NAME
        self.WINDOW_TITLE = cgmSimpleUI.WINDOW_TITLE
        self.DEFAULT_SIZE = cgmSimpleUI.DEFAULT_SIZE
        #>>> Standard cgm variables
        #====================	    
        #self.initializeTemplates() 

        #>>> Insert our init, overloaded for other tools
        #self.insert_init(*args,**kws)

        #>>> Menu
        #self.setup_Variables()	
        #self.build_menus()

        #>>> Body
        #====================        
        self.build_layoutWrapper(self)

        self.show()
        
    def build_layoutWrapper(self,parent):
        MainForm = zooUI.MelColumnLayout(parent)
        SetHeader = cgmUI.add_Header('HI')
        #self.l_helpElements.extend(add_InstructionBlock(MainForm,"Purge all traces of cgmThinga tools from the object and so and so forth forever, amen.",vis = self.var_ShowHelp.value))        
        cgmUI.add_Button(MainForm)
        cgmUI.add_Button(MainForm,'Debug test', lambda *a: self.do_DebugEchoTest())
        cgmUI.add_MelLabel(MainForm,'asdfasdfasdf')
        
    def do_DebugEchoTest(self):
        log.info('#'+'='*25)
        log.info('Tool: %s'%self.__toolName__)	
        log.info("Info call")
        log.debug("Debug call")
        log.warning("warning call")    