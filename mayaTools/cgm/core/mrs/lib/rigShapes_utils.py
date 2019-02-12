"""
------------------------------------------
cgm.core.mrs.blocks.organic.limb
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
# From Python =============================================================
import copy
import re
import pprint
import time
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel    

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import cgm.core.cgm_General as cgmGEN
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.rig.general_utils as CORERIGGEN
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core import cgm_RigMeta as cgmRigMeta
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.lib.locator_utils as LOC
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.position_utils as POS
import cgm.core.rig.joint_utils as JOINT
import cgm.core.rig.ik_utils as IK
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.mrs.lib.builder_utils as BUILDUTILS
import cgm.core.lib.shapeCaster as SHAPECASTER
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.cgm_RigMeta as cgmRIGMETA


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.09122018'
def log_start(str_func):
    log.debug("|{0}| >> ...".format(str_func)+'/'*60)
    
def ik_rp(self,mHandle = None,ml_targets = None):
    _str_func = 'rp'
    #Mid IK...---------------------------------------------------------------------------------
    log.debug("|{0}| >> ...".format(_str_func)+'/'*30)
    if mHandle == None:
        mHandle = self.mMidTemplateHandle
    if not ml_targets:
        self.ml_handleTargetsCulled
        
    size_knee =  MATH.average(POS.get_bb_size(mHandle.mNode,True)) * .75
    crv = CURVES.create_fromName('sphere',
                                  direction = 'z+',#_jointOrientation[0]+'+',
                                  size = size_knee)#max(size_knee) * 1.25)            
    
    mRP = cgmMeta.validateObjArg(crv,setClass=True)
    mRP.p_position = self.mBlock.atUtils('prerig_get_rpBasePos',ml_targets,False)
    self.mBlock.asHandleFactory().color(mRP.mNode, controlType = 'main')

    #mRP.doCopyNameTagsFromObject(ml_fkJoints[1].mNode,ignore=['cgmType','cgmTypeModifier'])
    mRP.doStore('cgmName',self.d_module['partName'])    
    mRP.doStore('cgmAlias','midIK')
    mRP.doStore('cgmTypeModifier','ikPole')
    
    mRP.doName()

    self.mRigNull.connectChildNode(mRP,'controlIKMid','rigNull')#Connect
    log.debug(cgmGEN._str_subLine)    
    return mRP

def ik_segMid(self,mHandle = None):
    try:
        _str_func = 'ik_segMid'
        log_start(_str_func)
        ml_shapes = self.atBuilderUtils('shapes_fromCast',
                                        targets = mHandle,
                                        offset = self.v_offset,
                                        mode = 'simpleCast')#'segmentHan
        CORERIG.shapeParent_in_place(mHandle.mNode, ml_shapes[0].mNode,False)
    
        mHandle.doStore('cgmTypeModifier','ik')
        mHandle.doStore('cgmType','handle')
        mHandle.doName()            
        self.mHandleFactory.color(mHandle.mNode, controlType = 'sub')
        return mHandle
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

def rootOrCog(self,mHandle = None):
    try:
        _str_func = 'rootOrCog'
        log_start(_str_func)
        
        mBlock = self.mBlock
        ml_prerigHandles = self.ml_prerigHandles
        ml_templateHandles = self.ml_templateHandles
        _offset = self.v_offset
        if mBlock.getMessage('cogHelper') and mBlock.getMayaAttr('addCog'):
            log.debug("|{0}| >> Cog...".format(_str_func))
            mCogHelper = mBlock.cogHelper
        
            mCog = mCogHelper.doCreateAt(setClass=True)
            CORERIG.shapeParent_in_place(mCog.mNode, mCogHelper.shapeHelper.mNode)
        
            #Cast a simple curve
            #Cv's 4,2 | 
        
            ml_shapes = self.atBuilderUtils('shapes_fromCast',
                                            targets = mCogHelper.shapeHelper,
                                            offset = _offset * 2.0,
                                            mode = 'singleCast')#'segmentHan            
            CORERIG.shapeParent_in_place(mCog.mNode, ml_shapes[0].mNode,False)
        
            CORERIG.override_color(mCog.mNode,'white')
        
            mCog.doStore('cgmName','cog')
            mCog.doStore('cgmAlias','cog')
            mCog.doName()
        
            self.mRigNull.connectChildNode(mCog,'rigRoot','rigNull')#Connect
            self.mRigNull.connectChildNode(mCog,'settings','rigNull')#Connect
        
        
        else:#Root =============================================================================
            log.debug("|{0}| >> Root...".format(_str_func))
    
            mRootHandle = ml_prerigHandles[0]
            #mRoot = ml_joints[0].doCreateAt()
            
            ml_joints = self.d_joints['ml_moduleJoints']
            mRoot = ml_joints[0].doCreateAt()
    
            #_size_root =  MATH.average(mHandleFactory.get_axisBox_size(ml_templateHandles[0].mNode))
            _size_root = POS.get_bb_size(ml_templateHandles[0].loftCurve.mNode,True,mode='max')
            mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('sphere', _size_root * 1.5),'cgmObject',setClass=True)
            mRootCrv.doSnapTo(mRootHandle)
    
            #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)
    
            CORERIG.shapeParent_in_place(mRoot.mNode,mRootCrv.mNode, False)
    
            ATTR.copy_to(self.mModule.mNode,'cgmName',mRoot.mNode,driven='target')
            mRoot.doStore('cgmTypeModifier','root')
            mRoot.doName()
    
            self.mHandleFactory.color(mRoot.mNode, controlType = 'sub')
    
            self.mRigNull.connectChildNode(mRoot,'rigRoot','rigNull')#Connect        
       
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


def ik_end(self,ikEnd=None,ml_handleTargets = None, ml_rigJoints = None,ml_fkShapes = None,
          ml_ikJoints = None, ml_fkJoints = None,shapeArg = None):
    try:
        _str_func = 'ik_end'
        #Mid IK...---------------------------------------------------------------------------------
        log_start(_str_func)
        mBlock = self.mBlock
        ml_templateHandles = self.ml_templateHandles
        
        if ml_handleTargets == None:
            raise ValueError,"{0} | ml_handleTargets required".format(_str_func)
        if ikEnd == None:
            ikEnd = mBlock.getEnumValueString('ikEnd')
    
        
        if ml_templateHandles[-1].getMessage('proxyHelper'):
            log.debug("|{0}| >> proxyHelper IK shape...".format(_str_func))
            mProxyHelper = ml_templateHandles[-1].getMessage('proxyHelper',asMeta=True)[0]
            #bb_ik = mHandleFactory.get_axisBox_size(mProxyHelper.mNode)
            bb_ik = POS.get_bb_size(mProxyHelper.mNode,True,mode='max')
        
            _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
            ATTR.set(_ik_shape,'scale', 1.5)
            mIKShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
        
            mIKShape.doSnapTo(mProxyHelper)
            pos_ik = POS.get_bb_center(mProxyHelper.mNode)
            mIKShape.p_position = pos_ik
            mIKCrv = ml_handleTargets[self.int_handleEndIdx].doCreateAt()
            CORERIG.shapeParent_in_place(mIKCrv.mNode, mIKShape.mNode, False)
    
        elif ikEnd in ['tipBase','tipEnd','tipMid']:
            log.debug("|{0}| >> tip shape...".format(_str_func))
            ml_curves = []
    
            if ikEnd == 'tipBase':
                mIKCrv = ml_handleTargets[self.int_handleEndIdx].doCreateAt()
            elif ikEnd == 'tipMid':
                mIKCrv = ml_handleTargets[self.int_handleEndIdx].doCreateAt()
    
                pos = DIST.get_average_position([ml_rigJoints[self.int_segBaseIdx].p_position,
                                                 ml_rigJoints[-1].p_position])
    
                mIKCrv.p_position = pos
    
            else:
                mIKCrv = ml_handleTargets[-1].doCreateAt()
                
            if shapeArg is not None:
                mIK_templateHandle = ml_templateHandles[ self.int_handleEndIdx ]
                bb_ik = POS.get_bb_size(mIK_templateHandle.mNode,True,mode='max')
                _ik_shape = CURVES.create_fromName(shapeArg, size = bb_ik)
                ATTR.set(_ik_shape,'scale', 2.0)
                mIKShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                mIKShape.doSnapTo(mIK_templateHandle)          
                
                CORERIG.shapeParent_in_place(mIKCrv.mNode, mIKShape.mNode, False)
                
            else:
                CORERIG.shapeParent_in_place(mIKCrv.mNode, ml_fkShapes[-1].mNode, True)
        elif ikEnd == 'shapeArg':
            mIK_templateHandle = ml_templateHandles[ self.int_handleEndIdx ]
            bb_ik = POS.get_bb_size(mIK_templateHandle.mNode,True,mode='max')
            _ik_shape = CURVES.create_fromName(shapeArg, size = bb_ik)
            ATTR.set(_ik_shape,'scale', 1.1)
    
            mIKShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
    
            mIKShape.doSnapTo(mIK_templateHandle)
            mIKCrv = ml_ikJoints[self.int_handleEndIdx].doCreateAt()
            CORERIG.shapeParent_in_place(mIKCrv.mNode, mIKShape.mNode, False)                            
            
        else:
            log.debug("|{0}| >> default IK shape...".format(_str_func))
            mIK_templateHandle = ml_templateHandles[ self.int_handleEndIdx ]
            bb_ik = POS.get_bb_size(mIK_templateHandle.mNode,True,mode='max')
            _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
            ATTR.set(_ik_shape,'scale', 1.1)
    
            mIKShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
    
            mIKShape.doSnapTo(mIK_templateHandle)
            mIKCrv = ml_ikJoints[self.int_handleEndIdx].doCreateAt()
            CORERIG.shapeParent_in_place(mIKCrv.mNode, mIKShape.mNode, False)                
    
        self.mHandleFactory.color(mIKCrv.mNode, controlType = 'main',transparent=True)
        mIKCrv.doCopyNameTagsFromObject(ml_fkJoints[self.int_handleEndIdx].mNode,
                                        ignore=['cgmType','cgmTypeModifier'])
        mIKCrv.doStore('cgmTypeModifier','ik')
        mIKCrv.doStore('cgmType','handle')
        mIKCrv.doName()
    
    
        self.mHandleFactory.color(mIKCrv.mNode, controlType = 'main')        
        self.mRigNull.connectChildNode(mIKCrv,'controlIK','rigNull')#Connect
        log.debug(cgmGEN._str_subLine)    
        return mIKCrv
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
def ik_base(self,ikBase = None, ml_baseJoints = None, ml_fkShapes = None):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        ml_templateHandles = self.ml_templateHandles
        
        if ikBase == None:
            ikBase = mBlock.getEnumValueString('ikBase')        
        
        if not ml_baseJoints:
            raise ValueError,"{0} | ml_baseJoints required".format(_str_func)
        
        
        log.debug("|{0}| >> {1} ...".format(_str_func,ikBase))
            
        if ikBase in ['hips','simple']:
            if ikBase ==  'hips':
                mIKBaseCrv = ml_baseJoints[1].doCreateAt(setClass=True)
                mIKBaseCrv.doCopyNameTagsFromObject(ml_baseJoints[0].mNode,ignore=['cgmType'])                
                mIKBaseCrv.doStore('cgmName','hips')
            else:
                mIKBaseCrv = ml_baseJoints[0].doCreateAt(setClass=True)
                mIKBaseCrv.doCopyNameTagsFromObject(ml_baseJoints[0].mNode,ignore=['cgmType'])
                
            CORERIG.shapeParent_in_place(mIKBaseCrv.mNode, ml_fkShapes[0].mNode, True)
            
        else:
            log.debug("|{0}| >> default IK base shape...".format(_str_func))
            mIK_templateHandle = ml_templateHandles[ 0 ]
            #bb_ik = mHandleFactory.get_axisBox_size(mIK_templateHandle.mNode)
            bb_ik = POS.get_bb_size(mIK_templateHandle.mNode,True,mode='max')
            
            _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
            ATTR.set(_ik_shape,'scale', 1.1)
        
            mIKBaseShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
        
            mIKBaseShape.doSnapTo(mIK_templateHandle)
            #pos_ik = POS.get_bb_center(mProxyHelper.mNode)
            #SNAPCALLS.get_special_pos(mEndHandle.p_nameLong,
            #                                   'axisBox','z+',False)                
        
            #mIKBaseShape.p_position = pos_ik
            mIKBaseCrv = ml_baseJoints[0].doCreateAt()
            mIKBaseCrv.doCopyNameTagsFromObject(ml_baseJoints[0].mNode,ignore=['cgmType'])
            CORERIG.shapeParent_in_place(mIKBaseCrv.mNode, mIKBaseShape.mNode, False)                            

        mIKBaseCrv.doStore('cgmTypeModifier','ikBase')
        mIKBaseCrv.doName()

        self.mHandleFactory.color(mIKBaseCrv.mNode, controlType = 'main')
        self.mRigNull.connectChildNode(mIKBaseCrv,'controlIKBase','rigNull')#Connect                
      
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
def settings(self,settingsPlace = None,ml_targets = None):
    try:
        _str_func = 'rp'
        log_start(_str_func)
        log.debug("|{0}| >> settings: {1}...".format(_str_func,settingsPlace))
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        if settingsPlace == None:
            settingsPlace = mBlock.getEnumValueString('settingsPlace')
        
        if settingsPlace == 'cog':
            mCog = mRigNull.getMessageAsMeta('rigRoot')
            if mCog:
                log.debug("|{0}| >> Settings is cog...".format(_str_func))
                mRigNull.connectChildNode(mCog,'settings','rigNull')#Connect
                return mCog
            else:
                log.warning("|{0}| >> Settings. Cog option but no cog found...".format(_str_func))
                settingsPlace = 'start'
            
        if settingsPlace in ['start','end']:
            _settingsSize = _offset * 2
            if settingsPlace == 'start':
                _mTar = ml_targets[0]
            else:
                _mTar = ml_targets[self.int_handleEndIdx]

            mSettingsShape = cgmMeta.validateObjArg(CURVES.create_fromName('gear',_settingsSize,
                                                                           '{0}+'.format(_jointOrientation[2])),'cgmObject',setClass=True)

            mSettingsShape.doSnapTo(_mTar.mNode)
            d_directions = {'up':'y+','down':'y-','in':'x+','out':'x-'}
            str_settingsDirections = d_directions.get(mBlock.getEnumValueString('settingsDirection'),'y+')

            mMesh_tmp =  mBlock.atUtils('get_castMesh')
            str_meshShape = mMesh_tmp.getShapes()[0]        
            pos = RAYS.get_cast_pos(_mTar.mNode,str_settingsDirections,shapes = str_meshShape)
            #SNAPCALLS.get_special_pos([_mTar,str_meshShape],'castNear',str_settingsDirections,False)
            vec = MATH.get_vector_of_two_points(_mTar.p_position, pos)
            newPos = DIST.get_pos_by_vec_dist(pos,vec,_offset * 2.0)

            mSettingsShape.p_position = newPos
            mMesh_tmp.delete()

            SNAP.aim_atPoint(mSettingsShape.mNode,
                             _mTar.p_position,
                             aimAxis=_jointOrientation[0]+'+',
                             mode = 'vector',
                             vectorUp= _mTar.getAxisVector(_jointOrientation[0]+'-'))

            mSettingsShape.parent = _mTar
            mSettings = mSettingsShape
            CORERIG.match_orientation(mSettings.mNode, _mTar.mNode)

            ATTR.copy_to(self.d_module['partName'],'cgmName',mSettings.mNode,driven='target')

            mSettings.doStore('cgmTypeModifier','settings')
            mSettings.doName()
            self.mHandleFactory.color(mSettings.mNode, controlType = 'sub')
            mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect
        else:
            raise ValueError,"Unknown settingsPlace: {1}".format(settingsPlace)
        
        return mSettings
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
def direct(self,ml_rigJoints = None):
    try:
        _str_func = 'direct'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']        
        
        if not ml_rigJoints:
            ml_rigJoints = mRigNull.msgList_get('rigJoints')
            
        
        if len(ml_rigJoints) < 3:
            _size_direct = DIST.get_distance_between_targets([mObj.mNode for mObj in ml_rigJoints], average=True)        
            d_direct = {'size':_size_direct/2}
        else:
            d_direct = {'size':None}
    
        ml_directShapes = self.atBuilderUtils('shapes_fromCast',
                                              ml_rigJoints,
                                              mode ='direct',**d_direct)
    
        for i,mCrv in enumerate(ml_directShapes):
            self.mHandleFactory.color(mCrv.mNode, controlType = 'sub')
            CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
    
        for mJnt in ml_rigJoints:
            try:
                mJnt.drawStyle =2
            except:
                mJnt.radius = .00001
                
        return ml_rigJoints
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
def segment_handles(self,ml_handles = None):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        if not ml_handles:
            raise ValueError,"{0} | ml_handles required".format(_str_func)
            
        ml_handleShapes = self.atBuilderUtils('shapes_fromCast',
                                              targets = ml_handles,
                                              offset = _offset,
                                              mode = 'limbSegmentHandle')#'segmentHandle') limbSegmentHandle

    
        for i,mCrv in enumerate(ml_handleShapes):
            log.debug("|{0}| >> Shape: {1} | Handle: {2}".format(_str_func,mCrv.mNode,ml_handles[i].mNode ))                
            self.mHandleFactory.color(mCrv.mNode, controlType = 'sub')            
            CORERIG.shapeParent_in_place(ml_handles[i].mNode, 
                                         mCrv.mNode, False,
                                         replaceShapes=True)
      
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
def backup(self,ml_handles = None):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        if not ml_handles:
            raise ValueError,"{0} | ml_handles required".format(_str_func)        
      
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())