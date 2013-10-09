import cgm.core
cgm.core._reload()
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
from cgm.core.rigger import RigFactory as Rig
from cgm.core import cgm_General as cgmGeneral
reload(Rig)
#======================================================================
cgmMeta.log.setLevel(cgmMeta.logging.INFO)
cgmMeta.log.setLevel(cgmMeta.logging.DEBUG)
mFactory.log.setLevel(mFactory.logging.INFO)
mFactory.log.setLevel(mFactory.logging.DEBUG)
m1.modulePuppet.__verify__()
m1.getState()


#Squashstretch face =====================================================
jointList = mc.ls(sl=True)
influenceJoints = mc.ls(sl=True)
startControl = 'upr_influenceBottom_crv'
endControl = 'upr_influenceTop_crv'
startControl = 'lwrSquash_influenceStart_crv'
endControl = 'lwrSquash_influenceEnd_crv'
controlOrientation = 'zyx'
t = rUtils.createCGMSegment(jointList,influenceJoints=influenceJoints, startControl=startControl,endControl=endControl,secondaryAxis = 'zdown',controlOrientation=controlOrientation,additiveScaleSetup=True,connectAdditiveScale=True)

