#=================================================================================================================================================
#=================================================================================================================================================
#	cgmSkeletonBuilder - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for finding stuff
# 
# ARGUMENTS:
# 	Maya
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#   0.11 - 04/04/2011 - added cvListSimplifier
#
# FUNCTION KEY:
#   1) ????
#   2) ????
#   3) ????
#   
#=================================================================================================================================================

import maya.cmds as mc
from cgm.lib import joints, rigging, attributes, names, distance, autoname , search, curves, dictionary, lists, settings, modules


import copy

typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
namesDictionary = dictionary.initializeDictionary( settings.getNamesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())

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


