from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()
import maya.cmds as mc

import cgm.core.rig.ik_utils as IK
reload(IK)
_d = {'globalScaleAttr':'spine_masterAnim.sy',
      'stretch':False,
      'controlObject':'spine_ik_anim',
      'moduleInstance':'spine_part'}
_start = 'spine_ik_1_frame'
_end = 'spine_ik_3_frame'
reload(IK)
IK.handle(_start,_end,**_d)
