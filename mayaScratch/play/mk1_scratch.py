#Stuff for MK 1 till we migrate to something more permenant

attrs = ['rest','mouth_up','mouth_dn','mouth_left','mouth_right','lip_seal','jaw_open','jaw_fwd','jaw_back','jaw_left','jaw_right','smile','frown','wide','narrow','cheek_blow','cheek_in']
customAttrs = ['head_tall','head_wide','head_angle_in','head_angle_out','head_in','head_out','eyes_up','eyes_out']


def mkAttrs():  
    attrs = ['rest','mouth_up','mouth_dn','mouth_left','mouth_right','lip_seal','jaw_open','jaw_fwd','jaw_back','jaw_left','jaw_right','smile','frown','wide','narrow','cheek_blow','cheek_in']
    customAttrs = ['head_tall','head_wide','head_angle_in','head_angle_out','head_in','head_out','eyes_up','eyes_out']
    
    
    mi_animHolder = cgmMeta.cgmObject('sdk_anim_attrHolder')
    mi_customHolder = cgmMeta.cgmObject('sdk_custom_attrHolder')
    
    for mObj in mi_animHolder,mi_customHolder:
        mObj.addAttr("XXX_attrs_XXX",
                     attrType = 'int',
                     keyable = False,
                     hidden = False,lock=True)     
    for a in attrs:
        cgmMeta.cgmAttr('sdk_anim_attrHolder',a,attrType = 'float', keyable = True, hidden = False)
        
    for a in customAttrs:
        cgmMeta.cgmAttr('sdk_custom_attrHolder',a,attrType = 'float', keyable = True, hidden = False)
        
#>>>Puppet
mPuppet = cgmPM.cgmPuppet(name = 'Head')
mPuppet.connectModule(mModule)   
mPuppet.gatherModules()
#after adding eyes
mPuppet._verifyMasterControl(size = 5)

#Registering a head module from a joint
mPuppet.addModule(mClass='cgmLimb',mType = 'head')

mHead = cgmPM.cgmModule('head_part')
mHead.isSkeletonized()
mHead.rigNull.msgList_connect('headRoot_jnt','moduleJoints','rigNull')
mHead.rigNull.msgList_connect('headRoot_jnt','skinJoints','rigNull')


#>>> Eye rigging
from cgm.core import cgm_PuppetMeta as cgmPM
a = cgmPM.cgmEyeballBlock(direction = 'left')
a = r9Meta.MetaClass('l_eye_rigHelper')
a = r9Meta.MetaClass('r_eye_rigHelper')
a.__mirrorBuild__()
a.__mirrorPush__()
a.__verifyModule__()
a.__updateSizeData__()

#>>Eyes
mModule = cgmPM.cgmModule('l_eye_part')
mModule = cgmPM.cgmModule('r_eye_part')
mModule.doSkeletonize()#...skeletonize eyes
mModule.doRig()#...skeletonize eyes


m1.doSetParentModule('Head_puppetNetwork')
p = cgmMeta.cgmNode('Morphy_puppetNetwork')
p.mClass
p.gatherModules()
m1 = cgmPM.cgmModule('l_eyelid_part')
m1.getNameAlias()
m1.get_allModuleChildren()
m1.isSized()
m1.doTemplate()
m1.isTemplated()
m1.doSkeletonize()
p = cgmPM.cgmPuppet(name = 'left_eye')
p._verifyMasterControl(size = 1)
p.getModules()
p.gatherModules()