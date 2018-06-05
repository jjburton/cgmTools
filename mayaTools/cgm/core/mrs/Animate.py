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
import maya.mel as mel

from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

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
import cgm.core.lib.search_utils as SEARCH
import cgm.core.lib.list_utils as LISTS

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
__version__ = '1.05222018 - ALPHA'
__toolname__ ='MRSAnimate'
_d_contexts = {'control':{'short':'ctrl'},
               'part':{},
               'puppet':{},
               'scene':{}}
_l_contexts = _d_contexts.keys()

_subLineBGC = [.75,.75,.75]


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
        self._sel = None
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
        
        _mDev = mUI.MelMenuItem(self.uiMenu_FirstMenu, l="Dev",subMenu=True)
        mUI.MelMenuItem(_mDev, l="Puppet - Mirror verify",
                        ann = "Please don't mess with this if you don't know what you're doing ",
                        c = cgmGEN.Callback(uiFunc_contextualAction,self,**{'mode':'mirrorVerify','context':'puppet'}))
        mUI.MelMenuItem(_mDev, l="Puppet - Up to date?",
                        ann = "Please don't mess with this if you don't know what you're doing ",
                        c = cgmGEN.Callback(uiFunc_contextualAction,self,**{'mode':'upToDate','context':'puppet'}))
        
    
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
    _row = mUI.MelHLayout(_column,ut='cgmUISubTemplate',padding=10)
    
    #mUI.MelSpacer(_row,w=1)                      
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

        #mUI.MelSpacer(_row,w=1)       
    _row.layout() 
    
    
    #>>>Context Options -------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
    _d = {}
    
    mUI.MelSpacer(_row,w=5)                          
    mUI.MelLabel(_row,l='Options: ')
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    
    _d_defaults = {}
    _l_order = ['children','siblings','mirror']
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
    
    buildSection_mrsAnim(self,_column)
    buildSection_mrsTween(self,_column)
    buildSection_mrsHold(self,_column)        
    buildSection_mrsMirror(self,_column)
    buildSection_mrsSwitch(self,_column)
    buildSection_mrsSettings(self,_column)
    

def buildSection_mrsAnim(self,parent):
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
                     'arg':{'mode':'delete'},},
              'report':{'ann':'Report objects in context',
                        'arg':{'mode':'report'}},              
              }
    
    l_anim = ['<<','key','bKey','>>','delete','report']
    for b in l_anim:
        _d = d_anim.get(b,{})
        _arg = _d.get('arg',{'mode':b})
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  en = _d.get('en',True),
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
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
                      c=cgmGEN.Callback(uiFunc_contextSetValue,self,n,v,_mode))
                      #c=lambda *a: LOCINATOR.ui())             
            
        mUI.MelSpacer(_row,w=2)
        _row.layout()
        

def buildSection_mrsHold(self,parent):
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
                             'arg':{'mode':'holdNext'}},}
    
    l_hold = ['holdCurrent','holdAverage','holdPrev','holdNext']
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    
    for i,b in enumerate(l_hold):
        _d = d_hold.get(b,{})
        _arg = _d.get('arg',{'mode':b})
        
        mc.button(parent=_row,
                  l = _d.get('short',b),
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
        if i == 1:#New row
            _row.layout()
            _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
            
    _row.layout()

def buildSection_mrsMirror(self,parent):
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
        if i == 2:#New row
            _row.layout()
            _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
            
    _row.layout()

def buildSection_mrsTween(self,parent):
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
    self.uiFF_relax = mUI.MelFloatField(_uiRow_relax, w = 50, value = .2,
                                        #cc = lambda *a: self.uiSlider_relax.setValue(self.uiFF_relax.getValue()),
                                        )"""

    self.uiSlider_reset = mUI.MelFloatSlider(_uiRow_reset, 0, 1.0, defaultValue=0, 
                                             #bgc = cgmUI.guiBackgroundColor,
                                             value = 0,
                                             cc = lambda *a: uiFunc_resetSlider(self))
                                             #cc = lambda *a: self.uiFF_relax.setValue(self.uiSlider_relax.getValue()),
                                             #dragCommand = lambda *a: log.info(self.uiSlider_relax.getValue()),
                                             
    self.uiSlider_reset.setPostChangeCB(cgmGEN.Callback(uiFunc_resetSliderDrop,self))
    
    mUI.MelSpacer(_uiRow_reset, w = 1)
    """
    mc.button(parent=_uiRow_relax ,
              ut = 'cgmUITemplate',
              l = 'R',
              c = lambda *a: self.uiSlider_relax.reset(),
              ann = "Reset relaxer")
    """
    mUI.MelSpacer(_uiRow_reset, w = 2)
    _uiRow_reset.setStretchWidget(self.uiSlider_reset)
    _uiRow_reset.layout() 
    
    #>>>Tween ===================================================================================== 
    cgmUI.add_LineSubBreak()
    
    _uiRow_tween = mUI.MelHSingleStretchLayout(_inside, height = 27)

    mUI.MelSpacer(_uiRow_tween, w = 2)
    mUI.MelLabel(_uiRow_tween,l='Tween')

    self.uiSlider_tween = mUI.MelFloatSlider(_uiRow_tween, -1.5, 1.5, defaultValue=0, 
                                             #bgc = cgmUI.guiBackgroundColor,
                                             value = 0,
                                             cc = lambda *a: uiFunc_tweenSlider(self))
                                             
    self.uiSlider_tween.setPostChangeCB(cgmGEN.Callback(uiFunc_tweenSliderDrop,self))
    cgmUI.add_Button(_uiRow_tween,'Drag',
                     cgmGEN.Callback(uiFunc_contextualAction,self,**d_tween['tweenDrag']['arg']),
                     d_tween['tweenDrag']['ann'])        
    
    mUI.MelSpacer(_uiRow_tween, w = 1)
    """
    mc.button(parent=_uiRow_tween ,
              ut = 'cgmUITemplate',
              l = 'R',
              c = lambda *a: self.uiSlider_tween.reset(),
              ann = "Reset tweener")
    """
    mUI.MelSpacer(_uiRow_tween, w = 2)
    _uiRow_tween.setStretchWidget(self.uiSlider_tween)
    _uiRow_tween.layout() 
    
    
    #Amount slider ------------------------------------------------------------------------------------
    _uiRow_twnAmount = mUI.MelHSingleStretchLayout(_inside, height = 27)

    mUI.MelSpacer(_uiRow_twnAmount, w = 2)
    mUI.MelLabel(_uiRow_twnAmount,l='Amount')

    self.uiFF_tweenBase = mUI.MelFloatField(_uiRow_twnAmount, w = 50, value = .2,
                                            cc = lambda *a: self.uiSlider_tweenBase.setValue(self.uiFF_tweenBase.getValue()))    

    self.uiSlider_tweenBase = mUI.MelFloatSlider(_uiRow_twnAmount, 0, 2.0, defaultValue=.2, 
                                                 #bgc = cgmUI.guiBackgroundColor,
                                                 value = .2,
                                                 cc = lambda *a: self.uiFF_tweenBase.setValue(self.uiSlider_tweenBase.getValue()),
                                                 #dragCommand = lambda *a: log.info(self.uiSlider_tweenBase.getValue()),
                                                 )
    mUI.MelSpacer(_uiRow_twnAmount, w = 1)
    """
    mc.button(parent=_uiRow_tween ,
              ut = 'cgmUITemplate',
              l = 'R',
              c = lambda *a: self.uiSlider_tween.reset(),
              ann = "Reset tweener")
    """
    mUI.MelSpacer(_uiRow_twnAmount, w = 2)
    _uiRow_twnAmount.setStretchWidget(self.uiSlider_tweenBase)
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    _row.layout() 
    
    
    return
    

def buildSection_mrsSwitch(self,parent):
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
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
                  c = cgmGEN.Callback(uiFunc_contextualAction,self,**_arg),
                  ann = _d.get('ann',b))
    mUI.MelSpacer(_row,w=5)
    _row.layout()
    
def buildSection_mrsSettings(self,parent):
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
                      c=cgmGEN.Callback(uiFunc_contextSetValue,self,n,v,_mode))
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
                    c = cgmGEN.Callback(mPuppet.atUtils,'modules_settings_set',**{attr:1}))                    
        mc.menuItem(p = mi_tmpMenu, l="Hide",
                    c = cgmGEN.Callback(mPuppet.atUtils,'modules_settings_set',**{attr:0}))
        
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
                                               c = cgmGEN.Callback(mc.setAttr,"%s"%mi_attr.p_combinedName,i),
                                               rb = b_state )    
    """

@cgmGEN.Timer
def get_context(self, addMirrors = False,**kws):
    _str_func='get_context'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    
    _keys = kws.keys()
    if 'children' in _keys:
        b_children = kws.get('children')
    else:
        b_children = bool(self.cgmVar_mrsContext_children.value)
    
    if 'siblings' in _keys:
        b_siblings = kws.get('siblings')
    else:
        b_siblings = bool(self.cgmVar_mrsContext_siblings.value)
        
    if 'mirror' in _keys:
        b_mirror = kws.get('mirror')
    else:
        b_mirror = bool(self.cgmVar_mrsContext_mirror.value)
        
    if 'context' in _keys:
        context = kws.get('context')
    else:
        context = self.var_mrsContext.value
    
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
    self.d_puppetData = {'mControls':[],
                         'mControlsMirror':[],
                         'mPuppets':[],
                         'mModules':[],
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

    #before we get mirrors we're going to buffer our main modules so that mirror calls don't get screwy
    self.d_puppetData['mModulesBase'] = copy.copy(self.d_puppetData['mModules'])
    

    if context == 'scene':
        log.debug("|{0}| >> Scene mode bail...".format(_str_func))          
        self.d_puppetData['mPuppets'] = r9Meta.getMetaNodes(mTypes = 'cgmRigPuppet')
        ls=[]
        for mPuppet in self.d_puppetData['mPuppets']:
            for mModule in mPuppet.atUtils('modules_get'):
                if mModule not in self.d_puppetData['mModules']:
                    self.d_puppetData['mModules'].append(mModule)            
            
            #mPuppet.puppetSet.select()
            #ls.extend(mc.ls(sl=True))
        #self.d_puppetData['sControls'] = ls
        return self.d_puppetData['mPuppets']


    #process...
    if b_siblings:
        log.debug(cgmGEN._str_subLine)        
        log.debug("|{0}| >> sibling check...".format(_str_func))
        if context == 'part':
            print(cgmGEN._str_hardBreak)        
            log.warning(cgmGEN._str_hardBreak)        
            log.warning("|{0}| >> JOSH ... part siblings won't work right until you tag build profile for matching ".format(_str_func))
            log.warning(cgmGEN._str_hardBreak)        
            print(cgmGEN._str_hardBreak)                    
            
            res = []
            for mModule in self.d_puppetData['mModules']:
                log.debug("|{0}| >> sibling check: {1}".format(_str_func,mModule))
                for mSib in mModule.atUtils('siblings_get'):
                    if mSib not in res:
                        res.append(mSib)
                            
            self.d_puppetData['mModules'].extend(res)#...push new data back
            
        elif context == 'control':
            res = []
            for mModule in self.d_puppetData['mModules']:
                log.debug("|{0}| >> sibling gathering for control | {1}".format(_str_func,mModule))
                #res.extend(mModule.rigNull.msgList_get("controlsAll"))
                res.extend(mModule.rigNull.moduleSet.getMetaList())
            self.d_puppetData['mControls'] = res
                
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

        """   
        elif context == 'puppet':
            log.warning('Puppet context with children is [parts] contextually. Changing for remainder of query.')
            context = 'part'
            res = []
            for mPuppet in self.d_puppetData['mPuppets']:
                res.extend(mPuppet.atUtils('modules_get'))
            self.d_puppetData['mPuppets'] = res
            """
        
    if  b_mirror or addMirrors:
        log.debug(cgmGEN._str_subLine)        
        log.debug("|{0}| >> Context mirror check...".format(_str_func))
        if context == 'control':
            ml_mirror = []
            
            for mControl in self.d_puppetData['mControls']:
                if mControl.getMessage('mirrorControl'):
                    log.debug("|{0}| >> Found mirror for: {1}".format(_str_func,mControl))                    
                    ml_mirror.append(mControl.getMessage('mirrorControl',asMeta=True)[0])
                    
            if ml_mirror:
                res.extend(ml_mirror)
                self.d_puppetData['mControls'].extend(ml_mirror)
                self.d_puppetData['mControlsMirror'].extend(ml_mirror)
            
        elif context == 'part':
            ml_mirrors =[]
            for mModule in self.d_puppetData['mModules']:
                mMirror = mModule.atUtils('mirror_get')
                if mMirror:
                    log.debug("|{0}| >> Mirror: {1}".format(_str_func,mMirror))
                    if mMirror not in res:
                        res.append(mMirror)
                        ml_mirrors.append(mMirror)
            self.d_puppetData['mModules'] = res
            self.d_puppetData['mModulesMirror'] = ml_mirrors
    
    if context in ['puppet','scene']:
        for mPuppet in self.d_puppetData['mPuppets']:
            for mModule in mPuppet.atUtils('modules_get'):
                if mModule not in self.d_puppetData['mModules']:
                    self.d_puppetData['mModules'].append(mModule)
        
    #pprint.pprint(self.d_puppetData)
    return res

@cgmGEN.Timer
def get_contextualControls(self,mirrorQuery=False,**kws):
    _str_func='get_contextualControls'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    
    _keys = kws.keys()
    if 'children' in _keys:
        b_children = kws.get('children')
    else:
        b_children = bool(self.cgmVar_mrsContext_children.value)
    
    if 'siblings' in _keys:
        b_siblings = kws.get('siblings')
    else:
        b_siblings = bool(self.cgmVar_mrsContext_siblings.value)
        
    if 'mirror' in _keys:
        b_mirror = kws.get('mirror')
    else:
        b_mirror = bool(self.cgmVar_mrsContext_mirror.value)
        
    if 'context' in _keys:
        context = kws.get('context')
    else:
        context = self.var_mrsContext.value
    
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
        if context == 'part':
            if mirrorQuery:
                for mPart in self.d_puppetData['mModules']:
                    ls.extend([mObj.mNode for mObj in mPart.UTILS.controls_get(mPart,'mirror')])            
            else:
                for mPart in self.d_puppetData['mModules']:
                    ls.extend(mPart.rigNull.moduleSet.getList())
        elif context in ['puppet','scene']:
            if mirrorQuery:
                for mPuppet in self.d_puppetData['mPuppets']:
                    for mPart in mPuppet.UTILS.modules_get(mPuppet):
                        ls.extend([mObj.mNode for mObj in mPart.UTILS.controls_get(mPart,'mirror')])            
            else:
                for mPuppet in self.d_puppetData['mPuppets']:
                    mPuppet.puppetSet.select()
                    ls.extend(mc.ls(sl=True))
                
        self.d_puppetData['sControls'] = ls
    else:
        self.d_puppetData['sControls'] = [mObj.mNode for mObj in self.d_puppetData['mControls']]
        
    self.d_puppetData['sControls'] = LISTS.get_noDuplicates(self.d_puppetData['sControls'])
    self.d_puppetData['mControls'] = cgmMeta.validateObjListArg(self.d_puppetData['sControls'])
    return self.d_puppetData['sControls']

#@cgmGEN.Timer
def uiFunc_contextualAction(self, **kws):
    try:
        _str_func='uiFunc_contextualAction'
        l_kws = []
        for k,v in kws.iteritems():
            l_kws.append("{0}:{1}".format(k,v))
        
        _mode = kws.pop('mode',False)
        _context = kws.get('context') or self.var_mrsContext.value
        
        log.debug("|{0}| >> context: {1} | {2}".format(_str_func,_context,' | '.join(l_kws)))
        
        d_context = {}
        _mirrorQuery = False
        if _mode in ['mirrorPush','mirrorPull','symLeft','symRight','mirrorFlip','mirrorSelect','mirrorSelectOnly']:
            kws['addMirrors'] = True
            _mirrorQuery = True
            
        res_context = get_context(self,**kws)
        
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
            #pprint.pprint(self.d_puppetData['mModules'])
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
            for mObj in self.d_puppetData['mModules']:
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
            for mObj in self.d_puppetData['mModules']:
                _l_buffer = mObj.atUtils('controls_getDat',_tag,listOnly=True)
                if _l_buffer:
                    l_new.extend([mHandle.mNode for mHandle in _l_buffer])
            
            if not l_new:
                return log.warning("Context: {0} | No controls found in mode: {1}".format(_context, _mode))
    
                    
            mc.select(l_new)
            ml_resetChannels.main(**{'transformsOnly': self.var_resetMode.value})
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
                ml_resetChannels.main(**{'transformsOnly': self.var_resetMode.value})
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
            mBaseModule = self.d_puppetData['mModulesBase'][0]
            log.debug("|{0}| >> Mirroring. base: {1}".format(_str_func,mBaseModule))
            _primeAxis = 'Left'
            
            if _mode == 'mirrorSelect':
                mc.select(_l_controls)
                return
            elif _mode == 'mirrorSelectOnly':
                l_sel = []
                if _context == 'control':
                    for mObj in  self.d_puppetData['mControlsMirror']:
                        l_sel.append(mObj.mNode)
                elif _context == 'part':
                    #pprint.pprint( self.d_puppetData['mModulesMirror'] )
                    #return
                    for mPart in self.d_puppetData['mModulesMirror']:
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
                mMirror = mBaseModule.atUtils('mirror_get')
                if mMirror and mMirror.hasAttr('cgmDirection'):
                    _primeAxis = mMirror.cgmDirection.capitalize()
                else:
                    _primeAxis = 'Centre'
                    
            elif _mode == 'mirrorPush':
                if mBaseModule.hasAttr('cgmDirection'):
                    _primeAxis = mBaseModule.cgmDirection.capitalize()
                else:
                    _primeAxis = 'Centre'
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
            if not self.d_puppetData['mPuppets']:
                return log.error("No puppets detected".format(_mode))
            for mPuppet in self.d_puppetData['mPuppets']:
                mPuppet.atUtils('mirror_verify')
            return endCall(self)
        
        elif _mode == 'upToDate':
            log.info("Context: {0} | {1}".format(_context,_mode))
            if not self.d_puppetData['mPuppets']:
                return log.error("No puppets detected".format(_mode))
            for mPuppet in self.d_puppetData['mPuppets']:
                mPuppet.atUtils('is_upToDate',True)
            return endCall(self)
        
        elif _mode == 'tweenDrag':
            mc.select(_l_controls)
            return ml_breakdownDragger.drag()
    
        elif _mode in ['tweenNext','tweenPrev','tweenAverage']:
            v_tween = kws.get('tweenValue', None)
            if v_tween is None:
                try:v_tween = self.uiFF_tweenBase.getValue()
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
            if not self.d_puppetData['mModules']:
                return log.error("No modules detected".format(_mode))
            for mModule in self.d_puppetData['mModules']:
                res.append(mModule.atUtils('switchMode',_mode))
            
            if _mode in ['aimSnap','aimToIK','aimToFK']:#no reselect
                return res
            endCall(self,False)
            return res
            #sreturn mc.select(_l_controls)
            
        else:
            return log.error("Unknown contextual action: {0}".format(_mode))
        return 
    except Exception,err:
        pprint.pprint(vars())
        raise Exception,err

def uiFunc_contextSetValue(self, attr=None,value=None, mode = None,**kws):
    _str_func='uiFunc_settingsSet'
    log.debug("|{0}| >>  context: {1} | attr: {2} | value: {3} | mode: {4}".format(_str_func,mode,attr,value,mode)+ '-'*80)
    
    get_context(self,**kws)
    
    if mode == 'moduleSettings':
        if not self.d_puppetData['mModules']:
            return log.error("No modules found in context")
        for mModule in self.d_puppetData['mModules']:
            ATTR.set(mModule.rigNull.settings.mNode, attr, value)
            
    elif mode == 'puppetSettings':
        for mPuppet in self.d_puppetData['mPuppets']:
            ATTR.set(mPuppet.masterControl.controlSettings.mNode, attr, value)
    else:
        return log.error("Unknown contextualSetValue mode: {0}".format(mode))
    """
    for mPuppet in self.d_puppetData['mPuppets']:
        if mode == 'moduleSettings':
            mPuppet.atUtils('modules_settings_set',**{attr:value})
            #mPuppet.UTILS.module_settings_set(mPuppet,**{attr,value})
        elif mode == 'puppetSettings':
            ATTR.set(mPuppet.masterControl.controlSettings.mNode, attr, value)
        else:
            return log.error("Unknown contextualSetValue mode: {0}".format(mode))"""
        
    
    
    

def buildColumn_main(self,parent, asScroll = False):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """   
    if asScroll:
        _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUISubTemplate') 
    else:
        _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
    
    #buildSection_puppet(self,_inside)
    buildSection_MRSAnim(self,_inside)
    #buildSection_MRSAnim(self,_inside)
    
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

def uiFunc_tweenSliderDrop(self):
    _str_func='uiFunc_tweenSliderDrop'
    """
    _context = self.var_mrsContext.value
    
    #log.debug("|{0}| >> context: {1} | {2}".format(_str_func,_context,' | '.join(l_kws)))
    
    v_tween = self.uiSlider_tween.getValue()
    if v_tween >= 0.0:
        mode = 'tweenNext'
    else:
        mode = 'tweenPrev'
        
    uiFunc_contextualAction(self,**{'mode':mode,'tweenValue':v_tween})
    """

    log.info("Last drag value: {0}".format(self.uiSlider_tween.getValue()))
    self.uiSlider_tween.setValue(0)
    self.keySel = {}#...clear thiss
    if not self._sel:
        return log.error("Nothing in context")    
    mc.select(self._sel)
    #if report:log.info("Context: {0} | mode: {1} | done.".format(_context, _mode))
    return     
    
def uiFunc_tweenSlider(self):
    _str_func='uiFunc_tweenSlider'
    
    try:self.keySel
    except:self.keySel = {}
    
    if not self.keySel:
        uiFunc_contextualAction(self,mode='select')
        
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

    if not self._sel:
        return     
    v_tween = self.uiSlider_tween.getValue()
    if v_tween > 0:
        for curve in self.keySel.curves:
            for i,v,n in zip(self.time[curve],self.value[curve],self.next[curve]):
                mc.keyframe(curve, time=(i,), valueChange=v+((n-v)*v_tween))
    elif v_tween <0:
        for curve in self.keySel.curves:
            for i,v,p in zip(self.time[curve],self.value[curve],self.prev[curve]):
                mc.keyframe(curve, time=(i,), valueChange=v+((p-v)*(-1*v_tween)))
    
    #log.info(self.uiSlider_tween.getValue())
    
     
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
        selection = search.returnSelectedAttributesFromChannelBox(False) or []
        if not selection:
            selection = mc.ls(sl=True) or []
            if not selection:
                return log.warning('cgmPuppetKey.deleteKey>>> Nothing l_selected!')

        mel.eval('timeSliderClearKey;') 
        
        
        
        
def uiFunc_resetSliderDrop(self):
    _str_func='uiFunc_resetSliderDrop'
    """
    _context = self.var_mrsContext.value
    
    #log.debug("|{0}| >> context: {1} | {2}".format(_str_func,_context,' | '.join(l_kws)))
    
    v_tween = self.uiSlider_tween.getValue()
    if v_tween >= 0.0:
        mode = 'tweenNext'
    else:
        mode = 'tweenPrev'
        
    uiFunc_contextualAction(self,**{'mode':mode,'tweenValue':v_tween})
    """
    mc.undoInfo(closeChunk=True)
    if self.b_autoKey:mc.autoKeyframe(state=True)
    log.info("Last drag value: {0}".format(self.uiSlider_tween.getValue()))
    self.uiSlider_reset.setValue(0)
    #pprint.pprint(self.d_resetDat)
    self.d_resetDat = {}#...clear thiss
    if not self._sel:
        return log.error("Nothing in context")
    
    mc.select(self._sel)
    #if report:log.info("Context: {0} | mode: {1} | done.".format(_context, _mode))
    return     
    
def uiFunc_resetSlider(self):
    _str_func='uiFunc_tweenSlider'
    
    try:self.d_resetDat
    except:self.d_resetDat = {}
    self.b_autoKey = mc.autoKeyframe(q=True,state=True)
    
    if not self.d_resetDat:
        mc.undoInfo(openChunk=True)
        if self.b_autoKey:mc.autoKeyframe(state=False)
        
        uiFunc_contextualAction(self,mode='select')
        
        for i,mCtrl in enumerate(self.d_puppetData['mControls']):
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
                
        
    if not self._sel:
        return
    
    v_reset = self.uiSlider_reset.getValue()
    
    for mCtrl,aDat in self.d_resetDat.iteritems():
        for a,vDat in aDat.iteritems():
            #print("{0} | {1} | {2}".format(mCtrl.mNode,a,vDat['default']))
            current = vDat['value']
            setValue = current + ((vDat['default'] - current)*v_reset)
            #ATTR.set(mCtrl.mNode,a,setValue)
            mCtrl.__setattr__(a,setValue)
            
#==============================================================================================
#Marking menu
#==============================================================================================
@cgmGEN.Timer
def mmUI_radial(self,parent):
    _str_func = "bUI_radial" 
    
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
                #c = cgmGEN.Callback(mmFunc_test,self),
                #rp = 'SW',
                #) 
@cgmGEN.Timer
def mmUI_optionMenu(self, parent):
    return
    _optionVar_val_moduleOn = self.var_PuppetMMBuildModule.value
    _optionVar_val_puppetOn = self.var_PuppetMMBuildPuppet.value    
    
    uiBuildMenus = mc.menuItem(parent = parent, subMenu = True,
                               l = 'Build Menus')
    
    mc.menuItem(parent = uiBuildMenus,
                l = 'Module',
                c = cgmGEN.Callback(self.var_PuppetMMBuildModule.setValue, not _optionVar_val_moduleOn),
                cb = _optionVar_val_moduleOn)
    mc.menuItem(parent = uiBuildMenus,
                l = 'Puppet',
                c = cgmGEN.Callback(self.var_PuppetMMBuildPuppet.setValue, not _optionVar_val_puppetOn),
                cb = _optionVar_val_puppetOn)    
    
@cgmGEN.Timer
def mmUI_lower(self,parent):
    """
    Create the UI
    """
    _str_func = 'bUI_lower'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    
    #_optionVar_val_moduleOn = self.var_PuppetMMBuildModule.value
    #_optionVar_val_puppetOn = self.var_PuppetMMBuildPuppet.value  
    
    #Change space menu
    DYNPARENTTOOL.uiMenu_changeSpace(self,parent,False)
    
    #>>> Control ==========================================================================================    
    mmUI_controls(self,parent)
    mmUI_part(self,parent)
    mmUI_puppet(self,parent)
    return
        
    #>>> Module ==========================================================================================    
    if _optionVar_val_moduleOn and self._ml_modules:
        bUI_moduleSection(self,parent)
    
    #>>> Puppet ==========================================================================================    
    if _optionVar_val_puppetOn and self._l_puppets:
        bUI_puppetSection(self,parent)
    
    
    mc.menuItem(p=parent,l = "-"*25,en = False)    
    mc.menuItem(parent = parent,
                l='MRS - WIP',
                c=lambda *a: mc.evalDeferred(TOOLCALLS.mrsUI))    
    



def mmFunc_test(self):
    uiFunc_contextualAction(self, **{'mode':'report',
                                     'context':'control',
                                     'mirror':False,
                                     'children':False,
                                     'siblings':False})
            

@cgmGEN.Timer
def mmUI_controls(self,parent = None):
    _str_func = 'mmUI_controls'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    
    mc.menuItem(p=parent,l="-- Controls --",en=False)
    _context = 'control'

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
                  'context':_context,
                  'mirror':_d.get('mirror',False),
                  'children':_d.get('children',False),
                  'siblings':_d.get('siblings',False)}
        
        mc.menuItem(p=_mirror,l=m,
                    c=cgmGEN.Callback(uiFunc_contextualAction,self, **_d_tmp),
                )
    return

@cgmGEN.Timer
def mmUI_puppet(self,parent = None):
    _str_func = 'mmUI_part'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    
    mc.menuItem(p=parent,l="-- Puppet --",en=False)
    _context = 'puppet'
    

    
    #Basic =============================================================================
    d_setup = {'Key':{'mode':'key'},
               'bdKey':{'mode':'bdKey'},
               'Reset':{'mode':'reset'},
               'Next Key':{'mode':'nextKey'},
               'Prev Key':{'mode':'prevKey'},
               
               }
    
    for m in ['Key','bdKey','Reset','Next Key','Prev Key']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'context':_context,
                  'mirror':_d.get('mirror',False),
                  'children':_d.get('children',False),
                  'siblings':_d.get('siblings',False)}
        
        mc.menuItem(p=parent,l=m,
                    c=cgmGEN.Callback(uiFunc_contextualAction,self, **_d_tmp),
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
        _d_tmp = {'context':_context,
                  'mirror':False,
                  'children':False,
                  'siblings':False}                  
        for v,o in enumerate(l_options):
            mc.menuItem(p=_sub,l=o,
                        c=cgmGEN.Callback(uiFunc_contextSetValue,self,n,v,_mode,**_d_tmp))
        
        """
        if n in l_settings:
            l_options = ['hide','show']
            _mode = 'moduleSettings'
        else:
            l_options = ['off','lock','on']
            _mode = 'puppetSettings'
        """    
    

@cgmGEN.Timer
def mmUI_part(self,parent = None):
    _str_func = 'mmUI_part'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    
    mc.menuItem(p=parent,l="-- Part --",en=False)
    _context = 'part'
    
    #Switch =============================================================================
    _select = mc.menuItem(p=parent,l="Switch",subMenu=True)

    for m in ['FKon','FKsnap','IKon','IKsnap','IKsnapAll',
              'aimToFK','aimOn','aimOff','aimToIK','aimSnap']:
        #_d = d_setup[m]
        _d_tmp = {'mode':m,
                  'context':_context,
                  'mirror':False,
                  'children':False,
                  'siblings':False}

        mc.menuItem(p=_select,l=m,
                    c=cgmGEN.Callback(uiFunc_contextualAction,self, **_d_tmp))
        
    #Basic =============================================================================
    d_setup = {'Key':{'mode':'key'},
               'bdKey':{'mode':'bdKey'},
               'Reset':{'mode':'reset'},
               'Next Key':{'mode':'nextKey'},
               'Prev Key':{'mode':'prevKey'},
               
               }
    
    for m in ['Key','bdKey','Reset','Next Key','Prev Key']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'context':_context,
                  'mirror':_d.get('mirror',False),
                  'children':_d.get('children',False),
                  'siblings':_d.get('siblings',False)}
        
        mc.menuItem(p=parent,l=m,
                    c=cgmGEN.Callback(uiFunc_contextualAction,self, **_d_tmp),
                )

        
            
    
    
    #Select =============================================================================
    d_setup = {'all':{'mode':'select'},
               'add mirror':{'mode':'mirrorSelect'},
               'mirror only':{'mode':'mirrorSelectOnly'},
               'fk':{'mode':'selectFK'},
               'ik':{'mode':'selectIK'},
               'ikEnd':{'mode':'selectIKEnd'},
               'seg':{'mode':'selectSeg'},
               'direct':{'mode':'selectDirect'},}

    ['select','selectFK','selectIK','selectIKEnd','selectSeg','selectDirect']
    _select = mc.menuItem(p=parent,l="Select",subMenu=True)
    
    for m in ['all','add mirror','mirror only','fk','ik','ikEnd','seg','direct']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'context':_context,
                  'mirror':_d.get('mirror',False),
                  'children':_d.get('children',False),
                  'siblings':_d.get('siblings',False)}
        
        mc.menuItem(p=_select,l=m,
                    c=cgmGEN.Callback(uiFunc_contextualAction,self, **_d_tmp),
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
                  'context':_context,
                  'mirror':_d.get('mirror',False),
                  'children':_d.get('children',False),
                  'siblings':_d.get('siblings',False)}
        
        mc.menuItem(p=_mirror,l=m,
                    c=cgmGEN.Callback(uiFunc_contextualAction,self, **_d_tmp),
                )
        
    _children = mc.menuItem(p=parent,l="Children",subMenu=True)
    mmUI_section(self,_children,children=True)
    
    
    _toggle = mc.menuItem(p=parent,l="Toggle",subMenu=True)
    
    l_settings = ['visSub','visDirect','visRoot']
    #l_enums = ['skeleton','geo','proxy']

    for n in l_settings:
        _sub = mc.menuItem(p=_toggle,l=n,subMenu=True)
        _d_tmp = {'context':_context,
                  'mirror':False,
                  'children':False,
                  'siblings':False}                  
        for v,o in enumerate(['hide','show']):
            mc.menuItem(p=_sub,l=o,
                        c=cgmGEN.Callback(uiFunc_contextSetValue,self,n,v,'moduleSettings',**_d_tmp))
        
        """
        if n in l_settings:
            l_options = ['hide','show']
            _mode = 'moduleSettings'
        else:
            l_options = ['off','lock','on']
            _mode = 'puppetSettings'
        """
        
    return


@cgmGEN.Timer
def mmUI_section(self,parent = None, context= 'part', mirror = False, children = False, siblings=False):
    _str_func = 'mmUI_part'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    
    _context = context

    #Basic =============================================================================
    d_setup = {'Key':{'mode':'key'},
               'bdKey':{'mode':'bdKey'},
               'Reset':{'mode':'reset'},
               'Next Key':{'mode':'nextKey'},
               'Prev Key':{'mode':'prevKey'},
               
               }
    
    for m in ['Key','bdKey','Reset','Next Key','Prev Key']:
        _d = d_setup[m]
        _d_tmp = {'mode':_d['mode'],
                  'context':_context,
                  'mirror':mirror,
                  'children':children,
                  'siblings':siblings,
                  }
        
        mc.menuItem(p=parent,l=m,
                    c=cgmGEN.Callback(uiFunc_contextualAction,self, **_d_tmp),
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
                  'context':_context,
                  'mirror':mirror,
                  'children':children,
                  'siblings':siblings,
                  }
        
        mc.menuItem(p=_select,l=m,
                    c=cgmGEN.Callback(uiFunc_contextualAction,self, **_d_tmp),
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
                  'context':_context,
                  'mirror':mirror,
                  'children':children,
                  'siblings':siblings,
                  }
        
        mc.menuItem(p=_mirror,l=m,
                    c=cgmGEN.Callback(uiFunc_contextualAction,self, **_d_tmp),
                )
        
    _toggle = mc.menuItem(p=parent,l="Toggle",subMenu=True)
    
    l_settings = ['visSub','visDirect','visRoot']
    #l_enums = ['skeleton','geo','proxy']

    for n in l_settings:
        _sub = mc.menuItem(p=_toggle,l=n,subMenu=True)
        _d_tmp = {'context':_context,
                  'mirror':mirror,
                  'children':children,
                  'siblings':siblings,}
        for v,o in enumerate(['hide','show']):
            mc.menuItem(p=_sub,l=o,
                        c=cgmGEN.Callback(uiFunc_contextSetValue,self,n,v,'moduleSettings',**_d_tmp))
    return
