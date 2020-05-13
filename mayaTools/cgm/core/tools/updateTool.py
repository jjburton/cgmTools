"""
------------------------------------------
updateTool: cgm.core.tools
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
import os
import datetime

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import maya.cmds as mc

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

from cgm.core.lib import shared_data as SHARED
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
import cgm.core.cgm_Meta as cgmMeta
from cgm.core.cgmPy import path_Utils as CGMPATH
import cgmUpdate
#reload(cgmUpdate)

#>>> Root settings =============================================================
__version__ = '1.03042019'
__toolname__ ='cgmUpdate'
_commit_limit = 12
_l_branches = ['stable','master','MRS','MRSDEV','MRSWORKSHOP','MRSWORKSHOPDEV']

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = '{0}_ui'.format(__toolname__)    
    WINDOW_TITLE = '{1} - {0}'.format(__version__,__toolname__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 425,350
    TOOLNAME = '{0}.ui'.format(__toolname__)
    
    def insert_init(self,*args,**kws):
        _str_func = '__init__[{0}]'.format(self.__class__.TOOLNAME)            
        log.info("|{0}| >>...".format(_str_func))        

        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        log.info(self.__call__(q=True, title=True))

        self.__version__ = __version__
        self.__toolName__ = self.__class__.WINDOW_NAME	

        self.WINDOW_TITLE = self.__class__.WINDOW_TITLE
        self.DEFAULT_SIZE = self.__class__.DEFAULT_SIZE

 
    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))
        #self.uiMenu_Buffers = mUI.MelMenu( l='Buffers', pmc = lambda *a:UICHUNKS.uiOptionMenu_buffers(self,False))
        self.uiMenu_Help = mUI.MelMenu(l = 'Help', pmc = lambda *a:self.buildMenu_help())

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     

        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        
    def buildMenu_help(self):
        self.uiMenu_Help.clear()
        cgmUI.uiSection_help(self.uiMenu_Help)
        
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        #self._d_uiCheckBoxes = {}
    
        #_MainForm = mUI.MelFormLayout(parent,ut='cgmUISubTemplate')
        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        _column = buildColumn_main(self,_MainForm,False)
        
        
        self.uiScroll_commits = mUI.MelScrollLayout(_MainForm,bgc=[.5,.5,.5])
        #for v in range(50):
            #mUI.MelLabel(self.uiFrame_commits, l=v)
        self.uiUpdate_commits()
            
        _row_buttons = buildRow_commitButtons(self,_MainForm)
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)
                
        _MainForm(edit = True,
                  af = [(_column,"top",0),
                        (_column,"left",0),
                        (_column,"right",0),                        
                        (_row_buttons,"left",0),
                        (_row_buttons,"right",0),
                        (self.uiScroll_commits,"left",0),
                        (self.uiScroll_commits,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(self.uiScroll_commits,"top",2,_column),                        
                        (self.uiScroll_commits,"bottom",5,_row_buttons),
                        (_row_buttons,"bottom",2,_row_cgm)
                        ],
                  attachNone = [(_row_buttons,"top")])
        
    def uiFunc_checkForUpdates(self):
        _str_func = 'uiFunc_checkForUpdates'
        log.debug("|{0}| >> ...".format(_str_func))
        
        
        try:self.var_lastUpdate
        except:self.var_lastUpdate = cgmMeta.cgmOptionVar('cgmVar_branchLastUpdate', defaultValue = [''])
        
        _lastUpdate = self.var_lastUpdate.getValue()
        self.var_lastUpdate.report()
        if _lastUpdate == 'None':
            return log.error("No last update found. Can't check for updates")
        
        try:_lastBranch = _lastUpdate[0]
        except:_lastBranch = 'MRS'
        
        try:_lastHash = _lastUpdate[1]
        except:_lastHash = None
        try:_lastMsg = _lastUpdate[2]
        except:_lastMsg = None
        try:_lastDate = _lastUpdate[3]
        except:_lastDate = None
        
        #Get our dat from the server
        _d_serverDat = cgmUpdate.get_dat(_lastBranch,1,True)
        _targetHash = _d_serverDat[0].get('hash')
        _targetMsg = _d_serverDat[0].get('msg')
        _targetDate = _d_serverDat[0].get('date')
        
        if _d_serverDat[0]['hash'] == _lastHash:
            return log.info("No update necessary. Branch [{0}] Up to date! Hash: [{1}]".format(_lastBranch,_lastHash))
        
        result = mc.confirmDialog(title="Update your local cgmTools...",
                                 message='Are you sure you want to get and update to build: \n Last update: {4} \n Target: [{0}] | [{1}] \n Last: [{2}] | [{3}]'.format(_lastBranch,_targetHash,_lastBranch,_lastHash,_lastDate),
                                 messageAlign='center',
                                 button=['OK', 'Cancel'],
                                 #text = self.value,
                                 defaultButton='OK',
                                 cancelButton='Cancel',
                                 dismissString='Cancel')
        
        if result == 'OK':
            log.debug("|{0}| >> go!".format(_str_func))
            
            try:
                cgmUpdate.here(_lastBranch,0)

                try:self.var_lastUpdate
                except:self.var_lastUpdate = cgmMeta.cgmOptionVar('cgmVar_branchLastUpdate', defaultValue = ['None'])                
                self.var_lastUpdate.setValue([_lastBranch,_targetHash,_targetMsg,
                                              datetime.datetime.now().__str__()[:-7]
                                              ])
                
                self.uiUpdate_topReport()
                
            except Exception,err:
                print err
            finally:pass
        else:
            return log.error("|{0}| update cancelled".format(_str_func))
        
    def uiUpdate_topReport(self):
        try:self.var_lastUpdate
        except:self.var_lastUpdate = cgmMeta.cgmOptionVar('cgmVar_branchLastUpdate', defaultValue = [''])
        
        _lastUpdate = self.var_lastUpdate.getValue()
        self.var_lastUpdate.report()
        if _lastUpdate == 'None':
            self.uiField_report(edit=True, label='No last update data found...')
            return log.error("No last update found.")
        else:
            try:_lastBranch = _lastUpdate[0]
            except:_lastBranch = None
            try:_lastHash = _lastUpdate[1]
            except:_lastHash = None
            try:_lastMsg = _lastUpdate[2]
            except:_lastMsg = None
            try:_lastDate = _lastUpdate[3]
            except:_lastDate = None
            
            self.uiField_report(edit = True,
                                label = "Last update: [{0}] - {1}".format(_lastBranch,
                                                                           _lastDate,
                                                                           _lastHash),
                                ann = _lastMsg,
                                )
             
    def uiFunc_updateMyStuff(self):
        _str_func = 'uiFunc_updateMyStuff'
        log.debug("|{0}| >> ...".format(_str_func))
        
        if self.uiRC_commits.getSelectedIndex() == None:
            return log.error("No commit selected.")
        
        try:self.var_lastUpdate
        except:self.var_lastUpdate = cgmMeta.cgmOptionVar('cgmVar_branchLastUpdate', defaultValue = ['None'])
        
        _branch = self.var_branchMode.value
        _idx = self.uiRC_commits.getSelectedIndex()
        _d = self.dat_commits[_idx]
        _hash = _d['hash']
        _msg = _d['msg']
        _lastBranch = None
        _lastHash = None
        
        _lastUpdate = self.var_lastUpdate.getValue() or None
        
        if _lastUpdate and _lastUpdate[0] != 'None':
            try:_lastBranch = _lastUpdate[0] 
            except:pass
            try:_lastHash = _lastUpdate[1]
            except:pass
            try:_lastMsg = _lastUpdate[2]
            except:pass
            try:_lastDate = _lastUpdate[3]
            except:_lastDate = None
            
        result = mc.confirmDialog(title="Update your local cgmTools...",
                                 message='Are you sure you want to get and update to build? \n Last update: {4} \n Selected: [{0}] | [{1}] \n Last: [{2}] | [{3}]'.format(_branch,
                                                                                                                                                      _hash,
                                                                                                                                              
                                                                                                                                              _lastBranch,
                                                                                                                                              _lastHash,
                                                                                                                                              _lastDate),
                                 messageAlign='center',
                                 button=['OK', 'Cancel'],
                                 #text = self.value,
                                 defaultButton='OK',
                                 cancelButton='Cancel',
                                 dismissString='Cancel')
        
        if result == 'OK':
            log.debug("|{0}| >> go!".format(_str_func))
            
            try:
                cgmUpdate.here(_branch,_idx)
                
                self.var_lastUpdate.setValue([_branch,
                                              _hash,
                                              _msg,datetime.datetime.now().__str__()[:-7]])
                

                
                self.uiUpdate_topReport()
            except Exception,err:
                pprint.pprint(vars())
            finally:pass
        else:
            return log.error("|{0}| update cancelled".format(_str_func))
        
        
    def uiUpdate_commits(self):
        self.uiScroll_commits.clear()
        #_d_ui_annotations = {}
    
        _sidePadding = 25
        _parent = self.uiScroll_commits
        _branch = self.var_branchMode.value
        _dat = cgmUpdate.get_dat(_branch,_commit_limit,True)
        
        uiRC = mUI.MelRadioCollection()
        self.uiRC_commits = uiRC
        self.dat_commits = _dat
        
        for i,d in enumerate(_dat):
            _hash = d['hash']
            _msg = d['msg']
            _date = d['date']
            _url = d['url']
            
            _ann = '\n {0} commit {1} | {2} | {3} \n {4} \n {5}'.format(_branch, i, _hash, _date, _msg, _url)
            _report = '{0} | {1}'.format(_hash, _msg[:50])
            _label = "{0} - {1} | {3}...".format(i,_date, _hash[:8],_msg[:40])
            #log.debug(_report)
            #cgmUI.mUI.MelLabel(_parent, l = _msg,
            #                   annotation = d['msg'])
            
            #mc.separator(parent = _parent, height = 5,
                         #ut='cgmUISubTemplate'
            #             )
            cgmUI.mUI.MelSpacer(_parent, h=5)
            uiRC.createButton(_parent,label=_label,
                              annotation = _ann,
                              onCommand = cgmGEN.Callback(log.info,_ann),
                              #ut='cgmUIHeader',
                              #onCommand = lambda*a:(log.info("{0} | {1} | {2}".format(uiRC.getSelectedIndex(), _branch, self.dat_commits[uiRC.getSelectedIndex()]['hash'])))
                              #sl=_rb,
                              #onCommand = cgmGEN.Callback(_var.setValue,i)
                              )
            mc.setParent(_parent)
            cgmUI.add_LineSubBreak()

        

def buildRow_commitButtons(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)

    cgmUI.add_Button(_row,'Check for updates',
                     lambda *a:(self.uiFunc_checkForUpdates()),
                     "Check your last branch pull for updates"
                     )
    cgmUI.add_Button(_row,'Get Selected',
                     lambda *a:(self.uiFunc_updateMyStuff()),
                    )    
    _row.layout() 
    return _row

def buildRow_branches(self,parent):
    """
    try:self.var_matchModeMove
    except:self.var_matchModeMove = cgmMeta.cgmOptionVar('cgmVar_matchModeMove', defaultValue = 1)
    try:self.var_matchModeRotate
    except:self.var_matchModeRotate = cgmMeta.cgmOptionVar('cgmVar_matchModeRotate', defaultValue = 1)
    try:self.var_matchMode
    except:self.var_matchMode = cgmMeta.cgmOptionVar('cgmVar_matchMode', defaultValue = 2)
    """
    try:self.var_branchMode
    except:self.var_branchMode = cgmMeta.cgmOptionVar('cgmVar_branchUpdateMode', defaultValue = 'master')
    
    #>>>Branch -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)
    mUI.MelLabel(_row,l='Choose which branch you want to use:')
    
    #>>>Settings -------------------------------------------------------------------------------------
    

    #cc = Callback(puppetBoxLib.uiModuleOptionMenuSet,self,self.moduleDirectionMenus,self.moduleDirections,'cgmDirection',i)
    self.uiSelector_branch = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
    
    for a in _l_branches:
        self.uiSelector_branch.append(a)
      
    
    self.uiSelector_branch(edit=True,
                             value = self.var_branchMode.getValue(),
                             cc = lambda*a:uiFunc_branchChange(self, self.var_branchMode, self.uiSelector_branch)
                             #cc = cgmGEN.Callback(self.set_optionVar, self.var_branchMode, None,
                             #                     self.uiSelector_branch)
                             )    
                             
    _row.setStretchWidget( self.uiSelector_branch )
    mUI.MelSpacer(_row,w=5)

    _row.layout()

def uiFunc_setLastUpdateDebug(branch = 'MRS',clear=False):
    var_lastUpdate = cgmMeta.cgmOptionVar('cgmVar_branchLastUpdate', defaultValue = ['None'])
    if clear:
        var_lastUpdate.setValue(['None'])
        var_lastUpdate.report()
        return
    d_branch = cgmUpdate.get_dat(branch,1,True)
    var_lastUpdate.setValue([branch,
                             d_branch[0]['hash'],
                             d_branch[0]['msg'],
                             datetime.datetime.now().__str__()[:-7]])
    
def uiFunc_branchChange(self, varMode, uiSelector):
    self.set_optionVar(varMode, None,uiSelector)
    self.uiUpdate_commits()

def buildColumn_main(self,parent, asScroll = False):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """   
    if asScroll:
        _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
    else:
        _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUITemplate') 
    
    #>>>Match mode ============================================================================
    _row = mUI.MelHLayout(_inside ,ut='cgmUIInstructionsTemplate',h=20)

    #mUI.MelSpacer(_row,w=5)                      
    #mUI.MelLabel(_row,l='Last build:')
    
    self.uiField_report = mUI.MelLabel(_row,
                                       bgc = SHARED._d_gui_state_colors.get('help'),
                                       label = 'No last update data found...',
                                       h=20)

    
    #_row.setStretchWidget( self.mLabel_report )
    #mUI.MelSpacer(_row,w=5)                      

    _row.layout()          
    #buildSection_snap(self, _inside)
    #buildSection_aim(self,_inside)
    
    buildRow_branches(self,_inside)
    
    self.uiUpdate_topReport()
    return _inside



#>>> Core functions =====================================================================================
def checkBranch():
    """
    Standalone update call
    """
    _str_func = 'checkBranch'
    log.debug("|{0}| >> ...".format(_str_func))
    
    try:var_lastUpdate
    except:var_lastUpdate = cgmMeta.cgmOptionVar('cgmVar_branchLastUpdate', defaultValue = [''])
    
    _lastUpdate = var_lastUpdate.getValue()
    var_lastUpdate.report()
    if _lastUpdate == 'None':
        return log.error("No last update found. Can't check for updates")
    
    _lastBranch = _lastUpdate[0]
    
    try:_lastHash = _lastUpdate[1]
    except:_lastHash = None
    try:_lastMsg = _lastUpdate[2]
    except:_lastMsg = None
    try:_lastDate = _lastUpdate[3]
    except:_lastDate = None
    
    #Get our dat from the server
    _d_serverDat = cgmUpdate.get_dat(_lastBranch,1,True)
    _targetHash = _d_serverDat[0].get('hash')
    _targetMsg = _d_serverDat[0].get('msg')
    _targetDate = _d_serverDat[0].get('date')
    
    if _d_serverDat[0]['hash'] == _lastHash:
        return log.info("No update necessary. Branch [{0}] Up to date! Last update: {2} | Hash: [{1}]".format(_lastBranch,_lastHash,_lastDate))
    
    result = mc.confirmDialog(title="Update your local cgmTools...",
                             message='Are you sure you want to get and update to build: \n Last update: {0} \n [{1}] | [{2}] \n \n {3} \n \n Target updated: {4} \n [{1}] | [{5}] \n \n {6}'.format(_lastDate, _lastBranch, _lastHash,_lastMsg,_targetDate,_targetHash, _targetMsg),
                             messageAlign='center',
                             button=['OK', 'Cancel'],
                             #text = self.value,
                             defaultButton='OK',
                             cancelButton='Cancel',
                             dismissString='Cancel')
    
    if result == 'OK':
        log.debug("|{0}| >> go!".format(_str_func))
        
        try:
            cgmUpdate.here(_branch,0)
            var_lastUpdate.setValue([_branch,
                                     _targetHash,
                                     _targetMsg,datetime.datetime.now().__str__()[:-7]])
        except Exception,err:
            print err
        finally:pass
    else:
        return log.error("|{0}| update cancelled".format(_str_func))