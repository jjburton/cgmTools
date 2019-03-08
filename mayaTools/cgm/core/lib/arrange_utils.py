"""
------------------------------------------
arrange_utils: cgm.core.lib.distance_utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
# From Python =============================================================
import copy
import re
import sys

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGen
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import node_utils as NODE
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.position_utils as POS
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.curve_Utils as CURVES

#>>> Utilities
#===================================================================


def layout_byColumn(objList,columns=3,startPos = [0,0,0]):
    """
    Get a uv position in world space. UV should be normalized.
    
    :parameters:
        objList(list) | list of objects to arrange
        uValue(float) | uValue  
        vValue(float) | vValue 

    :returns
        pos(double3)

    """        
    _str_func = 'layout_byColumn'
    
    sizeXBuffer = []
    sizeYBuffer = []
    for obj in objectList:
        sizeBuffer = distance.returnBoundingBoxSize(obj)
        sizeXBuffer.append(sizeBuffer[0])
        sizeYBuffer.append(sizeBuffer[1])

    for obj in objList:
        mc.move(0,0,0,obj,a=True)

    sizeX = max(sizeXBuffer) * 1.75
    sizeY = max(sizeYBuffer) * 1.75

    startX = startPos[0]
    startY = startPos[1]
    startZ = startPos[2]

    col=1
    objectCnt = 0
    #sort the list

    sortedList = lists.returnListChunks(objectList,columns)
    bufferY = startY
    for row in sortedList:
        bufferX = startX
        for obj in row:
            mc.xform(obj,os=True,t=[bufferX,bufferY,startZ])
            bufferX += sizeX
        bufferY -= sizeY  
        
_d_arrangeLine_ann = {'linearEven':"Layout on line from first to last item evenly",
                      'linearSpaced':'Layout on line from first to last item closest as possible to original position',
                      'cubicEven':'Layout evenly on a curve created from the list',
                      'cubicArcEven':'Layout evenly on an arc defined by start,mid,last',
                      'cubicArcSpaced':'Layout spaced on an arc defined by start,mid,last',                      
                      'cubicRebuild2Even':'Layout evenly on a 2 span rebuild curve from the list.',
                      'cubicRebuild3Even':'Layout evenly on a 2 span rebuild curve from the list.',
                      'cubicRebuild2Spaced':'Layout spaced on a 2 span rebuild curve from the list.',
                      'cubicRebuild3Spaced':'Layout spaced on a 2 span rebuild curve from the list.'}

def alongLine(objList = None, mode = 'even', curve = 'linear',spans = 2):
    """    
    Arrange a list of objects evenly along a vector from first to last
    
    :parameters:
        objList(list): objects to layout
        mode(string)
            'even' - evenly distributed along line
            'spaced' - distribute along line as close as possible to current position

    :returns
        list of constraints(list)
    """   
    _str_func = 'onLine'
    objList = VALID.mNodeStringList(objList)
    log.info("|{0}| >> ObjList: {1} ".format(_str_func,objList))             
    _len = len(objList)
    if _len < 3:
        raise ValueError,"|{0}| >> Need at least 3 objects".format(_str_func)
    
    _pos_start = POS.get(objList[0])
    _pos_end = POS.get(objList[-1])    
    curveBuffer = []
    if curve == 'linear':
        if mode != 'even':
            curveBuffer = mc.curve (d=1, ep = [_pos_start,_pos_end])
    elif curve in ['cubic','cubicRebuild']:
        l_pos = [POS.get(o) for o in objList]
        knot_len = len(l_pos)+3-1		
        crv1 = mc.curve (d=3, ep = l_pos, k = [i for i in range(0,knot_len)], os=True)
        curveBuffer = [crv1]
        if curve == 'cubicRebuild':
            curveBuffer.append(mc.rebuildCurve (crv1, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=spans, d=3, tol=0.001)[0])

    elif curve == 'cubicArc':
        _mid = MATH.get_midIndex(_len)-1
        log.info("|{0}| >> cubicArc | mid: {1} ".format(_str_func,_mid))
        
        l_pos = [POS.get(o) for o in [objList[0],objList[_mid],objList[-1]]]
        knot_len = len(l_pos)+3-1		
        curveBuffer = mc.curve (d=3, ep = l_pos, k = [i for i in range(0,knot_len)], os=True)
    else:
        raise ValueError,"|{0}| >>unknown curve setup: {1}".format(_str_func,curve)
    
    if mode == 'even':
        if curve == 'linear':
            _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)
            _offsetDist = DIST.get_distance_between_points(_pos_start,_pos_end) / (_len - 1)
            _l_pos = [ DIST.get_pos_by_vec_dist(_pos_start, _vec, (_offsetDist * i)) for i in range(_len)]
            log.info("|{0}| >> offset: {1} ".format(_str_func,_offsetDist))   
            log.info("|{0}| >> l_pos: {1} ".format(_str_func,_l_pos)) 
            for i,o in enumerate(objList[1:-1]):
                POS.set(o,_l_pos[i+1])        
        else:
            _l_pos = CURVES.getUSplitList(curveBuffer,points = _len,rebuild=1)
            
        for i,o in enumerate(objList[1:-1]):
            POS.set(o,_l_pos[i+1])
            
    elif mode == 'spaced':
        _l_pos = []
        for i,o in enumerate(objList[1:-1]):
            #SNAP.go(o,curveBuffer,pivot= 'closestPoint')
            p = DIST.get_by_dist(o,curveBuffer,resMode='pointOnSurface')
            POS.set(o,p)
            _l_pos.append(p)
    else:
        try:raise ValueError,"{0} >> mode not supported: {1}".format(sys._getframe().f_code.co_name, mode)
        except:raise ValueError,"mode not supported: {0}".format(mode)
        
        
    if curveBuffer:
        mc.delete(curveBuffer)
    return _l_pos



    
