"""
------------------------------------------
snap_utils: cgm.core.lib.snap_Utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
# From Python =============================================================
import copy
import re
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
from maya import mel
# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID
reload(VALID)
from cgm.core.lib import shared_data as SHARED
reload(SHARED)
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import position_utils as POS
reload(POS)
from cgm.core.lib import euclid as EUCLID
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
reload(ATTR)
#!!!! No rigging_utils!!!!!!!!!!!!!!!!!!!!!!!!!

#>>> Utilities
#===================================================================  
    
def go(obj = None, target = None,
       position = True, rotation = True, rotateAxis = False,rotateOrder = False, scalePivot = False,
       pivot = 'rp', space = 'w', mode = 'xform'):
    """
    Core snap functionality. We're moving an object by it's rp to move it around. The scale pivot may be snapped as well
    
    :parameters:
        obj(str): Object to modify
        target(str): Object to snap to
        sourceObject(str): object to copy from

    :returns
        success(bool)
    """   
    _str_func = 'go'
    
    try:obj = obj.mNode
    except:pass    
    
    _obj = VALID.mNodeString(obj)
    _target = VALID.mNodeString(target)
    
    _pivot = VALID.kw_fromDict(pivot, SHARED._d_pivotArgs, noneValid=False,calledFrom= __name__ + _str_func + ">> validate pivot")
    _space = VALID.kw_fromDict(space,SHARED._d_spaceArgs,noneValid=False,calledFrom= __name__ + _str_func + ">> validate space")  
    #_mode = VALID.kw_fromDict(mode,_d_pos_modes,noneValid=False,calledFrom= __name__ + _str_func + ">> validate mode")
    _mode = mode
    log.debug("|{0}| >> obj: {1} | target:{2} | pivot: {5} | space: {3} | mode: {4}".format(_str_func,_obj,_target,_space,_mode,_pivot))             
    log.debug("|{0}| >> position: {1} | rotation:{2} | rotateAxis: {3} | rotateOrder: {4}".format(_str_func,position,rotation,rotateAxis,rotateOrder))             
    
    kws = {'ws':False,'os':False}
    if _space == 'world':
        kws['ws']=True
    else:kws['os']=True  
    
    #cgmGEN.walk_dat(kws)
    
    if position:
        kws_move = copy.copy(kws)
        if _pivot == 'sp':
            kws_move['spr'] = True
        else:
            kws_move['rpr'] = True
            
        if _pivot == 'closestPoint':
            log.debug("|{0}|...closestPoint...".format(_str_func))        
            _targetType = SEARCH.get_mayaType(_target)
            p = DIST.get_by_dist(_obj,_target,resMode='pointOnSurface')
            POS.set(_obj,p)
                
        else:
            log.debug("|{0}|...postion...".format(_str_func))
            pos = POS.get(target,_pivot,_space,_mode)
            #log.debug(pos)
            #cgmGEN.print_dict(kws,'move kws','snap.go')
            mc.move (pos[0],pos[1],pos[2], _obj, **kws_move)
            #log.debug(POS.get(_obj))
    if rotateAxis:
        log.debug("|{0}|...rotateAxis...".format(_str_func))        
        mc.xform(obj,ra = mc.xform(_target, q=True, ra=True, **kws), p=True, **kws)    
    if rotateOrder:
        log.debug("|{0}|...rotateOrder...".format(_str_func))
        mc.xform(obj,roo = mc.xform(_target, q=True, roo=True), p=True)
    if rotation:
        log.debug("|{0}|...rotation...".format(_str_func))
        _t_ro = ATTR.get_enumValueString(_target,'rotateOrder')
        _obj_ro = ATTR.get_enumValueString(obj,'rotateOrder')
        
        if _t_ro != _obj_ro:
            #Creating a loc to get our target space rotateOrder into new space
            log.debug("|{0}|...rotateOrders don't match...".format(_str_func))
            _loc = mc.spaceLocator(n='tmp_roTranslation')[0]
            ATTR.set(_loc,'rotateOrder',_t_ro)
            rot = mc.xform (_target, q=True, ro=True, **kws )   
            mc.xform(_loc, ro = rot, **kws)
            mc.xform(_loc, roo = _obj_ro, p=True)
            rot = mc.xform (_loc, q=True, ro=True, **kws )   
            mc.delete(_loc)
        else:
            rot = mc.xform (_target, q=True, ro=True, **kws )
        mc.xform(_obj, ro = rot, **kws)
    
    if scalePivot:
        log.debug("|{0}|...scalePivot...".format(_str_func))
        mc.xform(obj,sp = mc.xform(_target, q=True, sp=True,**kws), p=True, **kws)
        

    return
    pos = infoDict['position']
    
    mc.move (pos[0],pos[1],pos[2], _target, ws=True)
    mc.xform(_target, roo=infoDict['rotateOrder'],p=True)
    mc.xform(_target, ro=infoDict['rotation'], ws = True)
    mc.xform(_target, ra=infoDict['rotateAxis'],p=True)
    
    #mTarget = r9Meta.getMObject(target)
    mc.xform(_target, rp=infoDict['position'], ws = True, p=True)        
    mc.xform(_target, sp=infoDict['scalePivot'], ws = True, p=True)    
    
def to_ground(obj=None):
    _str_func = 'snap_to_ground'    
    _obj = VALID.mNodeString(obj)
    
    p_bottom = POS.get_bb_pos(_obj,True,'bottom')
    p_pivot = POS.get(_obj)
    
    p_pivot[1] = p_pivot[1] - p_bottom[1] 
    POS.set(_obj,p_pivot)
    
def aim_atPoint(obj = None, position = [0,0,0], aimAxis = "z+", upAxis = "y+", mode = 'local',vectorUp = None,ignoreAimAttrs = False):
    """
    Aim functionality.
    
    :parameters:
        obj(str): Object to modify
        position(array): object to copy from
        aimAxis(str): axis that is pointing forward
        upAxis(str): axis that is pointing up
        mode(str): 
            'local'-- use standard maya aiming with local axis
            'world' -- use standard maya aiming with world axis
            'matrix' -- use Bokser's fancy method
            'vector' -- maya standard with vector up axis
            'object' -- maya standard with object

    :returns
        success(bool)
    """ 
    try:
        _str_func = 'aimAtPoint'
        _loc = False
        
        
        _obj = VALID.objString(obj, noneValid=False, calledFrom = __name__ + _str_func + ">> validate obj")
        try:position = position.x,position.y,position.z
        except:pass
        try:vectorUp = vectorUp.x,vectorUp.y,vectorUp.z
        except:pass
        
        log.debug("|{0}| >> obj: {1} | position:{2} | mode: {3}".format(_str_func,_obj,position,mode))  
        
        if not ignoreAimAttrs:
            _d_aim = ATTR.validate_arg(_obj,'axisAim')
            _d_up =ATTR.validate_arg(_obj,'axisUp')
            if ATTR.has_attr(_d_aim) and ATTR.has_attr(_d_up):
                aimAxis = ATTR.get_enumValueString(_d_aim)
                upAxis = ATTR.get_enumValueString(_d_up)
                log.debug("|{0}| >> obj: {1} aimable from attrs. aim: {2} | up: {3}".format(_str_func,_obj,aimAxis,upAxis))              
        
        if mode == 'matrix':
            '''Rotate transform based on look vector'''
            # get source and target vectors
            objPos = POS.get(_obj, asEuclid=True)
            targetPos = MATH.Vector3.Create(position)
        
            aim = (targetPos - objPos).normalized()
            
            if not vectorUp:
                upVector = MATH.Vector3.up()
                if upAxis == "y-":
                    upVector = MATH.Vector3.down()
                elif upAxis == "z+":
                    upVector = MATH.Vector3.forward()
                elif upAxis == "z-":
                    upVector = MATH.Vector3.back()
                elif upAxis == "x+":
                    upVector = MATH.Vector3.right()
                elif upAxis == "x-":
                    upVector = MATH.Vector3.left()
                else:
                    upVector = MATH.Vector3.up()
                
                vectorUp = MATH.transform_direction( _obj, upVector )

            wantedAim, wantedUp = MATH.convert_aim_vectors_to_different_axis(aim, vectorUp, aimAxis, upAxis)
            
            xformPos = mc.xform(_obj, q=True, matrix = True, ws=True)
            pos = MATH.Vector3(xformPos[12], xformPos[13], xformPos[14])
            rot_matrix = EUCLID.Matrix4.new_look_at(MATH.Vector3.zero(), -wantedAim, wantedUp)
            
            s = MATH.Vector3.Create( mc.xform(_obj, q=True, ws=True, s=True) )
            
            scale_matrix = EUCLID.Matrix4()
            scale_matrix.a = s.x
            scale_matrix.f = s.y
            scale_matrix.k = s.z
            scale_matrix.p = 1
        
            result_matrix = rot_matrix * scale_matrix
        
            transform_matrix = result_matrix[0:12] + [pos.x, pos.y, pos.z, 1.0]
        
            mc.xform(_obj, matrix = transform_matrix , roo="xyz", ws=True)
            """elif mode == 'world':
            _loc = mc.spaceLocator()[0]
            mc.move (position[0],position[1],position[2], _loc, ws=True)  
            
            mAxis_aim = VALID.simpleAxis(aimAxis)
            mAxis_up = VALID.simpleAxis(upAxis)
            
            _constraint = mc.aimConstraint(_loc,_obj,
                                           maintainOffset = False,
                                           aimVector = mAxis_aim.p_vector,
                                           upVector = mAxis_up.p_vector,
                                           worldUpType = 'scene',)
            mc.delete(_constraint + [_loc])"""
        elif mode in ['local','world','vector','object']:
            _loc = mc.spaceLocator(name='test')[0]
            _loc_snap = POS.create_loc(_obj)
            
            mc.move (position[0],position[1],position[2], _loc, ws=True)  
            mAxis_aim = VALID.simpleAxis(aimAxis)
            mAxis_up = VALID.simpleAxis(upAxis) 
            
            if mode == 'world':                
                _constraint = mc.aimConstraint(_loc,_loc_snap,
                                               maintainOffset = False,
                                               aimVector = mAxis_aim.p_vector,
                                               upVector = mAxis_up.p_vector,
                                               worldUpType = 'scene',) 
            elif mode == 'object':
                vectorUp = VALID.mNodeString(vectorUp)
                _constraint = mc.aimConstraint(_loc,_loc_snap,
                                               maintainOffset = False,
                                               aimVector = mAxis_aim.p_vector,
                                               upVector = mAxis_up.p_vector,
                                               worldUpType = 'object',
                                               worldUpObject = vectorUp)
                                               #worldUpVector = _vUp)
            else:
                if mode == 'vector':
                    _vUp = vectorUp
                else:
                    _vUp = MATH.get_obj_vector(_obj,upAxis)
                _constraint = mc.aimConstraint(_loc,_loc_snap,
                                               maintainOffset = False,
                                               aimVector = mAxis_aim.p_vector,
                                               upVector = mAxis_up.p_vector,
                                               worldUpType = 'vector',
                                               worldUpVector = _vUp)                 
                
            go(obj,_loc_snap)
            mc.delete(_constraint,_loc_snap)    
        else:
            raise NotImplementedError,"mode: {0}".format(mode)
        
        if _loc:mc.delete(_loc)
        return True
    except Exception,err:
        try:mc.delete(_loc)
        except:pass
        log.error( "aim_atPoint | obj: {0} | err: {1}".format(obj,err) )
        #cgmGEN.cgmExceptCB(Exception,err)
    

def aim_atMidPoint(obj = None, targets = None, aimAxis = "z+", upAxis = "y+",mode='local',vectorUp = None):
    """
    Aim functionality.
    
    :parameters:
        obj(str): Object to modify
        target(str): object to copy from
        aimAxis(str): axis that is pointing forward
        upAxis(str): axis that is pointing up
        vectorUp(vector): Only relevent during vector mode
        mode(str): 
            'local'-- use standard maya aiming with local axis
            'world' -- use standard maya aiming with world axis
            'matrix' -- use Bokser's fancy method
            'vector' -- maya standard with vector up axis
    :returns
        success(bool)
    """  
    _str_func = 'aimAtMidpoint'
    
    _obj = VALID.objString(obj, noneValid=False, calledFrom = __name__ + _str_func + ">> validate obj")
    _targets = VALID.objStringList(targets, noneValid=False, calledFrom = __name__ + _str_func + ">> validate targets")

    targetPos = MATH.Vector3.zero()

    for t in _targets:
        targetPos += MATH.Vector3.Create(POS.get(t))

    targetPos /= len(_targets)

    aim_atPoint(_obj, MATH.Vector3.AsArray(targetPos), aimAxis, upAxis,mode = mode,vectorUp=vectorUp)

def aim(obj = None, target = None, aimAxis = "z+", upAxis = "y+",mode = 'local',vectorUp = None):
    """
    Aim functionality.
    
    :parameters:
        obj(str): Object to modify
        target(str): object to copy from
        aimAxis(str): axis that is pointing forward
        upAxis(str): axis that is pointing up
        vectorUp(vector): Only relevent during vector mode
        mode(str): 
            'local'-- use standard maya aiming with local axis
            'world' -- use standard maya aiming with world axis
            'matrix' -- use Bokser's fancy method
            'vector' -- maya standard with vector up axis
    :returns
        success(bool)
    """  
    _str_func = 'aim'
          
    _obj = VALID.objString(obj, noneValid=False, calledFrom = __name__ + _str_func + ">> validate obj")
    _target = VALID.objString(target, noneValid=False, calledFrom = __name__ + _str_func + ">> validate target")

    targetPos = POS.get(_target)
    log.debug("|{0}| >> obj: {1} | target:{2} | mode: {3}".format(_str_func,_obj,_target,mode))             

    aim_atPoint(_obj, targetPos, aimAxis, upAxis, mode,vectorUp)

    return True



def matchTarget_set(obj = None, target = None):
    """
    Set the match target of an object
    
    :parameters:
        obj(str): Object to modify
        target(str): Target to match

    :returns
        success(bool)
    """     
    _str_func = 'matchTarget_set'
        
    _obj = VALID.objString(obj, noneValid=False, calledFrom = __name__ + _str_func + ">> validate obj")
    _target = VALID.objString(target, noneValid=False, calledFrom = __name__ + _str_func + ">> validate target")
    
    ATTR.set_message(_obj, 'cgmMatchTarget',_target,'cgmMatchDat',0)
    
    return True

def matchTarget_clear(obj = None):
    """
    Clear the match target of an object
    
    :parameters:
        obj(str): Object to modify

    :returns
        success(bool)
    """     
    _str_func = 'matchTarget_set'
    
    _obj = VALID.objString(obj, noneValid=False, calledFrom = __name__ + _str_func + ">> validate obj")
    
    ATTR.delete(_obj,'cgmMatchTarget')
    ATTR.delete(_obj,'cgmMatchDat')
    
    return True


def matchTarget_snap(obj = None, move = True, rotate = True, boundingBox = False, pivot = 'rp'):
    """
    Snap an object to it's match target
    
    :parameters:
        obj(str): Object to modify
        target(str): Target to match

    :returns
        success(bool)
    """     
    _str_func = 'matchTarget_snap'
    
    _obj = VALID.objString(obj, noneValid=False, calledFrom = __name__ + _str_func + ">> validate obj")
    
    _target = ATTR.get_message(_obj, 'cgmMatchTarget','cgmMatchDat',0)
    
    if not _target:
        raise ValueError,"|{0}| >> {1} has no cgmMatchTarget.".format(_str_func,NAMES.get_short(_obj))
    
    log.debug("|{0}| >> {1} snapping to: {2}.".format(_str_func,NAMES.get_short(_obj),_target[0]))
    
    _dict = POS.get_info(_target[0])
    
    #cgmGEN.log_info_dict(_dict)
    
    pos = _dict['position']
    
    if move:
        mc.move (pos[0],pos[1],pos[2], _obj, ws=True, rpr = True)
    if rotate:
        #if _dict.get('rotateOrder'):mc.xform(_obj, roo=_dict['rotateOrder'],p=True)
        if _dict.get('rotation'):mc.xform(_obj, ro=_dict['rotation'], ws = True)
        #if _dict.get('rotateAxis'):mc.xform(_obj, ra=_dict['rotateAxis'],p=True)
        
    
    return True


def verify_aimAttrs(obj = None, aim = None, up = None, checkOnly = False):
    """
    Make sure an object has aim attributes.
    
    :parameters:
        obj(str): Object to modify
        aim(arg): Value to set with on call
        up(arg): Value to set with on call
        out(arg): Value to set with on call
        checkOnly(bool): Check only, no adding attrs

    :returns
        success(bool)
    """     
    _str_func = 'verify_aimAttrs'
    _str_enum = 'x+:y+:z+:x-:y-:z-'
    
    _obj = VALID.objString(obj, noneValid=False, calledFrom = __name__ + _str_func + ">> validate obj")
    
    _l = [aim,up]
    _l_defaults = [aim or 2, up or 1]
    
    for i,a in enumerate(['axisAim','axisUp']):
        _d = ATTR.validate_arg(_obj,a)
        _good = False
        if mc.objExists(_d['combined']):
            if ATTR.get_type(_d) == 'enum':
                if ATTR.get_enum(_d) == _str_enum:
                    _good = True
        if not _good:
            if checkOnly:
                return False
            log.debug("|{0}| >> {1} not a good attr. Must rebuild".format(_str_func,_d['combined']))
            ATTR.delete(_d)
            ATTR.add(_d,'enum',enumOptions= _str_enum, hidden = False)
            ATTR.set(_d,value =_l_defaults[i])
            ATTR.set_keyable(_d,False)
        _v = _l[i]
        if _v is not None:
            ATTR.set(_d,value = _v)

    return True
    