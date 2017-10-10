import cgm.core.cgm_Meta as cgmMeta
import cgm.core.rigger.RigFactory as Rig
cgm.core._reload()

m1 = cgmMeta.asMeta('spine_part')

m1.rig_getSkinJoints()
m1.doRig()
m1.isRigged()
m1.doSkeletonize()
m1.rig_getSkinJoints(False)
m1.rig_getHandleJoints(False)
m1.rig_getRigHandleJoints(m1)
Rig.get_rigDeformationJoints(m1)
Rig.get_rigJointDriversDict(m1)
Rig.get_simpleRigJointDriverDict(m1)

import cgm.core.cgm_Meta as cgmMeta
import cgm.core.rigger.RigFactory as Rig
import maya.cmds as mc
import cgm.core.lib.attribute_utils as ATTR
for o in mc.ls(type='joint'):
    ATTR.set(o,'segmentScaleCompensate',1)

import maya.cmds as mc 

m1.rig_getRigHandleJoints(False)
m1.setState('skeleton',forceNew=True)
reload(Rig)
Rig.get_report(m1)
m1.rig_getHandleJoints()
m1.rigConnect()
m1.isRigged()
m1.isRigConnected()
m1.getState()
m1.rigDelete()
m1.doRig()
m1.rig_getSkinJoints()
reload(Rig)
m1 = cgmMeta.asMeta('r_leg_part')
m1.modulePuppet.masterControl
i_rig = Rig.go(m1,forceNew=False,autoBuild = True)#call to do general rig
i_rig = Rig.go(m1,forceNew=False,autoBuild = False)#call to do general rig
i_rig.doBuild('')
i_rig.build(i_rig,buildTo = '')
i_rig.isShaped()

#spine ------------------------------------------------------------------------
i_rig = Rig.go(m1,forceNew=False,autoBuild = True)#call to do general rig

m1 = cgmMeta.asMeta('spine_part')
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_deformation(i_rig)
i_rig.buildModule.build_rig(i_rig)
m1.rigConnect()


#neckhead ------------------------------------------------------------------------
m1 = cgmMeta.asMeta('neck_part')
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_deformation(i_rig)
i_rig.buildModule.build_rig(i_rig)

#Leg ------------------------------------------------------------------------
m1 = cgmMeta.asMeta('r_leg_part')
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_foot(i_rig)
i_rig.buildModule.build_FKIK(i_rig)
i_rig.buildModule.build_deformation(i_rig)
i_rig.buildModule.build_rig(i_rig)
i_rig.buildModule.build_matchSystem(i_rig)
i_rig.buildModule.build_twistDriver_hip(i_rig)
i_rig.buildModule.build_twistDriver_ankle(i_rig)


#arm ------------------------------------------------------------------------
m1 = cgmMeta.asMeta('l_arm_part')
i_rig = Rig.go(m1,forceNew=False,autoBuild = False)#call to do general rig
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_FKIK(i_rig)
i_rig.buildModule.build_deformation(i_rig)
i_rig.buildModule.build_rig(i_rig)
i_rig.buildModule.build_matchSystem(i_rig)
i_rig.buildModule.build_twistDriver_shoulder(i_rig)
i_rig.buildModule.build_twistDriver_wrist(i_rig)

#finger ------------------------------------------------------------------------
m1 = cgmMeta.asMeta('l_index_part')
i_rig = Rig.go(m1,forceNew=False,autoBuild = False)#call to do general rig
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_FKIK(i_rig)
i_rig.buildModule.build_rig(i_rig)
i_rig.buildModule.build_matchSystem(i_rig)

for m in 'l_clav_part', 'r_clav_part':
    m1 = cgmMeta.asMeta(m)
    Rig.go(m1,forceNew=False,autoBuild = True)#call to do general rig
    m1.rigConnect()  
        
for m in 'l_thumb_part','l_index_part','l_middle_part','l_ring_part','l_pinky_part','r_thumb_part','r_index_part','r_middle_part','r_ring_part','r_pinky_part':
    m1 = cgmMeta.asMeta(m)
    Rig.go(m1,forceNew=False,autoBuild = True)#call to do general rig
    m1.rigConnect()
    
#eye ------------------------------------------------------------------------
m1 = cgmMeta.asMeta('l_eye_part')
i_rig = Rig.go(m1,forceNew=False,autoBuild = False)#call to do general rig
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_rig(i_rig)
i_rig.buildModule.build_matchSystem(i_rig)

#eyelids ------------------------------------------------------------------------
m1 = cgmMeta.asMeta('l_eyelids_part')
i_rig = Rig.go(m1,forceNew=False,autoBuild = False)#call to do general rig
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_rig(i_rig)
i_rig.buildModule.build_matchSystem(i_rig)


#>>>Scratch...
m1.getMessage('rigNull',simple=False)
import cgm.core.cgm_RigMeta as cgmRigMeta
cgmRigMeta.cgmDynamicMatch(dynObject='l_knee_ik_anim',dynPrefix = "FKtoIK",dynMatchTargets='l_knee_blend_jnt') 
n1 = cgmRigMeta.cgmDynamicSwitch()
n1.addSwitch()
Rig.get_report(spine)
m1.doRig()
m1.rigDelete()
reload(Rig)
import cgm.core.lib.attribute_utils as ATTR
reload(ATTR)
m1 = cgmMeta.asMeta('l_leg_part')
ATTR.get_message('M1_puppetNetwork','masterControl',simple = True)
m1.modulePuppet.hasAttr('masterControl')
m1.modulePuppet.masterControl
m1.modulePuppet.getMessage('masterControl')
cgmMeta.asMeta('l_leg_rigNull_dynSwitchSystem').getMessage('dynStoredAttr_0',simple=False)

#ShapeCasting========================================================
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
reload(mShapeCast)
from cgm.core.lib import shapeCaster as ShapeCast
reload(ShapeCast)
mShapeCast.go(m1,l_toBuild)

m1 = cgmMeta.asMeta('l_arm_part')
mShapeCast.go(m1,['segmentFK_Loli'])
mShapeCast.go(m1,['settings'])
mShapeCast.go(m1,['midIK'])
mShapeCast.go(m1,['hand'])

#Issues========================================================
import cgm.core.cgmPy.validateArgs as VALID
reload(VALID)
VALID.is_transform('cgmObject_poly2_parentConstraint1')

mc.listAttr('cgmObject_poly2_parentConstraint1')

ATTR.set('cgmObject_poly2_parentConstraint1','ty',100)
ATTR.get('cgmObject_poly2_parentConstraint1','ty')


import cgm.core.lib.curve_Utils as CURVES
reload(CURVES)
import maya.cmds as mc
CURVES.mirror_worldSpace('l_eye_block|uprLid_rigHelper','r_eye_block|uprLid_rigHelper')
CURVES.mirror_worldSpace(mc.ls(sl=1)[0],mc.ls(sl=1)[1])

CURVES.Copy


eyeBlock = cgmMeta.asMeta('r_eyelids_part')
eyeBlock.doSkeletonize()

#Joints ==========================================================================
_l = mc.ls(sl=True, type='joint')
_good = []
for mObj in cgmMeta.validateObjListArg(_l):
    if mObj.hasAttr('scaleJoint'):
        continue
    _good.append(mObj.mNode)
mc.select(_good)


#>>.Fixes =======================================================================
for m in 'l_eyelids_part','r_eyelids_part':
    mMod = cgmMeta.asMeta(m)
    mMod.helper.uprLidJoints = 12
    mMod.helper.lwrLidJoints = 12
    #mMod.doDeleteSkeleton()
    mMod.doSkeletonize()
    
mHead = cgmMeta.cgmObject('head_jnt')
for mChild in mHead.getChildren(asMeta=True):
    mChild.parent = mHead.scaleJoint
    
for m in 'l_eye_part','l_eyelids_part','r_eye_part','r_eyelids_part':
    mMod = cgmMeta.asMeta(m)
    Rig.go(mMod,forceNew=False,autoBuild = True)#call to do general rig
    mMod.rigConnect()

for m in 'l_leg_part','r_leg_part':
    mMod = cgmMeta.asMeta(m)
    Rig.go(mMod,forceNew=False,autoBuild = True)#call to do general rig
    mMod.rigConnect()
    
for m in 'l_clav_part','l_arm_part','r_clav_part','r_arm_part':
    mMod = cgmMeta.asMeta(m)
    Rig.go(mMod,forceNew=False,autoBuild = True)#call to do general rig
    mMod.rigConnect()
    
    
#Name fixing...:(
#
#
[mObj.doName() for mObj in cgmMeta.asMeta(mc.ls(sl=1))]
    
#Optimization stuff ==============================================================================
#Trying parent change up
#Parent rig joints in deform null to constrain
for mod in ['l_clav_part','r_clav_part']:
    mMod = cgmMeta.asMeta(mod)
    mConstrain = mMod.constrainNull
    mTarget = mConstrain.getConstrainingObjects(asMeta=True)[0].rigJoint
    mc.delete(mConstrain.getConstraintsTo())
    mConstrain.parent = mTarget
    
    
    
#NEW STUFF =========================================================================================
import cgm.core.rig.segment_utils as SEGMENT
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.distance_utils as DIST


#Segment ------------------------------------------------------------------------------------------
SEGMENT.create

#Def ---------------------------------------
#Return change

i_curve = curveSegmentReturn['mSegmentCurve']

SEGMENT.add_subControl_toCurve

#Segment scale
ATTR.copy_to(i_curve.mNode,'segmentScaleMult',mi_cog.mNode,'squashStretch',driven='source')
ATTR.set_keyable(mi_cog.mNode,'squashStretch',False)

#MidFactor
l_keys = i_curve.getSequentialAttrDict('midFactor').keys()
for i,k in enumerate(l_keys):
    a = 'midFactor_{0}'.format(i)
    ATTR.copy_to(i_curve.mNode,a,ml_segmentHandles[1].mNode,driven='source')
    ATTR.set_keyable(ml_segmentHandles[1].mNode,a,False)
    if i == 1:
        ATTR.set(mi_handleIK.mNode,1)    
    

l_keys = i_curve.getSequentialAttrDict('scaleMult').keys()


#Segment joints parenting...
for mHandle in mi_segmentCurve.msgList_get('ikHandles',asMeta=True):
    ml_chain = mHandle.msgList_get('drivenJoints',asMeta=True)
    ml_chain[0].parent = mi_cog

#Rig....
mi_distanceBuffer = mi_segmentCurve

#NewDynParent --------------------------------------------------------------------------------------
ml_shoulderDynParents.append(mi_go._i_puppet.masterNull.puppetSpaceObjectsGroup)   
ml_shoulderDynParents.append(mi_go._i_puppet.masterNull.worldSpaceObjectsGroup)  

#Uneeded...
#mi_go.collect_worldDynDrivers()

No more spline segment
#ml_segmentSplineJoints = mi_segmentCurve.msgList_get('driverJoints',asMeta = True)

#Twist driver distances

ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')
fl_baseDist = DIST.get_distance_between_points(ml_blendJoints[0].p_position, ml_blendJoints[-1].p_position)



import cgm.core.lib.attribute_utils as ATTR
for o in mc.ls(type='joint'):
    ATTR.set(o,'segmentScaleCompensate',0)
    
    
ATTR.set_default('l_glove_upr_pinky_end_jnt','tz', ATTR.get('l_glove_upr_pinky_end_jnt','tz'))



for o in mc.ls(sl=True):
    mc.rename(o,o.replace('__','_'))

import cgm.core.cgm_Meta as cgmMeta    
import cgm.core.lib.rigging_utils as RIGGING
ml = cgmMeta.validateObjListArg(mc.ls(sl=1))
for mObj in ml:
    _source = mObj.getMessage('cgmSource')
    RIGGING.shapeParent_in_place(_source[0],mObj.mNode,False)
    cgmMeta.asMeta(_source).doGroup(True)
    
    
import cgm.core.rig.joint_utils as JOINTS
ml = cgmMeta.validateObjListArg(mc.ls(sl=1))
_p = []
for mObj in ml:
    _p.append(mObj.parent)
    mObj.parent = False
for mObj in ml:
    mObj.rx = 90
    mObj.rz = 180
    JOINTS.freezeOrientation(mObj)
for i,mObj in enumerate(ml):
    mObj.parent = _p[i]
    
    
#Control shape parent tassels
import cgm.core.cgm_Meta as cgmMeta    
import cgm.core.lib.rigging_utils as RIGGING
import cgm.core.lib.attribute_utils as ATTR
import maya.cmds as mc
ml = cgmMeta.validateObjListArg(mc.ls(sl=1))
for mObj in ml:
    _source = mObj.getMessage('cgmSource')
    RIGGING.shapeParent_in_place(_source[0],mObj.mNode,False)
    mSource = cgmMeta.asMeta(_source[0])
    mSource.doGroup(True)
    mSource.radius = 0
    ATTR.set_hidden(mSource.mNode,'cgmIterator')
    
def reorderUnderParent():
    ml = cgmMeta.validateObjListArg(mc.ls(sl=1))
    for mObj in ml:
        p = mObj.parent
        mObj.parent = False
        mObj.parent = p
        
        
#Face ==============================================================================================================
_d = {'jointList' : [u'tongue_0_jnt',
                     u'tongue_1_jnt',
                     u'tongue_2_jnt',
                     u'tongue_3_jnt',
                     u'tongue_4_jnt',
                     u'tongue_5_jnt'],
      'useCurve' : None,
      'baseName' : 'test',
      'stretchBy' : 'scale',
      'advancedTwistSetup' : False,
      'addMidTwist' : False,
      'extendTwistToEnd':False,
      'moduleInstance' : None,
      'reorient' : False}

import cgm.core.rig.segment_utils as SEGMENT
reload(SEGMENT)
SEGMENT.create_curveSetup(**_d)


import cgm.core.rig.joint_utils as JOINTS
JOINTS.orientChain(mc.ls(sl=1))


#Beard attach
import cgm.core.lib.surface_Utils as SURF
reload(SURF)
_d = {'objToAttach':'beardTubeA1',
      'targetSurface':'body_REN',
      'createControlLoc': False,
      'createUpLoc':False,
      'pointAttach':False,
      'parentToFollowGroup':True,
      'attachControlLoc':False,
      'f_offset':1.0}

SURF.attachObjToSurface(**_d)


import cgm.core.lib.surface_Utils as SURF
reload(SURF)
_d = {'objToAttach':'beardTubeA1',
      'targetSurface':'geometry_GRP|body_GRP|body_REN',
      'createControlLoc': False,
      'createUpLoc':False,
      'pointAttach':False,
      'parentToFollowGroup':True,
      'attachControlLoc':False,
      'f_offset':1.0}

SURF.simple_surfaceAttach(mc.ls(sl=True)[0],'geometry_GRP|body_GRP|body_REN','pointGroup')

for o in mc.ls(sl=True):
    SURF.simple_surfaceAttach(o,'geometry_GRP|body_GRP|body_REN','pointGroup')

SURF.attachObjToSurface(**_d)

import cgm.core.lib.distance_utils as DIST
reload(DIST)
DIST.get_closest_point_data_from_mesh('geometry_GRP|body_GRP|body_REN','beardTubeA1')

import cgm.core.cgm_Meta as cgmMeta
mc.select(mc.ls(type='joint'))
for o in mc.ls(sl=True):
    mObj = cgmMeta.asMeta(o)
    mObj.doStore('cgmName',mObj.p_nameBase)
    mObj.doName()

                        
                        
                    
// Warning: line 0: Unrecognized node type for node 'mentalrayItemsList'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'mentalrayGlobals'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'miDefaultOptions'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'miDefaultFramebuffer'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'miContourPreset'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'Draft'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'DraftMotionBlur'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'DraftRapidMotion'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'Preview'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'PreviewMotionblur'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'PreviewRapidMotion'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'PreviewCaustics'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'PreviewGlobalIllum'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'PreviewFinalGather'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'Production'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'ProductionMotionblur'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'ProductionRapidMotion'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'ProductionFineTrace'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'ProductionRapidFur'; preserving node information during this session. // 
// Warning: line 0: Unrecognized node type for node 'ProductionRapidHair'; preserv


#Finger unlock -----------------------------------------------------------------
import cgm.core.cgm_Meta as cgmMeta
import cgm.core.lib.attribute_utils as ATTR
import maya.cmds as mc
for m in 'l_thumb_part','l_index_part','l_middle_part','l_ring_part','l_pinky_part','r_thumb_part','r_index_part','r_middle_part','r_ring_part','r_pinky_part':
    m1 = cgmMeta.asMeta(m)
    ml_blend = m1.rigNull.msgList_get('blendJoints')
    ml_fk = m1.rigNull.msgList_get('fkJoints')
    ml_ik = m1.rigNull.msgList_get('ikJoints')
    
    for mJnt in ml_fk:
        ATTR.set_standardFlags(mJnt.mNode,visible=True,keyable=True,lock=False)
        try:ATTR.break_connection(mJnt.mNode,'translateZ')
        except:pass
        
    for i,mJnt in enumerate(ml_blend):
        mJnt.segmentScaleCompensate = False
        ATTR.set_standardFlags(mJnt.mNode,['scale'],visible=True,keyable=True,lock=False)
        mc.scaleConstraint([ml_fk[i].mNode], mJnt.mNode)
        
    
m1 = cgmMeta.asMeta('l_thumb_part')

#Tassel control simplification --------------------------------------------------
import cgm.core.lib.transform_utils as TRANS
sel = mc.ls(sl=True)
import cgm.core.lib.math_utils as MATH
for i,o in enumerate(sel):
    if not i%2==0:#if not even
        mObj = cgmMeta.asMeta(o)
        mc.delete(mc.listRelatives(o,shapes=True))
        mObj.doConnectIn('rotate',"{0}.rotate".format(sel[i-1]))
        
        
for o in mc.ls(sl=True):
    mObj = cgmMeta.asMeta(o)
    _m = self.p_nameBase
    _m.replace('l_','r_')
    mMirror = cgmMeta.asMeta(_m.replace('l_','r_'))
    mObj.translate = mMirror.translate
    
for m in 'l_thumb_part','l_index_part','l_middle_part','l_ring_part','l_pinky_part','r_thumb_part','r_index_part','r_middle_part','r_ring_part','r_pinky_part':
    m1 = cgmMeta.asMeta(m)
    ml_fk = m1.rigNull.msgList_get('fkJoints')
    for mJnt in ml_fk[1:]:
        mJnt.doGroup(True)
        
#Simple Lip --------------------------------------------------
import cgm.core.lib.curve_Utils as CURVES
CURVES.returnSplitCurveList('curve5',8,markPoints=True)



_d = {'jointList' : [u'l_uprLip_0_jnt',
                     u'l_uprLip_1_jnt',
                     u'l_uprLip_2_jnt',
                     u'l_uprLip_3_jnt',
                     u'l_uprLip_4_jnt',
                     u'l_uprLip_5_jnt',
                     u'center_uprLip_jnt',
                     u'r_uprLip_5_jnt',
                     u'r_uprLip_4_jnt',
                     u'r_uprLip_3_jnt',
                     u'r_uprLip_2_jnt',
                     u'r_uprLip_1_jnt',
                     u'r_uprLip_0_jnt'],
      'useCurve' : 'uprLip_CRV',
      'baseName' : 'uprLipSegment',
      'stretchBy' : 'scale',
      'advancedTwistSetup' : False,
      'addMidTwist' : True,
      'extendTwistToEnd':False,
      'moduleInstance' : None,
      'reorient' : False}

_d = {'jointList' : [u'l_lwrLip_0_jnt',
                     u'l_lwrLip_1_jnt',
                     u'l_lwrLip_2_jnt',
                     u'l_lwrLip_3_jnt',
                     u'l_lwrLip_4_jnt',
                     u'l_lwrLip_5_jnt',
                     u'centter_lwrLip_jnt',
                     u'r_lwrLip_5_jnt',
                     u'r_lwrLip_4_jnt',
                     u'r_lwrLip_3_jnt',
                     u'r_lwrLip_2_jnt',
                     u'r_lwrLip_1_jnt',
                     u'r_lwrLip_0_jnt'],
      'useCurve' : 'lwrLip_CRV',
      'baseName' : 'lwrLipSegment',
      'stretchBy' : 'scale',
      'advancedTwistSetup' : False,
      'addMidTwist' : False,
      'extendTwistToEnd':False,
      'moduleInstance' : None,
      'reorient' : False}

_d = {'jointList' : [u'l_lwrLip_0_jnt',
                     u'l_lwrLip_1_jnt',
                     u'l_lwrLip_2_jnt',
                     u'l_lwrLip_3_jnt',
                     u'l_lwrLip_4_jnt',
                     u'l_lwrLip_5_jnt'],
      'useCurve' : 'l_lwrLip_CRV',
      'baseName' : 'l_lwrLipSegment',
      'stretchBy' : 'scale',
      'advancedTwistSetup' : False,
      'addMidTwist' : False,
      'extendTwistToEnd':False,
      'moduleInstance' : None,
      'reorient' : False}
_d = {'jointList' : [u'r_lwrLip_0_jnt',
                     u'r_lwrLip_1_jnt',
                     u'r_lwrLip_2_jnt',
                     u'r_lwrLip_3_jnt',
                     u'r_lwrLip_4_jnt',
                     u'r_lwrLip_5_jnt'],
      'useCurve' : 'r_lwrLip_CRV',
      'baseName' : 'r_lwrLipSegment',
      'stretchBy' : 'scale',
      'advancedTwistSetup' : False,
      'addMidTwist' : False,
      'extendTwistToEnd':False,
      'moduleInstance' : None,
      'reorient' : False}


import cgm.core.rig.segment_utils as SEGMENT
reload(SEGMENT)
SEGMENT.create_curveSetup(**_d)


#....making armor follow segment...
import cgm.core.cgm_Meta as cgmMeta
import cgm.core.lib.attribute_utils as ATTR
import maya.cmds as mc
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.rigging_utils as RIG
for mObj in cgmMeta.validateObjListArg(mc.ls(sl=True)):
    mDup = mObj.doDuplicate(po=True, ic=False)
    #RIG.create_at(mObj.mNode,'joint')
    mDup.parent = mObj
    mDup.segmentScaleCompensate = 0
    mDup.doStore('cgmTypeModifier','armor')
    mDup.doName()
    mDup.setAttrFlags(['scale'],lock=False)
    #ATTR.set(mDup.mNode,'segmentScaleCompensate',0)
    

#Clean up...
#Scale driver - 
import cgm.core.classes.NodeFactory as NODEF
arg = "tongue_splineIKCurve.masterScale = head_ik_anim.sy * MasterControl_masterAnim.masterScale"
NODEF.argsToNodes(arg).doBuild()
_crvs = [u'r_uprLip_CRV_splineIKCurve',
         u'r_lwrLip_CRV_splineIKCurve',
         u'l_uprLip_CRV_splineIKCurve',
         u'l_lwrLip_CRV_splineIKCurve']
for crv in _crvs:
    arg = "{0}.masterScale = head_ik_anim.sy * MasterControl_masterAnim.masterScale".format(crv)
    NODEF.argsToNodes(arg).doBuild()
    
    
#RENAME -------------------------------------------------------------------------
#def sceneCleanBrazen():
ml_joints = cgmMeta.validateObjListArg(mc.ls(type='joint'))
for mJnt in ml_joints:
    if not mJnt.getShapes():
        if mJnt.p_nameShort.endswith('jnt'):
            mJnt.rename(mJnt.p_nameBase.replace('jnt','JNT'))
            #print (mJnt.p_nameBase + '>>' + mJnt.p_nameBase.replace('jnt','JNT'))
        else:
            mJnt.rename(mJnt.p_nameBase + '_JNT')
            #print (mJnt.p_nameBase + '>>' + mJnt.p_nameBase + '_JNT')
    

cgmMeta.cgmNode('DragonLord_animSet').select()
ml_CON = cgmMeta.validateObjListArg(mc.ls(sl=1))
for mCon in ml_CON:
    if cgmMeta.VALID.is_transform(mCon.mNode):
        if mCon.p_nameShort.endswith('_anim'):
            #mCon.rename(mCon.p_nameBase.replace('anim','CON'))
            print (mCon.p_nameBase + '>>' + mCon.p_nameBase.replace('anim','CON'))        
        elif mCon.p_nameShort.endswith('_jnt'):
            #mCon.rename(mCon.p_nameBase.replace('jnt','CON'))
            print (mCon.p_nameBase + '>>' + mCon.p_nameBase.replace('jnt','CON'))          
        else:
            print ('>>> ????? ' + mCon.p_nameBase)
#l/r
ml_trans = cgmMeta.validateObjListArg(mc.ls(type='transform'))
for mObj in ml_trans:
    _new = mObj.p_nameBase    
    if _new.startswith('l_'):
        #mObj.rename(mObj.p_nameBase.replace('l_','L_'))
        _new = list(_new)
        _new[0] = 'L'
        _new = ''.join(_new)
        print (mObj.p_nameBase + '>>' + _new)
        mObj.rename(_new)
        continue
    elif _new.startswith('r_'):
        _new = list(_new)        
        _new[0] = 'R'
        _new = ''.join(_new)        
        #mObj.rename(mObj.p_nameBase.replace('r_','R_'))
        print (mObj.p_nameBase + '>>' + _new)
        mObj.rename(_new)        
        continue
    elif _new.count('_l_'):
        _new = _new.replace('_l_','_L_')
        print (mObj.p_nameBase + '>>' + _new)
        mObj.rename(_new)        
        continue 
    elif _new.count('_r_'):
        _new = _new.replace('_r_','_R_')
        print (mObj.p_nameBase + '>>' + _new)
        mObj.rename(_new)        
        continue
    elif _new.count('right_'):
        _new = _new.replace('right_','R_')
        print (mObj.p_nameBase + '>>' + _new)
        mObj.rename(_new)
        continue  
    elif _new.count('left_'):
        _new = _new.replace('left_','L_')
        print (mObj.p_nameBase + '>>' + _new)
        mObj.rename(_new)        
        continue 
    elif _new.count('jnt'):
        _new = _new.replace('jnt','JNT')
        print (mObj.p_nameBase + '>>' + _new)
        mObj.rename(_new)                
        continue
    elif _new.count('grp'):
        _new = _new.replace('grp','GRP')
        print (mObj.p_nameBase + '>>' + _new)
        mObj.rename(_new)                        
        continue
    #else:
       # print ('>>> ????? ' + mObj.p_nameBase)
        #print (mJnt.p_nameBase + '>>' + mJnt.p_nameBase + '_JNT')

import cgm.lib.skinning as legSKIN
legSKIN.skinMeshFromMesh


for skin in mc.ls(type='skinCluster'):
    _shape = mc.skinCluster(skin, q=1,g=True)[0]
    mSkin = cgmMeta.cgmNode(skin)
    mShape = cgmMeta.cgmNode(_shape)
    mTrans = mShape.getTransform(True)
    mSkin.rename(mTrans.p_nameBase + '_SKIN')
    
    
    left_arm_settings_animShape.u[168367970969986]
    [8.549035523202997, 70.81442180792435, -1.0244357673943685]
    [8.549035523202997, 70.81442180792435, -1.0244357673943685]
    # Result: [8.549035523202997, 70.81442180792435, -1.0244357673943685] # 
    _obj
    Result: left_arm_settings_animShape.u[1.68367970969986] #     