"""
------------------------------------------
builder_utils: cgm.core.mrs.lib
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
__MAYALOCAL = 'BUILDERUTILS'

import random
import re
import copy
import time
import os
import pprint

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as PUPPETMETA
import cgm.core.cgm_RigMeta as cgmRIGMETA
import cgm.core.lib.geo_Utils as GEO
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as CORERIG
import cgm.core.lib.rigging_utils as CORERIG
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.lib.node_utils as NODES
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.lib.locator_utils as LOC
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.rig.general_utils as RIGGEN
import cgm.core.lib.surface_Utils as SURF
import cgm.core.lib.string_utils as STRING
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.list_utils as LISTS
import cgm.core.classes.NodeFactory as NodeF
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
from cgm.core.classes import GuiFactory as cgmUI
from cgm.core.cgmPy import os_Utils as cgmOS


class eyeLook(object):
    def __init__(self,dag=None):
        if dag:
            mDag = cgmMeta.asMeta(dag)
            if not mDag.getMayaAttr('cgmType') == 'eyeLookMain':
                raise ValueError,"Not a eyeLookMain tagged node: {0}".format(mDag)
            self.mDag = mDag
            
    @classmethod
    def helper_get(self):
        pass
            
    

def eyeLook_get(self,autoBuild=False):
    _str_func = 'eyeLook_get'
    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    mBlock = self.mBlock
    
    mModule = self.mModule
    mRigNull = self.mRigNull
    mPuppet = self.mPuppet

    try:return mModule.eyeLook
    except:pass
    try:return mi_module.moduleParent.eyeLook
    except:pass
    
    ml_puppetEyelooks = mPuppet.msgList_get('eyeLook')
    if ml_puppetEyelooks:
        if len(ml_puppetEyelooks) == 1 and ml_puppetEyelooks[0]:
            return ml_puppetEyelooks[0]
        else:
            raise StandardError,"More than one puppet eye look"
        
    if autoBuild:
        return eyeLook_verify(self)
    return False

#@cgmGEN.Timer
def eyeLook_verify(self):
    _str_func = 'eyeLook_verify'
    try:
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        mBlock = self.mBlock
        
        mModule = self.mModule
        mRigNull = self.mRigNull
        mPuppet = self.mPuppet
        mHandleFactory = mBlock.asHandleFactory()
        
        _eyeLook = eyeLook_get(self)
        if _eyeLook:
            log.debug("|{0}| >> Found existing eyeLook...".format(_str_func))                      
            return _eyeLook
        
        if mBlock.blockType not in ['eye']:
            raise ValueError,"blocktype must be eye. Found {0} | {1}".format(mBlock.blockType,mBlock)
        
        #Data... -----------------------------------------------------------------------
        log.debug("|{0}| >> Get data...".format(_str_func))
        #_size = mHandleFactory.get_axisBox_size(mBlock.getMessage('bbHelper'))
        
        try:
            _size = self.v_baseSize
            _sizeAvg = self.f_sizeAvg             
        except:
            _size = [mBlock.blockScale * v for v in mBlock.baseSize]
            _sizeAvg = MATH.average(_size)
        
        #Create shape... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Creating shape...".format(_str_func))
        mCrv = cgmMeta.asMeta( CURVES.create_fromName('arrow4Fat',
                                                      direction = 'z+',
                                                      size = _sizeAvg ,
                                                      absoluteSize=False),'cgmObject',setClass=True)
        mCrv.doSnapTo(mBlock.mNode,rotation=False)
        pos = mBlock.getPositionByAxisDistance('z+',
                                               _sizeAvg * 8)
        
        mCrv.p_position = 0,pos[1],pos[2]
        
        
        mBlockParent = mBlock.p_blockParent
        if mBlockParent:
            mCrv.doStore('cgmName',mBlockParent.cgmName + '_eyeLook')
            mBlockParent.asHandleFactory().color(mCrv.mNode)
        else:
            mCrv.doStore('cgmName','eyeLook')
            mHandleFactory.color(mCrv.mNode)
        
        mCrv.doName()
        

        #Register control... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Registering Control... ".format(_str_func))
        d_buffer = MODULECONTROL.register(mCrv,
                                          mirrorSide= 'center',
                                          mirrorAxis="translateX,rotateY,rotateZ",
                                          addSpacePivots = 2)
        
        mCrv = d_buffer['mObj']        
        
        
        #Dynparent... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Dynparent setup.. ".format(_str_func))
        ml_dynParents = copy.copy(self.ml_dynParentsAbove)
        mHead = False
        for mParent in ml_dynParents:
            log.debug("|{0}| >> mParent: {1}".format(_str_func,mParent))
            
            if mParent.getMayaAttr('cgmName') == 'head':
                log.debug("|{0}| >> found head_direct...".format(_str_func))
                mHead = mParent
                break
        if mHead:
            ml_dynParents.insert(0,mHead)
        #if mBlock.attachPoint == 'end':
        #ml_dynParents.reverse()
        
        ml_dynParents.extend(mCrv.msgList_get('spacePivots'))
        ml_dynParents.extend(copy.copy(self.ml_dynEndParents))
        
        ml_dynParents = LISTS.get_noDuplicates(ml_dynParents)
        mDynParent = cgmRIGMETA.cgmDynParentGroup(dynChild=mCrv,dynMode=0)
        
        for o in ml_dynParents:
            mDynParent.addDynParent(o)
        mDynParent.rebuild()
        
        #Connections... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Connections... ".format(_str_func))
        mModule.connectChildNode(mCrv,'eyeLook')
        mPuppet.msgList_append('eyeLook',mCrv,'puppet')
        
        if mBlockParent:
            log.debug("|{0}| >> Adding to blockParent...".format(_str_func))
            mModuleParent = mBlockParent.moduleTarget
            mModuleParent.connectChildNode(mCrv,'eyeLook')
            if mModuleParent.mClass == 'cgmRigModule':
                mBlockParentRigNull = mModuleParent.rigNull
                mBlockParentRigNull.msgList_append('controlsAll',mCrv)
                mBlockParentRigNull.moduleSet.append(mCrv)
                mRigNull.faceSet.append(mCrv)
                
                mCrv.connectParentNode(mBlockParentRigNull,'rigNull')
                
            else:
                mModuleParent.puppetSet.append(mCrv)
                mModuleParent.msgList_append('controlsAll',mCrv)
                mModuleParent.faceSet.append(mCrv)
                

        #Connections... -----------------------------------------------------------------------        
        log.debug("|{0}| >> Heirarchy... ".format(_str_func))
        mCrv.masterGroup.p_parent = self.mDeformNull
        
        for link in 'masterGroup','dynParentGroup':
            if mCrv.getMessage(link):
                mCrv.getMessageAsMeta(link).dagLock(True)
                
        mCrv.addAttr('cgmControlDat','','string')
        mCrv.cgmControlDat = {'tags':['ik']}                
        
        return mCrv
    
    except Exception,error:
        cgmGEN.cgmExceptCB(Exception,error,msg=vars())

   


    try:#moduleParent Stuff =======================================================
        if mi_moduleParent:
            try:
                for mCtrl in self.ml_controlsAll:
                    mi_parentRigNull.msgList_append('controlsAll',mCtrl)
            except Exception,error: raise Exception,"!Controls all connect!| %s"%error	    
            try:mi_parentRigNull.moduleSet.extend(self.ml_controlsAll)
            except Exception,error: raise Exception,"!Failed to set module objectSet! | %s"%error
    except Exception,error:raise Exception,"!Module Parent registration! | %s"%(error)	    

