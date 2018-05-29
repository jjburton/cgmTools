import cgm.core.rig.general_utils as CORERIGGEN
reload(CORERIGGEN)
_d  = {'matchObj' : None,
      'matchAttr' : None,
      'drivenObj' : 'L_ball_blend_frame',
      'drivenAttr' : 'rx',
      'driverAttr' : 'L_ankle_ik_anim.rx', 
      'minIn' : -180, 'maxIn' : 180, 'maxIterations' : 40, 'matchValue' : -33.242}
CORERIGGEN.matchValue_iterator(**_d)


_d  = {'matchObj' : None,
       'matchAttr' : None,
       'drivenObj' : 'L_ball_blend_frame',
       'drivenAttr' : 'rz',
       'driverAttr' : 'L_ankle_ik_anim.ballTwist', 
       'minIn' : -179, 'maxIn' : 180, 'maxIterations' : 40, 'matchValue' : 34.591}

_d  = {'matchObj' : None,
       'matchAttr' : None,
       'drivenObj' : 'L_ball_blend_frame',
       'drivenAttr' : 'ry',
       'driverAttr' : 'L_ankle_ik_anim.ballSide', 
       'minIn' : -179, 'maxIn' : 180, 'maxIterations' : 40, 'matchValue' : -10.666}




