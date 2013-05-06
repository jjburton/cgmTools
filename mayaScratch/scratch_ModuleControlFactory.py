import cgm.core
cgm.core._reload()
import maya.cmds as mc

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta

from cgm.core.classes import SnapFactory as Snap
reload(Snap)
from cgm.core.rigger import ModuleControlFactory as mControlFactory
reload(mControlFactory)
from cgm.lib import search
obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

#>>> Modules
#=======================================================
m1 = cgmPM.cgmModule(name = 'test')
m1 = r9Meta.MetaClass('spine_part')
m1.setState('skeleton')
m1.getPartNameBase()
m1.modulePuppet.getGeo()
mObj = cgmMeta.cgmObject(control)
i_loc = mObj.doLoc()
i_loc.rx = i_loc.rx + 90
mObj.doCopyTransform(i_loc.mNode)
mObj.mNode
mObj.getAttr('asdfasdf')

#>>> Testing control registering
control = 'cog_controlCurve'
mControlFactory.registerControl(mc.ls(sl=True)[0])
mControlFactory.registerControl(control)
for i in range(2):log.info(i)
class dataHolder(object):
    pass
l_targetObjects = mc.ls(sl=True)
log.info(cgmMeta.cgmObject(mc.ls(sl=True)[0]).getNameDict())
log.info(cgmMeta.cgmObject(mc.ls(sl=True)[0]).doName())

str_control = 'neck_2_anim'
mControlFactory.registerControl(str_control,addExtraGroups = True,addDynParentGroup=True,
                                addConstraintGroup=True,setRotateOrder=5)

mControlFactory.registerControl(str_control, addSpacePivots = 2, addDynParentGroup = True, addConstraintGroup=True,
                                makeAimable = True, setRotateOrder=5)




