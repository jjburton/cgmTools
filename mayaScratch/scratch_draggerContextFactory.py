import cgm.core
cgm.core._reload()
import maya.cmds as mc

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta

from cgm.lib import locators
from cgm.lib import distance
from cgm.lib import attributes
reload(attributes)
attributes.validateAttrArg(['spine_1_anchorJoint','rz'])
reload(distance)
from cgm.core.lib import rayCaster as RayCast
reload(RayCast)

from cgm.core.classes import DraggerContextFactory as dragFactory
reload(dragFactory)

obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []

#>>> ClickMesh
#=======================================================
i_obj = cgmMeta.cgmObject(mc.ls(sl=True)[0])
i_obj.getPosition()
mesh = 'Morphy_Body_GEO'
mesh = 'polySurface2'
mesh = 'cage_v01'
create = 'curve'
create = 'locator'
create = 'joint'
create = 'follicle'
offsetMode = 'vector'
offsetMode = 'normal'

geo= [u'|Morpheus|noTransform_grp|geo_grp|Morphy_GRP|Morphy_Body_GEO', u'|Morpheus|noTransform_grp|geo_grp|Morphy_GRP|Morphy_R_GRP|Morphy_Ear_R_GEO', u'|Morpheus|noTransform_grp|geo_grp|Morphy_GRP|Morphy_R_GRP|Morphy_Brow_R_GEO', u'|Morpheus|noTransform_grp|geo_grp|Morphy_GRP|Morphy_R_GRP|Morphy_Eye_R_GRP|EyeBall_R_GEO', u'|Morpheus|noTransform_grp|geo_grp|Morphy_GRP|Morphy_R_GRP|Morphy_Eye_R_GRP|EyeIris_R_GEO', u'|Morpheus|noTransform_grp|geo_grp|Morphy_GRP|Morphy_R_GRP|Morphy_Eye_R_GRP|EyePupil_R_GEO', u'|Morpheus|noTransform_grp|geo_grp|Morphy_GRP|Morphy_L_GRP|Morphy_Ear_L_GEO', u'|Morpheus|noTransform_grp|geo_grp|Morphy_GRP|Morphy_L_GRP|Morphy_Brow_L_GEO', u'|Morpheus|noTransform_grp|geo_grp|Morphy_GRP|Morphy_L_GRP|Morphy_Eye_L_GRP|EyeBall_L_GEO', u'|Morpheus|noTransform_grp|geo_grp|Morphy_GRP|Morphy_L_GRP|Morphy_Eye_L_GRP|EyeIris_L_GEO', u'|Morpheus|noTransform_grp|geo_grp|Morphy_GRP|Morphy_L_GRP|Morphy_Eye_L_GRP|EyePupil_L_GEO'] 
geo = ['headWrapDriver']
geo = ['cage_v01']
geo = ['pSphere1']
geo = ['segment:polySurface3']
a = dragFactory.clickMesh(mode = 'midPoint',
                           mesh = geo,
                           create = 'locator',
                           )
a = dragFactory.clickMesh(mode = 'surface',
                           mesh = geo,
                           create = 'curve',
                           )

a = dragFactory.clickMesh(mode = 'surface',
                          mesh = geo,
                          create = 'locator',
                          posOffset=[0,0,3],
                          )
a = dragFactory.clickMesh(mode = 'surface',
                          mesh = geo,
                          create = create,
                          offsetMode = offsetMode,
                          posOffset=[0,0,-.5],
                          clampValues = [0,None,None],
                          orientSnap=False,
                          )
a = dragFactory.clickMesh(mode = 'surface',
                          mesh = geo,
                          create = create,
                          offsetMode = offsetMode,
                          posOffset=[0,0,-.75],
                          tagAndName={'cgmDirection':'left','cgmName':'temple'},
                          orientSnap=True,
                          )
a = dragFactory.clickMesh(mode = 'surface',
                          mesh = geo,
                          create = create,
                          offsetMode = None,
                          )
reload(dragFactory)
from cgm.lib import constraints as constraints
reload(constraints)

#>>> Constraining to surface
#=======================================================
from cgm.lib import surfaces
surfaces.attachObjectToMesh(mc.ls(sl=True)[0],geo[0])
for obj in mc.ls(sl=True):
    surfaces.attachObjectToMesh(obj,geo[0])
    
#>>Follicle ===================================================================
#Single
from cgm.core.rigger.lib import joint_Utils as jntUtils
jntUtils.metaFreezeJointOrientation(mc.ls(sl=True))
def addFollicleSingleAttach(obj,mesh):
    from cgm.lib import (distance,nodes,attributes)
    mi_obj = cgmMeta.validateObjArg(obj,cgmMeta.cgmObject)
    mi_mesh = cgmMeta.validateObjArg(mesh,mayaType = 'mesh')
    uv = distance.returnClosestUVToPos(mi_mesh.mNode,mi_obj.getPosition())
    follicle = nodes.createFollicleOnMesh(mi_mesh.mNode)
    attributes.doSetAttr(follicle[0],'parameterU',uv[0])
    attributes.doSetAttr(follicle[0],'parameterV',uv[1])
    
    #create group
    mi_attachPoint = mi_obj.doLoc()
    mi_attachPoint.parent = follicle[1]
    
    #parent constrain
    mc.pointConstraint(mi_attachPoint.mNode,mi_obj.mNode,maintainOffset = True)
    mc.orientConstraint(mi_attachPoint.mNode,mi_obj.mNode,maintainOffset = True)
    
    
def addPointOnPolyNormalAttach(obj,mesh):
    from cgm.lib import (distance,nodes,attributes)
    mi_obj = cgmMeta.validateObjArg(obj,cgmMeta.cgmObject)
    mi_mesh = cgmMeta.validateObjArg(mesh,mayaType = 'mesh')
    
    #create group
    mi_attachPoint = mi_obj.doLoc()
    mc.pointOnPolyConstraint(mi_mesh.mNode,mi_attachPoint.mNode,maintainOffset = True)
    mc.normalConstraint(mi_mesh.mNode,mi_attachPoint.mNode,maintainOffset = True)
    
    #parent constrain
    mc.parentConstraint(mi_attachPoint.mNode,mi_obj.mNode,maintainOffset = True)
    
3.847
150.804
16.954