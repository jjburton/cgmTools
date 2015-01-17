from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
import cgm.core
cgm.core._reload()
import maya.cmds as mc

from cgm.lib import locators
from cgm.lib import distance
reload(distance)
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)
from cgm.lib import cgmMath
reload(cgmMath)
cgmMath.isFloatEquivalent(3,3.0)
obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
objList = mc.ls(sl=True)
cgmMeta.cgmObject(obj).createTransformFromObj()


#>>> connect_controlWiring
#=======================================================
reload(NodeF)
_obj = 'face_attrHolder'

_wiringDict = {'mouth_up':{'driverAttr':'ty'},'mouth_dn':{'driverAttr':'-ty'},'mouth_right':{'driverAttr':'-tx'}}

_wiringDict = {'mouth_up':{'driverAttr':'ty','driverAttr2':'tx','mode':'cornerBlend'}}

NodeF.connect_controlWiring('mouth_anim',_obj,_wiringDict,baseName = 33)

NodeF.connect_controlWiring('upper_lipRoll_anim',_obj,_wiringDict,baseName = 33)


#>>> createAndConnectBlendColors
#=======================================================
NodeF.createAndConnectBlendColors('l_knee_seg_0_jnt_Transform_anchor','l_knee_seg_0_jnt_Transform_aim','l_knee_seg_0_jnt_Transform_attach','l_knee_ik_1_anim.followRoot','rotate')


#>>> single blend
#=======================================================
driver = 'null1.FKIK'
result1 = 'null1.resultFK'
result2 = 'null1.resultIK'
NodeF.createSingleBlendNetwork(driver, result1, result2,keyable=True)


#>>> puppet adding controls
i_node = a.masterControl.controlSettings
str_nodeShort = str(i_node.getShortName())

d_attrKWs = {'skeleton':{'value':0,'defaultValue':0},
             'geo':{'value':1,'defaultValue':1}}

l_buildCatch = []      
i_node = a.masterControl.controlSettings
str_nodeShort = str(i_node.getShortName())
#Skeleton/geo settings
for attr in ['skeleton','geo',]:
    i_node.addAttr(attr,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
    NodeF.argsToNodes("%s.%sVis = if %s.%s > 0"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
    NodeF.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()

#Geotype
i_node.addAttr('geoType',enumName = 'reg:proxy', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
for i,attr in enumerate(['reg','proxy']):
    NodeF.argsToNodes("%s.%sVis = if %s.geoType == %s:1 else 0"%(str_nodeShort,attr,str_nodeShort,i)).doBuild()    

#Divider
i_node.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)

#Part
for part in ['spineRig']:
    i_node.addAttr(part,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
    NodeF.argsToNodes("%s.%sVis = if %s.%s > 0"%(str_nodeShort,part,str_nodeShort,part)).doBuild()
    NodeF.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(str_nodeShort,part,str_nodeShort,part)).doBuild()
                         
                         

i_node.addAttr('________', defaultValue = 2, enumName = 'Parts:Parts',attrType = 'enum',keyable = False,hidden = False,lock=True)

i_node.addAttr('partGuts',enumName = 'proxy:parts:reg', attrType = 'enum',keyable = False,hidden = False)



NodeF.argsToNodes("%s.skeletonVis = if %s.skeleton > 0"%(str_nodeShort,str_nodeShort)).doBuild()
NodeF.argsToNodes("%s.skeletonLock = if %s.skeleton == 2:0 else 2"%(str_nodeShort,str_nodeShort)).doBuild()


'if %s.skeleton == 2:0 else 2; %s.skeletonUnlock'


#>>> validateNodeArg
#=======================================================
reload(NodeF)
"""
valideateNodeArg theory....
need, default types per node type, reult connections per nodeType
arg = validateattr function validateattr = validateAttr
parenthesis
functions = +,-,*,/,<=,>=,>,<,!=,==,av, = 
cond = [if,==,!=,>,<,>=,<=,]
md = [*,/,pow]
pma = [+,-,average]
if attrArg = 1, attrArg = resultAttrArg
if attrArg = 1, attrArg = result1. elif attrArt = 2, result = 
['if', arg,'=',1]
if worldCenter_loc.ty == 1, result = worldCenter_loc.result1
"""
obj = 'worldCenter_loc'
arg = "if worldCenter_loc.ty > 3;worldCenter.condResult1"
arg = "worldCenter_loc.tx + worldCenter_loc.ty + worldCenter_loc.tz = worldCenter.sumResult1"
arg = "if worldCenter_loc.ty > 3;worldCenter_loc.result2"#Working

arg = "if worldCenter_loc.ty == 1, result = %s.result1"%obj
#TODO

arg = "worldCenter_loc.ty = worldCenter_loc.tz "#Working

from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)
a = NodeF.argsToNodes(arg).doBuild()
a = NodeF.argsToNodes(arg)

arg = "worldCenter_loc.sumResult1 = worldCenter_loc.tx + worldCenter_loc.ty + worldCenter_loc.tz"#Working
arg = "worldCenter_loc.simpleSum = 1 + 2 + 3"#Working
arg = "worldCenter_loc.simpleSum = 1 + 2 + 7"#Working
arg = "worldCenter_loc.simpleAv = 1 >< worldCenter_loc.ty  >< 3"#Working
arg = "worldCenter_loc.inverseMultThree = 3 * -worldCenter_loc.ty"#Working
arg = "worldCenter_loc.simpleMathResult = 4 - 2 "#Working
arg = "worldCenter_loc.tz = -worldCenter_loc.ty "#Working
arg = "worldCenter_loc.multResult = worldCenter_loc.ty * 3"#Working
arg = "worldCenter_loc.sumResult = worldCenter_loc.ty + 3 + worldCenter_loc.tx"#Working
arg = "worldCenter_loc.result2 = if worldCenter_loc.ty < 3"#Working
arg = "worldCenter_loc.result23, worldCenter_loc.result2 = if worldCenter_loc.ty < 2:5 "#Working
arg = "worldCenter_loc.directConnect, worldCenter_loc.directConnectY = worldCenter_loc.ty"#Working
arg = "worldCenter_loc.simpleMathResult = 4 - -2 "#Working
arg = "worldCenter_loc.floatMult = 1 * 0.5 "#Working

cgm.core._reload()

#Example
for attr in ['skeleton','geo',]:
    i_node.addAttr(attr,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
    NodeF.argsToNodes("%s.%sVis = if %s.%s > 0"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
    NodeF.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
#Demo
arg = "worldCenter_loc.simpleSum = 1 + 2 + 3"#Working
arg = "worldCenter_loc.simpleAv = 1 >< 2 >< 3"#Working
arg = "worldCenter_loc.inverseTY = -worldCenter_loc.ty"#Working
arg = "worldCenter_loc.result2 = if worldCenter_loc.ty <= 2:5 else 20"#Working
arg = "worldCenter_loc.clampResult = clamp(0, 1, worldCenter_loc.tx)"#working
arg = "worldCenter_loc.setRangeResult = setRange(0,1,1,10,worldCenter_loc.tx)"
arg = "worldCenter_loc.clampResult = clamp(0, 1, worldCenter_loc.tx)"#working
arg = "worldCenter_loc.clamp2Result = clamp(worldCenter_loc.tx, 0, worldCenter_loc.tx)"#working
arg = "worldCenter_loc.clamp1Result = clamp(0, worldCenter_loc.tx, worldCenter_loc.tx)"#working


#Leg test arg
Driven = 'left_leg_settings_anim.result_kneeSpinInfluence'
Driver1 = 'left_leg_seg0_splineIKCurve_to_left_leg_seg0_splineIKCurve_twist_pma_to_left_leg_seg0_splineIKCurve_twist_1_pma.output1D'
Driver2 = 'l_seg_0_hip_mid_0_ik_anim.rotateZ'
mc.objExists(Driver2)
NodeF.argsToNodes("%s = if %s > 1:0 else %s "%(Driven,
                                               Driver1,
                                               Driver2)).doBuild()    
return

#ToDo

from cgm.core.lib import nameTools
reload(nameTools)
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)
NodeF.argsToNodes(arg)
a = NodeF.argsToNodes(arg).doBuild()
for b in a.ml_attrs:
    b.p_combinedName
#TO DO:
#negative number values catch
#sometimes plug connecteor on invers isn't working

mc.ls(a.ml_attrs[0].p_combinedName,sn=True)[0]
NodeF.argsToNodes(arg).d_networksToBuild
NodeF.argsToNodes(arg).d_connectionsToMake
NodeF.argsToNodes(arg)


NodeF.argsToNodes(arg).doBuild()
NodeF.argsToNodes(arg,defaultAttrType='bool',keyable=False, hidden = True, lock = True).buildNodes()

str_pivotName = 'neck_2_ik_1_anim_spacePivot_2_anim'
str_objName = 'neck_2_ik_1_anim'
str_pivotAttr = 'pivot_0'
arg = "%s.overrideVisibility = if %s.%s > 0"%(str_pivotName,str_objName,str_pivotAttr)

       awesomeArgObj_loc
arg = "awesomeArgObj_loc.tx + awesomeArgObj_loc.ty + awesomeArgObj_loc.tz = awesomeArgObj_loc.sumResult1"
"awesomeArgObj_loc.tx + awesomeArgObj_loc.ty + awesomeArgObj_loc.tz = awesomeArgObj_loc.sumResult1",
"1 + 2 + 3 = awesomeArgObj_loc.simpleSum",#Working
"1 >< 2 >< 3 = awesomeArgObj_loc.simpleAv",#Working
"3 * -awesomeArgObj_loc.ty = awesomeArgObj_loc.inverseMultThree",#Working
"4 - 2 = awesomeArgObj_loc.simpleMathResult",#Working
"-awesomeArgObj_loc.ty = awesomeArgObj_loc.ty",#Working
"awesomeArgObj_loc.ty * 3 = awesomeArgObj_loc.multResult",#Working
"awesomeArgObj_loc.ty + 3 + awesomeArgObj_loc.ty = awesomeArgObj_loc.sumResult",#Working
"if awesomeArgObj_loc.ty > 3;awesomeArgObj_loc.result2",#Working

"(1+2)"

#>>> setRange
#======================================================================
"""
linstep 1 3 2;
// Result: 0.5 //
linstep 1 3 5;
// Result: 1 //
linstep 1 3 2.5;
// Result: 0.75 //
"""
mi_setRange = cgmMeta.cgmNode(nodeType='setRange')
cgmMeta.cgmAttr(mi_setRange,'result',attrType='float').doConnectIn("%s.%s."%(mi_setRange.mNode,'outValueX'))

mi_remap = cgmMeta.cgmNode(nodeType='remapValue')
cgmMeta.cgmAttr(mi_remap,'result',attrType='float').doConnectIn("%s.%s."%(mi_remap.mNode,'outColorR'))

mi_clamp = cgmMeta.cgmNode(nodeType='clamp')
cgmMeta.cgmAttr(mi_clamp,'result',attrType='float').doConnectIn("%s.%s."%(mi_clamp.mNode,'outputR'))

