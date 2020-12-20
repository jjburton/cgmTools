"""
------------------------------------------
facs_utils: cgm.core.mrs.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__MAYALOCAL = 'FACSUTILS'

import random
import re
import copy
import time
import os
import pprint

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#========================================================================

import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta

"""
from cgm.core import cgm_PuppetMeta as PUPPETMETA
import cgm.core.cgm_RigMeta as cgmRIGMETA
import cgm.core.lib.geo_Utils as GEO
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as CORERIG
import cgm.core.lib.rigging_utils as CORERIG
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.lib.node_utils as NODES
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.lib.locator_utils as LOC
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.rig.general_utils as RIGGEN
import cgm.core.lib.surface_Utils as SURF
import cgm.core.lib.string_utils as STRING
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.list_utils as LISTS
import cgm.core.classes.NodeFactory as NodeF
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
from cgm.core.classes import GuiFactory as cgmUI
from cgm.core.cgmPy import os_Utils as cgmOS
"""
d_defineScaleSpace = {'default':
                     {'R_browInAnchor': [-0.27203796475517916,
                                         0.6238101968178391,
                                         1.2374333510236686],
                      'R_browMidAnchor': [-0.653658667174884,
                                          0.6913925936975573,
                                          0.9779912439843496],
                      'R_browOutAnchor': [-0.9465948718732347,
                                          0.5201796111822148,
                                          0.09738985697345892],
                      'R_cheekAnchor': [-0.7042341563603586,
                                        -0.5122525720393405,
                                        0.2684650456302832],
                      'R_eyeAnchor': [-0.4664454973461831, 0.47394849201335276, 0.7477437370602481],
                      'R_eyeHelper': [-0.4664454973461831,
                                      0.47394849201335276,
                                      0.36138009823361006],
                      'R_irisHelper': [-0.4664454973461831,
                                       0.47394849201335276,
                                       0.7261073732859563],
                      'R_jawCornerAnchor': [-0.950633788567028,
                                            -0.33623728329366287,
                                            -1.0813987279570352],
                      'R_lipAnchor': [-0.39355193024997054,
                                      -0.43174420158682736,
                                      0.9248373401348743],
                      'R_nostrilAnchor': [-0.2267019162921641,
                                          -0.019148398268878708,
                                          1.012453966188127],
                      'R_orbitFrontAnchor': [-0.584110588628023,
                                             -0.06913725975175922,
                                             0.6340744017820076],
                      'R_orbitOutAnchor': [-0.9142144309733505,
                                           0.2493744736506649,
                                           0.18966987438668415],
                      'R_pupilHelper': [-0.4664454973461831,
                                        0.47394849201335276,
                                        0.7021528276787049],
                      'R_sideUprAnchor': [-1.167861300502792,
                                          0.6961031599648173,
                                          -0.9291068632065278],
                      'R_skullFrontAnchor': [-0.6671526189036749,
                                             0.9811429697260934,
                                             0.7234631604979681],
                      'bottomAnchor': [-2.697495005143935e-16,
                                       -1.3264335108621275,
                                       -0.1506813856165703],
                      'browAnchor': [5.117434254131581e-17, 0.5699139046335482, 1.2618197021681716],
                      'chinAnchor': [2.6107588313450947e-16,
                                     -1.0324481185790013,
                                     0.9537196153513007],
                      'mouthAnchor': [1.5005358067199381e-16,
                                      -0.4269899985046166,
                                      1.145336506112777],
                      'mouthBackAnchor': [0.01, -0.4077855432193047, -1.4417617455995324],
                      'noseAnchor': [0.004228731013136509,
                                     -0.15089260197652976,
                                     1.2286326712272913],
                      'noseTopAnchor': [5.117434254131581e-17,
                                        0.3999999999999986,
                                        1.2618197021681716],
                      'teethAnchor': [0.011000000000000001,
                                      -0.4370198371542706,
                                      0.9757351468628984],
                      'topAnchor': [4.336808689942018e-18, 0.9749907754676599, 1.1631904897590046]}
                      }
