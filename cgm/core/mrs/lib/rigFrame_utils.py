"""
------------------------------------------
cgm.core.mrs.blocks.organic.limb
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
__MAYALOCAL = 'RIGFRAME'

# From Python =============================================================
import copy
import re
import pprint
import time
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
import importlib
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel    

# From Red9 =============================================================
import cgm.core.cgm_General as cgmGEN
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.rig.ik_utils as IK
import cgm.core.classes.NodeFactory as NODEFACTORY

"""
from Red9.core import Red9_Meta as r9Meta
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.rig.general_utils as CORERIGGEN
import cgm.core.lib.transform_utils as TRANS

import cgm.core.tools.lib.snap_calls as SNAPCALLS
from cgm.core import cgm_RigMeta as cgmRigMeta
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.lib.locator_utils as LOC
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.position_utils as POS
import cgm.core.rig.joint_utils as JOINT
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.mrs.lib.builder_utils as BUILDUTILS
import cgm.core.lib.shapeCaster as SHAPECASTER
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.cgm_RigMeta as cgmRIGMETA
"""

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.09122018'

log_start = cgmGEN.log_start


def get_moduleScaleNoTransformGroup(self, mScaler = False):
    mGrp = self.mModule.getMessageAsMeta('noTransformScaleGroup')
    if mGrp:
        return mGrp
    
    if not self.mModule.getMessage('noTransformScaleGroup'):
        mGrp = self.mConstrainNull.doCreateAt()
        mGrp.addAttr('cgmName',self.d_module['partName'],lock=True)
        mGrp.addAttr('cgmTypeModifier','noTransformScale',lock=True)
        mGrp.doName()
        mGrp.parent = self.d_module['mMasterNull']
        self.mModule.connectChildNode(mGrp,'noTransformScaleGroup','module')
        if mScaler:
            mc.scaleConstraint(mScaler.mNode, mGrp.mNode, maintainOffset = True)
        mGrp.dagLock()
        
        
    self.mScaleNoTransformGroup = mGrp
    return mGrp


def get_spinGroup(self,mStart,mRoot,mControl):
    #=========================================================================================
    log.debug("|{0}| >> spin setup...".format(_str_func))

    #Make a spin group
    mSpinGroup = mStart.doGroup(False,False,asMeta=True)
    mSpinGroup.doCopyNameTagsFromObject(self.mModule.mNode, ignore = ['cgmName','cgmType'])	
    mSpinGroup.addAttr('cgmName','{0}NoFlipSpin'.format(self.d_module['partName']))
    mSpinGroup.doName()

    mSpinGroup.parent = mRoot

    mSpinGroup.doGroup(True,True,typeModifier='zero')

    #Setup arg
    mPlug_spin = cgmMeta.cgmAttr(mControl,'spin',attrType='float',keyable=True, defaultValue = 0, hidden = False)
    mPlug_spin.doConnectOut("%s.r%s"%(mSpinGroup.mNode,self.d_orientation['str'][0]))
    return mSpinGroup


def segment_mid(self, ml_handles = None,ml_ribbonHandles= None, mGroup = None,
                mIKBase = None, mIKEnd = None, ml_ikJoints = None,
                upMode = 'matrix'):
    try:
        _str_func = 'segment_mid'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mModule = self.mModule
        
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        _str_mode = mBlock.getEnumValueString('ikMidSetup')
        
        if not ml_handles:
            
            raise ValueError("{0} | ml_handles required".format(_str_func))
        if not ml_ribbonHandles:
            raise ValueError("{0} | ml_ribbonHandles required".format(_str_func))
        

                
        ml_midTrackJoints = copy.copy(ml_ribbonHandles)
        
        #Handles... ==============================================================
        
        ml_drivers = []
        for mHandle in ml_handles:
            mHandle.masterGroup.parent = mGroup
            
            mDriver = mHandle.doCreateAt('joint',setClass='cgmObject')
            mDriver.rename('{0}_mainDriver'.format(mHandle.p_nameBase))
            mDriver.p_parent = mHandle.masterGroup
            mHandle.doStore('mainDriver',mDriver.mNode,'msg')
            ml_drivers.append(mDriver)
            
            #if _str_mode == 'ribbon':
                #ml_midTrackJoints.insert(-1, mDriver)
                #Setup our aim setup ---------------------------------------------------------
                #mFollicle = mHandle.masterGroup.getMessageAsMeta('ribbonDriver')
                
                #mTar = ml_ikJoints[1].doCreateAt(setClass='cgmObject')
                #mTar.rename('{0}_mid_baseTarget'.format(self.d_module['partName']))
                #mTar.p_parent = mIKBase
                
                
                
                #mc.pointConstraint([mFollicle.mNode],mDriver.mNode,maintainOffset=True)
                #mc.aimConstraint([mTar.mNode], mDriver.mNode, maintainOffset = True, #skip = 'z',
                                 #aimVector = [0,0,-1], upVector = [1,0,0], worldUpObject = mHandle.masterGroup.mNode,
                                 #worldUpType = 'objectrotation', worldUpVector = [1,0,0])
                
            
        #Setup.. ================================================================
        _len = len(ml_handles) 
        if _str_mode == 'ribbon':
            #Make our Driver -----------------------------------------------------
            ml_midTrackJoints.insert(1,mHandle)
            ml_midTrackJoints = [ml_ribbonHandles[0]] + ml_handles + [ml_ribbonHandles[-1]]
            d_mid = {'jointList':[mJnt.mNode for mJnt in ml_midTrackJoints],
                     #'ribbonJoints':[mObj.mNode for mObj in ml_rigJoints[self.int_segBaseIdx:]],
                     'baseName' :self.d_module['partName'] + '_midRibbon',
                     'driverSetup':None,
                     'squashStretch':None,
                     'msgDriver':'masterGroup',
                     'specialMode':'noStartEnd',
                     'paramaterization':'floating',
                     'connectBy':'constraint',
                     'influences':ml_ribbonHandles,
                     'moduleInstance' : mModule}
            #reload(IK)
            IK.ribbon(**d_mid)
            
        elif _str_mode == 'prntConstraint':
            mc.parentConstraint([mObj.mNode for mObj in ml_ribbonHandles], mDriver.mNode, maintainOffset = 1)
        
        elif _str_mode in ['linearTrack','cubicTrack']:
            ml_track = ml_ribbonHandles
            
            if _str_mode == 'cubicTrack':
                if _len >= 3:
                    for i,mHandle in enumerate([ml_handles[0],ml_handles[1]]):
                        mCurveDriver = mHandle.doCreateAt(setClass='cgmObject')
                        mCurveDriver.rename("{}_curveDriver".format(mHandle.p_nameBase))
                        
                        if not i:
                            if mIKBase:
                                mCurveDriver.p_parent = mIKBase
                            else:
                                mCurveDriver.p_parent = mGroup
                        else:
                            mCurveDriver.p_parent = mIKEnd
                        
                        ml_track.insert(-1, mCurveDriver)
                else:
                    for i,mHandle in enumerate(ml_handles):
                        mCurveDriver = mHandle.doCreateAt(setClass='cgmObject')
                        mCurveDriver.rename("{}_curveDriver".format(mHandle.p_nameBase))
                        

                        mCurveDriver.p_parent = mIKEnd
                        
                        ml_track.insert(-1, mCurveDriver)                    
                
            
            #IKMid Handle ---------------------------------------------------------------------
            _trackCurve,_l_clusters = CORERIG.create_at([mObj.mNode for mObj in ml_track],_str_mode,baseName = self.d_module['partName'] + '_mid{}'.format(_str_mode))
            mCrv = cgmMeta.asMeta(_trackCurve)
            mShape = cgmMeta.asMeta(mCrv.getShapes()[0])
            
            ml_clusters = cgmMeta.asMeta([s[1] for s in _l_clusters])
            
            for mObj in [mCrv] + ml_clusters:
                mObj.overrideEnabled = 1		
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(_trackCurve,'overrideVisibility'))
                cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(_trackCurve,'overrideDisplayType'))    
            
            mCrv.p_parent = mModule.rigNull.mNode
                
            for mDriver in ml_drivers:
                RIGCONSTRAINT.attach_toShape(mDriver, mShape.mNode, 'conPoint',parentTo=mModule.rigNull.mNode, floating=False)
                
            
            if len(ml_drivers) > 1:
                for i,mDriver in enumerate(ml_drivers):
                    if mDriver == ml_drivers[-1]:
                        mc.aimConstraint([ml_drivers[-2].mNode],
                                         mDriver.mNode,
                                         maintainOffset = True, #skip = 'z',
                                         aimVector = [0,0,-1], upVector = [0,1,0],
                                         worldUpObject = mIKEnd.mNode,
                                         worldUpType = 'objectrotation', worldUpVector = [1,0,0])      
                    elif mDriver == ml_drivers[0]:
                        mc.aimConstraint([ml_drivers[i+1].mNode],
                                         mDriver.mNode,
                                         maintainOffset = True, #skip = 'z',
                                         aimVector = [0,0,-1], upVector = [0,1,0],
                                         worldUpObject = mIKBase.mNode,
                                         worldUpType = 'objectrotation', worldUpVector = [1,0,0])                              
                    else:
                        mc.aimConstraint([ml_drivers[i+1].mNode],
                                         mDriver.mNode,
                                         maintainOffset = True, #skip = 'z',
                                         aimVector = [0,0,1], upVector = [0,1,0],
                                         worldUpObject = ml_drivers[i-1].mNode,
                                         worldUpType = 'objectrotation', worldUpVector = [1,0,0])
            else:
                mc.aimConstraint([mIKBase.mNode],
                                 mDriver.mNode,
                                 maintainOffset = True, #skip = 'z',
                                 aimVector = [0,0,-1], upVector = [0,1,0],
                                 worldUpObject = mIKEnd.mNode,
                                 worldUpType = 'objectrotation', worldUpVector = [1,0,0])                
            
        else:
            raise Exception("{} | unknown mode : {}".format(_str_func, _str_mode))
            
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
    
    

def ik_rp(self,mStart,mEnd,ml_ikFrame = None,
          mIKControl=None,mIKBaseControl = None,
          mIKHandleDriver = None,mRoot=None,mIKGroup=None,mIKControlEnd=None,
          ml_ikFullChain=None):
    try:
        _str_func = "ik_rp"
        log.debug("|{0}| >> {1}...".format(_str_func,_str_func)+'-'*60)
        
        mRigNull = self.mRigNull
        mBlock = self.mBlock
        
        if not ml_ikFrame:
            ml_ikFrame = self.ml_handleTargetsCulled
        if not mIKControl:
            raise ValueError("Must have mIKControl")
            
        if not mIKHandleDriver:
            raise ValueError("Must have mIKHandleDriver")
        if not mRoot:
            raise ValueError("Must have mRoot")
        
        log.debug("|{0}| >> rp setup...".format(_str_func))
        mIKMid = mRigNull.controlIKMid
        str_ikEnd = mBlock.getEnumValueString('ikEnd')
        #Measture ======================================================
        log.debug("|{0}| >> measure... ".format(_str_func)+'-'*30)
        
        res_ikScale = self.UTILS.get_blockScale(self,
                                                '{0}_ikMeasure'.format(self.d_module['partName'],),
                                                ml_ikFrame)
        
        mPlug_masterScale = res_ikScale[0]
        mMasterCurve = res_ikScale[1]
        mMasterCurve.p_parent = mRoot
        self.fnc_connect_toRigGutsVis( mMasterCurve )
        mMasterCurve.dagLock(True)
    
        #Unparent the children from the end while we set stuff up...
        log.debug("|{0}| >> end unparent ...".format(_str_func)+'-'*30)
        
        ml_end_children = mEnd.getChildren(asMeta=True)
        if ml_end_children:
            for mChild in ml_end_children:
                mChild.parent = False
    
    
        #Build the IK ---------------------------------------------------------------------
        cgmGEN._reloadMod(IK)
        """
        if mIKControlEnd and str_ikEnd in ['tipCombo']:
            mMainIKControl = mIKControlEnd
        else:
            mMainIKControl = mIKControl
        """
        _d_ik= {'globalScaleAttr':mPlug_masterScale.p_combinedName,#mPlug_globalScale.p_combinedName,
                'stretch':'translate',
                'lockMid':True,
                'rpHandle':mIKMid.mNode,
                'nameSuffix':'ik',
                'baseName':'{0}_ikRP'.format(self.d_module['partName']),
                'controlObject':mIKControl.mNode,
                'moduleInstance':self.mModule.mNode}
    
        d_ikReturn = IK.handle(mStart.mNode,mEnd.mNode,**_d_ik)
        mIKHandle = d_ikReturn['mHandle']
        ml_distHandlesNF = d_ikReturn['ml_distHandles']
        mRPHandleNF = d_ikReturn['mRPHandle']
    
        #>>>Parent IK handles -----------------------------------------------------------------
        log.debug("|{0}| >> parent IK stuff ...".format(_str_func)+'-'*30)
    
        mIKHandle.parent = mIKHandleDriver.mNode#handle to control	
        for mObj in ml_distHandlesNF[:-1]:
            mObj.parent = mRoot
        ml_distHandlesNF[-1].parent = mIKHandleDriver.mNode#handle to control
        ml_distHandlesNF[1].parent = mIKMid
        ml_distHandlesNF[1].t = 0,0,0
        ml_distHandlesNF[1].r = 0,0,0
    
        if mIKBaseControl:
            ml_distHandlesNF[0].parent = mIKBaseControl
    
        #>>> Fix our ik_handle twist at the end of all of the parenting
        IK.handle_fixTwist(mIKHandle,self.d_orientation['str'][0])#Fix the twist
    
        if mIKControlEnd:
            mIKEndDriver = mIKControlEnd
        else:
            mIKEndDriver = mIKControl
    
        if ml_end_children:
            for mChild in ml_end_children:
                mChild.parent = mEnd                
    
        #mc.scaleConstraint([mIKControl.mNode],
        #                    ml_ikFrame[self.int_handleEndIdx].mNode,
        #                    maintainOffset = True)                
        #if mIKBaseControl:
            #ml_ikFrame[0].parent = mRigNull.controlIKBase
    
        #if mIKBaseControl:
            #mc.pointConstraint(mIKBaseControl.mNode, ml_ikFrame[0].mNode,maintainOffset=True)
    
    
        #Make a spin group ===========================================================
        log.debug("|{0}| >> spin group ...".format(_str_func)+'-'*30)
        
        mSpinGroup = mStart.doGroup(False,False,asMeta=True)
        mSpinGroup.doCopyNameTagsFromObject(self.mModule.mNode, ignore = ['cgmName','cgmType'])	
        mSpinGroup.addAttr('cgmName','{0}NoFlipSpin'.format(self.d_module['partName']))
        mSpinGroup.doName()
        ATTR.set(mSpinGroup.mNode, 'rotateOrder', self.d_orientation['str'])
    
    
        mSpinGroup.parent = mIKGroup
        mSpinGroup.doGroup(True,True,typeModifier='zero')
        mSpinGroupAdd = mSpinGroup.doDuplicate()
    
        mSpinGroupAdd.doStore('cgmTypeModifier','addSpin')
        mSpinGroupAdd.doName()
        mSpinGroupAdd.p_parent = mSpinGroup
    
        if mIKBaseControl:
            mc.pointConstraint(mIKBaseControl.mNode, mSpinGroup.mNode,maintainOffset=True)
    
        #Setup arg
        #mPlug_spin = cgmMeta.cgmAttr(mIKControl,'spin',attrType='float',keyable=True, defaultValue = 0, hidden = False)
        #mPlug_spin.doConnectOut("%s.r%s"%(mSpinGroup.mNode,_jointOrientation[0]))
    
        mSpinTarget = mIKControl
    
        if mBlock.getMayaAttr('ikRPAim'):
            mc.aimConstraint(mSpinTarget.mNode, mSpinGroup.mNode, maintainOffset = False,
                             aimVector = [0,0,1], upVector = [0,1,0], 
                             worldUpType = 'none')
        else:
            mc.aimConstraint(mSpinTarget.mNode, mSpinGroup.mNode, maintainOffset = False,
                             aimVector = [0,0,1], upVector = [0,1,0], 
                             worldUpObject = mSpinTarget.mNode,
                             worldUpType = 'objectrotation', 
                             worldUpVector = self.v_twistUp)
    
        mPlug_spinMid = cgmMeta.cgmAttr(mSpinTarget,'spinMid',attrType='float',defaultValue = 0,keyable = True,lock=False,hidden=False)	
        
        _direction = self.d_module.get('direction') or 'center'
    
        if _direction.lower() == 'right':
            str_arg = "{0}.r{1} = -{2}".format(mSpinGroupAdd.mNode,
                                               self.d_orientation['str'][0].lower(),
                                               mPlug_spinMid.p_combinedShortName)
            log.debug("|{0}| >> Right knee spin: {1}".format(_str_func,str_arg))        
            NODEFACTORY.argsToNodes(str_arg).doBuild()
        else:
            mPlug_spinMid.doConnectOut("{0}.r{1}".format(mSpinGroupAdd.mNode,self.d_orientation['str'][0]))
    
        mSpinGroup.dagLock(True)
        mSpinGroupAdd.dagLock(True)
    
        #>>> mBallRotationControl ==========================================================
        mIKBallRotationControl = mRigNull.getMessageAsMeta('controlBallRotation')
        if mIKBallRotationControl:# and str_ikEnd not in ['tipCombo']:
            log.debug("|{0}| >> mIKBallRotationControl...".format(_str_func)+'-'*30)
            
            mBallOrientGroup = cgmMeta.validateObjArg(mIKBallRotationControl.doGroup(True,False,asMeta=True,typeModifier = 'orient'),'cgmObject',setClass=True)
            ATTR.set(mBallOrientGroup.mNode, 'rotateOrder', self.d_orientation['str'])
    
            mLocBase = mIKBallRotationControl.doCreateAt()
            mLocAim = mIKBallRotationControl.doCreateAt()
    
            mLocAim.doStore('cgmTypeModifier','extendedIK')
            mLocBase = mIKBallRotationControl.doCreateAt()
    
            mLocBase.doName()
            mLocAim.doName()
    
            mLocAim.p_parent = ml_ikFullChain[-1]
            mLocBase.p_parent = mIKBallRotationControl.masterGroup
    
    
            const = mc.orientConstraint([mLocAim.mNode,mLocBase.mNode],
                                        mBallOrientGroup.mNode, maintainOffset = True)[0]
    
            d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mIKControl.mNode,
                                                                  'extendIK'],
                                                                 [mIKControl.mNode,'resRootFollow'],
                                                                 [mIKControl.mNode,'resFullFollow'],
                                                                 keyable=True)
    
            targetWeights = mc.orientConstraint(const,q=True,
                                                weightAliasList=True,
                                                maintainOffset=True)
    
            #Connect                                  
            d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
            d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
            d_blendReturn['d_result1']['mi_plug'].p_hidden = True
            d_blendReturn['d_result2']['mi_plug'].p_hidden = True                    
    
    
            mBallOrientGroup.dagLock(True)
            mLocAim.dagLock(True)
            mLocBase.dagLock(True)
    
            mIKBallRotationControl.p_parent = mBallOrientGroup                    
    
    
            #Joint constraint -------------------------
            mIKBallRotationControl.masterGroup.p_parent = mPivotResultDriver
            mc.orientConstraint([mIKBallRotationControl.mNode],
                                ml_ikFrame[self.int_handleEndIdx].mNode,
                                maintainOffset = True)
            mc.parentConstraint([mPivotResultDriver.mNode],
                                ml_ikFrame[self.int_handleEndIdx+1].mNode,
                                maintainOffset = True)
    
            ATTR.set_default(mIKControl.mNode, 'extendIK', 1.0)
            mIKControl.extendIK = 0.0
    
        elif str_ikEnd == 'bank':
            mc.orientConstraint([mPivotResultDriver.mNode],
                                ml_ikFrame[self.int_handleEndIdx].mNode,
                                maintainOffset = True)
        elif str_ikEnd == 'pad':
            mc.orientConstraint([mPivotResultDriver.mNode],
                                ml_ikFrame[self.int_handleEndIdx].mNode,
                                maintainOffset = True)                    
        else:
            mc.orientConstraint([mIKEndDriver.mNode],
                                ml_ikFrame[self.int_handleEndIdx].mNode,
                                maintainOffset = True)
    
    
        #Mid IK driver -----------------------------------------------------------------------
        log.debug("|{0}| >> mid Ik driver...".format(_str_func)+'-'*30)
        
        log.debug("|{0}| >> mid IK driver.".format(_str_func))
        mMidControlDriver = mIKMid.doCreateAt()
        mMidControlDriver.addAttr('cgmName','{0}_midIK'.format(self.d_module['partName']))
        mMidControlDriver.addAttr('cgmType','driver')
        mMidControlDriver.doName()
        mMidControlDriver.addAttr('cgmAlias', 'midDriver')
    
    
        if mIKBaseControl:
            l_midDrivers = [mIKBaseControl.mNode]
        else:
            l_midDrivers = [mRoot.mNode]
    
        if str_ikEnd in ['tipCombo'] and mIKControlEnd:
            log.debug("|{0}| >> mIKControlEnd + tipCombo...".format(_str_func))
            l_midDrivers.append(mIKControl.mNode)
        else:
            l_midDrivers.append(mIKHandleDriver.mNode)
    
    
        mc.pointConstraint(l_midDrivers, mMidControlDriver.mNode)
        mMidControlDriver.parent = mSpinGroupAdd#mIKGroup
        mIKMid.masterGroup.parent = mMidControlDriver
        mMidControlDriver.dagLock(True)
    
        #Mid IK trace
        log.debug("|{0}| >> midIK track Crv".format(_str_func, mIKMid))
        trackcrv,clusters = CORERIG.create_at([mIKMid.mNode,
                                               ml_ikFrame[MATH.get_midIndex(len(
                                                                               ml_ikFrame))].mNode],#ml_handleJoints[1]],
                                              'linearTrack',
                                              baseName = '{0}_midTrack'.format(self.d_module['partName']))
    
        mTrackCrv = cgmMeta.asMeta(trackcrv)
        mTrackCrv.p_parent = self.mModule
        mHandleFactory = mBlock.asHandleFactory()
        mHandleFactory.color(mTrackCrv.mNode, controlType = 'sub')
    
        for s in mTrackCrv.getShapes(asMeta=True):
            s.overrideEnabled = 1
            s.overrideDisplayType = 2
        mTrackCrv.doConnectIn('visibility',"{0}.v".format(mIKGroup.mNode))
    
        #Full IK chain -----------------------------------------------------------------------
        if ml_ikFullChain:
            log.debug("|{0}| >> Full IK Chain...".format(_str_func))
            _d_ik= {'globalScaleAttr':mPlug_masterScale.p_combinedName,#mPlug_globalScale.p_combinedName,
                    'stretch':'translate',
                    'lockMid':False,
                    'rpHandle':mIKMid.mNode,
                    'baseName':'{0}_ikFullChain'.format(self.d_module['partName']),
                    'nameSuffix':'ikFull',
                    'controlObject':mIKControl.mNode,
                    'moduleInstance':self.mModule.mNode}
    
            d_ikReturn = IK.handle(ml_ikFullChain[0],ml_ikFullChain[-1],**_d_ik)
            mIKHandle = d_ikReturn['mHandle']
            ml_distHandlesNF = d_ikReturn['ml_distHandles']
            mRPHandleNF = d_ikReturn['mRPHandle']
    
            mIKHandle.parent = mIKControl.mNode#handle to control	
            for mObj in ml_distHandlesNF[:-1]:
                mObj.parent = mRoot
            ml_distHandlesNF[-1].parent = mIKControl.mNode#handle to control
            #ml_distHandlesNF[1].parent = mIKMid
            #ml_distHandlesNF[1].t = 0,0,0
            #ml_distHandlesNF[1].r = 0,0,0
    
            #>>> Fix our ik_handle twist at the end of all of the parenting
            IK.handle_fixTwist(mIKHandle,self.d_orientation['str'][0])#Fix the twist
    
            #mIKControl.masterGroup.p_parent = ml_ikFullChain[-2]
            
            
        ######mc.parentConstraint([mIKControl.mNode], ml_ikFrame[-1].mNode, maintainOffset = True)
        
        if mIKBaseControl:
            ml_ikFrame[0].parent = mIKBaseControl
        #if mIKBaseControl:
            #mc.pointConstraint(mIKBaseControl.mNode, ml_ikFrame[0].mNode,maintainOffset=True)
            
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
            
def get_spinGroup(self):
    try:
        _str_func = 'get_spinGroup'
        log_start(_str_func)
        
        #Make a spin group
        mSpinGroup = mStart.doGroup(False,False,asMeta=True)
        mSpinGroup.doCopyNameTagsFromObject(self.mModule.mNode, ignore = ['cgmName','cgmType'])	
        mSpinGroup.addAttr('cgmName','{0}NoFlipSpin'.format(self.d_module['partName']))
        mSpinGroup.doName()
    
        mSpinGroup.parent = mRoot
    
        mSpinGroup.doGroup(True,True,typeModifier='zero')
    
        #Setup arg
        mPlug_spin = cgmMeta.cgmAttr(mIKControl,'spin',attrType='float',keyable=True, defaultValue = 0, hidden = False)
        mPlug_spin.doConnectOut("%s.r%s"%(mSpinGroup.mNode,_jointOrientation[0]))
        return mSpinGroup
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

def spline(self, ml_ikJoints = None,ml_ribbonIkHandles=None,mIKControl=None,
           mIKBaseControl=None,ml_skinDrivers=None,mPlug_masterScale=None,stretchBy='scale',
           ikEndTwistConnect = True,extendEnd=False, aimEnd=False, mSettings = None):
    try:
        _str_func = 'spline'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        ml_ikUse = [mObj for mObj in ml_ikJoints]
        
        #ml_ribbonIkHandles = mRigNull.msgList_get('ribbonIKDrivers')
        #if not ml_ribbonIkHandles:
        #    raise ValueError,"No ribbon IKDriversFound"
            
        _aim = self.d_orientation['vectorAim']
        _aimNeg = self.d_orientation['vectorAimNeg']
        _up = self.d_orientation['vectorUp']
        _out = self.d_orientation['vectorOut']
        
        _l_posUse = [mObj.p_position for mObj in ml_ikUse]
        
        
        if extendEnd or aimEnd:
            #try:
            #    _l_posUse.append(self.ml_formHandles[ self.int_handleEndIdx ].p_position)
            #except:
            _l_posUse.append(ml_ikUse[-1].getPositionByAxisDistance( "{}+".format(_jointOrientation[0]),
                                                                     DIST.get_distance_between_points(_l_posUse[-1],
                                                                                                      _l_posUse[-2])))
            
        _crv = CORERIG.create_at(create='curve',l_pos = _l_posUse)
        
        
        #...-------------------------------------------------------------------------------
        
        #ATTR.set_default(mIKControl.mNode,'twistType',1)
        #ATTR.set(mIKControl.mNode,'twistType',1)        
        
        mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mHandle.mNode for mHandle in ml_skinDrivers],
                                                              _crv,
                                                              tsb=True,
                                                              maximumInfluences = 2,
                                                              normalizeWeights = 1,dropoffRate=5),
                                              'cgmNode',
                                              setClass=True)
    
        mSkinCluster.doStore('cgmName', _crv)
        mSkinCluster.doName()
        
        _node = mc.rebuildCurve(_crv, d=3, keepControlPoints=False,
                                ch=1,s=len(ml_skinDrivers),
                                n="{0}_reparamRebuild".format(_crv))
        mc.rename(_node[1],"{0}_reparamRebuild".format(_crv))
        
        #We're going to add another end joint so we can orient it
        """
        if extendEnd or aimEnd:
        
            #_l_posUse.append(ml_ikUse[-1].getPositionByAxisDistance( "{}+".format(_jointOrientation[0]),
             #                                                        DIST.get_distance_between_points(_l_posUse[-1],_l_posUse[-2])))
            
            
            
            mEnd = ml_ikUse.pop(-1)
            mEndHelp = mEnd.doDuplicate(po=True, ic=False)
            mEndHelp.rename("{}_endHelp".format(mEnd.p_nameBase))
            mEnd.p_parent = mEndHelp
            ml_ikUse.append(mEndHelp)"""
            
            

        mEnd = ml_ikUse[-1]
        if extendEnd:
            #We're going to add another end joint so we can stablize the end
            mEndHelp = ml_ikUse[-1].doDuplicate(po=True, ic=False)
            mEndHelp.rename("{}_endHelp".format( ml_ikUse[-1].p_nameBase))
            mEndHelp.p_parent = ml_ikUse[-1]
            ml_ikUse.append(mEndHelp)
            mEndHelp.p_position = _l_posUse[-1]
        
        
        if aimEnd:
            #Then we want to setup our aim
            mEndAim = mEnd.doCreateAt()
            mEndAim.rename("{}_endHelpAim".format(mEnd.p_nameBase))
            mEndAim.p_position = _l_posUse[-1]
            #mEndAim.p_parent = mIKControl or mEndHelp
            
            #mc.orientConstraint(mEndAim.mNode, mEnd.mNode, maintainOffset = True)
            """
            mc.aimConstraint(mEndAim.mNode,
                             mEnd.mNode,
                             maintainOffset = True, weight = 1,
                             aimVector = self.d_orientation['vectorAim'],
                             upVector = self.d_orientation['vectorUp'],
                             worldUpVector = self.d_orientation['vectorOut'],
                             worldUpObject = mEndHelp.mNode,
                             worldUpType = 'objectRotation' ) """        
        
        l = []
        log.info(cgmGEN.logString_sub(_str_func,'mlIKUse'))
        pprint.pprint(ml_ikUse)
        res_spline = IK.spline([mObj.mNode for mObj in ml_ikUse],
                               useCurve= _crv,
                               orientation = _jointOrientation,
                               advancedTwistSetup=True,
                               stretchBy=stretchBy,
                               baseName= self.d_module['partName'] + '_spline',
                               moduleInstance = self.mModule)
        
        mSplineCurve = res_spline['mSplineCurve']
        log.debug("|{0}| >> spline curve...".format(_str_func))
        
        mSplineCurve.doConnectIn('masterScale',mPlug_masterScale.p_combinedShortName)
    
        #Twist end...--------------------------------------------------------------------
        if ikEndTwistConnect:
            _twistAxis = mBlock.getEnumValueString('ikSplineTwistAxis')
            mPlug_addEnd = cgmMeta.cgmAttr(mIKControl.mNode,'twistEndAdd',attrType='float',keyable=True, hidden=False)

            arg1 = "{}.twistEnd = {}.r{} + {}".format(mSplineCurve.mNode,
                                                      mIKControl.mNode,
                                                      _twistAxis,#_jointOrientation[0],
                                                      mPlug_addEnd.p_combinedName)    
            
            NODEFACTORY.argsToNodes(arg1).doBuild()
            
            #start...
            mPlug_addEnd = cgmMeta.cgmAttr(mIKBaseControl.mNode,'twistBaseAdd',attrType='float',keyable=True, hidden=False)            
            arg1 = "{}.twistStart = {}.r{} + {}".format(mSplineCurve.mNode,
                                                        mIKBaseControl.mNode,
                                                        _twistAxis,#_jointOrientation[0],
                                                        mPlug_addEnd.p_combinedName)    
            
            NODEFACTORY.argsToNodes(arg1).doBuild()            
        else:
            ATTR.copy_to(mSplineCurve.mNode,'twistEnd',mSettings.mNode, driven='source')
            
            ATTR.copy_to(mSplineCurve.mNode,'twistStart',mSettings.mNode, driven='source')
            
            
        ATTR.copy_to(mSplineCurve.mNode,'stretch',mSettings.mNode, driven='source')
        ATTR.copy_to(mSplineCurve.mNode,'twistType',mSettings.mNode, driven='source')

        
        #mc.orientConstraint(mIKControl.mNode, ml_ikJoints[-1].mNode, maintainOffset=True)
        
      
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
    
def segment_handles(self, ml_handles = None, ml_handleParents = None, mIKBaseControl=None,
                    mRoot = None, str_ikBase = None, upMode = 'asdf'):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        if not ml_handles:
            raise ValueError("{0} | ml_handles required".format(_str_func))
        if not ml_handleParents:
            raise ValueError("{0} | ml_handleParents required".format(_str_func))
        
        ml_ribbonIkHandles = mRigNull.msgList_get('ribbonIKDrivers')
        if not ml_ribbonIkHandles:
            ml_ribbonIkHandles = ml_handleParents
            #raise ValueError,"No ribbon IKDriversFound"
        
        if str_ikBase == None:
            str_ikBase = mBlock.getEnumValueString('ikBase')
            
        _aim = self.d_orientation['vectorAim']
        _aimNeg = self.d_orientation['vectorAimNeg']
        _up = self.d_orientation['vectorUp']
        _out = self.d_orientation['vectorOut']        
    
        if str_ikBase == 'hips':
            log.debug("|{0}| >> hips setup...".format(_str_func))
            

    
        if len(ml_handles) == 1:
            mHipHandle = ml_handles[0]
            RIGCONSTRAINT.build_aimSequence(ml_handles,
                                            ml_ribbonIkHandles,
                                            [mIKBaseControl],#ml_handleParents,
                                            mode = 'singleBlend',
                                            upMode = 'objectRotation')
        else:
            if str_ikBase == 'pickles':#'hips':
                log.debug("|{0}| >> hips handles...".format(_str_func))                    
                ml_handles[0].masterGroup.p_parent = mIKBaseControl
                mHipHandle = ml_handles[1]
                mHipHandle.masterGroup.p_parent = mRoot
                mc.pointConstraint(mIKBaseControl.mNode,
                                   mHipHandle.masterGroup.mNode,
                                   maintainOffset = True)
    
                RIGCONSTRAINT.build_aimSequence(ml_handles[1],
                                                ml_ribbonIkHandles,
                                                [mIKBaseControl],#ml_handleParents,
                                                mode = 'singleBlend',
                                                upParent=self.d_orientation['vectorOut'],
                                                upMode = 'objectRotation')
                """
                        RIGCONSTRAINT.build_aimSequence(ml_handles[-1],
                                                        ml_ribbonIkHandles,
                                                         #[mRigNull.controlIK.mNode],#ml_handleParents,
                                                        mode = 'singleBlend',
                                                        upMode = 'objectRotation')"""
    

    
                for i,mHandle in enumerate(ml_handles):
                    if mHandle in ml_handles[:2]:# + [ml_handles[-1]]:
                        continue
    
                    mHandle.masterGroup.parent = ml_handleParents[i]
                    s_rootTarget = False
                    s_targetForward = False
                    s_targetBack = False
                    mMasterGroup = mHandle.masterGroup
                    b_first = False
                    if mHandle == ml_handles[0]:
                        log.debug("|{0}| >> First handle: {1}".format(_str_func,mHandle))
                        if len(ml_handles) <=2:
                            s_targetForward = ml_handleParents[-1].mNode
                        else:
                            s_targetForward = ml_handles[i+1].getMessage('masterGroup')[0]
                        s_rootTarget = mRoot.mNode
                        b_first = True
    
                    elif mHandle == ml_handles[-1]:
                        log.debug("|{0}| >> Last handle: {1}".format(_str_func,mHandle))
                        s_rootTarget = ml_handleParents[i].mNode                
                        s_targetBack = ml_handles[i-1].getMessage('masterGroup')[0]
                    else:
                        log.debug("|{0}| >> Reg handle: {1}".format(_str_func,mHandle))            
                        s_targetForward = ml_handles[i+1].getMessage('masterGroup')[0]
                        s_targetBack = ml_handles[i-1].getMessage('masterGroup')[0]
    
                    #Decompose matrix for parent...
                    if upMode == 'matrix':
                        mUpDecomp = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
                        mUpDecomp.doStore('cgmName',ml_handleParents[i])                
                        mUpDecomp.addAttr('cgmType','aimMatrix',attrType='string',lock=True)
                        mUpDecomp.doName()
        
                        ATTR.connect("%s.worldMatrix"%(ml_handleParents[i].mNode),"%s.%s"%(mUpDecomp.mNode,'inputMatrix'))
                        
                        _d_up = {'aimVector': _aim,
                                 'upVector': _out,
                                 'worldUpObject': ml_handleParents[i].mNode,
                                 'worldUpType': 'vector',
                                 'worldUpVector': [0,0,0]}
                    else:
                        _d_up = {'aimVector': _aim,
                                 'upVector': _out,
                                 'worldUpObject': ml_handleParents[i].mNode,
                                 'worldUpType': 'objectRotation',
                                 'worldUpVector': [1,0,0]}

    
                    if s_targetForward:
                        mAimForward = mHandle.doCreateAt()
                        mAimForward.parent = mMasterGroup            
                        mAimForward.doStore('cgmTypeModifier','forward')
                        mAimForward.doStore('cgmType','aimer')
                        mAimForward.doName()
    
                        _const=mc.aimConstraint(s_targetForward, mAimForward.mNode, maintainOffset = True, 
                                                **_d_up)            
                        
                        
                        
                        s_targetForward = mAimForward.mNode
                        if upMode == 'matrix':
                            ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                 
    
                    else:
                        s_targetForward = ml_handleParents[i].mNode
    
                    if s_targetBack:
                        mAimBack = mHandle.doCreateAt()
                        mAimBack.parent = mMasterGroup                        
                        mAimBack.doStore('cgmTypeModifier','back')
                        mAimBack.doStore('cgmType','aimer')
                        mAimBack.doName()
                        
                        _d_up['aimVector'] = _aimNeg
                                                
    
                        _const = mc.aimConstraint(s_targetBack, mAimBack.mNode, maintainOffset = True,
                                                  **_d_up)  
                        s_targetBack = mAimBack.mNode
                        
                        if upMode == 'matrix':
                            ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                                     
                    else:
                        s_targetBack = s_rootTarget
                        #ml_handleParents[i].mNode
    
                    #pprint.pprint([s_targetForward,s_targetBack])
                    mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
    
                    mHandle.parent = False
    
                    if b_first:
                        const = mc.orientConstraint([s_targetBack, s_targetForward], mAimGroup.mNode, maintainOffset = True)[0]
                    else:
                        const = mc.orientConstraint([s_targetForward, s_targetBack], mAimGroup.mNode, maintainOffset = True)[0]
    
    
                    d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mHandle.mNode,'followRoot'],
                                                                         [mHandle.mNode,'resultRootFollow'],
                                                                         [mHandle.mNode,'resultAimFollow'],
                                                                         keyable=True)
                    targetWeights = mc.orientConstraint(const,q=True, weightAliasList=True,maintainOffset=True)
    
                    #Connect                                  
                    d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                    d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                    d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                    d_blendReturn['d_result2']['mi_plug'].p_hidden = True
    
                    mHandle.parent = mAimGroup#...parent back
    
    
            else:
                log.debug("|{0}| >> reg handles...".format(_str_func))
                for i,mHandle in enumerate(ml_handles):
                    mHandle.masterGroup.parent = ml_handleParents[i]
                    s_rootTarget = False
                    s_targetForward = False
                    s_targetBack = False
                    mMasterGroup = mHandle.masterGroup
                    b_first = False
                    if mHandle == ml_handles[0]:
                        log.debug("|{0}| >> First handle: {1}".format(_str_func,mHandle))
                        if len(ml_handles) <=2:
                            s_targetForward = ml_handleParents[-1].mNode
                        else:
                            s_targetForward = ml_handles[i+1].getMessage('masterGroup')[0]
                            
                        #s_rootTarget = ml_handleParents[0].mNode#mRoot.mNode
                        mRootDriver = mHandle.doCreateAt()
                        mRootDriver.parent = mMasterGroup                        
                        mRootDriver.doStore('cgmTypeModifier','root')
                        mRootDriver.doStore('cgmType','driver')
                        mRootDriver.doName()
                        
                        mc.orientConstraint([mRoot.mNode], mRootDriver.mNode, maintainOffset = True)
                        
                        s_rootTarget = mRootDriver.mNode
                        
                        
                        b_first = True
    
                    elif mHandle == ml_handles[-1]:
                        log.debug("|{0}| >> Last handle: {1}".format(_str_func,mHandle))
                        s_rootTarget = ml_handleParents[i].mNode                
                        s_targetBack = ml_handles[i-1].getMessage('masterGroup')[0]
                    else:
                        log.debug("|{0}| >> Reg handle: {1}".format(_str_func,mHandle))            
                        s_targetForward = ml_handles[i+1].getMessage('masterGroup')[0]
                        s_targetBack = ml_handles[i-1].getMessage('masterGroup')[0]
    
                    #Decompose matrix for parent...
                    mUpDecomp = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
                    mUpDecomp.doStore('cgmName',ml_handleParents[i])                
                    mUpDecomp.addAttr('cgmType','aimMatrix',attrType='string',lock=True)
                    mUpDecomp.doName()
    
                    ATTR.connect("%s.worldMatrix"%(ml_handleParents[i].mNode),"%s.%s"%(mUpDecomp.mNode,'inputMatrix'))
    
                    if s_targetForward:
                        mAimForward = mHandle.doCreateAt()
                        mAimForward.parent = mMasterGroup            
                        mAimForward.doStore('cgmTypeModifier','forward')
                        mAimForward.doStore('cgmType','aimer')
                        mAimForward.doName()
    
                        _const=mc.aimConstraint(s_targetForward, mAimForward.mNode, maintainOffset = True, #skip = 'z',
                                                aimVector = _aim, upVector = _out, worldUpObject = ml_handleParents[i].mNode,
                                                worldUpType = 'vector', worldUpVector = [0,0,0])            
                        s_targetForward = mAimForward.mNode
                        ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                 
    
                    else:
                        s_targetForward = ml_handleParents[i].mNode
    
                    if s_targetBack:
                        mAimBack = mHandle.doCreateAt()
                        mAimBack.parent = mMasterGroup                        
                        mAimBack.doStore('cgmTypeModifier','back')
                        mAimBack.doStore('cgmType','aimer')
                        mAimBack.doName()
    
                        _const = mc.aimConstraint(s_targetBack, mAimBack.mNode, maintainOffset = True, #skip = 'z',
                                                  aimVector = _aimNeg, upVector = _out, worldUpObject = ml_handleParents[i].mNode,
                                                  worldUpType = 'vector', worldUpVector = [0,0,0])  
                        s_targetBack = mAimBack.mNode
                        ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                                     
                    else:
                        s_targetBack = s_rootTarget
                        #ml_handleParents[i].mNode
    
                    #pprint.pprint([s_targetForward,s_targetBack])
                    mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
    
                    mHandle.parent = False
    
                    if b_first:
                        const = mc.orientConstraint([s_targetBack, s_targetForward], mAimGroup.mNode, maintainOffset = True)[0]
                    else:
                        const = mc.orientConstraint([s_targetForward, s_targetBack], mAimGroup.mNode, maintainOffset = True)[0]
    
    
                    d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mHandle.mNode,'followRoot'],
                                                                         [mHandle.mNode,'resultRootFollow'],
                                                                         [mHandle.mNode,'resultAimFollow'],
                                                                         keyable=True)
                    targetWeights = mc.orientConstraint(const,q=True, weightAliasList=True,maintainOffset=True)
    
                    #Connect                                  
                    d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                    d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                    d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                    d_blendReturn['d_result2']['mi_plug'].p_hidden = True
    
                    mHandle.parent = mAimGroup#...parent back

        for mHandle in ml_handles:
            if mHandle == ml_handles[0]:
                mHandle.followRoot = 0
                ATTR.set_default(mHandle.mNode,'followRoot',0)                
            elif mHandle == ml_handles[-1]:
                mHandle.followRoot = 1
                ATTR.set_default(mHandle.mNode,'followRoot',1.0)
            else:
                mHandle.followRoot = .5
                ATTR.set_default(mHandle.mNode,'followRoot',.5)
    

      
    except Exception as err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
    
    
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