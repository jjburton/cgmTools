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

from cgm.rigger.lib.Limb import module
reload(module)
from cgm.rigger import ModuleFactory
reload(ModuleFactory)

from cgm.rigger.ModuleFactory import *
from cgm.rigger.lib import *


import random
import re
import copy

from cgm.lib import (search,
                     distance,
                     names,
                     logic,
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
reload(logic)

typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
namesDictionary = dictionary.initializeDictionary( settings.getNamesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())

axisDirectionsByString = ['x+','y+','z+','x-','y-','z-']
geoTypes = 'nurbsSurface','mesh','poly','subdiv'
CharacterTypes = 'Bio','Mech','Prop'

moduleTypeToFunctionDict = {'None':ModuleFactory,
                            'segment':Limb.module.Segment}

moduleTypeToMasterClassDict = {'None':['none','None',False],
                               'Limb':['segment']}

#Make our class bridge
#guiFactory.classBridge_Puppet()   

#These are our init variables
initLists = ['geo','modules','rootModules','orderedModules','orderedParentModules']
initDicts = ['templateSizeObjects','Module','moduleParents','moduleChildren','moduleStates']
initStores = ['PuppetNull','refState',]
 
class PuppetFactory():
    """ 
    Character
    
    """    
    def __init__(self,characterName = '',*a,**kw):
        """ 
        Intializes an optionVar class handler
        
        Keyword arguments:
        varName(string) -- name for the optionVar
        
        ObjectFactories:
        self.PuppetNull - main null
        self.NoTransformGroup        
        >>> self.GeoGroup - group where geo is stored to
        self.PuppetInfoNull - master puppet info null under which the other nulls live        
        >>> self.GeoInfoNull
        >>> self.ModuleInfoNull
        >>> self.ModulesGroup
        
        BufferFactories:
        self.ModulesBuffer - buffer for modules. Instanced from self.ModuleInfoNull
        
        """    
        #>>>Keyword args        
        characterType = kw.pop('characterType','')
        initializeOnly = kw.pop('initializeOnly',False)
        
        
        #Default to creation of a var as an int value of 0
        ### input check         
        self.masterNulls = modules.returnPuppetObjects()
        self.nameBase = characterName
        
        for l in initLists:
            self.__dict__[l] = []
        for d in initDicts:
            self.__dict__[d] = {}
        for o in initStores:
            self.__dict__[o] = False

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
                       

        if self.refState or initializeOnly:
            guiFactory.report("'%s' Initializing..."%characterName)
            if not self.initialize():
                guiFactory.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%moduleName)
                return     
            
        else:
            if not self.verify():
                guiFactory.warning("'%s' failed to verify!"%characterName)
                return         
        
        self.checkGeo()
        self.verifyTemplateSizeObject(False)
        self.getModules(initializeOnly=initializeOnly,*a,**kw)
        guiFactory.report("'%s' checks out"%self.nameBase)
        guiFactory.doPrintReportEnd()
                
    def verify(self):
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
                self.PuppetNull.doName(False)
            
            attributes.doSetLockHideKeyableAttr(self.PuppetNull.nameShort,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
        except:
            guiFactory.warning("Puppet null failed!")
            
        #Checks our modules container null
        created = False
        #Initialize message attr
        self.msgModulesGroup = AttrFactory(self.PuppetNull,'modulesGroup','message')
        if not self.msgModulesGroup.get():
            self.ModulesGroup = ObjectFactory(mc.group(empty=True))            
            self.msgModulesGroup.doStore(self.ModulesGroup.nameShort)
            created = True
        else:
            self.ModulesGroup = ObjectFactory(self.msgModulesGroup.get())
            
        self.ModulesGroup.store('cgmName','modules')   
        self.ModulesGroup.store('cgmType','group')
        
        self.ModulesGroup.doParent(self.PuppetNull.nameShort)
        
        if created:
            self.ModulesGroup.doName(False)
            
        self.msgModulesGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.ModulesGroup.nameShort)

            
        #Checks our noTransform container null
        created = False        
        self.msgNoTransformGroup = AttrFactory(self.PuppetNull,'noTransformGroup','message')
        if not self.msgNoTransformGroup.get():
            self.NoTransformGroup = ObjectFactory(mc.group(empty=True))
            self.msgNoTransformGroup.doStore(self.NoTransformGroup.nameShort)
            created = True
        else:
            self.NoTransformGroup = ObjectFactory(self.msgNoTransformGroup.get())
            
        self.NoTransformGroup.store('cgmName','noTransform')   
        self.NoTransformGroup.store('cgmType','group')
        
        self.NoTransformGroup.doParent(self.PuppetNull.nameShort)
        
        if created:
            self.NoTransformGroup.doName(False)
            
        self.msgNoTransformGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.NoTransformGroup.nameShort)
         
            
        #Checks our geo container null
        created = False        
        self.msgGeoGroup = AttrFactory(self.PuppetNull,'geoGroup','message')
        if not self.msgGeoGroup.get():
            self.GeoGroup = ObjectFactory(mc.group(empty=True))
            self.msgGeoGroup.doStore(self.GeoGroup.nameShort)            
            created = True
        else:
            self.GeoGroup = ObjectFactory(self.msgGeoGroup.get())
            
        self.GeoGroup.store('cgmName','geo')   
        self.GeoGroup.store('cgmType','group')
        
        self.GeoGroup.doParent(self.msgNoTransformGroup.get())
        
        if created:
            self.GeoGroup.doName(False)
            
        self.msgGeoGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.GeoGroup.nameShort)
        
        #Checks master info null
        created = False        
        self.msgPuppetInfo = AttrFactory(self.PuppetNull,'info','message')
        if not self.msgPuppetInfo.get():
            self.PuppetInfoNull = ObjectFactory(mc.group(empty=True))
            self.msgPuppetInfo.doStore(self.PuppetInfoNull.nameShort)               
            created = True
        else:
            self.PuppetInfoNull = ObjectFactory(self.msgPuppetInfo.get())
            
            
        self.PuppetInfoNull.store('cgmName','master')   
        self.PuppetInfoNull.store('cgmType','info')
        
        self.PuppetInfoNull.doParent(self.PuppetNull.nameShort)
        
        if created:
            self.PuppetInfoNull.doName(False)
            
        self.msgPuppetInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.PuppetInfoNull.nameShort)
        
            
        #Checks modules info null
        created = False        
        self.msgModuleInfo = AttrFactory(self.msgPuppetInfo.get(),'modules','message')
        if not self.msgModuleInfo.get():
            self.ModuleInfoNull = ObjectFactory(mc.group(empty=True))
            self.msgModuleInfo.doStore(self.ModuleInfoNull.nameShort)     
            created = True
        else:
            self.ModuleInfoNull = ObjectFactory(self.msgModuleInfo.get())
            
        self.ModuleInfoNull.store('cgmName','modules')   
        self.ModuleInfoNull.store('cgmType','info')
        
        self.ModuleInfoNull.doParent(self.PuppetInfoNull.nameShort)
        
        if created:
            self.ModuleInfoNull.doName(False)
            
        self.msgModuleInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.ModuleInfoNull.nameShort)
        
        #Initialize our modules null as a buffer
        self.ModulesBuffer = BufferFactory(self.ModuleInfoNull.nameShort)
        
        #Checks geo info null
        created = False        
        self.msgGeoInfo = AttrFactory(self.msgPuppetInfo.get(),'geo','message')
        if not self.msgGeoInfo.get():
            self.GeoInfoNull = ObjectFactory(mc.group(empty=True))
            self.msgGeoInfo.doStore(self.GeoInfoNull.nameShort)              
            created = True
        else:
            self.GeoInfoNull = ObjectFactory(self.msgGeoInfo.get())
            
        self.GeoInfoNull.store('cgmName','geo')   
        self.GeoInfoNull.store('cgmType','info')
        
        self.GeoInfoNull.doParent(self.msgPuppetInfo.get())
        
        if created:
            self.GeoInfoNull.doName(False)
            
        self.msgGeoInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.GeoInfoNull.nameShort) 
        
        #Checks settings info null
        created = False        
        self.msgSettingsInfo = AttrFactory(self.msgPuppetInfo.get(),'settings','message')
        if not self.msgSettingsInfo.get():
            self.SettingsInfoNull = ObjectFactory(mc.group(empty=True))
            self.msgSettingsInfo.doStore(self.SettingsInfoNull.nameShort)   
            created = True
        else:
            self.SettingsInfoNull = ObjectFactory(self.msgSettingsInfo.get())
            
        self.SettingsInfoNull.store('cgmName','settings')   
        self.SettingsInfoNull.store('cgmType','info')
        defaultFont = modules.returnSettingsData('defaultTextFont')
        self.SettingsInfoNull.store('font',defaultFont)
        
        self.SettingsInfoNull.doParent(self.msgPuppetInfo.get())
        
        if created:
            self.SettingsInfoNull.doName(False)
            
        self.msgSettingsInfo.updateData()   
        
        
        self.optionPuppetMode = AttrFactory(self.SettingsInfoNull,'optionPuppetTemplateMode','int',initialValue = 0)      
        
        self.optionAimAxis= AttrFactory(self.SettingsInfoNull,'axisAim','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=2) 
        self.optionUpAxis= AttrFactory(self.SettingsInfoNull,'axisUp','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=1) 
        self.optionOutAxis= AttrFactory(self.SettingsInfoNull,'axisOut','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=0)         
            
        attributes.doSetLockHideKeyableAttr(self.SettingsInfoNull.nameShort) 
        
        return True
     
    def initialize(self):
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
        
        self.msgModulesGroup = AttrFactory(self.PuppetNull,'modulesGroup')
        if not self.msgModulesGroup.get():
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.msgModulesGroup.attr)
            return False
        else:
            self.ModulesGroup = ObjectFactory(self.msgModulesGroup.get())

        self.msgNoTransformGroup = AttrFactory(self.PuppetNull,'noTransformGroup')
        if not self.msgNoTransformGroup.get():
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.msgNoTransformGroup.attr)
            return False
        else:
            self.NoTransformGroup = ObjectFactory(self.msgNoTransformGroup.get())        
            
        self.msgGeoGroup = AttrFactory(self.PuppetNull,'geoGroup')
        if not self.msgGeoGroup.get():
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.msgGeoGroup.attr)
            return False
        else:
            self.GeoGroup = ObjectFactory(self.msgGeoGroup.get())        
         
        self.msgPuppetInfo = AttrFactory(self.PuppetNull,'info')
        if not self.msgPuppetInfo.get():
            guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.msgPuppetInfo.attr)
            return False
        
        else:
            self.PuppetInfoNull = ObjectFactory(self.msgPuppetInfo.get())                    
            self.msgModuleInfo = AttrFactory(self.PuppetInfoNull,'modules')
            if not self.msgModuleInfo.get():
                guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.msgModuleInfo.attr)
                return False  
            else:
                #Initialize our modules null as a buffer
                self.ModuleInfoNull = ObjectFactory(self.msgModuleInfo.get())
                self.ModulesBuffer = BufferFactory(self.msgModuleInfo.get())                
            
            self.msgGeoInfo = AttrFactory(self.PuppetInfoNull,'geo')
            if not self.msgGeoInfo.get():
                guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.msgGeoInfo.attr)
                return False
            else:
                self.GeoInfoNull = ObjectFactory(self.msgGeoInfo.get())             
            
            self.msgSettingsInfo = AttrFactory(self.PuppetInfoNull,'settings')
            if not self.msgSettingsInfo.get():
                guiFactory.warning("'%s' looks to be missing. Go back to unreferenced file"%self.msgSettingsInfo.attr)
                return False 
            else:
                self.SettingsInfoNull = ObjectFactory(self.msgSettingsInfo.get(),)
                
                self.optionPuppetMode = AttrFactory(self.SettingsInfoNull,'optionPuppetTemplateMode')
                self.optionAimAxis= AttrFactory(self.SettingsInfoNull,'axisAim') 
                self.optionUpAxis= AttrFactory(self.SettingsInfoNull,'axisUp') 
                self.optionOutAxis= AttrFactory(self.SettingsInfoNull,'axisOut')
                
        return True
            
    def delete(self):
        """
        Delete the Puppet
        """
        mc.delete(self.PuppetNull.nameLong)
        self = False
        
    def getState(self):
        """
        Return a Puppet's state
        
        Returns:
        state/False -- (int)/(bool)
        """
        checkList = []
        if self.getModuleStates() is False:
            return False
        for k in self.moduleStates.keys():
            checkList.append(self.moduleStates[k])
        return min(checkList)
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Modules
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def changeModuleCGMTag(self,moduleName,tag,newInfo,*a,**kw):
        """
        Function to change a cgm tag on a module and push a rename through that moudule's instance
        
        moduleName(string)
        tag(string) which tag to use. For a list
        ###
        from cgm.lib.classes import NameFactory
        NameFactory.cgmNameTags   
        ###
        newInfo(*a,**kw) - info to pass into the attributes.storeInfo() function
        """
        if moduleName in self.ModulesBuffer.bufferList:
            #Clear our instanced module
            index = self.ModulesBuffer.bufferList.index(moduleName)
            modType = search.returnTagInfo(self.Module[index].ModuleNull.nameShort,'moduleType') or False
            if index is not False:
                if modType in moduleTypeToFunctionDict.keys():
                    if self.Module[index].changeCGMTag(tag,newInfo,*a,**kw):
                        self.Module[index] = moduleTypeToFunctionDict[modType](self.Module[index].ModuleNull.nameShort)                   
                    self.ModulesBuffer.updateData()
                else:
                    guiFactory.warning("'%s' is not a module type found in the moduleTypeToFunctionDict. Cannot initialize"%modType)
                    return False  
            else:
                guiFactory.warning("%s is not a valid index. Cannot continue"%index)
                return False                  
        else:
            guiFactory.warning("'%s' doesn't seem to be a connected module. Cannot change tag"%moduleName)        
            return False
        
    def getModules(self,*a,**kw):
        """
        Intializes all connected modules of a puppet
        """           
        self.Module = {}
        self.moduleIndexDict = {}
        self.moduleParents = {}
        self.ModulesBuffer.updateData()
        if self.ModulesBuffer.bufferList:
            for i,m in enumerate(self.ModulesBuffer.bufferList):
                modType = search.returnTagInfo(m,'moduleType') or False
                if modType in moduleTypeToFunctionDict.keys():
                    self.Module[i] = moduleTypeToFunctionDict[modType](m,*a,**kw)
                    self.Module[i].ModuleNull.doParent(self.ModulesGroup.nameLong)
                    self.moduleIndexDict[m] = i
                else:
                    guiFactory.warning("'%s' is not a module type found in the moduleTypeToFunctionDict. Cannot initialize"%modType)

    def getModuleStates(self,*a,**kw):
        """
        Get's a dictionary of module states indexed to same indexes as the self.Module[i] format
        """
        self.ModuleStates = {}
        if self.ModulesBuffer.bufferList:
            for i,m in enumerate(self.ModulesBuffer.bufferList):
                self.moduleStates[i] = self.Module[i].getState()
        else:
            return False
        return self.moduleStates
                
    
    def createModule(self,moduleType,*a,**kw):
        """
        Create and connect a new module
        
        moduleType(string) - type of module to create
        """   
        if moduleType in moduleTypeToFunctionDict.keys():
            tmpModule = moduleTypeToFunctionDict[moduleType](forceNew=True,*a,**kw)
            self.ModulesBuffer.store(tmpModule.ModuleNull.nameShort)
            tmpModule.ModuleNull.doParent(self.ModulesGroup.nameShort)             
            self.Module[ self.ModulesBuffer.bufferList.index(tmpModule.ModuleNull.nameShort) ] = tmpModule
        else:
            guiFactory.warning("'%s' is not a module type found in the moduleTypeToFunctionDict. Cannot initialize"%moduleType)

        
    def addModule(self,module,*a,**kw):
        """
        Adds a module to a puppet
        
        module(string)
        """
        if module in self.ModulesBuffer.bufferList:
            return guiFactory.warning("'%s' already connnected to '%s'"%(module,self.nameBase))

        elif mc.objExists(module):
            # If it exists, check type to initialize and add
            modType = search.returnTagInfo(module,'moduleType') or False
            if modType in moduleTypeToFunctionDict.keys():
                self.ModulesBuffer.store(module)
                moduleNullBuffer = rigging.doParentReturnName(module,self.msgModulesGroup.get())
                self.Module[ self.ModulesBuffer.bufferList.index(module) ] = moduleTypeToFunctionDict[modType](moduleNullBuffer)
                
            else:
                guiFactory.warning("'%s' is not a module type found in the moduleTypeToFunctionDict. Cannot initialize")
            
        else:
            guiFactory.warning("'%s' is not a module type found in the moduleTypeToFunctionDict. Cannot initialize"%module)
    
    def removeModule(self,moduleName):
        """
        Removes a module from a puppet
        
        module(string)
        """        
        if moduleName in self.ModulesBuffer.bufferList:
            #Clear our instanced module
            index = self.ModulesBuffer.bufferList.index(moduleName)
            if index is not False:
                self.Module[index] = False
            self.ModulesBuffer.remove(moduleName)
            buffer = rigging.doParentToWorld(moduleName)
            self.getModules()
        else:
            guiFactory.warning("'%s' doesn't seem to be a connected module. Cannot remove"%moduleName)
    
    def deleteModule(self,moduleName,*a,**kw):
        """
        Removes a module from a puppet
        
        module(string)
        """          
        if moduleName in self.ModulesBuffer.bufferList:
            #Clear our instanced module            
            index = self.ModulesBuffer.bufferList.index(moduleName)
            if index:
                self.Module[index] = False
                
            self.ModulesBuffer.remove(moduleName)
            buffer = rigging.doParentToWorld(moduleName)
            mc.delete(buffer)
            self.getModules()
        else:
            guiFactory.warning("'%s' doesn't seem to be a connected module. Cannot delete"%moduleName)
            
    def getOrderedModules(self):
        """ 
        Returns ordered modules of a character
        
        Stores:
        self.orderedModules(list)       
        
        Returns:
        self.orderedModules(list)
        """            
        assert self.ModulesBuffer.bufferList,"'%s' has no modules"%self.nameBase
        self.orderedModules = []
        self.rootModules = []
        moduleParents = {}
        
        for i,m in enumerate(self.ModulesBuffer.bufferList):
            if self.Module[i].moduleParent:
                moduleParents[m] = self.Module[i].moduleParent
            else:
                self.orderedModules.append(m)
                self.rootModules.append(m)                
                
        while len(moduleParents):
            for module in self.orderedModules:
                for k in moduleParents.keys():
                    if moduleParents.get(k) == module:
                        self.orderedModules.append(k)
                        moduleParents.pop(k)
            
                
        return self.orderedModules
                
    def getOrderedParentModules(self):
        """ 
        Returns ordered list of parent modules of a character
        
        Stores:
        self.moduleChildren(dict)
        self.orderedParentModules(list)       
        self.rootModules(list)
        
        Returns:
        self.orderedParentModules(list)
        """    
        moduleParents ={}
        self.orderedParentModules = []
        self.moduleChildren = {}
        
        #First get our module children stored tothe instance as a dict
        for i,m in enumerate(self.ModulesBuffer.bufferList):
            if not self.Module[i].moduleParent:
                self.orderedParentModules.append(m) 
            else:
                moduleParents[m] = self.Module[i].moduleParent                
                
            childrenBuffer = []
            for iCheck,mCheck in enumerate(self.ModulesBuffer.bufferList):
                if self.Module[iCheck].moduleParent == m:
                    childrenBuffer.append(mCheck)
            if childrenBuffer:
                self.moduleChildren[m] = childrenBuffer
    
        moduleChildrenD = copy.copy(self.moduleChildren)
        
        # Pop the 
        if self.orderedParentModules:
            for p in self.orderedParentModules:
                try:
                    moduleChildrenD.pop(p)
                except:pass
            
        cnt = 0
        #Process the childdren looking for parents as children and so on and so forth, appending them as it finds them
        while len(moduleChildrenD)>0 and cnt < 100:
            for module in self.orderedParentModules:
                print module
                for child in moduleChildrenD.keys():
                    cnt +=1
                    if child in moduleParents.keys() and moduleParents[child] == module:
                        self.orderedParentModules.append(child)
                        moduleChildrenD.pop(child)
     
        guiFactory.report("Children dict is - '%s'"%self.moduleChildren)
        guiFactory.report("Module Parents dict is - '%s'"%moduleParents)
        guiFactory.report("Ordered Parents dict is - '%s'"%self.orderedParentModules)
     
        return self.orderedParentModules
        
        

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
        """
        Basic ref check. Stores to self
        """
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
        startColors = modules.returnSettingsData('colorStart')
        endColors = modules.returnSettingsData('colorEnd')
        
        font = mc.getAttr((self.msgSettingsInfo.get()+'.font'))
        
        """ checks for there being anything in our geo group """
        if not self.geo:
            return guiFactory.warning('Need some geo defined to make this tool worthwhile')
            boundingBoxSize =  modules.returnSettingsDataAsFloat('meshlessSizeTemplate')
        else:
            boundingBoxSize = distance.returnBoundingBoxSize (self.msgGeoGroup.get())
            boundingBox = mc.exactWorldBoundingBox(self.msgGeoGroup.get())
            
        
        """determine orienation """
        maxSize = max(boundingBoxSize)
        matchIndex = boundingBoxSize.index(maxSize)
        
        """Find the pivot of the bounding box """
        pivotPosition = distance.returnCenterPivotPosition(self.msgGeoGroup.get())
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Get our positions
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        if self.optionPuppetMode.get() == 0:
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
        # Simple reverse of start pos buffers if the object is pointing negative        
        if self.optionAimAxis < 2:        
            posBuffers.reverse()
            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Making the controls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>       
        """ make our control object """
        startCurves = []
        startCurve = curves.createControlCurve('circle',depth*.8)
        mc.xform(startCurve,t=posBuffers[0],ws=True)
        attributes.doSetAttr(startCurve,'rotateOrder',5)
        curves.setCurveColorByName(startCurve,startColors[1])
        startCurves.append(startCurve)
        
        startText = curves.createTextCurve('start',size=depth*.75,font=font)
        mc.xform(startText,t=posBuffers[0],ws=True)
        curves.setCurveColorByName(startText,startColors[0])
        startCurves.append(startText)
        
        endCurves = []
        endCurve = curves.createControlCurve('circle',depth*.8)
        mc.xform(endCurve,t=posBuffers[1],ws=True)
        curves.setCurveColorByName(endCurve,endColors[1])
        attributes.doSetAttr(endCurve,'rotateOrder',5)        
        endCurves.append(endCurve)
        
        endText = curves.createTextCurve('end',size=depth*.6,font=font)
        mc.xform(endText,t=posBuffers[1],ws=True)
        curves.setCurveColorByName(endText,endColors[0])
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

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Geo Stuff
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
    def addGeo(self):
        """ 
        Add geo to a puppet
        """
        assert self.msgGeoGroup.get() is not False,"No geo group found!"
        
        selection = mc.ls(sl=True,flatten=True,long=True) or []
        
        if not selection:
            guiFactory.warning("No selection found to add to '%s'"%self.nameBase)
        
        returnList = []    
        for o in selection:
            if search.returnObjectType(o) in geoTypes:
                if self.msgGeoGroup.get() not in search.returnAllParents(o,True):
                    o = rigging.doParentReturnName(o,self.msgGeoGroup.get())
                    self.geo.append(o)
                else:
                    guiFactory.warning("'%s' already a part of '%s'"%(o,self.nameBase))
            else:
                guiFactory.warning("'%s' doesn't seem to be geo. Not added to '%s'"%(o,self.nameBase))
    
    def checkGeo(self):
        """
        Check a puppet's geo that it is actually geo
        """
        assert self.msgGeoGroup.get() is not False,"No geo group found!"
        
        children = search.returnAllChildrenObjects(self.msgGeoGroup.get())
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
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Data setting stuff
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
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
        if self.optionUpAxis.get() == self.optionAimAxis.get():
            self.doSetUpAxis(i)
        if self.optionOutAxis.get() == self.optionAimAxis.get():
            self.doSetOutAxis(i)
            
        return True
        
    def doSetUpAxis(self,i):
        """
        Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
        Then Up, and Out is last.
        
        """        
        assert i < 6,"%i isn't a viable up axis integer"%i
        axisBuffer = range(6)
        axisBuffer.remove(self.optionAimAxis.get())
        
        if i != self.optionAimAxis.get():
            self.optionUpAxis.set(i)  
        else:
            self.optionUpAxis.set(axisBuffer[0]) 
            guiFactory.warning("Aim axis has '%s'. Changed up axis to '%s'. Change aim setting if you want this seeting"%(axisDirectionsByString[self.optionAimAxis.get()],axisDirectionsByString[self.optionUpAxis.get()]))                  
            axisBuffer.remove(axisBuffer[0])
            
        if self.optionOutAxis.get() in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
            for i in axisBuffer:
                if i not in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
                    self.doSetOutAxis(i)
                    guiFactory.warning("Setting conflict. Changed out axis to '%s'"%axisDirectionsByString[i])                    
                    break
        return True        
        
        
    def doSetOutAxis(self,i):
        assert i < 6,"%i isn't a viable aim axis integer"%i
        
        if i not in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
            self.optionOutAxis.set(i)
        else:
            axisBuffer = range(6)
            axisBuffer.remove(self.optionAimAxis.get())
            axisBuffer.remove(self.optionUpAxis.get())
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
        self.verify()
        self.getModules()
        guiFactory.warning("Puppet renamed as '%s'"%newName)
        
        
   #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
   #>> Sizing
   #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def doSize(self):
        """ 
        Function to size a puppet
    
        """
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Get Info
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        ### TemplateSizeObject Check ###
        if not self.ModulesBuffer.bufferList:
            raise StandardError,"'%s' has no modules"%self.PuppetNull.nameLong            
        
        if not self.templateSizeObjects:
            raise StandardError,"'%s' has no size template"%self.PuppetNull.nameLong
        
        basicOrientation = logic.returnHorizontalOrVertical([self.templateSizeObjects['start'],self.templateSizeObjects['end']])
        print basicOrientation
        
        # Get module info
        if not self.getOrderedModules() and self.getOrderedParentModules():
            guiFactory.warning("Failed to get ordered module info, here's what we got...")
            guiFactory.report("Ordered modules - %s"%self.orderedModules)
            guiFactory.report("Ordered parent modules - %s"%self.orderedParentModules)
            guiFactory.report("Module children- %s"%self.moduleChildren)
        
        ##Delete this later
        guiFactory.report("Ordered modules - %s"%self.orderedModules)
        guiFactory.report("Ordered parent modules - %s"%self.orderedParentModules)
        guiFactory.report("Module children- %s"%self.moduleChildren)        
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Get our initial data
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>        
        self.sizeCorePositionList = {}
        self.sizeLocInfo = {}
        
        checkList = {}
        orderedListCopy = copy.copy(self.orderedModules)
        
        for m in self.orderedModules:
            checkList[m] = False
         
        # first do the root modules """        
        for m in self.rootModules:
            #Size each module and store it
            if not self.Module[ self.moduleIndexDict[m] ].doInitialSize(self):
                guiFactory.warning("Failed to get a size return on '%s'"%m)
                return False

            checkList.pop(m)
            orderedListCopy.remove(m)
            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # NEED TO DO CHILDREN MODULES NEXT
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
        
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Delete the temp locs 
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        """
        for i,m in enumerate(self.ModulesBuffer.bufferList):
            buffer = self.sizeLocInfo[m] 
            parentBuffer = search.returnAllParents( buffer )
            if mc.objExists(parentBuffer[-1]):
                mc.delete(parentBuffer[-1])"""        
        return    
