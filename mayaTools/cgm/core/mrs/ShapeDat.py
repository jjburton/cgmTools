"""
skinDat
Josh Burton 
www.cgmonks.com

Core skinning data handler for cgm going forward.

Storing joint positions and vert positions so at some point can implement a method
to apply a skin without a reference object in scene if geo or joint counts don't match

Currently only regular skin clusters are storing...

Features...
- Skin data gather
- Read/write skin data to a readable config file
- Apply skinning data to geo of different vert count
- 

Thanks to Alex Widener for some ideas on how to set things up.

"""
__MAYALOCAL = 'CGMPROJECT'


# From Python =============================================================
import copy
import os
import pprint
import getpass
import json

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

#import maya.OpenMaya as OM
#import maya.OpenMayaAnim as OMA

# From Red9 =============================================================
#from Red9.core import Red9_Meta as r9Meta
#import Red9.core.Red9_CoreUtils as r9Core

#import Red9.packages.configobj as configobj
#import Red9.startup.setup as r9Setup    

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.lib import position_utils as POS

#import cgm.core.classes.GuiFactory as cgmUI
#reload(cgmUI)
#import cgm.core.cgmPy.path_Utils as PATHS
#import cgm.core.lib.path_utils as COREPATHS
#reload(COREPATHS)
#import cgm.core.lib.math_utils as COREMATH
#import cgm.core.lib.string_utils as CORESTRINGS
#import cgm.core.lib.shared_data as CORESHARE
#import cgm.core.tools.lib.project_utils as PU
#import cgm.core.lib.mayaSettings_utils as MAYASET
#import cgm.core.mrs.lib.scene_utils as SCENEUTILS
import cgm.core.lib.attribute_utils as ATTR
#from cgm.core.mrs.lib import general_utils as BLOCKGEN
#from cgm.core.lib import math_utils as MATH
#from cgm.core.lib import transform_utils as TRANS
#from cgm.core.lib import distance_utils as DIST

log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start


class data(object):
    '''
    Class to handle blockShape data.
    '''    
    
    def __init__(self, mBlock = None, filepath = None, **kws):
        """

        """
        _str_func = 'data.__buffer__'
        log.debug(log_start(_str_func))
        
        self.str_filepath = None
        self.data = {}
        self.mBlock = None
        
        
    def get(self, mBlock = None):
        _str_func = 'data.get'
        log.debug(log_start(_str_func))
    
    
    def set(self, mBlock = None):
        _str_func = 'data.set'
        log.debug(log_start(_str_func))
        
        


def dat_set(mBlock,data,
            settings = True,
            formHandles = True,
            loftHandles = True,
            loftShapes=True,
            loftHandleMode = 'local',
            loops=2):
    _str_func = 'dat_get'
    log.debug(log_start(_str_func))
    
    _str_block = mBlock.mNode
    ml_handles = None
    
    #First part of block reset to get/load data------------------------------------------------------
    pos = mBlock.p_position
    orient = mBlock.p_orient
    
    mBlock.p_position = 0,0,0
    mBlock.p_orient = 0,0,0
    
    def get_loftShapes(ml_handles):
        _res = {}
        
        for i,mObj in enumerate(ml_handles):
            ml_loft = []            
            _res[i] = ml_loft
            
            mLoftCurve = mObj.getMessageAsMeta('loftCurve')
            
            if mLoftCurve:
                ml_loft.append(mLoftCurve)
            
            ml_subShapers = mObj.msgList_get('subShapers')
            if ml_subShapers:
                ml_loft.extend(ml_subShapers)
        
        return _res
        
    def get_handles(ml_handles):
        if ml_handles:
            log.info("Found...")
            return ml_handles
        
        ml_handles = mBlock.msgList_get('formHandles')
        return ml_handles
    
    if settings:
        log.info(log_sub(_str_func,'Settings...'))
        
        for a,v in data['settings'].iteritems():
            
            if a in l_enumLists:
                ATTR.datList_connect(_str_block,a,v,enum=1)
            elif a in l_datLists:
                ATTR.datList_connect(_str_block,a,v)
            else:
                ATTR.set(_str_block, a, v)
            

        if mBlock.blockState < 1:
            mBlock.p_blockState = 1
            
        
        
    #Form Handles and shapes -----------------------------------------------------------    
    if formHandles: 
        log.info(log_sub(_str_func,'FormHandles...'))
        ml_handles = get_handles(ml_handles)
        
        if mBlock in ml_handles:
            raise ValueError,"mBlock cannot be in handles"
        
        pprint.pprint(ml_handles)
        
        dat_form = data['handles']['form']
        
        for ii in range(loops):
            for i, mObj in enumerate(ml_handles):
                
                #mObj.translate = dat_form[i]['trans']
                #mObj.rotate = dat_form[i]['rot']
                mObj.p_position = dat_form[i]['pos']
                mObj.p_orient = dat_form[i]['orient']
                
                mObj.scaleX = dat_form[i]['scale'][0]
                mObj.scaleY = dat_form[i]['scale'][1]
                try:mObj.scaleZ = dat_form[i]['scale'][2]
                except:pass
        
    #loft handles and shapes -----------------------------------------------------------
    if loftHandles or loftShapes:
        log.info(log_sub(_str_func,'loftHandles...'))
        if not ml_handles:
            ml_handles = get_handles(ml_handles)
            
        dat_loft = data['handles']['loft']
        dat_shapes = data['handles']['shapes']
        
        md_loftShapes = get_loftShapes(ml_handles)
        
        for i,mObj in enumerate(ml_handles):
            ml_loft = md_loftShapes[i]
            
            for ii,mObj in enumerate(ml_loft):
                
                if loftHandles:
                    if loftHandleMode == 'local':
                        mObj.translate = dat_loft[i][ii]['trans']
                        mObj.rotate = dat_loft[i][ii]['rot']                        
                    else:
                        mObj.p_position = dat_loft[i][ii]['pos']
                        mObj.p_orient = dat_loft[i][ii]['orient']                    
                        
                    #mObj.p_position = dat_loft[i][ii]['pos']
                    mObj.scale = dat_loft[i][ii]['scale']
                
                if loftShapes:
                    shapes_set(mObj, dat_shapes[i][ii])
                    #_d['shapes'][i][ii] = shapes_set(mObj)['os']
            
        
        
    if loftShapes:
        log.info(log_sub(_str_func,'loftShapes...'))
        
    #Restore our block...-----------------------------------------------------------------
    mBlock.p_position = pos
    mBlock.p_orient = orient         
            
l_dataAttrs = ['blockType','addLeverBase', 'addLeverEnd']
l_enumLists = ['loftList']
l_datLists = ['numSubShapers']

def dat_get(mBlock=None):
    _str_func = 'dat_get'
    log.debug(log_start(_str_func))
    
    _str_block = mBlock.mNode
    
    #Check state. must be form state
    if mBlock.blockState < 1:
        raise ValueError,"Must be in form state"
    
    #First part of block reset to get/load data------------------------------------------------------
    pos = mBlock.p_position
    orient = mBlock.p_orient
    
    mBlock.p_position = 0,0,0
    mBlock.p_orient = 0,0,0

    
    def get_attr(obj,a,d = {}):
        try:
            if a in l_enumLists:
                if ATTR.datList_exists(_str_block,a):
                    _d[a] = ATTR.datList_get(_str_block,a,enum=1)
            elif a in l_datLists:
                if ATTR.datList_exists(_str_block,a):
                    _d[a] = ATTR.datList_get(_str_block,a)                
            elif ATTR.get_type(obj, a) == 'enum':
                d[a] = ATTR.get_enumValueString(_str_block, a)
            else:
                d[a] = ATTR.get(_str_block, a)
        except:pass        
    
    #Form count
    _res = {}
    
    #Settings ... ---------------------------------------------------------------------------
    _d = {}
    _res['settings'] = _d
    
    for a in ['loftSetup','loftShape','numShapers','numSubShapers','shapersAim','shapeDirection','loftList']:
        get_attr(_str_block,a,_d)
    
            
    #Dat ... ---------------------------------------------------------------------------
    _d = {}
    _res['base'] = _d
    
    for a in l_dataAttrs:
        get_attr(_str_block,a,_d)

            
    #FormHandles ... ---------------------------------------------------------------------------
    _d = {}
    _d['form'] = []
    _d['loft'] = []
    _d['shapes'] = []
    
    _res['handles'] = _d
    
    ml_handles = mBlock.msgList_get('formHandles')
    pprint.pprint(ml_handles)
    
    def getCVS(mObj):
        _obj = mObj.mNode
        _res = {}
        
        _l_shapes_source = mc.listRelatives(_obj,shapes=True,fullPath=True)

        for i,s in enumerate(_l_shapes_source):
            _l_ep_source = mc.ls("{0}.cv[*]".format(s),flatten = True)
            for i,ep in enumerate(_l_ep_source):
                _pos = POS.get(ep,space='os')
            
    def get(mObj):
        d = {'pos':mObj.p_position,
             'orient':mObj.p_orient,
             'rot':mObj.rotate,
             'trans':mObj.translate,
             'scale':mObj.scale}
        return d
    
    for i, mObj in enumerate(ml_handles):
        _d['form'].append( get(mObj))
        _l_shapes = []
        _l_loft = []
        
        mLoftCurve = mObj.getMessageAsMeta('loftCurve')
        
        ml_loft = []
        if mLoftCurve:
            ml_loft.append(mLoftCurve)
        
        ml_subShapers = mObj.msgList_get('subShapers')
        if ml_subShapers:
            ml_loft.extend(ml_subShapers)
            
        for ii,mObj in enumerate(ml_loft):
            _l_loft.append( get(mObj))
            _l_shapes.append( shapes_get(mObj))
            
        _d['loft'].append(_l_loft)
        _d['shapes'].append(_l_shapes)

    #pprint.pprint(_res)
    
    #Restore our block...-----------------------------------------------------------------
    mBlock.p_position = pos
    mBlock.p_orient = orient      
    return _res
    
    
def shapes_get(mObj, mode = 'os'):
    _str_func = 'shapes_get'
    log.debug(log_start(_str_func))
        
    _obj = mObj.mNode
    _res = {}
    _l_shapes_source = mc.listRelatives(_obj,shapes=True,fullPath=True)

    for i,s in enumerate(_l_shapes_source):
        _l_ep_source = mc.ls("{0}.cv[*]".format(s),flatten = True)
        
        #Object Space
        if mode in ['os','all']:
            if not _res.get('os'):
                _res['os'] = []
                
            _d = []
            _res['os'].append(_d)
            for i,ep in enumerate(_l_ep_source):
                _d.append(POS.get(ep,space='os'))
        
        #WorldSpace
        if mode in ['ws','all']:
            if not _res.get('ws'):
                _res['ws'] = []        
            _d = []
            _res['ws'].append(_d)
            for i,ep in enumerate(_l_ep_source):
                _d.append(POS.get(ep,space='ws'))        
            
    #pprint.pprint(_res)
    return _res

def shapes_set(mObj, dat, mode = 'os'):
    _str_func = 'shapes_set'
    log.debug(log_start(_str_func))
    
    _dat = dat[mode]
    _obj = mObj.mNode
    _l_shapes_source = mc.listRelatives(_obj,shapes=True,fullPath=True)
    
    if len(_l_shapes_source) != len(_dat):
        raise ValueError,"Len of source shape ({0}) != dat ({1})".format(len(_l_shapes_source),len(_dat)) 
    
    for i,s in enumerate(_l_shapes_source):
        _l_ep_source = mc.ls("{0}.cv[*]".format(s),flatten = True)
        _l_pos = _dat[i]
        
        if len(_l_ep_source) != len(_l_pos):
            raise ValueError,"Len of source shape {} | ({}) != dat ({})".format(i,len(_l_ep_source),len(_l_pos))         
        
        for ii,ep in enumerate(_l_ep_source):
            POS.set(ep, _l_pos[ii],space='os')    
    