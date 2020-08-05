"""
------------------------------------------
toolbox: cgm.core.tools
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__version__ = '0.1.01092019'

import webbrowser

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import maya.cmds as mc
import maya
import maya.mel as mel
import Red9

from cgm.core import cgm_General as cgmGen
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
from cgm.core.lib import shared_data as SHARED
from cgm.core.tools import locinator as LOCINATOR
import cgm.core.lib.locator_utils as LOC
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import curve_Utils as CURVES
import cgm.core.tools.lib.snap_calls as SNAPCALLS
from cgm.core.tools import meshTools as MESHTOOLS
import cgm.core.lib.distance_utils as DIST
from cgm.core.lib import node_utils as NODES
from cgm.core.tools import attrTools as ATTRTOOLS
from cgm.core.tools import dynParentTool as DYNPARENTTOOL
import cgm.core.tools.mocapBakeTools as MOCAPBAKE
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.tools.locinator as LOCINATOR
import cgm.core.lib.arrange_utils as ARRANGE
import cgm.core.lib.rigging_utils as RIGGING
import cgm.core.classes.GuiFactory as cgmUI
import cgm.core.tools.lib.annotations as TOOLANNO
import cgm.core.lib.transform_utils as TRANS
import cgm.core.tools.transformTools as TT
import cgm.core.tools.jointTools as JOINTTOOLS
import cgm.core.lib.sdk_utils as SDK
from cgm.core.tools.lib import tool_chunks as UICHUNKS
import cgm.core.rig.constraint_utils as RIGCONSTRAINTS
import cgm.core.cgmPy.validateArgs as VALID
import cgm.core.tools.setTools as SETTOOLS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.skin_utils as SKIN
import cgm.core.lib.constraint_utils as CONSTRAINTS
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.skinDat as SKINDAT
import cgm.core.tools.lib.tool_chunks as UICHUNKS
import cgm.core.tools.lib.tool_calls as LOADTOOL
import cgm.core.tools.snapTools as SNAPTOOLS
from cgm.lib.ml import (ml_breakdownDragger,
                        ml_resetChannels,
                        ml_deleteKey,
                        ml_setKey,
                        ml_hold,
                        ml_stopwatch,
                        ml_arcTracer,
                        ml_convertRotationOrder,
                        ml_copyAnim)

mUI = cgmUI.mUI

_2016 = False
if cgmGen.__mayaVersion__ >=2016:
    _2016 = True

def uiSetupOptionVars_curveCreation(self):
    self.var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
    self.var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
    self.var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
    self.var_createSizeMode = cgmMeta.cgmOptionVar('cgmVar_createSizeMode', defaultValue=0)
    self.var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)
    self.var_createSizeMulti = cgmMeta.cgmOptionVar('cgmVar_createSizeMultiplierValue', defaultValue=1.25) 
    

def uiFunc_distanceMeastureToField(self):
    _res = DIST.get_distance_between_targets()
    if not _res:
        raise ValueError,"Found no distance data."
    
    self.uiFF_distance.setValue(_res)
    
def uiFunc_vectorMeasureToField(self):
    _res = DIST.get_vector_between_targets()
    
    if not _res:
        raise ValueError,"Found no vector data."
    
    self.uiFF_vecX.setValue(_res[0][0])
    self.uiFF_vecY.setValue(_res[0][1])
    self.uiFF_vecZ.setValue(_res[0][2])
    

#>>
def buildTab_td(self,parent):
    _column = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate')
    
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
               af = [(_column,"top",0),
                     (_column,"left",0),
                     (_column,"right",0),
                     (_column,"bottom",0)])
    except:pass
    #>>>Shape Creation ====================================================================================
    mc.setParent(_column)
    

    #>>>Tools -------------------------------------------------------------------------------------  
    #self.buildRow_context(_column)                     
    
    SNAPTOOLS.buildSection_snap(self,_column)
    cgmUI.add_HeaderBreak()        
    
    SNAPTOOLS.buildSection_aim(self,_column)
    cgmUI.add_HeaderBreak()
    
    SNAPTOOLS.buildSection_advancedSnap(self,_column)
    cgmUI.add_HeaderBreak()           
    
    buildSection_rigging(self,_column)
    cgmUI.add_SectionBreak()  
    
    buildSection_joint(self,_column)
    cgmUI.add_SectionBreak()          
    
    buildSection_transform(self,_column)
    cgmUI.add_SectionBreak()  
    
    
    buildSection_shape(self,_column)
    cgmUI.add_SectionBreak()            
    
    buildSection_color(self,_column)
    cgmUI.add_SectionBreak()  
    
    buildSection_rayCast(self,_column)
    cgmUI.add_SectionBreak()      
    
    buildSection_distance(self,_column)
    
def buildRow_parent(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Parent:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )      

    mc.button(parent=_row,
              l='Ordered',
              ut = 'cgmUITemplate',
              ann = "Parent in selection order",    
              c = lambda *a:TRANS.parent_orderedTargets())                                             

    mc.button(parent=_row,
              l='Reverse Ordered',
              ut = 'cgmUITemplate',
              ann = "Parent in reverse selection order",                                                                                                                       
              c = lambda *a:TRANS.parent_orderedTargets(reverse=True))  
    
    mUI.MelSpacer(_row,w=5)                      
    _row.layout()   
    

def buildColumn_transform(self,parent):
    _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
    

def uiByTab(tabIndex = 0):
    win = ui()
    win.uiTab_setup.setSelectedTabIdx(tabIndex)

def optionVarSetup_basic(self):
    
    self.var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode', defaultValue = 'world')   
    self.var_keyType = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
    self.var_keyMode = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)
    self.var_resetMode = cgmMeta.cgmOptionVar('cgmVar_ChannelResetMode', defaultValue = 0)
    self.var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)    
            
    self.var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
    self.var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)
    self.var_objDefaultOutAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultOutAxis', defaultValue = 3)
    
    self.var_createRayCast = cgmMeta.cgmOptionVar('cgmVar_createRayCast', defaultValue = 'locator')        
    self.var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])            
    self.var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
    self.var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetMode', defaultValue=0)
    self.var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0) 
    self.var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)
    self.var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)

    self.var_matchModeMove = cgmMeta.cgmOptionVar('cgmVar_matchModeMove', defaultValue = 1)
    self.var_matchModeRotate = cgmMeta.cgmOptionVar('cgmVar_matchModeRotate', defaultValue = 1)
    #self.var_matchModePivot = cgmMeta.cgmOptionVar('cgmVar_matchModePivot', defaultValue = 0)
    self.var_matchMode = cgmMeta.cgmOptionVar('cgmVar_matchMode', defaultValue = 2)
    self.var_locinatorTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_locinatorTargetsBuffer',defaultValue = [''])    

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmToolbox'    
    WINDOW_TITLE = 'cgmToolbox 2.0 - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 450,350
    TOOLNAME = 'ui'
    

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

        self.uiPopUpMenu_createShape = None
        self.uiPopUpMenu_color = None
        self.uiPopUpMenu_attr = None
        self.uiPopUpMenu_raycastCreate = None

        self.create_guiOptionVar('matchFrameCollapse',defaultValue = 0) 
        #self.create_guiOptionVar('rayCastFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('aimFrameCollapse',defaultValue = 0)
        self.create_guiOptionVar('aimOptionsFrameCollapse',defaultValue = 0) 
        #self.create_guiOptionVar('objectDefaultsFrameCollapse',defaultValue = 0) 
        #self.create_guiOptionVar('shapeFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('snapFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('tdFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('animFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('layoutFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('distanceFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('colorFrameCollapse',defaultValue = 0) 
        #self.create_guiOptionVar('animOptionsFrameCollapse',defaultValue = 0) 
        #self.create_guiOptionVar('transformFrameCollapse',defaultValue = 0) 


        self.var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode', defaultValue = 'world')   
        self.var_keyType = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
        self.var_keyMode = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)
        self.var_resetMode = cgmMeta.cgmOptionVar('cgmVar_ChannelResetMode', defaultValue = 0)
        self.var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
        self.var_attrCreateType = cgmMeta.cgmOptionVar('cgmVar_attrCreateType', defaultValue = 'float')        
        self.var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
        self.var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
        self.var_createSizeMode = cgmMeta.cgmOptionVar('cgmVar_createSizeMode', defaultValue=0)
        self.var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)
        self.var_createSizeMulti = cgmMeta.cgmOptionVar('cgmVar_createSizeMultiplierValue', defaultValue=1.25)
        self.var_contextTD = cgmMeta.cgmOptionVar('cgmVar_contextTD', defaultValue = 'selection')


        self.var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
        self.var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)
        self.var_objDefaultOutAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultOutAxis', defaultValue = 3)
        
        self.var_createRayCast = cgmMeta.cgmOptionVar('cgmVar_createRayCast', defaultValue = 'locator')        
        self.var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])            
        self.var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
        self.var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetMode', defaultValue=0)
        self.var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0) 
        self.var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)
        self.var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)

        self.var_matchModeMove = cgmMeta.cgmOptionVar('cgmVar_matchModeMove', defaultValue = 1)
        self.var_matchModeRotate = cgmMeta.cgmOptionVar('cgmVar_matchModeRotate', defaultValue = 1)
        #self.var_matchModePivot = cgmMeta.cgmOptionVar('cgmVar_matchModePivot', defaultValue = 0)
        self.var_matchMode = cgmMeta.cgmOptionVar('cgmVar_matchMode', defaultValue = 2)
        self.var_locinatorTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_locinatorTargetsBuffer',defaultValue = [''])

    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = lambda *a:self.buildMenu_first())
        self.uiMenu_Buffers = mUI.MelMenu( l='Buffers', pmc = lambda *a:self.buildMenu_buffer())
        self.uiMenu_Help = mUI.MelMenu(l = 'Help', pmc = lambda *a:self.buildMenu_help())

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     

        try:
            installer = AutoStartInstaller()
            setupMenu = mc.optionVar( q='cgmVar_ToolboxMainMenu' )
            
            mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Create cgm Tools Menu", cb=setupMenu, c=lambda *a: mc.optionVar( iv=('cgmVar_ToolboxMainMenu', not setupMenu) ) )
            mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )            
            mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Auto-Load On Maya Start", cb=installer.isInstalled(), c=lambda *a: AutoStartInstaller().install() )
        except:
            log.warning("Not loaded from cgm top menu. No autoinstaller options")
            
        UICHUNKS.uiOptionMenu_contextTD(self, self.uiMenu_FirstMenu)

        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )
        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Dock",
                         c = lambda *a:self.do_dock())        

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))


        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))   

    def buildMenu_help(self):
        self.uiMenu_Help.clear()
        
        cgmUI.uiSection_help(self.uiMenu_Help)
        
    def buildMenu_buffer(self):
        self.uiMenu_Buffers.clear()  

        uiMenu = self.uiMenu_Buffers

        _d = {'RayCast':self.var_rayCastTargetsBuffer,
              'Match':self.var_locinatorTargetsBuffer}

        for k in _d.keys():
            var = _d[k]
            _ui = mc.menuItem(p=uiMenu, subMenu = True,
                              l = k)

            mc.menuItem(p=_ui, l="Define",
                        c= cgmGen.Callback(cgmUI.varBuffer_define,self,var))                                

            mc.menuItem(p=_ui, l="Add Selected",
                        c= cgmGen.Callback(cgmUI.varBuffer_add,self,var))        

            mc.menuItem(p=_ui, l="Remove Selected",
                        c= cgmGen.Callback(cgmUI.varBuffer_remove,self,var))        


            mc.menuItem(p=_ui,l='----------------',en=False)
            mc.menuItem(p=_ui, l="Report",
                        c= cgmGen.Callback(var.report))        
            mc.menuItem(p=_ui, l="Select Members",
                        c= cgmGen.Callback(var.select))        
            mc.menuItem(p=_ui, l="Clear",
                        c= cgmGen.Callback(var.clear))  

        mc.menuItem(p=uiMenu, l="--------------",en=False)
        mc.menuItem(p=uiMenu, l="Reload",
                    c= cgmGen.Callback(ui))

    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        #Match
        #Aim

        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        #self._uiDockContent = _MainForm
        ui_tabs = mUI.MelTabLayout( _MainForm)
        #uiTab_setup = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        self.uiTab_setup = ui_tabs
        uiTab_td = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')
        uiTab_anim = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')        
        uiTab_options = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')       
        uiTab_legacy = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')       

        for i,tab in enumerate(['TD','Anim','Settings','Legacy']):
            ui_tabs.setLabel(i,tab)

        buildTab_td(self,uiTab_td)
        buildTab_anim(self,uiTab_anim)
        buildTab_options(self,uiTab_options)
        buildTab_legacy(self,uiTab_legacy)

        #self.buildTab_create(uiTab_create)
        #self.buildTab_update(uiTab_update)

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
  
        


def buildSection_aim(self,parent):
    try:self.var_aimFrameCollapse
    except:self.create_guiOptionVar('aimFrameCollapse',defaultValue = 0)
    
    _frame = mUI.MelFrameLayout(parent,label = 'Aim',vis=True,
                                collapse=self.var_aimFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_aimFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_aimFrameCollapse.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    #>>>Aim snap -------------------------------------------------------------------------------------    
    _row_aim = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)

    mc.button(parent=_row_aim,
              l = 'Aim',
              ut = 'cgmUITemplate',                                    
              c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
              ann = "Aim snap in a from:to selection")

    mc.button(parent=_row_aim,
              ut = 'cgmUITemplate',                  
              l = 'Sel Order',
              c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToNext'),
              ann = "Aim in selection order from each to next")

    mc.button(parent=_row_aim,
              ut = 'cgmUITemplate',                                    
              l = 'First to Mid',
              c = lambda *a:SNAPCALLS.snap_action(None,'aim','firstToRest'),
              ann = "Aim the first object to the midpoint of the rest")  
    
    mc.button(parent=_row_aim,
              l = 'AimCast',
              ut = 'cgmUITemplate',                                                        
              c = lambda *a:SNAPCALLS.aimSnap_start(None),
              ann = "AimCast snap selected objects")           

    _row_aim.layout()   
    
    
    self.buildRow_aimMode(_inside)        
    self.buildSection_objDefaults(_inside,frame=False)
    
        
def buildSection_snap(self,parent):
    try:self.var_snapFrameCollapse
    except:self.create_guiOptionVar('snapFrameCollapse',defaultValue = 0)
    
    _frame = mUI.MelFrameLayout(parent,label = 'Snap',vis=True,
                                collapse=self.var_snapFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_snapFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_snapFrameCollapse.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 


    #>>>Base snap -------------------------------------------------------------------------------------    
    _row_base = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)

    mc.button(parent=_row_base,
              l = 'Point',
              ut = 'cgmUITemplate',
              c = lambda *a:SNAPCALLS.snap_action(None,'point'),
              ann = "Point snap in a from:to selection")

    mc.button(parent=_row_base,
              l = 'Point - closest',
              ut = 'cgmUITemplate',                    
              c = lambda *a:SNAPCALLS.snap_action(None,'closestPoint'),
              ann = "Closest point on target")    

    mc.button(parent=_row_base,
              l = 'Parent',
              ut = 'cgmUITemplate',                    
              c = lambda *a:SNAPCALLS.snap_action(None,'parent'),
              ann = "Parent snap in a from:to selection")
    mc.button(parent=_row_base,
              l = 'Orient',
              ut = 'cgmUITemplate',                  
              c = lambda *a:SNAPCALLS.snap_action(None,'orient'),
              ann = "Orient snap in a from:to selection")        
    mc.button(parent=_row_base,
              l = 'RayCast',
              ut = 'cgmUITemplate',                                                        
              c = lambda *a:SNAPCALLS.raySnap_start(None),
              ann = "RayCast snap selected objects")
    _row_base.layout() 

    
    """
    #>>>Ray snap -------------------------------------------------------------------------------------
    _row_ray = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_ray,w=5)                                              
    mUI.MelLabel(_row_ray,l='CastSnap:')
    _row_ray.setStretchWidget(mUI.MelSeparator(_row_ray)) 

    mc.button(parent=_row_ray,
              l = 'RayCast',
              ut = 'cgmUITemplate',                                                        
              c = lambda *a:SNAPCALLS.raySnap_start(None),
              ann = "RayCast snap selected objects")
    mc.button(parent=_row_ray,
              l = 'AimCast',
              ut = 'cgmUITemplate',                                                        
              c = lambda *a:SNAPCALLS.aimSnap_start(None),
              ann = "AimCast snap selected objects")   
    mUI.MelSpacer(_row_ray,w=5)                                              
    _row_ray.layout()    """         

    #>>>Match snap -------------------------------------------------------------------------------------
    self.buildRow_matchMode(_inside)     

    _row_match = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_match,w=5)                                              
    mUI.MelLabel(_row_match,l='MatchSnap:')
    _row_match.setStretchWidget(mUI.MelSeparator(_row_match)) 

    mc.button(parent=_row_match,
              l = 'Self',
              ut = 'cgmUITemplate',                                                                    
              c = cgmGen.Callback(MMCONTEXT.func_process, LOCINATOR.update_obj, None,'each','Match',False,**{'mode':'self'}),#'targetPivot':self.var_matchModePivot.value                                                                      
              ann = "Update selected objects to match object. If the object has no match object, a loc is created")
    mc.button(parent=_row_match,
              ut = 'cgmUITemplate',                                                                            
              l = 'Target',
              c = cgmGen.Callback(MMCONTEXT.func_process, LOCINATOR.update_obj, None,'each','Match',False,**{'mode':'target'}),#'targetPivot':self.var_matchModePivot.value                                                                      
              ann = "Update the match object, not the object itself")
    mc.button(parent=_row_match,
              ut = 'cgmUITemplate',                                                                            
              l = 'Buffer',
              #c = cgmGen.Callback(buttonAction,raySnap_start(_sel)),                    
              c = cgmGen.Callback(LOCINATOR.update_obj,**{'mode':'buffer'}),#'targetPivot':self.var_matchModePivot.value                                                                      
              ann = "Update the buffer (if exists)")    
    mUI.MelSpacer(_row_match,w=5)                                              
    _row_match.layout()         

    #>>>Arrange snap -------------------------------------------------------------------------------------
    _row_arrange = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_arrange,w=5)                                              
    mUI.MelLabel(_row_arrange,l='Arrange:')
    _row_arrange.setStretchWidget(mUI.MelSeparator(_row_arrange)) 

    mc.button(parent=_row_arrange,
              l = 'Along line(Even)',
              ut = 'cgmUITemplate',                                                                                              
              c = cgmGen.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{}),                                               
              ann = "Layout on line from first to last item")
    mc.button(parent=_row_arrange,
              l = 'Along line(Spaced)',
              ut = 'cgmUITemplate',                                                                                              
              c = cgmGen.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'spaced'}),                                               
              ann = "Layout on line from first to last item closest as possible to original position")    
    mc.button(parent=_row_arrange,
                 l = 'Along Curve(Even)',
                 ut = 'cgmUITemplate',
                 c = cgmGen.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubic'}),                                               
                 ann = "Layout evenly on curve created from the list")        
    mUI.MelSpacer(_row_arrange,w=5)                                              
    _row_arrange.layout()      
    
    
def buildSection_distance(self,parent):
    try:self.var_distanceFrameCollapse
    except:self.create_guiOptionVar('distanceFrameCollapse',defaultValue = 0)
    
    _frame = mUI.MelFrameLayout(parent,label = 'Distance',vis=True,
                                collapse=self.var_distanceFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_distanceFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_distanceFrameCollapse.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 

    #>>>Distance -------------------------------------------------------------------------------------
    _row_dist= mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_dist,w=5)                                              
    mUI.MelLabel(_row_dist,l='Distance:')
    _row_dist.setStretchWidget(mUI.MelSeparator(_row_dist)) 

    self.uiFF_distance = mUI.MelFloatField(_row_dist, ut='cgmUISubTemplate', w= 50)
    """self.uiFF_distance = mUI.MelLabel(_row_dist,
                                          l='21231',
                                          ann='Change the default create shape',
                                          ut='cgmUIInstructionsTemplate',w=100)"""        
    mc.button(parent=_row_dist,
              ut = 'cgmUITemplate',                                                                                                
              l = 'Measure',
              c = lambda *a:uiFunc_distanceMeastureToField(self),
              #c = lambda *a:SNAPCALLS.aimSnap_start(None),
              ann = "Measures distance between selected objects/components")        

    _row_dist.layout()

    #>>>Vector -------------------------------------------------------------------------------------
    _row_vec= mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_vec,w=5)                                              
    mUI.MelLabel(_row_vec,l='Vector:')        
    _row_vec.setStretchWidget(mUI.MelSeparator(_row_vec)) 

    for a in list('xyz'):
        mUI.MelLabel(_row_vec,l=a)
        self.__dict__['uiFF_vec{0}'.format(a.capitalize())] = mUI.MelFloatField(_row_vec, ut='cgmUISubTemplate', w= 50 )

    mc.button(parent=_row_vec,
              ut = 'cgmUITemplate',                                                                                                
              l = 'Measure',
              c = lambda *a:uiFunc_vectorMeasureToField(self),
              ann = "Measures vector between selected objects/components")        


    _row_vec.layout()


    #>>>Near -------------------------------------------------------------------------------------
    _row_near = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_near,w=5)                                              
    mUI.MelLabel(_row_near,l='Near:')
    _row_near.setStretchWidget(mUI.MelSeparator(_row_near)) 

    mc.button(parent=_row_near, 
              ut = 'cgmUITemplate',                                                                              
              l = 'Target',
              ann = "Find nearest target in from:to selection list",
              c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Near Target',True,**{'mode':'closest','resMode':'object'}),                                                                      
              )   
    mc.button(parent=_row_near, 
              ut = 'cgmUITemplate', 
              l = 'Shape',
              ann = "Find nearest shape in  from:to selection list",                    
              c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Near Shape',True,**{'mode':'closest','resMode':'shape'}),                                                                      
              )               
    mc.button(parent=_row_near, 
              ut = 'cgmUITemplate',
              l = 'Surface Point',
              ann = "Find nearest surface point in from:to selection list",                    
              c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Near point on surface',True,**{'mode':'closest','resMode':'pointOnSurface'}),                                                                      
              )     
    mc.button(parent=_row_near, 
              ut = 'cgmUITemplate',
              l = 'Surface Loc',
              ann = "Find nearest surface point in from:to selection list. And loc it.",                                        
              c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Near point on surface',True,**{'mode':'closest','resMode':'pointOnSurfaceLoc'}),                                                                      
              )               
    mc.button(parent=_row_near, 
              ut = 'cgmUITemplate',
              l = 'Surface Nodes',
              ann = "Create nearest surface point nodes in from:to selection list",                                        
              c = cgmGen.Callback(MMCONTEXT.func_process, DIST.create_closest_point_node, None,'firstToEach','Create closest Point Node',True,**{}),                                                                      
              )      

    mUI.MelSpacer(_row_near,w=5)                                              
    _row_near.layout()   

    #>>>Far -------------------------------------------------------------------------------------
    _row_far = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_far,w=5)                                              
    mUI.MelLabel(_row_far,l='far:')
    _row_far.setStretchWidget(mUI.MelSeparator(_row_far)) 

    mc.button(parent=_row_far, 
              ut = 'cgmUITemplate',
              l = 'Target',
              ann = "Find furthest taregt in from:to selection list",                                        
              c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Far Target',True,**{'mode':'far','resMode':'object'}),                                                                      
              )                  
    mc.button(parent=_row_far, 
              ut = 'cgmUITemplate',
              l = 'Shape',
              ann = "Find furthest shape in from:to selection list",                                        
              c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Far Shape',True,**{'mode':'far','resMode':'shape'}),                                                                      
              )   

    mUI.MelSpacer(_row_far,w=5)                                              
    _row_far.layout()           




def buildSection_rigging(self,parent):
    try:self.var_tdFrameCollapse
    except:self.create_guiOptionVar('tdFrameCollapse',defaultValue = 0)
    
    _frame = mUI.MelFrameLayout(parent,label = 'Rigging',vis=True,
                                collapse=self.var_tdFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_tdFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_tdFrameCollapse.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 

    _row_tools1 = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)

    mc.button(parent=_row_tools1,
              l = 'DynParent Tool',
              ut = 'cgmUITemplate',
              c = lambda *a: mc.evalDeferred(DYNPARENTTOOL.ui,lp=1),                  
              ann = "Tool for modifying and setting up dynamic parent groups")

    mc.button(parent=_row_tools1,
              l = 'Locinator',
              ut = 'cgmUITemplate',
              c = lambda *a: mc.evalDeferred(LOCINATOR.ui,lp=1),                  
              ann = "LOCATORS")

    mc.button(parent=_row_tools1,
              l = 'SetTools',
              ut = 'cgmUITemplate',
              c = lambda *a: mc.evalDeferred(SETTOOLS.ui,lp=1),                  
              ann = "Tool for working with sets in maya")        

    _row_tools1.layout()                  

    
    #>>>Create -------------------------------------------------------------------------------------
    _row_create = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_create,w=5)                                              
    mUI.MelLabel(_row_create,l='Create:')
    _row_create.setStretchWidget(mUI.MelSeparator(_row_create)) 

    mc.button(parent=_row_create,
              ut = 'cgmUITemplate',                    
              l = 'Null',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'each','Create Tranform',**{'create':'null'}))    
    mc.button(parent=_row_create,
              ut = 'cgmUITemplate',                    
              l = 'Null(mid)',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Tranform at mid',**{'create':'null','midPoint':'True'}))    

    mc.button(parent=_row_create,
              ut = 'cgmUITemplate',                                        
              l = 'Jnt',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'each','Create Joint',**{'create':'joint'}))         
    mc.button(parent=_row_create,
              ut = 'cgmUITemplate',                                        
              l = 'Jnt(mid)',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Joint at mid',**{'create':'joint','midPoint':'True'}))         

    mc.button(parent=_row_create,
              ut = 'cgmUITemplate',                                        
              l = 'Loc',
              c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, None,'each','Create Loc')) 
    mc.button(parent=_row_create,
              ut = 'cgmUITemplate',                                        
              l = 'Loc(mid)',
              c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, None,'all','Create Loc at mid',**{'mode':'midPoint'}))           
    mc.button(parent=_row_create,
              ut = 'cgmUITemplate',                                        
              l = 'Crv',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Curve',**{'create':'curve'}))                          
    mc.button(parent=_row_create,
              ut = 'cgmUITemplate',                                        
              l = 'CrvLin',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Curve',**{'create':'curveLinear'}))                          

    mUI.MelSpacer(_row_create,w=5)                                              
    _row_create.layout()  
    
    #>>>Copy -------------------------------------------------------------------------------------
    _row_copy = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_copy,w=5)                                              
    mUI.MelLabel(_row_copy,l='Copy:')
    _row_copy.setStretchWidget(mUI.MelSeparator(_row_copy)) 

    mc.button(parent=_row_copy,
              ut = 'cgmUITemplate',                                        
              l = 'Transform',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.match_transform, None,'eachToFirst','Match Transform'),                    
              ann = "")
    mc.button(parent=_row_copy,
              ut = 'cgmUITemplate',                                        
              l = 'Orienation',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.match_orientation, None,'eachToFirst','Match Orientation'),                    
              ann = "")

    mc.button(parent=_row_copy,
              ut = 'cgmUITemplate',                                        
              l = 'Shapes',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.shapeParent_in_place, None,'lastFromRest','Copy Shapes', **{'snapFirst':True}),
              ann = "")

    
    #Pivot stuff -------------------------------------------------------------------------------------------
    mc.button(parent=_row_copy,
              ut = 'cgmUITemplate',                                                          
              l = 'rotatePivot',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.copy_pivot, None,'eachToFirst', 'Match RP',**{'rotatePivot':True,'scalePivot':False}),                                               
              ann = "Copy the rotatePivot from:to")
    mc.button(parent=_row_copy,
              ut = 'cgmUITemplate',                                        
              l = 'scalePivot',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.copy_pivot, None,'eachToFirst', 'Match SP', **{'rotatePivot':False,'scalePivot':True}),                                               
              ann = "Copy the scalePivot from:to")        


    mUI.MelSpacer(_row_copy,w=5)                                              
    _row_copy.layout()    

    buildRow_parent(self,_inside)
    
    #>>>group -------------------------------------------------------------------------------------
    _row_group = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_group,w=5)                                              
    mUI.MelLabel(_row_group,l='Group:')
    _row_group.setStretchWidget(mUI.MelSeparator(_row_group)) 

    mc.button(parent=_row_group,
              ut = 'cgmUITemplate',                                                          
              l = 'Just Group',
              ann = 'Simple grouping. Just like ctrl + g',                        
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.group_me, None,'each','Group',**{'parent':False,'maintainParent':False}),)  
    mc.button(parent=_row_group,
              ut = 'cgmUITemplate',                                                          
              l = 'Group Me',
              ann = 'Group selected objects matching transform as well.',                                        
              #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.group_me, None,'each','Group',**{'parent':True,'maintainParent':False}))          
    mc.button(parent=_row_group,
              ut = 'cgmUITemplate',                                                          
              l = 'In Place',
              ann = 'Group me while maintaining heirarchal position',                                                        
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.group_me, None,'each','Group In Place',**{'parent':True,'maintainParent':True}))     

    mUI.MelSpacer(_row_group,w=5)                                              
    _row_group.layout()      

    
    #>>>Attr -------------------------------------------------------------------------------------
    _row_attr = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_attr,w=5)                                              
    mUI.MelLabel(_row_attr,l='Attr:')
    _row_attr.setStretchWidget(mUI.MelSeparator(_row_attr)) 


    self.uiField_attrType = mUI.MelLabel(_row_attr,
                                         ann='Change the default attr type',
                                         ut='cgmUIInstructionsTemplate',w=100)        
    self.uiField_attrType(edit=True, label = self.var_attrCreateType.value)
    mc.button(parent = _row_attr,
              ut = 'cgmUITemplate',                                                                            
              l='+',
              ann = "Add specified attribute type",  
              c = lambda *a:ATTRTOOLS.uiPrompt_addAttr(self.var_attrCreateType.value))
            #c = cgmGen.Callback(ATTRTOOLS.uiPrompt_addAttr,self.var_attrCreateType.value,**{}))
        
    uiPopup_createAttr(self)
    
    
    mc.button(parent = _row_attr,
              ut = 'cgmUITemplate',                                                                            
              l='cgmAttrTools',
              ann = "Launch cgmAttrTools - Collection of tools for making creating, editing and managing attributes a little less painful",                                                                                                                       
              c=cgmGen.Callback(ATTRTOOLS.ui))   
    
    """
    _add = mc.menuItem(parent=uiAttr,subMenu=True,
                       l='Add',
                       ann = "Add attributes to selected objects...",                                                                                                                              
                       rp='S') 
    _d_attrTypes = {"string":'E','float':'S','enum':'NE','vector':'SW','int':'W','bool':'NW','message':'SE'}
    for _t,_d in _d_attrTypes.iteritems():
        mc.menuItem(parent=_add,
                    l=_t,
                    ann = "Add a {0} attribute(s) to the selected objects".format(_t),                                                                                                       
                    c = cgmGen.Callback(ATTRTOOLS.uiPrompt_addAttr,_t,**{'autoLoadFail':True}),
                    rp=_d)"""

    mc.button(parent = _row_attr,
              ut = 'cgmUITemplate',                                                                              
              l = 'Compare Attrs',
              ann = "Compare the attributes of selected objects. First object is the base of comparison",                                                                                                                                                
              c = cgmGen.Callback(MMCONTEXT.func_process, ATTR.compare_attrs, None, 'firstToRest','Compare Attrs',True,**{}))           

    mUI.MelSpacer(_row_attr,w=5)
    _row_attr.layout()         
    

    #>>>
    buildRow_shapeUtils(self,_inside)
    
    #>>>Joints -------------------------------------------------------------------------------------
    _row_joints = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_joints,w=5)                                              
    mUI.MelLabel(_row_joints,l='Joints:')
    _row_joints.setStretchWidget(mUI.MelSeparator(_row_joints)) 


    mc.button(parent=_row_joints, 
              ut = 'cgmUITemplate',                                                                              
              l = '*Show x',
              ann = "Show the joint axis by current context",                                        
              c= lambda *a:MMCONTEXT.set_attrs(self,'displayLocalAxis',1,self.var_contextTD.value,'joint',select=False),
              )               
    mc.button(parent=_row_joints, 
              ut = 'cgmUITemplate',                                                                              
              l = '*Hide x',
              ann = "Hide the joint axis by current context",                                        
              c= lambda *a:MMCONTEXT.set_attrs(self,'displayLocalAxis',0,self.var_contextTD.value,'joint',select=False),
              )     


    mc.button(parent = _row_joints,
              ut = 'cgmUITemplate',                                                                                                
              l='cometJO',
              c=lambda *a: mel.eval('cometJointOrient'),
              ann="General Joint orientation tool  by Michael Comet")   
    mc.button(parent=_row_joints, 
              ut = 'cgmUITemplate',                                                                              
              l = 'Freeze',
              ann = "Freeze the joint orientation - our method as we don't like Maya's",                                        
              c = cgmGen.Callback(MMCONTEXT.func_process, JOINTS.freezeOrientation, None, 'each','freezeOrientation',False,**{}),                                                                      
              )            


    mc.button(parent = _row_joints,
              ut = 'cgmUITemplate',                                                                                                
              l='seShapeTaper',
              ann = "Fantastic blendtaper like tool for sdk poses by our pal - Scott Englert",                                                        
              c=lambda *a: mel.eval('seShapeTaper'),)   

    mUI.MelSpacer(_row_joints,w=5)                                              
    _row_joints.layout()          

    
    buildRow_mesh(self,_inside)
    buildRow_skin(self,_inside)
    buildRow_constraints(self,_inside)
    buildRow_attachBy(self,_inside)
    buildRow_skinDat(self,_inside)
    buildRow_SDK(self,_inside)
    buildRow_cleanNodes(self,_inside)
    
    
def buildSection_color(self,parent):
    try:self.var_colorFrameCollapse
    except:self.create_guiOptionVar('colorFrameCollapse',defaultValue = 0)    
    _frame = mUI.MelFrameLayout(parent,label = 'Color',vis=True,
                                collapse=self.var_colorFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_colorFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_colorFrameCollapse.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 

    buildRow_color(self,_inside)
    
    
def buildSection_animOptions(self,parent):
    try:self.var_animOptionsFrameCollapse
    except:self.create_guiOptionVar('animOptionsFrameCollapse',defaultValue = 0)
    
    _frame = mUI.MelFrameLayout(parent,label = 'Anim Options',vis=True,
                                collapse=self.var_animOptionsFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_animOptionsFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_animOptionsFrameCollapse.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 


    #>>>KeyMode ====================================================================================
    uiRC = mUI.MelRadioCollection()

    _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row1,w=5)
    mUI.MelLabel(_row1,l='KeyMode')
    _row1.setStretchWidget( mUI.MelSeparator(_row1) )

    uiRC = mUI.MelRadioCollection()
    _on = self.var_keyMode.value

    for i,item in enumerate(['Default','Channelbox']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row1,label=item,sl=_rb,
                          onCommand = cgmGen.Callback(self.var_keyMode.setValue,i))

        mUI.MelSpacer(_row1,w=2)    

    _row1.layout()   

    #>>>KeyType ====================================================================================
    uiRC = mUI.MelRadioCollection()

    _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row1,w=5)
    mUI.MelLabel(_row1,l='Key Type')
    _row1.setStretchWidget( mUI.MelSeparator(_row1) )

    uiRC = mUI.MelRadioCollection()
    _on = self.var_keyType.value

    for i,item in enumerate(['reg','breakdown']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row1,label=item,sl=_rb,
                          onCommand = cgmGen.Callback(self.var_keyType.setValue,i))

        mUI.MelSpacer(_row1,w=2)    

    _row1.layout()   

    #>>>Reset mode ====================================================================================
    uiRC = mUI.MelRadioCollection()

    _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row1,w=5)
    mUI.MelLabel(_row1,l='Reset Mode')
    _row1.setStretchWidget( mUI.MelSeparator(_row1) )

    uiRC = mUI.MelRadioCollection()
    _on = self.var_resetMode.value

    for i,item in enumerate(SHARED.l_resetModes):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row1,label=item,sl=_rb,
                          onCommand = cgmGen.Callback(self.var_resetMode.setValue,i))

        mUI.MelSpacer(_row1,w=2)    

    _row1.layout()         

def buildSection_transform(self,parent):
    try:self.var_transformFrameCollapse
    except:self.create_guiOptionVar('transformFrameCollapse',defaultValue = 0)
    
    _frame = mUI.MelFrameLayout(parent,label = 'Transform',vis=True,
                                collapse=self.var_transformFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_transformFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_transformFrameCollapse.setValue(1)
                                )
    TT.buildColumn_main(self,_frame)

def buildSection_joint(self,parent,label='Joint'):
    try:self.var_jointFrameCollapse
    except:self.create_guiOptionVar('jointFrameCollapse',defaultValue = 0)
    
    _frame = mUI.MelFrameLayout(parent,label = label,vis=True,
                                collapse=self.var_jointFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_jointFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_jointFrameCollapse.setValue(1)
                                )
    JOINTTOOLS.buildColumn_main(self,_frame)   

def buildSection_rayCast(self,parent):
    try:self.var_rayCastFrameCollapse
    except:self.create_guiOptionVar('rayCastFrameCollapse',defaultValue = 0)
    
    _frame = mUI.MelFrameLayout(parent,label = 'Raycast',vis=True,
                                collapse=self.var_rayCastFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_rayCastFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_rayCastFrameCollapse.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 


    #>>>Raycast ====================================================================================

    #>>>Cast Mode  -------------------------------------------------------------------------------------
    uiRC = mUI.MelRadioCollection()
    _on = self.var_rayCastMode.value

    _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row1,w=5)

    mUI.MelLabel(_row1,l='Cast')
    _row1.setStretchWidget( mUI.MelSeparator(_row1) )

    uiRC = mUI.MelRadioCollection()
    _on = self.var_rayCastMode.value

    for i,item in enumerate(['close','mid','far','all','x','y','z']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row1,label=item,sl=_rb,
                          onCommand = cgmGen.Callback(self.var_rayCastMode.setValue,i))

        mUI.MelSpacer(_row1,w=2)    

    _row1.layout() 

    #>>>offset Mode  -------------------------------------------------------------------------------------
    uiRC = mUI.MelRadioCollection()
    _on = self.var_rayCastOffsetMode.value        

    _row_offset = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_offset,w=5)                              
    mUI.MelLabel(_row_offset,l='Offset')
    _row_offset.setStretchWidget( mUI.MelSeparator(_row_offset) )  

    for i,item in enumerate(['None','Distance','snapCast']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row_offset,label=item,sl=_rb,
                          onCommand = cgmGen.Callback(self.var_rayCastOffsetMode.setValue,i))

        mUI.MelSpacer(_row1,w=2)   


    _row_offset.layout()

    #>>>offset Mode  -------------------------------------------------------------------------------------
    uiRC = mUI.MelRadioCollection()
    _on = self.var_rayCastOrientMode.value        

    _row_orient = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_orient,w=5)                              
    mUI.MelLabel(_row_orient,l='Orient')
    _row_orient.setStretchWidget( mUI.MelSeparator(_row_orient) )  

    for i,item in enumerate(['None','Normal']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row_orient,label=item,sl=_rb,
                          onCommand = cgmGen.Callback(self.var_rayCastOrientMode.setValue,i))

        mUI.MelSpacer(_row1,w=2)   

    cgmUI.add_Button(_row_orient,'Set drag interval',
                     lambda *a:self.var_rayCastDragInterval.uiPrompt_value('Set drag interval'),
                     'Set the rayCast drag interval by ui prompt')   
    cgmUI.add_Button(_row_orient,'Set Offset',
                     lambda *a:self.var_rayCastOffsetDist.uiPrompt_value('Set offset distance'),
                     'Set the the rayCast offset distance by ui prompt')         
    mUI.MelSpacer(_row_orient,w=5)                                                  
    _row_orient.layout()

    #>>>rayCast -------------------------------------------------------------------------------------
    _row_rayCast = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_rayCast,w=5)                                              
    mUI.MelLabel(_row_rayCast,l='rayCast:')
    _row_rayCast.setStretchWidget(mUI.MelSeparator(_row_rayCast)) 


    self.uiField_rayCastCreate = mUI.MelLabel(_row_rayCast,
                                              ann='Change the default rayCast create type',
                                              ut='cgmUIInstructionsTemplate',w=100)        
    self.uiField_rayCastCreate(edit=True, label = self.var_createRayCast.value)

    uiPopup_createRayCast(self)       

    mc.button(parent=_row_rayCast,
              ut = 'cgmUITemplate',                                                                              
              l = 'Create',
              c = lambda a: SNAPCALLS.rayCast_create(None,self.var_createRayCast.value,False),
              ann = TOOLANNO._d['raycast']['create'])       
    mc.button(parent=_row_rayCast,
              ut = 'cgmUITemplate',                                                                              
              l = 'Drag',
              c = lambda a: SNAPCALLS.rayCast_create(None,self.var_createRayCast.value,True),
              ann = TOOLANNO._d['raycast']['drag'])       
    """
    mUI.MelLabel(_row_rayCast,
                 l=' | ')

    mc.button(parent=_row_rayCast,
              ut = 'cgmUITemplate',                                                                              

            l = 'RayCast Snap',
            c = lambda *a:SNAPCALLS.raySnap_start(None),
            ann = "RayCast snap selected objects")
    mc.button(parent=_row_rayCast,
              ut = 'cgmUITemplate',                                                                                                
              l = 'AimCast',
              c = lambda *a:SNAPCALLS.aimSnap_start(None),
              ann = "AimCast snap selected objects") """   

    mUI.MelSpacer(_row_rayCast,w=5)                                                  
    _row_rayCast.layout()

def buildSection_objDefaults(self,parent,frame=True):
    if frame:
        try:self.var_objectDefaultsFrameCollapse
        except:self.create_guiOptionVar('objectDefaultsFrameCollapse',defaultValue = 0)        
        
        _frame = mUI.MelFrameLayout(parent,label = 'Obj Defaults',vis=True,
                                    collapse=self.var_objectDefaultsFrameCollapse.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:self.var_objectDefaultsFrameCollapse.setValue(0),
                                    collapseCommand = lambda:self.var_objectDefaultsFrameCollapse.setValue(1)
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    else:
        _inside = parent


    #>>>Aim defaults mode -------------------------------------------------------------------------------------
    _d = {'aim':self.var_objDefaultAimAxis,
          'up':self.var_objDefaultUpAxis,
          'out':self.var_objDefaultOutAxis}

    for k in _d.keys():
        _var = _d[k]

        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l='Obj {0}:'.format(k))
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        uiRC = mUI.MelRadioCollection()

        _on = _var.value

        for i,item in enumerate(SHARED._l_axis_by_string):
            if i == _on:
                _rb = True
            else:_rb = False

            uiRC.createButton(_row,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(_var.setValue,i))

            mUI.MelSpacer(_row,w=2)       


        _row.layout() 


    #>>>Buttons -------------------------------------------------------------------------------------
    _row_defaults = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5, )

    cgmUI.add_Button(_row_defaults,'Tag selected for aim',
                     lambda *a:MMCONTEXT.func_process(SNAP.verify_aimAttrs, mc.ls(sl=True),'each','Verify aim attributes',True,**{}),)                                       
    _row_defaults.layout() 

def buildSection_shape(self,parent):
    try:self.var_shapeFrameCollapse
    except:self.create_guiOptionVar('shapeFrameCollapse',defaultValue = 0)

    _shapes_frame = mUI.MelFrameLayout(parent,label = 'Controls',vis=True,
                                       collapse=self.var_shapeFrameCollapse.value,
                                       collapsable=True,
                                       enable=True,
                                       useTemplate = 'cgmUIHeaderTemplate',
                                       expandCommand = lambda:self.var_shapeFrameCollapse.setValue(0),
                                       collapseCommand = lambda:self.var_shapeFrameCollapse.setValue(1)
                                       )	
    _shape_inside = mUI.MelColumnLayout(_shapes_frame,useTemplate = 'cgmUISubTemplate')  

    
    #>>>Shape Type Row  -------------------------------------------------------------------------------------
    # _row_shapeType = mUI.MelHSingleStretchLayout(_shape_inside,ut='cgmUISubTemplate',padding = 5)
    _row_shapeType = mUI.MelHSingleStretchLayout(_shape_inside,ut='cgmUISubTemplate')

    mUI.MelSpacer(_row_shapeType,w=5)                                      
    mUI.MelLabel(_row_shapeType,l='Shape:')
    self.uiField_shape = mUI.MelLabel(_row_shapeType,
                                      ann='Change the default create shape',
                                      ut='cgmUIInstructionsTemplate',w=100)

    _row_shapeType.setStretchWidget(self.uiField_shape) 


    mUI.MelLabel(_row_shapeType,l='Default Color:')
    self.uiField_shapeColor = mUI.MelLabel(_row_shapeType,
                                           ann='Change the default create color',                                               
                                           ut='cgmUIInstructionsTemplate',w = 100)



    _row_shapeType.layout()
    
    #....shape default
    self.uiField_shape(edit=True, label = self.var_curveCreateType.value)
    self.uiField_shapeColor(edit=True, label = self.var_defaultCreateColor.value)
    
    

    uiPopup_createShape(self)
    uiPopup_createColor(self)
    

    #>>>Create Aim defaults mode -------------------------------------------------------------------------------------
    _d = {'aim':self.var_createAimAxis,
          }

    for k in _d.keys():
        _var = _d[k]

        _row = mUI.MelHSingleStretchLayout(_shape_inside,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l='Create {0}:'.format(k))
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        uiRC = mUI.MelRadioCollection()

        _on = _var.value

        for i,item in enumerate(SHARED._l_axis_by_string):
            if i == _on:
                _rb = True
            else:_rb = False

            uiRC.createButton(_row,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(_var.setValue,i))

            mUI.MelSpacer(_row,w=2)       


        _row.layout()    
    
    #>>>Create Size Modes -------------------------------------------------------------------------------------
    _row_createSize = mUI.MelHSingleStretchLayout(_shape_inside,ut='cgmUISubTemplate')
    mUI.MelSpacer(_row_createSize,w=5)                                              
    mUI.MelLabel(_row_createSize,l='Size Mode:')
    _row_createSize.setStretchWidget(mUI.MelSeparator(_row_createSize)) 

    uiRC = mUI.MelRadioCollection()
    _on = self.var_createSizeMode.value
    #self.var_createSizeValue
    for i,item in enumerate(['guess','fixed','cast']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row_createSize,label=item,sl=_rb,
                          onCommand = cgmGen.Callback(self.var_createSizeMode.setValue,i))
        mUI.MelSpacer(_row_createSize,w=2)    


    cgmUI.add_Button(_row_createSize,'Size',
                     lambda *a:self.var_createSizeValue.uiPrompt_value('Set Size'),
                     'Set the create size value')   
    cgmUI.add_Button(_row_createSize,'Mutltiplier',
                     lambda *a:self.var_createSizeMulti.uiPrompt_value('Set create size multiplier'),
                     'Set the create size multiplier value') 
    mUI.MelSpacer(_row_createSize,w=5)                                              

    _row_createSize.layout()  
    
    #>>>Create -------------------------------------------------------------------------------------
    #_row_curveCreate = mUI.MelHSingleStretchLayout(_shape_inside,ut='cgmUISubTemplate') 
    _row_curveCreate = mUI.MelHLayout(_shape_inside,ut='cgmUISubTemplate',padding = 5)   

    cgmUI.add_Button(_row_curveCreate,'Create',
                     lambda *a:UICHUNKS.uiFunc_createCurve(),
                     #lambda *a:uiFunc_createCurve(),
                     'Create control curves from stored optionVars. Shape: {0} | Color: {1} | Direction: {2}'.format(self.var_curveCreateType.value,
                                                                                                                     self.var_defaultCreateColor.value,
                                                                                                                     SHARED._l_axis_by_string[self.var_createAimAxis.value]))                    
    #mUI.MelSpacer(_row_curveCreate,w=10)                                              
    cgmUI.add_Button(_row_curveCreate,'One of each',
                     lambda *a:UICHUNKS.uiFunc_createOneOfEach(),
                     'Create one of each curve stored in cgm libraries. Size: {0} '.format(self.var_createSizeValue.value) )

    _row_curveCreate.layout()  
    
    buildRow_resizeObj(self,_shape_inside)
    buildRow_mirrorCurve(self,_shape_inside)        
    buildRow_shapeUtils(self,_shape_inside)
    buildRow_colorControls(self,_shape_inside)
    
def buildTab_anim(self,parent):
    _column = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
    parent(edit = True,
           af = [(_column,"top",0),
                 (_column,"left",0),
                 (_column,"right",0),                        
                 (_column,"bottom",0)])    

    #>>>Shape Creation ====================================================================================
    mc.setParent(_column)

    SNAPTOOLS.buildSection_snap(self,_column)
    SNAPTOOLS.buildSection_aim(self,_column)
    SNAPTOOLS.buildSection_advancedSnap(self,_column)

    mc.button(parent = _column,
              ut = 'cgmUITemplate',                                                                                                
              l='cgmLocinator',
              ann = "Launch cgmLocinator - a tool for aiding in the snapping of things",                                                                                                                                       
              c=lambda *a: LOCINATOR.ui()) 

    mc.button(parent = _column,
              ut = 'cgmUITemplate',  
              l='cgmDynParentTool',
              ann = "Launch cgm's dynParent Tool - a tool for assisting space switching setups and more",                                                                                                                                       
              c=lambda *a: DYNPARENTTOOL.ui())   
    mc.button(parent = _column,
              ut = 'cgmUITemplate',  
              l='cgmTransformTools',
              ann = "Launch cgmTransformTools - a tool for tweaking values",                                                                                                                                       
              c=lambda *a: TT.ui())
    mc.button(parent = _column,
              ut = 'cgmUITemplate',
              l='cgmMocapBakeTool',
              ann = "Launch cgmMocapBakeTool -A tool for retargeting and baking control transforms from an animated source",
              c=lambda *a: MOCAPBAKE.ui())
    
    mc.button(parent = _column,
              ut = 'cgmUITemplate',                                                                                                
              l='cgmSetTools',
              ann = "Launch cgmSetTools - a tool for working with sets in maya",                                                                                                                                       
              c=lambda *a: SETTOOLS.ui()) 
    
    
    mc.button(parent = _column,
              ut = 'cgmUITemplate',  
              l='autoTangent',
              ann = "autoTangent by Michael Comet - an oldie but a goodie for those who loathe the graph editor",                                                                                                                                   
              c=lambda *a: mel.eval('autoTangent'))
    mc.button(parent = _column,
              ut = 'cgmUITemplate',  
              l='tweenMachine',
              ann = "tweenMachine by Justin Barrett - Fun little tweening tool",                                                                                                                                                   
              c=lambda *a: mel.eval('tweenMachine'))
    mc.button(parent = _column,
              ut = 'cgmUITemplate',  
              l='mlArcTracer',
              ann = "mlArcTracer by Morgan Loomis",                                                                                                                                                                   
              c=lambda *a: ml_arcTracer.ui())         
    mc.button(parent = _column,
              ut = 'cgmUITemplate',  
              l='mlCopyAnim',
              ann = "mlCopyAnim by Morgan Loomis",                                                                                                                                                                                   
              c=lambda *a: ml_copyAnim.ui())         
    mc.button(parent = _column,
              ut = 'cgmUITemplate',  
              l='mlHold',
              ann = "mlHold by Morgan Loomis",
              c=lambda *a: ml_hold.ui())  
    mc.button(parent = _column,
              ut = 'cgmUITemplate',  
              l='red9.Studio Tools',
              ann = "Launch Red 9's tools",
              c=lambda *a:Red9.start())           


def buildTab_legacy(self,parent):
    _column = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
    parent(edit = True,
           af = [(_column,"top",0),
                 (_column,"left",0),
                 (_column,"right",0),                        
                 (_column,"bottom",0)])    

    #>>>Shape Creation ====================================================================================
    mc.setParent(_column)

    cgmUI.add_Button(_column,
                     'AnimTools',
                     lambda a:LOADTOOL.animToolsLEGACY(),
                     "Old simple anim tool holder")

    cgmUI.add_Button(_column,
                     'SetTools 1.0',
                     lambda a:LOADTOOL.setToolsLEGACY(),
                     "Old object set tool window. Crashy. Use with caution")        

    cgmUI.add_Button(_column,
                     'Locinator 1.0',
                     lambda a:LOADTOOL.locinatorLEGACY(),
                     "Original Tool for creating, updating, locators")

    cgmUI.add_Button(_column,
                     'tdTools 1.0',
                     lambda a:LOADTOOL.tdToolsLEGACY(),
                     "Series of tools for general purpose TD work - curves, naming, position, deformers") 

    cgmUI.add_Button(_column,
                     'attrTools 1.0',
                     lambda a:LOADTOOL.attrToolsLEGACY(),
                     "Old attribute tools")


def buildTab_options(self,parent):

    try:self.var_matchFrameCollapse
    except:self.create_guiOptionVar('matchFrameCollapse',defaultValue = 0)
    
    _column = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
    parent(edit = True,
           af = [(_column,"top",0),
                 (_column,"left",0),
                 (_column,"right",0),                        
                 (_column,"bottom",0)])        

    #>>>Match ====================================================================================
    _update_frame = mUI.MelFrameLayout(_column,label = 'Match Options',vis=True,
                                       collapse=self.var_matchFrameCollapse.value,
                                       collapsable=True,
                                       enable=True,
                                       useTemplate = 'cgmUIHeaderTemplate',
                                       expandCommand = lambda:self.var_matchFrameCollapse.setValue(0),
                                       collapseCommand = lambda:self.var_matchFrameCollapse.setValue(1)
                                       )	
    _update_inside = mUI.MelColumnLayout(_update_frame,useTemplate = 'cgmUISubTemplate')  


    #>>>Match mode -------------------------------------------------------------------------------------
    buildRow_matchMode(self,_update_inside)     


    #>>>Aim ====================================================================================
    """
    try:self.var_aimOptionsFrameCollapse
    except:self.create_guiOptionVar('aimFrameCollapse',defaultValue = 0)
    
    mc.setParent(_column)
    #cgmUI.add_SectionBreak()        
    _aim_frame = mUI.MelFrameLayout(_column,label = 'Aim Options',vis=True,
                                    collapse=self.var_aimOptionsFrameCollapse.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:self.var_aimOptionsFrameCollapse.setValue(0),
                                    collapseCommand = lambda:self.var_aimOptionsFrameCollapse.setValue(1)
                                    )	
    _aim_inside = mUI.MelColumnLayout(_aim_frame,useTemplate = 'cgmUISubTemplate')  """




    buildSection_objDefaults(self,_column)
    #self.buildSection_rayCast(_column)
    buildSection_animOptions(self,_column)
    
def buildRow_mesh(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Mesh:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mc.button(parent=_row,
              l = 'MeshTools',
              ut = 'cgmUITemplate',
              c = lambda *a: mc.evalDeferred(MESHTOOLS.go,lp=1),                  
              ann = "LOCATORS")    
    mc.button(parent=_row,
              l = 'abSymMesh',
              ut = 'cgmUITemplate',
              ann = "abSymMesh by Brendan Ross - fantastic tool for some blendshape work",                                                                                                       
              c=lambda *a: mel.eval('abSymMesh'),)  
    mc.button(parent=_row,
              l = 'abTwoFace',
              ut = 'cgmUITemplate',        
              ann = "abTwoFace by Brendan Ross - fantastic tool for splitting blendshapes",                                                                                                       
              c=lambda *a: mel.eval('abTwoFace'),)         

    mUI.MelSpacer(_row,w=5)                      
    _row.layout()   

def buildRow_shapeUtils(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Shape:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mc.button(parent=_row,
              l = 'Parent',
              ut = 'cgmUITemplate',
              ann = "shapeParent in place with a from:to selection. Maya's version is not so good",                                                                                                                    
              c = lambda *a:MMCONTEXT.func_process( RIGGING.shapeParent_in_place, None, 'lastFromRest','shapeParent'),
              )   
    mc.button(parent=_row,
              l = 'Combine',
              ut = 'cgmUITemplate',
              ann = "Combine selected shapes to the last transform",  
              c = lambda *a:MMCONTEXT.func_process( RIGGING.combineShapes, None, 'all', 'shapeParentAllToLast', **{'keepSource':False}),
              )           


    mc.button(parent=_row,
              ut = 'cgmUITemplate',
              l = 'Add',
              ann = "Add selected shapes to the last transform",                   
              c = lambda *a:MMCONTEXT.func_enumrate_all_to_last(RIGGING.shapeParent_in_place, None,'toFrom', **{}),
              )

    mc.button(parent=_row,
              ut = 'cgmUITemplate',
              l = 'Replace',
              ann = "Replace the last transforms shapes with the former ones.",                                                                                                                  
              c = lambda *a:MMCONTEXT.func_process(
                  RIGGING.shapeParent_in_place,
                  None,'lastFromRest', 'replaceShapes',
                  **{'replaceShapes':True}),)             

    mc.button(parent=_row,
              ut = 'cgmUITemplate',
              l = 'Extract',
              ann = "Extract selected shapes from their respective transforms",                  
              c = lambda *a:MMCONTEXT.func_context_all(RIGGING.duplicate_shape,'selection','shape'),
              )    

    mc.button(parent=_row,
              ut = 'cgmUITemplate',
              l = 'Describe',
              ann = "Generate pythonic recreation calls for selected curve shapes", 
              c =  lambda *a:MMCONTEXT.func_process( CURVES.get_python_call, None, 'all','describe'),                
              ) 
    mc.button(parent=_row,
              ut = 'cgmUITemplate',
              l = 'Match OS',
              ann = "Match the first shape to the rest | object space",                                                                                                                  
              c = lambda *a:MMCONTEXT.func_process(
                  CURVES.match,
                  None,'firstToEach', 'match curve shape',False,
                  **{'space':'os'}),)
    mc.button(parent=_row,
              ut = 'cgmUITemplate',
              l = 'Match WS',
              ann = "Match the first shape to the rest | World space",                                                                                                                  
              c = lambda *a:MMCONTEXT.func_process(
                  CURVES.match,
                  None,'firstToEach', 'match curve shape',False,
                  **{'space':'ws'}),)    


    mUI.MelSpacer(_row,w=5)                      
    _row.layout()   

def buildRow_skin(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='skin:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mc.button(parent=_row,
              l='Get Joints',
              ut = 'cgmUITemplate',
              ann = "Select skinned joints from cluster",                                                                                                                       
              c = cgmGen.Callback(MMCONTEXT.func_process, SKIN.get_influences_fromSelected))           


    mc.button(parent=_row,
              l='Copy',
              ut = 'cgmUITemplate',
              ann = "Copy skin weights based on targets",                                                                                                                       
              c = cgmGen.Callback(MMCONTEXT.func_process, SKIN.transfer_fromTo, None, 'firstToRest','Copy skin weights',True,**{}))           

    mc.button(parent=_row,
              l='abWeightLifter',
              ut = 'cgmUITemplate',
              ann = "abWeightLifter by Brendan Ross - really good tool for transferring and working with skin data",                                                                                                                       
              c=lambda *a: mel.eval('abWeightLifter'),)         
    mc.button(parent=_row,
              l='ngSkinTools',
              ut = 'cgmUITemplate',
              ann = "Read the docs. Give it a chance. Be amazed.",                                                                                                                       
              c=lambda *a: LOADTOOL.ngskin())           

    mUI.MelSpacer(_row,w=5)                      
    _row.layout()   

def buildRow_SDK(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='SDK:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mc.button(parent = _row,
              ut = 'cgmUITemplate',                                                                                                
              l='Driven',
              ann = "Get driven objects from a sdk driver",                                                        
              c=lambda *a:SDK.get_driven(None,getPlug=False))
    mc.button(parent = _row,
              ut = 'cgmUITemplate',                                                                                                
              l='Driven Plugs',
              ann = "Get driven plugs from a sdk driver",                                                        
              c=lambda *a:SDK.get_driven(None,getPlug=True))

    mc.button(parent = _row,
              ut = 'cgmUITemplate',                                                                                                
              l='Driver',
              ann = "Get driver objects from a sdk driver",                                                        
              c=lambda *a:SDK.get_driver(None,getPlug=False))
    mc.button(parent = _row,
              ut = 'cgmUITemplate',                                                                                                
              l='Driver Plugs',
              ann = "Get driver plugs from a sdk driver",                                                        
              c=lambda *a:SDK.get_driver(None,getPlug=True))

    mc.button(parent = _row,
              ut = 'cgmUITemplate',                                                                                                
              l='seShapeTaper',
              ann = "Fantastic blendtaper like tool for sdk poses by our pal - Scott Englert",                                                        
              c=lambda *a: mel.eval('seShapeTaper'),)   

    mUI.MelSpacer(_row,w=5)                      
    _row.layout()   
    
def buildRow_cleanNodes(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Clean Nodes:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mc.button(parent = _row,
              ut = 'cgmUITemplate',                                                                                                
              l='Mental Ray',
              ann = "Clean Mental Ray nodes",                                                        
              c=lambda *a:NODES.renderer_clean('Mayatomr',True))
 
    mUI.MelSpacer(_row,w=5)                      
    _row.layout()   

def buildRow_constraints(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Constraints:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mc.button(parent=_row,
              l='Get Targets',
              ut = 'cgmUITemplate',
              ann = "Get targets of contraints",                                                                                                                       
              c = cgmGen.Callback(MMCONTEXT.func_process, CONSTRAINTS.get_targets, None, 'each','Get targets',True,**{'select':True}))           

    mUI.MelSpacer(_row,w=5)                      
    _row.layout()

def buildRow_attachBy(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Attach by:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    d_modes = {'parent':'prnt',
               'parentGroup':'prntGrp',
               'conPointGroup':'pntCon',
               'conPointOrientGroup':'pntOrntCon',
               'conParentGroup':'prntCon'}

    for m,l in d_modes.iteritems():
        mc.button(parent=_row,
                  l= l,
                  ut = 'cgmUITemplate',
                  ann = "Attach each to last by {0}".format(m),
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGCONSTRAINTS.attach_toShape, None,'eachToLast',**{'connectBy':m}))

    mUI.MelSpacer(_row,w=5)                      
    _row.layout()   

def buildRow_skinDat(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='skinDat:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mc.button(parent=_row,
              l='Write',
              ut = 'cgmUITemplate',
              ann = "Write skinDat data",
              c = lambda *a:SKINDAT.data().write())
            #c = cgmGen.Callback(MMCONTEXT.func_process, SKINDAT.data, None, 'each','Get targets',True,**{'select':True}))           

    mUI.MelSpacer(_row,w=5)                      
    _row.layout()   

def buildRow_resizeObj(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='resizeObj:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mc.button(parent=_row,
              ut = 'cgmUITemplate',                  
              l = 'Make resizeObj',
              ann = 'Make control a resize object so you can more easily shape it',                
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_controlResizeObj, None,'each','Resize obj'))        
    mc.button(parent=_row,
              ut = 'cgmUITemplate', 
              l = 'Push resizeObj changes',
              ann = 'Push the control changes back to control',
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.push_controlResizeObj, None,'each','Resize obj'))        
    _row.layout() 

def buildRow_mirrorCurve(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='mirror:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mc.button(parent=_row,
              ut = 'cgmUITemplate',  
              l = 'Mirror World Space To target',
              ann = 'Given a selection of two curves, mirror across X (for now only x)',
              c = cgmGen.Callback(CURVES.mirror_worldSpace))                   
    _row.layout()   


def buildRow_aimMode(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Aim Mode:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    uiRC = mUI.MelRadioCollection()

    _on = self.var_aimMode.value

    for i,item in enumerate(['local','world','matrix']):
        if item == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row,label=item,sl=_rb,
                          onCommand = cgmGen.Callback(self.var_aimMode.setValue,item))

        mUI.MelSpacer(_row,w=2)       


    _row.layout()      


def buildRow_matchMode(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Match Mode:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    uiRC = mUI.MelRadioCollection()

    _on = self.var_matchMode.value

    for i,item in enumerate(['point','orient','point/orient']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row,label=item,sl=_rb,
                          onCommand = cgmGen.Callback(LOCINATOR.uiFunc_change_matchMode,self,i))

        mUI.MelSpacer(_row,w=2)       

    _row.layout()

def buildRow_context(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Context:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    uiRC = mUI.MelRadioCollection()

    _on = self.var_contextTD.value

    for i,item in enumerate(['selection','children','heirarchy','scene']):
        if item == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row,label=item,sl=_rb,
                          onCommand = cgmGen.Callback(self.var_contextTD.setValue,item))

        mUI.MelSpacer(_row,w=2)       

    _row.layout()

def buildRow_color(self,parent):
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row,w=5)
    mUI.MelLabel(_row,l="Options:")
    _row.setStretchWidget( mUI.MelSeparator(_row) )            


    _cb_push = mUI.MelCheckBox(_row,en=True,
                               v = True,
                               label = 'push',
                               ann='Push color changes to shapes? If not, only first shape or selected shapes will be colored') 


    mc.button(parent = _row,
              ut = 'cgmUITemplate',                                                                                                
              l='Clear Override*',
              ann = "Clear override settings on contextual objects.",                                                                                                                                       
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.override_clear, None, 'each','Clear override',True,**{'context':None}))           

    mUI.MelSpacer(_row,w=5)        
    _row.layout()


    mc.setParent(parent)
    _b_idxOnly = False
    if cgmGen.__mayaVersion__ < 2016:
        _b_idxOnly = True        

    #_row_index = mUI.MelColumnLayout(parent)
    #mc.columnLayout(columnAttach = ('both',5),backgroundColor = [.2,.2,.2])
    cgmUI.add_Header('Index*')        

    #_row = mUI.MelRow(parent,ut='cgmUISubTemplate')

    mUI.MelGridLayout(parent = parent, aec = False, numberOfRowsColumns=(2,10), cwh = (27,14),cr=True)

    colorSwatchesList = [1,2,3,11,24,21,12,10,25,4,13,20,8,30,9,5,6,18,15,29,28,7,27,19,23,26,14,17,22,16]
    #for l in splitList:
        #r= mUI.MelGridLayout(parent = parent, aec = False, numberOfRowsColumns=(1,10), cwh = (27,14),cr=True)
        #r = mUI.MelHLayout(parent, height = 15)
    for i in colorSwatchesList:
        colorBuffer = mc.colorIndex(i, q=True)
        mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=colorBuffer, 
                  pc = cgmGen.Callback(uiFunc_colorShape,**{'index':i,'cb_push':_cb_push}),                                 
                  #pc = cgmGen.Callback(self.uiFunc_colorShape,_cb_push,**{'index':i}),
                  #pc = cgmGen.Callback(MMCONTEXT.color_override,i,None,'shape'),                        
                  annotation = 'Sets the color of the object to this')
        #r.layout()


    #_row.layout() 
    #_row_rbg
    mc.setParent(parent)
    if not _b_idxOnly:
        cgmUI.add_Header('RGB*')

        #_row = mUI.MelRow(parent,ut='cgmUISubTemplate')

        mUI.MelGridLayout(parent,aec = False, numberOfRowsColumns=(2,10), cwh = (27,14),cr=True)

        _IndexKeys = SHARED._d_colorSetsRGB.keys()
        i = 0
        for k1 in _IndexKeys:
            _keys2 = SHARED._d_colorSetsRGB.get(k1,[])
            _sub = False
            if _keys2:_sub = True
            colorBuffer = SHARED._d_colors_to_RGB[k1]
            mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=colorBuffer,
                      pc = cgmGen.Callback(uiFunc_colorShape, **{'rgb':SHARED._d_colors_to_RGB[k1],'cb_push':_cb_push}),                                
                      #pc = cgmGen.Callback(self.uiFunc_colorShape,_cb_push,**{'rgb':SHARED._d_colors_to_RGB[k1]}),                          
                      #pc = cgmGen.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[k1],None,'shape'),                        
                      annotation = 'Sets color by rgb to {0}'.format(k1))            

            i+=1

            if _sub:                  
                for k2 in _keys2:
                    _buffer = "{0}{1}".format(k1,k2)
                    #log.info( SHARED._d_colors_to_RGB[_buffer] )
                    mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=SHARED._d_colors_to_RGB[_buffer],     
                              pc = cgmGen.Callback(uiFunc_colorShape, **{'rgb':SHARED._d_colors_to_RGB[_buffer],'cb_push':_cb_push}),                                                                  
                              #pc = cgmGen.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[_buffer],None,'shape'),                        
                              annotation = 'Sets color by rgb to {0}{1}'.format(k1,k2))            
                    i+=1

        mc.setParent(parent)
    cgmUI.add_Header('Side defaults*')
    buildRow_colorControls(self,parent)

def buildRow_colorControls(self,parent):
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate')
    mUI.MelSpacer(_row,w=5)

    _b_idxOnly = False
    if cgmGen.__mayaVersion__ < 2016:
        _b_idxOnly = True

    _cb_rgb = mUI.MelCheckBox(_row,en=not _b_idxOnly,
                              label = 'rgb',
                              v = not _b_idxOnly,
                              ann='Use rgb rather than index values')
    _cb_geo = mUI.MelCheckBox(_row,en=True,
                              v = False,
                              label = 'geo',
                              ann='Setup shaders or just wireframe overrides on geo targets')           
    _cb_push = mUI.MelCheckBox(_row,en=True,
                               v = True,
                               label = 'push',
                               ann='Push color changes to shapes? If not, only first shape or selected shapes will be colored') 

    uiGrid_colorSwatch_index = mc.gridLayout(aec = False, numberOfRowsColumns=(1,9), cwh = (25,20),cr=True)

    i = 0
    for side in ['left','center','right']:
        for typ in ['main','sub','aux']:
            colorName = SHARED._d_side_colors[side][typ]
            colorBuffer = SHARED._d_colors_to_RGB.get(colorName,[0,0,0])
            mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=colorBuffer, 
                      pc = cgmGen.Callback(uiFunc_colorControl,self,side,typ,_cb_geo,_cb_rgb,_cb_push),                        
                      #pc = cgmGen.Callback(MMCONTEXT.func_process,RIGGING.colorControl,None,'each',noSelect = False,**{'direction':side,'controlType':typ, 'transparent':True}),                        
                      #pc = lambda *a: MMCONTEXT.func_process(RIGGING.colorControl,None,'each',noSelect = False,**{'direction':side,'controlType':typ, 'shaderSetup':_cb_geo.getValue(),'transparent':True}),                                                  
                      annotation = 'Sets color to for {0} {1} default'.format(side,typ))    

            i+=1

    #RIGGING.colorControl(shaderSetup=,transparent=,rgb =True)        
    _row.setStretchWidget( mUI.MelSeparator(_row) )     
    mc.button(parent = _row,
              ut = 'cgmUITemplate',                                                                                                
              l='Clr*',
              ann = "Clear override settings on contextual objects.",    
              #c = lambda *a:MMCONTEXT.func_process( RIGGING.override_clear, None, 'each','Clear override',True,**{'context':None}))                             
              c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.override_clear, None, 'each','Clear override',True,**{'context':None}))           

    mUI.MelSpacer(_row,w=5)  

    _row.layout()
    return

def uiPopup_createColor(self):
    if self.uiPopUpMenu_color:
        self.uiPopUpMenu_color.clear()
        self.uiPopUpMenu_color.delete()
        self.uiPopUpMenu_color = None

    self.uiPopUpMenu_color = mUI.MelPopupMenu(self.uiField_shapeColor,button = 1)
    _popUp = self.uiPopUpMenu_color 

    mUI.MelMenuItem(_popUp,
                    label = "Set Color",
                    en=False)     
    mUI.MelMenuItemDiv(_popUp)

    for k,l in SHARED._d_colorsByIndexSets.iteritems():
        _k = mUI.MelMenuItem(_popUp,subMenu = True,
                             label = k,
                             en=True)
        for o in l:
            mUI.MelMenuItem(_k,
                            label = o,
                            ann = "Set the create color to: {0}".format(o),
                            c=cgmGen.Callback(cb_setCreateColor,self,o))

def uiPopup_createAttr(self):
    if self.uiPopUpMenu_attr:
        self.uiPopUpMenu_attr.clear()
        self.uiPopUpMenu_attr.delete()
        self.uiPopUpMenu_attr = None

    self.uiPopUpMenu_attr = mUI.MelPopupMenu(self.uiField_attrType,button = 1)
    _popUp = self.uiPopUpMenu_attr 

    mUI.MelMenuItem(_popUp,
                    label = "Set Attr Type",
                    en=False)     
    mUI.MelMenuItemDiv(_popUp)

    for a in ATTR._l_simpleTypes:
        mUI.MelMenuItem(_popUp,
                        label = a,
                        ann = "Set the create attr to: {0}".format(a),
                        c=cgmGen.Callback(cb_setCreateAttr,self,a))

def uiPopup_createRayCast(self):
    if self.uiPopUpMenu_raycastCreate:
        self.uiPopUpMenu_raycastCreate.clear()
        self.uiPopUpMenu_raycastCreate.delete()
        self.uiPopUpMenu_raycastCreate = None

    self.uiPopUpMenu_raycastCreate = mUI.MelPopupMenu(self.uiField_rayCastCreate,button = 1)
    _popUp = self.uiPopUpMenu_raycastCreate 

    mUI.MelMenuItem(_popUp,
                    label = "Set Create Type",
                    en=False)     
    mUI.MelMenuItemDiv(_popUp)

    for m in  ['locator','joint','jointChain','curve','duplicate','vectorLine','data']:
        mUI.MelMenuItem(_popUp,
                        label = m,
                        ann = "Create {0} by rayCasting".format(m),
                        c=cgmGen.Callback(cb_setRayCastCreate,self,m))

def uiPopup_createShape(self):
    if self.uiPopUpMenu_createShape:
        self.uiPopUpMenu_createShape.clear()
        self.uiPopUpMenu_createShape.delete()
        self.uiPopUpMenu_createShape = None

    self.uiPopUpMenu_createShape = mUI.MelPopupMenu(self.uiField_shape,button = 1)
    _popUp = self.uiPopUpMenu_createShape 

    mUI.MelMenuItem(_popUp,
                    label = "Set shape",
                    en=False)     
    mUI.MelMenuItemDiv(_popUp)

    for k,l in CURVES._d_shapeLibrary.iteritems():
        _k = mUI.MelMenuItem(_popUp,subMenu = True,
                             label = k,
                             en=True)
        for o in l:
            mUI.MelMenuItem(_k,
                            label = o,
                            ann = "Set the create shape to: {0}".format(o),
                            c=cgmGen.Callback(cb_setCreateShape,self,o))  
            
def cb_setCreateShape(self,shape):
    self.var_curveCreateType.setValue(shape)
    self.uiField_shape(edit=True,label=shape)
    return True

def cb_setCreateColor(self,color):
    self.var_defaultCreateColor.setValue(color)
    self.uiField_shapeColor(edit=True,label=color)
    return True
def cb_setCreateAttr(self,attr):
    self.var_attrCreateType.setValue(attr)
    self.uiField_attrType(edit=True,label=attr)
    return True

def cb_setRayCastCreate(self,m):
    self.var_createRayCast.setValue(m)
    self.uiField_rayCastCreate(edit=True,label=m)
    return True


def uiFunc_colorControl(self,side,controlType,cb_geo,cb_rgb,cb_push):
    #'direction':side,'controlType':typ, 'shaderSetup':_cb_geo.getValue()
    
    MMCONTEXT.func_process(RIGGING.colorControl,None,'each',
                           noSelect = False,
                           **{'direction':side,'controlType':controlType,
                              'rgb':cb_rgb.getValue(),
                              'pushToShapes':cb_push.getValue(),
                              'shaderSetup':cb_geo.getValue(),'transparent':True}), 
    
def uiFunc_colorShape(cb_push = None,key=None,index=None,rgb=None):
    MMCONTEXT.func_process(RIGGING.override_color,None,'each',
                           noSelect = False,
                           **{'key':key,
                              'index':index,
                              'rgb':rgb,
                              'pushToShapes':cb_push.getValue()})