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
reload(TRANS)
reload(BLOCKSHARE)
reload(RBLOCKS)
reload(BLOCKUTILS)
cgm.core._reload()
from Red9.core import Red9_Meta as r9Meta
r9Meta.MetaClass(_block)
RBLOCKS.cgmRigBlock(_block)


from cgm.core import cgm_Meta as cgmMeta
import cgm.core.mrs.RigBlocks as RBLOCKS
RBLOCKS.get_modules_dat()#...also reloads

b1 = cgmMeta.createMetaNode('cgmRigBlock',blockType = 'head')
_block = 'head_block'
b1 = cgmMeta.asMeta(_block)

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

mRigFac.atBuilderUtils('shapes_fromCast',mode ='segmentHandle',uValues = [.2])



import cgm.core.rig.ik_utils as IK
_d = {'jointList' : [u'neck_base_ik_frame',
                     u'neck_base_ik_1_frame',
                     u'neck_base_ik_2_frame',
                     u'head_base_ik_frame'],
      'useCurve' : None,
      'orientation' : 'zyx',
      'secondaryAxis' : 'y+',
      'baseName' : None,
      'stretchBy' : 'translate',
      'advancedTwistSetup' : True,
      'extendTwistToEnd' : False,
      'reorient' : False,
      'moduleInstance' : None,
      'parentGutsTo' : None}
IK.spline(**_d)