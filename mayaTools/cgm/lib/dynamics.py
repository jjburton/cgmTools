#=================================================================================================================================================
#=================================================================================================================================================
#	cgmDynamicsTools - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for finding stuff
# 
# ARGUMENTS:
# 	Maya
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
#   1) ????
#   2) ????
#   3) ????
#   
#=================================================================================================================================================

import maya.cmds as mc

from cgm.lib import joints
from cgm.lib import search
from cgm.lib import attributes

import maya.OpenMaya as OpenMaya
import maya.mel as mel


# ====================================================================================================================
# FUNCTION - 1
#
# SIGNATURE:
#	makeChainsDynamic(startJoints,name)
#
# DESCRIPTION:
#   Makes input joint chains dynamic and names things properly
# 
# ARGUMENTS:
# 	startJoints - list of start joints
#   name - base name for the system
#
# RETURNS:
#	return[0] = list of follicles
#   return[1] = list of handles created
#   return[2] = hairSystem shape node name
#
# ====================================================================================================================

def makeChainsDynamic(startJoints,name):
    """ Makes input joint chains dynamic and names things properly  """
    curves = []
    startNames=[]
    for start in startJoints:
        curveBuffer= (joints.createCurveFromJoints(start))
        jointCount = search.returnJointHeirarchyCount(start)
        mc.rebuildCurve ((curveBuffer), ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=(jointCount*1.5), d=1, tol=5)
        curves.append(curveBuffer)
        startNames.append(start)
    """ see if we have enough points """
    #create test
    for crv in curves:
        """ rebuild curve """
        mc.rebuildCurve ((crv), ch=0, rpo=1, rt=0, end=0, kr=0, kcp=0, kep=1, kt=0, s=(20), d=1, tol=5)
    """ create hairsystem """
    mc.select (curves)
    mel.eval('makeCurvesDynamicHairs 0 0 1')
    #>>>>>>>>>>>>>>>>>>>>>>Get data and name stuff right
    """ return useful info on the curves since the maya command returns jack squat"""
    crvsInfo =[]
    follicles = []
    cnt=0
    for crv in curves:
        crvInfo = []
        follicleOldNameBuffer = mc.listRelatives (crv,parent=True)
        follicleBuffer=mc.rename(follicleOldNameBuffer[0],(startNames[cnt]+'_follicle'))
        shapeBuffer = mc.listRelatives (follicleBuffer,shapes=True)
        inputCurveOldNameBuffer = attributes.returnDriverObject(shapeBuffer[0]+'.startPosition')
        inputCurveBuffer = mc.rename(inputCurveOldNameBuffer,(startNames[cnt]+'_input_crv'))
        outputCurveShapeBuffer = attributes.returnDrivenObject(shapeBuffer[0]+'.outCurve')
        outputCurveOldNameBuffer = mc.listRelatives (outputCurveShapeBuffer,parent=True)
        outputCurveBuffer = mc.rename(outputCurveOldNameBuffer,(startNames[cnt]+'_output_crv'))
        hairSystemOldShapeNameBuffer = attributes.returnDriverObject(shapeBuffer[0]+'.currentPosition')
        hairSystemOldNameBuffer = mc.listRelatives (hairSystemOldShapeNameBuffer,parent=True)
        hairSystemBuffer = mc.rename(hairSystemOldNameBuffer,(name+'_hairSystem'))
        crvInfo.append(follicleBuffer)
        follicles.append(follicleBuffer)
        crvInfo.append(shapeBuffer[0])
        crvInfo.append(inputCurveBuffer)
        crvInfo.append(outputCurveBuffer)
        crvInfo.append(hairSystemBuffer)
        cnt+=1
        crvsInfo.append(crvInfo)
    """ Fix a few group names  """
    oldFolicleGroupBuffer = (mc.listRelatives (crvInfo[0],parent=True))
    folicleGroup = mc.rename(oldFolicleGroupBuffer[0],(name+'follicles_grp'))
    oldOutputGroupBuffer = (mc.listRelatives (crvInfo[3],parent=True))
    outputCrvsGroup = mc.rename(oldOutputGroupBuffer[0],(name+'OutputCrvs_grp'))
    print crvsInfo
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>> set follicle settings
    for follicle in  follicles:
        """lock to base"""
        mc.setAttr ((follicle+'Shape.pointLock'),1)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>> set hair system settings
    hairSystem = crvInfo[4]
    mc.setAttr ((hairSystem+'Shape.drag'),.675)
    mc.setAttr ((hairSystem+'Shape.motionDrag'),.126)
    mc.setAttr ((hairSystem+'Shape.startCurveAttract'),.046)
    mc.setAttr ((hairSystem+'Shape.iterations'),50)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>> set up IK
    cnt=0
    handlesList = []
    for start in startJoints:
        currentCurveInfo = crvsInfo[cnt]
        heirarchy = search.returnJointHeirarchy (start)
        handle = mc.ikHandle(startJoint = heirarchy[0], curve = currentCurveInfo[3], endEffector = heirarchy[-1] ,sol='ikSplineSolver',ccv=False,pcv=False)
        handleName = mc.rename (handle[0],(start+'_ikHandle'))
        effectorName = mc.rename (handle[1],(start+'_effector'))
        handlesList.append(handleName)
        cnt+=1
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>> prep data for return
    returnList = []
    returnList.append(follicles)
    returnList.append(handlesList)
    returnList.append(crvInfo[-1])
    return returnList

# ====================================================================================================================
# FUNCTION - 2
#
# SIGNATURE:
#	makeChainsFishDynamic(startJoints,name,controlHolder)
#
# DESCRIPTION:
#   connects stuff to a control
# 
# ARGUMENTS:
# 	startJoints - list of start joints
#   name - base name for the system
#   controlHolder - control to connect the attributes to
#
# RETURNS:
#	nada
#
# ====================================================================================================================

def makeChainsFishDynamic (startJoints,name,controlHolder):
    returnList = makeChainsDynamic(startJoints,name)
    folliclesList = returnList[0]
    parentList=[]
    # return the parent of the start joints
    for jnt in startJoints:
        parentBuffer = mc.listRelatives (jnt,parent=True)
        parentList.append(parentBuffer)
    #parent the start joints
    for cnt in range(len(startJoints)):
        mc.parent(folliclesList[cnt],parentList[cnt])
    # connect the hair system
    hairSystem = returnList[2]
    mc.connectAttr(controlHolder+'.Dynamics',(hairSystem+'.simulationMethod'))
    #mc.connectAttr(controlHolder+'.followCalc',(hairSystem+'.simulationMethod'))
    mc.connectAttr(controlHolder+'.startFrame',(hairSystem+'.startFrame'))


# ====================================================================================================================
# FUNCTION - 2
# ACKNOWLEDGE:
#   Tomaso Sanguini - http://www.tommasosanguigni.it/blog/?p=73
#
# SIGNATURE:
#	createFollicle (pos=[0, 0, 0], nurbs_surface=None, poly_surface=None)
#
# DESCRIPTION:
#   connects stuff to a control
# 
# ARGUMENTS:
# 	startJoints - list of start joints
#   name - base name for the system
#   controlHolder - control to connect the attributes to
#
# RETURNS:
#	nada
#
# ====================================================================================================================
 
def createFollicle (pos=[0, 0, 0], nurbs_surface=None, poly_surface=None):
 
    if (nurbs_surface==None and poly_surface==None):
        OpenMaya.displayError("Function createFollicle() needs a nurbs surface or poly surface")
        return
 
    transform_node = mc.createNode("transform")
    mc.setAttr((transform_node +".tx"), pos[0])
    mc.setAttr((transform_node +".ty"), pos[1])
    mc.setAttr((transform_node +".tz"), pos[2])
 
    #make vector product nodes to return correct rotation of the transform node
    vector_product = mc.createNode("vectorProduct")
    mc.setAttr((vector_product+".operation"), 4)
    mc.connectAttr( (transform_node+".worldMatrix"), (vector_product+".matrix"), f=1)
    mc.connectAttr( (transform_node+".rotatePivot"), (vector_product+".input1"), f=1)
 
    #connect the correct position to a closest point on surface node created
    if nurbs_surface:
        closest_position = mc.createNode("closestPointOnSurface", n=(transform_node+"_CPOS"))
        mc.connectAttr( (nurbs_surface+".ws"), (closest_position+".is"), f=1)
        mc.connectAttr( (vector_product+".output"), (closest_position+".inPosition"), f=1)
 
    if poly_surface:
        closest_position = mc.createNode("closestPointOnMesh", n=(transform_node+"_CPOS"))
        mc.connectAttr( (poly_surface+".outMesh"), (closest_position+".im"), f=1)
        mc.connectAttr( (vector_product+".output"), (closest_position+".inPosition"), f=1)
 
    #create a follicle node and connect it
    follicle_transform = mc.createNode("transform", n=(transform_node+"follicle"))
    follicle = mc.createNode("follicle", n=(transform_node+"follicleShape"), p=follicle_transform)
    mc.connectAttr((follicle+".outTranslate"), (follicle_transform+".translate"), f=1)
    mc.connectAttr((follicle+".outRotate"), (follicle_transform+".rotate"), f=1)
    if nurbs_surface:
        mc.connectAttr((nurbs_surface+".local"), (follicle+".is"), f=1)
        mc.connectAttr((nurbs_surface+".worldMatrix[0]"), (follicle+".inputWorldMatrix"), f=1)
    if poly_surface:
        mc.connectAttr((poly_surface+".outMesh"), (follicle+".inm"), f=1)
        mc.connectAttr((poly_surface+".worldMatrix[0]"), (follicle+".inputWorldMatrix"), f=1)
 
    mc.setAttr((follicle+".parameterU"), mc.getAttr (closest_position+".parameterU"))
    mc.setAttr((follicle+".parameterV"), mc.getAttr (closest_position+".parameterV"))
 
    #return strings
    mc.delete(transform_node)
    return [follicle_transform, follicle, closest_position]
 
def createFollicles  (follicle_positions=[[0,0,0]], nurbs_surface=None, poly_surface=None):
 
    out_follicles=list()
 
    if (nurbs_surface==None and poly_surface==None):
        OpenMaya.displayError("Function createFollicles() needs a nurbs surface or poly surface")
        return
 
    for pos in follicle_positions:
        lst = createFollicle(pos, nurbs_surface, poly_surface)
        out_follicles.append(lst)
    return out_follicles
