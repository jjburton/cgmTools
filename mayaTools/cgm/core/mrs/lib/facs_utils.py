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
                      {'R_cheekAnchor': [-0.7042341563603586,
                                         -0.512252572039344,
                                         0.2684650456302836],
                       'R_eyeAnchor': [-0.4664454973461831, 0.47394849201335276, 0.7477437370602481],
                       'R_jawCornerAnchor': [-0.950633788567028,
                                             -0.33623728329366287,
                                             -1.0813987279570352],
                       'R_lipAnchor': [-0.39355193024997076, -0.4317442015868238, 0.924837340134875],
                       'R_nostrilAnchor': [-0.22670191629216413,
                                           -0.01914839826888226,
                                           1.012453966188127],
                       'R_orbitFrontAnchor': [-0.584110588628023,
                                              -0.06913725975175922,
                                              0.7912417796255561],
                       'R_sideUprAnchor': [-1.167861300502792,
                                           0.6961031599648173,
                                           -0.9291068632065278],
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
                       'noseAnchor': [0.00422873101313651, -0.15089260197652976, 1.2286326712272913],
                       'noseTopAnchor': [5.117434254131581e-17,
                                         0.3999999999999986,
                                         1.2618197021681716],
                       'topAnchor': [4.336808689942018e-18, 0.9749907754676599, 1.1631904897590046]}
                      }
