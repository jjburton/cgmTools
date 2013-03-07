import cgm.core
cgm.core._reload()
import maya.cmds as mc

import Red9.core.Red9_Meta as r9Meta
reload(r9Meta)

from cgm.core.classes import SnapFactory as Snap
reload(Snap)
from cgm.core import cgm_Meta as cgmMeta
reload(cgmMeta)
obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

#>>> Modules
#=======================================================
i_obj = cgmMeta.cgmObject(mc.spaceLocator()[0])
i_obj.mNode
i_obj.isTransform()
Snap.go(i_obj)
Snap.go(i_obj.mNode,targets = 'Morphy_Body_GEO.vtx[2072]')
q_object = 'Morphy_Body_GEO.vtx[2072]'
q_object = 'locator1'
q_object = 'r_arm_bodyShaper_shape1.cv[6]'
mc.ls(i_obj.mNode,type = 'transform',long = True)
mc.ls('Morphy_Body_GEO.vtx[2072]',type = 'transform',long = True)
a = cgmMeta.cgmNode(q_object)
a.getComponent()
mc.select('%s.%s'%(a.mNode,a.__component__))
a.getShortName()
cgmMeta.cgmNode(i_obj.mNode)

from cgm.lib import search
search.returnObjectType('')
l_componentTypes = ['polyVertex','curveCV','surfaceCV','polyEdge','editPoint','isoparm','polyFace','polyUV','curvePoint','surfacePatch','nurbsUV']
q_object.split('.')[-1]
