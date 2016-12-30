"""
------------------------------------------
shape_utils: cgm.core.lib.shape_utils
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
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGen
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
reload(SHARED)
from cgm.lib import attributes

#>>> Utilities
#===================================================================
def set_color(target = None, key = None, index = None, rgb = None ):
    """
    Sets the color of a shape via override. In Maya 2016, they introduced 
    rgb value override.
    
    :parameters
        target(str): What to color - shape or transform with shapes
        key(varied): if str will check against our shared color dict definitions for rgb and index entries
        index(int): Color index
        rgb(list): rgb values to set in Maya 2016 or above

    :returns
        info(dict)
    """   
    _str_func = "set_color"
    if not target:raise ValueError,"|{0}| >> Must have a target".format(_str_func)

    if not SEARCH.is_shape(target):
        _shapes = mc.listRelatives(target, s=True)
        if not _shapes:
            raise ValueError,"|{0}| >> Not a shape and has no shapes: '{1}'".format(_str_func,target)
    else:
        _shapes = [target]
    
    if index is None and rgb is None and key is None:
        raise ValueError,"|{0}| >> Must have a value for index,rgb or key".format(_str_func)
    
    #...little dummy proofing..
    _type = type(key)
    
    if not issubclass(_type,str):
        log.debug("|{0}| >> Not a string arg for key...".format(_str_func))
        
        if rgb is None and issubclass(_type,list) or issubclass(_type,tuple):
            log.debug("|{0}| >> vector arg for key...".format(_str_func))            
            rgb = key
            key = None
        elif index is None and issubclass(_type,int):
            log.debug("|{0}| >> int arg for key...".format(_str_func))            
            index = key
            key = None
        else:
            raise ValueError,"|{0}| >> Not sure what to do with this key arg: {1}".format(_str_func,key)
    
    _b_RBGMode = False
    _b_2016Plus = False
    if cgmGen.__mayaVersion__ >=2016:
        _b_2016Plus = True
        
    if key is not None:
        _color = False
        if _b_2016Plus:
            log.debug("|{0}| >> 2016+ ...".format(_str_func))            
            _color = SHARED._d_colors_to_RGB.get(key,False)
            
            if _color:
                rgb = _color
        
        if _color is False:
            log.debug("|{0}| >> Color key not found in rgb dict checking index...".format(_str_func))
            _color = SHARED._d_colors_to_index.get(key,False)
            if _color is False:
                raise ValueError,"|{0}| >> Unknown color key: '{1}'".format(_str_func,key) 
                
    if rgb is not None:
        if not _b_2016Plus:
            raise ValueError,"|{0}| >> RGB values introduced in maya 2016. Current version: {1}".format(_str_func,cgmGen.__mayaVersion__) 
        
        _b_RBGMode = True        
        if len(rgb) == 3:
            _color = rgb
        else:
            raise ValueError,"|{0}| >> Too many rgb values: '{1}'".format(_str_func,rgb) 
        
    if index is not None:
        _color = index

    log.debug("|{0}| >> Color: {1} | rgbMode: {2}".format(_str_func,_color,_b_RBGMode))
    

    for i,s in enumerate(_shapes):
        mShape = r9Meta.MetaClass(s)
        
        mShape.overrideEnabled = True
        #attributes.doSetAttr(s,'overrideEnabled',True)
        
    
        if _b_RBGMode:
            mShape.overrideRGBColors = 1
            mShape.overrideColorRGB = _color
            #attributes.doSetAttr(s,'overrideRGBColors','RGB')#...brilliant attr naming here Autodesk...            
            #attributes.doSetAttr(s,'overrideColorsRGB',[1,1,1])

        else:
            if _b_2016Plus:
                mShape.overrideRGBColors = 0
            mShape.overrideColor = _color
    