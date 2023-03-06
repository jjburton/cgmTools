"""
------------------------------------------
cgm.core.mrs.blocks.organic.limb
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
__MAYALOCAL = 'RIGSHAPES'

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
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel    

# From Red9 =============================================================
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.lib.math_utils as MATH
import cgm.core.cgm_General as cgmGEN
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.mrs.lib.builder_utils as BUILDUTILS
import cgm.core.lib.shapeCaster as SHAPECASTER
import cgm.core.lib.surface_Utils as SURF
import cgm.core.lib.position_utils as POS

"""
from Red9.core import Red9_Meta as r9Meta
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.rig.general_utils as CORERIGGEN
import cgm.core.lib.transform_utils as TRANS

import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core import cgm_RigMeta as cgmRigMeta
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.locator_utils as LOC
import cgm.core.rig.create_utils as RIGCREATE

import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.rig.joint_utils as JOINT
import cgm.core.rig.ik_utils as IK
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
"""


#reload(SHAPECASTER)
#from cgm.core.cgmPy import validateArgs as VALID
#import cgm.core.cgm_RigMeta as cgmRIGMETA


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.09122018'
def log_start(str_func):
    log.debug("|{0}| >> ...".format(str_func)+'/'*60)
    
def ik_bankRollShapes(self):
    try:
        _str_func = 'bankRollShapes'
        log.debug(cgmGEN.logString_sub(_str_func))        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mHandleFactory = self.mHandleFactory
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        ml_formHandles=self.ml_formHandles
        ml_fkShapes = []
        
        mBallFK = False
        mToeFK = False
        mToeIK = False
        mBallIK = False
        _minRot = -90,
        _maxRot = 90
        mMesh_tmp =  self.mBlock.atUtils('get_castMesh',pivotEnd=1)
        str_meshShape = mMesh_tmp.getShapes()[0]        
        
        #if self.mPivotHelper:
        #    size_pivotHelper = POS.get_bb_size(self.mPivotHelper.mNode)
        #else:
        #    size_pivotHelper = POS.get_bb_size(ml_formHandles[-1].mNode)

            
        #reload(SHAPECASTER)
        _d_cast = {'vectorOffset':_offset,
                   'points':15,
                   #'minRot':-90,'maxRot':90,
                   'closedCurve':False}
        _max = None
        if self.mBall:
            try:
                _max = RAYS.get_dist_from_cast_axis(self.mBall.mNode,
                                                    self.d_orientation['str'][2],
                                                    shapes=str_meshShape)
            except:
                _max = 1
            _d_cast['maxDistance'] = _max
            
            crvBall = SHAPECASTER.createMeshSliceCurve(
                str_meshShape, self.mBall.mNode,
                **_d_cast)

            if not self.mToe:
                pos = RAYS.get_cast_pos(self.mBall.mNode,shapes=mMesh_tmp.mNode)
                pos_me = self.mBall.p_position
                dist = DIST.get_distance_between_points(pos,pos_me)/2
                pos_end = DIST.get_pos_by_vec_dist(pos_me, [0,0,1],dist)
                
                mDup = self.mBall.doDuplicate(po=True)
                mDup.p_position = pos_end
                
                crvBall2 = SHAPECASTER.createMeshSliceCurve(
                                str_meshShape, mDup.mNode,
                                **_d_cast)     
                
                CURVES.connect([crvBall,crvBall2],7)
                mDup.delete()
                
            mHandleFactory.color(crvBall, controlType = 'sub')                                
            mBallFK = self.mBall.getMessageAsMeta('fkJoint')
            CORERIG.shapeParent_in_place(mBallFK.mNode,crvBall, True, replaceShapes=True)            
    
            if self.str_ikRollSetup == 'control':
                log.debug(cgmGEN.logString_msg(_str_func,"Ball Ik control..."))
                mBallIK = self.mBall.doCreateAt(setClass=True)
                CORERIG.shapeParent_in_place(mBallIK.mNode,crvBall, True, replaceShapes=True)
                mRigNull.connectChildNode(mBallIK,'controlIKBall','rigNull')#Connect
    
                mBallIK.doCopyNameTagsFromObject(self.mBall.mNode, ignore = ['cgmType'])
                mBallIK.doStore('cgmTypeModifier','ik')
                mBallIK.doName()
    
                mBallIK.connectChildNode(self.mBall.fkJoint.blendJoint.mNode,'blendJoint')#Connect
                
                #Hinge ===================================================================
                log.debug(cgmGEN.logString_msg(_str_func,"Ball Hinge Ik control..."))
                #Need to make our cast locs
                
                mStart = mBallIK.doCreateAt(setClass=1)
                mEnd = mBallIK.doCreateAt(setClass=1)
                
                pos1_start = self.mBall.getParent(asMeta=1).p_position
                pos2_start = mEnd.p_position
                vec_to_end = MATH.get_vector_of_two_points(pos1_start,pos2_start)
                vec_to_start = MATH.get_vector_of_two_points(pos2_start,pos1_start)
                
                mStart.p_position = DIST.get_average_position([pos1_start,pos2_start])
                #DIST.get_pos_by_vec_dist(pos1_start,vec_to_end,_offset)#
                mEnd.p_position = DIST.get_pos_by_vec_dist(pos2_start,vec_to_start,_offset)
                
                crv1 = SHAPECASTER.createMeshSliceCurve(
                    str_meshShape,mStart.mNode,
                    **_d_cast)
                crv2 = SHAPECASTER.createMeshSliceCurve(
                    str_meshShape,mEnd.mNode,
                    **_d_cast)
                
                CURVES.connect([crv1,crv2],7)
                
                mBallHingeIK = self.mBall.doCreateAt(setClass=True)
                mRigNull.connectChildNode(mBallHingeIK,'controlIKBallHinge','rigNull')#Connect
                mBallHingeIK.connectChildNode(self.mBall.fkJoint.blendJoint.mNode,'blendJoint')#Connect
                
                mHandleFactory.color(crv1, controlType = 'sub')
                
                CORERIG.shapeParent_in_place(mBallHingeIK.mNode,crv1, True,
                                             replaceShapes=True)
                
                mBallHingeIK.doCopyNameTagsFromObject(self.mBall.mNode,
                                                 ignore = ['cgmType'])
                mBallHingeIK.doStore('cgmNameModifier','hinge')
                mBallHingeIK.doStore('cgmTypeModifier','ik')
                mBallHingeIK.doName()
                
                for mObj in mStart,mEnd:
                    mObj.delete()
                    
                ml_fkShapes.append(cgmMeta.asMeta(crv1))
            ml_fkShapes.append(cgmMeta.validateObjArg(crvBall,'cgmObject'))
                    
        if self.mToe:
            if not _max:
                _max = RAYS.get_dist_from_cast_axis(self.mToe.mNode,self.d_orientation['str'][2],shapes=str_meshShape)
            _d_cast['maxDistance'] = _max
            
            crv = SHAPECASTER.createMeshSliceCurve(
                str_meshShape, self.mToe.mNode,
                **_d_cast)
            
            
            """
            crv = CURVES.create_controlCurve(self.mToe.mNode, shape='circle',
                                             direction = _jointOrientation[0]+'+',
                                             sizeMode = 'fixed',
                                             size = size_pivotHelper[0])"""
    
            mHandleFactory.color(crv, controlType = 'sub')                    
            mToeFK = self.mToe.getMessageAsMeta('fkJoint')
            CORERIG.shapeParent_in_place(mToeFK.mNode,crv, True, replaceShapes=True)
    
            ml_fkShapes.append(cgmMeta.validateObjArg(crv,'cgmObject'))
            
    
            if self.str_ikRollSetup == 'control':
                log.debug(cgmGEN.logString_msg(_str_func,"Toe Ik control..."))
                mToeIK = self.mToe.doCreateAt(setClass=True)
                CORERIG.shapeParent_in_place(mToeIK.mNode,crv, True, replaceShapes=True)
                mRigNull.connectChildNode(mToeIK,'controlIKToe','rigNull')#Connect
    
                mToeIK.doCopyNameTagsFromObject(self.mToe.mNode, ignore = ['cgmType'])
                mToeIK.doStore('cgmTypeModifier','ik')
                mToeIK.doName()
    
                mToeIK.connectChildNode(self.mToe.fkJoint.blendJoint.mNode,'blendJoint')#Connect    
        
        mMesh_tmp.delete()
        return ml_fkShapes
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
def ik_rp(self,mHandle = None,ml_targets = None):
    _str_func = 'rp'
    #Mid IK...---------------------------------------------------------------------------------
    log.debug("|{0}| >> ...".format(_str_func)+'/'*30)
    if mHandle == None:
        mHandle = self.mMidFormHandle
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
                                        offset = self.v_offset * 2.0,
                                        mode = 'simpleCast')#'segmentHan
        
        #size = TRANS.bbSize_get(ml_shapes[0])
        
        
        
        CORERIG.shapeParent_in_place(mHandle.mNode, ml_shapes[0].mNode,False)
        
        #ml_shapes[0].delete()
        
        mHandle.doStore('cgmTypeModifier','ik')
        mHandle.doStore('cgmType','handle')
        mHandle.doName()            
        self.mHandleFactory.color(mHandle.mNode, controlType = 'sub')
        return mHandle
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
def limbRoot(self):
    try:
        _str_func = 'limbRoot'
        log_start(_str_func)
        ml_fkJoints = self.ml_fkJoints
        _short_module = self.mModule.mNode
        mHandleFactory = self.mHandleFactory
        
        #limbRoot ------------------------------------------------------------------------------
        log.debug("|{0}| >> LimbRoot".format(_str_func))
        idx = 0
        #if self.b_lever:
        #    idx = 1

        
        mLimbRootHandle = self.ml_prerigHandles[idx]
        mLimbRoot = ml_fkJoints[0].rigJoint.doCreateAt()

        _size_root = MATH.average(POS.get_bb_size(self.mRootFormHandle.mNode))
                    
        #MATH.average(POS.get_bb_size(self.mRootFormHandle.mNode))
        mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('locatorForm', _size_root),'cgmObject',setClass=True)
        mRootCrv.doSnapTo(ml_fkJoints[0])#mLimbRootHandle

        #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)

        CORERIG.shapeParent_in_place(mLimbRoot.mNode,mRootCrv.mNode, False)

        #for a in 'cgmName','cgmDirection','cgmModifier':
        #    if ATTR.get(_short_module,a):
        #        ATTR.copy_to(_short_module,a,mLimbRoot.mNode,driven='target')
        mLimbRoot.doStore('cgmName',self.d_module['partName'])

        mLimbRoot.doStore('cgmTypeModifier','limbRoot')
        mLimbRoot.doName()

        mHandleFactory.color(mLimbRoot.mNode, controlType = 'sub')
        self.mRigNull.connectChildNode(mLimbRoot,'limbRoot','rigNull')        

    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

def rootOrCog(self,mHandle = None):
    _str_func = 'rootOrCog'
    log_start(_str_func)
    
    mBlock = self.mBlock
    ml_formHandles = self.ml_formHandles
    
    try:ml_prerigHandles = self.ml_prerigHandles
    except:
        ml_prerigHandles = ml_formHandles #use these as a backup
        
    _offset = self.v_offset
    if mBlock.getMessage('cogHelper') and mBlock.getMayaAttr('addCog'):
        log.debug("|{0}| >> Cog...".format(_str_func))
        mCogHelper = mBlock.cogHelper
    
        mCog = mCogHelper.doCreateAt(setClass=True)
        CORERIG.shapeParent_in_place(mCog.mNode, mCogHelper.shapeHelper.mNode)
    
        #Cast a simple curve
        #Cv's 4,2 | 
        
        try:
            ml_shapes = self.atBuilderUtils('shapes_fromCast',
                                            targets = mCogHelper.shapeHelper,
                                            offset = _offset * 2.0,
                                            mode = 'singleCast')#'segmentHan            
            CORERIG.shapeParent_in_place(mCog.mNode, ml_shapes[0].mNode,False)
        except:
            ml_shapes = []
            pass
    
        CORERIG.override_color(mCog.mNode,'white')
        _name = '{0}_cog'.format(self.d_module['partName'])
        mCog.doStore('cgmName',_name)
        mCog.doStore('cgmAlias',_name)
        mCog.doName()
    
        self.mRigNull.connectChildNode(mCog,'rigRoot','rigNull')#Connect
        self.mRigNull.connectChildNode(mCog,'settings','rigNull')#Connect
        
        if mBlock.getMayaAttr('scaleSetup') and mBlock.blockType not in ['handle']:
            _bb_cog = POS.get_bb_size(mCog.mNode,True,'max')
            mScaleRootShape = cgmMeta.validateObjArg(CURVES.create_fromName('fatCross', _bb_cog * .7),'cgmObject',setClass=True)
            mScaleRootShape.doSnapTo(mCog)
            
            mScaleRootShape.doAimAtPoint(ml_prerigHandles[-1].p_position, 'z+')
            
            mScaleRoot = mCog.doCreateAt(setClass=True)
            CORERIG.shapeParent_in_place(mScaleRoot.mNode, mScaleRootShape.mNode,False)
            
            
            mScaleRoot.doStore('cgmName',self.d_module['partName'])
            #ATTR.copy_to(self.mModule.mNode,'cgmName',mRoot.mNode,driven='target')
            mScaleRoot.doStore('cgmTypeModifier','scaleRoot')
            mScaleRoot.doName()
    
            self.mHandleFactory.color(mScaleRoot.mNode, controlType = 'sub')
            self.mRigNull.connectChildNode(mScaleRoot,'scaleRoot','rigNull')#Connect                    
            mScaleRoot.p_parent = mCog
        return mCog
    
    else:#Root =============================================================================
        log.debug("|{0}| >> Root...".format(_str_func))

        mRootHandle = ml_prerigHandles[0]
        #mRoot = ml_joints[0].doCreateAt()
        
        ml_joints = self.d_joints['ml_moduleJoints']
        mRoot = ml_joints[0].doCreateAt()

        #_size_root =  MATH.average(mHandleFactory.get_axisBox_size(ml_formHandles[0].mNode))
        _bb_root = POS.get_bb_size(ml_formHandles[0].loftCurve.mNode,True)
        _size_root = MATH.average(_bb_root)
        mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('cubeOpen', _size_root * 1.5),'cgmObject',setClass=True)
        mRootCrv.doSnapTo(mRootHandle)

        #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)

        CORERIG.shapeParent_in_place(mRoot.mNode,mRootCrv.mNode, False)
        
        mRoot.doStore('cgmName',self.d_module['partName'])
        #ATTR.copy_to(self.mModule.mNode,'cgmName',mRoot.mNode,driven='target')
        mRoot.doStore('cgmTypeModifier','root')
        mRoot.doName()

        self.mHandleFactory.color(mRoot.mNode, controlType = 'sub')

        self.mRigNull.connectChildNode(mRoot,'rigRoot','rigNull')#Connect        
        return mRoot
       

def ik_end(self,ikEnd=None,ml_handleTargets = None, ml_rigJoints = None,ml_fkShapes = None,
          ml_ikJoints = None, ml_fkJoints = None,shapeArg = None):
    try:
        _str_func = 'ik_end'
        #Mid IK...---------------------------------------------------------------------------------
        log_start(_str_func)
        mBlock = self.mBlock
        ml_formHandles = self.ml_formHandles
        
        if ml_handleTargets == None:
            raise ValueError("{0} | ml_handleTargets required".format(_str_func))
        if ikEnd == None:
            ikEnd = mBlock.getEnumValueString('ikEnd')
    
        
        if ml_formHandles[-1].getMessage('proxyHelper'):
            log.debug("|{0}| >> proxyHelper IK shape...".format(_str_func))
            mProxyHelper = ml_formHandles[-1].getMessage('proxyHelper',asMeta=True)[0]
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
    
        elif ikEnd in ['helper','tipBase','tipEnd','tipMid']:
            log.debug("|{}| >> tip shape...{}".format(_str_func,ikEnd))
            ml_curves = []
    
            if ikEnd == 'tipBase':
                mIKCrv = mBlock.ikEndHandle.doCreateAt()#ml_handleTargets[self.int_handleEndIdx]
            elif ikEnd == 'tipMid':
                mIKCrv =  mBlock.ikEndHandle.doCreateAt()
                
                _crv = CORERIG.create_at(create='curve',l_pos=[mJnt.p_position for mJnt in ml_rigJoints])
                
                mIKCrv.p_position = CURVES.getPercentPointOnCurve(_crv,.5)
                
                mc.delete(_crv)
                """
                mIKCrv.p_position = DIST.get_average_position([ml_rigJoints[self.int_segBaseIdx].p_position,
                                                               ml_rigJoints[-1].p_position])"""
    
                
            elif ikEnd == 'tipEnd':
                mIKCrv = mBlock.ikEndHandle.doCreateAt()#ml_handleTargets[self.int_handleEndIdx]
                mIKCrv.p_position = ml_rigJoints[-1].p_position
                
            else:
                mIKCrv =  mBlock.ikEndHandle.doCreateAt()
                
            if shapeArg is not None:
                mIK_formHandle = ml_formHandles[ self.int_handleEndIdx] #self.int_handleEndIdx ]
                bb_ik = POS.get_bb_size(mIK_formHandle.mNode,True,mode='max')
                _ik_shape = CURVES.create_fromName(shapeArg, size = bb_ik * 1.5)
                #ATTR.set(_ik_shape,'scale', 4.0)
                mIKShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
                mIKShape.doSnapTo(mIK_formHandle)          
                
                CORERIG.shapeParent_in_place(mIKCrv.mNode, mIKShape.mNode, False)
                
            else:
                CORERIG.shapeParent_in_place(mIKCrv.mNode, ml_fkShapes[-1].mNode, True)
                
        elif ikEnd == 'shapeArg':
            mIK_formHandle = ml_formHandles[ self.int_handleEndIdx ]
            bb_ik = POS.get_bb_size(mIK_formHandle.mNode,True,mode='max')
            _ik_shape = CURVES.create_fromName(shapeArg, size = bb_ik + 1.3)
            #ATTR.set(_ik_shape,'scale', 1.1)
    
            mIKShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
    
            mIKShape.doSnapTo(mIK_formHandle)
            mIKCrv = ml_ikJoints[self.int_handleEndIdx].doCreateAt()
            CORERIG.shapeParent_in_place(mIKCrv.mNode, mIKShape.mNode, False)                            
            
        else:
            log.debug("|{0}| >> default IK shape...".format(_str_func))
            mIK_formHandle = ml_formHandles[ self.int_handleEndIdx ]
            bb_ik = POS.get_bb_size(mIK_formHandle.mNode,True,mode='max')
            _ik_shape = CURVES.create_fromName('cube', size = bb_ik)
            ATTR.set(_ik_shape,'scale', 1.1)
    
            mIKShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
    
            mIKShape.doSnapTo(mIK_formHandle)
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
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
def ik_base(self,ikBase = None, ml_baseJoints = None, ml_fkShapes = None):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        ml_formHandles = self.ml_formHandles
        
        if ikBase == None:
            ikBase = mBlock.getEnumValueString('ikBase')        
        
        if not ml_baseJoints:
            raise ValueError("{0} | ml_baseJoints required".format(_str_func))
        
        
        log.debug("|{0}| >> {1} ...".format(_str_func,ikBase))
            
        if ikBase in ['hips','simple','head']:
            if ikBase in  ['hips','head']:
                mIKBaseCrv = mBlock.ikStartHandle.doCreateAt(setClass=True)#ml_baseJoints[1]
                mIKBaseCrv.doCopyNameTagsFromObject(ml_baseJoints[0].mNode,ignore=['cgmType'])                
                mIKBaseCrv.doStore('cgmName',ikBase)
            else:
                mIKBaseCrv = mBlock.ikStartHandle.doCreateAt(setClass=True)
                mIKBaseCrv.doCopyNameTagsFromObject(ml_baseJoints[0].mNode,ignore=['cgmType'])
                
            CORERIG.shapeParent_in_place(mIKBaseCrv.mNode, ml_fkShapes[0].mNode, True)
            
        else:
            log.debug("|{0}| >> default IK base shape...".format(_str_func))
            mIK_formHandle = mBlock.ikStartHandle #ml_formHandles[ 0 ]
            #bb_ik = mHandleFactory.get_axisBox_size(mIK_formHandle.mNode)
            bb_ik = POS.get_bb_size(mIK_formHandle.mNode,True,mode='max')
            
            _ik_shape = CURVES.create_fromName('cube', size = bb_ik, bakeScale=True)
            ATTR.set(_ik_shape,'scale', 2.0)
        
            mIKBaseShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
        
            mIKBaseShape.doSnapTo(mIK_formHandle)
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
      
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
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
                
                
        mSettingsHelper = mBlock.getMessageAsMeta('settingsHelper')
        
        if settingsPlace in ['start','end']:
            if settingsPlace == 'start':
                _mTar = ml_targets[0]
            else:
                _mTar = ml_targets[self.int_handleEndIdx]
                
                
            #_settingsSize = _offset * 2
            if not mSettingsHelper:
                
                mMesh_tmp =  mBlock.atUtils('get_castMesh')
                str_meshShape = mMesh_tmp.getShapes()[0]
            

            
                d_directions = {'up':'y+','down':'y-','in':'x+','out':'x-'}
                
                str_settingsDirections = d_directions.get(mBlock.getEnumValueString('settingsDirection'),'y+')
                
                pos = RAYS.get_cast_pos(_mTar.mNode,str_settingsDirections,shapes = str_meshShape)
                if not pos:
                    log.debug(cgmGEN.logString_msg(_str_func, 'standard IK end'))
                    pos = _mTar.getPositionByAxisDistance(str_settingsDirections,_offset * 5)
                    
                vec = MATH.get_vector_of_two_points(_mTar.p_position, pos)
                newPos = DIST.get_pos_by_vec_dist(pos,vec,_offset * 4)

                _settingsSize = _offset * 2
                
                mSettingsShape = cgmMeta.validateObjArg(CURVES.create_fromName('gear',_settingsSize,
                                                                               '{0}+'.format(_jointOrientation[2]),
                                                                               baseSize=1.0),'cgmObject',setClass=True)
    
                
                mSettingsShape.doSnapTo(_mTar.mNode)
                
                #SNAPCALLS.get_special_pos([_mTar,str_meshShape],'castNear',str_settingsDirections,False)
                
                mSettingsShape.p_position = newPos
                mMesh_tmp.delete()
            
                SNAP.aim_atPoint(mSettingsShape.mNode,
                                 _mTar.p_position,
                                 aimAxis=_jointOrientation[0]+'+',
                                 mode = 'vector',
                                 vectorUp= _mTar.getAxisVector(_jointOrientation[0]+'-'))
            else:
                mSettingsShape = mSettingsHelper.doDuplicate(po=False)
            
            mSettingsShape.parent = _mTar

            mSettings = mSettingsShape
            CORERIG.match_orientation(mSettings.mNode, _mTar.mNode)
            
            ATTR.copy_to(self.mModule.mNode,'cgmName',mSettings.mNode,driven='target')

            mSettings.doStore('cgmTypeModifier','settings')
            mSettings.doName()
            self.mHandleFactory.color(mSettings.mNode, controlType = 'sub')
            mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect
            
            #cgmGEN.func_snapShot(vars())
            #mSettings.select()
        else:
            raise ValueError("Unknown settingsPlace: {1}".format(settingsPlace))
        
        return mSettings
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
def direct(self,ml_rigJoints = None, mult = 2.0):
    try:
        _str_func = 'direct'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        try:_offset = mBlock.jointRadius
        except:_offset = self.v_offset * mult
        _jointOrientation = self.d_orientation['str']        
        
        if not ml_rigJoints:
            ml_rigJoints = mRigNull.msgList_get('rigJoints')
            
        
        if len(ml_rigJoints) < 3:
            d_direct = {'size':_offset}
        else:
            d_direct = {'size':_offset}
    
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
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
def segment_handles(self,ml_handles = None):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        if not ml_handles:
            raise ValueError("{0} | ml_handles required".format(_str_func))
            
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
      
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
def leverBAK(self,ml_handles = None):
    try:
        _str_func = 'lever'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        ml_formHandles = self.ml_formHandles
        
        #Get our curves...
        ml_targets = []
        for i,mHandle in enumerate(ml_formHandles[:2]):
            ml_targets.append(mHandle.loftCurve)
            if i:
                continue
            ml_sub = mHandle.msgList_get('subShapers')
            if ml_sub:
                for mSub in ml_sub:
                    ml_targets.append(mSub)
                    
        ml_new = []
        for mTar in ml_targets:
            mDup = mTar.doDuplicate(po=False)
            DIST.offsetShape_byVector(mDup.mNode,_offset)
            mDup.p_parent = False
            ml_new.append(mDup)
            
        CURVES.connect([mTar.mNode for mTar in ml_new],mode='even')
        
        return ml_new[0]
        
        mLeverControlJoint = mRigNull.getMessageAsMeta('leverDirect')
        mLeverControlFK =  mRigNull.getMessageAsMeta('leverFK')
        if not mLeverControlJoint:
            mLeverControlJoint = mLeverControlFK
        else:
            mLeverControlJoint = mLeverControlJoint
        log.debug("|{0}| >> mLeverControlJoint: {1}".format(_str_func,mLeverControlJoint))            
    
        dist_lever = DIST.get_distance_between_points(ml_prerigHandles[0].p_position,
                                                      ml_prerigHandles[1].p_position)
        log.debug("|{0}| >> Lever dist: {1}".format(_str_func,dist_lever))
    
        #Dup our rig joint and move it 
        mDup = mLeverControlJoint.doDuplicate()
        mDup.p_parent = mLeverControlJoint
    
        mDup.resetAttrs()
        ATTR.set(mDup.mNode, 't{0}'.format(_jointOrientation[0]), dist_lever * .8)
    
        mDup2 = mDup.doDuplicate()
        ATTR.set(mDup2.mNode, 't{0}'.format(_jointOrientation[0]), dist_lever * .25)
    
    
        ml_clavShapes = BUILDUTILS.shapes_fromCast(self, targets= [mDup2.mNode,
                                                                   #ml_fkJoints[0].mNode],
                                                                   mDup.mNode],
                                                         aimVector= self.d_orientation['vectorOut'],
                                                         offset=_offset,
                                                         f_factor=0,
                                                         mode = 'frameHandle')
    
        mHandleFactory.color(ml_clavShapes[0].mNode, controlType = 'main')        
        CORERIG.shapeParent_in_place(mLeverControlFK.mNode,ml_clavShapes[0].mNode, True, replaceShapes=True)
        #CORERIG.shapeParent_in_place(mLeverFKJnt.mNode,ml_clavShapes[0].mNode, False, replaceShapes=True)
    
        mc.delete([mShape.mNode for mShape in ml_clavShapes] + [mDup.mNode,mDup2.mNode])        

      
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

def lever(self,ball = False):
    try:
        _str_func = 'lever_digit'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        ml_formHandles = self.ml_formHandles
        ml_prerigHandles = self.ml_prerigHandles
        mHandleFactory = self.mHandleFactory
        
        #Mesh shapes ----------------------------------------------------------
        mMesh_tmp =  self.mBlock.atUtils('get_castMesh')
        str_meshShape = mMesh_tmp.getShapes()[0]        
        
        #Figure out our knots ----------------------------------------------------
        mMain = self.ml_formHandlesUse[0]
        mMainLoft = mMain.loftCurve
        idxMain = self.ml_shapers.index(mMainLoft)
        
        
        minU = ATTR.get(str_meshShape,'minValueU')
        maxU = ATTR.get(str_meshShape,'maxValueU')
        
        f_factor = (maxU-minU)/(20)        
        
        pprint.pprint(vars())
        
        #reload(SURF)
         
        #Meat ==============================================================
        mLeverDirect = mRigNull.getMessageAsMeta('leverDirect')
        mLeverFK = mRigNull.getMessageAsMeta('leverFK')
        
        mLeverControlCast = mLeverDirect
        if not mLeverControlCast:
            mLeverControlCast = mLeverFK
        
        
        log.debug("|{0}| >> mLeverControlCast: {1}".format(_str_func,mLeverControlCast))
        
        dist_lever = DIST.get_distance_between_points(ml_prerigHandles[0].p_position,
                                                      ml_prerigHandles[1].p_position)
        log.debug("|{0}| >> Lever dist: {1}".format(_str_func,dist_lever))

        #Dup our rig joint and move it 
        mDup = mLeverControlCast.doDuplicate(po=True)
        mDup.p_parent = mLeverControlCast
        mDup.resetAttrs()
        ATTR.set(mDup.mNode, 't{0}'.format(_jointOrientation[0]), dist_lever * .5)

        l_lolis = []
        l_starts = []
        
        _mTar = mDup
        
        if ball:
            #Loli ===============================================================
            mDefineLeverObj = mBlock.defineLeverHelper
            _mVectorLeverUp = MATH.get_obj_vector(mDefineLeverObj.mNode,'y+',asEuclid=True)
            #mOrientHelper = mBlock.orientHelper
            #_mVectorLeverUp = MATH.get_obj_vector(mOrientHelper.mNode,'y+',asEuclid=True)
            
            mBall_tmp =  mBlock.atUtils('get_castMesh')
            str_ballShape = mBall_tmp.getShapes()[0]
            pos = RAYS.cast(str_ballShape,
                            startPoint=_mTar.p_position,
                            vector=_mVectorLeverUp).get('near')
            
            #pos = RAYS.get_cast_pos(_mTar.mNode,_mVectorLeverUp,shapes = str_ballShape)
            #SNAPCALLS.get_special_pos([_mTar,str_ballShape],'castNear',str_settingsDirections,False)
            vec = MATH.get_vector_of_two_points(_mTar.p_position, pos)
            newPos = DIST.get_pos_by_vec_dist(pos,vec,_offset * 4)
            
            ball = CURVES.create_fromName('sphere',_offset * 2)
            mBall = cgmMeta.cgmObject(ball)
            mBall.p_position = newPos
            
            SNAP.aim_atPoint(mBall.mNode,
                             _mTar.p_position,
                             aimAxis=_jointOrientation[0]+'+',
                             mode = 'vector',
                             vectorUp= _mTar.getAxisVector(_jointOrientation[0]+'-'))                
            
            line = mc.curve (d=1, ep = [pos,newPos], os=True)
            l_lolis.extend([ball,line])        
            ATTR.set(mDup.mNode, 't{0}'.format(_jointOrientation[0]), dist_lever * .8)
            CORERIG.shapeParent_in_place(mLeverFK.mNode,l_lolis,False)
            mBall_tmp.delete()

        #Main clav section ========================================
        """
        ml_clavShapes = BUILDUTILS.shapes_fromCast(self, 
                                                   targets= [mLeverControlCast.mNode,
                                                              mDup.mNode],
                                                         aimVector= self.d_orientation['vectorOut'],
                                                         connectionPoints = 5,
                                                         f_factor=0,
                                                         offset=_offset,
                                                         mode = 'frameHandle')"""
        
        l_curves = SURF.get_splitValues(str_meshShape,
                                        knotIndices=[0,idxMain],
                                        mode='u',
                                        insertMax=False,
                                        preInset = f_factor*.5,
                                        postInset = -f_factor*.5,
                                        curvesCreate=True,
                                        curvesConnect=True,
                                        connectionPoints=6,
                                        offset=self.v_offset)
        ml_shapes = cgmMeta.validateObjListArg(l_curves)
        
        
        
        
        mHandleFactory.color(mLeverFK.mNode, controlType = 'sub')
        CORERIG.shapeParent_in_place(mLeverFK.mNode,
                                     ml_shapes[0].mNode,
                                     False,replaceShapes=False)            
        mDup.delete()
        for mShape in ml_shapes:
            try:mShape.delete()
            except:pass
        mMesh_tmp.delete()

      
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

l_pivotOrder = BLOCKSHARE._l_pivotOrder
d_pivotBankNames = BLOCKSHARE._d_pivotBankNames
def pivotShapes(self, mPivotHelper = None, l_pivotOrder = l_pivotOrder):
    """
    Builder of shapes for pivot setup. Excpects to find pivotHelper on block
    
    :parameters:
        self(cgmRigBlock)
        mRigNull(cgmRigNull) | if none provided, tries to find it

    :returns
        dict
    """
    _str_func = 'pivotShapes'
    log.debug(cgmGEN.logString_start(_str_func))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    _offset = self.v_offset
    _jointOrientation = self.d_orientation['str']

    if mRigNull is None:
        mRigNull = self.moduleTarget.rigNull
        
    if mPivotHelper is None:
        if not self.getMessage('pivotHelper'):
            raise ValueError("|{0}| >> No pivots helper found. mBlock: {1}".format(_str_func,mBlock))
        mPivotHelper = mBlock.pivotHelper
        
    md = {}
    for a in l_pivotOrder:
        str_a = 'pivot' + a.capitalize()
        if mPivotHelper.getMessage(str_a):
            log.debug("|{0}| >> Found: {1}".format(_str_func,str_a))
            mPivotOrig = mPivotHelper.getMessage(str_a,asMeta=True)[0]
            
            if a in ['tilt','spin']:
                if a == 'tilt':
                    _tag = 'front'
                else:
                    _tag = 'center'
                    
                mPivot = mPivotHelper.getMessage('pivot' + _tag.capitalize(),asMeta=True)[0].doDuplicate(po=False,ic=False)
                CORERIG.shapeParent_in_place(mPivot.mNode, mPivotOrig.mNode,replaceShapes=True)
            else:
                mPivot = mPivotOrig.doDuplicate(po=False,ic=False)
                
            l_const = mPivot.getConstraintsTo(fullPath=1)
            if l_const:
                mc.delete(l_const)
            mRigNull.connectChildNode(mPivot,str_a,'rigNull')#Connect
            _nameSet = NAMETOOLS.combineDict( mPivotOrig.getNameDict(ignore=['cgmType','cgmTypeModifier','cgmDirection']))
            mPivot.parent = False            
            mPivot.cgmName = "{0}_{1}".format(self.d_module['partName'], _nameSet)
            if mPivot.getMayaAttr('cgmDirection'):
                mPivot.deleteAttr('cgmDirection')
            #mPivot.rename("{0}_{1}".format(self.d_module['partName'], mPivot.p_nameBase))
            mPivot.doName()
            md[a] = mPivot
    return True


def backup(self,ml_handles = None):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        if not ml_handles:
            raise ValueError("{0} | ml_handles required".format(_str_func))        
      
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())