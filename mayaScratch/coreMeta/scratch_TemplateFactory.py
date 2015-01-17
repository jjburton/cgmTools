import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()

from cgm.core.classes import SnapFactory as Snap
reload(Snap)
from cgm.core.rigger import TemplateFactory as TemplateF
from cgm.core.rigger import JointFactory as jFactory
from cgm.core.classes import  NodeFactory as nodeF
reload(TemplateF)
TemplateF.doOrientTemplateObjectsToMaster(m1)
reload(jFactory)
reload(Rig)
nodeF.validateAttrArg(['spine_1_anchorJoint','rz'])
assert 1==2

#Optimization - 05.01.2014
part = 'spine_part'
m1 = r9Meta.MetaClass(part)
TemplateF.go(m1,True)



#Get our module
#=======================================================
part = 'spine_part'
part = 'l_leg_part'
m1 = r9Meta.MetaClass(part)
m1 = cgmPM.cgmModule('l_eye_part')
m1.doTemplate()
m1.isSized()
m1.getState()
m1.isTemplated()
TemplateF.go(m1,True)

TemplateF.hasPivots(m1)
TemplateF.doCastPivots(m1)

cgm.core._reload()
m1.doSkeletonize()
m1.storeTemplatePose()
mFactory.isModule(m1)
jFactory.go(m1)
m1.isSkeletonized()
m1.rigNull.msgList_get('skinJoints',False)
m1.templateNull.handles
m1.helper.msgList_get('ml_helpers',False)
m1.helper.__rebuildShapes__()
mFactory.log.setLevel(mFactory.logging.INFO)
mFactory.log.setLevel(mFactory.logging.DEBUG)

