"""
------------------------------------------
snap_utils: cgm.core.lib.transform_utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

Unified location for transform calls. metanode instances may by passed
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
from maya import mel
# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
#from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import math_utils as MATH
#from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import position_utils as POS
from cgm.core.lib import snap_utils as SNAP

from cgm.core.lib import euclid as EUCLID
from cgm.core.lib import attribute_utils as ATTR


#Link up some of our ther functions for ease of call
position_get = POS.get
position_set = POS.set

localPosition_get = POS.get_local
localPosition_set = POS.set_local

snap = SNAP.go
aim = SNAP.aim
aim_atPoint = SNAP.aim_atPoint
aim_atMidPoint = SNAP.aim_atMidPoint
verify_aimAttrs = SNAP.verify_aimAttrs



"""
@property 
def localPosition(self):
    '''Return the local space position of the transform'''
    pos = mc.getAttr( self.GetAttrString("translate") )[0]
    return Vector3(pos[0], pos[1], pos[2])

@localPosition.setter
def localPosition(self, new_pos):
    '''Set the local space position of the transform'''
    mc.setAttr( self.GetAttrString("translate"), new_pos.x, new_pos.y, new_pos.z, type="double3" ) 

@property
def eulerAngles(self):
    '''Return the rotation of the transform in euler angles'''
    rot = mc.getAttr( self.GetAttrString("rotate") )[0]
    return Vector3( rot[0], rot[1], rot[2] )

@eulerAngles.setter
def eulerAngles(self, new_rot):
    '''Set the rotation of the transform in euler angles'''
    mc.setAttr( self.GetAttrString("rotate"), new_rot.x, new_rot.y, new_rot.z, type="double3" )

@property 
def localScale(self):
    '''Return the local space scale of the transform'''
    scale = mc.getAttr( self.GetAttrString("scale") )[0]
    return Vector3( scale[0], scale[1], scale[2] )

@localScale.setter
def localScale(self, new_scale):
    '''Set the scale of the transform in local space'''
    mc.setAttr( self.GetAttrString("scale"), new_scale.x, new_scale.y, new_scale.z, type="double3" )

@property
def lossyScale(self):
    lossyScale = self.localScale
    for parent in self.parents:
        lossyScale = lossyScale * parent.localScale
    return lossyScale
"""

def rotation():
    pass



def worldMatrix(node = None, asMatrix = False):
    """
    Query the worldMatrix of a given node
    
    :parameters:
        node(str): node to query
        asMatrix(bool): whether to return a EUCLID.Matrix4

    :returns
        matrix
    """   
    _str_func = 'matrix'
    
    node = VALID.mNodeString(node)

    try:matrix_a = mc.xform( node,q=True,m=True, ws=True )
    except Exception, e:
        if not VALID.is_transform(node):
            log.error("|{0}| >> Not a transform: '{1}'".format(_str_func,node))                        
            return False
        
        log.error("|{0}| >> Failed: '{1}'".format(_str_func,node))
        #for arg in e.args:
            #log.error(arg)
        raise Exception,e 
        
    if not asMatrix:
        return matrix_a
    
    current_matrix = EUCLID.Matrix4()
    current_matrix.a = matrix_a[0]
    current_matrix.b = matrix_a[1]
    current_matrix.c = matrix_a[2]
    current_matrix.d = matrix_a[3]
    current_matrix.e = matrix_a[4]
    current_matrix.f = matrix_a[5]
    current_matrix.g = matrix_a[6]
    current_matrix.h = matrix_a[7]
    current_matrix.i = matrix_a[8]
    current_matrix.j = matrix_a[9]
    current_matrix.k = matrix_a[10]
    current_matrix.l = matrix_a[11]
    current_matrix.m = matrix_a[12]
    current_matrix.n = matrix_a[13]
    current_matrix.o = matrix_a[14]
    current_matrix.p = matrix_a[15]
    
    return current_matrix





