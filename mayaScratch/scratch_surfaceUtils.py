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
from cgm.core.lib import surface_Utils as surfUtils
reload(surfUtils)
from cgm.core.rigger.lib import joint_Utils as jUtils

                               
obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
objList = mc.ls(sl=True)
cgmMeta.cgmObject(obj).createTransformFromObj()

#>>> mirror curve curve list
#=======================================================
reload(surfUtils)
surface = 'loftedSurface1'
surface = 'skullPlate'
surface = 'lwrPlate'
obj = 'center_browUpr_jnt'
surfUtils.attachObjToSurface(obj,surface,True)

for jnt in mc.ls(sl=True):
    surfUtils.attachObjToSurface(jnt,surface,True)
    
for jnt in mc.ls(sl=True):
    surfUtils.attachObjToSurface(jnt,surface,False)
#>>> Split curve list
#=======================================================
