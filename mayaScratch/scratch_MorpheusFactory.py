import maya.cmds as mc

import Red9.core.Red9_Meta as r9Meta
reload(r9Meta)
from cgm.lib.classes import NameFactory as nameF
reload(nameF)
nameF.doNameObject()
from cgm.core.rigger import MorpheusFactory as morphyF
from cgm.core.rigger import ModuleFactory as mFactory
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.rigger import JointFactory as jFactory

from cgm.core import cgm_PuppetMeta as cgmPM

reload(morphyF)
reload(mFactory)
reload(tFactory)
reload(jFactory)

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

import cgm.core
cgm.core._reload()
#>>> Morpheus
#=======================================================
p = cgmPM.cgmMorpheusMakerNetwork('Morphy_customizationNetwork')
p.setState('skeleton',forceNew = True)
p.mNode
p.mNode
morphyF.verify_customizationData(p)['clavicle_right'][0]
cgmPM.cgmPuppet('Morphy_puppetNetwork')
k = cgmPM.cgmMorpheusMakerNetwork('Morphy_customizationNetwork')
k.mNode
str_m1 = 'spine_part'
#[2.4872662425041199, 132.08547973632812, 11.861419200897217] #
m1 = r9Meta.MetaClass(str_m1)
p.setState('skeleton')
log.info(m1.getState())
m1.getGeneratedCoreNames()
tFactory.updateTemplate(m2)
m2.setState('size')
m2.setState('skeleton',forceNew = True)
m2.setState('template',forceNew = True)
tFactory.returnModuleBaseSize(m2)
m2.rigNull.skinJoints
m2.moduleParent.rigNull.skinJoints
m2.templateNull.controlObjects
m2 = r9Meta.MetaClass('l_hand_part')