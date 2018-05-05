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



import cgm.core.rig.ik_utils as IK
reload(IK)
ml_segJoints = cgmMeta.validateObjListArg(mc.ls(sl=1))
mModule = cgmMeta.asMeta('segment_part')#...noend, lever
l_joints = mc.ls(sl=1)
d_test = {'jointList':l_joints,
          'baseName' :"{0}_seg_{1}".format('test',1),                              
          'driverSetup':'stableBlend',
          'squashStretch':'both',
          'loftAxis':'x',
          'masterScalePlug':'settings_anim.scaleZ',          
          'settingsControl':'settings_anim',
          'extraSquashControl':True,
          'squashFactorMode':'midPeak',
          'squashFactorMax':2.0,
          'connectBy':'constraint',
          'moduleInstance' : mModule}

mSurf = IK.ribbon(**d_test)


d_test = {'jointList':l_joints,
          'baseName' :"{0}_seg_{1}".format('test',1),                              
          'driverSetup':'stableBlend',
          'squashStretch':'both',
          'loftAxis':'x',
          'squashStretchMain':'pointDist',
          'settingsControl':'settings_anim',
          'extraSquashControl':True,
          'squashFactorMode':'midPeak',
          'masterScalePlug':'create',                    
          'squashFactorMin':0,
          'squashFactorMax':2.0,
          'influences':['base_skin','end_skin'],
          'connectBy':'constraint',
          'moduleInstance' : None}


#Need a distance measure item to drive master scale




#Mid attach setup... -------------------------------------------------------------
reload(IK)

l_joints = [u'base_blend_ribbonIKDriver',
            u'segment_segMid_ik_anim',
            u'end_blend_ribbonIKDriver']
mModule = cgmMeta.asMeta('segment_part')#...noend, lever
d_midTest = {'jointList':l_joints,
             'baseName' :"{0}_midTrack".format('test'),
             'driverSetup':'stableBlend',
             'squashStretch':None,
             'msgDriver':'masterGroup',
             'specialMode':'noStartEnd',
             'connectBy':'constraint',
             'moduleInstance' : mModule}
mSurf = IK.ribbon(**d_test)



#Spline --------------------------------------------------------------------
import cgm.core.rig.ik_utils as IK
reload(IK)

spline(jointList = None,
       useCurve = None,
       orientation = 'zyx',
       secondaryAxis = 'y+',
       baseName = None,
       stretchBy = 'translate',
       advancedTwistSetup = False,
       extendTwistToEnd = False,
       reorient = False,
       moduleInstance = None,
       parentGutsTo = None)

_d = {'globalScaleAttr':'spine_masterAnim.sy',
      'stretch':False,
      'controlObject':'spine_ik_anim',
      'moduleInstance':'spine_part'}
_start = 'spine_ik_1_frame'
_end = 'spine_ik_3_frame'
reload(IK)
IK.handle(_start,_end,**_d)