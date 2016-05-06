import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()

reload(cgmMeta)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
orientation = ['xyz']
orientation[1]

#>>>cgmControl
obj = 'hips_controlCurve'
i_c = cgmMeta.asMeta(obj,'cgmControl',setClass=True)

from cgm.core.rigger.lib import joint_Utils as jntUtils
reload(jntUtils)

for jnt in mc.ls(sl=True):
    new = mc.mirrorJoint(jnt,mirrorBehavior = True, mirrorYZ = True, searchReplace = ['l_','r_'])
    jntUtils.mirrorJointOrientation(new,'zyx')
    
jntUtils.mirrorJointOrientation(mc.ls(sl=True),'zyx')

for jnt in mc.ls(sl=True):jntUtils.metaFreezeJointOrientation(jnt)

from cgm.lib import joints
reload(joints)
#>>> Copy joint orientation 
#=======================================================
source = mc.ls(sl=True)[0]
targets = mc.ls(sl=True)[1:]
joints.doCopyJointOrient(source,targets)

from cgm.lib import search
reload(search)
joints.createCurveFromJoints(mc.ls(sl=True)[0])

#
jnt = cgmMeta.cgmObject(mc.ls(sl=True)[0])
l_rValue = jnt.rotate
l_joValue = jnt.jointOrient
from cgm.lib import cgmMath
l_inverse = [-v for v in l_rValue]
l_added = cgmMath.list_add(l_rValue,l_joValue)	
l_added = cgmMath.list_add(l_inverse,l_joValue)	

jnt.jointOrientX = l_added[0]
jnt.jointOrientY = l_added[1]
jnt.jointOrientZ = l_added[2]	
jnt.rotate = [0,0,0]

jnt.jointOrientX = (l_rValue[0] + l_joValue[0])/2
jnt.jointOrientY = (l_rValue[1] + l_joValue[1])/2
jnt.jointOrientZ = (l_rValue[2] + l_joValue[2])/2	
jnt.rotate = [0,0,0]