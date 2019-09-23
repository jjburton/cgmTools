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
import cgm.core.lib.shared_data as SHARED
import cgm.core.lib.string_utils as CORESTRINGS

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
            _friendly = mPath.asFriendly()
            self.mOptionVar.append(_friendly)
            self.l_paths.append(_friendly)
            
        else:
            log.debug(cgmGEN.logString_msg(_str_func,'Invalid Path | {0}'.format(arg)))
            
    def verify(self):
        _str_func = 'pathList.verify'
        log.debug(cgmGEN.logString_start(_str_func))
        self.l_paths = []
        
        for p in self.mOptionVar.value:
            log.debug(p)
            mPath = PATHS.Path(p)
            if not mPath.exists():
                log.debug(cgmGEN.logString_msg(_str_func,"Path doesn't exists: {0}".format(p)))
                self.mOptionVar.remove(p)
            else:
                self.l_paths.append(p)
                
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
        
        

def buildFrame_poses(self,parent):
    try:self.var_mrsPosesFrameCollapse
    except:self.create_guiOptionVar('mrsPosesFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_mrsPosesFrameCollapse
    _frame = mUI.MelFrameLayout(parent,label = 'Poses',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=1,
                                ann="Thanks Red9!",
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    #Vars ==========================================================================
    self.var_pathMode = cgmMeta.cgmOptionVar('cgmVar_mrs_pathMode',defaultValue = 'local')
    self.var_pathLocal = cgmMeta.cgmOptionVar('cgmVar_mrs_localPosePath',defaultValue = '')
    self.var_pathProject = cgmMeta.cgmOptionVar('cgmVar_mrs_projectPosePath',defaultValue = '')
    

    
    self.cgmUIField_subPath= False
    self.cgmUIField_posePath = False
    #Red9 Stuff ====================================================================
    self.cgmUIBoot = True
    self.poseButtonBGC = [0.27, 0.3, 0.3]
    self.buttonBgc = r9Setup.red9ButtonBGC(1)
    self.internalConfigPath = False
    
    self.filterSettings = r9Core.FilterNode_Settings()
    self.filterSettings.transformClamp = True
    self.presetDir = r9Setup.red9Presets()  # os.path.join(r9Setup.red9ModulePath(), 'presets')
    self.basePreset = ''    
    
    # Hierarchy Controls
    # =====================
    self.cgmUIclHierarchyFilters = 'cgmUIMRSclHierarchyFilters'
    self.cgmUIcbMetaRig = 'cgmUIMRScbMetaRig'
    self.cgmUItfgSpecificNodeTypes = 'cgmUIMRStfgSpecificNodeTypes'
    self.cgmUItfgSpecificAttrs = 'cgmUIMRStfgSpecificAttrs'
    self.cgmUItfgSpecificPattern = 'cgmUIMRStfgSpecificPattern'
    self.cgmUItslFilterPriority = 'cgmUIMRStslFilterPriority'
    self.cgmUIcbSnapPriorityOnly = 'cgmUIMRScbSnapPriorityOnly'
    self.cgmUItslPresets = 'cgmUIMRStslPresets'
    self.cgmUIcbIncRoots = 'cgmUIMRScbIncRoots'    
    
    # Pose Saver Tab
    # ===============
    self.cgmUItfgPosePath = 'cgmUIMRStfgPosePath'
    self.cgmUIrcbPosePathMethod = 'posePathMode'
    self.posePopupGrid = 'posePopupGrid'
    #self.matchMethod = mc.optionMenu('om_MatchMethod', q=True, v=True)

    # SubFolder Scroller
    #=====================
    self.cgmUItslPoseSubFolders = 'cgmUIMRStslPoseSubFolders'


    #from functools import cgmGEN.Callback

    # Main PoseFields
    # =====================
    self.tfPoseSearchFilter = 'tfPoseSearchFilter'
    self.cgmUItslPoses = 'cgmUIMRStslPoses'
    self.cgmUIglPoseScroll = 'cgmUIMRSglPoseScroll'
    self.cgmUIglPoses = 'cgmUIMRSglPoses'
    self.cgmUIcbPoseHierarchy = 'cgmUIMRScbPoseHierarchy'
    self.cgmUItfgPoseRootNode = 'cgmUIMRStfgPoseRootNode'
    self.cgmUIcbPoseRelative = 'cgmUIMRScbPoseRelative'
    self.cgmUIcbPoseSpace = 'cgmUIMRScbPoseSpace'
    self.cgmUIflPoseRelativeFrame = 'PoseRelativeFrame'
    self.cgmUIrcbPoseRotMethod = 'relativeRotate'
    self.cgmUIrcbPoseTranMethod = 'relativeTranslate'    
    
    # Pose Management variables
    self.posePath = None  # working variable
    self.posePathLocal = 'Local Pose Path not yet set'
    self.posePathProject = 'Project Pose Path not yet set'
    self.posePathMode = 'localPoseMode'  # or 'project' : mode of the PosePath field and UI
    self.poseSelected = None
    self.poseGridMode = 'thumb'  # or text
    self.poseRootMode = 'RootNode'  # or MetaRig
    self.poses = None
    self.poseButtonBGC = [0.27, 0.3, 0.3]
    self.poseButtonHighLight = r9Setup.red9ButtonBGC('green')
    self.poseProjectMute = False  # whether to disable the save and update funcs in Project mode
    self.ANIM_UI_OPTVARS = dict()
    self.ANIM_UI_OPTVARS['AnimationUI'] = {}

    # Default Red9 poseHandlers now bound here if found, used to extend Clients handling of data
    self.poseHandlerPaths = [os.path.join(self.presetDir, 'posehandlers')]

    # bind the ui element names to the class
    self._uiElementBinding()

    # Internal config file setup for the UI state
    if self.internalConfigPath:
        self.cgmUI_optVarConfig = os.path.join(self.presetDir, '__red9config__')
    else:
        self.cgmUI_optVarConfig = os.path.join(r9Setup.mayaPrefs(), '__red9config__')
    self._uiCache_readUIElements()
    
    
    try:
        v_local = self.var_pathLocal.getValue()
        if v_local:
            log.info('setting local on call...')
            self.posePathLocal = v_local
            
        v_project = self.var_pathProject.getValue()
        if v_project:
            log.info('setting project on call...')        
            self.posePathProject = v_project
    except:
        pass    
    
    
    
    #Pose Path ===============================================================================
    uiRow_pose = mUI.MelHSingleStretchLayout(_inside)
    mUI.MelSpacer(uiRow_pose,w=2)    
    self.cgmUIField_posePath = mUI.MelTextField(uiRow_pose,
                                             ann='Testing',
                                             cc = lambda *x:self._uiCB_setPosePath(field=False),
                                             text = '')

    uiRow_pose.setStretchWidget(self.cgmUIField_posePath)
    
    mc.button(parent=uiRow_pose,
              l = 'Set Path',
              ut = 'cgmUITemplate',
              c= lambda *x:self._uiCB_setPosePath(fileDialog=True),
              #en = _d.get('en',True),
              #c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
              #ann = _d.get('ann',b))
              )
    mc.button(parent=uiRow_pose,
              l = 'Test',
              ut = 'cgmUITemplate',
              c= lambda *x:log.info("Mode: {0} | local: {1} | project: {2}".format(self.var_pathMode.getValue(),self.posePathLocal, self.posePathProject)),
              )
    mUI.MelSpacer(uiRow_pose,w=2)
    uiRow_pose.layout()
    mc.setParent(_inside)
    
    #Pose Mode ===============================================================================
    uiRow_poseMode = mUI.MelHSingleStretchLayout(_inside, ut='cgmUISubTemplate', padding = 10)
    
        
    mUI.MelSpacer(uiRow_poseMode,w=5)                      
    mUI.MelLabel(uiRow_poseMode,l='Mode: ')
    uiRow_poseMode.setStretchWidget( mUI.MelSeparator(uiRow_poseMode) )

    uiRC = mUI.MelRadioCollection()
    
    mVar = self.var_pathMode
    _on = mVar.value

    for i,item in enumerate(['local','project']):
        if item == _on:
            _rb = True
        else:_rb = False
        
        if item == 'local':
            _reverse = 'project'
        else:
            _reverse = 'local'
        
        uiRC.createButton(uiRow_poseMode,
                          label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(self._uiCB_switchPosePathMode, item),
                          offCommand = cgmGEN.Callback(self._uiCB_switchPosePathMode, _reverse))

        #mUI.MelSpacer(_row,w=1)       
    mUI.MelSpacer(uiRow_poseMode,w=5)                          
    uiRow_poseMode.layout()     
    
    
    #Sub path ===============================================================================
    uiRow_sub = mUI.MelHSingleStretchLayout(_inside)
    mUI.MelSpacer(uiRow_sub,w=2)    
    self.cgmUIField_subPath = mUI.MelLabel(uiRow_sub,
                                        ann='Testing',
                                        ut = 'cgmUIInstructionsTemplate',
                                        #en=False,
                                        #cc = lambda *x:self._uiCB_setPosePath(field=False),
                                        label = '')

    uiRow_sub.setStretchWidget(self.cgmUIField_subPath)
    
    mc.button(parent=uiRow_sub,
              l = 'Sub',
              ut = 'cgmUITemplate',
              c= lambda *x:self._uiCB_switchSubFolders(),
              #en = _d.get('en',True),
              #c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
              #ann = _d.get('ann',b))
              )
    mc.button(parent=uiRow_sub,
              l = 'Clear',
              ut = 'cgmUITemplate',
              c= lambda *x:self._uiCB_clearSubFolders(),
              )
    mUI.MelSpacer(uiRow_sub,w=2)
    uiRow_sub.layout()
    
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    
    
    #Search row ===============================================================================
    uiRow_search = mUI.MelHSingleStretchLayout(_inside,h=30)
    mUI.MelSpacer(uiRow_search,w=2)
    mUI.MelLabel(uiRow_search,l='Filter:')
    
    self.cgmUIField_searchPath = mUI.MelTextField(uiRow_search,
                                            ann='Testing',
                                            w=50,
                                            en=True,
                                            text = '')
    self.cgmUIField_searchPath(edit=True,
                            tcc = lambda x: self._uiCB_fillPoses(searchFilter=self.cgmUIField_searchPath.getValue(),))
                            
    uiRow_search.setStretchWidget(self.cgmUIField_searchPath)
    
    mUI.MelIconButton(uiRow_search,
                      image='sortByName.bmp',
                      w=22,
                      c=lambda * args: self._uiCB_fillPoses(rebuildFileList=True, sortBy='name'))
    mUI.MelIconButton(uiRow_search,
                      image='sortByDate.bmp',
                      w=22,
                      c=lambda * args: self._uiCB_fillPoses(rebuildFileList=True, sortBy='date'))
    
    mUI.MelSpacer(uiRow_search,w=2)
    uiRow_search.layout()
    
    
    #Pose Tumb area ===============================================================================
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    mc.button(parent=_row,
              l = 'Load',
              ut = 'cgmUITemplate',
              command=cgmGEN.Callback(self._uiCall, 'PoseLoad'))
    mc.button(parent=_row,
              l = 'Save',
              ut = 'cgmUITemplate',
              command=cgmGEN.Callback(self._uiCall, 'PoseSave'))
    mc.button(parent=_row,
              l = 'Blend',
              ut = 'cgmUITemplate',
              command=lambda *x:self._PoseBlend())    
    _row.layout()
    


    
    #Pose Tumb area ===============================================================================
    # SubFolder Scroller ---------------------------------------------------
    mc.setParent(_inside)
    mc.textScrollList(self.cgmUItslPoseSubFolders, numberOfRows=8,
                      allowMultiSelection=False,
                      height=350, vis=False)

    # Main PoseFields ------------------------------------------------------------
    mc.textScrollList(self.cgmUItslPoses, numberOfRows=8, allowMultiSelection=False,
                      # selectCommand=cgmGEN.Callback(self._uiPresetSelection), \
                      height=350, vis=False)
    
    self.posePopupText = mc.popupMenu()
    mc.scrollLayout(self.cgmUIglPoseScroll,
                    cr=True,
                    height=350,
                    hst=16,
                    vst=16,
                    vis=False,
                    rc=self._uiCB_gridResize)
    
    mc.gridLayout(self.cgmUIglPoses, cwh=(100, 100), cr=False, ag=True)
    self.posePopupGrid = mc.popupMenu('posePopupGrid')
    
    
    self._uiCB_setPosePath()
    self._uiCB_switchPosePathMode('local')
    return

    # SubFolder Scroller
    mc.textScrollList(self.cgmUItslPoseSubFolders, numberOfRows=8,
                        allowMultiSelection=False,
                        height=350, vis=False)

    # Main PoseFields
    mc.textScrollList(self.cgmUItslPoses, numberOfRows=8, allowMultiSelection=False,
                        # selectCommand=cgmGEN.Callback(self._uiPresetSelection), \
                        height=350, vis=False)
    self.posePopupText = mc.popupMenu()

    mc.scrollLayout(self.cgmUIglPoseScroll,
                      cr=True,
                      height=350,
                      hst=16,
                      vst=16,
                      vis=False,
                      rc=self._uiCB_gridResize)
    mc.gridLayout(self.cgmUIglPoses, cwh=(100, 100), cr=False, ag=True)
    self.posePopupGrid = mc.popupMenu('posePopupGrid')

    mc.setParent(_inside)
    mc.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 162), (2, 162)])
    mc.button('loadPoseButton', label=LANGUAGE_MAP._AnimationUI_.pose_load, bgc=self.buttonBgc,
                ann=LANGUAGE_MAP._AnimationUI_.pose_load_ann,
                command=cgmGEN.Callback(self._uiCall, 'PoseLoad'))
    mc.button('savePoseButton', label=LANGUAGE_MAP._AnimationUI_.pose_save, bgc=self.buttonBgc,
                ann=LANGUAGE_MAP._AnimationUI_.pose_save_ann,
                command=cgmGEN.Callback(self._uiCall, 'PoseSave'))    
    
    return
    #>>>Reset ===================================================================================== 
    cgmUI.add_LineSubBreak()
    
    _uiRow_reset = mUI.MelHSingleStretchLayout(_inside, height = 27)

    mUI.MelSpacer(_uiRow_reset, w = 2)
    mUI.MelLabel(_uiRow_reset,l='Reset')
    """
    self.cgmUIFF_relax = mUI.MelFloatField(_uiRow_relax, w = 50, value = .2,
                                        #cc = lambda *a: self.cgmUISlider_relax.setValue(self.cgmUIFF_relax.getValue()),
                                        )"""

    self.cgmUISlider_reset = mUI.MelFloatSlider(_uiRow_reset, 0, 1.0, defaultValue=0, 
                                             #bgc = cgmUI.guiBackgroundColor,
                                             value = 0,
                                             cc = lambda *a: uiCB_resetSlider(self))
                                             #cc = lambda *a: self.cgmUIFF_relax.setValue(self.cgmUISlider_relax.getValue()),
                                             #dragCommand = lambda *a: log.info(self.cgmUISlider_relax.getValue()),
                                             
    self.cgmUISlider_reset.setPostChangeCB(cgmGEN.Callback(uiCB_resetSliderDrop,self))
    
    mUI.MelSpacer(_uiRow_reset, w = 1)
    """
    mc.button(parent=_uiRow_relax ,
              ut = 'cgmUITemplate',
              l = 'R',
              c = lambda *a: self.cgmUISlider_relax.reset(),
              ann = "Reset relaxer")
    """
    mUI.MelSpacer(_uiRow_reset, w = 2)
    _uiRow_reset.setStretchWidget(self.cgmUISlider_reset)
    _uiRow_reset.layout() 
    
    

#>>> Root settings =============================================================
__version__ = '1.09222019'

__l_spaceModes = SHARED._d_spaceArgs.keys()
__l_pivots = SHARED._d_pivotArgs.keys()

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'mrsPoseMananger'    
    WINDOW_TITLE = 'mrsPoseManager - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 425,350
    TOOLNAME = 'mrsPoseMananger.ui'
    
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

        #self.uiPopUpMenu_createShape = None
        #self.uiPopUpMenu_color = None
        #self.uiPopUpMenu_attr = None
        #self.uiPopUpMenu_raycastCreate = None

        #self.create_guiOptionVar('matchFrameCollapse',defaultValue = 0) 
        #self.create_guiOptionVar('rayCastFrameCollapse',defaultValue = 0) 
        #self.create_guiOptionVar('aimFrameCollapse',defaultValue = 0) 

    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))
        #self.uiMenu_Buffers = mUI.MelMenu( l='Buffers', pmc = cgmGEN.Callback(self.buildMenu_buffer))

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     

        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
    
        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        _column = buildColumn_main(self,_MainForm,True)
    
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)            
        _MainForm(edit = True,
                  af = [(_column,"top",0),
                        (_column,"left",0),
                        (_column,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(_column,"bottom",2,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])          
        
        
def uiPopup_setPath(self):
    if self.uiPop_path:
        self.uiPop_path.clear()
        self.uiPop_path.delete()
        self.uiPop_path = None

    self.uiPop_path = mUI.MelPopupMenu(self.cgmUIField_posePath,button = 1)
    _popUp = self.uiPop_path 

    mUI.MelMenuItem(_popUp,
                    label = "Set Path",
                    en=False)     
    mUI.MelMenuItemDiv(_popUp)
    
    _recent = mUI.MelMenuItem(_popUp,subMenu = True,
                              label = 'recent',
                              en=True)
    
    self.mPathList.verify()
    for p in self.mPathList.l_paths:
        mUI.MelMenuItem(_recent,
                        label = CORESTRINGS.short(p,10),
                        ann = "Set the pathto: {0}".format(p),
                        c=cgmGEN.Callback(uiCB_setPosePath,self,p))
    
    """
    for k,l in CURVES._d_shapeLibrary.iteritems():
        _k = mUI.MelMenuItem(_popUp,subMenu = True,
                             label = k,
                             en=True)
        for o in l:
            mUI.MelMenuItem(_k,
                            label = o,
                            ann = "Set the create shape to: {0}".format(o),
                            c=cgmGen.Callback(cb_setCreateShape,self,o))
            """
    
def uiCB_setPosePath(self, path=None, field = False, fileDialog=False):
    '''
    Manage the PosePath textfield and build the PosePath
    '''
    _str_func = '_uiCB_setPosePath'
    
    if self.var_pathMode.getValue() == 'local':
        mVar = self.var_pathLocal
    else:
        mVar = self.var_pathProject
    
    if not path and not field and not fileDialog:
        self.posePath = mVar.getValue()
    
    if path:
        self.posePath = path
    elif fileDialog:
        log.debug("|{0}| >> file dialog mode...".format(_str_func))
        try:
            if r9Setup.mayaVersion() >= 2011:
                _dir = self.cgmUIField_posePath.getValue() or ''
                log.debug("|{0}| >> dir: {1}".format(_str_func,_dir))                    
                self.posePath = mc.fileDialog2(fileMode=3,
                                               dir=_dir)[0]
            else:
                print 'Sorry Maya2009 and Maya2010 support is being dropped'
                def setPosePath(fileName, fileType):
                    self.posePath = fileName
                mc.fileBrowserDialog(m=4, fc=setPosePath, ft='image', an='setPoseFolder', om='Import')
        except Exception,err:
            log.warning('No Folder Selected or Given | {0}'.format(err))
    elif field:
        self.posePath = self.cgmUIField_posePath.getValue()
    
    if not PATHS.Path(self.posePath):
        log.error("|{0}| >> Invalid path: {1}".format(_str_func,self.posePath))            
        self.posePath = ''
        return 
    
    mVar.setValue(self.posePath)
    self.cgmUIField_posePath.setValue(self.posePath,executeChangeCB=False)
    self.cgmUIField_posePath(edit=True, ann = self.posePath)
    
    self.mPathList.append(self.posePath)
    #mc.textFieldButtonGrp(self.cgmUItfgPosePath, edit=True, text=self.posePath)
    
    if self.var_pathMode.getValue == 'local':
        self.posePathLocal = self.posePath
    else:
        self.posePathProject = self.posePath
        
    self.uiScrollList_dir.rebuild(self.posePath)
    
    #pprint.pprint(vars())
    #self.cgmUIField_subPath.setValue('')
    #self._uiCB_pathSwitchInternals()
    
    return

def uiCB_switchPosePathMode(self, mode, *args):
    '''
    Switch the Pose mode from Project to Local. In project mode save is disabled.
    Both have different caches to store the 2 mapped root paths

    :param mode: 'local' or 'project', in project the poses are load only, save=disabled
    '''
    if mode == 'local' or mode == 'localPoseMode':
        self.posePath = os.path.join(self.posePathLocal, self.getPoseSubFolder())
        if not PATHS.Path(self.posePath):#os.path.exists(self.posePath):
            log.warning('No Matching Local SubFolder path found - Reverting to Root')
            self._uiCB_clearSubFolders()
            self.posePath = self.posePathLocal

        self.posePathMode = 'localPoseMode'
        if self.poseProjectMute:
            mc.button('savePoseButton', edit=True, en=True, bgc=r9Setup.red9ButtonBGC(1))
            
        #mc.textFieldButtonGrp(self.cgmUItfgPosePath, edit=True, text=self.posePathLocal)
        self.var_pathMode.setValue('local')            
        self.cgmUIField_posePath.setValue(self.posePath)
        
    elif mode == 'project' or mode == 'projectPoseMode':
        self.posePath = os.path.join(self.posePathProject, self.getPoseSubFolder())
        if not PATHS.Path(self.posePath):#os.path.exists(self.posePath):
            log.warning('No Matching Project SubFolder path found - Reverting to Root')
            self._uiCB_clearSubFolders()
            self.posePath = self.posePathProject

        self.posePathMode = 'projectPoseMode'
        if self.poseProjectMute:
            mc.button('savePoseButton', edit=True, en=False, bgc=r9Setup.red9ButtonBGC(2))
        #mc.textFieldButtonGrp(self.cgmUItfgPosePath, edit=True, text=self.posePathProject)
        self.var_pathMode.setValue('project')            
        self.cgmUIField_posePath.setValue(self.posePath)
        
        
    mc.scrollLayout(self.cgmUIglPoseScroll, edit=True, sp='up')  # scroll the layout to the top!

    self.ANIM_UI_OPTVARS['AnimationUI']['posePathMode'] = self.posePathMode
    #self._uiCB_fillPoses(rebuildFileList=True)
    
def buildColumn_main(self,parent,asScroll=False):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """
    self.uiPop_path = None
    self.mPathList = mrsPaths = pathList('cgmPosePaths')
    self.posePath = None
    self.posePathLocal = None
    self.posePathProject = None
    self.posePathSub = None
    
    #Vars ==========================================================================
    self.var_pathMode = cgmMeta.cgmOptionVar('cgmVar_mrs_pathMode',defaultValue = 'local')
    self.var_pathLocal = cgmMeta.cgmOptionVar('cgmVar_mrs_localPosePath',defaultValue = '')
    self.var_pathProject = cgmMeta.cgmOptionVar('cgmVar_mrs_projectPosePath',defaultValue = '')
    
    
    
    # Pose Management variables
    self.posePathMode = 'localPoseMode'  # or 'project' : mode of the PosePath field and UI
    self.poseSelected = None
    self.poseGridMode = 'thumb'  # or text
    self.poseRootMode = 'RootNode'  # or MetaRig
    self.poses = None
    self.poseButtonBGC = [0.27, 0.3, 0.3]
    self.poseButtonHighLight = r9Setup.red9ButtonBGC('green')
    self.poseProjectMute = False  # whether to disable the save and update funcs in Project mode
    self.ANIM_UI_OPTVARS = dict()
    self.ANIM_UI_OPTVARS['AnimationUI'] = {}

    # Default Red9 poseHandlers now bound here if found, used to extend Clients handling of data
    #self.poseHandlerPaths = [os.path.join(self.presetDir, 'posehandlers')]

    # bind the ui element names to the class
    #self._uiElementBinding()

    # Internal config file setup for the UI state
    #if self.internalConfigPath:
    #    self.cgmUI_optVarConfig = os.path.join(self.presetDir, '__red9config__')
    #else:
    #    self.cgmUI_optVarConfig = os.path.join(r9Setup.mayaPrefs(), '__red9config__')
    
    #self._uiCache_readUIElements()
    
    
    try:
        v_local = self.var_pathLocal.getValue()
        if v_local:
            log.info('setting local on call...')
            self.posePathLocal = v_local
            
        v_project = self.var_pathProject.getValue()
        if v_project:
            log.info('setting project on call...')        
            self.posePathProject = v_project
    except:
        pass        
    
    
    
    
    
    
    
    
    
    self.cgmUIField_subPath= False
    self.cgmUIField_posePath = False
    #Red9 Stuff ====================================================================
    self.cgmUIBoot = True
    self.poseButtonBGC = [0.27, 0.3, 0.3]
    self.buttonBgc = r9Setup.red9ButtonBGC(1)
    self.internalConfigPath = False
    
    self.filterSettings = r9Core.FilterNode_Settings()
    self.filterSettings.transformClamp = True
    self.presetDir = r9Setup.red9Presets()  # os.path.join(r9Setup.red9ModulePath(), 'presets')
    self.basePreset = ''    
    
    # Hierarchy Controls
    # =====================
    #self.cgmUIclHierarchyFilters = 'cgmUIMRSclHierarchyFilters'
    #self.cgmUIcbMetaRig = 'cgmUIMRScbMetaRig'
    #self.cgmUItfgSpecificNodeTypes = 'cgmUIMRStfgSpecificNodeTypes'
    #self.cgmUItfgSpecificAttrs = 'cgmUIMRStfgSpecificAttrs'
    #self.cgmUItfgSpecificPattern = 'cgmUIMRStfgSpecificPattern'
    #self.cgmUItslFilterPriority = 'cgmUIMRStslFilterPriority'
    #self.cgmUIcbSnapPriorityOnly = 'cgmUIMRScbSnapPriorityOnly'
    #self.cgmUItslPresets = 'cgmUIMRStslPresets'
    #self.cgmUIcbIncRoots = 'cgmUIMRScbIncRoots'    
    
    # Pose Saver Tab
    # ===============
    #self.cgmUItfgPosePath = 'cgmUIMRStfgPosePath'
    #self.cgmUIrcbPosePathMethod = 'posePathMode'
    #self.posePopupGrid = 'posePopupGrid'
    #self.matchMethod = mc.optionMenu('om_MatchMethod', q=True, v=True)

    # SubFolder Scroller
    #=====================
    #self.cgmUItslPoseSubFolders = 'cgmUIMRStslPoseSubFolders'

    
    if asScroll:
        _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
    else:
        _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUITemplate') 
        

    #Pose Path ===============================================================================
    uiRow_pose = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate')
    mUI.MelSpacer(uiRow_pose,w=2)    
    """
    self.uiField_path = mUI.MelLabel(uiRow_pose,
                                     ann='Change the current path',
                                     label = 'None',
                                     ut='cgmUIInstructionsTemplate',w=100) """   
    
    
    self.cgmUIField_posePath = mUI.MelTextField(uiRow_pose,
                                             ann='Testing',
                                             cc = lambda *x:self._uiCB_setPosePath(field=False),
                                             text = '')
                                             
    uiRow_pose.setStretchWidget(self.cgmUIField_posePath)
    
    mc.button(parent=uiRow_pose,
              l = 'Set Path',
              ut = 'cgmUITemplate',
              c= lambda *x:uiCB_setPosePath(self,fileDialog=True),
              #en = _d.get('en',True),
              #c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
              #ann = _d.get('ann',b))
              )
    mc.button(parent=uiRow_pose,
              l = 'Test',
              ut = 'cgmUITemplate',
              c= lambda *x:log.info("Mode: {0} | local: {1} | project: {2}".format(self.var_pathMode.getValue(),self.posePathLocal, self.posePathProject)),
              )
    mUI.MelSpacer(uiRow_pose,w=2)
    uiRow_pose.layout()
    mc.setParent(_inside)
    
    uiPopup_setPath(self)
    
        
    #Pose Mode ===============================================================================
    uiRow_poseMode = mUI.MelHSingleStretchLayout(_inside, ut='cgmUISubTemplate', padding = 10)
    
        
    mUI.MelSpacer(uiRow_poseMode,w=5)                      
    mUI.MelLabel(uiRow_poseMode,l='Mode: ')
    uiRow_poseMode.setStretchWidget( mUI.MelSeparator(uiRow_poseMode) )

    uiRC = mUI.MelRadioCollection()
    
    mVar = self.var_pathMode
    _on = mVar.value

    for i,item in enumerate(['local','project']):
        if item == _on:
            _rb = True
        else:_rb = False
        
        if item == 'local':
            _reverse = 'project'
        else:
            _reverse = 'local'
        
        uiRC.createButton(uiRow_poseMode,
                          label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(uiCB_switchPosePathMode, self,  item),
                          offCommand = cgmGEN.Callback(uiCB_switchPosePathMode, self, _reverse))

        #mUI.MelSpacer(_row,w=1)       
    mUI.MelSpacer(uiRow_poseMode,w=5)                          
    uiRow_poseMode.layout()
    
    #directory browser =====================================================================
    buildFrame_mrsPoseDir(self,_inside)
    
    #Search row ===============================================================================
    uiRow_search = mUI.MelHSingleStretchLayout(_inside,h=30,ut='cgmUISubTemplate')
    mUI.MelSpacer(uiRow_search,w=2)
    mUI.MelLabel(uiRow_search,l='Filter:')
    
    self.cgmUIField_searchPath = mUI.MelTextField(uiRow_search,
                                            ann='Testing',
                                            w=50,
                                            en=True,
                                            text = '')
    self.cgmUIField_searchPath(edit=True,
                            tcc = lambda x: self._uiCB_fillPoses(searchFilter=self.cgmUIField_searchPath.getValue(),))
                            
    uiRow_search.setStretchWidget(self.cgmUIField_searchPath)
    
    mUI.MelIconButton(uiRow_search,
                      image='sortByName.bmp',
                      w=22,
                      c=lambda * args: self._uiCB_fillPoses(rebuildFileList=True, sortBy='name'))
    mUI.MelIconButton(uiRow_search,
                      image='sortByDate.bmp',
                      w=22,
                      c=lambda * args: self._uiCB_fillPoses(rebuildFileList=True, sortBy='date'))
    
    mUI.MelSpacer(uiRow_search,w=2)
    uiRow_search.layout()
    
    
    #Pose Button area ===============================================================================
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    
    mc.button(parent=_row,
              l = 'Load',
              ut = 'cgmUITemplate')
              #command=cgmGEN.Callback(self._uiCall, 'PoseLoad'))
    mc.button(parent=_row,
              l = 'Save',
              ut = 'cgmUITemplate')
              #command=cgmGEN.Callback(self._uiCall, 'PoseSave'))
    mc.button(parent=_row,
              l = 'Blend',
              ut = 'cgmUITemplate')
              #command=lambda *x:self._PoseBlend())    
    _row.layout()
    
    
    #uiCB_setPosePath(self)
    #return _inside    

    #Pose Tumb area ===============================================================================
    # SubFolder Scroller ---------------------------------------------------
    #mc.setParent(_inside)

    # Main PoseFields ------------------------------------------------------------
    self.uiTS_poses = mUI.MelTextScrollList(_inside,
                          numberOfRows=8,
                          allowMultiSelection=False,
                          height=350, vis=False                          
                          ) 
    
    self.posePopupText = mc.popupMenu('posePopupText')
    
    #grid...
    self.uiSL_poses = mUI.MelScrollLayout(_inside,
                                          cr=True,
                                          height=350,
                                          hst=16,
                                          vst=16,
                                          vis=True,
                                          )
    
    self.uiGL_poses = mUI.MelGridLayout(self.uiSL_poses,
                                        cwh=(100, 100), cr=False, ag=True,
                                        vis=True,
                                        )
    
    #mc.gridLayout(self.cgmUIglPoses, cwh=(100, 100), cr=False, ag=True)
    self.posePopupGrid = mc.popupMenu('posePopupGrid')

    #Declare some functions after we've created stuff ---------------------------------
    self.uiSL_poses(edit=True,
                    rc = lambda *x:uiCB_gridResize(self),
                    )
    
    #self._uiCB_switchPosePathMode('local')
    uiCB_setPosePath(self)
    uiCB_fillPoses(self,True)
    
    return _inside


def uiCB_buildPoseList(self, sortBy='name'):
    '''
    Get a list of poses from the PoseRootDir, this allows us to
    filter much faster as it stops all the os calls, cached list instead
    '''
    self.poses = []
    if not PATHS.Path(self.posePath):#os.path.exists(self.posePath):
        log.debug('posePath is invalid')
        return self.poses
    files = os.listdir(self.posePath) if os.path.exists(self.posePath) else []
    if sortBy == 'name':
        files = r9Core.sortNumerically(files)
        # files.sort()
    elif sortBy == 'date':
        files.sort(key=lambda x: os.stat(os.path.join(self.posePath, x)).st_mtime)
        files.reverse()

    for f in files:
        if f.lower().endswith('.pose'):
            self.poses.append(f.split('.pose')[0])
    return self.poses


def uiCB_fillPoses(self, rebuildFileList=False, searchFilter=None, sortBy='name', *args):
    '''
    Fill the Pose List/Grid from the given directory
    '''
    # Store the current mode to the Cache File
    self.ANIM_UI_OPTVARS['AnimationUI']['poseMode'] = self.poseGridMode
    #self._uiCache_storeUIElements()
    searchFilter = self.cgmUIField_searchPath.getValue()#mc.textFieldGrp(self.tfPoseSearchFilter, q=True, text=True)
    
    log.debug('searchFilter  : %s : rebuildFileList : %s' % (searchFilter, rebuildFileList))
    

    if rebuildFileList:
        uiCB_buildPoseList(self, sortBy=sortBy)
        log.debug('Rebuilt Pose internal Lists')
        # Project mode and folder contains NO poses so switch to subFolders
        if not self.poses and self.posePathMode == 'projectPoseMode':
            log.warning('No Poses found in Root Project directory, switching to subFolder pickers')
            try:self._uiCB_switchSubFolders()
            except:pass
            return
        
    
    # TextScroll Layout
    # ================================
    if not self.poseGridMode == 'thumb':
        
        mc.textScrollList(self.cgmUItslPoseSubFolders, edit=True, vis=False)  # subfolder scroll OFF
        mc.textScrollList(self.cgmUItslPoses, edit=True, vis=True)  # pose TexScroll ON
        mc.scrollLayout(self.cgmUIglPoseScroll, edit=True, vis=False)  # pose Grid OFF
        mc.textScrollList(self.cgmUItslPoses, edit=True, ra=True)  # clear textScroller

        if searchFilter:
            mc.scrollLayout(self.cgmUIglPoseScroll, edit=True, sp='up')

        for pose in r9Core.filterListByString(self.poses, searchFilter, matchcase=False):  # self.buildFilteredPoseList(searchFilter):
            mc.textScrollList(self.cgmUItslPoses, edit=True,
                                    append=pose,
                                    sc=cgmGEN.Callback(self.setPoseSelected))
    # Grid Layout
    # ================================
    else:
        self.uiTS_poses(e=True, vis=False)
        self.uiSL_poses(e =True, vis=True)
        self.uiGL_poses(e=True, vis=True)
        
        uiCB_gridResize(self)
        
        #mc.textScrollList(self.cgmUItslPoseSubFolders, edit=True, vis=False)  # subfolder scroll OFF
        #mc.textScrollList(self.cgmUItslPoses, edit=True, vis=False)  # pose TexScroll OFF
        #mc.scrollLayout(self.cgmUIglPoseScroll, edit=True, vis=True)  # pose Grid ON
        #self._uiCB_gridResize()

        # Clear the Grid if it's already filled
        try:
            [mc.deleteUI(button) for button in self.uiGL_poses( q=True, ca=True)]
        except StandardError, error:
            print error
            
        for pose in r9Core.filterListByString(self.poses, searchFilter, matchcase=False):  # self.buildFilteredPoseList(searchFilter):
            print pose
            print PATHS.Path(os.path.join(self.posePath, '%s.bmp' % pose)).exists()
            try:
                # :NOTE we prefix the buttons to get over the issue of non-numeric
                # first characters which are stripped my Maya!
                _b = mc.iconTextCheckBox('_%s' % pose,
                                    style='iconAndTextVertical',
                                    image=os.path.join(self.posePath, '%s.bmp' % pose),
                                    label=pose,
                                    bgc=self.poseButtonBGC,
                                    parent = self.uiGL_poses,
                                    ann=pose)
                                    #onc=cgmGEN.Callback(self._uiCB_iconGridSelection, pose),
                                    #ofc="import maya.cmds as cmds;mc.iconTextCheckBox('_%s', e=True, v=True)" % pose)  # we DONT allow you to deselect
                print _b
            except StandardError, error:
                raise StandardError(error)

        if searchFilter:
            # with search scroll the list to the top as results may seem blank otherwise
            self.uiSL_poses(edit=True, sp='up')
            #mc.scrollLayout(self.cgmUIglPoseScroll, edit=True, sp='up')

    # Finally Bind the Popup-menu
    #mc.evalDeferred(self._uiCB_PosePopup)


def uiCB_gridResize(self, *args):
    if r9Setup.mayaVersion() >= 2010:
        cells = (int(self.uiSL_poses(q=True, w=True) / self.uiGL_poses(q=True, cw=True))) or 1
        
        self.uiGL_poses(e=True, nc=cells)
        #mc.gridLayout(self.cgmUIglPoses, e=True, nc=cells)
    else:
        log.debug('this call FAILS in 2009???')
        
        
class mrsPoseDirList(mUI.BaseMelWidget):
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
        
        self._l_uiStrings = []
        self._l_paths = []
        self.path = kw.get('path',None)
        
        self.rebuild()
        self.cmd_select = None
        self(e=True, sc = self.selCommand)
        
        
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
        
    def getSelectedIdxs( self ):
        return [ idx-1 for idx in self( q=True, sii=True ) or [] ]
        
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
        
        
    
    def setHLC(self,mBlock=None):
        log.debug(cgmGEN.logString_start('setHLC'))        
        if mBlock:
            try:
                _color = self._d_itc[mBlock]
                log.info("{0} | {1}".format(mBlock,_color))
                _color = [v*.7 for v in _color]
                self(e =1, hlc = _color)
                return
            except Exception,err:
                log.error(err)
                
            try:self(e =1, hlc = [.5,.5,.5])
            except:pass
            
    def getSelectedDir( self):
        log.debug(cgmGEN.logString_start('getSelectedDir'))                
        _indicesRaw = self.getSelectedIdxs()
        if not _indicesRaw:
            log.debug("Nothing selected")
            return []
        _indices = []
        for i in _indicesRaw:
            _indices.append(int(str(i).split('L')[0]))
            
        #for i in _indices:
        return [ self._d_uiStrings[ self._l_uiStrings[i]] for i in _indices ]
            
        #return [self._ml_loaded[i] for i in _indices]
    
    def selCommand(self):
        l_indices = self.getSelectedIdxs()
        log.debug(cgmGEN.logString_start('selCommand | {0}'.format(l_indices)))
        
        #self.getSelectedDir()
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
        self.b_selCommandOn = False
        #ml_sel = self.getSelectedBlocks()
        
        self( e=True, ra=True )
        
        try:self(e =1, hlc = [.5,.5,.5])
        except:pass        
        
        self._items = []
        self._ml_scene = []
        self._ml_loaded = []
        self._l_strings = []
        self._l_str_loaded = []
        self._l_itc = []
        self._d_itc  = {}
        #...
        
        if not path:
            return False
        
        _d_dir, _d_levels, _l_uiStrings, _d_uiStrings = walk_below_dir(path,
                                                                       uiStrings = 1,
                                                                       fileTest = {'endsWith':'pose'})        
        
        self._l_uiStrings = _l_uiStrings
        self._d_dir = _d_dir
        self._d_uiStrings = _d_uiStrings
        self._l_itc = []
        
        d_colors = {'left':[.4,.4,1],
                    'center': [1,2,1],
                    'right':[.9,.2,.2]}

        for i,uiString in enumerate(_l_uiStrings):
            _color = [.9,.2,.2]#d_colors.get(d_colors['center'])
            self._l_itc.append(_color)            
            self._d_itc[uiString] = _color
            
            self._l_strings.append(uiString)
            
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
        self._ml_loaded = []
        
    def clearSelection( self,):
        self( e=True, deselectAll=True )
        
    def set_filterObj(self,obj=None):
        self.filterField = obj

    def update_display(self,searchFilter='',matchCase = False):
        _str_func = 'update_display'
        log.debug(cgmGEN.logString_start(_str_func))
        
        l_items = self.getSelectedItems()
        
        if self.filterField is not None:
            searchFilter = self.filterField.getValue()
        
        self.clear()
        try:
            for i,strEntry in enumerate(r9Core.filterListByString(self._l_strings,
                                                                  searchFilter,
                                                                  matchcase=matchCase)):
                if strEntry in self._l_str_loaded:
                    log.warning("Duplicate string")
                    continue
                
                self.append(strEntry)
                self._l_str_loaded.append(strEntry)
                
                #idx = self._l_strings.index(strEntry)
                #_mBlock = self._ml_scene[idx]
                #self._ml_loaded.append(_mBlock)
                #_color = d_state_colors.get(_mBlock.getEnumValueString('blockState'))
                _color = self._d_itc[strEntry]
                try:self(e=1, itc = [(i+1,_color[0],_color[1],_color[2])])
                except:pass

        except Exception,err:
            log.error("|{0}| >> err: {1}".format(_str_func, err))  
            for a in err:
                log.error(a)

    def selectCallBack(self,func=None,*args,**kws):
        print self.getSelectedBlocks()
        
        
def mrsPoseDirSelect(self,ui = None):
    _str_func = 'mrsPoseDirSelect'
    log.debug(cgmGEN.logString_start(_str_func))
    
    _dir = self.getSelectedDir()
    _d = self._d_dir[_dir[0]]
    
    _depth = _d['depth']
    if not _depth:
        _str = _d['token']
    else:
        _str = ' | '.join(_d['split'][-_d['depth']:])
        
    ui.uiFrame_subDir(edit=1, label = "Sub : {0} ".format( CORESTRINGS.short(_str, 20)))
    
    ui.posePath = _dir[0]
    uiCB_fillPoses(ui,True)
    
    return
    basePath = self.cgmUIField_posePath.getValue()
    # turn OFF the 2 main poseScrollers
    mc.textScrollList(self.cgmUItslPoses, edit=True, vis=False)
    mc.scrollLayout(self.cgmUIglPoseScroll, edit=True, vis=False)
    # turn ON the subFolder scroller
    mc.textScrollList(self.cgmUItslPoseSubFolders, edit=True, vis=True)
    mc.textScrollList(self.cgmUItslPoseSubFolders, edit=True, ra=True)

    if not os.path.exists(basePath):
        # path not valid clear all
        log.warning('No current PosePath set')
        return

    dirs = [subdir for subdir in os.listdir(basePath) if os.path.isdir(os.path.join(basePath, subdir))]
    if not dirs:
        raise StandardError('Folder has no subFolders for pose scanning')
    for subdir in dirs:
        mc.textScrollList(self.cgmUItslPoseSubFolders, edit=True,
                                        append='/%s' % subdir,
                                        sc=cgmGEN.Callback(self._uiCB_setSubFolder))

    #def _uiCB_setSubFolder(self, *args):
    '''
    Select a subFolder from the scrollList and update the systems
    '''
    #basePath = mc.textFieldButtonGrp(self.cgmUItfgPosePath, query=True, text=True)
    basePath = self.cgmUIField_posePath.getValue()
    
    subFolder = mc.textScrollList(self.cgmUItslPoseSubFolders, q=True, si=True)[0].split('/')[-1]

    #mc.textFieldButtonGrp('cgmUItfgPoseSubPath', edit=True, text=subFolder)
    self.cgmUIField_subPath.setValue(subFolder)
    mc.textScrollList(self.cgmUItslPoseSubFolders, edit=True, vis=False)
    self.posePath = os.path.join(basePath, subFolder)
    self._uiCB_pathSwitchInternals()    
    
def buildFrame_mrsPoseDir(self,parent):
    try:self.var_mrsListFrameCollapse
    except:self.create_guiOptionVar('mrsPoseDirFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_mrsPoseDirFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Dir',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    
    self.uiFrame_subDir = _frame
    
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate')
    
    """
    _textField = mUI.MelTextField(_inside,
                                  ann='Filter blocks',
                                  w=50,
                                  bgc = [.3,.3,.3],
                                  en=True,
                                  text = '')
    self.cgmUIField_filterScene = _textField"""

    
    _scrollList = mrsPoseDirList(_inside, ut='cgmUISubTemplate',
                                 allowMultiSelection=0,en=True,
                                 ebg=0,
                                 h=100,
                                 bgc = [.2,.2,.2],
                                 #dcc = cgmGEN.Callback(self.uiFunc_block_setActive),
                                 w = 50)
    
    try:_scrollList(edit=True,hlc = [.5,.5,.5])
    except:pass
    
    _scrollList.set_selCallBack(mrsPoseDirSelect,_scrollList,self)
    
    #_scrollList.cmd_select = lambda *a:self.uiScrollList_block_select()
    #_scrollList.set_filterObj(self.cgmUIField_filterScene)
    #self.cgmUIField_filterScene(edit=True,
    #                             tcc = lambda *a: self.uiScrollList_blocks.update_display())
    
    self.uiScrollList_dir = _scrollList
    _row = mUI.MelHLayout(_inside,padding=5,)
    button_refresh = mUI.MelButton(_row,
                                   label='Clear Sel',ut='cgmUITemplate',
                                    c=lambda *a:self.uiScrollList_dir.clearSelection(),
                                    ann='Clear selection the scroll list to update')     
    button_refresh = mUI.MelButton(_row,
                                   label='Refresh',ut='cgmUITemplate',
                                    c=lambda *a:self.uiScrollList_dir.rebuild(),
                                    ann='Force the scroll list to update')    
    _row.layout()