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
    def __init__(self, moduleName = '', moduleParent = False, position = False, direction = False, directionModifier = False, nameModifier = False,*a,**kw):
        """ 
        Intializes an module master class handler
        
        Keyword arguments:
        moduleName(string) -- either base name or the name of an existing module in scene
        moduleParent(string) -- module parent to connect to. MUST exist if called. If the default False flag is passed, it looks for what's stored
        
        Naming and template tags. All Default to False
        position(string) -- position tag
        direction(string) -- direction
        directionModifier(string)
        
        """
        self.moduleNull = False
        self.infoNulls = {}
        self.parentTagDict = {}
        self.refPrefix = None
        self.refState = False
        
        if mc.objExists(moduleParent):
            self.parentTagDict = NameFactory.returnObjectGeneratedNameDict(moduleParent, ignore = ['cgmName','cgmIterator','cgmTypeModifier','cgmType'])
        
        self.callTags = {'cgmPosition':position, 
                         'cgmDirection':direction, 
                         'cgmDirectionModifier':directionModifier,
                         'cgmNameModifier':nameModifier}
        
        if mc.objExists(moduleName):
            #Make a name dict to check
            if search.findRawTagInfo(moduleName,'cgmType') == 'module':
                self.nameBase = search.findRawTagInfo(moduleName,'cgmName')
                self.nameModifier =  search.findRawTagInfo(moduleName,'cgmNameModifier')
                self.position =  search.findRawTagInfo(moduleName,'cgmPosition')
                self.directionModifier =  search.findRawTagInfo(moduleName,'cgmDirectionModifier')
                self.direction =  search.findRawTagInfo(moduleName,'cgmDirection')
                self.typeModifier =  search.findRawTagInfo(moduleName,'cgmTypeModifier')
                self.moduleParent = attributes.doGetAttr(moduleName,'moduleParent')
                
                self.moduleNull = moduleName
                self.isRef()
                guiFactory.report("'%s' exists. Checking..."%moduleName)

            else:
                guiFactory.warning("'%s' isn't a cgm module. Can't initialize"%moduleName)
                return False
                    
        else:
            #Set some variables
            self.nameBase = moduleName
            self.nameModifier = nameModifier                        
            self.direction = direction
            self.directionModifier = directionModifier
            self.position = position
            self.moduleParent = moduleParent
            self.typeModifier = False
                        
        if not self.refState:
            if not self.verifyModule():
                guiFactory.warning("'%s' failed to verify!"%moduleName)
                return False
        else:
            guiFactory.report("'%s' Referenced. Cannot verify, initializing..."%moduleName)
            if not self.initializeModule():
                guiFactory.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%moduleName)
                return False

                
    def isRef(self):
        if mc.referenceQuery(self.moduleNull, isNodeReferenced=True):
            self.refState = True
            self.refPrefix = search.returnReferencePrefix(self.moduleNull)
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
        
    def verifyModule(self):
        """
        Verifies the integrity of the base module class null. Repairing and restoring broken connections or deleted items.
        """
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Nulls creation
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        #need a check to see if it exists from specfic name call
        if not self.moduleNull:
            #See if one exists from the name dict
            buffer = NameFactory.returnCombinedNameFromDict(self.generateNameDict())
            if mc.objExists(buffer):
                self.moduleNull = buffer
        #if we still don't have one, make it
        if not self.moduleNull:
            self.moduleNull = mc.group(empty=True)
            
        #Initialize the module parent attr
        self.aModuleParent = AttrFactory(self.moduleNull,'moduleParent','message',self.moduleParent)

        #Naming stuff           
        attributes.storeInfo(self.moduleNull,'cgmName',self.nameBase,True)   
        attributes.storeInfo(self.moduleNull,'cgmType','module')
        attributes.storeInfo(self.moduleNull,'moduleType','None')
        
        #Store any naming tags from the init call
        for k in self.callTags.keys():
            if self.callTags.get(k):
                attributes.storeInfo(self.moduleNull,k,self.callTags.get(k),True)
            elif k in self.parentTagDict.keys():
                attributes.storeInfo(self.moduleNull,k,'%s.%s.'%(self.aModuleParent.value,k))                    
            
        self.moduleNull = NameFactory.doNameObject(self.moduleNull,True)
        mc.xform (self.moduleNull, os=True, piv= (0,0,0)) 
        
        self.aTemplateState = AttrFactory(self.moduleNull,'templateState','int',initialValue=0)
        self.aRigState = AttrFactory(self.moduleNull,'rigState','int',initialValue=0)
        self.aSkeletonState = AttrFactory(self.moduleNull,'skeletonState','int',initialValue=0)
        
        attributes.doSetLockHideKeyableAttr(self.moduleNull,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
    

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Main Nulls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>         
        self.aRigNull = AttrFactory(self.moduleNull,'rigNull','message')
        self.aTemplateNull = AttrFactory(self.moduleNull,'templateNull','message')
        self.aInfoNull = AttrFactory(self.moduleNull,'info','message')
        
        for null in [self.aRigNull, self.aTemplateNull,self.aInfoNull]:
            created = False
            if not null.value:
                #If there's nothing connected to our message, we're gonna make our null
                guiFactory.report("'%s' not found. Creating"%self.aRigNull.attr)
                createBuffer = mc.group (empty=True)
                created = True
            else:
                createBuffer = null.value
                
            if null.attr == 'info':
                #Special case stuff for the master info null
                attributes.storeInfo(createBuffer,'cgmName','master',True)  
                attributes.storeInfo(createBuffer,'cgmType','infoNull')
                
            else:
                attributes.storeInfo(createBuffer,'cgmType',null.attr)
                
            mc.xform (createBuffer, os=True, piv= (0,0,0)) 
            createBuffer = rigging.doParentReturnName(createBuffer,self.moduleNull)
            
            if created and mc.ls(created,long=True) != null.value:
                null.doStore(createBuffer)
                
            attributes.doSetLockHideKeyableAttr(createBuffer)
            NameFactory.doNameObject(createBuffer) 
            null.updateData()
            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Info Nulls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        for k in InfoNullsNames:
            self.infoNulls[k] = AttrFactory(self.aInfoNull.value,k,'message')
            
            if not self.infoNulls[k].value:
                guiFactory.report("'%s' not found. Creating"%k)                
                createBuffer = modules.createInfoNull(k)
                self.infoNulls[k].doStore(createBuffer)
                
            if self.infoNulls[k].value:  
                attributes.doSetLockHideKeyableAttr(self.infoNulls[k].value)                
                if rigging.doParentReturnName( self.infoNulls[k].value,self.aInfoNull.value):
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
        assert mc.objExists(self.moduleNull),"'%s' doens't exist"%self.moduleNull
            
        #Initialize the module parent attr
        self.aModuleParent = AttrFactory(self.moduleNull,'moduleParent')

        #Verfiy vital attributes on module Null
        for a in 'moduleType','cgmType':
            if not mc.objExists("%s.%s"%(self.moduleNull,a)):
                guiFactory("'%s.%s' missing. Initialization Aborted!"%(self.moduleNull,a))
                return False                
                    
        self.aTemplateState = AttrFactory(self.moduleNull,'templateState')
        self.aRigState = AttrFactory(self.moduleNull,'rigState')
        self.aSkeletonState = AttrFactory(self.moduleNull,'skeletonState')
            

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Main Nulls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>         
        self.aRigNull = AttrFactory(self.moduleNull,'rigNull')
        self.aTemplateNull = AttrFactory(self.moduleNull,'templateNull')
        self.aInfoNull = AttrFactory(self.moduleNull,'info')
        
        for null in [self.aRigNull, self.aTemplateNull,self.aInfoNull]:
            if null.form != 'message':
                guiFactory("'%s' isn't a message. Initialization Aborted!"%(null.nameCombined))                
                return False
            if not mc.objExists(null.value):
                guiFactory("'%s' has no connection. Initialization Aborted!"%(null.nameCombined))                                
                return False
            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Info Nulls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        for k in InfoNullsNames:
            self.infoNulls[k] = AttrFactory(self.aInfoNull.value,k)
            if self.infoNulls[k].form != 'message':
                guiFactory("'%s' isn't a message. Initialization Aborted!"%(self.infoNulls[k].nameCombined))                
                return False            
            
            if not self.infoNulls[k].value:
                guiFactory.report("'%s' not found. Initialization Aborted!"%k)
                return False
                

        return True
    
    def setModuleParent(self,moduleParent):
        if search.returnTagInfo(moduleParent,'cgmType') == 'module':
            self.moduleParent = moduleParent
            self.aModuleParent = AttrFactory(self.moduleNull,'moduleParent','message',self.moduleParent)
        else:
            guiFactory.warning("'%s' isn't tagged as a module."%moduleParent)


                
            
