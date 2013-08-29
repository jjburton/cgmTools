import cgm.core
cgm.core._reload()
import maya.cmds as mc

import Red9.core.Red9_Meta as r9Meta
reload(r9Meta)
from cgm.core import cgm_Meta as cgmMeta
reload(cgmMeta)

from cgm.lib.classes import NameFactory as NameF
reload(NameF)

from cgm.lib import search
reload(search)
obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

cgmMeta.log.setLevel(cgmMeta.logging.debug)
nameTools.log.setLevel(nameTools.logging.info)
nameTools.log.setLevel(nameTools.logging.debug)

#>>>name tools
cgmMeta.NameFactory('l_lwr_eyelid_jnt').doName()
cgmMeta.cgmNode('l_lwr_eyelid_jnt').getNameDict()
cgmMeta.NameFactory('l_lwr_eyelid_jnt').doName()

from cgm.core.lib import nameTools
reload(nameTools)
nameTools.returnObjectGeneratedNameDict('l_lwr_eyelid_0_jnt')
nameTools.returnObjectGeneratedNameDict('l_lwr_eyelid_0_jnt',ignore = ['cgmIterator'])
nameTools.returnObjectGeneratedNameDict('l_lwr_eyelid_0_jnt',ignore = ['cgmName'])

nameTools.returnCombinedNameFromDict(d)
#>>> Modules
#=======================================================
#>>>> OLD
i_obj = cgmMeta.cgmObject(mc.spaceLocator()[0])
i_obj = cgmMeta.cgmNode(obj)
i_obj = cgmMeta.cgmNode(mc.ls(sl=True)[0])
i_obj.doName(nameChildren=True)
i_obj.doName(True,nameChildren=True)
for j in mc.ls(sl=True):
    cgmMeta.cgmObject(j).doName()
obj = mc.ls(sl=True)[0]
NameF.returnObjectGeneratedNameDict(obj)
NameF.doRenameHeir(obj,True)
search.returnTagInfo(obj,'cgmName')

#>>> NEW
NewName = cgmMeta.NameFactory
cgm.core._reload()

log.info( issubclass(type(i_obj),cgmMeta.cgmNode) )
NewName.go('spine_1_3_jnt').getMatchedChildren()
NewName.go('spine_1_3_jnt').getBaseIterator()
obj = mc.ls(sl=True)[0]
obj = cgmMeta.cgmNode(mc.ls(sl=True)[0])
obj.__justCreatedState__
NewName(mc.ls(sl=True)[0]).getBaseIterator()
NewName(mc.ls(sl=True)[0]).getIterator()
NewName(mc.ls(sl=True)[0]).getFastIterator()

NewName(mc.ls(sl=True)[0]).getMatchedSiblings()
NewName(mc.ls(sl=True)[0]).getMatchedParents()
NewName(mc.ls(sl=True)[0]).getMatchedChildren()
NewName(mc.ls(sl=True)[0]).returnUniqueGeneratedName()
a=NewName(mc.ls(sl=True)[0]).returnUniqueGeneratedName()
NewName(mc.ls(sl=True)[0]).getIterator()
NewName(mc.ls(sl=True)[0]).getBaseIterator()
NewName(mc.ls(sl=True)[0]).doName()
NewName(mc.ls(sl=True)[0]).doName(fastIterate = False)
NewName(mc.ls(sl=True)[0]).doName(nameChildren = True,nameShapes = True)
NewName(mc.ls(sl=True)[0]).doName(nameChildren = True,fastIterate = False)
NewName(mc.ls(sl=True)[0]).doNameObject(fastIterate = False)
NewName(mc.ls(sl=True)[0]).doName(True)
for o in mc.ls(sl=True,sn=True):
    i_o = cgmMeta.cgmNode(o)
    NewName.go(i_o).doName()

search.returnParentObject(mc.ls(sl=True)[0])
i_obj = cgmMeta.cgmNode(mc.ls(sl=True)[0])
cgmMeta.NameFactory(i_obj).getBaseIterator()
NewName(i_obj).getBaseIterator()
cgmMeta.cgmNode(mc.ls(sl=True)[0]).doName()
log.info(cgmMeta.cgmNode(mc.ls(sl=True)[0]).translate)

i_obj.doName()
i_obj.mNode
i_obj.getBaseName()
i_obj.getMayaType()
cgmMeta.cgmNode(mc.ls(sl=True)[0]).getSiblings()
cgmMeta.cgmNode(mc.ls(sl=True)[0]).getLongName()
cgmMeta.cgmNode(mc.ls(sl=True)[0]).getTransform()
cgmMeta.cgmNode(mc.ls(sl=True)[0]).parent
log.info( cgmMeta.cgmNode(mc.ls(sl=True)[0]).getNameDict() )

a = cgmMeta.cgmNode(mc.ls(sl=True)[0])
cgmPM.cgmPuppet('Kermit')
a.__justCreatedState__
a.doName()
log.info(a)
a.getSiblings()
a.getLongName()
a.getNameDict()
cgmMeta.cgmNode(mc.ls(sl=True)[0]).doName()
cgmMeta.cgmNode(mc.ls(sl=True)[0]).doName(nameChildren = True)

cgmMeta.cgmNode(mc.ls(sl=True)[0]).getShortName()
cgmMeta.cgmNode(mc.ls(sl=True)[0]).getBaseName()
mc.ls(dagObjects = True, type='transform')



NewName(a).getBaseIterator()
NewName(a).getIterator()
NewName(a).getMatchedSiblings()
NewName(a).getMatchedParents()
NewName(a).getMatchedChildren()
NewName(a).returnUniqueGeneratedName()