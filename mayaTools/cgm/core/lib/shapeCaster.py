"""
Module for building controls for cgmModules

"""
# From Python =============================================================
import copy
import re
import time

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
import cgm.core.cgm_General as cgmGEN
from cgm.core.classes import SnapFactory as Snap
from cgm.core.lib import rayCaster as RayCast
from cgm.core.lib import curve_Utils as crvUtils
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.position_utils as POS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.lib import guiFactory

reload(RayCast)
reload(Snap)
from cgm.lib import (cgmMath,
                     locators,
                     modules,
                     distance,
                     dictionary,
                     rigging,
                     search,
                     curves,
                     lists,
                     )

from cgm.core.lib import nameTools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def returnBaseControlSize(mi_obj,mesh,axis=True,closestInRange = True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Figure out the base size for a control from a point in space within a mesh

    ARGUMENTS:
    mi_obj(cgmObject instance)
    mesh(obj) = ['option1','option2']
    axis(list) -- what axis to check

    RETURNS:
    axisDistances(dict) -- axis distances, average
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """       
    try:#>>Figure out the axis to do
        log.info(mi_obj)	
        mi_obj = cgmMeta.validateObjArg(mi_obj,cgmMeta.cgmObject,noneValid = True)
        if not mi_obj:
            raise ValueError,"mi_obj kw: {0} ".format(mi_obj)

        _str_func = "returnBaseControlSize(%s)"%mi_obj.p_nameShort
        log.debug(">> %s "%(_str_func) + "="*75)
        start = time.clock()

        log.debug("%s >> mesh: %s "%(_str_func,mesh))  
        log.debug("%s >> axis: %s "%(_str_func,axis)) 

        try:
            d_axisToDo = {}
            if axis == True:
                axis = ['x','y','z']
            if type(axis) in [list,tuple]:
                for a in axis:
                    if a in dictionary.stringToVectorDict.keys():
                        if list(a)[0] in d_axisToDo.keys():
                            d_axisToDo[list(a)[0]].append( a )
                        else:
                            d_axisToDo[list(a)[0]] = [ a ]

                    elif type(a) is str and a.lower() in ['x','y','z']:
                        buffer = []
                        buffer.append('%s+'%a.lower())
                        buffer.append('%s-'%a.lower())  
                        d_axisToDo[a.lower()] = buffer
                    else:
                        log.warning("Don't know what with: '%s'"%a)
            log.debug("%s >> d_axisToDo: %s "%(_str_func,d_axisToDo))  
            if not d_axisToDo:return False	    
        except Exception,error:
            raise Exception,"Axis check | {0}".format(error)


        #>>
        d_returnDistances = {}
        for axis in d_axisToDo:
            log.debug("Checking: %s"%axis)
            directions = d_axisToDo[axis]
            if len(directions) == 1:#gonna multiply our distance 
                try:
                    info = RayCast.findMeshIntersectionFromObjectAxis(mesh,mi_obj.mNode,directions[0])
                    d_returnDistances[axis] = (distance.returnDistanceBetweenPoints(info['near'],mi_obj.getPosition()) *2)
                except Exception,error:
                    raise Exception,"raycast | %s"%error
            else:
                try:
                    info1 = RayCast.findMeshIntersectionFromObjectAxis(mesh,mi_obj.mNode,directions[0])
                    info2 = RayCast.findMeshIntersectionFromObjectAxis(mesh,mi_obj.mNode,directions[1])
                    if info1 and info2:
                        d_returnDistances[axis] = distance.returnDistanceBetweenPoints(info1['near'],info2['near'])                    
                except Exception,error:
                    raise Exception,"raycast | %s"%error

        if not d_returnDistances:
            raise Exception,"No intersections found"

        #>>Add the average
        log.debug("%s >> d_returnDistances: %s "%(_str_func,d_returnDistances))        	
        d_returnDistances['average'] = (sum([d_returnDistances.get(k) for k in d_returnDistances.keys()]))/len(d_returnDistances.keys())

        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)     	
        return d_returnDistances    
    except Exception,error:
        raise Exception," returnBaseControlSize | {0}".format(error)



def joinCurves(targetObjects, mode = 'simple', curveDegree = 1):
    try:
        ml_targetObjects = cgmMeta.validateObjListArg(targetObjects)
        d_objInfo = {}
        for i_obj in ml_targetObjects:
            d_buffer = {}
            if i_obj.getMayaType() != 'nurbsCurve':
                raise StandardError,"joinCurve>> %s is not a 'nurbsCurve'. Type: %s"%(i_obj.getShortName(),i_obj.getMayaType())
            l_components = i_obj.getComponents('ep')
            l_componentIndices = []
            for c in l_components:
                l_componentIndices.append( int(c.split('[')[-1].split(']')[0]) )	
            d_buffer['indices'] = l_componentIndices
            d_buffer['components'] = l_components	
            d_buffer['indexMid'] = int(len(l_componentIndices)/2)
            d_buffer['midComponent'] = l_components[ d_buffer['indexMid'] ]
            d_objInfo[i_obj] = d_buffer


        #components
        l_created = []
        l_toDo = []
        l_nestedPos = []
        if mode == 'simple':
            for ep in [0,'mid',-1]:
                l_pos = []
                for i_crv in ml_targetObjects:
                    if ep == 'mid':ep = d_objInfo[i_crv]['indexMid']
                    l_pos.append( cgmMeta.cgmNode(d_objInfo[i_crv]['components'][ep]).getPosition() )
                l_created.append( mc.curve(d=curveDegree,ep=l_pos,os =True) )#Make the curve
        elif mode == 'quartered':
            d_pntsConnect = {}
            for mObj in ml_targetObjects:
                l_pos = crvUtils.returnSplitCurveList( mObj.mNode, 5 ) 
                for i,p in enumerate(l_pos):
                    if not d_pntsConnect.get(i):d_pntsConnect[i] = []
                    d_pntsConnect[i].append(p)
            for k in d_pntsConnect.keys():
                l_created.append( mc.curve(d=curveDegree,ep=d_pntsConnect[k],os =True) )#Make the curve		    
        else:
            for idx in d_objInfo[d_objInfo.keys()[0]]['indices']:
                l_pos = []
                for i_crv in ml_targetObjects:
                    l_pos.append( cgmMeta.cgmNode(d_objInfo[i_crv]['components'][idx]).getPosition() )
                l_created.append( mc.curve(d=curveDegree,ep=l_pos,os =True) )#Make the curve	
        return l_created

    except StandardError,error:
        raise StandardError,"joinCurve>> Failure. targets: %s | error: %s"%(targetObjects,error)

def createWrapControlShape(targetObjects,
                           targetGeo = None,
                           latheAxis = 'z',aimAxis = 'y+',objectUp = 'y+',
                           points = 8,
                           curveDegree = 1,
                           insetMult = None,#Inset multiplier
                           minRotate = None, maxRotate = None,
                           posOffset = [],
                           rootOffset = [],#offset root before cast
                           rootRotate = None,
                           joinMode = False,
                           extendMode = None,
                           closedCurve = True,
                           l_specifiedRotates = None,
                           maxDistance = 1000,
                           closestInRange = True,
                           vectorOffset = None,
                           midMeshCast = False,
                           subSize = None,#For ball on loli for example
                           rotateBank = None,
                           joinHits = None,#keys to processed hits to see what to join
                           axisToCheck = ['x','y'],
                           **kws):#'segment,radial,disc' 
    """
    This function lathes an axis of an object, shoot rays out the aim axis at the provided mesh and returning hits. 
    it then uses this information to build a curve shape.

    :parameters:
        mesh(string) | Surface to cast at
    mi_obj(string/mObj) | our casting object
    latheAxis(str) | axis of the objec to lathe TODO: add validation
    aimAxis(str) | axis to shoot out of
    points(int) | how many points you want in the curve
    curveDegree(int) | specified degree
    minRotate(float) | let's you specify a valid range to shoot
    maxRotate(float) | let's you specify a valid range to shoot
    posOffset(vector) | transformational offset for the hit from a normalized locator at the hit. Oriented to the surface
    markHits(bool) | whether to keep the hit markers
    returnDict(bool) | whether you want all the infomation from the process.
    rotateBank (float) | let's you add a bank to the rotation object
    l_specifiedRotates(list of values) | specify where to shoot relative to an object. Ignores some other settings
    maxDistance(float) | max distance to cast rays
    closestInRange(bool) | True by default. If True, takes first hit. Else take the furthest away hit in range.

    :returns:
        Dict ------------------------------------------------------------------
    'source'(double3) |  point from which we cast
    'hit'(double3) | world space points | active during single return
    'hits'(list) | world space points | active during multi return
    'uv'(double2) | uv on surface of hit | only works for mesh surfaces

    :raises:
    Exception | if reached

    """     
    _str_func = "createWrapControlShape"
    log.debug(">> %s >> "%(_str_func) + "="*75)  
    _joinModes = []
    _extendMode = []

    if type(targetObjects) not in [list,tuple]:targetObjects = [targetObjects]
    targetGeo = VALID.objStringList(targetGeo, calledFrom = _str_func)


    assert type(points) is int,"Points must be int: %s"%points
    assert type(curveDegree) is int,"Points must be int: %s"%points
    assert curveDegree > 0,"Curve degree must be greater than 1: %s"%curveDegree
    if posOffset is not None and len(posOffset) and len(posOffset)!=3:raise StandardError, "posOffset must be len(3): %s | len: %s"%(posOffset,len(posOffset))
    if rootOffset is not None and len(rootOffset) and len(rootOffset)!=3:raise StandardError, "rootOffset must be len(3): %s | len: %s"%(rootOffset,len(rootOffset))
    if rootRotate is not None and len(rootRotate) and len(rootRotate)!=3:raise StandardError, "rootRotate must be len(3): %s | len: %s"%(rootRotate,len(rootRotate))

    if extendMode in ['loliwrap','cylinder','disc'] and insetMult is None:insetMult = 1
    for axis in ['x','y','z']:
        if axis in latheAxis.lower():latheAxis = axis

    log.debug("targetObjects: %s"%targetObjects)

    if len(aimAxis) == 2:single_aimAxis = aimAxis[0]
    else:single_aimAxis = aimAxis
    mAxis_aim = VALID.simpleAxis(aimAxis)
    log.debug("Single aim: %s"%single_aimAxis)
    log.debug("createWrapControlShape>> midMeshCast: %s"%midMeshCast)
    log.debug("|{0}| >> extendMode: {1}".format(_str_func,extendMode))            
    #>> Info
    l_groupsBuffer = []
    il_curvesToCombine = []
    l_sliceReturns = []
    #Need to do more to get a better size

    #>> Build curves
    #=================================================================
    #> Root curve #
    log.debug("RootRotate: %s"%rootRotate)
    mi_rootLoc = cgmMeta.cgmNode(targetObjects[0]).doLoc()
    if rootOffset:
        log.debug("rootOffset: %s"%rootOffset)
        mc.move(rootOffset[0],rootOffset[1],rootOffset[2], [mi_rootLoc.mNode], r=True, rpr = True, os = True, wd = True)
    if rootRotate is not None and len(rootRotate):
        log.debug("rootRotate: %s"%rootRotate)	
        mc.rotate(rootRotate[0],rootRotate[1],rootRotate[2], [mi_rootLoc.mNode], os = True,r=True)   

    #>> Root
    mi_rootLoc.doGroup()#Group to zero    
    if extendMode == 'segment':
        log.debug("segment mode. Target len: %s"%len(targetObjects[1:]))	
        if len(targetObjects) < 2:
            log.warning("Segment build mode only works with two objects or more")    
        else:
            if insetMult is not None:
                rootDistanceToMove = distance.returnDistanceBetweenObjects(targetObjects[0],targetObjects[1])
                log.debug("rootDistanceToMove: %s"%rootDistanceToMove)
                mi_rootLoc.__setattr__('t%s'%latheAxis,rootDistanceToMove*insetMult)
                #mi_rootLoc.tz = (rootDistanceToMove*insetMult)#Offset it

            #Notes -- may need to play with up object for aim snapping
            #mi_upLoc = cgmMeta.cgmNode(targetObjects[0]).doLoc()
            #mi_upLoc.doGroup()#To zero
            objectUpVector = dictionary.returnStringToVectors(objectUp)
            log.debug("objectUpVector: %s"%objectUpVector)		    
            #mi_uploc

            for i,obj in enumerate(targetObjects[1:]):
                log.debug("i: %s"%i)
                #> End Curve
                mi_endLoc = cgmMeta.cgmNode(obj).doLoc()
                aimVector = dictionary.returnStringToVectors(latheAxis+'-')
                log.debug("segment aimback: %s"%aimVector)		    
                #Snap.go(mi_endLoc.mNode,mi_rootLoc.mNode,move=False,aim=True,aimVector=aimVector,upVector=objectUpVector)
                #Snap.go(mi_endLoc.mNode,mi_rootLoc.mNode,move=False,orient=True)	
                SNAP.go(mi_endLoc.mNode,mi_rootLoc.mNode,position=False,rotation=True)		    

                mi_endLoc.doGroup()

                if i == len(targetObjects[1:])-1:
                    if insetMult is not None:
                        log.debug("segment insetMult: %s"%insetMult)			    
                        distanceToMove = distance.returnDistanceBetweenObjects(targetObjects[-1],targetObjects[0])
                        log.debug("distanceToMove: %s"%distanceToMove)
                        #mi_endLoc.tz = -(distanceToMove*insetMult)#Offset it  
                        mi_endLoc.__setattr__('t%s'%latheAxis,-(distanceToMove*insetMult))
                log.debug("segment lathe: %s"%latheAxis)
                log.debug("segment aim: %s"%aimAxis)
                log.debug("segment rotateBank: %s"%rotateBank)		    
                d_endCastInfo = createMeshSliceCurve(targetGeo,mi_endLoc,midMeshCast=midMeshCast,curveDegree=curveDegree,latheAxis=latheAxis,aimAxis=aimAxis,posOffset = posOffset,points = points,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank, l_specifiedRotates = l_specifiedRotates,axisToCheck = axisToCheck)  	
                l_sliceReturns.append(d_endCastInfo)
                mi_end = cgmMeta.cgmObject(d_endCastInfo['curve'])
                il_curvesToCombine.append(mi_end)
                mc.delete(mi_endLoc.parent)#delete the loc


    elif extendMode == 'radial':
        log.debug("|{0}| >> radial...".format(_str_func))            
        d_handleInner = createMeshSliceCurve(targetGeo,mi_rootLoc,midMeshCast=midMeshCast,curveDegree=curveDegree,latheAxis=latheAxis,aimAxis=aimAxis,posOffset = 0,points = points,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank, l_specifiedRotates = l_specifiedRotates,axisToCheck = axisToCheck)  
        mi_buffer = cgmMeta.cgmObject(d_handleInner['curve'])#instance curve	
        l_sliceReturns.append(d_handleInner)
        il_curvesToCombine.append(mi_buffer)    

    elif extendMode == 'disc':
        log.debug("|{0}| >> disc...".format(_str_func))            
        d_size = returnBaseControlSize(mi_rootLoc,targetGeo,axis=[aimAxis])#Get size
        #discOffset = d_size[ d_size.keys()[0]]*insetMult
        size = False
        l_absSize = [abs(i) for i in posOffset]
        if l_absSize:size = max(l_absSize) 
        if not size:
            d_size = returnBaseControlSize(mi_rootLoc,targetGeo,axis=[aimAxis])#Get size
            log.debug("d_size: %s"%d_size)
            size = d_size[ d_size.keys()[0]]*insetMult	

        discOffset = size
        log.debug("d_size: %s"%d_size)
        log.debug("discOffset is: %s"%discOffset)

        mi_rootLoc.__setattr__('t%s'%latheAxis,discOffset)
        if posOffset:
            tmp_posOffset = [posOffset[0]*.5,posOffset[1]*.5,posOffset[2]*.5]
        d_handleInnerUp = createMeshSliceCurve(targetGeo,mi_rootLoc,curveDegree=curveDegree,midMeshCast=midMeshCast,latheAxis=latheAxis,aimAxis=aimAxis,posOffset = tmp_posOffset,points = points,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank, l_specifiedRotates = l_specifiedRotates,axisToCheck = axisToCheck) 
        mi_buffer = cgmMeta.cgmObject(d_handleInnerUp['curve'])#instance curve	
        l_sliceReturns.append(d_handleInnerUp)
        il_curvesToCombine.append(mi_buffer) 

        mi_rootLoc.__setattr__('t%s'%latheAxis,-discOffset)
        d_handleInnerDown = createMeshSliceCurve(targetGeo,mi_rootLoc,curveDegree=curveDegree,midMeshCast=midMeshCast,latheAxis=latheAxis,aimAxis=aimAxis,posOffset = tmp_posOffset,points = points,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank,  l_specifiedRotates = l_specifiedRotates,axisToCheck = axisToCheck) 
        mi_buffer = cgmMeta.cgmObject(d_handleInnerDown['curve'])#instance curve	
        l_sliceReturns.append(d_handleInnerDown)
        il_curvesToCombine.append(mi_buffer) 

        mi_rootLoc.tz = 0

    elif extendMode == 'cylinder':
        log.debug("|{0}| >> cylinder...".format(_str_func))            
        d_size = returnBaseControlSize(mi_rootLoc,targetGeo,axis=[aimAxis])#Get size
        discOffset = d_size[ d_size.keys()[0]]*insetMult
        log.debug("d_size: %s"%d_size)
        log.debug("discOffset is: %s"%discOffset)

        mi_rootLoc.__setattr__('t%s'%latheAxis,discOffset)
        d_handleInnerUp = createMeshSliceCurve(targetGeo,mi_rootLoc,curveDegree=curveDegree,midMeshCast=midMeshCast,latheAxis=latheAxis,aimAxis=aimAxis,posOffset = posOffset,points = points,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank, l_specifiedRotates = l_specifiedRotates,axisToCheck = axisToCheck)  
        mi_buffer = cgmMeta.cgmObject(d_handleInnerUp['curve'])#instance curve	
        l_sliceReturns.append(d_handleInnerUp)
        il_curvesToCombine.append(mi_buffer) 

        mi_rootLoc.__setattr__('t%s'%latheAxis,0)

    elif extendMode == 'loliwrap':
        log.debug("|{0}| >> lolipop...".format(_str_func))            
        #l_absSize = [abs(i) for i in posOffset]
        size = False
        #if l_absSize:
            #log.debug("l_absSize: %s"%l_absSize)
            #size = max(l_absSize)*1.25
        if subSize is not None:
            size = subSize
        if not size:
            d_size = returnBaseControlSize(mi_rootLoc,targetGeo,axis=[aimAxis])#Get size
            log.info("d_size: %s"%d_size)
            l_size = d_size[single_aimAxis]
            size = l_size/3
        log.info("loli size: %s"%size)
        i_ball = cgmMeta.cgmObject(curves.createControlCurve('sphere',size = size))

    elif extendMode == 'endCap':
        log.debug("|{0}| >> endCap...".format(_str_func))            
        returnBuffer1 = createMeshSliceCurve(targetGeo,mi_rootLoc.mNode,
                                             aimAxis = '{0}+'.format(latheAxis),
                                             latheAxis = objectUp[0],
                                             curveDegree=curveDegree,
                                             maxDistance=maxDistance,
                                             closestInRange=closestInRange,
                                             closedCurve=False,
                                             l_specifiedRotates=[-90,-60,-30,0,30,60,90],	                                      
                                             posOffset = posOffset)
        mi_rootLoc.rotate = [0,0,0]
        mi_rootLoc.__setattr__('r%s'%latheAxis,90)
        returnBuffer2 = createMeshSliceCurve(targetGeo,mi_rootLoc.mNode,
                                             aimAxis = '{0}+'.format(latheAxis),
                                             latheAxis = objectUp[0],
                                             curveDegree=curveDegree,
                                             maxDistance=maxDistance,	                                     
                                             closedCurve=False,
                                             closestInRange=closestInRange,	                                     
                                             l_specifiedRotates=[-90,-60,-30,0,30,60,90],	                                      
                                             posOffset = posOffset)	
        l_sliceReturns.extend([returnBuffer1,returnBuffer2])
        il_curvesToCombine.append(cgmMeta.cgmObject(returnBuffer1))
        il_curvesToCombine.append(cgmMeta.cgmObject(returnBuffer2))
        mi_rootLoc.rotate = [0,0,0]

    #Now cast our root since we needed to move it with segment mode before casting
    if extendMode == 'cylinder':
        log.debug("|{0}| >> cylinder move...".format(_str_func))                    
        mi_rootLoc.__setattr__('t%s'%latheAxis,-discOffset)

    log.debug("|{0}| >> Rootcast...".format(_str_func))                    

    d_rootCastInfo = createMeshSliceCurve(targetGeo,mi_rootLoc,curveDegree=curveDegree,minRotate=minRotate,maxRotate=maxRotate,latheAxis=latheAxis,midMeshCast=midMeshCast,aimAxis=aimAxis,posOffset = posOffset,points = points,vectorOffset=vectorOffset,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank, l_specifiedRotates = l_specifiedRotates,axisToCheck = axisToCheck)  
    #d_rootCastInfo = createMeshSliceCurve(targetGeo,mi_rootLoc,**kws)  
    log.debug("|{0}| >> Rootcast done".format(_str_func) + cgmGEN._str_subLine)                    

    if extendMode == 'disc':
        l_sliceReturns.insert(1,d_rootCastInfo)	
    else:
        l_sliceReturns.insert(0,d_rootCastInfo)

    #Special loli stuff
    if extendMode == 'loliwrap':
        SNAP.go(i_ball.mNode,mi_rootLoc.mNode,True, True)#Snap to main object

        #log.debug("hitReturns: %s"%d_rootCastInfo['hitReturns'])
        #cgmGEN.walk_dat(d_rootCastInfo['hitReturns'],'hitReturns')
        
        mi_crv = cgmMeta.cgmObject( d_rootCastInfo['curve'] )
        """
        d_return = RayCast.findMeshIntersectionFromObjectAxis(targetGeo,mi_rootLoc.mNode,mAxis_aim.p_string) or {}
        if not d_return.get('hit'):
            log.info(d_return)
            raise ValueError,"No hit on loli check"
        pos = d_return.get('hit')
        dist = distance.returnDistanceBetweenPoints(i_ball.getPosition(),pos) * 2"""
        
        if vectorOffset is not None:
            dist = vectorOffset + subSize * 4
        else:
            dist = max(posOffset) + subSize * 4
            
        if '-' in aimAxis:
            distM = -dist
        else:
            distM = dist
        log.debug("distM: %s"%distM)

        #Move the ball
        pBuffer = i_ball.doGroup()
        i_ball.__setattr__('t%s'%single_aimAxis,distM)
        i_ball.parent = False
        mc.delete(pBuffer)
        
        uPos = distance.returnClosestUPosition(i_ball.mNode,mi_crv.mNode)

        SNAP.aim(i_ball.mNode,mi_rootLoc.mNode,aimAxis='z-')
        #if posOffset:
                #mc.move(posOffset[0]*3,posOffset[1]*3,posOffset[2]*3, [i_ball.mNode], r = True, rpr = True, os = True, wd = True)
        #Make the curve between the two 
        mi_traceCrv = cgmMeta.cgmObject( mc.curve(degree = 1, ep = [uPos,i_ball.getPosition()]) )

        #Combine
        il_curvesToCombine.extend([i_ball,mi_traceCrv])


    mi_root = cgmMeta.cgmObject(d_rootCastInfo['curve'])#instance curve
    il_curvesToCombine.append(mi_root)    

    mc.delete(mi_rootLoc.parent)#delete the loc

    l_curvesToCombine = [mi_obj.mNode for mi_obj in il_curvesToCombine]#Build our combine list before adding connectors         
    log.debug("|{0}| >> processed: {1}".format(_str_func,d_rootCastInfo['processedHits']))            

    if joinMode and extendMode not in ['loliwrap','endCap'] and len(l_sliceReturns)>1:
        if joinHits:
            keys = d_rootCastInfo['processedHits'].keys()
            keys.sort()
            #goodDegrees = []
            #for i,key in enumerate(keys):
                #if i in joinHits:
                #goodDegrees.append(key)
            goodDegrees = [key for i,key in enumerate(keys) if i in joinHits]
            log.debug("joinHits: %s"%joinHits)
            log.debug("goodDegrees: %s"%goodDegrees)	    
        else:
            goodDegrees = [key for key in d_rootCastInfo['processedHits'].keys()]
        #> Side Curves
        for degree in goodDegrees:
            l_pos = []	    
            for d in l_sliceReturns:
                l_pos.append( d['processedHits'].get(degree) or False )
            while False in l_pos:
                l_pos.remove(False)
            log.debug("l_pos: %s"%l_pos)
            if len(l_pos)>=2:
                try:
                    l_curvesToCombine.append( mc.curve(d=curveDegree,ep=l_pos,os =True) )#Make the curve
                except:
                    log.debug("createWrapControlShape>>> skipping curve fail: %s"%(degree))

    #>>Combine the curves
    newCurve = curves.combineCurves(l_curvesToCombine) 
    mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(targetObjects[0],False) )
    curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
    mc.delete(newCurve)

    #>>Copy tags and name
    mi_crv.doCopyNameTagsFromObject(targetObjects[0],ignore = ['cgmType','cgmTypeModifier'])
    mi_crv.addAttr('cgmType',attrType='string',value = 'controlCurve',lock=True)
    mi_crv.doName()                

    #Store for return
    return {'curve':mi_crv.mNode,'instance':mi_crv}  

def createMeshSliceCurve(mesh, mi_obj,latheAxis = 'z',aimAxis = 'y+',
                         points = 12, curveDegree = 3, minRotate = None, maxRotate = None, rotateRange = None,
                         posOffset = None, vectorOffset = None, markHits = False,rotateBank = None, closedCurve = True, maxDistance = 1000,
                         initialRotate = 0, offsetMode = 'vector', midMeshCast = False,
                         l_specifiedRotates = None, closestInRange = True,
                         returnDict = False,axisToCheck = ['x','y'],**kws):
    """
    This function lathes an axis of an object, shoot rays out the aim axis at the provided mesh and returning hits. 
    it then uses this information to build a curve shape.

    :parameters:
        mesh(string) | Surface to cast at
    mi_obj(string/mObj) | our casting object
    latheAxis(str) | axis of the objec to lathe TODO: add validation
    aimAxis(str) | axis to shoot out of
    points(int) | how many points you want in the curve
    curveDegree(int) | specified degree
    minRotate(float) | let's you specify a valid range to shoot
    maxRotate(float) | let's you specify a valid range to shoot
    posOffset(vector) | transformational offset for the hit from a normalized locator at the hit. Oriented to the surface
    markHits(bool) | whether to keep the hit markers
    returnDict(bool) | whether you want all the infomation from the process.
    rotateBank (float) | let's you add a bank to the rotation object
    l_specifiedRotates(list of values) | specify where to shoot relative to an object. Ignores some other settings
    maxDistance(float) | max distance to cast rays
    closestInRange(bool) | True by default. If True, takes first hit. Else take the furthest away hit in range.

    :returns:
        Dict ------------------------------------------------------------------
    'source'(double3) |  point from which we cast
    'hit'(double3) | world space points | active during single return
    'hits'(list) | world space points | active during multi return
    'uv'(double2) | uv on surface of hit | only works for mesh surfaces

    :raises:
    Exception | if reached

    """       
    _str_func = 'createMeshSliceCurve'

    try:
        mi_obj = cgmMeta.validateObjArg(mi_obj,mType = 'cgmObject', noneValid = True)
        if not mi_obj:
            return False

        log.debug("mi_obj: {0}".format(mi_obj.mNode))

        mesh = VALID.objStringList(mesh,['mesh','nurbsSurface'], calledFrom = _str_func)
        #if len(mc.ls(mesh))>1:
            #log.error("{0}>>> More than one mesh named. Using first: {1}".format(_str_func,mesh))
        #mesh = mesh[0]
        log.debug("mesh: {0}".format(mesh))
        log.debug("points: {0}".format(points))

    except Exception,error:
        raise ValueError,"Validation fail | {0}".format(error) 


    #>>> Info #================================================================
    guiFactory.doProgressWindow(winName='Mesh Slice...', 
                                statusMessage='Progress...', 
                                startingProgress=1, 
                                interruptableState=True)		
    mi_loc = mi_obj.doLoc()
    mi_loc.doGroup()
    l_pos = []
    d_returnDict = {}
    d_hitReturnFromValue = {}
    d_processedHitFromValue = {}
    d_rawHitFromValue = {}
    pos_base = mi_obj.p_position

    for axis in ['x','y','z']:
        if axis in latheAxis:latheAxis = axis

    log.debug("latheAxis: %s"%latheAxis)
    if rotateBank is not None:#we need a bank  axis
        l_axisCull = ['x','y','z']
        if latheAxis!=aimAxis:l_axisCull.remove(latheAxis)
        log.debug(latheAxis)
        if len(aimAxis) == 2: aimCull = aimAxis[0].lower()
        else: aimCull = aimAxis.lower()
        if latheAxis!=aimCull:l_axisCull.remove(aimCull)
        log.debug(aimCull)	
        log.debug("Bank rotate: %s"%l_axisCull)
        bankAxis = l_axisCull[0]

    #posOffset
    if offsetMode == 'vector':
        if vectorOffset is None:
            if posOffset is not None:
                vectorOffset = max(posOffset)
    log.debug("|{0}| >> vectorOffset: {1}".format(_str_func, vectorOffset))
    

    if posOffset is not None:
        if MATH.is_vector_equivalent(posOffset,[0,0,0]):
            posOffset = None

    #midMeshCast
    if midMeshCast:
        axisToCheck = axisToCheck or [a for a in ['x','y','z'] if a != latheAxis]
        log.debug("createMeshSliceCurve>> axisToCheck: %s"%axisToCheck)
        try:
            Snap.go(mi_loc.parent,mesh[0],True,False,midSurfacePos=True, axisToCheck = axisToCheck)
        except:
            log.error("createMeshSliceCurve >> failed to midMeshCast")

    #Rotate obj 
    mi_rotObj = mi_loc
    if rotateBank is not None and type(rotateBank) is not list:
        rotateGroup = mi_loc.doGroup(True)
        mi_rotObj = cgmMeta.cgmObject(rotateGroup)
        mi_loc.__setattr__('rotate%s'%bankAxis.capitalize(),rotateBank)

    #Figure out the rotateBaseValue
    if minRotate is not None:
        rotateFloor = minRotate
    else:
        rotateFloor = 0
    if maxRotate is not None:
        rotateCeiling = maxRotate
    else:
        rotateCeiling = 360

    #>>> Get our rotate info
    #================================================================
    l_rotateSettings = []

    if l_specifiedRotates and type(l_specifiedRotates) in [list,tuple]:
        #See if it's good
        for f in l_specifiedRotates:
            if type(f) in [int,float]:
                l_rotateSettings.append(f) 

    if not l_rotateSettings or len(l_rotateSettings) < 2:
        #If we don't have data, we're gonna build it
        if minRotate is not None or maxRotate is not None:
            #add a point if we don't have a full loop
            #points = points+1	
            pass

        rotateBaseValue = len(range(int(rotateFloor),int(rotateCeiling)))/points
        #rotateBaseValue = (rotateCeiling - rotateFloor)/points

        log.debug("|{0}| >> floor: {1} | ceiling {2} | baseValue: {3} | points: {4}".format(_str_func,rotateFloor,rotateCeiling,rotateBaseValue,points))     

        #Build our rotate values
        for i in range(points-1):
            l_rotateSettings.append( (rotateBaseValue*(i)) + initialRotate + rotateFloor)
        l_rotateSettings.append(rotateCeiling)
        
    if not l_rotateSettings:raise ValueError, "Should have had some l_rotateSettings by now"
    log.debug("rotateSettings: %s"%l_rotateSettings)

    
    try:#>>> Pew, pew !
        #================================================================
        for i,rotateValue in enumerate(l_rotateSettings):
            guiFactory.doUpdateProgressWindow("Casting {0}".format(rotateValue), i, 
                                              len(l_rotateSettings), 
                                              reportItem=False)	    
            d_castReturn = {}
            hit = False

            #shoot our ray, store the hit
            log.debug("Casting: %i>>%f"%(i,rotateValue))
            mc.setAttr("%s.rotate%s"%(mi_rotObj.mNode,latheAxis.capitalize()),rotateValue)
            log.debug(mc.getAttr("%s.rotate%s"%(mi_rotObj.mNode,latheAxis.capitalize())) )

            #mi_rotObj.__setattr__('rotate%s'%latheAxis.capitalize(),rotateValue)
            try:
                log.debug("mesh: %s"%mesh)
                log.debug("mi_loc.mNode: %s"%mi_loc.mNode)
                log.debug("aimAxis: %s"%aimAxis)
                log.debug("latheAxis: %s"%latheAxis)
                log.debug("maxDistance: %s"%maxDistance)

                d_castReturn = RayCast.findMeshIntersectionFromObjectAxis(mesh, mi_loc.mNode, axis=aimAxis, maxDistance = maxDistance, firstHit=False) or {}
                d_hitReturnFromValue[rotateValue] = d_castReturn	
                if closestInRange:
                    hit = d_castReturn.get('near') or False
                else:
                    hit = d_castReturn.get('far') or False
                if not hit:log.info("{0} -- {1}".format(rotateValue,d_castReturn))

                """if closestInRange:
		    try:
			d_castReturn = RayCast.findMeshIntersectionFromObjectAxis(mesh, mi_loc.mNode, axis=aimAxis, maxDistance = maxDistance) or {}
		    except StandardError,error:
			log.error("createMeshSliceCurve >> closestInRange error : %s"%error)
			return False
		    log.debug("closest in range castReturn: %s"%d_castReturn)		
		    d_hitReturnFromValue[rotateValue] = d_castReturn	
		    log.debug("From %s: %s" %(rotateValue,d_castReturn))

		else:
		    d_castReturn = RayCast.findMeshIntersectionFromObjectAxis(mesh, mi_loc.mNode, axis=aimAxis, maxDistance = maxDistance, singleReturn=False) or {}
		    log.debug("castReturn: %s"%d_castReturn)
		    if d_castReturn.get('hits'):
			closestPoint = distance.returnFurthestPoint(mi_loc.getPosition(),d_castReturn.get('hits')) or False
			d_castReturn['hit'] = closestPoint
			log.debug("From %s: %s" %(rotateValue,d_castReturn))"""

                d_rawHitFromValue[rotateValue] = hit

            except Exception,error:
                for arg in error.args:
                    log.error(arg)
                raise Exception,"createMeshSliceCurve>> error: %s"%error 
            log.debug("rotateValue %s | raw hit: %s"%(rotateValue,hit))
            if hit and not cgmMath.isVectorEquivalent(hit,d_rawHitFromValue.get(l_rotateSettings[i-1])):
                log.debug("last raw: %s"%d_rawHitFromValue.get(l_rotateSettings[i-1]))
                if markHits or offsetMode != 'vector':
                    mi_tmpLoc = cgmMeta.cgmObject(mc.spaceLocator(n='loc_%s'%i)[0])
                    mc.move (hit[0],hit[1],hit[2], mi_tmpLoc.mNode,ws=True)	                    
                if offsetMode =='vector':
                    _baseVector = MATH.get_vector_of_two_points(pos_base,
                                                                hit)
                    _baseDist = DIST.get_distance_between_points(pos_base, 
                                                                 hit)
                    hit = DIST.get_pos_by_vec_dist(pos_base,_baseVector, _baseDist + vectorOffset)
                elif posOffset:
                    constBuffer = mc.normalConstraint(mesh,mi_tmpLoc.mNode,
                                                      aimVector=[0,0,1],
                                                      upVector=[0,1,0],
                                                      worldUpType = 'scene')
                    mc.delete(constBuffer)
                    mc.move(posOffset[0],posOffset[1],posOffset[2], [mi_tmpLoc.mNode], r=True, rpr = True, os = True, wd = True)
                    hit = mi_tmpLoc.getPosition()
                    if not markHits:
                        mi_tmpLoc.delete()

                l_pos.append(hit)
                d_processedHitFromValue[rotateValue] = hit
            else:#Gonna mark our max distance if no hit
                mi_dup = mi_loc.doDuplicate()#dup loc
                mi_dup.doGroup()#zero
                if '-' == aimAxis[1]:
                    mi_dup.__setattr__("t%s"%aimAxis[0],-maxDistance)#mve		
                else:
                    mi_dup.__setattr__("t%s"%aimAxis[0],maxDistance)#mve
                pos = mi_dup.getPosition()
                l_pos.append(pos)#append position
                if markHits:
                    mi_tmpLoc = cgmMeta.cgmObject(mc.spaceLocator(n='loc_%s'%i)[0])
                    mc.move (pos[0],pos[1],pos[2], mi_tmpLoc.mNode,ws=True)		    
                d_processedHitFromValue[rotateValue] = pos	    
                mc.delete(mi_dup.parent)#delete
                log.debug("%s : %s : max marked"%(i,rotateValue))
            if markHits:mc.curve (d=1, ep = l_pos, os=True)#build curves as we go to see what's up
        mc.delete(mi_loc.getParents()[-1])#delete top group
        log.debug("pos list: %s"%l_pos)    
        guiFactory.doCloseProgressWindow()

    except Exception,error:
        raise ValueError,"Cast fail | {0}".format(error) 	
    try:
        if not l_pos:
            log.warning("Cast return: %s"%d_castReturn)
            raise StandardError,"createMeshSliceCurve>> Not hits found. Nothing to do"
        if len(l_pos)>=3:
            if closedCurve:
                #l_pos2 = l_pos + [l_pos[0]]
                l_pos.extend(l_pos[:curveDegree])
                #_cvs.extend(_cvs[:_degree])

                #knot_len = len(l_pos2)+curveDegree-1
                knot_len = len(l_pos)+curveDegree-1		                
                #curveBuffer = mc.curve (d=curveDegree, ep = l_pos, k = [i for i in range(0,knot_len)], os=True)
                curveBuffer = mc.curve (d=curveDegree, periodic = True, p = l_pos, k = [i for i in range(0,knot_len)], os=True)
                for i,ep in enumerate(mc.ls("{0}.ep[*]".format(curveBuffer),flatten=True)):
                    #Second loop to put ep's where we want them. Necessary only because I couldn't get curve create to work right closed
                    POS.set(ep,l_pos[i])

            else:
                #knot_len = len(l_pos)+curveDegree-1		
                #curveBuffer = mc.curve (d=curveDegree, ep = l_pos, k = [i for i in range(0,knot_len)], os=True)
                knot_len = len(l_pos)+curveDegree-1		
                curveBuffer = mc.curve (d=curveDegree, ep = l_pos, k = [i for i in range(0,knot_len)], os=True)   
            if returnDict:
                return {'curve':curveBuffer,
                        'processedHits':d_processedHitFromValue,
                        'hitReturns':d_hitReturnFromValue}
            else:
                return curveBuffer
    except Exception,error:
        for arg in error.args:
            log.error(arg)
        raise Exception,"Post process | {0}".format(error) 
    return False    