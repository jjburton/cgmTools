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