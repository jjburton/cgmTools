"""
------------------------------------------
locinator: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
2.0 rewrite
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

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGen
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import locator_utils as LOC
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
reload(SNAP)
reload(LOC)
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
reload(MMCONTEXT)

def update_obj(obj = None, move = True, rotate = True, boundingBox = False):
    """
    Updates an tagged loc or matches a tagged object
    
    :parameters:
        obj(str): Object to modify
        target(str): Target to match

    :returns
        success(bool)
    """     
    _str_func = 'update_obj'
    
    _obj = VALID.objString(obj, noneValid=False, calledFrom = __name__ + _str_func + ">> validate obj")
    
    _locMode = ATTR.get(_obj,'cgmLocMode')
    if _locMode:
        log.info("|{0}| >> loc mode. updating {1}".format(_str_func,NAMES.get_short(_obj)))
        return LOC.update(_obj)
    if mc.objExists(_obj +'.cgmMatchTarget'):
        log.info("|{0}| >> Match mode. Matching {1} | move: {2} | rotate: {3} | bb: {4}".format(_str_func,NAMES.get_short(_obj),move,rotate,boundingBox))
        return SNAP.matchTarget_snap(_obj,move,rotate,boundingBox)
    
    log.info("|{0}| >> Not updatable: {1}".format(_str_func,NAMES.get_short(_obj)))    
    return False
        
        
def uiBuild_subMenu_create(self,parent,direction = None):
    #>>>Loc ==============================================================================================    
        _l = mc.menuItem(parent=parent,subMenu=True,
                     l = 'Loc',
                     rp = "N")
    
        mc.menuItem(parent=_l,
                    l = 'World Center',
                    c = cgmGen.Callback(LOC.create),
                    rp = "S")          
        mc.menuItem(parent=_l,
                    l = 'Me',
                    en = self._b_sel,
                    c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, self._l_sel,'each'),
                    rp = "N")           
        mc.menuItem(parent=_l,
                    l = 'Mid point',
                    en = self._b_sel_pair,                    
                    c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, self._l_sel,'all','midPointLoc',False,**{'mode':'midPoint'}),                                                                      
                    rp = "NE")            
        mc.menuItem(parent=_l,
                    l = 'closest Point',
                    en = self._b_sel_pair,                    
                    c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, self._l_sel,'all','closestPoint',False,**{'mode':'closestPoint'}),                                                                      
                    rp = "NW") 
        mc.menuItem(parent=_l,
                    l = 'closest Target',
                    en = self._b_sel_few,                    
                    c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, self._l_sel,'all','closestTarget',False,**{'mode':'closestTarget'}),                                                                      
                    rp = "W")   
        mc.menuItem(parent=_l,
                    l = 'rayCast',
                    c = lambda *a:self.rayCast_create('locator',False),
                    rp = "SE")       
    
def uiBuild_radialMenu(self,parent,direction = None):
    """
    
    """
    _r = mc.menuItem(parent=parent,subMenu = True,
                     l = 'Locinator',
                     rp = direction)  
    
  
    #---------------------------------------------------------------------------
    
    #>>>Loc ==============================================================================================    
    uiBuild_subMenu_create(self,_r,'N')
    
    #>>>Bake ==============================================================================================
    mc.menuItem(parent=_r,
                en = self._b_sel,
                l = 'Bake Range Frames',
                rp = 'NW')
    
    _bakeRange = mc.menuItem(parent=_r,subMenu = True,
                             en = self._b_sel,
                             l = 'Bake Range Keys',
                             rp = 'W')  
    mc.menuItem(parent=_bakeRange,
                l = 'of Loc',
                rp = 'NW')  
    mc.menuItem(parent=_bakeRange,
                 l = 'of Source',
                 rp = 'SW')       
    
    
    mc.menuItem(parent=_r,
                en = self._b_sel,
                l = 'Bake Timeline Frames',
                rp = 'NE')
        
    _bakeTime = mc.menuItem(parent=_r,subMenu = True,
                en = self._b_sel,
                l = 'Bake Timeline Keys',
                rp = 'E')
    mc.menuItem(parent=_bakeTime,
                    l = 'of Loc',
                    rp = 'NE')  
    mc.menuItem(parent=_bakeTime,
                 l = 'of Source',
                 rp = 'SE')     

    #>>>Utils ==============================================================================================
    mc.menuItem(parent=_r,
                l = 'Match',
                en=self._b_sel,
                #c = cgmGen.Callback(buttonAction,raySnap_start(_sel)),                    
                c = cgmGen.Callback(MMCONTEXT.func_process, update_obj, self._l_sel,'each','Match',False,**{'move':True,'rotate':True,'boundingBox':False}),                                                                      
                rp = 'S')         
    _utils = mc.menuItem(parent=_r,subMenu = True,
                         l = 'Utils',
                         en=self._b_sel,
                         rp = 'SE')  



