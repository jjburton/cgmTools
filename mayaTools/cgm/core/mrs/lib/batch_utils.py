"""
------------------------------------------
cgm.core.mrs.lib.post_utils
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
# From Python =============================================================
import copy
import re
import pprint
import time
import os
import os.path
import sys
import subprocess, os
import datetime
from time import gmtime
from time import strftime

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
from cgm.core.tools import Project as PROJECT
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
import cgm.core.mrs.lib.post_utils as MRSPOST
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.10212019'


#MRSBATCH.process_blocks_rig('D:/Dropbox/cgmMRS/maya/batch/master_template_v01.mb')



def create_Scene_batchFile(dat = [], batchFile = None, process = True,
                           postProcesses = True, deleteAfterProcess = False):
    
    _str_func = 'create_Scene_batchFile'
    cgmGEN.log_start(_str_func)
    
    if batchFile is None:
        var_project = cgmMeta.cgmOptionVar('cgmVar_projectCurrent',defaultValue = '')
        
        mProject = PROJECT.data(filepath = var_project.value )
        
        d_paths = mProject.userPaths_get()
        
        mPath_root = PATHS.Path( d_paths['root'])
        if mPath_root.exists():
            log.debug('Root | : {0}'.format(mPath_root.asFriendly()))
            
        else:
            log.debug('Root | Invalid Path: {0}'.format(mPath_root))
            
        mPath_content = PATHS.Path( d_paths['content'])
        if os.path.exists(mPath_content):
            log.debug('Root | : {0}'.format(mPath_content))
        else:
            log.debug('Root | Invalid Path: {0}'.format(mPath_content))        
            
            
        _batchPath = os.path.join(mPath_root.asFriendly(),'mrsScene_batch.py')
    
        
    log.debug("batchFile : {0}".format(_batchPath))
    
    
    l_pre = ['import maya',
    'from maya import standalone',
    'standalone.initialize()',
    'from cgm.core.mrs import Scene',
    'import maya.mel as mel',
    'from maya.api import OpenMaya as om2',
    'om2.MGlobal.displayInfo("Begin")',
    'import maya.cmds as mc',
    'mc.loadPlugin("fbxmaya")',
    'mc.workspace("{0}",openWorkspace=1)'.format(mPath_content),
    'import cgm.core.mrs.lib.batch_utils as MRSBATCH',
    '']
    
    l_post = ['except Exception,err:',
              '    print err',
    '    import msvcrt#...waits for key',
    '    om2.MGlobal.displayInfo("Hit a key to continue")',
    '    msvcrt.getch()',
    '',
    'om2.MGlobal.displayInfo("End")',
    'standalone.uninitialize()'    ]
    
    log.debug(cgmGEN.logString_sub(_str_func,"Checks ..."))
    
    l_paths = []
    l_dirs = []
    #l_check = VALID.listArg(f)
    l_mFiles = []
    l_batch = []

    #if not l_check:
        #log.debug(cgmGEN.logString_msg(_str_func,"No file passed. Using current"))
        #l_check = [mc.file(q=True, sn=True)]
        

    _dat = ['dat = [']
    
    for d2 in dat:
        _dat.append('{')
        for k,d in d2.iteritems():
            if k == 'objs':
                if d:
                    _l_tmp = ','.join("'{0}'".format(o) for o in d)
                    _dat.append('"{0}" : [{1}],'.format(k,_l_tmp))
                else:
                    _dat.append("'objs' : [ ],")
            elif 'Path' in k:
                _l_tmp = ','.join("'{0}'".format(o) for o in d)
                _dat.append('"{0}" : [{1}],'.format(k,_l_tmp))                
            else:
                _dat.append('"{0}" : "{1}",'.format(k,d))
        _dat.append('},')
    _dat.append(']')
        
    mTar = PATHS.Path(_batchPath)
    _l = "try:Scene.BatchExport(dat)"
    
    #_l = "try:MRSBATCH.process_blocks_rig('{0}',postProcesses = {1})".format(mFile.asString(),postProcesses)
    
    if mTar.getWritable():
        if mTar.exists():
            os.remove(mTar)
            
        log.warning("Writing file: {0}".format(_batchPath))

        with open( _batchPath, 'a' ) as TMP:
            for l in l_pre + _dat + [_l] + l_post:
                TMP.write( '{0}\n'.format(l) )
                
        l_batch.append(mTar)
                
    else:
        log.warning("Not writable: {0}".format(_batchPath))    
        
        
    if process:
        log.debug(cgmGEN.logString_sub(_str_func,"Processing ..."))        
        log.warning("Processing file: {0}".format(mTar.asFriendly()))            
        #subprocess.call([sys.argv[0].replace("maya.exe","mayapy.exe"),f.asFriendly()])
        subprocess.Popen([sys.argv[0].replace("maya.exe",
                                              "mayapy.exe"),'-i',
                          mTar.asFriendly()],
                         creationflags = subprocess.CREATE_NEW_CONSOLE)# env=my_env
            
        if deleteAfterProcess:
            os.remove(f)
        
    return
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

def create_MRS_batchFile(f=None, blocks = [None], process = False,
                         postProcesses = True, deleteAfterProcess = False,
                         gatherOptionVars = True):
    _str_func = 'create_MRS_batchFile'
    cgmGEN.log_start(_str_func)
    
    l_pre = ['import maya',
    'from maya import standalone',
    'standalone.initialize()',
    
    'from maya.api import OpenMaya as om2',
    'om2.MGlobal.displayInfo("Begin")',
    'import maya.cmds as mc',
    'mc.loadPlugin("matrixNodes")',      
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
        _batchPath = os.path.join(_d,_name+'_MRSbatch.py')
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




l_mrsPost_order = ['mirrorVerify',
                   'gatherSpaceDrivers',
                   'connectRig',
                   'proxyMesh',
                   'puppetMesh',
                   'isHistoricallyInteresting',
                   'controllerVerify',
                   'blocksGather',
                   'blocksParent',
                   'deleteCGMLightGroup',
                   'hideJointAxis','deleteUnusedShaders','deleteUnusedLayers',
                   'hideVisSub',
                   'blocksDelete']

d_mrsPost_calls = {"recommended":['mirrorVerify','connectRig','controllerVerify','qss'],
                   "cleanup":['gatherSpaceDrivers','blocksGather','blocksParent','worldGather',
                              'hideJointAxis','hideVisSub'],
                   'delete':['deleteUnusedShaders','deleteUnusedLayers','removeRefs','deleteCGMLightGroup'],
                   'mesh':['proxyMesh','puppetMesh',],
                   'experimental':['isHistoricallyInteresting','blocksDelete']}

d_dat = {'qss':{'ann':"Setup expected qss sets", 'label':'Add Qss Sets'},
         'mirrorVerify':{'ann':"Wire for mirroring", 'label':'Mirror Verify'},
         'connectRig':{'ann':"Connect bind joints to rig joints", 'label':'Connect Rig'},
         'controllerVerify':{'ann':"Setup maya controller tags", 'label':'Controller Verify'},
         'gatherSpaceDrivers':{'ann':"Gather space drivers from dynParent setups",
                               'label':'Gather Space Drivers'},
         'deleteCGMLightGroup':{'ann':"Delete cgm Light Group", 'label':'Delete cgmLightGroup'},
         'blocksParent':{'ann':"Parent and hide Block Group", 'label':'Parent Block Group'},
         'hideVisSub':{'ann':"Hide the sub controls on blocks", 'label':'Hide Vis Sub'},
         
         'blocksGather':{'ann':"Gather rigBlocks to a single group", 'label':'Gather Blocks'},
         'worldGather':{'ann':"Try to gather loose dags parented to world", 'label':'Gather World Dags'},
         'removeRefs':{'ann':"Remove references", 'label':'Remove References'},
         'hideJointAxis':{'ann':"Hide all joint axis displays", 'label':'Hide Joint Axis'},
         'deleteUnusedShaders':{'ann':"Delete unused shaders", 'label':'Unused Shaders'},
         'deleteUnusedLayers':{'ann':"Delete unused layers", 'label':'Unused Layers'},
         'proxyMesh':{'ann':"Build proxy mesh and direct proxy controls", 'label':'Proxy Mesh'},
         'puppetMesh':{'ann':"Build puppet mesh", 'label':'Puppet Mesh'},
         'isHistoricallyInteresting':{'ann':"Turn off isHistoricallyInteresting", 'label':'IHI'},
         'blocksDelete':{'ann':"blocksDelete", 'label':'Blocks delete'},
         
         }

def process_blocks_rig(f = None, blocks = None, postProcesses = 1,**kws):
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
    T1 = time.time()
    
    get_time = cgmGEN.get_timeString

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
                

                #str(datetime.timedelta(seconds=v))

                if postProcesses:
                    l_timeReports = []
                    
                    if kws.get('mirrorVerify',1):
                        print(cgmGEN._str_hardBreak)                                                
                                                
                        log.info('mirror_verify...')
                        t1 = time.clock()
                        mPuppet.atUtils('mirror_verify',1)
                        t2 = time.clock()
                        l_timeReports.append(['mirrorVerify', get_time(t2-t1)
])
                        
                    if kws.get('gatherSpaceDrivers',1):
                        log.info('collect worldSpace...')
                        t1 = time.clock()                                                
                        mPuppet.atUtils('collect_worldSpaceObjects')
                        t2 = time.clock()
                        l_timeReports.append(['gatherSpaceDrivers', get_time(t2-t1)
])
                        
                    if kws.get('qss',1):
                        print(cgmGEN._str_hardBreak)                                                
                                                
                        log.info('qss...')
                        t1 = time.clock()                                                
                        mPuppet.atUtils('qss_verify',puppetSet=1,bakeSet=1,deleteSet=1,exportSet=1)
                        t2 = time.clock()
                        l_timeReports.append(['qss', get_time(t2-t1)
])
                        
                    if kws.get('deleteUnusedShaders'):
                        print(cgmGEN._str_hardBreak)                                                
                                                
                        log.info('Delete unused shaders...')
                        t1 = time.clock()
                        MRSPOST.shaders_getUnused(delete=True)
                        t2 = time.clock()
                        l_timeReports.append(['deleteUnusedShaders', get_time(t2-t1)])
                                              
                    if kws.get('deleteCGMLightGroup'):
                        print(cgmGEN._str_hardBreak)                                                
                                                
                        log.info('Delete cgm shaders...')
                        t1 = time.clock()
                        try:mc.delete('cgmLightGroup')
                        except:pass
                        
                        t2 = time.clock()
                        l_timeReports.append(['deleteUnusedShaders', get_time(t2-t1)])
                        
                        
                    if kws.get('hideVisSub',1):
                        print(cgmGEN._str_hardBreak)                                                
                        
                        log.info('hideVisSub...')
                        t1 = time.clock()
                        
                        for i,mSubBlock in enumerate(ml_context):
                            if not i:
                                continue
                            try:
                                mSubBlock.moduleTarget.rigNull.settings.visSub = 0
                            except Exception,err:
                                log.error(mSubBlock)
                                log.error(err)

                        
                        t2 = time.clock()
                        l_timeReports.append(['hideVisSub', get_time(t2-t1)])
                        
                    if kws.get('hideJointAxis'):
                        print(cgmGEN._str_hardBreak)                                                
                                                
                        log.info('Hide axis on all joints...')   
                        t1 = time.clock()
                        
                        for mObj in cgmMeta.asMeta(mc.ls(type='joint')):
                            mObj.displayLocalAxis = 0
                        t2 = time.clock()
                        l_timeReports.append(['hideJointAxis', get_time(t2-t1)
])
                        
                    if kws.get('removeRefs'):
                        print(cgmGEN._str_hardBreak)                                                
                                                
                        log.info('Remove Refs...')
                        t1 = time.clock()
                        
                        MRSPOST.refs_remove()
                            
                        t2 = time.clock()
                        l_timeReports.append(['removeRefs', get_time(t2-t1)
])                    
                    if kws.get('ihi',1):
                        print(cgmGEN._str_hardBreak)                                                
                                                
                        log.info('ihi...')
                        t1 = time.clock()
                        
                        mPuppet.atUtils('rigNodes_setAttr','ihi',0)
                        
                        t2 = time.clock()
                        l_timeReports.append(['ihi', get_time(t2-t1)
])                        
                    if kws.get('connectRig',1):
                        print(cgmGEN._str_hardBreak)                                                
                                                
                        log.info('rig connect...')
                        t1 = time.clock()
                        
                        mPuppet.atUtils('rig_connectAll')
                        
                        t2 = time.clock()
                        l_timeReports.append(['connectRig', get_time(t2-t1)
])                        
                    log.info('...')
                    
                    if kws.get('controllerVerify',1):
                        print(cgmGEN._str_hardBreak)                                                
                                                
                        if cgmGEN.__mayaVersion__ >= 2018:
                            log.info('controller_verify...')
                            t1 = time.clock()
                            
                            mPuppet.atUtils('controller_verify')
                            log.info('...')
                            
                            t2 = time.clock()
                            l_timeReports.append(['controllerVerify', get_time(t2-t1)
])                            
                    
                    if kws.get('blocksGather',1):
                        print(cgmGEN._str_hardBreak)                                                
                                                
                        t1 = time.clock()
                        mGrp = BUILDERUTILS.gather_rigBlocks()
                        
                        if kws.get('blocksParent',1):
                            mGrp.p_parent = mPuppet                        
                            mGrp.v = False
                        t2 = time.clock()
                        l_timeReports.append(['blocksGather', get_time(t2-t1)])
                                              

                    if kws.get('proxyMesh',1):
                        print(cgmGEN._str_hardBreak)                                                

                        log.info('proxyMesh...')
                        t1 = time.clock()                        
                        mPuppet.atUtils('proxyMesh_verify',1)
                        t2 = time.clock()
                        l_timeReports.append(['proxyMesh', get_time(t2-t1)])
                        
                    if kws.get('puppetMesh',1):
                        print(cgmGEN._str_hardBreak)                                                
                        
                        log.info('puppetMesh...')
                        t1 = time.clock()                                                
                        mPuppet.atUtils('puppetMesh_create', **{'unified':True,'skin':True, 'proxy':True})
                        t2 = time.clock()
                        l_timeReports.append(['puppetMesh', get_time(t2-t1)])

                        
                    if kws.get('worldGather'):
                        print(cgmGEN._str_hardBreak)                                                
                                                
                        log.info('Gathering world dags...')
                        t1 = time.clock()
                        
                        MRSPOST.gather_worldStuff()
                        t2 = time.clock()
                        l_timeReports.append(['worldGather', get_time(t2-t1)
])                    
                    
                    if kws.get('deleteUnusedLayers'):
                        print(cgmGEN._str_hardBreak)                                                
                        log.info('Deleting Unused Layers...')
                        t1 = time.clock()
                        
                        MRSPOST.layers_getUnused(delete=True)
                        t2 = time.clock()
                        l_timeReports.append(['deleteUnusedLayers', get_time(t2-t1)
])
                    print(cgmGEN._str_hardBreak)            
                    print(cgmGEN.logString_sub("Batch",'Times'))
                    for i,pair_time in enumerate(l_timeReports):
                        print(" {0} | ['{1}'] | {2} ".format(i,pair_time[0],pair_time[1]))
                    print ('Completed: {}'.format(datetime.datetime.now()))                        

    except Exception,err:
        log.error(err)
        
        
    T2 = time.time()
    log.info("|{0}| >> Total Time >> = {1} seconds".format(_str_func, get_time(T2-T1))) 
    

    #cgmGEN.logString_msg(_str_func,'File Save...')
    newFile = mc.file(rename = _newPath)
    mc.file(save = 1)
    log.info(newFile)
      
