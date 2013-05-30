import cgm.core
cgm.core._reload()
import maya.cmds as mc

import Red9.core.Red9_Meta as r9Meta
reload(r9Meta)
from cgm.lib import curves
from cgm.core.classes import SnapFactory as Snap
reload(Snap)
from cgm.core import cgm_Meta as cgmMeta
reload(cgmMeta)
obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

#>>>aim
Snap.go(i_obj,target,False,orient = False, aim = True,aimVector=[0,0,-1],upVector=[0,0,-1])
Snap.go(i_obj,target,False,orient = True)

target = mc.ls(sl=True)[0] or []

#>>> Modules
#=======================================================
i_obj = cgmMeta.cgmObject(mc.spaceLocator()[0])
i_obj = cgmMeta.cgmNode(obj)
i_obj = cgmMeta.cgmNode(mc.ls(sl=True)[0])
i_obj.getComponents()
i_obj.getComponent()
a = i_obj
i_obj.mNode
i_obj.isTransform()
Snap.go(i_obj)
mc.xform(q_object, q=True, os=True, t = True)
mc.xform(a.getComponent(), q=True, ws=True, rp=True)
mc.pointPosition(a.getComponent())
cgmMeta.cgmNode(q_object).getPosition(True)
cgmMeta.cgmNode(q_object).getPosition(False)
i_obj = cgmMeta.cgmObject(mc.spaceLocator()[0])
Snap.go('hips_anim_shape1.ep[3]',targets = q_object,orient = False,posOffset=[0,0,2],
        snapToSurface=True,softSelection=True,softSelectDistance=20)
Snap.go(i_obj.getComponent(),targets = q_object,orient = False,posOffset=[0,0,2],
        snapToSurface=True,softSelection=True,softSelectDistance=20)
Snap.go(i_obj.getComponent(),targets = q_object,orient = False,snapToSurface=True,snapComponents=True)
Snap.go(i_obj.mNode,targets = q_object,move = False, orient = True,snapToSurface=True)
Snap.go(i_obj,targets = q_object,orient = False,snapToSurface=True)
Snap.go(i_obj,targets = q_object,snapToSurface=True,posOffset=[0,0,10])
Snap.go(i_obj,targets = q_object,orient = True, snapToSurface=True,posOffset=[0,0,1.5])
Snap.go(i_obj, q_object,snapComponents=True,)

#Mid point snap
Snap.go(i_obj, geo,midSurfacePos=True,axisToDo = ['y','x'])
Snap.go(i_obj, geo,midSurfacePos=True,axisToDo = ['x','y'])

reload(Snap)

q_object = mc.ls(sl=True)[0] or False
q_object = 'Morphy_Body_GEO'
q_object = 'locator1'
q_object = 'Morphy_Body_GEO.e[8198]'
q_object = 'nurbsCircle1.ep[0]'
q_object = 'Morphy_Body_GEO.map[5603]'
q_object = 'Morphy_Body_GEO.f[2015]'
q_object = 'nurbsCircle1.cv[2]'
mc.ls(i_obj.mNode,type = 'transform',long = True)
mc.ls('Morphy_Body_GEO.vtx[2072]',type = 'transform',long = True)
a = cgmMeta.cgmNode(q_object)
a.getComponent()
a.isComponent()
a.getMayaType()
mc.select('%s.%s'%(a.mNode,a.__component__))
a.getShortName()
cgmMeta.cgmNode(i_obj.mNode)

from cgm.lib import search
search.returnObjectType('')
l_componentTypes = ['polyVertex','curveCV','surfaceCV','polyEdge','editPoint','isoparm','polyFace','polyUV','curvePoint','surfacePatch','nurbsUV']
q_object.split('.')[-1]

offset = [0,0,10]
mc.move (offset[0],offset[1],offset[2], [i_obj.mNode], r=True, rpr = True, os = True, wd = True)								

i_root = cgmMeta.cgmObject(curves.createControlCurve('circle',20))

pos = 
mc.move (pos[0],pos[1],pos[2], i_root.mNode, rpr=True)

from cgm.lib import locators
