import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib import (modules,
                     curves,
                     lists,
                     distance,
                     locators,
                     constraints,
                     attributes,
                     position,
                     logic)
reload(attributes)
reload(constraints)
from cgm.lib.classes import NameFactory
from cgm.core.classes import DraggerContextFactory as dragFactory
reload(dragFactory)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 

class go(object):
    @r9General.Timer
    def __init__(self,module,forceNew = True,loadTemplatePose = True,**kws): 
        """
        To do:
        Add rotation order settting
        Add module parent check to make sure parent is templated to be able to move forward, or to constrain
        Add any other piece meal data necessary
        Add a cleaner to force a rebuild
        """
        # Get our base info
        #==============	        
        #>>> module null data 
        log.debug(">>> go.__init__")        
        assert module.mClass in ['cgmModule','cgmLimb'],"Not a module"
        module.deleteTemplate()        
        if module.isTemplated():
            if forceNew:
                module.deleteTemplate()
            else:
                raise StandardError,"'%s' has already been templated"%module.getShortName()
        
        self.cls = "TemplateFactory.go"
        self.m = module# Link for shortness
        
        self.moduleNullData = attributes.returnUserAttrsToDict(self.m.mNode)
        self.templateNull = self.m.getMessage('templateNull')[0] or False
        self.rigNull = self.m.getMessage('rigNull')[0] or False
        self.moduleParent = self.moduleNullData.get('moduleParent')
        self.moduleColors = self.m.getModuleColors()
        self.coreNames = self.m.coreNames.value
        self.corePosList = self.m.templateNull.templateStarterData
        self.foundDirections = False #Placeholder to see if we have it
        
        assert len(self.coreNames) == len(self.corePosList),"coreNames length and corePosList doesn't match"
        
        #>>> part name 
        self.partName = NameFactory.returnUniqueGeneratedName(self.m.mNode, ignore = 'cgmType')
        self.partType = self.m.moduleType or False
        
        self.direction = None
        if self.m.hasAttr('cgmDirection'):
            self.direction = self.m.cgmDirection or None
        
        #>>> template null 
        self.templateNullData = attributes.returnUserAttrsToDict(self.templateNull)
        self.curveDegree = self.m.templateNull.curveDegree
        self.rollOverride = self.m.templateNull.rollOverride
        
        log.debug("Module: %s"%self.m.getShortName())
        log.debug("moduleNullData: %s"%self.moduleNullData)
        log.debug("partType: %s"%self.partType)
        log.debug("direction: %s"%self.direction) 
        log.debug("colors: %s"%self.moduleColors)
        log.debug("coreNames: %s"%self.coreNames)
        log.debug("corePosList: %s"%self.corePosList)
        

        if self.m.mClass == 'cgmLimb':
            log.debug("mode: cgmLimb Template")
            doMakeLimbTemplate(self)
            doTagChildren(self)
        else:
            raise NotImplementedError,"haven't implemented '%s' templatizing yet"%self.m.mClass
        
        #>>> store template settings
        if loadTemplatePose:self.m.loadTemplatePose()
        
@r9General.Timer
def doTagChildren(self): 
    try:
        for obj in self.m.templateNull.getAllChildren():
            i_obj = cgmMeta.cgmNode(obj)
            i_obj.doStore('templateOwner',self.templateNull)
    except StandardError,error:
        log.warning(error) 
        
@r9General.Timer
def doTemplate(self):
    #Meat of the template process
    #==============	
    #>>> Get our base info
    """ module null data """
    moduleNullData = attributes.returnUserAttrsToDict(self.mNode)
    templateNull = self.templateNull.mNode or False
    rigNull = self.rigNull.mNode or false

    """ part name """
    partName = NameFactory.returnUniqueGeneratedName(self.mNode, ignore = 'cgmType')
    partType = self.moduleType or False
    
    direction = False
    if self.hasAttr('cgmDirection'):
        direction = self.cgmDirection or False
    
    """ template null """
    templateNullData = attributes.returnUserAttrsToDict(templateNull)
    curveDegree = self.templateNull.curveDegree
    rollOverride = self.templateNull.rollOverride
    
    log.debug("Module: %s"%self.getShortName())
    log.debug("moduleNullData: %s"%moduleNullData)
    log.debug("partType: %s"%partType)
    log.debug("direction: %s"%direction)
    
    
    """ template object nulls """
    #templatePosObjectsInfoNull = modules.returnInfoTypeNull(moduleNull,'templatePosObjects')
    #templateControlObjectsNull = modules.returnInfoTypeNull(moduleNull,'templateControlObjects')
        
    
    """ Start objects stuff """
    #templateStarterDataInfoNull = modules.returnInfoTypeNull(moduleNull,'templateStarterData')
    #initialObjectsTemplateDataBuffer = attributes.returnUserAttrsToList(templateStarterDataInfoNull)
    #initialObjectsPosData = lists.removeMatchedIndexEntries(initialObjectsTemplateDataBuffer,'cgm')
    """
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
    log.debug(corePositionList)
    log.debug( coreRotationList )
    log.debug( coreScaleList )
    """
    #template control objects stuff
    #==============	    
    """
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
    """
    # Names Info
    #==============	       
    """
    coreNamesInfoNull = modules.returnInfoTypeNull(moduleNull,'coreNames')
    coreNamesBuffer = attributes.returnUserAttrsToList(coreNamesInfoNull)
    coreNames = lists.removeMatchedIndexEntries(coreNamesBuffer,'cgm')
    coreNamesAttrs = []
    for set in coreNames:
        coreNamesAttrs.append(coreNamesInfoNull+'.'+set[0])
    divider = NameFactory.returnCGMDivider()
    
    print ('%s%s'% (moduleNull,' data aquired...'))
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> make template objects
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    return

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

@r9General.Timer
def returnModuleBaseSize(self):
    log.debug(">>> returnModuleSize")
    size = 12
    if self.getState() < 1:
        log.error("'%s' has not been sized. Cannot find base size"%self.getShortName())
        return False
    if not self.getMessage('moduleParent') and self.getMessage('modulePuppet'):
        log.debug("Sizing from modulePuppet")
        return size
    elif self.getMessage('moduleParent'):#If it has a parent
        log.debug("Sizing from moduleParent")
        i_templateNull = self.templateNull #Link
        i_parent = self.moduleParent #Link
        parentState = i_parent.getState()
        if i_parent.isTemplated():#If the parent has been templated, it makes things easy
            log.debug("Parent has been templated...")
            nameCount = len(self.coreNames.value) or 1
            parentTemplateObjects = i_parent.templateNull.getMessage('controlObjects')
            log.debug("parentTemplateObjects: %s"%parentTemplateObjects)
            log.debug("firstPos: %s"%i_templateNull.templateStarterData[0])
            closestObj = distance.returnClosestObjectFromPos(i_templateNull.templateStarterData[0],parentTemplateObjects)
            #Find the closest object from the parent's template object
            log.debug("closestObj: %s"%closestObj)
            
            boundingBoxSize = distance.returnBoundingBoxSize (closestObj)
            size = max(boundingBoxSize) *.25
            if self.moduleType == 'clavicle':
                return size * .5
            elif self.moduleType == 'head':
                return size * .75
            elif self.moduleType == 'leg':
                return size * 1.5           
            if i_parent.moduleType == 'clavicle':
                return size * 2            
        else:
            log.debug("Parent has not been templated...")          
    else:
        pass
    return size 

@r9General.Timer
def constrainToParentModule(self):
    """
    Pass a module class. Constrains template root to parent's closest template object
    """
    log.debug(">>> constrainToParentModule")
    if not self.isTemplated():
        log.error("Must be template state to contrainToParentModule: '%s' "%self.getShortName())
        return False
    
    if not self.getMessage('moduleParent'):
        return False
    else:
        log.debug("looking for moduleParent info")
        i_templateNull = self.templateNull #Link
        i_parent = self.moduleParent #Link
        parentState = i_parent.getState()
        if i_parent.isTemplated():#If the parent has been templated, it makes things easy
            log.debug("Parent has been templated...")
            parentTemplateObjects = i_parent.templateNull.getMessage('controlObjects')
            log.debug("parentTemplateObjects: %s"%parentTemplateObjects)
            closestObj = distance.returnClosestObject(i_templateNull.getMessage('root')[0],parentTemplateObjects)
            #Find the closest object from the parent's template object
            log.debug("closestObj: %s"%closestObj)
            
            if cgmMeta.cgmObject(i_templateNull.root.parent).isConstrainedBy(closestObj):
                log.debug("Already constrained!")
                return True
            else:
                return constraints.doConstraintObjectGroup(closestObj,group = i_templateNull.root.parent,constraintTypes=['point'])
        else:
            log.debug("Parent has not been templated...")           
            return False

@r9General.Timer
def doMakeLimbTemplate(self):  
    """
    Self should be a TemplateFactory.go
    """
    """
    returnList = []
    templObjNameList = []
    templHandleList = []
    """
    log.debug(">>> doMakeLimbTemplate")
    assert self.cls == 'TemplateFactory.go',"Not a TemlateFactory.go instance!"
    
    #Gather limb specific data and check
    #==============
    doCurveDegree = getGoodCurveDegree(self)
    if not doCurveDegree:raise ValueError,"Curve degree didn't query"
    
    #>>>Scale stuff
    size = returnModuleBaseSize(self.m)
    
    lastCountSizeMatch = len(self.corePosList) -1
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Making the template objects
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    templHandleList = []
    self.i_controlObjects = []
    self.i_locs = []
    for i,pos in enumerate(self.corePosList):# Don't like this sizing method but it is what it is for now
        #>> Make each of our base handles
        #=============================        
        if i == 0:
            sizeMultiplier = 1
        elif i == lastCountSizeMatch:
            sizeMultiplier = .8
        else:
            sizeMultiplier = .5
        
        #>>> Create and set attributes on the object
        i_obj = cgmMeta.cgmObject( curves.createControlCurve('sphere',(size * sizeMultiplier)) )
        i_obj.addAttr('mClass','cgmObject',lock=True)#tag it so it can initialize later
        
        curves.setCurveColorByName(i_obj.mNode,self.moduleColors[0])
        
        i_obj.addAttr('cgmName',value = str(self.coreNames[i]), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
        if self.direction != None:
            i_obj.addAttr('cgmDirection',value = self.direction,attrType = 'string',lock=True)  
        i_obj.addAttr('cgmType',value = 'templateObject', attrType = 'string',lock=True) 
        i_obj.doName()#Name it
        
        mc.move (pos[0], pos[1], pos[2], [i_obj.mNode], a=True)
        i_obj.parent = self.templateNull
        
        #>>> Loc it and store the loc
        i_loc = cgmMeta.cgmObject( i_obj.doLoc() )
        i_loc.addAttr('mClass','cgmObject',lock=True)#tag it so it can initialize later
        i_loc.addAttr('cgmName',value = self.m.getShortName(), attrType = 'string', lock=True) #Add name tag
        i_loc.addAttr('cgmType',value = 'templateCurveLoc', attrType = 'string', lock=True) #Add Type
        i_loc.v = False # Turn off visibility
        i_loc.doName()
        
        self.i_locs.append(i_loc)
        i_obj.connectChildNode(i_loc.mNode,'curveLoc','owner')
        i_loc.parent = self.templateNull#parent to the templateNull
        
        mc.pointConstraint(i_obj.mNode,i_loc.mNode,maintainOffset = False)#Point contraint loc to the object
                    
        templHandleList.append (i_obj.mNode)
        self.i_controlObjects.append(i_obj)
        
    #>> Make the curve
    #=============================     
    i_crv = cgmMeta.cgmObject( mc.curve (d=doCurveDegree, p = self.corePosList , os=True) )
    i_crv.addAttr('mClass','cgmObject',lock=True)#tag it so it can initialize later
    
    i_crv.addAttr('cgmName',value = str(self.m.getShortName()), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
    if self.direction != None:
        i_crv.addAttr('cgmDirection',value = self.direction, attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug

    i_crv.addAttr('cgmType',value = 'templateCurve', attrType = 'string', lock=True)
    curves.setCurveColorByName(i_crv.mNode,self.moduleColors[0])
    i_crv.parent = self.templateNull    
    i_crv.doName()
    i_crv.setDrawingOverrideSettings({'overrideEnabled':1,'overrideDisplayType':2},True)
        
    for i,i_obj in enumerate(self.i_controlObjects):#Connect each of our handles ot the cv's of the curve we just made
        mc.connectAttr ( (i_obj.curveLoc.mNode+'.translate') , ('%s%s%i%s' % (i_crv.mNode, '.controlPoints[', i, ']')), f=True )
        
    
    self.foundDirections = returnGeneralDirections(self,templHandleList)
    log.debug("directions: %s"%self.foundDirections )
    
    #>> Create root control
    #=============================  
    rootSize = (distance.returnBoundingBoxSizeToAverage(templHandleList[0])*1.25)    
    i_rootControl = cgmMeta.cgmObject( curves.createControlCurve('cube',rootSize) )
    i_rootControl.addAttr('mClass','cgmObject',lock=True)
    
    curves.setCurveColorByName(i_rootControl.mNode,self.moduleColors[0])
    i_rootControl.addAttr('cgmName',value = str(self.m.getShortName()), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug    
    i_rootControl.addAttr('cgmType',value = 'templateRoot', attrType = 'string', lock=True)
    if self.direction != None:
        i_rootControl.addAttr('cgmDirection',value = self.direction, attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
    i_rootControl.doName()

    #>>> Position it
    if self.m.moduleType in ['clavicle']:
        
        position.movePointSnap(i_rootControl.mNode,templHandleList[0])
    else:
        position.movePointSnap(i_rootControl.mNode,templHandleList[0])
    
    #See if there's a better way to do this    
    constBuffer = mc.aimConstraint(templHandleList[-1],i_rootControl.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = self.worldUpVector, worldUpType = 'vector' )
    mc.delete (constBuffer[0])
    
    i_rootControl.parent = self.templateNull
    i_rootControl.doGroup(maintain=True)
    
    #>> Store objects
    #=============================      
    #self.m.templateNull.connectChild(i_crv.mNode,'curve','owner')
    #self.m.templateNull.connectChild(i_rootControl.mNode,'root','owner')
    #self.m.templateNull.connectChildren(templHandleList,'controlObjects','owner')
    self.m.templateNull.curve = i_crv.mNode
    self.m.templateNull.root = i_rootControl.mNode
    self.m.templateNull.controlObjects = templHandleList
    
    self.i_rootControl = i_rootControl#link to carry

    #>> Orientation helpers
    #=============================      
    """ Make our Orientation Helpers """
    doCreateOrientationHelpers(self)
    doParentControlObjects(self)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> Control helpers
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #controlHelpersReturn = addControlHelpers(orientObjects,moduleNull,(templateNull+'.visControlHelpers'))

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> Input the saved values if there are any
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
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
    """
    if self.m.getMessage('moduleParent'):#If we have a moduleParent, constrain it
        constrainToParentModule(self.m)
    return True

def doCreateOrientationHelpers(self):
    """ 
    """
    log.debug(">>> addOrientationHelpers")
    assert self.cls == 'TemplateFactory.go',"Not a TemlateFactory.go instance!"
    assert mc.objExists(self.m.mNode),"module no longer exists"
    #Gather limb specific data and check
    #===================================
    #'orientHelpers':'messageSimple',#Orientation helper controls
    #'orientRootHelper':'messageSimple',#Root orienation helper

    helperObjects = []
    helperObjectGroups = []
    returnBuffer = []
    root = self.m.templateNull.getMessage('root')[0]
    objects =  self.m.templateNull.getMessage('controlObjects')
    log.debug(root)
    log.debug(objects)
    
    log.debug(self.foundDirections)
    
    #>> Create orient root control
    #=============================     
    orientRootSize = (distance.returnBoundingBoxSizeToAverage(root)*2.5)    
    i_orientRootControl = cgmMeta.cgmObject( curves.createControlCurve('circleArrow1',orientRootSize) )
    i_orientRootControl.addAttr('mClass','cgmObject',lock=True)
    
    curves.setCurveColorByName(i_orientRootControl.mNode,self.moduleColors[0])
    i_orientRootControl.addAttr('cgmName',value = str(self.m.getShortName()), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug    
    i_orientRootControl.addAttr('cgmType',value = 'templateOrientRoot', attrType = 'string', lock=True)
    i_orientRootControl.doName()
    
    #>>> Store it
    i_orientRootControl.connectParent(self.templateNull,'orientRootHelper','owner')#Connect it to it's object      
    
    #>>> Position and set up follow groups
    position.moveParentSnap(i_orientRootControl.mNode,root)    
    i_orientRootControl.parent = root #parent it to the root
    i_orientRootControl.doGroup(maintain = True)#group while maintainting position
    
    mc.pointConstraint(objects[0],i_orientRootControl.parent,maintainOffset = False)#Point contraint orient control to the first helper object
    mc.aimConstraint(objects[-1],i_orientRootControl.parent,maintainOffset = True, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpObject = root, worldUpType = 'objectRotation' )
    attributes.doSetLockHideKeyableAttr(i_orientRootControl.mNode,True,False,False,['tx','ty','tz','rx','ry','sx','sy','sz','v'])
    
    #>> Sub controls
    #============================= 
    self.i_orientHelpers = []#we're gonna store the instances so we can get them all after parenting and what not
    for i,obj in enumerate(objects):
        log.debug("on "+obj)
        #>>> Create and color      
        size = (distance.returnBoundingBoxSizeToAverage(obj)*2) # Get size
        i_obj = cgmMeta.cgmObject(curves.createControlCurve('circleArrow2Axis',size))#make the curve
        
        i_obj.addAttr('mClass','cgmObject',lock=True)
        curves.setCurveColorByName(i_obj.mNode,self.moduleColors[1])
        
        #>>> Tag and name
        i_obj.doCopyNameTagsFromObject(obj)
        i_obj.doStore('cgmType','templateOrientHelper',True)        
        i_obj.doName()
        
        #>>> Link it to it's object and append list for full store
        i_obj.connectParent(obj,'helper','owner')#Connect it to it's object      
        self.i_orientHelpers.append(i_obj)
        log.debug(i_obj.owner)
        #>>> initial snapping """
        position.movePointSnap(i_obj.mNode,obj)
        
        log.debug(i)
        log.debug(len(objects))
        if i < len(objects)-1:#If we have a pair for it, aim at that pairs aim, otherwise, aim at the second to last object
            constBuffer = mc.aimConstraint(objects[i+1],i_obj.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = self.foundDirections[1], worldUpType = 'vector' )
        else:
            constBuffer = mc.aimConstraint(objects[-2],i_obj.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,-1], upVector = [0,1,0], worldUpVector = self.foundDirections[1], worldUpType = 'vector' )

        mc.delete (constBuffer)
    
        #>>> follow groups
        i_obj.parent = obj
        i_obj.doGroup(maintain = True)
        
        if i < len(objects)-1:#If we have a pair for it, aim at that pairs aim, otherwise, aim at the second to last object
            mc.aimConstraint(objects[i+1],i_obj.parent,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = [0,1,0], worldUpObject = i_orientRootControl.mNode, worldUpType = 'objectrotation' )
        else:
            constBuffer = mc.aimConstraint(objects[-2],i_obj.parent,maintainOffset = False, weight = 1, aimVector = [0,0,-1], upVector = [0,1,0], worldUpObject = i_orientRootControl.mNode, worldUpType = 'objectrotation' )

        #>>> ConnectVis, lock and hide
        #mc.connectAttr((visAttr),(helperObj+'.v'))
        if obj == objects[-1]:
            attributes.doSetLockHideKeyableAttr(i_obj.mNode,True,False,False,['tx','ty','tz','ry','sx','sy','sz','v'])            
        else:
            attributes.doSetLockHideKeyableAttr(i_obj.mNode,True,False,False,['tx','ty','tz','rx','ry','sx','sy','sz','v'])
    
    #>>> Get data ready to go forward
    bufferList = []
    for o in self.i_orientHelpers:
        bufferList.append(o.mNode)
    self.m.templateNull.orientHelpers = bufferList
    self.i_orientRootHelper = i_orientRootControl
    log.debug("orientRootHelper: [%s]"%self.m.templateNull.orientRootHelper.getShortName())   
    log.debug("orientHelpers: %s"%self.m.templateNull.getMessage('orientHelpers'))

    return True

@r9General.Timer
def doParentControlObjects(self):
    log.debug(">>> addOrientationHelpers")
    assert self.cls == 'TemplateFactory.go',"Not a TemlateFactory.go instance!"
    assert mc.objExists(self.m.mNode),"module no longer exists"    
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> Parent objects
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    for i_obj in self.i_controlObjects:
        i_obj.parent = self.i_rootControl.mNode
        
    self.i_controlObjects[0].doGroup(maintain=True)#Group to zero out
    self.i_controlObjects[-1].doGroup(maintain=True)  
    
    log.debug(self.m.templateNull.getMessage('controlObjects',False))
    
    constraintGroups = constraints.doLimbSegmentListParentConstraint(self.m.templateNull.getMessage('controlObjects',False))    
    
    
    for i_obj in self.i_controlObjects:
         i_parent = cgmMeta.cgmObject(i_obj.parent)
         i_parent.addAttr('mClass','cgmObject',lock=True)#tag it so it can initialize later
         i_obj.addAttr('owner',i_parent.mNode,attrType = 'messageSimple',lock=True)
         
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Parenting constrainging parts
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    return
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
    #mc.setAttr ((moduleNull+'.templateState'), 1)
    #mc.setAttr ((moduleNull+'.skeletonState'), 0)
    
    #>>> Tag our objects for easy deletion
    #children = mc.listRelatives (templateNull, allDescendents = True,type='transform')
    #for obj in children:
        #attributes.storeInfo(obj,'cgmOwnedBy',templateNull)
        
    #>>> Visibility Connection
    #masterControl = attributes.returnMessageObject(masterNull,'controlMaster')
    #visControl = attributes.returnMessageObject(masterControl,'childControlVisibility')
    #attributes.doConnectAttr((visControl+'.orientHelpers'),(templateNull+'.visOrientHelpers'))
    #attributes.doConnectAttr((visControl+'.controlHelpers'),(templateNull+'.visControlHelpers'))
    #>>> Run a rename on the module to make sure everything is named properly
    #NameFactory.doRenameHeir(moduleNull)
    

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
def getGoodCurveDegree(self):
    log.debug(">>> getGoodCurveDegree")
    try:
        doCurveDegree = self.m.templateNull.curveDegree
    except:
        raise ValueError,"Failed to get module curve degree"
    
    if doCurveDegree == 0:
        doCurveDegree = 1
    else:
        if len(self.corePosList) <= 3:
            doCurveDegree = 1
        #else:
            #doCurveDegree = len(self.corePosList) - 1
    
    if doCurveDegree > 0:        
        return doCurveDegree
    return False

@r9General.Timer
def returnGeneralDirections(self,objList):
    """
    Get general direction of a list of objects in a module
    """
    log.debug(">>> returnGeneralDirections")

    self.generalDirection = logic.returnHorizontalOrVertical(objList)
    if self.generalDirection == 'vertical' and 'leg' not in self.m.moduleType:
        self.worldUpVector = [0,0,-1]
    elif self.generalDirection == 'vertical' and 'leg' in self.m.moduleType:
        self.worldUpVector = [0,0,1]
    else:
        self.worldUpVector = [0,1,0]    
    return [self.generalDirection,self.worldUpVector]



