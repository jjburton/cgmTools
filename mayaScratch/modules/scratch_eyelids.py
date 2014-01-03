import cgm.core
cgm.core._reload()
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
from cgm.core.rigger import RigFactory as Rig
from cgm.core import cgm_General as cgmGeneral
reload(Rig)
#======================================================================
cgmMeta.log.setLevel(cgmMeta.logging.INFO)
cgmMeta.log.setLevel(cgmMeta.logging.DEBUG)
mFactory.log.setLevel(mFactory.logging.INFO)
mFactory.log.setLevel(mFactory.logging.DEBUG)
m1.modulePuppet.__verify__()
m1.getState()
@cgmGeneral.Timer

m1 = cgmPM.cgmModule('l_eyelids_part')
m1.getNameAlias()
m1.get_allModuleChildren()
m1.isSized()
m1.doTemplate()
m1.isTemplated()
m1.doSkeletonize()
m1.__verify__()

m1.modulePuppet._verifyMasterControl()
m1.helper.__storeNames__()

i_rig.buildModule.__build__(i_rig)
m1.rigConnect()
m1.rig_getReport()
i_rig = Rig.go(m1,forceNew=False,autoBuild = False)#call to do general rig

i_rig = Rig.go(m1,forceNew=False)#call to do general rig
m1.templateNull.handles

rUtils.createEyeballRig('l_eye_rigHelper',aimTargetObject = 'l_eye_ik_anim', buildIK=True)

i_rig.build(i_rig,buildTo = 'controls')
i_rig.buildModule.build_rigSkeleton(i_rig)
i_rig.buildModule.build_shapes(i_rig)
i_rig.buildModule.build_controls(i_rig)
i_rig.buildModule.build_FKIK(i_rig)
i_rig.buildModule.build_deformation(i_rig)
i_rig.buildModule.build_rig(i_rig)
i_rig.buildModule.__build__(i_rig)
from cgm.lib import distance
l_constrainTargetJoints = [u'l_left_index_1_blend_jnt', u'l_left_index_2_blend_jnt', u'l_left_index_3_blend_jnt', u'l_left_index_4_blend_jnt', u'l_left_index_5_blend_jnt']
distance.returnClosestObject('l_left_index_1_rig_jnt',l_constrainTargetJoints)
m1.rigNull.getMessage('blendJoints',False)
m1.moduleParent.rigNull.rigJoints[-1]
i_rig.buildModule.build_matchSystem(i_rig)
reload(Rig)
from cgm.lib import cgmMath
cgmMath.isFloatEquivalent(0.002,0,2)
rUtils.matchValue_iterator(drivenAttr='l_left_index_2_ik_jnt.rz',driverAttr='left_index_noFlip_ikH.twist',minIn = -179, maxIn = 179, maxIterations = 5,matchValue=0)
cgmMeta.cgmObject('l_ankle_ik_anim').scalePivotY = 0
i_rig._i_deformNull.controlsIK

ml_ikJoints = m1.rigNull.ikJoints
ml_fkJoints = m1.rigNull.fkJoints
ml_blendJoints = m1.rigNull.blendJoints
mi_settings = m1.rigNull.settings

#Queries	
m1.isSized()
m1.setState('skeleton',forceNew=True)
m1.skeletonDelete()
m1.doRig()

#>>> Need to figure out a eyelid follow =============================================================================
from cgm.core.classes import NodeFactory as NodeF
"""
need some attributes
max rotUp
min rotUp
max rotOut
max rotOut
driver rotup
driver rotout
"""
mc.createNode('clamp')
mi_remapUp.select()
mi_resultLoc = cgmMeta.cgmObject('worldCenter_loc')
mi_clampUpr = cgmMeta.cgmNode('clamp1')
mi_controlObject = mi_resultLoc
orientation = 'zyx'
d_settings = {'upr':{''}}
mPlug_autoFollow = cgmMeta.cgmAttr("l_upr_lid_main_anim","autoFollow",attrType = 'float', value = 1.0, hidden = False,keyable=True,maxValue=1.0,minValue=0)

#Upr lid up
mPlug_driverUp = cgmMeta.cgmAttr('l_eye_blend_loc',"r%s"%orientation[2])
mPlug_uprUpLimit = cgmMeta.cgmAttr(mi_controlObject,"uprUpLimit",attrType='float',value=-60,keyable=False,hidden=False)
mPlug_uprDnLimit = cgmMeta.cgmAttr(mi_controlObject,"uprDnLimit",attrType='float',value=50,keyable=False,hidden=False)
mPlug_driverUp.doConnectOut("%s.inputR"%mi_clampUpr.mNode)
mPlug_uprDnLimit.doConnectOut("%s.maxR"%mi_clampUpr.mNode)
mPlug_uprUpLimit.doConnectOut("%s.minR"%mi_clampUpr.mNode)
mc.connectAttr("%s.outputR"%mi_clampUpr.mNode,"%s.r%s"%(mi_resultLoc.mNode,orientation[2]))

#Upr Lid side
mPlug_driverSide = cgmMeta.cgmAttr('l_eye_blend_loc',"r%s"%orientation[1])
mPlug_leftLimit = cgmMeta.cgmAttr(mi_controlObject,"uprLeftLimit",value=15,attrType='float',keyable=False,hidden=False)
mPlug_rightLimit = cgmMeta.cgmAttr(mi_controlObject,"uprRightLimit",value=-15,attrType='float',keyable=False,hidden=False)
mPlug_driverSide.doConnectOut("%s.inputG"%mi_clampUpr.mNode)
mPlug_leftLimit.doConnectOut("%s.maxG"%mi_clampUpr.mNode)
mPlug_rightLimit.doConnectOut("%s.minG"%mi_clampUpr.mNode)
mc.connectAttr("%s.outputG"%mi_clampUpr.mNode,"%s.r%s"%(mi_resultLoc.mNode,orientation[1]))
from cgm.lib import attributes
#Lwr lid
"""
Need
Only want a value greater than the lwrDnStart should start to push things down
"""
mc.createNode('clamp')
mc.createNode('setRange')
mc.createNode('remapValue')
mi_clampLwr = cgmMeta.cgmNode('clamp2')
mi_remapLwr = cgmMeta.cgmNode('remapValue1')
mi_remapLwr.outValue
mi_lwrResultLoc = cgmMeta.cgmObject('lwrLid_result')
mi_controlObject = mi_lwrResultLoc
mPlug_lwrUpLimit = cgmMeta.cgmAttr(mi_controlObject,"lwrUpLimit",attrType='float',value=-26,keyable=False,hidden=False)
mPlug_lwrDnLimit = cgmMeta.cgmAttr(mi_controlObject,"lwrDnLimit",attrType='float',value=35,keyable=False,hidden=False)
mPlug_lwrDnStart = cgmMeta.cgmAttr(mi_controlObject,"lwrDnStart",attrType='float',value=5,keyable=False,hidden=False)
mPlug_driverUp.doConnectOut("%s.inputValue"%mi_remapLwr.mNode)
mPlug_lwrDnStart.doConnectOut("%s.inputMin"%mi_remapLwr.mNode)
mi_remapLwr.inputLimit = 50
mPlug_lwrDnLimit.doConnectOut("%s.outputLimit"%mi_remapLwr.mNode)
attributes.doConnectAttr("%s.outValue"%mi_remapLwr.mNode,"%s.r%s"%(mi_lwrResultLoc.mNode,orientation[2]))

mPlug_driverUp.doConnectOut("%s.inputR"%mi_clampLwr.mNode)
mPlug_lwrDnLimit.doConnectOut("%s.maxR"%mi_clampLwr.mNode)
mPlug_lwrUpLimit.doConnectOut("%s.minR"%mi_clampLwr.mNode)
mc.connectAttr("%s.outputR"%mi_clampLwr.mNode,"%s.r%s"%(mi_lwrResultLoc.mNode,orientation[2]))

mc.connectAttr("%s.outputG"%mi_clampUpr.mNode,"%s.r%s"%(mi_lwrResultLoc.mNode,orientation[1]))
