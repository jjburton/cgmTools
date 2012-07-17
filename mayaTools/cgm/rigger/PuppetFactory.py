#=================================================================================================================================================
#=================================================================================================================================================
#	RigFactory - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for finding stuff
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2012 CG Monks - All Rights Reserved.
#
#=================================================================================================================================================
import maya.cmds as mc
from cgm.lib.classes import NameFactory
from cgm.lib.classes.AttrFactory import *
from cgm.lib.classes.BufferFactory import *
from cgm.lib.classes.ObjectFactory import *

from cgm.rigger import ModuleFactory
reload(ModuleFactory)

from cgm.rigger.ModuleFactory import *
from cgm.rigger.lib.Limb.module import *


import random
import re
import copy

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

axisDirectionsByString = ['x+','y+','z+','x-','y-','z-']
geoTypes = 'nurbsSurface','mesh','poly','subdiv'
CharacterTypes = 'Bio','Mech','Prop'

moduleTypeToFunctionDict = {'None':ModuleFactory,
                            'segment':Segment}

moduleTypeToMasterClassDict = {'None':['none','None',False],
                               'Limb':['segment']}
class PuppetFactory():
    """ 
    Character
    
    """
    def __init__(self,characterName = '',characterType = ''):
        """ 
        Intializes an optionVar class handler
        
        Keyword arguments:
        varName(string) -- name for the optionVar
        """
        #Default to creation of a var as an int value of 0
        ### input check         
        self.masterNulls = modules.returnPuppetObjects()
        self.nameBase = characterName
        self.geo = []
        self.modules = []
        self.templateSizeObjects = {}
        self.Module = {}
        self.PuppetNull = False
        self.refState = False
        
        guiFactory.doPrintReportStart()
        
        if mc.objExists(characterName):
            #Make a name dict to check
            if search.findRawTagInfo(characterName,'cgmModuleType') == 'master':
                self.nameBase = characterName
                self.PuppetNull = ObjectFactory(characterName)
                self.refState = self.PuppetNull.refState
                guiFactory.report("'%s' exists. Checking..."%characterName)

            else:
                guiFactory.warning("'%s' isn't a puppet module. Can't initialize"%characterName)
                return
        else:
            if self.nameBase == '':
                randomOptions = ['ReallyNameMe','SolarSystem_isADumbName','David','Josh','Ryan','NameMe','Homer','Georgie','PleaseNameMe','NAMEThis','PleaseNameThisPuppet']
                buffer = random.choice(randomOptions)
                cnt = 0
                while mc.objExists(buffer) and cnt<10:
                    cnt +=1
                    buffer = random.choice(randomOptions)
                self.nameBase = buffer            
                       
        if not self.refState:
            if not self.verifyPuppetNull():
                guiFactory.warning("'%s' failed to verify!"%characterName)
                return 
        else:
            guiFactory.report("'%s' Referenced. Cannot verify, initializing..."%characterName)
            if not self.initializePuppet():
                guiFactory.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%moduleName)
                return         
        
        self.checkGeo()
        self.verifyTemplateSizeObject(False)
        self.getModules()
        guiFactory.report("'%s' checks out"%self.nameBase)
        guiFactory.doPrintReportEnd()
                
    def verifyPuppetNull(self):
        """ 
        Verifies the various components a masterNull for a character/asset. If a piece is missing it replaces it.
        
        RETURNS:
        success(bool)
        """            
        #Puppet null
        try:
            if not mc.objExists(self.nameBase):
                buffer = mc.group(empty=True)
                self.PuppetNull = ObjectFactory(buffer)
            else:
                self.PuppetNull = ObjectFactory(self.nameBase)
            
            self.PuppetNull.store('cgmName',self.nameBase,True)   
            self.PuppetNull.store('cgmType','ignore')
            self.PuppetNull.store('cgmModuleType','master')
                 
            if self.PuppetNull.nameShort != self.nameBase:
                self.PuppetNull.doName(True)
            
            attributes.doSetLockHideKeyableAttr(self.PuppetNull.nameShort,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
        except:
            guiFactory.warning("Puppet null failed!")
            
        #Checks our modules container null
        created = False
        #Initialize message attr
        self.afModulesGroup = AttrFactory(self.PuppetNull,'modulesGroup','message')
        if not self.afModulesGroup.value:
            self.ModulesGroup = ObjectFactory(mc.group(empty=True))            
            self.afModulesGroup.doStore(self.ModulesGroup.nameShort)
            created = True
        else:
            self.ModulesGroup = ObjectFactory(self.afModulesGroup.value)
            
        self.ModulesGroup.store('cgmName','modules')   
        self.ModulesGroup.store('cgmType','group')
        
        self.ModulesGroup.doParent(self.PuppetNull.nameShort)
        
        if created:
            self.ModulesGroup.doName(True)
            
        self.afModulesGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.ModulesGroup.nameShort)

            
        #Checks our noTransform container null
        created = False        
        self.afNoTransformGroup = AttrFactory(self.PuppetNull,'noTransformGroup','message')
        if not self.afNoTransformGroup.value:
            self.NoTransformGroup = ObjectFactory(mc.group(empty=True))
            self.afNoTransformGroup.doStore(self.NoTransformGroup.nameShort)
            created = True
        else:
            self.NoTransformGroup = ObjectFactory(self.afNoTransformGroup.value)
            
        self.NoTransformGroup.store('cgmName','noTransform')   
        self.NoTransformGroup.store('cgmType','group')
        
        self.NoTransformGroup.doParent(self.PuppetNull.nameShort)
        
        if created:
            self.NoTransformGroup.doName(True)
            
        self.afNoTransformGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.NoTransformGroup.nameShort)
         
            
        #Checks our geo container null
        created = False        
        self.afGeoGroup = AttrFactory(self.PuppetNull,'geoGroup','message')
        if not self.afGeoGroup.value:
            self.GeoGroup = ObjectFactory(mc.group(empty=True))
            self.afGeoGroup.doStore(self.GeoGroup.nameShort)            
            created = True
        else:
            self.GeoGroup = ObjectFactory(self.afGeoGroup.value)
            
        self.GeoGroup.store('cgmName','geo')   
        self.GeoGroup.store('cgmType','group')
        
        self.GeoGroup.doParent(self.afNoTransformGroup.value)
        
        if created:
            self.GeoGroup.doName(True)
            
        self.afGeoGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.GeoGroup.nameShort)
        
            
        #Checks master info null
        created = False        
        self.afPuppetInfo = AttrFactory(self.PuppetNull,'info','message')
        if not self.afPuppetInfo.value:
            self.PuppetInfoNull = ObjectFactory(mc.group(empty=True))
            self.afPuppetInfo.doStore(self.PuppetInfoNull.nameShort)               
            created = True
        else:
            self.PuppetInfoNull = ObjectFactory(self.afPuppetInfo.value)
            
            
        self.PuppetInfoNull.store('cgmName','master')   
        self.PuppetInfoNull.store('cgmType','info')
        
        self.PuppetInfoNull.doParent(self.PuppetNull.nameShort)
        
        if created:
            self.PuppetInfoNull.doName(True)
            
        self.afPuppetInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.PuppetInfoNull.nameShort)
        
            
        #Checks modules info null
        created = False        
        self.afModuleInfo = AttrFactory(self.afPuppetInfo.value,'modules','message')
        if not self.afModuleInfo.value:
            self.ModuleInfoNull = ObjectFactory(mc.group(empty=True))
            self.afModuleInfo.doStore(self.ModuleInfoNull.nameShort)     
            created = True
        else:
            self.ModuleInfoNull = ObjectFactory(self.afModuleInfo.value)
            
        self.ModuleInfoNull.store('cgmName','modules')   
        self.ModuleInfoNull.store('cgmType','info')
        
        self.ModuleInfoNull.doParent(self.PuppetInfoNull.nameShort)
        
        if created:
            self.ModuleInfoNull.doName(True)
            
        self.afModuleInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.ModuleInfoNull.nameShort)
        
        #Initialize our modules null as a buffer
        self.ModulesBuffer = BufferFactory(self.ModuleInfoNull.nameShort)
        
        #Checks geo info null
        created = False        
        self.afGeoInfo = AttrFactory(self.afPuppetInfo.value,'geo','message')
        if not self.afGeoInfo.value:
            self.GeoInfoNull = ObjectFactory(mc.group(empty=True))
            self.afGeoInfo.doStore(self.GeoInfoNull.nameShort)              
            created = True
        else:
            self.GeoInfoNull = ObjectFactory(self.afGeoInfo.value)
            
        self.GeoInfoNull.store('cgmName','geo')   
        self.GeoInfoNull.store('cgmType','info')
        
        self.GeoInfoNull.doParent(self.afPuppetInfo.value)
        
        if created:
            self.GeoInfoNull.doName(True)
            
        self.afGeoInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.GeoInfoNull.nameShort) 
        
            
        #Checks settings info null
        created = False        
        self.afSettingsInfo = AttrFactory(self.afPuppetInfo.value,'settings','message')
        if not self.afSettingsInfo.value:
            self.SettingsInfoNull = ObjectFactory(mc.group(empty=True))
            self.afSettingsInfo.doStore(self.SettingsInfoNull.nameShort)   
            created = True
        else:
            self.SettingsInfoNull = ObjectFactory(self.afSettingsInfo.value)
            
        self.SettingsInfoNull.store('cgmName','settings')   
        self.SettingsInfoNull.store('cgmType','info')
        defaultFont = modules.returnSettingsData('defaultTextFont')
        self.SettingsInfoNull.store('font',defaultFont)
        
        self.SettingsInfoNull.doParent(self.afPuppetInfo.value)
        
        if created:
            self.SettingsInfoNull.doName(True)
            
        self.afSettingsInfo.updateData()   
        
        
        self.optionPuppetMode = AttrFactory(self.SettingsInfoNull,'cgmModuleMode','int',initialValue = 0)      
        
        self.optionAimAxis= AttrFactory(self.SettingsInfoNull,'axisAim','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=2) 
        self.optionUpAxis= AttrFactory(self.SettingsInfoNull,'axisUp','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=1) 
        self.optionOutAxis= AttrFactory(self.SettingsInfoNull,'axisOut','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=0)         
            
        attributes.doSetLockHideKeyableAttr(self.SettingsInfoNull.nameShort) 
        
        return True
     
    def initializePuppet(self):
        """ 
        Verifies the various components a masterNull for a character/asset. If a piece is missing it replaces it.
        
        RETURNS:
        success(bool)
        """            
        #Puppet null       
        if not attributes.doGetAttr(self.PuppetNull.nameShort,'cgmName'):
            return False
        if attributes.doGetAttr(self.PuppetNull.nameShort,'cgmType') != 'ignore':
            return False
        if attributes.doGetAttr(self.PuppetNull.nameShort,'cgmModuleType') != 'master':
            return False        
        
        self.afModulesGroup = AttrFactory(self.PuppetNull,'modulesGroup')
        if not self.afModulesGroup.value:
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.afModulesGroup.attr)
            return False
        else:
            self.ModulesGroup = ObjectFactory(self.afModulesGroup.value)

        self.afNoTransformGroup = AttrFactory(self.PuppetNull,'noTransformGroup')
        if not self.afNoTransformGroup.value:
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.afNoTransformGroup.attr)
            return False
        else:
            self.NoTransformGroup = ObjectFactory(self.afNoTransformGroup.value)        
            
        self.afGeoGroup = AttrFactory(self.PuppetNull,'geoGroup')
        if not self.afGeoGroup.value:
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.afGeoGroup.attr)
            return False
        else:
            self.GeoGroup = ObjectFactory(self.afGeoGroup.value)        
         
        self.afPuppetInfo = AttrFactory(self.PuppetNull,'info')
        if not self.afPuppetInfo.value:
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.afPuppetInfo.attr)
            return False
        
        else:
            self.PuppetInfoNull = ObjectFactory(self.afPuppetInfo.value)                    
            self.afModuleInfo = AttrFactory(self.PuppetInfoNull,'modules')
            if not self.afModuleInfo.value:
                guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.afModuleInfo.attr)
                return False  
            else:
                #Initialize our modules null as a buffer
                self.ModuleInfoNull = ObjectFactory(self.afModuleInfo.value)
                self.ModulesBuffer = BufferFactory(self.afModuleInfo.value)                
            
            self.afGeoInfo = AttrFactory(self.PuppetInfoNull,'geo')
            if not self.afGeoInfo.value:
                guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.afGeoInfo.attr)
                return False
            else:
                self.GeoInfoNull = ObjectFactory(self.afGeoInfo.value)             
            
            self.afSettingsInfo = AttrFactory(self.PuppetInfoNull,'settings')
            if not self.afSettingsInfo.value:
                guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.afSettingsInfo.attr)
                return False 
            else:
                self.SettingsInfoNull = ObjectFactory(self.afSettingsInfo.value,)
                
                self.optionPuppetMode = AttrFactory(self.SettingsInfoNull,'cgmModuleMode')
                self.optionAimAxis= AttrFactory(self.SettingsInfoNull,'axisAim') 
                self.optionUpAxis= AttrFactory(self.SettingsInfoNull,'axisUp') 
                self.optionOutAxis= AttrFactory(self.SettingsInfoNull,'axisOut')
                
        return True
            
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Modules
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def getModules(self):
        """
        Intializes all connected modules of a puppet
        """           
        self.Module = {}
        if self.ModulesBuffer.bufferList:
            for i,m in enumerate(self.ModulesBuffer.bufferList):
                modType = search.returnTagInfo(m,'moduleType') or False
                if modType in moduleTypeToFunctionDict.keys():
                    self.Module[i] = moduleTypeToFunctionDict[modType](m)
                else:
                    guiFactory.warning("'%s' is not a module type found in the moduleTypeToFunctionDict. Cannot initialize")

    def createModule(self,moduleType,*a,**kw):
        """
        Create and connect a new module
        """   
        if moduleType in moduleTypeToFunctionDict.keys():
            tmpModule = moduleTypeToFunctionDict[moduleType](forceNew=True)
            self.ModulesBuffer.store(tmpModule.ModuleNull.nameShort)
            
            self.Module[ self.ModulesBuffer.bufferList.index(tmpModule.ModuleNull.nameShort) ] = tmpModule
            
            moduleNullBuffer = rigging.doParentReturnName(tmpModule.ModuleNull.nameShort,self.afModulesGroup.value)             
        else:
            guiFactory.warning("'%s' is not a module type found in the moduleTypeToFunctionDict. Cannot initialize"%moduleType)

        
    def addModule(self,module,*a,**kw):
        """
        
        """
        if module in self.ModulesBuffer.bufferList:
            return guiFactory.warning("'%s' already connnected to '%s'"%(module,self.nameBase))

        elif mc.objExists(module):
            # If it exists, check type to initialize and add
            modType = search.returnTagInfo(module,'moduleType') or False
            if modType in moduleTypeToFunctionDict.keys():
                self.ModulesBuffer.store(module)
                moduleNullBuffer = rigging.doParentReturnName(module,self.afModulesGroup.value)
                self.Module[ self.ModulesBuffer.bufferList.index(module) ] = moduleTypeToFunctionDict[modType](moduleNullBuffer)
                
            else:
                guiFactory.warning("'%s' is not a module type found in the moduleTypeToFunctionDict. Cannot initialize")
            
        else:
            guiFactory.warning("'%s' is not a module type found in the moduleTypeToFunctionDict. Cannot initialize"%module)
    
    def removeModule(self,moduleName,*a,**kw):
        if moduleName in self.ModulesBuffer.bufferList:
            #Clear our instanced module
            index = self.ModulesBuffer.bufferList.index(moduleName)
            if index:
                self.Module[index] = False
            self.ModulesBuffer.remove(moduleName)
            buffer = rigging.doParentToWorld(moduleName)
        else:
            guiFactory.warning("'%s' doesn't seem to be a connected module. Cannot remove"%moduleName)
    
    def deleteModule(self,moduleName,*a,**kw):
        if moduleName in self.ModulesBuffer.bufferList:
            #Clear our instanced module            
            index = self.ModulesBuffer.bufferList.index(moduleName)
            if index:
                self.Module[index] = False
                
            self.ModulesBuffer.remove(moduleName)
            buffer = rigging.doParentToWorld(moduleName)
            mc.delete(buffer)
        else:
            guiFactory.warning("'%s' doesn't seem to be a connected module. Cannot delete"%moduleName)
        
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Size objects
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def verifyTemplateSizeObject(self,create = False):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Returns an existing template size object or makes one and returns it
        
        ARGUMENTS:
        masterNull(list)
        
        RETURNS:
        returnList(list) - size object controls
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        templateSizeObject = attributes.returnMessageObject(self.PuppetNull.nameShort,'templateSizeObject')
        if not mc.objExists(templateSizeObject) and create:
            self.createSizeTemplateControl()
            guiFactory.report("'%s' has template object '%s'"%(self.PuppetNull.nameShort,templateSizeObject))
            return True
        elif templateSizeObject:
            self.templateSizeObjects['root'] = templateSizeObject
            self.templateSizeObjects['start'] = attributes.returnMessageObject(templateSizeObject,'controlStart')
            self.templateSizeObjects['end'] = attributes.returnMessageObject(templateSizeObject,'controlEnd')
            for key in self.templateSizeObjects.keys():
                if not self.templateSizeObjects[key]:
                    #self.templateSizeObjects = {}
                    guiFactory.warning("'%s' didn't check out. Rebuildling..."%(key))
                    try:
                        mc.delete(templateSizeObject)
                        self.createSizeTemplateControl()
                    except:
                        guiFactory.warning("Rebuild failed")                        
                    return False
            guiFactory.report("'%s' has template object '%s'"%(self.PuppetNull.nameShort,templateSizeObject))
            return True
            
        guiFactory.warning("Size template failed to verify")
        return False
    
    def isRef(self):
        if mc.referenceQuery(self.PuppetNull.nameShort, isNodeReferenced=True):
            self.refState = True
            self.refPrefix = search.returnReferencePrefix(self.PuppetNull.nameShort)
            return
        self.refState = False
        self.refPrefix = None
        
    def createSizeTemplateControl(self):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
        DESCRIPTION:
        Generates a sizeTemplateObject. It's been deleted, it recreates it. Guess the size based off of there
        being a mesh there. If there is no mesh, it sets sets an intial size of a 
        [155,170,29] unit character.
        
        ARGUMENTS:
        self.PuppetNull.nameShort(string)
        
        RETURNS:
        returnList(list) = [startCrv(string),EndCrv(list)]
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Get info
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        centerColors = modules.returnSettingsData('colorCenter',True)
        font = mc.getAttr((self.afSettingsInfo.value+'.font'))
        
        """ checks for there being anything in our geo group """
        if not self.geo:
            return guiFactory.warning('Need some geo defined to make this tool worthwhile')
            boundingBoxSize =  modules.returnSettingsDataAsFloat('meshlessSizeTemplate')
        else:
            boundingBoxSize = distance.returnBoundingBoxSize (self.afGeoGroup.value)
            boundingBox = mc.exactWorldBoundingBox(self.afGeoGroup.value)
            
        
        """determine orienation """
        maxSize = max(boundingBoxSize)
        matchIndex = boundingBoxSize.index(maxSize)
        
        """Find the pivot of the bounding box """
        pivotPosition = distance.returnCenterPivotPosition(self.afGeoGroup.value)
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Get our positions
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        print self.optionPuppetMode.value
        if self.optionPuppetMode.value == 0:
            #If bio...
            if matchIndex == 1 or matchIndex == 0:
                #Vertical
                posBuffers = [[0,.5,0],[0,.75,0]]
                width = (boundingBoxSize[0]/2)
                height = (boundingBoxSize[1])
                depth = boundingBoxSize[2]
                
                for cnt,pos in enumerate(posBuffers):
                    posBuffer = posBuffers[cnt]
                    posBuffer[0] = 0
                    posBuffer[1] = (posBuffer[1] * height)
                    posBuffer[2] = 0
                    
            elif matchIndex == 2:
                #Horizontal
                posBuffers = [[0,0,-.33],[0,0,.66]]
                width = boundingBoxSize[1]
                height = boundingBoxSize[2]/2
                depth = (boundingBoxSize[0])
                
                for cnt,pos in enumerate(posBuffers):
                    posBuffer = posBuffers[cnt]
                    posBuffer[0] = 0
                    posBuffer[1] = boundingBoxSize[1] * .75
                    posBuffer[2] = (posBuffer[2] * height)
                          
        else:
            #Otherwise 
            if matchIndex == 1 or matchIndex == 0:
                #Vertical
                width = (boundingBoxSize[0]/2)
                height = (boundingBoxSize[1])
                depth = boundingBoxSize[2]                
                posBuffers = [[0,boundingBox[1],0],[0,boundingBox[4],0]]

            elif matchIndex == 2:
                #Horizontal
                width = boundingBoxSize[0]
                height = boundingBoxSize[2]/2
                depth = (boundingBoxSize[1])
                startHeight = max([boundingBox[4],boundingBox[1]]) - depth/2
                print startHeight
                posBuffers = [[0,startHeight,boundingBox[2]],[0,startHeight,boundingBox[5]]]
                    
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Making the controls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>       
        """ make our control object """
        startCurves = []
        startCurve = curves.createControlCurve('circle',depth*.8)
        mc.xform(startCurve,t=posBuffers[0],ws=True)
        attributes.doSetAttr(startCurve,'rotateOrder',5)
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
        attributes.doSetAttr(endCurve,'rotateOrder',5)        
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
        attributes.storeInfo(sizeCurveControlStart,'cgmName',(self.PuppetNull.nameShort+'.cgmName'))
        attributes.storeInfo(sizeCurveControlStart,'cgmDirection','start')
        attributes.storeInfo(sizeCurveControlStart,'cgmType','templateSizeObject')
        sizeCurveControlStart = NameFactory.doNameObject(sizeCurveControlStart)
        mc.makeIdentity(sizeCurveControlStart, apply = True, t=True,s=True,r=True)
    
        attributes.storeInfo(sizeCurveControlEnd,'cgmName',(self.PuppetNull.nameShort+'.cgmName'))
        attributes.storeInfo(sizeCurveControlEnd,'cgmDirection','end')
        attributes.storeInfo(sizeCurveControlEnd,'cgmType','templateSizeObject')
        sizeCurveControlEnd  = NameFactory.doNameObject(sizeCurveControlEnd)
        
        endGroup = rigging.groupMeObject(sizeCurveControlEnd)
        mc.makeIdentity(sizeCurveControlEnd, apply = True, t=True,s=True,r=True)
        
        mc.parentConstraint(sizeCurveControlStart,endGroup,maintainOffset = True)
        
        """ make control group """
        controlGroup = rigging.groupMeObject(sizeCurveControlStart)
        attributes.storeInfo(controlGroup,'cgmName',(self.PuppetNull.nameShort+'.cgmName'))
        attributes.storeInfo(controlGroup,'cgmType','templateSizeObjectGroup')
        controlGroup = NameFactory.doNameObject(controlGroup)

        
        endGroup = rigging.doParentReturnName(endGroup,controlGroup)
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Getting data ready
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
        attributes.storeInfo(controlGroup,'controlStart',sizeCurveControlStart)
        attributes.storeInfo(controlGroup,'controlEnd',sizeCurveControlEnd)        
        attributes.storeInfo(self.PuppetNull.nameShort,'templateSizeObject',controlGroup)
        
        self.templateSizeObjects['root'] = controlGroup
        self.templateSizeObjects['start'] = sizeCurveControlStart
        self.templateSizeObjects['end'] = sizeCurveControlEnd  
       
        returnList=[]
        returnList.append(sizeCurveControlStart)
        returnList.append(sizeCurveControlEnd)
        return returnList

        
    def addGeo(self):
        """ 
        Add geo to a puppet
        """
        assert self.afGeoGroup.value is not False,"No geo group found!"
        
        selection = mc.ls(sl=True,flatten=True,long=True) or []
        
        if not selection:
            guiFactory.warning("No selection found to add to '%s'"%self.nameBase)
        
        returnList = []    
        for o in selection:
            if search.returnObjectType(o) in geoTypes:
                if self.afGeoGroup.value not in search.returnAllParents(o,True):
                    o = rigging.doParentReturnName(o,self.afGeoGroup.value)
                    self.geo.append(o)
                else:
                    guiFactory.warning("'%s' already a part of '%s'"%(o,self.nameBase))
            else:
                guiFactory.warning("'%s' doesn't seem to be geo. Not added to '%s'"%(o,self.nameBase))
    
    def checkGeo(self):
        """
        Check a puppet's geo that it is actually geo
        """
        assert self.afGeoGroup.value is not False,"No geo group found!"
        self.geo = []
        children = search.returnAllChildrenObjects(self.afGeoGroup.value)
        if not children:
            return False
    
        for o in children:
            if search.returnObjectType(o) in geoTypes:
                buff = mc.ls(o,long=True)
                self.geo.append(buff[0])
            else:
                rigging.doParentToWorld(o)
                guiFactory.warning("'%s' isn't geo, removing from group."%o)
        return True
    
    def doSetMode(self,i):
        assert i <(len(CharacterTypes)),"%i isn't a viable base pupppet type"%i
        self.optionPuppetMode.set(i)
        
    def doSetAimAxis(self,i):
        """
        Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
        Then Up, and Out is last.
        
        """
        assert i < 6,"%i isn't a viable aim axis integer"%i
        
        self.optionAimAxis.set(i)
        if self.optionUpAxis.value == self.optionAimAxis.value:
            self.doSetUpAxis(i)
        if self.optionOutAxis.value == self.optionAimAxis.value:
            self.doSetOutAxis(i)
            
        return True
        
    def doSetUpAxis(self,i):
        """
        Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
        Then Up, and Out is last.
        
        """        
        assert i < 6,"%i isn't a viable up axis integer"%i
        axisBuffer = range(6)
        axisBuffer.remove(self.optionAimAxis.value)
        
        if i != self.optionAimAxis.value:
            self.optionUpAxis.set(i)  
        else:
            self.optionUpAxis.set(axisBuffer[0]) 
            guiFactory.warning("Aim axis has '%s'. Changed up axis to '%s'. Change aim setting if you want this seeting"%(axisDirectionsByString[self.optionAimAxis.value],axisDirectionsByString[self.optionUpAxis.value]))                  
            axisBuffer.remove(axisBuffer[0])
            
        if self.optionOutAxis.value in [self.optionAimAxis.value,self.optionUpAxis.value]:
            for i in axisBuffer:
                if i not in [self.optionAimAxis.value,self.optionUpAxis.value]:
                    self.doSetOutAxis(i)
                    guiFactory.warning("Setting conflict. Changed out axis to '%s'"%axisDirectionsByString[i])                    
                    break
        return True        
        
        
    def doSetOutAxis(self,i):
        assert i < 6,"%i isn't a viable aim axis integer"%i
        
        if i not in [self.optionAimAxis.value,self.optionUpAxis.value]:
            self.optionOutAxis.set(i)
        else:
            axisBuffer = range(6)
            axisBuffer.remove(self.optionAimAxis.value)
            axisBuffer.remove(self.optionUpAxis.value)
            self.optionOutAxis.set(axisBuffer[0]) 
            guiFactory.warning("Setting conflict. Changed out axis to '%s'"%axisDirectionsByString[ axisBuffer[0] ])                    


        
    def doRenamePuppet(self,newName):
        """
        Rename Puppet null
        """
        if newName == self.PuppetNull.cgm['cgmName']:
            return guiFactory.warning("Already named '%s'"%newName)
        
        self.PuppetNull.store('cgmName ',newName)   
        self.nameBase = newName
        self.PuppetNull.doName()
        self.initializePuppet()
        self.getModules()
        guiFactory.warning("Puppet renamed as '%s'"%newName)
        
        