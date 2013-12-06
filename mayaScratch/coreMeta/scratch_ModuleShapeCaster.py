import cgm.core
cgm.core._reload()
import maya.cmds as mc

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta

from cgm.core.classes import SnapFactory as Snap
reload(Snap)
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.lib import shapeCaster as ShapeCast
reload(mShapeCast)
reload(ShapeCast)
from cgm.lib import rigging
reload(rigging)
#>>>Base control size
caster = 'curve1'
geo = 'Morphy_Body_GEO'
axis = ['z+']
mShapeCast.returnBaseControlSize(caster,geo,axis)#Get size
reload(mShapeCast)
mi_go = mShapeCast.go(m1)
m1.isTemplated()
mShapeCast.shapeCast_mouthNose(mi_go,reportTimes = True)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

#Meshslice bankRotate:
rotateBank = -10
mShapeCast.createMeshSliceCurve('Morphy_Body_GEO1',l_targetObjects[0],curveDegree=3,posOffset = [0,0,2.5],points=8,returnDict = True,latheAxis='z',aimAxis='y-')
info = mShapeCast.createMeshSliceCurve('Morphy_Body_GEO1',l_targetObjects[0],maxDistance=12,curveDegree=3,rotateBank = rotateBank,posOffset = [0,0,2.5],points=8,returnDict = True,latheAxis='z',aimAxis='y-')
ShapeCast.createMeshSliceCurve('Morphy_Body_GEO','noseTip_rig_jnt_loc',rotateBank = -10,curveDegree=3,posOffset = [0,0,.5],points=8,returnDict = True,latheAxis='z',aimAxis='y-')

minRotate = 0
maxRotate = 360
mShapeCast.createMeshSliceCurve('Morphy_Body_GEO1',l_targetObjects[0],minRotate=minRotate,maxRotate=maxRotate,curveDegree=3,posOffset = [0,0,2.5],points=8,returnDict = True,latheAxis='z',aimAxis='y+')
mShapeCast.createMeshSliceCurve('Morphy_Body_GEO1',l_targetObjects[0],closestInRange=False,minRotate=minRotate,maxRotate=maxRotate,curveDegree=3,posOffset = [0,0,2.5],points=8,returnDict = True,latheAxis='z',aimAxis='y+',maxDistance=10)

range(minRotate,maxRotate+1)
from cgm.lib import lists
lists.returnListChunks(l_range,22)
l_range = range(minRotate,maxRotate+1)
len( range(minRotate,maxRotate+1) ) /8
l_specifiedRotates = [-60,-30,-10,0,10,30,60]
l_specifiedRotates = [-120,-150,180,150,120]
l_specifiedRotates = [-20,0,20]

curveDegree = 3
closedCurve = False
ShapeCast.createMeshSliceCurve(geo,l_targetObjects[0],closedCurve = closedCurve,l_specifiedRotates = l_specifiedRotates,curveDegree=curveDegree,posOffset = [0,0,1.5],points=8,returnDict = True,latheAxis='z',aimAxis='y+')
l_pos = []
for curve in mc.ls(sl=True):
    l_buffer = []
    for cv in mc.ls("%s.cv[*]"%curve,flatten=True):
        l_buffer.append(cgmMeta.cgmNode(cv).getPosition())
    l_pos.append(l_buffer)
l_pos
for i,pos in enumerate(l_pos[0]):
    mc.curve(degree=1, ep = [pos,l_pos[1][i]])

#>>> Wrap shape
#=======================================================
reload(mShapeCast)
l_targetObjects = mc.ls(sl=True)
log.debug(l_targetObjects)
geo = 'Morphy_Body_GEO'
mShapeCast.createWrapControlShape(l_targetObjects,geo,posOffset = posOffset,points=points,latheAxis=latheAxis,aimAxis=aimAxis,extendMode=extendMode)
posOffset = [0,0,1]
mShapeCast.createWrapControlShape(l_targetObjects,'Morphy_Body_GEO',joinMode = True, extendMode = extendMode, curveDegree=3, maxDistance = maxDistance, posOffset = posOffset,points=points,latheAxis='z+',aimAxis='y-')
mShapeCast.createWrapControlShape(l_targetObjects[0],'Morphy_Body_GEO',joinMode = True, extendMode = extendMode, curveDegree=3, maxDistance = maxDistance, posOffset = posOffset,points=points,latheAxis='z+',aimAxis='y-')
mShapeCast.createWrapControlShape(l_targetObjects[0],geo,joinMode = True, extendMode = extendMode, curveDegree=3, maxDistance = maxDistance, posOffset = posOffset,points=points,latheAxis='z+',aimAxis='y-')
#clavicle
mShapeCast.createWrapControlShape(l_targetObjects,geo,joinMode = True, insetMult = insetMult, rootRotate=[0,-30,0],closedCurve = closedCurve,  l_specifiedRotates = l_specifiedRotates,extendMode = extendMode, curveDegree=3, maxDistance = maxDistance, posOffset = posOffset,points=points,latheAxis=latheAxis,aimAxis=aimAxis)

#finger
extendMode = 'loliwrap'
curveDegree = 3
posOffset = [0,0,.75]
closedCurve = False
maxDistance = 50
aimAxis = 'y+'
latheAxis = 'z'
closestInRange = False
joinMode = False
l_specifiedRotates = [-40,-20,0,]
ShapeCast.createWrapControlShape(l_targetObjects,geo,joinMode = True, insetMult = insetMult,closedCurve = closedCurve,  l_specifiedRotates = l_specifiedRotates,extendMode = extendMode, curveDegree=3, maxDistance = maxDistance, posOffset = posOffset,points=points,latheAxis=latheAxis,aimAxis=aimAxis)

#capEnd
extendMode = 'endCap'
curveDegree = 3
posOffset = [0,0,.5]
closedCurve = True
maxDistance = 5
points = 12
aimAxis = 'y+'
latheAxis = 'z'
closestInRange = True
joinMode = False
l_specifiedRotates = []
ShapeCast.createWrapControlShape(l_targetObjects,'polySurface2',joinMode = True, insetMult = insetMult,closedCurve = closedCurve,  l_specifiedRotates = l_specifiedRotates,extendMode = extendMode, curveDegree=3, maxDistance = maxDistance, posOffset = posOffset,points=points,latheAxis=latheAxis,aimAxis=aimAxis)

extendMode = 'loliwrap'
curveDegree = 3
posOffset = [0,0,.75]
points = 6
rotateBank = 0
closedCurve = True
maxDistance = 2
aimAxis = 'x-'
latheAxis = 'z'
closestInRange = True
insetMult = .3
joinMode = True
l_specifiedRotates = []
l_specifiedRotates = [-180,-120,-90,-30,0,30]
l_specifiedRotates = [30,0,-30,-90,-120,-180]
l_specifiedRotates = [0,5,10,40,90,120,170,175,180]

l_specifiedRotates = [-30,-20,-10,-5,0,5,10,20,30]
geo = 'Morphy_Body_GEO'
l_specifiedRotates = [-40,-30,-20,-10,0,10,20,30,40]
l_specifiedRotates = [-90,-60,-30,0,30,60,90]#Neck
l_specifiedRotates = [-90,-60,-30,0,30,60,90]#hip
l_specifiedRotates = [-40,-20,0,20,40,60,80,100]#foot front, closed false, closest in range false
l_specifiedRotates = [-90,-60,-20,0,20,40,60,80,100,120]#foot back, closed false, closest in range false
l_specifiedRotates = [-120,-100,-80,-50]#foot front closest, closed false, closest in range true

ShapeCast.createMeshSliceCurve(geo,l_targetObjects[0],maxDistance = maxDistance,closedCurve = closedCurve,curveDegree=curveDegree,posOffset = [0,0,1.5],points=8,returnDict = True,latheAxis=latheAxis,aimAxis=aimAxis,closestInRange=closestInRange)
ShapeCast.createMeshSliceCurve(geo,l_targetObjects[0],closedCurve = closedCurve,closestInRange = closestInRange, maxDistance = maxDistance,midMeshCast=True,l_specifiedRotates = l_specifiedRotates,curveDegree=curveDegree,posOffset = [0,0,.75],points=points,returnDict = True,latheAxis='z',aimAxis='y+')
ShapeCast.createMeshSliceCurve(geo,l_targetObjects[0],axisToCheck=['x'],offsetMode='vector',maxDistance = maxDistance,l_specifiedRotates = l_specifiedRotates,closedCurve = closedCurve,curveDegree=curveDegree,posOffset = [0,0,.75],points=points,returnDict = True,latheAxis=latheAxis,aimAxis=aimAxis,closestInRange=closestInRange,midMeshCast=True)

extendMode = ''
for o in l_targetObjects:
    mShapeCast.createWrapControlShape(o,'Morphy_Body_GEO1',joinMode = True, rotateBank=rotateBank,closedCurve = closedCurve, l_specifiedRotates = l_specifiedRotates, extendMode = extendMode, maxDistance=maxDistance,curveDegree=curveDegree, posOffset = posOffset,points=points,latheAxis='z+',aimAxis='y+')
mShapeCast.createWrapControlShape(l_targetObjects,geo,joinMode = joinMode, insetMult = insetMult,rotateBank=rotateBank,closedCurve = closedCurve, l_specifiedRotates = l_specifiedRotates, extendMode = extendMode, maxDistance=maxDistance,curveDegree=curveDegree, posOffset = posOffset,points=points,latheAxis=latheAxis,aimAxis=aimAxis)

#Loli
extendMode = 'cylinder'
closedCurve = False
l_specifiedRotates = [-30,-20,-10,-5,0,5,10,20,30]



#>>> Modules
#=======================================================
reload(mShapeCast)
m1 = cgmPM.cgmModule(name = 'test')
m1 = r9Meta.MetaClass('spine_part')
m1.setState('template')
m1.getPartNameBase()
m1.modulePuppet.getGeo()
mShapeCast.go(m1,['loliHandles'],['neck_1_1_jnt','neck_2_jnt'])
mShapeCast.go(m1,['segmentIK'])
mShapeCast.go(m1,['torsoIK'])

mShapeCast.go(m1,['segmentFK'])
mShapeCast.go(m1,['segmentFK_Loli'])
mShapeCast.go(m1,['cog'])
mShapeCast.go(m1,['hips'])
mShapeCast.go(m1)
mShapeCast.go(m1,['segmentFK_Loli','segmentIK'])

a = dataHolder()
a=[]
a.__dict__
mShapeCast.go(m1,['hips'])
class dataHolder(object):
    pass
l_targetObjects = mc.ls(sl=True)
#Curve Creation demo
#Extend modes: 'segment','radial
degree = 3
points = 8
extendMode = 'disc'
joinMode = True
insetMult = 0
posOffset = [0,0,3]
rootOffset = [0,0,-2]

info = mShapeCast.createMeshSliceCurve(geo,l_targetObjects[0],curveDegree=3,posOffset = [0,0,2.5],points=8,returnDict = True,latheAxis='z',aimAxis='y+')
info = mShapeCast.createMeshSliceCurve('Morphy_Body_GEO1',l_targetObjects[0],curveDegree=3,posOffset = [0,0,2.5],points=8,returnDict = True,latheAxis='x',aimAxis='y+')
info = mShapeCast.createMeshSliceCurve(geo,l_targetObjects[0],axisToCheck = ['y'],midMeshCast=True,curveDegree=3,posOffset = [0,0,2.5],points=7,returnDict = True,latheAxis='z',aimAxis='x+')

mShapeCast.createWrapControlShape(l_targetObjects,geo,extendMode=extendMode,midMeshCast=True,rootOffset=rootOffset,curveDegree=degree,joinMode=joinMode,insetMult=insetMult,posOffset = posOffset,points=points,latheAxis='z+',aimAxis='y-')

l_targetObjects = mc.ls(sl=True)

info = mShapeCast.createMeshSliceCurve('Morphy_Body_GEO1',target,latheAxis='y+',aimAxis='z+',curveDegree=degree,posOffset = posOffset,points=points,returnDict = True)
info = mShapeCast.createMeshSliceCurve('Morphy_Body_GEO1',target,latheAxis='y+',aimAxis='z+',curveDegree=degree,posOffset = posOffset,points=points,returnDict = True)

info = mShapeCast.createMeshSliceCurve('Morphy_Body_GEO1',mc.ls(sl=True)[0],initialRotate=45,curveDegree=1,posOffset = [0,0,8],points=4,returnDict = True)
mShapeCast.BuildControlShapes
info = mShapeCast.createMeshSliceCurve('Morphy_Body_GEO1',mc.ls(sl=True)[0],curveDegree=1,posOffset = [0,0,3],points=5,returnDict = True)
info = mShapeCast.createMeshSliceCurve('Morphy_Body_GEO1',mc.ls(sl=True)[0],offsetMode='',curveDegree=1,posOffset = [0,0,3],points=5,returnDict = True)

log.debug(info)
info['processedHits'].get(111)
mShapeCast.limbControlMaker(m1,['segmentControlsNew','hips'])
mShapeCast.limbControlMaker(m1,['fkSegmentControls','ikSegmentControls'])

mShapeCast.limbControlMaker(m1,['segmentControls','hips','cog'])

mShapeCast.limbControlMaker(m1,['segmentControls','hips','cog'])
mShapeCast.limbControlMaker(m1,['segmentControlsNEW'])

mesh = 'Morphy_Body_GEO1'
i_obj = cgmMeta.cgmObject('pelvis_templateOrientHelper')
mShapeCast.returnBaseControlSize(i_obj, mesh,axis = ['x','y','z-'])
mShapeCast.returnBaseControlSize(i_obj, mesh,axis = ['x'])

mc.softSelect(softSelectEnabled = True)
mc.softSelect(q = True, softSelectDistance = True)
mc.softSelect(q = True, softSelectUVDistance = True)
mc.softSelect(q = True, softSelectFalloff = 2)
mc.softSelect(softSelectFalloff = 0)
mc.softSelect(softSelectDistance = 20)
mc.softSelect(softSelectUVDistance = 30)

#252ms
m1.isSkeletonized()
mShapeCast.go(obj)
m1.setState('skeleton')
tFactory.returnModuleBaseSize(m2)
m2.rigNull.skinJoints
m2.moduleParent.rigNull.skinJoints
m2.templateNull.controlObjects
m2 = r9Meta.MetaClass('l_hand_part')