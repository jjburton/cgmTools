#=================================================================================================================================================
#=================================================================================================================================================
#	surfaces - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with surfaces
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
#   0.11 = 4/2/2011 - added documentation for all the scripts written during River Monsters gig
#=================================================================================================================================================

import maya.cmds as mc

from cgm.lib import rigging
from cgm.lib import distance
from cgm.lib import attributes
from cgm.lib.classes import NameFactory 
from cgm.lib import curves
from cgm.lib import position

reload(distance)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Naming Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def basicEyeJointSurfaceSetup(jointList, jointRoot, surface):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Script to rename a joint chain list
    
    ARGUMENTS:
    jointList(list) - list of joints in order
    startJointName(string) - what you want the root named
    interiorJointRootName(string) - what you want the iterative name to be
    
    RETURNS:
    newJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    baseDistance = distance.returnAverageDistanceBetweenObjectsAndRoot (jointList,jointRoot)
    controls = []
    groups = []
    
    for joint in jointList:
        """ make the control """        
        jointControl = curves.createControlCurve('circle',1)
        scaleFactor = baseDistance*.25
        mc.setAttr((jointControl+'.sx'),scaleFactor)
        mc.setAttr((jointControl+'.sy'),scaleFactor)
        mc.setAttr((jointControl+'.sz'),scaleFactor)
        position.movePointSnap(jointControl,joint)
        position.aimSnap(jointControl,jointRoot,[0,0,-1])
        mc.xform(jointControl,t=[0,0,baseDistance*.4],os=True, r=True)
        mc.makeIdentity(jointControl, apply = True, s=True)
        
        
        """ naming it """
        attributes.storeInfo(jointControl,'cgmName',joint,True)
        attributes.storeInfo(jointControl,'cgmType','controlAnim')
        jointControl = NameFactory.doNameObject(jointControl)
        controls.append(jointControl)
        
        groups.append( rigging.zeroTransformMeObject(jointControl) )
        
    for control in controls:
        indexCount = controls.index(control)
        attachAimedObjectToSurface (jointList[indexCount], surface, control, 'constrain')
    
    
        


def attachAimedObjectToSurface (obj, surface, aimObject, parent = True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Script to rename a joint chain list
    
    ARGUMENTS:
    jointList(list) - list of joints in order
    startJointName(string) - what you want the root named
    interiorJointRootName(string) - what you want the iterative name to be
    
    RETURNS:
    newJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    
    """ Make a transform group """
    surfaceLoc = locators.locMeClosestUVOnSurface(obj,surface)
    surfaceFollowGroup = rigging.groupMeObject(surfaceLoc,False)
    transformGroup = rigging.groupMeObject(obj,False)
    
    surfaceFollowGroup = mc.rename(surfaceFollowGroup,(obj+'_surfaceFollowGroup'))
    attributes.storeInfo(surfaceFollowGroup,'object',obj)  
    
    transformGroup = mc.rename(transformGroup,(obj+'_surfaceFollowTransformGroup'))
    attributes.storeInfo(transformGroup,'object',obj) 
    
    
    controlSurface = mc.listRelatives(surface,shapes=True)
    
    """ make the node """
    closestPointNode = mc.createNode ('closestPointOnSurface',name= (obj+'_closestPointInfoNode'))
    """ to account for target objects in heirarchies """
    attributes.doConnectAttr((surfaceLoc+'.translate'),(closestPointNode+'.inPosition'))
    attributes.doConnectAttr((controlSurface[0]+'.worldSpace'),(closestPointNode+'.inputSurface'))
    
    pointOnSurfaceNode = mc.createNode ('pointOnSurfaceInfo',name= (obj+'_posInfoNode'))
    """ Connect the info node to the surface """                  
    attributes.doConnectAttr  ((controlSurface[0]+'.worldSpace'),(pointOnSurfaceNode+'.inputSurface'))
    """ Contect the pos group to the info node"""
    attributes.doConnectAttr ((pointOnSurfaceNode+'.position'),(surfaceFollowGroup+'.translate'))
    attributes.doConnectAttr ((closestPointNode+'.parameterU'),(pointOnSurfaceNode+'.parameterU'))
    attributes.doConnectAttr  ((closestPointNode+'.parameterV'),(pointOnSurfaceNode+'.parameterV'))

    """ if we wanna aim """
    if aimObject != False: 
        """ make some locs """
        upLoc = locators.locMeObject(surface)
        aimLoc = locators.locMeObject(aimObject)
        attributes.storeInfo(upLoc,'cgmName',obj)
        attributes.storeInfo(upLoc,'cgmTypeModifier','up')
        upLoc = NameFactory.doNameObject(upLoc)
        
        attributes.storeInfo(aimLoc,'cgmName',aimObject)
        attributes.storeInfo(aimLoc,'cgmTypeModifier','aim')
        aimLoc = NameFactory.doNameObject(aimLoc)

        attributes.storeInfo(surfaceFollowGroup,'locatorUp',upLoc)
        attributes.storeInfo(surfaceFollowGroup,'aimLoc',aimLoc)
        #mc.parent(upLoc,aimObject)
        
        boundingBoxSize = distance.returnBoundingBoxSize(surface)
        distance = max(boundingBoxSize)*2
        
        mc.xform(upLoc,t = [0,distance,0],ws=True,r=True)
        
        attributes.doConnectAttr((aimLoc+'.translate'),(closestPointNode+'.inPosition'))

        """ constrain the aim loc to the aim object """
        pointConstraintBuffer = mc.pointConstraint(aimObject,aimLoc,maintainOffset = True, weight = 1)
        
        """ aim it """
        aimConstraintBuffer = mc.aimConstraint(aimLoc,surfaceFollowGroup,maintainOffset = True, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )

        """ aim the controller back at the obj"""
        aimConstraintBuffer = mc.aimConstraint(obj,aimLoc,maintainOffset = True, weight = 1, aimVector = [0,0,-1], upVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
        
        mc.parent(upLoc,aimObject)
    else:
        mc.delete(closestPointNode)
    
    transformGroup = rigging.doParentReturnName(transformGroup,surfaceFollowGroup)
    """finally parent it"""    
    if parent == True:
        mc.parent(obj,transformGroup)
        
    if parent == 'constrain':
        mc.parentConstraint(transformGroup,obj,maintainOffset = True)
    
    mc.delete(surfaceLoc)
    return [transformGroup,surfaceFollowGroup]
    

def attachObjectToMesh (obj, mesh, aim=False):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    Rotation not working!
    DESCRIPTION:
    Script to rename a joint chain list
    
    ARGUMENTS:
    jointList(list) - list of joints in order
    startJointName(string) - what you want the root named
    interiorJointRootName(string) - what you want the iterative name to be
    
    RETURNS:
    newJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ Make a transform group """
    surfaceFollowGroup =  mc.group (w=True, empty=True)
    originalPosGroup = rigging.groupMeObject(obj,False)
    
    surfaceFollowGroup = mc.rename(surfaceFollowGroup,(obj+'_surfaceFollowGroup'))
    attributes.storeInfo(surfaceFollowGroup,'object',obj)  
    
    
    """ make the closest point node """
    closestPointNode = mc.createNode ('closestPointOnMesh')
    controlSurface = mc.listRelatives(mesh,shapes=True)
    
    """ to account for target objects in heirarchies """
    attributes.doConnectAttr((originalPosGroup+'.translate'),(closestPointNode+'.inPosition'))
    attributes.doConnectAttr((controlSurface[0]+'.worldMesh'),(closestPointNode+'.inMesh'))
    attributes.doConnectAttr((controlSurface[0]+'.worldMatrix'),(closestPointNode+'.inputMatrix'))

    """ Contect the locator to the info node"""
    attributes.doConnectAttr ((closestPointNode+'.position'),(surfaceFollowGroup+'.translate'))
    
    
    mc.normalConstraint(mesh,surfaceFollowGroup,worldUpType='object',worldUpObject=originalPosGroup)
    mc.parentConstraint(mesh,originalPosGroup, maintainOffset = True)
    return [surfaceFollowGroup]
