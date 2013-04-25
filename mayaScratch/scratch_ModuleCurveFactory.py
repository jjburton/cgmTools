import cgm.core
cgm.core._reload()
import maya.cmds as mc

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta

from cgm.core.classes import SnapFactory as Snap
reload(Snap)
from cgm.core.rigger import ModuleCurveFactory as mCurveFactory
reload(mCurveFactory)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

#Meshslice bankRotate:
rotateBank = -10
mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',l_targetObjects[0],curveDegree=3,posOffset = [0,0,2.5],points=8,returnDict = True,latheAxis='z',aimAxis='y-')
info = mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',l_targetObjects[0],maxDistance=12,curveDegree=3,rotateBank = rotateBank,posOffset = [0,0,2.5],points=8,returnDict = True,latheAxis='z',aimAxis='y-')

minRotate = 0
maxRotate = 360
mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',l_targetObjects[0],minRotate=minRotate,maxRotate=maxRotate,curveDegree=3,posOffset = [0,0,2.5],points=8,returnDict = True,latheAxis='z',aimAxis='y+')
mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',l_targetObjects[0],closestInRange=False,minRotate=minRotate,maxRotate=maxRotate,curveDegree=3,posOffset = [0,0,2.5],points=8,returnDict = True,latheAxis='z',aimAxis='y+',maxDistance=10)

range(minRotate,maxRotate+1)
from cgm.lib import lists
lists.returnListChunks(l_range,22)
l_range = range(minRotate,maxRotate+1)
len( range(minRotate,maxRotate+1) ) /8
l_specifiedRotates = [-60,-30,-10,0,10,30,60]
l_specifiedRotates = [-120,-150,180,150,120]

curveDegree = 3
closedCurve = False
mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',l_targetObjects[0],closedCurve = closedCurve,l_specifiedRotates = l_specifiedRotates,curveDegree=curveDegree,posOffset = [0,0,1.5],points=8,returnDict = True,latheAxis='z',aimAxis='y+')


#>>> Wrap shape
#=======================================================
reload(mCurveFactory)
l_targetObjects = mc.ls(sl=True)
log.info(l_targetObjects)
mCurveFactory.createWrapControlShape(l_targetObjects,'Morphy_Body_GEO1',posOffset = posOffset,points=points,latheAxis='z+',aimAxis='y-')
posOffset = [0,0,1]
mCurveFactory.createWrapControlShape(l_targetObjects,'Morphy_Body_GEO1',joinMode = True, extendMode = 'disc', curveDegree=3, posOffset = posOffset,points=points,latheAxis='z+',aimAxis='y-')

extendMode = 'disc'
curveDegree = 3
posOffset = [0,0,1]
points = 8
rotateBank = 10
closedCurve = False
maxDistance = 1000
l_specifiedRotates = None
l_specifiedRotates = [-60,-30,-10,0,10,30,60]
l_specifiedRotates = [-90,-60,-30,0,30,60,90]#Neck
for o in l_targetObjects:
    mCurveFactory.createWrapControlShape(o,'Morphy_Body_GEO1',joinMode = True, rotateBank=rotateBank,closedCurve = closedCurve, l_specifiedRotates = l_specifiedRotates, extendMode = extendMode, maxDistance=maxDistance,curveDegree=curveDegree, posOffset = posOffset,points=points,latheAxis='z+',aimAxis='y+')
mCurveFactory.createWrapControlShape(l_targetObjects,'Morphy_Body_GEO1',joinMode = True, rotateBank=rotateBank,closedCurve = closedCurve, l_specifiedRotates = l_specifiedRotates, extendMode = extendMode, maxDistance=maxDistance,curveDegree=curveDegree, posOffset = posOffset,points=points,latheAxis='z+',aimAxis='y+')




#>>> Modules
#=======================================================
reload(mCurveFactory)
m1 = cgmPM.cgmModule(name = 'test')
m1 = r9Meta.MetaClass('neck_part')
m1.setState('skeleton')
m1.getPartNameBase()
m1.modulePuppet.getGeo()
mCurveFactory.go(m1,['loliHandles'],['neck_1_1_jnt','neck_2_jnt'])
mCurveFactory.go(m1,['segmentIK'])
mCurveFactory.go(m1,['segmentFK'])
mCurveFactory.go(m1,['segmentFK_Loli'])
mCurveFactory.go(m1,['cog'])
mCurveFactory.go(m1,['hips'])
mCurveFactory.go(m1)
mCurveFactory.go(m1,['segmentFK_Loli','segmentIK'])

a = dataHolder()
a=[]
a.__dict__
mCurveFactory.go(m1,['hips'])
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
posOffset = [0,0,6]
info = mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',l_targetObjects[0],curveDegree=3,posOffset = [0,0,2.5],points=8,returnDict = True,latheAxis='y',aimAxis='z+')

mCurveFactory.createWrapControlShape(l_targetObjects,'Morphy_Body_GEO1',extendMode=extendMode,curveDegree=degree,joinMode=joinMode,insetMult=insetMult,posOffset = posOffset,points=points,latheAxis='z+',aimAxis='y-')

target = mc.ls(sl=True)[0]

info = mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',target,latheAxis='y+',aimAxis='z+',curveDegree=degree,posOffset = posOffset,points=points,returnDict = True)
info = mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',target,latheAxis='y+',aimAxis='z+',curveDegree=degree,posOffset = posOffset,points=points,returnDict = True)

info = mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',mc.ls(sl=True)[0],initialRotate=45,curveDegree=1,posOffset = [0,0,8],points=4,returnDict = True)
mCurveFactory.BuildControlShapes
info = mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',mc.ls(sl=True)[0],curveDegree=1,posOffset = [0,0,3],points=5,returnDict = True)
info = mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',mc.ls(sl=True)[0],offsetMode='',curveDegree=1,posOffset = [0,0,3],points=5,returnDict = True)

log.info(info)
info['processedHits'].get(111)
mCurveFactory.limbControlMaker(m1,['segmentControlsNew','hips'])
mCurveFactory.limbControlMaker(m1,['fkSegmentControls','ikSegmentControls'])

mCurveFactory.limbControlMaker(m1,['segmentControls','hips','cog'])

mCurveFactory.limbControlMaker(m1,['segmentControls','hips','cog'])
mCurveFactory.limbControlMaker(m1,['segmentControlsNEW'])

mesh = 'Morphy_Body_GEO1'
i_obj = cgmMeta.cgmObject('pelvis_templateOrientHelper')
mCurveFactory.returnBaseControlSize(i_obj, mesh,axis = ['x','y','z-'])
mCurveFactory.returnBaseControlSize(i_obj, mesh,axis = ['x'])

mc.softSelect(softSelectEnabled = True)
mc.softSelect(q = True, softSelectDistance = True)
mc.softSelect(q = True, softSelectUVDistance = True)
mc.softSelect(q = True, softSelectFalloff = 2)
mc.softSelect(softSelectFalloff = 0)
mc.softSelect(softSelectDistance = 20)
mc.softSelect(softSelectUVDistance = 30)

#252ms
m1.isSkeletonized()
mCurveFactory.go(obj)
m1.setState('skeleton')
tFactory.returnModuleBaseSize(m2)
m2.rigNull.skinJoints
m2.moduleParent.rigNull.skinJoints
m2.templateNull.controlObjects
m2 = r9Meta.MetaClass('l_hand_part')