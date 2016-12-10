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
from cgm.core.lib import rigging_utils as coreRigging
reload(coreRigging)
reload(mmTemplate)
from cgm.core.lib.zoo import baseMelUI as mUI
from cgm.lib import search
from cgm.lib import locators
from cgm.tools.lib import tdToolsLib#...REFACTOR THESE!!!!

def run():
    mmWindow = cgmMMRigger()

_str_popWindow = 'cgmRigMM'#...outside to push to killUI
class cgmMMRigger(mmTemplate.cgmMarkingMenu):
    WINDOW_NAME = 'cgmRigMMWindow'
    POPWINDOW = _str_popWindow
    MM = True#...whether to use mm pop up menu for build or not 
    
    @cgmGeneral.Timer
    def build_menu(self, parent):
        self._d_radial_menu = {}
        
        self._l_sel = mc.ls(sl=True)
        self._b_sel = False
        if self._l_sel:self._b_sel = True
        self._b_sel_pair = False
        if len(self._l_sel) >= 2:
            self._b_sel_pair = True
            
        log.info("{0} >> build_menu".format(self._str_MM))                
        #mc.setParent(self)
        mUI.MelMenuItem(parent,l = 'ButtonAction...',
                        c = mUI.Callback(self.button_action,None))        
   
        
        #mc.menu(parent,e = True, deleteAllItems = True)
        self.build_radial_snap(parent,'S')
        self.build_radial_dynParent(parent,'NW')
        self.build_radial_create(parent,'N')
        self.build_radial_copy(parent,'W')
        self.build_radial_aim(parent,'NE')
        self.build_radial_control(parent,'SW')
        
        mUI.MelMenuItem(parent,l = "-"*20,en = False)
        mUI.MelMenuItem(parent,l = 'Reset...',
                        c=mUI.Callback(self.button_action,self.reset))             
        mUI.MelMenuItem(parent,l='Report',
                        c = lambda *a: self.report())
        
    @cgmGeneral.Timer
    def build_radial_snap(self,parent,direction = None):
        _r = mUI.MelMenuItem(parent,subMenu = True,
                             en = self._b_sel,
                             l = 'Snap',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             rp = direction)
        
        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'Point Snap',
                        c = lambda *a:self.button_action(tdToolsLib.doPointSnap()),
                        rp = 'SW')		            
        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'Parent Snap',
                        c = lambda *a:self.button_action(tdToolsLib.doParentSnap()),
                        rp = 'S')	
        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'Orient Snap',
                        c = lambda *a:self.button_action(tdToolsLib.doOrientSnap()),
                        rp = 'SE')	
    
        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'Surface Snap',
                        c = lambda *a:self.button_action(tdToolsLib.doSnapClosestPointToSurface(False)),
                        rp = 'W')
        
        mUI.MelMenuItem(_r,
                        en = self._b_sel,
                        l = 'RayCast',
                        #c = mUI.Callback(buttonAction,raySnap_start(_sel)),		            
                        c = lambda *a:self.button_action(raySnap_start(self._l_sel)),
                        rp = 'N')	        
        """
        if self.LocinatorUpdateObjectsOptionVar.value:
            ShowMatch = False
            if self.LocinatorUpdateObjectsBufferOptionVar.value:
                ShowMatch = True
            mUI.MelMenuItem(_r,
                            en = ShowMatch,
                            l = 'Buffer Snap',
                            c = lambda *a:buttonAction(locinatorLib.doUpdateLoc(self,True)),
                            rp = 'S')					
        else:
            ShowMatch = search.matchObjectCheck()			
            mUI.MelMenuItem(_r,
                            en = ShowMatch,
                            l = 'Match Snap',
                            c = lambda *a:buttonAction(locinatorLib.doUpdateSelectedObjects(self)),
                            rp = 'S')				
        mUI.MelMenuItem(_r,
                        en = 0,
                        l = 'Mirror',
                        c = lambda *a:buttonAction(locinatorLib.doUpdateObj(self,True)),
                        rp = 'SE')	"""
        
    #@cgmGeneral.Timer
    def build_radial_dynParent(self,parent,direction = None):
        """
        Menu to work with dynParent setup from cgm
        """
        _r = mUI.MelMenuItem(parent,subMenu = True,
                             en = False,
                             l = 'dynParent',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             rp = direction)
        
    def build_radial_create(self,parent,direction = None):
        """
        Menu to create items from selected objects
        """
        _r = mUI.MelMenuItem(parent,subMenu = True,
                             en = self._b_sel,
                             l = 'Create',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             rp = direction)  
        
        mUI.MelMenuItem(_r,
                        en = True,
                        l = 'Transform here',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        c = mUI.Callback(self.button_action_per_sel,coreRigging.create_at,'Create Transform'),
                        rp = "N")        
        mUI.MelMenuItem(_r,
                        en = True,
                        l = 'Group',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        c = mUI.Callback(self.button_action_per_sel,coreRigging.group_me,'Group Me'),
                        rp = "E")   
        mUI.MelMenuItem(_r,
                        en = True,
                        l = 'Group in Place',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        c = mUI.Callback(self.create_groupMe,'Group Me'),
                        rp = "NE")  
        mUI.MelMenuItem(_r,
                         en = True,
                         l = 'Locator',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         c = mUI.Callback(self.button_action_per_sel,locators.locMeObject,'Locator'),
                         rp = "S")          
        
        
        #locators.locMeObject(item, self.forceBoundingBoxState)
        
    def build_radial_aim(self,parent,direction = None):
        _r = mUI.MelMenuItem(parent,subMenu = True,
                             en = False,
                             l = 'Aim',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             rp = direction)   
    def build_radial_copy(self,parent,direction = None):
        _r = mUI.MelMenuItem(parent,subMenu = True,
                             en = self._b_sel_pair,
                             l = 'Copy',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             rp = direction)         
        #---------------------------------------------------------------------------
        mUI.MelMenuItem(_r,
                        en = True,
                        l = 'Rotate Pivot',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        c = mUI.Callback(self.copy_pivot,True, False,'Rotate Pivot'),
                        rp = "W")   
        mUI.MelMenuItem(_r,
                        en = True,
                        l = 'Scale Pivot',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        c = mUI.Callback(self.copy_pivot,False, True,'Rotate Pivot'),
                        rp = "SW") 
        mUI.MelMenuItem(_r,
                        en = True,
                        l = 'Orientation',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        #c = mUI.Callback(self.button_action_per_sel,locators.locMeObject,'Locator'),
                        rp = "NW")         
    def build_radial_control(self,parent,direction = None):
        _r = mUI.MelMenuItem(parent,subMenu = True,
                             en = False,
                             l = 'Control',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             rp = direction) 
        
    def button_action_per_sel(self,func,calling = None):
        for o in self._l_sel:
            _res = func(o)
            log.info("{0} : '{1}' | result: '{2}'".format(calling,o,_res)) 
    def button_action_each_to_last_sel(self,calling = None):
        pass    
    
    def action_logged(self,func,calling=None):
        _res = func
        log.info("{0} | result: '{1}'".format(calling,_res)) 
        

    
    def create_groupMe(self, calling = None):
        for o in self._l_sel:
            self.action_logged( coreRigging.group_me(o,True,True), "{0} : {1}".format(calling,o) )
            
    def copy_pivot(self,rotatePivot = False, scalePivot = False, calling=None):        
        for o in self._l_sel[1:]:
            _msg = "{0} : {1}".format(calling,o)
            try:
                self.action_logged( coreRigging.copy_pivot(o,self._l_sel[0],rotatePivot,scalePivot), _msg  )
                raise ValueError,'a'
            except Exception,err:
                log.error("{0} ||| Failure >>> err:s[{1}]".format(_msg,err))
def killUI():
    log.info("killUI...")
    try:
        if mc.popupMenu(_str_popWindow,ex = True):
            mc.deleteUI(_str_popWindow)  
    except Exception,err:
        log.error(err)    
        
from cgm.core.classes import DraggerContextFactory as cgmDrag
def raySnap_start(targets = []):
    _toSnap = targets
    log.info("raySnap_start | targets: {0}".format(_toSnap))
    if not _toSnap:
        raise ValueError,"raySnap_start >> Must have targets!"

    var_RayCastMode = cgmMeta.cgmOptionVar('cgmVar_SnapMenuRayCastMode', defaultValue=0)
    log.info("mode: {0}".format(var_RayCastMode.value))

    cgmDrag.clickMesh( mode = var_RayCastMode.value,
                       mesh = None,
                       closestOnly = True,
                       create = 'locator',
                       dragStore = False,
                       toSnap = _toSnap,
                       timeDelay = .25,
                       )

    log.warning("raySnap_start >>> ClickMesh initialized")




	
