import cgm.core
cgm.core._reload()
import maya.cmds as mc

import Red9.core.Red9_Meta as r9Meta
reload(r9Meta)
from cgm.lib.classes import NameFactory as nameF
reload(nameF)

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
from cgm.core import cgm_General as cgmGeneral
from cgm.core.rigger import ModuleFactory as mFactory
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.rigger import JointFactory as jFactory

reload(mFactory)
reload(tFactory)
reload(jFactory)
from cgm.lib import curves
reload(curves)
obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
curves.createControlCurve('circleArrow',1, absoluteSize=False)
curves.createCurve('circleArrowInterior')

#>>> Modules
#=======================================================
m1 = cgmPM.cgmModule(name = 'test')
m1 = cgmPM.cgmModule('spine_part',initializeOnly = True)
m1 = cgmPM.cgmModule('spine_part')
m1.coreNames.value
cgmPM.cgmModule('spine_part').__verify__()
m1.coreNames.__verify__()
#518 w doStore
m1.initialize()
m1.getPartNameBase()

a.getState()
a.templateNull.handles = 1
a.templateNull.__setattr__('handles',0)
str_m1 = 'spine_part'
str_m1 = 'l_foot_part'
mFactory.deleteSkeleton(m1)
mFactory.returnExpectedJointCount(m1)
m1.isSized()
m1 = r9Meta.MetaClass(str_m1)
m1.setState('template',forceNew = True)
m1.storeTemplatePose()
m1.loadTemplatePose()
m1.isSkeletonized()
m1.getGeneratedCoreNames()
tFactory.updateTemplate(m1,False)

r9Meta.MetaClass('pelvis_tmplObj').translate

m1.setState('size')
m1.setState('skeleton',forceNew = True)
m2.setState('template',forceNew = True)
tFactory.returnModuleBaseSize(m2)
m2.rigNull.skinJoints
m2.moduleParent.rigNull.skinJoints
m2.templateNull.controlObjects
m2 = r9Meta.MetaClass('l_hand_part')