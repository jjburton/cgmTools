"""
------------------------------------------
================================================================
"""
import random
import re
import copy
import time
import os
import pprint
import sys

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

import maya.cmds as mc
import maya.mel as mel
# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
import cgm.core.mrs.lib.post_utils as MRSPOST
reload(MRSPOST)

def mobileToon():
    # ================================================================================
    # Control Shapes
    # ================================================================================
    #d_shapes = {'head_root_anim':{'noMirror': True, 'shape':'loftDiamond', 'size' : 60},
    #            }
    #MRSPOST.setup_shapes(d_shapes)
    
    
    # ================================================================================
    # Values
    # ================================================================================
    d_values = {'spine_cog_anim':{'spine_rigRibbon_aimFactor_0':1,
                                  'spine_rigRibbon_aimFactor_1':1,
                                  'spine_rigRibbon_aimFactor_2':.25,
                                  'spine_rigRibbon_outFactor_0':.25,
                                  'spine_rigRibbon_outFactor_1':1,
                                  'spine_rigRibbon_outFactor_2':.25,
                                  'blendParam':1,
                                  'visScaleRoot':False,
                                  },
                'settingsControl':{'geo':'lock', 'proxy':'off'},
                'head_fk_anim':{'orientTo':'spine_cog'},
                'head_ik_anim':{'orientTo':'spine_cog'},                
                }    
    MRSPOST.setup_defaults(d_values)
    
    # ================================================================================
    # Object Sets
    # ================================================================================
    """
    l_toDelete = ['leafExample_1_sknJnt',
                  'leafExample_2_sknJnt']
    
    
    for objectSet in ['delete_tdSet']:
        mSet = cgmMeta.cgmObjectSet(objectSet)
        mSet.extend(l_toDelete)
        """
    
    # ================================================================================
    # Limits
    # ================================================================================
    """
    d_limits = {'HND_knee_fullChain_frame':{'rz':(0,0), 'erz': (1,1)},
                'HND_knee_ik_frame':{'rz':(0,0), 'erz': (1,1), 'rx':(-30,0),'erx':(1,0)}, 
                
                'FRNT_elbow_fullChain_frame':{'rz':(0,0), 'erz': (1,1)},
                'FRNT_elbow_ik_frame':{'rz':(0,0), 'erz': (1,1)},
                'FRNT_wrist_fullChain_frame':{'rx':(0,0), 'erx':(1,0)},
                }
    MRSPOST.setup_limits(d_limits)"""


    # ================================================================================
    # SDK
    # ================================================================================
    
    d_fingers = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
                 'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
                 'roll':{
                     0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                     'd':'rx', '+d':10.0, '-d':-10.0, '+':90, '-':-40},
                 'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
                 0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
                 1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
                 2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
                 3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
                 4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky
    
    for s in ['L','R']:
        ml = []
        for t in ['thumb','index','middle','ring','pinky']:
            ml.append(cgmMeta.asMeta("{}_{}_limb_part".format(s,t)))
        print [mObj.p_nameShort for mObj in ml]
        MRSPOST.SDK_wip(ml,d_attrs=d_fingers)
            
    # ================================================================================
    # Deformation
    # ================================================================================
    #MRSPOST.defJointFix('rootMotion_jnt')
    
    # ================================================================================
    # Material
    # ================================================================================

    # ================================================================================
    # Space Switch
    # ================================================================================ 

    # ================================================================================
    # Create
    # ================================================================================   

    
    # ================================================================================
    # Imports
    # ================================================================================
    
    
    # ================================================================================
    # SkinClusters/Blendshapes
    # ================================================================================    

def gameToon():
    # ================================================================================
    # Control Shapes
    # ================================================================================
    #d_shapes = {'head_root_anim':{'noMirror': True, 'shape':'loftDiamond', 'size' : 60},
    #            }
    #MRSPOST.setup_shapes(d_shapes)
    
    
    # ================================================================================
    # Values
    # ================================================================================
    d_values = {#'head_settings_anim': {'visRoot':True},
            'settingsControl':{'geo':'lock', 'proxy':'off'},
            'head_fk_anim':{'orientTo':'spine_cog'},
            'head_root_anim':{'orientTo':'spine_cog'},

            'L_shoulder_fk_anim': {'ro': 'yzx'},
            'L_elbow_fk_anim': {'ro': 'yzx'},
            'L_wrist_fk_anim': {'ro': 'yzx'},
            'R_shoulder_fk_anim': {'ro': 'yzx'},
            'R_elbow_fk_anim': {'ro': 'yzx'},
            'R_wrist_fk_anim': {'ro': 'yzx'},                

            'hips_ikBase_anim': {'ro': 'xyz'},
            'spine_1_fk_anim': {'ro': 'xyz'},
            'spine_2_fk_anim': {'ro': 'xyz'},
            'chest_fk_anim': {'ro': 'xyz'},
            
            'L_wrist_ik_anim': {'space': 'chest',
                                'ro':'yzx'},
            'R_wrist_ik_anim': {'space': 'chest',
                                'ro':'yzx'},
            
            'L_ankle_ik_anim': {'ro':'zxy'},
            'R_ankle_ik_anim': {'ro':'zxy'},            


            'spine_midIK_0_ik_anim': {'space': 'spine_cog'},

            'chest_ik_anim': {'ro': 'xyz'},
            'hips_ikBase_anim': {'ro': 'xyz'},
            'settingsControl':{'geo':'lock', 'proxy':'off'},


            'spine_cog_anim':{'spine_rigRibbon_aimFactor_0':.25,
                                  'spine_rigRibbon_aimFactor_1':1,
                                  'spine_rigRibbon_aimFactor_2':.25,
                                  'spine_rigRibbon_aimFactor_3':0,
                                  'spine_rigRibbon_outFactor_0':.25,
                                  'spine_rigRibbon_outFactor_1':1,
                                  'spine_rigRibbon_outFactor_2':.75,
                                  'spine_rigRibbon_outFactor_2':.5,
                                  'blendParam':1,
                                  'visScaleRoot':False,
                                  },                   

            'L_arm_settings_anim': {'elbow_seg_1_out_factor_0': 1.0,
                                    'elbow_seg_1_out_factor_1': 1.0,
                                     'elbow_seg_1_out_factor_2': 0.0,
                                     'elbow_seg_1_segScale': 1.0,
                                     'shoulder_seg_0_out_factor_0': 1.0,
                                     'shoulder_seg_0_out_factor_1': 1.0,
                                     'shoulder_seg_0_out_factor_2': 1.0,
                                     'shoulder_seg_0_segScale': 1.0},
            'R_arm_settings_anim': {'elbow_seg_1_out_factor_0': 1.0,
                                    'elbow_seg_1_out_factor_1': 1.0,
                                     'elbow_seg_1_out_factor_2': 0.0,
                                     'elbow_seg_1_segScale': 1.0,
                                     'shoulder_seg_0_out_factor_0': 1.0,
                                     'shoulder_seg_0_out_factor_1': 1.0,
                                     'shoulder_seg_0_out_factor_2': 1.0,
                                     'shoulder_seg_0_segScale': 1.0},
            'R_leg_settings_anim': {'ankle_seg_2_out_factor_0': 1.0,
                                          'ankle_seg_2_out_factor_1': 1.0,
                                           'ankle_seg_2_out_factor_2': 0.0,
                                           'ankle_seg_2_segScale': 1.0,
                                           'hip_seg_0_out_factor_0': 1.0,
                                           'hip_seg_0_out_factor_1': 1.0,
                                           'hip_seg_0_out_factor_2': 1.0,
                                           'hip_seg_0_segScale': 1.0,
                                           'knee_seg_1_out_factor_0': 1.0,
                                           'knee_seg_1_out_factor_1': 1.0,
                                           'knee_seg_1_out_factor_2': 1.0,
                                           'knee_seg_1_segScale': 1.0},
            'L_leg_settings_anim': {'ankle_seg_2_out_factor_0': 1.0,
                                          'ankle_seg_2_out_factor_1': 1.0,
                                           'ankle_seg_2_out_factor_2': 0.0,
                                           'ankle_seg_2_segScale': 1.0,
                                           'hip_seg_0_out_factor_0': 1.0,
                                           'hip_seg_0_out_factor_1': 1.0,
                                           'hip_seg_0_out_factor_2': 1.0,
                                           'hip_seg_0_segScale': 1.0,
                                           'knee_seg_1_out_factor_0': 1.0,
                                           'knee_seg_1_out_factor_1': 1.0,
                                           'knee_seg_1_out_factor_2': 1.0,
                                           'knee_seg_1_segScale': 1.0},
            }        
 
    MRSPOST.setup_defaults(d_values)
    
    # ================================================================================
    # Object Sets
    # ================================================================================
    """
    l_toDelete = ['leafExample_1_sknJnt',
                  'leafExample_2_sknJnt']
    
    
    for objectSet in ['delete_tdSet']:
        mSet = cgmMeta.cgmObjectSet(objectSet)
        mSet.extend(l_toDelete)
        """
    
    # ================================================================================
    # Limits
    # ================================================================================
    """
    d_limits = {'HND_knee_fullChain_frame':{'rz':(0,0), 'erz': (1,1)},
                'HND_knee_ik_frame':{'rz':(0,0), 'erz': (1,1), 'rx':(-30,0),'erx':(1,0)}, 
                
                'FRNT_elbow_fullChain_frame':{'rz':(0,0), 'erz': (1,1)},
                'FRNT_elbow_ik_frame':{'rz':(0,0), 'erz': (1,1)},
                'FRNT_wrist_fullChain_frame':{'rx':(0,0), 'erx':(1,0)},
                }
    MRSPOST.setup_limits(d_limits)"""


    # ================================================================================
    # SDK
    # ================================================================================
    
    d_fingers = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
                 'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
                 'roll':{
                     0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                     'd':'rx', '+d':10.0, '-d':-10.0, '+':90, '-':-40},
                 'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
                 0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
                 1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
                 2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
                 3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
                 4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky
    
    for s in ['L','R']:
        ml = []
        for t in ['thumb','index','middle','ring','pinky']:
            ml.append(cgmMeta.asMeta("{}_{}_limb_part".format(s,t)))
        print [mObj.p_nameShort for mObj in ml]
        MRSPOST.SDK_wip(ml,d_attrs=d_fingers)
            
    # ================================================================================
    # Deformation
    # ================================================================================
    #MRSPOST.defJointFix('rootMotion_jnt')
    
    # ================================================================================
    # Material
    # ================================================================================

    # ================================================================================
    # Space Switch
    # ================================================================================ 

    # ================================================================================
    # Create
    # ================================================================================   

    
    # ================================================================================
    # Imports
    # ================================================================================
    
    
    # ================================================================================
    # SkinClusters/Blendshapes