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
#May not use DISTANCE,CURVES
from cgm.core import cgm_General as cgmGeneral
from cgm.core.lib import name_utils as coreNames
reload(coreNames)
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import search_utils as SEARCH
reload(SEARCH)
reload(VALID)
from cgm.core.lib import snap_utils as SNAP
reload(SNAP)
from cgm.core.cgmPy import OM_Utils as cgmOM
from cgm.core.lib import position_utils as POS
from cgm.core.lib import distance_utils as DIST
reload(POS)
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import node_utils as NODES
reload(NODES)
reload(ATTR)
#TO REFACTOR
#from cgm.lib import attributes

from cgm.core.classes import DraggerContextFactory as cgmDrag
reload(cgmDrag)

#>>> Utilities
#===================================================================
@cgmGeneral.Timer
def create(target = None, position = None, tag = True, setMatchTarget=True, pivot = 'rp', mode = 'fromTarget',name=None):
    """
    Return the short name of an object

    :parameters
        :target(str): What to create a loc from
        :tag(bool): Whether to tag for updating or special naming
        :pivot: Whether to force it to be created at the rotatePivot, scalePivot or BoundingBox center
        :mode
            fromTarget -- can be component or transform
            midPoint -- mid point of specfied targets
            closestPointOnTarget -- closest point from source to targets
            closestTarget -- closest target from source
            rayCast -- create a rayCast locator. For more options, see LOCINATOR
            attachPoint -- Create a rayCast follicle, and parent your loc to that.
        :setMatchTarget
    :returns
        short name(str)
    """   
    _str_func = "create"
    
    try:
        if mode == 'rayCast':
            #_catch = mc.group(em=True)
            class rayCastLoc(cgmDrag.clickMesh):
                def release_post_insert(self):
                    #ATTR.set_messagse(_catch, 'tmpMsg', self.l_created[-1])
                    _loc = self.l_created[-1]
                    _mLoc = r9Meta.MetaClass(_loc)
                    _buffer = _mLoc.cgmLocDat
                    _target = ATTR.get_message(_loc,'meshTarget')[0]
                    _loc = mc.rename(_loc, "{0}_u{1}_v{2}_rayCast_loc".format(coreNames.get_base(_target),
                                                                          "{0:.4f}".format(_buffer['uv'][0]),
                                                                          "{0:.4f}".format(_buffer['uv'][1]),
                                                                          ))
                    self.dropTool()
                                   
            rayCastLoc(create='locator')
            #_res = ATTR.get_message(_catch,'tmpMsg')[0]
            return True
        
        _loc = mc.spaceLocator()[0]
    
        if position:
            mc.move (position[0],position[1],position[2], _loc, ws=True)
            if name:
                return mc.rename(_loc, name)            
            return mc.rename("pos_loc")
        if not target:
            return mc.rename("world_center_loc")
    
        _targets = VALID.objStringList(target, noneValid=False, calledFrom= __name__ + _str_func + ">> validate target")
        #_targets = VALID.listArg(target)
        if tag or mode:
            _mi_loc = r9Meta.MetaClass(_loc)
            if not _mi_loc.hasAttr('cgmLocDat'):
                _mi_loc.addAttr('cgmLocDat',attrType='string')
                
        log.debug("|{0}| >> {1} mode...".format(_str_func,mode))
               
        if mode in ['fromTarget','attachPoint']:
            if len(_targets) != 1:
                log.warning("|{0}| >> mode: {1} | targets: {2} | ".format(_str_func,mode,_targets))
                raise ValueError,"May only have one target for mode: {0} | targets: {1}".format(mode,_targets)            
            
            _target = _targets[0]
            
            if name:
                _loc = mc.rename(_loc, name)
            else:
                _loc = mc.rename(_loc,"{0}_fromTarget_loc".format( coreNames.get_base(_target)))
    
            if tag:#store info
                ATTR.store_info(_loc,'cgmName',coreNames.get_base(_target), attrType='string', lock = True)
                ATTR.store_info(_loc,'cgmLocMode','fromTarget',lock = True)
                ATTR.set_message(_loc, 'cgmLocSource',_target,'cgmLocDat')
                if not VALID.is_component(_target) and setMatchTarget:
                    SNAP.matchTarget_set(_target,_loc)
                #_d = r9Meta.MetaClass(_loc).cgmLocDat
                
                _res =update(_loc)
            _res = update(_loc, _target, 'fromTarget')
            
            if mode == 'attachPoint':
                class follicleAttach(cgmDrag.clickMesh):
                    def release_post_insert(self):
                        _str_funcName = 'follicleAttach.release'
                        """if not self.b_dragStoreMode:#If not on drag, do it here. Otherwise do it on update
                            if self._posBuffer:
                                self.l_return.extend(self._posBuffer)
                                if self._posBufferRaw:
                                    self.l_returnRaw.extend(self._posBufferRaw)
                                else:
                                    self.l_returnRaw.extend(self._posBuffer)
                        
                            if self._createModeBuffer:
                                self.l_created.extend(self._createModeBuffer)"""
                        
                        for pos in self.l_returnRaw:
                            log.debug("|{0}|...pos {1}".format(_str_funcName,pos))                
                            for i,m in enumerate(self.d_meshPos.keys()):
                                log.debug("|{0}|...mesh: {1}".format(_str_funcName,m))                                    
                                for i2,h in enumerate(self.d_meshPos[m]):
                                    if h == pos:
                                        log.debug("Found follicle match!")
                                        try:
                                            _set = [m, self.d_meshUV[m][i2], "{0}_u{1}_v{2}".format(coreNames.get_short(m),"{0:.4f}".format(self.d_meshUV[m][i2][0]),"{0:.4f}".format(self.d_meshUV[m][i2][1]))]
                                            self._l_folliclesToMake.append(_set)
                                            log.debug("|{0}|...uv {1}".format(_str_funcName,_set))                                                
                                        except Exception,err:
                                            log.error("|{0}| >> Failed to query uv for hit {2} on shape {2} | err:{1}".format(_str_funcName,err,pos,m))                
                            if self._l_folliclesToMake:
                                for f_dat in self._l_folliclesToMake:
                                    _follicle = NODES.add_follicle(f_dat[0],f_dat[2])
                                    log.info("|finalize| >> Follicle created: {0}".format(_follicle))                        
                                    ATTR.set(_follicle[0],'parameterU',f_dat[1][0])
                                    ATTR.set(_follicle[0],'parameterV',f_dat[1][1])
                                    mc.parent(_loc, _follicle[0])
                        mc.delete(self.l_created)
                        self.dropTool()
                                       
                follicleAttach()
                
            return _loc
        elif not _targets:
            raise ValueError,"Must have targets for mode: {0} | targets: {1}".format(mode,_targets)
        else:
            if len(_targets) <= 2 and mode not in ['midPoint']:
                log.warning("|{0}| >> mode: {1} | targets: {2} | ".format(_str_func,mode,_targets))            
                raise ValueError,"Must have more than two targets for mode: {0} | targets: {1}".format(mode,_targets)
            
            _name = "{0}_{1}_loc".format('_to_'.join([coreNames.get_base(t) for t in _targets]),mode)
  
            _loc = mc.rename(_loc, _name)
                
            if tag:
                ATTR.store_info(_loc,'cgmName',_name, lock = True)
                ATTR.store_info(_loc,'cgmLocMode',mode,lock = True)
                ATTR.msgList_connect(_loc, 'cgmLocSource',_targets, dataAttr='cgmLocDat')
                
                if not VALID.is_component(_targets[0]) and setMatchTarget:
                    SNAP.matchTarget_set(_targets[0],_loc)

                return update(_loc)
            return update(_loc, _targets, mode)
        
    except ValueError,err:
        try:mc.delete(_loc)
        except:pass
        raise ValueError,err


def update(loc = None, targets = None, mode = None, forceBBCenter = False):
    """
    Get data for updating a loc

    :parameters
        target(str): What to use for updating our loc
        source(list): What to use to update if no data is stored

    :returns
        info(dict)
    """   
    def getAndMove(loc,targets = None,mode=None,forceBBCenter=False):
        
        log.info("|{0}| >> mode: {1} | targets: {2}".format(_str_func,mode,targets))
        if not targets:
            raise ValueError,"Must have targets"
        
        _kws = {'target':loc, 'move':True, 'rotate':True }
        
        if mode == 'fromTarget':
            _d = POS.get_info(targets[0])
            _kws['infoDict'] = _d
        
        elif mode == 'midPoint':
            if len(targets) == 1:
                _d = POS.get_info(targets[0],boundingBox=True)
                _kws['infoDict'] = _d                
            
            elif not len(targets) >= 2:
                raise ValueError,"midPoint mode must have at least two targets"
            else:
                _d = get_midPointDict(targets,forceBBCenter)
                _kws['infoDict'] = _d

        elif mode == 'closestPoint':
            if not len(targets) >= 2:
                raise ValueError,"midPoint mode must have at least two targets"
            
            _d = {'position':DIST.get_by_dist(targets[0],targets[1:],resMode='pointOnSurface')}
            _kws['infoDict'] = _d
            _kws['rotate'] = False
 
        elif mode == 'closestTarget':
            if not len(targets) >= 3:
                raise ValueError,"midPoint mode must have at least three targets"
            
            _d = POS.get_info(DIST.get_by_dist(targets[0],targets[1:],resMode='object'))
            _d['rotateOrder'] = False
            _d['rotateAxis'] = False
            
            _kws['infoDict'] = _d
            
        elif mode == 'rayCast':
            _dbuffer = r9Meta.MetaClass(_loc).cgmLocDat
            _d = {}
            _p = POS.get_uv_position(_target[0], _dbuffer['uv'])
            if _dbuffer.get('offsetDist'):
                _v = POS.get_uv_normal(_target[0], _dbuffer['uv'])
                _dist = _dbuffer.get('offsetDist')
                _p = DIST.get_pos_by_vec_dist(_p,_v,_dist)
            _d['position'] = _p 
            _kws['infoDict'] = _d
            _kws['rotate'] = False
        else:
            log.error("|{0}| >> unknown mode: {1}".format(_str_func,_mode))                
            return False        
            
        try:return position(**_kws)
        except Exception,err:
            log.error("|{0}| >> loc: {1}".format(_str_func,loc))
            cgmGeneral.log_info_dict(_kws['infoDict'],"{0} >> {1}".format(_str_func,mode)) 
            log.error("|{0}| >> err: {1}".format(_str_func,_err))
            return False
        
    
    _str_func = "update"
    _loc = VALID.objString(loc, noneValid=True, calledFrom = __name__ + _str_func + ">> validate loc")
    _type = VALID.get_mayaType(_loc)

    _targets = VALID.listArg(targets)

    if _type == 'locator':
        if mode and _targets:
            log.info("|{0}| >> mode override...".format(_str_func))         
            
            return getAndMove(_loc,_targets,mode,forceBBCenter)

        elif _targets:
            log.info("|{0}| >> source mode...".format(_str_func))
            if len(_targets) >1:
                log.info("|{0}| >> assuming midPoint...".format(_str_func))
                return getAndMove(_loc,_targets,'midPoint',forceBBCenter)
            else:
                log.info("|{0}| >> singleTarget...".format(_str_func))
                _d = POS.get_info(_targets,boundingBox=forceBBCenter)
                position(_loc,_d)
                return True                
        else:
            log.info("|{0}| >> tagged...".format(_str_func))          
            _mode = SEARCH.get_nodeTagInfo(_loc,'cgmLocMode')
            if _mode == 'fromTarget':
                _targets = ATTR.get_message(_loc,'cgmLocSource','cgmLocDat')
                return getAndMove(_loc,_targets,_mode,forceBBCenter)

            elif _mode == 'midPoint':
                _targets = ATTR.msgList_get(_loc,'cgmLocSource','cgmLocDat')
                return getAndMove(_loc,_targets,_mode,forceBBCenter)

            elif _mode == 'closestPoint':
                _targets = ATTR.msgList_get(_loc,'cgmLocSource','cgmLocDat')
                return getAndMove(_loc,_targets,_mode,forceBBCenter)

            elif _mode == 'closestTarget':
                _targets = ATTR.msgList_get(_loc,'cgmLocSource','cgmLocDat')
                log.info("|{0}| >> targets: {1}".format(_str_func,_targets))
                return getAndMove(_loc,_targets,_mode,forceBBCenter)
            elif _mode == 'rayCast':
                _target = ATTR.get_message(_loc,'meshTarget')
                return getAndMove(_loc,_target,_mode)
            else:
                log.error("|{0}| >> unknown mode: {1}".format(_str_func,_mode))                
                return False
                
    else:
        raise ValueError,"Not a locator. target: {0} | type: {1}".format(_loc,_type)


    raise RuntimeError,"Shouldn't have arrived here. target: {0}".format(_loc)

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
        if infoDict.get('rotateOrder'):mc.xform(_target, roo=infoDict['rotateOrder'],p=True)
        if infoDict.get('rotation'):mc.xform(_target, ro=infoDict['rotation'], ws = True)
        if infoDict.get('rotateAxis'):mc.xform(_target, ra=infoDict['rotateAxis'],p=True)

    #mTarget = r9Meta.getMObject(target)
    mc.xform(_target, rp=infoDict['position'], ws = True, p=True)        
    if infoDict.get('scalePivot'):mc.xform(_target, sp=infoDict['scalePivot'], ws = True, p=True)    

    #Rotate
    #if infoDict['objectType'] == 'polyFace':
        #constBuffer = mc.normalConstraint((locInfo['createdFrom']),locatorName)
        #mc.delete(constBuffer[0])

    return True


def get_midPointDict(sourceList,forceBBCenter = False):
    _l_info = []
    _l_pos = []
    _l_rot = []
    for s in sourceList:
        _d = POS.get_info(s,boundingBox=forceBBCenter)
        _l_pos.append(_d['position'])
        _l_rot.append(_d['rotation'])
        _l_info.append(_d)
    _d = _l_info[0]
    _d['position'] = MATH.get_average_pos(_l_pos)
    _d['rotation'] = MATH.get_average_pos(_l_rot)
    #position(_target,_d)
    return _d   

def get_closestPointDict(basePoint,sourceList):
    pass

def tag_to_loc(obj = None, loc = None):
    """
    Match an object to it's loc or a specified loc.

    :parameters
        obj(str): What to use for updating our loc
        loc(str): locator to use

    :returns
        None
    """
    _str_func = "tag_to_loc"
    
    