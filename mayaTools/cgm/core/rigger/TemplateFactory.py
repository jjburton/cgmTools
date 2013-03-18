import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
__version__ = 0.03012013

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
                     cgmMath,
                     curves,
                     lists,
                     distance,
                     locators,
                     constraints,
                     attributes,
                     position,
                     search,
                     logic)
reload(attributes)
reload(constraints)
from cgm.core.lib import nameTools
from cgm.core.classes import DraggerContextFactory as dragFactory
reload(dragFactory)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    @r9General.Timer
    def __init__(self,module,forceNew = True,loadTemplatePose = True,tryTemplateUpdate = False, **kws): 
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
        log.debug(">>> TemplateFactory.go.__init__")        
        assert module.isModule(),"Not a module"
        self.m = module# Link for shortness
        log.info("loadTemplatePose: %s"%loadTemplatePose)     
            
        if tryTemplateUpdate:
            log.info("Trying template update...")
            if updateTemplate(module,**kws):
                if loadTemplatePose:
                    log.info("Trying loadTemplatePose...")                                    
                    self.m.loadTemplatePose()                
                return
        
        if module.isTemplated():
            if forceNew:
                module.deleteTemplate()
            else:
                log.warning("'%s' has already been templated"%module.getShortName())
                return
        
        self.cls = "TemplateFactory.go"
        
        self.moduleNullData = attributes.returnUserAttrsToDict(self.m.mNode)
        self.templateNull = self.m.getMessage('templateNull')[0] or False
        self.i_templateNull = self.m.templateNull#link
        self.rigNull = self.m.getMessage('rigNull')[0] or False
        self.moduleParent = self.moduleNullData.get('moduleParent')
        self.moduleColors = self.m.getModuleColors()
        self.l_coreNames = self.m.i_coreNames.value
        self.corePosList = self.i_templateNull.templateStarterData
        self.foundDirections = False #Placeholder to see if we have it
        
        assert len(self.l_coreNames) == len(self.corePosList),"coreNames length and corePosList doesn't match"
        
        #>>> part name 
        self.partName = self.m.getPartNameBase()
        self.partType = self.m.moduleType or False
        
        self.direction = None
        if self.m.hasAttr('cgmDirection'):
            self.direction = self.m.cgmDirection or None
        
        #>>> template null 
        self.templateNullData = attributes.returnUserAttrsToDict(self.templateNull)
        self.curveDegree = self.i_templateNull.curveDegree
        self.rollOverride = self.i_templateNull.rollOverride
        
        log.debug("Module: %s"%self.m.getShortName())
        log.debug("moduleNullData: %s"%self.moduleNullData)
        log.debug("partType: %s"%self.partType)
        log.debug("direction: %s"%self.direction) 
        log.debug("colors: %s"%self.moduleColors)
        log.debug("coreNames: %s"%self.l_coreNames)
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
        for obj in self.i_templateNull.getAllChildren():
            i_obj = cgmMeta.cgmNode(obj)
            i_obj.doStore('templateOwner',self.templateNull)
    except StandardError,error:
        log.warning(error) 
        
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
            nameCount = len(self.l_coreNames.value) or 1
            parentTemplateObjects = i_parent.templateNull.getMessage('controlObjects')
            log.debug("parentTemplateObjects: %s"%parentTemplateObjects)
            log.debug("firstPos: %s"%i_templateNull.templateStarterData[0])
            closestObj = distance.returnClosestObjectFromPos(i_templateNull.templateStarterData[0],parentTemplateObjects)
            #Find the closest object from the parent's template object
            log.debug("closestObj: %s"%closestObj)
            
            boundingBoxSize = distance.returnBoundingBoxSize(closestObj,True)
            log.info("bbSize = %s"%max(boundingBoxSize))
            
            size = max(boundingBoxSize) *.6
            if i_parent.moduleType == 'clavicle':
                return size * 2   
            
            if self.moduleType == 'clavicle':
                return size * .5
            elif self.moduleType == 'head':
                return size * .75
            elif self.moduleType == 'neck':
                return size * .5
            elif self.moduleType == 'leg':
                return size * 1.5
            elif self.moduleType in ['finger','thumb']:
                return size * .75                

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
            log.debug("closestObj: %s"%closestObj)
            if parentTemplateObjects.index(closestObj) == 0:#if it's the first object, connect to the root
                log.info('Use root for parent object')
                closestObj = i_parent.templateNull.root.mNode
                
            #Find the closest object from the parent's template object
            log.debug("closestObj: %s"%closestObj)
            l_constraints = cgmMeta.cgmObject(i_templateNull.root.parent).getConstraintsTo()
            if cgmMeta.cgmObject(i_templateNull.root.parent).isConstrainedBy(closestObj):
                log.debug("Already constrained!")
                return True
            elif l_constraints:mc.delete(l_constraints)
                
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
            sizeMultiplier = .75
        
        #>>> Create and set attributes on the object
        i_obj = cgmMeta.cgmObject( curves.createControlCurve('sphere',(size * sizeMultiplier)) )
        i_obj.addAttr('mClass','cgmObject',lock=True)#tag it so it can initialize later
        
        curves.setCurveColorByName(i_obj.mNode,self.moduleColors[0])
        
        i_obj.addAttr('cgmName',value = str(self.l_coreNames[i]), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
        if self.direction != None:
            i_obj.addAttr('cgmDirection',value = self.direction,attrType = 'string',lock=True)  
        i_obj.addAttr('cgmType',value = 'templateObject', attrType = 'string',lock=True) 
        i_obj.doName()#Name it
        
        mc.move (pos[0], pos[1], pos[2], [i_obj.mNode], a=True)
        i_obj.parent = self.templateNull
        
        #>>> Loc it and store the loc
        #i_loc = cgmMeta.cgmObject( i_obj.doLoc() )
        i_loc =  i_obj.doLoc()
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
    rootSize = (distance.returnBoundingBoxSizeToAverage(templHandleList[0],True)*1.25)    
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
    log.debug("templHandleList: %s"%templHandleList)
    if self.m.moduleType not in ['foot']:
        if len(templHandleList)>1:
            log.info("setting up constraints...")        
            constBuffer = mc.aimConstraint(templHandleList[-1],i_rootControl.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = self.worldUpVector, worldUpType = 'vector' )
            mc.delete (constBuffer[0])    
        elif self.m.getMessage('moduleParent'):
            #parentTemplateObjects =  self.m.moduleParent.templateNull.getMessage('controlObjects')
            helper = self.m.moduleParent.templateNull.controlObjects[-1].helper.mNode
            if helper:
                log.info("helper: %s"%helper)
                constBuffer = mc.orientConstraint( helper,i_rootControl.mNode,maintainOffset = False)
                mc.delete (constBuffer[0])    
    
    i_rootControl.parent = self.templateNull
    i_rootControl.doGroup(maintain=True)
    
    
    #>> Store objects
    #=============================      
    self.i_templateNull.curve = i_crv.mNode
    self.i_templateNull.root = i_rootControl.mNode
    self.i_templateNull.controlObjects = templHandleList
    
    self.i_rootControl = i_rootControl#link to carry

    #>> Orientation helpers
    #=============================      
    """ Make our Orientation Helpers """
    doCreateOrientationHelpers(self)
    doParentControlObjects(self.m)

    #if self.m.getMessage('moduleParent'):#If we have a moduleParent, constrain it
        #constrainToParentModule(self.m)
    return True

@r9General.Timer
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
    root = self.i_templateNull.getMessage('root')[0]
    objects =  self.i_templateNull.getMessage('controlObjects')
    log.debug(root)
    log.debug(objects)
    log.debug(self.foundDirections)
    
    #>> Create orient root control
    #=============================     
    orientRootSize = (distance.returnBoundingBoxSizeToAverage(root,True)*2.5)    
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
    
    self.i_orientHelpers = []#we're gonna store the instances so we can get them all after parenting and what not
    #>> Sub controls
    #============================= 
    if len(objects) == 1:#If a single handle module
        i_obj = cgmMeta.cgmObject(objects[0])
        position.moveOrientSnap(objects[0],root)
    else:
        for i,obj in enumerate(objects):
            log.debug("on %s"%(mc.ls(obj,shortNames=True)[0]))
            #>>> Create and color      
            size = (distance.returnBoundingBoxSizeToAverage(obj,True)*2) # Get size
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
            
            if i < len(objects)-1:#If we have a pair for it, aim at that pairs aim, otherwise, aim at the second to last object
                constBuffer = mc.aimConstraint(objects[i+1],i_obj.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = self.foundDirections[1], worldUpType = 'vector' )
            else:
                constBuffer = mc.aimConstraint(objects[-2],i_obj.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,-1], upVector = [0,1,0], worldUpVector = self.foundDirections[1], worldUpType = 'vector' )
    
            if constBuffer:mc.delete(constBuffer)
        
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
    self.i_templateNull.orientHelpers = bufferList
    self.i_orientRootHelper = i_orientRootControl
    log.debug("orientRootHelper: [%s]"%self.i_templateNull.orientRootHelper.getShortName())   
    log.debug("orientHelpers: %s"%self.i_templateNull.getMessage('orientHelpers'))

    return True

@r9General.Timer
def doParentControlObjects(self):
    """
    Needs instanced module
    """
    log.info(">>> doParentControlObjects")
    i_templateNull = self.templateNull#link for speed
    i_root = i_templateNull.root
    i_controlObjects = i_templateNull.controlObjects
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> Parent objects
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    for i_obj in i_controlObjects:
        i_obj.parent = i_root.mNode
        
    i_controlObjects[0].doGroup(maintain=True)#Group to zero out
    i_controlObjects[-1].doGroup(maintain=True)  
    
    log.debug(i_templateNull.getMessage('controlObjects',False))
    if self.moduleType not in ['foot']:
        constraintGroups = constraints.doLimbSegmentListParentConstraint(i_templateNull.getMessage('controlObjects',False))    
    
    for i_obj in i_controlObjects:
         i_parent = cgmMeta.cgmObject(i_obj.parent)
         i_parent.addAttr('mClass','cgmObject',lock=True)#tag it so it can initialize later
         i_obj.addAttr('owner',i_parent.mNode,attrType = 'messageSimple',lock=True)
         
    return

@r9General.Timer
def updateTemplate(self,saveTemplatePose = False,**kws):
    """
    Function to update a skeleton if it's been resized
    """
    if not self.isSized():
        log.warning("'%s' not sized. Can't update"%self.getShortName())
        return False
    if not self.isTemplated():
        log.warning("'%s' not templated. Can't update"%self.getShortName())
        return False
    
    if saveTemplatePose:self.storeTemplatePose()#Save our pose before destroying anything
        
    i_templateNull = self.templateNull#link for speed
    corePosList = i_templateNull.templateStarterData
    i_root = i_templateNull.root
    i_controlObjects = i_templateNull.controlObjects
    
    
    if not cgmMath.isVectorEquivalent(i_templateNull.controlObjects[0].translate,[0,0,0]):
        raise StandardError,"updateTemplate: doesn't currently support having a moved first template object"
        return False
    
    mc.xform(i_root.parent, translation = corePosList[0],worldSpace = True)
    
    for i,i_obj in enumerate(i_controlObjects[1:]):
        log.info(i_obj.getShortName())
        objConstraints = constraints.returnObjectConstraints(i_obj.parent)
        if objConstraints:mc.delete(objConstraints) 
        buffer = search.returnParentsFromObjectToParent(i_obj.mNode,i_root.mNode)
        i_obj.parent = False
        if buffer:mc.delete(buffer)
        mc.xform(i_obj.mNode, translation = corePosList[1:][i],worldSpace = True) 
        
    buffer = search.returnParentsFromObjectToParent(i_controlObjects[0].mNode,i_root.mNode)
    i_controlObjects[0].parent = False
    if buffer:mc.delete(buffer)
    
    doParentControlObjects(self)
    self.loadTemplatePose()#Restore the pose
    return True



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
def getGoodCurveDegree(self):
    log.debug(">>> getGoodCurveDegree")
    try:
        doCurveDegree = self.i_templateNull.curveDegree
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



