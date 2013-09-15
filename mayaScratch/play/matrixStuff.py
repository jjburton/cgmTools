matrix = getMatrix("sternum_segIK_anim")
decompMatrix("sternum_segIK_anim")

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import math
import sys


getMatrix("sternum_segIK_anim")
decompMatrix("sternum_segIK_anim")
m = OpenMaya.MObject()
OpenMaya.MMatrix(mc.getAttr('sternum_segIK_anim.worldMatrix'))

cgmMeta.cgmNode('worldCenter_loc')._MObject
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import math
import sys
def getMatrix(node):
     '''
     Gets the world matrix of an object based on name.
     '''
     #Selection list object and MObject for our matrix
     selection = OpenMaya.MSelectionList()
     matrixObject = OpenMaya.MObject()
     status = ''
     #Adding object
     mobj=OpenMaya.MObject()
     selection.add(node)
     selection.getDependNode(0,mobj) 
     print('dependNode',mobj)
     #New api is nice since it will just return an MObject instead of taking two arguments.
     #selection.getDependNode(0,MObjectA)
     
     #Dependency node so we can get the worldMatrix attribute
     fnThisNode = OpenMaya.MFnDependencyNode(mobj)
     print('fnThisNode',fnThisNode)

     #Get it's world matrix plug
     worldMatrixAttr = fnThisNode.attribute( "worldMatrix" )
     print('worldMatrixAttr')

     #Getting mPlug by plugging in our MObject and attribute
     matrixPlug = OpenMaya.MPlug( mobj, worldMatrixAttr )
     matrixPlug = matrixPlug.elementByLogicalIndex( 0 )
     print('matrixPlug',matrixPlug)
     
     #matrixObject = matrixPlug.asMObject(  )
     matrixObject = OpenMaya.MMatrix()
     #matrixPlug.getValue( matrixObject )
     matrixObject = matrixPlug.asMObject(  )
     print('matrixObject',status,matrixObject)

     #Finally get the data
     worldMatrixData = OpenMaya.MFnMatrixData( matrixObject )
     print('worldMatrixData',worldMatrixData)

     worldMatrix = worldMatrixData.matrix( )
     
     return worldMatrix

def getMatrix(node):
 '''
 Gets the world matrix of an object based on name.
 '''
 #Selection list object and MObject for our matrix
 selection = OpenMaya.MSelectionList()
 matrixObject = OpenMaya.MObject()
 MObjectA = OpenMaya.MObject()
 
 #Adding object
 selection.add(node)
 
 #New api is nice since it will just return an MObject instead of taking two arguments.
 selection.getDependNode(0,MObjectA)
 
 #Dependency node so we can get the worldMatrix attribute
 fnThisNode = OpenMaya.MFnDependencyNode(MObjectA)
 
 #Get it's world matrix plug
 worldMatrixAttr = fnThisNode.attribute( "worldMatrix" )
 
 #Getting mPlug by plugging in our MObject and attribute
 matrixPlug = OpenMaya.MPlug( MObjectA, worldMatrixAttr )
 matrixPlug = matrixPlug.elementByLogicalIndex( 0 )
 
 #Get matrix plug as MObject so we can get it's data.
 matrixObject = matrixPlug.asMObject(  )
 
 #Finally get the data
 worldMatrixData = OpenMaya.MFnMatrixData( matrixObject )
 worldMatrix = worldMatrixData.matrix( )
 
 return worldMatrix

def decompMatrix(node,matrix):
 '''
 Decomposes a MMatrix in new api. Returns an list of translation,rotation,scale in world space.
 '''
 #Rotate order of object
 rotOrder = cmds.getAttr('%s.rotateOrder'%node)
 
 #Puts matrix into transformation matrix
 mTransformMtx = OpenMaya.MTransformationMatrix(matrix)
 
 #Translation Values
 trans = mTransformMtx.translation(OpenMaya.MSpace.kWorld)
 
 #Euler rotation value in radians
 eulerRot = mTransformMtx.rotation()
 
 #Reorder rotation order based on ctrl.
 eulerRot.reorderIt(rotOrder)
 
 #Find degrees
 angles = [math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]
 
 #Find world scale of our object.
 scale = mTransformMtx.scale(OpenMaya.MSpace.kWorld)

 #Return Values
 return [trans.x,trans.y,trans.z],angles,scale