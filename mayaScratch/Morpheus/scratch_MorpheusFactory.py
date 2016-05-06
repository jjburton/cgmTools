import maya.cmds as mc

import Red9.core.Red9_Meta as r9Meta
reload(r9Meta)
from cgm.lib.classes import NameFactory as nameF
reload(nameF)
nameF.doNameObject()
from cgm.core.rigger import PuppetFactory as pFactory
from cgm.core.rigger import MorpheusFactory as morphyF
from cgm.core.rigger import ModuleFactory as mFactory
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.rigger import JointFactory as jFactory

from cgm.core import cgm_PuppetMeta as cgmPM

from morpheusRig_v2.core import CustomizationFactory as CustomF
reload(CustomF)
reload(morphyF)
CustomF.go()

reload(pFactory)
reload(morphyF)
reload(mFactory)
reload(tFactory)
reload(jFactory)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

import cgm.core
cgm.core._reload()

#>>> Face Controls - 06.23.2014
#=======================================================
reload(morphyF)

_obj = 'face_attrHolder'
morphyF.faceControls_verify()
morphyF.faceControls_verify(_obj)
morphyF.get_blendshapeListToMake()

#>>> Generate Morpheus asset Template
m1 = cgmMeta.cgmNode('Morphy_customizationNetwork')
m1.connectChildNode('Morphy_Body_GEO','baseBodyGeo')
CustomF.go('Morphy_customizationNetwork')
p = cgmPM.cgmMorpheusMakerNetwork(name = customizationNode)
p.jointList
p.leftJoints


from cgm.lib import attributes
def dup_morphyHeadShape(headToDup = 'UprFocus'):
    _sl = mc.ls(sl=True)
    if mc.objExists('bs_grp'):
        mGroup  = cgmMeta.cgmObject('bs_grp')
    else:
        mGroup  = cgmMeta.cgmObject()
        mGroup.addAttr('cgmName','bs')
        mGroup.addAttr('cgmType','grp')
        mGroup.doName()
    mGroup.v = 0
    result = mc.promptDialog(title='blendshape Name',
                             message='Enter Name:',
                             button=['OK', 'Cancel'],
                             defaultButton='OK',
                             cancelButton='Cancel',
                             dismissString='Cancel')
    if result:
        newName = mc.promptDialog(query=True, text=True)
        _name = newName
        if mc.objExists(_name):
            log.warning("Deleting {0}".format(_name))
            mc.delete(_name)
        log.info(_name)
        newMesh = mc.duplicate(headToDup)
        mMesh = cgmMeta.cgmObject(newMesh[0])
        attributes.doSetLockHideKeyableAttr(mMesh.mNode,False,True,True)			    
        mMesh.rename(_name)
        mMesh.parent = mGroup
        mMesh.translate = [0,0,0]
        if _sl:mc.select(_sl)
        return True
    return False


#>>> Morpheus Building - 04.28.2014
#=======================================================
'''
This is a part of the rewrite for beta push 2014
'''
from cgm.core.rigger import MorpheusFactory as morphyF
reload(morphyF)
mAsset = cgmPM.cgmMorpheusMakerNetwork('M1_customizationNetwork')
mPuppet = mAsset.mPuppet
mPuppet.templateSettingsCall(mode = 'reset')
mPuppet.templateSettingsCall(mode = None)
mAsset.__verify__()
mPuppet.getState()
mPuppet.isTemplated()
mPuppet.masterNull.geoGroup
mAsset.verifyPuppet()#...call to verify the puppet 

morphyF.updateTemplate()
for mModule in mPuppet.moduleChildren:
    mModule.isTemplated()

#>> Get Geo ------------------------------------------------------
reload(morphyF)
morphyF.geo_getActive(mAsset)
morphyF.geo_verify(mAsset)

#>> Puppet ------------------------------------------------------
mAsset = cgmPM.cgmMorpheusMakerNetwork('M1_customizationNetwork')
mPuppet = mAsset.mPuppet

mAsset.verifyPuppet()
reload(morphyF)
morphyF.puppet_verifyAll(mAsset)

morphyF.geo_verify(mAsset)


#>> Connect puppet vis to asset setttings


#Makes the puppet structure
mAsset.verifyPuppet()
mAsset.mClass
mAsset.mPuppet

#>>>Sizing data
reload(morphyF)
morphyF.verify_sizingData(mAsset)
morphyF.verify_sizingData(mAsset)['neckHead'][1]
#Get positional data for modules
morphyF.verifyMorpheusNodeStructure(mAsset.mPuppet)#Verify nodes

morphyF.setState(mAsset)#Call to change state
#Module to play with
m1 = cgmMeta.cgmNode('spine_part')

#>>>State pushing ----------------------------------------------------------
from cgm.core.rigger import PuppetFactory
reload(PuppetFactory)

from cgm.core.rigger import ModuleFactory
reload(ModuleFactory)
from cgm.core.rigger import TemplateFactory
reload(TemplateFactory)

#>>>Template state specific
m1.storeTemplatePose()
m1.loadTemplatePose()
morphyF.updateTemplate(mAsset)







#>>> Morpheus
#=======================================================
p = cgmPM.cgmMorpheusMakerNetwork('Morphy_customizationNetwork')

p.baseBodyGeo
p.connectChildNode('Morphy_puppetNetwork','mPuppet')
p = cgmPM.cgmPuppet("Morphy_puppetNetwork")
p.setState('skeleton',forceNew = True)
p.setState('template',forceNew = True)
p.setState('size',forceNew = True)
morphyF.verifyMorpheusNodeStructure(p.mPuppet)
morphyF.setState(p,2)
reload(morphyF)
p.mNode
p.mNode
morphyF.verify_customizationData(p)['neck']
cgmPM.cgmPuppet('Morphy_puppetNetwork')
k = cgmPM.cgmMorpheusMakerNetwork('Morphy_customizationNetwork')
k.mNode
str_m1 = 'spine_part'
part = 'neck_part'
m2 = r9Meta.MetaClass(part)
#[2.4872662425041199, 132.08547973632812, 11.861419200897217] #
m1 = r9Meta.MetaClass(str_m1)
p.setState('skeleton')
log.info(m1.getState())
m1.getGeneratedCoreNames()
tFactory.updateTemplate(m2)
m2.setState('size')
m2.setState('skeleton',forceNew = True)
m2.setState('template',forceNew = False)
tFactory.returnModuleBaseSize(m2)
m2.rigNull.skinJoints
m2.moduleParent.rigNull.skinJoints
m2.templateNull.controlObjects
m2 = r9Meta.MetaClass('l_hand_part')



#Face Stuff
from cgm.core.rigger import MorpheusFactory as morphyF
reload(morphyF)
morphyF.faceControls_verify('face_attrHolder',reportTimes = True)
morphyF.face_connectAttrHolderToBSNodes('face_attrHolder',True, reportTimes = True)