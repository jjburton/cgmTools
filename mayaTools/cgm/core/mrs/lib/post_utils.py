"""
------------------------------------------
cgm.core.mrs.lib.post_utils
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
# From Python =============================================================
import copy
import re
import pprint
import time
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel    

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import cgm.core.cgm_General as cgmGEN
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.rig.general_utils as CORERIGGEN
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core import cgm_RigMeta as cgmRigMeta
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.lib.locator_utils as LOC
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.position_utils as POS
import cgm.core.rig.joint_utils as JOINT
import cgm.core.rig.ik_utils as IK
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.lib.shapeCaster as SHAPECASTER
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.cgm_RigMeta as cgmRIGMETA


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.09122018'

log_start = cgmGEN.log_start

def skin_mesh(mMesh,ml_joints,**kws):
    try:
        _str_func = 'skin_mesh'
        log_start(_str_func)
        l_joints = [mObj.mNode for mObj in ml_joints]
        _mesh = mMesh.mNode
        
        try:
            kws_heat = copy.copy(kws)
            _defaults = {'heatmapFalloff' : 1,
                         'maximumInfluences' : 2,
                         'normalizeWeights' : 1, 
                         'dropoffRate':7}
            for k,v in _defaults.iteritems():
                if kws_heat.get(k) is None:
                    kws_heat[k]=vars
                    
            skin = mc.skinCluster (l_joints,
                                   _mesh,
                                   tsb=True,
                                   bm=2,
                                   wd=0,
                                   **kws)
        except Exception,err:
            log.warning("|{0}| >> heat map fail | {1}".format(_str_func,err))
            skin = mc.skinCluster (l_joints,
                                   mMesh.mNode,
                                   tsb=True,
                                   bm=0,
                                   maximumInfluences = 2,
                                   wd=0,
                                   normalizeWeights = 1,dropoffRate=10)
            """ """
        skin = mc.rename(skin,'{0}_skinCluster'.format(mMesh.p_nameBase))    
      
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

    

def backup(self,ml_handles = None):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        if not ml_handles:
            raise ValueError,"{0} | ml_handles required".format(_str_func)        
      
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
    
d_attrs = {'twist':{'d':'rz', '+d':1.0, '-d':-1.0, '+':50, '-':-50},
           'side':{'d':'ry', '+d':1.0, '-d':-1.0, '+':25, '-':-25},
           'roll':{'d':'rx', '+d':1.0, '-d':-1.0, '+':70, '-':-30},}

def SDK_wip(ml = [], matchType = False,
            d_attrs = d_attrs):
    _str_func = 'siblingSDK_wip'
    log.info(cgmGEN.logString_start(_str_func))
    
    if not ml:
        ml = cgmMeta.asMeta(sl=1)
    else:
        ml = cgmMeta.asMeta(ml)
        
    
    
    #mParent -----------------------------------------------------------------------------
    mParent = ml[0].moduleParent
    mParentSettings = mParent.rigNull.settings
    
    #pprint.pprint([mParent,mParentSettings])
    _settings = mParentSettings.mNode

    #Siblings get ------------------------------------------------------------------------
    #mSiblings = mTarget.atUtils('siblings_get',excludeSelf=False, matchType = matchType)
    mSiblings = ml
    
    md = {}
    d_int = {}
    
    #Need to figure a way to get the order...
    for i,mSib in enumerate(mSiblings):
        log.info(cgmGEN.logString_start(_str_func, mSib.__repr__()))
        
        _d = {}
        
        ml_fk = mSib.atUtils('controls_get','fk')
        if not ml_fk:
            log.warning('missing fk. Skippping...')
            continue
        
        
        if 'thumb' not in mSib.mNode:
            ml_fk = ml_fk[1:]
            
        
        
        _d['fk'] = ml_fk
        ml_sdk = []
        
        str_part = mSib.get_partNameBase()

        
        for ii,mFK in enumerate(ml_fk):
            mSDK = mFK.getMessageAsMeta('sdkGroup')
            if not mSDK:
                mSDK =  mFK.doGroup(True,True,asMeta=True,typeModifier = 'sdk')            
            ml_sdk.append(mSDK)
            
            if not d_int.get(ii):
                d_int[ii] = []
            
            d_int[ii].append(mSDK)
            
        _d['sdk'] = ml_sdk
        
        md[mSib] = _d
        
    #pprint.pprint(md)
    #pprint.pprint(d_int)
    #return
    
    for a,d in d_attrs.iteritems():
        log.info("{0} | ...".format(a))
        
        for i,mSib in enumerate(mSiblings):
            d2 = md[mSib]
            
            _aDriver = "{0}_{1}".format(a,i)
            #_aDriver = "{0}_{1}".format(str_part,a)
            if not mParentSettings.hasAttr(_aDriver):
                ATTR.add(_settings, _aDriver, attrType='float', keyable = True)            
            
            for mSDK in d2.get('sdk'):
                

                mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = 0, value = 0)
                
                #+ ------------------------------------------------------------------
                pos_v = d.get('+')
                pos_d = d.get('+d', 1.0)
                
                if pos_v:
                    mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = pos_d, value = pos_v)
                
                
                #- ----------------------------------------------------------
                neg_v = d.get('-')
                neg_d = d.get('-d', -1.0)
                    
                if neg_v:
                    mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = neg_d, value = neg_v)        
     
    




def siblingSDK_wip(mTarget = 'L_ring_limb_part',matchType = False,
                   d_attrs = d_attrs):
    _str_func = 'siblingSDK_wip'
    log.info(cgmGEN.logString_start(_str_func))
    
    if mTarget is None:
        mTarget = cgmMeta.asMeta(sl=1)
        if mTarget:mTarget = mTarget[0]
    else:
        mTarget = cgmMeta.asMeta(mTarget)
        
    #mParent -----------------------------------------------------------------------------
    mParent = mTarget.moduleParent
    mParentSettings = mParent.rigNull.settings
    
    #pprint.pprint([mParent,mParentSettings])
    _settings = mParentSettings.mNode

    #Siblings get ------------------------------------------------------------------------
    mSiblings = mTarget.atUtils('siblings_get',excludeSelf=False, matchType = matchType)
    md = {}
    #Need to figure a way to get the order...
    for i,mSib in enumerate(mSiblings):
        log.info(cgmGEN.logString_start(_str_func, mSib.__repr__()))
        
        _d = {}
        
        ml_fk = mSib.atUtils('controls_get','fk')
        if not ml_fk:
            log.warning('missing fk. Skippping...')
            continue
        
        
        if 'thumb' not in mSib.mNode:
            ml_fk = ml_fk[1:]
            
        
        
        _d['fk'] = ml_fk
        ml_sdk = []
        
        str_part = mSib.get_partNameBase()

        
        for mFK in ml_fk:
            mSDK = mFK.getMessageAsMeta('sdkGroup')
            if not mSDK:
                mSDK =  mFK.doGroup(True,True,asMeta=True,typeModifier = 'sdk')            
            ml_sdk.append(mSDK)
            
            

        for a,d in d_attrs.iteritems():
            log.info("{0} | ...".format(a))
            
            _aDriver = "{0}_{1}".format(a,i)
            #_aDriver = "{0}_{1}".format(str_part,a)
            if not mParentSettings.hasAttr(_aDriver):
                ATTR.add(_settings, _aDriver, attrType='float', keyable = True)
            
            
            for mSDK in ml_sdk:
                mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = 0, value = 0)
                
                #+ ------------------------------------------------------------------
                pos_v = d.get('+')
                pos_d = d.get('+d', 1.0)
                
                if pos_v:
                    mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = pos_d, value = pos_v)
                
                
                #- ----------------------------------------------------------
                neg_v = d.get('-')
                neg_d = d.get('-d', -1.0)
                    
                if neg_v:
                    mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = neg_d, value = neg_v)        
 
            
        _d['sdk'] = ml_sdk
        md[mSib] = _d
        
