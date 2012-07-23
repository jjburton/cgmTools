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
import random

from cgm.lib.classes import NameFactory
from cgm.lib.classes.AttrFactory import *

from cgm.lib import (modules,
                     rigging)

reload(modules)
reload(rigging)

InfoNullsNames = ['setupOptions',
                  'templatePosObjects',
                  'visibilityOptions',
                  'templateControlObjects',
                  'coreNames',
                  'templateStarterData',
                  'templateControlObjectsData',
                  'skinJoints',
                  'rotateOrders']

""" 1 """
class ModuleFactory:
    def __init__(self, moduleName = '', moduleParent = False, position = False, direction = False, directionModifier = False, nameModifier = False, forceNew = False,*a,**kw):
        """ 
        Intializes an module master class handler
        
        Keyword arguments:
        moduleName(string) -- either base name or the name of an existing module in scene
        moduleParent(string) -- module parent to connect to. MUST exist if called. If the default False flag is passed, it looks for what's stored
        
        Naming and template tags. All Default to False
        position(string) -- position tag
        direction(string) -- direction
        directionModifier(string)
        nameModifier(string)
        forceNew(bool) --whether to force the creation of another if the object exists
        
        """
        self.ModuleNull = False
        self.infoNulls = {}
        self.parentTagDict = {}
        self.refPrefix = None
        self.refState = False    
        self.moduleClass = None
        
        # Get parent info and the call tags to check later on
        if mc.objExists(moduleParent):
            self.parentTagDict = NameFactory.returnObjectGeneratedNameDict(moduleParent, ignore = ['cgmName','cgmIterator','cgmTypeModifier','cgmType'])
        
        self.callTags = {'cgmPosition':position, 
                         'cgmDirection':direction, 
                         'cgmDirectionModifier':directionModifier,
                         'cgmNameModifier':nameModifier}
        
        # If the object doesn't exist, we're first going to fill in our base flags from the init call
        if not mc.objExists(moduleName) or forceNew:
            #Set some variables
            self.nameBase = moduleName
            self.nameModifier = nameModifier                        
            self.direction = direction
            self.directionModifier = directionModifier
            self.position = position
            self.moduleParent = moduleParent
            self.typeModifier = False            
               
        else:
            #Make a name dict to check
            if search.findRawTagInfo(moduleName,'cgmType') == 'module':
                self.nameBase = search.findRawTagInfo(moduleName,'cgmName')
                self.nameModifier =  search.findRawTagInfo(moduleName,'cgmNameModifier')
                self.position =  search.findRawTagInfo(moduleName,'cgmPosition')
                self.directionModifier =  search.findRawTagInfo(moduleName,'cgmDirectionModifier')
                self.direction =  search.findRawTagInfo(moduleName,'cgmDirection')
                self.typeModifier =  search.findRawTagInfo(moduleName,'cgmTypeModifier')
                self.moduleParent = attributes.doGetAttr(moduleName,'moduleParent')
                
                self.ModuleNull = ObjectFactory(moduleName)
                self.refState = self.ModuleNull.refState
                guiFactory.report("'%s' exists. Checking..."%moduleName)

            else:
                guiFactory.warning("'%s' isn't a cgm module. Can't initialize"%moduleName)
                return False
                        
        if not self.refState:
            if not self.verifyModule(forceNew):
                guiFactory.warning("'%s' failed to verify!"%moduleName)
                return False
        else:
            guiFactory.report("'%s' Referenced. Cannot verify, initializing..."%moduleName)
            if not self.initializeModule():
                guiFactory.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%moduleName)
                return False

                
    def isRef(self):
        if mc.referenceQuery(self.ModuleNull.nameShort, isNodeReferenced=True):
            self.refState = True
            self.refPrefix = search.returnReferencePrefix(self.ModuleNull.nameShort)
            return
        self.refState = False
        self.refPrefix = None
        
    def generateNameDict(self):
        """
        Generate a name dict to test if anything with that 'would be' name exists.
        
        Returns
        returnDict(dict)
        """
        returnDict = {}
        returnDict['cgmName']=self.nameBase
        returnDict['cgmNameModifier']= self.nameModifier                         
        returnDict['cgmDirection']= self.direction 
        returnDict['cgmDirectionModifier']= self.directionModifier 
        returnDict['cgmPosition']= self.position 
        returnDict['cgmTypeModifier']= self.typeModifier
        returnDict['cgmType']= 'module'
        
        return returnDict
        
    def verifyModule(self,forceNew = False):
        """
        Verifies the integrity of the base module class null. Repairing and restoring broken connections or deleted items.
        """
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Nulls creation
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        #need a check to see if it exists from specfic name call
        if not self.ModuleNull or forceNew:
            #See if one exists from the name dict
            buffer = NameFactory.returnCombinedNameFromDict(self.generateNameDict())
            if mc.objExists(buffer):
                if forceNew:
                    cnt = NameFactory.returnIterateNumber(buffer)
                    self.ModuleNull = ObjectFactory(mc.group(empty=True))
                    self.ModuleNull.store('cgmIterator',cnt)
                else:
                    self.ModuleNull = ObjectFactory(buffer)
                
        #if we still don't have one, make it
        if not self.ModuleNull:
            self.ModuleNull = ObjectFactory(mc.group(empty=True))
            
        #Initialize the module parent attr
        self.afModuleParent = AttrFactory(self.ModuleNull,'moduleParent','message',self.moduleParent)

        #Naming stuff           
        self.ModuleNull.store('cgmName',self.nameBase,True)   
        self.ModuleNull.store('cgmType','module')
        self.afModuleType = AttrFactory(self.ModuleNull,'moduleType',initialValue='None')
        
        #Store any naming tags from the init call
        for k in self.callTags.keys():
            if self.callTags.get(k):
                self.ModuleNull.store(k,self.callTags.get(k),True)
            elif k in self.parentTagDict.keys():
                self.ModuleNull.store(k,'%s.%s'%(self.afModuleParent.value,k))                    
            
        self.ModuleNull.doName(True)
        mc.xform (self.ModuleNull.nameShort, os=True, piv= (0,0,0)) 
        
        self.afTemplateState = AttrFactory(self.ModuleNull,'templateState','int',initialValue=0)
        self.afRigState = AttrFactory(self.ModuleNull,'rigState','int',initialValue=0)
        self.afSkeletonState = AttrFactory(self.ModuleNull,'skeletonState','int',initialValue=0)
        
        attributes.doSetLockHideKeyableAttr(self.ModuleNull.nameShort,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
    

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Main Nulls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>         
        self.afRigNull = AttrFactory(self.ModuleNull,'rigNull','message')
        self.afTemplateNull = AttrFactory(self.ModuleNull,'templateNull','message')
        self.afInfoNull = AttrFactory(self.ModuleNull,'info','message')
        
        nullAttributes = [self.afRigNull, self.afTemplateNull, self.afInfoNull]
        nullInstances = ['RigNull', 'TemplateNull', 'InfoNull']
        
        for i,null in enumerate(nullAttributes):
            created = False
            if not null.value:
                #If there's nothing connected to our message, we're gonna make our null
                guiFactory.report("'%s' not found. Creating"%null.attr)
                self.__dict__[ nullInstances[i] ] = ObjectFactory(mc.group(empty=True))
                created = True
            else:
                self.__dict__[ nullInstances[i] ] = ObjectFactory(null.value)
                
            if null.attr == 'info':
                #Special case stuff for the master info null
                self.__dict__[ nullInstances[i] ].store('cgmName','master',True)  
                self.__dict__[ nullInstances[i] ].store('cgmType','infoNull')
                
            else:
                self.__dict__[ nullInstances[i] ].store('cgmType',null.attr)
                
            mc.xform (self.__dict__[ nullInstances[i] ].nameShort, os=True, piv= (0,0,0)) 
            self.__dict__[ nullInstances[i] ].doParent(self.ModuleNull.nameShort)
            
            if created and self.__dict__[ nullInstances[i] ].nameLong != null.value:
                null.doStore(self.__dict__[ nullInstances[i] ].nameLong)
                
            attributes.doSetLockHideKeyableAttr(self.__dict__[ nullInstances[i] ].nameShort)
            self.__dict__[ nullInstances[i] ].doName(True)
            null.updateData()
            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Info Nulls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        for k in InfoNullsNames:
            self.infoNulls[k] = AttrFactory(self.InfoNull,k,'message')
            
            if not self.infoNulls[k].value:
                guiFactory.report("'%s' not found. Creating"%k)                
                createBuffer = modules.createInfoNull(k)
                self.infoNulls[k].doStore(createBuffer)
                
            if self.infoNulls[k].value:  
                attributes.doSetLockHideKeyableAttr(self.infoNulls[k].value)                
                if rigging.doParentReturnName( self.infoNulls[k].value,self.afInfoNull.value):
                    buffer = NameFactory.doNameObject(self.infoNulls[k].value)
                    if buffer != self.infoNulls[k].value:
                        self.infoNulls[k].doStore(buffer)
                    else:
                        self.infoNulls[k].updateData()
                        
            else:
                guiFactory.warning("'%s' has failed to initialize"%k)

        return True
    
    def initializeModule(self):
        """
        Only initialized the data. References default to this. 
        """
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Nulls creation
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        #need a check to see if it exists from specfic name call
        assert mc.objExists(self.ModuleNull.nameShort),"'%s' doens't exist"%self.ModuleNull.nameShort
        
        self.nameBase = search.returnTagInfo(self.ModuleNull.nameShort,'cgmName')
            
        #Initialize the module parent attr
        self.afModuleParent = AttrFactory(self.ModuleNull,'moduleParent')
        self.afModuleType = AttrFactory(self.ModuleNull,'moduleType')

        #Verfiy vital attributes on module Null
        for a in 'moduleType','cgmType':
            if not mc.objExists("%s.%s"%(self.ModuleNull.nameShort,a)):
                guiFactory("'%s.%s' missing. Initialization Aborted!"%(self.ModuleNull.nameShort,a))
                return False                
                    
        self.afTemplateState = AttrFactory(self.ModuleNull,'templateState')
        self.afRigState = AttrFactory(self.ModuleNull,'rigState')
        self.afSkeletonState = AttrFactory(self.ModuleNull,'skeletonState')
            

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Main Nulls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>         
        self.afRigNull = AttrFactory(self.ModuleNull,'rigNull')
        self.afTemplateNull = AttrFactory(self.ModuleNull,'templateNull')
        self.afInfoNull = AttrFactory(self.ModuleNull,'info')
        
        nullAttributes = [self.afRigNull, self.afTemplateNull, self.afInfoNull]
        nullInstances = ['RigNull', 'TemplateNull', 'InfoNull']  
        
        for i,null in enumerate(nullAttributes):
            if null.form != 'message':
                guiFactory("'%s' isn't a message. Initialization Aborted!"%(null.nameCombined))                
                return False
            if not mc.objExists(null.value):
                guiFactory("'%s' has no connection. Initialization Aborted!"%(null.nameCombined))                                
                return False
            else:
                self.__dict__[ nullInstances[i] ] = ObjectFactory(null.value)
            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Info Nulls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        for k in InfoNullsNames:
            self.infoNulls[k] = AttrFactory(self.InfoNull,k)
            if self.infoNulls[k].form != 'message':
                guiFactory("'%s' isn't a message. Initialization Aborted!"%(self.infoNulls[k].nameCombined))                
                return False            
            
            if not self.infoNulls[k].value:
                guiFactory.report("'%s' not found. Initialization Aborted!"%k)
                return False
                

        return True
    
    def setParentModule(self,moduleParent):
        assert mc.objExists(moduleParent),"'%s' doesn't exists! Can't be module parent of '%s'"%(moduleParent,self.ModuleNull.nameShort)
        if search.returnTagInfo(moduleParent,'cgmType') == 'module':
            if self.afModuleParent.value != moduleParent:
                self.moduleParent = moduleParent
                self.afModuleParent = AttrFactory(self.ModuleNull,'moduleParent','message',self.moduleParent)
                guiFactory.repport("'%s' is not the module parent of '%s'"%(moduleParent,self.ModuleNull.nameShort))
            else:
                guiFactory.warning("'%s' already this module's parent. Moving on..."%moduleParent)                
        else:
            guiFactory.warning("'%s' isn't tagged as a module."%moduleParent)
            
    def changeCGMTag(self,tag,string,*a,**kw):
        if tag not in NameFactory.cgmNameTags:
            guiFactory.warning("'%s' is not a valid cgm name tag."%(tag))         
            return False
        
        if string in [None,False,'None','none']:
            guiFactory.warning("Removing '%s.%s'"%(self.ModuleNull.nameShort,tag))            
            self.ModuleNull.remove(tag)
            self.ModuleNull.doName(True,True)            
            return True
            
        elif self.ModuleNull.cgm[tag] == string:
            guiFactory.warning("'%s.%s' already has base name of '%s'."%(self.ModuleNull.nameShort,tag,string))
            return False
        else:
            self.ModuleNull.store(tag,string,True,*a,**kw)
            self.ModuleNull.doName(True,True)
            return True    
                
            
