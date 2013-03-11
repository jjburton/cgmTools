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

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.classes import GuiFactory as gui
from cgm.lib import (lists,
                     search,
                     curves,#tmp
                     modules,#tmp
                     distance,#tmp
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
    Control Factory for 
    """
    def __init__(self,obj,targets = [],move = True, orient = False, aim = False, pos = [],
                 snapToSurface = False, snapComponents = False, mode = None,**kws):
        """ 
        Asserts objects existance and that it has a transform. Then initializes. 

        Keyword arguments:
        obj(string/instance)
	targets(list) -- target objects
	
	snapToSurface -- if target is a snappable surface will try to do that
	snapComponents(bool) -- will try to use components if True
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
	assert self.i_obj.isTransform() or self.i_obj.isComponent(),"Not a snappable object. Not a transform: '%s"%self.i_obj.getShortName()      
	#>>> Pass through commands
	self.b_snaptoSurface = snapToSurface
	self.b_snapComponents = snapComponents
	
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
	
	log.info("targetTypes: %s"%self.d_targetTypes)
	if move:
	    log.info("Moving")
	    self.doMove(**kws)
	if orient:
	    log.info("orienting")
	    self.doOrient(**kws)	
	
    #======================================================================
    # Move
    #======================================================================    
    @r9General.Timer    
    def doMove(self,**kws):
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
		    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
			break
		    mc.progressBar(mayaMainProgressBar, edit=True, status = ("Wrapping '%s'"%c), step=1)
		    
		    if targetType in ['mesh','nurbsSurface','nurbsCurve']:
			pos = distance.returnWorldSpacePosition(c)
			targetLoc = mc.spaceLocator()
			mc.move (pos[0],pos[1],pos[2], targetLoc[0])

			closestLoc = locators.locClosest([targetLoc[0]],i_target.mNode)
			position.movePointSnap(c,closestLoc)
			mc.delete([targetLoc[0],closestLoc])
			
		gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
		
	    else:
		pos = False
		if self.b_snaptoSurface:#>>> If our target is surface we can use
		    if targetType in ['mesh','nurbsCurve','nurbsSurface']:
			i_locObj = self.i_obj.doLoc()#Get our position loc
			i_locTarget = cgmMeta.cgmNode( locators.locClosest([i_locObj.mNode],i_target.mNode) )#Loc closest
			pos = i_locTarget.getPosition(True)
			i_locObj.delete()
			i_locTarget.delete()
		else:
		    pos = cgmMeta.cgmNode(i_target.mNode).getPosition(True)	    
		if pos:
		    if self.i_obj.isComponent():
			mc.move (pos[0],pos[1],pos[2], self.i_obj.getComponent(), rpr=True)	    		    
		    else:
			mc.move (pos[0],pos[1],pos[2], self.i_obj.mNode, rpr=True)	    
	else:
	    raise NotImplementedError,"Haven't set up: doMove multi"
	
    def doOrient(self,**kws):
	if len(self.l_targets) == 1:
	    i_target = cgmMeta.cgmNode(self.l_targets[0])
	    if i_target.isComponent():
		if 'poly' in i_target.getMayaType():
		    aimVector = [0,0,1]
		    upVector = [0,1,0]
		    worldUpType = 'scene'
		    constBuffer = mc.normalConstraint(i_target.mNode,self.i_obj.mNode,
		                                      aimVector=aimVector,
		                                      upVector=upVector,
		                                      worldUpType = worldUpType)
		    mc.delete(constBuffer)
		else:
		    raise NotImplementedError,"Haven't set orient for type: %s"%i_target.getMayaType()			    
	    else:
		objRot = mc.xform (i_target.mNode, q=True, ws=True, ro=True)		
		mc.rotate (objRot[0], objRot[1], objRot[2], [self.i_obj.mNode], ws=True)    
	else:
	    raise NotImplementedError,"Haven't set up: doOrient multi"	
	
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
    
    
    """
    targetType = i_target.getMayaType()
    #>>> If our target is surface we can use
    if targetType in ['mesh','nurbsCurve','nurbsSurface','shape']:
	# Type check to get our Components to move
	if objType == 'mesh':
	    componentsToMove = (mc.ls ([i_target.mNode+'.vtx[*]'],flatten=True))
	elif targetType == 'polyVertex':
	    componentsToMove = [i_target.mNode]
	elif targetType in ['polyEdge','polyFace']:
	    mc.select(cl=True)
	    mc.select(i_target.mNode)
	    mel.eval("PolySelectConvert 3")
	    componentsToMove = mc.ls(sl=True,fl=True)
	elif targetType in ['nurbsCurve','nurbsSurface']:
	    componentsToMove = []
	    shapes = mc.listRelatives(i_target.mNode,shapes=True,fullPath=True)
	    if shapes:
		for shape in shapes:
		    componentsToMove.extend(mc.ls ([shape+'.cv[*]'],flatten=True))
	    else:
		componentsToMove = (mc.ls ([i_target.mNode+'.cv[*]'],flatten=True))
	elif targetType == 'shape':
	    componentsToMove = (mc.ls ([i_target.mNode+'.cv[*]'],flatten=True))
	elif targetType == 'surfaceCV':
	    componentsToMove = [i_target.mNode]
	else:
	    componentsToMove = [i_target.mNode]

	#>> Let's move it
	for c in componentsToMove:
	    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
		break
	    mc.progressBar(mayaMainProgressBar, edit=True, status = ("wrapping '%s'"%c), step=1)

	    if sourceType in ['mesh','nurbsSurface','nurbsCurve']:
		pos = distance.returnWorldSpacePosition(c)
		targetLoc = mc.spaceLocator()
		mc.move (pos[0],pos[1],pos[2], targetLoc[0])

		closestLoc = locators.locClosest([targetLoc[0]],sourceObject)
		position.movePointSnap(c,closestLoc)
		mc.delete([targetLoc[0],closestLoc])

	    else:
		guiFactory.warning('The source object must be a poly,nurbs curve or nurbs surface')
    """