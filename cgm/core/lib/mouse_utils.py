"""
------------------------------------------
mouse_utils: cgm.core.lib
Author: David Bokser
email: dbokser@cgmonks.com
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

Reference:
https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes

================================================================
"""
from ctypes import windll, Structure, c_long, byref

class Point(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def getMousePosition():
    pt = Point()
    windll.user32.GetCursorPos(byref(pt))
    return { "x": pt.x, "y": windll.user32.GetSystemMetrics(1) - pt.y}

def getMouseDown(button=1):
    if button == 1:
        return windll.user32.GetAsyncKeyState(0x01) > 1
    elif button == 2:
        return windll.user32.GetAsyncKeyState(0x02) > 1

def getScreenSize():
    user32 = windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
