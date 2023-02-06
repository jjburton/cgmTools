"""
------------------------------------------
anim_utils: cgm.core.lib
Author: David Bokser, Josh Burton
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
import pprint
import logging

import maya.cmds as mc

import cgm.core.lib.math_utils as COREMATH
import cgm.core.lib.position_utils as POS
import cgm.core.lib.distance_utils as DIST
from cgm.core import cgm_General as cgmGEN
import cgm.core.lib.attribute_utils as ATTR

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start

def get_anim_value_by_time(node = None, attributes = [], time = 0.0):
    _str_func = 'get_anim_value_by_time'    
    _res = []
    for a in attributes:
        _comb = "{}.{}".format(node,a)
        anim_curve_node = mc.listConnections(_comb, source=True, destination=False, type="animCurve")
        if anim_curve_node:
            anim_curve_node = anim_curve_node[0]
        else:
            log.error(log_msg(_str_func,"| Doesn't have anim: {}".format(_comb)))
            continue
        _res.append(mc.getAttr("{}.output".format(anim_curve_node), time = time))
        
    if _res and len(_res)==1:
        return _res[0]
    return _res


def project_animCurve_value(node = None, targetFrame = None, sampleStart = None, sampleEnd = None,
                            attributes = ['tx','ty','tz','rx','ry','rz','sx','sy','sz'],
                            mode = 'project',
                            setValue = False):
    """
    
    """
    _res = []
    _timeDelta = COREMATH.get_fixedTimeDelta()
    
    for a in attributes:
        mVector = []
        mVelocity = []
        
        mValues = []
    
        #_current = mc.currentTime(q=True)
        
        for frame in range(int(sampleStart), int(sampleEnd+1)):
            #print(frame)
            #mc.currentTime(frame, edit=True)
            _v = get_anim_value_by_time(node,[a],frame)
            mValues.append( COREMATH.Vector3(_v,frame,0) )
            
            #mPos.append(POS.get(obj,asEuclid=1))
            
    
        for i,v in enumerate(mValues):
            if v != mValues[-1]:
                mVector.append( COREMATH.get_vector_of_two_points(v,mValues[i+1],asEuclid=True))
    
            if i:
                _vel = DIST.get_distance_between_points(v,mValues[i-1]) / (_timeDelta)
                mVelocity.append(_vel)
    
    
        if len(mVelocity) ==1:
            mVelocity.append(mVelocity[-1])
        if len(mVector) == 1:
            mVector.append(mVector[-1])
    
        _timePassed = (targetFrame - sampleEnd) * _timeDelta
    
        #pprint.pprint([mPos,mVector,mVelocity,_timePassed])
    
        _tmp = COREMATH.average_vector_args(mVector)#...average the vectors
        if mode == 'reflect':
            _tmp = [-v for v in _tmp]
        mVec = COREMATH.Vector3(_tmp[0],_tmp[1],_tmp[2])
        #    mVec.reflect(COREMATH.Vector3(-1,-1,-1))
            
        mVel = COREMATH.average(mVelocity)
        
        #mVel.normalize()
        #pprint.pprint([mVec,mVel,_timePassed])
    
        final_point = [mValues[-1].x + (mVec.x * mVel * _timePassed), 
                       mValues[-1].y + (mVec.y * mVel * _timePassed), 
                       mValues[-1].z + (mVec.z * mVel * _timePassed)] 
        pprint.pprint(final_point)
        #mc.currentTime(_current)
        _res.append(final_point)
        if setValue:
            mc.setKeyframe( node, t=[targetFrame], at=a, v=final_point[0])
            mc.dgdirty(node)
    return _res
