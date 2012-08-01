#=================================================================================================================================================
#=================================================================================================================================================
#	position - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with distances
# 
# ARGUMENTS:
# 	rigging, nodes
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#
# FUNCTION SECTIONS:
#   1) Measure Tools - measuring distances between stuff
#   2) Positional Information - Querying positional info
#   3) Measure Rigs - Setups for continual information
#   4) Size Tools - Volume info
#   5) Proximity Tools - Finding closest x to y
#   6) returnBoundingBoxSize (meshGrp/mesh/obj)
#   
#=================================================================================================================================================
import maya.cmds as mc
import cgm
import cgm.lib

from cgm.lib import (distance,
                     dictionary,
                     lists)

def layoutByColumns(objectList,columnNumber=3,startPos = [0,0,0]):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Lays out a seies of objects in column and row format

    ARGUMENTS:
    objectList(string)
    columnNumber(int) - number of columns
    
    RETURNS:
    Nada
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #Get our sizes
    sizeXBuffer = []
    sizeYBuffer = []
    for obj in objectList:
	sizeBuffer = distance.returnBoundingBoxSize(obj)
	sizeXBuffer.append(sizeBuffer[0])
	sizeYBuffer.append(sizeBuffer[1])
	
    for obj in objectList:
	mc.move(0,0,0,obj,a=True)

    sizeX = max(sizeXBuffer) * 1.75
    sizeY = max(sizeYBuffer) * 1.75
    
    startX = startPos[0]
    startY = startPos[1]
    startZ = startPos[2]
    
    col=1
    objectCnt = 0
    #sort the list
    
    sortedList = lists.returnListChunks(objectList,columnNumber)
    bufferY = startY
    for row in sortedList:
	bufferX = startX
	for obj in row:
	    mc.xform(obj,os=True,t=[bufferX,bufferY,startZ])
	    bufferX += sizeX
	bufferY -= sizeY

	
    """
    for i in range (len(objectList)):
	row = i//columnNumber
	if col>columnNumber:
	    col=1
	#mc.xform(objectList[objectCnt],a=True,t=[((sizeX*(col+1.2))*1.5),(sizeY*row*-1.5),0])
	mc.xform(objectList[objectCnt],a=True,t=[((sizeX*(col+1.2))),(sizeY*row),0])	
	objectCnt +=1
	col+=1
    """
	
	

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Snap/Move Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def moveParentSnap (obj,target):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Snaps with a parent constraint style
    
    ARGUMENTS:
    obj(string)
    target(string)
    
    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """return stuff to transfer"""
    objTrans = mc.xform (target, q=True, ws=True, sp=True)
    objRot = mc.xform (target, q=True, ws=True, ro=True)
    mc.move (objTrans[0],objTrans[1],objTrans[2], [obj], rotatePivotRelative = True)
    mc.rotate (objRot[0], objRot[1], objRot[2], [obj], ws=True)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def movePointSnap (obj,target):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Snaps with a point constraint style
    
    ARGUMENTS:
    obj(string)
    target(string)
    
    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objTrans = mc.xform (target, q=True, ws=True, rp=True)
    mc.move (objTrans[0],objTrans[1],objTrans[2], [obj], rpr=True)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def moveOrientSnap (obj,target):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Snaps with a orient constraint style
    
    ARGUMENTS:
    obj(string)
    target(string)
    
    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objRot = mc.xform (target, q=True, ws=True, ro=True)
    mc.rotate (objRot[0], objRot[1], objRot[2], [obj], ws=True)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def aimSnapUpObject (obj,target,worldUpObject,aimVector = [0,0,1],upVector = [0,1,0]):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Snaps with a point constraint style
    
    ARGUMENTS:
    obj(string)
    target(string)
    aimVector(list)
    upVector(list)
    worldUp(list) - default is [0,1,0]
    
    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    for o in obj,target,worldUpObject:
	assert mc.objExists(o), "'%s' doesn't exist. Aborting aimSnapUpObject"%o
	
    aimVector = dictionary.validateDirectionVector(aimVector)
    upVector = dictionary.validateDirectionVector(upVector)
    
    assert type(aimVector) is list,"invalid aimVector argument"
    assert type(upVector) is list,"invalid upVector argument"
    
    aimConstraint = mc.aimConstraint([target],[obj],aimVector=aimVector,upVector = upVector,worldUpObject = worldUpObject, worldUpType='object')
    mc.delete(aimConstraint[0])
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def aimSnap (obj,target,aimVector = [0,0,1],upVector = [0,1,0],worldUp = [0,1,0]):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Snaps with a point constraint style
    
    ARGUMENTS:
    obj(string)
    target(string)
    aimVector(list)
    upVector(list)
    worldUp(list) - default is [0,1,0]
    
    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    for o in obj,target:
	assert mc.objExists(o), "'%s' doesn't exist. Aborting aimSnapUpObject"%o
	
    aimVector = dictionary.validateDirectionVector(aimVector)
    upVector = dictionary.validateDirectionVector(upVector)
    worldUp = dictionary.validateDirectionVector(worldUp)
    
    assert type(aimVector) is list,"invalid aimVector argument"
    assert type(upVector) is list,"invalid upVector argument"
    assert type(worldUp) is list,"invalid worldUp argument"
    
    aimConstraint = mc.aimConstraint([target],[obj],aimVector=aimVector,upVector = upVector,worldUpVector = worldUp, worldUpType='vector')
    mc.delete(aimConstraint[0])
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def moveAimSnap(obj,target,aimTarget,vector):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Snaps with a point constraint style
    
    ARGUMENTS:
    obj(string)
    target(string)
    aimTarget(string)
    vector(list) - [float, float, float]
    
    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    for o in obj,target,aimTarget:
	assert mc.objExists(o), "'%s' doesn't exist. Aborting aimSnapUpObject"%o
	
    vector = dictionary.validateDirectionVector(vector)

    assert type(vector) is list,"invalid vector argument"

    
    movePointSnap (obj,target)
    aimSnap (obj,aimTarget,vector)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   

def aimObjects(objList,objAim,objUp,worldUp,**kw):
    """
    Aim snap tool function for a list of objects
    
    Arg:
    objList(list) -- list of objects
    objAim(string) -- string format of aim axis. ex. 'x+'
    objUp(string) -- string format of up axis. 
    worldUp(string) -- string format of world up
    
    Kw:
    any keyword arguments for an aim constraint
    """
    worldUpType = kw.pop('worldUpType','vector')
    
    for o in objList:
	assert mc.ls(o,type = 'transform'),"'%s' doesn't have a transform, erroring out."%o	
    assert len(objList) >= 2,"moveAimObjects should only be used on lists of objects more than two items"
    
    objAim = dictionary.validateDirectionVector(objAim)
    objUp = dictionary.validateDirectionVector(objUp)
    worldUp = dictionary.validateDirectionVector(worldUp) 
    
    assert type(objAim) is list,"invalid objAim argument"
    assert type(objUp) is list,"invalid objUp argument"
    assert type(worldUp) is list,"invalid worldUp argument"
    

    pairList = lists.parseListToPairs(objList)
    
    for pair in pairList:       
        #>>> Set up constraints 
        constraintBuffer = mc.aimConstraint(pair[1],pair[0],maintainOffset = False, weight = 1,
	                                    aimVector = objAim,
	                                    upVector = objUp,
	                                    worldUpVector = worldUp,
	                                    worldUpType=worldUpType,**kw)
	mc.delete(constraintBuffer)

    #>>> For the last object in the chain
    for obj in objList[-1:]:
        constraintBuffer = mc.orientConstraint(objList[-2],obj,maintainOffset = False, weight = 1)
	mc.delete(constraintBuffer)
