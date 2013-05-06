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
i_c = cgmMeta.cgmControl(obj,setClass=True)


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