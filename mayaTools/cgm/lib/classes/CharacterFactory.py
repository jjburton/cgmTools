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

geoTypes = 'nurbsSurface','mesh','poly','subdiv'
CharacterTypes = 'Bio','Mech','Prop'

class CharacterFactory():
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
        self.masterNulls = modules.returnMasterObjects()
        self.nameBase = characterName
        self.geo = []
        self.modules = []
        self.templateSizeObjects = {}
        
        #>>> See if our null exists
        if not self.verifyMasterNull():
            guiFactory.warning("'%s' failed to verify!"%characterName)
            return False
        
        self.checkGeo()
        self.verifyTemplateSizeObject(False)
        guiFactory.report("'%s' checks out"%self.nameBase)
        
    def doRenameMaster(self,newName):
        """
        Rename Master null
        """
        if newName == self.nameBase:
            return guiFactory.warning("Already named '%s'"%newName)
        
        attributes.storeInfo(self.MasterNullName,'cgmName',newName)   
        self.MasterNullName = NameFactory.doNameObject(self.MasterNullName,False) 
        self.nameBase = newName
        guiFactory.report("Master renamed as '%s'"%newName)
        
        
    def verifyMasterNull(self):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        Verifies the various components a masterNull for a character/asset. If a piece is missing it replaces it.
        
        RETURNS:
        success(bool)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        if self.nameBase  == '':
            randomOptions = ['ReallyNameMe','SolarSystem_isADumbName','David','Josh','Ryan','NameMe','Homer','Georgie','PleaseNameMe','NAMEThis','PleaseNameThisPuppet']
            buffer = random.choice(randomOptions)
            cnt = 0
            while mc.objExists(buffer) and cnt<10:
                cnt +=1
                buffer = random.choice(randomOptions)
            self.nameBase = buffer
            
        #Master null
        if not mc.objExists(self.nameBase) and not attributes.doGetAttr(self.nameBase,'cgmModuleType') == 'master':
            self.MasterNullName = mc.group(empty=True)
        else:
            self.MasterNullName = self.nameBase
        
        attributes.storeInfo(self.MasterNullName,'cgmName',self.nameBase,True)   
        attributes.storeInfo(self.MasterNullName,'cgmType','ignore')
        attributes.storeInfo(self.MasterNullName,'cgmModuleType','master')
             
        
        if self.MasterNullName != self.nameBase:
            self.MasterNullName = NameFactory.doNameObject(self.MasterNullName,True)
        
        #Checks our modules container null
        buffer = attributes.returnMessageObject(self.MasterNullName,'modulesGroup')
        if buffer and mc.objExists(buffer):
            self.ModulesGroupName = buffer
            print self.ModulesGroupName
        else:
            self.ModulesGroupName = mc.group(empty=True)
            
        attributes.storeInfo(self.ModulesGroupName ,'cgmName','modules')   
        attributes.storeInfo(self.ModulesGroupName ,'cgmType','group')
        
        if self.ModulesGroupName != buffer:
            self.ModulesGroupName = NameFactory.doNameObject(self.ModulesGroupName)
        
        self.ModulesGroupName = rigging.doParentReturnName(self.ModulesGroupName,self.MasterNullName)
        attributes.storeObjectToMessage (self.ModulesGroupName, self.MasterNullName, 'modulesGroup')
        
        #Checks our noTransform container null
        buffer = attributes.returnMessageObject(self.MasterNullName,'noTransformGroup')
        if buffer and mc.objExists(buffer):
            self.NoTransformGroupName = buffer
        else:
            self.NoTransformGroupName = mc.group (empty=True)
            
        attributes.storeInfo(self.NoTransformGroupName ,'cgmName','noTransform')   
        attributes.storeInfo(self.NoTransformGroupName ,'cgmType','group')
        
        if self.NoTransformGroupName != buffer:
            self.NoTransformGroupName = NameFactory.doNameObject(self.NoTransformGroupName)
        self.NoTransformGroupName = rigging.doParentReturnName(self.NoTransformGroupName,self.MasterNullName)
        
        attributes.storeObjectToMessage (self.NoTransformGroupName, self.MasterNullName, 'noTransformGroup') 
        
        #Checks our geo container null
        buffer = attributes.returnMessageObject(self.MasterNullName,'geoGroup')
        if buffer and mc.objExists(buffer):
            self.GeoGroupName = buffer
        else:
            self.GeoGroupName = mc.group (empty=True)
            
        attributes.storeInfo(self.GeoGroupName ,'cgmName','geo')   
        attributes.storeInfo(self.GeoGroupName ,'cgmType','group')
        
        if self.GeoGroupName != buffer:
            self.GeoGroupName = NameFactory.doNameObject(self.GeoGroupName)
        self.GeoGroupName = rigging.doParentReturnName(self.GeoGroupName,self.NoTransformGroupName)
        
        attributes.storeObjectToMessage (self.GeoGroupName, self.MasterNullName, 'geoGroup') 
        
        #Checks master info null
        buffer = attributes.returnMessageObject(self.MasterNullName,'info')
        if buffer and mc.objExists(buffer):
            self.MasterInfoGroupName = buffer
        else:
            self.MasterInfoGroupName = mc.group (empty=True)
            
        attributes.storeInfo(self.MasterInfoGroupName ,'cgmName','master')   
        attributes.storeInfo(self.MasterInfoGroupName ,'cgmType','info')
        
        if self.MasterInfoGroupName != buffer:
            self.MasterInfoGroupName = NameFactory.doNameObject(self.MasterInfoGroupName,False)
        self.MasterInfoGroupName = rigging.doParentReturnName(self.MasterInfoGroupName,self.MasterNullName)
        
        attributes.storeObjectToMessage (self.MasterInfoGroupName, self.MasterNullName, 'info') 
        
        #Checks modules info null
        buffer = attributes.returnMessageObject(self.MasterInfoGroupName,'modules')
        if buffer and mc.objExists(buffer):
            self.ModulesInfoName = buffer
        else:
            self.ModulesInfoName = mc.group (empty=True)
            
        attributes.storeInfo(self.ModulesInfoName ,'cgmName','modules')   
        attributes.storeInfo(self.ModulesInfoName ,'cgmType','info')
        
        if self.ModulesInfoName != buffer:
            self.ModulesInfoName = NameFactory.doNameObject(self.ModulesInfoName,False)
        self.ModulesInfoName = rigging.doParentReturnName(self.ModulesInfoName,self.MasterInfoGroupName)
        
        attributes.storeObjectToMessage (self.ModulesInfoName, self.MasterInfoGroupName, 'modules') 
        
        #Checks geo info null
        buffer = attributes.returnMessageObject(self.MasterInfoGroupName,'geo')
        if buffer and mc.objExists(buffer):
            self.GeoInfoName = buffer
        else:
            self.GeoInfoName = mc.group (empty=True)
            
        attributes.storeInfo(self.GeoInfoName ,'cgmName','geo')   
        attributes.storeInfo(self.GeoInfoName ,'cgmType','info')
        
        if self.GeoInfoName != buffer:
            self.GeoInfoName = NameFactory.doNameObject(self.GeoInfoName,False)
        self.GeoInfoName = rigging.doParentReturnName(self.GeoInfoName,self.MasterInfoGroupName)
        
        attributes.storeObjectToMessage (self.GeoInfoName, self.MasterInfoGroupName, 'geo') 
        
        #Checks settings info null
        buffer = attributes.returnMessageObject(self.MasterInfoGroupName,'settings')
        if buffer and mc.objExists(buffer):
            self.SettingsInfoName = buffer
        else:
            self.SettingsInfoName = mc.group (empty=True)
            
        attributes.storeInfo(self.SettingsInfoName ,'cgmName','settings')   
        attributes.storeInfo(self.SettingsInfoName ,'cgmType','info')
        defaultFont = modules.returnSettingsData('defaultTextFont')
        
        
        if self.SettingsInfoName != buffer:
            self.SettingsInfoName = NameFactory.doNameObject(self.SettingsInfoName,False)
        self.SettingsInfoName = rigging.doParentReturnName(self.SettingsInfoName,self.MasterInfoGroupName)
        
        attributes.storeObjectToMessage (self.SettingsInfoName, self.MasterInfoGroupName, 'settings') 
        
        attributes.storeInfo(self.SettingsInfoName,'font',defaultFont)
        
        if not mc.objExists('%s.%s'%(self.SettingsInfoName,'cgmModuleMode')):
            self.aModuleMode = AttrFactory(self.SettingsInfoName,'cgmModuleMode','int',value = 0)      
        self.aModuleMode = AttrFactory(self.SettingsInfoName,'cgmModuleMode','int')
        
        self.aUpAxis= AttrFactory(self.SettingsInfoName,'axisUp','enum',enum = 'x+:y+:z+:x-:y-:z-') 
        self.aUpAxis= AttrFactory(self.SettingsInfoName,'axisAim','enum',enum = 'x+:y+:z+:x-:y-:z-') 
        
        if not mc.objExists('%s.%s'%(self.SettingsInfoName,'axisAim')):
            self.aUpAxis= AttrFactory(self.SettingsInfoName,'axisAim','enum',value = 0) 
            self.aUpAxis.setEnum('xyz:yzx:zxy:xzy:yxz:zyx')
        self.aUpAxis = AttrFactory(self.SettingsInfoName,'axisAim')
        
        if mc.ls(sl=True):
            mc.select(cl=True)
        return True
        
    def addGeo(self):
        """ 
        Add geo to a puppet
        """
        assert self.GeoGroupName is not False,"No geo group found!"
        
        selection = mc.ls(sl=True,flatten=True,long=True) or []
        
        if not selection:
            guiFactory.warning("No selection found to add to '%s'"%self.nameBase)
        
        returnList = []    
        for o in selection:
            if search.returnObjectType(o) in geoTypes:
                if self.GeoGroupName not in search.returnAllParents(o,True):
                    o = rigging.doParentReturnName(o,self.GeoGroupName)
                    self.geo.append(o)
                else:
                    guiFactory.warning("'%s' already a part of '%s'"%(o,self.nameBase))
            else:
                guiFactory.warning("'%s' doesn't seem to be geo. Not added to '%s'"%(o,self.nameBase))
    
    def checkGeo(self):
        assert self.GeoGroupName is not False,"No geo group found!"
        self.geo = []
        children = search.returnAllChildrenObjects(self.GeoGroupName)
        if not children:
            return False
    
        for o in children:
            if search.returnObjectType(o) in geoTypes:
                buff = mc.ls(o,long=True)
                self.geo.append(buff[0])
        return True
    
    def doSetMode(self,i):
        assert i <(len(CharacterTypes)),"%i isn't a viable base pupppet type"
        self.aModuleMode.set(i)
        
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
        templateSizeObject = attributes.returnMessageObject(self.MasterNullName,'templateSizeObject')
        if not mc.objExists(templateSizeObject) and create:
            self.createSizeTemplateControl()
            guiFactory.report("'%s' has template object '%s'"%(self.MasterNullName,templateSizeObject))
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
            guiFactory.report("'%s' has template object '%s'"%(self.MasterNullName,templateSizeObject))
            return True
            
        guiFactory.warning("Size template failed to verify")
        return False
        
    def createSizeTemplateControl(self):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
        DESCRIPTION:
        Generates a sizeTemplateObject. It's been deleted, it recreates it. Guess the size based off of there
        being a mesh there. If there is no mesh, it sets sets an intial size of a 
        [155,170,29] unit character.
        
        ARGUMENTS:
        self.MasterNullName(string)
        
        RETURNS:
        returnList(list) = [startCrv(string),EndCrv(list)]
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Get info
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        centerColors = modules.returnSettingsData('colorCenter',True)
        font = mc.getAttr((self.SettingsInfoName+'.font'))
        
        """ checks for there being anything in our geo group """
        if not self.geo:
            return guiFactory.warning('Need some geo defined to make this tool worthwhile')
            boundingBoxSize =  modules.returnSettingsDataAsFloat('meshlessSizeTemplate')
        else:
            boundingBoxSize = distance.returnBoundingBoxSize (self.GeoGroupName)
            boundingBox = mc.exactWorldBoundingBox(self.GeoGroupName)
            
        
        """determine orienation """
        maxSize = max(boundingBoxSize)
        matchIndex = boundingBoxSize.index(maxSize)
        
        """Find the pivot of the bounding box """
        pivotPosition = distance.returnCenterPivotPosition(self.GeoGroupName)
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Get our positions
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        print self.aModuleMode.value
        if self.aModuleMode.value == 0:
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
        attributes.storeInfo(sizeCurveControlStart,'cgmName',(self.MasterNullName+'.cgmName'))
        attributes.storeInfo(sizeCurveControlStart,'cgmDirection','start')
        attributes.storeInfo(sizeCurveControlStart,'cgmType','templateSizeObject')
        sizeCurveControlStart = NameFactory.doNameObject(sizeCurveControlStart)
        mc.makeIdentity(sizeCurveControlStart, apply = True, t=True,s=True,r=True)
    
        attributes.storeInfo(sizeCurveControlEnd,'cgmName',(self.MasterNullName+'.cgmName'))
        attributes.storeInfo(sizeCurveControlEnd,'cgmDirection','end')
        attributes.storeInfo(sizeCurveControlEnd,'cgmType','templateSizeObject')
        sizeCurveControlEnd  = NameFactory.doNameObject(sizeCurveControlEnd)
        
        endGroup = rigging.groupMeObject(sizeCurveControlEnd)
        mc.makeIdentity(sizeCurveControlEnd, apply = True, t=True,s=True,r=True)
        
        mc.parentConstraint(sizeCurveControlStart,endGroup,maintainOffset = True)
        
        """ make control group """
        controlGroup = rigging.groupMeObject(sizeCurveControlStart)
        attributes.storeInfo(controlGroup,'cgmName',(self.MasterNullName+'.cgmName'))
        attributes.storeInfo(controlGroup,'cgmType','templateSizeObjectGroup')
        controlGroup = NameFactory.doNameObject(controlGroup)

        
        endGroup = rigging.doParentReturnName(endGroup,controlGroup)
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Getting data ready
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
        attributes.storeInfo(controlGroup,'controlStart',sizeCurveControlStart)
        attributes.storeInfo(controlGroup,'controlEnd',sizeCurveControlEnd)        
        attributes.storeInfo(self.MasterNullName,'templateSizeObject',controlGroup)
        
        self.templateSizeObjects['root'] = controlGroup
        self.templateSizeObjects['start'] = sizeCurveControlStart
        self.templateSizeObjects['end'] = sizeCurveControlEnd  
       
        returnList=[]
        returnList.append(sizeCurveControlStart)
        returnList.append(sizeCurveControlEnd)
        return returnList

        

