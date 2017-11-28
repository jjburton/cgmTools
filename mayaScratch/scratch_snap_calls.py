import cgm.core.tools.snapTools as SNAPTOOLS
import maya.cmds as mc

reload(SNAPTOOLS)

_sel = mc.ls(sl=True)
_d = {'objPivot':'rp',
      'targetPivot':'rp',
      'mode':'boundingBoxAll',
      'position':True,
      'rotation':True,
      'rotateAxis':False,
      'rotateOrder':False,
      'scalePivot':False,}
targetPivot = 'rp'
targetPivot = 'closestPoint'
targetPivot = 'boundingBox'
targetPivot = 'groundPos'
targetPivot = 'castCenter'
targetPivot = 'castFar'
targetPivot = 'castNear'
targetPivot = 'axisBox'
reload(SNAPTOOLS)

SNAPTOOLS.snap(_sel[0],_sel[1],targetPivot = targetPivot)
SNAPTOOLS.snap(_sel[0],None,targetPivot = targetPivot)
SNAPTOOLS.snap(_sel[0],_sel[1:],targetPivot = targetPivot)

#------------------------------------------------------------------
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import maya.cmds as mc

reload(SNAPCALLS)
_mode = 'z+'
_mode = 'x-'
_mode = 'y-'
_mode = 'center'
_mode = 'center'

reload(SNAPCALLS)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'localAxisBox',_mode)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'boundingBox',_mode)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'boundingBoxShapes',_mode)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'boundingBoxEach',_mode)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'boundingBoxEachShapes',_mode)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'castCenter',_mode)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'castFar',_mode)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'cast',_mode)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'groundPos',_mode)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'boundingBoxEach',_mode)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'boundingBoxEachShapes',_mode)
SNAPCALLS.get_special_pos(mc.ls(sl=1), 'localAxisBox',_mode)




#-------------------------------------------------------------------------------------
import cgm.core.lib.distance_utils as DIST
reload(DIST)
_mode = 'bottom'
DIST.get_axisBox_pos(mc.ls(sl=1)[0], _mode)
mc.duplicate(mc.ls(sl=1),po=False)
import cgm.core.lib.rigging_utils as CORERIG
reload(CORERIG)
CORERIG.create_localAxisProxy()
CORERIG.create_localAxisProxy(mc.ls(sl=1)[0])
mc.parent('Box01_GEO2_localAxisProxy','Box01_GEO',r=True)

import cgm.core.lib.attribute_utils as ATTR
ATTR.set('curve1_localAxisProxy','scale',[11.456766206699672, 23.229830177917137, 11.456766206699672])