"""
Maya be Odd
Josh Burton 
www.cgmonastery.com

For use with meta instance data
"""
__MAYALOCAL = 'MAYABEODD'

# From Python =============================================================
import copy
import re
import subprocess, os
import sys
import pprint
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core import cgm_Meta as cgmMeta

from cgm.lib import attributes
from cgm.core.lib import attribute_utils as coreAttr
import cgm.core.cgmPy.path_Utils as PATHS
import cgm.core.cgmPy.os_Utils as CGMOS

#>>> Utilities
#===================================================================
def killRoguePanel(method = ''):
    """
    hattip:
    https://forums.autodesk.com/t5/maya-forum/error-cannot-find-procedure-quot-dcf-updateviewportlist-quot/td-p/8342659?fbclid=IwAR3IhCeCqzZvEREmxo5eA7ECQu9n82MEN_vqCFTmdySwNNbsrYREdDcv_QA
    """
    #['DCF_updateViewportList', 'CgAbBlastPanelOptChangeCallback']
    EVIL_METHOD_NAMES = cgmValid.listArg(method)
    pprint.pprint(EVIL_METHOD_NAMES)
    capitalEvilMethodNames = [name.upper() for name in EVIL_METHOD_NAMES]
    modelPanelLabel = mel.eval('localizedPanelLabel("ModelPanel")')
    processedPanelNames = []
    panelName = mc.sceneUIReplacement(getNextPanel=('modelPanel', modelPanelLabel))
    while panelName and panelName not in processedPanelNames:
        log.info(cgmGEN.logString_sub("Checking: ",panelName))
        editorChangedValue = mc.modelEditor(panelName, query=True, editorChanged=True)
        parts = editorChangedValue.split(';')
        newParts = []
        changed = False
        for part in parts:
            log.info("Part: {}".format(part))
            for evilMethodName in capitalEvilMethodNames:
                if evilMethodName in part.upper():
                    changed = True
                    break
            else:
                newParts.append(part)
        if changed:
            mc.modelEditor(panelName, edit=True, editorChanged=';'.join(newParts))
        processedPanelNames.append(panelName)
        panelName = mc.sceneUIReplacement(getNextPanel=('modelPanel', modelPanelLabel))
        log.info("Processed: {} | Found: {}".format(panelName,changed))
        


def cleanFile():
    kill_unknownPlugins()
    kill_rendererNodes()
    
def kill_unknownPlugins():
    """
    Hat tip to Ryan Porter
    """
    for each in mc.unknownPlugin(q=1, l=1) or []:
        mc.unknownPlugin(each, remove=True)
        
    
def kill_rendererNodes():
    for o in ['TurtleDefaultBakeLayer']:
        if mc.objExists(o):
            cgmMeta.asMeta(o).delete()
            print "killed node: " + o
            
def kill_outlinerSelectCommands():
    #https://forums.autodesk.com/t5/maya-forum/error-lt-function-selcom-at-0x7f29c5c04aa0-gt/td-p/9052236
    for _editor in mc.lsUI(editors=True):
        if not mc.outlinerEditor(_editor, query=True, exists=True):
            continue
        _sel_cmd = mc.outlinerEditor(_editor, query=True, selectCommand=True)
        if not _sel_cmd:
            continue
        print _editor, _sel_cmd
        mc.outlinerEditor(_editor, edit=True, selectCommand='print "";')
        
def mayaScanner_path(path = None):
    #Credit - Theodox - https://discourse.techart.online/t/another-maya-malware-in-the-wild/12970/6
    # usage :
    # mayapy.exe  quick_scan.py   path/to/directory/to/scan
    # recursively scanes all maya files in path/to/directory/to/scan 
    
    file_list = []
    cleanList = []
    d_exeptions = {}
    counter = 0
    print ("Checking: {}".format(path))
    
    for root, _, files in os.walk(path):
        for mayafile in files:
            lower = mayafile.lower()
            if lower.endswith(".ma") or lower.endswith(".mb"):
                counter += 1
                abspath = os.path.join(root, mayafile)
                log.info("scanning {}".format(abspath))
                if file_list:
                    log.info("filenodes found in {} files".format(len(file_list)))
                try:
                    mc.file(abspath, open=True, f=True, iv=True)
                    mc.MayaScan(scanType=0)
                except Exception,err:
                    d_exeptions[abspath] = '{}'.format(err)
                    continue
                
                scriptnodes = mc.ls(type='script')
                
                
                """"""
                # almost all Maya files will contain two nodes named
                # 'sceneConfigurationScriptNode' and 'uiConfigurationScriptNode'
                # a proper job wouldd make sure that they contained only trivial MEL 
                # but youd have to really inspect the contents to make sure
                # a smart attacker hadn't hidden inside those nodes.  For demo purposes
                # I'm just ignoring them but that is a clear vulnerability"""
    
                if len(scriptnodes) > 2:
                    # here's where you'd want to nuke and resave the file if you were really cleaning house,
                    # or you could loop through them applying your own safety test
                    log.warning("file {} contains {} scriptnodes".format(abspath, len(scriptnodes) - 2 ))
                    file_list.append(abspath)
                else:
                    cleanList.append(abspath)
    
    print(cgmGEN._str_hardBreak)
    print("scanned {} files".format(counter))

    if cleanList:
        print("No script nodes:")
        for i,f in enumerate(cleanList):
            print("{} | {}".format(i,f))
    if file_list:
        log.warning ("=" * 72)
        log.warning ("filenodes found in the following. Might be worth a look:")
        for i,f in enumerate(file_list):
            print("{} | {}".format(i,f))
    if d_exeptions:
        log.error ("=" * 72)
        log.error ("Exceptions")
        for f,e in d_exeptions.iteritems():
            print("{} | {}".format(f,e))           
    print(cgmGEN._str_hardBreak)

            
def mayaScanner_batch(path= None, process=True):
    _str_func = 'mayaScanner_batch'
    cgmGEN.log_start(_str_func)
    
    #Let's get our Target dir...
    if not path:
        #path = cgmValid.filepath(None, 2, None)
        path = mc.fileDialog2(fileFilter='', dialogStyle=2, fm=3)
        if path:
             path = path[0]
        else:return log.error(cgmGEN.logString_msg(_str_func,"No path"))
        
    log.info(cgmGEN.logString_msg(_str_func,"path: {}".format(path)))
    
    mPath_root = PATHS.Path( path)
    _batchPath = os.path.join(mPath_root.asFriendly(),'batch_mayaScanner.py')
    mTar = PATHS.Path(_batchPath)
    log.info("batchFile : {0}".format(_batchPath))
    _check_path = mPath_root.asFriendly()
    
    #Let's pick where to put our file
    
    l_pre = [
    'import maya.standalone',
    'maya.standalone.initialize()',
    
    'from maya.api import OpenMaya as om2',            
    'om2.MGlobal.displayInfo("Begin")',
    'import sys',
    'import time',
    #'logger = logging.getLogger("mayascan")',
    #'time.sleep(3)',
    #'logger.setLevel(logging.INFO)',
    'om2.MGlobal.displayInfo("MAYAODD")',    
    'import cgm.core.lib.mayaBeOdd_utils as MAYAODD',
    'reload(MAYAODD)',
    #'time.sleep(3)',    
    'om2.MGlobal.displayInfo("Os")',    
    'import os',
    'os.environ["MAYA_SKIP_USER_SETUP"] = "1"',
    #'logger.info("usersetup disabled")',
    #'logger.info("maya initialized")',
    #'time.sleep(3)',    
    'import maya.cmds as mc',
    'mc.optionVar(iv= ("fileExecuteSN", 0))',
    #'logger.info("scriptnodes disabled")',
    #'time.sleep(3)',
    'mc.loadPlugin("MayaScanner")',
    'om2.MGlobal.displayInfo("Go")',
]
    
    l_post = ['except Exception,err:',
              '    print err',
    '    import msvcrt#...waits for key',
    '    om2.MGlobal.displayInfo("Hit a key to continue")',
    '    msvcrt.getch()',
    '',
    'om2.MGlobal.displayInfo("End")',]
    #'standalone.uninitialize()'    ]
    
    
    _l = "try:MAYAODD.mayaScanner_path('" + path + "')"
    
    
    if mTar.getWritable():
        if mTar.exists():
            os.remove(mTar)
            
        log.warning("Writing file: {0}".format(_batchPath))

        with open( _batchPath, 'a' ) as TMP:
            for l in l_pre + [_l] + l_post:
                TMP.write( '{0}\n'.format(l) )
                
    else:
        log.warning("Not writable: {0}".format(_batchPath))    
        
        
    if process:
        log.debug(cgmGEN.logString_sub(_str_func,"Processing ..."))        
        log.warning("Processing file: {0}".format(mTar.asFriendly()))            
        subprocess.Popen([sys.argv[0].replace("maya.exe",
                                              "mayapy.exe"),'-i',
                          mTar.asFriendly()],
                         creationflags = subprocess.CREATE_NEW_CONSOLE)# env=my_env
            
        #if deleteAfterProcess:
        #    os.remove(f)    
    
    return
    