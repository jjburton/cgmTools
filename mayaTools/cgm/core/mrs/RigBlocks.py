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



_l_requiredModuleDat = ['__version__','__d_controlShapes__','__l_jointAttrs__','__l_buildOrder__']#...data required in a given module

#from cgm.core.lib import nameTools
#from cgm.core.rigger import ModuleFactory as mFactory
#from cgm.core.rigger import PuppetFactory as pFactory
#from cgm.core.classes import NodeFactory as nodeF

#from cgm.core.mrs.blocks import box

#_d_blockTypes = {'box':box}

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Rig Blocks
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
d_attrstoMake = {'version':'string',#Attributes to be initialzed for any module
                 'buildAs':'string',
                 'blockType':'string',
                 #'autoMirror':'bool',
                 'direction':'none:left:right:center',
                 'position':'none:front:back:upper:lower:forward',
                 'moduleTarget':'messageSimple',
                 'blockMirror':'messageSimple'}


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

    def create_rigBlock(self,blockType = None, size = 1):
        _str_func = 'create_rigBlock'
        _start = time.clock()
        
        _d = get_modules_dict()
        
        if blockType not in _d.keys():
            log.error("|{0}| >> [{1}] | Failed to query type. Probably not a module".format(_str_func,blockType))        
            return False
        
        _module = _d[blockType]
        
        if 'create' not in _module.__dict__.keys():
            log.error("|{0}| >> [{1}] | Failed to query create function.".format(_str_func,blockType))        
            return False
        
        _mObj = _module.create(size = size)
        log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start))) 
        
        self.set_rigBlock(_mObj)
        self.verify(blockType)
        return _mObj


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

        try:d_defaultSettings = _mod.d_defaultSettings
        except:d_defaultSettings = {}

        try:_l_msgLinks = _mod._l_controlLinks
        except:_l_msgLinks = []

        _d = copy.copy(d_attrstoMake)
        for k,v in d_attrsFromModule.iteritems():
            if k in _d.keys():
                log.warning("|{0}| >> key: {1} already in to create list of attributes from default. | blockType: {2}".format(_str_func,k,blockType))                
            else:
                _d[k] = v

        if _l_msgLinks:
            for l in _l_msgLinks:
                _d[l] = 'messageSimple'

        cgmGEN.log_info_dict(_d,_str_func + " '{0}' attributes to create".format(blockType))
        #cgmGEN.log_info_dict(d_defaultSettings,_str_func + " '{0}' defaults".format(blockType))

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

        _mod = _d_blockTypes.get(blockType,False)
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
        _str_func = 'rigBlock_verify'

        if self._mi_block is None:
            raise ValueError,"No root loaded."

        _mRoot = self._mi_block

        if _mRoot.isReferenced():
            raise ValueError,"Referenced node. Cannot verify"
        
        if blockType == None:
            blockType = ATTR.get(_mRoot.mNode,'blockType')
        if not blockType:
            raise ValueError,"No blockType specified or found."

        if not self.get_attrCreateDict(blockType):
            raise ValueError, "|{0}| >> Failed to get attr dict. blockType:{1}".format(_str_func,blockType)

        #Need to get the type, the get the attribute lists and data from the module

        #_mRoot.verifyAttrDict(self._d_attrsToVerify,keyable = False, hidden = False)
        _mRoot.verifyAttrDict(self._d_attrsToVerify)
        
        #s_mRoot.blockType = blockType
        _mRoot.addAttr('blockType', value = blockType,lock=True)	
        _mRoot.blockState = 'template'

        for k,v in self._d_attrToVerifyDefaults.iteritems():
            log.info("|{0}| type: ({3}) >>  Setting attr >> '{1}' | value: {2} ".format(_str_func,k,v,blockType)) 
            _mRoot.addAttr(k, initialValue = v, keyable = False, hidden = False)
            #try:ATTR.set(_mRoot.mNode,k,v)
            #except Exception,err:
                #log.error("|{0}| >> Failed to set default value. || key: {1} | value: {2} ||| err: {3}".format(_str_func,k,v,err))                

        return True


        return False
        #>>> Block transform ==================                   
        _mRoot.addAttr('mClass', initialValue='cgmRigBlock',lock=True) 
        _mRoot.addAttr('cgmType', value = 'rigHelper',lock=True)	

        if self.kw_name:#If we have a name, store it
            _mRoot.addAttr('cgmName',self.kw_name,attrType='string',lock=True)
        elif 'buildAs' in kws.keys():
            _mRoot.addAttr('cgmName',kws['buildAs'],attrType='string',lock=True)	    

        #Store tags from init call
        #==============  
        for k in self.kw_callNameTags.keys():
            if self.kw_callNameTags.get(k):
                self.addAttr(k,value = self.kw_callNameTags.get(k),lock = True)


        #Attrbute checking
        #=================
        self.verifyAttrDict(d_rigBlockAttrs_toMake,keyable = False, hidden = False)
        d_enumToCGMTag = {'cgmDirection':'direction','cgmPosition':'position'}
        for k in d_enumToCGMTag.keys():
            if k in self.kw_callNameTags.keys():
                try:self.__setattr__(d_enumToCGMTag.get(k),self.kw_callNameTags.get(k))
                except Exception,error: log.error("%s.__verify__ >>> Failed to set key: %s | data: %s | error: %s"%(self.p_nameShort,k,self.kw_callNameTags.get(k),error))

        self.doName()   

        return True        

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

    def skeletonize(self,forceNew = False):
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
        _mRoot = self._mi_block        

        _bfr = _mRoot.getMessage('moduleTarget')
        _kws = self.module_getBuildKWS()

        if _bfr:
            log.debug("|{0}| >> moduleTarget found: {1}".format(_str_func,_bfr))            
            mModule = cgmMeta.validateObjArg(_bfr,'cgmObject')
        else:
            log.debug("|{0}| >> Creating moduleTarget...".format(_str_func))   
            mModule = PUPPETMETA.cgmModule(**_kws)

        ATTR.set_message(_mRoot.mNode, 'moduleTarget', mModule.mNode,simple = True)
        ATTR.set_message(mModule.mNode, 'rigHelper', _mRoot.mNode,simple = True)

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
        _mRoot = self._mi_block

        d_kws = {}
        d_kws['name'] = str(_mRoot.blockType)

        #Direction
        str_direction = _mRoot.getEnumValueString('direction')
        log.debug("|{0}| >> direction: {1}".format(_str_func,str_direction))            
        if str_direction in ['left','right']:
            d_kws['direction'] = str_direction
        #Position
        str_position = _mRoot.getEnumValueString('position')	
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
        _mRoot = self._mi_block     

        mi_module = _mRoot.moduleTarget
        if not mi_module:
            mi_module = self.module_verify()

        _bfr = mi_module.getMessage('modulePuppet')
        if _bfr:
            log.debug("|{0}| >> modulePuppet found: {1}".format(_str_func,_bfr))                        
            mi_puppet = mi_module.modulePuppet
            self._mi_puppet = mi_puppet
            return mi_puppet            

        mi_puppet = PUPPETMETA.cgmPuppet(name = mi_module.getNameAlias())

        mi_puppet.connectModule(mi_module)	

        if mi_module.getMessage('moduleMirror'):
            mi_puppet.connectModule(mi_module.moduleMirror)

        mi_puppet.gatherModules()#Gather any modules in the chain
        self._mi_puppet = mi_puppet
        return mi_puppet        


def get_posList_fromStartEnd(start=[0,0,0],end=[0,1,0],split = 1):
    _str_func = 'get_posList_fromStartEnd'
    _base = 'joint_base_placer'
    _top = 'joint_top_placer'  

    #>>Get positions ==================================================================================    
    _l_pos = []

    if split == 1:
        _l_pos = [DIST.get_average_position([start,end])]
    elif split == 2:
        _l_pos = [start,end]
    else:
        _vec = MATH.get_vector_of_two_points(start, end)
        _max = DIST.get_distance_between_points(start,end)

        log.debug("|{0}| >> start: {1} | end: {2} | vector: {3}".format(_str_func,start,end,_vec))   

        _split = _max/(split-1)
        for i in range(split-1):
            _p = DIST.get_pos_by_vec_dist(start, _vec, _split * i)
            _l_pos.append( _p)
        _l_pos.append(end)
        _radius = _split/4    
    return _l_pos

def build_skeleton(positionList = [], joints = 1, axisAim = 'z+', axisUp = 'y+', worldUpAxis = [0,1,0],asMeta = True):
    _str_func = 'build_skeleton'

    _axisAim = axisAim
    _axisUp = axisUp
    _axisWorldUp = worldUpAxis
    _l_pos = positionList
    _radius = 1    
    mc.select(cl=True)

    #>>Get positions ================================================================================
    _len = len(_l_pos)
    if _len > 1:    
        _baseDist = DIST.get_distance_between_points(_l_pos[0],_l_pos[1])   
        _radius = _baseDist/4

    #>>Create joints =================================================================================
    _ml_joints = []

    log.debug("|{0}| >> pos list...".format(_str_func)) 
    for i,p in enumerate(_l_pos):
        log.debug("|{0}| >> {1}:{2}".format(_str_func,i,p)) 

        _mJnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
        _mJnt.displayLocalAxis = 1
        _mJnt.radius = _radius

        _ml_joints.append ( _mJnt )
        _mJnt.parent = False

    #>>Orient chain...
    for i,mJnt in enumerate(_ml_joints[:-1]):
        if i > 0:
            mJnt.parent = _ml_joints[i-1]
            #...after our first object, we use our last object's up axis to be our new up vector.
            #...this keeps joint chains that twist around from flipping. Ideally...
            _axisWorldUp = MATH.get_obj_vector(_ml_joints[i-1].mNode,'y+')
        mDup = mJnt.doDuplicate(parentOnly = True)
        mc.makeIdentity(mDup.mNode, apply = 1, jo = 1)#Freeze

        SNAP.aim(mDup.mNode,_ml_joints[i+1].mNode,_axisAim,_axisUp,'vector',_axisWorldUp)


        #_rot = mJnt.rotate
        mJnt.rotate = 0,0,0
        mJnt.jointOrient = mDup.rotate
        #mJnt.rotate = 0,0,0
        mDup.delete()

    #>>Last joint....        
    if _len > 1:
        _ml_joints[-1].parent = _ml_joints[-2]
        _ml_joints[-1].jointOrient = 0,0,0
    #_ml_joints[-1].rotate = _ml_joints[-2].rotate
    #_ml_joints[-1].rotateAxis = _ml_joints[-2].rotateAxis

    #JOINTS.metaFreezeJointOrientation(_ml_joints)
    if asMeta:
        return _ml_joints
    return [mJnt.mNode for mJnt in _ml_joints]
    #>>Wiring and naming =================================================================================
    """
    ml_handles = []
    ml_handleJoints = []
    for i_obj in mi_go._ml_controlObjects:
        if i_obj.hasAttr('handleJoint'):
            #d_buffer = i_obj.handleJoint.d_jointFlags
            #d_buffer['isHandle'] = True
            #i_obj.handleJoint.d_jointFlags = d_buffer
            ml_handleJoints.append(i_obj.handleJoint)

    mi_go._mi_rigNull.msgList_connect(ml_handleJoints,'handleJoints','rigNull')
    mi_go._mi_rigNull.msgList_connect(ml_moduleJoints,'skinJoints')     
    """





    _ml_joints[0].addAttr('cgmName','box')

    for i,mJnt in enumerate(_ml_joints):
        mJnt.addAttr('cgmIterator',i)
        mJnt.doName()


    #>>HelperJoint setup???
    
    
def build_loftMesh(root, jointCount = 3, degree = 3, cap = True, merge = True):
    """
    Core rig block factory. Runs processes for rig blocks.

    :parameters:
        root(str) | root object to check for wiring

    :returns
        factory instance
    """
    _str_func = 'build_loftMesh'
    
    _l_targets = ATTR.msgList_get(root,'loftTargets')
    
    
    mc.select(cl=True)
    log.debug("|{0}| >> loftTargets: {1}".format(_str_func,_l_targets))
    
    #tess method - general, uType 1, vType 2+ joint count
    
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

def build_jointProxyMesh(root,degree = 3):
    _str_func = 'build_jointProxyMesh'
    
    _l_targets = ATTR.msgList_get(root,'loftTargets')
    #_l_joints = [u'box_0_jnt', u'box_1_jnt', u'box_2_jnt', u'box_3_jnt', u'box_4_jnt']
    
    _mi_root = cgmMeta.cgmObject(root)
    _mi_module = _mi_root.moduleTarget
    _mi_rigNull = _mi_module.rigNull
    
    _l_joints = _mi_rigNull.msgList_get('skinJoints',asMeta = False)
    _castMesh = 'box_root_crv_grp_box_root_crv_proxy_geo'
    _name = ATTR.get(root,'blockType')
    
    #>>Make a nurbs body -----------------------------------------------------------------
    _res_body = mc.loft(_l_targets, o = True, d = degree, po = 0 )
    
    #>>Cast intersections to get v values -----------------------------------------------------------------
    #...get our initial range for casting
    #_l_dist = DIST.get_distance_between_points([POS.get(j) for j in _l_joints])
    #log.debug("|{0}| >> average dist: {1}".format(_str_func,_average))   
    
    _l_newCurves = []
    for j in _l_joints:
        _d = RAYS.cast(_res_body[0],j,'y+')
        log.debug("|{0}| >> Casting {1} ...".format(_str_func,j))
        #cgmGEN.log_info_dict(_d,j)
        _v = _d['uvs'][_res_body[0]][0][0]
        log.debug("|{0}| >> v: {1} ...".format(_str_func,_v))
        
        #>>For each v value, make a new curve -----------------------------------------------------------------        
        #duplicateCurve -ch 1 -rn 0 -local 0  "loftedSurface2.u[0.724977270271534]"
        _crv = mc.duplicateCurve("{0}.u[{1}]".format(_res_body[0],_v), ch = 0, rn = 0, local = 0)
        log.debug("|{0}| >> created: {1} ...".format(_str_func,_crv))        
        _l_newCurves.append(_crv[0])
    
    
    #>>Reloft those sets of curves and cap them -----------------------------------------------------------------
    log.debug("|{0}| >> Create new mesh objs. Curves: {1} ...".format(_str_func,_l_newCurves))        
    _l_new = []
    for i,c in enumerate(_l_newCurves[:-1]):
        _pair = [c,_l_newCurves[i+1]]
        _mesh = create_loftMesh(_pair, name="{0}_{1}".format(_name,i))
        RIGGING.match_transform(_mesh,_l_joints[i])
        _l_new.append(_mesh)
    
    #...clean up 
    mc.delete(_l_newCurves + _res_body)
    #>>Parent to the joints ----------------------------------------------------------------- 
    
    return _l_new

def create_loftMesh(targets = None, name = 'test', degree = 3, divisions = 1, cap = True, merge = True ):
    """
    Create lofted mesh from target curves.

    :parameters:
        targets(list) | List of curves to loft
        name(str) | Base name for created objects
        degree(int) | degree of surface
        divisions(int) | how many splits in the created mesh
        cap(bool) | whether to cap the top and bottom
        merge(bool) | whether to merge the caps to the base mesh

    :returns
        created(list)
    """    
    _str_func = 'create_loftMesh'
    
    if targets == None:
        targets = mc.ls(sl=True)
    if not targets:
        raise ValueError, "|{0}| >> Failed to get attr dict".format(_str_func,blockType)
    
    
    mc.select(cl=True)
    log.debug("|{0}| >> targets: {1}".format(_str_func,targets))
    
    #tess method - general, uType 1, vType 2+ joint count
    
    #>>Body -----------------------------------------------------------------
    _res_body = mc.loft(targets, o = True, d = degree, po = 1 )

    _inputs = mc.listHistory(_res_body[0],pruneDagObjects=True)
    _tessellate = _inputs[0]
    
    _d = {'format':2,#General
          'polygonType':1,#'quads',
          'uNumber': 1 + divisions}
    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)
        
    if cap:
        _l_combine = [_res_body[0]]
        
        #>>Top bottom -----------------------------------------------------------------
        for crv in targets[0],targets[-1]:
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
            
        _res = mc.polyUnite(_l_combine,ch=False,mergeUVSets=1,n = "{0}_proxy_geo".format(name))
        
        if merge:
            mc.polyMergeVertex(_res[0], d= .01, ch = 0, am = 1 )
            #polyMergeVertex  -d 0.01 -am 1 -ch 1 box_3_proxy_geo;
    else:
        _res = _res_body
    mc.polySetToFaceNormal(_res[0],setUserNormal = True)
    return _res[0]    

def create_remesh(mesh = None, joints = None, curve=None, positions = None,
                  name = 'test', vector = None, 
                  degree = 3, divisions = 1, cap = True, merge = True ):
    """
    Given a series of positions, or objects, or a curve and a mesh - loft retopology it

    :parameters:
        targets(list) | List of curves to loft
        name(str) | Base name for created objects
        degree(int) | degree of surface
        divisions(int) | how many splits in the created mesh
        cap(bool) | whether to cap the top and bottom
        merge(bool) | whether to merge the caps to the base mesh

    :returns
        created(list)
    """    
    _str_func = 'create_remesh'
    _l_pos = False
    
    #Validate
    if positions:
        _len_passed = len(positions)
        log.debug("|{0}| >> Positions passed... len:{1} | {2}".format(_str_func,_len_passed,positions))        
        _mode = 'positions'
        
        if _len_passed > divisions:
            log.warning("|{0}| >> More positions passed than divisions... positions:{1} | divisions:{2}".format(_str_func,_len_passed,divisions))                    
            return False
        else:
            log.debug("|{0}| >> Splitting Positions")
            _p_start = POS.get(_l_targets[0])
            _p_top = POS.get(_l_targets[1])    
            _l_pos = get_posList_fromStartEnd(_p_start,_p_top,_joints)          
        
        
    else:
        if joints:
            log.debug("|{0}| >> joints passed... len:{1} | {2}".format(_str_func,len(joints),joints))                    
            _mode = 'joint'
            _objs = joints
        elif curve:
            log.debug("|{0}| >> curve passed... len:{1} | {2}".format(_str_func,len(curve),curve))                                
            _mode = 'curve'
        
    #>>Get our positions
    if not _l_pos:
        log.warning("|{0}| >> Must have _l_pos by now.".format(_str_func))                    
        return False       
    
    #>If we have a curve, split it
    #>If we have a series of joints, get pos
    
    #>>Get our vectors
    _vec = [0,1,0]
    
    
    #>>Cast our Loft curves

def get_from_scene():
    """
    Gather all rig blocks data in scene

    :parameters:

    :returns
        _d_modules, _d_categories, _l_unbuildable
        _d_modules(dict) - keys to modules
        _d_categories(dict) - categories to list of entries
        _l_unbuildable(list) - list of unbuildable modules
    """
    _str_func = 'get_from_scene'
    
    _l_rigBlocks = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock')
    
    return _l_rigBlocks

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
        _mRoot = PATH.Path(root)
        _split = _mRoot.split()
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
                            if not is_buildable(module):
                                _l_unbuildable.append(name)
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

def is_buildable(blockModule):
    """
    Function to check if a givin block module is buildable or not
    
    """
    _str_func = 'is_buildable'  
    """_d_blockTypes = get_modules_dict()[0]
    
    if blockType not in _d_blockTypes.keys():
        log.error("|{0}| >> [{1}] Module not in dict".format(_str_func,blockType))            
        return False"""
    
    _res = True
    #_buildModule = _d_blockTypes[blockType]
    _buildModule = blockModule
    try:
        _blockType = _buildModule.__name__.split('.')[-1]
    except:
        log.error("|{0}| >> [{1}] | Failed to query name. Probably not a module".format(_str_func,_buildModule))        
        return False
    _keys = _buildModule.__dict__.keys()
    
    for a in _l_requiredModuleDat:
        if a not in _keys:
            log.debug("|{0}| >> [{1}] Missing data: {2}".format(_str_func,_blockType,a))
            _res = False
            
    if _res:return _buildModule
    return _res
    
    
    
    
    
    
    
    






