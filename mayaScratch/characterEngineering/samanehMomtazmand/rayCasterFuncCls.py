from cgm.core import cgm_Meta as cgmMeta
import Red9.core.Red9_Meta as r9Meta
import maya.cmds as mc
import copy
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as om
from zooPyMaya import apiExtensions
from cgm.core import cgm_General as cgmGeneral
from cgm.lib import(locators,dictionary,cgmMath,lists,geo,distance,search)
import os
import pdb
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
    
def rayCasterSurfaceFuncCls(*args, **kws):
            
    class fncWrap(cgmGeneral.cgmFuncCls):
        '''
        This is rayCasterSurface funcCls
        '''

        def __init__(self, *args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'rayCasterSurfaceFuncCls'
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'surface',"default":'nurbsCylinder1',"argType":'str','help':"nurbs or poly surface"},
                                   {'kw':'raySource',"default":[0,0,0],"argType":'tuple','help':"point in world space"},
                                   {'kw':'rayDir',"default":[0,0,0],"argType":'tuple','help':"world space vector"},
                                   {'kw':'maxDistance', "default":1000,"argType":'float','help':"maxDistance"},
                                   {'kw':'obj',"default":'',"argType":'string','help':"object source"},
                                   {'kw':'axis',"default":'z+',"argType":'string','help':"object source axis"},
                                   {'kw':'vector',"default":False,"argType":'bool','help':"object's vector"},
                                   {'kw':'singleReturn',"default":True,"argType":'bool','help':"one intersection"},
                                   {'kw':'axisToCheck',"default":['x','z'],"argType":'list','help':"axisToCheck"},
                                   {'kw':'maxIterations',"default":10,"argType":'float','help':"maxIterations"},
                                   {'kw':'pierceDepth',"default":4,"argType":'float','help':"pierceDepth"}]
            self.__dataBind__(*args, **kws)

            surface = self.d_kws['surface']
            raySource = self.d_kws['raySource']
            rayDir = self.d_kws['rayDir']
            maxDistance = self.d_kws['maxDistance']

            self.l_funcSteps = [{'step':'findSurfaceIntersections','call':self.findSurfaceIntersections},
								{'step':'findSurfaceIntersections','call':self.findSurfaceIntersections},
								{'step':'findSurfaceIntersectionFromObjectAxis','call':self.findSurfaceIntersectionFromObjectAxis},
								{'step':'findSurfaceMidPointFromObject','call':self.findSurfaceMidPointFromObject},
								{'step':'findFurthestPointInRangeFromObject','call':self.findFurthestPointInRangeFromObject}]
            return None
        def _setup_(self):pass
        #Functions
        def findSurfaceIntersection(self):
            '''
            Return the pierced point on a surface from a raySource and rayDir
            '''
            try:
                self._str_funcName = 'findSurfaceIntersection'
                log.debug(">>> %s >> "%self._str_funcName + "="*75)
                if len(mc.ls(surface))>1:
                    raise StandardError,"findSurfaceIntersection>>> More than one surface named: %s"%surface
                
                self.centerPoint = mc.xform(surface, q=1, ws=1, t=1)
                
                #checking the type 
                self.objType = search.returnObjectType(surface)
                
                if self.objType == 'nurbsSurface':
                    raySource = om.MPoint(raySource[0], raySource[1], raySource[2])
                    self.raySourceVector = om.MVector(raySource[0], raySource[1], raySource[2])
                    self.centerPointVector = om.MVector(self.centerPoint[0],self.centerPoint[1],self.centerPoint[2])
                    rayDir = om.MPoint(self.centerPointVector - self.raySourceVector)
                    self.rayDirection = om.MVector(rayDir[0], rayDir[1], rayDir[2])
                    self.hitPoint = om.MPoint()
                    self.selectionList = om.MSelectionList()
                    self.selectionList.add(surface)
                    self.surfacePath = om.MDagPath()
                    self.selectionList.getDagPath(0, self.surfacePath)
                    self.surfaceFn = om.MFnNurbsSurface(self.surfacePath)

                    #maxDist
                    self.maxDist = maxDistance

                    #other variables 
                    self.uSU = om.MScriptUtil()
                    self.vSU = om.MScriptUtil()
                    self.uPtr = self.uSU.asDoublePtr()
                    self.vPtr = self.vSU.asDoublePtr()
                    self.spc = om.MSpace.kWorld
                    self.toleranceSU = om.MScriptUtil()
                    self.tolerance = self.toleranceSU.asDoublePtr()
                    om.MScriptUtil.setDouble(self.tolerance, .1)

                    #Get the closest intersection.
                    self.gotHit = self.surfaceFn.intersect(raySource,self.rayDirection,self.uPtr,self.vPtr,self.hitPoint,self.toleranceSU.asDouble(),self.spc,False,None,False,None)
                    
                elif self.objType == 'mesh':
                    raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])
                    self.raySourceVector = om.MFloatVector(raySource[0], raySource[1], raySource[2])
                    self.centerPointVector = om.MFloatVector(self.centerPoint[0],self.centerPoint[1],self.centerPoint[2]) 
                    rayDir = om.MFloatPoint(self.centerPointVector - self.raySourceVector)
                    self.rayDirection = om.MFloatVector(rayDir[0], rayDir[1], rayDir[2])
                    self.hitPoint = om.MFloatPoint()     
                    self.selectionList = om.MSelectionList()
                    self.selectionList.add(surface)
                    self.meshPath = om.MDagPath()
                    self.selectionList.getDagPath(0, self.meshPath)
                    self.meshFn = om.MFnMesh(self.meshPath)

                    #maxDist
                    self.maxDist = maxDistance

                    #other variables 
                    self.spc = om.MSpace.kWorld

                    #Get the closest intersection.
                    self.gotHit = self.meshFn.closestIntersection(raySource,self.rayDirection,None,None,False,self.spc,self.maxDist,False,None,self.hitPoint,None,None,None,None,None)
                    
                else : raise StandardError,"wrong surface type!"
                    
                #Return the intersection as a Python list.
                if self.gotHit:
                    self.returnDict = {}
                    self.hitList = []
                    self.uvList = []
                    for i in range(self.hitPoints.length()):
                        self.hitList.append( [self.hitPoints[i].x, self.hitPoints[i].y, self.hitPoints[i].z])
                        self.hitMPoint = om.MPoint(self.hitPoints[i])
                        self.pArray = [0.0,0.0]
                        self.x1 = om.MScriptUtil()
                        self.x1.createFromList(pArray, 2)
                        self.uvPoint = x1.asFloat2Ptr()
                        self.uvSet = None
                        self.uvReturn = self.surfaceFn.getParamAtPoint(self.hitMPoint,self.uvPoint,self.paramU,self.paramV, self.ignoreTrimBoundaries, om.MSpace.kObject, self.kMFnNurbsEpsilon)
                                    
                        self.uValue = om.MScriptUtil.getFloat2ArrayItem(self.uvPoint, 0, 0) or False
                        self.vValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1) or False
                        self.uvList.append([self.uValue,self.vValue])
                                    
                        self.returnDict = {'hits':self.hitList,'source':[raySource.x,raySource.y,raySource.z],'uvs':self.uvList}
                        return self.returnDict
                else: return None
                        
            except StandardError,error:
                log.error(">>> surface| raysource | rayDir | error")
                return None

        def findSurfaceIntersections(self):
            '''
            Return the pierced points on a surface from a raySource and rayDir
            '''        
            try:
                self._str_funcName = 'findSurfaceIntersections'
                log.debug(">>> %s >> "%self._str_funcName + "="*75)
                if len(mc.ls(surface))>1:
                    raise StandardError,"findSurfaceIntersections>>> More than one surface named: %s"%surface

                self.centerPoint = mc.xform(surface, q=1, ws=1, t=1)

                #checking the type 
                self.objType = search.returnObjectType(surface)
                
                if self.objType == 'nurbsSurface':
                    raySource = om.MPoint(raySource[0], raySource[1], raySource[2])
                    self.raySourceVector = om.MVector(raySource[0], raySource[1], raySource[2])
                    self.centerPointVector = om.MVector(self.centerPoint[0],self.centerPoint[1],self.centerPoint[2])
                    rayDir = om.MPoint(self.centerPointVector - self.raySourceVector)
                    self.rayDirection = om.MVector(rayDir[0], rayDir[1], rayDir[2])
                    self.hitPoints = om.MPoint()
                    self.selectionList = om.MSelectionList()
                    self.selectionList.add(surface)
                    self.surfacePath = om.MDagPath()
                    self.selectionList.getDagPath(0, self.surfacePath)
                    self.surfaceFn = om.MFnNurbsSurface(self.surfacePath)
                    
                    #maxDist
                    self.maxDist = maxDistance

                    #other variables 
                    self.u = om.MDoubleArray()
                    self.v = om.MDoubleArray()
                    self.spc = om.MSpace.kWorld
                    self.toleranceSU = om.MScriptUtil()
                    self.tolerance = self.toleranceSU.asDoublePtr()
                    om.MScriptUtil.setDouble(self.tolerance, .1)

                    #Get the closest intersection.
                    self.gotHit = self.surfaceFn.intersect(raySource,self.rayDirection,self.u,self.v,self.hitPoints,self.toleranceSU.asDouble(),self.spc,False,None,False,None)
                    
                elif self.objType == 'mesh':
                    raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])
                    self.raySourceVector = om.MFloatVector(raySource[0], raySource[1], raySource[2])
                    self.centerPointVector = om.MFloatVector(self.centerPoint[0],self.centerPoint[1],self.centerPoint[2]) 
                    rayDir = om.MFloatPoint(self.centerPointVector - self.raySourceVector)
                    self.rayDirection = om.MFloatVector(rayDir[0], rayDir[1], rayDir[2])
                    self.hitPoints = om.MFloatPointArray()             
                    self.selectionList = om.MSelectionList()
                    self.selectionList.add(surface)
                    self.meshPath = om.MDagPath()
                    self.selectionList.getDagPath(0, self.meshPath)
                    self.meshFn = om.MFnMesh(self.meshPath)

                    #maxDist
                    self.maxDist = maxDistance

                    #other variables
                    self.spc = om.MSpace.kWorld

                    #Get the closest intersection.
                    self.gotHit = self.meshFn.allIntersections(raySource,self.rayDirection,None,None,False,self.spc,self.maxDist,False,None,False,self.hitPoints,None,None,None,None,None)
                 
                else : raise StandardError,"wrong surface type!"
                    
                #Return the intersection as a Python list.
                if self.gotHit:
                    self.returnDict = {}
                    self.hitList = []
                    self.uvList = []
                    for i in range( self.hitPoints.length() ):
                        self.hitList.append( [self.hitPoints[i].x, self.hitPoints[i].y, self.hitPoints[i].z])
                        self.hitMPoint = om.MPoint(self.hitPoints[i])
                        self.pArray = [0.0,0.0]
                        self.x1 = om.MScriptUtil()
                        self.x1.createFromList(pArray, 2)
                        self.uvPoint = x1.asFloat2Ptr()
                        self.uvSet = None
                        self.uvReturn = self.surfaceFn.getParamAtPoint(self.hitMPoint,self.uvPoint,self.paramU,self.paramV, self.ignoreTrimBoundaries, om.MSpace.kObject, self.kMFnNurbsEpsilon)
                                    
                        self.uValue = om.MScriptUtil.getFloat2ArrayItem(self.uvPoint, 0, 0) or False
                        self.vValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1) or False
                        self.uvList.append([self.uValue,self.vValue])
                                    
                        self.returnDict = {'hits':self.hitList,'source':[raySource.x,raySource.y,raySource.z],'uvs':self.uvList}
                        return self.returnDict
                else: return None
                        
            except StandardError,error:
                log.error(">>> surface | raysource | rayDir | error")
                return None

                            
        def findSurfaceIntersectionFromObjectAxis(self):
            '''
            Find surface intersections for an object's axis
            '''
            try:
                self._str_funcName = 'findSurfaceIntersectionFromObjectAxis'
                log.debug(">>> %s >> "%self._str_funcName + "="*75)
                if len(mc.ls(surface))>1:
                    raise StandardError,"findSurfaceIntersectionFromObjectAxis>>> More than one surface named: %s"%surface
                if not vector or type(vector) not in [list,tuple]:
                    self.d_matrixVectorIndices = {'x':[0,1,2],'y': [4,5,6],'z' : [8,9,10]}
                    self.matrix = mc.xform(obj, q=True,  matrix=True, worldSpace=True)
                    
                    #>>> Figure out our vector
                    if axis not in dictionary.stringToVectorDict.keys():
                        log.error("findSurfaceIntersectionFromObjectAxis axis arg not valid: '%s'"%axis)
                        return False 
                    if list(axis)[0] not in self.d_matrixVectorIndices.keys():
                        log.error("findSurfaceIntersectionFromObjectAxis axis arg not in d_matrixVectorIndices: '%s'"%axis)
                        return False
                    vector = [self.matrix[i] for i in self.d_matrixVectorIndices.get(list(axis)[0])]
                    if list(axis)[1] == '-':
                        for i,v in enumerate(vector):
                            vector[i]=-v
                if singleReturn:
                    return findSurfaceIntersection(surface, distance.returnWorldSpacePosition(obj), rayDir=vector, maxDistance = maxDistance)
                else:
                    return findSurfaceIntersections(surface, distance.returnWorldSpacePosition(obj), rayDir=vector, maxDistance = maxDistance)
            except StandardError,error:
                log.error(">>> surface| obj| axis| vector| error")
                return None     

        def findSurfaceMidPointFromObject(self):
            '''
            findSurfaceMidPointFromObject
            '''
            try:
                self._str_funcName = 'findSurfaceMidPointFromObject'
                log.debug(">>> %s >> "%self._str_funcName + "="*75)
                if len(mc.ls(surface))>1:
                    raise StandardError,"findSurfaceMidPointFromObject>>> More than one surface named: %s"%surface
                if type(axisToCheck) not in [list,tuple]:axisToCheck=[axisToCheck]
                axis = ['x','y','z']
                for a in axisToCheck :
                    if a not in axis:
                        raise StandardError,"findSurfaceMidPointFromObject>>> Not a valid axis : %s not in ['x','y','z']"%axisToCheck
                self.l_lastPos = []
                self.loc = locators.locMeObjectStandAlone(obj)
                for i in range(maxIterations):
                    self.l_positions = []
                    for a in axisToCheck:
                        log.debug("firing: %s"%a)
                        self.d_posReturn = findSurfaceIntersectionFromObjectAxis(surface, self.loc, axis = '%s+'%a,vector=vector,maxDistance = maxDistance) 
                        self.d_negReturn = findSurfaceIntersectionFromObjectAxis(surface, self.loc, axis = '%s-'%a,vector=vector,maxDistance = maxDistance) 
                        if 'hit' in self.d_posReturn.keys() and self.d_negReturn.keys():
                            self.l_pos = [self.d_posReturn.get('hit'),self.d_negReturn.get('hit')]
                            self.pos = distance.returnAveragePointPosition(self.l_pos)
                            self.l_positions.append(self.pos)
                    if len(self.l_positions) == 1:
                        self.l_pos =  self.l_positions[0]
                    else:
                        self.l_pos =  distance.returnAveragePointPosition(self.l_positions)
                    if self.l_lastPos:self.dif = cgmMath.mag( cgmMath.list_subtract(self.l_pos,self.l_lastPos) )
                    else:self.dif = 'No last'
                    log.debug("findSurfaceMidPointFromObject>>> Step : %s | dif: %s | last: %s | pos: %s "%(i,self.dif,self.l_lastPos,self.l_pos))
                    if self.l_lastPos and cgmMath.isVectorEquivalent(self.l_lastPos,self.l_pos,2):
                        log.debug("findSurfaceMidPointFromObject>>> Match found step: %s"%(i))
                        mc.delete(self.loc)
                        return self.l_pos 
                    mc.move(self.l_pos[0],self.l_pos[1],self.l_pos[2],self.loc,ws=True)
                    self.l_lastPos = self.l_pos#If we get to here, add the current    
                mc.delete(self.loc)    
                return self.l_pos
            except StandardError,error:
                raise StandardError, "error"
                            
                            
        def findFurthestPointInRangeFromObject(self):
            '''
            Find the furthest point in range on an axis. Useful for getting to the outershell of a surface
            '''
            try:
                self._str_funcName = 'findFurthestPointInRangeFromObject'
                log.debug(">>> %s >> "%self._str_funcName + "="*75)
                if len(mc.ls(surface))>1:
                    raise StandardError,"findFurthestPointInRangeFromObject>>> More than one surface named: %s"%surface                                  
                #>>>First cast to get our initial range
                self.d_firstcast = findSurfaceIntersectionFromObjectAxis(surface, obj, axis, vector, maxDistance)
                if not self.d_firstcast.get('hit'):
                    raise StandardError,"findFurthestPointInRangeFromObject>>> first cast failed to hit"
                self.baseDistance = distance.returnDistanceBetweenPoints(distance.returnWorldSpacePosition(obj),self.d_firstcast['hit'])                        
                log.debug("findFurthestPointInRangeFromObject>>>baseDistance: %s"%self.baseDistance)
                self.castDistance = self.baseDistance + pierceDepth
                log.debug("findFurthestPointInRangeFromObject>>>castDistance: %s"%castDistance)
                self.l_positions = []
                self.d_castReturn = findSurfaceIntersectionFromObjectAxis(surface, obj, axis, maxDistance = castDistance, singleReturn=False) or {}
                log.debug("2nd castReturn: %s"%self.d_castReturn)
                if self.d_castReturn.get('hits'):
                    self.closestPoint = distance.returnFurthestPoint(distance.returnWorldSpacePosition(obj),self.d_castReturn.get('hits')) or False    
                    self.d_castReturn['hit'] = self.closestPoint
                return self.d_castReturn
            except StandardError,error:
                for kw in [surface,obj,axis,pierceDepth,vector,maxDistance]:
                    log.debug("%s"%kw)
                raise StandardError, " >> error"

    return fncWrap(*args, **kws).go()

#test
surface = str(mc.cylinder()[0])
loc = mc.spaceLocator()
mc.move(8,6,3, loc)
mc.move(8,0,3, surface)
mc.delete(mc.aimConstraint(surface, loc))
raySource = mc.xform(loc, q=1, ws=1, t=1)

#unit testing
def ut_rayCasterSurfaceFuncCls(surface, raySource, rayDir, maxDistance, obj, axis, vector, singleReturn, axisToCheck, maxIterations, pierceDepth):
    assert type(surface) in [str], "surface is not a string!"
    assert type(raySource) in [list,tuple], "error type raySource!"
    assert type(rayDir) in [list,tuple], "error type rayDir!"
    assert type(maxDistance) in [int, float], "maxDistance is not int or float!"
    assert type(obj) in [str], "obj is not a string!"
    assert type(axis) in [str], "axis is not a string!"
    assert type(vector) in [bool], "axis is not a bool!"
    assert type(singleReturn) in [bool], "singleReturn is not a bool!"
    assert type(axisToCheck) in [list,tuple], "axisToCheck is not a list!"
    assert type(maxIterations) in [int, float], "maxIterations is not int or float!"
    assert type(pierceDepth) in [int, float], "pierceDepth is not int or float!"
ut_rayCasterSurfaceFuncCls(surface, raySource, rayDir=[0,1,0], maxDistance = 1000, obj='obj', axis='z+', vector=False, singleReturn=True, axisToCheck=['x','z'], maxIterations=10, pierceDepth=4)

rayCasterSurfaceFuncCls(reportTimes = 1)
rayCasterSurfaceFuncCls(printHelp = 1)
rayCasterSurfaceFuncCls(reportShow = 1)
rayCasterSurfaceFuncCls(reportEnv = 1)