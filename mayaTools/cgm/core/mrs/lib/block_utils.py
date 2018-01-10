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
from cgm.core import cgm_PuppetMeta as PUPPETMETA
from cgm.core import cgm_RigMeta as RIGMETA

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.mrs.lib import general_utils as BLOCKGEN
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.lib.transform_utils as TRANS
from cgm.core.lib import nameTools as NAMETOOLS

#=============================================================================================================
#>> Queries
#=============================================================================================================
def get_side(self):
    _side = 'center' 
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side') 
    return _side

def get_sideMirror(self):
    _side = get_side(self)
    if _side == 'left':return 'right'
    elif _side == 'right':return 'left'
    return False

def verify_blockAttrs(self, blockType = None, forceReset = False, queryMode = True):
    """
    Verify the attributes of a given block type
    
    force - overrides the excpetion on a failure
    """
    try:
        _str_func = 'verify_blockAttrs'
        _short = self.mNode
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        if queryMode:
            log.debug("|{0}| >> QUERY MODE".format(_str_func,self))
        if blockType is None:
            mBlockModule = self.p_blockModule
        else:
            raise NotImplementedError,"Haven't implemented blocktype changing..."
        
        try:d_attrsFromModule = mBlockModule.d_attrsToMake
        except:d_attrsFromModule = {}
        
        d_defaultSettings = copy.copy(BLOCKSHARE.d_defaultAttrSettings)
    
        try:d_defaultSettings.update(mBlockModule.d_defaultSettings)
        except:pass
    
        try:_l_msgLinks = mBlockModule._l_controlLinks
        except:_l_msgLinks = []
    
        _d = copy.copy(BLOCKSHARE.d_defaultAttrs)     
    
        _l_standard = mBlockModule.__dict__.get('l_attrsStandard',[])
        log.debug("|{0}| >> standard: {1} ".format(_str_func,_l_standard))                        
        for k in _l_standard:
            if k in BLOCKSHARE._d_attrsTo_make.keys():
                _d[k] = BLOCKSHARE._d_attrsTo_make[k]
    
        for k,v in d_attrsFromModule.iteritems():
            if k in _d.keys():
                log.warning("|{0}| >> key: {1} already in to create list of attributes from default. | blockType: {2}".format(_str_func,k,blockType))                
            else:
                _d[k] = v
    
        if _l_msgLinks:
            for l in _l_msgLinks:
                _d[l] = 'messageSimple'
    
        #cgmGEN.walk_dat(_d,_str_func + " '{0}' attributes to verify".format(blockType))
        #cgmGEN.walk_dat(d_defaultSettings,_str_func + " '{0}' defaults".format(blockType))
        
        if queryMode:
            return _d,d_defaultSettings
        
        
        #This is the verify part...
        _keys = _d.keys()
        _keys.sort()
        #for a,t in self._d_attrsToVerify.iteritems():
        for a in _keys:
            try:
                v = d_defaultSettings.get(a,None)
                t = _d[a]

                log.debug("|{0}| Add attr >> '{1}' | defaultValue: {2} | type: {3} ".format(_str_func,a,v,t)) 

                if ':' in t:
                    if forceReset:
                        self.addAttr(a, v, attrType = 'enum', enumName= t, keyable = False)		                        
                    else:
                        self.addAttr(a,initialValue = v, attrType = 'enum', enumName= t, keyable = False)		    
                elif t == 'stringDatList':
                    if forceReset or not ATTR.datList_exists(_short,a,mode='string'):
                        mc.select(cl=True)
                        ATTR.datList_connect(_short, a, v, mode='string')
                elif t == 'float3':
                    if not self.hasAttr(a):
                        ATTR.add(_short, a, attrType='float3', keyable = True)
                        if v:ATTR.set(_short,a,v)
                else:
                    if t == 'string':
                        _l = True
                        if v is None:v = ''                        
                    else:_l = False
                    
                    if forceReset:
                        self.addAttr(a, v, attrType = t,lock=_l, keyable = False)                                
                    else:
                        self.addAttr(a,initialValue = v, attrType = t,lock=_l, keyable = False)            
            except Exception,err:
                log.error("|{0}| Add attr Failure >> '{1}' | defaultValue: {2} ".format(_str_func,a,v)) 
                if not forceReset:
                    cgmGEN.cgmExceptCB(Exception,err)                    

        return True
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def set_nameTag(self,nameTag = None):
    try:
        _short = self.p_nameShort
        _str_func = 'set_nameTag'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        
        if nameTag is None:
            log.debug("|{0}| >> getting value by ui prompt".format(_str_func))
            _cgmName = self.getMayaAttr('cgmName')
            _title = 'Set name tag...'
            result = mc.promptDialog(title=_title,
                                     message='Block: {0} | Current: {1}'.format(_short,_cgmName),
                                     button=['OK', 'Cancel'],
                                     text = _cgmName,
                                     defaultButton='OK',
                                     cancelButton='Cancel',
                                     dismissString='Cancel')
            if result == 'OK':
                nameTag =  mc.promptDialog(query=True, text=True)
                log.debug("|{0}| >> from prompt: {1}".format(_str_func,nameTag))
            else:
                log.error("|{0}| >> Change cancelled".format(_str_func)+ '-'*80)
                return False
            
        self.cgmName = nameTag
        self.doName()
    except Exception,err:cgmGEN.cgmException(Exception,err)

def doName(self):
    """
    Override to handle difference with rig block

    """
    _short = self.p_nameShort
    _str_func = '[{0}] doName'.format(_short)
    
    _d = NAMETOOLS.returnObjectGeneratedNameDict(_short)

    _direction = self.getEnumValueString('side')
    if self.getMayaAttr('side'):
        _d['cgmDirection'] = _direction        
        self.doStore('cgmDirection',_direction)
    else:self.cgmDirection = ''

    _position = self.getEnumValueString('position')
    if self.getMayaAttr('position'):
        _d['cgmPosition'] = _position            
        self.doStore('cgmPosition',_position)
    else:self.cgmPosition = ''

    #Get Raw name

    for a in 'cgmName','baseName','puppetName',:
        if self.hasAttr(a):
            _d['cgmName'] = ATTR.get(_short,a)

    _blockType = ATTR.get(_short,'blockType')
    _d['cgmType'] = _blockType + 'Block'

    """
        if self.getMayaAttr('position'):
            _d['cgmPosition'] = self.getEnumValueString('position')
        if self.getMayaAttr('side'):
            _value = self.getEnumValueString('side')
            _d['cgmDirection'] = _value
            self.doStore('cgmDirection',_value)"""

    #Check for special attributes to replace data, name
    self.rename(NAMETOOLS.returnCombinedNameFromDict(_d))

    if self.getMessage('moduleTarget'):
        log.debug("|{0}| >> Module target naming...".format(_str_func))            
        self.moduleTarget.doName()
        
    
    ml_objs = get_blockDagNodes(self)
    for mObj in ml_objs:
        if mObj != self:
            mObj.doName()
    if self.getMessage('templateNull'):
        self.templateNull.doName()
    if self.getMessage('prerigNull'):
        self.prerigNull.doName()
        
        
        
def set_side(self,side=None):
    try:
        _short = self.p_nameShort
        _str_func = 'set_side'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        if side is None:
            side = 0
        try:
            ATTR.set(_short,'side',side)
        except Exception,err:
            log.error("|{0}| >> Failed to change attr. | err: {1}".format(_str_func,err))            
            return False
        color(self)
        
        ml_objs = get_blockDagNodes(self)
        for mObj in ml_objs:
            mObj.doName()
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def set_position(self,position=None):
    try:
        _short = self.p_nameShort
        _str_func = 'set_position'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        if position is None:
            position = 0
        try:
            ATTR.set(_short,'position',position)
        except Exception,err:
            log.error("|{0}| >> Failed to change attr. | err: {1}".format(_str_func,err))            
            return False
        
        ml_objs = get_blockDagNodes(self)
        for mObj in ml_objs:
            mObj.doName()
    except Exception,err:cgmGEN.cgmException(Exception,err)

def color(self):
    try:
        _short = self.p_nameShort
        _str_func = 'color'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        _side = get_side(self)
        log.debug("|{0}| >> side: {1}".format(_str_func,_side))
        
        mHandleFactory = self.asHandleFactory(self.mNode)
        
        ml_controls = get_blockDagNodes(self)
        
        for mHandle in ml_controls:
            for mShape in mHandle.getShapes(asMeta=True):
                if VALID.get_mayaType(mShape.mNode) in ['mesh','nurbsSurface']:
                    mHandleFactory.color(mShape.mNode)
                elif mShape.overrideEnabled:
                    log.debug("|{0}| >> shape: {1}".format(_str_func,mShape))
                    mHandleFactory.color(mShape.mNode)
            
    except Exception,err:
        cgmGEN.cgmException(Exception,err)


def test(self):
    return cgmGEN.queryCode()

def get_infoBlock_report(self):
    """
    Get a report of data 

    :returns
        list
    """
    try:
        _str_func = 'get_infoBlock_report'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        _short = self.p_nameShort
        mBlockModule = self.p_blockModule
        
        _res = []
        
        _res.append("blockParent : {0}".format(self.getBlockParent(False)))
        _res.append("blockChildren : {0}".format(len(self.getBlockChildren(False))))
        for msg in 'blockMirror','moduleTarget':
            _res.append("{0} : {1}".format(msg,ATTR.get(_short,msg)))          
    
        _res.append("       version: {0}".format(ATTR.get(_short,'version')))
        _res.append("module version: {0}".format(mBlockModule.__version__))
    
        for a in 'side','position':
            if ATTR.get(_short,a):
                _res.append("{0} : {1}".format(a,ATTR.get_enumValueString(_short,a)))
        return _res
    except Exception,err:
        cgmGEN.cgmException(Exception,err)

#=============================================================================================================
#>> Utilities
#=============================================================================================================


#=============================================================================================================
#>> define
#=============================================================================================================
def define(self):pass


#=============================================================================================================
#>> Template
#=============================================================================================================
def is_templateBAK(self):
    if not self.getMessage('templateNull'):
        return False
    return True


def is_template(self):
    try:
        _str_func = 'is_template'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        return check_msgDat(self, get_stateLinks(self,'template'))
        
    except Exception,err:
        cgmGEN.cgmException(Exception,err)

def templateDeleteBAK(self,msgLinks = []):
    try:
        _str_func = 'templateDelete'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        for link in msgLinks + ['templateNull']:
            if self.getMessage(link):
                log.info("|{0}| >> deleting link: {1}".format(_str_func,link))                        
                mc.delete(self.getMessage(link))
        return True
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
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

def create_templateLoftMesh(self, targets = None, mDatHolder = None, mTemplateNull = None,
                            uAttr = 'neckControls',baseName = 'test'):
    try:
        _str_func = 'create_templateLoftMesh'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
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
        #...this used to be {1} + 1. may need to revisit for head/neck
 
        
        
        _arg = "{0}.numberOfControlsOutTemp = {1} ".format(mDatHolder.p_nameShort,
                                                          self.getMayaAttrString(uAttr,'short'))
    
        NODEFACTORY.argsToNodes(_arg).doBuild()
    
        ATTR.connect("{0}.numberOfControlsOutTemp".format(mDatHolder.mNode), "{0}.uNumber".format(_tessellate))
        
        #Loft sides...
        _arg = "{0}.out_vSplitTemp = {1} + 1".format(targets[0],
                                                     self.getMayaAttrString('loftSides','short'))

        NODEFACTORY.argsToNodes(_arg).doBuild()
        #rg = "%s.condResult = if %s.ty == 3:5 else 1"%(str_obj,str_obj)


        ATTR.connect("{0}.out_vSplitTemp".format(targets[0]), "{0}.vNumber".format(_tessellate))                
        #ATTR.connect("{0}.loftSides".format(self.mNode), "{0}.vNumber".format(_tessellate))
    
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
        self.asHandleFactory().color(mLoft.mNode,transparent=True)
        #RIGGING.colorControl(mLoft.mNode,_side,'main',transparent = True)
    
        mLoft.inheritsTransform = 0
        for s in mLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 2   
    
        self.connectChildNode(mLoft.mNode, 'templateLoftMesh', 'block')    
        return mLoft
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
#=============================================================================================================
#>> Prerig
#=============================================================================================================
def noTransformNull_verify(self):
    try:
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
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
def prerigNull_verify(self):
    try:
        if not self.getMessage('prerigNull'):
            str_prerigNull = RIGGING.create_at(self.mNode)
            mPrerigNull = cgmMeta.validateObjArg(str_prerigNull, mType = 'cgmObject',setClass = True)
            mPrerigNull.connectParentNode(self, 'rigBlock','prerigNull') 
            mPrerigNull.doStore('cgmName', self.mNode)
            mPrerigNull.doStore('cgmType','prerigNull')
            mPrerigNull.doName()
            mPrerigNull.p_parent = self
            #mPrerigNull.setAttrFlags()
        else:
            mPrerigNull = self.prerigNull    
            
        return mPrerigNull
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
def prerig_simple(self):
    _str_func = 'prerig_simple'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
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

def prerig_delete(self, msgLinks = [], msgLists = [], templateHandles = True):
    try:
        _str_func = 'prerig_delete'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
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
    except Exception,err:
        cgmGEN.cgmException(Exception,err)

def delete_msgDat(self,d_wiring = {}, msgLinks = [], msgLists = [] ):
    _str_func = 'delete_msgDat'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)    
    
    _l_missing = []
    for l in d_wiring.get('msgLinks',[]) + msgLinks:
        l_dat = self.getMessage(l)
        if l_dat:
            log.debug("|{0}| >>  Found msgLink: {1} | {2}".format(_str_func,l,l_dat))
            mc.delete(l_dat)
            
    for l in d_wiring.get('msgLists',[]) + msgLists:
        if self.msgList_exists(l):
            self.msgList_purge('l')
            log.debug("|{0}| >>  Purging msgList: {1}".format(_str_func,l))
            
    return True

def check_msgDat(self,d_wiring = {}, msgLinks = [], msgLists = [] ):
    _str_func = 'check_msgDat'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)    
    
    _l_missing = []
    for l in d_wiring.get('msgLinks',[]) + msgLinks:
        if not self.getMessage(l):
            _l_missing.append('msgLink ' + self.p_nameBase + '.' + l)
        else:
            log.debug("|{0}| >>  Found msgLink: {1}".format(_str_func,l))
            
    for l in d_wiring.get('msgLists',[]) + msgLists:
        if not self.msgList_exists(l):
            _l_missing.append(self.p_nameBase + '.[msgList]' + l)
        else:
            log.debug("|{0}| >>  Found msgList: {1}".format(_str_func,l))
            
    if _l_missing:
        log.info("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.info("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True
    
def get_stateLinks(self, mode = 'template' ):
    try:
        _str_func = 'get_stateLinks'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        mBlockModule = self.p_blockModule
        log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
        
        d_wiring = {}
        try:
            d_wiring.update(getattr(mBlockModule,'d_wiring_{0}'.format(mode)))
            log.debug("|{0}| >>  Found {1} wiring dat in BlockModule".format(_str_func,mode))
        except Exception,err:
            log.debug("|{0}| >>  No {1} wiring dat in BlockModule. error: {2}".format(_str_func,mode,err))            
            pass
        return d_wiring
        
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
def is_prerig(self):
    try:
        _str_func = 'is_prerig'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        return check_msgDat(self, get_stateLinks(self,'prerig'))

    except Exception,err:
        cgmGEN.cgmException(Exception,err)

def is_prerigBAK(self, msgLinks = [], msgLists = [] ):
    try:
        _str_func = 'is_prerig'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
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
    except Exception,err:
        cgmGEN.cgmException(Exception,err)


def create_prerigLoftMesh(self, targets = None,
                          mPrerigNull = None,
                          uAttr = 'neckControls',
                          uAttr2 = 'loftSplit',
                          vAttr = 'loftSides',
                          degreeAttr = None,
                          polyType = 'mesh',
                          baseName = 'test'):
    try:
        _str_func = 'create_prerigLoftMesh'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        _short = self.mNode
        _side = 'center'
        if self.getMayaAttr('side'):
            _side = self.getEnumValueString('side')  
                
        log.debug("|{0}| >> Creating: {1}".format(_str_func,polyType))
        
        if polyType == 'mesh':
            _res_body = mc.loft(targets, o = True, d = 3, po = 1 )
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
            _inputs = mc.listHistory(mLoftSurface.mNode,pruneDagObjects=True)
        
            _tessellate = _inputs[0]
            _loftNode = _inputs[1]
        
            log.info("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 
            _d = {'format':2,#General
                  'polygonType':1,#'quads',
                  'uNumber': 1 + len(targets)}
        
            for a,v in _d.iteritems():
                ATTR.set(_tessellate,a,v)  
                
        elif polyType in ['bezier','noMult']:
            _res_body = mc.loft(targets, o = True, d = 1, po = 3, c = False)
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)                    
            _loftNode = _res_body[1]
            _inputs = mc.listHistory(mLoftSurface.mNode,pruneDagObjects=True)
            _rebuildNode = _inputs[0]            
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
            
            
            
            _d = {'keepCorners':False}#General}
            
            if polyType == 'noMult':
                _d['rebuildType'] = 3
        
            for a,v in _d.iteritems():
                ATTR.set(_rebuildNode,a,v)
                
        else:
            _res_body = mc.loft(targets, o = True, d = 3, po = 0 )
            _loftNode = _res_body[1]
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)        
            
        mLoftSurface.overrideEnabled = 1
        mLoftSurface.overrideDisplayType = 2
        
        mLoftSurface.p_parent = mPrerigNull
        mLoftSurface.resetAttrs()
    
        mLoftSurface.doStore('cgmName',self.mNode)
        mLoftSurface.doStore('cgmType','shapeApprox')
        mLoftSurface.doName()
        log.info("|{0}| loft node: {1}".format(_str_func,_loftNode)) 
    
        #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
        #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;
    
        #mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
    
        #Color our stuff...
        log.debug("|{0}| >> Color...".format(_str_func))        
        RIGGING.colorControl(mLoftSurface.mNode,_side,'main',transparent = True)
    
        mLoftSurface.inheritsTransform = 0
        for s in mLoftSurface.getShapes(asMeta=True):
            s.overrideDisplayType = 2    
        
        log.debug("|{0}| >> Linear/Cubic...".format(_str_func))        
        if polyType in ['bezier','noMult']:
            _arg = "{0}.out_degreeBez = if {1} == 0:1 else 3".format(targets[0],
                                                                     self.getMayaAttrString('loftDegree','short'))
            NODEFACTORY.argsToNodes(_arg).doBuild()            
            ATTR.connect("{0}.out_degreeBez".format(targets[0]), "{0}.degreeU".format(_rebuildNode))
            ATTR.connect("{0}.out_degreeBez".format(targets[0]), "{0}.degreeV".format(_rebuildNode))
            
        _arg = "{0}.out_degreePre = if {1} == 0:1 else 3".format(targets[0],
                                                              self.getMayaAttrString('loftDegree','short'))

        NODEFACTORY.argsToNodes(_arg).doBuild()            
        ATTR.connect("{0}.out_degreePre".format(targets[0]), "{0}.degree".format(_loftNode))    
        
        toName = []
        if polyType == 'mesh':
            #...wire some controls
            _arg = "{0}.out_vSplitPre = {1} + 1".format(targets[0],
                                                     self.getMayaAttrString(uAttr,'short'))
        
            NODEFACTORY.argsToNodes(_arg).doBuild()
            #rg = "%s.condResult = if %s.ty == 3:5 else 1"%(str_obj,str_obj)

        
            ATTR.connect("{0}.out_vSplitPre".format(targets[0]), "{0}.uNumber".format(_tessellate))
            ATTR.connect("{0}.{1}".format(self.mNode,vAttr), "{0}.vNumber".format(_tessellate)) 
        
            #ATTR.copy_to(_loftNode,'degree',self.mNode,'loftDegree',driven = 'source')
        
            toName = [_tessellate,_loftNode]
        elif polyType in ['bezier','noMult']:
            #_arg = "{0}.out_vSplitPre = {1} + 1".format(targets[0],
            #                                         self.getMayaAttrString(uAttr,'short'))
                    
            #NODEFACTORY.argsToNodes(_arg).doBuild()
            #ATTR.connect("{0}.out_vSplit".format(targets[0]), "{0}.spansU".format(_rebuildNode))
            ATTR.connect("{0}.{1}".format(self.mNode,uAttr), "{0}.spansU".format(_rebuildNode))            
            ATTR.connect("{0}.{1}".format(self.mNode,vAttr), "{0}.spansV".format(_rebuildNode))
            
            ATTR.connect("{0}.{1}".format(_short,uAttr2), "{0}.sectionSpans".format(_loftNode))
            
            #_close = mc.closeSurface(mLoftSurface.mNode,d=1,p=0,rpo=True)
            
            toName = [_rebuildNode,_loftNode]
        else:
            ATTR.connect("{0}.loftSplit".format(_short), "{0}.sectionSpans".format(_loftNode))
            toName = [_loftNode]

                
        for n in toName:
            mObj = cgmMeta.validateObjArg(n)
            mObj.doStore('cgmName',self.mNode)
            mObj.doStore('cgmTypeModifier','prerigMesh')
            mObj.doName()                        
       
        self.connectChildNode(mLoftSurface.mNode, 'prerigLoftMesh', 'block')    
        return mLoftSurface
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
def create_jointLoft(self, targets = None, mPrerigNull = None,
                     uAttr = 'neckJoints', baseName = 'test'):
    
    _str_func = 'create_jointLoft'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
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
    
    _str_func = 'create_jointLoftBAK'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
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
def rigDeleteBAK(self,msgLinks = []):
    try:
        _str_func = 'rigDelete'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        
        if self.isReferenced():
            raise ValueError,"Referenced node."
        
        _str_state = self.blockState
    
        if self.blockState != 'rig':
            raise ValueError,"{0} is not in rig state. state: {1}".format(_str_func, _str_state)
    
        self.blockState = 'rig>prerig'        
    
        mModuleTarget = self.moduleTarget
        if mModuleTarget:
            log.debug("|{0}| >> ModuleTarget: {1}".format(_str_func,mModuleTarget))            
            if mModuleTarget.mClass ==  'cgmRigModule':
                #Deform null
                _deformNull = mModuleTarget.getMessage('deformNull')
                if _deformNull:
                    log.debug("|{0}| >> deformNull: {1}".format(_str_func,_deformNull))                                
                    mc.delete(_deformNull)
                #ModuleSet
                _objectSet = mModuleTarget.rigNull.getMessage('moduleSet')
                if _objectSet:
                    log.debug("|{0}| >> objectSet: {1}".format(_str_func,_objectSet))                                
                    mc.delete(_deformNull)                
                #Module                
            elif mModuleTarget.mClass == 'cgmRigPuppet':
                pass
            else:
                log.error("|{0}| >> Unknown mClass moduleTarget: {1}".format(_str_func,mModuleTarget))            
    
    
    
        if 'rigDelete' in _mBlockModule.__dict__.keys():
            log.debug("|{0}| >> BlockModule rigDelete call found...".format(_str_func))            
            _mBlockModule.rigDelete(self)        
    
    
        self.blockState = 'prerig'
        
        
        for link in msgLinks + ['rigNull']:
            if self.getMessage(link):
                log.info("|{0}| >> deleting link: {1}".format(_str_func,link))                        
                mc.delete(self.getMessage(link))
                
        return True
    except Exception,err:
        cgmGEN.cgmException(Exception,err)


l_pivotOrder = ['center','back','front','left','right']
d_pivotBankNames = {'default':{'left':'outer','right':'inner'},
                    'right':{'left':'inner','right':'outer'}}

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
    _str_func = 'pivots_buildShapes'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
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
    _str_func = 'pivots_setup'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    _start = time.clock()
    
    _side = get_side(self)
    if _side in ['right']:
        d_bankNames = d_pivotBankNames['right']
    else:
        d_bankNames = d_pivotBankNames['default']
    
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
                
                if a in ['left','right']:
                    mPivot.doStore('cgmName', d_bankNames[a])
                    mPivot.doName()
                    
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
        mPlug_rollBall.doConnectOut("{0}.rx".format(mDriven.mNode))         
        """
        if _side in ['right']:
            str_arg = "{0}.rx = -{1}".format(mDriven.mNode,
                                             mPlug_rollBall.p_combinedShortName)
            log.info("|{0}| >> Right arg: {1}".format(_str_func,str_arg))        
            NODEFACTORY.argsToNodes(str_arg).doBuild()
        else:
            mPlug_rollBall.doConnectOut("{0}.rx".format(mDriven.mNode))         """
            
    
    #Spins ===================================================================================================
    log.info("|{0}| >> Spin ...".format(_str_func))
    
    d_mPlugSpin = {}
    for k in d_drivenGroups.keys():
        d_mPlugSpin[k] = cgmMeta.cgmAttr(mControl,'spin{0}'.format(d_strCaps[k]),attrType='float',defaultValue = 0,keyable = True)
        
    for k in d_drivenGroups.keys():
        str_key = d_strCaps[k]
        mPlug = d_mPlugSpin[k]
        mDriven = d_drivenGroups[k]
        log.debug("|{0}| >> Spin {1} setup".format(_str_func,str_key))        
        
        if _side in ['right']:
            str_arg = "{0}.ry = -{1}".format(mDriven.mNode,
                                             mPlug.p_combinedShortName)
            log.debug("|{0}| >> Spin Right arg: {1}".format(_str_func,str_arg))        
            NODEFACTORY.argsToNodes(str_arg).doBuild()
        else:
            mPlug.doConnectOut("{0}.ry".format(mDriven.mNode))     
            
    
    if b_bankOK:#Bank ===================================================================================================
        log.debug("|{0}| >> Bank ...".format(_str_func))
        mPlug_bank = cgmMeta.cgmAttr(mControl,'bank',attrType='float',defaultValue = 0,keyable = True)
        
        mPlug_outerResult = cgmMeta.cgmAttr(mControl,'result_clamp_outerBank',attrType='float',keyable = False,hidden=True)
        mPlug_innerResult = cgmMeta.cgmAttr(mControl,'result_clamp_innerBank',attrType='float',keyable = False,hidden=True)
        
        if _side in ['right']:
            log.debug("|{0}| >> Bank right...".format(_str_func))            
            mDrivenOutr = d_drivenGroups['right']
            mDrivenInner =d_drivenGroups['left']
            
            arg1 = "%s = clamp(-360,0,%s)"%(mPlug_innerResult.p_combinedShortName,                                  
                                            mPlug_bank.p_combinedShortName)
            arg2 = "%s = clamp(0,360,%s)"%(mPlug_outerResult.p_combinedShortName,
                                           mPlug_bank.p_combinedShortName)
            for arg in [arg1,arg2]:
                NODEFACTORY.argsToNodes(arg).doBuild()           
            
            str_bankDriverOutr = "%s.rz = -%s"%(mDrivenInner.mNode,
                                             mPlug_outerResult.p_combinedShortName)
            str_bankDriverInnr = "%s.rz = -%s"%(mDrivenOutr.mNode,
                                                mPlug_innerResult.p_combinedShortName)    
            for arg in [str_bankDriverInnr,str_bankDriverOutr]:
                NODEFACTORY.argsToNodes(arg).doBuild()
        else:
            log.debug("|{0}| >> Bank normal...".format(_str_func))                        
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
        log.debug("|{0}| >> Bank Center...".format(_str_func))        
        mDriven = d_drivenGroups['center']
        if _side in ['right']:
            str_arg = "{0}.rz = -{1}".format(mDriven.mNode,
                                             mPlug_bankBall.p_combinedShortName)
            log.info("|{0}| >> Right arg: {1}".format(_str_func,str_arg))        
            NODEFACTORY.argsToNodes(str_arg).doBuild()
        else:
            mPlug_bankBall.doConnectOut("{0}.rz".format(mDriven.mNode))         
    


    log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    
    
#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def prerigHandles_getNameDat(self, nameHandles = False,**kws):
    """
    Get a list of the driving attributes to plug in to our handles
    
    :parameters:
    
    :returns
        list
    """
    _str_func = 'prerigHandles_getNameDat'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    l_res = []

    mModule = self.moduleTarget
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')
    
    _number = self.numControls
    
    #Name dict...
    _nameDict ={}
    _short = self.mNode
    if mModule.getMayaAttr('cgmDirection'):
        _nameDict['cgmDirection'] = [mModule.mNode,'cgmDirection']
    if mModule.getMayaAttr('cgmPosition'):
        _nameDict['cgmPosition'] = [mModule.mNode,'cgmPosition']
    
    if self.getMayaAttr('nameIter'):
        _nameDict['cgmName'] = [_short,'nameIter']
    elif self.getMayaAttr('cgmName'):
        _nameDict['cgmName'] = [_short,'cgmName']
    else:
        _nameDict['cgmName'] = [_short,'blockType']
    
    _nameDict['cgmType'] = 'blockHandle'
    
    for a,v in kws.iteritems():
        _nameDict[a] = v    
    
    _cnt = 0
    l_range = range(_number)
    for i in l_range:
        _nameDictTemp = copy.copy(_nameDict)
        _specialName = False
        _cnt+=1

        if i == 0:
            if self.getMayaAttr(_baseNameAttrs[0]):
                _nameDictTemp['cgmName'] = [_short, _baseNameAttrs[0]]#"{0}.{1}".format(self.mNode, _baseNameAttrs[0])
                _cnt = 0
                _specialName = True
        elif i == len(l_range) -1:
            if self.getMayaAttr(_baseNameAttrs[-1]):
                _nameDictTemp['cgmName'] = [_short, _baseNameAttrs[-1]]#"{0}.{1}".format(self.mNode, _baseNameAttrs[-1])                
                #_nameDictTemp['cgmName'] = _l_baseNames[-1]
                _specialName = True

        if not _specialName:
            _nameDictTemp['cgmIterator'] = _cnt
            
        l_res.append( _nameDictTemp )
        
    if nameHandles:
        ml_prerigHandles = self.msgList_get('prerigHandles')
        if len(ml_prerigHandles) == _number:
            log.debug("|{0}| >>  nameHandles on. Same length...".format(_str_func))
            for i,mHandle in enumerate(ml_prerigHandles):
                _dict = l_res[i]
                for k,v in _dict.iteritems():
                    if issubclass(type(v),list):
                        ATTR.copy_to(v[0],v[1], toObject=mHandle.mNode,toAttr=k,driven='target')
                    else:
                        mHandle.doStore(k,v)
                mHandle.doName()
                for plug in ['masterGroup','aimGroup','jointHelper']:
                    if mHandle.getMessage(plug):
                        mHandle.getMessage(plug,asMeta=True)[0].doName()

                log.debug("|{0}| >>  {1} : {2}.".format(_str_func, i, mHandle.p_nameShort))
    return l_res    


def skeleton_getNameDicts(self, combined = False, count = None, **kws):
    """
    Get a list of name dicts for a given block's rig/skin joints
    
    :parameters:
    
    :returns
        list
    """
    _str_func = 'skeleton_getNameDicts'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    l_res = []
    if count is not None:
        _number = count
    else:
        _number = self.numJoints
    mModule = self.moduleTarget
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')    
    #Name dict...
    _nameDict ={}
    
    if mModule.getMayaAttr('cgmDirection'):
        _nameDict['cgmDirection'] = mModule.cgmDirection
    if mModule.getMayaAttr('cgmPosition'):
        _nameDict['cgmPosition']=mModule.cgmPosition
    
    if self.getMayaAttr('nameIter'):
        _nameDict['cgmName'] = self.nameIter
    elif self.getMayaAttr('cgmName'):
        _nameDict['cgmName'] = self.cgmName
    else:
        _nameDict['cgmName'] = self.blockType
        
    _nameDict['cgmType'] = 'joint'
    
    
    for a,v in kws.iteritems():
        _nameDict[a] = v
    
    _cnt = 0
    l_range = range(_number)
    for i in l_range:
        _nameDictTemp = copy.copy(_nameDict)
        _specialName = False
        _cnt+=1
        
        if i == 0:
            if self.getMayaAttr(_baseNameAttrs[0]):
                _nameDictTemp['cgmName'] = _l_baseNames[0]
                _cnt = 0
                _specialName = True
        elif i == len(l_range) -1:
            if self.getMayaAttr(_baseNameAttrs[-1]):
                _nameDictTemp['cgmName'] = _l_baseNames[-1]
                _specialName = True

        if not _specialName:
            _nameDictTemp['cgmIterator'] = _cnt
            
        #mJoint.rename(NAMETOOLS.returnCombinedNameFromDict(_nameDictTemp))
        if combined:
            l_res.append(NAMETOOLS.returnCombinedNameFromDict(_nameDictTemp))
        else:
            l_res.append( _nameDictTemp )
    return l_res



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
    _str_func = 'skeleton_getCreateDict'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
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


def skeleton_buildDuplicateChain(self,sourceJoints = None, modifier = 'rig', connectToModule = False, connectAs = 'rigJoints', connectToSource = 'skinJoint', singleMode = False, cgmType = None, indices  = [],blockNames=False):
    """
    blockNames(bool) - use the block generated names
    """
    _str_func = 'skeleton_buildDuplicateChain'
    
    
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

    if blockNames:
        l_names = skeleton_getNameDicts(self,False)        
    else:
        l_names = []
    
    for i,mJnt in enumerate(ml_joints):
        if blockNames:
            _d_tmp = l_names[i]
            log.info("|{0}| >> blockName dict {1} | {2}".format(_str_func, i,_d_tmp))              
            for a in ['cgmIterator','cgmName']:
                if _d_tmp.get(a):
                    mJnt.addAttr(a, str(_d_tmp.get(a)),attrType='string',lock=True)

        if modifier is not None:
            #l_names[i]['cgmTypeModifier'] = modifier
            mJnt.addAttr('cgmTypeModifier', modifier,attrType='string',lock=True)
        if cgmType is not None:
            #l_names[i]['cgmType'] = cgmType            
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
    for i,mJnt in enumerate(ml_joints):
        #mJnt.rename(NAMETOOLS.returnCombinedNameFromDict(l_names[i]))
        mJnt.doName()	
        
    if connectToModule:
        if singleMode:
            connectToModule.connectChildNode(ml_joints[0],connectAs,'rigNull')
        else:
            connectToModule.msgList_connect(connectAs, ml_joints,'rigNull')#connect	
            
    return ml_joints


def skeleton_connectToParent(self):
    _str_func = 'skeleton_connectToParent'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    mModule = self.moduleTarget
    ml_moduleJoints = mModule.rigNull.msgList_get('moduleJoints',asMeta = True)
    
    ml_parentBlocks = self.getBlockParents()
    
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
            _attachPoint = ATTR.get_enumValueString(self.mNode,'attachPoint')
            if _attachPoint == 'end':
                mTargetJoint = ml_targetJoints[-1]
            elif _attachPoint == 'base':
                mTargetJoint = ml_targetJoints[0]
            else:
                raise ValueError,"Not done with {0}".format(_attachPoint)
        
            ml_moduleJoints[0].p_parent = mTargetJoint
            
    return True

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

def skeleton_pushSettings(ml_chain = None, orientation = 'zyx', side = 'right',
                          d_rotateOrders = {}, d_preferredAngles = {}, d_limits = {}):
    
    _str_func = '[{0}] > '.format('skeleton_pushSettings')
    
    _preferredAxis = {}
    _l_axisAlias = ['aim','up','out']
    for k in _l_axisAlias:
        if d_preferredAngles.get(k) is not None:
            _v = d_preferredAngles.get(k)
            log.info("|{0}| >> found default preferred {1}:{2}".format(_str_func,k,_v))  
            _preferredAxis[k] = _v
    
    for mJnt in ml_chain:
        _key = mJnt.getMayaAttr('cgmName',False)
        
        _rotateOrderBuffer = d_rotateOrders.get(_key,d_rotateOrders.get('default',False))
        _limitBuffer = d_limits.get(_key,d_limits.get('default',False))
        _preferredAngles = d_preferredAngles.get(_key,d_preferredAngles.get('default',False))
        
        
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
        elif _preferredAxis:
            for k,v in _preferredAxis.iteritems():
                _idx = _l_axisAlias.index(k)
                if side.lower() == 'right':#negative value
                    mJnt.__setattr__('preferredAngle{0}'.format(orientation[_idx].upper()),-v)				
                else:
                    mJnt.__setattr__('preferredAngle{0}'.format(orientation[_idx].upper()),v)                
            
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
        
        ml_templateHandles = self.msgList_get('templateHandles',asMeta = True)
        if not ml_templateHandles:
            raise ValueError,"No templateHandles connected"        
        
        ml_prerigHandles = self.msgList_get('prerigHandles',asMeta = True)
        if not ml_prerigHandles:
            raise ValueError,"No prerigHandles connected"
        
        mOrientHelper = ml_templateHandles[0].orientHelper or ml_prerigHandles[0].orientHelper
        _d = skeleton_getCreateDict(self)
        pprint.pprint(_d)
        ml_fkJoints = COREJOINTS.build_chain(targetList=_d['helpers']['targets'],
                                           axisAim='z+',
                                           axisUp='y+',
                                           parent=True,
                                           worldUpAxis= mOrientHelper.getAxisVector('y+'))
        
        for i,mJnt in enumerate(ml_fkJoints):
            mJnt.doCopyNameTagsFromObject(ml_prerigHandles[i].mNode, ignore = ['cgmType'])
            if not typeModifier:
                mJnt.doName()
                
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


#=============================================================================================================
#>> blockParent
#=============================================================================================================
def blockParent_set(self, parent = False, attachPoint = None):        
    _str_func = 'blockParent_set'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    mParent_current =  self.blockParent
    if self.blockState == 'rig':
        raise ValueError,"Cannot change the block parent of a rigged rigBlock. State: {0} | rigBlock: {1}".format(self.blockState,self)
    
    if not parent:
        self.blockParent = False
        if self.p_blockParent != False:
            self.p_parent = False
            
        if self.getMessage('moduleTarget'):
            log.debug("|{0}| >>  parent false. clearing moduleTarget".format(_str_func,self))
            self.moduleTarget = False
            
    else:
        mParent = cgmMeta.validateObjArg(parent,'cgmRigBlock',noneValid=True)
        if not mParent:
            raise ValueError,"Invalid blockParent. Not a cgmRigBlock. parent: {0}".format( cgmMeta.asMeta(parent))
        
        if parent == self:
            raise ValueError, "Cannot blockParent to self"

        #if parent.getMessage('blockParent') and parent.blockParent == self:
            #raise ValueError, "Cannot blockParent to block whose parent is self"

        self.connectParentNode(parent, 'blockParent')

        if self.p_blockParent != False:
            self.p_parent = False

        #if attachPoint:
            #self.p_parent = attachPoint
        #else:
            #self.p_parent = parent

        #_parent = VALID.mNodeString(parent)
        #mc.parentConstraint([_parent], self.mNode, maintainOffset = True)
        #mc.scaleConstraint([_parent], self.mNode, maintainOffset = True)
        
        #Module parent wiring ----------------------------------------------------
        if mParent.getMessage('moduleTarget'):
            mParentModuleTarget = mParent.moduleTarget
            log.debug("|{0}| >>  mParent has moduleTarget: {1}".format(_str_func,mParentModuleTarget))            
            if self.getMessage('moduleTarget'):
                mModuleTarget = self.moduleTarget
                log.debug("|{0}| >>  parent true. setting moduleTarget module parent".format(_str_func,self))
                if mParent.blockType == 'master':
                    log.debug("|{0}| >>  master parent. Trying to connect to modulePuppet".format(_str_func))
                    mModuleTarget.modulePuppet = mParentModuleTarget
                else:
                    log.debug("|{0}| >>  Setting moduleParent".format(_str_func))                    
                    self.atRigModule('set_parentModule',mParentModuleTarget)
        


#=============================================================================================================
#>> Mirror/Duplicate
#=============================================================================================================
def duplicate(self):
    """
    Call to duplicate a block module and load data
    """
    try:
        _str_func = 'blockDuplicate'
        mDup = cgmMeta.createMetaNode('cgmRigBlock',blockType = self.blockType, autoTemplate=False)
        mDup.loadBlockDat(self.getBlockDat())
        mDup.doName()
        return mDup
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def blockMirror_create(self, forceNew = False):
    """
    Call to duplicate a block module and load data
    """
    try:
        _str_func = 'blockMirror_create'
        _side = get_sideMirror(self)
        _blockType = self.blockType
        if not _side:
            log.error("|{0}| >> Block is not sided. Can't create mirror".format(_str_func, self.mNode))                    
            return False
        if self.getMessage('blockMirror'):
            mMirror = self.blockMirror
            log.debug("|{0}| >> blockMirror found {1} ".format(_str_func, mMirror))
            if not forceNew:
                return mMirror
            log.debug("|{0}| >> focing new... ".format(_str_func, mMirror))            
            mMirror.delete()
            
        log.debug("|{0}| >> Creating mirror block. {1} | {2}".format(_str_func, _blockType, _side))
        
        mMirror = cgmMeta.createMetaNode('cgmRigBlock',blockType = self.blockType, side = _side, autoTemplate=False)
        
        blockDat = self.getBlockDat()
        blockDat['ud']['side'] = get_sideMirror(self)        
        blockDat_load(mMirror, blockDat, mirror = False)
        controls_mirror(self,mMirror)
        
        mMirror.p_blockParent = self.p_blockParent
        self.connectChildNode(mMirror,'blockMirror','blockMirror')#Connect    
        
        return mMirror
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def blockMirror_go(self, mode = 'push',autoCreate = False):
    """
    Call to duplicate a block module and load data
    """
    try:
        _str_func = 'blockMirror_go'
        _short = self.p_nameShort
        if not self.getMessage('blockMirror'):
            log.error("|{0}| >> [{1}] No block mirror found".format(_str_func, _short))                                
            return False
        
        mMirror = self.blockMirror
        
        if mode == 'push':
            controls_mirror(self,mMirror)
        else:
            controls_mirror(mMirror,self)

        return mMirror
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
    
def blockDat_mirror(self, reflectionVector = MATH.Vector3(1,0,0) ):
    try:
        '''Mirrors the template positions from the block to the mirrorBlock across the reflection vector transformed from the root block'''
        _str_func = 'MirrorBlock'

        if not self or not mirrorBlock:
            log.warning("|{0}| >> Must have rootBlock and mirror block".format(_str_func))                                            
            return

        if mirrorBlock.blockType != self.blockType:
            log.warning("|{0}| >> Blocktypes must match. | {1} != {2}".format(_str_func,block.blockType,mirrorBlock.blockType,))                                                        
            return

        rootTransform = self
        rootReflectionVector = TRANS.transformDirection(rootTransform,reflectionVector).normalized()
        #rootReflectionVector = rootTransform.templatePositions[0].TransformDirection(reflectionVector).normalized()

        print("|{0}| >> Root: {1}".format(_str_func, rootTransform.p_nameShort))                                            


        if mirrorBlock:
            print ("|{0}| >> Target: {1} ...".format(_str_func, mirrorBlock.p_nameShort))

            _blockState = rootBlock.getState(False)
            _mirrorState = mirrorBlock.getState(False)
            if _blockState > _mirrorState or _blockState < _mirrorState:
                print ("|{0}| >> root state greater. Matching root: {1} to mirror:{2}".format(_str_func, _blockState,_mirrorState))
            else:
                print ("|{0}| >> blockStates match....".format(_str_func, mirrorBlock.p_nameShort))

            #if rootBlock.blockState != BlockState.TEMPLATE or mirrorBlock.blockState != BlockState.TEMPLATE:
                #print "Can only mirror blocks in Template state"
                #return

            cgmGEN.func_snapShot(vars())
            return

            currentTemplateObjects = block.templatePositions
            templateHeirarchyDict = {}
            for i,p in enumerate(currentTemplateObjects):
                templateHeirarchyDict[i] = p.fullPath.count('|')

            templateObjectsSortedByHeirarchy = sorted(templateHeirarchyDict.items(), key=operator.itemgetter(1))

            for x in range(2):
                # do this twice in case there are any stragglers 
                for i in templateObjectsSortedByHeirarchy:
                    index = i[0]
                    #print "Mirroring %s to %s" % (mirrorBlock.templatePositions[index].name, block.templatePositions[index].name)

                    # reflect rotation
                    reflectAim = block.templatePositions[index].TransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
                    reflectUp  = block.templatePositions[index].TransformDirection( MATH.Vector3(0,1,0)).reflect( rootReflectionVector )
                    mirrorBlock.templatePositions[index].LookRotation( reflectAim, reflectUp )

                for i in templateObjectsSortedByHeirarchy:
                    index = i[0]
                    wantedPos = (block.templatePositions[index].position - rootTransform.templatePositions[0].position).reflect( rootReflectionVector ) + rootTransform.templatePositions[0].position

                    #print "wanted position:", wantedPos
                    mirrorBlock.templatePositions[index].position = wantedPos

                    if block.templatePositions[index].type == "joint":
                        #mirrorBlock.templatePositions[index].SetAttr("radius", block.templatePositions[index].GetAttr("radius"))
                        mirrorBlock.templatePositions[index].radius = block.templatePositions[index].radius

                    wantedScale = block.templatePositions[index].localScale
                    if not mc.getAttr(mirrorBlock.templatePositions[index].GetAttrString('sx'), l=True):
                        mirrorBlock.templatePositions[index].SetAttr('sx', wantedScale.x)
                    if not mc.getAttr(mirrorBlock.templatePositions[index].GetAttrString('sy'), l=True):
                        mirrorBlock.templatePositions[index].SetAttr('sy', wantedScale.y)
                    if not mc.getAttr(mirrorBlock.templatePositions[index].GetAttrString('sz'), l=True):
                        mirrorBlock.templatePositions[index].SetAttr('sz', wantedScale.z)

            for attr in mc.listAttr(block.name, ud=True, v=True, unlocked=True):
                mirrorBlock.SetAttr( attr, block.GetAttr(attr) )
                if attr == "reverseUp":
                    mirrorBlock.SetAttr( attr, 1-block.GetAttr(attr) )
                if attr == "reverseForward":
                    mirrorBlock.SetAttr( attr, 1-block.GetAttr(attr) )	

        # mirror child blocks
        for attachPoint in block.attachPoints:
            for child in attachPoint.children:
                childBlock = Block.LoadRigBlock( child )
                if childBlock:
                    Block.MirrorBlockPush(childBlock)
    except Exception,err:
        cgmGEN.cgm
        
def mirror_blockDat(self = None, mirrorBlock = None, reflectionVector = MATH.Vector3(1,0,0) ):
    try:
        '''Mirrors the template positions from the block to the mirrorBlock across the reflection vector transformed from the root block'''
        _str_func = 'MirrorBlock'

        if not self or not mirrorBlock:
            log.warning("|{0}| >> Must have rootBlock and mirror block".format(_str_func))                                            
            return

        if mirrorBlock.blockType != self.blockType:
            log.warning("|{0}| >> Blocktypes must match. | {1} != {2}".format(_str_func,block.blockType,mirrorBlock.blockType,))                                                        
            return

        rootTransform = self
        rootReflectionVector = TRANS.transformDirection(rootTransform,reflectionVector).normalized()
        #rootReflectionVector = rootTransform.templatePositions[0].TransformDirection(reflectionVector).normalized()

        print("|{0}| >> Root: {1}".format(_str_func, rootTransform.p_nameShort))                                            


        if mirrorBlock:
            print ("|{0}| >> Target: {1} ...".format(_str_func, mirrorBlock.p_nameShort))

            _blockState = rootBlock.getState(False)
            _mirrorState = mirrorBlock.getState(False)
            if _blockState > _mirrorState or _blockState < _mirrorState:
                print ("|{0}| >> root state greater. Matching root: {1} to mirror:{2}".format(_str_func, _blockState,_mirrorState))
            else:
                print ("|{0}| >> blockStates match....".format(_str_func, mirrorBlock.p_nameShort))

            #if rootBlock.blockState != BlockState.TEMPLATE or mirrorBlock.blockState != BlockState.TEMPLATE:
                #print "Can only mirror blocks in Template state"
                #return

            cgmGEN.func_snapShot(vars())
            return

            currentTemplateObjects = block.templatePositions
            templateHeirarchyDict = {}
            for i,p in enumerate(currentTemplateObjects):
                templateHeirarchyDict[i] = p.fullPath.count('|')

            templateObjectsSortedByHeirarchy = sorted(templateHeirarchyDict.items(), key=operator.itemgetter(1))

            for x in range(2):
                # do this twice in case there are any stragglers 
                for i in templateObjectsSortedByHeirarchy:
                    index = i[0]
                    #print "Mirroring %s to %s" % (mirrorBlock.templatePositions[index].name, block.templatePositions[index].name)

                    # reflect rotation
                    reflectAim = block.templatePositions[index].TransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
                    reflectUp  = block.templatePositions[index].TransformDirection( MATH.Vector3(0,1,0)).reflect( rootReflectionVector )
                    mirrorBlock.templatePositions[index].LookRotation( reflectAim, reflectUp )

                for i in templateObjectsSortedByHeirarchy:
                    index = i[0]
                    wantedPos = (block.templatePositions[index].position - rootTransform.templatePositions[0].position).reflect( rootReflectionVector ) + rootTransform.templatePositions[0].position

                    #print "wanted position:", wantedPos
                    mirrorBlock.templatePositions[index].position = wantedPos

                    if block.templatePositions[index].type == "joint":
                        #mirrorBlock.templatePositions[index].SetAttr("radius", block.templatePositions[index].GetAttr("radius"))
                        mirrorBlock.templatePositions[index].radius = block.templatePositions[index].radius

                    wantedScale = block.templatePositions[index].localScale
                    if not mc.getAttr(mirrorBlock.templatePositions[index].GetAttrString('sx'), l=True):
                        mirrorBlock.templatePositions[index].SetAttr('sx', wantedScale.x)
                    if not mc.getAttr(mirrorBlock.templatePositions[index].GetAttrString('sy'), l=True):
                        mirrorBlock.templatePositions[index].SetAttr('sy', wantedScale.y)
                    if not mc.getAttr(mirrorBlock.templatePositions[index].GetAttrString('sz'), l=True):
                        mirrorBlock.templatePositions[index].SetAttr('sz', wantedScale.z)

            for attr in mc.listAttr(block.name, ud=True, v=True, unlocked=True):
                mirrorBlock.SetAttr( attr, block.GetAttr(attr) )
                if attr == "reverseUp":
                    mirrorBlock.SetAttr( attr, 1-block.GetAttr(attr) )
                if attr == "reverseForward":
                    mirrorBlock.SetAttr( attr, 1-block.GetAttr(attr) )	

        # mirror child blocks
        for attachPoint in block.attachPoints:
            for child in attachPoint.children:
                childBlock = Block.LoadRigBlock( child )
                if childBlock:
                    Block.MirrorBlockPush(childBlock)
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
def MirrorSelectedBlocks( reflectionVector = MATH.Vector3(1,0,0) ):
    '''Mirrors the template positions from the block to the mirrorBlock across the reflection vector transformed from the root block'''

    for blockName in mc.ls(sl=True):
        currentBlock = Block.LoadRigBlock( GetNodeType(blockName) )
        if currentBlock:
            Block.MirrorBlock(currentBlock)

def MirrorBlockPush( block, reflectionVector = MATH.Vector3(1,0,0) ):
    '''Mirrors the given block to the corresponding block on the other side'''

    mirrorBlock = block.GetMirrorBlock()

    Block.MirrorBlock(block, mirrorBlock, reflectionVector)

def MirrorBlockPull( block, reflectionVector = MATH.Vector3(1,0,0) ):
    '''Mirrors the given block using the mirrorBlock's template positions'''

    mirrorBlock = block.GetMirrorBlock()

    Block.MirrorBlock(mirrorBlock, block, reflectionVector)
    
#=============================================================================================================
#>> blockDat
#=============================================================================================================
def blockDat_get(self,report = True):
    """
    Carry from Bokser stuff...
    """
    try:
        _l_udMask = ['blockDat','attributeAliasList','blockState','mClass','mClassGrp','mNodeID','version']
        _ml_controls = self.getControls(True)
        _short = self.p_nameShort
        _blockState_int = self.getState(False)
        #Trying to keep un assertable data out that won't match between two otherwise matching RigBlocks
        _d = {#"name":_short, 
              "blockType":self.blockType,
              "blockState":self.p_blockState,
              "baseName":self.getMayaAttr('cgmName'), 
              #"part":self.part,
              ##"blockPosition":self.getEnumValueString('position'),
              ##"blockDirection":self.getEnumValueString('side'),
              ###"attachPoint":self.getEnumValueString('attachPoint'),
              #"_rig":self._rig.name if self._rig else None, 
              #"_template":self._template.name if self._template else None, 
              #"_controls":self._controls.name if self._controls else None, 
              #"_attach":self._attach.name if self._attach else None, 
              #"_noTouch":self._noTouch.name if self._noTouch else None, 
              #"controls":[mObj.mNode for mObj in _ml_controls],
              "positions":[mObj.p_position for mObj in _ml_controls],
              "orientations":[mObj.p_orient for mObj in _ml_controls],
              "scale":[mObj.scale for mObj in _ml_controls],
              "isSkeletonized":self.isSkeletonized(),
              #...these will be indexed against the number of handles
              #"templatePositions":[x.name for x in self.templatePositions or []], 
              #"templateOrientation":[x.name for x in self.templateOrientation or []], 
              #"templateNodes":[x.name for x in self.templateNodes or []], 
              #"controls":[x.name for x in self.controls or []], 
              #"rigJoints":[x.name for x in self.rigJoints or []], 
              #"skinJoints":[x.name for x in self.skinJoints or []], 
              #"ikJoints":[x.name for x in self.ikJoints or []], 
              #"fkJoints":[x.name for x in self.fkJoints or []], 
              #"ikControls":[x.name for x in self.ikControls or []], 
              #"fkControls":[x.name for x in self.fkControls or []], 
              #"settingsControl":self.settingsControl.name if self.settingsControl else None, 
              #"ikSwitchNodes":[x.name for x in self.ikSwitchNodes or []], 
              #"fkSwitchNodes":[x.name for x in self.fkSwitchNodes or []], 
              #"attachPoints":[x.name for x in self.attachPoints or []],
              "version":self.version, 
              "ud":{}
              }   

        if self.getShapes():
            _d["size"] = POS.get_axisBox_size(self.mNode,False),
        else:
            _d['size'] = self.baseSize

        if _blockState_int >= 1:
            _d['template'] = self.getBlockDat_templateControls()

        #if _blockState_int >= 2:
            #_d['prerig'] = self.getBlockDat_prerigControls() 

        for a in self.getAttrs(ud=True):
            if a not in _l_udMask:
                _type = ATTR.get_type(_short,a)
                if _type in ['message']:
                    continue
                elif _type == 'enum':
                    _d['ud'][a] = ATTR.get_enumValueString(_short,a)                    
                else:
                    _d['ud'][a] = ATTR.get(_short,a)

        if report:cgmGEN.walk_dat(_d,'[{0}] blockDat'.format(self.p_nameShort))
        return _d
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
def blockDat_save(self):
    self.blockDat = self.getBlockDat()

def blockDat_reset(self):
    #This needs more work.
    self._factory.verify(self.blockType, forceReset=True) 

def blockDat_load(self, blockDat = None, mirror=False, reflectionVector = MATH.Vector3(1,0,0)):
    _short = self.p_nameShort        
    _str_func = '[{0}] loadBlockDat'.format(_short)
    ml_processed = []
    
    def mirrorHandle(mObj,pos=None,orient=None):
        """
        if no values passed, use current
        """
        if mObj in ml_processed:
            log.debug("|{0}| >> Obj [{1}] {2} already processed".format(_str_func, i, mObj.p_nameShort))                            
            return
        log.debug("|{0}| >> Obj [{1}] {2}".format(_str_func, i, mObj.p_nameShort))            

        if pos:
            posBase = mObj.p_positionEuclid
            #posNew = (mObj.p_positionEuclid - self.p_positionEuclid).reflect(rootReflectionVector) + self.p_positionEuclid
            posNew = mObj.p_positionEuclid.reflect(rootReflectionVector)
            #posNew = MATH.Vector3(pos[0],pos[1],pos[2]).reflect(rootReflectionVector)
            log.debug("|{0}| >> Mirror pos [{1}] | base: {2} | result: {3}".format(_str_func, i, posBase,posNew))
            mObj.p_positionEuclid = posNew
        
        if orient:
            reflectAim = mObj.getTransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
            reflectUp  = mObj.getTransformDirection( MATH.Vector3(0,-1,0)).reflect( rootReflectionVector )
            reflectAimPoint = DIST.get_pos_by_vec_dist(mObj.p_position, [reflectAim.x,reflectAim.y,reflectAim.z], 100)
            log.debug("|{0}| >> Mirror rot [{1}] | aim: {2} | up: {3} | point: {4}".format(_str_func, i, reflectAim,reflectUp,reflectAimPoint))
            
            #mObj.LookRotation( reflectAim, reflectUp )
            SNAP.aim_atPoint(mObj.mNode,reflectAimPoint, vectorUp=reflectUp,mode='vector')
            #reflectAim = block.templatePositions[index].TransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
            #reflectUp  = block.templatePositions[index].TransformDirection( MATH.Vector3(0,1,0)).reflect( rootReflectionVector )
            #mirrorBlock.templatePositions[index].LookRotation( reflectAim, reflectUp )
            
    
    if blockDat is None:
        log.debug("|{0}| >> No blockDat passed. Checking self...".format(_str_func))    
        blockDat = self.blockDat

    if not issubclass(type(blockDat),dict):
        raise ValueError,"|{0}| >> blockDat must be dict. type: {1} | blockDat: {2}".format(_str_func,type(blockDat),blockDat) 
    

    _blockType = blockDat.get('blockType')
    if _blockType != self.blockType:
        raise ValueError,"|{0}| >> blockTypes don't match. self: {1} | blockDat: {2}".format(_str_func,self.blockType,_blockType) 
    
    log.debug("|{0}| >> blockDat looks good...".format(_str_func))    
    
    if mirror:
        #rootReflectionVector = TRANS.transformDirection(_short,reflectionVector).normalized()
        rootReflectionVector = reflectionVector
        log.debug("|{0}| >> Mirror mode. Relect: {1}".format(_str_func,rootReflectionVector))    
        
    
    #.>>>..UD ====================================================================================
    log.debug("|{0}| >> ud...".format(_str_func)+ '-'*80)
    _ud = blockDat.get('ud')
    if not blockDat.get('ud'):
        raise ValueError,"|{0}| >> No ud data found".format(_str_func) 
    for a,v in _ud.iteritems():
        _current = ATTR.get(_short,a)
        if _current != v:
            try:
                if ATTR.get_type(_short,a) in ['message']:
                    log.debug("|{0}| >> userDefined '{1}' skipped. Not loading message data".format(_str_func,a))                     
                else:
                    log.debug("|{0}| >> userDefined '{1}' mismatch. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                    ATTR.set(_short,a,v)
            except Exception,err:
                log.error("|{0}| >> userDefined '{1}' failed to change. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                r9Meta.printMetaCacheRegistry()                
                for arg in err.args:
                    log.error(arg)                      

    #>>State ====================================================================================
    log.debug("|{0}| >> State".format(_str_func) + '-'*80)
    _state = blockDat.get('blockState')
    _current = self.getState()
    if _state != _current:
        log.debug("|{0}| >> States don't match. self: {1} | blockDat: {2}".format(_str_func,_current,_state)) 
        self.p_blockState = _state

    #>>Controls ====================================================================================
    log.debug("|{0}| >> Controls".format(_str_func)+ '-'*80)
    _pos = blockDat.get('positions')
    _orients = blockDat.get('orientations')
    _scale = blockDat.get('scale')
    

    _ml_controls = self.getControls(True)
    if len(_ml_controls) != len(_pos):
        log.error("|{0}| >> Control dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( _ml_controls),len(_pos))) 
    else:
        log.debug("|{0}| >> loading Controls...".format(_str_func))
        for i,mObj in enumerate(_ml_controls):
            if mObj in ml_processed:
                log.debug("|{0}| >> Obj [{1}] {2} already processed".format(_str_func, i, mObj.p_nameShort))                            
                continue
            
            log.debug("|{0}| >> Obj [{1}] {2}".format(_str_func, i, mObj.p_nameShort))
            pos = _pos[i]
            orient = _orients[i]
            
            mObj.p_position = pos
            mObj.p_orient = orient
            if mirror:
                mirrorHandle(mObj,pos,orient)
            
            ml_processed.append(mObj)
                
            """
            posBase = mObj.p_positionEuclid
            #posNew = (mObj.p_positionEuclid - self.p_positionEuclid).reflect(rootReflectionVector) + self.p_positionEuclid
            posNew = mObj.p_positionEuclid.reflect(rootReflectionVector)
            log.debug("|{0}| >> Mirror pos [{1}] | base: {2} | result: {3}".format(_str_func, i, posBase,posNew))
            mObj.p_positionEuclid = posNew
            
            reflectAim = mObj.getTransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
            reflectUp  = mObj.getTransformDirection( MATH.Vector3(0,-1,0)).reflect( rootReflectionVector )
            reflectAimPoint = DIST.get_pos_by_vec_dist(mObj.p_position, [reflectAim.x,reflectAim.y,reflectAim.z], 100)
            log.debug("|{0}| >> Mirror rot [{1}] | aim: {2} | up: {3} | point: {4}".format(_str_func, i, reflectAim,reflectUp,reflectAimPoint))
            
            #mObj.LookRotation( reflectAim, reflectUp )
            SNAP.aim_atPoint(mObj.mNode,reflectAimPoint, vectorUp=reflectUp,mode='vector')
            #reflectAim = block.templatePositions[index].TransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
            #reflectUp  = block.templatePositions[index].TransformDirection( MATH.Vector3(0,1,0)).reflect( rootReflectionVector )
            #mirrorBlock.templatePositions[index].LookRotation( reflectAim, reflectUp )
            """
                
                
            
#(block.templatePositions[index].position - rootTransform.templatePositions[0].position).reflect( rootReflectionVector ) + rootTransform.templatePositions[0].position
            
            for ii,v in enumerate(_scale[i]):
                _a = 's'+'xyz'[ii]
                if not self.isAttrConnected(_a):
                    ATTR.set(_short,_a,v)
    
    #>>Template Controls ====================================================================================
    _int_state = self.getState(False)
    if _int_state > 0:
        log.info("|{0}| >> template dat....".format(_str_func))             
        _d_template = blockDat.get('template',False)
        if not _d_template:
            log.error("|{0}| >> No template data found in blockDat".format(_str_func)) 
        else:
            if _int_state == 1:
                _ml_templateHandles = self.msgList_get('templateHandles',asMeta = True)            
            else:
                _ml_templateHandles = self.msgList_get('prerigHandles',asMeta = True)                


            #_ml_templateHandles = self.msgList_get('templateHandles',asMeta = True)
            if not _ml_templateHandles:
                log.error("|{0}| >> No template handles found".format(_str_func))
            else:
                _posTempl = _d_template.get('positions')
                _orientsTempl = _d_template.get('orientations')
                _scaleTempl = _d_template.get('scales')
                _jointHelpers = _d_template.get('jointHelpers')

                if len(_ml_templateHandles) != len(_posTempl):
                    log.error("|{0}| >> Template handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( _ml_templateHandles),len(_posTempl))) 
                else:
                    for i,mObj in enumerate(_ml_templateHandles):
                        if mObj in ml_processed:
                            log.debug("|{0}| >> Obj [{1}] {2} already processed".format(_str_func, i, mObj.p_nameShort))                            
                            continue
                        
                        log.debug ("|{0}| >> TemplateHandle: {1}".format(_str_func,mObj.mNode))
                        mObj.p_position = _posTempl[i]
                        mObj.p_orient = _orientsTempl[i]
                        
                        _tmp_short = mObj.mNode
                        for ii,v in enumerate(_scaleTempl[i]):
                            _a = 's'+'xyz'[ii]
                            if not self.isAttrConnected(_a):
                                ATTR.set(_tmp_short,_a,v)   
                        if _jointHelpers and _jointHelpers[i]:
                            mObj.jointHelper.translate = _jointHelpers[i]
                            
            if _d_template.get('rootOrientHelper'):
                if self.getMessage('orientHelper'):
                    self.orientHelper.p_orient = _d_template.get('rootOrientHelper')
                else:
                    log.error("|{0}| >> Found root orient Helper data but no orientHelper control".format(_str_func))



    #>>Generators ====================================================================================
    log.debug("|{0}| >> Generators".format(_str_func)+ '-'*80)
    _d = {"isSkeletonized":[self.isSkeletonized,self.doSkeletonize,self.deleteSkeleton]}

    for k,calls in _d.iteritems():
        _block = bool(blockDat.get(k))
        _current = calls[0]()
        if _state != _current:
            log.debug("|{0}| >> {1} States don't match. self: {2} | blockDat: {3}".format(_str_func,k,_current,_block)) 
            if _block == False:
                calls[2]()                         
            else:
                calls[1]()     
    return True


#=============================================================================================================
#>> Controls query
#=============================================================================================================
def get_blockDagNodes(self,):
    try:
        _short = self.p_nameShort
        _str_func = 'get_blockDagNodes'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        ml_controls = controls_get(self)
                
        for a in ['proxyHelper','prerigLoftMesh','jointLoftMesh']:
            if self.getMessage(a):
                ml_controls.extend(self.getMessage(a,asMeta=True))        
        return ml_controls
    except Exception,err:cgmGEN.cgmException(Exception,err)

def controls_get(self,template = True, prerig= True):
    try:
        
        _short = self.p_nameShort        
        _str_func = '[{0}] controls_get'.format(_short)
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
        
        def addMObj(mObj):
            if mObj in ml_controls:
                log.debug("|{0}| >> Already stored: {1} ".format(_str_func,mObj))                    
                return
            ml_controls.append(mObj)
            if mObj.getMessage('orientHelper'):
                addMObj(mObj.orientHelper)
            if mObj.getMessage('jointHelper'):
                addMObj(mObj.jointHelper)            
            
        
        ml_controls = [self]
        
        if self.getMessage('orientHelper'):
            ml_controls.append(self.orientHelper)
            
        if template:
            log.debug("|{0}| >> template pass...".format(_str_func))            
            ml_handles = self.msgList_get('templateHandles',asMeta = True)
            for mObj in ml_handles:
                addMObj(mObj)
                
        if prerig:
            log.debug("|{0}| >> Prerig pass...".format(_str_func))                        
            ml_handles = self.msgList_get('prerigHandles',asMeta = True)
            for mObj in ml_handles:
                addMObj(mObj)

        return ml_controls
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def controls_mirror(blockSource, blockMirror = None, mirrorMode = 'push', reflectionVector = MATH.Vector3(1,0,0), template = True, prerig= True, ):
    try:
        _short = blockSource.p_nameShort        
        _str_func = '[{0}] controls_mirror'.format(_short)
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
        
        ml_controls = controls_get(blockSource, template, prerig)
        int_lenSource = len(ml_controls)
        if blockMirror is None:
            log.debug("|{0}| >> Self mirror....".format(_str_func))
            ml_targetControls = ml_controls
        else:
            log.debug("|{0}| >> Mirror Target: {1}....".format(_str_func,blockMirror.p_nameShort))
            ml_targetControls = controls_get(blockMirror,template,prerig)
            int_lenTarget = len(ml_targetControls)
            if int_lenTarget!=int_lenSource:
                raise ValueError,"Control list lengths do not match. "
        
        l_dat = []
        
        if not ml_controls:
            raise ValueError,"No controls"
        
        #Root ----------------------------------------------------------------------------------
        log.debug("|{0}| >> root dat...".format(_str_func))
        
        mRoot = ml_controls[0]
        
        rootReflectionVector = reflectionVector
        log.debug("|{0}| >> root Reflect: {1}".format(_str_func,reflectionVector))
        
        posBase = mRoot.p_positionEuclid
        posNew = mRoot.p_positionEuclid.reflect(reflectionVector)
        log.debug("|{0}| >> Root base: {1} | result: {2}".format(_str_func, posBase,posNew))
        #mRoot.p_positionEuclid = posNew
        
        reflectAim = mRoot.getTransformDirection( MATH.Vector3(0,0,1)).reflect( reflectionVector )
        reflectUp  = mRoot.getTransformDirection( MATH.Vector3(0,-1,0)).reflect( reflectionVector )
        reflectAimPoint = DIST.get_pos_by_vec_dist(posNew, [reflectAim.x,reflectAim.y,reflectAim.z], 100)
        log.debug("|{0}| >> Root rot: aim: {1} | up: {2} | point: {3}".format(_str_func, reflectAim,reflectUp,reflectAimPoint))

        #SNAP.aim_atPoint(mRoot.mNode,reflectAimPoint, vectorUp=reflectUp,mode='vector')
        
        
        
        #l_dat.append([posNew,reflectAimPoint,reflectUp,reflectAim])
        l_dat.append({'pos':posNew,'aimPoint':reflectAimPoint,'up':reflectUp,'aim':reflectAim,'scale':mRoot.scale})
        

        #Other controls ------------------------------------------------------------------------
        #rootReflectionVector = TRANS.transformDirection(_short,reflectionVector).normalized()
        #log.debug("|{0}| >> reg Reflect: {1}".format(_str_func,rootReflectionVector))
        log.debug("|{0}| >> control dat...".format(_str_func))
        
        for i,mObj in enumerate(ml_controls[1:]):
            log.debug("|{0}| >> Get mObj: {1}".format(_str_func,mObj.p_nameShort))
            
            posBase = mObj.p_positionEuclid
            #posNew = (mObj.p_positionEuclid - self.p_positionEuclid).reflect(rootReflectionVector) + self.p_positionEuclid
            posNew = mObj.p_positionEuclid.reflect(reflectionVector)            
            log.debug("|{0}| >> Mirror pos [{1}] | base: {2} | result: {3}".format(_str_func, i, posBase,posNew))
            #mObj.p_positionEuclid = posNew
        
            reflectAim = mObj.getTransformDirection( MATH.Vector3(0,0,1)).reflect( reflectionVector )
            reflectUp  = mObj.getTransformDirection( MATH.Vector3(0,1,0)).reflect( reflectionVector )
            #reflectAim = mObj.getTransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
            #reflectUp  = mObj.getTransformDirection( MATH.Vector3(0,1,0)).reflect( rootReflectionVector )
            reflectAimPoint = DIST.get_pos_by_vec_dist(posNew, [reflectAim.x,reflectAim.y,reflectAim.z], 100)
            log.debug("|{0}| >> Mirror rot [{1}] | aim: {2} | up: {3} | point: {4}".format(_str_func, i, reflectAim,reflectUp,reflectAimPoint))
    
            #mObj.LookRotation( reflectAim, reflectUp )
            #SNAP.aim_atPoint(mObj.mNode,reflectAimPoint, vectorUp=reflectUp,mode='vector')
            #reflectAim = block.templatePositions[index].TransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
            #reflectUp  = block.templatePositions[index].TransformDirection( MATH.Vector3(0,1,0)).reflect( rootReflectionVector )
            #mirrorBlock.templatePositions[index].LookRotation( reflectAim, reflectUp )            
            #l_dat.append([posNew,reflectAimPoint,reflectUp,reflectAim])
            l_dat.append({'pos':posNew,'aimPoint':reflectAimPoint,'up':reflectUp,'aim':reflectAim, 'scale':mObj.scale})
            
        
        log.debug("|{0}| >> remap pass values...".format(_str_func))
        md_remap = {}
        for i,mObj in enumerate(ml_targetControls):
            if 'pivotHelper' in mObj.p_nameShort:
                if not md_remap.get('pivotHelper'):
                    md_remap['pivotHelper'] = {}
                    
                _cgmName = mObj.cgmName
                if _cgmName == 'left':
                    md_remap['pivotHelper']['right'] = i
                elif _cgmName == 'right':
                    md_remap['pivotHelper']['left'] = i

        log.debug("|{0}| >> push values...".format(_str_func))
        for i,mObj in enumerate(ml_targetControls):
            try:
                _dat = l_dat[i]
                
                if 'pivotHelper' in mObj.p_nameShort:
                    _cgmName = mObj.cgmName
                    
                    if _cgmName in ['left','right']:
                        _dat = l_dat[ md_remap['pivotHelper'][_cgmName] ]
    
                log.debug("|{0}| >> Push mObj: {1}".format(_str_func,mObj.p_nameShort))            
                mObj.p_positionEuclid = _dat['pos']
                
                SNAP.aim_atPoint(mObj.mNode, _dat['aimPoint'], vectorUp=_dat['up'],mode='vector')
                
                try:mObj.scale = _dat['scale']
                except Exception,err:log.debug("|{0}| >> scale err: {1}".format(_str_func,err))            
            except Exception,err:
                log.debug("|{0}| >> mObj failure: {1} | {2}".format(_str_func,mObj.p_nameShort,err))            
            
        return l_dat,md_remap
    
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def controlsRig_reset(self):
    try:
        
        _short = self.p_nameShort        
        _str_func = '[{0}] controlsRig_reset'.format(_short)
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
        
        self.moduleTarget.rigNull.moduleSet.reset()
        
    except Exception,err:cgmGEN.cgmException(Exception,err)


_d_attrStateMasks = {0:[],
                     1:['basicShape'],
                     2:['baseSizeX','baseSizeY','baseSizeZ','blockScale','proxyShape','shapeDirection'],
                     3:['hasJoint','side','position','attachPoint']}

def uiQuery_getStateAttrs(self,mode = None):
    try:
        _str_func = ' uiQuery_getStateAttrs'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        _short = self.mNode
        
        if mode is None:
            _intState = self.getState(False)
        else:
            _intState = mode
        log.debug("|{0}| >> state: {1}".format(_str_func,_intState))
            
        #First pass...
        l_attrs = []
        for a in self.getAttrs(ud=True):
            _type = ATTR.get_type(_short,a)
            if not ATTR.is_hidden(_short,a) or ATTR.is_keyable(_short,a):
                l_attrs.append(a)
            elif _type in ['string']:
                if '_' in a and not a.endswith('dict'):
                    l_attrs.append(a)
                elif a.startswith('name'):
                    l_attrs.append(a)
            #elif a in ['puppetName','cgmName']:
            #    _l_attrs.append(a)
            if _type in ['float3']:
                l_attrs.remove(a)
        
        for a in ['visibility','blockScale']:
            if ATTR.has_attr(_short,a) and ATTR.is_keyable(_short,a):
                l_attrs.append(unicode(a))
                
        for a in ['side','position']:
            if a in l_attrs:
                l_attrs.remove(a)
        
        if _intState > 0:#...template
            l_mask = []
            log.debug("|{0}| >> template cull...".format(_str_func))            
            for a in l_attrs:
                if not a.startswith('base'):
                    l_mask.append(a)
            l_attrs = l_mask        
            
        if _intState > 1:#prerig up
            l_mask = []
            log.debug("|{0}| >> prerig up cull...".format(_str_func))            
            for a in l_attrs:
                if not a.startswith('add'):
                    l_mask.append(a)
            l_attrs = l_mask
            
        for i in range(0,_intState):
            l_mask = _d_attrStateMasks[i+1]
            log.debug("|{0}| >> {1} mask: {2}".format(_str_func,i,l_mask))                        
            for a in l_mask:
                if a in l_attrs:
                    l_attrs.remove(a)
                    
        l_attrs.sort()
        return l_attrs

     
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
#=============================================================================================================
#>> State Changing
#=============================================================================================================
def templateDelete(self):
    _str_func = 'templateDelete'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError,"|{0}| >> referenced node: {1}".format(_str_func,self.mNode)

    _str_state = self.blockState
    
    if _str_state != 'template':
        raise ValueError,"[{0}] is not in template state. state: {1}".format(self.mNode, _str_state)

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    self.blockState = 'template>define'#...buffering that we're in process

    mBlockModule = self.p_blockModule
    l_blockModuleKeys = mBlockModule.__dict__.keys()
    if 'templateDelete' in l_blockModuleKeys:
        log.debug("|{0}| >> BlockModule templateDelete call found...".format(_str_func))
        self.atBlockModule('templateDelete')
    
    if self.getMessage('templateNull'):
        mc.delete(self.getMessage('templateNull'))
    
    if 'define' in l_blockModuleKeys:
        log.debug("|{0}| >> BlockModule define call found...".format(_str_func))
        self.atBlockModule('define')
    
    mc.delete(self.getShapes())
    
    d_links = get_stateLinks(self, 'template')
    delete_msgDat(self,d_links)
    
    self.blockState = 'define'#...yes now in this state
    return True

def template(self):
    _str_func = 'template'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError,"|{0}| >> referenced node: {1}".format(_str_func,self.mNode)

    _str_state = self.blockState
    
    if _str_state == 'template':
        log.debug("|{0}| >> Already in template state...".format(_str_func))                    
        return True
    elif _str_state != 'define':
        raise ValueError,"[{0}] is not in define state. state: {1}".format(self.mNode, _str_state)

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    self.blockState = 'define>template'#...buffering that we're in process

    mBlockModule = self.p_blockModule

    if 'template' in mBlockModule.__dict__.keys():
        log.debug("|{0}| >> BlockModule call found...".format(_str_func))            
        self.atBlockModule('template')

    #for mShape in self.getShapes(asMeta=True):
        #mShape.doName()

    self.blockState = 'template'#...yes now in this state
    return True

def prerig(self):
    _str_func = 'prerig'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError,"|{0}| >> referenced node: {1}".format(_str_func,self.mNode)

    _str_state = self.blockState
    
    if _str_state == 'prerig':
        log.debug("|{0}| >> Already in prerig state...".format(_str_func))                    
        return True
    elif _str_state != 'template':
        raise ValueError,"[{0}] is not in define template. state: {1}".format(self.mNode, _str_state)

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    self.blockState = 'template>prerig'#...buffering that we're in process

    mBlockModule = self.p_blockModule

    if 'prerig' in mBlockModule.__dict__.keys():
        log.debug("|{0}| >> BlockModule prerig call found...".format(_str_func))            
        self.atBlockModule('prerig')

    self.blockState = 'prerig'#...yes now in this state
    return True

def prerigDelete(self):
    _str_func = 'prerigDelete'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError,"|{0}| >> referenced node: {1}".format(_str_func,self.mNode)

    _str_state = self.blockState
    
    if _str_state != 'prerig':
        raise ValueError,"[{0}] is not in prerig state. state: {1}".format(self.mNode, _str_state)

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    self.blockState = 'prerig>template'#...buffering that we're in process

    mBlockModule = self.p_blockModule
    l_blockModuleKeys = mBlockModule.__dict__.keys()
    
    if 'prerigDelete' in l_blockModuleKeys:
        log.debug("|{0}| >> BlockModule prerigDelete call found...".format(_str_func))
        self.atBlockModule('prerigDelete')
    
    d_links = get_stateLinks(self, 'prerig')
    delete_msgDat(self,d_links)
    
    self.blockState = 'template'#...yes now in this state
    return True

def rig(self,**kws):
    _str_func = 'rig'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError,"|{0}| >> referenced node: {1}".format(_str_func,self.mNode)

    _str_state = self.blockState
    
    if _str_state == 'rig':
        log.debug("|{0}| >> Already in rig state...".format(_str_func))                    
        return True
    elif _str_state != 'prerig':
        raise ValueError,"[{0}] is not in prerig template. state: {1}".format(self.mNode, _str_state)

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    self.blockState = 'prerig>rig'#...buffering that we're in process
    if not 'autoBuild' in kws.keys():
        kws['autoBuild'] = True
    self.asRigFactory(**kws)
    if not is_rigged(self):
        log.error("|{0}| >> Failed to return is_rigged...".format(_str_func))                    
        self.blockState = 'prerig'
        return False
    else:
        self.blockState = 'rig'
    skeleton_connectToParent(self)
    return True

def rigDelete(self):
    
    _str_func = 'rigDelete'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError,"|{0}| >> referenced node: {1}".format(_str_func,self.mNode)

    _str_state = self.blockState
    
    if _str_state != 'rig':
        raise ValueError,"[{0}] is not in rig state. state: {1}".format(self.mNode, _str_state)

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    self.blockState = 'rig>prerig'#...buffering that we're in process
    
    mModuleTarget = self.moduleTarget
    if mModuleTarget:
        log.info("|{0}| >> ModuleTarget: {1}".format(_str_func,mModuleTarget))            
        if mModuleTarget.mClass ==  'cgmRigModule':
            #Deform null
            _deformNull = mModuleTarget.getMessage('deformNull')
            if _deformNull:
                log.info("|{0}| >> deformNull: {1}".format(_str_func,_deformNull))                                
                mc.delete(_deformNull)
            #ModuleSet
            _objectSet = mModuleTarget.rigNull.getMessage('moduleSet')
            if _objectSet:
                log.info("|{0}| >> objectSet: {1}".format(_str_func,_objectSet))                                
                mc.delete(_deformNull)                
            #Module                
        elif mModuleTarget.mClass == 'cgmRigPuppet':
            mModuleTarget.masterControl.delete()
        else:
            log.error("|{0}| >> Unknown mClass moduleTarget: {1}".format(_str_func,mModuleTarget))                

    mBlockModule = self.p_blockModule
    l_blockModuleKeys = mBlockModule.__dict__.keys()
    if 'rigDelete' in l_blockModuleKeys:
        log.debug("|{0}| >> BlockModule rigDelete call found...".format(_str_func))
        self.atBlockModule('rigDelete')
    
    self.blockState = 'prerig'#...yes now in this state
    return True

@cgmGEN.Timer
def changeState(self, state = None, rebuildFrom = None, forceNew = False,**kws):
    try:
        _str_func = 'changeState'
        log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
        
        if self.isReferenced():
            raise ValueError,"Referenced node. Cannot verify"
        
    
        #>Validate our data ------------------------------------------------------
        d_upStateFunctions = {'template':template,
                              'prerig':prerig,
                              'rig':rig,
                              }
        d_downStateFunctions = {'define':templateDelete,
                                'template':prerigDelete,
                                'prerig':rigDelete,
                                }
        d_deleteStateFunctions = {'template':templateDelete,
                                  'prerig':prerigDelete,
                                  'rig':rigDelete,
                                  }
        
        stateArgs = BLOCKGEN.validate_stateArg(state)
        _l_moduleStates = BLOCKSHARE._l_blockStates
    
        if not stateArgs:
            log.info("|{0}| >> No state arg.".format(_str_func))            
            return False
    
        _idx_target = stateArgs[0]
        _state_target = stateArgs[1]
    
        log.debug("|{0}| >> Target state: {1} | {2}".format(_str_func,_state_target,_idx_target))
    
        #>>> Meat
        #========================================================================
        currentState = self.getState(False) 
    
        if rebuildFrom:
            log.info("|{0}| >> Rebuid from: {1}".format(_str_func,rebuildFrom))
    
    
        if currentState == _idx_target:
            if not forceNew:
                log.info("|{0}| >> block [{1}] already in {2} state".format(_str_func,self.mNode,currentState))                
                return True
            elif currentState > 0:
                log.info("|{0}| >> Forcing new: {1}".format(_str_func,currentState))                
                currentState_target = self.getState(True) 
                d_deleteStateFunctions[currentState_target](self)
    
        #If we're here, we're going to move through the set states till we get to our spot
        log.debug("|{0}| >> Changing states...".format(_str_func))
        if _idx_target > currentState:
            startState = currentState+1        
            doStates = _l_moduleStates[startState:_idx_target+1]
            log.debug("|{0}| >> Going up. First stop: {1} | All stops: {2}".format(_str_func, _l_moduleStates[startState],doStates))
    
            for doState in doStates:
                #if doState in d_upStateFunctions.keys():
                log.debug("|{0}| >> Up to: {1} ....".format(_str_func, doState))
                if not d_upStateFunctions[doState](self,**kws):
                    log.error("|{0}| >> Failed: {1} ....".format(_str_func, doState))
                    return False
                elif self.getState(True) != doState:
                    log.error("|{0}| >> No errors but failed to query as:  {1} ....".format(_str_func, doState))                    
                    return False
                #else:
                #    log.debug("|{0}| >> No upstate function for {1} ....".format(_str_func, doState))
            return True
        elif _idx_target < currentState:#Going down
            l_reverseModuleStates = copy.copy(_l_moduleStates)
            l_reverseModuleStates.reverse()
            startState = currentState 
            rev_start = l_reverseModuleStates.index( _l_moduleStates[startState] )+1
            rev_end = l_reverseModuleStates.index( _l_moduleStates[_idx_target] )+1
            doStates = l_reverseModuleStates[rev_start:rev_end]
            log.debug("|{0}| >> Going down. First stop: {1} | All stops: {2}".format(_str_func, startState, doStates))
    
            for doState in doStates:
                log.debug("|{0}| >> Down to: {1} ....".format(_str_func, doState))
                if not d_downStateFunctions[doState](self,**kws):
                    log.error("|{0}| >> Failed: {1} ....".format(_str_func, doState))
                    return False 
                elif self.getState(True)  != doState:
                    log.error("|{0}| >> No errors but failed to query as:  {1} ....".format(_str_func, doState))                    
                    return False                
            return True
        else:
            log.error('Forcing recreate')
            if _state_target in d_upStateFunctions.keys():
                if not d_upStateFunctions[_state_target](self):return False
                return True
        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    

def puppet_verify(self):
    """

    """
    try:
        _str_func = 'puppet_verify'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        mPuppet = False
        if self.blockType == 'master':
            log.info("|{0}| >> master...".format(_str_func))                                                    
            if not self.getMessage('moduleTarget'):
                mPuppet = cgmMeta.createMetaNode('cgmRigPuppet')
                self.copyAttrTo('cgmName',mPuppet.mNode,'cgmName',driven='target')
                self.moduleTarget = mPuppet.mNode
                ATTR.set_message(mPuppet.mNode, 'rigBlock', self.mNode,simple = True)
            else:
                mPuppet = self.moduleTarget
            mPuppet.__verify__()
        else:
            log.info("|{0}| >> Non master calling...".format(_str_func))                                                                
            mi_module = self.moduleTarget
            if not mi_module:
                mi_module = module_verify(self)
    
            _bfr = mi_module.getMessage('modulePuppet')
            if _bfr:
                log.debug("|{0}| >> modulePuppet found: {1}".format(_str_func,_bfr))                        
                mPuppet = mi_module.modulePuppet
            else:
                for mBlockParent in self.getBlockParents():
                    if mBlockParent.blockType == 'master':
                        log.debug("|{0}| >> Found puppet on blockParent: {1}".format(_str_func,mBlockParent))                                                
                        mPuppet = mBlockParent.moduleTarget
                if not mPuppet:
                    mPuppet = cgmMeta.createMetaNode('cgmRigPuppet', name = mi_module.getNameAlias())

            mPuppet.connect_module(mi_module)
            mPuppet.gather_modules()#Gather any modules in the chain
    
    
        if not mPuppet.getMessage('masterNull'):
            mPuppet.__verify__()
            """
            if not mPuppet.masterNull.getMessage('blocksGroup'):
                mGroup = cgmMeta.cgmObject(name='blocks')#Create and initialize
                mGroup.doName()
                mGroup.parent = mPuppet.masterNull
        
                mGroup.connectParentNode(mPuppet.masterNull.mNode, 'puppet','blocksGroup') 
                ATTR.set_standardFlags(mGroup.mNode)"""
    
        return mPuppet                
 
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def module_verify(self,queryMode=True):
    """

    """
    try:
        _str_func = 'module_verify'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        if self.blockType == 'master':
            return True
    
        _bfr = self.getMessage('moduleTarget')
        #_kws = self.module_getBuildKWS()
    
        if _bfr:
            log.debug("|{0}| >> moduleTarget found: {1}".format(_str_func,_bfr))            
            mModule = cgmMeta.validateObjArg(_bfr,'cgmObject')
        else:
            log.debug("|{0}| >> Creating moduleTarget...".format(_str_func))  
            mModule = cgmMeta.createMetaNode('cgmRigModule', rigBlock=self)

        ATTR.set(mModule.mNode,'moduleType',self.blockType,lock=True)
        
        return mModule        
 
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def is_rigged(self):
    try:
        _str_func = 'is_rigged'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        if self.blockType == 'master':
            if self.getMessage('moduleTarget'):
                if self.moduleTarget.getMessage('masterControl'):
                    return True
            return False
        return self.moduleTarget.atUtils('is_rigged')

    except Exception,err:cgmGEN.cgmException(Exception,err)
    
    
def getState(self, asString = True):
    d_stateChecks = {'template':is_template,
                     'prerig':is_prerig,
                     'rig':is_rigged}
    try:
        _str_func = 'getState'
        log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
        
        _blockModule = self.p_blockModule
        _goodState = False
        _l_blockStates = BLOCKSHARE._l_blockStates
    
        _state = self.blockState
        if _state not in BLOCKSHARE._l_blockStates:
            log.debug("|{0}| >> Failed a previous change: {1}. Reverting to previous".format(_str_func,_state))                    
            _state = _state.split('>')[0]
            self.blockState = _state
            self.changeState(_state),#rebuild=True)
    
        if _state == 'define':
            _goodState = 'define'
        else:
            if d_stateChecks[_state](self):
                log.debug("|{0}| >> default test passed.".format(_str_func))
                _goodState = _state
                
            if 'is_{0}'.format(_state) in _blockModule.__dict__.keys():
                _call = getattr(_blockModule,'is_{0}'.format(_state))
                log.debug("|{0}| >> blockModule test: {1}".format(_str_func, _call))                
                if _call(self):
                    log.debug("|{0}| >> still good...".format(_str_func))
                else:
                    log.debug("|{0}| >> nope...".format(_str_func))                    
                    _goodState = False
                    
            if not _goodState:
                _idx = _l_blockStates.index(_state) - 1
                log.debug("|{0}| >> blockModule test failed. Testing: {1}".format(_str_func, _l_blockStates[_idx]))                
                while _idx > 0 and not self.atUtils('is_{0}'.format(_l_blockStates[_idx])):
                    log.debug("|{0}| >> Failed {1}. Going down".format(_str_func,_l_blockStates[_idx]))
                    _blockModule.__dict__['{0}Delete'.format(_l_blockStates[_idx])](self)
                    #self.changeState(_l_blockStates[_idx])
                    _idx -= 1
                _goodState = _l_blockStates[_idx]
    
    
        if _goodState != self.blockState:
            log.debug("|{0}| >> Passed: {1}. Changing buffer state".format(_str_func,_goodState))                    
            self.blockState = _goodState
    
        if asString:
            return _goodState
        return _l_blockStates.index(_goodState)        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
    
#Profile stuff ==============================================================================================
def profile_getOptions(self ):
    try:
        _str_func = 'profile_getOptions'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        mBlockModule = self.p_blockModule
        log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
        reload(mBlockModule)
        
        try:return mBlockModule.d_block_profiles.keys()
        except Exception,err:
            return log.error("|{0}| >>  Failed to query. | {1}".format(_str_func,err))
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
        
def profile_load(self, arg):
    _str_func = 'profile_load'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    _short = self.mNode
    mBlockModule = self.p_blockModule
    log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
    reload(mBlockModule)
    try:_d = mBlockModule.d_block_profiles[arg]
    except Exception,err:
        return log.error("|{0}| >>  Failed to query. | {1} | {2}".format(_str_func,err, Exception))
    
    cgmGEN.func_snapShot(vars())
    log.debug("|{0}| >>  {1}...".format(_str_func,arg))    
    for a,v in _d.iteritems():
        try:
            log.debug("|{0}| attr >> '{1}' | v: {2}".format(_str_func,a,v)) 
            
            if issubclass(type(v),list):
                if self.datList_exists(a):
                    mc.select(cl=True)
                    ATTR.datList_connect(_short, a, v, mode='string')                    
            else:
                ATTR.set(_short,a,v)
        except Exception,err:
            log.error("|{0}| Set attr Failure >> '{1}' | value: {2} | err: {3}".format(_str_func,a,v,err)) 

        
        