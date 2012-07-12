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

axisDirections = ['x+','y+','z+','x-','y-','z-']
geoTypes = 'nurbsSurface','mesh','poly','subdiv'
CharacterTypes = 'Bio','Mech','Prop'
moduleTypeToFunctionDict = {'None':ModuleFactory,
                            'segment':Segment}

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
        self.refPrefix = None
        self.refState = False        
        self.masterNulls = modules.returnPuppetObjects()
        self.nameBase = characterName
        self.geo = []
        self.modules = []
        self.templateSizeObjects = {}
        
        guiFactory.doPrintReportStart()
        
        
        if mc.objExists(characterName):
            #Make a name dict to check
            if search.findRawTagInfo(characterName,'cgmModuleType') == 'master':
                self.nameBase = characterName
                self.PuppetNullName = characterName
                self.isRef()
                guiFactory.report("'%s' exists. Checking..."%characterName)

            else:
                guiFactory.warning("'%s' isn't a puppet module. Can't initialize"%moduleName)
                return False
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
                self.PuppetNullName = mc.group(empty=True)
            else:
                self.PuppetNullName = self.nameBase
            
            attributes.storeInfo(self.PuppetNullName,'cgmName',self.nameBase,True)   
            attributes.storeInfo(self.PuppetNullName,'cgmType','ignore')
            attributes.storeInfo(self.PuppetNullName,'cgmModuleType','master')
                 
            if self.PuppetNullName != self.nameBase:
                self.PuppetNullName = NameFactory.doNameObject(self.PuppetNullName,True)
            
            attributes.doSetLockHideKeyableAttr(self.PuppetNullName,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
        except:
            guiFactory.warning("Puppet null failed!")
            
        #Checks our modules container null
        created = False
        #Initialize message attr
        self.aModulesGroup = AttrFactory(self.PuppetNullName,'modulesGroup','message')
        if not self.aModulesGroup.value:
            self.aModulesGroup.doStore(mc.group(empty=True))
            created = True
            
        attributes.storeInfo(self.aModulesGroup.value ,'cgmName','modules')   
        attributes.storeInfo(self.aModulesGroup.value ,'cgmType','group')
        
        rigging.doParentReturnName(self.aModulesGroup.value,self.PuppetNullName)
        
        if created:
            NameFactory.doNameObject(self.aModulesGroup.value)
            
        self.aModulesGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.aModulesGroup.value)

            
        #Checks our noTransform container null
        created = False        
        self.aNoTransformGroup = AttrFactory(self.PuppetNullName,'noTransformGroup','message')
        if not self.aNoTransformGroup.value:
            self.aNoTransformGroup.doStore(mc.group(empty=True))
            created = True
            
        attributes.storeInfo(self.aNoTransformGroup.value ,'cgmName','noTransform')   
        attributes.storeInfo(self.aNoTransformGroup.value ,'cgmType','group')
        
        rigging.doParentReturnName(self.aNoTransformGroup.value,self.PuppetNullName)
        
        if created:
            NameFactory.doNameObject(self.aNoTransformGroup.value)
            
        self.aNoTransformGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.aNoTransformGroup.value)
         
            
        #Checks our geo container null
        created = False        
        self.aGeoGroup = AttrFactory(self.PuppetNullName,'geoGroup','message')
        if not self.aGeoGroup.value:
            self.aGeoGroup.doStore(mc.group(empty=True))
            created = True
            
        attributes.storeInfo(self.aGeoGroup.value ,'cgmName','geo')   
        attributes.storeInfo(self.aGeoGroup.value ,'cgmType','group')
        
        rigging.doParentReturnName(self.aGeoGroup.value,self.aNoTransformGroup.value)
        
        if created:
            NameFactory.doNameObject(self.aGeoGroup.value)
            
        self.aGeoGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.aGeoGroup.value)
        
        
            
        #Checks master info null
        created = False        
        self.aPuppetInfo = AttrFactory(self.PuppetNullName,'info','message')
        if not self.aPuppetInfo.value:
            self.aPuppetInfo.doStore(mc.group(empty=True))
            created = True
            
        attributes.storeInfo(self.aPuppetInfo.value ,'cgmName','master')   
        attributes.storeInfo(self.aPuppetInfo.value ,'cgmType','info')
        
        rigging.doParentReturnName(self.aPuppetInfo.value,self.PuppetNullName)
        
        if created:
            NameFactory.doNameObject(self.aPuppetInfo.value)
            
        self.aPuppetInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.aPuppetInfo.value)
        
            
        #Checks modules info null
        created = False        
        self.aModuleInfo = AttrFactory(self.aPuppetInfo.value,'modules','message')
        if not self.aModuleInfo.value:
            self.aModuleInfo.doStore(mc.group(empty=True))
            created = True
            
        attributes.storeInfo(self.aModuleInfo.value ,'cgmName','modules')   
        attributes.storeInfo(self.aModuleInfo.value ,'cgmType','info')
        
        rigging.doParentReturnName(self.aModuleInfo.value,self.aPuppetInfo.value)
        
        if created:
            NameFactory.doNameObject(self.aModuleInfo.value)
            
        self.aModuleInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.aModuleInfo.value)        
        
        #Initialize our modules null as a buffer
        self.ModulesBuffer = BufferFactory(self.aModuleInfo.value)
        
        #Checks geo info null
        created = False        
        self.aGeoInfo = AttrFactory(self.aPuppetInfo.value,'geo','message')
        if not self.aGeoInfo.value:
            self.aGeoInfo.doStore(mc.group(empty=True))
            created = True
            
        attributes.storeInfo(self.aGeoInfo.value ,'cgmName','geo')   
        attributes.storeInfo(self.aGeoInfo.value ,'cgmType','info')
        
        rigging.doParentReturnName(self.aGeoInfo.value,self.aPuppetInfo.value)
        
        if created:
            NameFactory.doNameObject(self.aGeoInfo.value)
            
        self.aGeoInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.aGeoInfo.value) 
        
            
        #Checks settings info null
        created = False        
        self.aSettingsInfo = AttrFactory(self.aPuppetInfo.value,'settings','message')
        if not self.aSettingsInfo.value:
            self.aSettingsInfo.doStore(mc.group(empty=True))
            created = True
            
        attributes.storeInfo(self.aSettingsInfo.value ,'cgmName','settings')   
        attributes.storeInfo(self.aSettingsInfo.value ,'cgmType','info')
        defaultFont = modules.returnSettingsData('defaultTextFont')
        
        rigging.doParentReturnName(self.aSettingsInfo.value,self.aPuppetInfo.value)
        
        if created:
            NameFactory.doNameObject(self.aSettingsInfo.value)
            
        self.aSettingsInfo.updateData()   
        
        attributes.storeInfo(self.aSettingsInfo.value,'font',defaultFont)
        
        self.aPuppetMode = AttrFactory(self.aSettingsInfo.value,'cgmModuleMode','int',initialValue = 0)      
        
        self.aAimAxis= AttrFactory(self.aSettingsInfo.value,'axisAim','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=2) 
        self.aUpAxis= AttrFactory(self.aSettingsInfo.value,'axisUp','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=1) 
        self.aOutAxis= AttrFactory(self.aSettingsInfo.value,'axisOut','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=0)         
            
        attributes.doSetLockHideKeyableAttr(self.aSettingsInfo.value) 
        
        return True
     
    def initializePuppet(self):
        """ 
        Verifies the various components a masterNull for a character/asset. If a piece is missing it replaces it.
        
        RETURNS:
        success(bool)
        """            
        #Puppet null
        self.PuppetNullName = self.nameBase
        
        if not attributes.doGetAttr(self.PuppetNullName,'cgmName'):
            return False
        if attributes.doGetAttr(self.PuppetNullName,'cgmType') != 'ignore':
            return False
        if attributes.doGetAttr(self.PuppetNullName,'cgmModuleType') != 'master':
            return False        
        
        self.aModulesGroup = AttrFactory(self.PuppetNullName,'modulesGroup')
        if not self.aModulesGroup.value:
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.aModulesGroup.attr)
            return False

        self.aNoTransformGroup = AttrFactory(self.PuppetNullName,'noTransformGroup')
        if not self.aNoTransformGroup.value:
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.aNoTransformGroup.attr)
            return False
            
        self.aGeoGroup = AttrFactory(self.PuppetNullName,'geoGroup')
        if not self.aGeoGroup.value:
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.aGeoGroup.attr)
            return False
         
        self.aPuppetInfo = AttrFactory(self.PuppetNullName,'info')
        if not self.aPuppetInfo.value:
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.aPuppetInfo.attr)
            return False
        
        else:
            self.aModuleInfo = AttrFactory(self.aPuppetInfo.value,'modules')
            if not self.aModuleInfo.value:
                guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.aModuleInfo.attr)
                return False  
            else:
                #Initialize our modules null as a buffer
                self.ModulesBuffer = BufferFactory(self.aModuleInfo.value)                
            
            self.aGeoInfo = AttrFactory(self.aPuppetInfo.value,'geo')
            if not self.aGeoInfo.value:
                guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.aGeoInfo.attr)
                return False  
            
            self.aSettingsInfo = AttrFactory(self.aPuppetInfo.value,'settings')
            if not self.aSettingsInfo.value:
                guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.aSettingsInfo.attr)
                return False 
            else:
                self.aPuppetMode = AttrFactory(self.aSettingsInfo.value,'cgmModuleMode')
                self.aAimAxis= AttrFactory(self.aSettingsInfo.value,'axisAim') 
                self.aUpAxis= AttrFactory(self.aSettingsInfo.value,'axisUp') 
                self.aOutAxis= AttrFactory(self.aSettingsInfo.value,'axisOut')
                
        return True
            
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Modules
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def getModules(self):
        self.modules = {}
        if self.ModulesBuffer.bufferList:
            for k in self.ModulesBuffer.bufferDict.keys():
                pass
                #self.modules[k] = 
    
    def addModule(self,moduleName,*a,**kw):
        tmpModule = ModuleFactory(moduleName)
        
        self.ModulesBuffer.store(tmpModule.moduleNull)
        moduleNullBuffer = rigging.doParentReturnName(tmpModule.moduleNull,self.aModulesGroup.value)
        
        
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
        templateSizeObject = attributes.returnMessageObject(self.PuppetNullName,'templateSizeObject')
        if not mc.objExists(templateSizeObject) and create:
            self.createSizeTemplateControl()
            guiFactory.report("'%s' has template object '%s'"%(self.PuppetNullName,templateSizeObject))
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
            guiFactory.report("'%s' has template object '%s'"%(self.PuppetNullName,templateSizeObject))
            return True
            
        guiFactory.warning("Size template failed to verify")
        return False
    
    def isRef(self):
        if mc.referenceQuery(self.PuppetNullName, isNodeReferenced=True):
            self.refState = True
            self.refPrefix = search.returnReferencePrefix(self.PuppetNullName)
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
        self.PuppetNullName(string)
        
        RETURNS:
        returnList(list) = [startCrv(string),EndCrv(list)]
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Get info
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        centerColors = modules.returnSettingsData('colorCenter',True)
        font = mc.getAttr((self.aSettingsInfo.value+'.font'))
        
        """ checks for there being anything in our geo group """
        if not self.geo:
            return guiFactory.warning('Need some geo defined to make this tool worthwhile')
            boundingBoxSize =  modules.returnSettingsDataAsFloat('meshlessSizeTemplate')
        else:
            boundingBoxSize = distance.returnBoundingBoxSize (self.aGeoGroup.value)
            boundingBox = mc.exactWorldBoundingBox(self.aGeoGroup.value)
            
        
        """determine orienation """
        maxSize = max(boundingBoxSize)
        matchIndex = boundingBoxSize.index(maxSize)
        
        """Find the pivot of the bounding box """
        pivotPosition = distance.returnCenterPivotPosition(self.aGeoGroup.value)
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Get our positions
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        print self.aPuppetMode.value
        if self.aPuppetMode.value == 0:
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
        attributes.storeInfo(sizeCurveControlStart,'cgmName',(self.PuppetNullName+'.cgmName'))
        attributes.storeInfo(sizeCurveControlStart,'cgmDirection','start')
        attributes.storeInfo(sizeCurveControlStart,'cgmType','templateSizeObject')
        sizeCurveControlStart = NameFactory.doNameObject(sizeCurveControlStart)
        mc.makeIdentity(sizeCurveControlStart, apply = True, t=True,s=True,r=True)
    
        attributes.storeInfo(sizeCurveControlEnd,'cgmName',(self.PuppetNullName+'.cgmName'))
        attributes.storeInfo(sizeCurveControlEnd,'cgmDirection','end')
        attributes.storeInfo(sizeCurveControlEnd,'cgmType','templateSizeObject')
        sizeCurveControlEnd  = NameFactory.doNameObject(sizeCurveControlEnd)
        
        endGroup = rigging.groupMeObject(sizeCurveControlEnd)
        mc.makeIdentity(sizeCurveControlEnd, apply = True, t=True,s=True,r=True)
        
        mc.parentConstraint(sizeCurveControlStart,endGroup,maintainOffset = True)
        
        """ make control group """
        controlGroup = rigging.groupMeObject(sizeCurveControlStart)
        attributes.storeInfo(controlGroup,'cgmName',(self.PuppetNullName+'.cgmName'))
        attributes.storeInfo(controlGroup,'cgmType','templateSizeObjectGroup')
        controlGroup = NameFactory.doNameObject(controlGroup)

        
        endGroup = rigging.doParentReturnName(endGroup,controlGroup)
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Getting data ready
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
        attributes.storeInfo(controlGroup,'controlStart',sizeCurveControlStart)
        attributes.storeInfo(controlGroup,'controlEnd',sizeCurveControlEnd)        
        attributes.storeInfo(self.PuppetNullName,'templateSizeObject',controlGroup)
        
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
        assert self.aGeoGroup.value is not False,"No geo group found!"
        
        selection = mc.ls(sl=True,flatten=True,long=True) or []
        
        if not selection:
            guiFactory.warning("No selection found to add to '%s'"%self.nameBase)
        
        returnList = []    
        for o in selection:
            if search.returnObjectType(o) in geoTypes:
                if self.aGeoGroup.value not in search.returnAllParents(o,True):
                    o = rigging.doParentReturnName(o,self.aGeoGroup.value)
                    self.geo.append(o)
                else:
                    guiFactory.warning("'%s' already a part of '%s'"%(o,self.nameBase))
            else:
                guiFactory.warning("'%s' doesn't seem to be geo. Not added to '%s'"%(o,self.nameBase))
    
    def checkGeo(self):
        """
        Check a puppet's geo that it is actually geo
        """
        assert self.aGeoGroup.value is not False,"No geo group found!"
        self.geo = []
        children = search.returnAllChildrenObjects(self.aGeoGroup.value)
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
        self.aPuppetMode.set(i)
        
    def doSetAimAxis(self,i):
        """
        Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
        Then Up, and Out is last.
        
        """
        assert i < 6,"%i isn't a viable aim axis integer"%i
        
        self.aAimAxis.set(i)
        if self.aUpAxis.value == self.aAimAxis.value:
            self.doSetUpAxis(i)
        if self.aOutAxis.value == self.aAimAxis.value:
            self.doSetOutAxis(i)
            
        return True
        
    def doSetUpAxis(self,i):
        """
        Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
        Then Up, and Out is last.
        
        """        
        assert i < 6,"%i isn't a viable up axis integer"%i
        axisBuffer = range(6)
        axisBuffer.remove(self.aAimAxis.value)
        
        if i != self.aAimAxis.value:
            self.aUpAxis.set(i)  
        else:
            self.aUpAxis.set(axisBuffer[0]) 
            guiFactory.warning("Aim axis has '%s'. Changed up axis to '%s'. Change aim setting if you want this seeting"%(axisDirections[self.aAimAxis.value],axisDirections[self.aUpAxis.value]))                  
            axisBuffer.remove(axisBuffer[0])
            
        if self.aOutAxis.value in [self.aAimAxis.value,self.aUpAxis.value]:
            for i in axisBuffer:
                if i not in [self.aAimAxis.value,self.aUpAxis.value]:
                    self.doSetOutAxis(i)
                    guiFactory.warning("Setting conflict. Changed out axis to '%s'"%axisDirections[i])                    
                    break
        return True        
        
    

        
    def doSetOutAxis(self,i):
        assert i < 6,"%i isn't a viable aim axis integer"%i
        
        if i not in [self.aAimAxis.value,self.aUpAxis.value]:
            self.aOutAxis.set(i)
        else:
            axisBuffer = range(6)
            axisBuffer.remove(self.aAimAxis.value)
            axisBuffer.remove(self.aUpAxis.value)
            self.aOutAxis.set(axisBuffer[0]) 
            guiFactory.warning("Setting conflict. Changed out axis to '%s'"%axisDirections[ axisBuffer[0] ])                    


        
    def doRenamePuppet(self,newName):
        """
        Rename Puppet null
        """
        if newName == self.nameBase:
            return guiFactory.warning("Already named '%s'"%newName)
        
        attributes.storeInfo(self.PuppetNullName,'cgmName ',newName)   
        self.PuppetNullName = NameFactory.doNameObject(self.PuppetNullName,False) 
        self.nameBase = newName
        guiFactory.warning("Puppet renamed as '%s'"%newName)
        
        