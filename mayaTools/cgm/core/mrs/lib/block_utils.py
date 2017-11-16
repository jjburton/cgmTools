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
                          polyType = 'mesh',
                          baseName = 'test'):
    
    _str_func = 'create_preRigLoftMesh'
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')  
            
    
    if polyType == 'mesh':
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
    else:
        _res_body = mc.loft(targets, o = True, d = 3, po = 0 )
        mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)        

    mLoft.overrideEnabled = 1
    mLoft.overrideDisplayType = 2

    mLoft.p_parent = mPrerigNull
    mLoft.resetAttrs()

    mLoft.doStore('cgmName',self.mNode)
    mLoft.doStore('cgmType','shapeApprox')
    mLoft.doName()

    #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
    #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;

    #mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)

    #Color our stuff...
    RIGGING.colorControl(mLoft.mNode,_side,'main',transparent = True)

    mLoft.inheritsTransform = 0
    for s in mLoft.getShapes(asMeta=True):
        s.overrideDisplayType = 2    
        
    if polyType == 'mesh':
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
l_pivotOrder = ['center','back','front','left','right']

def pivots_buildShapes(self, mPivotHelper = None, mRigNull = None):
    """
    Builder of shapes for pivot setup. Excpects to find pivotHelper on block
    
    :parameters:
        self(cgmRigBlock)
        mRigNull(cgmRigNull) | if none provided, tries to find it

    :returns
        dict
    """
    _short = self.mNode
    _str_func = 'pivots_buildShapes ( {0} )'.format(_short)
    
    if mRigNull is None:
        mRigNull = self.moduleTarget.rigNull
        
    if mPivotHelper is None:
        if not self.getMessage('pivotHelper'):
            raise ValueError,"|{0}| >> No pivots helper found. mBlock: {1}".format(_str_func,self)
        mPivotHelper = self.pivotHelper
        
    """
    mBlockModule = self.getBlockModule()
    if not mBlockModule:
        log.warning("|{0}| >> No module found for: {1}".format(_str_func,blockType))
        return False       
    
    log.info("|{0}| >> ...".format(_str_func))
    """
    
    for a in l_pivotOrder:
        str_a = 'pivot' + a.capitalize()
        if mPivotHelper.getMessage(str_a):
            log.info("|{0}| >> Found: {1}".format(_str_func,str_a))
            mPivot = mPivotHelper.getMessage(str_a,asMeta=True)[0].doDuplicate(po=False)
            mRigNull.connectChildNode(mPivot,str_a,'rigNull')#Connect    
            mPivot.parent = False
    return True
                
def pivots_setup(self, mControl = None, mRigNull = None, pivotResult = None, rollSetup = 'default', **kws):
    """
    Builder for pivot setup
    
    :parameters:
        self(cgmRigBlock)
        mControl (cgmObject
        mRigNull(cgmRigNull) | if none provided, tries to find it

    :returns
        dict
    """
    _short = self.mNode
    _str_func = 'pivots_setup ( {0} )'.format(_short)
    
    _start = time.clock()
    
    _side = get_side(self)
    
    
    d_strCaps = {'front':kws.get('front','toe').capitalize(),
                 'back':kws.get('back','heel').capitalize(),
                 'left':kws.get('left','inner').capitalize(),
                 'right':kws.get('right','outer').capitalize(),
                 'center':kws.get('center','ball').capitalize()}
    
    if mRigNull is None:
        mRigNull = self.moduleTarget.rigNull
        
    if not mControl:
        mControl = mRigNull.handle
    else:
        mControl = cgmMeta.validateObjArg(mControl,'cgmObject')
        
    mPivotResult = cgmMeta.validateObjArg(pivotResult,'cgmObject',noneValid=True)
    
        
    #Find our pivots and create grups ========================================================================
    d_pivots = {}
    #d_twistGroups = {}
    d_drivenGroups = {}
    mLastParent = mControl
    for a in l_pivotOrder:
        str_a = 'pivot' + a.capitalize()
        mPivot = mRigNull.getMessage(str_a,asMeta=True)
        if mPivot:
            log.info("|{0}| >> Found: {1}".format(_str_func,str_a))
            if mPivot[0].getMessage('masterGroup'):
                mPivot = mPivot[0]
                d_pivots[a] = mPivot
                
                mPivot.rotateOrder = 2
                mPivot.masterGroup.parent = mLastParent
                mDrivenGroup = mPivot.doGroup(False, False, asMeta=True)
                mDrivenGroup.addAttr('cgmType','pivotDriver')
                
                mPivot.connectChildNode(mDrivenGroup,'drivenGroup','handle')#Connect    
                
                mDrivenGroup.doName()
                d_drivenGroups[a] = mDrivenGroup
                mDrivenGroup.parent = mPivot
                
                mLastParent = mDrivenGroup
                
                
                continue
            log.error("|{0}| >> No master group on pivot. Wrong stage: {1}".format(_str_func,str_a))
        
    if not d_pivots:
        raise ValueError,"|{0}| >> No pivots found. mBlock: {1}".format(_str_func,self)
    
    if mPivotResult:
        mPivotResult.parent = mLastParent    
    
    #pprint.pprint(vars())
    #Logic ======================================================================================
    if d_drivenGroups.get('center'):
        b_centerOK = True
    else:
        log.error("|{0}| >> Missing center pivot setup info...".format(_str_func))        
        b_centerOK = False
        
    if d_drivenGroups.get('front') and d_drivenGroups.get('back'):
        b_rollOK = True
    else:
        log.error("|{0}| >> Missing roll setup...".format(_str_func))                
        b_rollOK = False
        
    if d_drivenGroups.get('left') and d_drivenGroups.get('right'):
        b_bankOK = True
    else:
        log.error("|{0}| >> Missing bank setup...".format(_str_func))                
        b_bankOK = False
        
    
    
    #Attributes ...---------------------------------------------------------------------------------------------
    
    log.info("|{0}| >> Attributes ...".format(_str_func))    

    #Roll ===================================================================================================
    if b_rollOK:
        mPlug_roll = cgmMeta.cgmAttr(mControl,'roll',attrType='float',defaultValue = 0,keyable = True)
        
        
        if rollSetup in ['human','ik','foot']:
            
            log.info("|{0}| >> foot setup ...".format(_str_func))
            mToe = d_drivenGroups['front']
            mHeel = d_drivenGroups['back'] = d_drivenGroups['back']        
            mPlug_toeLift = cgmMeta.cgmAttr(mControl,'toeLift',attrType='float',initialValue = 35, defaultValue = 35,keyable = True)
            mPlug_toeStaighten = cgmMeta.cgmAttr(mControl,'toeStaighten',attrType='float',initialValue = 65,defaultValue = 70,keyable = True)
        
            #Heel setup ----------------------------------------------------------------------------------------
            log.info("|{0}| >> Heel ...".format(_str_func))        
            mPlug_heelClampResult = cgmMeta.cgmAttr(mControl,'result_clamp_heel',attrType='float',keyable = False,hidden=True)
        
            #Setup the heel roll
            #Clamp
        
            _arg = "{0} = clamp({1},0,{2})".format(mPlug_heelClampResult.p_combinedShortName,
                                                   mPlug_roll.p_combinedShortName,
                                                   mPlug_roll.p_combinedShortName)
        
            log.info("|{0}| >> heel arg: {1}".format(_str_func,_arg))        
            NODEFACTORY.argsToNodes(_arg).doBuild()
        
            #Inversion
            mPlug_heelClampResult.doConnectOut("%s.rx"%(d_drivenGroups['back'].mNode))        
        
            #Ball setup ----------------------------------------------------------------------------------------------
            """
                Schleifer's
                ball_loc.rx = (linstep(0,$toeLift, $roll) * (1-(linstep( $toeLift, $toeStraight, $roll))) * $roll;
                        ballToeLiftRoll        md   ( pma   toeToeStraightRoll                    md  
                            1               4       3             2                            5
                """
            log.info("|{0}| >> ball ...".format(_str_func))    
        
        
            mPlug_ballToeLiftRollResult = cgmMeta.cgmAttr(mControl,'result_range_ballToeLiftRoll',attrType='float',keyable = False,hidden=True)
            mPlug_toeStraightRollResult = cgmMeta.cgmAttr(mControl,'result_range_toeStraightRoll',attrType='float',keyable = False,hidden=True)
            mPlug_oneMinusToeResultResult = cgmMeta.cgmAttr(mControl,'result_pma_one_minus_toeStraitRollRange',attrType='float',keyable = False,hidden=True)
            mPlug_ball_x_toeResult = cgmMeta.cgmAttr(mControl,'result_md_roll_x_toeResult',attrType='float',keyable = False,hidden=True)
            mPlug_all_x_rollResult = cgmMeta.cgmAttr(mControl,'result_md_all_x_rollResult',attrType='float',keyable = False,hidden=True)
        
            arg1 = "%s = setRange(0,1,0,%s,%s)"%(mPlug_ballToeLiftRollResult.p_combinedShortName,
                                                 mPlug_toeLift.p_combinedShortName,
                                                 mPlug_roll.p_combinedShortName)
            arg2 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeStraightRollResult.p_combinedShortName,
                                                  mPlug_toeLift.p_combinedShortName,
                                                  mPlug_toeStaighten.p_combinedShortName,
                                                  mPlug_roll.p_combinedShortName)
            arg3 = "%s = 1 - %s"%(mPlug_oneMinusToeResultResult.p_combinedShortName,
                                  mPlug_toeStraightRollResult.p_combinedShortName)
        
            arg4 = "%s = %s * %s"%(mPlug_ball_x_toeResult.p_combinedShortName,
                                   mPlug_oneMinusToeResultResult.p_combinedShortName,
                                   mPlug_ballToeLiftRollResult.p_combinedShortName)
        
            arg5 = "%s = %s * %s"%(mPlug_all_x_rollResult.p_combinedShortName,
                                   mPlug_ball_x_toeResult.p_combinedShortName,
                                   mPlug_roll.p_combinedShortName)
        
            for arg in [arg1,arg2,arg3,arg4,arg5]:
                NODEFACTORY.argsToNodes(arg).doBuild()
            
            #>>>Josh - resolve getting this back in and where it need to be in heirarchy
            #mPlug_all_x_rollResult.doConnectOut("%s.r%s"%(mi_jointBallPivot.mNode,orientation[2]))
        
        
            #Toe setup -----------------------------------------------------------------------------------------------
            """
                Schleifer's
                toe_loc.rotateX = linstep($toeLift, $toeStraight,$roll) * $roll;
                              setRange                           md
                             1                                2
                """
            log.info("|{0}| >> Toe ...".format(_str_func))        
        
            mPlug_toeRangeResult = cgmMeta.cgmAttr(mControl,'result_range_toeLiftStraightRoll',attrType='float',keyable = False,hidden=True)
            mPlug_toe_x_rollResult = cgmMeta.cgmAttr(mControl,'result_md_toeRange_x_roll',attrType='float',keyable = False,hidden=True)
        
            arg1 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeRangeResult.p_combinedShortName,
                                                  mPlug_toeLift.p_combinedShortName,
                                                  mPlug_toeStaighten.p_combinedShortName,                                         
                                                  mPlug_roll.p_combinedShortName)
            arg2 = "%s = %s * %s"%(mPlug_toe_x_rollResult.p_combinedShortName,
                                   mPlug_toeRangeResult.p_combinedShortName,
                                   mPlug_roll.p_combinedShortName)
            for arg in [arg1,arg2]:
                NODEFACTORY.argsToNodes(arg).doBuild()    
        
            mPlug_toe_x_rollResult.doConnectOut("%s.rx"%(mToe.mNode))    
        else:
            log.info("|{0}| >> StandardRoll ...".format(_str_func))
            
            #Roll setup -----------------------------------------------------------------------------------------------
            """
            Schleifer's
            outside_loc.rotateZ = min($side,0);
            clamp1
            inside_loc.rotateZ = max(0,$side);
            clamp2
            """   
            log.info("|{0}| >> Bank ...".format(_str_func))        
            mToe = d_drivenGroups['front']
            mHeel = d_drivenGroups['back']
            
            mPlug_toeRollResult = cgmMeta.cgmAttr(mControl,'result_clamp_toeRoll',attrType='float',keyable = False,hidden=True)
            mPlug_heelRollResult = cgmMeta.cgmAttr(mControl,'result_clamp_heelRoll',attrType='float',keyable = False,hidden=True)
    
            arg1 = "%s = clamp(-360,0,%s)"%(mPlug_heelRollResult.p_combinedShortName,                                  
                                            mPlug_roll.p_combinedShortName)
            arg2 = "%s = clamp(0,360,%s)"%(mPlug_toeRollResult.p_combinedShortName,
                                           mPlug_roll.p_combinedShortName)
            for arg in [arg1,arg2]:
                NODEFACTORY.argsToNodes(arg).doBuild()   
    
            mPlug_toeRollResult.doConnectOut("%s.rx"%(mToe.mNode))
            mPlug_heelRollResult.doConnectOut("%s.rx"%(mHeel.mNode))
            
    if b_centerOK:        
        mPlug_bankBall = cgmMeta.cgmAttr(mControl,'centerBank',attrType='float',defaultValue = 0,keyable = True)
        mPlug_rollBall = cgmMeta.cgmAttr(mControl,'centerRoll',attrType='float',defaultValue = 0,keyable = True)    
        
        #Ball roll ....
        mDriven = d_drivenGroups['center']
        if _side in ['right']:
            str_arg = "{0}.rx = -{1}".format(mDriven.mNode,
                                             mPlug_rollBall.p_combinedShortName)
            log.info("|{0}| >> Right arg: {1}".format(_str_func,str_arg))        
            NODEFACTORY.argsToNodes(str_arg).doBuild()
        else:
            mPlug_rollBall.doConnectOut("{0}.rx".format(mDriven.mNode))         
            
    
    #Spins ===================================================================================================
    log.info("|{0}| >> Spin ...".format(_str_func))
    
    d_mPlugSpin = {}
    for k in d_drivenGroups.keys():
        d_mPlugSpin[k] = cgmMeta.cgmAttr(mControl,'spin{0}'.format(d_strCaps[k]),attrType='float',defaultValue = 0,keyable = True)
        
    for k in d_drivenGroups.keys():
        str_key = d_strCaps[k]
        mPlug = d_mPlugSpin[k]
        mDriven = d_drivenGroups[k]
        log.info("|{0}| >> Spin {1} setup".format(_str_func,str_key))        
        
        if _side in ['right']:
            str_arg = "{0}.ry = -{1}".format(mDriven.mNode,
                                             mPlug.p_combinedShortName)
            log.info("|{0}| >> Right arg: {1}".format(_str_func,str_arg))        
            NODEFACTORY.argsToNodes(str_arg).doBuild()
        else:
            mPlug.doConnectOut("{0}.ry".format(mDriven.mNode))     
            
    
    if b_bankOK:#Bank ===================================================================================================
        log.info("|{0}| >> Bank ...".format(_str_func))
        mPlug_bank = cgmMeta.cgmAttr(mControl,'bank',attrType='float',defaultValue = 0,keyable = True)
        
        mPlug_outerResult = cgmMeta.cgmAttr(mControl,'result_clamp_outerBank',attrType='float',keyable = False,hidden=True)
        mPlug_innerResult = cgmMeta.cgmAttr(mControl,'result_clamp_innerBank',attrType='float',keyable = False,hidden=True)
        
        if _side in ['right']:
            mDrivenOutr = d_drivenGroups['right']
            mDrivenInner =d_drivenGroups['left']
            
            arg1 = "%s = clamp(-360,0,%s)"%(mPlug_innerResult.p_combinedShortName,                                  
                                            mPlug_bank.p_combinedShortName)
            arg2 = "%s = clamp(0,360,%s)"%(mPlug_outerResult.p_combinedShortName,
                                           mPlug_bank.p_combinedShortName)
            for arg in [arg1,arg2]:
                NODEFACTORY.argsToNodes(arg).doBuild()           
            
            str_bankDriverOutr = "%s.rz = -%s"%(mDrivenOutr.mNode,
                                             mPlug_outerResult.p_combinedShortName)
            str_bankDriverInnr = "%s.rz = -%s"%(mDrivenInner.mNode,
                                                mPlug_innerResult.p_combinedShortName)    
            for arg in [str_bankDriverInnr,str_bankDriverOutr]:
                NODEFACTORY.argsToNodes(arg).doBuild()
        else:     
            mDrivenOutr = d_drivenGroups['left']
            mDrivenInner =d_drivenGroups['right']
            
            arg1 = "%s = clamp(-360,0,%s)"%(mPlug_outerResult.p_combinedShortName,                                  
                                            mPlug_bank.p_combinedShortName)
            arg2 = "%s = clamp(0,360,%s)"%(mPlug_innerResult.p_combinedShortName,
                                           mPlug_bank.p_combinedShortName)
            for arg in [arg1,arg2]:
                NODEFACTORY.argsToNodes(arg).doBuild()           
            
            mPlug_outerResult.doConnectOut("%s.rz"%(mDrivenOutr.mNode))
            mPlug_innerResult.doConnectOut("%s.rz"%(mDrivenInner.mNode))        
    
    if b_centerOK:#Ball bank ....
        mDriven = d_drivenGroups['center']
        if _side in ['right']:
            str_arg = "{0}.rz = -{1}".format(mDriven.mNode,
                                             mPlug_bankBall.p_combinedShortName)
            log.info("|{0}| >> Right arg: {1}".format(_str_func,str_arg))        
            NODEFACTORY.argsToNodes(str_arg).doBuild()
        else:
            mPlug_bankBall.doConnectOut("{0}.rz".format(mDriven.mNode))         
    


    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    
    
#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def skeleton_getCreateDict(self, count = None):
    """
    Data checker to see the skeleton create dict for a given blockType regardless of what's loaded

    :parameters:
        blockType(str) | rigBlock type
        count(int) | Overload for count

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

    if count:
        _joints = count
    else:
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


def skeleton_buildDuplicateChain(sourceJoints = None, modifier = 'rig', connectToModule = False, connectAs = 'rigJoints', connectToSource = 'skinJoint', singleMode = False, cgmType = None, indices  = []):
    _str_func = 'skeleton_buildDuplicateChain'
    
    start = time.clock()
    
    if indices:
        log.info("|{0}| >> Indices arg: {1}".format(_str_func, indices))          
        l_buffer = []
        for i in indices:
            l_buffer.append(sourceJoints[i])
        sourceJoints = l_buffer    
    
    ml_source = cgmMeta.validateObjListArg(sourceJoints,mayaType=['joint'],noneValid=False)
    
    if connectToModule:
        #mRigNull = self.moduleTarget.rigNull
    
        #Get our segment joints
        if singleMode:
            l_jointsExist = connectToModule.getMessage(connectAs)
        else:
            l_jointsExist = connectToModule.msgList_get(connectAs,asMeta = False, cull = True)
        
        if l_jointsExist:
            log.info("|{0}| >> Deleting existing {1} chain".format(_str_func, modifier))  
            mc.delete(l_jointsExist)

    l_joints = mc.duplicate([i_jnt.mNode for i_jnt in ml_source],po=True,ic=True,rc=True)
    
    ml_joints = [cgmMeta.cgmObject(j) for j in l_joints]


    for i,mJnt in enumerate(ml_joints):
        if modifier is not None:
            mJnt.addAttr('cgmTypeModifier', modifier,attrType='string',lock=True)
        if cgmType is not None:
            mJnt.addAttr('cgmType', cgmType,attrType='string',lock=True)
            
        #l_joints[i] = mJnt.mNode
        if connectToSource:
            mJnt.connectChildNode(ml_joints[i].mNode,connectToSource,'{0}Joint'.format(modifier))#Connect	    
        
        if mJnt.hasAttr('scaleJoint'):
            if mJnt.scaleJoint in ml_skinJoints:
                int_index = ml_source.index(mJnt.scaleJoint)
                mJnt.connectChildNode(ml_source[int_index],'scaleJoint','sourceJoint')#Connect

    #Name loop
    ml_joints[0].parent = False
    for mJnt in ml_joints:
        mJnt.doName()	
        
    if connectToModule:
        if singleMode:
            connectToModule.connectChildNode(ml_joints[0],connectAs,'rigNull')
        else:
            connectToModule.msgList_connect(connectAs, ml_joints,'rigNull')#connect	
        
    log.debug("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	
    
    return ml_joints


def skeleton_connectToParent(self):
    _short = self.mNode
    _str_func = 'skeleton_connectToParent ( {0} )'.format(_short)
    
    mModule = self.moduleTarget
    l_moduleJoints = mModule.rigNull.msgList_get('moduleJoints',asMeta = False)
    
    if not mModule.moduleParent:
        log.info("|{0}| >> No moduleParent".format(_str_func))
        ml_parentBlocks = self.getBlockParents()
        
        if ml_parentBlocks:
            if ml_parentBlocks[0].blockType == 'master' and ml_parentBlocks[0].moduleTarget.getMessage('rootJoint'):
                log.info("|{0}| >> Root joint on master found".format(_str_func))           
                TRANS.parent_set(l_moduleJoints[0], ml_parentBlocks[0].moduleTarget.getMessage('rootJoint')[0])
                return True
    raise ValueError,"Finish this..."
    
    return
    ml_parentBlocks = self.getParentBlocks()
    if ml_parentBlocks and ml_parentBlocks[0].blockType == 'master' and ml_parentBlocks[0].moduleTarget.getMessage('rootJoint'):
        log.info("|{0}| >> Deleting existing {1} chain".format(_str_func, modifier))  
        
        
        
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
    ml_skinJoints = _mRigNull.msgList_get('moduleJoints')
    
    if l_rigJointsExist:
        log.info("|{0}| >> Deleting existing rig chain".format(_str_func))  
        mc.delete(l_rigJointsExist)

    l_rigJoints = mc.duplicate([i_jnt.mNode for i_jnt in _mRigNull.msgList_get('moduleJoints')],po=True,ic=True,rc=True)
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
   

def skeleton_getHandleChain(self, typeModifier = None):
    """
    Generate a handle chain of joints if none exists, otherwise return existing
    """
    _short = self.mNode
    _str_func = 'skeleton_getHandleChain [{0}]'.format(_short)
    start = time.clock()	
    
    mRigNull = self.moduleTarget.rigNull
    ml_fkJoints = mRigNull.msgList_get('fkJoints')
    
    if not ml_fkJoints:
        log.info("|{0}| >> Generating handleJoints".format(_str_func))
        
        ml_prerigHandles = self.msgList_get('prerigHandles',asMeta = True)
        if not ml_prerigHandles:
            raise ValueError,"No prerigHandles connected"
        
        mOrientHelper = ml_prerigHandles[0].orientHelper
        _d = skeleton_getCreateDict(self)
        pprint.pprint(_d)
        ml_fkJoints = COREJOINTS.build_chain(targetList=_d['helpers']['targets'],
                                           axisAim='z+',
                                           axisUp='y+',
                                           parent=True,
                                           worldUpAxis= mOrientHelper.getAxisVector('z-'))
        if typeModifier:
            for mJnt in ml_fkJoints:
                mJnt.addAttr('cgmTypeModifier',typeModifier,attrType='string',lock=True)
                mJnt.addAttr('cgmType','frame',attrType='string',lock=True)                
                mJnt.doName()
                
        ml_fkJoints[0].p_parent = False
    else:
        log.info("|{0}| >> Found fkJoints".format(_str_func))
        
    log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	
    return ml_fkJoints


def skeleton_buildHandleChain(self,typeModifier = 'handle',connectNodesAs = False,clearType = False): 
    _short = self.mNode
    _str_func = 'skeleton_buildHandleChain [{0}]'.format(_short)
    start = time.clock()
    
    mRigNull = self.moduleTarget.rigNull
    ml_handleJoints = skeleton_getHandleChain(self,typeModifier)
    ml_handleChain = []
    
    if typeModifier and typeModifier.lower() not in ['fk']:
        for i,mHandle in enumerate(ml_handleJoints):
            mNew = mHandle.doDuplicate()
            if ml_handleChain:mNew.parent = ml_handleChain[-1]#if we have data, parent to last
            else:mNew.parent = False
            if typeModifier or clearType:
                if typeModifier:mNew.addAttr('cgmTypeModifier',typeModifier,attrType='string',lock=True)
                if clearType:
                    try:ATTR.delete(mNew.mNode, 'cgmType')
                    except:pass
                mNew.doName()
            ml_handleChain.append(mNew)
    else:
        ml_handleChain = ml_handleJoints

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


def prerig_getHandleTargets(self):
    """
    
    """
    _short = self.mNode
    _str_func = 'prerig_getHandleTargets [{0}]'.format(_short)
    start = time.clock()
    
    ml_handles = self.msgList_get('prerigHandles',asMeta = True)
    if not ml_handles:
        raise ValueError,"No prerigHandles connected"
    
    for i,mHandle in enumerate(ml_handles):
        if mHandle.getMessage('jointHelper'):
            log.debug("|{0}| >> Found jointHelper on : {1}".format(_str_func, mHandle.mNode))                    
            ml_handles[i] = mHandle.jointHelper
            
    log.debug("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	
    return ml_handles
        

