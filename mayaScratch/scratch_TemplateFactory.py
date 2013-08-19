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
nodeF.validateAttrArg(['spine_1_anchorJoint','rz'
assert 1==2

#Get our module
#=======================================================
part = 'l_leg_part'
m1 = r9Meta.MetaClass(part)
TemplateF.go(m1,True)

TemplateF.hasPivots(m1)
TemplateF.doCastPivots(m1)

