"""
------------------------------------------
module_utils: cgm.core.mrs.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
import random
import re
import stat
import copy
import time
import os
import pprint
import sys

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================
__version__ = '1.05312019'

import maya.cmds as mc
from cgm.core import cgm_General as cgmGEN

from cgm.core.cgmPy import path_Utils as PATH

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

import cgm.core.lib.mayaSettings_utils as MAYASET
import cgm.core.tools.lib.project_utils as PU
import cgm.core.lib.mayaBeOdd_utils as MAYABEODD


"""
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as RIGMETA

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import list_utils as LISTS
import cgm.core.lib.name_utils as NAMES
import cgm.core.cgmPy.str_Utils as STRINGS
from cgm.core.classes import GuiFactory as cgmUI

from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.mrs.lib.general_utils as BLOCKGEN
import cgm.core.lib.ml_tools.ml_resetChannels as ml_resetChannels
import cgm.core.rig.general_utils as RIGGEN
"""
d_annotations = {
'replace':'Replace existing file',
'rename':'Rename file',
'import':'Import selected',
'reference':'Reference selected',
'explorer':'Open OS explorer here',
'openHere':'Open maya dialog to open file here',
'saveHere':'Open maya dialog to open file here',

}

#=============================================================================================================
#>> Queries
#=============================================================================================================
def find_tmpFiles(path = None, level = None, cleanFiles = False,
                  endMatch = ['_batch.py','_MRSbatch.py'],
                  l_mask = ['max',
                            'mab',
                            'markdown',
                            'mapping']):
    """
    Function for walking below a given directory looking for modules to reload. It finds modules that have pyc's as
    well for help in reloading. There is a cleaner on it as well to clear all pycs found.
    
    :parameters
        path(str)
        level(int) - Depth to search. None means everything
        mode(int)
            0 - normal
            1 - pycs only
        self(instance): cgmMarkingMenu
        cleanPyc: Delete pycs after check
    :returns
        _d_files,_l_ordered,_l_pycd
        _d_files - dict of import key to file
        _l_ordered - ordered list of module keys as found
        _l_pycd - list of modules that were _pycd
    
    """
    _str_func = 'find_tmpFiles'
    _b_debug = log.isEnabledFor(logging.DEBUG)

    _path = PATH.Path(path)
    
    _l_subs = []
    _d_files = {}
    _d_names = {}
    
    _l_duplicates = []
    _l_errors = []
    _base = _path.split()[-1]
    _l_ordered_list = []
    _l_weirdFiles = []
    _d_weirdFiles = {}
    
    log.debug("|{0}| >> Checking base: {1} | path: {2}".format(_str_func,_base,path))
    
    _i = 0
    for root, dirs, files in os.walk(path, True, None):
        
        # Parse all the files of given path and reload python modules
        _mRoot = PATH.Path(root)
        _split = _mRoot.split()
        _subRoot = _split[-1]
        _splitUp = _split[_split.index(_base):]
        
        log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        log.debug("|{0}| >> On split: {1}".format(_str_func,_splitUp))   
        
        _mod = False
        _l_sub = []
        for f in files:
            key = False
            _pycd = False
            _long = os.path.join(root,f)
            
            if '.' not in f:
                continue
            
            _dot_split = f.split('.')
            _extension = _dot_split[-1]
            _pre = _dot_split[0]
            
            if _extension in l_mask:
                continue
            
            if len(_extension) > 3:
                if _extension.startswith('ma') or _extension.startswith('mb'):
                    _l_weirdFiles.append(f)
                    _d_weirdFiles[f] = os.path.join(root,f)
                    continue
            
            for s in endMatch:
                if f.endswith(s):
                    _l_weirdFiles.append(f)
                    _d_weirdFiles[f] = os.path.join(root,f)
                    continue                
            
                    

        if level is not None and _i >= level:break 
        _i +=1
        
    if cleanFiles:
        for f,_path in _d_weirdFiles.iteritems():
            try:
                log.warning("Remove: {0}".format(_path))
                os.remove( _path )
            except WindowsError, e:
                try:
                    log.info("|{0}| >> Initial delete fail. attempting chmod... ".format(_str_func))                          
                    os.chmod( _path, stat.S_IWRITE )
                    os.remove( _path )                          
                except Exception,e:
                    for arg in e.args:
                        log.error(arg)   
                    raise RuntimeError,"Stop"
    else:
        if _d_weirdFiles:
            pprint.pprint(_d_weirdFiles)
            log.warning( cgmGEN.logString_msg(_str_func,"Found {0} files".format(len(_d_weirdFiles.keys()))) )
        else:
            log.warning( cgmGEN.logString_msg(_str_func,"No files found.") )
    return
    """
    if cleanPyc:
        _l_failed = []
        log.debug("|{0}| >> Found {1} pyc files under: {2}".format(_str_func,len(_l_pyc),path))                        
        for _file in _l_pyc:
        #for k in _l_ordered_list:
            #if k in _l_pycd:
            log.debug("|{0}| >> Attempting to clean pyc for: {1} ".format(_str_func,_file))  
            if not _file.endswith('.pyc'):
                raise ValueError,"Should NOT be here"
            try:
                os.remove( _file )
            except WindowsError, e:
                try:
                    log.info("|{0}| >> Initial delete fail. attempting chmod... ".format(_str_func))                          
                    os.chmod( _file, stat.S_IWRITE )
                    os.remove( _file )                          
                except Exception,e:
                    for arg in e.args:
                        log.error(arg)   
                    raise RuntimeError,"Stop"
        _l_pyc = []
        """
    #return _d_files, _l_ordered_list, _l_pycd
    
def buildMenu_utils(self, mMenu):

    mUI.MelMenuItemDiv( mMenu, label='Maya Settings..' )
    
    for a in 'inTangent','outTangent','both':
        
        if a == 'inTangent':
            fnc = MAYASET.defaultInTangent_set
            _current = MAYASET.defaultInTangent_get()
        elif a == 'outTangent':
            fnc = MAYASET.defaultOutTangent_set
            _current = MAYASET.defaultOutTangent_get()
        else:
            fnc = MAYASET.defaultTangents_set
            _current = MAYASET.defaultOutTangent_get()
            
        _sub = mUI.MelMenuItem( mMenu, l=a,
                         subMenu=True)
        
        for t in PU._tangents:
            if t == _current:
                _l = "{0}(current)".format(t)
            else:
                _l = t
                
            mUI.MelMenuItem( _sub,
                             l=_l,                
            c = cgmGEN.Callback(fnc,t))        

    mUI.MelMenuItemDiv( mMenu, label='Global Settings..' )
    mUI.MelMenuItem( mMenu, l="World Match",
                     c = lambda *a:fncMayaSett_do(self,True,False))
    mUI.MelMenuItem( mMenu, l="Anim Match",
                     c = lambda *a:fncMayaSett_do(self,False,True))
    mUI.MelMenuItem( mMenu, l="All Match",
                     c = lambda *a:fncMayaSett_do(self,True,True))
    
    #mUI.MelMenuItemDiv( mMenu,)
    
    mUI.MelMenuItem( mMenu, l="Query",
                     c = lambda *a:fncMayaSett_query(self))
    
    
    mUI.MelMenuItemDiv( mMenu )
    
    #DropBox...
    _fileTrash = mUI.MelMenuItem(mMenu,l='File Trash',subMenu=True)
    
    mUI.MelMenuItem(_fileTrash,
                  label='Query',ut='cgmUITemplate',
                   c=lambda *a: find_tmpFiles( self.directory),
                   ann='Query trash files')    
    mUI.MelMenuItem(_fileTrash,
                  label='Clean',ut='cgmUITemplate',
                   c=lambda *a: find_tmpFiles( self.directory,cleanFiles=1),
                   ann='Clean trash files')            
    
    
    
d_nameToKey = {'world':'d_world',
               'anim':'d_animSettings'}

def fncMayaSett_do(self,world=False,anim=False):
    _str_func = 'ui.fncMayaSett_do'
    log.info("|{0}| >>...".format(_str_func))
    
    d_settings  = {'world':PU._worldSettings,
                   'anim':PU._animSettings}
    d_toDo = {}
    if world:
        d_toDo['world'] = d_settings['world']
    if anim:
        d_toDo['anim'] = d_settings['anim']
        
    d_nameToSet = {'world':{'worldUp':MAYASET.sceneUp_set,
                            'linear':MAYASET.distanceUnit_set,
                            'angular':MAYASET.angularUnit_set},
                   'anim':{'frameRate':MAYASET.frameRate_set,
                           'defaultInTangent':MAYASET.defaultInTangent_set,
                           'defaultOutTangent':MAYASET.defaultOutTangent_set,
                           'weightedTangents':MAYASET.weightedTangets_set},}
    
    #pprint.pprint(d_toDo)
    for k,l in d_toDo.iteritems():
        log.info(cgmGEN.logString_sub(_str_func,k))
        
        #_d = self.d_tf[k]
        _d = self.mDat.__dict__.get(d_nameToKey.get(k))
        
        for d in l:
            try:
                
                log.info(cgmGEN.logString_msg(_str_func,d))
                _type = d.get('t')
                _dv = d.get('dv')
                _name = d.get('n')
                
                _value = _d[_name]#_d[_name].getValue()
                
                fnc = d_nameToSet.get(k,{}).get(_name)
                log.info(cgmGEN.logString_msg(_str_func,"name: {0} | value: {1}".format(_name,_value)))
                
                if fnc:
                    fnc(_value)
                else:
                    log.warning("No function found for {0} | {1}".format(k,_name))
            except Exception,err:
                log.error("Failure {0} | {1} | {2}".format(k,_name,err))
    
def fncMayaSett_query(self):
    _str_func = 'ui.fncMayaSett_query'
    log.info("|{0}| >>...".format(_str_func))
    
    d_settings  = {'world':PU._worldSettings,
                   'anim':PU._animSettings}

    d_nameToCheck = {'world':{'worldUp':MAYASET.sceneUp_get,
                            'linear':MAYASET.distanceUnit_get,
                            'angular':MAYASET.angularUnit_get},
                   'anim':{'frameRate':MAYASET.frameRate_get,
                           'defaultInTangent':MAYASET.defaultInTangent_get,
                           'defaultOutTangent':MAYASET.defaultOutTangent_get,
                           'weightedTangents':MAYASET.weightedTangents_get},}

    #pprint.pprint(d_toDo)
    for k,l in d_settings.iteritems():
        log.info(cgmGEN.logString_sub(_str_func,k))
        
        _d = self.mDat.__dict__.get(d_nameToKey.get(k))
        
        for d in l:
            try:
                
                log.debug(cgmGEN.logString_msg(_str_func,d))
                _type = d.get('t')
                _dv = d.get('dv')
                _name = d.get('n')
                
                _value = _d[_name]#_d[_name].getValue()
                
                fnc = d_nameToCheck.get(k,{}).get(_name)
                
                if fnc:
                    _current = fnc()

                    if _value != _current:
                        log.warning(cgmGEN.logString_msg(_str_func,"name: {0} | setting: {1} | found :{2}".format(_name,_value,_current)))
                    else:
                        log.debug(cgmGEN.logString_msg(_str_func,"name: {0} | setting: {1} | found :{2}".format(_name,_value,_current)))
                    
                else:
                    log.warning("No function found for {0} | {1}".format(k,_name))
            except Exception,err:
                log.error("Failure {0} | {1} | {2}".format(k,_name,err))        