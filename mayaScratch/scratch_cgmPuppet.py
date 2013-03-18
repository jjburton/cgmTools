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

from cgm.core.rigger import ModuleFactory as mFactory
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.rigger import JointFactory as jFactory

reload(mFactory)
reload(tFactory)
reload(jFactory)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
mTypes = ['cgmPuppet','cgmMorpheusPuppet','cgmMorpheusMakerNetwork']
r9Meta.getMetaNodes(mAttrs = 'mClass', mTypes=mTypes,dataType = '')
a = cgmMeta.getMetaNodesInitializeOnly(mTypes = ['cgmPuppet','cgmMorpheusPuppet','cgmMorpheusMakerNetwork'],dataType='')
a = r9Meta.getMetaNodes(mTypes=['cgmMorpheusMakerNetwork','cgmPuppet','cgmMorpheusPuppet'],dataType = 'mClass',initializeOnly = True)
log.info(a)
#>>> Modules
#=======================================================
import cgm.core
cgm.core._reload()
a = cgmPM.cgmPuppet(name = 'Kermit')
a = cgmPM.cgmPuppet(name = 'Kermit',initializeOnly=True)
a = cgmPM.cgmPuppet(name = 'Morphy')
b = cgmPM.cgmMorpheusMakerNetwork('Morphy_customizationNetwork')
b.__verify__()
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