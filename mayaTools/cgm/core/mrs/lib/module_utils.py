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
log.setLevel(logging.INFO)
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
import cgm.core.lib.name_utils as NAMES
import cgm.core.cgmPy.str_Utils as STRINGS
from cgm.core.classes import GuiFactory as cgmUI

from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.lib.ml_tools.ml_resetChannels as ml_resetChannels
import cgm.core.rig.general_utils as RIGGEN

l_faceModules = ['eyebrow','eyelids','eyeball','mouthNose','simpleFace']

#=============================================================================================================
#>> Queries
#=============================================================================================================
def get_partName(self):
    _str_func = ' get_partName'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:#Quick select sets ================================================================
        _d = NAMETOOLS.get_objNameDict(self.mNode)
        _d['cgmTypeModifier'] = self.getMayaAttr('moduleType')
        log.debug("|{0}| >>  d: {1}".format(_str_func,_d))
        
        _str= NAMETOOLS.returnCombinedNameFromDict(_d)
        log.debug("|{0}| >>  str: {1}".format(_str_func,_str))
        return STRINGS.stripInvalidChars(_str)

    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

def mirror_getSideString(self):
    _str_func = ' mirror_getSideString'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        _str_direction = self.getMayaAttr('cgmDirection') 
        
        if _str_direction is not None and _str_direction.lower() in ['right','left']:
            return _str_direction.capitalize()
        else:return 'Centre'	           
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)


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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
    
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
    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def doName(self):
    _str_func = ' doName'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    try:
        _d = NAMETOOLS.get_objNameDict(self.mNode)
        
        _d['cgmTypeModifier'] = self.getMayaAttr('moduleType')
        _d['cgmType'] = 'part'
        log.debug("|{0}| >>  d: {1}".format(_str_func,_d))
        
        _str= NAMETOOLS.returnCombinedNameFromDict(_d)
        log.debug("|{0}| >>  str: {1}".format(_str_func,_str))
        self.rename(_str)
    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
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
        mSet.doStore('cgmName',self)
        mSet.doName()

        if self.getMessage('modulePuppet'):
            mi_modulePuppet = self.modulePuppet
            if not mi_modulePuppet.getMessage('puppetSet'):
                mi_modulePuppet.verify_objectSet()
            self.modulePuppet.puppetSet.addObj(mSet.mNode)
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def verify_faceObjectSet(self):
    _str_func = ' verify_faceObjectSet'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:#Quick select sets ================================================================
        mPuppetSet = False
        mRigNull = self.rigNull
        
        if self.modulePuppet:
            mModulePuppet = self.modulePuppet
            mPuppetSet = mModulePuppet.getMessageAsMeta('puppetSet') or mModulePuppet.verify_objectSet()
                
        mParentModule = self.getMessageAsMeta('moduleParent')
        if not mParentModule:
            mParentModule = mModulePuppet
        
        mFaceSet = mParentModule.rigNull.getMessageAsMeta('faceSet')
        #mParentSet = mParentModule.rigNull.getMessageAsMeta('moduleSet')
        
        _created = False
        
        if mFaceSet:
            log.debug("|{0}| >>  faceSet exists from moduleParent: {1}".format(_str_func,mFaceSet))            
        else:
            _created = True
            mFaceSet = cgmMeta.cgmObjectSet(setType='animSet',qssState=True)
            mParentModule.rigNull.connectChildNode(mFaceSet.mNode,'faceSet','rigNull')
        
        mRigNull.connectChildNode(mFaceSet.mNode,'faceSet')        
        mFaceSet.doStore('cgmName',"{0}_face".format(get_partName(mParentModule)))
        mFaceSet.doName()
        
        if mPuppetSet:
            mPuppetSet.addObj(mFaceSet.mNode)
        return mFaceSet
            
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
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

    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
#=============================================================================================================
#>> Rig
#=============================================================================================================


def is_rigged(self):
    _str_func = ' is_rigged'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        log.debug("|{0}| >>  ||| FINISH THIS CALL ||| ".format(_str_func))
        
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)


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
            #ATTR.connect((ml_rigJoints[i].mNode+'.s'),(mJnt.mNode+'.s'))
            #attributes.doConnectAttr((ml_rigJoints[i].mNode+'.s'),(i_jnt.mNode+'.s'))

        return True        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
    
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
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
    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def rig_reset(self,transformsOnly = True):
    _str_func = ' rig_reset'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    try:
        _sel = mc.ls(os=True) or []
        self.rigNull.moduleSet.select()
        RIGGEN.reset_channels(transformsOnly = transformsOnly)
        if _sel:
            mc.select(_sel)
        return True
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
    
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
    #except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
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
    
def parentModules_get(self):
    _str_func = ' parentModules_get'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))    
    
    #try:
    mModuleParent  = self.getMessageAsMeta('moduleParent')
    ml_moduleParents = []
    
    if mModuleParent:
        _parentFound = True
        ml_moduleParents.append(mModuleParent)
        while _parentFound:
            mBuffer = ml_moduleParents[-1].getMessageAsMeta('moduleParent')
            if mBuffer:
                ml_moduleParents.append(mBuffer)
                log.debug("|{0}| >>  Found mParent: {1} ".format(_str_func,mBuffer))
            else:
                _parentFound = False
                
        return ml_moduleParents
    log.debug("|{0}| >> Failed to get a moduleParent".format(_str_func))
    return []
    mModulePuppet = self.getMessageAsMeta('modulePuppet')
    if mModulePuppet:
        return [mModulePuppet]
    log.debug("|{0}| >> Failed to find a modulePuppet".format(_str_func))
    
    return False

    
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
            log.debug("|{0}| >> Master block...".format(_str_func))           
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
        
        l_msgLinks = ['blendJoints','fkJoints','moduleJoints']
        _direct = False
        if mParentModule.moduleType in ['head'] and mode == 'end':
            l_msgLinks = ['rigJoints']
            _direct = True
            
        for plug in l_msgLinks:#'handleJoints',        
        

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
        elif mode == 'closest':
            ml_moduleJoints = self.rigNull.msgList_get('moduleJoints',asMeta = True)            
            jnt = DIST.get_closestTarget(ml_moduleJoints[0].mNode, [mObj.mNode for mObj in ml_targetJoints])
            mTarget = cgmMeta.asMeta(jnt)
        else:
            _msg = ("|{0}| >> Unknown mode: {1}".format(_str_func,mode))
            if noneValid:
                return log.error(_msg)
            raise ValueError,_msg
        return mTarget
    
def get_driverPoint(self, mode = 'end',noneValid = True):
    """
    Get the main driver point for a 
    """
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
            return self.modulePuppet.masterControl
            #return self.modulePuppet.masterNull.skeletonGroup
        raise RuntimeError,"Shouldn't have gotten here"
    else:
        mParentModule = mParentModule[0]
        log.debug("|{0}| >> moduleParent: {1}".format(_str_func,mParentModule))
        mParentRigNull = mParentModule.rigNull
        #ml_targetJoints = mParentRigNull.msgList_get('rigJoints',asMeta = True, cull = True)
        _plugUsed = None
        l_msgLinks = ['blendJoints','fkJoints','moduleJoints']
        _direct = False
        if mParentModule.moduleType in ['head'] and mode == 'end':
            l_msgLinks = ['rigJoints']
            _direct = True
            
        for plug in l_msgLinks:#'handleJoints',
            if mParentRigNull.msgList_get(plug):
                ml_targetJoints = mParentRigNull.msgList_get(plug,asMeta = True, cull = True)
                log.debug("|{0}| >> Found parentJoints: {1}".format(_str_func,plug))
                _plugUsed = plug
                break        
        
        if not ml_targetJoints:
            raise ValueError,"mParentModule has no rig joints."
        if mode == 'end':
            mTarget = ml_targetJoints[-1]
        elif mode == 'base':
            mTarget = ml_targetJoints[0]
        elif mode == 'closest':
            ml_moduleJoints = self.rigNull.msgList_get('moduleJoints',asMeta = True)            
            jnt = DIST.get_closestTarget(ml_moduleJoints[0].mNode, [mObj.mNode for mObj in ml_targetJoints])
            mTarget = cgmMeta.asMeta(jnt)        
        else:
            _msg = ("|{0}| >> Unknown mode: {1}".format(_str_func,mode))
            if noneValid:
                return log.error(_msg)
            raise ValueError,_msg
        
        if _plugUsed not in ['handleJoints'] and _direct != True:
            if mTarget.getMessage('masterGroup'):
                log.debug("|{0}| >>  masterGroup found found. ".format(_str_func))
                return mTarget.masterGroup
            if mTarget.getMessage('dynParentGroup'):
                log.debug("|{0}| >>  dynParentGroup found. ".format(_str_func,self))
                mDynParentGroup = mTarget.dynParentGroup
                #if not mDynParentGroup.hasAttr('cgmAlias'):
                mDynParentGroup.doStore('cgmAlias', mTarget.cgmName)
                log.debug("|{0}| >> alias: {1}".format(_str_func,mDynParentGroup.cgmAlias))
                return mDynParentGroup
                mTarget = mTarget.dynParentGroup

        return mTarget
    
reload(BLOCKSHARE)
l_controlOrder = ['root','settings','fk','ik','pivots','segmentHandles','direct']
d_controlLinks = {'root':['cog','rigRoot','limbRoot'],
                  'fk':['fkJoints','leverFK','controlsFK','controlFK'],
                  'ikEnd':['controlIK'],
                  'ik':['controlIK','controlIKEnd',
                        'controlIKBase','controlsFK',
                        'controlIKMid','leverIK','eyeLookAt','lookAt'],
                  'face':['controlsFace'],
                  'pivots':['pivot{0}'.format(n.capitalize()) for n in BLOCKSHARE._l_pivotOrder],
                  'segmentHandles':['handleJoints','controlSegMidIK'],
                  'direct':['rigJoints']}

def controls_getDat(self, keys = None, ignore = [], report = False, listOnly = False):
    """
    Function to find all the control data for comparison for mirroing or other reasons
    """
    def addMObj(mObj,mList):
        if mObj not in mList:
            if ml_objs is not None:
                if mObj in ml_objs:
                    ml_objs.remove(mObj)
                else:
                    log.warning("|{0}| >> Not in list. resolve: {1}".format(_str_func,mObj))
            log.debug("|{0}| >> adding: {1}".format(_str_func,mObj))
            mList.append(mObj)
                
                    
    _str_func = ' controls_getDat'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    ignore = VALID.listArg(ignore)
    
    mRigNull = self.rigNull
    try:ml_objs = mRigNull.moduleSet.getMetaList() or []
    except:ml_objs = []
    #l_objs = [mObj.mNode for mObj in ml_objs]
    md_controls = {}
    ml_controls = []
    
    if keys:
        l_useKeys = VALID.listArg(keys)
        
    else:
        l_useKeys = l_controlOrder
    
    if ignore:
        log.debug("|{0}| >> Ignore found... ".format(_str_func)+'-'*20)        
        for k in ignore:
            if k in l_useKeys:
                l_useKeys.remove(k)
                
    for key in l_useKeys:
        l_options = d_controlLinks.get(key,[key])
        log.debug("|{0}| >>  {1}:{2}".format(_str_func,key,l_options))
        md_controls[key] = []
        _ml = md_controls[key]
        for o in l_options:
            if mRigNull.getMessage(o):
                log.debug("|{0}| >>  Message found: {1} ".format(_str_func,o))                
                mObj = mRigNull.getMessage(o,asMeta=True)[0]
                addMObj(mObj,_ml)
            elif mRigNull.msgList_exists(o):
                log.debug("|{0}| >>  msgList found: {1} ".format(_str_func,o))                
                _msgList = mRigNull.msgList_get(o)
                for mObj in _msgList:
                    addMObj(mObj,_ml)
        ml_controls.extend(_ml)

    if ml_objs:
        ml_dup = copy.copy(ml_objs)
        log.debug("|{0}| >> Second pass {1}... ".format(_str_func,len(ml_objs))+'-'*20)
        for mObj in ml_dup:
            log.debug("|{0}| >> {1} ".format(_str_func,mObj))            
            if mObj.hasAttr('cgmControlDat'):
                _tags = mObj.cgmControlDat.get('tags',[])
                log.debug("|{0}| >> tags: {1} ".format(_str_func,_tags))            
                for t in _tags:
                    _t = str(t)
                    #if keys is not None and _t not in l_useKeys:
                    #    continue
                    if not md_controls.get(_t):
                        md_controls[_t] = []
                    _ml = md_controls[_t] 
                    ml_controls.append(mObj)                    
                    addMObj(mObj,_ml)
    
    if not keys and 'spacePivots' not in ignore:
        md_controls['spacePivots'] = []
        _ml = md_controls['spacePivots']
        for mObj in ml_controls:
            mBuffer = mObj.msgList_get('spacePivots')
            for mSpace in mBuffer:
                addMObj(mSpace,_ml)
                ml_controls.append(mSpace)
    
    if report:
        log.info("|{0}| >> Dict... ".format(_str_func))
        pprint.pprint( md_controls)
        
        log.info("|{0}| >> List... ".format(_str_func))
        pprint.pprint( ml_controls)
    
    if ml_objs and keys is None and not ignore:        
        log.debug("|{0}| >> remaining... ".format(_str_func))
        pprint.pprint( ml_objs)
        raise ValueError,("|{0}| >> Resolve missing controls!".format(_str_func))
        #return log.error("|{0}| >> Resolve missing controls!".format(_str_func))
    
    if report:
        return
    
    if keys or listOnly:
        return ml_controls
    return md_controls,ml_controls
    
def controls_get(self, mode = 'mirror'):
    _str_func = ' controls_get'    
    if mode == 'mirror':
        return controls_getDat(self,ignore='spacePivots',listOnly=True)
    else:
        return controls_getDat(self,mode,listOnly=True)
        
    log.error("|{0}| >> No options specified".format(_str_func))
    return False
    
def get_joints(self, skinJoints = False, moduleJoints =False, rigJoints=False,
               selectResult = False, asMeta = False):
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
    
    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
    
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)



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
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def anim_select(self):
    try:
        _str_func = ' anim_select'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        mRigNull = self.rigNull        
        mRigNull.moduleSet.select()
        return True        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
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
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

def siblings_get(self,matchType = False, excludeSelf = True, matchName=False):
    _str_func = 'siblings_get'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)

    d = {}
    if matchType:
        d['moduleType'] = self.moduleType
    if matchName:
        d['cgmName'] = self.cgmName


    mModuleParent  = self.getMessage('moduleParent',asMeta=True)
    log.debug("|{0}| >> ModuleParent: {1}".format(_str_func,mModuleParent))
    if not mModuleParent:
        return False
    
    ml_match = []
    ml_children = mModuleParent[0].atUtils('moduleChildren_get')
    for mChild in ml_children:
        log.debug("|{0}| >> mChild: {1}".format(_str_func,mChild))        
        _match = True
        for a,v in d.iteritems():
            if not str(mChild.getMayaAttr(a)) == str(v):
                _match = False
                continue
        if not mChild.moduleParent == mModuleParent[0]:
            _match = False
            continue
        if _match:ml_match.append(mChild)
    
    if excludeSelf:
        ml_match.remove(self)
    return ml_match

def mirror_get(self,recheck=False):
    _str_func = 'mirror_get'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    if not recheck:
        mMirror = self.getMessage('moduleMirror',asMeta=True)
        if mMirror:
            log.debug("|{0}| >>  Stored moduleMirror found: {1}".format(_str_func,mMirror))
            return mMirror[0]
        
    l_direction = ['left','right']
    _cgmDirection = self.getMayaAttr('cgmDirection')
    if not _cgmDirection or str(_cgmDirection).lower() in ['center','centre']:
        log.debug("|{0}| >>  has no cgmDirection".format(_str_func))
        return False

    int_direction = l_direction.index(self.cgmDirection)
    d = {'cgmName':self.cgmName,'moduleType':self.moduleType,
         'cgmDirection':l_direction[not int_direction]}
    for plug in 'cgmPosition','cgmPositionModifier','cgmDirectionModifier':
        if self.hasAttr(plug):
            d[plug] = getattr(self,plug)
        
    log.debug("|{0}| >>  looking for: {1}".format(_str_func,d))

    mModulePuppet  = self.getMessage('modulePuppet',asMeta=True)
    
    log.debug("|{0}| >> mModulePuppet: {1}".format(_str_func,mModulePuppet))
    if not mModulePuppet:
        return False
    
    ml_match = []
    ml_children = mModulePuppet[0].atUtils('modules_get')
    #print ml_children
    for mChild in ml_children:
        log.debug("|{0}| >> mChild: {1}".format(_str_func,mChild))        
        _match = True
        for a,v in d.iteritems():
            if not str(mChild.getMayaAttr(a)) == str(v):
                log.debug("|{0}| >> fail: {1}:{2} | {3}".format(_str_func,a,v,str(mChild.getMayaAttr(a))))
                _match = False
                continue
        if _match:ml_match.append(mChild)
    
    if len(ml_match)>1:
        pprint.pprint(vars())
        raise ValueError,"Shouldn't have found more than one mirror module!"
    elif not ml_match:
        return False
    
    self.doStore('moduleMirror',ml_match[0])
    return ml_match[0]

def mirror_reportSetup(self):
    _str_func = ' mirror_reportSetup'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    d_self = get_mirrorDat(self)
    d_mirror = {}
    if d_self.get('mMirror'):
        d_mirror = get_mirrorDat(d_self.get('mMirror'))
        
    md_controls = {'Centre':{},'Left':{},'Right':{}}
    
    def registerObj(mObj):
        _side = mObj.getEnumValueString('mirrorSide')
        _v = mObj.mirrorIndex
        
        if md_controls[_side].get(_v):
            raise ValueError,"Already stored: {0} | {1} | stored: {2} | mObj: {3}".format(_v,
                                                                                          _side,
                                                                                          md_controls[_side].get(_v),mObj)
        
        md_controls[_side][_v] = mObj
        
        
        
    if not d_mirror:
        for mObj in d_self['ml_controls']:
            registerObj(mObj)
            
            """
            print("{0} [{1}] | {2} | {3}".format(mObj.mirrorIndex,
                                                         mObj.getEnumValueString('mirrorSide'),
                                                         mObj.p_nameShort,
                                                         mObj.mirrorAxis))"""
    else:
        for dSet in d_self,d_mirror:
            for mObj in dSet['ml_controls']:
                registerObj(mObj)
                       
    if md_controls.get('Centre'):
        print(cgmGEN._str_subLine)
        print("Centre...")
        l_keys = md_controls['Centre'].keys()
        l_keys.sort()
        for i in l_keys:
            mObj = md_controls['Centre'][i]
            print("[{0}] : {1} | {2}".format(mObj.mirrorIndex,
                                             mObj.p_nameShort,
                                             mObj.mirrorAxis))
    
    if md_controls.get('Left') and md_controls.get('Right'):
        print(cgmGEN._str_subLine)
        print("Sides...")
        
        l_keysLeft = md_controls['Left'].keys()
        l_keysRight = md_controls['Right'].keys()
        
        minLeft = min(l_keysLeft)
        minRight = min(l_keysRight)
        maxLeft = max(l_keysLeft)
        maxRight = max(l_keysRight)
        
        i_min = minLeft
        if minRight<i_min:
            i_min = minRight
        
        i_max = maxLeft
        if maxRight>i_max:
            i_max = maxRight
            
        for i in range(i_min,i_max):
            print("[{0}] | Left: {1} | Right: {2}".format(i,
                                                          md_controls['Left'][i].p_nameShort,
                                                          md_controls['Right'][i].p_nameShort,
))                        
    
    else:
        for t in ['Left','Right']:
            print("{0}...".format(t))
            l_keys = md_controls[t].keys()
            l_keys.sort()
            for i in l_keys:
                mObj = md_controls[t][i]
                print("[{0}] : {1} | {2}".format(mObj.mirrorIndex,
                                                 mObj.p_nameShort,
                                                 mObj.mirrorAxis))            
    
def get_mirrorDat(self):
    _str_module = self.p_nameShort
    _d = {}
    _d['str_name'] = _str_module
    md,ml = controls_getDat(self,ignore=['spacePivots'])
    _d['md_controls'] = md
    _d['ml_controls'] = ml#self.rigNull.moduleSet.getMetaList()
    _d['mMirror'] = mirror_get(self)
    _d['str_side'] = cgmGEN.verify_mirrorSideArg(self.getMayaAttr('cgmDirection') or 'center')
    
    #if _d['str_side'] not in d_runningSideIdxes.keys():
        #d_runningSideIdxes[_d['str_side']] = [startIdx]    
    
    return _d

def mirror_verifySetup(self, d_Indices = {},
                       l_processed = None,
                       md_data = None,
                       progressBar = None,progressEnd=True):
    _str_func = ' mirror_verifySetup'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    md_indicesToControls = {}
    for k in ['Centre','Left','Right']:
        if not d_Indices.has_key(k):
            d_Indices[k] = 0
        if not k in md_indicesToControls:
            md_indicesToControls[k] = {}
            
    if l_processed is not None and self in l_processed:
        log.info("|{0}| >> Already processed: {1}".format(_str_func,self))        
        return
    
    if md_data is None:
        md_data = {}
    ml_noMatch = []
    d_runningSideIdxes = {}
    #ml_modules = []
    md_cgmTags = {}
    
    def validate_controls(ml):
        for i,mObj in enumerate(ml):
            log.debug("|{0}| >> First pass: {1}".format(_str_func,mObj))
            
            if not issubclass(type(mObj), cgmMeta.cgmControl):
                log.debug("|{0}| >> Reclassing: {1}".format(_str_func,mObj))
                
                mObj = cgmMeta.asMeta(mObj,'cgmControl',setClass = True)#,setClass = True
                ml[i] = mObj#...push back
                
            md_cgmTags[mObj] = mObj.getCGMNameTags(['cgmDirection'])
            mObj._verifyMirrorable()#...veryify the mirrorsetup
            
            """
            _mirrorSideFromCGMDirection = cgmGEN.verify_mirrorSideArg(mObj.getNameDict().get('cgmDirection','centre'))
            
            _mirrorSideCurrent = cgmGEN.verify_mirrorSideArg(mObj.getEnumValueString('mirrorSide'))

            _setMirrorSide = False
            if _mirrorSideFromCGMDirection:
                if _mirrorSideFromCGMDirection != _mirrorSideCurrent:
                    log.debug("|{0}| >> {1}'s cgmDirection ({2}) is not it's mirror side({3}). Resolving...".format(_str_func,mObj.p_nameShort,_mirrorSideCurrent,_mirrorSideFromCGMDirection))
                    _setMirrorSide = _mirrorSideFromCGMDirection                                            
            elif not _mirrorSideCurrent:
                _setMirrorSide = str_mirrorSide
        
            if _setMirrorSide:
                if not cgmMeta.cgmAttr(mObj,'mirrorSide').getDriver():
                    mObj.doStore('mirrorSide',_setMirrorSide)
                else:
                    #log.debug("{0} mirrorSide driven".format(mObj.p_nameShort))
                    log.debug("|{0}| >> mirror side driven: {1}".format(_str_func,mObj))
        """
            #append the control to our lists to process                                    
            #md_culling_controlLists[_mirrorSideCurrent].append(mObj)    
    
    #>>>Module control maps ===============================================================================
    d_self = get_mirrorDat(self)
    d_mirror = {}
    if d_self.get('mMirror'):
        d_mirror = get_mirrorDat(d_self.get('mMirror'))
        
    if progressBar:
        cgmUI.progressBar_start(progressBar)    
    
    if not d_mirror:
        log.debug("|{0}| >> No mirror found...".format(_str_func))
        if not d_self['ml_controls']:
            raise ValueError,"Not rigged: {0} ".format(self)
        validate_controls(d_self['ml_controls'])
        log.debug(cgmGEN._str_subLine)
        _v = None
        int_len = len(d_self['ml_controls'])
        for i,mObj in enumerate(d_self['ml_controls']):
            if progressBar:
                cgmUI.progressBar_set(progressBar,
                                      minValue = 0,
                                      maxValue=int_len,
                                      progress=i, vis=True)
                
            _side = mObj.getEnumValueString('mirrorSide')
            i_start = d_Indices[_side]
            _v = i_start+1
            log.debug("|{0}| >> Setting index: [{1}] | {2} | {3}".format(_str_func,_v,_side,mObj))
            mObj.mirrorIndex = _v
            d_Indices[_side] = _v#...push it back
            md_indicesToControls[_side][_v] = mObj
            
        if l_processed is not None:l_processed.append(self)
        d_Indices[d_self['str_side']] = _v
        
        if progressBar and progressEnd:cgmUI.progressBar_end(progressBar)
            
        return md_indicesToControls
    
    else:
        log.debug("|{0}| >>  Mirror module found...".format(_str_func))
        mMirror = d_self['mMirror']
        
        #i_start = max([d_Indices['Left'],d_Indices['Right']])
        #i_running = copy.copy(i_start)
        #log.debug("|{0}| >> Starting with biggest side int: {1}".format(_str_func,i_start))
        
        validate_controls(d_self['ml_controls'])
        validate_controls(d_mirror['ml_controls'])
        
        for key in l_controlOrder:
            self_keyControls = d_self['md_controls'].get(key,[])
            mirr_keyControls = d_mirror['md_controls'].get(key,[])
            len_self = len(self_keyControls)
            len_mirr = len(mirr_keyControls)
            
            log.debug("|{0}| >> Key: {1} | self: {2} | mirror: {3}".format(_str_func,key,len_self,len_mirr))
            
            ml_primeControls = self_keyControls #...longer list of controls
            ml_secondControls = mirr_keyControls
            if len_mirr>len_self:
                ml_primeControls = mirr_keyControls 
                ml_secondControls = self_keyControls
            
            ml_cull = copy.copy(ml_secondControls)
            
            for i,mObj in enumerate(ml_primeControls):
                if progressBar:
                    cgmUI.progressBar_set(progressBar,
                                          minValue = 0,
                                          maxValue=len(ml_primeControls),
                                          progress=i, vis=True)
                    
                _side = mObj.getEnumValueString('mirrorSide')                
                i_start = d_Indices[_side]
                _v = i_start+1
                tags_prime = md_cgmTags[mObj]
                
                mObj.mirrorIndex = _v
                d_Indices[_side] = _v#...push it back                
                log.debug("|{0}| >> Setting index: [{1}] | {2} | {3}".format(_str_func,_v,_side,mObj))
                md_indicesToControls[_side][_v] = mObj
                
                #l_baseSplit = mObj.p_nameBase.split('_')
                for mCandidate in ml_cull:
                    #First try a simple name match
                    #l_candSplit = mCandidate.p_nameBase.split('_')
                    _match = True
                    tags_second = md_cgmTags[mCandidate]
                    for a,v in tags_second.iteritems():
                        if tags_prime[a] != v:
                            _match = False
                            break
                    if _match:
                        log.debug("|{0}| >> Match found: {1} | {2}".format(_str_func,mObj.p_nameShort,mCandidate.p_nameShort))
                        
                        mObj.doStore('mirrorControl',mCandidate)
                        mCandidate.doStore('mirrorControl',mObj)                        
                        
                        mCandidate.mirrorIndex = _v
                        
                        _sideMirror = mCandidate.getEnumValueString('mirrorSide')                
                        d_Indices[_sideMirror] = _v#...push it back                
                        ml_cull.remove(mCandidate)
                        md_indicesToControls[_sideMirror][_v] = mCandidate
                        

                        
            for mObj in ml_cull:
                log.debug("|{0}| >> Setting index of unmatched: [{1}] | {2} | {3}".format(_str_func,_v,_side,mObj))
                _side = mObj.getEnumValueString('mirrorSide')                
                i_start = d_Indices[_side]
                _v = i_start+1
                tags_prime = md_cgmTags[mObj]
                
                mObj.mirrorIndex = _v
                d_Indices[_side] = _v#...push it back                
                md_indicesToControls[_side][_v] = mObj
                
                
            
            
            """
            for i,mObj in enumerate(self_keyControls):
                _side = mObj.getEnumValueString('mirrorSide')                
                i_start = d_Indices[_side]
                _v = i_start+1
                log.debug("|{0}| >> Setting index: [{1}] | {2} | {3}".format(_str_func,_v,_side,mObj))
                mObj.mirrorIndex = _v
                d_Indices[_side] = _v#...push it back
                md_indicesToControls[_side][_v] = mObj
                
            for i,mObj in enumerate(mirr_keyControls):
                _side = mObj.getEnumValueString('mirrorSide')                
                i_start = d_Indices[_side]
                _v = i_start+1
                log.debug("|{0}| >> Setting index: [{1}] | {2} | {3}".format(_str_func,_v,_side,mObj))
                mObj.mirrorIndex = _v
                d_Indices[_side] = _v#...push it back
                md_indicesToControls[_side][_v] = mObj
                
            i_running = i_running + max(len_self,len_mirr)
            log.debug("|{0}| >>  i_running: {1}".format(_str_func,i_running))"""
            #d_Indices[d_self['str_side']] = i_running
            #d_Indices[d_mirror['str_side']] = i_running
            
        if progressBar and progressEnd:cgmUI.progressBar_end(progressBar)
        
        if l_processed is not None:l_processed.extend([self,mMirror])
        return md_indicesToControls
        
    
    #return ml_modules,md_data
    
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
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
    
def switchMode(self,mode = 'fkOn', bypassModuleCheck=False):
    try:
        _str_func = 'switchMode'    
        if not bypassModuleCheck:
            log.debug("checking blockModule")        
            mBlockModule = self.p_blockModule
            reload(mBlockModule)
            _blockCall = mBlockModule.__dict__.get('switchMode')
            if _blockCall:
                log.debug("|{0}| >> Found swich mode in block module ".format(_str_func))
                return _blockCall(self,mode)
            
        log.debug("|{0}| >> mode: {1} ".format(_str_func,mode)+ '-'*80)
        log.debug("{0}".format(self))
            
        mRigNull = self.rigNull
        mSettings = mRigNull.settings
        
        _mode = mode.lower()
        
        if _mode == 'fkon':
            mSettings.FKIK = 0
            
        elif _mode == 'ikon':
            mSettings.FKIK = 1
            
        elif _mode in ['aimon','aimoff','aimtofk','aimtoik','aimsnap']:
            if not mRigNull.getMessage('lookAt'):
                return log.warning("|{0}| >> No lookAt/aim setup detected ".format(_str_func))        
            mLookAt = mRigNull.lookAt
            
            if _mode == 'aimon':
                mSettings.blend_aim = 1
            elif _mode == 'aimoff':
                mSettings.blend_aim = 0
                
            elif _mode in ['aimtoik','aimtofk']:
                if _mode == 'aimtoik':
                    if not mLookAt.getMessage('controlIK'):
                        return log.warning("|{0}| >> No IK control on lookAt detected ".format(_str_func))
                    if not mLookAt.getMessage('ikMatch'):
                        return log.warning("|{0}| >> No IK match on lookAt detected ".format(_str_func))
                    mControl = mLookAt.controlIK
                    mMatch = mLookAt.getMessageAsMeta('ikMatch')
                    _v = 1
                else:
                    if not mLookAt.getMessage('controlFK'):
                        return log.warning("|{0}| >> No FK control on lookAt detected ".format(_str_func))
                    if not mLookAt.getMessage('ikMatch'):
                        return log.warning("|{0}| >> No IK match on lookAt detected ".format(_str_func))
                    
                    mControl = mLookAt.controlFK
                    mMatch = mLookAt.getMessageAsMeta('fkMatch')
                    
                    _v = 0
                    
                mBlendTarget = mLookAt.getMessage('drivenBlend',asMeta=True)[0]
                
                mLoc = mMatch.doLoc(fastMode=True)
                #pos = mLookAt.p_position
                
                mSettings.blend_aim = 0
                mSettings.FKIK = _v
                
                SNAP.go(mControl.mNode,mLoc.mNode,position=False)
                #SNAP.aim_atPoint(mControl.mNode,pos,)#vectorUp=MATH.get_obj_vector(mLookAt.mNode,'y+'))
                mControl.select()
                mLoc.delete()
                
            elif _mode == 'aimsnap':
                if not mLookAt.getMessage('switchTarget'):
                    return log.warning("|{0}| >> No IK control on lookAt detected ".format(_str_func))
                
                mSwitchTarget = mLookAt.switchTarget            
                mLoc = mSwitchTarget.doLoc(fastMode=True)
                
                mSettings.blend_aim = 1
                
                SNAP.go(mLookAt.mNode,mLoc.mNode)
                mLookAt.select()        
                mLoc.delete()
            
            
        elif _mode == 'fksnap':
            ml_controls= self.atUtils('controls_get','fk')
            ml_blends = []
            ml_targets = []
            l_pos = []
            l_rot = []
            md_locs = {}
            
            ml_handleJoints = mRigNull.msgList_get('handleJoints')
            
            for i,mObj in enumerate(ml_controls):
                log.debug("|{0}| >> On: {1} ".format(_str_func,mObj))
                
                #if ml_handleJoints:
                #    md_locs[i] = ml_handleJoints[i].doLoc(fastMode = True)
                    
                #else:
                mTarget = mObj.getMessageAsMeta('switchTarget')
                if not mTarget:
                    log.debug("|{0}| >> no switchTarget ".format(_str_func))                    
                    mTarget = mObj.getMessageAsMeta('blendJoint')
                if not mTarget:
                    log.warning("|{0}| >> No target joint found! ".format(_str_func))
                    break
                
                log.debug("|{0}| >> blend: {1} ".format(_str_func,mTarget.mNode))
                
                ml_blends.append(mTarget)
                l_pos.append(mTarget.p_position)
                l_rot.append(mTarget.p_orient)
                md_locs[i] = mTarget.doLoc(fastMode = True)
                
            mSettings.FKIK = 0
            
            for i,mObj in enumerate(ml_controls):
                mLoc = md_locs.get(i)
                if not mLoc:
                    continue
                #mObj.p_position = l_pos[i]
                #mObj.p_orient = l_rot[i]
                SNAP.go(mObj.mNode,mLoc.mNode)
            
            for i,mLoc in md_locs.iteritems():
                mLoc.delete()
                
            for mObj in mRigNull.msgList_get('handleJoints'):
                mObj.resetAttrs(transformsOnly = True)
                
        elif _mode in ['iksnap','iksnapall']:
            if not mRigNull.getMessage('controlIK'):
                return log.debug("|{0}| >> No IK mode detected ".format(_str_func))
            if MATH.is_float_equivalent(mSettings.FKIK,1.0):
                return log.debug("|{0}| >> Already in IK mode ".format(_str_func))
            
            mControlIK = mRigNull.controlIK        
            ml_controls = [mControlIK]
            md_controls = {}        
            md_locs = {}
            if mRigNull.getMessage('controlIKBase'):
                ml_controls.append(mRigNull.controlIKBase)
            if mRigNull.getMessage('controlIKMid'):
                ml_controls.append(mRigNull.controlIKMid)
                
            ml_ikJoints = mRigNull.msgList_get('ikJoints')
            ml_blendJoints = mRigNull.msgList_get('blendJoints')
            
            md_datPostCompare = {}
            for i,mObj in enumerate (ml_blendJoints):
                md_datPostCompare[i] = {}
                md_datPostCompare[i]['pos'] = mObj.p_position
                md_datPostCompare[i]['orient'] = mObj.p_orient
            
            #IKsnapAll ========================================================================
            if _mode == 'iksnapall':
                log.debug("|{0}| >> iksnapall prep...".format(_str_func))
                mSettings.visDirect=True
                ml_rigLocs = []
                ml_rigJoints = mRigNull.msgList_get('rigJoints')
                for i,mObj in enumerate(ml_rigJoints):
                    ml_rigLocs.append( mObj.doLoc(fastMode = True) )
                    
            #Main IK control =====================================================================
            
            #dat we need
            #We need to store the blendjoint target for the ik control or loc it
            for i,mCtrl in enumerate(ml_controls):
                if mCtrl.getMessage('switchTarget'):
                    mCtrl.resetAttrs(transformsOnly = True)
                    md_locs[i] = mCtrl.switchTarget.doLoc(fastMode=True)
                    md_controls[i] = mCtrl
                else:
                    raise ValueError,"mCtrl: {0}  missing switchTarget".format(mCtrl)
            
            mSettings.FKIK = 1
            
            for i,mLoc in md_locs.iteritems():
                SNAP.go(md_controls[i].mNode,mLoc.mNode)
                #mLoc.delete()
            
            for i,v in md_datPostCompare.iteritems():
                mBlend = ml_blendJoints[i]
                dNew = {'pos':mBlend.p_position, 'orient':mBlend.p_orient}
                
                if DIST.get_distance_between_points(md_datPostCompare[i]['pos'], dNew['pos']) > .05:
                    log.warning("|{0}| >> [{1}] pos blend dat off... {2}".format(_str_func,i,mBlend))
                    log.warning("|{0}| >> base: {1}.".format(_str_func,md_datPostCompare[i]['pos']))
                    log.warning("|{0}| >> base: {1}.".format(_str_func,dNew['pos']))
                    
                if not MATH.is_vector_equivalent(md_datPostCompare[i]['orient'], dNew['orient'], places=2):
                    log.warning("|{0}| >> [{1}] orient blend dat off... {2}".format(_str_func,i,mBlend))
                    log.warning("|{0}| >> base: {1}.".format(_str_func,md_datPostCompare[i]['orient']))
                    log.warning("|{0}| >> base: {1}.".format(_str_func,dNew['orient']))                
                    
    
            #IKsnapAll close========================================================================
            if _mode == 'iksnapall':
                log.debug("|{0}| >> iksnapall end...".format(_str_func))
                for i,mObj in enumerate(ml_rigJoints):
                    SNAP.go(mObj.mNode,ml_rigLocs[i].mNode)
            
                return log.warning("mode: {0} | Direct controls vis turned on for mode.".format(_mode))
            
        else:
            raise ValueError,"|{0}| >> unknown mode: {1} | [{2}]".format(_str_func,_mode,self)
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())

def is_upToDate(self,report=False):
    _str_func = ' is_upToDate'
    log.debug("|{0}| >>".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    v_build = self.rigNull.version
    v_blockBuild = self.getBlockModule().__version__
    
    b_upToDate = False
    if v_build == v_blockBuild:
        b_upToDate = True

    if report:
        _short = self.p_nameBase        
        if b_upToDate:
            print("|{0}| >> build current | {1}".format(_short,v_build))
        else:
            print("|{0}| >> OUT OF DATE | buildVersion: {1} | blockVersion: {2}".format(_short,
                                                                          v_build,
                                                                          v_blockBuild))        
    if b_upToDate:
        return True
    return False

    
def get_report(self, mode='rig'):
    _str_func = ' get_report'
    log.debug("|{0}| >>".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    if mode == 'rig':
        mBlockModule = self.getBlockModule()
        v_build = self.rigNull.version
        v_blockBuild = mBlockModule.__version__
        _short = self.p_nameBase
        
        b_upToDate = False
        if v_build == v_blockBuild:
            b_upToDate = True
            
        if b_upToDate:
            print("|{0}| >> build current. ".format(_short))
        else:
            print("|{0}| >> buildVersion: {1} | blockVersion: {2}".format(_short,v_build, v_blockBuild))
        
        
        
    else:
        return log.error("|{0}| >> uknown mode: {1}".format(_str_func,mode))

    return True


def clean_null(self,null='rigNull'):
    _str_func = ' clean_null'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    mNull = self.getMessageAsMeta(null)
    if mNull:
        log.debug("|{0}| >>  null: {1}".format(_str_func,mNull))        
        for mChild in mNull.getChildren(asMeta=True):
            log.debug("|{0}| >>  deleting: {1}".format(_str_func,mChild))
            mChild.delete()
            