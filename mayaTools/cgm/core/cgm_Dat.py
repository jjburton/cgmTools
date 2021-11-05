"""
cgmDat
Josh Burton 
www.cgmonks.com

"""
__MAYALOCAL = 'CGMDAT'


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
from cgm.core.cgmPy import validateArgs as cgmValid
import cgm.core.classes.GuiFactory as CGMUI
import cgm.core.cgmPy.path_Utils as PATHS
import cgm.core.lib.path_utils as COREPATHS
import cgm.core.lib.shared_data as CORESHARE

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

def startDir_getBase(mode = 'workspace'):
    str_func = 'startDir_get'
    log.debug(log_start(str_func))
    
    if mode == 'workspace':
        return mc.workspace(q=True, rootDirectory=True)
    elif mode == 'file':
        _file = mc.file(q=True, loc=True)
        if not os.path.exists(_file):
            raise ValueError,"Invalid file path: {}".format(_file)
        return os.path.split(_file)[0]

    else:
        raise ValueError,"Unknown mode: {}".format(mode)
    
    
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
        
        if filepath:
            self.read(filepath)
            
    def get(self):
        str_func = 'data.get'
        log.debug(log_start(str_func))
        
    def log_self(self):
        log.info(cgmGEN._str_hardBreak)
        pprint.pprint(self.__dict__)
        
    def log_dat(self):
        log.info(cgmGEN._str_hardBreak)
        pprint.pprint(self.dat)
    
    def set(self):
        str_func = 'data.set'
        log.debug(log_start(str_func))
        
    def startDir_get(self):
        startDir = startDir_getBase(self.structureMode)
        
        if len(self._startDir)>1:
            _path = os.path.join(startDir, os.path.join(*self._startDir))                    
        else:
            _path = os.path.join(startDir, self._startDir[0])        
        
        return _path
    
    def validateFilepath(self, filepath = None, fileMode = 0):
        '''
        Validates a given filepath or generates one with dialog if necessary
        '''        
        if filepath is None:
            startDir = self.startDir_get()
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
        for k,d in self.dat.iteritems():
            dataHolder[k] = d
            
    def fillDat(self, dataHolder = {}):
        for k,d in dataHolder.iteritems():
            self.dat[k] = d

    def write(self, filepath = None, update = False):
        str_func = 'data.write'
        log.debug("|{0}| >>...".format(str_func))
        
        if update:
            filepath = self.str_filepath
            
        filepath = self.validateFilepath(filepath)
        if not filepath:
            log.warning('Invalid path: {0}'.format(filepath))
            
            return False
        log.warning('Write to: {0}'.format(filepath))
            
            
        # =========================
        # write to ConfigObject
        # =========================
        if self.dataformat == 'config':
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
            raise ValueError,"Unknown mode: {}".format(self.mode)
        
        #if update:
        self.str_filepath = filepath
        log.warning('Completed: {} | {}'.format(self._dataformat_resolved,filepath))
        return True
        
    def read(self, filepath = None, decode = True, report = False):
        '''
        Read the Data ConfigObj from file and report the data if so desired.
        ''' 
        str_func = 'data.read'
        log.debug("|{0}| >>...".format(str_func))
        
        mPath = self.validateFilepath(filepath, fileMode = 1)
        
        if not mPath or not mPath.exists():            
            raise ValueError('Given filepath doesnt not exist : %s' % filepath)   
        
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
            except IOError, err:
                self._dataformat_resolved = 'config'
                log.info('JSON : DataMap format failed to load, reverting to legacy ConfigObj')
        # =========================
        # read ConfigObject
        # =========================
        if self._dataformat_resolved == 'config' or self.dataformat == 'config':
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
        
            
        if report:self.log_self()
        self.str_filepath = str(mPath)
        
        return True    
        
def decodeDat(self,dat = None):
    str_func  = 'decodeDat'
    if dat == None:
        dat = self.dat
    
    def processDict(dArg):
        for k,d in dArg.iteritems():
            _type = type(d)
            log.debug(log_msg(str_func, "{} | {}").format(k,_type))            
            if issubclass(_type,list):
                log.debug(log_msg(str_func, "...sublist"))                                                        
                for i,v in enumerate(d):
                    d[i] = r9Core.decodeString(v)
            elif issubclass(_type,dict):
                log.debug(log_msg(str_func, "...subdict"))                                        
                dArg[k] = processDict(d)
            elif issubclass(_type,str) or issubclass(_type,unicode):
                log.debug(log_msg(str_func, "...str"))                                                        
                dArg[k] = r9Core.decodeString(d)
        
        pprint.pprint(dArg)
        return dArg
                
    for k,d in dat.iteritems():
        _type = type(d)
        log.debug(log_msg(str_func, "{} | {}").format(k,_type))
        if issubclass(_type,list):
            log.debug(log_msg(str_func, "...list"))                        
            for i,v in enumerate(d):
                d[i] = r9Core.decodeString(v)
        elif issubclass(_type,dict):
            log.debug(log_msg(str_func, "...dict"))            
            dat[k] = processDict(d)
        elif issubclass(_type,str) or issubclass(_type,unicode):
            dat[k] = r9Core.decodeString(d)
        
    #pprint.pprint(dat)
    
    
class ui(CGMUI.cgmGUI):
    _toolname = 'cgmDat'
    USE_Template = 'CGMUITemplate'
    WINDOW_NAME = "{}UI".format(_toolname)
    WINDOW_TITLE = 'cgmDat | {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 200,300
    
    _datClass = data
    
    def insert_init(self,*args,**kws):
        self._loadedFile = ""
        self.dat = self._datClass()
        
    def build_menus(self):
        self.uiMenu_FileMenu = mUI.MelMenu(l='File', pmc = cgmGEN.Callback(self.buildMenu_file))
        self.uiMenu_SetupMenu = mUI.MelMenu(l='Dev', pmc = cgmGEN.Callback(self.buildMenu_dev))

    def buildMenu_file(self):
        self.uiMenu_FileMenu.clear()                      

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_save_actions,self)))

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save As",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_save_as_actions,self)))
        
        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Load",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_load_actions,self)))
                        
    def buildMenu_dev(self):
        self.uiMenu_SetupMenu.clear()
        _menu = self.uiMenu_SetupMenu
        mUI.MelMenuItem( _menu, l="Dat | self",
                         c=lambda *a: self.dat.log_self())        
        mUI.MelMenuItem( _menu, l="Dat | stored",
                         c=lambda *a: self.dat.log_dat())            
    
    def uiStatus_refresh(self):
        _str_func = 'uiStatus_refresh[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        if not self.dat:
            self.uiStatus_top(edit=True,bgc = CORESHARE._d_gui_state_colors.get('warning'),label = 'No Data')            
            self.uiData_base(edit=True,vis=0)
            self.uiData_base.clear()
            
        else:
            self.uiData_base.clear()
            
            """
            _base = self.dat['base']
            _str = "Source: {}".format(_base['source'])
            self.uiStatus_top(edit=True,bgc = CORESHARE._d_gui_state_colors.get('connected'),label = _str)
            
            self.uiData_base(edit=True,vis=True)
            
            mUI.MelLabel(self.uiData_base, label = "Base", h = 13, 
                         ut='CGMUIHeaderTemplate',align = 'center')
            
            for a in ['type','blockType','shapers','subs']:
                mUI.MelLabel(self.uiData_base, label = "{} : {}".format(a,self.dat['base'].get(a)),
                             bgc = CORESHARE._d_gui_state_colors.get('help'))                
                             """
                
    def uiFunc_dat_get(self):
        _str_func = 'uiFunc_dat_get[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        _sel = mc.ls(sl=1)
        return
        mBlock = BLOCKGEN.block_getFromSelected()
        if not mBlock:
            return log.error("No blocks selected")
        
        sDat = dat_get(mBlock)
        self.dat = sDat
        
        self.uiStatus_refresh()
        if _sel:mc.select(_sel)
 
    def uiFunc_dat(self,mode='Select Source'):
        _str_func = 'uiFunc_dat[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))  
        
        if not self.dat:
            return log.error("No dat loaded selected")

    
    def uiFunc_printDat(self,mode='all'):
        _str_func = 'uiFunc_print[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))  
        
        if not self.dat:
            return log.error("No dat loaded selected")    
        
        sDat = self.dat
        
        print(log_sub(_str_func,mode))
        if mode == 'all':
            pprint.pprint(self.dat)
        elif mode == 'settings':
            pprint.pprint(sDat['settings'])
        elif mode == 'base':
            pprint.pprint(sDat['base'])
        elif mode == 'settings':
            pprint.pprint(sDat['settings'])
        elif mode == 'formHandles':
            pprint.pprint(sDat['handles']['form'])        
        elif mode == 'loftHandles':
            pprint.pprint(sDat['handles']['loft'])  
        elif mode == 'sub':
            pprint.pprint(sDat['handles']['sub'])
        elif mode == 'subShapes':
            pprint.pprint(sDat['handles']['subShapes'])
        elif mode == 'subRelative':
            pprint.pprint(sDat['handles']['subRelative'])            
            
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        #Declare form frames...------------------------------------------------------
        _MainForm = mUI.MelFormLayout(parent,ut='CGMUITemplate')#mUI.MelColumnLayout(ui_tabs)
        
        self.uiStatus_top = mUI.MelButton(_MainForm,
                                         vis=True,
                                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_get)),
                                         bgc = CORESHARE._d_gui_state_colors.get('warning'),
                                         label = 'No Data',
                                         h=20)
        
        _inside = mUI.MelScrollLayout(_MainForm)

        #SetHeader = CGMUI.add_Header('{0}'.format(_strBlock))

        
        
        
        #mc.setParent(_MainForm)
        """
        self.uiStatus_bottom = mUI.MelButton(_MainForm,
                                             bgc=CORESHARE._d_gui_state_colors.get('warning'),
                                             #c=lambda *a:self.uiFunc_updateStatus(),
                                             ann="...",
                                             label='...',
                                             h=20)"""
  
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)

        _row_cgm = CGMUI.add_cgmFooter(_MainForm)            

        #Form Layout--------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(self.uiStatus_top,"top",0),
                        (self.uiStatus_top,"left",0),
                        (self.uiStatus_top,"right",0),                        
                        (_inside,"left",0),
                        (_inside,"right",0),
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(_inside,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])    
    

        self.uiFunc_dat_get()