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
import os
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import maya.cmds as mc

import cgm.core.classes.GuiFactory as cgmUI
from cgm.core import cgm_RigMeta as cgmRigMeta
mUI = cgmUI.mUI

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

#>>> Root settings =============================================================
__version__ = '0.04122018 - ALPHA'
__toolname__ ='MRSAnimate'
_d_contexts = {'control':{'short':'ctrl'},
               'part':{},
               'puppet':{},
               'scene':{}}
_l_contexts = _d_contexts.keys()



class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = '{0}_ui'.format(__toolname__)    
    WINDOW_TITLE = '{1} - {0}'.format(__version__,__toolname__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 275,500
    TOOLNAME = '{0}.ui'.format(__toolname__)
    
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
        
        self.create_guiOptionVar('puppetFrameCollapse',defaultValue = 0) 
        
        self.uiMenu_snap = None
        self.uiMenu_help = None
        self._l_contexts = _l_contexts
        try:self.var_mrsContext
        except:self.var_mrsContext = cgmMeta.cgmOptionVar('cgmVar_mrsContext',
                                                          defaultValue = _l_contexts[0])
        
    def build_menus(self):
        log.debug("build menus... "+'-'*50)
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = lambda *a:self.buildMenu_first())
        self.uiMenu_switch = mUI.MelMenu( l='Switch', pmc=lambda *a:self.buildMenu_switch())                 
        self.uiMenu_snap = mUI.MelMenu( l='Snap', pmc=self.buildMenu_snap)                 
        self.uiMenu_help = mUI.MelMenu(l = 'Help', pmc = lambda *a:self.buildMenu_help()) 
        
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
        mUI.MelMenuItem( self.uiMenu_help, l="Get Call Size",
                         c=lambda *a: RIGBLOCKS.get_callSize('selection' ) )
        mUI.MelMenuItem( self.uiMenu_help, l="Gather Blocks",
                         c=lambda *a: BUILDERUTILS.gather_rigBlocks() )        
        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("https://http://docs.cgmonks.com/mrs.html");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )   
        mUI.MelMenuItem( self.uiMenu_help, l="Update Display",
                         c=lambda *a: self.uiUpdate_building() )
        
        
    def buildMenu_snap( self, force=False, *args, **kws):
        if self.uiMenu_snap and force is not True:
            return
        self.uiMenu_snap.clear()
        
        UICHUNKS.uiSection_snap(self.uiMenu_snap)
            
        mUI.MelMenuItemDiv(self.uiMenu_snap)
        
        mUI.MelMenuItem(self.uiMenu_snap, l='Rebuild',
                        c=cgmGEN.Callback(self.buildMenu_snap,True))
        log.debug("Snap menu rebuilt")
        
    def buildMenu_switch(self, *args):
        log.debug("buildMenu_switch..."+'-'*50)
        self.uiMenu_switch.clear()
        
        self._ml_objList = cgmMeta.validateObjListArg( CONTEXT.get_list(getTransform=True) )
        pprint.pprint(self._ml_objList)
        DYNPARENTTOOL.uiMenu_changeSpace(self,self.uiMenu_switch,True)

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     
    
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
        self.uiTab_setup = ui_tabs
        
        uiTab_mrs = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')
        uiTab_poses = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')
        uiTab_anim = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')        
        uiTab_settings = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')

        for i,tab in enumerate(['MRS','Poses','Anim','Settings']):
            ui_tabs.setLabel(i,tab)

        buildTab_mrs(self,uiTab_mrs)
        #buildTab_anim(self,uiTab_poses)
        reload(TOOLBOX)
        TOOLBOX.optionVarSetup_basic(self)
        TOOLBOX.buildTab_options(self,uiTab_settings)
        TOOLBOX.buildTab_anim(self,uiTab_anim)

        _row_cgm = cgmUI.add_cgmFooter(_MainForm)  
        _MainForm(edit = True,
                  af = [(ui_tabs,"top",0),
                        (ui_tabs,"left",0),
                        (ui_tabs,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),

                        ],
                  ac = [(ui_tabs,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])  
        


def buildTab_mrs(self,parent):
    _column = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
    parent(edit = True,
           af = [(_column,"top",0),
                 (_column,"left",0),
                 (_column,"right",0),                        
                 (_column,"bottom",0)])    

    mc.setParent(_column)
    
    
    #>>>Context set -------------------------------------------------------------------------------
    _row = mUI.MelHLayout(_column,ut='cgmUISubTemplate')
    
    mUI.MelSpacer(_row,w=1)                      
    #mUI.MelLabel(_row,l='Context: ')
    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    uiRC = mUI.MelRadioCollection()
    
    mVar = self.var_mrsContext
    _on = mVar.value

    for i,item in enumerate(_l_contexts):
        if item == _on:
            _rb = True
        else:_rb = False
        _label = str(_d_contexts[item].get('short',item))
        uiRC.createButton(_row,label=_label,sl=_rb,
                          onCommand = cgmGEN.Callback(mVar.setValue,item))

        mUI.MelSpacer(_row,w=1)       
    _row.layout() 
    
    
    #>>>Context Options -------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
    _d = {}
    
    mUI.MelSpacer(_row,w=5)                          
    mUI.MelLabel(_row,l='Options: ')
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    
    _d_defaults = {}
    _l_order = ['children','sibblings','mirror']
    self._dCB_contextOptions = {}
    for k in _l_order:
        _plug = 'cgmVar_mrsContext_' + k
        try:self.__dict__[_plug]
        except:
            _default = _d_defaults.get(k,0)
            #log.debug("{0}:{1}".format(_plug,_default))
            self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = _default)

        l = _d.get(k,k)
        
        _cb = mUI.MelCheckBox(_row,label=l,
                              annotation = 'Include {0} in context.'.format(k),
                              value = self.__dict__[_plug].value,
                              onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                              offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
        self._dCB_contextOptions[k] = _cb
    _row.layout()
    
    

    buildSection_MRSFunctions(self,_column)

def buildSection_MRSFunctions(self,parent):
    try:self.var_mrsFuncFrameCollapse
    except:self.create_guiOptionVar('mrsFuncFrameCollapse',defaultValue = 0)
    mVar_frame = self.var_mrsFuncFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Functions',vis=True,
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

    d_anim = {'key':{'ann':'',
                     'arg':{}}}
    
    l_anim = ['<<','key','>>','reset','delete']
    for b in l_anim:
        _d = d_anim.get(b,{})
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  en=False,
                  #c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
                  ann = _d.get('ann',b))
    _row.layout()
    
    #>>>Select -------------------------------------------------------------------------------------
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    d_select = {'select':{'ann':'Select objects in context',
                          'arg':{'mode':'select'}},
                'report':{'ann':'Report objects in context',
                          'arg':{'mode':'report'}},                
                }
    
    l_select = ['select','report']
    for b in l_select:
        _d = d_select.get(b,{})
        _arg = _d.get('arg',{})        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    _row.layout()
    
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    
    """
    mc.button(parent = _inside,
              ut = 'cgmUITemplate',
              l='Test context',
              c=lambda *a: get_context(self))
              """
    #>>>Mirror ===================================================================================== 
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    cgmUI.add_Header('Mirror')
    cgmUI.add_LineSubBreak()
    
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    d_mirror = {'<Pull':{'ann':'Select objects in context',
                          'arg':{}},
                'Push>':{'ann':'Report objects in context',
                          'arg':{}},
                }
    
    l_mirror = ['<Pull','Flip','Push>']
    for b in l_mirror:
        _d = d_mirror.get(b,{})
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  en=False,
                  ut = 'cgmUITemplate',
                  #c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
                  ann = _d.get('ann',b))
    _row.layout()
    
    
    
    #>>>Switch ===================================================================================== 
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()        
    cgmUI.add_Header('Switch')
    cgmUI.add_LineSubBreak()
    
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    d_switch = {'<Pull':{'ann':'Select objects in context',
                          'arg':{}},
                'Push>':{'ann':'Report objects in context',
                          'arg':{}},
                }
    
    l_switch = ['FKsnap','FKon','IKon','IKSnap']
    for b in l_switch:
        _d = d_switch.get(b,{})
        mc.button(parent=_row,
                  en=False,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  #c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
                  ann = _d.get('ann',b))
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
                      c=cgmGEN.Callback(uiFunc_contextSetValue,self,'puppet',n,v,_mode))
                      #c=lambda *a: LOCINATOR.ui())             
            
        mUI.MelSpacer(_row,w=2)
        _row.layout()


def buildSection_puppet(self,parent):
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
                      c=cgmGEN.Callback(uiFunc_contextSetValue,self,'puppet',n,v,_mode))
                      #c=lambda *a: LOCINATOR.ui())             
            
        mUI.MelSpacer(_row,w=2)
        _row.layout()
    
    """
    #puppet settings ===========================================================================
    mmPuppetSettingsMenu = mc.menuItem(p = parent, l='Settings', subMenu=True)
    mmPuppetControlSettings = mPuppet.masterControl.controlSettings 
    
    for attr in ['visSub','visDirect','visRoot']:
        mi_tmpMenu = mc.menuItem(p = mmPuppetSettingsMenu, l=attr, subMenu=True)
        
        mc.menuItem(p = mi_tmpMenu, l="Show",
                    c = cgmGen.Callback(mPuppet.atUtils,'modules_settings_set',**{attr:1}))                    
        mc.menuItem(p = mi_tmpMenu, l="Hide",
                    c = cgmGen.Callback(mPuppet.atUtils,'modules_settings_set',**{attr:0}))
        
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
                                               c = cgmGen.Callback(mc.setAttr,"%s"%mi_attr.p_combinedName,i),
                                               rb = b_state )    
    """

def get_context(self):
    _str_func='get_context'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    
    b_children = bool(self.cgmVar_mrsContext_children.value)
    b_sibblings = bool(self.cgmVar_mrsContext_sibblings.value)
    b_mirror = bool(self.cgmVar_mrsContext_mirror.value)
    context = self.var_mrsContext.value
    
    log.debug("|{0}| >> context: {1} | children: {2} | sibblings: {3} | mirror: {4}".format(_str_func,context,b_children,b_sibblings,b_mirror))
    
    #>>  Individual objects....  ============================================================================
    ml_sel = cgmMeta.asMeta(mc.ls(sl=True))
    self._sel = ml_sel
    self.d_puppetData = {'mControls':[],
                         'mPuppets':[],
                         'mModules':[]}
    
    res = []
    
    #------------------------------------------------------
    for i,mObj in enumerate(ml_sel):
        log.debug("|{0}| >> First pass check: {1}".format(_str_func,mObj))  
        
        #>>> Module --------------------------------------------------------------------------
        if mObj.getMessage('rigNull'):
            if mObj not in self.d_puppetData['mControls']:
                self.d_puppetData['mControls'].append(mObj)
                if context == 'control':
                    res.append(mObj)


            mRigNull = mObj.rigNull
            mModule = mRigNull.module
            
            if mModule not in self.d_puppetData['mModules']:
                self.d_puppetData['mModules'].append(mModule)
                if context == 'part':
                    res.append(mModule)
            
            if mModule.getMessage('modulePuppet'):
                mPuppet = mModule.modulePuppet
                if mPuppet not in self.d_puppetData['mPuppets']:
                    self.d_puppetData['mPuppets'].append(mPuppet)
                    if context == 'puppet':
                        res.append(mPuppet)


    if b_sibblings:

        log.debug(cgmGEN._str_subLine)        
        log.debug("|{0}| >> sibbling check...".format(_str_func))
        if context == 'part':
            print(cgmGEN._str_hardBreak)        
            log.warning(cgmGEN._str_hardBreak)        
            log.warning("|{0}| >> JOSH ... part Sibblings won't work right until you tag build profile for matching ".format(_str_func))
            log.warning(cgmGEN._str_hardBreak)        
            print(cgmGEN._str_hardBreak)                    
            
            res = []
            for mModule in self.d_puppetData['mModules']:
                log.debug("|{0}| >> sibbling check: {1}".format(_str_func,mModule))
                mModuleParent  = mModule.getMessage('moduleParent',asMeta=True)
                log.debug("|{0}| >> ModuleParent: {1}".format(_str_func,mModuleParent))
                if mModuleParent:
                    ml_children = mModuleParent[0].atUtils('moduleChildren_get')
                    for mChild in ml_children:
                        if mChild.getMessage('moduleParent',asMeta=True) == mModuleParent:
                            if mChild not in res:
                                res.append(mChild)
                            
            self.d_puppetData['mModules'] = res#...push new data back
            
        elif context == 'control':
            res = []
            for mModule in self.d_puppetData['mModules']:
                log.debug("|{0}| >> sibbling gathering for control | {1}".format(_str_func,mModule))
                res.extend(mModule.rigNull.msgList_get("controlsAll"))
            
                
    if b_children:
        log.debug(cgmGEN._str_subLine)        
        log.debug("|{0}| >> Children check...".format(_str_func))
        
        if context == 'part':
            for mModule in self.d_puppetData['mModules']:
                log.debug("|{0}| >> child check: {1}".format(_str_func,mModule))
                ml_children = mModule.atUtils('moduleChildren_get')
                for mChild in ml_children:
                    if mChild not in res:
                        res.append(mChild)
            self.d_puppetData['mModules'] = res

            
        elif context == 'puppet':
            log.warning('Puppet context with children is [parts] contextually. Changing for remainder of query.')
            context = 'part'
            res = []
            for mPuppet in self.d_puppetData['mPuppets']:
                res.extend(mPuppet.atUtils('modules_get'))
                
    
    if b_mirror:
        log.debug(cgmGEN._str_subLine)        
        log.debug("|{0}| >> Mirror check...".format(_str_func))
        
        if context == 'control':
            for mModule in self.d_puppetData['mModules']:
                mMirror = mModule.atUtils('mirror_get')
                if mMirror:
                    log.debug("|{0}| >> Mirror: {1}".format(_str_func,mMirror))                    
                    ml_mirrorControls = mMirror.rigNull.msgList_get('controlsAll')
                    for mControl in self.d_puppetData['mControls']:
                        if not mControl.hasAttr('mirrorIndex'):
                            log.debug("|{0}| >> Missing mirrorIndex: {1}".format(_str_func,mControl))
                            break
                        _idx = mControl.mirrorIndex
                        for mControlMirrorOption in ml_mirrorControls:
                            if mControlMirrorOption.hasAttr('mirrorIndex'):
                                if mControlMirrorOption.mirrorIndex == _idx:
                                    log.debug("|{0}| >> Match: {1}".format(_str_func,mControlMirrorOption))
                                    res.append(mControlMirrorOption)
        elif context == 'part':
            for mModule in self.d_puppetData['mModules']:
                mMirror = mModule.atUtils('mirror_get')
                if mMirror:
                    log.debug("|{0}| >> Mirror: {1}".format(_str_func,mMirror))
                    if mMirror not in res:
                        res.append(mMirror)
                    

    if context == 'scene':
        return self.d_puppetData['mPuppets']
    pprint.pprint(self.d_puppetData)
    return res


def uiFunc_contextualAction(self, **kws):
    _str_func='uiFunc_contextualAction'
    l_kws = []
    for k,v in kws.iteritems():
        l_kws.append("{0}:{1}".format(k,v))
    
    _mode = kws.get('mode',False)
    _context = self.var_mrsContext.value
    log.debug("|{0}| >> context: {1} | {2}".format(_str_func,_context,' | '.join(l_kws)))
    res_context = get_context(self)
    
    if _mode == 'report':
        log.info("Context: {0} ".format(_context))
        for i,v in enumerate(res_context):
            log.info("[{0}] : {1}".format(i,v))
        log.debug(cgmGEN._str_subLine)
    elif _mode == 'select':
        if _context == 'control':
            return mc.select([mObj.mNode for mObj in res_context])
        if _context == 'part':
            _ls = []
            for mPart in res_context:
                _ls.extend(mPart.rigNull.moduleSet.getList())
            return mc.select(_ls)
        if _context == 'puppet':
            for mPuppet in self.d_puppetData['mPuppets']:
                mPuppet.puppetSet.select()
                
    else:
        return log.error("Unknown contextual action: {0}".format(_mode))
    return 


def uiFunc_contextSetValue(self, context = 'puppet',attr=None,value=None, mode = None):
    _str_func='uiFunc_settingsSet'
    log.debug("|{0}| >>  context: {1} | attr: {2} | value: {3} | mode: {4}".format(_str_func,mode,attr,value,mode)+ '-'*80)
    
    d_context = get_context(self)
    
    if context == 'puppet':
        if not d_context.get('mPuppets'):
            return log.error("No puppets found in context")
        
        for mPuppet in d_context['mPuppets']:
            log.debug("|{0}| >>  On: {1}".format(_str_func,mPuppet))
            
            if mode == 'moduleSettings':
                mPuppet.atUtils('modules_settings_set',**{attr:value})
                #mPuppet.UTILS.module_settings_set(mPuppet,**{attr,value})
            elif mode == 'puppetSettings':
                ATTR.set(mPuppet.masterControl.controlSettings.mNode, attr, value)
        
    
    
    

def buildColumn_main(self,parent, asScroll = False):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """   
    if asScroll:
        _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUISubTemplate') 
    else:
        _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
    
    #buildSection_puppet(self,_inside)
    buildSection_MRSFunctions(self,_inside)
    
    return _inside
    
def uiFunc_load_selected(self, bypassAttrCheck = False):
    _str_func = 'uiFunc_load_selected'  
    #self._ml_ = []
    self._mTransformTarget = False

    _sel = mc.ls(sl=True,type='transform')

    #Get our raw data
    if _sel:
        mNode = cgmMeta.validateObjArg(_sel[0])
        _short = mNode.p_nameBase            
        log.debug("|{0}| >> Target: {1}".format(_str_func, _short))
        self._mTransformTarget = mNode

        uiFunc_updateTargetDisplay(self)
    else:
        log.warning("|{0}| >> Nothing selected.".format(_str_func))            
        uiFunc_clear_loaded(self)

    #uiFunc_updateFields(self)
    #self.uiReport_do()
    #self.uiFunc_updateScrollAttrList()

def uiFunc_clear_loaded(self):
    _str_func = 'uiFunc_clear_loaded'  
    self._mTransformTarget = False
    self.uiTF_objLoad(edit=True, l='',en=False)      


     
def uiFunc_updateTargetDisplay(self):
    _str_func = 'uiFunc_updateTargetDisplay'  
    #self.uiScrollList_parents.clear()

    if not self._mTransformTarget:
        log.info("|{0}| >> No target.".format(_str_func))                        
        #No obj
        self.uiTF_objLoad(edit=True, l='',en=False)
        self._mGroup = False

        #for o in self._l_toEnable:
            #o(e=True, en=False)
        return
    
    _short = self._mTransformTarget.p_nameBase
    self.uiTF_objLoad(edit=True, ann=_short)
    
    if len(_short)>20:
        _short = _short[:20]+"..."
    self.uiTF_objLoad(edit=True, l=_short)   
    
    self.uiTF_objLoad(edit=True, en=True)
    
    return


 