import cgm.core
cgm.core._reload()
import maya.cmds as mc

import Red9.core.Red9_Meta as r9Meta
reload(r9Meta)
#from cgm.lib.classes import NameFactory as nameF
#reload(nameF)
from cgm.core.lib import nameTools

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
from cgm.lib import search
from cgm.core.rigger import ModuleFactory as mFactory
from cgm.core.rigger import PuppetFactory as pFactory
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.rigger import JointFactory as jFactory
from cgm.lib import attributes
reload(attributes)
reload(pFactory)
reload(mFactory)
reload(tFactory)
reload(jFactory)


pFactory.stateCheck(m1.modulePuppet)




p1 = cgmPM.cgmPuppet(name = 'bob')
p1.connectModule(leg)
pFactory.animSetAttr(m1.modulePuppet,'visSub',1,True)
#>>> Morphy Puppet
#=======================================================
Morphy = cgmPM.cgmPuppet('Morphy_puppetNetwork')
Morphy.p_nameShort
Morphy.getModules()
Morphy.mirrorMe()
Morphy.puppetSet.select()

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
mTypes = ['cgmPuppet','cgmMorpheusPuppet','cgmMorpheusMakerNetwork']
r9Meta.getMetaNodes(mAttrs = 'mClass', mTypes=mTypes,dataType = '')
a = cgmMeta.getMetaNodesInitializeOnly(mTypes = ['cgmPuppet','cgmMorpheusPuppet','cgmMorpheusMakerNetwork'],dataType='')
a = r9Meta.getMetaNodes(mTypes=['cgmMorpheusMakerNetwork','cgmPuppet','cgmMorpheusPuppet'],dataType = 'mClass',initializeOnly = True)
log.info(a)
from cgm.core.lib import nameTools

#>>> Rig Block - eye
#=======================================================
nameTools.log.setLevel(nameTools.logging.INFO)
nameTools.log.setLevel(nameTools.logging.DEBUG)
cgmPM.log.setLevel(cgmPM.logging.INFO)
cgmPM.log.setLevel(cgmPM.logging.DEBUG)
mFactory.log.setLevel(mFactory.logging.DEBUG)
import cgm.core
cgm.core._reload()
from cgm.core import cgm_PuppetMeta as cgmPM
a = cgmPM.cgmEyeballBlock(direction = 'left')
a = r9Meta.MetaClass('l_eye_rigHelper')
a.mNode
a.pupilHelper
a.__verifyModule__()
a.__updateSizeData__()
p=a.__buildSimplePuppet__()
cgmPM.getSettingsColors('')
p.getModules()
a.__rebuildShapes__()
a.doName(nameChildren=True)
a.connectModule(m1)
b = cgmPM.cgmEyeball(name = 'eye',direction = 'left')
m1 = cgmPM.cgmModule(name = 'eye',direction = 'left')
m1.__verifySelectionSet__()
m1 = cgmPM.cgmModule('l_eye_part')
m1 = cgmPM.cgmModule('l_eyelid_part')
m1.getNameAlias()
m1.get_allModuleChildren()
m1.isSized()
m1.doTemplate()
m1.isTemplated()
m1.doSkeletonize()
p = cgmPM.cgmPuppet(name = 'left_eye')
p._verifyMasterControl()
p.getModules()
p.gatherModules()
#>>> Modules
#=======================================================
import cgm.core
cgm.core._reload()
a = cgmPM.cgmPuppet(name = 'MorphyEye')
a.getGeo()
a.masterControl.controlSettings.mNode
a.masterControl.controlSettings.addAttr('skeleton',enumName = 'off:referenced:on', attrType = 'enum', defaultValue = 2, keyable = False,hidden = False)
a.masterNull.geoGroup.getAllChildren()
from cgm.lib import search
reload(search)
search.returnObjectType('Morphy_Body_GEO')
for o in a.masterNull.geoGroup.getAllChildren():
    search.returnObjectType(o)
    
cgmMeta.cgmObjectSet(setType='anim',qssState=True)
a._verifyMasterControl()
a = cgmPM.cgmPuppet(name = 'Kermit',initializeOnly=True)
a = cgmPM.cgmPuppet(name = 'Morphy')
a.__verify__()
a.cgmName
a._verifyMasterControl()
b = cgmPM.cgmMorpheusMakerNetwork('Morphy_customizationNetwork')
a.__verify__()
a.getMessage('asdf')
a.puppetSet.value = []
b.mNode
a = cgmPM.cgmPuppet('Kermit_puppetNetwork')
a.masterNull.mNode
b = cgmPM.cgmPuppet(name = 'Testing')
assert a == b,'no'
a==b
a.mNode
b.mNode
k = cgmMeta.cgmObject(name = 'testModule')

cgmPM.cgmModuleBufferNode(name = 'test',bufferType = 'coreNames', overideMessageCheck = True).doName()
a = cgmPM.cgmModuleBufferNode(bufferType = 'coreNames', overideMessageCheck = True)
a = cgmPM.cgmModuleBufferNode(name = 'test', module = k, bufferType = 'coreNames', overideMessageCheck = True)
a.doName()
a.mNode