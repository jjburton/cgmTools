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
log.setLevel(logging.INFO)
#========================================================================

import maya.cmds as mc
import maya.mel as mel
# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as PUPPETMETA
from cgm.core import cgm_RigMeta as RIGMETA
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.lib.arrange_utils as ARRANGE
reload(ARRANGE)
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as CORERIG
from cgm.core.mrs.lib import general_utils as BLOCKGEN
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.name_utils as NAMES
import cgm.core.lib.surface_Utils as SURF
import cgm.core.lib.locator_utils as LOC
import cgm.core.mrs.lib.builder_utils as BUILDUTILS
from cgm.core.lib import nameTools as NAMETOOLS
import cgm.core.classes.DraggerContextFactory as DRAGFACTORY
import cgm.core.lib.list_utils as LISTS
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.skin_utils as CORESKIN
import cgm.core.lib.string_utils as STR
reload(ATTR)
#=============================================================================================================
#>> Queries
#=============================================================================================================
def get_side(self):
    _side = 'center' 
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side') 
    return _side

def reorder_udAttrs(self):
    ATTR.reorder_ud(self.mNode)


def get_sideMirror(self):
    _side = get_side(self)
    if _side == 'left':return 'right'
    elif _side == 'right':return 'left'
    return False
    
def blockParent_getAttachPoint(self, mode = 'end',noneValid = True):
    _str_func = 'get_attachPoint'
    log.debug(cgmGEN.logString_start(_str_func))

    log.debug("|{0}| >> NOT SURE WE NEED THIS!!!!!".format(_str_func,self)+ '-'*80)
    
    mBlockParent = self.p_blockParent
    if not mBlockParent:
        log.error("|{0}| >> Must have block parent".format(_str_func))        
        return False
    
    mParentModule = mBlockParent.getMessage('moduleTarget',asMeta=True)
    
    if not mParentModule:
        log.debug("|{0}| >> mParentModule: {1}".format(_str_func,mParentModule))        
        if mBlockParent.getMessage('modulePuppet'):
            if mBlockParent.modulePuppet.getMessage('rootJoint'):
                log.debug("|{0}| >> Root joint on master found".format(_str_func))
                return mBlockParent.modulePuppet.rootJoint[0]
            return False
        raise RuntimeError,"Shouldn't have gotten here"    
    
    else:
        mParentModule = mParentModule[0]
        log.debug("|{0}| >> moduleParent: {1}".format(_str_func,mParentModule))
        
        ml_targetJoints = mParentModule.rigNull.msgList_get('moduleJoints',asMeta = True, cull = True)
        
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

def verify_blockAttrs(self, blockType = None, forceReset = False, queryMode = True, extraAttrs = None):
    """
    Verify the attributes of a given block type
    
    force - overrides the excpetion on a failure
    """
    try:
        _str_func = 'verify_blockAttrs'
        _short = self.mNode
        log.debug(cgmGEN.logString_start(_str_func))

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
        
        try:d_defaultSettings.update(mBlockModule.d_block_profiles[self.blockProfile])
        except Exception,err:
            log.debug(cgmGEN.logString_msg(_str_func,'Failed to query blockProfile defaults | {0}'.format(err)))
            pass        
    
        try:_l_msgLinks = mBlockModule._l_controlLinks
        except:_l_msgLinks = []
    
        _d = copy.copy(BLOCKSHARE.d_defaultAttrs)
        #pprint.pprint(d_defaultSettings)
        
        _l_standard = mBlockModule.__dict__.get('l_attrsStandard',[])
        log.debug("|{0}| >> standard: {1} ".format(_str_func,_l_standard))                        
        for k in _l_standard:
            if k in BLOCKSHARE._d_attrsTo_make.keys():
                _d[k] = BLOCKSHARE._d_attrsTo_make[k]
                
        if extraAttrs is not None:
            _d.update(extraAttrs)
    
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
                        strValue = ATTR.get_enumValueString(_short,a)
                        self.addAttr(a,initialValue = v, attrType = 'enum', enumName= t, keyable = False)
                        if strValue and strValue in t:ATTR.set(_short,a,strValue)
                elif t == 'stringDatList':
                    if forceReset or not ATTR.datList_exists(_short,a,mode='string'):
                        mc.select(cl=True)
                        if v == None:
                            v = []
                        ATTR.datList_connect(_short, a, v, mode='string')
                elif t == 'enumDatList':
                    if forceReset or not ATTR.datList_exists(_short,a,mode='enum'):
                        mc.select(cl=True)
                        if v == None:
                            v = []
                        if a == 'loftList':
                            enum = BLOCKSHARE._d_attrsTo_make['loftShape']
                        else:
                            enum = 'off:on'
                        ATTR.datList_connect(_short, a, v, mode='enum',enum=enum)                    
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
                log.error("|{0}| Add attr Failure >> '{1}' | defaultValue: {2} | err: {3}".format(_str_func,a,v,err)) 
                _msg= ("|{0}| Add attr Failure >> '{1}' | defaultValue: {2} | err: {3}".format(_str_func,a,v,err))
                if not forceReset:
                    cgmGEN.cgmExceptCB(Exception,err,msg=_msg)                    

        return True
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def set_nameListFromName(self):
    try:
        _short = self.p_nameShort
        _str_func = 'set_nameListFromName'
        log.debug("|{0}| >>...".format(_str_func)+ '-'*80)
        log.debug(self)
        
        _name = self.cgmName
        if self.datList_exists('nameList'):
            _len = len(self.datList_get('nameList'))
            _l = ["{0}_{1}".format(_name,i) for i in range(_len)]
            self.datList_connect('nameList',_l)
            return _l
        return False
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
        
def set_nameTag(self,nameTag = None):
    try:
        _short = self.p_nameShort
        _str_func = 'set_nameTag'
        log.debug(cgmGEN.logString_start(_str_func))

        
        
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
                log.error("|{0}| >> Change cancelled. Verifying name".format(_str_func)+ '-'*80)
                self.doName()
                return False
            
        self.cgmName = nameTag
        self.doName()
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

def set_blockNullTemplateState(self,state=True, define = True, template=True,prerig=True):
    _str_func = 'set_blockNullTemplateState'
    log.debug(cgmGEN.logString_start(_str_func))

    
    self.template = state
    
    if define:
        try:self.defineNull.template = state
        except:pass
        #try:self.noTransDefineNull.template=state
        #except:pass
    if template:
        try:self.templateNull.template = state
        except:pass
        #try:self.noTransTemplateNull.template=state
        #except:pass
    if prerig:
        try:self.prerigNull.template = state
        except:pass
        #try:self.noTransPrerigNull.template=state
        #except:pass        


def doName(self):
    """
    Override to handle difference with rig block

    """
    _short = self.p_nameShort
    _str_func = '[{0}] doName'.format(_short)
    log.debug(cgmGEN.logString_start(_str_func))

    
    _d = NAMETOOLS.returnObjectGeneratedNameDict(_short)

    _direction = self.getEnumValueString('side')
    if _direction != 'none':
        log.debug("|{0}| >>  direction: {1}".format(_str_func,_direction))
        _d['cgmDirection'] = _direction        
        self.doStore('cgmDirection',_direction)
    else:
        if _d.get('cgmDirection'):_d.pop('cgmDirection')
        self.doStore('cgmDirection','')
        log.debug("|{0}| >>  cgmDirection: {1}".format(_str_func,self.cgmDirection))
        

    _position = self.getMayaAttr('position')#self.getEnumValueString('position')
    if _position and _position != '':
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
    #pprint.pprint(vars())
    #Check for special attributes to replace data, name
    _d_new = {}
    for k,v in _d.iteritems():
        if v in ['none','None','NONE',None]:
            continue
        _d_new[k] = v
    log.debug("|{0}| >>  dict: {1}".format(_str_func,_d_new))
    self.rename(NAMETOOLS.returnCombinedNameFromDict(_d_new))
    
    
    if self.getMessage('moduleTarget'):
        log.debug("|{0}| >> Module target naming...".format(_str_func))            
        self.moduleTarget.doName()
        
    
    ml_objs = get_blockDagNodes(self)
    for mObj in ml_objs:
        if mObj != self:
            mObj.doName()
    
    for plug in ['templateNull','noTransTemplateNull',
                 'prerigNull','noTransPrerigNull',
                 'defineNull','noTransDefineNull',
                 'moduleTarget']:
        mPlug = self.getMessageAsMeta(plug)
        if mPlug:
            mPlug.doName()
    """         
    if self.getMessage('templateNull'):
        self.templateNull.doName()
    if self.getMessage('prerigNull'):
        self.prerigNull.doName()
    if self.getMessage('moduleTarget'):
        self.moduleTarget.doName()
    """
        
def set_side(self,side=None):
    try:
        _short = self.p_nameShort
        _str_func = 'set_side'
        log.debug(cgmGEN.logString_start(_str_func))

        
        if str(side).lower() in ['none']:
            side = 0
        try:
            ATTR.set(_short,'side',side)
        except Exception,err:
            log.error("|{0}| >> Failed to change attr. | err: {1}".format(_str_func,err))            
            return False
        
        self.doName()
        color(self)
            
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def set_position(self,position=None,ui=False):
    try:
        _short = self.p_nameShort
        _str_func = 'set_position'
        log.debug(cgmGEN.logString_start(_str_func))

        
        
        if ui:
            log.debug("|{0}| >> getting value by ui prompt".format(_str_func))
            position = self.getMayaAttr('cgmPosition')
            _title = 'Set position tag...'
            result = mc.promptDialog(title=_title,
                                     message='Block: {0} | Current: {1}'.format(_short,position),
                                     button=['OK', 'Cancel'],
                                     text = position,
                                     defaultButton='OK',
                                     cancelButton='Cancel',
                                     dismissString='Cancel')
            if result == 'OK':
                position =  mc.promptDialog(query=True, text=True) or ''
                log.debug("|{0}| >> from prompt: {1}".format(_str_func,position))
            else:
                log.error("|{0}| >> Change cancelled | {1}.".format(_str_func,self))
                #self.doName()
                return False        
        
        try:
            ATTR.set(_short,'position',position)
        except Exception,err:
            log.error("|{0}| >> Failed to change attr. | err: {1}".format(_str_func,err))            
            return False
        
        self.doName()
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

def color(self):
    try:
        _short = self.p_nameShort
        _str_func = 'color'
        log.debug(cgmGEN.logString_start(_str_func))

        
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
        cgmGEN.cgmExceptCB(Exception,err)


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
        log.debug(cgmGEN.logString_start(_str_func))

        
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
        cgmGEN.cgmExceptCB(Exception,err)

#=============================================================================================================
#>> Utilities
#=============================================================================================================


#=============================================================================================================
#>> define
#=============================================================================================================
def define(self):
    _str_func = 'define'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError,"|{0}| >> referenced node: {1}".format(_str_func,self.mNode)

    _str_state = self.blockState
    
    if _str_state != 'define':
        raise ValueError,"[{0}] is not in define template. state: {1}".format(self.mNode, _str_state)

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    mBlockModule = self.p_blockModule
    
    for c in ['define']:
        if c in mBlockModule.__dict__.keys():
            log.debug("|{0}| >> BlockModule {1} call found...".format(_str_func,c))            
            self.atBlockModule(c)

    self.blockState = 'define'#...yes now in this state
    return True
    


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
        log.debug(cgmGEN.logString_start(_str_func))

        return msgDat_check(self, get_stateLinks(self,'template'))
        
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)

def templateDeleteBAK(self,msgLinks = []):
    try:
        _str_func = 'templateDelete'
        log.debug(cgmGEN.logString_start(_str_func))

        
        for link in msgLinks + ['templateNull']:
            if self.getMessage(link):
                log.debug("|{0}| >> deleting link: {1}".format(_str_func,link))                        
                mc.delete(self.getMessage(link))
        return True
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def templateNull_verify(self):
    if not self.getMessage('templateNull'):
        str_templateNull = CORERIG.create_at(self.mNode)
        templateNull = cgmMeta.validateObjArg(str_templateNull, mType = 'cgmObject',setClass = True)
        templateNull.connectParentNode(self, 'rigBlock','templateNull') 
        templateNull.doStore('cgmName', self)
        templateNull.doStore('cgmType','templateNull')
        templateNull.doName()
        templateNull.p_parent = self
        templateNull.setAttrFlags()
    else:
        templateNull = self.templateNull   
    return templateNull

def snap_toBaseDat(self):
    _str_func = 'snap_toBaseDat'
    log.debug(cgmGEN.logString_start(_str_func))

    pos = DIST.get_pos_by_vec_dist(self.p_position, self.baseAim, 100)
    log.debug("|{0}| >>  pos: {1}".format(_str_func,pos))
    
    SNAP.aim_atPoint(self.mNode, pos, mode='vector',vectorUp=self.baseUp )
    
def blockFrame_get(self):
    _str_func = 'blockFrame_get'
    log.debug(cgmGEN.logString_start(_str_func))
    return self.getMessageAsMeta('blockFrame')


def blockFrame_alignTo(self,templateScale = False):
    _str_func = 'blockFrame_get'
    log.debug(cgmGEN.logString_start(_str_func))
    mBlockFrame = self.getMessageAsMeta('blockFrame')
    if not mBlockFrame:
        return log.error(cgmGEN.logString_msg(_str_func,'No blockFrame found'))
    
    mBlockFrame.atBlockModule('subBlock_align',self,templateScale)

    

    
def stateNull_verify(self,state='define'):
    _strPlug = state.lower() + 'Null'
    
    if not self.getMessage(_strPlug):
        str_null = CORERIG.create_at(self.mNode)
        mNull = cgmMeta.validateObjArg(str_null, mType = 'cgmObject',setClass = True)
        mNull.connectParentNode(self, 'rigBlock',_strPlug) 
        mNull.doStore('cgmName', self)
        mNull.doStore('cgmType',_strPlug)
        mNull.doName()
        #mNull.rename(_strPlug)
        mNull.p_parent = self
        mNull.setAttrFlags()
    else:
        mNull = self.getMessageAsMeta(_strPlug)
    return mNull

def create_templateLoftMesh(self, targets = None, mDatHolder = None, mTemplateNull = None,
                            uAttr = 'neckControls',baseName = 'test',plug = 'templateLoftMesh'):
    try:
        _str_func = 'create_templateLoftMesh'
        log.debug(cgmGEN.logString_start(_str_func))

        
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
    
        mLoft.doStore('cgmName',self)
        mLoft.doStore('cgmType','controlsApprox')
        mLoft.doName()
    
        for n in _tessellate,_loftNode:
            mObj = cgmMeta.validateObjArg(n)
            mObj.doStore('cgmName',self)
            mObj.doStore('cgmTypeModifier','controlsApprox')
            mObj.doName()            
    
    
        #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
        #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;
    
        mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
    
        #Color our stuff...
        self.asHandleFactory().color(mLoft.mNode,transparent=True)
        #CORERIG.colorControl(mLoft.mNode,_side,'main',transparent = True)
    
        mLoft.inheritsTransform = 0
        for s in mLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 2   
    
        self.connectChildNode(mLoft.mNode, plug, 'block')    
        return mLoft
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
#=============================================================================================================
#>> Prerig
#=============================================================================================================
def noTransformNull_verify(self,mode='template'):
    try:
        _plug = 'noTrans{0}Null'.format(STR.capFirst(mode[0]) + mode[1:])
        if not self.getMessage(_plug):
            str_prerigNull = mc.group(em=True)
            mNoTransformNull = cgmMeta.validateObjArg(str_prerigNull, mType = 'cgmObject',setClass = True)
            mNoTransformNull.connectParentNode(self, 'rigBlock',_plug) 
            mNoTransformNull.doStore('cgmName', self)
            mNoTransformNull.doStore('cgmType',_plug)
            mNoTransformNull.doName()
    
            mNoTransformNull.dagLock()
            #mNoTransformNull.p_parent = self.prerigNull
            #mNoTransformNull.resetAttrs()
            #mNoTransformNull.setAttrFlags()
            #mNoTransformNull.inheritsTransform = False
        else:
            mNoTransformNull = self.getMessage(_plug,asMeta=True)[0]
    
        return mNoTransformNull    
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def prerigNull_verify(self):
    try:
        if not self.getMessage('prerigNull'):
            str_prerigNull = CORERIG.create_at(self.mNode)
            mPrerigNull = cgmMeta.validateObjArg(str_prerigNull, mType = 'cgmObject',setClass = True)
            mPrerigNull.connectParentNode(self, 'rigBlock','prerigNull') 
            mPrerigNull.doStore('cgmName', self)
            mPrerigNull.doStore('cgmType','prerigNull')
            mPrerigNull.doName()
            mPrerigNull.p_parent = self
            #mPrerigNull.setAttrFlags()
        else:
            mPrerigNull = self.prerigNull    
            
        return mPrerigNull
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def prerig_simple(self):
    _str_func = 'prerig_simple'
    log.debug(cgmGEN.logString_start(_str_func))

    
    _short = self.p_nameShort
    _size = self.baseSize
    _sizeSub = _size * .2
    #_baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
    _side = 'center'
    
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
    
    log.debug("|{0}| >> [{1}] | baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))     
        
    self._factory.module_verify()  
    
    #Create preRig Null  ==================================================================================
    mPrerigNull = prerigNull_verify(self)   
    
    return True

def prerig_delete(self, msgLinks = [], msgLists = [], templateHandles = True):
    try:
        _str_func = 'prerig_delete'
        log.debug(cgmGEN.logString_start(_str_func))
        
        try:self.moduleTarget.delete()
        except:log.debug("|{0}| >> No moduleTarget...".format(_str_func))
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
                log.debug("|{0}| >> Missing msgList: {1}".format(_str_func,l))  
            else:
                mc.delete(_buffer)
        return True   
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def prerig_handlesLock(self, lock=None):
    try:
        _str_func = 'prerig_handlesLock'
        log.debug(cgmGEN.logString_start(_str_func))
        ml_prerigHandles = self.msgList_get('prerigHandles')
        if not ml_prerigHandles:
            return log.error(cgmGEN.logString_msg(_str_func,'No prerigHandles found'))
        if lock:
            mPrerigNull = self.prerigNull
            for mHandle in ml_prerigHandles:
                mLoc = mHandle.getMessageAsMeta('lockLoc')
                if mLoc:
                    mLoc.delete()
                    
                mLoc = mHandle.doLoc()
                mLoc.p_parent = mPrerigNull
                mc.parentConstraint([mLoc.mNode],mHandle.mNode)
                mHandle.connectChildNode(mLoc.mNode,'lockLoc')
        else:
            for mHandle in ml_prerigHandles:            
                mLoc = mHandle.getMessageAsMeta('lockLoc')
                if mLoc:
                    mLoc.delete()
        
        return True   
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)

def delete(self):
    _d_delete = {4:rigDelete,
                 3:skeleton_delete}
    _str_func = 'delete'
    log.debug(cgmGEN.logString_start(_str_func))

    _int_state,_state = BLOCKGEN.validate_stateArg(self.blockState)
    
    _range = range(_int_state+1)
    _range.reverse()
    for i in _range:
        try:
            int_state,state = BLOCKGEN.validate_stateArg(i)
            _subCall = _d_delete.get(int_state)
            if _subCall:
                log.debug("|{0}| >> Found subcall: {1}".format(_str_func,state))                  
                _subCall(self)
            d_links = get_stateLinks(self, state)
            log.debug("|{0}| >> links {1} | {2}".format(_str_func,i,d_links))  
            msgDat_delete(self,d_links)
        except Exception,err:
            log.error(err)
    
    mc.delete(self.mNode)
    return True


def msgDat_delete(self,d_wiring = {}, msgLinks = [], msgLists = [] ):
    _str_func = 'msgDat_delete'
    log.debug(cgmGEN.logString_start(_str_func))
    
    
    _l_missing = []
    for l in d_wiring.get('msgLinks',[]) + msgLinks:
        if l in ['moduleTarget']:
            if self.getMessage(l):
                log.debug("|{0}| >>  Found msgLink: {1} ".format(_str_func,l))
                self.moduleTarget.delete()
        else:
            l_dat = self.getMessage(l)
            if l_dat:
                log.debug("|{0}| >>  Found msgLink: {1} | {2}".format(_str_func,l,l_dat))
                try:mc.delete(l_dat)
                except Exception,err:
                    log.error("|{0}| >>  Failed to delete: {1} | {2} | {3}".format(_str_func,l,l_dat,err))
                
    for l in d_wiring.get('msgLists',[]) + msgLists:
        if self.msgList_exists(l):
            dat = self.msgList_get(l,asMeta=False)
            if dat:
                log.debug("|{0}| >>  Purging msgList: {1} | {2}".format(_str_func,l, 0))
                for o in dat:
                    try:mc.delete(o)
                    except Exception,err:
                        log.error("|{0}| >>  Failed to delete msgList: {1} | {2}".format(_str_func,l,err))                
                #self.msgList_purge(l)
    return True

def msgDat_check(self,d_wiring = {}, msgLinks = [], msgLists = [] ):
    _str_func = 'msgDat_check'
    log.debug(cgmGEN.logString_start(_str_func))
    
    
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
        log.debug("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.debug("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True
    
def get_stateLinks(self, mode = 'template' ):
    try:
        _str_func = 'get_stateLinks'
        log.debug(cgmGEN.logString_start(_str_func))

        
        mBlockModule = self.p_blockModule
        log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
        d_wiring = {}
        try:
            d_wiring.update(getattr(mBlockModule,'d_wiring_{0}'.format(mode)))
            log.debug("|{0}| >>  Found {1} wiring dat in BlockModule".format(_str_func,mode))
        except Exception,err:
            log.debug("|{0}| >>  No {1} wiring dat in BlockModule. error: {2}".format(_str_func,mode,err))
            pass
        
        _noTrans = 'NoTrans' + mode.capitalize() + 'Null'
        if _noTrans not in d_wiring and self.getMessage(_noTrans):
            if not d_wiring.get('msgLinks'):d_wiring['msgLinks'] = []            
            d_wiring['msgLinks'].append(a)
        return d_wiring
        
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def is_prerig(self):
    try:
        _str_func = 'is_prerig'
        log.debug(cgmGEN.logString_start(_str_func))

        return msgDat_check(self, get_stateLinks(self,'prerig'))
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def is_skeleton(self):
    try:
        _str_func = 'is_skeleton'
        log.debug(cgmGEN.logString_start(_str_func))

        
        mBlockModule = self.p_blockModule
    
        if 'skeleton_check' in mBlockModule.__dict__.keys():
            log.debug("|{0}| >> BlockModule skeleton_check call found...".format(_str_func))            
            return self.atBlockModule('skeleton_check')
        else:
            log.error("|{0}| >> Need skeleton_check for: {1}".format(_str_func,self.blockType))            
            
        return True
        
    
        #return False        
        
        return msgDat_check(self, get_stateLinks(self,'skeleton'))
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)

def is_prerigBAK(self, msgLinks = [], msgLists = [] ):
    try:
        _str_func = 'is_prerig'
        log.debug(cgmGEN.logString_start(_str_func))

        
        _l_missing = []
    
        _d_links = {self : ['moduleTarget','prerigNull']}
    
        for l in msgLinks:
            if not self.getMessage(l):
                _l_missing.append(self.p_nameBase + '.' + l)
                
        for l in msgLists:
            if not self.msgList_exists(l):
                _l_missing.append(self.p_nameBase + '.[msgList]' + l)
    
        if _l_missing:
            log.debug("|{0}| >> Missing...".format(_str_func))  
            for l in _l_missing:
                log.debug("|{0}| >> {1}".format(_str_func,l))  
            return False
        return True
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)

def get_castMesh(self):
    mMesh = self.getMessage('prerigLoftMesh', asMeta = True)[0]
    mRebuildNode = mMesh.getMessage('rebuildNode',asMeta=True)[0]
    
    _rebuildState = mRebuildNode.rebuildType
    if _rebuildState != 5:
        mRebuildNode.rebuildType = 5
        
    mCastMesh =  cgmMeta.validateObjArg(mMesh.mNode,'cgmObject').doDuplicate(po=False,ic=False)
    mRebuildNode.rebuildType = _rebuildState
    mCastMesh.parent=False
    return mCastMesh

    
def create_defineLoftMesh(self, targets = None,
                          mNull = None,
                          polyType = 'mesh',
                          baseName = 'test',
                          plug = 'defineLoftMesh'):
    try:
        _str_func = 'create_defineLoftMesh'
        log.debug(cgmGEN.logString_start(_str_func))

        _short = self.mNode
        _side = 'center'
        _rebuildNode = None
        _loftNode = None
        
        if self.getMayaAttr('side'):
            _side = self.getEnumValueString('side')  
                
        log.debug("|{0}| >> Creating: {1}".format(_str_func,polyType))
        
        
                
        _res_body = mc.loft(targets, o = True, d = 1, po = 3, c = False,autoReverse=0)
        mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)                    
        _loftNode = _res_body[1]
        _inputs = mc.listHistory(mLoftSurface.mNode,pruneDagObjects=True)
        _rebuildNode = _inputs[0]            
        mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
        
        _d = {'keepCorners':False}#General}
        
            
        mLoftSurface.overrideEnabled = 1
        mLoftSurface.overrideDisplayType = 2
        
        mLoftSurface.p_parent = mNull
        mLoftSurface.resetAttrs()
    
        mLoftSurface.doStore('cgmName',self)
        mLoftSurface.doStore('cgmType','shapeApprox')
        mLoftSurface.doName()
        log.debug("|{0}| loft node: {1}".format(_str_func,_loftNode)) 
    
        #mc.polySetToFaceNormal(mLoftSurface.mNode,setUserNormal = True)
        #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;
    
        #mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
    
        #Color our stuff...
        log.debug("|{0}| >> Color...".format(_str_func))        
        CORERIG.colorControl(mLoftSurface.mNode,_side,'main',transparent = True)
    
        mLoftSurface.inheritsTransform = 0
        for s in mLoftSurface.getShapes(asMeta=True):
            s.overrideDisplayType = 2    

        toName = [_rebuildNode,_loftNode]

            
        if _rebuildNode:
            mLoftSurface.connectChildNode(_rebuildNode, 'rebuildNode','builtMesh')
            if _loftNode:
                mLoftSurface.connectChildNode(_rebuildNode, 'loftNode','builtMesh')        

        for n in toName:
            mObj = cgmMeta.validateObjArg(n)
            mObj.doStore('cgmName',self)
            mObj.doStore('cgmTypeModifier','prerigMesh')
            mObj.doName()                        
       
        self.connectChildNode(mLoftSurface.mNode, plug, 'block')
        
        return mLoftSurface
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
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
        log.debug(cgmGEN.logString_start(_str_func))

        _short = self.mNode
        _side = 'center'
        _rebuildNode = None
        _loftNode = None
        
        if self.getMayaAttr('side'):
            _side = self.getEnumValueString('side')  
                
        log.debug("|{0}| >> Creating: {1}".format(_str_func,polyType))
        
        if polyType == 'mesh':
            _res_body = mc.loft(targets, o = True, d = 3, po = 1,autoReverse=False)
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
            _inputs = mc.listHistory(mLoftSurface.mNode,pruneDagObjects=True)
        
            _tessellate = _inputs[0]
            _loftNode = _inputs[1]
        
            log.debug("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 
            _d = {'format':2,#General
                  'polygonType':1,#'quads',
                  'uNumber': 1 + len(targets)}
        
            for a,v in _d.iteritems():
                ATTR.set(_tessellate,a,v)  
                
        elif polyType in ['bezier','noMult']:
            _res_body = mc.loft(targets, o = True, d = 1, po = 3, c = False,autoReverse=False)
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)                    
            _loftNode = _res_body[1]
            _inputs = mc.listHistory(mLoftSurface.mNode,pruneDagObjects=True)
            _rebuildNode = _inputs[0]            
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
            
            if polyType == 'bezier':
                mc.reverseSurface(mLoftSurface.mNode, direction=1,rpo=True)
                
            _d = {'keepCorners':False}#General}
            
            if polyType == 'noMult':
                _d['rebuildType'] = 3
        
            for a,v in _d.iteritems():
                ATTR.set(_rebuildNode,a,v)
                
        else:
            _res_body = mc.loft(targets, o = True, d = 3, po = 0,autoReverse=False)
            _loftNode = _res_body[1]
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)        
            
        
        mLoftSurface.overrideEnabled = 1
        mLoftSurface.overrideDisplayType = 2
        
        mLoftSurface.p_parent = mPrerigNull
        mLoftSurface.resetAttrs()
    
        mLoftSurface.doStore('cgmName',self)
        mLoftSurface.doStore('cgmType','shapeApprox')
        mLoftSurface.doName()
        log.debug("|{0}| loft node: {1}".format(_str_func,_loftNode)) 
    
        #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
        #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;
    
        #mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
    
        #Color our stuff...
        log.debug("|{0}| >> Color...".format(_str_func))        
        CORERIG.colorControl(mLoftSurface.mNode,_side,'main',transparent = True)
    
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
            
        if _rebuildNode:
            mLoftSurface.connectChildNode(_rebuildNode, 'rebuildNode','builtMesh')
            if _loftNode:
                mLoftSurface.connectChildNode(_rebuildNode, 'loftNode','builtMesh')        

        for n in toName:
            mObj = cgmMeta.validateObjArg(n)
            mObj.doStore('cgmName',self)
            mObj.doStore('cgmTypeModifier','prerigMesh')
            mObj.doName()                        
       
        self.connectChildNode(mLoftSurface.mNode, 'prerigLoftMesh', 'block')
        
        return mLoftSurface
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def create_simpleTemplateLoftMesh(self, targets = None,
                                  mNull = None,
                                  uAttr = 'loftSplit',
                                  degreeAttr = 'loftDegree',
                                  polyType = 'mesh',
                                  plug = None,
                                  baseName = None,
                                  noReverse = False,
                                  d_rebuild = {},
                                  **kws
                                  ):
    try:
        _str_func = 'create_prerigLoftMesh'
        log.debug(cgmGEN.logString_start(_str_func))

        _short = self.mNode
        _side = 'center'
        _rebuildNode = None
        _loftNode = None
        _b_noReverse = VALID.boolArg(noReverse)
        _plug = plug or baseName+'TemplateLoft'
        _cgmName = baseName or None
        
        if self.getMayaAttr('side'):
            _side = self.getEnumValueString('side')  
                
        log.debug("|{0}| >> Creating: {1}".format(_str_func,polyType))
        
        if polyType == 'mesh':
            _res_body = mc.loft(targets, o = True, d = 3, po = 1,autoReverse=False)
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
            _inputs = mc.listHistory(mLoftSurface.mNode,pruneDagObjects=True)
        
            _tessellate = _inputs[0]
            _loftNode = _inputs[1]
        
            log.debug("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 
            _d = {'format':2,#General
                  'polygonType':1,#'quads',
                  'uNumber': 1 + len(targets)}
        
            for a,v in _d.iteritems():
                ATTR.set(_tessellate,a,v)  
        elif polyType in ['bezier','noMult']:
            _res_body = mc.loft(targets, o = True, d = 1, po = 3, c = False,autoReverse=False)
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)                    
            _loftNode = _res_body[1]
            _inputs = mc.listHistory(mLoftSurface.mNode,pruneDagObjects=True)
            _rebuildNode = _inputs[0]            
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
            
            if polyType == 'bezier' and _b_noReverse is not True:
                mc.reverseSurface(mLoftSurface.mNode, direction=1,rpo=True)
                
            _d = {'keepCorners':False,
                  'keepControlPoints':True}#General}
            
            if polyType == 'noMult':
                _d['rebuildType'] = 3
        
            for a,v in _d.iteritems():
                ATTR.set(_rebuildNode,a,v)
        elif polyType == 'faceLoft':
            _res_body = mc.loft(targets, o = True, d = 1, po = 3, c = False,autoReverse=False)
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)                    
            _loftNode = _res_body[1]
            _inputs = mc.listHistory(mLoftSurface.mNode,pruneDagObjects=True)
            _rebuildNode = _inputs[0]            
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
            
            if kws.get('noRebuild') is not True and _b_noReverse is not True:
                mc.reverseSurface(mLoftSurface.mNode, direction=1,rpo=True)
            _len = len(targets)*2
            _d = {'keepCorners':False,
                  'rebuildType':0,
                  'degreeU':1,
                  'degreeV':3,
                  'keepControlPoints':False,
                  'spansU':_len,
                  'spansV':_len}#General}
            _d.update(d_rebuild)
            
            for a,v in _d.iteritems():
                ATTR.set(_rebuildNode,a,v)
                
            toName = [_loftNode]
                
        else:
            _res_body = mc.loft(targets, o = True, d = 3, po = 0,autoReverse=False)
            _loftNode = _res_body[1]
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)        
            
        
        mLoftSurface.overrideEnabled = 1
        mLoftSurface.overrideDisplayType = 2
        
        mLoftSurface.p_parent = mNull
        mLoftSurface.resetAttrs()
    
        mLoftSurface.doStore('cgmName',_cgmName,attrType='string')
        mLoftSurface.doStore('cgmType','shapeApprox')
        mLoftSurface.doName()
        log.debug("|{0}| loft node: {1}".format(_str_func,_loftNode)) 
    
        #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
        #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;
    
        #mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
    
        #Color our stuff...
        log.debug("|{0}| >> Color...".format(_str_func))        
        CORERIG.colorControl(mLoftSurface.mNode,_side,'main',transparent = True)
    
        mLoftSurface.inheritsTransform = 0
        for s in mLoftSurface.getShapes(asMeta=True):
            s.overrideDisplayType = 2    
        
        if polyType not in ['faceLoft']:
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
                #ATTR.connect("{0}.{1}".format(self.mNode,vAttr), "{0}.vNumber".format(_tessellate)) 
            
                #ATTR.copy_to(_loftNode,'degree',self.mNode,'loftDegree',driven = 'source')
            
                toName = [_tessellate,_loftNode]
            elif polyType in ['bezier','noMult']:
                #_arg = "{0}.out_vSplitPre = {1} + 1".format(targets[0],
                #                                         self.getMayaAttrString(uAttr,'short'))
                        
                #NODEFACTORY.argsToNodes(_arg).doBuild()
                #ATTR.connect("{0}.out_vSplit".format(targets[0]), "{0}.spansU".format(_rebuildNode))
                ATTR.connect("{0}.{1}".format(self.mNode,uAttr), "{0}.spansU".format(_rebuildNode))            
                #ATTR.connect("{0}.{1}".format(self.mNode,vAttr), "{0}.spansV".format(_rebuildNode))
                
                ATTR.connect("{0}.{1}".format(_short,uAttr), "{0}.sectionSpans".format(_loftNode))
                
                #_close = mc.closeSurface(mLoftSurface.mNode,d=1,p=0,rpo=True)
                
                toName = [_rebuildNode,_loftNode]
            else:
                ATTR.connect("{0}.loftSplit".format(_short), "{0}.sectionSpans".format(_loftNode))
                toName = [_loftNode]
            
        if _rebuildNode:
            mLoftSurface.connectChildNode(_rebuildNode, 'rebuildNode','builtMesh')
            if _loftNode:
                mLoftSurface.connectChildNode(_rebuildNode, 'loftNode','builtMesh')        

        for n in toName:
            mObj = cgmMeta.validateObjArg(n)
            
            if _cgmName:
                mObj.addAttr('cgmName',_cgmName,'string')
            else:
                mObj.doStore('cgmName',self)
                
            mObj.doStore('cgmTypeModifier','prerigMesh')
            mObj.doName()                        
       
        self.connectChildNode(mLoftSurface.mNode, _plug, 'block')
        
        return mLoftSurface
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def create_jointLoft(self, targets = None, mPrerigNull = None,
                     uAttr = 'neckJoints', baseCount = 1, baseName = 'test',degree = 1,
                     simpleMode = False):
    
    _str_func = 'create_jointLoft'
    log.debug(cgmGEN.logString_start(_str_func))

    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')  
            
    

    _res_body = mc.loft(targets, o = True, d = 3, po = 1 )
    mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
    _inputs = mc.listHistory(mLoft.mNode,pruneDagObjects=True)

    _tessellate = _inputs[0]
    _loftNode = _inputs[1]
    
    mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)

    log.debug("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 
    _d = {'format':1,#fit, 2 - #General
          'polygonType':1,#'quads',
          'uNumber': baseCount + len(targets)}

    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)  
        
    ATTR.set(_loftNode,'degree',degree)  
    
        

    log.debug("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 

    mLoft.overrideEnabled = 1
    mLoft.overrideDisplayType = 2
    mLoft.p_parent = mPrerigNull
    mLoft.resetAttrs()

    mLoft.doStore('cgmName',self)
    mLoft.doStore('cgmType','jointApprox')
    mLoft.doName()

    #Color our stuff...
    CORERIG.colorControl(mLoft.mNode,_side,'main',transparent = False)

    mLoft.inheritsTransform = 0
    for s in mLoft.getShapes(asMeta=True):
        s.overrideDisplayType = 2    
        
    if not simpleMode:
        #...wire some controls
        _arg = "{0}.out_vSplit = {1} + {2} ".format(targets[0],
                                                 self.getMayaAttrString(uAttr,'short'),
                                                 baseCount)

        NODEFACTORY.argsToNodes(_arg).doBuild()
    
        #rg = "%s.condResult = if %s.ty == 3:5 else 1"%(str_obj,str_obj)
        #NODEFACTORY.argsToNodes(_arg).doBuild()    
    
        ATTR.connect("{0}.out_vSplit".format(targets[0]), "{0}.uNumber".format(_tessellate))  

    for n in _tessellate,_loftNode:
        mObj = cgmMeta.validateObjArg(n)
        mObj.doStore('cgmName',self)
        mObj.doStore('cgmTypeModifier','jointApprox')
        mObj.doName()            

    self.connectChildNode(mLoft.mNode, 'jointLoftMesh', 'block')    
    return mLoft

def create_jointLoftBAK(self, targets = None, mPrerigNull = None,
                     uAttr = 'neckJoints', baseName = 'test'):
    
    _str_func = 'create_jointLoftBAK'
    log.debug(cgmGEN.logString_start(_str_func))

    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')  
            
    
    _res_body = mc.loft(targets, o = True, d = 3, po =3 )

    mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
    _inputs = mc.listHistory(mLoft.mNode,pruneDagObjects=True)
    _tessellate = _inputs[0]
    _loftNode = _inputs[1]

    log.debug("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 

    mLoft.overrideEnabled = 1
    mLoft.overrideDisplayType = 2

    mLoft.p_parent = mPrerigNull
    mLoft.resetAttrs()

    mLoft.doStore('cgmName',self)
    mLoft.doStore('cgmType','jointApprox')
    mLoft.doName()

    #Color our stuff...
    CORERIG.colorControl(mLoft.mNode,_side,'main',transparent = False)

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
        mObj.doStore('cgmName',self)
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
        log.debug(cgmGEN.logString_start(_str_func))

        
        
        if self.isReferenced():
            raise ValueError,"Referenced node."
        
        _str_state = self.blockState
    
        if self.blockState != 'rig':
            raise ValueError,"{0} is not in rig state. state: {1}".format(_str_func, _str_state)
    
        #self.blockState = 'rig>prerig'        
    
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
                log.debug("|{0}| >> deleting link: {1}".format(_str_func,link))                        
                mc.delete(self.getMessage(link))
                
        return True
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)

"""
l_pivotOrder = ['center','back','front','left','right']
d_pivotBankNames = {'default':{'left':'outer','right':'inner'},
                    'right':{'left':'inner','right':'outer'}}"""

l_pivotOrder = BLOCKSHARE._l_pivotOrder
d_pivotBankNames = BLOCKSHARE._d_pivotBankNames

@cgmGEN.Timer
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
    log.debug(cgmGEN.logString_start(_str_func))

    
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
    
    log.debug("|{0}| >> ...".format(_str_func))
    """
    
    for a in l_pivotOrder:
        str_a = 'pivot' + a.capitalize()
        if mPivotHelper.getMessage(str_a):
            log.debug("|{0}| >> Found: {1}".format(_str_func,str_a))
            mPivot = mPivotHelper.getMessage(str_a,asMeta=True)[0].doDuplicate(po=False)
            mRigNull.connectChildNode(mPivot,str_a,'rigNull')#Connect    
            mPivot.parent = False
    return True

@cgmGEN.Timer
def pivots_setup(self, mControl = None,
                 mRigNull = None,
                 mBallJoint = None,
                 mBallWiggleJoint = None,
                 mToeJoint = None,
                 jointOrientation = 'zyx',
                 pivotResult = None,
                 mDag = None,
                 rollSetup = 'default', **kws):
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
    log.debug(cgmGEN.logString_start(_str_func))

        
    _side = get_side(self)
    if _side in ['right']:
        d_bankNames = d_pivotBankNames['right']
    else:
        d_bankNames = d_pivotBankNames['default']
    
    if mDag == None:
        mDag = mControl

    d_strCaps = {'front':kws.get('front','toe').capitalize(),
                 'back':kws.get('back','heel').capitalize(),
                 'left':kws.get('left','outer').capitalize(),
                 'right':kws.get('right','inner').capitalize(),
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
    mLastParent = mDag
    for a in l_pivotOrder:
        str_a = 'pivot' + a.capitalize()
        mPivot = mRigNull.getMessage(str_a,asMeta=True)
        
        #remap for right side
        if _side == 'right':
            if a == 'left':
                a = 'right'
            elif a == 'right':
                a = 'left'
                
        if mPivot:
            log.debug("|{0}| >> Found: {1}".format(_str_func,str_a))
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
    
    #if mDag == None:
        #mDag.p_parent = mLastParent
        #mLastParent = mDag
    
    if mBallWiggleJoint:
        mBallWiggleJoint.parent = mLastParent
        mZeroGroup = mBallWiggleJoint.doGroup(True, True, asMeta=True,typeModifier = 'zero')
        mBallWiggleJoint.jointOrient = 0,0,0
        mBallWiggleJoint.rotate = 0,0,0
        
        #mPivot.connectChildNode(mDrivenGroup,'drivenGroup','handle')#Connect    
        
    if mBallJoint:
        mBallJoint.parent = mLastParent
        mZeroGroup = mBallJoint.doGroup(True, True, asMeta=True,typeModifier = 'zero')
        mBallJoint.jointOrient = 0,0,0
        mBallJoint.rotate = 0,0,0
        
        mLastParent = mBallJoint
        
        
    if not d_pivots:
        raise ValueError,"|{0}| >> No pivots found. mBlock: {1}".format(_str_func,self)
    
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
    
    log.debug("|{0}| >> Attributes ...".format(_str_func))    

    #Roll ===================================================================================================
    if b_rollOK:
        mPlug_roll = cgmMeta.cgmAttr(mControl,'roll',attrType='float',defaultValue = 0,keyable = True)
        
        
        if rollSetup in ['human','ik','foot']:
            log.debug("|{0}| >> foot setup ...".format(_str_func))
            mFrontToe = d_drivenGroups['front']
            mHeel = d_drivenGroups['back']
            
            mPlug_toeLift = cgmMeta.cgmAttr(mControl,'rollBallLift_set',attrType='float',initialValue = 35, defaultValue = 35,keyable = True)
            mPlug_toeStaighten = cgmMeta.cgmAttr(mControl,'rollBallStraight_set',attrType='float',initialValue = 65,defaultValue = 65,keyable = True)
            
            if mBallWiggleJoint:
                mPlug_ballUpDn = cgmMeta.cgmAttr(mControl,'ballLift',attrType='float',defaultValue = 0,keyable = True)
                mPlug_ballTwist= cgmMeta.cgmAttr(mControl,'ballTwist',attrType='float',defaultValue = 0,keyable = True)                
                mPlug_ballWiggle= cgmMeta.cgmAttr(mControl,'ballSide',attrType='float',defaultValue = 0,keyable = True)                
                
                mPlug_ballUpDn.doConnectOut("%s.r%s"%(mBallWiggleJoint.mNode,jointOrientation[2].lower()))
                
                if _side in ['right']:
                    str_arg = "{0}.r{1} = -{2}".format(mBallWiggleJoint.mNode,
                                                       jointOrientation[0].lower(),
                                                       mPlug_ballTwist.p_combinedShortName)
                    log.debug("|{0}| >> Ball wiggle Right arg: {1}".format(_str_func,str_arg))        
                    NODEFACTORY.argsToNodes(str_arg).doBuild()
                    
                    str_arg = "{0}.r{1} = -{2}".format(mBallWiggleJoint.mNode,
                                                       jointOrientation[1].lower(),
                                                       mPlug_ballWiggle.p_combinedShortName)
                    log.debug("|{0}| >> Ball wiggle Right arg: {1}".format(_str_func,str_arg))        
                    NODEFACTORY.argsToNodes(str_arg).doBuild()                    
                else:
                    mPlug_ballTwist.doConnectOut("%s.r%s"%(mBallWiggleJoint.mNode,jointOrientation[0].lower()))
                    mPlug_ballWiggle.doConnectOut("%s.r%s"%(mBallWiggleJoint.mNode,jointOrientation[1].lower()))
                
                
            #Heel setup ----------------------------------------------------------------------------------------
            log.debug("|{0}| >> Heel ...".format(_str_func))        
            mPlug_heelClampResult = cgmMeta.cgmAttr(mControl,'result_clamp_heel',attrType='float',keyable = False,hidden=True)
        
            #Setup the heel roll
            #Clamp
        
            _arg = "{0} = clamp({1},0,{2})".format(mPlug_heelClampResult.p_combinedShortName,
                                                   mPlug_roll.p_combinedShortName,
                                                   mPlug_roll.p_combinedShortName)
        
            log.debug("|{0}| >> heel arg: {1}".format(_str_func,_arg))        
            NODEFACTORY.argsToNodes(_arg).doBuild()
        
            #Inversion
            mPlug_heelClampResult.doConnectOut("%s.rx"%(mHeel.mNode))        
        
            #Ball setup ----------------------------------------------------------------------------------------------
            """
                Schleifer's
                ball_loc.rx = (linstep(0,$toeLift, $roll) * (1-(linstep( $toeLift, $toeStraight, $roll))) * $roll;
                        ballToeLiftRoll        md   ( pma   toeToeStraightRoll                    md  
                            1               4       3             2                            5
                """
            log.debug("|{0}| >> ball ...".format(_str_func))    
        
            mPlug_ballToeLiftRollResult = cgmMeta.cgmAttr(mControl,'result_range_ballToeLiftRoll',
                                                          attrType='float',keyable = False,hidden=True)
            mPlug_toeStraightRollResult = cgmMeta.cgmAttr(mControl,'result_range_toeStraightRoll',
                                                          attrType='float',keyable = False,hidden=True)
            mPlug_oneMinusToeResultResult = cgmMeta.cgmAttr(mControl,
                                                            'result_pma_one_minus_toeStraitRollRange',
                                                            attrType='float',keyable = False,hidden=True)
            mPlug_ball_x_toeResult = cgmMeta.cgmAttr(mControl,'result_md_roll_x_toeResult',
                                                     attrType='float',keyable = False,hidden=True)
            mPlug_all_x_rollResult = cgmMeta.cgmAttr(mControl,'result_md_all_x_rollResult',
                                                     attrType='float',keyable = False,hidden=True)
        
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
            if mBallJoint:
                mPlug_all_x_rollResult.doConnectOut("%s.r%s"%(mBallJoint.mNode,jointOrientation[2]))
        
        
            #Toe setup -----------------------------------------------------------------------------------------------
            """
                Schleifer's
                toe_loc.rotateX = linstep($toeLift, $toeStraight,$roll) * $roll;
                              setRange                           md
                             1                                2
                """
            log.debug("|{0}| >> Toe ...".format(_str_func))        
        
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
        
            mPlug_toe_x_rollResult.doConnectOut("%s.rx"%(mFrontToe.mNode))
            
            #mPlug_toeRollResult.doConnectOut("%s.rx"%(mToe.mNode))
            #mPlug_heelRollResult.doConnectOut("%s.rx"%(mHeel.mNode))            
        else:
            log.debug("|{0}| >> StandardRoll ...".format(_str_func))
            
            #Roll setup -----------------------------------------------------------------------------------------------
            """
            Schleifer's
            outside_loc.rotateZ = min($side,0);
            clamp1
            inside_loc.rotateZ = max(0,$side);
            clamp2
            """   
            log.debug("|{0}| >> Bank ...".format(_str_func))        
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
            log.debug("|{0}| >> Right arg: {1}".format(_str_func,str_arg))        
            NODEFACTORY.argsToNodes(str_arg).doBuild()
        else:
            mPlug_rollBall.doConnectOut("{0}.rx".format(mDriven.mNode))         """
            
    
    #Spins ===================================================================================================
    log.debug("|{0}| >> Spin ...".format(_str_func))
    
    d_mPlugSpin = {}
    for k in d_drivenGroups.keys():
        d_mPlugSpin[k] = cgmMeta.cgmAttr(mControl,'spin{0}'.format(d_strCaps[k]),attrType='float',defaultValue = 0,keyable = True)
        
    for k in d_drivenGroups.keys():
        str_key = d_strCaps[k]
        mPlug = d_mPlugSpin[k]
        mDriven = d_drivenGroups[k]
        log.debug("|{0}| >> Spin {1} setup".format(_str_func,str_key))        
        
        if _side in ['right']:# and k not in ['inner','outer']:
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
            mDrivenOutr = d_drivenGroups['left']
            mDrivenInner =d_drivenGroups['right']
            
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
            log.debug("|{0}| >> Right arg: {1}".format(_str_func,str_arg))        
            NODEFACTORY.argsToNodes(str_arg).doBuild()
        else:
            mPlug_bankBall.doConnectOut("{0}.rz".format(mDriven.mNode))         
    
    if mPivotResult:#Do this at the very end...
        mPivotResult.parent = mLastParent        


    
    
#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def prerigHandles_getNameDat(self, nameHandles = False, count = None, **kws):
    """
    Get a list of the driving attributes to plug in to our handles
    
    :parameters:
    
    :returns
        list
    """
    _str_func = 'prerigHandles_getNameDat'
    log.debug(cgmGEN.logString_start(_str_func))

    l_res = []

    mModule = self.moduleTarget
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')
    
    if count == None:
        count = self.numControls
    
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
    l_range = range(count)
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
        if len(ml_prerigHandles) == count:
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
        else:
            log.debug("|{0}| >>  nameHandles on. mismatch length...".format(_str_func))
            pprint.pprint(vars())
            
    return l_res    

def skeleton_getNameDictBase(self):
    """
    Get the base name dict - direction, etc
    """
    _str_func = 'skeleton_getNameDicts'
    log.debug(cgmGEN.logString_start(_str_func))

    l_res = []

        
    mModule = self.moduleTarget
    
    #Name dict...
    _nameDict ={}
    
    if mModule.getMayaAttr('cgmDirection'):
        _nameDict['cgmDirection'] = mModule.cgmDirection
    if mModule.getMayaAttr('cgmPosition'):
        _nameDict['cgmPosition']=mModule.cgmPosition
        
    _nameDict['cgmType'] = 'joint'
    
    return _nameDict

    
def skeleton_getNameDicts(self, combined = False, count = None, iterName= None, **kws):
    """
    Get a list of name dicts for a given block's rig/skin joints
    
    :parameters:
    
    :returns
        list
    """
    _str_func = 'skeleton_getNameDicts'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))    

    l_res = []
    if count is not None:
        _number = count
    else:
        _number = self.numJoints
    mModule = self.moduleTarget
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')
    log.debug("|{0}| >>  baseNames: {1}".format(_str_func,_l_baseNames))
    if not _baseNameAttrs and not _l_baseNames:
        _l_baseNames = []
        for i in range(_number):
            _l_baseNames.append(self.cgmName)
    else:
        _l_baseNames = []
        for i,a in enumerate(_baseNameAttrs):
            _l_baseNames.append(self.getMayaAttr(a))
    #Name dict...
    _nameDict ={}
    
    if mModule.getMayaAttr('cgmDirection'):
        _nameDict['cgmDirection'] = mModule.cgmDirection
    if mModule.getMayaAttr('cgmPosition'):
        _nameDict['cgmPosition']=mModule.cgmPosition
    
    if iterName:
        log.debug("|{0}| >>  iterName: {1}".format(_str_func,iterName))        
        _nameDict['cgmName'] = iterName
    elif self.getMayaAttr('nameIter'):
        _nameDict['cgmName'] = self.nameIter
    elif self.getMayaAttr('cgmName'):
        _nameDict['cgmName'] = self.cgmName
    else:
        _nameDict['cgmName'] = self.blockType
        
    _nameDict['cgmType'] = 'skinJoint'
    
    
    for a,v in kws.iteritems():
        _nameDict[a] = v
    
    log.debug("|{0}| >>  baseDict: {1}".format(_str_func,_nameDict))

    _cnt = 0
    l_range = range(_number)
    l_dicts = []
    for i in l_range:
        _nameDictTemp = copy.copy(_nameDict)
        _specialName = False
        _cnt+=1
        if i == 0:
            if _l_baseNames[0]:
                log.debug("|{0}| >>  First and name attr...interupting default name".format(_str_func))                            
                _nameDictTemp['cgmName'] = _l_baseNames[0]
                #_nameDict['cgmName'] = _l_baseNames[0]#...interupt the default name...
                _cnt = 0
                _specialName = True
        elif i == len(l_range) -1:
            log.debug("|{0}| >>  last...".format(_str_func))            
            if _l_baseNames[-1]:
                log.debug("|{0}| >>  found: {1}".format(_str_func,_l_baseNames[-1]))                            
                _nameDictTemp['cgmName'] = _l_baseNames[-1]
                _specialName = True
                _cnt = 0
        
        if not _specialName:
            _nameDictTemp['cgmIterator'] = _cnt
            
            if _cnt == 1 and l_dicts and not l_dicts[-1].get('cgmIterator'):
                l_dicts[-1]['cgmIterator'] = 0
            
        l_dicts.append(_nameDictTemp)
        log.debug("|{0}| >>  [{1}]: {2}".format(_str_func,i,_nameDict))
    
    if combined:
        return [NAMETOOLS.returnCombinedNameFromDict(d) for d in l_dicts]
    return l_dicts



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
    log.debug(cgmGEN.logString_start(_str_func))

    
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
            log.debug("|{0}| >>  {1} | {2}".format(_str_func,i,mObj.mNode))
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
        log.debug("|{0}| >> No helper orient. Using root.".format(_str_func))   
        _axisWorldUp = MATH.get_obj_vector(_short,_helperUp)                 
    else:
        log.debug("|{0}| >> Found orientHelper: {1}".format(_str_func,_helperOrient))            
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


def skeleton_buildDuplicateChain(self,sourceJoints = None, modifier = 'rig', connectToModule = False, connectAs = 'rigJoints', connectToSource = None, singleMode = False, cgmType = None, indices  = [],blockNames=False):
    """
    blockNames(bool) - use the block generated names
    """
    _str_func = 'skeleton_buildDuplicateChain'
    
    
    if indices:
        log.debug("|{0}| >> Indices arg: {1}".format(_str_func, indices))          
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
            log.debug("|{0}| >> Deleting existing {1} chain".format(_str_func, modifier))  
            mc.delete(l_jointsExist)

    l_joints = mc.duplicate([i_jnt.mNode for i_jnt in ml_source],po=True,ic=True,rc=True)
    
    ml_joints = cgmMeta.validateObjListArg(l_joints,'cgmObject',setClass=True)
    
    if blockNames:
        l_names = skeleton_getNameDicts(self,False,len(l_joints))        
    else:
        l_names = []
    
    for i,mJnt in enumerate(ml_joints):
        if blockNames:
            _d_tmp = l_names[i]
            log.debug("|{0}| >> blockName dict {1} | {2}".format(_str_func, i,_d_tmp))              
            for a in ['cgmIterator','cgmName']:
                if _d_tmp.get(a):
                    mJnt.addAttr(a, str(_d_tmp.get(a)),attrType='string',lock=True)

        if modifier is not None:
            #l_names[i]['cgmTypeModifier'] = modifier
            mJnt.addAttr('cgmTypeModifier', modifier,attrType='string',lock=True)
            
        if cgmType is False:
            ATTR.delete(mJnt.mNode,'cgmType')
        elif cgmType:
            mJnt.addAttr('cgmType', cgmType,attrType='string',lock=True)
        
        #l_joints[i] = mJnt.mNode
        if connectToSource:
            mJnt.connectChildNode(ml_source[i].mNode,'sourceJoint',"{0}Joint".format(connectToSource))#Connect
        
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
    log.debug(ml_joints)
    return ml_joints

def skeleton_duplicateJoint(self,sourceJoints = None, modifier = 'rig', connectToModule = False, connectAs = 'rigJoints', connectToSource = 'skinJoint', singleMode = False, cgmType = None, indices  = [],blockNames=False):
    """
    blockNames(bool) - use the block generated names
    """
    _str_func = 'skeleton_buildDuplicateChain'
    
    
    if indices:
        log.debug("|{0}| >> Indices arg: {1}".format(_str_func, indices))          
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
            log.debug("|{0}| >> Deleting existing {1} chain".format(_str_func, modifier))  
            mc.delete(l_jointsExist)

    l_joints = mc.duplicate([i_jnt.mNode for i_jnt in ml_source],po=True,ic=True,rc=True)
    
    ml_joints = [cgmMeta.cgmObject(j) for j in l_joints]

    if blockNames:
        l_names = skeleton_getNameDicts(self,False,len(l_joints))        
    else:
        l_names = []
    
    for i,mJnt in enumerate(ml_joints):
        if blockNames:
            _d_tmp = l_names[i]
            log.debug("|{0}| >> blockName dict {1} | {2}".format(_str_func, i,_d_tmp))              
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

def skeleton_getAttachJoint(self):
    _str_func = 'skeleton_connectToParent'
    log.debug(cgmGEN.logString_start(_str_func))

    
    if self.blockType == 'master':
        log.debug("|{0}| >> Master block type. No connection possible".format(_str_func))                   
        return False
    
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
            log.debug("|{0}| >> Master block...".format(_str_func))           
            if mParentModule.getMessage('rootJoint'):
                log.debug("|{0}| >> Root joint on master found".format(_str_func))
                return mParentModule.getMessage('rootJoint')[0]
                return True
            else:
                log.debug("|{0}| >> No root joint".format(_str_func))
                return False
        else:
            ml_targetJoints = mParentModule.rigNull.msgList_get('moduleJoints',asMeta = True, cull = True)
            if not ml_targetJoints:
                raise ValueError,"mParentModule has no module joints."
            _attachPoint = ATTR.get_enumValueString(self.mNode,'attachPoint')
            if _attachPoint == 'end':
                mTargetJoint = ml_targetJoints[-1]
            elif _attachPoint == 'base':
                mTargetJoint = ml_targetJoints[0]
            elif _attachPoint == 'closest':
                jnt = DIST.get_closestTarget(ml_moduleJoints[0].mNode, [mObj.mNode for mObj in ml_targetJoints])
                mTargetJoint = cgmMeta.asMeta(jnt)
            else:
                raise ValueError,"Not done with {0}".format(_attachPoint)
            return mTargetJoint

    return False

def skeleton_connectToParent(self):
    _str_func = 'skeleton_connectToParent'
    log.debug(cgmGEN.logString_start(_str_func))

    
    if self.blockType == 'master':
        log.debug("|{0}| >> Master block type. No connection possible".format(_str_func))                   
        return True
    
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
            _attachPoint = ATTR.get_enumValueString(self.mNode,'attachPoint')
            if _attachPoint == 'end':
                mTargetJoint = ml_targetJoints[-1]
            elif _attachPoint == 'base':
                mTargetJoint = ml_targetJoints[0]
            elif _attachPoint == 'closest':
                jnt = DIST.get_closestTarget(ml_moduleJoints[0].mNode, [mObj.mNode for mObj in ml_targetJoints])
                mTargetJoint = cgmMeta.asMeta(jnt)
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
        log.debug("|{0}| >> Deleting existing rig chain".format(_str_func))  
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
    log.debug("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	
    
    return ml_rigJoints

def skeleton_pushSettings(ml_chain = None, orientation = 'zyx', side = 'right',
                          d_rotateOrders = {}, d_preferredAngles = {}, d_limits = {}):
    try:
        _str_func = '[{0}] > '.format('skeleton_pushSettings')
        
        _preferredAxis = {}
        _l_axisAlias = ['aim','up','out']
        for k in _l_axisAlias:
            if d_preferredAngles.get(k) is not None:
                _v = d_preferredAngles.get(k)
                log.debug("|{0}| >> found default preferred {1}:{2}".format(_str_func,k,_v))  
                _preferredAxis[k] = _v
        
        for mJnt in ml_chain:
            _key = mJnt.getMayaAttr('cgmName',False)
            _key = VALID.stringArg(_key)
            
            _rotateOrderBuffer = d_rotateOrders.get(_key,d_rotateOrders.get('default',False))
            _limitBuffer = d_limits.get(_key,d_limits.get('default',False))
            _preferredAngles = d_preferredAngles.get(_key,d_preferredAngles.get('default',False))
            
            
            if _rotateOrderBuffer:
                log.debug("|{0}| >> found rotate order data on {1}:{2}".format(_str_func,_key,_rotateOrderBuffer))  
                TRANS.rotateOrder_set(mJnt.mNode, _rotateOrderBuffer, True)
                
            if _preferredAngles:
                log.debug("|{0}| >> found preferred angle data on {1}:{2}".format(_str_func,_key,_preferredAngles))              
                #log.debug("preferred angles(%s)>>> %s"%(i_jnt.cgmName,__d_preferredAngles__.get(i_jnt.cgmName)))
                for i,v in enumerate(_preferredAngles):	
                    #if side.lower() == 'right':#negative value
                    #    mJnt.__setattr__('preferredAngle{0}'.format(orientation[i].upper()),-v)				
                    #else:
                    mJnt.__setattr__('preferredAngle{0}'.format(orientation[i].upper()),v)
            elif _preferredAxis:
                for k,v in _preferredAxis.iteritems():
                    _idx = _l_axisAlias.index(k)
                    #if side.lower() == 'right':#negative value
                        #mJnt.__setattr__('preferredAngle{0}'.format(orientation[_idx].upper()),-v)				
                    #else:
                    mJnt.__setattr__('preferredAngle{0}'.format(orientation[_idx].upper()),v)                
                
            if _limitBuffer:
                log.debug("|{0}| >> found limit data on {1}:{2}".format(_str_func,_key,_limitBuffer))              
                raise Exception,"Limit Buffer not implemented"
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())

def skeleton_getHandleChain(self, typeModifier = None, jointHelpers = True, mOrientHelper = None):
    """
    Generate a handle chain of joints if none exists, otherwise return existing
    
    :parameters:
        typeModifier(str): for nam linking
        jointHelpers(bool): Whether to use jointHelpers or preRigHandles
        
    """
    _short = self.mNode
    _str_func = 'skeleton_getHandleChain'
    #start = time.clock()	
    log.debug(cgmGEN.logString_start(_str_func))
    
    mRigNull = self.moduleTarget.rigNull
    ml_fkJoints = mRigNull.msgList_get('fkJoints')
    
    if not ml_fkJoints:
        log.debug("|{0}| >> Generating handleJoints".format(_str_func))
        
        ml_templateHandles = self.msgList_get('templateHandles',asMeta = True)
        if not ml_templateHandles:
            raise ValueError,"No templateHandles connected"        
        
        ml_prerigHandles = self.msgList_get('prerigHandles',asMeta = True)
        if not ml_prerigHandles:
            raise ValueError,"No prerigHandles connected"
        
        if mOrientHelper is None:
            mOrientHelper = ml_templateHandles[0].orientHelper or ml_prerigHandles[0].orientHelper
            
        #_d = skeleton_getCreateDict(self)
        #pprint.pprint(_d)
        l_pos = []
        if jointHelpers:
            ml_jointHandles = self.msgList_get('jointHelpers',asMeta = True)
            if not ml_jointHandles:
                raise ValueError,"No jointHelpers connected"            
            for mObj in ml_jointHandles:
                l_pos.append(mObj.p_position)
        else:
            for mObj in ml_prerigHandles:
                l_pos.append(mObj.p_position)
            
        ml_fkJoints = COREJOINTS.build_chain(posList = l_pos,
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
        log.debug("|{0}| >> Found fkJoints".format(_str_func))
        
    #log.debug("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	
    return ml_fkJoints


def skeleton_buildHandleChain(self,typeModifier = 'handle', connectNodesAs = False,clearType = False,mOrientHelper=None): 
    _short = self.mNode
    _str_func = 'skeleton_buildHandleChain [{0}]'.format(_short)
    #start = time.clock()
    
    mRigNull = self.moduleTarget.rigNull
    ml_handleJoints = skeleton_getHandleChain(self,typeModifier,mOrientHelper=mOrientHelper)
    ml_handleChain = []
    
    if typeModifier and typeModifier.lower() not in ['fk']:
        for i,mHandle in enumerate(ml_handleJoints):
            mNew = mHandle.doDuplicate()
            if ml_handleChain:mNew.parent = ml_handleChain[-1]#if we have data, parent to last
            else:mNew.parent = False
            if typeModifier or clearType:
                if typeModifier:
                    mNew.addAttr('cgmTypeModifier',typeModifier,attrType='string',lock=True)
                    mHandle.connectChildNode(mNew.mNode,'{0}Joint'.format(typeModifier),'sourceJoint')
                if clearType:
                    try:ATTR.delete(mNew.mNode, 'cgmType')
                    except:pass
                mNew.doName()
            ml_handleChain.append(mNew)
    else:
        ml_handleChain = ml_handleJoints

    if connectNodesAs and type(connectNodesAs) in [str,unicode]:
        self.moduleTarget.rigNull.msgList_connect(connectNodesAs,ml_handleChain,'rigNull')#Push back

    #log.debug("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)
    return ml_handleChain


def verify_loftList(self,int_shapers):
    try:
        log.debug("loftList | attr validation"+ '-'*60)
        _short = self.p_nameShort
        
        l_loftList = ATTR.datList_get(_short,'loftList',enum=True)
        
        if len(l_loftList) > int_shapers:
            log.debug("loftList | cleaning")
            _d_attrs = ATTR.get_sequentialAttrDict(_short, 'loftList')
            for i in range(len(l_loftList) - int_shapers):
                ATTR.delete(_short,_d_attrs[i+int_shapers] )
    
        v = self.loftShape
        _enum_loftShape = BLOCKSHARE._d_attrsTo_make['loftShape']
        for i in range(int_shapers):
            str_attr = "loftList_{0}".format(i)
            if not ATTR.has_attr(_short,str_attr):
                self.addAttr(str_attr, v, attrType = 'enum',
                             enumName= _enum_loftShape,
                             keyable = False)
            else:
                strValue = ATTR.get_enumValueString(_short,str_attr)
                self.addAttr(str_attr,initialValue = v, attrType = 'enum', enumName= _enum_loftShape, keyable = False)
                if strValue:
                    ATTR.set(_short,str_attr,strValue)
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

                    
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


def rigNodes_get(self,report = False):
    _str_func = 'rigNodes_get'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mModuleTarget = self.getMessageAsMeta('moduleTarget')
    if not mModuleTarget:
        return False
    
    if mModuleTarget.mClass == 'cgmRigPuppet':
        _res = mModuleTarget.getMessage('rigNodes')
    else:
        _res = mModuleTarget.rigNull.getMessage('rigNodes')
        
    if report:
        _len = len(_res)
        log.debug(cgmGEN._str_subLine)
        ml = []
        l_fails = []
        """
        for o in _res:
            try:
                ml.append(cgmMeta.asMeta(o))
            except Exception,err:
                l_fails.append("{0} | {1}".format(o,err))
                log.warning("|{0}| >> node failed to initialize: {1} | {2}".format(_str_func,o,err))"""
                
        #ml = [cgmMeta.asMeta(o) for o in _res]
        md = {}
        d_counts = {}
        
        for o in _res:
            _type = SEARCH.get_mayaType(o)#mObj.getMayaType()
            if not md.get(_type):
                md[_type] = []
            md[_type].append(o)

            
        for k,l in md.iteritems():
            _len_type = len(l)
            print("|{0}| >>  Type: {1} ...".format(_str_func,k)+'-'*60)
            d_counts[k] = _len_type
            for i,mNode in enumerate(l):
                print("{0} | {1}".format(i,mNode))
                
        log.debug(cgmGEN._str_subLine)
        _sort = d_counts.keys()
        _sort.sort()
        for k in _sort:
            print("|{0}| >>  {1} : {2}".format(_str_func,k,d_counts[k]))
        #print("|{0}| >>  Fails to initialize : {1}".format(_str_func,len(l_fails)))
        #for i,n in enumerate(l_fails):
        #    print("{0} | {1}".format(i,n))            
        print("|{0}| >>  Total: {1} | {2}".format(_str_func,_len,self))
        log.debug(cgmGEN._str_hardLine)
    return _res



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
    log.debug(cgmGEN.logString_start(_str_func))

    
    mParent_current =  self.blockParent
    if self.blockState == 'rig':
        raise ValueError,"Cannot change the block parent of a rigged rigBlock. State: {0} | rigBlock: {1}".format(self.blockState,self)
    
    if not parent:
        self.blockParent = False
        if self.p_blockParent != False:
            self.p_parent = False
            
        if self.getMessage('moduleTarget'):
            #log.debug("|{0}| >>  parent false. clearing moduleTarget".format(_str_func,self))
            self.moduleTarget.p_parent = False
            
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
                    
        #blockProfile ----------------------------------------------------
        if mParent.hasAttr('buildProfile'):
            log.debug("|{0}| >>  buildProfile_load...".format(_str_func))
            self.atUtils('buildProfile_load', mParent.getMayaAttr('buildProfile'))
            


#=============================================================================================================
#>> Mirror/Duplicate
#=============================================================================================================
def duplicate2(self):
    """
    Call to duplicate a block module and load data
    """
    try:
        _str_func = 'blockDuplicate'
        mDup = cgmMeta.createMetaNode('cgmRigBlock',blockType = self.blockType, autoTemplate=False)
        mDup.loadBlockDat(self.getBlockDat())
        mDup.doName()
        return mDup
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def duplicate(self, uiPrompt = True, forceNew = False):
    """
    Call to duplicate a block module and load data
    """
    try:
        _str_func = 'duplicate'
        _blockType = self.blockType
        _side = get_side(self)
        
        
        _d = {'blockType':self.blockType,
              'autoTemplate':False,
              'side':_side,
              'baseSize':baseSize_get(self),
              'blockProfile':self.blockProfile,
              'blockParent': self.p_blockParent}
        
        for a in 'cgmName','blockProfile':
            if a in ['cgmName']:
                _d['name'] =  self.getMayaAttr(a)
            elif self.hasAttr(a):
                _d[a] = self.getMayaAttr(a)        
        
        _title = 'New name for duplicate'.format(_blockType)
        result = mc.promptDialog(title=_title,
                                 message='Current: {0} | type: {1} | build: {2} | block:{3} '.format(_d['name'],_blockType,_d.get('blockProfile'),_d.get('buildProfile')),
                                 button=['OK', 'Cancel'],
                                 text = _d['name'],
                                 defaultButton='OK',
                                 cancelButton='Cancel',
                                 dismissString='Cancel')
        if result == 'OK':
            _v =  mc.promptDialog(query=True, text=True)
            _d['name'] =  _v
            
        else:
            log.error("Duplication cancelled for |{0}|".format(self))
            return False
        
        log.debug("|{0}| >> Creating duplicate block. {1} | source: {2}".format(_str_func, _blockType, self))

        
        log.debug("|{0}| >> Block settings...".format(_str_func))                    
        #pprint.pprint(_d)
        mDup = cgmMeta.createMetaNode('cgmRigBlock',
                                      **_d)
        
        mDup.doSnapTo(self)
        
        blockDat = self.getBlockDat()
        
        blockDat['baseName'] = _v
        blockDat['ud']['cgmName'] = _v
        
        if _d['blockType'] in ['finger','thumb']:
            log.debug("|{0}| >> Clearing nameList".format(_str_func))
            for a in blockDat['ud'].iteritems():
                if 'nameList' in a:
                    blockDat['ud'].remove(a)
            blockDat['ud']['nameList_0'] = _v            
            
        """
        if blockDat['ud'].get('rigSetup') in ['finger']:
            log.debug("|{0}| >> Clearing nameList".format(_str_func))
            for a in blockDat['ud'].iteritems():
                if 'nameList' in a:
                    blockDat['ud'].remove(a)
            blockDat['nameList_0'] = _v"""
            
        #changeState(mDup,'define',forceNew=True)#redefine to catch any optional created items from settings
        mDup.blockDat = blockDat
        blockDat_load(mDup,redefine=True)
        #log.debug('here...')
        #blockDat_load(mDup)#...investigate why we need two...
        
        #mDup.p_blockParent = self.p_blockParent
        #self.connectChildNode(mMirror,'blockMirror','blockMirror')#Connect    
        return mDup
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
    
    
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
            
        log.debug("|{0}| >>  blockParent....".format(_str_func))
        mBlockParent = self.p_blockParent
        if mBlockParent.getMessage('blockMirror'):
            mBlockParent = mBlockParent.blockMirror
            log.debug("|{0}| >>  blockParent has blockMirror: {1}".format(_str_func,mBlockParent))
            
        log.debug("|{0}| >> Creating mirror block. {1} | {2}".format(_str_func, _blockType, _side))
        
        _d = {'blockType':self.blockType, 'side':_side,
              'autoTemplate':False,
              'blockParent':mBlockParent,
              #'baseAim':[self.baseAimX,-self.baseAimY,self.baseAimZ],
              'baseSize':baseSize_get(self)}
        for a in 'blockProfile','buildProfile','cgmName':
            if a in ['cgmName']:
                _d['name'] =  self.getMayaAttr(a)
            else:
                _d[a] =  self.getMayaAttr(a)

        
        log.debug("|{0}| >> Block settings...".format(_str_func, self.mNode))                    
        pprint.pprint(_d)
        
        mMirror = cgmMeta.createMetaNode('cgmRigBlock',
                                         **_d)
        
        
        
        blockDat = self.getBlockDat()
        blockDat['ud']['side'] = _side
        for k in ['baseSize','baseAim']:
            if blockDat['ud'].has_key(k):
                blockDat['ud'].pop(k)
            for a in 'XYZ':
                if blockDat['ud'].has_key(k+a):
                    blockDat['ud'].pop(k+a)
        mMirror.blockDat = blockDat
        
        blockMirror_settings(self,mMirror)
        mMirror.saveBlockDat()
        _d = mMirror.blockDat
        _d['blockState']=self.blockState
        mMirror.blockDat = _d
        
        """
        for k,dIter in BLOCKSHARE._d_mirrorAttrCheck.iteritems():
            _check = blockDat['ud'].get(k)
            if _check:
                log.debug("|{0}| >> mirror dat check {1} | {2}".format(_str_func, k, dIter))
                blockDat['ud'][k] = dIter.get(blockDat['ud'][k])"""
        
        """
        #Mirror some specfic dat
        if blockDat.get('template'):
            _subShapers = blockDat['template'].get('subShapers',{})
            log.debug("|{0}| >> subShaper dat mirror...".format(_str_func, self.mNode))                    
            
            for i,d_sub in _subShapers.iteritems():
                l_t = d_sub.get('t')
                l_r = d_sub.get('r')
                l_s = d_sub.get('s')
                
                for ii,d_list in enumerate(l_t):
                    d_list[0] = d_list[0]*-1
                for ii,d_list in enumerate(l_r):
                    d_list[0] = d_list[0]*-1  
                    d_list[1] = d_list[1]*-1
                    
                _subShapers[str(i)]['r'][ii] = l_r
                _subShapers[str(i)]['r'][ii] = l_t"""
            
        
        #if blockDat['ud'].get('cgmDirection'):
            #blockDat['ud']['cgmDirection'] = _side
        #blockDat_load(mMirror, blockDat, mirror = False)
       
            
        self.connectChildNode(mMirror,'blockMirror','blockMirror')#Connect
        mMirror.p_blockParent = mBlockParent
        
        
        blockDat_load(mMirror,useMirror=True,redefine=True)
        return
        #mMirror.loadBlockDat(blockDat)
        controls_mirror(self,mMirror)
        
        #blockMirror_settings(self,mMirror)
        return mMirror
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

def blockMirror_settings(blockSource, blockMirror = None,
                         mode = 'push'):
    
        _str_func = 'blockMirror_settings'
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(blockSource)
        
        if blockMirror is None:
            log.debug("|{0}| >> Self mirror....".format(_str_func))
            if blockSource.getMessage('blockMirror'):
                mMirror = blockSource.blockMirror
            else:
                return log.error("|{0}| >> No block mirror found on: {1}".format(_str_func,blockSource))
            log.debug("|{0}| >> UseMirror. BlockMirror Found: {1}".format(_str_func,mMirror))
        else:
            mMirror = blockMirror
        
        
        if mode == 'push':
            mSource = blockSource
            mTarget = mMirror
        else:
            mSource = mMirror
            mTarget = blockSource
            
        #Root ----------------------------------------------------------------------------------
        log.debug("|{0}| >> Source: {1}".format(_str_func,mSource))
        log.debug("|{0}| >> Target: {1}".format(_str_func,mTarget))
        
        blockDat = blockDat_get(mSource)
        _short = mTarget.mNode
        _ud = blockDat.get('ud')
        _udFail = {}
        _l_done = []
        if not blockDat.get('ud'):
            raise ValueError,"|{0}| >> No ud data found".format(_str_func)
        
        _ud['baseSize'] = baseSize_get(mSource)
        
        """
        for k,dIter in BLOCKSHARE._d_mirrorAttrCheck.iteritems():
            _check = _ud.get(k)
            if _check:
                log.debug("|{0}| >> mirror dat check {1} | {2}".format(_str_func, k, dIter))
                blockDat['ud'][k] = dIter.get(blockDat['ud'][k])        
                _l_done.append(k)"""
        
                
        _mask = ['side','version','blockState','baseAim','baseAimY']
        for a,v in _ud.iteritems():
            if a in _mask or a in _l_done:
                continue
            _type = ATTR.get_type(_short,a)
            
            if VALID.stringArg(v):
                #log.debug("string...")                
                if v.endswith('Pos'):
                    log.debug("{0} | Pos > Neg".format(v))
                    v = str(v).replace('Pos','Neg')
                elif v.endswith('Neg'):
                    v = str(v).replace('Neg','Pos')
                    log.debug("{0} | Neg > Pos".format(v))
                    
                
            if _type == 'enum':
                _current = ATTR.get_enumValueString(_short,a)
            else:
                _current = ATTR.get(_short,a)
            if _current != v:
                try:
                    if ATTR.get_type(_short,a) in ['message']:
                        log.debug("|{0}| >> userDefined '{1}' skipped. Not loading message data".format(_str_func,a))                     
                    else:
                        log.debug("|{0}| >> userDefined '{1}' mismatch. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                        ATTR.set(_short,a,v)
                except Exception,err:
                    _udFail[a] = v
                    log.error("|{0}| >> userDefined '{1}' failed to change. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                    #r9Meta.printMetaCacheRegistry()                
                    for arg in err.args:
                        log.error(arg)
                        
        #loftList
        _loftList = ATTR.datList_get(mSource.mNode,'loftList','enum',enum=True)
        log.debug("|{0}| >> loftList pre : {1}".format(_str_func,_loftList))
        _loftUse = []
        for i,v in enumerate(_loftList):
            if 'Pos' in v:
                log.debug("|{0}| >> loftList pos: {1}".format(_str_func,v))                
                _loftUse.append(str(v).replace('Pos','Neg'))
            elif 'Neg' in v:
                log.debug("|{0}| >> loftList neg: {1}".format(_str_func,v))                                
                _loftUse.append(str(v).replace('Neg','Pos'))
            else:
                _loftUse.append(v)
        log.debug("|{0}| >> loftList post: {1}".format(_str_func,_loftUse))
            
        ATTR.datList_connect(mTarget.mNode, 'loftList', _loftUse,'enum',enum = BLOCKSHARE._d_attrsTo_make['loftShape'])
    
        if _udFail:
            log.error("|{0}| >> UD Fails...".format(_str_func) + '-'*80)
            pprint.pprint(_udFail)
            return False
        return True

def blockMirror_settings2():
    #.>>>..UD ====================================================================================
        log.debug("|{0}| >> ud...".format(_str_func)+ '-'*80)
        _ud = blockDat.get('ud')
        _udFail = {}
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
                    _udFail[a] = v
                    log.error("|{0}| >> userDefined '{1}' failed to change. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                    #r9Meta.printMetaCacheRegistry()                
                    for arg in err.args:
                        log.error(arg)                      
    
        if _udFail:
            log.error("|{0}| >> UD Fails...".format(_str_func) + '-'*80)
            pprint.pprint(_udFail)    
    
def mirror_self(self,primeAxis = 'left'):
    _str_func = 'mirror_self'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    

    mBlockModule = self.p_blockModule

    if 'mirror_self' in mBlockModule.__dict__.keys():
        log.debug("|{0}| >> BlockModule mirror_self call found...".format(_str_func))
        reload(mBlockModule)
        mBlockModule.mirror_self(self,primeAxis)
        return True
    return log.error("No mirror self call found: {0}".format(self))
    
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
        cgmGEN.cgmExceptCB(Exception,err)
        
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
def baseSize_get(self):
    mBlockModule = self.p_blockModule
    
    if 'baseSize_get' in mBlockModule.__dict__.keys():
        log.debug("|{0}| >> BlockModule call found...".format(_str_func))            
        return mBlockModule.baseSize_get
    
    _baseSize = self.baseSize
    try:mDefineEndObj = self.defineEndHelper
    except:mDefineEndObj = False
    
    if mDefineEndObj and mDefineEndObj.hasAttr('length'):
        return [mDefineEndObj.width,mDefineEndObj.height,mDefineEndObj.length]
    return _baseSize


def defineSize_get(self):
    _str_func = 'defineSize_get'            
    _baseSize = self.baseSize
    if _baseSize:
        log.debug("|{0}| >> Base size found: {1}...".format(_str_func,_baseSize))                    
        return MATH.average(_baseSize[:-2])/2.0
    return self.atUtils('get_shapeOffset') or 1.0# * 2.0

def define_getHandles(self):
    md_vectorHandles = {}
    md_defineHandles = {}
    #Template our vectors
    for k in BLOCKSHARE._l_defineHandlesOrder:
        mHandle = self.getMessageAsMeta("vector{0}Helper".format(STR.capFirst(k)))    
        if mHandle:
            log.debug("define vector: {0} | {1}".format(k,mHandle))            
            md_vectorHandles[k] = mHandle
            
        mHandle = self.getMessageAsMeta("define{0}Helper".format(STR.capFirst(k)))    
        if mHandle:
            log.debug("define handle: {0} | {1}".format(k,mHandle))                        
            md_defineHandles[k] = mHandle

    return md_defineHandles,md_vectorHandles


def blockDat_get(self,report = True):
    """
    Carry from Bokser stuff...
    """
    try:
        _str_func = 'blockDat_get'        
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        _l_udMask = ['blockDat','attributeAliasList','blockState','mClass','mClassGrp','mNodeID','version']
        #_ml_controls = self.getControls(True,True)
        _ml_controls = []
        _short = self.p_nameShort
        _blockState_int = self.getState(False)
        
        #self.baseSize = baseSize_get(self)
        #Trying to keep un assertable data out that won't match between two otherwise matching RigBlocks
        _d = {#"name":_short, 
              "blockType":self.blockType,
              "blockState":self.p_blockState,
              "baseName":self.getMayaAttr('cgmName'), 
              'position':self.p_position,
              'baseSize':self.getState(False),
              'orient':self.p_orient,
              'scale':self.scale,
              'blockScale':ATTR.get(_short,'blockScale'),
              "version":self.version, 
              "ud":{}
              }   
        
        """
        if self.getShapes():
            _d["size"] = POS.get_axisBox_size(self.mNode,False),
        else:
            _d['size'] = self.baseSize"""
        
            
        if self.getMessage('orientHelper'):
            _d['rootOrientHelper'] = self.orientHelper.rotate
        
        _d['define'] = blockDat_getControlDat(self,'define')#self.getBlockDat_templateControls()
        
        if _blockState_int >= 1:
            _d['template'] = blockDat_getControlDat(self,'template')#self.getBlockDat_templateControls()

        if _blockState_int >= 2:
            _d['prerig'] = blockDat_getControlDat(self,'prerig')#self.getBlockDat_prerigControls() 

        for a in self.getAttrs(ud=True):
            if a not in _l_udMask:
                try:
                    _type = ATTR.get_type(_short,a)
                    if _type in ['message']:
                        continue
                    elif _type == 'enum':
                        _d['ud'][a] = ATTR.get_enumValueString(_short,a)                    
                    else:
                        _d['ud'][a] = ATTR.get(_short,a)
                except Exception,err:
                    log.error("Failed to query attr: {0} | type: {1} | err: {2}".format(a,_type,err))
        
        _d['ud']['baseSize'] = baseSize_get(self)
        
        if report:cgmGEN.walk_dat(_d,'[{0}] blockDat'.format(self.p_nameShort))
        return _d
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def blockDat_save(self):
    self.blockDat = blockDat_get(self,False)

def blockDat_reset(self):
    #This needs more work.
    blockProfile_load(self, self.blockProfile)

def blockDat_copy(self,sourceBlock=None,ignoreChecks=False,load=False):
    _str_func = 'blockDat_copy'
    log.debug("|{0}| >>  ".format(_str_func)+ '='*80)
    log.debug("|{0}| {1}".format(_str_func,self))
    
    if self == sourceBlock:
        raise ValueError,"Can't copy blockDat from self."
    blockDat = sourceBlock.getBlockDat()
    
    _type = blockDat['ud'].get('blockType')
    _profile = blockDat['ud'].get('blockProfile')
    
    if not ignoreChecks:
        if _type != self.blockType:
            raise ValueError,"Incompatible blockTypes. dat: {0} | {1}".format(_type,self.blockType)
        if _profile != self.blockProfile:
            raise ValueError,"Incompatible blockProfiles. dat: {0} | {1}".format(_profile,self.blockProfile)
    
    blockDat['baseName'] = self.cgmName
    blockDat['ud']['cgmName'] = self.cgmName
    
    if blockDat['ud'].get('rigSetup') in ['finger']:
        log.debug("|{0}| >> Clearing nameList".format(_str_func))
        for a in blockDat['ud'].iteritems():
            if 'nameList' in a:
                blockDat['ud'].remove(a)
        blockDat['nameList_0'] = _v
        
    self.blockDat = blockDat
    
    if load:
        blockDat_load(self)
    
def blockDat_getControlDat(self,mode = 'define',report = True):
    _short = self.p_nameShort        
    _str_func = 'blockDat_getControlDat'
    log.debug("|{0}| >>  ".format(_str_func)+ '='*80)
    log.debug("|{0}| {1}".format(_str_func,self))
    
    _mode_int,_mode_str = BLOCKGEN.validate_stateArg(mode)
    
    _modeToState = {'define':0,
                    'template':1,
                    'prerig':2}
    
    if _mode_str not in _modeToState.keys():
        raise ValueError,"Unknown mode: {0}".format(_mode_str)
    
    _blockState_int = self.getState(False)
    
    if not _blockState_int >= _modeToState[_mode_str]:
        raise ValueError,'[{0}] not {1} yet. State: {2}'.format(_short,_mode_str,_blockState_int)
        #_ml_templateHandles = self.msgList_get('templateHandles',asMeta = True)
    
    _d_controls = {'define':False,'template':False,'prerig':False}
    _d_controls[_mode_str] = True
    ml_handles = controls_get(self, **_d_controls)
    #pprint.pprint(vars())
    
    if not ml_handles:
        log.error('[{0}] No template or prerig handles found'.format(_short))
        return False

    _ml_controls = ml_handles

    _l_orientHelpers = []
    _l_jointHelpers = []
    _d_orientHelpers = {}
    _d_jointHelpers = {}
    _d_loftCurves = {}
    _d_subShapers = {}
    
    for i,mObj in enumerate(ml_handles):
        _str_short = mObj.mNode
        log.debug("|{0}| >>  {1} | {2}".format(_str_func,i,mObj.mNode))
        if mObj.getMessage('orientHelper'):
            #_l_orientHelpers.append(mObj.orientHelper.rotate)
            _d_orientHelpers[i] = mObj.orientHelper.rotate
        #else:
            #_l_orientHelpers.append(False)

        if mObj.getMessage('jointHelper'):
            #_l_jointHelpers.append(mObj.jointHelper.translate)
            _d_jointHelpers[i] = mObj.jointHelper.translate
            
        mLoftCurve = mObj.getMessageAsMeta('loftCurve')
        if mLoftCurve:
            log.debug("|{0}| >>  loftcurve: {1}".format(_str_func,mLoftCurve)+'-'*20)
            if mLoftCurve.v:
                _d = {}
                _rot = mLoftCurve.rotate
                _trans = mLoftCurve.translate
                _scale = mLoftCurve.scale
                _p = mLoftCurve.p_position
                
                if not MATH.is_float_equivalent(sum(_rot),0.0):
                    _d['r'] = _rot
                if not MATH.is_float_equivalent(MATH.multiply(_scale), 1.0):
                    _d['s'] = _scale
                if not MATH.is_float_equivalent(sum(_trans),0.0):
                    _d['t'] = _trans
                    
                _d['p'] = _p
                if _d:
                    _d_loftCurves[i] = _d
                    log.debug("|{0}| >>  d: {1}".format(_str_func,_d))
        
        ml_subShapers = mObj.msgList_get('subShapers')
        if ml_subShapers:
            _d = {}
            log.debug("|{0}| >>  subShapers...".format(_str_func))
            _d = {'p':[mObj.p_position for mObj in ml_subShapers],
                  'o':[mObj.p_orient for mObj in ml_subShapers],
                  'r':[mObj.rotate for mObj in ml_subShapers],
                  't':[mObj.translate for mObj in ml_subShapers],
                  's':[mObj.scale for mObj in ml_subShapers]}            
            if _d:
                _d_subShapers[i] = _d            
        
        log.debug(cgmGEN._str_subLine)    


        #else:
            #_l_jointHelpers.append(False)
    _d = {'positions':[mObj.p_position for mObj in ml_handles],
          'orients':[mObj.p_orient for mObj in ml_handles],
          'scales':[mObj.scale for mObj in ml_handles]}
    
    if _d_orientHelpers:
        _d['orientHelpers'] =_d_jointHelpers
        
    if _d_jointHelpers:
        _d['jointHelpers'] =_d_jointHelpers
        
    if _d_loftCurves:
        _d['loftCurves'] =_d_loftCurves
    
    if _d_subShapers:
        _d['subShapers'] =_d_subShapers
        


    #if self.getMessage('orientHelper'):
    #    _d['rootOrientHelper'] = self.orientHelper.rotate

    if report:cgmGEN.walk_dat(_d,'[{0}] template blockDat'.format(self.p_nameShort))
    return _d

def blockDat_load_state(self,state = None,blockDat = None, d_warnings = None):
    _str_func = 'blockDat_load_state'
    log.debug(cgmGEN.logString_start(_str_func))
    
    if not blockDat:
        log.debug(cgmGEN.logString_msg(_str_func,"No blockDat, using self"))
        blockDat = self.blockDat

    d_state = blockDat.get(state,False)
    if not d_state:
        log.error(cgmGEN.logString_msg(_str_func,"No {0} data found in blockDat".format(state)))
        return False
    
    ml_handles = self.atUtils('controls_get',**{state:True})
    
    if d_warnings:
        if not d_warnings.get(state):
            d_warnings[state] =  []
        _l_warnings = d_warnings[state]
    else:
        _l_warnings = []
        
    if not ml_handles:
        log.error("|{0}| >> No define handles found".format(_str_func))
    else:
        _posTempl = d_state.get('positions')
        _orientsTempl = d_state.get('orients')
        _scaleTempl = d_state.get('scales')
        _jointHelpers = d_state.get('jointHelpers')
        _loftCurves = d_state.get('loftCurves',{})
        _subShapers = d_state.get('subShapers',{})
        _len_posTempl = len(_posTempl)
        _jointHelpersPre = {}
        if state == 'prerig':
            _jointHelpersPre = d_state.get('jointHelpers')
            
        if len(ml_handles) < _len_posTempl:
            _l_warnings.append("|{0}| >> {3} handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( ml_handles),_len_posTempl,state))
        else:
            for i_loop in range(3):
                log.debug(cgmGEN.logString_sub(_str_func,"Loop: {0}".format(i_loop)))
                for i,mObj in enumerate(ml_handles):
                    log.debug(cgmGEN.logString_msg(_str_func,"Handle: {0}".format(mObj)))
                    
                    _handleType = mObj.getMayaAttr('handleType')
                    if _handleType == 'vector':
                        try:
                            mObj.p_orient = _orientsTempl[i]
                            continue
                        except Exception,err:
                            _l_warnings.append('{0}...'.format(mObj.p_nameShort))
                            _l_warnings.append('Couldnt set vector handle orient | {0}'.format(err))
                    
                    if i > _len_posTempl-1:
                        _l_warnings.append("No data for: {0}".format(mObj))
                        continue
                    
                    mObj.p_position = _posTempl[i]
                    if not ATTR.is_locked(mObj.mNode,'rotate'):
                        mObj.p_orient = _orientsTempl[i]
                        
                    _tmp_short = mObj.mNode
                    for ii,v in enumerate(_scaleTempl[i]):
                        _a = 's'+'xyz'[ii]
                        if not mObj.isAttrConnected(_a):
                            ATTR.set(_tmp_short,_a,v)
                        else:
                            log.debug("|{0}| >> connected scale: {1}".format(_str_func,_a))
                    if _jointHelpers and _jointHelpers.get(i):
                        mObj.jointHelper.translate = _jointHelpers[i]
                    
                    _d_loft = _loftCurves.get(str(i))
                    if _d_loft:
                        if i_loop:
                            log.debug("|{0}| >> _d_loft: {1}".format(_str_func,_d_loft))
                        
                            mLoftCurve = mObj.loftCurve
                            _rot = _d_loft.get('r')
                            _s = _d_loft.get('s')
                            _t = _d_loft.get('t')
                            if _rot:
                                ATTR.set(mLoftCurve.mNode,'rotate',_rot)
                            if _s:
                                ATTR.set(mLoftCurve.mNode,'scale',_s)
                            if _t:
                                ATTR.set(mLoftCurve.mNode,'translate',_t)
                                
                    if _jointHelpersPre and _jointHelpersPre.get(i):
                        mObj.jointHelper.translate = _jointHelpersPre[i]                    
                            
                for i,d_sub in _subShapers.iteritems():
                    ml_subs = ml_handles[int(i)].msgList_get('subShapers')
                    log.debug ("|{0}| >> subShapers: {1}".format(_str_func,i))
                    if not ml_subs:
                        raise ValueError,"Failed to find subShaper: {0} | {1}".format(i,d_sub)
                    _t = d_sub.get('t')
                    _r = d_sub.get('r')
                    _s = d_sub.get('s')
                    _p = d_sub.get('p')
                    for ii,mObj in enumerate(ml_subs):
                        mObj.p_position = _p[ii]
                        #ATTR.set(mObj.mNode,'t',_t[ii])
                        ATTR.set(mObj.mNode,'r',_r[ii])
                        ATTR.set(mObj.mNode,'s',_s[ii])        

@cgmGEN.Timer
def blockDat_load(self, blockDat = None,
                  useMirror = False,
                  settingsOnly = False,
                  autoPush = True,
                  currentOnly=False,
                  redefine=False):
    """
    redefine - When duplicating, sometimes we need to redfine after data load
    """
    try:
        _short = self.p_nameShort        
        _str_func = 'blockDat_load'
        log.debug(cgmGEN.logString_start(_str_func))
        _d_warnings = {}
    
        if blockDat is None:
            log.debug("|{0}| >> No blockDat passed. Checking self...".format(_str_func))    
            blockDat = self.blockDat
    
        if not issubclass(type(blockDat),dict):
            raise ValueError,"|{0}| >> blockDat must be dict. type: {1} | blockDat: {2}".format(_str_func,type(blockDat),blockDat) 
    
        _blockType = blockDat.get('blockType')
        if _blockType != self.blockType:
            raise ValueError,"|{0}| >> blockTypes don't match. self: {1} | blockDat: {2}".format(_str_func,self.blockType,_blockType) 
    
            
        self.blockScale = blockDat['blockScale']
        
        #.>>>..UD ====================================================================================
        log.debug("|{0}| >> ud...".format(_str_func)+ '-'*80)
        _ud = blockDat.get('ud')
        _udFail = {}
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
                    _udFail[a] = v
                    log.error("|{0}| >> userDefined '{1}' failed to change. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                    #r9Meta.printMetaCacheRegistry()                
                    for arg in err.args:
                        log.error(arg)                      
    
        if _udFail:
            log.warning(cgmGEN.logString_sub(_str_func,'UD Fails'))
            pprint.pprint(_udFail)
            
        if settingsOnly:
            log.warning(cgmGEN.logString_msg(_str_func,'settings only'))
            return
        
        
        #>>State ====================================================================================
        log.debug("|{0}| >> State".format(_str_func) + '-'*80)
        _stateArgs = BLOCKGEN.validate_stateArg(blockDat.get('blockState'))
        _target_state_idx = _stateArgs[0]
        _target_state = _stateArgs[1]
        
        _current_state = self.getState()
        _onlyState = False
        _current_state_idx = self.getState(False)
        
        if currentOnly:
            log.debug("|{0}| >> Current only mode: {1}".format(_str_func,_current_state))
            return blockDat_load_state(self,_current_state,blockDat)

            
        elif _target_state != _current_state:
            log.debug("|{0}| >> States don't match. self: {1} | blockDat: {2}".format(_str_func,_current_state,_target_state)) 
            #self.p_blockState = _state
            
        mMirror = False
        if useMirror:
            if self.getMessage('blockMirror'):
                mMirror = self.blockMirror
            log.debug("|{0}| >> UseMirror. BlockMirror Found: {1}".format(_str_func,mMirror))
            
    
        #>>Controls ====================================================================================
        def setAttr(node,attr,value):
            try:ATTR.set(node,attr,value)
            except Exception,err:
                log.warning("|{0}| >> Failed to set: {1} | attr:{2} | value:{3} | err: {4}".format(_str_func,
                                                                                                   node,
                                                                                                   attr,value))
        log.debug("|{0}| >> Block main controls".format(_str_func)+ '-'*80)
        _pos = blockDat.get('position')
        _orients = blockDat.get('orient')
        _scale = blockDat.get('scale')
        _orientHelper = blockDat.get('rootOrientHelper')
        
        self.p_position = blockDat.get('position')
        self.p_orient = blockDat.get('orient')
        
        if blockDat.get('blockScale'):
            self.blockScale = blockDat['blockScale']
        #else:
            #for ii,v in enumerate(_scale):
                #_a = 's'+'xyz'[ii]
                #if not self.isAttrConnected(_a) and not(ATTR.is_locked(_short,a)):
                #setAttr(_short,_a,v)
            
        #>>Define Controls ====================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'define'))
        
        if redefine:
            changeState(self,'define',forceNew=True,rebuildFrom='define')
            _current_state_idx = 0
            _current_state = 'define'
            
        if mMirror == 'cat':
            log.debug("|{0}| >> mMirror define pull...".format(_str_func))            
            controls_mirror(mMirror,self,define=True)
        else:
            blockDat_load_state(self,'define',blockDat,_d_warnings)
        
        #>>Template Controls ====================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'template'))
        
        if _target_state_idx >= 1:
            log.debug("|{0}| >> template dat....".format(_str_func))
            if autoPush:
                if _current_state_idx < 1:
                    log.debug("|{0}| >> Pushing to template....".format(_str_func))
                    self.p_blockState = 1
            else:
                return log.warning(cgmGEN.logString_msg(_str_func,"Autopush off. Can't go to: {1}".format(_target_state)))
            
            log.debug(cgmGEN.logString_msg(_str_func,'template push'))
            
        if mMirror:
            log.debug("|{0}| >> mMirror template pull...".format(_str_func))            
            self.UTILS.controls_mirror(mMirror,self,template=True,prerig=False)
        
        else:
            if _orientHelper:
                mOrientHelper = self.getMessageAsMeta('orientHelper')
                if mOrientHelper:
                    _ctrl = mOrientHelper.mNode
                    for ii,v in enumerate(_orientHelper):
                        _a = 'r'+'xyz'[ii]
                        setAttr(_ctrl,_a,v)
                else:
                    _d_warnings['template']=["Missing orient Helper. Data found."]
                
            blockDat_load_state(self,'template',blockDat,_d_warnings)
           
        
        #Prerig ==============================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'prerig'))
        
        if _target_state_idx >= 2:
            log.debug("|{0}| >> prerig dat....".format(_str_func))
            if _current_state_idx < 2:
                if not autoPush:
                    return log.warning(cgmGEN.logString_msg(_str_func,"Autopush off. Can't go to: {1}".format(_target_state)))
                else:
                    log.debug("|{0}| >> Pushing to prerig....".format(_str_func))
                    self.p_blockState = 2

        if mMirror:
            log.debug("|{0}| >> mMirror prerig pull...".format(_str_func))            
            self.UTILS.controls_mirror(mMirror,self,template=False,prerig=True)
        else:
            blockDat_load_state(self,'prerig',blockDat,_d_warnings)
            
        if _d_warnings:
            for k,d in _d_warnings.iteritems():
                for i,w in enumerate(d):
                    if i == 0:log.warning(cgmGEN.logString_sub(_str_func,"{0} | Warnings".format(k)))
                    log.warning(w)
        return

    except Exception,err:cgmGEN.cgmException(Exception,err)


def blockDat_load_prefactor(self, blockDat = None,
                  useMirror = False,
                  settingsOnly = False,
                  autoPush = True,
                  currentOnly=False,
                  redefine=False):
    """
    redefine - When duplicating, sometimes we need to redfine after data load
    """
    try:
        _short = self.p_nameShort        
        _str_func = '[{0}] loadBlockDat'.format(_short)
        _d_warnings = {}
        log.debug(cgmGEN.logString_start(_str_func))
    
    
        if blockDat is None:
            log.debug("|{0}| >> No blockDat passed. Checking self...".format(_str_func))    
            blockDat = self.blockDat
    
        if not issubclass(type(blockDat),dict):
            raise ValueError,"|{0}| >> blockDat must be dict. type: {1} | blockDat: {2}".format(_str_func,type(blockDat),blockDat) 
    
        _blockType = blockDat.get('blockType')
        if _blockType != self.blockType:
            raise ValueError,"|{0}| >> blockTypes don't match. self: {1} | blockDat: {2}".format(_str_func,self.blockType,_blockType) 
    
        mMirror = False
        if useMirror:
            if self.getMessage('blockMirror'):
                mMirror = self.blockMirror
            log.debug("|{0}| >> UseMirror. BlockMirror Found: {1}".format(_str_func,mMirror))                
            
        self.blockScale = blockDat['blockScale']
        
        #.>>>..UD ====================================================================================
        log.debug("|{0}| >> ud...".format(_str_func)+ '-'*80)
        _ud = blockDat.get('ud')
        _udFail = {}
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
                    _udFail[a] = v
                    log.error("|{0}| >> userDefined '{1}' failed to change. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                    #r9Meta.printMetaCacheRegistry()                
                    for arg in err.args:
                        log.error(arg)                      
    
        if _udFail:
            log.error("|{0}| >> UD Fails...".format(_str_func) + '-'*80)
            pprint.pprint(_udFail)
            
        if settingsOnly:
            log.warning(cgmGEN.logString_msg(_str_func,'settings only'))
            
            return
        
        
        #>>State ====================================================================================
        log.debug("|{0}| >> State".format(_str_func) + '-'*80)
        _stateArgs = BLOCKGEN.validate_stateArg(blockDat.get('blockState'))
        _target_state_idx = _stateArgs[0]
        _target_state = _stateArgs[1]
        
        _current_state = self.getState()
        _onlyState = False
        _current_state_idx = self.getState(False)
        
        if currentOnly:
            log.debug("|{0}| >> Current only mode: {1}".format(_str_func,_current_state)) 
            _target_state = _current_state
            _onlyState = _current_state
            
        elif _target_state != _current_state:
            log.debug("|{0}| >> States don't match. self: {1} | blockDat: {2}".format(_str_func,_current_state,_target_state)) 
            #self.p_blockState = _state
            
    
        #>>Controls ====================================================================================
        def setAttr(node,attr,value):
            try:ATTR.set(node,attr,value)
            except Exception,err:
                log.warning("|{0}| >> Failed to set: {1} | attr:{2} | value:{3} | err: {4}".format(_str_func,
                                                                                                   node,
                                                                                                   attr,value))
        log.debug("|{0}| >> Block main controls".format(_str_func)+ '-'*80)
        _pos = blockDat.get('position')
        _orients = blockDat.get('orient')
        _scale = blockDat.get('scale')
        _orientHelper = blockDat.get('rootOrientHelper')
        
        self.p_position = blockDat.get('position')
        self.p_orient = blockDat.get('orient')
        
        if blockDat.get('blockScale'):
            self.blockScale = blockDat['blockScale']
        #else:
            #for ii,v in enumerate(_scale):
                #_a = 's'+'xyz'[ii]
                #if not self.isAttrConnected(_a) and not(ATTR.is_locked(_short,a)):
                #setAttr(_short,_a,v)
            
        #>>Define Controls ====================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'define'))
        
        if redefine:
            changeState(self,'define',forceNew=True,rebuildFrom='define')
            _current_state_idx = 0
            _current_state = 'define'
            
        if mMirror == 'cat':
            log.debug("|{0}| >> mMirror define pull...".format(_str_func))            
            controls_mirror(mMirror,self,define=True)
        else:
            if not _onlyState or _onlyState == 'define':
                _d_define = blockDat.get('define',False)
                if not _d_define:
                    log.error("|{0}| >> No define data found in blockDat".format(_str_func)) 
                else:
                    _ml_defineHandles = self.atUtils('controls_get',define=True)
                    _d_warnings['define'] =  []
                    _l_warnings = _d_warnings['define']
                    if not _ml_defineHandles:
                        log.error("|{0}| >> No define handles found".format(_str_func))
                    else:
                        _posTempl = _d_define.get('positions')
                        _orientsTempl = _d_define.get('orients')
                        _scaleTempl = _d_define.get('scales')
                        _jointHelpers = _d_define.get('jointHelpers')
                        _loftCurves = _d_define.get('loftCurves',{})
                        _subShapers = _d_define.get('subShapers',{})
                        _len_posTempl = len(_posTempl)
                        if len(_ml_defineHandles) < _len_posTempl:
                            log.error("|{0}| >> Define handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( _ml_defineHandles),_len_posTempl))
                        else:
                            for i_loop in range(3):
                                log.debug("|{0}| >> Loop: {1}".format(_str_func,i_loop)+ '-'*80)
                                for i,mObj in enumerate(_ml_defineHandles):
                                    log.debug ("|{0}| >> TemplateHandle: {1}".format(_str_func,mObj.mNode))
                                    if i > _len_posTempl-1:
                                        _l_warnings.append("No data for: {0}".format(mObj))
                                        continue
                                    
                                    mObj.p_position = _posTempl[i]
                                    if not ATTR.is_locked(mObj.mNode,'rotate'):
                                        mObj.p_orient = _orientsTempl[i]
                                        
                                    _tmp_short = mObj.mNode
                                    for ii,v in enumerate(_scaleTempl[i]):
                                        _a = 's'+'xyz'[ii]
                                        if not mObj.isAttrConnected(_a):
                                            ATTR.set(_tmp_short,_a,v)
                                        else:
                                            log.debug("|{0}| >> connected scale: {1}".format(_str_func,a))
                                    if _jointHelpers and _jointHelpers.get(i):
                                        mObj.jointHelper.translate = _jointHelpers[i]
                                    
                                    
                                    _d_loft = _loftCurves.get(str(i))
                                    if _d_loft:
                                        if i_loop:
                                            log.debug("|{0}| >> _d_loft: {1}".format(_str_func,_d_loft))
                                        
                                            mLoftCurve = mObj.loftCurve
                                            _rot = _d_loft.get('r')
                                            _s = _d_loft.get('s')
                                            _t = _d_loft.get('t')
                                            if _rot:
                                                ATTR.set(mLoftCurve.mNode,'rotate',_rot)
                                            if _s:
                                                ATTR.set(mLoftCurve.mNode,'scale',_s)
                                            if _t:
                                                ATTR.set(mLoftCurve.mNode,'translate',_t)
                                            
                                for i,d_sub in _subShapers.iteritems():
                                    ml_subs = _ml_defineHandles[int(i)].msgList_get('subShapers')
                                    log.debug ("|{0}| >> subShapers: {1}".format(_str_func,i))
                                    if not ml_subs:
                                        raise ValueError,"Failed to find subShaper: {0} | {1}".format(i,d_sub)
                                    _t = d_sub.get('t')
                                    _r = d_sub.get('r')
                                    _s = d_sub.get('s')
                                    _p = d_sub.get('p')
                                    for ii,mObj in enumerate(ml_subs):
                                        mObj.p_position = _p[ii]
                                        #ATTR.set(mObj.mNode,'t',_t[ii])
                                        ATTR.set(mObj.mNode,'r',_r[ii])
                                        ATTR.set(mObj.mNode,'s',_s[ii])    
        
        
        #>>Template Controls ====================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'template'))
        
        if _target_state_idx >= 1:
            log.debug("|{0}| >> template dat....".format(_str_func))
            if autoPush and currentOnly != True:
                if _current_state_idx < 1:
                    log.debug("|{0}| >> Pushing to template....".format(_str_func))
                    self.p_blockState = 1
            
        if not _onlyState or _onlyState == 'template':
            log.debug(cgmGEN.logString_msg(_str_func,'template push'))
            
            if mMirror:
                log.debug("|{0}| >> mMirror template pull...".format(_str_func))            
                self.UTILS.controls_mirror(mMirror,self,template=True,prerig=False)
            
            else:
                if _orientHelper:
                    _ctrl = self.orientHelper.mNode
                    for ii,v in enumerate(_orientHelper):
                        _a = 'r'+'xyz'[ii]
                        setAttr(_ctrl,_a,v)
                
                _d_template = blockDat.get('template',False)
                _d_warnings['template'] =  []
                _l_warnings = _d_warnings['template']
                
                if not _d_template:
                    log.error("|{0}| >> No template data found in blockDat".format(_str_func)) 
                else:
                    _ml_templateHandles = self.atUtils('controls_get',template=True)
    
                    if not _ml_templateHandles:
                        log.error("|{0}| >> No template handles found".format(_str_func))
                    else:
                        _posTempl = _d_template.get('positions')
                        _orientsTempl = _d_template.get('orients')
                        _scaleTempl = _d_template.get('scales')
                        _jointHelpers = _d_template.get('jointHelpers')
                        _loftCurves = _d_template.get('loftCurves',{})
                        _subShapers = _d_template.get('subShapers',{})
                        
                        if len(_ml_templateHandles) > len(_posTempl):
                            _l_warnings.append("|{0}| >> Template handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( _ml_templateHandles),len(_posTempl)))
                        
                        for i_loop in range(3):
                            log.debug("|{0}| >> Loop: {1}".format(_str_func,i_loop))
    
                            for i,mObj in enumerate(_ml_templateHandles):
                                try:
                                    log.debug ("|{0}| >> TemplateHandle: {1}".format(_str_func,mObj.mNode))
                                    mObj.p_position = _posTempl[i]
                                    if not ATTR.is_locked(mObj.mNode,'rotate'):
                                        mObj.p_orient = _orientsTempl[i]
                                        
                                    _tmp_short = mObj.mNode
                                    for ii,v in enumerate(_scaleTempl[i]):
                                        _a = 's'+'xyz'[ii]
                                        if not mObj.isAttrConnected(_a):
                                            ATTR.set(_tmp_short,_a,v)   
                                    if _jointHelpers and _jointHelpers.get(i):
                                        mObj.jointHelper.translate = _jointHelpers[i]
                                    
                                    
                                    _d_loft = _loftCurves.get(str(i))
                                    if _d_loft:
                                        if i_loop:
                                            log.debug("|{0}| >> _d_loft: {1}".format(_str_func,_d_loft))
                                        
                                            mLoftCurve = mObj.loftCurve
                                            _rot = _d_loft.get('r')
                                            _s = _d_loft.get('s')
                                            _t = _d_loft.get('t')
                                            _p = _d_loft.get('p')
                                            if _rot:
                                                ATTR.set(mLoftCurve.mNode,'rotate',_rot)
                                            if _s:
                                                ATTR.set(mLoftCurve.mNode,'scale',_s)
                                            if _t:
                                                ATTR.set(mLoftCurve.mNode,'translate',_t)
                                            elif _p:
                                                mLoftCurve.p_position = _p
                                except Exception,err:
                                    _l_warnings.append("{0} | {1} | mObj: {2} | err: {3}".format(i_loop,i,mObj.p_nameShort, err))
                                        
                            for i,d_sub in _subShapers.iteritems():
                                try:
                                    ml_subs = _ml_templateHandles[int(i)].msgList_get('subShapers')
                                    log.debug ("|{0}| >> subShapers: {1}".format(_str_func,i))
                                    if not ml_subs:
                                        raise ValueError,"Failed to find subShaper: {0} | {1}".format(i,d_sub)
                                    _t = d_sub.get('t')
                                    _r = d_sub.get('r')
                                    _s = d_sub.get('s')
                                    _p = d_sub.get('p')
                                    
                                    for ii,mObj in enumerate(ml_subs):
                                        #mObj.p_position = _p[0]                                    
                                        ATTR.set(mObj.mNode,'t',_t[ii])
                                        ATTR.set(mObj.mNode,'r',_r[ii])
                                        ATTR.set(mObj.mNode,'s',_s[ii])
                                except Exception,err:
                                    _l_warnings.append("{0} | {1} | subs | err: {2}".format(i_loop,i, err))
                                    
                                
        
                    #if _d_template.get('rootOrientHelper'):
                        #if self.getMessage('orientHelper'):
                        #    self.orientHelper.p_orient = _d_template.get('rootOrientHelper')
                        #else:
                            #log.error("|{0}| >> Found root orient Helper data but no orientHelper control".format(_str_func))
        #pprint.pprint(vars())
        
        #Prerig ==============================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'prerig'))
        
        if _target_state_idx >= 2:
            log.debug("|{0}| >> prerig dat....".format(_str_func))
            if _current_state_idx < 2:
                if not autoPush:
                    log.debug("|{0}| >> Autopush off. Stopping at template....".format(_str_func))                
                    return True
                
                log.debug("|{0}| >> Pushing to prerig....".format(_str_func))
                self.p_blockState = 2
            
        if not _onlyState or _onlyState == 'prerig':
            log.debug(cgmGEN.logString_msg(_str_func,'prerig push'))
        
            if mMirror:
                log.debug("|{0}| >> mMirror prerig pull...".format(_str_func))            
                self.UTILS.controls_mirror(mMirror,self,template=False,prerig=True)
            else:
                _d_prerig = blockDat.get('prerig',False)
                if not _d_prerig:
                    log.error("|{0}| >> No template data found in blockDat".format(_str_func)) 
                else:
                    _ml_prerigControls = self.atUtils('controls_get',prerig=True)
                    
                    _d_warnings['prerig'] =  []
                    _l_warnings = _d_warnings['prerig']
                    
                    if not _ml_prerigControls:
                        log.error("|{0}| >> No prerig handles found".format(_str_func))
                    else:
                        _posPre = _d_prerig.get('positions')
                        _orientsPre = _d_prerig.get('orients')
                        _scalePre = _d_prerig.get('scales')
                        _jointHelpersPre = _d_prerig.get('jointHelpers')
            
                        if len(_ml_prerigControls) > len(_posPre):
                            _l_warnings.append("|{0}| >> Prerig handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( _ml_prerigControls),len(_posPre)))
                            pprint.pprint(_ml_prerigControls)
                        
                        for i_loop in range(3):
                            log.debug("|{0}| >> Loop: {1}".format(_str_func,i_loop))
        
                            for i,mObj in enumerate(_ml_prerigControls):
                                try:
                                    log.debug ("|{0}| >> Prerig handle: {1}".format(_str_func,mObj.mNode))
                                    mObj.p_position = _posPre[i]
                                    mObj.p_orient = _orientsPre[i]
                                    _tmp_short = mObj.mNode
                                    for ii,v in enumerate(_scalePre[i]):
                                        _a = 's'+'xyz'[ii]
                                        if not mObj.isAttrConnected(_a):
                                            ATTR.set(_tmp_short,_a,v)   
                                    if _jointHelpersPre and _jointHelpersPre.get(i):
                                        mObj.jointHelper.translate = _jointHelpersPre[i]
                                except Exception,err:
                                    _l_warnings.append("{0} | {1} | mObj: {2} | err: {3}".format(i_loop,i,mObj.p_nameShort, err))                
                    #if _d_prerig.get('rootOrientHelper'):
                        #if self.getMessage('orientHelper'):
                            #self.orientHelper.p_orient = _d_prerig.get('rootOrientHelper')
                        #else:
                            #log.error("|{0}| >> Found root orient Helper data but no orientHelper #control".format(_str_func))
            
            #if _target_state_idx > 2:
            #    self.p_blockState = _target_state

        if _d_warnings:
            for k,d in _d_warnings.iteritems():
                for i,w in enumerate(d):
                    if i == 0:log.warning(cgmGEN.logString_sub(_str_func,"{0} | Warnings".format(k)))
                    log.warning(w)
        return
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
    except Exception,err:cgmGEN.cgmException(Exception,err)



def blockDat_loadBAK(self, blockDat = None, mirror=False, reflectionVector = MATH.Vector3(1,0,0), controls=True):
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
        log.debug("|{0}| >> template dat....".format(_str_func))             
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


def blockAttr_set(self, **kws):
    _short = self.p_nameShort        
    _str_func = '[{0}] blockAttr_set'.format(_short)
    #log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
    
    for a,v in kws.iteritems():
        if self.hasAttr(a):
            try:
                ATTR.set(_short,a,v)
            except Exception,err:
                log.error("|{0}| Set attr Failure >> '{1}' | value: {2} | err: {3}".format(_str_func,a,v,err)) 
                
            if a == 'numRoll':
                log.debug("numRoll check...")
                if ATTR.datList_exists(_short,'rollCount'):
                    log.debug("rollCount Found...")                                            
                    l = ATTR.datList_getAttrs(_short,'rollCount')
                    for a in l:
                        log.debug("{0}...".format(a))                                                
                        ATTR.set(_short,a, v)                    
    
        
        
        
        else:
            log.warning("|{0}| Lacks attr >> '{1}'".format(_str_func,a)) 
            


def messageConnection_setAttr(self,plug = None, **kws):
    _short = self.p_nameShort        
    _str_func = '[{0}] messageConnection_setAttr'.format(_short)
    log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
    
    l_objs = []
    if self.getMessage(plug):
        log.debug("|{0}| >>  Message found: {1} ".format(_str_func,plug))                
        l_objs = self.getMessage(plug)
    elif mRigNull.msgList_exists(plug):
        log.debug("|{0}| >>  msgList found: {1} ".format(_str_func,plug))                
        l_objs = self.msgList_get(plug)
        
    for o in l_objs:
        for a,v in kws.iteritems():
            try:
                ATTR.set(o,a,v)
            except Exception,err:
                print err
    return l_objs

    
    

#=============================================================================================================
#>> Controls query
#=============================================================================================================
def get_blockDagNodes(self):
    try:
        _short = self.p_nameShort
        _str_func = 'get_blockDagNodes'
        log.debug(cgmGEN.logString_start(_str_func))

        
        ml_controls = controls_get(self,True,True,True)
                
        for a in ['proxyHelper','defineLoftMesh','prerigLoftMesh','jointLoftMesh']:
            if self.getMessage(a):
                ml_controls.extend(self.getMessage(a,asMeta=True))
                
        if 'd_wiring_extraDags' in self.p_blockModule.__dict__.keys():
            log.debug("|{0}| >>  Found extraDat wiring".format(_str_func))
            for k in self.p_blockModule.d_wiring_extraDags.get('msgLinks',[]):
                mNode = self.getMessageAsMeta(k)
                if mNode:
                    ml_controls.append(mNode)
            for k in self.p_blockModule.d_wiring_extraDags.get('msgLists',[]):
                ml = self.msgList_get(k)
                if ml:
                    ml_controls.extend(ml)
        return ml_controls
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

def controls_get(self,define = False, template = False, prerig= False):
    try:
        _short = self.p_nameShort        
        _str_func = '[{0}] controls_get'.format(_short)
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
        
        def addMObj(mObj):
            log.debug("|{0}| >> Storing: {1} ".format(_str_func,mObj))
            if mObj in ml_controls:
                log.debug("|{0}| >> Already stored: {1} ".format(_str_func,mObj))                    
                return
            ml_controls.append(mObj)
            if mObj.getMessage('orientHelper'):
                log.debug("|{0}| >> ... has orient helper".format(_str_func))
                addMObj(mObj.orientHelper)
            if mObj.getMessage('jointHelper'):
                log.debug("|{0}| >> has joint helper...".format(_str_func))
                addMObj(mObj.jointHelper)
        
        def addPivotHelper(mPivotHelper):
            addMObj(mPivotHelper)
            for mChild in mPivotHelper.getChildren(asMeta=True):
                if mChild.getMayaAttr('cgmType') == 'pivotHelper':
                    addMObj(mChild)
            
        ml_controls = []
        
        #if self.getMessage('orientHelper'):
            #ml_controls.append(self.orientHelper)
        if define:
            ml_handles = self.msgList_get('defineHandles',asMeta=True)
            if ml_handles:
                log.debug("|{0}| >> define dat found...".format(_str_func))            
                for mObj in ml_handles:
                    addMObj(mObj)
            
        if template:
            log.debug("|{0}| >> template pass...".format(_str_func))            
            ml_handles = self.msgList_get('templateHandles',asMeta = True)
            for mObj in ml_handles:
                addMObj(mObj)
                if mObj.getMessage('pivotHelper'):addPivotHelper(mObj.pivotHelper)
                
        if prerig:
            log.debug("|{0}| >> Prerig pass...".format(_str_func))                        
            ml_handles = self.msgList_get('prerigHandles',asMeta = True)
            for mObj in ml_handles:
                addMObj(mObj)
                if mObj.getMessage('pivotHelper'):addPivotHelper(mObj.pivotHelper)

        return ml_controls
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def controls_mirror(blockSource, blockMirror = None,
                    mirrorMode = 'push', 
                    reflectionVector = MATH.Vector3(1,0,0),
                    define=True,template = True, prerig= True,
                    mirrorLofts = True):
    try:
        _short = blockSource.p_nameShort        
        _str_func = '[{0}] controls_mirror'.format(_short)
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
        
        d_controlCall = {'define':True,'template':template,'prerig':prerig}
        
        if blockMirror is not None:
            _mirrorState = BLOCKGEN.validate_stateArg(blockMirror.blockState)
            #_mirrorState = blockMirror.getState()
            if prerig and _mirrorState[0]<2:
                log.debug("|{0}| >> blockMirror not prerigged. Removing controls".format(_str_func))
                d_controlCall['prerig'] = False
            if template and _mirrorState[0]<1:
                log.debug("|{0}| >> blockMirror not templated. Removing controls".format(_str_func))
                d_controlCall['template'] = False                
            
        
        ml_controls = controls_get(blockSource, **d_controlCall)
        ml_controls.insert(0,blockSource)        
        int_lenSource = len(ml_controls)
        
        if blockMirror is None:
            log.debug("|{0}| >> Self mirror....".format(_str_func))
            ml_targetControls = ml_controls
        else:
            log.debug("|{0}| >> Mirror Target: {1}....".format(_str_func,blockMirror.p_nameShort))
            ml_targetControls = controls_get(blockMirror,**d_controlCall)
            ml_targetControls.insert(0,blockMirror)
            int_lenTarget = len(ml_targetControls)
            
            if int_lenTarget!=int_lenSource:
                for i,mObj in enumerate(ml_controls):
                    try:
                        log.debug(" {0} >> {1}".format(mObj.p_nameBase, ml_targetControls[i].p_nameBase))
                    except:
                        log.debug(" {0} >> ERROR".format(mObj.p_nameBase))
                        
                raise ValueError,"Control list lengths do not match. source: {0} | target: {1} ".format(int_lenSource,int_lenTarget)
            """
            if ml_targetControls[0] != ml_controls[0]:
                ml_targetControls[0].baseAimX = ml_controls[0].baseAimX
                ml_targetControls[0].baseAimY = -ml_controls[0].baseAimY
                ml_targetControls[0].baseAimZ = -ml_controls[0].baseAimZ"""
        
        l_dat = []
        
        if not ml_controls:
            raise ValueError,"No controls"
        
        blockMirror.scaleY = blockSource.scaleY
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
        reflectUp  = mRoot.getTransformDirection( MATH.Vector3(0,1,0)).reflect( reflectionVector )
        reflectAimPoint = DIST.get_pos_by_vec_dist(posNew, [reflectAim.x,reflectAim.y,reflectAim.z], 100)
        log.debug("|{0}| >> Root rot: aim: {1} | up: {2} | point: {3}".format(_str_func, reflectAim,reflectUp,reflectAimPoint))
        

        l_dat.append({'pos':posNew,'aimPoint':reflectAimPoint,'up':reflectUp,'aim':reflectAim,'scale':mRoot.scale})
        
        #Other controls ------------------------------------------------------------------------
        #rootReflectionVector = TRANS.transformDirection(_short,reflectionVector).normalized()
        #log.debug("|{0}| >> reg Reflect: {1}".format(_str_func,rootReflectionVector))
        log.debug("|{0}| >> control dat...".format(_str_func))
        
        for i,mObj in enumerate(ml_controls[1:]):
            log.debug(cgmGEN._str_subLine)                        
            log.debug("|{0}| >> Get {1} | {2}".format(_str_func,i+1,mObj.p_nameBase))
            str_obj = mObj.mNode
            _dat = {'source':str_obj,'target':ml_targetControls[i+1].mNode}
            
            #Pos... ----------------------------------------------------------------------------------------
            posBase = mObj.p_positionEuclid
            #posNew = (mObj.p_positionEuclid - self.p_positionEuclid).reflect(rootReflectionVector) + self.p_positionEuclid
            posNew = mObj.p_positionEuclid.reflect(reflectionVector)
            log.debug("|{0}| >> Mirror pos [{1}] | base: {2} | result: {3}".format(_str_func, i+1, posBase,posNew))
            #mObj.p_positionEuclid = posNew
            
            _dat['pos'] = posNew
            
            #Reflect/Orient ---------------------------------------------------------------------------------
            '''If we have locked rotates we can't reflect properly and instead do a attr check'''
            _lock_rot = False
            _rot_good = []
            for a in 'xyz':
                if ATTR.is_locked(str_obj,'r{0}'.format(a)):
                    _lock_rot = True
                else:
                    _rot_good.append(a)
                    
            if _lock_rot:
                _rot = {}
                log.debug("|{0}| >> lock rot detected...".format(_str_func))
                for a in _rot_good:
                    if a in list('zy'):
                        _rot[a] = -ATTR.get(str_obj,'r{0}'.format(a))
                    else:
                        _rot[a] = ATTR.get(str_obj,'r{0}'.format(a))
                if _rot:
                    log.debug("|{0}| >> lock rot detected. Good: {1} | fixed: {2}".format(_str_func, _rot_good, _rot))                    
                    _dat['simpleRot'] = _rot
                else:
                    _dat['simpleRot'] = False
            else:
                reflectAim = mObj.getTransformDirection( MATH.Vector3(0,0,1)).reflect( reflectionVector )
                reflectUp  = mObj.getTransformDirection( MATH.Vector3(0,1,0)).reflect( reflectionVector )
                #reflectUp = MATH.get_obj_vector(mObj.mNode,'y+')
                
                reflectAimPoint = DIST.get_pos_by_vec_dist(posNew, [reflectAim.x,reflectAim.y,reflectAim.z], 10)
                log.debug("|{0}| >> Mirror rot [{1}] | aim: {2} | up: {3} | point: {4}".format(_str_func, i, reflectAim,reflectUp,reflectAimPoint))
                
                _dat['aimPoint']=reflectAimPoint
                _dat['up'] = reflectUp
                _dat['aim'] = reflectAim
                
            #Scale ---------------------------------------------------------------------------------
            _lock_scale = False
            _scale_good = []
            for a in 'xyz':
                if ATTR.is_locked(str_obj,'s{0}'.format(a)):
                    _lock_scale = True
                else:
                    _scale_good.append(a)
                    
            if _lock_scale:
                _scale = {}
                log.debug("|{0}| >> lock scale detected...".format(_str_func))
                for a in _scale_good:
                    _scale[a] = ATTR.get(str_obj,'s{0}'.format(a))
                if _scale:
                    log.debug("|{0}| >> lock scale detected. Good: {1} | fixed: {2}".format(_str_func, _scale_good, _scale))
                    
                    _dat['simpleScale'] = _scale
                else:
                    _dat['simpleScale'] = False
            else:
                _dat['scale'] = mObj.scale
                log.debug("|{0}| >> scale: {1}".format(_str_func, _dat['scale']))
                
            
            
            #Sub shapers ---------------------------------------------------------------------------------
            ml_subShapers = mObj.msgList_get('subShapers')
            if ml_subShapers:
                _d = {}
                log.debug("|{0}| >>  subShapers...".format(_str_func))
                for ii,mShaper in enumerate(ml_subShapers):
                    str_shaper = mShaper.mNode
                    _d_sub = {}
                    
                    _d_sub['position'] =  mShaper.p_positionEuclid.reflect(reflectionVector)
                    
                    #import cgm.core.lib.locator_utils as LOC
                    #LOC.create(position=_d_sub['position'])

                    for atr in 'rs':
                        _l_sub = []
                        for axs in 'xyz':
                            if atr == 't':
                                if axs == 'x':
                                    _l_sub.append(-ATTR.get(str_shaper,"{0}{1}".format(atr,axs)))
                                    continue
                            elif atr == 'r':
                                if axs in list('zy'):
                                    _l_sub.append(-ATTR.get(str_shaper,"{0}{1}".format(atr,axs)))
                                    continue
                            _l_sub.append(ATTR.get(str_shaper,"{0}{1}".format(atr,axs)))
                        _d_sub[atr] = _l_sub
                    if _d_sub:
                        _d[ii] = _d_sub
                if _d:
                    _dat['subShapers'] = _d
                    #pprint.pprint(_d)
            
            #Sub shapers ---------------------------------------------------------------------------------
            mLoftCurve = mObj.getMessage('loftCurve',asMeta=True)
            if mLoftCurve:
                mLoftCurve = mLoftCurve[0]
                _d = {}
                log.debug("|{0}| >>  loftCurve: {1}.".format(_str_func,mLoftCurve))
                str_shaper = mLoftCurve.mNode
                _d_sub = {}
                _d_sub['position'] =  mLoftCurve.p_positionEuclid.reflect(reflectionVector)
                
                for atr in 'rs':
                    _l_sub = []
                    for axs in 'xyz':
                        if atr == 't':
                            if axs == 'x':
                                _l_sub.append(-ATTR.get(str_shaper,"{0}{1}".format(atr,axs)))
                                continue
                        elif atr == 'r':
                            if axs in list('zy'):
                                _l_sub.append(-ATTR.get(str_shaper,"{0}{1}".format(atr,axs)))
                                continue
                        _l_sub.append(ATTR.get(str_shaper,"{0}{1}".format(atr,axs)))
                    _d_sub[atr] = _l_sub

                if _d_sub:
                    _dat['loftCurve'] = _d_sub
                    #pprint.pprint(_d_sub)            
    
            #mObj.LookRotation( reflectAim, reflectUp )
            #SNAP.aim_atPoint(mObj.mNode,reflectAimPoint, vectorUp=reflectUp,mode='vector')
            #reflectAim = block.templatePositions[index].TransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
            #reflectUp  = block.templatePositions[index].TransformDirection( MATH.Vector3(0,1,0)).reflect( rootReflectionVector )
            #mirrorBlock.templatePositions[index].LookRotation( reflectAim, reflectUp )            
            #l_dat.append([posNew,reflectAimPoint,reflectUp,reflectAim])
            l_dat.append(_dat)
            #l_dat.append({'pos':posNew,'aimPoint':reflectAimPoint,'up':reflectUp,'aim':reflectAim, 'scale':mObj.scale})
            
        #pprint.pprint(l_dat)
        
        log.debug(cgmGEN._str_subLine)            
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
        
        #return
        for i_loop in range(2):
            log.debug("|{0}| >> push values...".format(_str_func))
            
            for i,mObj in enumerate(ml_targetControls):
                try:
                    log.debug("|{0}| >> [{1}] | {2}".format(_str_func,i,mObj.p_nameShort))            
                    
                    _dat = l_dat[i]
                    str_obj = mObj.mNode
                    if str_obj != _dat.get('target'):
                        log.warning("|{0}| >> [{1}] | {2} data mismatch | {3}".format(_str_func,i,mObj.p_nameShort,_dat.get('target')))            
                        
                    
                    if 'pivotHelper' in mObj.p_nameShort:
                        _cgmName = mObj.cgmName
                        
                        if _cgmName in ['left','right']:
                            _dat = l_dat[ md_remap['pivotHelper'][_cgmName] ]
        
                    log.debug("|{0}| >> Push mObj: {1}".format(_str_func,mObj.p_nameShort))            
                    #mObj.p_positionEuclid = _dat['pos']
                    mObj.p_positionEuclid = _dat['pos']
                    
                    if _dat.has_key('simpleRot'):
                        _rot = _dat.get('simpleRot')
                        if _rot != False:
                            log.debug("|{0}| >> Simple rot mObj: {1} | {2}".format(_str_func,
                                                                                   mObj.p_nameBase,
                                                                                   _rot))            
                            for a,v in _rot.iteritems():
                                ATTR.set(str_obj,'r{0}'.format(a),v)
                    else:
                        SNAP.aim_atPoint(mObj.mNode, _dat['aimPoint'], vectorUp=_dat['up'],mode='vector')
                        """
                        if not i_loop:
                            import cgm.core.lib.locator_utils as LOC
                            LOC.create(position=_dat['aimPoint'], name='{0}_aim__loc'.format(str_obj))
                            print mObj.mNode
                            print _dat['aimPoint']
                            print _dat['up']"""
                        
                    #Subshapers ----------------------------------------------------------------------
                    if _dat.has_key('subShapers'):
                        ml_subShapers = mObj.msgList_get('subShapers')
                        if not ml_subShapers:
                            raise ValueError, "SubShaper data but no datList: {0}".format(mObj)
                        
                        for i_sub,mSub in enumerate(ml_subShapers):
                            _d_sub = _dat['subShapers'][i_sub]
                            for a,d in _d_sub.iteritems():
                                if a == 'position':
                                    log.debug("|{0}| >> subShaper position: {1} | {2}".format(_str_func,mSub,d))
                                    mSub.p_positionEuclid = d
                                else:
                                    ATTR.set(mSub.mNode,a,d)
                                
                                """
                            if _d_sub.get('position'):
                                log.debug("|{0}| >> subShaper position: {1}".format(_str_func,_d_sub.get('position')))
                                mSub.p_position = _d_sub.get('position')"""
                    
                    #Loft Curve ----------------------------------------------------------------------
                    if _dat.has_key('loftCurve'):
                        mLoftCurve = mObj.getMessage('loftCurve',asMeta=True)[0]
                        if not mLoftCurve:
                            raise ValueError, "loftCurve data but no datList: {0}".format(mObj)
                        
                        _d_sub = _dat['loftCurve']
                        for a,d in _d_sub.iteritems():
                            if a == 'position':
                                log.debug("|{0}| >> loftCurve position: {1} | {2}".format(_str_func,mLoftCurve,d))
                                mLoftCurve.p_positionEuclid = d                            
                            else:
                                ATTR.set(mLoftCurve.mNode,a,d)
                            
                    #Scale -----------------------------------------------------------------------
                    if _dat.has_key('simpleScale'):
                        _scale = _dat.get('simpleScale')
                        if _scale != False:
                            log.debug("|{0}| >> Simple scale mObj: {1} | {2}".format(_str_func,
                                                                                   mObj.p_nameBase,
                                                                                   _scale))            
                            for a,v in _scale.iteritems():
                                ATTR.set(str_obj,'s{0}'.format(a),v)
                        else:
                            continue
                    else:
                        try:mObj.scale = _dat['scale']
                        except Exception,err:log.debug("|{0}| >> scale err: {1}".format(_str_func,err))            
                except Exception,err:
                    log.debug("|{0}| >> mObj failure: {1} | {2}".format(_str_func,mObj.p_nameShort,err))            
                
        return l_dat,md_remap
    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
def controlsRig_reset(self):
    try:
        
        _short = self.p_nameShort        
        _str_func = '[{0}] controlsRig_reset'.format(_short)
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
        
        self.moduleTarget.rigNull.moduleSet.reset()
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)


_d_attrStateMasks = {0:[],
                     1:['basicShape',],
                     2:['baseSizeX','baseSizeY','baseSizeZ','blockProfile',
                        'blockScale','proxyShape','shapeDirection'],
                     3:['hasJoint','side','position','attachPoint'],
                     4:[]}

def uiQuery_getStateAttrs(self,mode = None):
    try:
        _str_func = ' uiQuery_getStateAttrs'
        log.debug(cgmGEN.logString_start(_str_func))

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
            
        if _intState > 1:#...prerig
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

     
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
#=============================================================================================================
#>> State Changing
#=============================================================================================================
def templateDelete(self):
    _str_func = 'templateDelete'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError,"|{0}| >> referenced node: {1}".format(_str_func,self.mNode)

    _str_state = self.blockState
    
    #if _str_state != 'template':
        #raise ValueError,"[{0}] is not in template state. state: {1}".format(self.mNode, _str_state)

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
    if self.getMessage('noTransTemplateNull'):
        mc.delete(self.getMessage('noTransTemplateNull'))
    
    #if 'define' in l_blockModuleKeys:
        #log.debug("|{0}| >> BlockModule define call found...".format(_str_func))
        #self.atBlockModule('define')
    if self.getMessage('defineNull'):
        log.debug("|{0}| >> DefineNull found...".format(_str_func))        
        self.defineNull.template = False
    else:
        if 'define' in l_blockModuleKeys:
            log.debug("|{0}| >> BlockModule define call found...".format(_str_func))
            self.atBlockModule('define')        
    #mc.delete(self.getShapes())
    
    d_links = get_stateLinks(self, 'template')
    msgDat_delete(self,d_links)
    
    self.blockState = 'define'#...yes now in this state
    return True

def templateAttrLock(self,v=1):
    self.template = v
    
def test_exception(self,*args,**kws):
    try:
        raise ValueError,"here"
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
def test_nestedException(self,*args,**kws):
    try:
        test_exception(self,*args,**kws)
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
def template_segment(self,aShapers = 'numShapers',aSubShapers = 'numSubShapers',
                     loftShape=None,l_basePos = None, baseSize=1.0,
                     sizeWidth = 1.0, sizeLoft=1.0,
                     side = None,orientHelperPlug = 'orientHelper',templateAim='toEnd',
                     mTemplateNull = None,mNoTransformNull = None,
                     mDefineEndObj=None):
    """
    Factored out our segment setup to clean up 
    """
    _str_func = 'template_segment'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    _short = self.p_nameShort    
    _size_handle = baseSize
    _size_loft = sizeLoft
    _side = side
    _size_width = sizeWidth
    _loftShape = loftShape
    _l_basePos = l_basePos
    md_handles = {}
    ml_handles = []
    ml_loftHandles = []
    md_loftHandles ={}
    ml_shapers = []
    ml_handles_chain = []
    _templateAim = templateAim
    
    try:
        _short = self.mNode        
        _int_shapers = self.getMayaAttr(aShapers)
        _int_sub = self.getMayaAttr(aSubShapers)        
        _loftSetup = self.getEnumValueString('loftSetup')
        _loftShape = self.getEnumValueString('loftShape')
        
        _baseName = self.cgmName
        if not _baseName:
            _baseName = self.blockType
        
        if _loftSetup == 'loftList':
            _l_loftShapes =  ATTR.datList_get(_short,'loftList',enum=True) or []
            if len(_l_loftShapes) != _int_shapers:
                log.warning("|{0}| >> Not enough shapes in loftList. Padding with loftShape".format(_str_func,i,_loftShape))
                while len(_l_loftShapes) < _int_shapers:
                    _l_loftShapes.append(self.loftShape)
        else:
            _l_loftShapes = [_loftShape for i in range(_int_shapers)]

        log.debug("|{0}| >> loftShapes: {1}".format(_str_func,_l_loftShapes)) 
        
        
        mHandleFactory = self.asHandleFactory()
        mRootUpHelper = self.vectorUpHelper
        _mVectorAim = MATH.get_obj_vector(self.vectorEndHelper.mNode,asEuclid=True)
        _mVectorUp = MATH.get_obj_vector(mRootUpHelper.mNode,'y+',asEuclid=True)            
        #pprint.pprint(vars())
        for i,n in enumerate(['start','end']):
            log.debug("|{0}| >> {1}:{2}...".format(_str_func,i,n)) 
            mHandle = mHandleFactory.buildBaseShape('cubeOpen',baseSize = _size_handle, shapeDirection = 'z+')
            mHandle.p_parent = mTemplateNull
        
            mHandle.resetAttrs()
        
            self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
            mHandle.doStore('cgmType','blockHandle')
            mHandle.doStore('cgmNameModifier',n)
        
            mHandle.doName()
        
            #Convert to loft curve setup ----------------------------------------------------
            mHandleFactory.setHandle(mHandle.mNode)
            #mHandleFactory = self.asHandleFactory(mHandle.mNode)
            if n == 'start':
                _shape = 'loft' + _l_loftShapes[0][0].capitalize() + ''.join(_l_loftShapes[0][1:])
            else:
                _shape = 'loft' + _l_loftShapes[-1][0].capitalize() + ''.join(_l_loftShapes[-1][1:])
                
            mLoftCurve = mHandleFactory.rebuildAsLoftTarget(_shape, _size_loft, shapeDirection = 'z+',rebuildHandle = False)
            mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
        
            mHandleFactory.color(mHandle.mNode)            
            mHandle.p_position = _l_basePos[i]
        
            md_handles[n] = mHandle
            ml_handles.append(mHandle)
        
            md_loftHandles[n] = mLoftCurve                
            ml_loftHandles.append(mLoftCurve)
        
            mLoftCurve.p_parent = mTemplateNull
            mTransformedGroup = mLoftCurve.getMessageAsMeta('transformedGroup')
            if not mTransformedGroup:
                mTransformedGroup = mLoftCurve.doGroup(True,True,asMeta=True,typeModifier = 'transformed',setClass='cgmObject')
            mHandle.doConnectOut('scale', "{0}.scale".format(mTransformedGroup.mNode))
            mc.pointConstraint(mHandle.mNode,mTransformedGroup.mNode,maintainOffset=False)
        
            mBaseAttachGroup = mHandle.doGroup(True,True, asMeta=True,typeModifier = 'attach')
        
        #Constrain the define end to the end of the template handles
        if mDefineEndObj:
            mc.pointConstraint(md_handles['end'].mNode,mDefineEndObj.mNode,maintainOffset=False)
    
    
        #>> Base Orient Helper ============================================================================
        log.debug("|{0}| >> Base orient helper...".format(_str_func) + '-'*40) 
    
        mHandleFactory = self.asHandleFactory(md_handles['start'].mNode)
        mBaseOrientCurve = mHandleFactory.addOrientHelper(baseSize = _size_width,
                                                          shapeDirection = 'y+',
                                                          setAttrs = {'ty':_size_width})
    
        self.copyAttrTo('cgmName',mBaseOrientCurve.mNode,'cgmName',driven='target')
        mBaseOrientCurve.doName()
    
        mBaseOrientCurve.p_parent =  mTemplateNull
        mOrientHelperAimGroup = mBaseOrientCurve.doGroup(True,asMeta=True,typeModifier = 'aim')
        mc.pointConstraint(md_handles['start'].mNode, mOrientHelperAimGroup.mNode )
        
        _const = mc.aimConstraint(ml_handles[1].mNode, mOrientHelperAimGroup.mNode, maintainOffset = False,
                                  aimVector = [0,0,1], upVector = [0,1,0], 
                                  worldUpObject = mRootUpHelper.mNode,
                                  worldUpType = 'objectrotation', 
                                  worldUpVector = [0,1,0])
                #worldUpType = 'vector',
                #worldUpVector = [_worldUpVector.x,_worldUpVector.y,_worldUpVector.z])    
    
        self.connectChildNode(mBaseOrientCurve.mNode,orientHelperPlug)
    
        mBaseOrientCurve.setAttrFlags(['ry','rx','translate','scale','v'])
        mHandleFactory.color(mBaseOrientCurve.mNode,controlType='sub')
        mc.select(cl=True)
    
        ml_handles_chain = copy.copy(ml_handles)
        
        if _int_shapers > 2:
            log.debug("|{0}| >> more handles necessary...".format(_str_func)) 
            #Mid Track curve ============================================================================
            log.debug("|{0}| >> TrackCrv...".format(_str_func)) 
            _midTrackResult = CORERIG.create_at([mObj.mNode for mObj in ml_handles],'cubicTrack',#'linearTrack',
                                                baseName='midTrack')
    
            _midTrackCurve = _midTrackResult[0]
            mMidTrackCurve = cgmMeta.validateObjArg(_midTrackCurve,'cgmObject')
            mMidTrackCurve.rename(_baseName + 'midHandlesTrack_crv')
            mMidTrackCurve.parent = mNoTransformNull
    
            for s in _midTrackResult[1]:
                ATTR.set(s[1],'visibility',False)
    
            #>>> mid main handles =====================================================================
            l_scales = []
            for mHandle in ml_handles:
                l_scales.append(mHandle.scale)
                mHandle.scale = 1,1,1
    
            _l_posMid = CURVES.returnSplitCurveList(mMidTrackCurve.mNode,_int_shapers,markPoints = False)
            #_l_pos = [ DIST.get_pos_by_vec_dist(_pos_start, _vec, (_offsetDist * i)) for i in range(self.numControls-1)] + [_pos_end]
    
    
            #Sub handles... -----------------------------------------------------------------------------------
            log.debug("|{0}| >> Mid Handle creation...".format(_str_func))
            ml_aimGroups = []
            ml_midHandles = []
            ml_midLoftHandles = []
            for i,p in enumerate(_l_posMid[1:-1]):
                log.debug("|{0}| >> mid handle cnt: {1} | p: {2}".format(_str_func,i,p))
                crv = CURVES.create_fromName('sphere2', _size_handle, direction = 'y+')
                mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
    
                self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
                mHandle.doStore('cgmType','blockHandle')
                mHandle.doStore('cgmNameModifier',"mid_{0}".format(i+1))
                mHandle.doName()                
    
                _short = mHandle.mNode
                ml_midHandles.append(mHandle)
                mHandle.p_position = p
    
                mHandle.p_parent = mTemplateNull
                #mHandle.resetAttrs()
    
                mHandleFactory.setHandle(mHandle.mNode)
                mLoftCurve = mHandleFactory.rebuildAsLoftTarget('loft' + _l_loftShapes[i+1][0].capitalize() + ''.join(_l_loftShapes[i+1][1:]),#_loftShape,
                                                                _size_loft,
                                                                shapeDirection = 'z+',rebuildHandle = False)
                mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
                ml_midLoftHandles.append(mLoftCurve)
    
                mTransformedGroup = mHandle.getMessageAsMeta('transformedGroup')
                if not mTransformedGroup:
                    mTransformedGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'transformed')
                #mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
                #mAimGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'aim')
    
    
                _vList = DIST.get_normalizedWeightsByDistance(mTransformedGroup.mNode,
                                                              [ml_handles[0].mNode,ml_handles[-1].mNode])
    
                #_scale = mc.scaleConstraint([ml_handles[0].mNode,ml_handles[-1].mNode],
                #                            mTransformedGroup.mNode,maintainOffset = False)
    
                _res_attach = RIGCONSTRAINT.attach_toShape(mTransformedGroup.mNode, mMidTrackCurve.mNode, 'conPoint')
                TRANS.parent_set(_res_attach[0], mNoTransformNull.mNode)
    
                mTransformedGroup.resetAttrs('rotate')
    
    
                mLoftCurve.p_parent = mTemplateNull
                mLoftTransformedGroup = mLoftCurve.getMessageAsMeta('transformedGroup')
                if not mLoftTransformedGroup:
                    mLoftTransformedGroup = mLoftCurve.doGroup(True,asMeta=True,typeModifier = 'transformed')
    
                #mTransformedGroup = mLoftCurve.doGroup(True,True,asMeta=True,typeModifier = 'transformed')
                #mHandle.doConnectOut('scale', "{0}.scale".format(mScaleGroup.mNode))
                mc.scaleConstraint(mHandle.mNode,
                                   mLoftTransformedGroup.mNode,maintainOffset = False)                
                mc.pointConstraint(mHandle.mNode,mLoftTransformedGroup.mNode,maintainOffset=False)
    
    
                #for c in [_scale]:
                    #CONSTRAINT.set_weightsByDistance(c[0],_vList)
    
                mHandleFactory = self.asHandleFactory(mHandle.mNode)
    
                CORERIG.colorControl(mHandle.mNode,_side,'main',transparent = True)
    
            #Push scale back...
            for i,mHandle in enumerate(ml_handles):
                mHandle.scale = l_scales[i]
    
    
    
            #Main Track curve ============================================================================
            ml_handles_chain = [ml_handles[0]] + ml_midHandles + [ml_handles[-1]]
    
            log.debug("|{0}| >> Main TrackCrv...".format(_str_func)) 
            _mainTrackResult = CORERIG.create_at([mObj.mNode for mObj in ml_handles_chain],'linearTrack',
                                                 baseName='mainTrack')
    
            mMainTrackCurve = cgmMeta.validateObjArg(_mainTrackResult[0],'cgmObject')
            mMainTrackCurve.rename(_baseName+ 'mainHandlesTrack_crv')
            mMainTrackCurve.parent = mNoTransformNull
    
            for s in _mainTrackResult[1]:
                ATTR.set(s[1],'visibility',False)            
    
    
    
        log.debug("|{0}| >> Aim main handles...".format(_str_func)+'-'*40) 
    
        #AimEndHandle ============================================================================
        log.debug("|{0}| >> Aim end...".format(_str_func)) 
        mGroup =  md_handles['end'].doGroup(True,True,asMeta=True,typeModifier = 'aim')            
        _const = mc.aimConstraint(self.mNode, mGroup.mNode,
                                  maintainOffset = False,
                                  aimVector = [0,0,-1],
                                  upVector = [0,1,0], 
                                  worldUpObject = mRootUpHelper.mNode,
                                  worldUpType = 'objectrotation', 
                                  worldUpVector = [0,1,0])        
        #mAimGroup = md_handles['end'].doGroup(True, asMeta=True,typeModifier = 'aim')
        #...not doing this now...
        #SNAP.go(md_handles['end'].mNode, self.mNode, position=False)
    
        """
                        _const = mc.aimConstraint(self.mNode, md_handles['end'].mNode, maintainOffset = False,
                                                  aimVector = [0,0,-1], upVector = [0,1,0], 
                                                  worldUpObject = mBaseOrientCurve.mNode,
                                                  worldUpType = 'objectrotation', 
                                                  worldUpVector = [0,1,0])"""
    
        #cgmMeta.cgmNode(_const[0]).doConnectIn('worldUpVector','{0}.baseUp'.format(self.mNode))
    
    
        #AimStartHandle ============================================================================
        log.debug("|{0}| >> Aim main handles...".format(_str_func)) 
        mGroup =  md_handles['start'].doGroup(True,True,asMeta=True,typeModifier = 'aim')            
        _const = mc.aimConstraint(md_handles['end'].mNode, mGroup.mNode,
                                  maintainOffset = False,
                                  aimVector = [0,0,1],
                                  upVector = [0,1,0], 
                                  worldUpObject = mRootUpHelper.mNode,
                                  worldUpType = 'objectrotation', 
                                  worldUpVector = [0,1,0])
    
    
    
        #>>> Aim Main loft curves ================================================================== 
        log.debug("|{0}| >> Aim main loft curves...".format(_str_func)) 
    
    
        #Aim the segment -------------------------------------------------------------------------
        """
                if _templateAim == 'toEnd':
                    for i,mHandle in enumerate(ml_handles):
                        if mHandle != ml_handles[0] and mHandle != ml_handles[-1]:
                        #if i > 0 and i < len(ml_handles) - 1:
                            mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
    
                            mc.aimConstraint(ml_handles[-1].mNode, mAimGroup.mNode, maintainOffset = True, #skip = 'z',
                                             aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = mBaseOrientCurve.mNode,
                                             worldUpType = 'objectrotation', worldUpVector = [0,1,0])
                else:#chain
                    for i,mHandle in enumerate(ml_handles):
                        if mHandle != ml_handles[0] and mHandle != ml_handles[-1]:
                        #if i > 0 and i < len(ml_handles) - 1:
                            mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
    
                            mc.aimConstraint(ml_handles[i+1].mNode, mAimGroup.mNode,
                                             maintainOffset = True,
                                             aimVector = [0,0,1],
                                             upVector = [0,1,0],
                                             worldUpObject = mHandle.masterGroup.mNode,
                                             worldUpType = 'objectrotation', worldUpVector = [0,1,0])"""
    
    
        for i,mHandle in enumerate(ml_handles_chain):
            mLoft = mHandle.loftCurve
            _str_handle = mHandle.mNode
    
            mTransformedGroup = mLoft.getMessageAsMeta('transformedGroup')
            if not mTransformedGroup:
                mTransformedGroup = mLoft.doGroup(True,asMeta=True,typeModifier = 'transformed')
            mLoft.visibility = 1
            #mLoft.setAttrFlags(['translate'])
    
            for mShape in mLoft.getShapes(asMeta=True):
                mShape.overrideDisplayType = 0
    
            _worldUpType = 'objectrotation'
            _worldUpBack = 'objectrotation'
    
    
            _aimBack = None
            _aimForward = None
            _backUpObj = None
    
            if mHandle == ml_handles_chain[0]:
                _aimForward = ml_handles_chain[i+1].mNode
            elif mHandle == ml_handles_chain[-1]:
                if len(ml_handles_chain)>2:
                    _aimBack = ml_handles_chain[-2].mNode#md_handles['start'].mNode#ml_handles_chain[].mNode
                else:
                    _aimBack = md_handles['start'].mNode
            else:
                _aimForward =  ml_handles_chain[i+1].mNode
                _aimBack  =  ml_handles_chain[i-1].mNode
    
            if _aimBack and md_handles.get('lever'):
                if _aimBack == md_handles.get('lever').mNode:
                    _backUpObj = md_handles.get('lever').mNode
    
            if _aimForward and _aimBack is None:
                mc.aimConstraint(_aimForward, mTransformedGroup.mNode, maintainOffset = False,
                                 aimVector = [0,0,1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = _worldUpType, 
                                 worldUpVector = [0,1,0])
            elif _aimBack and _aimForward is None:
                mc.aimConstraint(_aimBack, mTransformedGroup.mNode, maintainOffset = False,
                                 aimVector = [0,0,-1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = _worldUpBack, 
                                 worldUpVector = [0,1,0])
            else:
                mAimForward = mLoft.doCreateAt()
                mAimForward.p_parent = mLoft.p_parent
                mAimForward.doStore('cgmName',mHandle)                
                mAimForward.doStore('cgmTypeModifier','forward')
                mAimForward.doStore('cgmType','aimer')
                mAimForward.doName()
    
                mAimBack = mLoft.doCreateAt()
                mAimBack.p_parent = mLoft.p_parent
                mAimBack.doStore('cgmName',mHandle)                                
                mAimBack.doStore('cgmTypeModifier','back')
                mAimBack.doStore('cgmType','aimer')
                mAimBack.doName()
    
                mc.aimConstraint(_aimForward, mAimForward.mNode, maintainOffset = False,
                                 aimVector = [0,0,1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = _worldUpType, 
                                 worldUpVector = [0,1,0])
    
                if _backUpObj == None:
                    _backUpObj =  mBaseOrientCurve.mNode
    
                mc.aimConstraint(_aimBack, mAimBack.mNode, maintainOffset = False,
                                 aimVector = [0,0,-1], upVector = [0,1,0], 
                                 worldUpObject = _backUpObj,
                                 worldUpType = _worldUpType, 
                                 worldUpVector = [0,1,0])                
    
                const = mc.orientConstraint([mAimForward.mNode, mAimBack.mNode],
                                            mTransformedGroup.mNode, maintainOffset = False)[0]
    
                ATTR.set(const,'interpType',2)#.shortest...
    
                #...also aim our main handles...
                
                if mHandle not in [md_handles['end'],md_handles['start']]:
                    log.debug("|{0}| >> {2} | Aiming Handle: {1}".format(_str_func,mHandle,_templateAim))
                    
                    mHandleAimGroup = mHandle.getMessageAsMeta('transformedGroup')
                    if not mHandleAimGroup:
                        mHandleAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'transformed')
    
                    if _templateAim == 'toEnd':
                        mc.aimConstraint(md_handles['end'].mNode,
                                         mHandleAimGroup.mNode, maintainOffset = False,
                                         aimVector = [0,0,1], upVector = [0,1,0], 
                                         worldUpObject = mBaseOrientCurve.mNode,
                                         worldUpType = 'objectrotation', 
                                         worldUpVector = [0,1,0])                        
                    else:
                        mc.aimConstraint(_aimForward, mHandleAimGroup.mNode, maintainOffset = False,
                                         aimVector = [0,0,1], upVector = [0,1,0], 
                                         worldUpObject = mBaseOrientCurve.mNode,
                                         worldUpType = 'objectrotation', 
                                         worldUpVector = [0,1,0])
    
    
            if mHandle in [md_handles['start'],md_handles['end']]:
                _lock = []
                if mHandle == md_handles['start']:
                    _lock.append('rotate')
    
                #ATTR.set_alias(mHandle.mNode,'sy','handleScale')    
                #ATTR.set_standardFlags( mHandle.mNode, _lock)
                #mHandle.doConnectOut('sy',['sx','sz'])
                ATTR.set_standardFlags( mHandle.mNode, _lock)
    
            else:
                ATTR.set_standardFlags( mHandle.mNode, ['rotate','sz'])
                ATTR.connect('{0}.sy'.format(mHandle.mNode), '{0}.sz'.format(mHandle.mNode))
    
    
        ml_shapers = copy.copy(ml_handles_chain)
        #>>> shaper handles =======================================================================
        if _int_sub:
            _numSubShapers = _int_sub
            ml_shapers = []
            log.debug("|{0}| >> Sub shaper handles: {1}".format(_str_func,_numSubShapers))
    
            mOrientHelper = mBaseOrientCurve
    
            log.debug("|{0}| >> pairs...".format(_str_func))
    
    
            ml_handlesToShaper = ml_handles_chain
            ml_shapers = [ml_handlesToShaper[0]]
    
            ml_pairs = LISTS.get_listPairs(ml_handlesToShaper)
            #pprint.pprint(ml_pairs)
    
    
            for i,mPair in enumerate(ml_pairs):
                log.debug(cgmGEN._str_subLine)
                ml_shapersTmp = []
    
                _mStart = mPair[0]
                _mEnd = mPair[1]
                _end = _mEnd.mNode
                log.debug("|{0}| >> pairs: {1} | end: {2}".format(_str_func,i,_end))
    
                _pos_start = _mStart.p_position
                _pos_end = _mEnd.p_position 
    
                _leverLoftAimMode = False
    
        
    
                _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)
                _offsetDist = DIST.get_distance_between_points(_pos_start,_pos_end) / (_numSubShapers+1)
                _l_pos_seg = [ DIST.get_pos_by_vec_dist(_pos_start,
                                                        _vec,
                                                        (_offsetDist * ii)) for ii in range(_numSubShapers+1)] + [_pos_end]
    
                _mVectorAim = MATH.get_vector_of_two_points(_pos_start, _pos_end,asEuclid=True)
                #_mVectorUp = _mVectorAim.up()
                #_worldUpVector = [_mVectorUp.x,_mVectorUp.y,_mVectorUp.z]        
    
    
                #Linear track curve ----------------------------------------------------------------------
                _linearCurve = mc.curve(d=1,p=[_pos_start,_pos_end])
                mLinearCurve = cgmMeta.validateObjArg(_linearCurve,'cgmObject')
    
                l_clusters = []
                for ii,cv in enumerate(mLinearCurve.getComponents('cv')):
                    _res = mc.cluster(cv, n = 'seg_{0}_{1}_cluster'.format(mPair[0].p_nameBase,ii))
                    TRANS.parent_set(_res[1], mTemplateNull)
                    mc.pointConstraint(mPair[ii].mNode,
                                       _res[1],maintainOffset=True)
                    ATTR.set(_res[1],'v',False)                
                    l_clusters.append(_res)
    
                mLinearCurve.parent = mNoTransformNull
                mLinearCurve.rename('seg_{0}_trackCrv'.format(i))
    
    
    
                #Tmp loft mesh -------------------------------------------------------------------
                _l_targets = [mObj.loftCurve.mNode for mObj in mPair]
                log.debug(_l_targets)
                _res_body = mc.loft(_l_targets, o = True, d = 3, po = 0 )
                _str_tmpMesh =_res_body[0]
    
                l_scales_seg = []
    
                #for mHandle in mPair:
                    #l_scales_seg.append(mHandle.scale)
                    #mHandle.scale = 1,1,1
    
                #Sub handles... --------------------------------------------------------------------------
                for ii,p in enumerate(_l_pos_seg[1:-1]):
                    #mHandle = mHandleFactory.buildBaseShape('circle', _size, shapeDirection = 'y+')
                    mHandle = cgmMeta.cgmObject(name = 'subHandle_{0}_{1}'.format(i,ii))
                    _short = mHandle.mNode
                    ml_handles.append(mHandle)
                    mHandle.p_position = p
                    if _leverLoftAimMode:
                        SNAP.aim_atPoint(_short,_l_pos_seg[ii+2],'z+', 'y+', mode='vector',
                                         vectorUp = _mVectorLeverUp)
                    else:
                        SNAP.aim_atPoint(_short,_l_pos_seg[ii+2],'z+', 'y+', mode='vector', vectorUp = _mVectorUp)
    
                    #...Make our curve
                    _d = RAYS.cast(_str_tmpMesh, _short, 'x+')
                    #pprint.pprint(_d)
                    log.debug("|{0}| >> Casting {1} ...".format(_str_func,_short))
                    cgmGEN.log_info_dict(_d)
                    _v = _d['uvs'][_str_tmpMesh][0][0]
                    log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))
    
                    #>>For each v value, make a new curve -----------------------------------------------------------------        
                    #duplicateCurve -ch 1 -rn 0 -local 0  "loftedSurface2.u[0.724977270271534]"
                    _crv = mc.duplicateCurve("{0}.u[{1}]".format(_str_tmpMesh,_v), ch = 0, rn = 0, local = 0)
                    log.debug("|{0}| >> created: {1} ...".format(_str_func,_crv))  
    
                    CORERIG.shapeParent_in_place(_short, _crv, False)
    
                    #self.copyAttrTo(_baseNameAttrs[1],mHandle.mNode,'cgmName',driven='target')
                    self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
                    mHandle.doStore('cgmNameModifier','shapeHandle_{0}_{1}'.format(i,ii))
                    mHandle.doStore('cgmType','blockHandle')
                    mHandle.doName()
    
                    mHandle.p_parent = mTemplateNull
    
                    mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
                    mGroup.p_parent = mTemplateNull
    
                    _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,[mPair[0].mNode,mPair[1].mNode])
    
                    _scale = mc.scaleConstraint([mPair[0].mNode,mPair[1].mNode],mGroup.mNode,maintainOffset = False)#Point contraint loc to the object
    
                    if _leverLoftAimMode:
                        upObj = md_handles['lever'].mNode
                    else:
                        upObj = mBaseOrientCurve.mNode
    
                    mc.aimConstraint([_end], mGroup.mNode, maintainOffset = False, #skip = 'z',
                                     aimVector = [0,0,1], upVector = [0,1,0],
                                     worldUpObject = upObj,
                                     worldUpType = 'objectrotation', worldUpVector = [0,1,0])                    
    
                    _res_attach = RIGCONSTRAINT.attach_toShape(mGroup.mNode, 
                                                               mLinearCurve.mNode,
                                                               'conPoint')
                    TRANS.parent_set(_res_attach[0], mNoTransformNull.mNode)
    
                    for c in [_scale]:
                        CONSTRAINT.set_weightsByDistance(c[0],_vList)
    
                    #Convert to loft curve setup ----------------------------------------------------
                    mHandleFactory = self.asHandleFactory(mHandle.mNode)
                    #mHandleFactory.rebuildAsLoftTarget('self', None, shapeDirection = 'z+')
                    mHandle.doStore('loftCurve',mHandle)
    
    
                    CORERIG.colorControl(mHandle.mNode,_side,'sub',transparent = True)        
                    #LOC.create(position = p)
                    ml_shapers.append(mHandle)
                    ml_shapersTmp.append(mHandle)
    
    
                ml_shapers.append(mPair[1])
                mc.delete(_res_body)
    
                _mStart.msgList_connect('subShapers',[mObj.mNode for mObj in ml_shapersTmp])                    
    
                #Push scale back...
                #for mHandle in mPair:
                    #mHandle.scale = l_scales_seg[i]
    
                #Template Loft Mesh -------------------------------------
                #mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]        
                #for s in mTemplateLoft.getShapes(asMeta=True):
                    #s.overrideDisplayType = 1       
    
    
                #Aim the segment
                """
                        for ii,mHandle in enumerate(ml_shapersTmp):
                            mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
                            log.debug("|{0}| >> seg constrain: {1} {2} | end: {3}".format(_str_func,i,ii,_end))
    
                            mc.aimConstraint([_end], mAimGroup.mNode, maintainOffset = True, #skip = 'z',
                                             aimVector = [0,0,1], upVector = [0,1,0],
                                             worldUpObject = mBaseOrientCurve.mNode,
                                             worldUpType = 'objectrotation', worldUpVector = [0,1,0])"""        
        
        return md_handles,ml_handles,ml_shapers,ml_handles_chain
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


    
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
        reload(mBlockModule)
        mBlockModule.prerig(self)
        #self.atBlockModule('prerig')

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
    msgDat_delete(self,d_links)
    
    self.blockState = 'template'#...yes now in this state
    return True


def skeleton(self):
    _str_func = 'skeleton'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError,"|{0}| >> referenced node: {1}".format(_str_func,self.mNode)

    _str_state = self.blockState
    
    if _str_state == 'skeleton':
        log.debug("|{0}| >> Already in skeleton state...".format(_str_func))                    
        return True
    elif _str_state != 'prerig':
        raise ValueError,"[{0}] is not in prerig template. state: {1}".format(self.mNode, _str_state)

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    self.blockState = 'prerig>skeleton'#...buffering that we're in process

    mBlockModule = self.p_blockModule
    
    for c in ['skeleton_build','build_skeleton']:
        if c in mBlockModule.__dict__.keys():
            log.debug("|{0}| >> BlockModule {1} call found...".format(_str_func,c))            
            self.atBlockModule(c)

    self.blockState = 'skeleton'#...yes now in this state
    return True

def skeleton_delete(self):
    _str_func = 'skeleton_delete'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError,"|{0}| >> referenced node: {1}".format(_str_func,self.mNode)

    _str_state = self.blockState
    
    if _str_state != 'skeleton':
        raise ValueError,"[{0}] is not in skeleton state. state: {1}".format(self.mNode, _str_state)

    #>>>Children ------------------------------------------------------------------------------------
    def closeOut():
        d_links = get_stateLinks(self, 'skeleton')
        msgDat_delete(self,d_links)
        self.blockState = 'prerig'#...yes now in this state
        
    #>>>Meat ------------------------------------------------------------------------------------
    self.blockState = 'skeleton>prerig'#...buffering that we're in process

    mBlockModule = self.p_blockModule
    l_blockModuleKeys = mBlockModule.__dict__.keys()
    
    if 'skeleton_delete' in l_blockModuleKeys:
        log.debug("|{0}| >> BlockModule skeleton_delete call found...".format(_str_func))
        self.atBlockModule('skeleton_delete')
    
    else:
        mModule = self.getMessageAsMeta('moduleTarget')
        if mModule:
            mRigNull = mModule.rigNull
            if not mRigNull:
                closeOut()
                return log.error(cgmGEN.logString_sub(_str_func,'No rigNull'))
            # return log.error("|{0}| >> No joints found".format(_str_func))                
            if mRigNull:
                ml_joints = mRigNull.msgList_get('moduleJoints')
                if not ml_joints:
                    closeOut()
                    return log.error("|{0}| >> No joints found".format(_str_func))
                else:
                    ml_children = []
                    for mJnt in ml_joints:
                        ml_childrenTmp = mJnt.getChildren(asMeta=True)
                        log.debug("|{0}| >> joint: {1} | children: {2}".format(_str_func,mJnt.p_nameBase,ml_childrenTmp))
                        for mChild in ml_childrenTmp:
                            if mChild not in ml_children and mChild not in ml_joints:
                                ml_children.append(mChild)
                                
                    for mChild in ml_children:
                        log.debug("|{0}| >> Stray child! {1}".format(_str_func,mChild))
                        mChild.p_parent = False
                        
                    ml_joints[0].delete()
        
    closeOut()
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
    elif _str_state != 'skeleton':
        raise ValueError,"[{0}] is not in skeleton template. state: {1}".format(self.mNode, _str_state)

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    self.blockState = 'skeleton>rig'#...buffering that we're in process
    if not 'autoBuild' in kws.keys():
        kws['autoBuild'] = True
    
    try:self.asRigFactory(**kws)
    except ValueError,err:
        self.blockState = 'skeleton'
        log.error(err)
        return False
    
    if not is_rigged(self):
        log.error("|{0}| >> Failed to return is_rigged...".format(_str_func))                    
        self.blockState = 'skeleton'
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


    #>>>Meat ------------------------------------------------------------------------------------
    self.blockState = 'rig>skeleton'#...buffering that we're in process
    
    mModuleTarget = self.moduleTarget
    mModuleTarget.rig_disconnect()
    
    
    if mModuleTarget:
        log.debug("|{0}| >> ModuleTarget: {1}".format(_str_func,mModuleTarget))
        ml_blockControls = self.UTILS.controls_get(self,True,True,True)
        for mNode in ml_blockControls:
            try:ml_blockControls.extend(mNode.getShapes(asMeta=1))
            except:pass
            
        if mModuleTarget.mClass ==  'cgmRigModule':
            self.template = False
            try:self.noTransTemplateNull.template=True
            except:pass
            mRigNull = mModuleTarget.getMessageAsMeta('rigNull')
            
            _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
            if _bfr:
                log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
                mc.delete([mObj.mNode for mObj in _bfr])
            mFaceSet = mRigNull.getMessageAsMeta('faceSet')
            
            #Rig nodes....
            ml_rigNodes = mRigNull.getMessageAsMeta('rigNodes')
            for mNode in ml_rigNodes:
                if mNode in [mModuleTarget,mRigNull,mFaceSet]:
                    continue
                if mNode in ml_blockControls:
                    log.debug("|{0}| >> block control in rigNodes: {1}".format(_str_func,mNode))
                    continue
                try:
                    log.debug("|{0}| >> deleting: {1}".format(_str_func,mNode))                     
                    mNode.delete()
                except:pass
                    #log.debug("|{0}| >> failed...".format(_str_func,mNode)) 
            
            mRigNull.rigNodes = []
            """
            #Deform null
            log.debug("|{0}| >> deformNull...".format(_str_func))                        
            _deformNull = mModuleTarget.getMessage('deformNull')
            if _deformNull:
                log.debug("|{0}| >> deformNull: {1}".format(_str_func,_deformNull))
                mc.delete(_deformNull)
            
            #ModuleSet
            log.debug("|{0}| >> moduleSet...".format(_str_func))                        
            _objectSet = mModuleTarget.rigNull.getMessage('moduleSet')
            if _objectSet:
                log.debug("|{0}| >> objectSet: {1}".format(_str_func,_objectSet))
                mc.delete(_objectSet)
                
            #Module
            log.debug("|{0}| >> Children...".format(_str_func))                        
            for mChild in mModuleTarget.rigNull.getChildren(asMeta=True):
                mChild.delete()
                
            log.debug("|{0}| >> Children of part...".format(_str_func))                        
            for mChild in mModuleTarget.getChildren(asMeta=True):
                if mChild == mRigNull:continue
                mChild.delete()            """
            
            mModuleTarget.p_parent = False
        elif mModuleTarget.mClass == 'cgmRigPuppet':
            pass#mModuleTarget.masterControl.delete()
        
        else:
            log.error("|{0}| >> Unknown mClass moduleTarget: {1}".format(_str_func,mModuleTarget))                

    mBlockModule = self.p_blockModule
    l_blockModuleKeys = mBlockModule.__dict__.keys()
    if 'rigDelete' in l_blockModuleKeys:
        log.debug("|{0}| >> BlockModule rigDelete call found...".format(_str_func))
        self.p_blockModule.rigDelete(self)
    
    self.blockState = 'skeleton'#...yes now in this state
    set_blockNullTemplateState(self, state=False, define=False)
    return True

@cgmGEN.Timer
def changeState(self, state = None, rebuildFrom = None, forceNew = False,checkDependency=True,**kws):
    #try:
    _str_func = 'changeState'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError,"Referenced node. Cannot verify"
    
    if rebuildFrom:
        log.debug("|{0}| >> Rebuid from: {1}".format(_str_func,rebuildFrom))
        changeState(self,rebuildFrom,forceNew=True)
    
    
    
    #>Validate our data ------------------------------------------------------
    d_upStateFunctions = {'template':template,
                          'prerig':prerig,
                          'skeleton':skeleton,
                          'rig':rig,
                          }
    d_downStateFunctions = {'define':templateDelete,
                            'template':prerigDelete,
                            'prerig':skeleton_delete,
                            'skeleton':rigDelete,
                            }
    d_deleteStateFunctions = {'template':templateDelete,
                              'prerig':prerigDelete,
                              'rig':rigDelete,
                              'skeleton':skeleton_delete,
                              }
    
    stateArgs = BLOCKGEN.validate_stateArg(state)
    _l_moduleStates = BLOCKSHARE._l_blockStates

    if not stateArgs:
        log.debug("|{0}| >> No state arg.".format(_str_func))            
        return False

    _idx_target = stateArgs[0]
    _state_target = stateArgs[1]

    log.debug("|{0}| >> Target state: {1} | {2}".format(_str_func,_state_target,_idx_target))
    


    #>>> Meat
    #========================================================================
    currentState = self.getState(False) 
    
    
    if self.getMayaAttr('isBlockFrame'):
        if _idx_target == 0 and currentState == 0 and forceNew:
            define(self)
            return True
        self.blockState = _state_target
        log.debug(cgmGEN.logString_sub(_str_func,'blockFrame bypass'))
        return    
    
    log.debug('forceNew: {0}'.format(forceNew))
    
    if _idx_target == 0 and currentState == 0 and forceNew:
        define(self)
        return True    
    elif currentState == _idx_target:
        if not forceNew:
            log.debug("|{0}| >> block [{1}] already in {2} state".format(_str_func,self.mNode,currentState))
            return True
        elif currentState > 0:
            log.debug("|{0}| >> Forcing new: {1}".format(_str_func,currentState))                
            currentState_target = self.getState(True) 
            d_deleteStateFunctions[currentState_target](self)

    

    #If we're here, we're going to move through the set states till we get to our spot
    log.debug("|{0}| >> Changing states...".format(_str_func))
    if _idx_target > currentState:
        startState = currentState+1
        
        if _idx_target > 2:
            #>>>Parents ------------------------------------------------------------------------------------
            ml_parents = self.getBlockParents() or []
            ml_dependencies = []
            if ml_parents:
                #ml_children.reverse()
                for mParent in ml_parents:
                    _parentState = mParent.getState(False)
                    if _parentState < _idx_target:
                        ml_dependencies.append(mParent)
                        
                if ml_dependencies:
                    _msg = "Target state: {1} \nThe Following [{0}] parents need processing: ".format(len(ml_dependencies),_state_target)
                    _l_parents = []
                    for mParent in ml_dependencies:
                        _l_parents.append(mParent.p_nameShort)
                    if _l_parents:
                        _msg = _msg + '\n' + '\n'.join(_l_parents)
                    result = mc.confirmDialog(title="Shall we continue",
                                              message= _msg,
                                              button=['OK', 'Cancel'],
                                              defaultButton='OK',
                                              cancelButton='Cancel',
                                              dismissString='Cancel')
                    
                    if result != 'OK':
                        log.error("|{0}| >> Cancelled | {1} | {2}.".format(_str_func,_state_target,self))
                        return False
                        
                    for mParent in ml_dependencies:
                        log.error("|{0}| >> Parent state lower than target state | changing state to: {1} | {2}".format(_str_func, _idx_target, mParent))
                        changeState(mParent,_idx_target)

        
        
        
        doStates = _l_moduleStates[startState:_idx_target+1]
        log.debug("|{0}| >> Going up. First stop: {1} | All stops: {2}".format(_str_func, _l_moduleStates[startState],doStates))

        for doState in doStates:
            #if doState in d_upStateFunctions.keys():
            log.debug("|{0}| >> Up to: {1} ....".format(_str_func, doState))
            if not d_upStateFunctions[doState](self,**kws):
                log.error("|{0}| >> Failed: {1} ....".format(_str_func, doState))
                return False
            elif checkState(self,True) != doState:
                log.error("|{0}| >> No errors but failed to query as:  {1} ....".format(_str_func, doState))                    
                return False
            #else:
            #    log.debug("|{0}| >> No upstate function for {1} ....".format(_str_func, doState))
        return True
    elif _idx_target < currentState:#Going down
        #>>>Children ------------------------------------------------------------------------------------
        if _idx_target > 2:
            ml_children = self.getBlockChildren() or []
            ml_dependencies = []            
            if ml_children:
                ml_children.reverse()
                for mChild in ml_children:
                    _childState = mChild.getState(False)
                    if _childState > _idx_target:
                        ml_dependencies.append(mChild)
                                                
                                        
                if ml_dependencies:
                    _msg = "Target state: {1} \nThe Following [{0}] children need processing: ".format(len(ml_dependencies),_state_target)
                    _l_parents = []
                    for mChild in ml_dependencies:
                        _l_parents.append(mChild.p_nameShort)
                    if _l_parents:
                        _msg = _msg + '\n' + '\n'.join(_l_parents)
                        result = mc.confirmDialog(title="Shall we continue",
                                                  message= _msg,
                                                  button=['OK', 'Cancel'],
                                                  defaultButton='OK',
                                                  cancelButton='Cancel',
                                                  dismissString='Cancel')
                    
                    if result != 'OK':
                        log.error("|{0}| >> Cancelled | {1} | {2}.".format(_str_func,_state_target,self))
                        return False
                        
                    for mChild in ml_dependencies:
                        log.error("|{0}| >> Child state higher than target state | changing state to: {1} | {2}".format(_str_func, _idx_target, mChild))
                        changeState(mChild,_idx_target)
                    
        
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
            elif checkState(self,True)  != doState:
                log.error("|{0}| >> No errors but failed to query as:  {1} ....".format(_str_func, doState))
                return False
            
            #if _idx_target == 0:
                #define(self)
        return True
    else:
        log.warning('Forcing recreate')
        if _state_target in d_upStateFunctions.keys():
            if not d_upStateFunctions[_state_target](self):return False
            return True
    
    #except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def get_shapeOffset(self):
    """
    Get the shape offset value 
    """
    try:
        _str_func = ' get_shapeOffset'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
        ml_check = self.getBlockParents()
        ml_check.insert(0,self)
        
        for mBlock in ml_check:
            l_attrs = ['controlOffset','skinOffset']
            for a in l_attrs:
                if mBlock.hasAttr(a):
                    v = mBlock.getMayaAttr(a)
                    log.debug("|{0}| >> {1} attr found on rigBlock: {2} | {3}".format(_str_func,a,v,mBlock.mNode))                
                    return v            
        return 1
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
def puppet_get(self,mModuleTarget = None):
    try:
        _str_func = ' puppet_get'
        if mModuleTarget is None:
            mModuleTarget = self.getMessageAsMeta('moduleTarget') or False
        
        if self.blockType == 'master':
            return mModuleTarget
        
        mPuppet = mModuleTarget.getMessageAsMeta('modulePuppet')
        if not mPuppet:
            mRoot = self.p_blockRoot
            if mRoot:
                log.debug("|{0}| >>  Checking root for puppet: {1} ".format(_str_func,mRoot))
                mPuppetTest = mRoot.getMessageAsMeta('moduleTarget')
                log.debug("|{0}| >>  root target: {1} ".format(_str_func,mPuppetTest))
                if mPuppetTest and mPuppetTest.mClass == 'cgmRigPuppet':
                    mPuppet = mPuppetTest
                else:
                    mPuppet = False
        return mPuppet
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
def puppet_verify(self):
    """

    """
    try:
        _str_func = 'puppet_verify'
        log.debug(cgmGEN.logString_start(_str_func))

        
        mPuppet = False
        if self.blockType == 'master':
            log.debug("|{0}| >> master...".format(_str_func))                                                    
            if not self.getMessage('moduleTarget'):
                mPuppet = cgmMeta.createMetaNode('cgmRigPuppet',rigBlock=self)
                self.copyAttrTo('cgmName',mPuppet.mNode,'cgmName',driven='target')
                self.moduleTarget = mPuppet.mNode
                ATTR.set_message(mPuppet.mNode, 'rigBlock', self.mNode,simple = True)
                
            else:
                mPuppet = self.moduleTarget
            mPuppet.__verify__()
        else:
            log.debug("|{0}| >> Non master calling...".format(_str_func))                                                                
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
 
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def module_verify(self,moduleType = None, moduleLink = 'moduleTarget',**kws):
    """

    """
    try:
        _str_func = 'module_verify'
        log.debug(cgmGEN.logString_start(_str_func))

        _moduleType = moduleType or self.blockType
        
        def checkAttrs(mModule):
            _nameDict = self.getNameDict(ignore='cgmType')
    
            if not _nameDict.get('cgmName'):
                _nameDict['cgmName'] = kws.get('moduleType',self.blockType)
            _side = self.atUtils('get_side')
    
            if _side != 'center':
                log.debug("|{0}| >> rigBlock side: {1}".format(_str_func,_side))
                _nameDict['cgmDirection'] = _side
    
            for k,v in _nameDict.iteritems():
                if v:
                    log.debug("|{0}| >> Name dat k: {1} | v:{2}".format(_str_func,k,v))
                    mModule.addAttr(k,value = v,lock = True)
            mModule.doName()
            
        
        log.debug("|{0}| >>  moduleType: {1}".format(_str_func,_moduleType))
        
        if self.blockType == 'master':
            return True
        
        _bfr = self.getMessage(moduleLink)
        #_kws = self.module_getBuildKWS()
    
        if _bfr:
            log.debug("|{0}| >> moduleTarget found: {1}".format(_str_func,_bfr))
            mModule = cgmMeta.validateObjArg(_bfr,'cgmObject')
            if mModule.moduleType ==_moduleType:
                checkAttrs(mModule)
                return mModule
 
        log.debug("|{0}| >> Creating moduleTarget...".format(_str_func))  
        mModule = cgmMeta.createMetaNode('cgmRigModule',
                                         rigBlock=self,
                                         moduleLink = moduleLink,
                                         moduleType = _moduleType,
                                         **kws)

        #ATTR.set(mModule.mNode,'moduleType',_moduleType,lock=True)
        return mModule
 
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def is_rigged(self):
    try:
        _str_func = 'is_rigged'
        log.debug(cgmGEN.logString_start(_str_func))

        if self.blockType == 'master':
            if self.getMessage('moduleTarget'):
                if self.moduleTarget.getMessage('masterControl'):
                    return True
            return False
        return self.moduleTarget.atUtils('is_rigged')

    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

def checkState(self,asString=True):
    return getState(self,asString,False)

def getState(self, asString = True, fastCheck=True):
    d_stateChecks = {'template':is_template,
                     'prerig':is_prerig,
                     'skeleton':is_skeleton,
                     'rig':is_rigged}
    try:
        _str_func = 'getState'
        log.debug(cgmGEN.logString_start(_str_func))

        
        _l_blockStates = BLOCKSHARE._l_blockStates
        
        def returnRes(arg):
            if asString:
                return arg
            return _l_blockStates.index(arg)
        
        _str_func = 'getState'
        log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
        
        if fastCheck:
            try:return returnRes(self.blockState)
            except:pass
            
        _blockModule = self.p_blockModule
        _goodState = False
    
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
                if _call:
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
            
            
        return returnRes(_goodState)
        if asString:
            return _goodState
        return _l_blockStates.index(_goodState)
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
    
#Profile stuff ==============================================================================================
def nameList_resetToProfile(self,arg = None):
    try:
        _str_func = 'nameList_resetToProfile'
        log.debug(cgmGEN.logString_start(_str_func))

        if arg is None:
            arg = self.getMayaAttr('blockProfile')
        log.debug("|{0}| >>  arg: {1}".format(_str_func,arg))
        
        mBlockModule = self.p_blockModule
        log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
        reload(mBlockModule)
        l_nameList_current = self.datList_get('nameList')
        log.debug("|{0}| >>  current: {1}".format(_str_func,l_nameList_current))
        l_nameList = []
        try:
            l_nameList =  mBlockModule.d_block_profiles[arg]['nameList']
            log.debug("|{0}| >>  Found on profile: {1}".format(_str_func,l_nameList))
        except Exception,err:
            try:
                l_nameList =  mBlockModule.d_defaultSettings['nameList']
                log.debug("|{0}| >>  Found on module: {1}".format(_str_func,l_nameList))
            except Exception,err:
                pass
        
        if not l_nameList:
            return log.error("|{0}| >>  No nameList dat found: {1}".format(_str_func,arg))
        
        if l_nameList == l_nameList_current:
            log.debug("|{0}| >>  Lists already match".format(_str_func,l_nameList))
            return True
            
        if len(l_nameList) == len(l_nameList_current):
            log.debug("|{0}| >>  Lists lengths match".format(_str_func,l_nameList))
            for i,n in enumerate(l_nameList):
                if n != l_nameList_current[i]:
                    ATTR.datList_setByIndex(self.mNode, 'nameList', n, 'string',indices=i)
        else:
            if getState(self,False)>1:
                return log.error("|{0}| >>  nameLists don't match and higher than template state. Please go to template state before resetting".format(_str_func,self.p_nameShort))
            else:
                self.datList_connect('nameList', l_nameList, mode='string')
        log.debug("|{0}| >>  New: {1}".format(_str_func,self.datList_get('nameList')))
        return l_nameList
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)


def blockProfile_getOptions(self):
    try:
        _str_func = 'blockProfile_getOptions'
        log.debug(cgmGEN.logString_start(_str_func))

        
        mBlockModule = self.p_blockModule
        log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
        reload(mBlockModule)
        
        try:return mBlockModule.d_block_profiles.keys()
        except Exception,err:
            return log.error("|{0}| >>  Failed to query. | {1}".format(_str_func,err))
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
        
def blockProfile_load(self, arg):
    _str_func = 'blockProfile_load'
    log.debug(cgmGEN.logString_start(_str_func))

    _short = self.mNode
    
    mBlockModule = self.p_blockModule
    log.debug("|{0}| >>  BlockModule: {1} | profile: {2}".format(_str_func,mBlockModule,arg))
    try:_d = mBlockModule.d_block_profiles[arg]
    except Exception,err:
        return log.error("|{0}| >>  Failed to query. | {1} | {2}".format(_str_func,err, Exception))
    
    #if not _d.get('blockProfile'):
    #    _d['blockProfile'] = arg
    
    cgmGEN.func_snapShot(vars())
    log.debug("|{0}| >>  {1}...".format(_str_func,arg))    
    for a,v in _d.iteritems():
        try:
            log.debug("|{0}| attr >> '{1}' | v: {2}".format(_str_func,a,v)) 
            _done = False
            _typeDat = type(v)
            if issubclass(_typeDat,list):
                if self.datList_exists(a):
                    log.debug("|{0}| datList...".format(_str_func))
                    if a == 'loftList':
                        ATTR.datList_connect(_short, a, v, 
                                             mode='enum',enum= BLOCKSHARE._d_attrsTo_make['loftShape'])
                    else:
                        mc.select(cl=True)
                        ATTR.datList_connect(_short, a, v, mode='string')
                    _done = True
                else:
                    log.debug("|{0}| Missing datList >> '{1}' | v: {2}.".format(_str_func,a,v))
            if issubclass(_typeDat,dict):
                log.debug("|{0}| dict...".format(_str_func))                                     
                #self.__dict__['a'] = v
                setattr(self,a,v)
                _done = True
            if not _done:
                ATTR.set(_short,a,v)
        except Exception,err:
            log.error("|{0}| Set attr Failure >> '{1}' | value: {2} | err: {3}".format(_str_func,a,v,err)) 
    
    self.doStore('blockProfile',arg)
    log.debug("|{0}| >>  Block: {1} | {2}".format(_str_func,_short,arg))


def buildProfile_load(self, arg):
    _str_func = 'buildProfile_load'
    log.debug(cgmGEN.logString_start(_str_func))

    _short = self.mNode
    mBlockModule = self.p_blockModule
    log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
    reload(mBlockModule)
    
    _d = BLOCKSHARE.d_build_profiles.get(arg,{})
    
    
    try:_d_block = mBlockModule.d_build_profiles[arg]
    except Exception,err:
        return log.error("|{0}| >>  Failed to query. | {1} | {2}".format(_str_func,err, Exception))
    
    
    _blockProfile = 'default'
    if self.hasAttr('blockProfile'):
        _blockProfile = self.blockProfile
        if _d_block.get(_blockProfile):
            _d_block = _d_block.get(_blockProfile)
        else:
            _d_block = _d_block.get('default')
    
    cgmGEN.func_snapShot(vars())

    _d.update(_d_block)

    """
    if self.hasAttr('blockProfile'):
        _strValue = ATTR.get_enumValueString(_short,'blockProfile')
        log.debug("|{0}| >>  blockProfile check: {1}".format(_str_func,_strValue))
        _d_block = _d.get(_strValue,None)
        _d_default = _d.get('default',None)
        if _d_block:
            log.debug("|{0}| >>  Found blockProfile...".format(_str_func))
            _d = _d_block
        elif _d_default:
            log.debug("|{0}| >>  Found default dat...".format(_str_func))
            _d = _d_default"""
            
    #if not _d.get('buildProfile'):
    #    _d['buildProfile'] = arg
        
    if self.blockState not in ['define','template','prerig']:
        log.error(cgmGEN._str_subLine)
        return log.error("|{0}| >>  [FAILED] Block: {1} | profile: {2} | Can't load in state: {3}".format(_str_func,_short,arg,self.blockState))
    
    log.debug("|{0}| >>  Loading: {1}...".format(_str_func,arg))
    for a,v in _d.iteritems():
        try:
            log.debug("|{0}| attr >> '{1}' | v: {2}".format(_str_func,a,v)) 
            _done = False
            if issubclass(type(v),list):
                if self.datList_exists(a):
                    log.debug("|{0}| datList...".format(_str_func))                                     
                    mc.select(cl=True)
                    ATTR.datList_connect(_short, a, v, mode='string')
                    _done = True
            if not _done and mc.objExists("{0}.{1}".format(_short,a)):
                ATTR.set(_short,a,v)
                
            if a == 'numRoll':
                log.debug("special...")                            
                if ATTR.datList_exists(_short,'rollCount'):
                    log.debug("numRoll...")                            
                    l = ATTR.datList_getAttrs(_short,'rollCount')
                    for a2 in l:
                        log.debug("{0}...".format(a2))
                        ATTR.set(_short,a2, v)                
        except Exception,err:
            log.error("|{0}| Set attr Failure >> '{1}' | value: {2} | err: {3}".format(_str_func,a,v,err)) 
    
    self.doStore('buildProfile',arg)
    log.debug("|{0}| >>  [LOADED] Block: {1} | profile: {2}".format(_str_func,_short,arg))


#Profile stuff ==============================================================================================
def doSize(self, mode = None, postState = None):
    """
    mode is placeholder for now
    """
    #try:
    _str_func = 'size'
    log.debug(cgmGEN.logString_start(_str_func))

    
    _str_state = getState(self)
    if _str_state not in ['define','template']:
        raise ValueError,"|{0}| >>  [{1}] is not in define state. state: {2}".format(_str_func,self.mNode, _str_state)
    
    #mBlockModule = self.p_blockModule
    #log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
    #reload(mBlockModule)
    
    l_baseNames = self.datList_get('nameList')
    l_toCreate = l_baseNames#...this needs to be 2
    
    cgmGEN.func_snapShot(vars())
    
    mRigBlock = self
    class castSizer(DRAGFACTORY.clickMesh):
        def __init__(self,rigBlock = mRigBlock,**kws):
            if kws:log.debug("kws: %s"%str(kws))
    
            super(castSizer, self).__init__(**kws)
            self._mRigBlock = mRigBlock
            self.toCreate = l_toCreate
            self._rigBlockTally = 0
            log.debug("|{0}| >>  Please place '{1}'".format(_str_func, self.toCreate[0]))
    
        def release_post_insert(self):
            
            #cgmGEN.func_snapShot(self.__dict__)
            self._rigBlockTally +=1                
            if self._createModeBuffer:
                mc.delete(self._createModeBuffer)
                
            if self._rigBlockTally < len(l_toCreate):
                log.debug("|{0}| >>  Please place '{1}'".format(_str_func, self.toCreate[self._rigBlockTally]))
            else:
                log.debug("|{0}| >>  Finalizing...".format(_str_func,self)+ '-'*80)
                
                l_pos = self.l_returnRaw
                mVector = MATH.get_vector_of_two_points(l_pos[0],l_pos[-1],asEuclid=True)
                mVector.normalize()
                
                mRigBlock.p_position = l_pos[0]
                mRigBlock.baseAim = mVector.x, mVector.y, mVector.z
                
                mRigBlock.baseSizeZ = DIST.get_distance_between_points(l_pos[0],l_pos[-1])
                mRigBlock.baseSizeX = mRigBlock.baseSizeZ/2
                mRigBlock.baseSizeY = mRigBlock.baseSizeX
                
                #cgmGEN.func_snapShot(vars())
                
                log.debug(" pos...")
                for p in l_pos:
                    log.debug("      {0}".format(p))
                log.debug(" baseAim: {0}".format(_str_func,mRigBlock.baseAim))
                log.debug(" baseSize: {0}".format(_str_func,mRigBlock.baseSize))
                
                self.finalize()
                self.dropTool()
                
                if postState:
                    changeState(postState,forceNew=True)
                return True
                
    castSizer(mode = 'midPoint',toCreate = l_toCreate)

    
    #except Exception,err:
        #cgmGEN.cgmExceptCB(Exception,err)


def get_loftCurves(self):
    _str_func = 'get_loftCurves'
    log.debug(cgmGEN.logString_start(_str_func))

    
    ml_templateHandles = self.msgList_get('templateHandles')
    ml_loftCurves = []
    for mHandle in ml_templateHandles:
        if mHandle.getMessage('loftCurve'):
            ml_loftCurves.append(mHandle.getMessage('loftCurve',asMeta=1)[0])
        ml_subShapers = mHandle.msgList_get('subShapers')
        if ml_subShapers:
            for mSub in ml_subShapers:
                if mSub.getMessage('loftCurve'):
                    ml_loftCurves.append(mSub.getMessage('loftCurve',asMeta=1)[0])
        
    if ml_templateHandles[-1].getMessage('pivotHelper'):
        mPivotHelper = ml_templateHandles[-1].pivotHelper
        log.debug("|{0}| >> pivot helper found ".format(_str_func))
    
        #make the foot geo....    
        mBaseCrv = mPivotHelper.doDuplicate(po=False)
        mBaseCrv.parent = False
        mShape2 = False
    
        for mChild in mBaseCrv.getChildren(asMeta=True):
            if mChild.cgmName == 'topLoft':
                mShape2 = mChild.doDuplicate(po=False)
                mShape2.parent = False
                ml_loftCurves.append(mShape2)
            mChild.delete()
            
        ml_loftCurves.append(mBaseCrv)
    """
    ml_newLoft = []
    for mCrv in ml_loftCurves:
        mCrv.doDuplicate(po=True)
        mCrv.p_parent = False
        ml_newLoft.append(mCrv)"""
    reload(BUILDUTILS)
    _mesh = BUILDUTILS.create_loftMesh([mCrv.mNode for mCrv in ml_loftCurves],
                                       name= 'test',
                                       divisions=1,
                                       form=2,
                                       degree=1)




    return ml_loftCurves


def get_module(self):
    _str_func = 'get_module'
    log.debug("|{0}| >>... ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mModuleTarget = self.getMessage('moduleTarget',asMeta=True)
    if not mModuleTarget:
        return log.error("|{0}| >> Must have moduleTarget for skining mode".format(_str_func))
    log.debug("|{0}| >> mModuleTarget: {1}".format(_str_func,mModuleTarget[0]))
    return mModuleTarget[0]

    
def get_puppet(self):
    _str_func = 'get_puppet'
    log.debug("|{0}| >>... ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))

    mModuleTarget = get_module(self)
    if cgmMeta.validateObjArg(mModuleTarget,'cgmRigPuppet',noneValid=True):
        return mModuleTarget
    
    mPuppet = mModuleTarget.getMessage('modulePuppet',asMeta=True)
    if not mPuppet:
        return log.error("|{0}| >> Must have puppet for skining mode".format(_str_func))
    log.debug("|{0}| >> mPuppet: {1}".format(_str_func,mPuppet[0]))
    return mPuppet[0]

def puppetMesh_delete(self):
    _str_func = 'puppetMesh_delete'
    log.debug("|{0}| >>... ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mPuppet = get_puppet(self)
    if not mPuppet:
        return log.error("|{0}| >> Must have puppet to check".format(_str_func))

    #Check for existance of mesh ========================================================================
    bfr = mPuppet.msgList_get('puppetMesh',asMeta=True)
    if bfr:
        log.debug("|{0}| >> puppetMesh detected...".format(_str_func))            
        mc.delete([mObj.mNode for mObj in bfr])
        return True
    return False

def puppetMesh_create(self,unified=True,skin=False, proxy = False, forceNew=True):
    try:
        _str_func = 'puppetMesh_create'
        log.debug("|{0}| >>  Unified: {1} | Skin: {2} ".format(_str_func,unified,skin)+ '-'*80)
        log.debug("{0}".format(self))
        
        mPuppet = False
        mParent = False
        if skin:
            mModuleTarget = self.getMessage('moduleTarget',asMeta=True)
            if not mModuleTarget:
                return log.error("|{0}| >> Must have moduleTarget for skining mode".format(_str_func))
            mModuleTarget = mModuleTarget[0]        
            
            mPuppet = puppet_get(self,mModuleTarget)
            if not mPuppet:
                return log.error("|{0}| >> Must have puppet for skining mode".format(_str_func))        
            """
            mPuppet = mModuleTarget.getMessageAsMeta('modulePuppet')
            if not mPuppet:
                mRoot = self.p_blockRoot
                if mRoot:
                    log.debug("|{0}| >>  Checking root for puppet: {1} ".format(_str_func,mRoot))
                    mPuppetTest = mRoot.getMessageAsMeta('moduleTarget')
                    log.debug("|{0}| >>  root target: {1} ".format(_str_func,mPuppetTest))
                    if mPuppetTest and mPuppetTest.mClass == 'cgmRigPuppet':
                        mPuppet = mPuppetTest
                    else:
                        mPuppet = False
                if not mPuppet:
                    return log.error("|{0}| >> Must have puppet for skining mode".format(_str_func))"""
                
            mGeoGroup = mPuppet.masterNull.geoGroup
            mParent = mGeoGroup
            log.debug("|{0}| >> mPuppet: {1}".format(_str_func,mPuppet))
            log.debug("|{0}| >> mGeoGroup: {1}".format(_str_func,mGeoGroup))        
            log.debug("|{0}| >> mModuleTarget: {1}".format(_str_func,mModuleTarget))
        
        
        if proxy:
            mPuppet = self.UTILS.get_puppet(self)
            if not mPuppet.masterControl.controlSettings.skeleton:
                log.warning("|{0}| >> Skeleton was off. proxy mesh in puppetMeshMode needs a visible skeleton to see. Feel free to turn it back off if you like.".format(_str_func, self.mNode))            
                mPuppet.masterControl.controlSettings.skeleton = 1        
        
        
        #Check for existance of mesh ========================================================================
        if mPuppet:
            bfr = mPuppet.msgList_get('puppetMesh',asMeta=True)
            if skin and bfr:
                log.debug("|{0}| >> puppetMesh detected...".format(_str_func))            
                if forceNew:
                    log.debug("|{0}| >> force new...".format(_str_func))                            
                    mc.delete([mObj.mNode for mObj in bfr])
                else:
                    return bfr
        
        if proxy:
            if unified:
                log.warning("|{0}| >> Proxy mode detected, unified option overridden".format(_str_func))            
                unified = False
            if skin:
                log.warning("|{0}| >> Proxy mode detected, skin option overridden".format(_str_func))
                skin = False
        
        #Process-------------------------------------------------------------------------------------
        if self.blockType == 'master':
            mRoot = self
        else:
            mRoot = self.getBlockParents()[-1]
        log.debug("|{0}| >> mRoot: {1}".format(_str_func,mRoot))
        ml_ordered = mRoot.getBlockChildrenAll()
        ml_mesh = []
        subSkin = False
        if skin:
            #if not unified:
            subSkin=True
                
        for mBlock in ml_ordered:
            if mBlock.blockType in ['master']:
                log.debug("|{0}| >> unmeshable: {1}".format(_str_func,mBlock))
                continue
            log.debug("|{0}| >> Meshing... {1}".format(_str_func,mBlock))
            
            if proxy:
                ml_mesh.extend(mBlock.verify_proxyMesh(puppetMeshMode=True))
            else:
                ml_mesh.extend(create_simpleMesh(mBlock,skin=subSkin,forceNew=subSkin))
            
            """
            if skin:
                mModuleTarget = mBlock.getMessage('moduleTarget',asMeta=True)
                if not mModuleTarget:
                    return log.error("|{0}| >> Must have moduleTarget for skining mode".format(_str_func))
                mModuleTarget = mModuleTarget[0]
                mModuleTarget.atUtils('rig_connect')
                ml_joints = mModuleTarget.rigNull.msgList_get('moduleJoints')
                if not ml_joints:
                    return log.error("|{0}| >> Must have moduleJoints for skining mode".format(_str_func))
                ml_moduleJoints.extend(ml_joints)"""
            
        if unified:
            if skin:
                #self.msgList_connect('simpleMesh',ml_mesh)
                for mObj in ml_mesh:
                    TRANS.pivots_zeroTransform(mObj)
                    mObj.dagLock(False)
                    mObj.p_parent = False
                #Have to dup and copy weights because the geo group isn't always world center
                if len(ml_mesh)>1:
                    mMesh = cgmMeta.validateObjListArg(mc.polyUniteSkinned([mObj.mNode for mObj in ml_mesh],ch=0))
                    mMesh = mMesh[0]
                else:
                    mMesh = ml_mesh[0]
                
                mMesh.dagLock(False)
                
                #mMeshBase = mMeshBase[0]
                #mMesh = mMeshBase.doDuplicate(po=False,ic=False)
                mMesh.rename('{0}_unified_geo'.format(mPuppet.p_nameBase))
                mMesh.p_parent = mParent
                cgmGEN.func_snapShot(vars())
                
                #now copy weights
                #CORESKIN.transfer_fromTo(mMeshBase.mNode, [mMesh.mNode])
                #mMeshBase.delete()
                
                ml_mesh = [mMesh]
                #ml_mesh[0].p_parent = mGeoGroup
                mMesh.dagLock(True)
                
                """
                log.debug("|{0}| >> skinning..".format(_str_func))
                for mMesh in ml_mesh:
                    log.debug("|{0}| >> skinning {1}".format(_str_func,mMesh))
                    mMesh.p_parent = mGeoGroup
                    skin = mc.skinCluster ([mJnt.mNode for mJnt in ml_moduleJoints],
                                           mMesh.mNode,
                                           tsb=True,
                                           bm=0,
                                           wd=0,
                                           heatmapFalloff = 1.0,
                                           maximumInfluences = 2,
                                           normalizeWeights = 1, dropoffRate=10.0)
                    skin = mc.rename(skin,'{0}_skinCluster'.format(mMesh.p_nameBase))        """
            else:
                if len(ml_mesh)>1:
                    ml_mesh = cgmMeta.validateObjListArg(mc.polyUnite([mObj.mNode for mObj in ml_mesh],ch=False))
                
            ml_mesh[0].rename('{0}_unified_geo'.format(mRoot.p_nameBase))
            
        if skin or proxy:
            mPuppet.msgList_connect('puppetMesh',ml_mesh)
            
        for mGeo in ml_mesh:
            CORERIG.color_mesh(mGeo.mNode,'puppetmesh')
            
        return ml_mesh
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
            
    

def create_simpleMesh(self, forceNew = True, skin = False,connect=True,deleteHistory=False):
    """
    Main call for creating a skinned or single mesh from a rigBlock
    """
    _str_func = 'create_simpleMesh'
    log.debug("|{0}| >>  forceNew: {1} | skin: {2} ".format(_str_func,forceNew,skin)+ '-'*80)
    log.debug("{0}".format(self))
    
    mParent = False
    #Check for existance of mesh ========================================================================
    if connect:
        bfr = self.msgList_get('simpleMesh',asMeta=True)
        if skin and bfr:
            log.debug("|{0}| >> simpleMesh detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in bfr])
            else:
                return bfr
    if skin:
        mModuleTarget = self.getMessageAsMeta('moduleTarget')
        if not mModuleTarget:
            return log.error("|{0}| >> Must have moduleTarget for skining mode".format(_str_func))        
        mPuppet = puppet_get(self,mModuleTarget)
        if not mPuppet:
            return log.error("|{0}| >> Must have puppet for skining mode".format(_str_func))
        mGeoGroup = mPuppet.masterNull.geoGroup
        mParent = mGeoGroup
        log.debug("|{0}| >> mPuppet: {1}".format(_str_func,mPuppet))
        log.debug("|{0}| >> mGeoGroup: {1}".format(_str_func,mGeoGroup))        
        log.debug("|{0}| >> mModuleTarget: {1}".format(_str_func,mModuleTarget))
            
    #BlockModule call? ====================================================================================
    mBlockModule = self.p_blockModule
    if mBlockModule.__dict__.has_key('create_simpleMesh'):
        log.debug("|{0}| >> BlockModule 'create_simpleMesh' call found...".format(_str_func))            
        ml_mesh = mBlockModule.create_simpleMesh(self,skin=skin,parent=mParent)
    
    else:#Create ======================================================================================
        ml_mesh = create_simpleLoftMesh(self,form=2,degree=None,divisions=2,deleteHistory=deleteHistory)
    
        
        #Get if skin data -------------------------------------------------------------------------------
        if skin:
            log.debug("|{0}| >> skinnable? ...".format(_str_func))        
            ml_moduleJoints = mModuleTarget.rigNull.msgList_get('moduleJoints')
            if not ml_moduleJoints:
                return log.error("|{0}| >> Must have moduleJoints for skining mode".format(_str_func))
            log.debug("|{0}| >> ml_moduleJoints: {1}".format(_str_func,ml_moduleJoints))        

            md_parents = {}#We're going to un parent our joints before skinning and then reparent
            for i,mJnt in enumerate(ml_moduleJoints):
                md_parents[mJnt] = mJnt.getParent(asMeta=True)
                if i:mJnt.p_parent = ml_moduleJoints[i-1]
        

            log.debug("|{0}| >> skinning..".format(_str_func))
            l_joints= [mJnt.mNode for mJnt in ml_moduleJoints]
            for mMesh in ml_mesh:
                log.debug("|{0}| >> skinning {1}".format(_str_func,mMesh))
                mMesh.p_parent = mParent
                #mMesh.doCopyPivot(mGeoGroup.mNode)
                skin = mc.skinCluster (l_joints,
                                       mMesh.mNode,
                                       tsb=True,
                                       bm=1,
                                       maximumInfluences = 2,
                                       normalizeWeights = 1,dropoffRate=10.0)
                """ 
                skin = mc.skinCluster ([mJnt.mNode for mJnt in ml_moduleJoints],
                                       mMesh.mNode,
                                       tsb=True,
                                       bm=0,
                                       wd=0,
                                       heatmapFalloff = 1.0,
                                       maximumInfluences = 2,
                                       normalizeWeights = 1, dropoffRate=10)"""
                skin = mc.rename(skin,'{0}_skinCluster'.format(mMesh.p_nameBase))
            
            #Reparent
            for i,mJnt in enumerate(ml_moduleJoints):
                mJnt.p_parent = md_parents[mJnt]
            #pprint.pprint(md_parents)
    if connect:
        self.msgList_connect('simpleMesh',ml_mesh)        
    return ml_mesh
            

def create_simpleLoftMesh(self, form = 2, degree=None, uSplit = None,vSplit=None,cap=True,
                          deleteHistory = True,divisions=None):
    """
    form
    0 - count
    1 - fit
    2 - general
    3 - cvs
    
    """
    _str_func = 'create_simpleLoftMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))


    mBlockModule = self.p_blockModule

    ml_delete = []
    ml_templateHandles = self.msgList_get('templateHandles')
    ml_loftCurves = []
    
    if degree == None:
        degree = 1 + self.loftDegree
        if degree ==1:
            form = 3
    if vSplit == None:
        vSplit = self.loftSides
    if uSplit == None:
        uSplit = self.loftSplit-1
        
    for mHandle in ml_templateHandles:
        if mHandle.getMessage('loftCurve'):
            ml_loftCurves.append(mHandle.getMessage('loftCurve',asMeta=1)[0])
        ml_subShapers = mHandle.msgList_get('subShapers')
        if ml_subShapers:
            for mSub in ml_subShapers:
                if mSub.getMessage('loftCurve'):
                    ml_loftCurves.append(mSub.getMessage('loftCurve',asMeta=1)[0])
        
    if ml_templateHandles[-1].getMessage('pivotHelper') and self.blockProfile not in ['arm']:
        mPivotHelper = ml_templateHandles[-1].pivotHelper
        log.debug("|{0}| >> pivot helper found ".format(_str_func))
    
        #make the foot geo....    
        mBaseCrv = mPivotHelper.doDuplicate(po=False)
        mBaseCrv.parent = False
        mShape2 = False
        ml_delete.append(mBaseCrv)
        for mChild in mBaseCrv.getChildren(asMeta=True):
            if mChild.cgmName == 'topLoft':
                mShape2 = mChild.doDuplicate(po=False)
                mShape2.parent = False
                ml_loftCurves.append(mShape2)
                ml_delete.append(mShape2)                
            mChild.delete()
            
        ml_loftCurves.append(mBaseCrv)
    
    reload(BUILDUTILS)
    _mesh = BUILDUTILS.create_loftMesh([mCrv.mNode for mCrv in ml_loftCurves],
                                       uSplit=uSplit,
                                       vSplit=vSplit,
                                       cap = cap,
                                       form=form,
                                       deleteHistory=deleteHistory,
                                       degree=degree)
    
    """
    if form in [1,2]:
        mc.polyNormal(_mesh,nm=0)    
    if form == 3 and degree ==1:
        mc.polyNormal(_mesh,nm=0)    """
        
    
    _mesh = mc.rename(_mesh,'{0}_0_geo'.format(self.p_nameBase))
    
    if deleteHistory:
        log.debug("|{0}| >> delete history...".format(_str_func))        
        mc.delete(_mesh, ch=True)
        if ml_delete:mc.delete([mObj.mNode for mObj in ml_delete])
    
    return cgmMeta.validateObjListArg(_mesh,'cgmObject',setClass=True)


    ml_shapes = []
    
    mMesh_tmp =  get_castMesh(self)
    str_meshShape = mMesh_tmp.getShapes()[0]
    
    _l_targets = ATTR.msgList_get(self.mNode,'loftTargets')


    mc.select(cl=True)
    log.debug("|{0}| >> loftTargets: {1}".format(_str_func,_l_targets))

    #>>Body -----------------------------------------------------------------
    _res_body = mc.loft(_l_targets, o = True, d = degree, po = 1 )

    _inputs = mc.listHistory(_res_body[0],pruneDagObjects=True)
    _tessellate = _inputs[0]

    _d = {'format':2,#General
          'polygonType':1,#'quads',
          'uNumber': 1 + jointCount}
    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)

    #>>Top/Bottom bottom -----------------------------------------------------------------
    if cap:
        _l_combine = [_res_body[0]]        
        for crv in _l_targets[0],_l_targets[-1]:
            _res = mc.planarSrf(crv,po=1)
            _inputs = mc.listHistory(_res[0],pruneDagObjects=True)
            _tessellate = _inputs[0]        
            _d = {'format':2,#General
                  'polygonType':1,#'quads',
                  'vNumber':1,
                  'uNumber':1}
            for a,v in _d.iteritems():
                ATTR.set(_tessellate,a,v)
            _l_combine.append(_res[0])

        _res = mc.polyUnite(_l_combine,ch=False,mergeUVSets=1,n = "{0}_proxy_geo".format(root))
        if merge:
            mc.polyMergeVertex(_res[0], d= .01, ch = 0, am = 1 )
            #polyMergeVertex  -d 0.01 -am 1 -ch 1 box_3_proxy_geo;
        mc.polySetToFaceNormal(_res[0],setUserNormal = True) 
    else:
        _res = _res_body
    return _res[0]
    
    
    
    
    return 
    l_uIsos = SURF.get_dat(str_meshShape, uKnots=True)['uKnots']
    log.debug("|{0}| >> Isoparms U: {1}".format(_str_func,l_uIsos))
    
    #Process ----------------------------------------------------------------------------------
    l_newCurves = []
    d_curves = {}
    
    def getCurve(uValue,l_curves):
        _crv = d_curves.get(uValue)
        if _crv:return _crv
        _crv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,uValue), ch = 0, rn = 0, local = 0)[0]
        mCrv = cgmMeta.asMeta(_crv)
        mCrv.p_parent=False
        d_curves[uValue] = mCrv
        log.debug("|{0}| >> created: {1} ...".format(_str_func,_crv))        
        l_curves.append(mCrv)
        return mCrv
    
    for uValue in l_uIsos:
        mCrv = getCurve(uValue,l_newCurves)
        

def create_defineCurve(self,d_definitions,md_handles, mParentNull = None):
    try:
        _short = self.p_nameShort
        _str_func = 'create_defineCurve'
        log.debug("|{0}| >>...".format(_str_func)+ '-'*80)
        log.debug(self)
        
        md_defineCurves = {}
        ml_defineCurves =[]
        
        if mParentNull == None:
            mParentNull = self.atUtils('stateNull_verify','define')
            
        mHandleFactory = self.asHandleFactory()
        for k in d_definitions.keys():
            log.debug("|{0}| >>  curve: {1}...".format(_str_func,k))            
            _dtmp = d_definitions[k]
            
            str_name = _dtmp.get('name') or "{0}_{1}".format(self.blockProfile,k)
            _tagOnly = _dtmp.get('tagOnly',False)
            _handleKeys = _dtmp.get('keys')
            
            ml_handles = [md_handles[k2] for k2 in _handleKeys]
        
            l_pos = []
            for mHandle in ml_handles:
                l_pos.append(mHandle.p_position)
        
            _crv = mc.curve(d=1,p=l_pos)
            #CORERIG.create_at(create='curve',l_pos = l_pos)
            mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
            mCrv.p_parent = mParentNull
            
            _color = _dtmp.get('color')
            if _color:
                CORERIG.override_color(mCrv.mNode, _color)
            else:
                mHandleFactory.color(mCrv.mNode)
                
            mCrv.rename('{0}_defineCurve'.format(k))
            mCrv.doStore('handleTag',k,attrType='string')
            #mCrv.v=False
            #md_loftCurves[tag] = mCrv
        
            self.connectChildNode(mCrv, k+'DefineCurve','block')
            ml_defineCurves.append(mCrv)
            md_defineCurves[k] = mCrv
        
            l_clusters = []
            for i,cv in enumerate(mCrv.getComponents('cv')):
                _res = mc.cluster(cv, n = 'test_{0}_{1}_pre_cluster'.format(ml_handles[i].p_nameBase,i))
                TRANS.parent_set( _res[1], ml_handles[i].mNode)
                l_clusters.append(_res)
                ATTR.set(_res[1],'visibility',False)
                
            if _dtmp.get('rebuild'):
                _node = mc.rebuildCurve(mCrv.mNode, d=3, keepControlPoints=False,
                                        ch=1,s=len(ml_handles),
                                        n="{0}_reparamRebuild".format(mCrv.p_nameBase))
                mc.rename(_node[1],"{0}_reparamRebuild".format(mCrv.p_nameBase))
                
            mCrv.dagLock()
        return {'md_curves':md_defineCurves,
                'ml_curves':ml_defineCurves}
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    finally:pass

def create_define_rotatePlane(self, md_handles,md_vector,mStartParent=None):
    try:
        _str_func = 'create_define_rotatePlane'        
        _side = self.UTILS.get_side(self)
        mDefineNull = self.defineNull
        #Make our curves...
        vector_pos = md_vector['rp'].getAxisVector('y+',asEuclid = 0)
        vector_neg = md_vector['rp'].getAxisVector('y-',asEuclid = 0)        
        
        if mStartParent:
            mStart = mStartParent
        else:mStart = self
        mEnd = md_handles['end']
    
    
        #Setup Loft curves and plane ----------------------------------------------------------------
        log.debug("|{0}| >> Setup curves...".format(_str_func))                     
    
        l_crvs = []
        ml_crvs = []
        
        for i,mObj in enumerate([mStart,mEnd]):
            crv =   mc.curve (d=1, ep = [DIST.get_pos_by_vec_dist([0,0,0], [1,0,0], .5),
                                         DIST.get_pos_by_vec_dist([0,0,0], [-1,0,0], .5)],
                                   os=True)
            log.debug("|{0}| >> Created: {1}".format(_str_func,crv))
            
            mCrv = cgmMeta.validateObjArg(crv,setClass=True)#mObj.doCreateAt()
            #CORERIG.shapeParent_in_place(mCrv.mNode,crv,False)
            ml_crvs.append(mCrv)
            
            
            if mObj == mStart:
                mTarget = mEnd
                _aim = [0,0,1]
                _tag = 'start'
            else:
                mTarget = mStart
                _aim = [0,0,-1]
                _tag = 'end'
                
            mc.pointConstraint(mObj.mNode, mCrv.mNode,maintainOffset = False)
            mc.aimConstraint(mTarget.mNode, mCrv.mNode, maintainOffset = False,
                                 aimVector = _aim, upVector = [1,0,0], 
                                 worldUpObject = md_vector['rp'].mNode,
                                 worldUpType = 'objectRotation', 
                                 worldUpVector = [0,1,0])
            
            mCrv.addAttr('cgmName',_tag)
            mCrv.addAttr('cgmType','rpLoft')
            mCrv.doName()
            
            mCrv.p_parent = mDefineNull
            
            #mEnd.doConnectOut('height', "{0}.scaleX".format(mCrv.mNode))
            #mEnd.doConnectOut('height', "{0}.scaleY".format(mCrv.mNode))
            mCrv.scaleX = mEnd.height
            mCrv.scaleY = mEnd.height
            mc.scaleConstraint(mEnd.mNode, mCrv.mNode)
            
            mCrv.v=False
            
        _res_body = mc.loft([mCrv.mNode for mCrv in ml_crvs], o = True, d = 1, po = 1 )
        _inputs = mc.listHistory(_res_body[0],pruneDagObjects=True)
        _tessellate = _inputs[0]
        
        _d = {'format':2,#General
              'polygonType':1,#'quads'
              }
              
        for a,v in _d.iteritems():
            ATTR.set(_tessellate,a,v)
        
        mPlane = cgmMeta.validateObjArg(_res_body[0])
        mPlane.doStore('cgmName', self)
        mPlane.doStore('cgmType','rotatePlaneVisualize')
        mPlane.doName()
        
        mPlane.p_parent = mDefineNull
        mPlane.resetAttrs()
        
        mPlane.inheritsTransform = 0
        for s in mPlane.getShapes(asMeta=True):
            s.overrideDisplayType = 2
            
        CORERIG.colorControl(mPlane.mNode,_side,'sub',transparent = True)
        self.doConnectOut('visRotatePlane',"{0}.visibility".format(mPlane.mNode))
        #mHandleFactory.color(mPlane.mNode,controlType='sub',transparent=False)
        mPlane.dagLock()
        #Aim them...
        #Make our loft...
        return mPlane
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())

def create_defineHandles(self,l_order,d_definitions,baseSize,mParentNull = None, mScaleSpace = None, rotVecControl = False,blockUpVector = [0,1,0], vecControlLiveScale = False, vectorScaleAttr = 'baseSize'):
    try:
        _short = self.p_nameShort
        _str_func = 'create_defineHandles'
        log.debug("|{0}| >>...".format(_str_func)+ '-'*80)
        log.debug(self)
        
        md_handles = {}
        ml_handles = []
        md_vector = {}
        md_jointLabels = {}
        
        _size = baseSize
        _sizeSub = _size / 4
        _offset = _size * 2
        
        if mParentNull == None:
            mParentNull = self.atUtils('stateNull_verify','define')
        mHandleFactory = self.asHandleFactory()
        
        for k in l_order:
            
            _dtmp = d_definitions.get(k,False)
            if not _dtmp:
                log.error("|{0}| >> handle: {1} has no dict. Bailing".format(_str_func,k))
                continue
            
            log.debug("|{0}| >> handle: {1} ...".format(_str_func,k))
            if k in ['end','start','lever']:
                _useSize = 1.0
            else:
                _useSize = _sizeSub
            
            str_name = _dtmp.get('name') or "{0}_{1}".format(self.blockProfile,k)
            _tagOnly = _dtmp.get('tagOnly',False)
            _pos = _dtmp.get('pos',False)
            mEnd = md_handles.get(_dtmp.get('endTag')) or md_handles.get('end')
            
            #sphere
            if k in ['up','rp'] or _dtmp.get('handleType') == 'vector':# and rotVecControl:
                #if not vecControlLiveScale:
                #    _rotSize = [.25,.25,2.0]
                #    if k == 'rp':_rotSize = [.5,.5,1.25]
                #else:
                _rotSize = [.05,.05,.8]
                if k == 'rp':_rotSize = [.105,.105,.6]                    
                    
                _crv = CURVES.create_fromName(name='cylinder',#'arrowsAxis', 
                                              direction = 'y+', size = _rotSize)                
                #_crv = CORERIG.create_at(create='curveLinear', 
                #                         l_pos=[[0,0,0],[0,1.25,0]], 
                #                         baseName='up')
            
                mHandle = cgmMeta.validateObjArg(_crv)
                mHandle.p_parent = mParentNull
                mHandle.resetAttrs()
                            
                mHandle.doStore('mClass','cgmObject')            
                
                #if k not in ['end','star']:
                mHandle.addAttr('cgmColorLock',True,lock=True,hidden=True)
                    
                if _tagOnly:
                    mHandle.doStore('cgmName',k)
                else:
                    mHandle.doStore('cgmName',self)
                    mHandle.doStore('cgmTypeModifier',str_name)
                mHandle.doStore('cgmType','defineHandle')
                mHandle.doName()
                mHandle.doStore('handleTag',k,attrType='string')
                mHandle.doStore('handleType','vector')            
                
                SNAP.aim_atPoint(mEnd.p_position, 'z+')
            
                #mc.aimConstraint(mHandle.mNode, mAim.mNode, maintainOffset = False,
                                 #aimVector = [0,0,1], upVector = [0,0,0], 
                                 #worldUpType = 'none')
                                 
                self.connectChildNode(mHandle.mNode,'vector{0}Helper'.format(STR.capFirst(k)),'block')
                md_vector[k] = mHandle
                """
                _arrow = CURVES.create_fromName(name='arrowForm',#'arrowsAxis', 
                                                direction = 'z+', size = _sizeSub)
            
                mArrow = cgmMeta.cgmObject(_arrow)
                mArrow.p_parent = mParent
                mArrow.resetAttrs()
                mArrow.ty = _size*2
            
                SNAP.aim_atPoint(mArrow.mNode,mHandle.p_position, 'z-')
                
                CORERIG.shapeParent_in_place(mHandle.mNode,mArrow.mNode,False)"""
                
                CORERIG.override_color(mHandle.mNode, _dtmp['color'])
                
            else:
                if k == 'aim':
                    _shape = 'eye'
                else:
                    _shape = 'sphere'
                _crv = CURVES.create_fromName(name=_shape,#'arrowsAxis', 
                                              direction = 'z+', size = _useSize)
                #CORERIG.shapeParent_in_place(_crv,_circle,False)
            
                #_crv = CURVES.create_fromName(name='sphere',#'arrowsAxis', 
                #                              direction = 'z+', size = _sizeSub)
                mHandle = cgmMeta.validateObjArg(_crv,'cgmControl',setClass = True)
                mHandle.p_parent = mParentNull
                mHandle.doSnapTo(self.mNode)
                CORERIG.override_color(_crv, _dtmp['color'])
            
                if k not in ['end','start']:
                    mHandle.addAttr('cgmColorLock',True,lock=True,hidden=True)
                    
                if _tagOnly:
                    mHandle.doStore('cgmName',k)
                else:
                    mHandle.doStore('cgmName',self)
                    mHandle.doStore('cgmTypeModifier',str_name)
                mHandle.doStore('cgmType','defineHandle')
                mHandle.doName()
                mHandle.doStore('handleTag',k,attrType='string')
            
                mHandle.resetAttrs()
            
                #Move for initial aim ----------------------------------------------------------------------
                ATTR.set(mHandle.mNode,'tz', _size * 5)
                """
                        mc.aimConstraint(self.mNode, mHandle.mNode, maintainOffset = False,
                                         aimVector = [0,0,-1], upVector = [0,1,0], 
                                         worldUpObject = self.mNode,
                                         worldUpType = 'object', 
                                         worldUpVector = [0,1,0])"""
            
                if mScaleSpace and _dtmp.get('scaleSpace'):
                    mLoc = mHandle.doLoc()
                    mLoc.p_parent = mScaleSpace
                    
                    mLoc.translate = [v*.5 for v in _dtmp['scaleSpace']]
                    mHandle.p_position = mLoc.p_position
                    mLoc.delete()
                elif _pos:
                    mHandle.p_position = _pos
                else:
                    mHandle.resetAttrs('translate')
                    
                for a,v in _dtmp.get('defaults',{}).iteritems():
                    if issubclass(type(v),list):
                        ATTR.set(mHandle.mNode, a, v)
                    else:
                        ATTR.set(mHandle.mNode, a, _offset * v)
        
            md_handles[k] = mHandle
            ml_handles.append(mHandle)        
        
            _trackTag = _dtmp.get('parentTag',False)
            if _trackTag:
                mParent = md_handles[_trackTag]
            else:
                mParent = mParentNull
            
                        
                        
            if k == 'lever':#Arrow ---------------------------------------------
                _arrow = CURVES.create_fromName(name='arrowForm',#'arrowsAxis', 
                                                direction = 'y+', size = _size)
                CORERIG.override_color(_arrow, _dtmp['color'])
            
                mArrow = cgmMeta.cgmObject(_arrow)
                mArrow.p_parent = mHandle
                mArrow.resetAttrs()
                mArrow.ty = _size * 3
                
                CORERIG.shapeParent_in_place(mHandle.mNode,mArrow.mNode,False)
 
            #Helper --------------------------------------------------------------------------------
            if _dtmp.get('vectorLine') !=False:
                if rotVecControl and k in ['up','rp']:pass
                elif k in ['start']:pass
                else:
                    _crv = CORERIG.create_at(create='curveLinear', 
                                             l_pos=[[0,0,0],[0,0,_size / 2.0]], 
                                             baseName='end')
                
                    CORERIG.override_color(_crv, _dtmp['color'])
                    mAim = cgmMeta.validateObjArg(_crv)
                    mAim.p_parent = mParent
                    mAim.resetAttrs()
                
                    mAim.doStore('mClass','cgmObject')            
                    mAim.doStore('cgmName',self)
                    mAim.doStore('cgmTypeModifier',str_name)
                    mAim.doStore('cgmType','aimLine')
                    mAim.doName()            
                
                    mc.aimConstraint(mHandle.mNode, mAim.mNode, maintainOffset = False,
                                     aimVector = [0,1,0], upVector = [0,0,0], 
                                     worldUpType = 'none')
                
                    for mShape in mAim.getShapes(asMeta=1):
                        mShape.overrideEnabled = 1
                        mShape.overrideDisplayType = 2
                
                    mAim.dagLock(True)
        
                
            if _dtmp.get('arrow') !=False:#Arrow ---------------------------------------------
                if rotVecControl and k in ['up','rp']:pass
                elif k in ['start']:pass                
                else:                
                    _arrow = CURVES.create_fromName(name='arrowForm',#'arrowsAxis', 
                                                    direction = 'z+', size = _sizeSub)
                    CORERIG.override_color(_arrow, _dtmp['color'])
                
                    mArrow = cgmMeta.cgmObject(_arrow)
                    mArrow.p_parent = mParent
                    mArrow.resetAttrs()
                    mArrow.tz = _sizeSub * 3.0
                    
                    CORERIG.copy_pivot(mArrow.mNode,mParent.mNode)
                
                    mc.aimConstraint(mHandle.mNode, mArrow.mNode, maintainOffset = False,
                                     aimVector = [0,0,1], upVector = [0,0,0], 
                                     worldUpType = 'none')
                
                    mArrow.doStore('mClass','cgmObject')            
                    mArrow.doStore('cgmName',self)
                    mArrow.doStore('cgmTypeModifier',str_name)
                    mArrow.doStore('cgmType','vectorHelper')
                    mArrow.doName()
                
                    mArrow.dagLock()
                
                    md_vector[k] = mArrow
                    self.connectChildNode(mArrow.mNode,'vector{0}Helper'.format(STR.capFirst(k)),'block')
                    
                    for mShape in mArrow.getShapes(True):
                        mShape.overrideEnabled = 1
                        mShape.overrideDisplayType = 2
            
            if _dtmp.get('jointLabel') !=False:#Joint Label-----------------------------------------------------------------
                if _tagOnly:
                    labelName = k
                else:
                    labelName = str_name
                mJointLabel = mHandleFactory.addJointLabel(mHandle,labelName)
                md_jointLabels[k] = mJointLabel
        
        
            self.connectChildNode(mHandle.mNode,'define{0}Helper'.format(STR.capFirst(k)),'block')
        
        
        self.msgList_connect('defineHandles', ml_handles)
        
        #Parent the tags
        for k in l_order:
            _dtmp = d_definitions.get(k,{})
            _trackTag = _dtmp.get('parentTag',False)
            if _trackTag:
                mc.pointConstraint(md_handles[_trackTag].mNode,  md_handles[k].mNode, maintainOffset = False)

        
        
        #Parent Up to aim ---------------------------------------------
        """
        if md_handles.get('up') and md_vector.get('end'):
            log.debug("|{0}| >> Up track to end...".format(_str_func))            
            mFollowGroup =  md_handles['up'].doGroup(True,True,asMeta=True,typeModifier = 'follow')
            #mFollowGroup.p_parent = md_vector['end']            
            mUpTrack = md_handles['up'].doCreateAt()
            mUpTrack.p_parent = md_vector['end']
            mc.pointConstraint(mUpTrack.mNode,mFollowGroup.mNode,maintainOffset=True)
            mFollowGroup.dagLock()
            mUpTrack.dagLock()"""
    
        """
        if md_handles.get('rp') and md_vector.get('rp'):
            mFollowGroup =  md_handles['rp'].doGroup(True,True,asMeta=True,typeModifier = 'follow')
            mFollowGroup.p_parent = md_vector['end']"""
    
            #mFollowGroup =  md_handles['rp'].doGroup(True,True,asMeta=True,typeModifier = 'follow')
            #mRPTrack = md_handles['rp'].doCreateAt()
            #mRPTrack.p_parent = md_vector['end']
            #mc.pointConstraint(mRPTrack.mNode,mFollowGroup.mNode,maintainOffset=True)
            #mFollowGroup.dagLock()
            #mRPTrack.dagLock()            
    
        #If end -----------------------
        if md_handles.get('end'):
            mHandleFactory.color(md_handles['end'].mNode)
            mHandleFactory.color(md_jointLabels['end'].mNode)
    
    
            mEndAimLoc = self.doCreateAt()
            mEndAimLoc.p_parent = md_vector['end']
            mEndAimLoc.resetAttrs()
            ATTR.set(mEndAimLoc.mNode,'tz',-2)
            mEndAimLoc.dagLock()
            
            #SNAP.aim_atPoint(md_handles['end'].mNode,self.p_position,'z-')
            #aim
            if rotVecControl:
                mc.aimConstraint(self.mNode, md_handles.get('end').mNode, maintainOffset = False,
                                aimVector = [0,0,-1], upVector = [0,1,0], 
                                worldUpObject = self.mNode,
                                worldUpType = 'objectRotation', 
                                worldUpVector = blockUpVector)
            else:
                mc.aimConstraint(self.mNode, md_handles.get('end').mNode, maintainOffset = False,
                                 aimVector = [0,0,-1], upVector = [0,1,0], 
                                 worldUpObject = md_vector.get('up').mNode,
                                 worldUpType = 'objectRotation', 
                                 worldUpVector = [0,1,0])
                
        if  md_handles.get('start'):
            mc.aimConstraint(md_handles.get('end').mNode, md_handles.get('start').mNode, maintainOffset = False,
                             aimVector = [0,0,-1], upVector = [0,1,0], 
                             worldUpObject = md_vector.get('up').mNode,
                             worldUpType = 'objectRotation', 
                             worldUpVector = [0,1,0])            

        for k,dTmp in d_definitions.iteritems():
            if dTmp.get('handleType') == 'vector':
                if md_handles.get(k):
                    ATTR.set_standardFlags(md_handles[k].mNode,['tx','ty','tz','sx','sy','sz'])
                    

        if rotVecControl:
            for k in 'rp','up':
                if md_handles.get(k):
                    ATTR.set_standardFlags(md_handles[k].mNode,['tx','ty','tz','sx','sy','sz'])
                    
        if md_handles.get('end'):
            _rotUpType = 'object'
            if rotVecControl:
                _rotUpType = 'objectRotation'
            #BaseSizeHandle -------------------------------------------------
            _crv = CURVES.create_fromName(name='square',#'arrowsAxis', 
                                          direction = 'z+', size = 1.0)
        
            mBaseSizeHandle = cgmMeta.validateObjArg(_crv,'cgmObject',setClass = True)
            mBaseSizeHandle.p_parent = mParentNull
            mBaseSizeHandle.resetAttrs()
            mBaseSizeHandle.v = False
            
            mc.aimConstraint(md_handles['end'].mNode, mBaseSizeHandle.mNode, maintainOffset = False,
                             aimVector = [0,0,1], upVector = [0,1,0], 
                             worldUpObject = md_handles['up'].mNode,
                             worldUpType = _rotUpType, 
                             worldUpVector = [0,1,0])
            #md_handles['end'].doConnectOut('scale', "{0}.scale".format(mBaseSizeHandle.mNode))
            md_handles['end'].doConnectOut('scaleX', "{0}.scaleX".format(mBaseSizeHandle.mNode))
            md_handles['end'].doConnectOut('scaleY', "{0}.scaleY".format(mBaseSizeHandle.mNode))            
        
            mBaseSizeHandle.doStore('cgmName',self)
            mBaseSizeHandle.doStore('cgmTypeModifier',k)
            mBaseSizeHandle.doStore('cgmType','baseSizeBase')
            mBaseSizeHandle.doName()
            
            if md_handles.get('start'):
                mc.pointConstraint(md_handles['start'].mNode, mBaseSizeHandle.mNode,maintainOffset=False)
                
        
            mBaseSizeHandle.dagLock()
        
            #AimLoftHandle --------------------------------------------------
            _crv = CURVES.create_fromName(name='square',#'arrowsAxis', 
                                          direction = 'z+', size = 1.0)
        
            mEndSizeHandle = cgmMeta.validateObjArg(_crv,'cgmObject',setClass = True)
            mEndSizeHandle.p_parent = mParentNull
            mEndSizeHandle.resetAttrs()
            mEndSizeHandle.v = False
        
            mc.pointConstraint(md_handles['end'].mNode, mEndSizeHandle.mNode,maintainOffset=False)
            md_handles['end'].doConnectOut('scaleX', "{0}.scaleX".format(mEndSizeHandle.mNode))
            md_handles['end'].doConnectOut('scaleY', "{0}.scaleY".format(mEndSizeHandle.mNode))
        
            mc.aimConstraint(mEndAimLoc.mNode, mEndSizeHandle.mNode, maintainOffset = False,
                             aimVector = [0,0,-1], upVector = [0,1,0], 
                             worldUpObject = md_handles['up'].mNode,
                             worldUpType = _rotUpType, 
                             worldUpVector = [0,1,0])
        
            mEndSizeHandle.doStore('cgmName',self)
            mEndSizeHandle.doStore('cgmTypeModifier',k)
            mEndSizeHandle.doStore('cgmType','endSizeBase')
            mEndSizeHandle.doName()                    
        
            mEndSizeHandle.dagLock()
        
            #measure height/width ----------------------------------------------------------------
            d_measure = {'height':'ty',
                         'width':'tx',
                         'length':'tz'}
            md_measure = {}
            for k,d in d_measure.iteritems():
                md_measure[k] = {}
                if k == 'length':
                    mPos =mEndSizeHandle.doLoc()
                    mNeg = mBaseSizeHandle.doLoc()
                    
                    mPos.p_parent = mEndSizeHandle
                    mNeg.p_parent = mBaseSizeHandle
                    
                else:
                    mPos = mEndSizeHandle.doLoc()
                    mNeg = mEndSizeHandle.doLoc()
            
                    for mObj in mPos,mNeg:
                        mObj.p_parent = mEndSizeHandle
            
                    ATTR.set(mPos.mNode,d,.5)
                    ATTR.set(mNeg.mNode,d,-.5)
                    
                mPos.rename("{0}_{1}_pos_loc".format(self.p_nameBase,k))
                mNeg.rename("{0}_{1}_neg_loc".format(self.p_nameBase,k))
                
                for mObj in mPos,mNeg:
                    mObj.v=False
                    mObj.dagLock()
        
                buffer =  RIGCREATE.distanceMeasure(mPos.mNode,mNeg.mNode,
                                                    baseName="{0}_{1}".format(self.p_nameBase,k))
                buffer['mDag'].p_parent = mParentNull
                ATTR.copy_to(buffer['mShape'].mNode,'distance',md_handles['end'].mNode,k,driven='target')
                ATTR.set_standardFlags(md_handles['end'].mNode,
                                       attrs=[k],visible=True,keyable=False,lock=True)
        
                buffer['mShape'].overrideEnabled = 1
                buffer['mShape'].overrideDisplayType = 2
                md_measure[k]['Dag'] = buffer['mDag']
                md_measure[k]['mShape'] = buffer['mDag']
                
                ATTR.connect("{0}.visMeasure".format(_short), "{0}.visibility".format(buffer['mDag'].mNode))
                #mHandleFactory.color(buffer['mShape'].mNode,controlType='sub')
        
        
        
            # Loft ==============================================================================
            targets = [mEndSizeHandle.mNode, mBaseSizeHandle.mNode]
            
            create_defineLoftMesh(self,targets,mParentNull,baseName= self.cgmName)
            """
            self.atUtils('create_defineLoftMesh',
                         targets,
                         mParentNull,
                         baseName = self.cgmName )"""
        
            

            for tag,mHandle in md_handles.iteritems():
                if tag in ['lever']:
                    continue
                if tag in ['up','rp'] and rotVecControl:
                    continue
                if tag in ['start']:
                    ATTR.set_standardFlags(mHandle.mNode,attrs = ['sx','sy','sz'])
                    
                ATTR.set_standardFlags(mHandle.mNode,attrs = ['rx','ry','rz'])
                
            #Scaling our up vector =============================================================
            if rotVecControl and md_handles.get('up'):
                
                if not vecControlLiveScale:
                    mPlug = cgmMeta.cgmAttr(mEnd,'average',attrType='float')
                    
                    
                    _arg = "{0} = {1} >< {2}".format(mPlug.asCombinedShortName(),
                                                     "{0}.{1}X".format(_short,vectorScaleAttr),
                                                     "{0}.{1}Y".format(_short,vectorScaleAttr),
                                                     )
                    NODEFACTORY.argsToNodes("{0}".format(_arg)).doBuild()
                    
                    for tag in ['rp','up']:
                        if md_handles.get(tag):
                            mPlug.doConnectOut("{0}.scaleX".format(md_handles[tag].mNode))
                            mPlug.doConnectOut("{0}.scaleY".format(md_handles[tag].mNode))
                            mPlug.doConnectOut("{0}.scaleZ".format(md_handles[tag].mNode))
                
                else:
                    mPlug = cgmMeta.cgmAttr(mEnd,'average',attrType='float')
                    _arg = "{0} = {1} >< {2}".format(mPlug.asCombinedShortName(),
                                                     "{0}.distance".format(md_measure['width']['mShape'].mNode),
                                                     "{0}.distance".format(md_measure['height']['mShape'].mNode),
                                                     )
                    NODEFACTORY.argsToNodes("{0}".format(_arg)).doBuild()
                    
                    for tag in ['rp','up']:
                        if md_handles.get(tag):
                            mPlug.doConnectOut("{0}.sx".format(md_handles[tag].mNode))
                            mPlug.doConnectOut("{0}.sy".format(md_handles[tag].mNode))
                            mPlug.doConnectOut("{0}.sz".format(md_handles[tag].mNode))
                            
                    

                    
                    #md_measure['length']['mShape'].doConnectOut('distance',"{0}.scaleX".format(md_handles['up'].mNode))
                    #md_measure['length']['mShape'].doConnectOut('distance',"{0}.scaleY".format(md_handles['up'].mNode))
                    #d_measure['length']['mShape'].doConnectOut('distance',"{0}.scaleZ".format(md_handles['up'].mNode))
                
                #md_handles['end'].doConnectOut('scaleX',"{0}.scaleX".format(md_handles['up'].mNode) )
                #md_handles['end'].doConnectOut('scaleX',"{0}.scaleY".format(md_handles['up'].mNode) )
                #md_handles['end'].doConnectOut('scaleX',"{0}.scaleZ".format(md_handles['up'].mNode) )
                
                #mScaleGroup = md_handles['up'].doGroup(True,asMeta=True,typeModifier = 'scale')
            if md_handles.get('start'):
                mHandleFactory.color(md_handles['start'].mNode)
                mHandleFactory.color(md_jointLabels['start'].mNode)                
                if  md_handles.get('end'):
                    md_handles['end'].doConnectOut('scaleX',"{0}.scaleX".format(md_handles['start'].mNode))
                    md_handles['end'].doConnectOut('scaleY',"{0}.scaleY".format(md_handles['start'].mNode))
                    #mPlug.doConnectOut("{0}.scaleZ".format(md_handles['start'].mNode))
                
            if md_handles.get('end'):
                pos = md_handles['end'].p_position
                md_handles['end'].p_position = 1,2,3
                md_handles['end'].p_position = pos
                
            mel.eval('EnableAll;doEnableNodeItems true all;')

        return {'md_handles':md_handles,
                'ml_handles':ml_handles,
                'md_vector':md_vector,
                'md_jointLabels':md_jointLabels}
 
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
    
def define_set_baseSize(self,baseSize = None, baseAim = None, baseAimDefault = [0,0,1]):
    _str_func = 'define_set_baseSize'
    log.debug(cgmGEN.logString_start(_str_func))

    
    if baseSize is None:
        try:baseSize = self.baseSize
        except:raise ValueError,"No baseSize offered or found"

    d_baseDat = {}
    if self.hasAttr('baseDat'):
        d_baseDat = self.baseDat
        log.debug("|{0}| >>  Base dat found | {1}".format(_str_func,d_baseDat))        

    if not baseSize:
        return log.error("|{0}| >>  No baseSize value. Returning.".format(_str_func))
    log.debug("|{0}| >>  baseSize: {1}".format(_str_func,baseSize))
    
    if baseAim is None:
        try:baseAim = self.baseAim
        except:pass
        
    if not baseAim:
        baseAim = d_baseDat.get('end',None)
        if baseAim is None:
            log.debug("|{0}| >>  No baseAim value. Using default.".format(_str_func))
            baseAim = baseAimDefault
        else:
            log.debug("|{0}| >>  Found base aim in baseDat.".format(_str_func))
            
    log.debug("|{0}| >>  baseAim: {1}".format(_str_func,baseAim))
    
    #vBaseAim = MATH.Vector3(baseAim[0],baseAim[1],baseAim[2]) 
    #vBaseAim = MATH.transform_direction(self.mNode,vBaseAim)
    #log.debug("|{0}| >>  baseAim transformed: {1}".format(_str_func,vBaseAim))
    
    try:mDefineEndObj = self.defineEndHelper
    except:
        return log.warning("|{0}| >>  no defineEndHelper".format(_str_func))
        
    log.debug("|{0}| >>  mDefineEndObj: {1}".format(_str_func,mDefineEndObj))
    

    
    #Meat ==================================================
    log.debug("|{0}| >>  Processing...".format(_str_func)+ '-'*80)
    pos_self = self.p_position
    pos = DIST.get_pos_by_vec_dist(pos_self, TRANS.transformDirection(self.mNode,baseAim), baseSize[2])
    
    mDefineEndObj.p_position = pos
    
    _width = baseSize[0]
    _height = baseSize[1]
    
    mDefineEndObj.sx = _width
    mDefineEndObj.sy = _height
    mDefineEndObj.sz = MATH.average(_width,_height)
    
    if d_baseDat:
        log.debug("|{0}| >>  baseDat...".format(_str_func)+ '-'*40)
        #pprint.pprint(d_baseDat)
        for k,vec in d_baseDat.iteritems():
            mHandle = self.getMessageAsMeta('define{0}Helper'.format(STR.capFirst(k)))
            mUp = self.getMessageAsMeta('vector{0}Helper'.format(STR.capFirst(k)))
            
            if mHandle:
                log.debug("|{0}| >>  mHandle: {1}".format(_str_func,mHandle))
                if k == 'end':
                    _pos = DIST.get_pos_by_vec_dist(pos_self, TRANS.transformDirection(self.mNode,vec),baseSize[2])
                else:
                    _pos = DIST.get_pos_by_vec_dist(pos_self, TRANS.transformDirection(self.mNode,vec),baseSize[1])
                if mHandle == mUp:
                    SNAP.aim_atPoint(mHandle.mNode,_pos,'y+')
                else:
                    mHandle.p_position = _pos
            else:
                log.debug("|{0}| >>  Missing: {1}".format(_str_func,k))
    

def prerig_snapRPtoOrientHelper(self):
    _str_func = 'prerig_snapRPtoOrientHelper'
    log.debug(cgmGEN.logString_start(_str_func))

    
    mRP = self.getMessageAsMeta('defineRpHelper')
    if not mRP:
        return log.error("No rp found")
    mRPVec = self.getMessageAsMeta('vectorRpHelper')
    
    try:mOrientHelper = self.orientHelper
    except:return log.error("No orientHelper found")
    log.debug("|{0}| >>  mOrientHelper: {1}".format(_str_func,mOrientHelper))    
    log.debug("|{0}| >>  mRP: {1}".format(_str_func,mRP))        
    
    if mRP == mRPVec:
        mRP.p_orient = mOrientHelper.p_orient

    else:
        pos_self = self.p_position
        dist = DIST.get_distance_between_points(pos_self, mRP.p_position)
        vector_pos = mOrientHelper.getAxisVector('y+',asEuclid = 0)
    
        mRP.p_position = DIST.get_pos_by_vec_dist(pos_self, vector_pos,dist)
        
def prerig_handlesLayout(self,mode='even',curve='linear',spans=2):
    try:
        _str_func = 'prerig_handlesLayout'
        log.debug(cgmGEN.logString_start(_str_func))
        
        ml_prerig = self.msgList_get('prerigHandles')
        if not ml_prerig:
            return log.error(cgmGEN.logString_msg(_str_func,'No prerigHandles found'))
        
        ml_prerig = [mObj for mObj in ml_prerig if mObj.cgmType == 'blockHandle']
        try:idx_start,idx_end = self.atBlockModule('get_handleIndices')
        except:idx_start,idx_end = 0,len(ml_prerig)-1
            
        mStart = ml_prerig[idx_start]
        mEnd = ml_prerig[idx_end]
        ml_toSnap = ml_prerig[idx_start:idx_end+1]
        
        if not ml_toSnap:
            raise ValueError,"|{0}| >>  Nothing found to snap | {1}".format(_str_func,self)
        
        pprint.pprint(vars())
        
        return ARRANGE.alongLine([mObj.mNode for mObj in ml_toSnap],mode,curve,spans)
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
    
def handles_snapToRotatePlane(self,mode = 'template',cleanUp=0):
    _str_func = 'handles_snapToRotatePlane'
    log.debug(cgmGEN.logString_start(_str_func))

    log.debug(cgmGEN.logString_msg(_str_func,'dat get'))
    
    
    ml_handles = self.msgList_get('{0}Handles'.format(mode))
    if not ml_handles:
        raise ValueError,"|{0}| >>  No {2} handles | {1}".format(_str_func,self,mode)
    
    
    mOrientHelper = self.getMessageAsMeta('vectorRpHelper')
    if mOrientHelper:
        log.debug("|{0}| >>  RP helper found...".format(_str_func))
        vector_pos = mOrientHelper.getAxisVector('y+',asEuclid = 0)
        vector_neg = mOrientHelper.getAxisVector('y-',asEuclid = 0)        
    else:
        try:mOrientHelper = self.orientHelper
        except:raise ValueError,"No orientHelper found"
        
        vector_pos = mOrientHelper.getAxisVector('y+',asEuclid = 0)
        vector_neg = mOrientHelper.getAxisVector('y-',asEuclid = 0)        
    
    log.debug("|{0}| >>  mOrientHelper: {1}".format(_str_func,mOrientHelper))
   
    try:idx_start,idx_end = self.atBlockModule('get_handleIndices')
    except:
        idx_start,idx_end = 0,len(ml_handles)-1
    
    if mode == 'template':
        idx_end = -1
        
    log.debug(cgmGEN.logString_msg(_str_func,'Indicies || start: {0} | end: {1}'.format(idx_start,idx_end)))        
    
    mStart = ml_handles[idx_start]
    mEnd = ml_handles[idx_end]
    ml_toSnap = ml_handles[idx_start:idx_end]
    
    if not ml_toSnap:
        raise ValueError,"|{0}| >>  Nothing found to snap | {1}".format(_str_func,self)
        
    #pprint.pprint(vars())
    
    f_dist = DIST.get_distance_between_points(mStart.p_position,mEnd.p_position)
    f_cast = f_dist * 1.0
    
     
    #Meat ==================================================
    log.debug("|{0}| >>  processing...".format(_str_func)+ '-'*40)

    #Setup Loft curves and plane ----------------------------------------------------------------
    log.debug("|{0}| >> Setup curves...".format(_str_func))                     
    
            
    l_crvs = []
    for mObj in [mStart,mEnd]:
        _pos = mObj.p_position
        crv =   mc.curve (d=1, ep = [DIST.get_pos_by_vec_dist(_pos, vector_pos, f_cast),
                                     DIST.get_pos_by_vec_dist(_pos, vector_neg, f_cast)],
                               os=True)
        log.debug("|{0}| >> Created: {1}".format(_str_func,crv))
        l_crvs.append(crv)
        
    _res_body = mc.loft(l_crvs, o = True, d = 1, po = 1 )
    _inputs = mc.listHistory(_res_body[0],pruneDagObjects=True)
    _tessellate = _inputs[0]
    
    _d = {'format':2,#General
          'polygonType':1,#'quads'
          }
          
    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)    
            
    #Snap our joints ---------------------------------------------------------------------------------
    for mObj in ml_toSnap:
        SNAP.go(mObj, _res_body[0], rotation=False, pivot='closestPoint')
            
    #Cleanup --------------------------------------------------------------------------------------------
    if cleanUp:
        mc.delete(_res_body + l_crvs)
    
    
def prerig_snapHandlesToRotatePlane(self,cleanUp=0):
    _str_func = 'prerig_snapHandlesToRotatePlane'
    log.debug(cgmGEN.logString_start(_str_func))

    
    log.debug("|{0}| >>  Dat get...".format(_str_func)+ '-'*40)
    
    
    ml_prerig = self.msgList_get('prerigHandles')
    if not ml_prerig:
        raise ValueError,"|{0}| >>  No prerig handles | {1}".format(_str_func,self)
    
    
    mOrientHelper = self.getMessageAsMeta('vectorRpHelper')
    if mOrientHelper:
        log.debug("|{0}| >>  RP helper found...".format(_str_func))
        vector_pos = mOrientHelper.getAxisVector('y+',asEuclid = 0)
        vector_neg = mOrientHelper.getAxisVector('y-',asEuclid = 0)        
    else:
        try:mOrientHelper = self.orientHelper
        except:raise ValueError,"No orientHelper found"
        
        vector_pos = mOrientHelper.getAxisVector('y+',asEuclid = 0)
        vector_neg = mOrientHelper.getAxisVector('y-',asEuclid = 0)        
    
    log.debug("|{0}| >>  mOrientHelper: {1}".format(_str_func,mOrientHelper))
   
    try:idx_start,idx_end = self.atBlockModule('get_handleIndices')
    except:
        idx_start,idx_end = 0,len(ml_prerig)-1
        
    log.debug(cgmGEN.logString_msg(_str_func,'Indicies || start: {0} | end: {1}'.format(idx_start,idx_end)))        
    
    mStart = ml_prerig[idx_start]
    mEnd = ml_prerig[idx_end]
    ml_toSnap = ml_prerig[idx_start:idx_end]
    
    if not ml_toSnap:
        raise ValueError,"|{0}| >>  Nothing found to snap | {1}".format(_str_func,self)
        
    #pprint.pprint(vars())
    
    f_dist = DIST.get_distance_between_points(mStart.p_position,mEnd.p_position)
    f_cast = f_dist * 1.0
    
     
    #Meat ==================================================
    log.debug("|{0}| >>  processing...".format(_str_func)+ '-'*40)

    #Setup Loft curves and plane ----------------------------------------------------------------
    log.debug("|{0}| >> Setup curves...".format(_str_func))                     
    
            
    l_crvs = []
    for mObj in [mStart,mEnd]:
        _pos = mObj.p_position
        crv =   mc.curve (d=1, ep = [DIST.get_pos_by_vec_dist(_pos, vector_pos, f_cast),
                                     DIST.get_pos_by_vec_dist(_pos, vector_neg, f_cast)],
                               os=True)
        log.debug("|{0}| >> Created: {1}".format(_str_func,crv))
        l_crvs.append(crv)
        
    _res_body = mc.loft(l_crvs, o = True, d = 1, po = 1 )
    _inputs = mc.listHistory(_res_body[0],pruneDagObjects=True)
    _tessellate = _inputs[0]
    
    _d = {'format':2,#General
          'polygonType':1,#'quads'
          }
          
    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)    
            
    #Snap our joints ---------------------------------------------------------------------------------
    for mObj in ml_toSnap:
        SNAP.go(mObj, _res_body[0], rotation=False, pivot='closestPoint')
            
    #Cleanup --------------------------------------------------------------------------------------------
    if cleanUp:
        mc.delete(_res_body + l_crvs)
        

def prerig_get_rpBasePos(self,ml_handles = [], markPos = False, forceMidToHandle=False):
    """
    
    """
    try:
        _str_func = 'get_midIK_basePosOrient'
        log.debug(cgmGEN.logString_start(_str_func))

        
        if ml_handles:
            ml_use = ml_handles
        else:
            ml_handles = self.msgList_get('prerigHandles')
            if not ml_handles:
                ml_handles = self.msgList_get('templateHandles')
            
            #int_count = self.numControls
            #ml_use = ml_handles[:int_count]
            
            
            try:idx_start,idx_end = self.atBlockModule('get_handleIndices')
            except:idx_start,idx_end = 0,len(ml_handles)-1
                
            mStart = ml_handles[idx_start]
            mEnd = ml_handles[idx_end]
            
            if not idx_end == -1:
                ml_use = ml_handles[idx_start:idx_end+1]        
            else:
                ml_use = ml_handles[idx_start:]        
            
            
            log.debug("|{0}| >> Using: {1} : {2} | {3}".format(_str_func,idx_start,idx_end,[mObj.p_nameBase for mObj in ml_use]))
        
        #Mid dat... ----------------------------------------------------------------------
        _len_handles = len(ml_use)
        if _len_handles == 1:
            mid=0
            mMidHandle = ml_use[0]
        else:
            
            mid = int(_len_handles)/2
            mMidHandle = ml_use[mid]
            
        log.debug("|{0}| >> mid: {1}".format(_str_func,mid))
        
        b_absMid = False
        if MATH.is_even(_len_handles) and not forceMidToHandle:
            log.debug("|{0}| >> absolute mid mode...".format(_str_func,mid))
            b_absMid = True
            
        #...Main vector -----------------------------------------------------------------------
        try:mOrientHelper = self.vectorRpHelper#orientHelper
        except Exception,err:
            return log.warning("|{0}| >> No rp helper found: {1}".format(_str_func,self))
        #vec_base = MATH.get_obj_vector(mOrientHelper, 'y+')
        vec_base = MATH.get_obj_vector(mOrientHelper, 'y+')        
        log.debug("|{0}| >> Block up: {1}".format(_str_func,vec_base))
        
        #...Get vector -----------------------------------------------------------------------
        if b_absMid:
            crvCubic = CORERIG.create_at(ml_use, create= 'curve')
            pos_mid = CURVES.getMidPoint(crvCubic)
            mc.delete(crvCubic)
        else:
            pos_mid = mMidHandle.p_position
            
        crv = CORERIG.create_at([ml_use[0].mNode,ml_use[-1].mNode], create= 'curveLinear')
        pos_close = DIST.get_closest_point(pos_mid, crv)[0]
        #log.debug("|{0}| >> Pos close: {1} | Pos mid: {2}".format(_str_func,pos_close,pos_mid))
        vec_use = vec_base
        #if MATH.is_vector_equivalent(pos_mid,pos_close,3):
        #    log.debug("|{0}| >> Mid on linear line, using base vector".format(_str_func))
        #    vec_use = vec_base
        #else:
        #    vec_use = MATH.get_vector_of_two_points(pos_close,pos_mid)
        mc.delete(crv)
        
        #...Get length -----------------------------------------------------------------------
        #dist_helper = 0
        #if ml_use[-1].getMessage('pivotHelper'):
            #log.debug("|{0}| >> pivotHelper found!".format(_str_func))
            #dist_helper = max(POS.get_bb_size(ml_use[-1].getMessage('pivotHelper')))
            
        dist_min = DIST.get_distance_between_points(ml_use[0].p_position, pos_mid)/2.0
        dist_base = DIST.get_distance_between_points(pos_mid, pos_close)
        
        #...get new pos
        dist_use = MATH.Clamp(dist_base, dist_min, None)
        log.debug("|{0}| >> Dist min: {1} | dist base: {2} | use: {3}".format(_str_func,
                                                                              dist_min,
                                                                              dist_base,
                                                                              dist_use))
        
        pos_use = DIST.get_pos_by_vec_dist(pos_mid,vec_use,
                                           DIST.get_distance_between_points(ml_handles[0].p_position,
                                                                                            pos_mid))
        pos_use2 = DIST.get_pos_by_vec_dist(pos_mid,vec_base,dist_use)
        
        if markPos:
            crv = CORERIG.create_at(create='curve',l_pos= [pos_mid,pos_use])
            crv=mc.rename(crv,'{0}_RPPos'.format(self.p_nameBase))
            TRANS.rotatePivot_set(crv,pos_use)
            CORERIG.override_color(crv,'white')
            #LOC.create(position=pos_use,name='{0}_RPPos'.format(self.p_nameBase))
            #LOC.create(position=pos_use2,name='pos2')
        
        return pos_use
        
        pos_mid = ml_templateHandles[mid].p_position
    
    
        #Get our point for knee...
        vec_mid = MATH.get_obj_vector(ml_blendJoints[1], 'y+')
        pos_mid = mKnee.p_position
        pos_knee = DIST.get_pos_by_vec_dist(pos_knee,
                                            vec_knee,
                                            DIST.get_distance_between_points(ml_blendJoints[0].p_position, pos_knee)/2)
    
        mKnee.p_position = pos_knee
    
        CORERIG.match_orientation(mKnee.mNode, mIKCrv.mNode)    
    
    
        return True
    except Exception,err:cgmGEN.cgmException(Exception,err)
        
        
def focus(self,arg=True,mode='vis',ml_focus = None):
    '''
    
    :parameters:
        arg(bool) - on or off
        mode(string)
            vis
            template
            
    :returns:
        None
        
    :raises:
        Exception | if reached
    
    '''
    try:
        mRoot = self.getBlockRoot()
        if mRoot:
            if not ml_focus:
                ml_focus = [self]
            mChildren = mRoot.getBlockChildrenAll()
            for mBlock in mChildren:
                if not arg:
                    mBlock.v=True
                    mBlock.template = False
                else:
                    if mBlock not in ml_focus:
                        if mode == 'vis':
                            mBlock.v = False
    
                        elif mode == 'template':
                            mBlock.template = True
                            mBlock.v=True
                    else:
                        mBlock.v=True
                        mBlock.template=False

            
        #cgmGEN.func_snapShot(vars())
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
        
        
def pivotHelper_get(self,mHandle=None, 
                    baseShape=None,
                    baseSize = None,
                    upAxis = 'y+',
                    setAttrs = {},
                    side = None,
                    loft = True,
                    forceNew=False):
    try:
        _str_func = 'addPivotSetupHelper'
        mBuffer = mHandle.getMessageAsMeta('pivotHelper')
        if mBuffer:
            if forceNew:
                mBuffer.delete()
            else:
                return mBuffer
            
        #_bbsize = POS.get_axisBox_size(mHandle.mNode,False)
        #_size = MATH.average(_bbsize)
        _size = baseSize
        _sizeSub = _size * .2        
        mHandleFactory = self.asHandleFactory()
        
        if side == None:
            _side = self.UTILS.get_side(self)
        else:
            _side = side

        ml_pivots = []
        mPivotRootHandle = False
        self_pos = mHandle.p_position
        self_upVector = mHandle.getAxisVector(upAxis)

        d_pivotDirections = {'back':'z-',
                             'front':'z+',
                             'left':'x+',
                             'right':'x-'}

        d_altName = {'back':'heel',
                     'front':'toe',
                     'center':'ball'}

        mAxis = VALID.simpleAxis(d_pivotDirections['front'])

        _baseShape = 'loft' + baseShape[0].capitalize() + ''.join(baseShape[1:])
        _baseSize = baseSize
        #Main Handle -----------------------------------------------------------------------------
        pivotHandle = CURVES.create_controlCurve(mHandle.mNode,
                                                 shape=_baseShape,
                                                 direction = 'y-',
                                                 sizeMode = 'fixed',
                                                 size = _size)
        mPivotRootHandle = cgmMeta.validateObjArg(pivotHandle,'cgmObject',setClass=True)
        mPivotRootHandle.addAttr('cgmName','base')
        mPivotRootHandle.addAttr('cgmType','pivotHelper')            
        mPivotRootHandle.doName()

        mPivotRootHandle.p_position = self_pos
        mHandleFactory.color(mPivotRootHandle.mNode,_side,'sub')

        mHandle.connectChildNode(mPivotRootHandle,'pivotHelper','block')#Connect    

        if mHandle.hasAttr('addPivot'):
            mHandle.doConnectOut('addPivot',"{0}.v".format(mPivotRootHandle.mNode))

        self.msgList_append('prerigHandles',mPivotRootHandle)

        #Top loft ----------------------------------------------------------------
        mTopLoft = mPivotRootHandle.doDuplicate(po=False)
        mTopLoft.addAttr('cgmName','topLoft')
        mTopLoft.addAttr('cgmType','pivotHelper')            
        mTopLoft.doName()

        mTopLoft.parent = mPivotRootHandle

        #_axisBox = CORERIG.create_proxyGeo('cube',_baseSize,ch=False)[0]
        #SNAP.go(_axisBox,mHandle.mNode)
            #_axisBox = CORERIG.create_axisProxy(self._mTransform.mNode)

        #Sub pivots =============================================================================
        for a in ['pivotBack','pivotFront','pivotLeft','pivotRight','pivotCenter']:
            _strPivot = a.split('pivot')[-1]
            _strPivot = _strPivot[0].lower() + _strPivot[1:]
            _strName = d_altName.get(_strPivot,_strPivot)
            log.debug("|{0}| >> Adding pivot helper: {1}".format(_str_func,_strPivot))
            if _strPivot == 'center':
                pivot = CURVES.create_controlCurve(mHandle.mNode, shape='circle',
                                                   direction = upAxis,
                                                   sizeMode = 'fixed',
                                                   size = _sizeSub)
                mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                mPivot.addAttr('cgmName',_strName)
                ml_pivots.append(mPivot)
                mPivot.p_parent = mPivotRootHandle

                mPivotRootHandle.connectChildNode(mPivot, a ,'handle')#Connect    

                #mPivot.p_position = p_ballPush
            else:


                mAxis = VALID.simpleAxis(d_pivotDirections[_strPivot])
                _inverse = mAxis.inverse.p_string
                pivot = CURVES.create_controlCurve(mHandle.mNode, shape='hinge',
                                                   direction = _inverse,
                                                   sizeMode = 'fixed', size = _sizeSub)
                mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                mPivot.addAttr('cgmName',_strName)
                mPivot.p_parent = mPivotRootHandle

                mPivotRootHandle.connectChildNode(mPivot, a ,'handle')#Connect    

                #mPivot.p_position = DIST.get_pos_by_axis_dist(mHandle.mNode,mAxis.p_string, _size)
                mPivot.p_position = DIST.get_closest_point(DIST.get_pos_by_axis_dist(mHandle.mNode,mAxis.p_string, _size),
                                                           mPivotRootHandle.mNode)[0]
                #SNAPCALLS.snap(mPivot.mNode,_axisBox,rotation=False,targetPivot='castNear',targetMode=mAxis.p_string)
                #SNAPCALLS.get_special_pos()
                #mPivot.p_position = #SNAPCALLS.get_special_pos(mPivotRootHandle.p_nameLong,'axisBox',mAxis.p_string,True)
                SNAP.aim_atPoint(mPivot.mNode,self_pos, _inverse, upAxis, mode='vector', vectorUp = self_upVector)

                ml_pivots.append(mPivot)

                #if _strPivot in ['left','right']:
                    #mPivot.p_position = p_ballPush
                    #mPivot.tz = .75

        #Clean up Pivot root after all else --------------------------------------------------
        #mAxis = VALID.simpleAxis(d_pivotDirections['back'])
        #p_Base = DIST.get_pos_by_axis_dist(mPivotRootHandle.mNode,
        #                                   d_pivotDirections['back'],
        #                                   _size/4 )

        #mc.xform (mPivotRootHandle.mNode,  ws=True, sp= p_Base, rp=p_Base, p=True)

        for mPivot in ml_pivots:#Unparent for loft
            mPivot.p_parent = False
            
        if loft:
            if mHandle.getMessage('loftCurve'):
                log.debug("|{0}| >> LoftSetup...".format(_str_func))
    
                #Fix the aim on the foot
                mTopLoft.parent = False
    
                l_footTargets = [mHandle.loftCurve.mNode, mTopLoft.mNode,mPivotRootHandle.mNode]
    
                _res_body = mc.loft(l_footTargets, o = True, d = 3, po = 0,reverseSurfaceNormals=True)
    
                mTopLoft.parent = mPivotRootHandle
    
                _loftNode = _res_body[1]
                mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)        
    
    
                mLoftSurface.overrideEnabled = 1
                mLoftSurface.overrideDisplayType = 2
                #...this used to be {1} + 1. may need to revisit for head/neck
    
                mLoftSurface.parent = self.templateNull
    
                #mLoft.p_parent = mTemplateNull
                mLoftSurface.resetAttrs()
    
                ATTR.set(_loftNode,'degree',1)    
    
                mLoftSurface.doStore('cgmName',self)
                mLoftSurface.doStore('cgmType','footApprox')
                mLoftSurface.doName()
    
    
                #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
                #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;
    
                #mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
    
                #Color our stuff...
                mHandleFactory.color(mLoftSurface.mNode,transparent=True)
                #RIGGING.colorControl(mLoft.mNode,_side,'main',transparent = True)
    
                mLoftSurface.inheritsTransform = 0
                for s in mLoftSurface.getShapes(asMeta=True):
                    s.overrideDisplayType = 2   
    
                self.connectChildNode(mLoftSurface.mNode, 'templateFootMesh', 'block')

        for mPivot in ml_pivots:
            mPivot.addAttr('cgmType','pivotHelper')            
            mPivot.doName()

            #CORERIG.colorControl(mPivot.mNode,_side,'sub') 
            mHandleFactory.color(mPivot.mNode,_side,'sub')

            mPivot.parent = mPivotRootHandle

            #if mPivot.cgmName in ['ball','left','right']:
                #mPivot.tz = .5

            #mPivotRootHandle.connectChildNode(mPivot,'pivot'+ mPivot.cgmName.capitalize(),'handle')#Connect    
            self.msgList_append('prerigHandles',mPivot)



        #if mHandle.getShapes():
        #    SNAPCALLS.snap(mPivotRootHandle.mNode,mHandle.mNode,rotation=False,targetPivot='axisBox',targetMode='y-')
        #    mTopLoft.ty = 1

        #if _axisBox:
        #    mc.delete(_axisBox)

        #log.debug(_bbsize)
        #TRANS.scale_to_boundingBox(mPivotRootHandle.mNode,[_bbsize[0],None,_bbsize[2] * 2], False)
        #mPivotRootHandle.scale = [_bbsize[0],_bbsize[1],_bbsize[2] * 2]
        #mc.xform(mPivotRootHandle.mNode,
            #scale = [_bbsize[0],_bbsize[1],_bbsize[2] * 2],
            #worldSpace = True, absolute = True)

        return mPivotRootHandle,mTopLoft
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        

def is_current(self):
    try:
        _str_func = 'is_current'
        log.debug(cgmGEN.logString_start(_str_func))
        
        _ver_block = self.version
        mBlockModule = self.getBlockModule()
        _ver_module = mBlockModule.__version__
        
        _blockProfile = self.getMayaAttr('blockProfile')
        _d_profiles = mBlockModule.__dict__.get('d_block_profiles',{})
        _typeDict=  _d_profiles.get(_blockProfile,{})
        if not _typeDict:
            print(cgmGEN._str_subLine)
            log.error(cgmGEN.logString_msg(_str_func,'blockType not found in blockProfiles. Please fix | found {0}'.format(_blockProfile)))
            pprint.pprint(_d_profiles.keys())
            print(cgmGEN._str_subLine)
            
        
        if _ver_block == _ver_module:
            print("[{0}] up to date | blockVersion: {1}".format(self.p_nameShort, _ver_block))            
            return True
        
        log.debug("[{0}] out of date | blockVersion: {1} | blockModule: {2}".format(self.p_nameShort, _ver_block, _ver_module))
        return False   
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
    
def update(self,force=False,stopState = 'define'):
    """
    Bring a rigBlock to current settings - check attributes, reset baseDat
    """
    try:
        _str_func = 'update'
        log.debug(cgmGEN.logString_start(_str_func))
        
        if is_current(self) and not force:
            return True
        
        log.debug(cgmGEN.logString_sub(_str_func,"Checking blockProfile"))
        mBlockModule = self.p_blockModule
        _blockProfile = self.getMayaAttr('blockProfile')
        _d_profiles = mBlockModule.d_block_profiles
        _typeDict=  _d_profiles.get(_blockProfile,{})
        if not _typeDict:
            log.error(cgmGEN.logString_msg(_str_func,'blockType not found in blockProfiles. Please fix | found {0}'.format(_blockProfile)))
            pprint.pprint(_d_profiles.keys())
            return False        
        
        
        verify_blockAttrs(self)
        
        _baseDat = _typeDict.get('baseDat')
        if _baseDat:
            log.debug(cgmGEN.logString_msg(_str_func,'baseDat: {0}'.format(_baseDat)))
            self.baseDat = _baseDat
 
            
        blockDat_save(self)
        
        _dat = self.blockDat
        
        for k in ['baseAim','baseSize']:
            _v = _typeDict.get(k)
            if _v is not None:
                log.debug(cgmGEN.logString_msg(_str_func,'{0} : {1}'.format(k,_v)))
                _dat['ud'][k] = _v
                for a in 'XYZ':
                    _dat['ud'].pop(k+a)
        
        if stopState is not None:
            _dat['blockState'] = stopState
        self.blockDat = _dat
        
        
        blockDat_load(self,redefine=True)
        
        try:self.doStore('version', mBlockModule.__version__, 'string',lock=True)
        except Exception,err:
            log.error(cgmGEN.logString_msg(_str_func,"Failed to set version | {0}".format(err)))
        #Verify
        #verify_blockAttrs(self, queryMode=False)
        #Check out base dat
        
        #pprint.pprint(vars())
        
        return True   
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def to_scriptEditor(self,string='mBlock'):
    try:
        _str_func = 'to_scriptEditor'
        log.debug(cgmGEN.logString_start(_str_func))
        mel.eval('python "import cgm.core.cgm_Meta as cgmMeta;mBlock = cgmMeta.asMeta({0});"'.format("'{0}'".format(self.mNode)))
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)