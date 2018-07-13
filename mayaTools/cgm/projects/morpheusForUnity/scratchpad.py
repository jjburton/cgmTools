import cgm.core.rig.ik_utils as IK
reload(IK)

ml_segJoints = cgmMeta.validateObjListArg(mc.ls(sl=1))
mModule = cgmMeta.asMeta('segment_part')#...noend, lever

l_joints = mc.ls(sl=1)
d_test = {'jointList':l_joints,
          'baseName' :"{0}_seg_{1}".format('test',1),                              
          'driverSetup':None,
          'squashStretch':None,
          'connectBy':'parent',
          'loftAxis':'z',
          'extendEnds':True,
          'msgDriver':'driverGroup',
          'extraSquashControl':False,
          'baseName':'brow',
          'connectBy':'constraint'}

mSurf = IK.ribbon(**d_test)



import cgm.projects.morpheusForUnity.m_utils as MORPHYUTILS
reload(MORPHYUTILS) 

MORPHYUTILS.rigJoint_verify()
MORPHYUTILS.driverGroup_verify()
MORPHYUTILS.rigJoint_connectFromRig()

driven1 = [u'L_lip_corner_rig',u'L_lip_upr_rig',u'CTR_lip_upr_rig',u'R_lip_upr_rig',u'R_lip_corner_rig']
driven2 = [u'L_lip_corner_rig',u'L_lip_lwr_rig',u'CTR_lip_lwr_rig',u'R_lip_lwr_rig',u'R_lip_corner_rig']

influences1 =[u'L_lip_corner_anim',u'L_lip_upr_anim',u'CTR_lip_upr_anim',u'R_lip_upr_anim',u'R_lip_corner_anim']
influences2 =[u'L_lip_corner_anim',u'L_lip_lwr_anim',u'CTR_lip_lwr_anim',u'R_lip_lwr_anim',u'R_lip_corner_anim']

d_test = {'driven1':driven1,
          'driven2':driven2,
          'influences1':influences1,
          'influences2':influences2,
          'baseName':'lipRibbons',
          'baseName1' :"uprLip",
          'baseName2':"lwrLip",
          'extendEnds':True,
          'msgDriver':'driverGroup'}
reload(MORPHYUTILS)
MORPHYUTILS.ribbon_seal(**d_test)



driven1 = [u'L_lip_corner_rig',u'L_lip_upr_rig',u'CTR_lip_upr_rig',u'R_lip_upr_rig',u'R_lip_corner_rig']
driven2 = [u'L_lip_corner_rig',u'L_lip_lwr_rig',u'CTR_lip_lwr_rig',u'R_lip_lwr_rig',u'R_lip_corner_rig']

influences1 =[u'L_lip_corner_anim',u'L_lip_upr_anim',u'CTR_lip_upr_anim',u'R_lip_upr_anim',u'R_lip_corner_anim']
influences2 =[u'L_lip_corner_anim',u'L_lip_lwr_anim',u'CTR_lip_lwr_anim',u'R_lip_lwr_anim',u'R_lip_corner_anim']

d_test = {'driven1':driven1,
          'driven2':driven2,
          'influences1':influences1,
          'influences2':influences2,
          'baseName':'lipRibbons',
          'baseName1' :"uprLip",
          'baseName2':"lwrLip",
          'sealDriver1':'L_lip_corner_anim',
          'sealDriver2':'R_lip_corner_anim',
          'sealDriverMid':'CTR_lip_upr_anim',
          'extendEnds':True,
          'sealSplit':True,
          'specialMode':'endsToInfluences',
          'settingsControl':'jaw_rig',
          'msgDriver':'driverGroup'}
reload(MORPHYUTILS)
MORPHYUTILS.ribbon_seal(**d_test)
d_split = {'driven1':driven1,
           'driven2':driven2,
           'sealDriver1':'L_lip_corner_anim',
           'sealDriver2':'R_lip_corner_anim',
           'sealDriverMid':'CTR_lip_upr_anim',
           'settingsControl':'jaw_rig',
           'buildNetwork':True,
           }
reload(MORPHYUTILS)
MORPHYUTILS.split_blends(**d_split)

import cgm.core.lib.math_utils as MATH
reload(MATH)
l = [4.020265273374398, 2.712863014235007,1.2084344688755784,2.7127737672840446, 4.020333705296969]
l = [10,2]
MATH.normalizeListToSum(l)
MATH.normalizeListToSum(l,10.0)
