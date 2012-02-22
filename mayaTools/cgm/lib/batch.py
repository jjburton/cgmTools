#=================================================================================================================================================
#=================================================================================================================================================
#	batch - a part of rigger
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for bath stuff
# 
# REQUIRES:
# 	rigging
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru David Bokser) - jjburton@gmail.com
#	http://www.joshburton.com
# 	Copyright 2011 Josh Burton - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#=================================================================================================================================================

import maya.cmds as mc
from cgm.lib import guiFactory


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doFunctionOnSelected(function,**a):
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    for item in selected:
        bufferList.append(function(item,**a))

def doObjToTargetFunctionOnSelected(function,**a):
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    if len(selected) >=2:
        for item in selected[:-1]:
            print ('on ' + item)
            bufferList.append(function(item,selected[-1]))
        return bufferList
    else:
        guiFactory.warning('You must have at least two objects selected')

def doObjOnlyFunctionOnSelected(function):
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    for item in selected:
        bufferList.append(function(item))
    return bufferList

def doObjOnlyFunctionOnObjectPerFrame(function,object,startFrame,endFrame):
    bufferList = []
    for f in range(startFrame,endFrame + 1):
        mc.currentTime(f)
        bufferList.append(function(object))
    return bufferList


