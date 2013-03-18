
from cgm.core import cgm_Meta as cgmMeta
reload(cgmMeta)

import Red9.core.Red9_Meta as r9Meta
reload(r9Meta)

from cgm.lib.classes import NameFactory as nameF
reload(nameF)

import cgm.core
cgm.core._reload()

from cgm.lib import locators
reload(locators)

obj = mc.ls(sl=True)[0] or False
obj = 'Morphy_Body_GEO.f[1648]'
obj = 'pelvis_bodyShaper'
objList = []

cgmMeta.cgmNode(name = 'test',nodeType='transform')
i_obj.getPosition(True)

i_obj = cgmMeta.cgmNode(obj)
i_obj = cgmMeta.cgmNode(mc.ls(sl=True)[0])
i_obj.mNode
i_obj.getSiblings()
i_obj.doName()

i_obj.getComponents('cv')
i_obj.doLoc()

i_obj.mNode
i_obj.isComponent()
i_obj.doName(sceneUnique=True,nameChildren=True,fastIterate = False)
i_obj.doName()
nameF.returnUniqueGeneratedName(i_obj.mNode,sceneUnique = True,fastIterate=True)

ObjectSet = cgmMeta.cgmMetaFactory(name = 'test',nodeType = 'network')
cgmMeta.cgmObjectSet(name = 'cgmObjectAnimationSet',setType = 'animation', qssState = True)
cgmMeta.cgmObjectSet(name = 'cgmObjectAnimationSet',qssState = True)
cgmMeta.cgmObjectSet(name = 'cgmObjectAnimationSet',setType = 'animation')
a = cgmMeta.cgmObjectSet(name = 'cgmObjectAnimationSet',qssState = True)
a.objectSetType = 'animation'
a.doName()
mc.ls('cgmObjectSet_animSet')
cgmMeta.cgmBufferNode(name = 'testBuffer')


cgm.core._reload()
cgmMeta.cgmBufferNode(name = 'testBuffer')
i_n = cgmMeta.cgmMetaFactory(name = 'cgmNode',nodeType = 'network').doName()
i_n.doName()
i_obj = cgmMeta.cgmNode(mc.ls(sl=True)[0])
i_obj.doName()

