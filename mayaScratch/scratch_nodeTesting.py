
from cgm.core import cgm_Meta as cgmMeta
reload(cgmMeta)

import Red9.core.Red9_Meta as r9Meta
reload(r9Meta)

from cgm.lib.classes import NameFactory as nameF
reload(nameF)

import cgm.core
cgm.core._reload()

obj = mc.ls(sl=True)[0] or False
obj = 'Morphy_Body_GEO.f[1648]'
obj = 'pelvis_bodyShaper'
objList = []

cgmMeta.cgmNode(name = 'test',nodeType='transform')
i_obj = cgmMeta.cgmNode(obj)
i_obj.getPosition(True)
i_obj.mNode
i_obj.isComponent()
i_obj.doName(sceneUnique=True,nameChildren=True,fastIterate = False)
i_obj.doName()
nameF.returnUniqueGeneratedName(i_obj.mNode,sceneUnique = True,fastIterate=True)

