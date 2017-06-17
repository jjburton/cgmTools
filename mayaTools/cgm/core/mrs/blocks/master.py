"""
------------------------------------------
cgm.core.mrs.blocks.simple.master
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
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as RIG


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPUPPET
#>>>Block data =================================================================================
__version__ = 'alpha.06142017'

l_attrsStandard = ['proxyType','hasRootJoint']
d_attrsToMake = {'puppetName':'string'}

d_defaultSettings = {'version':__version__,
                     'puppetName':'NotBatman',
                     'proxyType':1}


def build_rigBlock(self,size = 1):
    """
    Creation should entail curve creation
    """
    #_mObj = cgmPUPPET.cgmRigBlock(None)
    _crv = CURVES.create_controlCurve(None,shape='circleArrow',direction = 'y+', size = size)
    RIG.shapeParent_in_place(self.mNode,_crv,False)

    return True

def build_skeleton(self):
    pass

def rig():
    pass



 








