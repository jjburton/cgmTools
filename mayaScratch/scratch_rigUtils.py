from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()
import maya.cmds as mc
from cgm.lib import curves
from cgm.lib import locators
from cgm.lib import distance
from cgm.lib import joints
reload(distance)
from cgm.core.rigger.lib import rig_Utils as rUtils
from cgm.core.rigger.lib import joint_Utils as jUtils
for i_jnt in cgmMeta.validateObjListArg(mc.ls(sl=True),cgmMeta.cgmObject,mayaType = 'joint'):
    jUtils.metaFreezeJointOrientation(i_jnt)
                               
reload(rUtils)
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
objList = mc.ls(sl=True)
cgmMeta.cgmObject(obj).createTransformFromObj()


#>>> connect_singleDriverAttrToMulti
#=======================================================
reload(rUtils)
drivenAttr = 'noseBase_bodyShaper_parentConstraint_grp.scale'
driverAttrs = ['lwrFace_bodyShaper.sx','mouth_bodyShaper.sx']

drivenAttr = 'l_eyeOrb_bodyShaper_scale_parentConstraint_grp.scale'
driverAttrs = 'cranium_bodyShaper.sx'
driverAttrs = ['cranium_bodyShaper.sx']
rUtils.connect_singleDriverAttrToMulti(drivenAttr ,driverAttrs)


#>>> Stretch IK
#=======================================================
jointList = mc.ls(sl=True)
joints.orientJointChain(jointList,'zyx','zdown')
rUtils.IKHandle_create(jointList[0],jointList[-1],lockMid=False, nameSuffix = 'noFlip',rpHandle=True,controlObject='joint3_loc',addLengthMulti=True,globalScaleAttr='null1.sy', stretch='translate')
   






rUtils.createCGMSegment(jointList)


start = 'l_left_index_2_ik_jnt'
end = 'l_left_index_4_ik_jnt'
mc.ikHandle( sj=start, ee=end,solver = 'ikSpringSolver', forceSolver = True,snapHandleFlagToggle=True )  

rUtils.IKHandle_addSplineIKTwist(handle,True)
rUtils.IKHandle_addSplineIKTwist(handle,False)

#>>> Playing with spline Ik twist setup
#=======================================================
#root twist mode off
#Playing with a better spline IK twist setup, ramp multiplier works
handle = 'ikHandle1'
mPlug_start = cgmMeta.cgmAttr(handle,'twistStart',attrType='float',keyable=True, hidden=False)
mPlug_end = cgmMeta.cgmAttr(handle,'twistEnd',attrType='float',keyable=True, hidden=False)
mPlug_equalizedRoll = cgmMeta.cgmAttr(handle,'twistEqualized',attrType='float',keyable=True, hidden=False)
mPlug_twist = cgmMeta.cgmAttr(handle,'twist',attrType='float',keyable=True, hidden=False)
mPlug_start.doConnectOut("%s.roll"%handle)

arg1 = "%s = %s - %s"%(mPlug_equalizedRoll.p_combinedShortName,mPlug_start.p_combinedShortName,mPlug_end.p_combinedShortName)
log.info("arg1: %s"%arg1)
NodeF.argsToNodes(arg1).doBuild()

arg2 = "%s =  %s - %s"%(mPlug_twist.p_combinedShortName,mPlug_end.p_combinedShortName,mPlug_equalizedRoll.p_combinedShortName)
log.info("arg2: %s"%arg2)
NodeF.argsToNodes(arg2).doBuild()

mPlug_twistRampMultiplier = cgmMeta.cgmAttr(handle,'twistRampMultiplier',attrType='float',keyable=True, hidden=False)
mPlug_twistRampMultiplier.doConnectOut("%s.dTwistRampMult"%handle)
#>>>Iterator
#=======================================================
#Value match mode
rUtils.matchValue_iterator(targetAttr = 'l_hip_ik_jnt.rz' , driverAttr = 'ikChain_ikH.twist', matchValue = 0)

rUtils.matchValue_iterator(drivenAttr = 'l_knee_ik_jnt.tz' , driverAttr = 'l_ankle_ik_anim.lengthUpr', maxIterations=2,matchValue = 66.991, minIn=0.1,maxIn=30.0)

#>>>ikHandle
#=======================================================
"""
reload(rUtils)
mc.ls(sl=True)
handles = [u'l_hip', u'l_knee', u'l_ankle']
rUtils.create_IKHandle(start,end,handles = ['l_knee_ik_jnt_loc'],stretch = 'translate')
rUtils.create_IKHandle(start,end,handles = handles,stretch = 'translate')

rUtils.create_distanceMeasure('l_knee_ik_jnt_loc','nurbsSphere1')
"""
start = 'l_hip_ik_jnt'
end = 'l_ankle_ik_jnt'
rUtils.IKHandle_create(start,end,stretch = 'translate')
rUtils.IKHandle_fixTwist('ikChain_ikH')
rUtils.IKHandle_fixTwist('ikHandle2')
rUtils.IKHandle_fixTwist('left_pinky_noFlip_ikH')

#>>>Connect joint length
#=======================================================
joint = 'l_hip_fk_jnt'
control = 'l_hip_loliHandle.length'
rUtils.addJointLengthAttr(joint,control)

#>>>Connect blend chain
#=======================================================
chain1 = mc.ls(sl=True)
chain2 = mc.ls(sl=True)
blendChain = mc.ls(sl=True)
rUtils.connectBlendJointChain(chain1,chain2,blendChain)

#>>>Trace curve
#=======================================================
start = 'hips_anim'
end = 'hips_anim_spacePivot_1_anim'
rUtils.create_traceCurve(start,end)

#>>>space Pivot
#=======================================================
str_control = 'neck_2_loliHandle'
rUtils.create_spaceLocatorForObject(str_control)


#>>> Middle constraint obj
#=======================================================
i_obj = cgmMeta.cgmObject('driverMid')
#Create a dup constraint curve

r9Meta.isMetaNodeInherited(i_obj,'cgmObject')
r9Meta.isMetaNode(i_obj,'cgmObject')

#segment curve creation
#=================================================================
jointList = mc.ls(sl=True)

reload(rUtils)
rUtils.createSegmentCurve(jointList,secondaryAxis='zdown')

scaleBuffer = 'test_distanceBuffer'
rUtils.addSquashAndStretchToControlSurfaceSetup(scaleBuffer, jointList ,moduleInstance=False,connectBy='translate')

#Mid group sguff
#=================================================================
segmentCurve = 'testSegment_splineIKCurve'
joints = 'driverMid'
joints = 'l_hip_mid_0_influence_jnt'
baseParent = 'l_hip_influence_jnt'
endParent = 'l_knee_influence_jnt'
midControls = 'l_hip_mid_0_ik_anim'
controlOrientation = 'zyx'

baseParent = 'driverBase'
endParent = 'driverTop'
midControls = ['mid_crv']
controlOrientation = 'yxz'
controlOrientation = 'yzx'
rUtils.addCGMSegmentSubControl(joints,segmentCurve,baseParent, endParent,midControls=midControls,controlOrientation=controlOrientation)

rUtils.addCGMSegmentSubControl('spine_2_influenceJoint',
                               segmentCurve = 'spine_splineIKCurve',
                               baseParent='spine_1_influenceJoint',
                               endParent='sternum_influenceJoint',
                               midControls='spine_2_ik_anim',
                               baseName='torso',
                               orientation='zyx')
rUtils.addCGMSegmentSubControl('spine_2_influenceJoint', segmentCurve = 'spine_splineIKCurve',baseParent='spine_1_influenceJoint',endParent='sternum_influenceJoint',midControls='spine_2_ik_anim',baseName='torso',orientation='zyx')


#Build segment stuff
#==================================================================
from cgm.core.rigger.lib import rig_Utils as rUtils
reload(rUtils)
"""
testSegment_splineIKCurve.scaleEndUp = -1*(1-top_crv.scaleZ);
testSegment_splineIKCurve.scaleEndOut = -1*(1-top_crv.scaleX);
"""
jointList = [u'joint1', u'joint2', u'joint3', u'joint4', u'joint5', u'joint6']
jointList = [u'joint1', u'joint2', u'joint3', u'joint4', u'joint5']
jointList = mc.ls(sl=True)
influenceJoints = ['driverBase','driverTop']
influenceJoints = ['l_knee_influence_jnt','l_ankle_influence_jnt']

influenceJoints = mc.ls
startControl = 'base_crv'
endControl = 'top_crv'
controlOrientation = 'yzx'
startControl = 'driverBase'
endControl = 'driverTop'
influenceJoints = ['l_seg_0_hip_influence_jnt','l_seg_0_knee_influence_jnt']
startControl = 'l_seg_0_hip_ik_anim'
endControl = 'l_seg_0_knee_ik_anim'
startControl = 'l_knee_segIKCurve'
endControl = 'l_ankle_segIKCurve'
controlOrientation = 'zyx'
controlOrientation = 'zxy'

influenceJoints = ['l_seg_1_knee_influence_jnt','l_seg_1_ankle_influence_jnt']
startControl = 'l_seg_0_hip_ik_anim'
endControl = 'l_seg_0_knee_ik_anim'
startControl = 'l_seg_1_knee_ik_anim'
endControl = 'l_seg_1_ankle_ik_anim'
controlOrientation = 'zyx'
t = rUtils.createCGMSegment(jointList,influenceJoints=influenceJoints, startControl=startControl,endControl=endControl,secondaryAxis = 'zup',controlOrientation=controlOrientation,additiveScaleSetup=True,connectAdditiveScale=True)
reload(rUtils)
startControl = 'l_seg_0_hip_ik_anim'
endControl = 'l_seg_0_knee_ik_anim'
startControl = 'l_seg_1_knee_ik_anim'
endControl = 'l_seg_1_ankle_ik_anim'
controlOrientation = 'zyx'

influenceJoints = ['influnece1','influnece2']
startControl = 'influnece1'
endControl = 'influnece2'
#Squashrework
#=================================================
scaleBuffer = 'testSegment_distanceBuffer'

rUtils.addSquashAndStretchToControlSurfaceSetup(scaleBuffer, jointList ,moduleInstance=False)

def doMid(jnt='driverMid',curve = 'testSegment_splineIKCurve',influenceJnts = ['driverBase','driverTop']):
    i_obj = cgmMeta.cgmObject(jnt)
    mi_splineCurve = cgmMeta.cgmObject(curve)
    ml_influenceJoints = [cgmMeta.cgmObject(obj) for obj in influenceJnts]
    i_controlSurfaceCluster = cgmMeta.cgmNode('testSegment_segmentCurve_skinNode')
    
    #Create ConstraintCurves
    i_constraintSplineCurve = mi_splineCurve.doDuplicate(po = False,ic=False)
    i_constraintSplineCurve.addAttr('cgmTypeModifier','constraintSpline')
    i_constraintSplineCurve.doName()
    
    l_pos = [i_jnt.getPosition() for i_jnt in ml_influenceJoints]#<<<<<<<<<<<<<<<<
    i_constraintLinearCurve = cgmMeta.cgmObject(mc.curve (d=1, ep = l_pos, os=True))
    i_constraintLinearCurve.addAttr('cgmTypeModifier','constraintLinear')
    i_constraintLinearCurve.doName()    
    
    #Skin it
    i_constraintCurve = cgmMeta.cgmNode(mc.skinCluster ([i_jnt.mNode for i_jnt in ml_influenceJoints],
                                                                i_constraintSplineCurve.mNode,
                                                                tsb=True,
                                                                maximumInfluences = 3,
                                                                normalizeWeights = 1,dropoffRate=2.5)[0])
    
    i_constraintCurve.doStore('cgmName', "%s.cgmName"%mi_splineCurve.mNode)
    i_constraintCurve.addAttr('cgmTypeModifier','constraint', lock=True)
    i_constraintCurve.doName()
    
    i_constLinearCurveCluster = cgmMeta.cgmNode(mc.skinCluster ([i_jnt.mNode for i_jnt in ml_influenceJoints],
                                                                i_constraintLinearCurve.mNode,
                                                                tsb=True,
                                                                maximumInfluences = 3,
                                                                normalizeWeights = 1,dropoffRate=2.5)[0])
    

    ml_pointOnCurveInfos = []
    splineShape = mc.listRelatives(i_constraintSplineCurve.mNode,shapes=True)[0]
    
    for i_obj in [i_obj]:
        #Create group
        grp = i_obj.doGroup()
        i_followGroup = cgmMeta.asMeta(grp,'cgmObject',setClass=True)
	
	#>>>Transforms 
	#=============================================================	
	#>>>PointTargets
	#linear follow
	i_linearFollowNull = i_obj.duplicateTransform()
	i_linearFollowNull.addAttr('cgmType','linearFollow',attrType='string',lock=True)
	i_linearFollowNull.doName()
	#i_linearFollowNull.parent = i_anchorStart.mNode     
	
	#splineFollow
	i_splineFollowNull = i_obj.duplicateTransform()
	i_splineFollowNull.addAttr('cgmType','splineFollow',attrType='string',lock=True)
	i_splineFollowNull.doName()	
	
	#>>>Attach 
	#=============================================================
        #>>>Spline
        l_closestInfo = distance.returnNearestPointOnCurveInfo(i_obj.mNode,i_constraintSplineCurve.mNode)
	i_closestSplinePointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
        mc.connectAttr ((splineShape+'.worldSpace'),(i_closestSplinePointNode.mNode+'.inputCurve'))	
	
        #> Name
        i_closestSplinePointNode.doStore('cgmName',i_obj)
        i_closestSplinePointNode.doName()
        #>Set attachpoint value
        i_closestSplinePointNode.parameter = l_closestInfo['parameter']
        mc.connectAttr ((i_closestSplinePointNode.mNode+'.position'),(i_splineFollowNull.mNode+'.translate'))
        ml_pointOnCurveInfos.append(i_closestSplinePointNode) 
	
        #>>>Linear
	cBuffer = mc.pointConstraint([ml_influenceJoints[0].mNode,ml_influenceJoints[-1].mNode],
	                              i_linearFollowNull.mNode,
	                              maintainOffset = False, weight = 1)[0]
	
	
	#>>>Constrain 
	#=============================================================	
	cBuffer = mc.pointConstraint([i_linearFollowNull.mNode,i_splineFollowNull.mNode],
	                              i_followGroup.mNode,
	                              maintainOffset = False, weight = 1)[0]
	i_pointConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)	
	
        #Make aim groups since one will be aiming backwards
        #Aim
        #AimBlend        
        #Add mid to original curve cluster        
        mc.skinCluster(i_controlSurfaceCluster.mNode,edit=True,ai=i_obj.mNode,dropoffRate = 2.5)

    
    
#Create group
#i_midInfluenceGroup = 
#Attach
#Make aim groups since one will be aiming backwards
#Aim
#AimBlend

#>>> 
#=======================================================
jointList = mc.ls(sl=True)
joints.orientJointChain(jointList,'zyx','zdown')
rUtils.createCGMSegment(jointList)

rUtils.createSegmentCurve(jointList,secondaryAxis='zdown'moduleInstance=m1,connectBy='scale')
rUtils.createCGMSegment(jointList,influenceJoints = ['driverBase','driverTop'],secondaryAxis = 'zdown')

rUtils.createControlCurveSegment(jointList,secondaryAxis='zdown')
cgmMeta.asMeta('topAim','cgmObject',setClass=True).doDuplicate()
from cgm.lib import distance
reload(distance)
distance.returnNearestPointOnCurveInfo('worldCenter_loc','curve1')
rigUtils.controlCurveTightenEndWeights('test_splineIKCurve','driverBase','driverTop',3)

rigUtils.createControlSurfaceSegment(jointList,secondaryAxis='zdown')
rigUtils.addRibbonTwistToControlSurfaceSetup(jointList,'spine_1_influenceJoint.rotateZ','sternum_influenceJoint.rotateZ')
rigUtils.addSquashAndStretchToControlSurfaceSetup('test_distanceBuffer',jointList,orientation = 'zyx')
rigUtils.addRibbonTwistToControlSurfaceSetup(jointList,['spine_1_influenceJoint','rotateZ'],['sternum_influenceJoint','rotateZ'])
addSquashAndStretchToControlSurfaceSetup(attributeHolder,jointList,orientation = 'zyx', moduleInstance = None):
rigUtils.addRibbonTwistToControlSurfaceSetup(jointList,startControlDriver = ['driverBase','rz'], endControlDriver = ['driverTop','rz'],rotateGroupAxis = 'rotateZ',orientation = 'zyx', moduleInstance = None)
#>>> Smooth skin weights on surface
rigUtils.controlSurfaceSmoothWeights('test_controlSurface',start = 'spine_1_influenceJoint', end = 'sternum_influenceJoint', blendLength = 5)
cgmMeta.cgmObject('test_controlSurface').getComponents('cv')
test = [u'test_controlSurface.cv[0][0]', u'test_controlSurface.cv[0][1]', u'test_controlSurface.cv[0][2]', u'test_controlSurface.cv[0][3]', u'test_controlSurface.cv[0][4]', u'test_controlSurface.cv[0][5]', u'test_controlSurface.cv[0][6]', u'test_controlSurface.cv[1][0]', u'test_controlSurface.cv[1][1]', u'test_controlSurface.cv[1][2]', u'test_controlSurface.cv[1][3]', u'test_controlSurface.cv[1][4]', u'test_controlSurface.cv[1][5]', u'test_controlSurface.cv[1][6]'] # 
cvStarts = [int(obj[-5]) for obj in test]
cvEnds = [int(obj[-2]) for obj in test]
from cgm.lib import lists
cvStarts = lists.returnListNoDuplicates(cvStarts)
cvEnds = lists.returnListNoDuplicates(cvEnds)
log.info(cvStarts)
log.info(cvEnds)



cgmMeta.cgmObject(mc.ls(sl=True)[0],ud = True).compareAttrs(mc.ls(sl=True)[1])
#Can't find difference in to

#Joint attach:
from cgm.lib import joints
reload(joints)
joints.attachJointChainToSurface(jointList,'loftedSurface1','zyx','yup')
joints.loftSurfaceFromJointList(jointList,'x')
                          
#Logic for building ribbon twist setups
log.info(l)
from cgm.lib import lists
lists.returnFactoredConstraintList(objList,3)
l = [1,2,3,4,5]
lists.returnFactoredConstraintList(jointList,3)
lists.returnFactoredConstraintList(l,3)
# __main__ : [[1, 4, 6], [1, 2, 3, 4], [4, 5, 6]] # 
#1==driver
#2>1:1,4
#3>1,4:4
#4>1:6
#5>4:6
#6 == driver
driver1 = ['test','asdf']
assert type(driver1) is list and len(driver1) == 2,"Driver1 wrong: %s"%driver1

[[u'spine_1_surfaceJoint', u'spine_2_surfaceJoint',u'sternum_surfaceJoint'],
 [u'spine_1_surfaceJoint', u'spine_1_1_surfaceJoint', u'spine_2_surfaceJoint'],
 [u'spine_2_surfaceJoint', u'spine_2_1_surfaceJoint', u'sternum_surfaceJoint']] # 

#Working 2 joint split
from cgm.lib import attributes
attributes.doConnectAttr('pelvis_influenceJoint.rotateZ','plusMinusAverage1.input1D[0]')
attributes.doConnectAttr('spine_2_influenceJoint.rotateZ','plusMinusAverage1.input1D[1]')
mc.ls('spine_2_1_surfaceJoint_ikH_poleVectorConstraint1',sn = True)
attributes.doConnectAttr('plusMinusAverage1.output1D','plusMinusAverage2.input1D[0]')
attributes.doConnectAttr('pelvis_influenceJoint.rotateZ','plusMinusAverage2.input1D[1]')

attributes.doConnectAttr('plusMinusAverage1.output1D','plusMinusAverage3.input1D[0]')
attributes.doConnectAttr('spine_2_influenceJoint.rotateZ','plusMinusAverage3.input1D[1]')

attributes.doConnectAttr('plusMinusAverage2.output1D','spine_1_surfaceJoint_rotate_grp.ry')
attributes.doConnectAttr('plusMinusAverage3.output1D','spine_1_1_surfaceJoint_rotate_grp.ry')


attributes.doConnectAttr('plusMinusAverage1.output1D','multiplyDivide1.input1X')
#mode 2
attributes.doSetAttr('multiplyDivide1','input2X',2)
attributes.doSetAttr('multiplyDivide2','input2X',2)


'multiplyDivide1'
#Working through zero equivalency 
'%f'%(-4.11241646134e-07)
round(4.11241646134e-07,1)
round(f1,places)
round(.005,3)
number = .2
number = scientific
number = .000065183
number = 0.0
for n in [1,2,3,4,5,6,7,8,9]:
    log.info(round(number,n))

from cgm.lib import cgmMath
reload(cgmMath)
cgmMath.test_isFloatEquivalent()
cgmMath.isFloatEquivalent(-4.11241646134e-07,0.0)
cgmMath.isFloatEquivalent(0,0.0)
cgmMath.isFloatEquivalent(-4.11241646134e-07,.00001)
round(-0.00000000)
scientific = -4.11241646134e-07
round(scientific)
type(scientific)
mc.xform ('spine_1_1_surfaceJoint', q=True, os=True, ro=True)
assert isFloatEquivalent(-4.11241646134e-07,0.0)
