"""
locator_utils
Josh Burton 
www.cgmonks.com

"""
# From Python =============================================================
#import copy
#import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
#May not use DISTANCE,
from cgm.core import cgm_General as cgmGeneral
from cgm.core.lib import name_utils as coreNames
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import search_utils as SEARCH
reload(VALID)
from cgm.core.lib import snap_utils as SNAP
from cgm.core.cgmPy import OM_Utils as cgmOM

#TO REFACTOR
from cgm.lib import attributes

#>>> Utilities
#===================================================================
@cgmGeneral.Timer
def create(target = None, position = None, tag = True, pivot = 'rp'):
    """
    Return the short name of an object
    
    :parameters
        target(str): What to create a loc from
        tag(bool): Whether to tag for updating or special naming
        pivot: Whether to force it to be created at the rotatePivot, scalePivot or BoundingBox center

    :returns
        short name(str)
    """   
    _str_func = "create"
    
    _loc = mc.spaceLocator()[0]
    
    if position:
        mc.move (position[0],position[1],position[2], _loc, ws=True)
        return mc.rename("pos_loc")
    if not target:
        return mc.rename("world_center_loc")
    
    _target = VALID.objString(target, noneValid=True, calledFrom= __name__ + _str_func + ">> validate target")
    
    if tag:#store info
        attributes.storeInfo(_loc, 'cgmName',coreNames.get_short(_target),False)
        attributes.storeInfo(_loc,'cgmLocMode','fromObject',False)

        #return nameBuffer[0]
        #return cgmMeta.NameFactory(_loc).doNameObject()
        
    update(_loc)
    return mc.rename(_loc,"{0}_loc".format( coreNames.get_base(target)))

def update(target = None, mode = None, forceBBCenter = False):
    """
    Get data for updating a loc
    
    :parameters
        target(str): What to use for updating our loc
    
    :returns
        info(dict)
    """   
    _str_func = "update"
    _target = VALID.objString(target, noneValid=True, calledFrom = __name__ + _str_func + ">> validate target")
    _type = SEARCH.get_mayaType(_target)
    if _type == 'locator':
        _mode = SEARCH.get_tag(_target,'cgmLocMode')
        log.info(_type)
        log.info(_mode)
        if _mode == 'fromObject':
            _source = SEARCH.get_tag(_target,'cgmName')
            log.info(_source)
            if _source:
                _d = SNAP.get_info(_source)
                position(_target,_d)
                return True
    else:
        raise ValueError,"Not a locator. target: {0} | type: {1}".format(_target,_type)
    
    
    raise RuntimeError,"Shouldn't have arrived here. target: {0}".format(_target)
    
    return False

def position(target = None, infoDict = None):
    """
    Get data for updating a loc
    
    :parameters
        target(str): What to use for updating our loc
    
    :returns
        info(dict)
    """   
    _str_func = "position"
    _target = VALID.objString(target, noneValid=True, calledFrom = __name__ + _str_func + ">> validate target")
    
    pos = infoDict['position']
    
    mc.move (pos[0],pos[1],pos[2], _target, ws=True)
    mc.xform(_target, roo=infoDict['rotateOrder'],p=True)
    mc.xform(_target, ro=infoDict['rotation'], ws = True)
    mc.xform(_target, ra=infoDict['rotateAxis'],p=True)
    
    #mTarget = r9Meta.getMObject(target)
    mc.xform(_target, rp=infoDict['position'], ws = True, p=True)        
    mc.xform(_target, sp=infoDict['scalePivot'], ws = True, p=True)    
    
    #Rotate
    #if infoDict['objectType'] == 'polyFace':
        #constBuffer = mc.normalConstraint((locInfo['createdFrom']),locatorName)
        #mc.delete(constBuffer[0])

    return True


    """
    if search.returnObjectType(locatorName) == 'locator':
        locatorMode = search.returnTagInfo(locatorName,'cgmLocMode')
        if locatorMode == 'fromObject':
            obj = search.returnTagInfo(locatorName,'cgmName')
            if mc.objExists(obj) == True:
                locInfo = returnInfoForLoc(obj,forceBBCenter)
                doPositionLocator(locatorName,locInfo)
                return True
            else:
                guiFactory.warning ("The stored object doesn't exist")
                return False
    
        else:
            sourceObjects = search.returnTagInfo(locatorName,'cgmSource')
            targetObjectsBuffer = sourceObjects.split(',')
            targetObjects = []
            for obj in targetObjectsBuffer:
                if mc.objExists(obj):
                    targetObjects.append(obj)
                else:
                    guiFactory.warning  ('%s%s' % (obj, " not found, using any that are... "))
            if locatorMode == 'selectCenter':
                locBuffer = locMeCenter(targetObjects,forceBBCenter)
                position.moveParentSnap(locatorName,locBuffer)
                mc.delete(locBuffer)
    
            if locatorMode == 'closestPoint':
                locBuffer = locClosest(targetObjects[:-1],targetObjects[-1])
                position.moveParentSnap(locatorName,locBuffer)
                mc.delete(locBuffer)
    
    
    
        else:
            return False
    
        return locatorName"""
            
