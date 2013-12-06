from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()
import maya.cmds as mc
from cgm.lib import cgmMath
reload(cgmMath)


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
#>>> Split value list
#=======================================================
reload(cgmMath)
minU = .1
maxU = 1
points = 5
startSplitFactor = .3
insetSplitFactor = .3
cullStartEnd = True
cgmMath.returnSplitValueList(minU,maxU,points)
cgmMath.returnSplitValueList(minU,maxU,points,startSplitFactor = startSplitFactor,insetSplitFactor = None)
cgmMath.returnSplitValueList(minU,maxU,points,startSplitFactor = None,insetSplitFactor = insetSplitFactor)
cgmMath.returnSplitValueList(minU,maxU,points,cullStartEnd = cullStartEnd)

crvUtils.returnSplitCurveList(crv,5,reverseCurve = False, maxU = .35, markPoints=True,rebuildForSplit=True)
