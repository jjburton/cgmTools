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
from cgm.core.lib import curve_Utils as crvUtils

from cgm.core.lib import surface_Utils as surfUtils
reload(surfUtils)
from cgm.core.rigger.lib import joint_Utils as jUtils

                               
obj = mc.ls(sl=True)[0] or False
obj = ''
objList = []
objList = mc.ls(sl=True)
cgmMeta.cgmObject(obj).createTransformFromObj()

#>>> normalize uv value
#=======================================================
surfUtils.returnNormalizedUV('nurbsSurface1',2.0, 4.328492105359997)

#>>> mirror curve curve list
#=======================================================
reload(surfUtils)
surface = 'loftedSurface1'
surface = 'skullPlate'
surface = 'uprLipFollow_plate_surf'
surface = 'browPlate'
obj = 'center_browUpr_jnt'
surfUtils.attachObjToSurface(obj,surface,True)
for jnt in mc.ls(sl=True):
    surfUtils.attachObjToSurface(jnt,surface,True)
    
for jnt in mc.ls(sl=True):
    surfUtils.attachObjToSurface(jnt,surface,True,attachControlLoc = 1)
    
for jnt in mc.ls(sl=True):
    surfUtils.attachObjToSurface(jnt,surface,False)
    
#>>> loft curve - radial
# create_curveLoft
#=======================================================
reload(surfUtils)
curve = 'smileLeft_2_rigHelper'
posObj = 'mouthMove_handle_anim'
posObj = [0,0,0]
surfUtils.create_radialCurveLoft(curve,posObj)
surfUtils.create_radialCurveLoft(curve,aimPointObject = posObj,reportShow = 1)
surfUtils.create_radialCurveLoft(printHelp = 1)
self._l_ARGS_KWS_DEFAULTS = [{'kw':'crvToLoft',"default":None,
                              'help':"Curve which will be lofted"},
                             {'kw':'aimPointObject',"default":None,
                              'help':"Point object from which to loft"},
                             {'kw':'f_offset',"default":-.5,
                              'help':"Width of this new surface"},
                             
                             
convertCurve