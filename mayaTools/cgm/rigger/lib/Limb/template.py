"""
cgmLimb
Josh Burton (under the supervision of David Bokser:)
www.cgmonks.com
1/12/2011

Key:
1) Class - Limb
    Creates our rig objects
2)  


"""
import maya.cmds as mc
from cgm.lib.classes import NameFactory
from cgm.lib.classes.AttrFactory import *
from cgm.lib.classes.ObjectFactory import *

from cgm.rigger.ModuleFactory import *


from cgm.lib import (search,
                     distance,
                     names,
                     attributes,
                     names,
                     rigging,
                     constraints,
                     curves,
                     dictionary,
                     settings,
                     lists,
                     modules,
                     position,
                     cgmMath,
                     controlBuilder)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>> Sizing
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def getGeneratedInitialPositionData(self, PuppetInstance, startLocList,*a,**kw):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Calculates initial positioning info for objects
    
    ARGUMENTS:
    sourceObjects(list)
    visAttr(string)
    PuppetInstance.templateSizeObjects['start'],PuppetInstance.templateSizeObjects['end']
    
    RETURNS:
    returnList(list) = [posList(list),endChildLoc(loc)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    guiFactory.report("Generating Initial position data via Limb - '%s'"%self.ModuleNull.nameBase)
    partBaseDistance = kw.pop('partBaseDistance',1)
    
    startLoc = startLocList[0]
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Distances
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ measure root object"""
    absStartCurveSize = distance.returnAbsoluteSizeCurve(PuppetInstance.templateSizeObjects['start'])
    sizeObjectLength = distance.returnDistanceBetweenObjects(startLoc,PuppetInstance.templateSizeObjects['end'])
    corePositionList = modules.returncgmTemplatePartPositionData(self.afModuleType.value) or False
    
    if not corePositionList:
        corePositionList = []
        positions = cgmMath.divideLength(1,self.optionHandles.value)
        for position in positions:
            bufferList = [0,0]
            bufferList.append(position)
            corePositionList.append(bufferList)     
    guiFactory.report( "Core position list %s"%corePositionList )      
            
                    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Things with the character root as a base Limb segments and Torsos
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
    if not self.moduleParent:    
        """ 
        Get the data in a usable format. Our positional ratios are stored in x,y,z format
        so we're going to get the absolute size data in that format with our distance
        being our z value
        """
        moduleSizeBaseDistanceValues = []
        moduleSizeBaseDistanceValues.append(absStartCurveSize[0])
        moduleSizeBaseDistanceValues.append(absStartCurveSize[2])
        moduleSizeBaseDistanceValues.append(sizeObjectLength)
        
        """ multiply our values """
        translationValues = []
        for list in corePositionList:
            translationValues.append(cgmMath.multiplyLists([list,moduleSizeBaseDistanceValues]))
            
        baseLocs = []
        for value in translationValues:
            locBuffer = mc.duplicate(startLoc)
            mc.xform(locBuffer,t=value,r=True,os=True)
            baseLocs.append(locBuffer[0])
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # SubSplitting
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        splitTransformationValues = []
        if self.optionStiffIndex.value != 0:
            if self.optionHandles.value > len(baseLocs):                
                if self.optionStiffIndex.value > 0:
                    stiff = 'positive'
                    splitDistance = distance.returnDistanceBetweenObjects(baseLocs[self.optionStiffIndex.value],baseLocs[-1])
                    print splitDistance
                    print baseLocs[self.optionStiffIndex.value]
                    positions = cgmMath.divideLength(splitDistance,(self.optionHandles.value-len(baseLocs)+2))
                    for position in positions[1:-1]:
                        splitTransformationValues.append([0,0,position])
                else:
                    stiff = 'negative'
                    splitDistance = distance.returnDistanceBetweenObjects(baseLocs[0],baseLocs[self.optionStiffIndex.value +-1])
                    positions = cgmMath.divideLength(splitDistance,(self.optionHandles.value-len(baseLocs)+2))
                    for pos in positions[1:-1]:
                        splitTransformationValues.append([0,0,pos])
        else:
            if self.optionHandles.value > len(baseLocs):
                stiff = 'zero'
                splitDistance = distance.returnDistanceBetweenObjects(baseLocs[0],baseLocs[1])
                positions = cgmMath.divideLength(splitDistance,(self.optionHandles.value-len(baseLocs)+2))
                for pos in positions[1:-1]:
                    splitTransformationValues.append([0,0,pos])
                        
        if len(splitTransformationValues) > 0 :
            for value in splitTransformationValues:
                if stiff == 'positive':
                    locBuffer = mc.duplicate(baseLocs[stiffIndex])
                else:
                    locBuffer = mc.duplicate(baseLocs[0])
                mc.xform(locBuffer,t=value,r=True,os=True)
                baseLocs.append(locBuffer[0])
            
        baseLocs = distance.returnDistanceSortedList(startLoc,baseLocs)
        mc.delete(startLoc)
        posList =  distance.returnWorldSpacePositionFromList(baseLocs)
        
        returnList = {}
        returnList['positions'] = posList
        returnList['locator'] = baseLocs[-1]
        
        
        for loc in baseLocs[:-1]:
            mc.delete(loc)
            
        guiFactory.report( "Initial position list is %s"%returnList)   
        return returnList
        
    else:           
        """ 
        Get the data in a usable format. Our positional ratios are stored in x,y,z format
        so we're going to get the absolute size data in that format with our distance
        being our z value
        """
        moduleSizeBaseDistanceValues = []
        moduleSizeBaseDistanceValues.append(absStartCurveSize[0])
        moduleSizeBaseDistanceValues.append(absStartCurveSize[2])
        moduleSizeBaseDistanceValues.append(sizeObjectLength)
        
        """ multiply our values """
        translationValues = []
        for list in corePositionList:
            translationValues.append(cgmMath.multiplyLists([list,moduleSizeBaseDistanceValues]))
        
        baseLocs = []
        if partType == 'clavicle' and direction == 'left':
            for value in translationValues:
                locBuffer = mc.duplicate(startLoc)
                mc.xform(locBuffer,t=[-value[0],value[1],value[2]],r=True,os=True)
                baseLocs.append(locBuffer[0])
        else:
            for value in translationValues:
                locBuffer = mc.duplicate(startLoc)
                mc.xform(locBuffer,t=value,r=True,os=True)
                baseLocs.append(locBuffer[0])
            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # SubSplitting
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        splitTransformationValues = []
        if stiffIndex != 0:
            if handles > len(baseLocs):                
                if stiffIndex > 0:
                    stiff = 'positive'
                    splitDistance = distance.returnDistanceBetweenObjects(baseLocs[stiffIndex],baseLocs[-1])
                    print splitDistance
                    print baseLocs[stiffIndex]
                    positions = cgmMath.divideLength(splitDistance,(handles-len(baseLocs)+2))
                    for position in positions[1:-1]:
                        splitTransformationValues.append([0,0,position])
                else:
                    stiff = 'negative'
                    splitDistance = distance.returnDistanceBetweenObjects(baseLocs[0],baseLocs[stiffIndex +-1])
                    positions = cgmMath.divideLength(splitDistance,(handles-len(baseLocs)+2))
                    for position in positions[1:-1]:
                        splitTransformationValues.append([0,0,position])
        else:
            if handles > len(baseLocs):
                stiff = 'zero'
                splitDistance = distance.returnDistanceBetweenObjects(baseLocs[0],baseLocs[1])
                positions = cgmMath.divideLength(splitDistance,(handles-len(baseLocs)+2))
                for position in positions[1:-1]:
                    splitTransformationValues.append([0,0,position])
                        
        if len(splitTransformationValues) > 0 :
            for value in splitTransformationValues:
                if stiff == 'positive':
                    locBuffer = mc.duplicate(baseLocs[stiffIndex])
                else:
                    locBuffer = mc.duplicate(baseLocs[0])
                mc.xform(locBuffer,t=value,r=True,os=True)
                baseLocs.append(locBuffer[0])
            
        
        baseLocs = distance.returnDistanceSortedList(startLoc,baseLocs)
        mc.delete(startLoc)
        posList =  distance.returnWorldSpacePositionFromList(baseLocs)
        if partType == 'clavicle':
            posList.reverse() 
            
        returnList = {}
        returnList['positions'] = posList
        returnList['locator'] = baseLocs[-1]
        
        for loc in baseLocs[:-1]:
            mc.delete(loc)
            
        print "Initial position list is %s"%returnList        
        return returnList
    
def addOrientationHelpers(self):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds orientation helpers to a template chain
    
    ARGUMENTS:
    objects(list)
    root(string) - root control of the limb chain
    moduleType(string)
    
    RETURNS:
    returnList(list) = [rootHelper(string),helperObjects(list),helperObjectGroups(list)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    moduleColors = modules.returnModuleColors(self.ModuleNull.nameLong)
    helperObjects = []
    helperObjectGroups = []
    returnBuffer = []
    root = self.msgTemplateRoot.getMessage()
    visAttr = "%s.visOrientHelpers"%self.infoNulls['visibilityOptions'].get()  
    objects =  self.templatePosObjectsBuffer.bufferList
    
    #>>> Direction and size Stuff
    """ Directional data derived from joints """
    generalDirection = logic.returnHorizontalOrVertical(objects)
    
    if generalDirection == 'vertical' and 'leg' not in self.afModuleType.get():
        worldUpVector = [0,0,-1]
    elif generalDirection == 'vertical' and 'leg' in self.afModuleType.get():
        worldUpVector = [0,0,1]
    else:
        worldUpVector = [0,1,0]
    
    #Get Size 
    size = (distance.returnBoundingBoxSizeToAverage(objects[0])*2)
    
    #>>> Master Orient helper
    createBuffer = curves.createControlCurve('circleArrow1',(size*2),'z+') # make the curve
    curves.setCurveColorByName(createBuffer,moduleColors[0])
    
    attributes.storeInfo(createBuffer,'cgmType','templateOrientRoot') #copy the name attr
    mainOrientHelperObj = NameFactory.doNameObject(createBuffer)
    
    attributes.storeObjectToMessage (mainOrientHelperObj, self.msgTemplateRoot.get() , 'orientHelper')#store the object to it's respective  object
    returnBuffer.append(mainOrientHelperObj)
    
    # Snapping 
    position.movePointSnap(mainOrientHelperObj,root)    
    constBuffer = mc.aimConstraint(objects[1],mainOrientHelperObj,maintainOffset = False, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpVector = worldUpVector, worldUpType = 'vector' )
    mc.delete (constBuffer[0])
    
    # Follow Groups 
    mainOrientHelperGroupBuffer = rigging.groupMeObject(mainOrientHelperObj)
    mainOrientHelperGroupBuffer = NameFactory.doNameObject(mainOrientHelperGroupBuffer)
    mainOrientHelperGroup = rigging.doParentReturnName(mainOrientHelperGroupBuffer,root)
    mc.pointConstraint(objects[0],mainOrientHelperGroupBuffer,maintainOffset = False)
    helperObjectGroups.append(mainOrientHelperGroup)
    
    # set up constraints
    mc.aimConstraint(objects[-1],mainOrientHelperGroup,maintainOffset = True, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpObject = root, worldUpType = 'objectRotation' )
    # lock and hide stuff 
    attributes.doSetLockHideKeyableAttr(mainOrientHelperObj,True,False,False,['tx','ty','tz','rz','ry','sx','sy','sz','v'])
    
    #>>> The sub helpers
    """ make our pair lists """
    pairList = lists.parseListToPairs(objects)

    """ make our controls """
    helperObjects = []
    for pair in pairList:
        """ Get Size """
        size = (distance.returnBoundingBoxSizeToAverage(pair[0])*2)
        
        """ make the curve"""
        createBuffer = curves.createControlCurve('circleArrow2Axis',size,'y-')
        curves.setCurveColorByName(createBuffer,moduleColors[1])
        
        """ copy the name attr"""
        attributes.copyUserAttrs(pair[0],createBuffer,['cgmName'])
        attributes.storeInfo(createBuffer,'cgmType','templateOrientObject')
        helperObj = NameFactory.doNameObject(createBuffer)
        
        
        """ store the object to it's respective  object and to an object list """
        attributes.storeObjectToMessage (helperObj, pair[0], 'orientHelper')
        helperObjects.append(helperObj)
        
        """ initial snapping """
        position.movePointSnap(helperObj,pair[0])
        constBuffer = mc.aimConstraint(pair[1],helperObj,maintainOffset = False, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpVector = worldUpVector, worldUpType = 'vector' )
        mc.delete (constBuffer[0])
        
        """ follow groups """
        helperGroupBuffer = rigging.groupMeObject(helperObj)
        helperGroup = NameFactory.doNameObject(helperGroupBuffer)
        helperGroup = rigging.doParentReturnName(helperGroup,pair[0])
        helperObjectGroups.append(helperGroup)
        
        """ set up constraints """
        mc.aimConstraint(pair[1],helperGroup,maintainOffset = False, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpVector = [0,1,0], worldUpObject = mainOrientHelperObj, worldUpType = 'objectrotation' )

        """ lock and hide stuff """
        helperObj = attributes.returnMessageObject(pair[0],'orientHelper')
        mc.connectAttr((visAttr),(helperObj+'.v'))
        attributes.doSetLockHideKeyableAttr(helperObj,True,False,False,['tx','ty','tz','ry','rz','sx','sy','sz','v'])
    
    #>>> For the last object in the chain
    for obj in objects[-1:]:
        """ Get Size """
        size = (distance.returnBoundingBoxSizeToAverage(obj)*2)
        
        """ make the curve"""
        createBuffer = curves.createControlCurve('circleArrow2Axis',size,'y-')
        curves.setCurveColorByName(createBuffer,moduleColors[1])
        """ copy the name attr"""
        attributes.copyUserAttrs(obj,createBuffer,['cgmName'])
        attributes.storeInfo(createBuffer,'cgmType','templateOrientObject')
        helperObj = NameFactory.doNameObject(createBuffer)
        
        """ store the object to it's respective  object """
        attributes.storeObjectToMessage (helperObj, obj, 'orientHelper')
        
        """ initial snapping """
        position.movePointSnap(helperObj,obj)
        constBuffer = mc.aimConstraint(objects[-2],helperObj,maintainOffset = False, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpVector = worldUpVector, worldUpType = 'vector' )
        mc.delete (constBuffer[0])
        
        """ follow groups """
        helperGroupBuffer = rigging.groupMeObject(helperObj)
        helperGroup = NameFactory.doNameObject(helperGroupBuffer)
        helperGroup = rigging.doParentReturnName(helperGroup,obj)
        helperObjectGroups.append(helperGroup)
        
        """ set up constraints """
        secondToLastHelperObject = attributes.returnMessageObject(objects[-2],'orientHelper')
        mc.orientConstraint(secondToLastHelperObject,helperGroup,maintainOffset = False, weight = 1)
        
        """ lock and hide stuff """
        helperObj = attributes.returnMessageObject(obj,'orientHelper')
        mc.connectAttr((visAttr),(helperObj+'.v'))
        attributes.doSetLockHideKeyableAttr(helperObj,True,False,False,['tx','ty','tz','sx','sy','sz','v'])
        helperObjects.append(helperObj)
   
    
    returnBuffer.append(helperObjects)
    returnBuffer.append(helperObjectGroups)
    return returnBuffer