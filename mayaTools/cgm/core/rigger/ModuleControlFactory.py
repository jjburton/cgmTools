# From Python =============================================================
import copy
import re

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
from cgm.core import cgm_PuppetMeta as cgmPM
from cgm.core.classes import SnapFactory as Snap
from cgm.core.lib import rayCaster as RayCast
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

from cgm.lib.classes import NameFactory

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
@r9General.Timer
def returnBaseControlSize(i_obj,mesh,axis=True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Figure out the base size for a control from a point in space within a mesh

    ARGUMENTS:
    i_obj(cgmObject instance)
    mesh(obj) = ['option1','option2']
    axis(list) -- what axis to check
    
    RETURNS:
    axisDistances(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    #if type(l_mesh) not in [list,tuple]:l_mesh = [l_mesh]
    if not issubclass(type(i_obj),cgmMeta.cgmObject):
        log.error("Not a cgmObject: '%s'"%i_obj)
        return     
    #Make some locs
    #i_loc = i_obj.doLoc()
    #i_targetLoc = i_obj.doLoc()
    
    #>>>Figure out the axis to do
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
    
    log.info(d_axisToDo)
    if not d_axisToDo:return False
    #>>>
    d_returnDistances = {}
    for axis in d_axisToDo:
        log.info("Checking: %s"%axis)
        directions = d_axisToDo[axis]
        if len(directions) == 1:#gonna multiply our distance 
            info = RayCast.findMeshIntersectionFromObjectAxis(mesh,i_obj.mNode,directions[0])
            d_returnDistances[axis] = (distance.returnDistanceBetweenPoints(info['hit'],i_obj.getPosition()) *2)
        else:
            info1 = RayCast.findMeshIntersectionFromObjectAxis(mesh,i_obj.mNode,directions[0])
            info2 = RayCast.findMeshIntersectionFromObjectAxis(mesh,i_obj.mNode,directions[1])
            if info1 and info2:
                d_returnDistances[axis] = distance.returnDistanceBetweenPoints(info1['hit'],info2['hit'])                    
    log.info(d_returnDistances) 
    return d_returnDistances
    
@r9General.Timer
def limbControlMaker(moduleInstance,controlTypes = ['cog']):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    * Save the new positional information from the template objects
    * Collect all names of objects for a delete list
    * If anything in the module doesn't belong there, un parent it, report it
        * like a template object parented to another obect

    ARGUMENTS:
    moduleNull(string)
    controlTypes(list) = ['option1','option2']
    
    RETURNS:
    limbJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    if type(controlTypes) is not list:controlTypes = [controlTypes]
    if not issubclass(type(moduleInstance),cgmPM.cgmModule):
        log.error("Not a cgmModule: '%s'"%moduleInstance)
        return 
    
    assert moduleInstance.mClass in ['cgmModule','cgmLimb'],"Not a module"
    assert moduleInstance.isTemplated(),"Module is not templated: '%s'"%moduleInstance.getShortName()        
    assert moduleInstance.isSkeletonized(),"Module is not skeletonized: '%s'"%moduleInstance.getShortName()
    
    log.info(">>> ModuleControlFactory.go.__init__")
    i_m = moduleInstance# Link for shortness
    """
    if moduleInstance.hasControls():
        if forceNew:
            deleteControls(moduleInstance)
        else:
            log.warning("'%s' has already been skeletonized"%moduleInstance.getShortName())
            return        
    """
    #>>> Gather info
    #=========================================================
    l_moduleColors = i_m.getModuleColors()
    l_coreNames = i_m.coreNames.value
            
    #>>> part name 
    partName = i_m.getPartNameBase()
    partType = i_m.moduleType or False
    
    direction = None
    if i_m.hasAttr('cgmDirection'):
        direction = i_m.cgmDirection or None
        
    
    #Gether information 
    i_templateNull = i_m.templateNull
    bodyGeo = i_m.modulePuppet.getGeo() or ['Morphy_Body_GEO'] #>>>>>>>>>>>>>>>>>this needs better logic
    l_controlSnapObjects = []
    for i_obj in i_templateNull.controlObjects:
        l_controlSnapObjects.append(i_obj.helper.mNode)  
        
    skinDepth = 2.5
    d_returnControls = {}    
    
    if 'segmentControls' in controlTypes:
            l_segmentControls = []
            l_indexPairs = lists.parseListToPairs(list(range(len(l_controlSnapObjects))))
            l_segments = lists.parseListToPairs(l_controlSnapObjects)
            for i,seg in enumerate(l_segments):
                log.info("segment: %s"%seg)
                log.info("indices: %s"%l_indexPairs[i])
                i_loc = cgmMeta.cgmObject(mc.spaceLocator()[0])#Make a loc            
                #>>> Get a base distance
                distanceToMove = distance.returnDistanceBetweenObjects(seg[0],seg[1])
                log.info("distanceToMove: %s"%distanceToMove)
                l_groupsBuffer = []
                #Need to do more to get a better size
                
                #>>> Build curves
                #=================================================================
                #> Root curve #
                i_root = cgmMeta.cgmObject(curves.createControlCurve('circle',1))
                Snap.go(i_root.mNode,seg[0],move = True, orient = True)#Snap it
                i_root.doGroup()
                i_root.tz = (distanceToMove*.1)#Offset it
                
                #> End Curve
                i_end = cgmMeta.cgmObject(curves.createControlCurve('circle',1))
                Snap.go(i_end.mNode,seg[1],move = True, orient = True)#Snap it
                i_end.doGroup()
                i_end.tz = -(distanceToMove*.1)#Offset it  
                
                #> Figure out a base scale and set it
                if bodyGeo:
                    multiplier = 1.25
                    log.info("Shrinkwrap mode")
                    Snap.go(i_loc.mNode,i_root.parent,move = True, orient = True)#Snap
                    i_loc.parent = i_root.parent#parent
                    """
                    #> First y
                    i_loc.ty = distanceToMove*multiplier#Move
                    d_yPos1 = distance.returnClosestPointOnMeshInfo(i_loc.mNode,bodyGeo[0])#Get Data
                    i_loc.ty = -distanceToMove*multiplier#Move
                    d_yPos2 = distance.returnClosestPointOnMeshInfo(i_loc.mNode,bodyGeo[0])#GetData
                    #> Now x
                    i_loc.ty = 0
                    i_loc.tx = distanceToMove*multiplier#Move                
                    d_xPos1 = distance.returnClosestPointOnMeshInfo(i_loc.mNode,bodyGeo[0])#Get Data
                    i_loc.tx = -distanceToMove*multiplier#Move
                    d_xPos2 = distance.returnClosestPointOnMeshInfo(i_loc.mNode,bodyGeo[0])#GetData
                    #> Now distance
                    f_yScale = distance.returnDistanceBetweenPoints(d_yPos1['position'],d_yPos2['position'])
                    f_xScale = distance.returnDistanceBetweenPoints(d_xPos1['position'],d_xPos2['position'])
                    """
                    d_info = returnBaseControlSize(i_loc,bodyGeo[0],axis = ['x','y'])
                    xScale = d_info['x']
                    yScale = d_info['y']
                    log.info("x: %s"%xScale)
                    log.info("y: %s"%yScale)                
                    #> Now our first pass of scaling
                    i_root.sx = xScale*1.25
                    i_root.sy = yScale*1.25
                    i_root.sz = 1
                    
                    i_end.sx = xScale*1.25
                    i_end.sy = yScale*1.25
                    i_end.sz = 1    
                    #> Now we're gonna strink wrap it
                    for i_crv in [i_root,i_end]:
                        Snap.go(i_crv ,targets = bodyGeo[0],orient = False,snapToSurface=True,snapComponents=True,posOffset=[0,0,skinDepth])                    
                        log.info(i_crv.getShortName())
    
                #> Side Curves
                l_rootPos = []
                l_endPos = []
                l_curvesToCombine = []
                for cv in [0,3,5,7]:
                    l_posBuffer = []
                    #>>> Need to get u positions for more accuracy
                    l_posBuffer.append(cgmMeta.cgmNode('%s.ep[%i]'%(i_root.mNode,cv-1)).getPosition())
                    l_posBuffer.append(cgmMeta.cgmNode('%s.ep[%i]'%(i_end.mNode,cv-1)).getPosition())
                    l_curvesToCombine.append( mc.curve(d=1,p=l_posBuffer,os =True) )#Make the curve
                
                #>>>Store groups
                l_groupsBuffer.append( i_end.parent )
                l_groupsBuffer.append( i_root.parent )
    
                #>>>Combine the curves
                l_curvesToCombine.extend([i_root.mNode,i_end.mNode])            
                newCurve = curves.combineCurves(l_curvesToCombine) 
                i_crv = cgmMeta.cgmObject( rigging.groupMeObject(seg[0],False) )
                curves.parentShapeInPlace(i_crv.mNode,newCurve)#Parent shape
                mc.delete(newCurve)
                
                #>>Copy tags and name
                i_crv.doCopyNameTagsFromObject(seg[0],ignore = ['cgmType'])
                i_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
                i_crv.doName()
                
                #>>> Color
                curves.setCurveColorByName(i_crv.mNode,l_moduleColors[0])                    
                
                #>>>Clean up groups
                for g in l_groupsBuffer:
                    if mc.objExists(g):
                        mc.delete(g)
                
                #Store for return
                l_segmentControls.append( i_crv.mNode )
    
            d_returnControls['segmentControls'] = l_segmentControls 
            
    if 'cog' in controlTypes:
        if 'segmentControls' not in d_returnControls.keys():
            log.warn("Don't have cog creation without segment controls at present")
            return False
        
        i_crv = cgmMeta.cgmObject( curves.createControlCurve('cube',1))
        Snap.go(i_crv, d_returnControls['segmentControls'][0]) #Snap it
        size = distance.returnBoundingBoxSize(d_returnControls['segmentControls'][0],True)#Get size
        log.info(size)
        mc.scale(size[0]*1.1,size[1],size[2]*1.1,i_crv.mNode,relative = True)
        
        #>>Copy tags and name
        i_crv.addAttr('cgmName',attrType='string',value = 'cog')        
        i_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
        i_crv.doName()        

        #>>> Color
        curves.setCurveColorByName(i_crv.mNode,l_moduleColors[0])    
        
        d_returnControls['cog'] = i_crv.mNode
        
    if 'hips' in controlTypes:
        if 'segmentControls' not in d_returnControls.keys():
            log.warn("Don't have hip creation without segment controls at present")
            return False
        
        #>>>Create the curve
        i_crv = cgmMeta.cgmObject( curves.createControlCurve('semiSphere',1,'z-'))
        Snap.go(i_crv, d_returnControls['segmentControls'][0],orient = True) #Snap it
        i_crv.doGroup()
        if len(l_controlSnapObjects)>2:
            distanceToMove = distance.returnDistanceBetweenObjects(l_controlSnapObjects[0],l_controlSnapObjects[1])
            i_crv.tz = -(distanceToMove*.1)#Offset it
        
        #>Clean up group
        g = i_crv.parent
        i_crv.parent = False
        mc.delete(g)
        
        #>Size it
        size = distance.returnBoundingBoxSize(d_returnControls['segmentControls'][0],True)#Get size
        i_obj = cgmMeta.cgmObject(d_returnControls['segmentControls'][0])
        d_size = returnBaseControlSize(i_crv,bodyGeo[0],['z-'])      
        log.info(size)
        mc.scale(size[0],size[2],(size[1]),i_crv.mNode,os = True, relative = True)
        i_crv.sz = d_size['z'] * 1.25
        mc.makeIdentity(i_crv.mNode,apply=True, scale=True)
        
        #>>Copy tags and name
        i_crv.addAttr('cgmName',attrType='string',value = 'hips')        
        i_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
        i_crv.doName()  
        
        #>>> Color
        curves.setCurveColorByName(i_crv.mNode,l_moduleColors[0])        

        d_returnControls['hips'] = i_crv.mNode
        
    """
        
        mc.makeIdentity(cogControl,apply=True, scale=True)
        """
    
    return d_returnControls

def limbControlMakerBAK(moduleNull,controlTypes = ['cog']):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    * Save the new positional information from the template objects
    * Collect all names of objects for a delete list
    * If anything in the module doesn't belong there, un parent it, report it
        * like a template object parented to another obect

    ARGUMENTS:
    moduleNull(string)
    controlTypes(list) = ['option1','option2']
    
    RETURNS:
    limbJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Gather data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ control helper objects - distance sorted"""
    templateRoot =  modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateRoot')
    controlTemplateObjects =  modules.returnInfoNullObjects(moduleNull,'templateControlObjects',types='all')
    controlTemplateObjects = distance.returnDistanceSortedList(templateRoot,controlTemplateObjects)

    """size list of template control objects """
    controlTemplateObjectsSizes = []
    for obj in controlTemplateObjects:
        controlTemplateObjectsSizes.append(distance.returnAbsoluteSizeCurve(obj))
    
    """ pos objects - distance sorted """
    posTemplateObjects =  modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateObject')
    posTemplateObjects = distance.returnDistanceSortedList(templateRoot,posTemplateObjects)

    
    """ orientation objects - distance sorted """
    orientationTemplateObjects = []
    for obj in posTemplateObjects:
        orientationTemplateObjects.append(attributes.returnMessageObject(obj,'orientHelper'))
    
    orientationTemplateObjects = distance.returnDistanceSortedList(templateRoot,orientationTemplateObjects)
    

    returnControls = {}
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Control Maker
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if 'spineIKHandle' in controlTypes:
        """ initial create"""
        ikHandleCurve = curves.createControlCurve('circleArrow2',1)
        mc.setAttr((ikHandleCurve+'.rz'),90)
        mc.setAttr((ikHandleCurve+'.ry'),90)
        mc.makeIdentity(ikHandleCurve, apply = True, r=True)
        startSizeBuffer = controlTemplateObjectsSizes[-1]
        scaleFactor = startSizeBuffer[0] * 1.25
        mc.setAttr((ikHandleCurve+'.sx'),1)
        mc.setAttr((ikHandleCurve+'.sy'),scaleFactor)
        mc.setAttr((ikHandleCurve+'.sz'),scaleFactor)
        position.moveParentSnap(ikHandleCurve,controlTemplateObjects[-1])
        position.movePointSnap(ikHandleCurve,orientationTemplateObjects[-1])
        
        """ make our transform """
        transform = rigging.groupMeObject(controlTemplateObjects[-1],False)
        
        """ connects shape """
        curves.parentShapeInPlace(transform,ikHandleCurve)
        mc.delete(ikHandleCurve)
        
        """ copy over the pivot we want """
        rigging.copyPivot(transform,orientationTemplateObjects[-1])
        
        """ Store data and name"""
        attributes.copyUserAttrs(controlTemplateObjects[-1],transform,attrsToCopy=['cgmName'])
        attributes.storeInfo(transform,'cgmType','controlAnim')
        attributes.storeInfo(transform,'cgmTypeModifier','ik')
        transform = NameFactory.doNameObject(transform)
        returnControls['spineIKHandle'] = transform
    
    if 'ikHandle' in controlTypes:
        """ initial create"""
        ikHandleCurve = curves.createControlCurve('cube',1)
        endSizeBuffer = controlTemplateObjectsSizes[-1]
        mc.setAttr((ikHandleCurve+'.sx'),endSizeBuffer[0])
        mc.setAttr((ikHandleCurve+'.sy'),endSizeBuffer[1])
        mc.setAttr((ikHandleCurve+'.sz'),endSizeBuffer[1])
        position.moveParentSnap(ikHandleCurve,controlTemplateObjects[-1])
        position.movePointSnap(ikHandleCurve,orientationTemplateObjects[-1])
        
        """ make our transform """
        transform = rigging.groupMeObject(controlTemplateObjects[-1],False)
        
        """ connects shape """
        curves.parentShapeInPlace(transform,ikHandleCurve)
        mc.delete(ikHandleCurve)
        
        """ copy over the pivot we want """
        rigging.copyPivot(transform,orientationTemplateObjects[-1])
        
        """ Store data and name"""
        attributes.copyUserAttrs(controlTemplateObjects[-1],transform,attrsToCopy=['cgmName'])
        attributes.storeInfo(transform,'cgmType','controlAnim')
        attributes.storeInfo(transform,'cgmTypeModifier','ik')
        transform = NameFactory.doNameObject(transform)
        returnControls['ikHandle'] = transform
        
    if 'twistFix' in controlTypes:
        """ initial create"""
        twistCurve = curves.createControlCurve('circleArrow1',1,'y+')
        startSizeBuffer = controlTemplateObjectsSizes[0]
        scaleFactor = startSizeBuffer[0] * 1.25
        mc.setAttr((twistCurve+'.sx'),1)
        mc.setAttr((twistCurve+'.sy'),scaleFactor)
        mc.setAttr((twistCurve+'.sz'),scaleFactor)
        position.moveParentSnap(twistCurve,orientationTemplateObjects[0])

        """ make our transform """
        transform = rigging.groupMeObject(controlTemplateObjects[0],False)
        
        """ connects shape """
        curves.parentShapeInPlace(transform,twistCurve)
        mc.delete(twistCurve)
        
        """ copy over the pivot we want """
        rigging.copyPivot(transform,orientationTemplateObjects[0])
        
        """ Store data and name"""
        attributes.copyUserAttrs(controlTemplateObjects[0],transform,attrsToCopy=['cgmName'])
        attributes.storeInfo(transform,'cgmType','controlAnim')
        attributes.storeInfo(transform,'cgmTypeModifier','twist')
        transform = NameFactory.doNameObject(transform)
        returnControls['twistFix'] = transform
     
    if 'vectorHandleSpheres' in controlTypes:
        vectorHandles = []
        for obj in controlTemplateObjects[1:-1]:
            vectorHandleBuffer = []
            currentIndex = controlTemplateObjects.index(obj)
            vectorHandleCurve = curves.createControlCurve('sphere',1)
            sizeBuffer = controlTemplateObjectsSizes[currentIndex]
            scaleFactor = sizeBuffer[0]*.75
            mc.setAttr((vectorHandleCurve+'.sx'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sy'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sz'),scaleFactor)
            position.moveParentSnap(vectorHandleCurve,orientationTemplateObjects[currentIndex])
            
            """ make our transform """
            transform = rigging.groupMeObject(obj,False)
            
            """ connects shape """
            curves.parentShapeInPlace(transform,vectorHandleCurve)
            mc.delete(vectorHandleCurve)
            
            """ copy over the pivot we want """
            rigging.copyPivot(transform,orientationTemplateObjects[currentIndex])
            
            """ Store data and name"""
            attributes.copyUserAttrs(obj,transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','ik')
            vectorHandleBuffer = NameFactory.doNameObject(transform)
            vectorHandles.append(vectorHandleBuffer)
            
            
        returnControls['vectorHandleSpheres'] = vectorHandles
        
    if 'vectorHandles' in controlTypes:
        vectorHandles = []
        for obj in controlTemplateObjects[1:-1]:
            vectorHandleBuffer = []
            currentIndex = controlTemplateObjects.index(obj)
            vectorHandleCurve = curves.createControlCurve('circleArrow',1)
            mc.setAttr((vectorHandleCurve+'.rx'),90)
            mc.makeIdentity(vectorHandleCurve, apply = True, r=True)
            sizeBuffer = controlTemplateObjectsSizes[currentIndex]
            scaleFactor = sizeBuffer[0]*1.5
            mc.setAttr((vectorHandleCurve+'.sx'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sy'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sz'),scaleFactor)
            position.moveParentSnap(vectorHandleCurve,controlTemplateObjects[currentIndex])
            position.movePointSnap(vectorHandleCurve,orientationTemplateObjects[currentIndex])
            
            """ make our transform """
            transform = rigging.groupMeObject(obj,False)
            
            """ connects shape """
            curves.parentShapeInPlace(transform,vectorHandleCurve)
            mc.delete(vectorHandleCurve)
            
            """ copy over the pivot we want """
            rigging.copyPivot(transform,orientationTemplateObjects[currentIndex])
            
            """ Store data and name"""
            attributes.copyUserAttrs(obj,transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','ik')
            vectorHandleBuffer = NameFactory.doNameObject(transform)
            vectorHandles.append(vectorHandleBuffer)
            
            
        returnControls['vectorHandles'] = vectorHandles
        
    if 'hips' in controlTypes:
        hipsCurve = curves.createControlCurve('semiSphere',1)
        mc.setAttr((hipsCurve+'.rx'),90)
        mc.makeIdentity(hipsCurve,apply=True,translate =True, rotate = True, scale=True)
        rootSizeBuffer = controlTemplateObjectsSizes[0]
        mc.setAttr((hipsCurve+'.sx'),rootSizeBuffer[0])
        mc.setAttr((hipsCurve+'.sy'),rootSizeBuffer[1])
        mc.setAttr((hipsCurve+'.sz'),rootSizeBuffer[0])
        position.moveParentSnap(hipsCurve,controlTemplateObjects[0])
        
        """ make our transform """
        transform = rigging.groupMeObject(controlTemplateObjects[0],False)
        
        """ connects shape """
        curves.parentShapeInPlace(transform,hipsCurve)
        mc.delete(hipsCurve)
        
        """ Store data and name"""
        attributes.storeInfo(transform,'cgmName','hips')
        attributes.storeInfo(transform,'cgmType','controlAnim')
        hips = NameFactory.doNameObject(transform)
        returnControls['hips'] = hips
            
    if 'cog' in controlTypes:
        cogControl = curves.createControlCurve('cube',1)
        rootSizeBuffer = controlTemplateObjectsSizes[0]
        mc.setAttr((cogControl+'.sx'),rootSizeBuffer[0]*1.05)
        mc.setAttr((cogControl+'.sy'),rootSizeBuffer[1]*1.05)
        mc.setAttr((cogControl+'.sz'),rootSizeBuffer[0]*.25)
        position.moveParentSnap(cogControl,controlTemplateObjects[0])
        
        mc.makeIdentity(cogControl,apply=True, scale=True)
        
        """ Store data and name"""
        attributes.storeInfo(cogControl,'cgmName','cog')
        attributes.storeInfo(cogControl,'cgmType','controlAnim')
        cogControl = NameFactory.doNameObject(cogControl)
        returnControls['cog'] = cogControl
    

    if 'limbControls' in controlTypes:
        limbControls = []
        controlSegments = lists.parseListToPairs(controlTemplateObjects)
        orientationSegments = lists.parseListToPairs(orientationTemplateObjects)
        cnt = 0
        for segment in controlSegments:
            """ get our orientation segment buffer """
            orientationSegment = orientationSegments[cnt]
            """move distance """
            distanceToMove = distance.returnDistanceBetweenObjects(orientationSegment[0],orientationSegment[1])

            """ root curve """
            rootCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[0])
            mc.setAttr((rootCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((rootCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((rootCurve+'.sz'),1)
            position.moveParentSnap(rootCurve,segment[0])
            #mc.move(0, 0, (distanceToMove * .15), rootCurve, r=True,os=True,wd=True)
            
            """ end curve """
            endCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[1])
            mc.setAttr((endCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((endCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((endCurve+'.sz'),1)
            position.moveParentSnap(endCurve,segment[1])
            position.movePointSnap(endCurve,orientationSegment[1])
            mc.move(0, 0, -(distanceToMove * .15), endCurve, r=True,os=True,wd=True)
            
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #>>> Side curves
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            """ locators on curve"""
            side1Locs = []
            side2Locs = []
            frontLocs = []
            backLocs = []
            side1Locs.append(locators.locMeCvFromCvIndex(rootCurve,3))
            side1Locs.append(locators.locMeCvFromCvIndex(endCurve,3))
            side2Locs.append(locators.locMeCvFromCvIndex(rootCurve,7))
            side2Locs.append(locators.locMeCvFromCvIndex(endCurve,7))
            frontLocs.append(locators.locMeCvFromCvIndex(rootCurve,5))
            frontLocs.append(locators.locMeCvFromCvIndex(endCurve,5))
            backLocs.append(locators.locMeCvFromCvIndex(rootCurve,0))
            backLocs.append(locators.locMeCvFromCvIndex(endCurve,0))
            
            """ get u positions for new curves"""
            side1PosSet = []
            side2PosSet = []
            frontPosSet = []
            backPosSet = []
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[0],rootCurve))
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[1],endCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[0],rootCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[1],endCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[0],rootCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[1],endCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[0],rootCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[1],endCurve))

            """ make side curves"""
            sideCrv1 = mc.curve (d=1, p = side1PosSet , os=True)
            sideCrv2 = mc.curve (d=1, p = side2PosSet , os=True)
            frontCrv = mc.curve (d=1, p = frontPosSet , os=True)
            backCrv = mc.curve (d=1, p = backPosSet , os=True)
            
            """ combine curves """
            mc.makeIdentity(rootCurve,apply=True,translate =True, rotate = True, scale=True)
            mc.makeIdentity(endCurve,apply=True,translate =True, rotate = True, scale=True)
            segmentCurveBuffer = curves.combineCurves([sideCrv1,sideCrv2,frontCrv,backCrv,rootCurve,endCurve])
            
            """ delete locs """
            for loc in side1Locs,side2Locs,frontLocs,backLocs:
                mc.delete(loc)
                
            """ make our transform """
            transform = rigging.groupMeObject(segment[0],False)
            
            """ connects shape """
            curves.parentShapeInPlace(transform,segmentCurveBuffer)
            mc.delete(segmentCurveBuffer)
            
            """ copy over the pivot we want """
            rigging.copyPivot(transform,orientationSegment[0])

                
            """ Store data and name"""
            attributes.copyUserAttrs(segment[0],transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','fk')
            limbControlBuffer = NameFactory.doNameObject(transform)
            limbControls.append(limbControlBuffer)
            
            cnt+=1
        returnControls['limbControls'] = limbControls
        
    if 'headControls' in controlTypes:
        headControls = []
        controlSegments = lists.parseListToPairs(controlTemplateObjects)
        orientationSegments = lists.parseListToPairs(orientationTemplateObjects)
        """ figure out our second to last segment to do something a bit different """
        secondToLastCheck = (len(controlSegments)-2)
        print secondToLastCheck  
        cnt = 0
        for segment in controlSegments:
            """ get our orientation segment buffer """
            orientationSegment = orientationSegments[cnt]            
            """move distance """
            distanceToMove = distance.returnDistanceBetweenObjects(segment[0],segment[1])

            """ root curve """
            rootCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[0])
            mc.setAttr((rootCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((rootCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((rootCurve+'.sz'),1)
            position.moveParentSnap(rootCurve,segment[0])
            mc.move(0, 0, (distanceToMove * .05), rootCurve, r=True,os=True,wd=True)
            
            """ end curve """
            endCurve = curves.createControlCurve('circle',1)
            if cnt != secondToLastCheck:
                rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[1])
            else:
                rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[0])
            mc.setAttr((endCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((endCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((endCurve+'.sz'),1)
            position.moveParentSnap(endCurve,segment[1])
            mc.move(0, 0, -(distanceToMove * .05), endCurve, r=True,os=True,wd=True)
            
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #>>> Side curves
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            """ locators on curve"""
            side1Locs = []
            side2Locs = []
            frontLocs = []
            backLocs = []
            side1Locs.append(locators.locMeCvFromCvIndex(rootCurve,3))
            side1Locs.append(locators.locMeCvFromCvIndex(endCurve,3))
            side2Locs.append(locators.locMeCvFromCvIndex(rootCurve,7))
            side2Locs.append(locators.locMeCvFromCvIndex(endCurve,7))
            frontLocs.append(locators.locMeCvFromCvIndex(rootCurve,5))
            frontLocs.append(locators.locMeCvFromCvIndex(endCurve,5))
            backLocs.append(locators.locMeCvFromCvIndex(rootCurve,0))
            backLocs.append(locators.locMeCvFromCvIndex(endCurve,0))
            
            """ get u positions for new curves"""
            side1PosSet = []
            side2PosSet = []
            frontPosSet = []
            backPosSet = []
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[0],rootCurve))
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[1],endCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[0],rootCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[1],endCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[0],rootCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[1],endCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[0],rootCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[1],endCurve))

            """ make side curves"""
            sideCrv1 = mc.curve (d=1, p = side1PosSet , os=True)
            sideCrv2 = mc.curve (d=1, p = side2PosSet , os=True)
            frontCrv = mc.curve (d=1, p = frontPosSet , os=True)
            backCrv = mc.curve (d=1, p = backPosSet , os=True)
            
            """ combine curves """
            mc.makeIdentity(rootCurve,apply=True,translate =True, rotate = True, scale=True)
            mc.makeIdentity(endCurve,apply=True,translate =True, rotate = True, scale=True)
            segmentCurveBuffer = curves.combineCurves([sideCrv1,sideCrv2,frontCrv,backCrv,rootCurve,endCurve])
            
            """ delete locs """
            for loc in side1Locs,side2Locs,frontLocs,backLocs:
                mc.delete(loc)
                
            """ make our transform """
            transform = rigging.groupMeObject(segment[0],False)
            
            """ connects shape """
            curves.parentShapeInPlace(transform,segmentCurveBuffer)
            mc.delete(segmentCurveBuffer)
            
            """ copy over the pivot we want """
            rigging.copyPivot(transform,orientationSegment[0])
              
            """ Store data and name"""
            attributes.copyUserAttrs(segment[0],transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','fk')
            segmentCurveBuffer = NameFactory.doNameObject(transform)
            headControls.append(segmentCurveBuffer)
            
            cnt+=1
        returnControls['headControls'] = headControls


    
    return returnControls
