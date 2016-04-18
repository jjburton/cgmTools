#=================================================================================================================================================
#=================================================================================================================================================
#	geo - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with attributes
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
#
#   
#=================================================================================================================================================

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as OM

from cgm.core.cgmPy import validateArgs as cgmValid
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Create Tools 
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>     
def createPolyFromPosList(posList):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a poly from position list
    
    ARGUMENTS:
    posList(string) - list of positions
    
    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    polyBuffer = mc.polyCreateFacet(p = posList,hole = False)
    newFaceVerts = (mc.ls ([polyBuffer[0]+'.vtx[*]'],flatten=True))
    for vert in newFaceVerts:
        cnt = newFaceVerts.index(vert)
        pos = posList[cnt]
        mc.xform(vert,t = [pos[0],pos[1],pos[2]],ws=True)
    return polyBuffer[0]


def compare_area(sourceObj, targetList, shouldMatch = True):
    """
    Looks at the area of two pieces of geo. Most likely used for culling out unecessary blend targets that don't do anything.

    :parameters:
        sourceObj | Object to base comparison on
        targetList | List of objects to compare with
        shouldMatch | Mode with which to return data ('same' or not)

    :returns
        list of objects matching conditions
    """  
    _f_baseArea = mc.polyEvaluate(sourceObj, area = True)
    result = []
    for o in targetList:
        _f_area = mc.polyEvaluate(o, area = True)
        if shouldMatch:
            if cgmValid.isFloatEquivalent(_f_baseArea,_f_area):
                log.info("Match: {0}".format(o))
                result.append(o)
        else:
            if not cgmValid.isFloatEquivalent(_f_baseArea,_f_area):        
                log.info("Nonmatch: {0}".format(o))
                result.append(o)                     
    return result
    
def compare_points(sourceObj = None,targetList = None, shouldMatch = True):
    """
    Compares points of geo mesh. Most likely used for culling out unecessary blend targets that don't do anything.
    Can work of selection as well when no arguments are passed for source and target in a source then targets selection format.
    
    Thanks for the help: Travis Miller and Raffaele
    :parameters:
        sourceObj | Object to base comparison on
        targetList | List of objects to compare with
        shouldMatch | Mode with which to return data ('same' or not)

    :returns
        list of objects matching conditions
    """      
    result = []
    
    #Get our objects if we don't have them
    if sourceObj is None and targetList is None:
        _sel = mc.ls(sl=True)
        sourceObj = _sel[0]
        targetList = _sel[1:]
        
    #Maya OpenMaya 2.0 came in 2012 and is better but we want this to work in previous versions...
    if mel.eval('getApplicationVersionAsFloat') <2012:
        sel = OM.MSelectionList()#..make selection list
        for o in [sourceObj] + targetList:
            sel.add(o)#...add objs
    
        meshPath = OM.MDagPath()#...mesh path holder
        sel.getDagPath(0,meshPath)#...get source dag path
        fnMesh  = OM.MFnMesh(meshPath)#...fnMesh holder
        basePoints = OM.MFloatPointArray() #...data array
        fnMesh.getPoints(basePoints)#...get our data
        
        sel.remove(0)#...remove the source form our list
        
        morph = OM.MDagPath()#...dag path holder
        morphPoints = OM.MFloatPointArray()#...data array
        targets = OM.MSelectionList()#...new list for found matches
        
        for i in xrange(sel.length()):
            sel.getDagPath(i, morph)#...get the target
            fnMesh.setObject(morph)#...get it to our fnMesh obj
            fnMesh.getPoints(morphPoints)#...get comparing data
            _match = True                    
            for j in xrange(morphPoints.length()):
                if (morphPoints[j] - basePoints[j]).length() > 0.0001:#...if they're different   
                    _match = False
                    if not shouldMatch:
                        log.info("{0} doesn't match".format(morph))                                        
                        targets.add(morph)
                        break
                elif shouldMatch and j == (morphPoints.length()-1) and _match:#if we get to the end and they haven't found a mismatch
                    log.info("{0} match".format(morph))                                        
                    targets.add(morph)   
                    
        OM.MGlobal.setActiveSelectionList(targets)#select our targets
        return mc.ls(sl=True)#...return
    
    else:#We can use the new OpenMaya 2.0
        from maya.api import OpenMaya as OM2   
        
        sel = OM2.MSelectionList()#...make selection list
        for o in [sourceObj] + targetList:
            sel.add(o)#...add them to our lists        
            
        basePoints = OM2.MFnMesh(sel.getDagPath(0)).getPoints()#..base points data
        sel.remove(0)#...remove source obj
        
        count = sel.length()
        targets = OM2.MSelectionList()#...target selection list
        
        for i in xrange(count):
            comparable = OM2.MFnMesh(sel.getDagPath(i)).getPoints()#...target points data
            compareMesh = sel.getDagPath(i)#...dag path for target
            _match = True
            for ii in xrange(basePoints.__len__()):
                if (basePoints[ii] - comparable[ii]).length() > 0.0001:#...if they're different
                    _match = False
                    if not shouldMatch:
                        log.debug("'{0}' doesn't match".format(compareMesh))                         
                        targets.add(compareMesh)
                        break  
                elif shouldMatch and _match and  ii == (basePoints.__len__()-1):
                    log.debug("'{0}' match".format(compareMesh))                                                                
                    targets.add(compareMesh)                    
                
        if targets:
            OM2.MGlobal.setActiveSelectionList(targets)#...select our targets            
            result = targets.getSelectionStrings()#...get the strings
                
    return result

def is_equivalent(sourceObj = None, target = None):
    """
    Compares points of geo mesh. Most likely used for culling out unecessary blend targets that don't do anything.
    Can work of selection as well when no arguments are passed for source and target in a source then targets selection format.
    
    :parameters:
        sourceObj | Object to base comparison on
        target | List of objects to compare with

    :returns
        list of objects matching conditions
    """      
    result = []
    
    #Get our objects if we don't have them
    if sourceObj is None and target is None:
        _sel = mc.ls(sl=True)
        sourceObj = _sel[0]
        target = _sel[1]
        
    #Maya OpenMaya 2.0 came in 2012 and is better but we want this to work in previous versions...
    if mel.eval('getApplicationVersionAsFloat') <2012:
        sel = OM.MSelectionList()#..make selection list
        for o in sourceObj,target:
            sel.add(o)#...add objs
    
        meshPath = OM.MDagPath()#...mesh path holder
        sel.getDagPath(0,meshPath)#...get source dag path
        fnMesh  = OM.MFnMesh(meshPath)#...fnMesh holder
        basePoints = OM.MFloatPointArray() #...data array
        fnMesh.getPoints(basePoints)#...get our data
        
        sel.remove(0)#...remove the source form our list
        
        morph = OM.MDagPath()#...dag path holder
        morphPoints = OM.MFloatPointArray()#...data array
        targets = OM.MSelectionList()#...new list for found matches
        
        for i in xrange(sel.length()):
            sel.getDagPath(i, morph)#...get the target
            fnMesh.setObject(morph)#...get it to our fnMesh obj
            fnMesh.getPoints(morphPoints)#...get comparing data
            _match = True                    
            for j in xrange(morphPoints.length()):
                if (morphPoints[j] - basePoints[j]).length() > 0.0001:#...if they're different   
                    return False 
        return True
    
    else:#We can use the new OpenMaya 2.0
        from maya.api import OpenMaya as OM2   
        
        sel = OM2.MSelectionList()#...make selection list
        for o in sourceObj,target:
            sel.add(o)#...add them to our lists        
            
        basePoints = OM2.MFnMesh(sel.getDagPath(0)).getPoints()#..base points data
        sel.remove(0)#...remove source obj
        
        count = sel.length()
        targets = OM2.MSelectionList()#...target selection list
        
        for i in xrange(count):
            comparable = OM2.MFnMesh(sel.getDagPath(i)).getPoints()#...target points data
            compareMesh = sel.getDagPath(i)#...dag path for target
            _match = True
            for ii in xrange(basePoints.__len__()):
                if (basePoints[ii] - comparable[ii]).length() > 0.0001:#...if they're different
                    return False

    return True



