"""
------------------------------------------
baseTool: cgm.core.tools
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
Example ui to start from
================================================================
"""
# From Python =============================================================
import copy
import re
import time
import pprint
import sys
import os
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import maya.cmds as mc
import maya.mel as mel

import Red9.core.Red9_CoreUtils as r9Core
import Red9.core.Red9_General as r9General
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim
import Red9.core.Red9_CoreUtils as r9Core
import Red9.core.Red9_PoseSaver as r9Pose
import Red9.packages.configobj as configobj

import Red9.startup.setup as r9Setup    
LANGUAGE_MAP = r9Setup.LANGUAGE_MAP

import cgm.core.classes.GuiFactory as cgmUI
import cgm.core.cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGEN
import cgm.core.cgmPy.path_Utils as PATHS

mUI = cgmUI.mUI

_pathTest = "D:\Dropbox\MK1"

class pathList(object):
    def __init__(self, optionVar = 'testPath'):
        self.l_paths = []
        self.mOptionVar = cgmMeta.cgmOptionVar(optionVar,'string')
    
    def append(self, arg = _pathTest):
        _str_func = 'pathList.append'
        log.debug(cgmGEN.logString_start(_str_func))
        mPath = PATHS.Path(arg)
        if mPath.exists():
            log.debug(cgmGEN.logString_msg(_str_func,'Path exists | {0}'.format(arg)))
            self.mOptionVar.append(mPath.asFriendly())
        else:
            log.debug(cgmGEN.logString_msg(_str_func,'Invalid Path | {0}'.format(arg)))
            
    def verify(self):
        _str_func = 'pathList.verify'
        log.debug(cgmGEN.logString_start(_str_func))
        
        for p in self.mOptionVar.value:
            log.debug(p)
            mPath = PATHS.Path(p)
            if not mPath.exists():
                log.debug(cgmGEN.logString_msg(_str_func,"Path doesn't exists: {0}".format(p)))
                self.mOptionVar.remove(p)
                
    def remove(self,arg = None):
        _str_func = 'pathList.remove'
        log.debug(cgmGEN.logString_start(_str_func))
        self.mOptionVar.remove(arg)
        
    def log_self(self):
        log.info(cgmGEN._str_hardBreak)        
        log.info(cgmGEN.logString_start('pathList.log_self'))
        self.mOptionVar.report()
        
        log.info(cgmGEN.logString_start('//pathList.log_self'))
        log.info(cgmGEN._str_hardBreak)
        

def walk_below_dir(arg = _pathTest, tests = None,uiStrings = True,
                   fileTest=None):
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
    
    if uiStrings:
        log.debug("|{0}| >> uiStrings on".format(_str_func))           
        _d_uiStrings = {}
        _l_uiStrings = []
    
    log.debug("|{0}| >> Checking base: {1} | path: {2}".format(_str_func,_base,_path))   
    _i = 0
    
    
    for root, dirs, files in os.walk(_path, True, None):
        _rootPath = PATHS.Path(root)
        _split = _rootPath.split()
        _subRoot = _split[-1]
        _splitUp = _split[_split.index(_base):]
        _depth = len(_splitUp) - 1

        log.debug(cgmGEN.logString_sub(_str_func,_subRoot))
        #log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        #log.debug("|{0}| >> On split up: {1}".format(_str_func,_splitUp))
        #log.debug("|{0}| >> On split: {1}".format(_str_func,_split))
        
        _key = _rootPath.asString()
        

            
        _d_dir[_key] = {'depth':_depth,
                        'split':_split,
                        'token':_subRoot,
                        'pyString':_rootPath.asFriendly(),
                        'raw':root,
                        'dir':dirs,
                        'index':_i,
                        'files':files}
        
        if uiStrings:
            if _depth:
                _uiString = ' '*_depth + ' |' + '--' + '{0}'.format(_subRoot)
            else:
                _uiString = _subRoot
            
            if files and fileTest and fileTest.get('endsWith'):
                _cnt = 0
                for f in files:
                    if f.endswith(fileTest.get('endsWith')):
                        _cnt +=1
                _uiString = _uiString + ' ({0})'.format(_cnt)
                
            #if files:
            #    _uiString = _uiString + ' cnt: {0}'.format(len(files))
            
            if _uiString in _l_uiStrings:
                _uiString = _uiString+ "[dup | {0}]".format(_i)
                
            _l_uiStrings.append(_uiString)
            _d_uiStrings[_uiString] = _key
            
            _d_dir[_key]['uiString'] = _uiString
            
        if not _d_levels.get(_depth):
            _d_levels[_depth] = []
            
        _d_levels[_depth].append(_key)
        
        _i+=1
        
        continue
        if len(_split) == 1:
            _cat = 'base'
        else:_cat = _split[-1]
        _l_cat = []
        _d_categories[_cat]=_l_cat

        for f in files:
            key = False

            if f.endswith('.py'):

                if f == '__init__.py':
                    continue
                else:
                    name = f[:-3]    
            else:
                continue

            if _i == 'cat':
                key = '.'.join([_base,name])                            
            else:
                key = '.'.join(_splitUp + [name])    
                if key:
                    log.debug("|{0}| >> ... {1}".format(_str_func,key))                      
                    if name not in _d_modules.keys():
                        _d_files[key] = os.path.join(root,f)
                        _d_import[name] = key
                        _l_cat.append(name)
                        try:
                            module = __import__(key, globals(), locals(), ['*'], -1)
                            reload(module) 
                            _d_modules[name] = module
                            #if not is_buildable(module):
                                #_l_unbuildable.append(name)
                        except Exception, e:
                            log.warning("|{0}| >> Module failed: {1}".format(_str_func,key))                               
                            cgmGEN.cgmExceptCB(Exception,e,msg=vars())

                    else:
                        _l_duplicates.append("{0} >> {1} ".format(key, os.path.join(root,f)))
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
            pprint.pprint(_d_uiStrings)
            
            for s in _l_uiStrings:
                print s        
        

    if _l_duplicates and _b_debug:
        log.debug(cgmGEN._str_subLine)
        log.debug("|{0}| >> DUPLICATE ....".format(_str_func))
        for m in _l_duplicates:
            print(m)
        raise Exception,"Must resolve"
    
    #log.debug("|{0}| >> Found {1} modules under: {2}".format(_str_func,len(_d_files.keys()),_path))     
    if uiStrings:
        return _d_dir, _d_levels, _l_uiStrings, _d_uiStrings
    return _d_dir, _d_levels, None, None
        
        
        