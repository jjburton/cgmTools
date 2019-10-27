"""
skinDat
Josh Burton 
www.cgmonks.com

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
__version__ = "10.01.2019"
__MAYALOCAL = 'CGMPROJECT'


# From Python =============================================================
import copy
import os
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

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
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as cgmValid
import cgm.core.classes.GuiFactory as cgmUI
import cgm.core.cgmPy.path_Utils as PATHS
import cgm.core.lib.path_utils as COREPATHS
reload(COREPATHS)
import cgm.core.lib.string_utils as CORESTRINGS
import cgm.images as cgmImages
mImagesPath = PATHS.Path(cgmImages.__path__[0])

mUI = cgmUI.mUI

_dataConfigToStored = {'general':'d_project',
                       'enviornment':'d_env',
                       'paths':'d_paths',
                       'anim':'d_animSettings',
                       'world':'d_world',}
                   
                   
l_projectDat = ['name','type','nameStyle']
l_nameConventions = ['none','lower','capital','camelCase']
l_projectTypes = ['asset','unity','unreal','commercial']
l_projectPaths = ['root','content','export','image']

_tangents = ['linear','spline','clamped','flat','plateau','auto']
_fps = [2,3,4,5,6,8,10,12,15,16,20,23.976,
        24,25,29.97,30,40,48,50,
        60,75,80,100,120]

_fpsStrings = ['2', '3', '4', '5', '6', '8', '10', '12', '15', '16', '20', '23.976', '24', '25', '29.97', '30', '40', '48', '50', '60', '75', '80', '100', '120']

_animSettings = [{'n':'frameRate','t':_fpsStrings,'dv':'24'},
                 {'n':'defaultInTangent','t':_tangents,'dv':'linear'},
                 {'n':'defaultOutTangent','t':_tangents,'dv':'linear'},
                 {'n':'weightedTangents','t':'bool','dv':False},
                  ]

_worldSettings = [{'n':'worldUp','t':['y','z'],'dv':'y'},
                  {'n':'linear','t':['milimeter','centimeter','meter',
                                     'inch','foot','yard'],'dv':'centimeter'},
                  {'n':'angular','t':['degrees','radians'],'dv':'degrees'},                   
                   ]

_cameraSettings = [{'n':'nearClip','t':'float','dv':.1},
                    {'n':'farClip','t':'float','dv':100000}]


d_projectFramework = {
    'default':{'Art':['Character','Enviornment','FX','images','mocap_library',
                      'movies','poses','props','ui','visdev'],
               'audio':['BGM','Debug','SFX','UI','design','media','ref']},
    'asset':{''}
}

d_dirFramework = {
'game':{'content':{'art':['Character','Enviornment','FX','images','mocap_library','movies','poses','Props',
                          'UI','visdev'],
                   'audio':['BGM','Debug','SFX','UI']},
         'export':{'art':['Character','DesignParts','Enviornment','FX','Props','UI'],
                   'audio':['BGM','Debug','SFX']}},
'asset':{'content':['templates','rigs','builds','textures'],
         'export':[]}
}

def dirCreateList_get(projectType,dirSet,key = None):
    try:
        _dType = d_dirFramework.get(projectType,{})
        _dDir = _dType.get(dirSet)
        
        if key == None:
            return _dDir
        if issubclass(type(_dDir),list):
            return _dDir
        return _dDir.get(key,[])
    except Exception,err:
        log.error(err)
        
#RangeSlider|MainPlaybackRangeLayout|formLayout9|formLayout13|optionMenuGrp1
#timeField -e -v `playbackOptions -q -ast` RangeSlider|MainPlaybackRangeLayout|formLayout9|timeField2; timeField -e -v `playbackOptions -q -aet` RangeSlider|MainPlaybackRangeLayout|formLayout9|timeField5;

from cgm.lib import (search,
                     names,
                     cgmMath,
                     attributes,
                     rigging,
                     distance,
                     skinning)

def buildFrames(self,parent):
    _str_func = 'buildFrames'
    log.debug("|{0}| >>...".format(_str_func))
        
    d_toDo  = {'world':_worldSettings,
               'anim':_animSettings}
    
    for k,l in d_toDo.iteritems():
        log.debug(cgmGEN.logString_sub(_str_func,k))
        
        _key = 'project{0}DatCollapse'.format(k.capitalize())
        try:self.__dict__['var_'+_key]
        except:self.create_guiOptionVar(_key,defaultValue = 0)
        mVar_frame = self.__dict__['var_'+_key]
        
        _frame = mUI.MelFrameLayout(parent,label = k.capitalize(),vis=True,
                                    collapse=mVar_frame.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = cgmGEN.Callback(mVar_frame.setValue,0),
                                    collapseCommand =  cgmGEN.Callback(mVar_frame.setValue,1),
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate')
        
        
        self.d_tf[k] = {}
        _d = self.d_tf[k]
        
        for d in l:
            log.debug(cgmGEN.logString_msg(_str_func,d))
            
            _type = d.get('t')
            _dv = d.get('dv')
            _name = d.get('n')

            mUI.MelSeparator(_inside,ut='cgmUISubTemplate',h=3)
            
            _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
            mUI.MelSpacer(_row,w=5)                          
            mUI.MelLabel(_row,l='{0}: '.format(CORESTRINGS.capFirst(_name)))
            
            if cgmValid.isListArg(_type):
                
                _d[_name] = mUI.MelOptionMenu(_row,ut = 'cgmUITemplate')
                
                for t in _type:
                    _d[_name].append(t)
        
                #_d[key].selectByIdx(self.setMode,False)                
                _d[_name].setValue(_dv)
            elif _type == 'bool':
                _d[_name] =  mUI.MelCheckBox(_row,
                                              ann='Project settings | {0}'.format(_name))
                _d[_name].setValue(_dv)
                
            else:
                #_rowContextKeys.setStretchWidget( mUI.MelSeparator(_rowContextKeys) )
                _d[_name] =  mUI.MelTextField(_row,
                                            ann='Project settings | {0}'.format(_name),
                                            text = '')
                
            _row.setStretchWidget(_d[_name])
            mUI.MelSpacer(_row,w=5)
            _row.layout()            

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmProjectManager'    
    WINDOW_TITLE = 'cgmProjectManager - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 350,500
    TOOLNAME = 'cgmProjectManager.ui'
    
    def insert_init(self,*args,**kws):
        _str_func = '__init__[{0}]'.format(self.__class__.TOOLNAME)            
        log.info("|{0}| >>...".format(_str_func))        

        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        log.info(self.__call__(q=True, title=True))

        self.__version__ = __version__
        self.__toolName__ = self.__class__.WINDOW_NAME	

        #self.l_allowedDockAreas = []
        self.WINDOW_TITLE = self.__class__.WINDOW_TITLE
        self.DEFAULT_SIZE = self.__class__.DEFAULT_SIZE
        
        self.pathProject = None
        self.mDat = data()
        self.path_projectConfig = None
        
        self.var_project = cgmMeta.cgmOptionVar('cgmVar_projectCurrent',defaultValue = '')
        self.var_pathProject = cgmMeta.cgmOptionVar('cgmVar_projectPath',defaultValue = '')
        self.var_pathLastProject = cgmMeta.cgmOptionVar('cgmVar_projectLastPath',defaultValue = '')
        
        self.mPathList = cgmMeta.pathList('cgmProjectPaths')
        
        self.d_tf = {}
        
    
    def uiProject_new(self):
        _str_func = 'uiProject_new'
        log.debug("|{0}| >>...".format(_str_func))        
        
        
        result = mc.promptDialog(
                title="New Project",
                message='Enter Name for a new Project',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
        
        if result == 'OK':
            _name = mc.promptDialog(query=True, text=True)
            self.mDat = data(_name)
            
            #self.mDat.write()
            self.uiProject_save()
            self.uiProject_load(revert=True)
                
                
    def uiProject_pushPaths(self):
        _str_func = 'uiProject_load'
        log.debug("|{0}| >>...".format(_str_func))        
        
        mPath = PATHS.Path( self.d_tf['paths']['content'].getValue() )
        if mPath.exists():
            mel.eval('setProject "{0}";'.format(mPath.asString()))
        else:
            log.error('Invalid Path: {0}'.format(mPath))
            
            
    def uiProject_toScene(self):
        _str_func = 'uiProject_toScene'
        log.debug("|{0}| >>...".format(_str_func))
        
        cgmMeta.cgmOptionVar('cgmVar_sceneUI_export_directory').setValue(self.d_tf['paths']['export'].getValue())
        cgmMeta.cgmOptionVar('cgmVar_sceneUI_last_directory').setValue(self.d_tf['paths']['content'].getValue())
        
        import cgm.core.mrs.Scene as SCENE
        SCENE.ui()
        
    def uiProject_load(self,path=None,revert=False):
        _str_func = 'uiProject_load'
        log.info("|{0}| >>...".format(_str_func))
        
        if path == None and revert is True:
            path = self.path_projectConfig or self.mDat.str_filepath
            
        #if revert is not True:
        self.mDat.read(path)
        
        for dType in ['general','anim','paths']:
            log.debug(cgmGEN.logString_sub(_str_func,dType))
            
            for k,v in self.mDat.__dict__[_dataConfigToStored[dType]].iteritems():
                try:
                    log.info(cgmGEN.logString_msg(_str_func,"{0} | {1}".format(k,v)))
                    _type = type(self.d_tf[dType][k])
                    if _type not in [mUI.MelOptionMenu]:
                        try:self.d_tf[dType][k].clear()
                        except:pass
                        
                        
                        if v is not None:
                            self.d_tf[dType][k].setValue(v)
                except Exception,err:
                    log.error("Missing data field or failure: {0}".format(k))
                    log.error("err | {0}".format(err))                
                
                
            """            
            log.debug(cgmGEN.logString_sub(_str_func,"general"))
            for k,v in self.mDat.d_project.iteritems():
                log.info(cgmGEN.logString_msg(_str_func,"{0} | {1}".format(k,v)))
                try:
                    self.d_tf['general'][k].setValue(v)
                except Exception,err:
                    log.error("Missing data field: {0}".format(k))
                    log.error("err | {0}".format(err))
                    
                    #mUi.setValue(v)
     
     
            log.debug(cgmGEN.logString_sub(_str_func,"paths"))
            for k,v in self.mDat.d_paths.iteritems():
                log.info(cgmGEN.logString_msg(_str_func,"{0} | {1}".format(k,v)))
                
                try:
                    self.d_tf['paths'][k].setValue(v)
                except Exception,err:
                    log.error("Missing data field: {0}".format(k))
                    log.error("err | {0}".format(err))
            
            """        
        #Set maya project path
        log.debug(cgmGEN.logString_sub(_str_func,"Push Paths..."))
        self.uiProject_pushPaths()
        
        log.debug(cgmGEN.logString_sub(_str_func,"PathList append: {0}".format(self.mDat.str_filepath)))
        
        self.path_projectConfig = self.mDat.str_filepath
        self.mPathList.append(self.mDat.str_filepath)
        self.mPathList.log_self()        
        
        
        #Set pose path
        
        #Update file dir
        self.uiScrollList_dirContent.rebuild( self.mDat.d_paths.get('content'))
        self.uiScrollList_dirExport.rebuild(self.mDat.d_paths.get('export'))
        
        #Project image
        log.debug(cgmGEN.logString_sub(_str_func,"Image..."))        
        self.reload_headerImage()
        
        #self.uiImage_Project= mUI.MelImage(imageRow,w=350, h=50)
        
        #self.uiImage_Project.setImage(mThumb)
        

        log.info(True)
        self.var_pathLastProject.value = self.mDat.str_filepath
    
    def reload_headerImage(self):
        _str_func = 'reload_headerImage'
        log.info("|{0}| >>...".format(_str_func))
        
        _path = PATHS.Path(self.d_tf['paths']['image'].getValue())
        if _path.exists():
            log.warning('Image path: {0}'.format(_path))
            _imagePath = _path
        else:
            _imagePath = os.path.join(mImagesPath.asFriendly(),
                                      'cgm_project_{0}.png'.format(self.d_tf['general']['type'].getValue()))
            
        self.uiImage_Project.setImage(_imagePath)        
        
    def uiProject_save(self, path = None, updateFile = True):
        _str_func = 'uiProject_save'
        log.debug("|{0}| >>...".format(_str_func))
        
        if path == None and updateFile == True:
            if self.mDat.str_filepath:
                log.info("|{0}| >> Saving to existing mDat: {1}".format(_str_func,self.mDat.str_filepath))
                path = self.mDat.str_filepath        
            
            
        for dType,d in _dataConfigToStored.iteritems():
            if dType in ['enviornment']:
                continue
            
            log.debug(cgmGEN.logString_sub(_str_func,"{0} | {1}".format(dType,d)))
            
            for k,ui in self.d_tf[dType].iteritems():
                self.mDat.__dict__[d][k] = ui.getValue()            
            
        """
        for k,ui in self.d_tf['general'].iteritems():
            self.mDat.d_project[k] = ui.getValue()

        for k,ui in self.d_tf['paths'].iteritems():
            self.mDat.d_paths[k] = ui.getValue()
            """
        self.mDat.log_self()
        self.mDat.write( path)
        
    def uiProject_saveAs(self):
        _str_func = 'uiProject_saveAs'
        log.debug("|{0}| >>...".format(_str_func))
        
        self.uiProject_save(None,False)
        
    def uiProject_revert(self):
        _str_func = 'uiProject_revert'
        log.debug("|{0}| >>...".format(_str_func))
        
        self.uiProject_load(None,True)    
    

    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))
        self.uiMenu_utils = mUI.MelMenu(l='Utils', pmc = cgmGEN.Callback(self.buildMenu_utils))
        
        self.uiMenu_help = mUI.MelMenu(l='Help', pmc = cgmGEN.Callback(self.buildMenu_help))
        
    def buildMenu_utils(self):
        self.uiMenu_utils.clear()
        
        #>>> Reset Options		                     
        mUI.MelMenuItemDiv( self.uiMenu_utils, label='Send To...' )
        mUI.MelMenuItem( self.uiMenu_utils, l="Scene",
                         c = lambda *a:mc.evalDeferred(self.uiProject_toScene,lp=True))

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        
        #>>> Reset Options		                     
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu, label='Project' )
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="New",
                         c = lambda *a:mc.evalDeferred(self.uiProject_new,lp=True))        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Load",
                         c = lambda *a:mc.evalDeferred(self.uiProject_load,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Save ",
                         c = lambda *a:mc.evalDeferred(self.uiProject_save,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Save As",
                         c = lambda *a:mc.evalDeferred(self.uiProject_saveAs,lp=True))        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Revert",
                         c = lambda *a:mc.evalDeferred(self.uiProject_revert,lp=True))
        
        self.mPathList.verify()
        _recent = mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Recent",subMenu=True)
        for i,p in enumerate(self.mPathList.l_paths):
            mUI.MelMenuItem(_recent,
                            label = PATHS.Path(p).asTruncate(2,3),
                            ann = "Set the project to: {0} | {1}".format(i,p),
                            c=cgmGEN.Callback(self.uiProject_load,p))
            
        mUI.MelMenuItemDiv(_recent)
        mUI.MelMenuItem(_recent,
                        label = "Clear Recent",
                        ann="Clear the recent projects",
                        c=cgmGEN.Callback(self.mPathList.clear))        
        
        
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu, label='Settings' )
        #uiMenuItem_matchMode(self,self.uiMenu_FirstMenu)
        
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu, label='Utils' )
        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Dock",
                         c = lambda *a:self.do_dock())        

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
        
        _log = mUI.MelMenuItem( self.uiMenu_help, l="Logs:",subMenu=True)
        
        
        mUI.MelMenuItem( _log, l="Dat",
                         c=lambda *a: self.mDat.log_self())
        mUI.MelMenuItem( _log, l="PathList",
                         c=lambda *a: self.mPathList.log_self())
        
        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("https://http://docs.cgmonks.com/mrs.html");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )   

        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
    
        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        
        _column = mUI.MelScrollLayout(parent=_MainForm)
        self.bUI_main(_column)
        #self.mManager = manager(parent = _column)
        
        #for k in self.__dict__.keys():
        #    if str(k).startswith('var_'):
        #        self.mManager.__dict__[k] = self.__dict__[k]
        
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)            
        _MainForm(edit = True,
                  af = [(_column,"top",0),
                        (_column,"left",0),
                        (_column,"right",0),
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [#(_column,"top",2,_context),
                        (_column,"bottom",2,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])
        
        
        #Attempting to autoload our last
        mPath = PATHS.Path(self.var_pathLastProject.value )
        if mPath.exists():
            try:
                self.uiProject_load(mPath)        
            except Exception,err:
                log.error("Failed to load last: {0} | {1}".format(mPath, err))
                
    def bUI_main(self,parent):
        #self.mLabel_projectName = mUI.MelLabel(parent,label='Project X'.upper(), al = 'center', ut = 'cgmUIHeaderTemplate')
        
        
        '''
        #Pose Path ===============================================================================
        uiRow_pose = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate')
        self.uiPop_root = None
        
        mUI.MelSpacer(uiRow_pose,w=2)    
        
        mUI.MelLabel(uiRow_pose,label='Root:')
        mUI.MelSpacer(uiRow_pose,w=2)    
        """
        self.uiField_path = mUI.MelLabel(uiRow_pose,
                                         ann='Change the current path',
                                         label = 'None',
                                         ut='cgmUIInstructionsTemplate',w=100) """   
        
        
        self.tf_projectPath = mUI.MelTextField(uiRow_pose,
                                               ann='The root path for our project',
                                               #cc = lambda *x:self._uiCB_setPosePath(field=False),
                                               text = '')
                                                 
        uiRow_pose.setStretchWidget(self.tf_projectPath)
        
        mc.button(parent=uiRow_pose,
                  l = 'Set Path',
                  ut = 'cgmUITemplate',
                  c= lambda *x:self.uiCB_setProjectPath(fileDialog=True),
                  #en = _d.get('en',True),
                  #c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                  #ann = _d.get('ann',b))
                  )
        """
        mc.button(parent=uiRow_pose,
                  l = 'Test',
                  ut = 'cgmUITemplate',
                  c= lambda *x:log.info("Mode: {0} | local: {1} | project: {2}".format(self.var_pathMode.getValue(),self.posePathLocal, self.posePathProject)),
                  )"""
        mUI.MelSpacer(uiRow_pose,w=2)
        uiRow_pose.layout()
        mc.setParent(self)
        '''
        
        # Image
        _imageFailPath = os.path.join(mImagesPath.asFriendly(),'cgm_project.png')
        imageRow = mUI.MelHRowLayout(parent,bgc=[.6,.3,.3])
        
        #mUI.MelSpacer(imageRow,w=10)
        self.uiImage_Project= mUI.MelImage(imageRow,w=350, h=50)
        self.uiImage_Project.setImage(_imageFailPath)
        #mUI.MelSpacer(imageRow,w=10)	
        imageRow.layout()        
        
        #self.uiPopup_setPath()
        
        self.buildFrame_baseDat(parent)
        self.buildFrame_paths(parent)
        buildFrames(self,parent)
        
        #self.buildFrame_content(parent)
        buildFrame_dirContent(self,parent)
        buildFrame_dirExport(self,parent)
        
    def uiCB_setProjectPath(self, path=None, field = False, fileDialog=False):
        '''
        Manage the PosePath textfield and build the PosePath
        '''
        _str_func = 'uiCB_setProjectPath'
        
        mVar = self.var_pathProject
    
        if not path and not field and not fileDialog:
            self.pathProject = mVar.getValue()
        
        if path:
            self.pathProject = path
            
        elif fileDialog:
            log.debug("|{0}| >> file dialog mode...".format(_str_func))
            try:
                if r9Setup.mayaVersion() >= 2011:
                    _dir = self.tf_projectPath.getValue() or ''
                    log.debug("|{0}| >> dir: {1}".format(_str_func,_dir))                    
                    self.pathProject = mc.fileDialog2(fileMode=3,
                                                   dir=_dir)[0]
                else:
                    print 'Sorry Maya2009 and Maya2010 support is being dropped'
                    def setPosePath(fileName, fileType):
                        self.pathProject = fileName
                    mc.fileBrowserDialog(m=4, fc=setPosePath, ft='image', an='setPoseFolder', om='Import')
            except Exception,err:
                log.warning('No Folder Selected or Given | {0}'.format(err))
        elif field:
            self.pathProject = self.tf_projectPath.getValue()
        
        if not PATHS.Path(self.pathProject):
            log.error("|{0}| >> Invalid path: {1}".format(_str_func,self.pathProject))            
            self.pathProject = ''
            return 
        
        mVar.setValue(self.pathProject)
        
        self.tf_projectPath.setValue(self.pathProject,executeChangeCB=False)
        self.tf_projectPath(edit=True, ann = self.pathProject)
        


        #self.uiScrollList_dir.rebuild(self.posePath)

        return    
    
    def buildFrame_baseDat(self,parent):
        try:self.var_projectBaseDatCollapse
        except:self.create_guiOptionVar('projectBaseDatCollapse',defaultValue = 0)
        mVar_frame = self.var_projectBaseDatCollapse
        
        _frame = mUI.MelFrameLayout(parent,label = 'General',vis=True,
                                    collapse=mVar_frame.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:mVar_frame.setValue(0),
                                    collapseCommand = lambda:mVar_frame.setValue(1)
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
        
        #>>>Hold ===================================================================================== 
        cgmUI.add_LineSubBreak()
        self.d_tf['general'] = {}
        _d = self.d_tf['general']
        for key in l_projectDat:
            mUI.MelSeparator(_inside,ut='cgmUISubTemplate',h=3)
            
            _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
            mUI.MelSpacer(_row,w=5)                          
            mUI.MelLabel(_row,l='{0}: '.format(CORESTRINGS.capFirst(key)))            
            if key == 'type':
                _d[key] = mUI.MelOptionMenu(_row,ut = 'cgmUITemplate')
                for t in l_projectTypes:
                    _d[key].append(t)
        
                #_d[key].selectByIdx(self.setMode,False)                
            elif key =='nameStyle':
                _d[key] = mUI.MelOptionMenu(_row,ut = 'cgmUITemplate')
                for t in l_nameConventions:
                    _d[key].append(t)                
                
            else:
                #_rowContextKeys.setStretchWidget( mUI.MelSeparator(_rowContextKeys) )
                _d[key] =  mUI.MelTextField(_row,
                                            ann='Project settings | {0}'.format(key),
                                            text = '')
                
            _row.setStretchWidget(_d[key])
            mUI.MelSpacer(_row,w=5)
            _row.layout()

    def buildFrame_paths(self,parent):
        try:self.var_projectPathsCollapse
        except:self.create_guiOptionVar('projectPathsCollapse',defaultValue = 0)
        mVar_frame = self.var_projectPathsCollapse
        
        _frame = mUI.MelFrameLayout(parent,label = 'Paths',vis=True,
                                    collapse=mVar_frame.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:mVar_frame.setValue(0),
                                    collapseCommand = lambda:mVar_frame.setValue(1)
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
        
        #>>>Hold ===================================================================================== 
        cgmUI.add_LineSubBreak()
        self.d_tf['paths'] = {}
        _d = self.d_tf['paths']
        
        for key in l_projectPaths:
            mUI.MelSeparator(_inside,ut='cgmUISubTemplate',h=3)
            
            _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

            mUI.MelSpacer(_row,w=5)                          
            mUI.MelLabel(_row,l='{0}: '.format(CORESTRINGS.capFirst(key)))            
            #_rowContextKeys.setStretchWidget( mUI.MelSeparator(_rowContextKeys) )
            _d[key] =  mUI.MelTextField(_row,
                                        ann='Project Path | {0}'.format(key),
                                        text = '')
            
            mc.button(parent=_row,
                      l = 'Set',
                      ut = 'cgmUITemplate',
                      c = cgmGEN.Callback(self.uiButton_setPathToTextField,key)
                      #en = _d.get('en',True),
                      #c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                      #ann = _d.get('ann',b))
                      )            
            
            _row.setStretchWidget(_d[key])
            mUI.MelSpacer(_row,w=5)
            _row.layout()

    def buildFrame_content(self,parent):
        try:self.var_projectContentCollapse
        except:self.create_guiOptionVar('projectContentCollapse',defaultValue = 0)
        mVar_frame = self.var_projectContentCollapse
        
        _frame = mUI.MelFrameLayout(parent,label = 'Content',vis=True,
                                    collapse=mVar_frame.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:mVar_frame.setValue(0),
                                    collapseCommand = lambda:mVar_frame.setValue(1)
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
        
        return
        #>>>Hold ===================================================================================== 
        cgmUI.add_LineSubBreak()
        self.d_tf['content'] = {}
        _d = self.d_tf['paths']
        
        for key in l_projectPaths:
            _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

            mUI.MelSpacer(_row,w=5)                          
            mUI.MelLabel(_row,l='{0}: '.format(key))
            #_rowContextKeys.setStretchWidget( mUI.MelSeparator(_rowContextKeys) )
            _d[key] =  mUI.MelTextField(_row,
                                        ann='Project Path | {0}'.format(key),
                                        text = '')
            
            mc.button(parent=_row,
                      l = 'Set',
                      ut = 'cgmUITemplate',
                      c = cgmGEN.Callback(self.uiButton_setPathToTextField,key)
                      #c = lambda *x:self.uiButton_setPathToTextField(key),
                      #c= lambda *x:self.uiCB_setProjectPath(fileDialog=True),
                      #en = _d.get('en',True),
                      #c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                      #ann = _d.get('ann',b))
                      )            
            
            _row.setStretchWidget(_d[key])
            mUI.MelSpacer(_row,w=5)
            _row.layout()
    
    def uiButton_setPathToTextField(self,key):
        basicFilter = "*"
        if key in ['image']:
            x = mc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, fm=1)
        else:
            x = mc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, fm=3)
        if x:
            self.d_tf['paths'][key].setValue( x[0] )
            #self.optionVarExportDirStore.setValue( self.exportDirectory )    
            
            if key in ['image']:
                self.reload_headerImage()
                
def uiProject_addDir(self,pSet = None, mScrollList = None):
    _str_func = 'uiProject_addDir'
    log.debug("|{0}| >>...".format(_str_func))
    

    if pSet == None:
        raise ValueError,"Must have directory set arg. Most likely: export/content"
    
    _path = self.d_tf['paths'].get(pSet).getValue()
    mPath = PATHS.Path(_path)
    
    if not mPath.exists():
        raise ValueError,"Invalid Path: {0}".format(_path)
    
    log.debug(cgmGEN.logString_msg(_str_func,'Path: {0}'.format(mPath)))
    

    promptstring = 'Add {0} Dir '.format(pSet)
    
    result = mc.promptDialog(
            title=promptstring,
            message='Enter Name for {1} dir: \n Path: {0}'.format(mPath.asFriendly(),pSet),
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')
    
    if result == 'OK':
        subFolder = mc.promptDialog(query=True, text=True)
        
        mDir =  PATHS.Path( os.path.join(mPath, subFolder))
        if not mDir.exists():
            os.makedirs(mDir)
            log.warning("created dir: {0}".format(mDir))
        else:
            log.warning("Dir already exists: {0}".format(mDir))
            
        if mScrollList:
            mScrollList.rebuild()
            
def uiProject_verifyDir(self,pSet = None,pType = None, mScrollList = None):
    _str_func = 'uiProject_verifyDir'
    log.debug("|{0}| >>...".format(_str_func))
    
    if pType == None:
        pType = self.d_tf['general']['type'].getValue()
        
    if pType in ['unity','unreal']:
        pType = 'game'
        
    log.debug(cgmGEN.logString_msg(_str_func,'pType: {0}'.format(pType)))
    
    if pSet == None:
        raise ValueError,"Must have directory set arg. Most likely: export/content"
    
    _path = self.d_tf['paths'].get(pSet).getValue()
    mPath = PATHS.Path(_path)
    
    if not mPath.exists():
        raise ValueError,"Invalid Path: {0}".format(_path)
    
    log.debug(cgmGEN.logString_msg(_str_func,'Path: {0}'.format(mPath)))
    
    _dat = dirCreateList_get(pType,pSet)
    pprint.pprint(_dat)
    _type = type(_dat)
    
    if issubclass(_type,dict):
        log.debug(cgmGEN.logString_msg(_str_func,'dict...'))
        for k,l in _dat.iteritems():
            
            mDir =  PATHS.Path( os.path.join(mPath, k))
            if not mDir.exists():
                os.makedirs(mDir)
                log.warning("created dir: {0}".format(mDir))
                
            
            for k2 in l:
                #if case == 'lower':
                    #k2 = k2.lower()
                    
                mSub = PATHS.Path( os.path.join(mPath, k, k2))
                if not mSub.exists():
                    os.makedirs(mSub)
                    log.warning("created dir: {0}".format(mSub))               
            
    else:
        log.debug(cgmGEN.logString_msg(_str_func,'list...'))
        
        for k in _dat:
            #if case == 'lower':
                #k2 = k2.lower()
                
            mSub = PATHS.Path( os.path.join(mPath, k))
            if not mSub.exists():
                os.makedirs(mSub)
                log.warning("created dir: {0}".format(mSub))          
        
    if mScrollList:
        mScrollList.rebuild()

    
def buildFrame_dirContent(self,parent):
    try:self.var_projectDirContentFrameCollapse
    except:self.create_guiOptionVar('projectDirContentFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_projectDirContentFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Content',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    
    self.uiFrame_dirContent = _frame
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate')
    
    #Utils -------------------------------------------------------------------------------------------
    _row = mUI.MelHLayout(_inside,padding=10,)
    button_clear = mUI.MelButton(_row,
                                   label='Clear',ut='cgmUITemplate',
                                    c=lambda *a:self.uiScrollList_dirContent.clearSelection(),
                                    ann='Clear selection the scroll list to update')     
    button_refresh = mUI.MelButton(_row,
                                   label='Refresh',ut='cgmUITemplate',
                                    c=lambda *a:self.uiScrollList_dirContent.rebuild(),
                                    ann='Force the scroll list to update')
    
    button_add= mUI.MelButton(_row,
                              label='Add',ut='cgmUITemplate',
                               ann='Add a subdir to the path root')    
    
    button_verify = mUI.MelButton(_row,
                                   label='Verify Dir',ut='cgmUITemplate',
                                    ann='Verify the directories from the project Type')    
    _row.layout()
    #--------------------------------------------------------------------------------------------
    
    mUI.MelSeparator(_inside,ut='cgmUISubTemplate',h=3)
    
    
    _textField = mUI.MelTextField(_inside,
                                  ann='Filter',
                                  w=50,
                                  bgc = [.3,.3,.3],
                                  en=True,
                                  text = '')    
    
    
    
    #Scroll list
    mScrollList = cgmProjectDirList(_inside, ut='cgmUISubTemplate',
                                    allowMultiSelection=0,en=True,
                                    ebg=0,
                                    h=200,
                                    bgc = [.2,.2,.2],
                                    w = 50)
    
    #Connect the functions to the buttons after we add the scroll list...
    button_verify(edit=True,
                  c=lambda *a:uiProject_verifyDir(self,'content',None,mScrollList),)
    button_add(edit=True,
               c=lambda *a:uiProject_addDir(self,'content',mScrollList),
               )
    
    try:mScrollList(edit=True,hlc = [.5,.5,.5])
    except:pass
    
    mScrollList.set_filterObj(_textField)
    _textField(edit=True,
               tcc = lambda *a: mScrollList.update_display())    
   
    #mScrollList.set_selCallBack(mrsPoseDirSelect,mScrollList,self)
    
    self.uiScrollList_dirContent = mScrollList

    

def buildFrame_dirExport(self,parent):
    try:self.var_projectDirExportFrameCollapse
    except:self.create_guiOptionVar('projectDirExportFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_projectDirExportFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Export',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    
    self.uiFrame_dirExport = _frame
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate')
    
    #Utils -------------------------------------------------------------------------------------------
    _row = mUI.MelHLayout(_inside,padding=10,)
    button_clear = mUI.MelButton(_row,
                                   label='Clear',ut='cgmUITemplate',
                                    c=lambda *a:self.uiScrollList_dirContent.clearSelection(),
                                    ann='Clear selection the scroll list to update')     
    button_refresh = mUI.MelButton(_row,
                                   label='Refresh',ut='cgmUITemplate',
                                    c=lambda *a:self.uiScrollList_dirContent.rebuild(),
                                    ann='Force the scroll list to update')
    
    button_add= mUI.MelButton(_row,
                              label='Add',ut='cgmUITemplate',
                               ann='Add a subdir to the path root')    
    
    button_verify = mUI.MelButton(_row,
                                   label='Verify Dir',ut='cgmUITemplate',
                                    ann='Verify the directories from the project Type')    
    _row.layout()
    #--------------------------------------------------------------------------------------------    
    
    
    
    _textField = mUI.MelTextField(_inside,
                                  ann='Filter',
                                  w=50,
                                  bgc = [.3,.3,.3],
                                  en=True,
                                  text = '')    
    
    
    
    #Scroll list
    mScrollList = cgmProjectDirList(_inside, ut='cgmUISubTemplate',
                                    allowMultiSelection=0,en=True,
                                    ebg=0,
                                    h=200,
                                    bgc = [.2,.2,.2],
                                    w = 50)
    
    try:mScrollList(edit=True,hlc = [.5,.5,.5])
    except:pass
    
    
    #Connect the functions to the buttons after we add the scroll list...
    button_verify(edit=True,
                  c=lambda *a:uiProject_verifyDir(self,'content',None,mScrollList),)
    button_add(edit=True,
               c=lambda *a:uiProject_addDir(self,'content',mScrollList),
               )    
    
    mScrollList.set_filterObj(_textField)
    _textField(edit=True,
               tcc = lambda *a: mScrollList.update_display())    
    
    #_scrollList.set_selCallBack(mrsPoseDirSelect,_scrollList,self)
    
    self.uiScrollList_dirExport = mScrollList

    _row = mUI.MelHLayout(_inside,padding=5,)
    button_refresh = mUI.MelButton(_row,
                                   label='Clear Sel',ut='cgmUITemplate',
                                    c=lambda *a:self.uiScrollList_dirExport.clearSelection(),
                                    ann='Clear selection the scroll list to update')     
    button_refresh = mUI.MelButton(_row,
                                   label='Refresh',ut='cgmUITemplate',
                                    c=lambda *a:self.uiScrollList_dirExport.rebuild(),
                                    ann='Force the scroll list to update')    
    _row.layout()

class data(object):
    '''
    Class to handle skin data. Utilizes red9.packages.ConfigObj for storage format. Storing what might be an excess of info
    to make it more useful down the road for applying skinning data to meshes that don't have the same vert counts or joint counts.
    
    :param sourchMesh: Mesh to export data from
    :param targetMesh: Mesh to import data to
    :param filepath: File to read on call or via self.read() call to browse to one
    
    '''    

    #_geoToComponent = {'mesh':'vtx'}
    
    
    def __init__(self, project = None, filepath = None, **kws):
        """

        """        
        self.str_filepath = None
        self.d_env = {}#cgmGEN.get_mayaEnviornmentDict()
        self.d_env['file'] = mc.file(q = True, sn = True)
        
        for k,d in _dataConfigToStored.iteritems():
            log.debug("initialze: {0}".format(k))
            self.__dict__[d] = {}
        
        if filepath is not None:
            try:self.read(filepath)
            except Exception,err:log.error("data Filepath failed to read | {0}".format(err))
            
            
        return
        if sourceMesh is not None:
            self.validateSourceMesh(sourceMesh)
        if targetMesh is not None:
            self.validateTargetMesh(targetMesh)
        if sourceMesh is None and targetMesh is None and mc.ls(sl=True):
            self.validateSourceMesh(sourceMesh)

    def validateFilepath(self, filepath = None, fileMode = 0):
        '''
        Validates a given filepath or generates one with dialog if necessary
        '''        
        if filepath is None:
            startDir = mc.workspace(q=True, rootDirectory=True)
            filepath = mc.fileDialog2(dialogStyle=2, fileMode=fileMode, startingDirectory=startDir,
                                      fileFilter='Config file (*.cfg)')
            if filepath:filepath = filepath[0]
            
        if filepath is None:
            return False
        
        mFile = PATHS.Path(filepath)
        self.str_filepath = mFile.asFriendly()
        log.info("filepath validated...")        
        return mFile

    def write(self, filepath = None, update = False):
        '''
        Write the Data ConfigObj to file
        '''
        _str_func = 'data.write'
        log.debug("|{0}| >>...".format(_str_func))
        
        if update:
            filepath = self.str_filepath
            
        filepath = self.validateFilepath(filepath)
            
        ConfigObj = configobj.ConfigObj(indent_type='\t')
        ConfigObj['configType']= 'cgmProject'
        
        for k,d in _dataConfigToStored.iteritems():
            log.debug("Dat: {0}".format(k))
            ConfigObj[k] = self.__dict__[d] 
        
        ConfigObj.filename = filepath
        ConfigObj.write()
        
        if update:
            self.str_filepath = filepath
        return True
        
    def read(self, filepath = None, report = False):
        '''
        Read the Data ConfigObj from file and report the data if so desired.
        ''' 
        _str_func = 'data.read'
        log.debug("|{0}| >>...".format(_str_func))
        
        mPath = self.validateFilepath(filepath, fileMode = 1)
        
        if not mPath.exists():            
            raise ValueError('Given filepath doesnt not exist : %s' % mPath)   
        
        _config = configobj.ConfigObj(mPath.asFriendly())
        #if _config.get('configType') != 'cgmSkinConfig':
            #raise ValueError,"This isn't a cgmSkinConfig config | {0}".format(filepath)
                
        for k in _dataConfigToStored.keys():
            if _config.has_key(k):
                self.__dict__[_dataConfigToStored[k]] = _config[k]
            else:
                log.error("Config file missing section {0}".format(k))
                return False
            
        if report:self.log_self()
        self.str_filepath = str(mPath)
        
        return True
    
    def log_self(self):
        _d = copy.copy(self.__dict__)
        pprint.pprint(_d)
        

class cgmProjectDirList(mUI.BaseMelWidget):
    '''
    NOTE: you probably want to use the MelObjectScrollList instead!
    '''
    WIDGET_CMD = mc.iconTextScrollList
    KWARG_CHANGE_CB_NAME = 'sc'

    ALLOW_MULTI_SELECTION = False
    def __new__( cls, parent, *a, **kw ):
        if 'ams' not in kw and 'allowMultiSelection' not in kw:
            kw[ 'ams' ] = cls.ALLOW_MULTI_SELECTION
        return mUI.BaseMelWidget.__new__( cls, parent, *a, **kw )
    
    def __init__( self, parent, *a, **kw ):
        mUI.BaseMelWidget.__init__( self, parent, *a, **kw )
        self._appendCB = None
        self._items = []
        self._l_strings = []
        self._l_itc = []
        self._d_itc =  {}
        self.filterField = None
        self.b_selCommandOn = True
        
        self._l_uiKeys = []
        self._l_uiStrings = []
        self._l_paths = []
        self.path = kw.get('path',None)
        
        self.rebuild()
        self.cmd_select = None
        self(e=True, sc = self.selCommand)
        
        self.uiPopUpMenu = None
        
        self.set_selCallBack(self.select_popup)
        
    def __getitem__( self, idx ):
        return self.getItems()[ idx ]

    def setItems( self, items ):
        self.clear()
        for i in items:
            self.append( i )
            
    def getItems( self ):
        return self._items
        
    def getSelectedItems( self ):
        return self( q=True, si=True ) or []
        
    def getSelectedIdxs( self, process = True ):
        _res = [ idx-1 for idx in self( q=True, sii=True ) or [] ]
        if not process:
            return _res
        
        _indices = []
        for i in _res:
            _indices.append(int(str(i).split('L')[0]))
        return _indices
    def selectByIdx( self, idx ):
        self( e=True, selectIndexedItem=idx+1 )  #indices are 1-based in mel land - fuuuuuuu alias!!!

    def selectByValue( self, value):
        self( e=True, selectItem=value )

    def append( self, item ):
        self( e=True, append=item )
        self._items.append(item)
        
    def appendItems( self, items ):
        for i in items: self.append( i )
        
    def allowMultiSelect( self, state ):
        self( e=True, ams=state )
    
    def report(self):
        log.debug(cgmGEN.logString_start('report'))                
        log.info("Dat: "+cgmGEN._str_subLine)
        return
        for i,mObj in enumerate(self._l_dat):
            print ("{0} | {1} | {2}".format(i,self._l_strings[i],mObj))
            
        log.info("Loaded "+cgmGEN._str_subLine)
        for i,mObj in enumerate(self._ml_loaded):
            print("{0} | {1}".format(i, mObj))
            
        pprint.pprint(self._ml_scene)
        
    def set_selCallBack(self,func,*args,**kws):
        log.debug(cgmGEN.logString_start('set_selCallBack'))                
        self.cmd_select = func
        self.selArgs = args
        self.selkws = kws
        
        log.debug(cgmGEN.logString_msg('set_selCallBack',"cmd: {0}".format(self.cmd_select)))                
        log.debug(cgmGEN.logString_msg('set_selCallBack',"args: {0}".format(self.selArgs)))                
        log.debug(cgmGEN.logString_msg('set_selCallBack',"kws: {0}".format(self.selkws)))                
        
    def uiPath_openDir(self,path=None):
        import subprocess
        _path = os.path.normpath(path)
        subprocess.Popen('explorer "%s"' % _path)
        
        
    def uiPath_mayaOpen(self,path=None):
        _res = mc.fileDialog2(fileMode=1, dir=path)
        if _res:
            log.warning("Opening: {0}".format(_res[0]))
            mc.file(_res[0], o=True, f=True, pr=True)
        
        
    def uiPath_addDir(self, path = None):
        '''
        Insert a new SubFolder to the path, makes the dir and sets
        '''
        mPath = PATHS.Path(path)
        if not mPath.exists():
            raise StandardError('Invalid Path: {0}'.format(path))
        
        promptstring = 'Add Dir '.format(mPath.asFriendly())
        
        result = mc.promptDialog(
                title=promptstring,
                message='Enter Name: \n Path: {0}'.format(mPath.asFriendly()),
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
        
        if result == 'OK':
            subFolder = mc.promptDialog(query=True, text=True)
            
            mDir =  PATHS.Path( os.path.join(mPath, subFolder))
            if not mDir.exists():
                os.makedirs(mDir)
                log.warning("created dir: {0}".format(mDir))
                self.rebuild()
            else:
                log.warning("Dir already exists: {0}".format(mDir))
                
    def uiPath_removeDir(self, path = None):
        '''
        Insert a new SubFolder to the path, makes the dir and sets
        '''
        mPath = PATHS.Path(path)
        if not mPath.exists():
            raise StandardError('Invalid Path: {0}'.format(path))
        
        promptstring = 'Remove Dir '.format(mPath.asFriendly())
        
        result = mc.confirmDialog(
                title=promptstring,
                message='Are you sure you want to delete... \n Path: {0}'.format(mPath.asFriendly()),
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
        
        if result == 'OK':            
            if mPath.exists():
                import shutil
                shutil.rmtree(mPath)
                #_pathNow = mPath.asString()
                #_pathNew = os.path.join(mPath.up(),'renameING')
                #os.rename(_pathNow, _pathNew)
                #os.unlink(_pathNew)
                log.warning("deleted dir: {0}".format(mPath))
                self.rebuild()
            else:
                log.warning("Dir doesn't exists: {0}".format(mPath))


        
    @cgmGEN.Timer
    def select_popup(self): 
        try:
            _str_func = 'uiScrollList_select'  
            log.debug(cgmGEN.logString_start(_str_func))

            if self.uiPopUpMenu:
                self.uiPopUpMenu.clear()
                self.uiPopUpMenu.delete()
                self.uiPopUpMenu = None
                
            
            dat = self.getSelectedDirDat()
            _mPath = dat['mPath']
            _path = _mPath.asFriendly()

            #pprint.pprint(dat)
            
            self.uiPopUpMenu = mUI.MelPopupMenu(self,button = 3)
            _popUp = self.uiPopUpMenu
            
            mUI.MelMenuItemDiv(_popUp, label=_mPath.asTruncate())

            
            mUI.MelMenuItem(_popUp,
                            ann = "Open Path to: {0}".format(_path),
                            c= cgmGEN.Callback(self.uiPath_openDir,_path),
                            label = 'Open Dir')
            
            mUI.MelMenuItem(_popUp,
                            ann = "Open Maya file in: {0}".format(_path),
                            c= cgmGEN.Callback(self.uiPath_mayaOpen,_path),
                            label = 'Open Maya file')            
            
            mUI.MelMenuItem(_popUp,
                            ann = "Add sub dir to: {0}".format(_path),
                            c= cgmGEN.Callback(self.uiPath_addDir,_path),
                            label = 'Add Sub Dir')
            
            mUI.MelMenuItem(_popUp,
                            ann = "Remove dir: {0}".format(_path),
                            c= cgmGEN.Callback(self.uiPath_removeDir,_path),
                            label = 'Delete Dir')
            
            
            mUI.MelMenuItem(_popUp,
                            ann = "Log dat: {0}".format(_path),
                            c= lambda *a:pprint.pprint(dat),
                            label = 'Log Dat')            
            
            return
            ml_block = self.uiScrollList_blocks.getSelectedObjs()
            if not ml_block:
                log.warning("|{0}| >> Nothing selected".format(_str_func))
                return False
            
            _mBlock = ml_block[0]
            if _mBlock and not _mBlock.mNode:
                log.warning("|{0}| >> Dead block. Rebuilding blockList".format(_str_func))                
                self.uiScrollList_blocks.rebuild()
                return False
                
            self.uiScrollList_blocks.setHLC(_mBlock)
            
            _short = _mBlock.p_nameShort

            _mActiveBlock = self._blockCurrent
            _str_activeBlock = False
            if _mActiveBlock:
                _str_activeBlock = _mActiveBlock.mNode
        
            self.uiPopUpMenu = mUI.MelPopupMenu(self.uiScrollList_blocks,button = 3)
            _popUp = self.uiPopUpMenu 
            
            _b_active = False
            if _mActiveBlock:
                _b_active = True
                
            #>>>Special menu ---------------------------------------------------------------------------------------
            
            mBlockModule = _mBlock.getBlockModule()
            if 'uiBuilderMenu' in mBlockModule.__dict__.keys():
                mBlockModule.uiBuilderMenu(_mBlock,_popUp)
                #_mBlock.atBlockModule('uiBuilderMenu', _popUp)
                mUI.MelMenuItemDiv(_popUp)
                
            
            
            mUI.MelMenuItem(_popUp,
                            ann = 'Set selected active block',
                            c = cgmGEN.Callback(self.uiFunc_block_setActive),
                            label = "To active")
            
            mUI.MelMenuItem(_popUp,
                            ann = 'Select',
                            c = cgmGEN.Callback( self.uiFunc_contextBlockCall, 'select'),
                            label = "Select")
            
            
            #>>>Heirarchy ------------------------------------------------------------------------------------
            _menu_parent = mUI.MelMenuItem(_popUp,subMenu=True,
                                           label = "Parent")

            mUI.MelMenuItem(_menu_parent,
                            en = _b_active,
                            ann = 'Set parent block to active block: {0}'.format(_str_activeBlock),
                            #c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'setParentToActive'}),
                            c= lambda *a:self.uiFunc_blockManange_fromScrollList(**{'mode':'setParentToActive'}),
                            label = "To active")
            mUI.MelMenuItem(_menu_parent,
                            ann = 'Clear parent block',
                            #c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'clearParentBlock'}),
                            c= lambda *a:self.uiFunc_blockManange_fromScrollList(**{'mode':'clearParentBlock'}),
                            
                            label = "Clear")
            
            #>>Mirror ----------------------------------------------------------------------------------------
            _mirror = mUI.MelMenuItem(_popUp, subMenu = True,
                                      label = "Mirror",
                                      en=True,)   
        
            mUI.MelMenuItem(_mirror,
                            label = 'Verify',
                            ann = '[{0}] Create or load mirror block'.format(_short),
                            c = lambda *a: self.uiFunc_block_mirror_create(_mBlock,False) )    
            mUI.MelMenuItem(_mirror,
                            label = 'Rebuild',
                            ann = '[{0}] Rebuild mirror block from scratch'.format(_short),                                                    
                            #c=lambda *a:self.uiCallback_withUpdate( _mBlock.atBlockUtils, mirrorDat[1], **mirrorDat[2]) )                            
                            c = lambda *a: self.uiFunc_block_mirror_create(_mBlock,True) )  
            
            _l_mirror = [#['Create','blockMirror_create', {}],
                         #['Recreate','blockMirror_create', {'forceNew':True}],
                         ['Push','blockMirror_go', {'mode':'push'}],
                         ['Pull','blockMirror_go', {'mode':'pull'}]]
            for mirrorDat in _l_mirror:
                mUI.MelMenuItem(_mirror,
                                label = mirrorDat[0],
                                ann = '[{0}] {1} block controls'.format(_short,mirrorDat[0]),                                                    
                                #c=lambda *a:self.uiCallback_withUpdate( _mBlock.atBlockUtils, mirrorDat[1], **mirrorDat[2]) )                            
                                c=cgmGEN.Callback( _mBlock.atBlockUtils, mirrorDat[1], **mirrorDat[2]) )
    
            
            #>>Utilities ------------------------------------------------------------------------------------------       
            """
            mUI.MelMenuItem(_popUp,
                            label = "Select",
                            en=True,
                            ann = '[{0}] Select the block'.format(_short),                        
                            c=cgmGEN.Callback(_mBlock.select))
            """
            
            
            _sizeMode = mBlockModule.__dict__.get('__sizeMode__',None)
            if _sizeMode:
                mUI.MelMenuItem(_popUp,
                                label ='Size',
                                ann = 'Size by: {0}'.format(_sizeMode),
                                c=cgmGEN.Callback(_mBlock.atUtils, 'size', _sizeMode))
                
                
            mUI.MelMenuItemDiv(_popUp)
            mUI.MelMenuItem(_popUp,
                            label ='Set Name',
                            ann = 'Specify the name for the current block. Current: {0}'.format(_mBlock.cgmName),
                            c = uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'set_nameTag'))
            
            mUI.MelMenuItem(_popUp,
                            label ='Edit NameList',
                            ann = 'Ui Prompt to edit nameList',
                            c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                         'atUtils','nameList_uiPrompt',
                                                                         **{}))
            
            #...side ----------------------------------------------------------------------------------------
            sub_side = mUI.MelMenuItem(_popUp,subMenu=True,
                                       label = 'Set side')
            
            for i,side in enumerate(['None','left','right','center']):
                mUI.MelMenuItem(sub_side,
                                label = side,
                                ann = 'Specify the side for the current block to : {0}'.format(side),
                                c = uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'set_side',side))
            #...position ------------------------------------------------------------------------------
            #none:upper:lower:front:back:top:bottom
            sub_position = mUI.MelMenuItem(_popUp,subMenu=True,
                                           label = 'Set position')
            for i,position in enumerate(['None','upper','lower','front','back','top','bottom']):
                mUI.MelMenuItem(sub_position,
                                label = position,
                                ann = 'Specify the position for the current block to : {0}'.format(position),
                                c = uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'set_position',position))
                
            
            mUI.MelMenuItemDiv(_popUp)
            
            mUI.MelMenuItem(_popUp,
                            label = "Recolor",
                            en=True,
                            ann = '[{0}] Recolor the block'.format(_short),                        
                            c=cgmGEN.Callback(_mBlock.atBlockUtils,'color'))
            
            
            mUI.MelMenuItem(_popUp,
                            label = "Verify",
                            ann = '[{0}] Verify the block'.format(_short),                        
                            en=True,
                            c=uiCallback_withUpdate(self,_mBlock,_mBlock.verify))
            mUI.MelMenuItem(_popUp,
                            label = "Delete",
                            ann = '[{0}] delete the block'.format(_short),                        
                            en=True,
                            c=uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'delete'))
            mUI.MelMenuItem(_popUp,
                            label = "Duplicate",
                            ann = '[{0}] Duplicate the block'.format(_short),                        
                            en=True,
                            c=uiCallback_withUpdate(self,_mBlock,'duplicate'))
            
            mUI.MelMenuItemDiv(_popUp)
            
            
            mUI.MelMenuItem(_popUp,
                            ann = 'Initialize the block as mBlock in the script editor',
                            c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'toScriptEditor'}),
                            label = "To ScriptEditor")
            
            mUI.MelMenuItem(_popUp,
                            ann = 'Initialize the block as mBlock in the script editor as a rigFactory',
                            c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'toScriptEditorRigFactory'}),
                            label = "To ScriptEditor as RigFac")
            """
            mUI.MelMenuItem(_popUp,
                            ann = 'Initialize the block as mBlock in the script editor',
                            c =cgmGEN.Callback(self.uiScrollList_blocks.func_byBlock,
                                               'atUtils','to_scriptEditor',
                                               **{'updateUI':0}),
                            label = "To ScriptEditor")"""
            
            mUI.MelMenuItem(_popUp,
                            ann = self._d_ui_annotations.get('step build'),
                            c =cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                               'stepUI',
                                               **{'updateUI':0,'mode':'stepBuild'}),
                            label = "Step Build")             
            

            return
            
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    
    def setHLC(self,arg=None):
        log.debug(cgmGEN.logString_start('setHLC'))        
        if arg:
            try:
                _color = self._d_itc[arg]
                log.info("{0} | {1}".format(arg,_color))
                _color = [v*.7 for v in _color]
                self(e =1, hlc = _color)
                return
            except Exception,err:
                log.error(err)
                
            try:self(e =1, hlc = [.5,.5,.5])
            except:pass
            
    def getSelectedDirDat( self):
        log.debug(cgmGEN.logString_start('getSelectedDirDat'))                
        _indices = self.getSelectedIdxs(True)
        if not _indices:
            log.debug("Nothing selected")
            return []
        log.info(_indices)
        return self._d_dir[ self._l_str_loaded[ _indices[0]]]
    
        #for i in _indices:
            #print i
        #return [ self._d_dir[ self._l_uiStrings[i]] for i in _indices[:1] ]
            
        #return [self._ml_loaded[i] for i in _indices]
    
    def selCommand(self):
        l_indices = self.getSelectedIdxs(True)
        log.debug(cgmGEN.logString_start('selCommand | {0}'.format(l_indices)))
        
        #self.getSelectedDir()
        if l_indices:
            self.setHLC(self._l_str_loaded[l_indices[0]])
        """
        mBlock = self.getSelectedBlocks()
        if mBlock:
            self.setHLC(mBlock[0])
            pprint.pprint(mBlock)
            self.mDat._ml_listNodes = mBlock"""
        log.debug(cgmGEN.logString_start('cmd_select | {0}'.format(self.cmd_select)))            
        
        if self.b_selCommandOn and self.cmd_select:
            if len(l_indices)<=1:
                return self.cmd_select(*self.selArgs,**self.selkws)
        return False
    
    def rebuild( self, path = None ):
        _str_func = 'rebuild'
        
        if path == None:
            path = self.path
        else:
            self.path = path

        log.debug(cgmGEN.logString_start(_str_func))
        
        self._items = []
        self._ml_scene = []
        self._ml_loaded = []
        self._l_strings = []
        self._l_str_loaded = []
        self._l_itc = []
        self._d_itc  = {}
        self._l_uiKeys = []
        self._d_strToKey = {}
        #...
        
        mPath = PATHS.Path(path)
        if not mPath.exists():
            log.error("Invalid path: {0}".format(path))
            self.update_display()
            
            return False        
 
        
        
        self.b_selCommandOn = False
        #ml_sel = self.getSelectedBlocks()
        
        self( e=True, ra=True )
        
        try:self(e =1, hlc = [.5,.5,.5])
        except:pass                
        
        
        _d_dir, _d_levels, l_keys = COREPATHS.walk_below_dir(path,
                                                             uiStrings = 1,
                                                             #fileTest = {'endsWith':'pose'},
                                                             hardCap = None,
                                                             )        
        
        #self._l_uiStrings = _l_uiStrings
        self._d_dir = _d_dir
        self._l_uiKeys = l_keys
        
        self._l_itc = []
        
        d_colors = {'left':[.4,.4,1],
                    'center': [1,2,1],
                    'right':[.9,.2,.2]}
        
        
        for i,k in enumerate(l_keys):
            _color = [1,.5,0]#d_colors.get(d_colors['center'])
            self._l_itc.append(_color)            
            self._d_itc[k] = _color
            
            _str = _d_dir[k]['uiString']
            self._l_strings.append(_str)
            self._d_strToKey[_str] = k
            
        self.update_display()
        
        """
        if ml_sel:
            try:self.selectByBlock(ml_sel)
            except Exception,err:
                print err"""
        self.b_selCommandOn = True

    def clear( self ):
        log.debug(cgmGEN.logString_start('clear'))                
        self( e=True, ra=True )
        self._l_str_loaded = []
        self._l_uiStr_loaded = []
        self._ml_loaded = []
        
    def clearSelection( self,):
        self( e=True, deselectAll=True )
        
    def set_filterObj(self,obj=None):
        self.filterField = obj

    def update_display(self,searchFilter='',matchCase = False):
        _str_func = 'update_display'
        log.debug(cgmGEN.logString_start(_str_func))
        
        #l_items = self.getSelectedItems()
        
        if self.filterField is not None:
            searchFilter = self.filterField.getValue()
        
        self.clear()
        try:
            for i,str_entry in enumerate(r9Core.filterListByString(self._l_strings,
                                                                  searchFilter,
                                                                  matchcase=matchCase)):
                _key = self._d_strToKey[str_entry]
                
                if str_entry in self._l_uiStr_loaded:
                    raise ValueError,'Dup uiString: {0}'.format(str_entry)
                    #log.warning("Duplicate string: {0}".format(str_entry))
                
                self._l_uiStr_loaded.append(str_entry)
                self.append(str_entry)
                self._l_str_loaded.append(_key)
                
                #idx = self._l_strings.index(key)
                #_mBlock = self._ml_scene[idx]
                #self._ml_loaded.append(_mBlock)
                #_color = d_state_colors.get(_mBlock.getEnumValueString('blockState'))
                _color = self._d_itc[_key]
                try:self(e=1, itc = [(i+1,_color[0],_color[1],_color[2])])
                except:pass

        except Exception,err:
            log.error("|{0}| >> err: {1}".format(_str_func, err))  
            for a in err:
                log.error(a)

    def selectCallBack(self,func=None,*args,**kws):
        pprint.pprint( self.getSelectedDirDat() )

        
#>>> Utilities
#===================================================================
