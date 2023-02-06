"""
------------------------------------------
camera_utils: cgm.core.lib
Author: David Bokser
email: dbokser@cgmonks.com
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
import pprint
import maya.cmds as mc
import cgm.core.lib.transform_utils as TRANS
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.search_utils as SEARCH
import cgm.core.lib.shape_utils as SHAPE

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start

def getCurrentPanel():
    panel = mc.getPanel(withFocus=True)
    
    if mc.getPanel(typeOf=panel) != 'modelPanel':
        for p in mc.getPanel(visiblePanels=True):
            if mc.getPanel(typeOf=p) == 'modelPanel':
                panel = p
                break
        
    return panel if mc.getPanel(typeOf=panel) == 'modelPanel' else None

def getCurrentCamera():   
    panel = getCurrentPanel()
        
    return mc.modelEditor(panel, query=True, camera=True) if panel else None


def autoset_clipPlane():
    _str_func = 'autoset_clipPlane'
    _cam = getCurrentCamera()
    
    _eligible = SHAPE.get_eligibleMesh()
    _sel = VALID.objStringList(mc.ls(sl=1) or _eligible,calledFrom=_str_func)
        
    _size = TRANS.bbSize_get(_sel,True,'max')
    _farSize =  TRANS.bbSize_get(_eligible,True,'max')
    
    _near =  _size*0.1
    _far = _farSize*10
    
    log.info(log_msg(_str_func,"near: {} || far: {}".format(_near,_far)))
    mc.setAttr(_cam + '.nearClipPlane', _near)
    mc.setAttr(_cam + '.farClipPlane', _far)    
    


