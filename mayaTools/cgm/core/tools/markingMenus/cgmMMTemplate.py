import maya.cmds as mc
import maya.mel as mel

#from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.core.lib.zoo import baseMelUI as mUI
import cgm.core.classes.GuiFactory as cgmUI

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core import cgm_PuppetMeta as cgmPM
from cgm.core.lib import name_utils as NAMES
#reload(cgmUI)


import time

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def run():
    try:
        cgmMetaMM()
        #cgmMetaMMWindow = cgmMetaMM()
    except Exception,err:
        log.error("Failed to load. err:{0}".format(err))
        
_str_popWindow = 'cgmMetaMM'#...outside to push to killUI
#MelPopupMenu
class cgmMetaMM(mUI.BaseMelWindow):
    _DEFAULT_MENU_PARENT = 'viewPanes'
    WINDOW_NAME = 'cgmMetaMMWindow'
    POPWINDOW = _str_popWindow
    MM = True#...whether to use mm pop up menu for build or not 
    def __init__(self):	
        """
        Initializes the pop up menu class call
        """
        
        self._str_MM = type(self).__name__    
        log.debug(">>> %s "%(self._str_MM) + "="*75)          
        self.l_optionVars = []		
        self.create_guiOptionVar('isClicked', value = 0)
        self.create_guiOptionVar('mmAction', value = 0)
        self.create_guiOptionVar('clockStart', value = 0.0)  

        #>>>> Clock set
        #====================================================================

        self.var_clockStart.value = time.clock()
        #log.info("{0} >> clockStart: {1}".format(self._str_MM,self.clockStartVar.value))

        self.var_isClicked.value = 0
        self.var_mmAction.value = 0

        #try:#>> Panel check and build...
        _sub = "Panel check and build"
        log.debug( mc.getPanel(withFocus=True))            
        _p = mc.getPanel(up = True)
        if _p is None:
            log.debug("No panel detected...")
            return 
        if _p:
            log.debug("...panel under pointer {1}...".format(self._str_MM, _p))                    
            _parentPanel = mc.panel(_p,q = True,ctl = True)
            log.debug("...panel parent: {1}...".format(self._str_MM,_parentPanel))
            if 'MayaWindow' in _parentPanel:
                _p = 'viewPanes'     
        if not mc.control(_p, ex = True):
            return "{0} doesn't exist!".format(_p)
        else:
            #_pmc = mUI.Callback(self.createUI,self.__class__.POPWINDOW)
            if not mc.popupMenu('cgmMM',ex = True):
                mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0,
                             pmc = lambda *a: self.createUI('cgmMM'),                             
                             mm = self.__class__.MM, b =1, aob = 1, p = _p,postMenuCommandOnce=True)#postMenuCommandOnce=True
            else:
                mc.popupMenu('cgmMM', edit = True, ctl = 0, alt = 0, sh = 0,
                             pmc = lambda *a: self.createUI('cgmMM'),
                             mm =self.__class__.MM, b =1, aob = 1, p = _p, dai = True,postMenuCommandOnce=True)
                
            #mc.popupMenu('cgmMM', edit = True, ctl = 0, alt = 0, sh = 0, b = 3,
                         #pmc = lambda *a: killUI())
                         
            #self.createUI(self.__class__.POPWINDOW)
            #self.createUI('cgmMM')
            #mc.showWindow('cgmMM')
            #mc.showWindow( self.__class__.POPWINDOW )
            #self.show()
        #except Exception,err:
            #raise Exception,"{0} {1} exception | {2}".format(self._str_MM,_sub,err)

    def setup_optionVars(self):
        pass

    def create_guiOptionVar(self,varName,*args,**kws):
        fullName = "cgmVar_{0}_{1}".format(self._str_MM,varName)
        if args:args[0] = fullName
        if kws and 'varName' in kws.keys():kws.pop('varName')
        self.__dict__['var_{0}'.format(varName)] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        log.debug('var_{0}'.format(varName))
        if fullName not in self.l_optionVars:
            self.l_optionVars.append(fullName)

        return fullName
    
    def varBuffer_define(self,optionVar):
        _str_func = 'varBuffer_define'
        
        sel = mc.ls(sl=True, flatten = True) or []
        
        if not sel:
            log.error("|{0}| >> No selection found. Cannot define")
            return False
        
        optionVar.clear()
    
        for o in sel:
            optionVar.append(NAMES.get_short(o))
        return True
    
    def varBuffer_add(self,optionVar):
        _str_func = 'varBuffer_add'
        
        sel = mc.ls(sl=True, flatten = True) or []
        if not sel:
            log.error("|{0}| >> No selection found. Cannot define")
            return False
        
        for o in sel:
            optionVar.append(o)
            
    def varBuffer_remove(self,optionVar):
            _str_func = 'varBuffer_add'
            
            sel = mc.ls(sl=True, flatten = True) or []
            if not sel:
                log.error("|{0}| >> No selection found. Cannot define")
                return False
            
            for o in sel:
                optionVar.remove(o)
    
    
    @cgmGeneral.Timer
    def BUILD(self, parent):
        """
        This is the method designed to be overloaded to do build the subclass menus...
        """
        log.info("{0} >> build_menu".format(self._str_MM))                
        #mc.setParent(self)
        mc.menuItem(parent = parent,l = "-"*25,en = False)
        mc.menuItem(parent = parent,l = 'ButtonAction...',
                    c = mUI.Callback(self.button_action,None))        
        mc.menuItem(parent = parent,l = 'Reset...',
                    c=mUI.Callback(self.button_action,self.reset))        
        
        """
        mUI.MelMenuItem(parent,l = 'ButtonAction...',
                                c = lambda *a: self.button_action(None))        
        mUI.MelMenuItem(parent,l = 'Reset...',
                        c=lambda *a: self.button_action(self.reset))  """      
        mc.menuItem(parent = parent,l = "-"*25,en = False)
        mc.menuItem(parent = parent,l='Report',
                    c = lambda *a: self.report())
    @cgmGeneral.Timer    
    def button_action(self, command = None):
        """
        execute a command and let the menu know not do do the default button action but just kill the ui
        """	
        log.info("{0} >> buttonAction: {1}".format(self._str_MM,command))                    
        self.var_mmAction.value=1			
        if command:
            try:command()
            except Exception,err:
                log.info("{0} button >> error {1}".format(self._str_MM, err))      

    def createUI(self,parent):
        """
        Create the UI
        """	
        log.debug("{0}.createUI()...{1}".format(self._str_MM,self))
        """for c in self.get_uiChildren():
            #print c
            log.info('deleting old ui: {0}'.format(c))
            try:mc.deleteUI(c)
            except:log.info('failed to delete...')"""
            
        #time_buildMenuStart =  time.clock()
        self.setup_optionVars()#Setup our optionVars
        #mc.setParent(parent)
        
        self.BUILD(parent)
        
        #mUI.MelMenuItemDiv(parent)        
        #mUI.MelMenuItem(parent,l = '{0}'.format(self.__class__.POPWINDOW),en=False)   
        
        #f_time = time.clock()-time_buildMenuStart
        #log.info('build menu took: %0.3f seconds  ' % (f_time) + '<'*10) 
              

    def toggleVarAndReset(self, optionVar):
        try:
            self.mmActionOptionVar.value=1						
            optionVar.toggle()
            log.info("{0}.toggleVarAndReset>>> {1} : {2}".format(self._str_MM,optionVar.name,optionVar.value))
        except Exception,error:
            log.error(error)
            print "MM change var and reset failed!"

    def reset(self):
        log.info("{0} >> reset".format(self._str_MM))        
        mUI.Callback(cgmUI.do_resetGuiInstanceOptionVars(self.l_optionVars,False))
        #killUI()
        
    def report(self):
        cgmUI.log_selfReport(self)
        log.debug("{0} >> Children...".format(self._str_MM))  
        for c in self.get_uiChildren():
            log.debug(c)

    def get_uiChildren(self):
        """
        Because maya is stupid and you can't query uiChildren
        """
        l_ = []
        l_toCheck = []
        l_toCheck.extend( mc.lsUI(controls = True, l = True) )
        l_toCheck.extend( mc.lsUI(mi = True, l = True) )
        l_toCheck.extend( mc.lsUI(controlLayouts = True, l = True) )
        l_toCheck.extend( mc.lsUI(collection = True, l = True) )
        l_toCheck.extend( mc.lsUI(rmc = True, l = True) )
        l_toCheck.extend( mc.lsUI(menus = True, l = True) )
        l_toCheck.extend( mc.lsUI(contexts = True, l = True) )
        
        for c in l_toCheck:
            if  self.__class__.POPWINDOW in c.split('|') and not str(c).endswith(self.__class__.POPWINDOW):
                l_.append(c)
        
        return l_
   
def killChildren(uiElement):
    l_ = []
    l_toCheck = []
    l_toCheck.extend( mc.lsUI(controls = True, l = True) )
    l_toCheck.extend( mc.lsUI(mi = True, l = True) )
    l_toCheck.extend( mc.lsUI(controlLayouts = True, l = True) )
    l_toCheck.extend( mc.lsUI(collection = True, l = True) )
    l_toCheck.extend( mc.lsUI(rmc = True, l = True) )
    l_toCheck.extend( mc.lsUI(menus = True, l = True) )
    l_toCheck.extend( mc.lsUI(contexts = True, l = True) )
    
    for c in l_toCheck:
        if  uiElement in c.split('|') and not str(c).endswith(uiElement):
            l_.append(c)
            
    for c in l_:
        #log.info('deleting old ui: {0}'.format(c))
        try:mc.deleteUI(c)
        except Exception,err:log.debug('failed to delete: {0} | err: {1}'.format(c,err))          

def killUI():
    log.info("killUI...")
    try:
        _str_popWindow = 'cgmMM'
        if mc.popupMenu(_str_popWindow,ex = True):
            mc.deleteUI(_str_popWindow)
    except Exception,err:
        log.error(err)


