from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()
import maya.cmds as mc

import cgm.core.rig.ik_utils as IK
reload(IK)


#RIGSKIN --------------------------------------------------------------------
import cgm.core.rig.skin_utils as RIGSKIN
reload(RIGSKIN)
controlSurface='test_seg_1_controlSurface'
RIGSKIN.surface_tightenEnds(controlSurface,blendLength=3,hardLength=2)
