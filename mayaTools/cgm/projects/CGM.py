import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgm_RigMeta as RIGMETA
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.attribute_utils as ATTR
from cgm.core.rigger.lib import rig_Utils as rUtils
#reload(rUtils)
from cgm.core.classes import NodeFactory as NodeF
import cgm.core.lib.distance_utils as DIST

import maya.mel as mel
import maya.cmds as mc
import pprint

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#-------------------------------------------------------------------


def setup_forCapture(state = 1):
    mel.eval('PreferencesWindow;')
    mel.eval('preferencesWnd "Display";')        
    
    if state:
        mel.eval('ActivateViewport20;')        
    else:
        mel.eval('setRendererInModelPanel base_OpenGL_Renderer modelPanel4;')
        
    ATTR.set('hardwareRenderingGlobals.lineAAEnable',state)
    ATTR.set('hardwareRenderingGlobals.multiSampleEnable',state)
    
    if state:
        mel.eval('updateLineWidth 2;')
    else:
        mel.eval('updateLineWidth 1;')
    

    
    