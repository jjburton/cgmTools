import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta
cgm.core._reload()
import cgm.core.mrs.RigBlocks as RBLOCKS
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.cgm_General as cgmGEN

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
rFac = BLOCKS.rigFactory(_block)
rFac._d_block['buildModule']

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
b1 = cgmMeta.createMetaNode('cgmRigBlock',blockType = 'head')
_block = 'cube_head_block'
b1 = cgmMeta.asMeta(_block)

mRigFac = RBLOCKS.rigFactory(b1)
cgmGEN.walk_dat(mRigFac.__dict__)
cgmGEN.log_info_dict(mRigFac.__dict__)
import pprint
pprint.pprint(mRigFac.__dict__)

mRigFac.log_self()#>>uses pprint

#Skeleton...
b1.atBlockModule('build_skeleton')

BLOCKUTILS.skeleton_buildRigChain(b1)
b1.atBlockModule('build_skeleton')
b1.atBlockModule('build_rigSkeleton')
b1.atBlockUtils('verify_dynSwitch')
b1.moduleTarget.isSkeletonized()
BLOCKUTILS.skeleton_buildRigChain(b1)
BLOCKUTILS.skeleton_buildHandleChain(b1)

pprint.pprint(vars())

mRigFac.atBlockModule('build_rigSkeleton')
