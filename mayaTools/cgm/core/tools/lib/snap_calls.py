"""
------------------------------------------
snap_calls: cgm.core.tools.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__version__ = '0.1.03132017'

import webbrowser

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import maya.cmds as mc
import maya
import maya.mel as mel


from cgm.core import cgm_General as cgmGen
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
from cgm.core.lib import shared_data as SHARED
from cgm.core.tools import locinator as LOCINATOR
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import curve_Utils as CURVES

import cgm.core.classes.GuiFactory as cgmUI
reload(cgmUI)
mUI = cgmUI.mUI

_2016 = False
if cgmGen.__mayaVersion__ >=2016:
    _2016 = True
    
    
var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode', defaultValue = 'world') 
var_snapPivotMode = cgmMeta.cgmOptionVar('cgmVar_snapPivotMode', defaultValue = 0)        
var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)

#var_resetMode = cgmMeta.cgmOptionVar('cgmVar_ChannelResetMode', defaultValue = 0)
#var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)
#var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)        

#var_objDefaultOutAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultOutAxis', defaultValue = 3)                        
#var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])
#var_contextTD = cgmMeta.cgmOptionVar('cgmVar_contextTD', defaultValue = 'selection')   



"""self.create_guiOptionVar('snapPivotMode', defaultValue = 0)
self.create_guiOptionVar('rayCastMode', defaultValue = 0)
self.create_guiOptionVar('rayCastOffset', defaultValue = 0)
self.create_guiOptionVar('rayCastCreate', defaultValue = 0)
self.create_guiOptionVar('rayCastOffsetDist', defaultValue = 1.0) """ 

def snap_action(objects = None, snapMode = 'point',selectionMode = 'eachToLast'):
    """
    """
    _str_func = 'snap_action'
    if objects is None:
        objects = mc.ls(sl=True)
        
    if snapMode == 'aim':
        aim_axis = SHARED._l_axis_by_string[var_objDefaultAimAxis.value]
        up_axis = SHARED._l_axis_by_string[var_objDefaultUpAxis.value]
                
        kws = {'aimAxis':aim_axis, 'upAxis':up_axis, 'mode':var_aimMode.value}
        
        if selectionMode == 'firstToRest':
            MMCONTEXT.func_process(SNAP.aim_atMidPoint, objects ,selectionMode,'Snap aim', **kws)
        else:
            MMCONTEXT.func_process(SNAP.aim, objects ,selectionMode,'Snap aim', **kws)
    else:
        kws = {'position' : False, 'rotation' : False, 'rotateAxis' : False,'rotateOrder' : False,'scalePivot' : False,
               'pivot' : 'rp', 'space' : 'w', 'mode' : 'xform'}
        
        if snapMode in ['point','closestPoint']:
            kws['position'] = True
        elif snapMode == 'orient':
            kws['rotation'] = True
        elif snapMode == 'parent':
            kws['position'] = True
            kws['rotation'] = True
        elif snapMode == 'aim':
            kws['rotation'] = True
        else:
            raise ValueError,"Unknown mode!"
        
        _pivotMode = var_snapPivotMode.value
        
        if snapMode == 'closestPoint':
            kws['pivot'] = 'closestPoint'
        else:
            if not _pivotMode:pass#0 handled by default
            elif _pivotMode == 1:
                kws['pivot'] = 'sp'
            elif _pivotMode == 2:
                kws['pivot'] = 'boundingBox'
            else:
                raise ValueError,"Uknown pivotMode: {0}".format(_pivotMode)        
    
        MMCONTEXT.func_process(SNAP.go, objects ,selectionMode, 'Snap', **kws)
    
    
    return

from cgm.core.classes import DraggerContextFactory as cgmDrag
reload(cgmDrag)
def aimSnap_start(targets=[]):
    raySnap_start(targets, None, False, snap=False, aim=True)
    
def rayCast_create(targets = [],create = None, drag=False):
    raySnap_start(targets,create = create, drag = drag)
    
def raySnap_start(targets = [], create = None, drag = False, snap=True, aim=False):
    
    _str_func = 'raySnap_start'
    _toSnap = False
    _toAim = False
    
    if snap:
        if not create or create == 'duplicate':
            targets = mc.ls(sl=True)#...to use g to do again?...    
            _toSnap = targets

            log.debug("|{0}| | targets: {1}".format(_str_func,_toSnap))
            if not _toSnap:
                if create == 'duplicate':
                    log.error("|{0}| >> Must have targets to duplicate!".format(_str_func))
                return
    
    if aim:
        _toAim = targets

    var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
    var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetMode', defaultValue=0)
    var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0)
    var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])
    var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0) 
    var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
    var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)      
    var_objDefaultOutAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultOutAxis', defaultValue = 0)      
    var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)
    var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode',defaultValue='world')
    
    _rayCastMode = var_rayCastMode.value
    _rayCastOffsetMode = var_rayCastOffsetMode.value
    _rayCastTargetsBuffer = var_rayCastTargetsBuffer.value
    _rayCastOrientMode = var_rayCastOrientMode.value
    _objDefaultAimAxis = var_objDefaultAimAxis.value
    _objDefaultUpAxis = var_objDefaultUpAxis.value
    _objDefaultOutAxis = var_objDefaultOutAxis.value
    _rayCastDragInterval = var_rayCastDragInterval.value
    
    log.debug("|{0}| >> Mode: {1}".format(_str_func,_rayCastMode))
    log.debug("|{0}| >> offsetMode: {1}".format(_str_func,_rayCastOffsetMode))
    
    kws = {'mode':'surface', 'mesh':None,'closestOnly':True, 'create':'locator','dragStore':False,'orientMode':None,
           'objAimAxis':SHARED._l_axis_by_string[_objDefaultAimAxis], 'objUpAxis':SHARED._l_axis_by_string[_objDefaultUpAxis],'objOutAxis':SHARED._l_axis_by_string[_objDefaultOutAxis],
           'aimMode':var_aimMode.value,
           'timeDelay':.1, 'offsetMode':None, 'dragInterval':_rayCastDragInterval, 'offsetDistance':var_rayCastOffsetDist.value}#var_rayCastOffsetDist.value
    
    if _rayCastTargetsBuffer:
        log.debug("|{0}| >> Casting at buffer {1}".format(_str_func,_rayCastMode))
        kws['mesh'] = _rayCastTargetsBuffer
        
    if _toSnap:
        kws['toSnap'] = _toSnap
    elif create:
        kws['create'] = create

    if _toAim:
        kws['toAim'] = _toAim
        
    if _rayCastOrientMode == 1:
        kws['orientMode'] = 'normal'
        
    if create == 'duplicate':
        kws['toDuplicate'] = _toSnap        
        if _toSnap:
            kws['toSnap'] = False
        else:
            log.error("|{0}| >> Must have target with duplicate mode!".format(_str_func))
            cgmGen.log_info_dict(kws,"RayCast args")        
            return
        
    if drag:
        kws['dragStore'] = drag
    
    if _rayCastMode == 1:
        kws['mode'] = 'midPoint'
    elif _rayCastMode == 2:
        kws['mode'] = 'far'
    elif _rayCastMode == 3:
        kws['mode'] = 'surface'
        kws['closestOnly'] = False
    elif _rayCastMode == 4:
        kws['mode'] = 'planeX'
    elif _rayCastMode == 5:
        kws['mode'] = 'planeY'   
    elif _rayCastMode == 6:
        kws['mode'] = 'planeZ'        
    elif _rayCastMode != 0:
        log.warning("|{0}| >> Unknown rayCast mode: {1}!".format(_str_func,_rayCastMode))
        
    if _rayCastOffsetMode == 1:
        kws['offsetMode'] = 'distance'
    elif _rayCastOffsetMode == 2:
        kws['offsetMode'] = 'snapCast'
    elif _rayCastOffsetMode != 0:
        log.warning("|{0}| >> Unknown rayCast offset mode: {1}!".format(_str_func,_rayCastOffsetMode))
    cgmGen.log_info_dict(kws,"RayCast args")
    
    cgmDrag.clickMesh(**kws)
    return

