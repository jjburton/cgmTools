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
from cgm.core import cgm_PuppetMeta as PUPPETMETA

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTRS
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.rigger.lib import joint_Utils as JOINTS
reload(SNAP)
#from cgm.core.lib import nameTools
#from cgm.core.rigger import ModuleFactory as mFactory
#from cgm.core.rigger import PuppetFactory as pFactory
#from cgm.core.classes import NodeFactory as nodeF

from cgm.core.mrs.blocks import box
reload(box)

_d_blockTypes = {'box':box}

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
    
    def __init__(self, root = None, *a,**kws):
        """
        Core rig block factory. Runs processes for rig blocks.
        
        
        """
        _str_func = 'factory._init_'
        
        if a:log.debug("|{0}| >> a: {1}".format(_str_func,a))
        if kws:
            self._call_kws = kws
            cgmGEN.log_info_dict(kws,_str_func)
            #log.debug("|{0}| >> kws: {1}".format(_str_func,kws))
        
        self._mi_root = None
        
        _verify = kws.get('verify',False)
        log.debug("|{0}| >> verify: {1}".format(_str_func,_verify))
        
        if root is not None:
            self.rigBlock_set(root)
    
    def __repr__(self):
        try:return "{0}(root: {1})".format(self.__class__, self._mi_root)
        except:return self
        
    def rigBlock_create(self):
        raise NotImplementedError,"Not yet..."
    
    
    def get_attrCreateDict(self,blockType = None):
        """
        """
        _str_func = 'get_attrCreateDict'
        
        _mod = _d_blockTypes.get(blockType,False)
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
        cgmGEN.log_info_dict(d_defaultSettings,_str_func + " '{0}' defaults".format(blockType))
        
        self._d_attrsToVerify = _d
        self._d_attrToVerifyDefaults = d_defaultSettings
        
        #for k in _d.keys():
            #print k
        
        return True
        
       
    
    def rigBlock_verify(self, blockType = None):
        _str_func = 'rigBlock_verify'
        
        if self._mi_root is None:
            raise ValueError,"No root loaded."
        
        _mRoot = self._mi_root
        
        if _mRoot.isReferenced():
            raise ValueError,"Referenced node. Cannot verify"
        
        if not self.get_attrCreateDict(blockType):
            raise ValueError, "|{0}| >> Failed to get attr dict".format(_str_func,blockType)
        
        #Need to get the type, the get the attribute lists and data from the module
        #...attributes
        
        _mRoot.verifyAttrDict(self._d_attrsToVerify,keyable = False, hidden = False)
        _mRoot.addAttr('blockType', value = blockType,lock=True)	
        
        
        for k,v in self._d_attrToVerifyDefaults.iteritems():
            try:ATTRS.set(_mRoot.mNode,k,v)
            except Exception,err:
                log.error("|{0}| >> Failed to set default value. || key: {1} | value: {2} ||| err: {3}".format(_str_func,k,v,err))                
            
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
                #if log.getEffectiveLevel() == 10:log.debug(k + " : " + str(self.kw_callNameTags.get(k)))                
                self.addAttr(k,value = self.kw_callNameTags.get(k),lock = True)
                #if log.getEffectiveLevel() == 10:log.debug(str(self.getNameDict()))
                #if log.getEffectiveLevel() == 10:log.debug(self.__dict__[k])
    
    
        #Attrbute checking
        #=================
        self.verifyAttrDict(d_rigBlockAttrs_toMake,keyable = False, hidden = False)
        #if log.getEffectiveLevel() == 10:log.debug("%s.__verify__ >>> kw_callNameTags: %s"%(self.p_nameShort,self.kw_callNameTags))	    	
        d_enumToCGMTag = {'cgmDirection':'direction','cgmPosition':'position'}
        for k in d_enumToCGMTag.keys():
            if k in self.kw_callNameTags.keys():
                try:self.__setattr__(d_enumToCGMTag.get(k),self.kw_callNameTags.get(k))
                except Exception,error: log.error("%s.__verify__ >>> Failed to set key: %s | data: %s | error: %s"%(self.p_nameShort,k,self.kw_callNameTags.get(k),error))
    
        self.doName()   
    
        return True        
        
    
    def rigBlock_set(self,root=None):
        _str_func = 'rigBlock_set'
        log.debug("|{0}| >> root kw: {1}".format(_str_func,root))
        if root is None:
            return False
        
        self._mi_root = cgmMeta.validateObjArg(root,'cgmObject')
        log.debug("|{0}| >> mInstance: {1}".format(_str_func,self._mi_root))
        pass
    
    def skeletonize(self):
        #Build skeleton
        #Wire and name
        pass
    
    def module_verify(self):
        _str_func = 'module_verify'
        
        if self._mi_root is None:
            raise ValueError,"|{0}| >> No root loaded.".format(_str_func)
        _mRoot = self._mi_root        
        
        _bfr = _mRoot.getMessage('moduleTarget')
        if _bfr:
            log.debug("|{0}| >> moduleTarget found: {1}".format(_str_func,_bfr))            
            mModule = cgmMeta.validateObjArg(_bfr,'cgmObject')
        else:
            log.debug("|{0}| >> Creating moduleTarget...".format(_str_func))   
            _kws = self.module_getBuildKWS()
            mModule = PUPPETMETA.cgmModule(**_kws)
            
        ATTRS.set_message(_mRoot.mNode, 'moduleTarget', mModule.mNode,simple = True)
        ATTRS.set_message(mModule.mNode, 'rigHelper', _mRoot.mNode,simple = True)
        
        return mModule
    
    def module_getBuildKWS(self):
        _str_func = 'module_getBuildKWS'
        
        if self._mi_root is None:
            raise ValueError,"|{0}| >> No root loaded.".format(_str_func)
        _mRoot = self._mi_root

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
        _str_func = 'puppet_verify'
        if self._mi_root is None:
            raise ValueError,"|{0}| >> No root loaded.".format(_str_func)
        _mRoot = self._mi_root     
        
        mi_module = _mRoot.moduleTarget
        if not mi_module:
            mi_module = self.module_verify()
            
        if mi_module.getMessage('modulePuppet'):
            return False
    
        mi_puppet = PUPPETMETA.cgmPuppet(name = mi_module.getNameAlias())
        
        mi_puppet.connectModule(mi_module)	
        
        if mi_module.getMessage('moduleMirror'):
            mi_puppet.connectModule(mi_module.moduleMirror)
        
        mi_puppet.gatherModules()#Gather any modules in the chain
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
    
def build_skeleton(joints = 1, curve=None):
    _str_func = 'build_skeleton'
    

    _axisAim = 'z+'
    _axisUp = 'y+'
    _worldUp = 'orient_crv'
    _radius = 1
    
    _axisWorldUp = MATH.get_obj_vector(_worldUp,'y+')
    mc.select(cl=True)
    
    #>>Get positions ================================================================================
    if curve is not None:
        _l_pos = CURVES.returnSplitCurveList(curve,joints,rebuildSpans=10)
        
    else:
        _base = 'joint_base_placer'
        _top = 'joint_top_placer'     
        _p_start = POS.get(_base)
        _p_top = POS.get(_top)    
        _l_pos = get_posList_fromStartEnd(_p_start,_p_top,joints)        
    
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

            
            
            
    
    
        

