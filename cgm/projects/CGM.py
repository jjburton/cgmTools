#import cgm.core.cgm_Meta as cgmMeta
#import cgm.core.cgm_RigMeta as RIGMETA
#from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.attribute_utils as ATTR
#from cgm.core.rigger.lib import rig_Utils as rUtils
#reload(rUtils)
#from cgm.core.classes import NodeFactory as NodeF
#import cgm.core.lib.distance_utils as DIST

import maya.mel as mel
import maya.cmds as mc
#import pprint

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
        
        
d_bg_presets = {'gray':{'top':[.8, .8, .8],
                        'bottom':[.2, .2, .2]},
                'dark':{'top':[0.4708999991416931, 0.4708999991416931, 0.4708999991416931],
                        'bottom':[0,0,0]},                
                'green':{'top':[0.8718000054359436, 1.0, 0.8626999855041504],
                        'bottom':[0.515299916267395, 0.710099995136261, 0.5012000203132629]},                
                'fire':{'top':[1.0, 0.7757999897003174, 0.0],
                        'bottom':[1.0000240802764893, 0.3231506049633026, 0.0]},                 
                'dust':{'top':[1.0, 1.0, 1.0],
                        'bottom':[0.710099995136261, 0.6769000291824341, 0.598699986934661]},                 
                'blue':{'top':[0.7253999710083008, 0.8101999759674072, 1.0],
                        'bottom':[0.45089995861053467, 0.6172000169754028, 1.0]},}
def setup_bgColor(mode = 'gray', reverse = False):
    
    
    if mode == 'resetAll':
        mc.displayRGBColor(rf=True)
        return
    
    d_color = d_bg_presets.get(mode)
    if not d_color:
        raise ValueError("Invalid mode: {0}".format(mode))
    
    if reverse:
        _top = d_color['bottom']
        _bottom = d_color['top']        
    else:
        _top = d_color['top']
        _bottom = d_color['bottom']
    
    mc.displayRGBColor( 'backgroundTop', _top[0],_top[1],_top[2]  )
    mc.displayRGBColor( 'backgroundBottom', _bottom[0],_bottom[1],_bottom[2]  )
    
        
    

    
    