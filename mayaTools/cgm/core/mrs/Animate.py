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
log.setLevel(logging.INFO)

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

from cgm.core import cgm_RigMeta as cgmRigMeta
import cgm.core.mrs.RigBlocks as RIGBLOCKS
import cgm.core.mrs.lib.general_utils as BLOCKGEN

mUI = cgmUI.mUI

import cgm.core.lib.name_utils as NAMES
from cgm.core.lib import shared_data as SHARED
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
import cgm.core.lib.transform_utils as TRANS
from cgm.core.cgmPy import path_Utils as CGMPATH
import cgm.core.lib.math_utils as MATH
from cgm.lib import lists
import cgm.core.tools.lib.tool_chunks as UICHUNKS
import cgm.core.tools.dynParentTool as DYNPARENTTOOL
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.markingMenus.lib.contextual_utils as CONTEXT
import cgm.core.tools.toolbox as TOOLBOX
import cgm.core.lib.search_utils as SEARCH
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.list_utils as LISTS
import cgm.core.rig.general_utils as RIGGEN
import cgm.core.mrs.lib.animate_utils as MRSANIMUTILS

import cgm.core.tools.markingMenus.lib.mm_utils as MMUTILS
#reload(MMUTILS)

import cgm.core.mrs.PoseManager as POSEMANAGER
#reload(POSEMANAGER)

from cgm.core.lib.ml_tools import (ml_breakdownDragger,
                                   ml_breakdown,
                                   ml_resetChannels,
                                   ml_deleteKey,
                                   ml_setKey,
                                   ml_hold,
                                   ml_stopwatch,
                                   ml_arcTracer,
                                   ml_utilities,
                                   ml_convertRotationOrder,
                                   ml_copyAnim)
#>>> Root settings =============================================================
__version__ = '1.07162019'
__toolname__ ='MRSAnimate'
_d_contexts = MRSANIMUTILS._d_contexts
_l_contexts = MRSANIMUTILS._l_contexts
_l_contextTime = MRSANIMUTILS._l_contextTime

_d_shorts = MRSANIMUTILS._d_timeShorts
_l_contextKeys = MRSANIMUTILS._l_contextKeys

_subLineBGC = [.75,.75,.75]

log_start = cgmGEN.log_start
log_sub = cgmGEN.log_sub

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = '{0}_ui'.format(__toolname__)    
    WINDOW_TITLE = '{1} - {0}'.format(__version__,__toolname__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 300,500
    TOOLNAME = '{0}UI'.format(__toolname__)
    
    is_dragging_tween = False

    def insert_init(self,*args,**kws):
        _str_func = '__init__[{0}]'.format(self.__class__.TOOLNAME)            
        log.info("|{0}| >>...".format(_str_func))        

        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        log.info(self.__call__(q=True, title=True))

        self.__version__ = __version__
        self.__toolName__ = self.__class__.WINDOW_NAME	
        self._sel = None
        #self.l_allowedDockAreas = []
        self.WINDOW_TITLE = self.__class__.WINDOW_TITLE
        self.DEFAULT_SIZE = self.__class__.DEFAULT_SIZE
        
        self.mDat = MRSANIMUTILS.get_sharedDatObject()#MRSANIMUTILS.MRSDAT
        self.create_guiOptionVar('puppetFrameCollapse',defaultValue = 0) 
        
        self.uiPopUpMenu_poses = None
        self.uiMenu_snap = None
        self.uiMenu_help = None
        self.uiMenu_vis = None
        self._l_contexts = _l_contexts
        self._l_contextTime = _l_contextTime
        self._l_contextKeys = _l_contextKeys
        self.mmCallback = cgmGEN.Callback
        MRSANIMUTILS.uiSetup_context(self,self.__class__.TOOLNAME)
        self.mmCallback = cgmGEN.Callback

        """
        try:self.var_poseMatchMethod
        except:self.var_poseMatchMethod = cgmMeta.cgmOptionVar('cgmVar_poseMatchMethod', defaultValue = 'base')
            
        try:self.var_mrsContext
        except:self.var_mrsContext = cgmMeta.cgmOptionVar('cgmVar_mrsContext_mode',
                                                          defaultValue = _l_contexts[0])
        try:self.var_mrsContextTime
        except:self.var_mrsContextTime = cgmMeta.cgmOptionVar('cgmVar_mrsContext_time',
                                                          defaultValue = 'current')
        try:self.var_mrsContextKeys
        except:self.var_mrsContextKeys = cgmMeta.cgmOptionVar('cgmVar_mrsContext_keys',
                                                          defaultValue = 'each')
        """
        self.filterSettings = r9Core.FilterNode_Settings()
        self.filterSettings.metaRig = False
        self.filterSettings.transformClamp = False
        
    def build_menus(self):
        log.debug("build menus... "+'-'*50)
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = lambda *a:self.buildMenu_first())
        self.uiMenu_switch = mUI.MelMenu( l='Switch', pmc=lambda *a:self.buildMenu_switch())                 
        self.uiMenu_snap = mUI.MelMenu( l='Snap', pmc=self.buildMenu_snap)
        self.uiMenu_vis = mUI.MelMenu(l = 'Vis', pmc = lambda *a:self.buildMenu_vis()) 
        
        #self.uiMenu_picker = mUI.MelMenu( l='Picker',pmc=lambda *a:self.buildMenu_picker(True), tearOff=1)                
        self.uiMenu_help = mUI.MelMenu(l = 'Help', pmc = lambda *a:self.buildMenu_help()) 
        
        
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
        mUI.MelMenuItem( self.uiMenu_help, l="Get Pose Nodes",
                         c=lambda *a: self.get_poseNodes(select=True) )
        mUI.MelMenuItem( self.uiMenu_help, l="Reset Animate Module",
                         c=lambda *a: reload(MRSANIMUTILS) )        

        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("https://http://docs.cgmonks.com/mrs.html");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )   
        mUI.MelMenuItem( self.uiMenu_help, l="Update Display",
                         c=lambda *a: self.cgmUIUpdate_building() )
        
        
    def buildMenu_snap( self, force=False, *args, **kws):
        if self.uiMenu_snap and force is not True:
            return
        self.uiMenu_snap.clear()
        
        UICHUNKS.uiSection_snap(self.uiMenu_snap)
            
        mUI.MelMenuItemDiv(self.uiMenu_snap)
        
        mUI.MelMenuItem(self.uiMenu_snap, l='Rebuild',
                        c=self.mmCallback(self.buildMenu_snap,True))
        log.debug("Snap menu rebuilt")
        
    def buildMenu_vis( self, force=False, *args, **kws):
        if self.uiMenu_vis and force is not True:
            return
        self.uiMenu_vis.clear()        
        
        
        #Toggles ===============================================================================
        #_toggle = mc.menuItem(p=parent,l="Toggle",subMenu=True)
        
        l_settings = ['visModule','visSub','visDirect','visRoot']
        l_enums = ['skeleton','geo','proxy']
    
        for n in l_settings + l_enums:
            _sub = mc.menuItem(p=self.uiMenu_vis, l=n, subMenu=True)
            if n in l_settings:
                l_options = ['hide','show']
                
                if n == 'visModule':
                    _mode = 'moduleVis'
                else:
                    _mode = 'moduleSettings'
            else:
                l_options = ['off','lock','on']
                _mode = 'puppetSettings'
                
            _d_tmp = {}
            #_d_tmp = {'contextMode':None,
            #          'contextTime':None,
            #          'contextMirror':False,
            #          'contextChildren':False,
            #          'contextSiblings':False}
            
            for v,o in enumerate(l_options):
                mUI.MelMenuItem(_sub,
                                l=o,
                                c=self.mmCallback(uiCB_contextSetValue,self,n,v,_mode,**_d_tmp))
                
                
                #mc.menuItem(p=_sub,l=o,c=self.mmCallback(uiCB_contextSetValue,self,n,v,_mode,**_d_tmp))        
        
        
    def uiFunc_fillPickerMenu():
        try:
            mList = self.uiScrollList_blocks
        except:
            return log.error("No blocklist")
        
        _ml,_l_strings = BLOCKGEN.get_uiModuleScollList_dat(showSide=1,presOnly=1)
        
        def getString(pre,string):
            i = 1
            _check = ''.join([pre,string])
            while _check in self._l_strings and i < 100:
                _check = ''.join([pre,string,' | NAMEMATCH [{0}]'.format(i)])
                i +=1
            return _check
        
        def get_side(mNode):
            _cgmDirection = mNode.getMayaAttr('cgmDirection')
            if _cgmDirection:
                if _cgmDirection[0].lower() == 'l':
                    return 'left'
                return 'right'
            return 'center'
        
        for i,mBlock in enumerate(_ml):
            _arg = get_side(mBlock)
            _color = d_colors.get(_arg,d_colors['center'])
            self._l_itc.append(_color)            
            self._d_itc[mBlock] = _color
            try:
                _str_base = mBlock.UTILS.get_uiString(mBlock)#mBlock.p_nameBase#
                #_modType = mBlock.getMayaAttr('moduleType')
                #if _modType:
                    #_str_base = _str_base + ' | [{0}]'.format(_modType)
            except:_str_base = 'FAIL | {0}'.format(mBlock.mNode)
            _pre = _l_strings[i]
            self._l_strings.append(getString(_pre,_str_base))        
        
        
    def buildMenu_picker(self,force=False, *args,**kws):
        if self.uiMenu_snap and force is not True:
            return
        self.uiMenu_picker.clear()
        
        _menu = self.uiMenu_picker
        
        try:#Try to get our list dat
            mList = self.uiScrollList_blocks
        except:
            return log.error("No blocklist")        
        
        if not mList._ml_scene:
            mUI.MelMenuItem(_menu, l="None")
        else:
            for i,mObj in enumerate(mList._ml_scene):
                _str = mList._l_strings[i]
                _sub = mUI.MelMenuItem(_menu, l="{0}".format(_str),tearOff=True,
                                       subMenu = True)
                try:
                    mObj.atUtils('uiMenu_picker',_sub)
                except:
                    pass
        

        mUI.MelMenuItemDiv(self.uiMenu_picker)
        mUI.MelMenuItem(self.uiMenu_picker, l='Rebuild',
                        c=self.mmCallback(self.buildMenu_picker,True))
        log.debug("Snap menu rebuilt")        
        
        """
        try:
            mList = self.uiScrollList_blocks
        except:
            return log.error("No blocklist")

        _menu = self.uiMenu_picker

        ml_blocks = mList.getSelectedBlocks()
        if not ml_blocks:
            mUI.MelMenuItem(_menu, l="None")
            return log.error("Nothing selected")
            
        for mBlock in ml_blocks:
            mBlockModule = mBlock.getBlockModule()
            
            _sub = mUI.MelMenuItem(_menu, l="{0}".format(mBlock.UTILS.get_uiString(mBlock)),tearOff=True,
                                   subMenu = True)            
            #if 'uiBuilderMenu' in mBlockModule.__dict__.keys():
            mBlock.atUtils('uiStatePickerMenu',_sub)"""
        
        
    def buildMenu_switch(self, *args):
        log.debug("buildMenu_switch..."+'-'*50)
        self.uiMenu_switch.clear()
        
        d_contextSettings = MRSANIMUTILS.get_contextDict(self.__class__.TOOLNAME)
        self._ml_objList = cgmMeta.validateObjListArg( CONTEXT.get_list(getTransform=True) )
        #pprint.pprint(self._ml_objList)
        DYNPARENTTOOL.uiMenu_changeSpace(self,self.uiMenu_switch,True,d_contextSettings)

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options
        
        parent = self.uiMenu_FirstMenu
        _mDev = mUI.MelMenuItem(self.uiMenu_FirstMenu, l="Dev",subMenu=True)
        mUI.MelMenuItem(_mDev, l="Puppet - Mirror verify",
                        ann = "Please don't mess with this if you don't know what you're doing ",
                        c = self.mmCallback(uiCB_contextualAction,self,**{'mode':'mirrorVerify','context':'puppet'}))
        mUI.MelMenuItem(_mDev, l="Puppet - Up to date?",
                        ann = "Please don't mess with this if you don't know what you're doing ",
                        c = self.mmCallback(uiCB_contextualAction,self,**{'mode':'upToDate','context':'puppet'}))
        mUI.MelMenuItem(_mDev,l="Reset Buffer",
                        ann = "Reset anim buffer",
                        c = self.mmCallback(uiCB_bufferDat,self,True))
        
        
        #MatchMode ...
        POSEMANAGER.uiMenuItem_matchMode(self,self.uiMenu_FirstMenu)
        
        """
        uiPoseMatchMode = mc.menuItem(p=parent, l='Pose Match Method ', subMenu=True)
        
        uiRC = mc.radioMenuItemCollection()
        _v = self.var_poseMatchMethod.value
        
        for i,item in enumerate(['base','metaData','stripPrefix','index','mirrorIndex','mirrorIndex_ID']):
            if item == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(p=uiPoseMatchMode,collection = uiRC,
                        label=item,
                        c = self.mmCallback(self.var_poseMatchMethod.setValue,item),
                        rb = _rb)        
        """
        
        
    
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Dock",
                         c = lambda *a:self.do_dock())
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))   
        
    def build_layoutWrapper2(self,parent):
        _str_func = 'build_layoutWrapper'
        #self._d_uiCheckBoxes = {}
        log.debug("{0}...".format(_str_func)+'-'*50)
    
        #_MainForm = mUI.MelFormLayout(parent,ut='cgmUISubTemplate')
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
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        #Match
        #Aim

        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        ui_tabs = mUI.MelTabLayout( _MainForm)
        self.cgmUITab_setup = ui_tabs
        
        uiTab_mrs = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')
        #uiTab_poses = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')
        uiTab_anim = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')        
        uiTab_settings = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')

        for i,tab in enumerate(['Anim','Tools','Settings']):
            ui_tabs.setLabel(i,tab)

        buildTab_mrs(self,uiTab_mrs)
        #buildTab_poses(self,uiTab_poses)
        
        #buildTab_anim(self,uiTab_poses)
        reload(TOOLBOX)
        TOOLBOX.optionVarSetup_basic(self)
        TOOLBOX.buildTab_options(self,uiTab_settings)
        TOOLBOX.buildTab_anim(self,uiTab_anim)
        
        mc.setParent(_MainForm)
        self.uiProgressBar = mc.progressBar(vis=False)
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)  
        _MainForm(edit = True,
                  af = [(ui_tabs,"top",0),
                        (ui_tabs,"left",0),
                        (ui_tabs,"right",0),
                        (self.uiProgressBar,"left",0),
                        (self.uiProgressBar,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),

                        ],
                  ac = [(ui_tabs,"bottom",0,self.uiProgressBar),
                        (self.uiProgressBar,"bottom",0,_row_cgm)
                        ],
                  attachNone = [(_row_cgm,"top")])  
        
    #RED 9 PORTION ==================================================================================
    # -----------------------------------------------------------------------------
    # PoseSaver Path Management ---
    # ------------------------------------------------------------------------------

    def setPoseSelected(self, val=None, *args):
        '''
        set the PoseSelected cache for the UI calls
        '''
        if not self.poseGridMode == 'thumb':
            self.poseSelected = mc.textScrollList(self.cgmUItslPoses, q=True, si=True)[0]
        else:
            self.poseSelected = val
        log.debug('PoseSelected : %s' % self.poseSelected)

    def getPoseSelected(self):
        if not self.poseSelected:
            raise StandardError('No Pose Selected in the UI')
        return self.poseSelected

    def buildPoseList(self, sortBy='name'):
        '''
        Get a list of poses from the PoseRootDir, this allows us to
        filter much faster as it stops all the os calls, cached list instead
        '''
        self.poses = []
        if not CGMPATH.Path(self.posePath):#os.path.exists(self.posePath):
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

    def buildFilteredPoseList(self, searchFilter):
        '''
        build the list of poses to show in the poseUI
        TODO: hook up an order based by date in here as an option to tie into the UI
        '''
        filteredPoses = self.poses
        if searchFilter:
            filteredPoses = []
            filters = searchFilter.replace(' ', '').split(',')
            for pose in self.poses:
                for srch in filters:
                    if srch and srch.upper() in pose.upper():
                        if pose not in filteredPoses:
                            filteredPoses.append(pose)
        return filteredPoses

    def __validatePoseFunc(self, func):
        '''
        called in some of the funcs so that they either raise an error when called in 'Project' mode
        or raise a Confirm Dialog to let teh user decide. This behaviour is controlled by the var
        self.poseProjectMute
        '''
        if self.posePathMode == 'projectPoseMode':
            if self.poseProjectMute:
                raise StandardError('%s : function disabled in Project Pose Mode!' % func)
            else:
                result = mc.confirmDialog(
                    title='Project Pose Modifications',
                    button=['Continue', 'Cancel'],
                    message='You are trying to modify a Project Pose\n\nPlease Confirm Action!',
                    defaultButton='Cancel',
                    icon='warning',
                    cancelButton='Cancel',
                    bgc=r9Setup.red9ButtonBGC('red'),
                    dismissString='Cancel')
                if result == 'Continue':
                    return True
                else:
                    log.info('Pose Project function : "%s" : aborted by user' % func)
        else:
            return True

    def _uiCB_selectPose(self, pose):
        '''
        select the pose in the UI from the name
        '''
        if pose:
            if not self.poseGridMode == 'thumb':
                mc.textScrollList(self.cgmUItslPoses, e=True, si=pose)
            else:
                self._uiCB_iconGridSelection(pose)
                
                

    def _uiCB_switchPosePathMode(self, mode, *args):
        '''
        Switch the Pose mode from Project to Local. In project mode save is disabled.
        Both have different caches to store the 2 mapped root paths

        :param mode: 'local' or 'project', in project the poses are load only, save=disabled
        '''
        if mode == 'local' or mode == 'localPoseMode':
            self.posePath = os.path.join(self.posePathLocal, self.getPoseSubFolder())
            if not CGMPATH.Path(self.posePath):#os.path.exists(self.posePath):
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
            if not CGMPATH.Path(self.posePath):#os.path.exists(self.posePath):
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
        self._uiCB_fillPoses(rebuildFileList=True)

    def _uiCB_setPosePath(self, path=None, field = False, fileDialog=False):
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
        
        if not CGMPATH.Path(self.posePath):
            log.error("|{0}| >> Invalid path: {1}".format(_str_func,self.posePath))            
            self.posePath = ''
            return 
        
        mVar.setValue(self.posePath)
        self.cgmUIField_posePath.setValue(self.posePath,executeChangeCB=False)
        self.cgmUIField_posePath(edit=True, ann = self.posePath)
        #mc.textFieldButtonGrp(self.cgmUItfgPosePath, edit=True, text=self.posePath)
        
        if self.var_pathMode.getValue == 'local':
            self.posePathLocal = self.posePath
        else:
            self.posePathProject = self.posePath
            
        #pprint.pprint(vars())
        self.cgmUIField_subPath.setValue('')
        #self._uiCB_pathSwitchInternals()
        
        return
        mc.textFieldButtonGrp('cgmUItfgPoseSubPath', edit=True, text="")
        
        # internal cache for the 2 path modes


    def _uiCB_pathSwitchInternals(self):
        '''
        fill the UI Cache and update the poses in eth UI
        '''
        self._uiCB_fillPoses(rebuildFileList=True)

        # fill the cache up for the ini file
        self.ANIM_UI_OPTVARS['AnimationUI']['posePath'] = self.posePath
        self.ANIM_UI_OPTVARS['AnimationUI']['poseSubPath'] = self.getPoseSubFolder()
        self.ANIM_UI_OPTVARS['AnimationUI']['posePathLocal'] = self.posePathLocal
        self.ANIM_UI_OPTVARS['AnimationUI']['posePathProject'] = self.posePathProject
        self.ANIM_UI_OPTVARS['AnimationUI']['posePathMode'] = self.posePathMode
        self._uiCache_storeUIElements()


    # SubFolder Pose Calls ----------
    def _uiCB_switchSubFolders(self, *args):
        '''
        switch the scroller from pose mode to subFolder select mode
        note we prefix the folder with '/' to help denote it's a folder in the UI
        '''
        #basePath = mc.textFieldButtonGrp(self.cgmUItfgPosePath, query=True, text=True)
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
                                            sc=self.mmCallback(self._uiCB_setSubFolder))

    def _uiCB_setSubFolder(self, *args):
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

    def _uiCB_clearSubFolders(self, *args):
        mc.textScrollList(self.cgmUItslPoseSubFolders, edit=True, vis=False)
        self._uiCB_setPosePath()

    # ----------------------------------------------------------------------------
    # Build Pose UI calls  ---
    # ----------------------------------------------------------------------------

    def getPoseSubFolder(self):
        '''
        Return the given pose subFolder if set
        '''
        try:
            return self.cgmUIField_subPath.getValue()#mc.textFieldButtonGrp('cgmUItfgPoseSubPath', q=True, text=True)
        except:
            return ""

    def getPoseDir(self):
        '''
        Return the poseDir including subPath
        '''
        #return os.path.join(self.posePath,
        #                    self.getPoseSubFolder())        
        return os.path.join(self.cgmUIField_posePath.getValue(),
                            self.getPoseSubFolder())

    def getPosePath(self):
        '''
        Return the full posePath for loading
        '''
        return os.path.join(self.getPoseDir(), '%s.pose' % self.getPoseSelected())

    def getIconPath(self):
        '''
        Return the full posePath for loading
        '''
        return os.path.join(self.getPoseDir(), '%s.bmp' % self.getPoseSelected())

    def _uiCB_fillPoses(self, rebuildFileList=False, searchFilter=None, sortBy='name', *args):
        '''
        Fill the Pose List/Grid from the given directory
        '''

        # Store the current mode to the Cache File
        self.ANIM_UI_OPTVARS['AnimationUI']['poseMode'] = self.poseGridMode
        self._uiCache_storeUIElements()
        searchFilter = self.cgmUIField_searchPath.getValue()#mc.textFieldGrp(self.tfPoseSearchFilter, q=True, text=True)

        if rebuildFileList:
            self.buildPoseList(sortBy=sortBy)
            log.debug('Rebuilt Pose internal Lists')
            # Project mode and folder contains NO poses so switch to subFolders
            if not self.poses and self.posePathMode == 'projectPoseMode':
                log.warning('No Poses found in Root Project directory, switching to subFolder pickers')
                try:self._uiCB_switchSubFolders()
                except:pass
                return
        log.debug('searchFilter  : %s : rebuildFileList : %s' % (searchFilter, rebuildFileList))

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
                                        sc=self.mmCallback(self.setPoseSelected))
        # Grid Layout
        # ================================
        else:
            mc.textScrollList(self.cgmUItslPoseSubFolders, edit=True, vis=False)  # subfolder scroll OFF
            mc.textScrollList(self.cgmUItslPoses, edit=True, vis=False)  # pose TexScroll OFF
            mc.scrollLayout(self.cgmUIglPoseScroll, edit=True, vis=True)  # pose Grid ON
            self._uiCB_gridResize()

            # Clear the Grid if it's already filled
            try:
                [mc.deleteUI(button) for button in mc.gridLayout(self.cgmUIglPoses, q=True, ca=True)]
            except StandardError, error:
                print error
            for pose in r9Core.filterListByString(self.poses, searchFilter, matchcase=False):  # self.buildFilteredPoseList(searchFilter):
                try:
                    # :NOTE we prefix the buttons to get over the issue of non-numeric
                    # first characters which are stripped my Maya!
                    mc.iconTextCheckBox('_%s' % pose, style='iconAndTextVertical',
                                            image=os.path.join(self.posePath, '%s.bmp' % pose),
                                            label=pose,
                                            bgc=self.poseButtonBGC,
                                            parent=self.cgmUIglPoses,
                                            ann=pose,
                                            onc=self.mmCallback(self._uiCB_iconGridSelection, pose),
                                            ofc="import maya.cmds as cmds;mc.iconTextCheckBox('_%s', e=True, v=True)" % pose)  # we DONT allow you to deselect
                except StandardError, error:
                    raise StandardError(error)

            if searchFilter:
                # with search scroll the list to the top as results may seem blank otherwise
                mc.scrollLayout(self.cgmUIglPoseScroll, edit=True, sp='up')

        # Finally Bind the Popup-menu
        mc.evalDeferred(self._uiCB_PosePopup)

    def _uiCB_fill_mRigsPopup(self, *args):
        '''
        Fill the Pose root mRig popup menu
        '''
        mc.popupMenu('_setPose_mRigs_current', e=True, deleteAllItems=True)
        if self.poseRootMode == 'MetaRoot':
            # fill up the mRigs
            mc.menuItem(label='AUTO RESOLVED : mRigs', p='_setPose_mRigs_current',
                          command=self.mmCallback(self._uiCB_setPoseRootNode, '****  AUTO__RESOLVED  ****'))
            mc.menuItem(p='_setPose_mRigs_current', divider=True)
            #  mc.menuItem(p='_setPose_mRigs_current', divider=True)
            for rig in r9Meta.getMetaRigs():
                if rig.hasAttr('exportTag') and rig.exportTag:
                    mc.menuItem(label='%s :: %s' % (rig.exportTag.tagID, rig.mNode), p='_setPose_mRigs_current',
                              command=self.mmCallback(self._uiCB_setPoseRootNode, rig.mNode))
                else:
                    mc.menuItem(label=rig.mNode, p='_setPose_mRigs_current',
                              command=self.mmCallback(self._uiCB_setPoseRootNode, rig.mNode))
    
    def _uiCB_PosePopup(self, *args):
        '''
        RMB popup menu for the Pose functions
        '''        
        enableState = True
        if self.posePathMode == 'projectPoseMode' and self.poseProjectMute:
            enableState = False

        if self.poseGridMode == 'thumb':
            parent = self.posePopupGrid
            mc.popupMenu(self.posePopupGrid, e=True, deleteAllItems=True)
        else:
            parent = self.posePopupText
            mc.popupMenu(self.posePopupText, e=True, deleteAllItems=True)

        #mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_blender, p=parent,
        #            command=self.mmCallback(self._uiCall, 'PoseBlender'))
        
        
        #Pose basics -----------------------------------------------------------------------
        mc.menuItem(divider=True, p=parent)
        mc.menuItem(label='Delete', en=enableState, p=parent,
                    command=self.mmCallback(self._uiPoseDelete))
        mc.menuItem(label='Rename', en=enableState, p=parent,
                    command=self.mmCallback(self._uiPoseRename))
        #mc.menuItem(label='Select internals', p=parent,
        #            command=self.mmCallback(self._uiPoseSelectObjects))
        
        #Edit pose ------------------------------------------------------------------
        mc.menuItem(divider=True, p=parent)
        mc.menuItem(label='Update pose', en=enableState, p=parent,
                    command=self.mmCallback(self._uiPoseUpdate, False))
        if self.poseGridMode == 'thumb':
            mc.menuItem(label='Update thumb', p=parent, command=self.mmCallback(self._uiPoseUpdateThumb))
        mc.menuItem(label='Update both', en=enableState, p=parent, command=self.mmCallback(self._uiPoseUpdate, True))
        
        
        #Folders -----------------------------------------------
        mc.menuItem(divider=True, p=parent)
        mc.menuItem(label='Add subfolder', en=enableState, p=parent, command=self.mmCallback(self._uiPoseMakeSubFolder))
        mc.menuItem(label='Refresh', en=True, p=parent, command=lambda x: self._uiCB_fillPoses(rebuildFileList=True))
        mc.menuItem(label='Open File', p=parent, command=self.mmCallback(self._uiPoseOpenFile))
        mc.menuItem(label='Open Dir', p=parent, command=self.mmCallback(self._uiPoseOpenDir))
        
        #mc.menuItem(divider=True, p=parent)
        #mc.menuItem('red9PoseCompareSM', l=LANGUAGE_MAP._AnimationUI_.pose_rmb_compare, sm=True, p=parent)
        #mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_compare_skel, p='red9PoseCompareSM', command=self.mmCallback(self._uiCall, 'PoseCompareSkelDict'))
        #mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_compare_posedata, p='red9PoseCompareSM', command=self.mmCallback(self._uiCall, 'PoseComparePoseDict'))

        #mc.menuItem(label='Add Pose Handler', en=enableState, p=parent, command=self.mmCallback(self._uiPoseAddPoseHandler))
        
        #mc.menuItem(divider=True, p=parent)
        #mc.menuItem(label='Copy Pose', en=enableState, p=parent, command=self.mmCallback(self._uiPoseCopyToProject))

        mc.menuItem(divider=True, p=parent)
        mc.menuItem(label='Switch Mode', p=parent, command=self._uiCB_switchPoseMode)

        if self.poseGridMode == 'thumb':
            mc.menuItem(divider=True, p=parent)
            mc.menuItem(label='Thumb - small', p=parent, command=self.mmCallback(self._uiCB_setPoseGrid, 'small'))
            mc.menuItem(label='Thumb - med', p=parent, command=self.mmCallback(self._uiCB_setPoseGrid, 'medium'))
            mc.menuItem(label='Thumb - large', p=parent, command=self.mmCallback(self._uiCB_setPoseGrid, 'large'))

        if self.posePath:
            mc.menuItem(divider=True, p=parent)
            self.addPopupMenusFromFolderConfig(parent)
        if self.poseHandlerPaths:
            mc.menuItem(divider=True, p=parent)
            self.addPopupMenus_PoseHandlers(parent)
        

    def _uiCB_PosePopup2(self, *args):
        '''
        RMB popup menu for the Pose functions
        '''
        enableState = True
        if self.posePathMode == 'projectPoseMode' and self.poseProjectMute:
            enableState = False

        if self.poseGridMode == 'thumb':
            parent = self.posePopupGrid
            mc.popupMenu(self.posePopupGrid, e=True, deleteAllItems=True)
        else:
            parent = self.posePopupText
            mc.popupMenu(self.posePopupText, e=True, deleteAllItems=True)

        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_blender, p=parent, command=self.mmCallback(self._uiCall, 'PoseBlender'))
        mc.menuItem(divider=True, p=parent)
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_delete, en=enableState, p=parent, command=self.mmCallback(self._uiPoseDelete))
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_rename, en=enableState, p=parent, command=self.mmCallback(self._uiPoseRename))
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_selectinternal, p=parent, command=self.mmCallback(self._uiPoseSelectObjects))

        mc.menuItem(divider=True, p=parent)
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_update_pose, en=enableState, p=parent, command=self.mmCallback(self._uiPoseUpdate, False))
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_update_pose_thumb, en=enableState, p=parent, command=self.mmCallback(self._uiPoseUpdate, True))

        if self.poseGridMode == 'thumb':
            mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_update_thumb, p=parent, command=self.mmCallback(self._uiPoseUpdateThumb))

        mc.menuItem(divider=True, p=parent)
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_add_subfolder, en=enableState, p=parent, command=self.mmCallback(self._uiPoseMakeSubFolder))
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_refresh, en=True, p=parent, command=lambda x: self._uiCB_fillPoses(rebuildFileList=True))
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_openfile, p=parent, command=self.mmCallback(self._uiPoseOpenFile))
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_opendir, p=parent, command=self.mmCallback(self._uiPoseOpenDir))
        mc.menuItem(divider=True, p=parent)
        mc.menuItem('red9PoseCompareSM', l=LANGUAGE_MAP._AnimationUI_.pose_rmb_compare, sm=True, p=parent)
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_compare_skel, p='red9PoseCompareSM', command=self.mmCallback(self._uiCall, 'PoseCompareSkelDict'))
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_compare_posedata, p='red9PoseCompareSM', command=self.mmCallback(self._uiCall, 'PoseComparePoseDict'))

        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_copyhandler, en=enableState, p=parent, command=self.mmCallback(self._uiPoseAddPoseHandler))
        mc.menuItem(divider=True, p=parent)
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_copypose, en=enableState, p=parent, command=self.mmCallback(self._uiPoseCopyToProject))

        mc.menuItem(divider=True, p=parent)
        mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_switchmode, p=parent, command=self._uiCB_switchPoseMode)

        if self.poseGridMode == 'thumb':
            mc.menuItem(divider=True, p=parent)
            mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_grid_small, p=parent, command=self.mmCallback(self._uiCB_setPoseGrid, 'small'))
            mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_grid_med, p=parent, command=self.mmCallback(self._uiCB_setPoseGrid, 'medium'))
            mc.menuItem(label=LANGUAGE_MAP._AnimationUI_.pose_rmb_grid_large, p=parent, command=self.mmCallback(self._uiCB_setPoseGrid, 'large'))

        if self.posePath:
            mc.menuItem(divider=True, p=parent)
            self.addPopupMenusFromFolderConfig(parent)
        if self.poseHandlerPaths:
            mc.menuItem(divider=True, p=parent)
            self.addPopupMenus_PoseHandlers(parent)

    def addPopupMenus_PoseHandlers(self, parentPopup):
        '''
        for a given list of folders containing poseHandler files add these as 
        default 'make subfolder' types to the main poseUI popup menu
        '''
        if self.poseHandlerPaths:
            for path in self.poseHandlerPaths:
                log.debug('Inspecting PoseHandlerPath : %s' % path)
                if os.path.exists(path):
                    poseHandlers = os.listdir(path)
                    if poseHandlers:
                        for handler in poseHandlers:
                            if handler.endswith('_poseHandler.py'):
                                handlerPath = os.path.join(path, handler)
                                log.debug('poseHandler file being bound to RMB popup : %s' % handlerPath)
                                mc.menuItem(label='Add Subfolder : %s' % handler.replace('_poseHandler.py', '').upper(),
                                              en=True, p=parentPopup,
                                              command=self.mmCallback(self._uiPoseMakeSubFolder, handlerPath))

    def addPopupMenusFromFolderConfig(self, parentPopup):
        '''
        if the poseFolder has a poseHandler.py file see if it has the 'posePopupAdditions' func
        and if so, use that to extend the standard menu's
        '''
        poseHandler = r9Pose.getFolderPoseHandler(self.getPoseDir())
        if poseHandler:
            import imp
            import inspect
            print 'Adding to menus From PoseHandler File!!!!'
            tempPoseFuncs = imp.load_source(poseHandler.split('.py')[0], os.path.join(self.getPoseDir(), poseHandler))
            if [func for name, func in inspect.getmembers(tempPoseFuncs, inspect.isfunction) if name == 'posePopupAdditions']:
                # NOTE we pass in self so the new additions have the same access as everything else!
                tempPoseFuncs.posePopupAdditions(parentPopup, self)
            del(tempPoseFuncs)

    def _uiCB_setPoseGrid(self, size, *args):
        '''
        Set size of the Thumnails used in the PoseGrid Layout
        '''
        if size == 'small':
            mc.gridLayout(self.cgmUIglPoses, e=True, cwh=(75, 80), nc=4)
        if size == 'medium':
            mc.gridLayout(self.cgmUIglPoses, e=True, cwh=(100, 90), nc=3)
        if size == 'large':
            mc.gridLayout(self.cgmUIglPoses, e=True, cwh=(150, 120), nc=2)
        self._uiCB_fillPoses()
        self._uiCB_selectPose(self.poseSelected)

    def _uiCB_iconGridSelection(self, current=None, *args):
        '''
        Unselect all other iconTextCheckboxes than the currently selected
        without this you would be able to multi-select the thumbs

        .. note:: 
            because we prefix the buttons to get over the issue of non-numeric
            first characters we now need to strip the first character back off
        '''
        for button in mc.gridLayout(self.cgmUIglPoses, q=True, ca=True):
            if current and not button[1:] == current:
                mc.iconTextCheckBox(button, e=True, v=False, bgc=self.poseButtonBGC)
            else:
                mc.iconTextCheckBox(button, e=True, v=True, bgc=self.poseButtonHighLight)
        self.setPoseSelected(current)

    def _uiCB_gridResize(self, *args):
        if r9Setup.mayaVersion() >= 2010:
            cells = (int(mc.scrollLayout(self.cgmUIglPoseScroll, q=True, w=True) / mc.gridLayout(self.cgmUIglPoses, q=True, cw=True))) or 1

            mc.gridLayout(self.cgmUIglPoses, e=True, nc=cells)
        else:
            log.debug('this call FAILS in 2009???')


    # ------------------------------------------------------------------------------
    # Main Pose Function Wrappers ---
    # ------------------------------------------------------------------------------

    def _uiCB_switchPoseMode(self, *args):
        '''
        Toggle PoseField mode between Grid mode and TextScroll
        '''
        if self.poseGridMode == 'thumb':
            self.poseGridMode = 'text'
        else:
            self.poseGridMode = 'thumb'
        self._uiCB_fillPoses()
        self._uiCB_selectPose(self.poseSelected)

    def _uiCB_savePosePath(self, existingText=None):
        '''
        Build the path for the pose to be saved too
        '''
        result = mc.promptDialog(
                title='Pose',
                message='Enter Name:',
                button=['OK', 'Cancel'],
                text=existingText,
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
        if result == 'OK':
            name = mc.promptDialog(query=True, text=True)
            try:
                return os.path.join(self.getPoseDir(), '%s.pose' % r9Core.validateString(name, fix=True))
            except ValueError, error:
                raise ValueError(error)

    def _uiCB_setPoseRootNode(self, specific=None, *args):
        '''
        This changes the mode for the Button that fills in rootPath in the poseUI
        Either fills with the given node, or fill it with the connected MetaRig

        :param specific: passed in directly from the UI calls
        '''
        rootNode = mc.ls(sl=True, l=True)

        def fillTextField(text):
            # bound to a function so it can be passed onto the MetaNoode selector UI
            mc.textFieldButtonGrp(self.cgmUItfgPoseRootNode, e=True, text=text)

        if specific:
            fillTextField(specific)
            if self.poseRootMode == 'MetaRoot':
                if specific != '****  AUTO__RESOLVED  ****':
                    mc.select(r9Meta.MetaClass(specific).ctrl_main)
                else:
                    mc.select(cl=True)
        else:
            if self.poseRootMode == 'RootNode':
                if not rootNode:
                    raise StandardError('Warning nothing selected')
                fillTextField(rootNode[0])
            elif self.poseRootMode == 'MetaRoot':
                if rootNode:
                    # metaRig=r9Meta.getConnectedMetaNodes(rootNode[0])
                    metaRig = r9Meta.getConnectedMetaSystemRoot(rootNode[0])
                    if not metaRig:
                        raise StandardError("Warning selected node isn't connected to a MetaRig node")
                    fillTextField(metaRig.mNode)
                else:
                    metaRigs = r9Meta.getMetaNodes(dataType='mClass')
                    if metaRigs:
                        r9Meta.MClassNodeUI(closeOnSelect=True,
                                            funcOnSelection=fillTextField,
                                            mInstances=['MetaRig'],
                                            allowMulti=False)._showUI()
                    else:
                        raise StandardError("Warning: No MetaRigs found in the Scene")

        # fill the cache up for the ini file
        self.ANIM_UI_OPTVARS['AnimationUI']['poseRoot'] = mc.textFieldButtonGrp(self.cgmUItfgPoseRootNode, q=True, text=True)
        self._uiCache_storeUIElements()

    def _uiCB_managePoseRootMethod(self, *args):
        '''
        Manage the PoseRootNode method, either switch to standard rootNode or MetaNode
        '''

        if mc.checkBox('cgmUIcbMetaRig', q=True, v=True):
            self.poseRootMode = 'MetaRoot'
            mc.textFieldButtonGrp(self.cgmUItfgPoseRootNode, e=True, bl='MetaRoot')
        else:
            self.poseRootMode = 'RootNode'
            mc.textFieldButtonGrp(self.cgmUItfgPoseRootNode, e=True, bl='SetRoot')
        self._uiCache_storeUIElements()

    def _uiCB_getPoseInputNodes(self):
        '''
        Node passed into the __PoseCalls in the UI
        '''
        return MRSANIMUTILS._uiCB_getPoseInputNodes(self)
        
        """
        # posenodes = []
        uiCB_contextualAction(self,**{'mode':'select'})
        _sel = mc.ls(sl=1)
        #pprint.pprint(_sel)        
        
        return _sel"""
        


    def _uiCB_enableRelativeSwitches(self, *args):
        '''
        switch the relative mode on for the poseLaoder
        '''
        self._uiCache_addCheckbox(self.cgmUIcbPoseRelative)
        state = mc.checkBox(self.cgmUIcbPoseRelative, q=True, v=True)
        mc.checkBox(self.cgmUIcbPoseSpace, e=True, en=False)
        mc.checkBox(self.cgmUIcbPoseSpace, e=True, en=state)
        mc.frameLayout(self.cgmUIflPoseRelativeFrame, e=True, en=state)

    def _uiPoseDelete(self, *args):
        if not self.__validatePoseFunc('DeletePose'):
            return
        result = mc.confirmDialog(
                title='Confirm Pose Delete',
                button=['Yes', 'Cancel'],
                message='confirm deletion of pose file: "%s"' % self.poseSelected,
                defaultButton='Yes',
                cancelButton='Cancel',
                dismissString='Cancel')
        if result == 'Yes':
            try:
                os.remove(self.getPosePath())
            except:
                log.info('Failed to Delete PoseFile')
            try:
                os.remove(self.getIconPath())
            except:
                log.info('Failed to Delete PoseIcon')
            self._uiCB_fillPoses(rebuildFileList=True)

    def _uiPoseRename(self, *args):
        if not self.__validatePoseFunc('PoseRename'):
            return
        try:
            newName = self._uiCB_savePosePath(self.getPoseSelected())
        except ValueError, error:
            raise ValueError(error)
        try:
            os.rename(self.getPosePath(), newName)
            os.rename(self.getIconPath(), '%s.bmp' % newName.split('.pose')[0])
        except:
            log.info('Failed to Rename Pose')
        self._uiCB_fillPoses(rebuildFileList=True)
        pose = os.path.basename(newName.split('.pose')[0])
        self._uiCB_selectPose(pose)

    def _uiPoseOpenFile(self, *args):
        import subprocess
        path = os.path.normpath(self.getPosePath())
        subprocess.Popen('notepad "%s"' % path)

    def _uiPoseOpenDir(self, *args):
        import subprocess
        path = os.path.normpath(self.getPoseDir())
        subprocess.Popen('explorer "%s"' % path)

    def _uiPoseUpdate(self, storeThumbnail, *args):
        if not self.__validatePoseFunc('UpdatePose'):
            return
        result = mc.confirmDialog(
                title='PoseUpdate',
                message=('<< Replace & Update Pose file >>\n\n%s' % self.poseSelected),
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
        if result == 'OK':
            if storeThumbnail:
                try:
                    os.remove(self.getIconPath())
                except:
                    log.debug('unable to delete the Pose Icon file')
            self.__PoseSave(self.getPosePath(), storeThumbnail)
            self._uiCB_selectPose(self.poseSelected)

    def _uiPoseUpdateThumb(self, *args):
        sel = mc.ls(sl=True, l=True)
        mc.select(cl=True)
        thumbPath = self.getIconPath()
        if os.path.exists(thumbPath):
            try:
                os.remove(thumbPath)
            except:
                log.error('Unable to delete the Pose Icon file')
        r9General.thumbNailScreen(thumbPath, 128, 128)
        if sel:
            mc.select(sel)
        self._uiCB_fillPoses()
        self._uiCB_selectPose(self.poseSelected)

    def _uiPoseSelectObjects(self, *args):
        '''
        Select matching internal nodes
        '''
        rootNode = mc.textFieldButtonGrp(self.cgmUItfgPoseRootNode, q=True, text=True)
        if rootNode and mc.objExists(rootNode):
            self._uiPresetFillFilter()  # fill the filterSettings Object
            pose = r9Pose.PoseData(self.filterSettings)
            pose._readPose(self.getPosePath())
            nodes = pose.matchInternalPoseObjects(rootNode)
            if nodes:
                mc.select(cl=True)
                [mc.select(node, add=True) for node in nodes]
        else:
            raise StandardError('RootNode not Set for Hierarchy Processing')

    def _uiPoseMakeSubFolder(self, handlerFile=None, *args):
        '''
        Insert a new SubFolder to the posePath, makes the dir and sets
        it up in the UI to be the current active path
        '''
        basePath = self.cgmUIField_posePath.getValue()
        if not os.path.exists(basePath):
            raise StandardError('Base Pose Path is inValid or not yet set')
        promptstring = 'New Pose Folder Name'
        if handlerFile:
            promptstring = 'New %s POSE Folder Name' % os.path.basename(handlerFile).replace('_poseHandler.py', '').upper()
        result = mc.promptDialog(
                title=promptstring,
                message='Enter Name:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
        if result == 'OK':
            subFolder = mc.promptDialog(query=True, text=True)
            self.cgmUIField_subPath.setValue(subFolder)
            #mc.textFieldButtonGrp('cgmUItfgPoseSubPath', edit=True, text=subFolder)
            self.posePath = os.path.join(basePath, subFolder)
            os.mkdir(self.posePath)
            if handlerFile and os.path.exists(handlerFile):
                shutil.copy(handlerFile, self.posePath)
            self._uiCB_pathSwitchInternals()

    def _uiPoseCopyToProject(self, *args):
        '''
        Copy local pose to the Project Pose Folder
        TODO: have a way to let the user select the ProjectSubfolder the
        pose gets copied down too
        '''
        import shutil
        syncSubFolder = True
        projectPath = self.posePathProject
        localPath = self.posePathLocal
        
        if not os.path.exists(self.posePathProject):
            raise StandardError('Project Pose Path is inValid or not yet set')
        
        
        
        if syncSubFolder:
            subFolder = self.getPoseSubFolder()
            projectPath = os.path.join(projectPath, subFolder)

            if not os.path.exists(projectPath):
                result = mc.confirmDialog(
                    title='Add Project Sub Folder',
                    message='Add a matching subFolder to the project pose path?',
                    button=['Make', 'CopyToRoot', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')
                if result == 'Make':
                    try:
                        os.mkdir(projectPath)
                        log.debug('New Folder Added to ProjectPosePath: %s' % projectPath)
                    except:
                        raise StandardError('Failed to make the SubFolder path')
                elif result == 'CopyToRoot':
                    projectPath = self.posePathProject
                else:
                    return

        log.info('Copying Local Pose: %s >> %s' % (self.poseSelected, projectPath))
        try:
            shutil.copy2(self.getPosePath(), projectPath)
            shutil.copy2(self.getIconPath(), projectPath)
        except Exception,err:
            print ('Unable to copy pose : %s > to Project dirctory' % self.poseSelected)
            
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    def _uiPoseAddPoseHandler(self, *args):
        '''
        PRO_PACK : Copy local pose to the Project Pose Folder
        '''
        r9Setup.PRO_PACK_STUBS().AnimationUI_stubs.cgmUICB_poseAddPoseHandler(self.posePath)
        
    # ------------------------------------------------------------------------------
    # UI Elements ConfigStore Callbacks ---
    # ------------------------------------------------------------------------------

    def _uiCache_storeUIElements(self, *args):
        '''
        Store some of the main components of the UI out to an ini file
        '''
        return
        if not self.cgmUIBoot:
            log.debug('cgmUI configFile being written')
            ConfigObj = configobj.ConfigObj(indent_type='\t')
            self._uiPresetFillFilter()  # fill the internal filterSettings obj
            self.ANIM_UI_OPTVARS['AnimationUI']['cgmUI_docked'] = self.dock
            ConfigObj['filterNode_settings'] = self.filterSettings.__dict__
            ConfigObj['AnimationUI'] = self.ANIM_UI_OPTVARS['AnimationUI']
            ConfigObj.filename = self.cgmUI_optVarConfig
            ConfigObj.write()

    def _uiCache_loadUIElements(self):
        '''
        Restore the main UI elements from the ini file
        '''
        log.debug('CALLING: _uiCache_loadUIElements')
        return 
        self.cgmUIBoot = True  # is the UI being booted
        try:
            log.debug('Loading UI Elements from the config file')

            def _uiCache_LoadCheckboxes():
                if 'checkboxes' in self.ANIM_UI_OPTVARS['AnimationUI'] and \
                            self.ANIM_UI_OPTVARS['AnimationUI']['checkboxes']:
                    for cb, status in self.ANIM_UI_OPTVARS['AnimationUI']['checkboxes'].items():
                        try:
                            mc.checkBox(cb, e=True, v=r9Core.decodeString(status))
                        except:
                            print 'given checkbox no longer exists : %s' % cb

            AnimationUI = self.ANIM_UI_OPTVARS['AnimationUI']

            if self.basePreset:
                try:
                    mc.textScrollList(self.cgmUItslPresets, e=True, si=self.basePreset)
                    self._uiPresetSelection(Read=True)
                except:
                    log.debug('given basePreset not found')
            if 'filterNode_preset' in AnimationUI and AnimationUI['filterNode_preset']:
                mc.textScrollList(self.cgmUItslPresets, e=True, si=AnimationUI['filterNode_preset'])
                self._uiPresetSelection(Read=True)  # ##not sure on this yet????
            if 'keyPasteMethod' in AnimationUI and AnimationUI['keyPasteMethod']:
                mc.optionMenu('om_PasteMethod', e=True, v=AnimationUI['keyPasteMethod'])
            if 'matchMethod' in AnimationUI and AnimationUI['matchMethod']:
                mc.optionMenu('om_MatchMethod', e=True, v=AnimationUI['matchMethod'])
            if 'poseMode' in AnimationUI and AnimationUI['poseMode']:
                self.poseGridMode = AnimationUI['poseMode']
            if 'posePathMode' in AnimationUI and AnimationUI['posePathMode']:
                self.posePathMode = AnimationUI['posePathMode']
            if 'posePathLocal' in AnimationUI and AnimationUI['posePathLocal']:
                self.posePathLocal = AnimationUI['posePathLocal']
            if 'posePathProject' in AnimationUI and AnimationUI['posePathProject']:
                self.posePathProject = AnimationUI['posePathProject']
            if 'poseSubPath' in AnimationUI and AnimationUI['poseSubPath']:
                #mc.textFieldButtonGrp('cgmUItfgPoseSubPath', edit=True, text=AnimationUI['poseSubPath'])
                self.cgmUIField_subPath.setValue(AnimationUI['poseSubPath'])
            if 'poseRoot' in AnimationUI and AnimationUI['poseRoot']:
                if mc.objExists(AnimationUI['poseRoot']) or AnimationUI['poseRoot'] == '****  AUTO__RESOLVED  ****':
                    mc.textFieldButtonGrp(self.cgmUItfgPoseRootNode, e=True, text=AnimationUI['poseRoot'])

            _uiCache_LoadCheckboxes()

            # callbacks
            if self.posePathMode:
                print 'setting : ', self.posePathMode
                mc.radioCollection(self.cgmUIrcbPosePathMethod, edit=True, select=self.posePathMode)
            self._uiCB_enableRelativeSwitches()  # relativePose switch enables
            self._uiCB_managePoseRootMethod()  # metaRig or SetRootNode for Pose Root
            self._uiCB_switchPosePathMode(self.posePathMode)  # pose Mode - 'local' or 'project'
            self._uiCB_manageSnapHierachy()  # preCopyAttrs
            self._uiCB_manageSnapTime()  # preCopyKeys
            self._uiCB_manageTimeOffsetState()


        except StandardError, err:
            log.debug('failed to complete UIConfig load')
            log.warning(err)
        finally:
            self.cgmUIBoot = False

    def _uiCache_readUIElements(self):
        '''
        read the config ini file for the initial state of the ui
        '''
        try:
            if os.path.exists(self.cgmUI_optVarConfig):
                self.filterSettings.read(self.cgmUI_optVarConfig)  # use the generic reader for this
                self.ANIM_UI_OPTVARS['AnimationUI'] = configobj.ConfigObj(self.cgmUI_optVarConfig)['AnimationUI']
            else:
                self.ANIM_UI_OPTVARS['AnimationUI'] = {}
        except:
            pass

    def _uiCache_addCheckbox(self, checkbox):
        '''
        Now shifted into a sub dic for easier processing
        '''
        if 'checkboxes' not in self.ANIM_UI_OPTVARS['AnimationUI']:
            self.ANIM_UI_OPTVARS['AnimationUI']['checkboxes'] = {}
        self.ANIM_UI_OPTVARS['AnimationUI']['checkboxes'][checkbox] = mc.checkBox(checkbox, q=True, v=True)
        self._uiCache_storeUIElements()

    def _uiCache_resetDefaults(self, *args):
        defaultConfig = os.path.join(self.presetDir, '__red9animreset__')
        if os.path.exists(defaultConfig):
            self.ANIM_UI_OPTVARS['AnimationUI'] = configobj.ConfigObj(defaultConfig)['AnimationUI']
            self._uiCache_loadUIElements()
            
    def _uiCall(self, func, *args):
        '''
        MAIN ANIMATION UI CALL
        Why not just call the procs directly? well this also manages the collection /pushing
        of the filterSettings data for all procs
        '''
        
        # issue : up to v2011 Maya puts each action into the UndoQueue separately
        # when called by lambda or partial - Fix is to open an UndoChunk to catch
        # everything in one block
        objs = mc.ls(sl=True, l=True)
        self.kws = {}
        self.metaRig = None
        # If below 2011 then we need to store the undo in a chunk
        if r9Setup.mayaVersion() < 2011:
            mc.undoInfo(openChunk=True)
    
        # Main Hierarchy Filters =============
        self._uiPresetFillFilter()  # fill the filterSettings Object
        self.matchMethod = 'stripPrefix'#mc.optionMenu('om_MatchMethod', q=True, v=True)
    
        # self.filterSettings.transformClamp = True
    
        try:
            if func == 'CopyAttrs':
                self.__CopyAttrs()
            elif func == 'CopyKeys':
                self.__CopyKeys()
            elif func == 'Snap':
                self.__Snap()
            elif func == 'StabilizeFwd':
                self.__Stabilize('fwd')
            elif func == 'StabilizeBack':
                self.__Stabilize('back')
            elif func == 'TimeOffset':
                self.__TimeOffset()
            elif func == 'HierarchyTest':
                self.__Hierarchy()
            elif func == 'PoseSave':
                self.__PoseSave()
            elif func == 'PoseLoad':
                self.__PoseLoad()
            elif func == 'PoseCompareSkelDict':
                self.__PoseCompare(compareDict='skeletonDict')
            elif func == 'PoseComparePoseDict':
                self.__PoseCompare(compareDict='poseDict')
            elif func == 'PosePC_Make':
                self.__PosePointCloud('make')
            elif func == 'PosePC_Delete':
                self.__PosePointCloud('delete')
            elif func == 'PosePC_Snap':
                self.__PosePointCloud('snap')
            elif func == 'PosePC_Update':
                self.__PosePointCloud('update')
            elif func == 'PoseBlender':
                self.__PoseBlend()
            elif func == 'MirrorAnim':
                self.__MirrorPoseAnim('mirror', 'Anim')
            elif func == 'MirrorPose':
                self.__MirrorPoseAnim('mirror', 'Pose')
            elif func == 'SymmetryPose':
                self.__MirrorPoseAnim('symmetry', 'Pose')
            elif func == 'SymmetryAnim':
                self.__MirrorPoseAnim('symmetry', 'Anim')
    
        except r9Setup.ProPack_Error:
            log.warning('ProPack not Available')
        except Exception, error:
            cgmGEN.cgmExceptCB(Exception,error,msg=vars())
            
        if objs and not func == 'HierarchyTest':
            mc.select(objs)
        # close chunk
        if mel.eval('getApplicationVersionAsFloat') < 2011:
            mc.undoInfo(closeChunk=True)
    
        #self._uiCache_storeUIElements()
        
    def __PoseSave(self, path=None, storeThumbnail=True):
        '''
        Internal UI call for PoseLibrary Save func, note that filterSettings is bound
        but only filled by the main _uiCall call
        '''
        try:
            # test the code behaviour under Project mode
            if not self.__validatePoseFunc('PoseSave'):
                return
            if not path:
                try:
                    path = self._uiCB_savePosePath()
                except Exception, error:
                    raise Exception(error)
    
            poseHierarchy = False#mc.checkBox(self.cgmUIcbPoseHierarchy, q=True, v=True)
    
    #         #Work to hook the poseSave directly to the metaRig.poseCacheStore func directly
    #         if self.filterSettings.metaRig and r9Meta.isMetaNodeInherited(self._uiCB_getPoseInputNodes(),
    #                                                                       mInstances=r9Meta.MetaRig):
    #             print 'active MetaNode, calling poseCacheSave from metaRig subclass'
    #             r9Meta.MetaClass(self._uiCB_getPoseInputNodes()).poseCacheStore(filepath=path,
    #                                                                              storeThumbnail=storeThumbnail)
    #         else:
            r9Pose.PoseData(self.filterSettings).poseSave(self._uiCB_getPoseInputNodes(),
                                                          path,
                                                          useFilter=poseHierarchy,
                                                          storeThumbnail=storeThumbnail)
            log.info('Pose Stored to : %s' % path)
            self._uiCB_fillPoses(rebuildFileList=True)
        except Exception,error:
            raise cgmGEN.cgmExceptCB(Exception,error,msg=vars())
        
    def get_poseNodes(self,select=False):
        nodes = self._uiCB_getPoseInputNodes()
        log.info("Initial nodes: {0}".format(nodes))
        l_start = []
        if not nodes:
            log.debug("No nodes found.Checking pose file to build list...")
            path = self.getPosePath()
            log.debug('PosePath : %s' % path)
            #poseNode = r9Pose.PoseData(self.filterSettings)
            #poseNode.prioritySnapOnly = mc.checkBox(self.cgmUIcbSnapPriorityOnly, q=True, v=True)
            #poseNode.matchMethod = self.matchMethod
            
            d = configobj.ConfigObj(path)['poseData']
            nodes=[]
            l_start = []
            for k in d.keys():
                k_dat = d[k]
                _longName = k_dat['longName']
                _longmatch = _longName.split(':')[-1]
                _longmatch = NAMES.clean(_longmatch)
                l_start.append(k)
                buff_ref = mc.ls("*:{0}".format(_longmatch))
                buf_reg = mc.ls("*{0}".format(_longmatch))
                if buff_ref and len(buff_ref) == 1:
                    log.debug("Ref ls match for for {0}".format(_longmatch))
                    nodes.append(buff_ref[0])
                    continue
                if buf_reg and len(buf_reg) == 1:
                    log.debug("Reg ls match for for {0}".format(_longmatch))
                    nodes.append(buf_reg[0])
                    continue
                elif mc.objExists(_longmatch):
                    log.debug("Exists: {0}".format(_longmatch))
                    nodes.append(_longmatch)
                    continue
                elif mc.objExists(_longName):
                    log.debug("Exists: {0}".format(_longName))
                    nodes.append(_longName)
                    continue
                
                log.debug("No match for for {0}".format(_longName))
            
        if select:
            mc.select(nodes)
        #pprint.pprint(l_start)
        return nodes
                
                        
    def __PoseLoad(self):
        '''
        Internal UI call for PoseLibrary Load func, note that filterSettings is bound
        but only filled by the main _uiCall call
        '''
        """
        poseHierarchy = mc.checkBox(self.cgmUIcbPoseHierarchy, q=True, v=True)
        poseRelative = mc.checkBox(self.cgmUIcbPoseRelative, q=True, v=True)
        maintainSpaces = mc.checkBox(self.cgmUIcbPoseSpace, q=True, v=True)
        rotRelMethod = mc.radioCollection(self.cgmUIrcbPoseRotMethod, q=True, select=True)
        tranRelMethod = mc.radioCollection(self.cgmUIrcbPoseTranMethod, q=True, select=True)

        if poseRelative and not mc.ls(sl=True, l=True):
            log.warning('No node selected to use for reference!!')
            return

        relativeRots = 'projected'
        relativeTrans = 'projected'
        if not rotRelMethod == 'rotProjected':
            relativeRots = 'absolute'
        if not tranRelMethod == 'tranProjected':
            relativeTrans = 'absolute'
        """
        _sel = mc.ls(sl=1)
        
        path = self.getPosePath()
        log.info('PosePath : %s' % path)
        poseNode = r9Pose.PoseData(self.filterSettings)
        #poseNode.prioritySnapOnly = mc.checkBox(self.cgmUIcbSnapPriorityOnly, q=True, v=True)
        poseNode.matchMethod = self.var_poseMatchMethod.value#self.matchMethod

        nodes = self.get_poseNodes()

        poseNode.poseLoad(nodes,
                          path,
                          useFilter=False,#poseHierarchy,
                          relativePose=False,#poseRelative,
                          relativeRots='projected',#relativeRots,
                          relativeTrans='projected',#relativeTrans,
                          maintainSpaces=False)#maintainSpaces)
        
        if _sel:
            mc.select(_sel)
        else:mc.select(cl=1)

    def __PoseCompare(self, compareDict='skeletonDict', *args):
        '''
        PRO_PACK : Internal UI call for Pose Compare func, note that filterSettings is bound
        but only filled by the main _uiCall call
        '''
        r9Setup.PRO_PACK_STUBS().AnimationUI_stubs.cgmUICB_poseCompare(filterSettings=self.filterSettings,
                                                                    nodes=self._uiCB_getPoseInputNodes(),
                                                                    posePath=self.getPosePath(),
                                                                    compareDict=compareDict)

    def _PoseBlend(self):
        '''
        TODO: allow this ui and implementation to blend multiple poses at the same time
        basically we'd add a new poseObject per pose and bind each one top the slider
        but with a consistent poseCurrentCache via the _cacheCurrentNodeStates() call
        '''

        pb = r9Pose.PoseBlender(filepaths=[self.getPosePath()],
                                nodes = self.get_poseNodes(),
                                filterSettings=self.filterSettings,
                                useFilter=False)#mc.checkBox(self.cgmUIcbPoseHierarchy, q=True, v=True),
                                #matchMethod=self.matchMethod)
        pb.show()
        
        

    def _uiPresetFillFilter(self):
        '''
        Fill the internal filterSettings Object for the AnimationUI class calls
        Note we reset but leave the rigData cached as it's not all represented
        by the UI, some is cached only when the filter is read in
        '''
        log.debug("CALLING _uiPresetFillFilter ")
        self.filterSettings.resetFilters(rigData=False)
        self.filterSettings.transformClamp = True
        
        """
        if mc.textFieldGrp('cgmUItfgSpecificNodeTypes', q=True, text=True):
            self.filterSettings.nodeTypes = (mc.textFieldGrp('cgmUItfgSpecificNodeTypes', q=True, text=True)).split(',')
        if mc.textFieldGrp('cgmUItfgSpecificAttrs', q=True, text=True):
            self.filterSettings.searchAttrs = (mc.textFieldGrp('cgmUItfgSpecificAttrs', q=True, text=True)).split(',')
        if mc.textFieldGrp('cgmUItfgSpecificPattern', q=True, text=True):
            self.filterSettings.searchPattern = (mc.textFieldGrp('cgmUItfgSpecificPattern', q=True, text=True)).split(',')
        if mc.textScrollList('cgmUItslFilterPriority', q=True, ai=True):
            self.filterSettings.filterPriority = mc.textScrollList('cgmUItslFilterPriority', q=True, ai=True)
    
        self.filterSettings.metaRig = mc.checkBox(self.cgmUIcbMetaRig, q=True, v=True)
        self.filterSettings.incRoots = mc.checkBox(self.cgmUIcbIncRoots, q=True, v=True)
        """
        # If the above filters are blank, then the code switches to full hierarchy mode
        if not self.filterSettings.filterIsActive():
            self.filterSettings.hierarchy = True
    
        # this is kind of against the filterSettings Idea, shoe horned in here
        # as it makes sense from the UI standpoint
        #self.filterSettings.rigData['snapPriority'] = mc.checkBox(self.cgmUIcbSnapPriorityOnly, q=True, v=True)
        
    def _uiElementBinding(self):
        '''
        this is GASH! rather than have each ui element cast itself to the object as we used to do, 
        we're now manually setting up those name maps to by-pass the way we have to call the UI in 
        2017 via the workspace.... Maybe I'm missing something in the workspace setup but don't think so.
        Must see if there's a way of binding to the class object as you'd expect :(
        '''
        self.cgmUItabMain = 'cgmUItabMain'

        # CopyAttributes
        # ====================
        self.cgmUIcbCAttrHierarchy = 'cgmUIcbCAttrHierarchy'
        self.cgmUIcbCAttrToMany = 'cgmUIcbCAttrToMany'
        self.cgmUIcbCAttrChnAttrs = 'cgmUIcbCAttrChnAttrs'

        # CopyKeys
        # ====================
        self.cgmUIcbCKeyHierarchy = 'cgmUIcbCKeyHierarchy'
        self.cgmUIcbCKeyToMany = 'cgmUIcbCKeyToMany'
        self.cgmUIcbCKeyChnAttrs = 'cgmUIcbCKeyChnAttrs'
        self.cgmUIcbCKeyRange = 'cgmUIcbCKeyRange'
        self.cgmUIcbCKeyAnimLay = 'cgmUIcbCKeyAnimLay'
        self.cgmUIffgCKeyStep = 'cgmUIffgCKeyStep'

        # SnapTransforms
        # ====================
        self.cgmUIcbSnapRange = 'cgmUIcbSnapRange'
        self.cgmUIcbSnapTrans = 'cgmUIcbSnapTrans'
        self.cgmUIcbSnapPreCopyKeys = 'cgmUIcbSnapPreCopyKeys'
        self.cgmUIifgSnapStep = 'cgmUIifgSnapStep'
        self.cgmUIcbSnapHierarchy = 'cgmUIcbSnapHierarchy'
        self.cgmUIcbStapRots = 'cgmUIcbStapRots'
        self.cgmUIcbSnapPreCopyAttrs = 'cgmUIcbSnapPreCopyAttrs'
        self.cgmUIifSnapIterations = 'cgmUIifSnapIterations'

        # Stabilizer
        # ====================
        self.cgmUIcbStabRange = 'cgmUIcbStabRange'
        self.cgmUIcbStabTrans = 'cgmUIcbStabTrans'
        self.cgmUIcbStabRots = 'cgmUIcbStabRots'
        self.cgmUIffgStabStep = 'cgmUIffgStabStep'

        # TimeOffset
        # ====================
        self.cgmUIcbTimeOffsetHierarchy = 'cgmUIcbTimeOffsetHierarchy'
        self.cgmUIcbTimeOffsetScene = 'cgmUIcbTimeOffsetScene'
        self.cgmUIcbTimeOffsetPlayback = 'cgmUIcbTimeOffsetPlayback'
        self.cgmUIcbTimeOffsetRange = 'cgmUIcbTimeOffsetRange'
        self.cgmUIcbTimeOffsetFlocking = 'cgmUIcbTimeOffsetFlocking'
        self.cgmUIcbTimeOffsetRandom = 'cgmUIcbTimeOffsetRandom'
        self.cgmUIcbTimeOffsetRipple = 'cgmUIcbTimeOffsetRipple'
        self.cgmUIcbTimeOffsetStartfrm = 'cgmUIcbTimeOffsetStartfrm'
        self.cgmUIffgTimeOffset = 'cgmUIffgTimeOffset'
        self.cgmUIbtnTimeOffset = 'cgmUIbtnTimeOffset'

        self.cgmUIcbMirrorHierarchy = 'cgmUIcbMirrorHierarchy'

        # Hierarchy Controls
        # =====================
        self.cgmUIclHierarchyFilters = 'cgmUIclHierarchyFilters'
        self.cgmUIcbMetaRig = 'cgmUIcbMetaRig'
        self.cgmUItfgSpecificNodeTypes = 'cgmUItfgSpecificNodeTypes'
        self.cgmUItfgSpecificAttrs = 'cgmUItfgSpecificAttrs'
        self.cgmUItfgSpecificPattern = 'cgmUItfgSpecificPattern'
        self.cgmUItslFilterPriority = 'cgmUItslFilterPriority'
        self.cgmUIcbSnapPriorityOnly = 'cgmUIcbSnapPriorityOnly'
        self.cgmUItslPresets = 'cgmUItslPresets'
        self.cgmUIcbIncRoots = 'cgmUIcbIncRoots'

        # Pose Saver Tab
        # ===============
        self.cgmUItfgPosePath = 'cgmUItfgPosePath'
        self.cgmUIrcbPosePathMethod = 'posePathMode'
        self.posePopupGrid = 'posePopupGrid'

        # SubFolder Scroller
        #=====================
        self.cgmUItslPoseSubFolders = 'cgmUItslPoseSubFolders'

        # Main PoseFields
        # =====================
        self.tfPoseSearchFilter = 'tfPoseSearchFilter'
        self.cgmUItslPoses = 'cgmUItslPoses'
        self.cgmUIglPoseScroll = 'cgmUIglPoseScroll'
        self.cgmUIglPoses = 'cgmUIglPoses'
        self.cgmUIcbPoseHierarchy = 'cgmUIcbPoseHierarchy'
        self.cgmUItfgPoseRootNode = 'cgmUItfgPoseRootNode'
        self.cgmUIcbPoseRelative = 'cgmUIcbPoseRelative'
        self.cgmUIcbPoseSpace = 'cgmUIcbPoseSpace'
        self.cgmUIflPoseRelativeFrame = 'PoseRelativeFrame'
        self.cgmUIrcbPoseRotMethod = 'relativeRotate'
        self.cgmUIrcbPoseTranMethod = 'relativeTranslate'



def buildTab_poses(self,parent):
  
    #_column = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
    _column = mUI.MelColumn(parent,useTemplate = 'cgmUITemplate') 
    
    parent(edit = True,
           af = [(_column,"top",0),
                 (_column,"left",0),
                 (_column,"right",0),                        
                 (_column,"bottom",0)])
    
    #_context = MRSANIMUTILS.uiColumn_context(self,_column,header=True)

    _manager = POSEMANAGER.manager(parent = _column)
    self.mPoseManager = _manager
    for k in self.__dict__.keys():
        if str(k).startswith('var_'):
            self.mPoseManager.__dict__[k] = self.__dict__[k]
    
    return _column 

def buildTab_mrs(self,parent):
    _column = mUI.MelColumn(parent,useTemplate = 'cgmUITemplate') 
    
    _context = MRSANIMUTILS.uiColumn_context(self,_column,header=True)
    
    """
    #>>>Context set -------------------------------------------------------------------------------    
    _column = mUI.MelColumn(parent,useTemplate = 'cgmUITemplate') 
    
    _rowContext = mUI.MelHLayout(_column,ut='cgmUISubTemplate',padding=10)
    
    #mUI.MelSpacer(_row,w=1)                      
    #mUI.MelLabel(_row,l='Context: ')
    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    uiRC = mUI.MelRadioCollection()
    
    mVar = self.var_mrsContext_mode
    _on = mVar.value

    for i,item in enumerate(_l_contexts):
        if item == _on:
            _rb = True
        else:_rb = False
        _label = str(_d_contexts[item].get('short',item))
        uiRC.createButton(_rowContext,label=_label,sl=_rb,
                          ann = "Set context: {0}".format(item),
                          onCommand = self.mmCallback(mVar.setValue,item))

        #mUI.MelSpacer(_row,w=1)       
    _rowContext.layout() 
    
    
    #>>>Context Options -------------------------------------------------------------------------------
    _rowContextSub = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
    _d = {'children':'chldrn',
          'siblings':'sblg',
          'mirror':'mrr'}
    
    mUI.MelSpacer(_rowContextSub,w=5)                          
    mUI.MelLabel(_rowContextSub,l='Options:')
    _rowContextSub.setStretchWidget( mUI.MelSeparator(_rowContextSub) )
    
    _d_defaults = {}
    _l_order = ['core','children','siblings','mirror']
    self._dCB_contextOptions = {}
    for k in _l_order:
        _plug = 'cgmVar_mrsContext_' + k
        try:self.__dict__[_plug]
        except:
            _default = _d_defaults.get(k,0)
            #log.debug("{0}:{1}".format(_plug,_default))
            self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = _default)

        l = _d.get(k,k)
        
        _cb = mUI.MelCheckBox(_rowContextSub,label=l,
                              annotation = 'Include {0} in context.'.format(k),
                              value = self.__dict__[_plug].value,
                              onCommand = self.mmCallback(self.__dict__[_plug].setValue,1),
                              offCommand = self.mmCallback(self.__dict__[_plug].setValue,0))
        self._dCB_contextOptions[k] = _cb
        
    mUI.MelSpacer(_rowContextSub,w=5)                      
        
    _rowContextSub.layout()
    """

    buildFrame_mrsTimeContext(self,_column)                
    
    
    #Column below =================================================================
    _columnBelow = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
    
    mc.setParent(_columnBelow)
    buildFrame_mrsList(self,_columnBelow)    
    buildFrame_mrsAnim(self,_columnBelow)
    buildFrame_poses(self,_columnBelow)    
    buildFrame_mrsTween(self,_columnBelow)
    buildFrame_mrsHold(self,_columnBelow)        
    buildFrame_mrsMirror(self,_columnBelow)
    buildFrame_mrsSwitch(self,_columnBelow)
    #buildFrame_mrsSettings(self,_columnBelow)
    
    
    parent(edit = True,
           af = [(_column,"top",0),
                 (_column,"left",0),
                 (_column,"right",0),            
                 (_columnBelow,"left",0),
                 (_columnBelow,"right",0),
                 (_columnBelow,"bottom",0)],
           ac = [(_columnBelow,"top",0,_column),
                 ],)
    
    return _column

#@cgmGEN.Timer
def get_contextTimeDat(self,mirrorQuery=False,**kws):
    try:        
        _str_func='get_contextTimeDat'
        log.debug(cgmGEN.logString_start(_str_func))
        _res = {}
        self.mDat.d_context['partControls'] = {}
        log.debug(cgmGEN.logString_sub(_str_func,'Get controls'))
        
        
        _context = kws.get('context') or self.var_mrsContext_mode.value
        _contextTime = kws.get('contextTime') or self.var_mrsContext_time.value
        _contextKeys = kws.get('contextKeys') or self.var_mrsContext_keys.value
        _frame = SEARCH.get_time('current')
        self.mDat.d_context['frameInitial'] = _frame
        
        if _contextTime == 'selected':
            if not SEARCH.get_time('selected'):
                #log.error("Time Context: selected | No time selected.")
                return False,"Time Context: selected | No time selected."
            
        if _context in ['puppet','scene'] and _contextTime in ['bookEnd']:
            log.error("Unsupported context/time combo (bad mojo!) | context:{0} | contextTime:{1}".format(_context,_contextTime))
            return False,"Unsupported context/time combo (bad mojo!) | context:{0} | contextTime:{1}".format(_context,_contextTime)            
        
        
        log.debug("|{0}| >> context: {1} | {2} - {3} | {4}".format(_str_func,_context,_contextKeys,_contextTime, ' | '.join(kws)))
        
        #First cather our controls
        _keys = kws.keys()
        if 'children' in _keys:
            b_children = kws.get('children')
        else:
            b_children = bool(self.var_mrsContext_children.value)
        
        if 'siblings' in _keys:
            b_siblings = kws.get('siblings')
        else:
            b_siblings = bool(self.var_mrsContext_siblings.value)
            
        if 'mirror' in _keys:
            b_mirror = kws.get('mirror')
        else:
            b_mirror = bool(self.var_mrsContext_mirror.value)
            
        if _context == 'control' and b_siblings:
            if b_mirror:
                log.warning("Context control + siblings = part mode")
                _context = 'part'
                b_siblings = False
                
        if _context == 'puppet' and b_siblings:
            log.warning("Context puppet + siblings = scene mode")
            _context = 'scene'
            
            
        
        def addSourceControls(self,mObj,controls):
            if not self.mDat.d_context['partControls'].get(mObj):
                log.debug("New partControl list: {0}".format(mObj))
                self.mDat.d_context['partControls'][mObj] = []
            
            _l = self.mDat.d_context['partControls'][mObj]
            for c in controls:
                if c not in _l:
                    #log.debug("New control: {0}".format(c))                    
                    _l.append(c)
            self.mDat.d_context['partControls'][mObj] = _l            
                
        
        if _context != 'control':
            log.debug("|{0}| >> Reaquiring control list...".format(_str_func))
            ls = []

            if self.mDat.d_context['b_puppetPart']:
                log.info("|{0}| >> puppetPart mode...".format(_str_func))
                for mPuppet in self.mDat.d_context['mPuppets']:
                    _l = [mObj.mNode for mObj in mPuppet.UTILS.controls_get(mPuppet)]
                    ls.extend(_l)
                    addSourceControls(self,mPuppet,_l)
            
            if _context == 'part':
                if mirrorQuery:
                    for mPart in self.mDat.d_context['mModules']:
                        _l = [mObj.mNode for mObj in mPart.UTILS.controls_get(mPart,'mirror')]
                        ls.extend(_l)
                        addSourceControls(self,mPart,_l)
 
                else:
                    for mPart in self.mDat.d_context['mModules']:
                        _l = mPart.rigNull.moduleSet.getList()
                        ls.extend(_l)
                        addSourceControls(self,mPart,_l)
                        
            elif _context in ['puppet','scene']:
                if mirrorQuery:
                    for mPuppet in self.mDat.d_context['mPuppets']:
                        addSourceControls(self,mPuppet,
                                          [mObj.mNode for mObj in mPuppet.UTILS.controls_get(mPuppet)])
                        
                        for mPart in mPuppet.UTILS.modules_get(mPuppet):
                            _l = [mObj.mNode for mObj in mPart.UTILS.controls_get(mPart,'mirror')]
                            ls.extend(_l)
                            addSourceControls(self,mPart,_l)
                            
                else:
                    for mPuppet in self.mDat.d_context['mPuppets']:
                        _l =  [mObj.mNode for mObj in mPuppet.UTILS.controls_get(mPuppet)]
                        addSourceControls(self,mPuppet,_l)
                        ls.extend(_l)
                        
                        for mPart in mPuppet.UTILS.modules_get(mPuppet):
                            #_l = [mObj.mNode for mObj in mPart.UTILS.controls_get(mPart)]
                            _l = mPart.rigNull.moduleSet.getList()
                            ls.extend(_l)
                            addSourceControls(self,mPart,_l)
                            
                        #mPuppet.puppetSet.select()
                        #ls.extend(mc.ls(sl=True))
                    
            self.mDat.d_context['sControls'] = ls
        else:
            self.mDat.d_context['sControls'] = [mObj.mNode for mObj in self.mDat.d_context['mControls']]
            self.mDat.d_context['partControls']['control'] = self.mDat.d_context['sControls']
 
        self.mDat.d_context['sControls'] = LISTS.get_noDuplicates(self.mDat.d_context['sControls'])
        self.mDat.d_context['mControls'] = cgmMeta.validateObjListArg(self.mDat.d_context['sControls'])
        
        #================================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'Find keys'))
        self.l_sources = []
        
        def addSource(self,mObj,key,res):
            if not _res.get(key):
                log.debug("New frame: {0}".format(key))                
                res[key]=[]
            
            _l = res[key]
            if mObj not in _l:
                _l.append(mObj)
            if mObj not in self.l_sources:
                self.l_sources.append(mObj)
                
            res[key] = _l
            
        if _contextTime == 'current':
            _controls = self.mDat.d_context['sControls']
            _res[_frame] = _controls
        else:
            if _context == 'control':
                for mObj in self.mDat.d_context['mControls']:
                    _keys = SEARCH.get_key_indices_from( mObj.mNode,mode = _contextTime)
                    if _keys:
                        log.debug("{0} | {1}".format(mObj.p_nameShort,_keys))
                        for k in _keys:
                            addSource(self,mObj,k,_res)
            elif _context in ['part','puppet','scene']:
                d_tmp = {}
                l_keys = []
                #First pass we collect all the keys...
                for mPart,controls in self.mDat.d_context['partControls'].iteritems():
                    d_tmp[mPart] = []
                    _l = d_tmp[mPart]
                    for c in controls:
                        _keys = SEARCH.get_key_indices_from( c,mode = _contextTime)
                        if _keys:
                            log.debug("{0} | {1}".format(c,_keys))
                            for k in _keys:
                                #addSource(self,mPart,k,_res)
                                if k not in d_tmp[mPart]:d_tmp[mPart].append(k)
                                if k not in l_keys:l_keys.append(k)
                #Second pass we do any special processing in case a given set of controls gives us more data that we want...                
                if _context in ['part']:
                    if _contextTime in ['next','previous']:
                        log.debug(cgmGEN.logString_sub(_str_func,'Second pass | {0}'.format(_contextTime)))                        
                        for mPart,keys in d_tmp.iteritems():
                            if not keys:
                                continue
                            if _contextTime== 'next':
                                _match = MATH.find_valueInList(_frame,keys,'next')
                            else:
                                _match = MATH.find_valueInList(_frame,keys,'previous')
                            d_tmp[mPart] = [_match]
                elif _context == 'puppet':
                    if _contextTime in ['next','previous']:
                        log.debug(cgmGEN.logString_sub(_str_func,'Second pass | {0}'.format(_contextTime)))
                        if _contextTime== 'next':
                            _match = MATH.find_valueInList(_frame,l_keys,'next')
                        else:
                            _match = MATH.find_valueInList(_frame,l_keys,'previous')                        
                        
                        for mPart,keys in d_tmp.iteritems():
                            d_tmp[mPart] = [_match]                    
                    
                
                for mPart,keys in d_tmp.iteritems():
                    for k in keys:
                        addSource(self,mPart,k,_res)
                        
                
                                
                                
        #We have to cull some data in some cases....
        if _contextTime not in ['all']:
            if _contextTime in ['next','previous'] and _context !='control' and 'cat'=='dog':
                #We only want one value here...
                if _contextTime== 'next':
                    _match = MATH.find_valueInList(_frame,_res.keys(),'next')
                else:
                    _match = MATH.find_valueInList(_frame,_res.keys(),'previous')
                
                for k in _res.keys():
                    if k != _match:
                        _res.pop(k)
            else:
                _range = SEARCH.get_time('slider')
                for k in _res.keys():
                    if k < _range[0] or k > _range[1]:
                        log.debug("Out of range: {0}".format(k))
                        _res.pop(k)

        if _contextKeys == 'combined':
            log.debug(cgmGEN.logString_sub(_str_func,'Combining keys'))
            
            if _context == 'control':
                for k in _res.keys():
                    _res[k]= self.l_sources                
            else:
                mSources = self.mDat.d_context['partControls'].keys()
                for k in _res.keys():
                    _res[k]= mSources
            
            if _contextTime in ['next','previous']:
                log.debug(cgmGEN.logString_sub(_str_func,'Combined final cull | {0}'.format(_contextTime)))
                if _contextTime== 'next':
                    _match = MATH.find_valueInList(_frame,_res.keys(),'next')
                else:
                    _match = MATH.find_valueInList(_frame,_res.keys(),'previous')
                
                for k in _res.keys():
                    if k != _match:
                        _res.pop(k)                
            
        return _res
    except Exception,err:
        #pprint.pprint(self.mDat.d_context)
        cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
        

_l_timeFunctions = ['reset','report',
                    'resetFK','resetIK','resetIKEnd','resetSeg','resetDirect',
                    'FKon','IKon','FKsnap','IKsnap','IKsnapAll','mirrorPush','mirrorPull','mirrorFlip',
                   'aimToFK','aimOn','aimOff','aimToIK','aimSnap',
                   'aimSnap','aimToIK','aimToFK']

_l_noReselect = ['aimSnap','aimToIK','aimToFK']


def uiCB_contextualActionMM(self,**kws):
    _res = None
    try:
        _res = uiCB_contextualAction(self,**kws)
    except Exception,err:
        log.error(err)
    finally:
        mc.evalDeferred(MMUTILS.kill_mmTool,lp=True)
        return _res
    
@cgmGEN.Timer
def uiCB_contextualAction(self,**kws):
    _str_func='uiCB_contextualTime'
    log.debug(cgmGEN.logString_start(_str_func))
    
    l_kws = []
    for k,v in kws.iteritems():
        l_kws.append("{0}:{1}".format(k,v))
    
    #_mode = kws.pop('mode',False)
    #_context = kws.get('context') or self.var_mrsContext_mode.value
    #_contextTime = kws.get('contextTime') or self.var_mrsContext_time.value
    #_contextKeys = kws.get('contextKeys') or self.var_mrsContext_keys.value
    
    try:contextArg = self.__class__.TOOLNAME 
    except:contextArg = False
        
    log.debug(cgmGEN.logString_msg(_str_func,"contextArg: {0}".format(contextArg)))
    d_contextSettings = MRSANIMUTILS.get_contextDict(contextArg)
    d_contextSettings['contextPrefix'] = contextArg

    _mode = kws.pop('mode',False)
    
    for k in ['contextMode','contextTime','contextKeys','contextChildren','contextSiblings','contextMirror','contextKeys']:
        if kws.get(k) is not None:
            log.info(cgmGEN.logString_msg(_str_func,"Found: {0} : {1}".format(k,kws.get(k))))
            d_contextSettings[k] = kws.get(k)
            
    _context = d_contextSettings.get('contextMode')
    _contextTime = d_contextSettings.get('contextTime')
    _contextKeys = d_contextSettings.get('contextKeys')

    d_context = {}
    _mirrorQuery = False
    if _mode in ['mirrorPush','mirrorPull','symLeft','symRight','mirrorFlip','mirrorSelect','mirrorSelectOnly']:
        kws['addMirrors'] = True
        _mirrorQuery = True
        
    if _mode == 'mirrorVerify':
        kws['context'] = 'puppet'
    #res_context = get_context(self,**kws)
    
    #pprint.pprint(self.mDat.d_context)
    #return        
    #if not res_context:
        #return log.error("Nothing found in context: {0} ".format(_context))
    
    def endCall(self,report=True):
        if _mode not in _l_noReselect:
            mc.select(self.mDat._sel)
        if report:log.info("Context: {0} | mode: {1} | {2} - {3} | done.".format(_context, _mode,
                                                                                 _contextTime,_contextKeys))
        return 
    
    self.var_resetMode = cgmMeta.cgmOptionVar('cgmVar_ChannelResetMode', defaultValue = 0)
    
    log.debug("contextualAction pre...")
    #pprint.pprint(d_contextSettings)
    
    _ml_controls = self.mDat.context_get(addMirrors=_mirrorQuery,**d_contextSettings)
    
    if not _ml_controls:
        return log.error("No controls in context")
    
    #First we see if we have a current only function or current time ========================
    if _mode == 'simpleRes':
        return _ml_controls
    elif _mode == 'mirrorVerify':
        if not self.mDat.d_context.get('mPuppets'):
            log.warning("No puppets in context.")
            endCall(self,False)
            
        for mPuppet in self.mDat.d_context['mPuppets']:
            try:
                mPuppet.UTILS.mirror_verify(mPuppet)
            except Exception,err:
                log.error(err)
        endCall(self,False)
        
    #@cgmGEN.Timer
    def key(f,l_controls):
        for o in l_controls:#self.mDat.d_context['sControls']:
            mc.setKeyframe(o,time = f)
            
    if _contextTime == 'current' or _mode not in _l_timeFunctions:
        log.info(cgmGEN.logString_sub(None,'Current Only mode: {0}'.format(_mode)))
        
        _l_controls = [mObj.mNode for mObj in _ml_controls]
        
        if not _l_controls:
            return log.error("Nothing found in context: {0} ".format(_context))
            
            
        _contextTime = 'current'
        
        if _mode == 'report':
            self.mDat.report_contextDat()
            if _contextTime == 'current':
                return endCall(self)
        elif _mode == 'animFlip':
            self.mDat.mirrorData('Anim')
            return endCall(self)
        elif _mode == 'select':
            return  mc.select(_l_controls)
        elif _mode in ['selectFK','selectIK','selectIKEnd','selectSeg','selectDirect']:
            if _mode == 'selectFK':
                _tag = 'fk'
            elif _mode == 'selectIK':
                _tag = 'ik'
            elif _mode == 'selectIKEnd':
                _tag = 'ikEnd'
            elif _mode == 'selectSeg':
                _tag = 'segmentHandles'
            elif _mode == 'selectDirect':
                _tag = 'direct'
        
            l_new = []
            for mObj in self.mDat.d_context['mModules']:
                _l_buffer = mObj.atUtils('controls_getDat',_tag,listOnly=True)
                if _l_buffer:
                    l_new.extend([mHandle.mNode for mHandle in _l_buffer])
        
            if not l_new:
                return log.warning("Context: {0} | No controls found in mode: {1}".format(_context, _mode))
        
            return mc.select(l_new)                
        elif _mode in ['nextKey','prevKey']:
            l_keys = []
            if _mode == 'nextKey':
                for o in _l_controls:
                    l_keys.extend( SEARCH.get_key_indices_from(o,'next') )
                #mel.eval('NextKey;')
            elif _mode == 'prevKey':
                for o in _l_controls:
                    l_keys.extend( SEARCH.get_key_indices_from(o,'previous') )
            if l_keys:
                _key = min(l_keys)
                mc.currentTime(_key)
            else:
                log.error('No keys detected')
            return endCall(self)
        elif _mode == 'upToDate':
            log.info("Context: {0} | {1}".format(_context,_mode))
            if not self.mDat.d_context['mPuppets']:
                return log.error("No puppets detected".format(_mode))
            for mPuppet in self.mDat.d_context['mPuppets']:
                mPuppet.atUtils('is_upToDate',True)
            return endCall(self)
        elif _mode == 'tweenDrag':
            mc.select(_l_controls)
            return ml_breakdownDragger.drag()
        
        elif _mode in ['tweenNext','tweenPrev','tweenAverage']:
            v_tween = kws.get('tweenValue', None)
            if v_tween is None:
                try:v_tween = self.cgmUIFF_tweenBase.getValue()
                except:pass
                if not v_tween:
                    return log.error("No tween value detected".format(_mode))
            log.info("Context: {0} | {1} | tweenValue: {2}".format(_context,_mode,v_tween))
            mc.select(_l_controls)
    
            if _mode == 'tweenNext':
                ml_mode = 'next'
            elif _mode == 'tweenPrev':
                ml_mode = 'previous'
            else:
                ml_mode = 'average'
    
            ml_breakdown.weightBreakdownStep(ml_mode,v_tween)
    
            return endCall(self)
    
        elif _mode in ['holdCurrent','holdAverage','holdPrev','holdNext','holdCurrentTime','holdAverageTime']:
            mc.select(_l_controls)
    
            if _mode == 'holdCurrent':
                ml_hold.current()
            elif _mode == 'holdAverage':
                ml_hold.average()
            elif _mode == 'holdPrev':
                ml_hold.previous()
            elif _mode == 'holdNext':
                ml_hold.next()
            elif _mode == 'holdCurrentTime':
                ml_hold.holdRange(True,False)
            elif _mode == 'holdAverageTime':
                ml_hold.holdRange(False,True)
            return endCall(self)
        elif _mode == 'mirrorSelect':
            mc.select(_l_controls)
            return
        elif _mode == 'mirrorSelectOnly':
            l_sel = []
            if _context == 'control':
                for mObj in  self.mDat.d_context['mControlsMirror']:
                    l_sel.append(mObj.mNode)
            elif _context == 'part':
                for mPart in self.mDat.d_context['mModulesMirror']:
                    l_sel.extend([mObj.mNode for mObj in mPart.UTILS.controls_get(mPart)])
            else:
                return log.error("Context not supported: {0}".format(_context))
    
            if not l_sel:
                return log.error("Nothing found in context".format(_context))
    
            mc.select(l_sel)
            return
        elif _mode == 'mirrorFlip':
            self.mDat.mirrorData()
            self.mDat.key()
            return endCall(self)
        
        elif _mode in ['mirrorPush','mirrorPull',
                     'symLeft','symRight']:
            mBaseModule = self.mDat.d_context['mModulesBase'][0]                
            log.debug("|{0}| >> Mirroring. base: {1}".format(_str_func,mBaseModule))
            
            _l_cBuffer = [mObj.mNode for mObj in _ml_controls]
            for mMirror in self.mDat.d_context['mModulesMirror']:
                d_mModule = self.mDat.module_get(mMirror)
                _l_cBuffer.extend([mObj.mNode for mObj in d_mModule['mControls']])
                
            log.debug(cgmGEN._str_subLine)
            
            try:
                _primeAxis = self.mDat._ml_sel[0].getEnumValueString('mirrorSide')
                log.info("Prime axis from control: {0}".format(_primeAxis))
            except:
                if mBaseModule.hasAttr('cgmDirection'):
                    _primeAxis = mBaseModule.cgmDirection.capitalize()
                else:
                    _primeAxis = 'Centre'
                log.info("Prime axis from module: {0}".format(_primeAxis))
            else:
                _primeAxisUse = _primeAxis
                
                log.info("mirror call...")
                
                if _mode == 'mirrorPull':
                    _dFlip = {'Left':'Right',
                              'Right':'Left'}
            
                    _primeAxisUse = _dFlip.get(_primeAxis,_primeAxis)

                elif _mode == 'mirrorPush':
                    pass #...trying to just use first selected
                elif _mode == 'symLeft':
                    _primeAxisUse = 'Left'
                else:
                    _primeAxisUse = 'Right'
        
                    log.debug("|{0}| >> Mirror {1} | primeAxis: {2}.".format(_str_func,_mode,_primeAxisUse))
                
                r9Anim.MirrorHierarchy().makeSymmetrical(_l_cBuffer,
                                                         mode = '',
                                                         primeAxis = _primeAxisUse )        
            self.mDat.key()
            return endCall(self)    
    
    
    log.debug(cgmGEN.logString_sub(_str_func,'contextualAction | time query | mirrorQuery: {0}'.format(_mirrorQuery)))
    _res  = self.mDat.contextTime_get(mirrorQuery=_mirrorQuery,**d_contextSettings)
    log.debug("contextualAction time...")
    #pprint.pprint(d_contextSettings)
    #pprint.pprint(_res)
    #get_contextTimeDat(self,_mirrorQuery,**kws)
    try:
        if not _res[0]:
            return log.error(_res[1])
    except:
        if not _res:
            return log.error("Nothing found in time context: {0} ".format(_contextTime))
    
    if _mode == 'report':
        log.debug(cgmGEN.logString_sub(_str_func,'reportTime'))
        
        self.mDat.report_timeDat()
        log.debug("contextualAction | report time...")
        return endCall(self,True)
        
    #Frame Processing ============================================================================
    log.info(cgmGEN.logString_sub(None,'Frame Processing: {0}'.format(_mode)))
    
    _keys = _res.keys()
    _keys.sort()
    _int_keys = len(_keys)
    
    mc.undoInfo(openChunk=True,chunkName="undo{0}".format(_mode))
    _resetMode = self.var_resetMode.value
    d_buffer = {}
    _primeAxis = False
    _keyResult = False
    err=None
    if len(_keys) > 1:
        log.info("key result...")
        _keyResult=True
    
    _autoKey = mc.autoKeyframe(q=True,state=True)
    #if _autoKey:mc.autoKeyframe(state=False)
    _l_cBuffer = []
    #mc.refresh(su=1)
    
    if _mode == 'pushKey':
        log.debug("|{0}| >> Push Key buffer".format(_str_func))
        self.mDat.snapShot_get()

    try:
        for i,f in enumerate(_keys):
            log.info(cgmGEN.logString_sub(None,'Key: {0}'.format(f),'_',40))
            try:mc.progressBar(self.uiProgressBar,edit=True,maxValue = _int_keys,progress = i, vis=1)
            except:pass
            
            mc.currentTime(f,update=True)
            if _mode == 'mirrorFlip':
                self.mDat.mirrorData()
                self.mDat.key()
                
            elif _mode in ['mirrorPush','mirrorPull',
                         'symLeft','symRight']:
                mBaseModule = self.mDat.d_context['mModulesBase'][0]                
                log.debug("|{0}| >> Mirroring. base: {1}".format(_str_func,mBaseModule))
                
                if not _l_cBuffer:
                    _l_cBuffer = [mObj.mNode for mObj in _ml_controls]
                    #_l_cBuffer = _l_controls#self.mDat.d_context['sControls']
                    for mMirror in self.mDat.d_context['mModulesMirror']:
                        d_mModule = self.mDat.module_get(mMirror)
                        _l_cBuffer.extend([mObj.mNode for mObj in d_mModule['mControls']])
                    
                log.debug(cgmGEN._str_subLine)
                
                #if not _primeAxis:
                try:
                    _primeAxis = self.mDat._ml_sel[0].getEnumValueString('mirrorSide')
                    log.info("Prime axis from control: {0}".format(_primeAxis))
                except:
                    if mBaseModule.hasAttr('cgmDirection'):
                        _primeAxis = mBaseModule.cgmDirection.capitalize()
                    else:
                        _primeAxis = 'Centre'
                    log.info("Prime axis from module: {0}".format(_primeAxis))
                else:
                    _primeAxisUse = _primeAxis
                    
                    log.info("mirror call...")
                    
                    if _mode == 'mirrorPull':
                        _dFlip = {'Left':'Right',
                                  'Right':'Left'}
                
                        _primeAxisUse = _dFlip.get(_primeAxis,_primeAxis)

                    elif _mode == 'mirrorPush':
                        pass #...trying to just use first selected
                    elif _mode == 'symLeft':
                        _primeAxisUse = 'Left'
                    else:
                        _primeAxisUse = 'Right'
            
                        log.debug("|{0}| >> Mirror {1} | primeAxis: {2}.".format(_str_func,_mode,_primeAxisUse))
                    
                    r9Anim.MirrorHierarchy().makeSymmetrical(_l_cBuffer,
                                                             mode = '',
                                                             primeAxis = _primeAxisUse )
                if _keyResult:
                    key(f,_l_cBuffer)
                    #for o in _l_cBuffer:#self.mDat.d_context['sControls']:
                        #mc.setKeyframe(o,time = f)
                        
            if _mode in ['FKon','IKon','FKsnap','IKsnap','IKsnapAll',
                         'aimToFK','aimOn','aimOff','aimToIK','aimSnap']:
                log.info("Context: {0} | Switch call".format(_context))
                res = []
        
                #if not self.mDat.d_context['mModules']:
                    #return log.error("No modules detected".format(_mode))
                #pprint.pprint(self.mDat.d_context['mModules'])
                for mModule in self.mDat.d_context['mModules']:
                    res.append(mModule.atUtils('switchMode',_mode))
                        
                    if _keyResult:
                        key(f,self.mDat.d_timeContext['partControls'][mModule])                    
                        #for o in _l_controls:#self.mDat:#self.mDat.d_context['sControls']:
                            #mc.setKeyframe(o,time = f)
            elif _mode == 'pushKey':
                self.mDat.snapShot_set()
                for mPart,controls in self.mDat.d_timeContext['partControls'].iteritems():
                    for c in controls:
                        if SEARCH.get_key_indices_from(c):
                            mc.setKeyframe(c,time = f)                        
            else:
                log.info("Processing parts...".format(_context))
                
                for mPart,controls in self.mDat.d_timeContext['partControls'].iteritems():
                    log.info(cgmGEN.logString_sub(None,'Part: {0}'.format(mPart),'_',40))
                    try:
                        mc.progressBar(self.uiProgressBar,edit=True,
                                       maxValue = len(self.mDat.d_timeContext['partControls'].keys()),step = 1, vis=1)
                    except:pass
                    
                    if _mode == 'reset':
                        RIGGEN.reset_channels_fromMode(controls,_resetMode)
                        if _keyResult:
                            key(f,controls)
                    
                    elif _mode in ['resetFK','resetIK','resetIKEnd','resetSeg','resetDirect']:
                        l_use = controls
                        if _context != 'control':
                            if _mode == 'resetFK':
                                _tag = 'fk'
                            elif _mode == 'resetIK':
                                _tag = 'ik'
                            elif _mode == 'resetIKEnd':
                                _tag = 'ikEnd'
                            elif _mode == 'resetSeg':
                                _tag = 'segmentHandles'
                            elif _mode == 'resetDirect':
                                _tag = 'direct'
                                
                            l_use = d_buffer.get(mPart,[])
                            if not l_use:
                                log.info("Buffering controls for: {0}".format(mPart))
                                for mObj in self.mDat.d_context['mModules']:
                                    _l_buffer = mObj.atUtils('controls_getDat',_tag,listOnly=True)
                                    if _l_buffer:l_use.extend([mHandle.mNode for mHandle in _l_buffer])
                                if not l_use:
                                    return log.warning("Context: {0} | No controls found in mode: {1}".format(_context, _mode))
                                    
                        RIGGEN.reset_channels_fromMode(l_use,_resetMode)
                        if _keyResult:
                            for c in controls:
                                if SEARCH.get_key_indices_from(c):
                                    mc.setKeyframe(c,time = f)
                                
                        
                    elif _mode in ['key','bdKey','delete']:
                        mc.select(controls)
                        if _mode == 'key':
                            setKey('default')
                        elif _mode == 'bdKey':
                            setKey('breakdown')
                        elif _mode == 'delete':
                            deleteKey()
                        print(controls)
                            
                    elif _mode in ['mirrorPush','mirrorPull',
                                   'symLeft','symRight','mirrorFlip']:
                        log.debug(cgmGEN._str_subLine)
                        mBaseModule = self.mDat.d_context['mModulesBase'][0]
                        log.debug("|{0}| >> Mirroring. base: {1}".format(_str_func,mBaseModule))
                    
                        try:
                            _primeAxis = self._ml_sel[0].getEnumValueString('mirrorSide')
                            log.info("Prime axis from control: {0}".format(_primeAxis))
                        except:
                            if mBaseModule.hasAttr('cgmDirection'):
                                _primeAxis = mBaseModule.cgmDirection.capitalize()
                            else:
                                _primeAxis = 'Centre'
                            log.info("Prime axis from module: {0}".format(_primeAxis))
                    
                        if _mode == 'mirrorFlip':
                            if not _l_cBuffer:
                                _l_cBuffer = [mObj.mNode for mObj in _ml_controls]                            
                            r9Anim.MirrorHierarchy().mirrorData(_l_cBuffer,mode = '')
                        else:
                            if _mode == 'mirrorPull':
                                _dFlip = {'Left':'Right',
                                          'Right':'Left'}
                        
                                _primeAxis = _dFlip.get(_primeAxis,_primeAxis)
                                #mMirror = mBaseModule.atUtils('mirror_get')
                                #if mMirror and mMirror.hasAttr('cgmDirection'):
                                #    _primeAxis = mMirror.cgmDirection.capitalize()
                                #else:
                                #    _primeAxis = 'Centre'
                        
                            elif _mode == 'mirrorPush':
                                pass #...trying to just use first selected
                                """
                                        if mBaseModule.hasAttr('cgmDirection'):
                                            _primeAxis = mBaseModule.cgmDirection.capitalize()
                                        else:
                                            _primeAxis = 'Centre'"""
                            elif _mode == 'symLeft':
                                _primeAxis = 'Left'
                            else:
                                _primeAxis = 'Right'
                    
                                log.debug("|{0}| >> Mirror {1} | primeAxis: {2}.".format(_str_func,_mode,_primeAxis))
                            
                                r9Anim.MirrorHierarchy().makeSymmetrical(self.mDat.d_context['sControls'],
                                                                 mode = '',
                                                                 primeAxis = _primeAxis )                        

            
    except Exception,err:
        pprint.pprint(vars())
        log.error(err)
    finally:
        mc.undoInfo(closeChunk=True)
        mc.currentTime(self.mDat.d_timeContext.get('frameInitial',1.0))
        if _autoKey:mc.autoKeyframe(state=True)
        mc.refresh(su=0)
        if err:
            cgmGEN.cgmExceptCB(Exception,err,localDat=vars())    
            
        try:cgmUI.progressBar_end(self.uiProgressBar)
        except:pass
        return endCall(self)            
        
        
        
        

def buildFrame_mrsTimeContext(self,parent):
    def setContext_time(self,arg):
        self.var_mrsContext_time.setValue(arg)
        updateHeader(self)
    def setContext_keys(self,arg):
        self.var_mrsContext_keys.setValue(arg)
        updateHeader(self)        
        
    def updateHeader(self):
        self.uiFrame_time(edit=True, label = "Time | {0} - {1}".format(self.var_mrsContext_keys.value,
                                                                       self.var_mrsContext_time.value))        
        
    try:self.var_mrsTimeContextFrameCollapse
    except:self.create_guiOptionVar('mrsTimeContextFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_mrsTimeContextFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Time',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                #ann='Contextual MRS functionality',
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    self.uiFrame_time = _frame
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    #>>>Anim ===================================================================================== 
    #>>>Keys Context Options -------------------------------------------------------------------------------
    #bgc=_subLineBGC
    _rowContextKeys = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    #_rowContextKeys = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5,bgc=_subLineBGC)


    mUI.MelSpacer(_rowContextKeys,w=5)                          
    mUI.MelLabel(_rowContextKeys,l='Keys: ')
    _rowContextKeys.setStretchWidget( mUI.MelSeparator(_rowContextKeys) )

    uiRC = mUI.MelRadioCollection()

    mVar = self.var_mrsContext_keys
    _on = mVar.value

    for i,item in enumerate(_l_contextKeys):
        if item == _on:
            _rb = True
        else:_rb = False
        _label = str(_d_shorts.get(item,item))
        uiRC.createButton(_rowContextKeys,label=_label,sl=_rb,
                          ann = "Set keys context to: {0}".format(item),                          
                          onCommand = cgmGEN.Callback(setContext_keys,self,item))
        
    mUI.MelButton(_rowContextKeys,label='Q',
                  ann='Query the time context',
                  c=cgmGEN.Callback(uiCB_contextualAction,self,**{'mode':'report'}))
    mUI.MelSpacer(_rowContextKeys,w=2)                          
    
    _rowContextKeys.layout()    

    #>>>Time Context Options -------------------------------------------------------------------------------
    #_rowContextTime = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    _rowContextTime = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=3)

    _d = {}

    #mUI.MelSpacer(_rowContextTime,w=5)                          
    #mUI.MelLabel(_rowContextTime,l='Time: ')
    #_rowContextTime.setStretchWidget( mUI.MelSeparator(_rowContextTime) )

    uiRC = mUI.MelRadioCollection()

    mVar = self.var_mrsContext_time
    _on = mVar.value

    for i,item in enumerate(_l_contextTime):
        #if item == _on:
        #    _rb = True
        #else:_rb = False
        _label = str(_d_shorts.get(item,item))
        mUI.MelButton(_rowContextTime,label=_label,
                      ann = "Set time context to: {0}".format(item),
                      ut='cgmUITemplate',
                      c = cgmGEN.Callback(setContext_time,self,item)) 
        #uiRC.createButton(_rowContextTime,label=_label,sl=_rb,
        #                  ann = "Set time context to: {0}".format(item),                          
        #                  onCommand = self.mmCallback(setContext_time,self,item))        
    _rowContextTime.layout()         
    mc.setParent(_inside)
    cgmUI.add_LineBreak()
    updateHeader(self)
    
def buildFrame_mrsList(self,parent):
    try:self.var_mrsListFrameCollapse
    except:self.create_guiOptionVar('mrsListFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_mrsListFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'List',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                #ann='Contextual MRS functionality',
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate')
    
    _textField = mUI.MelTextField(_inside,
                                  ann='Filter blocks',
                                  w=50,
                                  bgc = [.3,.3,.3],
                                  en=True,
                                  text = '')
    self.cgmUIField_filterScene = _textField

    
    _scrollList = mrsScrollList(_inside, ut='cgmUISubTemplate',
                                allowMultiSelection=True,en=True,
                                ebg=0,
                                h=200,
                                bgc = [.2,.2,.2],
                                #dcc = self.mmCallback(self.uiFunc_block_setActive),
                                w = 50)
    try:_scrollList(edit=True,hlc = [.5,.5,.5])
    except:pass
    
    #_scrollList.cmd_select = lambda *a:self.uiScrollList_block_select()
    _scrollList.set_filterObj(self.cgmUIField_filterScene)
    self.cgmUIField_filterScene(edit=True,
                                 tcc = lambda *a: self.uiScrollList_blocks.update_display())
    
    self.uiScrollList_blocks = _scrollList
    _row = mUI.MelHLayout(_inside,padding=5,)
    button_refresh = mUI.MelButton(_row,
                                   label='Clear Sel',ut='cgmUITemplate',
                                    c=lambda *a:self.uiScrollList_blocks.clearSelection(),
                                    ann='Clear selection the scroll list to update')     
    button_refresh = mUI.MelButton(_row,
                                   label='Refresh',ut='cgmUITemplate',
                                    c=lambda *a:self.uiScrollList_blocks.rebuild(),
                                    ann='Force the scroll list to update')    
    _row.layout()
    
    

def buildFrame_mrsAnim(self,parent):
    try:self.var_mrsAnimFrameCollapse
    except:self.create_guiOptionVar('mrsAnimFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_mrsAnimFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Anim',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                #ann='Contextual MRS functionality',
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    #>>>Anim ===================================================================================== 

    #>>>Key snap -------------------------------------------------------------------------------------
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)

    d_anim = {'key':{'ann':'Key all controls in context',
                     'arg':{'mode':'key'},},
              'bKey':{'ann':'Set a breakdown key',
                     'arg':{'mode':'bdKey'},},              
              '<<':{'ann':'Find previous contexual key',
                     'arg':{'mode':'prevKey'},},
              '>>':{'ann':'Find next contexual key',
                     'arg':{'mode':'nextKey'},},
              'delete':{'ann':'Clear current contextual keys',
                        'short':'del',
                        'arg':{'mode':'delete'},},
              'push':{'ann':'Push current contextual key to others in context',
                     'arg':{'mode':'pushKey'},}}
    
    l_anim = ['<<','key','bKey','>>','delete','push']
    for b in l_anim:
        _d = d_anim.get(b,{})
        _arg = _d.get('arg',{'mode':b})
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  en = _d.get('en',True),
                  c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    _row.layout()

    #>>>Select -------------------------------------------------------------------------------------
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    d_select = {'select':{'ann':'Select objects in context',
                          'short':'all',
                          'arg':{'mode':'select'}},
                'selectFK':{'ann':'Select fk objects in context',
                            'short':'fk',                            
                            'arg':{'mode':'selectFK'}},
                'selectDirect':{'ann':'Select direct objects in context',
                                'short':'direct',                                
                                'arg':{'mode':'selectDirect'}},
                'selectSeg':{'ann':'Select segment handles objects in context',
                             'short':'seg',                             
                             'arg':{'mode':'selectSeg'}},
                'selectIK':{'ann':'Select IK  objects in context',
                            'short':'ik',
                             'arg':{'mode':'selectIK'}},
                'selectIKEnd':{'ann':'Select IK  objects in context',
                            'short':'ikEnd',
                             'arg':{'mode':'selectIKEnd'}},
                'reset':{'ann':'Reset all controls in context',
                         'short':'all',
                         'arg':{'mode':'reset'},},
                'resetFK':{'ann':'Reset fk objects in context',
                            'short':'fk',                            
                            'arg':{'mode':'resetFK'}},
                'resetDirect':{'ann':'Reset direct objects in context',
                                'short':'direct',                                
                                'arg':{'mode':'resetDirect'}},
                'resetSeg':{'ann':'Reset segment handles objects in context',
                             'short':'seg',                             
                             'arg':{'mode':'resetSeg'}},
                'resetIK':{'ann':'Reset IK  objects in context',
                            'short':'ik',
                             'arg':{'mode':'resetIK'}},
                'resetIKEnd':{'ann':'Reset IK  objects in context',
                            'short':'ikEnd',
                             'arg':{'mode':'resetIKEnd'}},
                }
    """
    l_select = ['select','report']
    for b in l_select:
        _d = d_select.get(b,{})
        _arg = _d.get('arg',{'mode':b})
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = self.mmCallback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    _row.layout()"""
    
    #mc.setParent(_inside)
    #cgmUI.add_LineSubBreak()
    
    """
    mc.button(parent = _inside,
              ut = 'cgmUITemplate',
              l='Test context',
              c=lambda *a: get_context(self))
              """
    #Select row ---------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5,bgc=_subLineBGC)

    mUI.MelSpacer(_row,w=5)
    mUI.MelLabel(_row,l='Select:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    
    l_switch = ['selectFK','selectIK','selectIKEnd','selectSeg','selectDirect','select']
    for b in l_switch:
        _d = d_select.get(b,{})
        _arg = _d.get('arg',{'mode':b})        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    mUI.MelSpacer(_row,w=5)
    _row.layout()            
    
    
    
    #Reset row ---------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5,bgc=_subLineBGC)

    mUI.MelSpacer(_row,w=5)
    mUI.MelLabel(_row,l='Reset:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    
    l_switch = ['resetFK','resetIK','resetIKEnd','resetSeg','resetDirect','reset']
    for b in l_switch:
        _d = d_select.get(b,{})
        _arg = _d.get('arg',{'mode':b})        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    mUI.MelSpacer(_row,w=5)
    _row.layout()        
    
    return
    #>>>Mirror ===================================================================================== 
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    cgmUI.add_Header('Mirror')
    cgmUI.add_LineSubBreak()
    
    d_mirror = {'push':{'ann':'Push to the opposite side',
                        'arg':{'mode':'mirrorPush'}},
                'pull':{'ann':'Pull from the opposite side',
                        'arg':{'mode':'mirrorPull'}},
                'symLeft':{'ann':'Symmetrical to the left',
                        'arg':{'mode':'symLeft'}},
                'symRight':{'ann':'Symmetrical to the right',
                            'arg':{'mode':'symRight'}},
                'flip':{'ann':'Flip the pose',
                        'arg':{'mode':'mirrorFlip'}},
                'mirrorSelect':{'ann':'Select objects in mirror context',
                                'short':'select',
                                'arg':{'mode':'mirrorSelect'}},                
                }
    
    l_mirror = ['push','pull','flip','symLeft','mirrorSelect','symRight']
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    
    for i,b in enumerate(l_mirror):
        _d = d_mirror.get(b,{})
        _arg = _d.get('arg',{'mode':b})
        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = self.mmCallback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
        if i == 2:#New row
            _row.layout()
            _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
            
    _row.layout()
    
    
    
    #>>>Switch ===================================================================================== 
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()        
    cgmUI.add_Header('Switch')
    cgmUI.add_LineSubBreak()
    
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    d_switch = {'FKsnap':{'ann':'Snap fk controls to blend chain for modules in context',
                          'arg':{'mode':'FKsnap'}},
                'FKon':{'ann':'Turn fk on to all modules in context',
                        'arg':{'mode':'FKon'}},
                'IKsnap':{'ann':'Snap main ik controls to blend chain for modules in context',
                          'arg':{'mode':'IKsnap'}},
                'IKon':{'ann':'Turn ik on to all modules in context',
                        'arg':{'mode':'IKon'}},
                'IKforce':{'ann':'Snap main ik/direct controls to blend chain for modules in context',
                         'arg':{'mode':'IKsnapAll'}},
                
                'aimOn':{'ann':'Turn aim on contexually',
                         'short':'on',
                         'arg':{'mode':'aimOn'}},                
                'aimOff':{'ann':'Turn aim off contexually',
                          'short':'off',                          
                          'arg':{'mode':'aimOff'}},
                'aimToIK':{'ann':'Snap aim to controls in context',
                           'short':'toIK',                           
                           'arg':{'mode':'aimToIK'}},
                'aimToFK':{'ann':'Snap aim to controls in context',
                           'short':'toFK',                           
                           'arg':{'mode':'aimToFK'}},
                'aimSnap':{'ann':'Snap aim controls on in context',
                           'short':'snap',                           
                           'arg':{'mode':'aimSnap'}},                
                }
    
    l_switch = ['FKsnap','FKon','IKon','IKsnap','IKforce']
    for b in l_switch:
        _d = d_switch.get(b,{})
        _arg = _d.get('arg',{'mode':b})        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = self.mmCallback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    _row.layout()
    
    #Aim row ---------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)
    mUI.MelLabel(_row,l='Aim:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    
    l_switch = ['aimOn','aimOff','aimToFK','aimToIK','aimSnap']
    for b in l_switch:
        _d = d_switch.get(b,{})
        _arg = _d.get('arg',{'mode':b})        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = self.mmCallback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    mUI.MelSpacer(_row,w=5)
    _row.layout()    
    
    #>>>Settings ===================================================================================== 
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()        
    cgmUI.add_Header('Settings')
    l_settings = ['visSub','visDirect','visRoot']
    l_enums = ['skeleton','geo','proxy']

    for n in l_settings + l_enums:
        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l=' {0}:'.format(n))
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        if n in l_settings:
            l_options = ['hide','show']
            _mode = 'moduleSettings'
        else:
            l_options = ['off','lock','on']
            _mode = 'puppetSettings'
        
        for v,o in enumerate(l_options):
            mc.button(parent = _row,
                      ut = 'cgmUITemplate',
                      l=o,
                      c=self.mmCallback(uiCB_contextSetValue,self,n,v,_mode))
                      #c=lambda *a: LOCINATOR.cgmUI())             
            
        mUI.MelSpacer(_row,w=2)
        _row.layout()
        

def buildFrame_mrsHold(self,parent):
    try:self.var_mrsHoldFrameCollapse
    except:self.create_guiOptionVar('mrsHoldFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_mrsHoldFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Hold',vis=True,
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
    
    d_hold = {'holdCurrent':{'short':'current',
                             'ann':'ml_hold + context | Creates a hold for the selected range, or the surrounding keys, based on current frame.',
                             'arg':{'mode':'holdCurrent'}},
              
              'holdAverage':{'short':'average',
                             'ann':'ml_hold + context | Creates a hold for the selected range, or the surrounding keys, based on average of keys.',
                             'arg':{'mode':'holdAverage'}},              

              'holdPrev':{'short':'<<Prev',
                             'ann':'ml_hold + context | Matches selected key or current frame to the previous keyframe value.',
                             'arg':{'mode':'holdPrev'}},
              'holdNext':{'short':'Next>>',
                             'ann':'ml_hold + context | Matches selected key or current frame to the next keyframe value.',
                             'arg':{'mode':'holdNext'}},
              'holdCurrentTime':{'short':'Current Time',
                                 'ann':'ml_hold + context | hold for range',
                                 'arg':{'mode':'holdCurrentTime'}},              

              'holdAverageTime':{'short':'Average Time',
                                 'ann':'ml_hold + context | Matches selected key or current frame to the next keyframe value.',
                                 'arg':{'mode':'holdAverageTime'}},}
    
    l_hold = ['holdCurrent','holdAverage','holdCurrentTime','holdAverageTime','holdPrev','holdNext',]
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    
    for i,b in enumerate(l_hold):
        _d = d_hold.get(b,{})
        _arg = _d.get('arg',{'mode':b})
        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
        if i in [1,3]:#New row
            _row.layout()
            _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
            
    _row.layout()

def buildFrame_mrsMirror(self,parent):
    try:self.var_mrsMirrorFrameCollapse
    except:self.create_guiOptionVar('mrsMirrorFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_mrsMirrorFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Mirror',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    #>>>Mirror ===================================================================================== 
    cgmUI.add_LineSubBreak()
    
    d_mirror = {'push':{'ann':'Push to the opposite side',
                        'arg':{'mode':'mirrorPush'}},
                'pull':{'ann':'Pull from the opposite side',
                        'arg':{'mode':'mirrorPull'}},
                'symLeft':{'ann':'Symmetrical to the left',
                        'arg':{'mode':'symLeft'}},
                'symRight':{'ann':'Symmetrical to the right',
                            'arg':{'mode':'symRight'}},
                'flip':{'ann':'Flip the pose',
                        'arg':{'mode':'mirrorFlip'}},
                'animFlip':{'ann':'Flip the animation | IGNORES TIME CONTEXT',
                            'arg':{'mode':'animFlip'}},
                'mirrorSelect':{'ann':'Select objects in mirror context',
                                'short':'select',
                                'arg':{'mode':'mirrorSelect'}},                
                }
    
    l_mirror = ['push','pull','flip','symLeft','symRight','mirrorSelect','animFlip']
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    
    for i,b in enumerate(l_mirror):
        _d = d_mirror.get(b,{})
        _arg = _d.get('arg',{'mode':b})
        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
        if i and MATH.is_even(i):#New row
            _row.layout()
            _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    _row.layout()
    
    
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
    #_inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate')
    
    
    _manager = POSEMANAGER.manager(parent = _frame)
    self.mPoseManager = _manager
    for k in self.__dict__.keys():
        if str(k).startswith('var_'):
            self.mPoseManager.__dict__[k] = self.__dict__[k]
    
    return _manager     
    
    
    return
    
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


    #from functools import self.mmCallback

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
              #c = self.mmCallback(uiCB_contextualAction,self,**_arg),
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
                          onCommand = self.mmCallback(self._uiCB_switchPosePathMode, item),
                          offCommand = self.mmCallback(self._uiCB_switchPosePathMode, _reverse))

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
              #c = self.mmCallback(uiCB_contextualAction,self,**_arg),
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
              command=self.mmCallback(self._uiCall, 'PoseLoad'))
    mc.button(parent=_row,
              l = 'Save',
              ut = 'cgmUITemplate',
              command=self.mmCallback(self._uiCall, 'PoseSave'))
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
                      # selectCommand=self.mmCallback(self._uiPresetSelection), \
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
                        # selectCommand=self.mmCallback(self._uiPresetSelection), \
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
                command=self.mmCallback(self._uiCall, 'PoseLoad'))
    mc.button('savePoseButton', label=LANGUAGE_MAP._AnimationUI_.pose_save, bgc=self.buttonBgc,
                ann=LANGUAGE_MAP._AnimationUI_.pose_save_ann,
                command=self.mmCallback(self._uiCall, 'PoseSave'))    
    
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
                                             
    self.cgmUISlider_reset.setPostChangeCB(self.mmCallback(uiCB_resetSliderDrop,self))
    
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
    
    
def buildFrame_mrsTween(self,parent):
    try:self.var_mrsTweenFrameCollapse
    except:self.create_guiOptionVar('mrsTweenFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_mrsTweenFrameCollapse
    _frame = mUI.MelFrameLayout(parent,label = 'Tween',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    d_tween = {'tweenDrag':{'ann':'Initialze Morgan Loomis fantastic breakdown dragger',
                        'arg':{'mode':'tweenDrag'}},
               'tweenAverage':{'ann':'mlBreakdown + context | Weight toward the average of the next and previous frame.',
                               'short':'avg',
                               'arg':{'mode':'tweenAverage'}},               
               'tweenPrev':{'ann':'mlBreakdown + context | Weight toward the previous key.',
                            'short':'<<',
                            'arg':{'mode':'tweenPrev'}},                
               'tweenNext':{'ann':'mlBreakdown + context | Weight toward the next key.',
                            'short':'>>',
                            'arg':{'mode':'tweenNext'}}}
    
    
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
    
    #>>>Tween ===================================================================================== 
    cgmUI.add_LineSubBreak()
    
    _uiRow_tween = mUI.MelHSingleStretchLayout(_inside, height = 27)

    mUI.MelSpacer(_uiRow_tween, w = 2)
    mUI.MelLabel(_uiRow_tween,l='Tween')

    self.cgmUISlider_tween = mUI.MelFloatSlider(_uiRow_tween, -1.5, 1.5, defaultValue=0, 
                                             #bgc = cgmUI.guiBackgroundColor,
                                             value = 0,
                                             cc = lambda *a: uiCB_tweenSlider(self))
                                             
    self.cgmUISlider_tween.setPostChangeCB(cgmGEN.Callback(uiCB_tweenSliderDrop,self))
    cgmUI.add_Button(_uiRow_tween,'Drag',
                     cgmGEN.Callback(uiCB_contextualAction,self,**d_tween['tweenDrag']['arg']),
                     d_tween['tweenDrag']['ann'])        
    
    mUI.MelSpacer(_uiRow_tween, w = 1)
    """
    mc.button(parent=_uiRow_tween ,
              ut = 'cgmUITemplate',
              l = 'R',
              c = lambda *a: self.cgmUISlider_tween.reset(),
              ann = "Reset tweener")
    """
    mUI.MelSpacer(_uiRow_tween, w = 2)
    _uiRow_tween.setStretchWidget(self.cgmUISlider_tween)
    _uiRow_tween.layout() 
    
    
    #Amount slider ------------------------------------------------------------------------------------
    _uiRow_twnAmount = mUI.MelHSingleStretchLayout(_inside, height = 27)

    mUI.MelSpacer(_uiRow_twnAmount, w = 2)
    mUI.MelLabel(_uiRow_twnAmount,l='Amount')

    self.cgmUIFF_tweenBase = mUI.MelFloatField(_uiRow_twnAmount, w = 50, value = .2,
                                            cc = lambda *a: self.cgmUISlider_tweenBase.setValue(self.cgmUIFF_tweenBase.getValue()))    

    self.cgmUISlider_tweenBase = mUI.MelFloatSlider(_uiRow_twnAmount, 0, 2.0, defaultValue=.2, 
                                                 #bgc = cgmUI.guiBackgroundColor,
                                                 value = .2,
                                                 cc = lambda *a: self.cgmUIFF_tweenBase.setValue(self.cgmUISlider_tweenBase.getValue()),
                                                 #dragCommand = lambda *a: log.info(self.cgmUISlider_tweenBase.getValue()),
                                                 )
    mUI.MelSpacer(_uiRow_twnAmount, w = 1)
    """
    mc.button(parent=_uiRow_tween ,
              ut = 'cgmUITemplate',
              l = 'R',
              c = lambda *a: self.cgmUISlider_tween.reset(),
              ann = "Reset tweener")
    """
    mUI.MelSpacer(_uiRow_twnAmount, w = 2)
    _uiRow_twnAmount.setStretchWidget(self.cgmUISlider_tweenBase)
    _uiRow_twnAmount.layout()    
    
    
    #Tween buttons ------------------------------------------------------------------------------------
    l_tween = ['tweenPrev','tweenAverage','tweenNext']
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    
    for i,b in enumerate(l_tween):
        _d = d_tween.get(b,{})
        _arg = _d.get('arg',{'mode':b})
        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    _row.layout() 
    
    
    return
    

def buildFrame_mrsSwitch(self,parent):
    try:self.var_mrsSwitchFrameCollapse
    except:self.create_guiOptionVar('mrsSwitchFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_mrsSwitchFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Switch',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
 
    #>>>Switch ===================================================================================== 
    cgmUI.add_LineSubBreak()        
    
    d_switch = {'FKsnap':{'ann':'Snap fk controls to blend chain for modules in context',
                          'short':'snap',
                          'arg':{'mode':'FKsnap'}},
                'FKon':{'ann':'Turn fk on to all modules in context',
                        'short':'on',
                        'arg':{'mode':'FKon'}},
                'IKsnap':{'ann':'Snap main ik controls to blend chain for modules in context',
                          'short':'snap',                          
                          'arg':{'mode':'IKsnap'}},
                'IKon':{'ann':'Turn ik on to all modules in context',
                        'short':'on',                        
                        'arg':{'mode':'IKon'}},
                'IKforce':{'ann':'Snap main ik/direct controls to blend chain for modules in context',
                           'short':'force',                           
                           'arg':{'mode':'IKsnapAll'}},
                
                'aimOn':{'ann':'Turn aim on contexually',
                         'short':'on',
                         'arg':{'mode':'aimOn'}},                
                'aimOff':{'ann':'Turn aim off contexually',
                          'short':'off',                          
                          'arg':{'mode':'aimOff'}},
                'aimToIK':{'ann':'Snap aim to controls in context',
                           'short':'toIK',                           
                           'arg':{'mode':'aimToIK'}},
                'aimToFK':{'ann':'Snap aim to controls in context',
                           'short':'toFK',                           
                           'arg':{'mode':'aimToFK'}},
                'aimSnap':{'ann':'Snap aim controls on in context',
                           'short':'snap',                           
                           'arg':{'mode':'aimSnap'}},                
                }
    """
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    
    l_switch = ['FKsnap','FKon','IKon','IKsnap','IKforce']
    for b in l_switch:
        _d = d_switch.get(b,{})
        _arg = _d.get('arg',{'mode':b})        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = self.mmCallback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    _row.layout()"""
    
    #FK row ---------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate', )

    mUI.MelSpacer(_row,w=5)
    mUI.MelLabel(_row,l='FK:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    
    l_switch = ['FKsnap','FKon']
    for b in l_switch:
        _d = d_switch.get(b,{})
        _arg = _d.get('arg',{'mode':b})        
        mc.button(parent=_row,
                  #l = '    {0}    '.format(_d.get('short',b)),
                  l = '    {0}    '.format(b),                  
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    mUI.MelSpacer(_row,w=5)
    _row.layout()
    
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    
    
    #IK row ---------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)
    mUI.MelLabel(_row,l='IK:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    
    l_switch = ['IKsnap','IKforce','IKon']
    for b in l_switch:
        _d = d_switch.get(b,{})
        _arg = _d.get('arg',{'mode':b})        
        mc.button(parent=_row,
                  #l = '    {0}    '.format(_d.get('short',b)),
                  l = '   {0}   '.format(b),                                    
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    mUI.MelSpacer(_row,w=5)
    _row.layout()
    
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    
    #Aim row ---------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5, bgc = _subLineBGC)

    mUI.MelSpacer(_row,w=5)
    mUI.MelLabel(_row,l='Aim:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    
    l_switch = ['aimOn','aimOff','aimToFK','aimToIK','aimSnap']
    for b in l_switch:
        _d = d_switch.get(b,{})
        _arg = _d.get('arg',{'mode':b})        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    mUI.MelSpacer(_row,w=5)
    _row.layout()
    
def buildFrame_mrsSettings(self,parent):
    try:self.var_mrsSettingsFrameCollapse
    except:self.create_guiOptionVar('mrsSettingsFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_mrsSettingsFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Settings',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    #>>>Settings ===================================================================================== 
    cgmUI.add_LineSubBreak()
    l_settings = ['visSub','visDirect','visRoot']
    l_enums = ['skeleton','geo','proxy']

    for n in l_settings + l_enums:
        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l=' {0}:'.format(n))
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        if n in l_settings:
            l_options = ['hide','show']
            _mode = 'moduleSettings'
        else:
            l_options = ['off','lock','on']
            _mode = 'puppetSettings'
        
        for v,o in enumerate(l_options):
            mc.button(parent = _row,
                      ut = 'cgmUITemplate',
                      l = '    {0}    '.format(o),
                      c=cgmGEN.Callback(uiCB_contextSetValue,self,n,v,_mode))
                      #c=lambda *a: LOCINATOR.cgmUI())             
            
        mUI.MelSpacer(_row,w=2)
        _row.layout()














def buildFrame_puppet(self,parent):
    try:self.var_puppetFrameCollapse
    except:self.create_guiOptionVar('puppetFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_puppetFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Puppet',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                ann='Buttons in this section work on the puppet level.',
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    

    
    
        
    #>>>Settings -------------------------------------------------------------------------------------    
    l_settings = ['visSub','visDirect','visRoot']
    l_enums = ['skeleton','geo','proxy']

    for n in l_settings + l_enums:
        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l=' {0}:'.format(n))
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        if n in l_settings:
            l_options = ['hide','show']
            _mode = 'moduleSettings'
        else:
            l_options = ['off','lock','on']
            _mode = 'puppetSettings'
        
        for v,o in enumerate(l_options):
            mc.button(parent = _row,
                      ut = 'cgmUITemplate',
                      l=o,
                      c=self.mmCallback(uiCB_contextSetValue,self,'puppet',n,v,_mode))
                      #c=lambda *a: LOCINATOR.cgmUI())             
            
        mUI.MelSpacer(_row,w=2)
        _row.layout()
    
    """
    #puppet settings ===========================================================================
    mmPuppetSettingsMenu = mc.menuItem(p = parent, l='Settings', subMenu=True)
    mmPuppetControlSettings = mPuppet.masterControl.controlSettings 
    
    for attr in ['visSub','visDirect','visRoot']:
        mi_tmpMenu = mc.menuItem(p = mmPuppetSettingsMenu, l=attr, subMenu=True)
        
        mc.menuItem(p = mi_tmpMenu, l="Show",
                    c = self.mmCallback(mPuppet.atUtils,'modules_settings_set',**{attr:1}))                    
        mc.menuItem(p = mi_tmpMenu, l="Hide",
                    c = self.mmCallback(mPuppet.atUtils,'modules_settings_set',**{attr:0}))
        
    for attr in ['skeleton','geo','proxy']:
        if mmPuppetControlSettings.hasAttr(attr):
            mi_tmpMenu = mc.menuItem(p = mmPuppetSettingsMenu, l=attr, subMenu=True)
            mi_collectionMenu = mUI.MelRadioMenuCollection()#build our collection instance			    
            mi_attr = cgmMeta.cgmAttr(mmPuppetControlSettings,attr)
            l_options = mi_attr.getEnum()
            for i,str_option in enumerate(l_options):
                if i == mi_attr.value:b_state = True
                else:b_state = False
                mi_collectionMenu.createButton(mi_tmpMenu,l=' %s '%str_option,
                                               c = self.mmCallback(mc.setAttr,"%s"%mi_attr.p_combinedName,i),
                                               rb = b_state )    
    """

#@cgmGEN.Timer
def get_context(self, addMirrors = False,**kws):
    try:
        _str_func='get_context'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        
        _keys = kws.keys()
        if 'children' in _keys:
            b_children = kws.get('children')
        else:
            b_children = bool(self.var_mrsContext_children.value)
        
        if 'siblings' in _keys:
            b_siblings = kws.get('siblings')
        else:
            b_siblings = bool(self.var_mrsContext_siblings.value)
            
        if 'mirror' in _keys:
            b_mirror = kws.get('mirror')
        else:
            b_mirror = bool(self.var_mrsContext_mirror.value)
            
        if 'context' in _keys:
            context = kws.get('context')
        else:
            context = self.var_mrsContext_mode.value
        
        if context == 'control' and b_siblings:
            if b_mirror or addMirrors:
                log.warning("Context control + siblings = part mode")
                context = 'part'
                b_siblings = False
                
        if context == 'puppet' and b_siblings:
            log.warning("Context puppet + siblings = scene mode")
            context = 'scene'
            b_siblings = False
        
        log.debug("|{0}| >> context: {1} | children: {2} | siblings: {3} | mirror: {4}".format(_str_func,context,b_children,b_siblings,b_mirror))
        
        #>>  Individual objects....===============================================================
        sel = mc.ls(sl=True)
        ml_sel = cgmMeta.asMeta(mc.ls(sl=True))
        self._sel = sel
        self._ml_sel = ml_sel
        self.mDat.d_context = {'mControls':[],
                             'mControlsMirror':[],
                             'mPuppets':[],
                             'mModules':[],
                             'b_puppetPart':False,
                             'mModulesMirror':[],
                             'mModulesBase':[]}
        
        
        res = []
        #------------------------------------------------------
        _cap = 5
        for i,mObj in enumerate(ml_sel):
            log.debug("|{0}| >> First pass check: {1}".format(_str_func,mObj))  
            if i > _cap:
                log.debug("|{0}| >> Large number of items selected, stopping processing at {1}".format(_str_func,i))              
                break
            #>>> Module --------------------------------------------------------------------------
            if mObj.getMessage('rigNull'):
                if mObj not in self.mDat.d_context['mControls']:
                    self.mDat.d_context['mControls'].append(mObj)
                    if context == 'control':
                        res.append(mObj)
    
                mRigNull = mObj.rigNull
                mModule = mRigNull.module
                
                if mModule not in self.mDat.d_context['mModules']:
                    self.mDat.d_context['mModules'].append(mModule)
                    if context == 'part':
                        res.append(mModule)
                
                if mModule.getMessage('modulePuppet'):
                    mPuppet = mModule.modulePuppet
                    if mPuppet not in self.mDat.d_context['mPuppets']:
                        self.mDat.d_context['mPuppets'].append(mPuppet)
                        if context == 'puppet':
                            res.append(mPuppet)
            elif mObj.getMessage('puppet'):
                mPuppet = mObj.puppet
                if mPuppet not in self.mDat.d_context['mPuppets']:
                    self.mDat.d_context['mPuppets'].append(mPuppet)
                    self.mDat.d_context['b_puppetPart'] = True
                    if context in ['puppet','scene']:
                        res.append(mPuppet)
                    else:
                        res.append(mObj)
                    #elif context == 'control':
                        #res.append(mObj)
    
        #before we get mirrors we're going to buffer our main modules so that mirror calls don't get screwy
        self.mDat.d_context['mModulesBase'] = copy.copy(self.mDat.d_context['mModules'])
        
    
        if context == 'scene':
            log.debug("|{0}| >> Scene mode bail...".format(_str_func))          
            self.mDat.d_context['mPuppets'] = self.mDat.dat['mPuppets']#r9Meta.getMetaNodes(mTypes = 'cgmRigPuppet')
            ls=[]
            """
            for mPuppet in self.mDat.d_context['mPuppets']:
                for mModule in mPuppet.atUtils('modules_get'):
                    if mModule not in self.mDat.d_context['mModules']:
                        self.mDat.d_context['mModules'].append(mModule)"""            
            self.mDat.d_context['mModules'] = self.dat['mModules']
            return self.mDat.d_context['mPuppets']
    
    
        #process...
        if b_siblings:
            log.debug(cgmGEN._str_subLine)        
            log.debug("|{0}| >> sibling check...".format(_str_func))
            if context == 'part':
                print(cgmGEN._str_hardBreak)        
                log.warning(cgmGEN._str_hardBreak)
                log.debug("|{0}| >> JOSH ... part siblings won't work right until you tag build profile for matching ".format(_str_func))
                log.warning(cgmGEN._str_hardBreak)        
                print(cgmGEN._str_hardBreak)                    
                
                res = []
                for mModule in self.mDat.d_context['mModules']:
                    res.append(mModule)
                    log.debug("|{0}| >> sibling check: {1}".format(_str_func,mModule))
                    mSib = self.mDat.dat[mModule]['mSibling']
                    if mSib:res.append(mSib)
                    """
                    for mSib in mModule.atUtils('siblings_get'):
                        if mSib not in res:
                            res.append(mSib)"""
                                
                self.mDat.d_context['mModules'].extend(res)#...push new data back
                
            elif context == 'control':
                res = []
                for mModule in self.mDat.d_context['mModules']:
                    log.debug("|{0}| >> sibling gathering for control | {1}".format(_str_func,mModule))
                    #res.extend(mModule.rigNull.msgList_get("controlsAll"))
                    #res.extend(mModule.rigNull.moduleSet.getMetaList())
                    res.extend(self.mDat.dat[mModule]['mControls'])
                self.mDat.d_context['mControls'] = res
                    
        if b_children:
            log.debug(cgmGEN._str_subLine)        
            log.debug("|{0}| >> Children check...".format(_str_func))
            
            if self.mDat.d_context['b_puppetPart']:
                for mPuppet in self.mDat.d_context['mPuppets']:
                    for mModule in self.mDat.dat[mPuppet]['mModules']:
                        self.mDat.d_context['mModules'].append(mModule)
                    """
                    for mModule in mPuppet.atUtils('modules_get'):
                        if mModule not in self.mDat.d_context['mModules']:
                            self.mDat.d_context['mModules'].append(mModule)"""            
    
            
            if context == 'part':
                for mModule in self.mDat.d_context['mModules']:
                    log.debug("|{0}| >> child check: {1}".format(_str_func,mModule))
                    for mChild in self.mDat.dat['mModules']['mChildren']:
                        if mChild not in self.mDat.d_context['mModules']:
                            self.mDat.d_context['mModules'].append(mChild)                        
                    """
                    ml_children = mModule.atUtils('moduleChildren_get')
                    for mChild in ml_children:
                        if mChild not in self.mDat.d_context['mModules']:
                            self.mDat.d_context['mModules'].append(mChild)"""
                #self.mDat.d_context['mModules'] = res
    
            """   
            elif context == 'puppet':
                log.warning('Puppet context with children is [parts] contextually. Changing for remainder of query.')
                context = 'part'
                res = []
                for mPuppet in self.mDat.d_context['mPuppets']:
                    res.extend(mPuppet.atUtils('modules_get'))
                self.mDat.d_context['mPuppets'] = res
                """
            
        if  b_mirror or addMirrors:
            log.debug(cgmGEN._str_subLine)        
            log.debug("|{0}| >> Context mirror check...".format(_str_func))
            if context == 'control':
                ml_mirror = []
                
                for mControl in self.mDat.d_context['mControls']:
                    if mControl.getMessage('mirrorControl'):
                        log.debug("|{0}| >> Found mirror for: {1}".format(_str_func,mControl))                    
                        ml_mirror.append(mControl.getMessage('mirrorControl',asMeta=True)[0])
                        
                if ml_mirror:
                    res.extend(ml_mirror)
                    self.mDat.d_context['mControls'].extend(ml_mirror)
                    self.mDat.d_context['mControlsMirror'].extend(ml_mirror)
                
            elif context == 'part':
                ml_mirrors =[]
                for mModule in self.mDat.d_context['mModules']:
                    mMirror = mModule.atUtils('mirror_get')
                    if mMirror:
                        log.debug("|{0}| >> Mirror: {1}".format(_str_func,mMirror))
                        if mMirror not in self.mDat.d_context['mModules']:
                            #res.append(mMirror)
                            ml_mirrors.append(mMirror)
                
                for mModule in ml_mirrors:
                    if mModule not in self.mDat.d_context['mModules']:
                        self.mDat.d_context['mModules'].append(mModule)
                self.mDat.d_context['mModulesMirror'] = ml_mirrors
                
        
        for mPuppet in self.mDat.d_context['mPuppets']:
            if not mPuppet.mClass == 'cgmRigPuppet':
                log.error("|{0}| >> Not a cgmRigPuppet: {1}".format(_str_func,mPuppet))
                self.mDat.d_context['mPuppets'].remove(mPuppet)
        
        if context in ['puppet','scene']:
            for mPuppet in self.mDat.d_context['mPuppets']:
                for mModule in mPuppet.atUtils('modules_get'):
                    if mModule not in self.mDat.d_context['mModules']:
                        self.mDat.d_context['mModules'].append(mModule)
                        
        for mModule in self.mDat.d_context['mModules']:
            if not mModule.mClass == 'cgmRigModule':
                log.error("|{0}| >> Not a rigModule: {1}".format(_str_func,mModule))
                self.mDat.d_context['mModules'].remove(mModule)
                

        #pprint.pprint(self.mDat.d_context)
        return res
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

#@cgmGEN.Timer
def get_contextualControls(self,mirrorQuery=False,**kws):
    try:
        _str_func='get_contextualControls'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        
        _keys = kws.keys()
        if 'children' in _keys:
            b_children = kws.get('children')
        else:
            b_children = bool(self.var_mrsContext_children.value)
        
        if 'siblings' in _keys:
            b_siblings = kws.get('siblings')
        else:
            b_siblings = bool(self.var_mrsContext_siblings.value)
            
        if 'mirror' in _keys:
            b_mirror = kws.get('mirror')
        else:
            b_mirror = bool(self.var_mrsContext_mirror.value)
            
        if 'context' in _keys:
            context = kws.get('context')
        else:
            context = self.var_mrsContext_mode.value
        
        if context == 'control' and b_siblings:
            if b_mirror:
                log.warning("Context control + siblings = part mode")
                context = 'part'
                b_siblings = False
                
        if context == 'puppet' and b_siblings:
            log.warning("Context puppet + siblings = scene mode")
            context = 'scene'   
        
        if context != 'control':
            log.debug("|{0}| >> Reaquiring control list...".format(_str_func))
            ls = []
            
            if self.mDat.d_context['b_puppetPart']:
                log.info("|{0}| >> puppetPart mode...".format(_str_func))
                for mPuppet in self.mDat.d_context['mPuppets']:
                    ls.extend([mObj.mNode for mObj in mPuppet.UTILS.controls_get(mPuppet)])
            
            if context == 'part':
                if mirrorQuery:
                    for mPart in self.mDat.d_context['mModules']:
                        ls.extend([mObj.mNode for mObj in mPart.UTILS.controls_get(mPart,'mirror')])            
                else:
                    for mPart in self.mDat.d_context['mModules']:
                        ls.extend(mPart.rigNull.moduleSet.getList())
            elif context in ['puppet','scene']:
                #if mirrorQuery:
                    #for mPuppet in self.mDat.d_context['mPuppets']:
                    #for mPart in mPuppet.UTILS.modules_get(mPuppet):
                    #  ls.extend([mObj.mNode for mObj in mPart.UTILS.controls_get(mPart,'mirror')])            
                for mPuppet in self.mDat.d_context['mPuppets']:
                    #_l = [mObj.mNode for mObj in mPuppet.UTILS.controls_get(mPuppet,walk=True)]
                    #ls.extend(_l)
                    ls.extend(mPuppet.puppetSet.getList())
                    #mPuppet.puppetSet.select()
                    #ls.extend(mc.ls(sl=True))
                    
            self.mDat.d_context['sControls'] = ls
        else:
            self.mDat.d_context['sControls'] = [mObj.mNode for mObj in self.mDat.d_context['mControls']]
            
        self.mDat.d_context['sControls'] = LISTS.get_noDuplicates(self.mDat.d_context['sControls'])
        self.mDat.d_context['mControls'] = cgmMeta.validateObjListArg(self.mDat.d_context['sControls'])
        return self.mDat.d_context['sControls']
    except Exception,err:
        pprint.pprint(self.mDat.d_context)
        cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

#@cgmGEN.Timer
def uiCB_contextualActionBAK(self, **kws):
    try:
        _str_func='cgmUICB_contextualAction'
        l_kws = []
        for k,v in kws.iteritems():
            l_kws.append("{0}:{1}".format(k,v))
        
        _mode = kws.pop('mode',False)
        _context = kws.get('context') or self.var_mrsContext_mode.value
        
        log.debug("|{0}| >> context: {1} | {2}".format(_str_func,_context,' | '.join(l_kws)))
        
        d_context = {}
        _mirrorQuery = False
        if _mode in ['mirrorPush','mirrorPull','symLeft','symRight','mirrorFlip','mirrorSelect','mirrorSelectOnly']:
            kws['addMirrors'] = True
            _mirrorQuery = True
            

        #res_context = get_context(self,**kws)
        res_context = self.mDat.context_get(addMirrors=_mirrorQuery,**d_contextSettings)
        
        #pprint.pprint(self.mDat.d_context)
        #return        
        if not res_context:
            return log.error("Nothing found in context: {0} ".format(_context))
        
        def endCall(self,report=True):
            mc.select(self._sel)
            if report:log.info("Context: {0} | mode: {1} | done.".format(_context, _mode))
            return 
        
        self.var_resetMode = cgmMeta.cgmOptionVar('cgmVar_ChannelResetMode', defaultValue = 0)
        _l_controls = get_contextualControls(self,_mirrorQuery,**kws)
        
        if _mode == 'report':
            log.info("Context: {0} | controls: {1}".format(_context, len(_l_controls)))
            for i,v in enumerate(res_context):
                log.info("[{0}] : {1}".format(i,v))
            #pprint.pprint(self.mDat.d_context['mModules'])
            log.debug(cgmGEN._str_subLine)
            return endCall(self)
        
        elif _mode == 'select':
            return  mc.select(_l_controls)
        
        elif _mode in ['selectFK','selectIK','selectIKEnd','selectSeg','selectDirect']:
            if _mode == 'selectFK':
                _tag = 'fk'
            elif _mode == 'selectIK':
                _tag = 'ik'
            elif _mode == 'selectIKEnd':
                _tag = 'ikEnd'
            elif _mode == 'selectSeg':
                _tag = 'segmentHandles'
            elif _mode == 'selectDirect':
                _tag = 'direct'
                
            l_new = []
            for mObj in self.mDat.d_context['mModules']:
                _l_buffer = mObj.atUtils('controls_getDat',_tag,listOnly=True)
                if _l_buffer:
                    l_new.extend([mHandle.mNode for mHandle in _l_buffer])
            
            if not l_new:
                return log.warning("Context: {0} | No controls found in mode: {1}".format(_context, _mode))
    
            return mc.select(l_new)        
        
        elif _mode in ['resetFK','resetIK','resetIKEnd','resetSeg','resetDirect']:
            if _mode == 'resetFK':
                _tag = 'fk'
            elif _mode == 'resetIK':
                _tag = 'ik'
            elif _mode == 'resetIKEnd':
                _tag = 'ikEnd'
            elif _mode == 'resetSeg':
                _tag = 'segmentHandles'
            elif _mode == 'resetDirect':
                _tag = 'direct'
                
            l_new = []
            for mObj in self.mDat.d_context['mModules']:
                _l_buffer = mObj.atUtils('controls_getDat',_tag,listOnly=True)
                if _l_buffer:
                    l_new.extend([mHandle.mNode for mHandle in _l_buffer])
            
            if not l_new:
                return log.warning("Context: {0} | No controls found in mode: {1}".format(_context, _mode))
    
                    
            mc.select(l_new)
            RIGGEN.reset_channels_fromMode(self.var_resetMode.value)
            return endCall(self)
            
        elif _mode in ['nextKey','prevKey']:
            l_keys = []
            if _mode == 'nextKey':
                for o in _l_controls:
                    l_keys.extend( SEARCH.get_key_indices_from(o,'next') )
                #mel.eval('NextKey;')
            elif _mode == 'prevKey':
                for o in _l_controls:
                    l_keys.extend( SEARCH.get_key_indices_from(o,'previous') )
            if l_keys:
                _key = min(l_keys)
                mc.currentTime(_key)
            else:
                log.error('No keys detected')
            return endCall(self)
        
        elif _mode in ['key','bdKey','reset','delete',]:
            mc.select(_l_controls)
            if _mode == 'reset':
                RIGGEN.reset_channels_fromMode(self.var_resetMode.value)
                #ml_resetChannels.main(**{'transformsOnly': self.var_resetMode.value})
            elif _mode == 'key':
                setKey('default')
            elif _mode == 'bdKey':
                setKey('breakdown')
            elif _mode == 'delete':
                deleteKey()
            return endCall(self)
        
        
        elif _mode in ['mirrorPush','mirrorPull',
                       'symLeft','symRight',
                       'mirrorFlip','mirrorSelect','mirrorSelectOnly']:
            log.debug(cgmGEN._str_subLine)
            mBaseModule = self.mDat.d_context['mModulesBase'][0]
            log.debug("|{0}| >> Mirroring. base: {1}".format(_str_func,mBaseModule))
            
            try:
                _primeAxis = self._ml_sel[0].getEnumValueString('mirrorSide')
                log.info("Prime axis from control: {0}".format(_primeAxis))
                
            except:
                if mBaseModule.hasAttr('cgmDirection'):
                    _primeAxis = mBaseModule.cgmDirection.capitalize()
                else:
                    _primeAxis = 'Centre'
                log.info("Prime axis from module: {0}".format(_primeAxis))
            
            if _mode == 'mirrorSelect':
                mc.select(_l_controls)
                return
            elif _mode == 'mirrorSelectOnly':
                l_sel = []
                if _context == 'control':
                    for mObj in  self.mDat.d_context['mControlsMirror']:
                        l_sel.append(mObj.mNode)
                elif _context == 'part':
                    #pprint.pprint( self.mDat.d_context['mModulesMirror'] )
                    #return
                    for mPart in self.mDat.d_context['mModulesMirror']:
                        l_sel.extend([mObj.mNode for mObj in mPart.UTILS.controls_get(mPart)])
                else:
                    return log.error("Context not supported: {0}".format(_context))
                
                if not l_sel:
                    return log.error("Nothing found in context".format(_context))

                mc.select(l_sel)
                return
            elif _mode == 'mirrorFlip':
                r9Anim.MirrorHierarchy().mirrorData(_l_controls,mode = '')
                return endCall(self)            
            elif _mode == 'mirrorPull':
                _dFlip = {'Left':'Right',
                          'Right':'Left'}
                
                _primeAxis = _dFlip.get(_primeAxis,_primeAxis)
                #mMirror = mBaseModule.atUtils('mirror_get')
                #if mMirror and mMirror.hasAttr('cgmDirection'):
                #    _primeAxis = mMirror.cgmDirection.capitalize()
                #else:
                #    _primeAxis = 'Centre'
                    
            elif _mode == 'mirrorPush':
                pass #...trying to just use first selected
                """
                if mBaseModule.hasAttr('cgmDirection'):
                    _primeAxis = mBaseModule.cgmDirection.capitalize()
                else:
                    _primeAxis = 'Centre'"""
            elif _mode == 'symLeft':
                _primeAxis = 'Left'
            else:
                _primeAxis = 'Right'
                
            log.debug("|{0}| >> Mirror {1} | primeAxis: {2}.".format(_str_func,_mode,_primeAxis))
    
            r9Anim.MirrorHierarchy().makeSymmetrical(_l_controls,
                                                     mode = '',
                                                     primeAxis = _primeAxis )        
            return endCall(self)
                
        elif _mode == 'mirrorVerify':
            log.info("Context: {0} | Mirror verify".format(_context))
            if not self.mDat.d_context['mPuppets']:
                return log.error("No puppets detected".format(_mode))
            for mPuppet in self.mDat.d_context['mPuppets']:
                mPuppet.atUtils('mirror_verify')
            return endCall(self)
        
        elif _mode == 'upToDate':
            log.info("Context: {0} | {1}".format(_context,_mode))
            if not self.mDat.d_context['mPuppets']:
                return log.error("No puppets detected".format(_mode))
            for mPuppet in self.mDat.d_context['mPuppets']:
                mPuppet.atUtils('is_upToDate',True)
            return endCall(self)
        
        elif _mode == 'tweenDrag':
            mc.select(_l_controls)
            return ml_breakdownDragger.drag()
    
        elif _mode in ['tweenNext','tweenPrev','tweenAverage']:
            v_tween = kws.get('tweenValue', None)
            if v_tween is None:
                try:v_tween = self.cgmUIFF_tweenBase.getValue()
                except:pass
                if not v_tween:
                    return log.error("No tween value detected".format(_mode))
            log.info("Context: {0} | {1} | tweenValue: {2}".format(_context,_mode,v_tween))
            mc.select(_l_controls)
            
            if _mode == 'tweenNext':
                ml_mode = 'next'
            elif _mode == 'tweenPrev':
                ml_mode = 'previous'
            else:
                ml_mode = 'average'
                
            ml_breakdown.weightBreakdownStep(ml_mode,v_tween)
            
            return endCall(self)
        
        elif _mode in ['holdCurrent','holdAverage','holdPrev','holdNext']:
            mc.select(_l_controls)
            
            if _mode == 'holdCurrent':
                ml_hold.current()
            elif _mode == 'holdAverage':
                ml_hold.average()
            elif _mode == 'holdPrev':
                ml_hold.previous()
            elif _mode == 'holdNext':
                ml_hold.next()
                
            return endCall(self)
        
        
        elif _mode in ['FKon','IKon','FKsnap','IKsnap','IKsnapAll',
                       'aimToFK','aimOn','aimOff','aimToIK','aimSnap']:
            log.info("Context: {0} | Switch call".format(_context))
            res = []
            if not self.mDat.d_context['mModules']:
                return log.error("No modules detected".format(_mode))
            for mModule in self.mDat.d_context['mModules']:
                res.append(mModule.atUtils('switchMode',_mode))
            
            if _mode in ['aimSnap','aimToIK','aimToFK']:#no reselect
                return res
            endCall(self,False)
            return res
            #sreturn mc.select(_l_controls)
            
        else:
            return log.error("Unknown contextual action: {0}".format(_mode))
        return 
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())


def uiCB_contextSetValue(self, attr=None,value=None, mode = None,**kws):
    _str_func='cgmUICB_settingsSet'
    log.debug("|{0}| >>  context: {1} | attr: {2} | value: {3} | mode: {4}".format(_str_func,mode,attr,value,mode)+ '-'*80)
    
    try:contextArg = self.__class__.TOOLNAME 
    except:contextArg = False
        
    log.debug(cgmGEN.logString_msg(_str_func,"contextArg: {0}".format(contextArg)))
    d_contextSettings = MRSANIMUTILS.get_contextDict(contextArg)
    d_contextSettings['contextPrefix'] = contextArg    
    
    self.mDat.context_get(**d_contextSettings)
    
    #pprint.pprint(self.mDat.d_context)
    
    if mode == 'moduleSettings':
        if not self.mDat.d_context['mModules']:
            return log.error("No modules found in context")
        for mModule in self.mDat.d_context['mModules']:
            try:ATTR.set(mModule.rigNull.settings.mNode, attr, value)
            except Exception,err:log.warning("Failed to set: {0} | value: {1} | mModule: {2} | {3}".format(attr,value,mModule,err))
    elif mode == 'puppetSettings':
        for mPuppet in self.mDat.d_context['mPuppets']:
            ATTR.set(mPuppet.masterControl.controlSettings.mNode, attr, value)
    elif mode == 'moduleVis':
        for mModule in self.mDat.d_context['mModules']:
            attr = "{0}_vis".format(mModule.get_partNameBase())
            try:ATTR.set(mModule.modulePuppet.masterControl.controlVis.mNode, attr, value)
            except Exception,err:
                log.info("attr: {0} | Switch call".format(attr))
                
    else:
        return log.error("Unknown contextualSetValue mode: {0}".format(mode))


def buildColumn_main(self,parent, asScroll = False):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """   
    if asScroll:
        _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUISubTemplate') 
    else:
        _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
    
    #buildFrame_puppet(self,_inside)
    buildFrame_MRSAnim(self,_inside)
    #buildFrame_MRSAnim(self,_inside)
    
    return _inside
    
def uiCB_load_selected(self, bypassAttrCheck = False):
    _str_func = 'cgmUICB_load_selected'  
    #self._ml_ = []
    self._mTransformTarget = False

    _sel = mc.ls(sl=True,type='transform')

    #Get our raw data
    if _sel:
        mNode = cgmMeta.validateObjArg(_sel[0])
        _short = mNode.p_nameBase            
        log.debug("|{0}| >> Target: {1}".format(_str_func, _short))
        self._mTransformTarget = mNode

        uiCB_updateTargetDisplay(self)
    else:
        log.warning("|{0}| >> Nothing selected.".format(_str_func))            
        uiCB_clear_loaded(self)

    #uiCB_updateFields(self)
    #self.cgmUIReport_do()
    #self.cgmUICB_updateScrollAttrList()

def uiCB_clear_loaded(self):
    _str_func = 'cgmUICB_clear_loaded'  
    self._mTransformTarget = False
    self.cgmUITF_objLoad(edit=True, l='',en=False)

def uiCB_tweenSliderDrop(self):
    _str_func='cgmUICB_tweenSliderDrop'
    """
    _context = self.var_mrsContext_mode.value
    
    #log.debug("|{0}| >> context: {1} | {2}".format(_str_func,_context,' | '.join(l_kws)))
    
    v_tween = self.cgmUISlider_tween.getValue()
    if v_tween >= 0.0:
        mode = 'tweenNext'
    else:
        mode = 'tweenPrev'
        
    uiCB_contextualAction(self,**{'mode':mode,'tweenValue':v_tween})
    """

    if self.is_dragging_tween:
        self.is_dragging_tween = False
        mc.undoInfo(closeChunk=True)

    log.info("Last drag value: {0}".format(self.cgmUISlider_tween.getValue()))
    self.cgmUISlider_tween.setValue(0)
    self.keySel = {}#...clear thiss
    if not self.mDat._sel:
        return #log.error("Nothing in context")    
    mc.select(self._sel)
    #if report:log.info("Context: {0} | mode: {1} | done.".format(_context, _mode))
    return     

def uiCB_tweenSlider(self):
    _str_func='cgmUICB_tweenSlider'
    
    if not self.is_dragging_tween:
        mc.undoInfo(openChunk=True)
        self._sel = mc.ls(sl=True)
        self.is_dragging_tween = True        

    try:self.keySel
    except:self.keySel = {}
    
    if not self.keySel:
        uiCB_contextualAction(self,mode='select')
        
        self.keySel = ml_utilities.KeySelection()
        if self.keySel.selectedKeys():
            pass
        elif self.keySel.visibleInGraphEditor():
            self.keySel.setKeyframe()
        elif self.keySel.keyedChannels():
            self.keySel.setKeyframe()
        
        if not self.keySel.curves:
            return
        
        #setup tangent type
        itt,ott = ml_utilities.getHoldTangentType()
        
        self.time = dict()
        self.value = dict()
        self.next = dict()
        self.prev = dict()
        self.average = dict()
        
        for curve in self.keySel.curves:
            if self.keySel.selected:
                self.time[curve] = mc.keyframe(curve, query=True, timeChange=True, sl=True)
                self.value[curve] = mc.keyframe(curve, query=True, valueChange=True, sl=True)
            else:
                self.time[curve] = self.keySel.time
                self.value[curve] = mc.keyframe(curve, time=self.keySel.time, query=True, valueChange=True)
                
            self.next[curve] = list()
            self.prev[curve] = list()
            self.average[curve] = list()
            
            for i in self.time[curve]:
                next = mc.findKeyframe(curve, time=(i,), which='next')
                prev = mc.findKeyframe(curve, time=(i,), which='previous')
                n = mc.keyframe(curve, time=(next,), query=True, valueChange=True)[0]
                p = mc.keyframe(curve, time=(prev,), query=True, valueChange=True)[0]
                
                self.next[curve].append(n)
                self.prev[curve].append(p)
                self.average[curve].append((n+p)/2)
                
                #set the tangents on this key, and the next and previous, so they flatten properly
                mc.keyTangent(curve, time=(i,), itt=itt, ott=ott)
                mc.keyTangent(curve, time=(next,), itt=itt)
                mc.keyTangent(curve, time=(prev,), ott=ott)

    if not self.mDat._sel:
        return     
    v_tween = self.cgmUISlider_tween.getValue()
    if v_tween > 0:
        for curve in self.keySel.curves:
            for i,v,n in zip(self.time[curve],self.value[curve],self.next[curve]):
                mc.keyframe(curve, time=(i,), valueChange=v+((n-v)*v_tween))
    elif v_tween <0:
        for curve in self.keySel.curves:
            for i,v,p in zip(self.time[curve],self.value[curve],self.prev[curve]):
                mc.keyframe(curve, time=(i,), valueChange=v+((p-v)*(-1*v_tween)))
    
    #log.info(self.cgmUISlider_tween.getValue())
    
     
def uiCB_updateTargetDisplay(self):
    _str_func = 'cgmUICB_updateTargetDisplay'  
    #self.cgmUIScrollList_parents.clear()

    if not self._mTransformTarget:
        log.info("|{0}| >> No target.".format(_str_func))                        
        #No obj
        self.cgmUITF_objLoad(edit=True, l='',en=False)
        self._mGroup = False

        #for o in self._l_toEnable:
            #o(e=True, en=False)
        return
    
    _short = self._mTransformTarget.p_nameBase
    self.cgmUITF_objLoad(edit=True, ann=_short)
    
    if len(_short)>20:
        _short = _short[:20]+"..."
    self.cgmUITF_objLoad(edit=True, l=_short)   
    
    self.cgmUITF_objLoad(edit=True, en=True)
    
    return


def setKey(keyModeOverride = None):
    _str_func = "setKey"        
    KeyTypeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
    KeyModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)	
    selection = False

    log.debug("|{0}| >> keyType: {1} | keyMode: {2} |  keyModeOverride: {3}".format(_str_func,KeyTypeOptionVar.value,KeyModeOptionVar.value,keyModeOverride))  

    if not KeyModeOptionVar.value:#This is default maya keying mode
        selection = mc.ls(sl=True) or []
        if not selection:
            return log.error("Nothing selected,can't key.")


        """if not KeyTypeOptionVar.value:
            mc.setKeyframe(selection)
        else:
            mc.setKeyframe(breakdown = True)"""
    else:#Let's check the channel box for objects
        selection = SEARCH.get_selectedFromChannelBox(False) or []
        if not selection:
            log.debug("|{0}| >> No channel box selection. ".format(_str_func))
            selection = mc.ls(sl=True) or []

    if not selection:
        return log.warning('cgmPuppetKey.setKey>>> Nothing selected!')

    if keyModeOverride:
        log.debug("|{0}| >> Key override mode. ".format(_str_func))
        if keyModeOverride== 'breakdown':
            mc.setKeyframe(selection,breakdown = True)     
        else:
            mc.setKeyframe(selection)

    else:
        if not KeyTypeOptionVar.value:
            mc.setKeyframe(selection)
        else:
            mc.setKeyframe(selection,breakdown = True)     

def deleteKey():
    KeyTypeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
    KeyModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)	

    if not KeyModeOptionVar.value:#This is default maya keying mode
        selection = mc.ls(sl=True) or []
        if not selection:
            return log.warning('cgmPuppetKey.deleteKey>>> Nothing l_selected!')

        mel.eval('timeSliderClearKey;')

    else:#Let's check the channel box for objects
        selection = SEARCH.get_selectedFromChannelBox(False) or []
        if not selection:
            selection = mc.ls(sl=True) or []
            if not selection:
                return log.warning('cgmPuppetKey.deleteKey>>> Nothing l_selected!')

        mel.eval('timeSliderClearKey;') 
        
def uiCB_bufferDat(self,update=True):
    _str_func='uiCB_bufferDat'
    log.info(cgmGEN.logString_msg(_str_func))
    reload(MRSANIMUTILS)
    self.mDat = MRSANIMUTILS.get_sharedDatObject()#MRSANIMUTILS.MRSDAT
        
def uiCB_resetSliderDrop(self):
    _str_func='cgmUICB_resetSliderDrop'
    """
    _context = self.var_mrsContext_mode.value
    
    #log.debug("|{0}| >> context: {1} | {2}".format(_str_func,_context,' | '.join(l_kws)))
    
    v_tween = self.cgmUISlider_tween.getValue()
    if v_tween >= 0.0:
        mode = 'tweenNext'
    else:
        mode = 'tweenPrev'
        
    uiCB_contextualAction(self,**{'mode':mode,'tweenValue':v_tween})
    """
    mc.undoInfo(closeChunk=True)
    if self.b_autoKey:mc.autoKeyframe(state=True)
    self.cgmUISlider_reset.setValue(0)
    #pprint.pprint(self.d_resetDat)
    self.d_resetDat = {}#...clear thiss
    if not self.mDat._sel:
        return
    mc.select(self.mDat._sel)
    #if report:log.info("Context: {0} | mode: {1} | done.".format(_context, _mode))
    return     
    
#@cgmGEN.Timer
def uiCB_resetSlider(self):
    _str_func='cgmUICB_tweenSlider'
    
    try:self.d_resetDat
    except:
        self.d_resetDat = {}
        self.b_autoKey = mc.autoKeyframe(q=True,state=True)
    
    if not self.d_resetDat:
        mc.undoInfo(openChunk=True)
        if self.b_autoKey:mc.autoKeyframe(state=False)
        
        #uiCB_contextualAction(self,mode='select')
        _ml_controls = uiCB_contextualAction(self,mode='simpleRes')#self.mDat.context_get(mirrorQuery=_mirrorQuery,**kws)
        _selAttrs = SEARCH.get_selectedFromChannelBox(True)
        
        for mCtrl in _ml_controls:
            if _selAttrs:
                attrs = _selAttrs
                
            else:
                attrs = mc.listAttr(mCtrl.mNode, keyable=True, unlocked=True) or False
                
            self.d_resetDat[mCtrl] = {}
            _short = mCtrl.mNode
            for a in attrs:
                if a in ['visibility']:
                    continue
                try:
                    _d = ATTR.get_default(_short,a) or 0
                    _v = ATTR.get(mCtrl.mNode,a)
                    self.d_resetDat[mCtrl][a] = {'default':_d,
                                                 'value':_v}
                except Exception,err:
                    pass
                
        
    if not self.mDat._sel:
        return
    
    v_reset = self.cgmUISlider_reset.getValue()
    #log.info("value: {0}".format(v_reset))
    
    for mCtrl,aDat in self.d_resetDat.iteritems():
        for a,vDat in aDat.iteritems():
            try:
                
                #print("{0} | {1} | {2}".format(mCtrl.mNode,a,vDat['default']))
                current = vDat['value']
                setValue = current + ((vDat['default'] - current)*v_reset)
                #ATTR.set(mCtrl.mNode,a,setValue)
                mCtrl.__setattr__(a,setValue)
            except Exception,err:
                log.error("Attr fail: {0}.{1}".format(mCtrl,a))
                self.d_resetDat[mCtrl].pop(a)
                
            
#==============================================================================================
#Marking menu
#==============================================================================================
#@cgmGEN.Timer
def mmUI_radial(self,parent):
    _str_func = "bUI_radial" 
    self.mDat = MRSANIMUTILS.get_sharedDatObject()#MRSANIMUTILS.MRSDAT
    
    
    mc.menuItem(parent = parent,
                l = 'Select Last Context',
                #c = self.mmCallback(self.mDat.select_lastContext),
                c = lambda *x:self.mDat.select_lastContext(),
                rp = 'W',
                )     
    
    #====================================================================		
    #mc.menu(parent,e = True, deleteAllItems = True)
    
    #self._ml_objList = cgmMeta.validateObjListArg(self._l_sel,'cgmObject',True)
    #log.debug("|{0}| >> mObjs: {1}".format(_str_func, self._ml_objList))                

    #self._ml_modules = []
    #self._l_modules = []
    #self._l_puppets = []
    #self._ml_puppets = []
    #_optionVar_val_moduleOn = self.var_PuppetMMBuildModule.value
    #_optionVar_val_puppetOn = self.var_PuppetMMBuildPuppet.value
       
    #>>Radial --------------------------------------------------------------------------------------------
    #mc.menuItem(parent = parent,
                #en = self._b_sel,
                #l = 'Mirror Selected (WIP)',
                #c = self.mmCallback(mmFunc_test,self),
                #rp = 'SW',
                #) 
#@cgmGEN.Timer
def mmUI_optionMenu(self, parent):
    return
    _optionVar_val_moduleOn = self.var_PuppetMMBuildModule.value
    _optionVar_val_puppetOn = self.var_PuppetMMBuildPuppet.value    
    
    uiBuildMenus = mc.menuItem(parent = parent, subMenu = True,
                               l = 'Build Menus')
    
    mc.menuItem(parent = uiBuildMenus,
                l = 'Module',
                c = self.mmCallback(self.var_PuppetMMBuildModule.setValue, not _optionVar_val_moduleOn),
                cb = _optionVar_val_moduleOn)
    mc.menuItem(parent = uiBuildMenus,
                l = 'Puppet',
                c = self.mmCallback(self.var_PuppetMMBuildPuppet.setValue, not _optionVar_val_puppetOn),
                cb = _optionVar_val_puppetOn)    
    
#@cgmGEN.Timer
def mmUI_lower(self,parent):
    """
    Create the UI
    """
    _str_func = 'bUI_lower'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    
    #_optionVar_val_moduleOn = self.var_PuppetMMBuildModule.value
    #_optionVar_val_puppetOn = self.var_PuppetMMBuildPuppet.value  
    """
    try:self.var_mrsContext_mode
    except:self.var_mrsContext_mode = cgmMeta.cgmOptionVar('cgmVar_mrsContext_mode',
                                                      defaultValue = _l_contexts[0])
    try:self.var_mrsContext_time
    except:self.var_mrsContext_time = cgmMeta.cgmOptionVar('cgmVar_mrsContext_time',
                                                      defaultValue = 'current')
    try:self.var_mrsContext_keys
    except:self.var_mrsContext_keys = cgmMeta.cgmOptionVar('cgmVar_mrsContext_keys',
                                                      defaultValue = 'each')    
    """
    
    
    #Change space menu
    DYNPARENTTOOL.uiMenu_changeSpace(self,parent,False,{'contextTime':'current','contextKeys':'each'},Callback=self.mmCallback)

    #>>> Control ==========================================================================================    
    mmUI_controls(self,parent)
    mmUI_part(self,parent)
    mmUI_puppet(self,parent)
    
    mc.menuItem(parent = parent,en=False,
                l='---------------',)
    mc.menuItem(parent = parent,
                l='Open UI',
                c=lambda *a: mc.evalDeferred(ui))
    
    mc.menuItem(parent = parent,
                l='Test destroy',
                c=lambda *a: self.mmCallback(pprint.pprint,'hello'))
    return
        
    #>>> Module ==========================================================================================    
    if _optionVar_val_moduleOn and self._ml_modules:
        bUI_moduleSection(self,parent)
    
    #>>> Puppet ==========================================================================================    
    if _optionVar_val_puppetOn and self._l_puppets:
        bUI_puppetSection(self,parent)
    
    """
    mc.menuItem(p=parent,l = "-"*25,en = False)    
    mc.menuItem(parent = parent,
                l='MRS - WIP',
                c=lambda *a: mc.evalDeferred(TOOLCALLS.mrsUI)) """   
    



def mmFunc_test(self):
    uiCB_contextualAction(self, **{'mode':'report',
                                     'context':'control',
                                     'mirror':False,
                                     'children':False,
                                     'siblings':False})
            

#@cgmGEN.Timer
def mmUI_controls(self,parent = None):
    _str_func = 'mmUI_controls'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    
    mc.menuItem(p=parent,l="-- Controls --",en=False)
    _context = 'control'
    _contextTime = 'current'
    
    #Mirror =============================================================================
    d_setup = {'Add to selection':{'mode':'mirrorSelect'},
               'Select Only':{'mode':'mirrorSelectOnly'},
               'Push':{'mode':'mirrorPush'},
               'Pull':{'mode':'mirrorPull'},
               'SymLeft':{'mode':'symLeft'},
               'SymRight':{'mode':'symRight'},
               'Flip':{'mode':'mirrorFlip'}}
    
    _mirror = mc.menuItem(p=parent,l="Mirror",subMenu=True)

    for m in ['Add to selection','Select Only','Push','Pull','SymLeft','SymRight','Flip']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'contextMode':_context,
                  'contextMirror':_d.get('mirror',False),
                  'contextChildren':_d.get('children',False),
                  'contextTime':_contextTime,                  
                  'contextSiblings':_d.get('siblings',False)}
        
        mc.menuItem(p=_mirror,l=m,
                    c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                )
    return

#@cgmGEN.Timer
def mmUI_puppet(self,parent = None):
    _str_func = 'mmUI_part'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    
    mc.menuItem(p=parent,l="-- Puppet --",en=False)
    _context = 'puppet'
    _contextTime = 'current'
    self.mDat = MRSANIMUTILS.get_sharedDatObject()#MRSANIMUTILS.MRSDAT

    
    #Basic =============================================================================
    d_setup = {'Select':{'mode':'select'},
               'Key':{'mode':'key'},
               'bdKey':{'mode':'bdKey'},
               'Reset':{'mode':'reset'},
               'Next Key':{'mode':'nextKey'},
               'Prev Key':{'mode':'prevKey'},
               
               }
    
    for m in ['Select','Key','bdKey','Reset','Next Key','Prev Key']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'contextMode':_context,
                  'contextMirror':False,#_d.get('mirror',False),
                  'contextChildren':False,#_d.get('children',False),
                  'contextTime':_contextTime,                  
                  'contextSiblings':False,#_d.get('siblings',False)}
                  }
        
        mc.menuItem(p=parent,l=m,
                    c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                )
        
    #Mirror =============================================================================
    d_setup = {'Push':{'mode':'mirrorPush'},
               'Pull':{'mode':'mirrorPull'},
               'SymLeft':{'mode':'symLeft'},
               'SymRight':{'mode':'symRight'},
               'Flip':{'mode':'mirrorFlip'}}
    
    _mirror = mc.menuItem(p=parent,l="Mirror",subMenu=True)

    for m in ['Push','Pull','SymLeft','SymRight','Flip']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'contextMode':_context,
                  'contextTime':_contextTime,                  
                  'contextMirror':_d.get('mirror',False),
                  'contextChildren':_d.get('children',False),
                  'contextSiblings':_d.get('siblings',False)}
        
        mc.menuItem(p=_mirror,l=m,
                    c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                )    
        
    #Toggles ===============================================================================
    _toggle = mc.menuItem(p=parent,l="Toggle",subMenu=True)
    
    l_settings = ['visSub','visDirect','visRoot']
    l_enums = ['skeleton','geo','proxy']

    for n in l_settings + l_enums:
        _sub = mc.menuItem(p=_toggle,l=n,subMenu=True)
        if n in l_settings:
            l_options = ['hide','show']
            _mode = 'moduleSettings'
        else:
            l_options = ['off','lock','on']
            _mode = 'puppetSettings'        
        _d_tmp = {'contextMode':_context,
                  'contextTime':_contextTime,                  
                  'contextMirror':False,
                  'contextChildren':False,
                  'contextSiblings':False}                  
        for v,o in enumerate(l_options):
            mc.menuItem(p=_sub,l=o,
                        c=self.mmCallback(uiCB_contextSetValue,self,n,v,_mode,**_d_tmp))
        
        """
        if n in l_settings:
            l_options = ['hide','show']
            _mode = 'moduleSettings'
        else:
            l_options = ['off','lock','on']
            _mode = 'puppetSettings'
        """    
    

    
#@cgmGEN.Timer
def mmUI_part(self,parent = None):
    _str_func = 'mmUI_part'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    
    mc.menuItem(p=parent,l="-- Part --",en=False)
    _context = 'part'
    _contextTime = 'current'
    
    #Switch =============================================================================
    _select = mc.menuItem(p=parent,l="Switch",subMenu=True)

    for m in ['FKon','FKsnap','IKon','IKsnap','IKsnapAll',
              'aimToFK','aimOn','aimOff','aimToIK','aimSnap']:
        #_d = d_setup[m]
        _d_tmp = {'mode':m,
                  'contextMode':_context,
                  'contextTime':_contextTime,                  
                  'contextMirror':False,
                  'contextChildren':False,
                  'contextSiblings':False}

        mc.menuItem(p=_select,l=m,
                    c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp))
        
    #Basic =============================================================================
    d_setup = {'Key':{'mode':'key'},
               'bdKey':{'mode':'bdKey'},
               'Reset':{'mode':'reset'},
               'Tween':{'mode':'tweenDrag'},
               'all':{'mode':'select'},
               'add mirror':{'mode':'mirrorSelect'},
               'mirror only':{'mode':'mirrorSelectOnly'},
               'fk':{'mode':'selectFK'},
               'ik':{'mode':'selectIK'},
               'ikEnd':{'mode':'selectIKEnd'},
               'seg':{'mode':'selectSeg'},
               'direct':{'mode':'selectDirect'},
               'Push':{'mode':'mirrorPush'},
               'Pull':{'mode':'mirrorPull'},
               'SymLeft':{'mode':'symLeft'},
               'SymRight':{'mode':'symRight'},
               'Flip':{'mode':'mirrorFlip'}               
               #'Next Key':{'mode':'nextKey'},
               #'Prev Key':{'mode':'prevKey'},
               
               }
    
    for m in ['Key','bdKey','Reset','Tween']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'contextMode':_context,
                  'contextTime':_contextTime,
                  'contextMirror':_d.get('mirror',False),
                  'contextChildren':_d.get('children',False),
                  'contextSiblings':_d.get('siblings',False)}
        
        mc.menuItem(p=parent,l=m,
                    c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                )


    #Select =============================================================================
    """d_setup = {'all':{'mode':'select'},
               'add mirror':{'mode':'mirrorSelect'},
               'mirror only':{'mode':'mirrorSelectOnly'},
               'fk':{'mode':'selectFK'},
               'ik':{'mode':'selectIK'},
               'ikEnd':{'mode':'selectIKEnd'},
               'seg':{'mode':'selectSeg'},
               'direct':{'mode':'selectDirect'},}"""

    ['select','selectFK','selectIK','selectIKEnd','selectSeg','selectDirect']
    _select = mc.menuItem(p=parent,l="Select",subMenu=True)
    
    for m in ['all','add mirror','mirror only','fk','ik','ikEnd','seg','direct']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'contextMode':_context,
                  'contextTime':_contextTime,                  
                  'contextMirror':_d.get('mirror',False),
                  'contextChildren':_d.get('children',False),
                  'contextSiblings':_d.get('siblings',False)}
        
        mc.menuItem(p=_select,l=m,
                    c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                )

    #Mirror =============================================================================
    """d_setup = {'Push':{'mode':'mirrorPush'},
               'Pull':{'mode':'mirrorPull'},
               'SymLeft':{'mode':'symLeft'},
               'SymRight':{'mode':'symRight'},
               'Flip':{'mode':'mirrorFlip'}}"""
    
    _mirror = mc.menuItem(p=parent,l="Mirror",subMenu=True)

    for m in ['Push','Pull','SymLeft','SymRight','Flip']:
        _d = d_setup.get(m)
        _d_tmp = {'mode':_d['mode'],
                  'contextMode':_context,
                  'contextTime':_contextTime,                  
                  'contextMirror':True,
                  'contextChildren':_d.get('children',False),
                  'contextSiblings':_d.get('siblings',False)}
        
        mc.menuItem(p=_mirror,l=m,
                    c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                )
        
    #Toggle --------------------------------------------------------------------------------
    _toggle = mc.menuItem(p=parent,l="Toggle",subMenu=True)
    
    l_settings = ['visSub','visDirect','visRoot']
    #l_enums = ['skeleton','geo','proxy']

    for n in l_settings:
        _sub = mc.menuItem(p=_toggle,l=n,subMenu=True)
        _d_tmp = {'contextMode':_context,
                  'contextMirror':False,
                  'contextTime':_contextTime,                  
                  'contextChildren':False,
                  'contextSiblings':False}                  
        for v,o in enumerate(['hide','show']):
            mc.menuItem(p=_sub,l=o,
                        c=self.mmCallback(uiCB_contextSetValue,self,n,v,'moduleSettings',**_d_tmp))
        
        """
        if n in l_settings:
            l_options = ['hide','show']
            _mode = 'moduleSettings'
        else:
            l_options = ['off','lock','on']
            _mode = 'puppetSettings'
        """
        
    ###Children/Siblings ------------------------------------------------------------
    """
    _children = mc.menuItem(p=parent,l="Children",subMenu=True)
    mmUI_section(self,_children,'part',children=True)
    
    _siblings = mc.menuItem(p=parent,l="Siblings",subMenu=True)
    mmUI_section(self,_siblings,'part',siblings=True)"""
    
    
    
    for section in 'Children','Siblings':
        _sub = mc.menuItem(p=parent,l=section,subMenu=True)
        _children = False
        _siblings = False
        
        if section == 'Children':
            _children = True
        else:
            _siblings = True
        
        #Switch =============================================================================
        _select = mc.menuItem(p=_sub,l="Switch",subMenu=True)
    
        for m in ['FKon','FKsnap','IKon','IKsnap','IKsnapAll',
                  'aimToFK','aimOn','aimOff','aimToIK','aimSnap']:
            #_d = d_setup[m]
            _d_tmp = {'mode':m,
                      'contextMode':_context,
                      'contextTime':_contextTime,                  
                      'contextMirror':False,
                      'contextChildren':_children,
                      'contextSiblings':_siblings}
    
            mc.menuItem(p=_select,l=m,
                        c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp))
        
        #Basic ============================================================================
        for m in ['Key','bdKey','Reset','Tween']:
            _d = d_setup.get(m)
            _d_tmp = {'mode':_d.get('mode'),
                      'contextMode':_context,
                      'contextTime':_contextTime,
                      'contextMirror':_d.get('mirror',False),
                      'contextChildren':_children,
                      'contextSiblings':_siblings}
            
            mc.menuItem(p=_sub,l=m,
                        c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                    )
    
        
        #Select =============================================================================
        #['select','selectFK','selectIK','selectIKEnd','selectSeg','selectDirect']
        _select = mc.menuItem(p=_sub,l="Select",subMenu=True)
        
        for m in ['all','add mirror','mirror only','fk','ik','ikEnd','seg','direct']:
            _d = d_setup[m]
            _d_tmp = {'mode':_d['mode'],
                      'contextMode':_context,
                      'contextTime':_contextTime,                  
                      'contextMirror':_d.get('mirror',False),
                      'contextChildren':_d.get('children',_children),
                      'contextSiblings':_d.get('siblings',_siblings)}
            
            mc.menuItem(p=_select,l=m,
                        c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                    )
    
        #Mirror =============================================================================       
        _mirror = mc.menuItem(p=_sub,l="Mirror",subMenu=True)
    
        for m in ['Push','Pull','SymLeft','SymRight','Flip']:
            _d = d_setup[m]
            _d_tmp = {'mode':_d['mode'],
                      'contextMode':_context,
                      'contextTime':_contextTime,                  
                      'contextMirror':True,
                      'contextChildren':_d.get('children',_children),
                      'contextSiblings':_d.get('siblings',_siblings)}
            
            mc.menuItem(p=_mirror,l=m,
                        c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                    )
                
    
    
    return
   
        
    return


#@cgmGEN.Timer
def mmUI_section(self,parent = None, context= 'part', mirror = False, children = False, siblings=False):
    _str_func = 'mmUI_part'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    
    _context = 'part'

    #Basic =============================================================================
    d_setup = {'Key':{'mode':'key'},
               'bdKey':{'mode':'bdKey'},
               'Reset':{'mode':'reset'},
               'Tween':{'mode':'tweenDrag'},
               
               #'Next Key':{'mode':'nextKey'},
               #'Prev Key':{'mode':'prevKey'},
               
               }
    
    for m in ['Key','bdKey','Reset','Tween']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'contextMode':_context,
                  'contextMirror':mirror,
                  'contextChildren':children,
                  'contextSiblings':siblings,
                  }
        
        mc.menuItem(p=parent,l=m,
                    c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                )    
    
    #Select =============================================================================
    d_setup = {'all':{'mode':'select'},
               'mirror':{'mode':'mirrorSelect'},
               'mirror only':{'mode':'mirrorSelectOnly'},
               'fk':{'mode':'selectFK'},
               'ik':{'mode':'selectIK'},
               'ikEnd':{'mode':'selectIKEnd'},
               'seg':{'mode':'selectSeg'},
               'direct':{'mode':'selectDirect'},}

    ['select','selectFK','selectIK','selectIKEnd','selectSeg','selectDirect']
    _select = mc.menuItem(p=parent,l="Select",subMenu=True)
    
    for m in ['all','mirror','mirror only','fk','ik','ikEnd','seg','direct']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'contextMode':_context,
                  'contextMirror':mirror,
                  'contextChildren':children,
                  'contextSiblings':siblings,
                  }
        
        mc.menuItem(p=_select,l=m,
                    c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                )

    #Mirror =============================================================================
    d_setup = {'Select':{'mode':'mirrorSelect'},
               'Select Only':{'mode':'mirrorSelectOnly'},
               'Push':{'mode':'mirrorPush'},
               'Pull':{'mode':'mirrorPull'},
               'SymLeft':{'mode':'symLeft'},
               'SymRight':{'mode':'symRight'},
               'Flip':{'mode':'mirrorFlip'}}
    
    _mirror = mc.menuItem(p=parent,l="Mirror",subMenu=True)

    for m in ['Push','Pull','SymLeft','SymRight','Flip']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'contextMode':_context,
                  'contextMirror':True,
                  'contextChildren':children,
                  'contextSiblings':siblings,
                  }
        
        mc.menuItem(p=_mirror,l=m,
                    c=self.mmCallback(uiCB_contextualActionMM,self, **_d_tmp),
                )
        
    _toggle = mc.menuItem(p=parent,l="Toggle",subMenu=True)
    
    l_settings = ['visSub','visDirect','visRoot']
    #l_enums = ['skeleton','geo','proxy']

    for n in l_settings:
        _sub = mc.menuItem(p=_toggle,l=n,subMenu=True)
        _d_tmp = {'contextMode':_context,
                  'contextMirror':mirror,
                  'contextChildren':children,
                  'contextSiblings':siblings,}
        for v,o in enumerate(['hide','show']):
            mc.menuItem(p=_sub,l=o,
                        c=self.mmCallback(uiCB_contextSetValue,self,n,v,'moduleSettings',**_d_tmp))
    return







class mrsScrollList(mUI.BaseMelWidget):
    '''
    NOTE: you probably want to use the MelObjectScrollList instead!
    '''
    WIDGET_CMD = mc.iconTextScrollList
    KWARG_CHANGE_CB_NAME = 'sc'

    ALLOW_MULTI_SELECTION = True
    def __new__( cls, parent, *a, **kw ):
        if 'ams' not in kw and 'allowMultiSelection' not in kw:
            kw[ 'ams' ] = cls.ALLOW_MULTI_SELECTION
        return mUI.BaseMelWidget.__new__( cls, parent, *a, **kw )
    
    def __init__( self, parent, *a, **kw ):
        mUI.BaseMelWidget.__init__( self, parent, *a, **kw )
        self._appendCB = None
        self._items = []
        self._ml_scene = []
        self._ml_loaded = []
        self._l_strings = []
        self._l_itc = []
        self._d_itc =  {}
        self.filterField = None
        self.b_selCommandOn = True
        self.rebuild()
        self.cmd_select = None
        self(e=True, sc = self.selCommand)
        self.mDat = MRSANIMUTILS.get_sharedDatObject()#MRSANIMUTILS.MRSDAT
        
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
        
    def selectByBlock(self,Block):
        log.debug(cgmGEN.logString_start('selectByBlock'))        
        
        ml = VALID.listArg(Block)
        _cleared = False
        for Block in ml:
            if Block in self._ml_loaded:
                if not _cleared:
                    self.clearSelection()
                    _cleared = True
                self.selectByIdx(self._ml_loaded.index(Block))
                self.setHLC(Block)
            
    def getSelectedBlocks( self):
        log.debug(cgmGEN.logString_start('getSelectedBlocks'))                
        _indicesRaw = self.getSelectedIdxs()
        if not _indicesRaw:
            log.debug("Nothing selected")
            return []
        _indices = []
        for i in _indicesRaw:
            _indices.append(int(str(i).split('L')[0]))
        return [self._ml_loaded[i] for i in _indices]

    def append( self, item ):
        self( e=True, append=item )
        self._items.append(item)
        
    def appendItems( self, items ):
        for i in items: self.append( i )
        
    def allowMultiSelect( self, state ):
        self( e=True, ams=state )
    
    def report(self):
        log.debug(cgmGEN.logString_start('report'))                
        log.info("Scene: "+cgmGEN._str_subLine)
        for i,mObj in enumerate(self._ml_scene):
            print ("{0} | {1} | {2}".format(i,self._l_strings[i],mObj))
            
        log.info("Loaded "+cgmGEN._str_subLine)
        for i,mObj in enumerate(self._ml_loaded):
            print("{0} | {1}".format(i, mObj))
            
        pprint.pprint(self._ml_scene)
        
    def set_selCallBack(self,func,*args,**kws):
        log.debug(cgmGEN.logString_start('set_selCallBack'))                
        self.selCommand = func
        self.selArgs = args
        self.selkws = kws
    
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
            
    def selCommand(self):
        log.debug(cgmGEN.logString_start('selCommand'))
        l_indices = self.getSelectedIdxs()
        mBlock = self.getSelectedBlocks()
        if mBlock:
            self.setHLC(mBlock[0])
            pprint.pprint(mBlock)
            self.mDat._ml_listNodes = mBlock
        if self.b_selCommandOn and self.cmd_select:
            if len(l_indices)<=1:
                return self.cmd_select()
        return False
    
    def rebuild( self ):
        _str_func = 'rebuild'
        self.mDat = MRSANIMUTILS.get_sharedDatObject()#MRSANIMUTILS.MRSDAT
        
        log.debug(cgmGEN.logString_start(_str_func))
        self.b_selCommandOn = False
        ml_sel = self.getSelectedBlocks()
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
        _ml,_l_strings = BLOCKGEN.get_uiModuleScollList_dat(showSide=1,presOnly=1)
        
        self._ml_scene = _ml
        self._l_itc = []
        
        d_colors = {'left':[.4,.4,1],
                    'right':[.9,.2,.2],
                    'center':[.8,.8,0]}
        
        def getString(pre,string):
            i = 1
            _check = ''.join([pre,string])
            while _check in self._l_strings and i < 100:
                _check = ''.join([pre,string,' | NAMEMATCH [{0}]'.format(i)])
                i +=1
            return _check
        
        def get_side(mNode):
            _cgmDirection = mNode.getMayaAttr('cgmDirection')
            if _cgmDirection:
                if _cgmDirection[0].lower() == 'l':
                    return 'left'
                return 'right'
            return 'center'
        
        for i,mBlock in enumerate(_ml):
            _arg = get_side(mBlock)
            _color = d_colors.get(_arg,d_colors['center'])
            self._l_itc.append(_color)            
            self._d_itc[mBlock] = _color
            try:
                _str_base = mBlock.UTILS.get_uiString(mBlock)#mBlock.p_nameBase#
                #_modType = mBlock.getMayaAttr('moduleType')
                #if _modType:
                    #_str_base = _str_base + ' | [{0}]'.format(_modType)
            except:_str_base = 'FAIL | {0}'.format(mBlock.mNode)
            _pre = _l_strings[i]
            self._l_strings.append(getString(_pre,_str_base))
            
        self.update_display()
        
        if ml_sel:
            try:self.selectByBlock(ml_sel)
            except Exception,err:
                print err
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
                idx = self._l_strings.index(strEntry)
                _mBlock = self._ml_scene[idx]
                self._ml_loaded.append(_mBlock)
                #_color = d_state_colors.get(_mBlock.getEnumValueString('blockState'))
                _color = self._d_itc[_mBlock]
                try:self(e=1, itc = [(i+1,_color[0],_color[1],_color[2])])
                except:pass

        except Exception,err:
            log.error("|{0}| >> err: {1}".format(_str_func, err))  
            for a in err:
                log.error(a)
        
        #if l_items:
            #try:self.selectByValue(l_items)
            #except Exception,err:
                #print err
    
    def func_byBlock(self,func,*args,**kws):
        try:
            for mBlock in self.getSelectedBlocks():
                try:
                    res = func( *args, **kws )
                except Exception,err:
                    try:log.debug("Func: {0}".format(_func.__name__))
                    except:log.debug("Func: {0}".format(_func))
      
                    if args:
                        log.debug("args: {0}".format(args))
                    if kws:
                        log.debug("kws: {0}".format(kws))
                    for a in err.args:
                        log.debug(a)
                    raise Exception,err
        except:pass
        finally:
            self.rebuild()
            
    def selectCallBack(self,func=None,*args,**kws):
        print self.getSelectedBlocks()