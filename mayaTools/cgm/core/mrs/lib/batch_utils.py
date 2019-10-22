"""
------------------------------------------
cgm.core.mrs.lib.post_utils
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
# From Python =============================================================
import copy
import re
import pprint
import time
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel    

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import cgm.core.cgm_General as cgmGEN
import cgm.core.cgmPy.validateArgs as VALID
import cgm.core.cgmPy.path_Utils as PATHS
import cgm.core.mrs.RigBlocks as RIGBLOCKS
import cgm.core.mrs.lib.general_utils as BLOCKGEN

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.10212019'


def process_blocks_rig(f = None, blocks = None):
    _str_func = 'process_blocks_rig'
    #cgmGEN.log_start(_str_func)
    
    mFile = PATHS.Path(f)
    
    if not mFile.exists():
        raise ValueError,"Invalid file: {0}".format(f)
    
    _path = mFile.asFriendly()
    
    log.info("Good Path: {0}".format(_path))
    
    if 'template' in _path:
        _newPath = _path.replace('template','build')
    else:
        raise ValueError,"Invalid file | missing 'template' tag: {0}".format(f)

    log.info("New Path: {0}".format(_newPath))
    
    #cgmGEN.logString_msg(_str_func,'File Open...')
    mc.file(_path, open = 1, f = 1)
    
    #cgmGEN.logString_msg(_str_func,'Process...')
    
    if not blocks:
        #cgmGEN.logString_sub(_str_func,'No blocks arg')
        
        ml_masters = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',
                                         nTypes=['transform','network'],
                                         mAttrs='blockType=master')

        for mMaster in ml_masters:
            #cgmGEN.logString_sub(_str_func,mMaster)
    
            RIGBLOCKS.contextual_rigBlock_method_call(mMaster, 'below', 'atUtils','changeState','rig',forceNew=False)

            ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(mMaster,'below',True,False)
            l_fails = []
    
            for mSubBlock in ml_context:
                _state =  mSubBlock.getState(False)
                if _state != 4:
                    l_fails.append(mSubBlock)
                    
            if l_fails:
                log.info('The following failed...')
                pprint.pprint(l_fails)
                raise ValueError,"Modules failed to rig: {0}".format(l_fails)
    
            log.info("Begin Rig Prep cleanup...")
            '''
    
            Begin Rig Prep process
    
            '''
            mPuppet = mMaster.moduleTarget#...when mBlock is your masterBlock
            
            """
            log.info('mirror_verify...')
            mPuppet.atUtils('mirror_verify')
            log.info('collect worldSpace...')                        
            mPuppet.atUtils('collect_worldSpaceObjects')
            log.info('qss...')                        
            mPuppet.atUtils('qss_verify',puppetSet=1,bakeSet=1,deleteSet=1,exportSet=1)
            log.info('proxyMesh...')
            mPuppet.atUtils('proxyMesh_verify')
            log.info('ihi...')                        
            mPuppet.atUtils('rigNodes_setAttr','ihi',0)
            log.info('rig connect...')                        
            mPuppet.atUtils('rig_connectAll')"""

    #cgmGEN.logString_msg(_str_func,'File Save...')
    newFile = mc.file(rename = _newPath)
    mc.file(save = 1)        
      
