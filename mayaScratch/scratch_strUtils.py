from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()
import maya.cmds as mc
from cgm.lib import curves
from cgm.lib import locators
from cgm.lib import distance
from cgm.lib import joints
reload(distance)
from cgm.core.rigger.lib import rig_Utils as rUtils
from cgm.core.cgmPy import str_Utils as strUtils
reload(strUtils)
from cgm.core.rigger.lib import joint_Utils as jUtils
for i_jnt in cgmMeta.validateObjListArg(mc.ls(sl=True),cgmMeta.cgmObject,mayaType = 'joint'):
    jUtils.metaFreezeJointOrientation(i_jnt)
                               
reload(rUtils)
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
objList = mc.ls(sl=True)
cgmMeta.cgmObject(obj).createTransformFromObj()
_str = "5_asdfasdf<><"
_str = "dog -1 * 3"
strUtils.stripInvalidChars(_str)
_str.startswith('0')
#>>> Stretch IK
#=======================================================
reload(crvUtils)
crv = 'uprLid_rigHelper'
crvUtils.returnSplitCurveList(crv,5,markPoints=True,rebuildForSplit=True)