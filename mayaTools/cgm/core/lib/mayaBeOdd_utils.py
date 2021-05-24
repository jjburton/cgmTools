"""
Maya be Odd
Josh Burton 
www.cgmonks.com

For use with meta instance data
"""
__MAYALOCAL = 'MAYABEODD'

# From Python =============================================================
import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core import cgm_Meta as cgmMeta

from cgm.lib import attributes
from cgm.core.lib import attribute_utils as coreAttr

#>>> Utilities
#===================================================================
def killRoguePanel(method = ''):
    """
    hattip:
    https://forums.autodesk.com/t5/maya-forum/error-cannot-find-procedure-quot-dcf-updateviewportlist-quot/td-p/8342659?fbclid=IwAR3IhCeCqzZvEREmxo5eA7ECQu9n82MEN_vqCFTmdySwNNbsrYREdDcv_QA
    """
    #['DCF_updateViewportList', 'CgAbBlastPanelOptChangeCallback']
    EVIL_METHOD_NAMES = cgmValid.listArg(method)
    
    capitalEvilMethodNames = [name.upper() for name in EVIL_METHOD_NAMES]
    modelPanelLabel = mel.eval('localizedPanelLabel("ModelPanel")')
    processedPanelNames = []
    panelName = mc.sceneUIReplacement(getNextPanel=('modelPanel', modelPanelLabel))
    while panelName and panelName not in processedPanelNames:
        editorChangedValue = mc.modelEditor(panelName, query=True, editorChanged=True)
        parts = editorChangedValue.split(';')
        newParts = []
        changed = False
        for part in parts:
            for evilMethodName in capitalEvilMethodNames:
                if evilMethodName in part.upper():
                    changed = True
                    break
            else:
                newParts.append(part)
        if changed:
            mc.modelEditor(panelName, edit=True, editorChanged=';'.join(newParts))
        processedPanelNames.append(panelName)
        panelName = mc.sceneUIReplacement(getNextPanel=('modelPanel', modelPanelLabel))
        log.info("Processed: {0}".format(panelName))
        


def cleanFile():
    kill_unknownPlugins()
    kill_rendererNodes()
    
def kill_unknownPlugins():
    """
    Hat tip to Ryan Porter
    """
    for each in mc.unknownPlugin(q=1, l=1) or []:
        mc.unknownPlugin(each, remove=True)
        
    
def kill_rendererNodes():
    for o in ['TurtleDefaultBakeLayer']:
        if mc.objExists(o):
            cgmMeta.asMeta(o).delete()
            print "killed node: " + o
            
def kill_outlinerSelectCommands():
    #https://forums.autodesk.com/t5/maya-forum/error-lt-function-selcom-at-0x7f29c5c04aa0-gt/td-p/9052236
    for _editor in mc.lsUI(editors=True):
        if not mc.outlinerEditor(_editor, query=True, exists=True):
            continue
        _sel_cmd = mc.outlinerEditor(_editor, query=True, selectCommand=True)
        if not _sel_cmd:
            continue
        print _editor, _sel_cmd
        mc.outlinerEditor(_editor, edit=True, selectCommand='pass')    


        