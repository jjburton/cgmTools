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
reload(SEARCH)
reload(VALID)
from cgm.core.lib import snap_utils as SNAP
from cgm.core.cgmPy import OM_Utils as cgmOM
from cgm.core.lib import position_utils as POS
reload(POS)
from cgm.core.lib import math_utils as MATH

#TO REFACTOR
from cgm.lib import attributes

#>>> Utilities
#===================================================================
@cgmGeneral.Timer
def create(target = None, position = None, tag = True, pivot = 'rp', mode = None):
    """
    Return the short name of an object
    
    :parameters
        :target(str): What to create a loc from
        :tag(bool): Whether to tag for updating or special naming
        :pivot: Whether to force it to be created at the rotatePivot, scalePivot or BoundingBox center
        :mode
            midPoint
            closestPointOnTarget
            closestTarget
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
    
    _targets = VALID.objStringList(target, noneValid=True, calledFrom= __name__ + _str_func + ">> validate target")
    
    if len(_targets) == 1:
        #Regular mode
        _target = _targets[0]
        _loc = mc.rename(_loc,"{0}_loc".format( coreNames.get_base(_target)))
        
        if tag:#store info
            attributes.storeInfo(_loc, 'cgmName',coreNames.get_short(_target),False)
    
            _d = {}
            attributes.storeInfo(_loc,'cgmLocMode','fromObject',False)
            if VALID.is_component(_target):
                _bfr = VALID.get_component(_target)
                _d['component'] = _bfr[0]
                _d['targetType'] = VALID.get_mayaType(_target)
    
            _target_trans = SEARCH.get_transform(_target)
    
            attributes.storeInfo(_loc,'cgmLocSource',_target_trans,False)
    
            mi_loc = r9Meta.MetaClass(_loc)
            mi_loc.addAttr('locData',attrType='string')
            mi_loc.locData = _d
            return update(_loc)
        return update(_loc, _target)
    
    else:#MidPointMode
        if tag:
            pass
        #return nameBuffer[0]
        #return cgmMeta.NameFactory(_loc).doNameObject()
        _loc = mc.rename(_loc,"{0}_loc".format( coreNames.get_base(target)))
    
    return update(_loc,_targets)


def update(target = None, source = None, mode = None, forceBBCenter = False):
    """
    Get data for updating a loc
    
    :parameters
        target(str): What to use for updating our loc
        source(list): What to use to update if no data is stored
        
    :returns
        info(dict)
    """   
    def get_midPointDict(source):
        _l_info = []
        _l_pos = []
        _l_rot = []
        for s in source:
            _d = POS.get_info(s,boundingBox=forceBBCenter)
            _l_pos.append(_d['position'])
            _l_rot.append(_d['rotation'])
            _l_info.append(_d)
        _d = _l_info[0]
        _d['position'] = MATH.get_average_pos(_l_pos)
        _d['rotation'] = MATH.get_average_pos(_l_rot)
        position(_target,_d)
        return _d   
    
    _str_func = "update"
    _target = VALID.objString(target, noneValid=True, calledFrom = __name__ + _str_func + ">> validate target")
    _type = VALID.get_mayaType(_target)
    
    _source = VALID.listArg(source)
    
    if _type == 'locator':
        if mode:
            log.info("|{0}| >> mode override...".format(_str_func))         
            raise Exception,"Not implemented"
        
        elif _source:
            log.info("|{0}| >> source mode...".format(_str_func))
            if len(_source) >1:
                log.info("|{0}| >> midPoint...".format(_str_func))
                position(_target,get_midPointDict(source))
                return
                    
                    
            else:
                log.info("|{0}| >> singleTarget...".format(_str_func))
                _d = POS.get_info(_source,boundingBox=forceBBCenter)
                position(_target,_d)
                return True                
        
        else:
            log.info("|{0}| >> tagged...".format(_str_func))          
            _mode = SEARCH.get_tag(_target,'cgmLocMode')
            log.info(_type)
            log.info(_mode)
            if _mode == 'fromObject':
                _source = SEARCH.get_tag(_target,'cgmName')
                log.info(_source)
                if _source:
                    _d = POS.get_info(_source)
                    position(_target,_d)
                    return True
    else:
        raise ValueError,"Not a locator. target: {0} | type: {1}".format(_target,_type)
    
    
    raise RuntimeError,"Shouldn't have arrived here. target: {0}".format(_target)
    
    return False

def position(target = None, infoDict = None, move = True, rotate = True):
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
    
    if move:
        mc.move (pos[0],pos[1],pos[2], _target, ws=True)
    if rotate:
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
            
