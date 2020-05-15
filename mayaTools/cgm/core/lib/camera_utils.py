"""
------------------------------------------
mouse_utils: cgm.core.lib
Author: David Bokser
email: dbokser@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
import maya.cmds as mc

from ctypes import windll, Structure, c_long, byref

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def getScreenSize():
    user32 = windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def getMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return { "x": pt.x, "y": windll.user32.GetSystemMetrics(1) - pt.y}

def getCurrentCamera():   
    panel = mc.getPanel(withFocus=True)
    
    if mc.getPanel(typeOf=panel) != 'modelPanel':
        for p in mc.getPanel(visiblePanels=True):
            if mc.getPanel(typeOf=p) == 'modelPanel':
                panel = p
                break
        
    return mc.modelEditor(panel, query=True, camera=True) if mc.getPanel(typeOf=panel) == 'modelPanel' else None
