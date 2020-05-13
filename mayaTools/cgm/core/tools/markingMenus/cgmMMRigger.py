import maya.cmds as mc
import maya.mel as mel

import time

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGen
from cgm.core.tools.markingMenus import cgmMMTemplate as mmTemplate
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.lib import snap_utils as SNAP
#reload(RIGGING)
#reload(mmTemplate)
from cgm.core.lib.zoo import baseMelUI as mUI
from cgm.lib import search
from cgm.lib import locators
from cgm.tools.lib import tdToolsLib#...REFACTOR THESE!!!!

def run():
    mmWindow = cgmMarkingMenu()

_str_popWindow = 'cgmMarkingMenuMM'#...outside to push to killUI

class cgmMarkingMenu(mmTemplate.cgmMetaMM):
    WINDOW_NAME = 'cgmMarkingMenuWindow'
    POPWINDOW = _str_popWindow
    MM = True#...whether to use mm pop up menu for build or not 
    
    @cgmGen.Timer
    def build_menu(self, parent):
        self._d_radial_menu = {}
        self._l_res = []
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
        self.uiRadial_snap_build(parent,'S')
        self.build_radial_dynParent(parent,'NW')
        self.build_radial_create(parent,'N')
        self.build_radial_copy(parent,'W')
        self.build_radial_aim(parent,'NE')
        self.build_radial_control(parent,'SW')
        self.build_radial_arrange(parent,'SE')
        
        mUI.MelMenuItem(parent,l = "-"*20,en = False)
        mUI.MelMenuItem(parent,l = 'Reset...',
                        c=mUI.Callback(self.button_action,self.reset))             
        mUI.MelMenuItem(parent,l='Report',
                        c = lambda *a: self.report())
         
    #@cgmGen.Timer
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
        if not self._b_sel:
            return        
        #---------------------------------------------------------------------------

        mUI.MelMenuItem(_r,
                        en = self._b_sel,
                        l = 'Transform here',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        c = mUI.Callback(self.button_action_per_sel,RIGGING.create_at,'Create Transform'),
                        rp = "N")        
        mUI.MelMenuItem(_r,
                        en = self._b_sel,
                        l = 'Group',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        c = mUI.Callback(self.button_action_per_sel,RIGGING.group_me,'Group Me'),
                        rp = "E")   
        mUI.MelMenuItem(_r,
                        en = self._b_sel,
                        l = 'Group Me',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        c = mUI.Callback(self.bc_create_groupMe,'Group Me'),
                        rp = "NE")  
        mUI.MelMenuItem(_r,
                         en = self._b_sel,
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
        
    def build_radial_arrange(self,parent,direction = None):
        _r = mUI.MelMenuItem(parent,subMenu = True,
                             en = False,
                             l = 'Arrange',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             rp = direction)  
        
    def build_radial_copy(self,parent,direction = None):
        _r = mUI.MelMenuItem(parent,subMenu = True,
                             en = self._b_sel_pair,
                             l = 'Copy',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             rp = direction)  
        if not self._b_sel_pair:
            return        
        #---------------------------------------------------------------------------

        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'Rotate Pivot',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        c = mUI.Callback(self.bc_copy_pivot,True, False,'Rotate Pivot'),
                        rp = "W")   
        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'Scale Pivot',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        c = mUI.Callback(self.bc_copy_pivot,False, True,'Scale Pivot'),
                        rp = "SW") 
        mUI.MelMenuItem(_r,
                        en = False,
                        l = 'Orientation',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        #c = mUI.Callback(self.button_action_per_sel,locators.locMeObject,'Locator'),
                        rp = "NW")         
    def build_radial_control(self,parent,direction = None):
        _r = mUI.MelMenuItem(parent,subMenu = True,
                             en = self._b_sel,
                             l = 'Control',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             rp = direction) 
        if not self._b_sel:
            return        
        #---------------------------------------------------------------------------   
        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'Combine Curves',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        #c = mUI.Callback(self.copy_pivot,True, False,'Rotate Pivot'),
                        rp = "W")   
        mUI.MelMenuItem(_r,
                         en = self._b_sel_pair,
                         l = 'ParentShape',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         #c = mUI.Callback(self.copy_pivot,True, False,'Rotate Pivot'),
                         rp = "SW")      
        mUI.MelMenuItem(_r,
                        en = False,
                        l = 'Replace Curves',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        #c = mUI.Callback(self.copy_pivot,True, False,'Rotate Pivot'),
                        rp = "NW")
        mUI.MelMenuItem(_r,subMenu = True,
                        en = False,
                        l = 'Color',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        #c = mUI.Callback(self.copy_pivot,True, False,'Rotate Pivot'),
                        rp = "E")         
        
    def button_action_per_sel(self,func,calling = None):
        for o in self._l_sel:
            _res = func(o)
            log.info("{0} : '{1}' | result: '{2}'".format(calling,o,_res)) 
            self._l_res.append(_res)
        mc.select(self._l_res)
        
    def button_action_each_to_last_sel(self,calling = None):
        pass    
    
    def action_logged(self,func,calling=None):
        _res = func
        log.info("{0} | result: '{1}'".format(calling,_res)) 
        
    def bc_create_groupMe(self, calling = None):
        for o in self._l_sel:
            _res = self.action_logged( RIGGING.group_me(o,True,True), "{0} : {1}".format(calling,o) )
            self._l_res.append(_res)
        mc.select(self._l_res)
        
    def bc_copy_pivot(self,rotatePivot = False, scalePivot = False, calling=None):        
        for o in self._l_sel[1:]:
            _msg = "{0} : {1}".format(calling,o)
            try:
                self.action_logged( RIGGING.copy_pivot(o,self._l_sel[0],rotatePivot,scalePivot), _msg  )
            except Exception,err:
                log.error("{0} ||| Failure >>> err:s[{1}]".format(_msg,err))
        mc.select(self._l_sel)
        
    def uiRadial_snap_build(self,parent,direction = None):
        """
        Radial menu for snap functionality
        """
        self.create_guiOptionVar('snapPivotMode', defaultValue = 0)

        _r = mUI.MelMenuItem(parent,subMenu = True,
                             en = self._b_sel,
                             l = 'Snap',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             rp = direction)
        if not self._b_sel:
            return        
        #---------------------------------------------------------------------------
    
        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'Point',
                        c = lambda *a:snap_action(self,'point'),
                        rp = 'NE')		            
        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'Parent',
                        c = lambda *a:snap_action(self,'parent'),
                        rp = 'N')	
        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'Orient',
                        c = lambda *a:snap_action(self,'orient'),
                        rp = 'E')	
        """mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'bbCenter',
                        ann = 'To the center of the bounding box',
                        c = lambda *a:snap_action(self,'boundingBox'),
                        rp = 'SE')	"""        
        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'scalePivot',
                        c = lambda *a:snap_action(self,'scalePivot'),
                        rp = 'SE')	        
    
        mUI.MelMenuItem(_r,
                        en = self._b_sel_pair,
                        l = 'Surface',
                        c = lambda *a:self.button_action(tdToolsLib.doSnapClosestPointToSurface(False)),
                        rp = 'SW')
    
        mUI.MelMenuItem(_r,
                        en = self._b_sel,
                        l = 'RayCast',
                        #c = mUI.Callback(buttonAction,raySnap_start(_sel)),		            
                        c = lambda *a:self.button_action(raySnap_start(self._l_sel)),
                        rp = 'W')	
        
        #Settings....
        #======================================================================================
        _settings = mUI.MelMenuItem(_r,subMenu = True,
                                    en = True,
                                    l = 'Pivot Mode',
                                    rp = 'S')
        self._l_pivotModes = ['rotatePivot','scalePivot','boundingBox']
        _l_toBuild = [{'l':'rotatePivot',
                       'rp':'S',
                       'c':lambda *a:self.var_snapPivotMode.setValue(0)},
                      {'l':'scalePivot',
                       'rp':'SW',
                       'c':lambda *a:self.var_snapPivotMode.setValue(1)},
                      {'l':'boundingBox',
                       'rp':'SE',
                       'c':lambda *a:self.var_snapPivotMode.setValue(2)}]
        for i,m in enumerate(_l_toBuild):
            if i == self.var_snapPivotMode.value:
                m['l'] = m['l'] + '(Active)'
            mUI.MelMenuItem(_settings,
                            en = True,
                            l = m['l'],
                            #c=mUI.Callback(self.var_snapPivotMode.setValue,0),
                            c = m['c'],
                            rp = m['rp'])                
        
        """mUI.MelMenuItem(_settings,
                        en = True,
                        l = 'rotatePivot',
                        #c=mUI.Callback(self.var_snapPivotMode.setValue,0),
                        c = lambda *a:self.var_snapPivotMode.setValue(0),
                        rp = 'S')        
        mUI.MelMenuItem(_settings,
                        en = True,
                        l = 'scalePivot',
                        #c=mUI.Callback(self.var_snapPivotMode.setValue,1),                        
                        c = lambda *a:self.var_snapPivotMode.setValue(1),
                        rp = 'SW')          
        mUI.MelMenuItem(_settings,
                        en = True,
                        l = 'boundingBox',
                        c = lambda *a:self.var_snapPivotMode.setValue(2),
                        rp = 'SE')   """   
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
    
def snap_action(self,mode = 'point'):
    _str_func = 'snap_action'
    for o in self._l_sel[:-1]:
        _msg = "|{0}| >> mode: {1} | obj: {2} |target: {3}".format(_str_func,mode,o,self._l_sel[-1])
        try:
            kws = {'obj' : o, 'target' : self._l_sel[-1],
                   'position' : False, 'rotation' : False, 'rotateAxis' : False,'rotateOrder' : False,'scalePivot' : False,
                   'pivot' : 'rp', 'space' : 'w', 'mode' : 'xform'}
            if mode == 'point':
                kws['position'] = True
            elif mode == 'orient':
                kws['rotation'] = True
            elif mode == 'parent':
                kws['position'] = True
                kws['rotation'] = True
            else:
                raise ValueError,"Unknown mode!"
            
            _pivotMode = self.var_snapPivotMode.value
            
            if not _pivotMode:pass#0 handled by default
            elif _pivotMode == 1:
                kws['pivot'] = 'sp'
            elif _pivotMode == 2:
                kws['pivot'] = 'boundingBox'
            else:
                raise ValueError,"Uknown pivotMode: {0}".format(_pivotMode)
            
            self.action_logged( SNAP.go(**kws), _msg  )
        except Exception,err:
            log.error("{0} ||| Failure >>> err:s[{1}]".format(_msg,err))
    mc.select(self._l_sel)    
    




	
