#=================================================================================================================================================
#=================================================================================================================================================
#	cgmConstrainttools - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for constraint stuff
# 
# ARGUMENTS:
# 	rigging
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#=================================================================================================================================================

import maya.cmds as mc

from cgm.lib import lists
from cgm.lib import rigging
from cgm.lib import distance
from cgm.lib.classes import NameFactory 
from cgm.lib import cgmMath
from cgm.lib import search
from cgm.lib import guiFactory


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Constraint Info
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnNormalizedWeightsByDistance(obj,targets):
    """
    Returns a normalized weight set based on distance from object to targets
    
    ARGUMENTS:
    obj(string)--
    targets(string)--
    
    RETURNS:
    weights(list)--
    """
    weights = []
    distances = []
    distanceObjDict = {}
    objDistanceDict = {}
    
    for t in targets:
        buffer = distance.returnDistanceBetweenObjects(obj,t) # get the distance
        distances.append(buffer)
        distanceObjDict[buffer] = t
        objDistanceDict[t] = buffer
        
    normalizedDistances = cgmMath.normList(distances) # get normalized distances to 1
    distances.sort() #sort our distances
    normalizedDistances.sort() # sort the normalized list (should match the distance sort)
    normalizedDistances.reverse() # reverse the sort for weight values    
    
    for i,t in enumerate(targets):
        d = objDistanceDict[t] 
        index = distances.index(d)
        weights.append( normalizedDistances[index] )
    
    return weights
    

def parent(*a, **kw):
    buffer = mc.parentConstraint(*a, **kw)
    if buffer:
        returnList = []
        for c in buffer:
            returnList.append(NameFactory.doNameObject(c))
        return returnList
    else:
        return False
    
def orient(*a, **kw):
    buffer = mc.orientConstraint(*a, **kw)
    if buffer:
        returnList = []
        for c in buffer:
            returnList.append(NameFactory.doNameObject(c))
        return returnList
    else:
        return False
    
def point(*a, **kw):
    buffer = mc.pointConstraint(*a, **kw)
    if buffer:
        returnList = []
        for c in buffer:
            returnList.append(NameFactory.doNameObject(c))
        return returnList
    else:
        return False

def scale(*a, **kw):
    buffer = mc.scaleConstraint(*a, **kw)
    if buffer:
        returnList = []
        for c in buffer:
            returnList.append(NameFactory.doNameObject(c))
        return returnList
    else:
        return False
    
def aim(*a, **kw):
    buffer = mc.aimConstraint(*a, **kw)
    if buffer:
        returnList = []
        for c in buffer:
            returnList.append(NameFactory.doNameObject(c))
        return returnList
    else:
        return False



def returnObjectConstraints(object):
    buffer = mc.listRelatives(object,type='constraint')
    if buffer:
        return buffer
    else:
        guiFactory.warning('%s has no constraints' %object)

def returnConstraintTargets(constraint):
    objType = search.returnObjectType(constraint)
    targetsDict = {}
    targetList = []
    constaintCmdDict = {'parentConstraint':mc.parentConstraint,
                        'orientConstraint':mc.orientConstraint,
                        'pointConstraint':mc.pointConstraint,
                        'aimConstraint':mc.aimConstraint}
    
    if objType in constaintCmdDict.keys():
        cmd = constaintCmdDict.get(objType)
        #>>> Get targets
        targetList = cmd(constraint,q=True,targetList=True)

    if not targetList:
        guiFactory.warning('%s has no targets' %constraint)
        return False
    else:
        return targetList

def returnConstraintTargetWeights(constraint):
    objType = search.returnObjectType(constraint)
    targetsDict = {}
    targetList = []
    constaintCmdDict = {'parentConstraint':mc.parentConstraint,
                        'orientConstraint':mc.orientConstraint,
                        'pointConstraint':mc.pointConstraint,
                        'aimConstraint':mc.aimConstraint}
    
    if objType in constaintCmdDict.keys():
        cmd = constaintCmdDict.get(objType)
        aliasList = mc.parentConstraint(constraint,q=True, weightAliasList=True)
        if aliasList:
            for o in aliasList:
                targetsDict[o] = mc.getAttr(constraint+'.'+o)


    if not targetsDict:
        guiFactory.warning('%s has no targets' %constraint)
        return False
    else:
        return targetsDict


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Point/Aim
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doPointAimConstraintObjectGroup(targets,object,mode=0): 
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    ACKNOWLEDGEMENT:
    Idea for this stype of constraint setup is from http://td-matt.blogspot.com/2011/01/spine-control-rig.html
    
    DESCRIPTION:
    Groups an object and constrains that group to the other objects
    
    ARGUMENTS:
    targets(list) - should be in format of from to back with the last one being the aim object
    object(string)
    mode(int) - 0 - equal influence
                1 - distance spread
    
    RETURNS:
    group(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    returnList = []
    """ figure out which is the aim direction  """
    aimVector = locators.returnLocalAimDirection(object,targets[-1])
    upVector = locators.returnLocalUp(aimVector)
    
    """ create locators """
    locs = []
    toMake = ['point','aim','up']
    for type in toMake:
        locBuffer = locators.locMeObject(object)
        attributes.storeInfo(locBuffer,'cgmName',object)
        attributes.storeInfo(locBuffer,'cgmTypeModifier',type)
        locs.append(NameFactory.doNameObject(locBuffer))
    
    pointLoc = locs[0]
    aimLoc = locs[1]
    upLoc = locs[2]

    """ move the locators """
    mc.xform(aimLoc,t=aimVector,r=True,os=True)
    mc.xform(upLoc,t=upVector,r=True,os=True)
    
    """group constraint"""
    objGroup = rigging.groupMeObject(object,True)
    attributes.storeInfo(objGroup,'cgmName',object)
    attributes.storeInfo(objGroup,'cgmTypeModifier','follow')
    objGroup = NameFactory.doNameObject(objGroup)
    
    pointConstraintBuffer = mc.pointConstraint (pointLoc,objGroup, maintainOffset=False)
    aimConstraintBuffer = mc.aimConstraint(aimLoc,objGroup,maintainOffset = False, weight = 1, aimVector = aimVector, upVector = upVector, worldUpObject = upLoc, worldUpType = 'object' )

    """loc constraints"""
    locConstraints = []
    for loc in locs:
        parentConstraintBuffer = mc.parentConstraint (targets,loc, maintainOffset=True)
        locConstraints.append(parentConstraintBuffer[0])
    
    if mode == 1:
        distances = []
        for target in targets:
            distances.append(distance.returnDistanceBetweenObjects(target,objGroup))
        normalizedDistances = cgmMath.normList(distances)
        for constraint in locConstraints:
            targetWeights = mc.parentConstraint(constraint,q=True, weightAliasList=True)      
            cnt=1
            for value in normalizedDistances:
                mc.setAttr(('%s%s%s' % (constraint,'.',targetWeights[cnt])),value )
                cnt-=1

    returnList.append(objGroup)
    returnList.append(locs)
    return returnList
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def doSegmentAimPointConstraint(objList):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Processes a list of items to make a contstraint array
    
    ARGUMENTS:
    objList(list) - list of items to connect
    
    RETURNS:
    constraintGroups(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """       
    constraintGroups = []   
    
    if len(objList) < 3:
        return 'Not enough items to make this tool worthwhile'
    # check to see if we have at least 3 items
    if len(objList) == 3:
        print 'Three!'
        constraintGroups.append(doPointAimConstraintObjectGroup([objList[0],objList[2]],objList[1],mode=0))
    elif len(objList) == 4:
        constraintGroups.append(doPointAimConstraintObjectGroup([objList[0],objList[3]],objList[1],mode=1))
        constraintGroups.append(doPointAimConstraintObjectGroup([objList[0],objList[3]],objList[2],mode=1))
    else:
        #first get  our main sets
        mainSet = lists.returnFirstMidLastList(objList)
        constraintGroups.append(doPointAimConstraintObjectGroup([mainSet[0],mainSet[2]],mainSet[1],mode=0))
        setsToConstrain = lists.returnFactoredList(objList, 3)
        for set in setsToConstrain:
            if len(set) == 3:
                constraintGroups.append(doPointAimConstraintObjectGroup([set[0],set[2]],set[1],mode=0))
            else:
                constraintGroups.append(doPointAimConstraintObjectGroup([set[0],set[3]],set[1],mode=1))
                constraintGroups.append(doPointAimConstraintObjectGroup([set[1],set[3]],set[2],mode=1))
                

    return constraintGroups
    

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Parent Constraints
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doParentConstraintObjectGroup(targets,object,mode=0): 
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Groups an object and constrains that group to the other objects
    
    ARGUMENTS:
    targets(list)
    object(string
    mode(int) - 0 - equal influence
                1 - distance spread
    
    RETURNS:
    group(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    objGroup = rigging.groupMeObject(object,True)
    constraint = mc.parentConstraint (targets,objGroup, maintainOffset=True)
    if mode == 1:
        weights = returnNormalizedWeightsByDistance(object,targets)
        targetWeights = mc.parentConstraint(constraint,q=True, weightAliasList=True)
        for cnt,value in enumerate(weights):
            mc.setAttr(('%s%s%s' % (constraint[0],'.',targetWeights[cnt])),value )
    return objGroup

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def doLimbSegmentListParentConstraint(objList):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Processes a list of items to make a contstraint array
    
    ARGUMENTS:
    objList(list) - list of items to connect
    
    RETURNS:
    constraintGroups(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """       
    constraintGroups = []   
    
    if len(objList) < 3:
        return 'Not enough items to make this tool worthwhile'
    # check to see if we have at least 3 items
    if len(objList) == 3:        
        constraintGroups.append(doParentConstraintObjectGroup([objList[0],objList[2]],objList[1],mode=0))
    if len(objList) == 4:
        constraintGroups.append(doParentConstraintObjectGroup([objList[0],objList[3]],objList[1],mode=1))
        constraintGroups.append(doParentConstraintObjectGroup([objList[0],objList[3]],objList[2],mode=1))
    else:
        #first get  our main sets
        mainSet = lists.returnFirstMidLastList(objList)
        constraintGroups.append(doParentConstraintObjectGroup([mainSet[0],mainSet[2]],mainSet[1],mode=0))
        setsToConstrain = lists.returnFactoredList(objList, 3)
        for set in setsToConstrain:
            if len(set) == 3:
                constraintGroups.append(doParentConstraintObjectGroup([set[0],set[2]],set[1],mode=0))
            else:
                constraintGroups.append(doParentConstraintObjectGroup([set[0],set[3]],set[1],mode=1))
                constraintGroups.append(doParentConstraintObjectGroup([set[1],set[3]],set[2],mode=1))
                

    return constraintGroups
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Point Constrains
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doPointConstraintObjectGroup(targets,object,mode=0): 
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Groups an object and constrains that group to the other objects
    
    ARGUMENTS:
    targets(list)
    object(string
    mode(int) - 0 - equal influence
                1 - distance spread
    
    RETURNS:
    group(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    objGroup = rigging.groupMeObject(object,True)
    constraint = mc.pointConstraint (targets,objGroup, maintainOffset=True)
    if mode == 1:
        distances = []
        for target in targets:
            distances.append(distance.returnDistanceBetweenObjects(target,objGroup))
        normalizedDistances = cgmMath.normList(distances)
        targetWeights = mc.pointConstraint(constraint,q=True, weightAliasList=True)
        
        cnt=1
        for value in normalizedDistances:
            mc.setAttr(('%s%s%s' % (constraint[0],'.',targetWeights[cnt])),value )
            cnt-=1
    return objGroup



def doLimbSegmentListPointConstraint(objList):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Processes a list of items to make a contstraint array
    
    ARGUMENTS:
    objList(list) - list of items to connect
    
    RETURNS:
    constraintGroups(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """       
    constraintGroups = []   
    
    if len(objList) < 3:
        return 'Not enough items to make this tool worthwhile'
    # check to see if we have at least 3 items
    if len(objList) == 3:        
        constraintGroups.append(doPointConstraintObjectGroup([objList[0],objList[2]],objList[1],mode=0))
    if len(objList) == 4:
        constraintGroups.append(doPointConstraintObjectGroup([objList[0],objList[3]],objList[1],mode=1))
        constraintGroups.append(doPointConstraintObjectGroup([objList[0],objList[3]],objList[2],mode=1))
    else:
        #first get  our main sets
        mainSet = lists.returnFirstMidLastList(objList)
        constraintGroups.append(doPointConstraintObjectGroup([mainSet[0],mainSet[2]],mainSet[1],mode=0))
        setsToConstrain = lists.returnFactoredList(objList, 3)
        for set in setsToConstrain:
            if len(set) == 3:
                constraintGroups.append(doPointConstraintObjectGroup([set[0],set[2]],set[1],mode=0))
            else:
                constraintGroups.append(doPointConstraintObjectGroup([set[0],set[3]],set[1],mode=1))
                constraintGroups.append(doPointConstraintObjectGroup([set[1],set[3]],set[2],mode=1))
                

    return constraintGroups

    

