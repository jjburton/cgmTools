import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta

import cgm.core.mrs.RigBlocks as RBLOCKS
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.cgm_General as cgmGEN
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
reload(BLOCKSHARE)
cgm.core._reload()

RBLOCKS.get_modules_dat()#...also reloads

b1 = RBLOCKS.cgmRigBlock(blockType = 'handle')
b1 = cgmMeta.asMeta('handle_block')
b1.p_blockState = 'define'
b1.p_blockState = 'template'
b1.p_blockState = 'prerig'

reload(cgm.core.lib.rigging_utils)

import cgm.core.lib.curve_Utils as CURVES
reload(CURVES)
CURVES.create_fromName('squareOpen', size = 1)
CURVES.create_controlCurve(b1.mNode, 'circle')



#>>>Skeleton ---------------------------------------------------------------------------------------
b1.atBlockModule('build_skeleton')
b1.atBlockUtils('skeleton_getCreateDict')

#>>>Rig process
b1.verify()
mRigFac = RBLOCKS.rigFactory(b1)
mRigFac.log_self()#>>uses pprint
mRigFac.mRigNull.fkHeadJoint
pprint.pprint(b1.__dict__)
mRigFac.mRigNull.headFK.dynParentGroup
mRigFac.atBlockModule('rig_skeleton')

mRigFac.atBlockModule('build_proxyMesh', False)#must have rig joints


mRigFac.atBlockModule('rig_shapes')
mRigFac.atBlockModule('rig_controls')
mRigFac.atBlockModule('rig_neckSegment')
mRigFac.atBlockModule('rig_frame')
mRigFac.atBlockModule('rig_cleanUp')

import cgm.core.lib.attribute_utils as ATTR
ATTR.datList_connect(b1.mNode, 'baseNames', ['head'], mode='string')