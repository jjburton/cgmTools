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



#>>> Dynamic group
#=======================================================
parents = mc.ls(sl=True)
dParents = [u'parent1', u'parent2', u'parent3']
mode = 'space'
a = cgmMeta.cgmDynParentGroup(dynChild = 'dynChild',dynParents = dParents)
#Hips
dynParents = [ u'cog_anim',u'worldCenter_loc']#hips
dynGroup = 'hips_anim_grp'
dynChild = 'hips_anim'

a = cgmMeta.cgmDynParentGroup(dynChild = dynChild,dynParents = dynParents, dynGroup = dynGroup,dynMode = dynMode)
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