import cgm.core
cgm.core._reload()
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
from cgm.core.rigger import RigFactory as Rig
#======================================================================
cgm.core._reload()
cgmMeta.log.setLevel(cgmMeta.logging.INFO)
cgmMeta.log.setLevel(cgmMeta.logging.DEBUG)
neckHead = r9Meta.MetaClass('neck_part')
neckHead.rig
neckHead.doRig()
neckHead.isSkeletonized()
reload(Rig)
reload(jFactory)
neckHead.isTemplated()
neckHead.rig_getSkinJoints()
neckHead.setState('skeleton',forceNew=True)
jFactory.connectToParentModule(neckHead)
jFactory.deleteSkeleton(neckHead)

neckHead.setState(3,forceNew=True)
Rig.get_report(spine)
Rig.get_report(neckHead)
Rig.get_segmentHandleTargets(neckHead)
neckHead.rigNull.getMessage('rigJoints',False)
neckHead.rigNull.getMessage('skinJoints',False)
if len(spine.rigNull.getMessage('rigJoints'))!=9:print False
neckHead.rigNull.moduleJoints[-1].getShortName()
neckHead.setState('skeleton',forceNew=True)
neckHead.moduleParent.isRigged()
neckHead.setState('rig',forceNew=True)
reload(Rig)
neckHead.rigConnect()
neckHead.isRigged()
neckHead.rigDelete()
i_rig._i_rigNull.getMessage('anchorJoints',False)
i_rig = Rig.go(neckHead,forceNew=False,autoBuild = False)#call to do general rig
i_rig.get_report()
i_rig._i_rigNull.getMessage('rigJoints')
i_rig.build_rigChain()
neckHead.rig_getRigHandleJoints()
len(i_rig._i_rigNull.skinJoints)
i_rig.get_rigDeformationJoints()
neckHead.rig_getRigHandleJoints()
i_rig._i_masterControl
i_rig.build(i_rig,buildTo = '')
i_rig.build(i_rig,buildTo = 'skeleton')
i_rig.build(i_rig,buildTo = 'shapes')
i_rig.build(i_rig,buildTo = 'controls')
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_deformation(i_rig)
i_rig.buildModule.build_rig(i_rig)
neckHead.rigNull.msgList_get('segmentHandles')
i_rig.isShaped()
Rig.get_report(neckHead)
reload(Rig)
neckHead.rigConnect()
cgmMeta.cgmObject('head_ik_1_anim').dynParentGroup.dynMode
if len(spine.rigNull.getMessage('rigJoints'))!=9:print False
spine.isRigged()