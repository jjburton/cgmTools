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
mControlFactory.go(m1)
mesh = 'Morphy_Body_GEO'
i_obj = cgmMeta.cgmObject('pelvis_templateOrientHelper')
mControlFactory.returnBaseControlSize(i_obj, mesh,axis = ['x','y','z-'])
mControlFactory.returnBaseControlSize(i_obj, mesh,axis = ['x+'])

mc.softSelect(softSelectEnabled = True)
mc.softSelect(q = True, softSelectDistance = True)
mc.softSelect(q = True, softSelectUVDistance = True)
mc.softSelect(q = True, softSelectFalloff = 2)
mc.softSelect(softSelectFalloff = 1)
mc.softSelect(softSelectDistance = 20)
mc.softSelect(softSelectUVDistance = 1)

#252ms
m1.isSkeletonized()
mControlFactory.go(obj)
m1.setState('skeleton')
tFactory.returnModuleBaseSize(m2)
m2.rigNull.skinJoints
m2.moduleParent.rigNull.skinJoints
m2.templateNull.controlObjects
m2 = r9Meta.MetaClass('l_hand_part')