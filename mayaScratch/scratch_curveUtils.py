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
from cgm.core.lib import curve_Utils as crvUtils
reload(crvUtils)
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

#>>> midpoint
#=======================================================
reload(crvUtils)
baseCrv = 'curve18'
obj = 'l_brow_direct_0_anim_master_grp_control_loc1'
crv = 'l_brow_driver_crv'
crvUtils.attachObjToCurve(obj,crv)

#>>> midpoint
#=======================================================
reload(crvUtils)
baseCrv = 'curve18'
crvUtils.getMidPoint(mc.ls(sl=True))

crvUtils.convertCurve(mc.ls(sl=True)[0])

#>>> mirror curve curve list
#=======================================================
reload(crvUtils)
baseCrv = 'curve18'
crvUtils.mirrorCurve(baseCrv)
crvUtils.mirrorCurve(baseCrv,mirrorAcross='y')
crvUtils.mirrorCurve(mc.ls(sl=True)[0])
crvUtils.mirrorCurve(mc.ls(sl=True)[0],mc.ls(sl=True)[1],mirrorAcross='x')

#>>> Split curve list
#=======================================================
reload(crvUtils)
crv = 'upper_l_lip_crv_mirrored4'
crv = 'noseBaseCast_1_rigHelper'
crvUtils.returnSplitCurveList(crv,5,minU = .3, markPoints=True,rebuildForSplit=True)

crvUtils.returnSplitCurveList(crv,1,markPoints=True,rebuildForSplit=True)
crvUtils.returnSplitCurveList(crv,5,markPoints=True,rebuildForSplit=True,insetSplitFactor=.01)
crvUtils.returnSplitCurveList(crv,8,markPoints=True,rebuildForSplit=True,startSplitFactor=.3)

#>>> percentPointOnCurve
reload(crvUtils)
crv = 'smileLeft_2_rigHelper'
crvUtils.getPercentPointOnCurve(crv,.5)