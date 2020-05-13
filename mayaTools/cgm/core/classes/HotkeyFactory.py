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
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgmPy.validateArgs as cgmValid
import cgm.core.cgm_General as cgmGeneral
import cgm.core.classes.GuiFactory as cgmUI
from cgm.core.lib.zoo import baseMelUI as zooUI

mayaVersion = cgmGeneral.__mayaVersion__

#>>> Root settings =============================================================
__version__ = '02.12.2016'
__toolName__ = 'cgmHotkeyer'
#__description__ = "This is the Morpheus Rig 2.0 asset generator"
#__toolURL__ = 'www.cgmonks.com'
#__author__ = 'Josh Burton'
#__owner__ = 'CG Monks'
#__website__ = 'www.cgmonks.com'
__defaultSize__ = 200, 100

def hotkeys_resetAll():
    """
    Reset all hot keys on current hotkeySet
    """
    _set = validate_hotkeySet(False)
    log.warning("All hotkeys on '{0}' set reset to maya defaults".format(_set))
    mc.hotkey(fs = True )
    
def validate_hotkeySet(setName = 'cgmHotkeySet'):
    """
    Validates a given setName as existing and is current set.
    
    :param setName: Name for the hotkeySet
    
    :returns validated name
    """
    if mayaVersion >= 2016:
        if setName:
            _str_hotKeySet = setName
            _exists = mc.hotkeySet(_str_hotKeySet, q=True, exists =True)
            if not _exists:
                _str_hotKeySet = mc.hotkeySet(_str_hotKeySet, source = 'Maya_Default')
                log.info("Created: "+ _str_hotKeySet)
            mc.hotkeySet(_str_hotKeySet, edit = True, current = True)
            #if mc.hotkeySet(q=True, current=True) == "Maya_Default":
                #...if it's another set, it'll use whatever your current set is
                #log.error("Current maya default hot key set is active. Creating new one as maya's is unchangable")
                #if mc.hotkeySet(_str_hotKeySet, q=True, exists =True):#...if our name exists, make it current
                    #log.info("cgm default set exists..changing to that...")
                    #mc.hotkeySet(_str_hotKeySet,e = True, current = True)                    
                #else:#...else, make it
                    #mc.hotkeySet(_str_hotKeySet, source = 'Maya_Default', current = True)
        return mc.hotkeySet(q=True, current=True)
    return "Maya_Default"

class cgmHotkeyer(object):
    '''
    Class to handle hot key setup. A hotkey setup is comprised of a key being pressed and a runTime command being executed.
    There is an option to show a UI which will let the user specify a modifer and key to use for the setup.
    
    :param name: Name for the runtime command. Will be prefaced with 'cgmHK_'
    :param pressCmd: Command to run with the button is pressed
    :param releaseCmd: ditto but released
    :param annotation: Help text for the setup
    :param commandLangauge: Language of the commands to setup - mel/python
    :param defaultKey: Default key for the UI pop up
    :param showUI: Whether to show the UI on call
    :param modifier: Keyboard modifer for the hotkey to activate - cntrl/alt. shift was added in maya 2016
    :param hotkey: Keyboard key to use for the function
    
    '''
    _l_modifierOptions = ['none','alt','ctrl']    
    if mayaVersion >= 2016:
        _l_modifierOptions.append('shift')
    
    def __init__(self, name = None,
                 pressCmd = None, releaseCmd = None,
                 annotation = None,
                 commandLanguage = 'mel',defaultKey = None,
                 showUI = True, 
                 modifier = None,  hotkey = None, **kws):
        
        self._defaultKey = defaultKey
        self._d_kws = {'name':name,
                       'annotation':annotation,
                       'hotkey':hotkey,
                       'pressCmd':pressCmd,
                       'releaseCmd':releaseCmd,
                       'modifier':modifier,
                       'commandLanguage':commandLanguage}
        self._d_fromUI = {}
        self._valid_cmdPress = None
        self._valid_cmdRelease = None
        
        if showUI:
            cgmHotkeyer.ui(self)#Pass to the gui for input
        else:
            self.build()

    def build(self):
        #Validate and build
        _pressCmd = self._d_kws.get('pressCmd',None)
        if _pressCmd is not None:
            self._valid_cmdPress = self.setup_runTime(_pressCmd, self._d_kws['commandLanguage'], self._d_kws['annotation'],'_prs')
            log.info("cmdPress: {0}".format(self._valid_cmdPress))
        _releaseCmd = self._d_kws.get('releaseCmd',None)
        if _releaseCmd is not None:
            self._valid_cmdRelease = self.setup_runTime(_releaseCmd, self._d_kws['commandLanguage'], self._d_kws['annotation'],'_rls')
            log.info("cmdRelease: {0}".format(self._valid_cmdRelease))  
        self.setup_hotKey()  
        
    def reset_hotkey(self):
        '''
        Function to attempt to reset a hotkey to default settings
        '''
        
    def validate_hotkeySet(self):
        return validate_hotkeySet()
    
    def validateModifier(self):
        _modifier = self._d_fromUI.get('modifier', self._d_kws['modifier'])
        if _modifier is None:
            return False
        elif cgmValid.stringArg(_modifier):
            if _modifier.lower() in cgmHotkeyer._l_modifierOptions:
                return _modifier
            else:return False
        elif cgmValid.valueArg(_modifier, inRange = [0,len(cgmHotkeyer._l_modifierOptions)]):
            return cgmHotkeyer._l_modifierOptions[_modifier]
        return False
    
    def setup_hotKey(self):
        self.validate_hotkeySet()
   
        _press = ''
        if self._valid_cmdPress:
            #_press = mc.nameCommand( self._valid_cmdPress + 'COMMAND', annotation=self._valid_cmdPress, command=self._valid_cmdPress) 
            _press = self._valid_cmdPress
            
        _release = ''
        if self._valid_cmdRelease:
            #_release = mc.nameCommand( self._valid_cmdRelease + 'COMMAND', annotation=self._valid_cmdRelease, command=self._valid_cmdRelease) 
            _release = self._valid_cmdRelease
        
        _d = {'keyShortcut':self._d_fromUI.get('hotkey', self._d_kws['hotkey']),
              'name':_press,
              'releaseName':_release,
              'altModifier':False,
              'ctrlModifier':False,
              'shiftModifier':False}       
        _l_order = ['keyShortcut']
        _modifer = self.validateModifier()
        
        if _modifer and _modifer+'Modifier' in _d.keys():
            _d[_modifer+'Modifier'] = True
            
        if mayaVersion < 2016:
            _d.pop('shiftModifier')
            if _modifer == 'shift':
                log.error("The shiftModifer was added in Maya 2016. Cannot setup.")
                return
        cgmGeneral.log_info_dict(_d,'hotkey args')

        _k = _d.get('keyShortcut')

        log.info(_k)
        log.info(_d)
        mc.hotkey(_k,**_d)#...run it                                        
        mc.savePrefs(hk = True)#...have to save prefs after setup or it won't keep        
        
    def setup_runTime(self, command = None, commandLanguage = 'mel', annotation = None, suffix = '_prs'):
        _str_runTime_cmd = self._d_kws['name'] + suffix#...build name string
        
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
        log.debug("arg: " + _str_runTimeArg)
        try:
            mel.eval(_str_runTimeArg)#...evaluate the runTime call cause maya sucks and doesn't have a python command for this
            return mc.nameCommand( _str_runTime_cmd + 'COMMAND', annotation=_str_runTime_cmd, command=_str_runTime_cmd)                        
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
            cgmUI.add_TextBlock(self.mi_cgmHotkeyer._d_kws['name'])
            
            #>>>Modifier row ------------------------------------------------------------------------------------
            self.uiRow_Modifier = zooUI.MelHSingleStretchLayout(uiColumn_main,ut='cgmUISubTemplate',padding = 2)
            #zooUI.MelSpacer(self.uiRow_Modifier,w=5)
            #zooUI.MelLabel(self.uiRow_Modifier, label = 'Modifier: ',align='right')
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
            uiRow_buttons = zooUI.MelHLayout(uiColumn_main,ut='cgmUISubTemplate',padding = 5)  
            cgmUI.add_Button(uiRow_buttons,'Go',commandText = lambda *a:self.buttonPress_go(),
                             annotationText="Set it up")
            cgmUI.add_Button(uiRow_buttons,'Reset',commandText = lambda *a:self.buttonPress_reset(),en = False,
                                         annotationText="Reset given key to the default maya setting")   
            uiRow_buttons.layout()
            
            #mc.radioCollection(self.uiRadioCollection_modifier,edit=True, sl=self.uiOptions_main[self._l_tabOptions.index(self.var_Mode.value)])
        
        def buttonPress_go(self):
            log.info("Modifier from gui: {0}".format(self.uiRadioCollection_modifier.getSelectedIndex()))           
            log.info("Hotkey from gui arg: {0}".format(self.uiText_key.getValue()))
            self.mi_cgmHotkeyer._d_fromUI['hotkey'] = self.uiText_key.getValue()
            self.mi_cgmHotkeyer._d_fromUI['modifier'] = self.uiRadioCollection_modifier.getSelectedIndex()
            self.mi_cgmHotkeyer.build()
            self.close()
            
        def buttonPress_reset(self):
            log.info("Hotkey from gui arg: {0}".format(self.uiText_key.getValue()))
            #self.mi_cgmHotkeyer._d_fromUI['hotkey'] = self.uiText_key.getValue()
            self.mi_cgmHotkeyer._d_fromUI['modifier'] = self.uiRadioCollection_modifier.getSelectedIndex()
            #self.mi_cgmHotkeyer.build()
            self.mi_cgmHotkeyer.reset_hotkey()       
            self.close()        
        def buttonPress_resetAll(self):
            _set = self.mi_cgmHotkeyer.validate_hotkeySet()
            log.warning("All hotkeys on {0} set reset to maya defaults".format(_set))
            mc.hotkey(fs = True )
            self.close()        
        
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