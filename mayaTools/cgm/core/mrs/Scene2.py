import maya.cmds as mc
import maya.mel as mel
import pprint
from functools import partial
import os
import time
from datetime import datetime
import json

from shutil import copyfile
#import fnmatch
import cgm.lib.pyui as pyui
#import subprocess
import re
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.lib import asset_utils as ASSET
from cgm.core.tools import Project as Project
from cgm.core.mrs.lib import batch_utils as BATCH
from cgm.core import cgm_General as cgmGEN
from cgm.core.lib import math_utils as MATH
from cgm.core.mrs.lib import scene_utils as SCENEUTILS
from cgm.core.lib import skinDat as SKINDAT
import cgm.core.mrs.Builder as BUILDER
import cgm.core.lib.mayaBeOdd_utils as MAYABEODD
import cgm.core.cgmPy.validateArgs as VALID
import cgm.core.tools.Project as PROJECT

import Red9.core.Red9_General as r9General

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

import cgm.core.cgmPy.path_Utils as PATHS
import cgm.core.cgmPy.os_Utils as CGMOS

import cgm.images as cgmImages

mImagesPath = PATHS.Path(cgmImages.__path__[0])

global UI
UI = None
def ui_get():
    global UI
    if UI:
        log.info('cached...')
        UI.show()
        return UI
    return ui()

log_start = cgmGEN.logString_start
log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub

#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================
_d_ann = SCENEUTILS.d_annotations


#>>> Root settings =============================================================
__version__ = cgmGEN.__RELEASE
__toolname__ ='MRSScene'

_subLineBGC = [.75,.75,.75]
_l_directoryMask = ['meta','.mayaSwatches']

class ui(cgmUI.cgmGUI):
    '''
Animation Importer UI class.

Loads the Animation Importer UI.

| outputs AnimationImporter

example:
.. python::

    import cgm.core.mrs.Scene as SCENE
    x = SCENE.SceneUI()

    # returns loaded directory
    print x.directory

    # prints the names of all of the loaded assets
    print x.assetList
    '''

    WINDOW_NAME = 'cgmScene'
    DEFAULT_SIZE = 800, 400

    TOOLNAME = 'cgmScene'
    WINDOW_TITLE = '%s - %s'%(TOOLNAME,__version__)    
    reload(SCENEUTILS)

    def insert_init(self,*args,**kws):
        
        self.categoryList                = ["Character", "Environment", "Props"]
        self.categoryIndex               = 0

        self.subTypes                    = ['animation']
        self.subTypeIndex                = 0
        self.l_subTypesBase = []
        
        self.var_lastProject       = cgmMeta.cgmOptionVar("cgmVar_projectCurrent", varType = "string")
        self.var_lastAsset     = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_asset", varType = "string")
        self.var_lastAnim      = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_animation", varType = "string")
        self.var_lastVariation = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_variation", varType = "string")
        self.var_lastVersion   = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_version", varType = "string")
        self.var_showAllFiles           = cgmMeta.cgmOptionVar("cgmVar_sceneUI_show_all_files", defaultValue = 0)
        #self.var_removeNamespace        = cgmMeta.cgmOptionVar("cgmVar_sceneUI_remove_namespace", defaultValue = 0)
        #self.var_zeroRoot               = cgmMeta.cgmOptionVar("cgmVar_sceneUI_zero_root", defaultValue = 0)
        self.var_useMayaPy              = cgmMeta.cgmOptionVar("cgmVar_sceneUI_use_mayaPy", defaultValue = 0)
        self.var_categoryStore               = cgmMeta.cgmOptionVar("cgmVar_sceneUI_category", defaultValue = 0)
        self.var_subTypeStore                = cgmMeta.cgmOptionVar("cgmVar_sceneUI_subType", defaultValue = 0)
        self.var_alwaysSendReferenceFiles    = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_version", defaultValue = 0)
        self.var_showDirectories        = cgmMeta.cgmOptionVar("cgmVar_sceneUI_show_directories", defaultValue = 0)
        self.var_displayDetails         = cgmMeta.cgmOptionVar("cgmVar_sceneUI_display_details", defaultValue = 1)
        self.var_displayProject         = cgmMeta.cgmOptionVar("cgmVar_sceneUI_display_project", defaultValue = 1)
        
        #self.var_postEuler          = cgmMeta.cgmOptionVar("cgmVar_sceneUI_postEuler", defaultValue = 1)
        #self.var_postTangent     = cgmMeta.cgmOptionVar("cgmVar_sceneUI_postTangent", varType = "string", defaultValue='auto')
        #self.var_mayaFilePref     = cgmMeta.cgmOptionVar("cgmVar_sceneUI_mayaFilePref", varType = "string", defaultValue='ma')
        
        
        
        
        self.var_bakeSet                     = cgmMeta.cgmOptionVar('cgm_bake_set', varType="string",defaultValue = 'bake_tdSet')
        self.var_deleteSet                   = cgmMeta.cgmOptionVar('cgm_delete_set', varType="string",defaultValue = 'delete_tdSet')
        self.var_exportSet                   = cgmMeta.cgmOptionVar('cgm_export_set', varType="string",defaultValue = 'export_tdSet') 

        ## sizes
        self.__itemHeight                = 35
        self.__cw1                       = 125

        # UI elements
        self.assetList                   = None #pyui.SearchableList()
        self.subTypeSearchList           = None #pyui.SearchableList()
        self.variationList               = None #pyui.SearchableList()
        self.versionList                 = None #pyui.SearchableList()
        self.queueTSL                    = None #pyui.UIList()
        self.updateCB                    = None
        self.menuBarLayout               = None
        self.uiMenu_Projects             = None
        self.uiMenu_ToolsMenu            = None
        self.uiMenu_OptionsMenu          = None
        self.categoryBtn                 = None
        self.subTypeBtn                  = None
        self.exportQueueFrame            = None
        self.categoryMenu                = None
        self.categoryMenuItemList        = []
        self.subTypeMenuItemList         = []
        self.uList_sendToProject_version   = []
        self.uList_sendToProject_variant   = []
        self.d_subPops = {}
        self.assetRigMenuItemList        = []
        self.assetReferenceRigMenuItemList  = []
        self.uiPop_sendToProject_version = None
        self.uiPop_sendToProject_variant = None
        self.uiPop_sendToProject_sub = None
        self.displayProject = True
        self.mDat                     = None
        self.assetMetaData               = {}

        self.exportCommand               = ""

        self.cb_showAllFiles          = None
        #self.cb_removeNamespace       = None
        #self.cb_zeroRoot              = None
        self.cb_useMayaPy             = None
        self.cb_showDirectories       = None

        self.showDirectories             = self.var_showDirectories.getValue()
        self.displayDetails              = self.var_displayDetails.getValue()

        self.showAllFiles                = self.var_showAllFiles.getValue()
        #self.removeNamespace             = self.var_removeNamespace.getValue()
        #self.zeroRoot                    = self.var_zeroRoot.getValue()
        self.useMayaPy                   = self.var_useMayaPy.getValue()

        self.fileListMenuItems           = []
        self.batchExportItems            = []

        self.exportDirectory             = None

        self.v_bgc                       = [.6,.3,.3]
        
        
        #Project migration ---------------------------------------------------------------------------------------
        self.pathProject = None
        self.mDat = PROJECT.data()
        self.path_projectConfig = None
        
        self.var_project = cgmMeta.cgmOptionVar('cgmVar_projectCurrent',defaultValue = '')
        self.var_pathProject = cgmMeta.cgmOptionVar('cgmVar_projectPath',defaultValue = '')
        self.var_pathLastProject = cgmMeta.cgmOptionVar('cgmVar_projectLastPath',defaultValue = '')
        self.mPathList = PROJECT.pathList_project('cgmProjectPaths')
        self.d_tf = {}
        self.d_uiTypes = {}
        self.d_buttons = {}
        self.d_labels = {}        
        
        global UI
        UI = self

    def post_init(self,*args,**kws):
        if self.var_lastProject.getValue():
            self.LoadProject(self.var_lastProject.getValue())
        else:
            mPathList = cgmMeta.pathList('cgmProjectPaths')
            try:self.LoadProject(mPathList.mOptionVar.value[0])
            except:pass
    @property
    def directory(self):
        return self.directoryTF.getValue()

    @directory.setter
    def directory(self, directory):
        self.directoryTF.setValue( directory )

    @property
    def path_dir_category(self):
        return os.path.normpath(os.path.join( self.directory, self.category ))
    
    
    def report_selectedPaths(self):
        _str_func = 'report_selectedPaths'

        log.debug(log_start(_str_func))    
        
        log.info("Directory: {0}".format(self.directory))        
        log.info("Asset: {0}".format(self.path_asset))
        log.info("Subtype Dir: {0}".format(self.path_subTypeDir))                
        log.info("Subtype: {0}".format(self.path_subType))
        log.info("Variation: {0}".format(self.path_variationDirectory))
        log.info("Version: {0}".format(self.path_versionDirectory))
        
    def report_states(self):
        _str_func = 'report_selectedPaths'

        log.debug(log_start(_str_func))    
        
        log.info(log_sub(_str_func,'Options...'))
        log.info("Asset: {0}".format(self.category))     
        log.info("Subtype: {0}".format(self.selectedSubType))
        log.info("Variation: {0}".format(self.selectedVariation))        
        log.info("Version: {0}".format(self.selectedVersion))        
        
        log.info("File: {0}".format(self.versionFile))        
        
        
        
        log.info(log_sub(_str_func,'Paths...'))    
        
        log.info("Directory: {0}".format(self.directory))        
        log.info("Asset: {0}".format(self.path_asset))
        log.info("Subtype Dir: {0}".format(self.path_subTypeDir))        
        log.info("Subtype: {0}".format(self.path_subType))
        log.info("Variation: {0}".format(self.path_variationDirectory))
        log.info("Version: {0}".format(self.path_versionDirectory))
        
        log.info(log_sub(_str_func,'States...'))            
        log.info("hasSub: {0}".format(self.hasSub))
        log.info("hasVariant: {0}".format(self.hasVariant))
        log.info("hasNested: {0}".format(self.hasNested))
        log.info("hasSubTypes: {0}".format(self.hasSubTypes))

    @property
    def selectedAsset(self):
        return self.assetList['scrollList'].getSelectedItem()

    @property
    def path_asset(self):
        try:return os.path.normpath(os.path.join( self.path_dir_category, self.assetList['scrollList'].getSelectedItem() )) if self.assetList['scrollList'].getSelectedItem() else None
        except Exception,err:
            log.debug(err)
            return False        
    @property
    def selectedSubType(self):
        return self.subTypeSearchList['scrollList'].getSelectedItem()	

    @property
    def path_subTypeDir(self):
        try:
            return os.path.normpath(os.path.join( self.path_asset, self.subType ))
        except Exception,err:
            log.debug(err)
            return False
        
    @property
    def path_subType(self):
        try:
            if self.hasSub:
                if self.subTypeSearchList['scrollList'].getSelectedItem():
                    return os.path.normpath(os.path.join( self.path_asset, self.subType, self.subTypeSearchList['scrollList'].getSelectedItem() ))
                else:
                    return None
            else:
                return os.path.normpath(os.path.join( self.path_asset, self.subType ))
        except Exception,err:
            log.debug(err)
            return False
            

    @property
    def selectedVariation(self):
        return self.variationList['scrollList'].getSelectedItem()

    @property
    def path_variationDirectory(self):
        try:return os.path.normpath(os.path.join( self.path_subType, self.variationList['scrollList'].getSelectedItem() )) if self.variationList['scrollList'].getSelectedItem() else None
        except Exception,err:
            log.debug(err)
            return False
        
    @property
    def path_versionDirectory(self):
        try:
            
            if self.hasSub:
                if self.hasVariant:
                    return os.path.normpath(os.path.join( self.path_variationDirectory))
                else:
                    return os.path.normpath(os.path.join( self.path_subType))
            else:
                return os.path.normpath(os.path.join( self.path_subType))   
        except Exception,err:
            log.debug(err)
            return False            

    @property
    def selectedVersion(self):
        return self.versionList['scrollList'].getSelectedItem()

    @property
    def versionFile(self):
        if self.hasSub:
            if self.hasVariant:
                return os.path.normpath(os.path.join( self.path_variationDirectory, self.versionList['scrollList'].getSelectedItem() )) if self.versionList['scrollList'].getSelectedItem() else None
            else:
                return os.path.normpath(os.path.join( self.path_subType, self.versionList['scrollList'].getSelectedItem() )) if self.versionList['scrollList'].getSelectedItem() else None
        else:
            return os.path.normpath(os.path.join( self.path_subType, self.subTypeSearchList['scrollList'].getSelectedItem() )) if self.subTypeSearchList['scrollList'].getSelectedItem() else None

    @property
    def exportFileName(self):
        if self.hasSub:
            if self.hasVariant:
                return '{0}_{1}_{2}.fbx'.format(self.assetList['scrollList'].getSelectedItem(), self.subTypeSearchList['scrollList'].getSelectedItem(), self.variationList['scrollList'].getSelectedItem())
            else:
                return '{0}_{1}.fbx'.format(self.assetList['scrollList'].getSelectedItem(), self.subTypeSearchList['scrollList'].getSelectedItem())
        else:
            return '{0}_{1}.fbx'.format(self.assetList['scrollList'].getSelectedItem(), self.subType)


    @property
    def category(self):
        _str_func = 'category'
        log.debug(log_start(_str_func))        
        return self.categoryList[self.categoryIndex] if len(self.categoryList) > self.categoryIndex else self.categoryList[0]

    @property
    def subType(self):
        _str_func = 'subType'
        log.debug(log_start(_str_func))
        log.debug(log_msg(_str_func, self.subTypeIndex))
        return self.subTypes[min(self.subTypeIndex, len(self.subTypes)-1)] if self.subTypes else None

    @property
    def hasSub(self):
        _str_func = 'hasSub'

        _res = False
        _path  = self.path_subTypeDir
        if not _path:
            return False
        
        log.debug(log_start(_str_func))    
        log.debug(log_msg(_str_func, self.category))
        
        #path_subType = os.path.normpath(os.path.join( self.path_dir_category, self.category ))
        try:
            _dirs = CGMOS.get_lsFromPath(_path,'dir')
            for d in _l_directoryMask:
                try:_dirs = _dirs.remove(d)
                except:pass
        except Exception,err:
            log.error(log_msg(_str_func, err))
            return False
                
        if _dirs:
            _res = True
            
        #log.debug(log_start(_str_func))    
        #pprint.pprint(_dirs)
        log.debug(log_msg(_str_func,_res))
        return _res
        
        
        """
        try:
            r = self.mDat.assetType_get(self.category)['content'][self.subTypeIndex].get('hasSub', False)
            return r
        except:
            return True
            
        """
    @property
    def hasSubTypes(self):
        _str_func = 'hasSubTypes'

        _res = False
        _path = self.path_asset
        if not _path:
            return False
        
        log.debug(log_start(_str_func))    
        log.debug(log_msg(_str_func, self.subType))
        
        #path_subType = os.path.normpath(os.path.join( self.path_dir_category, self.category ))
        try:
            _dirs = CGMOS.get_lsFromPath(_path,'dir')
            for d in _l_directoryMask:
                try:_dirs = _dirs.remove(d)
                except:pass
        except Exception,err:
            log.error(log_msg(_str_func, err))
            return False
            
        if _dirs:
            _res = True
        
        log.debug(log_msg(_str_func,_res))
        return _res
    
    @property
    def hasNested(self):
        _str_func = 'hasSub'

        _res = False
        _path = self.path_subTypeDir
        if not _path:
            return False
        
        log.debug(log_start(_str_func))    
        log.debug(log_msg(_str_func, self.subType))
        
        #path_subType = os.path.normpath(os.path.join( self.path_dir_category, self.category ))
        try:
            _dirs = CGMOS.get_lsFromPath(_path,'dir')
            for d in _l_directoryMask:
                try:_dirs = _dirs.remove(d)
                except:pass
        except Exception,err:
            log.error(log_msg(_str_func, err))
            return False
            
        if _dirs:
            _res = True
        
        log.debug(log_msg(_str_func,_res))
        return _res
    
    @property
    def hasVariant(self):
        _str_func = 'hasVariant'
        _res = False
        
        try:
            _path_subType = self.path_subType
            log.debug(log_msg(_str_func, _path_subType))
        except:
            return _res
        
        log.debug(log_start(_str_func))
        log.debug(log_msg(_str_func, self.category))        
        try:
            if _path_subType:
                _dirs = CGMOS.get_lsFromPath(_path_subType,'dir')
                for d in _l_directoryMask:
                    try:_dirs = _dirs.remove(d)
                    except:pass
                        
                if _dirs:
                    _res = True
        except Exception,err:
            log.error(log_msg(_str_func, err))
            return False

        log.debug(log_msg(_str_func,_res))

        return _res
        """
        try:
            r = self.mDat.assetType_get(self.category)['content'][self.subTypeIndex].get('hasVariant', False)
            return r
        except:
            return True"""

    def HasSub(self, category, subType):
        _str_func = 'HasSub ||||||||| laksj;flaksjdfkl;'
        log.warning(log_start(_str_func))
        log.warning(log_msg(_str_func, self.category))
        
        try:
            hasSub = True
            for sub in self.mDat.assetType_get(category)['content']:
                if sub['n'] == subType:
                    hasSub = sub.get('hasSub', True)
            return hasSub
        except:
            return True

    def LoadOptions(self, *args):
        self.showAllFiles    = bool(self.var_showAllFiles.getValue())
        self.categoryIndex   = int(self.var_categoryStore.getValue())
        self.subTypeIndex    = int(self.var_subTypeStore.getValue())
        #self.removeNamespace = bool(self.var_removeNamespace.getValue())
        #self.zeroRoot        = bool(self.var_zeroRoot.getValue())
        self.useMayaPy       = bool(self.var_useMayaPy.getValue())
        self.showDirectories = bool(self.var_showDirectories.getValue())
        self.displayDetails  = bool(self.var_displayDetails.getValue())
        self.displayProject  = bool(self.var_displayProject.getValue())

        if self.cb_showAllFiles:
            self.cb_showAllFiles(e=True, checkBox = self.showAllFiles)
        #if self.cb_removeNamespace:
        #    self.cb_removeNamespace(e=True, checkBox = self.removeNamespace)
        #if self.cb_zeroRoot:
        #    self.cb_zeroRoot(e=True, checkBox = self.zeroRoot)

        self.SetSubType(self.subTypeIndex)
        self.buildMenu_subTypes()
        self.SetCategory(self.categoryIndex)
        self.LoadPreviousSelection()
        self.uiFunc_showDirectories(self.showDirectories)	
        self.uiFunc_displayDetails(self.displayDetails)
        self.uiFunc_displayProject( self.displayProject )

        self.setTitle('%s - %s' % (self.WINDOW_TITLE, self.mDat.d_project['name']))

    def SaveOptions(self, *args):
        log.info( "Saving options" )
        self.showAllFiles = self.cb_showAllFiles( q=True, checkBox=True ) if self.cb_showAllFiles else False
        #self.removeNamespace = self.cb_removeNamespace( q=True, checkBox=True ) if self.cb_removeNamespace else False
        #self.zeroRoot = self.cb_zeroRoot( q=True, checkBox=True ) if self.cb_zeroRoot else False

        self.useMayaPy = self.cb_useMayaPy( q=True, checkBox=True ) if self.cb_useMayaPy else False
        self.showDirectories = self.cb_showDirectories( q=True, checkBox=True ) if self.cb_showDirectories else False

        self.var_showAllFiles.setValue(self.showAllFiles)
        #self.var_removeNamespace.setValue(self.removeNamespace)
        #self.var_zeroRoot.setValue(self.zeroRoot)
        self.var_useMayaPy.setValue(self.useMayaPy)
        self.var_showDirectories.setValue(self.showDirectories)
        self.var_displayDetails.setValue(self.displayDetails)
        self.var_displayProject.setValue(self.displayProject)

        # self.optionVarExportDirStore.setValue( self.exportDirectory )
        self.var_categoryStore.setValue( self.categoryIndex )
        self.var_subTypeStore.setValue( self.subTypeIndex )
        self.uiFunc_showDirectories( self.showDirectories )
        self.uiFunc_displayDetails( self.displayDetails )
        self.uiFunc_displayProject( self.displayProject )

    def UpdateToLatestRig(self, *args):
        for obj in mc.ls(sl=True):
            myAsset = ASSET.Asset(obj)
            myAsset.UpdateToLatest()

    def SetExportSets(self, *args):
        mc.window( width=150 )
        col = mc.columnLayout( adjustableColumn=True )
        #mc.button( label='Set Bake Set', command=self.SetBakeSet )
        cgmUI.add_Button(col,'Set Bake Set', lambda *a: self.SetBakeSet())

        #mc.button( label='Set Delete Set', command=self.SetDeleteSet )
        cgmUI.add_Button(col,'Set Delete Set', lambda *a: self.SetDeleteSet())

        # mc.button( label='Set Export Set', command=self.SetExportSet )
        cgmUI.add_Button(col,'Set Export Set', lambda *a: self.SetExportSet())

        mc.showWindow()
        
    def ResetExportSets(self, *args):
        for n in 'bake','delete','export':
            mc.optionVar(sv=('cgm_{0}_set'.format(n), '{0}_tdSet'.format(n)))
        self.QueryExportSets()
            
    def QueryExportSets(self, *args):
        for n in 'bake','delete','export':
            print mc.optionVar(q='cgm_{0}_set'.format(n))
        
    def SetDeleteSet(self, *args):
        sel = mc.ls(sl=True)
        deleteSet = sel[0].split(':')[-1]
        log.info( "Setting delete set to: %s" % deleteSet )
        self.var_deleteSet.setValue(deleteSet)

    def SetBakeSet(self, *args):
        sel = mc.ls(sl=True)
        bakeSet = sel[0].split(':')[-1]
        log.info( "Setting bake set to: %s" % bakeSet )
        self.var_bakeSet.setValue(bakeSet)

    def SetExportSet(self, *args):
        sel = mc.ls(sl=True)
        exportSet = sel[0].split(':')[-1]
        log.info( "Setting geo set to: %s" % exportSet )
        self.var_exportSet.setValue(exportSet)

    def uiFunc_contentDir_loadSelect(self):
        try:_dat = self.mContentListDat
        except:
            log.warning("No self.mContentListDat")
            return
            
        
        if self.mDat:#Adding the ability to load to Scene
            select_idx = self.uiScrollList_dirContent.getSelectedIdxs(False)
            
            for i,d in enumerate(self.mDat.assetDat):
                k = d.get('n')
                if k in _dat['split']:
                    idx_split = _dat['split'].index(k)
                    l_temp = _dat['split'][idx_split:]
                    print ('Found: {0} | {1}'.format(k,l_temp))

                    numItemsFound = len(l_temp)   
                    
                    if numItemsFound > 0:
                        if l_temp[0] in self.categoryList:
                            idx = self.categoryList.index(l_temp[0])
                            self.SetCategory(idx)
                        else:
                            log.warning('{0} not found in category list'.format(l_temp[0]) )
                            return
                    
                    if numItemsFound > 1:
                        self.assetList['scrollList'].clearSelection()
                        self.assetList['scrollList'].selectByValue(l_temp[1])
                    
                    if numItemsFound > 2:
                        if l_temp[2] in self.subTypes:
                            self.SetSubType(self.subTypes.index(l_temp[2]))
                        else:
                            log.warning('{0} not found in subType list'.format(l_temp[2]) )
                            return
                    
                    if numItemsFound > 3:
                        self.subTypeSearchList['scrollList'].clearSelection()
                        self.subTypeSearchList['scrollList'].selectByValue(l_temp[3])
                        self.LoadVariationList()
                        
                    if numItemsFound > 4:                  
                        if self.hasVariant:
                            self.variationList['scrollList'].clearSelection()
                            self.variationList['scrollList'].selectByValue(l_temp[4])
                            self.LoadVersionList()
                            if numItemsFound > 5:   
                                self.versionList['scrollList'].selectByValue(l_temp[5])
                        else:
                            self.versionList['scrollList'].selectByValue(l_temp[4])

                    #if self.mScene:
                    #self.var_categoryStore.value = i
                    #self.LoadOptions()
                    
                    #if select_idx:
                        #self.uiScrollList_dirContent.selectByIdx(select_idx[0])
                    #return
                        
                    
    def uiFunc_reloadContentBrowswer(self):
        self.uiScrollList_dirContent.rebuild( self.directory)
        
    def uiFunc_reloadExportBrowswer(self):
        self.uiScrollList_dirExport.rebuild( self.exportDirectory)
        
    def build_layoutWrapper(self,parent):

        _ParentForm = mUI.MelFormLayout(self,ut='cgmUISubTemplate')

        _headerColumn = mUI.MelColumnLayout(_ParentForm,useTemplate = 'cgmUISubTemplate')

        _imageFailPath = os.path.join(mImagesPath.asFriendly(),'cgm_project.png')
        imageRow = mUI.MelHRowLayout(_headerColumn,bgc=self.v_bgc)

        #mUI.MelSpacer(imageRow,w=10)
        self.uiImage_ProjectRow = imageRow
        self.uiImage_Project= mUI.MelImage(imageRow,w=800, h=50)#350
        self.uiImage_Project.setImage(_imageFailPath)
        #mUI.MelSpacer(imageRow,w=10)	
        imageRow.layout()

        self._detailsColumn = mUI.MelScrollLayout(_ParentForm,useTemplate = 'cgmUISubTemplate', w=294)
        self._projectForm = mUI.MelTabLayout( _ParentForm, w=400, ut='cgmUITemplate')#w180 mUI.MelFormLayout(_ParentForm,useTemplate = 'cgmUISubTemplate', w=250)

        _MainForm = mUI.MelFormLayout(_ParentForm,ut='cgmUITemplate')

        ##############################
        # Top Column Layout 
        ##############################

        self._detailsToggleBtn = mUI.MelButton(_MainForm, ut = 'cgmUITemplate', label="<", w=15, bgc=(1.0, .445, .08), c = lambda *a:mc.evalDeferred(self.uiFunc_toggleDisplayInfo,lp=True))	
        
        self._projectToggleBtn = mUI.MelButton(_MainForm,
                                               ut = 'cgmUITemplate',
                                               label=">", w=15, bgc=(1.0, .445, .08), c = lambda *a:mc.evalDeferred(self.uiFunc_toggleProjectColumn,lp=True))	
        
        _directoryColumn = mUI.MelColumnLayout(_MainForm,useTemplate = 'cgmUISubTemplate')

        self._uiRow_dir = mUI.MelHSingleStretchLayout(_directoryColumn)

        mUI.MelLabel(self._uiRow_dir,l='Content', w=100)
        self.directoryTF = mUI.MelTextField(self._uiRow_dir, editable = False, bgc=(.8,.8,.8))
        self.directoryTF.setValue( self.directory )
        mUI.MelButton(self._uiRow_dir,l='Explorer', ut = 'cgmUITemplate',
                      c=lambda *a:self.OpenDirectory(self.directory))        

        mUI.MelSpacer(self._uiRow_dir,w=2)

        self._uiRow_dir.setStretchWidget(self.directoryTF)
        self._uiRow_dir.layout()

        self._uiRow_export = mUI.MelHSingleStretchLayout(_directoryColumn)

        mUI.MelLabel(self._uiRow_export,l='Export Dir', w=100)
        self.exportDirectoryTF = mUI.MelTextField(self._uiRow_export, editable = False, bgc=(.8,.8,.8))
        self.exportDirectoryTF.setValue( self.exportDirectory )
        
        mUI.MelButton(self._uiRow_export,l='Explorer', ut = 'cgmUITemplate',
                      c=lambda *a:self.OpenDirectory(self.exportDirectory))        

        mUI.MelSpacer(self._uiRow_export,w=2)                      

        self._uiRow_export.setStretchWidget(self.exportDirectoryTF)

        self._uiRow_export.layout()

        self._uiRow_export(e=True, vis=self.showDirectories)
        self._uiRow_dir(e=True, vis=self.showDirectories)
        
        
        #======================================
        # Projects Column
        ui_tabs = self._projectForm
        #ui_tabs = mUI.MelTabLayout( self._projectForm )#w180

        uiTab_Project = mUI.MelScrollLayout(ui_tabs,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        uiTab_Content = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        self.uiTab_Content = uiTab_Content
        uiTab_Export = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')#mUI.MelScrollLayout( ui_tabs,ut='cgmUITemplate' )
        
        
        for i,tab in enumerate(['Project','Content','Export']):
            ui_tabs.setLabel(i,tab)
            
        #self.buildTab_setup(uiTab_setup)
        #self.buildTab_utilities(uiTab_utils)
        
        
        #Project Setup ========================================================================================
        #iColumn_project = mUI.MelScrollLayout(parent=uiTab_Project)
        self.ui_projectDirty = mUI.MelButton(uiTab_Project, label = 'Changes detected. Save?', vis = False, height = 15, bgc = PROJECT._colorBad,
                                             command = cgmGEN.Callback(self.uiProject_saveAndRefresh))
        
        PROJECT.buildFrame_baseDat(self, uiTab_Project, changeCommand=cgmGEN.Callback(self.uiFunc_projectDirtyState,True))
        
        PROJECT.buildFrame_assetTypes(self,uiTab_Project,changeCommand=cgmGEN.Callback(self.uiFunc_projectDirtyState,True))
        
        PROJECT.buildFrame_paths(self,uiTab_Project,changeCommand=cgmGEN.Callback(self.uiFunc_projectDirtyState,True))
        PROJECT.buildFrames(self,uiTab_Project,changeCommand=cgmGEN.Callback(self.uiFunc_projectDirtyState,True))
        
        
        
        
        
        #Content ========================================================================================================
        _projectColumnTop = mUI.MelColumn(uiTab_Content)
        
        
        #_inside = _projectColumnTop

        mUI.MelSeparator(_projectColumnTop,ut='cgmUISubTemplate',h=3)
        
        _textField = mUI.MelTextField(_projectColumnTop,
                                      ann='Filter',
                                      #w=50,
                                      bgc = [.3,.3,.3],
                                      en=True,
                                      text = '')    
        
        
        #Scroll list
        mScrollList = Project.cgmProjectDirList(uiTab_Content, ut='cgmUISubTemplate',
                                                allowMultiSelection=0, en=True,
                                                ebg=0,
                                                bgc = [.2,.2,.2],
                                                #w = 50,
                                                dcc = cgmGEN.Callback(self.uiFunc_contentDir_loadSelect))
        
        
        
        try:mScrollList(edit=True,hlc = [.5,.5,.5])
        except:pass
        
        mScrollList.set_filterObj(_textField)
        _textField(edit=True,
                   tcc = lambda *a: mScrollList.update_display())    
       
        #mScrollList.set_selCallBack(mrsPoseDirSelect,mScrollList,self)
        
        self.uiScrollList_dirContent = mScrollList        
        mScrollList.mScene = self
        
        
        _refresh = mUI.MelButton(uiTab_Content,l='Refresh', h=15, ut = 'cgmUITemplate',
                                 c=lambda *a:self.uiFunc_reloadContentBrowswer())        
        
        
        uiTab_Content( edit=True, 
                       attachForm=[
                           (_projectColumnTop, 'top', 0), 
                           (_projectColumnTop, 'left', 0), 
                           (_projectColumnTop, 'right', 0),
                           (mScrollList, 'left', 0), 
                           (mScrollList, 'right', 0),
                           (_refresh, 'left', 0), 
                           (_refresh, 'right', 0),                           
                           (_refresh, 'bottom', 0)], 
                       attachControl=[
                           (mScrollList, 'top', 0, _projectColumnTop),
                           (mScrollList, 'bottom', 0, _refresh)] )
        
        #Export ========================================================================================================
        _projectColumnTop = mUI.MelColumn(uiTab_Export)
    
    
        #_inside = _projectColumnTop
    
        mUI.MelSeparator(_projectColumnTop,ut='cgmUISubTemplate',h=3)
    
        _textField = mUI.MelTextField(_projectColumnTop,
                                          ann='Filter',
                                          #w=50,
                                          bgc = [.3,.3,.3],
                                          en=True,
                                          text = '')    
    
    
        #Scroll list
        mScrollList2 = Project.cgmProjectDirList(uiTab_Export, ut='cgmUISubTemplate',
                                                allowMultiSelection=0, en=True,
                                                ebg=0,
                                                bgc = [.2,.2,.2],)
                                                #w = 50)
    
    
    
        try:mScrollList2(edit=True,hlc = [.5,.5,.5])
        except:pass
    
        mScrollList2.set_filterObj(_textField)
        _textField(edit=True,
                   tcc = lambda *a: mScrollList2.update_display())    
    
        #mScrollList.set_selCallBack(mrsPoseDirSelect,mScrollList,self)
    
        self.uiScrollList_dirExport = mScrollList2        
        mScrollList2.mScene = self
    
    
        _refresh = mUI.MelButton(uiTab_Export,l='Refresh', h=15, ut = 'cgmUITemplate',
                                     c=lambda *a:self.uiFunc_reloadExportBrowswer())        
    
    
        uiTab_Export( edit=True, 
                           attachForm=[
                               (_projectColumnTop, 'top', 0), 
                               (_projectColumnTop, 'left', 0), 
                               (_projectColumnTop, 'right', 0),
                               (mScrollList2, 'left', 0), 
                               (mScrollList2, 'right', 0),
                               (_refresh, 'left', 0), 
                               (_refresh, 'right', 0),                           
                               (_refresh, 'bottom', 0)], 
                           attachControl=[
                               (mScrollList2, 'top', 0, _projectColumnTop),
                               (mScrollList2, 'bottom', 0, _refresh)] )        
        
        #--------------------------------------

        ##############################
        # Main Asset Lists 
        ##############################
        self._assetsForm = mUI.MelFormLayout(_MainForm,ut='cgmUISubTemplate', numberOfDivisions=100) #mc.columnLayout(adjustableColumn=True)

        # Category
        _catForm = mUI.MelFormLayout(self._assetsForm,ut='cgmUISubTemplate')
        self.categoryBtn = mUI.MelButton(_catForm,
                                                 label=self.category,ut='cgmUITemplate',
                                                  ann='Select the asset category')

        self.categoryMenu = mUI.MelPopupMenu(self.categoryBtn, button=1 )
        # for i,category in enumerate(self.categoryList):
        # 	self.categoryMenuItemList.append( mUI.MelMenuItem(self.categoryMenu, label=category, c=partial(self.SetCategory,i)) )
        # 	if i == self.categoryIndex:
        # 		self.categoryMenuItemList[i]( e=True, enable=False)

        self.assetList = self.build_searchable_list(_catForm, sc=self.uiFunc_assetList_select)

        self.assetTSLpum = mUI.MelPopupMenu(self.assetList['scrollList'], pmc=self.UpdateAssetTSLPopup)

        mRow_asset = mUI.MelHLayout(_catForm)
        self.assetButton = mUI.MelButton(mRow_asset, ut='cgmUITemplate', label="New Asset", command=self.CreateAsset)
        self.addSubTypeButton = mUI.MelButton(mRow_asset, ut='cgmUITemplate', label="Add SubType", command=self.CreateSubType)
        mRow_asset.layout()

        _catForm( edit=True, 
                          attachForm=[
                              (self.categoryBtn, 'top', 0), 
                              (self.categoryBtn, 'left', 0), 
                                      (self.categoryBtn, 'right', 0), 
                                    (self.assetList['formLayout'], 'left', 0),
                                        (self.assetList['formLayout'], 'right', 0),
                                        (mRow_asset, 'bottom', 0), 
                                        (mRow_asset, 'right', 0), 
                                        (mRow_asset, 'left', 0)], 
                          attachControl=[
                              (self.assetList['formLayout'], 'top', 0, self.categoryBtn),
                                      (self.assetList['formLayout'], 'bottom', 0, mRow_asset)] )


        # SubTypes ======================================================================================
        _animForm = mUI.MelFormLayout(self._assetsForm,ut='cgmUISubTemplate')
        self.subTypeBtn = mUI.MelButton( _animForm,
                                                 label=self.subType,ut='cgmUITemplate',
                                         ann='Select the sub type', en=True )

        self.subTypeMenu = mUI.MelPopupMenu(self.subTypeBtn, button=1 )
        # for i,subType in enumerate(self.subTypes):
        # 	self.subTypeMenuItemList.append( mUI.MelMenuItem(self.subTypeMenu, label=subType, c=partial(self.SetSubType,i)) )
        # 	if i == self.subTypeIndex:
        # 		self.subTypeMenuItemList[i]( e=True, enable=False)


        self.subTypeSearchList = self.build_searchable_list(_animForm, sc=self.uiFunc_subTypeList_select)
        
        #JOSH HERE
        pum = mUI.MelPopupMenu(self.subTypeSearchList['scrollList'],
                               pmc= lambda *a: self.UpdateVersionTSLPopup(self.uiPop_sendToProject_sub))        
        
        mUI.MelMenuItem( pum, label='        Subtype', en=False )
        
        mUI.MelMenuItem(pum,label="Add Subtype",
                        command=self.CreateSubType)
        
        
        mUI.MelMenuItem(pum, label="Rename Subtype", command= partial(self.rename_below,'subtype') )
        
        
        
        mUI.MelMenuItem(pum,label="Add Sub Dir",
                        command=self.CreateSubAsset)
        
        mUI.MelMenuItem(pum,label="Add Variation",
                        command=self.CreateVariation)
        
        mUI.MelMenuItemDiv( pum, label='Selected' )
                
        
        self._referenceSubTypePUM = mUI.MelMenuItem(pum,label="Reference",
                                                    ann = _d_ann.get('reference'),
                                                    command=self.ReferenceFile,en=1 )
        self._importSubTypePUM = mUI.MelMenuItem(pum,label="Import",
                                                 ann = _d_ann.get('import'),
                                                 command=self.ImportFile,en=1 )
        self._importSubTypePUM = mUI.MelMenuItem(pum,label="Replace",
                                                 ann=_d_ann.get('replace','Replace'),
                                                 command=self.file_replace,en=1 )
                
        
        
        self.uiPop_sendToProject_sub = mUI.MelMenuItem(pum, label="Send To Project", subMenu=True, en=1)
        
        #mUI.MelMenuItem(pum, label="Send To Build", command=self.SendToBuild,en=1)
        
        
        mUI.MelMenuItem( pum, label="Send Last To Queue", command=self.AddLastToExportQueue )
        
        mUI.MelMenuItem( pum, label="Create SubTypeRef", command= lambda *a:self.CreateSubTypeRef() )
        
        _batch = mUI.MelMenuItem(pum, label="To Queue as:", subMenu=True )
        for t in ['export','rig','cutscene']:
            mUI.MelMenuItem( _batch, label= t.capitalize(),
                             command = partial(self.AddToExportQueue,t))        

        mUI.MelMenuItemDiv( pum, label='Directory' )
        mUI.MelMenuItem(pum, label="Explorer", command=self.OpenSubTypeDirectory )
        
        mUI.MelMenuItem(pum,
                        ann = "Open Maya file",
                        c= lambda *a:self.uiPath_mayaOpen_subType(),
                        label = 'Open Maya here')
        
        mUI.MelMenuItem(pum,
                        ann = "Save Maya file",
                        c= lambda *a:self.uiPath_mayaSaveTo_subType(),
                        label = 'Save Maya here')
        mUI.MelMenuItem(pum, label="Refresh", command=lambda *a:self.LoadSubTypeList() )
        
        
        
        mRow_subType = mUI.MelHLayout(_animForm)
        self.subTypeButton = mUI.MelButton(mRow_subType, ut='cgmUITemplate', label="New Subtype", command=self.CreateSubAsset)
        #self.addSubButton = mUI.MelButton(mRow_subType, ut='cgmUITemplate', label="Add Sub", command=self.CreateVariation)
        mRow_subType.layout()
        _animForm( edit=True, 
                           attachForm=[
                               (self.subTypeBtn, 'top', 0), 
                               (self.subTypeBtn, 'left', 0), 
                                       (self.subTypeBtn, 'right', 0), 
                                    (self.subTypeSearchList['formLayout'], 'left', 0),
                                        (self.subTypeSearchList['formLayout'], 'right', 0),
                                        (mRow_subType, 'bottom', 0), 
                                        (mRow_subType, 'right', 0),
                                        (mRow_subType, 'left', 0)], 
                           attachControl=[
                               (self.subTypeSearchList['formLayout'], 'top', 0, self.subTypeBtn),
                                       (self.subTypeSearchList['formLayout'], 'bottom', 0, mRow_subType)] )

        # Variation ======================================================================================
        _variationForm = mUI.MelFormLayout(self._assetsForm,ut='cgmUISubTemplate')
        _variationBtn = mUI.MelButton(_variationForm,
                                              label='Variation',ut='cgmUITemplate',
                                              ann='Select the asset variation', en=False)

        self.variationList = self.build_searchable_list(_variationForm, sc=self.uiFunc_variationList_select)
        
   
        pum = mUI.MelPopupMenu(self.variationList['scrollList'],
                               pmc= lambda *a: self.UpdateVersionTSLPopup(self.uiPop_sendToProject_variant))
        
        
        #------------------------------------------------------------------------------
        mUI.MelMenuItem( pum, label='        Variant', en=False )
        mUI.MelMenuItemDiv( pum, label='Selected' )
        
        mUI.MelMenuItem(pum, label="Rename Variant", command= partial(self.rename_below,'variant') )
        
        mUI.MelMenuItem(pum, label="Reference File",
                        ann = _d_ann.get('reference'),
                        command=self.ReferenceFile )
        mUI.MelMenuItem(pum,label="Import",
                        ann = _d_ann.get('import'),
                        command=self.ImportFile)        
        mUI.MelMenuItem(pum,label="Replace",
                        ann=_d_ann.get('replace','Replace'),
                        command=self.file_replace)        

        self.uiPop_sendToProject_variant = mUI.MelMenuItem(pum, label="Send To Project", subMenu=True )
        mUI.MelMenuItem(pum, label="Send To Build", command=self.SendToBuild,en=1)
        
        mUI.MelMenuItem( pum, label="Send Last To Queue", command=self.AddLastToExportQueue )
        

        mUI.MelMenuItemDiv( pum, label='Directory' )
        mUI.MelMenuItem(pum, label="Explorer", command=self.OpenVariationDirectory )
        
        mUI.MelMenuItem(pum,
                        ann = "Open Maya file",
                        c= lambda *a:self.uiPath_mayaOpen_variant(),
                        label = 'Open Maya here')
        
        mUI.MelMenuItem(pum,
                        ann = "Save Maya file",
                        c= lambda *a:self.uiPath_mayaSaveTo_variant(),
                        label = 'Save Maya here')
        mUI.MelMenuItem(pum, label="Refresh", command=lambda *a:self.LoadVariationList() )        
        

        #---------------------------------------------------------------------------------------
        
        self.variationButton = mUI.MelButton(_variationForm, ut='cgmUITemplate', label="New Variation", command=self.CreateVariation)

        _variationForm( edit=True, 
                                attachForm=[
                                    (_variationBtn, 'top', 0), 
                                    (_variationBtn, 'left', 0), 
                                            (_variationBtn, 'right', 0), 
                                    (self.variationList['formLayout'], 'left', 0),
                                        (self.variationList['formLayout'], 'right', 0),
                                        (self.variationButton, 'bottom', 0), 
                                        (self.variationButton, 'right', 0), 
                                        (self.variationButton, 'left', 0)], 
                                attachControl=[
                                    (self.variationList['formLayout'], 'top', 0, _variationBtn),
                                            (self.variationList['formLayout'], 'bottom', 0, self.variationButton)] )


        # Version ======================================================================================
        _versionForm = mUI.MelFormLayout(self._assetsForm,ut='cgmUISubTemplate')
        _versionBtn = mUI.MelButton(_versionForm,
                                            label='Version',ut='cgmUITemplate',
                                            ann='Select the asset version', en=False)

        self.versionList = self.build_searchable_list(_versionForm, sc=self.uiFunc_versionList_select)

        pum = mUI.MelPopupMenu(self.versionList['scrollList'],
                               pmc= lambda *a: self.UpdateVersionTSLPopup(self.uiPop_sendToProject_version))
        
        

        #------------------------------------------------------------------------------
        mUI.MelMenuItem( pum, label='        Version', en=False )
        mUI.MelMenuItemDiv( pum, label='Selected' )
        
        mUI.MelMenuItem(pum, label="Reference File",
                        ann = _d_ann.get('reference'),
                        command=self.ReferenceFile )
        mUI.MelMenuItem(pum,label="Import",
                        ann = _d_ann.get('import'),
                        command=self.ImportFile)        
        mUI.MelMenuItem(pum,label="Replace",
                        ann=_d_ann.get('replace','Replace'),
                        command=self.file_replace)        

        self.uiPop_sendToProject_version = mUI.MelMenuItem(pum, label="Send To Project", subMenu=True )
        mUI.MelMenuItem(pum, label="Send To Build", command=self.SendToBuild,en=1)
        
        #mUI.MelMenuItem( pum, label="Send Last To Queue", command=self.AddLastToExportQueue )
        
        _batch = mUI.MelMenuItem(pum, label="To Queue as:", subMenu=True )
        for t in ['export','rig','cutscene']:
            mUI.MelMenuItem( _batch, label= t.capitalize(),
                             command = partial(self.AddToExportQueue,t))
            
        
        
        
        
        mUI.MelMenuItem( pum, label="Create SubTypeRef", command= lambda *a:self.CreateSubTypeRef() )
        

        mUI.MelMenuItemDiv( pum, label='Directory' )
        mUI.MelMenuItem(pum, label="Explorer", command=self.OpenVersionDirectory )
        
        mUI.MelMenuItem(pum,
                        ann = "Save Maya file",
                        c= lambda *a:self.uiPath_mayaSaveTo_version(),
                        label = 'Save Maya here')
        mUI.MelMenuItem(pum, label="Refresh", command=lambda *a:self.LoadVersionList() )


        self.versionButton = mUI.MelButton(_versionForm, ut='cgmUITemplate', label="Save New Version", command=self.SaveVersion)

        _versionForm( edit=True, 
                      attachForm=[
                          (_versionBtn, 'top', 0), 
                          (_versionBtn, 'left', 0), 
                                  (_versionBtn, 'right', 0), 
                            (self.versionList['formLayout'], 'left', 0),
                                (self.versionList['formLayout'], 'right', 0),
                                (self.versionButton, 'bottom', 0), 
                                (self.versionButton, 'right', 0), 
                                (self.versionButton, 'left', 0)], 
                      attachControl=[
                          (self.versionList['formLayout'], 'top', 0, _versionBtn),
                                  (self.versionList['formLayout'], 'bottom', 0, self.versionButton)] )


        self._subForms = [_catForm,_animForm,_variationForm,_versionForm]

        self.buildAssetForm()


        ##############################
        # Bottom 
        ##############################
        _bottomColumn    = mUI.MelColumnLayout(_MainForm,useTemplate = 'cgmUISubTemplate', adjustableColumn=True)#mc.columnLayout(adjustableColumn = True)

        mc.setParent(_bottomColumn)
        cgmUI.add_LineSubBreak()

        _row = mUI.MelHSingleStretchLayout(_bottomColumn,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=10)
        mUI.MelLabel(_row, label="Process: ", h=self.__itemHeight, align = 'right')
        
        self.exportButton = mUI.MelButton(_row, label="Export", ut = 'cgmUITemplate', c=partial(self.RunExportCommand,1), h=self.__itemHeight)
        mc.popupMenu()
        mc.menuItem( l="Bake Without Export", c=partial(self.RunExportCommand,0))
        mc.menuItem( l="Export Rig", c=partial(self.RunExportCommand,3))
        mc.menuItem( l="Force Export As Cutscene", c=partial(self.RunExportCommand,2))

        mUI.MelButton(_row, ut = 'cgmUITemplate', label="Bake Without Export", c=partial(self.RunExportCommand,0), h=self.__itemHeight)
        mUI.MelButton(_row, ut = 'cgmUITemplate', label="Export Rig", c=partial(self.RunExportCommand,3), h=self.__itemHeight)
        mUI.MelButton(_row, ut = 'cgmUITemplate', label="Export Cutscene", c=partial(self.RunExportCommand,2), h=self.__itemHeight)
        
        _split = mUI.MelLabel(_row, label=" | ", h=self.__itemHeight, align = 'center')
        mUI.MelLabel(_row, label="Add to queue as: ", h=self.__itemHeight, align = 'right')
        
        mUI.MelButton(_row, ut = 'cgmUITemplate', label="Export", w=100, c=lambda *a:(self.AddToExportQueue('export')), h=self.__itemHeight)
        mUI.MelButton(_row, ut = 'cgmUITemplate', label="Rig", w=100, c=lambda *a:(self.AddToExportQueue('rig')), h=self.__itemHeight)
        mUI.MelButton(_row, ut = 'cgmUITemplate', label="Cutscene", w=100, c=lambda *a:(self.AddToExportQueue('cutscene')), h=self.__itemHeight)

        _row.setStretchWidget(_split)

        #mUI.MelSpacer(_row,w=0)
        mUI.MelSpacer(_row,w=10)

        _row.layout()

        mc.setParent(_bottomColumn)
        cgmUI.add_LineSubBreak()

        #_row = mUI.MelHSingleStretchLayout(_bottomColumn,ut='cgmUISubTemplate',padding = 5)
        _row = mUI.MelColumnLayout(_bottomColumn,useTemplate = 'cgmUISubTemplate') 
        #mUI.MelSpacer(_row,w=5)

        self.loadBtn = mUI.MelButton(_row, ut = 'cgmUITemplate', label="Load File", c=self.LoadFile, h=self.__itemHeight)
        #_row.setStretchWidget( self.loadBtn )

        #mUI.MelSpacer(_row,w=5)

        #_row.layout()

        mc.setParent(_bottomColumn)
        cgmUI.add_LineSubBreak()

        self.exportQueueFrame = mUI.MelFrameLayout(_bottomColumn, label="Export Queue", collapsable=True, collapse=True)
        _rcl = mUI.MelFormLayout(self.exportQueueFrame,ut='cgmUITemplate')

        self.queueTSL = cgmUI.cgmScrollList(_rcl)
        self.queueTSL.allowMultiSelect(True)

        _col = mUI.MelColumnLayout(_rcl,width=200,adjustableColumn=True,useTemplate = 'cgmUISubTemplate')#mc.columnLayout(width=200,adjustableColumn=True)

        cgmUI.add_LineSubBreak()
        #mUI.MelButton(_col, label="Add", ut = 'cgmUITemplate', command=partial(self.AddToExportQueue))
        #cgmUI.add_LineSubBreak()
        mUI.MelButton(_col, label="Remove", ut = 'cgmUITemplate', command=partial(self.RemoveFromQueue, 0))
        cgmUI.add_LineSubBreak()
        mUI.MelButton(_col, label="Remove All", ut = 'cgmUITemplate', command=partial(self.RemoveFromQueue, 1))
        cgmUI.add_LineSubBreak()
        mUI.MelButton(_col, label="Batch Export", ut = 'cgmUITemplate', command=partial(self.batch_buildFile))
        cgmUI.add_LineSubBreak()

        _options_fl = mUI.MelFrameLayout(_col, label="Options", collapsable=True)

        _c2 = mUI.MelColumnLayout(_options_fl, adjustableColumn=True)
        self.updateCB = mUI.MelCheckBox(_c2, label="Update and Save Increment", v=False)

        _rcl( edit=True, 
                      attachForm=[
                          (self.queueTSL, 'top', 0), 
                          (self.queueTSL, 'left', 0), 
                                  (self.queueTSL, 'bottom', 0), 
                                    (_col, 'bottom', 0), 
                                        (_col, 'top', 0), 
                                        (_col, 'right', 0)], 
                      attachControl=[
                          (self.queueTSL, 'right', 0, _col)] )

        ##############################
        # Layout form
        ##############################

        _footer = cgmUI.add_cgmFooter(_ParentForm)            

        _MainForm( edit=True, 
                           attachForm=[
                               (_directoryColumn, 'top', 0), 
                                        #(_directoryColumn, 'left', 0), 
                                        (_bottomColumn, 'left', 0),
                                        (_bottomColumn, 'bottom', 0),
                                                                (self._assetsForm, 'left', 0),
                                                                

                                        (self._projectToggleBtn, 'top', 0),
                                        (self._projectToggleBtn, 'bottom', 0),
                                        (self._projectToggleBtn, 'left', 0),
                                        
                                        (self._detailsToggleBtn, 'right', 0),
                                        (self._detailsToggleBtn, 'top', 0),
                                        (self._detailsToggleBtn, 'bottom', 0)], 
                           attachControl=[
                               (self._assetsForm, 'top', 0, _directoryColumn),
                                        (self._assetsForm, 'bottom', 0, _bottomColumn),
                                        
                                        (self._assetsForm, 'left', 0, self._projectToggleBtn),
                                        (_bottomColumn, 'left', 0, self._projectToggleBtn),
                                        (_directoryColumn, 'left', 0, self._projectToggleBtn),                                        
                                        (self._assetsForm, 'right', 0, self._detailsToggleBtn),
                                         (_bottomColumn, 'right', 0, self._detailsToggleBtn),
                                         (_directoryColumn, 'right', 0, self._detailsToggleBtn)])

        _ParentForm( edit=True,
                             attachForm=[						 
                                        (_headerColumn, 'left', 0),
                                        (_headerColumn, 'right', 0),
                                        (_headerColumn, 'top', 0),
                                        (self._detailsColumn, 'right', 0),
                                        (self._projectForm, 'left', 0),                                        
                                         #(_MainForm, 'left', 0),
                                        (_footer, 'left', 0),
                                          (_footer, 'right', 0),
                                        (_footer, 'bottom', 0)],
                                         attachControl=[(_MainForm, 'top', 0, _headerColumn),
                                                        (_MainForm, 'bottom', 0, _footer),
                                                        (_MainForm, 'left', 0, self._projectForm),
                                                         (_MainForm, 'right', 0, self._detailsColumn),
                                                         (self._projectForm, 'top', 0, _headerColumn),
                                                          (self._projectForm, 'bottom', 1, _footer),
                                                         (self._detailsColumn, 'top', 0, _headerColumn),
                                                          (self._detailsColumn, 'bottom', 1, _footer)])
    def show( self ):		
        self.setVisibility( True )
        self.buildMenu_options()
        self.buildDetailsColumn()


    #=========================================================================
    # Menu Building
    #=========================================================================
    def buildAssetForm(self):
        mc.formLayout( self._subForms[2], e=True, vis=self.hasVariant and self.hasSub )
        _hasSub = self.hasSub
        
        if not self.hasSubTypes:
            #mc.formLayout( self._subForms[1], e=True, vis=False )
            mc.formLayout( self._subForms[3], e=True, vis=self.hasSub )
        
        else:
            mc.formLayout( self._subForms[3], e=True, vis=self.hasSub)#self.hasSub )
                
            #    mc.formLayout( self._subForms[3], e=True, vis=0)#self.hasSub )                
            #else:
            #mc.formLayout( self._subForms[3], e=True, vis=True)#self.hasSub )
                
            mc.formLayout( self._subForms[1], e=True, vis=True )
            
        
        attachForm = []
        attachControl = []
        attachPosition = []

        attachedForms = []

        for form in self._subForms:
            vis = mc.formLayout(form, q=True, visible=True)
            if vis:
                attachedForms.append(form)

        for i,form in enumerate(attachedForms):
            if i == 0:
                attachForm.append( (form, 'left', 1) )
            else:
                attachControl.append( (form, 'left', 5, attachedForms[i-1]) )

            attachForm.append((form, 'top', 0))
            attachForm.append((form, 'bottom', 5))

            if i == len(attachedForms)-1:
                attachForm.append( (form, 'right', 1) )
            else:
                attachPosition.append( (form, 'right', 5, (100 / len(attachedForms)) * (i+1)) )

        self._assetsForm( edit=True, attachForm = attachForm, attachControl = attachControl, attachPosition = attachPosition)

    def build_menus(self):
        _str_func = 'build_menus[{0}]'.format(self.__class__.TOOLNAME)            
        log.info("|{0}| >>...".format(_str_func))   
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmo=1, pmc = cgmGEN.Callback(self.buildMenu_first))

        self.uiMenu_Projects = mUI.MelMenu( l='Projects', pmc=self.buildMenu_project)		        
        
        self.uiMenu_OptionsMenu = mUI.MelMenu( l='Options', pmc=self.buildMenu_options)
        self.uiMenu_ToolsMenu = mUI.MelMenu( l='Tools', pmc=self.buildMenu_tools,pmo=True)
        self.uiMenu_Utils = mUI.MelMenu(l='Utils', pmo=1,
                                        pmc = cgmGEN.Callback(self.buildMenu_utils),
                                        tearOff=True)         
        self.uiMenu_HelpMenu = mUI.MelMenu( l='Help', pmc=self.buildMenu_help,pmo=True)
        
        
    def uiProject_saveAndRefresh(self):
        self.SaveOptions()
        PROJECT.uiProject_save(self)
        self.uiProject_refreshDisplay()
        self.uiFunc_projectDirtyState(False)
        
    def reload_headerImage(self, path = None):
        _str_func = 'reload_headerImage'
        log.debug("|{0}| >>...".format(_str_func))
        
        if path:
            _path = PATHS.Path(path)
            
        else:
            _path = PATHS.Path(self.d_tf['paths']['image'].getValue())
            
        if _path.exists():
            log.warning('Image path: {0}'.format(_path))
            _imagePath = _path
        else:
            _imagePath = os.path.join(mImagesPath.asFriendly(),
                                      'cgm_project_{0}.png'.format(self.d_tf['general']['type'].getValue()))
            
        self.uiImage_Project.setImage(_imagePath)
        
    def uiProject_refreshDisplay(self):
        #self.uiFunc_displayProject(self.displayProject)
        
        _bgColor = self.v_bgc
        try:
            _bgColor = self.mDat.d_colors['project']
            
        except Exception,err:
            log.warning("No project color stored | {0}".format(err))

        try:self.uiImage_ProjectRow(edit=True, bgc = _bgColor)
        except Exception,err:
            log.warning("Failed to set bgc: {0} | {1}".format(_bgColor,err))

        try:
            
            _c_secondary = self.mDat.d_colors['secondary']
            print _c_secondary
            vTmp = _c_secondary
            vLite = [MATH.Clamp(1.7 * v, .5, 1.0) for v in vTmp]

            
            self._detailsToggleBtn(edit=True, bgc=vTmp)
            self._projectToggleBtn(edit=True, bgc=vTmp)
            self.uiScrollList_dirContent.v_hlc = vLite
            self.uiScrollList_dirExport.v_hlc = vLite
            
        except Exception,err:
            log.error("Load project color set error | {0}".format(err))
            
            self._detailsToggleBtn(edit=True, bgc=(1.0, .445, .08))
            self._projectToggleBtn(edit=True, bgc=(1.0, .445, .08))
            self.uiScrollList_dirContent(edit=True, hlc = (1.0, .445, .08))
            self.uiScrollList_dirExport(edit=True, hlc = (1.0, .445, .08))

        d_userPaths = self.mDat.userPaths_get()

        if not d_userPaths.get('content'):
            log.error("No Content path found")
            return False
        if not d_userPaths.get('export'):
            log.error("No Export path found")
            return False


        if os.path.exists(d_userPaths['content']):

            self.LoadCategoryList(d_userPaths['content'])
            self.exportDirectory = d_userPaths['export']
            
            

            self.exportDirectoryTF.setValue( self.exportDirectory )
            
            self.l_categoriesBase = self.mDat.assetTypes_get() if self.mDat.assetTypes_get() else self.mDat.d_structure.get('assetTypes', [])
            self.categoryList = [c for c in self.l_categoriesBase]
            
            for i,f in enumerate(os.listdir(self.directory)):
                if os.path.isfile(os.path.join(self.directory, f)):
                    continue
                if f in self.l_categoriesBase:
                    continue
                
                self.categoryList.append(f)

            if d_userPaths.get('image') and os.path.exists(d_userPaths.get('image')):
                self.uiImage_Project.setImage(d_userPaths['image'])
            else:
                _imageFailPath = os.path.join(mImagesPath.asFriendly(),
                                                              'cgm_project_{0}.png'.format(self.mDat.d_project.get('type','unity')))
                self.uiImage_Project.setImage(_imageFailPath)

            self.buildMenu_category()

            mc.workspace( d_userPaths['content'], openWorkspace=True )

            self.assetMetaData = {}
            self.LoadOptions()
        else:
            mel.eval('error "Project path does not exist"')
            
            
        self.uiScrollList_dirContent.mDat = self.mDat
        self.uiScrollList_dirContent.rebuild( self.directory)
        
        self.uiScrollList_dirExport.mDat = self.mDat        
        self.uiScrollList_dirExport.rebuild( self.exportDirectory)
        
        log.info( "+"*100)
        log.info(self.d_tf['general']['mayaFilePref'].getValue())        
        log.info(self.d_tf['exportOptions']['removeNameSpace'].getValue())
        log.info(self.d_tf['exportOptions']['zeroRoot'].getValue())        
        log.info(self.d_tf['exportOptions']['postEuler'].getValue())        
        log.info(self.d_tf['exportOptions']['postTangent'].getValue())        
        
        """
        
        self.var_mayaFilePref.setValue( self.mDat.d_project.get('mayaFilePref','mb') )
        
        if self.mDat.d_exportOptions:
            self.var_postEuler.setValue( self.mDat.d_exportOptions.get('postEuler',True) )
            self.var_postTangent.setValue( self.mDat.d_exportOptions.get('postTangent',True) )
            if self.mDat.d_exportOptions.get('removeNameSpace'):
                self.var_removeNamespace.setValue( self.mDat.d_exportOptions.get('removeNameSpace',False) )
                self.removeNamespace = self.mDat.d_exportOptions.get('removeNameSpace',False)
            
            self.var_zeroRoot.setValue( self.mDat.d_exportOptions.get('zeroRoot',False) )"""
            
            
            
            
    def uiProject_reset(self):
        PROJECT.uiProject_reset(self)
        self.uiProject_refreshDisplay()
    
    def uiProject_revert(self):
        PROJECT.uiProject_revert(self)
        self.uiProject_refreshDisplay()
        
    def uiProject_clear(self):
        PROJECT.uiProject_clear(self)
        self.uiProject_refreshDisplay()
        
    def uiProject_new(self):

        
        if not PROJECT.uiProject_new(self):
            return
        
        self.directory = ''
        self.exportDirectoryTF.setValue('')
        
        self.assetList['scrollList'].clear()
        self.subTypeSearchList['scrollList'].clear()
        self.variationList['scrollList'].clear()
        self.versionList['scrollList'].clear()                
        
        self.LoadProject(self.mDat.str_filepath)
        
    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        
        #Recent -------------------------------------------------------------------
        
        
        
        #>>> Reset Options		                     
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu, label='Basic' )
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="New",
                         ann='Create a new project',                         
                         c = lambda *a:mc.evalDeferred(self.uiProject_new,lp=True))
        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Save ",
                         c = lambda *a:mc.evalDeferred(self.uiProject_saveAndRefresh,lp=True))
        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Save As",
                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(PROJECT.uiProject_saveAs,self),lp=True))
        
        
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu, label='Utils' )
        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         ann='Reset data to default',
                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiProject_reset),lp=True))
        
        #mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Fill",
        #                 ann='Refill the ui fields from the mDat',                         
        #                 c = lambda *a:mc.evalDeferred(cgmGEN.Callback(PROJECT.uiProject_fill,self),lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Revert",
                         ann='Revert to saved file data',
                         c = lambda *a:mc.evalDeferred(self.uiProject_revert,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Clear",
                         ann='Clear the fields',
                         c = lambda *a:mc.evalDeferred(self.uiProject_clear,lp=True))
        
        
        """
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Load",
                         c = lambda *a:mc.evalDeferred(self.uiProject_load,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Save ",
                         c = lambda *a:mc.evalDeferred(self.uiProject_save,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Save As",
                         c = lambda *a:mc.evalDeferred(self.uiProject_saveAs,lp=True))
        #mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Duplicate",
        #                c = lambda *a:mc.evalDeferred(self.uiProject_duplicate,lp=True))
        
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu, label='Utils' )
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         ann='Reset data to default',
                         c = lambda *a:mc.evalDeferred(self.reset,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Fill",
                         ann='Refill the ui fields from the mDat',                         
                         c = lambda *a:mc.evalDeferred(self.uiProject_fill,lp=True))        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Revert",
                         ann='Revert to saved file data',
                         c = lambda *a:mc.evalDeferred(self.uiProject_revert,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Clear",
                         ann='Clear the fields',
                         c = lambda *a:mc.evalDeferred(self.uiProject_clear,lp=True))
        """
        
        
        
        
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu, label='UI' )
        
        #self.uiMenu_buildDock(self.uiMenu_FirstMenu)
        """
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Dock",
                         c = lambda *a:self.do_dock())"""        

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))    
    def buildMenu_utils(self):
        self.uiMenu_Utils.clear()

        SCENEUTILS.buildMenu_utils(self, self.uiMenu_Utils)
        


    def buildMenu_help( self, *args):
        self.uiMenu_HelpMenu.clear()

        _log = mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Logs:",subMenu=True)


        mUI.MelMenuItem( _log, l="Dat",
                                 c=lambda *a: self.mDat.log_self())
        mUI.MelMenuItem( _log, l="States",
                                 c=lambda *a: self.report_states())
        mUI.MelMenuItem( _log, l="Export Batch",
                                 c=lambda *a: pprint.pprint(self.batchExportItems))        
        mc.menuItem(parent=self.uiMenu_HelpMenu,
                            l = 'Get Help',
                            c='import webbrowser;webbrowser.open("https://http://docs.cgmonks.com/mrs.html");',                        
                            rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Log Self",
                                 c=lambda *a: cgmUI.log_selfReport(self) )

    #@cgmGEN.Timer
    def buildMenu_project( self, *args):
        self.uiMenu_Projects.clear()
        mMenu = self.uiMenu_Projects
        #>>> Reset Options			

        mPathList = cgmMeta.pathList('cgmProjectPaths')

        project_names = []
        for i,p in enumerate(mPathList.mOptionVar.value):
            proj = Project.data(filepath=p)
            name = proj.d_project['name']
            project_names.append(name)
            en = True
            _path = proj.userPaths_get().get('content') or False
            if _path and os.path.exists(_path):
                #en=True
                pass
            else:
                log.warning("'{0}' Missing content path".format(name))
                
            mUI.MelMenuItem( self.uiMenu_Projects, en=en, l=name if project_names.count(name) == 1 else '%s {%i}' % (name,project_names.count(name)-1),
                                         c = partial(self.LoadProject,p))

        mUI.MelMenuItemDiv( self.uiMenu_Projects )

        mUI.MelMenuItem( self.uiMenu_Projects, l="MRSProject",
                                 c = lambda *a:mc.evalDeferred(Project.ui,lp=True))                         
        
        
        mUI.MelMenuItemDiv(mMenu)
        #mUI.MelMenuItem(mMenu,
        #                label = "Clear Recent",
        #                ann="Clear the recent projects",
        #                c=cgmGEN.Callback(self.mPathList.clear))
        mUI.MelMenuItem(mMenu,
                        label = "Edit Path List",
                        ann="Open Edit UI",
                        c=cgmGEN.Callback(self.mPathList.ui))            

    def buildMenu_options( self, *args):
        self.uiMenu_OptionsMenu.clear()
        #>>> Reset Options		
        
        mUI.MelMenuItemDiv( self.uiMenu_OptionsMenu, label = 'Export', )
        self.cb_useMayaPy =  mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Use Maya Standalone",
                                                 ann="Use Mayapy/Maya stand alone to process",
                                                 checkBox=self.useMayaPy,
                                                 c = lambda *a:mc.evalDeferred(self.SaveOptions,lp=True))        
        
        """
        self.cb_removeNamespace = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Remove namespace upon export",
                                                      checkBox=self.removeNamespace,
                                                      c = lambda *a:mc.evalDeferred(self.SaveOptions,lp=True))
        
        self.cb_zeroRoot = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Zero root upon export",
                                               checkBox=self.zeroRoot,
                                               c = lambda *a:mc.evalDeferred(self.SaveOptions,lp=True))
        
        self.cb_postEuler = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Post Euler",
                                               checkBox=self.var_postEuler.getValue(),
                                               c = lambda *a:mc.evalDeferred(self.SaveOptions,lp=True))
        
        self.cb_tangent = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Post Tangent",subMenu=True
                                              )
        uiMenu = self.cb_tangent 
                
        uiRC = mc.radioMenuItemCollection()
        #self.uiOptions_menuMode = []		
        _v = self.var_postTangent.value
    
        for i,item in enumerate(['none','auto','linear']):
            if item == _v: _rb = True
            else:_rb = False            
            mc.menuItem(parent=uiMenu,collection = uiRC,
                        label=item,
                        c = cgmGEN.Callback(self.var_postTangent.setValue,item),                                  
                        rb = _rb)
                
        #...-------------------------------------------------------------------------------------------
        self.cb_mayaFilePref = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Maya File Pref",subMenu=True
                                              )
        uiMenu = self.cb_mayaFilePref 
                
        uiRC = mc.radioMenuItemCollection()
        #self.uiOptions_menuMode = []		
        _v = self.var_mayaFilePref.value
    
        for i,item in enumerate(['ma','mb']):
            if item == _v: _rb = True
            else:_rb = False            
            mc.menuItem(parent=uiMenu,collection = uiRC,
                        label=item,
                        c = cgmGEN.Callback(self.var_mayaFilePref.setValue,item),                                  
                        rb = _rb)        
        
        """
        
        mUI.MelMenuItemDiv( self.uiMenu_OptionsMenu, l = 'Other')
        
        self.cb_showAllFiles = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Show all files",
                                                           checkBox=self.showAllFiles,
                                                        c = lambda *a:mc.evalDeferred(self.uiFunc_showAllFiles,lp=True))

        
        self.cb_showDirectories =  mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Show Directories",
                                                               checkBox=self.showDirectories,
                                                         c = lambda *a:mc.evalDeferred(self.SaveOptions,lp=True))

    def uiFunc_showAllFiles(self):
        self.SaveOptions()
        self.LoadVersionList()
        
    def uiFunc_assetList_select(self):
        _str_func = 'uiFunc_assetList_select'
        log.info(log_start(_str_func))
        
        path_subType = os.path.normpath(os.path.join( self.path_dir_category, self.assetList['scrollList'].getSelectedItem() ))
        if not os.path.exists(path_subType):
            self.LoadCategoryList()
            return
        
        
        self.subTypeSearchList['items'] = []
        self.subTypeSearchList['scrollList'].clear()

        self.variationList['items'] = []
        self.variationList['scrollList'].clear()

        self.versionList['items'] = []
        self.versionList['scrollList'].clear()        
        
        
        l_newTypes = []
        l_expected = []
        for d in CGMOS.get_lsFromPath(path_subType,'dir'):
            if d in self.l_subTypesBase:
                l_expected.append(d)
            else:
                l_newTypes.append(d)
                
        #pprint.pprint(l_expected)
        #pprint.pprint(l_newTypes)
        
        self.subTypes = []
        if l_expected:
            self.subTypes.extend(l_expected)
        if l_newTypes:
            self.subTypes.extend(l_newTypes)

        #print self.subType
        #pprint.pprint(self.subTypes)        
        
        if self.subTypes:
            self.buildMenu_subTypes()
            if self.subType not in self.subTypes:
                log.debug(log_msg(_str_func, "Setting subtype because stored not in list"))
                self.subType = self.subTypes[0]
            else:
                self.SetSubType(self.subTypes.index(self.subType))
                
        #if self.subTypes:
            #self.buildMenu_subTypes()
            #self.LoadSubTypeList()
            
        self.buildAssetForm()
        self.LoadPreviousSelection()
                
    def uiFunc_subTypeList_select(self):
        _str_func = 'uiFunc_subTypeList_select'
        log.info(log_start(_str_func))
        
        self.report_selectedPaths()
        self.file_subType = None
        
        try: 
            _path = os.path.normpath(os.path.join( self.path_dir_category,
                                                   self.assetList['scrollList'].getSelectedItem(),
                                                   self.subType,
                                                   self.subTypeSearchList['scrollList'].getSelectedItem(),
                                                   ))
        except:
            _path = None
           
        print _path
        if _path and os.path.isfile(_path):
            self.file_subType = _path
            return

        self.LoadVariationList()
        
    def uiFunc_variationList_select(self):
        _str_func = 'uiFunc_variationList_select'
        log.info(log_start(_str_func))
        self.report_selectedPaths()
        
        
        self.LoadVersionList()
        
    def uiFunc_versionList_select(self, selectKey= None):
        _str_func = 'uiFunc_variationList_select'
        log.info(log_start(_str_func))
        if selectKey:
            #searchList['scrollList'].selectByValue(anims[-1])
            self.versionList['scrollList'].selectByValue(selectKey)
        self.report_selectedPaths()
        
        self.assetMetaData = self.getMetaDataFromFile()
        self.buildDetailsColumn()
        self.StoreCurrentSelection()
        log.info( self.versionFile )
        
        
        
    def buildProjectColumn(self):
        if not self._projectForm(q=True, vis=True):
            log.info("Project column isn't visible")
            return
        
        log.info("Project column...")
        
        self._projectForm.clear()
        
        #self._projectForm(e=1, vis=1)
        mc.setParent(self._projectForm)

        mUI.MelLabel(self._projectForm,l='Project', h=15, ut = 'cgmUIHeaderTemplate')
        
        _inside = self._projectForm
        #Utils -------------------------------------------------------------------------------------------
        _row = mUI.MelHLayout(_inside,padding=3,)
        button_refresh = mUI.MelButton(_row,
                                       label='Refresh',ut='cgmUITemplate',
                                        c=lambda *a: self.uiScrollList_dirContent.rebuild( self.directory),
                                        ann='Force the scroll list to update')
        
        button_add= mUI.MelButton(_row,
                                  label='Add',ut='cgmUITemplate',
                                   ann='Add a subdir to the path root')    
        
        button_verify = mUI.MelButton(_row,
                                       label='Verify Dir',ut='cgmUITemplate',
                                        ann='Verify the directories from the project Type')  
        
        mUI.MelButton(_row,
                      label='Query',ut='cgmUITemplate',
                       c=lambda *a: SCENEUTILS.find_tmpFiles( self. self.directory),
                       ann='Query trash files')    
        mUI.MelButton(_row,
                      label='Clean',ut='cgmUITemplate',
                       c=lambda *a: SCENEUTILS.find_tmpFiles( self.directory,cleanFiles=1),
                       ann='Clean trash files')
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
        mScrollList = Project.cgmProjectDirList(_inside, ut='cgmUISubTemplate',
                                        allowMultiSelection=0,en=True,
                                        ebg=0,
                                        h=600,
                                        bgc = [.2,.2,.2],
                                        w = 50)
        
        mScrollList.mDat = self.mDat
        
        #Connect the functions to the buttons after we add the scroll list...
        button_verify(edit=True,
                      c=lambda *a:Project.uiProject_verifyDir(self,'content',None,mScrollList),)
        button_add(edit=True,
                   c=lambda *a:Project.uiProject_addDir(self,'content',mScrollList),
                   )
        
        try:mScrollList(edit=True,hlc = [.5,.5,.5])
        except:pass
        
        mScrollList.set_filterObj(_textField)
        _textField(edit=True,
                   tcc = lambda *a: mScrollList.update_display())    
       
        #mScrollList.set_selCallBack(mrsPoseDirSelect,mScrollList,self)
        
        self.uiScrollList_dirContent = mScrollList        
        
        self.uiScrollList_dirContent.mDat = self.mDat
        
        

        
    def buildDetailsColumn(self):
        if not self._detailsColumn(q=True, vis=True):
            log.info("details column isn't visible")
            return
        _spacer = 2
        _bgc = .8,.8,.8
        
        self._detailsColumn.clear()

        mc.setParent(self._detailsColumn)

        mUI.MelLabel(self._detailsColumn,l='Details', h=15, ut = 'cgmUIHeaderTemplate')

        mc.setParent(self._detailsColumn)
        cgmUI.add_LineSubBreak()		

        thumb = self.getThumbnail()

        self.uiImage_Thumb = mUI.MelImage( self._detailsColumn, w=130, h=150 )
        self.uiImage_Thumb(e=True, vis=(thumb != None))

        if thumb:
            self.uiImage_Thumb.setImage(thumb)

        pum = mUI.MelPopupMenu(self.uiImage_Thumb)
        mUI.MelMenuItem(pum, label="Remake Thumbnail", command=cgmGEN.Callback(self.makeThumbnail) )		

        self.uiButton_MakeThumb = mUI.MelButton(self._detailsColumn, ut = 'cgmUITemplate', h=150, label="Make Thumbnail", c=cgmGEN.Callback(self.makeThumbnail), vis=(thumb == None))

        mc.setParent(self._detailsColumn)
        cgmUI.add_LineSubBreak()
        
        _row = mUI.MelHLayout(self._detailsColumn)
        
        mUI.MelButton(_row, ut = 'cgmUITemplate', h=15, label="Refresh Data",
                      c=cgmGEN.Callback(self.refreshMetaData) )
        mUI.MelButton(_row, ut = 'cgmUITemplate', h=15, label="Report Data",
                      c=cgmGEN.Callback(self.metaData_print) )
        mUI.MelButton(_row, ut = 'cgmUITemplate', h=15, label="Copy ShotList",
                      c=cgmGEN.Callback(self.metaData_copyShotList) )                
        _row.layout()
        
        
        mc.setParent(self._detailsColumn)
        cgmUI.add_LineSubBreak()	
        
        _d = {'Asset':self.assetMetaData.get('asset', None),
              'Type':self.assetMetaData.get('type', None),
              'SubAsset':self.assetMetaData.get('subTypeAsset', None),
              'Variation':self.assetMetaData.get('variation', None),
              'User':self.assetMetaData.get('user', None)}
        
        for k in ['Asset','Type','SubAsset','Variation','User']:
            _dat = _d.get(k)
            if _dat is not None:
                _row = mUI.MelHSingleStretchLayout(self._detailsColumn)
                mUI.MelLabel(_row,l=k, w=70)
                _row.setStretchWidget(mUI.MelTextField(_row, text=_dat, ann=_dat,
                                                       editable = False, bgc=_bgc))	
                mUI.MelSpacer(_row,w=_spacer)
    
                _row.layout()	
                
                
        """
        _row = mUI.MelHSingleStretchLayout(self._detailsColumn)

        mUI.MelLabel(_row,l='Asset', w=70)
        _row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('asset', ""), editable = False, bgc=(.8,.8,.8)))	
        mUI.MelSpacer(_row,w=_spacer)

        _row.layout()

        _row = mUI.MelHSingleStretchLayout(self._detailsColumn)

        mUI.MelLabel(_row,l='Type', w=70)
        _row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('type', ""), editable = False, bgc=(.8,.8,.8)))	
        mUI.MelSpacer(_row,w=_spacer)

        _row.layout()

        _row = mUI.MelHSingleStretchLayout(self._detailsColumn)

        mUI.MelLabel(_row,l='SubType', w=70)
        _row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('subType', ""), editable = False, bgc=(.8,.8,.8)))	
        mUI.MelSpacer(_row,w=_spacer)

        _row.layout()

        if self.assetMetaData.get('subTypeAsset', None):
            _row = mUI.MelHSingleStretchLayout(self._detailsColumn)

            mUI.MelLabel(_row,l='SubAsset', w=70)
            _row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('subTypeAsset', ""), editable = False, bgc=(.8,.8,.8)))	
            mUI.MelSpacer(_row,w=_spacer)

            _row.layout()	

        if self.assetMetaData.get('variation', None):
            _row = mUI.MelHSingleStretchLayout(self._detailsColumn)

            mUI.MelLabel(_row,l='Variation', w=70)
            _row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('variation', ""), editable = False, bgc=(.8,.8,.8)))	
            mUI.MelSpacer(_row,w=_spacer)

            _row.layout()	

        _row = mUI.MelHSingleStretchLayout(self._detailsColumn)

        mUI.MelLabel(_row,l='User', w=70)
        _row.setStretchWidget(mUI.MelTextField(_row, text=self.assetMetaData.get('user', ""), editable = False, bgc=(.8,.8,.8)))	
        mUI.MelSpacer(_row,w=_spacer)

        _row.layout()	
        """
        mUI.MelLabel(self._detailsColumn,l='Notes', w=70)

        _row = mUI.MelHSingleStretchLayout(self._detailsColumn)
        mUI.MelSpacer(_row,w=_spacer)		
        noteField = mUI.MelScrollField(_row, h=150, text=self.assetMetaData.get('notes', ""), wordWrap=True, editable=True, bgc=(.8,.8,.8))
        noteField(e=True, changeCommand=cgmGEN.Callback( self.saveMetaNote,noteField ) )
        _row.setStretchWidget(noteField)
        mUI.MelSpacer(_row,w=_spacer)
        _row.layout()

        if self.assetMetaData.get('references', None):
            mUI.MelLabel(self._detailsColumn,l='References', w=50)

            for ref in self.assetMetaData.get('references', []):
                _row = mUI.MelHSingleStretchLayout(self._detailsColumn)
                path = os.path.normpath(self.directory) +  os.path.normpath(ref)
                mUI.MelSpacer(_row,w=_spacer)		
                _row.setStretchWidget(mUI.MelTextField(_row, text=ref, editable = False, bgc=(.8,.8,.8)))
                cgmUI.add_Button(_row,'Load', lambda *a: VALID.fileOpen(path,True,True))
                
                
                mUI.MelSpacer(_row,w=_spacer)
                _row.layout()			

        if self.assetMetaData.get('shots', None):
            mUI.MelLabel(self._detailsColumn,l='Shots', w=50)

            for shot in self.assetMetaData.get('shots', []):
                _row = mUI.MelHRowLayout(self._detailsColumn, w=150)
                _ann = "{0} | start: {1} | end: {2} | length: {3}".format(shot[0],shot[1][0],shot[1][1],shot[1][2])
                mUI.MelSpacer(_row,w=_spacer)
                mUI.MelTextField(_row, text=shot[0], ann = _ann,
                                 editable = False, bgc=(.8,.8,.8), w = 120)
                mUI.MelTextField(_row, text=shot[1][0], editable = False, ann = _ann,
                                 bgc=(.8,.8,.8), w=40)
                mUI.MelTextField(_row, text=shot[1][1], editable = False, ann = _ann,
                                 bgc=(.8,.8,.8), w=40)
                mUI.MelTextField(_row, text=shot[1][2], editable = False, ann = _ann,
                                 bgc=(.8,.8,.8), w=40)
                mUI.MelSpacer(_row,w=_spacer)
                _row.layout()
                
                
        mUI.MelLabel(self._detailsColumn,l='File', w=50)
        for k in ['size','dateModified','dateAccess','file']:
            if self.assetMetaData.get(k, None) is not None:
                _row = mUI.MelHSingleStretchLayout(self._detailsColumn)
                _dat = self.assetMetaData.get(k, "")
                mUI.MelLabel(_row,l=k, w=70)
                _row.setStretchWidget(mUI.MelTextField(_row, text=_dat, ann=_dat,
                                                       editable = False, bgc=(_bgc)))	
                mUI.MelSpacer(_row,w=_spacer)
            
                _row.layout()                
        """
        ata['size'] = os.path.getsize(self.versionFile)
        data['dateModified'] = time.ctime(os.path.getmtime(self.versionFile))
        data['dateAccess'] = time.ctime(os.path.getctime(self.versionFile))
        data['file']
        """

    def makeThumbnail(self):
        if self.versionFile:
            path, filename = os.path.split(self.versionFile)
            basefile = os.path.splitext(filename)[0]

            metaDir = os.path.join(path, 'meta')
            if not os.path.exists(metaDir):
                os.mkdir( os.path.join(path, 'meta') )

            thumbFile = os.path.join(path, 'meta', '{0}.bmp'.format(basefile))
            r9General.thumbNailScreen(thumbFile, 256, 256)		
            self.uiButton_MakeThumb(e=True, vis=False)
            self.uiImage_Thumb.setImage(thumbFile)
            self.uiImage_Thumb(e=True, vis=True)

    def getThumbnail(self):
        thumbFile = None

        if self.versionFile:
            path, filename = os.path.split(self.versionFile)
            basefile = os.path.splitext(filename)[0]
            thumbFile = os.path.join(path, 'meta', '{0}.bmp'.format(basefile))
            if not os.path.exists(thumbFile):
                thumbFile = None

        return thumbFile
    
    def metaData_copyShotList(self):
        _d = self.getMetaDataFromFile() 
        
        _d.get('file')
        _file =  os.path.normpath(_d.get('file')).replace(os.path.normpath(self.mDat.userPaths_get()['content']), '')

        """
        {"arame_poker_cheer_left": [280, 420, 140], "arame_poker_cheer_right": [560, 700, 140], "arame_poker_cheer_lwrR": [700, 840, 140], "arame_poker_cheer_center": [0, 140, 140], "arame_poker_cheer_lwrL": [420, 560, 140], "arame_poker_cheer_down": [140, 280, 140]}
        """
        #Shots
        _d_res = {}
        
        if _d.get('shots'):
            _shots = _d.get('shots')
            _total = 0
            _lows = []
            _highs = []
            
            _l_shots = []
            
            for s in _shots:
                _d_res[str(s[0])] = s[1]
                _total += s[1][2]
                _l = [s[0], s[1][0], s[1][1], s[1][2]] 
                _l = [str(v) for v in _l]
                _l_shots.append( _l )
                _lows.append(s[1][0])
                _highs.append(s[1][1])
                
            """
            print ','.join(['clip','start','end',str(_total), "{0}".format(max(_highs) - min(_lows))])
            print ''
            for s in _l_shots:
                print ','.join(s)"""
                
            pprint.pprint(_d_res)
            
            mList = cgmMeta.validateObjArg('AnimListNode',noneValid=True)
            
            if mList is False:
                mList = cgmMeta.cgmObject(name="AnimListNode")#node.Transform(name="AnimListNode")
            mList.addAttr("subAnimList", attrType = 'string')
            

            mList.subAnimList = _d_res#json.dumps(self.animDict)            
        
    def metaData_print(self):
        
        _d = self.getMetaDataFromFile() 
        pprint.pprint(_d)
        
        _type = _d.get('type')
        _subType =_d.get('subType')
        _subTypeAsset = _d.get('subTypeAsset')
        _asset = _d.get('asset')
        
        _l = []
        for k in _type,_asset,_subType,_subTypeAsset:
            if k:
                _l.append(k)
        
        _name = '.'.join(_l)
        
        print ''
        _d.get('file')
        _file =  os.path.normpath(_d.get('file')).replace(os.path.normpath(self.mDat.userPaths_get()['content']), '')
        _l_asset = [_name,_file]
        print ','.join(_l_asset)
        print ''
        
        #Shots
        if _d.get('shots'):
            _shots = _d.get('shots')
            _total = 0
            _lows = []
            _highs = []
            
            _l_shots = []
            
            for s in _shots:
                _total += s[1][2]
                _l = [s[0], s[1][0], s[1][1], s[1][2]] 
                _l = [str(v) for v in _l]
                _l_shots.append( _l )
                _lows.append(s[1][0])
                _highs.append(s[1][1])
                
            
            print ','.join(['clip','start','end',str(_total), "{0}".format(max(_highs) - min(_lows))])
            print ''
            for s in _l_shots:
                print ','.join(s)
                
        print 'Notes'
        print _d.get('notes','None')
        
        #pprint.pprint( self.getMetaDataFromCurrent() )
        
    def getMetaDataFromCurrent(self):
        from cgm.core.mrs.Shots import AnimList
        import getpass

        #if os.path.normpath(self.versionFile) != os.path.normpath(mc.file(q=True, loc=True)):
            #mc.confirmDialog(title="No. Just no.", message="The open file doesn't match the selected file. I refuse to refresh this metaData with the wrong file. It just wouldn't feel right.", button=["Cancel", "Sorry"])
            #return

        data = {}
        data['asset'] = self.assetList['scrollList'].getSelectedItem()
        data['type'] = self.category
        data['subType'] = self.subType
        data['subTypeAsset'] = self.subTypeSearchList['scrollList'].getSelectedItem() if self.hasSub else ""
        data['variation'] = self.variationList['scrollList'].getSelectedItem() if self.hasVariant else ""
        data['user'] = getpass.getuser()
        
        data['size'] = os.path.getsize(self.versionFile)
        data['dateModified'] = time.ctime(os.path.getmtime(self.versionFile))
        data['dateAccess'] = time.ctime(os.path.getctime(self.versionFile))
        data['file'] = self.versionFile

        data['saved'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        data['notes'] = ""

        data['references'] = [os.path.normpath(x).replace(os.path.normpath(self.directory), "") for x in mc.file(q=True, r=True)]

        data['startTime'] = mc.playbackOptions(q=True, min=True)
        data['endTime'] = mc.playbackOptions(q=True, max=True)

        l = AnimList()
        data['shots'] = l.SortedList(1)

        return data

    def getMetaDataFromFile(self):
        _func_str = 'Scene.getMetaDataFromFile'

        metaFile = None

        data = {}

        if self.versionFile:
            path, filename = os.path.split(self.versionFile)
            basefile = os.path.splitext(filename)[0]
            metaFile = os.path.join(path, 'meta', '{0}.dat'.format(basefile))
            if not os.path.exists(metaFile):
                log.info("{0} | No meta file found".format(_func_str))
                metaFile = None
            else:
                f = open(metaFile, 'r')
                data = json.loads(f.read())
        else:
            log.info("{0} | No version file found".format(_func_str))
        return data

    def refreshMetaData(self):
        if os.path.normpath(self.versionFile) != os.path.normpath(mc.file(q=True, loc=True)):
            mc.confirmDialog(title="No. Just no.", message="The open file doesn't match the selected file. I refuse to refresh this metaData with the wrong file. It just wouldn't feel right.", button=["Cancel", "Sorry"])
            return

        notes = self.assetMetaData.get('notes', "")
        self.assetMetaData = self.getMetaDataFromCurrent()
        self.assetMetaData['notes'] = notes

        self.buildDetailsColumn()
        self.saveMetaData()

    def saveMetaNote(self, field):
        self.assetMetaData['notes'] = field.getValue()
        self.saveMetaData()

    def saveMetaData(self):
        if self.versionFile:
            path, filename = os.path.split(self.versionFile)
            basefile = os.path.splitext(filename)[0]

            metaDir = os.path.join(path, 'meta')
            if not os.path.exists(metaDir):
                os.mkdir( os.path.join(path, 'meta') )

            metaFile = os.path.join(path, 'meta', '{0}.dat'.format(basefile))
            f = open(metaFile, 'w')
            f.write( json.dumps(self.assetMetaData) )
            f.close()

            log.info('wrote file: {0}'.format(metaFile))

    def uiFunc_showDirectories(self, val):
        self._uiRow_dir(e=True, vis=val)
        self._uiRow_export(e=True, vis=val)

    def uiFunc_toggleDisplayInfo(self):
        self.displayDetails = not self.displayDetails
        self.SaveOptions()
        
    def uiFunc_toggleProjectColumn(self):
        self.displayProject = not self.displayProject
        self.uiFunc_displayProject(self.displayProject)
        #self.SaveOptions()
        
    def uiFunc_displayDetails(self, val):
        self._detailsColumn(e=True, vis=val)
        self._detailsToggleBtn(e=True, label='>' if val else '<')

        if val:
            self.buildDetailsColumn()
            
    def uiFunc_projectDirtyState(self,arg=True):
        _str_func = 'uiFunc_projectDirtyState'
        log.info("|{}| >>...{}".format(_str_func,arg))
        if arg:
            self.b_projectDirty = True            
            self.ui_projectDirty(edit=True,vis=True)
        else:
            self.b_projectDirty = False            
            self.ui_projectDirty(edit=True,vis=False)
            
    def uiFunc_displayProject(self,val):
        _str_func = 'uiFunc_displayProject'
        log.info("|{}| >>...{}".format(_str_func,val))        
        self._projectForm(e=True, vis=val)
        self._projectToggleBtn(e=True, label='<' if val else '>')

        #if val:
            #self.uiScrollList_dirContent.mDat = self.mDat
            #self.uiScrollList_dirContent.rebuild( self.directory)
            #self.buildProjectColumn()        

    def buildMenu_tools( self, *args):
        self.uiMenu_ToolsMenu.clear()
        #>>> Reset Options		
        
        mUI.MelMenuItemDiv( self.uiMenu_ToolsMenu, label='Asset..' )
        
        mUI.MelMenuItem( self.uiMenu_ToolsMenu, l="Update Selected Rigs",
                                 c = lambda *a:mc.evalDeferred(self.UpdateToLatestRig,lp=True))

        mUI.MelMenuItem( self.uiMenu_ToolsMenu, l="Remap Unlinked Textures",
                                 c = lambda *a:mc.evalDeferred(self.RemapTextures,lp=True))

        mUI.MelMenuItem( self.uiMenu_ToolsMenu, l="Verify Asset Dirs",
                                 c = cgmGEN.Callback(self.VerifyAssetDirs) )
        
        mUI.MelMenuItem( self.uiMenu_ToolsMenu, l="Clean Scene",
                                 c = lambda *a:mc.evalDeferred(MAYABEODD.cleanFile,lp=1) )        
        
        mUI_skinDat = mUI.MelMenuItem(self.uiMenu_ToolsMenu,l='SkinDat',subMenu=True)
        SKINDAT.uiBuildMenu(mUI_skinDat)
        
        mUI.MelMenuItemDiv( self.uiMenu_ToolsMenu, label='Baking..' )
        
        #Export Menu ...
        _exportMenu = mUI.MelMenuItem(self.uiMenu_ToolsMenu,l='Export Sets',subMenu=True)
        mUI.MelMenuItem( _exportMenu, l="Set",
                         c = lambda *a:mc.evalDeferred(self.SetExportSets,lp=True))
        mUI.MelMenuItem( _exportMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.ResetExportSets,lp=True))
        mUI.MelMenuItem( _exportMenu, l="Query",
                         c = lambda *a:mc.evalDeferred(self.QueryExportSets,lp=True))        

        

    def RemapTextures(self, *args):
        import cgm.tools.findTextures as findTextures
        findTextures.FindAndRemapTextures()

    def buildMenu_category(self, *args):
        self.categoryMenu.clear()
        self.categoryMenuItemList = []
        
        l_cats = []
        b_extra = False
        for i,category in enumerate(self.categoryList):
            #if category not in self.l_categoriesBase and not b_extra != True:
            #    mUI.MelMenuItemDiv( self.categoryMenu, label='Extras..' )
            #    b_extra = True
                
            
            self.categoryMenuItemList.append( mUI.MelMenuItem(self.categoryMenu, label=category, c=partial(self.SetCategory,i)) )
            if i == self.categoryIndex:
                self.categoryMenuItemList[i]( e=True, enable=False)
            l_cats.append(category)


    def buildMenu_subTypes(self, *args):
        _str_func = 'buildMenu_subTypes'
        log.debug(log_start(_str_func))
        
        self.subTypeMenu.clear()
        # for item in self.subTypeMenuItemList:
        # 	if mc.menuItem(item, q=True, exists=True):
        # 		mc.deleteUI(item)

        self.subTypeMenuItemList = []

        mc.setParent(self.subTypeMenu, menu=True)
        b_extra = False

        for i,subType in enumerate(self.subTypes):
            # mc.menuItem(label=subType, c=cgmGEN.Callback(self.SetSubType,i))
            
            if subType not in self.l_subTypesBase and not b_extra:
                mUI.MelMenuItemDiv( self.subTypeMenu, label='Extras..' )
                b_extra = True
            self.subTypeMenuItemList.append( mc.menuItem(label=subType, enable=i!=self.subTypeIndex, c=cgmGEN.Callback(self.SetSubType,i)) ) #mUI.MelMenuItem(self.subTypeMenu, label=subType, c=partial(self.SetSubType,i)) )

        
    #####
    ## Searchable Lists
    #####
    def build_searchable_list(self, parent = None, sc=None):
        _margin = 0

        if not parent:
            parent = self

        form = mUI.MelFormLayout(parent,ut='cgmUITemplate')

        rcl = mc.rowColumnLayout(numberOfColumns=2, adjustableColumn=1)

        tx = mUI.MelTextField(rcl)
        b = mUI.MelButton(rcl, label='clear', ut='cgmUISubTemplate')

        tsl = cgmUI.cgmScrollList(form)
        tsl.allowMultiSelect(False)

        if sc != None:
            tsl(edit = True, sc=sc)

        form( edit=True, attachForm=[(rcl, 'top', _margin), (rcl, 'left', _margin), (rcl, 'right', _margin), (tsl, 'bottom', _margin), (tsl, 'right', _margin), (tsl, 'left', _margin)], attachControl=[(tsl, 'top', _margin, rcl)] )

        searchableList = {'formLayout':form, 'scrollList':tsl, 'searchField':tx, 'searchButton':b, 'items':[], 'selectCommand':sc}

        tx(edit=True, tcc=partial(self.process_search_filter, searchableList))
        b(edit=True, command=partial(self.clear_search_filter, searchableList))

        return searchableList

    def process_search_filter(self, searchableList, *args):
        #print "processing search for %s with search term %s" % (searchableList['scrollList'], searchableList['searchField'].getValue())
        if not searchableList['searchField'].getValue():
            searchableList['scrollList'].setItems(searchableList['items'])
        else:
            searchTerms = searchableList['searchField'].getValue().lower().strip().split(' ')  #set(searchableList['searchField'].getValue().replace(' ', '').lower())
            listItems = []
            for item in searchableList['items']:
                hasAllTerms = True
                for term in searchTerms:
                    if not term in item.lower():
                        hasAllTerms = False
                if hasAllTerms:
                    listItems.append(item)
            searchableList['scrollList'].setItems(listItems)

        searchableList['selectCommand']

    def clear_search_filter(self, searchableList, *args):
        log.info( "Clearing search filter for %s with search term %s" % (searchableList['scrollList'], searchableList['searchField'].getValue()) )
        searchableList['searchField'].setValue("")
        selected = searchableList['scrollList'].getSelectedItem()
        searchableList['scrollList'].setItems(searchableList['items'])
        searchableList['scrollList'].selectByValue(selected)

    def SetCategory(self, index, *args):
        self.categoryIndex = index

        mc.button( self.categoryBtn, e=True, label=self.category )
        for i,category in enumerate(self.categoryMenuItemList):
            if i == self.categoryIndex:
                self.categoryMenuItemList[i]( e=True, enable=False)
            else:
                self.categoryMenuItemList[i]( e=True, enable=True)

        self.LoadCategoryList(self.directory)

        self.var_categoryStore.setValue(self.categoryIndex)
        
        try:
            self.l_subTypesBase = [x['n'] for x in self.mDat.assetType_get(self.category).get('content', [{'n':'animation'}])]
        except:
            self.l_subTypesBase = []
        
        self.subTypes = [c for c in self.l_subTypesBase]        

        # Set SubType -------------------------------------------------------------------------
        try:
            self.subTypes = [x['n'] for x in self.mDat.assetType_get(self.category)['content']]
        except:
            self.subTypes = ['None']
            

        
        

        if self.subTypeBtn(q=True, label=True) in self.subTypes:
            self.subTypeIndex = self.subTypes.index(self.subTypeBtn(q=True, label=True))
        else:
            self.subTypeIndex = min(self.subTypeIndex, len(self.subTypes)-1)
        
        self.SetSubType(self.subTypeIndex)
        self.buildMenu_subTypes()

    def LoadCategoryList(self, directory="", *args):
        _str_func = 'LoadCategoryList'
        if directory:		
            self.directory = directory

        assetList = []

        categoryDirectory = os.path.join(self.directory, self.category)
        log.debug( log_msg( _str_func, categoryDirectory ) )
        if os.path.exists(categoryDirectory):
            for d in os.listdir(categoryDirectory):
                #for ext in fileExtensions:
                #	if os.path.splitext(f)[-1].lower() == ".%s" % ext :
                if d[0] == '_' or d[0] == '.':
                    continue

                charDir = os.path.normpath(os.path.join(categoryDirectory, d))
                if os.path.isdir(charDir):
                    assetList.append(d)

        assetList = sorted(assetList, key=lambda v: v.upper())

        self.UpdateAssetList(assetList)

        self.subTypeSearchList['items'] = []
        self.subTypeSearchList['scrollList'].clear()

        self.variationList['items'] = []
        self.variationList['scrollList'].clear()

        self.versionList['items'] = []
        self.versionList['scrollList'].clear()

        self.StoreCurrentSelection()

    def SetSubType(self, index, *args):
        self.subTypeIndex = index

        self.subTypeBtn( e=True, label=self.subType )

        if self.hasSub:
            self.subTypeButton(edit=True, label="New {0}".format(self.subType.capitalize()), command=self.CreateSubAsset)
        else:
            self.subTypeButton(edit=True, label="Save New Version", command=self.SaveVersion)

        self.LoadSubTypeList()

        self.var_subTypeStore.setValue(self.subTypeIndex)

        for i,item in enumerate(self.subTypeMenuItemList):
            mc.menuItem(item, e=True, enable= i != self.subTypeIndex)

        if not self.hasNested:
            mc.formLayout( self._subForms[3], e=True, vis=False )
        else:
            mc.formLayout( self._subForms[3], e=True, vis=self.hasSub )
            
        mc.formLayout( self._subForms[2], e=True, vis=self.hasVariant and self.hasSub )
        self.buildAssetForm()

    def LoadSubTypeList(self, *args):
        _str_func = 'LoadSubTypeList'
        log.info(log_start(_str_func))
        
        
        if not self.hasSub:
            self.LoadVersionList()
            self._referenceSubTypePUM(e=True, en=True)
            return

        self._referenceSubTypePUM(e=True, en=False)

        subList = []

        if self.path_dir_category and self.assetList['scrollList'].getSelectedItem():
            charDir = os.path.normpath(os.path.join( self.path_dir_category, self.assetList['scrollList'].getSelectedItem(), self.subType ))

            if os.path.exists(charDir):
                for d in os.listdir(charDir):
                    #for ext in fileExtensions:
                    #	if os.path.splitext(f)[-1].lower() == ".%s" % ext :
                    
                    #if d[0] == '_' or d[0] == '.':
                    #    continue

                    animDir = os.path.normpath(os.path.join(charDir, d))
                    if os.path.isdir(animDir):
                        subList.append(d)
                    else:
                        subList.append(d)
                        

        self.subTypeSearchList['items'] = subList
        self.subTypeSearchList['scrollList'].clear()
        self.subTypeSearchList['scrollList'].setItems(subList)
        

        self.variationList['items'] = []
        self.variationList['scrollList'].clear()

        self.versionList['items'] = []
        self.versionList['scrollList'].clear()

        self.StoreCurrentSelection()

    def LoadVariationList(self, *args):
        _str_func = 'LoadVariationList'
        log.info(log_start(_str_func))
        
        if not self.hasSub and self.hasNested:
            self.LoadVersionList()            
            #self.uiFunc_versionList_select()
            return
        
        
        if not self.hasVariant:
            self.LoadVersionList()
            #self.buildAssetForm()
            mc.formLayout( self._subForms[2], e=True, vis=False )
            self.buildAssetForm()            
            return
        else:
            mc.formLayout( self._subForms[2], e=True, vis=False )                        
            self.buildAssetForm()
            

        variationList = []

        selectedVariation = self.variationList['scrollList'].getSelectedItem()

        self.variationList['items'] = []
        self.variationList['scrollList'].clear()

        if self.path_dir_category and self.assetList['scrollList'].getSelectedItem() and self.subTypeSearchList['scrollList'].getSelectedItem():
            animationDir = self.path_subType

            if os.path.exists(animationDir):
                for d in os.listdir(animationDir):
                    #for ext in fileExtensions:
                    #	if os.path.splitext(f)[-1].lower() == ".%s" % ext :
                    if d[0] == '_' or d[0] == '.':
                        continue

                    animDir = os.path.normpath(os.path.join(animationDir, d))
                    if os.path.isdir(animDir):
                        variationList.append(d)

        self.variationList['items'] = variationList
        self.variationList['scrollList'].setItems(variationList)

        self.variationList['scrollList'].selectByValue(selectedVariation) # if selectedVariation else variationList[0]

        self.versionList['items'] = []
        self.versionList['scrollList'].clear()

        self.LoadVersionList()

        if len(self.versionList['items']) > 0:
            self.versionList['scrollList'].selectByIdx( len(self.versionList['items'])-1 )

        self.StoreCurrentSelection()

    def LoadVersionList(self, *args):
        _str_func = 'LoadVersionList'
        log.info(log_start(_str_func))

        searchDir = os.path.join(self.path_asset if self.path_asset else self.path_dir_category, self.subType if self.subType else "")
        searchList = self.subTypeSearchList
        if self.hasSub:
            searchDir = self.path_subType
            searchList = self.versionList
        if self.hasVariant and self.hasSub:
            searchDir = self.path_variationDirectory

        if not searchDir:
            return

        versionList = []
        anims = []

        # populate animation info list
        fileExtensions = ['mb', 'ma']

        #log.info('{0} >> searchDir: {1}'.format(_str_func, searchDir))
        if os.path.exists(searchDir):
            # animDir = (self.path_variationDirectory if self.hasVariant else self.path_subType) if self.hasSub else self.path_dir_category

            # if os.path.exists(animDir):
            for d in os.listdir(searchDir):
                if d[0] == '_' or d[0] == '.':
                    continue

                if self.showAllFiles:
                    if d not in ['meta']:
                        anims.append(d)
                elif os.path.splitext(d)[-1].lower()[1:] in fileExtensions:
                    if self.hasSub:
                        if self.hasVariant:
                            if '{0}_{1}_{2}_'.format(self.selectedAsset, self.selectedSubType, self.selectedVariation) in d:
                                anims.append(d)
                        else:
                            if '{0}_{1}_'.format(self.selectedAsset, self.selectedSubType) in d:
                                anims.append(d)							
                    else:
                        if '{0}_{1}_'.format(self.selectedAsset, self.subType) in d:
                            anims.append(d)

        searchList['items'] = anims
        searchList['scrollList'].clear()
        searchList['scrollList'].setItems(anims)
        
        if anims:
            #searchList['scrollList'].selectByValue(anims[-1])
            self.uiFunc_versionList_select(anims[-1])
        else:
            self.StoreCurrentSelection()

    def LoadFile(self, *args):
        if not self.assetList['scrollList'].getSelectedItem():
            log.warning( "No asset selected" )
            return
        if not self.subTypeSearchList['scrollList'].getSelectedItem():
            print "No animation selected"
            return
        if not self.versionList['scrollList'].getSelectedItem() and self.hasSub:
            print "No version selected"
            return
        
        VALID.fileOpen(self.versionFile,True,True)


    def SetAnimationDirectory(self, *args):
        basicFilter = "*"
        x = mc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, fm=3)
        if x:
            self.LoadCategoryList(x[0])

    def GetPreviousDirectories(self, *args):
        if type(self.optionVarDirStore.getValue()) is list:
            return self.optionVarDirStore.getValue()
        else:
            return []

    def UpdateAssetList(self, assetList):
        self.assetList['items'] = assetList
        self.assetList['scrollList'].setItems(assetList)

    # def GetPreviousDirectory(self, *args):
    # 	if self.optionVarLastDirStore.getValue():
    # 		return self.optionVarLastDirStore.getValue()
    # 	else:
    # 		return None

    def StoreCurrentSelection(self, *args):
        _str_func = 'StoreCurrentSelection'
        log.debug(log_start(_str_func))
        
        if self.assetList['scrollList'].getSelectedItem():
            self.var_lastAsset.setValue(self.assetList['scrollList'].getSelectedItem())
        #else:
        #	mc.optionVar(rm=self.var_lastAsset)

        if self.subTypeSearchList['scrollList'].getSelectedItem():
            self.var_lastAnim.setValue(self.subTypeSearchList['scrollList'].getSelectedItem())
        #else:
        #	mc.optionVar(rm=self.var_lastAnim)

        if self.variationList['scrollList'].getSelectedItem():
            self.var_lastVariation.setValue(self.variationList['scrollList'].getSelectedItem())
        #else:
        #	mc.optionVar(rm=self.var_lastVariation)

        if self.versionList['scrollList'].getSelectedItem():
            self.var_lastVersion.setValue( self.versionList['scrollList'].getSelectedItem() )
        #else:
        #	mc.optionVar(rm=self.var_lastVersion)

    def LoadPreviousSelection(self, *args):
        if self.var_lastAsset.getValue():
            self.assetList['scrollList'].selectByValue( self.var_lastAsset.getValue() )

        self.LoadSubTypeList()

        if self.var_lastAnim.getValue():
            self.subTypeSearchList['scrollList'].selectByValue( self.var_lastAnim.getValue() )

        self.LoadVariationList()

        if not self.hasSub:
            self.assetMetaData = self.getMetaDataFromFile()		
            return

        if self.var_lastVariation.getValue():
            self.variationList['scrollList'].selectByValue( self.var_lastVariation.getValue() )

        self.LoadVersionList()

        if self.var_lastVersion.getValue():
            self.versionList['scrollList'].selectByValue( self.var_lastVersion.getValue() )
        #else:
        #self.versionList['scrollList'].selectByIdx(-1)

        self.assetMetaData = self.getMetaDataFromFile()	

    def ClearPreviousDirectories(self, *args):		
        self.optionVarDirStore.clear()
        self.buildMenu_project()

    def CreateAsset(self, *args):
        result = mc.promptDialog(
                    title='New Asset',
                    message='Asset Name:',
                    button=['OK', 'Cancel'],
                            defaultButton='OK',
                                        cancelButton='Cancel',
                                        dismissString='Cancel')

        if result == 'OK':
            #pprint.pprint(self.l_subTypesBase)
            charName = mc.promptDialog(query=True, text=True)
            charPath = os.path.normpath(os.path.join(self.path_dir_category, charName))
            if not os.path.exists(charPath):
                os.mkdir(charPath)
                for subType in self.l_subTypesBase:
                    os.mkdir(os.path.normpath(os.path.join(charPath, subType)))

            self.LoadCategoryList(self.directory)
            self.assetList['scrollList'].selectByValue(charName)
            
    def DuplicateAssetStructure(self, *args):
        result = mc.promptDialog(
                    title='New Asset',
                    message='Asset Name:',
                    button=['OK', 'Cancel'],
                            defaultButton='OK',
                                        cancelButton='Cancel',
                                        dismissString='Cancel')

        if result == 'OK':
            _currentChar = self.assetList['scrollList'].getSelectedItem()
            _path1  = os.path.normpath(os.path.join(self.path_dir_category, _currentChar))
            
            
            charName = mc.promptDialog(query=True, text=True)
            _path2 = os.path.normpath(os.path.join(self.path_dir_category, charName))
            
            CGMOS.dup_dirsBelow(_path1,_path2)
            
            #if not os.path.exists(charPath):
                #os.mkdir(charPath)
                #for subType in self.l_subTypesBase:
                    #os.mkdir(os.path.normpath(os.path.join(charPath, subType)))

            self.LoadCategoryList(self.directory)
            self.assetList['scrollList'].selectByValue(charName)   
            self.uiFunc_assetList_select()
            
    def CreateSubType(self, *args):
        if not self.path_asset:
            log.error("No asset selected.")
            return

        result = mc.promptDialog(
                    title='New Subtype category'.format(self.subType.capitalize()),
                    message='New SubType Name:'.format(self.subType.capitalize()),
                    button=['OK', 'Cancel'],
                            defaultButton='OK',
                                        cancelButton='Cancel',
                                        dismissString='Cancel')

        if result == 'OK':
            subTypeCat = mc.promptDialog(query=True, text=True)
            subTypeDir = self.path_asset #os.path.normpath(os.path.join(self.path_asset, self.subType)) if self.hasSub else os.path.normpath(self.path_asset)
            if not os.path.exists(subTypeDir):
                os.mkdir(subTypeDir)

            subTypePath = os.path.normpath(os.path.join(subTypeDir, subTypeCat))
            if not os.path.exists(subTypePath):
                os.mkdir(subTypePath)
                
            self.uiFunc_assetList_select()
            self.LoadSubTypeList()

            self.subTypeSearchList['scrollList'].clearSelection()
            self.subTypeSearchList['scrollList'].selectByValue( subTypeCat )
            
            

            if not self.hasVariant:
                self.CreateStartingFile()
                self.LoadVersionList()
                
    def CreateSubTypeRef(self, *args):
        _str_func = 'CreateSubTypeRef'
        filePath = self.versionFile
        if not self.versionFile and not os.path.exists(self.versionFile):
            return False
        
            #file -import -type "mayaBinary"  -ignoreVersion -mergeNamespacesOnClash false -rpr #"wing_birdBase_03" -options "v=0;"  -pr  -importTimeRange "combine" "D:/Dropbox/mrsMakers_share/content/Demo/wing/scenes/birdBase/wing_birdBase_03.mb";
            
            
            
            
        versionList = self.versionList if self.hasSub else self.subTypeSearchList
        existingFiles = versionList['items']

        wantedName = "%s_%s" % (self.assetList['scrollList'].getSelectedItem(), self.subTypeSearchList['scrollList'].getSelectedItem() if self.hasSub else self.subType)
        if self.hasVariant:
            wantedName = "%s_%s" % (wantedName, self.variationList['scrollList'].getSelectedItem())
        
        wantedName = "%s_%s.%s" % (wantedName, self.subType, self.d_tf['general']['mayaFilePref'].getValue())
            
        log.info(log_msg(_str_func,"Wanted: {0}".format(wantedName)))
    
        """
        if len(existingFiles) == 0:
            wantedName = "%s_%02d.mb" % (wantedName, 1)
        else:
            currentFile = mc.file(q=True, loc=True)
            if not os.path.exists(currentFile):
                currentFile = "%s_%02d.mb" % (wantedName, 1)

            baseFile = os.path.split(currentFile)[-1]
            baseName, ext = baseFile.split('.')

            wantedBasename = wantedName #"%s_%s" % (self.assetList['scrollList'].getSelectedItem(), self.subTypeSearchList['scrollList'].getSelectedItem())
            if not wantedBasename in baseName:
                baseName = "%s_%02d" % (wantedBasename, 1)

            noVersionName = '_'.join(baseName.split('_')[:-1])
            versionString = baseName.split('_')[-1]
            versionNumString = re.findall('[0-9]+', versionString)[0]
            versionPrefix = versionString[:versionString.find(versionNumString)]
            version = int(versionNumString)
            
            versionFiles = []
            versions = []
            for item in existingFiles:
                matchString = "^(%s_%s)[0-9]+\.m." % (noVersionName, versionPrefix)
                pattern = re.compile(matchString)
                if pattern.match(item):
                    versionFiles.append(item)
                    versions.append( int(item.split('.')[0].split('_')[-1].replace(versionPrefix, '')) )

            versions.sort()

            if len(versions) > 0:
                newVersion = versions[-1]+1
            else:
                newVersion = 1

            wantedName = "%s_%s%02d.%s" % (noVersionName, versionPrefix, newVersion, ext)"""
        
        #new file
        mc.file(f=True,new=True)
        mc.file(filePath, r=True, ignoreVersion=True, gl=True, mergeNamespacesOnClash=False,
                namespace=self.assetList['scrollList'].getSelectedItem())        
        
        saveLocation = os.path.join(self.path_asset, self.subType)
        if self.hasSub:
            saveLocation = self.path_subType
        if self.hasSub and self.hasVariant:
            saveLocation = self.path_variationDirectory
        
        log.info(log_msg(_str_func,"Save to: {0}".format(saveLocation)))

        saveFile = os.path.normpath(os.path.join(saveLocation, wantedName) ) 
        log.info( "Saving file: %s" % saveFile )
        mc.file( rename=saveFile )
        mc.file( save=True )

        self.LoadVersionList()

        versionList['scrollList'].selectByValue( wantedName )
        self.StoreCurrentSelection()

        self.refreshMetaData()
            
            
            
            
            
            
            

        
        
                
            
            
        
    def CreateSubAsset(self, *args):
        if not self.path_asset:
            log.error("No asset selected.")
            return

        result = mc.promptDialog(
                    title='New {0}'.format(self.subType.capitalize()),
                    message='{0} Name:'.format(self.subType.capitalize()),
                    button=['OK', 'Cancel'],
                            defaultButton='OK',
                                        cancelButton='Cancel',
                                        dismissString='Cancel')

        if result == 'OK':
            subTypeName = mc.promptDialog(query=True, text=True)
            subTypeDir = self.path_subTypeDir #os.path.normpath(os.path.join(self.path_asset, self.subType)) if self.hasSub else os.path.normpath(self.path_asset)
            if not os.path.exists(subTypeDir):
                os.mkdir(subTypeDir)

            subTypePath = os.path.normpath(os.path.join(subTypeDir, subTypeName))
            if not os.path.exists(subTypePath):
                os.mkdir(subTypePath)

            self.LoadSubTypeList()

            self.subTypeSearchList['scrollList'].clearSelection()
            self.subTypeSearchList['scrollList'].selectByValue( subTypeName )

            if not self.hasVariant:
                self.CreateStartingFile()
                self.LoadVersionList()

    def CreateStartingFile(self):
        createPrompt = mc.confirmDialog(
                    title='Create?',
                        message='Save Current File Here?',
                        button=['Yes', 'No', 'Make New File'],
                                                defaultButton='No',
                                                        cancelButton='No',
                                                        dismissString='No')

        if createPrompt == "Yes":
            self.SaveVersion()
        elif createPrompt == 'Make New File':
            mc.file(new=True, f=True)
            self.SaveVersion()

    def CreateVariation(self, *args):
        result = mc.promptDialog(
                    title='New Variation',
                    message='Variation Name:',
                    button=['OK', 'Cancel'],
                            defaultButton='OK',
                                        cancelButton='Cancel',
                                        dismissString='Cancel')

        if result == 'OK':
            variationName = mc.promptDialog(query=True, text=True)
            variationDir = os.path.normpath( os.path.join(self.path_subType, variationName) )
            if not os.path.exists(variationDir):
                os.mkdir(variationDir)

                self.LoadVariationList()
                self.variationList['scrollList'].clearSelection()
                self.variationList['scrollList'].selectByValue(variationName)

                self.CreateStartingFile()

                self.LoadVersionList()

    def SaveVersion(self, *args):
        if not self.path_asset:
            log.error("No asset selected")
            return
        
        _fileType = self.d_tf['general']['mayaFilePref'].getValue()
        versionList = self.versionList if self.hasSub else self.subTypeSearchList
        existingFiles = versionList['items']

        #animationName = self.subTypeSearchList['scrollList'].getSelectedItem()
        wantedName = "%s_%s" % (self.assetList['scrollList'].getSelectedItem(), self.subTypeSearchList['scrollList'].getSelectedItem() if self.hasSub else self.subType)
        if self.hasVariant:
            wantedName = "%s_%s" % (wantedName, self.variationList['scrollList'].getSelectedItem())
        if len(existingFiles) == 0:
            wantedName = "{0}_0{1}.{2}".format(wantedName, 1, _fileType)
        else:
            currentFile = mc.file(q=True, loc=True)
            if not os.path.exists(currentFile):
                wantedName = "{0}_{1}.{2}".format(wantedName, 1, _fileType)
                
                
            print wantedName
            baseFile = os.path.split(currentFile)[-1]
            baseName, ext = baseFile.split('.')
            
            if '_BUILD' in baseName:
                baseName = baseName.replace('_BUILD','')

            wantedBasename = wantedName #"%s_%s" % (self.assetList['scrollList'].getSelectedItem(), self.subTypeSearchList['scrollList'].getSelectedItem())
            if not wantedBasename in baseName:
                baseName = "%s_%02d" % (wantedBasename, 1)

            noVersionName = '_'.join(baseName.split('_')[:-1])
            versionString = baseName.split('_')[-1]
            versionNumString = re.findall('[0-9]+', versionString)[0]
            versionPrefix = versionString[:versionString.find(versionNumString)]
            version = int(versionNumString)
            
            versionFiles = []
            versions = []
            for item in existingFiles:
                matchString = "^(%s_%s)[0-9]+\.m." % (noVersionName, versionPrefix)
                pattern = re.compile(matchString)
                if pattern.match(item):
                    versionFiles.append(item)
                    versions.append( int(item.split('.')[0].split('_')[-1].replace(versionPrefix, '')) )

            versions.sort()

            if len(versions) > 0:
                newVersion = versions[-1]+1
            else:
                newVersion = 1

            wantedName = "%s_%s%02d.%s" % (noVersionName, versionPrefix, newVersion, _fileType)

        saveLocation = os.path.join(self.path_asset, self.subType)
        if self.hasSub:
            saveLocation = self.path_subType
        if self.hasSub and self.hasVariant:
            saveLocation = self.path_variationDirectory

        saveFile = os.path.normpath(os.path.join(saveLocation, wantedName) ) 
        log.info( "Saving file: %s" % saveFile )
        mc.file( rename=saveFile )
        mc.file( save=True )

        self.LoadVersionList()

        versionList['scrollList'].selectByValue( wantedName )
        self.StoreCurrentSelection()

        self.refreshMetaData()

    def OpenDirectory(self, path):
        if os.path.exists(path):
            os.startfile(path)
        else:
            log.warning("Path not found - {0}".format(path))

    def LoadProject(self, path, *args):
        if not os.path.exists(path):
            mel.eval('warning "No Project Set"')
            return
        
        self.mDat = Project.data(filepath=path)
        
        PROJECT.uiProject_load(self, path=path)
        
        self.var_lastProject.setValue( path )
        
        self.uiProject_refreshDisplay()
        self.uiFunc_projectDirtyState(False)
        
        return
    
    
    
    
        _bgColor = self.v_bgc
        try:
            _bgColor = self.mDat.d_colors['project']
        except Exception,err:
            log.warning("No project color stored | {0}".format(err))

        try:self.uiImage_ProjectRow(edit=True, bgc = _bgColor)
        except Exception,err:
            log.warning("Failed to set bgc: {0} | {1}".format(_bgColor,err))

        try:
            vTmp = [MATH.Clamp(1.5 * v,None,2.0) for v in _bgColor]
            vLite = [MATH.Clamp(1.7 * v, .5, 1.0) for v in _bgColor]

            
            self._detailsToggleBtn(edit=True, bgc=vTmp)
            self._projectToggleBtn(edit=True, bgc=vTmp)
            #self.uiScrollList_dirContent(edit=True, bgc = vLite)
            self.uiScrollList_dirContent.v_hlc = vLite
            self.uiScrollList_dirExport.v_hlc = vLite
            
        except Exception,err:
            log.error("Load project color set error | {0}".format(err))
            
            self._detailsToggleBtn(edit=True, bgc=(1.0, .445, .08))
            self._projectToggleBtn(edit=True, bgc=(1.0, .445, .08))
            self.uiScrollList_dirContent(edit=True, hlc = (1.0, .445, .08))
            self.uiScrollList_dirExport(edit=True, hlc = (1.0, .445, .08))

        d_userPaths = self.mDat.userPaths_get()

        if not d_userPaths.get('content'):
            log.error("No Content path found")
            return False
        
        if not d_userPaths.get('export'):
            log.error("No Export path found")
            return False


        if os.path.exists(d_userPaths['content']):
            self.var_lastProject.setValue( path )

            self.LoadCategoryList(d_userPaths['content'])
            self.exportDirectory = d_userPaths['export']
            
            

            self.exportDirectoryTF.setValue( self.exportDirectory )
            # self.optionVarExportDirStore.setValue( self.exportDirectory )
            
            self.l_categoriesBase = self.mDat.assetTypes_get() if self.mDat.assetTypes_get() else self.mDat.d_structure.get('assetTypes', [])
            self.categoryList = [c for c in self.l_categoriesBase]
            
            for i,f in enumerate(os.listdir(self.directory)):
                if os.path.isfile(os.path.join(self.directory, f)):
                    continue
                if f in self.l_categoriesBase:
                    continue
                
                self.categoryList.append(f)

    


            if d_userPaths.get('image') and os.path.exists(d_userPaths.get('image')):
                self.uiImage_Project.setImage(d_userPaths['image'])
            else:
                _imageFailPath = os.path.join(mImagesPath.asFriendly(),
                                                              'cgm_project_{0}.png'.format(self.mDat.d_project.get('type','unity')))
                self.uiImage_Project.setImage(_imageFailPath)

            self.buildMenu_category()

            #self.buildMenu_subTypes()

            mc.workspace( d_userPaths['content'], openWorkspace=True )

            self.assetMetaData = {}

            self.LoadOptions()
        else:
            mel.eval('error "Project path does not exist"')
            
            
        self.uiScrollList_dirContent.mDat = self.mDat
        self.uiScrollList_dirContent.rebuild( self.directory)
        self.uiScrollList_dirExport.rebuild( self.exportDirectory)
        
        
        log.info( "+"*100)
        log.info(self.d_tf['exportOptions']['removeNameSpace'].getValue())
        self.var_mayaFilePref.setValue( self.mDat.d_project.get('mayaFilePref','mb') )
        
        if self.mDat.d_exportOptions:
            self.var_postEuler.setValue( self.mDat.d_exportOptions.get('postEuler',True) )
            self.var_postTangent.setValue( self.mDat.d_exportOptions.get('postTangent',True) )
            
            
            if self.mDat.d_exportOptions.get('removeNameSpace'):
                self.var_removeNamespace.setValue( self.mDat.d_exportOptions.get('removeNameSpace',False) )
                self.removeNamespace = self.mDat.d_exportOptions.get('removeNameSpace',False)
            
            self.var_zeroRoot.setValue( self.mDat.d_exportOptions.get('zeroRoot',False) )
            
            
            
            
        return True
    
    def rename_below(self, mode = 'asset',*args):
        _str_func = 'rename_below'
        
        if mode == 'asset':
            sourceName = self.selectedAsset
            path = self.path_dir_category
        elif mode == 'subtype':
            sourceName = self.selectedSubType
            path = self.path_subTypeDir
        elif mode in ['variant','variation']:
            sourceName = self.selectedVariation
            path = self.path_subType
        else:
            return log.warning(log_msg(_str_func, "Unknown mode: {0}".format(mode)))        
        
        
        
        result = mc.promptDialog(
                    title='Rename {0}'.format(mode.capitalize()),
                    message='Current: {0} | Enter Name:'.format(sourceName),
                    button=['OK', 'Cancel'],
                            defaultButton='OK',
                                        cancelButton='Cancel',
                                        dismissString='Cancel')
        

        if result == 'OK':
            newName = mc.promptDialog(query=True, text=True)
            if not newName:
                return log.warning(log_msg(_str_func, "Must enter a new name"))
            if newName == sourceName:
                return log.warning(log_msg(_str_func, "Must have a different name"))
            
            #_path = r"{0}".format(path)
            #print os.path.normpath(path)
            log.info(log_msg(_str_func,"Current: {0}".format(sourceName)))
            log.info(log_msg(_str_func,"New: {0}".format(newName)))
            #log.info(log_msg(_str_func,"path: {0}".format(_path)))
            log.info(log_msg(_str_func,"path: {0}".format(path)))
            
            
            
            #Do the rename pass...
            try:
                CGMOS.rename_filesInPath(path, sourceName, newName)
            except Exception,err:
                log.error(err)
                return log.warning(log_msg(_str_func, "Error on rename. Check if you have one of the directories open as file browsers"))
            
            #Cat...
            self.LoadCategoryList(self.directory)
            if mode == 'asset':
                self.assetList['scrollList'].selectByValue( newName )
            else:
                self.assetList['scrollList'].selectByValue( self.var_lastAsset.getValue() )
            
            #Sub...
            self.LoadSubTypeList()
            
            if mode == 'subtype':
                self.subTypeSearchList['scrollList'].selectByValue( newName )
            else:
                self.subTypeSearchList['scrollList'].selectByValue( self.var_lastAnim.getValue() )

            
            #Var...
            self.LoadVariationList()
            if mode in ['variant','variation']:
                self.variationList['scrollList'].selectByValue( newName )
    
            elif self.var_lastVariation.getValue():
                self.variationList['scrollList'].selectByValue( self.var_lastVariation.getValue() )
            
            
            #Version...
            self.LoadVersionList()

            if self.var_lastVersion.getValue():
                self.versionList['scrollList'].selectByValue( self.var_lastVersion.getValue() )            
            
            






                
    def RenameAsset(self, *args):
        result = mc.promptDialog(
                    title='Rename Object',
                    message='Enter Name:',
                    button=['OK', 'Cancel'],
                            defaultButton='OK',
                                        cancelButton='Cancel',
                                        dismissString='Cancel')

        if result == 'OK':
            newName = mc.promptDialog(query=True, text=True)
            log.info( 'Renaming %s to %s' % (self.selectedAsset, newName) )

            originalAssetName = self.selectedAsset

            # rename animations
            for animation in os.listdir(os.path.join(self.path_asset, self.subType)):
                for variation in os.listdir(os.path.join(self.path_asset, self.subType, animation)):
                    for version in os.listdir(os.path.join(self.path_asset, self.subType, animation, variation)):
                        if originalAssetName in version:
                            originalPath = os.path.join(self.path_asset, self.subType, animation, variation, version)
                            newPath = os.path.join(self.path_asset, self.subType, animation, variation, version.replace(originalAssetName, newName))
                            os.rename(originalPath, newPath)

            # rename rigs
            for baseFile in os.listdir(self.path_asset):
                if os.path.isfile(os.path.join(self.path_asset, baseFile)):
                    if originalAssetName in baseFile:
                        originalPath = os.path.join(self.path_asset, baseFile)
                        newPath = os.path.join(self.path_asset, baseFile.replace(originalAssetName, newName))
                        os.rename(originalPath, newPath)

            # rename folder
            os.rename(self.path_asset, self.path_asset.replace(originalAssetName, newName))

            self.LoadCategoryList(self.directory)
            self.assetList['scrollList'].selectByValue( newName )

            self.LoadSubTypeList()

            if self.var_lastAnim.getValue():
                self.subTypeSearchList['scrollList'].selectByValue( self.var_lastAnim.getValue() )

            self.LoadVariationList()

            if self.var_lastVariation.getValue():
                self.variationList['scrollList'].selectByValue( self.var_lastVariation.getValue() )

            self.LoadVersionList()

            if self.var_lastVersion.getValue():
                self.versionList['scrollList'].selectByValue( self.var_lastVersion.getValue() )



    def OpenAssetDirectory(self, *args):
        if self.selectedAsset:
            self.OpenDirectory( os.path.join(self.path_dir_category, self.selectedAsset) )
        else:
            self.OpenDirectory( self.path_dir_category )

    def uiPath_mayaOpen(self,path=None):
        _res = mc.fileDialog2(fileMode=1, dir=path)
        if _res:
            log.warning("Opening: {0}".format(_res[0]))
            mc.file(_res[0], o=True, f=True, pr=True)
            return
        log.warning("Unknown path: {0}".format(path))
            
    def uiPath_mayaSaveTo(self,path=None):
        _filter = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;"
        _res = mc.fileDialog2(fileMode=0,dialogStyle=2,dir=path, fileFilter = _filter)
        #fileFilter = 'Maya Files (*.ma *.mb)'
        if _res:
            log.warning("Saving: {0}".format(_res[0]))
            newFile = mc.file(rename = _res[0])
            mc.file(save = 1)        
            
    def uiPath_mayaOpen_subType(self):
        _path = os.path.normpath(os.path.join(self.path_asset, self.subType) )
        if os.path.exists(_path):
            self.uiPath_mayaOpen( _path)
        else:
            log.warning("SubType path doesn't exist")
            
    def uiPath_mayaSaveTo_subType(self):
        _path = os.path.normpath(os.path.join(self.path_asset, self.subType) )        
        if _path:
            self.uiPath_mayaSaveTo( _path )
        else:
            log.warning("SubType path doesn't exist")
            
    def uiPath_mayaOpen_variant(self):
        
        if self.path_variationDirectory:
            self.uiPath_mayaOpen( self.path_variationDirectory )
        else:
            log.warning("Variation path doesn't exist")
            
            
    def uiPath_mayaSaveTo_variant(self):
        if self.path_variationDirectory:
            self.uiPath_mayaSaveTo( self.path_variationDirectory)
        else:
            log.warning("Variation path doesn't exist")
            
    def uiPath_mayaSaveTo_version(self):
        if self.path_versionDirectory:
            self.uiPath_mayaSaveTo( self.path_versionDirectory)
        else:
            log.warning("Version path doesn't exist")

    def OpenSubTypeDirectory(self, *args):
        if self.path_asset:
            self.OpenDirectory( os.path.normpath(os.path.join(self.path_asset, self.subType) ))
        else:
            log.warning("Asset path doesn't exist")

    def OpenVariationDirectory(self, *args):
        self.OpenDirectory(self.path_subType)

    def OpenVersionDirectory(self, *args):
        self.OpenDirectory(self.path_versionDirectory)

    def ReferenceFile(self, *args):
        #if not self.assetList['scrollList'].getSelectedItem():
            #log.info( "No asset selected" )
            #return
        #if not self.subTypeSearchList['scrollList'].getSelectedItem():
            #log.info( "No animation selected" )
            #return
        #if not self.versionList['scrollList'].getSelectedItem():
            #log.info( "No version selected" )
            #return

        filePath = self.versionFile
        if self.versionFile and os.path.exists(self.versionFile):
            mc.file(filePath, r=True, ignoreVersion=True, namespace=self.assetList['scrollList'].getSelectedItem() if self.hasSub else self.selectedAsset)
        else:
            log.info( "Version file doesn't exist" )
            
    def ImportFile(self, *args):
        filePath = self.versionFile
        if self.versionFile and os.path.exists(self.versionFile):
            #file -import -type "mayaBinary"  -ignoreVersion -mergeNamespacesOnClash false -rpr #"wing_birdBase_03" -options "v=0;"  -pr  -importTimeRange "combine" "D:/Dropbox/mrsMakers_share/content/Demo/wing/scenes/birdBase/wing_birdBase_03.mb";

            mc.file(filePath, i=True, ignoreVersion=True,
                    mergeNamespacesOnClash=False,
                    importTimeRange = 'combine')
        else:
            log.info( "Version file doesn't exist" )
    def file_replace(self, *args):
        filePath = self.versionFile
        if self.versionFile and os.path.exists(self.versionFile):
            result = mc.confirmDialog(title='Confirm',
                                      message= "Replacing : {0}".format(self.versionFile),
                                      button=['OK', 'Cancel'],
                                      defaultButton='OK',
                                      cancelButton='Cancel',
                                      dismissString='Cancel')
            if result != 'OK':
                log.error(">> Replacing Cancelled | {0}".format(filePath))
                return False
            mc.file(rn=filePath)
            mc.file(s=True)
        else:
            log.info( "Version file doesn't exist" )
            
    def UpdateAssetTSLPopup(self, *args):
        ''''''
        _str_func = 'UpdateAssetTSLPopup'
        log.debug(_str_func)
        
        self.assetTSLpum.clear()

        renameAssetMB = mUI.MelMenuItem(self.assetTSLpum, label="Rename Asset", command= partial(self.rename_below,'asset') )
        mUI.MelMenuItem(self.assetTSLpum, label="Duplicate Structure", command=self.DuplicateAssetStructure,en=1)
        
        openInExplorerMB = mUI.MelMenuItem(self.assetTSLpum, label="Open In Explorer", command=self.OpenAssetDirectory )
        openMayaFileHereMB = mUI.MelMenuItem(self.assetTSLpum, label="Open In Maya", command=lambda *a:self.uiPath_mayaOpen( os.path.join(self.path_dir_category, self.selectedAsset) ))

        for item in self.assetRigMenuItemList:
            mc.deleteUI(item, menuItem=True)
        for item in self.assetReferenceRigMenuItemList:
            mc.deleteUI(item, menuItem=True)

        self.assetRigMenuItemList = []
        self.assetReferenceRigMenuItemList = []

        openMB = mUI.MelMenuItem(self.assetTSLpum, label="Open", subMenu=True )
        referenceMB = mUI.MelMenuItem(self.assetTSLpum, label="Reference", subMenu=True )

        hasItems = False

        for subType in self.subTypes:
            if self.HasSub(self.category, subType):
                continue

            try:subDir = os.path.join(self.path_asset, subType)
            except:
                continue
            if not os.path.exists(subDir):
                continue

            assetList = ASSET.AssetDirectory(subDir, self.selectedAsset, subType)
            directoryList = assetList.GetFullPaths()

            if len(assetList.versions) == 0:
                continue

            openRigMB = mUI.MelMenuItem(openMB, label=subType, subMenu=True )
            referenceRigMB = mUI.MelMenuItem(referenceMB, label=subType, subMenu=True )

            #rigPath = #os.path.normpath(os.path.join(self.path_asset, "%s_rig.mb" % self.assetList['scrollList'].getSelectedItem() ))
            #if len(assetList.versions) > 0:
                #mc.menuItem( openRigMB, e=True, enable=True )
                #mc.menuItem( referenceRigMB, e=True, enable=True )
            #else:
                #mc.menuItem( openRigMB, e=True, enable=False )
                #mc.menuItem( referenceRigMB, e=True, enable=False )

            for i,rig in enumerate(assetList.versions):
                item = mUI.MelMenuItem( openRigMB, l=rig,
                                                        c = cgmGEN.Callback(self.OpenRig,directoryList[i]))
                self.assetRigMenuItemList.append(item)

                item = mUI.MelMenuItem( referenceRigMB, l=rig,
                                                        c = cgmGEN.Callback(self.ReferenceRig,directoryList[i], self.selectedAsset))
                self.assetReferenceRigMenuItemList.append(item)

                hasItems = True

        if not hasItems:
            openMB(e=True, en=False)
            referenceMB(e=True, en=False)


        self.refreshAssetListMB = mUI.MelMenuItem(self.assetTSLpum, label="Refresh", command=self.LoadCategoryList )

    def UpdateVersionTSLPopup(self, mMenu = None,  *args):	
        for item in self.d_subPops.get(mMenu,[]):
            mc.deleteUI(item, menuItem=True)

        self.d_subPops[mMenu] = []

        asset = self.versionFile

        mPathList = cgmMeta.pathList('cgmProjectPaths')

        project_names = []
        for i,p in enumerate(mPathList.mOptionVar.value):
            mProj = Project.data(filepath=p)
            name = mProj.d_project['name']
            project_names.append(name)

            if self.mDat.userPaths_get().get('content') == mProj.userPaths_get().get('content'):
                continue

            item = mUI.MelMenuItem( mMenu, l=name if project_names.count(name) == 1 else '%s {%i}' % (name,project_names.count(name)-1),
                                                c = partial(self.SendVersionFileToProject,{'filename':asset,'project':p}))
            self.d_subPops[mMenu].append(item)
            #mMenu.append(item)
            
    def SendToBuild(self,*args):
        f = self.versionFile
        if not f:
            return log.error("SendToBuild: No version file found")
        
        log.info ("file: {0}".format(f))
        mStandAlone = BUILDER.ui_toStandAlone()
        mStandAlone.l_files = [f]
        
        
    def SendVersionFileToProject(self, infoDict, *args):
        _str_func = 'ui.SendVersionFileToProject'
        newProject = Project.data(filepath=infoDict['project'])
        _file = infoDict['filename']
        newFilename = os.path.normpath(_file).replace(os.path.normpath(self.mDat.userPaths_get()['content']), os.path.normpath(newProject.userPaths_get()['content']))
        
        log.info( log_msg(_str_func,"Selected: {0}".format(_file)))            
        log.info( log_msg(_str_func,"New: {0}".format(newFilename)))            

        if os.path.exists(newFilename):
            result = mc.confirmDialog(
                            title='Destination file exists!',
                            message='The destination file already exists. Would you like to overwrite it?',
                            button=['Yes', 'Cancel'],
                                        defaultButton='Yes',
                                                    cancelButton='Cancel',
                                                    dismissString='Cancel')

            if result != 'Yes':
                return False

        if not os.path.exists(os.path.dirname(newFilename)):
            log.info( log_msg(_str_func,"Creating path : {0}".format(newFilename)))            
            os.makedirs(os.path.dirname(newFilename))

        copyfile(_file, newFilename)

        #if os.path.exists(newFilename) and os.path.normpath(mc.file(q=True, loc=True)) == os.path.normpath(infoDict['filename']):
        result = 'Cancel'
        if not self.var_alwaysSendReferenceFiles.getValue():
            result = mc.confirmDialog(
                                title='Send Missing References?',
                                message='Copy missing references as well?',
                                button=['Yes', 'Yes and Stop Asking', 'Cancel'],
                                                defaultButton='Yes',
                                                            cancelButton='No',
                                                            dismissString='No')

        if result == 'Yes and Stop Asking':
            self.var_alwaysSendReferenceFiles.setValue(1)

        if result == 'Yes' or self.var_alwaysSendReferenceFiles.getValue():
            log.info( log_msg(_str_func,"Trying References..."))
            for refFile in mc.file(_file,query=True, reference=True):
                if not os.path.exists(refFile):
                    continue

                newRefFilename = os.path.normpath(refFile).replace(os.path.normpath(self.mDat.userPaths_get()['content']), os.path.normpath(newProject.userPaths_get()['content']))
                print newRefFilename
                if not os.path.exists(newRefFilename):
                    if not os.path.exists(os.path.dirname(newRefFilename)):
                        os.makedirs(os.path.dirname(newRefFilename))
                    copyfile(refFile, newRefFilename)

        result = mc.confirmDialog(
                        title='Change Project?',
                        message='Change to the new project?',
                        button=['Yes', 'No'],
                                    defaultButton='Yes',
                                                cancelButton='No',
                                                dismissString='No')

        if result == 'Yes':
            if self.LoadProject(infoDict['project']):
                self.LoadOptions()
        #else:
        #    log.info( log_msg(_str_func,"Path mismatch, no ref possible"))
            
        log.info( log_msg(_str_func,"Done"))

    def SendLatestRigToProject():
        pass

    def OpenRig(self, filename, *args):
        rigPath = filename #os.path.normpath(os.path.join(self.path_asset, "%s_rig.mb" % self.assetList['scrollList'].getSelectedItem() ))
        if os.path.exists(rigPath):
            mc.file(rigPath, o=True, f=True, ignoreVersion=True)

    def ReferenceRig(self, filename, assetName, *args):
        _str_func = 'Scene.ReferenceRig'
        rigPath = filename #os.path.normpath(os.path.join(self.path_asset, "%s_rig.mb" % self.assetList['scrollList'].getSelectedItem() ))

        log.info( '{0} | Referencing file : {1}'.format(_str_func, rigPath) )

        if os.path.exists(rigPath):
            mc.file(rigPath, r=True, ignoreVersion=True, gl=True, mergeNamespacesOnClash=False, namespace=assetName)

    def VerifyAssetDirs(self):
        _str_func = 'Scene.VerifyAssetDirs'
        assetName = self.selectedAsset
        assetPath = os.path.normpath(os.path.join(self.path_dir_category, assetName))
        #subTypes = [x['n'] for x in self.mDat.assetType_get(category).get('content', [{'n':'animation'}])]

        if not os.path.exists(assetPath):
            os.mkdir(charPath)
            log.info('{0}>> Path not found. Appending: {1}'.format(_str_func, assetPath))		
        for subType in self.subTypes:
            subPath = os.path.normpath(os.path.join(assetPath, subType))
            if not os.path.exists(subPath):
                os.mkdir(subPath)
                log.info('{0}>> Path not found. Appending: {1}'.format(_str_func, subPath))

    def AddLastToExportQueue(self, *args):
        if self.variationList != None:
            self.batchExportItems.append( {"category":self.category,
                                           'subType':self.subType,                                           
                                           "asset":self.assetList['scrollList'].getSelectedItem(),
                                           "animation":self.subTypeSearchList['scrollList'].getSelectedItem(),
                                           "variation":self.variationList['scrollList'].getSelectedItem(),
                                           "version":self.versionList['scrollList'].getItems()[-1]} )

        self.RefreshQueueList()

    def AddToExportQueue(self, exportMode = 'export', *args):
        if self.versionList['scrollList'].getSelectedItem() != None:
            self.batchExportItems.append( {"category":self.category,
                                           "path":self.versionFile,
                                           'subType':self.subType,
                                           'exportMode':exportMode,
                                           "asset":self.assetList['scrollList'].getSelectedItem(),
                                           "animation":self.subTypeSearchList['scrollList'].getSelectedItem(),
                                           "variation":self.variationList['scrollList'].getSelectedItem(),
                                           "version":self.versionList['scrollList'].getSelectedItem()} )
        elif self.variationList != None:
            self.batchExportItems.append( {"category":self.category,
                                           "path":None,
                                           'subType':self.subType,
                                           'exportMode':exportMode,
                                           "asset":self.assetList['scrollList'].getSelectedItem(),
                                           "animation":None,#self.subTypeSearchList['scrollList'].getSelectedItem(),
                                           "variation":None, # self.variationList['scrollList'].getSelectedItem(),
                                           "version":self.subTypeSearchList['scrollList'].getItems()[-1]} )
        pprint.pprint(self.batchExportItems[-1])
        self.RefreshQueueList()

    def RemoveFromQueue(self, *args):
        if args[0] == 0:
            idxes = self.queueTSL.getSelectedIdxs()
            print idxes
            idxes.reverse()

            for idx in idxes:
                #del self.batchExportItems[idx-1]
                self.batchExportItems.remove( self.batchExportItems[idx] )
        elif args[0] == 1:
            self.batchExportItems = []

        self.RefreshQueueList()

    def batch_buildFile(self, *args):
        _str_func = 'batch_buildFile'
        log.info(log_start(_str_func))
        
        
        if self.useMayaPy:
            #reload(BATCH)
            log.info('Maya Py!')

            bakeSetName = self.var_bakeSet.getValue()
            deleteSetName = self.var_deleteSet.getValue()
            exportSetName = self.var_exportSet.getValue()

            #if(mc.optionVar(exists='cgm_bake_set')):
                #bakeSetName = mc.optionVar(q='cgm_bake_set')    
            #if(mc.optionVar(exists='cgm_delete_set')):
                #deleteSetName = mc.optionVar(q='cgm_delete_set')
            #if(mc.optionVar(exists='cgm_export_set')):
                #exportSetName = mc.optionVar(q='cgm_export_set')                


            l_dat = []
            d_base = {'removeNamespace' : self.d_tf['exportOptions']['removeNameSpace'].getValue(),
                      'bakeSetName':bakeSetName,
                      'exportSetName':exportSetName,
                      'deleteSetName':deleteSetName,
                      'zeroRoot' : self.d_tf['exportOptions']['zeroRoot'].getValue(),
                      'euler':self.d_tf['exportOptions']['postEuler'].getValue(),
                      'tangent':self.d_tf['exportOptions']['postTangent'].getValue(),
                      }

            for animDict in self.batchExportItems:
                
                categoryDirectory = os.path.normpath(os.path.join( self.directory, animDict["category"] ))
                path_asset = os.path.normpath(os.path.join( categoryDirectory, animDict["asset"] ))
                path_subType = os.path.normpath(os.path.join( path_asset, animDict["subType"], animDict["animation"] ))
                
                if animDict.get('path'):
                    versionFile = animDict.get('path')
                else:
                    path_variationDirectory = os.path.normpath(os.path.join( path_subType, animDict["variation"] ))                    
                    versionFile = os.path.normpath(os.path.join( path_variationDirectory, animDict["version"] ))

                categoryExportPath = os.path.normpath(os.path.join( self.exportDirectory, animDict["category"]))
                exportAssetPath = os.path.normpath(os.path.join( categoryExportPath, animDict["asset"]))
                exportAnimPath = os.path.normpath(os.path.join(exportAssetPath, animDict["subType"]))                
                
                _exportFileName = [animDict["asset"], animDict["animation"]]
                if animDict.get("variation"):
                    _exportFileName.append(animDict["variation"])
                
                exportFileName = "_".join(_exportFileName) + '.fbx'
                    
                #exportFileName = '%s_%s_%s.fbx' % (animDict["asset"], animDict["animation"], animDict["variation"])

                d = {
                    'file':PATHS.Path(versionFile).asString(),
                    #'objs':objs,
                    'mode':-1, #Probably needs to be able to specify this
                    'exportMode':animDict['exportMode'],
                    'exportName':exportFileName,
                    'animationName':animDict["animation"],
                    'exportAssetPath' : PATHS.Path(exportAssetPath).split(),
                    'categoryExportPath' : PATHS.Path(categoryExportPath).split(),
                    'exportAnimPath' : PATHS.Path(exportAnimPath).split(),
                    'updateAndIncrement' : int(mc.checkBox(self.updateCB, q=True, v=True))
                }                

                d.update(d_base)

                l_dat.append(d)



            pprint.pprint(l_dat)
            
            BATCH.create_Scene_batchFile(l_dat)
            return





        for animDict in self.batchExportItems:
            self.assetList['scrollList'].selectByValue( animDict["asset"] )
            self.LoadSubTypeList()
            self.subTypeSearchList['scrollList'].selectByValue( animDict["animation"])
            self.LoadVariationList()
            self.variationList['scrollList'].selectByValue( animDict["variation"])
            self.LoadVersionList()
            self.versionList['scrollList'].selectByValue( animDict["version"])

            mc.file(self.versionFile, o=True, f=True, ignoreVersion=True)

            masterNode = None
            for item in mc.ls("*:master", r=True):
                if len(item.split(":")) == 2:
                    masterNode = item

                if mc.checkBox(self.updateCB, q=True, v=True):
                    rig = ASSET.Asset(item)
                    if rig.UpdateToLatest():
                        self.SaveVersion()

            mc.select(masterNode)

            #mc.confirmDialog(message="exporting %s from %s" % (masterNode, mc.file(q=True, loc=True)))
            self.RunExportCommand(1)


    def RefreshQueueList(self, *args):
        self.queueTSL.clear()
        for i,item in enumerate(self.batchExportItems):
            self.queueTSL.append( "%i ||| Cat: %s | asset: %s | anim: %s | var: %s | version: %s | ----- Mode: [ %s ] " % (
            i,
            item["category"],
            item["asset"],
            item["animation"],
            item["variation"],
            item["version"],
            item['exportMode'],                                                                               
            ))

        if len(self.batchExportItems) > 0:
            mc.frameLayout(self.exportQueueFrame, e=True, collapse=False)
        else:
            mc.frameLayout(self.exportQueueFrame, e=True, collapse=True)

    # args[0]:
    # 0 is bake and prep, don't export
    # 1 is export as a regular asset
    #   - export the asset into the asset/animation directory
    # 2 is export as a cutscene 
    #   - cutscene means it adds the namespace to the 
    #   - asset and exports all of the assets into the
    #   - same directory
    # 3 is export as a rig
    #   - export into the base asset directory with
    #   - just the asset name
    def RunExportCommand(self, *args):
        _str_func = 'RunExportCommand'
        log.info(log_start(_str_func))
        categoryExportPath = os.path.normpath(os.path.join( self.exportDirectory, self.category))
        exportAssetPath = os.path.normpath(os.path.join( categoryExportPath, self.assetList['scrollList'].getSelectedItem()))
        exportAnimPath = os.path.normpath(os.path.join(exportAssetPath, self.subType))

        d_userPaths = self.mDat.userPaths_get()


        postEuler = self.d_tf['exportOptions']['postEuler'].getValue()
        postTangent = self.d_tf['exportOptions']['postTangent'].getValue()
        if postTangent == 'none':
            postTangent = False

        if self.useMayaPy:
            #reload(BATCH)
            log.info('Maya Py!')

            bakeSetName = self.var_bakeSet.getValue()
            deleteSetName = self.var_deleteSet.getValue()
            exportSetName = self.var_exportSet.getValue()
            


            d = {
                'file':mc.file(q=True, sn=True),
                'objs':mc.ls(sl=1),
                'mode':args[0],
                'exportName':self.exportFileName,
                'exportAssetPath' : PATHS.Path(exportAssetPath).split(),
                'categoryExportPath' : PATHS.Path(categoryExportPath).split(),
                'subType' : self.subType,
                'exportAnimPath' : PATHS.Path(exportAnimPath).split(),
                'removeNamespace' : self.d_tf['exportOptions']['removeNameSpace'].getValue(),
                'zeroRoot' : self.d_tf['exportOptions']['zeroRoot'].getValue(),
                'bakeSetName':bakeSetName,
                'exportSetName':exportSetName,
                'deleteSetName':deleteSetName,
                'animationName':self.selectedSubType,
                'tangent':postTangent,
                'euler':postEuler,
            'workspace':d_userPaths['content']
                        }

            #pprint.pprint(d)

            BATCH.create_Scene_batchFile([d])
            return


        ExportScene(mode = args[0],
                    exportObjs = None,
                    exportName = self.exportFileName,
                    exportAssetPath = exportAssetPath,
                    subType = self.subType,
                    categoryExportPath = categoryExportPath,
                    exportAnimPath = exportAnimPath,
                    removeNamespace = self.d_tf['exportOptions']['removeNameSpace'].getValue(),
                    zeroRoot = self.d_tf['exportOptions']['zeroRoot'].getValue(),
                    animationName = self.selectedSubType,
                    tangent=postTangent,
                    euler=postEuler,                            
                    workspace=d_userPaths['content']
                    )        

        return True





def BatchExport(dataList = []):
    _str_func = 'BatchExport'
    log.info(log_start(_str_func))
    
    t1 = time.time()


    for fileDat in dataList:
        _d = {}

        _d['categoryExportPath'] = PATHS.NICE_SEPARATOR.join(fileDat.get('categoryExportPath'))
        _d['exportAnimPath'] = PATHS.NICE_SEPARATOR.join(fileDat.get('exportAnimPath'))
        _d['exportAssetPath'] = PATHS.NICE_SEPARATOR.join(fileDat.get('exportAssetPath'))
        _d['subType'] = fileDat.get('subType')
        _d['exportName'] = fileDat.get('exportName')
        mFile = PATHS.Path(fileDat.get('file'))
        _d['mode'] = int(fileDat.get('mode'))
        _d['exportMode'] = fileDat.get('exportMode')
        _d['exportObjs'] = fileDat.get('objs')
        _removeNamespace =  fileDat.get('removeNamespace', "False")
        _d['removeNamespace'] = False if _removeNamespace == "False" else True
        _zeroRoot =  fileDat.get('zeroRoot', "False")
        _d['zeroRoot'] = False if _zeroRoot == "False" else True
        _d['deleteSetName'] = fileDat.get('deleteSetName')
        _d['exportSetName'] = fileDat.get('exportSetName')
        _d['bakeSetName'] = fileDat.get('bakeSetName')
        _d['animationName'] = fileDat.get('animationName')
        _d['workspace'] = fileDat.get('workspace')
        _d['updateAndIncrement'] = fileDat.get('updateAndIncrement')
        
        _euler =  fileDat.get('euler', "0")        
        _d['euler'] = False if _euler == '0' else True
        _d['tangent'] = fileDat.get('tangent')

        log.info(mFile)
        #pprint.pprint(_d)


        _path = mFile.asString()
        if not mFile.exists():
            log.error("Invalid file: {0}".format(_path))
            continue

        mc.file(_path, open = 1, f = 1, iv = 1)

        # if not _d['exportObjs']:
        # 	log.info(log_sub(_str_func,"Trying to find masters..."))

        # 	l_masters = []
        # 	for item in mc.ls("*:master", r=True):
        # 		if len(item.split(":")) == 2:
        # 			masterNode = item
        # 			l_masters.append(item)

        # 		#if mc.checkBox(self.updateCB, q=True, v=True):
        # 			#rig = ASSET.Asset(item)
        # 			#if rig.UpdateToLatest():
        # 				#self.SaveVersion()

        # 	if l_masters:
        # 		log.info(log_msg(_str_func,"Found..."))
        # 		pprint.pprint(l_masters)

        # 		_d['exportObjs'] = l_masters


        #if _objs:
        #    mc.select(_objs)
        ExportScene(**_d)        

    t2 = time.time()
    log.info("|{0}| >> Total Time >> = {1} seconds".format(_str_func, "%0.4f"%( t2-t1 )))         

    return

    mFile = PATHS.Path(f)

    if not mFile.exists():
        raise ValueError,"Invalid file: {0}".format(f)

    _path = mFile.asFriendly()

    log.info("Good Path: {0}".format(_path))
    """
    if 'template' in _path:
        _newPath = _path.replace('template','build')
    else:"""
    _name = mFile.name()
    _d = mFile.up().asFriendly()
    log.debug(log_msg(_str_func,_name))
    _newPath = os.path.join(_d,_name+'_BUILD.{0}'.format(mFile.getExtension()))        

    log.info("New Path: {0}".format(_newPath))

    #log_msg(_str_func,'File Open...')
    mc.file(_path, open = 1, f = 1)

    #log_msg(_str_func,'Process...')
    t1 = time.time()

    try:
        if not blocks:
            #log_sub(_str_func,'No blocks arg')

            ml_masters = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',
                                                         nTypes=['transform','network'],
                                                         mAttrs='blockType=master')

            for mMaster in ml_masters:
                #log_sub(_str_func,mMaster)

                RIGBLOCKS.contextual_rigBlock_method_call(mMaster, 'below', 'atUtils','changeState','rig',forceNew=False)

                ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(mMaster,'below',True,False)
                l_fails = []

                for mSubBlock in ml_context:
                    _state =  mSubBlock.getState(False)
                    if _state != 4:
                        l_fails.append(mSubBlock)

                if l_fails:
                    log.info('The following failed...')
                    pprint.pprint(l_fails)
                    raise ValueError,"Modules failed to rig: {0}".format(l_fails)

                log.info("Begin Rig Prep cleanup...")
                '''

                Begin Rig Prep process

                '''
                mPuppet = mMaster.moduleTarget#...when mBlock is your masterBlock

                if postProcesses:
                    log.info('mirror_verify...')
                    mPuppet.atUtils('mirror_verify')
                    log.info('collect worldSpace...')                        
                    mPuppet.atUtils('collect_worldSpaceObjects')
                    log.info('qss...')                        
                    mPuppet.atUtils('qss_verify',puppetSet=1,bakeSet=1,deleteSet=1,exportSet=1)
                    log.info('proxyMesh...')
                    mPuppet.atUtils('proxyMesh_verify')
                    log.info('ihi...')                        
                    mPuppet.atUtils('rigNodes_setAttr','ihi',0)
                    log.info('rig connect...')                        
                    mPuppet.atUtils('rig_connectAll')
    except Exception,err:
        log.error(err)


    t2 = time.time()
    log.info("|{0}| >> Total Time >> = {1} seconds".format(_str_func, "%0.4f"%( t2-t1 ))) 


    #log_msg(_str_func,'File Save...')
    newFile = mc.file(rename = _newPath)
    mc.file(save = 1)            





# args[0]:
# -1 is unknown mode
# 0 is bake and prep, don't export
# 1 is export as a regular asset
#   - export the asset into the asset/animation directory
# 2 is export as a cutscene 
#   - cutscene means it adds the namespace to the 
#   - asset and exports all of the assets into the
#   - same directory
# 3 is export as a rig
#   - export into the base asset directory with
#   - just the asset name

def ExportScene(mode = -1,
                exportObjs = None,
                exportName = None,
                categoryExportPath = None,
                subType = None,
                exportAssetPath = None,
                exportAnimPath = None,
                exportMode = None,
                removeNamespace = False,
                zeroRoot = False,
                                bakeSetName = 'bake_tdSet',
                exportSetName = 'export_tdSet',
                deleteSetName = 'delete_tdSet',
                animationName = None,
                workspace = None,
                updateAndIncrement = False,
                euler = False,
                tangent = False,
                ):
    
    if workspace:
        mc.workspace( workspace, openWorkspace=True )

    #pprint.pprint(vars())
    
    #exec(self.exportCommand)
    import cgm.core.tools.bakeAndPrep as bakeAndPrep
    reload(bakeAndPrep)
    import cgm.core.mrs.Shots as SHOTS
    _str_func = 'ExportScene'
    log.info(log_start(_str_func))

    if not exportObjs:
        exportObjs = mc.ls(sl=True)

    cameras = []
    exportCams = []

    for obj in exportObjs:
        log.info("Checking: {0}".format(obj))
        if mc.listRelatives(obj, shapes=True, type='camera'):
            cameras.append(obj)
            exportCams.append( bakeAndPrep.MakeExportCam(obj) )
            exportObjs.remove(obj)

    exportObjs += exportCams

    addNamespaceSuffix = False
    exportFBXFile = False
    exportAsRig = False
    exportAsCutscene = False


    log.info("mode check...")
    d_exportModes = {'export':1,
                     'cutscene':2,
                     'rig':3}
    
    if exportMode is not None:
        mode = d_exportModes[exportMode]
    
    if not exportObjs:
        exportObjs = []
        for s in mc.ls('*%s' % exportSetName, r=True):
            if len(s.split(':')) == 2:
                ns = s.split(':')[0]
                for p in mc.ls(mc.sets(s,q=True)[0], l=True)[0].split('|'):
                    if mc.objExists(p) and ns in p:
                        exportObjs.append(p)
                        break
                    
            if len(s.split(':')) == 1:
                objName = s.replace('_%s' % exportSetName, '')
                if mc.objExists(objName):
                    exportObjs.append(objName)
    
                        
    if mode == -1:
        log.info("unknown mode, attempting to auto detect")

                        
        if len(exportObjs) > 1:
            log.info("More than one export obj found, setting cutscene mode: 2")
            mode = 2
        elif len(exportObjs) == 1:
            log.info("One export obj found, setting regular asset mode: 1")
            mode = 1
        else:
            log.info("Auto detection failed. Exiting.")
            return

    if mode > 0:
        exportFBXFile = True
    
    log.info("Mode: {0}".format(mode))    
    pprint.pprint(exportObjs)

    if len(exportObjs) > 1 and mode != 2:
        log.info("Multi check")            
        result = mc.confirmDialog(
                    title='Multiple Object Selected',
                    message='Will export in cutscene mode, is this what you intended? If not, hit Cancel, select one object and try again.',
                    button=['Yes', 'Cancel'],
                            defaultButton='Yes',
                            cancelButton='Cancel',
                            dismissString='Cancel')

        if result != 'Yes':
            return False

        addNamespaceSuffix = True
        exportAsCutscene = True

    if mode== 2:
        log.info("mode 2...")        
        addNamespaceSuffix = True
        exportAsCutscene = True
    if mode == 3:
        log.info("mode 3...")                
        exportAsRig = True

    # make the relevant directories if they dont exist
    #categoryExportPath = os.path.normpath(os.path.join( self.exportDirectory, self.category))

    #log.info("category path...")
    #if not os.path.exists(categoryExportPath):
    #    os.mkdir(categoryExportPath)
    #exportAssetPath = os.path.normpath(os.path.join( categoryExportPath, self.assetList['scrollList'].getSelectedItem()))

    #log.info("asset path...")

    #if not os.path.exists(exportAssetPath):
    #    os.mkdir(exportAssetPath)
    log.info(log_msg(_str_func,"Pathcheck..."))
    if not exportAnimPath:
        exportAnimPath = os.path.normpath(os.path.join(exportAssetPath, subType))
    log.info("exportPath: {0}".format(exportAnimPath))                
    
    
    #pprint.pprint(vars())
    #return

    #if not os.path.exists(exportAnimPath):
        #log.info("making export anim path...")

        #os.mkdir(exportAnimPath)
        ## create empty file so folders are checked into source control
        #f = open(os.path.join(exportAnimPath, "filler.txt"),"w")
        #f.write("filler file")
        #f.close()
    
    if '.' in animationName:
        animationName = animationName.split('.')[0]
        
    pprint.pprint(vars())
    if exportAsCutscene:
        log.info("export as cutscene...")
        if animationName is not None:
            exportAnimPath = os.path.normpath(os.path.join(exportAnimPath, animationName))
        
        CGMOS.mkdir_recursive(exportAnimPath)
        #if not os.path.exists(exportAnimPath):
        #    os.mkdir(exportAnimPath)

    exportFiles = []

    log.info("bake prep...")

    # rename for safety
    loc = mc.file(q=True, loc=True)
    base, ext = os.path.splitext(loc)
    bakedLoc = "%s_baked%s" % (base, ext)

    mc.file(rn=bakedLoc)

    if not bakeSetName:
        bakeSetName = cgmMeta.cgmOptionVar('cgm_bake_set', varType="string",defaultValue = 'bake_tdSet').getValue()
    if not deleteSetName:
        deleteSetName = cgmMeta.cgmOptionVar('cgm_delete_set', varType="string",defaultValue = 'delete_tdSet').getValue()
    if not exportSetName:
        exportSetName = cgmMeta.cgmOptionVar('cgm_export_set', varType="string",defaultValue = 'export_tdSet').getValue()  

    animList = SHOTS.AnimList()
    #find our minMax
    l_min = []
    l_max = []

    for shot in animList.shotList:
        l_min.append(min(shot[1]))
        l_max.append(max(shot[1]))

    if l_min:
        _start = min(l_min)
    else:
        _start = None

    if l_max:
        _end = max(l_max)
    else:
        _end = None

    log.info( log_sub(_str_func,'Bake | start: {0} | end: {1}'.format(_start,_end)) )
    

    #Bake Check -----------------------------------------------------------------------------------------------
    #if mc.objExists(bakeSetName) and mc.sets(bakeSetName, q=True):
    #    log.info("bake...")        
    bakeAndPrep.Bake(exportObjs,bakeSetName,startFrame= _start, endFrame= _end,
                     euler=euler,tangent=tangent)
    #else:
    #    log.info("bake skip...")
        
        

    mc.loadPlugin("fbxmaya")

    for obj in exportObjs:			
        log.info( log_sub(_str_func,'On: {0}'.format(obj)) )

        cgmObj = cgmMeta.asMeta(obj)
        mc.select(obj)

        assetName = obj.split(':')[0].split('|')[-1]
        exportFile = os.path.normpath(os.path.join(exportAnimPath, exportName) )

        if( addNamespaceSuffix ):
            exportFile = exportFile.replace(".fbx", "_%s.fbx" % assetName )
        if( exportAsRig ):
            exportFile = os.path.normpath(os.path.join(exportAssetPath, '{}_rig.fbx'.format( assetName )))

        bakeAndPrep.Prep(removeNamespace=removeNamespace, deleteSetName=deleteSetName,exportSetName=exportSetName, zeroRoot=zeroRoot)

        exportTransforms = mc.ls(sl=True)

        mc.select(exportTransforms, hi=True)		

        log.info("Heirarchy...")

        for i,o in enumerate(mc.ls(sl=1)):
            log.info("{0} | {1}".format(i,o))

        if(exportFBXFile):
            mel.eval('FBXExportSplitAnimationIntoTakes -c')
            for shot in animList.shotList:
                log.info( log_msg(_str_func, "shot..."))
                log.info(shot)
                mel.eval('FBXExportSplitAnimationIntoTakes -v \"{}\" {} {}'.format(shot[0], shot[1][0], shot[1][1]))
            
            exportDir = os.path.split(exportFile)[0]
            if not os.path.exists(exportDir):
                log.info("making export dir... {0}".format(exportDir))
                os.makedirs(exportDir)

            log.info('Export Command: FBXExport -f \"{}\" -s'.format(exportFile))
            mel.eval('FBXExport -f \"{}\" -s'.format(exportFile.replace('\\', '/')))

            if len(exportObjs) > 1 and removeNamespace:
                # Deleting the exported transforms in case another file has duplicate export names
                mc.delete(cgmObj.mNode)
                try:
                    mc.delete(exportTransforms)
                except:
                    pass

    return True



def PurgeData():

    optionVarProjectStore       = cgmMeta.cgmOptionVar("cgmVar_projectCurrent", varType = "string")
    optionVarProjectStore.purge()

    optionVarLastAssetStore     = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_asset", varType = "string")
    optionVarLastAssetStore.purge()

    optionVarLastAnimStore      = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_animation", varType = "string")
    optionVarLastAnimStore.purge()

    optionVarLastVariationStore = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_variation", varType = "string")
    optionVarLastVariationStore.purge()

    optionVarLastVersionStore   = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_version", varType = "string")
    optionVarLastVersionStore.purge()

    showAllFilesStore           = cgmMeta.cgmOptionVar("cgmVar_sceneUI_show_all_files", defaultValue = 0)
    showAllFilesStore.purge()

    removeNamespaceStore        = cgmMeta.cgmOptionVar("cgmVar_sceneUI_remove_namespace", defaultValue = 0)
    removeNamespaceStore.purge()

    categoryStore               = cgmMeta.cgmOptionVar("cgmVar_sceneUI_category", defaultValue = 0)
    categoryStore.purge()

    alwaysSendReferenceFiles    = cgmMeta.cgmOptionVar("cgmVar_sceneUI_last_version", defaultValue = 0)
    alwaysSendReferenceFiles.purge()