#=================================================================================================================================================
#=================================================================================================================================================
#	attribute - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with attributes
# 
# REQUIRES:
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

from cgm.lib import (distance,
                     dictionary,
                     cgmMath,
                     attributes,
                     search,
                     rigging,
                     autoname,
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
    
    REQUIRES:
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
    
    REQUIRES:
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
    print "curve scale is '%s'"%curveScale
    objScale =  mc.xform(obj,q=True, s=True,r=True)
    print "curve scale is '%s'"%objScale
    
    """account for freezing"""
    mc.makeIdentity(workingCurve,apply=True,translate =True, rotate = True, scale=False)
    
    
    """ make our zero out group"""
    group = rigging.groupMeObject(obj,False)
    pos = []
    pos.append(mc.getAttr(group+'.translateX') - mc.getAttr(obj+'.translateX'))
    pos.append(mc.getAttr(group+'.translateY') - mc.getAttr(obj+'.translateY'))
    pos.append(mc.getAttr(group+'.translateZ') - mc.getAttr(obj+'.translateZ'))
    
    workingCurve = rigging.doParentReturnName(workingCurve,group)
    
    """ zero out the group """
    mc.setAttr((group+'.tx'),pos[0])
    mc.setAttr((group+'.ty'),pos[1])
    mc.setAttr((group+'.tz'),pos[2])
    mc.setAttr((group+'.rx'),0)
    mc.setAttr((group+'.ry'),0)
    mc.setAttr((group+'.rz'),0)
    
    """ zero out the object """

    #main scale fix 
    baseMultiplier = [0,0,0]
    baseMultiplier[0] = ( curveScale[0]/objScale[0] )
    baseMultiplier[1] = ( curveScale[1]/objScale[1] )
    baseMultiplier[2] = ( curveScale[2]/objScale[2] )

    #parent scale fix     
    if parents:
	parents.reverse()
	multiplier = [baseMultiplier[0],baseMultiplier[1],baseMultiplier[2]]
        for p in parents:
	    scaleBuffer = []
	    scaleBuffer.append(mc.getAttr(p+'.sx'))
	    scaleBuffer.append(mc.getAttr(p+'.sy'))
	    scaleBuffer.append(mc.getAttr(p+'.sz'))
            #scaleBuffer = mc.xform(p,q=True, s=True,r=True)
	    print "'%s' scale is '%s'"%(p,objScale)
	    #multiplier[0] = ( (scaleBuffer[0]/objScale[0]) * multiplier[0] )
	    #multiplier[1] = ( (scaleBuffer[1]/objScale[1]) * multiplier[1] )
	    #multiplier[2] = ( (scaleBuffer[2]/objScale[2]) * multiplier[2] )
	    
	    multiplier[0] = ( (objScale[0]/scaleBuffer[0]) * multiplier[0] )
	    multiplier[1] = ( (objScale[1]/scaleBuffer[1]) * multiplier[1] )
	    multiplier[2] = ( (objScale[2]/scaleBuffer[2]) * multiplier[2] )
	    
	    mc.setAttr(workingCurve+'.sx',multiplier[0])
	    mc.setAttr(workingCurve+'.sy',multiplier[1])
	    mc.setAttr(workingCurve+'.sz',multiplier[2])
	    mc.makeIdentity(workingCurve,apply=True,translate =False, rotate = False, scale=True)
	    
	    
    else:
	mc.setAttr(workingCurve+'.sx',baseMultiplier[0])
	mc.setAttr(workingCurve+'.sy',baseMultiplier[1])
	mc.setAttr(workingCurve+'.sz',baseMultiplier[2])
	
    
    
    workingCurve = mc.parent(workingCurve,world=True)
    mc.delete(group)
    
    "freeze for parent shaping """
    mc.makeIdentity(workingCurve,apply=True,translate =True, rotate = True, scale=True)
    shape = mc.listRelatives (workingCurve, f= True,shapes=True)
    mc.parent (shape,obj,add=True,shape=True)
    mc.delete(workingCurve)
    
    #>>>Put object back where it was
    

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def parentShapeInPlace2(obj,curve):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Way to parent shape an object's transform node in place
    
    REQUIRES:
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
    print workingCurve
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

    REQUIRES:
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
        
    orderedDictList = dictionary.returnDictionarySortedToList (colorVolumes,sortBy='values')
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

    REQUIRES:
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
        return setCurveColorByIndex(obj,colorIndex)     
            
def setCurveColorByIndex(obj,colorIndex):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Set the color of a curve(and subshapes) or shape by color index

    REQUIRES:
    obj(string) - object to affect
    color(string) - the color name
    
    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if search.returnObjectType(obj) == 'shape':
        attributes.doSetAttr((obj+'.overrideEnabled'),True)
        attributes.doSetAttr((obj+'.overrideColor'),colorIndex)
    else:
	shapes = mc.listRelatives (obj, shapes=True,fullPath = True)
	
	if shapes > 0:
	    for shape in shapes:
		attributes.doSetAttr((shape+'.overrideEnabled'),True)
		attributes.doSetAttr((shape+'.overrideColor'),colorIndex)
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
    
    REQUIRES:
    obj(string) - the object we'd like to startfrom
    
    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    nameBuffer = textCurveObj
    attributes.storeInfo(textCurveObj,'cgmObjectText',nameBuffer,True)
    updateTextCurveObject(textCurveObj)
    buffer = autoname.doNameObject(textCurveObj)
    return buffer

def createTextCurve(text,size=1,font='Arial'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Replacement for maya's textCurves utilizing a single tranform instead of a nested tranform setup
    
    REQUIRES:
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
    
    REQUIRES:
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
    
    return autoname.doNameObject(textCurve)
    
def updateTextCurveObject(textCurveObj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Updates/e a text curve object using the stored size, text and font information
    utilizing the original tranform
    
    REQUIRES:
    textCurveObj(string)
    
    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ get our current size"""
    shapes = mc.listRelatives(textCurveObj,shapes=True,fullPath=True)
    storedSize = float(mc.getAttr(textCurveObj+'.cgmObjectSize'))
    """parent scales """
    parents = search.returnAllParents(textCurveObj)
    scales = []
    scaleBuffer = mc.xform(textCurveObj,q=True, s=True,r=True)
    scales.append(sum(scaleBuffer)/len(scaleBuffer))
    
    if parents:       
        for p in parents:
            scaleBuffer = mc.xform(p,q=True, s=True,r=True)
            average = sum(scaleBuffer)
            scales.append(sum(scaleBuffer)/len(scaleBuffer))
        
    if shapes == None:
        size = storedSize
        
    else:
        print 'here'
        boundingBoxSize =  distance.returnAbsoluteSizeCurve(textCurveObj)
        print boundingBoxSize
        print scaleBuffer
        print storedSize
        if max(boundingBoxSize) != storedSize:
            print 'got here'
            if parents:
                print parents
                print 'parents'
                scaleBuffer = max(boundingBoxSize)
                for s in scales:
                    scaleBuffer /= s
                size = scaleBuffer
                attributes.storeInfo(textCurveObj,'cgmObjectSize',size)
            else:
                print 'am I here'
                size = max(boundingBoxSize)
                #size = max(boundingBoxSize) / (sum(scaleBuffer)/len(scaleBuffer))
                attributes.storeInfo(textCurveObj,'cgmObjectSize',size)
        else:
            'equal'
            size = storedSize
    
    
    """ delete current shapes"""
    if shapes:
      """first get the current color"""
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
    textCurveObj = autoname.doNameObject(textCurveObj)
    setCurveColorByIndex(textCurveObj,colorIndex)
    
    return textCurveObj
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utility Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def duplicateShape(shape):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Duplicates a shape

    REQUIRES:
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
    
    REQUIRES:
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
    print ('%s%s' % (crvName,' may be created with....'))
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
        print ('%s%s%s' % (shape,' = ',commandsReturn[0]))
    
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
    
    REQUIRES:
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

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def createControlCurve(desiredShape,size,direction='z+'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a curve in the desired shape and scales it
    
    REQUIRES:
    desiredShape(string) - see help(createCurve) for list
    size(float)
    direction(string)
    
    RETURNS:
    curve(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    directionDict = {'x+':[0,90,0],'x-':[0,-90,0],'y+':[0,-90,-90],'y-':[0,90,90],'z+':[0,0,0],'z-':[0,180,0]}
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
    
    REQUIRES:
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
    
    REQUIRES:
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
    
    REQUIRES:
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
    
    REQUIRES:
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
    
    REQUIRES:
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
    
    REQUIRES:
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
    
    REQUIRES:
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
    
    REQUIRES:
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
    
    REQUIRES:
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
        createdCurves.append(mc.curve( d = 3,p = [[6.123233995736766e-17, 6.123233995736766e-17, -1.0], [-0.12970357175844988, 6.123233995736766e-17, -1.0], [-0.39193445061832721, 5.8061999932152845e-17, -0.94822441821720149], [-0.72372651710916114, 4.4515488034364602e-17, -0.72699309001351275], [-0.94653407255330735, 2.422901301834318e-17, -0.39568981089424904], [-1.0258707475105489, 2.7409222470331639e-19, -0.0044762657264796682], [-0.9499258217289045, -2.3722328092379964e-17, 0.38741501809168771], [-0.73014393465873273, -4.4127018346960661e-17, 0.72064889856705805], [-0.39981607656719287, -5.7850562587972674e-17, 0.94477138434119112], [-0.0089524462188481854, -6.2815118031585638e-17, 1.0258487275730435], [0.38326664845234165, -5.8269015790615579e-17, 0.95160524375166344], [0.71745567272457933, -4.4900567133698444e-17, 0.73328190895464662], [0.94301981906954235, -2.4733854896015301e-17, 0.40393450443402906], [1.0257926240355661, -8.2224802280658007e-19, 0.013428329268145904], [0.95329565023223506, 2.3213807591667487e-17, -0.37911024807854549], [0.73630406893916978, 4.3735296548626863e-17, -0.71425159611860467], [0.40842355504360439, 5.7634315397646268e-17, -0.94123979971651461], [0.14713622371352122, 6.1084406035020742e-17, -0.99758405570569553], [0.017452406437283526, 6.1223013975406661e-17, -0.99984769515639127]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 16.0, 16.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.99796527511422117, 0.0, -1.4396392372072158e-18], [-0.9499258217289045, -0.38741501809168771, 6.2301086541812688e-17], [-0.73014393465873273, -0.72064889856705805, 1.158891816250207e-16], [-0.39981607656719287, -0.94477138434119112, 1.5193082619254202e-16], [-0.0089524462188481854, -1.0258487275730435, 1.6496905739521686e-16], [0.38326664845234165, -0.95160524375166344, 1.5302979460281064e-16], [0.71745567272457933, -0.73328190895464662, 1.1792072463880884e-16], [0.94301981906954235, -0.40393450443402906, 6.4957622556626983e-17], [0.99788715163923836, 0.0, 1.439639237207216e-18]],k = (5.0, 5.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 11.0, 11.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-2.2303244447884462e-16, 0.0, 0.99796527511422117], [-1.4862481725206763e-16, -0.38741501809168771, 0.9499258217289045], [-4.6235339884685485e-17, -0.72064889856705805, 0.73014393465873273], [6.3153823428503611e-17, -0.94477138434119112, 0.39981607656719287], [1.6298121501144013e-16, -1.0258487275730435, 0.0089524462188481854], [2.3813208613935171e-16, -0.95160524375166344, -0.38326664845234165], [2.7722788604016059e-16, -0.73328190895464662, -0.71745567272457933], [2.7435008571839802e-16, -0.40393450443402906, -0.94301981906954235], [2.2301509758270671e-16, 0.0, -0.99788715163923836]],k = (5.0, 5.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 11.0, 11.0)))
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
        createBuffer = mc.curve( d = 1,p = [(0,2,0),(1,0,-1),(-1,0,-1),(0,2,0),(-1,0,1),(1,0,1),(0,2,0),(1,0,-1),(1,0,1),(-1,0,1),(-1,0,-1)],k = [0,1,2,3,4,5,6,7,8,9,10]) 
        return createBuffer
    #>>> Crosses #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'cross':
        createBuffer = mc.curve( d = 1,p = [[0.20000000000000001, 0.0, -0.20000000000000001], [0.20000000000000001, 0.0, -1.0], [-0.20000000000000001, 0.0, -1.0], [-0.20000000000000001, 0.0, -0.20000000000000001], [-1.0, 0.0, -0.20000000000000001], [-1.0, 0.0, 0.20000000000000001], [-0.20000000000000001, 0.0, 0.20000000000000001], [-0.20000000000000001, 0.0, 1.0], [0.20000000000000001, 0.0, 1.0], [0.20000000000000001, 0.0, 0.20000000000000001], [1.0, 0.0, 0.20000000000000001], [1.0, 0.0, -0.20000000000000001], [0.20000000000000001, 0.0, -0.20000000000000001]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0))
        return createBuffer   
    elif desiredShape == 'fatCross':
        createBuffer = mc.curve( d = 1,p = [[1.0, 0.0, 0.5], [1.0, 0.0, -0.5], [0.5, 0.0, -0.5], [0.5, 0.0, -1.0], [-0.5, 0.0, -1.0], [-0.5, 0.0, -0.5], [-1.0, 0.0, -0.5], [-1.0, 0.0, 0.5], [-0.5, 0.0, 0.5], [-0.5, 0.0, 1.0], [0.5, 0.0, 1.0], [0.5, 0.0, 0.5], [1.0, 0.0, 0.5]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0))
        return createBuffer
    #>>> Arrows #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'arrowSingle':
        createBuffer = mc.curve( d = 1,p = [[-1.2254123610044656e-16, 0.0, 1.000625128696409], [0.75046884652230672, 0.0, 9.1905927075334917e-17], [0.25015628217410224, 0.0, 3.0635309025111639e-17], [0.25015628217410235, 0.0, -0.75046884652230672], [-0.25015628217410213, 0.0, -0.75046884652230672], [-0.25015628217410224, 0.0, -3.0635309025111639e-17], [-0.75046884652230672, 0.0, -9.1905927075334917e-17], [-1.2254123610044656e-16, 0.0, 1.000625128696409]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0))
        return createBuffer
    elif desiredShape == 'arrowSingleFat':
        createBuffer = mc.curve( d = 1,p = [[-1.2124003311558797e-16, 0.0, 0.98999999999999999], [0.66000000000000003, 0.0, 8.0826688743725305e-17], [0.33000000000000002, 0.0, 4.0413344371862653e-17], [0.33000000000000007, 0.0, -0.66000000000000003], [-0.32999999999999996, 0.0, -0.66000000000000003], [-0.33000000000000002, 0.0, -4.0413344371862653e-17], [-0.66000000000000003, 0.0, -8.0826688743725305e-17], [-1.2124003311558797e-16, 0.0, 0.98999999999999999]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0))
        return createBuffer
    elif desiredShape == 'arrowDouble':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.0, -0.99992370289862254], [-0.4285387298136954, 0.0, -0.4285387298136954], [-0.1428462432712318, 0.0, -0.4285387298136954], [-0.1428462432712318, 0.0, 0.4285387298136954], [-0.4285387298136954, 0.0, 0.4285387298136954], [0.0, 0.0, 0.99992370289862254], [0.4285387298136954, 0.0, 0.4285387298136954], [0.1428462432712318, 0.0, 0.4285387298136954], [0.1428462432712318, 0.0, -0.4285387298136954], [0.4285387298136954, 0.0, -0.4285387298136954], [0.0, 0.0, -0.99992370289862254]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0))
        return createBuffer
    elif desiredShape == 'arrowDoubleFat':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.0, -0.99889063775106279], [-0.48834653401163075, 0.0, -0.26637083673361678], [-0.24417326700581538, 0.0, -0.26637083673361678], [-0.24417326700581538, 0.0, 0.26637083673361678], [-0.48834653401163075, 0.0, 0.26637083673361678], [0.0, 0.0, 0.99889063775106279], [0.48834653401163075, 0.0, 0.26637083673361678], [0.24417326700581538, 0.0, 0.26637083673361678], [0.24417326700581538, 0.0, -0.26637083673361678], [0.48834653401163075, 0.0, -0.26637083673361678], [0.0, 0.0, -0.99889063775106279]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0))
        return createBuffer
    elif desiredShape == 'arrow4':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.0, -0.98999999999999999], [-0.2475, 0.0, -0.66000000000000003], [-0.082500000000000004, 0.0, -0.66000000000000003], [-0.082500000000000004, 0.0, -0.082500000000000004], [-0.66000000000000003, 0.0, -0.082500000000000004], [-0.66000000000000003, 0.0, -0.2475], [-0.98999999999999999, 0.0, 0.0], [-0.66000000000000003, 0.0, 0.2475], [-0.66000000000000003, 0.0, 0.082500000000000004], [-0.082500000000000004, 0.0, 0.082500000000000004], [-0.082500000000000004, 0.0, 0.66000000000000003], [-0.2475, 0.0, 0.66000000000000003], [0.0, 0.0, 0.98999999999999999], [0.2475, 0.0, 0.66000000000000003], [0.082500000000000004, 0.0, 0.66000000000000003], [0.082500000000000004, 0.0, 0.082500000000000004], [0.66000000000000003, 0.0, 0.082500000000000004], [0.66000000000000003, 0.0, 0.2475], [0.98999999999999999, 0.0, 0.0], [0.66000000000000003, 0.0, -0.2475], [0.66000000000000003, 0.0, -0.082500000000000004], [0.082500000000000004, 0.0, -0.082500000000000004], [0.082500000000000004, 0.0, -0.66000000000000003], [0.2475, 0.0, -0.66000000000000003], [0.0, 0.0, -0.98999999999999999]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0))
        return createBuffer
    elif desiredShape == 'arrow4Fat':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.0, -0.99407037608705695], [-0.29754487447503747, 0.0, -0.54775306437450089], [-0.14877243723751873, 0.0, -0.54775306437450089], [-0.14877243723751873, 0.0, -0.14877243723751873], [-0.54775306437450089, 0.0, -0.14877243723751873], [-0.54775306437450089, 0.0, -0.29754487447503747], [-0.99407037608705695, 0.0, 0.0], [-0.54775306437450089, 0.0, 0.29754487447503747], [-0.54775306437450089, 0.0, 0.14877243723751873], [-0.14877243723751873, 0.0, 0.14877243723751873], [-0.14877243723751873, 0.0, 0.54775306437450089], [-0.29754487447503747, 0.0, 0.54775306437450089], [0.0, 0.0, 0.99407037608705695], [0.29754487447503747, 0.0, 0.54775306437450089], [0.14877243723751873, 0.0, 0.54775306437450089], [0.14877243723751873, 0.0, 0.14877243723751873], [0.54775306437450089, 0.0, 0.14877243723751873], [0.54775306437450089, 0.0, 0.29754487447503747], [0.99407037608705695, 0.0, 0.0], [0.54775306437450089, 0.0, -0.29754487447503747], [0.54775306437450089, 0.0, -0.14877243723751873], [0.14877243723751873, 0.0, -0.14877243723751873], [0.14877243723751873, 0.0, -0.54775306437450089], [0.29754487447503747, 0.0, -0.54775306437450089], [0.0, 0.0, -0.99407037608705695]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0))
        return createBuffer
    elif desiredShape == 'arrow8':
        createBuffer = mc.curve( d = 1,p = [[-0.94874999999999998, 0.0, 0.0], [-0.70125000000000004, 0.0, 0.18562500000000001], [-0.70125000000000004, 0.0, 0.061874999999999999], [-0.19048300000000001, 0.0, 0.078900499999999998], [-0.53961099999999995, 0.0, 0.45210650000000002], [-0.62711550000000005, 0.0, 0.36460200000000004], [-0.67086749999999995, 0.0, 0.67086749999999995], [-0.36460200000000004, 0.0, 0.62711550000000005], [-0.45210650000000002, 0.0, 0.53961099999999995], [-0.078900499999999998, 0.0, 0.19048300000000001], [-0.061874999999999999, 0.0, 0.70125000000000004], [-0.18562500000000001, 0.0, 0.70125000000000004], [0.0, 0.0, 0.94874999999999998], [0.18562500000000001, 0.0, 0.70125000000000004], [0.061874999999999999, 0.0, 0.70125000000000004], [0.078900499999999998, 0.0, 0.19048300000000001], [0.45210650000000002, 0.0, 0.53961099999999995], [0.36460200000000004, 0.0, 0.62711550000000005], [0.67086749999999995, 0.0, 0.67086749999999995], [0.62711550000000005, 0.0, 0.36460200000000004], [0.53961099999999995, 0.0, 0.45210650000000002], [0.19048300000000001, 0.0, 0.078900499999999998], [0.70125000000000004, 0.0, 0.061874999999999999], [0.70125000000000004, 0.0, 0.18562500000000001], [0.94874999999999998, 0.0, 0.0], [0.70125000000000004, 0.0, -0.18562500000000001], [0.70125000000000004, 0.0, -0.061874999999999999], [0.19048300000000001, 0.0, -0.078900499999999998], [0.53961099999999995, 0.0, -0.45210650000000002], [0.62711550000000005, 0.0, -0.36460200000000004], [0.67086749999999995, 0.0, -0.67086749999999995], [0.36460200000000004, 0.0, -0.62711550000000005], [0.45210650000000002, 0.0, -0.53961099999999995], [0.078900499999999998, 0.0, -0.19048300000000001], [0.061874999999999999, 0.0, -0.70125000000000004], [0.18562500000000001, 0.0, -0.70125000000000004], [0.0, 0.0, -0.94874999999999998], [-0.18562500000000001, 0.0, -0.70125000000000004], [-0.061874999999999999, 0.0, -0.70125000000000004], [-0.078900499999999998, 0.0, -0.19048300000000001], [-0.45210650000000002, 0.0, -0.53961099999999995], [-0.36460200000000004, 0.0, -0.62711550000000005], [-0.67086749999999995, 0.0, -0.67086749999999995], [-0.62711550000000005, 0.0, -0.36460200000000004], [-0.53961099999999995, 0.0, -0.45210650000000002], [-0.19048300000000001, 0.0, -0.078900499999999998], [-0.70125000000000004, 0.0, -0.061874999999999999], [-0.70125000000000004, 0.0, -0.18562500000000001], [-0.94874999999999998, 0.0, 0.0]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0))
        return createBuffer
    elif desiredShape == 'arrowsOnBall':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.35000000000000003, -1.0015670000000001], [-0.33663800000000005, 0.67788599999999999, -0.75117500000000004], [-0.095983499999999999, 0.67788599999999999, -0.75117500000000004], [-0.095983499999999999, 0.85045800000000005, -0.50078299999999998], [-0.095983499999999999, 0.95400099999999999, -0.098765599999999995], [-0.50078299999999998, 0.85045800000000005, -0.098765599999999995], [-0.75117500000000004, 0.67788599999999999, -0.098765599999999995], [-0.75117500000000004, 0.67788599999999999, -0.33663800000000005], [-1.0015670000000001, 0.35000000000000003, 0.0], [-0.75117500000000004, 0.67788599999999999, 0.33663800000000005], [-0.75117500000000004, 0.67788599999999999, 0.098765599999999995], [-0.50078299999999998, 0.85045800000000005, 0.098765599999999995], [-0.095983499999999999, 0.95400099999999999, 0.098765599999999995], [-0.095983499999999999, 0.85045800000000005, 0.50078299999999998], [-0.095983499999999999, 0.67788599999999999, 0.75117500000000004], [-0.33663800000000005, 0.67788599999999999, 0.75117500000000004], [0.0, 0.35000000000000003, 1.0015670000000001], [0.33663800000000005, 0.67788599999999999, 0.75117500000000004], [0.095983499999999999, 0.67788599999999999, 0.75117500000000004], [0.095983499999999999, 0.85045800000000005, 0.50078299999999998], [0.095983499999999999, 0.95400099999999999, 0.098765599999999995], [0.50078299999999998, 0.85045800000000005, 0.098765599999999995], [0.75117500000000004, 0.67788599999999999, 0.098765599999999995], [0.75117500000000004, 0.67788599999999999, 0.33663800000000005], [1.0015670000000001, 0.35000000000000003, 0.0], [0.75117500000000004, 0.67788599999999999, -0.33663800000000005], [0.75117500000000004, 0.67788599999999999, -0.098765599999999995], [0.50078299999999998, 0.85045800000000005, -0.098765599999999995], [0.095983499999999999, 0.95400099999999999, -0.098765599999999995], [0.095983499999999999, 0.85045800000000005, -0.50078299999999998], [0.095983499999999999, 0.67788599999999999, -0.75117500000000004], [0.33663800000000005, 0.67788599999999999, -0.75117500000000004], [0.0, 0.35000000000000003, -1.0015670000000001]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0))
        return createBuffer
    #>>> Nails #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'nail':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.0, 0.0], [-1.1102230246251565e-16, 0.0, 0.5], [0.17677674999999987, 0.0, 0.57322325000000007], [0.24999999999999983, 0.0, 0.75], [0.17677674999999979, 0.0, 0.92677675000000026], [-2.2204460492503131e-16, 0.0, 1.0], [-0.17677675000000023, 0.0, 0.92677675000000026], [-0.25000000000000017, 0.0, 0.75], [-0.17677675000000015, 0.0, 0.57322324999999996], [-1.1102230246251565e-16, 0.0, 0.5], [0.17677674999999987, 0.0, 0.57322325000000007], [-0.17677675000000023, 0.0, 0.92677675000000026], [-2.2204460492503131e-16, 0.0, 1.0], [0.17677674999999979, 0.0, 0.92677675000000026], [-0.17677675000000015, 0.0, 0.57322324999999996]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0))
        return createBuffer
    elif desiredShape == 'nail2':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.0, 0.0], [-1.1102230246251565e-16, 0.0, 0.5], [-0.17677675000000015, 0.0, 0.57322324999999996], [-0.25000000000000017, 0.0, 0.75], [-0.17677675000000023, 0.0, 0.92677675000000026], [-2.2204460492503131e-16, 0.0, 1.0], [0.17677674999999979, 0.0, 0.92677675000000026], [0.24999999999999983, 0.0, 0.75], [0.17677674999999987, 0.0, 0.57322325000000007], [-1.1102230246251565e-16, 0.0, 0.5], [0.17677674999999987, 0.0, 0.57322325000000007], [-0.17677675000000023, 0.0, 0.92677675000000026], [-0.25000000000000017, 0.0, 0.75], [-0.17677675000000015, 0.0, 0.57322324999999996], [0.17677674999999979, 0.0, 0.92677675000000026], [0.24999999999999983, 0.0, 0.75], [0.17677674999999987, 0.0, 0.57322325000000007], [-1.1102230246251565e-16, 0.0, 0.5], [0.0, 0.0, 0.0], [1.1102230246251565e-16, 0.0, -0.5], [-0.17677674999999987, 0.0, -0.57322325000000007], [-0.24999999999999983, 0.0, -0.75], [-0.17677674999999979, 0.0, -0.92677675000000026], [2.2204460492503131e-16, 0.0, -1.0], [0.17677675000000023, 0.0, -0.92677675000000026], [0.25000000000000017, 0.0, -0.75], [0.17677675000000015, 0.0, -0.57322324999999996], [1.1102230246251565e-16, 0.0, -0.5], [0.17677675000000015, 0.0, -0.57322324999999996], [-0.17677674999999979, 0.0, -0.92677675000000026], [-0.24999999999999983, 0.0, -0.75], [-0.17677674999999987, 0.0, -0.57322325000000007], [0.17677675000000023, 0.0, -0.92677675000000026]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0))
        return createBuffer
    elif desiredShape == 'nail4':
        createBuffer = mc.curve( d = 1,p = [[-0.5, 0.0, 0.0], [-0.57322324999999996, 0.0, -0.17677675000000001], [-0.75, 0.0, -0.25], [-0.92677675000000015, 0.0, -0.17677675000000001], [-1.0, 0.0, 0.0], [-0.92677675000000015, 0.0, 0.17677675000000001], [-0.75, 0.0, 0.25], [-0.57322324999999996, 0.0, 0.17677675000000001], [-0.5, 0.0, 0.0], [-0.57322324999999996, 0.0, 0.17677675000000001], [-0.92677675000000015, 0.0, -0.17677675000000001], [-1.0, 0.0, 0.0], [-0.92677675000000015, 0.0, 0.17677675000000001], [-0.57322324999999996, 0.0, -0.17677675000000001], [-0.5, 0.0, 0.0], [0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.57322324999999996, 0.0, 0.17677675000000001], [0.75, 0.0, 0.25], [0.92677675000000015, 0.0, 0.17677675000000001], [1.0, 0.0, 0.0], [0.92677675000000015, 0.0, -0.17677675000000001], [0.75, 0.0, -0.25], [0.57322324999999996, 0.0, -0.17677675000000001], [0.5, 0.0, 0.0], [0.57322324999999996, 0.0, 0.17677675000000001], [0.92677675000000015, 0.0, -0.17677675000000001], [1.0, 0.0, 0.0], [0.92677675000000015, 0.0, 0.17677675000000001], [0.57322324999999996, 0.0, -0.17677675000000001], [0.5, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.5], [-0.17677675000000001, 0.0, 0.57322324999999996], [-0.25, 0.0, 0.75], [-0.17677675000000001, 0.0, 0.92677675000000015], [0.0, 0.0, 1.0], [0.17677675000000001, 0.0, 0.92677675000000015], [0.25, 0.0, 0.75], [0.17677675000000001, 0.0, 0.57322324999999996], [0.0, 0.0, 0.5], [0.17677675000000001, 0.0, 0.57322324999999996], [-0.17677675000000001, 0.0, 0.92677675000000015], [0.0, 0.0, 1.0], [0.17677675000000001, 0.0, 0.92677675000000015], [-0.17677675000000001, 0.0, 0.57322324999999996], [0.0, 0.0, 0.5], [0.0, 0.0, -0.5], [-0.17677675000000001, 0.0, -0.57322324999999996], [-0.25, 0.0, -0.75], [-0.17677675000000001, 0.0, -0.92677675000000015], [0.0, 0.0, -1.0], [0.17677675000000001, 0.0, -0.92677675000000015], [0.25, 0.0, -0.75], [0.17677675000000001, 0.0, -0.57322324999999996], [0.0, 0.0, -0.5], [0.17677675000000001, 0.0, -0.57322324999999996], [-0.17677675000000001, 0.0, -0.92677675000000015], [0.0, 0.0, -1.0], [0.17677675000000001, 0.0, -0.92677675000000015], [-0.17677675000000001, 0.0, -0.57322324999999996]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0))
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
        createBuffer = mc.curve( d = 1,p = [[-0.035617531823693156, 0.0, -0.49068614205176153], [0.17154959710832532, 0.0, -0.40463188097194891], [0.22573195842464958, 0.0, -0.27077086790018573], [0.18111103531897801, 0.0, 0.012888952182598914], [0.37871672604034379, 0.0, 0.24236535720190844], [0.40421389460208423, 0.0, 0.51008913959068625], [0.34047097319773317, 0.0, 0.73319199887379261], [0.16836245103810779, 0.0, 0.8829909376032079], [-0.057927993376528937, 0.0, 1.0232253646927805], [-0.24278509981702454, 0.0, 1.0136643655434407], [-0.28740426667744456, 0.0, 0.74275475426838389], [-0.25234609896636434, 0.0, 0.28061286628977061], [-0.15991754574611652, 0.0, 0.047948129734698794], [-0.23322234442243323, 0.0, -0.1751547295484075], [-0.20453759072916231, 0.0, -0.36957371326086863], [-0.035617531823693156, 0.0, -0.49068614205176153]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0))
        return createBuffer
    #>>> Special #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'gear':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[0.36589275643190788, -2.0408077971202743e-06, 0.0], [0.36589275643190788, 0.066658905066453847, 0.0], [0.34805936158046424, 0.12914272554224085, 0.0], [0.31691745092461332, 0.18297352095965108, 0.0], [0.32982339037080916, 0.19042448106665821, 0.0], [0.42016612804034642, 0.24258187240882675, 0.0], [0.43307206748654231, 0.25003283251583436, 0.0], [0.38917102648517926, 0.3259051684616634, 0.0], [0.32590598478478217, 0.38917021016206016, 0.0], [0.25003283251583447, 0.4330720674865422, 0.0], [0.24258141890051846, 0.42016612804034631, 0.0], [0.1904208529593738, 0.32982339037080882, 0.0], [0.18296943934405777, 0.31691745092461299, 0.0], [0.12914354186535973, 0.34805936158046391, 0.0], [0.066655639773978939, 0.365892756431908, 0.0], [-2.0408077968871564e-06, 0.365892756431908, 0.0], [-2.0408077968871564e-06, 0.38079340682265889, 0.0], [-2.0408077968871564e-06, 0.48509930062986206, 0.0], [-2.0408077968871564e-06, 0.49999995102061295, 0.0], [-0.091089007040231817, 0.49999995102061295, 0.0], [-0.17647967055027494, 0.47562944063450113, 0.0], [-0.25003283251583469, 0.4330720674865422, 0.0], [-0.24258178170716541, 0.42016612804034631, 0.0], [-0.19042375544520174, 0.32982339037080882, 0.0], [-0.18297270463653242, 0.31691745092461299, 0.0], [-0.23849328890968227, 0.28479023826447297, 0.0], [-0.28479023826447353, 0.23849328890968163, 0.0], [-0.3169166346014945, 0.18296943934405777, 0.0], [-0.3298225740476905, 0.1904208529593738, 0.0], [-0.42016531171722776, 0.24258141890051832, 0.0], [-0.43307125116342365, 0.25003283251583436, 0.0], [-0.47562944063450124, 0.17647967055027458, 0.0], [-0.4999999510206129, 0.091084925424638155, 0.0], [-0.4999999510206129, -2.0408077971202743e-06, 0.0], [-0.48509920992820016, -2.0408077971202743e-06, 0.0], [-0.3807926812012018, -2.0408077971202743e-06, 0.0], [-0.36589194010878912, -2.0408077971202743e-06, 0.0], [-0.36589194010878912, -0.066662986682047162, 0.0], [-0.34805936158046419, -0.12914680715783416, 0.0], [-0.3169166346014945, -0.182973520959652, 0.0], [-0.3298225740476905, -0.19042448106665916, 0.0], [-0.42016531171722776, -0.2425818724088277, 0.0], [-0.43307125116342365, -0.25003283251583486, 0.0], [-0.38917021016206038, -0.32590925007725718, 0.0], [-0.32590925007725674, -0.38916694486958558, 0.0], [-0.25003609780830954, -0.43307614910213643, 0.0], [-0.25003573500166265, -0.43307614910213643, 0.0], [-0.25003319532248164, -0.43307614910213643, 0.0], [-0.25003283251583469, -0.43307614910213643, 0.0], [-0.24258178170716541, -0.42016975614763213, 0.0], [-0.19042375544520174, -0.32982384387911723, 0.0], [-0.18297270463653242, -0.31691745092461343, 0.0], [-0.12914680715783453, -0.34806344319605814, 0.0], [-0.066658905066453972, -0.36589683804750223, 0.0], [-2.0408077968871564e-06, -0.36589683804750223, 0.0], [-2.0408077968871564e-06, -0.38079703492994471, 0.0], [-2.0408077968871564e-06, -0.48509975413817047, 0.0], [-2.0408077968871564e-06, -0.49999995102061295, 0.0], [0.09108574174775691, -0.49999995102061295, 0.0], [0.17647640525780015, -0.47562944063450163, 0.0], [0.25003283251583447, -0.43307614910213643, 0.0], [0.24258141890051846, -0.42016975614763213, 0.0], [0.1904208529593738, -0.32982384387911723, 0.0], [0.18296943934405777, -0.31691745092461343, 0.0], [0.23849410523280098, -0.28479023826447342, 0.0], [0.28478697297199862, -0.23849737052527589, 0.0], [0.31691745092461332, -0.182973520959652, 0.0], [0.32982339037080916, -0.19042448106665916, 0.0], [0.42016612804034642, -0.2425818724088277, 0.0], [0.43307206748654231, -0.25003283251583486, 0.0], [0.47563025695762001, -0.17648375216586881, 0.0], [0.49999995102061284, -0.091089007040231457, 0.0], [0.49999995102061284, -2.0408077971202743e-06, 0.0], [0.48509930062986167, -2.0408077971202743e-06, 0.0], [0.38079340682265889, -2.0408077971202743e-06, 0.0], [0.36589275643190788, -2.0408077971202743e-06, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0, 8.0, 8.0, 8.0, 9.0, 9.0, 9.0, 10.0, 10.0, 10.0, 11.0, 11.0, 11.0, 12.0, 12.0, 12.0, 13.0, 13.0, 13.0, 14.0, 14.0, 14.0, 15.0, 15.0, 15.0, 16.0, 16.0, 16.0, 17.0, 17.0, 17.0, 18.0, 18.0, 18.0, 19.0, 19.0, 19.0, 20.0, 20.0, 20.0, 21.0, 21.0, 21.0, 22.0, 22.0, 22.0, 23.0, 23.0, 23.0, 24.0, 24.0, 24.0, 25.0, 25.0, 25.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-2.0408077968871564e-06, -0.21854398453452986, 0.0], [-0.1206962302328989, -0.21854398453452986, 0.0], [-0.21854316821141118, -0.12069704655601754, 0.0], [-0.21854316821141118, -2.0408077971202743e-06, 0.0], [-0.21854316821141118, 0.12069296494042377, 0.0], [-0.1206962302328989, 0.21853990291893702, 0.0], [-2.0408077968871564e-06, 0.21853990291893702, 0.0], [0.12069704655601754, 0.21853990291893702, 0.0], [0.21854398453453011, 0.12069296494042377, 0.0], [0.21854398453453011, -2.0408077971202743e-06, 0.0], [0.21854398453453011, -0.12069704655601754, 0.0], [0.12069704655601754, -0.21854398453452986, 0.0], [-2.0408077968871564e-06, -0.21854398453452986, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0)))
        return combineCurves(createdCurves)          
    elif desiredShape == 'dumcgmell':
        createBuffer = mc.curve( d = 1,p = [[-0.99849159389068964, 0.0, 0.021042779369566156], [-0.92904412938768721, -0.16766137908274195, 0.021042779369566156], [-0.76138275030494529, -0.23710884358574422, 0.021042779369566156], [-0.59372137122220348, -0.16766137908274195, 0.021042779369566156], [-0.52510409775306377, -0.0020051263364880313, 0.021042779369566156], [0.52431938531169364, 0.0, 0.021042779369566156], [0.59372137122220348, -0.16766137908274195, 0.021042779369566156], [0.76138275030494529, -0.23710884358574422, 0.021042779369566156], [0.92904412938768721, -0.16766137908274195, 0.021042779369566156], [0.99849159389068964, 0.0, 0.021042779369566156], [0.92904412938768721, 0.16766137908274195, 0.021042779369566156], [0.76138275030494529, 0.23710884358574422, 0.021042779369566156], [0.59372137122220348, 0.16766137908274195, 0.021042779369566156], [0.52431938531169364, 0.0, 0.021042779369566156], [-0.52510409775306377, -0.0020051263364880313, 0.021042779369566156], [-0.59372137122220348, 0.16766137908274195, 0.021042779369566156], [-0.76138275030494529, 0.23710884358574422, 0.021042779369566156], [-0.92904412938768721, 0.16766137908274195, 0.021042779369566156], [-0.99849159389068964, 0.0, 0.021042779369566156]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0))
        return createBuffer  
    elif desiredShape == 'locator':
        createBuffer = mc.curve( d = 1,p = [[0.0, 0.99266615978157735, 0.0], [0.0, -0.99266615978157735, 0.0], [0.0, 0.0, 0.0], [-0.99266615978157735, 0.0, 0.0], [0.99266615978157735, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.99266615978157735], [0.0, 0.0, -0.99266615978157735]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0))
        return createBuffer         
    elif desiredShape == 'arrowsLocator':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[-0.71034804226541659, 1.444130000945939e-16, 0.37639989243615296], [-0.75185548636799693, 1.5744710508753383e-16, 0.41790733653873335], [-0.79336293047057771, 1.7048121008047389e-16, 0.45941478064131408], [-0.83487037457315849, 1.8351531507341399e-16, 0.50092222474389481], [-0.89052839954470242, 1.7477649054610858e-16, 0.44526419977235115], [-0.94618642451624635, 1.6603766601880319e-16, 0.38960617480080723], [-1.0018444494877898, 1.5729884149149766e-16, 0.33394814982926291], [-1.0018444494877898, 2.0973178865533029e-16, 0.55658024971543862], [-1.0018444494877903, 2.6216473581916287e-16, 0.77921234960161434], [-1.0018444494877898, 3.1459768298299532e-16, 1.0018444494877894], [-0.77921234960161467, 2.971200339283846e-16, 1.0018444494877898], [-0.55658024971543907, 2.7964238487377368e-16, 1.0018444494877898], [-0.33394814982926363, 2.6216473581916287e-16, 1.0018444494877898], [-0.38960617480080734, 2.5342591129185741e-16, 0.94618642451624579], [-0.44526419977235093, 2.446870867645519e-16, 0.89052839954470164], [-0.50092222474389514, 2.3594826223724659e-16, 0.83487037457315805], [-0.45772982604933232, 2.2238505034468735e-16, 0.79167797587859545], [-0.41453742735476956, 2.0882183845212819e-16, 0.74848557718403264], [-0.38172203677546457, 6.1993002843385494e-17, 0.70423931712785359], [-0.26481424742794457, 9.6559646198364555e-17, 0.76716375552260285], [-0.0031783262100260785, 1.6001941806647711e-16, 0.83567594934909839], [0.25845759500789239, 1.9745701588398112e-16, 0.76880833547598626], [0.37265034682111103, 1.3715897067272084e-16, 0.70659849665037444], [0.41540763946203901, 1.4387226094564649e-16, 0.74935578929130242], [0.45816493210296694, 1.5058555121857211e-16, 0.79211308193223051], [0.50092222474389492, 1.5729884149149773e-16, 0.83487037457315838], [0.44526419977235093, 1.747764905461086e-16, 0.89052839954470231], [0.38960617480080706, 1.9225413960071945e-16, 0.94618642451624613], [0.33394814982926307, 2.0973178865533029e-16, 1.0018444494877898], [0.55658024971543874, 1.9225413960071945e-16, 1.0018444494877898], [0.77921234960161434, 1.7477649054610858e-16, 1.0018444494877903], [1.0018444494877896, 1.5729884149149769e-16, 1.0018444494877898], [1.0018444494877898, 1.0486589432766514e-16, 0.77921234960161467], [1.0018444494877898, 5.2432947163832572e-17, 0.55658024971543907], [1.0018444494877898, 3.8746300180516809e-32, 0.33394814982926369], [0.94618642451624613, 1.747764905461088e-17, 0.3896061748008075], [0.89052839954470231, 3.4955298109221711e-17, 0.44526419977235138], [0.83487037457315805, 5.2432947163832572e-17, 0.50092222474389492], [0.79203060492095201, 4.5706707237564665e-17, 0.45808245509168877], [0.74919083526874586, 3.8980467311296777e-17, 0.41524268543948262], [0.70824785987373673, 2.0806017849916152e-16, 0.37418079886870681], [0.76863466079818266, 1.9755408097015749e-16, 0.25913624873453944], [0.83460199676406488, 1.6075046072444915e-16, 0.0016988602732966463], [0.76949960568300624, 9.8753133175290541e-17, -0.25573852818794651], [0.70869401511251184, -1.4389360498274727e-16, -0.37474586528324888], [0.75075280159939417, -1.5710084167963618e-16, -0.41680465177013093], [0.79281158808627628, -1.703080783765251e-16, -0.45886343825701298], [0.83487037457315827, -1.8351531507341406e-16, -0.50092222474389492], [0.89052839954470231, -1.747764905461086e-16, -0.44526419977235138], [0.94618642451624613, -1.6603766601880324e-16, -0.3896061748008075], [1.0018444494877898, -1.5729884149149776e-16, -0.33394814982926352], [1.0018444494877898, -2.0973178865533034e-16, -0.55658024971543896], [1.0018444494877898, -2.6216473581916297e-16, -0.77921234960161467], [1.0018444494877898, -3.1459768298299532e-16, -1.0018444494877894], [0.77921234960161467, -2.971200339283846e-16, -1.0018444494877898], [0.55658024971543907, -2.7964238487377368e-16, -1.0018444494877898], [0.33394814982926363, -2.6216473581916287e-16, -1.0018444494877898], [0.38960617480080734, -2.5342591129185741e-16, -0.94618642451624579], [0.44526419977235038, -2.4468708676455185e-16, -0.8905283995447012], [0.50092222474389514, -2.3594826223724659e-16, -0.83487037457315805], [0.45715292811589109, -2.2220389372574211e-16, -0.79110107794515416], [0.41338363148788737, -2.0845952521423771e-16, -0.74733178131715039], [0.3712329255875696, -6.5075646777795373e-17, -0.70978759552297921], [0.25692527558551659, -9.8467201032597699e-17, -0.76919879718237927], [-0.0013560887064098001, -1.6072603892040224e-16, -0.83481771441419972], [-0.25963745299833596, -1.9762570998075685e-16, -0.7685061049403874], [-0.37232195974284721, -1.3710741086520974e-16, -0.70627010957211067], [-0.41518871474319652, -1.4383788774063903e-16, -0.74913686457245987], [-0.45805546974354572, -1.5056836461606837e-16, -0.79200361957280918], [-0.50092222474389492, -1.5729884149149773e-16, -0.83487037457315838], [-0.44526419977235093, -1.747764905461086e-16, -0.89052839954470231], [-0.38960617480080706, -1.9225413960071945e-16, -0.94618642451624613], [-0.33394814982926307, -2.0973178865533029e-16, -1.0018444494877898], [-0.55658024971543874, -1.9225413960071945e-16, -1.0018444494877898], [-0.77921234960161434, -1.7477649054610858e-16, -1.0018444494877903], [-1.0018444494877896, -1.5729884149149769e-16, -1.0018444494877898], [-1.0018444494877898, -1.0486589432766519e-16, -0.77921234960161467], [-1.0018444494877898, -5.2432947163832572e-17, -0.55658024971543907], [-1.0018444494877898, -3.8746300180516815e-32, -0.33394814982926369], [-0.94618642451624613, -1.747764905461088e-17, -0.3896061748008075], [-0.89052839954470231, -3.4955298109221711e-17, -0.44526419977235138], [-0.83487037457315805, -5.2432947163832572e-17, -0.50092222474389492], [-0.7924173445961511, -4.5767428942315047e-17, -0.45846919476688786], [-0.7499643146191437, -3.9101910720797504e-17, -0.41601616478988057], [-0.70751128464213653, -3.2436392499279979e-17, -0.3735631348128734], [-0.76860559236731751, -1.9757029367260258e-16, -0.25924966340546224], [-0.83517618056509113, -1.6045196064212086e-16, 0.00042826386489417854], [-0.76838565165830874, -9.7699478325664099e-17, 0.26010619113525046], [-0.70756863740377807, -6.383430593347148e-17, 0.37547201684070014]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.54337396735079224, -0.23613700130893922, 0.54337396735079224], [-0.58488141145337269, -0.23613700130893661, 0.5848814114533728], [-0.62638885555595336, -0.236137001308934, 0.62638885555595347], [-0.66789629965853414, -0.23613700130893139, 0.66789629965853425], [-0.66789629965853681, -0.31484933507858914, 0.66789629965853692], [-0.66789629965853925, -0.39356166884824689, 0.66789629965853925], [-0.66789629965854147, -0.4722740026179047, 0.66789629965854147], [-0.77921234960162422, -0.31484933507858215, 0.77921234960162433], [-0.89052839954470731, -0.15742466753925963, 0.89052839954470742], [-1.0018444494877898, 6.2919536596599075e-14, 1.0018444494877903], [-0.89052839954469731, 0.15742466753937145, 0.89052839954469731], [-0.77921234960160446, 0.31484933507868001, 0.77921234960160479], [-0.66789629965851183, 0.47227400261798858, 0.66789629965851194], [-0.66789629965851449, 0.39356166884833071, 0.66789629965851449], [-0.66789629965851649, 0.31484933507867302, 0.6678962996585166], [-0.66789629965851927, 0.23613700130901524, 0.66789629965851949], [-0.62470390096395645, 0.23613700130901261, 0.62470390096395645], [-0.58151150226939363, 0.23613700130900991, 0.58151150226939385], [-0.54298067695165186, 0.2280541559870515, 0.5429806769516522], [-0.5159890014752625, 0.35521474369949196, 0.51598900147526283], [-0.41942713777954366, 0.58866471464334758, 0.41942713777954382], [-0.25517537023402415, 0.72638670552707529, 0.25517537023402403], [-0.1669740749146077, 0.7631441758064369, 0.16697407491460772], [-0.16697407491460578, 0.82361211894959252, 0.16697407491460581], [-0.16697407491460392, 0.88408006209274814, 0.16697407491460392], [-0.16697407491460201, 0.94454800523590376, 0.16697407491460209], [-0.22263209988614596, 0.94454800523590754, 0.22263209988614596], [-0.27829012485768989, 0.94454800523591087, 0.27829012485768989], [-0.33394814982923376, 0.94454800523591431, 0.33394814982923376], [-0.22263209988614091, 1.1019726727752228, 0.22263209988614094], [-0.11131604994304831, 1.2593973403145315, 0.11131604994304833], [4.4490830996570345e-14, 1.4168220078538398, -4.4490830996570358e-14], [0.11131604994312726, 1.2593973403145173, -0.11131604994312727], [0.22263209988621013, 1.1019726727751948, -0.22263209988621022], [0.33394814982929288, 0.94454800523587235, -0.333948149829293], [0.27829012485774901, 0.94454800523587579, -0.27829012485774907], [0.22263209988620522, 0.94454800523587923, -0.22263209988620528], [0.16697407491466135, 0.94454800523588289, -0.16697407491466135], [0.16697407491465949, 0.8839634219847935, -0.16697407491465949], [0.16697407491465757, 0.82337883873370399, -0.16697407491465757], [0.167033530502539, 0.76539264474743052, -0.16703353050253925], [0.25474920603184431, 0.72674377963683745, -0.2547492060318447], [0.41645156824540264, 0.59135400712321362, -0.41645156824540297], [0.51261906693548787, 0.36328394180643175, -0.5126190669354882], [0.54171994019788805, 0.236137001308939, -0.54171994019788816], [0.58377872668477016, 0.23613700130893633, -0.58377872668477027], [0.62583751317165204, 0.23613700130893367, -0.62583751317165215], [0.66789629965853414, 0.236137001308931, -0.66789629965853425], [0.66789629965853681, 0.31484933507858875, -0.66789629965853692], [0.66789629965853925, 0.39356166884824645, -0.66789629965853925], [0.6678962996585418, 0.4722740026179042, -0.6678962996585418], [0.77921234960162433, 0.3148493350785817, -0.77921234960162455], [0.89052839954470731, 0.15742466753925907, -0.89052839954470742], [1.0018444494877898, -6.2919536596599075e-14, -1.0018444494877903], [0.89052839954469731, -0.15742466753937145, -0.89052839954469731], [0.77921234960160446, -0.31484933507868001, -0.77921234960160479], [0.66789629965851183, -0.47227400261798858, -0.66789629965851194], [0.66789629965851449, -0.39356166884833071, -0.66789629965851449], [0.66789629965851594, -0.31484933507867302, -0.66789629965851616], [0.66789629965851927, -0.23613700130901524, -0.66789629965851949], [0.62412700303051538, -0.23613700130901255, -0.62412700303051549], [0.58035770640251128, -0.2361370013090098, -0.5803577064025115], [0.54051026055526685, -0.23939430291373573, -0.54051026055526719], [0.51306203638393644, -0.36223208094348736, -0.51306203638393666], [0.41673081285387625, -0.5912641664371544, -0.41673081285387648], [0.25443432597100285, -0.72700728185175123, -0.25443432597100279], [0.16697407491460772, -0.76267976634664802, -0.16697407491460778], [0.16697407491460578, -0.82330251264306697, -0.16697407491460581], [0.16697407491460392, -0.88392525893948515, -0.16697407491460392], [0.16697407491460201, -0.94454800523590376, -0.16697407491460209], [0.22263209988614596, -0.94454800523590754, -0.22263209988614596], [0.27829012485768989, -0.94454800523591087, -0.27829012485768989], [0.33394814982923376, -0.94454800523591431, -0.33394814982923376], [0.22263209988614091, -1.1019726727752228, -0.22263209988614094], [0.11131604994304831, -1.2593973403145315, -0.11131604994304833], [-4.4490830996570345e-14, -1.4168220078538398, 4.4490830996570358e-14], [-0.11131604994312719, -1.2593973403145173, 0.11131604994312719], [-0.22263209988621013, -1.1019726727751948, 0.22263209988621022], [-0.33394814982929288, -0.94454800523587235, 0.333948149829293], [-0.27829012485774901, -0.94454800523587579, 0.27829012485774907], [-0.22263209988620522, -0.94454800523587923, 0.22263209988620528], [-0.16697407491466135, -0.94454800523588289, 0.16697407491466135], [-0.16697407491465949, -0.88451035447856785, 0.16697407491465949], [-0.1669740749146576, -0.82447270372125236, 0.16697407491465766], [-0.16697407491465568, -0.7644350529639371, 0.16697407491465568], [-0.25467796448095043, -0.72680342143514998, 0.25467796448095076], [-0.41780222221501112, -0.59025591248002629, 0.41780222221501151], [-0.51424592139679082, -0.3594078532736622, 0.51424592139679126], [-0.54152032712224629, -0.2348277724092542, 0.54152032712224685]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        createdCurves.append(mc.curve( d = 3,p = [[0.54337396735077781, -0.23613700130897328, 0.54337396735079158], [0.58488141145335826, -0.23613700130897328, 0.58488141145337214], [0.62638885555593904, -0.23613700130897328, 0.62638885555595281], [0.66789629965851971, -0.23613700130897328, 0.66789629965853348], [0.6678962996585176, -0.314849335078631, 0.66789629965853603], [0.66789629965851538, -0.39356166884828875, 0.66789629965853836], [0.66789629965851283, -0.47227400261794655, 0.66789629965854036], [0.77921234960160501, -0.31484933507863105, 0.77921234960162356], [0.89052839954469765, -0.15742466753931553, 0.89052839954470686], [1.0018444494877896, -2.1650076306131436e-32, 1.0018444494877898], [0.89052839954470675, 0.1574246675393155, 0.89052839954469776], [0.77921234960162356, 0.31484933507863105, 0.77921234960160535], [0.66789629965854025, 0.47227400261794655, 0.66789629965851305], [0.66789629965853792, 0.39356166884828875, 0.66789629965851538], [0.66789629965853536, 0.31484933507863105, 0.66789629965851727], [0.66789629965853337, 0.23613700130897328, 0.66789629965851993], [0.62470390096397066, 0.23613700130897333, 0.624703900963957], [0.58151150226940784, 0.23613700130897333, 0.58151150226939419], [0.54298067695166574, 0.22805415598701739, 0.54298067695165242], [0.51598900147528404, 0.35521474369945955, 0.51598900147526339], [0.4194271377795793, 0.58866471464332104, 0.4194271377795451], [0.25517537023406789, 0.72638670552705908, 0.25517537023402581], [0.1669740749146538, 0.76314417580642613, 0.16697407491460947], [0.16697407491465555, 0.82361211894958186, 0.1669740749146077], [0.16697407491465732, 0.88408006209273748, 0.166974074914606], [0.16697407491465907, 0.94454800523589311, 0.16697407491460423], [0.222632099886203, 0.94454800523589333, 0.22263209988614813], [0.2782901248577469, 0.94454800523589333, 0.27829012485769211], [0.33394814982929077, 0.94454800523589311, 0.33394814982923599], [0.22263209988620752, 1.1019726727752086, 0.22263209988614352], [0.1113160499431244, 1.2593973403145242, 0.11131604994305125], [4.1154018671827567e-14, 1.4168220078538394, -4.1154018671827574e-14], [-0.11131604994305111, 1.2593973403145242, -0.11131604994312429], [-0.22263209988614352, 1.1019726727752086, -0.22263209988620758], [-0.33394814982923576, 0.94454800523589333, -0.33394814982929072], [-0.27829012485769189, 0.94454800523589311, -0.27829012485774679], [-0.22263209988614813, 0.94454800523589311, -0.222632099886203], [-0.16697407491460423, 0.94454800523589311, -0.1669740749146591], [-0.166974074914606, 0.88396342198480371, -0.16697407491465741], [-0.16697407491460778, 0.82337883873371442, -0.16697407491465563], [-0.16703353050249292, 0.76539264474744084, -0.16703353050253714], [-0.25474920603180068, 0.72674377963685344, -0.25474920603184265], [-0.41645156824536711, 0.5913540071232396, -0.41645156824540125], [-0.51261906693546588, 0.36328394180646389, -0.51261906693548687], [-0.54171994019787362, 0.23613700130897297, -0.54171994019788738], [-0.58377872668475572, 0.23613700130897297, -0.58377872668476949], [-0.62583751317163772, 0.23613700130897297, -0.62583751317165148], [-0.66789629965851971, 0.23613700130897289, -0.66789629965853348], [-0.6678962996585176, 0.31484933507863061, -0.66789629965853603], [-0.66789629965851538, 0.3935616688482883, -0.66789629965853836], [-0.66789629965851305, 0.47227400261794605, -0.66789629965854058], [-0.77921234960160524, 0.31484933507863061, -0.77921234960162367], [-0.89052839954469765, 0.15742466753931494, -0.89052839954470686], [-1.0018444494877896, 2.1650076306131439e-32, -1.0018444494877898], [-0.89052839954470675, -0.1574246675393155, -0.89052839954469776], [-0.77921234960162356, -0.31484933507863105, -0.77921234960160535], [-0.66789629965854025, -0.47227400261794655, -0.66789629965851305], [-0.66789629965853792, -0.39356166884828875, -0.66789629965851538], [-0.66789629965853492, -0.31484933507863105, -0.66789629965851671], [-0.66789629965853337, -0.23613700130897328, -0.66789629965851993], [-0.62412700303052948, -0.23613700130897333, -0.62412700303051583], [-0.5803577064025256, -0.23613700130897333, -0.58035770640251205], [-0.5405102605552814, -0.23939430291370173, -0.54051026055526741], [-0.51306203638395842, -0.3622320809434551, -0.51306203638393733], [-0.41673081285391206, -0.5912641664371282, -0.41673081285387775], [-0.2544343259710467, -0.72700728185173513, -0.25443432597100452], [-0.16697407491465377, -0.76267976634663759, -0.1669740749146095], [-0.16697407491465552, -0.82330251264305621, -0.16697407491460772], [-0.16697407491465729, -0.88392525893947471, -0.166974074914606], [-0.16697407491465907, -0.94454800523589311, -0.16697407491460423], [-0.222632099886203, -0.94454800523589333, -0.22263209988614813], [-0.2782901248577469, -0.94454800523589333, -0.27829012485769211], [-0.33394814982929077, -0.94454800523589311, -0.33394814982923599], [-0.22263209988620752, -1.1019726727752086, -0.22263209988614352], [-0.1113160499431244, -1.2593973403145242, -0.11131604994305125], [-4.1154018671827567e-14, -1.4168220078538394, 4.1154018671827574e-14], [0.11131604994305104, -1.2593973403145242, 0.11131604994312422], [0.22263209988614352, -1.1019726727752086, 0.22263209988620758], [0.33394814982923576, -0.94454800523589333, 0.33394814982929072], [0.27829012485769189, -0.94454800523589311, 0.27829012485774679], [0.22263209988614813, -0.94454800523589311, 0.222632099886203], [0.16697407491460423, -0.94454800523589311, 0.1669740749146591], [0.166974074914606, -0.88451035447857806, 0.16697407491465743], [0.16697407491460772, -0.82447270372126258, 0.16697407491465566], [0.16697407491460944, -0.76443505296394754, 0.16697407491465385], [0.25467796448090668, -0.72680342143516574, 0.25467796448094865], [0.4178022222149757, -0.59025591248005249, 0.41780222221500979], [0.51424592139676939, -0.3594078532736944, 0.51424592139679004], [0.54152032712223241, -0.23482777240928815, 0.54152032712224574]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        return combineCurves(createdCurves)          
    elif desiredShape == 'arrowsPointCenter':
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[0.83264361409028087, 0.0, 0.0], [0.83264361409028087, -1.0210790426738748e-16, -0.45985311961018854], [0.45984849378663273, -1.8488504947319096e-16, -0.83264823991383852], [-4.6258235558205147e-06, -1.8488504947319096e-16, -0.83264823991383852], [-0.45985774543374808, -1.8488504947319096e-16, -0.83264823991383852], [-0.8326528657373925, -1.0210790426738748e-16, -0.45985311961018854], [-0.8326528657373925, 0.0, 0.0], [-0.8326528657373925, 1.0210995854571571e-16, 0.45986237125730206], [-0.45985774543374808, 1.8488504947319054e-16, 0.83264823991383663], [-4.6258235558205147e-06, 1.8488504947319054e-16, 0.83264823991383663], [0.45984849378663273, 1.8488504947319054e-16, 0.83264823991383663], [0.83264361409028087, 1.0210995854571571e-16, 0.45986237125730206], [0.83264361409028087, 0.0, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.16653427380632091, 0.0, 0.0], [-0.20354049218105183, -8.2170311387865599e-18, -0.037006218374730913], [-0.46258735139712764, -6.5736988650489902e-17, -0.29605307759080485], [-0.49959356977185859, -7.3954019789276457e-17, -0.33305929596553574], [-0.49959356977185859, -6.9845504219883186e-17, -0.31455618677817032], [-0.49959356977185859, -4.1085525464031716e-17, -0.18503275717013426], [-0.49959356977185859, -3.6977009894638444e-17, -0.16652964798276884], [-0.5551018693834423, -3.6977009894638444e-17, -0.16652964798276884], [-0.94366496246146603, -3.6977009894638444e-17, -0.16652964798276884], [-0.99917326207305157, -3.6977009894638444e-17, -0.16652964798276884], [-0.99917326207305157, -2.8760207006716935e-17, -0.12952445755854872], [-0.99917326207305157, 2.8758152728389121e-17, 0.12951520591143706], [-0.99917326207305157, 3.697495561631063e-17, 0.16652039633565718], [-0.94366496246146603, 3.697495561631063e-17, 0.16652039633565718], [-0.5551018693834423, 3.697495561631063e-17, 0.16652039633565718], [-0.49959356977185859, 3.697495561631063e-17, 0.16652039633565718], [-0.49959356977185859, 4.1083471185703914e-17, 0.18502350552302266], [-0.49959356977185859, 6.9843449941555785e-17, 0.31454693513106052], [-0.49959356977185859, 7.3951965510949069e-17, 0.333050044318426], [-0.46258735139712764, 6.5735162623027559e-17, 0.29604485389420587], [-0.20354049218105183, 8.2168028879215077e-18, 0.037005190424220118], [-0.16653427380632091, 0.0, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-4.6258235558205147e-06, 3.6977009894638025e-17, 0.16652964798276695], [-0.037010844198286728, 4.519404103342458e-17, 0.20353586635749785], [-0.29605770341435883, 1.0271399854512793e-16, 0.46258272557357183], [-0.33306392178908972, 1.109310296839145e-16, 0.49958894394830278], [-0.31456081260172614, 1.109310296839145e-16, 0.49958894394830278], [-0.1850373829936845, 1.109310296839145e-16, 0.49958894394830278], [-0.16653427380632091, 1.109310296839145e-16, 0.49958894394830278], [-0.16653427380632091, 1.2325657639209432e-16, 0.55509827151039903], [-0.16653427380632091, 2.0953651265964874e-16, 0.9436685603345073], [-0.16653427380632091, 2.2186205936782858e-16, 0.99917788789660367], [-0.12952805543159002, 2.2186205936782858e-16, 0.99917788789660367], [0.12951880378448208, 2.2186205936782858e-16, 0.99917788789660367], [0.166525022159213, 2.2186205936782858e-16, 0.99917788789660367], [0.166525022159213, 2.0953651265964874e-16, 0.9436685603345073], [0.166525022159213, 1.2325657639209432e-16, 0.55509827151039903], [0.166525022159213, 1.109310296839145e-16, 0.49958894394830278], [0.18502813134657661, 1.109310296839145e-16, 0.49958894394830278], [0.31455156095461823, 1.109310296839145e-16, 0.49958894394830278], [0.33305467014198181, 1.109310296839145e-16, 0.49958894394830278], [0.29604845176725092, 1.0271399854512793e-16, 0.46258272557357183], [0.037001592551175091, 4.519404103342458e-17, 0.20353586635749785], [-4.6258235558205147e-06, 3.6977009894638025e-17, 0.16652964798276695]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-4.6258235558205147e-06, -3.697906417296542e-17, -0.16653889962987672], [0.037001592551175091, -4.5195867060886929e-17, -0.20354409005409685], [0.29604845176725092, -1.0271422679599299e-16, -0.46258375352408265], [0.33305467014198181, -1.109310296839145e-16, -0.49958894394830278], [0.31455156095461823, -1.109310296839145e-16, -0.49958894394830278], [0.18502813134657661, -1.109310296839145e-16, -0.49958894394830278], [0.166525022159213, -1.109310296839145e-16, -0.49958894394830278], [0.166525022159213, -1.2325657639209432e-16, -0.55509827151039903], [0.166525022159213, -2.0953651265964916e-16, -0.94366856033450919], [0.166525022159213, -2.21862059367829e-16, -0.99917788789660555], [0.12951880378448208, -2.21862059367829e-16, -0.99917788789660555], [-0.12952805543159002, -2.21862059367829e-16, -0.99917788789660555], [-0.16653427380632091, -2.21862059367829e-16, -0.99917788789660555], [-0.16653427380632091, -2.0953651265964916e-16, -0.94366856033450919], [-0.16653427380632091, -1.2325657639209432e-16, -0.55509827151039903], [-0.16653427380632091, -1.109310296839145e-16, -0.49958894394830278], [-0.1850373829936845, -1.109310296839145e-16, -0.49958894394830278], [-0.31456081260172614, -1.109310296839145e-16, -0.49958894394830278], [-0.33306392178908972, -1.109310296839145e-16, -0.49958894394830278], [-0.29605770341435883, -1.0271422679599299e-16, -0.46258375352408265], [-0.037010844198286728, -4.5195867060886929e-17, -0.20354409005409685], [-4.6258235558205147e-06, -3.697906417296542e-17, -0.16653889962987672]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.166525022159213, 0.0, 0.0], [0.20353124053394392, 8.2170311387865599e-18, 0.037006218374730913], [0.46257809975001601, 6.5736988650489495e-17, 0.29605307759080302], [0.49958431812474696, 7.395401978927605e-17, 0.33305929596553391], [0.49958431812474696, 6.9845504219882779e-17, 0.31455618677816849], [0.49958431812474696, 4.1085525464031309e-17, 0.18503275717013243], [0.49958431812474696, 3.6977009894638025e-17, 0.16652964798276695], [0.55509364568684139, 3.6977009894638025e-17, 0.16652964798276695], [0.9436639345109552, 3.6977009894638025e-17, 0.16652964798276695], [0.99917326207304968, 3.6977009894638025e-17, 0.16652964798276695], [0.99917326207304968, 2.875997875585147e-17, 0.12952342960803606], [0.99917326207304968, -2.8759978755851877e-17, -0.12952342960803789], [0.99917326207304968, -3.6977009894638444e-17, -0.16652964798276884], [0.9436639345109552, -3.6977009894638444e-17, -0.16652964798276884], [0.55509364568684139, -3.6977009894638444e-17, -0.16652964798276884], [0.49958431812474696, -3.6977009894638444e-17, -0.16652964798276884], [0.49958431812474696, -4.1085525464031716e-17, -0.18503275717013426], [0.49958431812474696, -6.9845504219883186e-17, -0.31455618677817032], [0.49958431812474696, -7.3954019789276457e-17, -0.33305929596553574], [0.46257809975001601, -6.5736988650489902e-17, -0.29605307759080485], [0.20353124053394392, -8.2170311387865599e-18, -0.037006218374730913], [0.166525022159213, 0.0, 0.0]],k = (0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0)))        
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
        createdCurves.append(mc.curve( d = 3,p = [[0.49653306357323818, -1.6772259045506772e-16, -0.83175296395996756], [0.49653306357323818, -0.060313942143049908, -0.83175296395996756], [0.53259056699264318, -0.18589688147297709, -0.7956954605405625], [0.66333300332764356, -0.26235330212142899, -0.66495302420556213], [0.79454749798503155, -0.18689396006771827, -0.53373852954817402], [0.84977448787480936, -0.0022909995709952248, -0.47851153965839632], [0.796834041835628, 0.18364692607912861, -0.53145198569757768], [0.66657075401115962, 0.26233333665862968, -0.66171527352204607], [0.53490470348993635, 0.18911547096806502, -0.79338132404326933], [0.49730290854737419, 0.064441609270353931, -0.83098311898583155], [0.49655859138048963, 0.0041368532328297028, -0.83172743615271605]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.34008074617864159, -1.2977991762858933e-16, -0.99303021917653811], [0.34008074617864159, -0.11748096306721834, -0.99303021917653811], [0.41031442809358437, -0.36209446590044353, -0.92279653726159527], [0.66497772464881166, -0.51101814111220445, -0.66813324070636793], [0.92056050788269916, -0.36403659983170078, -0.41255045747248043], [1.0281329816594325, -0.0044624646710827902, -0.30497798369574725], [0.92501429359324649, 0.35771194807561529, -0.40809667176193315], [0.67128429415754765, 0.51097925189829507, -0.66182667119763194], [0.41482195943229527, 0.36836371278044638, -0.91828900592288432], [0.34158026893839522, 0.12552093346388851, -0.99153069641678448], [0.34013046986232626, 0.0080578633163772527, -0.99298049549285339]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[2.8271277527915075e-17, -0.94443168880522499, -0.46170500012899462], [-0.11748096306721817, -0.94443168880522499, -0.46170500012899462], [-0.36209446590044331, -0.94443168880522499, -0.36237957462948445], [-0.51101814111220412, -0.94443168880522499, -0.0022312868024406004], [-0.36403659983170045, -0.94443168880522499, 0.35921735155598611], [-0.0044624646710825231, -0.94443168880522499, 0.51134780290906634], [0.35771194807561552, -0.94443168880522499, 0.3655159557117455], [0.51097925189829518, -0.94443168880522499, 0.0066875493288623931], [0.36836371278044644, -0.94443168880522499, -0.35600496267745785], [0.12552093346388865, -0.94443168880522499, -0.45958435470506398], [0.0080578633163774088, -0.94443168880522499, -0.46163468022115661]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.37748142646064781, -1.3033817493018063e-16, -0.71270132684737708], [0.37748142646064781, -0.060313942143049866, -0.71270132684737708], [0.41353892988005286, -0.18589688147297703, -0.67664382342797202], [0.54428136621505308, -0.26235330212142893, -0.54590138709297176], [0.67549586087244129, -0.18689396006771822, -0.4146868924355836], [0.73072285076221899, -0.0022909995709951875, -0.35945990254580579], [0.67778240472303763, 0.18364692607912866, -0.41240034858498725], [0.54751911689856936, 0.26233333665862973, -0.5426636364094557], [0.41585306637734598, 0.18911547096806505, -0.67432968693067896], [0.37825127143478382, 0.064441609270353958, -0.71193148187324096], [0.37750695426789926, 0.004136853232829741, -0.71267579904012568]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[1.4514285145527346e-17, -0.94689057277391731, -0.23703626475213518], [-0.06031394214304972, -0.94689057277391731, -0.23703626475213518], [-0.18589688147297687, -0.94689057277391731, -0.18604325439109828], [-0.26235330212142871, -0.94689057277391731, -0.0011455277484399961], [-0.18689396006771797, -0.94689057277391731, 0.18441979017597035], [-0.0022909995709949867, -0.94689057277391731, 0.26252254828713595], [0.18364692607912883, -0.94689057277391731, 0.18765345150044455], [0.26233333665862985, -0.94689057277391731, 0.0034333431797712987], [0.18911547096806516, -0.94689057277391731, -0.18277057117144385], [0.064441609270354083, -0.94689057277391731, -0.23594753954878719], [0.0041368532328298849, -0.94689057277391731, -0.23700016298090251]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[1.4514285145527346e-17, -0.76930081733506617, -0.23703626475213518], [-0.06031394214304972, -0.76930081733506617, -0.23703626475213518], [-0.18589688147297687, -0.76930081733506617, -0.18604325439109828], [-0.26235330212142871, -0.76930081733506617, -0.0011455277484399961], [-0.18689396006771797, -0.76930081733506617, 0.18441979017597035], [-0.0022909995709949867, -0.76930081733506617, 0.26252254828713595], [0.18364692607912883, -0.76930081733506617, 0.18765345150044455], [0.26233333665862985, -0.76930081733506617, 0.0034333431797712987], [0.18911547096806516, -0.76930081733506617, -0.18277057117144385], [0.064441609270354083, -0.76930081733506617, -0.23594753954878719], [0.0041368532328298849, -0.76930081733506617, -0.23700016298090251]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[1.4514285145527346e-17, 0.93804557046393011, -0.23703626475213518], [-0.06031394214304972, 0.93804557046393011, -0.23703626475213518], [-0.18589688147297687, 0.93804557046393011, -0.18604325439109828], [-0.26235330212142871, 0.93804557046393011, -0.0011455277484399961], [-0.18689396006771797, 0.93804557046393011, 0.18441979017597035], [-0.0022909995709949867, 0.93804557046393011, 0.26252254828713595], [0.18364692607912883, 0.93804557046393011, 0.18765345150044455], [0.26233333665862985, 0.93804557046393011, 0.0034333431797712987], [0.18911547096806516, 0.93804557046393011, -0.18277057117144385], [0.064441609270354083, 0.93804557046393011, -0.23594753954878719], [0.0041368532328298849, 0.93804557046393011, -0.23700016298090251]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[2.8271277527915075e-17, 0.93804557046393011, -0.46170500012899462], [-0.11748096306721817, 0.93804557046393011, -0.46170500012899462], [-0.36209446590044331, 0.93804557046393011, -0.36237957462948445], [-0.51101814111220412, 0.93804557046393011, -0.0022312868024406004], [-0.36403659983170045, 0.93804557046393011, 0.35921735155598611], [-0.0044624646710825231, 0.93804557046393011, 0.51134780290906634], [0.35771194807561552, 0.93804557046393011, 0.3655159557117455], [0.51097925189829518, 0.93804557046393011, 0.0066875493288623931], [0.36836371278044644, 0.93804557046393011, -0.35600496267745785], [0.12552093346388865, 0.93804557046393011, -0.45958435470506398], [0.0080578633163774088, 0.93804557046393011, -0.46163468022115661]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[1.4514285145527346e-17, 0.76045581502507897, -0.23703626475213518], [-0.06031394214304972, 0.76045581502507897, -0.23703626475213518], [-0.18589688147297687, 0.76045581502507897, -0.18604325439109828], [-0.26235330212142871, 0.76045581502507897, -0.0011455277484399961], [-0.18689396006771797, 0.76045581502507897, 0.18441979017597035], [-0.0022909995709949867, 0.76045581502507897, 0.26252254828713595], [0.18364692607912883, 0.76045581502507897, 0.18765345150044455], [0.26233333665862985, 0.76045581502507897, 0.0034333431797712987], [0.18911547096806516, 0.76045581502507897, -0.18277057117144385], [0.064441609270354083, 0.76045581502507897, -0.23594753954878719], [0.0041368532328298849, 0.76045581502507897, -0.23700016298090251]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.3423640425868863, -3.7114397156534619e-16, 0.99531351558478265], [0.34236404258688624, -0.11748096306721856, 0.99531351558478265], [0.4125977245018288, -0.36209446590044375, 0.9250798336698397], [0.66726102105705598, -0.51101814111220478, 0.67041653711461258], [0.92284380429094359, -0.36403659983170128, 0.41483375388072491], [1.0304162780676771, -0.0044624646710834086, 0.30726128010399179], [0.92729759000149148, 0.35771194807561463, 0.4103799681701778], [0.67356759056579285, 0.51097925189829452, 0.66410996760587671], [0.41710525584054031, 0.36836371278044605, 0.92057230233112897], [0.34386356534664003, 0.12552093346388823, 0.99381399282502902], [0.34241376627057096, 0.0080578633163770098, 0.99526379190109793]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.54337396735079224, -0.23613700130893922, 0.54337396735079224], [-0.58488141145337269, -0.23613700130893661, 0.5848814114533728], [-0.62638885555595336, -0.236137001308934, 0.62638885555595347], [-0.66789629965853414, -0.23613700130893139, 0.66789629965853425], [-0.66789629965853681, -0.31484933507858914, 0.66789629965853692], [-0.66789629965853925, -0.39356166884824689, 0.66789629965853925], [-0.66789629965854147, -0.4722740026179047, 0.66789629965854147], [-0.77921234960162422, -0.31484933507858215, 0.77921234960162433], [-0.89052839954470731, -0.15742466753925963, 0.89052839954470742], [-1.0018444494877898, 6.2919536596599075e-14, 1.0018444494877903], [-0.89052839954469731, 0.15742466753937145, 0.89052839954469731], [-0.77921234960160446, 0.31484933507868001, 0.77921234960160479], [-0.66789629965851183, 0.47227400261798858, 0.66789629965851194], [-0.66789629965851449, 0.39356166884833071, 0.66789629965851449], [-0.66789629965851649, 0.31484933507867302, 0.6678962996585166], [-0.66789629965851927, 0.23613700130901524, 0.66789629965851949], [-0.62470390096395645, 0.23613700130901261, 0.62470390096395645], [-0.58151150226939363, 0.23613700130900991, 0.58151150226939385], [-0.54298067695165186, 0.2280541559870515, 0.5429806769516522], [-0.5159890014752625, 0.35521474369949196, 0.51598900147526283], [-0.41942713777954366, 0.58866471464334758, 0.41942713777954382], [-0.25517537023402415, 0.72638670552707529, 0.25517537023402403], [-0.1669740749146077, 0.7631441758064369, 0.16697407491460772], [-0.16697407491460578, 0.82361211894959252, 0.16697407491460581], [-0.16697407491460392, 0.88408006209274814, 0.16697407491460392], [-0.16697407491460201, 0.94454800523590376, 0.16697407491460209], [-0.22263209988614599, 0.94454800523590754, 0.22263209988614599], [-0.27829012485768989, 0.94454800523591087, 0.27829012485768989], [-0.33394814982923376, 0.94454800523591431, 0.33394814982923376], [-0.22263209988614091, 1.1019726727752228, 0.22263209988614094], [-0.11131604994304831, 1.2593973403145315, 0.11131604994304833], [4.4490830996570345e-14, 1.4168220078538398, -4.4490830996570358e-14], [0.11131604994312726, 1.2593973403145173, -0.11131604994312727], [0.22263209988621013, 1.1019726727751948, -0.22263209988621022], [0.33394814982929288, 0.94454800523587235, -0.333948149829293], [0.27829012485774901, 0.94454800523587579, -0.27829012485774907], [0.22263209988620522, 0.94454800523587923, -0.22263209988620528], [0.16697407491466135, 0.94454800523588289, -0.16697407491466135], [0.16697407491465949, 0.8839634219847935, -0.16697407491465949], [0.16697407491465757, 0.82337883873370399, -0.16697407491465757], [0.167033530502539, 0.76539264474743052, -0.16703353050253925], [0.25474920603184431, 0.72674377963683745, -0.2547492060318447], [0.41645156824540264, 0.59135400712321362, -0.41645156824540297], [0.51261906693548787, 0.36328394180643175, -0.5126190669354882], [0.54171994019788805, 0.236137001308939, -0.54171994019788816], [0.58377872668477016, 0.23613700130893633, -0.58377872668477027], [0.62583751317165204, 0.23613700130893367, -0.62583751317165215], [0.66789629965853414, 0.236137001308931, -0.66789629965853425], [0.66789629965853681, 0.31484933507858875, -0.66789629965853692], [0.66789629965853925, 0.39356166884824645, -0.66789629965853925], [0.6678962996585418, 0.4722740026179042, -0.6678962996585418], [0.77921234960162433, 0.3148493350785817, -0.77921234960162455], [0.89052839954470731, 0.15742466753925907, -0.89052839954470742], [1.0018444494877898, -6.2919536596599075e-14, -1.0018444494877903], [0.89052839954469731, -0.15742466753937145, -0.89052839954469731], [0.77921234960160446, -0.31484933507868001, -0.77921234960160479], [0.66789629965851183, -0.47227400261798858, -0.66789629965851194], [0.66789629965851449, -0.39356166884833071, -0.66789629965851449], [0.66789629965851594, -0.31484933507867302, -0.66789629965851616], [0.66789629965851927, -0.23613700130901524, -0.66789629965851949], [0.62412700303051538, -0.23613700130901255, -0.62412700303051549], [0.58035770640251128, -0.2361370013090098, -0.5803577064025115], [0.54051026055526685, -0.23939430291373573, -0.54051026055526719], [0.51306203638393644, -0.36223208094348736, -0.51306203638393666], [0.41673081285387625, -0.5912641664371544, -0.41673081285387648], [0.25443432597100285, -0.72700728185175123, -0.25443432597100279], [0.16697407491460772, -0.76267976634664802, -0.16697407491460778], [0.16697407491460578, -0.82330251264306697, -0.16697407491460581], [0.16697407491460392, -0.88392525893948515, -0.16697407491460392], [0.16697407491460201, -0.94454800523590376, -0.16697407491460209], [0.22263209988614599, -0.94454800523590754, -0.22263209988614599], [0.27829012485768989, -0.94454800523591087, -0.27829012485768989], [0.33394814982923376, -0.94454800523591431, -0.33394814982923376], [0.22263209988614091, -1.1019726727752228, -0.22263209988614094], [0.11131604994304831, -1.2593973403145315, -0.11131604994304833], [-4.4490830996570345e-14, -1.4168220078538398, 4.4490830996570358e-14], [-0.11131604994312719, -1.2593973403145173, 0.11131604994312719], [-0.22263209988621013, -1.1019726727751948, 0.22263209988621022], [-0.33394814982929288, -0.94454800523587235, 0.333948149829293], [-0.27829012485774901, -0.94454800523587579, 0.27829012485774907], [-0.22263209988620522, -0.94454800523587923, 0.22263209988620528], [-0.16697407491466135, -0.94454800523588289, 0.16697407491466135], [-0.16697407491465949, -0.88451035447856785, 0.16697407491465949], [-0.1669740749146576, -0.82447270372125236, 0.16697407491465766], [-0.16697407491465568, -0.7644350529639371, 0.16697407491465568], [-0.25467796448095043, -0.72680342143514998, 0.25467796448095076], [-0.41780222221501112, -0.59025591248002629, 0.41780222221501151], [-0.51424592139679082, -0.3594078532736622, 0.51424592139679126], [-0.54152032712224629, -0.2348277724092542, 0.54152032712224685]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        createdCurves.append(mc.curve( d = 3,p = [[0.54337396735077781, -0.23613700130897328, 0.54337396735079158], [0.58488141145335826, -0.23613700130897328, 0.58488141145337214], [0.62638885555593904, -0.23613700130897328, 0.62638885555595281], [0.66789629965851971, -0.23613700130897328, 0.66789629965853348], [0.6678962996585176, -0.314849335078631, 0.66789629965853603], [0.66789629965851538, -0.39356166884828875, 0.66789629965853836], [0.66789629965851283, -0.47227400261794655, 0.66789629965854036], [0.77921234960160501, -0.31484933507863105, 0.77921234960162356], [0.89052839954469765, -0.15742466753931553, 0.89052839954470686], [1.0018444494877896, -2.1650076306131436e-32, 1.0018444494877898], [0.89052839954470675, 0.1574246675393155, 0.89052839954469776], [0.77921234960162356, 0.31484933507863105, 0.77921234960160535], [0.66789629965854025, 0.47227400261794655, 0.66789629965851305], [0.66789629965853792, 0.39356166884828875, 0.66789629965851538], [0.66789629965853536, 0.31484933507863105, 0.66789629965851727], [0.66789629965853337, 0.23613700130897328, 0.66789629965851993], [0.62470390096397066, 0.23613700130897333, 0.624703900963957], [0.58151150226940784, 0.23613700130897333, 0.58151150226939419], [0.54298067695166574, 0.22805415598701739, 0.54298067695165242], [0.51598900147528404, 0.35521474369945955, 0.51598900147526339], [0.4194271377795793, 0.58866471464332104, 0.4194271377795451], [0.25517537023406789, 0.72638670552705908, 0.25517537023402581], [0.1669740749146538, 0.76314417580642613, 0.16697407491460947], [0.16697407491465555, 0.82361211894958186, 0.1669740749146077], [0.16697407491465732, 0.88408006209273748, 0.166974074914606], [0.16697407491465907, 0.94454800523589311, 0.16697407491460423], [0.222632099886203, 0.94454800523589333, 0.22263209988614813], [0.2782901248577469, 0.94454800523589333, 0.27829012485769211], [0.33394814982929077, 0.94454800523589311, 0.33394814982923599], [0.22263209988620752, 1.1019726727752086, 0.22263209988614352], [0.1113160499431244, 1.2593973403145242, 0.11131604994305125], [4.1154018671827567e-14, 1.4168220078538394, -4.1154018671827574e-14], [-0.11131604994305111, 1.2593973403145242, -0.11131604994312429], [-0.22263209988614352, 1.1019726727752086, -0.22263209988620758], [-0.33394814982923576, 0.94454800523589333, -0.33394814982929072], [-0.27829012485769189, 0.94454800523589311, -0.27829012485774679], [-0.22263209988614813, 0.94454800523589311, -0.222632099886203], [-0.16697407491460423, 0.94454800523589311, -0.1669740749146591], [-0.166974074914606, 0.88396342198480371, -0.16697407491465741], [-0.16697407491460778, 0.82337883873371442, -0.16697407491465563], [-0.16703353050249292, 0.76539264474744084, -0.16703353050253714], [-0.25474920603180068, 0.72674377963685344, -0.25474920603184265], [-0.41645156824536711, 0.5913540071232396, -0.41645156824540125], [-0.51261906693546588, 0.36328394180646389, -0.51261906693548687], [-0.54171994019787362, 0.23613700130897297, -0.54171994019788738], [-0.58377872668475572, 0.23613700130897297, -0.58377872668476949], [-0.62583751317163772, 0.23613700130897297, -0.62583751317165148], [-0.66789629965851971, 0.23613700130897289, -0.66789629965853348], [-0.6678962996585176, 0.31484933507863061, -0.66789629965853603], [-0.66789629965851538, 0.3935616688482883, -0.66789629965853836], [-0.66789629965851305, 0.47227400261794605, -0.66789629965854058], [-0.77921234960160524, 0.31484933507863061, -0.77921234960162367], [-0.89052839954469765, 0.15742466753931494, -0.89052839954470686], [-1.0018444494877896, 2.1650076306131439e-32, -1.0018444494877898], [-0.89052839954470675, -0.1574246675393155, -0.89052839954469776], [-0.77921234960162356, -0.31484933507863105, -0.77921234960160535], [-0.66789629965854025, -0.47227400261794655, -0.66789629965851305], [-0.66789629965853792, -0.39356166884828875, -0.66789629965851538], [-0.66789629965853492, -0.31484933507863105, -0.66789629965851671], [-0.66789629965853337, -0.23613700130897328, -0.66789629965851993], [-0.62412700303052948, -0.23613700130897333, -0.62412700303051583], [-0.5803577064025256, -0.23613700130897333, -0.58035770640251205], [-0.5405102605552814, -0.23939430291370173, -0.54051026055526741], [-0.51306203638395842, -0.3622320809434551, -0.51306203638393733], [-0.41673081285391206, -0.5912641664371282, -0.41673081285387775], [-0.2544343259710467, -0.72700728185173513, -0.25443432597100452], [-0.16697407491465377, -0.76267976634663759, -0.1669740749146095], [-0.16697407491465552, -0.82330251264305621, -0.16697407491460772], [-0.16697407491465729, -0.88392525893947471, -0.166974074914606], [-0.16697407491465907, -0.94454800523589311, -0.16697407491460423], [-0.222632099886203, -0.94454800523589333, -0.22263209988614813], [-0.2782901248577469, -0.94454800523589333, -0.27829012485769211], [-0.33394814982929077, -0.94454800523589311, -0.33394814982923599], [-0.22263209988620752, -1.1019726727752086, -0.22263209988614352], [-0.1113160499431244, -1.2593973403145242, -0.11131604994305125], [-4.1154018671827567e-14, -1.4168220078538394, 4.1154018671827574e-14], [0.11131604994305104, -1.2593973403145242, 0.11131604994312422], [0.22263209988614352, -1.1019726727752086, 0.22263209988620758], [0.33394814982923576, -0.94454800523589333, 0.33394814982929072], [0.27829012485769189, -0.94454800523589311, 0.27829012485774679], [0.22263209988614813, -0.94454800523589311, 0.222632099886203], [0.16697407491460423, -0.94454800523589311, 0.1669740749146591], [0.166974074914606, -0.88451035447857806, 0.16697407491465743], [0.16697407491460772, -0.82447270372126258, 0.16697407491465566], [0.16697407491460944, -0.76443505296394754, 0.16697407491465385], [0.25467796448090668, -0.72680342143516574, 0.25467796448094865], [0.4178022222149757, -0.59025591248005249, 0.41780222221500979], [0.51424592139676939, -0.3594078532736944, 0.51424592139679004], [0.54152032712223241, -0.23482777240928815, 0.54152032712224574]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        createdCurves.append(mc.curve( d = 3,p = [[0.37564205494233577, -3.7883583725197993e-16, 0.71086195532906515], [0.37564205494233577, -0.060313942143050116, 0.71086195532906515], [0.41169955836174071, -0.18589688147297725, 0.6748044519096601], [0.54244199469674093, -0.26235330212142921, 0.54406201557465983], [0.67365648935412903, -0.18689396006771858, 0.41284752091727167], [0.72888347924390706, -0.0022909995709956298, 0.35762053102749392], [0.67594303320472582, 0.18364692607912822, 0.41056097706667533], [0.54567974538025754, 0.26233333665862935, 0.54082426489114366], [0.41401369485903411, 0.18911547096806477, 0.67249031541236703], [0.37641189991647195, 0.064441609270353681, 0.71009211035492914], [0.37566758274958723, 0.004136853232829492, 0.71083642752181364]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.71188342203164257, 2.1174253174440696e-16, 0.37666352164491329], [-0.71188342203164257, -0.060313942143049533, 0.37666352164491329], [-0.67582591861223751, -0.18589688147297667, 0.41272102506431835], [-0.54508348227723724, -0.2623533021214286, 0.54346346139931867], [-0.41386898761984903, -0.18689396006771788, 0.67467795605670677], [-0.35864199773007122, -0.0022909995709948453, 0.72990494594648458], [-0.41158244376925263, 0.183646926079129, 0.67696449990730312], [-0.54184573159372096, 0.26233333665863007, 0.54670121208283473], [-0.67351178211494445, 0.18911547096806541, 0.41503516156161147], [-0.71111357705750655, 0.064441609270354305, 0.37743336661904942], [-0.71185789422439116, 0.0041368532328300827, 0.37668904945216486]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.82916763789423087, 2.4857194431410498e-16, 0.49394773750750148], [-0.82916763789423087, -0.060313942143049498, 0.49394773750750148], [-0.79311013447482581, -0.18589688147297664, 0.5300052409269066], [-0.66236769813982554, -0.26235330212142854, 0.66074767726190686], [-0.53115320348243733, -0.18689396006771783, 0.79196217191929497], [-0.47592621359265957, -0.0022909995709948085, 0.84718916180907278], [-0.52886665963184099, 0.18364692607912905, 0.79424871576989131], [-0.65912994745630937, 0.26233333665863012, 0.66398542794542292], [-0.79079599797753275, 0.18911547096806544, 0.53231937742419966], [-0.82839779292009486, 0.064441609270354333, 0.49471758248163761], [-0.82914211008697947, 0.0041368532328301191, 0.493973265314753]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.99891823097593857, 2.9069052161454964e-16, 0.34596875797804183], [-0.99891823097593857, -0.11748096306721792, 0.34596875797804183], [-0.92868454906099573, -0.36209446590044309, 0.41620243989298467], [-0.6740212525057685, -0.51101814111220412, 0.6708657364482119], [-0.41843846927188089, -0.36403659983170039, 0.9264485196820994], [-0.31086599549514765, -0.0044624646710823704, 1.0340209934588327], [-0.41398468356133356, 0.35771194807561574, 0.93090230539264673], [-0.6677146829970324, 0.51097925189829552, 0.67717230595694788], [-0.92417701772228489, 0.36836371278044683, 0.42070997123169551], [-0.99741870821618495, 0.12552093346388893, 0.3474682807377954], [-0.99886850729225385, 0.0080578633163776742, 0.3460184816617265]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.71755704583986968, 6.5101836113483467e-16, -0.38233714545314046], [-0.71755704583986968, -0.060313942143049089, -0.38233714545314046], [-0.68149954242046473, -0.18589688147297623, -0.41839464887254552], [-0.55075710608546458, -0.26235330212142821, -0.54913708520754578], [-0.41954261142807642, -0.18689396006771755, -0.68035157986493389], [-0.36431562153829838, -0.0022909995709945999, -0.7355785697547117], [-0.41725606757747968, 0.18364692607912925, -0.68263812371553012], [-0.54751935540194796, 0.2623333366586304, -0.55237483589106184], [-0.67918540592317134, 0.1891154709680658, -0.42070878536983858], [-0.71678720086573355, 0.064441609270354722, -0.38310699042727647], [-0.71753151803261828, 0.0041368532328305216, -0.38236267326039186]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.84273419635681623, 7.689421811505439e-16, -0.50751429597008735], [-0.84273419635681623, -0.060313942143048964, -0.50751429597008735], [-0.80667669293741129, -0.18589688147297612, -0.54357179938949252], [-0.67593425660241113, -0.2623533021214281, -0.67431423572449278], [-0.54471976194502292, -0.18689396006771744, -0.805528730381881], [-0.48949277205524488, -0.0022909995709944819, -0.86075572027165859], [-0.54243321809442624, 0.18364692607912936, -0.80781527423247723], [-0.67269650591889441, 0.26233333665863051, -0.67755198640800884], [-0.80436255644011778, 0.18911547096806591, -0.54588593588678547], [-0.84196435138268, 0.064441609270354847, -0.50828414094422347], [-0.84270866854956472, 0.0041368532328306395, -0.50753982377733897]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-1.0020042029130312, 8.9532549480666826e-16, -0.34905472991513559], [-1.0020042029130314, -0.11748096306721729, -0.34905472991513559], [-0.93177052099808877, -0.36209446590044247, -0.41928841183007848], [-0.67710722444286164, -0.51101814111220345, -0.6739517083853056], [-0.42152444120897403, -0.3640365998317, -0.92953449161919321], [-0.31395196743224041, -0.0044624646710821423, -1.0371069653959264], [-0.41707065549842609, 0.3577119480756159, -0.93398827732974044], [-0.67080065493412477, 0.51097925189829585, -0.68025827789404147], [-0.92726298965937737, 0.36836371278044733, -0.42379594316878921], [-1.0005046801532775, 0.12552093346388951, -0.35055425267488916], [-1.0019544792293467, 0.0080578633163782762, -0.34910445359882025]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[0.50081920545928216, -4.9675965726768921e-16, 0.83603910584601193], [0.50081920545928216, -0.060313942143050234, 0.83603910584601193], [0.5368767088786871, -0.18589688147297739, 0.79998160242660687], [0.66761914521368726, -0.26235330212142938, 0.66923916609160661], [0.79883363987107547, -0.18689396006771872, 0.53802467143421839], [0.8540606297608534, -0.0022909995709957478, 0.48279768154444069], [0.80112018372167215, 0.18364692607912808, 0.53573812758362205], [0.67085689589720388, 0.26233333665862923, 0.66600141540809055], [0.5391908453759805, 0.18911547096806464, 0.79766746592931381], [0.50158905043341828, 0.06444160927035357, 0.83526926087187581], [0.50084473326653356, 0.0041368532328293741, 0.83601357803876042]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        createdCurves.append(mc.curve( d = 3,p = [[-0.71034804226541659, 1.444130000945939e-16, 0.37639989243615296], [-0.75185548636799693, 1.5744710508753383e-16, 0.41790733653873335], [-0.79336293047057771, 1.7048121008047389e-16, 0.45941478064131408], [-0.83487037457315849, 1.8351531507341399e-16, 0.50092222474389481], [-0.89052839954470242, 1.7477649054610858e-16, 0.44526419977235115], [-0.94618642451624635, 1.6603766601880319e-16, 0.38960617480080723], [-1.0018444494877898, 1.5729884149149766e-16, 0.33394814982926291], [-1.0018444494877898, 2.0973178865533029e-16, 0.55658024971543862], [-1.0018444494877903, 2.6216473581916287e-16, 0.77921234960161434], [-1.0018444494877898, 3.1459768298299532e-16, 1.0018444494877894], [-0.77921234960161467, 2.971200339283846e-16, 1.0018444494877898], [-0.55658024971543907, 2.7964238487377368e-16, 1.0018444494877898], [-0.33394814982926363, 2.6216473581916287e-16, 1.0018444494877898], [-0.38960617480080734, 2.5342591129185741e-16, 0.94618642451624579], [-0.44526419977235093, 2.446870867645519e-16, 0.89052839954470164], [-0.50092222474389514, 2.3594826223724659e-16, 0.83487037457315805], [-0.45772982604933232, 2.2238505034468735e-16, 0.79167797587859545], [-0.41453742735476956, 2.0882183845212819e-16, 0.74848557718403275], [-0.38172203677546457, 6.1993002843385494e-17, 0.70423931712785359], [-0.26481424742794457, 9.6559646198364555e-17, 0.76716375552260285], [-0.0031783262100260785, 1.6001941806647711e-16, 0.83567594934909839], [0.25845759500789239, 1.9745701588398112e-16, 0.76880833547598626], [0.37265034682111103, 1.3715897067272084e-16, 0.70659849665037444], [0.41540763946203901, 1.4387226094564649e-16, 0.74935578929130242], [0.45816493210296694, 1.5058555121857211e-16, 0.79211308193223051], [0.50092222474389492, 1.5729884149149773e-16, 0.83487037457315838], [0.44526419977235093, 1.747764905461086e-16, 0.89052839954470231], [0.38960617480080706, 1.9225413960071945e-16, 0.94618642451624613], [0.33394814982926307, 2.0973178865533029e-16, 1.0018444494877898], [0.55658024971543874, 1.9225413960071945e-16, 1.0018444494877898], [0.77921234960161434, 1.7477649054610858e-16, 1.0018444494877903], [1.0018444494877896, 1.5729884149149769e-16, 1.0018444494877898], [1.0018444494877898, 1.0486589432766514e-16, 0.77921234960161467], [1.0018444494877898, 5.2432947163832572e-17, 0.55658024971543907], [1.0018444494877898, 3.8746300180516809e-32, 0.33394814982926369], [0.94618642451624613, 1.747764905461088e-17, 0.3896061748008075], [0.89052839954470231, 3.4955298109221711e-17, 0.44526419977235138], [0.83487037457315805, 5.2432947163832572e-17, 0.50092222474389492], [0.79203060492095201, 4.5706707237564665e-17, 0.45808245509168877], [0.74919083526874586, 3.8980467311296777e-17, 0.41524268543948262], [0.70824785987373673, 2.0806017849916152e-16, 0.37418079886870681], [0.76863466079818266, 1.9755408097015749e-16, 0.25913624873453944], [0.83460199676406488, 1.6075046072444915e-16, 0.0016988602732966463], [0.76949960568300624, 9.8753133175290541e-17, -0.25573852818794651], [0.70869401511251184, -1.4389360498274727e-16, -0.37474586528324888], [0.75075280159939417, -1.5710084167963618e-16, -0.41680465177013093], [0.79281158808627628, -1.703080783765251e-16, -0.45886343825701298], [0.83487037457315827, -1.8351531507341406e-16, -0.50092222474389492], [0.89052839954470231, -1.747764905461086e-16, -0.44526419977235138], [0.94618642451624613, -1.6603766601880324e-16, -0.3896061748008075], [1.0018444494877898, -1.5729884149149776e-16, -0.33394814982926352], [1.0018444494877898, -2.0973178865533034e-16, -0.55658024971543896], [1.0018444494877898, -2.6216473581916297e-16, -0.77921234960161467], [1.0018444494877898, -3.1459768298299532e-16, -1.0018444494877894], [0.77921234960161467, -2.971200339283846e-16, -1.0018444494877898], [0.55658024971543907, -2.7964238487377368e-16, -1.0018444494877898], [0.33394814982926363, -2.6216473581916287e-16, -1.0018444494877898], [0.38960617480080734, -2.5342591129185741e-16, -0.94618642451624579], [0.44526419977235038, -2.4468708676455185e-16, -0.8905283995447012], [0.50092222474389514, -2.3594826223724659e-16, -0.83487037457315805], [0.45715292811589109, -2.2220389372574211e-16, -0.79110107794515416], [0.41338363148788737, -2.0845952521423771e-16, -0.74733178131715039], [0.3712329255875696, -6.5075646777795373e-17, -0.70978759552297921], [0.25692527558551659, -9.8467201032597699e-17, -0.76919879718237927], [-0.0013560887064098001, -1.6072603892040224e-16, -0.83481771441419972], [-0.25963745299833596, -1.9762570998075685e-16, -0.7685061049403874], [-0.37232195974284721, -1.3710741086520974e-16, -0.70627010957211067], [-0.41518871474319652, -1.4383788774063903e-16, -0.74913686457245987], [-0.45805546974354572, -1.5056836461606837e-16, -0.79200361957280918], [-0.50092222474389492, -1.5729884149149773e-16, -0.83487037457315838], [-0.44526419977235093, -1.747764905461086e-16, -0.89052839954470231], [-0.38960617480080706, -1.9225413960071945e-16, -0.94618642451624613], [-0.33394814982926307, -2.0973178865533029e-16, -1.0018444494877898], [-0.55658024971543874, -1.9225413960071945e-16, -1.0018444494877898], [-0.77921234960161434, -1.7477649054610858e-16, -1.0018444494877903], [-1.0018444494877896, -1.5729884149149769e-16, -1.0018444494877898], [-1.0018444494877898, -1.0486589432766519e-16, -0.77921234960161467], [-1.0018444494877898, -5.2432947163832572e-17, -0.55658024971543907], [-1.0018444494877898, -3.8746300180516815e-32, -0.33394814982926369], [-0.94618642451624613, -1.747764905461088e-17, -0.3896061748008075], [-0.89052839954470231, -3.4955298109221711e-17, -0.44526419977235138], [-0.83487037457315805, -5.2432947163832572e-17, -0.50092222474389492], [-0.79241734459615121, -4.5767428942315047e-17, -0.45846919476688786], [-0.7499643146191437, -3.9101910720797504e-17, -0.41601616478988057], [-0.70751128464213653, -3.2436392499279979e-17, -0.3735631348128734], [-0.76860559236731751, -1.9757029367260258e-16, -0.25924966340546224], [-0.83517618056509113, -1.6045196064212086e-16, 0.00042826386489417854], [-0.76838565165830874, -9.7699478325664099e-17, 0.26010619113525046], [-0.70756863740377807, -6.383430593347148e-17, 0.37547201684070014]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        return combineCurves(createdCurves)
    #>>> Rotate Arrows #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'arrowRotate90':
        createBuffer = mc.curve( d = 1,p = [[-0.24759352915673019, 0.0, 1.0018422500573196], [-0.7513599900081197, 0.0, 0.96622673281974136], [-0.4798577499277803, 0.0, 0.91767553979328176], [-0.56288928461748122, 0.0, 0.87426074502151085], [-0.71785307865927483, 0.0, 0.76418126061314073], [-0.89679955249355259, 0.0, 0.54308436653906378], [-1.0098220116315675, 0.0, 0.28192396057905139], [-1.0484377061907209, 0.0, 9.6728103576410825e-09], [-0.94857381569979737, 0.0, 8.751463989448422e-09], [-0.91366248209391021, 0.0, 0.25506339866153238], [-0.81136550894278781, 0.0, 0.4913820996985242], [-0.64952359634719303, 0.0, 0.69137616860832141], [-0.50925593717350848, 0.0, 0.79100730372518457], [-0.43414992022088045, 0.0, 0.83028280059470383], [-0.4920557095310803, 0.0, 0.55992855735930636], [-0.24759352915673019, 0.0, 1.0018422500573196]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0))
        return createBuffer
    elif desiredShape == 'arrowRotate90Fat':
        createBuffer = mc.curve( d = 1,p = [[-0.8392879912621396, 0.0, 0.0], [-1.0258996494064341, 0.0, 0.0], [-0.94775773319032253, 0.0, 0.39260382038955405], [-0.72538185523265886, 0.0, 0.72536731212855887], [-0.50983214676182753, 0.0, 0.86007554068475756], [-0.88705390773384918, 0.0, 0.94195594359851798], [-0.11325624106502201, 0.0, 0.99666255650184599], [-0.48875555314522651, 0.0, 0.31787226208484004], [-0.40064524801272422, 0.0, 0.71684687101410238], [-0.5933368326147318, 0.0, 0.59353861818411602], [-0.77553011394471316, 0.0, 0.32118263615555165], [-0.8392879912621396, 0.0, 0.0]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0))
        return createBuffer         
    elif desiredShape == 'arrowRotate180':
        createBuffer = mc.curve( d = 1,p = [[-0.24759352915673019, 0.0, -1.0018422500573196], [-0.7513599900081197, 0.0, -0.96622673281974136], [-0.4798577499277803, 0.0, -0.91767553979328176], [-0.56288928461748122, 0.0, -0.87426074502151085], [-0.71785307865927483, 0.0, -0.76418126061314073], [-0.89679955249355259, 0.0, -0.54308436653906378], [-1.0098220116315675, 0.0, -0.28192396057905139], [-1.0484377061907209, 0.0, 9.6728103576410825e-09], [-1.0098220116315675, 0.0, 0.28192396057905139], [-0.89679955249355259, 0.0, 0.54308436653906378], [-0.71785307865927483, 0.0, 0.76418126061314073], [-0.56288928461748122, 0.0, 0.87426074502151085], [-0.4798577499277803, 0.0, 0.91767553979328176], [-0.7513599900081197, 0.0, 0.96622673281974136], [-0.24759352915673019, 0.0, 1.0018422500573196], [-0.4920557095310803, 0.0, 0.55992855735930636], [-0.43414992022088045, 0.0, 0.83028280059470383], [-0.50925593717350848, 0.0, 0.79100730372518457], [-0.64952359634719303, 0.0, 0.69137616860832141], [-0.81136550894278781, 0.0, 0.4913820996985242], [-0.91366248209391021, 0.0, 0.25506339866153238], [-0.94857381569979737, 0.0, 8.751463989448422e-09], [-0.91366248209391021, 0.0, -0.25506339866153238], [-0.81136550894278781, 0.0, -0.4913820996985242], [-0.64952359634719303, 0.0, -0.69137616860832141], [-0.50925593717350848, 0.0, -0.79100730372518457], [-0.43414992022088045, 0.0, -0.83028280059470383], [-0.4920557095310803, 0.0, -0.55992855735930636], [-0.24759352915673019, 0.0, -1.0018422500573196]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0))
        return createBuffer          
    elif desiredShape == 'arrowRotate180Fat':
        createBuffer = mc.curve( d = 1,p = [[-0.11348769652446823, 0.0, -0.99869938014846105], [-0.88886673030183672, 0.0, -0.94388096639331931], [-0.50919181177888528, 0.0, -0.86003257437679836], [-0.72686427764927797, 0.0, -0.72684970482424793], [-0.94969461277873612, 0.0, -0.39340616290749469], [-1.0279962232682027, 0.0, 0.0], [-0.94969461277873612, 0.0, 0.39340616290749469], [-0.72686427764927797, 0.0, 0.72684970482424793], [-0.51087406226828924, 0.0, 0.86183322906957116], [-0.88886673030183672, 0.0, 0.94388096639331931], [-0.11348769652446823, 0.0, 0.99869938014846105], [-0.48975439559352185, 0.0, 0.31852187988756947], [-0.40146402434753553, 0.0, 0.71831185095978056], [-0.59454940198757866, 0.0, 0.59475159993487015], [-0.77711502155907053, 0.0, 0.3218390191850295], [-0.84100319729227568, 0.0, 0.0], [-0.77711502155907053, 0.0, -0.3218390191850295], [-0.59454940198757866, 0.0, -0.59475159993487015], [-0.40002313627269159, 0.0, -0.71550840374462898], [-0.48975439559352185, 0.0, -0.31852187988756947], [-0.11348769652446823, 0.0, -0.99869938014846105]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0))
        return createBuffer          
    #>>> Circle Arrows #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif desiredShape == 'circleArrow':
        createBuffer = mc.curve( d = 3,p = [[-0.55219578040888184, 1.0377328105612351e-16, -0.16968494102702086], [-0.59437710830861523, 1.1313941734483299e-16, -0.16968494102702086], [-0.63655843620834895, 1.2250555363354254e-16, -0.16968494102702086], [-0.67873976410808268, 1.3187168992225214e-16, -0.16968494102702089], [-0.67873976410808279, 1.2559208564024016e-16, -0.22624658803602771], [-0.67873976410808268, 1.1931248135822812e-16, -0.28280823504503461], [-0.67873976410808223, 1.1303287707621607e-16, -0.33936988205404151], [-0.79186305812609636, 1.5071050276828816e-16, -0.22624658803602779], [-0.90498635214411016, 1.8838812846036019e-16, -0.11312329401801406], [-1.0181096461621237, 2.2606575415243213e-16, -3.3909863122864832e-16], [-0.90498635214411016, 2.1350654558840822e-16, 0.11312329401801345], [-0.79186305812609648, 2.009473370243842e-16, 0.22624658803602729], [-0.67873976410808279, 1.8838812846036021e-16, 0.33936988205404106], [-0.67873976410808257, 1.8210852417834818e-16, 0.28280823504503416], [-0.67873976410808246, 1.7582891989633612e-16, 0.22624658803602732], [-0.67873976410808268, 1.6954931561432419e-16, 0.16968494102702045], [-0.63484612595467715, 1.5980297007182895e-16, 0.16968494102702045], [-0.59095248780127185, 1.5005662452933379e-16, 0.16968494102702045], [-0.55179610484118546, 4.4547355870772012e-17, 0.16387671476775656], [-0.52436621272306716, 6.9386490808024169e-17, 0.25525263936804532], [-0.42623664287790902, 1.1498784759386418e-16, 0.42300671574228249], [-0.25931820656500104, 1.41890012619431e-16, 0.5219719256487696], [-0.16968494102702078, 9.8560630993509103e-17, 0.54838535997749571], [-0.16968494102702075, 1.0338471302107808e-16, 0.59183682802102466], [-0.16968494102702078, 1.0820879504864711e-16, 0.63528829606455373], [-0.16968494102702081, 1.1303287707621612e-16, 0.67873976410808268], [-0.22624658803602768, 1.2559208564024013e-16, 0.67873976410808257], [-0.28280823504503466, 1.3815129420426415e-16, 0.67873976410808257], [-0.33936988205404156, 1.5071050276828814e-16, 0.67873976410808246], [-0.22624658803602768, 1.3815129420426412e-16, 0.79186305812609636], [-0.11312329401801403, 1.2559208564024013e-16, 0.90498635214411016], [-2.2606575415243223e-16, 1.1303287707621609e-16, 1.0181096461621237], [0.11312329401801349, 7.5355251384144069e-17, 0.90498635214411016], [0.22624658803602735, 3.7677625692072047e-17, 0.79186305812609659], [0.33936988205404106, 2.9125252480334737e-32, 0.67873976410808279], [0.28280823504503422, 1.255920856402402e-17, 0.67873976410808268], [0.22624658803602737, 2.5118417128048019e-17, 0.67873976410808268], [0.16968494102702053, 3.7677625692072028e-17, 0.67873976410808257], [0.16968494102702053, 3.284423821405891e-17, 0.63520448001824836], [0.16968494102702056, 2.8010850736045779e-17, 0.59166919592841416], [0.16974536189133063, 1.4950930571235312e-16, 0.55000108016341442], [0.25888512347974124, 1.4195976231275446e-16, 0.52222851440413998], [0.42321276422377091, 1.1551316522565672e-16, 0.42493920592099171], [0.52094156644823197, 7.0962701678239409e-17, 0.26105105891827463], [0.55051489970904188, -1.0340005056520143e-16, 0.16968494102702061], [0.59325652117538885, -1.1289059701755166e-16, 0.16968494102702061], [0.63599814264173571, -1.2238114346990191e-16, 0.16968494102702061], [0.67873976410808268, -1.3187168992225219e-16, 0.16968494102702056], [0.67873976410808279, -1.2559208564024018e-16, 0.22624658803602746], [0.67873976410808268, -1.1931248135822817e-16, 0.28280823504503427], [0.67873976410808257, -1.1303287707621612e-16, 0.33936988205404123], [0.79186305812609648, -1.5071050276828819e-16, 0.22624658803602746], [0.90498635214411016, -1.8838812846036021e-16, 0.11312329401801366], [1.0181096461621237, -2.2606575415243213e-16, 3.3909863122864832e-16], [0.90498635214411016, -2.1350654558840822e-16, -0.11312329401801345], [0.79186305812609648, -2.009473370243842e-16, -0.22624658803602729], [0.67873976410808279, -1.8838812846036021e-16, -0.33936988205404106], [0.67873976410808257, -1.8210852417834818e-16, -0.28280823504503416], [0.67873976410808179, -1.7582891989633607e-16, -0.22624658803602732], [0.67873976410808268, -1.6954931561432419e-16, -0.16968494102702045], [0.63425986193815487, -1.596727933098985e-16, -0.16968494102702045], [0.58977995976822695, -1.4979627100547284e-16, -0.16968494102702045], [0.54928558061311561, -4.6762503227256076e-17, -0.17202559508649323], [0.5213917276171387, -7.0757234604034111e-17, -0.26029520554705798], [0.42349654243875129, -1.1549561603871655e-16, -0.42487464758646476], [0.25856513126194303, -1.4201123397696634e-16, -0.52241786362745024], [0.16968494102702078, -9.8523580794478919e-17, -0.54805164145240304], [0.16968494102702075, -1.0336001288839132e-16, -0.59161434900429632], [0.16968494102702078, -1.0819644498230372e-16, -0.63517705655618939], [0.16968494102702081, -1.1303287707621612e-16, -0.67873976410808268], [0.22624658803602768, -1.2559208564024013e-16, -0.67873976410808257], [0.28280823504503466, -1.3815129420426415e-16, -0.67873976410808257], [0.33936988205404156, -1.5071050276828814e-16, -0.67873976410808246], [0.22624658803602768, -1.3815129420426412e-16, -0.79186305812609636], [0.11312329401801403, -1.2559208564024013e-16, -0.90498635214411016], [2.2606575415243213e-16, -1.1303287707621609e-16, -1.0181096461621237], [-0.11312329401801342, -7.5355251384144082e-17, -0.90498635214411016], [-0.22624658803602735, -3.7677625692072047e-17, -0.79186305812609659], [-0.33936988205404106, -2.9125252480334743e-32, -0.67873976410808279], [-0.28280823504503422, -1.255920856402402e-17, -0.67873976410808268], [-0.22624658803602737, -2.5118417128048019e-17, -0.67873976410808268], [-0.16968494102702053, -3.7677625692072028e-17, -0.67873976410808257], [-0.16968494102702053, -3.2887872031853292e-17, -0.63559749850936753], [-0.16968494102702056, -2.809811837163453e-17, -0.59245523291065216], [-0.16968494102702056, -2.3308364711415793e-17, -0.54931296731193702], [-0.25881272530434607, -1.4197141254733455e-16, -0.52227137221538211], [-0.42458534640036399, -1.1529866699545279e-16, -0.42415012956388376], [-0.52259483330098699, -7.0205559171852771e-17, -0.25826575271699059], [-0.55031204586490023, -4.5870492035465221e-17, -0.16874414637221255]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995))
        return createBuffer 
    elif desiredShape == 'circleArrow1':
        createBuffer = mc.curve( d = 3,p = [[-0.53379611622126366, -3.555951156255315e-17, 0.22112437487093103], [-0.562801501459258, -2.4299528858340043e-17, 0.15110494751893597], [-0.59022322788907011, -3.0089978004041808e-18, 0.018711245693910392], [-0.5520960149242895, -4.7689127538133229e-17, -0.16905309058459309], [-0.5513381068864277, -1.224216521237115e-16, -0.16993867772440255], [-0.55133810671648897, -1.2242165208597754e-16, -0.16993867772440255], [-0.52172055126444183, 4.2042986751522554e-17, -0.26144141903589652], [-0.44447473395336284, 6.843762089596378e-17, -0.40570669337991533], [-0.30962054214099377, 8.4106330015823374e-17, -0.48904307667937452], [-0.1807219201014359, 8.8579177661457815e-17, -0.55490521691233263], [0.026296000282851135, 3.7733966556797188e-17, -0.60858857380282416], [0.24729540700333069, 8.4065005695258112e-17, -0.54996744891751259], [0.40205287467249906, 6.8126388069260636e-17, -0.42777611080719835], [0.52515031855019434, 4.1109135430098219e-17, -0.25563432887637322], [0.55262122768604816, 2.6392792951745091e-17, -0.16412176619147922], [0.55262122844403772, 2.639279498171162e-17, -0.16412176630391492], [0.55314409779606399, 2.6503507047203568e-17, -0.16481021540679583], [0.58696561111369183, 5.7934815440344195e-20, -0.00036026366180456031], [0.55255717154850825, -2.6812021680836452e-17, 0.16672871118523133], [0.42522024569560052, -6.8310538010437782e-17, 0.42478437838167232], [0.25919973835194854, -8.4113232383497099e-17, 0.52305234554348645], [0.16993867772440235, 3.7733966556797188e-17, 0.55013437702166834], [0.16993867772440241, 3.7733966556797188e-17, 0.59334115498031559], [0.16993867772440241, 3.7733966556797188e-17, 0.63654793293896306], [0.16993867772440235, 3.7733966556797188e-17, 0.6797547108976103], [0.22658490363253658, 5.031195540906292e-17, 0.6797547108976103], [0.2832311295406707, 6.2889944261328627e-17, 0.6797547108976103], [0.33987735544880487, 7.5467933113594365e-17, 0.67975471089761041], [0.22658490363253653, 5.031195540906292e-17, 0.79304716271387876], [0.11329245181626792, 2.5155977704531448e-17, 0.90633961453014711], [-3.5127271397669697e-16, -5.1821597173285392e-64, 1.0196320663464153], [-0.11329245181626876, -2.5155977704531454e-17, 0.90633961453014711], [-0.22658490363253703, -5.0311955409062902e-17, 0.79304716271387876], [-0.33987735544880543, -7.5467933113594377e-17, 0.67975471089761019], [-0.2832311295406712, -6.2889944261328652e-17, 0.6797547108976103], [-0.22658490363253697, -5.0311955409062908e-17, 0.6797547108976103], [-0.1699386777244028, -3.7733966556797188e-17, 0.6797547108976103], [-0.1699386777244028, -3.7733966556797195e-17, 0.63612686228207094], [-0.16993867772440274, -3.7733966556797182e-17, 0.5924990136665319], [-0.1699386777244028, -3.7733966556797188e-17, 0.54887116505099232], [-0.25895177407224457, -8.4136825225917698e-17, 0.52319905601003802], [-0.41206405628896908, -6.9574762607701017e-17, 0.43264587201536664], [-0.50748987254753264, -4.573600874077237e-17, 0.28440622206253408], [-0.5364643111441304, -3.3896710492905544e-17, 0.21078436088019495]],k = (1.6323232779999994, 1.6323232779999994, 1.6323232779999994, 2.1323614440000007, 2.508560687000001, 2.508560687000001, 2.508560687000001, 2.508560687200001, 3.1190822461999996, 3.7377151422000008, 3.7377151422000008, 3.7377151422000008, 8.2503519831999999, 8.8673647371999973, 9.4995526522000002, 9.4995526522000002, 9.4995526522000002, 9.4995526572000024, 9.8696137562000015, 10.237290478200002, 10.858238904700002, 11.4771425542, 11.4771425542, 11.4771425542, 11.7313917842, 11.7313917842, 11.7313917842, 12.7313917842, 12.7313917842, 12.7313917842, 13.7313917842, 13.7313917842, 13.7313917842, 14.7313917842, 14.7313917842, 14.7313917842, 15.7313917842, 15.7313917842, 15.7313917842, 15.988118794199998, 15.988118794199998, 15.988118794199998, 16.607948209199996, 17.131222498200003, 17.131222498200003, 17.131222498200003))
        return createBuffer
    elif desiredShape == 'circleArrow2':
        createBuffer = mc.curve( d = 3,p = [[0.53298838857343522, -3.5505703751369228e-17, -0.22078977470100786], [0.56194988354906039, -2.426275938645436e-17, -0.15087629908908476], [0.58933011607152574, -3.0044446561571861e-18, -0.018682932279831567], [0.55126059630291202, -4.7616965479169511e-17, 0.16879728344949688], [0.55050383511355305, -1.2223640657750344e-16, 0.16968153053980869], [0.55050383494387145, -1.2223640653982658e-16, 0.16968153053980869], [0.52093109607567112, 4.1979368299149984e-17, 0.26104581206906863], [0.42320425809640605, 6.8334062707978852e-17, 0.42493066509398114], [0.25887992016353861, 8.397906230808494e-17, 0.52221801816529112], [0.16974195018972343, 8.8445141746536688e-17, 0.54999002572547162], [0.16968153053980869, -3.7676868411786475e-17, 0.59165730400557071], [0.16968153053980869, -3.7676868411786475e-17, 0.63519171308240274], [0.16968153053980867, -3.7676868411786475e-17, 0.67872612215923511], [0.22624204071974494, -5.0235824549048641e-17, 0.67872612215923511], [0.28280255089968115, -6.2794780686310783e-17, 0.67872612215923511], [0.33936306107961739, -7.5353736823572937e-17, 0.67872612215923522], [0.22624204071974491, -5.0235824549048641e-17, 0.79184714251910793], [0.11312102035987226, -2.5117912274524311e-17, 0.9049681628789803], [-2.2606121047071887e-16, 3.1909351193429582e-64, 1.0180891832388526], [-0.11312102035987279, 2.5117912274524317e-17, 0.9049681628789803], [-0.22624204071974516, 5.0235824549048622e-17, 0.79184714251910782], [-0.33936306107961772, 7.5353736823572949e-17, 0.678726122159235], [-0.28280255089968143, 6.2794780686310783e-17, 0.67872612215923511], [-0.22624204071974516, 5.0235824549048635e-17, 0.67872612215923511], [-0.16968153053980886, 3.7676868411786475e-17, 0.67872612215923511], [-0.16968153053980886, 3.7676868411786481e-17, 0.63527552744409488], [-0.16968153053980886, 3.7676868411786468e-17, 0.5918249327289542], [-0.16968153053980886, 3.7676868411786475e-17, 0.54837433801381374], [-0.25931299454428813, 8.3937800518503522e-17, 0.52196143456708266], [-0.42622807597379281, 6.802330083142226e-17, 0.42299821375627339], [-0.52435567351875134, 4.1046930059440467e-17, 0.25524750906091792], [-0.5517850143251517, 2.6352856002181938e-17, 0.16387342101972774], [-0.55178501508199429, 2.6352858029076772e-17, 0.16387342113199332], [-0.55230709324049354, 2.6463402567691831e-17, 0.16456082848998765], [-0.58607742864474244, 5.7847149848967728e-20, 0.00035971851935922173], [-0.55172105511584291, -2.6771450364283809e-17, -0.16647642124602294], [-0.42457681248500317, -6.820717212126711e-17, -0.42414160471517703], [-0.25880752344327002, -8.3985954231259287e-17, -0.52226087511513686], [-0.16968153053980867, 3.7676868411786475e-17, -0.54930192670433209], [-0.16968153053980869, 3.7676868411786475e-17, -0.59244332518929976], [-0.16968153053980869, 3.7676868411786475e-17, -0.63558472367426766], [-0.16968153053980867, 3.7676868411786475e-17, -0.67872612215923511], [-0.22624204071974494, 5.0235824549048641e-17, -0.67872612215923511], [-0.28280255089968115, 6.2794780686310783e-17, -0.67872612215923511], [-0.33936306107961739, 7.5353736823572937e-17, -0.67872612215923522], [-0.22624204071974491, 5.0235824549048641e-17, -0.79184714251910793], [-0.11312102035987218, 2.5117912274524305e-17, -0.9049681628789803], [2.2606121047071877e-16, -5.1743181959087513e-64, -1.0180891832388526], [0.11312102035987279, -2.5117912274524317e-17, -0.9049681628789803], [0.22624204071974519, -5.0235824549048622e-17, -0.79184714251910782], [0.33936306107961778, -7.5353736823572949e-17, -0.678726122159235], [0.28280255089968154, -6.2794780686310795e-17, -0.67872612215923511], [0.22624204071974519, -5.0235824549048635e-17, -0.67872612215923511], [0.16968153053980892, -3.7676868411786475e-17, -0.67872612215923511], [0.16968153053980892, -3.7676868411786481e-17, -0.63516429017152654], [0.16968153053980889, -3.7676868411786468e-17, -0.59160245818381807], [0.16968153053980892, -3.7676868411786475e-17, -0.54804062619610927], [0.25855993437724445, -8.4009511373549199e-17, -0.5224073635828832], [0.41144053071276776, -6.9469483723794637e-17, -0.43199120252279066], [0.50672195088494865, -4.5666802094941459e-17, -0.28397586529935548], [0.53565254604690238, -3.3845418792940827e-17, -0.21046540697468888]],k = (1.6323232779999994, 1.6323232779999994, 1.6323232779999994, 2.1323614440000007, 2.508560687000001, 2.508560687000001, 2.508560687000001, 2.508560687200001, 3.1190822461999996, 3.7377151422000008, 3.7377151422000008, 3.7377151422000008, 3.9942805382, 3.9942805382, 3.9942805382, 4.9942805382, 4.9942805382, 4.9942805382, 5.9942805382, 5.9942805382, 5.9942805382, 6.9942805382, 6.9942805382, 6.9942805382, 7.9942805382, 7.9942805382, 7.9942805382, 8.2503519831999999, 8.2503519831999999, 8.2503519831999999, 8.8673647371999973, 9.4995526522000002, 9.4995526522000002, 9.4995526522000002, 9.4995526572000024, 9.8696137562000015, 10.237290478200002, 10.858238904700002, 11.4771425542, 11.4771425542, 11.4771425542, 11.7313917842, 11.7313917842, 11.7313917842, 12.7313917842, 12.7313917842, 12.7313917842, 13.7313917842, 13.7313917842, 13.7313917842, 14.7313917842, 14.7313917842, 14.7313917842, 15.7313917842, 15.7313917842, 15.7313917842, 15.988118794199998, 15.988118794199998, 15.988118794199998, 16.607948209199996, 17.131222498200003, 17.131222498200003, 17.131222498200003))
        return createBuffer 
    elif desiredShape == 'circleArrow3':
        createBuffer = mc.curve( d = 3,p = [[0.16968494102702067, -4.291423286575584e-16, -0.55219578040888195], [-3.2202213538468491e-05, -4.3296992039450818e-16, -0.56540006232443529], [-0.16387671476775673, -5.2500168076658194e-16, -0.55179610484118535], [-0.25525263936804549, -4.8289934335482806e-16, -0.52436621272306705], [-0.4230067157422826, -3.5787129332073725e-16, -0.42623664287790897], [-0.52197192564876971, -1.7517145165655823e-16, -0.25931820656500093], [-0.54838535997749582, -1.3187168992225214e-16, -0.16968494102702067], [-0.59183682802102477, -1.3187168992225209e-16, -0.16968494102702061], [-0.63528829606455373, -1.3187168992225211e-16, -0.16968494102702064], [-0.67873976410808268, -1.3187168992225214e-16, -0.16968494102702067], [-0.67873976410808268, -1.7582891989633619e-16, -0.22624658803602754], [-0.67873976410808268, -2.197861498704203e-16, -0.2828082350450345], [-0.67873976410808257, -2.6374337984450438e-16, -0.33936988205404139], [-0.79186305812609648, -1.7582891989633617e-16, -0.22624658803602749], [-0.90498635214411016, -8.7914459948168146e-17, -0.11312329401801384], [-1.0181096461621237, -1.9580130366828994e-47, -1.9595792849759288e-32], [-0.90498635214411016, 8.7914459948168023e-17, 0.11312329401801369], [-0.79186305812609648, 1.7582891989633619e-16, 0.22624658803602754], [-0.67873976410808268, 2.6374337984450418e-16, 0.33936988205404123], [-0.67873976410808257, 2.1978614987042015e-16, 0.28280823504503433], [-0.67873976410808257, 1.7582891989633619e-16, 0.22624658803602754], [-0.67873976410808257, 1.3187168992225214e-16, 0.16968494102702067], [-0.63520448001824836, 1.3187168992225214e-16, 0.16968494102702067], [-0.59166919592841405, 1.3187168992225219e-16, 0.1696849410270207], [-0.55000108016341431, 2.5805660762131672e-16, 0.16974536189133071], [-0.52222851440413987, 3.4265895257014982e-16, 0.2588851234797413], [-0.4249392059209916, 4.9120993581855448e-16, 0.42321276422377097], [-0.2610510589182744, 5.6250540145646559e-16, 0.52094156644823209], [-0.16968494102702042, 4.2783602193933111e-16, 0.55051489970904199], [-0.16968494102702039, 4.6105293452255696e-16, 0.59325652117538885], [-0.16968494102702039, 4.9426984710578291e-16, 0.63599814264173582], [-0.16968494102702036, 5.2748675968900856e-16, 0.67873976410808268], [-0.22624658803602724, 5.2748675968900876e-16, 0.67873976410808279], [-0.28280823504503405, 5.2748675968900856e-16, 0.67873976410808268], [-0.33936988205404101, 5.2748675968900866e-16, 0.67873976410808268], [-0.22624658803602721, 6.1540121963717662e-16, 0.79186305812609648], [-0.11312329401801335, 7.0331567958534478e-16, 0.90498635214411016], [-1.5475391152103335e-32, 7.9123013953351264e-16, 1.0181096461621237], [0.11312329401801374, 7.0331567958534478e-16, 0.90498635214411016], [0.22624658803602754, 6.1540121963717662e-16, 0.79186305812609648], [0.33936988205404128, 5.2748675968900856e-16, 0.67873976410808268], [0.28280823504503438, 5.2748675968900846e-16, 0.67873976410808257], [0.22624658803602754, 5.2748675968900787e-16, 0.67873976410808179], [0.16968494102702067, 5.2748675968900856e-16, 0.67873976410808268], [0.16968494102702067, 4.9291893162351866e-16, 0.63425986193815476], [0.16968494102702067, 4.5835110355802887e-16, 0.58977995976822695], [0.1720255950864934, 5.2118272324388136e-16, 0.5492855806131155], [0.26029520554705815, 4.7911632920042582e-16, 0.52139172761713859], [0.42487464758646487, 3.5483299663246441e-16, 0.42349654243875123], [0.52241786362745035, 1.7434726597351311e-16, 0.25856513126194292], [0.54805164145240315, 1.3187168992225214e-16, 0.16968494102702067], [0.59161434900429644, 1.3187168992225209e-16, 0.16968494102702061], [0.6351770565561895, 1.3187168992225211e-16, 0.16968494102702064], [0.67873976410808268, 1.3187168992225214e-16, 0.16968494102702067], [0.67873976410808268, 1.7582891989633619e-16, 0.22624658803602754], [0.67873976410808268, 2.197861498704203e-16, 0.2828082350450345], [0.67873976410808257, 2.6374337984450438e-16, 0.33936988205404139], [0.79186305812609648, 1.7582891989633617e-16, 0.22624658803602749], [0.90498635214411016, 8.7914459948168146e-17, 0.11312329401801384], [1.0181096461621237, -3.2450803497634904e-47, -3.2476761453293716e-32], [0.90498635214411016, -8.7914459948167962e-17, -0.11312329401801362], [0.79186305812609648, -1.7582891989633619e-16, -0.22624658803602754], [0.67873976410808268, -2.6374337984450418e-16, -0.33936988205404123], [0.67873976410808257, -2.1978614987042015e-16, -0.28280823504503433], [0.67873976410808257, -1.7582891989633619e-16, -0.22624658803602754], [0.67873976410808257, -1.3187168992225214e-16, -0.16968494102702067], [0.63559749850936742, -1.3187168992225214e-16, -0.16968494102702067], [0.59245523291065205, -1.3187168992225219e-16, -0.1696849410270207], [0.54931296731193691, -1.3187168992225214e-16, -0.16968494102702067], [0.522271372215382, -3.4259350432270919e-16, -0.25881272530434613], [0.42415012956388359, -4.9245452776441485e-16, -0.42458534640036405], [0.25826575271699037, -5.6370943549080899e-16, -0.5225948333009871], [0.16874414637221236, -5.7700832202115915e-16, -0.55031204586490023]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995))
        return createBuffer
    elif desiredShape == 'circleArrow1Interior':    
        createBuffer = mc.curve( d = 3,p = [[-2.3768126169586723, -1.5833441489433829e-16, 0.9845916598847505], [-2.5059637357068563, -1.0819754026219571e-16, 0.67281895621551124], [-2.6280633602199543, -1.3398044157812938e-17, 0.083314815325229746], [-2.4582958439898488, -2.123434708119949e-16, -0.75273593498901537], [-2.4549211371829944, -5.451019940279056e-16, -0.75667915342645153], [-2.4549211364263153, -5.4510199385988907e-16, -0.75667915342645153], [-2.323044231850413, 1.8720312555482081e-16, -1.1641097499153075], [-1.9790948706374627, 3.0472945732848938e-16, -1.806473966944822], [-1.3786350043904332, 3.7449689173990914e-16, -2.1775425477356092], [-0.80469326547149367, 3.944129615553574e-16, -2.4708042653250035], [0.11708714872313274, 1.6801652367758338e-16, -2.7098380014287073], [1.1011223679226028, 3.7431288859053806e-16, -2.4488180632657173], [1.790204754524652, 3.0334364336911409e-16, -1.9047415792336126], [2.3383158194665161, 1.8304500312628513e-16, -1.1382527518227046], [2.4606344378476921, 1.1751813356859091e-16, -0.73077842409732652], [2.4606344412227621, 1.1751814260734171e-16, -0.73077842459796438], [2.462962600673817, 1.1801110579331165e-16, -0.73384385438311284], [2.6135583002960532, 2.5796403554705499e-19, -0.0016041315977906674], [2.4603492176460611, -1.1938481656312e-16, 0.74238626380348771], [1.8933611808757289, -3.0416360044692208e-16, 1.8914204119199738], [1.1541283079922804, -3.745276256363825e-16, 2.3289742589701929], [0.75667915342645042, 1.6801652367758338e-16, 2.449561337358626], [0.75667915342645042, 1.6801652367758338e-16, 2.6419464294743515], [0.75667915342645042, 1.6801652367758338e-16, 2.8343315215900784], [0.75667915342644909, 1.6801652367758338e-16, 4.380951737356547], [1.0089055379019332, 2.2402203157011119e-16, 4.380951737356547], [1.2611319223774169, 2.8002753946263888e-16, 4.380951737356547], [1.5133583068529008, 3.3603304735516667e-16, 4.380951737356547], [1.0089055379019329, 2.2402203157011119e-16, 4.8854045063075127], [0.5044527689509638, 1.1201101578505555e-16, 5.3898572752584801], [-2.8419415788181005e-15, -2.3074395307394695e-63, 5.8943100442094467], [-0.5044527689509698, -1.1201101578505555e-16, 5.3898572752584792], [-1.0089055379019372, -2.240220315701111e-16, 4.8854045063075127], [-1.5133583068529051, -3.3603304735516677e-16, 4.3809517373565452], [-1.2611319223774207, -2.8002753946263903e-16, 4.3809517373565461], [-1.0089055379019367, -2.240220315701111e-16, 4.3809517373565461], [-0.75667915342645287, -1.6801652367758338e-16, 4.3809517373565461], [-0.75667915342645364, -1.6801652367758341e-16, 2.8324566371173008], [-0.75667915342645331, -1.6801652367758333e-16, 2.6381966605287985], [-0.75667915342645353, -1.6801652367758338e-16, 2.4439366839402945], [-1.153024207361637, -3.7463267654220798e-16, 2.329627510796767], [-1.8347811425005203, -3.0979276274715737e-16, 1.926424970193978], [-2.2596798578986648, -2.0364689686003645e-16, 1.2663642098504506], [-2.3886931817744452, -1.5093052707700432e-16, 0.93855109314798635]],k = (1.6323232779999994, 1.6323232779999994, 1.6323232779999994, 2.1323614440000007, 2.508560687000001, 2.508560687000001, 2.508560687000001, 2.508560687200001, 3.1190822461999996, 3.7377151422000008, 3.7377151422000008, 3.7377151422000008, 8.2503519831999999, 8.8673647371999973, 9.4995526522000002, 9.4995526522000002, 9.4995526522000002, 9.4995526572000024, 9.8696137562000015, 10.237290478200002, 10.858238904700002, 11.4771425542, 11.4771425542, 11.4771425542, 11.7313917842, 11.7313917842, 11.7313917842, 12.7313917842, 12.7313917842, 12.7313917842, 13.7313917842, 13.7313917842, 13.7313917842, 14.7313917842, 14.7313917842, 14.7313917842, 15.7313917842, 15.7313917842, 15.7313917842, 15.988118794199998, 15.988118794199998, 15.988118794199998, 16.607948209199996, 17.131222498200003, 17.131222498200003, 17.131222498200003))
        return createBuffer 
    elif desiredShape == 'circleArrow2Axis':  
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[-3.2784008818290875, -2.1839487122788093e-16, 1.3580734732627262], [-3.4565424562099261, -1.4923974606850079e-16, 0.92803708783350591], [-3.6249577169749707, -1.8480278785276574e-17, 0.1149183415145134], [-3.3907928648770023, -2.9289099906052822e-16, -1.038268702986838], [-3.3861380419883291, -7.5187368375491722e-16, -1.0437076890938191], [-3.3861380409446213, -7.5187368352316764e-16, -1.0437076890938191], [-3.2042367176473099, 2.5821425194443848e-16, -1.6056875512347324], [-2.7298182123517813, 4.2032144835353298e-16, -2.491717607007375], [-1.9015879425519864, 5.1655352692185749e-16, -3.0035423734208981], [-1.1099348313369981, 5.4402429192018657e-16, -3.4080460632330181], [0.16150141954225683, 2.3174966148205426e-16, -3.7377516553516035], [1.5188073793626966, 5.1629972648220424e-16, -3.3777199097512729], [2.4692770494453722, 4.1840995828736171e-16, -2.6272607392190515], [3.2253012247735078, 2.5247884304463719e-16, -1.570022305794933], [3.3940185496075066, 1.6209588840670333e-16, -1.0079821239959388], [3.3940185542628303, 1.6209590087409278e-16, -1.007982124686482], [3.3972298465384259, 1.6277585811264914e-16, -1.0122103535502598], [3.6049505018894372, 3.5581665781453619e-19, -0.0022126213935603129], [3.3936251377946145, -1.6467065392742419e-16, 1.0239931261495308], [2.6115634529686118, -4.1954094690117488e-16, 2.6088864987103872], [1.5919198828165741, -5.1659591900299223e-16, 3.2124161618323717], [1.0437076890938166, 2.3174966148205426e-16, 3.3787451274837292], [1.0437076890938166, 2.3174966148205426e-16, 3.6441070037809102], [1.0437076890938166, 2.3174966148205426e-16, 3.9094688800780926], [1.0437076890938164, 2.3174966148205426e-16, 4.1748307563752736], [1.3916102521250895, 3.0899954864273905e-16, 4.1748307563752736], [1.7395128151563619, 3.8624943580342364e-16, 4.1748307563752736], [2.087415378187635, 4.6349932296410843e-16, 4.1748307563752745], [1.391610252125089, 3.0899954864273905e-16, 4.8706358824378198], [0.69580512606254163, 1.5449977432136945e-16, 5.5664410085003651], [-3.6912098741419318e-15, -3.1827127382146156e-63, 6.2622461345629103], [-0.69580512606254952, -1.5449977432136948e-16, 5.5664410085003651], [-1.3916102521250944, -3.0899954864273895e-16, 4.8706358824378198], [-2.0874153781876399, -4.6349932296410853e-16, 4.1748307563752727], [-1.7395128151563666, -3.8624943580342384e-16, 4.1748307563752736], [-1.3916102521250939, -3.0899954864273895e-16, 4.1748307563752736], [-1.0437076890938211, -2.3174966148205426e-16, 4.1748307563752736], [-1.0437076890938211, -2.3174966148205431e-16, 3.9068828020402089], [-1.0437076890938206, -2.3174966148205421e-16, 3.638934847705146], [-1.0437076890938208, -2.3174966148205426e-16, 3.37098689337008], [-1.590396967440199, -5.1674081851246051e-16, 3.213317209457673], [-2.5307624474132777, -4.2730540023560083e-16, 2.6571692172952357], [-3.1168365507356364, -2.8089558322102695e-16, 1.7467298484820797], [-3.2947880609826958, -2.0818249176804344e-16, 1.2945684945728797]],k = (1.6323232779999994, 1.6323232779999994, 1.6323232779999994, 2.1323614440000007, 2.508560687000001, 2.508560687000001, 2.508560687000001, 2.508560687200001, 3.1190822461999996, 3.7377151422000008, 3.7377151422000008, 3.7377151422000008, 8.2503519831999999, 8.8673647371999973, 9.4995526522000002, 9.4995526522000002, 9.4995526522000002, 9.4995526572000024, 9.8696137562000015, 10.237290478200002, 10.858238904700002, 11.4771425542, 11.4771425542, 11.4771425542, 11.7313917842, 11.7313917842, 11.7313917842, 12.7313917842, 12.7313917842, 12.7313917842, 13.7313917842, 13.7313917842, 13.7313917842, 14.7313917842, 14.7313917842, 14.7313917842, 15.7313917842, 15.7313917842, 15.7313917842, 15.988118794199998, 15.988118794199998, 15.988118794199998, 16.607948209199996, 17.131222498200003, 17.131222498200003, 17.131222498200003)))
        createdCurves.append(mc.curve( d = 3,p = [[0.98459165988474995, -1.5833441489433829e-16, 2.3768126169586723], [0.67281895621551069, -1.0819754026219571e-16, 2.5059637357068563], [0.083314815325229163, -1.3398044157812938e-17, 2.6280633602199543], [-0.75273593498901592, -2.123434708119949e-16, 2.4582958439898488], [-0.75667915342645209, -5.451019940279056e-16, 2.4549211371829944], [-0.75667915342645209, -5.4510199385988907e-16, 2.4549211364263153], [-1.1641097499153079, 1.8720312555482081e-16, 2.3230442318504125], [-1.8064739669448224, 3.0472945732848938e-16, 1.9790948706374623], [-2.1775425477356096, 3.7449689173990914e-16, 1.3786350043904327], [-2.4708042653250035, 3.944129615553574e-16, 0.80469326547149311], [-2.7098380014287073, 1.6801652367758338e-16, -0.11708714872313333], [-2.4488180632657168, 3.7431288859053806e-16, -1.1011223679226032], [-1.9047415792336122, 3.0334364336911409e-16, -1.7902047545246524], [-1.1382527518227041, 1.8304500312628513e-16, -2.3383158194665166], [-0.73077842409732596, 1.1751813356859091e-16, -2.4606344378476921], [-0.73077842459796383, 1.1751814260734171e-16, -2.4606344412227621], [-0.73384385438311228, 1.1801110579331165e-16, -2.462962600673817], [-0.0016041315977900871, 2.5796403554705499e-19, -2.6135583002960532], [0.74238626380348827, -1.1938481656312e-16, -2.4603492176460611], [1.8914204119199742, -3.0416360044692208e-16, -1.8933611808757285], [2.3289742589701934, -3.745276256363825e-16, -1.1541283079922799], [2.449561337358626, 1.6801652367758338e-16, -0.75667915342644987], [2.6419464294743515, 1.6801652367758338e-16, -0.75667915342644987], [2.8343315215900784, 1.6801652367758338e-16, -0.75667915342644976], [4.380951737356547, 1.6801652367758338e-16, -0.75667915342644809], [4.380951737356547, 2.2402203157011119e-16, -1.0089055379019323], [4.380951737356547, 2.8002753946263888e-16, -1.261131922377416], [4.380951737356547, 3.3603304735516667e-16, -1.5133583068529], [4.8854045063075127, 2.2402203157011119e-16, -1.0089055379019318], [5.3898572752584801, 1.1201101578505555e-16, -0.50445276895096258], [5.8943100442094467, -2.3074395307394695e-63, 4.1507413238902311e-15], [5.3898572752584792, -1.1201101578505555e-16, 0.50445276895097102], [4.8854045063075127, -2.240220315701111e-16, 1.0089055379019383], [4.3809517373565452, -3.3603304735516677e-16, 1.513358306852906], [4.3809517373565461, -2.8002753946263903e-16, 1.2611319223774216], [4.3809517373565461, -2.240220315701111e-16, 1.0089055379019376], [4.3809517373565461, -1.6801652367758338e-16, 0.75667915342645387], [2.8324566371173008, -1.6801652367758341e-16, 0.75667915342645431], [2.6381966605287985, -1.6801652367758333e-16, 0.75667915342645387], [2.4439366839402945, -1.6801652367758338e-16, 0.75667915342645409], [2.3296275107967666, -3.7463267654220798e-16, 1.1530242073616375], [1.9264249701939775, -3.0979276274715737e-16, 1.8347811425005207], [1.2663642098504502, -2.0364689686003645e-16, 2.2596798578986652], [0.93855109314798579, -1.5093052707700432e-16, 2.3886931817744452]],k = (1.6323232779999994, 1.6323232779999994, 1.6323232779999994, 2.1323614440000007, 2.508560687000001, 2.508560687000001, 2.508560687000001, 2.508560687200001, 3.1190822461999996, 3.7377151422000008, 3.7377151422000008, 3.7377151422000008, 8.2503519831999999, 8.8673647371999973, 9.4995526522000002, 9.4995526522000002, 9.4995526522000002, 9.4995526572000024, 9.8696137562000015, 10.237290478200002, 10.858238904700002, 11.4771425542, 11.4771425542, 11.4771425542, 11.7313917842, 11.7313917842, 11.7313917842, 12.7313917842, 12.7313917842, 12.7313917842, 13.7313917842, 13.7313917842, 13.7313917842, 14.7313917842, 14.7313917842, 14.7313917842, 15.7313917842, 15.7313917842, 15.7313917842, 15.988118794199998, 15.988118794199998, 15.988118794199998, 16.607948209199996, 17.131222498200003, 17.131222498200003, 17.131222498200003)))
        return combineCurves(createdCurves)
    elif desiredShape == 'masterAnim':  
        createdCurves = []
        createdCurves.append(mc.curve( d = 3,p = [[-0.27118683226552831, 5.0963713164509079e-17, -0.083333345296857], [-0.29190234857282799, 5.5563481798781466e-17, -0.083333345296857], [-0.31261786488012783, 6.0163250433053878e-17, -0.083333345296857], [-0.33333338118742767, 6.4763019067326327e-17, -0.083333345296857014], [-0.33333338118742772, 6.1679065778406027e-17, -0.11111112706247596], [-0.33333338118742767, 5.8595112489485727e-17, -0.1388889088280949], [-0.33333338118742745, 5.551115920056539e-17, -0.16666669059371389], [-0.38888894471866553, 7.401487893408724e-17, -0.111111127062476], [-0.44444450824990345, 9.2518598667609029e-17, -0.05555556353123807], [-0.50000007178114136, 1.1102231840113078e-16, -1.6653347760169626e-16], [-0.44444450824990345, 1.0485441182329023e-16, 0.055555563531237771], [-0.38888894471866559, 9.8686505245449629e-17, 0.11111112706247575], [-0.33333338118742772, 9.2518598667609041e-17, 0.1666666905937137], [-0.33333338118742761, 8.9434645378688741e-17, 0.13888890882809471], [-0.33333338118742756, 8.6350692089768391e-17, 0.11111112706247576], [-0.33333338118742767, 8.326673880084814e-17, 0.083333345296856792], [-0.31177693850940258, 7.8480247002816963e-17, 0.083333345296856792], [-0.2902204958313776, 7.3693755204785823e-17, 0.083333345296856792], [-0.27099054907217029, 2.1877487574161723e-17, 0.080480888729432626], [-0.25751955596282483, 3.4076143483595905e-17, 0.12535618190776401], [-0.20932750498738548, 5.6471257558182193e-17, 0.20774126738935378], [-0.1273528076130323, 6.9683080562273015e-17, 0.25634370647202959], [-0.083333345296856959, 4.8403747825508506e-17, 0.26931551074687732], [-0.083333345296856945, 5.0772884950527465e-17, 0.29065480089372742], [-0.083333345296856959, 5.3142022075546449e-17, 0.31199409104057757], [-0.083333345296856973, 5.5511159200565415e-17, 0.33333338118742767], [-0.11111112706247595, 6.1679065778406015e-17, 0.33333338118742761], [-0.13888890882809493, 6.7846972356246628e-17, 0.33333338118742761], [-0.16666669059371392, 7.4014878934087228e-17, 0.33333338118742756], [-0.11111112706247595, 6.7846972356246615e-17, 0.38888894471866553], [-0.055555563531238056, 6.1679065778406015e-17, 0.44444450824990345], [-1.1102231840113083e-16, 5.5511159200565415e-17, 0.50000007178114136], [0.055555563531237792, 3.7007439467043614e-17, 0.44444450824990345], [0.11111112706247578, 1.8503719733521813e-17, 0.38888894471866564], [0.1666666905937137, 1.430359528141852e-32, 0.33333338118742772], [0.13888890882809474, 6.1679065778406064e-18, 0.33333338118742767], [0.11111112706247578, 1.2335813155681201e-17, 0.33333338118742767], [0.083333345296856848, 1.8503719733521804e-17, 0.33333338118742761], [0.083333345296856848, 1.613001264306978e-17, 0.31195292845133471], [0.083333345296856862, 1.3756305552617758e-17, 0.29057247571524186], [0.083363018364591743, 7.3424963480034861e-17, 0.2701090011258192], [0.12714011777698825, 6.9717335076803856e-17, 0.25646971882893732], [0.20784245909883511, 5.6729244362053745e-17, 0.20869032551066052], [0.25583769056679662, 3.4850230588281228e-17, 0.12820382233849828], [0.27036134114701899, -5.0780417315230547e-17, 0.083333345296856889], [0.29135202116048853, -5.5441284565929143e-17, 0.083333345296856889], [0.31234270117395807, -6.0102151816627732e-17, 0.083333345296856889], [0.33333338118742767, -6.4763019067326352e-17, 0.083333345296856862], [0.33333338118742772, -6.167906577840604e-17, 0.11111112706247582], [0.33333338118742767, -5.8595112489485739e-17, 0.13888890882809476], [0.33333338118742761, -5.5511159200565415e-17, 0.16666669059371378], [0.38888894471866559, -7.4014878934087252e-17, 0.11111112706247582], [0.44444450824990345, -9.2518598667609041e-17, 0.055555563531237882], [0.50000007178114136, -1.1102231840113078e-16, 1.6653347760169626e-16], [0.44444450824990345, -1.0485441182329023e-16, -0.055555563531237771], [0.38888894471866559, -9.8686505245449629e-17, -0.11111112706247575], [0.33333338118742772, -9.2518598667609041e-17, -0.1666666905937137], [0.33333338118742761, -8.9434645378688741e-17, -0.13888890882809471], [0.33333338118742717, -8.6350692089768367e-17, -0.11111112706247576], [0.33333338118742767, -8.326673880084814e-17, -0.083333345296856792], [0.31148902055140182, -7.8416316373581875e-17, -0.083333345296856792], [0.28964465991537602, -7.3565893946315622e-17, -0.083333345296856792], [0.26975761478166921, -2.2965360419118022e-17, -0.084482855275632554], [0.25605876755748702, -3.4749324411585448e-17, -0.12783261797825182], [0.2079818243709303, -5.6720625845607256e-17, -0.20865862050519357], [0.12698296757958893, -6.9742613135898617e-17, -0.25656270942735054], [0.083333345296856959, -4.8385552238967876e-17, -0.26915161947334887], [0.083333345296856945, -5.0760754559500389e-17, -0.29054554004470851], [0.083333345296856959, -5.3135956880032902e-17, -0.31193946061606803], [0.083333345296856973, -5.5511159200565415e-17, -0.33333338118742767], [0.11111112706247595, -6.1679065778406015e-17, -0.33333338118742761], [0.13888890882809493, -6.7846972356246628e-17, -0.33333338118742761], [0.16666669059371392, -7.4014878934087228e-17, -0.33333338118742756], [0.11111112706247595, -6.7846972356246615e-17, -0.38888894471866553], [0.055555563531238056, -6.1679065778406015e-17, -0.44444450824990345], [1.1102231840113078e-16, -5.5511159200565415e-17, -0.50000007178114136], [-0.055555563531237757, -3.700743946704362e-17, -0.44444450824990345], [-0.11111112706247578, -1.8503719733521813e-17, -0.38888894471866564], [-0.1666666905937137, -1.4303595281418523e-32, -0.33333338118742772], [-0.13888890882809474, -6.1679065778406064e-18, -0.33333338118742767], [-0.11111112706247578, -1.2335813155681201e-17, -0.33333338118742767], [-0.083333345296856848, -1.8503719733521804e-17, -0.33333338118742761], [-0.083333345296856848, -1.6151441486329952e-17, -0.31214594231237774], [-0.083333345296856862, -1.3799163239138094e-17, -0.29095850343732776], [-0.083333345296856862, -1.1446884991946246e-17, -0.26977106456227795], [-0.12710456257619937, -6.9723056580522298e-17, -0.25649076657048286], [-0.2085165428671297, -5.6623902927657973e-17, -0.20830280513239677], [-0.25664962035075162, -3.4478393125618012e-17, -0.12683594088700212], [-0.27026171834409768, -2.2527288093994418e-17, -0.08287131510520851]],k = (15.745750770000001, 15.745750770000001, 15.745750770000001, 15.994336930000003, 15.994336930000003, 15.994336930000003, 16.994336930000003, 16.994336930000003, 16.994336930000003, 17.994336930000003, 17.994336930000003, 17.994336930000003, 18.994336930000003, 18.994336930000003, 18.994336930000003, 19.994336930000003, 19.994336930000003, 19.994336930000003, 20.253014204999999, 20.253014204999999, 20.253014204999999, 20.885202120000002, 21.502214874, 21.502214874, 21.502214874, 21.758286319, 21.758286319, 21.758286319, 22.758286319, 22.758286319, 22.758286319, 23.758286319, 23.758286319, 23.758286319, 24.758286319, 24.758286319, 24.758286319, 25.758286319, 25.758286319, 25.758286319, 26.014851714999999, 26.014851714999999, 26.014851714999999, 26.633484611, 27.244006168999999, 27.244006168999999, 27.244006168999999, 27.495894292999999, 27.495894292999999, 27.495894292999999, 28.495894292999999, 28.495894292999999, 28.495894292999999, 29.495894292999999, 29.495894292999999, 29.495894292999999, 30.495894292999999, 30.495894292999999, 30.495894292999999, 31.495894292999999, 31.495894292999999, 31.495894292999999, 31.758026582999999, 31.758026582999999, 31.758026582999999, 32.371381249000002, 32.991210664, 32.991210664, 32.991210664, 33.247937673999999, 33.247937673999999, 33.247937673999999, 34.247937673999999, 34.247937673999999, 34.247937673999999, 35.247937673999999, 35.247937673999999, 35.247937673999999, 36.247937673999999, 36.247937673999999, 36.247937673999999, 37.247937673999999, 37.247937673999999, 37.247937673999999, 37.502186903999998, 37.502186903999998, 37.502186903999998, 38.121090553499997, 38.742038981499995, 38.742038981499995, 38.742038981499995)))
        createdCurves.append(mc.curve( d = 3,p = [[1.4057201132611796e-17, 1.4057201132611796e-17, -0.22957151633269232], [-0.058414534874067073, 1.4057201132611796e-17, -0.22957151633269232], [-0.18004261502304847, 1.1033111110977267e-17, -0.18018437836376902], [-0.25409126930803444, 6.7934389616067828e-20, -0.001109452777133234], [-0.18100829360871529, -1.0936833172124684e-17, 0.17861204029993519], [-0.0022188513895999916, -1.5568639958856005e-17, 0.2542551855717991], [0.1778635152469584, -1.1128602257249335e-17, 0.18174386712964916], [0.25407193259778965, -2.0361101996689876e-19, 0.0033252203020276649], [0.18315984466557828, 1.0839027870971301e-17, -0.17701475851678794], [0.062412213466930301, 1.3992635361726024e-17, -0.22851707727433315], [0.0040065754094616955, 1.405506015279172e-17, -0.22953655147880028]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        return combineCurves(createdCurves)    
    else:
        return ('desiredShape not found')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

