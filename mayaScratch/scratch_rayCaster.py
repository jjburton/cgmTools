import cgm.core
cgm.core._reload()
import maya.cmds as mc

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta

from cgm.lib import locators
from cgm.lib import distance
reload(distance)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

#>>> Distance
#=======================================================
i_obj = cgmMeta.cgmObject(mc.ls(sl=True)[0])
i_obj.getPosition()
mesh = 'Morphy_Body_GEO'
info = distance.findMeshIntersection(mesh,i_obj.getPosition(), vector)
vector = [matrix[9],matrix[10],matrix[11]]
vector = [matrix[8],matrix[9],matrix[10]]#Z
vector = [-matrix[8],-matrix[9],-matrix[10]]#Z

locators.doLocPos(info['hit'])

matrix = mc.xform(i_obj.mNode, q=True,  matrix=True, worldSpace=True)
matrix
len(matrix)
