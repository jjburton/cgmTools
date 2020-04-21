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


#=============================================================================================================
#>> Queries
#=============================================================================================================
def find_tmpFiles(path = None, level = None, cleanFiles = False):
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
            
            _dot_split = f.split('.')
            _extension = _dot_split[-1]
            
            if len(_extension) > 2:
                if _extension.startswith('ma') or _extension.startswith('mb'):
                    _l_weirdFiles.append(f)
                    _d_weirdFiles[f] = os.path.join(root,f)
                    

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