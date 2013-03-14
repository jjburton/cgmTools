import cgm.core
cgm.core._reload()
import maya.cmds as mc

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta

from cgm.lib import locators
from cgm.lib import distance
reload(distance)
from cgm.core.lib import rayCaster as RayCast
reload(RayCast)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

#>>> Distance
#=======================================================
i_obj = cgmMeta.cgmObject(mc.ls(sl=True)[0])
i_obj.getPosition()
mesh = 'Morphy_Body_GEO'
RayCast.findMeshIntersectionFromObjectAxis(mesh,i_obj.mNode)
info = RayCast.findMeshIntersectionFromObjectAxis(mesh,i_obj.mNode,vector = [0,-1,0])
log.info(info)
info = distance.findMeshIntersection(mesh,i_obj.getPosition(), vector)
vector = [matrix[9],matrix[10],matrix[11]]
vector = [matrix[8],matrix[9],matrix[10]]#Z
vector = [-matrix[8],-matrix[9],-matrix[10]]#Z
RayCast.findMeshIntersectionFromObjectAxis(mesh,i_obj.mNode,axis = 'z-')
locators.doLocPos(info['hit'])
for axis in ['x+','x-','z+','z-']:
    locators.doLocPos(RayCast.findMeshIntersectionFromObjectAxis(mesh,i_obj.mNode,axis = axis)['hit'])

matrix = mc.xform(i_obj.mNode, q=True,  matrix=True, worldSpace=True)
matrix
len(matrix)
