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
        

def alongLine(objList = None):
    """    
    Arrange a list of objects evenly along a vector from first to last
    
    :parameters:
        objList(list): objects to layout

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
    
    _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)
    _offsetDist = DIST.get_distance_between_points(_pos_start,_pos_end) / (_len - 1)
    _l_pos = [ DIST.get_pos_by_vec_dist(_pos_start, _vec, (_offsetDist * i)) for i in range(_len)]
    log.info("|{0}| >> offset: {1} ".format(_str_func,_offsetDist))             
    log.info("|{0}| >> l_pos: {1} ".format(_str_func,_l_pos))             
    
    for i,o in enumerate(objList[1:-1]):
        POS.set(o,_l_pos[i+1])
        
    return _l_pos
    

    
