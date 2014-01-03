import cgm.core
cgm.core._reload()
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
from cgm.core.rigger import RigFactory as Rig
from cgm.core import cgm_General as cgmGeneral
reload(Rig)
#======================================================================
from cgm.core.rigger import ModuleFactory as mFactory
from cgm.core.rigger import JointFactory as jFactory
reload(jFactory)

cgmMeta.log.setLevel(cgmMeta.logging.INFO)
cgmMeta.log.setLevel(cgmMeta.logging.DEBUG)
mFactory.log.setLevel(mFactory.logging.INFO)
mFactory.log.setLevel(mFactory.logging.DEBUG)
m1.modulePuppet.__verify__()
m1.getState()
@cgmGeneral.Timer

b = cgmPM.cgmEyebrow(name = 'brow')
m1 = cgmPM.cgmModule('brow_part')
m1.getNameAlias()
m1.get_allModuleChildren()
m1.isSized()
m1.doTemplate()
m1.isTemplated()
m1.doSkeletonize()
m1.modulePuppet._verifyMasterControl()



m1 = cgmPM.cgmModule('l_eye_part')
m1.__verify__()

m1.modulePuppet._verifyMasterControl()
m1.helper.__storeNames__()


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
i_rig.buildModule.build_matchSystem(i_rig)

i_rig.doBuild()

#Queries	
m1.isSized()
m1.setState('skeleton',forceNew=True)
m1.skeletonDelete()
m1.doRig()


#>>> Rig Block - brow
#=======================================================
nameTools.log.setLevel(nameTools.logging.INFO)
nameTools.log.setLevel(nameTools.logging.DEBUG)
cgmPM.log.setLevel(cgmPM.logging.INFO)
cgmPM.log.setLevel(cgmPM.logging.DEBUG)
mFactory.log.setLevel(mFactory.logging.DEBUG)
import cgm.core
cgm.core._reload()
from cgm.core import cgm_PuppetMeta as cgmPM
a = cgmPM.cgmEyebrowBlock()
a.mirrorBrowCurvesTMP()
m1 = a.__buildModule__()
a = r9Meta.MetaClass('brow_rigHelper')

p = cgmMeta.cgmNode('Morphy_puppetNetwork')
p.mClass
m1.mNode

a = r9Meta.MetaClass('brow_rigHelper')
m1 = a.__buildModule__()
m1.doSetParentModule('neck_part')
p.gatherModules()

m1.getState()


