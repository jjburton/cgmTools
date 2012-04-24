#=================================================================================================================================================
#=================================================================================================================================================
#	nodes - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for skinning
# 
# REQUIRES:
# 	Maya
#   distance
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#
# FUNCTION KEY:
#   1) locMe - creates locators at the pivots of every object selected - matching translation, rotation and rotation order
#
#=================================================================================================================================================
import maya.cmds as mc

from cgm.lib import search
from cgm.lib import attributes
from cgm.lib.classes import NameFactory


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Blendshapes
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def insertMulitiplyDivideBridge(drivenAttribute,newDriver):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Inserts a multiplyDivide bridge node for help taking care of compound scales
    
    1) get the driver
    2) create node
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>> Get variables
    driverAttribute = attributes.returnDriverAttribute(drivenAttribute)
    print driverAttribute
    
    driverBuffer = driverAttribute.split('.')
    drivenBuffer = drivenAttribute.split('.')
    
    #>>> Create
    bridgeMDNode = createNamedNode ((driverBuffer[0]+'_to_'+newDriver),'multiplyDivide')
    
    #>>> Connect
    attributes.doConnectAttr(driverAttribute,(bridgeMDNode+'.input1'))
    attributes.doConnectAttr(newDriver,(bridgeMDNode+'.input2'))
    
    attributes.doConnectAttr((bridgeMDNode+'.output'),drivenAttribute)
    """
    mc.connectAttr(('time1.outTime'),(speedMDNode+'.input1X'))
    mc.connectAttr(speedAttr,(speedMDNode+'.input2.input2X'))
    mc.connectAttr((speedMDNode+'.outputX'),(waveDeformer+'_offset.input'))
    """

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Blendshapes
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def createPoseBuffer(name,poseList):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the colors used on the shapes of a curve as a list in order
    of volume used

    REQUIRES:
    curve(string
    
    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    returnList = []
    
    poseBuffer = mc.group( em=True)
    attributes.storeInfo(poseBuffer,'cgmName', name)
    attributes.storeInfo(poseBuffer,'cgmType', 'poseBuffer')
    poseBuffer = NameFactory.doNameObject(poseBuffer)
    returnList.append(poseBuffer)
    
    returnList.append(attributes.addFloatAttrsToObj(poseBuffer, poseList,dv = 0))
    
    attributes.doSetLockHideKeyableAttr(poseBuffer,True,False,False)
    
    return returnList




def blendShapeNodeToPoseBuffer(name,blendShapeNode,doConnect = True, transferConnections = True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Takes the attributes of a blendshape, adds them as attributes, connects them and transfers
    any driver should you choose

    REQUIRES:
    name(string)
    blendShapeNode(string)
    doConnect(bool) - (True) - if you want to connect the atributes to the new ones
    transferConnections(bool) - (True) - if you wanna transfer exisiting connections or not
    
    
    RETURNS:
    returnList(list) - [poseBuffer(string),newAttrs(list)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    """ first get the blendshape attrs """
    blendShapeAttrs = search.returnBlendShapeAttributes(blendShapeNode)
    
    returnList =  createPoseBuffer(name,blendShapeAttrs)
    
    newAttrs = returnList[1]
    
    if doConnect == True:
        for attr in blendShapeAttrs:
            listIndex = blendShapeAttrs.index(attr)
            attributes.doConnectAttr((newAttrs[listIndex]),(blendShapeNode+'.'+attr),False,transferConnections)
    
    
    return returnList

# ====================================================================================================================
# FUNCTION - 1
#
# SIGNATURE:
#	createNode (name, type)
#
# DESCRIPTION:
#   Pass a node name (sans suffix) along with the node type into it and return a node created
# 
# REQUIRES:
# 	name - name for the node (sans suffix)
# 	type - the node type
#
# RETURNS:
#	Name of the created node
#
# ====================================================================================================================
def createNamedNode (nodeName, type):
    nodeSuffixDictionary = {'curveInfo':'crvInfo','multiplyDivide':'mdNode','pointOnSurfaceInfo':'posInfoNode','closestPointOnSurface':'cPntOnSurfNode','closestPointOnMesh':'cPntOnMeshNode','plusMinusAverage':'pmAvNode','frameCache':'fCacheNode'}
    utilityNodeList = ['plusMinusAverage']
    if not type in nodeSuffixDictionary:
        print (type + ' is not a node type or is not in the dictionary. Expected one of the following:')
        print nodeSuffixDictionary
        return False
    else:  
        suffix = nodeSuffixDictionary[type]
        if type in utilityNodeList:
            createdNode = mc.shadingNode (type,name= (nodeName+'_'+suffix),asUtility=True)
        else:
            createdNode = mc.createNode (type,name= (nodeName+'_'+suffix),)
    return createdNode




def returnConnectedClosestPointOnMeshNode (targetObj, mesh):
    """ make the closest point node """
    closestPointNode = createNamedNode((targetObj+'_to_'+mesh),'closestPointOnMesh')
    controlSurface = mc.listRelatives(mesh,shapes=True)
    
    """ to account for target objects in heirarchies """
    attributes.doConnectAttr((targetObj+'.translate'),(closestPointNode+'.inPosition'))
    attributes.doConnectAttr((controlSurface[0]+'.worldMesh'),(closestPointNode+'.inMesh'))    
    
    return closestPointNode


# ====================================================================================================================
# FUNCTION - 2
#
# SIGNATURE:
#	offsetCycleSpeedControlNodeSetup (waveDeformer,speedAttr,startFrameAttr,cycleAttr,offsetLength,direction)
#
# DESCRIPTION:
#   roviding the proper variables, creates a nodal setup to control the speed of an offset animation
# 
# REQUIRES:
# 	waveDeformer - the object with the .offset attribute to drive
# 	speedAttr -  the attribute you want to drive speed (float)
# 	cycleLength - how many frames you want the cycle to happen over (integer)
# 	offset - the offset length for a full cycle (usually 10 or -10)
#
# RETURNS:
#	nothing
#
# ====================================================================================================================
def offsetCycleSpeedControlNodeSetup (waveDeformer,speedAttr,cycleLength,offset):
    """ Providing the proper variables, creates a nodal setup to control the speed of an offset animation """
    """ Create the nodes """
    speedMDNode = createNamedNode ('speedMult','multiplyDivide')
    offsetNode = createNamedNode ('offset','multiplyDivide')
    #mc.setAttr ((frameCountDivNode+'.operation'),2)
    """ create the cycle """
    mc.setKeyframe ((waveDeformer+'.offset'), time=0, value = 0, inTangentType = 'spline', outTangentType = 'spline')
    mc.setKeyframe ((waveDeformer+'.offset'), time=cycleLength, value = (offset*.99), inTangentType = 'linear', outTangentType = 'linear')
    mc.setInfinity ((waveDeformer+'.offset'),pri = 'linear', poi = 'linear')
    """ Connect the nodes """
    mc.connectAttr(('time1.outTime'),(speedMDNode+'.input1X'))
    mc.connectAttr(speedAttr,(speedMDNode+'.input2.input2X'))
    mc.connectAttr((speedMDNode+'.outputX'),(waveDeformer+'_offset.input'))
    

