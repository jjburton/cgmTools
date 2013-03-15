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

#>>> Modules
#=======================================================
i_obj = cgmMeta.cgmObject(mc.spaceLocator()[0])
i_obj = cgmMeta.cgmNode(obj)
i_obj = cgmMeta.cgmNode(mc.ls(sl=True)[0])
i_obj.doName()
i_obj.doName(True,nameChildren=True)
for j in mc.ls(sl=True):
    cgmMeta.cgmObject(j).doName()
obj = 'pelvis_surfaceJoint'
NameF.returnObjectGeneratedNameDict(obj)
NameF.doRenameHeir(obj,True)
search.returnTagInfo(obj,'cgmName')