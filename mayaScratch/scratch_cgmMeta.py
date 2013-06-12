import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()

reload(cgmMeta)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
orientation = ['xyz']
orientation[1]

#>>>cgmControl
obj = 'hips_controlCurve'
i_c = cgmMeta.cgmControl(obj,setClass=True)

#>>> Dynamic Match
dynObject = 'nurbsSphere1'
dynMatchTargets =  [u'pCube1', u'pCube2']
dynSnapTargets = ['worldCenter_loc']
dynNull = 'nurbsSphere1_dynMatchDriver'
a = cgmMeta.cgmDynamicMatch(dynObject=dynObject,dynMatchTargets = dynMatchTargets)
a = cgmMeta.cgmDynamicMatch(dynObject=dynObject,dynNull = dynNull)

a = cgmMeta.cgmDynamicMatch(dynObject=dynObject,dynMatchTargets = dynMatchTargets, dynSnapTargets = dynSnapTargets, dynPrefix = 'fkik')
a = cgmMeta.cgmDynamicMatch(dynObject=dynObject,dynNull = dynNull,dynSuffix = 'fkik')
a.getMessage('dynDrivers',False)
a.getMessage('dynTargets',False)
a.doMatch(1)
a.doMatch(0)
cgmMeta.cgmNode('nurbsSphere1').dynMatchDriver_fkik.doMatch(0)
cgmMeta.cgmNode('nurbsSphere1').dynMatchDriver_fkik.doMatch(1)

#>>> Dynamic group
#=======================================================
parents = mc.ls(sl=True)
dParents = [u'parent1', u'parent2', u'parent3']
dynMode = 'follow'
a = cgmRigMeta.cgmDynParentGroup(dynChild = 'dynChild',dynParents = dParents,dynMode = dynMode)
a.rebuild()
#Hips
dynParents = [ u'cog_anim',u'worldCenter_loc']#hips
dynGroup = 'hips_anim_grp'
dynChild = 'dynChild'

a = cgmRigMeta.cgmDynParentGroup(dynChild = dynChild,dynParents = dynParents, dynGroup = dynGroup,dynMode = dynMode)
#Shoulders
c1 = r9Meta.MetaClass('shoulders_ik_anim')
c1.dynParentGroup
c1.dynParentGroup.dynChild
c1.dynParentGroup.addDynChild('shoulders_ik_anim')
c1.dynParentGroup.rebuild()

dynParents = ['spine_2_fk_anim','cog_anim','|Morphy|Morphy_1_masterAnim','shoulders_ik_anim_spacePivot_anim','shoulders_ik_anim_spacePivot_1_anim']
for o in dynParents:
    c1.dynParentGroup.addDynParent(o)
c1.dynParentGroup.rebuild()


spineFK,cog,world,pivots
dynParents = [ u'spine_2_fk_anim',u'cog_anim',u'worldCenter_loc','pivotAnim']#Shoulderes
dynParents = [ u'spine_2_fk_anim',u'cog_anim',u'worldCenter_loc']#Shoulderes
dynParents = [ u'spine_2_fk_anim',u'cog_anim','hips_anim',u'worldCenter_loc']#Shoulderes
dynGroup = 'shoulders_ik_anim_grp'
dynChild = 'shoulders_ik_anim'
dynMode = 'follow'