import cgm.core.cgm_Meta as cgmMeta
import cgm.core.rigger.RigFactory as Rig
cgm.core._reload()

import cgm.core.lib.name_utils as NAMES
[NAMES.short(o) for o in mc.ls(sl=True)]


import cgm.core.rig.segment_utils as SEGMENT
reload(SEGMENT)




#Options =========================================================================================
jointList = [u'joint11', u'joint5', u'joint6', u'joint7', u'joint8']
useCurve = None
baseName = 'test'
connectBy = 'translate'
advancedTwistSetup = False
addMidTwist = False
extendTwistToEnd=False
moduleInstance = None