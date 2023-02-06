#=================================================================================================================================================
#=================================================================================================================================================
#	rigging - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for the widgety magic of rigging
#
# ARGUMENTS:
# 	Maya
#   distance
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - cgmonks.info@gmail.com
#	https://github.com/jjburton/cgmTools/wiki
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
from cgm.lib.classes import NameFactory as NameFactoryOld
from cgm.lib import lists
from cgm.lib import cgmMath
from cgm.lib import names

# Maya version check
mayaVersion = int( mel.eval( 'getApplicationVersionAsFloat' ) )

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Geo stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import maya.cmds as mc


def sortChildrenByName(obj):
    _l = search.returnChildrenObjects(obj,fullPath = True)
    if not _l:
        log.error("sortChildrenByName>> No children found.")
        return False
    
    _d = {}
    for i,o in enumerate(_l):
        _bfr = names.getBaseName(o)
        if _bfr not in list(_d.keys()):
            _d[_bfr] = o
        else:
            _d[names.getShortName(o)] = o
    
    l_keys = list(_d.keys())
    l_keys.sort()
    
    for k in l_keys:
        o = _d[k]
        o = doParentToWorld(o)
        mc.parent(o,obj)
    
    return True
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Pivot Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def copyPivot(obj,sourceObject):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Basic Pivot copy

    ARGUMENTS:
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

    ARGUMENTS:
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

    ARGUMENTS:
    objList(list)

    RETURNS:
    obj(string) - new name if parented to world
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    parents = search.returnParentObject(obj)
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
    Parents an object while returning the new name as a simple string
    
    ARGUMENTS:
    obj(string)

    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #assert mc.objExists(parentObj),"Parent object doesn't exist: %s"%str(parentObj)
    if parentObj in str(mc.ls(obj,long=True)):
        return obj
    else:
        returnBuffer = mc.parent(obj,parentObj)
        return returnBuffer[0]



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def parentListToHeirarchy(objList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the items in a list to eachother heirarchally where list[0] is the root

    ARGUMENTS:
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

    ARGUMENTS:
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

    ARGUMENTS:
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

    ARGUMENTS:
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
    return returnBuffer
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def groupMeObject(obj,parent=True,maintainParent=False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass  an object into it and return group placed at the pivots -
    matching translation, rotation and rotation order and grouping
    it under the grp

    ARGUMENTS:
    obj(string)
    parent(bool) - Whether to parent the object to the group

    RETURNS:
    groupName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if maintainParent == True:
        oldParent = mc.listRelatives(obj,parent=True,fullPath = True)
        if oldParent:oldParent = oldParent[0]
    returnBuffer = []
    rotationOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}
    
    #_matrix = mc.xform (obj, q=True, m =True)
    #groupBuffer = mc.group (w=True, empty=True)    
    #mc.xform(groupBuffer, m = _matrix)    
    #mc.xform(groupBuffer,ra=[0,0,0],p=True)
    #mc.xform(groupBuffer, roo = 'xyz', p=True)#...always do pushing values in xyz 
    #objRot = mc.xform(groupBuffer, q=True, os = True, ro=True)
    #objRa = mc.xform(groupBuffer, q=True, os = True, ra=True)
    #mc.xform(groupBuffer, os = True, ra=[v + objRot[i] for i,v in enumerate(objRa)])
    #mc.xform(groupBuffer,os=True, ro = [0,0,0])#...clear    
    
    #mc.xform(groupBuffer, roo = mc.xform (obj, q=True, roo=True ), p=True)#...match rotateOrder
    
    #return stuff to transfer
    objTrans = mc.xform (obj, q=True, ws=True, rp=True)
    objRot = mc.xform (obj, q=True, ws=True, ro=True)
    objRotAxis = mc.xform(obj, q=True, ws = True, ra=True)
    
    #return rotation order
    groupBuffer = mc.group (w=True, empty=True)
    #mc.setAttr ((groupBuffer+'.rotateOrder'), correctRo)
    mc.xform(groupBuffer, roo = mc.xform (obj, q=True, roo=True ))#...match rotateOrder    
    mc.move (objTrans[0],objTrans[1],objTrans[2], [groupBuffer])
    #for i,a in enumerate(['X','Y','Z']):
        #attributes.doSetAttr(groupBuffer, 'rotateAxis{0}'.format(a), objRotAxis[i])    
    #mc.rotate(objRot[0], objRot[1], objRot[2], [groupBuffer], ws=True)
    mc.xform(groupBuffer, ws=True, ro= objRot,p=False)
    mc.xform(groupBuffer, ws=True, ra= objRotAxis,p=False)    
    
    #mc.xform (groupBuffer, cp=True)
    
    if maintainParent == True and oldParent:
        #for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
        groupBuffer = doParentReturnName(groupBuffer,oldParent)
    if parent:
        _wasLocked = []  
        for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            attrBuffer = '%s.%s'%(obj,attr)
            if mc.getAttr(attrBuffer,lock=True):
                _wasLocked.append(attr)
                mc.setAttr(attrBuffer,lock=False)                
            #attributes.doSetAttr(obj,attr,0)          
        obj = doParentReturnName(obj,groupBuffer)        
        #for attr in ['tx','ty','tz','rx','ry','rz']:
            #if attributes.doGetAttr(obj,attr):
                #attributes.doSetAttr(obj,attr,0)    
        if _wasLocked:
            for attr in _wasLocked:
                attrBuffer = '%s.%s'%(obj,attr)
                mc.setAttr(attrBuffer,lock=True)                
                
    return NameFactoryOld.doNameObject(groupBuffer,True)


def zeroTransformMeObject(obj,scaleZero=False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Makes sure an object is zeroed out, parents the zero group back to the original objects parent

    ARGUMENTS:
    obj(string)

    RETURNS:
    groupName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    parent = mc.listRelatives(obj,parent=True,fullPath = True)

    group = groupMeObject(obj,True,True)
    group2 = ''
    attributes.storeInfo(group,'cgmTypeModifier','zero')
    
    
    objScale = []
    objScale.append(mc.getAttr(obj+'.sx'))
    objScale.append(mc.getAttr(obj+'.sy'))
    objScale.append(mc.getAttr(obj+'.sz'))
    
    #Check if we got zero translates
    zeroCheck = mc.xform (obj, q=True, os=True, rp=True)
    if zeroCheck:
        if scaleZero:
            mc.makeIdentity(obj,apply=True,t=0,r=0,s=1)              
        group2 = groupMeObject(obj,True,True)
        zeroCheck = mc.xform (obj, q=True, os=True, rp=True)
        
        zeroCheck = cgmMath.multiplyLists([objScale,zeroCheck])
        mc.xform (group2,t=(-zeroCheck[0],-zeroCheck[1],-zeroCheck[2]), os=True)
        attributes.storeInfo(group,'cgmTypeModifier','zeroParent')
        attributes.storeInfo(group2,'cgmTypeModifier','zero')
        group2 = NameFactoryOld.doNameObject(group2) 
    
        for attr in 'tx','ty','tz':
            attributes.doSetAttr(obj, attr, 0)
    
    #Check for zero rotates
    rotateCheck = mc.xform(obj, q=True, os=True, ro=True)
    if rotateCheck:
        if not group2:
            group2 = groupMeObject(obj,True,True)
            attributes.storeInfo(group,'cgmTypeModifier','zeroParent')
            attributes.storeInfo(group2,'cgmTypeModifier','zero')
            NameFactoryOld.doNameObject(group2) 
        
        mc.xform (group2,ro=(rotateCheck[0],rotateCheck[1],rotateCheck[2]), os=True)
        for attr in 'rx','ry','rz':
            attributes.doSetAttr(obj, attr, 0)        
    
    """
    objScale = []
    objScale.append(mc.getAttr(obj+'.sx'))
    objScale.append(mc.getAttr(obj+'.sy'))
    objScale.append(mc.getAttr(obj+'.sz'))
    grpScale = []
    grpScale.append(mc.getAttr(group+'.sx'))
    grpScale.append(mc.getAttr(group+'.sy'))
    grpScale.append(mc.getAttr(group+'.sz'))
    multScale = cgmMath.multiplyLists([objScale,grpScale])
    
    mc.scale(multScale[0], multScale[1], multScale[2],[group])
    for attr in 'sx','sy','sz':
        attributes.doSetAttr(obj,attr,1)
    """
    return NameFactoryOld.doNameObject(group)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


