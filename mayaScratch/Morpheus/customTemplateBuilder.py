from cgm.core.rigger import CustomizationFactory as CustomF
reload(CustomF)

asset = 'M1_customizationNetwork'
CustomF.go(asset,reportShow = 1)
CustomF.go(asset,stopAtStep = 1,reportShow = 0)
help(CustomF.go)
 
reload(CustomF)
CustomF.log.setLevel(CustomF.logging.DEBUG)
CustomF.go(stopAtStep = 1,setLogLevel = 'debug' )
CustomF.go(stopAtStep = 1,setLogLevel = 'info' )

reload(pFactory)
reload(morphyF)
reload(mFactory)
reload(tFactory)
reload(jFactory)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

import cgm.core
cgm.core._reload()

#>>> Generate Morpheus asset Template
m1 = cgmMeta.cgmNode('M1_customizationNetwork')
m1.objSetAll.reset()

m1.__verify__()
m1.masterControl.rebuildControlCurve()
m1.isCustomizable()
m1.baseBodyGeo = mc.ls(sl=1)
m1.baseBodyGeo 
m1.connectChildNode('Morphy_Body_GEO','baseBodyGeo')
m1.masterGroup
m1.__verify__()
m1.masterNull.getMessage('bodyGeoGroup')

#>>> Snippets
for obj in mc.ls(sl=True):
    mObj = cgmMeta.cgmObject(obj)
    if mObj.hasAttr('constraintPointTargets'):
        if mObj.getMessage('constraintPointTargets'):
            print "{0} has constraintPointTargets attr".format(mObj.p_nameShort)
            
for str_attr in ['constraintPointTargets','constraintParentTargets','constraintScaleTargets','constraintOrientTargets']:
    for obj in mc.ls(sl=True):
        mObj = cgmMeta.cgmObject(obj)
        if mObj.hasAttr(str_attr):
            if not mObj.getMessage(str_attr):
                print "{0} has empty {1} attr".format(mObj.p_nameShort,str_attr)
                mObj.doRemove(str_attr)
                
for str_attr in ['constraintPointTargets','constraintParentTargets','constraintScaleTargets','constraintOrientTargets']:
    for obj in mc.ls(sl=True):
        mObj = cgmMeta.cgmObject(obj)
        if mObj.hasAttr(str_attr):
            mObj.doRemove(str_attr)
            
for str_attr in ['constraintParentTargets']:
    for obj in mc.ls(sl=True):
        mObj = cgmMeta.cgmObject(obj)
        if mObj.hasAttr(str_attr):
            mObj.doRemove(str_attr)       
            
#Morpheus Gui ===================================================================================
import morpheusRig_v2
#from morpheusRig_v2.tools import MorpheusMaker as MorphyMaker
from morpheusRig_v2.core.tools import MorpheusMaker as MorphyMaker
from morpheusRig_v2.core.tools.lib import MorpheusMaker_utils as MorphyMakerUtils
reload(MorphyMakerUtils)
reload(MorphyMaker)    
MorphyMaker.go()

r9Meta.getMetaNodes(mAttrs = 'mClass', mTypes='cgmMorpheusMakerNetwork',dataType = '')

#Preset Saving ----------------------
from morpheusRig_v2.core import MorpheusPresetFactory as mPreset
reload(mPreset)
filePath = 'J:/repos/morpheusrig2/morpheusRig_v2/presets/test.cfg'
m1 = cgmMeta.cgmNode('M1_customizationNetwork')
nodes = m1.objSetAll.value
for mObj in nodes:
    log.info(mObj)
    
poseBuffer = mPreset.go()
poseBuffer.poseSave(nodes,filePath,useFilter=False)
poseBuffer.poseSave(nodes)
poseBuffer.metaPose=False
poseBuffer.buildInternalPoseData(nodes)
poseBuffer.thumbnailRes
poseBuffer.useFilter = False
poseBuffer.useFilter

poseBuffer.metaPose
poseBuffer._buildInfoBlock()
poseBuffer._buildPoseDict(nodes)
poseBuffer.rootJnt = nodes[0]
poseBuffer._buildSkeletonData(poseBuffer.rootJnt)
poseBuffer._buildSkeletonData(poseBuffer.rootJnt)
poseBuffer.poseDict

from Red9.core import Red9_PoseSaver as r9Pose
reload(r9Pose)
r9Pose.log.setLevel(r9Pose.logging.DEBUG)

poseBuffer = r9Pose.PoseData()
poseBuffer.poseSave(nodes,filePath)
poseBuffer.metaPose=False

#Thumbnail -------------------------------------------------------------------
from Red9.core import Red9_General as r9General
reload(r9General)
filePath = 'J:/repos/morpheusrig2/morpheusRig_v2/presets/test.bmp'
r9General.thumbnailApiFromView(filePath, 230, 230, compression='bmp', modelPanel='modelPanel4')

