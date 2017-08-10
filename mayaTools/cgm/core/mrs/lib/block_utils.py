"""
------------------------------------------
block: cgm.core.mrs.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

These are functions with self assumed to be a cgmRigBlock
================================================================
"""
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
log.setLevel(logging.DEBUG)
#========================================================================

import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as PUPPETMETA
from cgm.core import cgm_RigMeta as RIGMETA

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
reload(RIGGING)

from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.lib.transform_utils as TRANS

#=============================================================================================================
#>> define
#=============================================================================================================
def define(self):pass


#=============================================================================================================
#>> Template
#=============================================================================================================
def is_template(self):
    if not self.getMessage('templateNull'):
        return False
    return True

def templateDelete(self,msgLinks = []):
    _str_func = 'templateDelete'    
    log.info("|{0}| >> ...".format(_str_func))                            
    for link in msgLinks:
        if self.getMessage(link):
            log.info("|{0}| >> deleting link: {1}".format(_str_func,link))                        
            mc.delete(self.getMessage(link))
    return True

def templateNull_verify(self):
    if not self.getMessage('templateNull'):
        str_templateNull = RIGGING.create_at(self.mNode)
        templateNull = cgmMeta.validateObjArg(str_templateNull, mType = 'cgmObject',setClass = True)
        templateNull.connectParentNode(self, 'rigBlock','templateNull') 
        templateNull.doStore('cgmName', self.mNode)
        templateNull.doStore('cgmType','templateNull')
        templateNull.doName()
        templateNull.p_parent = self
        templateNull.setAttrFlags()
    else:
        templateNull = self.templateNull   
        
    return templateNull

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerigNull_verify(self):
    if not self.getMessage('prerigNull'):
        str_prerigNull = RIGGING.create_at(self.mNode)
        mPrerigNull = cgmMeta.validateObjArg(str_prerigNull, mType = 'cgmObject',setClass = True)
        mPrerigNull.connectParentNode(self, 'rigBlock','prerigNull') 
        mPrerigNull.doStore('cgmName', self.mNode)
        mPrerigNull.doStore('cgmType','prerigNull')
        mPrerigNull.doName()
        mPrerigNull.p_parent = self
        mPrerigNull.setAttrFlags()
    else:
        mPrerigNull = self.prerigNull    
        
    return mPrerigNull

def prerig_simple(self):
    _str_func = 'prerig'
    
    _short = self.p_nameShort
    _size = self.baseSize
    _sizeSub = _size * .2
    #_baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
    _side = 'center'
    
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
    
    log.info("|{0}| >> [{1}] | baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))     
        
    self._factory.module_verify()  
    
    #Create preRig Null  ==================================================================================
    mPrerigNull = prerigNull_verify(self)   
    
    return True

def prerig_delete(self ,msgLists = [], templateHandles = True):
    _str_func = 'prerig_delete'    
    self.moduleTarget.delete()
    self.prerigNull.delete()
    
    if templateHandles:
        for mHandle in [self] + self.msgList_get('templateHandles'):
            try:mHandle.jointHelper.delete()
            except:pass    
    
    for l in msgLists:
        _buffer = self.msgList_get(l,asMeta=False)
        if not _buffer:
            log.info("|{0}| >> Missing msgList: {1}".format(_str_func,l))  
        else:
            mc.delete(_buffer)
    
    return True   

def is_prerig(self, msgLinks = [], msgLists = [] ):
    _str_func = 'is_prerig'
    _l_missing = []

    _d_links = {self : ['moduleTarget','prerigNull']}

    for l in msgLinks:
        if not self.getMessage(l):
            _l_missing.append(self.p_nameBase + '.' + l)
            
    for l in msgLists:
        if not self.msgList_exists(l):
            _l_missing.append(self.p_nameBase + '.[msgList]' + l)

    if _l_missing:
        log.info("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.info("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True

#=============================================================================================================
#>> Rig
#=============================================================================================================


#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def skeleton_connectToParent(self):
    _short = self.mNode
    _str_func = 'skeleton_connectToParent ( {0} )'.format(_short)
    
    mModule = self.moduleTarget
    
    l_moduleJoints = mModule.rigNull.msgList_get('moduleJoints',asMeta = False)

    if not mModule.getMessage('moduleParent'):
        log.info("|{0}| >> No moduleParent. Checking puppet".format(_str_func))  
        TRANS.parent_set(l_moduleJoints[0], mModule.modulePuppet.masterNull.skeletonGroup.mNode)
    else:
        mParent = self.moduleParent #Link
        if mParent.isSkeletonized():#>> If we have a module parent
            #>> If we have another anchor
            if self.moduleType == 'eyelids':
                str_targetObj = mParent.rigNull.msgList_get('moduleJoints',asMeta = False)[0]
                for jnt in l_moduleJoints:
                    TRANS.parent_set(jnt,str_targetObj)
            else:
                l_parentSkinJoints = mParent.rigNull.msgList_get('moduleJoints',asMeta = False)
                str_targetObj = distance.returnClosestObject(l_moduleJoints[0],l_parentSkinJoints)
                TRANS.parent_set(l_moduleJoints[0],str_targetObj)		
        else:
            log.info("|{0}| >> Module parent is not skeletonized".format(_str_func))  
            return False   
        
        
def skeleton_buildRigChain(self):
    _short = self.mNode
    _str_func = 'skeleton_buildRigChain ( {0} )'.format(_short)
    start = time.clock()	
    _mRigNull = self.moduleTarget.rigNull
    
    #Get our segment joints
    l_rigJointsExist = _mRigNull.msgList_get('rigJoints',asMeta = False, cull = True)
    ml_skinJoints = _mRigNull.msgList_get('skinJoints')
    
    if l_rigJointsExist:
        log.info("|{0}| >> Deleting existing rig chain".format(_str_func))  
        mc.delete(l_rigJointsExist)

    l_rigJoints = mc.duplicate([i_jnt.mNode for i_jnt in _mRigNull.msgList_get('skinJoints')],po=True,ic=True,rc=True)
    ml_rigJoints = [cgmMeta.cgmObject(j) for j in l_rigJoints]


    for i,mJnt in enumerate(ml_rigJoints):
        mJnt.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
        l_rigJoints[i] = mJnt.mNode
        mJnt.connectChildNode(ml_skinJoints[i].mNode,'skinJoint','rigJoint')#Connect	    
        if mJnt.hasAttr('scaleJoint'):
            if mJnt.scaleJoint in ml_skinJoints:
                int_index = ml_skinJoints.index(mJnt.scaleJoint)
                mJnt.connectChildNode(l_rigJoints[int_index],'scaleJoint','sourceJoint')#Connect
        try:mJnt.delAttr('rigJoint')
        except:pass

    #Name loop
    ml_rigJoints[0].parent = False
    for mJnt in ml_rigJoints:
        mJnt.doName()	
        
    _mRigNull.msgList_connect('rigJoints',ml_rigJoints,'rigNull')#connect	
    log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	
    
    return ml_rigJoints

def skeleton_buildRigChain(self):
    _short = self.mNode
    _str_func = 'skeleton_buildRigChain [{0}]'.format(_short)
    start = time.clock()	
    _mRigNull = self.moduleTarget.rigNull
    
    #Get our segment joints
    l_rigJointsExist = _mRigNull.msgList_get('rigJoints',asMeta = False, cull = True)
    ml_skinJoints = _mRigNull.msgList_get('skinJoints')
    
    if l_rigJointsExist:
        log.info("|{0}| >> Deleting existing rig chain".format(_str_func))  
        mc.delete(l_rigJointsExist)

    l_rigJoints = mc.duplicate([i_jnt.mNode for i_jnt in _mRigNull.msgList_get('skinJoints')],po=True,ic=True,rc=True)
    ml_rigJoints = [cgmMeta.cgmObject(j) for j in l_rigJoints]


    for i,mJnt in enumerate(ml_rigJoints):
        mJnt.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
        l_rigJoints[i] = mJnt.mNode
        mJnt.connectChildNode(ml_skinJoints[i].mNode,'skinJoint','rigJoint')#Connect	    
        if mJnt.hasAttr('scaleJoint'):
            if mJnt.scaleJoint in ml_skinJoints:
                int_index = ml_skinJoints.index(mJnt.scaleJoint)
                mJnt.connectChildNode(l_rigJoints[int_index],'scaleJoint','sourceJoint')#Connect
        try:mJnt.delAttr('rigJoint')
        except:pass

    #Name loop
    ml_rigJoints[0].parent = False
    for mJnt in ml_rigJoints:
        mJnt.doName()	
        
    _mRigNull.msgList_connect('rigJoints',ml_rigJoints,'rigNull')#connect	
    log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	
    
    return ml_rigJoints

def skeleton_buildHandleChain(self,typeModifier = 'handle',connectNodesAs = False): 
    _short = self.mNode
    _str_func = 'skeleton_buildHandleChain [{0}]'.format(_short)
    start = time.clock()	
    
    _mModule = self.moduleTarget
    _mRigNull = self.moduleTarget.rigNull
    
    ml_handleJoints = _mModule.rig_getHandleJoints()
    ml_handleChain = []

    for i,mHandle in enumerate(ml_handleJoints):
        mNew = mHandle.doDuplicate()
        if ml_handleChain:mNew.parent = ml_handleChain[-1]#if we have data, parent to last
        else:mNew.parent = False
        mNew.addAttr('cgmTypeModifier',typeModifier,attrType='string',lock=True)
        mNew.doName()

        ml_handleChain.append(mNew)

    if connectNodesAs and type(connectNodesAs) in [str,unicode]:
        self.moduleTarget.rigNull.msgList_connect(connectNodesAs,ml_handleChain,'rigNull')#Push back

    log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)
    return ml_handleChain

def verify_dynSwitch(self):
    _short = self.mNode
    _str_func = 'skeleton_buildHandleChain [{0}]'.format(_short)
    _mRigNull = self.moduleTarget.rigNull
    
    if not _mRigNull.getMessage('dynSwitch'):
        mDynSwitch = RIGMETA.cgmDynamicSwitch(dynOwner=_mRigNull.mNode)
        log.debug("|{0}| >> Created dynSwitch: {1}".format(_str_func,mDynSwitch))        
    else:
        mDynSwitch = _mRigNull.dynSwitch 
        
    return mDynSwitch    
        

