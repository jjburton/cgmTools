#=================================================================================================================================================
#=================================================================================================================================================
#	controlBuilder - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for making stuff you can grab to make other stuff move!
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
#   0.11 - 04/04/2011 - added cvListSimplifier
#
# FUNCTION KEY:
#   1) ????
#   2) ????
#   3) ????
#   
#=================================================================================================================================================
import maya.cmds as mc
from cgm.lib.classes.ObjectFactory import *
from cgm.lib.classes.ControlFactory import *

from cgm.lib import search
from cgm.lib import locators
from cgm.lib import distance
from cgm.lib import position
from cgm.lib import names
from cgm.lib import attributes
from cgm.lib import rigging
from cgm.lib.classes import NameFactory 
from cgm.lib import constraints
from cgm.lib import curves
from cgm.lib import dictionary
from cgm.lib import settings
from cgm.lib import lists
from cgm.lib import modules
from cgm.lib import settings

import re
import math

typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
namesDictionary = dictionary.initializeDictionary( settings.getNamesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Joysticks
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def createJoystickControl(name,mode='classic',border = True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates traditional joystick style controls
    
    ARGUMENTS:
    name(string)
    mode(string) - (4point)
            classic
            horizontalSlider
            verticalSlide
    
    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ make the base transform"""
    controlTransform = mc.group( em=True)
    attributes.storeInfo(controlTransform,'cgmName', name)
    attributes.storeInfo(controlTransform,'cgmType', 'joystickControlTransform')
    controlTransform = NameFactory.doNameObject(controlTransform)

    if border == True:
        """ make the base border square"""
        #borderBuffer = curves.createControlCurve('square',2)
        borderBuffer = curves.createControlCurve('squareRounded',2.25)
        attributes.storeInfo(borderBuffer,'cgmName', name)
        attributes.storeInfo(borderBuffer,'cgmType', 'borderCurve')
        borderBuffer = NameFactory.doNameObject(borderBuffer)
        
        borderBuffer = rigging.doParentReturnName(borderBuffer,controlTransform)
        shapes = mc.listRelatives(borderBuffer, shapes = True)
        for shape in shapes:
            attributes.doSetAttr(shape, 'overrideEnabled', 1)
            attributes.doSetAttr(shape, 'overrideDisplayType', 1)

    """ make the joystick"""
    controlBuffer = curves.createControlCurve('circle',.25)
    attributes.storeInfo(controlBuffer,'cgmName', name)
    attributes.storeInfo(controlBuffer,'cgmType', 'controlAnim')
    controlBuffer = NameFactory.doNameObject(controlBuffer)
    
    if mode == 'classic':
        """ parent control to transform """
        controlBuffer = rigging.doParentReturnName(controlBuffer,controlTransform)
        
        """ set limits and lock and hide un-needed stuff"""
        attributes.doSetLockHideKeyableAttr(controlBuffer,True,False,False,['tz','rx','ry','rz','sx','sy','sz','v'])
        mc.transformLimits(controlBuffer, tx = [-1,1], ty = [-1,1], etx = [1,1], ety = [1,1])
        
        return [controlBuffer,controlTransform]
        
    elif mode == 'horizontalSlider':
        mc.xform(controlTransform,scale = [1,.15,1],ws=True)
        mc.makeIdentity(controlTransform, apply=True, s=True)

        """ parent control to transform """
        controlBuffer = rigging.doParentReturnName(controlBuffer,controlTransform)
        
        """ set limits and lock and hide un-needed stuff"""
        attributes.doSetLockHideKeyableAttr(controlBuffer,True,False,False,['ty','tz','rx','ry','rz','sx','sy','sz','v'])
        mc.transformLimits(controlBuffer, tx = [-1,1],  etx = [1,1])
        
        return [controlBuffer,controlTransform]
        
    elif mode == 'verticalSlider':
        mc.xform(controlTransform,scale = [.15,1,1],ws=True)
        mc.makeIdentity(controlTransform, apply=True, s=True)

        """ parent control to transform """
        controlBuffer = rigging.doParentReturnName(controlBuffer,controlTransform)
        
        """ set limits and lock and hide un-needed stuff"""
        attributes.doSetLockHideKeyableAttr(controlBuffer,True,False,False,['tx','tz','rx','ry','rz','sx','sy','sz','v'])
        mc.transformLimits(controlBuffer, ty = [-1,1],  ety = [1,1])
        
        return [controlBuffer,controlTransform]
   

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Module tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def createMasterControl(characterName,controlScale,font, controlVis = False, controlSettings = False, defaultGroups = False):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    1) get info
    2)
    
    DESCRIPTION:
    Generates a sizeTemplateObject. If there is one connected, it returns it.
    If it's been deleted, it recreates it. Guess the size based off of there
    being a mesh there. If there is no mesh, it sets sets an intial size of a 
    [155,170,29] unit character.
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    returnList(list) = [bottomCrv(string),TopCrv(list)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    nullBuffer = mc.group(em=True)
    attributes.storeInfo(nullBuffer,'cgmName',characterName)
    masterNull = NameFactory.doNameObject(nullBuffer)
    masterColors = modules.returnSettingsData('colorMaster',True)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Making the controls
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>       
    """ make our control object """
    controlsReturn = []
    rootCurve = curves.createControlCurve('masterAnim',controlScale)
    rootShapes = mc.listRelatives(rootCurve, shapes = True,fullPath=True)
    curves.setCurveColorByName(rootShapes[0],masterColors[0])
    curves.setCurveColorByName(rootShapes[1],masterColors[1])

    #attributes.storeInfo(rootCurve,"cgmName",(masterNull+'.cgmName'))
    attributes.storeInfo(rootCurve,"cgmType","controlMaster")
    RootCurve = ControlFactory(rootCurve,makeAimable=True,controlRO=True)
    RootCurve.doParent(masterNull)
    RootCurve.doName()
    guiFactory.warning("I'm here!")
    RootCurve.RotateOrderControl.set(2)        
    controlsReturn.append(RootCurve.nameShort)
    
    """ name curve """
    rootShapes = mc.listRelatives(RootCurve.nameShort, shapes = True)
    characterName = mc.getAttr(masterNull+'.cgmName')
    sizeCurve = curves.duplicateShape(rootShapes[1])
    nameScaleBuffer = distance.returnAbsoluteSizeCurve(sizeCurve)
    nameScale = max(nameScaleBuffer) * .8
    mc.delete(sizeCurve)
    masterText = curves.createTextCurveObject(characterName,size=nameScale,font=font)
    curves.setCurveColorByName(masterText,masterColors[0])
    mc.setAttr((masterText+'.rx'), -90)

    attributes.storeInfo(masterText,"cgmName","master")
    attributes.storeInfo(masterText,"cgmType","textCurve")
    attributes.storeInfo(masterText,"cgmObjectText",(masterNull+'.cgmName'))
    
    masterText = NameFactory.doNameObject(masterText)
    masterText = rigging.doParentReturnName(masterText,RootCurve.nameShort)
    controlsReturn.append(masterText)
    
    attributes.storeInfo(RootCurve.nameShort,"textCurve",masterText)
    
    attributes.doSetLockHideKeyableAttr(masterText,True,False,False,['tx','ty','tz','rx','ry','rz','v'])

    
    """ children controls"""
    controlsToMake = []
    if controlVis:
        controlsToMake.append('controlVisibility')
    if controlSettings:
        controlsToMake.append('controlSettings')
    if len(controlsToMake) >=1:
        childControls = childControlMaker(RootCurve.nameShort, baseAim = [0,1,0], baseUp = [0,0,-1], offset = 135, controls = controlsToMake, mode = ['incremental',90],distanceMultiplier = .8, zeroGroups = True,lockHide = True)
        for c in childControls.keys():
            controlsReturn.append(childControls.get(c))
        
    """ Default groups """
    if defaultGroups:
        nullBuffer = mc.group(em=True)
        noTransNull = ObjectFactory(nullBuffer)
        noTransNull.store('cgmName','noTransform')
        noTransNull.doName()
        noTransNull.doParent(masterNull)
        
        nullBuffer = mc.group(em=True)
        geoNull = ObjectFactory(nullBuffer)
        geoNull.store('cgmName','geo')
        geoNull.doName()
        geoNull.doParent(noTransNull.nameLong)
        
        nullBuffer = mc.group(em=True)
        skeletonNull = ObjectFactory(nullBuffer)
        skeletonNull.store('cgmName','skeleton')
        skeletonNull.doName()
        skeletonNull.doParent(RootCurve.nameShort)    
        
        nullBuffer = mc.group(em=True)
        rigNull = ObjectFactory(nullBuffer)
        rigNull.store('cgmName','rig')
        rigNull.doName()
        rigNull.doParent(RootCurve.nameShort)   
        
    if controlVis and defaultGroups:
        visControl =  childControls.get('controlVisibility')
        attributes.addSectionBreakAttrToObj(visControl,'Parts')
        attributes.addBoolAttrToObject(visControl,'rig')
        attributes.addBoolAttrToObject(visControl,'skeleton')
        attributes.addBoolAttrToObject(visControl,'geo')
            
        attributes.doConnectAttr((visControl+'.rig'),(rigNull.nameLong+'.v'))
        attributes.doConnectAttr((visControl+'.skeleton'),(skeletonNull.nameLong+'.v'))
        attributes.doConnectAttr((visControl+'.geo'),(geoNull.nameLong+'.v'))
        
        attributes.doSetAttr(visControl, 'rig', 1)
        attributes.doSetAttr(visControl, 'skeleton', 1)
        attributes.doSetAttr(visControl, 'geo', 1)
            
    """ store it to the master null"""
    attributes.storeInfo(masterNull,'controlMaster',RootCurve.nameShort)
    buffer = RootCurve.doGroup(True)
    grp = ObjectFactory(buffer)
    grp.store('cgmTypeModifier','constraint')
    grp.doName()
    
    return controlsReturn


def childControlMaker(baseControl, controls = ['controlVisibility'], mode = ['incremental',90], baseAim = [0,0,1], baseUp = [0,1,0], offset = 0, localRotationOffset = [0,0,0], scaleMultiplier = .15, distanceMultiplier = 1, aimChildren=False, zeroGroups = False, lockHide = True,getFont = False):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
    DESCRIPTION:
    Generates a radial array of controls around a base control where things start at noon and it divides
    the clock positions by the number of controls to make.  You can also change the mode so that you can
    tell it where to start on the clock and increment which to use.Stores the children controls to the baseControl
    as a message  node and stores the parentControl info to each generated control. It also takes into 
    account the colors of the baseControl using a secondary color if it exists.
    
    ARGUMENTS:
    baseControl(string) - The control we're working off of
    controlTypes(list) - the controls you want created. If the type specified isn't in the base settings,
                         the control is created as a cgmTextCurveObject
        Presets - settings
                  visibility
    mode(list) - (['even']) -  mode to set our values by and other information as required
        Options -   ['even']
                    ['incremental',30] - the firest term is mode, the second
                                        is the degrees to separate the controls by. Can be negative   
    baseAim(vector) - ([0,0,1]) - which way does your master control point
    baseUp(vector) - ([0,1,0]) - which way is up for your master control
    offset(int/float) - (0) - offset the starting clock position
    scaleMultiplier(float) - (.25) - multiplier for scale (default is .25) of the absolute size of the parent control
    distanceMultiplier(float) - (1.25) - multiplier for distance to travel 
    localRotationOffset(vector) - ([0,0,0]) - offset rotation for the controls if you want it
    aimChildren(bool) - (False) - aims the controls at the root of the base if True
    zeroGroups(bool) - (False) - if True adds zero transform groups to zero out the controls
    lockHide(bool) - (True) - If true, locks hides and makes unkeyable the typical transform attributes per control
    
    RETURNS:
    controlsMade(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get info
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    controlTypes = {'controlSettings':'gear','controlVisibility':'eye'}

    if getFont:
        masterNull = search.returnObjectMasterNull(baseControl)
        masterInfoNull = attributes.returnMessageObject(masterNull,'info')
        settingsInfoNull  = attributes.returnMessageObject(masterInfoNull,'settings')
    
        font = mc.getAttr(settingsInfoNull+'.font')
    else:
        font = 'Arial'
    
    """ our size """
    absSize = distance.returnAbsoluteSizeCurve(baseControl)
    controlScale = max(absSize) * scaleMultiplier
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Make Controls 
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    controlsMade={}
    for control in controls:
        """ If the type is in the dictionary, use that shape, if not make it as text"""
        if controlTypes.get(control) != None:
            controlBuffer = curves.createControlCurve(controlTypes.get(control),controlScale)
            attributes.storeInfo(controlBuffer,'cgmName', baseControl)
            attributes.storeInfo(controlBuffer,'cgmType', control)
            attributes.storeInfo(controlBuffer,'parentControl', baseControl)

            controlBuffer = NameFactory.doNameObject(controlBuffer)
            controlNameCleanBuffer = control.split('control')
            controlNameClean = controlNameCleanBuffer[1]
            attributes.storeInfo(baseControl,('childControl'+ (controlNameClean.capitalize())), controlBuffer)
            controlsMade[control] = controlBuffer
            
        else:
            controlBuffer = curves.createTextCurveObject(control,size=controlScale,font=font)
            attributes.storeInfo(controlBuffer,'parentControl', baseControl)
            attributes.storeInfo(baseControl,('childControl'+ (control.capitalize())), controlBuffer)
            attributes.storeInfo(controlBuffer,"textFont",(settingsInfoNull+'.font'))
            controlsMade[control] = controlBuffer 
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Prepping the transform group
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """first get a group out that we use to snap back to the parent control"""
    baseControlTransformGroup = rigging.groupMeObject(baseControl,False)
    
    """ zero out the group """
    mc.setAttr((baseControlTransformGroup+'.tx'),0)
    mc.setAttr((baseControlTransformGroup+'.ty'),0)
    mc.setAttr((baseControlTransformGroup+'.tz'),0)
    mc.setAttr((baseControlTransformGroup+'.rx'),0)
    mc.setAttr((baseControlTransformGroup+'.ry'),0)
    mc.setAttr((baseControlTransformGroup+'.rz'),0)
    
    """ create the locators to aim with"""
    locs = []
    toMake = ['aim','up','out']
    for type in toMake:
        locBuffer = locators.locMeObject(baseControlTransformGroup)
        locs.append(locBuffer)
    
    aimLoc = locs[0]
    upLoc = locs[1]
    outLoc = locs[2]

    """ move the locators """
    mc.xform(aimLoc,t=[0,0,25],ws=True)
    mc.xform(upLoc,t=[0,25,0],ws=True)
    mc.xform(outLoc,t=[25,0,0],ws=True)
    
    """ orient it to our common curve setup - zyx """
    aimConstraintBuffer = mc.aimConstraint(aimLoc,baseControlTransformGroup,maintainOffset = False, weight = 1, aimVector = baseAim, upVector = baseUp )
    mc.delete(aimConstraintBuffer[0])
    
    
    for loc in locs:
        mc.delete(loc)
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Positioning of controls
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ get our degree rotations """
    if mode[0] == 'even':
        rotateFactor = 360/len(controlsMade)
    elif mode[0] == 'incremental':
        rotateFactor = mode[1]
    else:
        rotateFactor = 360/len(controlsMade)

    """ base position of the control """
    distanceFactor = (max(absSize)/2) * distanceMultiplier
    
    runningRotation = 0 + offset
    for c in controlsMade.keys():
        control = controlsMade.get(c)
        """ move it """
        mc.setAttr((control+'.ty'),distanceFactor)
        """ loc it and rotate to get our control position"""
        locBuffer = locators.parentPivotLocMeObject(control)
        mc.setAttr((locBuffer+'.rz'),runningRotation)
        runningRotation = runningRotation + rotateFactor
        
        """ cente pivot of loc and point snap control to it, then delete the loc"""
        mc.xform(locBuffer, cp = True)
        position.movePointSnap(control,locBuffer)
        mc.delete(locBuffer)
        
        """ if the user wants to aim at the base control"""
        if aimChildren == True:
            position.aimSnap(control,baseControlTransformGroup,[0,-1,0],[0,0,1],[0,0,1])
        
        """ if there's an offset, let's put it in """
        if sum(localRotationOffset) != 0:
            mc.xform(control,rotation = localRotationOffset,r=True, os=True)
        
        
        mc.parent(control,baseControlTransformGroup)
        
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Finish Out
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ get colors from the master """
    baseColors = curves.returnColorsFromCurve(baseControl)
    if len(baseColors) > 1:
        controlColor = baseColors[1]
    else:
        controlColor = baseColors[0]
        
    position.moveParentSnap(baseControlTransformGroup,baseControl)
    
    for c in controlsMade.keys():
        control = controlsMade.get(c)
        mc.parent(control,baseControl)
        curves.setColorByIndex(control,controlColor)
        if zeroGroups == True:
            rigging.groupMeObject(control,True,True)
        if lockHide == True:
            attributes.doSetLockHideKeyableAttr(control)
            
    mc.delete(baseControlTransformGroup)
                
    
    return controlsMade
            
    
    

def createSizeTemplateControl(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
    DESCRIPTION:
    Generates a sizeTemplateObject. If there is one connected, it returns it.
    If it's been deleted, it recreates it. Guess the size based off of there
    being a mesh there. If there is no mesh, it sets sets an intial size of a 
    [155,170,29] unit character.
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    returnList(list) = [startCrv(string),EndCrv(list)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get info
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    geoGroup = attributes.returnMessageObject(masterNull,'geoGroup')
    centerColors = modules.returnSettingsData('colorCenter',True)
    masterInfoNull = attributes.returnMessageObject(masterNull,'info')
    geoInfoNull = attributes.returnMessageObject(masterInfoNull,'geo')
    settingsInfoNull  = attributes.returnMessageObject(masterInfoNull,'settings')
    font = mc.getAttr((settingsInfoNull+'.font'))
    
    """ first see if we already have one """
    geoInfoNull = attributes.returnMessageObject(masterInfoNull,'geo')
    templateObjectCheck = attributes.returnMessageObject(geoInfoNull,'sizeTemplateObject')
    if templateObjectCheck != False:
        returnList = []
        childCatch = mc.listRelatives(templateObjectCheck,children = True, type='transform')
        returnList.append(templateObjectCheck)
        for c in childCatch:
            returnList.append(c)
        return returnList
    
    """ checks for there being anything in our geo group """
    inMeshGroup = mc.listRelatives(geoGroup,children=True,type='transform')
    if inMeshGroup == None:
        boundingBoxSize =  modules.returnSettingsDataAsFloat('meshlessSizeTemplate')
    else:
        boundingBoxSize = distance.returnBoundingBoxSize (geoGroup)
    
    """determine orienation """
    maxSize = max(boundingBoxSize)
    matchIndex = boundingBoxSize.index(maxSize)
    
    """Find the pivot of the bounding box """
    pivotPosition = distance.returnCenterPivotPosition(geoGroup)
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # if a vertical object
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if matchIndex == 1 or matchIndex == 0:
        """ get our dimensions"""
        posBuffers = [[0,.5,0],[0,.75,0]]
        width = (boundingBoxSize[0]/2)
        height = (boundingBoxSize[1])
        depth = boundingBoxSize[2]
        cnt = 0
        for pos in posBuffers:
            posBuffer = posBuffers[cnt]
            posBuffer[0] = 0
            posBuffer[1] = (posBuffer[1] * height)
            posBuffer[2] = 0
            cnt+=1
            
    elif matchIndex == 2:
        """ get our dimensions"""
        posBuffers = [[0,0,-.33],[0,0,.66]]
        width = boundingBoxSize[1]
        height = boundingBoxSize[2]/2
        depth = (boundingBoxSize[0])
        cnt = 0
        for pos in posBuffers:
            posBuffer = posBuffers[cnt]
            posBuffer[0] = 0
            posBuffer[1] = boundingBoxSize[1] * .75
            posBuffer[2] = (posBuffer[2] * height)
            cnt+=1 
        
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Making the controls
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>       
    """ make our control object """
    startCurves = []
    startCurve = curves.createControlCurve('circle',depth*.8)
    mc.xform(startCurve,t=posBuffers[0],ws=True)
    curves.setCurveColorByName(startCurve,centerColors[1])
    startCurves.append(startCurve)

    startText = curves.createTextCurve('start',size=depth*.75,font=font)
    mc.xform(startText,t=posBuffers[0],ws=True)
    curves.setCurveColorByName(startText,centerColors[0])
    startCurves.append(startText)
    
    endCurves = []
    endCurve = curves.createControlCurve('circle',depth*.8)
    mc.xform(endCurve,t=posBuffers[1],ws=True)
    curves.setCurveColorByName(endCurve,centerColors[1])
    endCurves.append(endCurve)
    
    endText = curves.createTextCurve('end',size=depth*.6,font=font)
    mc.xform(endText,t=posBuffers[1],ws=True)
    curves.setCurveColorByName(endText,centerColors[0])
    endCurves.append(endText)
    
    """ aiming """
    position.aimSnap(startCurve,endCurve,[0,0,1],[0,1,0])
    position.aimSnap(startText,endCurve,[0,0,1],[0,1,0])
    
    position.aimSnap(endCurve,startCurve,[0,0,-1],[0,1,0])
    position.aimSnap(endText,startCurve,[0,0,-1],[0,1,0])
        
    sizeCurveControlStart = curves.combineCurves(startCurves)
    sizeCurveControlEnd = curves.combineCurves(endCurves)
    """ store our info to name our objects"""
    attributes.storeInfo(sizeCurveControlStart,'cgmName',(masterNull+'.cgmName'))
    attributes.storeInfo(sizeCurveControlStart,'cgmDirection','start')
    attributes.storeInfo(sizeCurveControlStart,'cgmType','templateSizeObject')
    sizeCurveControlStart = NameFactory.doNameObject(sizeCurveControlStart)
    mc.makeIdentity(sizeCurveControlStart, apply = True, t=True,s=True,r=True)

    attributes.storeInfo(sizeCurveControlEnd,'cgmName',(masterNull+'.cgmName'))
    attributes.storeInfo(sizeCurveControlEnd,'cgmDirection','end')
    attributes.storeInfo(sizeCurveControlEnd,'cgmType','templateSizeObject')
    sizeCurveControlEnd  = NameFactory.doNameObject(sizeCurveControlEnd)
    
    endGroup = rigging.groupMeObject(sizeCurveControlEnd)
    mc.makeIdentity(sizeCurveControlEnd, apply = True, t=True,s=True,r=True)
    
    mc.parentConstraint(sizeCurveControlStart,endGroup,maintainOffset = True)
    
    """ make control group """
    controlGroup = rigging.groupMeObject(sizeCurveControlStart)
    attributes.storeInfo(controlGroup,'cgmName',(masterNull+'.cgmName'))
    attributes.storeInfo(controlGroup,'cgmType','templateSizeObjectGroup')
    controlGroup = NameFactory.doNameObject(controlGroup)
    attributes.storeInfo(controlGroup,'controlStart',sizeCurveControlStart)
    attributes.storeInfo(controlGroup,'controlEnd',sizeCurveControlEnd)
    
    endGroup = rigging.doParentReturnName(endGroup,controlGroup)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Getting data ready
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>        
    attributes.storeInfo(masterNull,'templateSizeObject',controlGroup)
    
    returnList=[]
    returnList.append(sizeCurveControlStart)
    returnList.append(sizeCurveControlEnd)
    return returnList
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def limbControlMaker(moduleNull,controlTypes = ['cog']):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
	* Save the new positional information from the template objects
	* Collect all names of objects for a delete list
	* If anything in the module doesn't belong there, un parent it, report it
		* like a template object parented to another obect

    ARGUMENTS:
    moduleNull(string)
    controlTypes(list) = ['option1','option2']
    
    RETURNS:
    limbJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Gather data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ control helper objects - distance sorted"""
    templateRoot =  modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateRoot')
    controlTemplateObjects =  modules.returnInfoNullObjects(moduleNull,'templateControlObjects',types='all')
    controlTemplateObjects = distance.returnDistanceSortedList(templateRoot,controlTemplateObjects)

    """size list of template control objects """
    controlTemplateObjectsSizes = []
    for obj in controlTemplateObjects:
        controlTemplateObjectsSizes.append(distance.returnAbsoluteSizeCurve(obj))
    
    """ pos objects - distance sorted """
    posTemplateObjects =  modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateObject')
    posTemplateObjects = distance.returnDistanceSortedList(templateRoot,posTemplateObjects)

    
    """ orientation objects - distance sorted """
    orientationTemplateObjects = []
    for obj in posTemplateObjects:
        orientationTemplateObjects.append(attributes.returnMessageObject(obj,'orientHelper'))
    
    orientationTemplateObjects = distance.returnDistanceSortedList(templateRoot,orientationTemplateObjects)
    

    returnControls = {}
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Control Maker
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if 'spineIKHandle' in controlTypes:
        """ initial create"""
        ikHandleCurve = curves.createControlCurve('circleArrow2',1)
        mc.setAttr((ikHandleCurve+'.rz'),90)
        mc.setAttr((ikHandleCurve+'.ry'),90)
        mc.makeIdentity(ikHandleCurve, apply = True, r=True)
        startSizeBuffer = controlTemplateObjectsSizes[-1]
        scaleFactor = startSizeBuffer[0] * 1.25
        mc.setAttr((ikHandleCurve+'.sx'),1)
        mc.setAttr((ikHandleCurve+'.sy'),scaleFactor)
        mc.setAttr((ikHandleCurve+'.sz'),scaleFactor)
        position.moveParentSnap(ikHandleCurve,controlTemplateObjects[-1])
        position.movePointSnap(ikHandleCurve,orientationTemplateObjects[-1])
        
        """ make our transform """
        transform = rigging.groupMeObject(controlTemplateObjects[-1],False)
        
        """ connects shape """
        curves.parentShapeInPlace(transform,ikHandleCurve)
        mc.delete(ikHandleCurve)
        
        """ copy over the pivot we want """
        rigging.copyPivot(transform,orientationTemplateObjects[-1])
        
        """ Store data and name"""
        attributes.copyUserAttrs(controlTemplateObjects[-1],transform,attrsToCopy=['cgmName'])
        attributes.storeInfo(transform,'cgmType','controlAnim')
        attributes.storeInfo(transform,'cgmTypeModifier','ik')
        transform = NameFactory.doNameObject(transform)
        returnControls['spineIKHandle'] = transform
    
    if 'ikHandle' in controlTypes:
        """ initial create"""
        ikHandleCurve = curves.createControlCurve('cube',1)
        endSizeBuffer = controlTemplateObjectsSizes[-1]
        mc.setAttr((ikHandleCurve+'.sx'),endSizeBuffer[0])
        mc.setAttr((ikHandleCurve+'.sy'),endSizeBuffer[1])
        mc.setAttr((ikHandleCurve+'.sz'),endSizeBuffer[1])
        position.moveParentSnap(ikHandleCurve,controlTemplateObjects[-1])
        position.movePointSnap(ikHandleCurve,orientationTemplateObjects[-1])
        
        """ make our transform """
        transform = rigging.groupMeObject(controlTemplateObjects[-1],False)
        
        """ connects shape """
        curves.parentShapeInPlace(transform,ikHandleCurve)
        mc.delete(ikHandleCurve)
        
        """ copy over the pivot we want """
        rigging.copyPivot(transform,orientationTemplateObjects[-1])
        
        """ Store data and name"""
        attributes.copyUserAttrs(controlTemplateObjects[-1],transform,attrsToCopy=['cgmName'])
        attributes.storeInfo(transform,'cgmType','controlAnim')
        attributes.storeInfo(transform,'cgmTypeModifier','ik')
        transform = NameFactory.doNameObject(transform)
        returnControls['ikHandle'] = transform
        
    if 'twistFix' in controlTypes:
        """ initial create"""
        twistCurve = curves.createControlCurve('circleArrow1',1,'y+')
        startSizeBuffer = controlTemplateObjectsSizes[0]
        scaleFactor = startSizeBuffer[0] * 1.25
        mc.setAttr((twistCurve+'.sx'),1)
        mc.setAttr((twistCurve+'.sy'),scaleFactor)
        mc.setAttr((twistCurve+'.sz'),scaleFactor)
        position.moveParentSnap(twistCurve,orientationTemplateObjects[0])

        """ make our transform """
        transform = rigging.groupMeObject(controlTemplateObjects[0],False)
        
        """ connects shape """
        curves.parentShapeInPlace(transform,twistCurve)
        mc.delete(twistCurve)
        
        """ copy over the pivot we want """
        rigging.copyPivot(transform,orientationTemplateObjects[0])
        
        """ Store data and name"""
        attributes.copyUserAttrs(controlTemplateObjects[0],transform,attrsToCopy=['cgmName'])
        attributes.storeInfo(transform,'cgmType','controlAnim')
        attributes.storeInfo(transform,'cgmTypeModifier','twist')
        transform = NameFactory.doNameObject(transform)
        returnControls['twistFix'] = transform
     
    if 'vectorHandleSpheres' in controlTypes:
        vectorHandles = []
        for obj in controlTemplateObjects[1:-1]:
            vectorHandleBuffer = []
            currentIndex = controlTemplateObjects.index(obj)
            vectorHandleCurve = curves.createControlCurve('sphere',1)
            sizeBuffer = controlTemplateObjectsSizes[currentIndex]
            scaleFactor = sizeBuffer[0]*.75
            mc.setAttr((vectorHandleCurve+'.sx'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sy'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sz'),scaleFactor)
            position.moveParentSnap(vectorHandleCurve,orientationTemplateObjects[currentIndex])
            
            """ make our transform """
            transform = rigging.groupMeObject(obj,False)
            
            """ connects shape """
            curves.parentShapeInPlace(transform,vectorHandleCurve)
            mc.delete(vectorHandleCurve)
            
            """ copy over the pivot we want """
            rigging.copyPivot(transform,orientationTemplateObjects[currentIndex])
            
            """ Store data and name"""
            attributes.copyUserAttrs(obj,transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','ik')
            vectorHandleBuffer = NameFactory.doNameObject(transform)
            vectorHandles.append(vectorHandleBuffer)
            
            
        returnControls['vectorHandleSpheres'] = vectorHandles
        
    if 'vectorHandles' in controlTypes:
        vectorHandles = []
        for obj in controlTemplateObjects[1:-1]:
            vectorHandleBuffer = []
            currentIndex = controlTemplateObjects.index(obj)
            vectorHandleCurve = curves.createControlCurve('circleArrow',1)
            mc.setAttr((vectorHandleCurve+'.rx'),90)
            mc.makeIdentity(vectorHandleCurve, apply = True, r=True)
            sizeBuffer = controlTemplateObjectsSizes[currentIndex]
            scaleFactor = sizeBuffer[0]*1.5
            mc.setAttr((vectorHandleCurve+'.sx'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sy'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sz'),scaleFactor)
            position.moveParentSnap(vectorHandleCurve,controlTemplateObjects[currentIndex])
            position.movePointSnap(vectorHandleCurve,orientationTemplateObjects[currentIndex])
            
            """ make our transform """
            transform = rigging.groupMeObject(obj,False)
            
            """ connects shape """
            curves.parentShapeInPlace(transform,vectorHandleCurve)
            mc.delete(vectorHandleCurve)
            
            """ copy over the pivot we want """
            rigging.copyPivot(transform,orientationTemplateObjects[currentIndex])
            
            """ Store data and name"""
            attributes.copyUserAttrs(obj,transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','ik')
            vectorHandleBuffer = NameFactory.doNameObject(transform)
            vectorHandles.append(vectorHandleBuffer)
            
            
        returnControls['vectorHandles'] = vectorHandles
        
    if 'hips' in controlTypes:
        hipsCurve = curves.createControlCurve('semiSphere',1)
        mc.setAttr((hipsCurve+'.rx'),90)
        mc.makeIdentity(hipsCurve,apply=True,translate =True, rotate = True, scale=True)
        rootSizeBuffer = controlTemplateObjectsSizes[0]
        mc.setAttr((hipsCurve+'.sx'),rootSizeBuffer[0])
        mc.setAttr((hipsCurve+'.sy'),rootSizeBuffer[1])
        mc.setAttr((hipsCurve+'.sz'),rootSizeBuffer[0])
        position.moveParentSnap(hipsCurve,controlTemplateObjects[0])
        
        """ make our transform """
        transform = rigging.groupMeObject(controlTemplateObjects[0],False)
        
        """ connects shape """
        curves.parentShapeInPlace(transform,hipsCurve)
        mc.delete(hipsCurve)
        
        """ Store data and name"""
        attributes.storeInfo(transform,'cgmName','hips')
        attributes.storeInfo(transform,'cgmType','controlAnim')
        hips = NameFactory.doNameObject(transform)
        returnControls['hips'] = hips
            
    if 'cog' in controlTypes:
        cogControl = curves.createControlCurve('cube',1)
        rootSizeBuffer = controlTemplateObjectsSizes[0]
        mc.setAttr((cogControl+'.sx'),rootSizeBuffer[0]*1.05)
        mc.setAttr((cogControl+'.sy'),rootSizeBuffer[1]*1.05)
        mc.setAttr((cogControl+'.sz'),rootSizeBuffer[0]*.25)
        position.moveParentSnap(cogControl,controlTemplateObjects[0])
        
        mc.makeIdentity(cogControl,apply=True, scale=True)
        
        """ Store data and name"""
        attributes.storeInfo(cogControl,'cgmName','cog')
        attributes.storeInfo(cogControl,'cgmType','controlAnim')
        cogControl = NameFactory.doNameObject(cogControl)
        returnControls['cog'] = cogControl
    
    if 'segmentControls' in controlTypes:
        segmentControls = []
        segments = lists.parseListToPairs(controlTemplateObjects)
        orientationSegments = lists.parseListToPairs(orientationTemplateObjects)
        cnt = 0
        for segment in segments:
            """ get our orientation segment buffer """
            orientationSegment = orientationSegments[cnt]
            
            """move distance """
            distanceToMove = distance.returnDistanceBetweenObjects(segment[0],segment[1])

            """ root curve """
            rootCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[0])
            mc.setAttr((rootCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((rootCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((rootCurve+'.sz'),1)
            position.moveParentSnap(rootCurve,segment[0])
            mc.move(0, 0, (distanceToMove * .1), rootCurve, r=True,os=True,wd=True)
            
            """ end curve """
            endCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[1])
            mc.setAttr((endCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((endCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((endCurve+'.sz'),1)
            position.moveParentSnap(endCurve,segment[1])
            mc.move(0, 0, -(distanceToMove * .1), endCurve, r=True,os=True,wd=True)
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #>>> Side curves
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            """ locators on curve"""
            side1Locs = []
            side2Locs = []
            frontLocs = []
            backLocs = []
            side1Locs.append(locators.locMeCvFromCvIndex(rootCurve,3))
            side1Locs.append(locators.locMeCvFromCvIndex(endCurve,3))
            side2Locs.append(locators.locMeCvFromCvIndex(rootCurve,7))
            side2Locs.append(locators.locMeCvFromCvIndex(endCurve,7))
            frontLocs.append(locators.locMeCvFromCvIndex(rootCurve,5))
            frontLocs.append(locators.locMeCvFromCvIndex(endCurve,5))
            backLocs.append(locators.locMeCvFromCvIndex(rootCurve,0))
            backLocs.append(locators.locMeCvFromCvIndex(endCurve,0))
            
            """ get u positions for new curves"""
            side1PosSet = []
            side2PosSet = []
            frontPosSet = []
            backPosSet = []
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[0],rootCurve))
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[1],endCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[0],rootCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[1],endCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[0],rootCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[1],endCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[0],rootCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[1],endCurve))

            """ make side curves"""
            sideCrv1 = mc.curve (d=1, p = side1PosSet , os=True)
            sideCrv2 = mc.curve (d=1, p = side2PosSet , os=True)
            frontCrv = mc.curve (d=1, p = frontPosSet , os=True)
            backCrv = mc.curve (d=1, p = backPosSet , os=True)
            
            """ combine curves """
            mc.makeIdentity(rootCurve,apply=True,translate =True, rotate = True, scale=True)
            mc.makeIdentity(endCurve,apply=True,translate =True, rotate = True, scale=True)
            segmentCurveBuffer = curves.combineCurves([sideCrv1,sideCrv2,frontCrv,backCrv,rootCurve,endCurve])
            
            """ delete locs """
            for loc in side1Locs,side2Locs,frontLocs,backLocs:
                mc.delete(loc)
                
            """ make our transform """
            transform = rigging.groupMeObject(segment[0],False)
            
            """ connects shape """
            curves.parentShapeInPlace(transform,segmentCurveBuffer)
            mc.delete(segmentCurveBuffer)


            """ copy over the pivot we want """
            rigging.copyPivot(transform,orientationSegment[0])
              
            """ Store data and name"""
            attributes.copyUserAttrs(segment[0],transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','fk')
            segmentCurveBuffer = NameFactory.doNameObject(transform)
            segmentControls.append(segmentCurveBuffer)
            
            cnt+=1
        returnControls['segmentControls'] = segmentControls
        
    if 'limbControls' in controlTypes:
        limbControls = []
        controlSegments = lists.parseListToPairs(controlTemplateObjects)
        orientationSegments = lists.parseListToPairs(orientationTemplateObjects)
        cnt = 0
        for segment in controlSegments:
            """ get our orientation segment buffer """
            orientationSegment = orientationSegments[cnt]
            """move distance """
            distanceToMove = distance.returnDistanceBetweenObjects(orientationSegment[0],orientationSegment[1])

            """ root curve """
            rootCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[0])
            mc.setAttr((rootCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((rootCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((rootCurve+'.sz'),1)
            position.moveParentSnap(rootCurve,segment[0])
            #mc.move(0, 0, (distanceToMove * .15), rootCurve, r=True,os=True,wd=True)
            
            """ end curve """
            endCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[1])
            mc.setAttr((endCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((endCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((endCurve+'.sz'),1)
            position.moveParentSnap(endCurve,segment[1])
            position.movePointSnap(endCurve,orientationSegment[1])
            mc.move(0, 0, -(distanceToMove * .15), endCurve, r=True,os=True,wd=True)
            
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #>>> Side curves
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            """ locators on curve"""
            side1Locs = []
            side2Locs = []
            frontLocs = []
            backLocs = []
            side1Locs.append(locators.locMeCvFromCvIndex(rootCurve,3))
            side1Locs.append(locators.locMeCvFromCvIndex(endCurve,3))
            side2Locs.append(locators.locMeCvFromCvIndex(rootCurve,7))
            side2Locs.append(locators.locMeCvFromCvIndex(endCurve,7))
            frontLocs.append(locators.locMeCvFromCvIndex(rootCurve,5))
            frontLocs.append(locators.locMeCvFromCvIndex(endCurve,5))
            backLocs.append(locators.locMeCvFromCvIndex(rootCurve,0))
            backLocs.append(locators.locMeCvFromCvIndex(endCurve,0))
            
            """ get u positions for new curves"""
            side1PosSet = []
            side2PosSet = []
            frontPosSet = []
            backPosSet = []
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[0],rootCurve))
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[1],endCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[0],rootCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[1],endCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[0],rootCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[1],endCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[0],rootCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[1],endCurve))

            """ make side curves"""
            sideCrv1 = mc.curve (d=1, p = side1PosSet , os=True)
            sideCrv2 = mc.curve (d=1, p = side2PosSet , os=True)
            frontCrv = mc.curve (d=1, p = frontPosSet , os=True)
            backCrv = mc.curve (d=1, p = backPosSet , os=True)
            
            """ combine curves """
            mc.makeIdentity(rootCurve,apply=True,translate =True, rotate = True, scale=True)
            mc.makeIdentity(endCurve,apply=True,translate =True, rotate = True, scale=True)
            segmentCurveBuffer = curves.combineCurves([sideCrv1,sideCrv2,frontCrv,backCrv,rootCurve,endCurve])
            
            """ delete locs """
            for loc in side1Locs,side2Locs,frontLocs,backLocs:
                mc.delete(loc)
                
            """ make our transform """
            transform = rigging.groupMeObject(segment[0],False)
            
            """ connects shape """
            curves.parentShapeInPlace(transform,segmentCurveBuffer)
            mc.delete(segmentCurveBuffer)
            
            """ copy over the pivot we want """
            rigging.copyPivot(transform,orientationSegment[0])

                
            """ Store data and name"""
            attributes.copyUserAttrs(segment[0],transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','fk')
            limbControlBuffer = NameFactory.doNameObject(transform)
            limbControls.append(limbControlBuffer)
            
            cnt+=1
        returnControls['limbControls'] = limbControls
        
    if 'headControls' in controlTypes:
        headControls = []
        controlSegments = lists.parseListToPairs(controlTemplateObjects)
        orientationSegments = lists.parseListToPairs(orientationTemplateObjects)
        """ figure out our second to last segment to do something a bit different """
        secondToLastCheck = (len(controlSegments)-2)
        print secondToLastCheck  
        cnt = 0
        for segment in controlSegments:
            """ get our orientation segment buffer """
            orientationSegment = orientationSegments[cnt]            
            """move distance """
            distanceToMove = distance.returnDistanceBetweenObjects(segment[0],segment[1])

            """ root curve """
            rootCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[0])
            mc.setAttr((rootCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((rootCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((rootCurve+'.sz'),1)
            position.moveParentSnap(rootCurve,segment[0])
            mc.move(0, 0, (distanceToMove * .05), rootCurve, r=True,os=True,wd=True)
            
            """ end curve """
            endCurve = curves.createControlCurve('circle',1)
            if cnt != secondToLastCheck:
                rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[1])
            else:
                rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[0])
            mc.setAttr((endCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((endCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((endCurve+'.sz'),1)
            position.moveParentSnap(endCurve,segment[1])
            mc.move(0, 0, -(distanceToMove * .05), endCurve, r=True,os=True,wd=True)
            
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #>>> Side curves
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            """ locators on curve"""
            side1Locs = []
            side2Locs = []
            frontLocs = []
            backLocs = []
            side1Locs.append(locators.locMeCvFromCvIndex(rootCurve,3))
            side1Locs.append(locators.locMeCvFromCvIndex(endCurve,3))
            side2Locs.append(locators.locMeCvFromCvIndex(rootCurve,7))
            side2Locs.append(locators.locMeCvFromCvIndex(endCurve,7))
            frontLocs.append(locators.locMeCvFromCvIndex(rootCurve,5))
            frontLocs.append(locators.locMeCvFromCvIndex(endCurve,5))
            backLocs.append(locators.locMeCvFromCvIndex(rootCurve,0))
            backLocs.append(locators.locMeCvFromCvIndex(endCurve,0))
            
            """ get u positions for new curves"""
            side1PosSet = []
            side2PosSet = []
            frontPosSet = []
            backPosSet = []
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[0],rootCurve))
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[1],endCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[0],rootCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[1],endCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[0],rootCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[1],endCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[0],rootCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[1],endCurve))

            """ make side curves"""
            sideCrv1 = mc.curve (d=1, p = side1PosSet , os=True)
            sideCrv2 = mc.curve (d=1, p = side2PosSet , os=True)
            frontCrv = mc.curve (d=1, p = frontPosSet , os=True)
            backCrv = mc.curve (d=1, p = backPosSet , os=True)
            
            """ combine curves """
            mc.makeIdentity(rootCurve,apply=True,translate =True, rotate = True, scale=True)
            mc.makeIdentity(endCurve,apply=True,translate =True, rotate = True, scale=True)
            segmentCurveBuffer = curves.combineCurves([sideCrv1,sideCrv2,frontCrv,backCrv,rootCurve,endCurve])
            
            """ delete locs """
            for loc in side1Locs,side2Locs,frontLocs,backLocs:
                mc.delete(loc)
                
            """ make our transform """
            transform = rigging.groupMeObject(segment[0],False)
            
            """ connects shape """
            curves.parentShapeInPlace(transform,segmentCurveBuffer)
            mc.delete(segmentCurveBuffer)
            
            """ copy over the pivot we want """
            rigging.copyPivot(transform,orientationSegment[0])
              
            """ Store data and name"""
            attributes.copyUserAttrs(segment[0],transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','fk')
            segmentCurveBuffer = NameFactory.doNameObject(transform)
            headControls.append(segmentCurveBuffer)
            
            cnt+=1
        returnControls['headControls'] = headControls


    
    return returnControls


def createMasterControlFromMasterNull(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    1) get info
    2)
    
    DESCRIPTION:
    Generates a sizeTemplateObject. If there is one connected, it returns it.
    If it's been deleted, it recreates it. Guess the size based off of there
    being a mesh there. If there is no mesh, it sets sets an intial size of a 
    [155,170,29] unit character.
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    returnList(list) = [bottomCrv(string),TopCrv(list)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get info
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    geoGroup = attributes.returnMessageObject(masterNull,'geoGroup')
    masterColors = modules.returnSettingsData('colorMaster',True)
    masterInfoNull = attributes.returnMessageObject(masterNull,'info')
    geoInfoNull = attributes.returnMessageObject(masterInfoNull,'geo')
    settingsInfoNull  = attributes.returnMessageObject(masterInfoNull,'settings')
    font = mc.getAttr((settingsInfoNull+'.font'))

    
    """ checks for there being anything in our geo group """
    inMeshGroup = mc.listRelatives(geoGroup,children=True,type='transform')
    if inMeshGroup == None:
        boundingBoxSize =  modules.returnSettingsDataAsFloat('meshlessSizeTemplate')
    else:
        boundingBoxSize = distance.returnBoundingBoxSize (geoGroup)
        
    """ Determine our size """
    sizeCheck=[]
    sizeCheck.append(boundingBoxSize[0])
    sizeCheck.append(boundingBoxSize[1])
    sizeCheck.append(boundingBoxSize[2])
    maxSize = max(sizeCheck)
    matchIndex = boundingBoxSize.index(maxSize)
    controlScale = maxSize * .75
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Making the controls
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>       
    """ make our control object """
    controlsReturn = []
    rootCurve = curves.createControlCurve('masterAnim',controlScale)
    rootShapes = mc.listRelatives(rootCurve, shapes = True)
    curves.setCurveColorByName(rootShapes[0],masterColors[0])
    curves.setCurveColorByName(rootShapes[1],masterColors[1])

    attributes.storeInfo(rootCurve,"cgmName",(masterNull+'.cgmName'))
    attributes.storeInfo(rootCurve,"cgmType","controlMaster")
    
    rootCurve = rigging.doParentReturnName(rootCurve,masterNull)
    rootCurve = NameFactory.doNameObject(rootCurve)

    controlsReturn.append(rootCurve)
    
    """ name curve """
    rootShapes = mc.listRelatives(rootCurve, shapes = True)
    characterName = mc.getAttr(masterNull+'.cgmName')
    sizeCurve = curves.duplicateShape(rootShapes[1])
    nameScaleBuffer = distance.returnAbsoluteSizeCurve(sizeCurve)
    nameScale = max(nameScaleBuffer) * .8
    mc.delete(sizeCurve)
    masterText = curves.createTextCurveObject(characterName,size=nameScale,font=font)
    curves.setCurveColorByName(masterText,masterColors[0])
    mc.setAttr((masterText+'.rx'), -90)

    attributes.storeInfo(masterText,"cgmName","master")
    attributes.storeInfo(masterText,"cgmType","textCurve")
    
    attributes.storeInfo(masterText,"curveText",(masterNull+'.cgmName'))
    attributes.storeInfo(masterText,"textFont",(settingsInfoNull+'.font'))
    
    masterText = NameFactory.doNameObject(masterText)
    masterText = rigging.doParentReturnName(masterText,rootCurve)
    controlsReturn.append(masterText)
    
    attributes.storeInfo(rootCurve,"textCurve",masterText)
    
    attributes.doSetLockHideKeyableAttr(masterText,True,False,False,['tx','ty','tz','rx','ry','rz','v'])

    
    """ children controls"""
    childControls = childControlMaker(rootCurve, baseAim = [0,1,0], baseUp = [0,0,-1], offset = 135, controls = ['controlSettings','controlVisibility'], mode = ['incremental',90],distanceMultiplier = .8, zeroGroups = True,lockHide = True)
    for control in childControls:
        controlsReturn.append(control)
        
        
    """ store it to the master null"""
    attributes.storeInfo(masterNull,'controlMaster',rootCurve)
    return controlsReturn

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Making the controls
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def makeObjectControl(obj,desiredShape, size):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Shape parents a nurbs curve to an object to make it usable as a control
    
    ARGUMENTS:
    obj(string)
    desiredShape(string) - see options in curves (createControlCurve)
    size(float)
    
    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    ctrl = curves.createControlCurve(desiredShape,size)
    curves.parentShape(obj,ctrl)
    mc.delete (ctrl)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def makeControlForObject(obj,desiredShape, size):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    First creates a transform node at the object (matching positin, rotation
    and rotationOrder. Then shape parents a nurbs curve to an object to make
    it usable as a control
    
    ARGUMENTS:
    obj(string)
    desiredShape(string) - see options in curves (createControlCurve)
    size(float)
    
    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    transform = groupMeObject(obj,True)
    ctrl = curves.createControlCurve(desiredShape,size)
    curves.parentShape(transform,ctrl)
    mc.delete (ctrl)