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
            loftShapes=True):
    _str_func = 'dat_get'
    log.debug(log_start(_str_func))
    
    _str_block = mBlock.mNode
    ml_handles = None
    
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
        
    #Form Handles and shapes -----------------------------------------------------------    
    if formHandles: 
        log.info(log_sub(_str_func,'FormHandles...'))
        ml_handles = get_handles(ml_handles)
        
        dat_form = data['handles']['form']
        
        for i, mObj in enumerate(ml_handles):
            mObj.translate = dat_form[i]['t']
            mObj.rotate = dat_form[i]['r']
            
            mObj.scaleX = dat_form[i]['s'][0]
            mObj.scaleY = dat_form[i]['s'][1]
            try:mObj.scaleZ = dat_form[i]['s'][2]
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
                    mObj.translate = dat_loft[i][ii]['t']
                    mObj.rotate = dat_loft[i][ii]['r']
                    mObj.scale = dat_loft[i][ii]['s']
                
                if loftShapes:
                    shapes_set(mObj, dat_shapes[i][ii])
                    #_d['shapes'][i][ii] = shapes_set(mObj)['os']
            
        
        
    if loftShapes:
        log.info(log_sub(_str_func,'loftShapes...'))
            
            
def dat_get(mBlock=None):
    _str_func = 'dat_get'
    log.debug(log_start(_str_func))
    
    _str_block = mBlock.mNode
    
    #Check state. must be form state
    if mBlock.blockState < 1:
        raise ValueError,"Must be in form state"
    
    
    #Form count
    _res = {}
    
    #Settings ... ---------------------------------------------------------------------------
    _d = {}
    _res['settings'] = _d
    
    for a in ['loftSetup','loftShape','numShapers','numSubShapers','shapersAim']:
        try:
            if ATTR.get_type(_str_block, a) == 'enum':
                _d[a] = ATTR.get_enumValueString(_str_block, a)
            else:
                _d[a] = ATTR.get(_str_block, a)
        except:pass
    
    #datLists
    for a in ['loftList']:
        if ATTR.datList_exists(_str_block,a):
            _d[a] = ATTR.datList_get(_str_block,a,enum=1)
            
    #FormHandles ... ---------------------------------------------------------------------------
    _d = {}
    _d['form'] = []
    _d['loft'] = {}
    _d['shapes'] = {}
    
    _res['handles'] = _d
    
    ml_handles = mBlock.msgList_get('formHandles')
    
    
    def getCVS(mObj):
        _obj = mObj.mNode
        _res = {}
        
        _l_shapes_source = mc.listRelatives(_obj,shapes=True,fullPath=True)

        for i,s in enumerate(_l_shapes_source):
            _l_ep_source = mc.ls("{0}.cv[*]".format(s),flatten = True)
            for i,ep in enumerate(_l_ep_source):
                _pos = POS.get(ep,space='os')
            
    def get(mObj):
        d = {#'p':mObj.p_position,
                #'o':mObj.p_orient,
                'r':mObj.rotate,
                't':mObj.translate,
                's':mObj.scale}
        
        return d
    
    for i, mObj in enumerate(ml_handles):
        _d['form'].append( get(mObj))
        _d['loft'][i] = []
        _d['shapes'][i] = {}
        
        mLoftCurve = mObj.getMessageAsMeta('loftCurve')
        
        ml_loft = []
        if mLoftCurve:
            ml_loft.append(mLoftCurve)
        
        ml_subShapers = mObj.msgList_get('subShapers')
        if ml_subShapers:
            ml_loft.extend(ml_subShapers)
            
        for ii,mObj in enumerate(ml_loft):
            _d['loft'][i].append(get(mObj))
            _d['shapes'][i][ii] = shapes_get(mObj)

    #pprint.pprint(_res)
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
    