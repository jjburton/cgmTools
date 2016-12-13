"""
------------------------------------------
math_utils: cgm.core.lib.math_utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
# From Python =============================================================

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

#>>> Utilities
#===================================================================

def get_average_pos(posList = []):
    """
    Returns the average of a list of given positions
    
    :parameters:
        posList(list): List of positions
    :returns
        average(list)
    """   
    _str_func = 'get_average_pos'
    
    posX = []
    posY = []
    posZ = []
    for pos in posList:
        posBuffer = pos
        posX.append(posBuffer[0])
        posY.append(posBuffer[1])
        posZ.append(posBuffer[2])
    return [float(sum(posX)/len(posList)), float(sum(posY)/len(posList)), float(sum(posZ)/len(posList))]    