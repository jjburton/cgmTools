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
from cgm.core.lib.zoo import baseMelUI as mUI
from cgm.lib import search

def run():
    cgmMMRiggerWindow = cgmMMRigger()

_str_popWindow = 'cgmMMRigger'#...outside to push to killUI
class cgmMMRigger(mmTemplate.cgmMarkingMenu):
    WINDOW_NAME = 'cgmMMRiggerWindow'
    POPWINDOW = _str_popWindow
    
    def build_menu(self, parent):
        log.info("{0} >> build_menu".format(self._str_MM))                        
        mc.setParent(self)
        mUI.MelMenuItemDiv(parent)
        mUI.MelMenuItem(parent,l = 'ButtonAction...',
                        c = mUI.Callback(self.button_action,None))        
        mUI.MelMenuItem(parent,l = 'Reset...',
                        c=mUI.Callback(self.button_action,self.reset))
        #mUI.MelMenuItem(parent,l = "-"*20,en = False)
        mUI.MelMenuItem(parent,l='Report',
                        c = lambda *a: self.report())     

def killUI():
    log.info("killUI...")
    if mc.popupMenu(_str_popWindow,ex = True):
        mc.deleteUI(_str_popWindow)     




	
