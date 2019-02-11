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

def ik_rp(self,mStart,mEnd,ml_ikFrame = None,
          mIKControl=None,mIKControlBase = None,
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
            raise ValueError,"Must have mIKControl"
            
        if not mIKHandleDriver:
            raise ValueError,"Must have mIKHandleDriver"
        if not mRoot:
            raise ValueError,"Must have mRoot"
        
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
        reload(IK)
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
    
        if mIKControlBase:
            ml_distHandlesNF[0].parent = mIKControlBase
    
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
        #if mIKControlBase:
            #ml_ikFrame[0].parent = mRigNull.controlIKBase
    
        #if mIKControlBase:
            #mc.pointConstraint(mIKControlBase.mNode, ml_ikFrame[0].mNode,maintainOffset=True)
    
    
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
    
        if mIKControlBase:
            mc.pointConstraint(mIKControlBase.mNode, mSpinGroup.mNode,maintainOffset=True)
    
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
    
    
        if mIKControlBase:
            l_midDrivers = [mIKControlBase.mNode]
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
                                               ml_ikFrame[1].mNode],#ml_handleJoints[1]],
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
        
        if mIKControlBase:
            ml_ikFrame[0].parent = mIKControlBase
        #if mIKControlBase:
            #mc.pointConstraint(mIKControlBase.mNode, ml_ikFrame[0].mNode,maintainOffset=True)
            
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
            