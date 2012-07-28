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
    print "Core position list %s"%corePositionList        
            
                    
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
        
        """
        for loc in baseLocs[:-1]:
            mc.delete(loc)"""
            
        print "Initial position list is %s"%returnList        
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