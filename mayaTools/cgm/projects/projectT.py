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
d_knight = {u'R_wrist_direct_anim': 4, u'CTR_totem_0_fk_anim_1_spacePivot_anim': 4, u'R_hip_fk_anim': 4, u'CTR_BCK_tailBase_0_direct_anim': 4, u'L_tailBase_0_direct_anim': 4, u'R_ankle_seg_anim': 4, u'R_pouch_0_ikBase_anim_0_spacePivot_anim': 4, u'R_elbow_roll_0_direct_anim': 4, u'leg_root_anim': 4, u'toe_pivot_anim': 2, u'arm_root_anim': 4, u'cog_anim': 4, u'CTR_head_fk_anim': 4, u'L_segMid_0_ik_anim': 4, u'CTR_spine_1_fk_anim': 4, u'L_ankle_ik_anim_0_spacePivot_anim': 4, u'ponyTail_root_anim': 4, u'R_ball_direct_anim': 4, u'R_segMid_1_ik_anim_0_spacePivot_anim': 4, u'L_pinky_2_direct_anim': 4, u'R_pouch_0_ik_anim_0_spacePivot_anim': 4, u'CTR_pelvis_fk_frame': 0, u'L_index_2_direct_anim': 4, u'R_elbow_seg_anim': 4, u'L_clav_FK_anim': 4, u'L_pouch_0_direct_anim': 4, u'L_middle_0_fk_anim': 4, u'R_middle_0_direct_anim': 4, u'L_ring_0_direct_anim': 4, u'R_knee_fk_anim': 4, u'R_thumb_2_direct_anim': 4, u'L_hip_seg_anim': 4, u'CTR_bell_0_ikBase_anim': 3, u'R_index_0_fk_anim': 4, u'L_pouch_0_ikBase_anim': 3, u'L_thumb_0_fk_anim': 4, u'R_pouch_0_fk_anim': 4, u'R_tailTip_fk_anim': 4, u'L_pouch_0_ikBase_anim_0_spacePivot_anim': 4, u'L_ring_1_direct_anim': 4, u'CTR_BCK_tail_2_fk_anim': 4, u'L_shoulder_seg_anim': 4, u'L_ponyTail_segMid_0_ik_anim_1_spacePivot_anim': 4, u'CTR_pelvis_handle_anim': 4, u'L_ankle_direct_anim': 4, u'R_ankle_ik_anim': 3, u'middle_root_anim': 4, u'R_hip_direct_anim': 4, u'R_thumb_2_fk_anim': 4, u'R_tail_2_direct_anim': 4, u'L_tailBase_ikBase_anim_0_spacePivot_anim': 4, u'L_segMid_1_ik_anim': 4, u'cog_anim_0_spacePivot_anim': 4, u'R_middle_settings_anim': 4, u'L_shoulder_ikBase_anim_1_spacePivot_anim': 4, u'R_hip_seg_anim': 4, u'R_tailTip_ik_anim_1_spacePivot_anim': 4, u'L_elbow_seg_anim': 4, u'R_ponyTail_settings_anim': 0, u'R_thumb_1_fk_anim': 4, u'CTR_neck_ikBase_anim': 4, u'R_pinky_1_direct_anim': 4, u'R_elbow_direct_anim': 4, u'R_tailBase_fk_anim': 4, u'L_pouch_0_ik_anim': 3, u'CTR_totem_3_direct_anim': 4, u'CTR_totem_2_direct_anim': 4, u'R_ring_settings_anim': 4, u'CTR_BCK_tailTip_direct_anim': 4, u'R_wrist_ik_anim': 3, u'L_segMid_0_ik_anim_0_spacePivot_anim': 4, u'L_tailTip_ik_anim': 4, u'R_middle_2_fk_anim': 4, u'L_index_1_fk_anim': 4, u'L_ankle_fk_anim': 4, u'R_shoulder_ikBase_anim_1_spacePivot_anim': 4, u'L_ring_1_fk_anim': 4, u'L_elbow_fk_anim': 4, u'CTR_hips_ikBase_anim_0_spacePivot_anim': 4, u'outer_pivot_anim': 2, u'CTR_chest_handle_anim': 4, u'L_ring_0_fk_anim': 4, u'R_knee_ikPole_anim': 3, u'L_pouch_0_ik_anim_1_spacePivot_anim': 4, u'R_pouch_0_ikBase_anim': 3, u'CTR_chest_direct_anim': 4, u'R_ring_1_direct_anim': 4, u'L_pinky_0_fk_anim': 4, u'L_ball_fk_anim': 4, u'R_hip_ikBase_anim': 3, u'L_hip_ikBase_anim_1_spacePivot_anim': 4, u'L_tailBase_ikBase_anim_1_spacePivot_anim': 4, u'CTR_bell_0_fk_anim': 4, u'L_hip_ikBase_anim_0_spacePivot_anim': 4, u'L_thumb_2_direct_anim': 4, u'R_segMid_0_ik_anim': 4, u'R_shoulder_ikBase_anim': 3, u'ring_root_anim': 4, u'L_thumb_1_fk_anim': 4, u'R_tailTip_direct_anim': 4, u'R_ponyTail_segMid_0_ik_anim': 4, u'CTR_head_ik_anim': 3, u'L_elbow_ikPole_anim_0_spacePivot_anim': 4, u'CTR_pelvis_0_direct_anim': 4, u'R_clav_direct_anim': 4, u'L_tail_1_direct_anim': 4, u'CTR_BCK_tailTip_ik_anim': 4, u'R_pouch_0_ik_anim_1_spacePivot_anim': 4, u'L_pinky_settings_anim': 4, u'L_ponyTail_segMid_0_ik_anim': 4, u'R_arm_limbRoot_anim': 4, u'L_tail_2_direct_anim': 4, u'R_shoulder_direct_anim': 4, u'bell_root_anim': 4, u'L_pinky_2_fk_anim': 4, u'L_knee_seg_anim': 4, u'head_root_anim': 4, u'CTR_BCK_tailBase_ikBase_anim_0_spacePivot_anim': 4, u'L_knee_ikPole_anim': 3, u'L_ring_2_direct_anim': 4, u'L_tailTip_direct_anim': 4, u'R_shoulder_ikBase_anim_0_spacePivot_anim': 4, u'R_index_2_direct_anim': 4, u'thumb_root_anim': 4, u'R_tail_2_fk_anim': 4, u'L_shoulder_ikBase_anim': 3, u'cog_anim_1_spacePivot_anim': 4, u'CTR_neck_fk_anim': 4, u'R_hip_ikBase_anim_1_spacePivot_anim': 4, u'R_clav_FK_anim': 4, u'R_ball_fk_anim': 4, u'L_ball_direct_anim': 4, u'L_ankle_ik_anim_1_spacePivot_anim': 4, u'L_clav_direct_anim': 4, u'L_leg_settings_anim': 4, u'rootMotion_anim': 0, u'CTR_BCK_tailTip_ik_anim_1_spacePivot_anim': 4, u'R_thumb_0_direct_anim': 4, u'R_hip_roll_0_direct_anim': 4, u'ponyTail_root_anim_1_spacePivot_anim': 4, u'ponyTail_root_anim_0_spacePivot_anim': 4, u'head_lookAt_anim': 2, u'R_knee_roll_0_direct_anim': 4, u'L_elbow_direct_anim': 4, u'L_index_2_fk_anim': 4, u'CTR_bell_0_ik_anim': 3, u'R_tailBase_0_direct_anim': 4, u'R_segMid_0_ik_anim_1_spacePivot_anim': 4, u'CTR_BCK_ponyTail_segMid_0_ik_anim': 4, u'CTR_chest_ik_anim': 4, u'L_ankle_seg_anim': 4, u'R_pinky_2_fk_anim': 4, u'R_ring_2_direct_anim': 4, u'R_ponyTail_segMid_0_ik_anim_1_spacePivot_anim': 4, u'CTR_bell_settings_anim': 4, u'R_thumb_0_fk_anim': 4, u'L_middle_1_fk_anim': 4, u'index_root_anim': 4, u'L_hip_ikBase_anim': 3, u'R_wrist_seg_anim': 4, u'CTR_chest_ik_anim_0_spacePivot_anim': 4, u'L_arm_settings_anim': 4, u'R_index_2_fk_anim': 4, u'R_leg_settings_anim': 4, u'L_tailBase_fk_anim': 4, u'L_middle_1_direct_anim': 4, u'R_wrist_fk_anim': 4, u'L_wrist_fk_anim': 4, u'R_knee_direct_anim': 4, u'CTR_bell_0_ikBase_anim_1_spacePivot_anim': 4, u'L_thumb_1_direct_anim': 4, u'R_arm_settings_anim': 4, u'R_pinky_1_fk_anim': 4, u'CTR_totem_3_fk_anim': 4, u'L_pinky_1_direct_anim': 4, u'L_segMid_1_ik_anim_0_spacePivot_anim': 4, u'L_knee_direct_anim': 4, u'ball_pivot_anim': 2, u'L_wrist_direct_anim': 4, u'L_thumb_settings_anim': 4, u'L_hip_roll_0_direct_anim': 4, u'L_segMid_1_ik_anim_1_spacePivot_anim': 4, u'pouch_root_anim': 4, u'L_shoulder_ikBase_anim_0_spacePivot_anim': 4, u'R_knee_seg_anim': 4, u'R_shoulder_seg_anim': 4, u'CTR_BCK_ponyTail_settings_anim': 0, u'L_ankle_ik_anim': 3, u'CTR_chest_ik_anim_1_spacePivot_anim': 4, u'CTR_totem_settings_anim': 4, u'R_pinky_2_direct_anim': 4, u'R_knee_ikPole_anim_1_spacePivot_anim': 4, u'CTR_BCK_ponyTail_segMid_0_ik_anim_0_spacePivot_anim': 4, u'L_shoulder_fk_anim': 4, u'R_tailTip_ik_anim_0_spacePivot_anim': 4, u'L_shoulder_direct_anim': 4, u'R_index_1_direct_anim': 4, u'pinky_root_anim': 4, u'L_index_settings_anim': 4, u'R_pouch_settings_anim': 4, u'R_ponyTail_segMid_0_ik_anim_0_spacePivot_anim': 4, u'CTR_neck_direct_anim': 4, u'L_ring_settings_anim': 4, u'L_pouch_0_fk_anim': 4, u'L_index_0_direct_anim': 4, u'R_tailBase_ikBase_anim': 4, u'L_pinky_1_fk_anim': 4, u'R_middle_1_direct_anim': 4, u'CTR_totem_0_direct_anim': 4, u'R_pouch_0_direct_anim': 4, u'R_ring_0_fk_anim': 4, u'L_wrist_seg_anim': 4, u'L_ponyTail_settings_anim': 0, u'L_knee_roll_0_direct_anim': 4, u'L_pinky_0_direct_anim': 4, u'CTR_totem_1_fk_anim': 4, u'R_middle_0_fk_anim': 4, u'CTR_BCK_tail_1_fk_anim': 4, u'CTR_totem_1_direct_anim': 4, u'CTR_spine_2_direct_anim': 4, u'L_hip_fk_anim': 4, u'L_index_1_direct_anim': 4, u'L_wrist_ik_anim_0_spacePivot_anim': 4, u'R_wrist_ik_anim_0_spacePivot_anim': 4, u'R_shoulder_fk_anim': 4, u'R_ankle_fk_anim': 4, u'R_tailTip_ik_anim': 4, u'R_ankle_direct_anim': 4, u'R_pinky_0_fk_anim': 4, u'L_thumb_2_fk_anim': 4, u'heel_pivot_anim': 2, u'L_middle_2_fk_anim': 4, u'R_segMid_0_ik_anim_0_spacePivot_anim': 4, u'R_elbow_ikPole_anim_1_spacePivot_anim': 4, u'R_tail_1_fk_anim': 4, u'L_middle_settings_anim': 4, u'L_middle_2_direct_anim': 4, u'R_pinky_0_direct_anim': 4, u'L_hip_direct_anim': 4, u'head_settings_anim': 4, u'R_thumb_settings_anim': 4, u'CTR_BCK_ponyTail_segMid_0_ik_anim_1_spacePivot_anim': 4, u'L_index_0_fk_anim': 4, u'R_ankle_ik_anim_0_spacePivot_anim': 4, u'R_pinky_settings_anim': 4, u'CTR_bell_0_direct_anim': 4, u'CTR_bell_0_ik_anim_0_spacePivot_anim': 4, u'R_middle_1_fk_anim': 4, u'CTR_totem_0_fk_anim': 4, u'L_ball_ik_anim': 4, u'L_tail_2_fk_anim': 4, u'R_index_settings_anim': 4, u'R_knee_ikPole_anim_0_spacePivot_anim': 4, u'L_shoulder_roll_0_direct_anim': 4, u'R_ankle_ik_anim_1_spacePivot_anim': 4, u'R_tailBase_ikBase_anim_1_spacePivot_anim': 4, u'L_pouch_0_ik_anim_0_spacePivot_anim': 4, u'CTR_totem_2_fk_anim': 4, u'R_index_1_fk_anim': 4, u'L_tailBase_ikBase_anim': 4, u'CTR_BCK_tailTip_fk_anim': 4, u'R_ring_2_fk_anim': 4, u'CTR_BCK_tailBase_ikBase_anim_1_spacePivot_anim': 4, u'master_anim': 3, u'L_elbow_roll_0_direct_anim': 4, u'L_elbow_ikPole_anim_1_spacePivot_anim': 4, u'L_arm_limbRoot_anim': 4, u'R_pouch_0_ikBase_anim_1_spacePivot_anim': 4, u'CTR_spine_1_direct_anim': 4, u'L_tailTip_ik_anim_1_spacePivot_anim': 4, u'CTR_BCK_tailTip_ik_anim_0_spacePivot_anim': 4, u'L_middle_0_direct_anim': 4, u'CTR_totem_0_fk_anim_0_spacePivot_anim': 4, u'L_pouch_settings_anim': 4, u'L_tailTip_fk_anim': 4, u'CTR_bell_0_ikBase_anim_0_spacePivot_anim': 4, u'R_segMid_1_ik_anim': 4, u'R_index_0_direct_anim': 4, u'R_segMid_1_ik_anim_1_spacePivot_anim': 4, u'CTR_BCK_tail_1_direct_anim': 4, u'CTR_BCK_tailBase_fk_anim': 4, u'R_elbow_ikPole_anim': 3, u'R_ball_hinge_ik_anim': 4, u'R_shoulder_roll_0_direct_anim': 4, u'L_thumb_0_direct_anim': 4, u'L_knee_ikPole_anim_1_spacePivot_anim': 4, u'L_ball_hinge_ik_anim': 4, u'totem_root_anim': 4, u'L_knee_fk_anim': 4, u'CTR_hips_ikBase_anim_1_spacePivot_anim': 4, u'L_tailTip_ik_anim_0_spacePivot_anim': 4, u'R_hip_ikBase_anim_0_spacePivot_anim': 4, u'L_segMid_0_ik_anim_1_spacePivot_anim': 4, u'L_tail_1_fk_anim': 4, u'R_ring_0_direct_anim': 4, u'CTR_bell_0_ik_anim_1_spacePivot_anim': 4, u'L_ring_2_fk_anim': 4, u'R_thumb_1_direct_anim': 4, u'L_knee_ikPole_anim_0_spacePivot_anim': 4, u'L_ponyTail_segMid_0_ik_anim_0_spacePivot_anim': 4, u'R_tailBase_ikBase_anim_0_spacePivot_anim': 4, u'R_elbow_fk_anim': 4, u'L_pouch_0_ikBase_anim_1_spacePivot_anim': 4, u'L_wrist_ik_anim_1_spacePivot_anim': 4, u'CTR_chest_fk_anim': 4, u'R_ring_1_fk_anim': 4, u'CTR_head_direct_anim': 4, u'R_pouch_0_ik_anim': 3, u'R_wrist_ik_anim_1_spacePivot_anim': 4, u'R_elbow_ikPole_anim_0_spacePivot_anim': 4, u'CTR_spine_1_handle_anim': 4, u'CTR_BCK_tail_2_direct_anim': 4, u'master_anim_0_spacePivot_anim': 3, u'L_elbow_ikPole_anim': 3, u'R_middle_2_direct_anim': 4, u'L_wrist_ik_anim': 3, u'inner_pivot_anim': 2, u'R_ball_ik_anim': 4, u'CTR_BCK_tailBase_ikBase_anim': 4, u'CTR_hips_ikBase_anim': 4, u'R_tail_1_direct_anim': 4} # 

d_shaders = {u'base': {u'ambientColor': [(0.0, 0.0, 0.0)],
                 u'ambientColorB': 0.0,
                 u'ambientColorG': 0.0,
                 u'ambientColorR': 0.0,
                 u'binMembership': None,
                 u'caching': False,
                 u'chromaticAberration': False,
                 u'diffuse': 1.0,
                 u'frozen': False,
                 u'glowIntensity': 0.0,
                 u'hardwareShader': [(0.0, 0.0, 0.0)],
                 u'hardwareShaderB': 0.0,
                 u'hardwareShaderG': 0.0,
                 u'hardwareShaderR': 0.0,
                 u'hideSource': False,
                 u'incandescence': [(0.0, 0.0, 0.0)],
                 u'incandescenceB': 0.0,
                 u'incandescenceG': 0.0,
                 u'incandescenceR': 0.0,
                 u'isHistoricallyInteresting': 2,
                 u'lightAbsorbance': 0.0,
                 u'lightDataArray': {},
                 u'materialAlphaGain': 1.0,
                 u'matteOpacity': 1.0,
                 u'matteOpacityMode': 2,
                 u'mediumRefractiveIndex': 1.0,
                 u'message': [u'hyperShadePrimaryNodeEditorSavedTabsInfo',
                              u'materialInfo21',
                              u'defaultShaderList1'],
                 u'nodeState': 0,
                 u'objectId': 0.0,
                 u'opacityDepth': 0.0,
                 u'outColor': [(0.0, 0.0, 0.0)],
                 u'outColorB': 0.0,
                 u'outColorG': 0.0,
                 u'outColorR': 0.0,
                 u'outGlowColor': [(0.0, 0.0, 0.0)],
                 u'outGlowColorB': 0.0,
                 u'outGlowColorG': 0.0,
                 u'outGlowColorR': 0.0,
                 u'outMatteOpacity': [(1.0, 1.0, 1.0)],
                 u'outMatteOpacityB': 1.0,
                 u'outMatteOpacityG': 1.0,
                 u'outMatteOpacityR': 1.0,
                 u'outTransparency': [(0.0, 0.0, 0.0)],
                 u'outTransparencyB': 0.0,
                 u'outTransparencyG': 0.0,
                 u'outTransparencyR': 0.0,
                 u'pointCamera': [(1.0, 1.0, 1.0)],
                 u'pointCameraX': 1.0,
                 u'pointCameraY': 1.0,
                 u'pointCameraZ': 1.0,
                 u'primitiveId': 0,
                 u'rayDepth': 0,
                 u'rayDirection': [(0.0, 0.0, 1.0)],
                 u'rayDirectionX': 0.0,
                 u'rayDirectionY': 0.0,
                 u'rayDirectionZ': 1.0,
                 u'rayInstance': 0,
                 u'raySampler': 0.0,
                 u'reflectedColor': [(0.0, 0.0, 0.0)],
                 u'reflectedColorB': 0.0,
                 u'reflectedColorG': 0.0,
                 u'reflectedColorR': 0.0,
                 u'reflectionLimit': 1,
                 u'reflectionRolloff': True,
                 u'reflectionSpecularity': 1.0,
                 u'reflectivity': 0.0,
                 u'refractionLimit': 6,
                 u'refractions': False,
                 u'refractiveIndex': 1.0,
                 u'shadowAttenuation': 0.5,
                 u'surfaceThickness': 0.0,
                 u'translucence': 0.0,
                 u'translucenceDepth': 0.5,
                 u'translucenceFocus': 0.5,
                 u'transparency': [(0.0, 0.0, 0.0)],
                 u'transparencyB': 0.0,
                 u'transparencyDepth': 0.0,
                 u'transparencyG': 0.0,
                 u'transparencyR': 0.0,
                 u'triangleNormalCamera': [(0.0, 1.0, 0.0)],
                 u'triangleNormalCameraX': 0.0,
                 u'triangleNormalCameraY': 1.0,
                 u'triangleNormalCameraZ': 0.0,
                 u'vrEdgeColor': [(0.5, 0.5, 0.5)],
                 u'vrEdgeColorB': 0.5,
                 u'vrEdgeColorG': 0.5,
                 u'vrEdgeColorR': 0.5,
                 u'vrEdgePriority': 0,
                 u'vrEdgeStyle': 0,
                 u'vrEdgeWeight': 0.0,
                 u'vrFillObject': 0,
                 u'vrHiddenEdges': False,
                 u'vrHiddenEdgesOnTransparent': False,
                 u'vrOutlinesAtIntersections': True,
                 u'vrOverwriteDefaults': False},
 u'blackDiffuse': {u'ambientColor': [(0.0, 0.0, 0.0)],
                   u'ambientColorB': 0.0,
                   u'ambientColorG': 0.0,
                   u'ambientColorR': 0.0,
                   u'binMembership': None,
                   u'caching': False,
                   u'chromaticAberration': False,
                   u'color': [(0.0, 0.0, 0.0)],
                   u'colorB': 0.0,
                   u'colorG': 0.0,
                   u'colorR': 0.0,
                   u'cosinePower': 2.0,
                   u'diffuse': 0.0,
                   u'frozen': False,
                   u'glowIntensity': 0.0,
                   u'hardwareShader': [(0.0, 0.0, 0.0)],
                   u'hardwareShaderB': 0.0,
                   u'hardwareShaderG': 0.0,
                   u'hardwareShaderR': 0.0,
                   u'hideSource': False,
                   u'incandescence': [(0.0, 0.0, 0.0)],
                   u'incandescenceB': 0.0,
                   u'incandescenceG': 0.0,
                   u'incandescenceR': 0.0,
                   u'isHistoricallyInteresting': 2,
                   u'lightAbsorbance': 0.0,
                   u'lightDataArray': {},
                   u'materialAlphaGain': 1.0,
                   u'matteOpacity': 1.0,
                   u'matteOpacityMode': 2,
                   u'mediumRefractiveIndex': 1.0,
                   u'message': [u'defaultShaderList1', u'materialInfo23'],
                   u'nodeState': 0,
                   u'normalCamera': [(1.0, 1.0, 1.0)],
                   u'normalCameraX': 1.0,
                   u'normalCameraY': 1.0,
                   u'normalCameraZ': 1.0,
                   u'objectId': 0.0,
                   u'opacityDepth': 0.0,
                   u'outColor': [(0.0, 0.0, 0.0)],
                   u'outColorB': 0.0,
                   u'outColorG': 0.0,
                   u'outColorR': 0.0,
                   u'outGlowColor': [(0.0, 0.0, 0.0)],
                   u'outGlowColorB': 0.0,
                   u'outGlowColorG': 0.0,
                   u'outGlowColorR': 0.0,
                   u'outMatteOpacity': [(1.0, 1.0, 1.0)],
                   u'outMatteOpacityB': 1.0,
                   u'outMatteOpacityG': 1.0,
                   u'outMatteOpacityR': 1.0,
                   u'outTransparency': [(0.0, 0.0, 0.0)],
                   u'outTransparencyB': 0.0,
                   u'outTransparencyG': 0.0,
                   u'outTransparencyR': 0.0,
                   u'pointCamera': [(1.0, 1.0, 1.0)],
                   u'pointCameraX': 1.0,
                   u'pointCameraY': 1.0,
                   u'pointCameraZ': 1.0,
                   u'primitiveId': 0,
                   u'rayDepth': 0,
                   u'rayDirection': [(0.0, 0.0, 1.0)],
                   u'rayDirectionX': 0.0,
                   u'rayDirectionY': 0.0,
                   u'rayDirectionZ': 1.0,
                   u'rayInstance': 0,
                   u'raySampler': 0.0,
                   u'reflectedColor': [(0.0, 0.0, 0.0)],
                   u'reflectedColorB': 0.0,
                   u'reflectedColorG': 0.0,
                   u'reflectedColorR': 0.0,
                   u'reflectionLimit': 1,
                   u'reflectionSpecularity': 1.0,
                   u'reflectivity': 1.0,
                   u'refractionLimit': 6,
                   u'refractions': False,
                   u'refractiveIndex': 1.0,
                   u'shadowAttenuation': 0.5,
                   u'specularColor': [(0.0, 0.0, 0.0)],
                   u'specularColorB': 0.0,
                   u'specularColorG': 0.0,
                   u'specularColorR': 0.0,
                   u'surfaceThickness': 0.0,
                   u'translucence': 0.0,
                   u'translucenceDepth': 0.5,
                   u'translucenceFocus': 0.5,
                   u'transparency': [(0.0, 0.0, 0.0)],
                   u'transparencyB': 0.0,
                   u'transparencyDepth': 0.0,
                   u'transparencyG': 0.0,
                   u'transparencyR': 0.0,
                   u'triangleNormalCamera': [(0.0, 1.0, 0.0)],
                   u'triangleNormalCameraX': 0.0,
                   u'triangleNormalCameraY': 1.0,
                   u'triangleNormalCameraZ': 0.0,
                   u'vrEdgeColor': [(0.5, 0.5, 0.5)],
                   u'vrEdgeColorB': 0.5,
                   u'vrEdgeColorG': 0.5,
                   u'vrEdgeColorR': 0.5,
                   u'vrEdgePriority': 0,
                   u'vrEdgeStyle': 0,
                   u'vrEdgeWeight': 0.0,
                   u'vrFillObject': 0,
                   u'vrHiddenEdges': False,
                   u'vrHiddenEdgesOnTransparent': False,
                   u'vrOutlinesAtIntersections': True,
                   u'vrOverwriteDefaults': False}}


d_characters = {'Knight01':{'cog':'cog_anim',
                            'l_arm':'L_arm_limb',
                            'r_arm':'R_arm_limb',
                            'l_leg':'L_leg_limb',
                            'r_leg':'R_leg_limb',
                            'totem':'CTR_totem_limb'},
                'Hawk':{'puppet':'master_puppetNetwork',
                        'snapHip':'cog_snap',
                        'snapLAnkle':'L_ankle_snap',
                        'snapRAnkle':'R_ankle_snap',
                        'snapLWrist':'L_wrist_snap',
                        'snapRWrist':'R_wrist_snap',
                        'snapTotem':'totem_snap',
                        }}

def attachCharacterToMount(character= 'Knight01', mount = 'Hawk', totem = False):
    _str_func = 'attachCharacterToMount'
    log.info("|{0}| >>...".format(_str_func))
    
    
    md_dat = {}
    
    md_dat['character'] = {}
    md_char = md_dat['character']
    for k,d in d_characters.get(character).iteritems():
        md_char[k] = cgmMeta.asMeta('{0}:{1}'.format(character,d))
        
        
    md_dat['puppet'] = {}
    md_puppet = md_dat['puppet']
    for k,d in d_characters.get(mount).iteritems():
        md_puppet[k] = cgmMeta.asMeta('{0}:{1}'.format(mount,d))
        
    pprint.pprint(md_dat)
    
    #Attach -------------------------------------------------------------------
    log.info(cgmGEN.logString_sub(_str_func,'attach'))
    
    log.info(cgmGEN.logString_msg(_str_func,'cog'))
    
    mCog = md_dat['character']['cog']
    mCog.pivot_0 = 2
    mCog.space = 3
    
    mSpacePivot = mCog.spacePivots_0
    mc.parentConstraint(md_puppet['snapHip'].mNode, mSpacePivot.mNode, maintainOffset = False)
    
    
    
    #assuming settings....
    d_attaches = {'l_arm':{'control':'controlIK','target':'snapLWrist','space':8},
                  'r_arm':{'control':'controlIK','target':'snapRWrist','space':8},
                  'l_leg':{'control':'controlIK','target':'snapLAnkle','space':7},
                  'r_leg':{'control':'controlIK','target':'snapRAnkle','space':7},
                  'totem':{'control':['fk',0],'target':'snapTotem','space':7},
                  }
    
    for k,d in d_attaches.iteritems():
        log.info(cgmGEN.logString_msg(_str_func,k))
        mPart = md_char[k]
        mRigNull = md_char[k].rigNull
        mSettings = mRigNull.settings
        
        if k == 'totem' and not totem:
            continue
        
        try:
            
            if VALID.isListArg(d['control']):
                log.info("list arg..")
                mControl = mRigNull.getMessageAsMeta('{0}Joints_{1}'.format(d['control'][0],d['control'][1]))
            else:
                mControl = mRigNull.getMessageAsMeta(d['control'])
            
            mTarget = md_puppet[d['target']]
            
            mSettings.FKIK = 1
            mControl.pivot_0 = 2
            mControl.space = d['space']
            
            mSpacePivot = mControl.spacePivots_0
            mc.parentConstraint(mTarget.mNode, mSpacePivot.mNode, maintainOffset = False)
            
            mControl.doSnapTo(mTarget)
        except Exception,err:
            log.error("{0} failed | {1}".format(k, err))
            pprint.pprint(vars())
        
        
    mCog.doSnapTo(md_puppet['snapHip'].mNode)
    
    
    
    #Mount ------------------------------------------------------------------
    #....Find our mount points
    
    
    
    #Character ------------------------------------------------------------------
    
    
    #Find our controls
    

    
    #Attach -------------------------------------------------------------------
    
_d_wheels = {'L_BCK_wheel_handle':{},
             'R_BCK_wheel_handle':{},
             'L_FRNT_wheel_handle':{},
             'R_FRNT_wheel_handle':{},             
             }

def setupWheelRoll(dat = _d_wheels):
    for m,d in dat.iteritems():
        mModule = cgmMeta.asMeta(m)
    
        mRigNull = mModule.rigNull
        mPivot = mRigNull.getMessageAsMeta('pivotResultDriver')
        mSettings = mRigNull.getMessageAsMeta('settings')
        
        mAttr = cgmMeta.cgmAttr(mSettings, 'wheelSpin','float',hidden=False,keyable=True)
        
        mAttr.doConnectOut("{0}.rx".format(mPivot.mNode))
        
        

def createAndContrainRigFromSkinJoints(joints = []):
    pprint.pprint(vars())    
    
    ml_joints = cgmMeta.validateObjListArg(joints,'cgmObject')
    ml_new = []
    for i,mObj in enumerate(ml_joints):
        mDup = mObj.doDuplicate(po=True)
        mDup.rename( mObj.p_nameBase.replace('sknj','rig') )
        mDup.connectChildNode(mObj,'skinJoin','rigJoint')
        ml_new.append(mObj)
        if i > 0:
            if ml_joints[i].parent:
                _buffer = ml_joints[i].getParent(asMeta=True).getMessage('rigJoint')
                if _buffer:
                    mDup.parent =_buffer[0]
        
        mc.pointConstraint([mDup.mNode], mObj.mNode, maintainOffset = True)
        mc.orientConstraint([mDup.mNode], mObj.mNode, maintainOffset = True)
    return ml_new
