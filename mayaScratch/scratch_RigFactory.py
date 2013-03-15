import cgm.core
cgm.core._reload()
import maya.cmds as mc

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta

from cgm.core.classes import SnapFactory as Snap
reload(Snap)
from cgm.core.rigger import RigFactory as Rig
reload(Rig)
from cgm.lib import curves
from cgm.lib import distance
from cgm.lib import locators
reload(distance)
from cgm.lib import nodes
reload(nodes)
obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

#>>> Modules
#=======================================================
curves.createControlCurve('semiSphere',10,'z-')

m1 = cgmPM.cgmModule(name = 'test')
m1 = r9Meta.MetaClass('spine_part')
m1.setState('skeleton')
m1.rigNull.skinJoints
m1.getModuleColors()
m1.getPartNameBase()
m1.modulePuppet.getGeo()
f = cgmMeta.cgmNode('test_foll')
f.parameterU
f = cgmMeta.cgmNode('follicle2')
a = distance.returnClosestUV(mc.ls(sl=True)[0],'test_controlSurface')
log.info(a)
nodes.createFollicleOnMesh('spine_controlSurface','test')
locators.locMeClosestUVOnSurface(mc.ls(sl=True)[0], 'test_controlSurface', pivotOnSurfaceOnly = False)

Rig.go(m1)
l_joints = mc.ls(sl=True)
Rig.createControlSurfaceSegment(l_joints)
mControlFactory.limbControlMaker(m1,['cog','segmentControls','hips'])

mesh = 'Morphy_Body_GEO'
i_obj = cgmMeta.cgmObject('hips_anim')
mControlFactory.returnBaseControlSize(i_obj, mesh,axis = ['x','y','z-'])
mControlFactory.returnBaseControlSize(i_obj, mesh,axis = ['z-'])

mc.softSelect(softSelectEnabled = True)
mc.softSelect(q = True, softSelectDistance = True)
mc.softSelect(q = True, softSelectUVDistance = True)
mc.softSelect(q = True, softSelectFalloff = 2)
mc.softSelect(softSelectFalloff = 0)
mc.softSelect(softSelectDistance = 20)
mc.softSelect(softSelectUVDistance = 30)

#252ms
m1.isSkeletonized()
mControlFactory.go(obj)
m1.setState('skeleton')
tFactory.returnModuleBaseSize(m2)
m2.rigNull.skinJoints
m2.moduleParent.rigNull.skinJoints
m2.templateNull.controlObjects
m2 = r9Meta.MetaClass('l_hand_part')