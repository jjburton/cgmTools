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

from cgm.lib import (search,
                     distance,
                     names,
                     attributes,
                     names,
                     rigging,
                     logic,
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

""" 1 """
class Limb:
    def __init__(self):
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Initial Checks
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        """ make sure no module with this name exists """
        modules = modules.returnSceneModules()
        moduleNamesInfo = []
        modulesDirectionInfo = []
        modulesModifierInfo = []
        moduleModuleTypesInfo = []
        
        """ get directional info from parent if there is any """
        parentDirection = search.returnTagInfo(self.moduleParent,'cgmDirection')
        if parentDirection != False:
            self.direction = parentDirection
        parentPosition = search.returnTagInfo(self.moduleParent,'cgmPosition')
        if parentPosition != False:
            self.position = parentPosition
        
        """ make sure there is a master null """
        masterNull = masterNullCheck()
        if masterNull == False:
            return 'Weve got a problem scotty'
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Variable setup
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>                
        """Setting the variables"""        
        templateDataToStore = ['fk', 'ik' , 'stretch', 'bend','rollJoints','stiffIndex','curveDegree']
        name = self.name
        self.fk = 0
        self.ik = 0
        self.stretch = 0
        self.bend = 0
        self.templateAttrs = {'fk' : 0, 'ik' : 0 , 'stretch' : 0, 'visOrientHelpers':1, 'visControlHelpers':1, 'bend' : 0, 'rollJoints' : self.rollJoints, 'handles' : self.handles, 'stiffIndex': self.stiffIndex,'curveDegree':self.curveDegree}
        self.templateAttrTypes = {'fk' : 'bool', 'ik' : 'bool' , 'stretch' : 'bool', 'visOrientHelpers':'bool','visControlHelpers':'bool', 'bend' : 'bool', 'rollJoints' : 'long', 'handles' : 'long', 'stiffIndex':'long','curveDegree':'long'}
        cnt = 0     
                        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Nulls creation
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        """ Create our module null"""
        createBuffer = mc.group (empty=True)
        attributes.storeInfo(createBuffer,'cgmName',self.name)
        if self.nameModifier != 'None':
            attributes.storeInfo(createBuffer,'cgmNameModifier',self.nameModifier)
            
        if parentDirection != False:
            attributes.storeInfo(createBuffer,'cgmDirection',(self.moduleParent+'.cgmDirection'))
        elif self.direction != 'None':
            attributes.storeInfo(createBuffer,'cgmDirection',self.direction)
            
        if parentPosition != False:
            attributes.storeInfo(createBuffer,'cgmPosition',(self.moduleParent+'.cgmPosition'))
        elif self.position != 'None':
            attributes.storeInfo(createBuffer,'cgmPosition',self.position,True)
            
        attributes.storeInfo(createBuffer,'cgmType','module')
        attributes.storeInfo(createBuffer,'cgmModuleType',self.partType)
        
        """ make sure name is unique """
        rawModuleName = NameFactory.returnObjectGeneratedNameDict(createBuffer)
        cnt = 0
        for module in modules:
            if NameFactory.returnObjectGeneratedNameDict(module,'cgmNameModifier') ==  rawModuleName:
                cnt +=1
                print 'yes'
        if cnt > 0:
            attributes.storeInfo(createBuffer,'cgmNameModifier',('%s%i' % ('extra',cnt)))
        moduleNull = NameFactory.doNameObject(createBuffer)

        mc.xform (moduleNull, os=True, piv= (0,0,0)) 
        self.moduleNull = moduleNull
        mc.addAttr (moduleNull, ln = 'templateState',  at ='long' )
        mc.setAttr ((moduleNull+'.templateState'), 0)
        mc.addAttr (moduleNull, ln = 'rigState',  at ='long' )
        mc.setAttr ((moduleNull+'.rigState'), 0)
        mc.addAttr (moduleNull, ln = 'skeletonState',  at ='long' )
        mc.setAttr ((moduleNull+'.skeletonState'), 0)
        
        #>>> Parent Module
        if self.moduleParent == None:
            attributes.storeInfo(moduleNull,'moduleParent',masterNull)
        else:
            attributes.storeInfo(moduleNull,'moduleParent',self.moduleParent)
        
        
        """creates rig null"""
        createBuffer = mc.group (empty=True)
        attributes.storeInfo(createBuffer,'cgmType','rigNull')
        mc.xform (createBuffer, os=True, piv= (0,0,0)) 
        createBuffer = rigging.doParentReturnName(createBuffer,moduleNull)
        attributes.storeObjectToMessage (createBuffer, moduleNull, 'rigNull')
        rigNullName = NameFactory.doNameObject(createBuffer)
        
        #>>>TemplateNull stuff
        """creates template null"""
        createBuffer = mc.group (empty=True)
        attributes.storeInfo(createBuffer,'cgmType','templateNull')
        if self.direction != 'None':
            attributes.storeInfo(createBuffer,'cgmDirection',self.direction)
        if self.position != 'None':
            attributes.storeInfo(createBuffer,'cgmPosition',self.position,True)
        mc.xform (createBuffer, os=True, piv= (0,0,0)) 
        createBuffer = rigging.doParentReturnName(createBuffer,moduleNull)
        templateNullName = NameFactory.doNameObject(createBuffer)
        attributes.storeObjectToMessage (templateNullName, moduleNull, 'templateNull')
        
        """stores our variables"""   
        attributes.addAttributesToObj(templateNullName,self.templateAttrTypes)
        for attr in self.templateAttrs:
            mc.setAttr ((templateNullName+"."+attr) , self.templateAttrs.get(attr)) 
        
        #>>>Info Null stuff
        """ creates the master info"""
        moduleInfoNull = modules.createInfoNull('master')
        attributes.storeObjectToMessage (moduleInfoNull, moduleNull, 'info')
        moduleInfoNull = rigging.doParentReturnName(moduleInfoNull,moduleNull)
        
        #>>> pos template objects null
        """ creates the name info null"""
        templatePosObjectsInfoNull = modules.createInfoNull('templatePosObjects')
        attributes.storeObjectToMessage (templatePosObjectsInfoNull, moduleInfoNull, 'templatePosObjects')
        namesInfoNull=rigging.doParentReturnName(templatePosObjectsInfoNull,moduleInfoNull)

        #>>> control template objects null
        """ creates the name info null"""
        templateRotationObjectsInfoNull = modules.createInfoNull('templateControlObjects')
        attributes.storeObjectToMessage (templateRotationObjectsInfoNull, moduleInfoNull, 'templateControlObjects')
        namesInfoNull=rigging.doParentReturnName(templateRotationObjectsInfoNull,moduleInfoNull)

        #>>> Name null
        """ creates the name info null"""
        namesInfoNull = modules.createInfoNull('coreNames')
        attributes.storeObjectToMessage (namesInfoNull, moduleInfoNull, 'coreNames')
        namesInfoNull=rigging.doParentReturnName(namesInfoNull,moduleInfoNull)
                
        #>>> Initial positions
        """ Creates our template object initial data """
        starterObjectsInfoNull = modules.createInfoNull('templateStarterData')
        attributes.storeObjectToMessage (starterObjectsInfoNull, moduleInfoNull, 'templateStarterData')
        starterObjectsInfoNull=rigging.doParentReturnName(starterObjectsInfoNull,moduleInfoNull)

        #>>> Template control objects save data
        """ Creates our template object initial data """
        templateControlObjectsDataNull = modules.createInfoNull('templateControlObjectsData')
        attributes.storeObjectToMessage (templateControlObjectsDataNull, moduleInfoNull, 'templateControlObjectsData')
        templateControlObjectsDataNull=rigging.doParentReturnName(templateControlObjectsDataNull,moduleInfoNull)
        
        #>>> Joints infoNull
        """ creates the name info null"""
        jointInfoNull = modules.createInfoNull('skinJoints')
        attributes.storeObjectToMessage (jointInfoNull, moduleInfoNull, 'skinJoints')
        sizeInfoNull=rigging.doParentReturnName(jointInfoNull,moduleInfoNull)
        
        #>>> Rotation Order infoNull
        """ creates the name info null"""
        rotateOrderInfoNull = modules.createInfoNull('rotateOrder')
        attributes.storeObjectToMessage (rotateOrderInfoNull, moduleInfoNull, 'rotateOrderInfo')
        rotateOrderInfoNull = rigging.doParentReturnName(rotateOrderInfoNull,moduleInfoNull)
        
        #>>> Checks naming
        NameFactory.doRenameHeir(moduleNull)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Subclasses
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class Finger(Limb):
    def __init__(self, moduleParent = None, name ='Finger', handles = 5, position = 'None', direction = 'None', nameModifier = 'None'):
        self.partType = 'finger'
        self.stiffIndex = 1
        self.curveDegree = 0
        self.rollJoints = 0
        self.direction = direction
        self.position = position
        self.nameModifier = nameModifier
        self.moduleParent = moduleParent
        self.handles = handles
        self.name = name
        
        
        Limb.__init__(self)
        

class Segment(Limb):
    def __init__(self, moduleParent = None, name ='segment', handles = 3, position = 'None', direction = 'None', nameModifier = 'None'):
        self.partType = 'segment'
        self.stiffIndex = 0
        self.curveDegree = 1
        self.rollJoints = 3
        self.direction = direction
        self.position = position
        self.nameModifier = nameModifier
        self.moduleParent = moduleParent
        self.handles = handles
        self.name = name
        
        
        Limb.__init__(self)

class Clavicle(Limb):
    def __init__(self,moduleParent = None, name = 'clavicle', position = 'None', direction = 'None', nameModifier = 'None' ):
        self.partType = 'clavicle'
        self.stiffIndex = 0
        self.curveDegree = 0
        self.direction = direction
        self.position = position
        self.nameModifier = nameModifier
        self.rollJoints = 0
        self.handles = 1
        self.moduleParent = moduleParent
        self.name = name

            
        Limb.__init__(self)  


class Arm(Limb):
    def __init__(self,moduleParent = None, name = 'arm', position = 'None', direction = 'None', nameModifier = 'None' ):
        self.partType = 'arm'
        self.stiffIndex = 0
        self.curveDegree = 0
        self.direction = direction
        self.position = position
        self.nameModifier = nameModifier
        self.rollJoints = 3
        self.handles = 3
        self.moduleParent = moduleParent
        self.name = name
        
            
        Limb.__init__(self)      
            
class Leg(Limb):
    def __init__(self, moduleParent = None, name = 'leg', position = 'None', direction = 'None', nameModifier = 'None' ):
        self.partType = 'leg'
        self.stiffIndex = 0
        self.curveDegree = 0
        self.direction = direction
        self.position = position
        self.nameModifier = nameModifier
        self.rollJoints = 3
        self.handles = 3
        self.moduleParent = moduleParent
        self.name = name
              
        Limb.__init__(self)
        
class Tail(Limb):
    def __init__(self, moduleParent = None, handles = 5, name = 'tail', position = 'None', direction = 'None', nameModifier = 'None' ):
        self.partType = 'tail'
        self.stiffIndex = 0
        self.curveDegree = 1
        self.direction = direction
        self.position = position
        self.nameModifier = nameModifier
        self.rollJoints = 3
        self.handles = handles
        self.moduleParent = moduleParent
        self.name = name

            
        Limb.__init__(self)        
        
class Torso(Limb):
    def __init__(self, moduleParent = None, handles = 4, name = 'spine', position = 'None', direction = 'None', nameModifier = 'None' ):
        self.partType = 'torso'
        self.stiffIndex = -1
        self.curveDegree = 1
        self.direction = direction
        self.position = position
        self.nameModifier = nameModifier
        self.rollJoints = 2
        self.handles = handles
        self.moduleParent = moduleParent
        self.name = name

            
        Limb.__init__(self)

class Head(Limb):
    def __init__(self, moduleParent = False, handles = 4, name = 'head', position = 'None', direction = 'None', nameModifier = 'None' ):
        self.partType = 'head'
        self.stiffIndex = -1
        self.curveDegree = 0
        self.direction = direction
        self.position = position
        self.nameModifier = nameModifier
        self.rollJoints = 3
        self.handles = handles
        self.moduleParent = moduleParent
        self.name = name
        
        
        Limb.__init__(self)
        
class Foot(Limb):
    def __init__(self, moduleParent = None, handles = 3, name = 'foot', position = 'None', direction = 'None', nameModifier = 'None' ):
        self.partType = 'foot'
        self.stiffIndex = 0
        self.curveDegree = 0
        self.direction = direction
        self.position = position
        self.nameModifier = nameModifier
        self.rollJoints = 0
        self.handles = handles
        self.moduleParent = moduleParent
        self.name = name

            
        Limb.__init__(self)  
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# TemplateMaker
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
def doTemplate(masterNull, moduleNull):
    def makeLimbTemplate (moduleNull):  
        #>>>Curve degree finder
        if curveDegree == 0:
            doCurveDegree = 1
        else:
            if len(corePositionList) <= 3:
                doCurveDegree = 1
            else:
                doCurveDegree = len(corePositionList) - 1
        
        returnList = []
        templObjNameList = []
        templHandleList = []
        
        moduleColors = modules.returnModuleColors(moduleNull)
        
        #>>>Scale stuff
        moduleParent = attributes.returnMessageObject(moduleNull,'moduleParent')
        if moduleParent == masterNull:
            length = (distance.returnDistanceBetweenPoints (corePositionList[0],corePositionList[-1]))
            size = length / len(coreNamesAttrs)
        else:
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
            
        cnt = 0
        lastCountSizeMatch = len(corePositionList) -1
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Making the template objects
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        for pos in corePositionList:
            if cnt == 0:
                sizeMultiplier = 1
            elif cnt == lastCountSizeMatch:
                sizeMultiplier = .8
            else:
                sizeMultiplier = .5
            """make a sphere and move it"""
            createBuffer = curves.createControlCurve('sphere',(size * sizeMultiplier))
            curves.setCurveColorByName(createBuffer,moduleColors[0])
            attributes.storeInfo(createBuffer,'cgmName',coreNamesAttrs[cnt])
            if direction != None:
                attributes.storeInfo(createBuffer,'cgmDirection',direction)
            attributes.storeInfo(createBuffer,'cgmType','templateObject')
            tmpObjName = NameFactory.doNameObject(createBuffer)
            mc.move (pos[0], pos[1], pos[2], [tmpObjName], a=True)
                        
            """adds it to the list"""
            templObjNameList.append (tmpObjName)
            templHandleList.append (tmpObjName)  
            """ replaces the message node locator objects with the new template ones """  
            attributes.storeObjectToMessage (tmpObjName, templatePosObjectsInfoNull, NameFactory.returnUniqueGeneratedName(tmpObjName,ignore='cgmType'))  
            
            cnt +=1

        """Makes our curve"""    
        crvName = mc.curve (d=doCurveDegree, p = corePositionList , os=True, n=('%s%s%s' %(partName,'_',(typesDictionary.get('templateCurve')))))            
        if direction != None:
                attributes.storeInfo(crvName,'cgmDirection',direction)
        attributes.storeInfo(crvName,'cgmType','templateCurve')
        curves.setCurveColorByName(crvName,moduleColors[1])
        curveLocs = []
        
        cnt = 0
        for obj in templObjNameList:
            pointLoc = locators.locMeObject (obj)
            attributes.storeInfo(pointLoc,'cgmName',templObjNameList[cnt])
            if direction != None:
                attributes.storeInfo(pointLoc,'cgmDirection',direction)
            mc.setAttr ((pointLoc+'.visibility'),0)
            mc.parentConstraint ([obj],[pointLoc],mo=False)
            mc.connectAttr ( (pointLoc+'.translate') , ('%s%s%i%s' % (crvName, '.controlPoints[', cnt, ']')), f=True )
            curveLocs.append (pointLoc)
            cnt+=1
        
        #>>> Direction and size Stuff
        
        """ Directional data derived from joints """
        generalDirection = locators.returnHorizontalOrVertical(templObjNameList)
        if generalDirection == 'vertical' and 'leg' not in partType:
            worldUpVector = [0,0,-1]
        elif generalDirection == 'vertical' and 'leg' in partType:
            worldUpVector = [0,0,1]
        else:
            worldUpVector = [0,1,0]
        
        """ Create root control"""
        moduleNullData = attributes.returnUserAttrsToDict(moduleNull)
        templateNull = moduleNullData.get('templateNull')
        
        rootSize = (distance.returnBoundingBoxSizeToAverage(templObjNameList[0])*1.5)
        createBuffer = curves.createControlCurve('cube',rootSize)
        curves.setCurveColorByName(createBuffer,moduleColors[0])
        
        if partType == 'clavicle' or partType == 'clavicle':
            position.movePointSnap(createBuffer,templObjNameList[0])
        else:
            position.movePointSnap(createBuffer,templObjNameList[0])
        constBuffer = mc.aimConstraint(templObjNameList[-1],createBuffer,maintainOffset = False, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpVector = worldUpVector, worldUpType = 'vector' )
        mc.delete (constBuffer[0])
        attributes.storeInfo(createBuffer,'cgmType','templateRoot')
        if direction != None:
            attributes.storeInfo(createBuffer,'cgmDirection',direction)
        rootCtrl = NameFactory.doNameObject(createBuffer)
        
        rootGroup = rigging.groupMeObject(rootCtrl)
        rootGroup = rigging.doParentReturnName(rootGroup,templateNull)
        
        templObjNameList.append (crvName)
        templObjNameList += curveLocs
        
        """ replaces the message node locator objects with the new template ones """                          
        attributes.storeObjectToMessage (crvName, templatePosObjectsInfoNull, 'curve')
        attributes.storeObjectToMessage (rootCtrl, templatePosObjectsInfoNull, 'root')  
        
        """Get our modules group, parents our part null there and connects it to the info null"""
        modulesGroup = attributes.returnMessageObject(masterNull,'modulesGroup')
        modulesInfoNull = modules.returnInfoTypeNull(masterNull,'modules')
        
        attributes.storeObjectToMessage (moduleNull, modulesInfoNull, (NameFactory.returnUniqueGeneratedName(moduleNull,ignore='cgmType')))
        
        """ parenting of the modules group if necessary"""
        moduleNullBuffer = rigging.doParentReturnName(moduleNull,modulesGroup)
        if moduleNullBuffer == False:
            moduleNull = moduleNull
        else:
            moduleNull = moduleNullBuffer

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        #>> Orientation helpers
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        """ Make our Orientation Helpers """
        orientHelpersReturn = addOrientationHelpers(templHandleList,rootCtrl,moduleNull,partType,(templateNull+'.visOrientHelpers'))
        masterOrient = orientHelpersReturn[0]
        orientObjects = orientHelpersReturn[1]
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        #>> Control helpers
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        print orientObjects
        print moduleNull
        print (templateNull+'.visControlHelpers')
        controlHelpersReturn = addControlHelpers(orientObjects,moduleNull,(templateNull+'.visControlHelpers'))

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        #>> Input the saved values if there are any
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        """ Orientation Helpers """
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
                
        """ Control Helpers """
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
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # The actual meat of the limb template process
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> get colors

    #>>> Get our base info
    """ module null data """
    moduleNullData = attributes.returnUserAttrsToDict(moduleNull)

    """ part name """
    partName = NameFactory.returnUniqueGeneratedName(moduleNull, ignore = 'cgmType')
    partType = moduleNullData.get('cgmModuleType')
    direction = moduleNullData.get('cgmDirection')
    
    
    """ template null """
    templateNull = moduleNullData.get('templateNull')
    templateNullData = attributes.returnUserAttrsToDict(templateNull)
    curveDegree = templateNullData.get('curveDegree')
    stiffIndex = templateNullData.get('stiffIndex')
    
    """ template object nulls """
    templatePosObjectsInfoNull = modules.returnInfoTypeNull(moduleNull,'templatePosObjects')
    templateControlObjectsNull = modules.returnInfoTypeNull(moduleNull,'templateControlObjects')
    
    """ rig null """
    rigNull = moduleNullData.get('rigNull')
    
    
    """ Start objects stuff """
    templateStarterDataInfoNull = modules.returnInfoTypeNull(moduleNull,'templateStarterData')
    initialObjectsTemplateDataBuffer = attributes.returnUserAttrsToList(templateStarterDataInfoNull)
    initialObjectsPosData = lists.removeMatchedIndexEntries(initialObjectsTemplateDataBuffer,'cgm')
    corePositionList = []
    coreRotationList = []
    coreScaleList = []
    for set in initialObjectsPosData:
        if re.match('pos',set[0]):
            corePositionList.append(set[1])
        elif re.match('rot',set[0]):
            coreRotationList.append(set[1])
        elif re.match('scale',set[0]):
            coreScaleList.append(set[1])
    print corePositionList
    print coreRotationList
    print coreScaleList
    
    """ template control objects stuff """
    templateControlObjectsDataNull = modules.returnInfoTypeNull(moduleNull,'templateControlObjectsData')
    templateControlObjectsDataNullBuffer = attributes.returnUserAttrsToList(templateControlObjectsDataNull)
    templateControlObjectsData = lists.removeMatchedIndexEntries(templateControlObjectsDataNullBuffer,'cgm')
    controlPositionList = []
    controlRotationList = []
    controlScaleList = []
    print templateControlObjectsData
    for set in templateControlObjectsData:
        if re.match('pos',set[0]):
            controlPositionList.append(set[1])
        elif re.match('rot',set[0]):
            controlRotationList.append(set[1])
        elif re.match('scale',set[0]):
            controlScaleList.append(set[1])
    print controlPositionList
    print controlRotationList
    print controlScaleList

    
    """ Names Info """
    coreNamesInfoNull = modules.returnInfoTypeNull(moduleNull,'coreNames')
    coreNamesBuffer = attributes.returnUserAttrsToList(coreNamesInfoNull)
    coreNames = lists.removeMatchedIndexEntries(coreNamesBuffer,'cgm')
    coreNamesAttrs = []
    for set in coreNames:
        coreNamesAttrs.append(coreNamesInfoNull+'.'+set[0])
        
    
    divider = NameFactory.returnCGMDivider()
    
    print ('%s%s'% (moduleNull,' data aquired...'))
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> make template objects
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    """makes template objects"""
    templateObjects = makeLimbTemplate(moduleNull)
    print 'Template Limb made....'
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> Parent objects
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    for obj in templateObjects[0]:    
        obj =  rigging.doParentReturnName(obj,templateNull) 

    print 'Template objects parented'
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> Transform groups and Handles...handling
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    root = modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateRoot')
    
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
    
    """ makes our mid transform groups"""
    if len(handlesToSplit)>2:
        constraintGroups = constraints.doLimbSegmentListParentConstraint(handlesToSplit)
        print 'Constraint groups created...'
        
        for group in constraintGroups:
            mc.parent(group,root[0])
        
    """ zero out the first and last"""
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
    moduleParent = attributes.returnMessageObject(moduleNull,'moduleParent')
    if moduleParent != masterNull:
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
        if (search.returnTagInfo(moduleNull,'cgmModuleType')) != 'foot':
            constraintGroup = rigging.groupMeObject(rootName,maintainParent=True)
            constraintGroup = NameFactory.doNameObject(constraintGroup)
            mc.pointConstraint(closestParentObject,constraintGroup, maintainOffset=True)
            mc.scaleConstraint(closestParentObject,constraintGroup, maintainOffset=True)
        else:
            constraintGroup = rigging.groupMeObject(closestParentObject,maintainParent=True)
            constraintGroup = NameFactory.doNameObject(constraintGroup)
            mc.parentConstraint(rootName,constraintGroup, maintainOffset=True)
            
    """ grab the last clavicle piece if the arm has one and connect it to the arm  """
    moduleParent = attributes.returnMessageObject(moduleNull,'moduleParent')
    if moduleParent != masterNull:
        if (search.returnTagInfo(moduleNull,'cgmModuleType')) == 'arm':
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
    mc.setAttr ((moduleNull+'.templateState'), 1)
    mc.setAttr ((moduleNull+'.skeletonState'), 0)
    print ('%s%s'% (moduleNull,' done'))
    
    #>>> Tag our objects for easy deletion
    children = mc.listRelatives (templateNull, allDescendents = True,type='transform')
    for obj in children:
        attributes.storeInfo(obj,'cgmOwnedBy',templateNull)
        
    #>>> Visibility Connection
    masterControl = attributes.returnMessageObject(masterNull,'controlMaster')
    visControl = attributes.returnMessageObject(masterControl,'childControlVisibility')
    attributes.doConnectAttr((visControl+'.orientHelpers'),(templateNull+'.visOrientHelpers'))
    attributes.doConnectAttr((visControl+'.controlHelpers'),(templateNull+'.visControlHelpers'))
    #>>> Run a rename on the module to make sure everything is named properly
    #NameFactory.doRenameHeir(moduleNull)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def templatizeCharacter(masterNull):
    if mc.objExists(masterNull) == False:
        return 'No character exists'
        
    """ master stuff """
    masterControl = attributes.returnMessageObject(masterNull,'controlMaster')
    if masterControl == False or masterControl == None:
        controlBuilder.createMasterControlFromMasterNull(masterNull)
        masterControl = attributes.returnMessageObject(masterNull,'controlMaster')
    print masterControl
    visControl = attributes.returnMessageObject(masterControl,'childControlVisibility')
    print visControl
    attributes.addSectionBreakAttrToObj(visControl,'templateStuff')
    attributes.addBoolAttrToObject(visControl,'orientHelpers')
    attributes.addBoolAttrToObject(visControl,'controlHelpers')
    orderedModules = modules.returnOrderedModules(masterNull)
    for module in orderedModules:
        stateCheck = modules.moduleStateCheck(module,['template'])
        if stateCheck > 0:
            print ('%s%s' % (module,' has already been templatized. Moving on...'))
        else:
            doTemplate(masterNull, module)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>> Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def returnTemplateSizeObject(masterNull):
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
    templateSizeObject = attributes.returnMessageObject(masterNull,'templateSizeObject')
    if templateSizeObject != False:
        templateSizeObjects =[]
        templateSizeObjects.append(attributes.returnMessageObject(templateSizeObject,'controlBottom'))
        templateSizeObjects.append(attributes.returnMessageObject(templateSizeObject,'controlTop'))
        return templateSizeObjects
    else:
        return controlBuilder.createSizeTemplateControl(masterNull)

def masterNullCheck():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Makes sure we have a master null in scene. If there aren't any, it makes one. If there is
    it returns it, if there are too many it returns False
    
    ARGUMENTS:
    Nada
    
    RETURNS:
    masterNull(string) - success
    False - failure
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Check for a master node
    masterNulls = modules.returnMasterObjects()
    if len(masterNulls) == 0:
        return modules.createMasterNull()
    elif len(masterNulls) == 1:
        return masterNulls[0]
    elif len(masterNulls) > 1:
        print 'Too many masterNulls!'
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
# Template Control Special Objects   
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addOrientationHelpers(objects,root,moduleNull,moduleType,visAttr):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds orientation helpers to a template chain
    
    ARGUMENTS:
    objects(list)
    root(string) - root control of the limb chain
    moduleType(string)
    
    RETURNS:
    returnList(list) = [rootHelper(string),helperObjects(list),helperObjectGroups(list)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    moduleColors = modules.returnModuleColors(moduleNull)
    helperObjects = []
    helperObjectGroups = []
    returnBuffer = []
    #>>> Direction and size Stuff
    """ Directional data derived from joints """
    generalDirection = locators.returnHorizontalOrVertical(objects)
    if generalDirection == 'vertical' and 'leg' not in moduleType:
        worldUpVector = [0,0,-1]
    elif generalDirection == 'vertical' and 'leg' in moduleType:
        worldUpVector = [0,0,1]
    else:
        worldUpVector = [0,1,0]
    
    """ Get Size """
    size = (distance.returnBoundingBoxSizeToAverage(objects[0])*2)
    #>>> Master Orient helper
    """ make the curve"""
    createBuffer = curves.createControlCurve('circleArrow1',(size*2),'y+')
    curves.setCurveColorByName(createBuffer,moduleColors[0])
    """ copy the name attr"""
    attributes.storeInfo(createBuffer,'cgmType','templateOrientRoot')
    mainOrientHelperObj = NameFactory.doNameObject(createBuffer)
    """ store the object to it's respective  object """
    attributes.storeObjectToMessage (mainOrientHelperObj, root, 'orientHelper')
    returnBuffer.append(mainOrientHelperObj)
    """ Snapping """
    position.movePointSnap(mainOrientHelperObj,root)    
    constBuffer = mc.aimConstraint(objects[1],mainOrientHelperObj,maintainOffset = False, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpVector = worldUpVector, worldUpType = 'vector' )
    mc.delete (constBuffer[0])
    """ Follow Groups """
    mainOrientHelperGroupBuffer = rigging.groupMeObject(mainOrientHelperObj)
    mainOrientHelperGroupBuffer = NameFactory.doNameObject(mainOrientHelperGroupBuffer)
    mainOrientHelperGroup = rigging.doParentReturnName(mainOrientHelperGroupBuffer,root)
    mc.pointConstraint(objects[0],mainOrientHelperGroupBuffer,maintainOffset = False)
    helperObjectGroups.append(mainOrientHelperGroup)
    
    """ set up constraints """
    mc.aimConstraint(objects[-1],mainOrientHelperGroup,maintainOffset = True, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpObject = root, worldUpType = 'objectRotation' )
    """ lock and hide stuff """
    attributes.doSetLockHideKeyableAttr(mainOrientHelperObj,True,False,False,['tx','ty','tz','rz','ry','sx','sy','sz','v'])
    
    #>>> The sub helpers
    """ make our pair lists """
    pairList = lists.parseListToPairs(objects)

    """ make our controls """
    helperObjects = []
    for pair in pairList:
        """ Get Size """
        size = (distance.returnBoundingBoxSizeToAverage(pair[0])*2)
        
        """ make the curve"""
        createBuffer = curves.createControlCurve('circleArrow2Axis',size,'y-')
        curves.setCurveColorByName(createBuffer,moduleColors[1])
        
        """ copy the name attr"""
        attributes.copyUserAttrs(pair[0],createBuffer,['cgmName'])
        attributes.storeInfo(createBuffer,'cgmType','templateOrientObject')
        helperObj = NameFactory.doNameObject(createBuffer)
        
        
        """ store the object to it's respective  object and to an object list """
        attributes.storeObjectToMessage (helperObj, pair[0], 'orientHelper')
        helperObjects.append(helperObj)
        
        """ initial snapping """
        position.movePointSnap(helperObj,pair[0])
        constBuffer = mc.aimConstraint(pair[1],helperObj,maintainOffset = False, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpVector = worldUpVector, worldUpType = 'vector' )
        mc.delete (constBuffer[0])
        
        """ follow groups """
        helperGroupBuffer = rigging.groupMeObject(helperObj)
        helperGroup = NameFactory.doNameObject(helperGroupBuffer)
        helperGroup = rigging.doParentReturnName(helperGroup,pair[0])
        helperObjectGroups.append(helperGroup)
        
        """ set up constraints """
        mc.aimConstraint(pair[1],helperGroup,maintainOffset = False, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpVector = [0,1,0], worldUpObject = mainOrientHelperObj, worldUpType = 'objectrotation' )

        """ lock and hide stuff """
        helperObj = attributes.returnMessageObject(pair[0],'orientHelper')
        mc.connectAttr((visAttr),(helperObj+'.v'))
        attributes.doSetLockHideKeyableAttr(helperObj,True,False,False,['tx','ty','tz','ry','rz','sx','sy','sz','v'])
    
    #>>> For the last object in the chain
    for obj in objects[-1:]:
        """ Get Size """
        size = (distance.returnBoundingBoxSizeToAverage(obj)*2)
        
        """ make the curve"""
        createBuffer = curves.createControlCurve('circleArrow2Axis',size,'y-')
        curves.setCurveColorByName(createBuffer,moduleColors[1])
        """ copy the name attr"""
        attributes.copyUserAttrs(obj,createBuffer,['cgmName'])
        attributes.storeInfo(createBuffer,'cgmType','templateOrientObject')
        helperObj = NameFactory.doNameObject(createBuffer)
        
        """ store the object to it's respective  object """
        attributes.storeObjectToMessage (helperObj, obj, 'orientHelper')
        
        """ initial snapping """
        position.movePointSnap(helperObj,obj)
        constBuffer = mc.aimConstraint(objects[-2],helperObj,maintainOffset = False, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpVector = worldUpVector, worldUpType = 'vector' )
        mc.delete (constBuffer[0])
        
        """ follow groups """
        helperGroupBuffer = rigging.groupMeObject(helperObj)
        helperGroup = NameFactory.doNameObject(helperGroupBuffer)
        helperGroup = rigging.doParentReturnName(helperGroup,obj)
        helperObjectGroups.append(helperGroup)
        
        """ set up constraints """
        secondToLastHelperObject = attributes.returnMessageObject(objects[-2],'orientHelper')
        mc.orientConstraint(secondToLastHelperObject,helperGroup,maintainOffset = False, weight = 1)
        
        """ lock and hide stuff """
        helperObj = attributes.returnMessageObject(obj,'orientHelper')
        mc.connectAttr((visAttr),(helperObj+'.v'))
        attributes.doSetLockHideKeyableAttr(helperObj,True,False,False,['tx','ty','tz','sx','sy','sz','v'])
        helperObjects.append(helperObj)
   
    
    returnBuffer.append(helperObjects)
    returnBuffer.append(helperObjectGroups)
    return returnBuffer
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addControlHelpers(sourceObjects,moduleNull,visAttr):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds control size and pivot helpers to a template chain
    
    ARGUMENTS:
    sourceObjects(list)
    visAttr(string)
    
    RETURNS:
    returnList(list) = [rootHelper(string),helperObjects(list),helperObjectGroups(list)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    moduleColors = modules.returnModuleColors(moduleNull)
    helperObjects = []
    helperObjectGroups = []
    returnBuffer = []
    
    templateControlObjectsNull = modules.returnInfoTypeNull(moduleNull,'templateControlObjects')
    for obj in sourceObjects:
        """ Get Size """
        size = (distance.returnBoundingBoxSizeToAverage(obj))*2.5
        
        """ make the curve"""
        createBuffer = curves.createControlCurve('nail4',size)
        curves.setCurveColorByName(createBuffer,moduleColors[1])
        
        mc.setAttr((createBuffer+'.rx'),90)
        mc.makeIdentity(createBuffer, apply = True, r=True)
        
        
        """ copy the name attr"""
        attributes.copyUserAttrs(obj,createBuffer,['cgmName'])
        attributes.storeInfo(createBuffer,'cgmType','templateControlObject')
        helperObj = NameFactory.doNameObject(createBuffer)
        
        helperObjects.append(helperObj)
        
        """ initial snapping """
        position.movePointSnap(helperObj,obj)
        aimLoc = locators.locMeObject(obj)
        aimGroup = rigging.groupMeObject(aimLoc)
        upLoc = locators.locMeObject(obj)
        upGroup = rigging.groupMeObject(upLoc)
        mc.setAttr((aimLoc+'.tx'),20)
        mc.setAttr((upLoc+'.ty'),20)
        constBuffer = mc.aimConstraint(aimLoc,helperObj,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
        mc.delete (constBuffer[0])
        mc.delete(aimGroup)
        mc.delete(upGroup)
        
        """ follow groups """
        helperGroupBuffer = rigging.groupMeObject(helperObj)
        helperGroup = NameFactory.doNameObject(helperGroupBuffer)
        #objParent = search.returnParentObject(obj)
        helperGroup = rigging.doParentReturnName(helperGroup,obj)
        helperObjectGroups.append(helperGroup)
        
        """ store """
        attributes.storeObjectToMessage (helperObj, templateControlObjectsNull, search.returnTagInfo(helperObj,'cgmName'))

        """ lock and hide stuff """
        mc.connectAttr((visAttr),(helperObj+'.v'))
        attributes.doSetLockHideKeyableAttr(helperObj,True,False,False,['ry','rz','v'])

    
    returnBuffer.append(helperObjects)
    returnBuffer.append(helperObjectGroups)
    return returnBuffer
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>> Sizing
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def doSizeCharacter(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds control size and pivot helpers to a template chain
    
    ARGUMENTS:
    sourceObjects(list)
    visAttr(string)
    
    RETURNS:
    returnList(list) = [rootHelper(string),helperObjects(list),helperObjectGroups(list)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get Info
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ TemplateSizeObject Check """
    templateSizeObject = attributes.returnMessageObject(masterNull,'templateSizeObject')
    if templateSizeObject != False:
        templateSizeObjects =[]
        templateSizeObjects.append(attributes.returnMessageObject(templateSizeObject,'controlStart'))
        templateSizeObjects.append(attributes.returnMessageObject(templateSizeObject,'controlEnd'))
    else:
        return 'MUST HAVE BASE SIZE OBJECT'


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Make our start locs and get our initial positional data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    meshGroup = attributes.returnMessageObject(masterNull,'meshGroup')
    
    """ basic orientation"""
    basicOrientation = locators.returnHorizontalOrVertical(templateSizeObjects)
    
    horiztonalLegDict = {'left':[3,templateSizeObjects[0],templateSizeObjects[1]],'right':[7,templateSizeObjects[0],templateSizeObjects[1]],'left_front':[3,templateSizeObjects[1],templateSizeObjects[0]], 'right_front':[7,templateSizeObjects[1],templateSizeObjects[0]], 'left_back':[3,templateSizeObjects[0],templateSizeObjects[1]],'right_back':[7,templateSizeObjects[0],templateSizeObjects[1]]}
    cvDict = {'left':3,'right':7,'bottom':5,'top':0, 'left_front':4, 'right_front':6, 'left_back':2,'right_back':8,'None':0}
    typeWorkingCurveDict = {'clavicle':templateSizeObjects[1],'head':templateSizeObjects[1],'arm':templateSizeObjects[1],'leg':templateSizeObjects[0],'tail':templateSizeObjects[0],'wing':templateSizeObjects[1],'finger':templateSizeObjects[1]}
    typeAimingCurveDict = {'arm':templateSizeObjects[0],'leg':templateSizeObjects[1],'tail':templateSizeObjects[1],'wing':templateSizeObjects[0],}
    modeDict = {'finger':'parentDuplicate','foot':'footBase','head':'child','arm':'radialOut','leg':'radialDown','tail':'cvBack','wing':'radialOut','clavicle':'radialOut'}
    aimSpreads = ['arm','leg','wing']

    """ Order the modules for processing """
    orderedModules = modules.returnOrderedModules(masterNull)
    parentModules = modules.returnOrderedParentModules(masterNull)
    print parentModules
    
    """ make our starter locs """
    characterCorePositionList = {}
    locInfo = {}
    checkList = {}
    for m in orderedModules:
        checkList[m] = 0

    """ first do the root modules """
    for module in orderedModules:
        moduleParent = attributes.returnMessageObject(module,'moduleParent')
        if moduleParent == masterNull:
            rawModuleName = NameFactory.returnUniqueGeneratedName(module,ignore='cgmType')
            locInfoBuffer = createStartingPositionLoc(module,'innerChild',templateSizeObjects[0],templateSizeObjects[1])
            characterCorePositionListBuffer = doGenerateInitialPositionData(module,masterNull,locInfoBuffer,templateSizeObjects)      
            characterCorePositionList[module] = characterCorePositionListBuffer[0]
            locInfo[module] = characterCorePositionListBuffer[1]
            checkList.pop(module)
            orderedModules.remove(module) 
    
    for module in parentModules:
        childrenModules = modules.returnOrderedChildrenModules(module)
        for moduleType in childrenModules.keys():
            typeModuleDict = childrenModules.get(moduleType)
            for directionKey in typeModuleDict.keys():
                directionModuleSet = typeModuleDict.get(directionKey)
                locInfoBuffer = {}
                #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                # Starter locs
                #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                for m in directionModuleSet:
                    rawModuleName = NameFactory.returnUniqueGeneratedName(m,ignore='cgmType')
                    """ make our initial sub groups """
                    if moduleType == 'arm' or moduleType == 'wing' or moduleType == 'tail':
                        locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(moduleType),typeWorkingCurveDict.get(moduleType),typeAimingCurveDict.get(moduleType),cvDict.get(directionKey))
                        orderedModules.remove(m) 
                        checkList.pop(m)
                    elif moduleType == 'clavicle':
                        locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(moduleType),templateSizeObjects[1],templateSizeObjects[0],cvDict.get(directionKey))
                        orderedModules.remove(m) 
                        checkList.pop(m)
                    elif moduleType == 'finger':
                        moduleParent = attributes.returnMessageObject(m,'moduleParent')
                        parentLoc = locInfo.get(moduleParent)
                        locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(moduleType),parentLoc)
                        orderedModules.remove(m) 
                    elif moduleType == 'foot':
                        moduleParent = attributes.returnMessageObject(m,'moduleParent')
                        parentLoc = locInfo.get(moduleParent)
                        locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(moduleType),parentLoc)
                        orderedModules.remove(m) 
                        checkList.pop(m)
                    elif moduleType == 'head':
                        locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(moduleType),templateSizeObjects[1],templateSizeObjects[0],cvDict.get(directionKey))
                        orderedModules.remove(m) 
                        checkList.pop(m)
                    elif moduleType == 'leg':
                        if basicOrientation == 'vertical':
                            locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(moduleType),typeWorkingCurveDict.get(moduleType),typeAimingCurveDict.get(moduleType),cvDict.get(directionKey))
                        else:
                            horizontalLegInfoBuffer = horiztonalLegDict.get(directionKey)
                            locInfoBuffer[m] = createStartingPositionLoc(m,modeDict.get(moduleType),horizontalLegInfoBuffer[1],horizontalLegInfoBuffer[2],horizontalLegInfoBuffer[0])
                        orderedModules.remove(m) 
                        checkList.pop(m)
                    """ do we need to spread them? """
                numberOfLocs = len(directionModuleSet)
                if numberOfLocs > 1:        
                    if moduleType in aimSpreads:
                        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                        # Aim spread
                        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                        print 'aim spread!'
                        """ do an aim spread """
                        sizeObjectLength = distance.returnDistanceBetweenObjects(templateSizeObjects[0],templateSizeObjects[1])
                        moveDistance = (sizeObjectLength/1.25)/len(directionModuleSet)
                            
                        """ let's move stuff """
                        cnt = 0
                        for m in directionModuleSet:
                            mLocInfo = locInfoBuffer.get(m)
                            mc.xform(mLocInfo[1],t=[0,0,moveDistance*cnt],r=True,os=True)
                            cnt += 1
                    else:
                        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                        # Split spread
                        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                        print 'split spread!'
                        """ if we're not going to do an aim spread...do a split spread """
                        if moduleType == 'finger':
                            print 'yes!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                            """ get the parent module"""
                            moduleParent = attributes.returnMessageObject(directionModuleSet[0],'moduleParent')
                            print 
                            """ get it's positional data"""
                            parentPositions = characterCorePositionList.get(moduleParent)
                            parentLastSegmentDistance = distance.returnDistanceBetweenPoints(parentPositions[-2],parentPositions[-1])
                            curveWidth = parentLastSegmentDistance / 5
                        else:
                            absCurveSize = distance.returnAbsoluteSizeCurve(typeWorkingCurveDict.get(moduleType))
                            curveWidth = max(absCurveSize)
                            curveWidth = (curveWidth*.9)/2
                            
                        mLocInfo = locInfoBuffer.get(directionModuleSet[0])
                        
                        """ gonna make a curve to split"""
                        locs=[]
                        locToDup = mLocInfo[0]
                        curveStartBuffer = mc.duplicate(locToDup,rc=True)
                        curveEndBuffer = mc.duplicate(locToDup,rc=True)
                        curveStartBuffer = rigging.doParentToWorld(curveStartBuffer[0])
                        curveEndBuffer = rigging.doParentToWorld(curveEndBuffer[0])
                        locs.append(curveStartBuffer)
                        locs.append(curveEndBuffer)
                        mc.xform(locs[0],t=[curveWidth,0,0],r=True,os=True)
                        mc.xform(locs[1],t=[-curveWidth,0,0],r=True,os=True)
                        
                        if numberOfLocs == 2:
                            cnt = 0
                            for m in directionModuleSet:
                                mLocInfo = locInfoBuffer.get(m)
                                position.movePointSnap(mLocInfo[1],locs[cnt])
                                cnt +=1
                            for loc in locs:
                                mc.delete(loc)
                        elif numberOfLocs == 3:
                            midM = directionModuleSet[0]
                            cnt = 0
                            for m in directionModuleSet:
                                if m != midM:
                                    mLocInfo = locInfoBuffer.get(m)
                                    position.movePointSnap(mLocInfo[1],locs[cnt])
                                    cnt +=1
                            for loc in locs:
                                mc.delete(loc)
                        else:
                            crvName = curves.curveFromObjList(locs)          
                            crvName = mc.rebuildCurve (crvName, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=len(directionModuleSet)-1, d=1, tol=0.001)
                            curveLocs = locators.locMeCVsOnCurve(crvName[0])
                            cnt = 0
                            for m in directionModuleSet:
                                mLocInfo = locInfoBuffer.get(m)
                                position.movePointSnap(mLocInfo[1],curveLocs[cnt])
                                cnt+=1
                            
                            for loc in curveLocs,locs:
                                mc.delete(loc)
                            mc.delete(crvName[0])
                #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                # Generate initial positional data
                #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                for module in directionModuleSet:
                    #characterCorePositionListBuffer = doGenerateInitialPositionData(m,masterNull,locInfoBuffer,templateSizeObjects)      
                    characterCorePositionList[module] = 'data goes here!'
                    currentLocInfo = locInfoBuffer.get(module)
                    locInfo[module] = currentLocInfo
                    if moduleType == 'arm':
                        if modules.returnOrderedChildrenModules(module) != False:
                            baseDistance = (doGeneratePartBaseDistance(currentLocInfo[0],meshGroup)) * .7
                        else: baseDistance = doGeneratePartBaseDistance(currentLocInfo[0],meshGroup)
                    elif moduleType == 'leg':
                        if modules.returnOrderedChildrenModules(module) != False:
                            baseDistance = (doGeneratePartBaseDistance(currentLocInfo[0],meshGroup)) * .9
                        else: baseDistance = doGeneratePartBaseDistance(currentLocInfo[0],meshGroup)
                    elif moduleType == 'foot' or moduleType == 'hoof':
                        """ get the parent module"""
                        moduleParent = attributes.returnMessageObject(m,'moduleParent')
                        """ get it's positional data"""
                        parentPositions = characterCorePositionList.get(moduleParent)
                        parentLastSegmentDistance = distance.returnDistanceBetweenPoints(parentPositions[-2],parentPositions[-1])
                        baseDistance = parentLastSegmentDistance / 2.5
                    else:
                        baseDistance = doGeneratePartBaseDistance(currentLocInfo[0],meshGroup)
                    characterCorePositionListBuffer = doGenerateInitialPositionData(module,masterNull,currentLocInfo,templateSizeObjects,baseDistance)      
                    characterCorePositionList[module] = characterCorePositionListBuffer[0]
                    locInfo[module] = characterCorePositionListBuffer[1]
                        
    
    for key in locInfo.keys():
        infoBuffer = locInfo.get(key)
        parentBuffer = search.returnAllParents(infoBuffer)
        if mc.objExists(parentBuffer[-1]) == True:
            mc.delete(parentBuffer[-1])
            
            
    
    orderedModules = modules.returnOrderedModules(masterNull)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Store everything
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    for module in orderedModules:
        """ module null data """
        moduleData = attributes.returnUserAttrsToDict(module)
        infoNulls = modules.returnInfoNullsFromModule(module)
    
        """ part name """
        partName = NameFactory.returnUniqueGeneratedName(module, ignore = 'cgmType')
        partType = moduleData.get('cgmModuleType')
        direction = moduleData.get('cgmDirection')
        
        """ template null """
        templateNull = moduleData.get('templateNull')
        templateNullData = attributes.returnUserAttrsToDict(templateNull)
        curveDegree = templateNullData.get('curveDegree')
        handles = templateNullData.get('handles')
        stiffIndex = templateNullData.get('stiffIndex') 
    
        """ template object nulls """
        templatePosObjectsInfoNull = infoNulls.get('templatePosObjects')
        templateControlObjectsNull = infoNulls.get('templateControlObjects')
        starterObjectsInfoNull = infoNulls.get('templateStarterData')
        templateControlObjectsDataNull = infoNulls.get('templateControlObjectsData')
        rotateOrderInfoNull = infoNulls.get('rotateOrderInfo')
        coreNamesInfoNull = infoNulls.get('coreNames')
        
        """ rig null """
        rigNull = moduleData.get('rigNull')
        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Positional
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
        corePositionList = characterCorePositionList.get(module)
        
        modules.doPurgeNull(starterObjectsInfoNull)
        """ store our positional data """
        for i in range(len(corePositionList)):
            buffer = ('%s%s' % ('pos_',i))
            mc.addAttr (starterObjectsInfoNull, ln=buffer, at= 'double3')
            mc.addAttr (starterObjectsInfoNull, ln=(buffer+'X'),p=buffer , at= 'double')
            mc.addAttr (starterObjectsInfoNull, ln=(buffer+'Y'),p=buffer , at= 'double')
            mc.addAttr (starterObjectsInfoNull, ln=(buffer+'Z'),p=buffer , at= 'double')
            xBuffer = (starterObjectsInfoNull+'.'+buffer+'X')
            yBuffer = (starterObjectsInfoNull+'.'+buffer+'Y')
            zBuffer = (starterObjectsInfoNull+'.'+buffer+'Z')
            set = corePositionList[i]
            mc.setAttr (xBuffer, set[0])
            mc.setAttr (yBuffer, set[1])
            mc.setAttr (zBuffer, set[2])
            
        """ make a place to store rotational data """
        for i in range(len(corePositionList)+1):
            buffer = ('%s%s' % ('rot_',i))
            mc.addAttr (starterObjectsInfoNull, ln=buffer, at= 'double3')
            mc.addAttr (starterObjectsInfoNull, ln=(buffer+'X'),p=buffer , at= 'double')
            mc.addAttr (starterObjectsInfoNull, ln=(buffer+'Y'),p=buffer , at= 'double')
            mc.addAttr (starterObjectsInfoNull, ln=(buffer+'Z'),p=buffer , at= 'double')

        modules.doPurgeNull(templateControlObjectsDataNull)
        """ store our positional data """
        for i in range(len(corePositionList)):
            buffer = ('%s%s' % ('pos_',i))
            mc.addAttr (templateControlObjectsDataNull, ln=buffer, at= 'double3')
            mc.addAttr (templateControlObjectsDataNull, ln=(buffer+'X'),p=buffer , at= 'double')
            mc.addAttr (templateControlObjectsDataNull, ln=(buffer+'Y'),p=buffer , at= 'double')
            mc.addAttr (templateControlObjectsDataNull, ln=(buffer+'Z'),p=buffer , at= 'double')
            
            """ make a place to store rotational data """
            buffer = ('%s%s' % ('rot_',i))
            mc.addAttr (templateControlObjectsDataNull, ln=buffer, at= 'double3')
            mc.addAttr (templateControlObjectsDataNull, ln=(buffer+'X'),p=buffer , at= 'double')
            mc.addAttr (templateControlObjectsDataNull, ln=(buffer+'Y'),p=buffer , at= 'double')
            mc.addAttr (templateControlObjectsDataNull, ln=(buffer+'Z'),p=buffer , at= 'double')
                      
            
            """ make a place for scale data """
            buffer = ('%s%s' % ('scale_',i))
            mc.addAttr (templateControlObjectsDataNull, ln=buffer, at= 'double3')
            mc.addAttr (templateControlObjectsDataNull, ln=(buffer+'X'),p=buffer , at= 'double')
            mc.addAttr (templateControlObjectsDataNull, ln=(buffer+'Y'),p=buffer , at= 'double')
            mc.addAttr (templateControlObjectsDataNull, ln=(buffer+'Z'),p=buffer , at= 'double')
    
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Need to generate names
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
        """ check the settings first """
        settingsCoreNames = modules.returncgmTemplateCoreNames(partType)
        
        """ if there are no names settings, genearate them from name of the limb module"""
        generatedNames = []
        if settingsCoreNames == False:   
            cnt = 1
            for handle in range(handles):
                generatedNames.append('%s%s%i' % (partName,'_',cnt))
                cnt+=1
        
        elif (len(corePositionList)) > (len(settingsCoreNames)):
            """ Otherwise we need to make sure that there are enough core names for handles """       
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
            
        
        modules.doPurgeNull(coreNamesInfoNull)
        """ store our name data"""
        n = 0
        for name in generatedNames:
            attrBuffer = (coreNamesInfoNull + '.' + ('%s%s' % ('name_',n)))
            attributes.addStringAttributeToObj(coreNamesInfoNull,('%s%s' % ('name_',n)))
            n+=1
            mc.setAttr(attrBuffer, name, type='string')

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Rotation orders
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        modules.doPurgeNull(rotateOrderInfoNull)
        """ store our rotation order data """
        for i in range(len(corePositionList)):
            atrrNamebuffer = ('%s%s' % ('rotateOrder_',i))
            attributes.addRotateOrderAttr(rotateOrderInfoNull,atrrNamebuffer)
            
        print ('%s%s' % (module,' sized and stored!'))

    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doGenerateInitialPositionData(moduleNull,masterNull, startLocList, templateSizeObjects, partBaseDistance = 0):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Calculates initial positioning info for objects
    
    ARGUMENTS:
    sourceObjects(list)
    visAttr(string)
    
    RETURNS:
    returnList(list) = [posList(list),endChildLoc(loc)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    """ module null data """
    moduleNullData = attributes.returnUserAttrsToDict(moduleNull)

    """ part name """
    partName = NameFactory.returnUniqueGeneratedName(moduleNull, ignore = 'cgmType')
    partType = moduleNullData.get('cgmModuleType')
    direction = moduleNullData.get('cgmDirection')
    
    """ template null """
    templateNull = moduleNullData.get('templateNull')
    templateNullData = attributes.returnUserAttrsToDict(templateNull)
    curveDegree = templateNullData.get('curveDegree')
    handles = templateNullData.get('handles')
    stiffIndex = templateNullData.get('stiffIndex') 
    
    """ template object nulls """
    templatePosObjectsInfoNull = modules.returnInfoTypeNull(moduleNull,'templatePosObjects')
    
    """ module parent """
    moduleParent = attributes.returnMessageObject(moduleNull,'moduleParent')
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Things with the character root as a base Limb segments and Torsos
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
    if moduleParent == masterNull:
        startLoc = startLocList[0]
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Distances
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """ measure root object"""
        absStartCurveSize = distance.returnAbsoluteSizeCurve(templateSizeObjects[0])
        sizeObjectLength = distance.returnDistanceBetweenObjects(startLoc,templateSizeObjects[-1])
        corePositionList = modules.returncgmTemplatePartPositionData(partType)
        
        if corePositionList == False:
            corePositionList = []
            positions = cgmMath.divideLength(1,handles)
            for position in positions:
                bufferList = [0,0]
                bufferList.append(position)
                corePositionList.append(bufferList)
        
        """ 
        Get the data in a usable format. Our positional ratios are stored in x,y,z format
        so we're going to get the absolute size data in that format with our distance
        being our z value
        """
        moduleSizeBaseDistanceValues = []
        moduleSizeBaseDistanceValues.append(absStartCurveSize[0])
        moduleSizeBaseDistanceValues.append(absStartCurveSize[2])
        moduleSizeBaseDistanceValues.append(sizeObjectLength)
        
        """ multiply our values """
        translationValues = []
        for list in corePositionList:
            translationValues.append(cgmMath.multiplyLists([list,moduleSizeBaseDistanceValues]))
            
        baseLocs = []
        for value in translationValues:
            locBuffer = mc.duplicate(startLoc)
            mc.xform(locBuffer,t=value,r=True,os=True)
            baseLocs.append(locBuffer[0])
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # SubSplitting
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        splitTransformationValues = []
        if stiffIndex != 0:
            if handles > len(baseLocs):                
                if stiffIndex > 0:
                    stiff = 'positive'
                    splitDistance = distance.returnDistanceBetweenObjects(baseLocs[stiffIndex],baseLocs[-1])
                    print splitDistance
                    print baseLocs[stiffIndex]
                    positions = cgmMath.divideLength(splitDistance,(handles-len(baseLocs)+2))
                    for position in positions[1:-1]:
                        splitTransformationValues.append([0,0,position])
                else:
                    stiff = 'negative'
                    splitDistance = distance.returnDistanceBetweenObjects(baseLocs[0],baseLocs[stiffIndex +-1])
                    positions = cgmMath.divideLength(splitDistance,(handles-len(baseLocs)+2))
                    for position in positions[1:-1]:
                        splitTransformationValues.append([0,0,position])
        else:
            if handles > len(baseLocs):
                stiff = 'zero'
                splitDistance = distance.returnDistanceBetweenObjects(baseLocs[0],baseLocs[1])
                positions = cgmMath.divideLength(splitDistance,(handles-len(baseLocs)+2))
                for position in positions[1:-1]:
                    splitTransformationValues.append([0,0,position])
                        
        if len(splitTransformationValues) > 0 :
            for value in splitTransformationValues:
                if stiff == 'positive':
                    locBuffer = mc.duplicate(baseLocs[stiffIndex])
                else:
                    locBuffer = mc.duplicate(baseLocs[0])
                mc.xform(locBuffer,t=value,r=True,os=True)
                baseLocs.append(locBuffer[0])
            
        
        baseLocs = distance.returnDistanceSortedList(startLoc,baseLocs)
        mc.delete(startLoc)
        posList =  distance.returnWorldSpacePositionFromList(baseLocs)
        
        returnList = []
        returnList.append(posList)
        returnList.append(baseLocs[-1])
        
        for loc in baseLocs[:-1]:
            mc.delete(loc)
        return returnList
        
    else:
        startLoc = startLocList[0]
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Distances
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """ measure root object"""
        absStartCurveSize = distance.returnAbsoluteSizeCurve(templateSizeObjects[0])
        sizeObjectLength = partBaseDistance
        corePositionList = modules.returncgmTemplatePartPositionData(partType)
        
        if corePositionList == False:
            corePositionList = []
            positions = cgmMath.divideLength(1,handles)
            for position in positions:
                bufferList = [0,0]
                bufferList.append(position)
                corePositionList.append(bufferList)
        
        """ 
        Get the data in a usable format. Our positional ratios are stored in x,y,z format
        so we're going to get the absolute size data in that format with our distance
        being our z value
        """
        moduleSizeBaseDistanceValues = []
        moduleSizeBaseDistanceValues.append(absStartCurveSize[0])
        moduleSizeBaseDistanceValues.append(absStartCurveSize[2])
        moduleSizeBaseDistanceValues.append(sizeObjectLength)
        
        """ multiply our values """
        translationValues = []
        for list in corePositionList:
            translationValues.append(cgmMath.multiplyLists([list,moduleSizeBaseDistanceValues]))
        
        baseLocs = []
        if partType == 'clavicle' and direction == 'left':
            for value in translationValues:
                locBuffer = mc.duplicate(startLoc)
                mc.xform(locBuffer,t=[-value[0],value[1],value[2]],r=True,os=True)
                baseLocs.append(locBuffer[0])
        else:
            for value in translationValues:
                locBuffer = mc.duplicate(startLoc)
                mc.xform(locBuffer,t=value,r=True,os=True)
                baseLocs.append(locBuffer[0])
            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # SubSplitting
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        splitTransformationValues = []
        if stiffIndex != 0:
            if handles > len(baseLocs):                
                if stiffIndex > 0:
                    stiff = 'positive'
                    splitDistance = distance.returnDistanceBetweenObjects(baseLocs[stiffIndex],baseLocs[-1])
                    print splitDistance
                    print baseLocs[stiffIndex]
                    positions = cgmMath.divideLength(splitDistance,(handles-len(baseLocs)+2))
                    for position in positions[1:-1]:
                        splitTransformationValues.append([0,0,position])
                else:
                    stiff = 'negative'
                    splitDistance = distance.returnDistanceBetweenObjects(baseLocs[0],baseLocs[stiffIndex +-1])
                    positions = cgmMath.divideLength(splitDistance,(handles-len(baseLocs)+2))
                    for position in positions[1:-1]:
                        splitTransformationValues.append([0,0,position])
        else:
            if handles > len(baseLocs):
                stiff = 'zero'
                splitDistance = distance.returnDistanceBetweenObjects(baseLocs[0],baseLocs[1])
                positions = cgmMath.divideLength(splitDistance,(handles-len(baseLocs)+2))
                for position in positions[1:-1]:
                    splitTransformationValues.append([0,0,position])
                        
        if len(splitTransformationValues) > 0 :
            for value in splitTransformationValues:
                if stiff == 'positive':
                    locBuffer = mc.duplicate(baseLocs[stiffIndex])
                else:
                    locBuffer = mc.duplicate(baseLocs[0])
                mc.xform(locBuffer,t=value,r=True,os=True)
                baseLocs.append(locBuffer[0])
            
        
        baseLocs = distance.returnDistanceSortedList(startLoc,baseLocs)
        mc.delete(startLoc)
        posList =  distance.returnWorldSpacePositionFromList(baseLocs)
        if partType == 'clavicle':
            posList.reverse() 
        returnList = []
        returnList.append(posList)
        returnList.append(baseLocs[-1])
        
        for loc in baseLocs[:-1]:
            mc.delete(loc)
        
        return returnList
        
def createStartingPositionLoc(moduleNull, modeType='child', workingObject=None, aimingObject=None, cvIndex = None ):
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
    moduleName = NameFactory.returnUniqueGeneratedName(moduleNull,ignore='cgmType')
    if modeType == 'child':
        """ make initial lock and orient it """
        returnLoc = []
        curveShapes = mc.listRelatives(workingObject, shapes = True)
        startLoc = locators.locMeObject(workingObject)
        aimLoc = locators.locMeObject(workingObject)
        upLoc = locators.locMeCvFromCvIndex(curveShapes[0],0)
        
        startLoc = mc.rename(startLoc,(moduleName+'child_startLoc'))
        
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
        
        startLoc = mc.rename(startLoc, (moduleName+'_innerChild_startLoc'))
        
        aimConstraintBuffer = mc.aimConstraint(aimLoc,startLoc,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
        mc.delete(aimConstraintBuffer[0])
        mc.delete(upLoc)
        mc.delete(aimLoc)
        
        returnLoc.append(startLoc)
        zeroGroup = rigging.zeroTransformMeObject(startLoc)
        attributes.storeInfo(zeroGroup,'locator',startLoc)
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
        startLoc = mc.rename(startLoc, (moduleName+'_radialBackl_startLoc'))
        
        sizeObjectLength = distance.returnDistanceBetweenObjects(workingObject,aimingObject)
        mc.xform(aimLoc,t=[0,0,-sizeObjectLength],r=True,ws=True)
        aimConstraintBuffer = mc.aimConstraint(aimLoc,startLoc,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpType = 'vector' )
        mc.delete(aimConstraintBuffer[0])
        mc.delete(aimLoc)
        mc.delete(upLoc)
        returnLoc.append(startLoc)
        zeroGroup = rigging.zeroTransformMeObject(startLoc)
        attributes.storeInfo(zeroGroup,'locator',startLoc)
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
        startLoc = mc.rename(startLoc, (moduleName+'_radialOut_startLoc'))
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
        zeroGroup = rigging.zeroTransformMeObject(transformGroup)
        attributes.storeInfo(zeroGroup,'locator',startLoc)
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
        startLoc = mc.rename(startLoc, (moduleName+'_radialDown_startLoc'))
        
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
        zeroGroup = rigging.zeroTransformMeObject(transformGroup)
        attributes.storeInfo(zeroGroup,'locator',startLoc)
        attributes.storeInfo(zeroGroup,'move',transformGroup)
        returnLoc.append(zeroGroup)
        
        return returnLoc
        
    elif modeType == 'footBase':
        returnLoc = []
        startLoc = locators.locMeObject(workingObject)
        startLoc = mc.rename(startLoc,(moduleName+'_footcgmase_startLoc'))
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
        startLoc = mc.rename(startLoc,(moduleName+'_parentDup_startLoc'))
        masterGroup = rigging.groupMeObject(startLoc)
        returnLoc.append(startLoc)
        returnLoc.append(masterGroup)
        
        return returnLoc
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doGeneratePartBaseDistance(locator,meshGroup):
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
    boundingBoxSize = distance.returnBoundingBoxSize(meshGroup)
    boundingBoxSize = cgmMath.multiplyLists([[.5,.5,.5],boundingBoxSize])
    
    """ make our bounding box pivot """
    cgmLoc = rigging.centerPivotLocMeObject(meshGroup)
    
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


