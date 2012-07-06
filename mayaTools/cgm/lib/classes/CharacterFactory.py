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
        self.templateSizeObject = {}
        
        #>>> See if our null exists
        if not self.verifyMasterNull():
            guiFactory.warning("'%s' failed to verify!"%characterName)
            return False
        
        self.checkGeo()
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
        
        if not mc.objExists('%s.%s'%(self.MasterNullName,'cgmModuleMode')):
            self.aModuleMode = AttrFactory(self.MasterNullName,'cgmModuleMode',value = 0)      
        self.aModuleMode = AttrFactory(self.MasterNullName,'cgmModuleMode','int')      
        
        
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
        attributes.storeInfo(self.SettingsInfoName,'font',defaultFont)
        
        if self.SettingsInfoName != buffer:
            self.SettingsInfoName = NameFactory.doNameObject(self.SettingsInfoName,False)
        self.SettingsInfoName = rigging.doParentReturnName(self.SettingsInfoName,self.MasterInfoGroupName)
        
        attributes.storeObjectToMessage (self.SettingsInfoName, self.MasterInfoGroupName, 'settings') 

        mc.select(cl=True)
        return True
    

    def verifyTemplateSizeObject(self):
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
        if not templateSizeObject:
            buffer = controlBuilder.createSizeTemplateControl(self.MasterNullName)
            
        if buffer:
            self.templateSizeObjects['root'] = templateSizeObject
            self.templateSizeObjects['bottom'] = attributes.returnMessageObject(templateSizeObject,'controlBottom')
            self.templateSizeObjects['top'] = attributes.returnMessageObject(templateSizeObject,'controlTop')
            return templateSizeObjects
        else:
            return controlBuilder.createSizeTemplateControl(masterNull)    
        
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

        

