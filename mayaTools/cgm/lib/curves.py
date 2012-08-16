#=================================================================================================================================================
#=================================================================================================================================================
#	attribute - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with attributes
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
#   
#=================================================================================================================================================

import maya.cmds as mc
import maya.mel as mel

from cgm.lib.classes import NameFactory

from cgm.lib import (distance,
                     dictionary,
                     cgmMath,
                     attributes,
                     search,
                     rigging,
                     guiFactory,
                     locators,
                     position)

import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Parent shape
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def parentShape(obj,curve):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Simple parent shape 

    ARGUMENTS:
    obj(string)
    curve(string)

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    mc.select (cl=True)
    shape = mc.listRelatives (curve, f= True,shapes=True)
    mc.parent (shape,obj,add=True,shape=True)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def parentShapeInPlace(obj,curve):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Way to parent shape an object's transform node in place. Man this thing
    sucked figuring out....:) 

    ARGUMENTS:
    obj(string)
    curve(string)

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(obj) is True,"'%s' doesn't exist."%obj
    assert mc.objExists(curve) is True,"'%s' doesn't exist."%curve

    mc.select (cl=True)
    workingCurve = mc.duplicate(curve)
    parents = search.returnAllParents(obj)

    """Check for parents on the curve and get rid of them to alleviate some transform nonsense"""
    curveParents = search.returnAllParents(workingCurve)
    if curveParents:
        workingCurve = mc.parent(workingCurve,world=True)

    """copy pivot """
    rigging.copyPivot(workingCurve,obj)
    pos = mc.xform(obj, q=True, os=True, rp = True)

    curveScale =  mc.xform(workingCurve,q=True, s=True,r=True)
    objScale =  mc.xform(obj,q=True, s=True,r=True)

    """account for freezing"""
    mc.makeIdentity(workingCurve,apply=True,translate =True, rotate = True, scale=False)

    # make our zero out group
    group = rigging.groupMeObject(obj,False)
    """
    pos = []
    pos.append(mc.getAttr(group+'.translateX') - mc.getAttr(obj+'.translateX'))
    pos.append(mc.getAttr(group+'.translateY') - mc.getAttr(obj+'.translateY'))
    pos.append(mc.getAttr(group+'.translateZ') - mc.getAttr(obj+'.translateZ'))
    """
    workingCurve = rigging.doParentReturnName(workingCurve,group)

    # zero out the group 
    mc.setAttr((group+'.tx'),pos[0])
    mc.setAttr((group+'.ty'),pos[1])
    mc.setAttr((group+'.tz'),pos[2])
    mc.setAttr((group+'.rx'),0)
    mc.setAttr((group+'.ry'),0)
    mc.setAttr((group+'.rz'),0)

    #main scale fix 
    baseMultiplier = [0,0,0]
    baseMultiplier[0] = ( curveScale[0]/objScale[0] )
    baseMultiplier[1] = ( curveScale[1]/objScale[1] )
    baseMultiplier[2] = ( curveScale[2]/objScale[2] )
    mc.setAttr(workingCurve+'.sx',baseMultiplier[0])
    mc.setAttr(workingCurve+'.sy',baseMultiplier[1])
    mc.setAttr(workingCurve+'.sz',baseMultiplier[2])

    #parent scale fix  
    if parents:
        parents.reverse()
        multiplier = [baseMultiplier[0],baseMultiplier[1],baseMultiplier[2]]
        for p in parents:
            scaleBuffer = mc.xform(p,q=True, s=True,r=True)
            multiplier[0] = ( (multiplier[0]/scaleBuffer[0]) )
            multiplier[1] = ( (multiplier[1]/scaleBuffer[1]) )
            multiplier[2] = ( (multiplier[2]/scaleBuffer[2])  )
        mc.setAttr(workingCurve+'.sx',multiplier[0])
        mc.setAttr(workingCurve+'.sy',multiplier[1])
        mc.setAttr(workingCurve+'.sz',multiplier[2])	

    workingCurve = mc.parent(workingCurve,world=True)
    mc.delete(group)

    "freeze for parent shaping """
    mc.makeIdentity(workingCurve,apply=True,translate =True, rotate = True, scale=True)
    shape = mc.listRelatives (workingCurve, f= True,shapes=True)
    mc.parent (shape,obj,add=True,shape=True)
    mc.delete(workingCurve)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def parentShapeInPlace3(obj,curve):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Way to parent shape an object's transform node in place. Man this thing
    sucked figuring out....:) 

    ARGUMENTS:
    obj(string)
    curve(string)

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(obj) is True,"'%s' doesn't exist."%obj
    assert mc.objExists(curve) is True,"'%s' doesn't exist."%curve

    mc.select (cl=True)
    workingCurve = mc.duplicate(curve)
    parents = search.returnAllParents(obj)

    """Check for parents on the curve and get rid of them to alleviate some transform nonsense"""
    curveParents = search.returnAllParents(workingCurve)
    if curveParents:
        workingCurve = mc.parent(workingCurve,world=True)

    """copy pivot """
    rigging.copyPivot(workingCurve,obj)
    curveScale =  mc.xform(workingCurve,q=True, s=True,r=True)
    objScale =  mc.xform(obj,q=True, s=True,r=True)

    """account for freezing"""
    pos = mc.xform(obj, q=True, os=True, rp = True)
    mc.makeIdentity(workingCurve,apply=True,translate =True, rotate = True, scale=False)

    """ make our zero out group"""
    group = rigging.groupMeObject(obj,False)
    mc.move(pos[0],pos[1],pos[2],workingCurve)
    workingCurve = rigging.doParentReturnName(workingCurve,group)

    """ zero out the group """
    mc.setAttr((group+'.tx'),0)
    mc.setAttr((group+'.ty'),0)
    mc.setAttr((group+'.tz'),0)
    mc.setAttr((group+'.rx'),0)
    mc.setAttr((group+'.ry'),0)
    mc.setAttr((group+'.rz'),0)    

    """main scale fix """
    baseMultiplier = [0,0,0]
    baseMultiplier[0] = ( curveScale[0]/objScale[1] )
    baseMultiplier[1] = ( curveScale[0]/objScale[1] )
    baseMultiplier[2] = ( curveScale[0]/objScale[1] )
    mc.setAttr(workingCurve+'.sx',baseMultiplier[0])
    mc.setAttr(workingCurve+'.sy',baseMultiplier[1])
    mc.setAttr(workingCurve+'.sz',baseMultiplier[2])

    """ parent scale fix """    
    if parents:
        parents.reverse()
        multiplier = [baseMultiplier[0],baseMultiplier[1],baseMultiplier[2]]
        for p in parents:
            scaleBuffer = mc.xform(p,q=True, s=True,r=True)
            multiplier[0] = ( (objScale[0]/scaleBuffer[0]) * multiplier[0] )
            multiplier[1] = ( (objScale[1]/scaleBuffer[1]) * multiplier[1] )
            multiplier[2] = ( (objScale[2]/scaleBuffer[2]) * multiplier[2] )
        mc.setAttr(workingCurve+'.sx',multiplier[0])
        mc.setAttr(workingCurve+'.sy',multiplier[1])
        mc.setAttr(workingCurve+'.sz',multiplier[2])

    workingCurve = mc.parent(workingCurve,world=True)
    mc.delete(group)

    "freeze for parent shaping """
    mc.makeIdentity(workingCurve,apply=True,translate =True, rotate = True, scale=True)
    shape = mc.listRelatives (workingCurve, f= True,shapes=True)
    mc.parent (shape,obj,add=True,shape=True)
    mc.delete(workingCurve)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def parentShapeInPlace2(obj,curve):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Way to parent shape an object's transform node in place

    ARGUMENTS:
    obj(string)
    curve(string)

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    mc.select (cl=True)
    workingCurve = mc.duplicate(curve)
    shape = mc.listRelatives (workingCurve, f= True,shapes=True)
    parents = search.returnAllParents(obj)

    """copy pivot """
    rigging.copyPivot(workingCurve,obj)
    curveScale =  mc.xform(workingCurve,q=True, s=True,r=True)

    mc.makeIdentity(workingCurve,apply=True,translate =True, rotate = True, scale=True)

    """ make our zero out group"""
    group = rigging.groupMeObject(obj,False)
    workingCurve = rigging.doParentReturnName(workingCurve,group)
    """ zero out the group """
    mc.setAttr((group+'.tx'),0)
    mc.setAttr((group+'.ty'),0)
    mc.setAttr((group+'.tz'),0)
    mc.setAttr((group+'.rx'),0)
    mc.setAttr((group+'.ry'),0)
    mc.setAttr((group+'.rz'),0)

    """ scale fix """
    objScale = mc.xform(obj,q=True, s=True,r=True)
    baseMultiplier = [0,0,0]
    baseMultiplier[0] = ( (1/curveScale[0])*(1/objScale[0]) )
    baseMultiplier[1] = ( (1/curveScale[1])*(1/objScale[1] ))
    baseMultiplier[2] = ( (1/curveScale[2])*(1/objScale[2]) )

    mc.setAttr(group+'.sx',baseMultiplier[0])
    mc.setAttr(group+'.sy',baseMultiplier[1])
    mc.setAttr(group+'.sz',baseMultiplier[2])


    """ parent scale fix """    
    if parents != None:
        parents.reverse()
        multiplier = mc.xform(obj,q=True, s=True,r=True)
        for p in parents:
            scaleBuffer = mc.xform(p,q=True, s=True,r=True)
            multiplier[0] = ( (1/scaleBuffer[0]) * multiplier[0] )
            multiplier[1] = ( (1/scaleBuffer[1]) * multiplier[1] )
            multiplier[2] = ( (1/scaleBuffer[2]) * multiplier[2] )
        mc.setAttr(workingCurve+'.sx',multiplier[0])
        mc.setAttr(workingCurve+'.sy',multiplier[1])
        mc.setAttr(workingCurve+'.sz',multiplier[2])

    workingCurve = mc.parent(workingCurve,world=True)
    mc.delete(group)

    "freeze for parent shaping """
    mc.makeIdentity(workingCurve,apply=True,translate =True, rotate = True, scale=False)
    mc.parent (shape,obj,add=True,shape=True)
    mc.delete(workingCurve)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Color Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnColorsFromCurve(curve):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the colors used on the shapes of a curve as a list in order
    of volume used

    ARGUMENTS:
    curve(string

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ first get the shapes """
    shapes = mc.listRelatives(curve,shapes=True,fullPath=True)
    colorsCatcher = []
    for shape in shapes:
        colorsCatcher.append(mc.getAttr(shape+'.overrideColor'))
    colorVolumes = {}
    for color in colorsCatcher:
        volmesBuffer = 0
        for shape in shapes:
            if (mc.getAttr(shape+'.overrideColor')) == color:
                absSize = distance.returnAbsoluteSizeCurve(shape)
                volume = cgmMath.multiplyList(absSize)
                volmesBuffer = volmesBuffer + volume
        colorVolumes[color] = volmesBuffer

    orderedDictList = dictionary.returnDictionarySortedToList (colorVolumes,True)
    returnList = []
    orderedDictList.reverse()
    for set in orderedDictList:
        returnList.append(set[0])
    return returnList

def setCurveColorByName(obj,color):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Set the color of a curve(and subshapes) or shape by color name

    ARGUMENTS:
    obj(string) - object to affect
    color(string) - the color name

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    colorIndex = dictionary.returnColorIndex(color)
    if colorIndex == False:
        return False
    else:
        return setColorByIndex(obj,colorIndex)     

def setColorByIndex(obj,colorIndex):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Set the color of a curve(and subshapes) or shape by color index

    ARGUMENTS:
    obj(string) - object to affect
    color(string) - the color name

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if search.returnObjectType(obj) == 'shape':
        attributes.doSetAttr(obj, 'overrideEnabled', True)
        attributes.doSetAttr(obj, 'overrideColor', colorIndex)
    else:
        shapes = mc.listRelatives (obj, shapes=True,fullPath = True)

        if shapes > 0:
            for shape in shapes:
                attributes.doSetAttr(shape, 'overrideEnabled', True)
                attributes.doSetAttr(shape, 'overrideColor', colorIndex)
        else:
            return False



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Curve Division
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Text Curves
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def doUpdateTextFromNameSelected():
    buffer = mc.ls(sl=True)
    for obj in buffer:
        doUpdateTextFromName(obj)

def doUpdateTextFromName(textCurveObj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Names an object's heirarchy below

    ARGUMENTS:
    obj(string) - the object we'd like to startfrom

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    nameBuffer = textCurveObj
    attributes.storeInfo(textCurveObj,'cgmObjectText',nameBuffer,True)
    updateTextCurveObject(textCurveObj)
    buffer = NameFactory.doNameObject(textCurveObj)
    return buffer

def createTextCurve(text,size=1,font='Arial'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Replacement for maya's textCurves utilizing a single tranform instead of a nested tranform setup

    ARGUMENTS:
    text(string) = the text to be created as curves
    size(float) = size you want it initiall created as
    font(string) = make sure you use an existing font

    RETURNS:
    objName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    textBuffer = mc.textCurves(cch = False, f = font, t = text)
    createdCurves = []
    children = search.returnAllChildrenObjects(textBuffer,True)
    for c in children:
        shapesBuffer = (mc.listRelatives(c,shapes=True,fullPath=True))
        if shapesBuffer is not None:
            """ delete the history, parent to the world, freeze it and append"""
            mc.delete(c,ch=True)
            c = rigging.doParentToWorld(c)
            mc.makeIdentity(c, apply = True, t=True,s=True,r=True)
            createdCurves.append(c)
    combineCurves(createdCurves)
    for obj in textBuffer:
        if mc.objExists(obj) != False:
            mc.delete(obj)       
    """rename the curve"""        
    textCurve = mc.rename(createdCurves[0],(text+'_curve'))

    """ center pivot """
    mc.xform(textCurve,cp=True)

    """move to world center and freeze"""
    worldCenterMaker = mc.group (w=True, empty=True)
    position.movePointSnap(textCurve,worldCenterMaker)
    mc.makeIdentity(textCurve, apply = True, t=True,s=True,r=True)
    mc.delete(worldCenterMaker)

    """ scale it """
    doScaleCurve(textCurve,size)

    return textCurve

def createTextCurveObject(text,size=1,name=None,font='Arial'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a text curve objected with pertinent information

    ARGUMENTS:
    text(string) = the text to be created as curves
    size(float) = size you want it initiall created as
    name(string) = name tag should you want to specify one, if not, it uses the text
    font(string) = make sure you use an existing font

    RETURNS:
    objName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    textCurve = createTextCurve(text,size=size,font=font)
    absSize =  distance.returnAbsoluteSizeCurve(textCurve)
    currentSize = max(absSize)
    """ tag it"""
    if name == None:
        attributes.storeInfo(textCurve,'cgmName',text)
    else:
        attributes.storeInfo(textCurve,'cgmName',name)
    attributes.storeInfo(textCurve,'cgmObjectText',text)
    attributes.storeInfo(textCurve,'cgmObjectFont',font)
    attributes.storeInfo(textCurve,'cgmType','textCurve')
    attributes.storeInfo(textCurve,'cgmObjectType','textCurve')
    attributes.storeInfo(textCurve,'cgmObjectSize',currentSize)

    return NameFactory.doNameObject(textCurve)

def updateTextCurveObject(textCurveObj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Updates/e a text curve object using the stored size, text and font information
    utilizing the original tranform

    ARGUMENTS:
    textCurveObj(string)

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ get our current size"""
    shapes = mc.listRelatives(textCurveObj,shapes=True,fullPath=True)
    storedSize = float(mc.getAttr(textCurveObj+'.cgmObjectSize'))
    """parent scales """
    scales = []
    scaleBuffer = mc.xform(textCurveObj,q=True, s=True,r=True)
    scales.append(sum(scaleBuffer)/len(scaleBuffer))

    if shapes == None:
        size = storedSize

    else:
        boundingBoxSize =  distance.returnAbsoluteSizeCurve(textCurveObj)
        if max(boundingBoxSize) != storedSize:
            if storedSize < max(boundingBoxSize):
                size = max(boundingBoxSize)
            else:
                size = storedSize
            attributes.storeInfo(textCurveObj,'cgmObjectSize',size)
        else:
            size = storedSize

    """ delete current shapes"""
    colorIndex = []
    if shapes:
        #girst get the current color"""
        colorIndex = mc.getAttr(shapes[0]+'.overrideColor')
        for shape in shapes:
            mc.delete(shape)

    """ get our text """
    text = mc.getAttr(textCurveObj+'.cgmObjectText')
    font = mc.getAttr(textCurveObj+'.cgmObjectFont')

    """ make our new text """
    textCurve = createTextCurve(text,size=size,font=font)
    position.moveParentSnap(textCurve,textCurveObj)

    """parentshape in place """
    parentShapeInPlace(textCurveObj,textCurve)
    mc.delete(textCurve)
    textCurveObj = NameFactory.doNameObject(textCurveObj)
    if colorIndex:
        setColorByIndex(textCurveObj,colorIndex)

    return textCurveObj

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utility Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def duplicateShape(shape):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Duplicates a shape

    ARGUMENTS:
    shape(string)

    RETURNS:
    crvName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """     
    parentObj = mc.listRelatives(shape, p=True, fullPath=True)
    shapes = mc.listRelatives(parentObj, shapes=True, fullPath=True)
    matchObjName = mc.ls(shape, long=True)
    matchIndex = shapes.index(matchObjName[0])

    dupBuffer = mc.duplicate(parentObj)
    children = mc.listRelatives(dupBuffer[0], children = True, fullPath =True)
    if len(children) > 0:
        for c in children:
            if search.returnObjectType(c) != 'shape':
                mc.delete(c)

    dupShapes = mc.listRelatives(dupBuffer[0], shapes=True, fullPath=True)
    for shape in dupShapes:
        if dupShapes.index(shape) != matchIndex:
            mc.delete(shape)
            return dupBuffer[0]



def curveToPython(crvName):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function to figure out tshe command to recreate a curve

    ARGUMENTS:
    crvName(string)

    RETURNS:
    command(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """      
    shapesInfo = returnCurveInfo(crvName)
    commandsReturn = []
    shapeNodes = []
    for shape in shapesInfo.keys():
        dictBuffer =  shapesInfo[shape]
        shapeNodes.append(dictBuffer['shape'])
        commandBuffer =[]
        commandBuffer.append('mc.curve')
        commandBuffer.append('%s%i' % ('d = ',dictBuffer['degree']))
        commandBuffer.append('%s%s' % ('p = ',dictBuffer['cvs'])) 
        commandBuffer.append('%s%s' % ('k = ',dictBuffer['knots'])) 
        command = ('%s%s%s%s' % (commandBuffer[0],'( ',(','.join(commandBuffer[1:])),')'))
        commandsReturn.append(command)
    #Get our message ready
    print ''
    print ("'%s' may be created with..." % crvName)
    print (guiFactory.doPrintReportStart())
    print ('import maya.cmds as mc')
    print ('from cgm.lib import curves')
    print ''
    cmd = 0 
    if len(shapeNodes)>1:
        print 'createdCurves = []'
        for shape in shapeNodes:
            print ('%s%s%s' % ('createdCurves.append(',commandsReturn[cmd],')'))
            cmd += 1
        print 'curves.combineCurves(createdCurves)'
    else:
        print ('%s%s' % ('createBuffer = ',commandsReturn[0]))

    print ''

    print (guiFactory.doPrintReportEnd())
    return commandsReturn

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Creation
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def curveFromObjList(objList):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a curve from an object list through the object's pivots

    ARGUMENTS:
    objList(list)

    RETURNS:
    crvName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    # Get the curve degree
    if len(objList) <= 3:
        curveDegree = 1
    else:
        #curveDegree = 4
        curveDegree = len(objList) - 1

    # Get our Position array
    objPositionList = []
    for obj in objList:
        tempPos = mc.xform (obj,q=True, ws=True, rp=True)
        objPositionList.append (tempPos)

    # Make the curve
    crvName = mc.curve (d=curveDegree, p = objPositionList , os=True, )
    return crvName

def curveFromPosList(posList):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a curve from an object list through the object's pivots

    ARGUMENTS:
    objList(list)

    RETURNS:
    crvName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    # Get the curve degree
    if len(posList) <= 3:
        curveDegree = 1
    else:
        #curveDegree = 4
        curveDegree = len(posList) - 1

    # Make the curve
    return mc.curve (d=curveDegree, p = posList , ws=True, )

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def createControlCurve(desiredShape,size,direction='z+'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a curve in the desired shape and scales it

    ARGUMENTS:
    desiredShape(string) - see help(createCurve) for list
    size(float)
    direction(string)

    RETURNS:
    curve(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    directionDict = {'x+':[0,90,0],'x-':[0,-90,0],'y+':[-90,0,0],'y-':[90,0,0],'z+':[0,0,0],'z-':[0,180,0]}
    rotationFactor = directionDict.get(direction)
    curve = createCurve(desiredShape)
    mc.rotate (rotationFactor[0], rotationFactor[1], rotationFactor[2], curve, ws=True)
    mc.makeIdentity(curve, apply=True,r =1, n= 1)
    doScaleCurve(curve,size)

    return curve
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modifying
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doScaleCurve(curve,size):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Combines curve on the first curve's transform

    ARGUMENTS:
    curves(list)

    RETURNS:
    combinedCurve(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    boundingBoxSize =  distance.returnBoundingBoxSize(curve)
    currentSize = max(boundingBoxSize)
    multiplier = size/currentSize
    mc.scale(multiplier,multiplier,multiplier, curve,relative = True)
    mc.makeIdentity(curve,apply=True,scale=True)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def combineCurves(curvesToCombine):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Combines curve on the first curve's transform

    ARGUMENTS:
    curves(list)

    RETURNS:
    combinedCurve(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    curveShapes = []
    for curve in curvesToCombine:
        mc.delete(curve, ch=True)

    for curve in curvesToCombine[1:]:
        shapeBuffer = mc.listRelatives (curve, f= True,shapes=True,fullPath=True)
        for shape in shapeBuffer:
            curveShapes.append(shape)

    for shape in curveShapes:
        parentShapeInPlace(curvesToCombine[0],shape)

    for curve in curvesToCombine[1:]:
        mc.delete(curve)

    return curvesToCombine[0]

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doCombineSelectedCurves():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Combines curve on the first curve's transform

    ARGUMENTS:
    curves(list)

    RETURNS:
    combinedCurve(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    curves = (mc.ls (sl=True))
    return combineCurves(curves)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Archaic
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def translateMelCommandToPy(string):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Translates a mel curve create command to python

    ARGUMENTS:
    command(string) - 'curve -d = 1, p = ....'

    RETURNS:
    pythonCommand(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    initalSplit = string.split(' ')
    flagList = []
    flagBuffer = []
    infoBuffer = []
    # get the flag lists split out
    for split in initalSplit:
        splitBuffer = list(split)
        if '-' in list(split):
            flag = splitBuffer[1]
            if re.match("^[A-Za-z]*$", flag):
                flagBuffer = []
                infoBuffer = []
                flagList.append(infoBuffer)
                infoBuffer.append(flag)
            else:
                infoBuffer.append(split)
        else:
            infoBuffer.append(split)
    # get it into a more useful format
    flagInfo = []
    i=0
    matchFlag = ''
    cnt = len(flagList)
    infoBuffer = []
    while cnt > 0:
        for chunk in flagList:        
            if chunk[0] == matchFlag:
                infoBuffer.append(chunk[1:])
                if cnt == 1:
                    flagInfo.append(infoBuffer) 
                cnt -=1
            else:
                if len(infoBuffer) > 0:
                    flagInfo.append(infoBuffer)
                matchFlag = chunk[0]
                infoBuffer = []
                infoBuffer.append(chunk[0])
                infoBuffer.append(chunk[1:])
                cnt -=1

    commandBuffer =[]
    commandBuffer.append('mc.' + initalSplit[0])
    for flagSet in flagInfo:
        buffer = []
        for info in flagSet[1:]:
            if len(info) > 2:
                buffer.append('%s%s%s' % ('(',(','.join(info)),')'))
            else:
                buffer.append('%s' % ((','.join(info))))
        if len(flagSet) < 3:
            commandBuffer.append ('%s%s%s' % (flagSet[0],' = ',(','.join(buffer))))
        else:
            commandBuffer.append ('%s%s%s%s' % (flagSet[0],' = [',(','.join(buffer)),']'))

    return ('%s%s%s%s' % (commandBuffer[0],'( ',(','.join(commandBuffer[1:])),')'))


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Search Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnShapeInfo(crvShape,type = 'all'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Simple funtion for getting curve info

    ARGUMENTS:
    crvName(string)
    type(string) -  shape,spans,form,degree,cvs,knots,all(default)

    RETURNS:
    shape(string)
    spans(int)
    form(int)
    degrees(int)
    cvs(list)
    knots(list)
    all(dictionary)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    parentBuffer = mc.listRelatives(crvShape,parent=True,type='transform',fullPath=True)
    shapeNode = crvShape
    crvName = parentBuffer[0]
    infoNode = mc.createNode('curveInfo')
    mc.connectAttr((crvName+'.worldSpace'),(infoNode+'.inputCurve'))
    spansInfo = mc.getAttr(shapeNode + '.spans')
    formInfo = mc.getAttr(crvName + '.form')
    degreeInfo = mc.getAttr(shapeNode + '.degree')
    cvsInfo = returnCurveCVs(shapeNode)
    knotsInfo = returnCurveKnots(shapeNode)
    mc.delete(infoNode)

    if type == 'shape':
        return shapeNode
    elif type == 'spans':
        return spansInfo
    elif type == 'form':
        return formInfo
    elif type == 'degree':
        return degreeInfo
    elif type == 'cvs':
        return cvsInfo
    elif type == 'knots':
        return knotsInfo
    elif type == 'all':
        fullReturnDict = {}
        fullReturnDict['name'] = crvName
        fullReturnDict['shape'] = shapeNode
        fullReturnDict['form'] = formInfo
        fullReturnDict['degree'] = degreeInfo
        fullReturnDict['cvs'] = cvsInfo
        fullReturnDict['knots'] = knotsInfo[0]
        return fullReturnDict
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnCurveInfo(crvName,type = 'all'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Simple funtion for getting curve info

    ARGUMENTS:
    crvName(string)
    type(string) -  shape,spans,form,degree,cvs,knots,all(default)

    RETURNS:
    shape(string)
    spans(int)
    form(int)
    degrees(int)
    cvs(list)
    knots(list)
    all(dictionary)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    shapeNodes = mc.listRelatives(crvName, s=True)
    curveReturnDict = {}
    for shape in shapeNodes:
        transform = mc.group(em=True)
        mc.parent(shape,transform, add=True, s=True)
        tmpShapeNode = mc.listRelatives (transform, f=True, shapes=True)
        curveReturnDict[shape] = (returnShapeInfo(tmpShapeNode[0],type))
        mc.delete(transform)

    return curveReturnDict

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnCurveCVs(crvShape):
    """
    Pythonized from http://nccastaff.bournemouth.ac.uk/jmacey/RobTheBloke/www/mel/DATA_ncurve.html
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Return the cv positions of a curve

    ARGUMENTS:
    crvName(string)

    RETURNS:
    CVPositions(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    parentBuffer = mc.listRelatives(crvShape,parent=True,type='transform')
    crvName = parentBuffer[0]
    spans = mc.getAttr(crvShape + '.spans')
    degree = mc.getAttr(crvShape + '.degree')
    numCVs = spans + degree

    CVpos = []
    i=0
    for cv in range(numCVs):
        cvBuffer = []
        cv = mc.pointPosition ('%s%s%i%s' % (crvName,'.cp[',i,']'))
        cvBuffer.append(cv[0])
        cvBuffer.append(cv[1])
        cvBuffer.append(cv[2])
        CVpos.append(cvBuffer)
        i+=1
    return CVpos

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnCurveKnots(crvShape):
    """
    Pythonized from http://nccastaff.bournemouth.ac.uk/jmacey/RobTheBloke/www/mel/DATA_ncurve.html
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Return the knots of a curve

    ARGUMENTS:
    crvName(string)

    RETURNS:
    knots(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    parentBuffer = mc.listRelatives(crvShape,parent=True,type='transform')
    infoNode = mc.createNode('curveInfo')
    mc.connectAttr((parentBuffer[0]+'.worldSpace'),(infoNode+'.inputCurve'))
    spans = mc.getAttr(crvShape + '.spans')
    form = mc.getAttr(parentBuffer[0] + '.form')
    degree = mc.getAttr(crvShape + '.degree')
    rawKnots = mc.getAttr(infoNode + '.knots')
    knots = []
    # Get rid of the crazy long numbers
    for knot in rawKnots:
        #knots.append(decimal.Decimal(knot))
        if 'e' in list(knot):
            knots.append('%f' % (knot))
        else:
            knots.append(knot)

    knotsInfo = []    
    if form == 2:
        knotsInfo.append(knots[0]-1)
    else:
        knotsInfo.append(knots[0])

    i=0
    while i > len(knots):
        knotInfo.append(knots[i])
        i+=1

    if form == 2:
        knotsInfo.append(knots[len(knots)-1]+1)
    else:
        knotsInfo.append(knots[len(knots)-1])
    mc.delete(infoNode)
    return knotsInfo


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Library Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def createCurve(desiredShape):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a nurbs control for rigging purposes

    ARGUMENTS:
    shape(string) - Options...
                    circleX/Y/Z
                    circle
                    squareX/Y/Z
                    squareRounded
                    squareDoubleRounded
                    semiSphere
                    sphere2 - 2 circle sphere
                    sphere - 3 circle sphere0
                    cube
                    pyramid
                    cross, fatCross
                    arrowSingle, arrowSingleFat
                    arrowDouble, arrowDoubleFat
                    arrow4, arrow4Fat
                    arrow8
                    arrowsOnBall
                    nail, nail2, nail4
                    foot
                    teeth
                    eye
                    gear
                    dumcgmell
                    locator
                    arrowsLocator
                    arrowsPointCenter
                    arrowForm
                    arrowDirectionBall
                    arrowRotate90, arrowRotate90Fat
                    arrowRotate180, arrowRotate180Fat
                    circleArrow, circleArrow1, circleArrow2, circleArrow3
                    cirlceArrow1Interior
                    circleArrow2Axis
                    masterAnim

    RETURNS:
    curveName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>> Flats #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if desiredShape == 'circleX':
        createBuffer = mc.circle(c=(0,0,0),nr=(1, 0, 0),sw= 360, r = 1, d = 3, ut = 0, tol =  0.01, s = 8,  ch=1)        
        return createBuffer[0]
    elif desiredShape == 'circleY':
        createBuffer = mc.circle(c=(0,0,0),nr=(0, 1, 0),sw= 360, r = 1, d = 3, ut = 0, tol =  0.01, s = 8,  ch=1)    
        return createBuffer[0]
    elif desiredShape == 'circleZ':
        createBuffer = mc.circle(c=(0,0,0),nr=(0, 0, 1),sw= 360, r = 1, d = 3, ut = 0, tol =  0.01, s = 8,  ch=1)    
        return createBuffer[0]
    elif desiredShape == 'circle':
        createBuffer = mc.curve( d = 3,p = [[0.0, 0.49781146167708507, 1.2325951644078309e-32], [0.13123176445184653, 0.49690102559137289, -7.9907779390103673e-17], [0.39451623539044561, 0.38714621134894039, -6.2257859120672911e-17], [0.55136877994331923, -0.0036079204573358946, 5.8019786056735407e-19], [0.38810846598335608, -0.39227187637508171, 6.3082128922992234e-17], [-0.0024074716196590775, -0.55174835088601837, 8.8727901998153843e-17], [-0.39151686245640288, -0.38887009755839469, 6.2535081166561775e-17], [-0.5513792701556135, 0.001203756152089949, -1.9357875328634412e-19], [-0.39112276826467002, 0.39057422994031382, -6.2809126554702937e-17], [-0.12689054310937159, 0.49802730377391141, -8.0088898735621358e-17], [3.1101827599225328e-17, 0.49781146167708512, 2.4651903288156619e-32]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0))
        return createBuffer
    elif desiredShape == 'squareX':
        createBuffer = mc.curve(d=1, p= [(0, -1, -1),( 0, 1, -1), (0, 1, 1),(0, -1, 1),( 0, -1, -1)], k = [0,1,2,3,4])
        return createBuffer[0]
    elif desiredShape == 'squareY':
        createBuffer = mc.curve(d=1, p= [(-1, 0, -1),(1, 0, -1), (1, 0, 1),(-1, 0, 1),( -1, 0, -1)], k = [0,1,2,3,4])
        return createBuffer[0]
    elif desiredShape == 'squareZ':
        createBuffer = mc.curve(d=1, p= [(-1, -1, 0),(1, -1, 0), (1, 1, 0),(-1, 1, 0),( -1, -1, 0)], k = [0,1,2,3,4])
        return createBuffer[0] 
    elif desiredShape == 'square':
        createBuffer = mc.curve(d=1, p= [(-1, -1, 0),(1, -1, 0), (1, 1, 0),(-1, 1, 0),( -1, -1, 0)], k = [0,1,2,3,4])
        return createBuffer
    elif desiredShape == 'squareRounded':
        createBuffer = mc.curve( d = 3,p = [[-1.0000000004369547, 0.77777777811763138, 0.0], [-1.0000000004369547, 0.83333333369746221, 0.0], [-0.94444444485712398, 0.94444444485712398, 0.0], [-0.83333333369746221, 1.0000000004369547, 0.0], [-0.77777777811763138, 1.0000000004369547, 0.0], [0.0, 1.0000000004369547, 0.0], [0.77777777811763138, 1.0000000004369547, 0.0], [0.83333333369746221, 1.0000000004369547, 0.0], [0.94444444485712398, 0.94444444485712398, 0.0], [1.0000000004369547, 0.83333333369746221, 0.0], [1.0000000004369547, 0.77777777811763138, 0.0], [1.0000000004369547, -0.77777777811763138, 0.0], [1.0000000004369547, -0.83333333369746221, 0.0], [0.94444444485712398, -0.94444444485712398, 0.0], [0.83333333369746221, -1.0000000004369547, 0.0], [0.77777777811763138, -1.0000000004369547, 0.0], [0.0, -1.0000000004369547, 0.0], [-0.77777777811763138, -1.0000000004369547, 0.0], [-0.83333333369746221, -1.0000000004369547, 0.0], [-0.94444444485712398, -0.94444444485712398, 0.0], [-1.0000000004369547, -0.83333333369746221, 0.0], [-1.0000000004369547, -0.77777777811763138, 0.0], [-1.0000000004369547, 0.0, 0.0], [-1.0000000004369547, 0.77777777811763138, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 21.0, 21.0))
        return createBuffer
    elif desiredShape == 'squareDoubleRounded':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[-14.1732288, 11.023622400000001, 0.0], [-14.1732288, 11.811024, 0.0], [-13.385827200000001, 13.385827200000001, 0.0], [-11.811024, 14.1732288, 0.0], [-11.023622400000001, 14.1732288, 0.0], [0.0, 14.1732288, 0.0], [11.023622400000001, 14.1732288, 0.0], [11.811024, 14.1732288, 0.0], [13.385827200000001, 13.385827200000001, 0.0], [14.1732288, 11.811024, 0.0], [14.1732288, 11.023622400000001, 0.0], [14.1732288, -11.023622400000001, 0.0], [14.1732288, -11.811024, 0.0], [13.385827200000001, -13.385827200000001, 0.0], [11.811024, -14.1732288, 0.0], [11.023622400000001, -14.1732288, 0.0], [0.0, -14.1732288, 0.0], [-11.023622400000001, -14.1732288, 0.0], [-11.811024, -14.1732288, 0.0], [-13.385827200000001, -13.385827200000001, 0.0], [-14.1732288, -11.811024, 0.0], [-14.1732288, -11.023622400000001, 0.0], [-14.1732288, 0.0, 0.0], [-14.1732288, 11.023622400000001, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 21.0, 21.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-14.441444006310256, 11.232234227130199, 0.0], [-14.441444006310256, 12.034536671925213, 0.0], [-13.639141561515244, 13.639141561515244, 0.0], [-12.034536671925213, 14.441444006310256, 0.0], [-11.232234227130199, 14.441444006310256, 0.0], [0.0, 14.441444006310256, 0.0], [11.232234227130199, 14.441444006310256, 0.0], [12.034536671925213, 14.441444006310256, 0.0], [13.639141561515244, 13.639141561515244, 0.0], [14.441444006310256, 12.034536671925213, 0.0], [14.441444006310256, 11.232234227130199, 0.0], [14.441444006310256, -11.232234227130199, 0.0], [14.441444006310256, -12.034536671925213, 0.0], [13.639141561515244, -13.639141561515244, 0.0], [12.034536671925213, -14.441444006310256, 0.0], [11.232234227130199, -14.441444006310256, 0.0], [0.0, -14.441444006310256, 0.0], [-11.232234227130199, -14.441444006310256, 0.0], [-12.034536671925213, -14.441444006310256, 0.0], [-13.639141561515244, -13.639141561515244, 0.0], [-14.441444006310256, -12.034536671925213, 0.0], [-14.441444006310256, -11.232234227130199, 0.0], [-14.441444006310256, 0.0, 0.0], [-14.441444006310256, 11.232234227130199, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 21.0, 21.0)))
        return (combineCurves(createdCurves))
    #>>> Shapes #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'semiSphere':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[2.857475428624581e-18, -0.49945484503664428, -1.4148404260869211e-16], [-0.064781077333315659, -0.49945484503664428, -1.4148404260869211e-16], [-0.19575356029809832, -0.4735952798606346, -1.341586239896448e-16], [-0.36146871545166515, -0.36310022111541057, -1.0285792132369657e-16], [-0.47275102852901435, -0.19762919318276717, -5.5983794064387245e-17], [-0.51237611522550586, -0.002235692604763364, -6.3332017077307753e-19], [-0.47444505408791537, 0.19349630782585031, 5.4813042926931563e-17], [-0.36467392573942187, 0.35993158395963543, 1.0196031947076868e-16], [-0.19969007656502574, 0.47187064536118212, 1.336700747976021e-16], [-0.0044713426389336687, 0.51236511726102951, 1.4514122508201703e-16], [0.19142438451047772, 0.47528384955404163, 1.3463695685361517e-16], [0.35833671184131494, 0.36624120220511452, 1.037476888507223e-16], [0.47099581759986103, 0.20174704531704907, 5.7150286636465102e-17], [0.51233709607741473, 0.0067068441137208981, 1.8998943103379021e-18], [0.47612813126084641, -0.18934845020587496, -5.3638050492536764e-17], [0.36775063465186242, -0.35673642025659413, -1.01055203258571e-16], [0.20398912339361808, -0.47010677830973407, -1.3317041192808817e-16], [0.073487899814113494, -0.49824818995351527, -1.4114222504321649e-16], [0.0087166889526499192, -0.49937877564458133, -1.4146249390370945e-16]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 16.0, 16.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.49843859183412376, -1.6318141489256825e-15, -1.5965779634541381e-34], [-0.47444505408791537, -1.6499358675724566e-15, 0.19349630782585195], [-0.36467392573942187, -1.6921180779411187e-15, 0.35993158395963709], [-0.19969007656502577, -1.7470541964651004e-15, 0.47187064536118384], [-0.0044713426389336973, -1.8064270552111321e-15, 0.51236511726103129], [0.19142438451047769, -1.861247068431426e-15, 0.47528384955404346], [0.35833671184131494, -1.9032139830644273e-15, 0.36624120220511641], [0.47099581759986103, -1.9259742633798967e-15, 0.20174704531705098], [0.49839957268603247, -1.9208881583862078e-15, 1.5965779634541383e-34]],k = (5.0, 5.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 11.0, 11.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-8.3725734944525709e-17, 0.49843859183412187, 1.1067560020319692e-16], [-4.78943939208342e-17, 0.47444505408791343, 0.19349630782585206], [-2.8489950755045629e-18, 0.36467392573941998, 0.35993158395963715], [4.262750913353735e-17, 0.19969007656502383, 0.47187064536118389], [8.1649966864859167e-17, 0.0044713426389318064, 0.51236511726103129], [1.0831003622307075e-16, -0.19142438451047952, 0.4752838495540434], [1.1857112745928954e-16, -0.35833671184131671, 0.36624120220511636], [1.1087995948819629e-16, -0.47099581759986275, 0.20174704531705087], [8.3719236951033887e-17, -0.49839957268603413, -1.1066693621187448e-16]],k = (5.0, 5.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 11.0, 11.0)))
        return (combineCurves(createdCurves))
    elif desiredShape == 'sphere2':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[5.3290705182007512e-17, 1.0, 0.0], [-0.26120387496374148, 1.0, 0.0], [-0.78361162489122427, 0.78361162489122427, 0.0], [-1.1081941875543879, 3.2112695072372299e-16, 0.0], [-0.78361162489122449, -0.78361162489122405, 0.0], [-3.3392053635905195e-16, -1.1081941875543881, 0.0], [0.78361162489122382, -0.78361162489122438, 0.0], [1.1081941875543879, -5.9521325992805852e-16, 0.0], [0.78361162489122504, 0.78361162489122382, 0.0], [0.26120387496374164, 0.99999999999999978, 0.0], [8.8817841970012528e-17, 0.99999999999999989, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[1.9721522630525296e-33, 1.0, -5.3290705182007512e-17], [-1.5994124469961577e-17, 1.0, 0.26120387496374148], [-4.7982373409884707e-17, 0.78361162489122427, 0.78361162489122427], [-6.7857323231109134e-17, 3.2112695072372299e-16, 1.1081941875543879], [-4.7982373409884731e-17, -0.78361162489122405, 0.78361162489122449], [-2.0446735801084019e-32, -1.1081941875543881, 3.3392053635905195e-16], [4.7982373409884682e-17, -0.78361162489122438, -0.78361162489122382], [6.7857323231109134e-17, -5.9521325992805852e-16, -1.1081941875543879], [4.7982373409884762e-17, 0.78361162489122382, -0.78361162489122504], [1.5994124469961583e-17, 0.99999999999999978, -0.26120387496374164], [4.9303806576313241e-33, 0.99999999999999989, -8.8817841970012528e-17]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        return (combineCurves(createdCurves))
    elif desiredShape == 'sphere':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[5.3290705182007512e-17, 6.123233995736766e-17, -1.0], [-0.26120387496374148, 6.123233995736766e-17, -1.0], [-0.78361162489122427, 4.7982373409884707e-17, -0.78361162489122427], [-1.1081941875543879, 1.9663354616187859e-32, -3.2112695072372299e-16], [-0.78361162489122449, -4.7982373409884701e-17, 0.78361162489122405], [-3.3392053635905195e-16, -6.7857323231109146e-17, 1.1081941875543881], [0.78361162489122382, -4.7982373409884713e-17, 0.78361162489122438], [1.1081941875543879, -3.6446300679047921e-32, 5.9521325992805852e-16], [0.78361162489122504, 4.7982373409884682e-17, -0.78361162489122382], [0.26120387496374164, 6.123233995736766e-17, -0.99999999999999978], [8.8817841970012528e-17, 6.123233995736766e-17, -0.99999999999999989]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[5.3290705182007512e-17, 1.0, 0.0], [-0.26120387496374148, 1.0, 0.0], [-0.78361162489122427, 0.78361162489122427, 0.0], [-1.1081941875543879, 3.2112695072372299e-16, 0.0], [-0.78361162489122449, -0.78361162489122405, 0.0], [-3.3392053635905195e-16, -1.1081941875543881, 0.0], [0.78361162489122382, -0.78361162489122438, 0.0], [1.1081941875543879, -5.9521325992805852e-16, 0.0], [0.78361162489122504, 0.78361162489122382, 0.0], [0.26120387496374164, 0.99999999999999978, 0.0], [8.8817841970012528e-17, 0.99999999999999989, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[1.9721522630525296e-33, 1.0, -5.3290705182007512e-17], [-1.5994124469961577e-17, 1.0, 0.26120387496374148], [-4.7982373409884707e-17, 0.78361162489122427, 0.78361162489122427], [-6.7857323231109134e-17, 3.2112695072372299e-16, 1.1081941875543879], [-4.7982373409884731e-17, -0.78361162489122405, 0.78361162489122449], [-2.0446735801084019e-32, -1.1081941875543881, 3.3392053635905195e-16], [4.7982373409884682e-17, -0.78361162489122438, -0.78361162489122382], [6.7857323231109134e-17, -5.9521325992805852e-16, -1.1081941875543879], [4.7982373409884762e-17, 0.78361162489122382, -0.78361162489122504], [1.5994124469961583e-17, 0.99999999999999978, -0.26120387496374164], [4.9303806576313241e-33, 0.99999999999999989, -8.8817841970012528e-17]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        return (combineCurves(createdCurves))      
    elif desiredShape == 'cube':
        createBuffer = mc.curve(d=1, p= [(-1, 1, 1),(1, 1, 1),(1, 1, -1),(-1, 1, -1),(-1, 1, 1),(-1, -1, 1),(-1, -1, -1),(1, -1, -1),(1, -1, 1),(-1, -1, 1),(1, -1, 1),(1, 1, 1),(1, 1, -1),(1, -1, -1),(-1, -1, -1),(-1, 1, -1)], k = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
        return createBuffer
    elif desiredShape == 'pyramid':
        createBuffer = mc.curve( d = 1,p = [[0.0, 2.2204460492503131e-16, 1.0], [0.5, 0.5, -1.1102230246251565e-16], [-0.5, 0.5, -1.1102230246251565e-16], [0.0, 2.2204460492503131e-16, 1.0], [-0.5, -0.5, 1.1102230246251565e-16], [0.5, -0.5, 1.1102230246251565e-16], [0.0, 2.2204460492503131e-16, 1.0], [0.5, 0.5, -1.1102230246251565e-16], [0.5, -0.5, 1.1102230246251565e-16], [-0.5, -0.5, 1.1102230246251565e-16], [-0.5, 0.5, -1.1102230246251565e-16]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0))
        return createBuffer
    #>>> Crosses #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'cross':
        createBuffer = mc.curve( d = 1,p = [[0.10000000000000001, 0.10000000000000001, -2.2204460492503132e-17], [0.10000000000000001, 0.5, -1.1102230246251565e-16], [-0.10000000000000001, 0.5, -1.1102230246251565e-16], [-0.10000000000000001, 0.10000000000000001, -2.2204460492503132e-17], [-0.5, 0.10000000000000001, -2.2204460492503132e-17], [-0.5, -0.10000000000000001, 2.2204460492503132e-17], [-0.10000000000000001, -0.10000000000000001, 2.2204460492503132e-17], [-0.10000000000000001, -0.5, 1.1102230246251565e-16], [0.10000000000000001, -0.5, 1.1102230246251565e-16], [0.10000000000000001, -0.10000000000000001, 2.2204460492503132e-17], [0.5, -0.10000000000000001, 2.2204460492503132e-17], [0.5, 0.10000000000000001, -2.2204460492503132e-17], [0.10000000000000001, 0.10000000000000001, -2.2204460492503132e-17]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0))
        return createBuffer   
    elif desiredShape == 'fatCross':
        createBuffer = mc.curve( d = 1,p = [[0.50000000000000189, -0.250000000000001, 5.5511151231257827e-17], [0.50000000000000189, 0.249999999999999, -5.5511151231257827e-17], [0.25000000000000183, 0.24999999999999906, -5.5511151231257827e-17], [0.25000000000000183, 0.49999999999999906, -1.1102230246251565e-16], [-0.24999999999999828, 0.49999999999999911, -1.1102230246251565e-16], [-0.24999999999999828, 0.24999999999999917, -5.5511151231257827e-17], [-0.49999999999999833, 0.24999999999999922, -5.5511151231257827e-17], [-0.49999999999999833, -0.25000000000000078, 5.5511151231257827e-17], [-0.24999999999999828, -0.25000000000000083, 5.5511151231257827e-17], [-0.24999999999999828, -0.50000000000000089, 1.1102230246251565e-16], [0.25000000000000183, -0.50000000000000089, 1.1102230246251565e-16], [0.25000000000000183, -0.25000000000000094, 5.5511151231257827e-17], [0.50000000000000189, -0.250000000000001, 5.5511151231257827e-17]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0))
        return createBuffer
    #>>> Arrows #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'arrowSingle':
        createBuffer = mc.curve( d = 1,p = [[-6.997981610378801e-17, 0.57142856334177883, 1.2688262959010351e-16], [0.42857142250633412, 5.2484862077841004e-17, 1.1653980464618964e-32], [0.14285714083544471, 1.7494954025947002e-17, 3.8846601548729881e-33], [0.14285714083544479, -0.42857142250633412, -9.5161972192577631e-17], [-0.14285714083544465, -0.42857142250633412, -9.5161972192577631e-17], [-0.14285714083544471, -1.7494954025947002e-17, -3.8846601548729881e-33], [-0.42857142250633412, -5.2484862077841004e-17, -1.1653980464618964e-32], [-6.997981610378801e-17, 0.57142856334177883, 1.2688262959010351e-16]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0))
        return createBuffer
    elif desiredShape == 'arrowSingleFat':
        createBuffer = mc.curve( d = 1,p = [[-7.347880794884119e-17, 0.60000000000000042, 1.3322676295501878e-16], [0.40000000000000002, 4.9307508181595673e-16, 1.0877048587575128e-32], [0.20000000000000001, 4.6858214583300972e-16, 5.4385242937875638e-33], [0.20000000000000004, -0.39999999999999958, -8.8817841970012528e-17], [-0.19999999999999998, -0.39999999999999958, -8.8817841970012528e-17], [-0.20000000000000001, 4.1959627386711556e-16, -5.4385242937875638e-33], [-0.40000000000000002, 3.951033378841685e-16, -1.0877048587575128e-32], [-7.347880794884119e-17, 0.60000000000000042, 1.3322676295501878e-16]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0))
        return createBuffer
    elif desiredShape == 'arrowDouble':
        createBuffer = mc.curve( d = 1,p = [[0.0, -0.50000010145707274, -1.1102232499051129e-16], [-0.2142857577673169, -0.2142857577673169, -4.758099642450484e-17], [-0.071428585922438961, -0.2142857577673169, -4.758099642450484e-17], [-0.071428585922438961, 0.2142857577673169, 4.758099642450484e-17], [-0.2142857577673169, 0.2142857577673169, 4.758099642450484e-17], [0.0, 0.50000010145707274, 1.1102232499051129e-16], [0.2142857577673169, 0.2142857577673169, 4.758099642450484e-17], [0.071428585922438961, 0.2142857577673169, 4.758099642450484e-17], [0.071428585922438961, -0.2142857577673169, -4.758099642450484e-17], [0.2142857577673169, -0.2142857577673169, -4.758099642450484e-17], [0.0, -0.50000010145707274, -1.1102232499051129e-16]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0))
        return createBuffer
    elif desiredShape == 'arrowDoubleFat':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.50000006895203375, -1.1102231777294275e-16], [-0.24444447815432763, 0.13333335172054234, -2.9605951406118067e-17], [-0.12222223907716381, 0.13333335172054234, -2.9605951406118067e-17], [-0.12222223907716381, -0.13333335172054234, 2.9605951406118067e-17], [-0.24444447815432763, -0.13333335172054234, 2.9605951406118067e-17], [0.0, -0.50000006895203375, 1.1102231777294275e-16], [0.24444447815432763, -0.13333335172054234, 2.9605951406118067e-17], [0.12222223907716381, -0.13333335172054234, 2.9605951406118067e-17], [0.12222223907716381, 0.13333335172054234, -2.9605951406118067e-17], [0.24444447815432763, 0.13333335172054234, -2.9605951406118067e-17], [0.0, 0.50000006895203375, -1.1102231777294275e-16]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0))
        return createBuffer
    elif desiredShape == 'arrow4':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.5, -1.1102230246251565e-16], [-0.125, 0.33333333333333337, -7.4014868308343778e-17], [-0.041666666666666671, 0.33333333333333337, -7.4014868308343778e-17], [-0.041666666666666671, 0.041666666666666671, -9.2518585385429722e-18], [-0.33333333333333337, 0.041666666666666671, -9.2518585385429722e-18], [-0.33333333333333337, 0.125, -2.7755575615628914e-17], [-0.5, 0.0, 0.0], [-0.33333333333333337, -0.125, 2.7755575615628914e-17], [-0.33333333333333337, -0.041666666666666671, 9.2518585385429722e-18], [-0.041666666666666671, -0.041666666666666671, 9.2518585385429722e-18], [-0.041666666666666671, -0.33333333333333337, 7.4014868308343778e-17], [-0.125, -0.33333333333333337, 7.4014868308343778e-17], [0.0, -0.5, 1.1102230246251565e-16], [0.125, -0.33333333333333337, 7.4014868308343778e-17], [0.041666666666666671, -0.33333333333333337, 7.4014868308343778e-17], [0.041666666666666671, -0.041666666666666671, 9.2518585385429722e-18], [0.33333333333333337, -0.041666666666666671, 9.2518585385429722e-18], [0.33333333333333337, -0.125, 2.7755575615628914e-17], [0.5, 0.0, 0.0], [0.33333333333333337, 0.125, -2.7755575615628914e-17], [0.33333333333333337, 0.041666666666666671, -9.2518585385429722e-18], [0.041666666666666671, 0.041666666666666671, -9.2518585385429722e-18], [0.041666666666666671, 0.33333333333333337, -7.4014868308343778e-17], [0.125, 0.33333333333333337, -7.4014868308343778e-17], [0.0, 0.5, -1.1102230246251565e-16]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0))
        return createBuffer
    elif desiredShape == 'arrow4Fat':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.49999993767396633, -1.1102228862335613e-16], [-0.14965984529016679, 0.27551016973871617, -6.1175546792461548e-17], [-0.074829922645083397, 0.27551016973871617, -6.1175546792461548e-17], [-0.074829922645083397, 0.074829922645083397, -1.6615580610298197e-17], [-0.27551016973871617, 0.074829922645083397, -1.6615580610298197e-17], [-0.27551016973871617, 0.14965984529016679, -3.3231161220596393e-17], [-0.49999993767396633, 0.0, 0.0], [-0.27551016973871617, -0.14965984529016679, 3.3231161220596393e-17], [-0.27551016973871617, -0.074829922645083397, 1.6615580610298197e-17], [-0.074829922645083397, -0.074829922645083397, 1.6615580610298197e-17], [-0.074829922645083397, -0.27551016973871617, 6.1175546792461548e-17], [-0.14965984529016679, -0.27551016973871617, 6.1175546792461548e-17], [0.0, -0.49999993767396633, 1.1102228862335613e-16], [0.14965984529016679, -0.27551016973871617, 6.1175546792461548e-17], [0.074829922645083397, -0.27551016973871617, 6.1175546792461548e-17], [0.074829922645083397, -0.074829922645083397, 1.6615580610298197e-17], [0.27551016973871617, -0.074829922645083397, 1.6615580610298197e-17], [0.27551016973871617, -0.14965984529016679, 3.3231161220596393e-17], [0.49999993767396633, 0.0, 0.0], [0.27551016973871617, 0.14965984529016679, -3.3231161220596393e-17], [0.27551016973871617, 0.074829922645083397, -1.6615580610298197e-17], [0.074829922645083397, 0.074829922645083397, -1.6615580610298197e-17], [0.074829922645083397, 0.27551016973871617, -6.1175546792461548e-17], [0.14965984529016679, 0.27551016973871617, -6.1175546792461548e-17], [0.0, 0.49999993767396633, -1.1102228862335613e-16]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0))
        return createBuffer
    elif desiredShape == 'arrow8':
        createBuffer = mc.curve( d = 1,p = [[-0.5, 0.0, 0.0], [-0.36956521739130438, -0.097826086956521757, 2.1721754829622632e-17], [-0.36956521739130438, -0.032608695652173912, 7.2405849432075425e-18], [-0.10038629776021081, -0.041581291172595521, 9.2329013706916642e-18], [-0.28437997364953888, -0.23826429512516473, 5.2905301278808265e-17], [-0.33049565217391308, -0.19214861660079055, 4.266556366001385e-17], [-0.35355335968379448, -0.35355335968379448, 7.8504616070905637e-17], [-0.19214861660079055, -0.33049565217391308, 7.3384776516397094e-17], [-0.23826429512516473, -0.28437997364953888, 6.3145038897602673e-17], [-0.041581291172595521, -0.10038629776021081, 2.2290235826052565e-17], [-0.032608695652173912, -0.36956521739130438, 8.205996268968549e-17], [-0.097826086956521757, -0.36956521739130438, 8.205996268968549e-17], [0.0, -0.5, 1.1102230246251565e-16], [0.097826086956521757, -0.36956521739130438, 8.205996268968549e-17], [0.032608695652173912, -0.36956521739130438, 8.205996268968549e-17], [0.041581291172595521, -0.10038629776021081, 2.2290235826052565e-17], [0.23826429512516473, -0.28437997364953888, 6.3145038897602673e-17], [0.19214861660079055, -0.33049565217391308, 7.3384776516397094e-17], [0.35355335968379448, -0.35355335968379448, 7.8504616070905637e-17], [0.33049565217391308, -0.19214861660079055, 4.266556366001385e-17], [0.28437997364953888, -0.23826429512516473, 5.2905301278808265e-17], [0.10038629776021081, -0.041581291172595521, 9.2329013706916642e-18], [0.36956521739130438, -0.032608695652173912, 7.2405849432075425e-18], [0.36956521739130438, -0.097826086956521757, 2.1721754829622632e-17], [0.5, 0.0, 0.0], [0.36956521739130438, 0.097826086956521757, -2.1721754829622632e-17], [0.36956521739130438, 0.032608695652173912, -7.2405849432075425e-18], [0.10038629776021081, 0.041581291172595521, -9.2329013706916642e-18], [0.28437997364953888, 0.23826429512516473, -5.2905301278808265e-17], [0.33049565217391308, 0.19214861660079055, -4.266556366001385e-17], [0.35355335968379448, 0.35355335968379448, -7.8504616070905637e-17], [0.19214861660079055, 0.33049565217391308, -7.3384776516397094e-17], [0.23826429512516473, 0.28437997364953888, -6.3145038897602673e-17], [0.041581291172595521, 0.10038629776021081, -2.2290235826052565e-17], [0.032608695652173912, 0.36956521739130438, -8.205996268968549e-17], [0.097826086956521757, 0.36956521739130438, -8.205996268968549e-17], [0.0, 0.5, -1.1102230246251565e-16], [-0.097826086956521757, 0.36956521739130438, -8.205996268968549e-17], [-0.032608695652173912, 0.36956521739130438, -8.205996268968549e-17], [-0.041581291172595521, 0.10038629776021081, -2.2290235826052565e-17], [-0.23826429512516473, 0.28437997364953888, -6.3145038897602673e-17], [-0.19214861660079055, 0.33049565217391308, -7.3384776516397094e-17], [-0.35355335968379448, 0.35355335968379448, -7.8504616070905637e-17], [-0.33049565217391308, 0.19214861660079055, -4.266556366001385e-17], [-0.28437997364953888, 0.23826429512516473, -5.2905301278808265e-17], [-0.10038629776021081, 0.041581291172595521, -9.2329013706916642e-18], [-0.36956521739130438, 0.032608695652173912, -7.2405849432075425e-18], [-0.36956521739130438, 0.097826086956521757, -2.1721754829622632e-17], [-0.5, 0.0, 0.0]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0))
        return createBuffer
    elif desiredShape == 'arrowsOnBall':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.5, 0.17472620403827191], [-0.16805565678581663, 0.3749998751955686, 0.33841270728768014], [-0.047916664586592807, 0.3749998751955686, 0.33841270728768014], [-0.047916664586592807, 0.24999975039113714, 0.42456370866851639], [-0.047916664586592807, 0.04930553822160684, 0.47625420965347298], [-0.24999975039113706, 0.049305538221606833, 0.42456370866851645], [-0.37499987519556854, 0.049305538221606812, 0.33841270728768019], [-0.37499987519556854, 0.16805565678581671, 0.33841270728768014], [-0.5, 3.8797010945728521e-17, 0.17472620403827202], [-0.37499987519556854, -0.16805565678581655, 0.33841270728768025], [-0.37499987519556854, -0.04930553822160666, 0.33841270728768019], [-0.24999975039113706, -0.049305538221606639, 0.42456370866851645], [-0.047916664586592807, -0.049305538221606632, 0.47625420965347298], [-0.047916664586592807, -0.24999975039113698, 0.4245637086685165], [-0.047916664586592807, -0.37499987519556849, 0.33841270728768025], [-0.16805565678581663, -0.37499987519556849, 0.33841270728768025], [0.0, -0.49999999999999994, 0.17472620403827213], [0.16805565678581663, -0.37499987519556849, 0.33841270728768025], [0.047916664586592807, -0.37499987519556849, 0.33841270728768025], [0.047916664586592807, -0.24999975039113698, 0.4245637086685165], [0.047916664586592807, -0.049305538221606632, 0.47625420965347298], [0.24999975039113706, -0.049305538221606639, 0.42456370866851645], [0.37499987519556854, -0.04930553822160666, 0.33841270728768019], [0.37499987519556854, -0.16805565678581655, 0.33841270728768025], [0.5, 3.8797010945728521e-17, 0.17472620403827202], [0.37499987519556854, 0.16805565678581671, 0.33841270728768014], [0.37499987519556854, 0.049305538221606812, 0.33841270728768019], [0.24999975039113706, 0.049305538221606833, 0.42456370866851645], [0.047916664586592807, 0.04930553822160684, 0.47625420965347298], [0.047916664586592807, 0.24999975039113714, 0.42456370866851639], [0.047916664586592807, 0.3749998751955686, 0.33841270728768014], [0.16805565678581663, 0.3749998751955686, 0.33841270728768014], [0.0, 0.5, 0.17472620403827191]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0))
        return createBuffer
    #>>> Nails #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'nail':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.0, 0.0], [-1.1102230246251565e-16, 0.5, 1.1102230246251565e-16], [0.17677674999999987, 0.57322325000000007, 1.2728113008009247e-16], [0.24999999999999983, 0.75, 1.6653345369377348e-16], [0.17677674999999979, 0.92677675000000026, 2.0578577730745457e-16], [-2.2204460492503131e-16, 1.0, 2.2204460492503131e-16], [-0.17677675000000023, 0.92677675000000026, 2.0578577730745457e-16], [-0.25000000000000017, 0.75, 1.6653345369377348e-16], [-0.17677675000000015, 0.57322324999999996, 1.2728113008009244e-16], [-1.1102230246251565e-16, 0.5, 1.1102230246251565e-16], [0.17677674999999987, 0.57322325000000007, 1.2728113008009247e-16], [-0.17677675000000023, 0.92677675000000026, 2.0578577730745457e-16], [-2.2204460492503131e-16, 1.0, 2.2204460492503131e-16], [0.17677674999999979, 0.92677675000000026, 2.0578577730745457e-16], [-0.17677675000000015, 0.57322324999999996, 1.2728113008009244e-16]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0))
        return createBuffer
    elif desiredShape == 'nail2':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.0, 0.0], [-5.5511151231257827e-17, -0.25, 5.5511151231257827e-17], [-0.088388375000000075, -0.28661162499999998, 6.3640565040046222e-17], [-0.12500000000000008, -0.375, 8.3266726846886741e-17], [-0.088388375000000116, -0.46338837500000013, 1.0289288865372728e-16], [-1.1102230246251565e-16, -0.5, 1.1102230246251565e-16], [0.088388374999999894, -0.46338837500000013, 1.0289288865372728e-16], [0.12499999999999992, -0.375, 8.3266726846886741e-17], [0.088388374999999936, -0.28661162500000004, 6.3640565040046234e-17], [-5.5511151231257827e-17, -0.25, 5.5511151231257827e-17], [0.088388374999999936, -0.28661162500000004, 6.3640565040046234e-17], [-0.088388375000000116, -0.46338837500000013, 1.0289288865372728e-16], [-0.12500000000000008, -0.375, 8.3266726846886741e-17], [-0.088388375000000075, -0.28661162499999998, 6.3640565040046222e-17], [0.088388374999999894, -0.46338837500000013, 1.0289288865372728e-16], [0.12499999999999992, -0.375, 8.3266726846886741e-17], [0.088388374999999936, -0.28661162500000004, 6.3640565040046234e-17], [-5.5511151231257827e-17, -0.25, 5.5511151231257827e-17], [0.0, 0.0, 0.0], [5.5511151231257827e-17, 0.25, -5.5511151231257827e-17], [-0.088388374999999936, 0.28661162500000004, -6.3640565040046234e-17], [-0.12499999999999992, 0.375, -8.3266726846886741e-17], [-0.088388374999999894, 0.46338837500000013, -1.0289288865372728e-16], [1.1102230246251565e-16, 0.5, -1.1102230246251565e-16], [0.088388375000000116, 0.46338837500000013, -1.0289288865372728e-16], [0.12500000000000008, 0.375, -8.3266726846886741e-17], [0.088388375000000075, 0.28661162499999998, -6.3640565040046222e-17], [5.5511151231257827e-17, 0.25, -5.5511151231257827e-17], [0.088388375000000075, 0.28661162499999998, -6.3640565040046222e-17], [-0.088388374999999894, 0.46338837500000013, -1.0289288865372728e-16], [-0.12499999999999992, 0.375, -8.3266726846886741e-17], [-0.088388374999999936, 0.28661162500000004, -6.3640565040046234e-17], [0.088388375000000116, 0.46338837500000013, -1.0289288865372728e-16]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0))
        return createBuffer
    elif desiredShape == 'nail4':
        createBuffer = mc.curve( d = 1,p = [[-0.25, 0.0, 0.0], [-0.28661162499999998, 0.088388375000000005, -1.9626161806840515e-17], [-0.375, 0.125, -2.7755575615628914e-17], [-0.46338837500000007, 0.088388375000000005, -1.9626161806840515e-17], [-0.5, 0.0, 0.0], [-0.46338837500000007, -0.088388375000000005, 1.9626161806840515e-17], [-0.375, -0.125, 2.7755575615628914e-17], [-0.28661162499999998, -0.088388375000000005, 1.9626161806840515e-17], [-0.25, 0.0, 0.0], [-0.28661162499999998, -0.088388375000000005, 1.9626161806840515e-17], [-0.46338837500000007, 0.088388375000000005, -1.9626161806840515e-17], [-0.5, 0.0, 0.0], [-0.46338837500000007, -0.088388375000000005, 1.9626161806840515e-17], [-0.28661162499999998, 0.088388375000000005, -1.9626161806840515e-17], [-0.25, 0.0, 0.0], [0.0, 0.0, 0.0], [0.25, 0.0, 0.0], [0.28661162499999998, -0.088388375000000005, 1.9626161806840515e-17], [0.375, -0.125, 2.7755575615628914e-17], [0.46338837500000007, -0.088388375000000005, 1.9626161806840515e-17], [0.5, 0.0, 0.0], [0.46338837500000007, 0.088388375000000005, -1.9626161806840515e-17], [0.375, 0.125, -2.7755575615628914e-17], [0.28661162499999998, 0.088388375000000005, -1.9626161806840515e-17], [0.25, 0.0, 0.0], [0.28661162499999998, -0.088388375000000005, 1.9626161806840515e-17], [0.46338837500000007, 0.088388375000000005, -1.9626161806840515e-17], [0.5, 0.0, 0.0], [0.46338837500000007, -0.088388375000000005, 1.9626161806840515e-17], [0.28661162499999998, 0.088388375000000005, -1.9626161806840515e-17], [0.25, 0.0, 0.0], [0.0, 0.0, 0.0], [-2.7755575615628914e-17, -0.25, 5.5511151231257827e-17], [-0.088388375000000033, -0.28661162499999998, 6.3640565040046222e-17], [-0.12500000000000006, -0.375, 8.3266726846886741e-17], [-0.088388375000000061, -0.46338837500000007, 1.0289288865372727e-16], [-5.5511151231257827e-17, -0.5, 1.1102230246251565e-16], [0.08838837499999995, -0.46338837500000007, 1.0289288865372727e-16], [0.12499999999999996, -0.375, 8.3266726846886741e-17], [0.088388374999999977, -0.28661162499999998, 6.3640565040046222e-17], [-2.7755575615628914e-17, -0.25, 5.5511151231257827e-17], [0.088388374999999977, -0.28661162499999998, 6.3640565040046222e-17], [-0.088388375000000061, -0.46338837500000007, 1.0289288865372727e-16], [-5.5511151231257827e-17, -0.5, 1.1102230246251565e-16], [0.08838837499999995, -0.46338837500000007, 1.0289288865372727e-16], [-0.088388375000000033, -0.28661162499999998, 6.3640565040046222e-17], [-2.7755575615628914e-17, -0.25, 5.5511151231257827e-17], [2.7755575615628914e-17, 0.25, -5.5511151231257827e-17], [-0.088388374999999977, 0.28661162499999998, -6.3640565040046222e-17], [-0.12499999999999996, 0.375, -8.3266726846886741e-17], [-0.08838837499999995, 0.46338837500000007, -1.0289288865372727e-16], [5.5511151231257827e-17, 0.5, -1.1102230246251565e-16], [0.088388375000000061, 0.46338837500000007, -1.0289288865372727e-16], [0.12500000000000006, 0.375, -8.3266726846886741e-17], [0.088388375000000033, 0.28661162499999998, -6.3640565040046222e-17], [2.7755575615628914e-17, 0.25, -5.5511151231257827e-17], [0.088388375000000033, 0.28661162499999998, -6.3640565040046222e-17], [-0.08838837499999995, 0.46338837500000007, -1.0289288865372727e-16], [5.5511151231257827e-17, 0.5, -1.1102230246251565e-16], [0.088388375000000061, 0.46338837500000007, -1.0289288865372727e-16], [-0.088388374999999977, 0.28661162499999998, -6.3640565040046222e-17]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0))
        return createBuffer
    #>>> Character #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'eye':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[0.042006584699803277, 0.17069043513773416, 0.0], [0.037165726718830387, 0.16095623697775083, 0.0], [0.034371674461356139, 0.15002661097355802, 0.0], [0.034371674461356139, 0.13842138080096569, 0.0], [0.034371674461356139, 0.098314984890458354, 0.0], [0.066888144874591701, 0.065798514477223263, 0.0], [0.1069953738358615, 0.065798514477223263, 0.0], [0.11624057119824927, 0.065798514477223263, 0.0], [0.12505091606260491, 0.067596238022729419, 0.0], [0.13318648980932346, 0.070744336854272158, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.13318648980932346, 0.070744336854272158, 0.0], [0.16033394805815201, 0.081263268832545671, 0.0], [0.1796182401596044, 0.10756434750665984, 0.0], [0.1796182401596044, 0.13842138080096569, 0.0], [0.1796182401596044, 0.17852860976223595, 0.0], [0.14710176974636929, 0.21104508017547102, 0.0], [0.1069953738358615, 0.21104508017547102, 0.0], [0.078493375047184039, 0.21104508017547102, 0.0], [0.053895885182412506, 0.19458316405741946, 0.0], [0.042006584699803277, 0.17069043513773416, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.034371674461356139, 0.13842138080096569, 0.0], [0.034371674461356139, 0.15002661097355802, 0.0], [0.037165726718830387, 0.16095623697775083, 0.0], [0.042006584699803277, 0.17069043513773416, 0.0], [0.028786902149457508, 0.17495315588952276, 0.0], [0.014712509516771805, 0.17731652090277625, 0.0], [7.3308467101231836e-05, 0.17731652090277625, 0.0], [-0.075316119438952736, 0.17731652090277625, 0.0], [-0.13642789032626798, 0.1161964195078366, 0.0], [-0.13642789032626798, 0.040806991601783096, 0.0], [-0.13642789032626798, -0.034583269355034266, 0.0], [-0.075316119438952736, -0.095703370749974384, 0.0], [7.3308467101231836e-05, -0.095703370749974384, 0.0], [0.075462736373155204, -0.095703370749974384, 0.0], [0.13658283776809577, -0.034583269355034266, 0.0], [0.13658283776809577, 0.040806991601783096, 0.0], [0.13658283776809577, 0.051105998178751284, 0.0], [0.13534659043652369, 0.061095942922827266, 0.0], [0.13318648980932346, 0.070744336854272158, 0.0], [0.12505091606260491, 0.067596238022729419, 0.0], [0.11624057119824927, 0.065798514477223263, 0.0], [0.1069953738358615, 0.065798514477223263, 0.0], [0.066888144874591701, 0.065798514477223263, 0.0], [0.034371674461356139, 0.098314984890458354, 0.0], [0.034371674461356139, 0.13842138080096569, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.23925384509574379, 0.040806991601783096, 0.0], [0.23925384509574379, -0.091285702556359136, 0.0], [0.13217766533591749, -0.19837021282381007, 0.0], [7.7473720914016399e-05, -0.19837021282381007, 0.0], [-0.13201522043722774, -0.19837021282381007, 0.0], [-0.23909889765391529, -0.091285702556359136, 0.0], [-0.23909889765391529, 0.040806991601783096, 0.0], [-0.23909889765391529, 0.17290301796297378, 0.0], [-0.13201522043722774, 0.27998336297661147, 0.0], [7.7473720914016399e-05, 0.27998336297661147, 0.0], [0.13217766533591749, 0.27998336297661147, 0.0], [0.23925384509574379, 0.17290301796297378, 0.0], [0.23925384509574379, 0.040806991601783096, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.45838118376913201, 0.024145976351489188, 0.0], [-0.43338966089369158, -0.039911462032078238, 0.0], [-0.30010153889134128, -0.3151764254898069, 0.0], [-0.0085337720112004436, -0.3151764254898069, 0.0], [0.27053823343122052, -0.3151764254898069, 0.0], [0.38356156258463814, -0.15964584812831437, 0.0], [0.44547889355930492, 0.024145976351489188, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.50000123291512855, -0.00084554652395190679, 0.0], [-0.45900347268873037, 0.12180118503803529, 0.0], [-0.29982080078437379, 0.3151764254898069, 0.0], [7.7473720914016399e-05, 0.3151764254898069, 0.0], [0.29455758606680593, 0.3151764254898069, 0.0], [0.46213990880959838, 0.076594019308650563, 0.0], [0.50000123291512855, -0.045118029297795521, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        return combineCurves(createdCurves)                  
    elif desiredShape == 'teeth':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[0.0035452534401896724, -0.12635142854758835, 0.0], [0.027080320620084496, -0.10299287186429079, 0.0], [0.069566196571074546, -0.098438700471957186, 0.0], [0.095265523135390384, -0.11938829003691286, 0.0], [0.12725303614100578, -0.14545969270485343, 0.0], [0.10256262752883295, -0.19822931088376508, 0.0], [0.11447207154644319, -0.23416323754911003, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.39681164276072656, -0.16494003296574228, 0.0], [0.40371661303956802, -0.20704380380761986, 0.0], [0.42833882441441812, -0.24147939705298099, 0.0], [0.41345176866726763, -0.28528809882790657, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.1153135051069305, -0.14364745141307983, 0.0], [-0.12074922608170514, -0.15765295757778836, 0.0], [-0.11850674045447276, -0.1732550814162685, 0.0], [-0.11320841685489157, -0.18682934034497301, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.48908049905615064, 0.23729830466481919, 0.0], [-0.43400922411762405, 0.2851416753477739, 0.0], [-0.33926220056598966, 0.30012601244816178, 0.0], [-0.27149821628119913, 0.32317166416021764, 0.0], [-0.17945501260926802, 0.35448221929535689, 0.0], [-0.083356079117781076, 0.38418713065178622, 0.0], [0.014808829504338197, 0.37965301727042849, 0.0], [0.079477862695372367, 0.37666537653539961, 0.0], [0.15853450716022846, 0.3698296063944293, 0.0], [0.21991302365048063, 0.3483023461133351, 0.0], [0.26412288564494613, 0.3327884775231536, 0.0], [0.30675618797661824, 0.31217285384096405, 0.0], [0.35072134223716472, 0.29739310845254152, 0.0], [0.40003396222418675, 0.28083221168935885, 0.0], [0.46608398947098773, 0.27909819664039476, 0.0], [0.49376203881818759, 0.22977655054843352, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.11871233506698611, -0.16107084264827418, 0.0], [0.1186341088241766, -0.17164843473700916, 0.0], [0.11592126283953362, -0.18186397972760993, 0.0], [0.11183745180461063, -0.19123608535662454, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.15026860083659566, 0.086863222337114035, 0.0], [-0.13631223679878052, 0.12317825121102249, 0.0], [-0.18517455443936831, 0.15046416644362126, 0.0], [-0.21559453388712727, 0.13518597948241953, 0.0], [-0.24562237922028604, 0.12010335812824437, 0.0], [-0.26085242695514238, 0.070918106510925727, 0.0], [-0.26566133508688461, 0.041790865870635872, 0.0], [-0.27090048755408469, 0.010049063499490314, 0.0], [-0.26692398687788915, -0.027374170480897859, 0.0], [-0.24241008876231543, -0.050350622055082971, 0.0], [-0.22227385154247806, -0.069223204583368711, 0.0], [-0.15909312276593909, -0.079282297088347678, 0.0], [-0.15277585220872436, -0.041006597641434571, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.45866051960839122, 0.12697924429116927, 0.0], [-0.45814101712408578, 0.1557725190486911, 0.0], [-0.50000108313259284, 0.20962025531761933, 0.0], [-0.48874753607393201, 0.23980555603694745, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.33499185002897985, -0.10978050277891707, 0.0], [0.34285659613307273, -0.062338292315502704, 0.0], [0.39342284180615866, -0.11498054212471145, 0.0], [0.39680161375523881, -0.13987654534939761, 0.0], [0.40160049288149141, -0.1753902566847734, 0.0], [0.37216034726996033, -0.21987391052907682, 0.0], [0.33975261893437575, -0.1875052953148979, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.11801732498663192, -0.13867206179022806, 0.0], [0.13243402037637181, -0.11219949890274669, 0.0], [0.17711424272824886, -0.095148183771176134, 0.0], [0.19650632774083954, -0.12387326129137667, 0.0], [0.21138335448249951, -0.14590999505128766, 0.0], [0.20001246805962258, -0.18756346354673195, 0.0], [0.19423375509714119, -0.21182362782344694, 0.0], [0.18802379489865298, -0.23796322772870834, 0.0], [0.17433219660573418, -0.27591499029834116, 0.0], [0.14577360057664318, -0.27110608216659893, 0.0], [0.11782075647905735, -0.26638542928315578, 0.0], [0.11177828067222856, -0.22384038219978369, 0.0], [0.11127883619890185, -0.1967410064692699, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.29511150970390437, -0.13763405972216619, 0.0], [0.29819643179217115, -0.16946411734161082, 0.0], [0.29199650059917348, -0.21486943679030804, 0.0], [0.26396643315932616, -0.22909056657302043, 0.0], [0.24790498086947213, -0.23723913353243711, 0.0], [0.19936559720561378, -0.23785591736997994, 0.0], [0.20423367646973808, -0.20505605491979703, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.29840202640468638, -0.10903635057166948, 0.0], [0.331025378358272, -0.081446556472769618, 0.0], [0.34801852525800947, -0.124745784768878, 0.0], [0.34931126406547908, -0.15773118382059878, 0.0], [0.35012361351004934, -0.17812215777984475, 0.0], [0.34908561144198746, -0.19885612372679842, 0.0], [0.33320969575367032, -0.21069737050708595, 0.0], [0.32133936485746489, -0.21954094754685777, 0.0], [0.2979908371796578, -0.22286155126410387, 0.0], [0.28745235821232668, -0.21007055766405447, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.36087771609538249, 0.11444298743052662, 0.0], [-0.36945753029080597, 0.1305926949686807, 0.0], [-0.39722283198575603, 0.13926979051734301, 0.0], [-0.41169869850787705, 0.13016144773267391, 0.0], [-0.42896563725745052, 0.1193100637941029, 0.0], [-0.4301209786897276, 0.0894677550624806, 0.0], [-0.43108075451497907, 0.07181971410434361, 0.0], [-0.4339309978748136, 0.019215574515991575, 0.0], [-0.41898477099528197, -0.005738596940527702, 0.0], [-0.36589221883963996, -0.0059050784316372253, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.42105174902646514, 0.11695023880265534, 0.0], [-0.43954222644563656, 0.16350989678308067, 0.0], [-0.47705371567432475, 0.11586309460769957, 0.0], [-0.47869847257444126, 0.086863222337114035, 0.0], [-0.48005038251429288, 0.063034305296406315, 0.0], [-0.45463487680530129, -0.0082167641967393953, 0.0], [-0.42105174902646514, 0.021674686661775841, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.25808040983811731, 0.086863222337114035, 0.0], [0.26831500993914459, 0.11924186655678067, 0.0], [0.31243661668531381, 0.13486304550568962, 0.0], [0.34270014364745094, 0.12133792870388035, 0.0], [0.36901625404931054, 0.10958493717189052, 0.0], [0.37960387514353511, 0.070467804164492429, 0.0], [0.37604859269785679, 0.044239949010930542, 0.0], [0.3722285445072821, 0.016033371074485998, 0.0], [0.35622526044926023, -0.0284512856703645, 0.0], [0.32816610889349684, -0.043024433545723377, 0.0], [0.31167340936763599, -0.051584189730170475, 0.0], [0.30831369252898416, -0.049625524958264673, 0.0], [0.29374054465362531, -0.035434482192017322, 0.0], [0.2856210618101247, -0.027530622966518724, 0.0], [0.27061666669875811, -0.012555311971070069, 0.0], [0.27312391807088776, -0.0033978270595085105, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.36087771609538155, 0.11444298743052662, 0.0], [0.36945753029080597, 0.1305926949686807, 0.0], [0.39722283198575603, 0.13926979051734301, 0.0], [0.41169869850787705, 0.13016144773267391, 0.0], [0.42896563725745052, 0.1193100637941029, 0.0], [0.43012097868972665, 0.0894677550624806, 0.0], [0.43108075451497718, 0.07181971410434361, 0.0], [0.43393099787481271, 0.019215574515991575, 0.0], [0.41898477099528103, -0.005738596940527702, 0.0], [0.36589221883963902, -0.0059050784316372253, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.42105174902646325, 0.11695023880265534, 0.0], [0.4395432293461855, 0.16350989678308067, 0.0], [0.47705371567432475, 0.11586309460769957, 0.0], [0.47869847257444081, 0.086863222337114035, 0.0], [0.48005038251429244, 0.063034305296406315, 0.0], [0.45463487680530035, -0.0082167641967393953, 0.0], [0.42105174902646325, 0.021674686661775841, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.15026860083659566, 0.086863222337114035, 0.0], [0.13631223679878052, 0.12317825121102249, 0.0], [0.18517455443936645, 0.15046416644362126, 0.0], [0.21559453388712635, 0.13518597948241953, 0.0], [0.24562237922028513, 0.12010335812824437, 0.0], [0.26085242695514238, 0.070918106510925727, 0.0], [0.26566133508688461, 0.041790865870635872, 0.0], [0.27090048755408375, 0.010049063499490314, 0.0], [0.26692398687788821, -0.027374170480897859, 0.0], [0.24241008876231449, -0.050350622055082971, 0.0], [0.22227385154247714, -0.069223204583368711, 0.0], [0.15909312276593815, -0.079282297088347678, 0.0], [0.15277585220872436, -0.041006597641434571, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.45866051960839122, 0.12697924429116927, 0.0], [0.45814101712408528, 0.1557725190486911, 0.0], [0.50000108313259195, 0.20962025531761933, 0.0], [0.48874753607393201, 0.23980555603694745, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.0073552726252766208, 0.056776205871573185, 0.0], [-0.0026536748522599852, 0.10170013305682216, 0.0], [-0.033926119766543882, 0.1310921394420079, 0.0], [-0.075051059672744461, 0.13450099840755403, 0.0], [-0.12096484969970714, 0.13830098858715231, 0.0], [-0.13523512160931389, 0.10910454780899079, 0.0], [-0.1426876755878293, 0.071760542971961536, 0.0], [-0.14932788012177253, 0.038510378175343474, 0.0], [-0.15773118382059878, -0.011262573163601429, 0.0], [-0.15277585220872436, -0.046021100385692001, 0.0], [-0.14643952654108033, -0.090417501882243401, 0.0], [-0.089506868183887214, -0.083992920966301218, 0.0], [-0.054993048695715675, -0.080996254126333531, 0.0], [-0.01243797260685489, -0.077293545299974037, 0.0], [-0.0046424266406336328, -0.073561752357699378, 0.0], [-0.0028993854867298318, -0.028470340780791928, 0.0], [-0.0015665306573065499, 0.0059161103376739127, 0.0], [-0.0048480212531479064, 0.041614355374038618, 0.0], [-0.0048480212531479064, 0.076834216848600576, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.25808040983811825, 0.086863222337114035, 0.0], [-0.26831500993914648, 0.11924186655678067, 0.0], [-0.31243661668531286, 0.13486304550568962, 0.0], [-0.34270014364745188, 0.12133792870388035, 0.0], [-0.36901625404931054, 0.10958493717189052, 0.0], [-0.37960387514353511, 0.070467804164492429, 0.0], [-0.37604859269785768, 0.044239949010930542, 0.0], [-0.37222854450728304, 0.016033371074485998, 0.0], [-0.35622526044926112, -0.0284512856703645, 0.0], [-0.32816610889349779, -0.043024433545723377, 0.0], [-0.31167240646708794, -0.051584189730170475, 0.0], [-0.30831369252898605, -0.049625524958264673, 0.0], [-0.29374054465362626, -0.035434482192017322, 0.0], [-0.2856210618101247, -0.027530622966518724, 0.0], [-0.27061666669875994, -0.012555311971070069, 0.0], [-0.2731239180708887, -0.0033978270595085105, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.0073552726252756884, 0.056776205871573185, 0.0], [0.0026546777528089443, 0.10170013305682216, 0.0], [0.033926119766543882, 0.1310921394420079, 0.0], [0.075051059672742587, 0.13450099840755403, 0.0], [0.12096484969970714, 0.13830098858715231, 0.0], [0.13523512160931295, 0.10910454780899079, 0.0], [0.14268767558782836, 0.071760542971961536, 0.0], [0.14932888302232245, 0.038510378175343474, 0.0], [0.15773118382059786, -0.011262573163601429, 0.0], [0.15277585220872436, -0.046021100385692001, 0.0], [0.14643952654108128, -0.090417501882243401, 0.0], [0.089506868183886285, -0.083992920966301218, 0.0], [0.054993048695714739, -0.080996254126333531, 0.0], [0.01243797260685489, -0.077293545299974037, 0.0], [0.0046424266406327004, -0.073561752357699378, 0.0], [0.0028993854867298318, -0.028470340780791928, 0.0], [0.0015675335578545766, 0.0059161103376739127, 0.0], [0.0048480212531469731, 0.041614355374038618, 0.0], [0.0048480212531469731, 0.076834216848600576, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.11659721780945945, -0.25171399715400827, 0.0], [0.1018967015643958, -0.27743338172930326, 0.0], [0.077509168917977905, -0.31801876114021876, 0.0], [0.046207639887777908, -0.31188803008509086, 0.0], [0.015690379086779224, -0.30590372251009423, 0.0], [0.0058759943157202033, -0.26549385069522707, 0.0], [0.0056804287086945904, -0.23416323754911003, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.0035452534401896724, -0.11381517168694666, 0.0], [0.0035452534401896724, -0.15560603755758254, 0.0], [0.0048771053690639951, -0.19879695259441543, 0.0], [0.0014201071771724821, -0.23917774029336747, 0.0], [-0.0010380020680609578, -0.26782559447130561, 0.0], [-0.02118426829338697, -0.31317073988707178, 0.0], [-0.051378595117656203, -0.3164131173615084, 0.0], [-0.07891924708966358, -0.31938070008555908, 0.0], [-0.10912460581996858, -0.257541852243384, 0.0], [-0.11387434281932873, -0.22914873480485354, 0.0], [-0.11847765633855574, -0.20169633808114526, 0.0], [-0.12136701281979692, -0.13119944980073533, 0.0], [-0.10095598084957363, -0.11694923590210778, 0.0], [-0.076775045716218959, -0.10004534715121745, 0.0], [-0.014201071771736943, -0.094628681286872102, 0.0], [0.0014201071771724821, -0.12635142854758835, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.20405716597314083, -0.12885867991971614, 0.0], [0.21492860792268917, -0.1134140114674049, 0.0], [0.25044131635751599, -0.096127014706855016, 0.0], [0.26803118908382084, -0.098781692459663964, 0.0], [0.2876679818303296, -0.1017392461782269, 0.0], [0.30782427706114518, -0.13152238377746667, 0.0], [0.29364226039983754, -0.15142394226887271, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.29720757185100455, -0.1539311936410005, 0.0], [-0.29722662696143293, -0.11503971325709446, 0.0], [-0.29553272793442437, -0.10924194518418469, 0.0], [-0.26307485457139745, -0.11130792031481794, 0.0], [-0.23922688242026088, -0.11282631174577817, 0.0], [-0.22024598663269968, -0.11138614655762838, 0.0], [-0.20548730215580291, -0.13638043403610228, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.41389204200821411, -0.28528809882790657, 0.0], [-0.41363730526880643, -0.29941997046177093, 0.0], [-0.33912580609134518, -0.33206338042633393, 0.0], [-0.32301420877404874, -0.3398208161716994, 0.0], [-0.26936304101269609, -0.36567659522163698, 0.0], [-0.2053689598910397, -0.36950566951715136, 0.0], [-0.14761392308378671, -0.37541175084933665, 0.0], [-0.070976274742760234, -0.38325643894245037, 0.0], [0.01030279733834997, -0.38418713065178572, 0.0], [0.087812969156875892, -0.38069101933849042, 0.0], [0.17065957479584068, -0.37695922639621482, 0.0], [0.24459440615771375, -0.34483531891595681, 0.0], [0.32322983239205078, -0.32107459911256947, 0.0], [0.348429714483038, -0.31346458974788516, 0.0], [0.40591998554539377, -0.30645230911031529, 0.0], [0.42296127167147751, -0.28528809882790657, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.39693901113043129, -0.16494003296574228, 0.0], [-0.40384398140927275, -0.20704380380761986, 0.0], [-0.4284661927841229, -0.24147939705298099, 0.0], [-0.41356910803148372, -0.28528809882790657, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.11640064930188487, -0.14237477061658663, 0.0], [-0.12700832840708581, -0.11713577540419276, 0.0], [-0.15928868837296564, -0.10301292987526811, 0.0], [-0.18296115292805296, -0.11285539586169613, 0.0], [-0.2135867269883262, -0.12557819222442468, 0.0], [-0.20167728297071597, -0.16967974095961469, 0.0], [-0.19717225370527669, -0.19753430080341183, 0.0], [-0.19307841366486597, -0.22273418289440003, 0.0], [-0.17916116274845467, -0.28014622771394532, 0.0], [-0.14242391274348004, -0.27036192995935132, 0.0], [-0.11474586339628016, -0.262996628328587, 0.0], [-0.11006432363424271, -0.20849299510071032, 0.0], [-0.11164088329703699, -0.18499804394277011, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.33512924740417327, -0.10978050277891707, 0.0], [-0.34299399350826526, -0.062338292315502704, 0.0], [-0.3935502101758625, -0.11498054212471145, 0.0], [-0.39692898212494265, -0.13987654534939761, 0.0], [-0.40172786125119619, -0.1753902566847734, 0.0], [-0.37229774464515281, -0.21987391052907682, 0.0], [-0.33986995829859279, -0.1875052953148979, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.29470934658381553, -0.11228775415104579, 0.0], [-0.33497279491855148, -0.075824295995907204, 0.0], [-0.3508196264909525, -0.12861397218579712, 0.0], [-0.34938949030829042, -0.16494003296574228, 0.0], [-0.34858616696866074, -0.18507627018558057, 0.0], [-0.3496833401691038, -0.19901257621241836, 0.0], [-0.33334709312886379, -0.21069737050708595, 0.0], [-0.32076169414132866, -0.21968837392753798, 0.0], [-0.29420087600554817, -0.22131407571722661, 0.0], [-0.28756969757654371, -0.21007055766405447, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.29577743566834341, -0.14548877682076952, 0.0], [-0.29701100334343, -0.17684947698335249, 0.0], [-0.28962664660223725, -0.21772870625508228, 0.0], [-0.26184128689630992, -0.22997111325491157, 0.0], [-0.24578886071139558, -0.23705259403035123, 0.0], [-0.19963036295051106, -0.23697436778754077, 0.0], [-0.20437007094438256, -0.20505605491979703, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0)))
        return combineCurves(createdCurves)          
    elif desiredShape == 'foot':
        createBuffer = mc.curve( d = 1,p = [[-0.02352681782276193, -0.32411800821432263, -7.196865508303732e-17], [0.11331543518270899, -0.26727569434151321, -5.9347125956124728e-17], [0.14910507243792875, -0.17885509058662971, -3.971380792813888e-17], [0.11963115116266866, 0.0085136733063737625, 1.8904152257745471e-18], [0.25015768818817991, 0.16009210390161943, 3.554758796245215e-17], [0.26699959746807228, 0.33693447148228317, 7.4814481605907795e-17], [0.22489482426834137, 0.48430291778768692, 1.0753685004420686e-16], [0.11121019652272246, 0.58325116493112417, 1.2950777448919574e-16], [-0.03826377846039198, 0.67588166597053234, 1.5007587749649883e-16], [-0.16036936084595707, 0.6695662400082969, 1.4867357123378098e-16], [-0.18984212205032036, 0.49061950382081915, 1.0893941389440868e-16], [-0.16668478680819251, 0.18535612789235481, 4.11573281882915e-17], [-0.10563199561540997, 0.031671675589267277, 7.0325246935326107e-18], [-0.15405277481282481, -0.11569677071613642, -2.5689843744766443e-17], [-0.13510533685522166, -0.24411835909938534, -5.420516460116994e-17], [-0.02352681782276193, -0.32411800821432263, -7.196865508303732e-17]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0))
        return createBuffer
    #>>> Special #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'gear':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[0.36589275643190788, -2.0408077971202743e-06, 0.0], [0.36589275643190788, 0.066658905066453847, 0.0], [0.34805936158046424, 0.12914272554224085, 0.0], [0.31691745092461332, 0.18297352095965108, 0.0], [0.32982339037080916, 0.19042448106665821, 0.0], [0.42016612804034642, 0.24258187240882675, 0.0], [0.43307206748654231, 0.25003283251583436, 0.0], [0.38917102648517926, 0.3259051684616634, 0.0], [0.32590598478478217, 0.38917021016206016, 0.0], [0.25003283251583447, 0.4330720674865422, 0.0], [0.24258141890051846, 0.42016612804034631, 0.0], [0.1904208529593738, 0.32982339037080882, 0.0], [0.18296943934405777, 0.31691745092461299, 0.0], [0.12914354186535973, 0.34805936158046391, 0.0], [0.066655639773978939, 0.365892756431908, 0.0], [-2.0408077968871564e-06, 0.365892756431908, 0.0], [-2.0408077968871564e-06, 0.38079340682265889, 0.0], [-2.0408077968871564e-06, 0.48509930062986206, 0.0], [-2.0408077968871564e-06, 0.49999995102061295, 0.0], [-0.091089007040231817, 0.49999995102061295, 0.0], [-0.17647967055027494, 0.47562944063450113, 0.0], [-0.25003283251583469, 0.4330720674865422, 0.0], [-0.24258178170716541, 0.42016612804034631, 0.0], [-0.19042375544520174, 0.32982339037080882, 0.0], [-0.18297270463653242, 0.31691745092461299, 0.0], [-0.23849328890968227, 0.28479023826447297, 0.0], [-0.28479023826447353, 0.23849328890968163, 0.0], [-0.3169166346014945, 0.18296943934405777, 0.0], [-0.3298225740476905, 0.1904208529593738, 0.0], [-0.42016531171722776, 0.24258141890051832, 0.0], [-0.43307125116342365, 0.25003283251583436, 0.0], [-0.47562944063450124, 0.17647967055027458, 0.0], [-0.4999999510206129, 0.091084925424638155, 0.0], [-0.4999999510206129, -2.0408077971202743e-06, 0.0], [-0.48509920992820016, -2.0408077971202743e-06, 0.0], [-0.3807926812012018, -2.0408077971202743e-06, 0.0], [-0.36589194010878912, -2.0408077971202743e-06, 0.0], [-0.36589194010878912, -0.066662986682047162, 0.0], [-0.34805936158046419, -0.12914680715783416, 0.0], [-0.3169166346014945, -0.182973520959652, 0.0], [-0.3298225740476905, -0.19042448106665916, 0.0], [-0.42016531171722776, -0.2425818724088277, 0.0], [-0.43307125116342365, -0.25003283251583486, 0.0], [-0.38917021016206038, -0.32590925007725718, 0.0], [-0.32590925007725674, -0.38916694486958558, 0.0], [-0.25003609780830954, -0.43307614910213643, 0.0], [-0.25003573500166265, -0.43307614910213643, 0.0], [-0.25003319532248164, -0.43307614910213643, 0.0], [-0.25003283251583469, -0.43307614910213643, 0.0], [-0.24258178170716541, -0.42016975614763213, 0.0], [-0.19042375544520174, -0.32982384387911723, 0.0], [-0.18297270463653242, -0.31691745092461343, 0.0], [-0.12914680715783453, -0.34806344319605814, 0.0], [-0.066658905066453972, -0.36589683804750223, 0.0], [-2.0408077968871564e-06, -0.36589683804750223, 0.0], [-2.0408077968871564e-06, -0.38079703492994471, 0.0], [-2.0408077968871564e-06, -0.48509975413817047, 0.0], [-2.0408077968871564e-06, -0.49999995102061295, 0.0], [0.09108574174775691, -0.49999995102061295, 0.0], [0.17647640525780015, -0.47562944063450163, 0.0], [0.25003283251583447, -0.43307614910213643, 0.0], [0.24258141890051846, -0.42016975614763213, 0.0], [0.1904208529593738, -0.32982384387911723, 0.0], [0.18296943934405777, -0.31691745092461343, 0.0], [0.23849410523280098, -0.28479023826447342, 0.0], [0.28478697297199862, -0.23849737052527589, 0.0], [0.31691745092461332, -0.182973520959652, 0.0], [0.32982339037080916, -0.19042448106665916, 0.0], [0.42016612804034642, -0.2425818724088277, 0.0], [0.43307206748654231, -0.25003283251583486, 0.0], [0.47563025695762001, -0.17648375216586881, 0.0], [0.49999995102061284, -0.091089007040231457, 0.0], [0.49999995102061284, -2.0408077971202743e-06, 0.0], [0.48509930062986167, -2.0408077971202743e-06, 0.0], [0.38079340682265889, -2.0408077971202743e-06, 0.0], [0.36589275643190788, -2.0408077971202743e-06, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0, 8.0, 8.0, 8.0, 9.0, 9.0, 9.0, 10.0, 10.0, 10.0, 11.0, 11.0, 11.0, 12.0, 12.0, 12.0, 13.0, 13.0, 13.0, 14.0, 14.0, 14.0, 15.0, 15.0, 15.0, 16.0, 16.0, 16.0, 17.0, 17.0, 17.0, 18.0, 18.0, 18.0, 19.0, 19.0, 19.0, 20.0, 20.0, 20.0, 21.0, 21.0, 21.0, 22.0, 22.0, 22.0, 23.0, 23.0, 23.0, 24.0, 24.0, 24.0, 25.0, 25.0, 25.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-2.0408077968871564e-06, -0.21854398453452986, 0.0], [-0.1206962302328989, -0.21854398453452986, 0.0], [-0.21854316821141118, -0.12069704655601754, 0.0], [-0.21854316821141118, -2.0408077971202743e-06, 0.0], [-0.21854316821141118, 0.12069296494042377, 0.0], [-0.1206962302328989, 0.21853990291893702, 0.0], [-2.0408077968871564e-06, 0.21853990291893702, 0.0], [0.12069704655601754, 0.21853990291893702, 0.0], [0.21854398453453011, 0.12069296494042377, 0.0], [0.21854398453453011, -2.0408077971202743e-06, 0.0], [0.21854398453453011, -0.12069704655601754, 0.0], [0.12069704655601754, -0.21854398453452986, 0.0], [-2.0408077968871564e-06, -0.21854398453452986, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0)))
        return combineCurves(createdCurves)          
    elif desiredShape == 'dumbell':
        createBuffer = mc.curve( d = 1,p = [[-0.99849159389068964, 0.0, 0.021042779369566156], [-0.92904412938768721, -0.16766137908274195, 0.021042779369566156], [-0.76138275030494529, -0.23710884358574422, 0.021042779369566156], [-0.59372137122220348, -0.16766137908274195, 0.021042779369566156], [-0.52510409775306377, -0.0020051263364880313, 0.021042779369566156], [0.52431938531169364, 0.0, 0.021042779369566156], [0.59372137122220348, -0.16766137908274195, 0.021042779369566156], [0.76138275030494529, -0.23710884358574422, 0.021042779369566156], [0.92904412938768721, -0.16766137908274195, 0.021042779369566156], [0.99849159389068964, 0.0, 0.021042779369566156], [0.92904412938768721, 0.16766137908274195, 0.021042779369566156], [0.76138275030494529, 0.23710884358574422, 0.021042779369566156], [0.59372137122220348, 0.16766137908274195, 0.021042779369566156], [0.52431938531169364, 0.0, 0.021042779369566156], [-0.52510409775306377, -0.0020051263364880313, 0.021042779369566156], [-0.59372137122220348, 0.16766137908274195, 0.021042779369566156], [-0.76138275030494529, 0.23710884358574422, 0.021042779369566156], [-0.92904412938768721, 0.16766137908274195, 0.021042779369566156], [-0.99849159389068964, 0.0, 0.021042779369566156]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0))
        return createBuffer  
    elif desiredShape == 'locator':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.99266615978157735, 0.0], [0.0, -0.99266615978157735, 0.0], [0.0, 0.0, 0.0], [-0.99266615978157735, 0.0, 0.0], [0.99266615978157735, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.99266615978157735], [0.0, 0.0, -0.99266615978157735]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0))
        return createBuffer         
    elif desiredShape == 'arrowsLocator':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[0.27118679483659736, -0.083333333795273246, 3.4139358007223564e-15], [0.29190230828476249, -0.083333333795273246, 3.4416913763379853e-15], [0.31261782173292774, -0.083333333795273246, 3.4139358007223564e-15], [0.33333333518109298, -0.083333333795273246, 3.4139358007223564e-15], [0.33333333518109309, -0.11111111172703098, 4.5796699765787707e-15], [0.33333333518109309, -0.13888888965878873, 5.7176485768195562e-15], [0.33333333518109298, -0.16666666759054649, 6.8278716014447127e-15], [0.38888889104460844, -0.111111111727031, 4.5519144009631418e-15], [0.44444444690812401, -0.055555555863515502, 2.2759572004815709e-15], [0.50000000277163936, -7.640365658541241e-33, 0.0], [0.44444444690812401, 0.055555555863515488, -2.2759572004815709e-15], [0.3888888910446085, 0.111111111727031, -4.5519144009631418e-15], [0.33333333518109298, 0.16666666759054649, -6.8278716014447127e-15], [0.33333333518109298, 0.13888888965878873, -5.6621374255882984e-15], [0.33333333518109282, 0.111111111727031, -4.5519144009631418e-15], [0.33333333518109298, 0.083333333795273246, -3.3861802251067274e-15], [0.31177689547826626, 0.083333333795273259, -3.4139358007223564e-15], [0.29022045577543959, 0.083333333795273259, -3.4416913763379853e-15], [0.27099051167032995, 0.080480877621542213, -3.3306690738754696e-15], [0.25751952042023729, 0.12535616460623125, -5.1902926401226068e-15], [0.20932747609621588, 0.20774123871711514, -8.5348395018058909e-15], [0.12735279003592717, 0.25634367109173173, -1.0519363158323358e-14], [0.083333333795273246, 0.26931547357622415, -1.1067535776732029e-14], [0.083333333795273232, 0.29065476077784713, -1.1948775302528247e-14], [0.083333333795273246, 0.31199404797947006, -1.2809198146612744e-14], [0.083333333795273246, 0.33333333518109298, -1.3690437672408962e-14], [0.111111111727031, 0.33333333518109304, -1.3697376566312869e-14], [0.13888888965878879, 0.33333333518109304, -1.3683498778505054e-14], [0.16666666759054652, 0.33333333518109298, -1.3683498778505054e-14], [0.11111111172703099, 0.3888888910446085, -1.597333376679444e-14], [0.055555555863515529, 0.44444444690812401, -1.8256229861179918e-14], [-4.7331654313260708e-30, 0.50000000277163936, -2.0539126069419494e-14], [-0.05555555586351546, 0.44444444690812401, -1.8256229861179918e-14], [-0.111111111727031, 0.3888888910446085, -1.597333376679444e-14], [-0.16666666759054644, 0.33333333518109304, -1.3697376566312869e-14], [-0.13888888965878871, 0.33333333518109298, -1.3697376566312869e-14], [-0.111111111727031, 0.33333333518109298, -1.3683498778505054e-14], [-0.083333333795273246, 0.33333333518109298, -1.3690437672408962e-14], [-0.083333333795273273, 0.31195288539590849, -1.2823075934420558e-14], [-0.083333333795273273, 0.29057243561072399, -1.1934897514720433e-14], [-0.083363006858912694, 0.2701089638456492, -1.1032841307212493e-14], [-0.12714010022923841, 0.25646968343124732, -1.04638520070921e-14], [-0.20784243041263012, 0.2086902967074338, -8.507083926190262e-15], [-0.2558376552563385, 0.12820380464393688, -5.2180482157382357e-15], [-0.27036130383202139, 0.083333333795273135, -3.4139358007223564e-15], [-0.29135198094837866, 0.083333333795273135, -3.4139358007223564e-15], [-0.31234265806473582, 0.083333333795273135, -3.4139358007223564e-15], [-0.33333333518109298, 0.083333333795273107, -3.4139358007223564e-15], [-0.33333333518109309, 0.11111111172703085, -4.5796699765787707e-15], [-0.33333333518109309, 0.13888888965878857, -5.7176485768195562e-15], [-0.33333333518109309, 0.16666666759054632, -6.8556271770603416e-15], [-0.3888888910446085, 0.11111111172703085, -4.5519144009631418e-15], [-0.44444444690812401, 0.055555555863515294, -2.2759572004815709e-15], [-0.50000000277163936, 7.640365658541241e-33, 0.0], [-0.44444444690812401, -0.055555555863515488, 2.2759572004815709e-15], [-0.3888888910446085, -0.111111111727031, 4.5519144009631418e-15], [-0.33333333518109298, -0.16666666759054649, 6.8278716014447127e-15], [-0.33333333518109298, -0.13888888965878873, 5.6621374255882984e-15], [-0.33333333518109254, -0.111111111727031, 4.5519144009631418e-15], [-0.33333333518109298, -0.083333333795273246, 3.3861802251067274e-15], [-0.3114889775600036, -0.083333333795273259, 3.4139358007223564e-15], [-0.28964461993891433, -0.083333333795273259, 3.4139358007223564e-15], [-0.26975757754999724, -0.084482843615394779, 3.4972025275692431e-15], [-0.25605873221651609, -0.12783260033492388, 5.2735593669694936e-15], [-0.20798179566549019, -0.20865859170634285, 8.5764728652293343e-15], [-0.12698295005352872, -0.25656267401682609, 1.0533240946131173e-14], [-0.083333333795273246, -0.26915158232531594, 1.1053657988924215e-14], [-0.083333333795273232, -0.29054549994390833, 1.1934897514720433e-14], [-0.083333333795273246, -0.31193941756250065, 1.2809198146612744e-14], [-0.083333333795273246, -0.33333333518109298, 1.3690437672408962e-14], [-0.111111111727031, -0.33333333518109304, 1.3697376566312869e-14], [-0.13888888965878879, -0.33333333518109304, 1.3683498778505054e-14], [-0.16666666759054652, -0.33333333518109298, 1.3683498778505054e-14], [-0.11111111172703099, -0.3888888910446085, 1.597333376679444e-14], [-0.055555555863515529, -0.44444444690812401, 1.8256229861179918e-14], [4.7331654313260708e-30, -0.50000000277163936, 2.0539126069419494e-14], [0.055555555863515432, -0.44444444690812401, 1.8259699308131871e-14], [0.111111111727031, -0.3888888910446085, 1.597333376679444e-14], [0.16666666759054644, -0.33333333518109304, 1.3697376566312869e-14], [0.13888888965878871, -0.33333333518109298, 1.3697376566312869e-14], [0.111111111727031, -0.33333333518109298, 1.3683498778505054e-14], [0.083333333795273246, -0.33333333518109298, 1.3690437672408962e-14], [0.083333333795273273, -0.31214589923031194, 1.2830014828324465e-14], [0.083333333795273273, -0.29095846327953073, 1.1955714196432154e-14], [0.083333333795273246, -0.26977102732874964, 1.1074474670635936e-14], [0.12710454503335678, -0.25649073116988785, 1.0449974219284286e-14], [0.20851651408788835, -0.20830277638265515, 8.4932061383824475e-15], [0.25664958492823176, -0.12683592338123434, 5.134781488891349e-15], [0.27026168104284992, -0.082871303667393689, 3.3029134982598407e-15]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.083333333795273301, 5.0963706130549176e-17, 0.27118679483659736], [-0.083333333795273287, 5.5563474129966158e-17, 0.29190230828476249], [-0.083333333795273287, 6.0163242129383183e-17, 0.31261782173292774], [-0.083333333795273301, 6.4763010128800221e-17, 0.33333333518109298], [-0.11111111172703104, 6.1679057265524021e-17, 0.33333333518109309], [-0.13888888965878876, 5.8595104402247847e-17, 0.33333333518109309], [-0.16666666759054655, 5.5511151538971598e-17, 0.33333333518109287], [-0.11111111172703098, 7.4014868718628831e-17, 0.38888889104460844], [-0.055555555863515543, 9.2518585898286038e-17, 0.44444444690812407], [-5.5511151231257827e-17, 1.110223030779432e-16, 0.50000000277163936], [0.055555555863515432, 1.0485439735139085e-16, 0.44444444690812401], [0.11111111172703095, 9.8686491624838424e-17, 0.3888888910446085], [0.16666666759054644, 9.2518585898286038e-17, 0.33333333518109298], [0.13888888965878865, 8.9434633035009827e-17, 0.33333333518109298], [0.11111111172703095, 8.6350680171733603e-17, 0.33333333518109282], [0.083333333795273162, 8.3266727308457441e-17, 0.33333333518109298], [0.083333333795273232, 7.8480236171053009e-17, 0.31177689547826631], [0.083333333795273218, 7.3693745033648614e-17, 0.29022045577543959], [0.080480877621542143, 2.1877484554653122e-17, 0.27099051167032995], [0.12535616460623117, 3.4076138780441208e-17, 0.25751952042023729], [0.20774123871711508, 5.6471249764076607e-17, 0.20932747609621585], [0.25634367109173173, 6.9683070944685038e-17, 0.1273527900359272], [0.26931547357622415, 4.8403741144872408e-17, 0.083333333795273246], [0.29065476077784713, 5.077287794290549e-17, 0.083333333795273232], [0.31199404797947006, 5.3142014740938559e-17, 0.083333333795273287], [0.33333333518109298, 5.5511151538971635e-17, 0.083333333795273246], [0.33333333518109298, 6.1679057265524034e-17, 0.11111111172703104], [0.33333333518109298, 6.7846962992076432e-17, 0.13888888965878879], [0.33333333518109293, 7.4014868718628831e-17, 0.16666666759054649], [0.38888889104460844, 6.7846962992076432e-17, 0.11111111172703095], [0.44444444690812407, 6.1679057265524021e-17, 0.055555555863515543], [0.50000000277163936, 5.5511151538971611e-17, 0.0], [0.44444444690812401, 3.7007434359314415e-17, -0.055555555863515432], [0.3888888910446085, 1.8503717179657208e-17, -0.11111111172703095], [0.33333333518109304, 1.367366549238959e-32, -0.16666666759054641], [0.33333333518109309, 6.1679057265524108e-18, -0.13888888965878871], [0.33333333518109309, 1.2335811453104803e-17, -0.11111111172703098], [0.33333333518109287, 1.8503717179657208e-17, -0.083333333795273218], [0.31195288539590849, 1.6130010416821824e-17, -0.083333333795273259], [0.29057243561072399, 1.3756303653986447e-17, -0.083333333795273232], [0.27010896384564931, 7.3424953345996006e-17, -0.08336300685891268], [0.25646968343124732, 6.97173254544881e-17, -0.12714010022923841], [0.20869029670743383, 5.6729236532341085e-17, -0.20784243041263009], [0.12820380464393691, 3.4850225778287795e-17, -0.2558376552563385], [0.083333333795273121, -5.0780410306568946e-17, -0.27036130383202139], [0.083333333795273218, -5.5441276913979373e-17, -0.29135198094837866], [0.083333333795273204, -6.01021435213898e-17, -0.31234265806473582], [0.083333333795273246, -6.4763010128800245e-17, -0.33333333518109298], [0.11111111172703092, -6.1679057265524034e-17, -0.33333333518109309], [0.13888888965878865, -5.8595104402247859e-17, -0.33333333518109309], [0.16666666759054638, -5.5511151538971635e-17, -0.33333333518109304], [0.11111111172703089, -7.4014868718628843e-17, -0.3888888910446085], [0.055555555863515349, -9.2518585898286075e-17, -0.44444444690812401], [5.5511151231257827e-17, -1.110223030779432e-16, -0.50000000277163936], [-0.055555555863515432, -1.0485439735139085e-16, -0.44444444690812401], [-0.11111111172703095, -9.8686491624838424e-17, -0.3888888910446085], [-0.16666666759054644, -9.2518585898286038e-17, -0.33333333518109298], [-0.13888888965878865, -8.9434633035009827e-17, -0.33333333518109298], [-0.11111111172703098, -8.6350680171733578e-17, -0.33333333518109254], [-0.083333333795273162, -8.3266727308457441e-17, -0.33333333518109298], [-0.083333333795273232, -7.8416305550641539e-17, -0.3114889775600036], [-0.08333333379527319, -7.3565883792825663e-17, -0.28964461993891433], [-0.084482843615394723, -2.2965357249462307e-17, -0.26975757754999719], [-0.12783260033492383, -3.4749319615518991e-17, -0.25605873221651609], [-0.20865859170634282, -5.6720618017084087e-17, -0.20798179566549022], [-0.25656267401682614, -6.9742603510094013e-17, -0.12698295005352878], [-0.26915158232531589, -4.8385545560843116e-17, -0.083333333795273259], [-0.29054549994390827, -5.0760747553552604e-17, -0.083333333795273246], [-0.31193941756250065, -5.3135949546262117e-17, -0.083333333795273259], [-0.33333333518109298, -5.5511151538971635e-17, -0.083333333795273246], [-0.33333333518109298, -6.1679057265524034e-17, -0.11111111172703104], [-0.33333333518109298, -6.7846962992076432e-17, -0.13888888965878879], [-0.33333333518109293, -7.4014868718628831e-17, -0.16666666759054649], [-0.38888889104460844, -6.7846962992076432e-17, -0.11111111172703095], [-0.44444444690812407, -6.1679057265524021e-17, -0.055555555863515543], [-0.50000000277163936, -5.5511151538971611e-17, 0.0], [-0.44444444690812401, -3.7007434359314434e-17, 0.055555555863515432], [-0.3888888910446085, -1.8503717179657208e-17, 0.11111111172703095], [-0.33333333518109304, -1.3673665492389592e-32, 0.16666666759054641], [-0.33333333518109309, -6.1679057265524108e-18, 0.13888888965878871], [-0.33333333518109309, -1.2335811453104803e-17, 0.11111111172703098], [-0.33333333518109287, -1.8503717179657208e-17, 0.083333333795273218], [-0.31214589923031194, -1.6151439257124411e-17, 0.083333333795273259], [-0.29095846327953073, -1.3799161334591608e-17, 0.08333333379527319], [-0.26977102732874969, -1.1446883412058811e-17, 0.083333333795273218], [-0.25649073116988785, -6.9723046957416867e-17, 0.12710454503335678], [-0.20830277638265518, -5.6623895112484438e-17, 0.20851651408788835], [-0.12683592338123439, -3.4478388366945207e-17, 0.25664958492823176], [-0.082871303667393703, -2.2527284984801012e-17, 0.27026168104284992]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        createdCurves.append(mc.curve( d = 3,p = [[2.7755575615628914e-17, -0.083333333795261227, 0.27118679483660113], [2.7755575615628914e-17, -0.083333333795260311, 0.29190230828476627], [2.7755575615628914e-17, -0.083333333795259382, 0.31261782173293151], [5.5511151231257827e-17, -0.083333333795258466, 0.33333333518109676], [5.5511151231257827e-17, -0.11111111172701621, 0.33333333518109809], [2.7755575615628914e-17, -0.13888888965877397, 0.33333333518109931], [2.7755575615628914e-17, -0.16666666759053173, 0.33333333518110042], [2.7755575615628914e-17, -0.11111111172701374, 0.38888889104461344], [5.5511151231257827e-17, -0.055555555863495774, 0.44444444690812657], [1.6653345369377348e-16, 2.2204460615588647e-14, 0.50000000277163958], [2.7755575615628914e-17, 0.055555555863535236, 0.44444444690812157], [1.1102230246251565e-16, 0.11111111172704828, 0.38888889104460361], [2.7755575615628914e-17, 0.16666666759056131, 0.33333333518108565], [2.7755575615628914e-17, 0.13888888965880353, 0.33333333518108699], [8.3266726846886741e-17, 0.11111111172704581, 0.33333333518108799], [8.3266726846886741e-17, 0.083333333795288053, 0.33333333518108932], [2.7755575615628914e-17, 0.083333333795287123, 0.31177689547826259], [8.3266726846886741e-17, 0.08333333379528618, 0.29022045577543598], [1.1102230246251565e-16, 0.080480877621554259, 0.27099051167032645], [1.1102230246251565e-16, 0.12535616460624269, 0.2575195204202318], [5.5511151231257827e-17, 0.20774123871712449, 0.20932747609620667], [-2.7755575615628914e-17, 0.25634367109173745, 0.12735279003591582], [1.3877787807814457e-17, 0.26931547357622793, 0.083333333795261297], [1.3877787807814457e-17, 0.29065476077785085, 0.083333333795260339], [6.9388939039072284e-18, 0.31199404797947383, 0.083333333795259396], [2.7755575615628914e-17, 0.33333333518109676, 0.083333333795258466], [1.3877787807814457e-17, 0.33333333518109809, 0.11111111172701624], [0.0, 0.33333333518109926, 0.138888889658774], [1.3877787807814457e-17, 0.33333333518110048, 0.16666666759053178], [2.0816681711721685e-17, 0.38888889104461349, 0.11111111172701371], [1.0408340855860843e-17, 0.44444444690812657, 0.055555555863495809], [-6.3108872417680944e-30, 0.50000000277163958, -2.2204460615588643e-14], [-6.9388939039072284e-18, 0.44444444690812157, -0.055555555863535208], [-2.7755575615628914e-17, 0.38888889104460361, -0.1111111117270483], [-4.163336342344337e-17, 0.33333333518108565, -0.16666666759056126], [-2.7755575615628914e-17, 0.33333333518108688, -0.13888888965880353], [-1.3877787807814457e-17, 0.3333333351810881, -0.11111111172704582], [-6.9388939039072284e-18, 0.33333333518108937, -0.083333333795288067], [-6.9388939039072284e-18, 0.31195288539590488, -0.083333333795287123], [-6.9388939039072284e-18, 0.29057243561072033, -0.08333333379528618], [-6.9388939039072284e-17, 0.27010896384564553, -0.083363006858924713], [-1.1102230246251565e-16, 0.25646968343124166, -0.12714010022924982], [-9.7144514654701197e-17, 0.20869029670742464, -0.20784243041263939], [-8.3266726846886741e-17, 0.12820380464392553, -0.25583765525634433], [-5.5511151231257827e-17, 0.083333333795261144, -0.27036130383202522], [-5.5511151231257827e-17, 0.083333333795260214, -0.29135198094838244], [-5.5511151231257827e-17, 0.083333333795259271, -0.31234265806473954], [-5.5511151231257827e-17, 0.083333333795258327, -0.33333333518109676], [-5.5511151231257827e-17, 0.11111111172701607, -0.33333333518109809], [-2.7755575615628914e-17, 0.1388888896587738, -0.33333333518109931], [-2.7755575615628914e-17, 0.16666666759053153, -0.33333333518110053], [-1.1102230246251565e-16, 0.11111111172701359, -0.38888889104461349], [-5.5511151231257827e-17, 0.05555555586349558, -0.44444444690812657], [-1.6653345369377348e-16, -2.2204460615588647e-14, -0.50000000277163958], [-2.7755575615628914e-17, -0.055555555863535236, -0.44444444690812157], [-1.1102230246251565e-16, -0.11111111172704828, -0.38888889104460361], [-2.7755575615628914e-17, -0.16666666759056131, -0.33333333518108565], [-2.7755575615628914e-17, -0.13888888965880353, -0.33333333518108699], [-8.3266726846886741e-17, -0.11111111172704581, -0.33333333518108771], [-8.3266726846886741e-17, -0.083333333795288053, -0.33333333518108932], [-5.5511151231257827e-17, -0.083333333795287109, -0.31148897755999999], [-5.5511151231257827e-17, -0.083333333795286138, -0.28964461993891055], [-8.3266726846886741e-17, -0.084482843615406769, -0.26975757754999358], [-5.5511151231257827e-17, -0.12783260033493526, -0.25605873221651038], [-8.3266726846886741e-17, -0.20865859170635209, -0.20798179566548092], [0.0, -0.25656267401683175, -0.12698295005351737], [-2.0816681711721685e-17, -0.2691515823253196, -0.083333333795261311], [-1.3877787807814457e-17, -0.2905454999439121, -0.083333333795260339], [-6.9388939039072284e-18, -0.31193941756250437, -0.083333333795259396], [-2.7755575615628914e-17, -0.33333333518109676, -0.083333333795258466], [-1.3877787807814457e-17, -0.33333333518109809, -0.11111111172701624], [0.0, -0.33333333518109926, -0.138888889658774], [-1.3877787807814457e-17, -0.33333333518110048, -0.16666666759053178], [-2.0816681711721685e-17, -0.38888889104461349, -0.11111111172701371], [-1.0408340855860843e-17, -0.44444444690812657, -0.055555555863495809], [6.3108872417680944e-30, -0.50000000277163958, 2.2204460615588643e-14], [6.9388939039072284e-18, -0.44444444690812157, 0.055555555863535173], [2.7755575615628914e-17, -0.38888889104460361, 0.1111111117270483], [4.163336342344337e-17, -0.33333333518108565, 0.16666666759056126], [2.7755575615628914e-17, -0.33333333518108688, 0.13888888965880353], [1.3877787807814457e-17, -0.3333333351810881, 0.11111111172704582], [6.9388939039072284e-18, -0.33333333518108937, 0.083333333795288067], [6.9388939039072284e-18, -0.31214589923030833, 0.083333333795287123], [2.0816681711721685e-17, -0.29095846327952712, 0.083333333795286207], [6.9388939039072284e-18, -0.26977102732874597, 0.083333333795285236], [9.7144514654701197e-17, -0.2564907311698823, 0.12710454503336824], [1.1102230246251565e-16, -0.20830277638264591, 0.20851651408789762], [1.3877787807814457e-16, -0.12683592338122296, 0.25664958492823742], [1.6653345369377348e-16, -0.082871303667381713, 0.2702616810428537]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        return combineCurves(createdCurves)          
    elif desiredShape == 'arrowsPointCenter':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[-2.3148145554748575e-06, 0.083337953612808088, -3.7009485970433115e-17], [0.01851601644110213, 0.10185577047037507, -4.5233048626858206e-17], [0.14814600189718494, 0.23148215509352818, -1.0279872734987458e-16], [0.16666433315284254, 0.24999997195109516, -1.1102229000629967e-16], [0.15740516752501466, 0.24999997195109516, -1.1102229000629967e-16], [0.092590174796971403, 0.24999997195109516, -1.1102229000629967e-16], [0.08333100916914353, 0.24999997195109516, -1.1102229000629967e-16], [0.08333100916914353, 0.27777746883458154, -1.2335797664889971e-16], [0.08333100916914353, 0.47222244701870392, -2.0970889336999928e-16], [0.08333100916914353, 0.49999994390219032, -2.2204458001259934e-16], [0.064812677913485925, 0.49999994390219032, -2.2204458001259934e-16], [-0.064817307542595015, 0.49999994390219032, -2.2204458001259934e-16], [-0.083335638798252606, 0.49999994390219032, -2.2204458001259934e-16], [-0.083335638798252606, 0.47222244701870392, -2.0970889336999928e-16], [-0.083335638798252606, 0.27777746883458154, -1.2335797664889971e-16], [-0.083335638798252606, 0.24999997195109516, -1.1102229000629967e-16], [-0.092594804426080479, 0.24999997195109516, -1.1102229000629967e-16], [-0.15740979715412373, 0.24999997195109516, -1.1102229000629967e-16], [-0.16666896278195162, 0.24999997195109516, -1.1102229000629967e-16], [-0.14815063152629401, 0.23148215509352818, -1.0279872734987458e-16], [-0.018520646070213077, 0.10185577047037507, -4.5233048626858206e-17], [-2.3148145554748575e-06, 0.083337953612808088, -3.7009485970433115e-17]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-2.3148145554748575e-06, -0.083333323983698068, 3.7007430002099747e-17], [-0.018520646070213077, -0.10185165523935566, 4.5231221097166445e-17], [-0.14815063152629401, -0.23148164069543756, 1.0279849891123296e-16], [-0.16666896278195162, -0.24999997195109516, 1.1102229000629967e-16], [-0.15740979715412373, -0.24999997195109516, 1.1102229000629967e-16], [-0.092594804426080479, -0.24999997195109516, 1.1102229000629967e-16], [-0.083335638798252606, -0.24999997195109516, 1.1102229000629967e-16], [-0.083335638798252606, -0.27777746883458154, 1.2335797664889971e-16], [-0.083335638798252606, -0.47222244701870297, 2.0970889336999886e-16], [-0.083335638798252606, -0.49999994390218938, 2.2204458001259892e-16], [-0.064817307542595015, -0.49999994390218938, 2.2204458001259892e-16], [0.064812677913485925, -0.49999994390218938, 2.2204458001259892e-16], [0.08333100916914353, -0.49999994390218938, 2.2204458001259892e-16], [0.08333100916914353, -0.47222244701870297, 2.0970889336999886e-16], [0.08333100916914353, -0.27777746883458154, 1.2335797664889971e-16], [0.08333100916914353, -0.24999997195109516, 1.1102229000629967e-16], [0.092590174796971403, -0.24999997195109516, 1.1102229000629967e-16], [0.15740516752501466, -0.24999997195109516, 1.1102229000629967e-16], [0.16666433315284254, -0.24999997195109516, 1.1102229000629967e-16], [0.14814600189718494, -0.23148164069543756, 1.0279849891123296e-16], [0.01851601644110213, -0.10185165523935566, 4.5231221097166445e-17], [-2.3148145554748575e-06, -0.083333323983698068, 3.7007430002099747e-17]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.08333100916914353, 0.0, 0.0], [0.10184934042480114, -0.018518331255657605, 8.2237910950667038e-18], [0.23147932588088208, -0.14814831671173853, 6.5791068909132791e-17], [0.24999765713653971, -0.16666664796739614, 7.4014860004199495e-17], [0.24999765713653971, -0.15740748233956736, 6.9902964456666155e-17], [0.24999765713653971, -0.092592489611526885, 4.1119325549633105e-17], [0.24999765713653971, -0.083333323983698068, 3.7007430002099747e-17], [0.27777515402002512, -0.083333323983698068, 3.7007430002099747e-17], [0.47222013220414938, -0.083333323983698068, 3.7007430002099747e-17], [0.49999762908763484, -0.083333323983698068, 3.7007430002099747e-17], [0.49999762908763484, -0.064814992728040477, 2.878363890703305e-17], [0.49999762908763484, 0.064814992728041393, -2.8783638907033457e-17], [0.49999762908763484, 0.083333323983699012, -3.7007430002100167e-17], [0.47222013220414938, 0.083333323983699012, -3.7007430002100167e-17], [0.27777515402002512, 0.083333323983699012, -3.7007430002100167e-17], [0.24999765713653971, 0.083333323983699012, -3.7007430002100167e-17], [0.24999765713653971, 0.092592489611527801, -4.1119325549633512e-17], [0.24999765713653971, 0.15740748233956828, -6.9902964456666562e-17], [0.24999765713653971, 0.16666664796739705, -7.4014860004199902e-17], [0.23147932588088208, 0.14814831671173948, -6.579106890913321e-17], [0.10184934042480114, 0.018518331255657605, -8.2237910950667038e-18], [0.08333100916914353, 0.0, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.41666430510393582, 0.0, 0.0], [0.41666430510393582, 0.23011571492276076, -1.0219190601413109e-16], [0.2301134001082053, 0.41666661991849224, -1.8503715001049958e-16], [-2.3148145554748575e-06, 0.41666661991849224, -1.8503715001049958e-16], [-0.2301180297373181, 0.41666661991849224, -1.8503715001049958e-16], [-0.41666893473304678, 0.23011571492276076, -1.0219190601413109e-16], [-0.41666893473304678, 0.0, 0.0], [-0.41666893473304678, -0.23012034455187266, 1.0219396198246529e-16], [-0.2301180297373181, -0.4166666199184913, 1.8503715001049916e-16], [-2.3148145554748575e-06, -0.4166666199184913, 1.8503715001049916e-16], [0.2301134001082053, -0.4166666199184913, 1.8503715001049916e-16], [0.41666430510393582, -0.23012034455187266, 1.0219396198246529e-16], [0.41666430510393582, 0.0, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.083335638798252606, 0.0, 0.0], [-0.10185397005391023, 0.018518331255657605, -8.2237910950667038e-18], [-0.23148395550999301, 0.14814831671173948, -6.579106890913321e-17], [-0.25000228676565062, 0.16666664796739705, -7.4014860004199902e-17], [-0.25000228676565062, 0.15740748233956828, -6.9902964456666562e-17], [-0.25000228676565062, 0.092592489611527801, -4.1119325549633512e-17], [-0.25000228676565062, 0.083333323983699012, -3.7007430002100167e-17], [-0.27777926925104551, 0.083333323983699012, -3.7007430002100167e-17], [-0.47222064660224, 0.083333323983699012, -3.7007430002100167e-17], [-0.49999762908763579, 0.083333323983699012, -3.7007430002100167e-17], [-0.49999762908763579, 0.06481550712613203, -2.8783867345675076e-17], [-0.49999762908763579, -0.06481087749702108, 2.8781811377341295e-17], [-0.49999762908763579, -0.083328694354588062, 3.7005374033766386e-17], [-0.47222064660224, -0.083328694354588062, 3.7005374033766386e-17], [-0.27777926925104551, -0.083328694354588062, 3.7005374033766386e-17], [-0.25000228676565062, -0.083328694354588062, 3.7005374033766386e-17], [-0.25000228676565062, -0.092587859982416865, 4.1117269581299738e-17], [-0.25000228676565062, -0.15740285271045826, 6.9900908488333194e-17], [-0.25000228676565062, -0.16666201833828706, 7.4012804035866546e-17], [-0.23148395550999301, -0.14814420148072008, 6.5789241379441456e-17], [-0.10185397005391023, -0.018517816857566979, 8.2235626564250891e-18], [-0.083335638798252606, 0.0, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0)))        
        return combineCurves(createdCurves)  
    elif desiredShape == 'arrowForm':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[-4.4408920985006263e-18, 0.28844037738812506, -0.99596786444551899], [-0.07534174426978224, 0.28844037738812506, -0.99596786444551899], [-0.22602523280934661, 0.22602523280934661, -0.9959678644455191], [-0.31964794967751425, 9.2625978856248505e-17, -0.9959678644455191], [-0.22602523280934669, -0.22602523280934653, -0.9959678644455191], [-9.6316165525050071e-17, -0.31964794967751436, -0.9959678644455191], [0.22602523280934647, -0.22602523280934667, -0.9959678644455191], [0.31964794967751425, -1.7168353732006538e-16, -0.9959678644455191], [0.2260252328093468, 0.22602523280934647, -0.9959678644455191], [0.07534174426978224, 0.28844037738812495, -0.99596786444551899], [8.8817841970012525e-18, 0.288440377388125, -0.99596786444551899]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-4.4408920985006263e-18, 0.28844037738812506, 0.14686025062824787], [-0.07534174426978224, 0.28844037738812506, 0.14686025062824787], [-0.22602523280934661, 0.22602523280934661, 0.14686025062824787], [-0.31964794967751425, 9.2625978856248505e-17, 0.14686025062824787], [-0.22602523280934669, -0.22602523280934653, 0.14686025062824787], [-9.6316165525050071e-17, -0.31964794967751436, 0.14686025062824787], [0.22602523280934647, -0.22602523280934667, 0.14686025062824787], [0.31964794967751425, -1.7168353732006538e-16, 0.14686025062824787], [0.2260252328093468, 0.22602523280934647, 0.14686025062824787], [0.07534174426978224, 0.28844037738812495, 0.14686025062824787], [8.8817841970012525e-18, 0.288440377388125, 0.14686025062824787]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 1,p = [[-2.3450657154921291e-32, 1.0561237082449674e-16, 1.005426646899243], [1.2765943166224771e-16, -0.57492696886442785, 0.1430361936026012], [6.3829715831123853e-17, -0.28746348443221392, 0.14303619360260114], [6.3829715831123865e-17, -0.28746348443221403, -0.99930266876553975], [-6.3829715831123804e-17, 0.28746348443221381, -0.99930266876553975], [-6.3829715831123853e-17, 0.28746348443221392, 0.14303619360260109], [-1.2765943166224771e-16, 0.57492696886442785, 0.14303619360260106], [-2.3450657154921291e-32, 1.0561237082449674e-16, 1.005426646899243]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0)))
        createdCurves.append(mc.curve( d = 1,p = [[-1.0561237082449674e-16, 0.0, 1.005426646899243], [0.57492696886442785, 0.0, 0.1430361936026012], [0.28746348443221392, 0.0, 0.14303619360260114], [0.28746348443221403, 0.0, -0.99930266876553975], [-0.28746348443221381, 0.0, -0.99930266876553975], [-0.28746348443221392, 0.0, 0.14303619360260109], [-0.57492696886442785, 0.0, 0.14303619360260106], [-1.0561237082449674e-16, 0.0, 1.005426646899243]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0)))
        createdCurves.append(mc.curve( d = 2,p = [[5.3290705182007512e-17, 0.57308973969032917, 0.1468602506282479], [-0.20828267723722718, 0.57308973969032928, 0.1468602506282479], [-0.52695399225346895, 0.3044492898549937, 0.14686025062824698], [-0.59969179956475738, -0.10541346681778833, 0.14686025062824898], [-0.39145350560996839, -0.46645162661288925, 0.14686025062824773], [1.0527887672849144e-15, -0.60879458333967595, 0.14686025062824809], [0.39145350560996384, -0.4664516266128868, 0.14686025062824781], [0.59969179956475926, -0.10541346681778915, 0.14686025062824798], [0.52695399225347006, 0.30444928985499375, 0.14686025062824812], [0.20828267723722729, 0.57308973969032917, 0.1468602506282479], [5.3290705182007512e-17, 0.57308973969032917, 0.1468602506282479]],k = (0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 9.0)))
        return combineCurves(createdCurves)
    elif desiredShape == 'arrowDirectionBall':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[-0.083650686096113439, -4.5996665399810501e-17, -0.27204391857153731], [-0.083650686096113439, -0.021284939866493414, -0.27204391857153731], [-0.065655126187728008, -0.065603470821661791, -0.27204391857153737], [-0.00040425958533962802, -0.092585131414330418, -0.27204391857153731], [0.06508220163717468, -0.065955342332247174, -0.27204391857153737], [0.092644858806235283, -0.0008084994342956234, -0.27204391857153731], [0.066223368743725156, 0.064809455979342734, -0.27204391857153737], [0.0012116353288455228, 0.092578085552959266, -0.27204391857153742], [-0.06450018815752577, 0.066739319042217388, -0.27204391857153737], [-0.083266472269906605, 0.022741603839562752, -0.27204391857153731], [-0.083637945691449861, 0.0014599057725069701, -0.27204391857153737]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.083333333795273301, 5.0963706130549176e-17, 0.27118679483659736], [-0.083333333795273287, 5.5563474129966158e-17, 0.29190230828476249], [-0.083333333795273287, 6.0163242129383183e-17, 0.31261782173292774], [-0.083333333795273301, 6.4763010128800221e-17, 0.33333333518109298], [-0.11111111172703104, 6.1679057265524021e-17, 0.33333333518109309], [-0.13888888965878876, 5.8595104402247847e-17, 0.33333333518109309], [-0.16666666759054655, 5.5511151538971598e-17, 0.33333333518109287], [-0.11111111172703098, 7.4014868718628831e-17, 0.38888889104460844], [-0.055555555863515543, 9.2518585898286038e-17, 0.44444444690812407], [-5.5511151231257827e-17, 1.110223030779432e-16, 0.50000000277163936], [0.055555555863515432, 1.0485439735139085e-16, 0.44444444690812401], [0.11111111172703095, 9.8686491624838424e-17, 0.3888888910446085], [0.16666666759054644, 9.2518585898286038e-17, 0.33333333518109298], [0.13888888965878865, 8.9434633035009827e-17, 0.33333333518109298], [0.11111111172703095, 8.6350680171733603e-17, 0.33333333518109282], [0.083333333795273162, 8.3266727308457441e-17, 0.33333333518109298], [0.083333333795273232, 7.8480236171053009e-17, 0.31177689547826631], [0.083333333795273218, 7.3693745033648614e-17, 0.29022045577543959], [0.080480877621542143, 2.1877484554653122e-17, 0.27099051167032995], [0.12535616460623117, 3.4076138780441208e-17, 0.25751952042023729], [0.20774123871711508, 5.6471249764076607e-17, 0.20932747609621585], [0.25634367109173173, 6.9683070944685038e-17, 0.1273527900359272], [0.26931547357622415, 4.8403741144872408e-17, 0.083333333795273246], [0.29065476077784713, 5.077287794290549e-17, 0.083333333795273232], [0.31199404797947006, 5.3142014740938559e-17, 0.083333333795273287], [0.33333333518109298, 5.5511151538971635e-17, 0.083333333795273246], [0.33333333518109298, 6.1679057265524034e-17, 0.11111111172703104], [0.33333333518109298, 6.7846962992076432e-17, 0.13888888965878879], [0.33333333518109293, 7.4014868718628831e-17, 0.16666666759054649], [0.38888889104460844, 6.7846962992076432e-17, 0.11111111172703095], [0.44444444690812407, 6.1679057265524021e-17, 0.055555555863515543], [0.50000000277163936, 5.5511151538971611e-17, 0.0], [0.44444444690812401, 3.7007434359314415e-17, -0.055555555863515432], [0.3888888910446085, 1.8503717179657208e-17, -0.11111111172703095], [0.33333333518109304, 1.367366549238959e-32, -0.16666666759054641], [0.33333333518109309, 6.1679057265524108e-18, -0.13888888965878871], [0.33333333518109309, 1.2335811453104803e-17, -0.11111111172703098], [0.33333333518109287, 1.8503717179657208e-17, -0.083333333795273218], [0.31195288539590849, 1.6130010416821824e-17, -0.083333333795273259], [0.29057243561072399, 1.3756303653986447e-17, -0.083333333795273232], [0.27010896384564931, 7.3424953345996006e-17, -0.08336300685891268], [0.25646968343124732, 6.97173254544881e-17, -0.12714010022923841], [0.20869029670743383, 5.6729236532341085e-17, -0.20784243041263009], [0.12820380464393691, 3.4850225778287795e-17, -0.2558376552563385], [0.083333333795273121, -5.0780410306568946e-17, -0.27036130383202139], [0.083333333795273218, -5.5441276913979373e-17, -0.29135198094837866], [0.083333333795273204, -6.01021435213898e-17, -0.31234265806473582], [0.083333333795273246, -6.4763010128800245e-17, -0.33333333518109298], [0.11111111172703092, -6.1679057265524034e-17, -0.33333333518109309], [0.13888888965878865, -5.8595104402247859e-17, -0.33333333518109309], [0.16666666759054638, -5.5511151538971635e-17, -0.33333333518109304], [0.11111111172703089, -7.4014868718628843e-17, -0.3888888910446085], [0.055555555863515349, -9.2518585898286075e-17, -0.44444444690812401], [5.5511151231257827e-17, -1.110223030779432e-16, -0.50000000277163936], [-0.055555555863515432, -1.0485439735139085e-16, -0.44444444690812401], [-0.11111111172703095, -9.8686491624838424e-17, -0.3888888910446085], [-0.16666666759054644, -9.2518585898286038e-17, -0.33333333518109298], [-0.13888888965878865, -8.9434633035009827e-17, -0.33333333518109298], [-0.11111111172703098, -8.6350680171733578e-17, -0.33333333518109254], [-0.083333333795273162, -8.3266727308457441e-17, -0.33333333518109298], [-0.083333333795273232, -7.8416305550641539e-17, -0.3114889775600036], [-0.08333333379527319, -7.3565883792825663e-17, -0.28964461993891433], [-0.084482843615394723, -2.2965357249462307e-17, -0.26975757754999719], [-0.12783260033492383, -3.4749319615518991e-17, -0.25605873221651609], [-0.20865859170634282, -5.6720618017084087e-17, -0.20798179566549022], [-0.25656267401682614, -6.9742603510094013e-17, -0.12698295005352878], [-0.26915158232531589, -4.8385545560843116e-17, -0.083333333795273259], [-0.29054549994390827, -5.0760747553552604e-17, -0.083333333795273246], [-0.31193941756250065, -5.3135949546262117e-17, -0.083333333795273259], [-0.33333333518109298, -5.5511151538971635e-17, -0.083333333795273246], [-0.33333333518109298, -6.1679057265524034e-17, -0.11111111172703104], [-0.33333333518109298, -6.7846962992076432e-17, -0.13888888965878879], [-0.33333333518109293, -7.4014868718628831e-17, -0.16666666759054649], [-0.38888889104460844, -6.7846962992076432e-17, -0.11111111172703095], [-0.44444444690812407, -6.1679057265524021e-17, -0.055555555863515543], [-0.50000000277163936, -5.5511151538971611e-17, 0.0], [-0.44444444690812401, -3.7007434359314434e-17, 0.055555555863515432], [-0.3888888910446085, -1.8503717179657208e-17, 0.11111111172703095], [-0.33333333518109304, -1.3673665492389592e-32, 0.16666666759054641], [-0.33333333518109309, -6.1679057265524108e-18, 0.13888888965878871], [-0.33333333518109309, -1.2335811453104803e-17, 0.11111111172703098], [-0.33333333518109287, -1.8503717179657208e-17, 0.083333333795273218], [-0.31214589923031194, -1.6151439257124411e-17, 0.083333333795273259], [-0.29095846327953073, -1.3799161334591608e-17, 0.08333333379527319], [-0.26977102732874969, -1.1446883412058811e-17, 0.083333333795273218], [-0.25649073116988785, -6.9723046957416867e-17, 0.12710454503335678], [-0.20830277638265518, -5.6623895112484438e-17, 0.20851651408788835], [-0.12683592338123439, -3.4478388366945207e-17, 0.25664958492823176], [-0.082871303667393703, -2.2527284984801012e-17, 0.27026168104284992]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.059149967389469024, -0.27148816765093503, -0.059149967389469031], [-0.074200692706214377, -0.27148816765093503, -0.044099242072723678], [-0.092813844034371762, -0.27148816765093503, -3.6525859630105739e-05], [-0.065753428954273913, -0.27148816765093503, 0.065181719565967369], [-0.00061740370641559517, -0.27148816765093503, 0.092657535930808541], [0.064938112471383369, -0.27148816765093503, 0.066081503336535105], [0.09265419891970969, -0.27148816765093503, 0.00099978730370103158], [0.066319347641117771, -0.27148816765093503, -0.064605836526413982], [0.0015833046325297237, -0.27148816765093503, -0.092800345500519105], [-0.042797544897519697, -0.27148816765093503, -0.074959029477545444], [-0.05810864929130323, -0.27148816765093503, -0.060173267834569416]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.083650686096113425, 8.772165604222159e-17, 0.33016986404740656], [-0.083650686096113425, -0.021284939866493283, 0.33016986404740656], [-0.06565512618772798, -0.065603470821661652, 0.33016986404740656], [-0.00040425958533960027, -0.092585131414330279, 0.33016986404740656], [0.065082201637174736, -0.065955342332247036, 0.33016986404740656], [0.092644858806235339, -0.00080849943429548961, 0.33016986404740656], [0.066223368743725197, 0.064809455979342873, 0.33016986404740656], [0.0012116353288455506, 0.092578085552959405, 0.33016986404740656], [-0.064500188157525756, 0.066739319042217526, 0.33016986404740656], [-0.083266472269906605, 0.022741603839562884, 0.33016986404740661], [-0.083637945691449764, 0.0014599057725071035, 0.33016986404740661]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.33359927267136236, -1.7530771588374869e-16, 0.083650686096113494], [0.33359927267136236, -0.021284939866493543, 0.083650686096113494], [0.33359927267136236, -0.06560347082166193, 0.065655126187728147], [0.3335992726713623, -0.092585131414330585, 0.00040425958533973905], [0.3335992726713623, -0.065955342332247355, -0.065082201637174569], [0.33359927267136236, -0.00080849943429582105, -0.092644858806235214], [0.33359927267136236, 0.064809455979342526, -0.066223368743725142], [0.33359927267136247, 0.0925780855529591, -0.0012116353288454951], [0.33359927267136241, 0.066739319042217235, 0.064500188157525784], [0.33359927267136236, 0.022741603839562613, 0.083266472269906661], [0.33359927267136236, 0.0014599057725068407, 0.083637945691449903]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.083650686096113397, 7.4724464944928493e-17, 0.27163571906477435], [-0.083650686096113397, -0.021284939866493297, 0.27163571906477435], [-0.065655126187727966, -0.065603470821661666, 0.27163571906477435], [-0.00040425958533954476, -0.092585131414330307, 0.27163571906477435], [0.065082201637174736, -0.065955342332247049, 0.27163571906477429], [0.092644858806235367, -0.00080849943429550262, 0.27163571906477435], [0.066223368743725253, 0.064809455979342845, 0.27163571906477429], [0.0012116353288456061, 0.092578085552959391, 0.27163571906477429], [-0.064500188157525742, 0.066739319042217513, 0.27163571906477435], [-0.083266472269906577, 0.022741603839562873, 0.27163571906477435], [-0.08363794569144975, 0.0014599057725070907, 0.27163571906477441]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.27118679483659736, -0.083333333795273246, 3.4139358007223564e-15], [0.29190230828476249, -0.083333333795273246, 3.4416913763379853e-15], [0.31261782173292774, -0.083333333795273246, 3.4139358007223564e-15], [0.33333333518109298, -0.083333333795273246, 3.4139358007223564e-15], [0.33333333518109309, -0.11111111172703098, 4.5796699765787707e-15], [0.33333333518109309, -0.13888888965878873, 5.7176485768195562e-15], [0.33333333518109298, -0.16666666759054649, 6.8278716014447127e-15], [0.38888889104460844, -0.111111111727031, 4.5519144009631418e-15], [0.44444444690812401, -0.055555555863515502, 2.2759572004815709e-15], [0.50000000277163936, -7.640365658541241e-33, 0.0], [0.44444444690812401, 0.055555555863515488, -2.2759572004815709e-15], [0.3888888910446085, 0.111111111727031, -4.5519144009631418e-15], [0.33333333518109298, 0.16666666759054649, -6.8278716014447127e-15], [0.33333333518109298, 0.13888888965878873, -5.6621374255882984e-15], [0.33333333518109282, 0.111111111727031, -4.5519144009631418e-15], [0.33333333518109298, 0.083333333795273246, -3.3861802251067274e-15], [0.31177689547826626, 0.083333333795273259, -3.4139358007223564e-15], [0.29022045577543959, 0.083333333795273259, -3.4416913763379853e-15], [0.27099051167032995, 0.080480877621542213, -3.3306690738754696e-15], [0.25751952042023729, 0.12535616460623125, -5.1902926401226068e-15], [0.20932747609621588, 0.20774123871711514, -8.5348395018058909e-15], [0.12735279003592717, 0.25634367109173173, -1.0519363158323358e-14], [0.083333333795273246, 0.26931547357622415, -1.1067535776732029e-14], [0.083333333795273232, 0.29065476077784713, -1.1948775302528247e-14], [0.083333333795273246, 0.31199404797947006, -1.2809198146612744e-14], [0.083333333795273246, 0.33333333518109298, -1.3690437672408962e-14], [0.111111111727031, 0.33333333518109304, -1.3697376566312869e-14], [0.13888888965878879, 0.33333333518109304, -1.3683498778505054e-14], [0.16666666759054652, 0.33333333518109298, -1.3683498778505054e-14], [0.11111111172703099, 0.3888888910446085, -1.597333376679444e-14], [0.055555555863515529, 0.44444444690812401, -1.8256229861179918e-14], [-4.7331654313260708e-30, 0.50000000277163936, -2.0539126069419494e-14], [-0.05555555586351546, 0.44444444690812401, -1.8256229861179918e-14], [-0.111111111727031, 0.3888888910446085, -1.597333376679444e-14], [-0.16666666759054644, 0.33333333518109304, -1.3697376566312869e-14], [-0.13888888965878871, 0.33333333518109298, -1.3697376566312869e-14], [-0.111111111727031, 0.33333333518109298, -1.3683498778505054e-14], [-0.083333333795273246, 0.33333333518109298, -1.3690437672408962e-14], [-0.083333333795273273, 0.31195288539590849, -1.2823075934420558e-14], [-0.083333333795273273, 0.29057243561072399, -1.1934897514720433e-14], [-0.083363006858912694, 0.2701089638456492, -1.1032841307212493e-14], [-0.12714010022923841, 0.25646968343124732, -1.04638520070921e-14], [-0.20784243041263012, 0.2086902967074338, -8.507083926190262e-15], [-0.2558376552563385, 0.12820380464393688, -5.2180482157382357e-15], [-0.27036130383202139, 0.083333333795273135, -3.4139358007223564e-15], [-0.29135198094837866, 0.083333333795273135, -3.4139358007223564e-15], [-0.31234265806473582, 0.083333333795273135, -3.4139358007223564e-15], [-0.33333333518109298, 0.083333333795273107, -3.4139358007223564e-15], [-0.33333333518109309, 0.11111111172703085, -4.5796699765787707e-15], [-0.33333333518109309, 0.13888888965878857, -5.7176485768195562e-15], [-0.33333333518109309, 0.16666666759054632, -6.8556271770603416e-15], [-0.3888888910446085, 0.11111111172703085, -4.5519144009631418e-15], [-0.44444444690812401, 0.055555555863515294, -2.2759572004815709e-15], [-0.50000000277163936, 7.640365658541241e-33, 0.0], [-0.44444444690812401, -0.055555555863515488, 2.2759572004815709e-15], [-0.3888888910446085, -0.111111111727031, 4.5519144009631418e-15], [-0.33333333518109298, -0.16666666759054649, 6.8278716014447127e-15], [-0.33333333518109298, -0.13888888965878873, 5.6621374255882984e-15], [-0.33333333518109254, -0.111111111727031, 4.5519144009631418e-15], [-0.33333333518109298, -0.083333333795273246, 3.3861802251067274e-15], [-0.3114889775600036, -0.083333333795273259, 3.4139358007223564e-15], [-0.28964461993891433, -0.083333333795273259, 3.4139358007223564e-15], [-0.26975757754999724, -0.084482843615394779, 3.4972025275692431e-15], [-0.25605873221651609, -0.12783260033492388, 5.2735593669694936e-15], [-0.20798179566549019, -0.20865859170634285, 8.5764728652293343e-15], [-0.12698295005352872, -0.25656267401682609, 1.0533240946131173e-14], [-0.083333333795273246, -0.26915158232531594, 1.1053657988924215e-14], [-0.083333333795273232, -0.29054549994390833, 1.1934897514720433e-14], [-0.083333333795273246, -0.31193941756250065, 1.2809198146612744e-14], [-0.083333333795273246, -0.33333333518109298, 1.3690437672408962e-14], [-0.111111111727031, -0.33333333518109304, 1.3697376566312869e-14], [-0.13888888965878879, -0.33333333518109304, 1.3683498778505054e-14], [-0.16666666759054652, -0.33333333518109298, 1.3683498778505054e-14], [-0.11111111172703099, -0.3888888910446085, 1.597333376679444e-14], [-0.055555555863515529, -0.44444444690812401, 1.8256229861179918e-14], [4.7331654313260708e-30, -0.50000000277163936, 2.0539126069419494e-14], [0.055555555863515432, -0.44444444690812401, 1.8259699308131871e-14], [0.111111111727031, -0.3888888910446085, 1.597333376679444e-14], [0.16666666759054644, -0.33333333518109304, 1.3697376566312869e-14], [0.13888888965878871, -0.33333333518109298, 1.3697376566312869e-14], [0.111111111727031, -0.33333333518109298, 1.3683498778505054e-14], [0.083333333795273246, -0.33333333518109298, 1.3690437672408962e-14], [0.083333333795273273, -0.31214589923031194, 1.2830014828324465e-14], [0.083333333795273273, -0.29095846327953073, 1.1955714196432154e-14], [0.083333333795273246, -0.26977102732874964, 1.1074474670635936e-14], [0.12710454503335678, -0.25649073116988785, 1.0449974219284286e-14], [0.20851651408788835, -0.20830277638265515, 8.4932061383824475e-15], [0.25664958492823176, -0.12683592338123434, 5.134781488891349e-15], [0.27026168104284992, -0.082871303667393689, 3.3029134982598407e-15]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.059149967389469024, -0.334160033078932, -0.059149967389469031], [-0.074200692706214377, -0.334160033078932, -0.044099242072723678], [-0.092813844034371762, -0.334160033078932, -3.6525859630105739e-05], [-0.065753428954273913, -0.334160033078932, 0.065181719565967369], [-0.00061740370641559517, -0.334160033078932, 0.092657535930808541], [0.064938112471383369, -0.334160033078932, 0.066081503336535105], [0.09265419891970969, -0.334160033078932, 0.00099978730370103158], [0.066319347641117771, -0.334160033078932, -0.064605836526413982], [0.0015833046325297237, -0.334160033078932, -0.092800345500519105], [-0.042797544897519697, -0.334160033078932, -0.074959029477545444], [-0.05810864929130323, -0.334160033078932, -0.060173267834569416]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.16293684038255871, 1.0258540649938723e-16, 0.33560274678785229], [-0.16293684038255871, -0.041459323424967255, 0.33560274678785229], [-0.12788465122276654, -0.12778403564471863, 0.33560274678785229], [-0.00078742665008069146, -0.18033957021849042, 0.33560274678785229], [0.12676869485227693, -0.12846941952895297, 0.33560274678785229], [0.18045590868474154, -0.0015748148571529698, 0.33560274678785229], [0.12899148789041426, 0.12623743422801725, 0.33560274678785224], [0.0023600527549903771, 0.18032584611838873, 0.33560274678785229], [-0.12563503484469413, 0.12999646842738424, 0.33560274678785229], [-0.16218845934953879, 0.044296648931160344, 0.33560274678785229], [-0.16291202431256613, 0.0028436399619633495, 0.33560274678785229]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.16293684038255871, -4.5799655012623081e-17, -0.33266416094498535], [-0.16293684038255871, -0.041459323424967401, -0.33266416094498535], [-0.12788465122276654, -0.12778403564471877, -0.33266416094498535], [-0.0007874266500806637, -0.18033957021849054, -0.3326641609449853], [0.12676869485227693, -0.1284694195289531, -0.33266416094498535], [0.18045590868474154, -0.0015748148571531179, -0.33266416094498535], [0.1289914878904142, 0.12623743422801709, -0.33266416094498535], [0.0023600527549903771, 0.18032584611838856, -0.3326641609449853], [-0.12563503484469407, 0.12999646842738408, -0.3326641609449853], [-0.16218845934953879, 0.044296648931160199, -0.33266416094498535], [-0.16291202431256613, 0.0028436399619632007, -0.3326641609449853]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[2.7755575615628914e-17, -0.083333333795261227, 0.27118679483660113], [2.7755575615628914e-17, -0.083333333795260311, 0.29190230828476627], [2.7755575615628914e-17, -0.083333333795259382, 0.31261782173293151], [5.5511151231257827e-17, -0.083333333795258466, 0.33333333518109676], [5.5511151231257827e-17, -0.11111111172701621, 0.33333333518109809], [2.7755575615628914e-17, -0.13888888965877397, 0.33333333518109931], [2.7755575615628914e-17, -0.16666666759053173, 0.33333333518110042], [2.7755575615628914e-17, -0.11111111172701374, 0.38888889104461344], [5.5511151231257827e-17, -0.055555555863495774, 0.44444444690812657], [1.6653345369377348e-16, 2.2204460615588647e-14, 0.50000000277163958], [2.7755575615628914e-17, 0.055555555863535236, 0.44444444690812157], [1.1102230246251565e-16, 0.11111111172704828, 0.38888889104460361], [2.7755575615628914e-17, 0.16666666759056131, 0.33333333518108565], [2.7755575615628914e-17, 0.13888888965880353, 0.33333333518108699], [8.3266726846886741e-17, 0.11111111172704581, 0.33333333518108799], [8.3266726846886741e-17, 0.083333333795288053, 0.33333333518108932], [2.7755575615628914e-17, 0.083333333795287123, 0.31177689547826259], [8.3266726846886741e-17, 0.08333333379528618, 0.29022045577543598], [1.1102230246251565e-16, 0.080480877621554259, 0.27099051167032645], [1.1102230246251565e-16, 0.12535616460624269, 0.2575195204202318], [5.5511151231257827e-17, 0.20774123871712449, 0.20932747609620667], [-2.7755575615628914e-17, 0.25634367109173745, 0.12735279003591582], [1.3877787807814457e-17, 0.26931547357622793, 0.083333333795261297], [1.3877787807814457e-17, 0.29065476077785085, 0.083333333795260339], [6.9388939039072284e-18, 0.31199404797947383, 0.083333333795259396], [2.7755575615628914e-17, 0.33333333518109676, 0.083333333795258466], [1.3877787807814457e-17, 0.33333333518109809, 0.11111111172701624], [0.0, 0.33333333518109926, 0.138888889658774], [1.3877787807814457e-17, 0.33333333518110048, 0.16666666759053178], [2.0816681711721685e-17, 0.38888889104461349, 0.11111111172701371], [1.0408340855860843e-17, 0.44444444690812657, 0.055555555863495809], [-6.3108872417680944e-30, 0.50000000277163958, -2.2204460615588643e-14], [-6.9388939039072284e-18, 0.44444444690812157, -0.055555555863535208], [-2.7755575615628914e-17, 0.38888889104460361, -0.1111111117270483], [-4.163336342344337e-17, 0.33333333518108565, -0.16666666759056126], [-2.7755575615628914e-17, 0.33333333518108688, -0.13888888965880353], [-1.3877787807814457e-17, 0.3333333351810881, -0.11111111172704582], [-6.9388939039072284e-18, 0.33333333518108937, -0.083333333795288067], [-6.9388939039072284e-18, 0.31195288539590488, -0.083333333795287123], [-6.9388939039072284e-18, 0.29057243561072033, -0.08333333379528618], [-6.9388939039072284e-17, 0.27010896384564553, -0.083363006858924713], [-1.1102230246251565e-16, 0.25646968343124166, -0.12714010022924982], [-9.7144514654701197e-17, 0.20869029670742464, -0.20784243041263939], [-8.3266726846886741e-17, 0.12820380464392553, -0.25583765525634433], [-5.5511151231257827e-17, 0.083333333795261144, -0.27036130383202522], [-5.5511151231257827e-17, 0.083333333795260214, -0.29135198094838244], [-5.5511151231257827e-17, 0.083333333795259271, -0.31234265806473954], [-5.5511151231257827e-17, 0.083333333795258327, -0.33333333518109676], [-5.5511151231257827e-17, 0.11111111172701607, -0.33333333518109809], [-2.7755575615628914e-17, 0.1388888896587738, -0.33333333518109931], [-2.7755575615628914e-17, 0.16666666759053153, -0.33333333518110053], [-1.1102230246251565e-16, 0.11111111172701359, -0.38888889104461349], [-5.5511151231257827e-17, 0.05555555586349558, -0.44444444690812657], [-1.6653345369377348e-16, -2.2204460615588647e-14, -0.50000000277163958], [-2.7755575615628914e-17, -0.055555555863535236, -0.44444444690812157], [-1.1102230246251565e-16, -0.11111111172704828, -0.38888889104460361], [-2.7755575615628914e-17, -0.16666666759056131, -0.33333333518108565], [-2.7755575615628914e-17, -0.13888888965880353, -0.33333333518108699], [-8.3266726846886741e-17, -0.11111111172704581, -0.33333333518108771], [-8.3266726846886741e-17, -0.083333333795288053, -0.33333333518108932], [-5.5511151231257827e-17, -0.083333333795287109, -0.31148897755999999], [-5.5511151231257827e-17, -0.083333333795286138, -0.28964461993891055], [-8.3266726846886741e-17, -0.084482843615406769, -0.26975757754999358], [-5.5511151231257827e-17, -0.12783260033493526, -0.25605873221651038], [-8.3266726846886741e-17, -0.20865859170635209, -0.20798179566548092], [0.0, -0.25656267401683175, -0.12698295005351737], [-2.0816681711721685e-17, -0.2691515823253196, -0.083333333795261311], [-1.3877787807814457e-17, -0.2905454999439121, -0.083333333795260339], [-6.9388939039072284e-18, -0.31193941756250437, -0.083333333795259396], [-2.7755575615628914e-17, -0.33333333518109676, -0.083333333795258466], [-1.3877787807814457e-17, -0.33333333518109809, -0.11111111172701624], [0.0, -0.33333333518109926, -0.138888889658774], [-1.3877787807814457e-17, -0.33333333518110048, -0.16666666759053178], [-2.0816681711721685e-17, -0.38888889104461349, -0.11111111172701371], [-1.0408340855860843e-17, -0.44444444690812657, -0.055555555863495809], [6.3108872417680944e-30, -0.50000000277163958, 2.2204460615588643e-14], [6.9388939039072284e-18, -0.44444444690812157, 0.055555555863535173], [2.7755575615628914e-17, -0.38888889104460361, 0.1111111117270483], [4.163336342344337e-17, -0.33333333518108565, 0.16666666759056126], [2.7755575615628914e-17, -0.33333333518108688, 0.13888888965880353], [1.3877787807814457e-17, -0.3333333351810881, 0.11111111172704582], [6.9388939039072284e-18, -0.33333333518108937, 0.083333333795288067], [6.9388939039072284e-18, -0.31214589923030833, 0.083333333795287123], [2.0816681711721685e-17, -0.29095846327952712, 0.083333333795286207], [6.9388939039072284e-18, -0.26977102732874597, 0.083333333795285236], [9.7144514654701197e-17, -0.2564907311698823, 0.12710454503336824], [1.1102230246251565e-16, -0.20830277638264591, 0.20851651408789762], [1.3877787807814457e-16, -0.12683592338122296, 0.25664958492823742], [1.6653345369377348e-16, -0.082871303667381713, 0.2702616810428537]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.33714289204482173, 3.1596258909258473e-16, 0.16293684038255848], [-0.33714289204482178, -0.041459323424967033, 0.16293684038255854], [-0.33714289204482184, -0.12778403564471841, 0.12788465122276638], [-0.33714289204482184, -0.1803395702184902, 0.00078742665008060819], [-0.33714289204482184, -0.12846941952895283, -0.12676869485227704], [-0.33714289204482178, -0.0015748148571528894, -0.18045590868474171], [-0.33714289204482173, 0.12623743422801731, -0.12899148789041448], [-0.33714289204482162, 0.18032584611838884, -0.0023600527549906269], [-0.33714289204482167, 0.12999646842738441, 0.12563503484469385], [-0.33714289204482173, 0.044296648931160552, 0.16218845934953857], [-0.33714289204482173, 0.002843639961963562, 0.16291202431256596]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.27446730826136989, 2.2974599531022055e-16, 0.083650686096113439], [-0.27446730826136989, -0.02128493986649314, 0.083650686096113439], [-0.27446730826136989, -0.065603470821661514, 0.065655126187728063], [-0.27446730826136989, -0.092585131414330168, 0.00040425958533965578], [-0.27446730826136989, -0.065955342332246938, -0.065082201637174611], [-0.27446730826136984, -0.00080849943429541599, -0.092644858806235297], [-0.27446730826136978, 0.064809455979342942, -0.066223368743725211], [-0.27446730826136978, 0.092578085552959502, -0.0012116353288456061], [-0.27446730826136978, 0.066739319042217651, 0.064500188157525715], [-0.27446730826136978, 0.022741603839563022, 0.083266472269906605], [-0.27446730826136984, 0.0014599057725072455, 0.083637945691449819]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.083650686096113466, -5.9189718417369189e-17, -0.33146014722529393], [-0.083650686096113466, -0.021284939866493428, -0.33146014722529393], [-0.065655126187728063, -0.065603470821661819, -0.33146014722529393], [-0.00040425958533962802, -0.092585131414330446, -0.33146014722529393], [0.065082201637174653, -0.065955342332247188, -0.33146014722529393], [0.092644858806235242, -0.00080849943429563652, -0.33146014722529393], [0.066223368743725169, 0.064809455979342706, -0.33146014722529393], [0.0012116353288455228, 0.092578085552959252, -0.33146014722529393], [-0.064500188157525784, 0.066739319042217374, -0.33146014722529393], [-0.083266472269906661, 0.022741603839562741, -0.33146014722529393], [-0.083637945691449861, 0.0014599057725069567, -0.33146014722529393]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.33380370731970899, -1.3097762865248641e-16, 0.16293684038255862], [0.33380370731970899, -0.041459323424967477, 0.16293684038255862], [0.33380370731970888, -0.12778403564471885, 0.12788465122276649], [0.33380370731970888, -0.18033957021849065, 0.00078742665008069146], [0.33380370731970888, -0.12846941952895327, -0.12676869485227699], [0.33380370731970893, -0.0015748148571533363, -0.18045590868474159], [0.33380370731970904, 0.12623743422801686, -0.12899148789041437], [0.33380370731970915, 0.18032584611838837, -0.0023600527549905159], [0.3338037073197091, 0.12999646842738397, 0.12563503484469393], [0.33380370731970904, 0.044296648931160101, 0.16218845934953868], [0.33380370731970899, 0.0028436399619631149, 0.16291202431256602]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.11521374473961722, -0.33329228682404172, -0.11521374473961722], [-0.14452991347681793, -0.33329228682404172, -0.085897576002416515], [-0.18078506222105867, -0.33329228682404172, -7.1145957530452386e-05], [-0.128076127741721, -0.33329228682404172, 0.12696253829380325], [-0.0012025939518087309, -0.33329228682404172, 0.18048060149623552], [0.12648803447155504, -0.33329228682404172, 0.12871515900076749], [0.1804741015848762, -0.33329228682404172, 0.0019474100204327355], [0.12917843792052622, -0.33329228682404172, -0.12584081930650265], [0.0030839992620149692, -0.33329228682404172, -0.18075876944859748], [-0.083362098593194212, -0.33329228682404172, -0.14600702027932069], [-0.1131854400278858, -0.33329228682404172, -0.11720695422860034]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.33694065493451736, 2.7136160405137124e-16, 0.083650686096113369], [-0.33694065493451736, -0.021284939866493095, 0.083650686096113369], [-0.33694065493451741, -0.065603470821661472, 0.065655126187727952], [-0.33694065493451741, -0.092585131414330127, 0.00040425958533957251], [-0.33694065493451741, -0.065955342332246897, -0.065082201637174791], [-0.3369406549345173, -0.00080849943429537436, -0.092644858806235394], [-0.3369406549345173, 0.06480945597934297, -0.066223368743725308], [-0.33694065493451725, 0.092578085552959544, -0.0012116353288457171], [-0.33694065493451719, 0.066739319042217693, 0.064500188157525618], [-0.3369406549345173, 0.022741603839563064, 0.083266472269906466], [-0.33694065493451736, 0.0014599057725072871, 0.083637945691449667]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.059149967389469024, 0.33103860981264055, -0.059149967389469031], [-0.074200692706214377, 0.33103860981264055, -0.044099242072723678], [-0.092813844034371762, 0.33103860981264055, -3.6525859630105739e-05], [-0.065753428954273913, 0.33103860981264055, 0.065181719565967369], [-0.00061740370641559517, 0.33103860981264055, 0.092657535930808541], [0.064938112471383369, 0.33103860981264055, 0.066081503336535105], [0.09265419891970969, 0.33103860981264055, 0.00099978730370103158], [0.066319347641117771, 0.33103860981264055, -0.064605836526413982], [0.0015833046325297237, 0.33103860981264055, -0.092800345500519105], [-0.042797544897519697, 0.33103860981264055, -0.074959029477545444], [-0.05810864929130323, 0.33103860981264055, -0.060173267834569416]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.27112592599821494, -1.3369210714259799e-16, 0.083650686096113425], [0.27112592599821494, -0.021284939866493501, 0.083650686096113425], [0.27112592599821494, -0.065603470821661874, 0.065655126187728036], [0.27112592599821494, -0.092585131414330515, 0.00040425958533965578], [0.27112592599821489, -0.065955342332247299, -0.065082201637174653], [0.27112592599821494, -0.00080849943429577942, -0.092644858806235283], [0.271125925998215, 0.064809455979342567, -0.066223368743725253], [0.27112592599821506, 0.092578085552959127, -0.0012116353288456339], [0.271125925998215, 0.066739319042217291, 0.064500188157525729], [0.271125925998215, 0.022741603839562655, 0.083266472269906591], [0.27112592599821494, 0.0014599057725068823, 0.083637945691449792]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.059149967389469024, 0.26836674438464359, -0.059149967389469031], [-0.074200692706214377, 0.26836674438464359, -0.044099242072723678], [-0.092813844034371762, 0.26836674438464359, -3.6525859630105739e-05], [-0.065753428954273913, 0.26836674438464359, 0.065181719565967369], [-0.00061740370641559517, 0.26836674438464359, 0.092657535930808541], [0.064938112471383369, 0.26836674438464359, 0.066081503336535105], [0.09265419891970969, 0.26836674438464359, 0.00099978730370103158], [0.066319347641117771, 0.26836674438464359, -0.064605836526413982], [0.0015833046325297237, 0.26836674438464359, -0.092800345500519105], [-0.042797544897519697, 0.26836674438464359, -0.074959029477545444], [-0.05810864929130323, 0.26836674438464359, -0.060173267834569416]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.11521374473961722, 0.33103860981264055, -0.11521374473961722], [-0.14452991347681793, 0.33103860981264055, -0.085897576002416515], [-0.18078506222105867, 0.33103860981264055, -7.1145957530452386e-05], [-0.128076127741721, 0.33103860981264055, 0.12696253829380325], [-0.0012025939518087309, 0.33103860981264055, 0.18048060149623552], [0.12648803447155504, 0.33103860981264055, 0.12871515900076749], [0.1804741015848762, 0.33103860981264055, 0.0019474100204327355], [0.12917843792052622, 0.33103860981264055, -0.12584081930650265], [0.0030839992620149692, 0.33103860981264055, -0.18075876944859748], [-0.083362098593194212, 0.33103860981264055, -0.14600702027932069], [-0.1131854400278858, 0.33103860981264055, -0.11720695422860034]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        return combineCurves(createdCurves)
    #>>> Rotate Arrows #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'arrowRotate90':
        createBuffer = mc.curve( d = 1,p = [[-5.4875726275800358e-17, 0.24713830040737983, 1.0000002495975611], [-1.6652868629766813e-16, 0.74997852955667643, 0.96445021552274857], [-1.0635392058121785e-16, 0.47897547709896404, 0.9159882893642729], [-1.2475672692841999e-16, 0.56185434890679498, 0.87265331761047249], [-1.591023367408395e-16, 0.71653322445981993, 0.76277622680336898], [-1.9876338018407671e-16, 0.89515068493190808, 0.54208584441365393], [-2.2381326558212954e-16, 1.0079653394762524, 0.28140561144277382], [-2.3237190720655022e-16, 1.046510034706791, 9.6550258001172671e-09], [-2.1023843894475475e-16, 0.94682975529055224, 8.7353734315874386e-09], [-2.0250081836393942e-16, 0.91198261012605808, 0.25459443571095286], [-1.7982809054022319e-16, 0.80987372154769699, 0.49047863804724123], [-1.4395803963139696e-16, 0.64832937364094645, 0.69010499520714996], [-1.1286962752152362e-16, 0.50831961244738044, 0.78955294719644886], [-9.622340400350482e-17, 0.433351686414505, 0.82875623161606715], [-1.0905743183449556e-16, 0.49115100937181749, 0.5588990652810587], [-5.4875726275800358e-17, 0.24713830040737983, 1.0000002495975611]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0))
        return createBuffer
    elif desiredShape == 'arrowRotate90Fat':
        createBuffer = mc.curve( d = 1,p = [[-1.869833338230926e-16, 0.84209807253017288, 0.0], [-2.2855818099516065e-16, 1.0293345387622839, 0.0], [-2.1114909596412071e-16, 0.95093098990363112, 0.39391832584289183], [-1.6160640804858012e-16, 0.72781055906826975, 0.72779596727134344], [-1.1358450911271974e-16, 0.51153915291510532, 0.86295522226144417], [-1.9762500914548622e-16, 0.89002391754670263, 0.94510977491741754], [-2.5232136943557574e-17, 0.11363544253676722, 0.9999995550169376], [-1.0888889594882822e-16, 0.49039199121992749, 0.31893655336341381], [-8.925897300298752e-17, 0.40198667755572776, 0.71924699824725358], [-1.3218835512646459e-16, 0.59532342689026474, 0.59552588807261442], [-1.727788407499008e-16, 0.7781267228187595, 0.3222580111387216], [-1.869833338230926e-16, 0.84209807253017288, 0.0]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0))
        return createBuffer         
    elif desiredShape == 'arrowRotate180':
        createBuffer = mc.curve( d = 1,p = [[-2.7437849444199252e-17, 0.12356908853274352, -0.49999987525849604], [-8.3264301593228682e-17, 0.37498907762852929, -0.48222486709225321], [-5.3176933751027959e-17, 0.23948761902583507, -0.4579939161062152], [-6.2378332332388635e-17, 0.28092703424813842, -0.43632644104313345], [-7.9551128667987284e-17, 0.35826643342604991, -0.38138792305833541], [-9.9381640492580305e-17, 0.44757511908985326, -0.27104278693460487], [-1.1190657694065273e-16, 0.50398241821023138, -0.14070273549936813], [-1.1618589561713776e-16, 0.52325475620704898, 4.8275104907413506e-09], [-1.1190657694065273e-16, 0.50398241821023138, 0.14070273549936813], [-9.9381640492580305e-17, 0.44757511908985326, 0.27104278693460487], [-7.9551128667987284e-17, 0.35826643342604991, 0.38138792305833541], [-6.2378332332388635e-17, 0.28092703424813842, 0.43632644104313345], [-5.3176933751027959e-17, 0.23948761902583507, 0.4579939161062152], [-8.3264301593228682e-17, 0.37498907762852929, 0.48222486709225321], [-2.7437849444199252e-17, 0.12356908853274352, 0.49999987525849604], [-5.4528688703032008e-17, 0.24557538212397673, 0.27944939317273243], [-4.8111677990142793e-17, 0.21667573506857637, 0.41437790900001942], [-5.6434785595249887e-17, 0.25415967937750122, 0.39477627657300651], [-7.1978983892377288e-17, 0.32416452503621729, 0.34505232539462111], [-8.9914000395769936e-17, 0.40493665867778011, 0.2452391966294723], [-1.012503586498705e-16, 0.45599107748668588, 0.12729715432392436], [-1.0511916700943061e-16, 0.47341464137316863, 4.3676845359666925e-09], [-1.012503586498705e-16, 0.45599107748668588, -0.12729715432392436], [-8.9914000395769936e-17, 0.40493665867778011, -0.2452391966294723], [-7.1978983892377288e-17, 0.32416452503621729, -0.34505232539462111], [-5.6434785595249887e-17, 0.25415967937750122, -0.39477627657300651], [-4.8111677990142793e-17, 0.21667573506857637, -0.41437790900001942], [-5.4528688703032008e-17, 0.24557538212397673, -0.27944939317273243], [-2.7437849444199252e-17, 0.12356908853274352, -0.49999987525849604]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0))
        return createBuffer          
    elif desiredShape == 'arrowRotate180Fat':
        createBuffer = mc.curve( d = 1,p = [[-1.2616072571693186e-17, 0.05681773973275657, -0.49999993999619563], [-9.8812536684395905e-17, 0.44501210339137887, -0.47255504102751594], [-5.6605262482610387e-17, 0.25492743902389325, -0.43057625160360968], [-8.0803230283359613e-17, 0.36390539779447073, -0.36389810189363664], [-1.0557458229121225e-16, 0.47546564946649927, -0.1969592269283677], [-1.1427912763549614e-16, 0.51466743663544579, 0.0], [-1.0557458229121225e-16, 0.47546564946649927, 0.1969592269283677], [-8.0803230283359613e-17, 0.36390539779447073, 0.36389810189363664], [-5.6792273012456769e-17, 0.25576965957642378, 0.43147775135041683], [-9.8812536684395905e-17, 0.44501210339137887, 0.47255504102751594], [-1.2616072571693186e-17, 0.05681773973275657, 0.49999993999619563], [-5.4444465667531152e-17, 0.24519607529267906, 0.1594683285050055], [-4.4629501004987828e-17, 0.20099340409579436, 0.35962361599248854], [-6.6094199042227188e-17, 0.29766181017792576, 0.29776304080199811], [-8.6389448449403958e-17, 0.38906348784547834, 0.1611290579323558], [-9.3491697294056688e-17, 0.42104917309574891, 0.0], [-8.6389448449403958e-17, 0.38906348784547834, -0.1611290579323558], [-6.6094199042227188e-17, 0.29766181017792576, -0.29776304080199811], [-4.4469321980506532e-17, 0.20027202190082782, -0.35822006706953846], [-5.4444465667531152e-17, 0.24519607529267906, -0.1594683285050055], [-1.2616072571693186e-17, 0.05681773973275657, -0.49999993999619563]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0))
        return createBuffer          
    #>>> Circle Arrows #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'circleArrow':
        createBuffer = mc.curve( d = 3,p = [[-0.27118683226552837, 0.083333345296857, 3.2459993430987253e-17], [-0.29190234857282799, 0.083333345296857, 3.7059762065259641e-17], [-0.31261786488012783, 0.083333345296857, 4.1659530699532053e-17], [-0.33333338118742761, 0.083333345296857014, 4.6259299333804496e-17], [-0.33333338118742767, 0.11111112706247595, 3.7007439467043614e-17], [-0.33333338118742761, 0.13888890882809493, 2.7755579600282695e-17], [-0.33333338118742739, 0.16666669059371389, 1.8503719733521758e-17], [-0.38888894471866553, 0.11111112706247599, 4.934325262272479e-17], [-0.44444450824990345, 0.055555563531238077, 8.0182785511927791e-17], [-0.50000007178114125, 1.6653347760169628e-16, 1.1102231840113073e-16], [-0.44444450824990345, -0.055555563531237778, 1.171902249789714e-16], [-0.38888894471866559, -0.11111112706247574, 1.2335813155681201e-16], [-0.33333338118742767, -0.16666669059371367, 1.2952603813465263e-16], [-0.33333338118742756, -0.13888890882809471, 1.2027417826789172e-16], [-0.3333333811874275, -0.11111112706247575, 1.1102231840113078e-16], [-0.33333338118742761, -0.083333345296856792, 1.0177045853436992e-16], [-0.31177693850940258, -0.083333345296856792, 9.6983966736338739e-17], [-0.2902204958313776, -0.083333345296856792, 9.2197474938307612e-17], [-0.27099054907217029, -0.080480888729432626, 3.9747834716103998e-17], [-0.25751955596282483, -0.12535618190776401, 6.1910807370215723e-17], [-0.20932750498738545, -0.20774126738935375, 1.0259908520227653e-16], [-0.1273528076130323, -0.25634370647202959, 1.2660281759087302e-16], [-0.083333345296856959, -0.26931551074687726, 1.0820380400948188e-16], [-0.083333345296856945, -0.29065480089372736, 1.153112153845388e-16], [-0.083333345296856959, -0.31199409104057751, 1.2241862675959574e-16], [-0.083333345296856973, -0.33333338118742761, 1.2952603813465263e-16], [-0.11111112706247593, -0.33333338118742756, 1.3569394471249326e-16], [-0.13888890882809496, -0.33333338118742756, 1.4186185129033383e-16], [-0.16666669059371392, -0.3333333811874275, 1.4802975786817441e-16], [-0.11111112706247593, -0.38888894471866553, 1.5419766444601503e-16], [-0.055555563531238063, -0.44444450824990345, 1.6036557102385566e-16], [-1.1102231840113083e-16, -0.50000007178114125, 1.6653347760169621e-16], [0.055555563531237799, -0.44444450824990345, 1.3569394471249323e-16], [0.11111112706247576, -0.38888894471866564, 1.0485441182329027e-16], [0.16666669059371367, -0.33333338118742767, 7.4014878934087252e-17], [0.13888890882809474, -0.33333338118742761, 8.0182785511927828e-17], [0.11111112706247578, -0.33333338118742761, 8.6350692089768428e-17], [0.083333345296856834, -0.33333338118742756, 9.2518598667609016e-17], [0.083333345296856834, -0.31195292845133477, 8.5397477396252973e-17], [0.083333345296856848, -0.29057247571524192, 7.8276356124896906e-17], [0.083363018364591743, -0.2701090011258192, 1.3340120992171225e-16], [0.12714011777698825, -0.25646971882893738, 1.2666505246940911e-16], [0.20784245909883511, -0.20869032551066055, 1.0306780524174454e-16], [0.25583769056679662, -0.12820382233849828, 6.3317197669311982e-17], [0.27036134114701899, -0.083333345296856876, -3.2276697581708746e-17], [0.29135202116048858, -0.083333345296856876, -3.6937564832407336e-17], [0.31234270117395807, -0.083333345296856876, -4.1598432083105943e-17], [0.33333338118742761, -0.083333345296856848, -4.6259299333804557e-17], [0.33333338118742767, -0.11111112706247582, -3.7007439467043651e-17], [0.33333338118742761, -0.13888890882809476, -2.7755579600282744e-17], [0.33333338118742756, -0.16666669059371375, -1.8503719733521813e-17], [0.38888894471866559, -0.11111112706247582, -4.9343252622724839e-17], [0.44444450824990345, -0.055555563531237875, -8.0182785511927853e-17], [0.50000007178114125, -1.6653347760169628e-16, -1.1102231840113073e-16], [0.44444450824990345, 0.055555563531237778, -1.171902249789714e-16], [0.38888894471866559, 0.11111112706247574, -1.2335813155681201e-16], [0.33333338118742767, 0.16666669059371367, -1.2952603813465263e-16], [0.33333338118742756, 0.13888890882809471, -1.2027417826789172e-16], [0.33333338118742717, 0.11111112706247575, -1.1102231840113076e-16], [0.33333338118742761, 0.083333345296856792, -1.0177045853436992e-16], [0.31148902055140182, 0.083333345296856792, -9.6920036107103663e-17], [0.28964465991537597, 0.083333345296856792, -9.206961367983741e-17], [0.26975761478166915, 0.084482855275632554, -4.1724322641734449e-17], [0.25605876755748702, 0.12783261797825185, -6.3133867567098828e-17], [0.2079818243709303, 0.20865862050519357, -1.03052146799885e-16], [0.12698296757958896, 0.25656270942735054, -1.2671097858919027e-16], [0.083333345296856959, 0.26915161947334892, -1.0814921724985999e-16], [0.083333345296856945, 0.29054554004470851, -1.1527482421145756e-16], [0.083333345296856959, 0.31193946061606803, -1.224004311730551e-16], [0.083333345296856973, 0.33333338118742761, -1.2952603813465263e-16], [0.11111112706247593, 0.33333338118742756, -1.3569394471249326e-16], [0.13888890882809496, 0.33333338118742756, -1.4186185129033383e-16], [0.16666669059371392, 0.3333333811874275, -1.4802975786817441e-16], [0.11111112706247593, 0.38888894471866553, -1.5419766444601503e-16], [0.055555563531238063, 0.44444450824990345, -1.6036557102385566e-16], [1.1102231840113078e-16, 0.50000007178114125, -1.6653347760169621e-16], [-0.055555563531237764, 0.44444450824990345, -1.3569394471249326e-16], [-0.11111112706247576, 0.38888894471866564, -1.0485441182329027e-16], [-0.16666669059371367, 0.33333338118742767, -7.4014878934087252e-17], [-0.13888890882809474, 0.33333338118742761, -8.0182785511927828e-17], [-0.11111112706247578, 0.33333338118742761, -8.6350692089768428e-17], [-0.083333345296856834, 0.33333338118742756, -9.2518598667609016e-17], [-0.083333345296856834, 0.31214594231237774, -8.5461763926033488e-17], [-0.083333345296856848, 0.29095850343732782, -7.840492918445791e-17], [-0.083333345296856848, 0.26977106456227795, -7.134809444288237e-17], [-0.12710456257619934, 0.25649076657048292, -1.2667544751058361e-16], [-0.20851654286712973, 0.20830280513239674, -1.0287641699805679e-16], [-0.25664962035075156, 0.12683594088700215, -6.2641629510167022e-17], [-0.27026171834409768, 0.08287131510520851, -4.0928416516148218e-17]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995))
        return createBuffer 
    elif desiredShape == 'circleArrow1':
        createBuffer = mc.curve( d = 3,p = [[-0.32784008818290866, 0.1358073473262727, 5.1994775905766823e-17], [-0.34565424562099251, 0.092803708783350647, 3.5530537459226834e-17], [-0.36249577169749692, 0.011491834151451427, 4.3997276525506716e-18], [-0.33907928648770008, -0.10382687029868372, 6.2349035099791287e-18], [-0.3386138041988328, -0.10437076890938181, 5.2012402227286303e-17], [-0.33861380409446201, -0.10437076890938181, 5.2012402204111345e-17], [-0.32042367176473086, -0.16056875512347313, -6.147485098913953e-17], [-0.27298182123517806, -0.2491717607007374, -9.7359389998622974e-17], [-0.19015879425519863, -0.30035423734208966, -1.1834739066036914e-16], [-0.11099348313369985, -0.34080460632330173, -1.3007625335970702e-16], [0.016150141954225584, -0.37377516553516027, -1.0616972511024827e-16], [0.15188073793626952, -0.33777199097512722, -1.2663042093903379e-16], [0.24692770494453706, -0.26272607392190517, -1.0017790311623017e-16], [0.32253012247735063, -0.15700223057949333, -6.0109382565835982e-17], [0.33940185496075054, -0.10079821239959394, -3.859128809008756e-17], [0.33940185542628287, -0.10079821246864826, -3.8591289352159646e-17], [0.33972298465384249, -0.10122103535502604, -3.8753170616774298e-17], [0.36049505018894357, -0.00022126213935611954, -8.4711730099650405e-20], [0.33936251377946131, 0.10239931261495297, 3.9204280306924424e-17], [0.26115634529686116, 0.2608886498710386, 9.9883011880157075e-17], [0.15919198828165743, 0.3212416161832371, 1.2298955965118465e-16], [0.10437076890938168, 0.33787451274837282, 5.184824654924447e-17], [0.10437076890938173, 0.36441070037809092, 5.7740463847701723e-17], [0.10437076890938173, 0.39094688800780919, 6.363268114615903e-17], [0.10437076890938168, 0.41748307563752729, 6.9524898444616289e-17], [0.13916102521250898, 0.41748307563752729, 6.1799909728547803e-17], [0.17395128151563621, 0.41748307563752729, 5.4074921012479341e-17], [0.20874153781876348, 0.41748307563752735, 4.6349932296410874e-17], [0.13916102521250895, 0.48706358824378188, 7.7249887160684763e-17], [0.069580512606254266, 0.55664410085003646, 1.0814984202495868e-16], [-2.1574019373088604e-16, 0.62622461345629088, 1.3904979688923255e-16], [-0.06958051260625478, 0.55664410085003646, 1.3904979688923258e-16], [-0.13916102521250925, 0.48706358824378188, 1.3904979688923258e-16], [-0.20874153781876381, 0.41748307563752723, 1.3904979688923255e-16], [-0.17395128151563652, 0.41748307563752729, 1.313248081731641e-16], [-0.13916102521250923, 0.41748307563752729, 1.2359981945709561e-16], [-0.10437076890938196, 0.41748307563752729, 1.1587483074102713e-16], [-0.10437076890938196, 0.3906882802040208, 1.0992519097494716e-16], [-0.10437076890938193, 0.36389348477051453, 1.0397555120886722e-16], [-0.10437076890938196, 0.33709868933700793, 9.8025911442787211e-17], [-0.15903969674401974, 0.32133172094576723, 1.2302405687852935e-16], [-0.25307624474132756, 0.2657169217295236, 1.0173154893088763e-16], [-0.31168365507356349, 0.17467298484820801, 6.687475223379902e-17], [-0.32947880609826946, 0.12945684945728803, 4.9563444169387122e-17]],k = (1.6323232779999994, 1.6323232779999994, 1.6323232779999994, 2.1323614440000007, 2.508560687000001, 2.508560687000001, 2.508560687000001, 2.508560687200001, 3.1190822461999996, 3.7377151422000008, 3.7377151422000008, 3.7377151422000008, 8.2503519831999999, 8.8673647371999973, 9.4995526522000002, 9.4995526522000002, 9.4995526522000002, 9.4995526572000024, 9.8696137562000015, 10.237290478200002, 10.858238904700002, 11.4771425542, 11.4771425542, 11.4771425542, 11.7313917842, 11.7313917842, 11.7313917842, 12.7313917842, 12.7313917842, 12.7313917842, 13.7313917842, 13.7313917842, 13.7313917842, 14.7313917842, 14.7313917842, 14.7313917842, 15.7313917842, 15.7313917842, 15.7313917842, 15.988118794199998, 15.988118794199998, 15.988118794199998, 16.607948209199996, 17.131222498200003, 17.131222498200003, 17.131222498200003))
        return createBuffer
    elif desiredShape == 'circleArrow2':
        createBuffer = mc.curve( d = 3,p = [[0.26175923154725922, 0.1084334349457699, -4.1514485495050624e-17], [0.27598269087921606, 0.07409779453912417, -2.8368849683201099e-17], [0.28942956660543712, 0.0091754906888452618, -3.5128996448608625e-18], [0.27073300875606748, -0.082899080261891092, -4.9781695722119841e-18], [0.2703613510771421, -0.083333348331928098, -4.1528558979478701e-17], [0.2703613509938087, -0.083333348331928098, -4.1528558960974983e-17], [0.25583769988462263, -0.1282038270077904, 4.9083715916467178e-17], [0.2078424666686341, -0.20869033311133955, 7.9898527711871296e-17], [0.12714012240753933, -0.25646972816978236, 9.8191197349313188e-17], [0.08336302140074367, -0.27010901096341855, 1.0341309046726605e-16], [0.083333348331928098, -0.29057248629813831, 4.6016332514711197e-17], [0.083333348331928098, -0.31195293981292538, 5.0763746868520088e-17], [0.083333348331928084, -0.33333339332771256, 5.5511161222329004e-17], [0.11111113110923747, -0.33333339332771256, 4.9343254419847997e-17], [0.13888891388654684, -0.33333339332771256, 4.3175347617367002e-17], [0.1666666966638562, -0.33333339332771261, 3.7007440814886019e-17], [0.11111113110923745, -0.38888895888233149, 6.1679068024810036e-17], [0.055555565554618637, -0.44444452443695015, 8.6350695234734017e-17], [-1.1102232244465801e-16, -0.50000008999156875, 1.1102232244465798e-16], [-0.055555565554618894, -0.44444452443695015, 1.1102232244465801e-16], [-0.11111113110923758, -0.38888895888233144, 1.1102232244465803e-16], [-0.16666669666385636, -0.3333333933277125, 1.1102232244465798e-16], [-0.13888891388654698, -0.33333339332771256, 1.04854415642177e-16], [-0.11111113110923758, -0.33333339332771256, 9.8686508839696007e-17], [-0.083333348331928181, -0.33333339332771256, 9.2518602037214999e-17], [-0.083333348331928181, -0.31199410240366748, 8.7780327614605105e-17], [-0.083333348331928181, -0.29065481147962224, 8.3042053191995173e-17], [-0.083333348331928181, -0.26931552055557706, 7.8303778769385254e-17], [-0.12735281225132977, -0.25634371580828524, 9.8142952651022627e-17], [-0.20932751261127111, -0.20774127495546726, 7.9535174276967898e-17], [-0.25751956534190595, -0.12535618647334268, 4.7993477174868963e-17], [-0.27099055894187624, -0.080480891660615006, 3.0812662267356146e-17], [-0.27099055931357391, -0.080480891715750458, 3.0812663275039566e-17], [-0.2712469603543961, -0.080818488604624775, 3.0941915056486703e-17], [-0.28783211911961648, -0.00017666359196456387, 6.7636869843551674e-20], [-0.27095914753810468, 0.0817592672379443, -3.1302097139439706e-17], [-0.20851655036298555, 0.20830281277726065, -7.9750162889746083e-17], [-0.12710456720545552, 0.25649077591209457, -9.819925562205317e-17], [-0.083333348331928084, 0.26977107438756931, -4.1397491225146062e-17], [-0.083333348331928098, 0.29095851403428374, -4.6102047890873714e-17], [-0.083333348331928098, 0.31214595368099823, -5.0806604556601378e-17], [-0.083333348331928084, 0.33333339332771256, -5.5511161222329004e-17], [-0.11111113110923747, 0.33333339332771256, -4.9343254419847997e-17], [-0.13888891388654684, 0.33333339332771256, -4.3175347617367002e-17], [-0.1666666966638562, 0.33333339332771261, -3.7007440814886019e-17], [-0.11111113110923745, 0.38888895888233149, -6.1679068024810036e-17], [-0.055555565554618595, 0.44444452443695015, -8.6350695234734029e-17], [1.1102232244465796e-16, 0.50000008999156875, -1.1102232244465798e-16], [0.055555565554618894, 0.44444452443695015, -1.1102232244465801e-16], [0.11111113110923759, 0.38888895888233144, -1.1102232244465803e-16], [0.16666669666385639, 0.3333333933277125, -1.1102232244465798e-16], [0.13888891388654703, 0.33333339332771256, -1.0485441564217701e-16], [0.11111113110923759, 0.33333339332771256, -9.8686508839696007e-17], [0.083333348331928209, 0.33333339332771256, -9.2518602037214999e-17], [0.083333348331928209, 0.31193947197716826, -8.7768197223136198e-17], [0.083333348331928195, 0.29054555062662402, -8.301779240905741e-17], [0.083333348331928209, 0.26915162927607966, -7.8267387594978596e-17], [0.12698297220441654, 0.25656271877158243, -9.8226799440047824e-17], [0.20206510958902796, 0.21215787741680278, -8.1226100870875177e-17], [0.24885935850645113, 0.13946514759483478, -5.3395189867281129e-17], [0.26306764243936553, 0.10336297071016821, -3.9573223428905305e-17]],k = (1.6323232779999994, 1.6323232779999994, 1.6323232779999994, 2.1323614440000007, 2.508560687000001, 2.508560687000001, 2.508560687000001, 2.508560687200001, 3.1190822461999996, 3.7377151422000008, 3.7377151422000008, 3.7377151422000008, 3.9942805382, 3.9942805382, 3.9942805382, 4.9942805382, 4.9942805382, 4.9942805382, 5.9942805382, 5.9942805382, 5.9942805382, 6.9942805382, 6.9942805382, 6.9942805382, 7.9942805382, 7.9942805382, 7.9942805382, 8.2503519831999999, 8.2503519831999999, 8.2503519831999999, 8.8673647371999973, 9.4995526522000002, 9.4995526522000002, 9.4995526522000002, 9.4995526572000024, 9.8696137562000015, 10.237290478200002, 10.858238904700002, 11.4771425542, 11.4771425542, 11.4771425542, 11.7313917842, 11.7313917842, 11.7313917842, 12.7313917842, 12.7313917842, 12.7313917842, 13.7313917842, 13.7313917842, 13.7313917842, 14.7313917842, 14.7313917842, 14.7313917842, 15.7313917842, 15.7313917842, 15.7313917842, 15.988118794199998, 15.988118794199998, 15.988118794199998, 16.607948209199996, 17.131222498200003, 17.131222498200003, 17.131222498200003))
        return createBuffer 
    elif desiredShape == 'circleArrow3':
        createBuffer = mc.curve( d = 3,p = [[0.083333345296856903, -0.27118683226552842, 1.5053893257817498e-16], [-1.5814710273535653e-05, -0.27767153843689468, 1.5097879301346805e-16], [-0.080480888729432709, -0.27099054907217024, 1.976596489218251e-16], [-0.1253561819077641, -0.25751955596282478, 1.7997408668453624e-16], [-0.20774126738935381, -0.20932750498738542, 1.2927280727089782e-16], [-0.25634370647202964, -0.12735280761303225, 5.7749801435879419e-17], [-0.26931551074687732, -0.083333345296856903, 4.625929933380452e-17], [-0.29065480089372742, -0.083333345296856876, 4.6259299333804502e-17], [-0.31199409104057751, -0.083333345296856889, 4.6259299333804514e-17], [-0.33333338118742761, -0.083333345296856903, 4.625929933380452e-17], [-0.33333338118742761, -0.11111112706247586, 6.1679065778406027e-17], [-0.33333338118742761, -0.13888890882809488, 7.7098832223007565e-17], [-0.33333338118742756, -0.16666669059371383, 9.2518598667609078e-17], [-0.38888894471866559, -0.11111112706247583, 6.1679065778406027e-17], [-0.44444450824990345, -0.055555563531237966, 3.0839532889203032e-17], [-0.50000007178114125, -9.6236175233407056e-33, 7.4790532282192828e-48], [-0.44444450824990345, 0.055555563531237889, -3.0839532889202989e-17], [-0.38888894471866559, 0.11111112706247586, -6.1679065778406027e-17], [-0.33333338118742761, 0.16666669059371375, -9.2518598667609004e-17], [-0.33333338118742756, 0.13888890882809479, -7.7098832223007503e-17], [-0.33333338118742756, 0.11111112706247586, -6.1679065778406027e-17], [-0.33333338118742756, 0.083333345296856903, -4.625929933380452e-17], [-0.31195292845133477, 0.083333345296856903, -4.625929933380452e-17], [-0.29057247571524186, 0.083333345296856917, -4.6259299333804539e-17], [-0.27010900112581915, 0.083363018364591784, -1.082229199326299e-16], [-0.25646971882893732, 0.12714011777698828, -1.4005119665719783e-16], [-0.2086903255106605, 0.20784245909883514, -1.950860024325757e-16], [-0.12820382233849817, 0.25583769056679662, -2.1944257329169452e-16], [-0.083333345296856778, 0.27036134114701904, -1.5008069295497865e-16], [-0.083333345296856765, 0.29135202116048858, -1.6173286108172517e-16], [-0.083333345296856765, 0.31234270117395813, -1.7338502920847166e-16], [-0.083333345296856751, 0.33333338118742761, -1.8503719733521808e-16], [-0.11111112706247571, 0.33333338118742767, -1.8503719733521816e-16], [-0.13888890882809465, 0.33333338118742761, -1.8503719733521808e-16], [-0.16666669059371364, 0.33333338118742761, -1.8503719733521813e-16], [-0.1111111270624757, 0.38888894471866559, -2.1587673022442103e-16], [-0.05555556353123773, 0.44444450824990345, -2.4671626311362411e-16], [-7.6000622487577886e-33, 0.50000007178114125, -2.7755579600282704e-16], [0.055555563531237917, 0.44444450824990345, -2.4671626311362411e-16], [0.11111112706247586, 0.38888894471866559, -2.1587673022442103e-16], [0.16666669059371378, 0.33333338118742761, -1.8503719733521808e-16], [0.13888890882809482, 0.33333338118742756, -1.8503719733521806e-16], [0.11111112706247586, 0.33333338118742717, -1.8503719733521784e-16], [0.083333345296856903, 0.33333338118742761, -1.8503719733521808e-16], [0.083333345296856903, 0.31148902055140176, -1.7291114126705239e-16], [0.083333345296856903, 0.28964465991537597, -1.6078508519888682e-16], [0.084482855275632637, 0.2697576147816691, -1.9605790119119097e-16], [0.12783261797825193, 0.25605876755748697, -1.7844058474579538e-16], [0.20865862050519363, 0.20798182437093027, -1.2807948171563821e-16], [0.2565627094273506, 0.12698296757958891, -5.7427159630209787e-17], [0.26915161947334898, 0.083333345296856903, -4.625929933380452e-17], [0.29054554004470856, 0.083333345296856876, -4.6259299333804502e-17], [0.31193946061606809, 0.083333345296856889, -4.6259299333804514e-17], [0.33333338118742761, 0.083333345296856903, -4.625929933380452e-17], [0.33333338118742761, 0.11111112706247586, -6.1679065778406027e-17], [0.33333338118742761, 0.13888890882809488, -7.7098832223007565e-17], [0.33333338118742756, 0.16666669059371383, -9.2518598667609078e-17], [0.38888894471866559, 0.11111112706247583, -6.1679065778406027e-17], [0.44444450824990345, 0.055555563531237966, -3.0839532889203032e-17], [0.50000007178114125, -1.5949542486978914e-32, 1.2395284510896821e-47], [0.44444450824990345, -0.055555563531237855, 3.0839532889202964e-17], [0.38888894471866559, -0.11111112706247586, 6.1679065778406027e-17], [0.33333338118742761, -0.16666669059371375, 9.2518598667609004e-17], [0.33333338118742756, -0.13888890882809479, 7.7098832223007503e-17], [0.33333338118742756, -0.11111112706247586, 6.1679065778406027e-17], [0.33333338118742756, -0.083333345296856903, 4.625929933380452e-17], [0.31214594231237769, -0.083333345296856903, 4.625929933380452e-17], [0.29095850343732776, -0.083333345296856917, 4.6259299333804539e-17], [0.2697710645622779, -0.083333345296856903, 4.625929933380452e-17], [0.25649076657048286, -0.12710456257619937, 1.4002694945039556e-16], [0.20830280513239666, -0.20851654286712976, 1.9554755272688667e-16], [0.12683594088700204, -0.25664962035075162, 2.1985359737564023e-16], [0.082871315105208412, -0.27026171834409768, 2.2336227154918095e-16]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995))
        return createBuffer
    elif desiredShape == 'circleArrow1Interior':    
        createBuffer = mc.curve( d = 3,p = [[-0.27624032233739726, 0.11443013961678067, -0.00068814405594507183], [-0.29125065441771297, 0.078195631989783049, -0.0004702420143403071], [-0.3054414405958561, 0.0096829237319847796, -5.8229819806648762e-05], [-0.28571054844591803, -0.087483656062497431, 0.00052609704150816962], [-0.28531832985473915, -0.087941940501335858, 0.00052885300871732756], [-0.28531832976679561, -0.087941940501335858, 0.00052885300871732756], [-0.26999119864632881, -0.13529389557053204, 0.00081361160926925907], [-0.2300163677609291, -0.20995005002964603, 0.0012625684059908676], [-0.16022911325914349, -0.25307597851075936, 0.0015219131157043766], [-0.093523875399573977, -0.28715912247314002, 0.0017268775857660155], [0.013608221142073884, -0.3149398410287586, 0.001893941406608649], [0.12797575865996291, -0.28460386604167548, 0.0017115111400846917], [0.20806298944702623, -0.22137080144585264, 0.0013312489321862279], [0.27176610856374345, -0.13228877169800837, 0.00079553981334922212], [0.28598234686893947, -0.084931734144667009, 0.0005107506484610543], [0.28598234726120025, -0.084931734202851591, 0.0005107506488109567], [0.28625293296603183, -0.085288001244907416, 0.00051289311799032568], [0.30375561883594437, -0.000186433635564577, 1.1211486639065482e-06], [0.28594919771789851, 0.086280807849374919, -0.00051886352024497031], [0.2200521400696186, 0.2198226032458632, -0.0013219385932115879], [0.13413626869183098, 0.27067550993580697, -0.0016277507296243135], [0.087943530658288346, 0.28469025003383219, -0.0017120306241204342], [0.087943530658288346, 0.30704942069100249, -0.0018464910943699806], [0.087943530658288346, 0.32940859134817291, -0.0019809515646195285], [0.087943530658288194, 0.50915820170441795, -0.0030619047675024243], [0.11725804087771771, 0.50915820170441795, -0.0030619047675024308], [0.14657255109714717, 0.50915820170441795, -0.0030619047675024373], [0.17588706131657669, 0.50915820170441795, -0.0030619047675024438], [0.11725804087771768, 0.56778616203864163, -0.0034144734399806057], [0.05862902043885853, 0.62641412237286553, -0.0037670421124587688], [-3.3029901145564908e-16, 0.68504208270708933, -0.0041196107849369315], [-0.058629020438859231, 0.62641412237286542, -0.0037670421124587419], [-0.11725804087771817, 0.56778616203864163, -0.0034144734399805536], [-0.17588706131657719, 0.50915820170441772, -0.0030619047675023645], [-0.14657255109714762, 0.50915820170441783, -0.0030619047675023718], [-0.11725804087771811, 0.50915820170441783, -0.0030619047675023783], [-0.087943530658288624, 0.50915820170441783, -0.0030619047675023848], [-0.087943530658288721, 0.32919069056683742, -0.0019796411832115491], [-0.087943530658288679, 0.30661361912833179, -0.0018438703315540636], [-0.087943530658288707, 0.28403654768982595, -0.0017080994798965763], [-0.13400794679050579, 0.27075143145816533, -0.0016282072959144902], [-0.21324379154107068, 0.22389086489555754, -0.0013464037392093291], [-0.26262680022457363, 0.14717800205198101, -0.00088507859570146079], [-0.27762111736972039, 0.10907926301039104, -0.00065596569853753988]],k = (1.6323232779999994, 1.6323232779999994, 1.6323232779999994, 2.1323614440000007, 2.508560687000001, 2.508560687000001, 2.508560687000001, 2.508560687200001, 3.1190822461999996, 3.7377151422000008, 3.7377151422000008, 3.7377151422000008, 8.2503519831999999, 8.8673647371999973, 9.4995526522000002, 9.4995526522000002, 9.4995526522000002, 9.4995526572000024, 9.8696137562000015, 10.237290478200002, 10.858238904700002, 11.4771425542, 11.4771425542, 11.4771425542, 11.7313917842, 11.7313917842, 11.7313917842, 12.7313917842, 12.7313917842, 12.7313917842, 13.7313917842, 13.7313917842, 13.7313917842, 14.7313917842, 14.7313917842, 14.7313917842, 15.7313917842, 15.7313917842, 15.7313917842, 15.988118794199998, 15.988118794199998, 15.988118794199998, 16.607948209199996, 17.131222498200003, 17.131222498200003, 17.131222498200003))
        return createBuffer 
    elif desiredShape == 'circleArrow2Axis':  
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[0.098459185680312131, 0.2376813092321291, 6.8609297062635063e-17], [0.067281909077932883, 0.25059642368997037, 6.6463340084036035e-17], [0.0083314831988195569, 0.26280638858327315, 5.9694545408489381e-17], [-0.075273608553623306, 0.24582963356491161, 7.5819495191855764e-17], [-0.075667930476231313, 0.24549216281673203, 1.0902042060966535e-16], [-0.075667930476231313, 0.24549216274106408, 1.0902042057606203e-16], [-0.11641099827373046, 0.23230446964593521, 3.2861637885305274e-17], [-0.18064743282396881, 0.19790952664565156, 1.3471790827494349e-17], [-0.21775429832442064, 0.13786352801174889, -6.8378440529904764e-18], [-0.24708047594859556, 0.080469342641017849, -2.1573520648494767e-17], [-0.27098385433964162, -0.011708717214056776, -1.9401513216063635e-17], [-0.24488185530294276, -0.11011225881471209, -6.1881129351228614e-17], [-0.19047419601820043, -0.17902051125656751, -7.0084909099227146e-17], [-0.11382529794733001, -0.23383162871297741, -7.0225555590078985e-17], [-0.073077857025304005, -0.24606349299746783, -6.6388886796318183e-17], [-0.073077857075367805, -0.2460634933349749, -6.6388887775135069e-17], [-0.073384400115191262, -0.24629630932664359, -6.6489879638481632e-17], [-0.0001604131918616471, -0.26135588230078177, -5.8058460039024056e-17], [0.074238641228077079, -0.24603497097160032, -4.269225388312173e-17], [0.18914207902041325, -0.18933615595480405, -1.1624705819043144e-17], [0.23289747247651385, -0.11541285388179878, 1.1825968510737888e-17], [0.24495618272709915, -0.075667930476231091, -3.3603311456178956e-17], [0.26419469578637433, -0.075667930476231091, -3.3603311456178956e-17], [0.2834332088456496, -0.075667930476231077, -3.360331145617895e-17], [0.438095261354707, -0.07566793047623091, -3.3603311456178913e-17], [0.438095261354707, -0.10089057396830803, -4.4804415274905252e-17], [0.438095261354707, -0.12611321746038509, -5.6005519093631572e-17], [0.438095261354707, -0.15133586095246221, -6.7206622912357911e-17], [0.48854054833886096, -0.10089057396830799, -4.4804415274905246e-17], [0.53898583532301514, -0.05044528698415366, -2.2402207637452543e-17], [0.58943112230716921, 4.150742154038662e-16, 9.2164990173918816e-32], [0.53898583532301503, 0.0504452869841545, 2.2402207637452728e-17], [0.48854054833886096, 0.10089057396830863, 4.4804415274905375e-17], [0.43809526135470683, 0.15133586095246279, 6.7206622912358035e-17], [0.43809526135470689, 0.12611321746038565, 5.6005519093631708e-17], [0.43809526135470689, 0.10089057396830856, 4.4804415274905357e-17], [0.43809526135470689, 0.075667930476231493, 3.3603311456179042e-17], [0.28324572036087414, 0.075667930476231535, 3.3603311456179054e-17], [0.26381971881682365, 0.075667930476231493, 3.3603311456179042e-17], [0.24439371727277293, 0.075667930476231507, 3.3603311456179042e-17], [0.23296279767223621, 0.11530244379665251, 6.306556072659416e-17], [0.19264253554790486, 0.18347815094568226, 7.1719616009681517e-17], [0.12663644631233428, 0.22596803098347273, 7.0539675924354834e-17], [0.093855128085824205, 0.23886936595131772, 6.8132709717664651e-17]],k = (1.6323232779999994, 1.6323232779999994, 1.6323232779999994, 2.1323614440000007, 2.508560687000001, 2.508560687000001, 2.508560687000001, 2.508560687200001, 3.1190822461999996, 3.7377151422000008, 3.7377151422000008, 3.7377151422000008, 8.2503519831999999, 8.8673647371999973, 9.4995526522000002, 9.4995526522000002, 9.4995526522000002, 9.4995526572000024, 9.8696137562000015, 10.237290478200002, 10.858238904700002, 11.4771425542, 11.4771425542, 11.4771425542, 11.7313917842, 11.7313917842, 11.7313917842, 12.7313917842, 12.7313917842, 12.7313917842, 13.7313917842, 13.7313917842, 13.7313917842, 14.7313917842, 14.7313917842, 14.7313917842, 15.7313917842, 15.7313917842, 15.7313917842, 15.988118794199998, 15.988118794199998, 15.988118794199998, 16.607948209199996, 17.131222498200003, 17.131222498200003, 17.131222498200003)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.3278401537509395, 0.13580737448774752, 5.1994786304724066e-17], [-0.3456543147518556, 0.09280372734409606, 3.5530544565335732e-17], [-0.36249584419666592, 0.01149183644981863, 4.3997285324963597e-18], [-0.33907935430357111, -0.10382689106406202, 6.2349047569600591e-18], [-0.3386138719216073, -0.10437078978353986, 5.2012412629768805e-17], [-0.33861387181723651, -0.10437078978353986, 5.2012412606593847e-17], [-0.3204237358494782, -0.1605687872372307, -6.1474863284112225e-17], [-0.27298187583155331, -0.24917181053509962, -9.7359409470504901e-17], [-0.19015883228696512, -0.30035429741294933, -1.1834741432985205e-16], [-0.11099350533240088, -0.34080467448423674, -1.3007627937496291e-16], [0.01615014518425472, -0.37377524029020842, -1.0616974634419756e-16], [0.15188076831242334, -0.33777205852953901, -1.2663044626512307e-16], [0.2469277543300881, -0.26272612646713045, -1.001779231518148e-16], [0.3225301869833882, -0.15700226197994571, -6.0109394587714904e-17], [0.33940192284113524, -0.10079823255924039, -3.8591295808346709e-17], [0.33940192330666769, -0.10079823262829472, -3.8591297070419042e-17], [0.33972305259845315, -0.10122105559923711, -3.8753178367409963e-17], [0.36049512228796821, -0.00022126218360846804, -8.471174704198022e-20], [0.3393625816519778, 0.1023993330948197, 3.920428814778208e-17], [0.26115639752814068, 0.26088870204877918, 9.9883031856763488e-17], [0.15919202012006145, 0.32124168043157325, 1.2298958424910153e-16], [0.10437078978353963, 0.33787458032328899, 5.1848256918895876e-17], [0.10437078978353963, 0.36441077326024568, 5.7740475395796825e-17], [0.10437078978353963, 0.39094696619720254, 6.3632693872697817e-17], [0.1043707897835396, 0.41748315913415923, 6.9524912349598784e-17], [0.13916105304471957, 0.41748315913415923, 6.179992208853225e-17], [0.17395131630589947, 0.41748315913415923, 5.4074931827465734e-17], [0.20874157956707942, 0.41748315913415929, 4.6349941566399218e-17], [0.13916105304471951, 0.48706368565651914, 7.7249902610665318e-17], [0.069580526522359479, 0.55664421217887894, 1.0814986365493143e-16], [-3.6912106123840545e-16, 0.62622473870123885, 1.3904982469919754e-16], [-0.069580526522360256, 0.55664421217887894, 1.3904982469919752e-16], [-0.13916105304472007, 0.48706368565651914, 1.3904982469919754e-16], [-0.20874157956707992, 0.41748315913415912, 1.3904982469919752e-16], [-0.17395131630589994, 0.41748315913415923, 1.3132483443813101e-16], [-0.13916105304472001, 0.41748315913415923, 1.2359984417706447e-16], [-0.10437078978354007, 0.41748315913415923, 1.1587485391599794e-16], [-0.10437078978354007, 0.39068835834169258, 1.0992521295998978e-16], [-0.10437078978354003, 0.36389355754922614, 1.0397557200398164e-16], [-0.10437078978354004, 0.33709875675675938, 9.8025931047973442e-17], [-0.15903972855196563, 0.32133178521212435, 1.2302408148334565e-16], [-0.25307629535658688, 0.26571697487291857, 1.0173156927720148e-16], [-0.31168371741030715, 0.17467301978281194, 6.6874765608752147e-17], [-0.32947887199404402, 0.12945687534866304, 4.9563454082077924e-17]],k = (1.6323232779999994, 1.6323232779999994, 1.6323232779999994, 2.1323614440000007, 2.508560687000001, 2.508560687000001, 2.508560687000001, 2.508560687200001, 3.1190822461999996, 3.7377151422000008, 3.7377151422000008, 3.7377151422000008, 8.2503519831999999, 8.8673647371999973, 9.4995526522000002, 9.4995526522000002, 9.4995526522000002, 9.4995526572000024, 9.8696137562000015, 10.237290478200002, 10.858238904700002, 11.4771425542, 11.4771425542, 11.4771425542, 11.7313917842, 11.7313917842, 11.7313917842, 12.7313917842, 12.7313917842, 12.7313917842, 13.7313917842, 13.7313917842, 13.7313917842, 14.7313917842, 14.7313917842, 14.7313917842, 15.7313917842, 15.7313917842, 15.7313917842, 15.988118794199998, 15.988118794199998, 15.988118794199998, 16.607948209199996, 17.131222498200003, 17.131222498200003, 17.131222498200003)))
        return combineCurves(createdCurves)
    elif desiredShape == 'masterAnim':  
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[-0.27118683226552831, 5.0963713164509079e-17, -0.083333345296857], [-0.29190234857282799, 5.5563481798781466e-17, -0.083333345296857], [-0.31261786488012783, 6.0163250433053878e-17, -0.083333345296857], [-0.33333338118742767, 6.4763019067326327e-17, -0.083333345296857014], [-0.33333338118742772, 6.1679065778406027e-17, -0.11111112706247596], [-0.33333338118742767, 5.8595112489485727e-17, -0.1388889088280949], [-0.33333338118742745, 5.551115920056539e-17, -0.16666669059371389], [-0.38888894471866553, 7.401487893408724e-17, -0.111111127062476], [-0.44444450824990345, 9.2518598667609029e-17, -0.05555556353123807], [-0.50000007178114136, 1.1102231840113078e-16, -1.6653347760169626e-16], [-0.44444450824990345, 1.0485441182329023e-16, 0.055555563531237771], [-0.38888894471866559, 9.8686505245449629e-17, 0.11111112706247575], [-0.33333338118742772, 9.2518598667609041e-17, 0.1666666905937137], [-0.33333338118742761, 8.9434645378688741e-17, 0.13888890882809471], [-0.33333338118742756, 8.6350692089768391e-17, 0.11111112706247576], [-0.33333338118742767, 8.326673880084814e-17, 0.083333345296856792], [-0.31177693850940258, 7.8480247002816963e-17, 0.083333345296856792], [-0.2902204958313776, 7.3693755204785823e-17, 0.083333345296856792], [-0.27099054907217029, 2.1877487574161723e-17, 0.080480888729432626], [-0.25751955596282483, 3.4076143483595905e-17, 0.12535618190776401], [-0.20932750498738548, 5.6471257558182193e-17, 0.20774126738935378], [-0.1273528076130323, 6.9683080562273015e-17, 0.25634370647202959], [-0.083333345296856959, 4.8403747825508506e-17, 0.26931551074687732], [-0.083333345296856945, 5.0772884950527465e-17, 0.29065480089372742], [-0.083333345296856959, 5.3142022075546449e-17, 0.31199409104057757], [-0.083333345296856973, 5.5511159200565415e-17, 0.33333338118742767], [-0.11111112706247595, 6.1679065778406015e-17, 0.33333338118742761], [-0.13888890882809493, 6.7846972356246628e-17, 0.33333338118742761], [-0.16666669059371392, 7.4014878934087228e-17, 0.33333338118742756], [-0.11111112706247595, 6.7846972356246615e-17, 0.38888894471866553], [-0.055555563531238056, 6.1679065778406015e-17, 0.44444450824990345], [-1.1102231840113083e-16, 5.5511159200565415e-17, 0.50000007178114136], [0.055555563531237792, 3.7007439467043614e-17, 0.44444450824990345], [0.11111112706247578, 1.8503719733521813e-17, 0.38888894471866564], [0.1666666905937137, 1.430359528141852e-32, 0.33333338118742772], [0.13888890882809474, 6.1679065778406064e-18, 0.33333338118742767], [0.11111112706247578, 1.2335813155681201e-17, 0.33333338118742767], [0.083333345296856848, 1.8503719733521804e-17, 0.33333338118742761], [0.083333345296856848, 1.613001264306978e-17, 0.31195292845133471], [0.083333345296856862, 1.3756305552617758e-17, 0.29057247571524186], [0.083363018364591743, 7.3424963480034861e-17, 0.2701090011258192], [0.12714011777698825, 6.9717335076803856e-17, 0.25646971882893732], [0.20784245909883511, 5.6729244362053745e-17, 0.20869032551066052], [0.25583769056679662, 3.4850230588281228e-17, 0.12820382233849828], [0.27036134114701899, -5.0780417315230547e-17, 0.083333345296856889], [0.29135202116048853, -5.5441284565929143e-17, 0.083333345296856889], [0.31234270117395807, -6.0102151816627732e-17, 0.083333345296856889], [0.33333338118742767, -6.4763019067326352e-17, 0.083333345296856862], [0.33333338118742772, -6.167906577840604e-17, 0.11111112706247582], [0.33333338118742767, -5.8595112489485739e-17, 0.13888890882809476], [0.33333338118742761, -5.5511159200565415e-17, 0.16666669059371378], [0.38888894471866559, -7.4014878934087252e-17, 0.11111112706247582], [0.44444450824990345, -9.2518598667609041e-17, 0.055555563531237882], [0.50000007178114136, -1.1102231840113078e-16, 1.6653347760169626e-16], [0.44444450824990345, -1.0485441182329023e-16, -0.055555563531237771], [0.38888894471866559, -9.8686505245449629e-17, -0.11111112706247575], [0.33333338118742772, -9.2518598667609041e-17, -0.1666666905937137], [0.33333338118742761, -8.9434645378688741e-17, -0.13888890882809471], [0.33333338118742717, -8.6350692089768367e-17, -0.11111112706247576], [0.33333338118742767, -8.326673880084814e-17, -0.083333345296856792], [0.31148902055140182, -7.8416316373581875e-17, -0.083333345296856792], [0.28964465991537602, -7.3565893946315622e-17, -0.083333345296856792], [0.26975761478166921, -2.2965360419118022e-17, -0.084482855275632554], [0.25605876755748702, -3.4749324411585448e-17, -0.12783261797825182], [0.2079818243709303, -5.6720625845607256e-17, -0.20865862050519357], [0.12698296757958893, -6.9742613135898617e-17, -0.25656270942735054], [0.083333345296856959, -4.8385552238967876e-17, -0.26915161947334887], [0.083333345296856945, -5.0760754559500389e-17, -0.29054554004470851], [0.083333345296856959, -5.3135956880032902e-17, -0.31193946061606803], [0.083333345296856973, -5.5511159200565415e-17, -0.33333338118742767], [0.11111112706247595, -6.1679065778406015e-17, -0.33333338118742761], [0.13888890882809493, -6.7846972356246628e-17, -0.33333338118742761], [0.16666669059371392, -7.4014878934087228e-17, -0.33333338118742756], [0.11111112706247595, -6.7846972356246615e-17, -0.38888894471866553], [0.055555563531238056, -6.1679065778406015e-17, -0.44444450824990345], [1.1102231840113078e-16, -5.5511159200565415e-17, -0.50000007178114136], [-0.055555563531237757, -3.700743946704362e-17, -0.44444450824990345], [-0.11111112706247578, -1.8503719733521813e-17, -0.38888894471866564], [-0.1666666905937137, -1.4303595281418523e-32, -0.33333338118742772], [-0.13888890882809474, -6.1679065778406064e-18, -0.33333338118742767], [-0.11111112706247578, -1.2335813155681201e-17, -0.33333338118742767], [-0.083333345296856848, -1.8503719733521804e-17, -0.33333338118742761], [-0.083333345296856848, -1.6151441486329952e-17, -0.31214594231237774], [-0.083333345296856862, -1.3799163239138094e-17, -0.29095850343732776], [-0.083333345296856862, -1.1446884991946246e-17, -0.26977106456227795], [-0.12710456257619937, -6.9723056580522298e-17, -0.25649076657048286], [-0.2085165428671297, -5.6623902927657973e-17, -0.20830280513239677], [-0.25664962035075162, -3.4478393125618012e-17, -0.12683594088700212], [-0.27026171834409768, -2.2527288093994418e-17, -0.08287131510520851]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        createdCurves.append(mc.curve( d = 3,p = [[1.4057201132611796e-17, 1.4057201132611796e-17, -0.22957151633269232], [-0.058414534874067073, 1.4057201132611796e-17, -0.22957151633269232], [-0.18004261502304847, 1.1033111110977267e-17, -0.18018437836376902], [-0.25409126930803444, 6.7934389616067828e-20, -0.001109452777133234], [-0.18100829360871529, -1.0936833172124684e-17, 0.17861204029993519], [-0.0022188513895999916, -1.5568639958856005e-17, 0.2542551855717991], [0.1778635152469584, -1.1128602257249335e-17, 0.18174386712964916], [0.25407193259778965, -2.0361101996689876e-19, 0.0033252203020276649], [0.18315984466557828, 1.0839027870971301e-17, -0.17701475851678794], [0.062412213466930301, 1.3992635361726024e-17, -0.22851707727433315], [0.0040065754094616955, 1.405506015279172e-17, -0.22953655147880028]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        return combineCurves(createdCurves)    
    else:
        return ('desiredShape not found')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
