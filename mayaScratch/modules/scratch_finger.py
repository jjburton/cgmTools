import cgm.core
cgm.core._reload()
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
from cgm.core.rigger import RigFactory as Rig
#======================================================================
import cgm.core
import cgm
cgm.core._reload()
import cgm_PuppetMeta
from cgm.core import cgm_General
cgmMeta.log.setLevel(cgmMeta.logging.INFO)
cgmMeta.log.setLevel(cgmMeta.logging.DEBUG)
m1.modulePuppet
m1.getState()
m1 = r9Meta.MetaClass('l_index_part')
m1 = r9Meta.MetaClass('l_middle_part')
m1 = r9Meta.MetaClass('l_ring_part')
m1 = r9Meta.MetaClass('l_thumb_part')
m1 = r9Meta.MetaClass('l_pinky_part')
for m in ['r_index_part','r_middle_part','r_ring_part','r_thumb_part','r_pinky_part']:
    m1 = r9Meta.MetaClass(m).doRig()
for m in ['l_index_part','l_middle_part','l_ring_part','l_thumb_part','l_pinky_part']:
    m1 = r9Meta.MetaClass(m).doRig()
reload(rigging)
from cgm.lib import attributes
attributes.doBreakConnection('l_wrist_fk_anim','inverseScale')
i_rig.buildModule.__build__(i_rig)
m1.rigConnect()
m1.rig_getReport()
i_rig = Rig.go(m1,forceNew=False,autoBuild = False)#call to do general rig
m1.setState('skeleton',forceNew=True)
m1.doRig()
i_rig = Rig.go(m1,forceNew=False)#call to do general rig
m1.templateNull.handles
reload(Rig)
range(4,5)
cgmMeta.validateAttrArg([i_rig._i_rigNull.controlIK,'length'],noneValid = False)
m1.rigNull.controlIK.select()
i_rig.build(i_rig,buildTo = '')
i_rig.build(i_rig,buildTo = 'skeleton')
i_rig.build(i_rig,buildTo = 'shapes')
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

mPlug_globalScale = cgmMeta.cgmAttr('Morphy_1_masterAnim','scaleY')
reload(rUtils) 
cgmMeta.validateAttrArg(mPlug_FKIK,noneValid = True)
mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',lock=False,keyable=True)
rUtils.connectBlendChainByConstraint(ml_fkJoints[1:],ml_ikJoints[1:],ml_blendJoints[1:],driver = mPlug_FKIK ,l_constraints=['point','orient'])
d_ankleNoFlipReturn = rUtils.IKHandle_create(ml_ikJoints[1].mNode,ml_ikJoints[-2].mNode, nameSuffix = 'noFlip',
                                             rpHandle=False,controlObject='l_left_index_4_ik_anim',addLengthMulti=True,
                                             lockMid = False, globalScaleAttr=mPlug_globalScale.p_combinedName,
                                             stretch='translate',moduleInstance=m1)
	