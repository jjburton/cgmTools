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
d_knight = {'R_wrist_direct_anim': 4, 'CTR_totem_0_fk_anim_1_spacePivot_anim': 4, 'R_hip_fk_anim': 4, 'CTR_BCK_tailBase_0_direct_anim': 4, 'L_tailBase_0_direct_anim': 4, 'R_ankle_seg_anim': 4, 'R_pouch_0_ikBase_anim_0_spacePivot_anim': 4, 'R_elbow_roll_0_direct_anim': 4, 'leg_root_anim': 4, 'toe_pivot_anim': 2, 'arm_root_anim': 4, 'cog_anim': 4, 'CTR_head_fk_anim': 4, 'L_segMid_0_ik_anim': 4, 'CTR_spine_1_fk_anim': 4, 'L_ankle_ik_anim_0_spacePivot_anim': 4, 'ponyTail_root_anim': 4, 'R_ball_direct_anim': 4, 'R_segMid_1_ik_anim_0_spacePivot_anim': 4, 'L_pinky_2_direct_anim': 4, 'R_pouch_0_ik_anim_0_spacePivot_anim': 4, 'CTR_pelvis_fk_frame': 0, 'L_index_2_direct_anim': 4, 'R_elbow_seg_anim': 4, 'L_clav_FK_anim': 4, 'L_pouch_0_direct_anim': 4, 'L_middle_0_fk_anim': 4, 'R_middle_0_direct_anim': 4, 'L_ring_0_direct_anim': 4, 'R_knee_fk_anim': 4, 'R_thumb_2_direct_anim': 4, 'L_hip_seg_anim': 4, 'CTR_bell_0_ikBase_anim': 3, 'R_index_0_fk_anim': 4, 'L_pouch_0_ikBase_anim': 3, 'L_thumb_0_fk_anim': 4, 'R_pouch_0_fk_anim': 4, 'R_tailTip_fk_anim': 4, 'L_pouch_0_ikBase_anim_0_spacePivot_anim': 4, 'L_ring_1_direct_anim': 4, 'CTR_BCK_tail_2_fk_anim': 4, 'L_shoulder_seg_anim': 4, 'L_ponyTail_segMid_0_ik_anim_1_spacePivot_anim': 4, 'CTR_pelvis_handle_anim': 4, 'L_ankle_direct_anim': 4, 'R_ankle_ik_anim': 3, 'middle_root_anim': 4, 'R_hip_direct_anim': 4, 'R_thumb_2_fk_anim': 4, 'R_tail_2_direct_anim': 4, 'L_tailBase_ikBase_anim_0_spacePivot_anim': 4, 'L_segMid_1_ik_anim': 4, 'cog_anim_0_spacePivot_anim': 4, 'R_middle_settings_anim': 4, 'L_shoulder_ikBase_anim_1_spacePivot_anim': 4, 'R_hip_seg_anim': 4, 'R_tailTip_ik_anim_1_spacePivot_anim': 4, 'L_elbow_seg_anim': 4, 'R_ponyTail_settings_anim': 0, 'R_thumb_1_fk_anim': 4, 'CTR_neck_ikBase_anim': 4, 'R_pinky_1_direct_anim': 4, 'R_elbow_direct_anim': 4, 'R_tailBase_fk_anim': 4, 'L_pouch_0_ik_anim': 3, 'CTR_totem_3_direct_anim': 4, 'CTR_totem_2_direct_anim': 4, 'R_ring_settings_anim': 4, 'CTR_BCK_tailTip_direct_anim': 4, 'R_wrist_ik_anim': 3, 'L_segMid_0_ik_anim_0_spacePivot_anim': 4, 'L_tailTip_ik_anim': 4, 'R_middle_2_fk_anim': 4, 'L_index_1_fk_anim': 4, 'L_ankle_fk_anim': 4, 'R_shoulder_ikBase_anim_1_spacePivot_anim': 4, 'L_ring_1_fk_anim': 4, 'L_elbow_fk_anim': 4, 'CTR_hips_ikBase_anim_0_spacePivot_anim': 4, 'outer_pivot_anim': 2, 'CTR_chest_handle_anim': 4, 'L_ring_0_fk_anim': 4, 'R_knee_ikPole_anim': 3, 'L_pouch_0_ik_anim_1_spacePivot_anim': 4, 'R_pouch_0_ikBase_anim': 3, 'CTR_chest_direct_anim': 4, 'R_ring_1_direct_anim': 4, 'L_pinky_0_fk_anim': 4, 'L_ball_fk_anim': 4, 'R_hip_ikBase_anim': 3, 'L_hip_ikBase_anim_1_spacePivot_anim': 4, 'L_tailBase_ikBase_anim_1_spacePivot_anim': 4, 'CTR_bell_0_fk_anim': 4, 'L_hip_ikBase_anim_0_spacePivot_anim': 4, 'L_thumb_2_direct_anim': 4, 'R_segMid_0_ik_anim': 4, 'R_shoulder_ikBase_anim': 3, 'ring_root_anim': 4, 'L_thumb_1_fk_anim': 4, 'R_tailTip_direct_anim': 4, 'R_ponyTail_segMid_0_ik_anim': 4, 'CTR_head_ik_anim': 3, 'L_elbow_ikPole_anim_0_spacePivot_anim': 4, 'CTR_pelvis_0_direct_anim': 4, 'R_clav_direct_anim': 4, 'L_tail_1_direct_anim': 4, 'CTR_BCK_tailTip_ik_anim': 4, 'R_pouch_0_ik_anim_1_spacePivot_anim': 4, 'L_pinky_settings_anim': 4, 'L_ponyTail_segMid_0_ik_anim': 4, 'R_arm_limbRoot_anim': 4, 'L_tail_2_direct_anim': 4, 'R_shoulder_direct_anim': 4, 'bell_root_anim': 4, 'L_pinky_2_fk_anim': 4, 'L_knee_seg_anim': 4, 'head_root_anim': 4, 'CTR_BCK_tailBase_ikBase_anim_0_spacePivot_anim': 4, 'L_knee_ikPole_anim': 3, 'L_ring_2_direct_anim': 4, 'L_tailTip_direct_anim': 4, 'R_shoulder_ikBase_anim_0_spacePivot_anim': 4, 'R_index_2_direct_anim': 4, 'thumb_root_anim': 4, 'R_tail_2_fk_anim': 4, 'L_shoulder_ikBase_anim': 3, 'cog_anim_1_spacePivot_anim': 4, 'CTR_neck_fk_anim': 4, 'R_hip_ikBase_anim_1_spacePivot_anim': 4, 'R_clav_FK_anim': 4, 'R_ball_fk_anim': 4, 'L_ball_direct_anim': 4, 'L_ankle_ik_anim_1_spacePivot_anim': 4, 'L_clav_direct_anim': 4, 'L_leg_settings_anim': 4, 'rootMotion_anim': 0, 'CTR_BCK_tailTip_ik_anim_1_spacePivot_anim': 4, 'R_thumb_0_direct_anim': 4, 'R_hip_roll_0_direct_anim': 4, 'ponyTail_root_anim_1_spacePivot_anim': 4, 'ponyTail_root_anim_0_spacePivot_anim': 4, 'head_lookAt_anim': 2, 'R_knee_roll_0_direct_anim': 4, 'L_elbow_direct_anim': 4, 'L_index_2_fk_anim': 4, 'CTR_bell_0_ik_anim': 3, 'R_tailBase_0_direct_anim': 4, 'R_segMid_0_ik_anim_1_spacePivot_anim': 4, 'CTR_BCK_ponyTail_segMid_0_ik_anim': 4, 'CTR_chest_ik_anim': 4, 'L_ankle_seg_anim': 4, 'R_pinky_2_fk_anim': 4, 'R_ring_2_direct_anim': 4, 'R_ponyTail_segMid_0_ik_anim_1_spacePivot_anim': 4, 'CTR_bell_settings_anim': 4, 'R_thumb_0_fk_anim': 4, 'L_middle_1_fk_anim': 4, 'index_root_anim': 4, 'L_hip_ikBase_anim': 3, 'R_wrist_seg_anim': 4, 'CTR_chest_ik_anim_0_spacePivot_anim': 4, 'L_arm_settings_anim': 4, 'R_index_2_fk_anim': 4, 'R_leg_settings_anim': 4, 'L_tailBase_fk_anim': 4, 'L_middle_1_direct_anim': 4, 'R_wrist_fk_anim': 4, 'L_wrist_fk_anim': 4, 'R_knee_direct_anim': 4, 'CTR_bell_0_ikBase_anim_1_spacePivot_anim': 4, 'L_thumb_1_direct_anim': 4, 'R_arm_settings_anim': 4, 'R_pinky_1_fk_anim': 4, 'CTR_totem_3_fk_anim': 4, 'L_pinky_1_direct_anim': 4, 'L_segMid_1_ik_anim_0_spacePivot_anim': 4, 'L_knee_direct_anim': 4, 'ball_pivot_anim': 2, 'L_wrist_direct_anim': 4, 'L_thumb_settings_anim': 4, 'L_hip_roll_0_direct_anim': 4, 'L_segMid_1_ik_anim_1_spacePivot_anim': 4, 'pouch_root_anim': 4, 'L_shoulder_ikBase_anim_0_spacePivot_anim': 4, 'R_knee_seg_anim': 4, 'R_shoulder_seg_anim': 4, 'CTR_BCK_ponyTail_settings_anim': 0, 'L_ankle_ik_anim': 3, 'CTR_chest_ik_anim_1_spacePivot_anim': 4, 'CTR_totem_settings_anim': 4, 'R_pinky_2_direct_anim': 4, 'R_knee_ikPole_anim_1_spacePivot_anim': 4, 'CTR_BCK_ponyTail_segMid_0_ik_anim_0_spacePivot_anim': 4, 'L_shoulder_fk_anim': 4, 'R_tailTip_ik_anim_0_spacePivot_anim': 4, 'L_shoulder_direct_anim': 4, 'R_index_1_direct_anim': 4, 'pinky_root_anim': 4, 'L_index_settings_anim': 4, 'R_pouch_settings_anim': 4, 'R_ponyTail_segMid_0_ik_anim_0_spacePivot_anim': 4, 'CTR_neck_direct_anim': 4, 'L_ring_settings_anim': 4, 'L_pouch_0_fk_anim': 4, 'L_index_0_direct_anim': 4, 'R_tailBase_ikBase_anim': 4, 'L_pinky_1_fk_anim': 4, 'R_middle_1_direct_anim': 4, 'CTR_totem_0_direct_anim': 4, 'R_pouch_0_direct_anim': 4, 'R_ring_0_fk_anim': 4, 'L_wrist_seg_anim': 4, 'L_ponyTail_settings_anim': 0, 'L_knee_roll_0_direct_anim': 4, 'L_pinky_0_direct_anim': 4, 'CTR_totem_1_fk_anim': 4, 'R_middle_0_fk_anim': 4, 'CTR_BCK_tail_1_fk_anim': 4, 'CTR_totem_1_direct_anim': 4, 'CTR_spine_2_direct_anim': 4, 'L_hip_fk_anim': 4, 'L_index_1_direct_anim': 4, 'L_wrist_ik_anim_0_spacePivot_anim': 4, 'R_wrist_ik_anim_0_spacePivot_anim': 4, 'R_shoulder_fk_anim': 4, 'R_ankle_fk_anim': 4, 'R_tailTip_ik_anim': 4, 'R_ankle_direct_anim': 4, 'R_pinky_0_fk_anim': 4, 'L_thumb_2_fk_anim': 4, 'heel_pivot_anim': 2, 'L_middle_2_fk_anim': 4, 'R_segMid_0_ik_anim_0_spacePivot_anim': 4, 'R_elbow_ikPole_anim_1_spacePivot_anim': 4, 'R_tail_1_fk_anim': 4, 'L_middle_settings_anim': 4, 'L_middle_2_direct_anim': 4, 'R_pinky_0_direct_anim': 4, 'L_hip_direct_anim': 4, 'head_settings_anim': 4, 'R_thumb_settings_anim': 4, 'CTR_BCK_ponyTail_segMid_0_ik_anim_1_spacePivot_anim': 4, 'L_index_0_fk_anim': 4, 'R_ankle_ik_anim_0_spacePivot_anim': 4, 'R_pinky_settings_anim': 4, 'CTR_bell_0_direct_anim': 4, 'CTR_bell_0_ik_anim_0_spacePivot_anim': 4, 'R_middle_1_fk_anim': 4, 'CTR_totem_0_fk_anim': 4, 'L_ball_ik_anim': 4, 'L_tail_2_fk_anim': 4, 'R_index_settings_anim': 4, 'R_knee_ikPole_anim_0_spacePivot_anim': 4, 'L_shoulder_roll_0_direct_anim': 4, 'R_ankle_ik_anim_1_spacePivot_anim': 4, 'R_tailBase_ikBase_anim_1_spacePivot_anim': 4, 'L_pouch_0_ik_anim_0_spacePivot_anim': 4, 'CTR_totem_2_fk_anim': 4, 'R_index_1_fk_anim': 4, 'L_tailBase_ikBase_anim': 4, 'CTR_BCK_tailTip_fk_anim': 4, 'R_ring_2_fk_anim': 4, 'CTR_BCK_tailBase_ikBase_anim_1_spacePivot_anim': 4, 'master_anim': 3, 'L_elbow_roll_0_direct_anim': 4, 'L_elbow_ikPole_anim_1_spacePivot_anim': 4, 'L_arm_limbRoot_anim': 4, 'R_pouch_0_ikBase_anim_1_spacePivot_anim': 4, 'CTR_spine_1_direct_anim': 4, 'L_tailTip_ik_anim_1_spacePivot_anim': 4, 'CTR_BCK_tailTip_ik_anim_0_spacePivot_anim': 4, 'L_middle_0_direct_anim': 4, 'CTR_totem_0_fk_anim_0_spacePivot_anim': 4, 'L_pouch_settings_anim': 4, 'L_tailTip_fk_anim': 4, 'CTR_bell_0_ikBase_anim_0_spacePivot_anim': 4, 'R_segMid_1_ik_anim': 4, 'R_index_0_direct_anim': 4, 'R_segMid_1_ik_anim_1_spacePivot_anim': 4, 'CTR_BCK_tail_1_direct_anim': 4, 'CTR_BCK_tailBase_fk_anim': 4, 'R_elbow_ikPole_anim': 3, 'R_ball_hinge_ik_anim': 4, 'R_shoulder_roll_0_direct_anim': 4, 'L_thumb_0_direct_anim': 4, 'L_knee_ikPole_anim_1_spacePivot_anim': 4, 'L_ball_hinge_ik_anim': 4, 'totem_root_anim': 4, 'L_knee_fk_anim': 4, 'CTR_hips_ikBase_anim_1_spacePivot_anim': 4, 'L_tailTip_ik_anim_0_spacePivot_anim': 4, 'R_hip_ikBase_anim_0_spacePivot_anim': 4, 'L_segMid_0_ik_anim_1_spacePivot_anim': 4, 'L_tail_1_fk_anim': 4, 'R_ring_0_direct_anim': 4, 'CTR_bell_0_ik_anim_1_spacePivot_anim': 4, 'L_ring_2_fk_anim': 4, 'R_thumb_1_direct_anim': 4, 'L_knee_ikPole_anim_0_spacePivot_anim': 4, 'L_ponyTail_segMid_0_ik_anim_0_spacePivot_anim': 4, 'R_tailBase_ikBase_anim_0_spacePivot_anim': 4, 'R_elbow_fk_anim': 4, 'L_pouch_0_ikBase_anim_1_spacePivot_anim': 4, 'L_wrist_ik_anim_1_spacePivot_anim': 4, 'CTR_chest_fk_anim': 4, 'R_ring_1_fk_anim': 4, 'CTR_head_direct_anim': 4, 'R_pouch_0_ik_anim': 3, 'R_wrist_ik_anim_1_spacePivot_anim': 4, 'R_elbow_ikPole_anim_0_spacePivot_anim': 4, 'CTR_spine_1_handle_anim': 4, 'CTR_BCK_tail_2_direct_anim': 4, 'master_anim_0_spacePivot_anim': 3, 'L_elbow_ikPole_anim': 3, 'R_middle_2_direct_anim': 4, 'L_wrist_ik_anim': 3, 'inner_pivot_anim': 2, 'R_ball_ik_anim': 4, 'CTR_BCK_tailBase_ikBase_anim': 4, 'CTR_hips_ikBase_anim': 4, 'R_tail_1_direct_anim': 4} # 

d_shaders = {'base': {'ambientColor': [(0.0, 0.0, 0.0)],
                 'ambientColorB': 0.0,
                 'ambientColorG': 0.0,
                 'ambientColorR': 0.0,
                 'binMembership': None,
                 'caching': False,
                 'chromaticAberration': False,
                 'diffuse': 1.0,
                 'frozen': False,
                 'glowIntensity': 0.0,
                 'hardwareShader': [(0.0, 0.0, 0.0)],
                 'hardwareShaderB': 0.0,
                 'hardwareShaderG': 0.0,
                 'hardwareShaderR': 0.0,
                 'hideSource': False,
                 'incandescence': [(0.0, 0.0, 0.0)],
                 'incandescenceB': 0.0,
                 'incandescenceG': 0.0,
                 'incandescenceR': 0.0,
                 'isHistoricallyInteresting': 2,
                 'lightAbsorbance': 0.0,
                 'lightDataArray': {},
                 'materialAlphaGain': 1.0,
                 'matteOpacity': 1.0,
                 'matteOpacityMode': 2,
                 'mediumRefractiveIndex': 1.0,
                 'message': ['hyperShadePrimaryNodeEditorSavedTabsInfo',
                              'materialInfo21',
                              'defaultShaderList1'],
                 'nodeState': 0,
                 'objectId': 0.0,
                 'opacityDepth': 0.0,
                 'outColor': [(0.0, 0.0, 0.0)],
                 'outColorB': 0.0,
                 'outColorG': 0.0,
                 'outColorR': 0.0,
                 'outGlowColor': [(0.0, 0.0, 0.0)],
                 'outGlowColorB': 0.0,
                 'outGlowColorG': 0.0,
                 'outGlowColorR': 0.0,
                 'outMatteOpacity': [(1.0, 1.0, 1.0)],
                 'outMatteOpacityB': 1.0,
                 'outMatteOpacityG': 1.0,
                 'outMatteOpacityR': 1.0,
                 'outTransparency': [(0.0, 0.0, 0.0)],
                 'outTransparencyB': 0.0,
                 'outTransparencyG': 0.0,
                 'outTransparencyR': 0.0,
                 'pointCamera': [(1.0, 1.0, 1.0)],
                 'pointCameraX': 1.0,
                 'pointCameraY': 1.0,
                 'pointCameraZ': 1.0,
                 'primitiveId': 0,
                 'rayDepth': 0,
                 'rayDirection': [(0.0, 0.0, 1.0)],
                 'rayDirectionX': 0.0,
                 'rayDirectionY': 0.0,
                 'rayDirectionZ': 1.0,
                 'rayInstance': 0,
                 'raySampler': 0.0,
                 'reflectedColor': [(0.0, 0.0, 0.0)],
                 'reflectedColorB': 0.0,
                 'reflectedColorG': 0.0,
                 'reflectedColorR': 0.0,
                 'reflectionLimit': 1,
                 'reflectionRolloff': True,
                 'reflectionSpecularity': 1.0,
                 'reflectivity': 0.0,
                 'refractionLimit': 6,
                 'refractions': False,
                 'refractiveIndex': 1.0,
                 'shadowAttenuation': 0.5,
                 'surfaceThickness': 0.0,
                 'translucence': 0.0,
                 'translucenceDepth': 0.5,
                 'translucenceFocus': 0.5,
                 'transparency': [(0.0, 0.0, 0.0)],
                 'transparencyB': 0.0,
                 'transparencyDepth': 0.0,
                 'transparencyG': 0.0,
                 'transparencyR': 0.0,
                 'triangleNormalCamera': [(0.0, 1.0, 0.0)],
                 'triangleNormalCameraX': 0.0,
                 'triangleNormalCameraY': 1.0,
                 'triangleNormalCameraZ': 0.0,
                 'vrEdgeColor': [(0.5, 0.5, 0.5)],
                 'vrEdgeColorB': 0.5,
                 'vrEdgeColorG': 0.5,
                 'vrEdgeColorR': 0.5,
                 'vrEdgePriority': 0,
                 'vrEdgeStyle': 0,
                 'vrEdgeWeight': 0.0,
                 'vrFillObject': 0,
                 'vrHiddenEdges': False,
                 'vrHiddenEdgesOnTransparent': False,
                 'vrOutlinesAtIntersections': True,
                 'vrOverwriteDefaults': False},
 'blackDiffuse': {'ambientColor': [(0.0, 0.0, 0.0)],
                   'ambientColorB': 0.0,
                   'ambientColorG': 0.0,
                   'ambientColorR': 0.0,
                   'binMembership': None,
                   'caching': False,
                   'chromaticAberration': False,
                   'color': [(0.0, 0.0, 0.0)],
                   'colorB': 0.0,
                   'colorG': 0.0,
                   'colorR': 0.0,
                   'cosinePower': 2.0,
                   'diffuse': 0.0,
                   'frozen': False,
                   'glowIntensity': 0.0,
                   'hardwareShader': [(0.0, 0.0, 0.0)],
                   'hardwareShaderB': 0.0,
                   'hardwareShaderG': 0.0,
                   'hardwareShaderR': 0.0,
                   'hideSource': False,
                   'incandescence': [(0.0, 0.0, 0.0)],
                   'incandescenceB': 0.0,
                   'incandescenceG': 0.0,
                   'incandescenceR': 0.0,
                   'isHistoricallyInteresting': 2,
                   'lightAbsorbance': 0.0,
                   'lightDataArray': {},
                   'materialAlphaGain': 1.0,
                   'matteOpacity': 1.0,
                   'matteOpacityMode': 2,
                   'mediumRefractiveIndex': 1.0,
                   'message': ['defaultShaderList1', 'materialInfo23'],
                   'nodeState': 0,
                   'normalCamera': [(1.0, 1.0, 1.0)],
                   'normalCameraX': 1.0,
                   'normalCameraY': 1.0,
                   'normalCameraZ': 1.0,
                   'objectId': 0.0,
                   'opacityDepth': 0.0,
                   'outColor': [(0.0, 0.0, 0.0)],
                   'outColorB': 0.0,
                   'outColorG': 0.0,
                   'outColorR': 0.0,
                   'outGlowColor': [(0.0, 0.0, 0.0)],
                   'outGlowColorB': 0.0,
                   'outGlowColorG': 0.0,
                   'outGlowColorR': 0.0,
                   'outMatteOpacity': [(1.0, 1.0, 1.0)],
                   'outMatteOpacityB': 1.0,
                   'outMatteOpacityG': 1.0,
                   'outMatteOpacityR': 1.0,
                   'outTransparency': [(0.0, 0.0, 0.0)],
                   'outTransparencyB': 0.0,
                   'outTransparencyG': 0.0,
                   'outTransparencyR': 0.0,
                   'pointCamera': [(1.0, 1.0, 1.0)],
                   'pointCameraX': 1.0,
                   'pointCameraY': 1.0,
                   'pointCameraZ': 1.0,
                   'primitiveId': 0,
                   'rayDepth': 0,
                   'rayDirection': [(0.0, 0.0, 1.0)],
                   'rayDirectionX': 0.0,
                   'rayDirectionY': 0.0,
                   'rayDirectionZ': 1.0,
                   'rayInstance': 0,
                   'raySampler': 0.0,
                   'reflectedColor': [(0.0, 0.0, 0.0)],
                   'reflectedColorB': 0.0,
                   'reflectedColorG': 0.0,
                   'reflectedColorR': 0.0,
                   'reflectionLimit': 1,
                   'reflectionSpecularity': 1.0,
                   'reflectivity': 1.0,
                   'refractionLimit': 6,
                   'refractions': False,
                   'refractiveIndex': 1.0,
                   'shadowAttenuation': 0.5,
                   'specularColor': [(0.0, 0.0, 0.0)],
                   'specularColorB': 0.0,
                   'specularColorG': 0.0,
                   'specularColorR': 0.0,
                   'surfaceThickness': 0.0,
                   'translucence': 0.0,
                   'translucenceDepth': 0.5,
                   'translucenceFocus': 0.5,
                   'transparency': [(0.0, 0.0, 0.0)],
                   'transparencyB': 0.0,
                   'transparencyDepth': 0.0,
                   'transparencyG': 0.0,
                   'transparencyR': 0.0,
                   'triangleNormalCamera': [(0.0, 1.0, 0.0)],
                   'triangleNormalCameraX': 0.0,
                   'triangleNormalCameraY': 1.0,
                   'triangleNormalCameraZ': 0.0,
                   'vrEdgeColor': [(0.5, 0.5, 0.5)],
                   'vrEdgeColorB': 0.5,
                   'vrEdgeColorG': 0.5,
                   'vrEdgeColorR': 0.5,
                   'vrEdgePriority': 0,
                   'vrEdgeStyle': 0,
                   'vrEdgeWeight': 0.0,
                   'vrFillObject': 0,
                   'vrHiddenEdges': False,
                   'vrHiddenEdgesOnTransparent': False,
                   'vrOutlinesAtIntersections': True,
                   'vrOverwriteDefaults': False}}


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
    for k,d in list(d_characters.get(character).items()):
        md_char[k] = cgmMeta.asMeta('{0}:{1}'.format(character,d))
        
        
    md_dat['puppet'] = {}
    md_puppet = md_dat['puppet']
    for k,d in list(d_characters.get(mount).items()):
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
    
    for k,d in list(d_attaches.items()):
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
        except Exception as err:
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
    for m,d in list(dat.items()):
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
