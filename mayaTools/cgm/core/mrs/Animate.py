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

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = '{0}_ui'.format(__toolname__)    
    WINDOW_TITLE = '{1} - {0}'.format(__version__,__toolname__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 300,350
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

    #>>>Shape Creation ====================================================================================
    mc.setParent(_column)
    
    mc.button(parent = _column,
              ut = 'cgmUITemplate',
              l='Test context',
              c=lambda *a: get_context(self))    
    
    
    #>>>Key snap -------------------------------------------------------------------------------------    
    mc.setParent(_column)
    
    _row = mUI.MelHLayout(_column,ut='cgmUISubTemplate',padding=1)


    mc.button(parent=_row,
              l = '<<',
              ut = 'cgmUITemplate',                                    
              #c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
              ann = "Aim snap in a from:to selection")

    mc.button(parent=_row,
              l = 'Key',
              ut = 'cgmUITemplate',                                    
              #c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
              ann = "Aim snap in a from:to selection")

    mc.button(parent=_row,
              l = '>>',
              ut = 'cgmUITemplate',                                    
              #c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
              ann = "Aim snap in a from:to selection")


    mc.button(parent=_row,
              l = 'Breakdown',
              ut = 'cgmUITemplate',                                    
              #c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
              ann = "Aim snap in a from:to selection")

    mc.button(parent=_row,
              l = 'Reset',
              ut = 'cgmUITemplate',                                    
              #c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
              ann = "Aim snap in a from:to selection")    

    _row.layout()       
    
    
    
    buildSection_puppet(self,_column)


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
    
    #>>  Individual objects....  ============================================================================
    ml_sel = cgmMeta.asMeta(mc.ls(sl=True))
    self._sel = ml_sel
    self.d_puppetData = {'mControls':[],
                         'mPuppets':[],
                         'mModules':[]}
    
    #------------------------------------------------------
    for i,mObj in enumerate(ml_sel):
        log.debug("|{0}| >> checking: {1}".format(_str_func,mObj))  
        
        #>>> Module --------------------------------------------------------------------------
        if mObj.getMessage('rigNull'):
            
            if mObj not in self.d_puppetData['mControls']:
                self.d_puppetData['mControls'].append(mObj)                            
            
            mRigNull = mObj.rigNull
            
            mModule = mRigNull.module
            if mModule not in self.d_puppetData['mModules']:
                self.d_puppetData['mModules'].append(mModule)
            
            if mModule.getMessage('modulePuppet'):
                mPuppet = mModule.modulePuppet
                
                if mPuppet not in self.d_puppetData['mPuppets']:
                    self.d_puppetData['mPuppets'].append(mPuppet)                
                    
    log.debug(cgmGEN._str_subLine)
    pprint.pprint(self.d_puppetData)
    return self.d_puppetData
    
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
    
    buildSection_puppet(self,_inside)
    
    
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


 