"""
------------------------------------------
rayCaster: cgm.core.lib.rayCaster
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

ACKNOWLEDGEMENTS:
   Samaneh Momtazmand -- r&d for casting with surfaces
================================================================
"""
import maya.cmds as mc
import copy
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as om
from cgm.core.lib.zoo import apiExtensions
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import position_utils as POS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import name_utils as NAMES
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.shape_utils as SHAPE
reload(DIST)
from cgm.core import cgm_General as cgmGEN
from cgm.lib import locators
from cgm.lib import dictionary
from cgm.lib import search
from cgm.lib import cgmMath
from cgm.lib import lists
from cgm.lib import distance
from cgm.lib import attributes
import os
#CANNOT IMPORT: LOC, SNAP

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def get_eligibleMesh():
    _str_func = ''
    _res = []
    for l in mc.ls(type='mesh',visible = True, long=True), mc.ls(type='nurbsSurface',long=True, visible = True):
        for o in l:
            _mesh =  SHAPE.get_nonintermediate(o)
            _type = VALID.get_mayaType(_mesh)
            if _type in ['mesh','nurbsSurface']:
                _res.append( _mesh )#...this accounts for deformed mesh 
            else:
                log.debug("|{0}| >> Inelibible: {1} | {2}".format(_str_func,_type,_mesh))
    return _res

def get_dist_from_cast_axis(obj = None, axis = 'z', mode = 'near', shapes = None, mark = False,
                            startPoint = None, maxDistance = 1000, asEuclid = False):
    _str_func = 'get_dist_from_cast_axis'
    log.debug(cgmGEN.logString_start(_str_func))
    
    l_pos = []
    for d in ['+','-']:
        pos = get_cast_pos(obj,axis+d,mode,shapes,mark,startPoint,maxDistance,asEuclid)
        l_pos.append(pos)
        
    return DIST.get_distance_between_points(l_pos[0],l_pos[1])
    
    

def get_cast_pos(obj = None, axis = 'z+', mode = 'near', shapes = None, mark = False, startPoint = None, maxDistance = 1000, asEuclid = False):
    """
    Get the 

    :parameters:
        arg(str/list): Object(s) to check
        axis(str): 
        mode(varied): 
            center
            far
            near
        mark(bool): whether to add a locator at the position for testing
        asEuclid(bool) - whether to return as Vector or not

    :returns
        boundingBox size(list)
    """   
    try:
        _str_func = 'get_cast_pos'
        _sel = mc.ls(sl=True)
        _res = None
        
        if obj is None:
            obj = _sel[0]

        if shapes is None:
            shapes = get_eligibleMesh()
            for s in TRANS.shapes_get(obj,True):
                if s in shapes:
                    shapes.remove(s)
        else:
            _shapesArg = VALID.listArg(shapes)
            shapes = []
            for o in _shapesArg:
                if VALID.is_shape(o):
                    shapes.append(o)                
                else:
                    shapes.extend(TRANS.shapes_get(o,True))

        mAxis = VALID.simpleAxis(axis)
        posBase = POS.get(obj)

        if len(axis) == 1:
            log.debug("|{0}| >> Single axis arg...".format(_str_func))

        if mode in ['center','centerFar','centerNear']:
            _subMode = 'far'
            if 'near' in mode.lower():
                _subMode = 'near'
            l_hits = []
            for s in shapes:
                log.debug("|{0}| >> Casting at shape: {1}".format(_str_func,s))
                _d_resForward = cast(s,obj,mAxis.p_string, startPoint=startPoint,maxDistance=maxDistance,firstHit=False)
                _d_resBack = cast(s,obj,mAxis.inverse.p_string, startPoint=startPoint,maxDistance=maxDistance,firstHit=False)
                if not _d_resForward:
                    log.warning("|{0}| >> Failed to hit: {1}".format(_str_func,s))
                    return False
                p1 = _d_resForward.get(_subMode)
                p2 = _d_resBack.get(_subMode)
                l_hits.append(DIST.get_average_position([p1,p2]))
            if len(l_hits)>1:
                _res = DIST.get_average_position(l_hits)
            else:
                _res = l_hits[0]

        elif mode in ['near','far']:
            l_hits = []
            l_distances = []
            for s in shapes:
                log.debug("|{0}| >> Casting at shape: {1}".format(_str_func,s))
                _d_res = cast(s,obj,mAxis.p_string, startPoint=startPoint,
                              maxDistance=maxDistance,firstHit=False)
                p = _d_res.get(mode,None)
                if p:
                    l_hits.append(p)
                    l_distances.append(DIST.get_distance_between_points(posBase,p))
                else:
                    log.debug("|{0}| >> Failed to hit: {1}".format(_str_func,s))                    
            if not l_distances:
                log.debug("|{0}| >> Nothing hit".format(_str_func))                                    
                return False#raise ValueError,"Nothing hit."
            if mode == 'near':
                modeIdx = l_distances.index( min(l_distances) )
            else:
                modeIdx = l_distances.index( max(l_distances) )
                
            _hit =  l_hits[modeIdx]
            
            if MATH.is_vector_equivalent(_hit, startPoint):
                log.warning("|{0}| >> startPoint equivalent to hit. Using alternate method. May not be exact".format(_str_func,s))
                _vec = MATH.get_obj_vector(obj, axis)
                _outPoint = DIST.get_pos_by_axis_dist(obj,axis,maxDistance)
                _newPos = DIST.get_closest_point(_outPoint,s)
                _hit = _newPos[0]
                
            _res = _hit

        #cgmGEN.func_snapShot(vars())



        if mark:
            #_size = get_bb_size(arg, shapes)
            _loc = mc.spaceLocator()[0]
            #ATTR.set(_loc,'scale', [v/4 for v in _size])        
            mc.move (_res[0],_res[1],_res[2], _loc, ws=True)        
            mc.rename(_loc, '{0}_loc'.format(mode))
            

        if _sel:
            mc.select(_sel)
        if asEuclid:
            log.debug("|{0}| >> asEuclid...".format(_str_func))             
            return EUCLID.Vector3(_res[0], _res[1], _res[2])
        return _res
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)


def cast(mesh = None, obj = None, axis = 'z+',
         startPoint = None, vector = None,
         maxDistance = 1000, firstHit = True,
         offsetMode = None, offsetDistance = 1.0,
         locDat = False):
    """
    Find mesh intersections. Note -- startPoint will be converted from mayaspace to api space

    :parameters:
        mesh(string/list) | Surface to cast at
        obj(string) | transform to cast from
        axis(string) | Axis to cast
        vector(double3) | vector to cast
        maxDistance(float) | max cast range
        firstHit(bool) | single return per mesh
        offsetMode(str) | process the hit. Per mesh hits will be returned raw
            distance | offset a given distance along the cast vector
        offsetDistance(float) | how much to offset with distance mode
        locDat | loc each point of data

    :returns:
        Dict ------------------------------------------------------------------
        'source'(double3) |  point from which we cast
        'hit' | only there for firstHit and single mesh or closestInRange
        'hits'(list) | world space points
        'uvs'(dict) | uv on surface of hit
        'near' | nearest hit
        'far' | furthest hit

    :raises:
    Exception | if reached
    """  
    def simpleLoc( position = None):
        _loc = mc.spaceLocator()[0]
        mc.move (position[0],position[1],position[2], _loc, ws=True)
        return _loc


    _str_func = 'cast'
    if mesh is None:
        mesh = get_eligibleMesh()
    _meshArg = VALID.listArg(mesh)
    _mesh =  []
    for m in _meshArg:
        log.debug("|{0}| >> checking mesh arg: {1}...".format(_str_func,m))                            
        if SEARCH.is_transform(m):
            #_mesh.extend(mc.listRelatives(m,shapes = True))
            for s in TRANS.shapes_get(m,True):
                if VALID.get_mayaType(s) in ['mesh','nurbsSurface']:
                    log.debug("|{0}| >> good shape: {1}...".format(_str_func,s))                    
                    _mesh.append(m)
        elif SEARCH.is_shape(m):
            if VALID.get_mayaType(m) in ['mesh','nurbsSurface']:
                log.debug("|{0}| >> good shape: {1}...".format(_str_func,m))                    
                _mesh.append(m)            

    if not startPoint:
        startPoint = POS.get(obj,pivot='rp',space='ws')

    _castPoint = MATH.get_space_value(startPoint,'apiSpace')#...must convert value to apiSpace

    if not vector:
        if not obj:
            raise ValueError,"Must have an obj to get a vector when no vector is provided"

        d_matrixVectorIndices = {'x':[0,1,2],
                                 'y': [4,5,6],
                                 'z' : [8,9,10]}

        matrix = mc.xform(obj, q=True,  matrix=True, worldSpace=True)

        #>>> Figure out our vector
        if axis not in dictionary.stringToVectorDict.keys():
            log.error("|{0}| >> axis arg not valid: '{1}'".format(_str_func,axis))
            return False
        if list(axis)[0] not in d_matrixVectorIndices.keys():
            log.error("|{0}| >> axis arg not in d_matrixVectorIndices: '{1}'".format(_str_func,axis))            
            return False  
        vector = [matrix[i] for i in d_matrixVectorIndices.get(list(axis)[0])]
        if list(axis)[1] == '-':
            for i,v in enumerate(vector):
                vector[i]=-v

    _l_posBuffer = []
    _l_uvBuffer = []
    _source = None

    log.debug("|{0}| >> Source:{1} | Vector:{2}".format(_str_func,startPoint,vector))
    _d_meshPos = {}
    _d_meshUV = {}
    _d_meshUVRaw = {}
    _d_meshNormal = {}
    for m in _mesh:
        _b = {}
        if not _d_meshUV.get(m):_d_meshUV[m] = []
        if not _d_meshPos.get(m):_d_meshPos[m] = []
        if not _d_meshNormal.get(m):_d_meshNormal[m] = []
        if not _d_meshUVRaw.get(m):_d_meshUVRaw[m] = []        
        if firstHit:
            try:_b = findMeshIntersection(m, _castPoint, rayDir=vector, maxDistance = maxDistance)
            except:log.error("|{0}| mesh failed to get hit: {1}".format(_str_func,m))
            if _b:
                h = _b['hit']

                _uv = _b.get('uv',None)
                _uvRaw = _b.get('uvRaw',None)
                _normal = _b.get('normal',False)
                _d_meshUV[m].append(_uv)
                _d_meshUVRaw[m].append(_uvRaw)
                _d_meshPos[m].append(h)	
                _d_meshNormal[m].append(_normal)
                if not _uv:
                    log.debug("{0} failed to find uvs".format(m))

                if offsetMode:
                    h = offsetHit(h,startPoint,vector,offsetDistance)
                _l_posBuffer.append(h)                
        else:
            try:_b = findMeshIntersections(m, _castPoint, rayDir=vector, maxDistance = maxDistance)
            except:log.error("|{0}| mesh failed to get hit: {1}".format(_str_func,m))	
            if _b:
                _uvs = _b.get('uvs',None)
                _uvsRaw = _b.get('uvsRaw',[])
                _normals =_b.get('normals',False)

                if not _uvs:
                    log.debug("{0} failed to find uvs".format(m))
                if not _normals:
                    log.debug("{0} failed to find normals".format(m))   

                for i,h in enumerate(_b['hits']):
                    _uv = _uvs[i]
                    _d_meshUV[m].append(_uv)

                    if _uvsRaw:
                        _uvRaw = _uvsRaw[i]
                    else:
                        _uvRaw = None
                    _d_meshUVRaw[m].append(_uvRaw)

                    _d_meshPos[m].append(h)		
                    _d_meshNormal[m].append(_normals[i])
                    if offsetMode == 'vectorDistance':
                        h = offsetHit(h,startPoint,vector,offsetDistance)
                    _l_posBuffer.append(h)

        if _b:
            if _source == None:
                _source = _b['source']

    if not _l_posBuffer:
        log.debug("|{0}| No hits detected. startPoint: {1} | mesh:{2} | vector:{4} | axis: {3}".format(_str_func,startPoint,mesh,axis,vector))
        return {}


    _near = distance.returnClosestPoint(startPoint, _l_posBuffer)
    _furthest = distance.returnFurthestPoint(startPoint,_l_posBuffer)

    _d = {'source':startPoint, 'near':_near, 'far':_furthest, 'hits':_l_posBuffer, 'uvs':_d_meshUV, 'uvsRaw':_d_meshUVRaw, 'meshHits':_d_meshPos,'meshNormals':_d_meshNormal}

    if locDat:
        for k in ['source','near','far']:
            if _d.get(k):
                mc.rename( simpleLoc(position = _d.get(k)), 'cast_{0}_loc'.format(k))
        for m in _d['meshHits'].keys():
            for i,p in enumerate(_d['meshHits'][m]):
                _dist = DIST.get_distance_between_points(_d['source'],p) / 3
                mc.rename( simpleLoc(position = p), 'cast_hit_{0}_{1}_loc'.format(NAMES.get_base(m),i))

                _p = DIST.get_pos_by_vec_dist(p, _d['meshNormals'][m][i], _dist)
                mc.rename( simpleLoc(position = _p), 'cast_normalOffset_{0}_{1}_loc'.format(NAMES.get_base(m),i))



    if firstHit:
        _d['hit'] = _near
    else:_d['hit'] = _furthest
    return _d

def offset_hit_by_distance(h,startPoint,vector,offsetDistance, offsetMode = 'distance'):
    _str_func = 'offset_hit_by_distance'    
    log.debug("|{0}| >> offset call...".format(_str_func))
    if offsetMode == 'distance':
        if not offsetDistance:
            log.warning("|{0}| >> No offsetDistance provided. Using 1.0...".format(_str_func))
            offsetDistance = 1.0

        log.debug("|{0}| >> vectorDistance offset {1}...".format(_str_func,offsetDistance))

        _dist_base = DIST.get_distance_between_points(startPoint, h)#...get our base distance
        _offsetPos = DIST.get_pos_by_vec_dist(startPoint,vector,(_dist_base + offsetDistance))
        log.debug("|{0}| >> hit: {1} | offset: {2}...".format(_str_func,h,_offsetPos))
        h = _offsetPos
    else:
        log.warning("|{0}| >> unknown offsetMode {1}...".format(_str_func,offsetMode))

    return h

#LOOK AT BELOW FOR OPTIMIZATION =================================================================================================




def findSurfaceIntersection(surface, raySource, rayDir, maxDistance = 1000):
    """
    Thanks to Deane @ https://groups.google.com/forum/?fromgroups#!topic/python_inside_maya/n6aJq27fg0o%5B1-25%5D

    Return the closest point on a surface from a raySource and rayDir

    Arguments
    mesh(string) -- currently poly surface only
    raySource(double3) -- point in world space
    rayDir(double3) -- world space vector

    returns hitpoint(double3)
    """    
    try:
        _str_func = 'findSurfaceIntersection'
        log.debug(">>> %s >> "%_str_func + "="*75)           
        if len(mc.ls(surface))>1:
            raise StandardError,"findSurfaceIntersection>>> More than one surface named: %s"%surface    

        #Create an empty selection list.
        selectionList = om.MSelectionList()

        #Put the surface's name on the selection list.
        selectionList.add(surface)

        #Create an empty MDagPath object.
        meshPath = om.MDagPath()

        #Get the first item on the selection list (which will be our mesh)
        #as an MDagPath.
        selectionList.getDagPath(0, meshPath)

        #Create an MFnMesh functionset to operate on the node pointed to by
        #the dag path.
        nurbsFn = om.MFnNurbsSurface(meshPath)

        #Convert the 'raySource' parameter into an MFloatPoint.
        raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])

        #Convert the 'rayDir' parameter into an MVector.`
        rayDirection = om.MFloatVector(rayDir[0], rayDir[1], rayDir[2])

        #Create an empty MFloatPoint to receive the hit point from the call.
        hitPoint = om.MFloatPoint()

        #Create empty doubles
        uPoint = om.MFloatVector()
        vPoint = om.MFloatVector()
        pDistance = om.MFloatPoint()

        log.debug("maxDistance: %s"%maxDistance)

        #Set up a variable for each remaining parameter in the
        #MFnMesh::closestIntersection call. We could have supplied these as
        #literal values in the call, but this makes the example more readable.
        sortIds = False
        maxDist = maxDistance#om.MDistance.internalToUI(1000000)# This needs work    
        #maxDist = om.MDistance.internalToUI(maxDistance) # This needs work
        bothDirections = False
        noFaceIds = None
        noTriangleIds = None
        noAccelerator = None
        noHitParam = None
        noHitFace = None
        noHitTriangle = None
        noHitBary1 = None
        noHitBary2 = None
        b_calculateDistance = False
        f_tolerance = 1.0e-3
        b_calculateExactHit = False
        b_wasExactHit = False
        #Get the closest intersection.
        gotHit = nurbsFn.intersect(raySource, rayDirection,#Ins
                                   uPoint,vPoint,hitPoint,
                                   f_tolerance, om.MSpace.kWorld,
                                   b_calculateDistance,pDistance,
                                   b_calculateExactHit,b_wasExactHit)

        #Return the intersection as a Pthon list.
        if gotHit:
            return gotHit
            #Thank you Mattias Bergbom, http://bergbom.blogspot.com/2009/01/float2-and-float3-in-maya-python-api.html
            hitMPoint = om.MPoint(hitPoint) # Thank you Capper on Tech-artists.org          
            pArray = [0.0,0.0]
            x1 = om.MScriptUtil()
            x1.createFromList( pArray, 2 )
            uvPoint = x1.asFloat2Ptr()
            uvSet = None
            closestPolygon=None
            uvReturn = meshFn.getUVAtPoint(hitMPoint,uvPoint,om.MSpace.kWorld)

            uValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0) or False
            vValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1) or False
            log.debug("Hit! [%s,%s,%s]"%(hitPoint.x, hitPoint.y, hitPoint.z))
            if uValue and vValue:
                return {'hit':[hitPoint.x, hitPoint.y, hitPoint.z],'source':[raySource.x,raySource.y,raySource.z],'uv':[uValue,vValue]}                
            else:
                return {'hit':[hitPoint.x, hitPoint.y, hitPoint.z],'source':[raySource.x,raySource.y,raySource.z],'uv':False}
        else:
            return None    
    except StandardError,error:
        log.error(">>> %s >> mesh: %s | raysource: %s | rayDir %s | error: %s"%(_str_func,surface,raySource,rayDir,error))
        return None


def findMeshIntersection(mesh, raySource, rayDir, maxDistance = 1000, tolerance = .1):
    """
    Return the closest point on a surface from a raySource and rayDir. Can't process uv point for surfaces yet
    Thanks to Deane @ https://groups.google.com/forum/?fromgroups#!topic/python_inside_maya/n6aJq27fg0o%5B1-25%5D
    Thanks to Samaneh Momtazmand for doing the r&d to get this working with surfaces

    Note -- result hit points will be converted from apiSpace to maya space

    :parameters:
        mesh(string) | Surface to cast at
        raySource(double3) | point from which to cast in world space
        rayDir(vector) | world space vector
    maxDistance(float) | Maximum cast distance 
    tolerance(float) | Tolerance for cast (surface cast mode only) 

    :returns:
        Dict ------------------------------------------------------------------
    'source'(double3) |  point from which we cast
    'hit'(double3) | world space points | active during single return
    'hits'(list) | world space points | active during multi return
    'uv'(double2) | uv on surface of hit | only works for mesh surfaces

    :raises:
    Exception | if reached

    """      
    try:
        _str_func = 'findMeshIntersection'

        try:
            """if VALID.isListArg(mesh):
                log.debug("{0}>>> list provided. Using first : {1}".format(_str_func,mesh))
                mesh = mesh[0]
            if len(mc.ls(mesh))>1:
                raise StandardError,"{0}>>> More than one mesh named: {1}".format(_str_func,mesh)
            _str_objType = search.returnObjectType(mesh)
            if _str_objType not in ['mesh','nurbsSurface']:
                raise ValueError,"Object type not supported | type: {0}".format(_str_objType)"""

            _str_objType = VALID.get_mayaType(mesh)
            if _str_objType not in ['mesh','nurbsSurface']:
                raise ValueError,"Object type not supported | type: {0}".format(_str_objType)


            #Create an empty selection list.
            selectionList = om.MSelectionList()

            #Convert the 'raySource' parameter into an MFloatPoint.
            #raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])
            mPoint_raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])

            #Convert the 'rayDir' parameter into an MVector.`
            mVec_rayDirection = om.MFloatVector(rayDir[0], rayDir[1], rayDir[2])

            #Create an empty MFloatPoint to receive the hit point from the call.
            mPoint_hit = om.MFloatPoint()

            #centerPointVector = om.MFloatVector(centerPoint[0],centerPoint[1],centerPoint[2]) 
            #rayDir = om.MFloatPoint(centerPointVector - raySourceVector)
            maxDist = maxDistance
            spc = om.MSpace.kWorld	

        except Exception,error:
            raise ValueError,"Validation fail |{0}".format(error)    

        try:
            if _str_objType == 'nurbsSurface': 
                log.debug("{0} | Surface cast mode".format(_str_func))

                #surfaceShape = mc.listRelatives(mesh, s=1)[0]

                mPoint_raySource = om.MPoint(raySource[0], raySource[1], raySource[2])
                mVec_rayDirection = om.MVector(rayDir[0], rayDir[1], rayDir[2])
                mPoint_hit = om.MPoint()    
                selectionList = om.MSelectionList()
                selectionList.add(mesh)
                surfacePath = om.MDagPath()
                selectionList.getDagPath(0, surfacePath)
                surfaceFn = om.MFnNurbsSurface(surfacePath)		

                #other variables 
                #uSU = om.MScriptUtil()
                #vSU = om.MScriptUtil()
                #uPtr = uSU.asDoublePtr()
                #vPtr = vSU.asDoublePtr()		
                mPoint_u = om.doublePtr()
                mPoint_v = om.doublePtr()

                #Get the closest intersection.
                gotHit = surfaceFn.intersect(mPoint_raySource,
                                             mVec_rayDirection,
                                             mPoint_u, mPoint_v,mPoint_hit, tolerance, spc, False, None, False, None)

            elif _str_objType == 'mesh':
                log.debug("{0} | Mesh cast mode".format(_str_func))

                #Put the mesh's name on the selection list.
                selectionList.add(mesh)

                #Create an empty MDagPath object.
                meshPath = om.MDagPath()

                #Get the first item on the selection list (which will be our mesh)
                #as an MDagPath.
                selectionList.getDagPath(0, meshPath)

                #Create an MFnMesh functionset to operate on the node pointed to by
                #the dag path.
                meshFn = om.MFnMesh(meshPath)

                #Set up a variable for each remaining parameter in the
                #MFnMesh::closestIntersection call. We could have supplied these as
                #literal values in the call, but this makes the example more readable.
                sortIds = False
                #maxDist = maxDistance#om.MDistance.internalToUI(1000000)# This needs work    
                #maxDist = om.MDistance.internalToUI(maxDistance) # This needs work
                bothDirections = False
                noFaceIds = None
                noTriangleIds = None
                noAccelerator = None
                noHitParam = None
                noHitFace = None
                noHitTriangle = None
                noHitBary1 = None
                noHitBary2 = None

                #Get the closest intersection.
                gotHit = meshFn.closestIntersection(
                    mPoint_raySource, mVec_rayDirection,
                    noFaceIds, noTriangleIds,
                    sortIds, om.MSpace.kWorld, maxDist, bothDirections,
                    noAccelerator,
                    mPoint_hit,
                    noHitParam, noHitFace, noHitTriangle, noHitBary1, noHitBary2, .001)

                #Get the closest intersection.
                #gotHit=meshFn.closestIntersection(raySource,rayDirection,None,None,False,spc,maxDist,False,None,hitPoint,None,None,None,None,None)
            else : raise ValueError,"Wrong surface type!"
        except Exception,error:
            raise Exception,"Cast fail |{0}".format(error) 

        #Return the intersection as a Pthon list.
        d_return = {}
        if gotHit:
            #Thank you Mattias Bergbom, http://bergbom.blogspot.com/2009/01/float2-and-float3-in-maya-python-api.html
            hitMPoint = om.MPoint(mPoint_hit) # Thank you Capper on Tech-artists.org          
            pArray = [0.0,0.0]
            x1 = om.MScriptUtil()
            x1.createFromList( pArray, 2 )
            uvPoint = x1.asFloat2Ptr()
            uvSet = None
            closestPolygon=None
            log.debug("{0} | Hit! [{1},{2},{3}]".format(_str_func,mPoint_hit.x, mPoint_hit.y, mPoint_hit.z))

            d_return['hit'] = MATH.get_space_value( [mPoint_hit.x, mPoint_hit.y, mPoint_hit.z] )
            d_return['source'] = [mPoint_raySource.x,mPoint_raySource.y,mPoint_raySource.z]

            try:
                if _str_objType == 'mesh':
                    uvReturn = meshFn.getUVAtPoint(hitMPoint,uvPoint,om.MSpace.kWorld)

                    uValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0) or False
                    vValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1) or False
                    if uValue and vValue:
                        d_return['uv'] = [uValue,vValue]		    
                else:
                    uRaw = mPoint_u.value()
                    vRaw = mPoint_v.value()
                    __d = DIST.get_normalized_uv(mesh,uRaw,vRaw)#normalize data

                    d_return['uvRaw'] = [uRaw,vRaw]
                    d_return['uv'] = __d['uv']
            except Exception,err:raise Exception,"Uv Processing failure |{0}".format(err) 

            try:#...normal,face id processing
                if _str_objType == 'mesh':
                    mVector_normal = om.MVector()
                    meshFn.getClosestNormal(hitMPoint,mVector_normal,om.MSpace.kWorld)
                    #log.debug(mVector_normal)
                    #log.debug(mVector_normal.x)
                    d_return['normal'] = [mVector_normal.x,mVector_normal.y,mVector_normal.z]
                else:
                    _res = surfaceFn.normal( uRaw, vRaw,om.MSpace.kWorld)
                    d_return['normal'] = [_res.x, _res.y, _res.z]
                    pass

            except Exception,err:raise Exception,"Normal processing failure |{0}".format(err)             


        return d_return 
    except Exception,error:
        log.debug(">>> {0} >> Failure! mesh: '{1}' | raysource: {2} | rayDir {3}".format(_str_func,mesh,raySource,rayDir))
        log.debug(">>> {0} >> error: {1}".format(_str_func,error))        
        return None

def findMeshIntersections(mesh, raySource, rayDir, maxDistance = 1000, tolerance = .1):
    """
    Calls on OpenMaya 1 and 2 variations after some bugs were discovered with 2016 casting. 
    -2016 OM2 - when casting at poly edge, fails
    -2016 OM2 - nurbsSurface UV returns a different rawUV than 1. 1 Normalizes as expected, 2's does not.
    -2016 OM2 - nurbsSurface normal returns junk and broken

    Note -- result hit points will be converted from apiSpace to maya space


    :parameters:
        mesh(string) | Surface to cast at
        raySource(double3) | point from which to cast in world space
        rayDir(vector) | world space vector
    maxDistance(value) | Maximum cast distance 

    :returns:
        Dict ------------------------------------------------------------------
    'source'(double3) |  point from which we cast
    'hits'(list) | world space points
    'uvs'(list) | uv on surface of hit | only works for mesh surfaces

    :raises:
    Exception | if reached

    """      
    try:
        _str_func = 'findMeshIntersections'

        _b_OpenMaya_2 = False
        if cgmGEN.__mayaVersion__ >= 2012:
            _b_OpenMaya_2 = True

        """if VALID.isListArg(mesh):
            log.debug("{0}>>> list provided. Using first : {1}".format(_str_func,mesh))
            mesh = mesh[0]	    
        if len(mc.ls(mesh))>1:
            raise StandardError,"{0}>>> More than one mesh named: {1}".format(_str_func,mesh)
        _str_objType = search.returnObjectType(mesh)"""

        _str_objType = VALID.get_mayaType(mesh)
        if _str_objType not in ['mesh','nurbsSurface']:
            raise ValueError,"Object type not supported | type: {0}".format(_str_objType)        

        #if _str_objType not in ['mesh','nurbsSurface']:
            #raise ValueError,"Object type not supported | type: {0}".format(_str_objType)

        if _str_objType == 'mesh' and _b_OpenMaya_2:
            return findMeshIntersections_OM2(mesh, raySource, rayDir, maxDistance, tolerance)
        return findMeshIntersections_OM1(mesh, raySource, rayDir, maxDistance, tolerance)

    except Exception,error:
        log.debug(">>> {0} >> Failure! mesh: '{1}' | raysource: {2} | rayDir {3}".format(_str_func,mesh,raySource,rayDir))
        log.debug(">>> {0} >> error: {1}".format(_str_func,error))        
        return None 

def findMeshIntersections_OM2(mesh, raySource, rayDir, maxDistance = 1000, tolerance = .1):
    """
    Return the closest points on a surface from a raySource and rayDir. Can't process uv point for surfaces yet
    Thanks to Deane @ https://groups.google.com/forum/?fromgroups#!topic/python_inside_maya/n6aJq27fg0o%5B1-25%5D
    Thanks to Samaneh Momtazmand for doing the r&d to get this working with surfaces

    Note -- result hit points will be converted from apiSpace to maya space

    :parameters:
        mesh(string) | Surface to cast at
        raySource(double3) | point from which to cast in world space
        rayDir(vector) | world space vector
    maxDistance(value) | Maximum cast distance 

    :returns:
        Dict ------------------------------------------------------------------
    'source'(double3) |  point from which we cast
    'hits'(list) | world space points
    'uvs'(list) | uv on surface of hit | only works for mesh surfaces

    :raises:
    Exception | if reached

    """      
    try:
        _str_func = 'findMeshIntersections_OM2'
        from maya.api import OpenMaya as OM2

        try:
            """if VALID.isListArg(mesh):
                log.debug("{0}>>> list provided. Using first : {1}".format(_str_func,mesh))
                mesh = mesh[0]	    
            if len(mc.ls(mesh))>1:
                raise StandardError,"{0}>>> More than one mesh named: {1}".format(_str_func,mesh)
            _str_objType = search.returnObjectType(mesh)
            if _str_objType not in ['mesh','nurbsSurface']:
                raise ValueError,"Object type not supported | type: {0}".format(_str_objType)"""

            _str_objType = VALID.get_mayaType(mesh)
            if _str_objType not in ['mesh','nurbsSurface']:
                raise ValueError,"Object type not supported | type: {0}".format(_str_objType)


            mPoint_raySource = OM2.MFloatPoint(raySource[0], raySource[1], raySource[2])
            #Convert the 'rayDir' parameter into an MVector.`
            mVec_rayDirection = OM2.MFloatVector(rayDir[0], rayDir[1], rayDir[2])
            #Create an empty MFloatPoint to receive the hit point from the call.
            mPointArray_hits = OM2.MFloatPointArray()

            #centerPointVector = om.MFloatVector(centerPoint[0],centerPoint[1],centerPoint[2]) 
            #rayDir = om.MFloatPoint(centerPointVector - raySourceVector)
            maxDist = maxDistance
            spc = om.MSpace.kWorld	

        except Exception,error:
            raise ValueError,"Validation fail |0}".format(error)    

        try:
            if _str_objType == 'nurbsSurface': 
                log.debug("{0} | Surface cast mode".format(_str_func))
                #centerPoint = mc.xform(mesh, q=1, ws=1, t=1)    
                #surfaceShape = mc.listRelatives(mesh, s=1)[0]


                sel = OM2.MSelectionList()#...make selection list
                sel.add(mesh)#...add them to our lists 
                surfaceFn = OM2.MFnNurbsSurface(sel.getDagPath(0))

                mPoint_raySource = OM2.MPoint(raySource[0], raySource[1], raySource[2])
                mVec_rayDirection = OM2.MVector(rayDir[0], rayDir[1], rayDir[2])

                gotHit = surfaceFn.intersect(mPoint_raySource,
                                             mVec_rayDirection,
                                             tolerance,
                                             OM2.MSpace.kWorld,
                                             False,#distance to return maxDist,
                                             True,#exactHit, next is all
                                             True)                    

            elif _str_objType == 'mesh':
                log.debug("{0} | Mesh cast mode".format(_str_func))

                sel = OM2.MSelectionList()#...make selection list
                sel.add(mesh)#...add them to our lists 
                meshFn = OM2.MFnMesh(sel.getDagPath(0))

                gotHit = meshFn.allIntersections(mPoint_raySource,
                                                 mVec_rayDirection,
                                                 OM2.MSpace.kWorld,
                                                 maxDist,
                                                 False,
                                                 tolerance = tolerance)
                #Get the closest intersection.
                """
                """
            else : raise ValueError,"Wrong surface type!"
        except Exception,error:
            raise Exception,"Cast fail |{0}".format(error) 

        #Return the intersection as a Pthon list.
        d_return = {}
        l_hits = []
        l_uv = []	
        l_rawUV = []
        l_normals = []
        _space = OM2.MSpace.kWorld
        if gotHit:

            #Nurbs return -
            for i,hit in enumerate(gotHit[0]) :
                l_hits.append( MATH.get_space_value( [hit.x, hit.y,hit.z] ))
                mPoint_hit = OM2.MPoint(hit) # Thank you Capper on Tech-artists.org          
                log.debug("{0} | {4} Hit! [{1},{2},{3}]".format(_str_func,mPoint_hit.x, mPoint_hit.y, mPoint_hit.z, i))

                log.debug("Hit return...")
                for i4,item in enumerate(gotHit):
                    log.debug("|{2}| >> {0} : {1}".format(i4,item,_str_func))

                if _str_objType == 'mesh':
                    uvReturn = meshFn.getUVAtPoint(mPoint_hit,OM2.MSpace.kWorld)
                    if uvReturn:
                        l_uv.append([uvReturn[0],uvReturn[1]])

                    #normals...
                    mNormal = meshFn.getClosestNormal(mPoint_hit,OM2.MSpace.kWorld)
                    l_normals.append([mNormal[0].x,mNormal[0].y,mNormal[0].z])

                else:#Nurbs

                    raise Exception,"Open Maya 2.0 should not be used with Nurbs ray stuff. Normal returns are off."    
                    uRaw = gotHit[i+1][0]
                    vRaw =  gotHit[i+1][1] 

                    #log.info('u: {0}'.format(uRaw))
                    #log.debug('v: {0}'.format(vRaw))

                    __d = DIST.get_normalized_uv(mesh,uRaw,vRaw)#normalize data

                    l_rawUV.append([uRaw,vRaw])
                    l_uv.append(__d['uv']) 

                    #normals...
                    #

                    #mNormal = surfaceFn.normal(__d['uv'][0],__d['uv'][1],OM2.MSpace.kWorld)                    
                    try:
                        #Must use raw values
                        #mNormal = surfaceFn.normal(__d['uv'][0],__d['uv'][1],OM2.MSpace.kWorld) 
                        mNormal = surfaceFn.normal(uRaw,vRaw,_space)
                        l_normals.append([mNormal[0],mNormal[1],mNormal[2]])                                            
                    except Exception,err:
                        l_normals.append(False)
                        log.error("|{0}| >> Surface normal query failed. | uRaw:{1} | vRaw:{2} | space:{3} ||| err: {4}".format(_str_func,uRaw,vRaw,OM2.MSpace.kWorld,err))
                    log.debug('n: {0}'.format(mNormal))
                    #mNormal = surfaceFn.normal(uRaw,vRaw,OM2.MSpace.kWorld)                    

            try:            
                d_return['hits'] = l_hits
                d_return['source'] = [mPoint_raySource.x,mPoint_raySource.y,mPoint_raySource.z]	    
                if l_uv:
                    d_return['uvs'] = l_uv
                if l_rawUV:
                    d_return['uvsRaw'] = l_rawUV
                if l_normals:
                    d_return['normals'] = l_normals
            except Exception,err:
                raise Exception,"Return processing |{0}".format(err) 
        return d_return 
    except Exception,error:
        log.debug(">>> {0} >> Failure! mesh: '{1}' | raysource: {2} | rayDir {3}".format(_str_func,mesh,raySource,rayDir))
        log.debug(">>> {0} >> error: {1}".format(_str_func,error))
        return None

def findMeshIntersections_OM1(mesh, raySource, rayDir, maxDistance = 1000, tolerance = .1):
    """
    Return the closest points on a surface from a raySource and rayDir. Can't process uv point for surfaces yet
    Thanks to Deane @ https://groups.google.com/forum/?fromgroups#!topic/python_inside_maya/n6aJq27fg0o%5B1-25%5D
    Thanks to Samaneh Momtazmand for doing the r&d to get this working with surfaces

    Note -- result hit points will be converted from apiSpace to maya space

    :parameters:
        mesh(string) | mesh/surface shape
        raySource(double3) | point from which to cast in world space
        rayDir(vector) | world space vector
    maxDistance(value) | Maximum cast distance 

    :returns:
        Dict ------------------------------------------------------------------
    'source'(double3) |  point from which we cast
    'hits'(list) | world space points
    'uvs'(list) | uv on surface of hit | only works for mesh surfaces

    :raises:
    Exception | if reached

    """      
    try:
        _str_func = 'findMeshIntersections_OM1'

        try:
            """if VALID.isListArg(mesh):
                log.debug("{0}>>> list provided. Using first : {1}".format(_str_func,mesh))
                mesh = mesh[0]	    
            if len(mc.ls(mesh))>1:
                raise StandardError,"{0}>>> More than one mesh named: {1}".format(_str_func,mesh)
            #_str_objType = search.returnObjectType(mesh)
            _str_objType = VALID.get_mayaType(mesh)
            log.debug("|{0}| >> mesh: {1} | type:{2}".format(_str_func,mesh,_str_objType))
            if _str_objType not in ['mesh','nurbsSurface']:
                raise ValueError,"Object type not supported | type: {0}".format(_str_objType)"""

            _str_objType = VALID.get_mayaType(mesh)
            if _str_objType not in ['mesh','nurbsSurface']:
                raise ValueError,"Object type not supported | type: {0}".format(_str_objType)

            #Create an empty selection list.
            selectionList = om.MSelectionList()

            #Convert the 'raySource' parameter into an MFloatPoint.
            #raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])
            mPoint_raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])

            #Convert the 'rayDir' parameter into an MVector.`
            mVec_rayDirection = om.MFloatVector(rayDir[0], rayDir[1], rayDir[2])

            #Create an empty MFloatPoint to receive the hit point from the call.
            mPointArray_hits = om.MFloatPointArray()

            #centerPointVector = om.MFloatVector(centerPoint[0],centerPoint[1],centerPoint[2]) 
            #rayDir = om.MFloatPoint(centerPointVector - raySourceVector)
            maxDist = maxDistance
            spc = om.MSpace.kWorld	

        except Exception,error:
            raise ValueError,"Validation fail |{0}".format(error)    

        try:
            if _str_objType == 'nurbsSurface': 
                log.debug("|{0}| >>  Surface cast mode".format(_str_func))
                #centerPoint = mc.xform(mesh, q=1, ws=1, t=1)    
                #surfaceShape = mc.listRelatives(mesh, s=1)[0]

                mPointArray_hits = om.MPointArray()
                mPoint_raySource = om.MPoint(raySource[0], raySource[1], raySource[2])
                mVec_rayDirection = om.MVector(rayDir[0], rayDir[1], rayDir[2])

                selectionList = om.MSelectionList()
                selectionList.add(mesh)
                surfacePath = om.MDagPath()
                selectionList.getDagPath(0, surfacePath)
                surfaceFn = om.MFnNurbsSurface(surfacePath)

                #Get the closest intersection.
                mPointArray_u = om.MDoubleArray()
                mPointArray_v = om.MDoubleArray()	
                spc = om.MSpace.kWorld

                #Get the closest intersection.
                '''
                d_kws = {'raySource':mPoint_raySource,
                         'rayDirection':mVec_rayDirection,
                         'u':u,
                         'v':v,
                         'mPointArray':mPointArray_hits,
                         'space':spc}
                for k in d_kws.keys():
                    print ("# {0} | {1}".format(k,d_kws[k]))
                '''
                gotHit = surfaceFn.intersect(mPoint_raySource,
                                             mVec_rayDirection,
                                             mPointArray_u,mPointArray_v,mPointArray_hits,
                                             tolerance,
                                             spc,
                                             False,#Distance
                                             None,#DistanceArray
                                             False,#ExactHit
                                             None)


            elif _str_objType == 'mesh':
                log.debug("{0} | Mesh cast mode".format(_str_func))

                #Put the mesh's name on the selection list.
                selectionList.add(mesh)

                #Create an empty MDagPath object.
                meshPath = om.MDagPath()

                #Get the first item on the selection list (which will be our mesh)
                #as an MDagPath.
                selectionList.getDagPath(0, meshPath)

                #Create an MFnMesh functionset to operate on the node pointed to by
                #the dag path.
                meshFn = om.MFnMesh(meshPath)

                #Set up a variable for each remaining parameter in the
                #MFnMesh::closestIntersection call. We could have supplied these as
                #literal values in the call, but this makes the example more readable.
                bothDirections = False
                sortIds = False
                noFaceIds = None
                noTriangleIds = None
                noHitParam = None
                noSortHits = False
                noHitFace = None
                noHitTriangle = None
                noHitBary1 = None
                noHitBary2 = None
                noAccelerator = None      

                gotHit = meshFn.allIntersections(mPoint_raySource,
                                                 mVec_rayDirection,
                                                 noFaceIds,
                                                 noTriangleIds,
                                                 sortIds,
                                                 om.MSpace.kWorld,
                                                 maxDist,
                                                 bothDirections,
                                                 noAccelerator,
                                                 noSortHits,
                                                 mPointArray_hits, noHitParam, noHitFace, noHitTriangle, noHitBary1, noHitBary2,tolerance)                    


                #Get the closest intersection.
                """
                """
            else : raise ValueError,"Wrong surface type!"
        except Exception,error:
            raise Exception,"Cast fail |{0}".format(error) 

        #Return the intersection as a Pthon list.
        d_return = {}
        l_hits = []
        l_uv = []	
        l_rawUV = []
        l_normals = []
        if gotHit:
            for i in range( mPointArray_hits.length() ):
                try:
                
                    l_hits.append( MATH.get_space_value( [mPointArray_hits[i].x, mPointArray_hits[i].y,mPointArray_hits[i].z] ))
        
                    #Thank you Mattias Bergbom, http://bergbom.blogspot.com/2009/01/float2-and-float3-in-maya-python-api.html
                    mPoint_hit = om.MPoint(mPointArray_hits[i]) # Thank you Capper on Tech-artists.org          
                    log.debug("{0} | Hit! [{1},{2},{3}]".format(_str_func,mPoint_hit.x, mPoint_hit.y, mPoint_hit.z))
        
        
                    #for i4,item in enumerate(gotHit):
                    #log.debug("|{2}| >> {0} : {1}".format(i4,item,_str_func))
                    pArray = [0.0,0.0]
                    x1 = om.MScriptUtil()
                    x1.createFromList( pArray, 2 )
                    uvPoint = x1.asFloat2Ptr()
                    uvSet = None
                    closestPolygon=None
                    if _str_objType == 'mesh':
                        uvReturn = meshFn.getUVAtPoint(mPoint_hit,uvPoint,om.MSpace.kWorld)
                        uValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0) or False
                        vValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1) or False
                        if uValue and vValue:
                            l_uv.append([uValue,vValue])
    
                        #....normal
                        try:
                            mVector_normal = om.MVector()
                            meshFn.getClosestNormal(mPoint_hit,mVector_normal,om.MSpace.kWorld)
                            l_normals.append([mVector_normal.x, mVector_normal.y, mVector_normal.z])
                        except Exception,err:
                            log.debug(">>> {0} >> Failed to process normal: {1} | err: {2}".format(_str_func,i,err))
                            l_normals.append([0,0,0])
    
                    else:#Nurbs
                        uRaw = mPointArray_u[i]
                        vRaw =  mPointArray_v[i]
    
                        log.debug("Raw: {0} | {1}".format(uRaw,vRaw))
                        __d = DIST.get_normalized_uv(mesh,uRaw,vRaw)#normalize data
    
                        l_rawUV.append([uRaw,vRaw])
                        l_uv.append(__d['uv'])
    
                        #....normal
                        try:
                            _res = surfaceFn.normal( uRaw, vRaw,om.MSpace.kWorld)
                            l_normals.append([_res.x, _res.y, _res.z])
                        except Exception,err:
                            log.debug(">>> {0} >> Failed to process normal: {1} | err: {2}".format(_str_func,i,err))
                            l_normals.append([0,0,0])
                        
                except Exception,err:
                    log.debug(">>> {0} >> Failed to process hit: {1} | err: {2}".format(_str_func,i,err))
                    continue

            try:            
                d_return['hits'] = l_hits
                d_return['source'] = [mPoint_raySource.x,mPoint_raySource.y,mPoint_raySource.z]	    
                if l_uv:
                    d_return['uvs'] = l_uv
                if l_rawUV:
                    d_return['uvsRaw'] = l_rawUV
                if l_normals:
                    d_return['normals'] = l_normals
            except Exception,err:
                log.debug(">>> {0} >> Processing fail".format(_str_func))
                raise Exception,err
        return d_return 
    except Exception,error:
        log.error(">>> {0} >> Failure! mesh: '{1}' | raysource: {2} | rayDir {3}".format(_str_func,mesh,raySource,rayDir))
        log.error(">>> {0} >> error: {1}".format(_str_func,error))        
        return None


def findMeshIntersectionFromObjectAxis(mesh, obj, axis = 'z+', vector = False, maxDistance = 1000, firstHit = True):
    """
    Find mesh intersections for an object's axis

    Note -- result hit points will be converted from apiSpace to maya space

    :parameters:
        mesh(string) | Surface to cast at
        obj(string) | transform to cast from
        axis(string) | Axis to cast
        vector(double3) | vector to cast
        maxDistance(float) | max cast range
        firstHit(bool) | single return per mesh

    :returns:
        Dict ------------------------------------------------------------------
    'source'(double3) |  point from which we cast
    'hit' | only there for firstHit and single mesh or closestInRange
    'hits'(list) | world space points
    'uvs'(dict) | uv on surface of hit
    'near' | nearest hit
    'far' | furthest hit

    :raises:
    Exception | if reached
    """
    try:
        _str_func = 'findMeshIntersectionFromObjectAxis'
        log.debug(">>> %s >> "%_str_func + "="*75) 
        _mesh = VALID.listArg(mesh)
        _oneMesh = False
        if len(_mesh) == 1:
            _oneMesh = True
        if not vector or type(vector) not in [list,tuple]:
            d_matrixVectorIndices = {'x':[0,1,2],
                                     'y': [4,5,6],
                                     'z' : [8,9,10]}
            matrix = mc.xform(obj, q=True,  matrix=True, worldSpace=True)

            #>>> Figure out our vector
            if axis not in dictionary.stringToVectorDict.keys():
                log.error("findMeshIntersectionFromObjectAxis axis arg not valid: '%s'"%axis)
                return False
            if list(axis)[0] not in d_matrixVectorIndices.keys():
                log.error("findMeshIntersectionFromObjectAxis axis arg not in d_matrixVectorIndices: '%s'"%axis)
                return False  
            vector = [matrix[i] for i in d_matrixVectorIndices.get(list(axis)[0])]
            if list(axis)[1] == '-':
                for i,v in enumerate(vector):
                    vector[i]=-v

        #self._posBuffer.append(hit)  
        #self.startPoint = self.convertPosToLocalSpace( buffer['source'] )
        #self.d_meshPos[m].append(hit)
        #self.d_meshUV[m].append(buffer['uv'])
        _l_posBuffer = []
        _l_uvBuffer = []
        _source = None

        _d_meshPos = {}
        _d_meshUV = {}
        for m in _mesh:
            _b = {}
            if firstHit:
                try:_b = findMeshIntersection(m, distance.returnWorldSpacePosition(obj), rayDir=vector, maxDistance = maxDistance)
                except:log.error("{0} mesh failed to get hit: {1}".format(_str_func,m))
                #if _oneMesh:return _b
                if not _d_meshUV.get(m):_d_meshUV[m] = []
                if not _d_meshPos.get(m):_d_meshPos[m] = []
                if _b:
                    _l_posBuffer.append(_b['hit'])
                    _uv = _b.get('uv')
                    _d_meshUV[m].append(_uv)
                    _d_meshPos[m].append(_b['hit'])								    
                    #_l_uvBuffer.append("{0}.uv[{1},{2}]".format(m,_uv[0],_uv[1]))
            else:
                try:_b = findMeshIntersections(m, distance.returnWorldSpacePosition(obj), rayDir=vector, maxDistance = maxDistance)
                except:log.error("{0} mesh failed to get hit: {1}".format(_str_func,m))	
                #if _oneMesh:return _b	
                if not _d_meshUV.get(m):_d_meshUV[m] = []
                if not _d_meshPos.get(m):_d_meshPos[m] = []
                if _b:
                    _uvs = _b['uvs']		
                    for i,h in enumerate(_b['hits']):
                        _uv = _uvs[i]
                        _l_posBuffer.append(h)
                        _d_meshUV[m].append(_uv)
                        _d_meshPos[m].append(h)						
                        #_l_uvBuffer.append("{0}.uv[{1},{2}]".format(m,_uv[0],_uv[1]))
            if _b:
                if _source == None:
                    _source = _b['source']

        if not _l_posBuffer:
            log.info("{0} No hits detected. cast: {1} | mesh{2} | axis: {3}".format(_str_func,obj,mesh,axis))
            return {}
        _near = distance.returnClosestPoint(_source, _l_posBuffer)
        _furthest = distance.returnFurthestPoint(_source,_l_posBuffer)
        _d = {'source':_source, 'near':_near, 'far':_furthest, 'hits':_l_posBuffer, 'uvs':_d_meshUV, 'meshHits':_d_meshPos}
        if firstHit:
            _d['hit'] = _near
        else:_d['hit'] = _furthest
        return _d
    except Exception,error:
        log.error(">>> %s >> mesh: %s | obj: %s | axis %s | vector: %s | error: %s"%(_str_func,mesh,obj,axis,vector,error))
        return None

def findMeshMidPointFromObject(mesh,obj,axisToCheck = ['x','z'],
                               vector = False, maxDistance = 1000, maxIterations = 10,**kws):
    try:#findMeshMidPointFromObject
        _str_func = 'findMeshMidPointFromObject'
        log.debug(">>> %s >> "%_str_func + "="*75)             
        if len(mc.ls(mesh))>1:
            raise StandardError,"findMeshMidPointFromObject>>> More than one mesh named: %s"%mesh      
        if type(axisToCheck) not in [list,tuple]:axisToCheck=[axisToCheck]
        axis = ['x','y','z']
        for a in axisToCheck:
            if a not in axis:
                raise StandardError,"findMeshMidPointFromObject>>> Not a valid axis : %s not in ['x','y','z']"%axisToCheck
        l_lastPos = []
        loc = locators.locMeObjectStandAlone(obj)
        for i in range(maxIterations):
            l_positions = []
            for a in axisToCheck:
                log.debug("firing: %s"%a)
                d_posReturn = findMeshIntersectionFromObjectAxis(mesh, loc, axis = '%s+'%a,vector=vector,maxDistance = maxDistance)
                d_negReturn = findMeshIntersectionFromObjectAxis(mesh, loc, axis = '%s-'%a,vector=vector,maxDistance = maxDistance)

                if 'hit' in d_posReturn.keys() and d_negReturn.keys():
                    l_pos = [d_posReturn.get('hit'),d_negReturn.get('hit')]
                    pos = distance.returnAveragePointPosition(l_pos)          
                    l_positions.append(pos)
                else:
                    raise RuntimeError,"No hit deteted. Object isn't in the mesh"
            if len(l_positions) == 1:
                l_pos =  l_positions[0]
            else:
                l_pos =  distance.returnAveragePointPosition(l_positions)
            if l_lastPos:dif = cgmMath.mag( cgmMath.list_subtract(l_pos,l_lastPos) )
            else:dif = 'No last'
            log.debug("findMeshMidPointFromObject>>> Step : %s | dif: %s | last: %s | pos: %s "%(i,dif,l_lastPos,l_pos)) 					
            if l_lastPos and cgmMath.isVectorEquivalent(l_lastPos,l_pos,2):
                log.debug("findMeshMidPointFromObject>>> Match found step: %s"%(i))
                mc.delete(loc)
                return l_pos
            mc.move(l_pos[0],l_pos[1],l_pos[2],loc,ws=True)
            l_lastPos = l_pos#If we get to here, add the current
        mc.delete(loc)    
        return l_pos
    except StandardError,error:
        for kw in [mesh,obj,axisToCheck,vector,maxDistance,maxIterations]:
            log.debug("%s"%kw)  
        try:mc.delete(loc)
        except:pass
        raise StandardError, "%s >> error: %s"%(_str_func,error)

def findFurthestPointInRangeFromObject(mesh,obj,axis = 'z+', pierceDepth = 4,
                                       vector = False, maxDistance = 1000):
    """ Find the furthest point in range on an axis. Useful for getting to the outershell of a mesh """
    try:
        _str_func = 'findFurthestPointInRangeFromObject'
        log.debug(">>> %s >> "%_str_func + "="*75)             
        if len(mc.ls(mesh))>1:
            raise StandardError,"findFurthestPointInRangeFromObject>>> More than one mesh named: %s"%mesh      
        #>>>First cast to get our initial range
        d_firstcast = findMeshIntersectionFromObjectAxis(mesh, obj, axis = axis, vector=vector, maxDistance = maxDistance)
        if not d_firstcast.get('hit'):
            raise StandardError,"findFurthestPointInRangeFromObject>>> first cast failed to hit"

        baseDistance = distance.returnDistanceBetweenPoints(distance.returnWorldSpacePosition(obj),d_firstcast['hit'])
        log.debug("findFurthestPointInRangeFromObject>>>baseDistance: %s"%baseDistance)
        castDistance = baseDistance + pierceDepth
        log.debug("findFurthestPointInRangeFromObject>>>castDistance: %s"%castDistance)

        l_positions = []

        d_castReturn = findMeshIntersectionFromObjectAxis(mesh, obj, axis=axis, maxDistance = castDistance, firstHit=False) or {}
        log.debug("2nd castReturn: %s"%d_castReturn)
        if d_castReturn.get('hits'):
            closestPoint = distance.returnFurthestPoint(distance.returnWorldSpacePosition(obj),d_castReturn.get('hits')) or False
            d_castReturn['hit'] = closestPoint
        return d_castReturn
    except StandardError,error:
        for kw in [mesh,obj,axis,pierceDepth,vector,maxDistance]:
            log.debug("%s"%kw)
        raise StandardError, "%s >> error: %s"%(_str_func,error)


def returnNormalizedUVOLD(mesh, uValue, vValue):
    """
    uv Values from many functions need to be normalized to be correct when using those values for other functions

    The calculcaion for doing so is 
    size = maxV - minV
    sum = rawV + minV
    normalValue = sum / size

    :parameters:
    mesh(string) | Surface to normalize to
    uValue(float) | uValue to normalize 
    vValue(float) | vValue to normalize 

    :returns:
    Dict ------------------------------------------------------------------
    'uv'(double2) |  point from which we cast
    'uValue'(float) | normalized uValue
    'vValue'(float) | normalized vValue

    :raises:
    Exception | if reached

    """      
    try:
        _str_func = 'returnNormalizedUV'

        try:#Validation ----------------------------------------------------------------
            mesh = VALID.objString(mesh,'nurbsSurface', calledFrom = _str_func)
            if len(mc.ls(mesh))>1:
                raise StandardError,"{0}>>> More than one mesh named: {1}".format(_str_func,mesh)
            _str_objType = search.returnObjectType(mesh)

            l_shapes = mc.listRelatives(mesh, shapes=True)
            if len(l_shapes)>1:
                log.debug( "More than one shape found. Using 0. targetSurface : %s | shapes: %s"%(mesh,l_shapes) )
            #mi_shape = cgmMeta.validateObjArg(l_shapes[0],cgmMeta.cgmNode,noneValid=False)

            uMin = attributes.doGetAttr(l_shapes[0],'mnu')
            uMax = attributes.doGetAttr(l_shapes[0],'mxu')
            vMin = attributes.doGetAttr(l_shapes[0],'mnv')
            vMax = attributes.doGetAttr(l_shapes[0],'mxv')         
            """uMin = mi_shape.mnu
            uMax = mi_shape.mxu
            vMin = mi_shape.mnv
            vMax = mi_shape.mxv"""

        except Exception,error:raise Exception,"Validation failure | {0}".format(error) 		

        try:#Calculation ----------------------------------------------------------------
            uSize = uMax - uMin
            vSize = vMax - vMin

            uSum = uMin + uValue
            vSum = vMin + vValue

            uNormal = uSum / uSize
            vNormal = vSum / vSize
        except Exception,error:raise Exception,"Calculation |{0}".format(error) 		

        try:
            d_return = {'uv':[uNormal,vNormal],'uValue':uNormal,'vValue':vNormal}
            return d_return 
        except Exception,error:raise Exception,"Return prep |{0}".format(error) 		

    except Exception,error:
        log.error(">>> {0} >> Failure! mesh: '{1}' | uValue: {2} | vValue {3}".format(_str_func,mesh,uValue,vValue))
        log.error(">>> {0} >> error: {1}".format(_str_func,error))        
        return None



