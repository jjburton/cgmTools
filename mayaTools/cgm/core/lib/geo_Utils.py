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
from cgm.core.lib import selection_Utils as cgmSELECT
from cgm.core.cgmPy import OM_Utils as cgmOM
from cgm.lib import guiFactory
from cgm.core.lib import rayCaster as cgmRAYS
import re

from cgm.lib import search

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

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

def get_contained(sourceObj= None, targets = None, mode = 0, returnMode = 0, selectReturn = True,
                  expandBy = None, expandAmount = 0):
    """
    Method for checking targets componeents or entirty are within a source object.

    :parameters:
        sourceObj(str): Object to check against
        targets(list): list of objects to check
        mode(int):search by
           0: rayCast interior
           1: bounding box -- THIS IS MUCH FASTER
        returnMode(int):Data to return 
           0:obj
           1:face
           2:edge
           3:verts/cv
        selectReturn(bool): whether to select the return or not
        expandBy(str): None
                       expandSelection: uses polyTraverse to grow selection
                       softSelect: use softSelection with linear falloff by the expandAmount Distance
        expandAmount(float/int): amount to expand

    :returns
        list items matching conditions
        
    :acknowledgements
    http://forums.cgsociety.org/archive/index.php?t-904223.html
    http://maya-tricks.blogspot.com/2009/04/python.html -- idea of raycasting to resolve if in interior of object
    http://forums.cgsociety.org/archive/index.php?t-1065459.html
    
    :TODO
    Only works with mesh currently
    """      
    __l_returnModes = ['obj/transform','face','edge/span','vert/cv']
    __l_modes = ['raycast interior','bounding box']
    __l_expandBy = [None, 'expandSelection','softSelect']
    result = []
    
    _mode = cgmValid.valueArg(mode, inRange=[0,1], noneValid=False, calledFrom = 'get_contained')    
    log.info("mode: {0}".format(_mode))
    
    _returnMode = cgmValid.valueArg(returnMode, inRange=[0,3], noneValid=False, calledFrom = 'get_contained')
    log.info("returnMode: {0}".format(_returnMode))
    
    _selectReturn = cgmValid.boolArg(selectReturn, calledFrom='get_contained')
    
    _expandBy = None
    if expandBy is not None:
        if expandBy in __l_expandBy:
            _expandBy = expandBy
        else:
            raise ValueError,"'{0}' expandBy arg not found in : {1}".format(expandBy, __l_expandBy)
        
    #Get our objects if we don't have them
    if sourceObj is None and targets is None:
        _sel = mc.ls(sl=True)
        sourceObj = _sel[0]
        targets = _sel[1:]

    targets = cgmValid.listArg(targets)#...Validate our targets as a list
    l_targetCounts = []
    
    for o in targets:
        _d = cgmValid.MeshDict(o)
        l_targetCounts.append(_d['pointCountPerShape'][0])
        
    sel = OM.MSelectionList()#..make selection list
    for i,o in enumerate([sourceObj] + targets):
        try:
            sel.add(o)#...add objs
        except Exception,err:   
            raise Exception,"{0} fail. {1}".format(o,err)

    _dagPath = OM.MDagPath()#...mesh path holder
    matching = []#...our match holder
    _l_found = OM.MSelectionList()#...new list for found matches
    
    guiFactory.doProgressWindow(winName='get_contained', 
                                statusMessage='Progress...', 
                                startingProgress=1, 
                                interruptableState=True)
    if _mode is 1:
        log.info('bounding box mode...')        
        try:#Get our source bb info
            sel.getDagPath(0,_dagPath)
            fnMesh_source = OM.MFnMesh(_dagPath)
            matrix_source = OM.MMatrix(_dagPath.inclusiveMatrix())    
            
            bb_source = fnMesh_source.boundingBox()
            bb_source.transformUsing(matrix_source) 
                
            sel.remove(0)#...remove the source
            
        except Exception,err:
            raise Exception,"Source validation fail | {0}".format(err)
       
        for i in xrange(sel.length()):
            _tar = targets[i]
            _vtxCount = l_targetCounts[i]
            log.info("Checking '{0}'".format(_tar))
            
            guiFactory.doUpdateProgressWindow("Checking {0}".format(_tar), i, 
                                              sel.length(), 
                                              reportItem=False)
            
            sel.getDagPath(i, _dagPath)#...get the target 
            
            fnMesh_target = OM.MFnMesh(_dagPath)#...get the FnMesh for the target
            fnMesh_target.setObject(_dagPath)
            pArray_target = OM.MPointArray()#...data array  
            fnMesh_target.getPoints(pArray_target)#...get comparing data
            
            matrix_target = OM.MMatrix(_dagPath.inclusiveMatrix())    
            fnMesh_target = OM.MFnMesh(_dagPath)
            bb_target = fnMesh_source.boundingBox()
            bb_target.transformUsing(matrix_target)         
            
            if bb_source.contains( cgmOM.Point(mc.xform(_tar, q=True, ws=True, t=True))) or bb_source.intersects(bb_target):
                if _returnMode is 0:#...object
                    _l_found.add(_dagPath)
                    continue
            iter = OM.MItGeometry(_dagPath)
            while not iter.isDone():
                vert = iter.position(OM.MSpace.kWorld)
                if bb_source.contains(vert):
                    _l_found.add(_dagPath, iter.currentItem())
                iter.next()                
                
    elif _mode is 0:
        log.info('Ray cast Mode...')
        sel.remove(0)#...remove the source        
        for i in xrange(sel.length()):
            _tar = targets[i]
            _vtxCount = l_targetCounts[i]            
            log.info("Checking '{0}'".format(_tar))
            sel.getDagPath(i, _dagPath)#...get the target 
            fnMesh_target = OM.MFnMesh(_dagPath)#...get the FnMesh for the target
            fnMesh_target.setObject(_dagPath)
            
            guiFactory.doUpdateProgressWindow("Checking {0}".format(_tar), i, 
                                              sel.length(), 
                                              reportItem=False)
            
            iter = OM.MItGeometry(_dagPath)
            _cnt = 0            
            if _returnMode is 0:#...if the object intersects
                _found = False
                while not iter.isDone():
                    guiFactory.doUpdateProgressWindow("Checking vtx[{0}]".format(_cnt), _cnt, 
                                                      _vtxCount, 
                                                      reportItem=False)          
                    _cnt +=1
                    vert = iter.position(OM.MSpace.kWorld)
                    _inside = True                           
                    for v in cgmValid.d_stringToVector.itervalues():
                        d_return = cgmRAYS.findMeshIntersection(sourceObj, vert, 
                                                                v, 
                                                                maxDistance=10000, 
                                                                tolerance=.1)
                        if not d_return.get('hit'):#...if we miss once, it's not inside
                            _inside = False
                    if _inside:
                        _l_found.add(_dagPath)
                        _found = True
                    iter.next()                              
            else:#...vert/edge/face mode...
                while not iter.isDone():
                    guiFactory.doUpdateProgressWindow("Checking vtx[{0}]".format(_cnt), _cnt,  
                                                      _vtxCount, 
                                                      reportItem=False)          
                    _cnt +=1                    
                    vert = iter.position(OM.MSpace.kWorld)
                    _good = True                           
                    p = cgmOM.Point(vert)
                    for v in cgmValid.d_stringToVector.itervalues():
                        d_return = cgmRAYS.findMeshIntersection(sourceObj, vert, 
                                                                v, 
                                                                maxDistance=10000, 
                                                                tolerance=.1)
                        if not d_return.get('hit'):#...if we miss once, it's not inside
                            _good = False
                    if _good:
                        _l_found.add(_dagPath, iter.currentItem())
                    iter.next()  
                
    guiFactory.doCloseProgressWindow()
    
    #Post processing =============================================================================
    _l_found.getSelectionStrings(matching)#...push data to strings    
    log.info("Found {0} vers contained...".format(len(matching)))
    
    #Expand ========================================================================================
    if _expandBy is not None and returnMode > 0:
        log.info("Expanding result by '{0}'...".format(_expandBy))   
        _sel = mc.ls(sl=True) or []        
        _expandFactor = int(expandAmount)  
        mc.select(matching)        
        if _expandBy is 'expandSelection':
            for i in range(_expandFactor):
                mel.eval("PolySelectTraverse 1;")
            matching = mc.ls(sl = True)
        if _expandBy is 'softSelect':
            mc.softSelect(softSelectEnabled=True,ssc='1,0,0,0,1,2', softSelectFalloff = 1, softSelectDistance = _expandFactor)
            matching = cgmSELECT.get_softSelectionItems()   
            mc.softSelect(softSelectEnabled=False)
        #if _sel:mc.select(_sel)   

    if _returnMode > 0 and _returnMode is not 3 and matching:#...need to convert
        log.info("Return conversion necessary")
        if _returnMode is 1:#...face
            matching = mc.polyListComponentConversion(matching, fv=True, tf=True, internal = True)
        elif _returnMode is 2:#...edge
            matching = mc.polyListComponentConversion(matching, fv=True, te=True, internal = True )

    if _selectReturn and matching:
        mc.select(matching)
    return matching        



