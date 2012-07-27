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


import re
import copy

reload(search)
reload(distance)
reload(names)
reload(attributes)
reload(names)
reload(rigging)
reload(constraints)
reload(curves)
reload(dictionary)
reload(settings)
reload(lists)
reload(modules)
reload(cgmMath)
reload(controlBuilder)

typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
namesDictionary = dictionary.initializeDictionary( settings.getNamesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())


defaultSettings = {'partType':'none',
                   'stiffIndex':0,
                   'curveDegree':1,
                   'rollJoints':3,
                   'handles':3,
                   'bendy':True,
                   'stretchy':True,
                   'fk':True,
                   'ik':True}

#horiztonalLegDict = {'left':[3,templateSizeObjects[0],templateSizeObjects[1]],'right':[7,templateSizeObjects[0],templateSizeObjects[1]],'left_front':[3,templateSizeObjects[1],templateSizeObjects[0]], 'right_front':[7,templateSizeObjects[1],templateSizeObjects[0]], 'left_back':[3,templateSizeObjects[0],templateSizeObjects[1]],'right_back':[7,templateSizeObjects[0],templateSizeObjects[1]]}
#typeWorkingCurveDict = {'clavicle':templateSizeObjects[1],'head':templateSizeObjects[1],'arm':templateSizeObjects[1],'leg':templateSizeObjects[0],'tail':templateSizeObjects[0],'wing':templateSizeObjects[1],'finger':templateSizeObjects[1]}
#typeAimingCurveDict = {'arm':templateSizeObjects[0],'leg':templateSizeObjects[1],'tail':templateSizeObjects[1],'wing':templateSizeObjects[0],}
modeDict = {'finger':'parentDuplicate','foot':'footBase','head':'child','arm':'radialOut','leg':'radialDown','tail':'cvBack','wing':'radialOut','clavicle':'radialOut'}
aimSpreads = ['arm','leg','wing']

class Limb(ModuleFactory):
    """
    Limb class which inherits the ModuleFactory master class
    """
    def __init__(self,*a,**kw):
        initializeOnly = kw.pop('initializeOnly',False)
        
        guiFactory.doPrintReportStart()
        
        #Initialize the standard module
        ModuleFactory.__init__(self,initializeOnly = initializeOnly,*a,**kw)
        
        self.moduleClass = 'Limb'
        
        #Then check the subclass specific stuff
        if self.refState or initializeOnly:
            guiFactory.report("'%s' Limb initializing..."%self.ModuleNull.nameShort)
            if not self.initializeModule():
                guiFactory.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%self.ModuleNull.nameShort)
                return False
            
        else:
            if not self.verifyModule():
                guiFactory.warning("'%s' failed to verify!"%self.ModuleNull.nameShort)
                return False

            
        guiFactory.report("'%s' checks out"%self.ModuleNull.nameShort)
        guiFactory.doPrintReportEnd()
            
    def verifyModule(self,*a,**kw):
        """
        Verifies the integrity of the Limb module. Repairing and restoring broken connections or deleted items.
        """        
        #Initialize all of our options
        ModuleFactory.verifyModule(self,*a,**kw)
        
        for k in defaultSettings.keys():
            try:
                self.__dict__[k]
            except:
                self.__dict__[k] = defaultSettings[k]
            
        self.afModuleType = AttrFactory(self.ModuleNull,'moduleType','string',value= self.partType)
        
        if self.infoNulls['setupOptions']:
            self.SetupOptionsNull = ObjectFactory( self.infoNulls['setupOptions'].value )
            self.optionFK = AttrFactory(self.SetupOptionsNull,'fk','bool',initialValue= self.fk)
            self.optionIK = AttrFactory(self.SetupOptionsNull,'ik','bool',initialValue= self.ik)
            self.optionStretchy = AttrFactory(self.SetupOptionsNull,'stretchy','bool',initialValue= self.stretchy)
            self.optionBendy = AttrFactory(self.SetupOptionsNull,'bendy','bool',initialValue= self.bendy)
            
            self.optionHandles = AttrFactory(self.SetupOptionsNull,'handles','int',initialValue=self.handles)
            self.optionRollJoints = AttrFactory(self.SetupOptionsNull,'rollJoints','int',initialValue=self.rollJoints)
            self.optionStiffIndex= AttrFactory(self.SetupOptionsNull,'stiffIndex','int',initialValue=self.stiffIndex)
            self.optionCurveDegree= AttrFactory(self.SetupOptionsNull,'curveDegree','int',initialValue=self.curveDegree)
        else:
            guiFactory.warning("Setup options null is missing from '%s'. Rebuild"%self.ModuleNull.nameShort)
            return False
        if self.infoNulls['visibilityOptions']:
            self.VisibilityOptionsNull = ObjectFactory( self.infoNulls['visibilityOptions'].value )
            
            self.visOrientHelpers = AttrFactory(self.VisibilityOptionsNull,'visOrientHelpers','bool',initialValue=0)
            self.visControlHelpers = AttrFactory(self.VisibilityOptionsNull,'visControlHelpers','bool',initialValue=0)
        else:
            guiFactory.warning("Visibility options null is missing from '%s'. Rebuild"%self.ModuleNull.nameShort)
            return False
        
        return True
    
    def initializeModule(self):
        """
        Verifies the integrity of the Limb module. Repairing and restoring broken connections or deleted items.
        """        
        #Initialize all of our options
        ModuleFactory.initializeModule(self)
        
        self.afModuleType = AttrFactory(self.ModuleNull,'moduleType')
        
        LimbSettingAttrs ={'fk':'bool',
                    'ik':'bool',
                    'stretchy':'bool',
                    'bendy':'bool',
                    'handles':'int',
                    'rollJoints':'int',
                    'stiffIndex':'int',
                    'curveDegree':'int'}
        
        if self.infoNulls['setupOptions']:
            self.SetupOptionsNull = ObjectFactory( self.infoNulls['setupOptions'].value )
            self.optionFK = AttrFactory(self.SetupOptionsNull,'fk')
            self.optionIK = AttrFactory(self.SetupOptionsNull,'ik')
            self.optionStretchy = AttrFactory(self.SetupOptionsNull,'stretchy')
            self.optionBendy = AttrFactory(self.SetupOptionsNull,'bendy')
            
            self.optionHandles = AttrFactory(self.SetupOptionsNull,'handles')
            self.optionRollJoints = AttrFactory(self.SetupOptionsNull,'rollJoints')
            self.optionStiffIndex= AttrFactory(self.SetupOptionsNull,'stiffIndex')
            self.optionCurveDegree= AttrFactory(self.SetupOptionsNull,'curveDegree')
            
        if self.infoNulls['visibilityOptions']:
            self.VisibilityOptionsNull = ObjectFactory( self.infoNulls['visibilityOptions'].value )
            self.visOrientHelpers = AttrFactory(self.VisibilityOptionsNull,'visOrientHelpers')
            self.visControlHelpers = AttrFactory(self.VisibilityOptionsNull,'visControlHelpers')
                    
        return True
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> Sizing
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def doInitialSize(self,PuppetInstance,*a,**kw):
        guiFactory.report("Sizing via Limb - '%s'"%self.ModuleNull.nameBase)
        
        if not self.moduleParent:
            guiFactory.report("Root module mode!")            
            #>>>Get some info
            locInfoBuffer = ModuleFactory.doCreateStartingPositionLoc(self,'innerChild',PuppetInstance.templateSizeObjects['start'],PuppetInstance.templateSizeObjects['end'])
            print locInfoBuffer
            baseDistance = ModuleFactory.doGeneratePartBaseDistance(self,PuppetInstance,locInfoBuffer[0])
            print "buffer is '%s'"%baseDistance
            
            return self.doGenerateInitialPositionData(PuppetInstance,locInfoBuffer,baseDistance) 
        
        
    """
    def doInitialSize(self,PuppetInstance,*a,**kw):
        guiFactory.report("Sizing via Limb - '%s'"%self.ModuleNull.nameBase)
        
        #>>>Get some info
        locInfoBuffer = ModuleFactory.doCreateStartingPositionLoc(self,'innerChild',PuppetInstance.templateSizeObjects['start'],PuppetInstance.templateSizeObjects['end'])
        print locInfoBuffer
        
        baseDistance = ModuleFactory.doGeneratePartBaseDistance(self,PuppetInstance,locInfoBuffer[0])
        print "buffer is '%s'"%baseDistance
        
        buffer = self.doGenerateInitialPositionData(PuppetInstance,locInfoBuffer,baseDistance) 
        """
    
        
        
    def doGenerateInitialPositionData(self, PuppetInstance, startLocList,*a,**kw):
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
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Define Subclasses
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      
class Segment(Limb):
    def __init__(self, moduleName = 'segment',*a, **kw):
        moduleParent = kw.pop('moduleParent',False)
        handles = kw.pop('handles',3)
        position = kw.pop('position',False)
        nameModifier = kw.pop('nameModifier',False)
        direction = kw.pop('direction',False)
        directionModifier = kw.pop('directionModifier',False)
        initializeOnly = kw.pop('initializeOnly',False)

        self.partType = 'segment'
        self.stiffIndex = 0
        self.curveDegree = 1
        self.rollJoints = 3
        self.handles = handles
        
        
        Limb.__init__(self,moduleName,initializeOnly = initializeOnly,*a, **kw)
        
class SegmentBak(Limb):
    def __init__(self, moduleName ='segment', moduleParent = False, handles = 3, position = False, direction = False, directionModifier = False, nameModifier = False,initializeOnly = False,*a, **kw):
        moduleName = kw.pop('moduleName','segment')

        self.partType = 'segment'
        self.stiffIndex = 0
        self.curveDegree = 1
        self.rollJoints = 3
        self.handles = handles
        
        
        Limb.__init__(self,moduleName,moduleParent,position,direction,directionModifier,nameModifier,initializeOnly, *a,**kw)
        
        