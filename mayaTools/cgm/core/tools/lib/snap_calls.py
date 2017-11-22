"""
------------------------------------------
snap_calls: cgm.core.tools.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

This is for more advanced snapping functionality.
================================================================
"""
__version__ = '0.2.11212017'

import webbrowser

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import maya.cmds as mc
import maya
import maya.mel as mel


from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
from cgm.core.lib import shared_data as SHARED
from cgm.core.tools import locinator as LOCINATOR
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.position_utils as POS
import cgm.core.classes.GuiFactory as cgmUI
from cgm.core.lib import name_utils as NAMES
from cgm.core.lib import distance_utils as DIST
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.math_utils as COREMATH
reload(RAYS)
reload(cgmUI)
reload(MMCONTEXT)
mUI = cgmUI.mUI

_2016 = False
if cgmGEN.__mayaVersion__ >=2016:
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

def snap_action(objects = None, snapMode = 'point',selectionMode = 'eachToLast',**kws):
    """
    """
    try:
        _str_func = 'snap_action'
        subKWS = {}
        if objects is None:
            objects = mc.ls(sl=True)
            
        if snapMode == 'aim':
            aim_axis = SHARED._l_axis_by_string[var_objDefaultAimAxis.value]
            up_axis = SHARED._l_axis_by_string[var_objDefaultUpAxis.value]
                    
            subKWS = {'aimAxis':aim_axis, 'upAxis':up_axis, 'mode':var_aimMode.value}
            
            if selectionMode == 'firstToRest':
                MMCONTEXT.func_process(SNAP.aim_atMidPoint, objects ,selectionMode,'Snap aim', **subKWS)
            else:
                MMCONTEXT.func_process(SNAP.aim, objects ,selectionMode,'Snap aim', **subKWS)
                
            if selectionMode == 'eachToNext':
                SNAP.aim(objects[-1],objects[-2],VALID.simpleAxis(aim_axis).inverse.p_string, up_axis, var_aimMode.value)
        
        elif snapMode == 'ground':
            MMCONTEXT.func_process(SNAP.to_ground, objects ,'each', 'Snap')
            
        elif snapMode in ['axisBox',
                          'boundingBox','boundingBoxShapes','boundingBoxEach',
                          'castCenter','castFar','castNear',
                          'castAllCenter','castAllFar','castAllNear']:
            log.debug("|{0}| | special mode: {1}".format(_str_func,snapMode))
            subKWS['mode'] = kws.get('mode','z+')
            subKWS['arg'] = snapMode
            
            if len(objects) == 1:
                specialSnap(objects[0],**subKWS)
            elif snapMode in ['boundingBox'] and selectionMode != 'each':
                log.debug("|{0}| | bb each mode".format(_str_func,snapMode))                
                specialSnap(objects[0],objects,**subKWS)
            else:
                MMCONTEXT.func_process(specialSnap, objects ,selectionMode, 'Snap Special', **subKWS)
            
        else:
            subKWS = {'position' : False, 'rotation' : False, 'rotateAxis' : False,'rotateOrder' : False,'scalePivot' : False,
                   'pivot' : 'rp', 'space' : 'w', 'mode' : 'xform'}
            
            if snapMode in ['point','closestPoint']:
                subKWS['position'] = True
            elif snapMode == 'orient':
                subKWS['rotation'] = True
            elif snapMode == 'parent':
                subKWS['position'] = True
                subKWS['rotation'] = True
            elif snapMode == 'aim':
                subKWS['rotation'] = True
            else:
                raise ValueError,"Unknown mode!"
            
            _pivotMode = var_snapPivotMode.value
            
            if snapMode == 'closestPoint':
                subKWS['pivot'] = 'closestPoint'
            else:
                if not _pivotMode:pass#0 handled by default
                elif _pivotMode == 1:
                    subKWS['pivot'] = 'sp'
                elif _pivotMode == 2:
                    subKWS['pivot'] = 'boundingBox'
                else:
                    raise ValueError,"Uknown pivotMode: {0}".format(_pivotMode)        
        
            MMCONTEXT.func_process(SNAP.go, objects ,selectionMode, 'Snap', **subKWS)
        
        mc.select(objects)
        return
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

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
    if not targets:
        targets = mc.ls(sl=True)
        
    if snap:
        if not create or create == 'duplicate':
            #targets = mc.ls(sl=True)#...to use g to do again?...    
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
            cgmGEN.log_info_dict(kws,"RayCast args")        
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
    cgmGEN.log_info_dict(kws,"RayCast args")
    
    cgmDrag.clickMesh(**kws)
    return

def get_special_pos(targets = None,
                    arg = 'rp',
                    mode = 'center',
                    mark=True):
    """
    This had to move here fore import loop considerations

    :parameters:
        obj(str): Object to modify
        target(str): Object to snap to
        sourceObject(str): object to copy from
        arg
            rp
            sp
            boundingBoxEach
            boundingBoxAll - all targets bounding box cumulative
            localAxisBox
            castFar
            castNear
            groundPos
        mode - Relative to 
            center
            front
            x

    :returns
        success(bool)
    """   
    _str_func = 'get_special_pos'
    _sel = mc.ls(sl=True)
    
    targets = VALID.listArg(targets)
    _targets = VALID.mNodeStringList(targets)
    
    if not _targets:
        raise ValueError,"Must have targets!"

    _arg = VALID.kw_fromDict(arg, SHARED._d_pivotArgs, noneValid=True,calledFrom= __name__ + _str_func + ">> validate pivot")
    if _arg is None:
        _arg = arg
    if _arg == 'cast':
        _arg = 'castNear'
        
    l_nameBuild = ['_'.join([NAMES.get_base(o) for o in _targets]),_arg,mode]
    l_res = []
    if _arg in ['rp','sp']:
        for t in _targets:
            l_res.append(POS.get(t,_arg,'world'))
    elif _arg == 'boundingBox':
        l_res.append( POS.get_bb_pos( _targets, False, mode))
    elif _arg == 'boundingBoxShapes':
        l_res.append( POS.get_bb_pos( _targets, True, mode))        
    elif _arg == 'boundingBoxEach':
        for t in _targets:
            l_res.append(POS.get_bb_pos( t, False, mode))
    elif _arg == 'boundingBoxEachShapes':
        for t in _targets:
            l_res.append(POS.get_bb_pos( t, True, mode))
    elif _arg == 'groundPos':
        for t in targets:
            pos = TRANS.position_get(t)
            l_res.append([pos[0],0.0,pos[2]])
    elif _arg.startswith('castAll'):
        _type =  _arg.split('castAll')[-1].lower()
        log.info("|{0}| >> castAll mode: {1} | {2}".format(_str_func,mode,_type))
        pos = RAYS.get_cast_pos(_targets[-1],mode,_type, None, mark=False, maxDistance=100000)
        l_res.append(pos)        
    elif _arg.startswith('cast'):
        _type =  _arg.split('cast')[-1].lower()
        log.info("|{0}| >> cast mode: {1} | {2}".format(_str_func,mode,_type))
        if len(_targets)>1:
            log.info("|{0}| >> more than one target...".format(_str_func))            
            pos = RAYS.get_cast_pos(_targets[0],mode,_type, _targets[1:],mark=False, maxDistance=100000)
        else:
            pos = RAYS.get_cast_pos(_targets[0],mode,_type, _targets,mark=False, maxDistance=100000)            
        l_res.append(pos)
    elif _arg == 'axisBox':
        log.warning("|{0}| >> axisBox mode is still wip".format(_str_func))
        for t in targets:
            _proxy = CORERIG.create_axisProxy(t)
            pos = RAYS.get_cast_pos(t,mode,'near', _proxy, mark=False, maxDistance=100000)
            l_res.append(pos)
            mc.delete(_proxy)
    else:
        raise ValueError,"|{0}| >> Unknown mode: {1}".format(_str_func,_arg)

    #cgmGEN.func_snapShot(vars())

    if len(l_res)>1:
        _res = DIST.get_average_position(l_res)
    else:
        _res = l_res[0]

    if mark:
        _loc = mc.spaceLocator()[0]
        mc.move (_res[0],_res[1],_res[2], _loc, ws=True)        
        mc.rename(_loc, '{0}_loc'.format('_'.join(l_nameBuild)))
    if _sel:
        mc.select(_sel)
    return _res


def specialSnap(obj = None, targets = None,
                arg = 'axisBox',
                mode = 'center',
                castOffset = False):
    """
    Special snap functionality
    
    :parameters:
        obj(str): Object to modify
        target(str): Object to snap to
        sourceObject(str): object to copy from

    :returns
        success(bool)
    """   
    try:
        _str_func = 'specialSnap'
    
        _obj = VALID.mNodeString(obj)
        _targets = VALID.listArg(targets)
        if not _targets:
            _targets = [_obj]
            
        if arg not in ['axisBox']:
            _targets.insert(0,_obj) 
        
        p = get_special_pos(_targets,arg,mode,False)
        
        if castOffset:
            p_start = TRANS.position_get(_obj)
            _vector_to_hit = COREMATH.get_vector_of_two_points(p_start, p)
            _vector_to_start = COREMATH.get_vector_of_two_points(p,p_start)
            
            _cast = RAYS.cast(startPoint= p_start, vector=_vector_to_hit)
            _hit = _cast.get('near')
            
            
            _dist_base = DIST.get_distance_between_points(p_start, p)#...get our base distance
            _dist_to_hit = DIST.get_distance_between_points(p_start, _hit)#...get our base distance
            
            p_result = DIST.get_pos_by_vec_dist(p_start,_vector_to_hit,(_dist_base + _dist_to_hit))
            #_cast = RayCast.cast(self.l_mesh, startPoint=_pos_obj,vector=_vec_obj)
            #_nearHit = _cast['near']
            #_dist_firstHit = DIST.get_distance_between_points(_pos_obj,_nearHit)
            #log.debug("baseDist: {0}".format(_dist_base))
            #log.debug("firstHit: {0}".format(_dist_firstHit))
            """
            if not _m_normal:
                if self.mode == 'far':
                    _dist_new = _dist_base + _dist_firstHit
                else:
                    _dist_new = _dist_base - _dist_firstHit 
                    
                _offsetPos = DIST.get_pos_by_vec_dist(_pos_obj,_vec_obj,(_dist_new))
            else:
                log.debug("|{0}| >> mesh normal offset!".format(_str_funcName))                                    
                _offsetPos = DIST.get_pos_by_vec_dist(_pos_base,_m_normal,(_dist_firstHit))"""
            
            
            cgmGEN.func_snapShot(vars())
            POS.set(_obj,p_result)
            return
            
        POS.set(_obj,p)
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
