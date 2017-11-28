import cgm.core.lib.snap_utils as SNAP
import maya.cmds as mc

reload(SNAP)
_mode = 'z+'
SNAP.get_snap_pos(mc.ls(sl=1), 'boundingBox',_mode)
SNAP.get_snap_pos(mc.ls(sl=1), 'boundingBoxShapes',_mode)
SNAP.get_snap_pos(mc.ls(sl=1), 'boundingBoxEach',_mode)
SNAP.get_snap_pos(mc.ls(sl=1), 'boundingBoxEachShapes',_mode)
SNAP.get_snap_pos(mc.ls(sl=1), 'castFar',_mode)
SNAP.get_snap_pos(mc.ls(sl=1), 'boundingBoxShapes',_mode)
SNAP.get_snap_pos(mc.ls(sl=1), 'boundingBoxEach',_mode)
SNAP.get_snap_pos(mc.ls(sl=1), 'boundingBoxEachShapes',_mode)
