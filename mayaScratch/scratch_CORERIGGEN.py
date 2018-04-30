from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()

import cgm.core.rig.general_utils as CORERIGGEN
reload(CORERIGGEN)
_d  = {'matchObj' : None,
       'matchAttr' : None,
       'drivenObj' : 'L_ball_blend_frame',
       'drivenAttr' : 'rx',
       'driverAttr' : 'L_ankle_ik_anim.ballLift', 
       'minIn' : -179, 'maxIn' : 179, 'maxIterations' : 40, 'matchValue' : -63.858}
CORERIGGEN.matchValue_iterator(**_d)

_d  = {'matchObj' : None,
       'matchAttr' : None,
       'drivenObj' : 'L_ball_blend_frame',
       'drivenAttr' : 'rz',
       'driverAttr' : 'L_ankle_ik_anim.ballTwist', 
       'minIn' : -179, 'maxIn' : 179, 'maxIterations' : 40, 'matchValue' : 34.591}

_d  = {'matchObj' : None,
       'matchAttr' : None,
       'drivenObj' : 'L_ball_blend_frame',
       'drivenAttr' : 'ry',
       'driverAttr' : 'L_ankle_ik_anim.ballSide', 
       'minIn' : -179, 'maxIn' : 179, 'maxIterations' : 40, 'matchValue' : -10.666}