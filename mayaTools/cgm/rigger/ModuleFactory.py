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
                     rigging,
                     locators)

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

cvDict = {'left':3,'right':7,'bottom':5,'top':0, 'left_front':4, 'right_front':6, 'left_back':2,'right_back':8,'None':0}

""" 1 """
class ModuleFactory:
    def __init__(self,moduleName = '',*a,**kw):
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
        #>>>Keyword args
        moduleParent = kw.pop('moduleParent',False)
        position = kw.pop('position',False)
        direction = kw.pop('direction',False)
        directionModifier = kw.pop('directionModifier',False)
        nameModifier = kw.pop('nameModifier',False)
        forceNew = kw.pop('forceNew',False)
        initializeOnly = kw.pop('initializeOnly',False)

        #>>>Variables      
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
        
        if self.refState or initializeOnly:
            guiFactory.report("'%s' Module Initializing..."%moduleName)
            if not self.initializeModule():
                guiFactory.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%moduleName)
                return False                        
        else:
            if not self.verifyModule(forceNew):
                guiFactory.warning("'%s' failed to verify!"%moduleName)
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
        assert mc.objExists(self.nameBase),"'%s' doens't exist"%self.nameBase
        
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
        
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> Sizing
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def doInitialSize(self,PuppetInstance):
        guiFactory.report("Sizing via module'%s'"%self.ModuleNull.nameBase)
        return guiFactory.warning("This isn't done yet. Push to a subclass")

        
        
    def doCreateStartingPositionLoc(self, modeType='child', workingObject=None, aimingObject=None, cvIndex = None ):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Adds a locator setup to duplicate to get our initial position locators. All should be zeroed out.
        The top node of the return group has the loctor and move group connected is message nodes if needed.
        
        ARGUMENTS:
        modeType(string)
            child - basic child locator to the workingObject
            innerChild - aims locator from the working to the aiming curves
            cvBack - works off working curves cvIndex. Places it and aiming
                        it back on z. Mainly used for tails
            radialOut - Works off working curve cv for position and radial 
                        orientation. It's transform group is oriented to 
                        the aiming curves equivalent cv. Good for arms
            radialDown - same as radial out but locator orientation is y down zup for legs.
                        transform orientation is the same as radial out
            footBase - looking for it's module Parent's last loc to start from
            parentDuplicate - looking for it's module Parent's last loc to start from
            
        workingObject(string) - usually the sizing objects start curve (can be a locator for parentchild loc)
        aimingObject(string) - usually the sizing objects end curve
        cvIndex(int) - cv to work off of
        
        RETURNS:
        returnList(list) = [rootHelper(string),helperObjects(list),helperObjectGroups(list)]
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        
        if modeType == 'child':
            """ make initial loc and orient it """
            returnLoc = []
            curveShapes = mc.listRelatives(workingObject, shapes = True)
            startLoc = locators.locMeObject(workingObject)
            aimLoc = locators.locMeObject(workingObject)
            upLoc = locators.locMeCvFromCvIndex(curveShapes[0],0)
            
            startLoc = mc.rename(startLoc,(self.ModuleNull.nameBase+'child_startLoc'))
            
            sizeObjectLength = distance.returnDistanceBetweenObjects(workingObject,aimingObject)
            mc.xform(aimLoc,t=[0,0,sizeObjectLength],r=True,os=True)
            aimConstraintBuffer = mc.aimConstraint(aimLoc,startLoc,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
            mc.delete(aimConstraintBuffer[0])
            mc.delete(upLoc)
            mc.delete(aimLoc)
            
            returnLoc.append(startLoc)
            zeroGroup = rigging.zeroTransformMeObject(startLoc)
            attributes.storeInfo(zeroGroup,'locator',startLoc)
            returnLoc.append(zeroGroup)
            
            return returnLoc
            
        elif modeType == 'innerChild':       
            """ make initial lock and orient it """
            returnLoc = []
            curveShapes = mc.listRelatives(workingObject, shapes = True)
            startLoc = locators.locMeObject(workingObject)
            aimLoc = locators.locMeObject(aimingObject)
            upLoc = locators.locMeCvFromCvIndex(curveShapes[0],0)
            startLoc = mc.rename(startLoc, (self.ModuleNull.nameBase+'_innerChild_startLoc'))
            
            aimConstraintBuffer = mc.aimConstraint(aimLoc,startLoc,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
            mc.delete(aimConstraintBuffer[0])
            mc.delete(upLoc)
            mc.delete(aimLoc)
            
            returnLoc.append(startLoc)
            zeroGroup = rigging.groupMeObject(startLoc)            
            #zeroGroup = rigging.zeroTransformMeObject(startLoc)
            #attributes.storeInfo(zeroGroup,'locator',startLoc)
            returnLoc.append(zeroGroup)
            
            return returnLoc
            
        elif  modeType == 'cvBack':
            returnLoc = []
            curveShapes = mc.listRelatives(workingObject, shapes = True)
            startLoc = locators.locMeCvFromCvIndex(curveShapes[0],cvIndex)
            upLoc = locators.locMeObject(workingObject)
            
            initialAimLoc = locators.locMeObject(aimingObject)
            aimConstraintBuffer = mc.aimConstraint(initialAimLoc,startLoc,maintainOffset = False, weight = 1, aimVector = [0,0,-1], upVector = [0,-1,0],  worldUpObject = upLoc, worldUpType = 'object', skip = ['x','z'])
            mc.delete(aimConstraintBuffer[0])
            mc.delete(initialAimLoc)
    
            aimLoc = locators.locMeCvFromCvIndex(curveShapes[0],cvIndex)
            startLoc = mc.rename(startLoc, (self.ModuleNull.nameBase+'_radialBackl_startLoc'))
            
            sizeObjectLength = distance.returnDistanceBetweenObjects(workingObject,aimingObject)
            mc.xform(aimLoc,t=[0,0,-sizeObjectLength],r=True,ws=True)
            aimConstraintBuffer = mc.aimConstraint(aimLoc,startLoc,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpType = 'vector' )
            mc.delete(aimConstraintBuffer[0])
            mc.delete(aimLoc)
            mc.delete(upLoc)
            returnLoc.append(startLoc)
            zeroGroup = rigging.groupMeObject(startLoc)
            returnLoc.append(zeroGroup)
            
            return returnLoc
            
        elif  modeType == 'radialOut':
            sizeObjectLength = distance.returnDistanceBetweenObjects(workingObject,aimingObject)
            
            returnLoc = []
            
            workingObjectShapes = mc.listRelatives(workingObject, shapes = True)
            aimingObjectShapes = mc.listRelatives(aimingObject, shapes = True)
            
            """initial loc creation and orientation"""
            startLoc = locators.locMeCvFromCvIndex(workingObjectShapes[0],cvIndex)
            startLocAim = locators.locMeObject(workingObject)
            startLocUp = locators.locMeCvFromCvIndex(workingObjectShapes[0],cvIndex)
            startLoc = mc.rename(startLoc, (self.ModuleNull.nameBase+'_radialOut_startLoc'))
            """ move the up loc up """
            mc.xform(startLocUp,t=[0,sizeObjectLength,0],r=True,ws=True)
    
            """ aim it """
            aimConstraintBuffer = mc.aimConstraint(startLocAim,startLoc,maintainOffset = False, weight = 1, aimVector = [0,0,-1], upVector = [0,1,0], worldUpType = 'vector' )
            mc.delete(aimConstraintBuffer[0])
            mc.delete(startLocUp)
            
            """ setup the transform group"""
            transformGroup = rigging.groupMeObject(startLoc,False)
            transformGroup = mc.rename(transformGroup,('%s%s' %(startLoc,'_moveGroup')))
            groupUp = startLocAim
            groupAim = locators.locMeCvFromCvIndex(aimingObjectShapes[0],cvIndex)
            
            """aim it"""
            aimConstraintBuffer = mc.aimConstraint(groupAim,transformGroup,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,-1,0],  worldUpObject = groupUp, worldUpType = 'object')
            mc.delete(aimConstraintBuffer[0])
            mc.delete(groupUp)
            mc.delete(groupAim)
            
            startLoc = rigging.doParentReturnName(startLoc,transformGroup)
            rigging.zeroTransformMeObject(startLoc)
            returnLoc.append(startLoc)
            returnLoc.append(transformGroup)
            zeroGroup = rigging.groupMeObject(transformGroup)
            attributes.storeInfo(zeroGroup,'move',transformGroup)
            returnLoc.append(zeroGroup)
            
            return returnLoc
            
        elif  modeType == 'radialDown':
            sizeObjectLength = distance.returnDistanceBetweenObjects(workingObject,aimingObject)
            returnLoc = []
            
            workingObjectShapes = mc.listRelatives(workingObject, shapes = True)
            aimingObjectShapes = mc.listRelatives(aimingObject, shapes = True)
            
            """initial loc creation and orientation"""
            startLoc = locators.locMeCvFromCvIndex(workingObjectShapes[0],cvIndex)
            startLocAim = locators.locMeCvFromCvIndex(workingObjectShapes[0],cvIndex)
            startLoc = mc.rename(startLoc, (self.ModuleNull.nameBase+'_radialDown_startLoc'))
            
            """ move the up loc up """
            mc.xform(startLocAim,t=[0,-sizeObjectLength,0],r=True, ws=True)
            
            """ aim it """
            aimConstraintBuffer = mc.aimConstraint(startLocAim,startLoc,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,0,1], worldUpType = 'vector' )
            mc.delete(aimConstraintBuffer[0])
            
            
            """ setup the transform group"""
            transformGroup = rigging.groupMeObject(startLoc,False)
            transformGroup = mc.rename(transformGroup,('%s%s' %(startLoc,'_moveGroup')))
            groupUp = startLocAim
            groupAim = locators.locMeCvFromCvIndex(aimingObjectShapes[0],cvIndex)
            
            """aim it"""
            aimConstraintBuffer = mc.aimConstraint(groupAim,transformGroup,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,-1,0],  worldUpObject = groupUp, worldUpType = 'object')
            mc.delete(aimConstraintBuffer[0])
            mc.delete(groupUp)
            mc.delete(groupAim)
            
            startLoc = rigging.doParentReturnName(startLoc,transformGroup)
            rigging.zeroTransformMeObject(startLoc)
            returnLoc.append(startLoc)
            returnLoc.append(transformGroup)
            zeroGroup = rigging.groupMeObject(transformGroup)
            attributes.storeInfo(zeroGroup,'move',transformGroup)
            returnLoc.append(zeroGroup)
            
            return returnLoc
            
        elif modeType == 'footBase':
            returnLoc = []
            startLoc = locators.locMeObject(workingObject)
            startLoc = mc.rename(startLoc,(self.ModuleNull.nameBase+'_footcgmase_startLoc'))
            masterGroup = rigging.groupMeObject(startLoc)
            
            mc.setAttr((startLoc+'.rx'),-90)
            returnLoc.append(startLoc)
            zeroGroup = rigging.zeroTransformMeObject(startLoc)
            
            currentPos = mc.xform(zeroGroup,q=True, t=True,ws=True)
            mc.xform(zeroGroup,t=[currentPos[0],0,currentPos[2]], ws = True)
            
            attributes.storeInfo(zeroGroup,'locator',startLoc)
            returnLoc.append(zeroGroup)
            returnLoc.append(masterGroup)
            
            return returnLoc
            
        elif modeType == 'parentDuplicate':
            returnLoc = []
            startLoc = locators.locMeObject(workingObject)
            startLoc = mc.rename(startLoc,(self.ModuleNull.nameBase+'_parentDup_startLoc'))
            masterGroup = rigging.groupMeObject(startLoc)
            returnLoc.append(startLoc)
            returnLoc.append(masterGroup)
            
            return returnLoc
        else:
            return False
                
            
