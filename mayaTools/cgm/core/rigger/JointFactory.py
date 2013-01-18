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
        self.i_rigNull = self.m.rigNull
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
        log.info("joingOrientation: %s"%self.jointOrientation)
        
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
    l_limbJoints(list)
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
        
    #>>> Make the limb segement
    #==========================	 
    if stiffIndex == 0:#If no roll joints
        l_limbJoints = joints.createJointsFromCurve(curve,partName,rollJoints)
    else:
        rolledJoints = joints.createJointsFromCurve(curve,partName,rollJoints)
        if rollJoints == 0:#If no roll joints, we're done
            l_limbJoints = rolledJoints            
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
                l_limbJoints = []
                for joint in rolledJoints:
                    l_limbJoints.append(joint)
                for joint in stiffJoints:
                    l_limbJoints.append(joint)
            
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
                l_limbJoints = []
                for joint in stiffJoints:
                    l_limbJoints.append(joint)
                for joint in rolledJoints:
                    l_limbJoints.append(joint)
                    
     

    #>>> Naming
    #=========== 
    """ 
    Copy naming information from template objects to the joints closest to them
    copy over a cgmNameModifier tag from the module first
    """
    #attributes.copyUserAttrs(moduleNull,l_limbJoints[0],attrsToCopy=['cgmNameModifier'])
    
    #>>>First we need to find our matches
    for i_obj in self.i_controlObjects:
        closestJoint = distance.returnClosestObject(i_obj.mNode,l_limbJoints)
        #transferObj = attributes.returnMessageObject(obj,'cgmName')
        """Then we copy it"""
        attributes.copyUserAttrs(i_obj.mNode,closestJoint,attrsToCopy=['cgmPosition','cgmNameModifier','cgmDirection','cgmName'])
    
    #>>>Store these joints and rename the heirarchy
    for o in l_limbJoints:
        i_o = cgmMeta.cgmObject(o)
        i_o.addAttr('mClass','cgmObject',lock=True)
    self.i_rigNull.connectChildren(l_limbJoints,'skinJoints','module')
    log.info(self.i_rigNull.skinJoints)

    l_limbJointsBuffer = NameFactory.doRenameHeir(l_limbJoints[0],True)
    

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    #>>> Orientation    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    return
    l_limbJoints = orientSegment(l_limbJoints,self.i_templateNull.getMessage('controlObjects'),self.jointOrientation)
    
    #>>> Set its radius and toggle axis visbility on
    #averageDistance = distance.returnAverageDistanceBetweenObjects (l_limbJoints)
    jointSize = (distance.returnDistanceBetweenObjects (l_limbJoints[0],l_limbJoints[-1])/6)
    for jnt in l_limbJoints:
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
            
    
    for i in range(len(l_limbJoints)):
        buffer = ('%s%s' % ('joint_',i))
        attributes.storeInfo(skinJointsNull,buffer,l_limbJoints[i])
                
        
        
    return l_limbJoints 
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> OLD stuff
def doOrientSegment(self):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Basic limb skeletonizer
    
    ARGUMENTS:
    l_limbJoints(list)
    templeateObjects(list)
    orientation(string) - ['xyz','yzx','zxy','xzy','yxz','zyx']
    
    RETURNS:
    l_limbJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    log.info(">>> doOrientSegment")
    # Get our base info
    #==================	        
    assert self.cls == 'JointFactory.go',"Not a JointFactory.go instance!"
    assert mc.objExists(self.m.mNode),"module no longer exists"
    
    #>>> orientation vectors
    #=======================    
    reload(search)
    orientationVectors = search.returnAimUpOutVectorsFromOrientation(self.jointOrientation)
    wantedAimVector = orientationVectors[0]
    wantedUpVector = orientationVectors[1]    
    
    #>>> Put objects in order of closeness to root
    #l_limbJoints = distance.returnDistanceSortedList(l_limbJoints[0],l_limbJoints)
    
    #>>> Segment our joint list by cgmName, prolly a better way to optimize this
    """
    jointSegmentsList = []
    cullList = []
    cullList = copy.copy(l_limbJoints)
    
    while len(cullList) > 0:
        matchTerm = search.returnTagInfo(cullList[0],'cgmName')
        objSet = search.returnMatchedTagsFromObjectList(cullList,'cgmName',matchTerm)
        jointSegmentsList.append(objSet)
        for obj in objSet:
            cullList.remove(obj)
    """
    l_cull = copy.copy(self.i_rigNull.getMessage('skinJoints'))    
    self.l_jointSegmentIndexSets= []
    while l_cull:
        matchTerm = search.findRawTagInfo(l_cull[0],'cgmName')
        buffer = []
        objSet = search.returnMatchedTagsFromObjectList(l_cull,'cgmName',matchTerm)
        for o in objSet:
            buffer.append(self.i_rigNull.getMessage('skinJoints').index(o))
        self.l_jointSegmentIndexSets.append(buffer)
        for obj in objSet:
            l_cull.remove(obj)
    
    return self.l_jointSegmentIndexSets       
    #>>> get our orientation helpers
    """
    l_helperObjects = []
    for obj in posTemplateObjects:
        templateObj = attributes.returnMessageObject(obj,'cgmName')
        helperObjects.append(attributes.returnMessageObject(templateObj,'helper'))
    """
    
    #>>> un parenting the chain
    for joint in l_limbJoints[1:]:
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
    pairList = lists.parseListToPairs(l_limbJoints)
    for pair in pairList:
        mc.parent(pair[1],pair[0])
        
    """ Freeze the rotations """
    mc.makeIdentity(l_limbJoints[0],apply=True,r=True)
    return l_limbJoints
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
        
            l_limbJoints = skeletonize(module)
            rootName = rigging.doParentReturnName(l_limbJoints[0],closestJoint)
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
    l_limbJoints(list)
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
        l_limbJoints = joints.createJointsFromCurve(curve,partName,rollJoints)
    else:          
        rolledJoints = joints.createJointsFromCurve(curve,partName,rollJoints)
        if rollJoints == 0:
            l_limbJoints = rolledJoints            
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
                l_limbJoints = []
                for joint in rolledJoints:
                    l_limbJoints.append(joint)
                for joint in stiffJoints:
                    l_limbJoints.append(joint)
            
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
                l_limbJoints = []
                for joint in stiffJoints:
                    l_limbJoints.append(joint)
                for joint in rolledJoints:
                    l_limbJoints.append(joint)
                
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Naming
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    Copy naming information from template objects to the joints closest to them
    copy over a cgmNameModifier tag from the module first
    """
    attributes.copyUserAttrs(moduleNull,l_limbJoints[0],attrsToCopy=['cgmNameModifier'])
    
    """
    First we need to find our matches
    """
    for obj in posTemplateObjects:
        closestJoint = distance.returnClosestObject(obj,l_limbJoints)
        transferObj = attributes.returnMessageObject(obj,'cgmName')
        """Then we copy it"""
        attributes.copyUserAttrs(transferObj,closestJoint,attrsToCopy=['cgmNameModifier','cgmDirection','cgmName'])
    
    l_limbJointsBuffer = NameFactory.doRenameHeir(l_limbJoints[0])
    l_limbJoints = []
    l_limbJoints.append(l_limbJointsBuffer[0])
    for joint in l_limbJointsBuffer[1]:
        l_limbJoints.append(joint)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    #>>> Orientation    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    l_limbJoints = orientSegment(l_limbJoints,posTemplateObjects,jointOrientation)
     
    #>>> Set its radius and toggle axis visbility on
    #averageDistance = distance.returnAverageDistanceBetweenObjects (l_limbJoints)
    jointSize = (distance.returnDistanceBetweenObjects (l_limbJoints[0],l_limbJoints[-1])/6)
    for jnt in l_limbJoints:
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
            
    
    for i in range(len(l_limbJoints)):
        buffer = ('%s%s' % ('joint_',i))
        attributes.storeInfo(skinJointsNull,buffer,l_limbJoints[i])
                
        
        
    return l_limbJoints

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
#>>> Tools    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def orientSegment(l_limbJoints,posTemplateObjects,orientation):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Basic limb skeletonizer
    
    ARGUMENTS:
    l_limbJoints(list)
    templeateObjects(list)
    orientation(string) - ['xyz','yzx','zxy','xzy','yxz','zyx']
    
    RETURNS:
    l_limbJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """  
    """ orientation vectors"""
    orientationVectors = search.returnAimUpOutVectorsFromOrientation(orientation)
    wantedAimVector = orientationVectors[0]
    wantedUpVector = orientationVectors[1]    
    
    """put objects in order of closeness to root"""
    l_limbJoints = distance.returnDistanceSortedList(l_limbJoints[0],l_limbJoints)
    
    #>>> Segment our joint list by names
    jointSegmentsList = []
    cullList = []
    """ gonna be culling items from the list so need to rebuild it, just doing a list1 = list2 
    somehow keeps the relationship....odd """
    for obj in l_limbJoints:
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
    for joint in l_limbJoints[1:]:
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
    pairList = lists.parseListToPairs(l_limbJoints)
    for pair in pairList:
        mc.parent(pair[1],pair[0])
        
    """ Freeze the rotations """
    mc.makeIdentity(l_limbJoints[0],apply=True,r=True)
    return l_limbJoints



@r9General.Timer
def template(self):
    log.info(">>> functionname")
    assert self.cls == 'JointFactory.go',"Not a TemlateFactory.go instance!"
    assert mc.objExists(self.m.mNode),"module no longer exists"

    return 10 