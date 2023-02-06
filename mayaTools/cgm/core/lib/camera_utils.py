"""
------------------------------------------
camera_utils: cgm.core.lib
Author: David Bokser
email: dbokser@cgmonks.com
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
import maya.cmds as mc

def getCurrentPanel():
    panel = mc.getPanel(withFocus=True)
    
    if mc.getPanel(typeOf=panel) != 'modelPanel':
        for p in mc.getPanel(visiblePanels=True):
            if mc.getPanel(typeOf=p) == 'modelPanel':
                panel = p
                break
        
    return panel if mc.getPanel(typeOf=panel) == 'modelPanel' else None

def getCurrentCamera():   
    panel = getCurrentPanel()
        
    return mc.modelEditor(panel, query=True, camera=True) if panel else None
