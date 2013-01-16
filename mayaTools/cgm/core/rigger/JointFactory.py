# From Python =============================================================
import copy
import re

#TEMP
import cgm.core
cgm.core._reload()
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
from cgm.lib import (joints,
                     rigging,
                     attributes,
                     distance,
                     autoname,
                     search,
                     curves,
                     dictionary,
                     lists,
                     settings,
                     modules)
reload(joints)
from cgm.lib.classes import NameFactory

typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
namesDictionary = dictionary.initializeDictionary( settings.getNamesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    @r9General.Timer
    def __init__(self,moduleInstance): 
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
        assert moduleInstance.mClass in ['cgmModule','cgmLimb'],"Not a module"
        assert moduleInstance.isTemplated(),"Module is not templated"
        #assert object is templated
        #assert ...
        log.info(">>> go.__init__")
        self.cls = "JointFactory.go"
        self.m = moduleInstance# Link for shortness
        
        self.rigNull = self.m.getMessage('rigNull')[0] or False
        self.moduleColors = self.m.getModuleColors()
        self.coreNames = self.m.coreNames.value
        self.foundDirections = False #Placeholder to see if we have it
                
        #>>> part name 
        self.partName = NameFactory.returnUniqueGeneratedName(self.m.mNode, ignore = 'cgmType')
        self.partType = self.m.moduleType or False
        
        self.direction = None
        if self.m.hasAttr('cgmDirection'):
            self.direction = self.m.cgmDirection or None
        
        #>>> template null 
        self.i_templateNull = self.m.templateNull
        self.curveDegree = self.i_templateNull.curveDegree
        self.stiffIndex = self.i_templateNull.stiffIndex
        
        #>>> Instances and joint stuff
        self.jointOrientation = modules.returnSettingsData('jointOrientation')
        self.i_root = self.i_templateNull.root
        self.i_orientRootHelper = self.i_templateNull.orientRootHelper
        self.i_curve = self.i_templateNull.curve
        self.i_controlObjects = self.i_templateNull.controlObjects
        
        log.info("Module: %s"%self.m.getShortName())
        log.info("partType: %s"%self.partType)
        log.info("direction: %s"%self.direction) 
        log.info("colors: %s"%self.moduleColors)
        log.info("coreNames: %s"%self.coreNames)
        log.info("root: %s"%self.i_root.getShortName())
        log.info("curve: %s"%self.i_curve.getShortName())
        log.info("orientRootHelper: %s"%self.i_orientRootHelper.getShortName())
        log.info("rollJoints: %s"%self.i_templateNull.rollJoints)
        
        
        if self.m.mClass == 'cgmLimb':
            log.info("mode: cgmLimb Skeletonize")
            doSkeletonize(self)
        else:
            raise NotImplementedError,"haven't implemented '%s' templatizing yet"%self.m.mClass
        
@r9General.Timer
def doSkeletonize(self, stiffIndex=None):
    """ 
    DESCRIPTION:
    Basic limb skeletonizer
    
    ARGUMENTS:
    stiffIndex(int) - the index of the template objects you want to not have roll joints
                      For example, a value of -1 will let the chest portion of a spine 
                      segment be solid instead of having a roll segment. Default is the modules setting
    RETURNS:
    limbJoints(list)
    """
    log.info(">>> doSkeletonize")
    # Get our base info
    #==================	        
    assert self.cls == 'JointFactory.go',"Not a JointFactory.go instance!"
    assert mc.objExists(self.m.mNode),"module no longer exists"
    curve = self.i_curve.mNode
    partName = self.partName
    rollJoints = self.i_templateNull.rollJoints
    
    #>>> Stiff index    
    if stiffIndex is not None:
        stiffIndex = stiffIndex
    else:
        stiffIndex = self.i_templateNull.stiffIndex
        
    # Make the limb segement
    #=======================	 
    if stiffIndex == 0:#If no roll joints
        limbJoints = joints.createJointsFromCurve(curve,partName,rollJoints)
    else:
        rolledJoints = joints.createJointsFromCurve(curve,partName,rollJoints)
        if rollJoints == 0:#If no roll joints, we're done
            limbJoints = rolledJoints            
        else:
            if stiffIndex < 0:
                searchIndex = (int('%s%s' %('-',(rollJoints+1)))*abs(stiffIndex))
                toDelete = rolledJoints[searchIndex:]
                
                #>>>  delete out the roll joints we don't want
                mc.delete(toDelete[0])
                for name in toDelete:
                    rolledJoints.remove(name)
                
                #>>>  make our stiff joints 
                jointPositions = []
                if abs(stiffIndex) == 1:    
                    jointPositions.append(distance.returnClosestUPosition (self.i_templateNull.getMessage('controlObjects')[stiffIndex],curve))
                else:    
                    for obj in posTemplateObjects[stiffIndex:]:
                        jointPositions.append(distance.returnClosestUPosition (obj,curve))
                
                stiffJoints = joints.createJointsFromPosListName (jointPositions,'partName')
                
                #>>>  connect em up 
                mc.parent(stiffJoints[0],rolledJoints[-1])
                limbJoints = []
                for joint in rolledJoints:
                    limbJoints.append(joint)
                for joint in stiffJoints:
                    limbJoints.append(joint)
            
            else:
                #>>>  if it's not negative, it's positive....
                searchIndex = ((rollJoints+1)*abs(stiffIndex))
                toDelete = rolledJoints[:searchIndex]
                toKeep = rolledJoints[searchIndex:]
    
                #>>>  delete out the roll joints we don't want
                mc.parent(toKeep[0],world=True)
                mc.delete(toDelete[0])
                for name in toDelete:
                    rolledJoints.remove(name)
                
                #>>>  make our stiff joints 
                jointPositions = []
                if abs(stiffIndex) == 1:    
                    jointPositions.append(distance.returnClosestUPosition (self.i_templateNull.getMessage('controlObjects')[stiffIndex-1],curve))
                else:
                    for obj in posTemplateObjects[:stiffIndex]:
                        jointPositions.append(distance.returnClosestUPosition (obj,curve))
                
                stiffJoints = joints.createJointsFromPosListName (jointPositions,'partName')
                
                #>>>  connect em up 
                mc.parent(rolledJoints[0],stiffJoints[-1])
                limbJoints = []
                for joint in stiffJoints:
                    limbJoints.append(joint)
                for joint in rolledJoints:
                    limbJoints.append(joint)
                    
    return            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Naming
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    Copy naming information from template objects to the joints closest to them
    copy over a cgmNameModifier tag from the module first
    """
    attributes.copyUserAttrs(moduleNull,limbJoints[0],attrsToCopy=['cgmNameModifier'])
    
    """
    First we need to find our matches
    """
    for obj in posTemplateObjects:
        closestJoint = distance.returnClosestObject(obj,limbJoints)
        transferObj = attributes.returnMessageObject(obj,'cgmName')
        """Then we copy it"""
        attributes.copyUserAttrs(transferObj,closestJoint,attrsToCopy=['cgmNameModifier','cgmDirection','cgmName'])
    
    limbJointsBuffer = NameFactory.doRenameHeir(limbJoints[0])
    limbJoints = []
    limbJoints.append(limbJointsBuffer[0])
    for joint in limbJointsBuffer[1]:
        limbJoints.append(joint)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    #>>> Orientation    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    limbJoints = orientSegment(limbJoints,posTemplateObjects,jointOrientation)
     
    #>>> Set its radius and toggle axis visbility on
    #averageDistance = distance.returnAverageDistanceBetweenObjects (limbJoints)
    jointSize = (distance.returnDistanceBetweenObjects (limbJoints[0],limbJoints[-1])/6)
    for jnt in limbJoints:
        mc.setAttr ((jnt+'.radi'),jointSize*.2)
        #>>>>>>> TEMP
        joints.toggleJntLocalAxisDisplay (jnt)     
    
    print 'to orientation'
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    #>>> Storing data    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    skinJointsNull = modules.returnInfoTypeNull(moduleNull,'skinJoints')
    skinJointsNullData = attributes.returnUserAttrsToList(skinJointsNull)
    existingSkinJoints = lists.removeMatchedIndexEntries(skinJointsNullData,'cgm')
    print existingSkinJoints
    if len(existingSkinJoints) > 0:
        for entry in existingSkinJoints:
            attrBuffer = (skinJointsNull+'.'+entry[0])
            print attrBuffer
            attributes.doDeleteAttr(skinJointsNull,entry[0])
            
    
    for i in range(len(limbJoints)):
        buffer = ('%s%s' % ('joint_',i))
        attributes.storeInfo(skinJointsNull,buffer,limbJoints[i])
                
        
        
    return limbJoints    
    if stiffIndex == 0:#If no roll joints 
        limbJoints = joints.createJointsFromCurve(curve,partName,rollJoints)
    else:          
        rolledJoints = joints.createJointsFromCurve(curve,partName,rollJoints)
        if rollJoints == 0:
            limbJoints = rolledJoints            
        else:
            if stiffIndex < 0:
                """ Get our to delete number in a rolledJoints[-4:] format"""
                #searchIndex = (int('%s%s' %('-',(rollJoints+1)))*abs(stiffIndex)-1)
                searchIndex = (int('%s%s' %('-',(rollJoints+1)))*abs(stiffIndex))
                toDelete = rolledJoints[searchIndex:]
                
                """ delete out the roll joints we don't want"""
                mc.delete(toDelete[0])
                for name in toDelete:
                    rolledJoints.remove(name)
                
                """ make our stiff joints """
                jointPositions = []
                if abs(stiffIndex) == 1:    
                    jointPositions.append(distance.returnClosestUPosition (posTemplateObjects[stiffIndex],curve))
                else:    
                    for obj in posTemplateObjects[stiffIndex:]:
                        jointPositions.append(distance.returnClosestUPosition (obj,curve))
                
                stiffJoints = joints.createJointsFromPosListName (jointPositions,'partName')
                
                """ connect em up """
                mc.parent(stiffJoints[0],rolledJoints[-1])
                limbJoints = []
                for joint in rolledJoints:
                    limbJoints.append(joint)
                for joint in stiffJoints:
                    limbJoints.append(joint)
            
            else:
                """ if it's not negative, it's positive...."""
                searchIndex = ((rollJoints+1)*abs(stiffIndex))
                toDelete = rolledJoints[:searchIndex]
                toKeep = rolledJoints[searchIndex:]
    
                """ delete out the roll joints we don't want"""
                mc.parent(toKeep[0],world=True)
                mc.delete(toDelete[0])
                for name in toDelete:
                    rolledJoints.remove(name)
                
                """ make our stiff joints """
                jointPositions = []
                if abs(stiffIndex) == 1:    
                    jointPositions.append(distance.returnClosestUPosition (posTemplateObjects[stiffIndex-1],curve))
                else:
                    for obj in posTemplateObjects[:stiffIndex]:
                        jointPositions.append(distance.returnClosestUPosition (obj,curve))
                
                stiffJoints = joints.createJointsFromPosListName (jointPositions,'partName')
                
                """ connect em up """
                mc.parent(rolledJoints[0],stiffJoints[-1])
                limbJoints = []
                for joint in stiffJoints:
                    limbJoints.append(joint)
                for joint in rolledJoints:
                    limbJoints.append(joint)
                
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Naming
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    Copy naming information from template objects to the joints closest to them
    copy over a cgmNameModifier tag from the module first
    """
    attributes.copyUserAttrs(moduleNull,limbJoints[0],attrsToCopy=['cgmNameModifier'])
    
    """
    First we need to find our matches
    """
    for obj in posTemplateObjects:
        closestJoint = distance.returnClosestObject(obj,limbJoints)
        transferObj = attributes.returnMessageObject(obj,'cgmName')
        """Then we copy it"""
        attributes.copyUserAttrs(transferObj,closestJoint,attrsToCopy=['cgmNameModifier','cgmDirection','cgmName'])
    
    limbJointsBuffer = NameFactory.doRenameHeir(limbJoints[0])
    limbJoints = []
    limbJoints.append(limbJointsBuffer[0])
    for joint in limbJointsBuffer[1]:
        limbJoints.append(joint)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    #>>> Orientation    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    limbJoints = orientSegment(limbJoints,posTemplateObjects,jointOrientation)
     
    #>>> Set its radius and toggle axis visbility on
    #averageDistance = distance.returnAverageDistanceBetweenObjects (limbJoints)
    jointSize = (distance.returnDistanceBetweenObjects (limbJoints[0],limbJoints[-1])/6)
    for jnt in limbJoints:
        mc.setAttr ((jnt+'.radi'),jointSize*.2)
        #>>>>>>> TEMP
        joints.toggleJntLocalAxisDisplay (jnt)     
    
    print 'to orientation'
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    #>>> Storing data    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    skinJointsNull = modules.returnInfoTypeNull(moduleNull,'skinJoints')
    skinJointsNullData = attributes.returnUserAttrsToList(skinJointsNull)
    existingSkinJoints = lists.removeMatchedIndexEntries(skinJointsNullData,'cgm')
    print existingSkinJoints
    if len(existingSkinJoints) > 0:
        for entry in existingSkinJoints:
            attrBuffer = (skinJointsNull+'.'+entry[0])
            print attrBuffer
            attributes.doDeleteAttr(skinJointsNull,entry[0])
            
    
    for i in range(len(limbJoints)):
        buffer = ('%s%s' % ('joint_',i))
        attributes.storeInfo(skinJointsNull,buffer,limbJoints[i])
                
        
        
    return limbJoints

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> OLD stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Module tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
def skeletonizeCharacter(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Skeletonizes a character
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    modules = modules.returnModules(masterNull)
    orderedModules = modules.returnOrderedModules(modules)
    #>>> Do the spine first
    stateCheck = modules.moduleStateCheck(orderedModules[0],['template'])
    if stateCheck == 1:
        spineJoints = skeletonize(orderedModules[0])
    else:
        print ('%s%s' % (module,' has already been skeletonized. Moving on...'))
    
    #>>> Do the rest
    for module in orderedModules[1:]:
        stateCheck = modules.moduleStateCheck(module,['template'])
        if stateCheck == 1:
            templateNull = modules.returnTemplateNull(module)
            root =  modules.returnInfoNullObjects(module,'templatePosObjects',types='templateRoot')
            
            #>>> See if our item has a non default anchor
            anchored = storeTemplateRootParent(module) 
            if anchored == True:
                anchor =  attributes.returnMessageObject(root[0],'skeletonParent')
                closestJoint = distance.returnClosestObject(anchor,spineJoints)
            else:
                closestJoint = distance.returnClosestObject(root[0],spineJoints) 
        
            limbJoints = skeletonize(module)
            rootName = rigging.doParentReturnName(limbJoints[0],closestJoint)
            print rootName
        else:
            print ('%s%s' % (module,' has already been skeletonized. Moving on...'))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def skeletonStoreCharacter(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    stores a skeleton of a character
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    modules = modules.returnModules(masterNull)
    orderedModules = modules.returnOrderedModules(modules)
    #>>> Do the spine first
    stateCheck = modules.moduleStateCheck(orderedModules[0],['template'])
    if stateCheck == 1:
        spineJoints = modules.saveTemplateToModule(orderedModules[0])
    else:
        print ('%s%s' % (module,' has already been skeletonized. Moving on...'))
    
    #>>> Do the rest
    for module in orderedModules[1:]:
        stateCheck = modules.moduleStateCheck(module,['template'])
        if stateCheck == 1:
            templateNull = modules.returnTemplateNull(module)        
            modules.saveTemplateToModule(module)
        else:
            print ('%s%s' % (module,' has already been skeletonized. Moving on...'))

       
         
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>            

def storeTemplateRootParent(moduleNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Stores the template root parent to the root control if there is a new one
    
    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    templateNull = modules.returnTemplateNull(moduleNull)
    root =   modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateRoot')
    parent = search.returnParentObject(root, False)
    if parent != templateNull:
        if parent != False:
            attributes.storeObjectToMessage(parent,root,'skeletonParent')
            return True
    return False


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Skeletonize tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
def skeletonize(moduleNull, stiffIndex=0):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Basic limb skeletonizer
    
    ARGUMENTS:
    moduleNull(string)
    stiffIndex(int) - the index of the template objects you want to not have roll joints
                      For example, a value of -1 will let the chest portion of a spine 
                      segment be solid instead of having a roll segment. Default is '0'
                      which will put roll joints in every segment
    
    RETURNS:
    limbJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>>Get our info
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    partName = NameFactory.returnUniqueGeneratedName(moduleNull, ignore = 'cgmType')
    
    """ template null """
    templateNull = modules.returnTemplateNull(moduleNull)
    templateNullData = attributes.returnUserAttrsToDict (templateNull)
    
    
    """ template object nulls """
    templatePosObjectsInfoNull = modules.returnInfoTypeNull(moduleNull,'templatePosObjects')
    templateControlObjectsNull = modules.returnInfoTypeNull(moduleNull,'templateControlObjects')
    templatePosObjectsInfoData = attributes.returnUserAttrsToDict (templatePosObjectsInfoNull)
    templateControlObjectsData = attributes.returnUserAttrsToDict (templateControlObjectsNull)

    jointOrientation = modules.returnSettingsData('jointOrientation')
    moduleRootBuffer =  modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateRoot')
    moduleRoot =  moduleRootBuffer[0]
    stiffIndex = templateNullData.get('stiffIndex')
    rollJoints = templateNullData.get('rollJoints')

    """ AutonameStuff """
    divider = NameFactory.returnCGMDivider()
    skinJointsNull = modules.returnInfoTypeNull(moduleNull,'skinJoints')
    
    templateObjects = []
    coreNamesArray = [] 
    
    #>>>TemplateInfo
    for key in templatePosObjectsInfoData.keys():
        if (mc.attributeQuery (key,node=templatePosObjectsInfoNull,msg=True)) == True:
            templateObjects.append (templatePosObjectsInfoData[key])
        coreNamesArray.append (key)
    
    posTemplateObjects = []
    """ Get the positional template objects"""
    for obj in templateObjects:
        bufferList = obj.split(divider)
        if (typesDictionary.get('templateObject')) in bufferList:
            posTemplateObjects.append(obj+divider+typesDictionary.get('locator'))
    
    """put objects in order of closeness to root"""
    posTemplateObjects = distance.returnDistanceSortedList(moduleRoot,posTemplateObjects)
    curve = (templatePosObjectsInfoData['curve'])
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Actually making the skeleton with consideration for roll joints and the stiffIndex!
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if stiffIndex == 0:
        """ If no roll joints """
        limbJoints = joints.createJointsFromCurve(curve,partName,rollJoints)
    else:          
        rolledJoints = joints.createJointsFromCurve(curve,partName,rollJoints)
        if rollJoints == 0:
            limbJoints = rolledJoints            
        else:
            if stiffIndex < 0:
                """ Get our to delete number in a rolledJoints[-4:] format"""
                #searchIndex = (int('%s%s' %('-',(rollJoints+1)))*abs(stiffIndex)-1)
                searchIndex = (int('%s%s' %('-',(rollJoints+1)))*abs(stiffIndex))
                toDelete = rolledJoints[searchIndex:]
                
                """ delete out the roll joints we don't want"""
                mc.delete(toDelete[0])
                for name in toDelete:
                    rolledJoints.remove(name)
                
                """ make our stiff joints """
                jointPositions = []
                if abs(stiffIndex) == 1:    
                    jointPositions.append(distance.returnClosestUPosition (posTemplateObjects[stiffIndex],curve))
                else:    
                    for obj in posTemplateObjects[stiffIndex:]:
                        jointPositions.append(distance.returnClosestUPosition (obj,curve))
                
                stiffJoints = joints.createJointsFromPosListName (jointPositions,'partName')
                
                """ connect em up """
                mc.parent(stiffJoints[0],rolledJoints[-1])
                limbJoints = []
                for joint in rolledJoints:
                    limbJoints.append(joint)
                for joint in stiffJoints:
                    limbJoints.append(joint)
            
            else:
                """ if it's not negative, it's positive...."""
                searchIndex = ((rollJoints+1)*abs(stiffIndex))
                toDelete = rolledJoints[:searchIndex]
                toKeep = rolledJoints[searchIndex:]
    
                """ delete out the roll joints we don't want"""
                mc.parent(toKeep[0],world=True)
                mc.delete(toDelete[0])
                for name in toDelete:
                    rolledJoints.remove(name)
                
                """ make our stiff joints """
                jointPositions = []
                if abs(stiffIndex) == 1:    
                    jointPositions.append(distance.returnClosestUPosition (posTemplateObjects[stiffIndex-1],curve))
                else:
                    for obj in posTemplateObjects[:stiffIndex]:
                        jointPositions.append(distance.returnClosestUPosition (obj,curve))
                
                stiffJoints = joints.createJointsFromPosListName (jointPositions,'partName')
                
                """ connect em up """
                mc.parent(rolledJoints[0],stiffJoints[-1])
                limbJoints = []
                for joint in stiffJoints:
                    limbJoints.append(joint)
                for joint in rolledJoints:
                    limbJoints.append(joint)
                
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Naming
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    Copy naming information from template objects to the joints closest to them
    copy over a cgmNameModifier tag from the module first
    """
    attributes.copyUserAttrs(moduleNull,limbJoints[0],attrsToCopy=['cgmNameModifier'])
    
    """
    First we need to find our matches
    """
    for obj in posTemplateObjects:
        closestJoint = distance.returnClosestObject(obj,limbJoints)
        transferObj = attributes.returnMessageObject(obj,'cgmName')
        """Then we copy it"""
        attributes.copyUserAttrs(transferObj,closestJoint,attrsToCopy=['cgmNameModifier','cgmDirection','cgmName'])
    
    limbJointsBuffer = NameFactory.doRenameHeir(limbJoints[0])
    limbJoints = []
    limbJoints.append(limbJointsBuffer[0])
    for joint in limbJointsBuffer[1]:
        limbJoints.append(joint)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    #>>> Orientation    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    limbJoints = orientSegment(limbJoints,posTemplateObjects,jointOrientation)
     
    #>>> Set its radius and toggle axis visbility on
    #averageDistance = distance.returnAverageDistanceBetweenObjects (limbJoints)
    jointSize = (distance.returnDistanceBetweenObjects (limbJoints[0],limbJoints[-1])/6)
    for jnt in limbJoints:
        mc.setAttr ((jnt+'.radi'),jointSize*.2)
        #>>>>>>> TEMP
        joints.toggleJntLocalAxisDisplay (jnt)     
    
    print 'to orientation'
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    #>>> Storing data    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    skinJointsNull = modules.returnInfoTypeNull(moduleNull,'skinJoints')
    skinJointsNullData = attributes.returnUserAttrsToList(skinJointsNull)
    existingSkinJoints = lists.removeMatchedIndexEntries(skinJointsNullData,'cgm')
    print existingSkinJoints
    if len(existingSkinJoints) > 0:
        for entry in existingSkinJoints:
            attrBuffer = (skinJointsNull+'.'+entry[0])
            print attrBuffer
            attributes.doDeleteAttr(skinJointsNull,entry[0])
            
    
    for i in range(len(limbJoints)):
        buffer = ('%s%s' % ('joint_',i))
        attributes.storeInfo(skinJointsNull,buffer,limbJoints[i])
                
        
        
    return limbJoints

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
#>>> Tools    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def orientSegment(limbJoints,posTemplateObjects,orientation):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Basic limb skeletonizer
    
    ARGUMENTS:
    limbJoints(list)
    templeateObjects(list)
    orientation(string) - ['xyz','yzx','zxy','xzy','yxz','zyx']
    
    RETURNS:
    limbJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """  
    """ orientation vectors"""
    orientationVectors = search.returnAimUpOutVectorsFromOrientation(orientation)
    wantedAimVector = orientationVectors[0]
    wantedUpVector = orientationVectors[1]    
    
    """put objects in order of closeness to root"""
    limbJoints = distance.returnDistanceSortedList(limbJoints[0],limbJoints)
    
    #>>> Segment our joint list by names
    jointSegmentsList = []
    cullList = []
    """ gonna be culling items from the list so need to rebuild it, just doing a list1 = list2 
    somehow keeps the relationship....odd """
    for obj in limbJoints:
        cullList.append(obj)
    
    while len(cullList) > 0:
        matchTerm = search.returnTagInfo(cullList[0],'cgmName')
        objSet = search.returnMatchedTagsFromObjectList(cullList,'cgmName',matchTerm)
        jointSegmentsList.append(objSet)
        for obj in objSet:
            cullList.remove(obj)
            
    #>>> get our orientation helpers
    helperObjects = []
    for obj in posTemplateObjects:
        templateObj = attributes.returnMessageObject(obj,'cgmName')
        helperObjects.append(attributes.returnMessageObject(templateObj,'orientHelper'))
    
    #>>> un parenting the chain
    for joint in limbJoints[1:]:
        mc.parent(joint,world=True)
    
    #>>>per segment stuff
    cnt = 0
    for segment in jointSegmentsList:
        if len(segment) > 1:
            """ creat our up object from from the helper object """
            helperObjectCurvesShapes =  mc.listRelatives(helperObjects[cnt],shapes=True)
            upLoc = locators.locMeCvFromCvIndex(helperObjectCurvesShapes[0],30)
            print upLoc
            """ make a pair list"""
            pairList = lists.parseListToPairs(segment)
            for pair in pairList:
                """ set up constraints """
                constraintBuffer = mc.aimConstraint(pair[1],pair[0],maintainOffset = False, weight = 1, aimVector = wantedAimVector, upVector = wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
                mc.delete(constraintBuffer[0])
            for obj in segment[-1:]:
                constraintBuffer = mc.orientConstraint(segment[-2],obj,maintainOffset = False, weight = 1)
                mc.delete(constraintBuffer[0])
            """ increment and delete the up loc """
            cnt+=1
            mc.delete(upLoc)
        else:
            helperObjectCurvesShapes =  mc.listRelatives(helperObjects[cnt],shapes=True)
            upLoc = locators.locMeCvFromCvIndex(helperObjectCurvesShapes[0],30)
            """ make an aim object """
            aimLoc = locators.locMeObject(helperObjects[cnt])
            aimLocGroup = rigging.groupMeObject(aimLoc)
            mc.move (10,0,0, aimLoc, localSpace=True)
            constraintBuffer = mc.aimConstraint(aimLoc,segment[0],maintainOffset = False, weight = 1, aimVector = wantedAimVector, upVector = wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
            mc.delete(constraintBuffer[0])
            mc.delete(aimLocGroup)
            mc.delete(upLoc)
            cnt+=1
    #>>>reconnect the joints
    pairList = lists.parseListToPairs(limbJoints)
    for pair in pairList:
        mc.parent(pair[1],pair[0])
        
    """ Freeze the rotations """
    mc.makeIdentity(limbJoints[0],apply=True,r=True)
    return limbJoints



@r9General.Timer
def template(self):
    log.info(">>> functionname")
    assert self.cls == 'JointFactory.go',"Not a TemlateFactory.go instance!"
    assert mc.objExists(self.m.mNode),"module no longer exists"

    return 10 