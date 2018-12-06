import cgm.core.cgm_Meta as cgmMeta
cgmMeta.core._reload()
import cgm.core.lib.attribute_utils as ATTR
import maya.cmds as mc

#===================================================================================================
# >> AbyssCrabLarge
#===================================================================================================
import cgm.projects.specpl as SPECTRA
reload(SPECTRA)

mObjs = cgmMeta.validateObjListArg(mc.ls(sl=1))
for i,mObj in enumerate(mObjs):
    if i < 9:
        _v = "0{0}".format(i+1)
    else:
        _v = "{0}".format(i+1)
    mObj.rename("tail_{0}_segHandle".format(_v))
    
SPECTRA.createAndContrainRigFromSkinJoints(mc.ls(sl=True))
import cgm.core.rig.ik_utils as IK
_d = {'jointList':[u'tail_01_rig',
                   u'tail_02_rig',
                   u'tail_03_rig',
                   u'tail_04_rig',
                   u'tail_05_rig',
                   u'tail_06_rig',
                   u'tail_07_rig',
                   u'tail_08_rig',
                   u'tail_09_rig',
                   u'tail_10_rig']}
reload(IK)
IK.ribbon(**_d)

#===================================================================================================
# >> Guardian fix
#===================================================================================================
import cgm.core.classes.NodeFactory as NODEF
arg = "neck1_c.rx = clamp(0,head.maxRoll, head.rx)"
NODEF.argsToNodes(arg).doBuild()





#===================================================================================================
# >> Abyss work
#===================================================================================================
def renameFinger(base = 'thumb',direction = 'l',tag = 'sknj'):
    import cgm.core.cgm_Meta as cgmMeta
    import maya.cmds as mc
    ml = cgmMeta.validateObjListArg(mc.ls(sl=1))
    for i,mObj in enumerate(ml):
        mObj.rename("{0}_{1}_{2}_{3}".format(base,direction,i,tag))
        
        
#>>Arms.....

import cgm.core.rig.joint_utils as JOINTS
reload(JOINTS)

JOINTS.orientChain(mc.ls(sl=1), worldUpAxis=[0,1,0])

ml_joints = cgmMeta.validateObjListArg(mc.ls(type='joint'))
for mJnt in ml_joints:
    if not mJnt.getShapes():
        mJnt.rename(mJnt.p_nameBase.replace('blend','fk'))
        
        
import cgm.projects.specpl as SPECTRA
reload(SPECTRA)

d_l = {'fkJoints':[u'l_shoulder_fk', u'l_elbow_fk', u'l_wrist_fk'],
       'ikJoints':[u'l_shoulder_ik', u'l_elbow_ik', u'l_wrist_ik'],
       'blendJoints':[u'l_shoulder_blend', u'l_elbow_blend', u'l_wrist_blend'],
       'settings':'l_arm_root',
       'orientation':'xyz',
       'fkGroup':'l_arm_fk_grp',
       'ikGroup':'l_arm_ik_grp',        
       'ikControl':'l_arm_IK_anim',
       'mirrorDirection' : 'Left',        
       'globalScalePlug' : 'Master_master_anim.scaleY',
       'ikMid':'l_elbow_pole'}
SPECTRA.buildFKIK(**d_l)

d_r = {'fkJoints':[u'r_shoulder_fk', u'r_elbow_fk', u'r_wrist_fk'],
       'ikJoints':[u'r_shoulder_ik', u'r_elbow_ik', u'r_wrist_ik'],
       'blendJoints':[u'r_shoulder_blend', u'r_elbow_blend', u'r_wrist_blend'],
       'orientation':'xyz',
       'settings':'r_arm_root',
       'fkGroup':'r_arm_fk_grp',
       'ikGroup':'r_arm_ik_grp',        
       'ikControl':'r_arm_IK_anim',
       'mirrorDirection' : 'Right',        
       'globalScalePlug' : 'Master_master_anim.scaleY',
       'ikMid':'r_elbow_pole'}
SPECTRA.buildFKIK(**d_r)

ml_joints = cgmMeta.validateObjListArg(mc.ls(sl=1))
for mJnt in ml_joints:
    mJnt.rename(mJnt.p_nameBase + '_seg')
    
reload(SPECTRA)
import maya.cmds as mc
mc.ls(sl=True)
cgmMeta.validateObjListArg(mc.ls(sl=1))
SPECTRA.createAndContrainRigFromSkinJoints(mc.ls(sl=True))
SPECTRA.create_lengthSetup(mc.ls(sl=True))
SPECTRA.setup_fingers(mc.ls(sl=True))
SPECTRA.setup_linearSegment(mc.ls(sl=True))

#...arms...
_dshoulderTwist_l = {'blendJoints':[u'l_shoulder_blend', u'l_elbow_blend', u'l_wrist_blend'],
                     'settings':'l_arm_root',
                     'segmentHandle':'l_elbow_direct',
                     'rootGroup':'Arm_l_grp',
                     'baseName':'l_arm'}
_dshoulderTwist_r = {'blendJoints':[u'r_shoulder_blend', u'r_elbow_blend', u'r_wrist_blend'],
                     'settings':'r_arm_root',
                     'segmentHandle':'r_elbow_direct',
                     'rootGroup':'Arm_r_grp',
                     'baseName':'r_arm'}
SPECTRA.shoulderTwist(**_dshoulderTwist_l)

import cgm.core.classes.NodeFactory as NODEF
NODEF.createSingleBlendNetwork('l_arm_root.stableShoulder',
                               'l_shoulder_rig_orientConstraint1.l_shoulder_rig_stable_aimW0',   
                               'l_shoulder_rig_orientConstraint1.l_shoulder_rig_follow_aimW1',                            
                               maxValue=1, 
                               minValue=0)


#...Legs -----------------------------------------------------------------------
d_l_front = {'fkJoints':[u'l_front_hip_fk', u'l_front_knee_fk', u'l_front_ankle_fk'],
             'ikJoints':[u'l_front_hip_ik', u'l_front_knee_ik', u'l_front_ankle_ik'],
             'blendJoints':[u'l_front_hip_blend', u'l_front_knee_blend', u'l_front_ankle_blend'],
             'settings':'l_front_leg_root',
             'orientation':'xyz',
             'fkGroup':'l_front_leg_fk_grp',
             'ikGroup':'l_front_leg_ik_grp',        
             'ikControl':'l_front_foot_ik_anim',
             'mirrorDirection' : 'Left',        
             'globalScalePlug' : 'Master_master_anim.scaleY',
             'ikMid':'l_front_knee_pole'}
d_r_front = {'fkJoints':[u'r_front_hip_fk', u'r_front_knee_fk', u'r_front_ankle_fk'],
             'ikJoints':[u'r_front_hip_ik', u'r_front_knee_ik', u'r_front_ankle_ik'],
             'blendJoints':[u'r_front_hip_blend', u'r_front_knee_blend', u'r_front_ankle_blend'],
             'settings':'r_front_leg_root',
             'orientation':'xyz',
             'fkGroup':'r_front_leg_fk_grp',
             'ikGroup':'r_front_leg_ik_grp',        
             'ikControl':'r_front_foot_ik_anim',
             'mirrorDirection' : 'Left',        
             'globalScalePlug' : 'Master_master_anim.scaleY',
             'ikMid':'r_front_knee_pole'}
d_l_back = {'fkJoints':[u'l_back_hip_fk', u'l_back_knee_fk', u'l_back_ankle_fk'],
             'ikJoints':[u'l_back_hip_ik', u'l_back_knee_ik', u'l_back_ankle_ik'],
             'blendJoints':[u'l_back_hip_blend', u'l_back_knee_blend', u'l_back_ankle_blend'],
             'settings':'l_back_leg_root',
             'orientation':'xyz',
             'fkGroup':'l_back_leg_fk_grp',
             'ikGroup':'l_back_leg_ik_grp',        
             'ikControl':'l_back_foot_ik_anim',
             'mirrorDirection' : 'Left',        
             'globalScalePlug' : 'Master_master_anim.scaleY',
             'ikMid':'l_back_knee_pole'}
d_r_back = {'fkJoints':[u'r_back_hip_fk', u'r_back_knee_fk', u'r_back_ankle_fk'],
             'ikJoints':[u'r_back_hip_ik', u'r_back_knee_ik', u'r_back_ankle_ik'],
             'blendJoints':[u'r_back_hip_blend', u'r_back_knee_blend', u'r_back_ankle_blend'],
             'settings':'r_back_leg_root',
             'orientation':'xyz',
             'fkGroup':'r_back_leg_fk_grp',
             'ikGroup':'r_back_leg_ik_grp',        
             'ikControl':'r_back_foot_ik_anim',
             'mirrorDirection' : 'Right',        
             'globalScalePlug' : 'Master_master_anim.scaleY',
             'ikMid':'r_back_knee_pole'}


SPECTRA.buildFKIK(**d_l)
SPECTRA.create_lengthSetup(mc.ls(sl=True))
SPECTRA.createAndContrainRigFromSkinJoints(mc.ls(sl=True))
SPECTRA.setup_linearSegment(mc.ls(sl=True))
reload(SPECTRA)
SPECTRA.setup_footPivots(**SPECTRA.d_footTest)

#Feet... ------------------------------------------------------------------------------------------------
d_foot_r_front = {'pivotToe' : 'r_front_toe_pivot',
                  'pivotHeel' : 'r_front_heel_pivot',
                  'pivotBall' : 'r_front_ball_pivot',
                  'pivotInner' : 'r_front_inr_pivot',
                  'pivotOutr' : 'r_front_outr_pivot',
                  'pivotBall' : 'r_front_ball_pivot',
                  #pivotBallWiggle : None,
                  #jointBall : None,
                  'direction':'right',
                  'orientation' : 'xyz',
                  'controlIK' : 'r_front_foot_ik_anim',
                  'ikHandle':'r_front_foot_ik_anim|ikChain_PV_ikH',
                  'jointIKBall':'r_front_ball_ik',
                  'jointIKHeel':'r_front_heel_ik',
                  'baseName':'right_front'} 
d_foot_l_back = {'pivotToe' : 'l_back_toe_pivot',
                 'pivotHeel' : 'l_back_heel_pivot',
                 'pivotBall' : 'l_back_ball_pivot',
                 'pivotInner' : 'l_back_inr_pivot',
                 'pivotOutr' : 'l_back_outr_pivot',
                 'pivotBall' : 'l_back_ball_pivot',
                 #pivotBallWiggle : None,
                 #jointBall : None,
                 'direction':'left',
                 'orientation' : 'xyz',
                 'controlIK' : 'l_back_foot_ik_anim',
                 'ikHandle':'l_back_foot_ik_anim|ikChain_PV_ikH',
                 'jointIKBall':'l_back_ball_ik',
                 'jointIKHeel':'l_back_heel_ik',
                 'baseName':'left_back'} 
d_foot_r_back = {'pivotToe' : 'r_back_toe_pivot',
                 'pivotHeel' : 'r_back_heel_pivot',
                 'pivotBall' : 'r_back_ball_pivot',
                 'pivotInner' : 'r_back_inr_pivot',
                 'pivotOutr' : 'r_back_outr_pivot',
                 'pivotBall' : 'r_back_ball_pivot',
                 #pivotBallWiggle : None,
                 #jointBall : None,
                 'direction':'right',
                 'orientation' : 'xyz',
                 'controlIK' : 'r_back_foot_ik_anim',
                 'ikHandle':'r_back_foot_ik_anim|ikChain_PV_ikH',
                 'jointIKBall':'r_back_ball_ik',
                 'jointIKHeel':'r_back_heel_ik',
                 'baseName':'right_back'}          
SPECTRA.setup_footPivots(**d_foot_r_front)

#===================================================================================================
# >> Native work
#===================================================================================================
#Need call to buffer 
import cgm.core.lib.skinDat as SKINDAT
SKINDAT.data(targetMesh = mObj.mNode, filepath=mFile).applySkin(influenceMode = 'target', nameMatch = True)

import cgm.core.lib.skinDat as SKINDAT
_dat = SKINDAT.data(targetMesh = 'Native02_game')
_dat.read()
_dat.applySkin(influenceMode = 'target', nameMatch = True)

#>>> Skirt controls
ml_joints = cgmMeta.validateObjListArg(mc.ls(sl=1))
for mJnt in ml_joints:
    mDup = mJnt.doDuplicate()
    mDup.connectParentNode(mJnt.mNode,'source','driver')
    mDup.rename(mDup.p_nameBase.replace('_sknj','_driver_jnt'))
    mDup.parent = False
    mc.pointConstraint(mDup.mNode, mJnt.mNode, maintainOffset = True)
    mc.orientConstraint(mDup.mNode, mJnt.mNode, maintainOffset = True)
    
import cgm.core.lib.rigging_utils as RIGGING    
for o in mc.ls(sl=True):
    mObj = cgmMeta.cgmObject(o)
    _bfr = mObj.getMessage('cgmSource')[0]
    RIGGING.shapeParent_in_place(_bfr, mObj.mNode, False)
    
import cgm.core.lib.attribute_utils as ATTR
for o in mc.ls('*sdk'):
    ATTR.set(o,'rotateOrder', 5)
    
#...picker groups
def setUpPickerGroups(control = None, atr = None, groups = []):
    import cgm.core.classes.NodeFactory as nodeF
    import cgm.core.cgm_Meta as cgmMeta
    import cgm.core.lib.attribute_utils as ATTR
    
    mGroups = cgmMeta.validateObjListArg(groups,'cgmObject')
    mControl = cgmMeta.validateObjArg(control,'cgmObject')
    
    ATTR.add(mControl.mNode,atr,'enum',enumOptions=[mObj.p_nameBase for mObj in mGroups])
    import cgm.core.classes.NodeFactory as nodeF    
    nodeF.build_conditionNetworkFromGroup(shortName, chooseAttr = i, controlObject = "{0}.{1}".format(mControl.mNode,atr))
    
    #for i,mGrp in enumerate(mGroups):
    #    shortName = mGrp.getShortName()
        #if log.getEffectiveLevel() == 10:log.debug(shortName)
        #Let's get basic info for a good attr name
        #d = nameTools.returnObjectGeneratedNameDict(shortName,ignore=['cgmTypeModifier','cgmType'])
        #n = nameTools.returnCombinedNameFromDict(d)
    #    nodeF.build_conditionNetworkFromGroup(shortName, chooseAttr = i, controlObject = "{0}.{1}".format(mControl.mNode,atr))
    return True

#===================================================================================================
# >> Constraints
#===================================================================================================
n1 = cgmMeta.cgmNode(mc.ls(sl=True)[0])

import cgm.core.lib.constraint_utils as CONSTRAINT
mc.select(CONSTRAINT.get_targets(mc.ls(sl=True)[0]))


_target = 'leg_front_l_IK_anim'
_grp = 'clavicle_front_l_grp'
mc.aimConstraint(_target,_grp,
                 maintainOffset = True,
                 aimVector = [1,0,0],
                 upVector = [0,1,0],
                 worldUpType = 'objectrotation',
                 worldUpVector = [0,1,0],
                 worldUpObject = 'COG_c_anim')


#Foot aimer
aim -z
objrotup
leg_front_l_IK_anim

axis - y

import cgm.core.classes.NodeFactory as NODEF
NODEF.argsToNodes(arg).doBuild()
_arg = "leg_front_l_pad_ikDriver.tz = -leg_front_l_IK_anim.raise"
NODEF.argsToNodes(_arg).doBuild()
#====================================================================================================
#>>>FK IK
#====================================================================================================
import cgm.core.rig.joint_utils as JOINTS
reload(JOINTS)

JOINTS.orientChain(mc.ls(sl=1), worldUpAxis=[0,1,0])

ml_joints = cgmMeta.validateObjListArg(mc.ls(type='joint'))
for mJnt in ml_joints:
    if not mJnt.getShapes():
        mJnt.rename(mJnt.p_nameBase.replace('blend','fk'))
        
        
import cgm.projects.specpl as SPECTRA
reload(SPECTRA)

SPECTRA.buildFKIK(**SPECTRA._d_l)

ml_joints = cgmMeta.validateObjListArg(mc.ls(sl=1))
for mJnt in ml_joints:
    mJnt.rename(mJnt.p_nameBase + '_seg')
    
    

#====================================================================================================
#>>> Segment
#====================================================================================================
_d = {'jointList' : [u'arm1_l2_seg',
                     u'arm2_l_seg',
                     u'arm3_l_seg',
                     u'arm4_l_seg',
                     u'arm5_l_seg',
                     u'joint1_seg'],
      'useCurve' : 'l_arm_crv',
      'baseName' : 'l_armSegment',
      'stretchBy' : 'translate',
      'advancedTwistSetup' : False,
      'addMidTwist' : True,
      'midIndex': 2,
      'extendTwistToEnd':False,
      'moduleInstance' : None,
      'reorient' : False}


import cgm.core.rig.segment_utils as SEGMENT
reload(SEGMENT)
SEGMENT.create_curveSetup(**_d)


SPECTRA.twist_drivers(**SPECTRA._dTwistNodes_l)

SPECTRA.shoulderTwist(**SPECTRA._dshoulderTwist_l)
SPECTRA.wristTwist(**SPECTRA._dwristTwist_l)



#===================================================================================================
# >> SegmentDirect
#===================================================================================================

_d_segmentDirect_l = {'joints':[u'arm1_l',
                                u'arm1_l|arm2_l',
                                u'arm1_l|arm2_l|arm3_l',
                                u'arm1_l|arm2_l|arm3_l|arm4_l',
                                u'arm1_l|arm2_l|arm3_l|arm4_l|arm5_l',
                                u'arm1_l|arm2_l|arm3_l|arm4_l|arm5_l|joint1',
                                u'arm1_l|arm2_l|arm3_l|arm4_l|arm5_l|joint1|wrist1_l']}
_d_segmentDirect_r = {'joints':[u'arm1_r', u'arm2_r', u'arm3_r', u'arm4_r', u'joint2', u'wrist1_r']}


def setupDirectOrbs(joints=None):
    ml_joints = cgmMeta.validateObjListArg(joints, 'cgmObject')
    
    for mJnt in ml_joints:
        mTrans = mJnt.createAt()
        #ATTR.set_message(mJnt.mNode, 'cgmSource',mTrans.mNode)
        mJnt.doStore('cgmSource',mTrans)
        mTrans.doStore('cgmName',mJnt)
        mTrans.doStore('cgmType','anim')
        mTrans.doName()
        
        mTrans.doGroup(True)
        

#Dave twist
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.cgm_Meta as cgmMeta

import pyunify.lib.node as node
import pyunify.lib.curve as curve
import pyunify.lib.nodeNetwork as nodeNetwork
import pyunify.lib.curve as curve
_d_attach_l = {'joints' : [u'arm1_l2_seg',
                           u'arm2_l_seg',
                           u'arm3_l_seg',
                           u'arm4_l_seg',
                           u'arm5_l_seg',
                           u'joint1_seg'],
               'useCurve' : 'l_arm_crv',
               'baseName' : 'l_armSegment',
               'controls' : [u'l_shoulder_blend|guardian_arm_l1_IK_grp|guardian_arm_l1_IK_anim',
                             u'l_elbow_blend|guardian_arm_l2_IK_grp|guardian_arm_l2_IK_anim',
                             u'guardian_arm_l3_IK_sub_anim'],
               'pocLocators' : [u"arm1_l2_seg_loc",
                                u"arm2_l_seg_loc",
                                u"arm3_l_seg_loc",
                                u"arm4_l_seg_loc",
                                u"arm5_l_seg_loc",
                                u"joint1_seg_loc"]}

_d_attach_r = {'joints' : [u'arm1_r1_seg',
                           u'arm2_r_seg',
                           u'arm3_r_seg',
                           u'arm4_r_seg',
                           u'arm5_r_seg',
                           u'joint2_seg'],
               'useCurve' : 'r_arm_crv',
               'baseName' : 'r_armSegment',
               'controls':[u'r_shoulder_blend|guardian_arm_r1_IK_grp|guardian_arm_r1_IK_anim',
                           u'r_elbow_blend|guardian_arm_r2_IK_grp|guardian_arm_r2_IK_anim',
                           u'guardian_arm_r3_IK_sub_anim'],
               'pocLocators': [u'arm1_r1_seg_loc',
                               u'arm2_r_seg_loc',
                               u'arm3_r_seg_loc',
                               u'arm4_r_seg_loc',
                               u'arm5_r_seg_loc',
                               u'joint2_seg_loc']}

def twistOnCurve(joints = [], useCurve = None, baseName = "", controls = [], pocLocators=[]):
    # cast controls as nodes
    controlNodes = [node.Transform(x) for x in controls]
    jointNodes = [node.Joint(x) for x in joints]
    curveNode = curve.Curve( useCurve )
    pocNodes = [node.Transform(x) for x in pocLocators]

    # Get nodes to calculate world up direction of the controls
    controlAimVectors = []
    controlPR = []
    obj = controlNodes[0]
    for obj in controlNodes:
        aimVector = nodeNetwork.TransformDirection( obj )  
        controlAimVectors.append(aimVector)

        pr = curveNode.NearestParameterOnCurve( obj.position )  #aimVector.GetAttr('outputTranslate')
        controlPR.append(pr)

    constraints = []
    jointPR = []

    startCon = controlNodes[0]
    endCon = controlNodes[1]

    startIndex = 0
    endIndex = 1

    i = 0
    jnt = jointNodes[0]
    for i, jnt in enumerate(jointNodes[:-1]):
        constraint = ( node.GetNodeType( mc.aimConstraint(pocNodes[i+1].name, jnt.name)[0] ) )
        constraints.append(constraint)

        pr = curveNode.NearestParameterOnCurve( jnt.position )
        jointPR.append(pr)

        # increment controls if pr goes higher than end control
        if pr > controlPR[endIndex]:
            startIndex = min(startIndex+1, len(controls))
            endIndex = min(endIndex+1, len(controls))
            endCon = controls[ endIndex ]
            startCon = controls[ startIndex ]

        # get the weight between the control PRs
        weight = ( ( pr - controlPR[startIndex] ) / ( controlPR[endIndex] - controlPR[startIndex] ) )

        # make the slerp
        slerp = node.Node( mc.createNode('vector3Slerp') )
        slerp.ConnectAttrIn('input1', controlAimVectors[startIndex].GetAttrString('outputTranslate') )
        slerp.ConnectAttrIn('input2', controlAimVectors[endIndex].GetAttrString('outputTranslate') )

        slerp.SetAttr('percent', weight)

        constraint.ConnectAttrIn('worldUpVector', slerp.GetAttrString('output') )
        constraint.SetAttr('aimVectorX', 0 )
        constraint.SetAttr('aimVectorY', 0 )
        constraint.SetAttr('aimVectorZ', 1 )

        constraint.SetAttr('upVectorX', 0 )
        constraint.SetAttr('upVectorY', 1 )
        constraint.SetAttr('upVectorZ', 0 )

    constraint = ( node.GetNodeType( mc.orientConstraint(controlNodes[-1].name, jointNodes[-1].name, mo=True)[0] ) )
    constraints.append(constraint)

twistOnCurve(**_d_attach_l)
        

    
reload(SPECTRA)

for j in SPECTRA._d_handlesDynP['segmentJoints']:
    mObj = cgmMeta.validateObjArg(j,'cgmObject')
    mObj.doStore('cgmAlias','followSeg')
    
    
for j in SPECTRA._d_handlesDynP['controls']:
    mObj = cgmMeta.validateObjArg(j,'cgmObject')
    mObj.dynParentGroup.rebuild()
    
    
