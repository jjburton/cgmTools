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
from cgm.lib.classes.BufferFactory import *

from cgm.rigger.lib.Limb import template
reload(template)

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
                   'handles':3,
                   'rollJoints':3,
                   'bendy':True,
                   'stretchy':True,
                   'fk':True,
                   'ik':True}

#horiztonalLegDict = {'left':[3,templateSizeObjects[0],templateSizeObjects[1]],'right':[7,templateSizeObjects[0],templateSizeObjects[1]],'left_front':[3,templateSizeObjects[1],templateSizeObjects[0]], 'right_front':[7,templateSizeObjects[1],templateSizeObjects[0]], 'left_back':[3,templateSizeObjects[0],templateSizeObjects[1]],'right_back':[7,templateSizeObjects[0],templateSizeObjects[1]]}
horiztonalLegDict = {'left':3,'right':7,'left_front':3, 'right_front':7,'left_back':3,'right_back':7}
typeWorkingCurveDict = {'clavicle':'end','head':'end','arm':'end','leg':'start','tail':'start','wing':'end','finger':'end'}
typeAimingCurveDict = {'arm':'start','leg':'end','tail':'end','wing':'start',}
modeDict = {'finger':'parentDuplicate','foot':'footBase','head':'child','arm':'radialOut','leg':'radialDown','tail':'cvBack','wing':'radialOut','clavicle':'radialOut'}
aimSpreads = ['arm','leg','wing']

class Limb(ModuleFactory):
    """
    Limb class which inherits the ModuleFactory master class
    """
    def __init__(self,*a,**kw):
        initializeOnly = kw.pop('initializeOnly',False)
        self.handles = kw.pop('handles',3) or defaultSettings['handles']
        
        guiFactory.doPrintReportStart()
        
        #Initialize the standard module
        ModuleFactory.__init__(self,initializeOnly = initializeOnly,handles=self.handles,*a,**kw)
        
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
            
        self.afModuleType = AttrFactory(self.ModuleNull,'moduleType','string',value= self.partType,lock=True)
        
        if self.infoNulls['setupOptions']:
            self.SetupOptionsNull = ObjectFactory( self.infoNulls['setupOptions'].value )
            self.optionFK = AttrFactory(self.SetupOptionsNull,'fk','bool',initialValue= self.fk,lock=True)
            self.optionIK = AttrFactory(self.SetupOptionsNull,'ik','bool',initialValue= self.ik,lock=True)
            self.optionStretchy = AttrFactory(self.SetupOptionsNull,'stretchy','bool',initialValue= self.stretchy,lock=True)
            self.optionBendy = AttrFactory(self.SetupOptionsNull,'bendy','bool',initialValue= self.bendy,lock=True)
            
            self.optionRollJoints = AttrFactory(self.SetupOptionsNull,'rollJoints','int',initialValue=self.rollJoints,lock=True)
            self.optionStiffIndex= AttrFactory(self.SetupOptionsNull,'stiffIndex','int',initialValue=self.stiffIndex,lock=True)
            self.optionCurveDegree= AttrFactory(self.SetupOptionsNull,'curveDegree','int',initialValue=self.curveDegree,lock=True)
        else:
            guiFactory.warning("Setup options null is missing from '%s'. Rebuild"%self.ModuleNull.nameShort)
            return False
        if self.infoNulls['visibilityOptions']:
            self.VisibilityOptionsNull = ObjectFactory( self.infoNulls['visibilityOptions'].value )
            
            self.visOrientHelpers = AttrFactory(self.VisibilityOptionsNull,'visOrientHelpers','bool',initialValue=0,lock=True)
            self.visControlHelpers = AttrFactory(self.VisibilityOptionsNull,'visControlHelpers','bool',initialValue=0,lock=True)
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
        
        self.afModuleType = AttrFactory(self.ModuleNull,'moduleType',lock=True)
        
        if self.infoNulls['setupOptions']:
            self.SetupOptionsNull = ObjectFactory( self.infoNulls['setupOptions'].value )
            self.optionFK = AttrFactory(self.SetupOptionsNull,'fk',lock=True)
            self.optionIK = AttrFactory(self.SetupOptionsNull,'ik',lock=True)
            self.optionStretchy = AttrFactory(self.SetupOptionsNull,'stretchy',lock=True)
            self.optionBendy = AttrFactory(self.SetupOptionsNull,'bendy',lock=True)
            
            self.optionRollJoints = AttrFactory(self.SetupOptionsNull,'rollJoints',lock=True)
            self.optionStiffIndex= AttrFactory(self.SetupOptionsNull,'stiffIndex',lock=True)
            self.optionCurveDegree= AttrFactory(self.SetupOptionsNull,'curveDegree',lock=True)
            
        if self.infoNulls['visibilityOptions']:
            self.VisibilityOptionsNull = ObjectFactory( self.infoNulls['visibilityOptions'].value )
            self.visOrientHelpers = AttrFactory(self.VisibilityOptionsNull,'visOrientHelpers',lock=True)
            self.visControlHelpers = AttrFactory(self.VisibilityOptionsNull,'visControlHelpers',lock=True)
                    
        return True
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> Sizing
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def getInitialSize(self,PuppetInstance,*a,**kw):
        """
        Class specific sizer.
        
        Keyword arguments:
        PuppetInstance(instance) -- should be the module's puppet instance          
        """
        guiFactory.report("Sizing via Limb - '%s'"%self.ModuleNull.nameBase)
        
        #>>> If it's a root
        if not self.moduleParent:
            guiFactory.report("Root module mode!")            
            #>>>Get some info
            locInfoBuffer = ModuleFactory.doCreateStartingPositionLoc(self,'innerChild',PuppetInstance.templateSizeObjects['start'],PuppetInstance.templateSizeObjects['end'])
            print locInfoBuffer
            baseDistance = ModuleFactory.getPartBaseDistance(self,PuppetInstance,locInfoBuffer[0])
            print "buffer is '%s'"%baseDistance

            modulePosInfoBuffer = template.getGeneratedInitialPositionData(self, PuppetInstance,locInfoBuffer,baseDistance)
        
        
        if not modulePosInfoBuffer:
            guiFactory.warning("Failed to get a size return on '%s'"%m)
            return False
        
        #Store the necessary info back to the Puppet for children processes to have access to
        PuppetInstance.sizeCorePositionList[self.ModuleNull.nameBase] = modulePosInfoBuffer['positions']
        PuppetInstance.sizeLocInfo[self.ModuleNull.nameBase] = modulePosInfoBuffer['locator']
        
        return True
    
    
        try:pass################### Need to come back to do these...woot
        except:      
            if self.afModuleTyp.value in ['arm','wing','tail']:
                locInfoBuffer = ModuleFactory.doCreateStartingPositionLoc(self,'innerChild',PuppetInstance.templateSizeObjects['start'],PuppetInstance.templateSizeObjects['end'])
                PuppetInstance.locInfoDict[m] = createStartingPositionLoc(m,modeDict.get(self.afModuleTyp.value),typeWorkingCurveDict.get(self.afModuleTyp.value),typeAimingCurveDict.get(self.afModuleTyp.value),cvDict.get(directionKey))
                orderedModules.remove(m) 
                checkList.pop(m)
                
            elif self.afModuleTyp.value == 'clavicle':
                locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(self.afModuleTyp.value),templateSizeObjects[1],templateSizeObjects[0],cvDict.get(directionKey))
                orderedModules.remove(m) 
                checkList.pop(m)
            elif self.afModuleTyp.value == 'finger':
                moduleParent = attributes.returnMessageObject(m,'moduleParent')
                parentLoc = locInfo.get(moduleParent)
                locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(self.afModuleTyp.value),parentLoc)
                orderedModules.remove(m) 
            elif self.afModuleTyp.value == 'foot':
                moduleParent = attributes.returnMessageObject(m,'moduleParent')
                parentLoc = locInfo.get(moduleParent)
                locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(self.afModuleTyp.value),parentLoc)
                orderedModules.remove(m) 
                checkList.pop(m)
            elif self.afModuleTyp.value == 'head':
                locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(self.afModuleTyp.value),templateSizeObjects[1],templateSizeObjects[0],cvDict.get(directionKey))
                orderedModules.remove(m) 
                checkList.pop(m)
            elif self.afModuleTyp.value == 'leg':
                if basicOrientation == 'vertical':
                    locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(self.afModuleTyp.value),typeWorkingCurveDict.get(self.afModuleTyp.value),typeAimingCurveDict.get(self.afModuleTyp.value),cvDict.get(directionKey))
                else:
                    horizontalLegInfoBuffer = horiztonalLegDict.get(directionKey)
                    locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(self.afModuleTyp.value),horizontalLegInfoBuffer[1],horizontalLegInfoBuffer[2],horizontalLegInfoBuffer[0])
        



    def doTemplate(self,PuppetInstance):       
        """
        
        """
        def makeLimbTemplate (self):
            #>>>Curve degree finder
            if self.optionCurveDegree.get() == 0:
                doCurveDegree = 1
            else:
                if len(corePositionList) <= 3:
                    doCurveDegree = 1
                else:
                    doCurveDegree = len(corePositionList) - 1
            
            returnList = []
            templObjNameList = []
            templHandleList = []
            
            moduleColors = modules.returnModuleColors(self.ModuleNull.nameShort)
            
            #>>>Scale stuff
            moduleParent = self.afModuleParent.get()
            
            if not moduleParent:
                length = (distance.returnDistanceBetweenPoints (corePositionList[0],corePositionList[-1]))
                size = length / self.optionHandles.get()
            else:
                #>>>>>>>>>>>>>>>>>>>>> NOT TOUCHED YET
                parentTemplatePosObjectsInfoNull = modules.returnInfoTypeNull(moduleParent,'templatePosObjects')
                parentTemplatePosObjectsInfoData = attributes.returnUserAttrsToDict (parentTemplatePosObjectsInfoNull)
                parentTemplateObjects = []
                for key in parentTemplatePosObjectsInfoData.keys():
                    if (mc.attributeQuery (key,node=parentTemplatePosObjectsInfoNull,msg=True)) == True:
                        if search.returnTagInfo((parentTemplatePosObjectsInfoData[key]),'cgmType') != 'templateCurve':
                            parentTemplateObjects.append (parentTemplatePosObjectsInfoData[key])
                createBuffer = curves.createControlCurve('sphere',1)
                pos = corePositionList[0]
                mc.move (pos[0], pos[1], pos[2], createBuffer, a=True)
                closestParentObject = distance.returnClosestObject(createBuffer,parentTemplateObjects)
                boundingBoxSize = distance.returnBoundingBoxSize (closestParentObject)
                maxSize = max(boundingBoxSize)
                size = maxSize *.25
                mc.delete(createBuffer)
                if partType == 'clavicle':
                    size = size * .5
                elif partType == 'head':
                    size = size * .75
                if (search.returnTagInfo(moduleParent,'cgmModuleType')) == 'clavicle':
                    size = size * 2
        
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # Making the template objects
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            self.TemplateObject = {}
            
            self.templatePosObjectsBuffer = BufferFactory(self.infoNulls['templatePosObjects'].get())
            self.templatePosObjectsBuffer.purge()
            
            for cnt,pos in enumerate(corePositionList):
                #Size multiplier based on PuppetMode, make it take into account module mode eventually
                if PuppetInstance.optionPuppetMode.get() == 0:
                    if cnt == 0:
                        sizeMultiplier = 1
                    elif cnt == len(corePositionList) -1:
                        sizeMultiplier = .8
                    else:
                        sizeMultiplier = .5
                else:
                    sizeMultiplier = 1
                    
                #make a sphere and move it
                createBuffer = curves.createControlCurve('sphere',(size * sizeMultiplier))
                self.TemplateObject[cnt] = ObjectFactory(createBuffer) # Instance the control to our module
                obj = self.TemplateObject[cnt]
                curves.setCurveColorByName(obj.nameLong,moduleColors[0])
                obj.store('cgmName',coreNames[cnt])
                
                obj.getNameTagsFromObject(self.ModuleNull.nameLong,['cgmName','cgmType'])

                obj.store('cgmType','templateObject')
                obj.doName()
                mc.move (pos[0], pos[1], pos[2], [obj.nameLong], a=True)
                            
                #adds it to the list
                templObjNameList.append (obj.nameLong)
                templHandleList.append (obj.nameLong)  
                self.templatePosObjectsBuffer.store(obj.nameLong)
            
            
            # Makes our curve    
            crvName = mc.curve (d=doCurveDegree, p = corePositionList , os=True, n=('%s_%s' %(partName,(typesDictionary.get('templateCurve')))))            
            self.afTemplateCurve = AttrFactory(self.infoNulls['templatePosObjects'].get(), 'curve','message', value=crvName)
            
            curve = ObjectFactory(crvName)
            curve.getNameTagsFromObject(self.ModuleNull.nameLong,['cgmType'])

            attributes.storeInfo(crvName,'cgmType','templateCurve')
            curves.setCurveColorByName(crvName,moduleColors[1])
            curveLocs = []
            return
            for cnt,obj in enumerate(templObjNameList):
                pointLoc = locators.locMeObject(obj)
                loc = ObjectFactory(pointLoc)
                loc.store('cgmName',templObjNameList[cnt])
                loc.getNameTagsFromObject(obj,['cgmType'])
                mc.setAttr ((loc.nameShort+'.visibility'),0)
                mc.parentConstraint ([obj],[loc.nameShort],mo=False)
                mc.connectAttr ( (loc.nameShort+'.translate') , ('%s.controlPoints[%i]' % (crvName, cnt)), f=True )
                curveLocs.append (pointLoc)
            
            #>>> Direction and size Stuff
            
            # Directional data derived from joints 
            generalDirection = logic.returnHorizontalOrVertical(templObjNameList)
            if generalDirection == 'vertical' and 'leg' not in self.afModuleType.get():
                worldUpVector = [0,0,-1]
            elif generalDirection == 'vertical' and 'leg' in self.afModuleType.get():
                worldUpVector = [0,0,1]
            else:
                worldUpVector = [0,1,0]
            
            # Create root control
            templateNull = self.afTemplateNull.get()
            
            rootSize = (distance.returnBoundingBoxSizeToAverage(templObjNameList[0])*1.5)
            rootCtrl = ObjectFactory(curves.createControlCurve('cube',rootSize))
            rootCtrl.getNameTagsFromObject(self.ModuleNull.nameLong)
            self.msgTemplateRoot = AttrFactory(self.infoNulls['templatePosObjects'].get(), 'root', 'message', value = rootCtrl.nameLong)
            curves.setCurveColorByName(rootCtrl.nameLong,moduleColors[0])
            
            if self.afModuleType.get() == 'clavicle':
                position.movePointSnap(rootCtrl.nameLong,templObjNameList[0])
            else:
                position.movePointSnap(rootCtrl.nameLong,templObjNameList[0])
                
            constBuffer = mc.aimConstraint(templObjNameList[-1],rootCtrl.nameLong,maintainOffset = False, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpVector = worldUpVector, worldUpType = 'vector' )
            mc.delete (constBuffer[0])
            rootCtrl.store('cgmType','templateRoot')
            
            #>>>>>>>>>>>>>>>>>>>>>>> add tag copying
            
            rootCtrl.doName()
            
            rootGroup = rootCtrl.doGroup()
            rootGroup = rigging.doParentReturnName(rootGroup,templateNull)
            
            templObjNameList.append (crvName)
            templObjNameList += curveLocs
            
            return
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #>> Orientation helpers
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
            # Make our Orientation Helpers 
            orientHelpersReturn = template.addOrientationHelpers(self)
            masterOrient = orientHelpersReturn[0]
            orientObjects = orientHelpersReturn[1]
            
            
        
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #>> Control helpers
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
            print orientObjects
            print self.ModuleNull.nameShort
            print (templateNull+'.visControlHelpers')
            controlHelpersReturn = addControlHelpers(orientObjects,self.ModuleNull.nameShort,(templateNull+'.visControlHelpers'))
    
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #>> Input the saved values if there are any
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
            # Orientation Helpers 
            rotBuffer = coreRotationList[-1]
            #actualName = mc.spaceLocator (n= wantedName)
            rotCheck = sum(rotBuffer)
            if rotCheck != 0:
                mc.rotate(rotBuffer[0],rotBuffer[1],rotBuffer[2],masterOrient,os=True)
            
            cnt = 0
            for obj in orientObjects:
                rotBuffer = coreRotationList[cnt]
                rotCheck = sum(rotBuffer)
                if rotCheck != 0:
                    mc.rotate(rotBuffer[0],rotBuffer[1],rotBuffer[2],obj,os=True)
                cnt +=1 
                    
            # Control Helpers 
            controlHelpers = controlHelpersReturn[0]
            cnt = 0
            for obj in controlHelpers:
                posBuffer = controlPositionList[cnt]
                posCheck = sum(posBuffer)
                if posCheck != 0:
                    mc.xform(obj,t=[posBuffer[0],posBuffer[1],posBuffer[2]],ws=True)
                
                rotBuffer = controlRotationList[cnt]
                rotCheck = sum(rotBuffer)
                if rotCheck != 0:
                    mc.rotate(rotBuffer[0],rotBuffer[1],rotBuffer[2],obj,ws=True)
                
                scaleBuffer = controlScaleList[cnt]
                scaleCheck = sum(scaleBuffer)
                if scaleCheck != 0:
                    mc.scale(scaleBuffer[0],scaleBuffer[1],scaleBuffer[2],obj,absolute=True)
                cnt +=1 
            
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #>> Final stuff
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
            returnList.append(templObjNameList)
            returnList.append(templHandleList)
            returnList.append(rootCtrl)
            return returnList	



        # Start objects stuff 
        partName = NameFactory.returnRawGeneratedName(self.ModuleNull.nameShort,ignore=['cgmType','cgmTypeModifier'])
        templateStarterDataInfoNull = self.infoNulls['templateStarterData'].value
        initialObjectsPosData = mc.listAttr(templateStarterDataInfoNull,userDefined=True)
        corePositionList = []
        coreRotationList = []
        corePositionDict = {}
        coreRotationDict = {}        
        for a in initialObjectsPosData:
            buffer = attributes.doGetAttr(templateStarterDataInfoNull,a)                            
            if 'cgm' not in a and type(buffer) is list:
                if 'pos' in a:
                    split = a.split('pos_')
                    corePositionDict[int(split[1])] =  buffer[0]
                    corePositionList.append(buffer[0])
                elif 'rot' in a:
                    split = a.split('rot_')
                    coreRotationDict[int(split[1])] =  buffer[0] 
                    coreRotationList.append(buffer[0])
   
        print corePositionList
        print coreRotationList
        
        # template control objects stuff #
        templateControlObjectsDataNull = self.infoNulls['templateControlObjects'].value
        templateControlObjectsData = mc.listAttr(templateControlObjectsDataNull,userDefined=True)
        controlPositionList = []
        controlRotationList = []
        controlScaleList = []
        controlPositionDict = {}
        controlRotationDict = {}
        controlScaleDict = {}
        
        for a in templateControlObjectsData:
            buffer = attributes.doGetAttr(templateControlObjectsDataNull,a)                            
            if 'cgm' not in a and type(buffer) is list:
                if 'pos' in a:
                    split = a.split('pos_')
                    controlPositionDict[int(split[1])] =  buffer[0] 
                    controlPositionList.append(buffer[0])                    
                elif 'rot' in a:
                    split = a.split('rot_')
                    controlRotationDict[int(split[1])] =  buffer[0] 
                    controlRotationList.append(buffer[0])
                elif 'scale' in a:
                    split = a.split('scale_')
                    controlScaleDict[int(split[1])] =  buffer[0]   
                    controlScaleList.append(buffer[0])
                    
                  
        print controlPositionList
        print controlRotationList
        print controlScaleList
        
        # Names Info #
        coreNamesInfoNull = self.infoNulls['coreNames'].value
        coreNamesBuffer = mc.listAttr(coreNamesInfoNull,userDefined=True)
        coreNames = {}
        for a in coreNamesBuffer:
            if 'cgm' not in a and 'name_' in a:
                split = a.split('name_')
                coreNames[int(split[1])] =  attributes.doGetAttr(coreNamesInfoNull,a) 
                
        print coreNames    
        divider = NameFactory.returnCGMDivider()
        
        print ('%s%s'% (self.ModuleNull.nameShort,' data aquired...'))
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        #>> make template objects
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        #makes template objects#
        templateObjects = makeLimbTemplate(self)
        print 'Template Limb made....'
        
        return
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        #>> Parent objects
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        for obj in templateObjects[0]:    
            obj =  rigging.doParentReturnName(obj,templateNull) 
    
        print 'Template objects parented'
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        #>> Transform groups and Handles...handling
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        root = modules.returnInfoNullObjects(self.ModuleNull.nameShort,'templatePosObjects',types='templateRoot')
        
        handles = templateObjects[1]
        #>>> Break up the handles into the sets we need 
        if stiffIndex == 0:
            splitHandles = False
            handlesToSplit = handles
            handlesRemaining = [handles[0],handles[-1]]
        elif stiffIndex < 0:
            splitHandles = True
            handlesToSplit = handles[:stiffIndex]
            handlesRemaining = handles[stiffIndex:]
            handlesRemaining.append(handles[0])
        elif stiffIndex > 0:
            splitHandles = True
            handlesToSplit = handles[stiffIndex:]
            handlesRemaining = handles[:stiffIndex]
            handlesRemaining.append(handles[-1])
        
        # makes our mid transform groups#
        if len(handlesToSplit)>2:
            constraintGroups = constraints.doLimbSegmentListParentConstraint(handlesToSplit)
            print 'Constraint groups created...'
            
            for group in constraintGroups:
                mc.parent(group,root[0])
            
        # zero out the first and last#
        for handle in [handles[0],handles[-1]]:
            groupBuffer = (rigging.groupMeObject(handle,maintainParent=True))
            mc.parent(groupBuffer,root[0])
            
        #>>> Break up the handles into the sets we need 
        if stiffIndex < 0:
            for handle in handles[(stiffIndex+-1):-1]:
                groupBuffer = (rigging.groupMeObject(handle,maintainParent=True))
                mc.parent(groupBuffer,handles[-1])
        elif stiffIndex > 0:
            for handle in handles[1:(stiffIndex+1)]:
                groupBuffer = (rigging.groupMeObject(handle,maintainParent=True))
                mc.parent(groupBuffer,handles[0])
                
        print 'Constraint groups parented...'
        
        rootName = NameFactory.doNameObject(root[0])
        
        for obj in handles:
            attributes.doSetLockHideKeyableAttr(obj,True,False,False,['sx','sy','sz','v'])
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Parenting constrainging parts
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        moduleParent = attributes.returnMessageObject(self.ModuleNull.nameShort,'moduleParent')
        if moduleParent != PuppetInstance.PuppetNull.nameShort:
            if (search.returnTagInfo(moduleParent,'cgmModuleType')) == 'clavicle':
                moduleParent = attributes.returnMessageObject(moduleParent,'moduleParent')
            parentTemplatePosObjectsInfoNull = modules.returnInfoTypeNull(moduleParent,'templatePosObjects')
            parentTemplatePosObjectsInfoData = attributes.returnUserAttrsToDict (parentTemplatePosObjectsInfoNull)
            parentTemplateObjects = []
            for key in parentTemplatePosObjectsInfoData.keys():
                if (mc.attributeQuery (key,node=parentTemplatePosObjectsInfoNull,msg=True)) == True:
                    if search.returnTagInfo((parentTemplatePosObjectsInfoData[key]),'cgmType') != 'templateCurve':
                        parentTemplateObjects.append (parentTemplatePosObjectsInfoData[key])
            closestParentObject = distance.returnClosestObject(rootName,parentTemplateObjects)
            if (search.returnTagInfo(self.ModuleNull.nameShort,'cgmModuleType')) != 'foot':
                constraintGroup = rigging.groupMeObject(rootName,maintainParent=True)
                constraintGroup = NameFactory.doNameObject(constraintGroup)
                mc.pointConstraint(closestParentObject,constraintGroup, maintainOffset=True)
                mc.scaleConstraint(closestParentObject,constraintGroup, maintainOffset=True)
            else:
                constraintGroup = rigging.groupMeObject(closestParentObject,maintainParent=True)
                constraintGroup = NameFactory.doNameObject(constraintGroup)
                mc.parentConstraint(rootName,constraintGroup, maintainOffset=True)
                
        # grab the last clavicle piece if the arm has one and connect it to the arm  #
        moduleParent = attributes.returnMessageObject(self.ModuleNull.nameShort,'moduleParent')
        if moduleParent != PuppetInstance.PuppetNull.nameShort:
            if (search.returnTagInfo(self.ModuleNull.nameShort,'cgmModuleType')) == 'arm':
                if (search.returnTagInfo(moduleParent,'cgmModuleType')) == 'clavicle':
                    print '>>>>>>>>>>>>>>>>>>>>> YOU FOUND ME'
                    parentTemplatePosObjectsInfoNull = modules.returnInfoTypeNull(moduleParent,'templatePosObjects')
                    parentTemplatePosObjectsInfoData = attributes.returnUserAttrsToDict (parentTemplatePosObjectsInfoNull)
                    parentTemplateObjects = []
                    for key in parentTemplatePosObjectsInfoData.keys():
                        if (mc.attributeQuery (key,node=parentTemplatePosObjectsInfoNull,msg=True)) == True:
                            if search.returnTagInfo((parentTemplatePosObjectsInfoData[key]),'cgmType') != 'templateCurve':
                                parentTemplateObjects.append (parentTemplatePosObjectsInfoData[key])
                    closestParentObject = distance.returnClosestObject(rootName,parentTemplateObjects)
                    endConstraintGroup = rigging.groupMeObject(closestParentObject,maintainParent=True)
                    endConstraintGroup = NameFactory.doNameObject(endConstraintGroup)
                    mc.pointConstraint(handles[0],endConstraintGroup, maintainOffset=True)
                    mc.scaleConstraint(handles[0],endConstraintGroup, maintainOffset=True)
            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        #>> Final stuff
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        
        
        #>>> Set our new module rig process state
        mc.setAttr ((self.ModuleNull.nameShort+'.templateState'), 1)
        mc.setAttr ((self.ModuleNull.nameShort+'.skeletonState'), 0)
        print ('%s%s'% (self.ModuleNull.nameShort,' done'))
        
        #>>> Tag our objects for easy deletion
        children = mc.listRelatives (templateNull, allDescendents = True,type='transform')
        for obj in children:
            attributes.storeInfo(obj,'cgmOwnedBy',templateNull)
            
        #>>> Visibility Connection
        masterControl = attributes.returnMessageObject(PuppetInstance.PuppetNull.nameShort,'controlMaster')
        visControl = attributes.returnMessageObject(masterControl,'childControlVisibility')
        attributes.doConnectAttr((visControl+'.orientHelpers'),(templateNull+'.visOrientHelpers'))
        attributes.doConnectAttr((visControl+'.controlHelpers'),(templateNull+'.visControlHelpers'))
        #>>> Run a rename on the module to make sure everything is named properly
        #NameFactory.doRenameHeir(self.ModuleNull.nameShort)    











































        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Define Subclasses
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      
class Segment(Limb):
    def __init__(self, moduleName = 'segment',*a, **kw):
        moduleParent = kw.pop('moduleParent',False)
        self.handles = kw.pop('handles',3)
        position = kw.pop('position',False)
        nameModifier = kw.pop('nameModifier',False)
        direction = kw.pop('direction',False)
        directionModifier = kw.pop('directionModifier',False)
        initializeOnly = kw.pop('initializeOnly',False)

        self.partType = 'segment'
        self.stiffIndex = 0
        self.curveDegree = 1
        self.rollJoints = 3        
        
        Limb.__init__(self,moduleName,initializeOnly = initializeOnly,handles=self.handles ,*a, **kw)
        
class SegmentBak(Limb):
    def __init__(self, moduleName ='segment', moduleParent = False, handles = 3, position = False, direction = False, directionModifier = False, nameModifier = False,initializeOnly = False,*a, **kw):
        moduleName = kw.pop('moduleName','segment')

        self.partType = 'segment'
        self.stiffIndex = 0
        self.curveDegree = 1
        self.rollJoints = 3
        self.handles = handles
        
        
        Limb.__init__(self,moduleName,moduleParent,position,direction,directionModifier,nameModifier,initializeOnly, *a,**kw)
        
        