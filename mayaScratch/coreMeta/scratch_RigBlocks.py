import cgm.core.mrs.RigBlocks as BLOCKS
import cgm.core.mrs.Builder as BUILD

import cgm.core.cgm_Meta as cgmMeta

reload(RBLOCKS)

import cgm.core
reload(cgm.core)
cgm.core._reload()

_root = 'NotBatman_master_block'
mBlock = RBLOCKS.cgmRigBlock(blockType = 'master', size = 1)
mBlock = RBLOCKS.cgmRigBlock(_root)


#>>>Heirarchy ============================================================================
mBlock.getBlockParent()
mBlock.getBlockParent(False)
mBlock.p_blockParent = False
mBlock.p_blockParent = 'NotBatman_master_block1'
mBlock.getBlockRoot()
mBlock.p_blockRoot
mBlock.getParentMetaNode(mType = ['cgmRigBlock'])
mBlock.getChildMetaNodes(mType = ['cgmRigBlock'])
mBlock.getBlockChildren(True)

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
#>>>Blockshare data
#====================================================================================================
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
reload(BLOCKSHARE)
for a,v in BLOCKSHARE._d_attrsTo_make.iteritems():
    print "'{0}' - ({1})".format(a,v)

