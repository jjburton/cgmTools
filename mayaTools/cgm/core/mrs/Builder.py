"""
------------------------------------------
Builder: cgm.core.mrs
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
import random
import re
import copy
import time
import pprint
import os
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


# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as RIGMETA
from cgm.core import cgm_PuppetMeta as PUPPETMETA
from cgm.core.classes import GuiFactory as CGMUI
reload(CGMUI)
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.classes import NodeFactory as NODEFAC
from cgm.core.cgmPy import path_Utils as PATH
from cgm.core.mrs import RigBlocks as RIGBLOCKS
from cgm.core.lib import shared_data as SHARED
from cgm.core.mrs.lib import builder_utils as BUILDERUTILS
from cgm.core.mrs.lib import general_utils as BLOCKGEN
import cgm.core.tools.lib.tool_chunks as UICHUNKS
import cgm.core.tools.toolbox as TOOLBOX
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.markingMenus.lib.contextual_utils as CONTEXT
import cgm.core.tools.snapTools as SNAPTOOLS

for m in BLOCKGEN,BLOCKSHARE,BUILDERUTILS,SHARED,CONTEXT:
    reload(m)
_d_blockTypes = {}

# Factory 
#=====================================================================================================
import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

#>>> Root settings =============================================================
__version__ = '1.03022019'
_sidePadding = 25

def check_cgm():
    return
    try:
        cgmMeta.cgmNode(nodeType='decomposeMatrix').delete()
    except:
        import cgm
        cgm.core._reload()
        
class ui_stepBuild(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmBuilderSteppped'    
    WINDOW_TITLE = 'cgmBuilder | Stepped | - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 200,275
    
    _d_ui_annotations = {'select':"Select rigBlocks in maya from ui."}
    def __init__(self,mBlock = None, *a,**kws):
        self.mBlock = cgmMeta.validateObjArg(mBlock,'cgmRigBlock',True)
        self.block = None
        if mBlock:
            self.block = self.mBlock.mNode
        super(ui_stepBuild, self).__init__(*a,**kws)
        
    def insert_init(self,*args,**kws):
        _str_func = 'post_win.insert_init'
        #kws = self.kws
        #args = self.args
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        #log.debug(self.__call__(q=True, title=True))
        
        self.__version__ = __version__
        self.__toolName__ = 'Builder'		
        self.WINDOW_TITLE = ui_stepBuild.WINDOW_TITLE
        self.DEFAULT_SIZE = ui_stepBuild.DEFAULT_SIZE
        self.str_lastStep = 'None'
        self.var_buildProfile = cgmMeta.cgmOptionVar('cgmVar_cgmMRSBuildProfile',
                                                    defaultValue = 'unityMed')
                
        
    def build_menus(self):pass
    
    @cgmGEN.Timer
    def uiFunc_process(self):
        _str_func = 'uiFunc_process[{0}]'.format(self.__class__.TOOLNAME)
        log.debug("|{0}| >>...".format(_str_func))
        try:
            if not self.mBlock:
                if self.block:
                    self.mBlock = cgmMeta.validateObjArg(self.block,'cgmRigBlock',True)
                    
            if not self.mBlock:
                return log.warning("|Post| >> No Block loaded")

            self.uiStatus(edit=True,vis=True,label = 'Processing...')
            
            """
            l_toDo = []
            l_order = ['Mirror Verify','Gather Space Drivers',
                       'bakeQSS','deleteQSS','exportQSS',
                       'isHistoricallyInteresting','proxyMesh',
                       'connectRig','Delete Blocks']
            d_keyToFunction = {'Mirror Verify':'mirror_verify',
                               'Gather Space Drivers':'collect_worldSpaceObjects',
                               'proxyMesh':'proxyMesh_verify',
                               'connectRig':'rig_connectAll'}
            for k in l_order:
                log.debug("|{0}| >> {1}...".format(_str_func,k)+'-'*20)
                
                if self._dCB_reg[k].getValue():#self.__dict__['cgmVar_mrsPostProcess_{0}'.format(k)].getValue():
                    l_toDo.append(k)
                    
                    
            if not l_toDo:
                return log.warning("|Post| >> No options selected")
            
            for v in ['proxyMesh','connectRig']:
                if v in l_toDo:
                    self.uiStatus(edit=True,vis = True,label='Rig Reset...')
                    cgmUI.progressBar_test(self.uiPB_test,10)                    
                    self.mBlock.atUtils('anim_reset')
                    break
            
            lenDo = len(l_toDo)
            for i,k in enumerate(l_toDo):
                log.debug("|{0}| >> Processing: {1}...".format(_str_func,k)+'-'*30)
                self.uiStatus(edit=True,vis = True, label=" {0} | {1}/{2}".format(k,i+1,lenDo))
                
                if k in ['Gather Space Drivers','Mirror Verify','connectRig','proxyMesh']:
                    self.mBlock.atUtils(d_keyToFunction.get(k),progressBar=self.uiPB_test)
                elif 'QSS' in k:
                    d_qss = {'bakeQSS':{'blockSet':0,'bakeSet':1,'deleteSet':0,'exportSet':0},
                             'deleteQSS':{'blockSet':0,'bakeSet':0,'deleteSet':1,'exportSet':0},
                             'exportQSS':{'blockSet':0,'bakeSet':0,'deleteSet':0,'exportSet':1}}
                    self.mBlock.atUtils('qss_verify',**d_qss.get(k))
                    cgmUI.progressBar_test(self.uiPB_test,100)
                elif k == 'isHistoricallyInteresting':
                    self.mBlock.atUtils('rigNodes_setAttr','ihi',0,self.uiPB_test)
                elif k == 'Delete Blocks':
                    pass
                else:
                    log.warning("Finish {0}".format(k))
                    cgmUI.progressBar_test(self.uiPB_test,100)
            """
                
        finally:
            self.uiStatus(edit=True,vis=False)
            cgmUI.progressBar_end(self.uiPB_test)
            
    @cgmGEN.Timer
    def step(self,fnc=None):
        #mc.progressBar(mayaMainProgressBar, edit=True,
                       #status = "|{0}| >>Rig>> step: {1}...".format(self.d_block['shortName'],fnc), progress=i+1)    

        mc.undoInfo(openChunk=True,chunkName=fnc)
        log.debug(fnc)
        _fncShort = self.d_funcToShort.get(fnc)
        self.uiStatus(edit=True,label="Started: {0}".format(_fncShort))
        err=None
        _short = self.mBlock.mNode
        
        if _fncShort not in ['dataBuffer']:
            ATTR.store_info(_short, 'rigStepBuffer',_fncShort )
        try:
            getattr(self.mRigFac.d_block['buildModule'],fnc)(self.mRigFac)            
        except Exception,err:
            log.error(err)
        
        finally:
            mc.undoInfo(closeChunk=True)
            #self.uiStatus(edit=True,vis=True,label="Done: {0}".format(_fncShort))
            if err is not None:
                cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
                self.uiStatus(edit=True,label="Failed: {0}".format(_fncShort))
            elif fnc == self.l_buildOrder[-1]:
                self.uiStatus(edit=True,label="Done")
                if ATTR.has_attr(_short,'rigStepBuffer'):
                    ATTR.delete(_short,'rigStepBuffer')
            else:
                self.uiFunc_updateStatus()
                

                

    def uiFunc_updateStatus(self):
        if not self.mBlock:
            self.uiStatus(edit=1,
                          label='...')
            return log.error("No block loaded")
        
        _status = self.mBlock.getMayaAttr('rigStepBuffer')
        if _status:
            self.uiStatus(edit=1,
                          label="State: {0}".format(_status))
        else:
            self.uiStatus(edit=1,
                          label=self.str_lastStep)
            
            
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        log.debug("|{0}| >> mBlock: {1}".format(_str_func,self.mBlock))
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        _inside = mUI.MelColumnLayout(_MainForm)
        if self.mBlock:
            _strBlock = self.mBlock.p_nameBase
        else:
            _strBlock = self.mBlock
            
        SetHeader = cgmUI.add_Header('Block: {0}'.format(_strBlock))
        
        #mc.setParent(_MainForm)
        self.uiStatus = mUI.MelButton(_MainForm,bgc=SHARED._d_gui_state_colors.get('warning'),
                                      c=lambda *a:self.uiFunc_updateStatus(),
                                      ann="Query the last buffered state and update status",
                                      label='...',
                                      h=20)
        #mUI.MelLabel(_MainForm,
        #                             vis=True,
        #                             bgc = SHARED._d_gui_state_colors.get('warning'),
        #                             label = '...',
        #                             h=20)        
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)
        
        if not self.block:
            self.uiStatus(edit=True,vis=True,label="Must have something loaded")
            return
        elif self.mBlock.blockState != 'skeleton':
            self.uiStatus(edit=True,vis=True,label="Block must be skeleton state")            
            return log.error("{0} Block must be skeleton state. Found: {1}".format(self.mBlock.p_nameShort,self.mBlock.blockState))
            pass
        
        mRigFac = self.mBlock.asRigFactory(autoBuild=False)
        self.mRigFac = mRigFac
        mModule = mRigFac.d_block['buildModule']
        
        #SingleChecks======================================================================
        mRow_buttons = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 2)
        CGMUI.add_Button(mRow_buttons, "Reload",
                         cgmGEN.Callback(reload,mModule),
                         "Reload blockModule")
        CGMUI.add_Button(mRow_buttons, "Log Self",
                         cgmGEN.Callback( mRigFac.log_self),
                         "Log Rig Factory")
        mRow_buttons.layout()
        
        #SingleChecks======================================================================
        mRow_buttons2 = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 2)
        CGMUI.add_Button(mRow_buttons2, "INFO",
                         cgmGEN.Callback(mModule.log.setLevel,mModule.logging.INFO),
                         "Reload blockModule")
        CGMUI.add_Button(mRow_buttons2, "DEBUG",
                         cgmGEN.Callback(mModule.log.setLevel,mModule.logging.DEBUG),
                         "Log Rig Factory")
        mRow_buttons2.layout()        
        
        #Danger!!!!!!======================================================================
        mc.setParent(_inside)
        cgmUI.add_Header('Build Order')
        
        
        _l_buildOrder = mRigFac.d_block['buildModule'].__dict__.get('__l_rigBuildOrder__')
        if not _l_buildOrder:
            raise ValueError,"No build order found"
        _len = len(_l_buildOrder)
        self.d_funcToShort = {}
        self.l_buildOrder = _l_buildOrder
        
        for i,fnc in enumerate(_l_buildOrder):
            _short = '_'.join(fnc.split('_')[1:])
            self.d_funcToShort[fnc] = _short

            CGMUI.add_Button(_inside, _short,
                             cgmGEN.Callback(self.step,fnc),
                             "Process: {0}".format(_short))            
        
        
        
        mc.setParent(_inside)
        CGMUI.add_LineBreak()
        self.uiFunc_updateStatus()
        """
        _button = mc.button(parent=_MainForm,
                            l = 'Process',
                            ut = 'cgmUITemplate',
                            #c = cgmGEN.Callback(cgmUI.progressBar_test,self.uiPB_test,10000),
                            c = cgmGEN.Callback(self.uiFunc_process),
                            ann = 'Test progress bar')"""
        
        
        
        #_row_cgm = cgmUI.add_cgmFooter(_MainForm)
        mc.setParent(_MainForm)
 
        
        #_rowProgressBar = mUI.MelRow(_MainForm)

        _MainForm(edit = True,
                  af = [(_inside,"top",0),
                        (_inside,"left",0),
                        (_inside,"right",0),
                        (self.uiStatus,"left",0),
                        (self.uiStatus,"right",0),
                        #(self.uiPB_test,"left",0),
                        #(self.uiPB_test,"right",0),                        
                        #(_row_cgm,"left",0),
                        #(_row_cgm,"right",0),
                        (self.uiStatus,"bottom",0),
    
                        ],
                  ac = [(_inside,"bottom",0,self.uiStatus),
                        #(_button,"bottom",0,_row_cgm),
                        #(self.uiPB_test,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(self.uiStatus,"top")])
        
class ui_post(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmBuilderPost'    
    WINDOW_TITLE = 'cgmBuilder | Post | - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 200,230
    
    _d_ui_annotations = {'select':"Select rigBlocks in maya from ui."}
    def __init__(self,mPuppet = None, *a,**kws):
        self.mPuppet = cgmMeta.validateObjArg(mPuppet,'cgmRigPuppet',True)
        self.puppet = None
        if mPuppet:
            self.puppet = self.mPuppet.mNode
        super(ui_post, self).__init__(*a,**kws)
        
    def insert_init(self,*args,**kws):
        _str_func = 'post_win.insert_init'
        #kws = self.kws
        #args = self.args
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        #log.debug(self.__call__(q=True, title=True))
        
        self.__version__ = __version__
        self.__toolName__ = 'Builder'		
        self.WINDOW_TITLE = ui_post.WINDOW_TITLE
        self.DEFAULT_SIZE = ui_post.DEFAULT_SIZE

        self.var_buildProfile = cgmMeta.cgmOptionVar('cgmVar_cgmMRSBuildProfile',
                                                    defaultValue = 'unityMed')
                
        
    def build_menus(self):pass
    
    @cgmGEN.Timer
    def uiFunc_process(self):
        _str_func = 'uiFunc_process[{0}]'.format(self.__class__.TOOLNAME)
        log.debug("|{0}| >>...".format(_str_func))
        try:
            if not self.mPuppet:
                if self.puppet:
                    self.mPuppet = cgmMeta.validateObjArg(self.puppet,'cgmRigPuppet',True)
                    
            if not self.mPuppet:
                return log.warning("|Post| >> No Puppet loaded")

            self.uiStatus(edit=True,vis=True,label = 'Processing...')
            
            
            l_toDo = []
            l_order = ['Mirror Verify','Gather Space Drivers',
                       'bakeQSS','deleteQSS','exportQSS',
                       'isHistoricallyInteresting','proxyMesh',
                       'connectRig','Delete Blocks']
            d_keyToFunction = {'Mirror Verify':'mirror_verify',
                               'Gather Space Drivers':'collect_worldSpaceObjects',
                               'proxyMesh':'proxyMesh_verify',
                               'connectRig':'rig_connectAll'}
            for k in l_order:
                log.debug("|{0}| >> {1}...".format(_str_func,k)+'-'*20)
                
                if self._dCB_reg[k].getValue():#self.__dict__['cgmVar_mrsPostProcess_{0}'.format(k)].getValue():
                    l_toDo.append(k)
                    
                    
            if not l_toDo:
                return log.warning("|Post| >> No options selected")
            
            for v in ['proxyMesh','connectRig']:
                if v in l_toDo:
                    self.uiStatus(edit=True,vis = True,label='Rig Reset...')
                    cgmUI.progressBar_test(self.uiPB_test,10)                    
                    self.mPuppet.atUtils('anim_reset')
                    break
            
            lenDo = len(l_toDo)
            for i,k in enumerate(l_toDo):
                log.debug("|{0}| >> Processing: {1}...".format(_str_func,k)+'-'*30)
                self.uiStatus(edit=True,vis = True, label=" {0} | {1}/{2}".format(k,i+1,lenDo))
                
                if k in ['Gather Space Drivers','Mirror Verify','connectRig','proxyMesh']:
                    self.mPuppet.atUtils(d_keyToFunction.get(k),progressBar=self.uiPB_test)
                elif 'QSS' in k:
                    d_qss = {'bakeQSS':{'puppetSet':0,'bakeSet':1,'deleteSet':0,'exportSet':0},
                             'deleteQSS':{'puppetSet':0,'bakeSet':0,'deleteSet':1,'exportSet':0},
                             'exportQSS':{'puppetSet':0,'bakeSet':0,'deleteSet':0,'exportSet':1}}
                    self.mPuppet.atUtils('qss_verify',**d_qss.get(k))
                    cgmUI.progressBar_test(self.uiPB_test,100)
                elif k == 'isHistoricallyInteresting':
                    self.mPuppet.atUtils('rigNodes_setAttr','ihi',0,self.uiPB_test)
                elif k == 'Delete Blocks':
                    pass
                else:
                    log.warning("Finish {0}".format(k))
                    cgmUI.progressBar_test(self.uiPB_test,100)
                
        finally:
            self.uiStatus(edit=True,vis=False)
            cgmUI.progressBar_end(self.uiPB_test)
        
    
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        log.debug("|{0}| >> mPuppet: {1}".format(_str_func,self.mPuppet))
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        _inside = mUI.MelColumnLayout(_MainForm)
        if self.mPuppet:
            _strPuppet = self.mPuppet.cgmName
        else:
            _strPuppet = self.mPuppet
            
        SetHeader = cgmUI.add_Header('Puppet: {0}'.format(_strPuppet))
        self.uiStatus = mUI.MelLabel(_inside,
                                     vis=False,
                                     bgc = SHARED._d_gui_state_colors.get('warning'),
                                     label = '...',
                                     h=20)        
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)
        
        """
        mc.button(parent=_inside,
                  l = 'Progress bar',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(cgmUI.progressBar_test,self.uiPB_test,10000),
                  ann = 'Test progress bar')    """
    
        #add_Button(MainForm,'Reset', lambda *a: resetUI(self))
        #add_Button(MainForm,'Reload', lambda *a: reloadUI(self))
        #add_Button(MainForm,'module Reload', lambda *a: reloadUI(self))
    
        #SingleChecks======================================================================
        _l_order = ['Mirror Verify','Gather Space Drivers','connectRig','proxyMesh','isHistoricallyInteresting']
        _d = {'Gather Space Drivers':'gatherSpaceDrivers',
              'Mirror Verify':'mirrorVerify',
              'isHistoricallyInteresting':'ihi'}
        
        self._dCB_reg = {}
        for k in _l_order:
            _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
            mUI.MelSpacer(_row,w=10)    
            
            mUI.MelLabel(_row, label = '{0}:'.format(k))
            _row.setStretchWidget(mUI.MelSeparator(_row))

            _plug = 'cgmVar_mrsPostProcess_' + _d.get(k,k)
            try:self.__dict__[_plug]
            except:
                log.debug("{0}:{1}".format(_plug,1))
                self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = 1)
    
            l = k
            _buffer = _d.get(k)
            if _buffer:l = _buffer
            _cb = mUI.MelCheckBox(_row,
                                  #annotation = 'Create qss set: {0}'.format(k),
                                  value = self.__dict__[_plug].value,
                                  onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                                  offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
            self._dCB_reg[k] = _cb
            mUI.MelSpacer(_row,w=10)    
            
            _row.layout()
        
        #Danger!!!!!!======================================================================
        _l_order = ['Delete Blocks']
        _d = {'Delete Blocks':'deleteBlocks'}
    
        mc.setParent(_inside)
        cgmUI.add_Header('!!!!!DANGER!!!!!!')        
        _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    
        for k in _l_order:
            _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
            mUI.MelSpacer(_row,w=10)    
    
            mUI.MelLabel(_row, label = '{0}:'.format(k))
            _row.setStretchWidget(mUI.MelSeparator(_row))
    
            _plug = 'cgmVar_mrsPostProcess_' + _d.get(k,k)
            try:self.__dict__[_plug]
            except:
                log.debug("{0}:{1}".format(_plug,1))
                self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = 0)
    
            l = k
            _buffer = _d.get(k)
            if _buffer:l = _buffer
            _cb = mUI.MelCheckBox(_row,
                                  #annotation = 'Create qss set: {0}'.format(k),
                                  value = self.__dict__[_plug].value,
                                  en=False,
                                  onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                                  offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
            self._dCB_reg[k] = _cb
            mUI.MelSpacer(_row,w=10)    
    
            _row.layout()                
        
        
        #Qss======================================================================
        mc.setParent(_inside)
        cgmUI.add_Header('qss')        
        _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        
        _d = {'bake':False,
              'rotation':'rot',
              'rotateAxis':'ra',
              'rotateOrder':'ro',
              'scalePivot':'sp',
              'rotatePivot':'rp'}
        _d_defaults = {'position':1}
        _l_order = ['bake','delete','export']
        for k in _l_order:
            _plug = 'cgmVar_mrsPostProcess_QSS' + k
            try:self.__dict__[_plug]
            except:
                _default = _d_defaults.get(k,1)
                log.debug("{0}:{1}".format(_plug,_default))
                self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = _default)
    
            l = k
            _buffer = _d.get(k)
            if _buffer:l = _buffer
            _cb = mUI.MelCheckBox(_row,label=l,
                                  annotation = 'Create qss set: {0}'.format(k),
                                  value = self.__dict__[_plug].value,
                                  onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                                  offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
            self._dCB_reg[k+"QSS"] = _cb
        _row.layout()
        
        
        
        _button = mc.button(parent=_MainForm,
                            l = 'Process',
                            ut = 'cgmUITemplate',
                            #c = cgmGEN.Callback(cgmUI.progressBar_test,self.uiPB_test,10000),
                            c = cgmGEN.Callback(self.uiFunc_process),
                            ann = 'Test progress bar')        
        #_row_cgm = cgmUI.add_cgmFooter(_MainForm)
        mc.setParent(_MainForm)
 
        
        #_rowProgressBar = mUI.MelRow(_MainForm)

        _MainForm(edit = True,
                  af = [(_inside,"top",0),
                        (_inside,"left",0),
                        (_inside,"right",0),
                        (_button,"left",0),
                        (_button,"right",0),
                        #(self.uiPB_test,"left",0),
                        #(self.uiPB_test,"right",0),                        
                        #(_row_cgm,"left",0),
                        #(_row_cgm,"right",0),
                        (_button,"bottom",0),
    
                        ],
                  ac = [(_inside,"bottom",0,_button),
                        #(_button,"bottom",0,_row_cgm),
                        #(self.uiPB_test,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_button,"top")])
        
        

        
        
class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmBuilder_ui'    
    WINDOW_TITLE = 'mrsBuilder - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 600,400
    __modes = 'space','orient','follow'
    
    check_cgm()
    _d_ui_annotations = {'select':"Select rigBlocks in maya from ui.",
                         'step build':"DEV | Generate a step build ui for the block",
                         'rebuild':"Rebuild blocks from define state",
                         'save blockDat':'Save current blockDat to the block',
                         'load blockDat':'Load existing blockDat from the block to current settings',
                         'reset blockDat': 'Reset blockDat to defaults as defined by the module',
                         'copy blockDat': 'Copy the blockDat from one block to another',
                         'load state blockDat': 'Load the blockDat only for this state',
                         
                         'rig connect': 'Connect the bind joints to rig joints',
                         'rig disconnect': 'Disconnect the bind joints from the rig joints',
                         'proxy verify': 'Verify proxy geo per block (if available)',
                         'reset rig': 'Reset rig controls',
                         'query rig nodes':"Query and display the rig nodes of the block",
                         'verify':"Verify the attributes rigBlocks"}    
    
    def insert_init(self,*args,**kws):
            if kws:log.debug("kws: %s"%str(kws))
            if args:log.debug("args: %s"%str(args))
            log.debug(self.__call__(q=True, title=True))
            
    
            self.__version__ = __version__
            self.__toolName__ = 'Builder'		
            #self.l_allowedDockAreas = []
            self.WINDOW_TITLE = ui.WINDOW_TITLE
            self.DEFAULT_SIZE = ui.DEFAULT_SIZE

            self.uiPopUpMenu_parent = False
            self._l_toEnable = []
            #self.create_guiOptionVar('dynParentMode',  defaultValue = ui.__modes[0])       
            self.uiScrollList_parents = False
            self.uiPopUpMenu_blocks = None
            self.uiRC_profile = None
            self._blockRoot = None
            self._blockCurrent = None
            self._blockFactory = RIGBLOCKS.factory()
            
            self.create_guiOptionVar('blockAttrsFrameCollapse',defaultValue = 0)
            self.create_guiOptionVar('blockSharedFrameCollapse',defaultValue = 0)
            self.create_guiOptionVar('blockInfoFrameCollapse',defaultValue = 0) 
            self.create_guiOptionVar('blockMasterFrameCollapse',defaultValue = 0) 
            self.create_guiOptionVar('blockUtilsFrameCollapse',defaultValue = 0) 
            
            self.var_buildProfile = cgmMeta.cgmOptionVar('cgmVar_cgmMRSBuildProfile',
                                                        defaultValue = 'unityMed')            
            
            try:self.var_rigBlockCreateSizeMode
            except:self.var_rigBlockCreateSizeMode = cgmMeta.cgmOptionVar('cgmVar_rigBlockCreateSizeMode', defaultValue = 'selection')
            
            
    def build_menus(self):
        self.uiMenu_profile = mUI.MelMenu( l='Profile', pmc=self.buildMenu_profile)                
        #self.uiMenu_block = mUI.MelMenu( l='Contextual', pmc=self.buildMenu_block)
        self.uiMenu_block = mUI.MelMenu( l='Contextual', pmc=self.buildMenu_block,pmo=0)        
        self.uiMenu_post = mUI.MelMenu( l='Post', pmc=self.buildMenu_post,pmo=True)
        self.uiMenu_add = mUI.MelMenu( l='Add', pmc=self.buildMenu_add) 
        self.uiMenu_snap = mUI.MelMenu( l='Snap', pmc=self.buildMenu_snap,pmo=True)
        self.uiMenu_help = mUI.MelMenu( l='Help', pmc=self.buildMenu_help,pmo=True)
        
    def uiFunc_buildProfile_set(self,*args,**kws):
        _str_func = ''
        _updateUI = kws.pop('updateUI',True)
        _profile = kws.pop('buildProfile',None)
        

        if not _profile:
            return log.error("|{0}| >> blockProfile arg".format(_str_func))
        
        _current = self.var_buildProfile.value
        if _current != _profile:
            log.debug("|{0}| >> Setting to: {1}".format(_str_func,_profile))
            self.var_buildProfile.setValue(_profile)
            
        if self.uiScrollList_blocks.getSelectedIdxs() or self._blockCurrent:
            self.uiFunc_contextBlockCall('atUtils','buildProfile_load',_profile, **{'contextMode':'root'})
            
    def buildMenu_profile( self, *args, **kws):
        self.uiMenu_profile.clear()
        _menu = self.uiMenu_profile
        
        for i,item in enumerate(BLOCKSHARE._l_buildProfiles):
            mUI.MelMenuItem(_menu, l=item,
                            ann = "Load the following profile",
                            c = cgmGEN.Callback(self.uiFunc_buildProfile_set,**{'buildProfile':item}),
                            )        
        
        return


    

        
    def buildMenu_post( self, *args, **kws):
        self.uiMenu_post.clear()
        _menu = self.uiMenu_post
        
        #_mPuppet = mUI.MelMenuItem(self.uiMenu_post, l="Puppet",subMenu=True)
        mUI.MelMenuItem( _menu, l="Rig Prep",
                         #c = cgmGEN.Callback(ui)
                         c=cgmGEN.Callback(self.uiFunc_contextPuppetCall,'postUI'))
        mUI.MelMenuItemDiv(_menu)
        
        mUI.MelMenuItem( _menu, l="Gather Blocks",
                         c = self.uiCallback(self,BUILDERUTILS.gather_rigBlocks,self.uiPB_mrs))
                         #c=lambda *a: BUILDERUTILS.gather_rigBlocks(self.uiPB_mrs) )

        mUI.MelMenuItem(_menu, l="Up to date?",
                        ann = "Please don't mess with this if you don't know what you're doing ",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'is_upToDate'),
                        )        
        _subCalls = mUI.MelMenuItem( _menu, l="Calls",subMenu=True,tearOff=True)
        
        mUI.MelMenuItem(_subCalls, l="Mirror verify",
                        ann = "Please don't mess with this if you don't know what you're doing ",
                        c = cgmGEN.Callback(self.uiFunc_contextPuppetCall,'mirror_verify'),
                        )

        mUI.MelMenuItem(_subCalls, l="Gather space drivers",
                                ann = "Gather world and puppet space drivers ",
                                c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'collect_worldSpaceObjects'),
                                )
        """
        mUI.MelMenuItem(_menu, l="Armature Verify",
                        ann = "Verify puppet armature ",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'armature_verify'),
                        )
        mUI.MelMenuItem(_menu, l="Armature Remove",
                        ann = "Remove puppet armature ",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,'armature_remove'),
                        )"""
        mUI.MelMenuItem(_subCalls, l="Qss - Bake set",
                        ann = "Add bake set",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,
                                           'qss_verify',**{'puppetSet':False,
                                                           'bakeSet':True,
                                                           'deleteSet':False,
                                                           'exportSet':False}),)
        mUI.MelMenuItem(_subCalls, l="Qss - Delete set",
                        ann = "Add delete set",
                        c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,
                                           'qss_verify',**{'puppetSet':False,
                                                           'bakeSet':False,
                                                           'deleteSet':True,
                                                           'exportSet':False}),)
        mUI.MelMenuItem(_subCalls, l="Qss - Export set",
                                ann = "Add export set - visible geo and joints",
                                c= cgmGEN.Callback(self.uiFunc_contextPuppetCall,
                                                   'qss_verify',**{'puppetSet':0,
                                                                   'bakeSet':0,
                                                                   'deleteSet':0,
                                                                   'exportSet':1}),)
        
        _mHistorical = mUI.MelMenuItem(_subCalls, l="Is Historically Interesing",
                                         subMenu = True)
        mUI.MelMenuItem(_mHistorical, l="Off",
                        ann = "Turn off every node's isHistoricallyInteresting option",
                        c = cgmGEN.Callback(CONTEXT.set_attrs,None,'ihi',0,'scene',None,'reselect'))
        mUI.MelMenuItem(_mHistorical, l="On",
                        ann = "Turn on every node's isHistoricallyInteresting option",
                        c = cgmGEN.Callback(CONTEXT.set_attrs,None,'ihi',1,'scene',None,'reselect'))
        
        #>>Mesh ---------------------------------------------------------------------
        mUI.MelMenuItemDiv(_menu)        
        _mMesh = mUI.MelMenuItem(_menu, l="Puppet Mesh",tearOff=True,
                                 subMenu = True)
        
        mUI.MelMenuItem(_mMesh, l="Unified",
                        ann = "Create a unified unskinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':True,'skin':False}))
        mUI.MelMenuItem(_mMesh, l="Unified [Skinned]",
                        ann = "Create parts skinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':True,'skin':True}))        
        mUI.MelMenuItem(_mMesh, l="Parts Mesh",
                        ann = "Create parts unskinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':False,'skin':False}))
        mUI.MelMenuItem(_mMesh, l="Parts Mesh [Skinned]",
                        ann = "Create parts skinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':False,'skin':True}))
        mUI.MelMenuItem(_mMesh, l="Proxy Mesh [Parented]",
                        ann = "Create proxy puppet mesh parented to skin joints from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'proxy':True,'unified':False,'skin':False}))        
        mUI.MelMenuItem(_mMesh, l="Delete",
                        ann = "Remove skinned or wired puppet mesh",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_delete'))
            
    def buildMenu_block(self,*args,**kws):
        self.uiMenu_block.clear()   
        _menu = self.uiMenu_block
        d_s = {'Set Side':{},
               'Utilities':{'Verify':{'ann':'Check if the block is current (DEV)',
                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                     'verify',
                                                     **{'updateUI':0})},                   
                   'Block Current?':{'ann':'Check if the block is current (DEV)',
                                'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                       'atUtils','is_current',
                                                       **{'updateUI':0})},
                  'Block Update':{'ann':'[DEV] Update a block. In testing',
                                    'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                           'atUtils','update',
                                                           **{'updateUI':1,'reverseContext':False})},
                  'Reorder UD':{'ann':'Reorder user defined attrs',
                                'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                       'atUtils','reorder_udAttrs',
                                                       **{'updateUI':0})}},
               'blockFrame':{'Align To':{'ann':self._d_ui_annotations.get('blockframealignto'),
                                         'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils','blockFrame_alignTo',False,
                                                **{'updateUI':0})},
                        'Shape To':{'ann':self._d_ui_annotations.get('blockframeshapeto'),
                                    'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                           'atUtils','blockFrame_alignTo',True,
                                           **{'updateUI':0})}},               
               'Focus':{'Clear':{'ann':self._d_ui_annotations.get('focus clear'),
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                        'focus',False,None,
                                        **{'updateUI':0})},
                        'Vis':{'ann':self._d_ui_annotations.get('focus vis'),
                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'focus',True,'vis',
                                      **{'updateUI':0})},
                        'Template':{'ann':self._d_ui_annotations.get('focus template'),
                                    'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                           'focus',True,'template',
                                           **{'updateUI':0})},},

               'Rig':{'Step Build':{'ann':self._d_ui_annotations.get('step build'),
                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                      'stepUI',
                                                      **{'updateUI':0,'mode':'stepBuild'})},
                      'Prechecks':{'ann':'Precheck blocks for problems',
                                   'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                          'asRigFactory',
                                                          **{'updateUI':0,'mode':'prechecks'})},                      
                      'Verify Proxy':{'ann':self._d_ui_annotations.get('verify proxy mesh'),
                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'verify_proxyMesh',
                                      **{'updateUI':0})},
                      'Rig Connect':{'ann':self._d_ui_annotations.get('connect rig'),
                                        'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,'rig_connect',**{'updateUI':0})},
                      'Rig Disconnect':{'ann':self._d_ui_annotations.get('disconnect rig'),
                                     'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,'rig_disconnect',**{'updateUI':0})},                      
                      'Reset Controls':{'ann':self._d_ui_annotations.get('reset rig controls'),
                               'call':cgmGEN.Callback(self.uiFunc_contextModuleCall,
                                      'rig_reset',
                                      **{'updateUI':0})},
                      'Query Nodes':{'ann':self._d_ui_annotations.get('query rig nodes'),
                               'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','rigNodes_get',
                                      **{'updateUI':0,'report':True})},},
               'Parent':{'To Active':{'ann':'Set parent block to active block',
                                  'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                         'atUtils','blockParent_set',
                                                         **{'mode':'setParentToActive'})},
                         'Clear':{'ann':'Clear blockParent',
                                           'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                  'atUtils','blockParent_set',
                                                                  **{'parent':False})},},
               'Define':{'Load base size dat':{'ann':'Reset define dat to base',
                                            'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                   'atUtils', 'define_set_baseSize',
                                                                   **{'updateUI':0})}},
               'Template':{'Snap to RP':{'ann':'Snap handles to rp plane',
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                 'atUtils', 'handles_snapToRotatePlane','template',True,
                                 **{'updateUI':0})},},               
               'Prerig':{
                   'RP Pos':{'ann':'Create locator at the where the system thinks your rp handle will be',
                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                'atUtils', 'prerig_get_rpBasePos',
                                **{'markPos':1,'updateUI':0})},
                   'Snap RP to Orient':{'ann':'Snap rp hanlde to orient vector',
                            'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                   'atUtils', 'prerig_snapRPtoOrientHelper',
                                   **{'updateUI':0})},
                   'Query Indices':{'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                           'atBlockModule', 'get_handleIndices',
                                                           **{'updateUI':0})},
                   'Snap to RP':{'ann':'Snap handles to rp plane',
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                 'atUtils', 'handles_snapToRotatePlane','prerig',True,
                                 **{'updateUI':0})},
                   'Handles | Lock':{'ann':'Lock the prerig handles',
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                 'atUtils', 'prerig_handlesLock',True,
                                 **{'updateUI':0})},
                   'Handles | Unlock':{'ann':'Unlock the prerig handles',
                                   'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                   'atUtils', 'prerig_handlesLock',False,
                                   **{'updateUI':0})},
                   'divTags':['Handles | Lock','Query Indices'],                   
                   'Arrange | Linear Spaced':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                             'atUtils', 'prerig_handlesLayout','spaced','linear',
                                             **{'updateUI':0})},
                   'Arrange | Linear Even':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                             'atUtils', 'prerig_handlesLayout','even','linear',
                                             **{'updateUI':0})},
                   'Arrange | Cubic Even':{'ann':'Unlock the prerig handles',
                                            'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                            'atUtils', 'prerig_handlesLayout','even','cubicRebuild',
                                            **{'updateUI':0})},
                   'Arrange | Cubic Spaced':{'ann':'Unlock the prerig handles',
                                             'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                             'atUtils', 'prerig_handlesLayout','spaced','cubicRebuild',
                                             **{'updateUI':0})},                                      
                   
                   
                   },
               'Queries':{
                   'Visualize':{'ann':'Visualize the block tree in the script editor',
                                'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                       'VISUALIZEHEIRARCHY',
                                                       **{'updateUI':0})},
                  'Buildable?':{'ann':'Check if the block is buildable (DEV)',
                                'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                       'getModuleStatus',
                                                       **{'updateUI':0})}},

               'Geo':{
                   'order':['Block Mesh','Block Loft','Puppet Mesh',
                            'Unified','Unified [Skinned]',
                            'Parts Mesh','Parts Mesh [Skinned]',
                            'Proxy Mesh [Parented]','Delete',
                            ],
                   'divTags':['Delete'],
                   'headerTags':['Puppet Mesh'],
                   'Block Mesh':{'ann':'Generate Simple mesh',
                               'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                                'atUtils','create_simpleMesh',
                                                **{'connect':False,'updateUI':0})},
                   'Block Loft':{'ann':'Generate Simple mesh with history to weak the loft manually',
                               'call':cgmGEN.CB(self.uiFunc_contextBlockCall,
                                                'atUtils','create_simpleMesh',
                                                **{'connect':False,'updateUI':0,'deleteHistory':0})},
                   'Unified':{'ann':"Create a unified unskinned puppet mesh from the active block's basis.",
                              'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                               **{'unified':True,'skin':False})},
                   'Unified [Skinned]':{
                       'ann':"Create parts skinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                         **{'unified':True,'skin':True})},
                   'Parts Mesh':{
                       'ann':"Create parts unskinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                         **{'unified':False,'skin':False})},
                   'Parts Mesh [Skinned]':{
                       'ann':"Create parts skinned puppet mesh from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                         **{'unified':False,'skin':True})},
                   'Proxy Mesh [Parented]':{
                       'ann':"Create proxy puppet mesh parented to skin joints from the active block's basis.",
                       'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                         **{'proxy':True,'unified':False,'skin':False})},
                   'Delete':{
                       'ann':"Remove skinned or wired puppet mesh",
                       'call':cgmGEN.CB(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_delete')},
                   },
               'Mirror':{ 
                   'divTags':['Settings | Pull'],
                   'Controls | Push':{'ann':'Mirror block controls in context | push',
                                      'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                'atUtils','blockMirror_go',
                                                                **{'updateUI':True,'mode':'push'})},
                  'Controls | Pull':{'ann':'Mirror block controls in context | pull',
                                      'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                'atUtils','blockMirror_go',
                                                                **{'updateUI':True,'mode':'pull'})},
                  'Settings | Push':{'ann':'Mirror block controls in context | push',
                                     'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                               'atUtils','blockMirror_settings',
                                                               **{'updateUI':True,'mode':'push'})},
                 'Settings | Pull':{'ann':'Mirror block controls in context | pull',
                                     'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                               'atUtils','blockMirror_settings',
                                                               **{'updateUI':True,'mode':'pull'})},                  
                 },
               'blockDat':{'order':[]},
               'Names':{ 
                   'divTags':['nameList | iter baseName'],
                   'Name | Set tag':{'ann':'Set the name tag of the block and rename dags',
                                     'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                            'atUtils','set_nameTag', **{})},
                   'Position | Set tag':{'ann':'Set the position tag of the block and rename dags',
                                         'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                                'atUtils','set_position',
                                                                **{'ui':True})},
                  'nameList | reset':{'ann':'Reset the name list to the profile',
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                        'atUtils','nameList_resetToProfile',
                                                        **{})},
                   'nameList | iter baseName':{'ann':'Set nameList values from name attribute',
                                 'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                        'atUtils','set_nameListFromName',
                                                        **{})}}                      }
        """
        mUI.MelMenuItem(_mMesh, l="Unified",
                        ann = "Create a unified unskinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':True,'skin':False}))
        mUI.MelMenuItem(_mMesh, l="Unified [Skinned]",
                        ann = "Create parts skinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':True,'skin':True}))        
        mUI.MelMenuItem(_mMesh, l="Parts Mesh",
                        ann = "Create parts unskinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':False,'skin':False}))
        mUI.MelMenuItem(_mMesh, l="Parts Mesh [Skinned]",
                        ann = "Create parts skinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'unified':False,'skin':True}))
        mUI.MelMenuItem(_mMesh, l="Proxy Mesh [Parented]",
                        ann = "Create proxy puppet mesh parented to skin joints from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_create',
                                            **{'proxy':True,'unified':False,'skin':False}))        
        mUI.MelMenuItem(_mMesh, l="Delete",
                        ann = "Remove skinned or wired puppet mesh",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils','puppetMesh_delete'))        
        
        """
        for state in ['define','template','prerig']:
            d_s['blockDat']['order'].append('Load {0}'.format(state))
            d_s['blockDat']['Load {0}'.format(state)] = {
                'ann':"Load {0} blockDat in context".format(state),
                'call':cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                       'atUtils','blockDat_load_state',state,
                                       **{})}
        
        
        l_keys = d_s.keys()
        l_keys.sort()
        l_check = ['Define','Template','Prerig','Skeleton','Rig']
        l_check.reverse()
        for k in l_check:
            if k in l_keys:
                l_keys.remove(k)
                l_keys.insert(0,k)
                
        for s in l_keys:
            d = d_s[s]
            divTags = d.get('divTags',[])
            headerTags = d.get('headerTags',[])
            
                
            _sub = mUI.MelMenuItem(_menu, subMenu = True,tearOff=True,
                            label = s,
                            en=True,)
            
            if s == 'Set Side':
                for i,side in enumerate(['none','left','right','center']):
                    mUI.MelMenuItem(_sub,
                                    l = side,
                                    ann='Set contextual block side to: {0}'.format(side),
                                    c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                        'atUtils','set_side',side,
                                                        **{}))                
                
                continue
            
            l_keys2 = d.get('order',False)
            if l_keys2:
                for k in d.keys():
                    if k not in l_keys2:
                        l_keys2.append(k)
            else:
                l_keys2 = d.keys()
                l_keys2.sort()
            for l in l_keys2:
                if l in ['divTags','headerTags','order']:
                    continue
                if l in divTags:
                    mUI.MelMenuItemDiv(_sub)                
                if l in headerTags:
                    mUI.MelMenuItemDiv(_sub)
                    mUI.MelMenuItem(_sub,
                                    label = "--- {0} ---".format(l.upper()),
                                    en=False)
                    mUI.MelMenuItemDiv(_sub)
                    continue
                d2 = d[l]
                mUI.MelMenuItem(_sub,
                                label = l,
                                ann = d2.get('ann',''),
                                c=d2.get('call'))
                
            if s == 'Rig':
                mUI.MelMenuItemDiv(_menu)            

        #Vis menu -----------------------------------------------------------------------------
        _vis = mUI.MelMenuItem(_menu, subMenu = True,tearOff=True,
                               label = 'Vis',
                               en=True,)        
        for a in ['Measure','RotatePlane']:
            _sub = mUI.MelMenuItem(_vis, subMenu = True,tearOff=False,
                                   label = a,
                                   en=True,)
            for i,v in enumerate(['off','on']):
                mUI.MelMenuItem(_sub,
                                l = v,
                                ann='Set visibility of: {0} | {1}'.format(a,v),
                                c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                            'atUtils', 'blockAttr_set',
                                            **{"vis{0}".format(a):i}))                              
            

        log.info("Context menu rebuilt")        
        
    def buildMenu_blockOLD( self, *args, **kws):
        self.uiMenu_block.clear()
        _menu = self.uiMenu_block
        
        _str_context = "Context: {0} {1}".format(self._l_contextStartModes[self.var_contextStartMode.value],
                                        self._l_contextModes[self.var_contextMode.value])
        #c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'select',None,**{}))
        
        
        _d_ui_annotations = {'select':"Select rigBlocks in maya from ui. Context: {0}".format(_str_context),
                             'rebuild':"Rebuild blocks from define state. Context: {0}".format(_str_context),
                             'select':"Select the contextual blocks. Context: {0}".format(_str_context),
                             'Buildable Status': "Get the block modules buildable status. Context: {0}".format(_str_context),
                             'Verify Proxy Geo':"Verify the proxy geo of blocks and update direct controls if enabled on block. Context: {0}".format(_str_context),
                             'Get blockDat':"Get block dat. Context: {0}".format(_str_context),
                             'select':"Select the contextual blocks. Context: {0}".format(_str_context),
                             'select':"Select the contextual blocks. Context: {0}".format(_str_context),
                             'select':"Select the contextual blocks. Context: {0}".format(_str_context),
                             'verify':"Verify the attributes rigBlocks. Context: {0}".format(_str_context)}        
        
        mUI.MelMenuItem(self.uiMenu_block, l="Clear active",
                        en = bool(self._blockCurrent),
                        ann = _d_ui_annotations.get('Clear Active',"NEED select"),
                        c = cgmGEN.Callback(self.uiFunc_block_clearActive))
        
        
        
        mUI.MelMenuItem(self.uiMenu_block, l="Context: {0} ---".format(_str_context),
                        en=False)  
        
        
        mUI.MelMenuItem(self.uiMenu_block, l="Select",
                        ann = _d_ui_annotations.get('select',"NEED select"),
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'select',**{'updateUI':0}))
        mUI.MelMenuItem(self.uiMenu_block, l="Rebuild",
                        ann = _d_ui_annotations.get('rebuild',"NEED rebuild"),
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'rebuild'))        
        mUI.MelMenuItem(self.uiMenu_block, l="Verify",
                        ann = _d_ui_annotations.get('verify',"NEED verify"),
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'verify'))
        mUI.MelMenuItem(self.uiMenu_block, l="Buildable?",
                        ann = _d_ui_annotations.get('Buildable Status',"Nope"),
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'getModuleStatus',**{'updateUI':0}))
        mUI.MelMenuItem(self.uiMenu_block, l="Visualize Heirarchy",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'VISUALIZEHEIRARCHY',**{'updateUI':0}))
        
       
        
        
        _mBlockDat = mUI.MelMenuItem(self.uiMenu_block, l="BlockDat",subMenu=True)
        

        mUI.MelMenuItem(self.uiMenu_block, l="Report",
                        en=False)       
        
        _mRig = mUI.MelMenuItem(self.uiMenu_block, l="Rig",
                                subMenu = True)
        
        _mMesh = mUI.MelMenuItem(self.uiMenu_block, l="Puppet Mesh",
                                 subMenu = True)
        
        
        #>>Mirror -----------------------------------------------------------------------------------------------
        mUI.MelMenuItemDiv(_menu)
        
        _mirror = mUI.MelMenuItem(_menu, subMenu = True,
                                  label = "Mirror",
                                  en=True,)   
    
        mUI.MelMenuItem(_mirror,
                        label = 'Verify',
                        ann = 'Create or verify mirror block',
                        #c=lambda *a:self.uiCallback_withUpdate( _mBlock.atBlockUtils, mirrorDat[1], **mirrorDat[2]) )
                        #c = lambda *a: self.uiFunc_block_mirror_create(_mBlock,False) )
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils', 'blockMirror_create',**{'updateUI':1}))
        
        mUI.MelMenuItem(_mirror,
                        label = 'Rebuild',
                        ann = 'Rebuild mirror block from scratch',
                        #c=lambda *a:self.uiCallback_withUpdate( _mBlock.atBlockUtils, mirrorDat[1], **mirrorDat[2]) )
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils', 'blockMirror_create',**{'updateUI':1,'forceNew':True}))
        
        _l_mirror = [#['Create','blockMirror_create', {}],
                     #['Recreate','blockMirror_create', {'forceNew':True}],
                     ['Push','blockMirror_go', {'mode':'push','updateUI':1}],
                     ['Pull','blockMirror_go', {'mode':'pull','updateUI':1}]]
        for mirrorDat in _l_mirror:
            mUI.MelMenuItem(_mirror,
                            label = mirrorDat[0],
                            ann = '{0} block controls'.format(mirrorDat[0]),
                            #c=lambda *a:self.uiCallback_withUpdate( _mBlock.atBlockUtils, mirrorDat[1], **mirrorDat[2]) )
                            #c=cgmGEN.Callback( _mBlock.atBlockUtils, mirrorDat[1], **mirrorDat[2]) )
                            c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'atUtils', mirrorDat[1], **mirrorDat[2]))
        

        
        """
        _mSkeleton = mUI.MelMenuItem(self.uiMenu_block, l="Skeleton",
                                     subMenu = True)"""

        #>>Rig -----------------------------------------------------------------------------
        mUI.MelMenuItem(_mRig,
                        label = 'Verify Proxy',
                        ann = self._d_ui_annotations.get('verify proxy mesh',"FIX") + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'verify_proxyMesh',**{'updateUI':0}))  
                        
                        #c=cgmGEN.Callback( _mBlock.verify_proxyMesh,True ))
        mUI.MelMenuItem(_mRig,
                        label = 'Reset Rig controls',
                        ann = self._d_ui_annotations.get('reset rig controls',"FIX") + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextModuleCall,'rig_reset',**{'updateUI':0}))
                        #c=cgmGEN.Callback( _mBlock.atRigModule, 'rig_reset' ))
        mUI.MelMenuItem(_mRig,
                        label = 'Connect Rig',
                        ann = self._d_ui_annotations.get('connect rig',"FIX") + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextModuleCall,'rig_connect',**{'updateUI':0}))
                        #c=cgmGEN.Callback( _mBlock.atRigModule, 'rig_connect' ))
        mUI.MelMenuItem(_mRig,
                        label = 'Disconnect Rig',
                        ann = self._d_ui_annotations.get('disconnect rig',"FIX") + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextModuleCall,'rig_disconnect',**{'updateUI':0}))
                        #c=cgmGEN.Callback( _mBlock.atRigModule, 'rig_disconnect' ))        
        
        
        #>>BlockData ---------------------------------------------------------------------
        mUI.MelMenuItem(_mBlockDat, l="Save",
                        ann = self._d_ui_annotations.get('save blockDat') + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'saveBlockDat',**{'updateUI':0}))        
        mUI.MelMenuItem(_mBlockDat, l="Load",
                        ann = self._d_ui_annotations.get('load blockDat') + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'loadBlockDat'))        
        mUI.MelMenuItem(_mBlockDat, l="Copy - TO DO",
                        en=False,
                        ann = self._d_ui_annotations.get('copy blockDat') + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'loadBlockDat'))  
        mUI.MelMenuItem(_mBlockDat, l="Query",
                        ann = self._d_ui_annotations.get('Get blockDat','nope') + _str_context,
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'getBlockDat',**{'updateUI':0}))  
        mUI.MelMenuItem(_mBlockDat, l="Reset",
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'resetBlockDat'), 
                        ann = self._d_ui_annotations.get('reset blockDat') + _str_context)
        
        
        #>>Mesh ---------------------------------------------------------------------
        mUI.MelMenuItem(_mMesh, l="Unified",
                        ann = "Create a unified unskinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_activeBlockCall,'puppetMesh_create',
                                            **{'unified':True,'skin':False}))
        mUI.MelMenuItem(_mMesh, l="Unified [Skinned]",
                        ann = "Create parts skinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_activeBlockCall,'puppetMesh_create',
                                            **{'unified':True,'skin':True}))        
        mUI.MelMenuItem(_mMesh, l="Parts Mesh",
                        ann = "Create parts unskinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_activeBlockCall,'puppetMesh_create',
                                            **{'unified':False,'skin':False}))
        mUI.MelMenuItem(_mMesh, l="Parts Mesh [Skinned]",
                        ann = "Create parts skinned puppet mesh from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_activeBlockCall,'puppetMesh_create',
                                            **{'unified':False,'skin':True}))
        mUI.MelMenuItem(_mMesh, l="Proxy Mesh [Parented]",
                        ann = "Create proxy puppet mesh parented to skin joints from the active block's basis.",
                        c = cgmGEN.Callback(self.uiFunc_activeBlockCall,'puppetMesh_create',
                                            **{'proxy':True,'unified':False,'skin':False}))        
        mUI.MelMenuItem(_mMesh, l="Delete",
                        ann = "Remove skinned or wired puppet mesh",
                        c = cgmGEN.Callback(self.uiFunc_activeBlockCall,'puppetMesh_delete'))
        
        """
        mUI.MelMenuItem(_mMesh, l="Block Mesh",
                        ann = _d_ui_annotations.get('Block Mesh','Block Mesh'),
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'create_simpleMesh',**{'skin':False,'updateUI':0}))
        mUI.MelMenuItem(_mMesh, l="Block Mesh - skinned",
                        ann = _d_ui_annotations.get('Block Mesh Skinned','Block Mesh Skinned'),
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'create_simpleMesh',**{'skin':True,'updateUI':0}))"""
        
        """
        #>>Skeleton -----------------------------------------------------------------------
        mUI.MelMenuItem(_mSkeleton, l="Generate",
                        ann = _d_ui_annotations.get('Skeletonize',"NEED Skeletonize"),
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'skeletonize'))        
        mUI.MelMenuItem(_mSkeleton, l="Delete",
                        ann = _d_ui_annotations.get('DeleteSkeleton',"NEED load DeleteSkeleton"),
                        c = cgmGEN.Callback(self.uiFunc_contextBlockCall,'loadBlockDat'))"""
  
    
    def buildMenu_snap( self, force=False, *args, **kws):
        if self.uiMenu_snap and force is not True:
            return
        self.uiMenu_snap.clear()
        
        UICHUNKS.uiSection_snap(self.uiMenu_snap)
            
        mUI.MelMenuItemDiv(self.uiMenu_snap)
        
        mUI.MelMenuItem(self.uiMenu_snap, l='Rebuild',
                        c=cgmGEN.Callback(self.buildMenu_snap,True))
        log.info("Snap menu rebuilt")
        
    #def buildMenu_help(self):
        #self.uiMenu_Help.clear()
        
        #cgmUI.uiSection_help(self.uiMenu_Help)
    class uiCallback(object):
        '''
        By Hamish McKenzie
        stupid little callable object for when you need to "bake" temporary args into a
        callback - useful mainly when creating callbacks for dynamicly generated UI items
        '''
        def __init__( self, ui, func, *a, **kw ):
            self._ui = ui
            self._func = func
            self._args = a
            self._kwargs = kw
        def __call__( self, *args ):
            self._ui.uiRow_progress(edit=1,vis=1)
            cgmUI.progressBar_start(self._ui.uiPB_mrs)
            self._ui.uiProgressText(edit=True,vis=1,
                                    label="{0} ".format(self._func.__name__))

            try:return self._func( *self._args, **self._kwargs )
            except Exception,err:
                try:log.info("Func: {0}".format(self._func.__name__))
                except:log.info("Func: {0}".format(self._func))
                if self._args:
                    log.info("args: {0}".format(self._args))
                if self._kwargs:
                    log.info("kws: {0}".format(self._kwargs))
                for a in err.args:
                    log.info(a)
                    
                cgmGEN.cgmExceptCB(Exception,err)
                raise Exception,err
            finally:
                self._ui.uiRow_progress(edit=1,vis=0)
                self._ui.uiProgressText(edit=True,label='...')
                cgmUI.progressBar_end(self._ui.uiPB_mrs)
                
    def buildMenu_add( self, force=False, *args, **kws):
        if self.uiMenu_add and force is not True:
            log.debug("No load...")
            return
        
        self.uiMenu_add.clear()   
        
        _d = RIGBLOCKS.get_modules_dat(True)#...refresh data
            
        for b in _d[1]['blocks']:
            if _d[0][b].__dict__.get('__menuVisible__'):
                mUI.MelMenuItem(self.uiMenu_add, l=b,
                                c=cgmGEN.Callback(self.uiFunc_block_create,b),
                                ann="{0} : {1}".format(b, self.uiFunc_block_create))
                
                l_options = RIGBLOCKS.get_blockProfile_options(b)                
                if l_options:
                    for o in l_options:
                        mUI.MelMenuItem(self.uiMenu_add, l=o,
                                        c=cgmGEN.Callback(self.uiFunc_block_create,b,o),
                                        ann="{0} : {1}".format(b, self.uiFunc_block_create))

        
        for c in _d[1].keys():
            #d_sections[c] = []
            if c == 'blocks':continue
            for b in _d[1][c]:
                if _d[0][b].__dict__.get('__menuVisible__'):
                    #d_sections[c].append( [b,cgmGEN.Callback(self.uiFunc_block_create,b)] )
                    l_options = RIGBLOCKS.get_blockProfile_options(b)
                    if l_options:
                        _sub = mUI.MelMenuItem( self.uiMenu_add, subMenu=True,l=b,tearOff=True)
                        l_options.sort()
                        for o in l_options:
                            _l = "{0}".format(o)
                            _c = cgmGEN.Callback(self.uiFunc_block_create,b,o)
                            mUI.MelMenuItem(_sub, l=_l,
                                            c=_c,
                                            ann="{0} : {1}".format(_l, _c)
                                            )
                    else:
                        mUI.MelMenuItem(self.uiMenu_add, l=b,
                                        c=cgmGEN.Callback(self.uiFunc_block_create,b,'default'),
                                        ann="{0} : {1}".format(b, self.uiFunc_block_create))
                        """
                        d_sections[c].append( ["{0} ({1})".format(o,b),
                                               cgmGEN.Callback(self.uiFunc_block_create,b,o)] )       """ 
        
        """
        d_sections = {}
        for c in _d[1].keys():
            d_sections[c] = []
            if c == 'blocks':continue
            for b in _d[1][c]:
                if _d[0][b].__dict__.get('__menuVisible__'):
                    d_sections[c].append( [b,cgmGEN.Callback(self.uiFunc_block_create,b)] )
                    l_options = RIGBLOCKS.get_blockProfile_options(b)                
                    if l_options:
                        for o in l_options:
                            d_sections[c].append( ["{0} ({1})".format(o,b),cgmGEN.Callback(self.uiFunc_block_create,b,o)] )

        for s in d_sections.keys():
            if d_sections[s]:
                _sub = mUI.MelMenuItem( self.uiMenu_add, subMenu=True,
                                        l=s)                
                for option in d_sections[s]:
                    mUI.MelMenuItem(_sub, l=option[0],
                                    c=option[1],
                                    ann="{0} : {1}".format(option[0], option[1])
                                    )"""

        mUI.MelMenuItemDiv(self.uiMenu_add)
        uiOptionMenu_blockSizeMode(self, self.uiMenu_add)        
        mUI.MelMenuItem(self.uiMenu_add, l='Rebuild',
                        c=cgmGEN.Callback(self.buildMenu_add,True))
        log.info("Add menu rebuilt")

    def uiUpdate_building(self):
        _str_func = 'uiUpdate_building'   
        
        self.uiUpdate_scrollList_blocks()
        
        
            
    def uiFunc_block_create(self, blockType = None, blockProfile = None):
        _str_func = 'uiFunc_block_create'
        
        #index = _indices[0]
        #_mBlock = self._ml_blocks[_index]
        _sel = mc.ls(sl=1) or []
        
        mActiveBlock = None
        side = None
        if blockType in ['limb']:
            side = 'right'
            
        if self._blockCurrent:
            mActiveBlock = self._blockCurrent.mNode
            #side = self._blockCurrent.UTILS.get_side(self._blockCurrent)
        _sizeMode = self.var_rigBlockCreateSizeMode.value
        if _sizeMode == 'selection' and not mc.ls(sl=True):
            #if blockType not in ['master']:
                #log.info("|{0}| >> Must have selection for size mode: {1}.".format(_str_func,_sizeMode))        
                #return False
            _sizeMode = None
        
        _mBlock = cgmMeta.createMetaNode('cgmRigBlock',blockType = blockType, 
                                         size = _sizeMode,
                                         blockParent = mActiveBlock,
                                         side = side,
                                         buildProfile = self.var_buildProfile.value,
                                         blockProfile = blockProfile)
        
        log.info("|{0}| >> [{1}] | Created: {2}.".format(_str_func,blockType,_mBlock.mNode))        
        
        self.uiUpdate_building()
        #self.uiFunc_block_setActive(self._ml_blocks.index(_mBlock))
        
        if _sel:
            mc.select(_sel)
        else:
            _mBlock.select()
        
    def uiFunc_block_mirror_create(self, mBlock = None, forceNew = False):
        _str_func = 'uiFunc_block_mirror_create'
        
        #index = _indices[0]
        #_mBlock = self._ml_blocks[_index]
        mActiveBlock = None
        if self._blockCurrent:
            mActiveBlock = self._blockCurrent.mNode
            

        mMirror = mBlock.atBlockUtils('blockMirror_create',forceNew)
        
        if not mMirror:
            return False
        log.info("|{0}| >> mMirror: {1}.".format(_str_func,mMirror.mNode))        
        
        self.uiUpdate_building()
        _idx = self._ml_blocks.index(mMirror)
        self.uiFunc_block_setActive(_idx)
        self.uiScrollList_blocks.selectByIdx(_idx)
        
    def uiFunc_activeBlockCall(self,func,*args,**kws):          
        _str_func = 'uiFunc_activeBlockCall'
                                         
        if not self._ml_blocks:
            return log.error("|{0}| >> No blocks detected".format(_str_func))

        _mActiveBlock = self._blockCurrent
        _str_activeBlock = False
        if _mActiveBlock:
            _str_activeBlock = _mActiveBlock.mNode
        else:
            return log.error("|{0}| >> No active block detected".format(_str_func))
        return getattr(_mActiveBlock,func)(*args,**kws)
    
    def get_activeBlock(self):
        _str_func = 'get_activeBlock'        
        _indices = self.uiScrollList_blocks.getSelectedIdxs()        
        if not _indices:
            log.error("|{0}| >> Nothing selected".format(_str_func))                                                        
            return False
        
        if not self._ml_blocks:
            log.error("|{0}| >> No blocks detected".format(_str_func))
            return False            
        
        _index = int(str(_indices[0]).split('L')[0])
        return self._ml_blocks[_index]
        
        
    def uiFunc_blockManange_fromScrollList(self,**kws):          
        _str_func = 'uiFunc_blockManange_fromScrollList'
        _indices = self.uiScrollList_blocks.getSelectedIdxs()
        
        _mode = kws.get('mode',None)
        _fromPrompt = None
        
        if not _indices:
            log.error("|{0}| >> Nothing selected".format(_str_func))                                                        
            return False
        
        if not self._ml_blocks:
            log.error("|{0}| >> No blocks detected".format(_str_func))                                                        
            return False            
        
        _index = int(str(_indices[0]).split('L')[0])
        _mBlock = self._ml_blocks[_index]
        
        _mActiveBlock = self._blockCurrent
        _str_activeBlock = False
        if _mActiveBlock:
            _str_activeBlock = _mActiveBlock.mNode    
    
        _done = False    
        if _mode is not None:
            log.debug("|{0}| >> mode: {1}".format(_str_func,_mode)) 
            if _mode == 'setParentToActive':
                if not _mActiveBlock:
                    log.error("|{0}| >> mode: {1} requires active block".format(_str_func,_mode)) 
                    return
                _mBlock.p_blockParent = _mActiveBlock
            elif  _mode == 'clearParentBlock':
                _mBlock.p_blockParent = False
            elif _mode == 'toScriptEditor':
                _mBlock.atUtils('to_scriptEditor')
            else:
                raise ValueError,"Mode not setup: {0}".format(_mode)

                
        self.uiUpdate_scrollList_blocks(_mBlock)


    #@cgmGEN.Timer
    def uiFunc_contextBlockCall(self,*args,**kws):
        try:
            def confirm(title,message,funcString):
                result = mc.confirmDialog(title=title,
                                          message= message,
                                          button=['OK', 'Cancel'],
                                          defaultButton='OK',
                                          cancelButton='Cancel',
                                          dismissString='Cancel')
        
                if result != 'OK':
                    log.error("|{0}| >> Cancelled | {1}.".format(_str_func,funcString))
                    return False
                return True
            
            
            _str_func = ''
            log.info(cgmGEN._str_hardBreak)
            _updateUI = kws.pop('updateUI',True)
            _reverseContext = kws.pop('reverseContext',False)
            _startMode = self.var_contextStartMode.value   
            _contextMode = kws.pop('contextMode', self._l_contextModes[self.var_contextMode.value])
            _b_confirm = False            
            #_contextMode = self._l_contextModes[self.var_contextMode.value]
            log.debug("|{0}| >> Update ui: {1}".format(_str_func,_updateUI))
            _mode = kws.get('mode')
            ml_blocks = []
            _mActiveBlock = self._blockCurrent
            
            
            if _mode == 'setParentToActive':
                if not _mActiveBlock:
                    log.error("|{0}| >> mode: {1} requires active block".format(_str_func,_mode)) 
                    return
                kws['parent'] = _mActiveBlock
                kws.pop('mode')
            elif _mode == 'blockDatCopyActive':
                if not _mActiveBlock:
                    log.error("|{0}| >> mode: {1} requires active block".format(_str_func,_mode)) 
                    return
                kws['sourceBlock'] = _mActiveBlock
                kws.pop('mode')
                
                
            #elif  _mode == 'clearParentBlock':
            #else:
                #raise ValueError,"Mode not setup: {0}".format(_mode)            
            
            b_changeState = False
            b_rootMode = False
            if args[0] == 'changeState':
                b_changeState = True
                if _contextMode in ['scene']:
                    log.warning("|{0}| >> Change state cannot be run in any mode but self. Changing context.".format(_str_func))                    
                elif _contextMode == 'root':
                    b_rootMode = True
                
                if _contextMode == 'self':
                    kws['forceNew'] = True
                    kws['checkDependency'] = True
                else:
                    kws['forceNew'] = self.var_contextForceMode.value
            elif args[0] == 'stepUI':
                _contextMode = 'self'
            
            try:
                if args[1] in ['puppetMesh_create','puppetMesh_delete']:
                    _contextMode = 'self'
                    log.error("|{0}| >> Puppet Mesh".format(_str_func,_mode))
            except:pass
            
            if _contextMode != 'self':
                if b_changeState:
                    _b_confirm = True
                    _funcString = 'changeState'
                    log.debug("|{0}| >> Change state and not self... | {1}".format(_str_func,_contextMode)) 
                    _title = 'Confirm non self state rig change...'
                    _message = '{0} | This is a long process with lots of blocks'.format(_funcString)
                    _text = _contextMode
                    

            if _startMode == 0 :#Active
                log.debug("|{0}| >> Active start".format(_str_func))                
                mBlock = self._blockCurrent
                
                if not mBlock:
                    log.error("|{0}| >> No Active block".format(_str_func))
                    return False
                
                if _b_confirm:
                    if not confirm(_title, _message, _funcString):return False                
                
                if b_rootMode:
                    mRoot = mBlock.getBlockRoot()
                    if mRoot:
                        mBlock = mRoot
                    else:
                        mBlock = mBlock.getBlockRoot()
                    
                ml_blocks = [mBlock]
                #RIGBLOCKS.contextual_rigBlock_method_call(mBlock,_contextMode,*args,**kws)
                
                #if _updateUI:
                    #self.uiUpdate_scrollList_blocks(mBlock)
                    #self.uiUpdate_blockDat()
                
            else:
                log.debug("|{0}| >> start: {1}".format(_str_func,_startMode))
                _indices = self.uiScrollList_blocks.getSelectedIdxs()
                if not _indices:
                    log.error("|{0}| >> Nothing selected".format(_str_func))
                    return False    
                if not self._ml_blocks:
                    log.error("|{0}| >> No blocks detected".format(_str_func))
                    return False    

                for i in _indices:
                    ml_blocks.append( self._ml_blocks[int(str(i).split('L')[0])])
                    
                if not ml_blocks:
                    log.error("|{0}| >> Failed to query indices: {1}".format(_str_func,_indices))
                    return False
                
            if args[0] == 'VISUALIZEHEIRARCHY':
                BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks[0],_contextMode,False,True)
                return True
                
            _len = len(ml_blocks)
            if _b_confirm and _len>1:
                _message = "{0} \n Selected: {1}".format(_message,len(ml_blocks))
                if not confirm(_title, _message, _funcString):return False
                
            ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks,_contextMode,True,False)
            
            if _reverseContext:
                log.warning(cgmGEN.logString_msg(_str_func,'REVERSE CONTEXT MODE ON'))
                
                ml_context.reverse()
            #Now parse to sets of data
            if args[0] == 'stepUI':
                return ui_stepBuild(ml_blocks[0])
            elif args[0] == 'select':
                #log.info('select...')
                return mc.select([mBlock.mNode for mBlock in ml_context])
            elif args[0]== 'focus':
                log.debug("|{0}| >> Focus call | {1}".format(_str_func,_contextMode))
                #ml_root = BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks,'root',True,False)
                for mBlock in ml_blocks:
                    log.info("|{0}| >> Focus call | {1}".format(_str_func,mBlock))                    
                    mBlock.UTILS.focus(mBlock,args[1],args[2],ml_focus=ml_blocks)
                return
            
            
            int_len = len(ml_context)
            self.uiRow_progress(edit=1,vis=True,m=True)                
            self.uiProgressText(edit=True,vis=True,label="Processing...")
            mc.progressBar(self.uiPB_mrs,edit=True,vis=True)
            #cgmUI.progressBar_test(self.uiPB_mrs,5,.001)
            
            i_add = 0
            if int_len == 1:
                i_add = 1
                
            for i,mBlock in enumerate(ml_context):
                _short = mBlock.p_nameShort
                _call = str(args[0])
                if _call in ['atUtils']:
                    _call = str(args[1])
                    
                self.uiProgressText(edit=True,label="{0}/{1} | {2} | call: {3}".format(i+1,int_len,
                                                                             _short,_call))
                mc.progressBar(self.uiPB_mrs,edit=True,maxValue = int_len,progress = i, vis=1)
                #cgmUI.progressBar_set(self.uiPB_mrs,
                #                      maxValue = int_len+1,
                #                      progress=i+i_add, vis=True)
                log.debug("|{0}| >> Processing: {1}".format(_str_func,mBlock)+'-'*40)
                res = getattr(mBlock,args[0])(*args[1:],**kws) or None
                log.debug("|{0}| >> res: {1}".format(_str_func,res))
                
                
            #if _updateUI:
                #self.uiUpdate_scrollList_blocks()
                
            if _updateUI:
                self.uiUpdate_scrollList_blocks()
                
            if args[0] not in ['delete'] and _startMode != 0:
                #ml_processed.extend(BLOCKGEN.get_rigBlock_heirarchy_context(mBlock,_contextMode,True,False))
                self.uiScrollList_blocks.selectByIdx(_indices[0])                

            return ml_context
                
        #except Exception,err:
        #    cgmGEN.cgmExceptCB(Exception,err)
        finally:
            self.uiRow_progress(edit=1,vis=False)
            self.uiProgressText(edit=True,label='...')
            #cgmUI.progressBar_end(self.uiPB_mrs)
    @cgmGEN.Timer
    def uiFunc_contextModuleCall(self,*args,**kws):
        try:
            _str_func = ''
            _updateUI = kws.pop('updateUI',True)
            _startMode = self.var_contextStartMode.value   
            _contextMode = self._l_contextModes[self.var_contextMode.value]
            ml_blocks = []
            
            if _startMode == 0 :#Active
                mBlock = self._blockCurrent
                
                if not mBlock:
                    log.error("|{0}| >> No Active block".format(_str_func))
                    return False
                ml_blocks = [mBlock]
                
            else:
                _indices = self.uiScrollList_blocks.getSelectedIdxs()
                if not _indices:
                    log.error("|{0}| >> Nothing selected".format(_str_func))                                                        
                    return False    
                if not self._ml_blocks:
                    log.error("|{0}| >> No blocks detected".format(_str_func))                                                        
                    return False   
                
                for i in _indices:
                    ml_blocks.append( self._ml_blocks[int(str(i).split('L')[0])])
                    
                if not ml_blocks:
                    log.error("|{0}| >> Failed to query indices: {1}".format(_str_func,_indices))
                    return False                
                
            self.uiRow_progress(edit=1,vis=1)
            ml_context = BLOCKGEN.get_rigBlock_heirarchy_context(ml_blocks,_contextMode,True,False)
            pprint.pprint(ml_context)
            #Now parse to sets of data
            if args[0] == 'select':
                #log.info('select...')
                return mc.select([mBlock.mNode for mBlock in ml_context])
            
            int_len = len(ml_context)
            for i,mBlock in enumerate(ml_context):
                _short = mBlock.p_nameShort
                _call = str(args[0])
                if _call in ['atUtils']:
                    _call = str(args[1])
                self.uiProgressText(edit=True,vis=1,label="{0}/{1} | {2} | call: {3}".format(i,int_len,_short,_contextMode,_call))
                
                cgmUI.progressBar_start(self.uiPB_mrs,int_len)
                cgmUI.progressBar_set(self.uiPB_mrs,
                                      maxValue = int_len,
                                      progress=i, vis=True)
                
                log.debug("|{0}| >> Processing: {1}".format(_str_func,mBlock)+'-'*40)
                res = RIGBLOCKS.contextual_module_method_call(mBlock,'self',*args,**kws)
                log.debug("|{0}| >> res: {1}".format(_str_func,res))

        finally:
            self.uiRow_progress(edit=1,vis=0)
            self.uiProgressText(edit=True,label='...')
            cgmUI.progressBar_end(self.uiPB_mrs)
            
    def uiFunc_contextPuppetCall(self,*args,**kws):
        _str_func = ''
        _startMode = self.var_contextStartMode.value   
        
        if _startMode == 0 :#Active
            mBlock = self._blockCurrent
            if not mBlock:
                log.error("|{0}| >> No Active block".format(_str_func))
                return False
        else:
            _indices = self.uiScrollList_blocks.getSelectedIdxs()
            if not _indices:
                log.error("|{0}| >> Nothing selected".format(_str_func))                                                        
                return False    
            if not self._ml_blocks:
                log.error("|{0}| >> No blocks detected".format(_str_func))
                return False    
            
            _index = int(str(_indices[0]).split('L')[0])
            try:mBlock = self._ml_blocks[_index]   
            except:
                log.error("|{0}| >> Failed to query index: {1}".format(_str_func,_index))                                                        
                return False
            
        mPuppet = mBlock.atUtils('get_puppet')
        if not mPuppet:
            return log.error("|{0}| >> No puppet found.".format(_str_func,_index))
        
        if args[0] == 'postUI':
            return ui_post(mPuppet)
        return mPuppet.atUtils(*args,**kws)
        
        return
        RIGBLOCKS.contextual_module_method_call(mBlock,_contextMode,*args,**kws)
        if _updateUI:
            self.uiUpdate_scrollList_blocks(mBlock)
            self.uiUpdate_blockDat()
            
            
    def uiFunc_block_select_dcc(self,*args,**kws):
        if self._blockCurrent:
            self._blockCurrent.select()
            
    def uiScrollList_block_select(self): 
        try:
            _str_func = 'uiScrollList_block_select'  
    
            if self.uiPopUpMenu_blocks:
                self.uiPopUpMenu_blocks.clear()
                self.uiPopUpMenu_blocks.delete()
                self.uiPopUpMenu_blocks = None        
    
            _indices = self.uiScrollList_blocks.getSelectedIdxs() or []
            _ml = self.get_blockList()
            
            if not _indices or not _ml:
                self.uiUpdate_scrollList_blocks()
                return
            
            if len(_indices) > 1:
                return
            
            _index = int(str(_indices[0]).split('L')[0])
            try:_mBlock = _ml[_index]
            except:
                log.warning("|{0}| >> Index failed to query: {1}. Reloading list....".format(_str_func, _index))                        
                self.uiUpdate_scrollList_blocks()
                return                
            
            _blockState = _mBlock.p_blockState
            _short = _mBlock.p_nameShort
            if _mBlock.mNode == None:
                log.warning("|{0}| >> Index failed to query: {1}. Reloading list....".format(_str_func, _index))                        
                self.uiUpdate_scrollList_blocks()
                return
            
            #self.uiFunc_block_setActive(mBlock=_mBlock)
            
            _mActiveBlock = self._blockCurrent
            _str_activeBlock = False
            if _mActiveBlock:
                _str_activeBlock = _mActiveBlock.mNode
        
            self.uiPopUpMenu_blocks = mUI.MelPopupMenu(self.uiScrollList_blocks,button = 3)
            _popUp = self.uiPopUpMenu_blocks 
            
            _b_active = False
            if _mActiveBlock:
                _b_active = True
                
            #>>>Special menu ---------------------------------------------------------------------------------------
            
            mBlockModule = _mBlock.p_blockModule
            reload(mBlockModule)
            
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
            
            mUI.MelMenuItem(_popUp,
                            ann = 'Initialize the block as mBlock in the script editor',
                            c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'toScriptEditor'}),
                            label = "To ScriptEditor")            
            #>>>Heirarchy ------------------------------------------------------------------------------------
            _menu_parent = mUI.MelMenuItem(_popUp,subMenu=True,
                                           label = "Parent")
            

            
            mUI.MelMenuItem(_menu_parent,
                            en = _b_active,
                            ann = 'Set parent block to active block: {0}'.format(_str_activeBlock),
                            c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'setParentToActive'}),
                            label = "To active")
            mUI.MelMenuItem(_menu_parent,
                            ann = 'Clear parent block',
                            c = cgmGEN.Callback(self.uiFunc_blockManange_fromScrollList,**{'mode':'clearParentBlock'}),
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
            #...side ----------------------------------------------------------------------------------------
            sub_side = mUI.MelMenuItem(_popUp,subMenu=True,
                                       label = 'Set side')
            
            for i,side in enumerate(['None','left','right','center']):
                mUI.MelMenuItem(sub_side,
                                label = side,
                                ann = 'Specify the side for the current block to : {0}'.format(side),
                                c = uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'set_side',i))
            #...position ------------------------------------------------------------------------------
            #none:upper:lower:front:back:top:bottom
            sub_position = mUI.MelMenuItem(_popUp,subMenu=True,
                                           label = 'Set position')
            for i,position in enumerate(['None','upper','lower','front','back','top','bottom']):
                mUI.MelMenuItem(sub_position,
                                label = position,
                                ann = 'Specify the position for the current block to : {0}'.format(position),
                                c = uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'set_position',i))
            
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
                            c=uiCallback_withUpdate(self,_mBlock,_mBlock.atBlockUtils,'duplicate'))            
            
            return
            #>>Queries ---------------------------------------------------------------------------------------
            _queries = mUI.MelMenuItem(_popUp, subMenu = True,
                                       label = "Queries",
                                       en=True,)   
            
            _d_queries = {'getBlockChildren':{'asMeta':False},
                          'getBlockParents':{'asMeta':False},
                          'getBlockHeirarchyBelow':{'asMeta':False,'report':True},
                          'printBlockDat':{},
                          'getModuleStatus':{},
                          'getBlockDat':{'report':True}}
            for q,d_kws in _d_queries.iteritems():
                mUI.MelMenuItem(_queries,
                                label = q,
                                ann = '[{0}] {1}'.format(_short,q),                            
                                c=cgmGEN.Callback( _mBlock.string_methodCall, q, **d_kws) )
                
    
            #>>Rig processes -----------------------------------------------------------------------------------------------
            mUI.MelMenuItemDiv(_popUp)
            _b_rigged=False
            if _blockState == 'rig':
                _b_rigged = True
            _rigMenu = mUI.MelMenuItem(_popUp, subMenu = True,
                                       en=_b_rigged,
                                       label = "Rig")
            if _b_rigged:
                mUI.MelMenuItem(_rigMenu,
                                label = 'Verify Proxy',
                                ann = '[{0}] Verify a proxy mesh on the block. Warning - resetting rig positions is necessary'.format(_short),
                                c=cgmGEN.Callback( _mBlock.verify_proxyMesh,True ))
                mUI.MelMenuItem(_rigMenu,
                                label = 'Reset Rig controls',
                                ann = '[{0}] Reset rig controls'.format(_short),
                                c=cgmGEN.Callback( _mBlock.atRigModule, 'rig_reset' ))
                mUI.MelMenuItem(_rigMenu,
                                label = 'Connect Rig',
                                ann = '[{0}] {1}'.format(_short,self._d_ui_annotations.get('rig connect')),
                                c=cgmGEN.Callback( _mBlock.atRigModule, 'rig_connect' ))
                mUI.MelMenuItem(_rigMenu,
                                label = 'Disconnect Rig',
                                ann = '[{0}] {1}'.format(_short,self._d_ui_annotations.get('rig disconnect')),
                                c=cgmGEN.Callback( _mBlock.atRigModule, 'rig_disconnect' ))
                #mUI.MelMenuItem(_rigMenu,
                #                label = 'Verify Armature',
                #                ann = '[{0}] {1}'.format(_short,self._d_ui_annotations.get('armature')),
                #                c=cgmGEN.Callback( _mBlock.atRigModule, 'rig_disconnect' ))                
            return
            #>>Context ============================================================================================
            _menu_context = mUI.MelMenuItem(_popUp,subMenu=True,
                                           label = "Context: {0}".format(self._l_contextModes[self.var_contextMode.value]))
             
            
            
            _menu_blockDat = mUI.MelMenuItem(_menu_context,subMenu=True,
                                             label = "blockDat")        
            _menu_state = mUI.MelMenuItem(_menu_context,subMenu=True,
                                          label = "state")         
            mUI.MelMenuItem(_menu_context,
                             en=False,
                             label = "skeletonize")   
            mUI.MelMenuItem(_menu_context,
                            en=False,
                            label = "Mesh")           
            #self.uiUpdate_scrollList_blocks()
            return
        
        
            if len(_indices) == 1:
                _b_single = True
        
                log.debug("|{0}| >> Single pop up mode".format(_str_func))  
                _short = ml_parents[int(str(_indices[0]).split('L')[0])].p_nameShort
                mUI.MelMenuItem(_popUp,
                                label = "Single: {0}".format(_short),
                                en=False)            
            else:
                log.debug("|{0}| >> Multi pop up mode".format(_str_func))  
                mUI.MelMenuItem(_popUp,
                                label = "Mutli",
                                en=False)  
                _b_single = False
        
        
            if _b_single:
                mUI.MelMenuItem(_popUp,
                                label ='Alias',
                                ann = 'Enter value desired in prompt',
                                c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'alias'}))
                mUI.MelMenuItem(_popUp,
                                label ='Clear Alias',
                                ann = 'Remove any alias',
                                c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'aliasClear'}))
        
            mUI.MelMenuItem(_popUp,
                            label ='Set Name',
                            ann = 'Specify the name for the current block. Current: {0}'.format(_mActiveBlock.cgmName),
                            c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'setName'}))
            
            mUI.MelMenuItem(_popUp,
                            label ='Select',
                            ann = 'Select specified indice parents',
                            c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'select'}))
            
            mUI.MelMenuItem(_popUp,
                            label ='Move Up',
                            ann = 'Move selected up in list',
                            c = cgmGEN.Callback(self.uiFunc_dynParents_reorder,0)) 
            mUI.MelMenuItem(_popUp,
                            label ='Move Down',
                            ann = 'Move selected down in list',
                            c = cgmGEN.Callback(self.uiFunc_dynParents_reorder,1)) 
        
            self._ml_objList = cgmMeta.validateObjListArg( CONTEXT.get_list(getTransform=True) )        
            uiMenu_changeSpace(self,_popUp)
        
            return
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
    def uiFunc_block_clearActive(self):
        #self.uiField_inspector(edit=True, label = '')
        self.uiField_report(edit=True, label = '')        
        self._blockCurrent = None
        #self.uiFrame_blockAttrs.clear()
        self.uiFrame_blockInfo.clear()
        
    def get_blockList(self):
        _str_func = 'get_blockList'        
        l = []
        if self._blockCurrent and self._blockCurrent.mNode == None:
            self._blockCurrent = False
            log.debug("|{0}| >> Current no longer exists | {1} ".format(_str_func,self._blockCurrent))
            
        for mBlock in self._ml_blocks:
            if mBlock.mNode is not None:
                l.append(mBlock)
            else:
                log.debug("|{0}| >>Dead node | {1} ".format(_str_func,mBlock))
            
        self._ml_blocks = l
        return self._ml_blocks
                
    def uiFunc_block_setActive(self, index = None, mBlock = None):
        try:
            _str_func = 'uiFunc_block_setActive'
            
            _ml = self.get_blockList()
            if not _ml:
                self.uiFunc_block_clearActive()
                return
            
            """
            try:_blockCurrent = self._blockCurrent
            except:
                log.debug("|{0}| >> Current no longer exists. Reloading...".format(_str_func))                
                self.uiUpdate_scrollList_blocks()
                return"""
            
            _idx_current = None
            if self._blockCurrent and self._blockCurrent.mNode and self._blockCurrent in _ml:
                _idx_current = _ml.index(self._blockCurrent)
    
            log.debug("|{0}| >> Current: {1}".format(_str_func, _idx_current))    
            
            if index is not None:
                if index in self._ml_blocks:
                    index = self._ml_blocks.index(index)
                if index not in range(len(_ml)):
                    log.warning("|{0}| >> Invalid index: {1}".format(_str_func, index))    
                    return
            elif mBlock:
                if mBlock in self._ml_blocks:
                    index = self._ml_blocks.index(mBlock)
                else:
                    raise ValueError,"mBlock not found in list: {0}".format(mBlock)
            else:
                _indices = self.uiScrollList_blocks.getSelectedIdxs() or []
                log.debug("|{0}| >> indices: {1}".format(_str_func, _indices))    
            
                if not _indices:
                    log.warning("|{0}| >> Nothing selected".format(_str_func))                    
                    
                    if _idx_current is not None:
                        log.debug("|{0}| >> Using Current: {1}".format(_str_func, _idx_current))                        
                        index = _idx_current
                
                if not index:
                    #index = _indices[0]
                    index = int(str(_indices[0]).split('L')[0])
                    
            
            if _ml[index].mNode == None:
                log.warning("|{0}| >> Index failed to query: {1}. Reloading list....".format(_str_func, index))            
                self.uiUpdate_scrollList_blocks()                    
                return
            
            log.info("|{0}| >> To set: {1}".format(_str_func, _ml[index].mNode))
            self._blockFactory.set_rigBlock( _ml[index] )
            self._blockCurrent = _ml[index]
            _short = self._blockCurrent.p_nameShort
            
            #>>>Inspector ===================================================================================
            #>>>Report ---------------------------------------------------------------------------------------
            
            _l_report = ["Active: {0}".format(self._blockCurrent.p_nameShort)]
            if self._blockCurrent.hasAttr('buildProfile'):
                _l_report.insert(0,str(self._blockCurrent.buildProfile))
            #if ATTR.get(_short,'side'):
                #_l_report.append( ATTR.get_enumValueString(_short,'side'))
            if ATTR.has_attr(_short,'blockProfile'):
                _l_report.append("{0} - {1}".format(self._blockCurrent.blockProfile,
                                                    self._blockCurrent.blockType))
            else:
                _l_report.append("{0}".format(self._blockCurrent.blockType))                
            
            if self._blockCurrent.isReferenced():
                _l_report.insert(0,"Referenced!")
                
            #self.uiField_inspector(edit=True, label = '{0}'.format(' | '.join(_l_report)))
            self.uiField_report(edit=True, label = '[ ' + '{0}'.format(' ] [ '.join(_l_report))+ ' ]')
            
            #>>>Settings -------------------------------------------------------------------------------------
            self.uiUpdate_blockDat()#<<< build our blockDat frame
            
            #>>>Info ----------------------------------------------------------------------------------------
            self.uiFrame_blockInfo.clear()
            
            for l in self._blockCurrent.atBlockUtils('get_infoBlock_report'):
                mUI.MelLabel(self.uiFrame_blockInfo,l=l)
                
            return
            #>>>Attrs ----------------------------------------------------------------------------------------
            self.uiFrame_blockAttrs.clear()
            
            for a in self._blockCurrent.getAttrs(ud=True):
                if a in ['blockDat']:
                    continue
                if a not in ['attributeAliasList']:
                    if ATTR.get_type(_short,a) == 'enum':
                        mUI.MelLabel(self.uiFrame_blockAttrs,l="{0}:{1}".format(a,ATTR.get_enumValueString(_short,a)))                   
                    else:
                        mUI.MelLabel(self.uiFrame_blockAttrs,l="{0}:{1}".format(a,ATTR.get(_short,a)))
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
             
    def uiCallback_setAttrFromField(self, obj, attr, attrType, field):
        _v = field.getValue()
        ATTR.set(obj,attr,_v)
        
        if attrType == 'enum':
            _strValue = ATTR.get_enumValueString(obj,attr)
            field.setValue(_strValue)
            
            if attr == 'buildProfile':
                log.info("Loading buildProfile...")
                self._blockCurrent.atUtils('buildProfile_load',_strValue)
            if attr == 'blockProfile':
                log.info("Loading blockProfile...")
                self._blockCurrent.atUtils('blockProfile_load',_strValue)                
        else:
            field.setValue(ATTR.get(obj,attr))
            
        if attr == 'numRoll':
            log.info("numRoll check...")                            
            if ATTR.datList_exists(obj,'rollCount'):
                log.info("rollCount Found...")                                            
                l = ATTR.datList_getAttrs(obj,'rollCount')
                for a in l:
                    log.info("{0}...".format(a))                                                
                    ATTR.set(obj,a, _v)
                
                #self.uiUpdate_blockDat()
        
        log.info("Set: {0} | {1} | {2}".format(obj,attr,_v))
            
    def uiCallback_contextualSetAttrFromField(self, attr, attrType, field):
        _v = field.getValue()
        
        log.info("{0} | {1}".format(attr,_v))

        self.uiFunc_contextBlockCall('atUtils', 'blockAttr_set', **{'updateUI':False, attr:_v})
        
        if attr == 'buildProfile':
            #_strValue = BLOCKSHARE._d_attrsTo_make['buildProfile'].split(':')[_v]
            log.info("Loading buildProfile... {0}".format(_v))
            self.uiFunc_contextBlockCall('atUtils', 'buildProfile_load', _v, **{'updateUI':False})
        
        
        return
        if attrType == 'enum':
            #_strValue = ATTR.get_enumValueString(obj,attr)
            #field.setValue(_strValue)
            
            if attr == 'buildProfile':
                log.info("Loading buildProfile...")
                self._blockCurrent.atUtils('buildProfile_load',_strValue)
            if attr == 'blockProfile':
                log.info("Loading blockProfile...")
                self._blockCurrent.atUtils('blockProfile_load',_strValue)                
            
            
    def uiCallback_blockDatButton(self,func,*args,**kws):
        func(*args,**kws)
        self.uiUpdate_blockDat()
        
    def uiSection_blockDatUtils(self,parent):
        _str_func = 'uiUpdate_blockUtils'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        
        #self.uiFrame_blockDatUtils.clear()
        #_column = self.uiFrame_blockDatUtils
        
        _column = parent
        
        #BlcokDat ======================================================
        log.debug(cgmGEN.logString_sub(_str_func,'BlockDat Main'))
        mc.setParent(_column)
        _row = mUI.MelHLayout(_column,ut='cgmUISubTemplate',padding = 2)
        #mUI.MelSpacer(_row,w=1)
        
        mc.button(parent=_row,
                  l = 'Save',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'saveBlockDat',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('save blockDat'))
        mc.button(parent=_row,
                  l = 'Load',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'loadBlockDat',
                                      **{}),
                  ann = self._d_ui_annotations.get('load blockDat'))
        
        mc.button(parent=_row,
                  l = 'Load State',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'loadBlockDat',
                                      **{'autoPush':False,'currentOnly':True}),
                  ann = self._d_ui_annotations.get('load state blockDat'))
        
        mc.button(parent=_row,
                  l = 'Query',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'getBlockDat',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('get blockDat'))
        
        mc.button(parent=_row,
                  l = 'Copy',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockDat_copy',
                                      **{'mode':'blockDatCopyActive'}),
                  ann = "Copy the active blocks data")
        
        mc.button(parent=_row,
                  l = 'Reset',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockDat_reset',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('reset blockDat'))        
        
        #mUI.MelSpacer(_row,w=1)
        _row.layout()
        
        #BlcokDat ======================================================
        log.debug(cgmGEN.logString_sub(_str_func,'BlockDat Selective'))
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        
        mUI.MelSpacer(_row,w=1)
        mUI.MelLabel(_row,l="Load State data: ")        
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        
        for state in ['define','template','prerig','skeleton',]:
            mc.button(parent=_row,
                      l = state.capitalize(),
                      ut = 'cgmUITemplate',
                      c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                          'atUtils','blockDat_load_state',state,
                                          **{'updateUI':0}),
                      ann = "Load {0} blockDat in context".format(state))
       
        mUI.MelSpacer(_row,w=1)
        _row.layout()        
        
        
    def uiUpdate_blockUtils(self):
        _str_func = 'uiUpdate_blockUtils'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        
        self.uiFrame_blockUtils.clear()
        
        _column = self.uiFrame_blockUtils
                
        
        
        #General ======================================================
        log.debug("|{0}| >> General ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row,w=1)        
        mUI.MelLabel(_row,l="General: ")
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        mc.button(parent=_row,
                  l = 'Select',
                  ut = 'cgmUITemplate',                                    
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'select',
                                      **{'updateUI':0}),
                  ann = 'Select blocks')
        mc.button(parent=_row,
                  l = 'Verify',
                  ut = 'cgmUITemplate',                                    
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'verify',
                                      **{'updateUI':0}),
                  ann = 'Verify conextual blocks')
        
        mc.button(parent=_row,
                  l = 'Recolor',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','color',
                                      **{'updateUI':0}),
                  ann = 'Recolor conextual blocks')
        
        mc.button(parent=_row,
                  l = 'Duplicate',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','duplicate',
                                      **{'updateUI':1}),
                  ann = 'Duplicate conextual blocks')
        
        
        mc.button(parent=_row,
                  l = 'Delete',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'delete',
                                      **{'updateUI':1}),
                  ann = 'Delete conextual blocks')
        
        mUI.MelSpacer(_row,w=1)
        _row.layout()
        
        #General ======================================================
        """
        log.debug("|{0}| >> Queries ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row,w=1)        
        mUI.MelLabel(_row,l="Queries: ")
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        mc.button(parent=_row,
                  l = 'Buildable?',
                  ut = 'cgmUITemplate',                                    
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'getModuleStatus',
                                      **{'updateUI':0}),
                  ann = "Check if the block is buildable (DEV)")
        mc.button(parent=_row,
                  l = 'Visualize',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'VISUALIZEHEIRARCHY',
                                      **{'updateUI':0}),
                  ann = 'Visualize the block tree in the script editor')
        mUI.MelSpacer(_row,w=1)
        _row.layout()
        """
        """
        #Parent ======================================================
        log.debug("|{0}| >> parenting ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row,w=1)
        mUI.MelLabel(_row,l="Parent: ")        
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        
        mc.button(parent=_row,
                  l = 'To Active',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockParent_set',
                                      **{'mode':'setParentToActive'}),
                  ann = 'Set parent block to active block')
        mc.button(parent=_row,
                  l = 'Clear',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockParent_set',
                                      **{'parent':False}),
                  ann = 'Clear blockParent')
        mUI.MelSpacer(_row,w=1)
        _row.layout()
        """
        """
        #Side ======================================================
        log.debug("|{0}| >> side ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        
        mUI.MelSpacer(_row,w=1)
        mUI.MelLabel(_row,l="Set Side: ")        
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        for i,side in enumerate(['none','left','right','center']):
            mc.button(parent=_row,
                              l = side,
                              ut = 'cgmUITemplate',
                              c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                  'atUtils','set_side',side,
                                                  **{}))

        mUI.MelSpacer(_row,w=1)
        _row.layout()   
        """
        
        """
        #Naming ======================================================
        log.debug("|{0}| >> naming ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        
        mUI.MelSpacer(_row,w=1)
        mUI.MelLabel(_row,l="Naming: ")        
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        
        mc.button(parent=_row,
                  l = 'Set Name',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','set_nameTag',
                                      **{}),
                  ann = 'Set the name tag of the block and rename dags')
        mc.button(parent=_row,
                  l = 'Set Position',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','set_position',
                                      **{'ui':True}),
                  ann = 'Set the position tag of the block and rename dags')
        
        mUI.MelSpacer(_row,w=1)
        _row.layout()        
        """
        #NameList ======================================================
        """
        log.debug("|{0}| >> NameList ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        
        mUI.MelSpacer(_row,w=1)
        mUI.MelLabel(_row,l="Name List: ")        
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        
        mc.button(parent=_row,
                  l = 'Reset to Profile',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','nameList_resetToProfile',
                                      **{}),
                  ann = 'Reset the name list to the profile')
        mc.button(parent=_row,
                  l = 'Iter from base name',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','set_nameListFromName',
                                      **{}),
                  ann = 'Set nameList values from name attribute')        
        
        mUI.MelSpacer(_row,w=1)
        _row.layout()                
        """
        
        #BlcokDat ======================================================
        log.debug("|{0}| >> Blockdat ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        
        mUI.MelSpacer(_row,w=1)
        mUI.MelLabel(_row,l="BlockDat: ")        
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        
        mc.button(parent=_row,
                  l = 'Save',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'saveBlockDat',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('save blockDat'))
        mc.button(parent=_row,
                  l = 'Load',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'loadBlockDat',
                                      **{}),
                  ann = self._d_ui_annotations.get('load blockDat'))
        
        mc.button(parent=_row,
                  l = 'Load State',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'loadBlockDat',
                                      **{'autoPush':False,'currentOnly':True}),
                  ann = self._d_ui_annotations.get('load state blockDat'))
        
        mc.button(parent=_row,
                  l = 'Query',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'getBlockDat',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('get blockDat'))
        
        mc.button(parent=_row,
                  l = 'Copy',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockDat_copy',
                                      **{'mode':'blockDatCopyActive'}),
                  ann = "Copy the active blocks data")
        
        mc.button(parent=_row,
                  l = 'Reset',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockDat_reset',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('reset blockDat'))        
        
        mUI.MelSpacer(_row,w=1)
        _row.layout()
        
        
        #Mirror ======================================================
        log.debug("|{0}| >> mirror ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)                
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row,w=1)
        
        mUI.MelLabel(_row,l="Mirror: ")
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        mc.button(parent=_row,
                  l = 'Verify',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockMirror_create',
                                      **{}),
                  ann = 'Verify block mirrors. WARNING - do not do this with a block and its mirror selected')
        mc.button(parent=_row,
                  l = 'Rebuild',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockMirror_create',True,
                                      **{}),
                  ann = 'Rebuild mirror block from scratch. WARNING - do not do this with a block and its mirror selected')
        
        
        mc.button(parent=_row,
                  l = 'Push',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockMirror_go',
                                      **{'mode':'push','updateUI':0}),
                  ann = 'Push setup to the mirror')
        mc.button(parent=_row,
                  l = 'Pull',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','blockMirror_go',
                                      **{'mode':'pull','updateUI':0}),
                  ann = 'pull setup to the mirror')
        mUI.MelSpacer(_row,w=5)
        
        mc.button(parent=_row,
                  l = 'Self[L]',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','mirror_self',
                                      **{'primeAxis':'left','updateUI':0}),
                  ann = 'Mirror self - Left Prime Axis')
        mc.button(parent=_row,
                  l = 'Self[R]',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','mirror_self',
                                      **{'primeAxis':'right','updateUI':0}),
                  ann = 'Mirror self - Righ Prime Axis')        
        mUI.MelSpacer(_row,w=1)
        _row.layout()
        
        
        """
        #Define ======================================================
        log.debug("|{0}| >> define ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)                
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row,w=1)
        
        mUI.MelLabel(_row,l="Define: ")
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        mc.button(parent=_row,
                  l = 'Load base size dat',
                  ut = 'cgmUITemplate',                                    
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils', 'define_set_baseSize',
                                      **{'updateUI':0}),
                  
                  ann = "Reset define dat to base")
        mUI.MelSpacer(_row,w=1)
        _row.layout()
        """
        """
        #Visualize ======================================================
        log.debug("|{0}| >> Visualize ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row,w=1)        
        mUI.MelLabel(_row,l="Visualize: ")
        _row.setStretchWidget( mUI.MelSeparator(_row) )        
            
        mc.button(parent=_row,
                         l = 'RP Pos',
                         ut = 'cgmUITemplate',                                    
                         c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                             'atUtils', 'prerig_get_rpBasePos',
                                             **{'markPos':1,'updateUI':0}),
                         ann = "Create locator at the where the system thinks your rp handle will be")    

        mUI.MelSpacer(_row,w=1)
        _row.layout()
        
        #Prerig ======================================================
        log.debug("|{0}| >> prerig ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row,w=1)        
        mUI.MelLabel(_row,l="Prerig: ")
        _row.setStretchWidget( mUI.MelSeparator(_row) )        
            
        mc.button(parent=_row,
                         l = 'Snap RP to Orient',
                         ut = 'cgmUITemplate',                                    
                         c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                             'atUtils', 'prerig_snapRPtoOrientHelper',
                                             **{'updateUI':0}),
                         ann = "Snap rp hanlde to orient vector")    
        mc.button(parent=_row,
                  l = 'Query Indices',
                  ut = 'cgmUITemplate',                                    
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atBlockModule', 'get_handleIndices',
                                      **{'updateUI':0}),
                  ann = "Snap handles to rp plane")
        mc.button(parent=_row,
                  l = 'Snap to RP',
                  ut = 'cgmUITemplate',                                    
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils', 'prerig_snapHandlesToRotatePlane',
                                      **{'updateUI':0}),
                  ann = "Snap handles to rp plane")
        mUI.MelSpacer(_row,w=1)
        _row.layout()
        
        #Rig ======================================================
        log.debug("|{0}| >> rig ...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row,w=1)        
        mUI.MelLabel(_row,l="Rig: ")
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        mc.button(parent=_row,
                  l = 'Verify Proxy',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'verify_proxyMesh',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('verify proxy mesh'))
        mc.button(parent=_row,
                  l = 'Reset Controls',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextModuleCall,
                                      'rig_reset',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('reset rig controls'))
        mc.button(parent=_row,
                  l = 'Query Nodes',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                      'atUtils','rigNodes_get',
                                      **{'updateUI':0,'report':True}),
                  ann = self._d_ui_annotations.get('query rig nodes'))        
        
        
        

        mUI.MelSpacer(_row,w=1)
        _row.layout()        
        
        #Rig Connect ======================================================
        log.debug("|{0}| >> Rig Connect...".format(_str_func)+ '-'*40)
        mc.setParent(_column)
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row,w=1)        
        mUI.MelLabel(_row,l="Rig Connect: ")
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        
        mc.button(parent=_row,
                  l = 'Connect',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextModuleCall,
                                      'rig_connect',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('connect rig'))
        mc.button(parent=_row,
                  l = 'Disconnect',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_contextModuleCall,
                                      'rig_disconnect',
                                      **{'updateUI':0}),
                  ann = self._d_ui_annotations.get('disconnect rig'))
        
        mUI.MelSpacer(_row,w=1)
        _row.layout()                
        """
        
        return
        _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)

        mUI.MelLabel(_row,l=' {0}:'.format(n))
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        if n in l_settings:
            l_options = ['hide','show']
            _mode = 'moduleSettings'
        elif n in l_locks:
            l_options = ['unlock','lock']
            _mode = 'moduleSettings'
            _plug = d_shared[n].get('plug',n)
        else:
            l_options = ['off','lock','on']
            _mode = 'puppetSettings'
            
        for v,o in enumerate(l_options):
            mc.button(parent = _row,
                      ut = 'cgmUITemplate',
                      l=o,
                      c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                        'atUtils', 'messageConnection_setAttr',
                                        _plug,**{'template':v}),
                      )
        mUI.MelSpacer(_row,w=2)
        _row.layout()        
        
        
    @cgmGEN.Timer
    def uiUpdate_blockShared(self):
        _str_func = 'uiUpdate_blockShared'
        self.uiFrame_shared.clear()
        
        _column = self.uiFrame_shared
        
        d_shared = {'templateNull':{},
                    'prerigNull':{}}
        
        l_settings = ['visibility']
        l_locks = ['rigBlock','templateNull','prerigNull']
        l_enums = []
    
        for n in l_locks:
            _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
            
            mUI.MelLabel(_row,l=' {0}:'.format(n))
            _row.setStretchWidget( mUI.MelSeparator(_row) )
    
            if n in l_settings:
                l_options = ['hide','show']
                _mode = 'moduleSettings'
            elif n in l_locks:
                l_options = ['unlock','lock']
                _mode = 'moduleSettings'
                if n != 'rigBlock':
                    _plug = d_shared[n].get('plug',n)
            else:
                l_options = ['off','lock','on']
                _mode = 'puppetSettings'
                
            for v,o in enumerate(l_options):
                if n == 'rigBlock':
                    mc.button(parent = _row,
                              ut = 'cgmUITemplate',
                              l=o,
                              c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils','templateAttrLock',v),
                              )                    
                else:
                    mc.button(parent = _row,
                              ut = 'cgmUITemplate',
                              l=o,
                              c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                'atUtils', 'messageConnection_setAttr',
                                                _plug,**{'template':v}),
                              )
            mUI.MelSpacer(_row,w=2)
            _row.layout()
            
        for n in l_settings:
            _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
    
            mUI.MelLabel(_row,l=' {0}:'.format(n))
            _row.setStretchWidget( mUI.MelSeparator(_row) )
    
            l_options = ['hide','show']

            for v,o in enumerate(l_options):
                mc.button(parent = _row,
                          ut = 'cgmUITemplate',
                          l=o,
                          c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                            'atUtils', 'blockAttr_set',
                                            **{n:v})
                          )
            mUI.MelSpacer(_row,w=2)
            _row.layout()
                        
        
        d_attrDat = copy.copy(BLOCKSHARE._d_attrsTo_make)
        
        for i in range(4):
            d_attrDat['rollCount_{0}'.format(i)] = 'int'
        
        _keys = d_attrDat.keys()
        _keys.sort()
        
        l_mask = ['baseAim','basePoint','baseUp','controlOffset','moduleTarget','nameIter','nameList',
                  'namesHandles','namesJoints']
        self._d_attrFieldsContextual = {}
        for a in _keys:
            if a in l_mask:
                continue
            try:
                _type = d_attrDat[a]
                log.debug("|{0}| >> attr: {1} | {2}".format(_str_func, a, _type))
                _row = mUI.MelHSingleStretchLayout(_column,padding = 5)
                mUI.MelLabel(_row,l=' {0}:'.format(a))
                mUI.MelSpacer(_row,w=_sidePadding)
                
                if ':' in _type:
                    _enum = _type.split(':')                    
                    _type = 'enum'
        
                _row.setStretchWidget(mUI.MelSeparator(_row,))
        
                if _type == 'bool':
                    l_options = ['off','on']
                    for v,o in enumerate(l_options):
                        mc.button(parent = _row,
                                  ut = 'cgmUITemplate',
                                  l=o,
                                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,
                                                    'atUtils', 'blockAttr_set',
                                                    **{'updateUI':False,a:v}))
                                  
                elif _type == 'enum':
                    _optionMenu = mUI.MelOptionMenu(_row)
                    _optionMenu(e=True,
                                cc = cgmGEN.Callback(self.uiCallback_contextualSetAttrFromField,
                                                     a,
                                                     _type,
                                                     _optionMenu)) 
                    
                    for option in _enum:
                        _optionMenu.append(option)
                
                elif _type in ['double','doubleAngle','doubleLinear','float']:
                    self._d_attrFieldsContextual[a] = mUI.MelFloatField(_row,w = 50)
                    self._d_attrFieldsContextual[a](e=True,
                                          cc  = cgmGEN.Callback(self.uiCallback_contextualSetAttrFromField, a, _type,
                                                                self._d_attrFieldsContextual[a]))
                elif _type in ['int','long']:
                    self._d_attrFieldsContextual[a] = mUI.MelIntField(_row,w = 50,
                                                              )
                    self._d_attrFieldsContextual[a](e=True,
                                          cc  = cgmGEN.Callback(self.uiCallback_contextualSetAttrFromField, a, _type,
                                                                self._d_attrFieldsContextual[a]),
                                          )                
 
                mUI.MelSpacer(_row,w=_sidePadding)                
                _row.layout()
            except Exception,err:
                log.info("Attr {0} failed. err: {1}".format(a,err))            
            
            
            
        
        
        return
        
        #Lock nulls row ------------------------------------------------------------------------
        _mRow_lockNulls = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 2)
        mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
        
        mUI.MelLabel(_mRow_lockNulls,l='Lock null:')
        _mRow_lockNulls.setStretchWidget(mUI.MelSeparator(_mRow_lockNulls,))
        
        for null in ['templateNull','prerigNull']:
            #_str_null = mBlock.getMessage(null)
            #_nullShort = _str_null[0]
            mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                            #value = ATTR.get(_nullShort,'template'),
                            #onCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',1),
                            #offCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',0))                
                            )
        
        mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
        _mRow_lockNulls.layout()        
    
    
    def uiUpdate_blockDat(self):
        _str_func = 'uiUpdate_blockDat'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        
        self.uiFrame_blockSettings.clear()
        #_d_ui_annotations = {}
        
        
        _short = self._blockCurrent.p_nameShort
        _intState = self._blockCurrent.getState(False)        
        mBlock = self._blockCurrent
        
        if not mBlock:
            return
        
        log.debug("|{0}| >>  Current Block: {1}".format(_str_func,mBlock))
        
        #Save/Load row... ------------------------------------------------------------------------
        _mBlockDat = mUI.MelHLayout(self.uiFrame_blockSettings,ut='cgmUISubTemplate',padding = 2)
        CGMUI.add_Button(_mBlockDat, "Save",
                         cgmGEN.Callback(self._blockCurrent.saveBlockDat),
                         self._d_ui_annotations.get('save blockDat'))       
        CGMUI.add_Button(_mBlockDat, "Load",
                         cgmGEN.Callback(self._blockCurrent.loadBlockDat),
                         self._d_ui_annotations.get('load blockDat') )       
        CGMUI.add_Button(_mBlockDat, "Copy",
                         cgmGEN.Callback(self.uiFunc_contextBlockCall,'loadBlockDat'),
                         self._d_ui_annotations.get('copy blockDat'),                         
                         en=False)         
    
        CGMUI.add_Button(_mBlockDat,'Reset',
                         cgmGEN.Callback(self._blockCurrent.resetBlockDat), 
                         self._d_ui_annotations.get('reset blockDat'))                                
        CGMUI.add_Button(_mBlockDat,'Refresh',
                         cgmGEN.Callback(self.uiUpdate_blockDat),
                         "Resync the ui blockDat with any changes you've made in viewport.")
        _mBlockDat.layout()
        
        #Lock nulls row ------------------------------------------------------------------------
        _mRow_lockNulls = mUI.MelHSingleStretchLayout(self.uiFrame_blockSettings,ut='cgmUISubTemplate',padding = 2)
        mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
        
        mUI.MelLabel(_mRow_lockNulls,l='Lock null:')
        _mRow_lockNulls.setStretchWidget(mUI.MelSeparator(_mRow_lockNulls,))
        
        for null in ['templateNull','prerigNull']:
            _str_null = mBlock.getMessage(null)
            if _str_null:
                _nullShort = _str_null[0]
                mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                                value = ATTR.get(_nullShort,'template'),
                                onCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',1),
                                offCommand = cgmGEN.Callback(ATTR.set,_nullShort,'template',0))                
            else:
                mUI.MelCheckBox(_mRow_lockNulls, l="- {0}".format(null),
                                en=False)
        
        mUI.MelSpacer(_mRow_lockNulls,w=_sidePadding)
        _mRow_lockNulls.layout()
        

        #Attrs... ------------------------------------------------------------------------
        _l_attrs = self._blockCurrent.atUtils('uiQuery_getStateAttrs',_intState)
    
        self._d_attrFields = {}
        _l_attrs.sort()
        for a in _l_attrs:
            try:
                _type = ATTR.get_type(_short,a)
                log.debug("|{0}| >> attr: {1} | {2}".format(_str_func, a, _type))
                _hlayout = mUI.MelHSingleStretchLayout(self.uiFrame_blockSettings,padding = 5)
                mUI.MelSpacer(_hlayout,w=_sidePadding)
        
                _hlayout.setStretchWidget(mUI.MelSeparator(_hlayout,))
        
                if _type not in ['bool']:#Some labels parts of fields
                    mUI.MelLabel(_hlayout,l="{0} -".format(a))   
        
                if _type == 'bool':
                    mUI.MelCheckBox(_hlayout, l="- {0}".format(a),
                                    #annotation = "Copy values",		                           
                                    value = ATTR.get(_short,a),
                                    onCommand = cgmGEN.Callback(ATTR.set,_short,a,1),
                                    offCommand = cgmGEN.Callback(ATTR.set,_short,a,0))
        
                elif _type in ['double','doubleAngle','doubleLinear','float']:
                    self._d_attrFields[a] = mUI.MelFloatField(_hlayout,w = 50,
                                                              value = ATTR.get(_short,a),                                                          
                                                              )
                    self._d_attrFields[a](e=True,
                                          cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                self._d_attrFields[a]),
                                          )
                elif _type == 'long':
                    self._d_attrFields[a] = mUI.MelIntField(_hlayout,w = 50,
                                                             value = ATTR.get(_short,a),
                                                             maxValue=20,
                                                             minValue=ATTR.get_min(_short,a),
                                                              )
                    self._d_attrFields[a](e=True,
                                          cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                self._d_attrFields[a]),
                                          )                
                elif _type == 'string':
                    self._d_attrFields[a] = mUI.MelTextField(_hlayout,w = 75,
                                                             text = ATTR.get(_short,a),
                                                              )
                    self._d_attrFields[a](e=True,
                                          cc  = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                                self._d_attrFields[a]),
                                          )
                elif _type == 'enum':
                    _optionMenu = mUI.MelOptionMenu(_hlayout)
                    _optionMenu(e=True,
                                cc = cgmGEN.Callback(self.uiCallback_setAttrFromField,_short, a, _type,
                                                     _optionMenu),) 
                    for option in ATTR.get_enumList(_short,a):
                        _optionMenu.append(option)
                    _optionMenu.setValue(ATTR.get_enumValueString(_short,a))
                else:
                    mUI.MelLabel(_hlayout,l="{0}({1}):{2}".format(a,_type,ATTR.get(_short,a)))        
        
                mUI.MelSpacer(_hlayout,w=_sidePadding)                
                _hlayout.layout()
            except Exception,err:
                log.info("Attr {0} failed. err: {1}".format(a,err))
                
        
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
        mUI.MelMenuItem( self.uiMenu_help, l="Get Call Size",
                         c=lambda *a: RIGBLOCKS.get_callSize('selection' ) )
        mUI.MelMenuItem( self.uiMenu_help, l="Test Context",
                         c=lambda *a: self.uiFunc_contextBlockCall('VISUALIZEHEIRARCHY') )
        
        
        
        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("https://http://docs.cgmonks.com/mrs.html");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )   
        mUI.MelMenuItem( self.uiMenu_help, l="Update Display",
                         c=lambda *a: self.uiUpdate_building() )
        
 
    def uiFunc_clear_loaded(self):
        _str_func = 'uiFunc_clear_loaded'  
        self._mNode = False
        self._mGroup = False
        self._utf_obj(edit=True, l='',en=False)      
        self.uiField_report(edit=True, l='...')
        #self.uiReport_objects()
        self.uiScrollList_parents.clear()
        
        for o in self._l_toEnable:
            o(e=True, en=False)        
        
    
    def uiUpdate_scrollList_blocks(self, select = None):
        _str_func = 'uiUpdate_scrollList_blocks'          
        self.uiScrollList_blocks.clear()
        
        _ml = []
        _l_strings = []
        
        _ml,_l_strings = BLOCKGEN.get_uiScollList_dat()
        
        """
        for i,s in enumerate(_l_strings):
            log.debug("|{0}| >> {1} : {2}".format(_str_func,_ml[i].mNode,s)) 
        """
        #_ml = BLOCKGEN.get_from_scene()
        
        self._ml_blocks = _ml
        
        _len = len(_ml)
        
        if not _ml:
            log.warning("|{0}| >> No blocks found in scene.".format(_str_func)) 
            self.uiFunc_block_clearActive()
            return False      

        #...menu...
        _progressBar = cgmUI.doStartMayaProgressBar(_len,"Processing...")
        
        try:
            for i,strEntry in enumerate(_l_strings):
                self.uiScrollList_blocks.append(strEntry)

        except Exception,err:
            try:
                log.error("|{0}| >> err: {1}".format(_str_func, err))  
                for a in err:
                    log.error(a)
                cgmUI.doEndMayaProgressBar(_progressBar)
            except:
                raise Exception,err

        cgmUI.doEndMayaProgressBar(_progressBar) 
        
        if select:
            if select in self._ml_blocks:
                self.uiScrollList_blocks.selectByIdx(self._ml_blocks.index(select))
                
    def uiUpdate_context(self,var=None,value=None):
        if var:
            var.setValue(value)
            
        _context = self._l_contextModes[self.var_contextMode.value]
        _contextStart = self._l_contextStartModes[self.var_contextStartMode.value]
        _force = self.var_contextForceMode.value
        
        if _context == 'self':
            log.info("Self mode means force = True")
            _force = 1
        
        _label = "Context: {0} | Begin with: {1} | Force: {2}".format(
        _context,
        _contextStart,
        bool(_force))
        
        self.uiFrame_context(edit=True,label=_label)
        #self.uiField_contextReport(edit=True,label=_label)
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
    
        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        
        ui_tabs = mUI.MelTabLayout( _MainForm,w=180 )
        
        uiTab_setup = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        self.uiTab_setup = uiTab_setup
        
        uiTab_utils = mUI.MelScrollLayout( ui_tabs,ut='cgmUITemplate' )
        
        for i,tab in enumerate(['Setup','Utils']):
            ui_tabs.setLabel(i,tab)
            
        self.buildTab_setup(uiTab_setup)
        self.buildTab_utilities(uiTab_utils)
        #TOOLBOX.buildTab_td(self,uiTab_utils)

        #self.buildTab_create(uiTab_create)
        #self.buildTab_update(uiTab_update)
    
        self.uiRow_progress = mUI.MelHLayout(_MainForm,vis=False)
        self.uiProgressText = mUI.MelLabel(self.uiRow_progress,
                                           bgc = SHARED._d_gui_state_colors.get('warning'),
                                           label = '...',
                                           h=20)        
        self.uiPB_mrs=None
        mc.setParent(self.uiRow_progress)
        self.uiPB_mrs = mc.progressBar()
        self.uiRow_progress.layout()
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)
        self.uiRow_cgm = _row_cgm
        _MainForm(edit = True,
                  af = [(ui_tabs,"top",0),
                        (ui_tabs,"left",0),
                        (ui_tabs,"right",0),
                        (self.uiRow_progress,"left",0),
                        (self.uiRow_progress,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(ui_tabs,"bottom",0,self.uiRow_progress),
                        (self.uiRow_progress,"bottom",0,_row_cgm)
                        ],
                  attachNone = [(_row_cgm,"top")])
    
    def buildTab_utilities(self,parent):
        _MainForm = parent
        
        self.uiPopUpMenu_createShape = None
        self.uiPopUpMenu_color = None
        self.uiPopUpMenu_attr = None
        self.uiPopUpMenu_raycastCreate = None
                
        try:self.var_attrCreateType
        except:self.var_attrCreateType = cgmMeta.cgmOptionVar('cgmVar_attrCreateType', defaultValue = 'float')        
        try:self.var_curveCreateType
        except:self.var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
        try:self.var_curveCreateType
        except:self.var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
        try:self.var_defaultCreateColor
        except:self.var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
        try:self.var_createAimAxis 
        except:self.var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
        try:self.var_createSizeMode 
        except:self.var_createSizeMode = cgmMeta.cgmOptionVar('cgmVar_createSizeMode', defaultValue=0)
        try:self.var_createSizeValue     
        except:self.var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)
        try:self.var_createSizeMulti     
        except:self.var_createSizeMulti = cgmMeta.cgmOptionVar('cgmVar_createSizeMultiplierValue', defaultValue=1.25)
    
        self.var_createRayCast = cgmMeta.cgmOptionVar('cgmVar_createRayCast', defaultValue = 'locator')        
        self.var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])            
        self.var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
        self.var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetMode', defaultValue=0)
        self.var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0) 
        self.var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)
        self.var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)
    
        try:
            parent(edit = True,
                   af = [(_MainForm,"top",0),
                         (_MainForm,"left",0),
                         (_MainForm,"right",0),
                         (_MainForm,"bottom",0)])
        except:pass
        #>>>Shape Creation ====================================================================================
        mc.setParent(parent)
        
    
        #>>>Tools -------------------------------------------------------------------------------------  
        #self.buildRow_context(parent)                     
        
        SNAPTOOLS.buildSection_snap(self,parent)
        cgmUI.add_HeaderBreak()        
        
        SNAPTOOLS.buildSection_aim(self,parent)
        cgmUI.add_HeaderBreak()
        
        SNAPTOOLS.buildSection_advancedSnap(self,parent)
        cgmUI.add_HeaderBreak()           
        
        #buildSection_rigging(self,parent)
        #cgmUI.add_SectionBreak()  
        
        TOOLBOX.buildSection_joint(self,parent)
        cgmUI.add_SectionBreak()          
        
        #buildSection_transform(self,parent)
        #cgmUI.add_SectionBreak()  
        
        
        TOOLBOX.buildSection_shape(self,parent)
        cgmUI.add_SectionBreak()            
        
        TOOLBOX.buildSection_color(self,parent)
        cgmUI.add_SectionBreak()  
        
        TOOLBOX.buildSection_rayCast(self,parent)
        cgmUI.add_SectionBreak()      
        
        TOOLBOX.buildSection_distance(self,parent)        
        
        

        
    def buildTab_setup(self,parent):
        _str_func = 'buildTab_setup'
        _MainForm = parent
        #_MainForm = mUI.MelScrollLayout(parent)	        
        _row_report = mUI.MelHSingleStretchLayout(_MainForm ,ut='cgmUIInstructionsTemplate',h=20)
        self.uiField_report = mUI.MelLabel(_row_report,
                                           bgc = SHARED._d_gui_state_colors.get('help'),
                                           label = '...',
                                           h=20)
        _row_report.setStretchWidget(self.uiField_report)
        cgmUI.add_Button(_row_report,'<<',
                         cgmGEN.Callback(self.uiFunc_block_setActive),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Set the active block.")
        cgmUI.add_Button(_row_report,'Clear',
                         cgmGEN.Callback(self.uiFunc_block_clearActive),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Clear the active block.")
        mUI.MelSpacer(_row_report,w=2)
        _row_report.layout()         
        
        #=======================================================================
        #>> Left Column
        #============================================================
        _LeftColumn = mUI.MelFormLayout(_MainForm)
        _scrollList = mUI.MelObjectScrollList(_LeftColumn, ut='cgmUISubTemplate',
                                              allowMultiSelection=True,en=True,
                                              dcc = cgmGEN.Callback(self.uiFunc_block_setActive),
                                              #dcc = cgmGEN.Callback(self._blockCurrent.select()),
                                              #dcc = self.uiFunc_block_select_dcc,
                                              selectCommand = self.uiScrollList_block_select,
                                              w = 200)
        #dcc = self.uiFunc_dc_fromList,
        #selectCommand = self.uiFunc_selectParent_inList)
    
                                    #dcc = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}),
        
        self.uiScrollList_blocks = _scrollList
        self._l_toEnable.append(self.uiScrollList_blocks)
        
        button_refresh = CGMUI.add_Button(_LeftColumn,'Refresh',
                                          lambda *a: self.uiUpdate_building(),
                                          'Force the scroll list to update')
        
        _LeftColumn(edit = True,
                    af = [(_scrollList,"top",0),
                          (_scrollList,"left",0),
                          (_scrollList,"right",0),
                          
                          (button_refresh,"left",0),
                          (button_refresh,"right",0),
                          (button_refresh,"bottom",0),

                          ],
                    ac = [(_scrollList,"bottom",0,button_refresh),
                          
                         ],
                    attachNone = [(button_refresh,'top')])#(_row_cgm,"top")	          
  
        
        
        _RightColumn = mUI.MelFormLayout(_MainForm)
        _RightUpperColumn = mUI.MelColumn(_RightColumn)
        _RightScroll = mUI.MelScrollLayout(_RightColumn,useTemplate = 'cgmUITemplate')
        

        #=============================================================================================
        #>> Top
        #=============================================================================================
        self.create_guiOptionVar('contextSettingsFrameCollapse',defaultValue = 0)       
            
        _frame_context = mUI.MelFrameLayout(_RightUpperColumn,label = 'Utilities - Contextual',vis=True,
                                                collapse=self.var_contextSettingsFrameCollapse.value,
                                                collapsable=True,
                                                enable=True,
                                                useTemplate = 'cgmUIHeaderTemplate',
                                                expandCommand = lambda:self.var_contextSettingsFrameCollapse.setValue(0),
                                                collapseCommand = lambda:self.var_contextSettingsFrameCollapse.setValue(1)
                                                )	
        self.uiFrame_context = _frame_context
        _frame_context_inside = mUI.MelColumnLayout(_frame_context,useTemplate = 'cgmUISubTemplate')          
        
        
        
        
        
        
        
        #mc.setParent(_RightUpperColumn)
        """
        _row = mUI.MelHLayout(_frame_context_inside)
        self.uiField_contextReport = mUI.MelLabel(_row,
                                                  ut='cgmUIHeaderTemplate',
                                                  label = '...',
                                                  h=20) 
        _row.layout()"""
        
        #Context mode  -------------------------------------------------------------------------------          
        self.create_guiOptionVar('contextMode',defaultValue = 0)       
    
        _rc_contextMode = mUI.MelRadioCollection()
        
        self._l_contextModes = ['self','below','root','scene']
        _d_ann = {'self':'Context is only of the active/sel block',
                  'below':'Context is active/sel block and below',
                  'root':'Context is active/sel root and below',
                  'scene':'Context is all blocks in the scene. Careful skippy!',}
        
        #build our sub section options
        #MelHSingleStretchLayout
        _row_contextModes = mUI.MelHSingleStretchLayout(_frame_context_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_contextModes,w=1)
        mUI.MelLabel(_row_contextModes,l = 'Context:')
        _row_contextModes.setStretchWidget( mUI.MelSeparator(_row_contextModes) )
        _on = self.var_contextMode.value
        for i,item in enumerate(self._l_contextModes):
            if i == _on:_rb = True
            else:_rb = False
            _rc_contextMode.createButton(_row_contextModes,label=self._l_contextModes[i],sl=_rb,
                                             ann = _d_ann[item],
                                             onCommand = cgmGEN.Callback(self.uiUpdate_context,
                                                                         self.var_contextMode,i))
            mUI.MelSpacer(_row_contextModes,w=2)

        _row_contextModes.layout()         
  
        #Context Start  -------------------------------------------------------------------------------          
        self.create_guiOptionVar('contextStartMode',defaultValue = 0)       
    
        _rc_contextStartMode = mUI.MelRadioCollection()
    
        self._l_contextStartModes = ['active','selected']
        _d_ann = {'active':'Context begins with active block',
                  'selected':'Context beghins with selected block in the picker on the left',}
    
        #build our sub section options
        #MelHSingleStretchLayout
        _row_contextStartModes = mUI.MelHSingleStretchLayout(_frame_context_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_contextStartModes,w=1)
        mUI.MelLabel(_row_contextStartModes,l = 'Begin with:')
        _on = self.var_contextStartMode.value
        for i,item in enumerate(self._l_contextStartModes):
            mc.button(l=self._l_contextStartModes[i],
                      ann=_d_ann[item],
                      ut='cgmUITemplate',
                      c=cgmGEN.Callback(self.uiUpdate_context,self.var_contextStartMode,i))            
            """
            if i == _on:_rb = True
            else:_rb = False
            _rc_contextStartMode.createButton(_row_contextStartModes,label=self._l_contextStartModes[i],sl=_rb,
                                              ann = _d_ann[item],
                                              onCommand = cgmGEN.Callback(self.var_contextStartMode.setValue,i))"""
            mUI.MelSpacer(_row_contextStartModes,w=2)
        
        _row_contextStartModes.setStretchWidget( mUI.MelSeparator(_row_contextStartModes) )
        
        #..force modes
        self.create_guiOptionVar('contextForceMode',defaultValue = 0)       
    
        _rc_contextForceMode = mUI.MelRadioCollection()
        
        #build our sub section options
        #MelHSingleStretchLayout
        mUI.MelSpacer(_row_contextStartModes,w=1)
        mUI.MelLabel(_row_contextStartModes,l = 'Force:')
        
        _on = self.var_contextForceMode.value
        for i,item in enumerate(['False','True']):
            mc.button(l=item,
                      ann="Force Mode: {0}".format(item),
                      ut='cgmUITemplate',
                      c=cgmGEN.Callback(self.uiUpdate_context,self.var_contextForceMode,i))
            mUI.MelSpacer(_row_contextStartModes,w=2)
            
            """
            if i == _on:_rb = True
            else:_rb = False
            _rc_contextForceMode.createButton(_row_contextStartModes,label=item,sl=_rb,
                                              ann = "Force Mode: {0}".format(item),
                                              onCommand = cgmGEN.Callback(self.var_contextForceMode.setValue,i))
            mUI.MelSpacer(_row_contextStartModes,w=2)"""
    
        _row_contextStartModes.layout()       
        
        #Push Rows  -------------------------------------------------------------------------------  
        mc.setParent(_RightUpperColumn)
        CGMUI.add_LineSubBreak()
        _row_push = mUI.MelHLayout(_RightUpperColumn,ut='cgmUISubTemplate',padding = 2)
        mc.button(l='Define>',
                  bgc = SHARED._d_gui_state_colors.get('warning'),
                  height = 20,
                  align='center',
                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,'changeState','define',**{'forceNew':True}),
                  ann='[Define] - initial block state')
        mc.button(l='<Templ>',
                  bgc = SHARED._d_gui_state_colors.get('warning'),                  
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,'changeState','template',**{'forceNew':True}),
                  ann='[Template] - Shaping the proxy and initial look at settings')
                         
        mc.button(l='<Prerig>',
                  bgc = SHARED._d_gui_state_colors.get('warning'),                  
                  height = 20,
                  align='center',
                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,'changeState','prerig',**{'forceNew':True}),
                  ann='[Prerig] - More refinded placement and setup before rig process')

        mc.button(l='<Joint>',
                  bgc = SHARED._d_gui_state_colors.get('warning'),                  
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,'changeState','skeleton',**{'forceNew':True}),
                  ann='[Joint] - Build skeleton if necessary')

        mc.button(l='<Rig',
                  bgc = SHARED._d_gui_state_colors.get('warning'),                  
                  height = 20,
                  align='center',                  
                  c=cgmGEN.Callback(self.uiFunc_contextBlockCall,'changeState','rig',**{'forceNew':True}),
                  ann='[Rig] - Push to a fully rigged state.')

        _row_push.layout()
               
        
        #Utilities Frame =====================================================================================
        log.debug("|{0}| >>  blockUtils...".format(_str_func)+ '-'*40)
        
        self.create_guiOptionVar('blockUtilsFrameCollapse',defaultValue = 0)       
    
        _frame_blockUtils = mUI.MelFrameLayout(_RightScroll,label = 'Utilities - Contextual',vis=True,
                                                collapse=self.var_blockUtilsFrameCollapse.value,
                                                collapsable=True,
                                                enable=True,
                                                useTemplate = 'cgmUIHeaderTemplate',
                                                expandCommand = lambda:self.var_blockUtilsFrameCollapse.setValue(0),
                                                collapseCommand = lambda:self.var_blockUtilsFrameCollapse.setValue(1)
                                                )	
        self.uiFrameLayout_blockUtils = _frame_blockUtils
    
        _frame_blockUtils_inside = mUI.MelColumnLayout(_frame_blockUtils,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockUtils = _frame_blockUtils_inside
        
        """
        #BlockDat Frame =====================================================================================
        log.debug("|{0}| >>  blockDat...".format(_str_func)+ '-'*40)
        
        self.create_guiOptionVar('blockDatFrameCollapse',defaultValue = 0)       
    
        _frame_blockDat = mUI.MelFrameLayout(_RightScroll,label = 'BlockDat',vis=True,
                                             collapse=self.var_blockUtilsFrameCollapse.value,
                                             collapsable=True,
                                             enable=True,
                                             useTemplate = 'cgmUIHeaderTemplate',
                                             expandCommand = lambda:self.var_blockDatFrameCollapse.setValue(0),
                                             collapseCommand = lambda:self.var_blockDatFrameCollapse.setValue(1)
                                             )	
        self.uiFrameLayout_blockDat = _frame_blockDat
        _frame_blockDat_inside = mUI.MelColumnLayout(_frame_blockDat,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockDat = _frame_blockDat_inside
        self.uiSection_blockDatUtils(_frame_blockDat_inside)"""
        
        
        #Active  Frame ------------------------------------------------------------------------------------
        log.debug("|{0}| >>  Active block frame...".format(_str_func)+ '-'*40)
        
        self.create_guiOptionVar('blockSettingsFrameCollapse',defaultValue = 0)       
    
        _frame_blockSettings = mUI.MelFrameLayout(_RightScroll,label = 'Settings - Active',vis=True,
                                                  collapse=self.var_blockSettingsFrameCollapse.value,
                                                  collapsable=True,
                                                  enable=True,
                                                  useTemplate = 'cgmUIHeaderTemplate',
                                                  expandCommand = lambda:self.var_blockSettingsFrameCollapse.setValue(0),
                                                  collapseCommand = lambda:self.var_blockSettingsFrameCollapse.setValue(1)
                                                  )	
        self.uiFrameLayout_blockSettings = _frame_blockSettings
    
        _frame_settings_inside = mUI.MelColumnLayout(_frame_blockSettings,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockSettings = _frame_settings_inside
        
        #Contextual frame ------------------------------------------------------------------------------------
        log.debug("|{0}| >>  Contextual block frame...".format(_str_func)+ '-'*40)
        
        _frame_shared = mUI.MelFrameLayout(_RightScroll,label = 'Settings - Contextual',vis=True,
                                           collapse=self.var_blockSharedFrameCollapse.value,
                                           collapsable=True,
                                           enable=True,
                                           useTemplate = 'cgmUIHeaderTemplate',
                                           expandCommand = lambda:self.var_blockSharedFrameCollapse.setValue(0),
                                           collapseCommand = lambda:self.var_blockSharedFrameCollapse.setValue(1)
                                           )	
        self.uiFrameLayout_blockShared = _frame_shared
        self.uiFrame_shared = mUI.MelColumnLayout(_frame_shared,useTemplate = 'cgmUISubTemplate')  
        self.uiUpdate_blockShared()
        self.uiUpdate_blockUtils()
        

        #Info ------------------------------------------------------------------------------------
        _frame_info = mUI.MelFrameLayout(_RightScroll,label = 'Info',vis=True,
                                        collapse=self.var_blockInfoFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_blockInfoFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_blockInfoFrameCollapse.setValue(1)
                                        )	
        self.uiFrameLayout_blockInfo = _frame_info
        
        _frame_info_inside = mUI.MelColumnLayout(_frame_info,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockInfo = _frame_info_inside
        

        """
        #Attrs ------------------------------------------------------------------------------------
        _frame_attr = mUI.MelFrameLayout(_RightColumn,label = 'Attrs',vis=True,
                                        collapse=self.var_blockAttrsFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_blockAttrsFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_blockAttrsFrameCollapse.setValue(1)
                                        )	
        self.uiFrameLayout_blockAttrs = _frame_attr
        
        _frame_attr_inside = mUI.MelColumnLayout(_frame_attr,useTemplate = 'cgmUISubTemplate')  
        self.uiFrame_blockAttrs = _frame_attr_inside"""

        _RightColumn(edit = True,
                     af = [(_RightUpperColumn,"top",0),
                           (_RightUpperColumn,"left",0),
                           (_RightUpperColumn,"right",0),
    
                           (_RightScroll,"left",0),
                           (_RightScroll,"right",0),
                           (_RightScroll,"bottom",0),
    
                           ],
                     ac = [(_RightScroll,"top",0,_RightUpperColumn),
    
                           ],)
                #attachNone = [(button_refresh,'top')])#(_row_cgm,"top")

        self.uiUpdate_context()
        
        #>>> Layout form ---------------------------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_row_report,"top",0),
                        (_row_report,"left",0),
                        (_row_report,"right",0),
                        
                        (_LeftColumn,"left",0),
                        (_RightColumn,"right",0),                        
                        (_RightColumn,"bottom",0),
                        (_LeftColumn,"bottom",0),

                        ],
                  ac = [(_LeftColumn,"top",0,_row_report),
                        (_RightColumn,"top",0,_row_report),
                        (_RightColumn,"left",0,_LeftColumn),
                        
                        #(_RightColumn,"bottom",0,_row_cgm),
                        #(_LeftColumn,"bottom",0,_row_cgm),

                        
                       ],
                  attachNone = [])#(_row_cgm,"top")	  
        
        self.uiUpdate_building()        
        
        
    def build_layoutWrapperOLD(self,parent):
        _str_func = 'build_layoutWrapper'
        self._d_uiCheckBoxes = {}
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUISubTemplate')
        
        #_header_top = cgmUI.add_Header('cgmDynParentGroup',overrideUpper=True)     
        _row_report = mUI.MelHLayout(_MainForm ,ut='cgmUIInstructionsTemplate',h=20)
        self.uiField_report = mUI.MelLabel(_row_report,
                                           bgc = SHARED._d_gui_state_colors.get('help'),
                                           label = '...',
                                           h=20)
        _row_report.layout()         
        
        #_LeftColumn = mUI.MelColumn(_MainForm,ut='cgmUISubTemplate',w=100)
        #cgmUI.add_Header('Blocks',overrideUpper=True)  
        
        _LeftColumn = mUI.MelObjectScrollList(_MainForm, #ut='cgmUISubTemplate',
                                              allowMultiSelection=False,en=True,
                                              dcc = cgmGEN.Callback(self.uiFunc_block_setActive),
                                              selectCommand = self.uiScrollList_block_select,
                                              w = 200)
        #dcc = self.uiFunc_dc_fromList,
        #selectCommand = self.uiFunc_selectParent_inList)
    
                                    #dcc = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}),
        
        self.uiScrollList_blocks = _LeftColumn
        self._l_toEnable.append(self.uiScrollList_blocks)        
        
        
        _RightColumn = mUI.MelColumnLayout(_MainForm,useTemplate = 'cgmUITemplate')
        
        cgmUI.add_Header('Inspector',overrideUpper=True)
        """
        self.uiField_inspector= mUI.MelLabel(_RightColumn,
                                             bgc = SHARED._d_gui_state_colors.get('help'),
                                             label = '...',
                                             h=20) """
        
        
        _frame_attr = mUI.MelFrameLayout(_RightColumn,label = 'Attr',vis=True,
                                        collapse=self.var_attrFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_attrFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_attrFrameCollapse.setValue(1)
                                        )	
        _frame_attr_inside = mUI.MelColumnLayout(_frame_attr,useTemplate = 'cgmUISubTemplate')     
        CGMUI.add_Button(_frame_attr_inside)
        
        #>>>CGM Row
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)
        
               
        #>>> Layout form ---------------------------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_row_report,"top",0),
                        (_row_report,"left",0),
                        (_row_report,"right",0),
                        
                        (_LeftColumn,"left",0),
                        (_RightColumn,"right",0),                        
                       
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),

                        ],
                  ac = [(_LeftColumn,"top",0,_row_report),
                        (_RightColumn,"top",0,_row_report),
                        (_RightColumn,"left",0,_LeftColumn),
                        
                        (_RightColumn,"bottom",0,_row_cgm),
                        (_LeftColumn,"bottom",0,_row_cgm),

                        
                       ],
                  attachNone = [(_row_cgm,"top")])	        
        
        self.uiUpdate_building()
        
        #_sel = mc.ls(sl=True)
        #if _sel:
            #self.uiFunc_load_selected()                

        return


            

def uiOptionMenu_blockSizeMode(self, parent, callback = cgmGEN.Callback):
    uiMenu = mc.menuItem( parent = parent, l='Create Mode:', subMenu=True)
    
    try:self.var_rigBlockCreateSizeMode
    except:self.var_rigBlockCreateSizeMode = cgmMeta.cgmOptionVar('cgmVar_rigBlockCreateSizeMode', defaultValue = 'selection')

    try:#>>>
        _str_section = 'Contextual TD mode'
        uiRC = mc.radioMenuItemCollection()
        #self.uiOptions_menuMode = []		
        _v = self.var_rigBlockCreateSizeMode.value

        for i,item in enumerate(['selection','default']):
            if item == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(parent=uiMenu,collection = uiRC,
                        label=item,
                        c = callback(self.var_rigBlockCreateSizeMode.setValue,item),                                  
                        rb = _rb)
    except Exception,err:
        log.error("|{0}| failed to load. err: {1}".format(_str_section,err))
        cgmGEN.cgmExceptCB(Exception,err)

                        
    


class uiCallback_withUpdate(object):
    '''
    '''
    def __init__( self, ui, mBlock, func, *a, **kw ):
        self._func = func
        self._args = a
        self._kwargs = kw
        self._ui = ui
        self._mBlock = mBlock
    def __call__( self, *args ):
        try:self._func( *self._args, **self._kwargs )
        except Exception,err:
            try:log.debug("Func: {0}".format(self._func.__name__))
            except:log.debug("Func: {0}".format(self._func))
            if self._ui:
                log.debug("ui: {0}".format(self._ui))
                
            if self._args:
                log.debug("args: {0}".format(self._args))
            if self._kwargs:
                log.debug("kws: {0}".format(self._kwargs))
            for a in err.args:
                log.debug(a)
                
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())
            raise Exception,err
        
        if self._mBlock == self._ui._blockCurrent:
            log.debug("|{0}| resetting active block".format('uiCallback_withUpdate'))            
            self._ui.uiFunc_block_setActive()
        else:
            self._ui.uiUpdate_building()
        self._ui.uiUpdate_building()
        
        
        