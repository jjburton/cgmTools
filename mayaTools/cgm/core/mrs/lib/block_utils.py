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
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.lib.transform_utils as TRANS

def get_side(self):
    _side = 'center' 
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side') 
    return _side

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

def create_templateLoftMesh(self, targets = None, mBaseLoftCurve = None, mTemplateNull = None,
                            uAttr = 'neckControls',baseName = 'test'):
    
    _str_func = 'create_templateLoft'
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')  
            
    _res_body = mc.loft(targets, o = True, d = 3, po = 1, name = baseName )
    mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)

    _inputs = mc.listHistory(mLoft.mNode,pruneDagObjects=True)
    _tessellate = _inputs[0]
    _loftNode = _inputs[1]


    _d = {'format':2,#General
          'polygonType':1,#'quads',
          'uNumber': 1 + ATTR.get(self.mNode, uAttr)}

    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)    

    mLoft.overrideEnabled = 1
    mLoft.overrideDisplayType = 2
    _arg = "{0}.numberOfControlsOut = {1} + 1".format(mBaseLoftCurve.p_nameShort,
                                                      self.getMayaAttrString(uAttr,'short'))

    NODEFACTORY.argsToNodes(_arg).doBuild()

    ATTR.connect("{0}.numberOfControlsOut".format(mBaseLoftCurve.mNode), "{0}.uNumber".format(_tessellate))
    ATTR.connect("{0}.loftSides".format(self.mNode), "{0}.vNumber".format(_tessellate))

    mLoft.p_parent = mTemplateNull
    mLoft.resetAttrs()

    mLoft.doStore('cgmName',self.mNode)
    mLoft.doStore('cgmType','controlsApprox')
    mLoft.doName()

    for n in _tessellate,_loftNode:
        mObj = cgmMeta.validateObjArg(n)
        mObj.doStore('cgmName',self.mNode)
        mObj.doStore('cgmTypeModifier','controlsApprox')
        mObj.doName()            


    #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
    #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;

    mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)

    #Color our stuff...
    RIGGING.colorControl(mLoft.mNode,_side,'main',transparent = True)

    mLoft.inheritsTransform = 0
    for s in mLoft.getShapes(asMeta=True):
        s.overrideDisplayType = 2   

    self.connectChildNode(mLoft.mNode, 'templateLoftMesh', 'block')    
    return mLoft

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def noTransformNull_verify(self):
    if not self.getMessage('noTransformNull'):
        str_prerigNull = mc.group(em=True)
        mNoTransformNull = cgmMeta.validateObjArg(str_prerigNull, mType = 'cgmObject',setClass = True)
        mNoTransformNull.connectParentNode(self, 'rigBlock','noTransformNull') 
        mNoTransformNull.doStore('cgmName', self.mNode)
        mNoTransformNull.doStore('cgmType','noTransformNull')
        mNoTransformNull.doName()


        #mNoTransformNull.p_parent = self.prerigNull
        #mNoTransformNull.resetAttrs()
        #mNoTransformNull.setAttrFlags()
        #mNoTransformNull.inheritsTransform = False
    else:
        mNoTransformNull = self.noTransformNull    

    return mNoTransformNull    

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
    if self.getMessage('noTransformNull'):
        self.noTransformNull.delete()
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

def create_prerigLoftMesh(self, targets = None, mPrerigNull = None,
                          uAttr = 'neckControls', uAttr2 = 'loftSplit',
                          baseName = 'test'):
    
    _str_func = 'create_preRigLoftMesh'
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')  
            
    
    _res_body = mc.loft(targets, o = True, d = 3, po = 1 )
    mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
    _inputs = mc.listHistory(mLoft.mNode,pruneDagObjects=True)

    _tessellate = _inputs[0]
    _loftNode = _inputs[1]

    log.info("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 
    _d = {'format':2,#General
          'polygonType':1,#'quads',
          'uNumber': 1 + len(targets)}

    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)    

    mLoft.overrideEnabled = 1
    mLoft.overrideDisplayType = 2

    mLoft.p_parent = mPrerigNull
    mLoft.resetAttrs()

    mLoft.doStore('cgmName',self.mNode)
    mLoft.doStore('cgmType','shapeApprox')
    mLoft.doName()

    #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
    #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;

    mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)

    #Color our stuff...
    RIGGING.colorControl(mLoft.mNode,_side,'main',transparent = False)

    mLoft.inheritsTransform = 0
    for s in mLoft.getShapes(asMeta=True):
        s.overrideDisplayType = 2    

    #...wire some controls
    _arg = "{0}.out_vSplit = {1} + 1".format(targets[0],
                                                   self.getMayaAttrString(uAttr,'short'))

    NODEFACTORY.argsToNodes(_arg).doBuild()
    #rg = "%s.condResult = if %s.ty == 3:5 else 1"%(str_obj,str_obj)
    _arg = "{0}.out_degree = if {1} == 0:1 else 3".format(targets[0],
                                                          self.getMayaAttrString('loftDegree','short'))

    NODEFACTORY.argsToNodes(_arg).doBuild()    

    ATTR.connect("{0}.out_vSplit".format(targets[0]), "{0}.uNumber".format(_tessellate))
    ATTR.connect("{0}.loftSides".format(self.mNode), "{0}.vNumber".format(_tessellate)) 

    ATTR.connect("{0}.out_degree".format(targets[0]), "{0}.degree".format(_loftNode))    
    #ATTR.copy_to(_loftNode,'degree',self.mNode,'loftDegree',driven = 'source')

    
    for n in _tessellate,_loftNode:
        mObj = cgmMeta.validateObjArg(n)
        mObj.doStore('cgmName',self.mNode)
        mObj.doStore('cgmTypeModifier','prerigMesh')
        mObj.doName()            

    self.connectChildNode(mLoft.mNode, 'prerigLoftMesh', 'block')    
    return mLoft

def create_jointLoft(self, targets = None, mPrerigNull = None,
                     uAttr = 'neckJoints', baseName = 'test'):
    
    _str_func = 'create_jointLoft'
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')  
            
    

    _res_body = mc.loft(targets, o = True, d = 3, po = 1 )
    mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
    _inputs = mc.listHistory(mLoft.mNode,pruneDagObjects=True)

    _tessellate = _inputs[0]
    _loftNode = _inputs[1]
    
    mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)

    log.info("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 
    _d = {'format':2,#General
          'polygonType':1,#'quads',
          'uNumber': 1 + len(targets)}

    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)  
        

    log.info("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 

    mLoft.overrideEnabled = 1
    mLoft.overrideDisplayType = 2

    mLoft.p_parent = mPrerigNull
    mLoft.resetAttrs()

    mLoft.doStore('cgmName',self.mNode)
    mLoft.doStore('cgmType','jointApprox')
    mLoft.doName()

    #Color our stuff...
    RIGGING.colorControl(mLoft.mNode,_side,'main',transparent = False)

    mLoft.inheritsTransform = 0
    for s in mLoft.getShapes(asMeta=True):
        s.overrideDisplayType = 2    

    #...wire some controls
    _arg = "{0}.out_vSplit = {1} + 1 ".format(targets[0],
                                             self.getMayaAttrString(uAttr,'short'))

    NODEFACTORY.argsToNodes(_arg).doBuild()
    
    #rg = "%s.condResult = if %s.ty == 3:5 else 1"%(str_obj,str_obj)
    #NODEFACTORY.argsToNodes(_arg).doBuild()    

    ATTR.connect("{0}.out_vSplit".format(targets[0]), "{0}.uNumber".format(_tessellate))  

    for n in _tessellate,_loftNode:
        mObj = cgmMeta.validateObjArg(n)
        mObj.doStore('cgmName',self.mNode)
        mObj.doStore('cgmTypeModifier','jointApprox')
        mObj.doName()            

    self.connectChildNode(mLoft.mNode, 'jointLoftMesh', 'block')    
    return mLoft

def create_jointLoftBAK(self, targets = None, mPrerigNull = None,
                     uAttr = 'neckJoints', baseName = 'test'):
    
    _str_func = 'create_jointLoft'
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')  
            
    
    _res_body = mc.loft(targets, o = True, d = 3, po =3 )

    mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
    _inputs = mc.listHistory(mLoft.mNode,pruneDagObjects=True)
    _tessellate = _inputs[0]
    _loftNode = _inputs[1]

    log.info("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 

    mLoft.overrideEnabled = 1
    mLoft.overrideDisplayType = 2

    mLoft.p_parent = mPrerigNull
    mLoft.resetAttrs()

    mLoft.doStore('cgmName',self.mNode)
    mLoft.doStore('cgmType','jointApprox')
    mLoft.doName()

    #Color our stuff...
    RIGGING.colorControl(mLoft.mNode,_side,'main',transparent = False)

    mLoft.inheritsTransform = 0
    for s in mLoft.getShapes(asMeta=True):
        s.overrideDisplayType = 2    

    #...wire some controls
    _arg = "{0}.out_vSplit = {1} + 1 ".format(targets[0],
                                             self.getMayaAttrString(uAttr,'short'))

    NODEFACTORY.argsToNodes(_arg).doBuild()
    
    #rg = "%s.condResult = if %s.ty == 3:5 else 1"%(str_obj,str_obj)
    #NODEFACTORY.argsToNodes(_arg).doBuild()    

    ATTR.connect("{0}.out_vSplit".format(targets[0]), "{0}.uNumber".format(_tessellate))  

    for n in _tessellate,_loftNode:
        mObj = cgmMeta.validateObjArg(n)
        mObj.doStore('cgmName',self.mNode)
        mObj.doStore('cgmTypeModifier','jointApprox')
        mObj.doName()            

    self.connectChildNode(mLoft.mNode, 'jointLoftMesh', 'block')    
    return mLoft

#=============================================================================================================
#>> Rig
#=============================================================================================================


#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def skeleton_getCreateDict(self):
    """
    Data checker to see the skeleton create dict for a given blockType regardless of what's loaded

    :parameters:
        blockType(str) | rigBlock type

    :returns
        dict
    """
    _short = self.mNode
    _str_func = 'get_skeletonCreateDict ( {0} )'.format(_short)
    mModule = self.moduleTarget    

    _mod = self.getBlockModule()
    if not _mod:
        log.warning("|{0}| >> No module found for: {1}".format(_str_func,blockType))
        return False       
    

    #Validate mode data -------------------------------------------------------------------------
    try:_d_skeletonSetup = _mod.d_skeletonSetup
    except:_d_skeletonSetup = {}

    _mode = _d_skeletonSetup.get('mode',False)
    _targetsMode = _d_skeletonSetup.get('targetsMode','msgList')
    _targetsCall = _d_skeletonSetup.get('targets',False)
    _helperUp = _d_skeletonSetup.get('helperUp','y+')
    _countAttr = _d_skeletonSetup.get('countAttr','numberJoints')
    
    _l_targets = []

    log.debug("|{0}| >> mode: {1} | targetsMode: {2} | targetsCall: {3}".format(_str_func,_mode,_targetsMode,_targetsCall))

    #...get our targets
    if _targetsMode == 'msgList':
        _l_targets = ATTR.msgList_get(_short, _targetsCall)
    elif _targetsMode == 'msg':
        _l_targets = ATTR.get_message(_short, _targetsCall)
    elif _targetsMode == 'self':
        _l_targets = [_short]
    elif _targetsMode == 'prerigHandles':
        _ml_rigHandles = self.msgList_get('prerigHandles',asMeta = True)
        if not _ml_rigHandles:
            raise ValueError, "No rigHandles. Check your state"            
    
        #_ml_controls = [self] + _ml_rigHandles
    
        for i,mObj in enumerate(_ml_rigHandles):
            log.info("|{0}| >>  {1} | {2}".format(_str_func,i,mObj.mNode))
            if mObj.getMessage('jointHelper'):
                _l_targets.append(mObj.jointHelper.mNode)
            else:
                _l_targets.append(mObj.mNode)        
    else:
        raise ValueError,"targetsMode: {0} is not implemented".format(_targetsMode)
    
    if not _l_targets:
        log.error("|{0}| >> mode: {1} | targetsMode: {2} | targetsCall: {3}".format(_str_func,_mode,_targetsMode,_targetsCall))
        raise ValueError, "No targets found. Check your settings"
    
    log.debug("|{0}| >> Targets: {1}".format(_str_func,_l_targets))
    #pprint.pprint(vars())
    
    """
    _helperOrient = ATTR.get_message(_short,'orientHelper')
    if not _helperOrient:
        log.info("|{0}| >> No helper orient. Using root.".format(_str_func))   
        _axisWorldUp = MATH.get_obj_vector(_short,_helperUp)                 
    else:
        log.info("|{0}| >> Found orientHelper: {1}".format(_str_func,_helperOrient))            
        _axisWorldUp = MATH.get_obj_vector(_helperOrient[0], _helperUp)
    log.debug("|{0}| >> axisWorldUp: {1}".format(_str_func,_axisWorldUp))  
    """

    _joints = ATTR.get(_short,_countAttr)

    #...get our positional data
    _d_res = {}

    if _mode in ['vectorCast','curveCast']:
        if _mode == 'vectorCast':
            _p_start = POS.get(_l_targets[0])
            _p_top = POS.get(_l_targets[1])    
            _l_pos = get_posList_fromStartEnd(_p_start,_p_top,_joints)   
        elif _mode == 'curveCast':
            import cgm.core.lib.curve_Utils as CURVES
            _crv = CURVES.create_fromList(targetList = _l_targets)
            _l_pos = CURVES.returnSplitCurveList(_crv,_joints)
            mc.delete(_crv)
        _d_res['jointCount'] = _joints
        _d_res['helpers'] = {#'orient':_helperOrient,
                             'targets':_l_targets}
    elif _mode == 'handle':
        _l_pos = [POS.get(_l_targets[0])]
        _d_res['targets'] = _l_targets           
    else:
        raise ValueError,"mode: {0} is not implemented".format(_mode)                

    _d_res['positions'] = _l_pos
    _d_res['mode'] = _mode
    #_d_res['worldUpAxis'] = _axisWorldUp        

    #pprint.pprint(_d_res)
    return _d_res





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

def skeleton_buildRigChain2(self):
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

def skeleton_pushSettings(ml_chain, orientation = 'zyx', side = 'right',
                          d_rotateOrders = {}, d_preferredAngles = {}, d_limits = {}):
    _str_func = '[{0}] > '.format('skeleton_pushSettings')
    
    
    for mJnt in ml_chain:
        _key = mJnt.getMayaAttr('cgmName',False)
        
        _rotateOrderBuffer = d_rotateOrders.get(_key,False)
        _limitBuffer = d_limits.get(_key,False)
        _preferredAngles = d_preferredAngles.get(_key,False)
        
        if _rotateOrderBuffer:
            log.info("|{0}| >> found rotate order data on {1}:{2}".format(_str_func,_key,_rotateOrderBuffer))  
            TRANS.rotateOrder_set(mJnt.mNode, _rotateOrderBuffer, True)
            
        if _preferredAngles:
            log.info("|{0}| >> found preferred angle data on {1}:{2}".format(_str_func,_key,_preferredAngles))              
            #log.info("preferred angles(%s)>>> %s"%(i_jnt.cgmName,__d_preferredAngles__.get(i_jnt.cgmName)))
            for i,v in enumerate(_preferredAngles):	
                if side.lower() == 'right':#negative value
                    mJnt.__setattr__('preferredAngle{0}'.format(orientation[i].upper()),-v)				
                else:
                    mJnt.__setattr__('preferredAngle{0}'.format(orientation[i].upper()),v)
        
        if _limitBuffer:
            log.info("|{0}| >> found limit data on {1}:{2}".format(_str_func,_key,_limitBuffer))              
            raise Exception,"Limit Buffer not implemented"
   


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
        

