"""
------------------------------------------
arrange_utils: cgm.core.lib.distance_utils
Author: Josh Burton
email: cgmonks.info@gmail.com
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

"""
__MAYALOCAL = 'ARRANGE'

# From Python =============================================================
import copy
import re
import sys
import os
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
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.cgmPy.path_Utils as PATHS

#>>> Utilities
#===================================================================
def walk_below_dir(arg = None, tests = None,uiStrings = True,
                   fileTest=None, fileCount = True, hardCap = 20,
                   skipRoot = True, 
                   l_mask=['.svn','pristine']):
    """
    Walk directory for pertinent info

    :parameters:

    :returns
        _d_modules, _d_categories, _l_unbuildable
        _d_modules(dict) - keys to modules
        _d_categories(dict) - categories to list of entries
        _l_unbuildable(list) - list of unbuildable modules
    """
    _str_func = 'walk_below'       
    
    _b_debug = log.isEnabledFor(logging.DEBUG)

    _path = PATHS.Path(arg)
    if not _path.exists():
        log.debug(cgmGEN.logString_msg(_str_func,"Path doesn't exists: {0}".format(arg)))
        return False
    
    _l_duplicates = []
    _l_unbuildable = []
    _base = _path.split()[-1]
    #_d_files =  {}
    #_d_modules = {}
    #_d_import = {}
    #_d_categories = {}
    _d_levels = {}
    _d_dir = {}
    _l_keys = []
    
    if uiStrings:
        log.debug("|{0}| >> uiStrings on".format(_str_func))           
        _d_uiStrings = {}
        _l_uiStrings = []
    
    log.debug("|{0}| >> Checking base: {1} | path: {2}".format(_str_func,_base,_path))   
    _i = 0
    
    _rootKey = None
    for root, dirs, files in os.walk(_path, True, None):

        if hardCap and _i > hardCap:
            log.warning(cgmGEN.logString_msg(_str_func,"hit cap...{0}".format(hardCap)))
            break

        _rootPath = PATHS.Path(root)
        _split = _rootPath.split()
        _subRoot = _split[-1]
        _splitUp = _split[_split.index(_base):]
        _depth = len(_splitUp) - 1
        
        if _path == root:
            _rootKey = _split[-1]

            if skipRoot:
                log.debug(cgmGEN.logString_msg(_str_func,"Skipping root"))
                continue

        log.debug(cgmGEN.logString_sub(_str_func,_subRoot))
        
        if _subRoot[0] in ['.']:
            log.debug(cgmGEN.logString_msg(_str_func,"Skipping...{0}".format(_subRoot)))
            continue
        elif _subRoot in l_mask:
            log.debug(cgmGEN.logString_msg(_str_func,"Masked...{0}".format(_subRoot)))
            continue
        
        if l_mask:
            _break = False
            for v in l_mask:
                if v in _splitUp:
                    log.debug(cgmGEN.logString_msg(_str_func,"Masked...{0}".format(_rootPath)))
                    _break = True
                    continue
            
            if _break:
                continue
        
        
        log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        #log.debug("|{0}| >> On split up: {1}".format(_str_func,_splitUp))
        #log.debug("|{0}| >> On split: {1}".format(_str_func,_split))
        
        _splitRoot = _split[_split.index(_rootKey)+1:]
        _key = '|||'.join(_splitRoot)#_rootPath.asString()
        _l_keys.append(_key)
        

            
        _d_dir[_key] = {'depth':_depth,
                        'split':_split,
                        'splitRoot':_splitRoot,
                        'token':_subRoot,
                        'pyString':_rootPath.asFriendly(),
                        'raw':root,
                        'mPath':_rootPath,
                        'dir':dirs,
                        'index':_i,
                        'key':_key,
                        'files':files}
        
        if uiStrings:
            if _depth > 1:
                _Root = _splitRoot[:-1]
                _Root.reverse()
                _uiString = '  '*(_depth) + " {0} ".format(_subRoot) + '    \\\\' + '.'.join(_Root)
                
                #_reverseRoot = _splitRoot[:-1]
                #_reverseRoot.reverse()
                #_uiString = '   '*(_depth) + '>' + '--' + '{0}'.format(_subRoot) + "      {0}".format('.'.join(_reverseRoot))
            else:
                _uiString = " || "+ _subRoot
            
            if files:
                if fileTest and fileTest.get('endsWith'):
                    _cnt = 0
                    for f in files:
                        if f.endswith(fileTest.get('endsWith')):
                            _cnt +=1
                elif fileCount:
                    _cnt = len(files)
                    
                _uiString = _uiString + ' ({0})'.format(_cnt)
                    
                
            #if files:
            #    _uiString = _uiString + ' cnt: {0}'.format(len(files))
            
            #if _uiString in _l_uiStrings:
            #    _uiString = _uiString+ "[dup | {0}]".format(_i)
                
            _l_uiStrings.append(_uiString)
            _d_uiStrings[_i] = _uiString
            
            _d_dir[_key]['uiString'] = _uiString
            
        if not _d_levels.get(_depth):
            _d_levels[_depth] = []
            
        _d_levels[_depth].append(_key)
        
        _i+=1
        
    for k,d in _d_dir.iteritems():
        if d.get('dir'):
            d['tokensSub'] = {}
            for subD in d.get('dir'):
                for k,d2 in _d_dir.iteritems():
                    if d2.get('token') == subD:
                        d['tokensSub'][k] = subD

    if _b_debug:
        print(cgmGEN.logString_sub(_str_func,"Levels"))
        pprint.pprint(_d_levels)
        print(cgmGEN.logString_sub(_str_func,"Dat"))
        pprint.pprint(_d_dir)
        
        if uiStrings:
            print (cgmGEN.logString_sub(_str_func,'Ui Strings'))
            #pprint.pprint(_d_uiStrings)
            
            for s in _l_uiStrings:
                print s        
        

    if _l_duplicates and _b_debug:
        log.debug(cgmGEN._str_subLine)
        log.debug("|{0}| >> DUPLICATE ....".format(_str_func))
        for m in _l_duplicates:
            print(m)
        raise Exception,"Must resolve"
    
    #log.debug("|{0}| >> Found {1} modules under: {2}".format(_str_func,len(_d_files.keys()),_path))     
    return _d_dir, _d_levels, _l_keys



    
