"""
------------------------------------------
locinator: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
2.0 rewrite
================================================================
"""
__version__ = '2.0.01202017'


# From Python =============================================================
import copy
import re
import sys
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID
reload(VALID)
from cgm.core import cgm_General as cgmGen
reload(cgmGen)
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import locator_utils as LOC
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
from cgm.core.lib import search_utils as SEARCH
import cgm.core.classes.GuiFactory as cgmUI
reload(SNAP)
reload(LOC)
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
reload(MMCONTEXT)

from cgm.lib import lists



def update_obj(obj = None, move = True, rotate = True, boundingBox = False, targetPivot = 'rp'):
    """
    Updates an tagged loc or matches a tagged object
    
    :parameters:
        obj(str): Object to modify
        target(str): Target to match

    :returns
        success(bool)
    """     
    _str_func = 'update_obj'
    
    _obj = VALID.objString(obj, noneValid=False, calledFrom = __name__ + _str_func + ">> validate obj")
    
    _locMode = ATTR.get(_obj,'cgmLocMode')
    if _locMode:
        log.debug("|{0}| >> loc mode. updating {1}".format(_str_func,NAMES.get_short(_obj)))
        return LOC.update(_obj)
    if mc.objExists(_obj +'.cgmMatchTarget'):
        log.debug("|{0}| >> Match mode. Matching {1} | move: {2} | rotate: {3} | bb: {4}".format(_str_func,NAMES.get_short(_obj),move,rotate,boundingBox))
        return SNAP.matchTarget_snap(_obj,move,rotate,boundingBox)
    
    log.warning("|{0}| >> Not updatable: {1}".format(_str_func,NAMES.get_short(_obj)))    
    return False

def get_objDat(obj=None, report = False):
    """
    Get info as to whether an object is updatable or is a loc.
    
    :parameters:
        obj(str): Object to modify
        report(bool): Whether to report data

    :returns
        data(dict)
    """         
    _str_func = 'get_objDat'
    
    _res = {'updateType':None}
    
    _locMode = ATTR.get(obj,'cgmLocMode') or None
    if _locMode:
        _res['updateType'] = 'locUpdate'
        _res['locMode'] = _locMode
        _res['loc'] = obj
        
        _source = ATTR.get(obj,'cgmLocSource') or None
        if _source:
            _res['source'] = _source[0]
        
    elif mc.objExists(obj + '.cgmMatchTarget'):
        _res['updateType'] = 'matchTarget'
        _res['matchTarget'] = ATTR.get_message(obj, 'cgmMatchTarget','cgmMatchDat',0)
        _res['loc'] = _res['matchTarget'][0]
        _res['source'] = obj
    if not report:
        return _res
    
    log.info(cgmGen._str_hardLine)
    
    _res['objecType'] = VALID.get_mayaType(obj)
    
    cgmGen.print_dict(_res,"'{0}' Locinator data...".format(obj),_str_func)
    
    #log.info("Obj: '{0}' | updateType: '{1}' | objectType: {2}".format(obj,_res['updateType'],_res['objecType']))
    
    return _res
        

def bake_match(targets = None, move = True, rotate = True, boundingBox = False, pivot = 'rp',
               timeMode = 'slider', keysMode = 'loc'):
    """
    Updates an tagged loc or matches a tagged object
    
    :parameters:
        obj(str): Object to modify
        target(str): Target to match
        
        timeMode(str):
            :slider/range
            :scene
        keysMode(str)
            :loc
            :source
            :combine
            :frames -- bake every frame

    :returns
        success(bool)
    """     
    _str_func = 'update_obj'
    
    #log.info("|{0}| >> Not updatable: {1}".format(_str_func,NAMES.get_short(_obj)))  
    _targets = VALID.objStringList(l_args=targets,isTransform=True,noneValid=False,calledFrom=_str_func)
    
    if not _targets:raise ValueError,"|{0}| >> no targets.".format(_str_func)
    if not move and not rotate:raise ValueError,"|{0}| >> Move and rotate both False".format(_str_func)
    
    log.info("|{0}| >> Targets: {1}".format(_str_func,_targets))
    log.info("|{0}| >> move: {1} | rotate: {2} | boundingBox: {3}".format(_str_func,move,rotate,boundingBox))    
    log.info("|{0}| >> timeMode: {1} | keysMode: {2}".format(_str_func,timeMode,keysMode))
    
    _l_toDo = []
    _d_toDo = {}
    _d_keyDat = {}
    
    #>>>Validate ==============================================================================================  
    for o in _targets:
        _d = get_objDat(o)
        if _d:
            _l_toDo.append(o)
            _d_toDo[o] = _d
            
    #>>>Key data ==============================================================================================    
    _d_keyDat['currentTime'] = mc.currentTime(q=True)
    
    if timeMode in ['slider','range']:
        _d_keyDat['frameStart'] = mc.playbackOptions(q=True,min=True)
        _d_keyDat['frameEnd'] = mc.playbackOptions(q=True,max=True)
    elif timeMode == 'scene':
        _d_keyDat['frameStart'] = mc.playbackOptions(q=True,animationStartTime=True)
        _d_keyDat['frameEnd'] = mc.playbackOptions(q=True,animationEndTime=True)   
    else:
        raise ValueError,"|{0}| >> Unknown timeMode: {1}".format(_str_func,timeMode)
    
    _attrs = []
    if move:
        _attrs.extend(['translateX','translateY','translateZ']) 
    if rotate:
        _attrs.extend(['rotateX','rotateY','rotateZ']) 
    
    _d_keyDat['attrs'] = _attrs

    cgmGen.print_dict(_d_toDo,"bake_match to do...",__name__)
    cgmGen.print_dict(_d_keyDat,"Key data..",__name__)
    
    #>>>Process ==============================================================================================    
    _d_keysOfTarget = {}
    _keysToProcess = []
    _start = int(_d_keyDat['frameStart'])
    _end = int(_d_keyDat['frameEnd'])  
    
    #First for loop, gathers key data per object...
    for o in _l_toDo:
        log.info("|{0}| >> Processing: '{1}' | keysMode: {2}".format(_str_func,o,keysMode))
        _d = _d_toDo[o]
        
        #Gather target key data...
        if keysMode == 'loc':
            _keys = SEARCH.get_key_indices_from( SEARCH.get_transform( _d['loc']))
        elif keysMode == 'source':
            _keys = SEARCH.get_key_indices_from( SEARCH.get_transform( _d['source']))
        elif keysMode in ['combine','both']:
            _source = SEARCH.get_key_indices_from( SEARCH.get_transform( _d['loc']))
            _loc = SEARCH.get_key_indices_from( SEARCH.get_transform( _d['source']))
            
            _keys = _source + _loc
            _keys = lists.returnListNoDuplicates(_keys)
        elif keysMode == 'frames':
            _keys = range(_start,_end +1)
        else:raise ValueError,"|{0}| >> Unknown keysMode: {1}".format(_str_func,keysMode)
        
        if not _keys:
            log.error("|{0}| >> No keys found for: '{1}'".format(_str_func,o))
            break
        
        for k in _keys:
            if k < _d_keyDat['frameStart'] or k > _d_keyDat['frameEnd']:
                log.info("|{0}| >> Removing key from list: {1}".format(_str_func,k))                
                _keys.remove(k)
        
        _d_keysOfTarget[o] = _keys
        
        _keysToProcess.extend(_keys)
        
        log.info("|{0}| >> Keys: {1}".format(_str_func,_keys))
        

        #Clear keys in range
        mc.cutKey(o,animation = 'objects', time=(_start,_end+ 1),at= _attrs)
    
    #Second for loop processes our keys so we can do it in one go...
    _keysToProcess = lists.returnListNoDuplicates(_keysToProcess)
    
    #Process 
    _progressBar = cgmUI.doStartMayaProgressBar(len(_keysToProcess),"Processing...")
    
    for i,f in enumerate(_keysToProcess):

        mc.currentTime(f)
        
        for o in _l_toDo:
            _keys = _d_keysOfTarget[o]
            if f in _keys:
                
                if mc.progressBar(_progressBar, query=True, isCancelled=True ):
                    break
                mc.progressBar(_progressBar, edit=True, status = ("{0} On frame {1} for '{2}'".format(_str_func,f,o)), step=1)                    
            
            
                update_obj(o,move,rotate,boundingBox)
            
                mc.setKeyframe(o,time = f, at = _attrs)
         

    cgmUI.doEndMayaProgressBar(_progressBar)
    mc.currentTime(_d_keyDat['currentTime'])
    
    mc.select(_targets)
    return True
        
        
def uiRadial_create(self,parent,direction = None):
    #>>>Loc ==============================================================================================    
        _l = mc.menuItem(parent=parent,subMenu=True,
                     l = 'Loc',
                     rp = "N")
    
        mc.menuItem(parent=_l,
                    l = 'World Center',
                    c = cgmGen.Callback(LOC.create),
                    rp = "S")          
        mc.menuItem(parent=_l,
                    l = 'Me',
                    en = self._b_sel,
                    c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, self._l_sel,'each'),
                    rp = "N")           
        mc.menuItem(parent=_l,
                    l = 'Mid point',
                    en = self._b_sel_pair,                    
                    c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, self._l_sel,'all','midPointLoc',False,**{'mode':'midPoint'}),                                                                      
                    rp = "NE")            
        mc.menuItem(parent=_l,
                    l = 'closest Point',
                    en = self._b_sel_pair,                    
                    c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, self._l_sel,'all','closestPoint',False,**{'mode':'closestPoint'}),                                                                      
                    rp = "NW") 
        mc.menuItem(parent=_l,
                    l = 'closest Target',
                    en = self._b_sel_few,                    
                    c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, self._l_sel,'all','closestTarget',False,**{'mode':'closestTarget'}),                                                                      
                    rp = "W")   
        mc.menuItem(parent=_l,
                    l = 'rayCast',
                    c = lambda *a:self.rayCast_create('locator',False),
                    rp = "SE")       

def uiSetupOptionVars(self):
    self.var_matchModeMove = cgmMeta.cgmOptionVar('cgmVar_matchModeMove', defaultValue = 1)
    self.var_matchModeRotate = cgmMeta.cgmOptionVar('cgmVar_matchModeRotate', defaultValue = 1)
    self.var_matchModePivot = cgmMeta.cgmOptionVar('cgmVar_matchModePivot', defaultValue = 0)
    self.var_matchMode = cgmMeta.cgmOptionVar('cgmVar_matchMode', defaultValue = 2)
    
def uiFunc_change_matchMode(self,arg):
    self.var_matchMode.value = arg    
    if arg == 0:
        self.var_matchModeMove.value = 1
        self.var_matchModeRotate.value = 0
    elif arg == 1:
        self.var_matchModeMove.value = 0
        self.var_matchModeRotate.value = 1
    elif arg == 3:
        self.var_matchModeMove.value = 1
        self.var_matchModeRotate.value = 1
    else:
        self.var_matchMode.value = 2        
        raise ValueError,"|{0}| >> Unknown matchMode: {1}".format(sys._getframe().f_code.co_name,arg)
        
def uiOptionMenu_matchMode(self, parent):
    try:#>>> KeyMode ================================================================================
        _str_section = 'match mode'
        uiMatch = mc.menuItem(p=parent, l='Match ', subMenu=True)
        
        uiMenu = mc.menuItem(p=uiMatch, l='Mode ', subMenu=True)    
        uiRC = mc.radioMenuItemCollection()
        _v = self.var_matchMode.value
        
        for i,item in enumerate(['point','orient','point/orient']):
            if i == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(p=uiMenu,collection = uiRC,
                        label=item,
                        c = cgmGen.Callback(uiFunc_change_matchMode,i),
                        rb = _rb) 
            
        #>>> Match pivot ================================================================================    
        uiMenu = mc.menuItem(p=uiMatch, l='Pivot', subMenu=True)    
        uiRC = mc.radioMenuItemCollection() 
        _v = self.var_matchModePivot.value
        
        for i,item in enumerate(['rp','sp','boundingbox']):
            if i == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(p=uiMenu,collection = uiRC,
                        label=item,
                        c = cgmGen.Callback(self.var_matchModePivot.setValue,i),
                        rb = _rb)         
    except Exception,err:
        log.error("|{0}| failed to load. err: {1}".format(_str_section,err)) 
        
def uiRadialMenu_root(self,parent,direction = None):
    """
    
    """
    _r = mc.menuItem(parent=parent,subMenu = True,
                     l = 'Locinator',
                     rp = direction)  
    
  
    #---------------------------------------------------------------------------
    
    #>>>Loc ==============================================================================================    
    uiRadial_create(self,_r,'N')
    
    #>>>Bake ==============================================================================================
    mc.menuItem(parent=_r,
                en = self._b_sel,
                l = 'Bake Range Frames',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'each','Bake',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'frames','timeMode':'slider'}),                                                                                      
                rp = 'NW')
    
    _bakeRange = mc.menuItem(parent=_r,subMenu = True,
                             en = self._b_sel,
                             l = 'Bake Range Keys',
                             rp = 'W')  
    mc.menuItem(parent=_bakeRange,
                l = 'of Loc',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'each','Bake',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'loc','timeMode':'slider'}),                
                rp = 'NW')  
    mc.menuItem(parent=_bakeRange,
                 l = 'of Source',
                 c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'each','Bake',False,
                                     **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'source','timeMode':'slider'}),                  
                 rp = 'SW')       
    mc.menuItem(parent=_bakeRange,
                l = 'of Both',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'each','Bake',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'both','timeMode':'slider'}),                 
                rp = 'W')     
    
    mc.menuItem(parent=_r,
                en = self._b_sel,
                l = 'Bake Timeline Frames',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'each','Bake',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'frames','timeMode':'scene'}),                                                                                      
                rp = 'NE')
        
    _bakeTime = mc.menuItem(parent=_r,subMenu = True,
                en = self._b_sel,
                l = 'Bake Timeline Keys',
                rp = 'E')
    mc.menuItem(parent=_bakeTime,
                    l = 'of Loc',
                    c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'each','Bake',False,
                                        **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'loc','timeMode':'scene'}),                
                    rp = 'NE')  
    mc.menuItem(parent=_bakeTime,
                l = 'of Both',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'each','Bake',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'both','timeMode':'scene'}),                                 
                rp = 'E')     
    mc.menuItem(parent=_bakeTime,
                 l = 'of Source',
                 c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'each','Bake',False,
                                     **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'source','timeMode':'scene'}),                                                                                                       
                 rp = 'SE')     

    #>>>Utils ==============================================================================================
    mc.menuItem(parent=_r,
                l = 'Match',
                en=self._b_sel,
                #c = cgmGen.Callback(buttonAction,raySnap_start(_sel)),                    
                c = cgmGen.Callback(MMCONTEXT.func_process, update_obj, self._l_sel,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'targetPivot':self.var_matchModePivot.value}),                                                                      
                rp = 'S')         
    
    _utils = mc.menuItem(parent=_r,subMenu = True,
                         l = 'Utils',
                         rp = 'SE')  
    
    mc.menuItem(parent=_utils,
                l = 'Tag first as match Target',
                en=self._b_sel,
                rp = 'SE') 
    mc.menuItem(parent=_utils,
                l = 'Clear match Target data',
                en=self._b_sel,
                rp = 'S')     
    mc.menuItem(parent=_utils,
                l = 'Report',
                en=self._b_sel,
                c = cgmGen.Callback(MMCONTEXT.func_process, get_objDat, self._l_sel,'each',True,**{'report':True}),                                                                                      
                rp = 'E')  
    mc.menuItem(parent=_utils,
                l = 'Select Source Targets',
                en=self._b_sel,
                rp = 'NE')
    mc.menuItem(parent=_utils,
                l = 'Get Help',
                rp = 'N')       
    
    




