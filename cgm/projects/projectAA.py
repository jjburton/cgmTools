import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgm_RigMeta as RIGMETA
from .cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.attribute_utils as ATTR
from .cgm.core.rigger.lib import rig_Utils as rUtils
#reload(rUtils)
from .cgm.core.classes import NodeFactory as NodeF
import cgm.core.lib.distance_utils as DIST
from .cgm.core import cgm_General as cgmGEN

import maya.cmds as mc
import pprint

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#-------------------------------------------------------------------

d_drivenToDriver = {'ROOT': '|master|skeleton|rootMotion_jnt',
                    'TP': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt',
                    'TP_Head': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|neck_sknJnt|head_sknJnt',
                    'TP_L_Calf': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|L_hip_sknJnt|L_knee_sknJnt',
                    'TP_L_Clavicle': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt',
                    'TP_L_Finger0': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_thumb_0_sknJnt',
                    'TP_L_Finger01': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_thumb_0_sknJnt|L_thumb_1_sknJnt',
                    'TP_L_Finger02': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_thumb_0_sknJnt|L_thumb_1_sknJnt|L_thumb_2_sknJnt',
                    'TP_L_Finger1': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_index_1_sknJnt',
                    'TP_L_Finger11': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_index_1_sknJnt|L_index_2_sknJnt',
                    'TP_L_Finger12': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_index_1_sknJnt|L_index_2_sknJnt|L_index_3_sknJnt',
                    'TP_L_Finger2': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_middle_1_sknJnt',
                    'TP_L_Finger21': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_middle_1_sknJnt|L_middle_2_sknJnt',
                    'TP_L_Finger22': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_middle_1_sknJnt|L_middle_2_sknJnt|L_middle_3_sknJnt',
                    'TP_L_Finger3': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_ring_1_sknJnt',
                    'TP_L_Finger31': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_ring_1_sknJnt|L_ring_2_sknJnt',
                    'TP_L_Finger32': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_ring_1_sknJnt|L_ring_2_sknJnt|L_ring_3_sknJnt',
                    'TP_L_Finger4': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_pinky_1_sknJnt',
                    'TP_L_Finger41': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_pinky_1_sknJnt|L_pinky_2_sknJnt',
                    'TP_L_Finger42': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_pinky_1_sknJnt|L_pinky_2_sknJnt|L_pinky_3_sknJnt',
                    'TP_L_Foot': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|L_hip_sknJnt|L_knee_sknJnt|L_ankle_sknJnt',
                    'TP_L_Forearm': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt',
                    'TP_L_Hand': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt',
                    'TP_L_Thigh': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|L_hip_sknJnt',
                    'TP_L_Toe0': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|L_hip_sknJnt|L_knee_sknJnt|L_ankle_sknJnt|L_ball_sknJnt',
                    'TP_L_UpperArm': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt',
                    'TP_Neck': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|neck_sknJnt',
                    'TP_Pelvis': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt',
                    'TP_R_Calf': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|R_hip_sknJnt|R_knee_sknJnt',
                    'TP_R_Clavicle': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt',
                    'TP_R_Finger0': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_thumb_0_sknJnt',
                    'TP_R_Finger01': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_thumb_0_sknJnt|R_thumb_1_sknJnt',
                    'TP_R_Finger02': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_thumb_0_sknJnt|R_thumb_1_sknJnt|R_thumb_2_sknJnt',
                    'TP_R_Finger1': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_index_1_sknJnt',
                    'TP_R_Finger11': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_index_1_sknJnt|R_index_2_sknJnt',
                    'TP_R_Finger12': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_index_1_sknJnt|R_index_2_sknJnt|R_index_3_sknJnt',
                    'TP_R_Finger2': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_middle_1_sknJnt',
                    'TP_R_Finger21': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_middle_1_sknJnt|R_middle_2_sknJnt',
                    'TP_R_Finger22': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_middle_1_sknJnt|R_middle_2_sknJnt|R_middle_3_sknJnt',
                    'TP_R_Finger3': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_ring_1_sknJnt',
                    'TP_R_Finger31': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_ring_1_sknJnt|R_ring_2_sknJnt',
                    'TP_R_Finger32': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_ring_1_sknJnt|R_ring_2_sknJnt|R_ring_3_sknJnt',
                    'TP_R_Finger4': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_pinky_1_sknJnt',
                    'TP_R_Finger41': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_pinky_1_sknJnt|R_pinky_2_sknJnt',
                    'TP_R_Finger42': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_pinky_1_sknJnt|R_pinky_2_sknJnt|R_pinky_3_sknJnt',
                    'TP_R_Foot': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|R_hip_sknJnt|R_knee_sknJnt|R_ankle_sknJnt',
                    'TP_R_Forearm': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt',
                    'TP_R_Hand': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt',
                    'TP_R_Thigh': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|R_hip_sknJnt',
                    'TP_R_Toe0': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|R_hip_sknJnt|R_knee_sknJnt|R_ankle_sknJnt|R_ball_sknJnt',
                    'TP_R_UpperArm': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt',
                    'TP_Spine': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt',
                    'TP_Spine1': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt',
                    'TP_Spine2': '|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt'}



def attachFBXJointsToRig(connect=True):
    for driven,driver in list(d_drivenToDriver.items()):
        mDriver = cgmMeta.asMeta(driver)
        mDriven = cgmMeta.asMeta(driven)
        mTargetDriver = mDriver.getMessageAsMeta('fbxDriver')

        
        if connect:
            if not mTargetDriver:
                log.warning("Missing targetDriver: {0}".format(driver))
                continue
            _targetDriver = mTargetDriver.mNode
            
            log.info("Connecting: {0} -> {1}".format(mDriver.p_nameBase, mDriven.p_nameBase))
            
            mc.pointConstraint(_targetDriver,driven,maintainOffset=1)
            mc.orientConstraint(_targetDriver,driven,maintainOffset=1)            
            mc.scaleConstraint(_targetDriver,driven,maintainOffset=1)
        else:
            log.info("Breaking Connection: {0} -> {1}".format(mDriver.p_nameBase, mDriven.p_nameBase))            
            mDriven = cgmMeta.asMeta(driven)
            mc.delete(mDriven.getConstraintsTo())
            
            
def verifyTargetDrivers():
    for driven,driver in list(d_drivenToDriver.items()):
        mDriven = cgmMeta.asMeta(driven)
        mDriver = cgmMeta.asMeta(driver)
        
        if not mDriver.getMessage('fbxDriver'):
            mTargetDriver = mDriven.doCreateAt(setClass=True)
            mDriver.doStore('fbxDriver', mTargetDriver.mNode, 'message')
            mTargetDriver.rename("{0}_targetDriver".format(mDriver.p_nameBase))
            
            mDriverDriver = mDriver.getConstrainingObjects(asMeta=1)[0]
            mTargetDriver.p_parent = mDriverDriver
            mTargetDriver.rotateOrder = mDriven.rotateOrder
            mTargetDriver.dagLock(True)


            
