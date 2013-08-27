import cgm.core
cgm.core._reload()
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
from cgm.core.rigger import RigFactory as Rig
from cgm.core import cgm_General
reload(Rig)
#======================================================================
cgmMeta.log.setLevel(cgmMeta.logging.INFO)
cgmMeta.log.setLevel(cgmMeta.logging.DEBUG)
mFactory.log.setLevel(mFactory.logging.INFO)
mFactory.log.setLevel(mFactory.logging.DEBUG)
m1.modulePuppet.__verify__()
m1.getState()
m1 = cgmPM.cgmModule('l_eye_part')
m1.__verify__()

m1.modulePuppet._verifyMasterControl()
m1.helper.__storeNames__()

i_rig.buildModule.__build__(i_rig)
m1.rigConnect()
m1.rig_getReport()
i_rig = Rig.go(m1,forceNew=False,autoBuild = False)#call to do general rig

i_rig = Rig.go(m1,forceNew=False)#call to do general rig
m1.templateNull.handles

rUtils.createEyeballRig('l_eye_rigHelper',aimTargetObject = 'l_eye_ik_anim', buildIK=True)

i_rig.build(i_rig,buildTo = 'controls')
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_FKIK(i_rig)
i_rig.buildModule.build_deformation(i_rig)
i_rig.buildModule.build_rig(i_rig)
i_rig.buildModule.__build__(i_rig)
from cgm.lib import distance
l_constrainTargetJoints = [u'l_left_index_1_blend_jnt', u'l_left_index_2_blend_jnt', u'l_left_index_3_blend_jnt', u'l_left_index_4_blend_jnt', u'l_left_index_5_blend_jnt']
distance.returnClosestObject('l_left_index_1_rig_jnt',l_constrainTargetJoints)
m1.rigNull.getMessage('blendJoints',False)
m1.moduleParent.rigNull.rigJoints[-1]
i_rig.buildModule.build_matchSystem(i_rig)
reload(Rig)
from cgm.lib import cgmMath
cgmMath.isFloatEquivalent(0.002,0,2)
rUtils.matchValue_iterator(drivenAttr='l_left_index_2_ik_jnt.rz',driverAttr='left_index_noFlip_ikH.twist',minIn = -179, maxIn = 179, maxIterations = 5,matchValue=0)
cgmMeta.cgmObject('l_ankle_ik_anim').scalePivotY = 0
i_rig._i_deformNull.controlsIK

ml_ikJoints = m1.rigNull.ikJoints
ml_fkJoints = m1.rigNull.fkJoints
ml_blendJoints = m1.rigNull.blendJoints
mi_settings = m1.rigNull.settings

#Queries	
m1.isSized()
m1.setState('skeleton',forceNew=True)
m1.skeletonDelete()
m1.doRig()