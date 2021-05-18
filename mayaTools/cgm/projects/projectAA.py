import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgm_RigMeta as RIGMETA
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.attribute_utils as ATTR
from cgm.core.rigger.lib import rig_Utils as rUtils
#reload(rUtils)
from cgm.core.classes import NodeFactory as NodeF
import cgm.core.lib.distance_utils as DIST
from cgm.core import cgm_General as cgmGEN

import maya.cmds as mc
import pprint

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#-------------------------------------------------------------------

d_drivenToDriver = {u'ROOT': u'|master|skeleton|rootMotion_jnt',
                    u'TP': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt',
                    u'TP_Head': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|neck_sknJnt|head_sknJnt',
                    u'TP_L_Calf': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|L_hip_sknJnt|L_knee_sknJnt',
                    u'TP_L_Clavicle': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt',
                    u'TP_L_Finger0': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_thumb_0_sknJnt',
                    u'TP_L_Finger01': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_thumb_0_sknJnt|L_thumb_1_sknJnt',
                    u'TP_L_Finger02': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_thumb_0_sknJnt|L_thumb_1_sknJnt|L_thumb_2_sknJnt',
                    u'TP_L_Finger1': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_index_1_sknJnt',
                    u'TP_L_Finger11': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_index_1_sknJnt|L_index_2_sknJnt',
                    u'TP_L_Finger12': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_index_1_sknJnt|L_index_2_sknJnt|L_index_3_sknJnt',
                    u'TP_L_Finger2': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_middle_1_sknJnt',
                    u'TP_L_Finger21': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_middle_1_sknJnt|L_middle_2_sknJnt',
                    u'TP_L_Finger22': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_middle_1_sknJnt|L_middle_2_sknJnt|L_middle_3_sknJnt',
                    u'TP_L_Finger3': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_ring_1_sknJnt',
                    u'TP_L_Finger31': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_ring_1_sknJnt|L_ring_2_sknJnt',
                    u'TP_L_Finger32': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_ring_1_sknJnt|L_ring_2_sknJnt|L_ring_3_sknJnt',
                    u'TP_L_Finger4': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_pinky_1_sknJnt',
                    u'TP_L_Finger41': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_pinky_1_sknJnt|L_pinky_2_sknJnt',
                    u'TP_L_Finger42': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt|L_pinky_1_sknJnt|L_pinky_2_sknJnt|L_pinky_3_sknJnt',
                    u'TP_L_Foot': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|L_hip_sknJnt|L_knee_sknJnt|L_ankle_sknJnt',
                    u'TP_L_Forearm': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt',
                    u'TP_L_Hand': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt|L_elbow_sknJnt|L_wrist_sknJnt',
                    u'TP_L_Thigh': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|L_hip_sknJnt',
                    u'TP_L_Toe0': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|L_hip_sknJnt|L_knee_sknJnt|L_ankle_sknJnt|L_ball_sknJnt',
                    u'TP_L_UpperArm': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|L_clav_sknJnt|L_shoulder_sknJnt',
                    u'TP_Neck': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|neck_sknJnt',
                    u'TP_Pelvis': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt',
                    u'TP_R_Calf': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|R_hip_sknJnt|R_knee_sknJnt',
                    u'TP_R_Clavicle': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt',
                    u'TP_R_Finger0': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_thumb_0_sknJnt',
                    u'TP_R_Finger01': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_thumb_0_sknJnt|R_thumb_1_sknJnt',
                    u'TP_R_Finger02': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_thumb_0_sknJnt|R_thumb_1_sknJnt|R_thumb_2_sknJnt',
                    u'TP_R_Finger1': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_index_1_sknJnt',
                    u'TP_R_Finger11': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_index_1_sknJnt|R_index_2_sknJnt',
                    u'TP_R_Finger12': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_index_1_sknJnt|R_index_2_sknJnt|R_index_3_sknJnt',
                    u'TP_R_Finger2': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_middle_1_sknJnt',
                    u'TP_R_Finger21': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_middle_1_sknJnt|R_middle_2_sknJnt',
                    u'TP_R_Finger22': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_middle_1_sknJnt|R_middle_2_sknJnt|R_middle_3_sknJnt',
                    u'TP_R_Finger3': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_ring_1_sknJnt',
                    u'TP_R_Finger31': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_ring_1_sknJnt|R_ring_2_sknJnt',
                    u'TP_R_Finger32': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_ring_1_sknJnt|R_ring_2_sknJnt|R_ring_3_sknJnt',
                    u'TP_R_Finger4': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_pinky_1_sknJnt',
                    u'TP_R_Finger41': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_pinky_1_sknJnt|R_pinky_2_sknJnt',
                    u'TP_R_Finger42': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt|R_pinky_1_sknJnt|R_pinky_2_sknJnt|R_pinky_3_sknJnt',
                    u'TP_R_Foot': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|R_hip_sknJnt|R_knee_sknJnt|R_ankle_sknJnt',
                    u'TP_R_Forearm': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt',
                    u'TP_R_Hand': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt|R_elbow_sknJnt|R_wrist_sknJnt',
                    u'TP_R_Thigh': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|R_hip_sknJnt',
                    u'TP_R_Toe0': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|R_hip_sknJnt|R_knee_sknJnt|R_ankle_sknJnt|R_ball_sknJnt',
                    u'TP_R_UpperArm': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt|R_clav_sknJnt|R_shoulder_sknJnt',
                    u'TP_Spine': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt',
                    u'TP_Spine1': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt',
                    u'TP_Spine2': u'|master|skeleton|rootMotion_jnt|pelvis_sknJnt|spine_1_sknJnt|spine_2_sknJnt|chest_sknJnt'}



def attachFBXJointsToRig(connect=True):
    for driven,driver in d_drivenToDriver.iteritems():
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
    for driven,driver in d_drivenToDriver.iteritems():
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


            
