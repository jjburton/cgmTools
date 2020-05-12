import maya.cmds as mc
import maya.mel as mel

import time

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral
from cgm.core.tools.markingMenus import cgmMMTemplate as mmTemplate
#reload(mmTemplate)
from cgm.core.lib.zoo import baseMelUI as mUI
from cgm.lib import search

def run():
    mmWindow = cgmMMBASE()
"""
This is an example file for working with 
"""
_str_popWindow = 'cgmBASEMM'#...outside to push to killUI
class cgmMMBASE(mmTemplate.cgmMarkingMenu):
    WINDOW_NAME = 'cgmBASEMMWindow'
    POPWINDOW = _str_popWindow
    MM = False#...whether to use mm pop up menu for build or not 
    
    @cgmGeneral.Timer
    def build_menu(self, parent):
        log.info("{0} >> build_menu".format(self._str_MM))                
        #mc.setParent(self)
        mUI.MelMenuItem(parent,l = 'ButtonAction...',
                        c = mUI.Callback(self.button_action,None))        
        mUI.MelMenuItem(parent,l = 'Reset...',
                        c=mUI.Callback(self.button_action,self.reset))        
        
        """
        mUI.MelMenuItem(parent,l = 'ButtonAction...',
                                c = lambda *a: self.button_action(None))        
        mUI.MelMenuItem(parent,l = 'Reset...',
                        c=lambda *a: self.button_action(self.reset))  """      
        mUI.MelMenuItem(parent,l = "-"*20,en = False)
        mUI.MelMenuItem(parent,l='Report',
                        c = lambda *a: self.report())   

def killUI():
    log.info("killUI...")
    if mc.popupMenu(_str_popWindow,ex = True):
        mc.deleteUI(_str_popWindow)     




	
