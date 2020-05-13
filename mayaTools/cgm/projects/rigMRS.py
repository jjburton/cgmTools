##Export Rig as Batch process
import maya.cmds as mc
import maya.mel as ml
import sys

import logging
import pprint
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

#For logging Debug
#log.setLevel(logging.DEBUG)
'''
from cgm.core.mrs import RigBlocks as RIGBLOCKS
from Red9.core import Red9_Meta as r9Meta

from cgm.core import cgm_General as cgmGEN

@cgmGEN.Timer
'''
from Red9.core import Red9_Meta as r9Meta
import cgm

from cgm.core.mrs import RigBlocks as RIGBLOCKS

import cgm.core.cgm_General as cgmGEN
from cgm.core.mrs.lib import general_utils as BLOCKGEN


@cgmGEN.Timer
def createMRSRig(folderPath):
    cgm.core._#reload()

    fileList = mc.getFileList(folder = folderPath)

    if not folderPath.endswith('\\') :
        folderPath = folderPath + '\\'

    if not 'MRSRigs' in mc.getFileList(folder = folderPath) :
        mc.sysFile(folderPath + 'MRSRigs', md = 1)
        newFolderPath = folderPath + 'MRSRigs\\'
        
    for _file in fileList :
        try:
            if(_file.endswith('.ma')) :

                mc.file(folderPath + _file, open = 1, f = 1)

                log.info("Working on... " + _file)

                ml_masters = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',nTypes=['transform','network'],mAttrs='blockType=master')

                for mBlock in ml_masters:
                   
                    log.info(mBlock)

                    RIGBLOCKS.contextual_rigBlock_method_call(mBlock, 'below', 'atUtils', 'changeState','rig',forceNew=False)
                    mBlock.moduleTarget#<< link to puppet
               
                    '''
                    This is the start of the puppet calls

                    '''
                    

                    #If more than one Rig exists Do:
                    #if len(ml_masters):raise ValueError,"Too many masters: {0}".format(ml_masters)



                    #rig call if you prefer as a for loop: build rig, check rig
                    ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,'below',True,False)
                    pprint.pprint(ml_context)


                    log.info('Begin Rig Build')

                    ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,'below',True,False)
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

                    mPuppet = mBlock.moduleTarget#...when mBlock is your masterBlock
                    
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
                    mPuppet.atUtils('rig_connectAll')

                #Save the scene in the new folder.

                log.info("Saving out the new scene...")

                newFile = mc.file(rename = newFolderPath + _file.split('_template')[0] + "_rig.ma")
                mc.file(save = 1, type = 'mayaAscii')

                log.info("Saved new scene " + newFile)


            else :
                log.info("There was an error creating new file...")
        except Exception,err:
            log.error("File failed: {0}".format(_file))
            cgmGEN.cgmException(Exception,err)
                