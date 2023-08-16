"""
------------------------------------------
block: cgm.core.mrs.lib
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

These are functions with self assumed to be a cgmRigBlock
================================================================
"""
__MAYALOCAL = 'BLOCKUTILS'

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
import importlib
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

import maya.cmds as mc
import maya.mel as mel
# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
##from cgm.core import cgm_PuppetMeta as PUPPETMETA
from cgm.core import cgm_RigMeta as RIGMETA
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.lib.arrange_utils as ARRANGE
import cgm.core.lib.euclid as EUCLID

import cgm.core.lib.geo_Utils as GEO
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
import cgm.core.lib.string_utils as CORESTRING
import cgm.core.cgmPy.str_Utils as STRINGS
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
import cgm.core.mrs.lib.post_utils as MRSPOST
from cgm.core.classes import GuiFactory as CGMUI
from cgm.core.cgmPy import dict_utils as CGMDICT
import cgm.core.classes.GuiFactory as cgmUI
import cgm.core.mrs.lib.blockShapes_utils as BLOCKSHAPES

mUI = cgmUI.mUI
#=============================================================================================================
#>> Queries
#=============================================================================================================
def example(self):
    """
    Get a snap shot of all of the controls of a rigBlock
    """
    try:
        _str_func = 'snapShot_controls_get'
        log.debug(cgmGEN.logString_start(_str_func))
        str_self = self.mNode
        
        #Control sets ===================================================================================
        log.debug(cgmGEN.logString_sub(_str_func, '...'))
        return 'This does nothing'
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)

def get_side(self):
    _side = 'center' 
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side') 
    return _side

def reorder_udAttrs(self):
    ATTR.reorder_ud(self.mNode)
    
def get_uiString(self,showSide=True, skip = []):
    """
    Get a snap shot of all of the controls of a rigBlock
    """
    try:
        _str_func = 'get_uiString'
        log.debug(cgmGEN.logString_start(_str_func))
        str_self = self.mNode
        _d_scrollList_shorts = BLOCKGEN._d_scrollList_shorts
        _l_report = []
        
        #Control sets ===================================================================================
        log.debug(cgmGEN.logString_sub(_str_func, '...'))
        
        if showSide:
            if self.getMayaAttr('side'):
                _v = self.getEnumValueString('side')
                _l_report.append( _d_scrollList_shorts.get(_v,_v))
            
        if self.getMayaAttr('position'):
            _v = self.getMayaAttr('position')
            if _v.lower() not in ['','none']:
                _l_report.append( _d_scrollList_shorts.get(_v,_v) )
                
                                    
        l_name = []
        
        #l_name.append( ATTR.get(_short,'blockType').capitalize() )
        _cgmName = self.getMayaAttr('cgmName')
        l_name.append('"{0}"'.format(_cgmName))

        #_l_report.append(STR.camelCase(' '.join(l_name)))
        _l_report.append(' - '.join(l_name))
        
            
        #_l_report.append(ATTR.get(_short,'blockState'))
        if 'blockState' not in skip:
            if self.getMayaAttr('isBlockFrame'):
                _l_report.append("[FRAME]")
            else:
                _state = self.getEnumValueString('blockState')
                _blockState = _d_scrollList_shorts.get(_state,_state)
                _l_report.append("[{0}]".format(_blockState.upper()))
        
        """
        if mObj.hasAttr('baseName'):
            _l_report.append(mObj.baseName)                
        else:
            _l_report.append(mObj.p_nameBase)"""                
    
        if self.isReferenced():
            _l_report.append("Referenced")
            
        _str = " | ".join(_l_report)
        
        
        #Block dat
        l_block = []
        _blockProfile = self.getMayaAttr('blockProfile')
        l_block.append(ATTR.get(str_self,'blockType').capitalize())
        
        if _blockProfile:
            if _cgmName in _blockProfile:
                _blockProfile = _blockProfile.replace(_cgmName,'')
            _blockProfile= STR.camelCase(_blockProfile)                    
            l_block.append(_blockProfile)
            
        _str = _str + (' - [{0}]'.format("-".join(l_block)))        
        
        return _str
        
    except Exception as err:
        log.debug(cgmGEN.logString_start(_str_func,'ERROR'))
        log.error(err)
        return self.mNode


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
        raise RuntimeError("Shouldn't have gotten here")    
    
    else:
        mParentModule = mParentModule[0]
        log.debug("|{0}| >> moduleParent: {1}".format(_str_func,mParentModule))
        
        ml_targetJoints = mParentModule.rigNull.msgList_get('moduleJoints',asMeta = True, cull = True)
        
        if not ml_targetJoints:
            raise ValueError("mParentModule has no module joints.")
        if mode == 'end':
            mTarget = ml_targetJoints[-1]
        elif mode == 'base':
            mTarget = ml_targetJoints[0]
        else:
            _msg = ("|{0}| >> Unknown mode: {1}".format(_str_func,mode))
            if noneValid:
                return log.error(_msg)
            raise ValueError(_msg)
        return mTarget

def verify_blockAttrs(self, blockType = None, forceReset = False, queryMode = True, extraAttrs = None, mBlockModule = None, skipBlockAttrs = False):
    """
    Verify the attributes of a given block type
    
    force - overrides the excpetion on a failure
    """
    try:
        _str_func = 'verify_blockAttrs'
        log.debug(cgmGEN.logString_start(_str_func))

        if queryMode:
            log.debug("|{0}| >> QUERY MODE".format(_str_func,self))
        if blockType is None:
            mBlockModule = self.p_blockModule
        elif not mBlockModule:
            raise NotImplementedError("Haven't implemented blocktype changing...")
        cgmGEN._reloadMod(mBlockModule)
        try:d_attrsFromModule = mBlockModule.d_attrsToMake
        except:d_attrsFromModule = {}
        
        d_defaultSettings = copy.copy(BLOCKSHARE.d_defaultAttrSettings)
    
        try:d_defaultSettings.update(mBlockModule.d_defaultSettings)
        except:pass
        
        if not skipBlockAttrs:
            try:d_defaultSettings.update(mBlockModule.d_block_profiles[self.blockProfile])
            except Exception as err:
                log.debug(cgmGEN.logString_msg(_str_func,'Failed to query blockProfile defaults | {0}'.format(err)))
                pass        
    
        try:_l_msgLinks = mBlockModule._l_controlLinks
        except:_l_msgLinks = []
    
        _d = copy.copy(BLOCKSHARE.d_defaultAttrs)
        #pprint.pprint(d_defaultSettings)
        
        _l_standard = mBlockModule.__dict__.get('l_attrsStandard',[])
        log.debug("|{0}| >> standard: {1} ".format(_str_func,_l_standard))                        
        for k in _l_standard:
            if k in list(BLOCKSHARE._d_attrsTo_make.keys()):
                _d[k] = BLOCKSHARE._d_attrsTo_make[k]
            else:
                log.warning("|{0}| >> standard attr missing def: {1} ".format(_str_func,k))                        
                
        if extraAttrs is not None:
            _d.update(extraAttrs)
    
        for k,v in list(d_attrsFromModule.items()):
            if k in list(_d.keys()):
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
        
        _short = self.mNode
        
        #This is the verify part...
        _keys = list(_d.keys())
        _keys.sort()
        #for a,t in self._d_attrsToVerify.iteritems():
        
        def checkType(a,attrType,enum=None):
            try:
                if ATTR.has_attr(_short, a):
                    _type = ATTR.get_type(_short,a)
                    if _type != attrType:
                        v = ATTR.get(_short,a)
                        log.debug(cgmGEN.logString_msg(_str_func,'Attribute of wrong type | {0} | type: {1} | wanted: {2}'.format(a,_type,attrType)))
                        ATTR.convert_type(_short,a,attrType)
                        return v
            except Exception as err:
                log.error("Failed to convert 'Attribute of wrong type | {0} | type: {1} | wanted: {2} | err: {3}".format(a,_type,attrType,err))
                
        for a in _keys:
            try:
                if forceReset and a in ['blockType']:
                    continue
                v = d_defaultSettings.get(a,None)
                t = _d[a]
                
                log.debug("|{0}| '{1}' | defaultValue: {2} | type: {3} ".format(_str_func,a,v,t)) 
                
                if ':' in t:                    
                    if forceReset:
                        self.addAttr(a, v, attrType = 'enum', enumName= t, keyable = False)		                        
                    else:
                        strValue = None
                        _converted = False
                        
                        if self.hasAttr(a):
                            _type = ATTR.get_type(_short,a)
                            if _type != 'enum':
                                _use = ATTR.get(_short,a)
                                log.debug(cgmGEN.logString_msg(_str_func,'Attribute of wrong type | {0} | type: {1} | wanted: {2}'.format(a,_type,'enum')))
                                ATTR.convert_type(_short,a,'enum',t)
                                self.addAttr(a,value = _use, attrType = 'enum', enumName= t, keyable = False)
                            
                        _enum = ATTR.get_enum(_short,a)
                        if _enum != t:
                            strValue = ATTR.get_enumValueString(_short,a)
                        
                        self.addAttr(a,initialValue = v, attrType = 'enum', enumName= t, keyable = False)
                        
                        if strValue and strValue in t:
                            try:ATTR.set(_short,a,strValue)
                            except Exception as err:"...Failed to set old value: {0} | err: {1}".format(strValue,err)

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
                    #checkType(a,'float3')
                    if not self.hasAttr(a):
                        ATTR.add(_short, a, attrType='float3', keyable = True)
                        
                        if v:ATTR.set(_short,a,v)
                    elif forceReset:
                        ATTR.set(_short,a,v)
                else:
                    if t == 'string':
                        _l = True
                        if v is None:v = ''                        
                    else:_l = False
                    
                    if forceReset:
                        self.addAttr(a, v, attrType = t,lock=_l, keyable = False)                                
                    else:
                        self.addAttr(a,initialValue = v, attrType = t,lock=_l, keyable = False)            
            except Exception as err:
                _msg = "|{0}| Add attr Failure >> '{1}' | type: {4} | defaultValue: {2} | err: {3}".format(_str_func,a,v,err,_d.get(a))
                log.error(_msg) 
                if not forceReset:
                    cgmGEN.cgmExceptCB(Exception,err,msg=_msg)                    
        
        for a in ['blockState']:
            ATTR.set_lock(_short,a,True)
            
        return True
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    
def verify(self, blockType = None, size = None, side = None, forceReset = False, reloadModule=True):
    """
    Verify a block
    """
    _str_func = 'verify'
    _short = self.mNode
    
    log.debug(cgmGEN.logString_start(_str_func))

    if self.isReferenced():
        raise Exception("|{0}| >> Cannot verify referenced nodes".format(_str_func))

    _type = self.getMayaAttr('blockType')
    if blockType is not None:
        if _type is not None and _type != blockType:
            raise ValueError("|{0}| >> Conversion necessary. blockType arg: {1} | found: {2}".format(_str_func,blockType,_type))
    else:
        blockType = _type
        
    _mBlockModule = self.query_blockModuleByType(blockType)
    if reloadModule:
        cgmGEN._reloadMod(_mBlockModule)
    
    self.doStore('blockType',blockType)
    verify_blockAttrs(self,blockType,queryMode=False,mBlockModule=_mBlockModule,forceReset=forceReset)
    
    _side = side
    try:
        if _side is not None and self._callKWS.get('side'):
            log.debug("|{0}| >> side from call kws...".format(_str_func,_side))
            _side = self._callKWS.get('side')
    except:log.debug("|{0}| >> _callKWS check fail.".format(_str_func))


    if _side is not None:
        log.info("|{0}| >> Side: {1}".format(_str_func,_side))                
        try: ATTR.set(self.mNode,'side',_side)
        except Exception as err:
            log.error("|{0}| >> Failed to set side. {1}".format(_str_func,err))


    #>>> Base shapes --------------------------------------------------------------------------------
    try:self.baseSize = self._callSize
    except Exception as err:log.debug("|{0}| >> _callSize push fail: {1}.".format(_str_func,err))
    self.doName()
    
    if ATTR.get_type(self.mNode,'blockProfile') == 'enum':
        ATTR.convert_type(self.mNode,'blockProfile','string')
        
    return True
    
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
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
        
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
        
        l_nameList = self.datList_get('nameList')
        for i,n in enumerate(l_nameList):
            if _cgmName in n:
                l_nameList[i] = n.replace(_cgmName,nameTag)
                
        self.datList_connect('nameList',l_nameList)
        pprint.pprint(l_nameList)
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    
def set_nameIter(self,nameTag = None):
    try:
        _short = self.p_nameShort
        _str_func = 'set_nameIter'
        log.debug(cgmGEN.logString_start(_str_func))

        
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        
        if nameTag is None:
            log.debug("|{0}| >> getting value by ui prompt".format(_str_func))
            _cgmName = self.getMayaAttr('nameIter')
            _title = 'Set name iter tag...'
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
                log.error("|{0}| >> Change cancelled.".format(_str_func)+ '-'*80)
                #self.doName()
                return False
        if nameTag:
            self.nameIter = nameTag
        #self.doName()
        
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    

def set_blockNullFormState(self,state=True, define = True, form=True,prerig=True):
    _str_func = 'set_blockNullFormState'
    log.debug(cgmGEN.logString_start(_str_func))

    
    self.template = state
    
    if define:
        try:self.defineNull.template = state
        except:pass
        #try:self.noTransDefineNull.template=state
        #except:pass
    if form:
        try:self.formNull.template = state
        except:pass
        #try:self.noTransFormNull.template=state
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
            continue
    """
    if self.hasAttr('blockProfile'):
        _blockProfile = self.getMayaAttr('blockProfile') or ''
        if _d.get('cgmName','') not in _blockProfile:
            #if _d.get('cgmName','') in _blockProfile:
            _blockProfile = _blockProfile.replace(_d['cgmName'],'')
            if len(_blockProfile):
                _d['cgmNameModifier'] = STR.camelCase(_blockProfile)
                """
    _blockType = ATTR.get(_short,'blockType')
    _d['cgmType'] = _blockType + 'Block'
    
    pprint.pprint(_d)
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
    for k,v in list(_d.items()):
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
    
    for plug in ['formNull','noTransFormNull',
                 'prerigNull','noTransPrerigNull',
                 'defineNull','noTransDefineNull',
                 'moduleTarget']:
        mPlug = self.getMessageAsMeta(plug)
        if mPlug:
            mPlug.doName()

        
def set_side(self,side=None):
    try:
        _short = self.p_nameShort
        _str_func = 'set_side'
        log.debug(cgmGEN.logString_start(_str_func))

        
        if str(side).lower() in ['none']:
            side = 0
        try:
            ATTR.set(_short,'side',side)
        except Exception as err:
            log.error("|{0}| >> Failed to change attr. | err: {1}".format(_str_func,err))            
            return False
        
        self.doName()
        color(self)
        if self.getMessage('moduleTarget'):module_verify(self)
            
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    
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
        except Exception as err:
            log.error("|{0}| >> Failed to change attr. | err: {1}".format(_str_func,err))            
            return False
        
        self.doName()
        if self.getMessage('moduleTarget'):module_verify(self)
        
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)

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

    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def color_outliner(self,mNodes = None, arg = 'main', stateLinks = True):
    _short = self.p_nameShort
    _str_func = 'color'
    log.debug(cgmGEN.logString_start(_str_func))

    cgmGEN._reloadMod(BLOCKSHARE)
    
    d_color = BLOCKSHARE.d_outlinerColors.get(self.blockType)
    if not d_color:
        return log.warning(cgmGEN.logString_msg(_str_func,"No color data found"))
    
    if not mNodes:
        mNodes = [self]
        
    def color(mArg,arg):
        mArgs = VALID.listArg(mArg)
        for mO in mArgs:
            log.info(cgmGEN.logString_msg(_str_func, "Coloring: {0}".format(mO)))            
            mO.useOutlinerColor = 1
            mO.outlinerColor = d_color.get(arg)
        
    
    for mNode in mNodes:
        color(mNode,arg)
        
        if stateLinks:
            for s in BLOCKSHARE._l_blockStates[:mNode.blockState+1]:
                d_stateLinks = get_stateLinks(mNode,s)
                for lnk in d_stateLinks.get('msgLinks',[]):
                    mObj = mNode.getMessageAsMeta(lnk)
                    #print mObj
                    if mObj: color(mObj,'sub')
            
        
        


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
    except Exception as err:
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
        raise ValueError("|{0}| >> referenced node: {1}".format(_str_func,self.mNode))

    _str_state = self.getEnumValueString('blockState')
    
    if _str_state != 'define':
        raise ValueError("[{0}] is not in define form. state: {1}".format(self.mNode, _str_state))

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    mBlockModule = self.p_blockModule
    
    for c in ['define']:
        if c in list(mBlockModule.__dict__.keys()):
            log.debug("|{0}| >> BlockModule {1} call found...".format(_str_func,c))            
            self.atBlockModule(c)
            
    try:attrMask_getBaseMask(self)
    except Exception as err:
        log.info(cgmGEN.logString_msg(_str_func,'attrMask fail | {0}'.format(err)))

    self.blockState = 'define'#...yes now in this state
    return True
    


#=============================================================================================================
#>> Form
#=============================================================================================================
def is_formBAK(self):
    if not self.getMessage('formNull'):
        return False
    return True


def is_form(self):
    try:
        _str_func = 'is_form'
        log.debug(cgmGEN.logString_start(_str_func))

        return msgDat_check(self, get_stateLinks(self,'form'))
        
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)

def formDeleteBAK(self,msgLinks = []):
    try:
        _str_func = 'formDelete'
        log.debug(cgmGEN.logString_start(_str_func))

        
        for link in msgLinks + ['formNull']:
            if self.getMessage(link):
                log.debug("|{0}| >> deleting link: {1}".format(_str_func,link))                        
                mc.delete(self.getMessage(link))
        return True
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def formNull_verify(self):
    if not self.getMessage('formNull'):
        str_formNull = CORERIG.create_at(self.mNode)
        formNull = cgmMeta.validateObjArg(str_formNull, mType = 'cgmObject',setClass = True)
        formNull.connectParentNode(self, 'rigBlock','formNull') 
        formNull.doStore('cgmName', self)
        formNull.doStore('cgmType','formNull')
        formNull.doName()
        formNull.p_parent = self
        formNull.setAttrFlags()
    else:
        formNull = self.formNull   
    return formNull

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


def blockFrame_alignTo(self,formScale = False):
    _str_func = 'blockFrame_get'
    log.debug(cgmGEN.logString_start(_str_func))
    mBlockFrame = self.getMessageAsMeta('blockFrame')
    if not mBlockFrame:
        return log.error(cgmGEN.logString_msg(_str_func,'No blockFrame found'))
    
    mBlockFrame.atBlockModule('subBlock_align',self,formScale)

    

    
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
        
        mNull.doStore('cgmRelease',cgmGEN.__RELEASESTRING)
    else:
        mNull = self.getMessageAsMeta(_strPlug)
    return mNull

def create_formLoftMesh(self, targets = None, mDatHolder = None, mFormNull = None,transparent = True,
                            uAttr = 'neckControls',baseName = 'test',plug = 'formLoftMesh'):
    try:
        _str_func = 'create_formLoftMesh'
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
    
        for a,v in list(_d.items()):
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
    
        mLoft.p_parent = mFormNull
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
        self.asHandleFactory().color(mLoft.mNode,transparent=transparent)
        #CORERIG.colorControl(mLoft.mNode,_side,'main',transparent = True)
    
        mLoft.inheritsTransform = 0
        for s in mLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 2   
    
        self.connectChildNode(mLoft.mNode, plug, 'block')    
        return mLoft
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
#=============================================================================================================
#>> Prerig
#=============================================================================================================
def noTransformNull_verify(self,mode='form',forceNew=False,mVisLink = None):
    try:
        _plug = 'noTrans{0}Null'.format(STR.capFirst(mode[0]) + mode[1:])
        mNoTransformNull = self.getMessageAsMeta(_plug)
        if mNoTransformNull and not forceNew:
            return mNoTransformNull
        
        if forceNew and mNoTransformNull:
            mNoTransformNull.delete()
        
        str_prerigNull = mc.group(em=True)
        mNoTransformNull = cgmMeta.validateObjArg(str_prerigNull, mType = 'cgmObject',setClass = True)
        mNoTransformNull.connectParentNode(self, 'rigBlock',_plug) 
        mNoTransformNull.doStore('cgmName', self)
        mNoTransformNull.doStore('cgmType',_plug)
        mNoTransformNull.doName()
        
        if mVisLink:
            mNoTransformNull.doConnectIn('v',"{0}.v".format(mVisLink.mNode))

        mNoTransformNull.dagLock()
        #mNoTransformNull.p_parent = self.prerigNull
        #mNoTransformNull.resetAttrs()
        #mNoTransformNull.setAttrFlags()
        #mNoTransformNull.inheritsTransform = False

    
        return mNoTransformNull    
    except Exception as err:
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
    except Exception as err:
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

def prerig_delete(self, msgLinks = [], msgLists = [], formHandles = True):
    _str_func = 'prerig_delete'
    log.debug(cgmGEN.logString_start(_str_func))
    
    try:self.moduleTarget.delete()
    except:log.debug("|{0}| >> No moduleTarget...".format(_str_func))
    if self.getMessage('prerigNull'):
        self.prerigNull.delete()
    else:
        log.warning("No prerigNull found")
    if self.getMessage('noTransformNull'):
        self.noTransformNull.delete()
    if formHandles:
        for mHandle in [self] + self.msgList_get('formHandles'):
            try:mHandle.jointHelper.delete()
            except:pass    
    
    for l in msgLists:
        _buffer = self.msgList_get(l,asMeta=False)
        if not _buffer:
            log.debug("|{0}| >> Missing msgList: {1}".format(_str_func,l))  
        else:
            mc.delete(_buffer)
    return True   

        
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
                _const = mHandle.getConstraintsTo()
                if _const:
                    mc.delete(_const)
                mLoc = mHandle.getMessageAsMeta('lockLoc')
                if mLoc:
                    mLoc.delete()
        
        return True   
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)

def delete(self):
    _d_delete = {4:rigDelete,
                 3:skeleton_delete}
    _str_func = 'delete'
    log.debug(cgmGEN.logString_start(_str_func))

    _int_state,_state = BLOCKGEN.validate_stateArg(self.blockState)
    
    _range = list(range(_int_state+1))
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
        except Exception as err:
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
                except Exception as err:
                    log.error("|{0}| >>  Failed to delete: {1} | {2} | {3}".format(_str_func,l,l_dat,err))
                
    for l in d_wiring.get('msgLists',[]) + msgLists:
        if self.msgList_exists(l):
            dat = self.msgList_get(l,asMeta=1)
            if dat:
                log.debug("|{0}| >>  Purging msgList: {1} | {2}".format(_str_func, l, 0))
                for mObj in dat:
                    try:
                        mObj.delete()
                    except Exception as err:
                        log.error("|{0}| >>  Failed to delete msgList: {1} | {2}".format(_str_func,l,err))                
                #self.msgList_purge(l)
    return True

def msgDat_check(self,d_wiring = {}, msgLinks = [], msgLists = [] ):
    _str_func = 'msgDat_check'
    log.debug(cgmGEN.logString_start(_str_func))
    
    
    _l_missing = []
    _optional = d_wiring.get('optional',[])
    for l in d_wiring.get('msgLinks',[]) + msgLinks:
        if not self.getMessage(l):
            if l not in _optional:
                _l_missing.append('msgLink ' + self.p_nameBase + '.' + l)
        else:
            log.debug("|{0}| >>  Found msgLink: {1}".format(_str_func,l))
            
    for l in d_wiring.get('msgLists',[]) + msgLists:
        if not self.msgList_exists(l):
            if l not in _optional:
                _l_missing.append(self.p_nameBase + '.[msgList]' + l)
        else:
            log.debug("|{0}| >>  Found msgList: {1}".format(_str_func,l))
            
    if _l_missing:
        log.debug("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.debug("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True
    
def get_stateLinks(self, mode = 'form' ):
    try:
        _str_func = 'get_stateLinks'
        log.debug(cgmGEN.logString_start(_str_func))

        
        mBlockModule = self.p_blockModule
        log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
        d_wiring = {}
        try:
            d_wiring = CGMDICT.blendDat(d_wiring, getattr(mBlockModule,'d_wiring_{0}'.format(mode)))
            log.debug("|{0}| >>  Found {1} wiring dat in BlockModule".format(_str_func,mode))
        except Exception as err:
            log.debug("|{0}| >>  No {1} wiring dat in BlockModule. error: {2}".format(_str_func,mode,err))
            pass
        
        _noTrans = 'noTrans' + mode.capitalize() + 'Null'
        if _noTrans not in d_wiring and self.getMessage(_noTrans):
            if not d_wiring.get('msgLinks'):d_wiring['msgLinks'] = []            
            d_wiring['msgLinks'].append(_noTrans)
            
            
        for k,l in list(d_wiring.items()):
            d_wiring[k] = LISTS.get_noDuplicates(l)
            
        return d_wiring
        
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def is_prerig(self):
    try:
        _str_func = 'is_prerig'
        log.debug(cgmGEN.logString_start(_str_func))

        return msgDat_check(self, get_stateLinks(self,'prerig'))
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def is_skeleton(self):
    _str_func = 'is_skeleton'
    log.debug(cgmGEN.logString_start(_str_func))

    
    mBlockModule = self.p_blockModule

    if 'skeleton_check' in list(mBlockModule.__dict__.keys()):
        log.debug("|{0}| >> BlockModule skeleton_check call found...".format(_str_func))            
        return self.atBlockModule('skeleton_check')
    else:
        log.error("|{0}| >> Need skeleton_check for: {1}".format(_str_func,self.blockType))            
        
    return True
    

    #return False        
    
    return msgDat_check(self, get_stateLinks(self,'skeleton'))


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
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)


def get_castSize(self, casters, castMesh = None, axis1 = 'x', axis2 = 'y',extend = False):
    _str_func =  'get_castSize'
    log.debug(cgmGEN.logString_start(_str_func))
    
    
    ml_casters = cgmMeta.validateObjListArg(casters,'cgmObject')
    mMesh = None
    if not castMesh:
        mMesh = get_castMesh(self,extend)
        _surf = mMesh.mNode
        
    else:
        try:_surf = castMesh.mNode
        except:_surf = castMesh
        
    l_x = []
    l_y = []
    _res = []
    l_max = []
    l_min = []
    for mHandle in ml_casters:
        _mNode = mHandle.mNode
        try:xDist = RAYS.get_dist_from_cast_axis(_mNode,'x',shapes=_surf)
        except:
            xDist = None
        try:yDist = RAYS.get_dist_from_cast_axis(_mNode,'y',shapes=_surf)
        except:
            yDist = None
        
        if xDist is None and yDist is None:
            raise ValueError("Cast fail")
        if xDist is None:
            xDist = yDist
        if yDist is None:
            yDist = xDist
            
        l_x.append(xDist)
        l_y.append(yDist)
    
        l_box = [xDist,
                 yDist,
                 MATH.average(xDist,yDist)]
        l_max.append(max(l_box))
        l_min.append(min(l_box))
        _res.append(l_box)
        
    if mMesh:
        mMesh.delete()
    return {'bb':_res,
            'min':l_min,
            'max':l_max,
            axis1:l_x,
            axis2:l_y}
    
#@cgmGEN.Timer
def get_castMesh(self,extend=False,pivotEnd=False):
    _str_func =  'get_castMesh'
    log.debug(cgmGEN.logString_start(_str_func))
    ml_delete = []        
    
    if pivotEnd:
        #New override to make just a foot for casting
        l_targets = []
        ml_formHandles = self.msgList_get('formHandles')
        

        mHandle = ml_formHandles[-1]
        try:l_targets.append(mHandle.loftCurve.mNode)
        except:
            pass
        
        if mHandle.getMessage('pivotHelper'):
            mPivotHelper = ml_formHandles[-1].pivotHelper
            log.debug("|{0}| >> foot ".format(_str_func))


            mBaseCrv = mPivotHelper.doDuplicate(po=False)
            mBaseCrv.parent = False
            mShape2 = False
            ml_delete.append(mBaseCrv)
            
            mTopLoft = mPivotHelper.getMessageAsMeta('topLoft')
            if mTopLoft:
                mShape2 = mTopLoft.doDuplicate(po=False)
            
            if mShape2:
                mShape2.parent = False
                l_targets.append(mShape2.mNode)
                ml_delete.append(mShape2)                

            l_targets.append(mBaseCrv.mNode)        
        
        mesh = BUILDUTILS.create_loftMesh(l_targets, 
                                          name="{0}_pivotEnd_castMesh".format(self.p_nameBase),
                                          degree=1,divisions=1)
        
        for mObj in ml_delete:
            mObj.delete()
        return cgmMeta.asMeta(mesh)
        
    if extend and self.blockType not in ['handle','muzzle','brow','eye','facs']:
        log.debug(cgmGEN.logString_msg(_str_func,'extend'))
        ml_formHandles = self.msgList_get('formHandles')
        l_targets = []
        for mHandle in ml_formHandles:
            """
            if mHandle == ml_formHandles[0]:
                mLoft = mHandle.loftCurve
                mStartCollapse = mLoft.doDuplicate(po=False)
                mStartCollapse.scale = [.0001 for i in range(3)]
                l_targets.append(mStartCollapse.mNode)
                ml_delete.append(mStartCollapse)
                l_targets.append(mLoft.mNode)
                
                
            else:"""
            try:l_targets.append(mHandle.loftCurve.mNode)
            except:
                continue
            ml_sub = mHandle.msgList_get('subShapers')
            if ml_sub:
                for mSub in ml_sub:
                    l_targets.append(mSub.mNode)
            if mHandle == ml_formHandles[-1]:
                if mHandle.getMessage('pivotHelper') and self.blockProfile not in ['arm']:
                    mPivotHelper = ml_formHandles[-1].pivotHelper
                    log.debug("|{0}| >> foot ".format(_str_func))
        
        
                    mBaseCrv = mPivotHelper.doDuplicate(po=False)
                    mBaseCrv.parent = False
                    mShape2 = False
                    ml_delete.append(mBaseCrv)
                
                    mTopLoft = mPivotHelper.getMessageAsMeta('topLoft')
                    if mTopLoft:
                        mShape2 = mTopLoft.doDuplicate(po=False)
                    
                    if mShape2:
                        mShape2.parent = False
                        l_targets.append(mShape2.mNode)
                        ml_delete.append(mShape2)                
        
                    l_targets.append(mBaseCrv.mNode)
                    
        for v in [.9,.5,.0001]:
            mBaseCollapse = cgmMeta.asMeta(l_targets[-1]).doDuplicate(po=False)
            mBaseCollapse.p_parent = False
            mBaseCollapse.scale = [v* vScale for vScale in mBaseCollapse.scale]
            l_targets.append(mBaseCollapse.mNode)
            ml_delete.append(mBaseCollapse)
        
        if self.blockType == 'head':
            uAttr = 'neckControls'
        else:
            uAttr = 'numControls'
            
        mMesh = create_prerigLoftMesh(
            self,
            l_targets,
            None,
            uAttr,
            'loftSplit',
            polyType='bezier',
            justMesh = True,
            baseName = self.cgmName)
    else:
        mMesh = self.getMessage('prerigLoftMesh', asMeta = True)[0].doDuplicate(po=False)
        
    mRebuildNode = mMesh.getMessage('rebuildNode',asMeta=True)[0]
        
    _rebuildState = mRebuildNode.rebuildType
    if _rebuildState != 5:
        mRebuildNode.rebuildType = 5
        
    mCastMesh =  cgmMeta.validateObjArg(mMesh.mNode,'cgmObject').doDuplicate(po=False,ic=False)
    mRebuildNode.rebuildType = _rebuildState
    mCastMesh.parent=False
    
    if extend:
        mMesh.delete()

    for mObj in ml_delete:
        mObj.delete()
        
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
        
        
                
        _res_body = mc.loft(targets, o = True, d = 1, po = 3, c = False,autoReverse=0,ch=True)
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
        CORERIG.colorControl(mLoftSurface.mNode,_side,'sub',transparent = True)
        #self.asHandleFactory().color(mLoftSurface.mNode,_sice)
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
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def create_prerigLoftMesh(self, targets = None,
                          mPrerigNull = None,
                          uAttr = 'neckControls',
                          uAttr2 = 'loftSplit',
                          vAttr = 'loftSides',
                          degreeAttr = None,
                          polyType = 'mesh',
                          justMesh = False,
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
        
            for a,v in list(_d.items()):
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
        
            for a,v in list(_d.items()):
                ATTR.set(_rebuildNode,a,v)
                
        else:
            _res_body = mc.loft(targets, o = True, d = 3, po = 0,autoReverse=False)
            _loftNode = _res_body[1]
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)        
            
        
        mLoftSurface.overrideEnabled = 1
        mLoftSurface.overrideDisplayType = 2
        
        if mPrerigNull:
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
        #CORERIG.colorControl(mLoftSurface.mNode,_side,'main',transparent = True)
        mHandleFactory = self.asHandleFactory()
        mHandleFactory.color(mLoftSurface.mNode,_side,'sub',transparent=True)
    
        mLoftSurface.inheritsTransform = 0
        for s in mLoftSurface.getShapes(asMeta=True):
            s.overrideDisplayType = 2    
        
        log.debug("|{0}| >> Linear/Cubic...".format(_str_func))        
        if polyType in ['bezier','noMult']:
            
            _arg = "{0}.out_degreeBez = if {1} == 0:1 else 3".format(targets[0],
                                                                     self.getMayaAttrString('loftDegree','short'))
            NODEFACTORY.argsToNodes(_arg).doBuild()
            ATTR.connect("{0}.out_degreeBez".format(targets[0]), "{0}.degreeU".format(_rebuildNode))
            if polyType == 'bezier':
                ATTR.set(_rebuildNode,'degreeV',1)
                ATTR.set(_rebuildNode,'keepControlPoints',1)
            else:
                ATTR.connect("{0}.out_degreeBez".format(targets[0]), "{0}.degreeV".format(_rebuildNode))
            
            _arg = "{0}.out_degreePre = if {1} == 0:1 else 3".format(targets[0],
                                                                  self.getMayaAttrString('loftDegree','short'))
            
        if polyType in ['noMult']:
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
                
        if not justMesh:
            for n in toName:
                mObj = cgmMeta.validateObjArg(n)
                mObj.doStore('cgmName',self)
                mObj.doStore('cgmTypeModifier','prerigMesh')
                mObj.doName()                        
           
            self.connectChildNode(mLoftSurface.mNode, 'prerigLoftMesh', 'block')
        
        return mLoftSurface
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def create_simpleFormLoftMesh(self, targets = None,
                                  mNull = None,
                                  uAttr = 'loftSplit',
                                  degreeAttr = 'loftDegree',
                                  polyType = 'mesh',
                                  plug = None,
                                  baseName = None,
                                  noReverse = False,
                                  transparent = True,
                                  d_rebuild = {},
                                  uDriver = None,
                                  vDriver = None,
                                  **kws
                                  ):
    try:
        _str_func = 'create_prerigLoftMesh'
        log.debug(cgmGEN.logString_start(_str_func))
        
        if self.getMayaAttr('isBlockFrame'):
            log.debug(cgmGEN.logString_sub(_str_func,'blockFrame bypass'))
            return                    

        _short = self.mNode
        _side = 'center'
        _rebuildNode = None
        _loftNode = None
        _b_noReverse = VALID.boolArg(noReverse)
        _plug = plug or baseName+'FormLoft'
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
        
            for a,v in list(_d.items()):
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
        
            for a,v in list(_d.items()):
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
            
            for a,v in list(_d.items()):
                ATTR.set(_rebuildNode,a,v)
                
            toName = [_loftNode]
            
        elif polyType == 'faceNurbsLoft':
            _res_body = mc.loft(targets, o = True, d = 1, po = 0, c = False,autoReverse=False)
            mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)                    
            _loftNode = _res_body[1]
            #_inputs = mc.listHistory(mLoftSurface.mNode,pruneDagObjects=True)
            #_rebuildNode = _inputs[0]
            
            #rebuildSurface -ch 1 -rpo 1 -rt 0 -end 1 -kr 0 -kcp 0 -kc 0 -su 4 -du 3 -sv 4 -dv 3 -tol 0.01 -fr 0  -dir 2 "jaw_shapeApprox";
            
            _rebuildNode = mc.rebuildSurface(mLoftSurface.mNode,
                                             ch=1, rpo=1, rt=0,end=1,kr=0,kcp=0,kc=0,
                                             su=4,du=3,sv=4,dv=3,tol=0.01,
                                             fr=0,dir =2)[1]
            
            #mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
            
            if kws.get('noRebuild') is not True and _b_noReverse is not True:
                mc.reverseSurface(mLoftSurface.mNode, direction=1,rpo=True)
            
            _len = len(targets)*2
            _d = {
                'keepCorners':False,
                  'rebuildType':0,
                  'degreeU':1,
                  'degreeV':3,
                  'keepControlPoints':False,
                  'spansU':_len,
                  'spansV':_len}#General}
            _d.update(d_rebuild)
            
            for a,v in list(_d.items()):
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
        CORERIG.colorControl(mLoftSurface.mNode,_side,'main',transparent = transparent)
    
        mLoftSurface.inheritsTransform = 0
        for s in mLoftSurface.getShapes(asMeta=True):
            s.overrideDisplayType = 2    
        
        if polyType not in ['faceLoft','faceNurbsLoft']:
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
                
            if uDriver:
                ATTR.connect(uDriver, "{0}.spansU".format(_rebuildNode))
            if vDriver:
                ATTR.connect(vDriver, "{0}.spansV".format(_rebuildNode))
                
                

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
    except Exception as err:
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
    _d = {'format':3,#1,#fit, 2 - #General
          'polygonType':1,#'quads',
          'uNumber': baseCount + len(targets)}

    for a,v in list(_d.items()):
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
            raise ValueError("Referenced node.")
        
        _str_state =  _mBlock.getEnumValueString('blockState')
    
        if _str_state != 'rig':
            raise ValueError("{0} is not in rig state. state: {1}".format(_str_func, _str_state))
    
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
    
    
    
        if 'rigDelete' in list(_mBlockModule.__dict__.keys()):
            log.debug("|{0}| >> BlockModule rigDelete call found...".format(_str_func))            
            _mBlockModule.rigDelete(self)        
    
    
        self.blockState = 'prerig'
        
        
        for link in msgLinks + ['rigNull']:
            if self.getMessage(link):
                log.debug("|{0}| >> deleting link: {1}".format(_str_func,link))                        
                mc.delete(self.getMessage(link))
                
        return True
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)

"""
l_pivotOrder = ['center','back','front','left','right']
d_pivotBankNames = {'default':{'left':'outer','right':'inner'},
                    'right':{'left':'inner','right':'outer'}}"""

l_pivotOrder = BLOCKSHARE._l_pivotOrder
d_pivotBankNames = BLOCKSHARE._d_pivotBankNames

#@cgmGEN.Timer
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
            raise ValueError("|{0}| >> No pivots helper found. mBlock: {1}".format(_str_func,self))
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

#@cgmGEN.Timer
def pivots_setup(self, mControl = None,
                 mRigNull = None,
                 mBallJoint = None,
                 mBallWiggleJoint = None,
                 mToeJoint = None,
                 jointOrientation = 'zyx',
                 pivotResult = None,
                 mDag = None,
                 rollSetup = 'default',
                 l_pivotOrder = l_pivotOrder,
                 setup = 'default',
                 setupWobble = False,
                 setupSpin = True,
                 **kws):
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
                
                    _str = NAMETOOLS.get_combinedNameDict(mControl.mNode,['cgmType','cgmTypeModifier'])
                    mPivot.doStore('cgmNameModifier',_str)
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
        raise ValueError("|{0}| >> No pivots found. mBlock: {1}".format(_str_func,self))
    
    #pprint.pprint(vars())
    
    
    
    #Logic ======================================================================================
    if setup == 'default':
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
        if setupSpin:
            d_mPlugSpin = {}
            for k in list(d_drivenGroups.keys()):
                d_mPlugSpin[k] = cgmMeta.cgmAttr(mControl,'spin{0}'.format(d_strCaps[k]),attrType='float',defaultValue = 0,keyable = True)
                
            for k in list(d_drivenGroups.keys()):
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
    
    if setupWobble:
        mDriven = d_drivenGroups['tilt']
        mSpin = d_pivots['spin']
        mDriven.p_position = d_pivots['center'].p_position
        d_pivots['center'].masterGroup.p_position = mDriven.p_position
        
        arg1 = "{}.ry = {}.ry * -1.0".format(mDriven.p_nameShort,
                                             mSpin.p_nameShort)        
        for arg in [arg1]:
            NODEFACTORY.argsToNodes(arg).doBuild()
            
        mSpin.dagLock(ignore='ry')
            
        #Inner spin --------------------------------------------------------
        mInnerSpinGroup = mDriven.doGroup(False, False, asMeta=True)
        mInnerSpinGroup.addAttr('cgmType','innerSpin')
                
        mInnerSpinGroup.doName()
        mInnerSpinGroup.parent = mDriven
        
        mLastParent = mInnerSpinGroup        
        
        mPlug = cgmMeta.cgmAttr(d_pivots['tilt'],'innerSpin',attrType='float',defaultValue = 0,keyable = True)
            

        if _side in ['right']:# and k not in ['inner','outer']:
            str_arg = "{0}.ry = -{1}".format(mInnerSpinGroup.mNode,
                                             mPlug.p_combinedShortName)
            log.debug("|{0}| >> Spin Right arg: {1}".format(_str_func,str_arg))        
            NODEFACTORY.argsToNodes(str_arg).doBuild()
        else:
            mPlug.doConnectOut("{0}.ry".format(mInnerSpinGroup.mNode))           
            
        
            
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
    
    for s in 'cgmDirection','cgmPosition':
        _val = mModule.getMayaAttr(s)
        if _val and _val not in ['none','None','False']:
            _nameDict[s] = _val    
    """
    if mModule.getMayaAttr('cgmDirection'):
        _nameDict['cgmDirection'] = [mModule.mNode,'cgmDirection']
    if mModule.getMayaAttr('cgmPosition'):
        _nameDict['cgmPosition'] = [mModule.mNode,'cgmPosition']"""
    
    if self.getMayaAttr('nameIter'):
        _nameDict['cgmName'] = [_short,'nameIter']
    elif self.getMayaAttr('cgmName'):
        _nameDict['cgmName'] = [_short,'cgmName']
    else:
        _nameDict['cgmName'] = [_short,'blockType']
    
    _nameDict['cgmType'] = 'preHandle'
    
    for a,v in list(kws.items()):
        _nameDict[a] = v    
    
    _cnt = 0
    l_range = list(range(count))
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
                for k,v in list(_dict.items()):
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
    
    
    for s in 'cgmDirection','cgmPosition':
        _val = self.getMayaAttr(s)
        if _val and _val not in ['none','None','False']:
            _nameDict[s] = _val
    """
    if mModule.getMayaAttr('cgmDirection'):
        _nameDict['cgmDirection'] = mModule.cgmDirection
    if mModule.getMayaAttr('cgmPosition'):
        _pos = mModule.cgmPosition
        if _pos and _pos not in ['none','None','False']:
            _nameDict['cgmPosition']=mModule.cgmPosition"""
        
    _nameDict['cgmType'] = 'joint'
    
    return _nameDict

    
def skeleton_getNameDicts(self, combined = False, count = None, iterName= None, cgmType = None, **kws):
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
    
    for s in 'cgmDirection','cgmPosition':
        _val = mModule.getMayaAttr(s)
        if _val and _val not in ['none','None','False']:
            _nameDict[s] = _val
    """
    if mModule.getMayaAttr('cgmDirection'):
        _nameDict['cgmDirection'] = mModule.cgmDirection
    if mModule.getMayaAttr('cgmPosition'):
        _pos = mModule.cgmPosition
        if _pos and _pos not in ['none','None','False']:
            _nameDict['cgmPosition']=mModule.cgmPosition"""
            
    if iterName:
        log.debug("|{0}| >>  iterName: {1}".format(_str_func,iterName))        
        _nameDict['cgmName'] = iterName
    elif self.getMayaAttr('nameIter'):
        _nameDict['cgmName'] = self.nameIter
    elif self.getMayaAttr('cgmName'):
        _nameDict['cgmName'] = self.cgmName
    else:
        _nameDict['cgmName'] = self.blockType
        
    if cgmType:
        _nameDict['cgmType'] = cgmType
    else:
        _nameDict['cgmType'] = 'skinJoint'
    
    
    for a,v in list(kws.items()):
        _nameDict[a] = v
    
    log.debug("|{0}| >>  baseDict: {1}".format(_str_func,_nameDict))

    _cnt = 0
    l_range = list(range(_number))
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
            raise ValueError("No rigHandles. Check your state")            
    
        #_ml_controls = [self] + _ml_rigHandles
    
        for i,mObj in enumerate(_ml_rigHandles):
            log.debug("|{0}| >>  {1} | {2}".format(_str_func,i,mObj.mNode))
            if mObj.getMessage('jointHelper'):
                _l_targets.append(mObj.jointHelper.mNode)
            else:
                _l_targets.append(mObj.mNode)        
    else:
        raise ValueError("targetsMode: {0} is not implemented".format(_targetsMode))
    
    if not _l_targets:
        log.error("|{0}| >> mode: {1} | targetsMode: {2} | targetsCall: {3}".format(_str_func,_mode,_targetsMode,_targetsCall))
        raise ValueError("No targets found. Check your settings")
    
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
        raise ValueError("mode: {0} is not implemented".format(_mode))                

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
                raise ValueError("mParentModule has no module joints.")
            _attachPoint = ATTR.get_enumValueString(self.mNode,'attachPoint')
            if _attachPoint == 'end':
                mTargetJoint = ml_targetJoints[-1]
            elif _attachPoint == 'base':
                mTargetJoint = ml_targetJoints[0]
            elif _attachPoint == 'closest':
                jnt = DIST.get_closestTarget(ml_moduleJoints[0].mNode, [mObj.mNode for mObj in ml_targetJoints])
                mTargetJoint = cgmMeta.asMeta(jnt)
            elif _attachPoint == 'index':
                idx = self.attachIndex
                mTargetJoint = ml_targetJoints[idx]                
            else:
                raise ValueError("Not done with {0}".format(_attachPoint))
            return mTargetJoint

    return False

def skeleton_connectToParent(self):
    _str_func = 'skeleton_connectToParent'
    log.debug(cgmGEN.logString_start(_str_func))

    
    if self.blockType in ['master','eyeMain']:
        log.debug("|{0}| >> {1} block type. No connection possible".format(_str_func,self.blockType))                   
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
                ml_moduleJoints[0].p_parent = mParentModule.masterNull.skeletonGroup
                return True
        else:
            ml_targetJoints = mParentModule.rigNull.msgList_get('moduleJoints',asMeta = True, cull = True)
            if not ml_targetJoints:
                raise ValueError("mParentModule has no module joints.")
            _attachPoint = ATTR.get_enumValueString(self.mNode,'attachPoint')
            if _attachPoint == 'end':
                mTargetJoint = ml_targetJoints[-1]
            elif _attachPoint == 'base':
                mTargetJoint = ml_targetJoints[0]
            elif _attachPoint == 'closest':
                jnt = DIST.get_closestTarget(ml_moduleJoints[0].mNode, [mObj.mNode for mObj in ml_targetJoints])
                mTargetJoint = cgmMeta.asMeta(jnt)
            elif _attachPoint == 'index':
                idx = self.attachIndex
                mTargetJoint = ml_targetJoints[idx]
            else:
                raise ValueError("Not done with {0}".format(_attachPoint))
            ml_moduleJoints[0].p_parent = mTargetJoint

    return True

def skeleton_buildRigChain(self):
    _short = self.mNode
    _str_func = 'skeleton_buildRigChain ( {0} )'.format(_short)
    start = time.time()	
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
    log.debug("%s >> Time >> = %0.3f seconds " % (_str_func,(time.time()-start)) + "-"*75)	
    
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
                for k,v in list(_preferredAxis.items()):
                    _idx = _l_axisAlias.index(k)
                    #if side.lower() == 'right':#negative value
                        #mJnt.__setattr__('preferredAngle{0}'.format(orientation[_idx].upper()),-v)				
                    #else:
                    mJnt.__setattr__('preferredAngle{0}'.format(orientation[_idx].upper()),v)                
                
            if _limitBuffer:
                log.debug("|{0}| >> found limit data on {1}:{2}".format(_str_func,_key,_limitBuffer))              
                raise Exception("Limit Buffer not implemented")
    except Exception as err:
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
    #start = time.time()	
    log.debug(cgmGEN.logString_start(_str_func))
    
    mRigNull = self.moduleTarget.rigNull
    ml_fkJoints = mRigNull.msgList_get('fkJoints')
    
    if not ml_fkJoints:
        log.debug("|{0}| >> Generating handleJoints".format(_str_func))
        
        ml_formHandles = self.msgList_get('formHandles',asMeta = True)
        if not ml_formHandles:
            raise ValueError("No formHandles connected")        
        
        ml_prerigHandles = self.msgList_get('prerigHandles',asMeta = True)
        if not ml_prerigHandles:
            raise ValueError("No prerigHandles connected")
        
        if mOrientHelper is None:
            mOrientHelper = ml_formHandles[0].orientHelper or ml_prerigHandles[0].orientHelper
            
        #_d = skeleton_getCreateDict(self)
        #pprint.pprint(_d)
        l_pos = []
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
        
    #log.debug("%s >> Time >> = %0.3f seconds " % (_str_func,(time.time()-start)) + "-"*75)	
    return ml_fkJoints


def skeleton_buildHandleChain(self,typeModifier = 'handle', connectNodesAs = False,clearType = False,mOrientHelper=None): 
    _short = self.mNode
    _str_func = 'skeleton_buildHandleChain [{0}]'.format(_short)
    #start = time.time()
    
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

    if connectNodesAs and type(connectNodesAs) in [str,str]:
        self.moduleTarget.rigNull.msgList_connect(connectNodesAs,ml_handleChain,'rigNull')#Push back

    #log.debug("%s >> Time >> = %0.3f seconds " % (_str_func,(time.time()-start)) + "-"*75)
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
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

                    
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

            
        for k,l in list(md.items()):
            _len_type = len(l)
            print(("|{0}| >>  Type: {1} ...".format(_str_func,k)+'-'*60))
            d_counts[k] = _len_type
            for i,mNode in enumerate(l):
                print(("{0} | {1}".format(i,mNode)))
                
        log.debug(cgmGEN._str_subLine)
        _sort = list(d_counts.keys())
        _sort.sort()
        for k in _sort:
            print(("|{0}| >>  {1} : {2}".format(_str_func,k,d_counts[k])))
        #print("|{0}| >>  Fails to initialize : {1}".format(_str_func,len(l_fails)))
        #for i,n in enumerate(l_fails):
        #    print("{0} | {1}".format(i,n))            
        print(("|{0}| >>  Total: {1} | {2}".format(_str_func,_len,self)))
        log.debug(cgmGEN._str_hardLine)
    return _res



def prerig_getHandleTargets(self):
    """
    
    """
    _short = self.mNode
    _str_func = 'prerig_getHandleTargets [{0}]'.format(_short)
    start = time.time()
    
    ml_handles = self.msgList_get('prerigHandles',asMeta = True)
    if not ml_handles:
        raise ValueError("No prerigHandles connected")
    
    for i,mHandle in enumerate(ml_handles):
        if mHandle.getMessage('jointHelper'):
            log.debug("|{0}| >> Found jointHelper on : {1}".format(_str_func, mHandle.mNode))                    
            ml_handles[i] = mHandle.jointHelper
            
    log.debug("%s >> Time >> = %0.3f seconds " % (_str_func,(time.time()-start)) + "-"*75)	
    return ml_handles


#=============================================================================================================
#>> blockParent
#=============================================================================================================
def blockParent_set(self, parent = False, attachPoint = None, setBuildProfile = False):
    try:
        _str_func = 'blockParent_set'
        log.debug(cgmGEN.logString_start(_str_func))
    
        
        mParent_current =  self.blockParent
        _str_state = self.getEnumValueString('blockState')
        if _str_state == 'rig':
            raise ValueError("Cannot change the block parent of a rigged rigBlock. State: {0} | rigBlock: {1}".format(_str_state,self))
        
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
                raise ValueError("Invalid blockParent. Not a cgmRigBlock. parent: {0}".format( cgmMeta.asMeta(parent)))
            
            if parent == self:
                raise ValueError("Cannot blockParent to self")
    
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
            if setBuildProfile and mParent.hasAttr('buildProfile'):
                log.debug("|{0}| >>  buildProfile_load...".format(_str_func))
                self.atUtils('buildProfile_load', mParent.getMayaAttr('buildProfile'))
    except Exception as err:
        cgmGEN.cgmException(Exception,err)

def siblings_get(self,matchType = False, matchProfile = False, excludeSelf = True, matchName=False):
    _str_func = 'siblings_get'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)

    d = {}
    if matchType:
        d['blockType'] = self.blockType
    if matchProfile:
        d['blockProfile'] = self.blockProfile
    if matchName:
        d['cgmName'] = self.cgmName


    mBlockParent  = self.getMessage('blockParent',asMeta=True)
    log.debug("|{0}| >> mBlockParent: {1}".format(_str_func,mBlockParent))
    if not mBlockParent:
        return False
    
    ml_match = []
    ml_children = mBlockParent[0].getBlockChildren()
    
    for mChild in ml_children:
        log.debug("|{0}| >> mChild: {1}".format(_str_func,mChild))        
        _match = True
        for a,v in list(d.items()):
            if not str(mChild.getMayaAttr(a)) == str(v):
                _match = False
                continue
        if not mChild.blockParent == mBlockParent[0]:
            _match = False
            continue
        if _match:ml_match.append(mChild)
    
    if excludeSelf:
        ml_match.remove(self)
    
    #pprint.pprint(ml_match)
    return ml_match

def siblings_pushSubShapers(self,matchType=True,matchProfile=True):
    _str_func = 'siblings_pushSubShapers'
    
    ml_siblings = siblings_get(self, matchType,matchProfile)
    if not ml_siblings:
        return 
    
    ml_source = form_getSubShapers(self)
    if not ml_source:
        return log.warning("|{0}| >> Block settings...".format(_str_func))
    
    l = []
    for mHandle in ml_source:
        d = {}
        for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            d[a]= mHandle.getMayaAttr(a)
        l.append(d)
    
    #pprint.pprint(l)
    
    for mSib in ml_siblings:
        log.info(cgmGEN.logString_msg(_str_func,mSib))
        ml_shapers = form_getSubShapers(mSib)
        for i,mHandle in enumerate(ml_shapers):
            for a,v in list(l[i].items()):
                mHandle.setMayaAttr(a,v)
                
def siblings_pushFormHandles(self,matchType=True,matchProfile=True):
    _str_func = 'siblings_pushFormHandles'
    
    ml_siblings = siblings_get(self, matchType,matchProfile)
    if not ml_siblings:
        return 
    
    ml_source = self.msgList_get('formHandles')
    if not ml_source:
        return log.warning("|{0}| >> No form handles...".format(_str_func))
    
    l = []
    for mHandle in ml_source:
        d = {}
        for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            d[a]= mHandle.getMayaAttr(a)
        l.append(d)
    
    #pprint.pprint(l)
    
    for mSib in ml_siblings:
        log.info(cgmGEN.logString_msg(_str_func,mSib))
        ml_shapers = mSib.msgList_get('formHandles')
        for i,mHandle in enumerate(ml_shapers):
            for a,v in list(l[i].items()):
                mHandle.setMayaAttr(a,v)
        
def siblings_pushPrerigHandles(self,matchType=True,matchProfile=True):
    _str_func = 'siblings_pushPrerigHandles'
    
    ml_siblings = siblings_get(self, matchType,matchProfile)
    if not ml_siblings:
        return 
    
    ml_source = self.msgList_get('prerigHandles',asMeta = True)
    if not ml_source:
        return log.warning("|{0}| >> Block settings...".format(_str_func))
    
    l = []
    for mHandle in ml_source:
        d = {}
        for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            d[a]= mHandle.getMayaAttr(a)
        l.append(d)
    
    #pprint.pprint(l)
    
    for mSib in ml_siblings:
        log.info(cgmGEN.logString_msg(_str_func,mSib))
        ml_shapers = mSib.msgList_get('prerigHandles',asMeta = True)
        for i,mHandle in enumerate(ml_shapers):
            for a,v in list(l[i].items()):
                mHandle.setMayaAttr(a,v)
    
    

def form_getSubShapers(self):
    ml_formHandles = self.msgList_get('formHandles')
    ml = []
    for mHandle in ml_formHandles:
        mLoft = mHandle.getMessageAsMeta('loftCurve')
        if mLoft:
            ml.append(mLoft)
        ml_sub = mHandle.msgList_get('subShapers')
        if ml_sub:
            ml.extend(ml_sub)
    return ml

def form_snapHandlesToParam(self):
    for mHandle in self.msgList_get('formHandle') + form_getSubShapers(self):
        log.info(mHandle)
        mTrack = mHandle.getMessageAsMeta('trackCurve')
        print(mTrack)
        if mHandle.hasAttr('param') and mTrack:
            log.info('...')
            param = CURVES.getUParamOnCurve(mHandle.mNode, mTrack.mNode)
            mShape = mTrack.getShapes(asMeta=1)[0]
            _minU = mShape.minValue
            _maxU = mShape.maxValue
            pct = MATH.get_normalized_parameter(_minU,_maxU,param)
            
            pos = mHandle.p_position
            
            mHandle.param = pct
            mHandle.p_position = pos
            
    
    
#=============================================================================================================
#>> Mirror/Duplicate
#=============================================================================================================
def duplicate2(self):
    """
    Call to duplicate a block module and load data
    """
    try:
        _str_func = 'blockDuplicate'
        mDup = cgmMeta.createMetaNode('cgmRigBlock',blockType = self.blockType, autoForm=False)
        mDup.loadBlockDat(self.getBlockDat())
        mDup.doName()
        return mDup
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    
def duplicate(self, uiPrompt = True):
    """
    Call to duplicate a block module and load data
    """
    try:
        _str_func = 'duplicate'
        _blockType = self.blockType
        _side = get_side(self)
        _nameOriginal = self.cgmName
        
        _d = {'blockType':self.blockType,
              'autoForm':False,
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
        """
        if replaceSelf:
            ml_children = self.getBlockChildren()
            _blockProfile = self.getMayaAttr('blockProfile')
            mBlockModule = self.p_blockModule
            
            _d_profiles = {}        
            try:_d_profiles = mBlockModule.d_block_profiles
            except:
                log.error(cgmGEN.logString_msg(_str_func,'No d_block_profile_found'))            
            
            _typeDict=  _d_profiles.get(_blockProfile,{})
            if _blockProfile and not _typeDict:
                log.error(cgmGEN.logString_msg(_str_func,'blockType not found in blockProfiles. Please fix | found {0}'.format(_blockProfile)))
                pprint.pprint(_d_profiles.keys())
                return False        
            
            _baseDat = _typeDict.get('baseDat')"""
            
        mDup = cgmMeta.createMetaNode('cgmRigBlock',
                                      **_d)
        
        mDup.doSnapTo(self)
        
        blockDat = self.getBlockDat()
        
        blockDat['baseName'] = _v
        blockDat['ud']['cgmName'] = _v
        
        if _d['blockType'] in ['finger','thumb']:
            log.debug("|{0}| >> Clearing nameList".format(_str_func))
            for a in list(blockDat['ud'].items()):
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
        """
        if replaceSelf:
            if _baseDat:
                log.warning(cgmGEN.logString_msg(_str_func,'resetting baseDat: {0}'.format(_baseDat)))
                mDup.baseDat = _baseDat """                       
        
        for a in ['numSubShapers','rollCount']:
            if ATTR.datList_exists(self.mNode, a):
                l = self.datList_get(a)
                mDup.datList_connect(a,l)
                
                
        l_nameList = mDup.datList_get('nameList')
        for i,n in enumerate(l_nameList):
            if _nameOriginal in n:
                l_nameList[i] = n.replace(_nameOriginal,_d['name'])
                
        mDup.datList_connect('nameList',l_nameList)
        pprint.pprint(l_nameList)                
        
        
        blockDat_load(mDup,redefine=True)
        #log.debug('here...')
        #blockDat_load(mDup)#...investigate why we need two...
        
        #mDup.p_blockParent = self.p_blockParent
        #self.connectChildNode(mMirror,'blockMirror','blockMirror')#Connect    
        """
        if replaceSelf:
            for mChild in ml_children:
                mChild.p_blockParent = mDup
                
            self.delete()"""
        

            
        return mDup
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    
    
    
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
        if mBlockParent and mBlockParent.getMessage('blockMirror'):
            mBlockParent = mBlockParent.blockMirror
            log.debug("|{0}| >>  blockParent has blockMirror: {1}".format(_str_func,mBlockParent))
            
        log.debug("|{0}| >> Creating mirror block. {1} | {2}".format(_str_func, _blockType, _side))
        
        _d = {'blockType':self.blockType, 'side':_side,
              'autoForm':False,
              'blockParent':mBlockParent,
              
              #'baseAim':[self.baseAimX,-self.baseAimY,self.baseAimZ],
              'baseSize':baseSize_get(self)}
        
        for a in 'blockProfile','buildProfile','cgmName':
            if a in ['cgmName']:
                _d['name'] =  self.getMayaAttr(a)
            else:
                _d[a] =  self.getMayaAttr(a)

        
        log.debug("|{0}| >> Block settings...".format(_str_func, self.mNode))                    
        #pprint.pprint(_d)
        
        mMirror = cgmMeta.createMetaNode('cgmRigBlock',
                                         **_d)
        
        
        
        blockDat = self.getBlockDat()
        blockDat['ud']['side'] = _side
        for k in ['baseSize','baseAim']:
            if k in blockDat['ud']:
                blockDat['ud'].pop(k)
            for a in 'XYZ':
                if k+a in blockDat['ud']:
                    blockDat['ud'].pop(k+a)
        mMirror.blockDat = blockDat
        
        blockMirror_settings(self,mMirror)
        mMirror.saveBlockDat()
        _d = mMirror.blockDat
        _d['blockState']=self.getEnumValueString('blockState')

        mMirror.blockDat = _d
        
        """
        for k,dIter in BLOCKSHARE._d_mirrorAttrCheck.iteritems():
            _check = blockDat['ud'].get(k)
            if _check:
                log.debug("|{0}| >> mirror dat check {1} | {2}".format(_str_func, k, dIter))
                blockDat['ud'][k] = dIter.get(blockDat['ud'][k])"""
        
        """
        #Mirror some specfic dat
        if blockDat.get('form'):
            _subShapers = blockDat['form'].get('subShapers',{})
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
            

        self.connectChildNode(mMirror,'blockMirror','blockMirror')#Connect
        mMirror.p_blockParent = mBlockParent
        
        blockDat_load(mMirror,useMirror=True,redefine=True)
        controls_mirror(self,mMirror)
        return mMirror
    except Exception as err:cgmGEN.cgmException(Exception,err)
    
def blockMirror_go(self, mode = 'push',autoCreate = False,define=True,form = True, prerig= True):
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
        
        kws = {'define':True,'form':True, "prerig":True,}
        
        if mode == 'push':
            controls_mirror(self,mMirror,**kws)
        else:
            controls_mirror(mMirror,self,**kws)

        return mMirror
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)

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
            raise ValueError("|{0}| >> No ud data found".format(_str_func))
        
        _ud['baseSize'] = baseSize_get(mSource)
        
        """
        for k,dIter in BLOCKSHARE._d_mirrorAttrCheck.iteritems():
            _check = _ud.get(k)
            if _check:
                log.debug("|{0}| >> mirror dat check {1} | {2}".format(_str_func, k, dIter))
                blockDat['ud'][k] = dIter.get(blockDat['ud'][k])        
                _l_done.append(k)"""
        
                
        _mask = ['side','version','blockState','baseAim','baseAimY','cgmDirection','castVector']
        for a,v in list(_ud.items()):
            if a in _mask or a in _l_done:
                continue
            _type = ATTR.get_type(_short,a)
            
            if VALID.stringArg(v):
                #log.debug("string...")
                if a == 'castVector':
                    if v.startswith('out'):
                        if v.endswith('Neg'):
                            v = str(v).replace('Neg','')
                            log.debug("{0} | Neg > Pos".format(v))
                        else:
                            log.debug("{0} | Pos > Neg".format(v))
                            v = v + 'Neg'                  
                else:
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
                except Exception as err:
                    _udFail[a] = v
                    log.error("|{0}| >> userDefined '{1}' failed to change. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                    #r9Meta.printMetaCacheRegistry()                
                    for arg in err.args:
                        log.error(arg)
                        
                        
        for s in ['nameList','rollCount','numSubShapers']:
            _dat = ATTR.datList_get(mSource.mNode,s)
            if _dat:
                ATTR.datList_connect(mTarget.mNode, s, _dat)
                
            
        """
        #nameList 
        _nameList = ATTR.datList_get(mSource.mNode,'nameList')
        ATTR.datList_connect(mTarget.mNode, 'nameList', _nameList)
        
        #rollCount 
        _rollCount = ATTR.datList_get(mSource.mNode,'rollCount')
        if _rollCount:
            ATTR.datList_connect(mTarget.mNode, 'rollCount', _rollCount)        
        """
        
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
            raise ValueError("|{0}| >> No ud data found".format(_str_func))
        
        for a,v in list(_ud.items()):
            _current = ATTR.get(_short,a)
            if _current != v:
                try:
                    if ATTR.get_type(_short,a) in ['message']:
                        log.debug("|{0}| >> userDefined '{1}' skipped. Not loading message data".format(_str_func,a))                     
                    else:
                        log.debug("|{0}| >> userDefined '{1}' mismatch. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                        ATTR.set(_short,a,v)
                except Exception as err:
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

    if 'mirror_self' in list(mBlockModule.__dict__.keys()):
        log.debug("|{0}| >> BlockModule mirror_self call found...".format(_str_func))
        #reload(mBlockModule)
        mBlockModule.mirror_self(self,primeAxis)
        return True
    return log.error("No mirror self call found: {0}".format(self))
    
def mirror_blockDat(self = None, mirrorBlock = None, reflectionVector = MATH.Vector3(1,0,0) ):
    try:
        '''Mirrors the form positions from the block to the mirrorBlock across the reflection vector transformed from the root block'''
        _str_func = 'MirrorBlock'

        if not self or not mirrorBlock:
            log.warning("|{0}| >> Must have rootBlock and mirror block".format(_str_func))                                            
            return

        if mirrorBlock.blockType != self.blockType:
            log.warning("|{0}| >> Blocktypes must match. | {1} != {2}".format(_str_func,block.blockType,mirrorBlock.blockType,))                                                        
            return

        rootTransform = self
        rootReflectionVector = TRANS.transformDirection(rootTransform,reflectionVector).normalized()
        #rootReflectionVector = rootTransform.formPositions[0].TransformDirection(reflectionVector).normalized()

        print(("|{0}| >> Root: {1}".format(_str_func, rootTransform.p_nameShort)))                                            


        if mirrorBlock:
            print(("|{0}| >> Target: {1} ...".format(_str_func, mirrorBlock.p_nameShort)))

            _blockState = rootBlock.blockState
            _mirrorState = mirrorBlock.blockState
            if _blockState > _mirrorState or _blockState < _mirrorState:
                print(("|{0}| >> root state greater. Matching root: {1} to mirror:{2}".format(_str_func, _blockState,_mirrorState)))
            else:
                print(("|{0}| >> blockStates match....".format(_str_func, mirrorBlock.p_nameShort)))

            #if rootBlock.blockState != BlockState.TEMPLATE or mirrorBlock.blockState != BlockState.TEMPLATE:
                #print "Can only mirror blocks in Form state"
                #return

            cgmGEN.func_snapShot(vars())
            return

            currentFormObjects = block.formPositions
            formHeirarchyDict = {}
            for i,p in enumerate(currentFormObjects):
                formHeirarchyDict[i] = p.fullPath.count('|')

            formObjectsSortedByHeirarchy = sorted(list(formHeirarchyDict.items()), key=operator.itemgetter(1))

            for x in range(2):
                # do this twice in case there are any stragglers 
                for i in formObjectsSortedByHeirarchy:
                    index = i[0]
                    #print "Mirroring %s to %s" % (mirrorBlock.formPositions[index].name, block.formPositions[index].name)

                    # reflect rotation
                    reflectAim = block.formPositions[index].TransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
                    reflectUp  = block.formPositions[index].TransformDirection( MATH.Vector3(0,1,0)).reflect( rootReflectionVector )
                    mirrorBlock.formPositions[index].LookRotation( reflectAim, reflectUp )

                for i in formObjectsSortedByHeirarchy:
                    index = i[0]
                    wantedPos = (block.formPositions[index].position - rootTransform.formPositions[0].position).reflect( rootReflectionVector ) + rootTransform.formPositions[0].position

                    #print "wanted position:", wantedPos
                    mirrorBlock.formPositions[index].position = wantedPos

                    if block.formPositions[index].type == "joint":
                        #mirrorBlock.formPositions[index].SetAttr("radius", block.formPositions[index].GetAttr("radius"))
                        mirrorBlock.formPositions[index].radius = block.formPositions[index].radius

                    wantedScale = block.formPositions[index].localScale
                    if not mc.getAttr(mirrorBlock.formPositions[index].GetAttrString('sx'), l=True):
                        mirrorBlock.formPositions[index].SetAttr('sx', wantedScale.x)
                    if not mc.getAttr(mirrorBlock.formPositions[index].GetAttrString('sy'), l=True):
                        mirrorBlock.formPositions[index].SetAttr('sy', wantedScale.y)
                    if not mc.getAttr(mirrorBlock.formPositions[index].GetAttrString('sz'), l=True):
                        mirrorBlock.formPositions[index].SetAttr('sz', wantedScale.z)

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
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def MirrorSelectedBlocks( reflectionVector = MATH.Vector3(1,0,0) ):
    '''Mirrors the form positions from the block to the mirrorBlock across the reflection vector transformed from the root block'''

    for blockName in mc.ls(sl=True):
        currentBlock = Block.LoadRigBlock( GetNodeType(blockName) )
        if currentBlock:
            Block.MirrorBlock(currentBlock)

def MirrorBlockPush( block, reflectionVector = MATH.Vector3(1,0,0) ):
    '''Mirrors the given block to the corresponding block on the other side'''

    mirrorBlock = block.GetMirrorBlock()

    Block.MirrorBlock(block, mirrorBlock, reflectionVector)

def MirrorBlockPull( block, reflectionVector = MATH.Vector3(1,0,0) ):
    '''Mirrors the given block using the mirrorBlock's form positions'''

    mirrorBlock = block.GetMirrorBlock()

    Block.MirrorBlock(mirrorBlock, block, reflectionVector)
    
def blockMirror_subShapers(self,blockMirror=None,mode='push'):
    _str_func = 'blockMirror_subShapers'
      
    if blockMirror is None:
        log.debug("|{0}| >> Self mirror....".format(_str_func))
        if self.getMessage('blockMirror'):
            mMirror = self.blockMirror
        else:
            return log.error("|{0}| >> No block mirror found on: {1}".format(_str_func,self))
        log.debug("|{0}| >> UseMirror. BlockMirror Found: {1}".format(_str_func,mMirror))
    else:
        mMirror = blockMirror
    
    
    if mode == 'push':
        mSource = self
        mTarget = mMirror
    else:
        mSource = mMirror
        mTarget = self
        
    
    ml_source = form_getSubShapers(mSource)
    ml_target = form_getSubShapers(mTarget)
    
    if not ml_source:
        return log.warning("|{0}| >> no source".format(_str_func))
    if not ml_target:
        return log.warning("|{0}| >> no target".format(_str_func))
    
    for i,mCrv in enumerate(ml_source):
        print(mCrv)
        CURVES.mirror_worldSpace(mCrv.mNode, ml_target[i].mNode)
    
    
    
    
        
    
    
#=============================================================================================================
#>> blockDat
#=============================================================================================================
def baseSize_get(self):
    mBlockModule = self.p_blockModule
    
    if 'baseSize_get' in list(mBlockModule.__dict__.keys()):
        log.debug("|{0}| >> BlockModule call found...".format(_str_func))            
        return mBlockModule.baseSize_get
    
    _baseSize = self.baseSize
    try:mDefineEndObj = self.defineEndHelper
    except:mDefineEndObj = False
    
    if mDefineEndObj and mDefineEndObj.hasAttr('length'):
        return [mDefineEndObj.width,mDefineEndObj.height,mDefineEndObj.length]
    return _baseSize


def defineSize_get(self,resetBase=False):
    _str_func = 'defineSize_get'
    try:_baseDat = self.baseDat
    except:_baseDat = {}
    
    """
    if _baseDat.get('baseSize'):
        _size = _baseDat.get('baseSize')
        if resetBase:self.baseSize = _size
        return MATH.average(_size[:-2])/2.0"""

    #else:
    _baseSize = self.baseSize
    if _baseSize:
        log.debug("|{0}| >> Base size found: {1}...".format(_str_func,_baseSize))                    
        return MATH.average(_baseSize[:-2])/3.0
    return self.atUtils('get_shapeOffset') or 1.0# * 2.0

def define_getHandles(self):
    md_vectorHandles = {}
    md_defineHandles = {}
    #Form our vectors
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
        _blockState_int = self.blockState
        
        #self.baseSize = baseSize_get(self)
        #Trying to keep un assertable data out that won't match between two otherwise matching RigBlocks
        _d = {#"name":_short, 
              "blockType":self.blockType,
              "blockState":self.getEnumValueString('blockState'),
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
        
        _d['define'] = blockDat_getControlDat(self,'define',report)#self.getBlockDat_formControls()
        
        if _blockState_int >= 1:
            _d['form'] = blockDat_getControlDat(self,'form',report)#self.getBlockDat_formControls()

        if _blockState_int >= 2:
            _d['prerig'] = blockDat_getControlDat(self,'prerig',report)#self.getBlockDat_prerigControls() 

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
                except Exception as err:
                    log.error("Failed to query attr: {0} | type: {1} | err: {2}".format(a,_type,err))
        
        _d['ud']['baseSize'] = baseSize_get(self)
        
        if report:cgmGEN.walk_dat(_d,'[{0}] blockDat'.format(self.p_nameShort))
        return _d
    except Exception as err:
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
        raise ValueError("Can't copy blockDat from self.")
    blockDat = sourceBlock.getBlockDat()
    
    _type = blockDat['ud'].get('blockType')
    _profile = blockDat['ud'].get('blockProfile')
    
    if not ignoreChecks:
        if _type != self.blockType:
            raise ValueError("Incompatible blockTypes. dat: {0} | {1}".format(_type,self.blockType))
        if _profile != self.blockProfile:
            raise ValueError("Incompatible blockProfiles. dat: {0} | {1}".format(_profile,self.blockProfile))
    
    blockDat['baseName'] = self.cgmName
    blockDat['ud']['cgmName'] = self.cgmName
    
    if blockDat['ud'].get('rigSetup') in ['finger']:
        log.debug("|{0}| >> Clearing nameList".format(_str_func))
        for a in list(blockDat['ud'].items()):
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
                    'form':1,
                    'prerig':2}
    
    if _mode_str not in list(_modeToState.keys()):
        raise ValueError("Unknown mode: {0}".format(_mode_str))
    
    _blockState_int = self.blockState
    
    if not _blockState_int >= _modeToState[_mode_str]:
        raise ValueError('[{0}] not {1} yet. State: {2}'.format(_short,_mode_str,_blockState_int))
        #_ml_formHandles = self.msgList_get('formHandles',asMeta = True)
    
    _d_controls = {'define':False,'form':False,'prerig':False}
    _d_controls[_mode_str] = True
    ml_handles = controls_get(self, **_d_controls)
    #pprint.pprint(vars())
    
    if not ml_handles:
        log.debug('[{0}] No form or prerig handles found'.format(_short))
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
            _d_orientHelpers[i] = mObj.orientHelper.rotate

        if mObj.getMessage('jointHelper'):
            _d_jointHelpers[i] = mObj.jointHelper.translate
            
        mLoftCurve = mObj.getMessageAsMeta('loftCurve')
        if mLoftCurve:
            log.debug("|{0}| >>  loftcurve: {1}".format(_str_func,mLoftCurve)+'-'*20)
            if mLoftCurve.v:
                _d = {}
                _rot = mLoftCurve.rotate
                _orient = mLoftCurve.p_orient
                _trans = mLoftCurve.translate
                _scale = mLoftCurve.scale
                _p = mLoftCurve.p_position
                
                _d['bb'] = TRANS.bbSize_get(mLoftCurve.mNode)
                _d['ab'] = DIST.get_axisSize(mLoftCurve.mNode)
                
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
                  's':[mObj.scale for mObj in ml_subShapers],
                  'ab':[DIST.get_axisSize(mObj.mNode) for mObj in ml_subShapers],                             
                  'bb':[TRANS.bbSize_get(mObj.mNode) for mObj in ml_subShapers]}            
            if _d:
                _d_subShapers[i] = _d            
        
        log.debug(cgmGEN._str_subLine)    


        #else:
            #_l_jointHelpers.append(False)
    _d = {'positions':[mObj.p_position for mObj in ml_handles],
          'orients':[mObj.p_orient for mObj in ml_handles],
          'scales':[mObj.scale for mObj in ml_handles],
          'names':[mObj.p_nameBase for mObj in ml_handles],
          'bb':[TRANS.bbSize_get(mObj.mNode) for mObj in ml_handles]}
    
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

    if report:cgmGEN.walk_dat(_d,'[{0}] form blockDat'.format(self.p_nameShort))
    return _d

def blockDat_load_state(self,state = None,blockDat = None, d_warnings = None, overrideMode = None, mainHandleNormalizeScale = False):
    _str_func = 'blockDat_load_state'
    log.debug(cgmGEN.logString_start(_str_func))
    
    _noScale = False
    _scaleMode = None

        
    if overrideMode:
        if overrideMode == 'update':
            if state not in ['form',1]:
                _noScale = True
                mainHandleNormalizeScale = False
            else:
                mainHandleNormalizeScale = True
                _scaleMode = 'bb'
        elif overrideMode == 'useLoft':
            if state in ['form',1]:
                _scaleMode = 'useLoft'
                
    if state  in ['prerig', 2]:
        _noScale = True
    
    #pprint.pprint([mainHandleNormalizeScale,_noScale,_scaleMode])    
    
    if not blockDat:
        log.debug(cgmGEN.logString_msg(_str_func,"No blockDat, using self"))
        blockDat = self.blockDat

    d_state = blockDat.get(state,False)
    if not d_state:
        log.error(cgmGEN.logString_msg(_str_func,"No {0} data found in blockDat".format(state)))
        return False
    
    ml_handles = controls_get(self,**{state:True})
    
    if d_warnings:
        if not d_warnings.get(state):
            d_warnings[state] =  []
        _l_warnings = d_warnings[state]
    else:
        _l_warnings = []

    if not ml_handles:
        log.error("|{0}| >> No {1} handles found".format(_str_func,state))
    else:
        log.debug(cgmGEN.logString_sub(_str_func,"processing {0}".format(state)))        
        _posTempl = d_state.get('positions')
        _orientsTempl = d_state.get('orients')
        _scaleTempl = d_state.get('scales')
        _bbTempl = d_state.get('bb')
        _jointHelpers = d_state.get('jointHelpers')
        _loftCurves = d_state.get('loftCurves',{})
        _subShapers = d_state.get('subShapers',{})
        _len_posTempl = len(_posTempl)
        _jointHelpersPre = {}
        if state == 'prerig':
            _jointHelpersPre = d_state.get('jointHelpers')
            
        md_match = {}
        for i,mHandle in enumerate(ml_handles):
            md_match[i] = mHandle
            
        if len(ml_handles) > _len_posTempl:
            msg = "|{0}| >> {3} handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}. Attempting to match".format(_str_func,len( ml_handles),_len_posTempl,state)
            log.warning(msg)
            
            _names = d_state['names']
            for i,name in enumerate(_names):
                for mHandle in ml_handles:
                    if mHandle.p_nameShort == name:
                        md_match[i] = mHandle
                if not md_match.get(i):
                    log.warning(cgmGEN.logString_msg(_str_func, "Couldn't find: {0} | {1}".format(i,name)))
                    
                                            
            
            """
            msg = "|{0}| >> {3} handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( ml_handles),_len_posTempl,state)
            if d_warnings:
                _l_warnings.append(msg)
            else:
                log.warning(msg)"""
            
        #pprint.pprint(md_match)
        
        for i_loop in range(3):
            log.debug(cgmGEN.logString_sub(_str_func,"Loop: {0}".format(i_loop)))
            for i,mObj in list(md_match.items()):
                if not i_loop:log.info(cgmGEN.logString_msg(_str_func,"Handle: {0}".format(mObj)))
                
                _handleType = mObj.getMayaAttr('handleType')
                if _handleType == 'vector':
                    try:
                        mObj.p_orient = _orientsTempl[i]
                        continue
                    except Exception as err:
                        _l_warnings.append('{0}...'.format(mObj.p_nameShort))
                        _l_warnings.append('Couldnt set vector handle orient | {0}'.format(err))
                
                if i > _len_posTempl-1:
                    _l_warnings.append("No data for: {0}".format(mObj))
                    continue
                
                mObj.p_position = _posTempl[i]
                if not ATTR.is_locked(mObj.mNode,'rotate'):
                    mObj.p_orient = _orientsTempl[i]
                    
                _tmp_short = mObj.mNode
                _d_loft = _loftCurves.get(str(i))
                
                if _noScale != True:
                    _cgmType = mObj.getMayaAttr('cgmType')
                    if _scaleMode == 'useLoft' and  _cgmType in ['blockHandle','formHandle']:
                        _bb = _d_loft.get('bb')
                        _size = MATH.average(_bb) * .75
                        mc.scale(_size,_size,_size, _tmp_short, absolute = True)
                    elif mainHandleNormalizeScale and _cgmType in ['blockHandle','formHandle']:
                        _average = MATH.average(_bbTempl[i])
                        mc.scale(_average,_average,_average, _tmp_short, absolute = True)
                    else:
                        _noBB = False
                        _normalizeUp = False
                        if _cgmType in ['pivotHelper']:
                            if  mObj.getMayaAttr('cgmName') not in ['base','top']:
                                _noBB = True
                            else:
                                _normalizeUp = True
                                
                        if _scaleMode == 'bb' and _noBB != True:
                            TRANS.scale_to_boundingBox_relative(_tmp_short,_bbTempl[i],freeze=False)
                        else:
                            for ii,v in enumerate(_scaleTempl[i]):
                                _a = 's'+'xyz'[ii]
                                if not mObj.isAttrConnected(_a):
                                    ATTR.set(_tmp_short,_a,v)
                                else:
                                    log.debug("|{0}| >> connected scale: {1}".format(_str_func,_a))
                        if _normalizeUp:
                            mObj.sy = 1
                            
                #Secondary stuff
                if _jointHelpers and _jointHelpers.get(i):
                    mObj.jointHelper.translate = _jointHelpers[i]
                
                if _d_loft:
                    if i_loop:
                        log.debug("|{0}| >> _d_loft: {1}".format(_str_func,_d_loft))
                    
                        mLoftCurve = mObj.getMessageAsMeta('loftCurve')
                        if mLoftCurve:
                            _rot = _d_loft.get('r')
                            _s = _d_loft.get('s')
                            _t = _d_loft.get('t')
                            _bb = _d_loft.get('bb')
                            _ab = _d_loft.get('ab')
                            _p = _d_loft.get('p')
                            if _rot:
                                ATTR.set(mLoftCurve.mNode,'rotate',_rot)
                                
                            if _noScale != True:
                                if _s != None:
                                    if _scaleMode in ['bb','useLoft']:
                                        try:DIST.scale_to_axisSize(mLoftCurve.mNode,_ab,skip=2)
                                        except Exception as err:
                                            log.error(err)
                                            TRANS.scale_to_boundingBox_relative(mLoftCurve.mNode,_bb,freeze=False)
                                    else:
                                        ATTR.set(mLoftCurve.mNode,'scale',_s)
                                    
                            if _p:
                                mLoftCurve.p_position = _p
                            #if _t:
                                #ATTR.set(mLoftCurve.mNode,'translate',_t)
                            
                if _jointHelpersPre and _jointHelpersPre.get(i):
                    mObj.jointHelper.translate = _jointHelpersPre[i]                    
                        
            for i,d_sub in list(_subShapers.items()):
                try:
                    ml_subs = ml_handles[int(i)].msgList_get('subShapers')
                    log.debug ("|{0}| >> subShapers: {1}".format(_str_func,i))
                    if not ml_subs:
                        raise ValueError("Failed to find subShaper: {0} | {1}".format(i,d_sub))
                    _t = d_sub.get('t')
                    _r = d_sub.get('r')
                    _s = d_sub.get('s')
                    _p = d_sub.get('p')
                    _bb = d_sub.get('bb')
                    _ab = d_sub.get('ab')
                    
                    _len_p = len(_p)
                    for ii,mObj in enumerate(ml_subs):
                        if ii > _len_p-1:
                            _l_warnings.append("No data for sub {0} on {1}".format(ii,mObj))
                            #mObj.p_position = _p[ii-1]
                            #ATTR.set(mObj.mNode,'t',_t[ii])
                            ATTR.set(mObj.mNode,'r',_r[ii-1])
                            
                            if _noScale != True:
                                if _scaleMode in ['bb','useLoft']:
                                    try:DIST.scale_to_axisSize(mObj.mNode,_ab[ii-1],skip=2)
                                    except Exception as err:
                                        log.error(err)                                
                                        TRANS.scale_to_boundingBox_relative(mObj.mNode,_bb[ii-1],freeze=False)
                                else:
                                    ATTR.set(mObj.mNode,'s',_s[ii-1])
                            
                            continue                            
                        mObj.p_position = _p[ii]
                        #ATTR.set(mObj.mNode,'t',_t[ii])
                        ATTR.set(mObj.mNode,'r',_r[ii])
                        
                        if _noScale != True:
                            if _scaleMode in ['bb','useLoft']:
                                try:DIST.scale_to_axisSize(mObj.mNode,_ab[ii],skip=2)
                                except Exception as err:
                                    log.error(err)
                                    TRANS.scale_to_boundingBox_relative(mObj.mNode,_bb[ii],freeze=False)
                            else:
                                ATTR.set(mObj.mNode,'s',_s[ii])
                except Exception as err:
                    log.error(cgmGEN.logString_msg(_str_func,"subShapers: {0} | {1}".format(i,err)))
                    pprint.pprint(d_sub)

#@cgmGEN.Timer
def blockDat_load(self, blockDat = None,
                  useMirror = False,
                  settingsOnly = False,
                  autoPush = True,
                  currentOnly=False,
                  overrideMode = None,
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
            raise ValueError("|{0}| >> blockDat must be dict. type: {1} | blockDat: {2}".format(_str_func,type(blockDat),blockDat)) 
    
        _blockType = blockDat.get('blockType')
        if _blockType != self.blockType:
            raise ValueError("|{0}| >> blockTypes don't match. self: {1} | blockDat: {2}".format(_str_func,self.blockType,_blockType)) 
    
        self.blockScale = blockDat['blockScale']
        
        #.>>>..UD ====================================================================================
        log.debug("|{0}| >> ud...".format(_str_func)+ '-'*80)
        _ud = blockDat.get('ud')
        _udFail = {}
        if not blockDat.get('ud'):
            raise ValueError("|{0}| >> No ud data found".format(_str_func))
        
        for a,v in list(_ud.items()):
            _current = ATTR.get(_short,a)
            if _current != v:
                try:
                    if ATTR.get_type(_short,a) in ['message']:
                        log.debug("|{0}| >> userDefined '{1}' skipped. Not loading message data".format(_str_func,a))                     
                    else:
                        log.debug("|{0}| >> userDefined '{1}' mismatch. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                        ATTR.set(_short,a,v)
                except Exception as err:
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
            except Exception as err:
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
        
        #else:
            #for ii,v in enumerate(_scale):
                #_a = 's'+'xyz'[ii]
                #if not self.isAttrConnected(_a) and not(ATTR.is_locked(_short,a)):
                #setAttr(_short,_a,v)
            
        #>>Define Controls ====================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'define'))
        
        if redefine:
            changeState(self,'define',forceNew=True)
            changeState(self,'define',forceNew=True)            
            _current_state_idx = 0
            _current_state = 'define'
        
        if blockDat.get('blockScale'):
            self.blockScale = blockDat['blockScale']
            
            
        if mMirror == 'cat':
            log.debug("|{0}| >> mMirror define pull...".format(_str_func))            
            controls_mirror(mMirror,self,define=True)
        else:
            blockDat_load_state(self,'define',blockDat,_d_warnings,overrideMode=overrideMode)
        
        #>>Form Controls ====================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'form'))
        
        if _target_state_idx >= 1:
            log.debug("|{0}| >> form dat....".format(_str_func))
            if autoPush:
                if _current_state_idx < 1:
                    log.debug("|{0}| >> Pushing to form....".format(_str_func))
                    self.p_blockState = 1
            else:
                return log.warning(cgmGEN.logString_msg(_str_func,"Autopush off. Can't go to: {0}".format(_target_state)))
            
            log.debug(cgmGEN.logString_msg(_str_func,'form push'))
            
        if mMirror:
            log.debug("|{0}| >> mMirror form pull...".format(_str_func))            
            self.UTILS.controls_mirror(mMirror,self,form=True,prerig=False)
        
        else:
            if _orientHelper:
                mOrientHelper = self.getMessageAsMeta('orientHelper')
                if mOrientHelper:
                    _ctrl = mOrientHelper.mNode
                    for ii,v in enumerate(_orientHelper):
                        _a = 'r'+'xyz'[ii]
                        setAttr(_ctrl,_a,v)
                else:
                    _d_warnings['form']=["Missing orient Helper. Data found."]
                
            blockDat_load_state(self,'form',blockDat,_d_warnings,overrideMode=overrideMode)
           
        
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
            self.UTILS.controls_mirror(mMirror,self,form=False,prerig=True)
        else:
            blockDat_load_state(self,'prerig',blockDat,_d_warnings,overrideMode,overrideMode)
            
        if _d_warnings:
            try:
                for k,d in list(_d_warnings.items()):
                    for i,w in enumerate(d):
                        if i == 0:log.warning(cgmGEN.logString_sub(_str_func,"{0} | Warnings".format(k)))
                        log.warning(w)
            except:pass
        return

    except Exception as err:cgmGEN.cgmException(Exception,err)


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
            raise ValueError("|{0}| >> blockDat must be dict. type: {1} | blockDat: {2}".format(_str_func,type(blockDat),blockDat)) 
    
        _blockType = blockDat.get('blockType')
        if _blockType != self.blockType:
            raise ValueError("|{0}| >> blockTypes don't match. self: {1} | blockDat: {2}".format(_str_func,self.blockType,_blockType)) 
    
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
            raise ValueError("|{0}| >> No ud data found".format(_str_func))
        
        for a,v in list(_ud.items()):
            _current = ATTR.get(_short,a)
            if _current != v:
                try:
                    if ATTR.get_type(_short,a) in ['message']:
                        log.debug("|{0}| >> userDefined '{1}' skipped. Not loading message data".format(_str_func,a))                     
                    else:
                        log.debug("|{0}| >> userDefined '{1}' mismatch. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                        ATTR.set(_short,a,v)
                except Exception as err:
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
            except Exception as err:
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
                                    log.debug ("|{0}| >> FormHandle: {1}".format(_str_func,mObj.mNode))
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
                                            
                                for i,d_sub in list(_subShapers.items()):
                                    ml_subs = _ml_defineHandles[int(i)].msgList_get('subShapers')
                                    log.debug ("|{0}| >> subShapers: {1}".format(_str_func,i))
                                    if not ml_subs:
                                        raise ValueError("Failed to find subShaper: {0} | {1}".format(i,d_sub))
                                    _t = d_sub.get('t')
                                    _r = d_sub.get('r')
                                    _s = d_sub.get('s')
                                    _p = d_sub.get('p')
                                    for ii,mObj in enumerate(ml_subs):
                                        mObj.p_position = _p[ii]
                                        #ATTR.set(mObj.mNode,'t',_t[ii])
                                        ATTR.set(mObj.mNode,'r',_r[ii])
                                        ATTR.set(mObj.mNode,'s',_s[ii])    
        
        
        #>>Form Controls ====================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'form'))
        
        if _target_state_idx >= 1:
            log.debug("|{0}| >> form dat....".format(_str_func))
            if autoPush and currentOnly != True:
                if _current_state_idx < 1:
                    log.debug("|{0}| >> Pushing to form....".format(_str_func))
                    self.p_blockState = 1
            
        if not _onlyState or _onlyState == 'form':
            log.debug(cgmGEN.logString_msg(_str_func,'form push'))
            
            if mMirror:
                log.debug("|{0}| >> mMirror form pull...".format(_str_func))            
                self.UTILS.controls_mirror(mMirror,self,form=True,prerig=False)
            
            else:
                if _orientHelper:
                    _ctrl = self.orientHelper.mNode
                    for ii,v in enumerate(_orientHelper):
                        _a = 'r'+'xyz'[ii]
                        setAttr(_ctrl,_a,v)
                
                _d_form = blockDat.get('form',False)
                _d_warnings['form'] =  []
                _l_warnings = _d_warnings['form']
                
                if not _d_form:
                    log.error("|{0}| >> No form data found in blockDat".format(_str_func)) 
                else:
                    _ml_formHandles = self.atUtils('controls_get',form=True)
    
                    if not _ml_formHandles:
                        log.error("|{0}| >> No form handles found".format(_str_func))
                    else:
                        _posTempl = _d_form.get('positions')
                        _orientsTempl = _d_form.get('orients')
                        _scaleTempl = _d_form.get('scales')
                        _jointHelpers = _d_form.get('jointHelpers')
                        _loftCurves = _d_form.get('loftCurves',{})
                        _subShapers = _d_form.get('subShapers',{})
                        
                        if len(_ml_formHandles) > len(_posTempl):
                            _l_warnings.append("|{0}| >> Form handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( _ml_formHandles),len(_posTempl)))
                        
                        for i_loop in range(3):
                            log.debug("|{0}| >> Loop: {1}".format(_str_func,i_loop))
    
                            for i,mObj in enumerate(_ml_formHandles):
                                try:
                                    log.debug ("|{0}| >> FormHandle: {1}".format(_str_func,mObj.mNode))
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
                                except Exception as err:
                                    _l_warnings.append("{0} | {1} | mObj: {2} | err: {3}".format(i_loop,i,mObj.p_nameShort, err))
                                        
                            for i,d_sub in list(_subShapers.items()):
                                try:
                                    ml_subs = _ml_formHandles[int(i)].msgList_get('subShapers')
                                    log.debug ("|{0}| >> subShapers: {1}".format(_str_func,i))
                                    if not ml_subs:
                                        raise ValueError("Failed to find subShaper: {0} | {1}".format(i,d_sub))
                                    _t = d_sub.get('t')
                                    _r = d_sub.get('r')
                                    _s = d_sub.get('s')
                                    _p = d_sub.get('p')
                                    
                                    for ii,mObj in enumerate(ml_subs):
                                        #mObj.p_position = _p[0]                                    
                                        ATTR.set(mObj.mNode,'t',_t[ii])
                                        ATTR.set(mObj.mNode,'r',_r[ii])
                                        ATTR.set(mObj.mNode,'s',_s[ii])
                                except Exception as err:
                                    _l_warnings.append("{0} | {1} | subs | err: {2}".format(i_loop,i, err))
                                    
                                
        
                    #if _d_form.get('rootOrientHelper'):
                        #if self.getMessage('orientHelper'):
                        #    self.orientHelper.p_orient = _d_form.get('rootOrientHelper')
                        #else:
                            #log.error("|{0}| >> Found root orient Helper data but no orientHelper control".format(_str_func))
        #pprint.pprint(vars())
        
        #Prerig ==============================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'prerig'))
        
        if _target_state_idx >= 2:
            log.debug("|{0}| >> prerig dat....".format(_str_func))
            if _current_state_idx < 2:
                if not autoPush:
                    log.debug("|{0}| >> Autopush off. Stopping at form....".format(_str_func))                
                    return True
                
                log.debug("|{0}| >> Pushing to prerig....".format(_str_func))
                self.p_blockState = 2
            
        if not _onlyState or _onlyState == 'prerig':
            log.debug(cgmGEN.logString_msg(_str_func,'prerig push'))
        
            if mMirror:
                log.debug("|{0}| >> mMirror prerig pull...".format(_str_func))            
                self.UTILS.controls_mirror(mMirror,self,form=False,prerig=True)
            else:
                _d_prerig = blockDat.get('prerig',False)
                if not _d_prerig:
                    log.error("|{0}| >> No form data found in blockDat".format(_str_func)) 
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
                                except Exception as err:
                                    _l_warnings.append("{0} | {1} | mObj: {2} | err: {3}".format(i_loop,i,mObj.p_nameShort, err))                
                    #if _d_prerig.get('rootOrientHelper'):
                        #if self.getMessage('orientHelper'):
                            #self.orientHelper.p_orient = _d_prerig.get('rootOrientHelper')
                        #else:
                            #log.error("|{0}| >> Found root orient Helper data but no orientHelper #control".format(_str_func))
            
            #if _target_state_idx > 2:
            #    self.p_blockState = _target_state

        if _d_warnings:
            for k,d in list(_d_warnings.items()):
                for i,w in enumerate(d):
                    if i == 0:log.warning(cgmGEN.logString_sub(_str_func,"{0} | Warnings".format(k)))
                    log.warning(w)
        return
        #>>Generators ====================================================================================
        log.debug("|{0}| >> Generators".format(_str_func)+ '-'*80)
        _d = {"isSkeletonized":[self.isSkeletonized,self.doSkeletonize,self.deleteSkeleton]}
    
        for k,calls in list(_d.items()):
            _block = bool(blockDat.get(k))
            _current = calls[0]()
            if _state != _current:
                log.debug("|{0}| >> {1} States don't match. self: {2} | blockDat: {3}".format(_str_func,k,_current,_block)) 
                if _block == False:
                    calls[2]()                         
                else:
                    calls[1]()     
    
    
    
        return True
    except Exception as err:cgmGEN.cgmException(Exception,err)



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
            #reflectAim = block.formPositions[index].TransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
            #reflectUp  = block.formPositions[index].TransformDirection( MATH.Vector3(0,1,0)).reflect( rootReflectionVector )
            #mirrorBlock.formPositions[index].LookRotation( reflectAim, reflectUp )
            
    
    if blockDat is None:
        log.debug("|{0}| >> No blockDat passed. Checking self...".format(_str_func))    
        blockDat = self.blockDat

    if not issubclass(type(blockDat),dict):
        raise ValueError("|{0}| >> blockDat must be dict. type: {1} | blockDat: {2}".format(_str_func,type(blockDat),blockDat)) 
    

    _blockType = blockDat.get('blockType')
    if _blockType != self.blockType:
        raise ValueError("|{0}| >> blockTypes don't match. self: {1} | blockDat: {2}".format(_str_func,self.blockType,_blockType)) 
    
    log.debug("|{0}| >> blockDat looks good...".format(_str_func))    
    
    if mirror:
        #rootReflectionVector = TRANS.transformDirection(_short,reflectionVector).normalized()
        rootReflectionVector = reflectionVector
        log.debug("|{0}| >> Mirror mode. Relect: {1}".format(_str_func,rootReflectionVector))    
        
    
    #.>>>..UD ====================================================================================
    log.debug("|{0}| >> ud...".format(_str_func)+ '-'*80)
    _ud = blockDat.get('ud')
    if not blockDat.get('ud'):
        raise ValueError("|{0}| >> No ud data found".format(_str_func)) 
    for a,v in list(_ud.items()):
        _current = ATTR.get(_short,a)
        if _current != v:
            try:
                if ATTR.get_type(_short,a) in ['message']:
                    log.debug("|{0}| >> userDefined '{1}' skipped. Not loading message data".format(_str_func,a))                     
                else:
                    log.debug("|{0}| >> userDefined '{1}' mismatch. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                    ATTR.set(_short,a,v)
            except Exception as err:
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
            #reflectAim = block.formPositions[index].TransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
            #reflectUp  = block.formPositions[index].TransformDirection( MATH.Vector3(0,1,0)).reflect( rootReflectionVector )
            #mirrorBlock.formPositions[index].LookRotation( reflectAim, reflectUp )
            """
                
                
            
#(block.formPositions[index].position - rootTransform.formPositions[0].position).reflect( rootReflectionVector ) + rootTransform.formPositions[0].position
            
            for ii,v in enumerate(_scale[i]):
                _a = 's'+'xyz'[ii]
                if not self.isAttrConnected(_a):
                    ATTR.set(_short,_a,v)
    
    #>>Form Controls ====================================================================================
    _int_state = self.getState(False)
    if _int_state > 0:
        log.debug("|{0}| >> form dat....".format(_str_func))             
        _d_form = blockDat.get('form',False)
        if not _d_form:
            log.error("|{0}| >> No form data found in blockDat".format(_str_func)) 
        else:
            if _int_state == 1:
                _ml_formHandles = self.msgList_get('formHandles',asMeta = True)            
            else:
                _ml_formHandles = self.msgList_get('prerigHandles',asMeta = True)                


            #_ml_formHandles = self.msgList_get('formHandles',asMeta = True)
            if not _ml_formHandles:
                log.error("|{0}| >> No form handles found".format(_str_func))
            else:
                _posTempl = _d_form.get('positions')
                _orientsTempl = _d_form.get('orientations')
                _scaleTempl = _d_form.get('scales')
                _jointHelpers = _d_form.get('jointHelpers')

                if len(_ml_formHandles) != len(_posTempl):
                    log.error("|{0}| >> Form handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( _ml_formHandles),len(_posTempl))) 
                else:
                    for i,mObj in enumerate(_ml_formHandles):
                        if mObj in ml_processed:
                            log.debug("|{0}| >> Obj [{1}] {2} already processed".format(_str_func, i, mObj.p_nameShort))                            
                            continue
                        
                        log.debug ("|{0}| >> FormHandle: {1}".format(_str_func,mObj.mNode))
                        mObj.p_position = _posTempl[i]
                        mObj.p_orient = _orientsTempl[i]
                        
                        _tmp_short = mObj.mNode
                        for ii,v in enumerate(_scaleTempl[i]):
                            _a = 's'+'xyz'[ii]
                            if not self.isAttrConnected(_a):
                                ATTR.set(_tmp_short,_a,v)   
                        if _jointHelpers and _jointHelpers[i]:
                            mObj.jointHelper.translate = _jointHelpers[i]
                            
            if _d_form.get('rootOrientHelper'):
                if self.getMessage('orientHelper'):
                    self.orientHelper.p_orient = _d_form.get('rootOrientHelper')
                else:
                    log.error("|{0}| >> Found root orient Helper data but no orientHelper control".format(_str_func))



    #>>Generators ====================================================================================
    log.debug("|{0}| >> Generators".format(_str_func)+ '-'*80)
    _d = {"isSkeletonized":[self.isSkeletonized,self.doSkeletonize,self.deleteSkeleton]}

    for k,calls in list(_d.items()):
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
    
    for a,v in list(kws.items()):
        if self.hasAttr(a):
            try:
                ATTR.set(_short,a,v)
            except Exception as err:
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
        for a,v in list(kws.items()):
            try:
                ATTR.set(o,a,v)
            except Exception as err:
                print(err)
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
        mBlockModule = self.getBlockModule()
        if 'd_wiring_extraDags' in list(mBlockModule.__dict__.keys()):
            log.debug("|{0}| >>  Found extraDat wiring".format(_str_func))
            for k in mBlockModule.d_wiring_extraDags.get('msgLinks',[]):
                mNode = self.getMessageAsMeta(k)
                if mNode:
                    ml_controls.append(mNode)
            for k in mBlockModule.d_wiring_extraDags.get('msgLists',[]):
                ml = self.msgList_get(k)
                if ml:
                    ml_controls.extend(ml)
        return ml_controls
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)

def connect_jointLabels(self):
    try:
        _short = self.p_nameShort
        _str_func = 'connect_jointLabels'
        log.debug(cgmGEN.logString_start(_str_func))
        if not ATTR.has_attr(_short,'visLabels'):
            return log.info(cgmGEN.logString_msg(_str_func,"{0} has no visLabels attr".format(_short)))
        
        _driver =  "{0}.visLabels".format(_short)
        for mObj in self.getDescendents(asMeta=1):
            if mObj.getMayaAttr('cgmType') == 'jointLabel':
                log.info(cgmGEN.logString_msg(_str_func,"Found: {0}".format(mObj)))
                ATTR.connect(_driver, "{0}.overrideVisibility".format(mObj.mNode))        

    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    
def shapers_get(self):
    _short = self.p_nameShort        
    _str_func = '[{0}] controls_get'.format(_short)
    log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
    
    ml_handles = self.msgList_get('formHandles')
    ml_lofts = []
    if ml_handles:
        for i,mObj in enumerate(ml_handles):
            try:
                mLoft = mObj.loftCurve
            except:mLoft = False
            if mLoft:
                ml_lofts.append(mLoft)
                
            ml_sub = mObj.msgList_get('subShapers')
            if ml_sub:
                ml_lofts.extend(ml_sub)
                
    
    return ml_lofts
              
                
def controls_get(self,define = False, form = False, prerig= False, asDict =False, getExtra=False):
    try:
        _short = self.p_nameShort        
        _str_func = '[{0}] controls_get'.format(_short)
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
        
        def addMObj(mObj,datType=None):
            log.debug("|{0}| >> Storing: {1} ".format(_str_func,mObj))
            if mObj in ml_controls:
                log.debug("|{0}| >> Already stored: {1} ".format(_str_func,mObj))                    
                return
            
            if not md_controls.get(datType):md_controls[datType] = []
            
            ml_controls.append(mObj)
            md_controls[datType].append(mObj)

            if getExtra:
                if define:
                    pass
                    
                if form:
                    mLoftCurve = mObj.getMessageAsMeta('loftCurve')
                    if mLoftCurve:addMObj(mLoftCurve,datType)
                    
                    ml_subShapers = mObj.msgList_get('subShapers')
                    if ml_subShapers:
                        for mSub in ml_subShapers:
                            addMObj(mSub,datType)
            if prerig:
                for s in ['jointHelper','handle','shapeHelper']:
                    if mObj.getMessage(s):
                        log.debug("|{}| >> ... has {} helper".format(_str_func,s))
                        addMObj(mObj.getMessageAsMeta(s),datType)
                        
        def addPivotHelper(mPivotHelper,datType):
            addMObj(mPivotHelper)
            for a in ['pivotBack','pivotFront','pivotLeft','pivotRight','pivotCenter','topLoft']:
                mPivot = mPivotHelper.getMessageAsMeta(a)
                if mPivot:
                    addMObj(mPivot,datType)
            #for mChild in mPivotHelper.getChildren(asMeta=True):
                #if mChild.getMayaAttr('cgmType') == 'pivotHelper':
                    #addMObj(mChild,datType)
            
        ml_controls = []
        md_controls = {}
        
        #if self.getMessage('orientHelper'):
            #ml_controls.append(self.orientHelper)
        if define:
            ml_handles = self.msgList_get('defineHandles',asMeta=True)
            if ml_handles:
                log.debug("|{0}| >> define dat found...".format(_str_func))            
                for mObj in ml_handles:
                    addMObj(mObj,'define')
                
                for s in ['orientHelper']:
                    if self.getMessage(s):
                        log.info("|{}| >> ... has {} helper".format(_str_func,s))
                        addMObj(self.getMessageAsMeta(s),'define')                                    
            
        if form:
            log.debug("|{0}| >> form pass...".format(_str_func))            
            ml_handles = self.msgList_get('formHandles',asMeta = True)
            for mObj in ml_handles:
                addMObj(mObj,'form')
            for mObj in ml_handles:#.second loop to push this tothe back
                if mObj.getMessage('pivotHelper'):addPivotHelper(mObj.pivotHelper,'form')
                
        if prerig:
            log.debug("|{0}| >> Prerig pass...".format(_str_func))                        
            ml_handles = self.msgList_get('prerigHandles',asMeta = True)
            ml_jointHandles = self.msgList_get('jointHelpers',asMeta=1)
            if ml_jointHandles:
                ml_handles.extend(ml_jointHandles)
            for mObj in ml_handles:
                addMObj(mObj,'prerig')
            for mObj in ml_handles:#.second loop to push this tothe back
                if mObj.getMessage('pivotHelper'):addPivotHelper(mObj.pivotHelper,'prerig')
                
            for h in ['settingsHelper','cogHelper','ikStartHandle','ikEndHandle']:
                mFound = self.getMessageAsMeta(h)
                if mFound:
                    addMObj(mFound,'prerig')
        
        if asDict:
            return md_controls
        return ml_controls
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    
def controls_mirror(blockSource, blockMirror = None,
                    mirrorMode = 'push', 
                    reflectionVector = MATH.Vector3(1,0,0),
                    define=True,form = True, prerig= True,
                    mirrorLofts = True):
    try:
        _short = blockSource.p_nameShort        
        _str_func = 'controls_mirror'
        
        log.debug(cgmGEN.logString_start(_str_func, _short))

        md_sourceAll = {}
        md_targetAll = {}
        ml_sourceCheck = []
        ml_targetCheck = []
        
        #Control sets ===================================================================================
        log.debug(cgmGEN.logString_sub(_str_func, 'control sets...'))
        
        def add_mSet(mSet,ml_check,md_sourceAll,name='base'):
            ml_use = []
            for mObj in mSet:
                if mObj not in ml_check:
                    log.debug(cgmGEN.logString_msg(_str_func, '{1} | Add: {0}'.format(mObj,name)))
                    ml_check.append(mObj)
                    ml_use.append(mObj)
                else:
                    log.debug(cgmGEN.logString_msg(_str_func, '{1} | Removing: {0}'.format(mObj,name)))
            md_sourceAll[name] = ml_use
            return ml_use

        add_mSet([blockSource],ml_sourceCheck,md_sourceAll,'base')
        if blockMirror:
            add_mSet([blockMirror],ml_targetCheck,md_targetAll,'base')

        if define:
            add_mSet(controls_get(blockSource,define=True),ml_sourceCheck,md_sourceAll,'define')
            if blockMirror:
                ml_use = add_mSet(controls_get(blockMirror,define=True),ml_targetCheck,md_targetAll,'define')
                if not ml_use:
                    log.warning(cgmGEN.logString_msg(_str_func, "No [define] dat found on target. removing"))
                    md_sourceAll.pop('define')
                    md_targetAll.pop('define')

        if form:
            add_mSet(controls_get(blockSource,form=True),ml_sourceCheck,md_sourceAll,'form')
            if blockMirror:
                ml_use = add_mSet(controls_get(blockMirror,form=True),ml_targetCheck,md_targetAll,'form')
                if not ml_use:
                    log.warning(cgmGEN.logString_msg(_str_func, "No [form] dat found on target. removing"))
                    md_sourceAll.pop('form')
                    md_targetAll.pop('form')

        if prerig:
            add_mSet(controls_get(blockSource,prerig=True),ml_sourceCheck,md_sourceAll,'prerig')
            if blockMirror:
                ml_use = add_mSet(controls_get(blockMirror,prerig=True),ml_targetCheck,md_targetAll,'prerig')
                if not ml_use:
                    log.warning(cgmGEN.logString_msg(_str_func, "No [prerig] dat found on target. removing"))
                    md_sourceAll.pop('prerig')
                    md_targetAll.pop('prerig')

        if not blockMirror:
            md_targetAll = copy.copy(md_sourceAll)

        #Shuffle sets ===================================================================================
        log.debug(cgmGEN.logString_sub(_str_func, 'Shuffle sets'))
        ml_controls = []
        for k in 'base','define','form','prerig':
            dat = md_sourceAll.get(k)
            if dat:
                ml_controls.extend(dat)

        if blockMirror is None:
            log.debug("|{0}| >> Self mirror....".format(_str_func))
            ml_targetControls = ml_controls
        else:
            ml_targetControls = []
            for k in 'base','define','form','prerig':
                dat = md_targetAll.get(k)
                if dat:
                    ml_targetControls.extend(dat)            
            
        int_lenTarget = len(ml_targetControls)
        int_lenSource = len(ml_controls)

        #if int_lenTarget!=int_lenSource:
        for i,mObj in enumerate(ml_controls):
            try:
                log.debug(" {0} > = > {1}".format(mObj.p_nameBase, ml_targetControls[i].p_nameBase))
            except:
                log.debug(" {0} > !! > No match".format(mObj.p_nameBase))
                    
        #return
        #Control sets ===================================================================================
        log.debug(cgmGEN.logString_sub(_str_func, 'Data buffer'))


        l_dat = []
        
        if not ml_controls:
            raise ValueError("No controls")
        
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
        
        #LOC.create(position=reflectAimPoint)
        #LOC.create(position=DIST.get_pos_by_vec_dist(posNew, [reflectUp.x,reflectUp.y,reflectUp.z], 10))
        
        l_dat.append({'pos':posNew,'aimPoint':reflectAimPoint,'up':reflectUp,'aim':reflectAim,'scale':mRoot.scale})
        
        #pprint.pprint(l_dat)
        #return
    
        #Other controls ------------------------------------------------------------------------
        #rootReflectionVector = TRANS.transformDirection(_short,reflectionVector).normalized()
        #log.debug("|{0}| >> reg Reflect: {1}".format(_str_func,rootReflectionVector))
        log.debug("|{0}| >> control dat...".format(_str_func))
        
        for i,mObj in enumerate(ml_controls[1:]):
            log.debug(cgmGEN._str_subLine)                        
            log.debug("|{0}| >> Get {1} | {2}".format(_str_func,i+1,mObj.p_nameBase))
            str_obj = mObj.mNode
            try:_dat = {'source':str_obj,'target':ml_targetControls[i+1].mNode}
            except:
                log.warning(cgmGEN.logString_msg(_str_func, "No dat for {0} | {1}".format(str_obj,i+1)))
                continue
            _dat = {'source':str_obj,'target':ml_targetControls[i+1].mNode}
            
            #Pos... ----------------------------------------------------------------------------------------
            posBase = mObj.p_positionEuclid
            #posNew = (mObj.p_positionEuclid - self.p_positionEuclid).reflect(rootReflectionVector) + self.p_positionEuclid
            posNew = mObj.p_positionEuclid.reflect(reflectionVector)
            log.debug("|{0}| >> Mirror pos [{1}] | base: {2} | result: {3}".format(_str_func, i+1, posBase,posNew))
            #mObj.p_positionEuclid = posNew
            
            _dat['pos'] = posNew
            _dat['baseName'] = mObj.p_nameBase
            
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
                reflectAim = mObj.getAxisVector('z+',asEuclid=True).reflect( reflectionVector)
                reflectUp  = mObj.getAxisVector('y+',asEuclid=True).reflect( reflectionVector)
                #reflectAim = mObj.getTransformDirection( MATH.Vector3(0,0,1)).reflect( reflectionVector )
                #reflectUp  = mObj.getTransformDirection( MATH.Vector3(0,1,0)).reflect( reflectionVector )
                
                #reflectUp = MATH.get_obj_vector(mObj.mNode,'y+')
                
                reflectAimPoint = DIST.get_pos_by_vec_dist(posNew, [reflectAim.x,reflectAim.y,reflectAim.z], 10)
                log.debug("|{0}| >> Mirror rot [{1}] | aim: {2} | up: {3} | point: {4}".format(_str_func, i, reflectAim,reflectUp,reflectAimPoint))
                
                _dat['aimPoint']=reflectAimPoint
                _dat['up'] = reflectUp
                _dat['aim'] = reflectAim
                
                #DIST.create_vectorCurve(posNew, reflectUp, 20, "{0}_up".format(_dat['baseName']))
                
            #Scale ---------------------------------------------------------------------------------
            _noParent = False
            if ATTR.is_locked(str_obj,'translate'):
                _noParent = True
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
            else:
                _dat['scale'] = mc.xform(str_obj,q=True, scale = 1, worldSpace = True, absolute = True)
            _dat['noParent'] = _noParent

            """
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
                log.debug("|{0}| >> scale: {1}".format(_str_func, _dat['scale']))"""
                
            """
             _worldScale = _d.get('worldScale')
                if _worldScale and _noParent is not True:
                    mParent = mCtrl.p_parent
                    if mParent:
                        mCtrl.p_parent = False
                        
                    #mc.xform(mCtrl.mNode, scale = _worldScale, objectSpace = True, absolute = True)
                    mc.xform(mCtrl.mNode, scale = _worldScale, worldSpace = True, absolute = True)
            """
            
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
            #reflectAim = block.formPositions[index].TransformDirection( MATH.Vector3(0,0,1)).reflect( rootReflectionVector )
            #reflectUp  = block.formPositions[index].TransformDirection( MATH.Vector3(0,1,0)).reflect( rootReflectionVector )
            #mirrorBlock.formPositions[index].LookRotation( reflectAim, reflectUp )            
            #l_dat.append([posNew,reflectAimPoint,reflectUp,reflectAim])
            l_dat.append(_dat)
            #l_dat.append({'pos':posNew,'aimPoint':reflectAimPoint,'up':reflectUp,'aim':reflectAim, 'scale':mObj.scale})
            
        #pprint.pprint(l_dat)
        
        #pprint.pprint(vars())
        #return

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
                    
                    if 'simpleRot' in _dat:
                        _rot = _dat.get('simpleRot')
                        if _rot != False:
                            log.debug("|{0}| >> Simple rot mObj: {1} | {2}".format(_str_func,
                                                                                   mObj.p_nameBase,
                                                                                   _rot))            
                            for a,v in list(_rot.items()):
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
                    if 'subShapers' in _dat:
                        ml_subShapers = mObj.msgList_get('subShapers')
                        if not ml_subShapers:
                            raise ValueError("SubShaper data but no datList: {0}".format(mObj))
                        
                        for i_sub,mSub in enumerate(ml_subShapers):
                            _d_sub = _dat['subShapers'][i_sub]
                            for a,d in list(_d_sub.items()):
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
                    if 'loftCurve' in _dat:
                        mLoftCurve = mObj.getMessage('loftCurve',asMeta=True)[0]
                        if not mLoftCurve:
                            raise ValueError("loftCurve data but no datList: {0}".format(mObj))
                        
                        _d_sub = _dat['loftCurve']
                        for a,d in list(_d_sub.items()):
                            if a == 'position':
                                log.debug("|{0}| >> loftCurve position: {1} | {2}".format(_str_func,mLoftCurve,d))
                                mLoftCurve.p_positionEuclid = d                            
                            else:
                                ATTR.set(mLoftCurve.mNode,a,d)
                            
                    #Scale -----------------------------------------------------------------------
                    _noParent = _dat.get('noParent')
                    if _noParent is not True:
                        mParent = mObj.p_parent
                        if mParent:
                            mObj.p_parent = False
                            
                        mc.xform(mObj.mNode, scale = _dat['scale'], worldSpace = True, absolute = True)

                        mObj.p_parent = mParent

                    elif 'simpleScale' in _dat:
                        _scale = _dat.get('simpleScale')
                        if _scale != False:
                            log.debug("|{0}| >> Simple scale mObj: {1} | {2}".format(_str_func,
                                                                                   mObj.p_nameBase,
                                                                                   _scale))            
                            for a,v in list(_scale.items()):
                                ATTR.set(str_obj,'s{0}'.format(a),v)
                        else:
                            continue
                    else:
                        for i,a in enumerate('xyz'):
                            try:
                                ATTR.set(str_obj,'s{0}'.format(a), _dat['scale'][i])
                                #mObj.scale = _dat['scale']
                            except Exception as err:log.debug("|{0}| >> scale err: {1}".format(_str_func,err))            
                except Exception as err:
                    log.debug("|{0}| >> mObj failure: {1} | {2}".format(_str_func,mObj.p_nameShort,err))            
                
        return l_dat,md_remap
    
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
def controlsRig_reset(self):
    try:
        
        _short = self.p_nameShort        
        _str_func = '[{0}] controlsRig_reset'.format(_short)
        log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
        
        self.moduleTarget.rigNull.moduleSet.reset()
        
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)


_d_attrStateMasks = {0:[],
                     1:['basicShape','shapeDirection',
                        'axisAimX','axisAimY','axisAimZ',],
                     2:['blockProfile',
                        'blockScale','proxyShape'],
                     3:['hasJoint','side','position','attachPoint'],
                     4:[]}

_d_attrStateVisOn = {0:['blockState','scaleSetup','numControls',
                        #'proxyShape','shapeDirection','numShapers',
                        #'loftList','shapersAim','loftShape','loftSetup','numSubShapers',
                        ],
                     1:['attachPoint','attachIndex','numRoll',
                        'addAim','addCog','addPivot','addScalePivot','axisAim','axisUp',],
                     2:['ikEnd','ikSetup','ikOrientToWorld','ikBase',
                        'mainRotAxis','hasEndJoint',
                        'ribbonAim','ribbonParam','rigSetup',
                        'segmentMidIKControl','settingsDirection','settingsPlace',
                        'spaceSwitch_fk','ribbonConnectBy','numSpacePivots',
                        'rollCount'],
                     3:['spaceSwitch_direct','squash','squashExtraControl',
                        'squashFactorMax','squashFactorMin','squashMeasure',
                        'offsetMode','proxyDirect',],
                     4:['proxyLoft','proxyGeoRoot']}
_d_attrStateVisOff = {0:[],
                     1:['axisAimX','axisAimY','axisAimZ',],
                     2:['blockProfile','baseSizeX','baseSizeY','baseSizeZ',
                        'blockScale','proxyShape','numShapers',
                        'loftList','shapersAim','loftShape','loftSetup','numSubShapers',
                        ],
                     3:['addAim','addCog','addPivot','addScalePivot','shapeDirection','basicShape',
                        'hasJoint','side','position','numControls','numRoll'],
                     4:['hasEndJoint','numJoints','attachPoint','attachIndex',
                        'ikEnd','ikBase','ikSetup','ikOrientToWorld',
                        'mainRotAxis','hasEndJoint','rollCount',
                        'ribbonAim','ribbonParam','rigSetup','scaleSetup',
                        'segmentMidIKControl','settingsDirection','settingsPlace',
                        'numSpacePivots',
                        'spaceSwitch_direct','squash','squashExtraControl',
                        'squashFactorMax','squashFactorMin','squashMeasure',
                        'offsetMode',
                        'ribbonConnectBy',
                        'spaceSwitch_fk']}

l_aHidden = ('mSystemRoot',
              #u'baseSizeX',
              #u'baseSizeY',
              #u'baseSizeZ',
              'attributeAliasList',
              'cgmColorLock')
l_aKeyable = ()

def attrMask_getBaseMask(self):
    _str_func = ' attrMask_getBaseMask'
    log.debug(cgmGEN.logString_start(_str_func)) 
    _short = self.mNode
    
    l_hidden = []
    l_keyable = []
    for a in self.getAttrs(ud=True):
        _type = ATTR.get_type(_short,a)
        if _type in ['message','string']:
            continue
        
        if ATTR.is_hidden(_short,a):
            l_hidden.append(a)
        if ATTR.is_keyable(_short,a):
            l_keyable.append(a)
            
    _baseDat = self.baseDat or {}
    
            
    _baseDat['aHidden'] = l_hidden
    _baseDat['aKeyable'] = l_keyable
    
    self.baseDat = _baseDat
    #pprint.pprint(_baseDat)
    return True
    
def attrMask_set(self,mode=None,clear=False):
    _str_func = ' attrMask_set'
    log.debug(cgmGEN.logString_start(_str_func))    

    _short = self.mNode
    _baseDat = self.baseDat or {}
    l_hidden = l_aHidden#_baseDat.get('aHidden',[])
    l_keyable = l_aKeyable#_baseDat.get('aKeyable',[])
    
    if not l_hidden and not l_keyable:
        return log.warning(cgmGEN.logString_msg(_str_func,"[{0}] Necessary baseDat not found. This block needs to be rebuilt to enable".format(_short)))
    
    if mode is None:
        mode = self.blockState
    
    for a in self.getAttrs(ud=True):
        if a in l_hidden:
            log.debug(cgmGEN.logString_msg(_str_func,'Hiding | {0}'.format(a)))                
            ATTR.set_hidden(_short,a,1)
        else:
            ATTR.set_hidden(_short,a,0)
            log.debug(cgmGEN.logString_msg(_str_func,'showing | {0}'.format(a)))
            
        if a in l_keyable:
            log.debug(cgmGEN.logString_msg(_str_func,'keyable |{0}'.format(a)))
            ATTR.set_keyable(_short,a,1)
        else:
            log.debug(cgmGEN.logString_msg(_str_func,'not keyable | {0}'.format(a)))
            ATTR.set_keyable(_short,a,0)
    if clear: return
    else:
        _state = 1
        l_attrs = get_stateChannelBoxAttrs(self,mode)
        
        l_baseHidden = l_aHidden#self.baseDat['aHidden']
    
        for a in self.getAttrs(ud=True):
            if a not in l_attrs:
                if a in l_baseHidden:
                    continue
                if not ATTR.is_hidden(_short,a):
                    if not ATTR.get_children(_short,a):
                        log.debug(cgmGEN.logString_msg(_str_func,'Set {0} | {1}'.format(bool(_state),a)))
                        ATTR.set_hidden(_short,a,_state)
    
def get_stateChannelBoxAttrs(self,mode = None,report=False):
    try:
        _str_func = ' get_stateChannelBoxAttrs'
        log.debug(cgmGEN.logString_start(_str_func))

        _short = self.mNode
        
        if mode is None:
            _intState = self.blockState
        else:
            _intState = BLOCKGEN.validate_stateArg(mode)[0]
        log.debug("|{0}| >> state: {1}".format(_str_func,_intState))
        
        mBlockModule = self.p_blockModule
        #reload(mBlockModule)
        
        def updateDictLists(d1,d2):
            for k,l in list(d1.items()):
                _dat = d2.get(k)
                if _dat:
                    l.extend(_dat)
                    d1[k] = l
        try:
            d_attrsFromModule = mBlockModule._d_attrStateMasks
            log.debug(cgmGEN.logString_msg(_str_func,'Found blockModule attrStateMask dat'))
        except:d_attrsFromModule={}
        try:
            d_attrsOnFromModule = mBlockModule._d_attrStateOn
            log.debug(cgmGEN.logString_msg(_str_func,'Found blockModule _d_attrStateOn dat'))
        except:d_attrsOnFromModule={}
        try:
            d_attrsOffFromModule = mBlockModule._d_attrStateOff
            log.debug(cgmGEN.logString_msg(_str_func,'Found blockModule _d_attrStateOff dat'))
        except:d_attrsOffFromModule={}
        
        try:
            l_blockTypeMask = mBlockModule.d_attrProfileMask[self.blockProfile]
            log.debug(cgmGEN.logString_msg(_str_func,'Found blockModule l_blockTypeMask'))
            #pprint.pprint(l_blockTypeMask)
        except:l_blockTypeMask=[]        
        
        
        __d_attrStateVisOn = copy.copy(_d_attrStateVisOn)
        updateDictLists(__d_attrStateVisOn,d_attrsOnFromModule)
        
        __d_attrStateVisOff = copy.copy(_d_attrStateVisOff)
        updateDictLists(__d_attrStateVisOff,d_attrsOffFromModule)
        
        #First pass...
        l_attrs = []
        
        for a in self.getAttrs(ud=True):
            _type = ATTR.get_type(_short,a)
            if ATTR.is_keyable(_short,a):
                l_attrs.append(a)
            elif not ATTR.is_hidden(_short,a):
                l_attrs.append(a)
            elif _type in ['string','enum']:
                if '_' in a and not a.endswith('dict'):
                    l_attrs.append(a)
                elif a.startswith('name'):
                    l_attrs.append(a)
                    
            if _type in ['float3','message']:
                try:l_attrs.remove(a)
                except:pass
        for a in ['blockScale']:
            if ATTR.has_attr(_short,a) and ATTR.is_keyable(_short,a):
                l_attrs.append(str(a))
                
        #Make sure no core stuff sneaked through
        _baseDat = self.baseDat or {}
        l_hidden = l_aHidden#_baseDat.get('aHidden',[])
        for a in l_hidden:
            try:l_attrs.remove(a)
            except:pass
            
        for a in ['mClass','mNodeID','mClassGrp','blockType','blockProfile','buildProfile',
                  'baseDat','blockMirror','blockDat','version',
                  'blockParent','cgmDirection','cgmPosition','moduleTarget','side']:
            try:l_attrs.remove(a)
            except:pass            
        
        #Process dicts ======================================================
        d_mask = copy.copy(_d_attrStateMasks)
        d_mask.update(d_attrsFromModule)
        l_neverOn = []
        d_attrOn = {}
        d_attrOnCheck = {}
        
        for i,l in list(__d_attrStateVisOn.items()):
            d_attrOn[i] = []
            for a in l_attrs:
                for a2 in l:
                    if a2 == a:
                        d_attrOn[i].append(a)
                        d_attrOnCheck[a] = i
                        log.debug(cgmGEN.logString_msg(_str_func,'on [{0}] | {1}'.format(i,a)))                
                        
                    elif a.startswith(a2):
                        d_attrOn[i].append(a)
                        d_attrOnCheck[a] = i
                        log.debug(cgmGEN.logString_msg(_str_func,'on [{0}] | {1}'.format(i,a)))                
        for a in l_attrs:
            if d_attrOnCheck.get(a) is None:
                d_attrOn[0].append(a)
                    
        d_attrOff = {}
        for i,l in list(__d_attrStateVisOff.items()):
            log.debug(cgmGEN.logString_msg(_str_func,'Off check [{0}] | {1}'.format(i,l)))                
            
            d_attrOff[i] = []
            for a in l_attrs:
                for a2 in l:
                    if a2 == a:
                        d_attrOff[i].append(a)
                    elif a.startswith(a2):
                        d_attrOff[i].append(a)

                    
                    #d_attrOff[a] = i
                    
        #pprint.pprint(d_attrOn)
        #pprint.pprint(d_attrOff)
        
        #Build our list =============================================
        l_use = []
        l_removed = []
        #pprint.pprint(vars())
        for i in range(0,_intState+1):        
            l_use.extend(d_attrOn[i])
            log.debug(cgmGEN.logString_msg(_str_func,'adding [{0}]'.format(i)))                
            #pprint.pprint(d_attrOn[i])
            
        for i  in range(0,_intState+1):
            _off = d_attrOff[i]
            if not i and l_blockTypeMask:
                _off.extend(l_blockTypeMask)
            for a in _off:
                if ATTR.datList_exists(_short,a):
                    for a2 in ATTR.datList_getAttrs(_short,a):
                        if a2 in l_use:
                            l_use.remove(a2)
                            l_removed.append(a2)
                if a in l_use:
                    log.debug(cgmGEN.logString_msg(_str_func,'Hiding | {0}'.format(a)))                
                    l_use.remove(a)
                    l_removed.append(a)
                    

        l_use.sort()
        

        if report:
            pprint.pprint(l_use)
        return l_use
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    
def uiQuery_getStateAttrs(self,mode = None,report=True):
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
            if ATTR.is_keyable(_short,a):
                l_attrs.append(a)
            elif not ATTR.is_hidden(_short,a):
                l_attrs.append(a)
            elif _type in ['string']:
                if '_' in a and not a.endswith('dict'):
                    l_attrs.append(a)
                elif a.startswith('name'):
                    l_attrs.append(a)
            if _type in ['float3']:
                l_attrs.remove(a)
        
        for a in ['visibility','blockScale']:
            if ATTR.has_attr(_short,a) and ATTR.is_keyable(_short,a):
                l_attrs.append(str(a))
                
        for a in ['side','position']:
            if a in l_attrs:
                l_attrs.remove(a)
        
        if _intState > 0:#...form
            l_mask = []
            log.debug("|{0}| >> form cull...".format(_str_func))            
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
        if report:
            pprint.pprint(l_attrs)
        return l_attrs
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)


def uiQuery_filterListToAttrDict(l=[],d={}):
    '''
    Call to process a attr state dict against a given list of attributes
    '''
    if not l and d:
        raise ValueError("Must have list and dict")
    
    l_cull = copy.copy(l)
    l_cull = LISTS.get_noDuplicates(l_cull)
    _keys = list(d.keys())
    _keys.sort()
    l_order =['define','profile','basic','name',
              'form','proxySurface','prerig',
              'skeleton',
              'rig','space','squashStretch']
    l_order.reverse()
    
    for k in l_order:
        if k in _keys:
            _keys.remove(k)
            _keys.insert(0,k)
            
    l_end = ['data','wiring','advanced']
    for k in l_end:
        if k in _keys:
            _keys.remove(k)
            _keys.append(k)
            
    #Process... ---------------------------------------------------------------------
    _res = {}
    _l_resOrder = []
    _l_done = []
    for k in _keys:
        _dTest = d.get(k,[])
        
        for a in _dTest:
            log.debug("Checking: {} | {}".format(k,a))            
            if a in _l_done:
                continue
            if a in l_cull:
                if k not in _l_resOrder:_l_resOrder.append(k)
                if not _res.get(k):_res[k] = []
                log.debug("Found.".format(a,k))
                _res[k].append(a)
                l_cull.remove(a)
                _l_done.append(a)
    if l_cull:
        log.warning("Extra attributes..." + cgmGEN._str_hardBreak)
        pprint.pprint(l_cull)
        log.info(cgmGEN._str_hardBreak)
        
        #if not _res.get('extra'):_res['extra'] = []
        
        _res['extra'] = l_cull
        _l_resOrder.append('extra')
        
    return _l_resOrder, _res
        
    
def uiQuery_getStateAttrDictFromModule(mBlockModule = None, report = False, unknown = True):
    _str_func = ' uiQuery_getStateAttrDict'
    log.debug(cgmGEN.logString_start(_str_func))
        
    _res = {}
    _done = []
        
    _d = {}
    try:
        _d = mBlockModule.d_attrStateMask
    except Exception as err:
        log.error(err)
    
    d_use = CGMDICT.blendDat(BLOCKSHARE.d_uiAttrDict,_d)
        
    for k,l in list(d_use.items()):
        log.debug(cgmGEN.logString_sub(_str_func, k))
        if report:pprint.pprint(l)
        _tmp = []
        for s in l:
            #if s.endswith('List') or s in ['numSubShapers','rollCount']:
            #if self.hasAttr(s):
            #    if s in _done:
            #        log.debug("Already done: {0}".format(s))
            #    else:
            _tmp.append(s)
            _done.append(s)
        _tmp.sort()
        _res[k] = _tmp
        
    if report:
        pprint.pprint(_res)
        
        
    return _res

def uiQuery_getStateAttrDict(self,report = False, unknown = True):
    _str_func = ' uiQuery_getStateAttrDict'
    log.debug(cgmGEN.logString_start(_str_func))
    _short = self.mNode
        
    _res = {}
    _done = []
        
    mBlockModule = self.p_blockModule
    _d = {}
    try:
        _d = mBlockModule.d_attrStateMask
    except Exception as err:
        log.error(err)
    
    d_use = CGMDICT.blendDat(BLOCKSHARE.d_uiAttrDict,_d)
        
    for k,l in list(d_use.items()):
        log.debug(cgmGEN.logString_sub(_str_func, k))
        if report:pprint.pprint(l)
        _tmp = []
        for s in l:
            if s.endswith('List') or s in ['numSubShapers','rollCount']:
                if ATTR.datList_exists(_short,s):
                    for s2 in ATTR.datList_getAttrs(_short,s):
                        _tmp.append(s2)
                        _done.append(s2)
            if self.hasAttr(s):
                if s in _done:
                    log.debug("Already done: {0}".format(s))
                else:
                    _tmp.append(s)
                    _done.append(s)
        _tmp.sort()
        _res[k] = _tmp
        
    if report:
        pprint.pprint(_res)
        
    if unknown:
        _tmp = []
        for a in self.getAttrs(ud=True):
            if a not in _done:
                _tmp.append(str(a))
        _tmp.sort()
        log.info(cgmGEN.logString_sub(_str_func,'Unknown...'))
        pprint.pprint(_tmp) 
        
    return _res

def shapeDirection_toBaseDat(self):
    _d_baseDatFromDirection = {'x+':{'end':[1,0,0],'up':[0,1,0]},
                               'x-':{'end':[-1,0,0],'up':[0,1,0]},
                               'y+':{'end':[0,1,0],'up':[0,0,-1]},
                               'y-':{'end':[0,-1,0],'up':[0,0,1]},
                               'z+':{'end':[0,0,1],'up':[0,1,0]},
                               'z-':{'end':[0,0,-1],'up':[0,1,0]}}
    _shapeDirection = self.getEnumValueString('shapeDirection')
    
    _dBase = self.baseDat or {}
    if issubclass(type(_dBase),dict):
        _dBase = {}
        
    _dBase.update(_d_baseDatFromDirection.get(_shapeDirection,{}))
    _dBase['lever'] = [-1 * v for v in _dBase['end']]
    self.baseDat = _dBase            

#=============================================================================================================
#>> State Changing
#=============================================================================================================
def formDelete(self):
    _str_func = 'formDelete'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError("|{0}| >> referenced node: {1}".format(_str_func,self.mNode))

    _str_state = self.getEnumValueString('blockState')
    
    #if _str_state != 'form':
        #raise ValueError,"[{0}] is not in form state. state: {1}".format(self.mNode, _str_state)

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    #self.blockState = 'form>define'#...buffering that we're in process

    mBlockModule = self.p_blockModule
    l_blockModuleKeys = list(mBlockModule.__dict__.keys())
    if 'formDelete' in l_blockModuleKeys:
        log.debug("|{0}| >> BlockModule formDelete call found...".format(_str_func))
        self.atBlockModule('formDelete')
    
    if self.getMessage('formNull'):
        mc.delete(self.getMessage('formNull'))
    if self.getMessage('noTransFormNull'):
        mc.delete(self.getMessage('noTransFormNull'))
    
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
    
    d_links = get_stateLinks(self, 'form')
    msgDat_delete(self,d_links)
    
    for mObj in self.msgList_get('formStuff'):
        try:mObj.delete()    
        except Exception as err:
            pass
    self.blockState = 'define'#...yes now in this state
    return True

def templateAttrLock(self,v=1):
    self.template = v

#@cgmGEN.Wrap_exception
def test_exception(self,*args,**kws):
    try:
        localTest = 'hello world'
        raise ValueError("here")
    except:
        cgmGEN.log_tb()
        raise

def test_nestedException(self,*args,**kws):
    try:
        localTest = 'hello nested world'    
        test_exception(self,*args,**kws)
    except:
        cgmGEN.log_tb()
        raise    
    
def form_segment(self,aShapers = 'numShapers',aSubShapers = 'numSubShapers',
                     loftShape=None,l_basePos = None, baseSize=1.0,
                     sizeWidth = 1.0, sizeLoft=1.0,
                     side = None,orientHelperPlug = 'orientHelper',formAim='toEnd',
                     mFormNull = None,mNoTransformNull = None,
                     mDefineEndObj=None):
    """
    Factored out our segment setup to clean up 
    """
    _str_func = 'form_segment'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    _short = self.p_nameShort
    mc.select(cl=1)#...why maya....
    #_size_handle = baseSize
    #_size_loft = sizeLoft
    _size_width = sizeWidth
    
    _size_handle = 1.0
    _size_loft = 1.0
    
    _side = side
    _loftShape = loftShape
    _l_basePos = l_basePos
    md_handles = {}
    ml_handles = []
    ml_loftHandles = []
    md_loftHandles ={}
    ml_shapers = []
    ml_handles_chain = []
    _formAim = formAim
    
    _short = self.mNode        
    _int_shapers = self.getMayaAttr(aShapers)
    _int_sub = self.getMayaAttr(aSubShapers)        
    _loftSetup = self.getEnumValueString('loftSetup')
    _loftShape = self.getEnumValueString('loftShape')
    
    _baseName = self.cgmName
    if not _baseName:
        _baseName = self.blockType
    
    #Loft Shapes...-----------------------------------------------------------------------
    if _loftSetup == 'loftList':
        _l_loftShapes =  ATTR.datList_get(_short,'loftList',enum=True) or []
        if len(_l_loftShapes) != _int_shapers:
            log.warning("|{0}| >> Not enough shapes in loftList. Padding with loftShape".format(_str_func,i,_loftShape))
            while len(_l_loftShapes) < _int_shapers:
                _l_loftShapes.append(self.loftShape)
    else:
        _l_loftShapes = [_loftShape for i in range(_int_shapers)]

    log.debug("|{0}| >> loftShapes: {1}".format(_str_func,_l_loftShapes)) 
    
    #Subshaper count -------------------------------------------------------------------------
    l_numSubShapers =  self.datList_get('numSubShapers')
    int_shapers = self.getMayaAttr(aShapers)
    int_sub = self.getMayaAttr(aSubShapers)
    if not l_numSubShapers:
        l_numSubShapers = [int_sub for i in range(int_shapers-1)]
    log.info("|{0}| >> l_numSubShapers: {1}".format(_str_func,l_numSubShapers)) 

    
    mHandleFactory = self.asHandleFactory()
    mRootUpHelper = self.vectorUpHelper
    #_mVectorAim = MATH.get_obj_vector(self.vectorEndHelper.mNode,asEuclid=True)
    _mVectorUp = MATH.get_obj_vector(mRootUpHelper.mNode,'y+',asEuclid=True)            
    #pprint.pprint(vars())
    for i,n in enumerate(['start','end']):
        log.debug("|{0}| >> {1}:{2}...".format(_str_func,i,n)) 
        #mHandle = mHandleFactory.buildBaseShape('sphere2',baseSize = _size_handle, shapeDirection = 'y+')
        crv = CURVES.create_fromName('sphere2', [_size_handle,_size_handle,.2* _size_handle], direction = 'y+',baseSize=1)
        mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
        
        mHandle.p_parent = mFormNull
    
        mHandle.resetAttrs()
    
        self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
        mHandle.doStore('cgmType','formHandle')
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
        #mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
    
        mHandleFactory.color(mHandle.mNode)            
        mHandle.p_position = _l_basePos[i]
    
        md_handles[n] = mHandle
        ml_handles.append(mHandle)
    
        md_loftHandles[n] = mLoftCurve                
        ml_loftHandles.append(mLoftCurve)
    
        mLoftCurve.p_parent = mFormNull
        mTransformedGroup = mLoftCurve.getMessageAsMeta('transformedGroup')
        if not mTransformedGroup:
            mTransformedGroup = mLoftCurve.doGroup(True,True,asMeta=True,typeModifier = 'transformed',setClass='cgmObject')
        mHandle.doConnectOut('scale', "{0}.scale".format(mTransformedGroup.mNode))
        mc.pointConstraint(mHandle.mNode,mTransformedGroup.mNode,maintainOffset=False)
        #mc.scaleConstraint(mHandle.mNode,mTransformedGroup.mNode,maintainOffset=True)
    
        mBaseAttachGroup = mHandle.doGroup(True,True, asMeta=True,typeModifier = 'attach')
    
    #Constrain the define end to the end of the form handles
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

    mBaseOrientCurve.p_parent =  mFormNull
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
    #reload(CORERIG)
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
            crv = CURVES.create_fromName('sphere2', [_size_handle,_size_handle,.2* _size_handle], direction = 'y+',baseSize=1)
            mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)

            self.copyAttrTo('cgmName',mHandle.mNode,'cgmName',driven='target')
            mHandle.doStore('cgmType','formHandle')
            mHandle.doStore('cgmNameModifier',"form_{0}".format(i+1))
            mHandle.doName()                

            _short = mHandle.mNode
            ml_midHandles.append(mHandle)
            mHandle.p_position = p

            mHandle.p_parent = mFormNull
            #mHandle.resetAttrs()

            mHandleFactory.setHandle(mHandle.mNode)
            mLoftCurve = mHandleFactory.rebuildAsLoftTarget('loft' + _l_loftShapes[i+1][0].capitalize() + ''.join(_l_loftShapes[i+1][1:]),#_loftShape,
                                                            _size_loft,
                                                            shapeDirection = 'z+',rebuildHandle = False)
            #mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
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
            
            BLOCKSHAPES.attachToCurve(mHandle, mMidTrackCurve, parentTo = mNoTransformNull, trackLink='transformedGroup')
            
            #_res_attach = RIGCONSTRAINT.attach_toShape(mTransformedGroup.mNode, mMidTrackCurve.mNode, 'conPoint')
            #TRANS.parent_set(_res_attach[0], mNoTransformNull.mNode)

            mTransformedGroup.resetAttrs('rotate')


            mLoftCurve.p_parent = mFormNull
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
            CORERIG.colorControl(mLoftCurve.mNode,_side,'main',transparent = True)

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
            if _formAim == 'toEnd':
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
            
        if _formAim == 'orientToHandle':
            mc.orientConstraint([mHandle.mNode],
                                mTransformedGroup.mNode, maintainOffset = False)
        else:
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
                mAimForward.p_parent = mHandle.p_parent#mLoft
                mAimForward.doStore('cgmName',mHandle)                
                mAimForward.doStore('cgmTypeModifier','forward')
                mAimForward.doStore('cgmType','aimer')
                mAimForward.doName()
    
                mAimBack = mLoft.doCreateAt()
                mAimBack.p_parent = mHandle.p_parent
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
            log.debug("|{0}| >> {2} | Aiming Handle: {1}".format(_str_func,mHandle,_formAim))
            _aimForward = ml_handles_chain[i+1].mNode
            
            mHandleAimGroup = mHandle.getMessageAsMeta('transformedGroup')
            if not mHandleAimGroup:
                mHandleAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'transformed')

            if _formAim == 'toEnd':
                mc.aimConstraint(md_handles['end'].mNode,
                                 mHandleAimGroup.mNode, maintainOffset = False,
                                 aimVector = [0,0,1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = 'objectrotation', 
                                 worldUpVector = [0,1,0])
            elif _formAim == 'chain':
                mc.aimConstraint(_aimForward, mHandleAimGroup.mNode, maintainOffset = False,
                                 aimVector = [0,0,1], upVector = [0,1,0], 
                                 worldUpObject = mBaseOrientCurve.mNode,
                                 worldUpType = 'objectrotation', 
                                 worldUpVector = [0,1,0])

        """
        if mHandle in [md_handles['start'],md_handles['end']]:
            _lock = []
            #if mHandle == md_handles['start']:
            #    _lock.append('rotate')

            ##ATTR.set_alias(mHandle.mNode,'sy','handleScale')    
            ##ATTR.set_standardFlags( mHandle.mNode, _lock)
            ##mHandle.doConnectOut('sy',['sx','sz'])
            #ATTR.set_standardFlags( mHandle.mNode, _lock)

        else:
            ATTR.set_standardFlags( mHandle.mNode, ['sz'])
            ATTR.connect('{0}.sy'.format(mHandle.mNode), '{0}.sz'.format(mHandle.mNode))"""


    ml_shapers = copy.copy(ml_handles_chain)
    #>>> shaper handles =======================================================================
    if _int_sub or l_numSubShapers:
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
            
            _numSubShapers = l_numSubShapers[i]

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
                mCluster = cgmMeta.asMeta(_res[1])
                mCluster.p_parent = mFormNull
                mCluster.v = 0
                mc.pointConstraint(mPair[ii].mNode,
                                   mCluster.mNode,maintainOffset=True)
                l_clusters.append(_res)

            mLinearCurve.parent = mNoTransformNull
            mLinearCurve.rename('seg_{0}_trackCrv'.format(i))



            #Tmp loft mesh -------------------------------------------------------------------
            _l_targets = [mObj.loftCurve.mNode for mObj in mPair]
            log.debug(_l_targets)
            _res_body = mc.loft(_l_targets, o = True, d = 3, po = 0 )
            _str_tmpMesh =_res_body[0]

            l_scales_seg = []

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
                mHandle.doStore('cgmNameModifier','form_{0}_sub_{1}'.format(i,ii))
                mHandle.doStore('cgmType','shapeHandle')
                mHandle.doName()

                mHandle.p_parent = mFormNull

                mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master')
                mGroup.p_parent = mFormNull

                _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,[mPair[0].mNode,mPair[1].mNode])


                if _leverLoftAimMode:
                    upObj = md_handles['lever'].mNode
                else:
                    upObj = mBaseOrientCurve.mNode



                
                BLOCKSHAPES.attachToCurve(mHandle, mLinearCurve, parentTo = mNoTransformNull, trackLink='masterGroup')
                """
                _res_attach = RIGCONSTRAINT.attach_toShape(mGroup.mNode, 
                                                           mLinearCurve.mNode,
                                                           'conPoint')
                TRANS.parent_set(_res_attach[0], mNoTransformNull.mNode)"""
                # Has to be after the bind
                _scale = mc.scaleConstraint([mPair[0].mNode,mPair[1].mNode],mGroup.mNode,maintainOffset = False)#Point contraint loc to the object

                for c in [_scale]:
                    CONSTRAINT.set_weightsByDistance(c[0],_vList)
                    
                mc.aimConstraint([_end], mGroup.mNode, maintainOffset = False, #skip = 'z',
                                 aimVector = [0,0,1], upVector = [0,1,0],
                                 worldUpObject = upObj,
                                 worldUpType = 'objectrotation', worldUpVector = [0,1,0])                                        

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

            #Form Loft Mesh -------------------------------------
            #mFormLoft = self.getMessage('formLoftMesh',asMeta=True)[0]        
            #for s in mFormLoft.getShapes(asMeta=True):
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
    
    
    controller_wireHandles(self,ml_handles + ml_shapers,'form')
    controller_walkChain(self,ml_handles_chain,'form')
    
    """
    ml_done = []
    if cgmGEN.__mayaVersion__ >= 2018:
    
        for mHandle in ml_handles + ml_shapers:
            if mHandle in ml_done:
                continue
            if not mHandle:
                continue
            mLoft = mHandle.getMessageAsMeta('loftCurve')
            if mLoft:
                mLoft = cgmMeta.controller_get(mLoft)
                mLoft.visibilityMode = 2
                ml_done.append(mLoft)
            mController = cgmMeta.controller_get(mHandle)
            mController.visibilityMode = 2                            
            ml_done.append(mController)
                
                
                
        for mObj in ml_done:
            try:
                ATTR.connect("{0}.visProximityMode".format(self.mNode),
                             "{0}.visibilityMode".format(mObj.mNode))    
            except Exception,err:
                log.error(err)

            self.msgList_append('formStuff',mObj)
            """
    return md_handles,ml_handles,ml_shapers,ml_handles_chain


def jointRadius_guess(self,sizeTarget = None):
    _str_func = 'jointRadius_guess'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    _initial = self.jointRadius
    _done = False
    if sizeTarget:
        _size = TRANS.bbSize_get(sizeTarget,True)
        #print _size
        #print MATH.average(_size[0],_size[1])
        _v = (MATH.average(_size[0],_size[1]) * .1)
        if self.jointRadius < _v:
            log.info("|{0}| >> changing from sizeTarget | {1} | {2}".format(_str_func,_v,sizeTarget))
            self.jointRadius = _v
            _done = True
    else:
        _base = get_shapeOffset(self) * 2
        if self.jointRadius < _base:
            self.jointRadius = _base   

    log.info("|{0}| >> Initial: {1} | Now: {2}".format(_str_func,_initial,self.jointRadius))
    return self.jointRadius


    
def form(self):
    _str_func = 'form'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError("|{0}| >> referenced node: {1}".format(_str_func,self.mNode))

    _str_state = self.getEnumValueString('blockState')
    
    if _str_state == 'form':
        log.debug("|{0}| >> Already in form state...".format(_str_func))                    
        return True
    elif _str_state != 'define':
        raise ValueError("[{0}] is not in define state. state: {1}".format(self.mNode, _str_state))

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    #self.blockState = 'define>form'#...buffering that we're in process

    mBlockModule = self.p_blockModule

    if 'form' in list(mBlockModule.__dict__.keys()):
        log.debug("|{0}| >> BlockModule call found...".format(_str_func))            
        self.atBlockModule('form')

    #for mShape in self.getShapes(asMeta=True):
        #mShape.doName()

    self.blockState = 'form'#...yes now in this state
    return True

def prerig(self):
    _str_func = 'prerig'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError("|{0}| >> referenced node: {1}".format(_str_func,self.mNode))

    _str_state = self.getEnumValueString('blockState')
    
    if _str_state == 'prerig':
        log.debug("|{0}| >> Already in prerig state...".format(_str_func))                    
        return True
    elif _str_state != 'form':
        raise ValueError("[{0}] is not in define form. state: {1}".format(self.mNode, _str_state))

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    #self.blockState = 'form>prerig'#...buffering that we're in process

    mBlockModule = self.p_blockModule

    if 'prerig' in list(mBlockModule.__dict__.keys()):
        log.debug("|{0}| >> BlockModule prerig call found...".format(_str_func))
        #reload(mBlockModule)
        mBlockModule.prerig(self)
        #self.atBlockModule('prerig')

    self.blockState = 'prerig'#...yes now in this state
    return True

def prerigDelete(self):
    _str_func = 'prerigDelete'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError("|{0}| >> referenced node: {1}".format(_str_func,self.mNode))

    _str_state = self.getEnumValueString('blockState')
    
    if _str_state != 'prerig':
        raise ValueError("[{0}] is not in prerig state. state: {1}".format(self.mNode, _str_state))

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    #self.blockState = 'prerig>form'#...buffering that we're in process

    mBlockModule = self.p_blockModule
    l_blockModuleKeys = list(mBlockModule.__dict__.keys())
    
    if 'prerigDelete' in l_blockModuleKeys:
        log.debug("|{0}| >> BlockModule prerigDelete call found...".format(_str_func))
        self.atBlockModule('prerigDelete')
    
    d_links = get_stateLinks(self, 'prerig')
    msgDat_delete(self,d_links)
    
    self.blockState = 'form'#...yes now in this state
    return True


def skeleton(self):
    _str_func = 'skeleton'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError("|{0}| >> referenced node: {1}".format(_str_func,self.mNode))

    _str_state = self.getEnumValueString('blockState')
    
    if _str_state == 'skeleton':
        log.debug("|{0}| >> Already in skeleton state...".format(_str_func))                    
        return True
    elif _str_state != 'prerig':
        raise ValueError("[{0}] is not in prerig form. state: {1}".format(self.mNode, _str_state))

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    #self.blockState = 'prerig>skeleton'#...buffering that we're in process

    mBlockModule = self.p_blockModule
    
    for c in ['skeleton_build','build_skeleton']:
        if c in list(mBlockModule.__dict__.keys()):
            log.debug("|{0}| >> BlockModule {1} call found...".format(_str_func,c))            
            if not self.atBlockModule(c):
                self.blockState = 'prerig'#...yes now in this state
                return False

    self.blockState = 'skeleton'#...yes now in this state
    return True


def skeleton_getBind(self,select=False, tag = False, warn = True):
    _str_func = 'skeleton_getBind'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    _d = {'left':'Left','right':'Right'}
    
    mModule = self.getMessageAsMeta('moduleTarget')
    if mModule:
        mRigNull = mModule.rigNull
        if not mRigNull:
            #closeOut()
            return log.error(cgmGEN.logString_sub(_str_func,'No rigNull'))
        # return log.error("|{0}| >> No joints found".format(_str_func))                
        if mRigNull:
            ml_joints = mRigNull.msgList_get('moduleJoints')
            if not ml_joints:
                if warn: return log.error("|{0}| >> No joints found".format(_str_func))
                return False
            
            if tag:
                for mJnt in ml_joints:
                    _name = mJnt.mNode#...get our name string to avoid multiple calls
                    _tag = NAMETOOLS.get_combinedNameDict(_name,['cgmDirection','cgmType'])#...get tag via name dict without direction or type
                    
                
                    d = mJnt.getNameDict()#...get name dict
                    _s = _d.get(d.get('cgmDirection'),'Center')#...get the maya side value from a simple dict with 'Center' default
                    log.debug(cgmGEN.logString_msg(_str_func,"Tag: '{0}' | side '{1}' | {2}".format(_tag,_s,_name)))
                    
                    #set our stuff
                    ATTR.set(_name,'side',_s)
                    mJnt.type = 18
                    mJnt.otherType = _tag                    
                
            
            if select:
                mc.select([mJnt.mNode for mJnt in ml_joints],add=True)
            
            return ml_joints
               
    
    
def skeleton_delete(self):
    _str_func = 'skeleton_delete'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    if self.isReferenced():
        raise ValueError("|{0}| >> referenced node: {1}".format(_str_func,self.mNode))

    _str_state = self.getEnumValueString('blockState')
    
    if _str_state != 'skeleton':
        raise ValueError("[{0}] is not in skeleton state. state: {1}".format(self.mNode, _str_state))

    #>>>Children ------------------------------------------------------------------------------------
    def closeOut():
        d_links = get_stateLinks(self, 'skeleton')
        msgDat_delete(self,d_links)
        self.blockState = 'prerig'#...yes now in this state
        
    #>>>Meat ------------------------------------------------------------------------------------
    #self.blockState = 'skeleton>prerig'#...buffering that we're in process

    mBlockModule = self.p_blockModule
    l_blockModuleKeys = list(mBlockModule.__dict__.keys())
    
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
        raise ValueError("|{0}| >> referenced node: {1}".format(_str_func,self.mNode))

    _str_state = self.getEnumValueString('blockState')
    
    if _str_state == 'rig':
        log.debug("|{0}| >> Already in rig state...".format(_str_func))                    
        return True
    elif _str_state != 'skeleton':
        raise ValueError("[{0}] is not in skeleton form. state: {1}".format(self.mNode, _str_state))

    #>>>Children ------------------------------------------------------------------------------------

    #>>>Meat ------------------------------------------------------------------------------------
    #self.blockState = 'skeleton>rig'#...buffering that we're in process
    if not 'autoBuild' in list(kws.keys()):
        kws['autoBuild'] = True
    
    try:self.asRigFactory(**kws)
    except Exception as err:
        self.blockState = 'skeleton'
        #cgmGEN.cgmException(Exception,err)
        raise err
    
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
        raise ValueError("|{0}| >> referenced node: {1}".format(_str_func,self.mNode))

    _str_state = self.getEnumValueString('blockState')
    
    if _str_state != 'rig':
        raise ValueError("[{0}] is not in rig state. state: {1}".format(self.mNode, _str_state))


    #>>>Meat ------------------------------------------------------------------------------------
    #self.blockState = 'rig>skeleton'#...buffering that we're in process
    
    mModuleTarget = self.moduleTarget
    mModuleTarget.rig_disconnect()
    """
    CGMUI.(winName='Mesh Slice...', 
                                statusMessage='Progress...', 
                                startingProgress=1, 
                                interruptableState=True)		    """
    
    if mModuleTarget:
        log.debug("|{0}| >> ModuleTarget: {1}".format(_str_func,mModuleTarget))
        ml_blockControls = self.UTILS.controls_get(self,True,True,True)
        for mNode in ml_blockControls:
            try:ml_blockControls.extend(mNode.getShapes(asMeta=1))
            except:pass
            
        if mModuleTarget.mClass ==  'cgmRigModule':
            self.template = False
            try:self.noTransFormNull.template=True
            except:pass
            mRigNull = mModuleTarget.getMessageAsMeta('rigNull')
            
            _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
            if _bfr:
                log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
                mc.delete([mObj.mNode for mObj in _bfr])
            mFaceSet = mRigNull.getMessageAsMeta('faceSet')
            
            #Rig nodes....
            
            ml_rigNodes = mRigNull.getMessageAsMeta('rigNodes')
            try:_progressBar = CGMUI.doStartMayaProgressBar(stepMaxValue=len(ml_rigNodes))
            except:_progressBar = None                    
            try:
                for mNode in ml_rigNodes:
                    if mNode in [mModuleTarget,mRigNull,mFaceSet]:
                        continue
                    if mNode in ml_blockControls:
                        log.debug("|{0}| >> block control in rigNodes: {1}".format(_str_func,mNode))
                        continue
                    _str = "|{0}| >> deleting: {1}".format(_str_func,mNode)
                    if _progressBar:
                        CGMUI.progressBar_set(_progressBar,step=1,
                                              status = _str)                
                    try:
                        log.debug(_str)                     
                        mNode.delete()
                    except:pass
                        #log.debug("|{0}| >> failed...".format(_str_func,mNode)) 
            except:pass
            finally:
                if _progressBar:CGMUI.doEndMayaProgressBar()                
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
    l_blockModuleKeys = list(mBlockModule.__dict__.keys())
    if 'rigDelete' in l_blockModuleKeys:
        log.debug("|{0}| >> BlockModule rigDelete call found...".format(_str_func))
        self.p_blockModule.rigDelete(self)
    
    self.blockState = 'skeleton'#...yes now in this state
    set_blockNullFormState(self, state=False, define=False)
    return True

#@cgmGEN.Timer
def changeState(self, state = None, rebuildFrom = None, forceNew = False,checkDependency=True,**kws):
    #try:
    _str_func = 'changeState'
    log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
    
    mc.select(cl=True)
    
    if self.isReferenced():
        raise ValueError("Referenced node. Cannot verify")
    
    if rebuildFrom:
        log.debug("|{0}| >> Rebuid from: {1}".format(_str_func,rebuildFrom))
        changeState(self,rebuildFrom,forceNew=True)
    
    
    
    #>Validate our data ------------------------------------------------------
    d_upStateFunctions = {'form':form,
                          'prerig':prerig,
                          'skeleton':skeleton,
                          'rig':rig,
                          }
    d_downStateFunctions = {'define':formDelete,
                            'form':prerigDelete,
                            'prerig':skeleton_delete,
                            'skeleton':rigDelete,
                            }
    d_deleteStateFunctions = {'form':formDelete,
                              'prerig':prerigDelete,
                              'rig':rigDelete,
                              'skeleton':skeleton_delete,
                              }
    
    stateArgs = BLOCKGEN.validate_stateArg(state)
    _l_moduleStates = [v for v in BLOCKSHARE._l_blockStates]

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
        if _state_target in list(d_upStateFunctions.keys()):
            if not d_upStateFunctions[_state_target](self):return False
            return True
    
    #except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
def get_baseJointOrientation(self):
    return 'zyx'
    
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
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
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
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
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
 
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    
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
            else:
                if mModule.hasAttr('cgmDirection'):
                    ATTR.delete(mModule.mNode,'cgmDirection')
    
            for k,v in list(_nameDict.items()):
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
 
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    
def is_rigged(self):
    try:
        _str_func = 'is_rigged'
        log.debug(cgmGEN.logString_start(_str_func))

        if self.blockType == 'master':
            if self.getMessage('moduleTarget'):
                if self.moduleTarget.getMessage('masterControl'):
                    return True
            return False
        elif self.blockType in ['eyeMain']:
            return self.atBlockModule('is_rig')
        
        return self.moduleTarget.atUtils('is_rigged')

    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)

def checkState(self,asString=True):
    return getState(self,asString,False)

def getState(self, asString = True, fastCheck=True):
    d_stateChecks = {'form':is_form,
                     'prerig':is_prerig,
                     'skeleton':is_skeleton,
                     'rig':is_rigged}
    try:
        _str_func = 'getState'
        log.debug(cgmGEN.logString_start(_str_func))

        
        _l_blockStates = [v for v in BLOCKSHARE._l_blockStates]
        
        def returnRes(arg):
            if asString:
                return self.getEnumValueString('blockState')
            return self.blockState
        
        _str_func = 'getState'
        log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)
        
        if fastCheck:
            try:return returnRes(self.blockState)
            except:pass
            
        _blockModule = self.p_blockModule
        _goodState = False
    
        _state = self.getEnumValueString('blockState')
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
                
            if 'is_{0}'.format(_state) in list(_blockModule.__dict__.keys()):
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
    
    
        if _goodState != self.getEnumValueString('blockState'):
            log.debug("|{0}| >> Passed: {1}. Changing buffer state".format(_str_func,_goodState))                    
            self.blockState = _goodState
            
            
        return returnRes(_goodState)
        if asString:
            return _goodState
        return _l_blockStates.index(_goodState)
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
    
    
#Profile stuff ==============================================================================================  
def datList_validate(self,count = None, datList = 'rollCount',checkAttr = 'numControls',
                     defaultAttr = 'numRoll', default= 3, datType = int, forceEdit=False):
    """
    """
    try:
        _str_func = 'datList_validate | {0}'.format(datList)
        log.debug(cgmGEN.logString_start(_str_func))
        
        #pprint.pprint(locals())
        
        if not self.datList_get(datList) and not forceEdit:
            log.info(cgmGEN.logString_msg(_str_func,"No datList found | tag: {0}".format(datList)))
            _default = self.getMayaAttr(defaultAttr)
            l_subs = [_default for i in range(count)]
            self.datList_connect(datList, l_subs)            
            return  True

        if count is None:
            len_needed = self.getMayaAttr(checkAttr)
        else:len_needed = count
        l_current = self.datList_get(datList)
        len_current = len(l_current)
        
        if defaultAttr is not None:
            _default = self.getMayaAttr(defaultAttr)
            if _default:
                default = _default
        
        if len_current < len_needed or forceEdit:
            log.debug(cgmGEN.logString_sub(_str_func,'Getting via dialog'))
            msg_base = ''
            if len_current < len_needed:
                msg_base= msg_base + "{0} \n datList does not match num needed \n".format(self.p_nameBase)
                
            msg_base = msg_base + "Current: {0} | Needed: {1}".format(len_current,len_needed,self.p_nameShort)
            

            msg_full = msg_base + '\n Default: {0}'.format(default)
            
            msg_full = " {0} \n Please provide correct number in comma separated list".format(msg_full)
            

            _d = {'title':"Validate [{0}]".format(datList),
                  'm':msg_full,
                  'text':','.join(str(v) for v in l_current),
                  'button':['OK','Cancel'], 'defaultButton':'OK', 'messageAlign':'center', 'cancelButton':'Cancel','dismissString':'Cancel','style':'text'}
            
            try:
                #l_profileList = self.p_blockModule.d_block_profiles[self.blockProfile][datList]
                #msg_full = _d['m']
                #msg_full = msg_full + '\n ProfileList: {0}'.format(','.join(l_profileList))
                #_d['m'] = msg_full
                _d['button'] = ['OK','Iter Entry','Iter Default','Cancel']
            except:l_profileList = []            

            result = mc.promptDialog(**_d)
            
            if result == 'OK':
                _v =  mc.promptDialog(query=True, text=True)
                l_new = _v.split(',')
                l_new = [datType(v) for v in l_new]
                len_new = len(l_new)
                if len_new >= len_needed or forceEdit:
                    self.datList_connect(datList,[datType(v) for v in l_new],)
                    log.info(cgmGEN.logString_msg(_str_func,'Setting to: {0}'.format(l_new)))
                    return True
                else:
                    log.warning(cgmGEN.logString_msg(_str_func,l_new))
                    return log.error(cgmGEN.logString_msg(_str_func,
                                                         'Input len: {0} != needed: {1}'.format(len_new,len_needed)))
            elif result == 'Use Profile':
                log.warning(cgmGEN.logString_msg(_str_func,"Using Profile"))
                self.datList_connect(datList,[datType(v) for v in l_profileList],)
                return True
            elif result == 'Iter Entry':
                _v =  mc.promptDialog(query=True, text=True)
                l_new = _v.split(',')
                _value = l_new[0]
                _l = [datType(_value) for i in range(len_needed)]
                log.info(cgmGEN.logString_msg(_str_func,'Setting to: {0}'.format(_l)))            
                self.datList_connect(datList,_l)
                return True
            elif result == 'Iter Default':
                _l = [datType(default) for i in range(len_needed)]
                log.info(cgmGEN.logString_msg(_str_func,'Using default: {1} | Setting to: {0}'.format(_l,default)))
                self.datList_connect(datList,_l)
                
                return True
            else:
                log.warning(msg_base)
                log.warning("Current: {0}".format(l_current))
                
                return log.warning("|{0}| >> cancelled | {1}".format(_str_func, self))
            
        #pprint.pprint(vars())
        return True
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)



def nameList_uiPrompt(self, nameList = 'nameList'):
    """
    """
    try:
        _str_func = 'nameList_uiPrompt'
        log.debug(cgmGEN.logString_start(_str_func))

        if not self.datList_exists(nameList):
            log.info(cgmGEN.logString_msg(_str_func,"No nameList found | tag: {0}".format(nameList)))
            return 
        
        l_current = self.datList_get(nameList)
        len_needed = len(l_current)
        if len_needed == 1:
            try:len_needed = self.numControls
            except:pass
        
        msg_base= "Edit nameList : {0} \n Please provide comma separated list |  Estimate: {1}".format(self.p_nameShort,len_needed)
        

            
        _d = {'title':"Edit nameList",
              'm':msg_base,
              'text':','.join(l_current),
              'button':['OK','Cancel'], 'defaultButton':'OK', 'messageAlign':'center', 'cancelButton':'Cancel','dismissString':'Cancel','style':'text'}
        
        _cgmName = self.getMayaAttr('cgmName')
        try:
            l_profileList = self.p_blockModule.d_block_profiles[self.blockProfile]['nameList']
            msg_full = _d['m']
            msg_full = msg_full + '\n ProfileList: {0}'.format(','.join(l_profileList))
            
            msg_full = msg_full + '\n cgmName: {0}'.format(_cgmName)
            _d['m'] = msg_full
            _d['button'] = ['OK','Use Profile','Iter Entry','Iter cgmName','Cancel']
        except:l_profileList = []            

        result = mc.promptDialog(**_d)
        
        if result == 'OK':
            _v =  mc.promptDialog(query=True, text=True)
            l_new = _v.split(',')
            len_new = len(l_new)
            self.datList_connect('nameList',l_new)
            log.info(cgmGEN.logString_msg(_str_func,'Setting to: {0}'.format(l_new)))
            
            return True
        elif result == 'Use Profile':
            log.warning(cgmGEN.logString_msg(_str_func,"Using Profile"))
            self.datList_connect('nameList',l_profileList)
            return True
        elif result == 'Iter Entry':
            _v =  mc.promptDialog(query=True, text=True)
            l_new = _v.split(',')
            _name = l_new[0]
            _l = ["{0}_{1}".format(_name,i) for i in range(len_needed)]
            self.datList_connect('nameList',_l)
            log.info(cgmGEN.logString_msg(_str_func,'Setting to: {0}'.format(_l)))            
            return
        elif result == 'Iter cgmName':
            _name = _cgmName
            _l = ["{0}_{1}".format(_name,i) for i in range(len_needed)]
            self.datList_connect('nameList',_l)
            log.info(cgmGEN.logString_msg(_str_func,'Setting to: {0}'.format(_l)))            
            return        
        else:
            log.warning(msg_base)
            log.warning("Current: {0}".format(l_current))
            return log.warning("|{0}| >> cancelled | {1}".format(_str_func, self))
        
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)

        
        
def nameList_validate(self,count = None, nameList = 'nameList',checkAttr = 'numControls'):
    """
    """
    try:
        _str_func = 'nameList_validate'
        log.debug(cgmGEN.logString_start(_str_func))
        
        if not self.datList_get(nameList):
            log.info(cgmGEN.logString_msg(_str_func,"No nameList found | tag: {0}".format(nameList)))
            return 

        
        if count is None:
            len_needed = self.getMayaAttr(checkAttr)
        else:len_needed = count
        l_current = self.datList_get(nameList)
        len_current = len(l_current)
        if len_current < len_needed:
            log.debug(cgmGEN.logString_sub(_str_func,'Getting via dialog'))
            msg_base= "{2} \n nameList does not match num controls \n Current: {0} | Needed: {1}".format(len_current,len_needed,self.p_nameShort)
            
            _cgmName = self.getMayaAttr('cgmName')
            msg_full = msg_base + '\n cgmName: {0}'.format(_cgmName)
            
            msg_full = " {0} \n Please provide correct number in comma separated list".format(msg_full)
            

            _d = {'title':"Validate nameList",
                  'm':msg_full,
                  'text':','.join(l_current),
                  'button':['OK','Cancel'], 'defaultButton':'OK', 'messageAlign':'center', 'cancelButton':'Cancel','dismissString':'Cancel','style':'text'}
            
            try:
                l_profileList = self.p_blockModule.d_block_profiles[self.blockProfile]['nameList']
                msg_full = _d['m']
                msg_full = msg_full + '\n ProfileList: {0}'.format(','.join(l_profileList))
                _d['m'] = msg_full
                _d['button'] = ['OK','Use Profile','Iter Entry','Iter cgmName','Cancel']
            except:l_profileList = []            

            result = mc.promptDialog(**_d)
            
            if result == 'OK':
                _v =  mc.promptDialog(query=True, text=True)
                l_new = _v.split(',')
                len_new = len(l_new)
                if len_new >= len_needed:
                    self.datList_connect('nameList',l_new)
                    log.info(cgmGEN.logString_msg(_str_func,'Setting to: {0}'.format(l_new)))
                    return True
                else:
                    log.warning(cgmGEN.logString_msg(_str_func,l_new))
                    return log.error(cgmGEN.logString_msg(_str_func,
                                                         'Input len: {0} != needed: {1}'.format(len_new,len_needed)))
            elif result == 'Use Profile':
                log.warning(cgmGEN.logString_msg(_str_func,"Using Profile"))
                self.datList_connect('nameList',l_profileList)
                return True
            elif result == 'Iter Entry':
                _v =  mc.promptDialog(query=True, text=True)
                l_new = _v.split(',')
                _name = l_new[0]
                
                _l = ["{0}_{1}".format(_name,i) for i in range(len_needed)]
                log.info(cgmGEN.logString_msg(_str_func,'Setting to: {0}'.format(_l)))            
                
                self.datList_connect('nameList',_l)
                return True
            elif result == 'Iter cgmName':
                _name = _cgmName
                _l = ["{0}_{1}".format(_name,i) for i in range(len_needed)]
                self.datList_connect('nameList',_l)
                log.info(cgmGEN.logString_msg(_str_func,'Setting to: {0}'.format(_l)))            
                return True
            else:
                log.warning(msg_base)
                log.warning("Current: {0}".format(l_current))
                
                return log.warning("|{0}| >> cancelled | {1}".format(_str_func, self))
            
        #pprint.pprint(vars())
        return True
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)


def nameList_resetToProfile(self,arg = None):
    try:
        _str_func = 'nameList_resetToProfile'
        log.debug(cgmGEN.logString_start(_str_func))
        


        if arg is None:
            arg = self.getMayaAttr('blockProfile')
        log.debug("|{0}| >>  arg: {1}".format(_str_func,arg))
        
        mBlockModule = self.p_blockModule
        log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
        #reload(mBlockModule)
        l_nameList_current = self.datList_get('nameList')
        log.debug("|{0}| >>  current: {1}".format(_str_func,l_nameList_current))
        l_nameList = []
        try:
            l_nameList =  mBlockModule.d_block_profiles[arg]['nameList']
            log.debug("|{0}| >>  Found on profile: {1}".format(_str_func,l_nameList))
        except Exception as err:
            try:
                l_nameList =  mBlockModule.d_defaultSettings['nameList']
                log.debug("|{0}| >>  Found on module: {1}".format(_str_func,l_nameList))
            except Exception as err:
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
                return log.error("|{0}| >>  nameLists don't match and higher than form state. Please go to form state before resetting".format(_str_func,self.p_nameShort))
            else:
                self.datList_connect('nameList', l_nameList, mode='string')
        log.debug("|{0}| >>  New: {1}".format(_str_func,self.datList_get('nameList')))
        return l_nameList
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)


def blockProfile_getOptions(self):
    try:
        _str_func = 'blockProfile_getOptions'
        log.debug(cgmGEN.logString_start(_str_func))

        mBlockModule = self.p_blockModule
        log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
        #reload(mBlockModule)
        
        try:return list(mBlockModule.d_block_profiles.keys())
        except Exception as err:
            return log.error("|{0}| >>  Failed to query. | {1}".format(_str_func,err))
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def blockProfile_getAttrs(self,arg):
    _str_func = 'blockProfile_getOptions'
    log.debug(cgmGEN.logString_start(_str_func))
    _short = self.mNode

    mBlockModule = self.p_blockModule
    log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
    #reload(mBlockModule)
    
    try:_d = mBlockModule.d_block_profiles[arg]
    except Exception as err:
        return log.warning("|{0}| >>  Failed to query profile: {1} | {2} | {3}".format(_str_func,err, _short, Exception))
    
    return _d
        
def blockProfile_load(self, arg):
    _str_func = 'blockProfile_load'
    log.debug(cgmGEN.logString_start(_str_func))

    _short = self.mNode
    
    mBlockModule = self.p_blockModule
    log.debug("|{0}| >>  BlockModule: {1} | profile: {2}".format(_str_func,mBlockModule,arg))
    try:_d = mBlockModule.d_block_profiles[arg]
    except Exception as err:
        return log.warning("|{0}| >>  Failed to query profile: {1} | {2} | {3}".format(_str_func,err, _short, Exception))
    
    #if not _d.get('blockProfile'):
    #    _d['blockProfile'] = arg
    
    #cgmGEN.func_snapShot(vars())
    log.debug("|{0}| >>  {1}...".format(_str_func,arg))
    _l_badAttrs = ['side']
    for a,v in list(_d.items()):
        try:
            if a in _l_badAttrs:
                print(('!'*100))
                print((cgmGEN.logString_msg(_str_func, 'REMOVE {0} from {1} | {2}'.format(a,arg,mBlockModule.__name__))))
                print(('!'*100))                
                continue
            log.debug("|{0}| attr >> '{1}' | v: {2}".format(_str_func,a,v)) 
            _done = False
            _typeDat = type(v)
            _datList = False
            if a.endswith('DatList'):
                log.info("|{0}| datList attr | {1}".format(_str_func,a))
                a = a.replace('DatList','')
                _datList  = True
                
            if issubclass(_typeDat,list) or _datList:
                log.debug("|{0}| datList...".format(_str_func))
                if a == 'loftList':
                    ATTR.datList_connect(_short, a, v, 
                                         mode='enum',enum= BLOCKSHARE._d_attrsTo_make['loftShape'])
                else:
                    mc.select(cl=True)
                    if VALID.stringArg(v[0]):
                        ATTR.datList_connect(_short, a, v, mode='string')
                    else:
                        ATTR.datList_connect(_short, a, v, mode='int')
                        
                _done = True
                #else:
                    #log.debug("|{0}| Missing datList >> '{1}' | v: {2}.".format(_str_func,a,v))
            if issubclass(_typeDat,dict):
                log.debug("|{0}| dict...".format(_str_func))                                     
                #self.__dict__['a'] = v
                setattr(self,a,v)
                _done = True
            if not _done:
                ATTR.set(_short,a,v)
            log.info("|{0}| >>  {1} | {2}".format(_str_func,a,v))                
            
        except Exception as err:
            log.error("|{0}| Set attr Failure >> '{1}' | value: {2} | err: {3}".format(_str_func,a,v,err)) 
    
    self.doStore('blockProfile',arg)
    log.debug("|{0}| >>  Block: {1} | {2}".format(_str_func,_short,arg))


def buildProfile_load(self, arg):
    _str_func = 'buildProfile_load'
    log.debug(cgmGEN.logString_start(_str_func))

    _short = self.mNode
    mBlockModule = self.p_blockModule
    log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
    #reload(mBlockModule)
    
    _d = copy.copy(BLOCKSHARE.d_build_profiles.get(arg,{}))
    #pprint.pprint(BLOCKSHARE.d_build_profiles)
    _d_block = {}
    try:_d_block = mBlockModule.d_build_profiles[arg]
    except Exception as err:
        return log.error("|{0}| >>  Failed to query. | {1} | {2}".format(_str_func,err, Exception))
    
    _d_block = _d_block.get('shared',{}) or _d_block.get('default',{})
    
    #cgmGEN.func_snapShot(vars())
    
    if _d_block:
        pprint.pprint(_d_block)
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
    _state = self.getEnumValueString('blockState')
    if _state not in ['define','form','prerig']:
        log.error(cgmGEN._str_subLine)
        return log.error("|{0}| >>  [FAILED] Block: {1} | profile: {2} | Can't load in state: {3}".format(_str_func,_short,arg,_state))
    
    log.debug("|{0}| >>  Loading: {1}...".format(_str_func,arg))
    for a,v in list(_d.items()):
        try:
            log.info("|{0}| attr >> '{1}' | v: {2}".format(_str_func,a,v)) 
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
                        
        except Exception as err:
            log.error("|{0}| Set attr Failure >> '{1}' | value: {2} | err: {3}".format(_str_func,a,v,err)) 
    
    self.doStore('buildProfile',arg)
    log.debug("|{0}| >>  [LOADED] Block: {1} | profile: {2}".format(_str_func,_short,arg))

def blockProfile_get(self, bySection = False, skipSections = ['advanced','data','wiring','vis','proxySurface'],
                     attrMask = ['baseSizeX','baseSizeY','baseSizeZ','blockProfile','meshBuild','offsetMode','proxyShape','jointRadius','buildProfile',
                                 'root_dynParentMode','root_dynParentScaleMode']):
    _str_func = 'buildProfile_get'
    log.debug(cgmGEN.logString_start(_str_func))

    _short = self.mNode
    mBlockModule = self.p_blockModule
    log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
    #reload(mBlockModule)
    

    _res = {}

    for section,l in list(uiQuery_getStateAttrDict(self,unknown=False).items()):
        if section in skipSections:
            continue
        if bySection:
            _res[section] = {}
        for a in l:
            if a in attrMask:
                continue
            if bySection:
                _d = _res[section]
            else:
                _d = _res
                
            _type = ATTR.get_type(_short,a)
            if _type == 'enum':
                _d[str(a)] = str(ATTR.get_enumValueString(_short,a))
            else:
                _d[str(a)] =ATTR.get(_short,a)
                
    pprint.pprint(_res)
    return
    log.debug("|{0}| >>  Loading: {1}...".format(_str_func,arg))
    for a,v in list(_d.items()):
        try:
            log.info("|{0}| attr >> '{1}' | v: {2}".format(_str_func,a,v)) 
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
                        
        except Exception as err:
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
    if _str_state not in ['define','form']:
        raise ValueError("|{0}| >>  [{1}] is not in define state. state: {2}".format(_str_func,self.mNode, _str_state))
    
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

    
    ml_formHandles = self.msgList_get('formHandles')
    ml_loftCurves = []
    for mHandle in ml_formHandles:
        if mHandle.getMessage('loftCurve'):
            ml_loftCurves.append(mHandle.getMessage('loftCurve',asMeta=1)[0])
        ml_subShapers = mHandle.msgList_get('subShapers')
        if ml_subShapers:
            for mSub in ml_subShapers:
                if mSub.getMessage('loftCurve'):
                    ml_loftCurves.append(mSub.getMessage('loftCurve',asMeta=1)[0])
        
    if ml_formHandles[-1].getMessage('pivotHelper'):
        mPivotHelper = ml_formHandles[-1].pivotHelper
        log.debug("|{0}| >> pivot helper found ".format(_str_func))
    
        #make the foot geo....    
        mBaseCrv = mPivotHelper.doDuplicate(po=False)
        mBaseCrv.parent = False
        mShape2 = False
        
        mTopLoft = mPivotHelper.getMessageAsMeta('topLoft')
        if mTopLoft:
            mShape2 = mTopLoft.doDuplicate(po=False)
            mShape2.parent = False
            ml_loftCurves.append(mShape2)
        """
        for mChild in mBaseCrv.getChildren(asMeta=True):
            if mChild.cgmName == 'topLoft':
                mShape2 = mChild.doDuplicate(po=False)
                mShape2.parent = False
                ml_loftCurves.append(mShape2)
            mChild.delete()"""
            
        ml_loftCurves.append(mBaseCrv)
    """
    ml_newLoft = []
    for mCrv in ml_loftCurves:
        mCrv.doDuplicate(po=True)
        mCrv.p_parent = False
        ml_newLoft.append(mCrv)"""
    #reload(BUILDUTILS)
    _mesh = BUILDUTILS.create_loftMesh([mCrv.mNode for mCrv in ml_loftCurves],
                                       name= 'test',
                                       divisions=1,
                                       form=2,
                                       degree=1)




    return ml_loftCurves

def get_baseNameDict(self):
    return self.getNameDict(ignore=['cgmType','cgmIterator'])

def get_partName(self):
    _str_func = ' get_partName'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    
    #try:#Quick select sets ================================================================
    _d = NAMETOOLS.get_objNameDict(self.mNode,['cgmType'])
    if not _d.get('cgmName'):
        _d['cgmName'] = self.getMayaAttr('blockType')
    else:
        _d['cgmType'] = self.blockType
    log.debug("|{0}| >>  d: {1}".format(_str_func,_d))
    
    _str= NAMETOOLS.returnCombinedNameFromDict(_d)
    log.debug("|{0}| >>  str: {1}".format(_str_func,_str))
    return STRINGS.stripInvalidChars(_str)



def get_module(self):
    _str_func = 'get_module'
    log.debug("|{0}| >>... ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mModuleTarget = self.getMessage('moduleTarget',asMeta=True)
    if not mModuleTarget:
        return log.error("|{0}| >> Must have moduleTarget for skining mode".format(_str_func))
    log.debug("|{0}| >> mModuleTarget: {1}".format(_str_func,mModuleTarget[0]))
    return mModuleTarget[0]


@cgmGEN.Timer
def skeleton_getReport(self):
    """
    Verify the mirror setup of the puppet modules
    """
    _str_func = ' skeleton_getReport'.format(self)
    log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
    
    #ml_modules = modules_getHeirarchal(self,False)
    ml_blocks = BLOCKGEN.get_rigBlock_heirarchy_context(self,asList=True)
    ml_processed = []
    
    _cnt =0
    _len = 0
    _modules = 0
    #>> Process ======================================================================================
    for i,mBlock in enumerate(ml_blocks):
        if mBlock in ml_processed:
            log.debug("|{0}| >> Already processed: {1}".format(_str_func,mBlock))
            continue
        
        
        log.debug("|{0}| >> Processing: {1}".format(_str_func,mBlock))
        
        
        ml = mBlock.moduleTarget.atUtils('rig_getSkinJoints',asMeta=True)

        mMirror = mBlock.blockMirror
        
        if mMirror:
            _modules+=2
            log.debug("|{0}| >> Block has mirror: {1} | {2}".format(_str_func,mBlock.mNode, mMirror.mNode))
            ml_mirror = mMirror.moduleTarget.atUtils('rig_getSkinJoints',asMeta=True)
            for i,j in enumerate(ml):
                try:
                    print(("{} | {} >><<>> {}".format(_cnt, j.p_nameBase, ml_mirror[i].p_nameBase)))
                    _cnt +=1
                    _len+=2
                except Exception as err:
                    log.error(err)

        else:
            _modules+=1            
            for mObj in ml:
                print(("{} | {}".format(_cnt, mObj.p_nameBase)))
                _cnt +=1
                _len+=1
                
            
        ml_processed.append(mBlock)
        if mMirror:ml_processed.append(mMirror)

    
    print(("[{}] Joints in [{}] modules.".format(_len, _modules)))
    return
    log.info(cgmGEN.logString_sub(_str_func,'Centre'))
    for k,v in list(md_list['Centre'].items()):
        print(("{0} | {1} ".format(k,v.p_nameShort)))
        
    log.info(cgmGEN.logString_sub(_str_func,'Left/Right'))
    for k,v in list(md_list['Left'].items()):
        try:print(("{0} | {1} >><< {2}".format(k,v.p_nameShort,md_list['Right'][k].p_nameShort)))
        except:
            pass



        
    return



    
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

@cgmGEN.Timer
def puppetMesh_create(self,unified=True,skin=False, proxy = False, forceNew=True):
    #try:
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
        

        if mBlock.getMayaAttr('meshBuild') in [False,0]:
            log.error("|{0}| >> meshBuild off: {1}".format(_str_func,mBlock))
            continue
        
        if proxy:
            _res = mBlock.verify_proxyMesh(puppetMeshMode=True)
            if _res:ml_mesh.extend(_res)
            
        else:
            if mBlock.blockType not in ['brow','muzzle','eyeMain']:
                
                _res = create_simpleMesh(mBlock,skin=subSkin,forceNew=subSkin,deleteHistory=True,)
                if _res:ml_mesh.extend(_res)
                
                _side = get_side(mBlock)
                
                for mObj in _res:
                    CORERIG.colorControl(mObj.mNode,_side,'main',transparent=False,proxy=True)
        
        
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
            mMesh = False
            for mObj in ml_mesh:
                TRANS.pivots_zeroTransform(mObj)
                mObj.dagLock(False)
                mObj.p_parent = False
            #Have to dup and copy weights because the geo group isn't always world center
            if len(ml_mesh)>1:
                mMesh = cgmMeta.validateObjListArg(mc.polyUniteSkinned([mObj.mNode for mObj in ml_mesh],ch=0))
                mMesh = mMesh[0]
            elif ml_mesh:
                mMesh = ml_mesh[0]
            if mMesh:
                
                mMesh.dagLock(False)
                
                #mMeshBase = mMeshBase[0]
                #mMesh = mMeshBase.doDuplicate(po=False,ic=False)
                mMesh.rename('{0}_unified_geo'.format(mPuppet.p_nameBase))
                mMesh.p_parent = mParent
                #cgmGEN.func_snapShot(vars())
                
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
        if ml_mesh:
            ml_mesh[0].rename('{0}_unified_geo'.format(mRoot.p_nameBase))
        
    if skin or proxy and ml_mesh:
        mPuppet.msgList_connect('puppetMesh',ml_mesh)
        
    #for mGeo in ml_mesh:
    #    CORERIG.color_mesh(mGeo.mNode,'puppetmesh')
        
    return ml_mesh
    #except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
            
    

def create_simpleMesh(self, forceNew = True, skin = False,connect=True,reverseNormal = None,
                      deleteHistory=False,loftMode = None ):#'evenCubic'
    """
    Main call for creating a skinned or single mesh from a rigBlock
    """
    _str_func = 'create_simpleMesh'
    log.debug("|{0}| >>  forceNew: {1} | skin: {2} ".format(_str_func,forceNew,skin)+ '-'*80)
    log.debug("{0}".format(self))
    
    if self.getMayaAttr('isBlockFrame'):
        log.debug(cgmGEN.logString_sub(_str_func,'blockFrame bypass'))
        return                
    
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
    if 'create_simpleMesh' in mBlockModule.__dict__:
        log.debug("|{0}| >> BlockModule 'create_simpleMesh' call found...".format(_str_func))            
        ml_mesh = mBlockModule.create_simpleMesh(self,skin=skin,parent=mParent,deleteHistory=deleteHistory)
    
    else:#Create ======================================================================================
        if not loftMode:
            if self.getEnumValueString('loftDegree') == 'cubic':
                loftMode = 'evenCubic'
            else:
                loftMode = 'evenLinear'
            
            
        kws = {}
        if self.blockType in ['limb']:
            if self.addLeverBase and self.getEnumValueString('addLeverBase') != 'joint' and skin:
                kws['skip'] = [0]
            
        ml_mesh = create_simpleLoftMesh(self,form=2,degree=None,divisions=2,deleteHistory=deleteHistory,loftMode=loftMode,**kws)
    
        
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
            #l_joints= [mJnt.mNode for mJnt in ml_moduleJoints]
            for mMesh in ml_mesh:
                log.debug("|{0}| >> skinning {1}".format(_str_func,mMesh))
                mMesh.p_parent = mParent
                
                MRSPOST.skin_mesh(mMesh,ml_moduleJoints)
                
                """
                #mMesh.doCopyPivot(mGeoGroup.mNode)
                try:
                    skin = mc.skinCluster (l_joints,
                                           mMesh.mNode,
                                           tsb=True,
                                           bm=2,
                                           wd=0,
                                           heatmapFalloff = 1,
                                           maximumInfluences = 2,
                                           normalizeWeights = 1, dropoffRate=5)
                except Exception,err:
                    log.warning("|{0}| >> heat map fail: {1}.. | {2}".format(_str_func,format(self.mNode),err))
                    skin = mc.skinCluster (l_joints,
                                           mMesh.mNode,
                                           tsb=True,
                                           bm=0,
                                           maximumInfluences = 2,
                                           wd=0,
                                           normalizeWeights = 1,dropoffRate=10)
                skin = mc.rename(skin,'{0}_skinCluster'.format(mMesh.p_nameBase))"""
            
            #Reparent
            for i,mJnt in enumerate(ml_moduleJoints):
                mJnt.p_parent = md_parents[mJnt]
            #pprint.pprint(md_parents)
    if connect and ml_mesh:
        self.msgList_connect('simpleMesh',ml_mesh)        
    return ml_mesh
            

def create_simpleLoftMesh(self, form = 2, degree=None, uSplit = None,vSplit=None,cap=True,uniform = False,skip=[],
                          reverseNormal = None,deleteHistory = True,divisions=None, loftMode = None,flipUV = False):
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
    
    if self.getMayaAttr('isBlockFrame'):
        log.debug(cgmGEN.logString_sub(_str_func,'blockFrame bypass'))
        return            

    mBlockModule = self.p_blockModule

    ml_delete = []
    ml_formHandles = self.msgList_get('formHandles')
    ml_loftCurves = []
    
    if degree == None:
        degree = 1 + self.loftDegree
        if degree ==1:
            form = 3
    if vSplit == None:
        vSplit = self.loftSplit#-1
    if uSplit == None:
        uSplit = self.loftSides
        
        
    log.debug(cgmGEN.logString_sub(_str_func,"Gather loft curves"))
    for i,mHandle in enumerate(ml_formHandles):
        if skip and i in skip:
            continue
        if mHandle.getMessage('loftCurve'):
            ml_loftCurves.append(mHandle.getMessage('loftCurve',asMeta=1)[0])
        ml_subShapers = mHandle.msgList_get('subShapers')
        if ml_subShapers:
            for mSub in ml_subShapers:
                if mSub.getMessage('loftCurve'):
                    ml_loftCurves.append(mSub.getMessage('loftCurve',asMeta=1)[0])
        
    if ml_formHandles[-1].getMessage('pivotHelper') and self.blockProfile not in ['arm']:
        mPivotHelper = ml_formHandles[-1].pivotHelper
        log.debug("|{0}| >> pivot helper found ".format(_str_func))
    
        #make the foot geo....    
        mBaseCrv = mPivotHelper.doDuplicate(po=False)
        mBaseCrv.parent = False
        mShape2 = False
        ml_delete.append(mBaseCrv)
        
        mTopLoft = mPivotHelper.getMessageAsMeta('topLoft')
        if mTopLoft:
            mShape2 = mTopLoft.doDuplicate(po=False)        
            ml_loftCurves.append(mShape2)
            ml_delete.append(mShape2)
        """
        for mChild in mBaseCrv.getChildren(asMeta=True):
            if mChild.cgmName == 'topLoft':
                mShape2 = mChild.doDuplicate(po=False)
                mShape2.parent = False
                ml_loftCurves.append(mShape2)
                ml_delete.append(mShape2)                
            mChild.delete()"""
        ml_loftCurves.append(mBaseCrv)
        
    """
    if cap:
        log.debug(cgmGEN.logString_sub(_str_func,"cap"))        
        ml_use = copy.copy(ml_loftCurves)
        for i,mLoft in enumerate([ml_loftCurves[0],ml_loftCurves[-1]]):
            log.debug(cgmGEN.logString_msg(_str_func,"duping: {0}".format(mLoft.mNode)))
            
            mStartCollapse = mLoft.doDuplicate(po=False)
            mStartCollapse.p_parent = False
            mStartCollapse.scale = [.0001 for i in range(3)]
            if mLoft == ml_loftCurves[0]:
                ml_use.insert(0,mStartCollapse)
            else:
                ml_use.append(mStartCollapse)
            ml_delete.append(mStartCollapse)
        ml_loftCurves = ml_use"""
        
    log.debug(cgmGEN.logString_sub(_str_func,"Build"))
    #pprint.pprint(vars())
    
    _d = {'uSplit':uSplit,
          'vSplit':vSplit,
          'cap' : cap,
          'form':form,
          'uniform':uniform,
          'deleteHistory':deleteHistory,
          'merge':deleteHistory,
          'reverseNormal':reverseNormal,
          'degree':degree}
    
    if loftMode:
        if loftMode in ['evenCubic','evenLinear']:
            d_tess = {'format':2,#General
                      'polygonType':1,#'quads',
                      'vType':3,
                      'uType':1,
                      'vNumber':1}
            _d['d_tess'] = d_tess
            if loftMode == 'evenCubic':
                _d['degree'] = 3
                _d['uniform'] = True
                d_tess['uNumber'] = (4 + vSplit + (len(ml_loftCurves)) * vSplit)*2
                #..attempting to fix inconsistency in which is u and which is v
                #d_tess['vNumber'] = d_tess['uNumber']
                #d_tess['vType'] = 1
            else:
                _d['degree'] = 1
                d_tess['uNumber'] = (vSplit + (len(ml_loftCurves)) * vSplit)
                
            if flipUV:
                log.warning(cgmGEN.logString_msg(_str_func,"FLIPPING UV"))
                """
                dTmp = {}
                for i,k in enumerate(['u','v']):
                    for k2 in 'Type','Number':
                        if i:
                            dTmp['u'+k2] = d_tess['v'+k2]
                        else:
                            dTmp['v'+k2] = d_tess['u'+k2]
                d_tess.update(dTmp)"""
                            
                
        elif loftMode == 'default':
            pass
                

    #pprint.pprint(vars())
    
    _mesh = BUILDUTILS.create_loftMesh([mCrv.mNode for mCrv in ml_loftCurves],
                                      **_d)
    
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
    for a,v in list(_d.items()):
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
            for a,v in list(_d.items()):
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
        
def create_defineCurve(self,d_definitions,md_handles, mParentNull = None,crvType='defineCurve'):
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
        for k in list(d_definitions.keys()):
            log.debug("|{0}| >>  curve: {1}...".format(_str_func,k))            
            _dtmp = d_definitions[k]
            
            str_name = _dtmp.get('name') or "{0}_{1}".format(self.blockProfile,k)
            _tagOnly = _dtmp.get('tagOnly',False)
            _handleKeys = _dtmp.get('keys')
            if _handleKeys:
                _handleKeys = LISTS.get_noDuplicates(_handleKeys)
            
            ml_handles = _dtmp.get('ml_handles') or [md_handles[k2] for k2 in _handleKeys]
        
            #l_pos = []
            #for mHandle in ml_handles:
            #    l_pos.append(mHandle.p_position)
        
            #_crv = mc.curve(d=1,p=l_pos)
            _tmpRes = CORERIG.create_at([mHandle.mNode for mHandle in ml_handles],
                                        create='linearTrack')
            _crv = _tmpRes[0]
            
            #CORERIG.create_at(create='curve',l_pos = l_pos)
            mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
            mCrv.p_parent = mParentNull
            
            _color = _dtmp.get('color')
            if _color:
                CORERIG.override_color(mCrv.mNode, _color)
            else:
                mHandleFactory.color(mCrv.mNode)
                
            mCrv.rename('{0}_{1}'.format(k,crvType))
            mCrv.doStore('handleTag',k,attrType='string')
            #mCrv.v=False
            #md_loftCurves[tag] = mCrv
        
            self.connectChildNode(mCrv, k+STR.capFirst(crvType),'block')
            ml_defineCurves.append(mCrv)
            md_defineCurves[k] = mCrv
            
            mCrv.msgList_connect('handles',ml_handles)
            
            """
            l_clusters = []
            for i,cv in enumerate(mCrv.getComponents('cv')):
                _res = mc.cluster(cv, n = 'test_{0}_{1}_pre_cluster'.format(ml_handles[i].p_nameBase,i))
                mCluster = cgmMeta.asMeta(_res[1])
                mCluster.p_parent = ml_handles[i].mNode
                mCluster.v = 0
                l_clusters.append(_res)"""
                
            if _dtmp.get('rebuild'):
                _node = mc.rebuildCurve(mCrv.mNode, d=3, keepControlPoints=False,
                                        ch=1,s=len(ml_handles),
                                        n="{0}_reparamRebuild".format(mCrv.p_nameBase))
                mc.rename(_node[1],"{0}_reparamRebuild".format(mCrv.p_nameBase))
                
            mCrv.dagLock()
        return {'md_curves':md_defineCurves,
                'ml_curves':ml_defineCurves}
    except Exception as err:
        cgmGEN.func_snapShot(vars())
        raise

@cgmGEN.Timer
def create_define_rotatePlane(self, md_handles,md_vector,mStartParent=None):
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
          
    for a,v in list(_d.items()):
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

def create_defineHandles(self,l_order,d_definitions,baseSize,mParentNull = None, mScaleSpace = None, rotVecControl = False,blockUpVector = [0,1,0], vecControlLiveScale = False, statePlug ='define',vectorScaleAttr = 'baseSize',startScale=False, forceSize = False):
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
        mParentNull = self.atUtils('stateNull_verify',statePlug)
    mHandleFactory = self.asHandleFactory()
    
    for k in l_order:
        
        _dtmp = d_definitions.get(k,False)
        if not _dtmp:
            log.error("|{0}| >> handle: {1} has no dict. Bailing".format(_str_func,k))
            continue
        
        log.debug("|{0}| >> handle: {1} ...".format(_str_func,k))
        if k in ['end','start','lever'] or forceSize:
            _useSize = 1.0
        else:
            _useSize = _sizeSub
            
        str_name = _dtmp.get('name') or "{0}_{1}".format(self.cgmName,k)
        _tagOnly = _dtmp.get('tagOnly',False)
        _pos = _dtmp.get('pos',False)
        mEnd = md_handles.get(_dtmp.get('endTag')) or md_handles.get('end')
        
        #sphere
        if k in ['up','rp'] or _dtmp.get('handleType') == 'vector':# and rotVecControl:
            #if not vecControlLiveScale:
            #    _rotSize = [.25,.25,2.0]
            #    if k == 'rp':_rotSize = [.5,.5,1.25]
            #else:
            _rotSize = [.05,.8,.05]
            if k == 'rp':_rotSize = [.105,.6,.105]                    
                
            _crv = CURVES.create_fromName(name='cylinder',#'arrowsAxis', 
                                          bakeScale = True,
                                          direction = 'y+',
                                          size = _rotSize,
                                          baseSize=1)                
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
                mHandle.doStore('cgmTypeModifier',k)
                
                #mHandle.doStore('cgmTypeModifier',str_name)
                #mHandle.doStore('cgmName',str_name)
                
            mHandle.doStore('cgmType','defineHandle')
            mHandle.doName()
            mHandle.doStore('handleTag',k,attrType='string')
            mHandle.doStore('handleType','vector')            
            
            SNAP.aim_atPoint(mHandle.mNode,mEnd.p_position, 'z+')
        
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
            _shape = _dtmp.get('shape')
            _useSize = _dtmp.get('size',_useSize)
            if not _shape:
                if k == 'aim':
                    _shape = 'eye'
                else:
                    _shape = 'sphere'
                    if _dtmp.get('jointScale') != True:#We want spherical face shapes
                        _useSize = [_useSize,_useSize,_useSize*.5]
                
            _crv = CURVES.create_fromName(name=_shape,#'arrowsAxis', 
                                          bakeScale = 0,                                              
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
                mHandle.doStore('cgmTypeModifier',k)
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
                
            for a,v in list(_dtmp.get('defaults',{}).items()):
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
                                            bakeScale = 0,                                                
                                            direction = 'y+', size = _size)
            CORERIG.override_color(_arrow, _dtmp['color'])
        
            mArrow = cgmMeta.cgmObject(_arrow)
            mArrow.p_parent = mHandle
            mArrow.resetAttrs()
            mArrow.ty = _size * 3
            
            CORERIG.shapeParent_in_place(mHandle.mNode,mArrow.mNode,False)

        #Helper --------------------------------------------------------------------------------
        if _dtmp.get('vectorLine'):
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
    
            
        if _dtmp.get('arrow'):#Arrow ---------------------------------------------
            if rotVecControl and k in ['up','rp']:pass
            elif k in ['start']:pass                
            else:                
                _arrow = CURVES.create_fromName(name='arrowForm',#'arrowsAxis', 
                                                bakeScale = 1,
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
            
            
                md_vector[k] = mArrow
                self.connectChildNode(mArrow.mNode,'vector{0}Helper'.format(STR.capFirst(k)),'block')
                
                for mShape in mArrow.getShapes(True):
                    mShape.overrideEnabled = 1
                    mShape.overrideDisplayType = 2
                    
                _arrowFollow = _dtmp.get('arrowFollow',False)
                if _arrowFollow:
                    mc.pointConstraint(md_handles[_arrowFollow].mNode, mArrow.mNode, maintainOffset = False)
                    
                mArrow.dagLock()
                

            
        if _dtmp.get('jointLabel') !=False:#Joint Label-----------------------------------------------------------------
            if _tagOnly:
                labelName = k
            else:
                labelName = str_name
                
            mJointLabel = mHandleFactory.addJointLabel(mHandle,labelName)
            md_jointLabels[k] = mJointLabel
            
            #if self.hasAttr('jointRadius'):
            #    self.doConnectOut('jointRadius',"{0}.radius".format(mJointLabel.mNode))
            
    
    
        self.connectChildNode(mHandle.mNode,'{0}{1}Helper'.format(statePlug,STR.capFirst(k)),'block')
    
    self.msgList_connect('{0}Handles'.format(statePlug), ml_handles)
    
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
        mEndAimLoc.p_parent =  md_handles.get('end')#md_vector['end']
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
                         aimVector = [0,0,1], upVector = [0,1,0], 
                         worldUpObject = md_vector.get('up').mNode,
                         worldUpType = 'objectRotation', 
                         worldUpVector = [0,1,0])            

    for k,dTmp in list(d_definitions.items()):
        if dTmp.get('handleType') == 'vector':
            if md_handles.get(k):
                ATTR.set_standardFlags(md_handles[k].mNode,['tx','ty','tz'])
                

    if rotVecControl:
        for k in 'rp','up':
            if md_handles.get(k):
                ATTR.set_standardFlags(md_handles[k].mNode,['tx','ty','tz'])
                
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
        
        if startScale and md_handles.get('start'):
            mBaseSizeHandle.p_parent = md_handles['start']
            mBaseSizeHandle.resetAttrs()
            
        else:
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
        mBaseSizeHandle.v = False
        
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
        measureTag = 'end'
        if startScale:measureTag = 'start'
        for k,d in list(d_measure.items()):
            md_measure[k] = {}
            if k == 'length':
                mPos =mEndSizeHandle.doLoc()
                mNeg = mBaseSizeHandle.doLoc()
                
                mPos.p_parent = mEndSizeHandle
                mNeg.p_parent = mBaseSizeHandle
                
            else:
                mPos = mBaseSizeHandle.doLoc()
                mNeg = mBaseSizeHandle.doLoc()
        
                for mObj in mPos,mNeg:
                    mObj.p_parent = mBaseSizeHandle
        
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
    
        

        for tag,mHandle in list(md_handles.items()):
            _dtmp = d_definitions.get(tag,False)
            _noLock = _dtmp.get('noLock',[])
            if tag in ['lever']:
                continue
            if tag in ['up','rp'] and rotVecControl:
                continue
            if tag in ['start']:
                if startScale:
                    if 'translate' not in _noLock:
                        ATTR.set_standardFlags(mHandle.mNode,attrs = ['tx','ty','tz'])
                else:
                    ATTR.set_standardFlags(mHandle.mNode,attrs = ['sx','sy','sz'])
                
                
            ATTR.set_standardFlags(mHandle.mNode,attrs = ['rx','ry','rz'])
            
        #Scaling our up vector =============================================================
        if rotVecControl and md_handles.get('up'):
            
            if not vecControlLiveScale:
                if startScale and md_handles.get('start'):
                    for tag in ['rp','up']:
                        if md_handles.get(tag):
                            ATTR.set_lock(md_handles[tag].mNode,'scale',False)
                            ptag = d_definitions.get(tag,{}).get('parentTag','start')
                            mc.scaleConstraint(md_handles[ptag].mNode, md_handles[tag].mNode )
                            ATTR.set_lock(md_handles[tag].mNode,'scale',True)
                else:
                    for tag in ['rp','up']:
                        if md_handles.get(tag):
                            ATTR.set_lock(md_handles[tag].mNode,'scale',False)
                            mc.scaleConstraint(md_handles['end'].mNode,
                                               md_handles[tag].mNode,
                                               maintainOffset=True)
                            ATTR.set_lock(md_handles[tag].mNode,'scale',True)
                            
                    #        pass
                    """
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
                            mPlug.doConnectOut("{0}.scaleZ".format(md_handles[tag].mNode))"""                        

            
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
            if  md_handles.get('end') and not startScale:
                md_handles['end'].doConnectOut('scaleX',"{0}.scaleX".format(md_handles['start'].mNode))
                md_handles['end'].doConnectOut('scaleY',"{0}.scaleY".format(md_handles['start'].mNode))
                #mPlug.doConnectOut("{0}.scaleZ".format(md_handles['start'].mNode))
            
        if md_handles.get('end'):
            pos = md_handles['end'].p_position
            md_handles['end'].p_position = 1,2,3
            md_handles['end'].p_position = pos
            

        mel.eval('EnableAll;doEnableNodeItems true all;')
        
    for mHandle in ml_handles:
        d = d_definitions[mHandle.handleTag]
        if d.get('jointScale'):
            if not ATTR.is_connected('{0}.scale'.format(mHandle.mNode)):
                if self.hasAttr('jointRadius'):
                    mHandle.doConnectIn('scale', "{0}.jointRadius".format(self.mNode),pushToChildren=True)                
                    ATTR.set_standardFlags(mHandle.mNode, ['sx','sy','sz'])

    return {'md_handles':md_handles,
            'ml_handles':ml_handles,
            'md_vector':md_vector,
            'md_jointLabels':md_jointLabels}

    
    
def define_set_baseSize(self,baseSize = None, baseAim = None, baseAimDefault = [0,0,1]):
    _str_func = 'define_set_baseSize'
    log.debug(cgmGEN.logString_start(_str_func))
    
    d_baseDat = {}
    
    if self.hasAttr('baseDat'):
        d_baseDat = self.baseDat
        log.debug("|{0}| >>  Base dat found | {1}".format(_str_func,d_baseDat))        
        if baseSize is None:
            baseSize = d_baseDat.get('baseSize')
            log.debug("|{0}| >>  baseSize found in d_baseDat: {1}".format(_str_func,baseSize))
    
    if baseSize is None:
        baseSize = self.baseSize
        log.debug("|{0}| >>  baseSize found in on asset: {1}".format(_str_func,baseSize))



    if not baseSize:
        return log.error("|{0}| >>  No baseSize value. Returning.".format(_str_func))
    
    if self.hasAttr('baseDat') and baseSize:
        self.baseSize = baseSize
    log.debug("|{0}| >>  baseSize: {1}".format(_str_func,baseSize))
    
    if self.blockType in ['eye']:
        log.info("|{0}| >>  baseSize only type.".format(_str_func))
        self.baseSize = d_baseDat.get('baseSize') or baseSize
        return True
    
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
    
    mDefineStartObj = self.getMessageAsMeta('defineStartHelper')
    log.debug("|{0}| >>  mDefineStartObj: {1}".format(_str_func,mDefineStartObj))
    
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
    
    if mDefineStartObj:
        mDefineStartObj.sx = _width
        mDefineStartObj.sy = _height
        mDefineStartObj.sz = MATH.average(_width,_height)        
    
    if d_baseDat:
        log.debug("|{0}| >>  baseDat...".format(_str_func)+ '-'*40)
        #pprint.pprint(d_baseDat)
        for k,vec in list(d_baseDat.items()):
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
                    
                if k == 'lever':
                    log.debug("|{0}| >>  Aiming lever....".format(_str_func))
                    
                    _posAim = DIST.get_pos_by_vec_dist(_pos, TRANS.transformDirection(self.mNode,d_baseDat['up']),baseSize[2])
                    _vecUp = MATH.get_vector_of_two_points(_pos,pos_self)
                    SNAP.aim_atPoint(mHandle.mNode,_posAim,'y+',vectorUp=_vecUp)                    
                    
                    #_posAim = DIST.get_pos_by_vec_dist(pos_self, TRANS.transformDirection(self.mNode,baseAim),baseSize[2])
                    #SNAP.aim_atPoint(mHandle.mNode,_posAim,'z+',vectorUp=TRANS.transformDirection(self.mNode,d_baseDat['up']))
                    
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

def get_tagMessage(self,selfKey=None, msgList = None, idx = None):
    _str_func = 'get_tagMessage'
    log.debug(cgmGEN.logString_start(_str_func))    
    
    if selfKey:
        return self.getMessageAsMeta(selfKey)
    
    if msgList:
        if msgList:
            _res = self.msgList_get(msgList)
            
            
            
    if idx is not None:
        return _res[idx]
    return _res




def get_handleIndices(self):

    try:idx_start,idx_end = self.atBlockModule('get_handleIndices')
    except:
        idx_start = 0
        idx_end =-1
        
    return idx_start,idx_end

@cgmGEN.Timer
def prerig_handlesLayout(self,mode='even',curve='linear',spans=2):
    _str_func = 'prerig_handlesLayout'
    log.debug(cgmGEN.logString_start(_str_func))
    
    ml_prerig = self.msgList_get('prerigHandles')
    if not ml_prerig:
        return log.error(cgmGEN.logString_msg(_str_func,'No prerigHandles found'))
    
    ml_preUse = []
    for mObj in ml_prerig:
        if mObj.getMayaAttr('cgmType') in ['blockHandle','formHandle','preHandle','blockHelper']:
            ml_preUse.append(mObj)
            #print mObj
            
    try:idx_start,idx_end = self.atBlockModule('get_handleIndices')
    except:
        idx_start = 0
        idx_end =len(ml_preUse)-1
        
    mStart = ml_preUse[idx_start]
    mEnd = ml_preUse[idx_end]
    
    idx_startNew = ml_preUse.index(mStart)
    idx_endNew = ml_preUse.index(mEnd)
    
    ml_toSnap = ml_preUse[idx_startNew:idx_endNew+1]
    #pprint.pprint(vars())
    if not ml_toSnap:
        raise ValueError("|{0}| >>  Nothing found to snap | start: {1} | end: {2} | {3}".format(_str_func,idx_start,idx_end,self))
    
    #pprint.pprint(vars())
    
    return ARRANGE.alongLine([mObj.mNode for mObj in ml_toSnap],mode,curve,spans)

    
def handles_snapToRotatePlane(self,mode = 'form',cleanUp=0):
    _str_func = 'handles_snapToRotatePlane'
    log.debug(cgmGEN.logString_start(_str_func))

    log.debug(cgmGEN.logString_msg(_str_func,'dat get'))
    
    
    ml_handles = self.msgList_get('{0}Handles'.format(mode))
    if not ml_handles:
        raise ValueError("|{0}| >>  No {2} handles | {1}".format(_str_func,self,mode))
    
    ml_use = []
    for mObj in ml_handles:
        if mObj.getMayaAttr('cgmType') in ['blockHandle','preHandle','formHandle']:
            ml_use.append(mObj)
        else:
            log.debug("|{0}| >> Removing from list: {1}.".format(_str_func,mObj))    
    ml_handles = ml_use
    
    mOrientHelper = self.getMessageAsMeta('vectorRpHelper')
    if mOrientHelper:
        log.debug("|{0}| >>  RP helper found...".format(_str_func))
        vector_pos = mOrientHelper.getAxisVector('y+',asEuclid = 0)
        vector_neg = mOrientHelper.getAxisVector('y-',asEuclid = 0)        
    else:
        try:mOrientHelper = self.orientHelper
        except:raise ValueError("No orientHelper found")
        
        vector_pos = mOrientHelper.getAxisVector('y+',asEuclid = 0)
        vector_neg = mOrientHelper.getAxisVector('y-',asEuclid = 0)        
    
    log.debug("|{0}| >>  mOrientHelper: {1}".format(_str_func,mOrientHelper))
   
    try:idx_start,idx_end = self.atBlockModule('get_handleIndices')
    except:
        idx_start,idx_end = 0,len(ml_handles)-1
    
    if mode == 'form':
        idx_end = -1
        
    log.debug(cgmGEN.logString_msg(_str_func,'Indicies || start: {0} | end: {1}'.format(idx_start,idx_end)))        
    
    mStart = ml_handles[idx_start]
    mEnd = ml_handles[idx_end]
    ml_toSnap = ml_handles[idx_start:idx_end]
    
    log.debug("|{0}| >>  mStart: {1}".format(_str_func,mStart))
    log.debug("|{0}| >>  mEnd: {1}".format(_str_func,mEnd))
    
    if not ml_toSnap:
        raise ValueError("|{0}| >>  Nothing found to snap | {1}".format(_str_func,self))
        
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
          
    for a,v in list(_d.items()):
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
        raise ValueError("|{0}| >>  No prerig handles | {1}".format(_str_func,self))
    
    for mObj in ml_prerig:
        if mObj.getMayaAttr('cgmType') not in ['blockHandle','preHandle']:
            ml_prerig.remove(mObj)
            log.debug("|{0}| >> Removing from list: {0.".format(_str_func,mObj))
            
    
    mOrientHelper = self.getMessageAsMeta('vectorRpHelper')
    if mOrientHelper:
        log.debug("|{0}| >>  RP helper found...".format(_str_func))
        vector_pos = mOrientHelper.getAxisVector('y+',asEuclid = 0)
        vector_neg = mOrientHelper.getAxisVector('y-',asEuclid = 0)        
    else:
        try:mOrientHelper = self.orientHelper
        except:raise ValueError("No orientHelper found")
        
        vector_pos = mOrientHelper.getAxisVector('y+',asEuclid = 0)
        vector_neg = mOrientHelper.getAxisVector('y-',asEuclid = 0)        
    
    log.debug("|{0}| >>  mOrientHelper: {1}".format(_str_func,mOrientHelper))
   
    try:idx_start,idx_end = self.atBlockModule('get_handleIndices')
    except:
        idx_start,idx_end = 0,len(ml_prerig)-1
        
    
    mStart = ml_prerig[idx_start]
    
    mIKOrientHandle = self.getMessageAsMeta('ikOrientHandle')
    if mIKOrientHandle:
        mEnd = mIKOrientHandle
        idx_end = ml_prerig.index(mEnd)
    else:
        mEnd = ml_prerig[idx_end]
    
    log.debug(cgmGEN.logString_msg(_str_func,'Indicies || start: {0} | end: {1}'.format(idx_start,idx_end)))   
    
    ml_toSnap = ml_prerig[idx_start:idx_end]
    
    if not ml_toSnap:
        raise ValueError("|{0}| >>  Nothing found to snap | {1}".format(_str_func,self))
        
    #pprint.pprint(vars())
    
    f_dist = DIST.get_distance_between_points(mStart.p_position,mEnd.p_position)
    f_cast = f_dist * 4.0
    
     
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
          
    for a,v in list(_d.items()):
        ATTR.set(_tessellate,a,v)    
            
    #Snap our joints ---------------------------------------------------------------------------------
    for mObj in ml_toSnap:
        SNAP.go(mObj, _res_body[0], rotation=False, pivot='closestPoint')
            
    #Cleanup --------------------------------------------------------------------------------------------
    if cleanUp:
        mc.delete(_res_body + l_crvs)
        
def prerig_get_upVector(self, markPos = False):
    """
    """
    _str_func = 'prerig_get_upVector'
    log.debug(cgmGEN.logString_start(_str_func))

    mVectorRP = self.getMessageAsMeta('vectorRpHelper')
    pos_use = mVectorRP.p_position
    
    _blockType = self.blockType
    _tag_orient = 'orientHelper'
    if _blockType in ['head']:
        if self.neckBuild:
            _tag_orient = 'orientNeckHelper'
        
    mOrient = self.getMessageAsMeta(_tag_orient)
    
    if not mVectorRP:
        return log.error(cgmGEN.logString_start(_str_func,"No vector rp.") )
    if not mOrient:
        raise log.error( cgmGEN.logString_start(_str_func,"No mOrient.") )
    
    
    rpVectorX = mVectorRP.getTransformDirection(EUCLID.Vector3(1,0,0)).normalized()
    rpVectorY = mVectorRP.getTransformDirection(EUCLID.Vector3(0,1,0)).normalized()
    rpVectorZ = mVectorRP.getTransformDirection(EUCLID.Vector3(0,0,1)).normalized()
    
    upOrientVectorY = mOrient.getTransformDirection(EUCLID.Vector3(0,1,0)).normalized()
    
    closestDot = -1.0
    closestVector = rpVectorY
    
    for v in [rpVectorX, rpVectorY, rpVectorZ]:#rpVectorX, rpVectorY, rpVectorZ
        dot = upOrientVectorY.dot(v)
        if( abs(dot) > closestDot):
            closestDot = abs(dot)
            if dot < 0:
                closestVector = -v
            else:
                closestVector = v
                
    if markPos:
        pos_use = mVectorRP.p_position
        size = TRANS.bbSize_get(mVectorRP.mNode,mode='max') * 2
        crv = DIST.create_vectorCurve(pos_use,closestVector,
                                      size,name='{0}_baseUpVector'.format(self.p_nameBase))
        TRANS.rotatePivot_set(crv,pos_use)
        CORERIG.override_color(crv,'white')
        
    #Now that we have our main up vector, we need to aim at
    ml_prerig = self.msgList_get('prerigHandles')
    if ml_prerig:
        
        log.info(cgmGEN.logString_msg(_str_func,"Prerig dat found. More accurate check.") )
        
        try:idx_start,idx_end = self.atBlockModule('get_handleIndices')
        except:idx_start,idx_end = 0,len(ml_prerig)-1

        mLoc = mVectorRP.doLoc()
        SNAP.aim_atPoint(mLoc.mNode, ml_prerig[idx_end].p_position,mode = 'vector',vectorUp=closestVector)
                
        closestVector =  mLoc.getTransformDirection(EUCLID.Vector3(0,1,0)).normalized()
        mLoc.delete()
        
        if markPos:
            crv_toEnd = CORERIG.create_at(create= 'curveLinear',
                                          l_pos= [pos_use, ml_prerig[idx_end].p_position])
            CORERIG.override_color(crv_toEnd,'white')
            mc.rename(crv_toEnd, '{0}_toEnd'.format(self.p_nameBase))
            
            
        
                
    if markPos:
        size = TRANS.bbSize_get(mVectorRP.mNode,mode='max') * 2
        crv = DIST.create_vectorCurve(pos_use,closestVector,
                                      size,name='{0}_upVector'.format(self.p_nameBase))
        TRANS.rotatePivot_set(crv,pos_use)
        CORERIG.override_color(crv,'white')
        
        

    
    return closestVector

    
@cgmGEN.Timer
def prerig_get_rpBasePos(self,ml_handles = [], markPos = False, forceMidToHandle=False):
    """
    
    """
    _str_func = 'prerig_get_rpBasePos'
    log.debug(cgmGEN.logString_start(_str_func))

    b_passedHandles = False
    if ml_handles:
        ml_use = ml_handles
        b_passedHandles = True
    else:
        ml_handles = self.msgList_get('prerigHandles')
        if not ml_handles:
            ml_handles = self.msgList_get('formHandles')
        
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
        
        mid = int(_len_handles/2)
        mMidHandle = ml_use[mid]
        
    log.debug("|{0}| >> mid: {1}".format(_str_func,mid))
    
    b_absMid = False
    if MATH.is_even(_len_handles) and not forceMidToHandle:
        log.debug("|{0}| >> absolute mid mode...".format(_str_func,mid))
        b_absMid = True
        
    #...Main vector -----------------------------------------------------------------------
    #try:mOrientHelper = self.vectorRpHelper#orientHelper
    #except Exception,err:
    #    return log.warning("|{0}| >> No rp helper found: {1}".format(_str_func,self))
    #vec_base = MATH.get_obj_vector(mOrientHelper, 'y+')
    #vec_base = MATH.get_obj_vector(mOrientHelper, 'y+')
    
    mVectorRP = self.vectorRpHelper
    rpVectorY = mVectorRP.getTransformDirection(EUCLID.Vector3(0,1,0)).normalized()
    closestVector = copy.copy(rpVectorY)
    
    ml_prerig = self.msgList_get('prerigHandles')
    if ml_prerig:
        log.info(cgmGEN.logString_msg(_str_func,"More accurate check.") )
        mLoc = mVectorRP.doLoc()
        
        if b_passedHandles:
            idx_start,idx_end = 0,-1
            SNAP.aim_atPoint(mLoc.mNode, ml_handles[idx_end].p_position,mode = 'vector',vectorUp=closestVector)
        else:
            try:idx_start,idx_end = self.atBlockModule('get_handleIndices')
            except:idx_start,idx_end = 0,len(ml_prerig)-1
            SNAP.aim_atPoint(mLoc.mNode, ml_prerig[idx_end].p_position,mode = 'vector',vectorUp=closestVector)

                
        closestVector =  mLoc.getTransformDirection(EUCLID.Vector3(0,1,0)).normalized()
        mLoc.delete()
    vec_use = closestVector
    log.debug("|{0}| >> Block up: {1}".format(_str_func,vec_use))
    

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
    #vec_use = vec_base
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
    dist_mid = DIST.get_distance_between_points(ml_handles[0].p_position,pos_mid)
    
    #...get new pos
    if self.getMayaAttr('ikRP_pos_mult'):
        _mult = self.getMayaAttr('ikRP_pos_mult')
    else:
        _mult = 1.0
        
    dist_use = MATH.Clamp(dist_mid * _mult, dist_min, None)
    
    log.debug("|{0}| >> Dist min: {1} | dist base: {2} | use: {3}".format(_str_func,
                                                                          dist_min,
                                                                          dist_base,
                                                                          dist_use))
    
    pos_use = DIST.get_pos_by_vec_dist(pos_mid,vec_use,
                                       dist_use)
    #pos_use2 = DIST.get_pos_by_vec_dist(pos_mid,rpVectorY,
    #                                   DIST.get_distance_between_points(ml_handles[0].p_position,
    #                                                                                    pos_mid))
    
    if markPos:
        crv = CORERIG.create_at(create='curve',l_pos= [pos_mid,pos_use])
        crv=mc.rename(crv,'{0}_RPPos'.format(self.p_nameBase))
        TRANS.rotatePivot_set(crv,pos_use)
        CORERIG.override_color(crv,'white')
        #LOC.create(position=pos_use,name='{0}_RPPos'.format(self.p_nameBase))
        #LOC.create(position=pos_use2,name='posClose')
    
    return pos_use
    
    pos_mid = ml_formHandles[mid].p_position


    #Get our point for knee...
    vec_mid = MATH.get_obj_vector(ml_blendJoints[1], 'y+')
    pos_mid = mKnee.p_position
    pos_knee = DIST.get_pos_by_vec_dist(pos_knee,
                                        vec_knee,
                                        DIST.get_distance_between_points(ml_blendJoints[0].p_position, pos_knee)/2)

    mKnee.p_position = pos_knee

    CORERIG.match_orientation(mKnee.mNode, mIKCrv.mNode)    


    return True
        
@cgmGEN.Timer
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

        

@cgmGEN.Timer
def form_shapeHandlesToDefineMesh(self,ml_handles = None):
    _str_func = 'form_shapeHandlesToDefineMesh'
    log.debug(cgmGEN.logString_start(_str_func))
    
    if not ml_handles:
        ml_handles = self.msgList_get('formHandles')
        if not ml_handles:
            return log.error("No handles found")
    mDefineMesh = self.getMessageAsMeta('defineLoftMesh')
    if not mDefineMesh:
        return log.error(cgmGEN.logString_msg(_str_func,'No define Mesh'))
    _surf = mDefineMesh.mNode
    
    l_x = []
    l_y = []
    
    #Need fail safes
    mDefineEndObj = self.defineEndHelper
    mDefineStartObj = self.defineStartHelper
    
    size_base = DIST.get_axisSize(mDefineStartObj.mNode)
    size_end = DIST.get_axisSize(mDefineEndObj.mNode)
    
    ml_use = []
    for mHandle in ml_handles:
        _cgmType = mHandle.getMayaAttr('cgmType')
        if _cgmType in ['blockHelper']:
            continue
        ml_use.append(mHandle)
        
    if self.blockType == 'head':
        ml_use.reverse()
        
    for i,mHandle in enumerate(ml_use):
        log.debug(cgmGEN.logString_msg(_str_func,'Handle: {0}'.format(mHandle)))

        try:
            _mNode = mHandle.mNode
            try:xDist = RAYS.get_dist_from_cast_axis(_mNode,'x',shapes=_surf)
            except:
                log.debug("alternate X...")
                if i:xDist = size_end[0]
                else:xDist = size_base[0]
            
            try:yDist = RAYS.get_dist_from_cast_axis(_mNode,'y',shapes=_surf)
            except:
                log.debug("alternate Y...")                    
                if i:yDist = size_end[1]
                else:yDist = size_base[1]
                
            l_x.append(xDist)
            l_y.append(yDist)

            l_box = [xDist,
                     yDist,
                     xDist]
            if mHandle in [ml_use[0],ml_use[-1]]:
                l_box[2] = MATH.average(xDist,yDist)
            #TRANS.scale_to_boundingBox(_mNode,l_box,freeze=False)
            #DIST.scale_to_axisSize(_mNode,l_box)
            for i,a in enumerate('xyz'):
                ATTR.set(_mNode,'s{0}'.format(a),l_box[i])
            log.debug(l_box)
        except Exception as err:
            log.error("Form Handle failed to scale: {0}".format(mHandle))
            log.error(err)

    #cgmGEN.func_snapShot(vars())
    

    
    """
    DIST.scale_to_axisSize(ml_lofts[0].mNode,
                           [l_x[0],
                            l_y[0],
                            None])
    _size = DIST.get_axisSize(ml_profiles[-1].mNode)
    DIST.scale_to_axisSize(ml_lofts[-1].mNode,
                           [_size[0],
                            _size[1],
                    None])"""


  

@cgmGEN.Timer
def blockProfile_valid(self,update= False):
    _str_func = 'blockProfile_valid'
    log.debug(cgmGEN.logString_start(_str_func))
    
    mBlockModule = self.getBlockModule()
    _ver_module = mBlockModule.__version__
    
    _blockProfile = self.getMayaAttr('blockProfile')
    _d_profiles = mBlockModule.__dict__.get('d_block_profiles',{})
    _typeDict=  _d_profiles.get(_blockProfile,{})
    if _blockProfile and not _typeDict:
        print((cgmGEN._str_subLine))
        log.error(cgmGEN.logString_msg(_str_func,'blockType not found in blockProfiles. Please fix | found {0}'.format(_blockProfile)))
        pprint.pprint(list(_d_profiles.keys()))
        print((cgmGEN._str_subLine))
        return False
    
    if update:
        log.info(cgmGEN.logString_sub(_str_func,"Update..."))            
        verify_blockAttrs(self,queryMode=False)
        blockProfile_load(self,_blockProfile)
        
    print(("[{0}] Profile checks {1}".format(self.p_nameShort, _blockProfile)))            
    return _typeDict   
    
@cgmGEN.Timer
def is_current(self):
    _str_func = 'is_current'
    log.debug(cgmGEN.logString_start(_str_func))
    
    _ver_block = self.version
    mBlockModule = self.getBlockModule()
    _ver_module = mBlockModule.__version__
    
    _blockProfile = self.getMayaAttr('blockProfile')
    _d_profiles = mBlockModule.__dict__.get('d_block_profiles',{})
    _typeDict=  _d_profiles.get(_blockProfile,{})
    if _blockProfile and not _typeDict:
        print((cgmGEN._str_subLine))
        log.error(cgmGEN.logString_msg(_str_func,'blockType not found in blockProfiles. Please fix | found {0}'.format(_blockProfile)))
        pprint.pprint(list(_d_profiles.keys()))
        print((cgmGEN._str_subLine))
        
    
    if _ver_block == _ver_module:
        print(("[{0}] up to date | version: {1}".format(self.p_nameShort, _ver_block)))            
        return True
    
    log.warning("[{0}] out of date || rigBlock: {1} | module: {2}".format(self.p_nameShort, _ver_block, _ver_module))
    return False   

@cgmGEN.Timer
def update(self,force=False,stopState = 'define'):
    """
    Bring a rigBlock to current settings - check attributes, reset baseDat
    """
    _str_func = 'update'
    log.debug(cgmGEN.logString_start(_str_func))
    _short = self.mNode
    
    if is_current(self) and not force:
        return True
    
    log.debug(cgmGEN.logString_sub(_str_func,"Checking blockProfile"))
    blockType = self.blockType
    mBlockModule = self.p_blockModule
    _blockProfile = self.getMayaAttr('blockProfile')
    _d_profiles = {}        
    try:_d_profiles = mBlockModule.d_block_profiles
    except:
        log.error(cgmGEN.logString_msg(_str_func,'No d_block_profile_found'))
        
    _typeDict=  _d_profiles.get(_blockProfile,{})
    if _blockProfile and not _typeDict:
        log.error(cgmGEN.logString_msg(_str_func,'blockType not found in blockProfiles. Please fix | found {0}'.format(_blockProfile)))
        pprint.pprint(list(_d_profiles.keys()))
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
                
    if force:
        for a in mc.listAttr(self.mNode,ud=True):
            if a not in ['mClass','blockType','blockDat','blockType',
                         'cgmName','baseSize',
                         'blockParent','blockChildren','blockMirror']:
                try:ATTR.delete(_short,a)
                except Exception as err:log.error("Failed to delete: {0} | {1}".format(a,err))
        self.verify()
        changeState(self,'define',forceNew=True)
        
        if _baseDat:
            log.debug(cgmGEN.logString_msg(_str_func,'baseDat: {0}'.format(_baseDat)))
            self.baseDat = _baseDat
    
    if stopState is not None:
        _dat['blockState'] = stopState
    self.blockDat = _dat
    
    
    blockDat_load(self,redefine=True,overrideMode='update')
    
    try:self.doStore('version', mBlockModule.__version__, 'string',lock=True)
    except Exception as err:
        log.error(cgmGEN.logString_msg(_str_func,"Failed to set version | {0}".format(err)))
    #Verify
    #verify_blockAttrs(self, queryMode=False)
    #Check out base dat
    
    #pprint.pprint(vars())
    
    return True   

        
        
@cgmGEN.Timer
def rebuild(self, stopState = 'define'):
    """
    Bring a rigBlock to current settings - check attributes, reset baseDat
    """
    _str_func = 'rebuild'
    log.debug(cgmGEN.logString_start(_str_func))
    _short = self.mNode

    log.debug(cgmGEN.logString_sub(_str_func,"Checking blockProfile"))
    blockType = self.blockType
    mBlockModule = self.p_blockModule
    _blockProfile = self.getMayaAttr('blockProfile')
    _d_profiles = {}        
    try:_d_profiles = mBlockModule.d_block_profiles
    except:
        log.error(cgmGEN.logString_msg(_str_func,'No d_block_profile_found'))
        
    _typeDict=  _d_profiles.get(_blockProfile,{})
    if _blockProfile and not _typeDict:
        log.error(cgmGEN.logString_msg(_str_func,'blockType not found in blockProfiles. Please fix | found {0}'.format(_blockProfile)))
        pprint.pprint(list(_d_profiles.keys()))
        return False
    _baseDat = _typeDict.get('baseDat')
    
    ml_children = self.getBlockChildren()
    
    mBlockMirror = self.getMessageAsMeta('blockMirror')
    
    _blockType = self.blockType
    _side = get_side(self)
    
    l_datKeys = ATTR.get_datListKeys(_short)
    d_lists = {}
    for l in l_datKeys:
        if ATTR.datList_exists(_short,l):
            d_lists[l] = ATTR.datList_get(_short,l)
            
    _d = {'blockType':self.blockType,
          'autoForm':False,
          'side':_side,
          'baseSize':baseSize_get(self),
          'blockProfile':_blockProfile,
          'blockParent': self.p_blockParent}
    

    for a in 'cgmName','blockProfile':
        if a in ['cgmName']:
            _d['name'] =  self.getMayaAttr(a)
        elif self.hasAttr(a):
            _d[a] = self.getMayaAttr(a)        
    
    blockDat = self.getBlockDat()
    if blockDat['ud'].get('baseDat'):
        blockDat['ud'].pop('baseDat')
            
    mLoc = self.doLoc()
    self.delete()
    
    
    mDup = cgmMeta.createMetaNode('cgmRigBlock',
                                  **_d)
    
    mDup.doSnapTo(mLoc)
    mLoc.delete()

    

    mDup.blockDat = blockDat
    
    #if _baseDat:
        #log.warning(cgmGEN.logString_msg(_str_func,'resetting baseDat: {0}'.format(_baseDat)))
        #mDup.baseDat = _baseDat                        
    
    for a,l in list(d_lists.items()):
        ATTR.datList_connect(mDup.mNode,a,l)
        
    blockDat_load(mDup)

    for mChild in ml_children:
        mChild.p_blockParent = mDup
    
    if mBlockMirror:
        mDup.connectChildNode(mBlockMirror,'blockMirror','blockMirror')#Connect
        
        
        
    return mDup        
        
        
@cgmGEN.Timer
def to_scriptEditor(self,mode = 'block', blockString ='mBlock', facString = 'mRigFac'):
    _str_func = 'to_scriptEditor'
    log.debug(cgmGEN.logString_start(_str_func))
    log.debug(cgmGEN.logString_msg(_str_func,"Mode: {0} | string: {1}".format(mode,blockString)))
    
    if mode == 'rigFactory':
        mel.eval('python "import cgm.core.cgm_Meta as cgmMeta;{1} = cgmMeta.asMeta({0});{2} = {1}.asRigFactory()"'.format("'{0}'".format(self.mNode),blockString,facString))
    else:
        mel.eval('python "import cgm.core.cgm_Meta as cgmMeta;{1} = cgmMeta.asMeta({0});"'.format("'{0}'".format(self.mNode),blockString))


@cgmGEN.Timer
def blockModule_setLogger(self,mode = 'debug'):
    _str_func = 'to_scriptEditor'
    log.debug(cgmGEN.logString_start(_str_func))
    mModule = self.p_blockModule
    if mode == 'debug':
        mModule.log.setLevel(mModule.logging.DEBUG)
    else:
        mModule.log.setLevel(mModule.logging.INFO)

        
@cgmGEN.Timer
def blockScale_bake(self,sizeMethod = 'axisSize',force=False,):
    """
    Bring a rigBlock to current settings - check attributes, reset baseDat
    """
    _str_func = 'bake_blockScale'
    log.debug(cgmGEN.logString_start(_str_func))
    str_self = self.mNode
    
    if self.p_parent:
        return log.error(cgmGEN.logString_msg(_str_func, "Can't bake parented blocks, please unparent"))
    
    _blockScale = self.blockScale
    
    if MATH.is_float_equivalent(_blockScale,1):
        log.debug(cgmGEN.logString_msg(_str_func, 'Already 1.0'))
        return True
    
    if self.hasAttr('baseSize'):
        _baseSize = True
        for a in 'xyz':
            if ATTR.is_connected(str_self,'baseSize'+a.capitalize()):
                _baseSize=False
                break
        if _baseSize:
            log.info(cgmGEN.logString_msg(_str_func, 'baseSize buffer. Not connected'))
            self.baseSize = baseSize_get(self)
                    
    _factor = 1.0/_blockScale
    
    ml_ctrls = controls_get(self, define=True, form=True, prerig=True)
    md_dat = {}
    
    log.debug(cgmGEN.logString_sub(_str_func, 'Gather Dat'))
    #First Loop gateher
    for i,mCtrl in enumerate(ml_ctrls):
        _str = mCtrl.p_nameShort
        _d = {'str':_str}
        
        if not ATTR.is_locked(_str,'translate'):
            _d['pos']=mCtrl.p_position
            
        _d['lossyScale'] = TRANS.scaleLossy_get(_str)
        _d['worldScale'] = mc.xform(_str, q=True, scale = True, worldSpace = True, absolute = True)
        _d['factorScale'] = [v*_factor for v in _d['worldScale']]
        
        _d['noParent'] = False
        if ATTR.is_locked(_str,'translate'):
            _d['noParent'] = True
        
        
        for a in ['sx','sy','sz']:
            if not ATTR.is_locked(_str,a):
                v = ATTR.get(_str,a)
                #if not MATH.is_float_equivalent(1.0,v):
                _d[a] = v * _blockScale
                if not _d.get('axisSize'):
                    _d['axisSize'] = DIST.get_axisSize(_str)
                if not _d.get('bbSize'):
                    _d['bbSize'] = TRANS.bbSize_get(_str)
                
        md_dat[i] = _d
        
    
    #pprint.pprint(md_dat)
    #return
    log.debug(cgmGEN.logString_msg(_str_func, 'Setting intiial'))
    ATTR.set(self.mNode,'blockScale',1.0)
    """
    blockDat_save(self)
    blockDat_load(self,redefine=True)                
    ml_ctrls = controls_get(self, define=True, form=True, prerig=True)        
    """
    
    for ii in range(3):#3 loop to account for parentage
        log.debug(cgmGEN.logString_sub(_str_func, 'Push: {0}'.format(ii)))

        for i,mCtrl in enumerate(ml_ctrls):
            _d = md_dat[i]
            log.debug(cgmGEN.logString_msg(_str_func, "{0} | {1}".format(_d['str'],_d)))
            _pos = _d.get('pos')
            _noParent = _d['noParent']
            
            if _pos:mCtrl.p_position = _pos
            
            
            _worldScale = _d.get('worldScale')
            if _worldScale and _noParent is not True:
                mParent = mCtrl.p_parent
                if mParent:
                    mCtrl.p_parent = False
                    
                #mc.xform(mCtrl.mNode, scale = _worldScale, objectSpace = True, absolute = True)
                mc.xform(mCtrl.mNode, scale = _worldScale, worldSpace = True, absolute = True)
                
                if mParent:mCtrl.p_parent = mParent
            else:
                if not ATTR.is_locked(mCtrl.mNode,'scale'):
                    """
                    _worldScale = _d.get('factorScale')
                    if _worldScale:
                        mc.xform(_str, scale = _worldScale, worldSpace = True, )#absolute = True
                        
                        for a in ['sx','sy','sz']:
                            if _d.get(a):
                                ATTR.set(_d['str'],a,_d[a])"""
                    
                    if sizeMethod == 'axisSize':
                        if _d.get('axisSize'):
                            try:
                                DIST.scale_to_axisSize(_d['str'],_d['axisSize'])
                            except Exception as err:
                                log.warning(cgmGEN.logString_msg(_str_func, "{0} | failed to axisSize {1}".format(_d['str'],err)))
                    elif sizeMethod in ['bb','bbSize']:
                        if _d.get('bbSize'):
                            try:
                                #reload(TRANS)
                                TRANS.scale_to_boundingBox(_d['str'],_d['bbSize'],freeze=False)
                            except Exception as err:
                                log.warning(cgmGEN.logString_msg(_str_func, "{0} | failed to axisSize {1}".format(_d['str'],err)))
            """
            if ii == 0:
                _worldScale = _d.get('factorScale')
                if _worldScale:
                    mc.xform(_str, scale = _worldScale, worldSpace = True, )#absolute = True
                    
                    for a in ['sx','sy','sz']:
                        if _d.get(a):
                            ATTR.set(_d['str'],a,_d[a])
                    
                    if sizeMethod == 'axisSize':
                        if _d.get('axisSize'):
                            try:
                                DIST.scale_to_axisSize(_d['str'],_d['axisSize'])
                            except Exception,err:
                                log.warning(cgmGEN.logString_msg(_str_func, "{0} | failed to axisSize {1}".format(_d['str'],err)))
                    elif sizeMethod in ['bb','bbSize']:
                        if _d.get('bbSize'):
                            try:
                                reload(TRANS)
                                TRANS.scale_to_boundingBox(_d['str'],_d['bbSize'],freeze=False)
                            except Exception,err:
                                log.warning(cgmGEN.logString_msg(_str_func, "{0} | failed to axisSize {1}".format(_d['str'],err)))"""        
    #Fix the root shape
    #if not ATTR.is_connected(self.mNode,'baseSize'):
        #log.info(cgmGEN.logString_sub(_str_func, 'Base size buffer'))
        
    rootShape_update(self)
    #pprint.pprint(vars())
    return True   

        
        
@cgmGEN.Timer
def rootShape_update(self):
    """
    Bring a rigBlock to current settings - check attributes, reset baseDat
    """
    _str_func = 'rootShape_update'
    log.debug(cgmGEN.logString_start(_str_func))
    
    if self.blockType in ['master']:
        return True
    _size = defineSize_get(self)

    #_sizeSub = _size / 2.0
    log.debug("|{0}| >>  Size: {1}".format(_str_func,_size))        
    _crv = CURVES.create_fromName(name='cubeX',
                                  direction = 'z+', size = _size)

    SNAP.go(_crv,self.mNode,)
    CORERIG.override_color(_crv, 'white')
    CORERIG.shapeParent_in_place(self.mNode,_crv,False,True)
    self.addAttr('cgmColorLock',True,lock=True,hidden=True)          
    
    return True   

@cgmGEN.Timer
def get_orienationDict(self,orienation='zyx'):
    """
    Bring a rigBlock to current settings - check attributes, reset baseDat
    """
    _str_func = 'rootShape_update'
    log.debug(cgmGEN.logString_start(_str_func))
    
    _d = {}
    _mOrientation = VALID.simpleOrientation('zyx')#cgmValid.simpleOrientation(str(modules.returnSettingsData('jointOrientation')) or 'zyx')
    _d['str'] = _mOrientation.p_string
    _d['mOrientation'] = _mOrientation
    _d['vectorAim'] = _mOrientation.p_aim.p_vector
    _d['vectorUp'] = _mOrientation.p_up.p_vector
    _d['vectorOut'] = _mOrientation.p_out.p_vector
 
    _d['vectorAimNeg'] = _mOrientation.p_aimNegative.p_vector
    _d['vectorUpNeg'] = _mOrientation.p_upNegative.p_vector
    _d['vectorOutNeg'] = _mOrientation.p_outNegative.p_vector
    
    
    _d['stringAim'] = _mOrientation.p_aim.p_string
    _d['stringUp'] = _mOrientation.p_up.p_string
    _d['stringOut'] = _mOrientation.p_out.p_string
 
    _d['stringAimNeg'] = _mOrientation.p_aimNegative.p_string
    _d['stringUpNeg'] = _mOrientation.p_upNegative.p_string
    _d['stringOutNeg'] = _mOrientation.p_outNegative.p_string        
    return _d


def shapes_castTest(self,orient= 'zyx'):
    
    if self.blockType in ['master','eye','brow','mouth']:
        return
        
    if not is_skeleton(self):
        raise ValueError("Must be skeletonized | {0}".format(self))
    
    mFac = self.asRigFactory()
    
    ml_joints = self.prerigNull.msgList_get('handleJoints')
    if not ml_joints:  
        ml_joints = mFac.mRigNull.msgList_get('moduleJoints')
    
    if not ml_joints:
        return log.error("Must have joints")
    
    
    mHandleFactory = self.asHandleFactory()
    
    
    mdOrient = get_orienationDict(self,orient)
    
    _castVector = self.getEnumValueString('castVector')
    _aimVector = mdOrient.get('string{0}'.format(CORESTRING.capFirst(_castVector)))
    
    _offset = mFac.mPuppet.atUtils('get_shapeOffset')
    if self.getMayaAttr('controlOffsetMult'):
        _offset = _offset * self.controlOffsetMult
    
    mFac.d_orientation = mdOrient
    ml_shapes = mFac.atBuilderUtils('shapes_fromCast',
                                    targets = ml_joints,
                                    offset = _offset,
                                    aimVector = _aimVector,
                                    mode = 'frameHandle')   
    #pprint.pprint(vars())
    
    for i,mObj in enumerate(ml_shapes):
        mObj.p_parent = False
        mObj.rename("{0}_previs".format(ml_joints[i].p_nameBase))
        mHandleFactory.color(mObj.mNode, controlType = 'main')        
                
    
@cgmGEN.Wrap_suspendCall
def mesh_proxyCreate(self, targets = None, aimVector = None, degree = 1,firstToStart=False, 
                     ballBase = True,
                     ballMode = 'asdf',
                     ballPosition = 'joint',
                     reverseNormal=False,
                     extendCastSurface = False,
                     l_values = [],
                     orient = 'zyx',
                     hardenEdges = False,
                     extendToStart = True,method = 'u'):
    #try:
    _short = self.mNode
    _str_func = 'mesh_proxyCreate'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    if self.getMayaAttr('isBlockFrame'):
        log.debug(cgmGEN.logString_sub(_str_func,'blockFrame bypass'))
        return            
    

    mRigNull = self.moduleTarget.rigNull
    ml_shapes = []

    _offset = get_shapeOffset(self) or .25
    _dir = get_side(self)#self.d_module.get('direction')
    mdOrient = get_orienationDict(self,orient)
    
    
    
    if aimVector is None:
        if self.hasAttr('castVector'):
            _castVector = self.getEnumValueString('castVector')
            aimVector = mdOrient.get('string{0}'.format(CORESTRING.capFirst(_castVector)))
            
            if 'Neg' in _castVector:
                _castNeg = _castVector.replace('Neg','')
                aimAlternate = mdOrient.get('string{0}'.format(CORESTRING.capFirst(_castNeg)))
            else:
                aimAlternate = mdOrient.get('string{0}Neg'.format(CORESTRING.capFirst(_castVector)))

        else:
            if _dir and _dir.lower() == 'left':
                aimVector = mdOrient['mOrientation'].p_outNegative.p_string
            else:
                aimVector = mdOrient['mOrientation'].p_out.p_string
            
        aimAlternate = mdOrient['mOrientation'].p_up.p_string

    #Get our prerig handles if none provided
    if targets is None:
        ml_targets = mRigNull.msgList_get('rigJoints',asMeta = True)
        if not ml_targets:
            raise ValueError("No rigJoints connected. NO targets offered")
    else:
        ml_targets = cgmMeta.validateObjListArg(targets,'cgmObject')


    ml_handles = self.msgList_get('formHandles',asMeta = True)


    mMesh_tmp =  get_castMesh(self,extend=extendCastSurface)
    str_meshShape = mMesh_tmp.getShapes()[0]


    #Process ----------------------------------------------------------------------------------
    l_newCurves = []
    l_pos = []
    str_meshShape = mMesh_tmp.getShapes()[0]
    log.debug("|{0}| >> Shape: {1}".format(_str_func,str_meshShape))
    """
    minU = ATTR.get(str_meshShape,'minValueU')
    maxU = ATTR.get(str_meshShape,'maxValueU')

    l_failSafes = MATH.get_splitValueList(minU,maxU,
                                          len(ml_targets))
    log.debug("|{0}| >> Failsafes: {1}".format(_str_func,l_failSafes))

    l_uIsos = SURF.get_dat(str_meshShape, uKnots=True)['uKnots']
    log.debug("|{0}| >> Isoparms U: {1}".format(_str_func,l_uIsos))
    """
    _cap = method.capitalize()
    minU = ATTR.get(str_meshShape,'minValue{0}'.format(_cap))
    maxU = ATTR.get(str_meshShape,'maxValue{0}'.format(_cap))
    l_failSafes = MATH.get_splitValueList(minU,maxU,
                                          len(ml_targets))
    log.debug("|{0}| >> Failsafes: {1}".format(_str_func,l_failSafes))

    if method == 'u':
        l_uIsos = SURF.get_dat(str_meshShape, uKnots=True)['uKnots']
    else:
        l_uIsos = SURF.get_dat(str_meshShape, vKnots=True)['vKnots']

    log.debug("|{0}| >> Isoparms {2}: {1}".format(_str_func,l_uIsos,_cap))        

    l_uValues = []
    str_start = False
    l_sets = []
    #First loop through and get our base U Values for each point
    for i,mTar in enumerate(ml_targets):
        j = mTar.mNode
        _d = RAYS.cast(str_meshShape,j,aimVector)
        l_pos.append(mTar.p_position)
        log.debug("|{0}| >> Casting {1} ...".format(_str_func,j))
        _v = None
        #cgmGEN.log_info_dict(_d,j)
        if not _d:
            _d_alt = RAYS.cast(str_meshShape,j,aimAlternate)
            if not _d_alt:
                log.warning("|{0}| >> Using failsafe value for: {1}".format(_str_func,j))
                _v = l_failSafes[i]
            else:
                _d = _d_alt

        if _v is None:
            if method == 'v':
                _v = _d['uvsRaw'][str_meshShape][0][1]
            else:
                _v = _d['uvsRaw'][str_meshShape][0][0]

        log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))

        l_uValues.append(_v)

    _b_singleMode =False
    if len(l_uValues) < 2:
        l_uValues.append(maxU)
        _b_singleMode = True

    log.debug("|{0}| >> uValues: {1} ...".format(_str_func,l_uValues))

    for i,v in enumerate(l_uValues):
        _l = [v]

        for uKnot in l_uIsos:
            if uKnot > v:
                if v == l_uValues[-1]:
                    if uKnot < maxU:
                        _l.append(uKnot)
                elif uKnot < l_uValues[i+1]:
                    if (l_uValues[i+1] - uKnot < .01):
                        l_uValues[i] = uKnot
                        v=uKnot
                    else:
                        _l.append(uKnot)

        if v == l_uValues[-1]:
            _l.append(maxU)
        else:
            _l.append(l_uValues[i+1])

        """
        for ii,v2 in enumerate(_l):
            if ii:
                if _l[ii-1] - v2 < 1:
                    _l.remove(v2)"""

        l_sets.append(_l)
        log.debug("|{0}| >> uSet [{1}] : {2} ...".format(_str_func,i,_l))

    if extendToStart:
        _low = min(l_sets[0])
        l_add =[]
        for v in l_uIsos:
            if v < _low:
                l_add.append(v)
        l_add.reverse()
        for v in l_add:
            l_sets[0].insert(0,v)

    l_created = []
    d_curves = {}
    def getCurve(uValue):
        _crv = d_curves.get(uValue)
        if _crv:return _crv
        _crv = mc.duplicateCurve("{0}.{2}[{1}]".format(str_meshShape,uValue,method), ch = 0, rn = 0, local = 0)[0]
        #_crv = mc.rename(_crv,"u{0}_crv".format(str(uValue)))
        d_curves[uValue] = _crv
        log.debug("|{0}| >> created: {1} ...".format(_str_func,_crv))        
        l_created.append(_crv)
        return _crv

    _degree = 1
    #if self.loftDegree:
    #    _degree = 3

    #>>Reloft those sets of curves and cap them ------------------------------------------------------------
    log.debug("|{0}| >> Create new mesh objs.".format(_str_func))
    l_new = []
    _len_targets = len(ml_targets)
    for i,uSet in enumerate(l_sets):
        if i  and _b_singleMode:
            log.debug("|{0}| >> SINGLE MODE".format(_str_func))                
            break
        mc.select(cl=1)
        log.debug(cgmGEN.logString_sub(_str_func,"{0} | u's: {1}".format(i,uSet)))

        _loftCurves = [getCurve(uValue) for uValue in uSet]
        
        _mesh = None

        if ballBase and i != 0:
            log.debug("|{0}| >> ball started...".format(_str_func))
            CORERIG.match_transform(_loftCurves[0],ml_targets[i])
            TRANS.pivots_recenter(_loftCurves[0])


            if ballMode == 'loft':
                root = mc.duplicate(_loftCurves[0])[0]
                
                #We need some tighten edge values to use as well
                #startTight = getCurve(uSet[0]+.001)
                #endTight = getCurve(uSet[-1]-.001)
                
                #_loftCurves.insert(1,startTight)
                #_loftCurves.insert(-2,endTight)
                
                try:
                    #mc.select(cl=1)
                    #mc.refresh(su=0)

                    log.debug("Planar curve from: {0}".format(_loftCurves[0]))
                    _planar = mc.planarSrf(_loftCurves[0],ch=0,d=3,ko=0,rn=0,po=0,tol = 20)[0]
                    vecRaw = SURF.get_uvNormal(_planar,.5,.5)
                    vec = [-v for v in vecRaw]
                    log.debug("|{0}| >> vector: {1}".format(_str_func,vec))                                        
                    p1 = POS.get(_loftCurves[0])
                    #p1 = mc.pointOnSurface(_planar,parameterU=.5,parameterV=.5,position=True)#l_pos[i]                    
                except Exception as err:
                    log.debug(err)
                    try:
                        vec
                        log.debug("|{0}| >> surf fail. Using last vector: {1}".format(_str_func,vec))
                    except:
                        if i:
                            vec = MATH.get_vector_of_two_points(l_pos[i],l_pos[i-1])
                        else:
                            vec =MATH.get_vector_of_two_points(l_pos[i+1],l_pos[i])

                        log.debug("|{0}| >> Using last vector: {1}".format(_str_func,vec))
                    #p1 = l_pos[i]
                    p1 = POS.get(_loftCurves[0])

                try:mc.delete(_planar)
                except:pass
                
                #DIST.create_vectorCurve(p1,vec,10,"vec_{0}".format(i))

                p2 = l_pos[i-1]
                pClose = DIST.get_closest_point(ml_targets[i].mNode, _loftCurves[0])[0]
                dClose = DIST.get_distance_between_points(p1,pClose)
                d2 = DIST.get_distance_between_points(p1,p2)

                #if d2 > dClose:
                log.debug(cgmGEN.logString_msg(_str_func,'d2 >...'))
                
                #planarSrf -ch 1 -d 3 -ko 0 -tol 0.01 -rn 0 -po 0 "duplicatedCurve40";
                #vecRaw = mc.pointOnSurface(_planar,parameterU=.5,parameterV=.5,normalizedNormal=True)


                #vec = _resClosest['normal']

                """
                if uSet == l_sets[-1]:
                    vec = MATH.get_vector_of_two_points(p1,p2)                    
                else:
                    vec = MATH.get_vector_of_two_points(p1,l_pos[i-1])"""                
                    #vec = MATH.get_vector_of_two_points(l_pos[i+1],p1)

                #dMax = min([dClose,_offset*10])
                dMax = (mc.arclen(root)/3.14)/4

                #dMax = dClose * .5#_offset *10
                pSet1 = DIST.get_pos_by_vec_dist(p1,vec,dMax * .5)                
                pSet2 = DIST.get_pos_by_vec_dist(p1,vec,dMax * .85)
                pSet3 = DIST.get_pos_by_vec_dist(p1,vec,dMax)


                #DIST.offsetShape_byVector(root,-_offset)
                ATTR.set(root,'scale',.9)                                        
                mid1 = mc.duplicate(root)[0]
                ATTR.set(mid1,'scale',.7)
                mid2 = mc.duplicate(root)[0]
                ATTR.set(mid2,'scale',.5)                
                end = mc.duplicate(root)[0]
                ATTR.set(end,'scale',.1)

                #DIST.offsetShape_byVector(end,-_offset)

                TRANS.position_set(mid1,pSet1)
                TRANS.position_set(mid2,pSet2)
                TRANS.position_set(end,pSet3)

                #now loft new mesh...
                _loftTargets = [end,mid2,mid1]#root

                _mesh = BUILDUTILS.create_loftMesh(_loftTargets+_loftCurves, name="{0}_{1}".format('test',i), degree=1,divisions=1)

                log.debug("|{0}| >> mesh created...".format(_str_func))                            
                #CORERIG.match_transform(_mesh,ml_targets[i])

                #if reverseNormal:
                    #mc.polyNormal(_mesh, normalMode = 0, userNormalMode=1,ch=0)

                """


                _meshEnd = create_loftMesh(_loftTargets, name="{0}_{1}".format('test',i),
                                           degree=1,divisions=1)

                mc.polyNormal(_meshEnd, normalMode = 0, userNormalMode=1,ch=0)

                _mesh = mc.polyUnite([_mesh,_meshEnd], ch=False )[0]"""
                
                if hardenEdges:
                    try:
                        l_edges = []
                        for c in _loftCurves[0],_loftCurves[-1],root:
                            _crv = mc.duplicate(c)[0]
                            DIST.offsetShape_byVector(_crv, 1.0)
                            _crv2 = mc.duplicate(_crv)[0]
                            DIST.offsetShape_byVector(_crv2, .1, vector= vec, offsetMode='castVector')
                            
                            _checkMesh = BUILDUTILS.create_loftMesh([_crv,_crv2], name = '{}_check'.format(c),degree=1,divisions=1)
                            
                            """
                            _res_body = mc.nurbsToPoly(_planar,mnd=1,ch=0,f=2,pt= 1,pc=200,
                                                       chr=0.9,ft =0.01,mel=0.001,d =0.1,ut =1,
                                                       un =3,vt =1,vn =3,uch =0,ucr =0,
                                                       cht =0.2,es =0,ntr =0,mrt =0,uss =1)[0]"""                            
                            
                            vtxs = GEO.get_vertsFromCurve(_mesh,_checkMesh, mode ='bbCheck')                            
                            #vtxs = GEO.get_vertsFromCurve(_mesh,c)
                            l_edges.extend(GEO.get_edgeLoopFromVerts(vtxs))
                            
                            mc.delete([_crv,_crv2,_checkMesh])
                        mc.polySoftEdge(l_edges, a=0, ch=0)
                    except Exception as err:print(err)
                
                mc.select(cl=1)
                mc.delete([end,mid1,mid2])
                mc.delete(root)


            else:
                log.debug(cgmGEN.logString_msg(_str_func,'d2 <...'))
                
                _mesh = BUILDUTILS.create_loftMesh(_loftCurves, name="{0}_{1}".format('test',i), degree=_degree,divisions=1)
                log.debug("|{0}| >> mesh created...".format(_str_func))                            

                #TRANS.orient_set(_sphere[0], ml_targets[i].p_orient)
                if ballPosition == 'joint':
                    p2 = DIST.get_closest_point(ml_targets[i].mNode, _loftCurves[0])[0]
                    p1 = ml_targets[i].p_position
                    d1 = DIST.get_distance_between_points(p1,p2)

                    try:p1_2 = ml_targets[i+1].p_position
                    except:p1_2 = ml_targets[i-1].p_position

                    d2 = DIST.get_distance_between_points(p1,p1_2)
                    d2 = min([d1,d2])

                    #d_offset = d1 - _offset
                    #log.debug("{0} : {1}".format(d1,d_offset))
                    _sphere = mc.polySphere(axis = [0,0,1],
                                            radius = d1*.5,
                                            subdivisionsX = 10,
                                            subdivisionsY = 10)
                    #_sphere = mc.polyCylinder(axis = [0,0,1],
                    #                          radius = d1,
                    #                          height = d2,
                    #                          subdivisionsX = 1,
                    #                          subdivisionsY = 1)                    
                    #TRANS.scale_to_boundingBox(_sphere[0], [d1*1.75,d1*1.75,d2])

                    SNAP.go(_sphere[0],ml_targets[i].mNode,True,True)

                else:
                    _sphere = mc.polySphere(axis = [1,0,0], radius = 1, subdivisionsX = 10, subdivisionsY = 10)                    
                    _bb_size = SNAPCALLS.get_axisBox_size(_loftCurves[0])
                    _size = [_bb_size[0],_bb_size[1],MATH.average(_bb_size)]
                    _size = [v*.8 for v in _size]
                    SNAP.go(_sphere[0],_loftCurves[0],pivot='bb')
                    TRANS.scale_to_boundingBox(_sphere[0], _size)
                    SNAP.go(_sphere[0],ml_targets[i].mNode,False,True)

                _mesh = mc.polyUnite([_mesh,_sphere[0]], ch=False )[0]

        if not _mesh:
            _mesh = BUILDUTILS.create_loftMesh(_loftCurves, name="{0}_{1}".format('test',i),
                                               degree=_degree,divisions=1)
            log.debug("|{0}| >> mesh created...".format(_str_func))
            
            l_edges = []
            for c in [_loftCurves[-1]]:
                vtxs = GEO.get_vertsFromCurve(_mesh,c)
                l_edges.extend(GEO.get_edgeLoopFromVerts(vtxs))

            try:mc.polySoftEdge(l_edges, a=0, ch=0)                
            except:pass
            
        for s in TRANS.shapes_get(_mesh):
            GEO.normalCheck(s)

        #_mesh = mc.polyUnite([_mesh,_sphere[0]], ch=False )[0]
        #mc.polyNormal(_mesh,setUserNormal = True)
        log.debug(_mesh)
        CORERIG.match_transform(_mesh,ml_targets[i])
        l_new.append(_mesh)

    #...clean up 
    if l_created:mc.delete(l_created)# + [str_tmpMesh]
    mMesh_tmp.delete()

    if str_start:
        mc.delete(str_start)
    #>>Parent to the joints ----------------------------------------------------------------- 
    return l_new
    #except Exception,err:
    #    cgmGEN.cgmException(Exception,err)

@cgmGEN.Timer
def snapShot_controls_get(self,blockMirror=False,define=True,form=True,prerig=True):
    """
    Get a snap shot of all of the controls of a rigBlock
    """
    _str_func = 'snapShot_controls_get'
    log.debug(cgmGEN.logString_start(_str_func))
    str_self = self.mNode
    
    ml_check = []
    md_sourceAll = {}
    md_targetAll = {}
    ml_sourceCheck = []
    ml_targetCheck = []
    
    #Control sets ===================================================================================
    log.debug(cgmGEN.logString_sub(_str_func, 'control sets...'))
    
    def add_mSet(mSet,ml_check,md_sourceAll,name='base'):
        ml_use = []
        for mObj in mSet:
            if mObj not in ml_check:
                log.debug(cgmGEN.logString_msg(_str_func, '{1} | Add: {0}'.format(mObj,name)))
                ml_check.append(mObj)
                ml_use.append(mObj)
            else:
                log.debug(cgmGEN.logString_msg(_str_func, '{1} | Removing: {0}'.format(mObj,name)))
        md_sourceAll[name] = ml_use
        return ml_use

    add_mSet([self],ml_sourceCheck,md_sourceAll,'base')
    if blockMirror:
        add_mSet([blockMirror],ml_targetCheck,md_targetAll,'base')

    if define:
        add_mSet(controls_get(self,define=True),ml_sourceCheck,md_sourceAll,'define')
        if blockMirror:
            ml_use = add_mSet(controls_get(blockMirror,define=True),ml_targetCheck,md_targetAll,'define')
            if not ml_use:
                log.warning(cgmGEN.logString_msg(_str_func, "No [define] dat found on target. removing"))
                md_sourceAll.pop('define')
                md_targetAll.pop('define')

    if form:
        add_mSet(controls_get(self,form=True),ml_sourceCheck,md_sourceAll,'form')
        if blockMirror:
            ml_use = add_mSet(controls_get(blockMirror,form=True),ml_targetCheck,md_targetAll,'form')
            if not ml_use:
                log.warning(cgmGEN.logString_msg(_str_func, "No [form] dat found on target. removing"))
                md_sourceAll.pop('form')
                md_targetAll.pop('form')

    if prerig:
        add_mSet(controls_get(self,prerig=True),ml_sourceCheck,md_sourceAll,'prerig')
        if blockMirror:
            ml_use = add_mSet(controls_get(blockMirror,prerig=True),ml_targetCheck,md_targetAll,'prerig')
            if not ml_use:
                log.warning(cgmGEN.logString_msg(_str_func, "No [prerig] dat found on target. removing"))
                md_sourceAll.pop('prerig')
                md_targetAll.pop('prerig')

    if not blockMirror:
        md_targetAll = copy.copy(md_sourceAll)

    #Shuffle sets ===================================================================================
    log.debug(cgmGEN.logString_sub(_str_func, 'Shuffle sets'))
    ml_controls = []
    for k in 'base','define','form','prerig':
        dat = md_sourceAll.get(k)
        if dat:
            ml_controls.extend(dat)

    if blockMirror is None:
        log.debug("|{0}| >> Self mirror....".format(_str_func))
        ml_targetControls = ml_controls
    else:
        ml_targetControls = []
        for k in 'base','define','form','prerig':
            dat = md_targetAll.get(k)
            if dat:
                ml_targetControls.extend(dat)            
        
    int_lenTarget = len(ml_targetControls)
    int_lenSource = len(ml_controls)

    for i,mObj in enumerate(ml_controls):
        try:
            log.debug(" {0} > = > {1}".format(mObj.p_nameBase, ml_targetControls[i].p_nameBase))
        except:
            log.debug(" {0} > !! > No match".format(mObj.p_nameBase))        
            
    if blockMirror:
        return ml_controls,md_sourceAll,ml_targetControls,md_targetAll
    return ml_controls,md_sourceAll

@cgmGEN.Timer
def snapShot_get(self):
    """
    Bring a rigBlock to current settings - check attributes, reset baseDat
    """
    try:
        
        _progressBar = None
        _str_func = 'snapShot_get'
        log.debug(cgmGEN.logString_start(_str_func))
        str_self = self.mNode
        
        _blockScale = self.blockScale
                
        
        md_ctrls = controls_get(self, define=True, form=True, prerig=True,asDict=True,getExtra=0)
        md_dat = {}
        
        md_ctrls['base']=[self]
        
        log.debug(cgmGEN.logString_sub(_str_func, 'Gather Dat'))
        
        for datSet,dat in list(md_ctrls.items()):
            md_dat[datSet] = {}
            try:_progressBar = CGMUI.doStartMayaProgressBar(stepMaxValue=len(dat))
            except:_progressBar = None
            
            for i,mCtrl in enumerate(dat):
                _str = mCtrl.p_nameShort
                _d = {'str':_str,
                      'mObj':mCtrl,
                      'nameBase':mCtrl.p_nameBase,
                      'cgmTags':mCtrl.getNameDict()}
                
                _strStatus = "{0} | {1} ".format(_str_func,_str)
                log.debug(cgmGEN.logString_sub(_str_func,_str))
                if _progressBar:CGMUI.progressBar_set(_progressBar,step=1,
                                                      status = _strStatus)                
                
                if not ATTR.is_locked(_str,'translate'):
                    _d['pos']=mCtrl.p_position
                
                if not ATTR.is_locked(_str,'rotate'):
                    _d['orient']=mCtrl.p_orient
                
                    
                _d['lossyScale'] = TRANS.scaleLossy_get(_str)
                _d['worldScale'] = mc.xform(_str, q=True, scale = True, worldSpace = True, absolute = True)
                
                _d['noParent'] = False
                if ATTR.is_locked(_str,'translate'):
                    _d['noParent'] = True
                
                
                for a in ['sx','sy','sz']:
                    if not ATTR.is_locked(_str,a):
                        v = ATTR.get(_str,a)
                        #if not MATH.is_float_equivalent(1.0,v):
                        _d[a] = v 
                        if not _d.get('axisSize'):
                            _d['axisSize'] = DIST.get_axisSize(_str)
                        if not _d.get('bbSize'):
                            _d['bbSize'] = TRANS.bbSize_get(_str)
                        
                md_dat[datSet][i] = _d
        
        #pprint.pprint(md_dat)
        self.__snapShotDat = md_dat
        return md_dat   
    finally:
        if _progressBar:CGMUI.doEndMayaProgressBar()


@cgmGEN.Timer
def snapShot_set(self, md_dat = None, sizeMethod = 'bb', mainHandleNormalizeScale=True):
    """
    Bring a rigBlock to current settings - check attributes, reset baseDat
    """
    try:
        _str_func = 'snapShot_set'
        log.debug(cgmGEN.logString_start(_str_func))
        str_self = self.mNode
        
        if md_dat is None:
            md_dat = self.__snapShotDat
            


        md_ctrls = controls_get(self, define=True, form=True, prerig=True,asDict=True,getExtra=0)
        md_ctrls['base']=[self]
        
        log.debug(cgmGEN.logString_sub(_str_func, 'Gather Dat'))
        #_progressBar = CGMUI.doStartMayaProgressBar(stepMaxValue=len(ml_ctrls))
        _state = self.getEnumValueString('blockState')
        
        md_missing = []
        
        def matchControl(mDat,idx,datSet):
            def match(mObj):
                mDat['mCtrl'] = mObj
                mDat['strNew'] = mObj.mNode
                #md_dat[datSet][idx] = mDat#...force back
                ml_matched.append(mObj)
                ml_unmatched.remove(mObj)
                return mObj
            
            if datSet == 'base':
                return self
            
            mCtrl = mDat.get('mObj')
            if mCtrl.mNode:
                return match(mCtrl)
            
            #Str check
            mCandidate = cgmMeta.validateObjArg(mDat['str'],noneValid=True)
            if mCandidate:
                log.info(cgmGEN.logString_msg(_str_func, "Str Validated | {0} == {1}".format(mDat['nameBase'],mCandidate)))
                return match(mCandidate)
            
            for mObj in md_ctrls[datSet]:
                if mObj.getNameDict() == mDat['cgmTags']:
                    log.info(cgmGEN.logString_msg(_str_func, "cgmTag Validated | {0}".format(mDat['cgmTags'])))
                    return match(mObj)
            
            try:
                log.info(cgmGEN.logString_msg(_str_func, "Index Validated | {0}".format(idx)))
                mObj =  match(md_ctrls[datSet][idx])
                return match(mObj)
            except:pass
            
            log.error(cgmGEN.logString_msg(_str_func, "Missing: {0}".format(mDat['nameBase'])))
            md_missing.append(mDat)
            return False
        
        for datSet in 'base','define','form','prerig':
            mDatSet = md_dat[datSet]
            log.info(cgmGEN.logString_msg(_str_func, "{0}...".format(datSet)))
            ml_matched = []
            ml_unmatched = copy.copy(md_ctrls[datSet])
            
            for ii in range(3):#3 loop to account for parentage
                log.info(cgmGEN.logString_sub(_str_func, 'Push: {0}'.format(ii)))
                for i,mDat in list(mDatSet.items()):                    

                    mCtrl = mDat.get('mCtrl')
                    if not mCtrl:
                        mCtrl = matchControl(mDat,i,datSet)
                        
                    if not mCtrl:
                        log.error(cgmGEN.logString_msg(_str_func, "Missing: {0} | pass: {1}".format(mDat['nameBase'], ii)))
                        continue
                    
                    str_short = mCtrl.mNode#mDat['strNew']
                    log.info(cgmGEN.logString_msg(_str_func, "{0} | {1} | {2}".format(i,str_short,mDat)))
                    
                    _d = mDat
                    log.debug(cgmGEN.logString_msg(_str_func, "{0} | {1}".format(str_short,_d)))
                    
                    #Scale...
                    if datSet != 'base':
                        _bb = mDat.get('bbSize')
                        _scaleDone = False

                        if _bb:
                            if mainHandleNormalizeScale and mCtrl.getMayaAttr('cgmType') in ['blockHandle','formHandle']:
                                _average = MATH.average(_bb)
                                mc.scale(_average,_average,_average, str_short, absolute = True)
                                _scaleDone = True
                                #TRANS.scale_to_boundingBox(str_short,[_average,_average,_average],freeze=False)
                        
                        if not _scaleDone:
                            if sizeMethod == 'bb' and _bb:
                                TRANS.scale_to_boundingBox_relative(str_short,_bb,freeze=False)
                            else:
                                for ii,a in enumerate('xyz'):
                                    _a = 's'+ a
                                    _v = mDat.get(_a)
                                    if not mCtrl.isAttrConnected(_a) and _v:
                                        ATTR.set(str_short,_a,_v)
                                    else:
                                        log.debug("|{0}| >> connected scale: {1}".format(_str_func,_a))                    
                    
                    """
                    if not ATTR.is_locked(mCtrl.mNode,'scale'):
                        if sizeMethod == 'axisSize':
                            if _d.get('axisSize'):
                                try:
                                    DIST.scale_to_axisSize(_d['str'],_d['axisSize'])
                                except Exception,err:
                                    log.warning(cgmGEN.logString_msg(_str_func, "{0} | failed to axisSize {1}".format(_d['str'],err)))
                        elif sizeMethod in ['bb','bbSize']:
                            if _d.get('bbSize'):
                                try:
                                    reload(TRANS)
                                    TRANS.scale_to_boundingBox(_d['str'],_d['bbSize'],freeze=False)
                                except Exception,err:
                                    log.warning(cgmGEN.logString_msg(_str_func, "{0} | failed to axisSize {1}".format(_d['str'],err)))"""                    
                    
                    
                    
                    #Other...
                    
                    _pos = _d.get('pos')
                    _noParent = _d['noParent']
                    if _pos:
                        try:mCtrl.p_position = _pos
                        except:pass
                        
                    _orient = _d.get('orient')
                    if _orient:
                        mCtrl.p_orient = _orient

                    #_worldScale = _d.get('worldScale')
                    #if _worldScale and _noParent is not True:
                    #    mParent = mCtrl.p_parent
                    #    if mParent:
                    #        mCtrl.p_parent = False
                    #    mc.xform(mCtrl.mNode, scale = _worldScale, worldSpace = True, absolute = True)
                        
                    #    if mParent:mCtrl.p_parent = mParent
                    #else:

            if _state == datSet:
                break
            if ml_unmatched:
                log.warning(cgmGEN._str_subLine)
                log.info(cgmGEN.logString_msg(_str_func, "{0} | Unmatched...".format(datSet)))
                pprint.pprint(ml_unmatched)
                log.warning(cgmGEN._str_subLine)


            
        #rootShape_update(self)
        #pprint.pprint(vars())
        return True           
    finally:
        CGMUI.doEndMayaProgressBar()
        
@cgmGEN.Timer
def blockScale_bake(self,sizeMethod = 'axisSize',force=False,):
    """
    Bring a rigBlock to current settings - check attributes, reset baseDat
    """
    _str_func = 'bake_blockScale'
    log.debug(cgmGEN.logString_start(_str_func))
    str_self = self.mNode
    
    if self.p_parent:
        return log.error(cgmGEN.logString_msg(_str_func, "Can't bake parented blocks, please unparent"))
    
    _blockScale = self.blockScale
    
    if MATH.is_float_equivalent(_blockScale,1):
        log.debug(cgmGEN.logString_msg(_str_func, 'Already 1.0'))
        return True
    
    if self.hasAttr('baseSize'):
        _baseSize = True
        for a in 'xyz':
            if ATTR.is_connected(str_self,'baseSize'+a.capitalize()):
                _baseSize=False
                break
        if _baseSize:
            log.info(cgmGEN.logString_msg(_str_func, 'baseSize buffer. Not connected'))
            self.baseSize = baseSize_get(self)
                    
    _factor = 1.0/_blockScale
    
    ml_ctrls = controls_get(self, define=True, form=True, prerig=True)
    md_dat = {}
    
    log.debug(cgmGEN.logString_sub(_str_func, 'Gather Dat'))
    #First Loop gateher
    for i,mCtrl in enumerate(ml_ctrls):
        _str = mCtrl.p_nameShort
        _d = {'str':_str}
        
        if not ATTR.is_locked(_str,'translate'):
            _d['pos']=mCtrl.p_position
            
        _d['lossyScale'] = TRANS.scaleLossy_get(_str)
        _d['worldScale'] = mc.xform(_str, q=True, scale = True, worldSpace = True, absolute = True)
        _d['factorScale'] = [v*_factor for v in _d['worldScale']]
        
        _d['noParent'] = False
        if ATTR.is_locked(_str,'translate'):
            _d['noParent'] = True
        
        
        for a in ['sx','sy','sz']:
            if not ATTR.is_locked(_str,a):
                v = ATTR.get(_str,a)
                #if not MATH.is_float_equivalent(1.0,v):
                _d[a] = v * _blockScale
                if not _d.get('axisSize'):
                    _d['axisSize'] = DIST.get_axisSize(_str)
                if not _d.get('bbSize'):
                    _d['bbSize'] = TRANS.bbSize_get(_str)
                
        md_dat[i] = _d
        
    
    #pprint.pprint(md_dat)
    #return
    log.debug(cgmGEN.logString_msg(_str_func, 'Setting intiial'))
    ATTR.set(self.mNode,'blockScale',1.0)
    """
    blockDat_save(self)
    blockDat_load(self,redefine=True)                
    ml_ctrls = controls_get(self, define=True, form=True, prerig=True)        
    """
    
    for ii in range(3):#3 loop to account for parentage
        log.debug(cgmGEN.logString_sub(_str_func, 'Push: {0}'.format(ii)))

        for i,mCtrl in enumerate(ml_ctrls):
            _d = md_dat[i]
            log.debug(cgmGEN.logString_msg(_str_func, "{0} | {1}".format(_d['str'],_d)))
            _pos = _d.get('pos')
            _noParent = _d['noParent']
            
            if _pos:mCtrl.p_position = _pos
            
            
            _worldScale = _d.get('worldScale')
            if _worldScale and _noParent is not True:
                mParent = mCtrl.p_parent
                if mParent:
                    mCtrl.p_parent = False
                    
                #mc.xform(mCtrl.mNode, scale = _worldScale, objectSpace = True, absolute = True)
                mc.xform(mCtrl.mNode, scale = _worldScale, worldSpace = True, absolute = True)
                
                if mParent:mCtrl.p_parent = mParent
            else:
                if not ATTR.is_locked(mCtrl.mNode,'scale'):
                    """
                    _worldScale = _d.get('factorScale')
                    if _worldScale:
                        mc.xform(_str, scale = _worldScale, worldSpace = True, )#absolute = True
                        
                        for a in ['sx','sy','sz']:
                            if _d.get(a):
                                ATTR.set(_d['str'],a,_d[a])"""
                    
                    if sizeMethod == 'axisSize':
                        if _d.get('axisSize'):
                            try:
                                DIST.scale_to_axisSize(_d['str'],_d['axisSize'])
                            except Exception as err:
                                log.warning(cgmGEN.logString_msg(_str_func, "{0} | failed to axisSize {1}".format(_d['str'],err)))
                    elif sizeMethod in ['bb','bbSize']:
                        if _d.get('bbSize'):
                            try:
                                cgmGEN._reloadMod(TRANS)
                                TRANS.scale_to_boundingBox(_d['str'],_d['bbSize'],freeze=False)
                            except Exception as err:
                                log.warning(cgmGEN.logString_msg(_str_func, "{0} | failed to axisSize {1}".format(_d['str'],err)))
            """
            if ii == 0:
                _worldScale = _d.get('factorScale')
                if _worldScale:
                    mc.xform(_str, scale = _worldScale, worldSpace = True, )#absolute = True
                    
                    for a in ['sx','sy','sz']:
                        if _d.get(a):
                            ATTR.set(_d['str'],a,_d[a])
                    
                    if sizeMethod == 'axisSize':
                        if _d.get('axisSize'):
                            try:
                                DIST.scale_to_axisSize(_d['str'],_d['axisSize'])
                            except Exception,err:
                                log.warning(cgmGEN.logString_msg(_str_func, "{0} | failed to axisSize {1}".format(_d['str'],err)))
                    elif sizeMethod in ['bb','bbSize']:
                        if _d.get('bbSize'):
                            try:
                                reload(TRANS)
                                TRANS.scale_to_boundingBox(_d['str'],_d['bbSize'],freeze=False)
                            except Exception,err:
                                log.warning(cgmGEN.logString_msg(_str_func, "{0} | failed to axisSize {1}".format(_d['str'],err)))"""        
    #Fix the root shape
    #if not ATTR.is_connected(self.mNode,'baseSize'):
        #log.info(cgmGEN.logString_sub(_str_func, 'Base size buffer'))
        
    rootShape_update(self)
    #pprint.pprint(vars())
    return True   
 
        


def uiStatePickerMenu(self,parent = None):
    _short = self.p_nameShort
    ml_done = []
    #mc.setParent(parent)
    
    """
    mc.menuItem(en=True,divider = True,
                label = "Utilities")
    
    _sub = mc.menuItem(en=True,subMenu = True,tearOff=True,
                       label = "State Picker")"""

    _state = self.blockState
    #Define ----------------------------------------------------------------------------
    mUI.MelMenuItem(parent,
                    label = 'Root',
                    ann = 'select root',
                    c = cgmGEN.Callback(self.select),)
    ml_done.append(self)
    
    
    #Define .... --------------------------------------------------------
    d_define = []
    for k in ['start','end','rp','up','lever']:
        mHandle = self.getMessageAsMeta("define{0}Helper".format(k.capitalize()))
        if mHandle:
            if mHandle.v:
                if mHandle in ml_done:continue
                d = {'ann':'[{0}] Define {1} Helper'.format(_short,k),
                     'c':cgmGEN.Callback(mHandle.select),
                     'label':"{0} Helper".format(k)}
                d_define.append(d)
                ml_done.append(mHandle)
                
    ml_define  = self.msgList_get('defineHandles')#    
    for mHandle in ml_define:
        if mHandle.v:
            if mHandle in ml_done:continue
            k = mHandle.getMayaAttr('handleTag') or mHandle.p_nameBase
            d = {'ann':'[{0}] Define {1} Helper'.format(_short,k),
                 'c':cgmGEN.Callback(mHandle.select),
                 'label':"{0} Helper".format(k)}
            d_define.append(d)
            ml_done.append(mHandle)        
    
    
                
    if d_define:
        mUI.MelMenuItem(parent,en=True,divider = True, label = "Define")
        for d in d_define:
            mUI.MelMenuItem(parent,**d)
        
    #Form ------------------------------------------------------------------------------
    def addPivotHelper(mPivotHelper,i,l):
        _nameBase = mPivotHelper.p_nameBase
        d_form.append({'ann':' Pivot [{0}] [{1}]'.format(_nameBase,i),
                      'c':cgmGEN.Callback(mPivotHelper.select),
                      'label':' '*i + "{0} - [ {1} ]".format(_nameBase,i)})
        ml_done.append(mPivotHelper)
        
        mTopLoft = mPivotHelper.getMessageAsMeta('topLoft')
        if mTopLoft:
            d_form.append({'ann':'[{0}] Pivot Top [{1}]'.format(_short,i),
                          'c':cgmGEN.Callback(mTopLoft.select),
                          'label':' '*i + "Pivot Top - [ {0} ]".format(i)})            
        
    if _state:
        d_form = []
        
        for k in ['orientHelper']:
            mHandle = self.getMessageAsMeta("{0}".format(k))
            if mHandle:
                if mHandle in ml_done:continue                
                d_form.append({'ann':'[{0}] {1}'.format(_short,k),
                              'c':cgmGEN.Callback(mHandle.select),
                              'label':"{0}".format(k)})
                ml_done.append(mHandle)

        
        ml_handles = self.msgList_get('formHandles')
        ml_lofts = []
        if ml_handles:
            for i,mObj in enumerate(ml_handles):
                if mObj in ml_done:continue                                
                d_form.append({'ann':'[{0}] Form Handles [{1}]'.format(_short,i),
                              'c':cgmGEN.Callback(mObj.select),
                              'label':' '*i + "{0} | {1}".format(i,mObj.p_nameBase)})
                try:
                    mLoft = mObj.loftCurve
                except:mLoft = False
                if mLoft:
                    ml_lofts.append(mLoft)
                    
                ml_sub = mObj.msgList_get('subShapers')
                if ml_sub:
                    ml_lofts.extend(ml_sub)
                  
                mPivotHelper = mObj.getMessageAsMeta('pivotHelper')
                ml_done.append(mObj)
                if mPivotHelper:
                    addPivotHelper(mPivotHelper,i,d_form)
                    
        

        if d_form:
            mUI.MelMenuItem(parent,en=True,divider = True,
                        label = "Form")
            for d in d_form:
                mUI.MelMenuItem(parent,**d)                        
            
            if ml_lofts:
                mc.menuItem(en=False,divider = True,
                            label = "--- [Shapers]")
                for i,mSub in enumerate(ml_lofts):
                    mUI.MelMenuItem(parent,ann='[{0}] Loft Handles [{1}]'.format(mSub.mNode,i),
                                label=' '*i + "{0} | {1}".format(i,mSub.p_nameBase),
                                c=cgmGEN.Callback(mSub.select))

            
            #try:mc.setParent(parent)
            #except:pass            
    #Prerig ------------------------------------------------------------------------------
    if _state > 1:
        d_pre = []

        for k in ['cogHelper','scalePivotHelper']:
            mHandle = self.getMessageAsMeta("{0}".format(k))
            if mHandle:
                if mHandle in ml_done:continue                                                
                d_pre.append({'ann':'[{0}] {1}'.format(_short,k),
                              'c':cgmGEN.Callback(mHandle.select),
                              'label':"{0}".format(k)})
                ml_done.append(mHandle)
                
        
        ml_preHandles = self.msgList_get('prerigHandles')
        d_names = {}
        if ml_preHandles:
            for i,mObj in enumerate(ml_preHandles):
                if mObj in ml_done:continue                                                
                try:
                    _name = mObj.p_nameBase
                    #d_names[i] = _name
                    #_name = _name + ' ' + mObj.cgmType
                except:_name = "Pre handle - [ {0} ]".format(i)
                d_pre.append({'ann':'[{0}] prerig [{1}]'.format(_short,i),
                              'c':cgmGEN.Callback(mObj.select),
                              'label':' '*i + "{0} | {1}".format(i,_name)})
                ml_done.append(mObj)

        ml_jointHelpers = self.msgList_get('jointHelpers')
        if ml_jointHelpers:
            for i,mObj in enumerate(ml_jointHelpers):
                if mObj in ml_done:continue                                                
                try:_name = mObj.p_nameBase #"joint helper [{0}] ".format(d_names[i])
                except:_name = "joint helper - [ {0} ]".format(i)
                
                d_pre.append({'ann':'[{0}] Joint Helper [{1}]'.format(_short,i),
                              'c':cgmGEN.Callback(mObj.select),
                              'label':' '*i + "{0} | {1}".format(i,_name)})
                ml_done.append(mObj)
            
            #try:mc.setParent(parent)
            #except:pass
            
        if d_pre:
            mUI.MelMenuItem(parent,en=True,divider = True,
                        label = "Prerig")            
            for d in d_pre:
                mUI.MelMenuItem(parent,**d)
                
                

def get_handleScaleSpace(self,ml_objs = [], mBBHelper = None):
    """
    """
    _str_func = 'get_handleScaleSpace'
    log.debug(cgmGEN.logString_start(_str_func))
    str_self = self.mNode
    
    if not mBBHelper:
        mBBHelper = self.getMessageAsMeta('bbHelper')
        
    _sel = None
    if not ml_objs:
        _sel = mc.ls(sl=1)
        ml_objs = cgmMeta.validateObjListArg(_sel,'cgmObject')
        
    _res = {}
    for mObj in ml_objs:
        mLoc = mObj.doLoc()
        mLoc.p_parent = mBBHelper
        
        _t = mLoc.translate
        _l_v = []
        for i,v in enumerate(_t):
            if v:_l_v.append(2*v)
            else:_l_v.append(0)
            
        _tag = mObj.getMayaAttr('handleTag')
        if not _tag:
            _tag = mObj.p_nameBase.split('_')[0]
            
        _res[str(_tag)] = _l_v
        mLoc.delete()
    
    if _sel:
        mc.select(_sel)
    pprint.pprint(_res)
    return _res



def controller_walkChain(self,ml_chain,state='extra'):
    _str_func = 'controller_walkChain'
    if cgmGEN.__mayaVersion__ < 2018:
        log.info(cgmGEN.logString_msg(_str_func,'< 2018...>'))        
        
        return
    
    log.info(cgmGEN.logString_start(_str_func))
    ml_walked=[]
    mMainController = cgmMeta.controller_get(self)
    md_controllers = {}
    
    for mHandle in ml_chain:
        mController = mHandle.getMessageAsMeta('mController')
        if not mController:
            mController = cgmMeta.controller_get(mHandle)
        md_controllers[mHandle] = mController
        
    for i,mHandle in enumerate(ml_chain):
        try:
            
            if mHandle in ml_walked:
                continue
            
            mController =  md_controllers[mHandle]
            mController.cycleWalkSibling = 1
            mController.prepopulate = 1
            mController.parentprepopulate = 1
            
            if not i:
                mController.parent_set(mMainController,msgConnect=True)
            else:
                mController.parent_set(md_controllers[ml_chain[i-1]],msgConnect=False)
            ml_walked.append(mHandle)
            
            ATTR.multi_append(self.mNode, '{0}Stuff'.format(state), mController.mNode)
        except Exception as err:
            log.error("{0} | {1} | {2} | {3}".format(i,mController.mNode,type(mController),err))
        
        
def controller_wireHandles(self,ml_handles,state='extra'):
    _str_func = 'controller_wireHandles'
    if cgmGEN.__mayaVersion__ < 2018:
        log.info(cgmGEN.logString_msg(_str_func,'< 2018...>'))        
        return
    
    log.info(cgmGEN.logString_start(_str_func))
    
    if not state:
        _state = self.getEnumValueString('blockState') 
    if not ml_handles:
        return
    
    ml_handles = VALID.listArg(ml_handles)
    
    
    ml_done = []
    ml_walked = []
    md_controllers = {}
    ml_controllers = []

    mMainController = cgmMeta.controller_get(self)
    
    
    for mHandle in ml_handles:
        if mHandle in ml_done:
            continue
        if not mHandle:
            continue
        mLoft = mHandle.getMessageAsMeta('loftCurve')
        if mLoft:
            mController = cgmMeta.controller_get(mLoft)
            #mController.visibilityMode = 2
            ml_done.append(mController)
            md_controllers[mLoft] = mController
            ml_controllers.append(mController)
            
        mController = cgmMeta.controller_get(mHandle,True)
        #mController.visibilityMode = 2                            
        ml_done.append(mHandle)
        md_controllers[mHandle] = mController
        ml_controllers.append(mController)
        
    """    
    for i,mTag in enumerate(ml_controllers):
        if mTag in ml_walked:
            continue
        
        #mController =  md_controllers[mHandle]
        mTag.cycleWalkSibling = 1
        mTag.prepopulate = 1
        mTag.parentprepopulate = 1
        
        if not i:
            mTag.parent_set(mMainController,msgConnect=True)
        else:
            mTag.parent_set(ml_controllers[i-1],msgConnect=False)
        ml_walked.append(mTag)    
    """

    """
    for mSet in ml_handles:
        for i,mHandle in enumerate(mSet):
            if mHandle not in ml_done:
                continue
            
            mController =  md_controllers[mHandle]
            if not i:
                mController.parent_set(mMainController,msgConnect=True)
            else:
                mController.parent_set(md_controllers[mSet[i-1]],msgConnect=False)
                
            ml_done.append(mController)"""
    
    for mObj in ml_controllers + [mMainController]:
        mObj.cycleWalkSibling = 1
        mObj.prepopulate = 1
        mObj.parentprepopulate = 1
        
        if not ATTR.get_driver(mObj.mNode, 'visibilityMode') and not ATTR.is_locked(mObj.mNode,
                                                                                    'visibilityMode'):
            try:
                ATTR.connect("{0}.visProximityMode".format(self.mNode),
                             "{0}.visibilityMode".format(mObj.mNode))    
            except Exception as err:
                log.error(err)
        ATTR.multi_append(self.mNode, '{0}Stuff'.format(state), mObj.mNode)
        
        
def form_templateMesh(self,arg=None):
    mLoftMesh = self.getMessageAsMeta('prerigLoftMesh')
    if not mLoftMesh:
        return False
    
    mLoftMesh.template = arg
    
def mesh_skinable(self):
    mModuleTarget = self.getMessage('moduleTarget',asMeta=True)
    if not mModuleTarget:
        return log.error("|{0}| >> Must have moduleTarget for skining mode".format(_str_func))
    mModuleTarget = mModuleTarget[0]
    ml_moduleJoints = mModuleTarget.rigNull.msgList_get('moduleJoints')
    if not ml_moduleJoints:
        return log.error("|{0}| >> Must have moduleJoints for skining mode".format(_str_func))        
    return True