import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from Red9.core import Red9_General as r9General
reload(cgmRigMeta)
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()
reload(cgm.core)
reload(cgmMeta)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
orientation = ['xyz']
orientation[1]

#>>>cgmControl
obj = 'hips_controlCurve'
i_c = cgmMeta.asMeta(obj,'cgmControl',setClass=True)

cgmRigMeta.log.setLevel(cgmRigMeta.logging.INFO)
cgmRigMeta.log.setLevel(cgmRigMeta.logging.DEBUG)

#>>> Dynamic Switch
#=======================================================
a = cgmRigMeta.cgmDynamicSwitch(name='test')
a = cgmRigMeta.cgmDynamicSwitch(dynOwner = 'l_leg_rigNull')
a=cgmRigMeta.cgmDynamicSwitch('l_leg_rigNull_dynSwitchSystem')
a=cgmRigMeta.cgmDynamicSwitch('l_leg_rigNull_dynSwitchSystem')
a.addSwitch('FKtoIK',['left_leg_settings_anim','blend_FKIK'],1,['l_l_ankle_ik_anim_dynMatchDriver','l_l_knee_ik_anim_dynMatchDriver'])
a.addSwitch('IKtoFK',['left_leg_settings_anim','blend_FKIK'],0,['l_l_hip_fk_anim_dynMatchDriver','l_l_knee_fk_anim_dynMatchDriver','l_l_ankle_fk_anim_dynMatchDriver','l_l_ball_fk_anim_dynMatchDriver'])

a.setSwitchAttr(['left_leg_settings_anim','blend_FKIK'])
a.setSwitchAttr(['left_leg_settings_anim','asfasdf'])
a.setDynOwner('asdaf')
a.addSwitch('FKtoIK',['left_leg_settings_anim','blend_FKIK'],1,['l_l_hip_fk_anim_dynMatchDriver'])
a.getMessage('dynSwitchAttr')
a=cgmRigMeta.cgmDynamicSwitch('test_dynSwitchSystem')
a.go(1)

#>>> Dynamic Match
#=======================================================
b = cgmRigMeta.cgmDynamicMatch('l_ankle_ik_anim_dynMatchDriver')
b.doMatch()

dynObject = 'nurbsSphere1'
dynMatchTargets =  [u'pCube1', u'pCube2']
dynSnapTargets = ['worldCenter_loc']
dynNull = 'nurbsSphere1_dynMatchDriver'

dynObject = 'drivenJoint'
drivenObject = 'matchJoint'
matchObject = 'matchJoint_loc'
matchTarget = 'matchJoint_loc'

a = cgmRigMeta.cgmDynamicMatch(dynObject=dynObject)
a.addDynIterTarget(drivenObject = drivenObject, matchObject = matchObject, driverAttr = 'rz', maxValue = None, minValue = None, maxIter = 50, iterIndex = None)

a.addDynIterTarget(drivenObject = drivenObject, matchTarget = matchObject, driverAttr = 'rz', maxValue = None, minValue = None, iterations = 50, iterIndex = None)
a.doIter()

a = cgmRigMeta.cgmDynamicMatch(dynObject=dynObject,dynMatchTargets = dynMatchTargets)
a = cgmRigMeta.cgmDynamicMatch(dynObject=dynObject,dynNull = dynNull)

a = cgmRigMeta.cgmDynamicMatch(dynObject=dynObject,dynMatchTargets = dynMatchTargets, dynSnapTargets = dynSnapTargets, dynPrefix = 'fkik')
a = cgmRigMeta.cgmDynamicMatch(dynObject=dynObject,dynNull = dynNull,dynSuffix = 'fkik')
a.msgList_getMessage('dynDrivers',False)
a.msgList_getMessage('dynMatchTargets',False)
a.msgList_getMessage('dynSnapTargets',False)

a.doMatch(1)
a.doMatch(0)
cgmMeta.cgmNode('nurbsSphere1').dynMatchDriver_fkik.doMatch(0)
cgmMeta.cgmNode('nurbsSphere1').dynMatchDriver_fkik.doMatch(1)
a.dynDrivers[0].dynMatchAttrs = ['translate','rotate','scale']
cgmMeta.cgmNode('nurbsSphere1').fkik_dynMatchDriver.doMatch(match = 0)
cgmMeta.cgmNode('nurbsSphere1').fkik_dynMatchDriver.doMatch(match = 1)
cgmMeta.cgmNode('nurbsSphere1').fkik_dynMatchDriver.doSnap(0)
cgmMeta.cgmNode('nurbsSphere1').fkik_dynMatchDriver.doSnap(1)

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