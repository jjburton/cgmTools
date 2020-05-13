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
__version__ = '2.0.05312017'


# From Python =============================================================
import copy
import re
import sys
import pprint
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGen
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import locator_utils as LOC
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
from cgm.core.lib import search_utils as SEARCH
import cgm.core.classes.GuiFactory as cgmUI
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT

import cgm.core.classes.GuiFactory as cgmUI
#reload(cgmUI)
cgmUI.initializeTemplates()
mUI = cgmUI.mUI

from cgm.lib import lists

def update_uiCall(mode = 'self'):
    _move = cgmMeta.cgmOptionVar('cgmVar_matchModeMove', defaultValue = 1).getValue()
    _rotate = cgmMeta.cgmOptionVar('cgmVar_matchModeRotate', defaultValue = 1).getValue()
    
    if mode == 'buffer':
        update_obj(obj=None, move=_move, rotate=_rotate, mode='buffer')
    else:
        MMCONTEXT.func_process(update_obj, None,'each','Match',False,**{'move':_move,'rotate':_rotate,'mode':mode})

def update_obj(obj = None, move = None, rotate = None, mode = 'self',**kws):
    """
    Updates an tagged loc or matches a tagged object
    
    :parameters:
        obj(str): Object to modify
        target(str): Target to match

    :returns
        success(bool)
    """     
    if move is None:
        move = cgmMeta.cgmOptionVar('cgmVar_matchModeMove', defaultValue = 1).value
    if rotate is None:
        rotate = cgmMeta.cgmOptionVar('cgmVar_matchModeRotate', defaultValue = 1).value      
        
    def match(obj,move,rotate):
        _locMode = ATTR.get(obj,'cgmLocMode')
        if _locMode:
            log.debug("|{0}| >> loc mode. updating {1}".format(_str_func,NAMES.get_short(obj)))
            return LOC.update(obj)
        
        if ATTR.get(obj +'.cgmMatchTarget'):
            log.debug("|{0}| >> Match mode. Matching {1} | move: {2} | rotate: {3}".format(_str_func,NAMES.get_short(obj),move,rotate))
            return SNAP.matchTarget_snap(obj,move,rotate)
        else:
            _res = LOC.create(obj)
            log.info("|{0}| >> Match target created: {1}".format(_str_func,_res))        
            return _res
        log.warning("|{0}| >> Not updatable: {1}".format(_str_func,NAMES.get_short(obj)))    
        return False    
        
    _str_func = 'update_obj'
    log.debug("|{0}| >> obj {1} | move: {2} | rotate: {3} | mode: {4}".format(_str_func,obj,move,rotate,mode))
    
    if mode == 'buffer':
        _targets = cgmMeta.cgmOptionVar('cgmVar_locinatorTargetsBuffer').value or []
        if not _targets:
            log.error("|{0}| >> No buffer targets found".format(_str_func))   
            return False
        for t in _targets:
            log.info("|{0}| >> Buffer target: {1}".format(_str_func,t))               
            match(t,move,rotate)
        return True    
    
    if not obj:
        log.error("|{0}| >> No obj specified.".format(_str_func))           
        return False
    
    _obj = VALID.objString(obj, noneValid=False, calledFrom = __name__ + _str_func + ">> validate obj")
    _target = None
    
    if mode == 'self':
        return match(obj,move,rotate)    
    elif mode == 'source':
        source = ATTR.get_message(obj,'cgmLocSource')
        if not source:
            raise ValueError,"No source found: {0}.cgmLocSource".format(obj)
        log.debug("|{0}| >> source {1}".format(_str_func,NAMES.get_short(source)))
        SNAP.go(source[0],_obj,position=move,rotation=rotate)
    else:
        _target = ATTR.get_message(_obj,'cgmMatchTarget') or ATTR.get_message(_obj,'cgmLocSource')
        if _target:
            return match(_target[0],move,rotate)
        else:
            _res = LOC.create(obj)
            log.info("|{0}| >> Match target created: {1}".format(_str_func,_res))        
            return _res     
            

def get_objDat(obj=None, mode = 'self', report = False):
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
    
    if mode == 'self':
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
            if not _res['matchTarget']:
                log.error("|{0}| >> No matchTarget found on: {1}".format(_str_func,obj))        
                return {}
            _res['loc'] = _res['matchTarget'][0]
            _res['source'] = obj
    else:
        if mc.objExists(obj + '.cgmLocSource'):
            _res['updateType'] = 'source'
            _res['matchTarget'] = ATTR.get_message(obj, 'cgmLocSource','cgmMatchDat',0)
            if not _res['matchTarget']:
                log.error("|{0}| >> No matchTarget found on: {1}".format(_str_func,obj))        
                return {}
            _res['loc'] = obj
            _res['source'] = _res['matchTarget'][0]
        
    if not report:
        return _res
    
    log.info(cgmGen._str_hardLine)
    
    _res['objecType'] = VALID.get_mayaType(obj)
    
    cgmGen.print_dict(_res,"'{0}' Locinator data...".format(obj),_str_func)
    
    #log.info("Obj: '{0}' | updateType: '{1}' | objectType: {2}".format(obj,_res['updateType'],_res['objecType']))
    
    return _res
        

def bake_match(targets = None, move = True, rotate = True, boundingBox = False, pivot = 'rp',
               timeMode = 'slider',timeRange = None, keysMode = 'loc', keysDirection = 'all',
               matchMode = 'self',dynMode=None):
    """
    Updates an tagged loc or matches a tagged object
    
    :parameters:
        obj(str): Object to modify
        target(str): Target to match
        
        timeMode(str):
            :slider/range
            :scene
            :selected
            :custom
        keysMode(str)
            :loc
            :source
            :combine
            :frames -- bake every frame
            :twos
            :threes
        keysDirection(str):
            :all
            :forward
            :back
        timeRange(list) -- [0,111] for example
        matchMode - mode for update_obj call
            self
            source
    :returns
        success(bool)
    """     
    _str_func = 'bake_match'
    
    #log.info("|{0}| >> Not updatable: {1}".format(_str_func,NAMES.get_short(_obj)))  
    _targets = VALID.objStringList(l_args=targets,isTransform=True,noneValid=False,calledFrom=_str_func)
        
    if not _targets:raise ValueError,"|{0}| >> no targets.".format(_str_func)
    if not move and not rotate:raise ValueError,"|{0}| >> Move and rotate both False".format(_str_func)
    
    if dynMode is None:
        try:dynMode = cgmMeta.cgmOptionVar('cgmVar_dynMode').getValue()
        except:pass
        
    log.info("|{0}| >> Targets: {1}".format(_str_func,_targets))
    log.info("|{0}| >> move: {1} | rotate: {2} | boundingBox: {3}".format(_str_func,move,rotate,boundingBox))    
    log.info("|{0}| >> timeMode: {1} | keysMode: {2} | keysDirection: {3} | dynMode: {4}".format(_str_func,timeMode,keysMode,keysDirection,dynMode))
    
    _l_toDo = []
    _d_toDo = {}
    _d_keyDat = {}
    
    #>>>Validate ==============================================================================================  
    for o in _targets:
        _d = {}
        if matchMode == 'source':
            source = ATTR.get_message(o,'cgmLocSource')
            if not source:
                raise ValueError,"No source found: {0}.cgmLocSource".format(o)            
            _l_toDo.append(o)
            _d['loc'] = o
            _d['source'] = source[0]
            _d_toDo[o] = _d
        else:
            _d = get_objDat(o)
            if _d and _d.get('updateType'):
                _l_toDo.append(o)
                _d_toDo[o] = _d
            
    if not _l_toDo:
        log.error("|{0}| >> No updatable targets found in: {1}".format(_str_func,_targets))        
        return False
    
    #>>>Key data ==============================================================================================    
    _d_keyDat['currentTime'] = mc.currentTime(q=True)
    
    if timeMode in ['slider','range']:
        _d_keyDat['frameStart'] = mc.playbackOptions(q=True,min=True)
        _d_keyDat['frameEnd'] = mc.playbackOptions(q=True,max=True)
    elif timeMode == 'scene':
        _d_keyDat['frameStart'] = mc.playbackOptions(q=True,animationStartTime=True)
        _d_keyDat['frameEnd'] = mc.playbackOptions(q=True,animationEndTime=True)
    elif timeMode == 'selected':
        _tRes = SEARCH.get_time('selected')
        if not _tRes:
            log.error("|{0}| >> No time range selected".format(_str_func))                    
            return False
        _d_keyDat['frameStart'] = _tRes[0]
        _d_keyDat['frameEnd'] = _tRes[1]          
    elif timeMode == 'custom':
        _d_keyDat['frameStart'] = timeRange[0]
        _d_keyDat['frameEnd'] = timeRange[1]       
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
    
    _keysAll = None
    if keysMode == 'frames':
        _keysAll = range(_start,_end +1)
    elif keysMode == 'twos':
        _keysAll = []
        i = _start
        while i <= _end:
            _keysAll.append(i)
            i += 2
    elif keysMode == 'threes':
        _keysAll = []
        i = _start
        while i <= _end:
            _keysAll.append(i)
            i += 3   
            
    if keysDirection in ['forward','back'] and _keysAll:
        _keysDirection = []
        if keysDirection == 'forward':
            for k in _keysAll:
                if k > _d_keyDat['currentTime']:
                    _keysDirection.append(k)                     
        else:
            for k in _keysAll:
                if k < _d_keyDat['currentTime']:
                    _keysDirection.append(k)
        _keysAll = _keysDirection
        
        _start = _keysAll[0]
        _end = _keysAll[-1]

    if _keysAll:
        _keysToProcess = _keysAll
    

    #First for loop, gathers key data per object...
    for o in _l_toDo:
        log.info("|{0}| >> Processing: '{1}' | keysMode: {2}".format(_str_func,o,keysMode))
        _d = _d_toDo[o]
        
        #Gather target key data...
        if not _keysAll:
            if keysMode == 'loc':
                _keys = SEARCH.get_key_indices_from( SEARCH.get_transform( _d['loc']),mode = keysDirection)
            elif keysMode == 'source':
                _keys = SEARCH.get_key_indices_from( SEARCH.get_transform( _d['source']),mode = keysDirection)
            elif keysMode in ['combine','both']:
                _source = SEARCH.get_key_indices_from( SEARCH.get_transform( _d['loc']),mode = keysDirection)
                _loc = SEARCH.get_key_indices_from( SEARCH.get_transform( _d['source']),mode= keysDirection)
                
                _keys = _source + _loc
                _keys = lists.returnListNoDuplicates(_keys)
            elif keysMode == 'frames':
                _keys = range(_start,_end +1)
            else:raise ValueError,"|{0}| >> Unknown keysMode: {1}".format(_str_func,keysMode)
        
            _l_cull = []
            for k in _keys:
                if k < _d_keyDat['frameStart'] or k > _d_keyDat['frameEnd']:
                    log.info("|{0}| >> Removing key from list: {1}".format(_str_func,k))                
                else:
                    _l_cull.append(k)
                    
                if timeRange is not None:
                    if k < timeRange[0] or k > timeRange[1]:
                        log.info("|{0}| >> Key not in time range({2}). Removing: {1}".format(_str_func,k,timeRange))                
                    else:
                        _l_cull.append(k)
                        
            keys = _l_cull
                    
            if not _keys:
                log.error("|{0}| >> No keys found for: '{1}'".format(_str_func,o))
                break            
            
            _d_keysOfTarget[o] = _keys
            _keysToProcess.extend(_keys)  
            log.info("|{0}| >> Keys: {1}".format(_str_func,_keys))            
        else: _d_keysOfTarget[o] = _keysAll
        
        
        #Clear keys in range
        if matchMode in ['source']:
            mc.cutKey(_d['source'],animation = 'objects', time=(_start,_end+ 1),at= _attrs)
        else:
            mc.cutKey(o,animation = 'objects', time=(_start,_end+ 1),at= _attrs)
            
    #pprint.pprint(_d)
    #return 
    #Second for loop processes our keys so we can do it in one go...
    _keysToProcess = lists.returnListNoDuplicates(_keysToProcess)
    #log.info(_keysToProcess)
    
    if not _keysToProcess:
        log.error("|{0}| >> No keys to process. Check settings.".format(_str_func))
        return False
    #return #...keys test...

    #Process 
    _progressBar = cgmUI.doStartMayaProgressBar(len(_keysToProcess),"Processing...")
    _autoKey = mc.autoKeyframe(q=True,state=True)
    if _autoKey:mc.autoKeyframe(state=False)
    if not dynMode:
        mc.refresh(su=1)
    else:
        _start = mc.playbackOptions(q=True,min=True)
        _keysToProcessFull = range(int(_start), int(max(_keysToProcess))+1)
        #for k in _keysToProcess:
        #    if k not in _keysToProcessFull:
        #        _keysToProcessFull.append(k)
        #_keysToProcessFull.sort()
        
        _keysToProcess = _keysToProcessFull
        
    _len = len(_keysToProcess)
    try:
        for i,f in enumerate(_keysToProcess):
            mc.currentTime(f)
            for o in _l_toDo:
                _keys = _d_keysOfTarget.get(o,[])
                if f in _keys:
                    log.debug("|{0}| >> Baking: {1} | {2} | {3}".format(_str_func,f,o,_attrs))
                    if _progressBar:
                        
                        if mc.progressBar(_progressBar, query=True, isCancelled=True ):
                            log.warning('Bake cancelled!')
                            return False
                        
                        mc.progressBar(_progressBar, edit=True, status = ("{0} On frame {1} for '{2}'".format(_str_func,f,o)), step=1, maxValue = _len)                    
                
                    if matchMode == 'source':
                        try:update_obj(o,move,rotate,mode=matchMode)
                        except Exception,err:log.error(err)
                        mc.setKeyframe(_d_toDo[o]['source'],time = f, at = _attrs)
                    else:
                        try:update_obj(o,move,rotate)
                        except Exception,err:log.error(err)
                        mc.setKeyframe(o,time = f, at = _attrs)
    except Exception,err:
        log.error(err)
    finally:
        if not dynMode:mc.refresh(su=0)
        cgmUI.doEndMayaProgressBar(_progressBar)
    mc.currentTime(_d_keyDat['currentTime'])
    if _autoKey:mc.autoKeyframe(state=True)
    mc.select(_targets)
    return True
        
        
def uiRadial_create(self,parent,direction = None):
    #>>>Loc ==============================================================================================    
        _l = mc.menuItem(parent=parent,subMenu=True,
                     l = 'Loc',
                     rp = direction)
    
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
                    en = self._b_sel,                    
                    c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, self._l_sel,'all','midPointLoc',False,**{'mode':'midPoint'}),                                                                      
                    rp = "SW")   
        mc.menuItem(parent=_l,
                    l = 'Attach Point',
                    en = self._b_sel,
                    c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, self._l_sel,'each','attachPoint',False,**{'mode':'attachPoint'}),
                    rp = "E")         
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
                    c = lambda *a:LOC.create(mode = 'rayCast'),
                    #c = lambda *a:self.rayCast_create('locator',False),
                    rp = "SE")       

def uiSetupOptionVars(self):
    self.var_matchModeMove = cgmMeta.cgmOptionVar('cgmVar_matchModeMove', defaultValue = 1)
    self.var_matchModeRotate = cgmMeta.cgmOptionVar('cgmVar_matchModeRotate', defaultValue = 1)
    self.var_dynMode = cgmMeta.cgmOptionVar('cgmVar_dynMode', defaultValue = 0)
    
    #self.var_matchModePivot = cgmMeta.cgmOptionVar('cgmVar_matchModePivot', defaultValue = 0)
    self.var_matchMode = cgmMeta.cgmOptionVar('cgmVar_matchMode', defaultValue = 2)
    self.var_locinatorTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_locinatorTargetsBuffer',defaultValue = [''])
    self.var_keysMode = cgmMeta.cgmOptionVar('cgmVar_locinatorKeysMode',defaultValue = 'loc') 
    
def uiFunc_change_matchMode(self,arg):
    self.var_matchMode.value = arg    
    if arg == 0:
        self.var_matchModeMove.value = 1
        self.var_matchModeRotate.value = 0
    elif arg == 1:
        self.var_matchModeMove.value = 0
        self.var_matchModeRotate.value = 1
    elif arg == 2:
        self.var_matchModeMove.value = 1
        self.var_matchModeRotate.value = 1
    else:
        self.var_matchMode.value = 2        
        raise ValueError,"|{0}| >> Unknown matchMode: {1}".format(sys._getframe().f_code.co_name,arg)
    
        
def uiOptionMenu_matchMode(self, parent):
    try:#>>> KeyMode ================================================================================
        _str_section = 'match mode'
        uiMatch = mc.menuItem(p=parent, l='Match Mode ', subMenu=True)
        
        #uiMenu = mc.menuItem(p=uiMatch, l='Mode ', subMenu=True)    
        uiRC = mc.radioMenuItemCollection()
        _v = self.var_matchMode.value
        
        for i,item in enumerate(['point','orient','point/orient']):
            if i == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(p=uiMatch,collection = uiRC,
                        label=item,
                        c = cgmGen.Callback(uiFunc_change_matchMode,self,i),
                        rb = _rb)
            
        #Dyn mode...
        uiDyn = mc.menuItem(p=parent, l='Dyn Mode ', subMenu=True)        
        uiRC = mc.radioMenuItemCollection()
        _v = self.var_dynMode.value
        
        for i in range(2):
            if i == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(p=uiDyn,collection = uiRC,
                        label=bool(i),
                        c = cgmGen.Callback(self.var_dynMode.setValue,i),
                        rb = _rb)
            
        #self.var_dynMode = cgmMeta.cgmOptionVar('cgmVar_dynMode', defaultValue = 0)
        """    
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
                        rb = _rb)         """
    except Exception,err:
        log.error("|{0}| failed to load. err: {1}".format(_str_section,err)) 
        
        
def uiBuffer_control(self, parent):
    try:#>>> KeyMode ================================================================================
        _str_section = 'locinator buffer control'
            
        uiMenu = mc.menuItem(p=parent, l='Match', subMenu=True)    
        mc.menuItem(p=uiMenu, l="Define",
                    c= lambda *a: self.varBuffer_define(self.var_locinatorTargetsBuffer))
    
        mc.menuItem(p=uiMenu, l="Add Selected",
                         c= lambda *a: self.varBuffer_add(self.var_locinatorTargetsBuffer))
    
        mc.menuItem(p=uiMenu, l="Remove Selected",
                         c= lambda *a: self.varBuffer_remove(self.var_locinatorTargetsBuffer))
    
        mc.menuItem(p=uiMenu,l='----------------',en=False)
        mc.menuItem(p=uiMenu, l="Report",
                    c= lambda *a: self.var_locinatorTargetsBuffer.report())        
        mc.menuItem(p=uiMenu, l="Select Members",
                    c= lambda *a: self.var_locinatorTargetsBuffer.select())
        mc.menuItem(p=uiMenu, l="Clear",
                    c= lambda *a: self.var_locinatorTargetsBuffer.clear())       
    except Exception,err:
        log.error("|{0}| failed to load. err: {1}".format(_str_section,err)) 
        
def uiRadialMenu_root(self,parent,direction = None, callback = None):
    if callback == None:
        callback = cgmGen.Callback
        
    _r = mc.menuItem(parent=parent,subMenu = True,
                     l = 'Locinator',
                     rp = direction)  
    
  
    #---------------------------------------------------------------------------
    
    #>>>Loc ==============================================================================================    
    uiRadial_create(self,_r,'N')
    
    mc.menuItem(parent=_r,
                l = 'UI',
                c = lambda *a:mc.evalDeferred(ui,lp=True),                                                                                      
                rp = 'SW')       
    
    #>>>Bake ==============================================================================================
    _bakeFrames = mc.menuItem(parent=_r,subMenu = True,
                              en = self._b_sel,
                              l = 'Bake Range',                                
                              rp = 'NE')
    _bakeDirection = mc.menuItem(parent=_r,subMenu = True,
                               en = self._b_sel,
                               l = 'Bake Direction',                                
                               rp = 'E')      
    _bakeForward = mc.menuItem(parent=_bakeDirection,subMenu = True,
                               en = self._b_sel,
                               l = 'Forward',                                
                               rp = 'NE')    
    _bakeBack = mc.menuItem(parent=_bakeDirection,subMenu = True,
                            en = self._b_sel,
                            l = 'Back',                                
                            rp = 'SE')    
    
    
    
    
    
    mc.menuItem(parent=_bakeFrames,
                l = 'Selection',
                c = callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range',False,
                             **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':self.var_keysMode.value,'timeMode':'selected'}),                                                                                      
                rp = 'NE')      
    mc.menuItem(parent=_bakeFrames,
                l = 'Slider',
                c = callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range',False,
                             **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':self.var_keysMode.value,'timeMode':'slider'}),                                                                                      
                rp = 'E') 
    mc.menuItem(parent=_bakeFrames,
                l = 'Scene',
                c = callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range',False,
                             **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':self.var_keysMode.value,'timeMode':'scene'}),                                                                                      
                rp = 'SE')   
    
    
    
  
    mc.menuItem(parent=_bakeForward,
                l = 'Slider',
                c = callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range',False,
                             **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':self.var_keysMode.value,'timeMode':'slider','keysDirection':'forward'}),                                                                                      
                rp = 'NE') 
    mc.menuItem(parent=_bakeForward,
                l = 'Scene',
                c = callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range',False,
                             **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':self.var_keysMode.value,'timeMode':'scene','keysDirection':'forward'}),                                                                                      
                rp = 'SE')   
    
    
    
    mc.menuItem(parent=_bakeBack,
                l = 'Slider',
                c = callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range',False,
                             **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':self.var_keysMode.value,'timeMode':'slider','keysDirection':'back'}),                                                                                      
                rp = 'NE') 
    mc.menuItem(parent=_bakeBack,
                l = 'Scene',
                c = callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range',False,
                             **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':self.var_keysMode.value,'timeMode':'scene','keysDirection':'back'}),                                                                                      
                rp = 'SE') 
    
    
    
    #>>>Bake Options ==============================================================================================
    _bakeOptions = mc.menuItem(parent=_r,subMenu = True,
                               l = 'Bake By...?',                                
                               rp = 'SE')  
    
    _optionVar_keysMode_value = self.var_keysMode.value
    #self._l_pivotModes = ['rotatePivot','scalePivot','boundingBox']
    _l_toBuild = [{'l':'loc',
                   'rp':'NW',
                   'c':callback(self.var_keysMode.setValue,'loc')},
                  {'l':'source',
                   'rp':'N',
                   'c':callback(self.var_keysMode.setValue,'source')},
                  {'l':'combine',
                   'rp':'NE',
                   'c':callback(self.var_keysMode.setValue,'combine')},
                  {'l':'frames',
                   'rp':'SW',
                   'c':callback(self.var_keysMode.setValue,'frames')},
                  {'l':'twos',
                   'rp':'S',
                   'c':callback(self.var_keysMode.setValue,'twos')},
                  {'l':'threes',
                   'rp':'SE',
                   'c':callback(self.var_keysMode.setValue,'threes')},]                      
    for i,m in enumerate(_l_toBuild):
        _l = m['l']
        if _l == _optionVar_keysMode_value:
            _l = _l + '--(Active)'

        mc.menuItem(parent=_bakeOptions,
                    en = True,
                    l = _l,
                    c = m['c'],
                    rp = m['rp'])    

    #>>>Utils ==============================================================================================
    _match= mc.menuItem(parent=_r,subMenu = True,
                        l = 'Match',
                        rp = 'S')         
    mc.menuItem(parent=_match,
                l = 'Self',
                #c = cgmGen.Callback(buttonAction,raySnap_start(_sel)),  
                en=self._b_sel,                
                c = callback(MMCONTEXT.func_process, update_obj, self._l_sel,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'self'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                rp = 'S')     
    mc.menuItem(parent=_match,
                 l = 'Target',
                 #c = cgmGen.Callback(buttonAction,raySnap_start(_sel)),   
                 en=self._b_sel,                 
                 c = callback(MMCONTEXT.func_process, update_obj, self._l_sel,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'target'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                 rp = 'SW')      
    mc.menuItem(parent=_match,
                 l = 'Buffer',
                 #c = cgmGen.Callback(buttonAction,raySnap_start(_sel)),                    
                 c = callback(update_obj,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'buffer'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                 rp = 'SE')   
    
    
    _utils = mc.menuItem(parent=_r,subMenu = True,
                         l = 'Utils',
                         rp = 'W')  
    
    mc.menuItem(parent=_utils,
                l = 'Tag to last',
                en=self._b_sel,
                c = callback(MMCONTEXT.func_process, SNAP.matchTarget_set, self._l_sel,'eachToLast','Tag cgmMatchTarget',False),                                                                                      
                rp = 'SW') 
    mc.menuItem(parent=_utils,
                l = 'Clear match data',
                en=self._b_sel,
                c = callback(MMCONTEXT.func_process, SNAP.matchTarget_clear, self._l_sel,'each','Clear cgmMatch data',True),                                                                                                      
                rp = 'S')     
    mc.menuItem(parent=_utils,
                l = 'Report',
                en=self._b_sel,
                c = callback(MMCONTEXT.func_process, get_objDat, self._l_sel,'each','Report',True,**{'report':True}),                                                                                      
                rp = 'W')   
    #mc.menuItem(parent=_utils,
                #l = 'Select Source Targets',
                #en=self._b_sel,
                #rp = 'NE')
    mc.menuItem(parent=_utils,
                l = 'Get Help',
                c='import webbrowser;webbrowser.open("http://docs.cgmonks.com/locinator.html");',                        
                rp = 'N')       
    
    

def uiRadialMenu_rootOLD(self,parent,direction = None):
    _r = mc.menuItem(parent=parent,subMenu = True,
                     l = 'Locinator',
                     rp = direction)  
    
  
    #---------------------------------------------------------------------------
    
    #>>>Loc ==============================================================================================    
    uiRadial_create(self,_r,'N')
    
    #>>>Bake ==============================================================================================
    _bakeFrames = mc.menuItem(parent=_r,subMenu = True,
                              en = self._b_sel,
                              l = 'Bake Range Frames',                                
                              rp = 'NW')
    mc.menuItem(parent=_bakeFrames,
                l = 'All',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range',False,
                                                  **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'frames','timeMode':'slider'}),                                                                                      
                rp = 'N')      
    mc.menuItem(parent=_bakeFrames,
                l = 'Twos',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range by twos',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'twos','timeMode':'slider'}),                                                                                      
                rp = 'NW')      
    mc.menuItem(parent=_bakeFrames,
                l = 'Threes',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range by threes',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'threes','timeMode':'slider'}),                                                                                      
                rp = 'W')      
    
    _bakeRange = mc.menuItem(parent=_r,subMenu = True,
                             en = self._b_sel,
                             l = 'Bake Range Keys',
                             rp = 'W')  
    mc.menuItem(parent=_bakeRange,
                l = 'of Loc',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'loc','timeMode':'slider'}),                
                rp = 'NW')  
    mc.menuItem(parent=_bakeRange,
                 l = 'of Source',
                 c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake',False,
                                     **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'source','timeMode':'slider'}),                  
                 rp = 'SW')       
    mc.menuItem(parent=_bakeRange,
                l = 'of Both',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'both','timeMode':'slider'}),                 
                rp = 'W')     
    
    
    
    _bakeTimeline = mc.menuItem(parent=_r,subMenu = True,
                                en = self._b_sel,
                                l = 'Bake Timeline Frames',
                                rp = 'NE')
    mc.menuItem(parent=_bakeTimeline,
                l = 'All',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range',False,
                                                  **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'frames','timeMode':'scene'}),                                                                                      
                rp = 'N')      
    mc.menuItem(parent=_bakeTimeline,
                l = 'Twos',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range by twos',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'twos','timeMode':'scene'}),                                                                                      
                rp = 'NE')      
    mc.menuItem(parent=_bakeTimeline,
                l = 'Threes',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake range by threes',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'threes','timeMode':'scene'}),                                                                                      
                rp = 'E')      
    
    
    
        
    _bakeTime = mc.menuItem(parent=_r,subMenu = True,
                en = self._b_sel,
                l = 'Bake Timeline Keys',
                rp = 'E')
    mc.menuItem(parent=_bakeTime,
                    l = 'of Loc',
                    c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake',False,
                                        **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'loc','timeMode':'scene'}),                
                    rp = 'NE')  
    mc.menuItem(parent=_bakeTime,
                l = 'of Both',
                c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake',False,
                                    **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'both','timeMode':'scene'}),                                 
                rp = 'E')     
    mc.menuItem(parent=_bakeTime,
                 l = 'of Source',
                 c = cgmGen.Callback(MMCONTEXT.func_process, bake_match, self._l_sel,'all','Bake',False,
                                     **{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'boundingBox':False,'keysMode':'source','timeMode':'scene'}),                                                                                                       
                 rp = 'SE')     

    #>>>Utils ==============================================================================================
    _match= mc.menuItem(parent=_r,subMenu = True,
                        l = 'Match',
                        rp = 'S')         
    mc.menuItem(parent=_match,
                l = 'Self',
                #c = cgmGen.Callback(buttonAction,raySnap_start(_sel)),  
                en=self._b_sel,                
                c = cgmGen.Callback(MMCONTEXT.func_process, update_obj, self._l_sel,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'self'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                rp = 'S')     
    mc.menuItem(parent=_match,
                 l = 'Target',
                 #c = cgmGen.Callback(buttonAction,raySnap_start(_sel)),   
                 en=self._b_sel,                 
                 c = cgmGen.Callback(MMCONTEXT.func_process, update_obj, self._l_sel,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'target'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                 rp = 'SW')      
    mc.menuItem(parent=_match,
                 l = 'Buffer',
                 #c = cgmGen.Callback(buttonAction,raySnap_start(_sel)),                    
                 c = cgmGen.Callback(update_obj,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'buffer'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                 rp = 'SE')   
    
    
    _utils = mc.menuItem(parent=_r,subMenu = True,
                         l = 'Utils',
                         rp = 'SE')  
    
    mc.menuItem(parent=_utils,
                l = 'Tag to last as cgmMatchTarget',
                en=self._b_sel,
                c = cgmGen.Callback(MMCONTEXT.func_process, SNAP.matchTarget_set, self._l_sel,'eachToLast','Tag cgmMatchTarget',False),                                                                                      
                rp = 'SE') 
    mc.menuItem(parent=_utils,
                l = 'Clear match Target data',
                en=self._b_sel,
                c = cgmGen.Callback(MMCONTEXT.func_process, SNAP.matchTarget_clear, self._l_sel,'each','Clear cgmMatch data',True),                                                                                                      
                rp = 'S')     
    mc.menuItem(parent=_utils,
                l = 'Report',
                en=self._b_sel,
                c = cgmGen.Callback(MMCONTEXT.func_process, get_objDat, self._l_sel,'each','Report',True,**{'report':True}),                                                                                      
                rp = 'E') 
    mc.menuItem(parent=_utils,
                l = 'UI',
                c = cgmGen.Callback(ui),                                                                                      
                rp = 'NE')     
    #mc.menuItem(parent=_utils,
                #l = 'Select Source Targets',
                #en=self._b_sel,
                #rp = 'NE')
    mc.menuItem(parent=_utils,
                l = 'Get Help',
                c='import webbrowser;webbrowser.open("http://docs.cgmonks.com/locinator.html");',                        
                rp = 'N')       
    
    
class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmLocinator_ui'    
    WINDOW_TITLE = 'cgmLocinator - {0}'.format(__version__)
    DEFAULT_SIZE = 180, 275
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created

    _checkBoxKeys = ['shared','default','user','others']
    
    def insert_init(self,*args,**kws):
            if kws:log.debug("kws: %s"%str(kws))
            if args:log.debug("args: %s"%str(args))
            log.info(self.__call__(q=True, title=True))
    
            self.__version__ = __version__
            self.__toolName__ = 'cgmLocinator'		
            #self.l_allowedDockAreas = []
            self.WINDOW_TITLE = ui.WINDOW_TITLE
            self.DEFAULT_SIZE = ui.DEFAULT_SIZE
            
            self.currentFrameOnly = True
            self.startFrame = ''
            self.endFrame = ''
            self.startFrameField = ''
            self.endFrameField = ''
            self.forceBoundingBoxState = False
            self.forceEveryFrame = False
            self.showHelp = False
            self.helpBlurbs = []
            self.oldGenBlurbs = []
        
            self.showTimeSubMenu = False
            self.timeSubMenu = []            
            

            uiSetupOptionVars(self)
            self.create_guiOptionVar('bakeFrameCollapse',defaultValue = 0) 
            
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        
        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')            
        ui_tabs = mUI.MelTabLayout( _MainForm,w=180,ut='cgmUITemplate' )
        uiTab_update = mUI.MelColumnLayout(ui_tabs)
        uiTab_create = mUI.MelColumnLayout( ui_tabs )
        
        for i,tab in enumerate(['Update','Create']):
            ui_tabs.setLabel(i,tab)
            
        self.buildTab_create(uiTab_create)
        self.buildTab_update(uiTab_update)
        
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)            
        _MainForm(edit = True,
                  af = [(ui_tabs,"top",0),
                        (ui_tabs,"left",0),
                        (ui_tabs,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(ui_tabs,"bottom",2,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])          
    def build_menus(self):
        #pmc
        self.uiMenu_options = mUI.MelMenu( l='Options', pmc = cgmGen.Callback(self.buildMenu_options) )
        self.uiMenu_Buffer = mUI.MelMenu( l='Buffer', pmc = cgmGen.Callback(self.buildMenu_buffer))
        self.uiMenu_help = mUI.MelMenu( l='Help', pmc = cgmGen.Callback(self.buildMenu_help))        
        #pass#...don't want em  
    #def setup_Variables(self):pas
    
    
    def buildMenu_buffer(self):
        self.uiMenu_Buffer.clear()  
        
        uiMenu = self.uiMenu_Buffer   
        mc.menuItem(p=uiMenu, l="Define",
                    c= lambda *a: cgmUI.varBuffer_define(self,self.var_locinatorTargetsBuffer))
    
        mc.menuItem(p=uiMenu, l="Add Selected",
                         c= lambda *a: cgmUI.varBuffer_add(self,self.var_locinatorTargetsBuffer))
    
        mc.menuItem(p=uiMenu, l="Remove Selected",
                         c= lambda *a: cgmUI.varBuffer_remove(self,self.var_locinatorTargetsBuffer))
    
        mc.menuItem(p=uiMenu,l='----------------',en=False)
        mc.menuItem(p=uiMenu, l="Report",
                    c= lambda *a: self.var_locinatorTargetsBuffer.report())        
        mc.menuItem(p=uiMenu, l="Select Members",
                    c= lambda *a: self.var_locinatorTargetsBuffer.select())
        mc.menuItem(p=uiMenu, l="Clear",
                    c= lambda *a: self.var_locinatorTargetsBuffer.clear())       
      
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()

        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Report Loc Data',
                    c = cgmGen.Callback(MMCONTEXT.func_process, get_objDat, None,'each','Report',True,**{'report':True}),                                                                                      
                    rp = 'E')  
      
        mc.menuItem(p=self.uiMenu_help,l='----------------',en=False)
        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("http://docs.cgmonks.com/locinator.html");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )        
    

        
    def buildMenu_options( self, *args):
        self.uiMenu_options.clear()   
        _menu = self.uiMenu_options
        
        uiOptionMenu_matchMode(self, _menu)
        
        
        #>>> 
        uiMenu_keysModes = mc.menuItem(parent = _menu,subMenu = True,
                                       l='Bake Keys')
        
        uiRC = mc.radioMenuItemCollection(parent = uiMenu_keysModes)
        _v = self.var_keysMode.value
    
        _d_annos = {'loc':'Use keys of the loc',
                    'source':'Use keys of the source',
                    'combine':'Combine keys of the loc and source',
                    'frames':'Within specified range, every frame',
                    'twos':'Within specified range, on twos',
                    'threes':'Within specified range, on threes'}
        
        """
        timeMode(str):
            :slider/range
            :scene
            :custom
        keysMode(str)
            :loc
            :source
            :combine
            :frames -- bake every frame
            :twos
            :threes
        """
    
        for i,item in enumerate(['loc','source','combine','frames','twos','threes']):
            if item == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(parent=uiMenu_keysModes,collection = uiRC,
                        label=item,
                        ann=_d_annos.get(item,'Fill out the dict!'),                        
                        c = cgmGen.Callback(self.var_keysMode.setValue,item),                                  
                        rb = _rb) 
    

        mc.menuItem(p=_menu,l='----------------',en=False)
        
        mc.menuItem(parent=_menu,
                    l = 'Tag Selected',
                    ann = 'Tag to last as cgmMatchTarget',
                    c = cgmGen.Callback(MMCONTEXT.func_process, SNAP.matchTarget_set, None,'eachToLast','Tag cgmMatchTarget',False),                                                                                      
                    rp = 'SE') 
        mc.menuItem(parent=_menu,
                    l = 'Clear Selected',
                    ann = 'Clear match Target data from selected objects',
                    c = cgmGen.Callback(MMCONTEXT.func_process, SNAP.matchTarget_clear, None,'each','Clear cgmMatch data',True),                                                                                                      
                    rp = 'S')          
            
   
        
    def uiFunc_updateTimeRange(self,mode = 'slider'):
        _range = SEARCH.get_time(mode)
        if _range:
            self.uiFieldInt_start(edit = True, value = _range[0])
            self.uiFieldInt_end(edit = True, value = _range[1])            
             
        
        
        
    def buildTab_update(self,parent):
        _column = mUI.MelColumnLayout(parent,useTemplate = 'cgmUITemplate')
        
        self.buildRow_update(_column)

        mc.setParent(_column)    
        
        cgmUI.add_LineBreak()
        
        _bake_frame = mUI.MelFrameLayout(_column,label = 'Bake',vis=True,
                                         collapse=self.var_bakeFrameCollapse.value,
                                         collapsable=True,
                                         enable=True,
                                         useTemplate = 'cgmUIHeaderTemplate',
                                         expandCommand = lambda:self.var_bakeFrameCollapse.setValue(0),
                                         collapseCommand = lambda:self.var_bakeFrameCollapse.setValue(1)
                                         )	
        _frame_inside = mUI.MelColumnLayout(_bake_frame,useTemplate = 'cgmUISubTemplate')
        
        
        #>>>Update Row ---------------------------------------------------------------------------------------
        mc.setParent(_frame_inside)
        _row_timeSet = mUI.MelHLayout(_frame_inside,ut='cgmUISubTemplate',padding = 1)
    
        cgmUI.add_Button(_row_timeSet,'Slider',
                         cgmGen.Callback(self.uiFunc_updateTimeRange,'slider'),                         
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         _d_annotations.get('sliderRange','fix sliderRange'))
        cgmUI.add_Button(_row_timeSet,'Sel',
                                 cgmGen.Callback(self.uiFunc_updateTimeRange,'selected'),                         
                                 #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                                 _d_annotations.get('selectedRange','fix selectedRange'))        
    
        cgmUI.add_Button(_row_timeSet,'Scene',
                         cgmGen.Callback(self.uiFunc_updateTimeRange,'scene'),                         
                         _d_annotations.get('sceneRange','fix sceneRange'))
  
        
        _row_timeSet.layout()          
        
        # TimeInput Row ----------------------------------------------------------------------------------
        _row_time = mUI.MelHSingleStretchLayout(_frame_inside,ut='cgmUISubTemplate')
        self.timeSubMenu.append( _row_time )
        mUI.MelSpacer(_row_time)
        mUI.MelLabel(_row_time,l='start')
    
        self.uiFieldInt_start = mUI.MelIntField(_row_time,'cgmLocWinStartFrameField',
                                                width = 40)
        _row_time.setStretchWidget( mUI.MelSpacer(_row_time) )
        mUI.MelLabel(_row_time,l='end')
    
        self.uiFieldInt_end = mUI.MelIntField(_row_time,'cgmLocWinEndFrameField',
                                              width = 40)
        
        self.uiFunc_updateTimeRange()
    
        mUI.MelSpacer(_row_time)
        _row_time.layout()   
        
        
        #>>>Bake Mode --------------------------------------------------------------------------------------------        
        self.create_guiOptionVar('bakeMode',defaultValue = 0)       
    
        _rc_keyMode = mUI.MelRadioCollection()
        
        _l_bakeModes = ['sel','buffer']
        
        #build our sub section options
        _row_bakeModes = mUI.MelHSingleStretchLayout(_frame_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelLabel(_row_bakeModes,l = 'Targets:')
        _row_bakeModes.setStretchWidget( mUI.MelSeparator(_row_bakeModes) )
    
        _on = self.var_bakeMode.value
    
        for i,item in enumerate(_l_bakeModes):
            if i == _on:_rb = True
            else:_rb = False
            _rc_keyMode.createButton(_row_bakeModes,label=_l_bakeModes[i],sl=_rb,
                                     onCommand = cgmGen.Callback(self.var_bakeMode.setValue,i))
            mUI.MelSpacer(_row_bakeModes,w=2)

        _row_bakeModes.layout()         
        

        #>>>Update Row ---------------------------------------------------------------------------------------
        
        mc.setParent(_frame_inside)
        cgmUI.add_LineSubBreak()
        
        _row_bake = mUI.MelHLayout(_frame_inside,ut='cgmUISubTemplate',padding = 1)
    
        cgmUI.add_Button(_row_bake,' <<<',
                         cgmGen.Callback(self.uiFunc_bake,'back'),                         
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         _d_annotations.get('<<<','fix'))
    
        cgmUI.add_Button(_row_bake,'All',
                         cgmGen.Callback(self.uiFunc_bake,'all'),                         
                         _d_annotations.get('All','fix'))
        
        
        cgmUI.add_Button(_row_bake,'>>>',
                         cgmGen.Callback(self.uiFunc_bake,'forward'),                         
                         _d_annotations.get('>>>','fix'))    
        
        _row_bake.layout()         
        
    def uiFunc_bake(self,mode='all'):
        _bakeMode = self.var_bakeMode.value
        if _bakeMode == 0:
            _targets = None
        else:
            _targets = self.var_locinatorTargetsBuffer.value
            if not _targets:
                log.error("Buffer is empty")
                return False
            
        MMCONTEXT.func_process(bake_match, _targets,'all','Bake',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,
                                                                          'boundingBox':False,'keysMode':self.var_keysMode.value,'keysDirection':mode,
                                                                          'timeMode':'custom','timeRange':[self.uiFieldInt_start(q=True, value = True),self.uiFieldInt_end(q=True, value = True)]})       
                                                                    

        
    def buildTab_create(self,parent):
        _column = mUI.MelColumnLayout(parent,useTemplate = 'cgmUITemplate')
            
        #>>>  Center Section
        cgmUI.add_Header('Create')        
        cgmUI.add_LineSubBreak()
        cgmUI.add_Button(_column,'Loc Me',
                        cgmGen.Callback(MMCONTEXT.func_process, LOC.create, None,'each'),
                        _d_annotations['me'])
        
        cgmUI.add_LineSubBreak()
        cgmUI.add_Button(_column,'Mid point',
                         cgmGen.Callback(MMCONTEXT.func_process, LOC.create, None,'all','midPointLoc',False,**{'mode':'midPoint'}),                                                                      
                         _d_annotations['mid'])          
        
        cgmUI.add_LineSubBreak()
        cgmUI.add_Button(_column,'Attach point',
                         cgmGen.Callback(MMCONTEXT.func_process, LOC.create, None,'all','attachPoint',False,**{'mode':'attachPoint'}),                                                                      
                         _d_annotations['attach'])
        
        cgmUI.add_LineSubBreak()
        cgmUI.add_Button(_column,'Closest point',
                         cgmGen.Callback(MMCONTEXT.func_process, LOC.create, None,'all','closestPoint',False,**{'mode':'closestPoint'}),                                                                      
                         _d_annotations['closestPoint'])
        
        cgmUI.add_LineSubBreak()
        cgmUI.add_Button(_column,'Closest target',
                         cgmGen.Callback(MMCONTEXT.func_process, LOC.create, None,'all','closestTarget',False,**{'mode':'closestTarget'}),                                                                      
                         _d_annotations['closestTarget'])        
        
        
        cgmUI.add_LineSubBreak()
        cgmUI.add_Button(_column,'Raycast',
                         lambda *a:LOC.create(mode = 'rayCast'),                                                                      
                         _d_annotations['rayCast'])  
        
        
        cgmUI.add_LineBreak()
        
        self.buildRow_update(_column)
        
    def buildRow_update(self,parent):
        #>>>Update Row ---------------------------------------------------------------------------------------
        mc.setParent(parent)
        cgmUI.add_Header('Update')
        _row_update = mUI.MelHLayout(parent,ut='cgmUISubTemplate',padding = 1)
    
        cgmUI.add_Button(_row_update,' Self',
                         lambda *a:update_uiCall('self'),
                         #cgmGen.Callback(MMCONTEXT.func_process, update_obj, None,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'self'}),                         
                         _d_annotations.get('updateSelf','fix'))
    
        cgmUI.add_Button(_row_update,'Target',
                         lambda *a:update_uiCall('target'),
                         #cgmGen.Callback(MMCONTEXT.func_process, update_obj, None,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'target'}),                                                  
                         _d_annotations.get('updateTarget','fix'))
        
        
        cgmUI.add_Button(_row_update,'Buffer',
                         lambda *a:update_uiCall('buffer'),                         
                         #cgmGen.Callback(MMCONTEXT.func_process, update_obj, None,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'buffer'}),                                                                           
                         _d_annotations.get('updateBuffer','fix'))    
        
        _row_update.layout()        
        
        
        

_d_annotations = {'me':'Create a loc from selected objects',
                  'mid':'Create a loc at the bb midpoint of a single target or the mid point of multiple targets',
                  'closestPoint':'Create a loc at the closest point on the targets specified - curve, mesh, nurbs',
                  'closestTarget':'Create a loc at the closest target',
                  'rayCast':'Begin a clickMesh instance to cast a single locator in scene',
                  'updateSelf':'Update the selected objects',
                  'updateTarget':'Update the selected targets if possible',
                  'updateBuffer':'Update objects loaded to the buffer',
                  'sliderRange':' Push the slider range values to the int fields',
                  'selectedRange': 'Push the selected timeline range (if active)',
                  'sceneRange':'Push scene range values to the int fields',
                  '<<<':'Bake within a context of keys in range prior to the current time',
                  'All':'Bake within a context of the entire range of keys ',
                  '>>>':'Bake within a context of keys in range after the current time',
                  'attach':'Create a loc of the selected object AND start a clickMesh instance to setup an attach point on a mesh in scene'}



