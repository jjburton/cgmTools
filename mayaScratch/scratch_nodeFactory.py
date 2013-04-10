from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()
import maya.cmds as mc

from cgm.lib import locators
from cgm.lib import distance
reload(distance)
from cgm.core.classes import NodeFactory as nFactory
reload(nFactory)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
objList = mc.ls(sl=True)
cgmMeta.cgmObject(obj).createTransformFromObj()
#>>> 
#=======================================================

#>>> single blend
#=======================================================
driver = 'null1.FKIK'
result1 = 'null1.resultFK'
result2 = 'null1.resultIK'
nFactory.createSingleBlendNetwork(driver, result1, result2,keyable=True)