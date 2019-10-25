"""
------------------------------------------
SnapFactory: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Class Factory for the positioning of objects in space
================================================================
"""
# From Python =============================================================
import copy
import re

#TEMP
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General
from Red9.core import Red9_AnimationUtils as r9Anim
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import rayCaster as RayCast

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.classes import GuiFactory as gui
from cgm.lib import (lists,
                     search,
                     curves,#tmp
                     modules,#tmp
                     distance,#tmp
                     dictionary,
                     controlBuilder,
                     attributes,
                     locators,
                     dictionary,
                     position,
                     rigging,
                     settings,
                     guiFactory)

#>>>>>>>>>>>>>>>>>>>>>>>      
class go(object):
    """ 
    Control Factory for snapping objects around in maya
    """
    def __init__(self,obj,targets = [],move = True, orient = False, aim = False, pos = [],
                 snapToSurface = False, midSurfacePos = False,
                 posOffset = False,
                 aimVector = [0,0,1],upVector = [0,1,0], worldUpType = 'scene',
                 snapComponents = False,softSelection = False, softSelectDistance = 20,                 
                 mode = None,**kws):
        """ 
        Asserts objects existance and that it has a transform. Then initializes. 

        Keyword arguments:
        obj(string/instance)
        targets(list) -- target objects

        snapToSurface -- if target is a snappable surface will try to do that
        posOffset
        snapComponents(bool) -- will try to use components if True
        aimVector(vector) -- aim vector for object
        upVector(vector) -- up vector for object (used as lathe axis for midpoint surface snap too)
        midSurfacePos(bool) -- mid point snap with a surface
        worldUpType(string) -- arg for various modes (aim, orient, etc)
        softSelection(bool) -- soft select mode for component objects only
        softSelectDistance(float) -- arg for mc.softSelect

        ToDo:
        1) midSurfacePos
        """
        #>>> Check our obj
        log.debug("obj: %s"%obj)
        log.debug("targets: %s"%targets)
        if issubclass(type(obj),cgmMeta.cgmNode):
            self.i_obj = obj
        else:
            i_node = cgmMeta.cgmNode(obj)
            if i_node.isComponent():
                self.i_obj = i_node		
            else :
                self.i_obj = cgmMeta.cgmObject(obj)
        assert VALID.is_transform(self.i_obj.mNode) or self.i_obj.isComponent(),"Not a snappable object. Not a transform: '%s"%self.i_obj.getShortName()      

        #>>> Pass through args
        self.b_snaptoSurface = snapToSurface
        self.b_midSurfacePos = midSurfacePos	
        self.b_snapComponents = snapComponents
        self.b_softSelection = softSelection
        self.b_midSurfacePos = midSurfacePos
        self.b_aim = aim		
        self._softSelectionDistance = softSelectDistance,
        self._posOffset = posOffset
        self._aimVector = aimVector
        self._upVector = upVector
        self._worldUpType = worldUpType

        #>>> Check our targets
        if targets and not type(targets)==list:targets=[targets]
        self.l_targets = []	
        self.d_targetTypes = {}
        self.d_targetPositions = {}
        for t in targets:
            self.registerTarget(t)

        if not self.l_targets:
            log.error("No existing targets found")
            return

        if self.b_softSelection:
            #Should we save soft select info before changing?
            mc.softSelect(softSelectDistance = softSelectDistance)
            mc.softSelect(softSelectFalloff = 0)	    
        log.debug("targetTypes: %s"%self.d_targetTypes)
        if move:
            log.debug("Moving")
            self.doMove(**kws)
        if orient:
            log.debug("orienting")
            self.doOrient(**kws)
        if aim:
            log.debug("orienting")
            self.doAim(**kws)	    

    #======================================================================
    # Move
    #======================================================================    
    def doMove(self,**kws):
        if kws:log.debug("Snap.doMove>>> kws: %s"%kws)
        if len(self.l_targets) == 1:
            #>>> Check our target	    
            i_target = cgmMeta.cgmNode( self.l_targets[0] )
            log.debug("i_target: %s"%i_target)
            targetType = i_target.getMayaType()	    

            if self.b_snapComponents:
                components = self.i_obj.getComponents()
                if not components:raise StandardError,"This objects has no components to snap: '%s'"%self.i_obj.getShortName()
                #>>>Progress bar
                mayaMainProgressBar = gui.doStartMayaProgressBar(len(components))		

                for c in components:
                    if mayaMainProgressBar:
                        if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                            break
                        mc.progressBar(mayaMainProgressBar, edit=True, status = ("Wrapping '%s'"%c), step=1)

                    if targetType in ['mesh','nurbsSurface','nurbsCurve']:
                        pos = distance.returnWorldSpacePosition(c)
                        targetLoc = mc.spaceLocator()
                        mc.move (pos[0],pos[1],pos[2], targetLoc[0])

                        closestLoc = locators.locClosest([targetLoc[0]],i_target.mNode)
                        if self._posOffset:
                            self.doOrientObjToSurface(i_target.mNode,closestLoc)
                            mc.move (self._posOffset[0],self._posOffset[1],self._posOffset[2], [closestLoc], r=True, rpr = True, os = True, wd = True)								
                        position.movePointSnap(c,closestLoc)
                        mc.delete([targetLoc[0],closestLoc])

                if mayaMainProgressBar:gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    

            else:
                pos = False
                if self.b_snaptoSurface:#>>> If our target is surface we can use
                    if targetType in ['mesh','nurbsCurve','nurbsSurface']:
                        i_locObj = self.i_obj.doLoc()#Get our position loc
                        i_locTarget = cgmMeta.cgmObject( locators.locClosest([i_locObj.mNode],i_target.mNode) )#Loc closest
                        #i_locObj.rename('objLoc')
                        #i_locTarget.rename('targetLoc')
                        if self._posOffset:
                            try:
                                self.doOrientObjToSurface(i_target.mNode,i_locTarget.mNode)
                                mc.move (self._posOffset[0],self._posOffset[1],self._posOffset[2], [i_locTarget.mNode], r=True, rpr = True, os = True, wd = True)								
                            except StandardError,error:
                                log.warn("self._posOffset failure!")
                                log.error(error)

                        pos = i_locTarget.getPosition(True)
                        i_locObj.delete()
                        i_locTarget.delete()
                elif self.b_midSurfacePos:
                    log.debug("Snap.move>>> midSurfacePos mode!")
                    if targetType not in ['mesh','nurbsCurve','nurbsSurface']:
                        log.warning("Can't do midSurfacPos on targetType: '%s'"%targetType)
                        return False
                    #Get the axis info
                    axisToCheck = kws.pop('axisToCheck',False)
                    if not axisToCheck:
                        axisToCheck = []		    
                        up = dictionary.returnVectorToString(self._upVector) or False
                        if not up:
                            raise StandardError,"SnapFactory>>> must have up vector for midSurfaceSnap: %s"%self._upVector
                        for a in ['x','y','z']:
                            if a != up[0]:
                                axisToCheck.append(a)
                        if not axisToCheck:
                            raise StandardError,"SnapFactory>>> couldn't find any axis to do"
                    #i_locObj = self.i_obj.doLoc()#Get our position loc		
                    #log.debug(axisToCheck)
                    pos = RayCast.findMeshMidPointFromObject(i_target.mNode, self.i_obj.mNode, axisToCheck=axisToCheck,**kws)
                    #i_locObj.delete()

                else:
                    pos = i_target.getPosition(True)	    
                if pos:
                    if self.i_obj.isComponent():
                        if self.b_softSelection:#Only need to do this if soft select is on
                            mc.softSelect(softSelectEnabled = True)
                            mc.select(self.i_obj.getComponent())
                            mc.move (pos[0],pos[1],pos[2],rpr=True)
                            mc.select(cl=True)
                        else:
                            mc.move (pos[0],pos[1],pos[2], self.i_obj.getComponent())	    		    
                    else:
                        mc.move (pos[0],pos[1],pos[2], self.i_obj.mNode, rpr=True)	    
        else:
            raise NotImplementedError,"Haven't set up: doMove multi"

    def doOrient(self,**kws):
        if len(self.l_targets) == 1:
            i_target = cgmMeta.cgmNode(self.l_targets[0])
            #if self.i_obj.rotateOrder != i_target.rotateOrder:
                #raise StandardError, "Can't match different rotate orders yet"
            if i_target.isComponent():
                if 'poly' in i_target.getMayaType():
                    self.doOrientObjToSurface(i_target.mNode,self.i_obj.mNode)
                else:
                    raise NotImplementedError,"Haven't set orient for type: %s"%i_target.getMayaType()			   
            elif i_target.getMayaType() == 'mesh':
                self.doOrientObjToSurface(i_target.mNode,self.i_obj.mNode)		

            else:
                mc.delete(mc.orientConstraint(i_target.mNode,self.i_obj.mNode,mo=False))
                #objRot = mc.xform (i_target.mNode, q=True, ws=True, ro=True)		
                #mc.rotate (objRot[0], objRot[1], objRot[2], [self.i_obj.mNode], ws=True)    
        else:
            raise NotImplementedError,"Haven't set up: doOrient multi"	

    def doOrientObjToSurface(self,l_targets,obj,deleteConstraint = True):
        """
        constraint
        """
        if type(l_targets) is not list:l_targets = [l_targets]
        try:
            constBuffer = mc.normalConstraint(l_targets,obj,
                                              aimVector=self._aimVector,
                                              upVector=self._upVector,
                                              worldUpType = self._worldUpType)
            if deleteConstraint:
                mc.delete(constBuffer)
                return True
            return constBuffer

        except StandardError,error:
            log.error(error)	
            return False

    def doAim(self):
        """
        constraint
        """
        if not self.l_targets:
            raise StandardError, "doAim>> must have targets"
        try:
            constBuffer = mc.aimConstraint(self.l_targets,self.i_obj.mNode,
                                           maintainOffset = False, weight = 1,
                                           aimVector=self._aimVector,
                                           upVector=self._upVector,
                                           worldUpType = self._worldUpType)

            mc.delete(constBuffer)
            return True

        except StandardError,error:
            log.error(error)	
            return False

    def registerTarget(self,target):
        """
        if issubclass(type(target),r9Meta.MetaClass):
            i_obj = target
        else:
            i_obj = cgmMeta.cgmObject(target)
            """
        if not mc.objExists(target):
            log.warning("One of the targets doesn't exist: '%s'"%target)
            return False

        if target not in self.l_targets:self.l_targets.append(target)
        self.d_targetTypes[target] = search.returnObjectType(target)
        return True

