#=================================================================================================================================================
#=================================================================================================================================================
#	rigging - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for the widgety magic of rigging
#
# REQUIRES:
# 	Maya
#   distance
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#
# FUNCTION KEY:
#   1) locMe - creates locators at the pivots of every object selected - matching translation, rotation and rotation order
#   2) locMeObject (obj) - return name of locator created
#   3) setRotationOrderObj (obj, ro)
#   4) doSetLockHideKeyableAttr (obj,lock,visible,keyable,channels) - Pass an oject, True/False for locking it,
#       True/False for visible in channel box, and which channels you want locked in ('tx','ty',etc) form
#   5) groupMe() - Pass selection into it and return locators placed at the pivots of each object - matching translation, rotation and rotation order
#   6) groupMeObject(obj) - Pass object into it and return locators placed at the pivots of each object - matching translation, rotation and rotation order
#
# 3/4/2011 - added point, orient, parent snap functions as well as the list to heirarchy one
#=================================================================================================================================================
import maya.cmds as mc
import maya.mel as mel

from cgm.lib import search
from cgm.lib import attributes
from cgm.lib import autoname
from cgm.lib import lists

# Maya version check
mayaVersion = int( mel.eval( 'getApplicationVersionAsFloat' ) )

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Geo stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import maya.cmds as mc




#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Pivot Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def copyPivot(obj,sourceObject):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Basic Pivot copy

    REQUIRES:
    obj(string) - object to affect
    sourceObject(string) - the object to copy the pivot from

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    pos = mc.xform(sourceObject, q=True, ws=True, rp = True)
    mc.xform(obj,ws=True,piv = pos)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Locator Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeObjectStandAlone(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass  an object into it and return locator placed at the pivots -
    matching translation, rotation and rotation order

    REQUIRES:
    obj(string)

    RETURNS:
    name(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """pass  an object into it and get locator placed at the pivots - matching translation, rotation and rotation order"""
    rotationOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}
    """get stuff to transfer"""
    objTrans = mc.xform (obj, q=True, ws=True, sp=True)
    objRot = mc.xform (obj, q=True, ws=True, ro=True)
    objRoo = mc.xform (obj, q=True, roo=True )
    """get rotation order"""
    correctRo = rotationOrderDictionary[objRoo]
    wantedName = (obj + '_loc')
    cnt = 1
    while mc.objExists(wantedName) == True:
        wantedName = ('%s%s%s%i' % (obj,'_','loc_',cnt))
        cnt +=1
    actualName = mc.spaceLocator (n= wantedName)

    """ account for multipleNamed things """
    if '|' in list(obj):
        locatorName = ('|'+actualName[0])
    else:
        locatorName = actualName[0]


    mc.move (objTrans[0],objTrans[1],objTrans[2], locatorName)
    mc.setAttr ((locatorName+'.rotateOrder'), correctRo)
    mc.rotate (objRot[0], objRot[1], objRot[2], locatorName, ws=True)

    return locatorName




#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Parent Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doParentToWorld(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents an object to the world

    REQUIRES:
    objList(list)

    RETURNS:
    obj(string) - new name if parented to world
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    parents = search.returnParentObject(obj)
    print parents
    if parents != False:
        returnBuffer = mc.parent(obj,world = True)
        return returnBuffer[0]
    else:
        return obj

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def doParentReturnName(obj,parentObj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the items in a list to eachother heirarchally where list[0] is the root

    REQUIRES:
    objList(list)

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    parentChildren = search.returnChildrenObjects(parentObj)
    if parentChildren != None:
        if obj in parentChildren:
            return False
        else:
            returnBuffer = mc.parent(obj,parentObj)
            return returnBuffer[0]
    else:
        returnBuffer = mc.parent(obj,parentObj)
        return returnBuffer[0]
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def parentListToHeirarchy(objList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the items in a list to eachother heirarchally where list[0] is the root

    REQUIRES:
    objList(list)

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    cnt = (len(objList) - 1)
    firstTerm = 0
    secondTerm = 1
    while cnt > 0:
        mc.parent(objList[secondTerm],objList[firstTerm])
        firstTerm +=1
        secondTerm +=1
        cnt -= 1
        if (cnt == 0):
            break
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Mirror Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def moveMirrorPosObj(obj,targetObj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Attempts to mirror an objects position and rotation

    REQUIRES:
    obj(string)
    targetObj(string)

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objTrans = mc.xform (targetObj, q=True, ws=True, sp=True)
    actualName = mc.spaceLocator ()
    if objTrans[0] > 0:
        mc.xform (actualName[0],translation = [-objTrans[0],objTrans[1],objTrans[2]], ws=True)
        objTrans = mc.xform (actualName[0], q=True, ws=True, sp=True)
        mc.move (objTrans[0],objTrans[1],objTrans[2], [obj])
    else:
        mc.xform (actualName[0],translation = [objTrans[0],objTrans[1],objTrans[2]], a=True)
        objTrans = mc.xform (actualName[0], q=True, ws=True, sp=True)
        mc.move (-objTrans[0],objTrans[1],objTrans[2], [obj])
    mc.delete (actualName[0])
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def moveMirrorPosObjNow ():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Attempts to mirror an objects position and rotation from a first to
    a second object position

    REQUIRES:
    obj(string)
    targetObj(string)

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objs = (mc.ls (sl=True))
    if not len(objs)==2:
        print ('Need two objects please.Only two.')
    else:
        moveMirrorPosObj (objs[0],objs[1])
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>





#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Group Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def groupMe():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass selection into it and return groups placed at the pivots of each
    object - matching translation, rotation and rotation order and grouping
    the object to them

    REQUIRES:
    Selection

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """pass selection into it and return groups placed at the pivots of each object - matching translation, rotation and rotation order and grouping the object to them"""
    placeObjs = []
    placeObjs = (mc.ls (sl=True))
    returnBuffer = []
    for obj in placeObjs:
        buffer = groupMeObject(obj,True)
        returnBuffer.append(buffer)
        print (buffer+' created')
    return returnBuffer
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def groupMeObject(obj,parent=True,maintainParent=False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass  an object into it and return group placed at the pivots -
    matching translation, rotation and rotation order and grouping
    it under the grp

    REQUIRES:
    obj(string)
    parent(bool) - Whether to parent the object to the group

    RETURNS:
    groupName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if maintainParent == True:
        oldParent = mc.listRelatives(obj,parent=True)
    returnBuffer = []
    rotationOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}
    """return stuff to transfer"""
    objTrans = mc.xform (obj, q=True, ws=True, sp=True)
    objRot = mc.xform (obj, q=True, ws=True, ro=True)
    objRoo = mc.xform (obj, q=True, roo=True )
    """return rotation order"""
    correctRo = rotationOrderDictionary[objRoo]
    createBuffer = mc.group (w=True, empty=True)
    newName = autoname.doNameObject(createBuffer)
    mc.setAttr ((newName+'.rotateOrder'), correctRo)
    mc.move (objTrans[0],objTrans[1],objTrans[2], [newName])
    mc.rotate (objRot[0], objRot[1], objRot[2], [newName], ws=True)
    mc.xform (newName, cp=True)

    if maintainParent == True:
        newName = doParentReturnName(newName,oldParent)
    if parent == True:
        obj = doParentReturnName(obj,newName)

    newName = autoname.doNameObject(newName)


    return newName

def zeroTransformMeObject(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Makes sure an object is zeroed out, parents the zero group back to the original objects parent

    REQUIRES:
    obj(string)

    RETURNS:
    groupName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    parent = mc.listRelatives(obj,parent=True)
    if parent != None:
        group = groupMeObject(obj,True,True)
        mc.makeIdentity(obj,apply=True,scale =True)
        attributes.storeInfo(group,'cgmTypeModifier','zero')
        return autoname.doNameObject(group)
    else:
        return groupMeObject(obj,True)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


