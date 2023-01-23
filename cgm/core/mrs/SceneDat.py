"""
sceneDat
Josh Burton 
www.cgmonastery.com

Core skinning data handler for cgm going forward.

Storing joint positions and vert positions so at some point can implement a method
to apply a skin without a reference object in scene if geo or joint counts don't match

Currently only regular skin clusters are storing...

Features...
- Skin data gather
- Read/write skin data to a readable config file
- Apply skinning data to geo of different vert count
- 

Thanks to Alex Widener for some ideas on how to set things up.

"""
__MAYALOCAL = 'SCENEDAT'


# From Python =============================================================
import copy
import os
import pprint
import getpass

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel
#import maya.OpenMaya as OM
#import maya.OpenMayaAnim as OMA

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import Red9.core.Red9_CoreUtils as r9Core

import Red9.packages.configobj as configobj
import Red9.startup.setup as r9Setup    

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as cgmValid
import cgm.core.classes.GuiFactory as cgmUI
import cgm.core.cgmPy.path_Utils as PATHS
import cgm.core.lib.path_utils as COREPATHS
import cgm.core.lib.math_utils as COREMATH
import cgm.core.lib.string_utils as CORESTRINGS
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.tools.lib.project_utils as PU
import cgm.core.lib.mayaSettings_utils as MAYASET
import cgm.core.mrs.lib.scene_utils as SCENEUTILS
import cgm.core.lib.attribute_utils as ATTR
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Dat as CGMDAT

import cgm.images as cgmImages
mImagesPath = PATHS.Path(cgmImages.__path__[0])

mUI = cgmUI.mUI

__version__ = cgmGEN.__RELEASESTRING
_colorGood = CORESHARE._d_colors_to_RGB['greenWhite']
_colorBad = CORESHARE._d_colors_to_RGB['redWhite']

log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start



d_sample = {'data':[{'asset': 'punk_02',
             'category': 'character',
             'exportMode': 'export',
             'path': 'D:\\Dropbox\\Art\\Assets\\Animation\\Playspace\\content\\character\\punk_02\\animation\\throw\\base\\punk_02_throw_base_02.mb',
             'set': 'throw',
             'subType': 'animation',
             'variation': 'base',
             'version': 'punk_02_throw_base_02.mb'},
            {'asset': 'punk_02',
             'category': 'character',
             'exportMode': 'export',
             'path': 'D:\\Dropbox\\Art\\Assets\\Animation\\Playspace\\content\\character\\punk_02\\animation\\tube\\base\\punk_02_tube_base_03.mb',
             'set': 'tube',
             'subType': 'animation',
             'variation': 'base',
             'version': 'punk_02_tube_base_03.mb'}]}


class BaseDat(CGMDAT.data):
    def startDir_get(self,startDirMode=None):
        _str_func = 'BaseDat.startDir_get'
        log.debug(log_msg(_str_func,startDirMode))        
        if startDirMode == None:
            startDir = CGMDAT.startDir_getBase(self.structureMode)
        else:
            startDir = CGMDAT.startDir_getBase(startDirMode)
        
        if len(self._startDir)>1:
            _path = os.path.join(startDir, os.path.join(*self._startDir))                    
        else:
            _path = os.path.join(startDir, self._startDir[0])        
        
        return _path

class SceneExport(BaseDat):
    _ext = 'cgmSceneExportDat'
    _startDir = ['cgmDat','sceneExport']
    _string = 'SceneExport'
    _dataFormat = 'config'
    
    '''
    Class to handle blockDat data. Replacing existing block dat which storing on the node is not ideal
    '''    
    
    def __init__(self, dat = None, filepath = None, sceneUI = None, **kws):
        """

        """
        _str_func = '{}.__buffer__'.format(self._string)
        log.debug(log_start(_str_func))
        super(SceneExport, self).__init__(filepath, **kws)
        self.mSceneUI  = None
        
        if dat:
            self.dat = dat
        if sceneUI:
            self.mSceneUI = sceneUI
            
        self.structureMode = 'workspace'
        
    def get(self, report = False):
        _str_func = '{}.get'.format(self._string)
        log.debug(log_start(_str_func))
        
        
        if self.mSceneUI:
            self.dat = {'data':self.mSceneUI.batchExportItems}
        
        
    def set(self, mBlock = None, **kws):
        _str_func = '{}.set'.format(self._string)
        log.debug(log_start(_str_func))
        
        
    """
    def load(self):
        _str_func = '{}.load'.format(self._string)
        log.debug(log_start(_str_func))
        
        if not self.mSceneUI:
            raise ValueError,"Must have mBlock to save"
        
        startDir = self.startDir_get()
        _path = "{}.{}".format( os.path.normpath(os.path.join(startDir,self.mBlock.p_nameBase)), BlockDat._ext)
        
        if not os.path.exists(_path):
            raise ValueError,"Invalid path: {}".format(_path)
        pprint.pprint(_path)
        
        self.read(_path)
        
        self.set()
        
        return        
        
    def write(self,*arg,**kws):
        _str_func = '{}.write'.format(self._string)
        log.debug(log_start(_str_func))
        
        if not self.dat:
            raise ValueError,"Must have dat to save"
        
        if self.dir_export:
            startDir = self.dir_export
        else:
            startDir = self.startDir_get(kws.get('startDirMode'))
            
        _path = "{}.{}".format( os.path.normpath(os.path.join(startDir,_name)), BlockDat._ext)
        
        pprint.pprint(_path)
        pprint.pprint(kws)
        BaseDat.write(self, filepath = _path, *arg,**kws)
        #self.write(_path)
        
        return
        if not os.path.exists(startDir):
            CGMDAT.CGMOS.mkdir_recursive(startDir)
        
        if not mode:
            pass
"""