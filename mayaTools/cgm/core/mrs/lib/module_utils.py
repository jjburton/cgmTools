"""
------------------------------------------
module_utils: cgm.core.mrs.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
import random
import re
import copy
import time
import os
import pprint
import sys
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
from cgm.core import cgm_RigMeta as RIGMETA

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import list_utils as LISTS

from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.lib.ml_tools.ml_resetChannels as ml_resetChannels

l_faceModules = ['eyebrow','eyelids','eyeball','mouthNose','simpleFace']

#=============================================================================================================
#>> Queries
#=============================================================================================================
def get_partName(self):
    _str_func = ' get_partName'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:#Quick select sets ================================================================
        return NAMETOOLS.returnRawGeneratedName(self.mNode, ignore = ['cgmType'])
    except Exception,err:cgmGEN.cgmException(Exception,err)

def get_dynSwitch(self):
    _str_func = ' get_dynSwitch'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        mRigNull = self.rigNull
        if mRigNull.getMessage('dynSwitch'):
            return mRigNull.dynSwitch
        
        mDynSwitch = RIGMETA.cgmDynamicSwitch(dynOwner=mRigNull.mNode)
        log.debug("|{0}| >> Created dynSwitch: {1}".format(_str_func,mDynSwitch))
        return mDynSwitch
    except Exception,err:cgmGEN.cgmException(Exception,err)

def mirror_getSideString(self):
    _str_func = ' mirror_getSideString'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        _str_direction = self.getMayaAttr('cgmDirection') 
        
        if _str_direction is not None and _str_direction.lower() in ['right','left']:
            return _str_direction.capitalize()
        else:return 'Centre'	           
    except Exception,err:cgmGEN.cgmException(Exception,err)


def get_settingsHandle(self):
    _str_func = ' get_settingsHandle'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        mRigNull = self.rigNull#Link
        try:
            return mRigNull.settings#fastest check
        except:pass
        
        if self.moduleType in l_faceModules:
            try:return self.moduleParent.rigNull.settings#fastest check
            except:log.debug("|{0}| >> No module parent settings...".format(_str_func))   
            try:return self.modulePuppet.masterControl.controlSettings#fastest check
            except:log.debug("|{0}| >> No masterControl parent settings...".format(_str_func))   
        
        log.debug("|{0}| >> No settings found".format(_str_func))   
    
        return False       
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
    
def moduleChildren_get(self,excludeSelf = True):
    _str_func = ' moduleChildren_getAll'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        ml_children = []
        ml_childrenCull = copy.copy(self.moduleChildren)
    
        cnt = 0
        while len(ml_childrenCull)>0 and cnt < 100:#While we still have a cull list
            cnt+=1                        
            if cnt == 99:
                raise StandardError,"Max count reached"
            for mChild in ml_childrenCull:
                if mChild not in ml_children:
                    ml_children.append(mChild)
                for i_subChild in mChild.moduleChildren:
                    ml_childrenCull.append(i_subChild)
                ml_childrenCull.remove(mChild) 
        
        if not excludeSelf:
            ml_children.append(self)
        return ml_children
    
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
    
#=============================================================================================================
#>> verify
#=============================================================================================================
def verify_objectSet(self):
    _str_func = ' verify_objectSet'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:#Quick select sets ================================================================
        mRigNull = self.rigNull
        if not mRigNull.getMessage('moduleSet'):#
            mSet = cgmMeta.cgmObjectSet(setType='animSet',qssState=True)
            mSet.connectParentNode(mRigNull.mNode,'rigNull','moduleSet')

        mSet = mRigNull.moduleSet
        mSet.doStore('cgmName',self.mNode)
        mSet.doName()

        if self.getMessage('modulePuppet'):
            mi_modulePuppet = self.modulePuppet
            if not mi_modulePuppet.getMessage('puppetSet'):
                mi_modulePuppet.verify_objectSet()
            self.modulePuppet.puppetSet.addObj(mSet.mNode)
    except Exception,err:cgmGEN.cgmException(Exception,err)

#=============================================================================================================
#>> Skeleton
#=============================================================================================================
__l_passThroughModules__ = ['simpleFace']

def is_skeletonized(self):
    _str_func = ' is_skeletonized'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        if self.moduleType in __l_passThroughModules__:
            log.debug("|{0}| >> pass through module".format(_str_func))
            return True
        
        l_moduleJoints = self.rigNull.msgList_get('moduleJoints',asMeta=False)
        if not l_moduleJoints:
            log.debug("|{0}| >> no joints found...".format(_str_func))
            return False  
        return True
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def rig_getSkinJoints(self,asMeta=True):
    _str_func = ' rig_getSkinJoints'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        ml_skinJoints = []
        ml_moduleJoints = self.rigNull.msgList_get('moduleJoints',asMeta = True, cull = True)
        int_lenMax = len(ml_moduleJoints)	    
        for i,mJnt in enumerate(ml_moduleJoints):
            ml_skinJoints.append(mJnt)
            for attr in BLOCKSHARE.__l_moduleJointSingleHooks__:
                str_attrBuffer = mJnt.getMessage(attr)
                if str_attrBuffer:
                    ml_skinJoints.append( cgmMeta.validateObjArg(str_attrBuffer) )
            for attr in BLOCKSHARE.__l_moduleJointMsgListHooks__:
                l_buffer = mJnt.msgList_get(attr,asMeta = True,cull = True)
        if asMeta:return ml_skinJoints
        if ml_skinJoints:
            return [obj.p_nameShort for obj in ml_skinJoints]	            

    except Exception,err:cgmGEN.cgmException(Exception,err)
    
#=============================================================================================================
#>> Rig
#=============================================================================================================


def is_rigged(self):
    _str_func = ' is_rigged'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        log.error("|{0}| >>  ||| FINISH THIS CALL ||| ".format(_str_func))
        
        if self.moduleType in __l_passThroughModules__:
            log.debug("|{0}| >> pass through module".format(_str_func))
            return True
    
        mRigNull = self.rigNull
        str_shortName = self.p_nameShort
    
        if mRigNull.getMayaAttr('ignoreRigCheck'):
            log.debug("|{0}| >> ignoreRigCheck found...".format(_str_func))
            return True
    
        if not is_skeletonized(self):
            log.debug("|{0}| >> not skeletonized...".format(_str_func))
            return False
        
        if not get_joints(self, rigJoints=True):
            log.debug("|{0}| >> no rigJoints..".format(_str_func))
            return False
        
        if not mRigNull.msgList_get('controlsAll'):
            log.debug("|{0}| >> no controlsAll..".format(_str_func))
            return False
    
        return True
        l_rigJoints = get_joints(self,rigJoints = True, asMeta=False)            
        l_skinJoints = get_joints(self,skinJoints = True, asMeta=False)
    
        if not l_skinJoints or not l_rigJoints:
            log.debug("|{0}| >> Necessary chains not found...".format(_str_func))
            mRigNull.version = ''#clear the version	
            return False
    
        #See if we can find any constraints on the rig Joints
        if self.moduleType.lower() in __l_faceModules__:
            log.warning("Need to find a better face rig joint test rather than constraints")	    
        else:
            b_foundConstraint = False
            for i,jnt in enumerate(l_rigJoints):
                if cgmMeta.cgmObject(jnt).getConstraintsTo():
                    b_foundConstraint = True
                    break
                elif i == (len(l_rigJoints) - 1) and not b_foundConstraint:
                    self.log_warning("No rig joints are constrained")	    
                    return False
    
        if len( l_skinJoints ) < len( l_rigJoints ):
            log.warning(" %s != %s. Not enough rig joints"%(len(l_skinJoints),len(l_rigJoints)))
            mRigNull.version = ''#clear the version        
            return False
    
        for attr in ['controlsAll']:
            if not mRigNull.msgList_get(attr,asMeta = False):
                log.warning("No data found on '%s'"%(attr))
                mRigNull.version = ''#clear the version            
                return False            
    except Exception,err:cgmGEN.cgmException(Exception,err)


def rig_connect(self,force=False):
    _str_func = ' rig_connect'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        if not is_rigged(self) and force !=True:
            log.debug("|{0}| >>  Module not rigged".format(_str_func))
            return False
        
        if rig_isConnected(self):
            log.debug("|{0}| >>  Module already connected".format(_str_func))
            return True
        
        mRigNull = self.rigNull
        #str_shortName = self.p_nameShort
        
        mi_rigNull = self.rigNull
        ml_rigJoints = mi_rigNull.msgList_get('rigJoints',asMeta = True)
        ml_skinJoints = rig_getSkinJoints(self,asMeta=True)
    
        if self.moduleType in l_faceModules:
            _b_faceState = True
            mi_faceDeformNull = self.faceDeformNull
        else:_b_faceState = False
    
        if len(ml_skinJoints)!=len(ml_rigJoints):
            raise ValueError,"Rig/Skin joint chain lengths don't match"
    
        l_constraints = []
        int_lenMax = len(ml_skinJoints)
        for i,mJnt in enumerate(ml_skinJoints):
            _str_joint = mJnt.p_nameShort
            if _b_faceState:
                log.debug("|{0}| >>  face connect mode...".format(_str_func))                
                #pntConstBuffer = mc.parentConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)  
                pntConstBuffer = mc.pointConstraint(ml_rigJoints[i].mNode,mJnt.mNode,maintainOffset=False,weight=1)        
                orConstBuffer = mc.orientConstraint(ml_rigJoints[i].mNode,mJnt.mNode,maintainOffset=False,weight=1) 			
                #scConstBuffer = mc.scaleConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1) 
                #if 'eyeOrb' not in _str_joint:
                    #for str_a in 'xyz':
                    #attributes.doConnectAttr('%s.s%s'%(i_jnt.parent,str_a),'%s.offset%s'%(scConstBuffer[0],str_a.capitalize()))			    
                    ##attributes.doConnectAttr('%s.s%s'%(mi_faceDeformNull.mNode,str_a),'%s.offset%s'%(scConstBuffer[0],str_a.capitalize()))
            else:
                log.debug("|{0}| >>  Reg connect mode...".format(_str_func))                                
                pntConstBuffer = mc.pointConstraint(ml_rigJoints[i].mNode,mJnt.mNode,maintainOffset=False,weight=1)        
                orConstBuffer = mc.orientConstraint(ml_rigJoints[i].mNode,mJnt.mNode,maintainOffset=False,weight=1) 
            scConstBuffer = mc.scaleConstraint(ml_rigJoints[i].mNode,mJnt.mNode,maintainOffset=False,weight=1)                         
            #attributes.doConnectAttr((ml_rigJoints[i].mNode+'.s'),(i_jnt.mNode+'.s'))

        return True        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
    
def rig_isConnected(self):
    _str_func = ' rig_isConnected'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        mRigNull = self.rigNull
        ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
        ml_skinJoints = rig_getSkinJoints(self)

        if not is_rigged(self):
            log.debug("|{0}| >>  Module not rigged".format(_str_func))
            return False

        for i,mJnt in enumerate(ml_skinJoints):
            if not mJnt.isConstrainedBy(ml_rigJoints[i].mNode):
                log.warning(" [{0}]>> NOT constraining>> [{1}]".format(ml_rigJoints[i].getShortName(),mJnt.getShortName()))
                return False

        return True        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def rig_getSkinJoints(self,asMeta=True):
    _str_func = ' rig_getSkinJoints'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        mRigNull = self.rigNull
        ml_skinJoints = []
        
        ml_moduleJoints = mRigNull.msgList_get('moduleJoints',asMeta = True, cull = True)
        int_lenMax = len(ml_moduleJoints)
        for i,mJnt in enumerate(ml_moduleJoints):
            ml_skinJoints.append(mJnt)
            #for attr in mRig.__l_moduleJointSingleHooks__:
                #str_attrBuffer = i_j.getMessage(attr)
                #if str_attrBuffer:ml_skinJoints.append( cgmMeta.validateObjArg(str_attrBuffer) )
            #for attr in mRig.__l_moduleJointMsgListHooks__:
                #l_buffer = i_j.msgList_get(attr,asMeta = b_asMeta,cull = True)
        if asMeta:return ml_skinJoints
        if ml_skinJoints:
            return [obj.mNode for obj in ml_skinJoints]	    
        return True
    
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def rig_disconnect(self,force=False):
    _str_func = ' rig_disconnect'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        if not is_rigged(self) and force !=True:
            log.debug("|{0}| >>  Module not rigged".format(_str_func))
            return False
        
        if not rig_isConnected(self):
            log.debug("|{0}| >>  Module not connected".format(_str_func))
            return True
        
        mRigNull = self.rigNull
        mRigNull.moduleSet.reset()
        
        mi_rigNull = self.rigNull
        ml_skinJoints = rig_getSkinJoints(self,asMeta=True)
        if not ml_skinJoints:
            raise ValueError,"No skin joints found"
        
        l_constraints = []
        for i,mJnt in enumerate(ml_skinJoints):
            _str_joint = mJnt.p_nameShort
            l_constraints.extend( mJnt.getConstraintsTo() )
            #if not _b_faceState:attributes.doBreakConnection("%s.scale"%_str_joint)
            #attributes.doBreakConnection("%s.scale"%_str_joint)

        if l_constraints:mc.delete(l_constraints)
        return True        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def rig_reset(self,):
    _str_func = ' rig_reset'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        self.rigNull.moduleSet.reset()
        return True
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
    
def parentModule_set(self,mModuleParent = None):
    _str_func = ' parentModule_set'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))    
    #try:
    mModuleParent  = cgmMeta.validateObjArg(mModuleParent,'cgmRigModule',noneValid=True)
    if not mModuleParent:
        log.debug("|{0}| >> Failed to register as cgmRigModule: {1}".format(_str_func,mModuleParent))            
        return False
    
    ml_children = mModuleParent.moduleChildren or []

    if self in ml_children:
        log.debug("|{0}| >> Already connected to parent: {1}".format(_str_func,mModuleParent))
        if self.moduleParent is not mModuleParent:
            self.moduleParent = mModuleParent.mNode
    else:
        log.debug("|{0}| >> Not in children...".format(_str_func))            
        ml_children.append(self) #Revist when children has proper add/remove handling
        mModuleParent.moduleChildren = ml_children
        self.moduleParent = mModuleParent.mNode
    self.parent = mModuleParent.parent
    return True
    #except Exception,err:cgmGEN.cgmException(Exception,err)
set_parentModule = parentModule_set

def parentModule_get(self):
    _str_func = ' parentModule_get'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))    
    
    #try:
    mModuleParent  = self.getMessage('moduleParent',asMeta=True)
    
    if mModuleParent:
        return mModuleParent[0]
    log.debug("|{0}| >> Failed to get a moduleParent".format(_str_func))
        
    mModulePuppet = self.getMessage('modulePuppet',asMeta=True)
    if mModulePuppet:
        return mModulePuppet[0]
    log.debug("|{0}| >> Failed to find a modulePuppet".format(_str_func))
    
    return False
    #except Exception,err:cgmGEN.cgmException(Exception,err)
    
    
    
def skeleton_connectToParent(self):
    _str_func = 'skeleton_connectToParent'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    ml_moduleJoints = self.rigNull.msgList_get('moduleJoints',asMeta = True)
    mBlock = self.rigBlock
    ml_parentBlocks = mBlock.getBlockParents()
    
    if ml_parentBlocks:
        log.debug("|{0}| >> ml_parentBlocks: {1}".format(_str_func,ml_parentBlocks))           
        
        if ml_parentBlocks[0].getMessage('moduleTarget'):
            mParentModule = ml_parentBlocks[0].moduleTarget
        else:
            log.debug("|{0}| >> No module target found.".format(_str_func))           
            return False
        
        if ml_parentBlocks[0].blockType == 'master':
            log.info("|{0}| >> Master block...".format(_str_func))           
            if mParentModule.getMessage('rootJoint'):
                log.debug("|{0}| >> Root joint on master found".format(_str_func))
                ml_moduleJoints[0].p_parent = mParentModule.getMessage('rootJoint')[0]
                #TRANS.parent_set(l_moduleJoints[0], mParentModule.getMessage('rootJoint')[0])
                return True
            else:
                log.debug("|{0}| >> No root joint".format(_str_func))
                return True
        else:
            ml_targetJoints = mParentModule.rigNull.msgList_get('moduleJoints',asMeta = True, cull = True)
            if not ml_targetJoints:
                raise ValueError,"mParentModule has no module joints."
            _attachPoint = ATTR.get_enumValueString(mBlock.mNode,'attachPoint')
            if _attachPoint == 'end':
                mTargetJoint = ml_targetJoints[-1]
            elif _attachPoint == 'base':
                mTargetJoint = ml_targetJoints[0]
            else:
                raise ValueError,"Not done with {0}".format(_attachPoint)
        
            ml_moduleJoints[0].p_parent = mTargetJoint
    return True

def get_attachPoint(self, mode = 'end',noneValid = True):
    _str_func = 'get_attachPoint'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    mParentModule = self.getMessage('moduleParent',asMeta=True)
    if not mParentModule:
        if self.modulePuppet:
            if self.modulePuppet.getMessage('rootJoint'):
                log.debug("|{0}| >> Root joint on master found".format(_str_func))
                return self.modulePuppet.rootJoint[0]
            return False
        raise RuntimeError,"Shouldn't have gotten here"
    else:
        mParentModule = mParentModule[0]
        log.debug("|{0}| >> moduleParent: {1}".format(_str_func,mParentModule))
        
        mParentRigNull = mParentModule.rigNull
        
        for plug in ['blendJoints','fkJoints','moduleJoints']:
            if mParentRigNull.msgList_get(plug):
                ml_targetJoints = mParentRigNull.msgList_get(plug,asMeta = True, cull = True)
                log.debug("|{0}| >> Found parentJoints: {1}".format(_str_func,plug))                
                break
            
        if not ml_targetJoints:
            raise ValueError,"mParentModule has no module joints."
        if mode == 'end':
            mTarget = ml_targetJoints[-1]
        elif mode == 'base':
            mTarget = ml_targetJoints[0]
        else:
            _msg = ("|{0}| >> Unknown mode: {1}".format(_str_func,mode))
            if noneValid:
                return log.error(_msg)
            raise ValueError,_msg
        return mTarget
    
def get_driverPoint(self, mode = 'end',noneValid = True):
    _str_func = 'get_driverPoint'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    mParentModule = self.getMessage('moduleParent',asMeta=True)
    b_parentMode = False
    if not mParentModule:
        if self.modulePuppet:
            log.debug("|{0}| >> Master found".format(_str_func))            
            #if self.modulePuppet.getMessage('rootJoint'):
                #log.debug("|{0}| >> Root joint on master found".format(_str_func))
                #return self.modulePuppet.rootJoint[0]
            return self.modulePuppet.masterNull.skeletonGroup
        raise RuntimeError,"Shouldn't have gotten here"
    else:
        mParentModule = mParentModule[0]
        log.debug("|{0}| >> moduleParent: {1}".format(_str_func,mParentModule))
        mParentRigNull = mParentModule.rigNull
        #ml_targetJoints = mParentRigNull.msgList_get('rigJoints',asMeta = True, cull = True)
        for plug in ['blendJoints','fkJoints','moduleJoints']:
            if mParentRigNull.msgList_get(plug):
                ml_targetJoints = mParentRigNull.msgList_get(plug,asMeta = True, cull = True)
                log.debug("|{0}| >> Found parentJoints: {1}".format(_str_func,plug))
                
                break        
        
        if not ml_targetJoints:
            raise ValueError,"mParentModule has no rig joints."
        if mode == 'end':
            mTarget = ml_targetJoints[-1]
        elif mode == 'base':
            mTarget = ml_targetJoints[0]
        else:
            _msg = ("|{0}| >> Unknown mode: {1}".format(_str_func,mode))
            if noneValid:
                return log.error(_msg)
            raise ValueError,_msg
        
        if mTarget.getMessage('dynParentGroup'):
            log.debug("|{0}| >>  dynParentGroup found. ".format(_str_func,self))
            mDynParentGroup = mTarget.dynParentGroup
            #if not mDynParentGroup.hasAttr('cgmAlias'):
            mDynParentGroup.doStore('cgmAlias', mTarget.cgmName)
            log.debug("|{0}| >> alias: {1}".format(_str_func,mDynParentGroup.cgmAlias))
            return mDynParentGroup
            mTarget = mTarget.dynParentGroup

        return mTarget
    
    
def get_joints(self, skinJoints = False, moduleJoints =False, rigJoints=False, selectResult = False, asMeta = False):
    _str_func = ' get_joints'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        mRigNull = self.rigNull
        str_shortName = self.p_nameShort
        
        if not skinJoints and not moduleJoints and not rigJoints:
            log.debug("|{0}| >> Nothing set to find. Check your kws".format(_str_func))
            return False
        
        l_return = []
        if moduleJoints or skinJoints:
            l_res = mRigNull.msgList_get('moduleJoints',asMeta = False)
                
            if skinJoints:
                for obj in l_res:
                    log.debug("|{0}| >> Checking: {1}".format(_str_func,obj))
                    #l_attrs = mc.listAttr(obj,ud = 1)
                    #for a in l_attrs:
                    for singleHook in BLOCKSHARE.__l_moduleJointSingleHooks__:
                        if ATTR.has_attr(obj,singleHook):
                            log.debug("|{0}| >> Checking: {1}.{2}".format(_str_func,obj,singleHook))                                
                            bfr_single =  ATTR.get_message(obj,singleHook)
                            if bfr_single:
                                log.debug("|{0}| >> Found: {1}".format(_str_func,bfr_single))                                
                                l_res.insert(l_res.index(obj) +1,bfr_single[0])                                    

                    for msgHook in BLOCKSHARE.__l_moduleJointMsgListHooks__:
                        res_msgList = ATTR.msgList_get(obj,msgHook)
                        if res_msgList:
                            log.debug("|{0}| >> Found: {1}".format(_str_func,res_msgList))                                
                            l_res.insert(l_res.index(obj) +1, res_msgList)                                        
            if l_res:l_return.extend(l_res)
        if rigJoints:
            buffer = mRigNull.msgList_get('rigJoints',asMeta = False)
            if buffer:l_return.extend(buffer)
        
        l_return = LISTS.get_noDuplicates(l_return)
        
        if not l_return:
            return []
        elif selectResult:
            mc.select(l_return)
    
        if asMeta:
            return cgmMeta.validateObjListArg(l_return,'cgmObject')
        return l_return        
    
    
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
    
#=============================================================================================================
#>> Anim
#=============================================================================================================
def anim_settings_toggle(self,attr=None):
    try:
        _str_func = ' anim_settings_toggle'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
        if self.rigNull.getMessage('settings'):
            mSettings = self.rigNull.settings
            _short_settings = mSettings.mNode
            try:
                ATTR.set(_short_settings,attr,not(ATTR.get(_short_settings,attr)))
            except Exception,err:
                log.debug("|{0}| >>  Failed to set: module:{1} | attr:{2}".format(_str_func,self.mNode,attr))
        else:
            log.debug("|{0}| >>  Missing settings: {1}".format(_str_func,self.mNode))
        return True        
    except Exception,err:cgmGEN.cgmException(Exception,err)



def anim_reset(self,transformsOnly = True):
    try:
        _str_func = ' anim_reset'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        _result = False
        _sel = mc.ls(sl=True)
        mRigNull = self.rigNull
        mRigNull.moduleSet.select()
        if mc.ls(sl=True):
            ml_resetChannels.main(transformsOnly = transformsOnly)
            _result = True
        if _sel:mc.select(_sel)
        return _result
        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def anim_select(self):
    try:
        _str_func = ' anim_select'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        mRigNull = self.rigNull        
        mRigNull.moduleSet.select()
        return True        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def anim_key(self,**kws):
    try:
        _str_func = ' anim_key'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        mRigNull = self.rigNull
        _result = False
        _sel = mc.ls(sl=True)
        
        l_objs = mRigNull.moduleSet.getList() or []
        
        if l_objs:
            mc.select(l_objs)
            mc.setKeyframe(**kws)
            b_return =  True
            
        if _sel:mc.select(_sel)
        return _result
        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def mirror_get(self):
    _str_func = 'mirror_get'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    
    l_direction = ['left','right']
    if not self.hasAttr('cgmDirection'):
        log.debug("|{0}| >>  has no cgmDirection".format(_str_func))
        return False

    int_direction = l_direction.index(self.cgmDirection)
    d = {'cgmName':self.cgmName,'moduleType':self.moduleType,'cgmDirection':l_direction[not int_direction]}
    log.debug("|{0}| >>  looking for: {1}".format(_str_func,d))

    
    mModuleParent  = self.getMessage('moduleParent',asMeta=True)
    log.debug("|{0}| >> ModuleParent: {1}".format(_str_func,mModuleParent))
    if not mModuleParent:
        return False
    
    ml_match = []
    ml_children = mModuleParent[0].atUtils('moduleChildren_get')
    for mChild in ml_children:
        #log.debug("|{0}| >> mChild: {1}".format(_str_func,mChild))        
        _match = True
        for a,v in d.iteritems():
            if not str(mChild.getMayaAttr(a)) == str(v):
                #log.debug("|{0}| >> fail: {1}:{2} | {3}".format(_str_func,a,v,str(mChild.getMayaAttr(a))))                        
                _match = False
                break
        if not mChild.moduleParent == mModuleParent[0]:
            _match = False
        if _match:ml_match.append(mChild)
    
    if len(ml_match)>1:
        raise ValueError,"Shouldn't have found more than one mirror module!"
    elif not ml_match:
        return False
    return ml_match[0]
    
    

def mirror(self,mode = 'self'):
    """
    Module based mirror functions

    :parameters:
        mode(str):
            self
            push
            pull
            symLeft
            symRight
        
    :returns
        list of results(list)
    """        
    try:
        _str_func = ' mirror'.format(self)
        log.debug("|{0}| >> mode: {1} | [{2}]".format(_str_func,mode,self)+ '-'*80)
        
        mRigNull = self.rigNull
        _result = False
        _sel = mc.ls(sl=True)
        mode_lower = mode.lower()
        
        l_objs = mRigNull.moduleSet.getList() or []
        mMirror = mirror_get(self)
        if mMirror:
            l_objs.extend(mMirror.rigNull.moduleSet.getList())        
        
        if l_objs:
            if mode_lower in ['self','me']:
                r9Anim.MirrorHierarchy().mirrorData(l_objs,mode = '')
                _result = True
            elif mode_lower in ['push','pull','symleft','symright']:
                if not mMirror:
                    return log.error("|{0}| >> Must have mirror module for mode: {1} | [{2}]".format(_str_func,mode,self))
                if mode_lower == 'push':
                    _primeAxis = self.cgmDirection.capitalize()
                elif mode_lower == 'pull':
                    _primeAxis = mMirror.cgmDirection.capitalize()
                elif mode_lower == 'symleft':
                    _primeAxis = 'Left'
                else:
                    _primeAxis = 'Right'

                r9Anim.MirrorHierarchy().makeSymmetrical(l_objs,mode = '',primeAxis = _primeAxis )
                _result = True                
            else:
                raise ValueError,"|{0}| >> unknown mode: {1} | [{2}]".format(_str_func,mode,self)            
                
            
        if _sel:
            mc.select(_sel)
        else:
            mc.select(l_objs)
        return _result
        
    except Exception,err:cgmGEN.cgmException(Exception,err)