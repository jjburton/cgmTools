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

#>>> Modules
#=======================================================
m1 = cgmPM.cgmModule(name = 'test')
m1 = r9Meta.MetaClass('spine_part')
m1.setState('skeleton')
m1.getPartNameBase()
m1.modulePuppet.getGeo()
mCurveFactory.go(m1,['segmentIKHandle'])
mCurveFactory.go(m1,['segmentIK'])
mCurveFactory.go(m1,['segmentFK'])
mCurveFactory.go(m1,['cog'])
mCurveFactory.go(m1,['hips'])
mCurveFactory.go(m1)

a = dataHolder()
a=[]
a.__dict__
mCurveFactory.go(m1,['hips'])
class dataHolder(object):
    pass
l_targetObjects = mc.ls(sl=True)
#Extend modes: 'segment','radial
mCurveFactory.createWrapControlShape(l_targetObjects,'Morphy_Body_GEO1',extendMode='segment',curveDegree=3,joinMode=True,posOffset = [0,0,3],points=8)
mCurveFactory.createWrapControlShape(l_targetObjects,'Morphy_Body_GEO1',extendMode='segment',curveDegree=3,joinMode=True,posOffset = [0,0,2],points=8)
mCurveFactory.createWrapControlShape(l_targetObjects,'Morphy_Body_GEO1',extendMode='segment',distanceMult=.1,curveDegree=3,joinMode=False,posOffset = [0,0,2],points=8)

target = mc.ls(sl=True)[0]
info = mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',target,curveDegree=3,posOffset = [0,0,3],points=8,returnDict = True)
info = mCurveFactory.createMeshSliceCurve('Morphy_Body_GEO1',target,curveDegree=3,posOffset = [0,0,3],points=8,returnDict = True)

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