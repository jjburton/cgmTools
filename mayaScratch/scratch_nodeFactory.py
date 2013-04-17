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
from cgm.lib import cgmMath
reload(cgmMath)
cgmMath.isFloatEquivalent(3,3.0)
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


#>>> puppet adding controls
i_node = a.masterControl.controlSettings
d_attrKWs = {'skeleton':{'value':0,'defaultValue':0},
             'geo':{'value':1,'defaultValue':1}}

l_buildCatch = []             
for attr in ['skeleton','geo',]:
    i_node.addAttr(attr,enumName = 'off:referenced:on', attrType = 'enum',keyable = False,hidden = False)
    a = nFactory.argsToNodes("if %s.%s > 0; %s.%sVis"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
    l_buildCatch.append(a)
    a = nFactory.argsToNodes("if %s.%s == 2:0 else 2; %s.%sLock"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
    l_buildCatch.append(a)
    
for l in l_buildCatch:
    l
    
i_node.addAttr('partGuts',enumName = 'proxy:parts:reg', attrType = 'enum',keyable = False,hidden = False)
    
i_node.addAttr('geoType',enumName = 'proxy:parts:reg', attrType = 'enum',keyable = False,hidden = False)



str_nodeShort = str(i_node.getShortName())
nFactory.argsToNodes("if %s.skeleton > 0; %s.skeletonVis"%(str_nodeShort,str_nodeShort)).doBuild()
nFactory.argsToNodes("if %s.skeleton == 2:0 else 2; %s.skeletonLock"%(str_nodeShort,str_nodeShort)).doBuild()


'if %s.skeleton == 2:0 else 2; %s.skeletonUnlock'


#>>> validateNodeArg
#=======================================================
reload(nFactory)
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


arg = "worldCenter_loc.tx + worldCenter_loc.ty + worldCenter_loc.tz = worldCenter_loc.sumResult1"
arg = "1 + 2 + 3 = worldCenter_loc.simpleSum"#Working
arg = "1 + 2 + 7 = worldCenter_loc.simpleSum"#Working

arg = "1 >< 2 >< 3 = worldCenter_loc.simpleAv"#Working
arg = "3 * -worldCenter_loc.ty = worldCenter_loc.inverseMultThree"#Working
arg = "4 - 2 = worldCenter_loc.simpleMathResult"#Working
arg = "-worldCenter_loc.ty = worldCenter_loc.tz"#Working
arg = "worldCenter_loc.ty * 3 = worldCenter_loc.multResult"#Working
arg = "worldCenter_loc.ty + 3 + worldCenter_loc.ty = worldCenter_loc.sumResult"#Working
arg = "if worldCenter_loc.ty < 3;worldCenter_loc.result2"#Working
arg = "(1+2)"
arg = "worldCenter_loc.ty + worldCenter_loc.tz = worldCenter_loc.sumResult"#Working


arg = "if worldCenter_loc.ty > 3;worldCenter_loc.result2,worldCenter_loc.result2copy"#Working

from cgm.core.classes import NodeFactory as nFactory
reload(nFactory)
a = nFactory.argsToNodes(arg)
for b in a.ml_attrs:
    b.p_combinedName

mc.ls(a.ml_attrs[0].p_combinedName,sn=True)[0]
nFactory.argsToNodes(arg).d_networksToBuild
nFactory.argsToNodes(arg).d_connectionsToMake

nFactory.argsToNodes(arg).doBuild()
nFactory.argsToNodes(arg,defaultAttrType='bool',keyable=False, hidden = True, lock = True).buildNodes()



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