import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta

import cgm.core.mrs.RigBlocks as RBLOCKS
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.cgm_General as cgmGEN
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
reload(BLOCKSHARE)
cgm.core._reload()

_root = 'NotBatman_master_block'
mBlock = RBLOCKS.cgmRigBlock(blockType = 'master', size = 1)
mBlock = RBLOCKS.cgmRigBlock(_root)

RBLOCKS.get_modules_dat()#...also reloads

#====================================================================================================
#>>>Blockshare data
#====================================================================================================
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
reload(BLOCKSHARE)
for a,v in BLOCKSHARE._d_attrsTo_make.iteritems():
    print "'{0}' - ({1})".format(a,v)

b1 = cgmMeta.createMetaNode('cgmRigBlock',blockType = 'head')
_block = 'cube_head_block'
b1 = cgmMeta.asMeta(_block)

b1.changeState('define')
b1.changeState('template')
b1.changeState('prerig')

b1.getState()
cgm.core._reload()
rFac = RBLOCKS.rigFactory(_block)
rFac.d_block['buildModule']

rFac.buildModule.build_shapes(i_rig)
rFac.buildModule.build_rigSkeleton(i_rig)
rFac.buildModule.build_controls(i_rig)
rFac.buildModule.build_deformation(i_rig)
rFac.buildModule.build_rig(i_rig)


#>>>Data ================================================================================
mBlock.getBlockAttributes()
mBlock.p_blockAttributes

#====================================================================================================
#>>>BlockFactory
#====================================================================================================
BlockFactory = RBLOCKS.factory(_root)
BlockFactory.get_infoBlock_report()

#>>>State changes ============================================================================
mBlock.getState()
BlockFactory.template()
BlockFactory.templateDelete()

BlockFactory.changeState('template')
BlockFactory.changeState('define')

#====================================================================================================
#>>>Utilities
#====================================================================================================
RBLOCKS.get_blockModule('master')


#====================================================================================================
#>>>Rig building
#====================================================================================================
import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta
import cgm.core.cgm_General as cgmGEN
import cgm.core.mrs.RigBlocks as RBLOCKS
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as  BUILDUTILS
import cgm.core.cgm_General as cgmGEN
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.lib.transform_utils as TRANS

cgm.core._reload()
from Red9.core import Red9_Meta as r9Meta
r9Meta.MetaClass(_block)
RBLOCKS.cgmRigBlock(_block)


from cgm.core import cgm_Meta as cgmMeta
import cgm.core.mrs.RigBlocks as RBLOCKS
RBLOCKS.get_modules_dat()#...also reloads

b1 = cgmMeta.createMetaNode('cgmRigBlock',blockType = 'head')
b1 = cgmMeta.asMeta(_block)

b1 = cgmMeta.asMeta('L_thumb_limbBlock')#...end, no lever setup

mMirror = b1.atUtils('blockMirror_create')

b1.atUtils('blockMirror_create')
b1.atUtils('blockMirror_go')
b1.atUtils('controls_mirror')

b1.atUtils('blockDat_get')
b1.atUtils('blockDat_save')
b1.atUtils('blockDat_load')