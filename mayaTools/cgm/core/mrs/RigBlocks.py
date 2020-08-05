"""
------------------------------------------
RigBlocks: cgm.core.mrs
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__MAYALOCAL = 'RIGBLOCKS'

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
import cgm.core.lib.shape_utils as SHAPES
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
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.puppet_utils as PUPPETUTILS
import cgm.core.mrs.lib.module_utils as MODULEUTILS
import cgm.core.rig.general_utils as RIGGEN
from cgm.core.classes import GuiFactory as cgmUI
import cgm.core.mrs.lib.blockShapes_utils as BLOCKSHAPES
from cgm.core.lib import nameTools
from cgm.core.classes import GuiFactory as CGMUI
import cgm.core.tools.lib.snap_calls as SNAPCALLS
get_from_scene = BLOCKGEN.get_from_scene



#_d_blockTypes = {'box':box}

#====================================================================================	
# Rig Block Meta
#====================================================================================	
d_attrstoMake = BLOCKSHARE.d_defaultAttrs
d_defaultAttrSettings = BLOCKSHARE.d_defaultAttrSettings

def get_callSize(mode = None, arg = None, blockType = None, blockProfile = None, default = [1,1,1]):
    """
    Get size for block creation by mode

    :parameters:
        arg(str/list): Object(s) to check
        mode(varied): 
            selection - bounding box of only shapes of obj
            boundingBox - full child bounding box
            None - if blockModule, checks for default size
            default - failsafe

    :returns
        boundingBox size(list)
    """  
    try:
        _str_func = 'get_callSize'
        
        def floatValues(arg):
            return [float(MATH.Clamp(v,.1,None)) for v in arg]
        _sel = mc.ls(sl=True)

        if mode in [None,'default']:
            log.debug("|{0}| >>  mode is None...".format(_str_func))
            if not arg:
                log.debug("|{0}| >>  no arg...".format(_str_func))                
                if blockType:
                    blockModule = get_blockModule(blockType)
                    if blockProfile:
                        try:
                            log.debug("|{0}| >> checking block profile...".format(_str_func))                
                            _profileValues = blockModule.d_block_profiles.get(blockProfile,{})
                            return floatValues(_profileValues['baseSize'])
                        except:pass
                    try:
                        log.debug("|{0}| >> checking defaultSettings...".format(_str_func))
                        _profileValues = blockModule.d_defaultSettings                                
                        return floatValues(_profileValues['baseSize'])
                    except:pass
                    log.debug("|{0}| >> __baseSize__...".format(_str_func))
                    return floatValues(getattr(blockModule, '__baseSize__', default))
                return floatValues(default)
            else:
                mode = 'bb'
                #arg = arg[0]

        if arg is None and mode is None:
            if not _sel:
                raise ValueError,"|{0}| >> No obj arg and no selection".format(_str_func)
            arg = _sel[0]

    
        if mode in ['selection','bb']:
            arg =  _sel
            #if mode == 'selection':
            if not arg:
                raise ValueError,"|{0}| >> No obj arg and no selection".format(_str_func)
            
        #Checking mode for values, strings and the like --------------------------------------------------
        if VALID.valueArg(mode):
            return floatValues([mode,mode,mode])
        elif VALID.objString(mode,noneValid=True):
            arg = mode
            mode = 'selection'
            
        if VALID.isListArg(mode):
            if len(mode)==3:
                _valueList = True
                for v in mode:
                    if VALID.valueArg(v) is False:
                        log.info("|{0}| >> Invalid value arg: {1}".format(_str_func,v))                
                        _valueList = False
                        break
                    
                if _valueList:
                    return floatValues(mode)
                
            arg = VALID.objStringList(mode)
            mode = 'selection'
        
            
        mode = mode.lower()
        size = None
        if mode == 'selection':
            if VALID.isListArg(arg):
                size = POS.get_bb_size(arg, False)
            else:
                size = POS.get_axisBox_size(arg,True)
            #if rigBlock:
                #log.info("|{0}| >>  Created from obj. Tagging. | {1}".format(_str_func,arg))        
                #rigBlock.connectChildNode(arg,'sourceObj')#Connect
        elif mode in ['boundingbox','bb']:
            size = POS.get_bb_size(arg, False)
        else:
            size = 1,1,1
        
        if not size:
            raise ValueError,"No size found"
        
        _res = floatValues(size)
        
        log.info("|{0}| >>  mode: {1} | arg: '{2}' | size: {3}".format(_str_func,mode,arg,_res))        
        return _res
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())

class cgmRigBlock(cgmMeta.cgmControl):
    #These lists should be set up per rigblock as a way to get controls from message links
    _l_controlLinks = []
    _l_controlmsgLists = []

    def __init__(self, node = None, blockType = None, blockParent = None, autoForm = True, *args,**kws):
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

        #if blockType and not is_buildable(blockType):
            #log.warning("|{0}| >> Unbuildable blockType specified".format(_str_func))

        #Only check this with a no node call for speed
        _callSize = None
        _sel = None
        _size = kws.get('size',None)
        _side =  kws.get('side')
        _baseSize = kws.get('baseSize')
        _sizeMode = None
        _postState = None#...for sizeMode call
        _doVerify = kws.get('doVerify',False)
        _justCreated = False
        kw_name = kws.get('name',None)
        
        if node is None:
            _sel = mc.ls(sl=1)            
            _callSize = get_callSize(_size,blockProfile=kws.get('blockProfile'),blockType=blockType)
            _doVerify = True
            _justCreated = True
            if  _sel:
                pos_target = TRANS.position_get(_sel[0])
                log.debug("|{0}| >> pos_target: {1}".format(_str_func,pos_target))                                
                if pos_target[0] >= .05:
                    _side = 'left'
                elif pos_target[0] <= -.05:
                    _side = 'right'            


        #>>Verify or Initialize
        super(cgmRigBlock, self).__init__(node = node, name = blockType) 
        log.debug("|{0}| >> size: {1}".format(_str_func, _callSize))

        #====================================================================================	
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            log.debug('CACHE : Aborting __init__ on pre-cached {0} Object'.format(self))
            return
        #====================================================================================	
        #for a in 'p_blockState','testinasdfasdfasdf':
            #if a not in self.UNMANAGED:
                #self.UNMANAGED.append(a) 	

        
        #====================================================================================
        #Keywords - need to set after the super call
        #=====================================================================================         
        #self._factory = factory(self.mNode)
        self._callKWS = kws
        self._blockModule = None
        self._callSize = _callSize
        #self.UNMANAGED.extend(['kw_name','kw_moduleParent','kw_forceNew','kw_initializeOnly','kw_callNameTags'])	
        #>>> Initialization Procedure ================== 
        if _doVerify:
            if blockType:
                _blockModule =  get_blockModule(blockType)
                reload(_blockModule)
                self.doStore('blockType',blockType,attrType='string')
            else:
                _blockModule = False
            
            kw_blockProfile = kws.get('blockProfile',None)
            if self.__justCreatedState__:
                self.addAttr('blockType', value = blockType,lock=True)
                if kw_blockProfile and kw_name is None:
                    kw_name = kw_blockProfile
                elif blockType is not None and not kw_name:
                    kw_name = blockType
                else:
                    kw_name = 'NAMEME'
                self.addAttr('cgmName', kws.get('name', kw_name))
            else:
                self.addAttr('cgmName',attrType='string')
                if kw_name:
                    self.cgmName = kw_name
                    

            log.debug("|{0}| >> Just created or do verify...".format(_str_func))            
            if self.isReferenced():
                log.error("|{0}| >> Cannot verify referenced nodes".format(_str_func))
                return
            elif not self.verify(blockType,side= _side):
                raise RuntimeError,"|{0}| >> Failed to verify: {1}".format(_str_func,self.mNode)

            #Name -----------------------------------------------

            #On call attrs -------------------------------------------------------------------------
            for a,v in kws.iteritems():
                if self.hasAttr(a):
                    try:
                        if a == 'side' and v == None:
                            v = 0
                        log.debug("|{0}| On call set attr  >> '{1}' | value: {2}".format(_str_func,a,v))
                        ATTR.set(self.mNode,a,v)
                    except Exception,err:
                        log.error("|{0}| On call set attr Failure >> '{1}' | value: {2} | err: {3}".format(_str_func,a,v,err)) 
            
            #Profiles --------------------------------------------------------------------------
            
            _kw_buildProfile = kws.get('buildProfile')
            if _kw_buildProfile:
                self.UTILS.buildProfile_load(self, _kw_buildProfile)
                
            _kw_blockProfile = kws.get('blockProfile')
            if _kw_blockProfile:
                self.UTILS.blockProfile_load(self, kws.get('blockProfile',_kw_blockProfile))                
            
            #>>>Auto flags...
            if not _blockModule:
                _blockModule =  get_blockModule(self.blockType)                    
                
            #Size -----------------------------------------------------
            _sizeMode = _blockModule.__dict__.get('__sizeMode__',None)
            
            #if _sizeMode:
                #log.debug("|{0}| >> Sizing: {1}...".format(_str_func, _sizeMode))
                #self.atUtils('doSize', _sizeMode)

            #Snap with selection mode --------------------------------------
            if _size in ['selection']:
                log.info("|{0}| >> Selection mode snap...".format(_str_func))                      
                if _sel:
                    if  blockType in ['master']:
                        SNAPCALLS.snap(self.mNode,_sel[0],rotation=False,targetPivot='groundPos')
                    else:
                        log.info("|{0}| >> Selection mode snap to: {1}".format(_str_func,_sel))
                        SNAPCALLS.snap(self.mNode, _sel[0],targetPivot='bb',targetMode='center')
                        #self.doSnapTo(_sel[0])
            #cgmGEN.func_snapShot(vars())
            
            self._blockModule = _blockModule
            
            if _justCreated:
                if _baseSize:
                    log.info("|{0}| >> on call base size: {1}".format(_str_func,_baseSize))
                    self.baseSize = _baseSize
                if 'define' in _blockModule.__dict__.keys():
                    log.debug("|{0}| >> BlockModule define call found...".format(_str_func))            
                    _blockModule.define(self)
                    
                try:BLOCKUTILS.attrMask_getBaseMask(self)
                except Exception,err:
                    log.info(cgmGEN.logString_msg(_str_func,'attrMask fail | {0}'.format(err)))

                self.doName()
            
            #Form -------------------------------------------------
            if autoForm and _blockModule.__dict__.get('__autoForm__'):
                log.debug("|{0}| >> AutoForm...".format(_str_func))
                if _sizeMode:
                    _postState = 'form'
        
                else:
                    self.p_blockState = 'form'
        else:log.debug("|{0}| >> No verify...".format(_str_func))
            
        if blockParent is not None:
            try:
                self.p_blockParent = blockParent
            except Exception,err:
                log.warning("|{0}| >> blockParent on call failure.".format(_str_func))
                for arg in err.args:
                    log.error(arg)
                        
                #if _sizeMode:
                    #log.debug("|{0}| >> Sizing: {1}...".format(_str_func, _sizeMode))
                    #self.atUtils('doSize', _sizeMode, postState = _postState )                

        #except Exception,err:
        #    #pprint.pprint(vars())
        #    log.error("|{0}| >> Failed to initialize properly! ".format(_str_func) + '='*80)
        #    cgmGEN.cgmException(Exception,err)
        #    #cgmGEN.cgmExceptCB(Exception,err,msg=vars())

        #self._blockModule = get_blockModule(ATTR.get(self.mNode,'blockType'))        

    def verify(self, blockType = None, size = None, side = None,forceReset=False):
        """ 

        """
        return self.UTILS.verify(self,blockType,size,side,forceReset)

    def doName(self):
        return self.atUtils('doName')
    
    def query_blockModuleByType(self,*args,**kws):
        return get_blockModule(*args,**kws)


    def getControls(self, asMeta = False):
        """
        Function which MUST be overloaded
        """	
        return self.atUtils('controls_get')
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
        self.atUtils('blockParent_set', parent, attachPoint)

    p_blockParent = property(getBlockParent,setBlockParent)

    def getBlockChildrenAll(self,asMeta=True):
        ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(self,'below',True,False)
        if not asMeta:
            return [mObj.mNode for mObj in ml_context]
        return ml_context
        
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

    def getBlockDat_formControls(self,report = False):
        _short = self.p_nameShort        
        _str_func = '[{0}] getBlockDat_formControls'.format(_short)

        _blockState_int = self.blockState

        if not _blockState_int:
            raise ValueError,'[{0}] not formd yet'.format(_short)
            #_ml_formHandles = self.msgList_get('formHandles',asMeta = True)
        _ml_formHandles = self.atUtils('controls_get',True,False)
            
        if not _ml_formHandles:
            log.error('[{0}] No form or prerig handles found'.format(_short))
            return False

        _ml_controls = [self] + _ml_formHandles

        _l_orientHelpers = []
        _l_jointHelpers = []
        _d_orientHelpers = {}
        _d_jointHelpers = {}        
        for i,mObj in enumerate(_ml_formHandles):
            log.info("|{0}| >>  {1} | {2}".format(_str_func,i,mObj.mNode))
            if mObj.getMessage('orientHelper'):
                #_l_orientHelpers.append(mObj.orientHelper.rotate)
                _d_orientHelpers[i] = mObj.orientHelper.rotate
            #else:
                #_l_orientHelpers.append(False)
                
            if mObj.getMessage('jointHelper'):
                #_l_jointHelpers.append(mObj.jointHelper.translate)
                _d_jointHelpers[i] = mObj.jointHelper.translate
                
            #else:
                #_l_jointHelpers.append(False)
                
        _d = {'positions':[mObj.p_position for mObj in _ml_formHandles],
              'orientations':[mObj.p_orient for mObj in _ml_formHandles],
              'scales':[mObj.scale for mObj in _ml_formHandles],
              'jointHelpers':_d_jointHelpers,
              'orientHelpers':_d_orientHelpers}

        if self.getMessage('orientHelper'):
            _d['rootOrientHelper'] = self.orientHelper.rotate

        if report:cgmGEN.walk_dat(_d,'[{0}] form blockDat'.format(self.p_nameShort))
        return _d

    def getBlockDat_prerigControls(self,report = False):
        _short = self.p_nameShort        
        _str_func = '[{0}] getBlockDat_prerigControls'.format(_short)

        _ml_prerigHandles = self.msgList_get('prerigHandles',asMeta = True)
        #_ml_prerigHandles = self.atUtils('controls_get',False,True)
        
        if not _ml_prerigHandles:
            return False

        _ml_controls = [self] + _ml_prerigHandles

        _d_orientHelpers = {}
        _d_jointHelpers = {}

        for i,mObj in enumerate(_ml_prerigHandles):
            log.info("|{0}| >>  {1} | {2}".format(_str_func,i,mObj.mNode))
            if mObj.getMessage('orientHelper'):
                _d_orientHelpers[i] = mObj.orientHelper.rotate
            #else:
                #_l_orientHelpers.append(False)
            if mObj.getMessage('jointHelper'):
                _d_jointHelpers[i] = mObj.jointHelper.translate


        _d = {'positions':[mObj.p_position for mObj in _ml_prerigHandles],
              'orientations':[mObj.p_orient for mObj in _ml_prerigHandles],
              'scales':[mObj.scale for mObj in _ml_prerigHandles],
              'jointHelpers':_d_jointHelpers,
              'orientHelpers':_d_orientHelpers}

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

    def getBlockModule(self,update = False,reloadMod=False):
        def ret(mod,reloadMod=False):
            if reloadMod:
                reload(mod)
                log.info("Reloaded: {0}".format(mod))
            return mod
        
        if self._blockModule and  update:
            if self._blockModule:                
                return ret(self._blockModule,reloadMod)
            return ret(get_blockModule(self.getMayaAttr('blockType')), reloadMod)
        blockType = self.getMayaAttr('blockType')
        blockModule = get_blockModule(blockType)
        if not blockModule:
            raise ValueError,"No blockModule found. blockType: {0}".format(self.blockType)
        return ret(blockModule,reloadMod)

    try:p_blockModule = property(getBlockModule)
    except Exception,err:
        log.error("Failed to load block module. Check it. {0}".format(self))        
        log.error(err)
        
    def getBlockDat(self,report = False):
        """
        Carry from Bokser stuff...
        """
        return BLOCKUTILS.blockDat_get(self,report)

    def saveBlockDat(self):
        self.blockDat = self.getBlockDat(False)

    def resetBlockDat(self):
        #This needs more work.
        self.atUtils('verify_blockAttrs', forceReset=True) 

    def printBlockDat(self):
        cgmGEN.walk_dat(self.blockDat,'[{0}] blockDat'.format(self.p_nameShort))

    def loadBlockDat(self,*args,**kws):
        #reload(BLOCKUTILS)
        return BLOCKUTILS.blockDat_load(self,*args,**kws)
    
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
        
        
        #>>Form Controls ====================================================================================
        _int_state = self.getState(False)
        
        if _int_state > 0:
            log.info("|{0}| >> form dat....".format(_str_func))             
            _d_form = blockDat.get('form',False)
            if not _d_form:
                log.error("|{0}| >> No form data found in blockDat".format(_str_func)) 
            else:
                #if _int_state == 1:
                #_ml_formHandles = self.msgList_get('formHandles',asMeta = True)
                _ml_formHandles = self.atUtils('controls_get',True,False)
                #else:
                #_ml_formHandles = self.msgList_get('prerigHandles',asMeta = True)                


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
                        for i_loop in range(2):
                            log.info("|{0}| >> Loop: {1}".format(_str_func,i_loop))
                            
                            for i,mObj in enumerate(_ml_formHandles):
                                log.info ("|{0}| >> FormHandle: {1}".format(_str_func,mObj.mNode))
                                mObj.p_position = _posTempl[i]
                                mObj.p_orient = _orientsTempl[i]
                                _tmp_short = mObj.mNode
                                for ii,v in enumerate(_scaleTempl[i]):
                                    _a = 's'+'xyz'[ii]
                                    if not self.isAttrConnected(_a):
                                        ATTR.set(_tmp_short,_a,v)   
                                if _jointHelpers and _jointHelpers.get(i):
                                    mObj.jointHelper.translate = _jointHelpers[i]
                                
                if _d_form.get('rootOrientHelper'):
                    if self.getMessage('orientHelper'):
                        self.orientHelper.p_orient = _d_form.get('rootOrientHelper')
                    else:
                        log.error("|{0}| >> Found root orient Helper data but no orientHelper control".format(_str_func))
                        
        if _int_state > 1:
            log.info("|{0}| >> prerig dat....".format(_str_func))             
            _d_prerig = blockDat.get('prerig',False)
            if not _d_prerig:
                log.error("|{0}| >> No form data found in blockDat".format(_str_func)) 
            else:
                #if _int_state == 1:
                _ml_prerigControls = self.msgList_get('prerigHandles',asMeta = True)
                #_ml_prerigControls = self.atUtils('controls_get',True,False)
                #else:
                #_ml_formHandles = self.msgList_get('prerigHandles',asMeta = True)                


                #_ml_formHandles = self.msgList_get('formHandles',asMeta = True)
                if not _ml_prerigControls:
                    log.error("|{0}| >> No prerig handles found".format(_str_func))
                else:
                    _posPre = _d_prerig.get('positions')
                    _orientsPre = _d_prerig.get('orientations')
                    _scalePre = _d_prerig.get('scales')
                    _jointHelpersPre = _d_prerig.get('jointHelpers')

                    if len(_ml_prerigControls) != len(_posPre):
                        log.error("|{0}| >> Form handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( _ml_prerigControls),len(_posPre))) 
                    else:
                        for i_loop in range(2):
                            log.info("|{0}| >> Loop: {1}".format(_str_func,i_loop))
                            
                            for i,mObj in enumerate(_ml_prerigControls):
                                log.info ("|{0}| >> Prerig handle: {1}".format(_str_func,mObj.mNode))
                                mObj.p_position = _posPre[i]
                                mObj.p_orient = _orientsPre[i]
                                _tmp_short = mObj.mNode
                                for ii,v in enumerate(_scalePre[i]):
                                    _a = 's'+'xyz'[ii]
                                    if not self.isAttrConnected(_a):
                                        ATTR.set(_tmp_short,_a,v)   
                                if _jointHelpersPre and _jointHelpersPre.get(i):
                                    mObj.jointHelper.translate = _jointHelpersPre[i]
                                
                #if _d_prerig.get('rootOrientHelper'):
                    #if self.getMessage('orientHelper'):
                        #self.orientHelper.p_orient = _d_prerig.get('rootOrientHelper')
                    #else:
                        #log.error("|{0}| >> Found root orient Helper data but no orientHelper #control".format(_str_func))


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
    p_blockDat = property(getBlockDat,loadBlockDat)


    #==================================================================================================
    #>>> States 
    #==================================================================================================
    def rebuild(self,*args,**kws):
        raise NotImplementedError,"Not done"
        return self._factory.rebuild_rigBlock(*args,**kws)

    def getState(self, asString = True):
        return self.atUtils('getState',asString)
        

    def changeState(self, *args,**kws):
        _res = self.atUtils('changeState',*args,**kws)
        return _res

    p_blockState = property(getState,changeState)


    #================================================================================================
    #>>> Skeleton and Mesh generation 
    #================================================================================================
    """
    def isSkeletonized(self):
        _str_func = '[{0}] isSkeletonized'.format(self.p_nameShort)

        _blockModule = get_blockModule(self.blockType)

        _call = _blockModule.__dict__.get('is_skeletonized',False)
        if _call:
            log.debug("|{0}| >> blockModule check...".format(_str_func))                                
            return _call(self)

        mModule = self.moduleTarget
        if not mModule:
            log.debug("|{0}| >> No module target...".format(_str_func))                                            
            return False
            raise ValueError,"No moduleTarget connected"

        mRigNull = mModule.rigNull
        if not mRigNull:
            log.debug("|{0}| >> No rigNull...".format(_str_func))
            return False
            raise ValueError,"No rigNull connected"

        if mRigNull.msgList_get('moduleJoints'):
            return True
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
    """
    def delete(self):
        BLOCKUTILS.delete(self)
        
    def duplicate(self,uiPrompt=True):
        return BLOCKUTILS.duplicate(self,uiPrompt)
        
    def puppetMesh_create(self,*args,**kws):
        #reload(BLOCKUTILS)
        return BLOCKUTILS.puppetMesh_create(self,*args,**kws)
    def puppetMesh_delete(self,*args,**kws):
        #reload(BLOCKUTILS)
        return BLOCKUTILS.puppetMesh_delete(self,*args,**kws)

    #==============================================================================================
    #>>> Mirror 
    #==============================================================================================
    @staticmethod
    def MirrorBlock(rootBlock = None, mirrorBlock = None, reflectionVector = MATH.Vector3(1,0,0) ):
        try:
            '''Mirrors the form positions from the block to the mirrorBlock across the reflection vector transformed from the root block'''
            _str_func = 'MirrorBlock'
    
            if not rootBlock or not mirrorBlock:
                log.warning("|{0}| >> Must have rootBlock and mirror block".format(_str_func))                                            
                return
    
            if mirrorBlock.blockType != rootBlock.blockType:
                log.warning("|{0}| >> Blocktypes must match. | {1} != {2}".format(_str_func,block.blockType,mirrorBlock.blockType,))                                                        
                return
            
            rootTransform = rootBlock
            rootReflectionVector = TRANS.transformDirection(rootTransform,reflectionVector).normalized()
            #rootReflectionVector = rootTransform.formPositions[0].TransformDirection(reflectionVector).normalized()
            
            print("|{0}| >> Root: {1}".format(_str_func, rootTransform.p_nameShort))                                            
            
            
            if mirrorBlock:
                print ("|{0}| >> Target: {1} ...".format(_str_func, mirrorBlock.p_nameShort))
                
                _blockState = rootBlock.blockState
                _mirrorState = mirrorBlock.blockState
                if _blockState > _mirrorState or _blockState < _mirrorState:
                    print ("|{0}| >> root state greater. Matching root: {1} to mirror:{2}".format(_str_func, _blockState,_mirrorState))
                else:
                    print ("|{0}| >> blockStates match....".format(_str_func, mirrorBlock.p_nameShort))
                    
                #if rootBlock.blockState != BlockState.TEMPLATE or mirrorBlock.blockState != BlockState.TEMPLATE:
                    #print "Can only mirror blocks in Form state"
                    #return
                
                #cgmGEN.func_snapShot(vars())
                return
            
                currentFormObjects = block.formPositions
                formHeirarchyDict = {}
                for i,p in enumerate(currentFormObjects):
                    formHeirarchyDict[i] = p.fullPath.count('|')
    
                formObjectsSortedByHeirarchy = sorted(formHeirarchyDict.items(), key=operator.itemgetter(1))
    
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
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    @staticmethod
    def MirrorSelectedBlocks( reflectionVector = MATH.Vector3(1,0,0) ):
        '''Mirrors the form positions from the block to the mirrorBlock across the reflection vector transformed from the root block'''

        for blockName in mc.ls(sl=True):
            currentBlock = Block.LoadRigBlock( GetNodeType(blockName) )
            if currentBlock:
                Block.MirrorBlock(currentBlock)

    @staticmethod
    def MirrorBlockPush( block, reflectionVector = MATH.Vector3(1,0,0) ):
        '''Mirrors the given block to the corresponding block on the other side'''

        mirrorBlock = block.GetMirrorBlock()

        Block.MirrorBlock(block, mirrorBlock, reflectionVector)

    @staticmethod
    def MirrorBlockPull( block, reflectionVector = MATH.Vector3(1,0,0) ):
        '''Mirrors the given block using the mirrorBlock's form positions'''

        mirrorBlock = block.GetMirrorBlock()

        Block.MirrorBlock(mirrorBlock, block, reflectionVector)





    #========================================================================================================     
    #>>> Utilities 
    #========================================================================================================      
    def asHandleFactory(self,*a,**kws):
        if not kws.get('rigBlock'):
            kws['rigBlock'] = self
        return BLOCKSHAPES.handleFactory(*a,**kws)
    
    def asRigFactory(self,*a,**kws):
        return rigFactory(self,*a,**kws)    
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
        return contextual_rigBlock_method_call(self, context, func, *args, **kws)

    def atBlockModule(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        #try:
        _blockModule = self.p_blockModule
        #reload(_blockModule)
        return getattr(_blockModule,func)(self,*args,**kws)            
        #return self.stringModuleCall(_blockModule,func,*args, **kws)
        #except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    
    def atRigModule(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        #try:
        _str_func = 'atRigModule'
        if self.blockType in ['master']:
            log.debug("|{0}| >> ineligible blockType: {1}".format(_str_func, self.blockType))                 
            return False
        
        return self.moduleTarget.atUtils(func,*args,**kws)
        #except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
    def atRigPuppet(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        #try:
        _str_func = 'atRigPuppet'
        if self.blockType in ['master']:
            return self.moduleTarget.atUtils(func,*args,**kws)
        
        return self.moduleTarget.modulePuppet.atUtils(func,*args,**kws)
        #except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
    def atBlockUtils(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        #try:
        #reload(BLOCKUTILS)
        return getattr(BLOCKUTILS,func)(self,*args,**kws)
        #return self.stringModuleCall(BLOCKUTILS,func,*args, **kws)
        #except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
        
    atUtils = atBlockUtils
    UTILS = BLOCKUTILS


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
            """
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
            log.error(cgmGEN._str_subLine)"""
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        return res

        print res
        return res
    
    @cgmGEN.Timer
    def verify_proxyMesh(self, forceNew = True, puppetMeshMode = False):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        _str_func = 'verify_proxyMesh'        
        if self.getState() != 'rig':
            log.error("|{0}| >> Block must be rigged. {1}".format(_str_func, self.mNode))            
            return False
        if not 'build_proxyMesh' in self.p_blockModule.__dict__.keys():
            log.error("|{0}| >> [{1}] Block module lacks 'build_proxyMesh' call.".format(_str_func, self.blockType))                        
            return False
        
        return self.atBlockModule('build_proxyMesh', forceNew, puppetMeshMode = puppetMeshMode)
        #mRigFac = rigFactory(self, autoBuild = False)
        #return mRigFac.atBlockModule('build_proxyMesh', forceNew, puppetMeshMode = puppetMeshMode)
        
    @cgmGEN.Timer
    def proxyMesh_delete(self, forceNew = True, puppetMeshMode = False):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        _str_func = 'proxyMesh_delete'
        mModuleTarget = self.getMessageAsMeta('moduleTarget')
        if not mModuleTarget:
            return log.error( cgmGEN.logString_msg(_str_func,"No module target") )
        
        mRigNull = mModuleTarget.getMessageAsMeta('rigNull')
        if not mRigNull:
            return log.error( cgmGEN.logString_msg(_str_func,"No mRigNull") )
        
        _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
        if _bfr:
            log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
            mc.delete([mObj.mNode for mObj in _bfr])
            return True
            
        return False
    
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

    def form(self):
        #...build loftCurve, wire
        self.verify()
        pass

    def buildBaseShape(self, baseShape = None, baseSize = None, shapeDirection = 'z+' ):
        if baseSize is not None:
            self.doStore('baseSize',baseSize)

        _baseSize = self.baseSize

        _baseShape = self.getMayaAttr('baseShape') 
        _crv = CURVES.create_fromName(_baseShape, _baseSize, shapeDirection, baseSize=1.0)
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
        mCrv.doStore('cgmName',self)
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

        #cgmGEN.walk_dat(_d,_str_func + " '{0}' attributes to verify".format(blockType))
        #cgmGEN.walk_dat(d_defaultSettings,_str_func + " '{0}' defaults".format(blockType))

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
        _short = _mBlock.mNode
        if _mBlock.isReferenced():
            raise ValueError,"Referenced node. Cannot verify"

        if blockType == None:
            blockType = ATTR.get(_short,'blockType')
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
                    ATTR.datList_connect(_short, a, v, mode='string')
                elif t == 'float3':
                    if not _mBlock.hasAttr(a):
                        ATTR.add(_short, a, attrType='float3', keyable = True)
                        if v:ATTR.set(_short,a,v)
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
                cgmGEN.cgmExceptCB(Exception,err,msg=vars())
                if not forceReset:                
                    raise Exception,err

        _mBlock.addAttr('blockType', value = blockType,lock=True)	
        #_mBlock.blockState = 'base'

        return True
    #========================================================================================================     
    #>>> States 
    #========================================================================================================  

    def changeState(self, state = None, rebuildFrom = None, forceNew = False,**kws):
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
        d_upStateFunctions = {'form':self.form,
                              'prerig':self.prerig,
                              'rig':self.rig,
                              }
        d_downStateFunctions = {'define':self.formDelete,#deleteSizeInfo,
                                'form':self.prerigDelete,#deleteSkeleton,
                                'prerig':self.rigDelete,#rigDelete,
                                }
        d_deleteStateFunctions = {'form':self.formDelete,#deleteForm,#handle from factory now
                                  'prerig':self.prerigDelete,
                                  'rig':self.rigDelete,#rigDelete,
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
        currentState = _mBlock.getState(False) 

        if rebuildFrom:
            log.info("|{0}| >> Rebuid from: {1}".format(_str_func,rebuildFrom))


        if currentState == _idx_target:
            if not forceNew:
                log.info("|{0}| >> block [{1}] already in {2} state".format(_str_func,_mBlock.mNode,currentState))                
                return True
            elif currentState > 0:
                log.info("|{0}| >> Forcing new: {1}".format(_str_func,currentState))                
                currentState_target = _mBlock.getState(True) 
                d_deleteStateFunctions[currentState_target]()

        #If we're here, we're going to move through the set states till we get to our spot
        log.debug("|{0}| >> Changing states...".format(_str_func))
        if _idx_target > currentState:
            startState = currentState+1        
            doStates = _l_moduleStates[startState:_idx_target+1]
            log.debug("|{0}| >> Going up. First stop: {1} | All stops: {2}".format(_str_func, _l_moduleStates[startState],doStates))

            for doState in doStates:
                #if doState in d_upStateFunctions.keys():
                log.debug("|{0}| >> Up to: {1} ....".format(_str_func, doState))
                if not d_upStateFunctions[doState](**kws):
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
                if not d_downStateFunctions[doState](**kws):
                    log.error("|{0}| >> Failed: {1} ....".format(_str_func, doState))
                    return False 
                elif _mBlock.p_blockState != doState:
                    log.error("|{0}| >> No errors but failed to query as:  {1} ....".format(_str_func, doState))                    
                    return False                
            return True
        else:
            log.error('Forcing recreate')
            if _state_target in d_upStateFunctions.keys():
                if not d_upStateFunctions[_state_target]():return False
                return True	            

    def form(self):
        if self._mi_block is None:
            raise ValueError,"No root loaded."
        _mBlock = self._mi_block

        if _mBlock.isReferenced():
            raise ValueError,"Referenced node."

        _str_func = '[{0}] factory.form'.format(_mBlock.p_nameBase)

        _str_state = _mBlock.getEnumValueString('blockState')
        

        if _str_state != 'define':
            raise ValueError,"{0} is not in define state. state: {1}".format(_str_func, _str_state)

        #>>>Children ------------------------------------------------------------------------------------


        #>>>Meat ------------------------------------------------------------------------------------
        #_mBlock.blockState = 'define>form'#...buffering that we're in process

        _mBlockModule = get_blockModule(_mBlock.blockType)

        if 'form' in _mBlockModule.__dict__.keys():
            log.debug("|{0}| >> BlockModule call found...".format(_str_func))            
            _mBlockModule.form(_mBlock)

        for mShape in _mBlock.getShapes(asMeta=True):
            mShape.doName()

        _mBlock.blockState = 'form'#...yes now in this state
        return True


    def formDelete(self):
        if self._mi_block is None:
            raise ValueError,"No root loaded."
        _mBlock = self._mi_block

        if _mBlock.isReferenced():
            raise ValueError,"Referenced node."

        _str_func = '[{0}] factory.formDelete'.format(_mBlock.p_nameBase)


        _str_state = _mBlock.getEnumValueString('blockState')

        if _str_state != 'form':
            log.error("{0} is not in form state. state: {1}".format(_str_func, _str_state))


        #>>>Children ------------------------------------------------------------------------------------


        #>>>Meat ------------------------------------------------------------------------------------
        #_mBlock.blockState = 'form>define'        

        _mBlockModule = get_blockModule(_mBlock.blockType)
        _mBlockCall = False

        if _mBlock.getMessage('formNull'):
            _mBlock.formNull.delete()

        if 'formDelete' in _mBlockModule.__dict__.keys():
            log.debug("|{0}| >> BlockModule formDelete call found...".format(_str_func))            
            _mBlockCall = _mBlockModule.formDelete    
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

        if _mBlock.blockState != 'form':
            raise ValueError,"{0} is not in form state. state: {1}".format(_str_func, _str_state)

        #>>>Children ------------------------------------------------------------------------------------


        #>>>Meat ------------------------------------------------------------------------------------
        #_mBlock.blockState = 'form>prerig'#...buffering that we're in process

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
        _str_state = _mBlock.getEnumValueString('blockState')

        if _str_state != 'prerig':
            raise ValueError,"{0} is not in prerig state. state: {1}".format(_str_func, _str_state)


        #>>>Children ------------------------------------------------------------------------------------


        #>>>Meat ------------------------------------------------------------------------------------        
        _mBlock.blockState = 'prerig>form'        

        _mBlockModule = get_blockModule(_mBlock.blockType)
        _mBlockCall = False
        if 'prerigDelete' in _mBlockModule.__dict__.keys():
            log.debug("|{0}| >> BlockModule prerigDelete call found...".format(_str_func))            
            _mBlockCall = _mBlockModule.prerigDelete    


        if _mBlockCall:
            _mBlockCall(_mBlock)

        _mBlock.blockState = 'form'

        return True

    def rig(self,**kws):
        #Master control
        if self._mi_block is None:
            raise ValueError,"No root loaded."
        _mBlock = self._mi_block
        _short = _mBlock.mNode
        if _mBlock.isReferenced():
            raise ValueError,"Referenced node."

        _str_func = '[{0}] factory.rig'.format(_mBlock.p_nameBase)
        _str_state = _mBlock.getEnumValueString('blockState')


        if _str_state != 'prerig':
            raise ValueError,"{0} is not in prerig state. state: {1}".format(_str_func, _str_state)      

        #>>>Children ------------------------------------------------------------------------------------


        #>>>Meat ------------------------------------------------------------------------------------
        #_mBlock.blockState = 'prerig>rig'#...buffering that we're in process
        _BlockModule= _mBlock.p_blockModule


        rigFactory(_mBlock,autoBuild=True,**kws)

        #cgmRigBlock(_short).blockState = 'rig'
        #_mBlock.blockState = 'rig'#...yes now in this state
        return True

    def rigDelete(self):
        if self._mi_block is None:
            raise ValueError,"No root loaded."
        _mBlock = self._mi_block

        if _mBlock.isReferenced():
            raise ValueError,"Referenced node."

        _str_func = '[{0}] factory.rigDelete'.format(_mBlock.p_nameBase)
        _str_state = _mBlock.getEnumValueString('blockState')

        if _str_state != 'rig':
            raise ValueError,"{0} is not in rig state. state: {1}".format(_str_func, _str_state)

        #_mBlock.blockState = 'rig>prerig'        

        _mBlockModule = get_blockModule(_mBlock.blockType)
        _mBlockCall = False
        
        mModuleTarget = _mBlock.moduleTarget
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
                pass
            else:
                log.error("|{0}| >> Unknown mClass moduleTarget: {1}".format(_str_func,mModuleTarget))            
                
  
        
        if 'rigDelete' in _mBlockModule.__dict__.keys():
            log.debug("|{0}| >> BlockModule rigDelete call found...".format(_str_func))            
            _mBlockModule.rigDelete(_mBlock)        
            

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
        #_kws = self.module_getBuildKWS()

        if _bfr:
            log.debug("|{0}| >> moduleTarget found: {1}".format(_str_func,_bfr))            
            mModule = cgmMeta.validateObjArg(_bfr,'cgmObject')
        else:
            log.debug("|{0}| >> Creating moduleTarget...".format(_str_func))   
            mModule = cgmRigModule(rigBlock=_mBlock)

        #ATTR.set_message(_mBlock.mNode, 'moduleTarget', mModule.mNode,simple = True)
        #ATTR.set_message(mModule.mNode, 'rigBlock', _mBlock.mNode,simple = True)

        ATTR.set(mModule.mNode,'moduleType',_mBlock.blockType,lock=True)
        self._mi_module = mModule

        #assert mModule.isModule(),"Not a module: {0}".format(mModule)
        
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
        mi_puppet = False
        if _mBlock.blockType == 'master':
            log.info("|{0}| >> master...".format(_str_func))                                                    
            if not _mBlock.getMessage('moduleTarget'):
                #_name = _mBlock.getMayaAttr('cgmName') or _mBlock.blockType
                #log.info("|{0}| >> masterBlock name: {1}".format(_str_func,_name))                                        
                #mi_puppet = cgmRigPuppet(name = _name)
                mi_puppet = cgmRigPuppet()
                _mBlock.copyAttrTo('cgmName',mi_puppet.mNode,'cgmName',driven='target')
                
                #ATTR.set_message(_mBlock.mNode, 'moduleTarget', mi_puppet.mNode,simple = True)
                _mBlock.moduleTarget = mi_puppet.mNode
                ATTR.set_message(mi_puppet.mNode, 'rigBlock', _mBlock.mNode,simple = True)
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
                for mBlockParent in _mBlock.getBlockParents():
                    if mBlockParent.blockType == 'master':
                        log.debug("|{0}| >> Found puppet on blockParent: {1}".format(_str_func,mBlockParent))                                                
                        mi_puppet = mBlockParent.moduleTarget
                if not mi_puppet:
                    mi_puppet = cgmRigPuppet(name = mi_module.getNameAlias())

            
            mi_puppet.connect_module(mi_module)	
            mi_puppet.gather_modules()#Gather any modules in the chain

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
global CGM_RIGBLOCK_DAT
CGM_RIGBLOCK_DAT = None

def get_modules_dict(update=False):
    return get_modules_dat(update)[0]

#@cgmGEN.Timer
def get_modules_dat(update = False):
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
    global CGM_RIGBLOCK_DAT

    if CGM_RIGBLOCK_DAT and not update:
        log.debug("|{0}| >> passing buffer...".format(_str_func))          
        return CGM_RIGBLOCK_DAT
    
    
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
                            #reload(module) 
                            _d_modules[name] = module
                            #if not is_buildable(module):
                                #_l_unbuildable.append(name)
                        except Exception, e:
                            log.warning("|{0}| >> Module failed: {1}".format(_str_func,key))                               
                            cgmGEN.cgmExceptCB(Exception,e,msg=vars())

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
            
    CGM_RIGBLOCK_DAT = _d_modules, _d_categories, _l_unbuildable
    return _d_modules, _d_categories, _l_unbuildable


def get_blockModule(blockType,update=False):
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
        _d = get_modules_dict(update)
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
        log.error("|{0}| >> [{1}] | Failed to query name. Probably not a module".format(_str_func,blockModule))        
        return False
    
    _d = get_blockModule_status(_blockType)
    for k,v in _d.iteritems():
        if not v:
            return False
    
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


def valid_blockModule_rigBuildOrder(blockType):
    _str_func = 'get_blockModule_status'

    _BlockModule = get_blockModule(blockType)
    #reload(_BlockModule)
    try:
        _blockType = _BlockModule.__name__.split('.')[-1]
    except:
        log.error("|{0}| >> [{1}] | Failed to query name. Probably not a module".format(_str_func,_buildModule))        
        return False    


    _status = True
    _l_buildOrder = getattr(_BlockModule,'__l_rigBuildOrder__',[])
    if _l_buildOrder:
        for i,step in enumerate(_l_buildOrder):
            if not getattr(_BlockModule,step,False):
                _status = False
                log.error("|{0}| >> [{1}] FAIL. Missing rig step '{2}' call: '{3}'".format(_str_func,_blockType,i,step))
    elif getattr(_BlockModule,'rig',[]):
        log.info("|{0}| >> BlockModule rig call found...".format(_str_func))
    else:
        _status = False

    if _status:
        log.debug("|{0}| >> [{1}] Pass: valid rig build order ".format(_str_func,_blockType))                            
        return _l_buildOrder
    return False

_l_requiredModuleDat = ['__version__',
                        'form',
                        'prerig','is_prerig',
                        'rig','is_rig','rigDelete']

_d_requiredModuleDat = {'define':['__version__'],
                        'form':['form',],
                        'prerig':['prerig'],
                        'skeleton':['skeleton_build'],
                        'rig':['is_rig','rigDelete']}
_d_requiredModuleDatCalls = {'rig':[valid_blockModule_rigBuildOrder]}


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
        for state in BLOCKSHARE._l_blockStates:
            l_tests = _d_requiredModuleDat[state]
            l_functionTests = _d_requiredModuleDatCalls.get(state,[])            
            _good = True
            log.debug("|{0}| >> [{1}]{2}".format(_str_func,_blockType,state.capitalize()) + cgmGEN._str_subLine)            
            for test in l_tests:
                try:
                    if not getattr(_buildModule, test, False):
                        log.debug("|{0}| >> [{1}] FAIL: {2}".format(_str_func,_blockType,test))
                        _good = False  
                    else:
                        log.debug("|{0}| >> [{1}] Pass: {2}".format(_str_func,_blockType,test))
                except Exception,err:
                    log.error("|{0}| >> [{1}] FAIL: {2} | {3}".format(_str_func,_blockType,test,err))
            for test in l_functionTests:
                try:
                    if not test(_blockType):
                        _good = False
                except Exception,err:
                    log.error("|{0}| >> [{1}] FAIL: {2} | {3}".format(_str_func,_blockType,test,err))   
            _res[state] = _good

            if state == 'define':
                log.debug("|{0}| >> [{1}] version: {2}".format(_str_func,_blockType,_buildModule.__dict__.get('__version__',False)))            

    else:
        l_tests = _d_requiredModuleDat[state]
        l_functionTests = _d_requiredModuleDatCalls.get(state,[])
        _res = True
        for test in l_tests:
            if not getattr(_buildModule, test, False):
                log.debug("|{0}| >> [{1}] Missing {3} data: {2}".format(_str_func,_blockType,test,state))
                _res = False
        for test in l_functionTests:
            try:
                if not test(_blockType):
                    #print("|{0}| >> [{1}] Missing {3} data: {2}".format(_str_func,_blockType,test,state))
                    _res = False                
            except Exception,err:
                log.error("|{0}| >> [{1}] FAIL: {2} | {3}".format(_str_func,_blockType,test,err))   
        if state == 'define':
            log.debug("|{0}| >> [{1}] version: {2}".format(_str_func,_blockType,_buildModule.__dict__.get('__version__',False)))                    

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
def contextual_rigBlock_method_call(mBlock, context = 'self', func = 'getShortName',*args,**kws):
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
    _str_func = 'contextual_rigBlock_method_call'

    if func == 'VISUALIZEHEIRARCHY':
        BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,context,False,True)
        return True
    _l_context = BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,context,True,False)
    _res = []

    if not args:
        args = []
        
    _progressBar = None
    if kws:
        if kws.get('progressBar'):
            _progressBar = kws.pop('progressBar')

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
    
    if _progressBar:
        print 'progressBar !!!! | {0}'.format(_progressBar)
        int_len = len(_l_context)
        
    try:
        for i,mBlock in enumerate(_l_context):
            try:
                _short = mBlock.getShortName()
                if _progressBar:
                    cgmUI.progressBar_start(_progressBar)
                    cgmUI.progressBar_set(_progressBar,
                                          maxValue = int_len,beginProgress=True,
                                          progress=i, vis=True)                
                log.debug("|{0}| >> On: {1}".format(_str_func,_short))
                res = getattr(mBlock,func)(*args,**kws) or None
                print("|{0}| >> {1}.{2}({3},{4})".format(_str_func,_short,func,','.join(str(a) for a in args),
                                                               _kwString,))
                if res not in [True,None,False]:print(res)
                _res.append(res)
            except Exception,err:
                raise Exception,err
                cgmGEN.cgmExceptCB(Exception,err)
                log.error(cgmGEN._str_hardLine)
                log.error("|{0}| >> Failure: {1}".format(_str_func, err.__class__))
                log.error("block: {0} | func: {1} | context: {2}".format(_short,func,context))            
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
    finally:
        if _progressBar:cgmUI.progressBar_end(_progressBar)
    return _res

def contextual_module_method_call(mBlock, context = 'self', func = 'getShortName',*args,**kws):
    """
    Function to contextually call a series of rigBlocks and run a methodCall on their modules with 
    args and kws

    :parameters:
        mBlock(str): rigBlock starting point
        context(str): self,below,root,scene
        func(str): string of the method call to use. mBlock.getShortName(), is just 'getShortName'
        *args,**kws - pass through for method call

    :returns
        list of results(list)
    """
    _str_func = 'contextual_rigBlock_method_call'

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
        mc.select([mBlock.atUtils('get_module').mNode for mBlock in _l_context])
        return

    for mBlock in _l_context:
        _short = mBlock.p_nameShort
        try:
            log.debug("|{0}| >> On: {1}".format(_str_func,_short))
            mModule = mBlock.UTILS.get_module(mBlock)
            res = getattr(mModule,func)(*args,**kws) or None
            print("|{0}| >> {1}.{2}({3},{4}) = {5}".format(_str_func,_short,func,','.join(str(a) for a in args),_kwString, res))                        
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
    #@cgmGEN.Timer    
    def __init__(self, rigBlock = None, forceNew = True, autoBuild = False, ignoreRigCheck = False,mode=None,
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
        self.l_precheckErrors = []
        self.l_precheckWarnings = []
        
        if a:log.debug("|{0}| >> a: {1}".format(_str_func,a))
        if kws:#...intial population
            self.call_kws = kws
            #log.debug("|{0}| >> kws: {1}".format(_str_func,kws))

        self.call_kws['forceNew'] = forceNew
        self.call_kws['rigBlock'] = rigBlock
        self.call_kws['autoBuild'] = autoBuild
        self.call_kws['ignoreRigCheck'] = ignoreRigCheck
        
        self.mBlock = cgmMeta.validateObjArg(self.call_kws['rigBlock'],'cgmRigBlock',noneValid=False)
        
        #cgmGEN.log_info_dict(self.call_kws,_str_func)
        _buildModule = rigBlock.p_blockModule
        #reload(_buildModule)
        _short = self.mBlock.p_nameShort
        if _buildModule.__dict__.get('rig_prechecks'):
            log.debug("|{0}| >> Found precheck call".format(_str_func,))
            _buildModule.rig_prechecks(self)        
        
        if self.l_precheckErrors:
            _short = self.mBlock.mNode
            print(cgmGEN._str_hardLine)
            print("|{0}| >> Block: {1} ".format(_str_func, _short))            
            print("|{0}| >> Prechecks failed! ".format(_str_func))
            for i,e in enumerate(self.l_precheckErrors):
                print("{0} | {1}".format(i,e))
            print(cgmGEN._str_hardLine)
            #log.error("[ '{0}' ] Failure. See script editor".format(_short))
            return log.error("[ '{0}' ] Failure. See script editor".format(_short))
            raise ValueError,("[ '{0}' ] Failure. See script editor".format(_short))
        

        #except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
        
        if mode == 'prechecks':
            print(cgmGEN.logString_start("[ {0} ] || PRECHECK PASSED".format(self.mBlock.p_nameShort)))
            return
        
        self.fnc_check_rigBlock()
        self.fnc_get_nodeSnapShot()
        self.fnc_check_module()
        if not self.fnc_rigNeed():
            log.error('No rig need detected. Check settings. self: {0}'.format(self))
            return
        self.fnc_bufferDat()

        if not self.fnc_moduleRigChecks():
            pprint.pprint(self.__dict__)            
            raise RuntimeError,"|{0}| >> Failed to process module rig Checks. See warnings and errors.".format(_str_func)

        self.fnc_deformConstrainNulls()
        
        if self.l_precheckWarnings:
            print(cgmGEN._str_hardLine)
            print("|{0}| >> Block: {1} ".format(_str_func, _short))            
            print("|{0}| >> Prechecks Warnings! ".format(_str_func))
            for i,e in enumerate(self.l_precheckWarnings):
                print("{0} | {1}".format(i,e))
            print(cgmGEN._str_hardLine)                            
        self.fnc_processBuild(**kws)
        

        log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
        

        #_verify = kws.get('verify',False)
        #log.debug("|{0}| >> verify: {1}".format(_str_func,_verify))

    def __repr__(self):
        try:return "{0}(rigBlock: {1})".format(self.__class__, self.mBlock.mNode)
        except:return self

    def atBlockModule(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        _blockModule = self.d_block['buildModule']
        self.d_block['buildModule'] = _blockModule
        return cgmGEN.stringModuleClassCall(self, _blockModule, func, *args, **kws)

    def atBuilderUtils(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        #try:reload(BUILDERUTILS)
        #except Exception,err:
        #    cgmGEN.cgmExceptCB(Exception,err,msg=vars())
            
        return getattr(BUILDERUTILS,func)(self,*args,**kws)
        
        #return cgmGEN.stringModuleClassCall(self, BUILDERUTILS, func, *args, **kws)
    
    atUtils = atBuilderUtils
    UTILS = BUILDERUTILS
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

    @cgmGEN.Timer
    def fnc_get_nodeSnapShot(self):
        #self.ml_preNodesBuffer = RIGGEN.get_nodeSnapShot(1)#cgmMeta.asMeta(SEARCH.get_nodeSnapShot())
        self.l_preNodesBuffer,self.l_preNodesUUIDs = SEARCH.get_nodeSnapShot(uuid=True)
        #self.l_preNodesUUIDs = SEARCH.get_nodeSnapShot(uuid=True)
    def fnc_check_rigBlock(self):
        """
        Check the rig block data 
        """
        if self.l_precheckErrors:
            return False        
        _str_func = 'fnc_check_rigBlock' 
        _d = {}
        self.d_block = _d    
        
        _res = True

        if not self.call_kws['rigBlock']:
            raise RuntimeError,'No rigBlock stored in call kws'

        #BlockFactory = factory(self.call_kws['rigBlock'])
        mBlock = self.mBlock
        mBlock.verify()
        
        _d['mBlock'] = mBlock
        self.mBlock = mBlock
        #_d['mFactory'] = BlockFactory
        _d['shortName'] = mBlock.getShortName()

        _blockType = _d['mBlock'].blockType

        _buildModule = get_blockModule(_blockType)
        """
        reload(_buildModule)
        if _buildModule.__dict__.get('rig_prechecks'):
            log.debug("|{0}| >> Found precheck call".format(_str_func,))
            
            _buildModule.rig_prechecks(self)"""

        

        if not _buildModule:
            log.error("|{0}| >> No build module found for: {1}".format(_str_func,_d['mBlock'].blockType))
            return False
        _d['buildModule'] =  _buildModule   #if not is_buildable
        _d['buildVersion'] = _buildModule.__version__
        _d['blockParents'] = mBlock.getBlockParents()
        _d['b_faceBlock'] = _buildModule.__dict__.get('__faceBlock__',False)

        #Build order --------------------------------------------------------------------------------
        _d['buildOrder'] = valid_blockModule_rigBuildOrder(_buildModule)
        if not _d['buildOrder']:
            raise RuntimeError,'Failed to validate build order'

        
        self.buildModule = _buildModule
        log.debug("|{0}| >> passed...".format(_str_func)+ cgmGEN._str_subLine)

        return True

    #@cgmGEN.Timer
    def fnc_check_module(self):
        _str_func = 'fnc_check_module'  
        _res = True
        #BlockFactory = self.d_block['mFactory']

        _hasModule = True
        #if BlockFactory._mi_block.blockType in ['master']:
        if self.mBlock.blockType in ['master']:
            _hasModule = False


        #>>Module -----------------------------------------------------------------------------------  
        _d = {}    

        if _hasModule:
            #BlockFactory.module_verify()
            _mModule = self.mBlock.atUtils('module_verify')
            self.mModule = _mModule

            _mRigNull = _mModule.rigNull
            _d['mModule'] = _mModule
            _d['mRigNull'] = _mRigNull
            self.mRigNull = _mRigNull
            _d['shortName'] = _mModule.getShortName()
            _d['b_rigged'] = _mModule.atUtils('is_rigged')
            if not _d['b_rigged']: 
                _mModule.rigNull.version = ''
            _d['version'] = _mModule.rigNull.version
            
            
            _d['mModuleParent'] = False            
            if self.d_block['blockParents']:
                if not _mModule.getMessage('moduleParent'):
                    _mModule.atUtils('set_parentModule',self.d_block['blockParents'][0].moduleTarget)

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
            #BlockFactory.puppet_verify()
            self.mBlock.atUtils('puppet_verify')
            _mPuppet = _mModule.modulePuppet
            
            mc.editDisplayLayerMembers(_mPuppet.controlLayer.mNode, _mModule.mNode,noRecurse=True)
            
        else:
            _mPuppet = self.mBlock.moduleTarget

        self.mPuppet = _mPuppet

        _d['mPuppet'] = _mPuppet
        _mPuppet.UTILS.groups_verify(_mPuppet)
        
        
        if _hasModule:
            if not _mModule.atUtils('is_skeletonized'):
                log.warning("|{0}| >> Module isn't skeletonized. Attempting".format(_str_func))

                if not self.mBlock.atBlockModule('skeleton_build'):
                    log.warning("|{0}| >> Skeletonization failed".format(_str_func))            
                    _res = False
            #self.mBlock.atUtils('skeleton_connectToParent')

        self.d_module = _d    
        log.debug("|{0}| >> passed...".format(_str_func)+ cgmGEN._str_subLine)
        return _res    

    #@cgmGEN.Timer
    def fnc_moduleRigChecks(self):
        """
        Verify the module's rig visibility toggles and object set
        """
        _str_func = 'fnc_moduleRigChecks'  
        _res = True

        _blockType = self.mBlock.blockType

        if _blockType in ['master']:
            self.mPuppet.verify_objectSet()            
            return True

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
        
        #Block Vis ---------------------------------------------------------------------------------------
        _str_partVis = self.d_module['partName'] + '_vis'
        _mMasterVis = self.d_module['mMasterVis']

        self.mPlug_visModule = cgmMeta.cgmAttr(_mMasterVis,_str_partVis,value = True,
                                               defaultValue = True, attrType = 'bool',
                                               keyable = False,hidden = False)

        #>>> Object Set -----------------------------------------------------------------------------------
        self.mModule.verify_objectSet()
        
        if self.d_block['b_faceBlock']:
            mFaceSet = self.mModule.atUtils('verify_faceObjectSet')
            self.mFaceSet = mFaceSet
            
            #Settings =============================================================================
            mModuleParent =  self.d_module['mModuleParent']
            if mModuleParent:
                mSettings = mModuleParent.rigNull.settings
            else:
                log.debug("|{0}| >>  using puppet...".format(_str_func))
                mSettings = self.d_module['mMasterControl'].controlVis
                
            log.debug("|{0}| >> mModuleParent mSettings: {1}".format(_str_func,mSettings))
            self.mPlug_visSub_moduleParent = cgmMeta.cgmAttr(mSettings,'visSub','bool')
            self.mPlug_visDirect_moduleParent = cgmMeta.cgmAttr(mSettings,'visDirect','bool')



        log.debug("|{0}| >> passed...".format(_str_func)+ cgmGEN._str_subLine)
        return _res

    #@cgmGEN.Timer
    def fnc_rigNeed(self):
        """
        Function to check if a go instance needs to be rigged

        """
        _str_func = 'fnc_rigNeed'  
        log.debug("|{0}| >> self: {1}".format(_str_func,self)+ '-'*80)

        _mModule = self.d_module.get('mModule')
        _mModuleParent = self.d_module.get('mModuleParent')
        _buildVersion = self.d_block.get('buildVersion')
        _buildModule = self.buildModule
        _blockType = self.mBlock.blockType
        _version = self.d_module.get('version')
        
        _d_callKWS = self.call_kws

        if _blockType == 'master':
            _b_rigged = True
        else:
            if _mModuleParent:
                _str_moduleParent = _mModuleParent.getShortName()
                if not _mModuleParent.atUtils('is_rigged'):
                    log.warning("|{0}| >> [{1}] ModuleParent not rigged".format(_str_func,_str_moduleParent))            
                    return False

            _b_rigged = _mModule.atUtils('is_rigged')

        log.debug("|{0}| >> Rigged: {1}".format(_str_func,_b_rigged))            

        if _b_rigged and not _d_callKWS['forceNew'] and _d_callKWS['ignoreRigCheck'] is not True:
            log.warning("|{0}| >> Already rigged and not forceNew".format(_str_func))                    
            return False

        self.b_outOfDate = False
        if _version != _buildVersion:
            self.b_outOfDate = True
            log.warning("|{0}| >> Versions don't match: rigNull: {1} | buildModule: {2}".format(_str_func,_version,_buildVersion))                            
        else:
            if _d_callKWS['forceNew'] and _b_rigged:
                log.warning("|{0}| >> Force new and is rigged. Deleting rig...NOT IMPLEMENTED".format(_str_func))                    
                #_mModule.rigDelete()
            else:
                log.info("|{0}| >> Up to date.".format(_str_func))                    
                return False

        return True

    #@cgmGEN.Timer
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
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())

            #cgmGEN.log_info_dict(self.__dict__,'rigFactory')

            raise Exception,err
        return _res

    #@cgmGEN.Timer
    def log_self(self):
        _d = copy.copy(self.__dict__)
        for k in ['l_preNodesBuffer','l_preNodesUUIDs']:
            _d.pop(k)
        pprint.pprint(_d)

    #@cgmGEN.Timer
    def fnc_bufferDat(self):
        """
        Function to check if a go instance needs to be rigged

        """
        try:
            _str_func = 'fnc_bufferDat'  

            _mModule = self.d_module.get('mModule')    
            _mModuleParent = self.d_module.get('mModuleParent')
            _mPuppet = self.d_module.get('mPuppet')
            _mRigNull = self.d_module.get('mRigNull')
            _version = self.d_module.get('version')
            _buildVersion = self.d_block.get('buildVersion')
            _blockType = self.mBlock.blockType

            _d_callKWS = self.call_kws

            #>>Module dat ------------------------------------------------------------------------------
            _d = {}
            if _mModule:
                _d['partName'] = _mModule.get_partNameBase()
                _d['partType'] = _mModule.moduleType.lower() or False

                #_d['l_moduleColors'] = _mModule.getModuleColors() 
                #_d['l_coreNames'] = []#...need to do this
                #self.mFormNull = _mModule.formNull
                #_d['mFormNull'] = self.mFormNull
                #_d['bodyGeo'] = _mPuppet.getGeo() or ['Morphy_Body_GEO']
                _d['direction'] = _mModule.getAttr('cgmDirection')

                _d['mirrorDirection'] = _mModule.get_mirrorSideAsString()
            else:
                _d['mirrorDirection'] = 'Centre'

            _d['f_shapeOffset'] = _mPuppet.atUtils('get_shapeOffset')
            _d['mMasterNull'] = _mPuppet.masterNull

            #>MasterControl....
            if not _mPuppet.getMessage('masterControl'):
                log.info("|{0}| >> Creating masterControl...".format(_str_func))                    
                #_mPuppet.verify_masterControl(size = max(POS.get_axisBox_size(self.mBlock.mNode)) * 1.5)
                _mPuppet.verify_masterControl()

            _d['mMasterControl'] = _mPuppet.masterControl
            _d['mPlug_globalScale'] =  cgmMeta.cgmAttr(_d['mMasterControl'].mNode,'scaleY')	 
            _d['mMasterSettings'] = _d['mMasterControl'].controlSettings
            _d['mMasterVis'] = _d['mMasterControl'].controlVis
            
            _d['mMasterDeformGroup'] = _mPuppet.masterNull.deformGroup

            #_d['mMasterNull'].worldSpaceObjectsGroup.parent = _mPuppet.masterControl

            self.d_module.update(_d)

            #cgmGEN.log_info_dict(self._d_module,_str_func + " moduleDat")      
            log.info(cgmGEN._str_subLine)


            #>>Joint dat ------------------------------------------------------------------------------
            _d = {}
            if _mModule:
                _d['ml_moduleJoints'] = _mRigNull.msgList_get('moduleJoints',cull=True)
                if not _d['ml_moduleJoints']:
                    self.l_precheckErrors.append("No module joints found")
                    _d['ml_skinJoints'] = False
                else:
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
            _d['mOrientation'] = _mOrientation
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
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())
            raise Exception,err


    def fnc_deformConstrainNulls(self):
        """
        Verify the module's rig visibility toggles and object set
        """
        _str_func = 'fnc_deformConstrainNulls'  
        _res = True
        _start = time.clock()

        _blockType = self.mBlock.blockType

        if _blockType in ['master']:
            return True

        #>>Connect switches ----------------------------------------------------------------------------------- 
        _str_partType = self.d_module['partType']
        _str_partName= self.d_module['partName']

        _mMasterSettings = self.d_module['mMasterSettings']
        _mi_moduleParent = self.d_module['mModuleParent']
        _ml_skinJoints = self.d_joints['ml_skinJoints']
        
        try:_attachIdx = self.mBlock.attachIndex
        except:_attachIdx = None

        _attachPoint = ATTR.get_enumValueString(self.mBlock.mNode,'attachPoint')        
        self.attachPoint = self.mModule.atUtils('get_driverPoint',_attachPoint,idx=_attachIdx )        

        if not self.mModule.getMessage('deformNull'):
            if self.d_block['b_faceBlock'] or _blockType in ['eyeMain']:
                log.debug("|{0}| >> Face deformNull".format(_str_func))
                mGrp = self.attachPoint.doCreateAt(setClass=True)
                self.mModule.connectChildNode(mGrp,'constrainNull','module')
                mGrp.parent = self.attachPoint
            else:
                #Make it and link it
                buffer =  CORERIG.group_me(_ml_skinJoints[0].mNode,False)
                mGrp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
                mGrp.parent = self.d_module['mMasterDeformGroup'].mNode
                
            mGrp.addAttr('cgmName',_str_partName,lock=True)
            mGrp.addAttr('cgmTypeModifier','deform',lock=True)	 
            mGrp.doName()
            self.mModule.connectChildNode(mGrp,'deformNull','module')
                    
        self.mDeformNull = self.mModule.deformNull

        
        if not self.mModule.getMessage('constrainNull') and self.d_block['b_faceBlock'] is not True:
            buffer =  CORERIG.group_me(self.mDeformNull.mNode,False)
            mGrp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
            mGrp.addAttr('cgmName',_str_partName,lock=True)
            mGrp.addAttr('cgmTypeModifier','constrain',lock=True)	 
            mGrp.doName()
            mGrp.parent = self.mDeformNull.mNode
            self.mModule.connectChildNode(mGrp,'constrainNull','module')
        self.mConstrainNull = self.mModule.constrainNull
        
        
        if self.attachPoint:
            self.mRigNull.connectChildNode(self.attachPoint,'attachPoint')
            
            if not self.mRigNull.getMessage('attachDriver'):
                mAttachDriver = self.mDeformNull.doCreateAt()
                mAttachDriver.addAttr('cgmName',_str_partName,lock=True)
                mAttachDriver.addAttr('cgmType','attachDriver',lock=True)	 
                
                mAttachDriver.doName()
                
                #self.mRigNull.connectChildNode(mAttachDriver,'attachDriver')                
                mAttachDriver.connectChildNode(self.attachPoint,'attachPoint')
                self.mRigNull.connectChildNode(mAttachDriver,'attachDriver','module')
                
            else:
                mAttachDriver = self.mRigNull.getMessageAsMeta('attachDriver')
            
            mAttachDriver.parent = self.attachPoint
            mAttachDriver.setAttrFlags()
            #mc.parentConstraint([mAttachDriver.mNode],
            #                    self.mConstrainNull.mNode,
            #                    maintainOffset = True, weight = 1)            
            
            
            """
            log.info("|{0}| >> attaching to attachpoint: {1}".format(_str_func,self.attachPoint))
            mAttach = cgmMeta.validateObjArg(self.attachPoint)
            try:mc.delete(self.mConstrainNull.getConstraintsTo())
            except:pass            
            if not self.mConstrainNull.getMessage('attachDriver'):
                mAttachDriver = self.mDeformNull.doCreateAt()
                mAttachDriver.addAttr('cgmName',_str_partName,lock=True)
                mAttachDriver.addAttr('cgmTypeModifier','attachDriver',lock=True)	 
                mAttachDriver.doName()
                
                self.mRigNull.connectChildNode(mAttachDriver,'attachDriver')                
                mAttachDriver.connectChildNode(self.attachPoint,'attachPoint')
                self.mConstrainNull.connectChildNode(mAttachDriver,'attachDriver','module')
                
            else:
                mAttachDriver = self.mRigNull.getMessageAsMeta('attachDriver')
            
            mAttachDriver.parent = self.attachPoint
           
            mc.parentConstraint([mAttachDriver.mNode],
                                self.mConstrainNull.mNode,
                                maintainOffset = True, weight = 1)
            #mc.scaleConstraint([mAttach.mNode], self.mConstrainNull.mNode, maintainOffset = True, weight = 1)
            """

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
        else:log.error("|{0}| >> No autobuild condition met. Out of date: {1}".format(_str_func, self.b_outOfDate))
        
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))            

    def doBuild(self,buildTo = '',**kws):
        _str_func = 'doBuild'  
        _start = time.clock()
        

        try:
            _l_buildOrder = self.d_block['buildModule'].__dict__.get('__l_rigBuildOrder__')
            if not _l_buildOrder:
                raise ValueError,"No build order found"
            _len = len(_l_buildOrder)

            if not _len:
                log.error("|{0}| >> No steps to build!".format(_str_func))                    
                return False
            #Build our progress Bar
            try:mayaMainProgressBar = CGMUI.doStartMayaProgressBar(_len)
            except:mayaMainProgressBar = None

            for i,fnc in enumerate(_l_buildOrder):
                _str_func = '_'.join(fnc.split('_')[1:])
                
                if mayaMainProgressBar:
                    mc.progressBar(mayaMainProgressBar, edit=True,
                                   status = "|{0}| >>Rig>> step: {1}...".format(self.d_block['shortName'],fnc), progress=i+1)                    
                
                mc.undoInfo(openChunk=True,chunkName=fnc)
                
                
                err=None
                try:
                    getattr(self.d_block['buildModule'],fnc)(self)            
                except Exception,err:
                    log.error(err)
            
                finally:
                    mc.undoInfo(closeChunk=True)            
                    if err is not None:
                        cgmGEN.cgmExceptCB(Exception,err,localDat=vars())                        
                
                
                    if buildTo is not None:
                        _Break = False
                        if VALID.stringArg(buildTo):
                            if buildTo == fnc:
                                _Break = True
                        elif buildTo == i:
                            _Break = True
                
                        if _Break:
                            log.debug("|{0}| >> Stopped at step: [{1}]".format(_str_func, _str_subFunc))   
                            break                                
                
                    
            #self.mBlock.addAttr('rigNodeBuffer','message',l_diff)
            
            if mayaMainProgressBar:CGMUI.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
        except Exception,err:
            CGMUI.doEndMayaProgressBar()#Close out this progress bar
            cgmGEN.cgmException(Exception,err,msg=vars())

            raise Exception,"|{0}| >> err: {1}".format(_str_func,err)

        log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))

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

#========================================================================================================
# Rig Meta Classes...
#========================================================================================================
class cgmRigPuppet(cgmMeta.cgmNode):
    def __init__(self, node = None, name = None, initializeOnly = False, doVerify = False, *args,**kws):
        try:
            _str_func = 'cgmRigPuppet.__init__'
            log.debug("|{0}| >> node:{1} | name: {2}...".format(_str_func,node,name)+ '-'*80)
            
            
            if node:
                _buffer = ATTR.get_message(node,'puppet')
                if _buffer:
                    log.info("|{0}| >> Passed masterNull [{1}]. Using puppet [{2}]".format(_str_func,node,_buffer[0]))                
                    node = _buffer[0]
        
            super(cgmRigPuppet, self).__init__(node = node, name = name, nodeType = 'network') 
            self._blockModule=None
    
            #====================================================================================	
            #>>> TO USE Cached instance ---------------------------------------------------------
            if self.cached:
                log.debug('CACHE : Aborting __init__ on pre-cached {0} Object'.format(self))
                return
            #====================================================================================
    
            #self.UNMANAGED.extend(['i_masterNull','_UTILS'])
            #for a in 'i_masterNull','_UTILS':
            #    if a not in self.UNMANAGED:
            #        self.UNMANAGED.append(a) 	
            #self._UTILS = pFactory
            self.UTILS = PUPPETUTILS
            if self.__justCreatedState__ or doVerify:
                if self.isReferenced():
                    log.error("|{0}| >> Cannot verify referenced nodes".format(_str_func))
                    return
                elif not self.__verify__(name = name,**kws):
                    raise RuntimeError,"|{0}| >> Failed to verify: {1}".format(_str_func,self.mNode)
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
    #====================================================================================
    def __verify__(self,name = None,**kws):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """
        try:
            _short = self.p_nameShort
            _str_func = "cgmRigPuppet.__verify__"
            log.debug("|{0}| >> ...".format(_str_func))            
            log.debug("|{0}| >> name : {1}".format(_str_func,name))                                
    
            #Puppet Network Node 
            #---------------------------------------------------------------------------
            self.addAttr('mClass', initialValue='cgmRigPuppet',lock=True)  
            self.addAttr('cgmName',initialValue=name, attrType='string', lock = True)
            
            if name is not None:
                ATTR.set(_short, 'cgmName', name)
            if self.cgmName is None:
                ATTR.set(_short, 'cgmName', 'puppet')
                
            self.addAttr('cgmType','puppetNetwork')
            self.addAttr('version',initialValue = '', lock=True)  
            self.addAttr('masterNull',attrType = 'messageSimple',lock=True)
            self.addAttr('masterControl',attrType = 'messageSimple',lock=True)  	
            self.addAttr('moduleChildren',attrType = 'message',lock=True) 
            self.addAttr('unifiedGeo',attrType = 'messageSimple',lock=True) 
            self.addAttr('displayLayer',attrType = 'messageSimple',lock=True)              
    
            #Settings 
            #---------------------------------------------------------------------------
            #defaultFont = modules.returnSettingsData('defaultTextFont')
            defaultFont = BLOCKSHARE.str_defaultFont
            self.addAttr('font',attrType = 'string',initialValue=defaultFont,lock=True)   
            self.addAttr('axisAim',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=2) 
            self.addAttr('axisUp',enumName = 'x+:y+:z+:x-:y-:z-', attrType = 'enum',initialValue=1) 
            self.addAttr('axisOut',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=0) 
            self.addAttr('skinDepth',attrType = 'float',initialValue=.75,lock=True)   
    
            self.doName()
            
            if kws.get('rigBlock'):
                _moduleLink = kws.get('puppetLink','moduleTarget')
                mRigBlock = cgmMeta.validateObjArg(kws.get('rigBlock'),'cgmRigBlock')
                if mRigBlock:
                    log.debug("|{0}| >> rigBlock on call: {1}".format(_str_func,mRigBlock))
                    ATTR.set_message(mRigBlock.mNode, _moduleLink, self.mNode,simple = True)
                    ATTR.set_message(self.mNode, 'rigBlock', mRigBlock.mNode,simple = True)            
            
            # Layers ---------------------------------------------------------------------------            
            self.atUtils('layer_verify')
    
            #MasterNull 
            #---------------------------------------------------------------------------
            self.verify_masterNull()

                
            #if self.masterNull.getShortName() != self.cgmName:
                #self.masterNull.doName()
                #if self.masterNull.getShortName() != self.cgmName:
                    #log.warning("Master Null name still doesn't match what it should be.")
            
            ATTR.set_standardFlags(self.masterNull.mNode,attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
            
            #Quick select sets
            #---------------------------------------------------------------------------
            #self.verify_objectSet()
            self.atUtils('qss_verify')
    
            # Groups ---------------------------------------------------------------------------
            self.atUtils('groups_verify')
            
            return True
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
    def atUtils(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        #reload(PUPPETUTILS)
        return getattr(PUPPETUTILS,func)(self,*args,**kws)            
        #return self.stringModuleCall(PUPPETUTILS,func,*args, **kws)

    def changeName(self,name = None):
        try:
            _str_func = 'cgmRigPuppet.changeName'
            log.debug("|{0}| >> ...".format(_str_func))

            if name == self.cgmName:
                log.error("Puppet already named '%s'"%self.cgmName)
                return
            
            if name != '' and type(name) is str:
                log.warn("Changing name from '%s' to '%s'"%(self.cgmName,name))
                try:self.cgmName = name
                except:pass
                self.doName()
                #self.__verify__()
                
            #self.masterNull.displayLayer.doName()

        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
    def doName(self):
        try:
            _str_func = 'cgmRigPuppet.doName'
            log.debug("|{0}| >> ...".format(_str_func))
            
            _d = nameTools.returnObjectGeneratedNameDict(self.mNode)
            self.rename(nameTools.returnCombinedNameFromDict(_d))
            
            try:
                mMasterNull = self.masterNull
            except:
                pass
            
            try:
                self.masterControl.doName()
                self.masterControl.rebuildMasterShapes()
            except:pass
            
            try:self.puppetSet.doName()
            except:pass
            
            try:self.getMessage('rootJoint',asMeta=True)[0].doName()
            except:pass
            
            try:self.displayLayer.doName()
            except:pass
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
    def controller_get(self,verify=False):
        return cgmMeta.controller_get(self,verify)
    
    def verify_masterNull(self,**kws):
        try:
            _str_func = 'cgmRigPuppet.verify_masterNull'
            log.debug("|{0}| >> ...".format(_str_func))
            mRigBlock = self.getMessageAsMeta('rigBlock')
            
            if not self.getMessage('masterNull'):
                log.info("|{0}| >> making masterNull...".format(_str_func))                
                if mRigBlock:
                    log.info("|{0}| >> from rigBlock...".format(_str_func))                
                    mMasterNull = mRigBlock.doCreateAt()
                    mMasterNull.resetAttrs()
                else:
                    mMasterNull = cgmMeta.cgmObject()
            else:
                mMasterNull = self.masterNull

            ATTR.copy_to(self.mNode,'cgmName',mMasterNull.mNode,driven='target')
            mMasterNull.addAttr('puppet',attrType = 'messageSimple')
            if not mMasterNull.connectParentNode(self.mNode,'puppet','masterNull'):
                raise StandardError,"Failed to connect masterNull to puppet network!"

            mMasterNull.addAttr('mClass',value = 'cgmMasterNull',lock=True)
            mMasterNull.addAttr('cgmModuleType',value = 'master',lock=True)   
            mMasterNull.addAttr('partsGroup',attrType = 'messageSimple',lock=True)   
            mMasterNull.addAttr('deformGroup',attrType = 'messageSimple',lock=True)   	
            mMasterNull.addAttr('noTransformGroup',attrType = 'messageSimple',lock=True)   
            mMasterNull.addAttr('geoGroup',attrType = 'messageSimple',lock=True)   
            mMasterNull.addAttr('rigGroup',attrType = 'messageSimple',lock=True)   

            #See if it's named properly. Need to loop back after scene stuff is querying properly
            #mMasterNull.doName()
            mMasterNull.rename('master')#mMasterNull.cgmName)
            mc.editDisplayLayerMembers(self.displayLayer.mNode, mMasterNull.mNode,noRecurse=True)

            
            return True
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    #=================================================================================================
    # Puppet Utilities
    #=================================================================================================
    #@cgmGEN.Timer
    def verify_groups(self):
        try:
            _str_func = "cgmRigPuppet.verify_groups".format()
            log.debug("|{0}| >> ...".format(_str_func))
            
            raise ValueError,'NO. Go back!'
            mMasterNull = self.masterNull

            if not mMasterNull:
                raise ValueError, "No masterNull"

            for attr in 'rig','deform','noTransform','geo','skeleton','parts','worldSpaceObjects','puppetSpaceObjects':
                _link = attr+'Group'
                mGroup = mMasterNull.getMessage(_link,asMeta=True)# Find the group
                if mGroup:mGroup = mGroup[0]

                if not mGroup:
                    mGroup = cgmMeta.cgmObject(name=attr)#Create and initialize
                    mGroup.rename(attr+'_grp')
                    mGroup.connectParentNode(mMasterNull.mNode,'puppet', attr+'Group')
                log.debug("|{0}| >> attr: {1} | mGroup: {2}".format(_str_func, attr, mGroup))

                # Few Case things
                #==============
                if attr in ['rig']:
                    mGroup.p_parent = mMasterNull
                elif attr in ['geo','parts']:
                    mGroup.p_parent = mMasterNull.noTransformGroup
                elif attr in ['deform','puppetSpaceObjects'] and self.getMessage('masterControl'):
                    mGroup.p_parent = self.getMessage('masterControl')[0]	    
                else:    
                    mGroup.p_parent = mMasterNull.rigNull

                ATTR.set_standardFlags(mGroup.mNode)

                if attr == 'worldSpaceObjects':
                    mGroup.addAttr('cgmAlias','world')
                elif attr == 'puppetSpaceObjects':
                    mGroup.addAttr('cgmAlias','puppet')
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())


    def verify_objectSet(self):
        self.UTILS.qss_verify(self)
        """
        try:
            
            _str_func = "cgmRigPuppet.verify_objectSet"
            log.debug("|{0}| >> ...".format(_str_func))

            #Quick select sets ================================================================
            mSet = self.getMessageAsMeta('puppetSet')
            if not mSet:
                mSet = cgmMeta.cgmObjectSet(setType='animSet',qssState=True)
                mSet.connectParentNode(self.mNode,'puppet','puppetSet')
            #ATTR.copy_to(self.mNode,'cgmName',mSet.mNode,'cgmName',driven = 'target')
            mSet.rename('animSet')
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err)"""
        
    def rig_connect(self):
        return self.UTILS.rig_connect(self)
    def rig_disconnect(self):
        return self.UTILS.rig_disconnect(self)
    def rig_isConnected(self):
        return self.UTILS.rig_isConnected(self)
        
    def delete(self):
        """
        Delete the Puppet
        """
        try:
            _str_func = "cgmRigPuppet.delete"
            log.debug("|{0}| >> ...".format(_str_func))
            
            try:self.displayLayer.delete()
            except:pass
            try:self.controlLayer.delete()
            except:pass            
            mc.delete(self.masterNull.mNode)
            mc.delete(self.mNode)
            #del(self)
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
    #=================================================================================================
    # Modules
    #=================================================================================================
    def connect_module(self,mModule,**kws):
        return PUPPETUTILS.module_connect(self, mModule,**kws)
        #return self.atUtils('module_connect',mModule,**kws)
    def get_modules(self,*args,**kws):
        return PUPPETUTILS.modules_get(self, *args,**kws)        
        #return self.atUtils('modules_get',*args,**kws)    
    def gather_modules(self,*args,**kws):
        return PUPPETUTILS.modules_gather(self, *args,**kws)        
        #return self.atUtils('modules_gather',*args,**kws)    
    
    def get_mirrorNextIndex(self,side='center'):
        return PUPPETUTILS.mirror_getNextIndex(self, _side)                
        #return self.atUtils('mirror_getNextIndex',side)    
    def get_mirrorDict(self):
        return PUPPETUTILS.mirror_getDict(self)                
            
    
    def verify_masterControl(self,**kws):
        """ 
        """
        try:
            _str_func = "cgmRigPuppet.verify_masterControl"
            log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
            
            self.UTILS.groups_verify(self)
            self.UTILS.layer_verify(self)
            
            #self.verify_groups()#...make sure everythign is there
            
            # Size...
            #-------------------------------------------------------------------------
            _size = kws.get('size',None)
            if _size == None:
                log.debug("|{0}| >> No size kw passed, finding...".format(_str_func))
                _size = [10,10,10]
                
                if self.getMessage('rigBlock'):
                    log.info("|{0}| >> Finding size from rigBlock...".format(_str_func))                    
                    mBlock = self.rigBlock
                    bb = DIST.get_bb_size(mBlock.getShapes(),True)
                    _size = bb
                    
                kws['size'] = _size
                
                
            log.debug("|{0}| >> size: {1}".format(_str_func,_size))
            
            mMasterNull = self.masterNull
            
            # Master Control
            #==================================================================
            log.debug("|{0}| >> MasterControl...".format(_str_func))            
            mMasterControl = self.getMessage('masterControl',asMeta=True)
            if not mMasterControl:
                mMasterControl = cgmRigMaster(puppet = self,**kws)#Create and initialize
                mMasterControl.__verify__()
                if self.getMessage('rigBlock'):
                    SNAP.go(mMasterControl.mNode, self.rigBlock.mNode)
            else:
                mMasterControl = mMasterControl[0]
            mMasterControl.parent = mMasterNull.mNode
            #mMasterControl.doName()
            
            
            """
            #Vis network#--------------------------------------------------------------------------
            log.debug("|{0}| >> visNetwork...".format(_str_func))                        
            iVis = mMasterControl.controlVis
            visControls = 'left','right','sub','main'
            visArg = [{'result':[iVis,'leftSubControls_out'],'drivers':[[iVis,'left'],[iVis,'subControls'],[iVis,'controls']]},
                      {'result':[iVis,'rightSubControls_out'],'drivers':[[iVis,'right'],[iVis,'subControls'],[iVis,'controls']]},
                      {'result':[iVis,'subControls_out'],'drivers':[[iVis,'subControls'],[iVis,'controls']]},		      
                      {'result':[iVis,'leftControls_out'],'drivers':[[iVis,'left'],[iVis,'controls']]},
                      {'result':[iVis,'rightControls_out'],'drivers':[[iVis,'right'],[iVis,'controls']]}
                      ]
            NODEFAC.build_mdNetwork(visArg)
            """
            
            
            # Setup the settings
            #--------------------------------------------------------------------------
            log.debug("|{0}| >> Settings...".format(_str_func))            
            mSettings = mMasterControl.controlSettings
            str_settings = mSettings.mNode
            #Skeleton/geo settings
            for attr in ['skeleton','geo','proxy']:
                mSettings.addAttr(attr,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
                NODEFAC.argsToNodes("%s.%sVis = if %s.%s > 0"%(str_settings,attr,str_settings,attr)).doBuild()
                NODEFAC.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(str_settings,attr,str_settings,attr)).doBuild()

            mSettings.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)
            
            #>>> Deform group
            #--------------------------------------------------------------------------
            log.debug("|{0}| >> deformGroup...".format(_str_func))                        
            if mMasterNull.getMessage('deformGroup'):
                mMasterNull.deformGroup.parent = mMasterControl.mNode
            mMasterControl.addAttr('cgmAlias','world',lock = True)
            
            
            """
            #>>> Skeleton Group
            #--------------------------------------------------------------------------
            log.debug("|{0}| >> skeletonGroup...".format(_str_func))                        
            if not mMasterNull.getMessage('skeletonGroup'):
                #Make it and link it
                mGrp = cgmMeta.createMetaNode('cgmObject')
                mGrp.doSnapTo(mMasterControl.mNode)
                
                #mGrp.doRemove('cgmName')
                mGrp.addAttr('cgmTypeModifier','skeleton',lock=True)	 
                mGrp.parent = mMasterControl.mNode
                mMasterNull.connectChildNode(mGrp,'skeletonGroup','module')
                mGrp.doName('skeleton_grp')
                
                #mGrp.doName()
            else:
                mGrp = mMasterNull.skeletonGroup
                
            mGrp.overrideEnabled = 1             
            cgmMeta.cgmAttr(mSettings,'skeletonVis',lock=False).doConnectOut("%s.%s"%(mGrp.mNode,'overrideVisibility'))    
            cgmMeta.cgmAttr(mSettings,'skeletonLock',lock=False).doConnectOut("%s.%s"%(mGrp.mNode,'overrideDisplayType'))    
         
            #>>>Connect some flags
            #--------------------------------------------------------------------------
            log.info("|{0}| >> Geo connections...".format(_str_func))            
            if not mMasterNull.getMessage('geoGroup'):
                mGeoGroup = self.masterNull.geoGroup
                mGeoGroup.overrideEnabled = 1
                cgmMeta.cgmAttr(mSettings.mNode,
                                'geoVis',
                                lock=False).doConnectOut("%s.%s"%(mGeoGroup.mNode,
                                                                  'overrideVisibility'))
                cgmMeta.cgmAttr(mSettings.mNode,
                                'geoLock',
                                lock=False).doConnectOut("%s.%s"%(mGeoGroup.mNode,
                                                                  'overrideDisplayType'))  
            else:
                mGrp = mMasterNull.geoGroup
                
            try:mMasterNull.puppetSpaceObjectsGroup.parent = mMasterControl
            except:pass
            
            return True            
            """

            #>>> Skeleton Group
            #=====================================================================	
            if not self.masterNull.getMessage('skeletonGroup'):
                mSkeletonGrp = cgmMeta.createMetaNode('cgmObject')
                mSkeletonGrp.doSnapTo(mMasterControl.mNode)
                mSkeletonGrp.addAttr('cgmName','ignore',lock=True)
                mSkeletonGrp.addAttr('cgmTypeModifier','skeleton',lock=True)
                #mSkeletonGrp.parent = mMasterControl.mNode
                self.masterNull.connectChildNode(mSkeletonGrp,'skeletonGroup','module')
                mSkeletonGrp.doName()
            else:
                mSkeletonGrp = self.masterNull.skeletonGroup
            
            log.debug("|{0}| >> skeletonGroup...".format(_str_func))                                    
            mSkeletonGrp = self.masterNull.skeletonGroup
            _skeletonGrp = mSkeletonGrp.mNode
            
            #Verify the connections
            ATTR.set(_skeletonGrp,'overrideEnabled',1)
            #mSkeletonGrp.overrideEnabled = 1             
            cgmMeta.cgmAttr(str_settings,'skeletonVis',lock=False).doConnectOut("%s.%s"%(_skeletonGrp,'overrideVisibility'))    
            cgmMeta.cgmAttr(str_settings,'skeletonLock',lock=False).doConnectOut("%s.%s"%(_skeletonGrp,'overrideDisplayType'))    
    
    
            #>>>Connect some flags
            #=====================================================================
            log.debug("|{0}| >> geoGroup...".format(_str_func))                                    
            
            mGeoGrp = self.masterNull.geoGroup
            _geoGrp = mGeoGrp.mNode
            
            ATTR.set(_geoGrp,'overrideEnabled',1)
            cgmMeta.cgmAttr(str_settings,'geoVis',lock=False).doConnectOut("%s.%s"%(_geoGrp,'overrideVisibility'))
            cgmMeta.cgmAttr(str_settings,'geoLock',lock=False).doConnectOut("%s.%s"%(_geoGrp,'overrideDisplayType'))  
    
            try:self.masterNull.puppetSpaceObjectsGroup.parent = mMasterControl
            except:pass
            
            #mc.editDisplayLayerMembers(self.controlLayer.mNode, mMasterControl.mNode)
            mc.editDisplayLayerMembers(self.controlLayer.mNode, mMasterControl.mNode,noRecurse=True)
            
            
            return True
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
class cgmRigMaster(cgmMeta.cgmObject):
    """
    Make a master control curve
    """
    def __init__(self,*args,**kws):
        try:
            _str_func = 'cgmRigMaster.__init__'
            log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)        
    
            _size = kws.get('size',None)
            _sel = mc.ls(sl=1) or None
            log.debug("|{0}| >> size: {1} | sel: {2}".format(_str_func,_size,_sel))
            
            _callSize = get_callSize(_size,_sel)
            log.debug("|{0}| >> call size: {1}".format(_str_func,_callSize))
            
            kws['size'] = _callSize#...push back new value

            super(cgmRigMaster, self).__init__(*args,**kws)
            
            #====================================================================================	
            #>>> TO USE Cached instance ---------------------------------------------------------
            if self.cached:
                log.debug('CACHE : Aborting __init__ on pre-cached {0} Object'.format(self))
                return
            #====================================================================================

            doVerify = kws.get('doVerify') or False
            
            if self.__justCreatedState__ or doVerify:
                if not self.__verify__(*args,**kws):
                    raise StandardError,"Failed to verify!"	
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    def __verify__(self,*args,**kws):
        try:
            _str_func = 'cgmRigMaster.__verify__'
            _short = self.mNode
            log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)                
            
            puppet = kws.pop('puppet',False)
            if puppet and not self.isReferenced():
                log.debug("|{0}| >> puppet: {1}".format(_str_func,puppet))                            
                ATTR.copy_to(puppet.mNode,'cgmName',self.mNode,driven='target')
                self.connectParentNode(puppet,'puppet','masterControl')
            elif not self.hasAttr('cgmName'):
                self.addAttr('cgmName','MasterControl')
    
            #Check for shapes, if not, build
            #self.color =  modules.returnSettingsData('colorMaster',True)
    
            #>>> Attributes -------------------------------------------------
            if kws and 'name' in kws.keys():
                self.addAttr('cgmName', kws.get('name'), attrType = 'string')
    
            self.addAttr('cgmType','controlMaster',attrType = 'string')

            self.addAttr('controlVis', attrType = 'messageSimple',lock=True)
            self.addAttr('visControl', attrType = 'bool',keyable = False,initialValue= 1)
    
            self.addAttr('controlSettings', attrType = 'messageSimple',lock=True)
            self.addAttr('settingsControl', attrType = 'bool',keyable = False,initialValue= 1)
    
            #Connect and Lock the scale stuff------------------------------------
            self.setAttrFlags(attrs=['sx','sz'])
            self.doConnectOut('sy',['sx','sz'])
            ATTR.set_alias(_short,'sy','rigScale')
            
            
            #=====================================================================
            #>>> Curves!
            #=====================================================================
            #>>> Master curves
            _shapes = self.getShapes()
            if len(_shapes)<3:
                self.rebuildMasterShapes(**kws)
            self.doName()
            return True
        
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    def rebuildMasterShapes(self,**kws):
        """
        Rebuild the master control curve
        """
        try:
            _str_func = 'cgmRigMaster.rebuildControlCurve'
            _short = self.mNode
            log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
            
            l_shapes = self.getShapes()
            #self.color =  modules.returnSettingsData('colorMaster',True)
            
            #>>> Figure out the control size 	
            font = kws.get('font',None)
            
            size = get_callSize(kws.get('size',[10,10,10]))
            
            if self.getMessage('puppet'):
                if self.puppet.getMessage('rigBlock'):
                    log.info("|{0}| >> Finding size from rigBlock...".format(_str_func))                    
                    mBlock = self.puppet.rigBlock
                    size = DIST.get_bb_size(mBlock.getShapes(),True)
                    #size = self.puppet.rigBlock.baseSize
            
                    
            log.debug("|{0}| >> size: {1}".format(_str_func,size))
            
            _average = MATH.average([size[0],size[2]])
            _size = _average * 1.5
            _offsetSize = _average * .1
            
            mc.delete(l_shapes)
            
            mHandleFactory = BLOCKSHAPES.handleFactory(node = _short)
            
                    
            #>>> Figure out font------------------------------------------------------------------
            if font == None:#
                if kws and 'font' in kws.keys():font = kws.get('font')		
                else:font = 'arial'
                
            #>>> Main shape ----------------------------------------------------------------------
            _crv = CURVES.create_fromName(name='squareOpen',direction = 'y+', size = 1, baseSize=1.0)    
            TRANS.scale_to_boundingBox(_crv, [size[0],None,size[2]])
        
            mHandleFactory.color(_crv,'center','sub',transparent = False)
        
            mCrv = cgmMeta.validateObjArg(_crv,'cgmObject')
            l_offsetCrvs = []
            for shape in mCrv.getShapes():
                offsetShape = mc.offsetCurve(shape, distance = -_offsetSize, ch=False )[0]
                mHandleFactory.color(offsetShape,'center','main',transparent = False)
                l_offsetCrvs.append(offsetShape)
        
            CORERIG.combineShapes(l_offsetCrvs + [_crv], False)
            SNAP.go(_crv,self.mNode)    
            CORERIG.shapeParent_in_place(self.mNode,_crv,False)
            
            #>>> Name Curve ----------------------------------------------------------------------
            if self.hasAttr('cgmName'):
                log.debug("|{0}| >> Making name curve...".format(_str_func))                
                nameSize = size[0]
                _textCurve = CURVES.create_text(self.cgmName, size = nameSize * .7, font = font)
                #TRANS.scale_to_boundingBox(_textCurve, [None,None,size[2]*.95])
                
                ATTR.set(_textCurve,'rx',-90)
                mHandleFactory.color(_textCurve,'center','main',transparent = False)
                
                CORERIG.shapeParent_in_place(self.mNode,_textCurve,keepSource=False)
                
            
            #>> Helpers -----------------------------------------------------------------------------
            #======================
            _d = {'controlVis':['eye','x-','visControl'],
                  'controlSettings':['gear','x+','settingsControl']}
            
            _subSize = _offsetSize * 2
            
            pos_zForward = self.getPositionByAxisDistance('z+',(size[2]*.5) + (_offsetSize * 2.5))
            vec_xNeg = self.getAxisVector('x-')
            
            #cgmGEN.func_snapShot(vars())
            
            for k in _d.keys():
                #Make our node ------------------------------------------
                mHelper = self.getMessageAsMeta(k)
                newShape = CURVES.create_fromName(_d[k][0],_subSize,'y+')

                if not mHelper:
                    log.debug("|{0}| >> Creating: {1}".format(_str_func,k))
                    mHelper = cgmMeta.createMetaNode('cgmObject')
                    mHelper.p_parent = self.mNode
                    mHelper.rename(_d[k][2])
                    
                    ATTR.connect("{0}.{1}".format(self.mNode,_d[k][2]),"{0}.v".format(mHelper.mNode))
                    
                    if k == 'controlVis':
                        #mHelper.addAttr('controls',attrType = 'bool',keyable = False, initialValue = 1)
                        #mHelper.addAttr('subControls',attrType = 'bool',keyable = False, initialValue = 1)
                
                        self.controlVis = mHelper.mNode
                
                    elif k == 'controlSettings':
                        self.controlSettings = mHelper.mNode                    
                
                else:
                    log.debug("|{0}| >> Recreating shapes: {1}".format(_str_func,k))
                    mc.delete(mHelper.getShapes())
                    
                SNAP.go(newShape,mHelper.mNode)
                CORERIG.shapeParent_in_place(mHelper.mNode,newShape,keepSource=False)
                
                mHelper.setAttrFlags(attrs=['t'],lock=False)
                mHandleFactory.color(mHelper.mNode,'center','sub',transparent = False)
                
                vec_use = self.getAxisVector(_d[k][1])
                pos = DIST.get_pos_by_vec_dist(pos_zForward,vec_use, size[0]*.5)
                
                mHelper.p_position = pos
                mHelper.setAttrFlags(attrs=['t','r','s','v'],lock=True,visible=False)
            
            for mShape in self.getShapes(asMeta=True):
                mShape.doName()
            return True
        
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
    def rebuildControlCurveBAK(self,**kws):
        """
        Rebuild the master control curve
        """
        try:
            _str_func = 'cgmRigMaster.rebuildControlCurve'
            _short = self.mNode
            log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
            
            l_shapes = self.getShapes()
            #self.color =  modules.returnSettingsData('colorMaster',True)
            
            #>>> Figure out the control size 	
            size = kws.get('size',None)
            font = kws.get('font',None)
            if size == None:#
                if l_shapes:
                    size = DIST.get_bb_size(self.mNode,True,True)
                else:
                    size = [10,10,10]
                    
            log.debug("|{0}| >> size: {1}".format(_str_func,size))
            
            
                    
            #>>> Figure out font	
            if font == None:#
                if kws and 'font' in kws.keys():font = kws.get('font')		
                else:font = 'arial'
                
            #>>> Delete shapes
            if l_shapes:
                mc.delete(l_shapes)
    
            #>>> Build the new
            mCrv = cgmMeta.validateObjArg(CURVES.create_fromName('masterAnim',[size[0],None,size[2]],'z+'),'cgmObject',setClass=True)
            CORERIG.shapeParent_in_place(self.mNode,mCrv.mNode,keepSource=False)       
            l_shapes = self.getShapes(fullPath=True)
            CORERIG.override_color(l_shapes[0],'yellow')
            CORERIG.override_color(l_shapes[1],'white')        
            
            #i_o = cgmMeta.cgmObject( curves.createControlCurve('masterAnim',size))#Create and initialize
            #curves.setCurveColorByName( i_o.mNode,self.color[0] )
            #curves.setCurveColorByName( i_o.getShapes()[1],self.color[1] )
    
            #>>> Build the text curve if cgmName exists
            if self.hasAttr('cgmName'):
                nameSize = DIST.get_bb_size(l_shapes[1],True,True)
                log.info(l_shapes[1])
                log.info(nameSize)
                _textCurve = CURVES.create_text(self.cgmName, size = nameSize * .8, font = font)
                ATTR.set(_textCurve,'rx',-90)
                CORERIG.override_color(_textCurve,'yellow')
                CORERIG.shapeParent_in_place(self.mNode,_textCurve,keepSource=False)
    
    
            self.doName()    
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
    def getBlockModule(self,update = False):
        if self._blockModule and not update:
            return self._blockModule
        return get_blockModule('master')
    p_blockModule = property(getBlockModule)
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# MODULE Base class
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 


moduleStates = ['define','form','deform','rig']

initLists = []
initDicts = ['infoNulls','parentTagDict']
initStores = ['ModuleNull','refState']
initNones = ['refPrefix','moduleClass']

defaultSettings = {'partType':'none'}

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
moduleNulls_toMake = ['rig'] #These will be created and connected to a module and parented under them    

rigNullAttrs_toMake = {'version':'string',#Attributes to be initialzed for any module
                       'gutsLock':'int',
                       'gutsVis':'int',                       
                       'dynSwitch':'messageSimple'}

formNullAttrs_toMake = {'version':'string',
                            'gutsLock':'int',
                            'gutsVis':'int',
                            'controlsVis':'int',
                            'controlsLock':'int',
                            'root':'messageSimple',#The module root                            
                            'handles':'int',                            
                            'formStarterData':'string',#this will be a json dict
                            'controlObjectFormPose':'string'}

class cgmRigModule(cgmMeta.cgmObject):
    def __init__(self,*args,**kws):
        """ 
        Intializes an module master class handler
        Args:
        node = existing module in scene
        name = treated as a base name

        Keyword arguments:
        moduleName(string) -- either base name or the name of an existing module in scene
        moduleParent(string) -- module parent to connect to. MUST exist if called. If the default False flag is passed, it looks for what's stored

        Naming and form tags. All Default to False
        position(string) -- position tag
        direction(string) -- direction
        directionModifier(string)
        nameModifier(string)
        forceNew(bool) --whether to force the creation of another if the object exists
        """
        
        try:    
            super(cgmRigModule, self).__init__(*args,**kws)
            
            _str_func = ' cgmRigModule.__init__ [{0}]'.format(self)
            log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)        
            self._blockModule=None
            #====================================================================================	
            #>>> TO USE Cached instance ---------------------------------------------------------
            if self.cached:
                log.debug('CACHE : Aborting __init__ on pre-cached {0} Object'.format(self))
                return
            #====================================================================================

            doVerify = kws.get('doVerify') or False
            if self.__justCreatedState__ or doVerify:
                if not self.__verify__(*args,**kws):
                    raise StandardError,"Failed to verify!"
                
                
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
    def doName(self):
        return self.atUtils('doName')
    
    def atUtils(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        #try:
        #    reload(MODULEUTILS)
        #except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        return getattr(MODULEUTILS,func)(self,*args,**kws)            
        
        #return self.stringModuleCall(MODULEUTILS,func,*args, **kws)
    UTILS = MODULEUTILS
    
    def __verify__(self,**kws):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """
        try:
            _str_func = ' cgmModule.__verify__ '.format(self)
            log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)        
            
            self.addAttr('mClass', initialValue='cgmModule',lock=True) 
            self.addAttr('cgmType',value = 'module',lock=True)
            
            _b_nameDict = True
            _nameDict = kws.get('nameDict',False)
            if not _nameDict:
                _b_nameDict = False
                _nameDict = {}
            
            if not kws.get('rigBlock'):
                if kws.get('name'):#If we have a name, store it
                    _nameDict['cgmName'] = kws.get('name') or kws.get('mType')
                    #self.addAttr('cgmName',kws.get('name'),attrType='string',lock=True)

            if self.getMayaAttr('cgmType') != 'module':
                raise ValueError,"not a module: {0}".format(self)
            
            #kws
            #-------------------------------------------------------------------
            """for k,v in kws.iteritems():
                if self.hasAttr(k):
                    try:self.k = v
                    except Exception,err:
                        log.error("|{0}| Failed to set: {1}|{2}".format(_str_func,k,v,err))"""

            for k,v in kws.iteritems():
                if k in ['position','direction','directionModifier','nameModifier','iterator']:
                    if kws.get(k):
                        log.debug("|{0}| >> kw key: {1}".format(_str_func,k))
                        _nameDict['cgm'+k.capitalize()] = kws.get(k)
                        #self.addAttr('cgm'+k.capitalize(),value = kws.get(k),lock = True)                
                elif self.hasAttr(k):
                    try:self.k = v
                    except Exception,err:
                        log.error("|{0}| Failed to set: {1}|{2}".format(_str_func,k,v,err))
                        
                        
            #rigBlock
            #--------------------------------------------------------------------------------
            _moduleType = kws.get('moduleType','base')
            if kws.get('rigBlock'):
                _moduleLink = kws.get('moduleLink','moduleTarget')
                mRigBlock = cgmMeta.validateObjArg(kws.get('rigBlock'),'cgmRigBlock')
                if mRigBlock:
                    log.debug("|{0}| >> rigBlock on call: {1}".format(_str_func,mRigBlock))
                    ATTR.set_message(mRigBlock.mNode, _moduleLink, self.mNode,simple = True)
                    ATTR.set_message(self.mNode, 'rigBlock', mRigBlock.mNode,simple = True)
                    
            mRigBlock = self.getMessageAsMeta('rigBlock')
            if mRigBlock:
                if not _b_nameDict:
                    _nameDict_block = mRigBlock.getNameDict(ignore='cgmType')
                    _nameDict.update(_nameDict_block)
                    
                    if not _nameDict.get('cgmName'):
                        _nameDict['cgmName'] = kws.get('moduleType',mRigBlock.blockType)

                _side = mRigBlock.atUtils('get_side')
        
                if _side != 'center':
                    log.debug("|{0}| >> rigBlock side: {1}".format(_str_func,_side))
                    _nameDict['cgmDirection'] = _side
            
            for k,v in _nameDict.iteritems():
                if v:
                    log.debug("|{0}| >> Name dat k: {1} | v:{2}".format(_str_func,k,v))                
                    self.addAttr(k,value = v,lock = True)
                
            
            #Attributes
            #--------------------------------------------------------------------------------
            self.addAttr('moduleType',initialValue = _moduleType,lock=True)
    
            self.addAttr('moduleParent',attrType='messageSimple')#Changed to message for now till Mark decides if we can use single
            self.addAttr('modulePuppet',attrType='messageSimple')
            self.addAttr('moduleChildren',attrType='message')
    
            #stateDict = {'formState':0,'rigState':0,'skeletonState':0} #Initial dict
            #self.addAttr('moduleStates',attrType = 'string', initialValue=stateDict, lock = True)
    
            self.addAttr('rigNull',attrType='messageSimple',lock=True)
            self.addAttr('deformNull',attrType='messageSimple',lock=True)	
            

            #Groups
            #--------------------------------------------------------------------------------
            for attr in moduleNulls_toMake:
                mGrp = self.getMessage(attr+'Null')
                if not mGrp:
                    mGrp = cgmMeta.cgmObject(name=attr)
                    mGrp.connectParentNode(self.mNode,'module', attr+'Null')
                    mGrp.addAttr('cgmType',attr+'Null',lock=True)
                else:
                    mGrp = mGrp[0]
                    
                log.debug("|{0}| >> {1} group: {2}".format(_str_func,attr,mGrp))                            
                
                mGrp.parent = self
                mGrp.doName()
                
                mGrp.setAttrFlags()
                #attributes.doSetLockHideKeyableAttr( self.__dict__[Attr].mNode )
                
            mRigNull = self.rigNull

            #Attrbute checking
            #--------------------------------------------------------------------------------
            for a,t in rigNullAttrs_toMake.iteritems():
                mRigNull.addAttr(a,attrType=t)
            #self.__verifyAttributesOn__(self.i_rigNull,rigNullAttrs_toMake)
            #self.__verifyAttributesOn__(self.i_formNull,formNullAttrs_toMake)
    
            #Set Module Parent if we have that kw
            #=================		
            if kws.get('moduleParent'):
                _target = kws.get('moduleParent')
                log.debug("|{0}| >> moduleParent: {1}".format(_str_func,_target))                            
                raise NotImplemented,'Not finished moduleParent on call yet...'
                self.doSetParentModule(self.kw_moduleParent)
 
            self.doName()  
            return True
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
    def controller_get(self,verify=False):
        return cgmMeta.controller_get(self,verify)
    
    def get_allModuleChildren(self,*args,**kws):
        return MODULEUTILS.moduleChildren_get(self,*args,**kws)
        #return self.atUtils('moduleChildren_get',*args,**kws)
    def get_partNameBase(self,*args,**kws):
        return MODULEUTILS.get_partName(self,*args,**kws)
        #return self.atUtils('get_partName',*args,**kws)
    def verify_objectSet(self,*args,**kws):
        return MODULEUTILS.verify_objectSet(self,*args,**kws)        
        #return self.atUtils('verify_objectSet',*args,**kws)    
    def get_mirrorSideAsString(self,*args,**kws):
        return MODULEUTILS.mirror_getSideString(self,*args,**kws)                
        #return self.atUtils('mirror_getSideString',*args,**kws)
    def rig_getSkinJoints(self,asMeta=True):
        return MODULEUTILS.rig_getSkinJoints(self,asMeta)                        
        #return self.atUtils('rig_getSkinJoints',asMeta)
    
    def getBlockModule(self,update = False):
        if self._blockModule and update != False:
            return self._blockModule
        blockType = self.getMayaAttr('moduleType')
        self._blockModule = get_blockModule(blockType)
        return self._blockModule
    p_blockModule = property(getBlockModule)
    def atBlockModule(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        #try:
        #    reload(self.getBlockModule())
        #except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        return getattr(self._blockModule,func)(self,*args,**kws)            
        
        #return self.stringModuleCall(self._blockModule,func,*args, **kws)    
    
    
    def rig_reset(self):
        return self.UTILS.rig_reset(self)
    def rig_connect(self):
        return self.UTILS.rig_connect(self)
    def rig_disconnect(self):
        return self.UTILS.rig_disconnect(self)
    def rig_isConnected(self):
        return self.UTILS.rig_isConnected(self)    
#Profile stuff ==============================================================================================
def get_blockProfile_options(arg):
    try:
        _str_func = 'get_blockProfile_options'
        
        mBlockModule = get_blockModule(arg)
        
        log.debug("|{0}| >>  {1}".format(_str_func,arg)+ '-'*80)
        
        log.debug("|{0}| >>  BlockModule: {1}".format(_str_func,mBlockModule))
        #if mBlockModule:reload(mBlockModule)
        
        try:return mBlockModule.d_block_profiles.keys()
        except Exception,err:
            log.error("|{0}| >>  [{2}] Failed to query. | {1} ".format(_str_func,err,arg))
        return []
        
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================    
r9Meta.registerMClassInheritanceMapping()#Pushes our classes in













