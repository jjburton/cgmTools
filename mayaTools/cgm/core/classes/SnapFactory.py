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
from cgm.lib import (lists,
                     search,
                     curves,#tmp
                     modules,#tmp
                     distance,#tmp
                     controlBuilder,
                     attributes,
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
    def __init__(self,obj,targets = [],move = True, orient = False, aim = False, pos = [], mode = None,**kws):
        """ 
        Asserts objects existance and that it has a transform. Then initializes. 

        Keyword arguments:
        obj(string/instance)
	targets(list) -- target objects
        """
	#>>> Check our obj	
	if issubclass(type(obj),r9Meta.MetaClass):
	    self.i_obj = obj
	else:
	    self.i_obj = cgmMeta.cgmObject(obj)
	assert self.i_obj.isTransform(),"Not a snappable object. Not a transform: '%s"%self.i_obj.getShortName()      
	
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
	    pos = cgmMeta.cgmNode(self.l_targets[0]).getPosition(True)
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