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

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
import cgm.core.cgm_RigMeta as RIGMETA
from cgm.core import cgm_PuppetMeta as PUPPETMETA

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
import cgm.core.lib.transform_utils as TRANS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as CORERIG
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.classes.NodeFactory as NODEFAC
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
from cgm.core.mrs.lib import general_utils as BLOCKGEN
from cgm.core.mrs.lib import builder_utils as BUILDERUTILS
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
reload(BUILDERUTILS)
from cgm.core.lib import nameTools
reload(BLOCKSHARE)
from cgm.core.classes import GuiFactory as CGMUI
reload(CGMUI)

get_from_scene = BLOCKGEN.get_from_scene

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

    def __init__(self, node = None, blockType = None, blockParent = None, *args,**kws):
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
        
        if blockParent is not None:
            try:
                self.p_blockParent = blockParent
            except Exception,err:
                log.warning("|{0}| >> blockParent on call failure.".format(_str_func))
                for arg in err.args:
                    log.error(arg)                  
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
        self._blockModule = None
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
                log.debug("|{0}| >> AutoTemplate...".format(_str_func))  
                try:
                    self.p_blockState = 'template'
                except Exception,err:
                    for arg in err.args:
                        log.error(arg)  
                        
        #self._blockModule = get_blockModule(ATTR.get(self.mNode,'blockType'))        
                        
 
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
        if blockType is not None:
            if _type is not None and _type != blockType:
                raise ValueError,"|{0}| >> Conversion necessary. blockType arg: {1} | found: {2}".format(_str_func,blockType,_type)
        else:
            blockType = _type
            
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
            log.debug("|{0}| >> BlockModule define call found...".format(_str_func))            
            _mBlockModule.define(self)      
        self._blockModule = _mBlockModule
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
        if self.getMayaAttr('side'):
            _d['cgmDirection'] = self.getEnumValueString('side')

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
            _res = _mBlockParent[0]
        else:
            for mParent in self.getParents(asMeta=True):
                if issubclass(type(mParent), cgmRigBlock):
                    _res = mParent
        if _res and not asMeta:
            return _res.mNode
        return _res
    
    def getBlockParents(self,asMeta=True):
        """
        Get all the parents of a given node where the last parent is the top of the heirarchy
        
        :parameters:
            node(str): Object to check
            fullPath(bool): Whether you want long names or not
    
        :returns
            parents(list)
        """   
        _str_func = 'getBlockParents'
        
        _ml_parents = []
        tmpObj = self
        noParent = False
        while noParent == False:
            tmpParent = tmpObj.getBlockParent(True)
            if tmpParent:
                _ml_parents.append(tmpParent)
                tmpObj = tmpParent
            else:
                noParent = True
                
        if _ml_parents and not asMeta:
            return [mObj.mNode for mObj in _ml_parents]
        return _ml_parents

    def setBlockParent(self, parent = False, attachPoint = None):        
        _str_func = 'setBlockParent'
        
        if not parent:
            self.blockParent = False
            self.p_parent = False
        
        else:
            if parent == self:
                raise ValueError, "Cannot blockParent to self"
                
            #if parent.getMessage('blockParent') and parent.blockParent == self:
                #raise ValueError, "Cannot blockParent to block whose parent is self"

            self.connectParentNode(parent, 'blockParent')
            if attachPoint:
                self.p_parent = attachPoint
            else:
                self.p_parent = parent
            
    p_blockParent = property(getBlockParent,setBlockParent)
    
    def getBlockChildren(self,asMeta=True):
        _str_func = 'getBlockChildren'
        #ml_nodeChildren = self.getChildMetaNodes(mType = ['cgmRigBlock'])
        
        #ml_nodeChildren = self.getChildMetaNodes(mAttrs = 'mClass=cgmRigBlock')
        #if self in ml_nodeChildren:
            #ml_nodeChildren.remove(self)
        ml_nodeChildren = []
        for link in ATTR.get_driven(self.mNode,'message') or []:
            if link.endswith('.blockParent'):
                ml_nodeChildren.append(cgmMeta.validateObjArg(link.split('.')[0],'cgmObject'))
            
        for mChild in ml_nodeChildren:
            if not issubclass(type(mChild),cgmRigBlock):
                ml_nodeChildren.remove(mChild)
            
        ml_children = self.getChildren(asMeta = True, fullPath=True)#...always full path
        
        for mChild in ml_children:
            if mChild not in ml_nodeChildren and issubclass(type(mChild),cgmRigBlock):
                log.debug("|{0}| >> Found as reg child: {1}".format(_str_func,mChild.mNode))        
                ml_nodeChildren.append(mChild)
        
        if not asMeta:
            return [mChild.mNode for mChild in ml_nodeChildren]
        return ml_nodeChildren
    
    p_blockChildren = property(getBlockChildren)
    
    def getBlockHeirarchyBelow(self,asMeta=True,report = False):
        _res = BLOCKGEN.walk_rigBlock_heirarchy(self,asMeta=asMeta)
        if not _res:
            return False
        if report:cgmGEN.walk_dat(_res,"{0}.getBlockHeirarchyBelow...".format(self.mNode))
        if asMeta:
            return _res[self]
        return _res[self.mNode]
    

    
    #========================================================================================================     
    #>>> Info 
    #========================================================================================================      
    def getModuleStatus(self,state = None):
        return get_blockModule_status(self.blockType, state)
    
    def getBlockDat_templateControls(self,report = False):
        _short = self.p_nameShort        
        _str_func = '[{0}] getBlockDat_templateControls'.format(_short)
        
        _blockState_int = self.getState(False)
        
        if not _blockState_int:
            raise ValueError,'[{0}] not templated yet'.format(_short)
        elif _blockState_int == 1:
            _ml_templateHandles = self.msgList_get('templateHandles',asMeta = True)            
        else:
            _ml_templateHandles = self.msgList_get('prerigHandles',asMeta = True)
        
        if not _ml_templateHandles:
            log.error('[{0}] No template or prerig handles found'.format(_short))
            return False
        
        _ml_controls = [self] + _ml_templateHandles
        
        _l_orientHelpers = []
        _l_jointHelpers = []
        for i,mObj in enumerate(_ml_templateHandles):
            log.info("|{0}| >>  {1} | {2}".format(_str_func,i,mObj.mNode))
            if mObj.getMessage('orientHelper'):
                _l_orientHelpers.append(mObj.orientHelper.rotate)
            else:
                _l_orientHelpers.append(False)
            if mObj.getMessage('jointHelper'):
                _l_jointHelpers.append(mObj.jointHelper.translate)
            else:
                _l_jointHelpers.append(False)
                
        _d = {'positions':[mObj.p_position for mObj in _ml_templateHandles],
              'orientations':[mObj.p_orient for mObj in _ml_templateHandles],
              'scales':[mObj.scale for mObj in _ml_templateHandles],
              'jointHelpers':_l_jointHelpers,
              'orientHelpers':_l_orientHelpers}
        
        if self.getMessage('orientHelper'):
            _d['rootOrientHelper'] = self.orientHelper.rotate
        
        if report:cgmGEN.walk_dat(_d,'[{0}] template blockDat'.format(self.p_nameShort))
        return _d
    
    def getBlockDat_prerigControls(self,report = False):
        _short = self.p_nameShort        
        _str_func = '[{0}] getBlockDat_prerigControls'.format(_short)
        
        _ml_rigHandles = self.msgList_get('rigHandles',asMeta = True)
        if not _ml_rigHandles:
            return False
        
        _ml_controls = [self] + _ml_rigHandles
        
        _l_orientHelpers = []
        _l_jointHelpers = []
        
        for i,mObj in enumerate(_ml_rigHandles):
            log.info("|{0}| >>  {1} | {2}".format(_str_func,i,mObj.mNode))
            if mObj.getMessage('orientHelper'):
                _l_orientHelpers.append(mObj.orientHelper.rotate)
            else:
                _l_orientHelpers.append(False)
            if mObj.getMessage('jointHelper'):
                _l_jointHelpers.append(mObj.jointHelper.translate)
            else:
                _l_jointHelpers.append(False)
                
        _d = {'positions':[mObj.p_position for mObj in _ml_rigHandles],
              'orientations':[mObj.p_orient for mObj in _ml_rigHandles],
              'scales':[mObj.scale for mObj in _ml_rigHandles],
              'jointHelpers':_l_jointHelpers,
              'orientHelpers':_l_orientHelpers}
        
        if self.getMessage('orientHelper'):
            _d['rootOrientHelper'] = self.orientHelper.rotate
        
        if report:cgmGEN.walk_dat(_d,'[{0}] prerig blockDat'.format(self.p_nameShort))
        return _d    
    
    def getBlockAttributes(self):
        """
        keyable and unlocked attributes
        """
        _res = []
        _short = self.mNode
        for attr in self.getAttrs(ud=True):
            _type = ATTR.get_type(_short,attr)
            if not ATTR.is_hidden(_short,attr):#and not ATTR.is_locked(_short,attr)
                _res.append(attr)
        return _res
    p_blockAttributes = property(getBlockAttributes)
    
    def getBlockModule(self):
        blockType = self.getMayaAttr('blockType')
        return get_blockModule(blockType)
    
    p_blockModule = property(getBlockModule)
        
    def getBlockDat(self,report = True):
        """
        Carry from Bokser stuff...
        """
        _l_udMask = ['blockDat','attributeAliasList','blockState','mClass','mClassGrp','mNodeID','version']
        _ml_controls = self.getControls(True)
        _short = self.p_nameShort
        _blockState_int = self.getState(False)
        #Trying to keep un assertable data out that won't match between two otherwise matching RigBlocks
        _d = {#"name":_short, 
              "blockType":self.blockType,
              "blockState":self.p_blockState,
              "baseName":self.getMayaAttr('puppetName') or self.getMayaAttr('baseName'), 
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
            _d["size"] = DIST.get_size_byShapes(self),
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
        
    def saveBlockDat(self):
        self.blockDat = self.getBlockDat()
        
    def resetBlockDat(self):
        #This needs more work.
        self._factory.verify(self.blockType, forceReset=True) 
        
    def printBlockDat(self):
        cgmGEN.walk_dat(self.blockDat,'[{0}] blockDat'.format(self.p_nameShort))
        
    def loadBlockDat(self,blockDat = None):
        _short = self.p_nameShort        
        _str_func = '[{0}] loadBlockDat'.format(_short)
        
        if blockDat is None:
            log.debug("|{0}| >> No blockDat passed. Checking self...".format(_str_func))    
            blockDat = self.blockDat
            
        if not issubclass(type(blockDat),dict):
            raise ValueError,"|{0}| >> blockDat must be dict. type: {1} | blockDat: {2}".format(_str_func,type(blockDat),blockDat) 
        
        _blockType = blockDat.get('blockType')
        if _blockType != self.blockType:
            raise ValueError,"|{0}| >> blockTypes don't match. self: {1} | blockDat: {2}".format(_str_func,self.blockType,_blockType) 
        
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
                mObj.p_position = _pos[i]
                mObj.p_orient = _orients[i]
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
                            log.info ("|{0}| >> TemplateHandle: {1}".format(_str_func,mObj.mNode))
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
        #return BLOCKSHARE._l_blockStates.index(self.blockState)
        _blockModule = get_blockModule(self.blockType)
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
            _call = getattr(_blockModule,'is_{0}'.format(_state))
            if _call and _call(self):
                log.debug("|{0}| >> blockModule test...".format(_str_func))     
                _goodState = _state  
            else:
                _idx = _l_blockStates.index(_state) - 1
                log.debug("|{0}| >> blockModule test failed. Testing: {1}".format(_str_func, _l_blockStates[_idx]))                
                while _idx > 0 and not _blockModule.__dict__['is_{0}'.format(_l_blockStates[_idx])](self):
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
            log.debug("|{0}| >> blockModule check...".format(_str_func))                                
            return _call(self)
        return False
    
    def doSkeletonize(self):
        _str_func = '[{0}] doSkeletonize'.format(self.p_nameShort)
        
        _blockModule = get_blockModule(self.blockType)
                
        _call = _blockModule.__dict__.get('skeletonize',False)
        if _call:
            log.debug("|{0}| >> blockModule check...".format(_str_func))                                
            return _call(self)
        return False
    
    def deleteSkeleton(self):
        _str_func = '[{0}] deleteSkeleton'.format(self.p_nameShort)
        
        _blockModule = get_blockModule(self.blockType)
                
        _call = _blockModule.__dict__.get('skeletonDelete',False)
        if _call:
            log.debug("|{0}| >> blockModule check...".format(_str_func))                                
            return _call(self)
        
        return True    


    #========================================================================================================     
    #>>> Mirror 
    #========================================================================================================      
    #========================================================================================================     
    #>>> Utilities 
    #========================================================================================================      
    def asHandleFactory(self,*a,**kws):
        return handleFactory(*a,**kws)
    def contextual_methodCall(self, context = 'self', func = 'getShortName',*args,**kws):
        """
        Function to contextually call a series of rigBlocks and run a methodCall on them with 
        args and kws
            
        :parameters:
            context(str): self,below,root,scene
            func(str): string of the method call to use. mBlock.getShortName(), is just 'getShortName'
            *args,**kws - pass through for method call
    
        :returns
            list of results(list)
        """        
        return contextual_method_call(self, context, func, *args, **kws)
    
    def atBlockModule(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        _blockModule = self.p_blockModule
        return self.stringModuleCall(_blockModule,func,*args, **kws)
    
    def atBlockUtils(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        reload(BLOCKUTILS)
        return self.stringModuleCall(BLOCKUTILS,func,*args, **kws)    
    
    def string_methodCall(self, func = 'getShortName', *args,**kws):
        """
        Function to call a self function by string. For menus and other reasons
        """
        _str_func = 'string_methodCall'
        _short = self.p_nameShort
        res = None
        
        if not args:
            _str_args = ''
        else:
            _str_args = ','.join(str(a) for a in args) + ','

                
        if not kws:
            kws = {}
            _kwString = ''  
        else:
            _l = []
            for k,v in kws.iteritems():
                _l.append("{0}={1}".format(k,v))
            _kwString = ','.join(_l)  

        try:
            log.debug("|{0}| >> On: {1}".format(_str_func,_short))     
            print("|{0}| >> {1}.{2}({3}{4})...".format(_str_func,_short,func,_str_args,_kwString))                                    
            res = getattr(self,func)(*args,**kws)
        except Exception,err:
            log.error(cgmGEN._str_hardLine)
            log.error("|{0}| >> Failure: {1}".format(_str_func, err.__class__))
            log.error("block: {0} | func: {1}".format(_short,func))            
            if args:
                log.error("Args...")
                for a in args:
                    log.error("      {0}".format(a))
            if kws:
                log.error(" KWS...".format(_str_func))
                for k,v in kws.iteritems():
                    log.error("      {0} : {1}".format(k,v))   
            log.error("Errors...")
            for a in err.args:
                log.error(a)
            log.error(cgmGEN._str_subLine)
            raise Exception,err
        return res
        
        print res
        return res


class handleFactory(object):
    _l_controlLinks = []
    _l_controlmsgLists = []	

    def __init__(self, node = None, baseShape = 'square',  baseSize = 1,
                 shapeDirection = 'z+', aimDirection = 'z+', upDirection = 'y+',
                 rigBlock = None, *a,**kws):
        """
        :returns
            factory instance
        """
        _str_func = 'handleFactory._init_'
        
        if a:log.debug("|{0}| >> a: {1}".format(_str_func,a))
        if kws:
            self._call_kws = kws
            cgmGEN.walk_dat(kws,_str_func)
            #log.debug("|{0}| >> kws: {1}".format(_str_func,kws))

        self._mTransform = None
        self._baseShape = baseShape
        self._baseSize = baseSize
        
        #if node is None:
            #self._mTransform = cgmMeta.createMetaNode('cgmObject',nodeType = 'transform', nameTools = baseShape)
            #self.rebuildSimple(baseShape,baseSize,shapeDirection)
        if node is not None:
            self.setHandle(node)
            
    def setHandle(self,arg = None):
        if not VALID.is_transform(arg):
            raise ValueError,"must be a transform"
        
        self._mTransform = cgmMeta.validateObjArg(arg,'cgmObject')
        
    def rebuildSimple(self, baseShape = None, baseSize = None, shapeDirection = 'z+'):
        self.cleanShapes()
        
        if baseShape is None:
            baseShape = 'square'
        
        self._mTransform.addAttr('baseShape', baseShape,attrType='string')
        
        SNAP.verify_aimAttrs(self._mTransform.mNode, aim = 'z+', up = 'y+')
        
        if baseSize is not None:
            self._mTransform.doStore('baseSize',baseSize)
        
        _baseSize = self._mTransform.baseSize
        
        _baseShape = self._mTransform.getMayaAttr('baseShape') 
        #_crv = CURVES.create_fromName(_baseShape, _baseSize, shapeDirection)
        #TRANS.snap(_crv, self._mTransform.mNode)
        mCrv = self.buildBaseShape(_baseShape,_baseSize,shapeDirection)
        CORERIG.shapeParent_in_place(self._mTransform.mNode,mCrv.mNode,False)
        
        # CURVES.create_fromName('square', color = 'yellow', direction = 'y+', sizeMode = 'fixed', size = _size * .5)
        
        #self.color()
        
        #if not self._mTransform.hasAttr('cgmName'):
            #self._mTransform.doStore('cgmName',baseShape)
            
        self._mTransform.doStore('cgmType','blockHandle')
        self._mTransform.doName()
        return True
        
    def verify(self, baseShape = None, baseSize = None, shapeDirection = 'z+'):
        SNAP.verify_aimAttrs(self._mTransform.mNode, aim = 'z+', up = 'y+')
        return True
        
    def cleanShapes(self):
        if self._mTransform.getShapes():
            mc.delete(self._mTransform.getShapes())     
            
        for link in ['loftCurve']:
            _buffer = self._mTransform.getMessage(link)
            if _buffer:
                mc.delete(_buffer)
                
            
    def getBaseCreateSize(self):
        _maxLossy = max(self._mTransform.getScaleLossy())
        _baseSize = self._mTransform.baseSize * _maxLossy    
        return _baseSize
    
    def color(self, target = None, side = None, controlType = None):
        mTransform = self._mTransform
        _side = 'center'
        _controlType = 'main'        
        
        if mTransform.getMessage('rigBlock'):
            pass
        else:
            if mTransform.hasAttr('side'):
                _bfr = mTransform.getEnumValueString('side')
                if _bfr in ['left','right','center']:
                    _side = _bfr

            
        if target is None:
            target = self._mTransform.mNode
        CORERIG.colorControl(target,_side,_controlType,transparent = True)
            
    
    def get_baseDat(self, baseShape = None, baseSize = None, shapeDirection = None):
        _str_func = 'get_baseDat'
        
    
        if not self._mTransform or self._mTransform.mNode is None:
            if baseShape:
                name=baseShape
            else:
                name='handleFactory_shape'
            self._mTransform = cgmMeta.createMetaNode('cgmObject', name = name, nodeType = 'transform',)
            log.error("|{0}| >> Must have an handle loaded. One Generated".format(_str_func))                                
        
        if baseShape:
            _baseShape = baseShape
        elif self._mTransform.hasAttr('baseShape'):
            _baseShape = self._mTransform.baseShape
        else:
            _baseShape = 'square'
            
        if baseSize is not None:
            _baseSize = baseSize
        elif self._mTransform.hasAttr('baseSize'):
            _baseSize = self._mTransform.baseSize
        else:
            _baseSize = 1.0
            
        return [_baseShape,_baseSize]
        
        
    def buildBaseShape(self, baseShape = None, baseSize = None, shapeDirection = 'z+' ):
        _baseDat = self.get_baseDat(baseShape,baseSize)
        _baseShape = _baseDat[0]
        _baseSize = _baseDat[1]
        
        if baseShape == 'self':
            _crv = mc.duplicate( self._mTransform.getShapes()[0])[0]
        else:
            _crv = CURVES.create_fromName(_baseShape, _baseSize, shapeDirection)
            TRANS.snap(_crv, self._mTransform.mNode) 
        mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
        
        #...lossy
        _lossy = self._mTransform.getScaleLossy()
        mCrv.scaleX = mCrv.scaleX * _lossy[0]
        mCrv.scaleY = mCrv.scaleY * _lossy[1]
        mCrv.scaleZ = mCrv.scaleZ * _lossy[2]

        return mCrv
    
    def addOrientHelper(self,baseShape=None, baseSize = None, shapeDirection = 'z-', setAttrs = {}):
        _baseDat = self.get_baseDat(baseShape,baseSize)
        _baseShape = _baseDat[0]
        _baseSize = _baseDat[1]
        
        mHandle = self._mTransform
        _bfr = mHandle.getMessage('orientHelper')
        if _bfr:
            mc.delete(_bfr)

        
        #Orientation helper ======================================================================================
        _orientHelper = CURVES.create_controlCurve(mHandle.mNode,'arrowSingle',  direction= shapeDirection, sizeMode = 'fixed', size = _baseSize * .75)
        mOrientCurve = cgmMeta.validateObjArg(_orientHelper, mType = 'cgmObject',setClass=True)
        
        mOrientCurve.doStore('cgmType','orientHandle')
        mOrientCurve.doName()    
        
        mOrientCurve.p_parent = mHandle
        
        for a,v in setAttrs.iteritems():
            ATTR.set(mOrientCurve.mNode, a, v)
            
        CORERIG.match_transform(mOrientCurve.mNode, mHandle)
        mOrientCurve.connectParentNode(mHandle.mNode,'handle','orientHelper')      

        return mOrientCurve
    
    
    def addJointHelper(self,baseShape=None, baseSize = None, shapeDirection = 'z-'):
        _baseDat = self.get_baseDat(baseShape,baseSize)
        _baseShape = _baseDat[0]
        _baseSize = _baseDat[1]
        
        mHandle = self._mTransform
        _bfr = mHandle.getMessage('jointHelper')
        if _bfr:
            mc.delete(_bfr)

        
        #Joint helper ======================================================================================
        _jointHelper = CURVES.create_controlCurve(mHandle.mNode,'sphere',  direction= shapeDirection, sizeMode = 'fixed', size = _baseSize)
        mJointCurve = cgmMeta.validateObjArg(_jointHelper, mType = 'cgmObject',setClass=True)
        
        mJointCurve.doStore('cgmType','jointHandle')
        mJointCurve.doName()    
        
        mJointCurve.p_parent = mHandle
        
       
        CORERIG.match_transform(mJointCurve.mNode, mHandle)
        
        #mc.transformLimits(mJointCurve.mNode, tx = (-.5,.5), ty = (-.5,.5), tz = (-.5,.5),
        #                   etx = (True,True), ety = (True,True), etz = (True,True))        

        mJointCurve.connectParentNode(mHandle.mNode,'handle','jointHelper')   
        
        mJointCurve.setAttrFlags(['rotate','scale'])
        
        #...loft curve -------------------------------------------------------------------------------------
        mLoft = self.buildBaseShape('square',_baseSize*.5,'y+')
        mLoft.doStore('cgmName',mJointCurve.mNode)
        mLoft.doStore('cgmType','loftCurve')
        mLoft.doName()
        mLoft.p_parent = mJointCurve
        self.color(mLoft.mNode,controlType='sub')
        
        for s in mLoft.getShapes(asMeta=True):
            s.overrideEnabled = 1
            s.overrideDisplayType = 2
        mLoft.connectParentNode(mJointCurve,'handle','loftCurve')        
        

        return mJointCurve
        
        
    def rebuildAsLoftTarget(self, baseShape = None, baseSize = None, shapeDirection = 'z+', rebuildHandle = True):
        _baseDat = self.get_baseDat(baseShape,baseSize)
        _baseShape = _baseDat[0]
        _baseSize = _baseDat[1]   
        

        if baseShape is not 'self':
            if rebuildHandle:
                self.cleanShapes()      
                _offsetSize = _baseSize * 1.3
                _dist = _baseSize *.05
                _mShapeDirection = VALID.simpleAxis(shapeDirection)     
                
                for i,p in enumerate(['upper','lower']):
                    mCrv = self.buildBaseShape(_baseShape,_offsetSize,shapeDirection)
                    if i == 0:
                        _pos = self._mTransform.getPositionByAxisDistance(_mShapeDirection.p_string,_dist)
                    else:
                        _pos = self._mTransform.getPositionByAxisDistance(_mShapeDirection.p_string,-_dist)
                        
                    mCrv.p_position = _pos
                    CORERIG.shapeParent_in_place(self._mTransform.mNode,mCrv.mNode,False)
                
                    self.color(self._mTransform.mNode)
            
            #>>>make our loft curve
            mCrv = self.buildBaseShape(_baseShape,_baseSize,shapeDirection)
            mCrv.doStore('cgmName',self._mTransform.mNode)
            mCrv.doStore('cgmType','loftCurve')
            mCrv.doName()
            mCrv.p_parent = self._mTransform
            self.color(mCrv.mNode,controlType='sub')
            
            for s in mCrv.getShapes(asMeta=True):
                s.overrideEnabled = 1
                s.overrideDisplayType = 2
            mCrv.connectParentNode(self._mTransform,'handle','loftCurve')            
            
            return mCrv
        
        else:
            _baseSize = DIST.get_createSize(self._mTransform.getShapes()[0])
            _baseShape = 'self'
            
            _offsetSize = _baseSize * 1.3
            _dist = _baseSize *.05
            _mShapeDirection = VALID.simpleAxis(shapeDirection)               
 
            mBaseCrv = self.buildBaseShape('self',_offsetSize,shapeDirection)
            
            #>>> make our offset shapes to control our handle
            for i,p in enumerate(['upper','lower']):
                mCrv = mBaseCrv.doDuplicate(po=False)
                if baseShape == 'self':
                    #mc.scale(_offsetSize,_offsetSize,_offsetSize, mCrv.mNode, absolute = True)
                    #mc.xform(mCrv.mNode, scale = [_baseSize,_baseSize,_baseSize], worldSpace = True, relative = True)
                    mCrv.scale = [1.25,1.25,1.25]
                if i == 0:
                    _pos = self._mTransform.getPositionByAxisDistance(_mShapeDirection.p_string,_dist)
                else:
                    _pos = self._mTransform.getPositionByAxisDistance(_mShapeDirection.p_string,-_dist)
                    
                mCrv.p_position = _pos
                CORERIG.shapeParent_in_place(self._mTransform.mNode,mCrv.mNode,False)
                
            self.color(self._mTransform.mNode)
            
            #>>>make our loft curve
            mCrv = mBaseCrv
            mCrv.doStore('cgmName',self._mTransform.mNode)
            mCrv.doStore('cgmType','loftCurve')
            mCrv.doName()
            mCrv.p_parent = self._mTransform
            self.color(mCrv.mNode,controlType='sub')
            
            for s in mCrv.getShapes(asMeta=True):
                s.overrideEnabled = 1
                s.overrideDisplayType = 2
            mCrv.connectParentNode(self._mTransform,'handle','loftCurve')
                
            return mCrv
            
            
            
            
class cgmRigBlockHandle(cgmMeta.cgmControl):
    def __init__(self, node = None, baseShape = None,  baseSize = 1, shapeDirection = 'z+',
                 aimDirection = 'z+', upDirection = 'y+',
                 rigBlock = None, *args,**kws):
        """ 

        """
        _str_func = "cgmRigBlockHandle.__init__"   
        
        if node is None:
            if baseShape is None:
                raise ValueError,"|{0}| >> Must have either a node or a baseShape specified.".format(_str_func)
            
        #>>Verify or Initialize
        super(cgmRigBlockHandle, self).__init__(node = node, name = baseShape, nodeType = 'transform') 

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
        self._callKWS = kws
        

        #>>> Initialization Procedure ================== 
        if self.__justCreatedState__ or _doVerify:
            log.debug("|{0}| >> Just created or do verify...".format(_str_func))            
            if self.isReferenced():
                log.error("|{0}| >> Cannot verify referenced nodes".format(_str_func))
                return
            elif not self.verify(baseShape, baseSize, shapeDirection):
                raise RuntimeError,"|{0}| >> Failed to verify: {1}".format(_str_func,self.mNode)
            
    def verify(self, baseShape = None, baseSize = None, shapeDirection = 'z+'):
        self.cleanShapes()
        
        if baseShape is None:
            baseShape = 'square'
        self.addAttr('baseShape', baseShape,attrType='string')
        
        SNAP.verify_aimAttrs(self.mNode, aim = 'z+', up = 'y+')
        
        if baseSize is not None:
            self.doStore('baseSize',baseSize)
        
        _baseSize = self.baseSize
        
        _baseShape = self.getMayaAttr('baseShape') 
        #_crv = CURVES.create_fromName(_baseShape, _baseSize, shapeDirection)
        #TRANS.snap(_crv, self.mNode)
        mCrv = self.buildBaseShape(_baseShape,_baseSize,shapeDirection)
        CORERIG.shapeParent_in_place(self.mNode,mCrv.mNode,False)
        
        # CURVES.create_fromName('square', color = 'yellow', direction = 'y+', sizeMode = 'fixed', size = _size * .5)
        
        self.color()
        
        self.doStore('cgmType','blockHandle')
        self.doName()
        return True
    
    def cleanShapes(self):
        if self.getShapes():
            mc.delete(self.getShapes())     
            
        for link in ['loftShape']:
            _buffer = self.getMessage(link)
            if _buffer:
                mc.delete(_buffer)
                
            
    def getBaseCreateSize(self):
        _maxLossy = max(self.getScaleLossy())
        _baseSize = self.baseSize * _maxLossy    
        return _baseSize
    
    def color(self, target = None, side = None, controlType = None):
        if self.getMessage('rigBlock'):
            pass
        else:
            _side = 'center'
            _controlType = 'main'
            
        if target is None:
            target = self.mNode
        CORERIG.colorControl(target,_side,_controlType,transparent = True)
            
    def template(self):
        #...build loftCurve, wire
        self.verify()
        pass
    
    def buildBaseShape(self, baseShape = None, baseSize = None, shapeDirection = 'z+' ):
        if baseSize is not None:
            self.doStore('baseSize',baseSize)
            
        _baseSize = self.baseSize
        
        _baseShape = self.getMayaAttr('baseShape') 
        _crv = CURVES.create_fromName(_baseShape, _baseSize, shapeDirection)
        TRANS.snap(_crv, self.mNode) 
        mCrv = cgmMeta.validateObjArg(_crv)
        
        #...lossy
        _lossy = self.getScaleLossy()
        mCrv.scaleX = mCrv.scaleX * _lossy[0]
        mCrv.scaleY = mCrv.scaleY * _lossy[1]
        mCrv.scaleZ = mCrv.scaleZ * _lossy[2]

        return mCrv
    
    def rebuildAsLoftTarget(self, baseShape = 'square', baseSize = None, shapeDirection = 'z+'):
        self.cleanShapes()      
        
        if baseSize is None:
            _baseSize = self.baseSize        
        else:
            _baseSize = baseSize      
        
        _offsetSize = _baseSize + 1.1
        _dist = self.baseSize *.01
        _baseShape = self.getMayaAttr('baseShape')
        _mShapeDirection = VALID.simpleAxis(shapeDirection)
        
        #>>> make our offset shapes to control our handle
        for i,p in enumerate(['upper','lower']):
            mCrv = self.buildBaseShape(_baseShape,_offsetSize,shapeDirection)
            if i == 0:
                _pos = self.getPositionByAxisDistance(_mShapeDirection.p_string,_dist)
            else:
                _pos = self.getPositionByAxisDistance(_mShapeDirection.p_string,-_dist)
                
            mCrv.p_position = _pos
            CORERIG.shapeParent_in_place(self.mNode,mCrv.mNode,False)
            
        #>>>make our loft curve
        mCrv = self.buildBaseShape(_baseShape,_baseSize,shapeDirection)
        mCrv.doStore('cgmName',self.mNode)
        mCrv.doStore('cgmType','loftCurve')
        mCrv.doName()
        mCrv.p_parent = self
        self.color(mCrv.mNode,controlType='sub')
        
        for s in mCrv.getShapes(asMeta=True):
            s.overrideEnabled = 1
            s.overrideDisplayType = 2
        mCrv.connectParentNode(self,'handle','loftShape')
        
        


#====================================================================================	
# Factories
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
            cgmGEN.walk_dat(kws,_str_func)
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

        cgmGEN.walk_dat(_d,_str_func + " '{0}' attributes to verify".format(blockType))
        cgmGEN.walk_dat(d_defaultSettings,_str_func + " '{0}' defaults".format(blockType))

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
        _mBlock = self._mi_block
        if _blockType not in _d.keys():
            log.error("|{0}| >> [{1}] | Failed to query type. Probably not a module".format(_str_func,_blockType))        
            return False        

        _mod = _d.get(_blockType,False)
        
        _short = self._mi_block.p_nameShort
        
        _res = []
        
        #_res.append("{0} : {1}".format('blockType',_blockType))
        #_res.append("{0} : {1}".format('blockState',ATTR.get(_short,'blockState')))
        
        _res.append("blockParent : {0}".format(_mBlock.getBlockParent(False)))
        _res.append("blockChildren : {0}".format(len(_mBlock.getBlockChildren(False))))
        for msg in 'blockMirror','moduleTarget':
            _res.append("{0} : {1}".format(msg,ATTR.get(_short,msg)))          
        _res.append("skeletonized : {0}".format(_mBlock.isSkeletonized()))
        #_res.append("blockChildren : {0}".format(_mBlock.getBlockChildren(False)))
        
        _res.append("       version: {0}".format(ATTR.get(_short,'version')))
        _res.append("module version: {0}".format(_mod.__version__))
        
        for a in 'side','position':
            if ATTR.get(_short,a):
                _res.append("{0} : {1}".format(a,ATTR.get_enumValueString(_short,a)))
        
            
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
        elif _targetsMode == 'msg':
            _l_targets = ATTR.get_message(_root, _targetsCall)
        elif _targetsMode == 'self':
            _l_targets = [self._mi_block.mNode]
        else:
            raise ValueError,"targetsMode: {0} is not implemented".format(_targetsMode)

        log.debug("|{0}| >> Targets: {1}".format(_str_func,_l_targets))            

        _helperOrient = ATTR.get_message(_root,'orientHelper')
        if not _helperOrient:
            log.info("|{0}| >> No helper orient. Using root.".format(_str_func))   
            _axisWorldUp = MATH.get_obj_vector(_root,'y+')                 
        else:
            log.info("|{0}| >> orientHelper: {1}".format(_str_func,_helperOrient))            
            _axisWorldUp = MATH.get_obj_vector(_helperOrient[0], _d_skeletonSetup.get('helperAxis','y+')) 
            
        log.debug("|{0}| >> axisWorldUp: {1}".format(_str_func,_axisWorldUp))  

        _joints = ATTR.get(_root,'numberJoints')


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
            _d_res['helpers'] = {'orient':_helperOrient,
                                 'targets':_l_targets}
        elif _mode == 'handle':
            _l_pos = [POS.get(_l_targets[0])]
            _d_res['targets'] = _l_targets           
        else:
            raise ValueError,"mode: {0} is not implemented".format(_mode)                

        _d_res['positions'] = _l_pos
        _d_res['mode'] = _mode
        _d_res['worldUpAxis'] = _axisWorldUp        
        
        #pprint.pprint(_d_res)
        return _d_res

    def verify(self, blockType = None, forceReset = False):
        """
        Verify a given loaded root object as a given blockType

        :parameters:
            blockType(str) | rigBlock type
            forceReset(bool) | Push default attrs to the ribBlock

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
            try:
                v = self._d_attrToVerifyDefaults.get(a,None)
                t = self._d_attrsToVerify[a]
                
                log.debug("|{0}| Add attr >> '{1}' | defaultValue: {2} ".format(_str_func,a,v,blockType)) 
                
                if ':' in t:
                    if forceReset:
                        _mBlock.addAttr(a, v, attrType = 'enum', enumName= t, keyable = False)		                        
                    else:
                        _mBlock.addAttr(a,initialValue = v, attrType = 'enum', enumName= t, keyable = False)		    
                elif t == 'stringDatList':
                    mc.select(cl=True)
                    ATTR.datList_connect(_mBlock.mNode, a, v, mode='string')
                else:
                    if t == 'string':
                        _l = True
                    else:_l = False
                    
                    if forceReset:
                        _mBlock.addAttr(a, v, attrType = t,lock=_l, keyable = False)                                
                    else:
                        _mBlock.addAttr(a,initialValue = v, attrType = t,lock=_l, keyable = False)            
            except Exception,err:
                log.error("|{0}| Add attr Failure >> '{1}' | defaultValue: {2} ".format(_str_func,a,v,blockType)) 
                if not forceReset:                
                    raise Exception,err
                
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
        _l_moduleStates = BLOCKSHARE._l_blockStates
        
        if not stateArgs:
            return False
    
        _idx_target = stateArgs[0]
        _state_target = stateArgs[1]
        
        log.debug("|{0}| >> Target state: {1} | {2}".format(_str_func,_state_target,_idx_target))
        
        #>>> Meat
        #========================================================================
        currentState = _mBlock.getState(False) 
        
        if currentState == _idx_target and rebuildFrom is None and not forceNew:
            if not forceNew:
                log.debug("|{0}| >> block [{1}] already in {2} state".format(_str_func,_mBlock.mNode,currentState))                
            return True
        
        
        #If we're here, we're going to move through the set states till we get to our spot
        
        log.debug("|{0}| >> Changing states...".format(_str_func))
        if _idx_target > currentState:
            startState = currentState+1        
            doStates = _l_moduleStates[startState:_idx_target+1]
            log.debug("|{0}| >> Going up. First stop: {1} | All stops: {2}".format(_str_func, _l_moduleStates[startState],doStates))
            
            for doState in doStates:
                #if doState in d_upStateFunctions.keys():
                log.debug("|{0}| >> Up to: {1} ....".format(_str_func, doState))
                if not d_upStateFunctions[doState]():
                    log.error("|{0}| >> Failed: {1} ....".format(_str_func, doState))
                    return False
                elif _mBlock.p_blockState != doState:
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
                if not d_downStateFunctions[doState]():
                    log.error("|{0}| >> Failed: {1} ....".format(_str_func, doState))
                    return False 
                elif _mBlock.p_blockState != doState:
                    log.error("|{0}| >> No errors but failed to query as:  {1} ....".format(_str_func, doState))                    
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
            log.debug("|{0}| >> BlockModule call found...".format(_str_func))            
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
            log.error("{0} is not in template state. state: {1}".format(_str_func, _str_state))
        
        
        #>>>Children ------------------------------------------------------------------------------------
        
        
        #>>>Meat ------------------------------------------------------------------------------------
        _mBlock.blockState = 'template>define'        
        
        _mBlockModule = get_blockModule(_mBlock.blockType)
        _mBlockCall = False
        
        if _mBlock.getMessage('templateNull'):
            _mBlock.templateNull.delete()
        
        if 'templateDelete' in _mBlockModule.__dict__.keys():
            log.debug("|{0}| >> BlockModule templateDelete call found...".format(_str_func))            
            _mBlockCall = _mBlockModule.templateDelete    
            _mBlockCall(_mBlock)
            
        if 'define' in _mBlockModule.__dict__.keys():
            log.debug("|{0}| >> BlockModule define call found...".format(_str_func))            
            _mBlockCall = _mBlockModule.define   
            _mBlockCall(_mBlock)
            
        #Delete our shapes...
        mc.delete(_mBlock.getShapes())
            
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
            log.debug("|{0}| >> BlockModule prerig call found...".format(_str_func))            
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
            log.debug("|{0}| >> BlockModule prerigDelete call found...".format(_str_func))            
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
            log.debug("|{0}| >> BlockModule rig call found...".format(_str_func))            
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
            log.debug("|{0}| >> BlockModule rigDelete call found...".format(_str_func))            
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
             
        log.debug("|{0}| >> [{1}] |...".format(_str_func,_short))
        
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
        
        cgmGEN.walk_dat(_res, "Block Data [{0}]".format(_short))
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
            log.debug("|{0}| >> [{1}] | Block children...".format(_str_func,_short))            
            for mChild in _ml_blockChildren:
                mChild.p_blockParent = False

        _blockDat = _mBlock.getBlockDat()
        _mBlock.rename(_short + '_OLD')
        
        #Create New
        _mBlockNEW = self.create_rigBlock(_blockType)
        _short = _mBlockNEW.p_nameShort
        
        _mBlockNEW.p_blockDat = _blockDat
        
        #Reattach Children
        if _ml_blockChildren:
            log.debug("|{0}| >> [{1}] | reconnecting children...".format(_str_func,_short))            
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
        
        #>> If check for module,puppet -----------------------------------------------------------------------------------
        if not self._mi_module:
            self.module_verify()
        if not self._mi_puppet:
            self.puppet_verify()

        #>> If skeletons there, delete ----------------------------------------------------------------------------------- 
        _bfr = self._mi_module.rigNull.msgList_get('moduleJoints')
        if _bfr:
            log.debug("|{0}| >> Joints detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in _bfr])
            else:
                return _bfr
            
        # If our block odule has a call use that
        _mod = get_modules_dict().get(_blockType,False)
        if not _mod:
            log.warning("|{0}| >> No module found for: {1}".format(_str_func,blockType))
            return False  
        if _mod.__dict__.get('build_skeleton'):
            log.info("|{0}| >> Found build_skeletonc call in module. Using...".format(_str_func))            
            return _mod.build_skeleton(self._mi_block)
            
        return False
        #>> Get positions -----------------------------------------------------------------------------------
        _d_create = self.get_skeletonCreateDict(_blockType)
        _mode = _d_create['mode']
            
        #Build skeleton -----------------------------------------------------------------------------------
        _ml_joints = BUILDERUTILS.build_skeleton(_d_create['positions'],worldUpAxis=_d_create['worldUpAxis'])
        
        if _mode == 'handle':
            for i,mJnt in enumerate(_ml_joints):
                mJnt.doSnapTo(_d_create['targets'][i])
                JOINTS.metaFreezeJointOrientation(mJnt.mNode)
                

        #...need to do this better...
        
        #>>>HANDLES,CORENAMES -----------------------------------------------------------------------------------
        _ml_joints[0].addAttr('cgmName',_blockType)
        if len(_ml_joints) > 1:
            for i,mJnt in enumerate(_ml_joints):
                mJnt.addAttr('cgmIterator',i)
                mJnt.doName()                
        else:
            _ml_joints[0].doName()

        #Wire and name        
        self._mi_module.rigNull.msgList_connect('moduleJoints',_ml_joints)
        
        #>>>Connect to parent module/puppet
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
                log.debug(_root)
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
        str_side = None
        if _mBlock.hasAttr('side'):
            str_side = _mBlock.getEnumValueString('side')
        log.debug("|{0}| >> side: {1}".format(_str_func,str_side))            
        if str_side in ['left','right']:
            d_kws['side'] = str_side
        #Position
        str_position = None
        if _mBlock.hasAttr('position'):
            str_position = _mBlock.getEnumValueString('position')	
        log.debug("|{0}| >> position: {1}".format(_str_func,str_position))            
        if str_position != 'none':
            d_kws['position'] = str_position

        cgmGEN.walk_dat(d_kws,"{0} d_kws".format(_str_func))
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
                            log.warning("|{0}| >> Module failed: {1}".format(_str_func,key))                               
                            for arg in e.args:
                                log.error(arg)
                                          
                    else:
                        _l_duplicates.append("{0} >> {1} ".format(key, os.path.join(root,f)))
            _i+=1
            
    if _b_debug:
        cgmGEN.walk_dat(_d_modules,"Modules")        
        cgmGEN.walk_dat(_d_files,"Files")
        cgmGEN.walk_dat(_d_import,"Imports")
        cgmGEN.walk_dat(_d_categories,"Categories")
    
    if _l_duplicates and _b_debug:
        log.debug(cgmGEN._str_subLine)
        log.debug("|{0}| >> DUPLICATE MODULES....".format(_str_func))
        for m in _l_duplicates:
            print(m)
        raise Exception,"Must resolve"
    log.debug("|{0}| >> Found {1} modules under: {2}".format(_str_func,len(_d_files.keys()),_path))     
    if _l_unbuildable and _b_debug:
        log.debug(cgmGEN._str_subLine)
        log.debug("|{0}| >> ({1}) Unbuildable modules....".format(_str_func,len(_l_unbuildable)))
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
    for a in BLOCKSHARE._l_requiredModuleDat:
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
    
    for a in BLOCKSHARE._l_requiredModuleDat:
        if a not in _keys:
            log.warning("|{0}| >> [{1}] Missing data: {2}".format(_str_func,_blockType,a))
            _res = False
            
    if _res:return _buildModule
    return _res


_l_requiredModuleDat = ['__version__',
                        'template','is_template','templateDelete',
                        'prerig','is_prerig','prerigDelete',
                        'rig','is_rig','rigDelete']

_d_requiredModuleDat = {'define':['__version__'],
                        'template':['template','is_template','templateDelete'],
                        'prerig':['prerig','is_prerig','prerigDelete'],
                        'rig':['rig','is_rig','rigDelete']}


def get_blockModule_status2(blockType):
    """
    Function to check if a given blockType  is defineable, prerigable
    
    """      
    _str_func = 'get_blockModule_status'
    _res = {}
    
    _buildModule = get_blockModule(blockType)
    if not _buildModule:
        return False    
    
    for state in ['define','template','prerig','rig']:
        l_tests = _d_requiredModuleDat[state]
        _good = True
        for test in l_tests:
            if not getattr(_buildModule, test, False):
                log.warning("|{0}| >> [{1}] Missing data: {2}".format(_str_func,_blockType,a))
                _good = False  
        _res[state] = _good
        
        if state == 'define':
            print("|{0}| >> [{1}] version: {2}".format(_str_func,_blockType,_buildModule.get('__version__',False)))            
        
    return _res
    
def get_blockModule_status(blockModule, state = None):
    """
    Function to check if a blockModule is buildable by state or given a state if that one is okay
    
    """
    _str_func = 'get_blockModule_status'  
    
    #_buildModule = _d_blockTypes[blockType]
    
    if VALID.stringArg(blockModule):
        _buildModule = get_blockModule(blockModule)
    
    else:
        _buildModule = blockModule
        
    try:
        _blockType = _buildModule.__name__.split('.')[-1]
    except:
        log.error("|{0}| >> [{1}] | Failed to query name. Probably not a module".format(_str_func,_buildModule))        
        return False
    
    if state is None:
        _res = {}        
        for state in ['define','template','prerig','rig']:
            l_tests = _d_requiredModuleDat[state]
            _good = True
            print("|{0}| >> [{1}]{2}".format(_str_func,_blockType,state) + cgmGEN._str_subLine)            
            for test in l_tests:
                if not getattr(_buildModule, test, False):
                    print("|{0}| >> [{1}] {2}: Fail".format(_str_func,_blockType,test))
                    _good = False  
                else:
                    print("|{0}| >> [{1}] {2}: Pass".format(_str_func,_blockType,test))                    
            _res[state] = _good
            
            if state == 'define':
                print("|{0}| >> [{1}] version: {2}".format(_str_func,_blockType,_buildModule.__dict__.get('__version__',False)))            
    
    else:
        l_tests = _d_requiredModuleDat[state]
        _res = True
        for test in l_tests:
            if not getattr(_buildModule, test, False):
                print("|{0}| >> [{1}] Missing {3} data: {2}".format(_str_func,_blockType,test,state))
                _res = False   
                
        if state == 'define':
            print("|{0}| >> [{1}] version: {2}".format(_str_func,_blockType,_buildModule.__dict__.get('__version__',False)))                    
        
    return _res
    
    """
    _keys = _buildModule.__dict__.keys()
    _l_missing = []
    for a in BLOCKSHARE._l_requiredModuleDat:
        if a not in _keys:
            _l_missing.append(a)
            _res = False
            
    if _l_missing:
        log.warning("|{0}| >> [{1}] Missing data...".format(_str_func,_blockType))
        for i,a in enumerate(_l_missing):
            log.warning("|{0}| >> {1} : {2}".format(_str_func,i,a))  """
            
    #if _res:return _buildModule
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

#========================================================================================================     
#>>> Contextual call 
#========================================================================================================
def contextual_method_call(mBlock, context = 'self', func = 'getShortName',*args,**kws):
    """
    Function to contextually call a series of rigBlocks and run a methodCall on them with 
    args and kws
        
    :parameters:
        mBlock(str): rigBlock starting point
        context(str): self,below,root,scene
        func(str): string of the method call to use. mBlock.getShortName(), is just 'getShortName'
        *args,**kws - pass through for method call

    :returns
        list of results(list)
    """
    _str_func = 'contextual_method_call'
    
    if func == 'VISUALIZEHEIRARCHY':
        BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,context,False,True)
        return True
    _l_context = BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,context,True,False)
    _res = []
    
    if not args:
        args = []
        
    if not kws:
        kws = {}
        _kwString = None  
    else:
        _l = []
        for k,v in kws.iteritems():
            _l.append("{0}={1}".format(k,v))
        _kwString = ','.join(_l)

    if not _l_context:
        log.error("|{0}| >> No data in context".format(_str_func,))
        return False
    
    if func in ['select']:
        mc.select([mBlock.mNode for mBlock in _l_context])
        return
    
    for mBlock in _l_context:
        _short = mBlock.p_nameShort
        try:
            log.debug("|{0}| >> On: {1}".format(_str_func,_short))            
            res = getattr(mBlock,func)(*args,**kws) or None
            print("|{0}| >> {1}.{2}({3},{4}) = {5}".format(_str_func,_short,func,','.join(a for a in args),_kwString, res))                        
            _res.append(res)
        except Exception,err:
            log.error(cgmGEN._str_hardLine)
            log.error("|{0}| >> Failure: {1}".format(_str_func, err.__class__))
            log.error("block: {0} | func: {1}".format(_short,func))            
            if args:
                log.error("Args...")
                for a in args:
                    log.error("      {0}".format(a))
            if kws:
                log.error(" KWS...".format(_str_func))
                for k,v in kws.iteritems():
                    log.error("      {0} : {1}".format(k,v))   
            log.error("Errors...")
            for a in err.args:
                log.error(a)
            _res.append('ERROR')
            log.error(cgmGEN._str_subLine)
    
    return _res



class rigFactory(object):
    def __init__(self, rigBlock = None, forceNew = True, autoBuild = False, ignoreRigCheck = False,
                 *a,**kws):
        """
        Core rig block builder factory

        :parameters:
            rigBlock(str) | base rigBlock

        :returns
            factory instance

        """
        _str_func = 'rigFactory._init_'
        _start = time.clock()

        #>>Initial call ---------------------------------------------------------------------------------
        self.callBlock = None
        self.call_kws = {}
        self.mBlock = None
        self.d_block = {}
        self.d_module = {}
        self.d_joints = {}
        self.d_orientation = {}         
        self.md_controlShapes = {} 

        if a:log.debug("|{0}| >> a: {1}".format(_str_func,a))
        if kws:#...intial population
            self.call_kws = kws
            #log.debug("|{0}| >> kws: {1}".format(_str_func,kws))

        self.call_kws['forceNew'] = forceNew
        self.call_kws['rigBlock'] = rigBlock
        self.call_kws['autoBuild'] = autoBuild
        self.call_kws['ignoreRigCheck'] = ignoreRigCheck
        cgmGEN.log_info_dict(self.call_kws,_str_func)

        if not self.fnc_check_rigBlock():
            raise RuntimeError,"|{0}| >> RigBlock checks failed. See warnings and errors.".format(_str_func)
        log.debug("|{0}| >> RigBlock check passed".format(_str_func) + cgmGEN._str_subLine)

        if not self.fnc_check_module():
            raise RuntimeError,"|{0}| >> Module checks failed. See warnings and errors.".format(_str_func)
        log.debug("|{0}| >> Module check passed...".format(_str_func)+ cgmGEN._str_subLine)

        if not self.fnc_rigNeed():
            raise RuntimeError,"|{0}| >> No rig need see errors".format(_str_func)
        log.debug("|{0}| >> Rig needed...".format(_str_func)+ cgmGEN._str_subLine)

        if not self.fnc_bufferDat():
            raise RuntimeError,"|{0}| >> Failed to buffer data. See warnings and errors.".format(_str_func)

        if not self.fnc_moduleRigChecks():
            raise RuntimeError,"|{0}| >> Failed to process module rig Checks. See warnings and errors.".format(_str_func)

        if not self.fnc_deformConstrainNulls():
            raise RuntimeError,"|{0}| >> Failed to process deform/constrain. See warnings and errors.".format(_str_func)
                
        self.fnc_processBuild(**kws)
        
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                

        #_verify = kws.get('verify',False)
        #log.debug("|{0}| >> verify: {1}".format(_str_func,_verify))

    def __repr__(self):
        try:return "{0}(rigBlock: {1})".format(self.__class__, self.mBlock.mNode)
        except:return self
    
    def log_self(self):
        pprint.pprint(self.__dict__)
        
    def atBlockModule(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        _blockModule = self.d_block['buildModule']
        
        return cgmGEN.stringModuleClassCall(self, _blockModule, func, *args, **kws)
        
    def fnc_connect_toRigGutsVis(self, ml_objects, vis = True, doShapes = False):
        _str_func = 'fnc_connect_toRigGutsVis' 
        mRigNull = self.d_module['mRigNull']
        
        if type(ml_objects) not in [list,tuple]:ml_objects = [ml_objects]
        for mObj in ml_objects:
            if doShapes:
                for mShp in mObj.getShapes(asMeta=True):
                    mShp.overrideEnabled = 1		
                    if vis: cgmMeta.cgmAttr(mRigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mShp.mNode,'overrideVisibility'))
                    cgmMeta.cgmAttr(mRigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mShp.mNode,'overrideDisplayType'))    
            else:
                mObj.overrideEnabled = 1		
                if vis: cgmMeta.cgmAttr(mRigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(mRigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideDisplayType'))    

    def fnc_check_rigBlock(self):
        """
        Check the rig block data 
        """
        _str_func = 'fnc_check_rigBlock' 
        _d = {}
        _res = True
        _start = time.clock()

        if not self.call_kws['rigBlock']:
            log.error("|{0}| >> No rigBlock stored in call kws".format(_str_func))
            return False

        BlockFactory = factory(self.call_kws['rigBlock'])
        BlockFactory.verify()

        _d['mBlock'] = BlockFactory._mi_block
        self.mBlock = _d['mBlock']
        _d['mFactory'] = BlockFactory
        _d['shortName'] = BlockFactory._mi_block.getShortName()

        _blockType = _d['mBlock'].blockType

        _buildModule = get_blockModule(_blockType)

        if not _buildModule:
            log.error("|{0}| >> No build module found for: {1}".format(_str_func,_d['mBlock'].blockType))        
            return False
        _d['buildModule'] =  _buildModule   #if not is_buildable
        _d['buildVersion'] = _buildModule.__version__

        self.d_block = _d    
        #cgmGEN.log_info_dict(_d,_str_func + " blockDat")   
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
        self.buildModule = _buildModule
        return True


    def fnc_check_module(self):
        _str_func = 'fnc_check_module'  
        _res = True
        BlockFactory = self.d_block['mFactory']

        if BlockFactory._mi_block.blockType in ['master']:
            return True

        _start = time.clock()

        #>>Module -----------------------------------------------------------------------------------  
        _d = {}    
        BlockFactory.module_verify()
        _mModule = BlockFactory._mi_module
        self.mModule = _mModule

        _mRigNull = _mModule.rigNull
        _d['mModule'] = _mModule
        _d['mRigNull'] = _mRigNull
        self.mRigNull = _mRigNull
        _d['shortName'] = _mModule.getShortName()
        _d['version'] = _mModule.rigNull.version

        _d['mModuleParent'] = False
        if _mModule.getMessage('moduleParent'):
            _d['mModuleParent'] = _mModule.moduleParent

        """
        if not _mRigNull.getMessage('dynSwitch'):
            _mDynSwitch = RIGMETA.cgmDynamicSwitch(dynOwner=_mRigNull.mNode)
            log.debug("|{0}| >> Created dynSwitch: {1}".format(_str_func,_mDynSwitch))        
        else:
            _mDynSwitch = _mRigNull.dynSwitch  
        _d['mDynSwitch'] = _mDynSwitch"""

        #>>Puppet -----------------------------------------------------------------------------------    
        BlockFactory.puppet_verify()
        _mPuppet = _mModule.modulePuppet
        self.mPuppet = _mPuppet

        _d['mPuppet'] = _mPuppet
        _mPuppet.__verifyGroups__()

        if not _mModule.isSkeletonized():
            log.warning("|{0}| >> Module isn't skeletonized. Attempting".format(_str_func))
            
            self.d_block['mBlock'].atBlockModule('build_skeleton')

            if not _mModule.isSkeletonized():
                log.warning("|{0}| >> Skeletonization failed".format(_str_func))            
                _res = False

        self.d_module = _d    
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
        #cgmGEN.log_info_dict(_d,_str_func + " moduleDat")    
        return _res    


    def fnc_moduleRigChecks(self):
        """
        Verify the module's rig visibility toggles and object set
        """
        _str_func = 'fnc_moduleRigChecks'  
        _res = True
        _start = time.clock()


        #>>Connect switches ----------------------------------------------------------------------------------- 
        _str_settings = self.d_module['mMasterSettings'].getShortName()
        _str_partBase = self.d_module['partName'] + '_rig'
        _str_moduleRigNull = self.d_module['mRigNull'].getShortName()

        _mMasterSettings = self.d_module['mMasterSettings']

        _mMasterSettings.addAttr(_str_partBase,enumName = 'off:lock:on', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)

        try:NODEFAC.argsToNodes("{0}.gutsVis = if {1}.{2} > 0".format(_str_moduleRigNull,
                                                                      _str_settings,
                                                                      _str_partBase)).doBuild()
        except Exception,err:
            raise Exception,"|{0}| >> visArg failed [{1}]".format(_str_func,err)

        try:NODEFAC.argsToNodes("{0}.gutsLock = if {1}.{2} == 2:0 else 2".format(_str_moduleRigNull,
                                                                                 _str_settings,
                                                                                 _str_partBase)).doBuild()
        except Exception,err:
            raise Exception,"|{0}| >> lock arg failed [{1}]".format(_str_func,err)

        self.d_module['mRigNull'].overrideEnabled = 1		
        cgmMeta.cgmAttr(_str_moduleRigNull,'gutsVis',lock=False).doConnectOut("%s.%s"%(_str_moduleRigNull,'overrideVisibility'))
        cgmMeta.cgmAttr(_str_moduleRigNull,'gutsLock',lock=False).doConnectOut("%s.%s"%(_str_moduleRigNull,'overrideDisplayType'))    

        #log.debug("%s >> Time >> = %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)   


        #>>> Object Set -----------------------------------------------------------------------------------
        self.mModule.__verifyObjectSet__()

        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))            

        return _res

    def fnc_rigNeed(self):
        """
        Function to check if a go instance needs to be rigged

        """
        _str_func = 'fnc_rigNeed'  


        _mModule = self.d_module['mModule']    
        _mModuleParent = self.d_module['mModuleParent']
        _version = self.d_module['version']
        _buildVersion = self.d_block['buildVersion']

        _d_callKWS = self.call_kws

        if _mModuleParent:
            _str_moduleParent = _mModuleParent.getShortName()
            if not _mModuleParent.isRigged():
                log.warning("|{0}| >> [{1}] ModuleParent not rigged".format(_str_func,_str_moduleParent))            
                return False

        _b_rigged = _mModule.isRigged()
        log.debug("|{0}| >> Rigged: {1}".format(_str_func,_b_rigged))            

        if _b_rigged and not _d_callKWS['forceNew'] and _d_callKWS['ignoreRigCheck'] is not True:
            log.warning("|{0}| >> Already rigged and not forceNew".format(_str_func))                    
            return False

        self.b_outOfDate = False
        if _version != _buildVersion:
            self.b_outOfDate = True
            log.warning("|{0}| >> Versions don't match: rigNull: {1} | buildModule: {2}".format(_str_func,_version,_buildVersion))                            
        else:
            if _d_callKWS['forceNew'] and _mModule.isRigged():
                log.warning("|{0}| >> Force new and is rigged. Deleting rig...".format(_str_func))                    
                #_mModule.rigDelete()
            else:
                log.info("|{0}| >> Up to date.".format(_str_func))                    
                return False

        return True

    def fnc_atModule(self,func = '',*args,**kws):
        _str_func = 'fnc_atModule'
        _res = None
        _short = self.d_block['mBlock'].mNode
        _module = self.d_block['buildModule']
        if not args:
            _str_args = ''
            args = [self]
        else:
            _str_args = ','.join(str(a) for a in args) + ','
            args = [self] + [a for a in args]
            
        if not kws:
            kws = {}
            _kwString = ''  
        else:
            _l = []
            for k,v in kws.iteritems():
                _l.append("{0}={1}".format(k,v))
            _kwString = ','.join(_l)  
            
        try:
            log.debug("|{0}| >> {1}.{2}({3}{4})...".format(_str_func,_short,func,_str_args,_kwString))                                    
            _res = getattr(_module,func)(*args,**kws)
        except Exception,err:
            log.error(cgmGEN._str_hardLine)
            log.error("|{0}| >> Failure: {1}".format(_str_func, err.__class__))
            log.error("rigBlock: {0} | func: {1}".format(_short,func))
            log.error("Module: {0} ".format(_module))            
            
            if args:
                log.error("Args...")
                for a in args:
                    log.error("      {0}".format(a))
            if kws:
                log.error(" KWS...".format(_str_func))
                for k,v in kws.iteritems():
                    log.error("      {0} : {1}".format(k,v))   
            log.error("Errors...")
            for a in err.args:
                log.error(a)
            cgmGEN.cgmExceptCB(Exception,err)
            
            #cgmGEN.log_info_dict(self.__dict__,'rigFactory')
            
            raise Exception,err
        return _res     
    
    def log_self(self):
        pprint.pprint(self.__dict__)
        
    def fnc_bufferDat(self):
        """
        Function to check if a go instance needs to be rigged

        """
        _str_func = 'fnc_bufferDat'  

        _mModule = self.d_module['mModule']    
        _mModuleParent = self.d_module['mModuleParent']
        _mPuppet = self.d_module['mPuppet']
        _mRigNull = self.d_module['mRigNull']
        _version = self.d_module['version']
        _buildVersion = self.d_block['buildVersion']

        _d_callKWS = self.call_kws

        #>>Module dat ------------------------------------------------------------------------------
        _d = {}
        _d['partName'] = _mModule.getPartNameBase()
        _d['partType'] = _mModule.moduleType.lower() or False

        _d['l_moduleColors'] = _mModule.getModuleColors() 
        _d['l_coreNames'] = []#...need to do this
        self.mTemplateNull = _mModule.templateNull
        _d['mTemplateNull'] = self.mTemplateNull
        _d['bodyGeo'] = _mPuppet.getGeo() or ['Morphy_Body_GEO']
        _d['direction'] = _mModule.getAttr('cgmDirection')

        _d['mirrorDirection'] = _mModule.get_mirrorSideAsString()
        _d['f_skinOffset'] = _mPuppet.getAttr('skinDepth') or 1
        _d['mMasterNull'] = _mPuppet.masterNull

        #>MasterControl....
        if not _mPuppet.getMessage('masterControl'):
            log.info("|{0}| >> Creating masterControl...".format(_str_func))                    
            _mPuppet._verifyMasterControl(size = 5)

        _d['mMasterControl'] = _mPuppet.masterControl
        _d['mPlug_globalScale'] =  cgmMeta.cgmAttr(_d['mMasterControl'].mNode,'scaleY')	 
        _d['mMasterSettings'] = _d['mMasterControl'].controlSettings
        _d['mMasterDeformGroup'] = _mPuppet.masterNull.deformGroup

        _d['mMasterNull'].worldSpaceObjectsGroup.parent = _mPuppet.masterControl

        self.d_module.update(_d)

        #cgmGEN.log_info_dict(self._d_module,_str_func + " moduleDat")      
        log.info(cgmGEN._str_subLine)


        #>>Joint dat ------------------------------------------------------------------------------
        _d = {}

        _d['ml_moduleJoints'] = _mRigNull.msgList_get('moduleJoints',cull=True)
        if not _d['ml_moduleJoints']:
            log.warning("|{0}| >> No module joints found".format(_str_func))                    
            return False

        _d['l_moduleJoints'] = []

        for mJnt in _d['ml_moduleJoints']:
            _d['l_moduleJoints'].append(mJnt.p_nameShort)
            ATTR.set(mJnt.mNode,'displayLocalAxis',0)

        _d['ml_skinJoints'] = _mModule.rig_getSkinJoints()
        if not _d['ml_skinJoints']:
            log.warning("|{0}| >> No skin joints found".format(_str_func))                    
            return False      


        self.d_joints = _d
        #cgmGEN.log_info_dict(self.d_joints,_str_func + " jointsDat")      
        #log.info(cgmGEN._str_subLine)    

        #>>Orientation dat ------------------------------------------------------------------------------
        _d = {}

        _mOrientation = VALID.simpleOrientation('zyx')#cgmValid.simpleOrientation(str(modules.returnSettingsData('jointOrientation')) or 'zyx')
        _d['str'] = _mOrientation.p_string
        _d['vectorAim'] = _mOrientation.p_aim.p_vector
        _d['vectorUp'] = _mOrientation.p_up.p_vector
        _d['vectorOut'] = _mOrientation.p_out.p_vector

        _d['vectorAimNeg'] = _mOrientation.p_aimNegative.p_vector
        _d['vectorUpNeg'] = _mOrientation.p_upNegative.p_vector
        _d['vectorOutNeg'] = _mOrientation.p_outNegative.p_vector    

        self.d_orientation = _d
        #cgmGEN.log_info_dict(self.d_orientation,_str_func + " orientationDat")      
        #log.info(cgmGEN._str_subLine)    

        return True



    def fnc_deformConstrainNulls(self):
        """
        Verify the module's rig visibility toggles and object set
        """
        _str_func = 'fnc_deformConstrainNulls'  
        _res = True
        _start = time.clock()


        #>>Connect switches ----------------------------------------------------------------------------------- 
        _str_partType = self.d_module['partType']
        _str_partName= self.d_module['partName']

        _mMasterSettings = self.d_module['mMasterSettings']
        _mi_moduleParent = self.d_module['mModuleParent']
        _ml_skinJoints = self.d_joints['ml_skinJoints']

        if not self.mModule.getMessage('deformNull'):
            if _str_partType in ['eyebrow', 'mouthnose']:
                raise ValueError,"not implemented"
                """
                #Make it and link it ------------------------------------------------------
                buffer = rigging.groupMeObject(self.str_faceAttachJoint,False)
                i_grp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
                i_grp.addAttr('cgmName',self.partName,lock=True)
                i_grp.addAttr('cgmTypeModifier','deform',lock=True)	 
                i_grp.doName()
                i_grp.parent = self.i_faceDeformNull	
                self.mModule.connectChildNode(i_grp,'deformNull','module')
                self.mModule.connectChildNode(i_grp,'constrainNull','module')
                self.i_deformNull = i_grp#link"""
            else:
                #Make it and link it
                if _str_partType in ['eyelids']:
                    buffer =  CORERIG.group_me(_mi_moduleParent.deformNull.mNode,False)			
                else:
                    buffer =  CORERIG.group_me(_ml_skinJoints[0].mNode,False)

                i_grp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
                i_grp.addAttr('cgmName',_str_partName,lock=True)
                i_grp.addAttr('cgmTypeModifier','deform',lock=True)	 
                i_grp.doName()
                i_grp.parent = self.d_module['mMasterDeformGroup'].mNode
                self.mModule.connectChildNode(i_grp,'deformNull','module')
                if _str_partType in ['eyeball']:
                    self.mModule.connectChildNode(i_grp,'constrainNull','module')	
                    i_grp.parent = self.i_faceDeformNull				
        self.mDeformNull = self.mModule.deformNull


        if not self.mModule.getMessage('constrainNull'):
            #if _str_partType not in __l_faceModules__ or _str_partType in ['eyelids']:
                #Make it and link it
            buffer =  CORERIG.group_me(self.mDeformNull.mNode,False)
            i_grp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
            i_grp.addAttr('cgmName',_str_partName,lock=True)
            i_grp.addAttr('cgmTypeModifier','constrain',lock=True)	 
            i_grp.doName()
            i_grp.parent = self.mDeformNull.mNode
            self.mModule.connectChildNode(i_grp,'constrainNull','module')
        self.mConstrainNull = self.mModule.constrainNull

        #>> Roll joint check...
        self.b_noRollMode = False
        self.b_addMidTwist = True
        if self.mBlock.hasAttr('rollJoints'):
            if self.mBlock.rollJoints == 0:
                self.b_noRollMode = True
                self.b_addMidTwist = False
                log.info("|{0}| >> No rollJoint mode...".format(_str_func))                    


        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))            

        return _res

    def fnc_processBuild(self,**kws):
        """
        Verify the module's rig visibility toggles and object set
        """
        _str_func = 'fnc_processBuild'  
        _start = time.clock()

        if self.b_outOfDate and self.call_kws['autoBuild']:
            self.doBuild(**kws)
        else:log.error("|{0}| >> No autobuild condition met...".format(_str_func))                    


        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))            

    def doBuild(self,buildTo = '',**kws):
        _str_func = 'doBuild'  
        _start = time.clock()        

        try:
            _l_buildOrder = self.d_block['buildModule'].__l_buildOrder__
            _len = len(_l_buildOrder)

            if not _len:
                log.error("|{0}| >> No steps to build!".format(_str_func))                    
                return False
            #Build our progress Bar
            mayaMainProgressBar = CGMUI.doStartMayaProgressBar(_len)

            for i,fnc in enumerate(_l_buildOrder):
                try:	
                    #str_name = d_build[k].get('name','noName')
                    #func_current = d_build[k].get('function')
                    #_str_subFunc = str_name
                    _str_subFunc = fnc.__name__

                    mc.progressBar(mayaMainProgressBar, edit=True,
                                   status = "|{0}| >>Rigging>> step: {1}...".format(_str_func,_str_subFunc), progress=i+1)    
                    fnc(self)

                    if buildTo is not None:
                        _Break = False
                        if VALID.stringArg(buildTo):
                            if buildTo.lower() == _str_subFunc:
                                _Break = True
                        elif buildTo == i:
                            _Break = True

                        if _Break:
                            log.debug("|{0}| >> Stopped at step: [{1}]".format(_str_func, _str_subFunc))   
                            break
                except Exception,err:
                    raise Exception,"Fail step: {0} | err: [{1}]".format(fnc.__name__,err)  

            CGMUI.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
        except Exception,err:
            CGMUI.doEndMayaProgressBar()#Close out this progress bar    		
            raise Exception,"|{0}| >> err: {1}".format(_str_func,err)        

    def build_rigJoints(self):
        _str_func = 'build_rigJoints'  
        _res = True
        _start = time.clock()

        _ml_skinJoints = self.d_joints['ml_skinJoints']

        #>>Check if exists -----------------------------------------------------------------------------------  
        l_rigJointsExist = self.mRigNull.msgList_get('rigJoints',asMeta = False, cull = True)
        if l_rigJointsExist:
            log.warning("|{0}| >> Deleting existing chain!".format(_str_func))                    
            mc.delete(l_rigJointsExist)

        #>>Build -----------------------------------------------------------------------------------          
        l_rigJoints = mc.duplicate([i_jnt.mNode for i_jnt in _ml_skinJoints],po=True,ic=True,rc=True)
        ml_rigJoints = [cgmMeta.cgmObject(j) for j in l_rigJoints]

        for i,mJnt in enumerate(ml_rigJoints):
            mJnt.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
            l_rigJoints[i] = mJnt.mNode
            mJnt.connectChildNode(_ml_skinJoints[i],'skinJoint','rigJoint')#Connect	    
            if mJnt.hasAttr('scaleJoint'):
                if mJnt.scaleJoint in self.ml_skinJoints:
                    int_index = self.ml_skinJoints.index(mJnt.scaleJoint)
                    mJnt.connectChildNode(l_rigJoints[int_index],'scaleJoint','sourceJoint')#Connect
            if mJnt.hasAttr('rigJoint'):mJnt.doRemove('rigJoint')
            mJnt.doName()

        ml_rigJoints[0].parent = False

        #>>Connect back -----------------------------------------------------------------------------------                  
        self.d_joints['ml_rigJoints'] = ml_rigJoints
        self.d_joints['l_rigJoints'] = [i_jnt.p_nameShort for i_jnt in ml_rigJoints]
        self.mRigNull.msgList_connect(ml_rigJoints,'rigJoints','rigNull')#connect	


        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
        return ml_rigJoints






#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================    
r9Meta.registerMClassInheritanceMapping()#Pushes our classes in
    
    
    
    
    
    
    






