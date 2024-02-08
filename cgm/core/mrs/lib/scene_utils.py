"""
------------------------------------------
module_utils: cgm.core.mrs.lib
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
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

import maya.cmds as mc
from cgm.core import cgm_General as cgmGEN
__version__ = cgmGEN.__RELEASESTRING

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.cgmPy.os_Utils as CGMOS

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

import cgm.core.lib.mayaSettings_utils as MAYASET
import cgm.core.tools.lib.project_utils as PU
import cgm.core.lib.mayaBeOdd_utils as MAYABEODD

cgmGEN._reloadMod(MAYASET)

"""
# From cgm ==============================================================
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
log_start = cgmGEN.logString_start
log_sub = cgmGEN.logString_sub
log_msg = cgmGEN.logString_msg
#=============================================================================================================
#>> Queries
#=============================================================================================================
find_tmpFiles = CGMOS.find_tmpFiles
    
def buildMenu_utils(self, mMenu):
    mUI.MelMenuItem( mMenu, l="New Scene",
                    c = lambda *a:uiFunc_newProjectScene(self))    
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
                     c = lambda *a:fncMayaSett_do(self,True,False,False))
    mUI.MelMenuItem( mMenu, l="Anim Match",
                     c = lambda *a:fncMayaSett_do(self,False,True,False))
    mUI.MelMenuItem( mMenu, l="Grid Match",
                     c = lambda *a:fncMayaSett_do(self,False,False,True))    
    mUI.MelMenuItem( mMenu, l="All Match",
                     c = lambda *a:fncMayaSett_do(self,True,True,True))
    
    #mUI.MelMenuItemDiv( mMenu,)
    
    mUI.MelMenuItem( mMenu, l="Query",
                     c = lambda *a:fncMayaSett_query(self))
    
    
    mUI.MelMenuItemDiv( mMenu )
    
    #Empty
    _empty = mUI.MelMenuItem(mMenu,l='Empty Dirs',subMenu=True)
    
    mUI.MelMenuItem(_empty,
                  label='Add empty.txt',ut='cgmUITemplate',
                  c=lambda *a: CGMOS.find_emptyDirs( self.directory,True,False),
                  ann='Add empty txt files')
    
    mUI.MelMenuItem(_empty,
                  label='Remove',ut='cgmUITemplate',
                   c=lambda *a: CGMOS.find_emptyDirs( self.directory,False,True),
                   ann='Delete empty dirs')    
    
    
    
    
    
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

def fncMayaSett_do(self,world=False,anim=False,grid=False):
    _str_func = 'ui.fncMayaSett_do'
    log.debug("|{0}| >>...".format(_str_func))
    
    d_settings  = {'world':PU._worldSettings,
                   'grid':PU._worldSettings,
                   'anim':PU._animSettings}
    d_toDo = {}
    if world or grid:
        d_toDo['world'] = d_settings['world']
    if anim:
        d_toDo['anim'] = d_settings['anim']
        
        
    d_nameToSet = {'world':{'worldUp':MAYASET.sceneUp_set,
                            'linear':MAYASET.distanceUnit_set,
                            'angular':MAYASET.angularUnit_set,
                            'gridLengthAndWidth':MAYASET.grid_LengthAndWidth_set,
                            'gridLinesEvery':MAYASET.grid_spacing_set,
                            'gridSubdivisions':MAYASET.grid_subdivisions_set},
                   'anim':{'frameRate':MAYASET.frameRate_set,
                           'defaultInTangent':MAYASET.defaultInTangent_set,
                           'defaultOutTangent':MAYASET.defaultOutTangent_set,
                           'weightedTangents':MAYASET.weightedTangets_set},}
    
    #pprint.pprint(d_toDo)
    for k,l in list(d_toDo.items()):#d_toDo.iteritems():
        log.debug(cgmGEN.logString_sub(_str_func,k))
        
        #_d = self.d_tf[k]
        _d = self.mDat.__dict__.get(d_nameToKey.get(k))
        
        for d in l:
            try:
                
                log.debug(cgmGEN.logString_msg(_str_func,d))
                _type = d.get('t')
                _dv = d.get('dv')
                _name = d.get('n')
                
                if grid:
                    if not _name.startswith('grid'):
                        continue
                
                _value = _d.get(_name)#_d[_name].getValue()
            
                fnc = d_nameToSet.get(k,{}).get(_name)
                log.debug(cgmGEN.logString_msg(_str_func,"name: {0} | value: {1}".format(_name,_value)))
                
                if fnc and _value:
                    fnc(_value)
                else:
                    log.warning("No function found for {0} | {1}".format(k,_name))
            except Exception as err:
                log.error("Failure {0} | {1} | {2}".format(k,_name,err))
    
def fncMayaSett_query(self):
    _str_func = 'ui.fncMayaSett_query'
    log.debug("|{0}| >>...".format(_str_func))
    
    d_settings  = {'world':PU._worldSettings,
                   'anim':PU._animSettings}

    d_nameToCheck = {'world':{'worldUp':MAYASET.sceneUp_get,
                            'linear':MAYASET.distanceUnit_get,
                            'angular':MAYASET.angularUnit_get,
                            'gridLengthAndWidth':MAYASET.grid_LengthAndWidth_get,
                            'gridLinesEvery':MAYASET.grid_spacing_get,
                            'gridSubdivisions':MAYASET.grid_subdivisions_get},
                   'anim':{'frameRate':MAYASET.frameRate_get,
                           'defaultInTangent':MAYASET.defaultInTangent_get,
                           'defaultOutTangent':MAYASET.defaultOutTangent_get,
                           'weightedTangents':MAYASET.weightedTangents_get},}

    #pprint.pprint(d_toDo)
    for k,l in list(d_settings.items()):#d_toDo.iteritems():
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
            except Exception as err:
                log.error("Failure {0} | {1} | {2}".format(k,_name,err))
                
                
def verify_ObjectSets():
    log.debug("verify_ObjectSets..."+cgmGEN._str_subLine)
    for n in 'bake','delete','export':
        str_name = mc.optionVar(q='cgm_{0}_set'.format(n))
        if not mc.objExists(str_name):
            mSet = cgmMeta.cgmObjectSet(setType='tdSet',qssState=True)        
            mSet.doStore('cgmName',n)
            mSet.doName()
            log.info("{} created".format(str_name))
        else:
            log.info("{} exists".format(str_name))
    log.debug(cgmGEN._str_subLine)
    
    
def uiFunc_newProjectScene(self,*args):
    str_func = 'uiFunc_newProjectScene'
    log.debug(log_start(str_func))
    
    createPrompt = mc.confirmDialog(
                title='Create?',
                    message='Create New File',
                    button=['Yes', 'No'],
                    defaultButton='No',
                            cancelButton='No',
                            dismissString='No')

    if createPrompt == 'Yes':
        mc.file(new=True, f=True)
        fncMayaSett_do(self, True, True)    else:
        log.warning("No new file created")   
        
    log.debug(cgmGEN._str_hardBreak)
    
    

    