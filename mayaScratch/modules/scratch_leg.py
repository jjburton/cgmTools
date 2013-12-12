import cgm.core
cgm.core._reload()
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
from cgm.core.rigger import RigFactory as Rig
#======================================================================
import cgm.core.__init__
reload(cgm.core.__init__)
i_morphyNet = cgmMeta.cgmNode('Morphy_customizationNetwork')
i_morphyNet.setState('rig')
cgm.core._reload()
reload(Rig)
import cgm.core
leg = r9Meta.MetaClass('l_leg_part')
leg = r9Meta.MetaClass('r_leg_part')
leg.rig_getHandleJoints()
leg.setState('skeleton',forceNew=True)
Rig.get_report(leg)
i_rig._i_rigNull.pivot_ball.select()
leg.rigConnect()
leg.rigDelete()
spine.isRigged()
leg = cgmPM.cgmLimb(mType = 'leg', direction = 'left')
leg.doSize( sizeMode = 'manual', posList = [[0,1,0],[0,.5,0],[0,.01,0],[0,0.01,.02]])
leg.isSized()
cgmMeta.cgmObject('l_hip_blend_jnt').r
leg.rigDisconnect()
i_rig.get_report()
i_rig = Rig.go(leg,forceNew=False)#call to do general rig
leg.setState('skeleton',forceNew=True)
reload(Rig)
i_rig._i_masterControl
i_rig._ml_skinJoints
i_rig.build(i_rig,buildTo = '')
i_rig.build(i_rig,buildTo = 'skeleton')
i_rig.build(i_rig,buildTo = 'shapes')
i_rig.build(i_rig,buildTo = 'controls')
i_rig.build(i_rig,buildTo = '')
i_rig.isRigSkeletonized()
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_shapes(i_rig)
Rig.get_influenceChains(leg)
Rig.get_segmentHandleChains(leg)
Rig.get_segmentChains(leg)
leg.rigNull.msgList_getMessage('segment0_InfluenceJoints')
leg.rigNull.msgList_getMessage('rigJoints')
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_foot(i_rig)
i_rig.buildModule.build_FKIK(i_rig)
i_rig.buildModule.build_deformation(i_rig)
i_rig.buildModule.build_rig(i_rig)
i_rig._get_simpleRigJointDriverDict()
Rig.get_segmentHandleTargets(leg)
i_rig.buildModule.build_twistDriver_hip(i_rig)
i_rig.buildModule.build_twistDriver_ankle(i_rig)
leg.rig_getHandleJoints()
leg.isRigged()
reload(Rig)
leg.rigNull.msgList_getMessage('ikJoints',False)
i_rig._i_rigNull.getMessage('ikJoints',False)
i_rig.buildModule.build_matchSystem(i_rig)
i_rig = Rig.go(leg,forceNew=False,autoBuild = False, ignoreRigCheck = True)#call to do general rig

i_rig.buildModule.__build__(i_rig)
cgmRigMeta.log.setLevel(cgmRigMeta.logging.INFO)
cgmRigMeta.log.setLevel(cgmRigMeta.logging.DEBUG)