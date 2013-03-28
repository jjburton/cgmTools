import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()

from cgm.core.classes import SnapFactory as Snap
reload(Snap)
from cgm.core.rigger import RigFactory as Rig
reload(Rig)
from cgm.lib import curves
from cgm.lib import distance
from cgm.lib import locators
from cgm.lib import attributes
reload(attributes)
reload(distance)
from cgm.lib import nodes
reload(nodes)
obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
orientation = ['xyz']
orientation[1]
#>>> Modules
#=======================================================
m1 = r9Meta.MetaClass('spine_part')
m1.__dict__.keys()
m1.rigNull.skinJoints
i_rig = Rig.go(m1)
m1.getState()
i_rig.d_controlShapes
rig_segmentFK(i_rig.d_controlShapes)
Rig.registerControl('pelvis_anim')
l_joints = mc.ls(sl=True)

s = cgmMeta.cgmAttr('pelvis_surfaceJoint','scaleX')
s.p_hidden = False
curves.createControlCurve('semiSphere',10,'z-')
attributes.doSetAttr('closestPointOnSurface1','inPostionX',5)
mc.setAttr('closestPointOnSurface1.inPostionX',5)
m1 = cgmPM.cgmModule(name = 'test')
m1 = cgmMeta.cgmNode('spine_part')
m1.setState('skeleton',forceNew = True)
m1.rigNull.skinJoints
m1.getModuleColors()
m1.getPartNameBase()
m1.modulePuppet.getGeo()
targetObj = mc.ls(sl=True)[0]
distance.returnClosestPointOnSurfaceInfo(targetObj,'test_controlSurface')
distance.returnClosestUV(targetObj,'test_controlSurface')
log.info(a)
nodes.createFollicleOnMesh('spine_controlSurface','test')
locators.locMeClosestUVOnSurface(mc.ls(sl=True)[0], 'test_controlSurface', pivotOnSurfaceOnly = False)


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



l_joints = [u'|pelvis_surfaceJoint', u'|pelvis_surfaceJoint|spine_1_surfaceJoint', u'|pelvis_surfaceJoint|spine_1_surfaceJoint|spine_1_1_surfaceJoint', u'|pelvis_surfaceJoint|spine_1_surfaceJoint|spine_1_1_surfaceJoint|spine_1_2_surfaceJoint', u'|pelvis_surfaceJoint|spine_1_surfaceJoint|spine_1_1_surfaceJoint|spine_1_2_surfaceJoint|spine_2_surfaceJoint', u'|pelvis_surfaceJoint|spine_1_surfaceJoint|spine_1_1_surfaceJoint|spine_1_2_surfaceJoint|spine_2_surfaceJoint|spine_2_1_surfaceJoint', u'|pelvis_surfaceJoint|spine_1_surfaceJoint|spine_1_1_surfaceJoint|spine_1_2_surfaceJoint|spine_2_surfaceJoint|spine_2_1_surfaceJoint|spine_2_2_surfaceJoint', u'|pelvis_surfaceJoint|spine_1_surfaceJoint|spine_1_1_surfaceJoint|spine_1_2_surfaceJoint|spine_2_surfaceJoint|spine_2_1_surfaceJoint|spine_2_2_surfaceJoint|sternum_surfaceJoint']
surfaceBuffer= u'test_distanceBuffer'

Rig.addSquashAndStretchToControlSurfaceSetup(surfaceBuffer,l_joints)

from cgm.lib import skinning,distance,logic
cluster = 'spine_controlSurface'
reload(skinning)
reload(distance)
reload(logic)
skinning.simpleControlSurfaceSmoothWeights(cluster)
ns = cgmMeta.cgmNode('spine_controlSurface')
ns.getComponents('cv')[-1]

from cgm.lib import deformers
deformers.returnObjectDeformers(obj,deformerTypes = 'skinCluster')

reload(Rig)
Rig.controlSurfaceSmoothWeights('spine_controlSurface')