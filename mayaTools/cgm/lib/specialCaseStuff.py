#=================================================================================================================================================
#=================================================================================================================================================
#	rigging - a part of rigger
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for the widgety magic of rigging
#
# REQUIRES:
# 	Maya
#   distance
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.joshburton.com
# 	Copyright 2011 Josh Burton - All Rights Reserved.
#
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#
# FUNCTION KEY:
#   1) locMe - creates locators at the pivots of every object selected - matching translation, rotation and rotation order
#   2) locMeObject (obj) - return name of locator created
#   3) setRotationOrderObj (obj, ro)
#   4) doSetLockHideKeyableAttr (obj,lock,visible,keyable,channels) - Pass an oject, True/False for locking it,
#       True/False for visible in channel box, and which channels you want locked in ('tx','ty',etc) form
#   5) groupMe() - Pass selection into it and return locators placed at the pivots of each object - matching translation, rotation and rotation order
#   6) groupMeObject(obj) - Pass object into it and return locators placed at the pivots of each object - matching translation, rotation and rotation order
#
# 3/4/2011 - added point, orient, parent snap functions as well as the list to heirarchy one
#=================================================================================================================================================
import maya.cmds as mc
import maya.mel as mel

from cgm.lib import guiFactory
from cgm.lib import distance
from cgm.lib import attributes
from cgm.lib import autoname



# Maya version check
mayaVersion = int( mel.eval( 'getApplicationVersionAsFloat' ) )

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Special case tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def attachQSSSkinJointsToRigJoints (qssSkinJoints,qssRigJoints):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Created for N project. It will constrain one skeleton to the other
    by looking for the closest joint in a qss set of bind joints

    REQUIRES:
    qssSet(set) - must exist in scene. Set of the rig joints
    rigStartJoint - the first joint of a unifed  deformation skeleton

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    mc.select(cl=True)
    mc.select(qssSkinJoints)
    skinnedHeirarchy = mc.ls(sl=True)
    mc.select(cl=True)
    mc.select(qssRigJoints)
    rigHeirarchy = mc.ls(sl=True)
    constraintsList = []
    for obj in rigHeirarchy:
        print ('On '+obj)
        attachJoint = distance.returnClosestObject(obj,skinnedHeirarchy)
        pntConstBuffer = mc.pointConstraint(obj,attachJoint,maintainOffset=True,weight=1)
        orConstBuffer = mc.orientConstraint(obj,attachJoint,maintainOffset=True,weight=1)
        pntConst = mc.rename(pntConstBuffer,(obj+('_pntConst')))
        orConst = mc.rename(orConstBuffer,(obj+('_orConst')))
        constraintsList.append(pntConst)
        constraintsList.append(orConst)
    #make our attribute Holder object
    """ need to make our master scale connector"""
    dataHolderGrp= ('rigJointsConstraintHolder_grp')
    if mc.objExists (dataHolderGrp):
        pass
    else:
        mc.group (n= dataHolderGrp, w=True, empty=True)
    #stores the constraints
    attributes.storeObjListNameToMessage (constraintsList, dataHolderGrp)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>