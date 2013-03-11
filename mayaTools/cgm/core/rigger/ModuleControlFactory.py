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

from cgm.lib import (cgmMath,
                     locators,
                     modules,
                     distance,
                     rigging,
                     search,
                     curves,
                     lists,
                     )

from cgm.lib.classes import NameFactory

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    @r9General.Timer
    def __init__(self,moduleInstance,forceNew = True,**kws): 
        """
        To do:
        Add rotation order settting
        Add module parent check to make sure parent is templated to be able to move forward, or to constrain
        Add any other piece meal data necessary
        Add a cleaner to force a rebuild
        """
        # Get our base info
        #==============	        
        #>>> module null data
        if not issubclass(type(moduleInstance),cgmPM.cgmModule):
            log.error("Not a cgmModule: '%s'"%moduleInstance)
            return 
        
        assert moduleInstance.mClass in ['cgmModule','cgmLimb'],"Not a module"
        assert moduleInstance.isTemplated(),"Module is not templated: '%s'"%moduleInstance.getShortName()        
        assert moduleInstance.isSkeletonized(),"Module is not skeletonized: '%s'"%moduleInstance.getShortName()
        
        log.info(">>> ModuleControlFactory.go.__init__")
        self.m = moduleInstance# Link for shortness
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
        self.l_moduleColors = self.m.getModuleColors()
        self.l_coreNames = self.m.coreNames.value
                
        #>>> part name 
        self.partName = self.m.getPartNameBase()
        self.partType = self.m.moduleType or False
        
        self.direction = None
        if self.m.hasAttr('cgmDirection'):
            self.direction = self.m.cgmDirection or None
               
        #>>> Instances and joint stuff
        self.jointOrientation = modules.returnSettingsData('jointOrientation')
        #self.i_root = self.i_templateNull.root
        #self.i_orientRootHelper = self.i_templateNull.orientRootHelper
        #self.i_curve = self.i_templateNull.curve
        #self.i_controlObjects = self.i_templateNull.controlObjects
        
        
        #>>> We need to figure out which control to make
        self.l_controlsToMakeArg = ['cog']            
        if self.m.rigNull.ik:
            self.l_controlsToMakeArg.extend(['vectorHandles'])
            if self.partType == 'torso':#Maybe move to a dict?
                self.l_controlsToMakeArg.append('spineIKHandle')            
        if self.m.rigNull.fk:
            self.l_controlsToMakeArg.extend(['segmentControls'])
            if self.partType == 'torso':#Maybe move to a dict?
                self.l_controlsToMakeArg.append('hips')
        log.info("l_controlsToMakeArg: %s"%self.l_controlsToMakeArg)
        
        """
        fk = templateNullData.get('fk')
        ik = templateNullData.get('ik')
        stretch = templateNullData.get('stretch')
        bend = templateNullData.get('bend')
        
        controlsToMake =[]
        controlsToMake.append('cog')
        
        if fk == True:
            controlsToMake.append('segmentControls')
            controlsToMake.append('hips')
            
        if ik == True:
            controlsToMake.append('vectorHandles')
            controlsToMake.append('spineIKHandle')  
            
        controlsDict = modules.limbControlMaker(moduleNull,controlsToMake)
        
        print controlsDict
        #>>> Organize em
        segmentControls = controlsDict.get('segmentControls')
        spineIKHandle = controlsDict.get('spineIKHandle')
        cog = controlsDict.get('cog')
        hips = controlsDict.get('hips')
        vectorHandles = controlsDict.get('vectorHandles')
        for handle in vectorHandles[-1:]:
            mc.delete(handle)
            vectorHandles.remove(handle)        
        """
        
        #Make our stuff
        if issubclass(type(self.m), cgmPM.cgmLimb):
            log.info("mode: cgmLimb control building")
            if not limbControlMaker(self,self.l_controlsToMakeArg):
                raise StandardError,"limbControlMaker failed!"
        else:
            raise NotImplementedError,"haven't implemented '%s' templatizing yet"%self.m.mClass
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@r9General.Timer
def limbControlMaker(goInstance,controlTypes = ['cog']):
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
    if not issubclass(type(goInstance),go):
        log.error("Not a ModuleControlFactory.go instance: '%s'"%goInstance.getShortName())
        return False        
    self = goInstance
    i_templateNull = self.m.templateNull
    bodyGeo = self.m.modulePuppet.getGeo() or ['Morphy_Body_GEO'] #>>>>>>>>>>>>>>>>>this needs better logic
    returnControls = {}
    
    if 'segmentControls' in controlTypes:
        l_segmentControls = []
        l_controlObjects = []
        for i_obj in i_templateNull.controlObjects:
            l_controlObjects.append(i_obj.helper.mNode)
        l_indexPairs = lists.parseListToPairs(list(range(len(l_controlObjects))))
        l_segments = lists.parseListToPairs(l_controlObjects)
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
                
                log.info("f_xScale: %s"%f_xScale)
                log.info("f_yScale: %s"%f_yScale)                
                #> Now our first pass of scaling
                i_root.sx = f_xScale*1.25
                i_root.sy = f_yScale*1.25
                i_root.sz = 1
                
                i_end.sx = f_xScale*1.25
                i_end.sy = f_yScale*1.25
                i_end.sz = 1    
                #> Now we're gonna strink wrap it
                for i_crv in [i_root,i_end]:
                    Snap.go(i_crv ,targets = bodyGeo[0],orient = False,snapToSurface=True,snapComponents=True)                    
                    log.info(i_crv.getShortName())
                    i_crv.sx *= 1.3
                    i_crv.sy *= 1.3
                    
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
            i_crv.addAttr('cgmTypeModifier',attrType='string',value = 'fk')            
            i_crv.doName()
            
            #>>>Clean up groups
            for g in l_groupsBuffer:
                if mc.objExists(g):
                    mc.delete(g)
            
            #Store for return
            l_segmentControls.append( i_crv.mNode )

        returnControls['segmentControls'] = l_segmentControls
    return returnControls

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
    
    if 'segmentControls' in controlTypes:
        segmentControls = []
        segments = lists.parseListToPairs(controlTemplateObjects)
        orientationSegments = lists.parseListToPairs(orientationTemplateObjects)
        cnt = 0
        for segment in segments:
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
            mc.move(0, 0, (distanceToMove * .1), rootCurve, r=True,os=True,wd=True)
            
            """ end curve """
            endCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[1])
            mc.setAttr((endCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((endCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((endCurve+'.sz'),1)
            position.moveParentSnap(endCurve,segment[1])
            mc.move(0, 0, -(distanceToMove * .1), endCurve, r=True,os=True,wd=True)
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
            segmentControls.append(segmentCurveBuffer)
            
            cnt+=1
        returnControls['segmentControls'] = segmentControls
        
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
