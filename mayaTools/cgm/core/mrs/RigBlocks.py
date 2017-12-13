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
log.setLevel(logging.DEBUG)
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
from cgm.core.mrs.lib import builder_utils as BUILDERUTILS
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
reload(BUILDERUTILS)
from cgm.core.lib import nameTools
reload(BLOCKSHARE)
from cgm.core.classes import GuiFactory as CGMUI
reload(CGMUI)
import cgm.core.tools.lib.snap_calls as SNAPCALLS
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
                 'baseSize':'float3',
                 'blockState':'string',
                 'blockDat':'string',#...for pickle? 
                 'blockParent':'messageSimple',
                 'blockMirror':'messageSimple'}
d_defaultAttrSettings = {'blockState':'define'}

def get_callSize(mode = None, arg = None, blockType = None, default = [1,1,1]):
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
            return [float(v) for v in arg]
        _sel = mc.ls(sl=True)

        if mode is None:
            log.debug("|{0}| >>  mode is None...".format(_str_func))
            if not arg:
                if blockType:
                    blockModule = get_blockModule(blockType)
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
                    if not VALID.valueArg(v):
                        _valueList = False
                        break
                if _valueList:
                    return floatValues(mode)
                
            arg = VALID.objStringList(mode)
            mode = 'selection'

        mode = mode.lower()
        if mode == 'selection':
            size = POS.get_axisBox_size(arg,True)
            #if rigBlock:
                #log.info("|{0}| >>  Created from obj. Tagging. | {1}".format(_str_func,arg))        
                #rigBlock.connectChildNode(arg,'sourceObj')#Connect
        elif mode in ['boundingbox','bb']:
            size = POS.get_bb_size(arg, False)

        _res = floatValues(size)
        log.info("|{0}| >>  mode: {1} | arg: '{2}' | size: {3}".format(_str_func,mode,arg,_res))        
        return floatValues(_res)
    except Exception,err:
        cgmGEN.cgmException(Exception,err)

class cgmRigBlock(cgmMeta.cgmControl):
    #These lists should be set up per rigblock as a way to get controls from message links
    _l_controlLinks = []
    _l_controlmsgLists = []

    def __init__(self, node = None, blockType = None, blockParent = None, autoTemplate = True, *args,**kws):
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
        
        if node is None:
            _sel = mc.ls(sl=1)            
            _callSize = get_callSize(_size)

            if  _sel:
                pos_target = TRANS.position_get(_sel[0])
                log.debug("|{0}| >> pos_target: {1}".format(_str_func,pos_target))                                
                if pos_target[0] >= .05:
                    _side = 'left'
                elif pos_target[0] <= -.05:
                    _side = 'right'            

        log.debug("|{0}| >> size: {1}".format(_str_func, _callSize))

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
            log.info('CACHE : Aborting __init__ on pre-cached {0} Object'.format(self))
            return
        #====================================================================================	
        #for a in 'p_blockState','testinasdfasdfasdf':
            #if a not in self.UNMANAGED:
                #self.UNMANAGED.append(a) 	


        #====================================================================================
        #Keywords - need to set after the super call
        #==============         
        _doVerify = kws.get('doVerify',False) or False
        self._factory = factory(self.mNode)
        self._callKWS = kws
        self._blockModule = None
        self._callSize = _callSize
        #self.UNMANAGED.extend(['kw_name','kw_moduleParent','kw_forceNew','kw_initializeOnly','kw_callNameTags'])	
        #>>> Initialization Procedure ================== 
        try:
            if self.__justCreatedState__ or _doVerify:
                kw_name = kws.get('name',None)
                if kw_name:
                    self.addAttr('cgmName',kw_name)
                    if blockType == 'master':
                        self.addAttr('puppetName',kw_name)
                else:
                    self.addAttr('cgmName',attrType='string')


                log.debug("|{0}| >> Just created or do verify...".format(_str_func))            
                if self.isReferenced():
                    log.error("|{0}| >> Cannot verify referenced nodes".format(_str_func))
                    return
                elif not self.verify(blockType,side= _side):
                    raise RuntimeError,"|{0}| >> Failed to verify: {1}".format(_str_func,self.mNode)

                #Name -----------------------------------------------

                #>>>Auto flags...
                #Template
                _blockModule = get_blockModule(self.blockType)
                if autoTemplate and _blockModule.__dict__.get('__autoTemplate__'):
                    log.debug("|{0}| >> AutoTemplate...".format(_str_func))  
                    try:
                        self.p_blockState = 'template'
                    except Exception,err:
                        for arg in err.args:
                            log.error(arg)

                #Snap with selection mode --------------------------------------
                if _size in ['selection']:
                    log.info("|{0}| >> Selection mode snap...".format(_str_func))                      
                    if _sel:
                        if  blockType in ['master']:
                            SNAPCALLS.snap(self.mNode,_sel[0],rotation=False,targetPivot='groundPos')
                        else:
                            log.info("|{0}| >> Selection mode snap to: {1}".format(_str_func,_sel))                                              
                            self.doSnapTo(_sel[0])
                #cgmGEN.func_snapShot(vars())
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err)

        #self._blockModule = get_blockModule(ATTR.get(self.mNode,'blockType'))        

    def verify(self, blockType = None, size = None, side = None):
        """ 

        """
        _str_func = '[{0}] verify'.format(self.p_nameShort)

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

        _side = side
        if _side is not None and self._callKWS.get('side'):
            _side = self._callKWS.get('side')

        if _side is not None:
            try: ATTR.set(self.mNode,'side',_side)
            except Exception,err:
                log.error("|{0}| >> Failed to set side. {1}".format(_str_func,err))


        #>>> Base shapes --------------------------------------------------------------------------------
        #_size = self._callKWS.get('size')
        #log.info("|{0}| >> size: {1}".format(_str_func, self._callSize))  
        #get_callSize(self._callKWS.get('size'), blockModule=_mBlockModule, rigBlock = self)
        try:self.baseSize = self._callSize
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,fncDat=vars())


        _mBlockModule = get_blockModule(self.blockType)
        if 'define' in _mBlockModule.__dict__.keys():
            log.debug("|{0}| >> BlockModule define call found...".format(_str_func))            
            _mBlockModule.define(self)      
        self._blockModule = _mBlockModule

        self.doName()
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

        _blockType = ATTR.get(_short,'blockType')
        _d['cgmType'] = _blockType + 'Block'

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

        _ml_prerigHandles = self.msgList_get('prerigHandles',asMeta = True)
        if not _ml_prerigHandles:
            return False

        _ml_controls = [self] + _ml_prerigHandles

        _l_orientHelpers = []
        _l_jointHelpers = []

        for i,mObj in enumerate(_ml_prerigHandles):
            log.info("|{0}| >>  {1} | {2}".format(_str_func,i,mObj.mNode))
            if mObj.getMessage('orientHelper'):
                _l_orientHelpers.append(mObj.orientHelper.rotate)
            else:
                _l_orientHelpers.append(False)
            if mObj.getMessage('jointHelper'):
                _l_jointHelpers.append(mObj.jointHelper.translate)
            else:
                _l_jointHelpers.append(False)

        _d = {'positions':[mObj.p_position for mObj in _ml_prerigHandles],
              'orientations':[mObj.p_orient for mObj in _ml_prerigHandles],
              'scales':[mObj.scale for mObj in _ml_prerigHandles],
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
        try:
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
        _str_func = '[{0}]changeState'.format(self.mNode)
        start = time.clock()

        _res = self._factory.changeState(state)
        log.info("{0} >> Time >> = {1} seconds ".format(_str_func, "%0.3f"%(time.clock()-start)) + "-"*75)

        #log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)
        return _res

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

        mModule = self.moduleTarget
        if not mModule:
            raise ValueError,"No moduleTarget connected"

        mRigNull = mModule.rigNull
        if not mRigNull:
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


    #========================================================================================================     
    #>>> Mirror 
    #========================================================================================================      
    @staticmethod
    def MirrorBlock(rootBlock = None, mirrorBlock = None, reflectionVector = MATH.Vector3(1,0,0) ):
        try:
            '''Mirrors the template positions from the block to the mirrorBlock across the reflection vector transformed from the root block'''
            _str_func = 'MirrorBlock'
    
            if not rootBlock or not mirrorBlock:
                log.warning("|{0}| >> Must have rootBlock and mirror block".format(_str_func))                                            
                return
    
            if mirrorBlock.blockType != rootBlock.blockType:
                log.warning("|{0}| >> Blocktypes must match. | {1} != {2}".format(_str_func,block.blockType,mirrorBlock.blockType,))                                                        
                return
            
            rootTransform = rootBlock
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
                
                #cgmGEN.func_snapShot(vars())
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
    @staticmethod
    def MirrorSelectedBlocks( reflectionVector = MATH.Vector3(1,0,0) ):
        '''Mirrors the template positions from the block to the mirrorBlock across the reflection vector transformed from the root block'''

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
        '''Mirrors the given block using the mirrorBlock's template positions'''

        mirrorBlock = block.GetMirrorBlock()

        Block.MirrorBlock(mirrorBlock, block, reflectionVector)





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

    def verify_proxyMesh(self, forceNew = True):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        _str_func = 'verify_proxyMesh'        
        if self.getState() != 'rig':
            log.error("|{0}| >> Block must be rigged. {1}".format(_str_func, self.mNode))            
            return False
        
        mRigFac = rigFactory(self, autoBuild = False)
        return mRigFac.atBlockModule('build_proxyMesh', forceNew)
    

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
        self._baseSize = get_callSize(baseSize)

        #if node is None:
            #self._mTransform = cgmMeta.createMetaNode('cgmObject',nodeType = 'transform', nameTools = baseShape)
            #self.rebuildSimple(baseShape,baseSize,shapeDirection)
        if node is not None:
            self.setHandle(node)

    def setHandle(self,arg = None):
        #if not VALID.is_transform(arg):
            #raise ValueError,"must be a transform"

        self._mTransform = cgmMeta.validateObjArg(arg,'cgmObject')
        if not self._mTransform.hasAttr('baseSize'):
            ATTR.add(self._mTransform.mNode,'baseSize','float3')
            self._mTransform.baseSize = 1.0,1.0,1.0
            ATTR.set_hidden(self._mTransform.mNode,'baseSize',False)

    def rebuildSimple(self, baseShape = None, baseSize = None, shapeDirection = 'z+'):
        self.cleanShapes()

        if baseShape is None:
            baseShape = 'square'

        self._mTransform.addAttr('baseShape', baseShape,attrType='string')

        SNAP.verify_aimAttrs(self._mTransform.mNode, aim = 'z+', up = 'y+')

        if baseSize is not None:
            baseSize = get_callSize(baseSize)
            self._mTransform.baseSize = baseSize

        _baseSize = self._mTransform.baseSize

        _baseShape = self._mTransform.getMayaAttr('baseShape') 
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

    def color(self, target = None, side = None, controlType = None, transparent = None):
        _str_func = 'handleFactory.color'
        log.info("|{0}| >> ".format(_str_func)+ '-'*80)
        _targets = VALID.listArg(target)
        log.info("|{0}| >> target: [{1}]".format(_str_func, _targets))
        
        mTransform = self._mTransform
        if side is None:
            _side = self.get_side()
        else:
            log.info("|{0}| >> arg side: {1}".format(_str_func, side))            
            _side = side
            
        if transparent is None:
            _transparent = True
        else:
            log.info("|{0}| >> arg transparent: {1}".format(_str_func, transparent))            
            _transparent = transparent
                
        if controlType is None:
            _controlType = 'main'        
        else:
            log.info("|{0}| >> arg controlType: {1}".format(_str_func, controlType))                        
            _controlType = controlType
        
        for t in _targets:
            if t is None:
                t = self._mTransform.mNode
                
            if VALID.is_shape(t):
                _shapes = [t]
            else:
                _shapes = TRANS.shapes_get(t)
            
            for s in _shapes:
                _useType = _controlType
                if controlType is not None:
                    log.info("|{0}| >> Setting controlType: {1}".format(_str_func, controlType))                                            
                    ATTR.store_info(s,'cgmControlType',controlType)
                    
                if transparent is not None and VALID.get_mayaType(s) in ['mesh','nurbsSurface']:
                    log.info("|{0}| >> Setting transparent: {1}".format(_str_func, transparent))                                                                
                    ATTR.store_info(s,'cgmControlTransparent',transparent)
                    
                if ATTR.has_attr(s,'cgmControlType'):
                    _useType = ATTR.get(s,'cgmControlType')
                    log.info("|{0}| >> Shape has cgmControlType tag: {1}".format(_str_func,_useType))                
                log.info("|{0}| >> s: {1} | side: {2} | controlType: {3}".format(_str_func, s, _side, _useType))            
                    
                CORERIG.colorControl(s,_side,_useType,transparent = _transparent)


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
            _baseSize = get_callSize(baseSize)
        elif self._mTransform.getShapes():
            _baseSize = POS.get_axisBox_size(self._mTransform.mNode,False)
        elif self._mTransform.hasAttr('baseSize'):
            _baseSize = self._mTransform.baseSize
        else:
            _baseSize = [1.0,1.0,1.0]

        return [_baseShape,_baseSize]


    def buildBaseShape(self, baseShape = None, baseSize = None, shapeDirection = 'z+' ):
        _baseDat = self.get_baseDat(baseShape,baseSize)
        _baseShape = _baseDat[0]
        _baseSize = _baseDat[1]

        if _baseShape not in ['sphere']:
            _baseSize = [_baseSize[0],_baseSize[1],None]

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

    def get_side(self):
        _side = 'center'
        mHandle = self._mTransform        
        if mHandle.getMayaAttr('side'):
            _side = mHandle.getEnumValueString('side')
        return _side

    def addPivotSetupHelper(self,baseShape=None, baseSize = None, upAxis = 'y+', setAttrs = {}):
        try:
            _str_func = 'addPivotSetupHelper'
            mHandle = self._mTransform
            _short = mHandle.mNode
            _side = self.get_side()

            _baseDat = self.get_baseDat(baseShape,baseSize)
            _baseShape = _baseDat[0]
            _baseSize = _baseDat[1]

            _bbsize = POS.get_axisBox_size(mHandle.mNode,False)
            _size = MATH.average(_bbsize)
            _sizeSub = _size * .2

            _bfr = mHandle.getMessage('scalePivotHelper')
            if _bfr:
                mc.delete(_bfr)


            ml_pivots = []
            mPivotRootHandle = False
            self_pos = mHandle.p_position
            self_upVector = mHandle.getAxisVector(upAxis)

            d_pivotDirections = {'back':'z-',
                                 'front':'z+',
                                 'left':'x+',
                                 'right':'x-'}        
            _axisBox = False

            for a in ['pivotBack','pivotFront','pivotLeft','pivotRight','pivotCenter']:
                _strPivot = a.split('pivot')[-1]
                _strPivot = _strPivot[0].lower() + _strPivot[1:]
                log.info("|{0}| >> Adding pivot helper: {1}".format(_str_func,_strPivot))
                if _strPivot == 'center':
                    pivot = CURVES.create_controlCurve(mHandle.mNode, shape='circle',
                                                       direction = upAxis,
                                                       sizeMode = 'fixed',
                                                       size = _sizeSub)
                    mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                    mPivot.addAttr('cgmName',_strPivot)
                    ml_pivots.append(mPivot)
                else:
                    if not _axisBox:
                        _axisBox = CORERIG.create_axisProxy(self._mTransform.mNode)

                    mAxis = VALID.simpleAxis(d_pivotDirections[_strPivot])
                    _inverse = mAxis.inverse.p_string
                    pivot = CURVES.create_controlCurve(mHandle.mNode, shape='hinge',
                                                       direction = _inverse,
                                                       sizeMode = 'fixed', size = _sizeSub)
                    mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                    mPivot.addAttr('cgmName',_strPivot)

                    #mPivot.p_position = DIST.get_pos_by_axis_dist(_short,mAxis.p_string, _size/2)
                    SNAPCALLS.snap(mPivot.mNode,_axisBox,rotation=False,targetPivot='castNear',targetMode=mAxis.p_string)

                    SNAP.aim_atPoint(mPivot.mNode,self_pos, _inverse, upAxis, mode='vector', vectorUp = self_upVector)

                    ml_pivots.append(mPivot)

                    if not mPivotRootHandle:
                        pivotHandle = CURVES.create_controlCurve(mHandle.mNode, shape='squareOpen',
                                                                 direction = upAxis,
                                                                 sizeMode = 'fixed', size = _size * 1.25)
                        mPivotRootHandle = cgmMeta.validateObjArg(pivotHandle,'cgmObject',setClass=True)
                        mPivotRootHandle.addAttr('cgmName','base')
                        mPivotRootHandle.addAttr('cgmType','pivotHelper')            
                        mPivotRootHandle.doName()

                        CORERIG.colorControl(mPivotRootHandle.mNode,_side,'sub') 

                        #mPivotRootHandle.parent = mPrerigNull
                        mHandle.connectChildNode(mPivotRootHandle,'pivotHelper','block')#Connect    

                        if mHandle.hasAttr('addPivot'):
                            mHandle.doConnectOut('addPivot',"{0}.v".format(mPivotRootHandle.mNode))
                        self._mTransform.msgList_append('prerigHandles',mPivotRootHandle)

            if _axisBox:
                mc.delete(_axisBox)
            for mPivot in ml_pivots:
                mPivot.addAttr('cgmType','pivotHelper')            
                mPivot.doName()

                CORERIG.colorControl(mPivot.mNode,_side,'sub') 
                mPivot.parent = mPivotRootHandle
                mPivotRootHandle.connectChildNode(mPivot,'pivot'+ mPivot.cgmName.capitalize(),'handle')#Connect    
                self._mTransform.msgList_append('prerigHandles',mPivot)

            if self._mTransform.getShapes():
                SNAPCALLS.snap(mPivotRootHandle.mNode,self._mTransform.mNode,rotation=False,targetPivot='axisBox',targetMode='y-')

            return mPivotRootHandle
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

    def addScalePivotHelper(self,baseShape=None, baseSize = None, shapeDirection = 'z+', setAttrs = {}):
        _baseDat = self.get_baseDat(baseShape,baseSize)
        _baseShape = _baseDat[0]
        _baseSize = _baseDat[1]
        _side = self.get_side()

        mHandle = self._mTransform
        _bfr = mHandle.getMessage('scalePivotHelper')
        if _bfr:
            mc.delete(_bfr)


        _sizeSub = self.get_subSize(.5)


        #helper ======================================================================================
        _curve = CURVES.create_controlCurve(mHandle.mNode,'arrowsScaleOut',  direction= shapeDirection, sizeMode = 'fixed', size = _sizeSub)
        mCurve = cgmMeta.validateObjArg(_curve, mType = 'cgmObject',setClass=True)

        if mHandle.hasAttr('cgmName'):
            ATTR.copy_to(mHandle.mNode,'cgmName',mCurve.mNode,driven='target')
        mCurve.doStore('cgmType','scalePivotHelper')
        mCurve.doName()    

        mCurve.p_parent = mHandle

        for a,v in setAttrs.iteritems():
            ATTR.set(mCurve.mNode, a, v)

        CORERIG.match_transform(mCurve.mNode, mHandle)
        mCurve.connectParentNode(mHandle.mNode,'handle','scalePivotHelper')      
        CORERIG.colorControl(mCurve.mNode,_side,'sub')

        if mHandle.hasAttr('addScalePivot'):
            mHandle.doConnectOut('addScalePivot',"{0}.v".format(mCurve.mNode))

        self._mTransform.msgList_append('prerigHandles',mCurve.mNode)
        return mCurve    

    def get_subSize(self,mult = .2):
        mHandle = self._mTransform        
        _bbsize = POS.get_axisBox_size(mHandle.mNode)
        _size = MATH.average(_bbsize)
        _sizeSub = _size * mult
        return _sizeSub

    def addCogHelper(self,baseShape=None, baseSize = None, shapeDirection = 'z+', setAttrs = {}):
        try:
            _baseDat = self.get_baseDat(baseShape,baseSize)
            _baseShape = _baseDat[0]
            _baseSize = _baseDat[1]
            _plug = 'cogHelper'
            _side = self.get_side()
            upAxis = 'y+'

            mHandle = self._mTransform
            _short = mHandle.mNode

            _bfr = mHandle.getMessage(_plug)
            if _bfr:
                mc.delete(_bfr)

            _sizeSub = self.get_subSize(.25)
            _sizeByBB = [_sizeSub, _sizeSub * .5, _sizeSub]
            self_pos = mHandle.p_position
            self_upVector = mHandle.getAxisVector(upAxis)

            #helper ======================================================================================
            d_shapeDirections = {'back':'z-',
                                 'front':'z+',
                                 'left':'x+',
                                 'right':'x-'}
            ml_shapes = []
            for d,axis in d_shapeDirections.iteritems():
                mAxis = VALID.simpleAxis(axis)
                _inverse = mAxis.inverse.p_string
                shape = CURVES.create_controlCurve(mHandle.mNode, shape='arrowSingleFat3d',
                                                   direction = axis,
                                                   sizeMode = 'fixed', size = _sizeByBB)
                mShape = cgmMeta.validateObjArg(shape,'cgmObject',setClass=True)

                mShape.p_position = DIST.get_pos_by_axis_dist(_short,mAxis.p_string, _baseSize[0]/1.75)
                SNAP.aim_atPoint(mShape.mNode,self_pos, _inverse, upAxis, mode='vector', vectorUp = self_upVector)

                ml_shapes.append(mShape)

                #mCurve.scaleY = 2
                #mCurve.scaleZ = .75
            mCurve = cgmMeta.validateObjArg(CORERIG.combineShapes([mObj.mNode for mObj in ml_shapes],keepSource=False),
                                            'cgmObject',setClass=True)


            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mCurve.mNode,driven='target')
            mCurve.doStore('cgmType',_plug)
            mCurve.doName()    

            mCurve.p_parent = mHandle

            for a,v in setAttrs.iteritems():
                ATTR.set(mCurve.mNode, a, v)

            CORERIG.match_transform(mCurve.mNode, mHandle)
            mCurve.connectParentNode(mHandle.mNode,'handle',_plug)

            CORERIG.colorControl(mCurve.mNode,_side,'sub')

            if mHandle.hasAttr('addCog'):
                mHandle.doConnectOut('addCog',"{0}.v".format(mCurve.mNode))

            self._mTransform.msgList_append('prerigHandles',mCurve.mNode)

            return mCurve    
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

    def setAttrs_fromDict(self, setAttrs={}):
        try:
            mHandle = self._mTransform   
            _short = mHandle.mNode

            for a,v in setAttrs.iteritems():
                ATTR.set(_short, a, v)
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

    def addOrientHelper(self,baseShape=None, baseSize = None, shapeDirection = 'z-', setAttrs = {}):
        try:
            _baseDat = self.get_baseDat(baseShape,baseSize)
            _baseShape = _baseDat[0]
            _baseSize = _baseDat[1]

            mHandle = self._mTransform
            _short = mHandle.mNode
            _bfr = mHandle.getMessage('orientHelper')
            if _bfr:
                mc.delete(_bfr)

            _size = MATH.average(_baseSize[:1])

            #Orientation helper ======================================================================================
            _orientHelper = CURVES.create_controlCurve(mHandle.mNode,'arrowSingle',  direction= shapeDirection, sizeMode = 'fixed', size = _size * .75)
            mCurve = cgmMeta.validateObjArg(_orientHelper, mType = 'cgmObject',setClass=True)


            mCurve.p_position = DIST.get_pos_by_axis_dist(_short,shapeDirection, _size/1.75)

            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mCurve.mNode,driven='target')        
            mCurve.doStore('cgmType','orientHandle')
            mCurve.doName()    

            mCurve.p_parent = mHandle

            for a,v in setAttrs.iteritems():
                ATTR.set(mCurve.mNode, a, v)

            CORERIG.match_transform(mCurve.mNode, mHandle)
            mCurve.connectParentNode(mHandle.mNode,'handle','orientHelper')      

            return mCurve
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

    def addProxyHelper(self,baseShape=None, baseSize = None, shapeDirection = 'z+', setAttrs = {}):
        try:
            _baseDat = self.get_baseDat(baseShape,baseSize)
            _baseShape = _baseDat[0]
            _baseSize = _baseDat[1]
            _side = self.get_side()
            #cgmGEN.func_snapShot(vars())
            mHandle = self._mTransform
            _short = mHandle.mNode
            _bfr = mHandle.getMessage('proxyHelper')

            if _bfr:
                mc.delete(_bfr)

            _proxyShape = mHandle.getEnumValueString('proxyShape')

            #Orientation helper ======================================================================================
            _proxy = CORERIG.create_proxyGeo(_proxyShape, _baseSize, shapeDirection)
            mProxy = cgmMeta.validateObjArg(_proxy[0], mType = 'cgmObject',setClass=True)

            mProxy.doSnapTo(mHandle)

            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mProxy.mNode,driven='target')        
            mProxy.doStore('cgmType','proxyHelper')
            mProxy.doName()    

            mProxy.p_parent = mHandle

            self.setAttrs_fromDict(setAttrs)

            CORERIG.colorControl(mProxy.mNode,_side,'sub',transparent=True)

            mProxy.connectParentNode(mHandle.mNode,'handle','proxyHelper')

            if mHandle.hasAttr('proxyVis'):
                mHandle.doConnectOut('proxyVis',"{0}.v".format(mProxy.mNode))

            return mProxy
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

    def addRootMotionHelper(self,baseShape='arrowsAxis', baseSize = None, shapeDirection = 'z+'):
        try:
            _baseDat = self.get_baseDat(baseShape,baseSize)
            _baseShape = _baseDat[0]
            _baseSize = _baseDat[1]

            mHandle = self._mTransform
            _bfr = mHandle.getMessage('rootMotionHelper')
            if _bfr:
                mc.delete(_bfr)

            _size = MATH.average(_baseSize[:1]) * .1


            #helper ======================================================================================
            _str_curve = CURVES.create_controlCurve(mHandle.mNode, baseShape,  direction= shapeDirection, sizeMode = 'fixed', size = _size)

            mCurve = cgmMeta.validateObjArg(_str_curve, mType = 'cgmObject',setClass=True)


            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mCurve.mNode,driven='target')
            mCurve.doStore('cgmType','rootMotionHelper')
            mCurve.doName()    

            mCurve.p_parent = mHandle


            CORERIG.match_transform(mCurve.mNode, mHandle)


            mCurve.connectParentNode(mHandle.mNode,'handle','rootMotionHelper')   
            if mHandle.hasAttr('addMotionJoint'):
                mHandle.doConnectOut('addMotionJoint',"{0}.v".format(mCurve.mNode))
                ATTR.set_standardFlags(mCurve.mNode,['v'])

            self._mTransform.msgList_append('prerigHandles',mCurve.mNode)
            return mCurve
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

    def addJointHelper(self,baseShape=None, baseSize = None, shapeDirection = 'z-', loftHelper = True, lockChannels = ['rotate','scale']):
        try:
            _baseDat = self.get_baseDat(baseShape,baseSize)
            _baseShape = _baseDat[0]
            _baseSize = _baseDat[1]

            mHandle = self._mTransform
            _bfr = mHandle.getMessage('jointHelper')
            if _bfr:
                mc.delete(_bfr)

            _size = MATH.average(_baseSize[:1]) * .3


            #Joint helper ======================================================================================
            _jointHelper = CURVES.create_controlCurve(mHandle.mNode,'sphere',  direction= shapeDirection, sizeMode = 'fixed', size = _size)
            mJointCurve = cgmMeta.validateObjArg(_jointHelper, mType = 'cgmObject',setClass=True)

            if mHandle.hasAttr('cgmName'):
                ATTR.copy_to(mHandle.mNode,'cgmName',mJointCurve.mNode,driven='target')
            mJointCurve.doStore('cgmType','jointHandle')
            mJointCurve.doName()    

            mJointCurve.p_parent = mHandle

            self.color(mJointCurve.mNode)

            CORERIG.match_transform(mJointCurve.mNode, mHandle)

            #mc.transformLimits(mJointCurve.mNode, tx = (-.5,.5), ty = (-.5,.5), tz = (-.5,.5),
            #                   etx = (True,True), ety = (True,True), etz = (True,True))        

            mJointCurve.connectParentNode(mHandle.mNode,'handle','jointHelper')   

            mJointCurve.setAttrFlags(lockChannels)

            if loftHelper:#...loft curve -------------------------------------------------------------------------------------
                mLoft = self.buildBaseShape('square',_size*.5,'y+')
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
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

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
                cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
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

    def rig(self,**kws):
        #Master control
        if self._mi_block is None:
            raise ValueError,"No root loaded."
        _mBlock = self._mi_block
        _short = _mBlock.mNode
        if _mBlock.isReferenced():
            raise ValueError,"Referenced node."

        _str_func = '[{0}] factory.rig'.format(_mBlock.p_nameBase)
        _str_state = _mBlock.blockState


        if _mBlock.blockState != 'prerig':
            raise ValueError,"{0} is not in prerig state. state: {1}".format(_str_func, _str_state)      

        #>>>Children ------------------------------------------------------------------------------------


        #>>>Meat ------------------------------------------------------------------------------------
        _mBlock.blockState = 'prerig>rig'#...buffering that we're in process
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
        mi_puppet = False
        if self._mi_block.blockType == 'master':
            if not _mBlock.getMessage('moduleTarget'):
                mi_puppet = cgmRigPuppet(name = _mBlock.puppetName)
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
                for mBlockParent in _mBlock.getBlockParents():
                    if mBlockParent.blockType == 'master':
                        log.debug("|{0}| >> Found puppet on blockParent: {1}".format(_str_func,mBlockParent))                                                
                        mi_puppet = mBlockParent.moduleTarget
                if not mi_puppet:
                    mi_puppet = cgmRigPuppet(name = mi_module.getNameAlias())

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
                            cgmGEN.cgmExceptCB(Exception,e,fncDat=vars())

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
    reload(_BlockModule)
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
                print("|{0}| >> [{1}] FAIL. Missing rig step {2} call: {3}".format(_str_func,_blockType,i,step))
    elif getattr(_BlockModule,'rig',[]):
        log.info("|{0}| >> BlockModule rig call found...".format(_str_func))
    else:
        _status = False

    if _status:
        print("|{0}| >> [{1}] Pass: valid rig build order ".format(_str_func,_blockType))                            
        return _l_buildOrder
    return False

_l_requiredModuleDat = ['__version__',
                        'template','is_template','templateDelete',
                        'prerig','is_prerig','prerigDelete',
                        'rig','is_rig','rigDelete']

_d_requiredModuleDat = {'define':['__version__'],
                        'template':['template','is_template','templateDelete'],
                        'prerig':['prerig','is_prerig','prerigDelete'],
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
        for state in ['define','template','prerig','rig']:
            l_tests = _d_requiredModuleDat[state]
            l_functionTests = _d_requiredModuleDatCalls.get(state,[])            
            _good = True
            print("|{0}| >> [{1}]{2}".format(_str_func,_blockType,state.capitalize()) + cgmGEN._str_subLine)            
            for test in l_tests:
                try:
                    if not getattr(_buildModule, test, False):
                        print("|{0}| >> [{1}] FAIL: {2}".format(_str_func,_blockType,test))
                        _good = False  
                    else:
                        print("|{0}| >> [{1}] Pass: {2}".format(_str_func,_blockType,test))
                except Exception,err:
                    print("|{0}| >> [{1}] FAIL: {2} | {3}".format(_str_func,_blockType,test,err))
            for test in l_functionTests:
                try:
                    if not test(_blockType):
                        _good = False
                except Exception,err:
                    print("|{0}| >> [{1}] FAIL: {2} | {3}".format(_str_func,_blockType,test,err))   
            _res[state] = _good

            if state == 'define':
                print("|{0}| >> [{1}] version: {2}".format(_str_func,_blockType,_buildModule.__dict__.get('__version__',False)))            

    else:
        l_tests = _d_requiredModuleDat[state]
        l_functionTests = _d_requiredModuleDatCalls.get(state,[])
        _res = True
        for test in l_tests:
            if not getattr(_buildModule, test, False):
                print("|{0}| >> [{1}] Missing {3} data: {2}".format(_str_func,_blockType,test,state))
                _res = False
        for test in l_functionTests:
            try:
                if not test(_blockType):
                    #print("|{0}| >> [{1}] Missing {3} data: {2}".format(_str_func,_blockType,test,state))
                    _res = False                
            except Exception,err:
                print("|{0}| >> [{1}] FAIL: {2} | {3}".format(_str_func,_blockType,test,err))   
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
    @cgmGEN.Timer    
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

        try:self.fnc_check_rigBlock()
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=self.__dict__)

        try:self.fnc_check_module()
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=self.__dict__)

        try:self.fnc_rigNeed()
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=self.__dict__)

        try:self.fnc_bufferDat()
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=self.__dict__)

        if not self.fnc_moduleRigChecks():
            pprint.pprint(self.__dict__)            
            raise RuntimeError,"|{0}| >> Failed to process module rig Checks. See warnings and errors.".format(_str_func)

        try:self.fnc_deformConstrainNulls()
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=self.__dict__)

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
        _blockModule = reload(self.d_block['buildModule'])
        self.d_block['buildModule'] = _blockModule
        return cgmGEN.stringModuleClassCall(self, _blockModule, func, *args, **kws)

    def atBuilderUtils(self, func = '', *args,**kws):
        """
        Function to call a blockModule function by string. For menus and other reasons
        """
        try:reload(BUILDERUTILS)
        except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err)
        return cgmGEN.stringModuleClassCall(self, BUILDERUTILS, func, *args, **kws)

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
    def fnc_check_rigBlock(self):
        """
        Check the rig block data 
        """
        _str_func = 'fnc_check_rigBlock' 
        _d = {}
        _res = True

        if not self.call_kws['rigBlock']:
            raise RuntimeError,'No rigBlock stored in call kws'

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


        #Build order --------------------------------------------------------------------------------
        _d['buildOrder'] = valid_blockModule_rigBuildOrder(_buildModule)
        if not _d['buildOrder']:
            raise RuntimeError,'Failed to validate build order'

        self.d_block = _d    

        self.buildModule = _buildModule
        log.debug("|{0}| >> passed...".format(_str_func)+ cgmGEN._str_subLine)

        return True

    @cgmGEN.Timer
    def fnc_check_module(self):
        _str_func = 'fnc_check_module'  
        _res = True
        BlockFactory = self.d_block['mFactory']

        _hasModule = True
        if BlockFactory._mi_block.blockType in ['master']:
            _hasModule = False


        #>>Module -----------------------------------------------------------------------------------  
        _d = {}    

        if _hasModule:
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
        else:
            _mPuppet = self.mBlock.moduleTarget

        self.mPuppet = _mPuppet

        _d['mPuppet'] = _mPuppet
        _mPuppet.verify_groups()

        if _hasModule:
            if not _mModule.isSkeletonized():
                log.warning("|{0}| >> Module isn't skeletonized. Attempting".format(_str_func))

                if not self.mBlock.atBlockModule('build_skeleton'):
                    log.warning("|{0}| >> Skeletonization failed".format(_str_func))            
                    _res = False

        self.d_module = _d    
        log.debug("|{0}| >> passed...".format(_str_func)+ cgmGEN._str_subLine)
        return _res    

    @cgmGEN.Timer
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


        #>>> Object Set -----------------------------------------------------------------------------------
        self.mModule.verify_objectSet()

        log.debug("|{0}| >> passed...".format(_str_func)+ cgmGEN._str_subLine)
        return _res

    @cgmGEN.Timer
    def fnc_rigNeed(self):
        """
        Function to check if a go instance needs to be rigged

        """
        _str_func = 'fnc_rigNeed'  

        _mModule = self.d_module.get('mModule')
        _mModuleParent = self.d_module.get('mModuleParent')
        _version = self.d_module.get('version')
        _buildVersion = self.d_block.get('buildVersion')
        _buildModule = self.buildModule
        _blockType = self.mBlock.blockType

        _d_callKWS = self.call_kws

        if _blockType == 'master':
            _b_rigged = True
        else:
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
            if _d_callKWS['forceNew'] and _b_rigged:
                log.warning("|{0}| >> Force new and is rigged. Deleting rig...NOT IMPLEMENTED".format(_str_func))                    
                #_mModule.rigDelete()
            else:
                log.info("|{0}| >> Up to date.".format(_str_func))                    
                return False

        return True

    @cgmGEN.Timer
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

    @cgmGEN.Timer
    def log_self(self):
        pprint.pprint(self.__dict__)

    @cgmGEN.Timer
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
                _d['partName'] = _mModule.getPartNameBase()
                _d['partType'] = _mModule.moduleType.lower() or False

                _d['l_moduleColors'] = _mModule.getModuleColors() 
                _d['l_coreNames'] = []#...need to do this
                self.mTemplateNull = _mModule.templateNull
                _d['mTemplateNull'] = self.mTemplateNull
                _d['bodyGeo'] = _mPuppet.getGeo() or ['Morphy_Body_GEO']
                _d['direction'] = _mModule.getAttr('cgmDirection')

                _d['mirrorDirection'] = _mModule.get_mirrorSideAsString()
            else:
                _d['mirrorDirection'] = 'Centre'

            _d['f_skinOffset'] = _mPuppet.getAttr('skinDepth') or 1
            _d['mMasterNull'] = _mPuppet.masterNull

            #>MasterControl....
            if not _mPuppet.getMessage('masterControl'):
                log.info("|{0}| >> Creating masterControl...".format(_str_func))                    
                _mPuppet.verify_masterControl(size = max(POS.get_axisBox_size(self.mBlock.mNode)) * 1.5)

            _d['mMasterControl'] = _mPuppet.masterControl
            _d['mPlug_globalScale'] =  cgmMeta.cgmAttr(_d['mMasterControl'].mNode,'scaleY')	 
            _d['mMasterSettings'] = _d['mMasterControl'].controlSettings
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
                    log.warning("|{0}| >> No module joints found".format(_str_func))
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
            cgmGEN.cgmExceptCB(Exception,err,localDat==vars())
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
            _l_buildOrder = self.d_block['buildModule'].__dict__.get('__l_rigBuildOrder__')
            if not _l_buildOrder:
                raise ValueError,"No build order found"
            _len = len(_l_buildOrder)

            if not _len:
                log.error("|{0}| >> No steps to build!".format(_str_func))                    
                return False
            #Build our progress Bar
            mayaMainProgressBar = CGMUI.doStartMayaProgressBar(_len)

            for i,fnc in enumerate(_l_buildOrder):
                #str_name = d_build[k].get('name','noName')
                #func_current = d_build[k].get('function')
                #_str_subFunc = str_name
                #_str_subFunc = fnc.__name__

                mc.progressBar(mayaMainProgressBar, edit=True,
                               status = "|{0}| >>Rigging>> step: {1}...".format(_str_func,fnc), progress=i+1)    

                getattr(self.d_block['buildModule'],fnc)(self)

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


            CGMUI.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
        except Exception,err:
            CGMUI.doEndMayaProgressBar()#Close out this progress bar
            cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

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
    
            if self.__justCreatedState__ or doVerify:
                if self.isReferenced():
                    log.error("|{0}| >> Cannot verify referenced nodes".format(_str_func))
                    return
                elif not self.__verify__(name,**kws):
                    raise RuntimeError,"|{0}| >> Failed to verify: {1}".format(_str_func,self.mNode)
        except Exception,err:cgmGEN.cgmException(Exception,err)
        
    #====================================================================================
    def __verify__(self,name = None):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """
        try:
            _short = self.p_nameShort
            _str_func = "cgmRigPuppet.__verify__({0})".format(_short)
            log.debug("|{0}| >> ...".format(_str_func))
    
            #============== 
            #Puppet Network Node ================================================================
            self.addAttr('mClass', initialValue='cgmRigPuppet',lock=True)  
            if name is not None and name:
                self.addAttr('cgmName',name, attrType='string', lock = True)
            self.addAttr('cgmType','puppetNetwork')
            self.addAttr('version',initialValue = 1.0, lock=True)  
            self.addAttr('masterNull',attrType = 'messageSimple',lock=True)  
            self.addAttr('masterControl',attrType = 'messageSimple',lock=True)  	
            self.addAttr('moduleChildren',attrType = 'message',lock=True) 
            self.addAttr('unifiedGeo',attrType = 'messageSimple',lock=True) 
    
            #Settings ============================================================================
            #defaultFont = modules.returnSettingsData('defaultTextFont')
            defaultFont = BLOCKSHARE.str_defaultFont
            self.addAttr('font',attrType = 'string',initialValue=defaultFont,lock=True)   
            self.addAttr('axisAim',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=2) 
            self.addAttr('axisUp',enumName = 'x+:y+:z+:x-:y-:z-', attrType = 'enum',initialValue=1) 
            self.addAttr('axisOut',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=0) 
            self.addAttr('skinDepth',attrType = 'float',initialValue=.75,lock=True)   
    
            self.doName()
    
            #MasterNull ===========================================================================
            self.verify_masterNull()

                
            if self.masterNull.getShortName() != self.cgmName:
                self.masterNull.doName()
                if self.masterNull.getShortName() != self.cgmName:
                    log.warning("Master Null name still doesn't match what it should be.")
            
            ATTR.set_standardFlags(self.masterNull.mNode,attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
            #self.verify_groups()
    
    
            #Quick select sets ================================================================
            self.verify_objectSet()
    
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # Groups
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
            self.verify_groups()
    
            return True
        except Exception,err:cgmGEN.cgmException(Exception,err)
    
    def atFactory(self, func = 'get_report', *args,**kws):
        """
        Function to call a self function by string. For menus and other reasons
        """
        try:
            _str_func = 'cgmRigPuppet.atFactory'
            log.debug("|{0}| >> ...".format(_str_func))            
            _short = self.p_nameShort
            _res = None
            
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
                log.debug("|{0}| >> On: {1}".format(_str_func,_short))     
                log.debug("|{0}| >> {1}.{2}({3}{4})...".format(_str_func,_short,func,_str_args,_kwString))                                    
                _res = getattr(pFactory,func)(*args,**kws)
            except Exception,err:
                log.error(cgmGEN._str_hardLine)
                log.error("|{0}| >> Failure: {1}".format(_str_func, err.__class__))
                log.error("Node: {0} | func: {1}".format(_short,func))            
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
            return _res
        except Exception,err:cgmGEN.cgmException(Exception,err)
        
    def changeName(self,name = ''):
        try:
            _str_func = 'cgmRigPuppet.changeName'
            log.debug("|{0}| >> ...".format(_str_func))
            
            if name == self.cgmName:
                log.error("Puppet already named '%s'"%self.cgmName)
                return
            if name != '' and type(name) is str:
                log.warn("Changing name from '%s' to '%s'"%(self.cgmName,name))
                self.cgmName = name
                self.__verify__()
        except Exception,err:cgmGEN.cgmException(Exception,err)

    def verify_masterNull(self,**kws):
        try:
            _str_func = 'cgmRigPuppet.verify_masterNull'
            log.debug("|{0}| >> ...".format(_str_func))
    
            if not self.getMessage('masterNull'):
                mMasterNull = cgmMeta.cgmObject()
            else:
                mMasterNull = self.masterNull
                
            ATTR.copy_to(self.mNode,'cgmName',mMasterNull.mNode,driven='target')
            mMasterNull.addAttr('puppet',attrType = 'messageSimple')
            if not mMasterNull.connectParentNode(self.mNode,'puppet','masterNull'):
                raise StandardError,"Failed to connect masterNull to puppet network!"
    
            mMasterNull.addAttr('mClass',value = 'cgmMasterNull',lock=True)
            mMasterNull.addAttr('cgmName',initialValue = '',lock=True)
            mMasterNull.addAttr('cgmType',initialValue = 'ignore',lock=True)
            mMasterNull.addAttr('cgmModuleType',value = 'master',lock=True)   
            mMasterNull.addAttr('partsGroup',attrType = 'messageSimple',lock=True)   
            mMasterNull.addAttr('deformGroup',attrType = 'messageSimple',lock=True)   	
            mMasterNull.addAttr('noTransformGroup',attrType = 'messageSimple',lock=True)   
            mMasterNull.addAttr('geoGroup',attrType = 'messageSimple',lock=True)   
    
            #See if it's named properly. Need to loop back after scene stuff is querying properly
            mMasterNull.doName()
            return True
        except Exception,err:cgmGEN.cgmException(Exception,err)

    #=================================================================================================
    # Puppet Utilities
    #=================================================================================================
    def verify_groups(self):
        try:
            _str_func = "cgmRigPuppet.verify_groups".format()
            log.debug("|{0}| >> ...".format(_str_func))
            
            mMasterNull = self.masterNull
            
            if not mMasterNull:
                raise ValueError, "No masterNull"
            
            for attr in 'deform','noTransform','geo','parts','worldSpaceObjects','puppetSpaceObjects':
                _link = attr+'Group'
                mGroup = mMasterNull.getMessage(_link,asMeta=True)# Find the group
                if mGroup:mGroup = mGroup[0]
                                                    
                if not mGroup:
                    mGroup = cgmMeta.cgmObject(name=attr)#Create and initialize
                    mGroup.doName()
                    mGroup.connectParentNode(mMasterNull.mNode,'puppet', attr+'Group')
                    
                log.debug("|{0}| >> attr: {1} | mGroup: {2}".format(_str_func, attr, mGroup))
    
                # Few Case things
                #==============            
                if attr in ['geo','parts']:
                    mGroup.p_parent = mMasterNull.noTransformGroup
                elif attr in ['deform','puppetSpaceObjects'] and self.getMessage('masterControl'):
                    mGroup.p_parent = self.getMessage('masterControl')[0]	    
                else:    
                    mGroup.p_parent = mMasterNull
                    
                ATTR.set_standardFlags(mGroup.mNode)
                
                if attr == 'worldSpaceObjects':
                    mGroup.addAttr('cgmAlias','world')
                elif attr == 'puppetSpaceObjects':
                    mGroup.addAttr('cgmAlias','puppet')
        except Exception,err:cgmGEN.cgmException(Exception,err)


    def verify_objectSet(self):
        try:
            _str_func = "cgmRigPuppet.verify_objectSet"
            log.debug("|{0}| >> ...".format(_str_func))
            
            #Quick select sets ================================================================
            mSet = self.getMessage('puppetSet',asMeta=True)
            if mSet:
                mSet = mSet[0]
            else:#
                mSet = cgmMeta.cgmObjectSet(setType='animSet',qssState=True)
                mSet.connectParentNode(self.mNode,'puppet','puppetSet')
    
            ATTR.copy_to(self.mNode,'cgmName',mSet.mNode,'cgmName',driven = 'target')
            mSet.doName()
        except Exception,err:cgmGEN.cgmException(Exception,err)

    """
    def doName(self,sceneUnique=False,nameChildren=False,**kws):
        #if not self.getTransform() and self.__justCreatedState__:
            #log.error("Naming just created nodes, causes recursive issues. Name after creation")
            #return False
        if self.isReferenced():
            log.error("'%s' is referenced. Cannot change name"%self.mNode)
            return False
        mc.rename(self.mNode,nameTools.returnCombinedNameFromDict(self.getNameDict()))"""

    def delete(self):
        """
        Delete the Puppet
        """
        try:
            _str_func = "cgmRigPuppet.delete"
            log.debug("|{0}| >> ...".format(_str_func))
            
            mc.delete(self.masterNull.mNode)
            #mc.delete(self.mNode)
            del(self)
        except Exception,err:cgmGEN.cgmException(Exception,err)

    def addModule(self,mClass = 'cgmModule',**kws):
        """
        Create and connect a new module

        moduleType(string) - type of module to create

        p = cgmPM.cgmRigPuppet(name='Morpheus')
        p.addModule(mClass = 'cgmLimb',mType = 'torso')
        p.addModule(mClass = 'cgmLimb',mType = 'neck', moduleParent = 'spine_part')
        p.addModule(mClass = 'cgmLimb',mType = 'head', moduleParent = 'neck_part')
        p.addModule(mClass = 'cgmLimb',mType = 'arm',direction = 'left', moduleParent = 'spine_part')
        """
        try:
            _str_func = "cgmRigPuppet.addModule"
            log.debug("|{0}| >> ...".format(_str_func))            

            if mClass == 'cgmModule':
                tmpModule = cgmModule(**kws)   
            elif mClass == 'cgmLimb':
                tmpModule = cgmLimb(**kws)
            else:
                log.warning("'%s' is not a known module type. Cannot initialize"%mClass)
                return False
    
            self.connectModule(tmpModule)
            return tmpModule
        except Exception,err:cgmGEN.cgmException(Exception,err)

    ##@r9General.Timer
    def connectModule(self,module,force = True,**kws):
        """
        Connects a module to a puppet

        module(string)
        """
        try:
            _str_func = "cgmRigPuppet.connectModule"
            log.debug("|{0}| >> ...".format(_str_func))
    
            #See if it's connected
            #If exists, connect
            #Get instance
            #==============	
            buffer = copy.copy(self.getMessage('moduleChildren')) or []#Buffer till we have have append functionality	
            #self.i_masterNull = self.masterNull
    
            try:
                module.mNode#see if we have an instance
                if module.mNode in buffer and force != True:
                    #log.warning("'%s' already connnected to '%s'"%(module.getShortName(),self.i_masterNull.getShortName()))
                    return False 	    
            except:
                if mc.objExists(module):
                    if mc.ls(module,long=True)[0] in buffer and force != True:
                        #log.warning("'%s' already connnected to '%s'"%(module,self.i_masterNull.getShortName()))
                        return False
    
                    module = r9Meta.MetaClass(module)#initialize
    
                else:
                    log.warning("'%s' doesn't exist"%module)#if it doesn't initialize, nothing is there		
                    return False	
    
            #Logic checks
            #==============	
            if not module.hasAttr('mClass'):
                log.warning("'%s' lacks an mClass attr"%module.mNode)	    
                return False
    
            elif module.mClass not in cgmModuleTypes:
                log.warning("'%s' is not a recognized module type"%module.mClass)
                return False
    
            #Connect
            #==============	
            else:
                #if log.getEffectiveLevel() == 10:log.debug("Current children: %s"%self.getMessage('moduleChildren'))
                #if log.getEffectiveLevel() == 10:log.debug("Adding '%s'!"%module.getShortName())    
    
                buffer.append(module.mNode)
                self.__setMessageAttr__('moduleChildren',buffer) #Going to manually maintaining these so we can use simpleMessage attr  parents
                module.modulePuppet = self.mNode
                #del self.moduleChildren
                #self.connectChildren(buffer,'moduleChildren','modulePuppet',force=force)#Connect	    
                #module.__setMessageAttr__('modulePuppet',self.mNode)#Connect puppet to 
    
            #module.parent = self.i_partsGroup.mNode
            module.doParent(self.masterNull.partsGroup.mNode)
    
            return True
        except Exception,err:cgmGEN.cgmException(Exception,err)

    def getGeo(self):
        return pFactory.getGeo(self)

    def getUnifiedGeo(self,*args,**kws):
        kws['mPuppet'] = self	
        return pFactory.getUnifiedGeo(*args,**kws)

    def getModuleFromDict(self,*args,**kws):
        """
        Pass a check dict of attributes and arguments. If that module is found, it returns it.
        checkDict = {'moduleType':'torso',etc}
        """
        kws['mPuppet'] = self	
        return pFactory.getModuleFromDict(*args,**kws)

    def getModules(self,*args,**kws):
        """
        Returns ordered modules. If you just need modules, they're always accessible via self.moduleChildren
        """
        kws['mPuppet'] = self	
        return pFactory.getModules(*args,**kws)   

    def getOrderedModules(self,*args,**kws):
        """
        Returns ordered modules. If you just need modules, they're always accessible via self.moduleChildren
        """
        kws['mPuppet'] = self		
        return pFactory.getOrderedModules(*args,**kws)

    def get_mirrorIndexDict(self,*args,**kws):
        """
        """
        kws['mPuppet'] = self			
        return pFactory.get_mirrorIndexDict(*args,**kws)

    def state_set(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.setState)
        """
        kws['mPuppet'] = self	
        return pFactory.state_set(*args,**kws)

    def get_nextMirrorIndex(self,*args,**kws):
        """
        """
        kws['mPuppet'] = self			
        return pFactory.get_nextMirrorIndex(*args,**kws) 

    def gatherModules(self,*args,**kws):
        """
        Gathers all connected module children to the puppet
        """
        kws['mPuppet'] = self
        return pFactory.gatherModules(*args,**kws)    

    def getState(self,*args,**kws):
        """
        Returns puppet state. That is the minimum state of it's modules
        """
        kws['mPuppet'] = self	
        return pFactory.getState(*args,**kws) 

    #>>> Animation
    #========================================================================
    def animSetAttr(self,*args,**kws):
        kws['mPuppet'] = self
        return pFactory.animSetAttr(*args,**kws) 

        #return pFactory.animSetAttr(self,attr, value, settingsOnly)
    def controlSettings_setModuleAttrs(self,*args,**kws):
        kws['mPuppet'] = self
        return pFactory.controlSettings_setModuleAttrs(*args,**kws)     

    def toggle_subVis(self):
        try:
            self.masterControl.controlVis.subControls = not self.masterControl.controlVis.subControls
        except:pass

    def anim_key(self,**kws):
        _str_func = "%s.animKey()"%self.p_nameShort  
        start = time.clock()
        b_return = None
        _l_callSelection = mc.ls(sl=True) or []
        try:
            try:buffer = self.puppetSet.getList()
            except:buffer = []
            if buffer:
                mc.select(buffer)
                mc.setKeyframe(**kws)
                b_return =  True
            b_return = False
            log.info("%s >> Complete Time >> %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)     
            if _l_callSelection:mc.select(_l_callSelection)                	    
            return b_return
        except Exception,error:
            log.error("%s.animKey>> animKey fail | %s"%(self.getBaseName(),error))
            return False

    def mirrorMe(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.mirrorMe(*args,**kws)

    def mirror_do(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.mirror_do(*args,**kws)

    def mirrorSetup_verify(self,**kws):
        kws['mPuppet'] = self			
        return pFactory.mirrorSetup_verify(**kws)   

    def anim_reset(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.animReset(*args,**kws)

    def anim_select(self):
        _str_func = "%s.anim_select()"%self.p_nameShort  
        start = time.clock()
        try:self.puppetSet.select()
        except:pass
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)     
        return buffer

    def isCustomizable(self):
        return False 

    def isTemplated(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.isTemplated(*args,**kws)

    def templateSettings_call(self,*args,**kws):
        '''
        Call for doing multiple functions with templateSettings.

        :parameters:
            mode | string
        reset:reset controls
        store:store data to modules
        load:load data from modules
        query:get current data
        export:export to a pose file
        import:import from a  pose file
            filepath | string/None -- if None specified, user will be prompted
        '''
        kws['mPuppet'] = self			
        return pFactory.templateSettings_call(*args,**kws)

    def isSized(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.isSized(*args,**kws)
    
    def isSkeletonized(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.isSkeletonized(*args,**kws)
    
    def verify_masterControl(self,**kws):
        """ 
        """
        try:
            _str_func = "cgmRigPuppet.verify_masterControl"
            log.debug("|{0}| >> ...".format(_str_func))
            
            self.verify_groups()#...make sure everythign is there
            
            # Master Curve
            #==================================================================
            masterControl = attributes.returnMessageObject(self.mNode,'masterControl')
            if mc.objExists( masterControl ):
                mi_masterControl = self.masterControl
            else:
                #Get size
                if not kws.get('size'):
                    if self.getGeo():
                        averageBBSize = distance.returnBoundingBoxSizeToAverage(self.masterNull.geoGroup.mNode)
                        kws['size'] = averageBBSize * .75
                    elif len(self.moduleChildren) == 1 and self.moduleChildren[0].getMessage('helper'):
                        averageBBSize = distance.returnBoundingBoxSizeToAverage(self.moduleChildren[0].getMessage('helper'))		
                        kws['size'] = averageBBSize * 1.5
                    elif 'size' not in kws.keys():kws['size'] = 50
                mi_masterControl = cgmMasterControl(puppet = self,**kws)#Create and initialize
                mi_masterControl.__verify__()
            mi_masterControl.parent = self.masterNull.mNode
            mi_masterControl.doName()
            
    
            # Vis setup
            # Setup the vis network
            #====================================================================
            try:
                if not mi_masterControl.hasAttr('controlVis') or not mi_masterControl.getMessage('controlVis'):
                    log.error("This is an old master control or the vis control has been deleted. rebuild")
                else:
                    iVis = mi_masterControl.controlVis
                    visControls = 'left','right','sub','main'
                    visArg = [{'result':[iVis,'leftSubControls_out'],'drivers':[[iVis,'left'],[iVis,'subControls'],[iVis,'controls']]},
                              {'result':[iVis,'rightSubControls_out'],'drivers':[[iVis,'right'],[iVis,'subControls'],[iVis,'controls']]},
                              {'result':[iVis,'subControls_out'],'drivers':[[iVis,'subControls'],[iVis,'controls']]},		      
                              {'result':[iVis,'leftControls_out'],'drivers':[[iVis,'left'],[iVis,'controls']]},
                              {'result':[iVis,'rightControls_out'],'drivers':[[iVis,'right'],[iVis,'controls']]}
                              ]
                    nodeF.build_mdNetwork(visArg)
            except Exception,err:
                log.error("{0} >> visNetwork fail! {1}".format(_str_func,err))
                raise StandardError,err 	
    
            # Settings setup
            # Setup the settings network
            #====================================================================	
            i_settings = mi_masterControl.controlSettings
            str_nodeShort = str(i_settings.getShortName())
            #Skeleton/geo settings
            for attr in ['skeleton','geo','proxy']:
                i_settings.addAttr(attr,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
                nodeF.argsToNodes("%s.%sVis = if %s.%s > 0"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
                nodeF.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
    
            #Geotype
            #i_settings.addAttr('geoType',enumName = 'reg:proxy', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
            #for i,attr in enumerate(['reg','proxy']):
            #    nodeF.argsToNodes("%s.%sVis = if %s.geoType == %s:1 else 0"%(str_nodeShort,attr,str_nodeShort,i)).doBuild()    
            
            
            
            #Divider
            i_settings.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)
    
            #i_settings.addAttr('templateVis',attrType = 'float',lock=True,hidden = True)
            #i_settings.addAttr('templateLock',attrType = 'float',lock=True,hidden = True)	
            #i_settings.addAttr('templateStuff',enumName = 'off:on', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
            #nodeF.argsToNodes("%s.templateVis = if %s.templateStuff > 0"%(i_settings.getShortName(),i_settings.getShortName())).doBuild()
            #nodeF.argsToNodes("%s.templateLock = if %s.templateStuff == 1:0 else 2"%(i_settings.getShortName(),i_settings.getShortName())).doBuild()	
    
    
            #>>> Deform group
            #=====================================================================	
            if self.masterNull.getMessage('deformGroup'):
                self.masterNull.deformGroup.parent = mi_masterControl.mNode
    
            mi_masterControl.addAttr('cgmAlias','world',lock = True)
    
    
            #>>> Skeleton Group
            #=====================================================================	
            if not self.masterNull.getMessage('skeletonGroup'):
                #Make it and link it
                #i_grp = mi_masterControl.doDuplicateTransform()
                mGrp = cgmMeta.createMetaNode('cgmObject')
                mGrp.doSnapTo(mi_masterControl.mNode)
                
                #mGrp.doRemove('cgmName')
                mGrp.addAttr('cgmTypeModifier','skeleton',lock=True)	 
                mGrp.parent = mi_masterControl.mNode
                self.masterNull.connectChildNode(mGrp,'skeletonGroup','module')
    
                mGrp.doName()
            else:
                mGrp = self.masterNull.skeletonGroup
    
    
            #Verify the connections
            mGrp.overrideEnabled = 1             
            cgmMeta.cgmAttr(i_settings,'skeletonVis',lock=False).doConnectOut("%s.%s"%(mGrp.mNode,'overrideVisibility'))    
            cgmMeta.cgmAttr(i_settings,'skeletonLock',lock=False).doConnectOut("%s.%s"%(mGrp.mNode,'overrideDisplayType'))    
    
    
            #>>>Connect some flags
            #=====================================================================
            i_geoGroup = self.masterNull.geoGroup
            i_geoGroup.overrideEnabled = 1		
            cgmMeta.cgmAttr(i_settings.mNode,'geoVis',lock=False).doConnectOut("%s.%s"%(i_geoGroup.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(i_settings.mNode,'geoLock',lock=False).doConnectOut("%s.%s"%(i_geoGroup.mNode,'overrideDisplayType'))  
    
            try:self.masterNull.puppetSpaceObjectsGroup.parent = mi_masterControl
            except:pass
            
            return True
        except Exception,err:cgmGEN.cgmException(Exception,err)

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
        except Exception,err:cgmGEN.cgmException(Exception,err)

    @cgmGEN.Timer
    def __verify__(self,*args,**kws):
        try:
            _str_func = 'cgmRigMaster.__verify__'
            _short = self.mNode
            log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)                
            
            puppet = kws.pop('puppet',False)
            if puppet and not self.isReferenced():
                ATTR.copy_to(puppet.mNode,'cgmName',self.mNode,driven='target')
                self.connectParentNode(puppet,'puppet','masterControl')
            else:
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
            ATTR.set_alias(_short,'sy','blockScale')            
            
            
            #=====================================================================
            #>>> Curves!
            #=====================================================================
            #>>> Master curves
            _shapes = self.getShapes()
            if len(_shapes)<3:
                self.rebuildMasterShapes(**kws)

            self.doName()
    
            return True
        except Exception,err:cgmGEN.cgmException(Exception,err)

    ##@r9General.Timer
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
    
                    
            log.debug("|{0}| >> size: {1}".format(_str_func,size))
            
            _average = MATH.average([size[0],size[2]])
            _size = _average * 1.5
            _offsetSize = _average * .1
            
            mc.delete(l_shapes)
            
            mHandleFactory = handleFactory(_short)
            
                    
            #>>> Figure out font------------------------------------------------------------------
            if font == None:#
                if kws and 'font' in kws.keys():font = kws.get('font')		
                else:font = 'arial'
                
            #>>> Main shape ----------------------------------------------------------------------
            _crv = CURVES.create_fromName(name='squareOpen',direction = 'y+', size = 1)    
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
                        mHelper.addAttr('controls',attrType = 'bool',keyable = False, initialValue = 1)
                        mHelper.addAttr('subControls',attrType = 'bool',keyable = False, initialValue = 1)
                
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
                

                

                
                

            return True
        
        except Exception,err:cgmGEN.cgmException(Exception,err)
        
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
        except Exception,err:cgmGEN.cgmException(Exception,err)








#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================    
r9Meta.registerMClassInheritanceMapping()#Pushes our classes in













