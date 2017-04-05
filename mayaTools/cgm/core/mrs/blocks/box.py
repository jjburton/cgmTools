"""
------------------------------------------
cgm.core.mrs.blocks.box
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""

# From Python =============================================================
import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================

#>>>Block data
__version__ = 'alpha.03232017'

d_skeletonSetup = {'mode':'vectorCast',
                   'targetsMode':'msgList',
                   'targets':'jointPlacers'}

d_attrsToMake = {'joints':'int',
                 'proxyType':'none:castMesh',
                 'buildBank':'bool'} 

d_defaultSettings = {'version':__version__,
                     'joints':1,
                     'blockType':__name__.split('.')[-1],
                     'buildBank':True,'direction':'center',
                     'proxyType':'castMesh'}

#d_helperSettings = {'iris':{'plug':'irisHelper','check':'buildIris'},
                    #'pupil':{'plug':'pupilHelper','check':'buildIris'}}

#These lists should be set up per rigblock as a way to get controls from message links
#auto validate controlLinks as messageSimple attrs
_l_controlLinks = ['helperBase','helperTop','helperOrient']
_l_controlmsgLists = ['jointPlacers','loftTargets']
#_l_proxyLoftLinks = ['helperBase','helperTop']#...each of these in turn must have a loftCurve link


#>>> Skeleton
#=========================================================================================================
__l_jointAttrs__ = ['rigJoints','influenceJoints','fkJoints','ikJoints','blendJoints']   
__d_preferredAngles__ = {'shoulder':[0,-10,10],'elbow':[0,-10,0]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
__d_controlShapes__ = {'shape':['segmentIK','controlsFK','midIK','settings','hand']}


def is_valid(root = None):
    return True
    raise Exception,'test'

def build_joints(root=None,module=None):
    """
    Core rig block factory. Runs processes for rig blocks.
    """ 
    _str_func = 'build_joints'
    
    
    
    








