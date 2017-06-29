"""
------------------------------------------
RigBlocks: cgm.core.mrs
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
import maya.cmds as mc

import random
import re
import copy
import time
import os
import cPickle as pickle

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as PUPPETMETA

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
from cgm.core.mrs.lib import shared_dat as BLOCKSHARED
from cgm.core.mrs.lib import general_utils as BLOCKGEN
from cgm.core.mrs.lib import builder_utils as BUILDERUTILS

from cgm.core.lib import nameTools
reload(BLOCKSHARED)

get_from_scene = BUILDERUTILS.get_from_scene

#from cgm.core.lib import nameTools
#from cgm.core.rigger import ModuleFactory as mFactory
#from cgm.core.rigger import PuppetFactory as pFactory
#from cgm.core.classes import NodeFactory as nodeF

#from cgm.core.mrs.blocks import box

#_d_blockTypes = {'box':box}

#====================================================================================	
# Rig Block Meta
#====================================================================================	
d_attrstoMake = {'version':'string',#Attributes to be initialzed for any module
                 'blockType':'string',
                 #'moduleTarget':'messageSimple',
                 'attachPoint':'base:end:closest:surface',                                    
                 'baseSize':'float',
                 'blockState':'string',
                 'blockDat':'string',#...for pickle? 
                 'blockParent':'messageSimple',
                 'blockMirror':'messageSimple'}
d_defaultAttrSettings = {'blockState':'define',
                         'baseSize':1.0}

class cgmRigBlock(cgmMeta.cgmControl):
    #These lists should be set up per rigblock as a way to get controls from message links
    _l_controlLinks = []
    _l_controlmsgLists = []

    def __init__(self, node = None, blockType = None, *args,**kws):
        """ 
        The root of the idea of cgmRigBlock is to be a sizing mechanism and build options for
        our modular rigger.

        Args:
        node = existing module in scene
        name = treated as a base name

        """
        _str_func = "cgmRigBlock.__init__"   
        
        if node is None and blockType is None:
            raise ValueError,"|{0}| >> Must have either a node or a blockType specified.".format(_str_func)
        
        if blockType and not is_buildable(blockType):
            log.warning("|{0}| >> Unbuildable blockType specified".format(_str_func))
            
        #>>Verify or Initialize
        super(cgmRigBlock, self).__init__(node = node, name = blockType) 
        self._blockModule = get_blockModule(blockType or self.blockType)        
        
        #====================================================================================	
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            log.debug('CACHE : Aborting __init__ on pre-cached {0} Object'.format(self))
            return
        #====================================================================================	

        #====================================================================================
        #Keywords - need to set after the super call
        #==============         
        _doVerify = kws.get('doVerify',False) or False
        self._factory = factory(self.mNode)
        self._callKWS = kws
        #self.UNMANAGED.extend(['kw_name','kw_moduleParent','kw_forceNew','kw_initializeOnly','kw_callNameTags'])	

        #>>> Initialization Procedure ================== 
        if self.__justCreatedState__ or _doVerify:
            log.debug("|{0}| >> Just created or do verify...".format(_str_func))            
            if self.isReferenced():
                log.error("|{0}| >> Cannot verify referenced nodes".format(_str_func))
                return
            elif not self.verify(blockType):
                raise RuntimeError,"|{0}| >> Failed to verify: {1}".format(_str_func,self.mNode)
            
            #>>>Auto flags...
            _blockModule = get_blockModule(self.blockType)
            if _blockModule.__dict__.get('__autoTemplate__'):
                log.info("|{0}| >> AutoTemplate...".format(_str_func))  
                try:
                    self.p_blockState = 'template'
                except Exception,err:
                    for arg in err.args:
                        log.error(arg)  
                        
    def verify(self, blockType = None, size = None):
        """ 

        """
        _str_func = '[{0}] verify'.format(self.p_nameShort)
        
        if size == None:
            size = self._callKWS.get('size')
            
        _start = time.clock()

        if self.isReferenced():
            raise StandardError,"|{0}| >> Cannot verify referenced nodes".format(_str_func)
        
        #if blockType and not is_blockType_valid(blockType):
            #raise ValueError,"|{0}| >> Invalid blocktype specified".format(_str_func)
        
        _type = self.getMayaAttr('blockType')
        if blockType is not None and _type is not None and _type != blockType:
            raise ValueError,"|{0}| >> Conversion necessary. blockType arg: {1} | found: {2}".format(_str_func,blockType,_type)
        
        _mBlockModule = get_blockModule(blockType)
        
        if not _mBlockModule:
            log.error("|{0}| >> [{1}] | Failed to query type. Probably not a module".format(_str_func,blockType))        
            return False
                
        #if 'build_rigBlock' not in _module.__dict__.keys():
            #log.error("|{0}| >> [{1}] | Failed to query create function.".format(_str_func,blockType))        
            #return False
        
        #>>> Attributes --------------------------------------------------------------------------------
        self._factory.verify(blockType)    
        
        #>>> Base shapes --------------------------------------------------------------------------------
        if size:
            self.baseSize = size
            
        _mBlockModule = get_blockModule(self.blockType)
        if 'define' in _mBlockModule.__dict__.keys():
            log.info("|{0}| >> BlockModule define call found...".format(_str_func))            
            _mBlockModule.define(self)      
        
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))         
        return True
        

    def doName(self, *a, **kws):
        """
        Override to handle difference with rig block

        """
        _short = self.p_nameShort
        _str_func = '[{0}] doName'.format(_short)

        #Get Raw name
        _d = nameTools.returnObjectGeneratedNameDict(_short)

        for a in 'puppetName','baseName':
            if self.hasAttr(a):
                _d['cgmName'] = ATTR.get(_short,a)

        _d['cgmTypeModifier'] = ATTR.get(_short,'blockType')
        _d['cgmType'] = 'block'
        
        if self.getMayaAttr('position'):
            _d['cgmPosition'] = self.getEnumValueString('position')
        if self.getMayaAttr('direction'):
            _d['cgmDirection'] = self.getEnumValueString('direction')

        #Check for special attributes to replace data, name
        self.rename(nameTools.returnCombinedNameFromDict(_d))

    def getControls(self, asMeta = False):
        """
        Function which MUST be overloaded
        """	
        #>>> Gather basic info for module build
        _str_func = " get_controls >> "
        if asMeta:
            _result = [self]
        else:
            _result = [self.mNode]
            
        for plug in self.__class__._l_controlLinks:
            if asMeta:
                _buffer = self.getMessageAsMeta(plug)
                if _buffer:
                    _result.append(_buffer)
            else:
                _buffer = self.getMessage(plug)
                if _buffer:
                    _result.extend(_buffer)
                else:
                    log.error("{2} Failed to find message on: {0}.{1}".format(self.p_nameShort,plug,_str_func))
        if not self.__class__._l_controlmsgLists:
            log.debug("{0} No msgList attrs registered".format(_str_func))
        else:
            for plug in self.__class__._l_controlmsgLists:
                _buffer = self.msgList_get(plug, asMeta = asMeta)
                if _buffer:
                    _result.extend(_buffer)
                else:
                    log.error("{2} Failed to find msgList on: {0}.{1}".format(self.p_nameShort,plug,_str_func))	    
        return _result
    
    #========================================================================================================     
    #>>> Heirarchy 
    #========================================================================================================      
    def getBlockRoot(self,asMeta = True):
        _mParent = self.getBlockParent(asMeta)
        while _mParent:
            _mCheck = _mParent.getBlockParent(asMeta)
            if not _mCheck:
                return _mParent
            else:_mParent = _mCheck
        
        if not asMeta:
            return _mParent.mNode
        return _mParent
        """
        self.getParentMetaNode(mType = 'cgmRigBlock')
        objs = [GetNodeType(x) for x in self.fullPath.split('|')[:-1]]
        rootBlock = self
    
        for obj in objs:
            if not obj:
                continue
            if( mc.objExists(obj.GetAttrString("bp_block")) ):
                rootBlock = Block.LoadRigBlock( obj )
                break
    
        return rootBlock """
    p_blockRoot = property(getBlockRoot)
    
    def getBlockParent(self,asMeta=True):
        _str_func = 'getBlockParent'
        _res = False
        
        _mBlockParent = self.getMessage('blockParent',asMeta = True)
        if _mBlockParent:
            _res = _mBlockParent
        
        for mParent in self.getParents(asMeta=True):
            if issubclass(type(mParent), cgmRigBlock):
                _res = mParent
        if _res and not asMeta:
            return _res.mNode
        return _res

    def setBlockParent(self, parent = False, attachPoint = None):        
        _str_func = 'setBlockParent'
        if not parent:
            self.blockParent = False
            self.p_parent = False
        
        else:
            self.connectParentNode(parent, 'blockParent')
            if attachPoint:
                self.p_parent = attachPoint
            else:
                self.p_parent = parent
            
    p_blockParent = property(getBlockParent,setBlockParent)
    
    def getBlockChildren(self,asMeta=True):
        _str_func = 'getBlockChildren'
        ml_nodeChildren = self.getChildMetaNodes(mType = ['cgmRigBlock'])
        ml_children = self.getChildren(asMeta = True)
        
        for mChild in ml_children:
            if mChild not in ml_nodeChildren and issubclass(type(mChild),cgmRigBlock):
                log.info("|{0}| >> Found as reg child: {1}".format(_str_func,mChild.mNode))        
                ml_nodeChildren.append(mChild)
        
        if not asMeta:
            return [mChild.mNode for mChild in ml_nodeChildren]
        return ml_nodeChildren
    
    p_blockChildren = property(getBlockChildren)

  
    
    #========================================================================================================     
    #>>> Info 
    #========================================================================================================      
    def getBlockAttributes(self):
        """
        keyable and unlocked attributes
        """
        _res = []
        _short = self.mNode
        for attr in self.getAttrs(ud=True):
            if ATTR.is_keyable(_short,attr):#and not ATTR.is_locked(_short,attr)
                _res.append(attr)
        return _res
    p_blockAttributes = property(getBlockAttributes)
    
    def getBlockDat(self):
        """
        Carry from Bokser stuff...
        """
        _l_udMask = ['blockDat','attributeAliasList','blockState','mClass','mClassGrp','mNodeID','version']
        _ml_controls = self.getControls(True)
        _short = self.p_nameShort
        #Trying to keep un assertable data out that won't match between two otherwise matching RigBlocks
        _d = {#"name":_short, 
              "blockType":self.blockType,
              "blockState":self.p_blockState,
              "baseName":self.getMayaAttr('puppetName') or self.getMayaAttr('baseName'), 
              #"part":self.part,
              ##"blockPosition":self.getEnumValueString('position'),
              ##"blockDirection":self.getEnumValueString('direction'),
              "size":DIST.get_size_byShapes(self),
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
        
        for a in self.getAttrs(ud=True):
            if a not in _l_udMask:
                if ATTR.get_type(_short,'enum'):
                    _d['ud'][a] = ATTR.get_enumValueString(_short,a)                    
                else:
                    _d['ud'][a] = ATTR.get(_short,a)
        
        cgmGEN.log_info_dict(_d,'[{0}] blockDat'.format(self.p_nameShort))
        return _d
        
    def saveBlockDat(self):
        self.blockDat = self.getBlockDat()
        
    def loadBlockDat(self,blockDat = None):
        _short = self.p_nameShort        
        _str_func = '[{0}] loadBlockDat'.format(_short)
        
        if blockDat is None:
            log.info("|{0}| >> No blockDat passed. Checking self...".format(_str_func))    
            blockDat = self.blockDat
            
        if not issubclass(type(blockDat),dict):
            raise ValueError,"|{0}| >> blockDat must be dict. type: {1} | blockDat: {2}".format(_str_func,type(blockDat),blockDat) 
        
        _blockType = blockDat.get('blockType')
        if _blockType != self.blockType:
            raise ValueError,"|{0}| >> blockTypes don't match. self: {1} | blockDat: {2}".format(_str_func,self.blockType,_blockType) 
        
        #.>>>..UD ----------------------------------------------------------------------------------------------------
        log.info("|{0}| >> ud...".format(_str_func)+ '-'*80)
        _ud = blockDat.get('ud')
        if not blockDat.get('ud'):
            raise ValueError,"|{0}| >> No ud data found".format(_str_func) 
        for a,v in _ud.iteritems():
            _current = ATTR.get(_short,a)
            if _current != v:
                try:
                    if ATTR.get_type(_short,a) in ['message']:
                        log.info("|{0}| >> userDefined '{1}' skipped. Not loading message data".format(_str_func,a))                     
                    else:
                        log.info("|{0}| >> userDefined '{1}' mismatch. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                        ATTR.set(_short,a,v)
                except Exception,err:
                    log.error("|{0}| >> userDefined '{1}' failed to change. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                    r9Meta.printMetaCacheRegistry()                
                    for arg in err.args:
                        log.error(arg)                      

        #>>State ----------------------------------------------------------------------------------------------------
        log.info("|{0}| >> State".format(_str_func) + '-'*80)
        _state = blockDat.get('blockState')
        _current = self.getState()
        if _state != _current:
            log.info("|{0}| >> States don't match. self: {1} | blockDat: {2}".format(_str_func,_current,_state)) 
            self.p_blockState = _state
            
        #>>Controls ----------------------------------------------------------------------------------------------------
        log.info("|{0}| >> Controls".format(_str_func)+ '-'*80)
        _pos = blockDat.get('positions')
        _orients = blockDat.get('orientations')
        _scale = blockDat.get('scale')
        
        _ml_controls = self.getControls(True)
        if len(_ml_controls) != len(_pos):
            log.error("|{0}| >> Control dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( _ml_controls),len(_pos))) 
        else:
            log.info("|{0}| >> loading Controls...".format(_str_func))
            for i,mObj in enumerate(_ml_controls):
                mObj.p_position = _pos[i]
                mObj.p_orient = _orients[i]
                for ii,v in enumerate(_scale[i]):
                    _a = 's'+'xyz'[ii]
                    if not self.isAttrConnected(_a):
                        ATTR.set(_short,_a,v)

        #>>Generators ----------------------------------------------------------------------------------------------------
        log.info("|{0}| >> Generators".format(_str_func)+ '-'*80)
        _d = {"isSkeletonized":[self.isSkeletonized,self.doSkeletonize,self.skeletonDelete]}
        
        for k,calls in _d.iteritems():
            _block = bool(blockDat.get(k))
            _current = calls[0]()
            if _state != _current:
                log.info("|{0}| >> {1} States don't match. self: {2} | blockDat: {3}".format(_str_func,k,_current,_block)) 
                if _block == False:
                    calls[2]()                         
                else:
                    calls[1]()     
                
                
                
        return True
    p_blockDat = property(getBlockDat,loadBlockDat)

    
    #========================================================================================================     
    #>>> States 
    #========================================================================================================      
    def rebuild(self,*args,**kws):
        return self._factory.rebuild_rigBlock(*args,**kws)
    
    def getState(self, asString = True):
        _str_func = '[{0}] getState'.format(self.p_nameShort)
        #if asString:
        #    return self.blockState
        #return BLOCKSHARED._l_blockStates.index(self.blockState)
        _blockModule = get_blockModule(self.blockType)
        _goodState = False
        _l_blockStates = BLOCKSHARED._l_blockStates
        
        _state = self.blockState
        if _state not in BLOCKSHARED._l_blockStates:
            log.info("|{0}| >> Failed a previous change: {1}. Reverting to previous".format(_str_func,_state))                    
            _state = _state.split('>')[0]
            self.blockState = _state
            self.changeState(_state),#rebuild=True)
        
        if _state == 'define':
            _goodState = 'define'
        else:
            if _blockModule.__dict__['is_{0}'.format(_state)](self):
                log.info("|{0}| >> blockModule test...".format(_str_func))                    
                _goodState = _state
            else:
                _idx = _l_blockStates.index(_state) - 1
                log.info("|{0}| >> blockModule test failed. Testing: {1}".format(_str_func, _l_blockStates[_idx]))                
                while _idx > 0 and not _blockModule.__dict__['is_{0}'.format(_l_blockStates[_idx])](self):
                    log.info("|{0}| >> Failed {1}. Going down".format(_str_func,_l_blockStates[_idx]))
                    _blockModule.__dict__['{0}Delete'.format(_l_blockStates[_idx])](self)
                    #self.changeState(_l_blockStates[_idx])
                    _idx -= 1
                _goodState = _l_blockStates[_idx]
                    
                
        if _goodState != self.blockState:
            log.info("|{0}| >> Passed: {1}. Changing buffer state".format(_str_func,_goodState))                    
            self.blockState = _goodState
            
        if asString:
            return _goodState
        return _l_blockStates.index(_goodState)
    

    def changeState(self, state = None, children = True):
        return self._factory.changeState(state)    
    p_blockState = property(getState,changeState)
    
    
    
    #========================================================================================================     
    #>>> Skeleton and Mesh generation 
    #========================================================================================================      
    def isSkeletonized(self):
        _str_func = '[{0}] isSkeletonized'.format(self.p_nameShort)
        
        _blockModule = get_blockModule(self.blockType)
        
        _call = _blockModule.__dict__.get('is_skeletonized',False)
        if _call:
            log.info("|{0}| >> blockModule check...".format(_str_func))                                
            return _call(self)
        return False
    
    def doSkeletonize(self):
        _str_func = '[{0}] doSkeletonize'.format(self.p_nameShort)
        
        _blockModule = get_blockModule(self.blockType)
                
        _call = _blockModule.__dict__.get('skeletonize',False)
        if _call:
            log.info("|{0}| >> blockModule check...".format(_str_func))                                
            return _call(self)
        return False
    
    def skeletonDelete(self):
        _str_func = '[{0}] deleteSkeleton'.format(self.p_nameShort)
        
        _blockModule = get_blockModule(self.blockType)
                
        _call = _blockModule.__dict__.get('skeletonDelete',False)
        if _call:
            log.info("|{0}| >> blockModule check...".format(_str_func))                                
            return _call(self)
        
        return True    


    #========================================================================================================     
    #>>> Mirror 
    #========================================================================================================      
       


#====================================================================================	
# Factory
#====================================================================================	
class factory(object):
    _l_controlLinks = []
    _l_controlmsgLists = []	

    def __init__(self, root = None, blockType = None, *a,**kws):
        """
        Core rig block factory. Runs processes for rig blocks.

        :parameters:
            root(str) | root object to check for wiring

        :returns
            factory instance
        """
        _str_func = 'factory._init_'

        if a:log.debug("|{0}| >> a: {1}".format(_str_func,a))
        if kws:
            self._call_kws = kws
            cgmGEN.log_info_dict(kws,_str_func)
            #log.debug("|{0}| >> kws: {1}".format(_str_func,kws))

        self._mi_block = None

        #_verify = kws.get('verify',False)
        #log.debug("|{0}| >> verify: {1}".format(_str_func,_verify))
        
        if root is not None:
            self.set_rigBlock(root)
            
        if blockType is not None:
            self.create_rigBlock(blockType)

    def __repr__(self):
        try:return "{0}(root: {1})".format(self.__class__, self._mi_block)
        except:return self

    def create_rigBlock(self, blockType = None, size = 1, blockParent = None):
        _str_func = 'create_rigBlock'
        _start = time.clock()
        """
        _d = get_modules_dict()
        
        if blockType not in _d.keys():
            log.error("|{0}| >> [{1}] | Failed to query type. Probably not a module".format(_str_func,blockType))        
            return False
        
        _module = _d[blockType]
        
        if 'build_rigBlock' not in _module.__dict__.keys():
            log.error("|{0}| >> [{1}] | Failed to query create function.".format(_str_func,blockType))        
            return False"""
        
        _mObj = cgmRigBlock(blockType=blockType)
        #_module.build_rigBlock(_mObj,size = size)
        
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start))) 
        
        #self.set_rigBlock(_mObj)
        #self.verify(blockType)
        return _mObj

    #========================================================================================================     
    #>>> Queries 
    #========================================================================================================  
    def get_attrCreateDict(self,blockType = None):
        """
        Data checker to see the create attr dict for a given blockType regardless of what's loaded

        :parameters:
            blockType(str) | rigBlock type

        :returns
            dict
        """
        _str_func = 'get_attrCreateDict'

        _mod = get_modules_dict().get(blockType,False)
        if not _mod:
            log.warning("|{0}| >> No module found for: {1}".format(_str_func,blockType))
            return False

        
        try:d_attrsFromModule = _mod.d_attrsToMake
        except:d_attrsFromModule = {}
        
        d_defaultSettings = copy.copy(d_defaultAttrSettings)
        
        try:d_defaultSettings.update(_mod.d_defaultSettings)
        except:pass

        try:_l_msgLinks = _mod._l_controlLinks
        except:_l_msgLinks = []
        
        _d = copy.copy(d_attrstoMake)     
        
        _l_standard = _mod.__dict__.get('l_attrsStandard',[])
        log.info("|{0}| >> standard: {1} ".format(_str_func,_l_standard))                        
        for k in _l_standard:
            if k in BLOCKSHARED._d_attrsTo_make.keys():
                _d[k] = BLOCKSHARED._d_attrsTo_make[k]
        
        for k,v in d_attrsFromModule.iteritems():
            if k in _d.keys():
                log.warning("|{0}| >> key: {1} already in to create list of attributes from default. | blockType: {2}".format(_str_func,k,blockType))                
            else:
                _d[k] = v

        if _l_msgLinks:
            for l in _l_msgLinks:
                _d[l] = 'messageSimple'

        cgmGEN.log_info_dict(_d,_str_func + " '{0}' attributes to create".format(blockType))
        cgmGEN.log_info_dict(d_defaultSettings,_str_func + " '{0}' defaults".format(blockType))

        self._d_attrsToVerify = _d
        self._d_attrToVerifyDefaults = d_defaultSettings

        #for k in _d.keys():
            #print k

        return True
    
    def is_valid(self,obj= None):
        """
        Data checker to see the skeleton create dict for a given blockType regardless of what's loaded

        :parameters:
            obj(str) | 
            blockType(str) | rigBlock type

        :returns
            dict
        """
        _str_func = 'is_valid'
        
        if not obj:
            raise ValueError,"|{0}| >> no obj provided".format(_str_func)
        
        _mObj = cgmMeta.cgmNode(obj)
        log.debug("|{0}| >> obj: {1}".format(_str_func,obj))        
        
        try:_blockType = _mObj.blockType
        except Exception,err:
            raise Exception,"blockType attr not detected or failed. err: {0}".format(err)
        log.debug("|{0}| >> blockType: {1}".format(_str_func,_blockType))        

        _mod = _d_blockTypes.get(_blockType,False)
        if not _mod:
            log.debug("|{0}| >> No module found for: {1}".format(_str_func,_blockType))
            return False   
        
        #>> Module is valid call ---------------------------------------------------------------
        log.debug("|{0}| >> Module is_valid?".format(_str_func))        
        _MOD_is_valid = None
        try:_MOD_is_valid = _mod.is_valid
        except:pass
        
        if _MOD_is_valid:
            log.debug("|{0}| >> Module is_valid call found. Attempting...".format(_str_func))   
            _MOD_is_valid(obj)
            #try:_MOD_is_valid(obj)
            #except Exception,err:
             #   raise Exception,"|{0}| >> Module is_valid call fail || err: {1} ".format(_str_func,err)
                
        
        #>> Standard attrs... ---------------------------------------------------------------
        log.debug("|{0}| >> Standard attrs...".format(_str_func))                
        _l_missing = []
        self.get_attrCreateDict(_blockType)
        if not self._d_attrsToVerify:
            raise ValueError,"|{0}| >> Failed to get attr create dict".format(_str_func)            
        for a in self._d_attrsToVerify.keys():
            if not _mObj.hasAttr(a):
                _l_missing.append(a)
        if _l_missing:
            raise ValueError,"|{0}| >> Missing the following attributes: {1}".format(_str_func,_l_missing)
        
        
        #>> Messages -------------------------------------------------------------------------
        log.debug("|{0}| >> Message/MsgLists...".format(_str_func))                        
        _l_controlLinks = _mod.__dict__.get('_l_controlLinks',[])
        _l_controlmsgLists = _mod.__dict__.get('_l_controlmsgLists',[])
        
        _l_missingLink = []
        _l_missingMsgLists = []
        
        for m in _l_controlLinks:
            if not ATTR.get_message(_mObj.mNode,m):
                _l_missingLink.append(m)
        for m in _l_controlmsgLists:
            if not ATTR.msgList_get(_mObj.mNode, m):
                _l_missingMsgLists.append(m)
                
        if _l_missingLink or _l_missingMsgLists:
            if _l_missingLink:
                log.warning("|{0}| >> Following links missing...".format(_str_func))          
                
                for m in _l_missingLink:
                    log.warning("|{0}| >> {1}".format(_str_func,m))          
            if _l_missingMsgLists:
                log.warning("|{0}| >> Following msgLists missing...".format(_str_func))          
                
                for m in _l_missingMsgLists:
                    log.warning("|{0}| >> {1}".format(_str_func,m))  
            raise ValueError,"|{0}| >> See missing links above...".format(_str_func,_l_missing)
        
        return True
            
    def get_infoBlock_report(self):
        """
        Get a report of data 

        :returns
            list
        """
        _str_func = 'get_infoBlock_report'
        
        if self._mi_block is None:
            raise ValueError,"|{0}| >> No root loaded.".format(_str_func) 
        
        _d = get_modules_dict()   
        _blockType = self._mi_block.blockType
        if _blockType not in _d.keys():
            log.error("|{0}| >> [{1}] | Failed to query type. Probably not a module".format(_str_func,_blockType))        
            return False        

        _mod = _d.get(_blockType,False)
        
        _short = self._mi_block.p_nameShort
        
        _res = []
        
        _res.append("{0} : {1}".format('blockType',_blockType))
        _res.append("{0} : {1}".format('blockState',ATTR.get(_short,'blockState')))
        
        _res.append("version: {0} | moduleVersion: {1}".format(ATTR.get(_short,'version'),_mod.__version__))
        
        for a in 'direction','position':
            if ATTR.get(_short,a):
                _res.append("{0} : {1}".format(a,ATTR.get_enumValueString(_short,a)))
        
        for msg in 'blockMirror','moduleTarget':
            _res.append("{0} : {1}".format(msg,ATTR.get(_short,msg)))  
            
        #Msg checks        
        #for link in  
        #Module data
                
        return _res
    
        
    def get_skeletonCreateDict(self,blockType = None):
        """
        Data checker to see the skeleton create dict for a given blockType regardless of what's loaded

        :parameters:
            blockType(str) | rigBlock type

        :returns
            dict
        """
        _str_func = 'get_skeletonCreateDict'

        _mod = get_blockModule(blockType)
        if not _mod:
            log.warning("|{0}| >> No module found for: {1}".format(_str_func,blockType))
            return False       

        if self._mi_block is None:
            raise ValueError,"|{0}| >> No root loaded.".format(_str_func)

        _root = self._mi_block.mNode

        #Validate mode data -------------------------------------------------------------------------
        try:_d_skeletonSetup = _mod.d_skeletonSetup
        except:_d_skeletonSetup = {}

        _mode = _d_skeletonSetup.get('mode',False)
        _targetsMode = _d_skeletonSetup.get('targetsMode','msgList')
        _targetsCall = _d_skeletonSetup.get('targets',False)
        _l_targets = []

        log.debug("|{0}| >> mode: {1} | targetsMode: {2} | targetsCall: {3}".format(_str_func,_mode,_targetsMode,_targetsCall))

        #...get our targets
        if _targetsMode == 'msgList':
            _l_targets = ATTR.msgList_get(_root, _targetsCall)
        else:
            raise ValueError,"targetsMode: {0} is not implemented".format(_targetsMode)

        log.debug("|{0}| >> Targets: {1}".format(_str_func,_l_targets))            

        _helperOrient = ATTR.get_message(_root,'helperOrient')
        if not _helperOrient:
            log.debug("|{0}| >> No helper orient. Using root.".format(_str_func))   
            _axisWorldUp = MATH.get_obj_vector(_root,'y+')                 
        else:
            log.debug("|{0}| >> helperOrient: {1}".format(_str_func,_helperOrient))            
            _axisWorldUp = MATH.get_obj_vector(_helperOrient[0],'y+') 
        log.debug("|{0}| >> axisWorldUp: {1}".format(_str_func,_axisWorldUp))  

        _joints = ATTR.get(_root,'joints')


        #...get our positional data
        if _mode == 'vectorCast':
            _p_start = POS.get(_l_targets[0])
            _p_top = POS.get(_l_targets[1])    
            _l_pos = get_posList_fromStartEnd(_p_start,_p_top,_joints)   

        else:
            raise ValueError,"mode: {0} is not implemented".format(_mode)                

        _d_res = {'positions':_l_pos,
                  'jointCount':_joints,
                  'helpers':{'orient':_helperOrient,
                             'targets':_l_targets},
                  'worldUpAxis':_axisWorldUp}
        cgmGEN.log_info_dict(_d_res,_str_func)
        return _d_res

    def verify(self, blockType = None):
        """
        Verify a given loaded root object as a given blockType

        :parameters:
            blockType(str) | rigBlock type

        :returns
            success(bool)
        """        

        if self._mi_block is None:
            raise ValueError,"No root loaded."

        _mBlock = self._mi_block
        _str_func = '[{0}] factory.verify'.format(_mBlock.p_nameShort)

        if _mBlock.isReferenced():
            raise ValueError,"Referenced node. Cannot verify"
        
        if blockType == None:
            blockType = ATTR.get(_mBlock.mNode,'blockType')
        if not blockType:
            raise ValueError,"No blockType specified or found."

        if not self.get_attrCreateDict(blockType):
            raise ValueError, "|{0}| >> Failed to get attr dict. blockType:{1}".format(_str_func,blockType)

        #Need to get the type, the get the attribute lists and data from the module

        #_mBlock.verifyAttrDict(self._d_attrsToVerify,keyable = False, hidden = False)
        #_mBlock.verifyAttrDict(self._d_attrsToVerify)
        
        _keys = self._d_attrsToVerify.keys()
        _keys.sort()
        #for a,t in self._d_attrsToVerify.iteritems():
        for a in _keys:
            v = self._d_attrToVerifyDefaults.get(a,None)
            t = self._d_attrsToVerify[a]
            
            log.info("|{0}| Setting attr >> '{1}' | defaultValue: {2} ".format(_str_func,a,v,blockType)) 
            
            if ':' in t:
                _mBlock.addAttr(a,initialValue = v, attrType = 'enum', enumName= t, keyable = False)		    
            else:
                if t == 'string':
                    _l = True
                else:_l = False
                _mBlock.addAttr(a,initialValue = v, attrType = t,lock=_l, keyable = False)            

        _mBlock.addAttr('blockType', value = blockType,lock=True)	
        #_mBlock.blockState = 'base'
        
        _mBlock.doName()

        return True
    #========================================================================================================     
    #>>> States 
    #========================================================================================================  
    
    def changeState(self, state = None, rebuildFrom = None, forceNew = False):
        """
        Change the state of a loaded rigBlock
        
        :parameters:
            state(str) | state to change to

        :returns
            success(bool)
        """        

        if self._mi_block is None:
            raise ValueError,"No root loaded."

        _mBlock = self._mi_block

        if _mBlock.isReferenced():
            raise ValueError,"Referenced node. Cannot verify"
        
        _str_func = '[{0}] factory.changeState'.format(_mBlock.p_nameBase)
        
        #>Validate our data ------------------------------------------------------
        d_upStateFunctions = {'template':self.template,
                              'prerig':self.prerig,
                              'rig':self.rig,
                              }
        d_downStateFunctions = {'define':self.templateDelete,#deleteSizeInfo,
                                'template':self.prerigDelete,#deleteSkeleton,
                                'prerig':self.rigDelete,#rigDelete,
                                }
        d_deleteStateFunctions = {'define':False,#deleteSizeInfo,
                                  'template':False,#deleteTemplate,#handle from factory now
                                  'prerig':False,#deleteSkeleton,
                                  'rig':False,#rigDelete,
                                  }        
        stateArgs = BLOCKGEN.validate_stateArg(state)
        _l_moduleStates = BLOCKSHARED._l_blockStates
        
        if not stateArgs:
            return False
    
        _idx_target = stateArgs[0]
        _state_target = stateArgs[1]
        
        log.info("|{0}| >> Target state: {1} | {2}".format(_str_func,_state_target,_idx_target))
        
        #>>> Meat
        #========================================================================
        currentState = _mBlock.getState(False) 
        
        if currentState == _idx_target and rebuildFrom is None and not forceNew:
            if not forceNew:
                log.info("|{0}| >> block [{1}] already in {2} state".format(_str_func,_mBlock.mNode,currentState))                
            return True
        
        
        #If we're here, we're going to move through the set states till we get to our spot
        
        log.info("|{0}| >> Changing states...".format(_str_func))
        if _idx_target > currentState:
            startState = currentState+1        
            doStates = _l_moduleStates[startState:_idx_target+1]
            log.info("|{0}| >> Going up. First stop: {1} | All stops: {2}".format(_str_func, _l_moduleStates[startState],doStates))
            
            for doState in doStates:
                #if doState in d_upStateFunctions.keys():
                log.info("|{0}| >> Up to: {1} ....".format(_str_func, doState))
                if not d_upStateFunctions[doState]():
                    log.info("|{0}| >> Failed: {1} ....".format(_str_func, doState))
                    return False
                #else:
                #    log.info("|{0}| >> No upstate function for {1} ....".format(_str_func, doState))
            return True
        elif _idx_target < currentState:#Going down
            l_reverseModuleStates = copy.copy(_l_moduleStates)
            l_reverseModuleStates.reverse()
            startState = currentState 
            rev_start = l_reverseModuleStates.index( _l_moduleStates[startState] )+1
            rev_end = l_reverseModuleStates.index( _l_moduleStates[_idx_target] )+1
            doStates = l_reverseModuleStates[rev_start:rev_end]
            log.info("|{0}| >> Going down. First stop: {1} | All stops: {2}".format(_str_func, startState, doStates))
            
            for doState in doStates:
                log.info("|{0}| >> Down to: {1} ....".format(_str_func, doState))
                if not d_downStateFunctions[doState]():
                    log.info("|{0}| >> Failed: {1} ....".format(_str_func, doState))
                    return False 
            return True
        else:
            log.error('Forcing recreate')
            if stateName in d_upStateFunctions.keys():
                if not d_upStateFunctions[stateName](self._mi_module,*args,**kws):return False
                return True	            
    
    def template(self):
        if self._mi_block is None:
            raise ValueError,"No root loaded."
        _mBlock = self._mi_block

        if _mBlock.isReferenced():
            raise ValueError,"Referenced node."
        
        _str_func = '[{0}] factory.template'.format(_mBlock.p_nameBase)
        
        _str_state = _mBlock.blockState
        
        if _mBlock.blockState != 'define':
            raise ValueError,"{0} is not in define state. state: {1}".format(_str_func, _str_state)
        
        #>>>Children ------------------------------------------------------------------------------------
        
        
        #>>>Meat ------------------------------------------------------------------------------------
        _mBlock.blockState = 'define>template'#...buffering that we're in process
        
        _mBlockModule = get_blockModule(_mBlock.blockType)
        
        if 'template' in _mBlockModule.__dict__.keys():
            log.info("|{0}| >> BlockModule call found...".format(_str_func))            
            _mBlockModule.template(_mBlock)
        
        for mShape in _mBlock.getShapes(asMeta=True):
            mShape.doName()
            
        _mBlock.blockState = 'template'#...yes now in this state
        return True

    
    def templateDelete(self):
        if self._mi_block is None:
            raise ValueError,"No root loaded."
        _mBlock = self._mi_block

        if _mBlock.isReferenced():
            raise ValueError,"Referenced node."
        
        _str_func = '[{0}] factory.templateDelete'.format(_mBlock.p_nameBase)
        _str_state = _mBlock.blockState
        
        if _mBlock.blockState != 'template':
            raise ValueError,"{0} is not in template state. state: {1}".format(_str_func, _str_state)
        
        
        #>>>Children ------------------------------------------------------------------------------------
        
        
        #>>>Meat ------------------------------------------------------------------------------------
        _mBlock.blockState = 'template>define'        
        
        _mBlockModule = get_blockModule(_mBlock.blockType)
        _mBlockCall = False
        if 'templateDelete' in _mBlockModule.__dict__.keys():
            log.info("|{0}| >> BlockModule templateDelete call found...".format(_str_func))            
            _mBlockCall = _mBlockModule.templateDelete    
            
        if 'define' in _mBlockModule.__dict__.keys():
                    log.info("|{0}| >> BlockModule define call found...".format(_str_func))            
                    _mBlockCall = _mBlockModule.define   
                    
        #Delete our shapes...
        mc.delete(_mBlock.getShapes())
        
        if _mBlockCall:
            _mBlockCall(_mBlock)
            
        _mBlock.blockState = 'define'
        
        return True
        
        
    
    def prerig(self):
        if self._mi_block is None:
            raise ValueError,"No root loaded."
        _mBlock = self._mi_block

        if _mBlock.isReferenced():
            raise ValueError,"Referenced node."
        
        _str_func = '[{0}] factory.prerig'.format(_mBlock.p_nameBase)
        _str_state = _mBlock.blockState
        
        if _mBlock.blockState != 'template':
            raise ValueError,"{0} is not in template state. state: {1}".format(_str_func, _str_state)
        
        #>>>Children ------------------------------------------------------------------------------------
        
        
        #>>>Meat ------------------------------------------------------------------------------------
        _mBlock.blockState = 'template>prerig'#...buffering that we're in process
        
        _mBlockModule = get_blockModule(_mBlock.blockType)
        
        if 'prerig' in _mBlockModule.__dict__.keys():
            log.info("|{0}| >> BlockModule prerig call found...".format(_str_func))            
            _mBlockModule.prerig(_mBlock)
 
        _mBlock.blockState = 'prerig'#...yes now in this state
        return True
    
    def prerigDelete(self):
        if self._mi_block is None:
            raise ValueError,"No root loaded."
        _mBlock = self._mi_block

        if _mBlock.isReferenced():
            raise ValueError,"Referenced node."
        
        _str_func = '[{0}] factory.prerigDelete'.format(_mBlock.p_nameBase)
        _str_state = _mBlock.blockState

        if _mBlock.blockState != 'prerig':
            raise ValueError,"{0} is not in prerig state. state: {1}".format(_str_func, _str_state)
        
        
        #>>>Children ------------------------------------------------------------------------------------
        
        
        #>>>Meat ------------------------------------------------------------------------------------        
        _mBlock.blockState = 'prerig>template'        
        
        _mBlockModule = get_blockModule(_mBlock.blockType)
        _mBlockCall = False
        if 'prerigDelete' in _mBlockModule.__dict__.keys():
            log.info("|{0}| >> BlockModule prerigDelete call found...".format(_str_func))            
            _mBlockCall = _mBlockModule.prerigDelete    
            
        
        if _mBlockCall:
            _mBlockCall(_mBlock)
            
        _mBlock.blockState = 'template'
        
        return True
    
    def rig(self):
        #Master control
        if self._mi_block is None:
            raise ValueError,"No root loaded."
        _mBlock = self._mi_block

        if _mBlock.isReferenced():
            raise ValueError,"Referenced node."
        
        _str_func = '[{0}] factory.rig'.format(_mBlock.p_nameBase)
        _str_state = _mBlock.blockState
        
        
        if _mBlock.blockState != 'prerig':
            raise ValueError,"{0} is not in prerig state. state: {1}".format(_str_func, _str_state)      
        
        #>>>Children ------------------------------------------------------------------------------------
        
        
        #>>>Meat ------------------------------------------------------------------------------------
        _mBlock.blockState = 'prerig>rig'#...buffering that we're in process
        _mBlockModule = get_blockModule(_mBlock.blockType)
        
        if 'rig' in _mBlockModule.__dict__.keys():
            log.info("|{0}| >> BlockModule rig call found...".format(_str_func))            
            _mBlockModule.rig(_mBlock)
            
        _mBlock.blockState = 'rig'#...yes now in this state
        return True
    
    def rigDelete(self):
        if self._mi_block is None:
            raise ValueError,"No root loaded."
        _mBlock = self._mi_block

        if _mBlock.isReferenced():
            raise ValueError,"Referenced node."
        
        _str_func = '[{0}] factory.rigDelete'.format(_mBlock.p_nameBase)
        _str_state = _mBlock.blockState
        
        if _mBlock.blockState != 'rig':
            raise ValueError,"{0} is not in rig state. state: {1}".format(_str_func, _str_state)
        
        _mBlock.blockState = 'rig>prerig'        
        
        _mBlockModule = get_blockModule(_mBlock.blockType)
        _mBlockCall = False
        if 'rigDelete' in _mBlockModule.__dict__.keys():
            log.info("|{0}| >> BlockModule rigDelete call found...".format(_str_func))            
            _mBlockCall = _mBlockModule.rigDelete    
            
        
        if _mBlockCall:
            _mBlockCall(_mBlock)
            
        _mBlock.blockState = 'prerig'
        
        return True
    
    #========================================================================================================     
    #>>> Self changes 
    #========================================================================================================  
    def set_rigBlock(self,root=None):
        """
        Set the active rigBlock to our factory

        :parameters:
            root(str) | node to set as our rigBlock

        :returns
            success(bool)
        """            
        _str_func = 'rigBlock_set'
        log.debug("|{0}| >> root kw: {1}".format(_str_func,root))
        self._mi_block = False
        self._mi_module = False
        self._mi_puppet = False   

        if root is None:
            return False
        
        self._mi_block = cgmMeta.validateObjArg(root,'cgmObject')
        log.debug("|{0}| >> mInstance: {1}".format(_str_func,self._mi_block))
        pass
    
    def get_rigBlockData( self, blockType = None ):
        _str_func = 'get_rigBlockData'

        if self._mi_block is None:
            raise ValueError,"No root loaded."

        _mBlock = self._mi_block
        _short = _mBlock.p_nameShort
             
        log.info("|{0}| >> [{1}] |...".format(_str_func,_short))
        
        _res = {}
        
        #Block data
        _res['block'] = {}
        _d_block = _res['block']
        
        for a in mc.listAttr(_short,ud=True):
            _d_block[a] = ATTR.get(_short,a)
        
        #Children Data
        #Sub Data
        #Positional data
        _res['pos'] = {}
        _d_pos = _res['pos']        
        for i,mObj in enumerate([_mBlock]):
            _d_pos[i] = [mObj.getPosition(),'euler','localScale']
        
        cgmGEN.log_info_dict(_res, "Block Data [{0}]".format(_short))
        return _res
        
    #========================================================================================================     
    #>>> Rigblock 
    #========================================================================================================      
    def rebuild_rigBlock( self, deleteOriginal = True ):
        """
        Rebuild a rigBlock

        :parameters:
            deleteOriginal(bool) | Whether to delete original or not. If True, the new one is loaded to the factory

        :returns
            success(bool)
        """ 
        if self._mi_block is None:
            raise ValueError,"No root loaded."

        _mBlock = self._mi_block
        _short = _mBlock.p_nameShort
        
        _str_func = '[{0}] factory.rebuild_rigBlock'.format(_mBlock.p_nameBase)
        _blockType = _mBlock.blockType
        
        if _mBlock.isReferenced():
            raise ValueError,"Referenced node. Cannot rebuild"        
        
        _blockParent = _mBlock.p_blockParent
        
        #Get Block Children
        _ml_blockChildren = _mBlock.getBlockChildren(True)
        if _ml_blockChildren:
            log.info("|{0}| >> [{1}] | Block children...".format(_str_func,_short))            
            for mChild in _ml_blockChildren:
                mChild.p_blockParent = False

        _blockDat = _mBlock.p_blockDat

        
        #Create New
        _mBlockNEW = self.create_rigBlock(_blockType)
        _short = _mBlockNEW.p_nameShort
        
        _mBlockNEW.p_blockDat = _blockDat
        
        #Reattach Children
        if _ml_blockChildren:
            log.info("|{0}| >> [{1}] | reconnecting children...".format(_str_func,_short))            
            for mChild in _ml_blockChildren:
                mChild.p_blockParent = _mBlockNEW        
        
        #If blockParent = set
        if _blockParent:
            _mBlockNEW.parent = _blockParent
        
        if deleteOriginal:
            _mBlock.delete()
            self.set_rigBlock(_mBlockNEW)
        
        return _mBlockNEW


    def create_skeleton(self,forceNew = False):
        """
        Create a the base joints of a rigBlock

        :parameters:
            forceNew(bool) | whether to rebuild on call or not

        :returns
            joints(mList)
        """           
        _str_func = 'skeletonize'
        _blockType = self._mi_block.blockType
        #>> Get positions -----------------------------------------------------------------------------------
        _d_create = self.get_skeletonCreateDict(_blockType)

        #>> If check for module,puppet -----------------------------------------------------------------------------------
        if not self._mi_module:
            self.module_verify()
        if not self._mi_puppet:
            self.puppet_verify()

        #>> If skeletons there, delete ----------------------------------------------------------------------------------- 
        _bfr = self._mi_module.rigNull.msgList_get('skinJoints')
        if _bfr:
            log.debug("|{0}| >> Joints detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in _bfr])
            else:
                return _bfr

        #Build skeleton -----------------------------------------------------------------------------------
        _ml_joints = build_skeleton(_d_create['positions'],worldUpAxis=_d_create['worldUpAxis'])

        #Wire and name        
        self._mi_module.rigNull.msgList_connect(_ml_joints,'skinJoints')
        self._mi_module.rigNull.msgList_connect(_ml_joints,'moduleJoints')

        #...need to do this better...
        #>>>HANDLES,CORENAMES -----------------------------------------------------------------------------------
        _ml_joints[0].addAttr('cgmName',_blockType)
        for i,mJnt in enumerate(_ml_joints):
            mJnt.addAttr('cgmIterator',i)
            mJnt.doName()

        return _ml_joints

    def create_mesh(self,mode='simple',castMesh = None):
        """
        Create mesh from our module..

        :parameters:
            mode(string) | kind of mesh to cast
                simple
                recast
                jointProxy

        :returns
            mesh(str)
        """          
        _str_func = 'create_mesh'
        
        _mode = mode
        _castMesh = castMesh
        
        if self._mi_block is None:
            raise ValueError,"|{0}| >> No root loaded.".format(_str_func)
        _root = self._mi_block.mNode    
                
        _joints = ATTR.get(_root,'joints')
        
        log.debug("|{0}| >> mode: {1} | count: {2} | ".format(_str_func,_mode,_joints))
        
        if _mode == 'simple':
            return build_loftMesh(_root,_joints)
        elif _mode in ['jointProxy','recast']:
            if not self.module_verify():
                raise ValueError,"|{0}| >> Module necessary for mode: {1}.".format(_str_func,_mode)
            
            if _mode == 'jointProxy':
                log.info(_root)
                return build_jointProxyMesh(_root)
        #else:
        raise NotImplementedError,"|{0}| >> mode not implemented: {1}".format(_str_func,_mode)
        

        
        
        #Get our cast curves
        pass

    #========================================================================================================     
    #>>> PuppetMeta 
    #========================================================================================================  
    def module_verify(self):
        """
        Verify a loaded rigBlock's module or create if necessary

        :returns
            moduleInstance(cgmModule)
        """           
        _str_func = 'module_verify'
        self._mi_module = False

        if self._mi_block is None:
            raise ValueError,"|{0}| >> No root loaded.".format(_str_func)
        _mBlock = self._mi_block        
        
        if self._mi_block.blockType == 'master':
            return True

        _bfr = _mBlock.getMessage('moduleTarget')
        _kws = self.module_getBuildKWS()

        if _bfr:
            log.debug("|{0}| >> moduleTarget found: {1}".format(_str_func,_bfr))            
            mModule = cgmMeta.validateObjArg(_bfr,'cgmObject')
        else:
            log.debug("|{0}| >> Creating moduleTarget...".format(_str_func))   
            mModule = PUPPETMETA.cgmModule(**_kws)

        ATTR.set_message(_mBlock.mNode, 'moduleTarget', mModule.mNode,simple = True)
        ATTR.set_message(mModule.mNode, 'rigHelper', _mBlock.mNode,simple = True)

        ATTR.set(mModule.mNode,'moduleType',_kws['name'],lock=True)
        self._mi_module = mModule
        
        assert mModule.isModule(),"Not a module: {0}".format(mModule)
        
        return mModule

    def module_getBuildKWS(self):
        """
        Get expected build kws for a new module

        :returns
            dict
        """            
        _str_func = 'module_getBuildKWS'

        if self._mi_block is None:
            raise ValueError,"|{0}| >> No root loaded.".format(_str_func)
        _mBlock = self._mi_block

        d_kws = {}
        d_kws['name'] = str(_mBlock.blockType)

        #Direction
        str_direction = None
        if _mBlock.hasAttr('direction'):
            str_direction = _mBlock.getEnumValueString('direction')
        log.debug("|{0}| >> direction: {1}".format(_str_func,str_direction))            
        if str_direction in ['left','right']:
            d_kws['direction'] = str_direction
        #Position
        str_position = None
        if _mBlock.hasAttr('position'):
            str_position = _mBlock.getEnumValueString('position')	
        log.debug("|{0}| >> position: {1}".format(_str_func,str_position))            
        if str_position != 'none':
            d_kws['position'] = str_position

        cgmGEN.log_info_dict(d_kws,"{0} d_kws".format(_str_func))
        return d_kws

    def puppet_verify(self):
        """
        Verify a loaded rigBlock's puppet or create if necessary

        :returns
            puppetInstance(cgmPuppet)
        """            
        _str_func = 'puppet_verify'
        self._mi_puppet = False

        if self._mi_block is None:
            raise ValueError,"|{0}| >> No root loaded.".format(_str_func)
        _mBlock = self._mi_block     
        
        if self._mi_block.blockType == 'master':
            if not _mBlock.getMessage('moduleTarget'):
                mi_puppet = PUPPETMETA.cgmPuppet(name = _mBlock.puppetName)
                ATTR.set_message(_mBlock.mNode, 'moduleTarget', mi_puppet.mNode,simple = True)
            else:
                mi_puppet = _mBlock.moduleTarget
                
            mi_puppet.__verify__()
        else:
            mi_module = _mBlock.moduleTarget
            if not mi_module:
                mi_module = self.module_verify()
    
            _bfr = mi_module.getMessage('modulePuppet')
            if _bfr:
                log.debug("|{0}| >> modulePuppet found: {1}".format(_str_func,_bfr))                        
                mi_puppet = mi_module.modulePuppet
            else:
                mi_puppet = PUPPETMETA.cgmPuppet(name = mi_module.getNameAlias())
            
            if mi_module.getMessage('moduleMirror'):
                mi_puppet.connectModule(mi_module.moduleMirror)            

            mi_puppet.connectModule(mi_module)	

            mi_puppet.gatherModules()#Gather any modules in the chain
            
        self._mi_puppet = mi_puppet
        
        if not mi_puppet.getMessage('masterNull'):
            mi_puppet.__verify__()
        
        if not mi_puppet.masterNull.getMessage('blocksGroup'):
            mGroup = cgmMeta.cgmObject(name='blocks')#Create and initialize
            mGroup.doName()
            mGroup.parent = mi_puppet.masterNull

            mGroup.connectParentNode(mi_puppet.masterNull.mNode, 'puppet','blocksGroup') 
            ATTR.set_standardFlags(mGroup.mNode)
            #ATTR.doSetLockHideKeyableAttr( self.__dict__[Attr].mNode ) 	    
        
        return mi_puppet        

#====================================================================================	
#>> Utilities
#====================================================================================	
def get_modules_dict():
    return get_modules_dat()[0]

def get_modules_dat():
    """
    Data gather for available blocks.

    :parameters:

    :returns
        _d_modules, _d_categories, _l_unbuildable
        _d_modules(dict) - keys to modules
        _d_categories(dict) - categories to list of entries
        _l_unbuildable(list) - list of unbuildable modules
    """
    _str_func = 'get_modules_dict'    
    
    _b_debug = log.isEnabledFor(logging.DEBUG)
    
    import cgm.core.mrs.blocks as blocks
    _path = PATH.Path(blocks.__path__[0])
    _l_duplicates = []
    _l_unbuildable = []
    _base = _path.split()[-1]
    _d_files =  {}
    _d_modules = {}
    _d_import = {}
    _d_categories = {}
    
    log.debug("|{0}| >> Checking base: {1} | path: {2}".format(_str_func,_base,_path))   
    _i = 0
    for root, dirs, files in os.walk(_path, True, None):
        # Parse all the files of given path and reload python modules
        _mBlock = PATH.Path(root)
        _split = _mBlock.split()
        _subRoot = _split[-1]
        _splitUp = _split[_split.index(_base):]
        
        log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        log.debug("|{0}| >> On split: {1}".format(_str_func,_splitUp))   
        
        if len(_split) == 1:
            _cat = 'base'
        else:_cat = _split[-1]
        _l_cat = []
        _d_categories[_cat]=_l_cat
        
        for f in files:
            key = False
            
            if f.endswith('.py'):
                    
                if f == '__init__.py':
                    continue
                else:
                    name = f[:-3]    
            else:
                continue
                    
            if _i == 'cat':
                key = '.'.join([_base,name])                            
            else:
                key = '.'.join(_splitUp + [name])    
                if key:
                    log.debug("|{0}| >> ... {1}".format(_str_func,key))                      
                    if name not in _d_modules.keys():
                        _d_files[key] = os.path.join(root,f)
                        _d_import[name] = key
                        _l_cat.append(name)
                        try:
                            module = __import__(key, globals(), locals(), ['*'], -1)
                            reload(module) 
                            _d_modules[name] = module
                            #if not is_buildable(module):
                                #_l_unbuildable.append(name)
                        except Exception, e:
                            for arg in e.args:
                                log.error(arg)
                            raise RuntimeError,"Stop"  
                                          
                    else:
                        _l_duplicates.append("{0} >> {1} ".format(key, os.path.join(root,f)))
            _i+=1
            
    if _b_debug:
        cgmGEN.log_info_dict(_d_modules,"Modules")        
        cgmGEN.log_info_dict(_d_files,"Files")
        cgmGEN.log_info_dict(_d_import,"Imports")
        cgmGEN.log_info_dict(_d_categories,"Categories")
    
    if _l_duplicates and _b_debug:
        log.debug(cgmGEN._str_subLine)
        log.debug("|{0}| >> DUPLICATE MODULES....".format(_str_func))
        for m in _l_duplicates:
            print(m)
        raise Exception,"Must resolve"
    log.debug("|{0}| >> Found {1} modules under: {2}".format(_str_func,len(_d_files.keys()),_path))     
    if _l_unbuildable and _b_debug:
        log.info(cgmGEN._str_subLine)
        log.info("|{0}| >> ({1}) Unbuildable modules....".format(_str_func,len(_l_unbuildable)))
        for m in _l_unbuildable:
            print(">>>    " + m) 
    return _d_modules, _d_categories, _l_unbuildable


def get_blockModule(blockType):
    """
    Function to check if a givin block module is buildable or not
        
    :parameters:
        blockType(str): Object to modify

    :returns
        success(bool)
    """
    _str_func = 'get_blockModule'  
    
    _res = True
    
    if VALID.stringArg(blockType):
        _d = get_modules_dict()
        _buildModule = _d.get(blockType,False)
        if not _buildModule:
            log.error("|{0}| >> [{1}] | Failed to query name in library ".format(_str_func,blockType))   
            return False
    else:
        _buildModule = blockType
    try:
        _blockType = _buildModule.__name__.split('.')[-1]
    except:
        log.error("|{0}| >> [{1}] | Failed to query name. Probably not a module".format(_str_func,_buildModule))        
        return False
    
    return _buildModule        
 

def is_buildable(blockModule):
    """
    Function to check if a givin block module is buildable or not
    
    """
    _str_func = 'is_buildable'  
    
    _res = True
    #_buildModule = _d_blockTypes[blockType]
    
    if VALID.stringArg(blockModule):
        _d = get_modules_dict()
        _buildModule = _d.get(blockModule,False)
    
    else:
        _buildModule = blockModule
    try:
        _blockType = _buildModule.__name__.split('.')[-1]
    except:
        log.error("|{0}| >> [{1}] | Failed to query name. Probably not a module".format(_str_func,_buildModule))        
        return False
    
    _keys = _buildModule.__dict__.keys()
    _l_missing = []
    for a in BLOCKSHARED._l_requiredModuleDat:
        if a not in _keys:
            _l_missing.append(a)
            _res = False
            
    if _l_missing:
        log.warning("|{0}| >> [{1}] Missing data...".format(_str_func,_blockType))
        for i,a in enumerate(_l_missing):
            log.warning("|{0}| >> {1} : {2}".format(_str_func,i,a))    
    if _res:return _buildModule
    return _res


def is_blockModule_valid(blockType):
    """
    Function to check if a given blockType module is buildable, rigable, skeleton
    
    """    
    _str_func = 'is_blockModule_valid'
    _res = True
    
    _buildModule = get_blockModule(blockType)
    if not _buildModule:
        return False
    
    _keys = _buildModule.__dict__.keys()
    
    for a in BLOCKSHARED._l_requiredModuleDat:
        if a not in _keys:
            log.warning("|{0}| >> [{1}] Missing data: {2}".format(_str_func,_blockType,a))
            _res = False
            
    if _res:return _buildModule
    return _res

def is_blockType_valid(blockType):
    """
    Function to check if a given blockType is valid
    
    """    
    _str_func = 'is_blockType_valid'
    _res = True
    
    _d = get_modules_dict()
    if blockType not in _d.keys():
        log.warning("|{0}| >> [{1}] Not found. | {2}".format(_str_func,blockType,_d.keys()))
        return False
    return True
   
    

#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================    
r9Meta.registerMClassInheritanceMapping()#Pushes our classes in
    
    
    
    
    
    
    






