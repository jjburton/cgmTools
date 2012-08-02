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
                     distance,
                     position,
                     logic,
                     rigging,
                     cgmMath,
                     locators)

reload(modules)
reload(rigging)

InfoNullsNames = ['settings',
                  'setupOptions',
                  'templatePosObjects',
                  'visibilityOptions',
                  'templateControlObjects',
                  'coreNames',
                  'templateStarterData',
                  'templateControlObjectsData',
                  'skinJoints',
                  'rotateOrders']

cvDict = {'left':3,'right':7,'bottom':5,'top':0, 'left_front':4, 'right_front':6, 'left_back':2,'right_back':8,'None':0}

moduleStates = ['template','deform','rig']

initLists = []
initDicts = ['infoNulls','parentTagDict']
initStores = ['ModuleNull','refState']
initNones = ['refPrefix','moduleClass']

defaultSettings = {'partType':'none'}

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
        self.handles = kw.pop('handles',1)
        
        #>>>Variables  
        for l in initLists:
            self.__dict__[l] = []
        for d in initDicts:
            self.__dict__[d] = {}
        for o in initStores:
            self.__dict__[o] = False
        for o in initStores:
            self.__dict__[o] = None
            
        
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
        for k in defaultSettings.keys():
            try:
                self.__dict__[k]
            except:
                self.__dict__[k] = defaultSettings[k]       
                
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
        self.msgModuleParent = AttrFactory(self.ModuleNull,'moduleParent','message',self.moduleParent)

        #Naming stuff           
        self.ModuleNull.store('cgmName',self.nameBase,True)   
        self.ModuleNull.store('cgmType','module')
        self.afModuleType = AttrFactory(self.ModuleNull,'moduleType',initialValue='None')
        
        #Store any naming tags from the init call
        for k in self.callTags.keys():
            if self.callTags.get(k):
                self.ModuleNull.store(k,self.callTags.get(k),True)
            elif k in self.parentTagDict.keys():
                self.ModuleNull.store(k,'%s.%s'%(self.msgModuleParent.value,k))                    
            
        self.ModuleNull.doName(True)
        mc.xform (self.ModuleNull.nameShort, os=True, piv= (0,0,0)) 
        
        for flag in moduleStates:
            self.__dict__["af%sState"%flag.capitalize()] = AttrFactory(self.ModuleNull,'%sState'%flag,'bool',initialValue=0,lock=True)

        attributes.doSetLockHideKeyableAttr(self.ModuleNull.nameShort,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
    
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Main Nulls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>         
        self.msgRigNull = AttrFactory(self.ModuleNull,'rigNull','message')
        self.msgTemplateNull = AttrFactory(self.ModuleNull,'templateNull','message')
        self.msgInfoNull = AttrFactory(self.ModuleNull,'info','message')
        
        nullAttributes = [self.msgRigNull, self.msgTemplateNull, self.msgInfoNull]
        nullInstances = ['RigNull', 'TemplateNull', 'InfoNull']
        
        for i,null in enumerate(nullAttributes):
            created = False
            if not null.get():
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
                if rigging.doParentReturnName( self.infoNulls[k].value,self.msgInfoNull.value):
                    buffer = NameFactory.doNameObject(self.infoNulls[k].value)
                    if buffer != self.infoNulls[k].value:
                        self.infoNulls[k].doStore(buffer)
                    else:
                        self.infoNulls[k].updateData()
                        
            else:
                guiFactory.warning("'%s' has failed to initialize"%k)
       
        if self.infoNulls['setupOptions']:
            self.SetupOptionsNull = ObjectFactory( self.infoNulls['setupOptions'].get() )            
            self.optionHandles = AttrFactory(self.SetupOptionsNull,'handles','int',initialValue=self.handles)
        
        if self.infoNulls['settings']:
            self.optionAimAxis = AttrFactory(self.infoNulls['settings'].get(),'axisAim','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=2) 
            self.optionUpAxis = AttrFactory(self.infoNulls['settings'].get(),'axisUp','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=1) 
            self.optionOutAxis = AttrFactory(self.infoNulls['settings'].get(),'axisOut','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=0)                       
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
        self.msgModuleParent = AttrFactory(self.ModuleNull,'moduleParent')
        self.afModuleType = AttrFactory(self.ModuleNull,'moduleType')

        #Verfiy vital attributes on module Null
        for a in 'moduleType','cgmType':
            if not mc.objExists("%s.%s"%(self.ModuleNull.nameShort,a)):
                guiFactory("'%s.%s' missing. Initialization Aborted!"%(self.ModuleNull.nameShort,a))
                return False      
        
        for flag in moduleStates:
            self.__dict__["af%sState"%flag.capitalize()] = AttrFactory(self.ModuleNull,'%sState'%flag)
          

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Main Nulls
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>         
        self.msgRigNull = AttrFactory(self.ModuleNull,'rigNull')
        self.msgTemplateNull = AttrFactory(self.ModuleNull,'templateNull')
        self.msgInfoNull = AttrFactory(self.ModuleNull,'info')
        
        nullAttributes = [self.msgRigNull, self.msgTemplateNull, self.msgInfoNull]
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
                
        if self.infoNulls['setupOptions']:
            self.SetupOptionsNull = ObjectFactory( self.infoNulls['setupOptions'].value )            
            self.optionHandles = AttrFactory(self.SetupOptionsNull,'handles',lock=True)
            
        if self.infoNulls['settings']:
            self.optionAimAxis= AttrFactory(self.infoNulls['settings'].get(),'axisAim') 
            self.optionUpAxis= AttrFactory(self.infoNulls['settings'].get(),'axisUp') 
            self.optionOutAxis= AttrFactory(self.infoNulls['settings'].get(),'axisOut')   
            
        return True
    
    def setParentModule(self,moduleParent):
        assert mc.objExists(moduleParent),"'%s' doesn't exists! Can't be module parent of '%s'"%(moduleParent,self.ModuleNull.nameShort)
        if search.returnTagInfo(moduleParent,'cgmType') == 'module':
            if self.msgModuleParent.value != moduleParent:
                self.moduleParent = moduleParent
                self.msgModuleParent = AttrFactory(self.ModuleNull,'moduleParent','message',self.moduleParent)
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
    def getInitialSize(self,PuppetInstance):
        """
        This is for class specific stuff
        Keyword arguments:
        PuppetInstance(instance) -- should be the module's puppet instance          
        """
        guiFactory.report("Sizing via module'%s'"%self.ModuleNull.nameBase)
        guiFactory.warning("This isn't done yet. Push to a subclass")
        return False
    
    def doInitialSize(self,PuppetInstance):
        """
        Initial storing of initial sizes for a module
        
        
        Keyword arguments:
        PuppetInstance(instance) -- should be the module's puppet instance   
        """
        guiFactory.report("Sizing via module'%s'"%self.ModuleNull.nameBase)
        
        if not self.getInitialSize(PuppetInstance):
            guiFactory.warning("Initial sizing failed!")            
            return False
        
        if not PuppetInstance.sizeCorePositionList[self.ModuleNull.nameBase] and PuppetInstance.sizeLocInfo[self.ModuleNull.nameBase]:      
            guiFactory.warning("Didn't get necessary data")            
            return False   
                            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Store everything
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        corePositionList = PuppetInstance.sizeCorePositionList[self.ModuleNull.nameBase]
        
        starterDataInfoNull = self.infoNulls['templateStarterData'].value #Get the infoNull
        templateControlObjectsDataNull = self.infoNulls['templateControlObjectsData'].value
        
        modules.doPurgeNull( starterDataInfoNull ) # Purge the null
        
        ### store our positional data ###
        for i,pos in enumerate(corePositionList):
            buffer = ('pos_%s' % i)
            AttrFactory(starterDataInfoNull,buffer,attrType='double3',value=pos,lock=True)
    
            
        ### make a place to store rotational data and an extra for the master###
        for i in range(len(corePositionList)+1):
            buffer = ('rot_%s' % i)
            AttrFactory(starterDataInfoNull,buffer,attrType='double3',lock=True)
    
        modules.doPurgeNull(templateControlObjectsDataNull)
        
        ### store our positional data ###
        for i,pos in enumerate(corePositionList):
            buffer = ('pos_%s' % i)
            AttrFactory(templateControlObjectsDataNull,buffer,attrType='double3',value=pos,lock=True)
    
            ### make a place to store rotational data ###
            buffer = ('rot_%s' % i)
            AttrFactory(templateControlObjectsDataNull,buffer,attrType='double3',lock=True)
    
            ### make a place for scale data ###
            buffer = ('scale_%s' %i)
            AttrFactory(templateControlObjectsDataNull,buffer,attrType='double3',lock=True)
    
    
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Need to generate names
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
        coreNames = self.getGeneratedCoreNames()
        if not coreNames:
            return "FAILURE OF CORE NAMES"
        
        coreNamesInfoNull = self.infoNulls['coreNames'].value
        
        modules.doPurgeNull(coreNamesInfoNull)
        ### store our name data###
        for n,name in enumerate(coreNames):
            AttrFactory(coreNamesInfoNull, ('name_%s' % n) ,value=name,lock=True)
    
        #>>>>>>>>>>>>>>>s>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Rotation orders
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        rotateOrderInfoNull = self.infoNulls['rotateOrders'].value  
        
        modules.doPurgeNull(rotateOrderInfoNull)
        
        ### store our rotation order data ###
        for i in range(len(corePositionList)):
            attrNameBuffer = ('rotateOrder_%s' % i)
            attributes.addRotateOrderAttr(rotateOrderInfoNull,attrNameBuffer)
        
        
        guiFactory.report("'%s' sized and stored"%self.ModuleNull.nameBase)    
    
        return True
            
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
            StartLoc = ObjectFactory(startLoc)
            
            sizeObjectLength = distance.returnDistanceBetweenObjects(workingObject,aimingObject)
            mc.xform(aimLoc,t=[0,0,sizeObjectLength],r=True,os=True)
            aimConstraintBuffer = mc.aimConstraint(aimLoc,startLoc,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
            mc.delete(aimConstraintBuffer[0])
            mc.delete(upLoc)
            mc.delete(aimLoc)
            
            zeroGroup = StartLoc.doGroup()
            returnLoc.append(StartLoc.nameLong)
            
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
            StartLoc = ObjectFactory(startLoc)
            
            aimConstraintBuffer = mc.aimConstraint(aimLoc,startLoc,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
            mc.delete(aimConstraintBuffer[0])
            mc.delete(upLoc)
            mc.delete(aimLoc)
            
            zeroGroup = StartLoc.doGroup()  
            returnLoc.append(StartLoc.nameLong)
            
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
            StartLoc = ObjectFactory(startLoc)
            
            sizeObjectLength = distance.returnDistanceBetweenObjects(workingObject,aimingObject)
            mc.xform(aimLoc,t=[0,0,-sizeObjectLength],r=True,ws=True)
            aimConstraintBuffer = mc.aimConstraint(aimLoc,startLoc,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpType = 'vector' )
            mc.delete(aimConstraintBuffer[0])
            mc.delete(aimLoc)
            mc.delete(upLoc)
            returnLoc.append(startLoc)
            zeroGroup = StartLoc.doGroup()  
            returnLoc.append(StartLoc.nameLong)
            
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
            StartLoc = ObjectFactory(startLoc)
            
            
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
            StartLoc = ObjectFactory(startLoc)
            
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
            StartLoc = ObjectFactory(startLoc)
            
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
            StartLoc = ObjectFactory(startLoc)
            
            masterGroup = rigging.groupMeObject(startLoc)
            returnLoc.append(startLoc)
            returnLoc.append(masterGroup)
            
            return returnLoc
        else:
            return False
                
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
        guiFactory.report("Generating Initial position data via ModuleFactory - '%s'"%self.ModuleNull.nameBase)
        partBaseDistance = kw.pop('partBaseDistance',1)
  
    def getPartBaseDistance(self,PuppetInstance,locator):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Pass  a generated locator (z is forward) from this system and it measures the distance
        to the bounding box edge
        
        ARGUMENTS:
        locator(string)
        meshGroup(string)
        
        RETURNS:
        distance(float)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        vectorToStringDict = {'x':[1,0,0],'-x':[1,0,0],'y':[0,1,0],'-y':[0,1,0],'z':[0,0,1],'-z':[0,0,1]}

        """ size distance for pivot """
        boundingBoxSize = distance.returnBoundingBoxSize( PuppetInstance.GeoGroup.nameLong )
        boundingBoxSize = cgmMath.multiplyLists([[.5,.5,.5],boundingBoxSize])
        
        """ make our bounding box pivot """
        cgmLoc = locators.centerPivotLocMeObject( PuppetInstance.GeoGroup.nameLong )
        
        """makeour measure loc and snap it to the the cgmLoc"""
        measureLocBuffer = mc.duplicate(locator)
        measureLoc = measureLocBuffer[0]
        position.movePointSnap(measureLoc,cgmLoc)
        
        """ Get it up on the axis with the cgmLoc back to where it was """
        distanceToPivot = mc.xform(measureLoc,q=True, t=True,os=True)
        mc.xform(measureLoc, t= [0,0,distanceToPivot[2]],os=True)
        
        """ figure out our relationship between our locators, which is in front"""
        measureLocPos = mc.xform(measureLoc,q=True, t=True,os=True)
        mainLocPos = mc.xform(locator,q=True, t=True,os=True)
        
        if measureLocPos[2] < mainLocPos[2]:
            distanceCombineMode = 'subtract'
            locOrder = [measureLoc,locator]
        else:
            distanceCombineMode = 'add'
            locOrder = [locator,measureLoc]
            
            """ determine our aim direction """
        aimDirection = logic.returnLinearDirection(locOrder[0],locOrder[1])
        aimVector = vectorToStringDict.get(aimDirection)
        maxIndexMatch =  max(aimVector)
        maxIndex = aimVector.index(maxIndexMatch)
        fullDistance = boundingBoxSize[maxIndex]
        
        """ get some measurements """
        distanceToSubtract = distance.returnDistanceBetweenObjects(locOrder[0],locOrder[1])
        if distanceCombineMode == 'subtract':
            returnDistance = fullDistance - distanceToSubtract
        else:
            returnDistance = fullDistance + distanceToSubtract
        
        mc.delete(measureLoc)
        mc.delete(cgmLoc)
        
        return returnDistance
    
    def getGeneratedCoreNames(self):
        """ 
        Generate core names for a module and return them
        
        RETURNS:
        generatedNames(list)
        """
        guiFactory.report("Generating core names via ModuleFactory - '%s'"%self.ModuleNull.nameBase)
        
        ### check the settings first ###
        partType = self.afModuleType.value
        settingsCoreNames = modules.returncgmTemplateCoreNames(partType)
        handles = self.optionHandles.value
        partName = NameFactory.returnRawGeneratedName(self.ModuleNull.nameShort,ignore=['cgmType','cgmTypeModifier'])
        
        ### if there are no names settings, genearate them from name of the limb module###
        generatedNames = []
        if settingsCoreNames == False:   
            cnt = 1
            for handle in range(handles):
                generatedNames.append('%s%s%i' % (partName,'_',cnt))
                cnt+=1
        
        elif (len(corePositionList)) > (len(settingsCoreNames)):
            ### Otherwise we need to make sure that there are enough core names for handles ###       
            cntNeeded = (len(corePositionList) - len(settingsCoreNames) +1)
            nonSplitEnd = settingsCoreNames[len(settingsCoreNames)-2:]
            toIterate = settingsCoreNames[1]
            iterated = []
            for i in range(cntNeeded):
                iterated.append('%s%s%i' % (toIterate,'_',(i+1)))
            generatedNames.append(settingsCoreNames[0])
            for name in iterated:
                generatedNames.append(name)
            for name in nonSplitEnd:
                generatedNames.append(name) 
                
        else:
            generatedNames = settingsCoreNames
            
        return generatedNames
    
    def returnOverrideColors(self):
        """ 
        Generate core names for a module and return them
        
        RETURNS:
        generatedNames(list)
        """
        direction = False
        if self.ModuleNull.cgm['cgmDirection']:
            direction = dictionary.validateStringDirection(self.ModuleNull.cgm['cgmDirection'])
        
        if not direction:
            return modules.returnSettingsData('colorCenter',True)
        else:
            return modules.returnSettingsData(('color'+direction.capitalize()),True)    
    #>>>>>>>>>>>>>>>s>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get States
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def getState(self):
        """ 
        Check module state ONLY from the state check attributes
        
        RETURNS:
        state(int) -- indexed to ModuleFactory.moduleStates
        """
        check = False
        for i,state in enumerate(moduleStates):
            buffer = self.__dict__["af%sState"%state.capitalize()].get()
            if buffer:
                check = True
                if i == len(moduleStates)-1:
                    return i+1
            elif check:
                return i
        return 0

    def setState(self,state,PuppetInstance):
        """ 
        Set a module's state
        
        RETURNS:
        generatedNames(list)
        """
        currentState = self.getState()
        if state is 0:
            guiFactory.report("This should set '%s' to 'define' state"%(self.ModuleNull.nameBase))

        elif state is 1:#Template
            guiFactory.report("This should set '%s' to '%s' state"%(self.ModuleNull.nameBase,moduleStates[state-1]))
            
            if state is currentState:
                guiFactory.report("'%s' is already at '%s' state"%(self.ModuleNull.nameBase,moduleStates[state-1]))
            else:
                self.doTemplate(PuppetInstance)
                
        elif state is 2:#Deform
            guiFactory.report("This should set '%s' to '%s' state"%(self.ModuleNull.nameBase,moduleStates[state-1]))
            
        elif state is 3:#Rig
            guiFactory.report("This should set '%s' to '%s' state"%(self.ModuleNull.nameBase,moduleStates[state-1]))
            
