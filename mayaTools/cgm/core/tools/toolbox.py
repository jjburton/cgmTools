"""
------------------------------------------
toolbox: cgm.core.tools
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__version__ = '0.1.08172017'

import webbrowser

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import maya.cmds as mc
import maya
import maya.mel as mel

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
reload(MESHTOOLS)
from cgm.core.lib import node_utils as NODES
from cgm.core.tools import attrTools as ATTRTOOLS
from cgm.core.tools import dynParentTool as DYNPARENTTOOL

import cgm.core.tools.locinator as LOCINATOR
import cgm.core.lib.arrange_utils as ARRANGE
import cgm.core.lib.rigging_utils as RIGGING
import cgm.core.classes.GuiFactory as cgmUI
reload(cgmUI)
mUI = cgmUI.mUI

_2016 = False
if cgmGen.__mayaVersion__ >=2016:
    _2016 = True

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmToolbox'    
    WINDOW_TITLE = 'cgmToolbox 2.0 - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 400,350
    TOOLNAME = 'toolbox.ui'
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

        self.create_guiOptionVar('matchFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('rayCastFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('aimFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('objectDefaultsFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('shapeFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('snapFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('tdFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('animFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('layoutFrameCollapse',defaultValue = 0) 


        self.var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode', defaultValue = 'world')   

        self.var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
        self.var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
        self.var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
        self.var_createSizeMode = cgmMeta.cgmOptionVar('cgmVar_createSizeMode', defaultValue=0)
        self.var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)
        self.var_createSizeMulti = cgmMeta.cgmOptionVar('cgmVar_createSizeMultiplierValue', defaultValue=1.25)


        self.var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
        self.var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)
        self.var_objDefaultOutAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultOutAxis', defaultValue = 3)

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
        self.uiMenu_FirstMenu = mUI.MelMenu(l='File', pmc = cgmGen.Callback(self.buildMenu_first))
        self.uiMenu_Buffers = mUI.MelMenu( l='Buffers', pmc = cgmGen.Callback(self.buildMenu_buffer))

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

        ui_tabs = mUI.MelTabLayout( _MainForm)

        #uiTab_setup = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        #self.uiTab_setup = uiTab_setup

        uiTab_options = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')       
        uiTab_tools = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')

        for i,tab in enumerate(['Options','Tools']):
            ui_tabs.setLabel(i,tab)

        self.buildTab_options(uiTab_options)
        self.buildTab_tools(uiTab_tools)
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

    def buildSection_shape(self,parent):
        _shapes_frame = mUI.MelFrameLayout(parent,label = 'Shape Creation',vis=True,
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


        self.uiPopup_createShape()
        self.uiPopup_createColor()


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
                         lambda *a:uiFunc_createCurve(),
                         'Create control curves from stored optionVars. Shape: {0} | Color: {1} | Direction: {2}'.format(self.var_curveCreateType.value,
                                                                                                                         self.var_defaultCreateColor.value,
                                                                                                                         SHARED._l_axis_by_string[self.var_createAimAxis.value]))                    
        #mUI.MelSpacer(_row_curveCreate,w=10)                                              
        cgmUI.add_Button(_row_curveCreate,'One of each',
                         lambda *a:uiFunc_createOneOfEach(),
                         'Create one of each curve stored in cgm libraries. Size: {0} '.format(self.var_createSizeValue.value) )       

        _row_curveCreate.layout()  

    def buildSection_snap(self,parent):
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

        _row_base.layout() 
        
        #>>>Aim snap -------------------------------------------------------------------------------------
        _row_aim = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        
        mc.button(parent=_row_aim,
                  l = 'Aim',
                  ut = 'cgmUITemplate',                                    
                  c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
                  ann = "Aim snap in a from:to selection")

        mc.button(parent=_row_aim,
                  ut = 'cgmUITemplate',                  
                  l = 'All to last',
                  c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
                  ann = "Aim all objects to the last in selection")
        
        mc.button(parent=_row_aim,
                  ut = 'cgmUITemplate',                  
                  l = 'Selection Order',
                  c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToNext'),
                  ann = "Aim in selection order from each to next")
        
        mc.button(parent=_row_aim,
                  ut = 'cgmUITemplate',                                    
                  l = 'First to Mid',
                  c = lambda *a:SNAPCALLS.snap_action(None,'aim','firstToRest'),
                  ann = "Aim the first object to the midpoint of the rest")    

        _row_aim.layout() 
        
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
        _row_ray.layout()             
        
        #>>>Match snap -------------------------------------------------------------------------------------
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
        mUI.MelSpacer(_row_arrange,w=5)                                              
        _row_arrange.layout()         

    def buildSection_rigging(self,parent):
        _frame = mUI.MelFrameLayout(parent,label = 'Rigging Utils',vis=True,
                                    collapse=self.var_tdFrameCollapse.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:self.var_tdFrameCollapse.setValue(0),
                                    collapseCommand = lambda:self.var_tdFrameCollapse.setValue(1)
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
        
        
        #>>>Create -------------------------------------------------------------------------------------
        _row_create = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_create,w=5)                                              
        mUI.MelLabel(_row_create,l='Create from selected:')
        _row_create.setStretchWidget(mUI.MelSeparator(_row_create)) 
        
        mc.button(parent=_row_create,
                  ut = 'cgmUITemplate',                    
                  l = 'Transform',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'each','Create Tranform',**{'create':'null'}))    
        
        mc.button(parent=_row_create,
                  ut = 'cgmUITemplate',                                        
                  l = 'Joint',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_joint_at, None,'each','Create Joint'))         
        mc.button(parent=_row_create,
                  ut = 'cgmUITemplate',                                        
                  l = 'Locator',
                  c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, None,'each','Create Loc'))                          
        mc.button(parent=_row_create,
                  ut = 'cgmUITemplate',                                        
                  l = 'Curve',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Curve',**{'create':'curve'}))                          
        
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
        


    def buildTab_tools(self,parent):
        _column = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
        parent(edit = True,
               af = [(_column,"top",0),
                     (_column,"left",0),
                     (_column,"right",0),                        
                     (_column,"bottom",0)])    

        #>>>Shape Creation ====================================================================================
        mc.setParent(_column)
        
        #>>>Tools -------------------------------------------------------------------------------------        
        cgmUI.add_SectionBreak()        
        _row_tools1 = mUI.MelHLayout(_column,ut='cgmUISubTemplate',padding = 5)
    
        mc.button(parent=_row_tools1,
                  l = 'DynParent Tool',
                  ut = 'cgmUITemplate',
                  c= cgmGen.Callback(DYNPARENTTOOL.ui),
                  ann = "Tool for modifying and setting up dynamic parent groups")
    
        mc.button(parent=_row_tools1,
                  l = 'Locinator',
                  ut = 'cgmUITemplate',
                  c= cgmGen.Callback(LOCINATOR.ui),
                  ann = "LOCATORS")
    
        mc.button(parent=_row_tools1,
                  l = 'AttrTools',
                  ut = 'cgmUITemplate',
                  c= cgmGen.Callback(ATTRTOOLS.ui),
                  ann = "Do stuff with attributes!")
    
        mc.button(parent=_row_tools1,
                  l = 'MeshTools',
                  ut = 'cgmUITemplate',
                  c= cgmGen.Callback(MESHTOOLS.go),
                  ann = "LOCATORS")
    
        _row_tools1.layout()          
        
        
        cgmUI.add_SectionBreak()
        self.buildSection_snap(_column)
        self.buildSection_shape(_column)
        self.buildSection_rigging(_column)


    def buildTab_options(self,parent):
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
        _row = mUI.MelHSingleStretchLayout(_update_inside,ut='cgmUISubTemplate',padding = 5)

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


        #>>>Aim ====================================================================================
        mc.setParent(_column)
        cgmUI.add_SectionBreak()        
        _aim_frame = mUI.MelFrameLayout(_column,label = 'Aim Options',vis=True,
                                        collapse=self.var_aimFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_aimFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_aimFrameCollapse.setValue(1)
                                        )	
        _aim_inside = mUI.MelColumnLayout(_aim_frame,useTemplate = 'cgmUISubTemplate')  


        #>>>Aim mode -------------------------------------------------------------------------------------
        _row_aimFlags = mUI.MelHSingleStretchLayout(_aim_inside,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row_aimFlags,w=5)                      
        mUI.MelLabel(_row_aimFlags,l='Aim Mode:')
        _row_aimFlags.setStretchWidget( mUI.MelSeparator(_row_aimFlags) )

        uiRC = mUI.MelRadioCollection()

        _on = self.var_aimMode.value

        for i,item in enumerate(['local','world','matrix']):
            if item == _on:
                _rb = True
            else:_rb = False

            uiRC.createButton(_row_aimFlags,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(self.var_aimMode.setValue,item))

            mUI.MelSpacer(_row_aimFlags,w=2)       


        _row_aimFlags.layout()



        #>>>Obj Defaults ====================================================================================
        mc.setParent(_column)
        cgmUI.add_SectionBreak()
        _defaults_frame = mUI.MelFrameLayout(_column,label = 'Object Defaults Options',vis=True,
                                             collapse=self.var_objectDefaultsFrameCollapse.value,
                                             collapsable=True,
                                             enable=True,
                                             useTemplate = 'cgmUIHeaderTemplate',
                                             expandCommand = lambda:self.var_objectDefaultsFrameCollapse.setValue(0),
                                             collapseCommand = lambda:self.var_objectDefaultsFrameCollapse.setValue(1)
                                             )	
        _defaults_inside = mUI.MelColumnLayout(_defaults_frame,useTemplate = 'cgmUISubTemplate')  


        #>>>Aim defaults mode -------------------------------------------------------------------------------------
        _d = {'aim':self.var_objDefaultAimAxis,
              'up':self.var_objDefaultUpAxis,
              'out':self.var_objDefaultOutAxis}

        for k in _d.keys():
            _var = _d[k]

            _row = mUI.MelHSingleStretchLayout(_defaults_inside,ut='cgmUISubTemplate',padding = 5)

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
        _row_defaults = mUI.MelHLayout(_defaults_inside,ut='cgmUISubTemplate',padding = 5, )

        cgmUI.add_Button(_row_defaults,'Tag selected for aim',
                         lambda *a:MMCONTEXT.func_process(SNAP.verify_aimAttrs, mc.ls(sl=True),'each','Verify aim attributes',True,**{}),)                                       
        _row_defaults.layout() 


        #>>>Raycast ====================================================================================
        mc.setParent(_column)
        cgmUI.add_SectionBreak()
        _raycast_frame = mUI.MelFrameLayout(_column,label = 'RayCast Options',vis=True,
                                            collapse=self.var_rayCastFrameCollapse.value,
                                            collapsable=True,
                                            enable=True,
                                            useTemplate = 'cgmUIHeaderTemplate',
                                            expandCommand = lambda:self.var_rayCastFrameCollapse.setValue(0),
                                            collapseCommand = lambda:self.var_rayCastFrameCollapse.setValue(1)
                                            )	
        _raycast_inside = mUI.MelColumnLayout(_raycast_frame,useTemplate = 'cgmUISubTemplate') 


        #>>>Cast Mode  -------------------------------------------------------------------------------------
        uiRC = mUI.MelRadioCollection()
        _on = self.var_rayCastMode.value

        _row1 = mUI.MelHSingleStretchLayout(_raycast_inside,ut='cgmUISubTemplate',padding = 5)


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

        _row_offset = mUI.MelHSingleStretchLayout(_raycast_inside,ut='cgmUISubTemplate',padding = 5)
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

        _row_orient = mUI.MelHSingleStretchLayout(_raycast_inside,ut='cgmUISubTemplate',padding = 5)
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

        _row_orient.layout()        







    def cb_setCreateShape(self,shape):
        self.var_curveCreateType.setValue(shape)
        self.uiField_shape(edit=True,label=shape)
        return True

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
                                c=cgmGen.Callback(self.cb_setCreateShape,o))  

    def cb_setCreateColor(self,color):
        self.var_defaultCreateColor.setValue(color)
        self.uiField_shapeColor(edit=True,label=color)
        return True

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
                                c=cgmGen.Callback(self.cb_setCreateColor,o))

        """
        self.var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])            
        #self.var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
        self.var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffset', defaultValue=0)
        self.var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0) 
        self.var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)
        #self.var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)        





        return

uiMenuAim = mc.menuItem( parent = uiMenu_objDefault, l='Obj Aim', subMenu=True)    
                uiRC = mc.radioMenuItemCollection(parent = uiMenuAim)

                #self.uiOptions_menuMode = []		
                _v = self.var_objDefaultAimAxis.value

                for i,item in enumerate(SHARED._l_axis_by_string):
                    if i == _v:
                        _rb = True
                    else:_rb = False
                    mc.menuItem(parent = uiMenuAim,collection = uiRC,
                                label=item,   
                                c = cgmGen.Callback(self.var_objDefaultAimAxis.setValue,i),
                                rb = _rb)  
"""
def uiFunc_createOneOfEach():
    var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)        
    CURVES.create_oneOfEach(var_createSizeValue.value)

def uiFunc_createCurve():
    reload(CURVES)
    var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
    var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
    var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
    var_createSizeMode = cgmMeta.cgmOptionVar('cgmVar_createSizeMode', defaultValue=0)
    var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)
    var_createSizeMulti = cgmMeta.cgmOptionVar('cgmVar_createSizeMultiplierValue', defaultValue=1.25)        
    CURVES.create_controlCurve(mc.ls(sl=True),
                               var_curveCreateType.value,
                               var_defaultCreateColor.value,
                               var_createSizeMode.value,
                               var_createSizeValue.value,
                               var_createSizeMulti.value,
                               SHARED._l_axis_by_string[var_createAimAxis.value])
def uiSetupOptionVars_curveCreation(self):
    self.var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
    self.var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
    self.var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
    self.var_createSizeMode = cgmMeta.cgmOptionVar('cgmVar_createSizeMode', defaultValue=0)
    self.var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)
    self.var_createSizeMulti = cgmMeta.cgmOptionVar('cgmVar_createSizeMultiplierValue', defaultValue=1.25) 
