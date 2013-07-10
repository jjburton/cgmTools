"""
cgmLimb
Josh Burton (under the supervision of David Bokser:)
www.cgmonks.com
1/12/2011

Key:
1) Class - Limb
    Creates our rig objects
2)  


"""
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

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral
from cgm.core.classes import SnapFactory as Snap

from cgm.lib import (distance,
                     attributes,
                     curves,
                     deformers,
                     lists,
                     rigging,
                     skinning,
                     dictionary,
                     search,
                     nodes,
                     joints,
                     cgmMath)
reload(distance)

#>>> Utilities
#===================================================================
def metaFreezeJointOrientation(targetJoints):
    """
    Copies joint orietnations from one joint to others
    """
    if type(targetJoints) not in [list,tuple]:targetJoints=[targetJoints]

    ml_targetJoints = cgmMeta.validateObjListArg(targetJoints,cgmMeta.cgmObject)
    for i_jnt in ml_targetJoints:
	if i_jnt.getConstraintsTo():
            log.warning("freezeJointOrientation>> target joint has constraints. Can't change orientation. Culling from targets: '%s'"%i_jnt.getShortName())
	    return False
	if i_jnt.getMayaType() != 'joint':
            log.warning("freezeJointOrientation>> target joint is not a joint. Can't change orientation. Culling from targets: '%s'"%i_jnt.getShortName())
	    return False
	
    #buffer parents and children of 
    d_children = {}
    d_parent = {}
    for i_jnt in ml_targetJoints:
        d_children[i_jnt] = cgmMeta.validateObjListArg( mc.listRelatives(i_jnt.mNode, path=True, c=True),cgmMeta.cgmObject,True) or []
	d_parent[i_jnt] = i_jnt.parent
    for i_jnt in ml_targetJoints:
	for i,i_c in enumerate(d_children[i_jnt]):
	    log.info(i_c.getShortName())
	    log.info("freezeJointOrientation>> parented '%s' to world to orient parent"%i_c.mNode)
	    i_c.parent = False
	
    #Orient
    for i,i_jnt in enumerate(ml_targetJoints):
	"""
	So....jointOrient is always in xyz rotate order
	dup,rotate order
	Unparent, add rotate & joint rotate, push value, zero rotate, parent back, done
	"""
	i_jnt.parent = d_parent.get(i_jnt)#parent back first before duping
	buffer = mc.duplicate(i_jnt.mNode,po=True,ic=False)[0]#Duplicate the joint
	i_dup = cgmMeta.cgmObject(buffer)
	i_dup.rotateOrder = 0
        mc.delete(mc.orientConstraint(i_jnt.mNode, i_dup.mNode, w=1, maintainOffset = False))
	
	#i_dup.parent = False
	
	l_rValue = i_dup.rotate
	l_joValue = i_dup.jointOrient
	l_added = cgmMath.list_add(l_rValue,l_joValue)	
	
	i_dup.jointOrientX = l_added[0]
	i_dup.jointOrientY = l_added[1]
	i_dup.jointOrientZ = l_added[2]	
	i_dup.rotate = [0,0,0]
	
	i_dup.parent = i_jnt.parent
	
	i_jnt.rotate = [0,0,0]
	i_jnt.jointOrient = i_dup.jointOrient	
	
        i_dup.delete()
	
    #reparent
    for i_jnt in ml_targetJoints:
        for i_c in d_children[i_jnt]:
            log.info("freezeJointOrientation>> parented '%s' back"%i_c.getShortName())
            i_c.parent = i_jnt.mNode 
	    cgmMeta.cgmAttr(i_c,"inverseScale").doConnectIn("%s.scale"%i_jnt.mNode )
	    
    return True
