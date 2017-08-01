import cgm.core.cgm_Meta as cgmMeta
import cgm.core.rigger.RigFactory as Rig
cgm.core._reload()

import cgm.core.lib.name_utils as NAMES
[NAMES.short(o) for o in mc.ls(sl=True)]


import cgm.core.rig.segment_utils as SEGMENT
reload(SEGMENT)


#BASE SETUP ========================================================================================================
SEGMENT.create_curveSetup(jointList,useCurve,'zyx','y+',baseName,stretchBy,advancedTwistSetup,addMidTwist,extendTwistToEnd,reorient,moduleInstance)

#Options =========================================================================================
jointList = [u'chain_0', u'chain_1', u'chain_2', u'chain_3', u'chain_4']
len(range(0,10))%2
useCurve = 'resultCurve'
baseName = 'test'
stretchBy = 'translate'
stretchBy = 'scale'
stretchBy = None
advancedTwistSetup = True
addMidTwist = False
addMidTwist = True
extendTwistToEnd=False
moduleInstance = None
reorient = False

SEGMENT.create_curveSetup(jointList,useCurve,'zyx','y+',baseName,stretchBy,advancedTwistSetup,addMidTwist,extendTwistToEnd,reorient,moduleInstance)

_d = {'jointList' : [u'tongue_0_jnt',
                     u'tongue_1_jnt',
                     u'tongue_2_jnt',
                     u'tongue_3_jnt',
                     u'tongue_4_jnt',
                     u'tongue_5_jnt'],
      'useCurve' : None,
      'baseName' : 'test',
      'stretchBy' : 'scale',
      'advancedTwistSetup' : True,
      'addMidTwist' : False,
      'extendTwistToEnd':False,
      'moduleInstance' : None,
      'reorient' : False}

#Segment SETUP ========================================================================================================
_d = {'jointList' : [u'chain_0', u'chain_1', u'chain_2', u'chain_3', u'chain_4'],
      'influenceJoints' : [u'lwrArm|elbowDirect', u'handDirect'],
      'addSquashStretch' : True,
      'useCurve' : 'resultCurve',
      'addTwist' : True,
      'startControl' : 'elbowDirect_crv',
      'endControl' : 'hand_crv',
      'segmentType' : 'curve',
      'rotateGroupAxis' : 'rz',
      'secondaryAxis' : None,
      'baseName' : None,
      'advancedTwistSetup' : False,
      'additiveScaleSetup' : True,
      'connectAdditiveScale' : True,
      'orientation' : 'zyx',
      'controlOrientation' : None,
      'moduleInstance' : None,
      'stretchBy' : 'scale'}
reload(SEGMENT)
SEGMENT.create(**_d)

#Squash and stretch SETUP ========================================================================================================
_d = {'jointList' : [u'chain_0', u'chain_1', u'chain_2', u'chain_3', u'chain_4'],
      'orientation' : 'zyx',
      'stretchBy' : 'scale'}
reload(SEGMENT)
SEGMENT.addSquashAndStretch_toCurve(**_d)


_d = {'jointList' : [u'chain_0', u'chain_1', u'chain_2', u'chain_3', u'chain_4'],
      'orientation' : 'zyx',
      'stretchBy' : 'scale'}
reload(SEGMENT)
SEGMENT.addAdditveScale_toCurve(**_d)


#Add mid ========================================================================================================
midReturn = rUtils.addCGMSegmentSubControl(ml_influenceJoints[1].mNode,
                                           segmentCurve = i_curve,
                                           baseParent=ml_influenceJoints[0],
                                           endParent=ml_influenceJoints[-1],
                                           midControls=ml_segmentHandles[1],
                                           baseName=mi_go._partName,
                                           controlTwistAxis =  'r'+mi_go._jointOrientation[0],
                                           orientation=mi_go._jointOrientation)
"""
joints=None,segmentCurve = None, baseParent = None, endParent = None,
midControls = None, orientation = 'zyx',controlOrientation = None,
controlTwistAxis = 'rotateY',
addTwist = True, baseName = None,
rotateGroupAxis = 'rotateZ', blendLength = None,
connectMidScale = True,
moduleInstance = None):
"""



_d = {'joints':'lwrArm|midDirect',
      'segmentCurve' : 'resultCurve_splineIKCurve_splineIKCurve',
      'baseParent':'null5_attach|elbowDirect',
      'endParent':'handDirect',
      'midControls':'mid_crv',
      #'jointList' : [u'chain_0', u'chain_1', u'chain_2', u'chain_3', u'chain_4'],
      'baseName':None,
      'controlTwistAxis':'rz',
      'orientation' : 'zyx'}

reload(SEGMENT)
SEGMENT.add_subControl_toCurve(**_d)

