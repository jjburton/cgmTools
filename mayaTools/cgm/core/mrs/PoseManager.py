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
        
        