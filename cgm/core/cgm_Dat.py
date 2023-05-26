"""
cgmDat
Josh Burton 
www.cgmonastery.com

"""
__MAYALOCAL = 'CGMDAT'


# From Python =============================================================
import copy
import os
import pprint
import getpass
from functools import partial

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
import importlib
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
##import maya.mel as mel
#import maya.OpenMaya as OM
#import maya.OpenMayaAnim as OMA

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import Red9.core.Red9_CoreUtils as r9Core

import json

import Red9.packages.configobj as configobj
import Red9.startup.setup as r9Setup    

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.classes.GuiFactory as CGMUI
import cgm.core.cgmPy.path_Utils as PATHS
import cgm.core.lib.path_utils as COREPATHS
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.lib.string_utils as CORESTRINGS

import cgm.core.cgmPy.os_Utils as CGMOS
"""
import cgm.core.lib.math_utils as COREMATH
import cgm.core.lib.string_utils as CORESTRINGS
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.tools.lib.project_utils as PU
import cgm.core.lib.mayaSettings_utils as MAYASET
import cgm.core.mrs.lib.scene_utils as SCENEUTILS
import cgm.core.lib.attribute_utils as ATTR
import cgm.images as cgmImages
mImagesPath = PATHS.Path(cgmImages.__path__[0])
"""
mUI = CGMUI.mUI
from cgm.core import cgm_General as cgmGEN

__version__ = cgmGEN.__RELEASESTRING
_colorGood = CORESHARE._d_colors_to_RGB['greenWhite']
_colorBad = CORESHARE._d_colors_to_RGB['redWhite']

log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start


_l_startDirModes = ('workspace','file','dev')


def startDir_getBase(mode = 'workspace', devList = []):
    str_func = 'startDir_get'
    log.debug(log_msg(str_func, mode))
    
    if mode == 'workspace':
        return mc.workspace(q=True, rootDirectory=True)
    elif mode == 'file':
        _file = mc.file(q=True, loc=True)
        if not os.path.exists(_file):
            log.warning("StartDir mode is 'file' and file not saved or invalid file path: {}".format(_file))
            return
        return os.path.split(_file)[0]
    elif mode == 'project':
        log.warning("Haven't implemented cgmProject")
    elif mode == 'dev':
        import cgm
        _cgmPath = os.path.split(cgm.__file__)[0]
        if devList:
            for p in devList:
                _cgmPath = os.path.join(_cgmPath,p)
        return _cgmPath
        
    else:
        raise ValueError("Unknown mode: {}".format(mode))

class batch(object):
    def __init__(self, mNodes, dataClass = None, mode = None):
        if not mNodes:
            raise ValueError("Must have mNodes passed")        
        if not dataClass:
            raise ValueError("Must have dataClass")
        
        self.dataclass = dataClass 
        self.mNodes = VALID.listArg(mNodes)
        self.mode = mode
        self.ml_mData = []
        self.dir_export = ''
        
    def get(self):
        _str_func = 'batch.get'
        log.debug("|{0}| >>...".format(_str_func))        
        self.ml_mData = []
        
        for mObj in self.mNodes:
            log.info(log_msg(_str_func,mObj))
            mDat = self.dataclass(mObj)
            mDat.get()
            self.ml_mData.append(mDat)
        
    def get_exportPath(self,startDir = None, force = False, startDirMode = None):
        _str_func = 'batch.get_exportPath'
        
        if not force and self.dir_export and os.path.exists(self.dir_export):
            log.info(log_msg(_str_func,"No force, passing stored"))                                    
            return self.dir_export

        if not startDir:
            
            startDir = self.dataclass().startDir_get(startDirMode = startDirMode)
            print((self.dataclass))
            print(startDir)
            if not os.path.exists(startDir):
                CGMOS.mkdir_recursive(startDir)            
            """
            if self.ml_mData:
                log.info(log_msg(_str_func,"Checking ml_mData[0]"))                        
                startDir = self.ml_mData[0].startDir_get()
            else:
                log.info(log_msg(_str_func,"Standard check"))                                        
                startDir = startDir_getBase()"""
                
        dirPath = mc.fileDialog2(fileMode=3,
                                 caption = "Export Path for: {}".format(self.dataclass.__name__),
                                dir=startDir)
        if not dirPath:
            return log.error (cgmGEN.logString_msg(_str_func, "No path selected"))
        dirPath =  dirPath[0]
                    
        pprint.pprint(dirPath)
        self.dir_export = dirPath
    
    def write(self,*args,**kws):
        _str_func = 'batch.write'
        
        pprint.pprint(kws)
        
        if not self.dir_export:
            self.get_exportPath(startDirMode=kws.get('startDirMode'))
            if not self.dir_export:
                return log.error(log_msg(_str_func,"Must have export directory."))
        
        kws.pop('startDirMode')
        
        if not self.ml_mData:
            log.warning(log_msg(_str_func,"Getting data"))
            self.get()
                
        
        for i,mObj in enumerate(self.mNodes):
            mDat = self.ml_mData[i]            
            log.info("{} | {}".format(i, mDat))
            mDat.dir_export = self.dir_export
            
            mDat.write(*args,**kws)
        
    
    def read(self):
        pass
    
    def report(self):
        log.info(cgmGEN._str_hardBreak)
        log.info("Export path: {}".format(self.dir_export))
        for i,mObj in enumerate(self.mNodes):
            log.info("{} | {}".format(i, self.ml_mData[i]))
            #self.ml_mData[i].log_self()
        log.info(cgmGEN._str_hardBreak)
        
    
class data(object):
    '''
    Core data class
    
    
    saveMode
    - file | start at the the file dir
    - workspace | start at the current workspace
    - path | set path
    
    '''    
    _ext = 'cgmDat'
    _dataFormat = 'config'
    _startDir = ['cgmDat']#...storing dir paths as lists to avoid weird os issues
    
    def __init__(self, filepath = None, **kws):
        """

        """
        str_func = 'data.__init__'
        log.debug(log_start(str_func))
        self.dataformat = kws.get('dataFormat',self._dataFormat)
        self.str_filepath = None
        self._dataformat_resolved = None
        self.dat = {}
        self.structureMode = 'workspace'#...workspace
        self.dir_export = None
        
        if filepath:
            self.read(filepath)
   
    def __repr__(self):
        return "({0} | {1} | {2})".format(self.__class__, self._ext, self._dataFormat)
      
       
    def get(self):
        str_func = 'data.get'
        log.debug(log_start(str_func))
        
    def log_self(self):
        log.info(cgmGEN._str_hardBreak)
        _d = copy.copy(self.__dict__)
        _d.pop('dat')
        pprint.pprint(_d)
        
    def log_dat(self):
        log.info(cgmGEN._str_hardBreak)
        #
        #pprint.pprint(self.dat)
        cgmGEN.walk_dat(self.dat)
        
        #for k,d in self.dat.iteritems():
        #    log.info(cgmGEN.logString_start(k))
        #    pprint.pprint(d)
    
    def set(self):
        str_func = 'data.set'
        log.debug(log_start(str_func))
        
    def checkState(self):
        _str_func = 'checkState'
        log.debug("|{0}| >>...".format(_str_func))
        if self.dat:
            return True
        return False
        
    def startDir_get(self,startDirMode=None):
        if startDirMode == None:
            startDir = startDir_getBase(self.structureMode)
        else:
            startDir = startDir_getBase(startDirMode)
        
        startDir = os.path.normpath(startDir)
        
        if len(self._startDir)>1:
            _path = os.path.normpath(os.path.join(startDir, os.path.normpath(os.path.join(*self._startDir))))                    
        else:
            _path = os.path.normpath(os.path.join(startDir, self._startDir[0]))        
        
        return _path
    
    def validateFilepath(self, filepath = None, fileMode = 0, startDirMode = None):
        '''
        Validates a given filepath or generates one with dialog if necessary
        '''        
        if filepath is None:
            startDir = self.startDir_get(startDirMode=startDirMode)
            log.debug(startDir)
            if not os.path.exists(startDir):
                CGMOS.mkdir_recursive(startDir)
                    
            filepath = mc.fileDialog2(dialogStyle=2, fileMode=fileMode, startingDirectory=startDir,
                                      fileFilter='{} file (*.{})'.format(self._ext,self._ext))
            if filepath:filepath = filepath[0]
            
        if filepath is None:
            return False
        
        mFile = PATHS.Path(filepath)
        self.str_filepath = mFile.asFriendly()
        log.debug("filepath validated...")        
        return mFile

    def fillDatHolder(self, dataHolder = {}):
        for k,d in list(self.dat.items()):
            print(k)
            dataHolder[k] = d
            
    def fillDat(self, dataHolder = {}):
        for k,d in list(dataHolder.items()):
            self.dat[k] = d

            
    def write(self, filepath = None, update = False, startDirMode = None, forcePrompt = False):
        str_func = 'data.write'
        log.debug("|{}| >>... filepath:{} | update:{} | startDirMode:{} | forcePrompt:{}".format(str_func,filepath, update, startDirMode, forcePrompt))
        
        if update and self.str_filepath:
            filepath = self.str_filepath
            
        if forcePrompt:
            log.debug("forcePrompt filepath")
            filepath = self.validateFilepath(None, startDirMode=startDirMode)            
        elif not filepath:
            log.debug("Getting filepath")
            filepath = self.validateFilepath(filepath, startDirMode=startDirMode)
            
        if not filepath:
            log.warning('Invalid path: {0}'.format(filepath))
            return False
        
        log.warning('Write to: {0}'.format(filepath))
            
            
        # =========================
        # write to ConfigObject
        # =========================
        if self.dataformat == 'config':
            cgmGEN._reloadMod(configobj)
            ConfigObj = configobj.ConfigObj(indent_type='\t', encoding='utf-8')
            self.fillDatHolder(ConfigObj)
            """
            ConfigObj['info'] = self.infoDict
            ConfigObj['filterNode_settings'] = self.settings.__dict__
            ConfigObj['poseData'] = self.poseDict
            if self.skeletonDict:
                ConfigObj['skeletonDict'] = self.skeletonDict
            if self.hikDict:
                ConfigObj['hikDict'] = self.hikDict"""
            
            ConfigObj.filename = filepath
            ConfigObj.write()
            self._dataformat_resolved = 'config'
            
        # =========================
        # write to JSON format
        # =========================
        elif self.dataformat == 'json':
            data = {}
            self.fillDatHolder(data)
            with open(filepath, 'w') as f:
                f.write(json.dumps(data, sort_keys=True, indent=4))
                f.close()
            self._dataformat_resolved = 'json'        
            
        else:
            raise ValueError("Unknown mode: {}".format(self.mode))
        
        #if update:
        self.str_filepath = filepath
        log.warning('Completed: {} | {}'.format(self._dataformat_resolved,filepath))
        return True
        
    def read(self, filepath = None, decode = True, report = False, startDirMode= None):
        '''
        Read the Data ConfigObj from file and report the data if so desired.
        ''' 
        str_func = 'data.read'
        log.debug("|{0}| >>...".format(str_func))
        
        mPath = self.validateFilepath(filepath, fileMode = 1, startDirMode=startDirMode)
        
        if not mPath or not mPath.exists():            
            return log.error('Given filepath doesnt not exist : %s' % filepath)   
        
        # =========================
        # read JSON format
        # =========================
        if self.dataformat == 'json':
            try:
                with open(mPath, 'r') as f:
                    data = json.load(f)
                self.fillDat(data)
                
                """
                self.poseDict = data['poseData']
                if 'info' in data.keys():
                    self.infoDict = data['info']
                if 'skeletonDict' in data.keys():
                    self.skeletonDict = data['skeletonDict']
                self._dataformat_resolved = 'json'"""
            except IOError as err:
                self._dataformat_resolved = 'config'
                log.info('JSON : DataMap format failed to load, reverting to legacy ConfigObj')
            except Exception as err:
                log.error(err)
                return False                
        # =========================
        # read ConfigObject
        # =========================
        if self._dataformat_resolved == 'config' or self.dataformat == 'config':
            try:
                
                # for key, val in configobj.ConfigObj(filename)['filterNode_settings'].items():
                #    self.settings.__dict__[key]=decodeString(val)
                data = configobj.ConfigObj(mPath.asFriendly(), encoding='utf-8')
                self.fillDat(data)
                
                if decode:decodeDat(self)
                """
                self.poseDict = data['poseData']
                if 'info' in data:
                    self.infoDict = data['info']
                if 'skeletonDict' in data:
                    self.skeletonDict = data['skeletonDict']
                if 'filterNode_settings' in data:
                    self.settings_internal = r9Core.FilterNode_Settings()
                    self.settings_internal.setByDict(data['filterNode_settings'])
                self._dataformat_resolved = 'config'"""
            except Exception as err:
                log.error("Read Fail: {}".format(str(mPath)))                                
                log.error(err)
                return False
            
        if report:self.log_self()
        self.str_filepath = str(mPath)
        
        return True    
        
def decodeDat(self,dat = None):
    str_func  = 'decodeDat'
    if dat == None:
        dat = self.dat
    
    def processDict(dArg):
        for k,d in list(dArg.items()):
            _type = type(d)
            log.debug(log_msg(str_func, "{} | {}").format(k,_type))            
            if issubclass(_type,list):
                log.debug(log_msg(str_func, "...sublist"))                                                        
                for i,v in enumerate(d):
                    d[i] = r9Core.decodeString(v)
            elif issubclass(_type,dict):
                log.debug(log_msg(str_func, "...subdict"))                                        
                dArg[k] = processDict(d)
            elif VALID.stringArg(d):#issubclass(_type,str) or issubclass(_type,unicode):
                log.debug(log_msg(str_func, "...str"))                                                        
                dArg[k] = r9Core.decodeString(d)
        
        #pprint.pprint(dArg)
        return dArg
                
    for k,d in list(dat.items()):
        _type = type(d)
        log.debug(log_msg(str_func, "{} | {}").format(k,_type))
        if issubclass(_type,list):
            log.debug(log_msg(str_func, "...list"))                        
            for i,v in enumerate(d):
                d[i] = r9Core.decodeString(v)
        elif issubclass(_type,dict):
            log.debug(log_msg(str_func, "...dict"))            
            dat[k] = processDict(d)
            
        elif VALID.stringArg(d):#issubclass(_type,str) or issubclass(_type,unicode):
            dat[k] = r9Core.decodeString(d)
        
    #pprint.pprint(dat)
    
    
    
# ============================================================================================================================================================================================================
# >> UI
# =============================================================================================================================================================================================================
_d_ann = {}
def uiDataSetup(self):
    if not self.__dict__.get('_l_startDirModes'):
        self._l_startDirModes = _l_startDirModes
    
    try:
        self.var_startDirMode
    except:
        self.create_guiOptionVar('startDirMode',defaultValue = 0)     
        
def uiMenu_addDirMode(self,parent):
    _starDir = mUI.MelMenuItem(parent, l="StartDir",tearOff=True,
                               subMenu = True)
    
    if not self.__dict__.get('_l_startDirModes'):
        self._l_startDirModes = _l_startDirModes
        
    _on = self.var_startDirMode.value
    uiRC = mc.radioMenuItemCollection()
    
    for i,item in enumerate(self._l_startDirModes):
        if i == _on:_rb = True
        else:_rb = False
        mUI.MelMenuItem(_starDir,label=item,
                        collection = uiRC,
                        ann = _d_ann.get(item),
                        c = cgmGEN.Callback(uiFunc_setDirMode,self,i),                                  
                        rb = _rb)
        
def uiFunc_setDirMode(self,v):
    _str_func = 'uiFunc_setDirMode[{0}]'.format(self.__class__.TOOLNAME)            
    log.debug("|{0}| >>...".format(_str_func))
    
    
    _path = startDir_getBase(self._l_startDirModes[v])
    if _path:
        self.var_startDirMode.setValue(v)
        print(_path)
        
        
class ui(CGMUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    _toolname = 'cgmDat'
    TOOLNAME = 'ui_cgmDat'
    WINDOW_NAME = "{}UI".format(TOOLNAME)
    WINDOW_TITLE = 'cgmDat | {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 300,300
    
    _datClass = data
 
    def insert_init(self,*args,**kws):
        self._loadedFile = ""
        self.uiDat = self._datClass()
        
        self.create_guiOptionVar('startDirMode',defaultValue = 0) 
        self._l_startDirModes = _l_startDirModes
        
        self.create_guiOptionVar('LastLoaded',defaultValue = '')
        self.var_LastLoaded.setType('string')
        
        self.mPathList_recent = cgmMeta.pathList('{}PathsRecent'.format(self._datClass.__name__))
    
    def post_init(self,*args,**kws):
        if self.uiDat.dat:
            return 
        _path = self.var_LastLoaded.value
        if os.path.exists(_path):
            self.uiFunc_dat_load(filepath = _path)
        
    def build_menus(self):
        self.uiMenu_FileMenu = mUI.MelMenu(l='File', pmc = cgmGEN.Callback(self.buildMenu_file))
        self.uiMenu_SetupMenu = mUI.MelMenu(l='Dev', pmc = cgmGEN.Callback(self.buildMenu_dev))

    def buildMenu_file(self):
        self.uiMenu_FileMenu.clear()
        mUI.MelMenuItemDiv(self.uiMenu_FileMenu, l="Options")
        
        _menu = self.uiMenu_FileMenu
        #Context ...---------------------------------------------------------------------------------
        _starDir = mUI.MelMenuItem(_menu, l="StartDir",tearOff=True,
                                   subMenu = True)
        
        uiRC = mc.radioMenuItemCollection()
        
        #self._l_contextModes = ['self','below','root','scene']
        _d_ann = {'self':'Context is only of the active/sel block',
                  'below':'Context is active/sel block and below',
                  'root':'Context is active/sel root and below',
                  'scene':'Context is all blocks in the scene. Careful skippy!',}
        
        _on = self.var_startDirMode.value
        for i,item in enumerate(self._l_startDirModes):
            if i == _on:_rb = True
            else:_rb = False
            mUI.MelMenuItem(_starDir,label=item,
                            collection = uiRC,
                            ann = _d_ann.get(item),
                            c = cgmGEN.Callback(self.uiFunc_setDirMode,i),                                  
                            rb = _rb)        
        
        mUI.MelMenuItemDiv(self.uiMenu_FileMenu, l="Utils")

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save",
                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_save)))
                         
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_save_actions,self)))

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save As",
                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_saveAs)))
        
        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Load",
                          c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_load)))
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_load_actions,self)))
                        
        #Recent Projects --------------------------------------------------------------------------
        self.mPathList_recent.verify()
        _recent = mUI.MelMenuItem( self.uiMenu_FileMenu, l="Recent",
                                   ann='Open an recent file',subMenu=True)
        
        for p in self.mPathList_recent.l_paths:
            if '.' in p:
                _split = p.split('.')
                _l = CORESTRINGS.short(str(_split[0]),20)                
            else:
                _l = CORESTRINGS.short(str(p),20)
            mUI.MelMenuItem(_recent, l=_l,
                            c = partial(self.uiFunc_dat_load,**{'filepath':p}))            
        #==========================================================================================        
                        
    def uiFunc_setDirMode(self,v):
        _str_func = 'uiFunc_setDirMode[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        _path = startDir_getBase(self._l_startDirModes[v])
        if _path:
            self.var_startDirMode.setValue(v)
            print(_path)
        
    def buildMenu_dev(self):
        self.uiMenu_SetupMenu.clear()
        _menu = self.uiMenu_SetupMenu
        mUI.MelMenuItem( _menu, l="Ui | ...",
                         c=lambda *a: self.log_self())               
        mUI.MelMenuItem( _menu, l="Dat | class",
                         c=lambda *a: self.uiDat.log_self())        
        mUI.MelMenuItem( _menu, l="Dat | stored",
                         c=lambda *a: self.uiDat.log_dat())            
    def log_self(self):
        _str_func = 'log_self[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        pprint.pprint(self.__dict__)
        
    def uiStatus_refresh(self, string = None):
        _str_func = 'uiStatus_refresh[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        if not self.uiDat.checkState():
            self.uiStatus_top(edit=True,bgc = CORESHARE._d_gui_state_colors.get('help'),label = 'No Data')            
        else:
            #self.uiData_base.clear()
            if not string:
                string = CORESTRINGS.short(self._loadedFile,max=40,start=10)
            self.uiStatus_top(edit=True,bgc = CORESHARE._d_gui_state_colors.get('connected'),label = string )            
            self.uiUpdate_data()
            
    def uiFunc_dat_save(self):
        _str_func = 'uiFunc_dat_save[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        self.uiDat.write(update=True,startDirMode = self._l_startDirModes[self.var_startDirMode.value])
        return
    
    def uiFunc_dat_saveAs(self):
        _str_func = 'uiFunc_dat_saveAs[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        self.uiDat.write(startDirMode = self._l_startDirModes[self.var_startDirMode.value], forcePrompt=True)
        return
    
    def uiFunc_dat_load(self,*args,**kws):
        _str_func = 'uiFunc_dat_load[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        if not kws.get('startDir'):
            kws['startDirMode'] = _l_startDirModes[self.var_startDirMode.value]
        
        
        if self.uiDat.read(**kws):
            self._loadedFile = self.uiDat.str_filepath
            self.var_LastLoaded.setValue(self.uiDat.str_filepath)
            log.info(cgmGEN.logString_msg(_str_func,"Read: {}".format(self.uiDat.str_filepath)))
            self.mPathList_recent.append_recent(self.uiDat.str_filepath)
            
        else:
            self._loadedFile = ''
            self.var_LastLoaded.setValue('')
            
            
            
        self.uiStatus_refresh()
        return
    
    def uiData_checkState(self):
        return self.uiDat.checkState()                
        
    def uiUpdate_top(self):
        _str_func = 'uiUpdate_top[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        self.uiSection_top.clear()
        CGMUI.add_Header('Put stuff here')
        
    def uiUpdate_data(self):
        _str_func = 'uiUpdate_data[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        self.uiFrame_data.clear()
        if not self.uiDat:
            return
        
        """
        mUI.MelLabel(self.uiFrame_data, label = "Select", h = 13, 
                     ut='cgmUIHeaderTemplate',align = 'center')
        
        for util in ['Select Source']:
            mUI.MelButton(self.uiFrame_data,
                          c = cgmGEN.Callback(self.uiFunc_dat,util),
                          ann="...",
                          label=util,
                          ut='cgmUITemplate',
                          h=20)"""
 
        row = mUI.MelHLayout( self.uiFrame_data )
        mUI.MelButton( row, l='apples' )
        mUI.MelButton( row, l='bananas' )
        mUI.MelButton( row, l='oranges' )
        row.layout()
        
        
        mUI.MelLabel(self.uiFrame_data, label = "PPRINT", h = 13, 
                     ut='cgmUIHeaderTemplate',align = 'center')
        
        for a in list(self.uiDat.dat.keys()):
            mUI.MelButton(self.uiFrame_data,
                          c = cgmGEN.Callback(self.uiFunc_printDat,a),
                          ann="...",
                          label=a,
                          ut='cgmUITemplate',
                          h=20)
            
        mUI.MelButton(self.uiFrame_data,
                      c = cgmGEN.Callback(self.uiFunc_printDat,'all'),
                      ann="...",
                      label='all',
                      ut='cgmUITemplate',
                      h=20)
    
    def uiFunc_dat_get(self):
        _str_func = 'uiFunc_dat_get[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        _sel = mc.ls(sl=1)
        
        return
 
    def uiFunc_dat(self,mode='Select Source'):
        _str_func = 'uiFunc_dat[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))  
        
        if not self.uiDat:
            return log.error("No dat loaded selected")

    def uiFunc_printDat(self,mode='all'):
        _str_func = 'uiFunc_print[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))  
        
        if not self.uiDat:
            return log.error("No dat loaded selected")    
        
        sDat = self.uiDat.dat
        
        print((log_sub(_str_func,mode)))
        if mode == 'all':
            pprint.pprint(sDat)
        elif mode == 'settings':
            pprint.pprint(sDat['settings'])
        else:
            pprint.pprint(sDat[mode])
  
    def uiStatus_fileClear(self):
        self.uiStatus_top(edit=True,bgc = CORESHARE._d_gui_state_colors.get('help'),label = '' )
        self._loadedFile = ""
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        #Declare form frames...------------------------------------------------------
        _MainForm = mUI.MelFormLayout(parent,ut='CGMUITemplate')#mUI.MelColumnLayout(ui_tabs)
        
        
        
        #>>>Objects Load Row ---------------------------------------------------------------------------------------
        _row_status = mUI.MelHSingleStretchLayout(_MainForm)
        mUI.MelSpacer(_row_status, w = 5)
        
        self.uiStatus_top = mUI.MelButton(_row_status,
                                         vis=True,
                                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_get)),
                                         bgc = CORESHARE._d_gui_state_colors.get('help'),
                                         label = 'No Data',
                                         h=20)
        mUI.MelIconButton(_row_status,
                          ann='Clear the loaded file link',
                          image=os.path.join(CGMUI._path_imageFolder,'clear.png') ,
                          w=25,h=25,
                          bgc = CGMUI.guiButtonColor,
                          c = partial(self.uiStatus_fileClear))
        _row_status.setStretchWidget(self.uiStatus_top)
        mUI.MelSpacer(_row_status, w = 5)
        _row_status.layout()
        """
        #self.uiStatus_topRow = mUI.MelHLayout(_MainForm,)
        self.uiStatus_top = mUI.MelButton(_MainForm,
                                         vis=True,
                                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_get)),
                                         bgc = CORESHARE._d_gui_state_colors.get('warning'),
                                         label = 'No Data',
                                         h=20)"""
        _inside = mUI.MelScrollLayout(_MainForm,ut='CGMUITemplate')
        

        
        #Top Section -----------
        self.uiSection_top = mUI.MelColumn(_inside ,useTemplate = 'cgmUISubTemplate',vis=True)         
        self.uiUpdate_top()
  
        #data frame...------------------------------------------------------
        try:self.var_shapeDat_dataFrameCollapse
        except:self.create_guiOptionVar('cgmDat_dataFrameCollapse',defaultValue = 0)
        mVar_frame = self.var_cgmDat_dataFrameCollapse
        
        _frame = mUI.MelFrameLayout(_inside,label = 'Data',vis=True,
                                    collapse=mVar_frame.value,
                                    collapsable=True,
                                    enable=True,
                                    #ann='Contextual MRS functionality',
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:mVar_frame.setValue(0),
                                    collapseCommand = lambda:mVar_frame.setValue(1)
                                    )	
        self.uiFrame_data = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 

        mUI.MelLabel(self.uiFrame_data, label = "Select", h = 13, 
                     ut='cgmUIHeaderTemplate',align = 'center')
        

        #Progress bar... ----------------------------------------------------------------------------
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)

        _row_cgm = CGMUI.add_cgmFooter(_MainForm)            

        #Form Layout--------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_row_status,"top",0),
                        (_row_status,"left",0),
                        (_row_status,"right",0),                        
                        (_inside,"left",0),
                        (_inside,"right",0),
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(_inside,"bottom",0,_row_cgm),
                        (_inside,"top",0,_row_status),
                        ],
                  attachNone = [(_row_cgm,"top")])    
    

#self.uiFunc_dat_get()

#global CGM_RIGBLOCK_DAT
#CGM_DAT = None

#def get_modules_dict(update=False):
#    return get_modules_dat(update)[0]

@cgmGEN.Wrap_exception
def get_ext_options(update = False,debug=None, path= None, skipRoot = True, extensions = ['cgmBlockConfig','cgmBlockDat','cgmShapeDat']):
    """
    Data gather for available blocks.

    :parameters:

    :returns
        _d_modules, _d_categories, _l_unbuildable
        _d_modules(dict) - keys to modules
        _d_categories(dict) - categories to list of entries
        _l_unbuildable(list) - list of unbuildable modules
        
    
    """
    _str_func = 'get_ext_options'    
    #global CGM_RIGBLOCK_DAT

    #if CGM_RIGBLOCK_DAT and not update:
    #    log.debug("|{0}| >> passing buffer...".format(_str_func))          
    #    return CGM_RIGBLOCK_DAT
    
    if debug is not None:
        _b_debug = debug
    else:
        _b_debug = log.isEnabledFor(logging.DEBUG)
        
    if path == None:
        path = os.path.join(startDir_getBase('dev'), 'cgmDat','mrs')
    mPath = PATHS.Path(path)
    _path = mPath.asFriendly()
    
    _l_duplicates = []
    _l_unbuildable = []
    _base = mPath.split()[-1]
    _d_files =  {}
    _d_import = {}
    _d_modules = {}
    _d_types = {}
    
    log.info("|{0}| >> Checking base: {1} | path: {2}".format(_str_func,_base,_path))   
    _i = 0
    
    #cgmGEN.func_snapShot(vars())
    

    for root, dirs, files in os.walk(_path, True, None):
        # Parse all the files of given path and reload python modules
        _mBlock = PATHS.Path(root)
        _split = _mBlock.split()
        _subRoot = _split[-1]
        
        _splitUp = _split[_split.index(_base):]
        
        if skipRoot:
            _splitUp = _splitUp[1:]

        log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        log.debug("|{}| >> On split: {} | {}".format(_str_func,len(_splitUp),_splitUp))   


        for f in files:
            key = False
            
            for t in extensions:
                if f.endswith('.{}'.format(t)):
                    name = f.split('.')[0]
                    #if _i == 'cat':
                    #    key = '.'.join([_base,name])                            
                    #else:
                    key = '.'.join(_splitUp + [name])    
                    log.debug("|{0}| >> ... {1}".format(_str_func,key))
                    
                    if not _d_types.get(t):
                        _d_types[t] = []
                        
                    if name not in list(_d_modules.keys()):
                        _d_files[key] = os.path.join(root,f)
                        _d_types[t].append(key)
                        
                        #_d_import[name] = key
                        
                    else:
                        _l_duplicates.append("{0} >> {1} ".format(key, os.path.join(root,f)))
            _i+=1

    if _b_debug:
        log.info(cgmGEN.logString_sub(_str_func,'Files'))
        pprint.pprint(_d_files)
        log.info(cgmGEN.logString_sub(_str_func,'Types'))
        
        pprint.pprint(_d_types)
        
        #cgmGEN.walk_dat(_d_files,"Files")
        #cgmGEN.walk_dat(_d_types,"Types")
        
        #cgmGEN.walk_dat(_d_import,"Imports")

    if _l_duplicates and _b_debug:
        log.debug(cgmGEN._str_subLine)
        log.debug("|{0}| >> DUPLICATE MODULES....".format(_str_func))
        for m in _l_duplicates:
            print(m)
        raise Exception("Must resolve")
            
    #CGM_RIGBLOCK_DAT = _d_modules, _d_categories, _l_unbuildable
    return _d_files, _d_types