import cgm.core
cgm.core._reload()
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
from cgm.core.rigger import RigFactory as Rig
#======================================================================
issubclass(type(i_rig._i_masterControl),cgmMeta.cgmObject)
cgmMeta.validateObjArg(i_rig._i_masterControl.mNode,cgmMeta.cgmObject)
cgmMeta.log.setLevel(cgmMeta.logging.INFO)
cgmMeta.log.setLevel(cgmMeta.logging.DEBUG)
jFactory.log.setLevel(jFactory.logging.DEBUG)
m1 = r9Meta.MetaClass('l_clav_part')
m1 = r9Meta.MetaClass('r_clav_part')
m1 = r9Meta.MetaClass('l_arm_part')
m1 = r9Meta.MetaClass('r_arm_part')
m1.rigDelete()
m1.doRig()
m1 = r9Meta.MetaClass('l_arm_part')
Rig.get_report(m1)
m1.rigNull.blendJoints
m1.rigConnect()
m1.isRigged()
m1.rigDelete()
m1.rigNull.moduleJoints
i_rig = Rig.go(m1,forceNew=False,autoBuild = False)#call to do general rig
m1.setState('skeleton',forceNew=True)
m1.getState()
m1.modulePuppet.getModuleFromDict({'moduleType':'thumb'})
m1.modulePuppet.getModuleFromDict(moduleType= ['torso','spine'])
m1.modulePuppet.getModuleFromDict(checkDict = {'moduleType':'head'})
i_rig = Rig.go(m1,forceNew=False)#call to do general rig
reload(Rig)
i_rig._get_simpleRigJointDriverDict()
i_rig._i_masterControl
i_rig.build(i_rig,buildTo = '')
i_rig.build(i_rig,buildTo = 'skeleton')
i_rig.build(i_rig,buildTo = 'shapes')
i_rig.build(i_rig,buildTo = 'controls')
Rig.get_report(m2)
m1.rigNull.getMessage('skinJoints',False)
m1.rigNull.msgList_getMessage('handleJoints')
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_FKIK(i_rig)
i_rig.buildModule.build_deformation(i_rig)
i_rig.buildModule.build_rig(i_rig)
i_rig.buildModule.build_matchSystem(i_rig)
i_rig.buildModule.build_twistDriver_shoulder(i_rig)
i_rig.buildModule.build_twistDriver_wrist(i_rig)
reload(Rig)
i_rig._get_handleJoints()
cgmMeta.cgmObject('l_ankle_ik_anim').scalePivotY = 0
i_rig.build(i_rig)
i_rig._i_deformNull.controlsIK