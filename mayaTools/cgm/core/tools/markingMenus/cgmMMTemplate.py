import maya.cmds as mc
import maya.mel as mel

#from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.core.lib.zoo import baseMelUI as mUI

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core import cgm_PuppetMeta as cgmPM

from cgm.lib import guiFactory
from cgm.lib import (lists,search)
from cgm.tools.lib import animToolsLib
from cgm.tools.lib import tdToolsLib
from cgm.tools.lib import locinatorLib
reload(animToolsLib)
from cgm.lib import locators


import time

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def run():
    cgmMMTemplate = cgmMarkingMenu()

class cgmMarkingMenu(mUI.BaseMelWindow):
    _DEFAULT_MENU_PARENT = 'viewPanes'
    _str_funcName = "puppetKeyMarkingMenu"
    log.debug(">>> %s "%(_str_funcName) + "="*75)  
    def __init__(self):	
        """
        Initializes the pop up menu class call
        """
        self._str_MM = 'snapMarkingMenu'        
        self.optionVars = []
        IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked', value = 0)
        mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction',value = 0)			


        #>>>> Clock set
        #====================================================================
        self.clockStartVar = cgmMeta.cgmOptionVar('cgmVar_PuppetKeyClockStart', defaultValue = 0.0)	
        self.clockStartVar.value = time.clock()
        log.debug("cgmPuppetKey.clockStart: %s"%self.clockStartVar.value)

        IsClickedOptionVar.value = 0
        mmActionOptionVar.value = 0
        
        

        try:#>> Panel check and build...
            _sub = "Panel check and build"
            _p = mc.getPanel(up = True)
            if _p is None:
                log.error("No panel detected...")
                return 
            if _p:
                log.info("{0} panel under pointer {1}...".format(self._str_MM, _p))                    
                _parentPanel = mc.panel(_p,q = True,ctl = True)
                log.info("{0} panel under pointer {1} | parent: {2}...".format(self._str_MM, _p,_parentPanel))
                if 'MayaWindow' in _parentPanel:
                    _p = 'viewPanes'     
            if not mc.control(_p, ex = True):
                return "{0} doesn't exist!".format(_p)
            else:
                if not mc.popupMenu('cgmMM',ex = True):
                    mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = _p,
                                 pmc = mUI.Callback(self.createUI,'cgmMM'))
                else:
                    mc.popupMenu('cgmMM', edit = True, ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = _p,
                                 pmc = mUI.Callback(self.createUI,'cgmMM'))
        except Exception,err:
            raise Exception,"{0} {1} exception | {2}".format(self._str_MM,_sub,err)
        #pmc = lambda *a: self.createUI('cgmMM'))

    def insert_init(self,*args,**kws):
        self.__toolName__ = __toolName__		        
        """ This is meant to be overloaded per gui """
        log.debug(">>> cgmGUI.__init__")	
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        log.debug(self.__call__(q=True, title=True))
        self.__version__ = __version__
        self.l_allowedDockAreas = ['right', 'left']
        self.WINDOW_NAME = cgmGUI.WINDOW_NAME
        self.WINDOW_TITLE = cgmGUI.WINDOW_TITLE
        self.DEFAULT_SIZE = cgmGUI.DEFAULT_SIZE
        
        self.setup_Variables()	

    def setup_Variables(self):
        #self.create_guiOptionVar('ShowHelp',defaultValue = 0)
        pass
        
    def create_guiOptionVar(self,varName,*args,**kws):
        fullName = "cgmVar_{0}{1}".format(self.__toolName__,varName)
        if args:args[0] = fullName
        if kws and 'varName' in kws.keys():kws.pop('varName')
        self.__dict__['var_{0}'.format(varName)] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        log.debug('var_{0}'.format(varName))
        if fullName not in self.l_optionVars:
            self.l_optionVars.append(fullName)
        return fullName

    def createUI(self,parent):
        """
        Create the UI
        """	
        log.info("{0}.createUI()...".format(self._str_MM))
        
        time_buildMenuStart =  time.clock()
        self.setupVariables()#Setup our optionVars

        def buttonAction(command):
            """
            execute a command and let the menu know not do do the default button action but just kill the ui
            """			
            self.mmActionOptionVar.value=1			
            command
            killUI()	
		
        #MelMenuItem(parent,l = "-"*20,en = False)
        mUI.MelMenuItemDiv(parent)
        mUI.MelMenuItem(parent,l = 'Reset...')
        #mUI.MelMenuItem(parent, l="Reset",
                        #c=lambda *a: guiFactory.resetGuiInstanceOptionVars(self.optionVars))

        f_time = time.clock()-time_buildMenuStart
        log.info('build menu took: %0.3f seconds  ' % (f_time) + '<'*10)  

    def toggleVarAndReset(self, optionVar):
        try:
            self.mmActionOptionVar.value=1						
            optionVar.toggle()
            log.info("PuppetKey.toggleVarAndReset>>> %s : %s"%(optionVar.name,optionVar.value))
        except Exception,error:
            log.error(error)
            print "MM change var and reset failed!"


def killUI():
    log.info("killUI()...")    
    IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked')
    mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction')

    sel = search.selectCheck()

    #>>> Timer stuff
    #=============================================================================
    var_clockStart = cgmMeta.cgmOptionVar('cgmVar_PuppetKeyClockStart', defaultValue = 0.0)    
    f_seconds = time.clock()-var_clockStart.value
    log.debug(">"*10  + '   cgmPuppetKey =  %0.3f seconds  ' % (f_seconds) + '<'*10)    

    #>>>Delete our gui and default behavior
    if mc.popupMenu('cgmMM',ex = True):
        mc.deleteUI('cgmMM')
    if sel and f_seconds <= .5 and not mmActionOptionVar.value:
        setKey()
	
