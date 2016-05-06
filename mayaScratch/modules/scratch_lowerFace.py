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
reload(mFactory)
from cgm.core.rigger import JointFactory as jFactory
reload(jFactory)

cgmMeta.log.setLevel(cgmMeta.logging.INFO)
cgmMeta.log.setLevel(cgmMeta.logging.DEBUG)
mFactory.log.setLevel(mFactory.logging.INFO)
mFactory.log.setLevel(mFactory.logging.DEBUG)
m1.modulePuppet.__verify__()
m1.getState()


#>>> Rig Block - mouthNose
#=======================================================
nameTools.log.setLevel(nameTools.logging.INFO)
nameTools.log.setLevel(nameTools.logging.DEBUG)
cgmPM.log.setLevel(cgmPM.logging.INFO)
cgmPM.log.setLevel(cgmPM.logging.DEBUG)
mFactory.log.setLevel(mFactory.logging.DEBUG)
import cgm.core
cgm.core._reload()
a = cgmPM.cgmMouthNoseBlock(reportTimes = True)
a = cgmPM.cgmMouthNoseBlock('mouthNose_rigHelper')
a.__verify__()
m1  = a.__verifyModule__()
a = cgmPM.cgmMouthNose()

p = cgmMeta.cgmNode('Morphy_puppetNetwork')
p.mClass
p.gatherModules()

m1.mNode

m1 = r9Meta.MetaClass('mouthNose_part')
m1.getState()
m1.doSetParentModule('neck_part')
m1.doSetParentModule('neck_part')
p.gatherModules()

m1.isSkeletonized()
m1.doSkeletonize()


