#=================================================================================================================================================
#=================================================================================================================================================
#	batch - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for bath stuff
# 
# ARGUMENTS:
# 	rigging
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#=================================================================================================================================================

import maya.cmds as mc
from cgm.lib import guiFactory


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doFunctionOnSelected(function,**a):
    bufferList = []
    selected = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)
    for item in selected:
        bufferList.append(function(item,**a))
    mc.select(selected)

def doObjToTargetFunctionOnSelected(function,**a):
    bufferList = []
    selected = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)
    if len(selected) >=2:
        for item in selected[:-1]:
            bufferList.append(function(item,selected[-1]))
        mc.select(selected)
        return bufferList
    else:
        guiFactory.warning('You must have at least two objects selected')

def doObjOnlyFunctionOnSelected(function):
    bufferList = []
    selected = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)
    for item in selected:
        bufferList.append(function(item))
        
    mc.select(selected)
    return bufferList

def doObjOnlyFunctionOnObjectPerFrame(function,object,startFrame,endFrame):
    bufferList = []
    for f in range(startFrame,endFrame + 1):
        mc.currentTime(f)
        bufferList.append(function(object))
    return bufferList


