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
import sys
import subprocess, os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

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




    #MRSBATCH.process_blocks_rig('D:/Dropbox/cgmMRS/maya/batch/master_template_v01.mb')


def create_MRS_batchFile(f=None, blocks = [None], process = False,
                         postProcesses = True, deleteAfterProcess = False):
    _str_func = 'create_MRS_batchFile'
    cgmGEN.log_start(_str_func)
    
    l_pre = ['import maya',
    'from maya import standalone',
    'standalone.initialize()',
    
    'from maya.api import OpenMaya as om2',
    'om2.MGlobal.displayInfo("Begin")',
    
    'import cgm.core.mrs.lib.batch_utils as MRSBATCH']
    
    l_post = ['except:',
    '    import msvcrt#...waits for key',
    '    om2.MGlobal.displayInfo("Hit a key to continue")',
    '    msvcrt.getch()',
    'om2.MGlobal.displayInfo("End")',
    'standalone.uninitialize()'    ]
    
    log.debug(cgmGEN.logString_sub(_str_func,"Checks ..."))
    
    l_paths = []
    l_dirs = []
    l_check = VALID.listArg(f)
    l_mFiles = []
    l_batch = []
    if not l_check:
        log.debug(cgmGEN.logString_msg(_str_func,"No file passed. Using current"))
        l_check = [mc.file(q=True, sn=True)]
        
    
    for f in l_check:
        mFile = PATHS.Path(f)
        if not mFile.exists():
            log.error("Invalid file: {0}".format(f))
            continue
        
        log.debug(cgmGEN.logString_sub(_str_func))
        
        _path = mFile.asFriendly()
        l_paths.append(_path)
        _name = mFile.name()
        
        _d = mFile.up().asFriendly()
        log.debug(cgmGEN.logString_msg(_str_func,_name))
        _batchPath = os.path.join(_d,_name+'_batch.py')
        log.debug(cgmGEN.logString_msg(_str_func,"batchPath: "+_batchPath))
        log.debug(cgmGEN.logString_msg(_str_func,"template: "+_path))
        
        
        mTar = PATHS.Path(_batchPath)
        _l = "try:MRSBATCH.process_blocks_rig('{0}',postProcesses = {1})".format(mFile.asString(),postProcesses)
        
        if mTar.getWritable():
            if mTar.exists():
                os.remove(mTar)
                
            log.warning("Writing file: {0}".format(_batchPath))
 
            with open( _batchPath, 'a' ) as TMP:
                for l in l_pre + [_l] + l_post:
                    TMP.write( '{0}\n'.format(l) )
                    
            l_batch.append(mTar)
                    
        else:
            log.warning("Not writable: {0}".format(_batchPath))
            
    
    if process:
        log.debug(cgmGEN.logString_sub(_str_func,"Processing ..."))        
        for f in l_batch:
            log.warning("Processing file: {0}".format(f.asFriendly()))            
            #subprocess.call([sys.argv[0].replace("maya.exe","mayapy.exe"),f.asFriendly()])
            subprocess.Popen([sys.argv[0].replace("maya.exe",
                                                  "mayapy.exe"),'-i',
                              f.asFriendly()],
                             creationflags = subprocess.CREATE_NEW_CONSOLE)# env=my_env
            
            if deleteAfterProcess:
                os.remove(f)
        

    '''
    def isInstalledPy( self, pyUserSetup ):
        
        
        l_lines = ['import cgmToolbox','import cgm.core.tools.lib.tool_chunks as TOOLCHUNKS','TOOLCHUNKS.loadLocalPython()']
        l_found = []
        l_missing = []
        with open( pyUserSetup ) as f:
            for i,codeLine in enumerate(l_lines):
                for line in f:
                    if codeLine in line:
                        l_found.append(codeLine)
                        break
                if codeLine not in l_found:
                    l_missing.append(codeLine)
        log.info("Found: %s"%l_found)
        if l_missing:
            log.info("Failed to find: %s"%l_missing)
            return l_missing
        return True		
        """with open( pyUserSetup ) as f:
            for line in f:
                if 'import' in line and 'cgmToolbox' in line:
                    return True
        return False"""

    def installPy( self, pyUserSetup ):
        buffer = self.isInstalledPy( pyUserSetup )
        if buffer == True:
            return

        if pyUserSetup.getWritable():
            with open( pyUserSetup, 'a' ) as f:
                for l in buffer:
                    f.write( '\n\n {0}\n'.format(l) )	
                else:
                    raise self.AutoSetupError( "%s isn't writeable - aborting auto setup!" % pyUserSetup ) '''   

def process_blocks_rig(f = None, blocks = None, postProcesses = False):
    _str_func = 'process_blocks_rig'
    #cgmGEN.log_start(_str_func)
    
    mFile = PATHS.Path(f)
    
    if not mFile.exists():
        raise ValueError,"Invalid file: {0}".format(f)
    
    _path = mFile.asFriendly()
    
    log.info("Good Path: {0}".format(_path))
    """
    if 'template' in _path:
        _newPath = _path.replace('template','build')
    else:"""
    _name = mFile.name()
    _d = mFile.up().asFriendly()
    log.debug(cgmGEN.logString_msg(_str_func,_name))
    _newPath = os.path.join(_d,_name+'_BUILD.{0}'.format(mFile.getExtension()))        

    log.info("New Path: {0}".format(_newPath))
    
    #cgmGEN.logString_msg(_str_func,'File Open...')
    mc.file(_path, open = 1, f = 1)
    
    #cgmGEN.logString_msg(_str_func,'Process...')
    t1 = time.time()
    
    try:
        
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
                
                
                if postProcesses:
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
    except Exception,err:
        log.error(err)
        
        
    t2 = time.time()
    log.info("|{0}| >> Total Time >> = {1} seconds".format(_str_func, "%0.4f"%( t2-t1 ))) 
    

    #cgmGEN.logString_msg(_str_func,'File Save...')
    newFile = mc.file(rename = _newPath)
    mc.file(save = 1)        
      
