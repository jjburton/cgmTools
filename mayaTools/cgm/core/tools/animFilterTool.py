"""
------------------------------------------
baseTool: cgm.core.tools
Author: David Bokser
email: dbokser@cgmonks.com

Website : http://www.cgmonastery.com
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

from cgm.core.tools import dragger as DRAGGER
from cgm.core.tools import trajectoryAim as TRAJECTORYAIM
from cgm.core.tools import keyframeToMotionCurve as K2MC
from cgm.core.tools import spring as SPRING

#>>> Root settings =============================================================
__version__ = '0.1.20.7.23'
__toolname__ ='postFilter'

_padding = 5

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

        #self.l_allowedDockAreas = []
        self.WINDOW_TITLE = self.__class__.WINDOW_TITLE
        self.DEFAULT_SIZE = self.__class__.DEFAULT_SIZE

        self._optionDict = {
            #'mode' : 'position',
            #'plane' : 'screen',
            #'planeObject' : None,
            'aimFwd' : 'z+',
            'aimUp' : 'y+'#,
            #'loopTime' : False,
            #'debug' : False,
            #'postBlendFrames' : 6,
            #'recordMode' : 'replace'
        }

 
    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))

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
        #self._d_uiCheckBoxes = {}
    
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
        

def buildColumn_main(self,parent, asScroll = False):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """   
    if asScroll:
        _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUISubTemplate') 
    else:
        _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
    
    #>>>Objects Load Row ---------------------------------------------------------------------------------------
    uiFunc_build_post_process_column(self,_inside)
    
    return _inside
    
def uiFunc_clear_loaded(self):
    _str_func = 'uiFunc_clear_loaded'  
    self._mTransformTarget = False
    #self._mGroup = False
    self.uiTF_objLoad(edit=True, l='',en=False)      
    #self.uiField_report(edit=True, l='...')
    #self.uiReport_objects()
    #self.uiScrollList_parents.clear()
    
    #for o in self._l_toEnable:
        #o(e=True, en=False)  
     
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

def uiFunc_build_post_process_column(self, parentColumn):   
    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()

    # Post Process Action
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)
    self._post_row_aimDirection = _row

    mUI.MelSpacer(_row,w=_padding)                          
    mUI.MelLabel(_row,l='Action:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    actions = ['Dragger', 'Spring', 'Trajectory Aim', 'Keys to Motion Curve']

    self.post_actionMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAction,self))
    for dir in actions:
        self.post_actionMenu.append(dir)
    
    self.post_actionMenu.setValue(actions[0])

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Post Process Action

    # Post Process Options Frame
    #
    self._postProcessOptionsColumn = mUI.MelColumnLayout(parentColumn,useTemplate = 'cgmUISubTemplate') 
    #
    # Post Process Options Frame

    uiFunc_setPostAction(self)
 
def uiFunc_setPostAction(self):
    postAction = self.post_actionMenu.getValue()

    if postAction == 'Dragger':
        uiFunc_build_post_dragger_column(self)
    elif postAction == 'Spring':
        uiFunc_build_post_spring_column(self)
    elif postAction == 'Trajectory Aim':
        uiFunc_build_post_trajectory_aim_column(self)
    elif postAction == 'Keys to Motion Curve':
        uiFunc_build_post_keyframe_to_motion_curve_column(self) 

def uiFunc_build_post_dragger_column(self):
    parentColumn = self._postProcessOptionsColumn

    parentColumn.clear()

    # Aim
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)
    self._post_row_aimDirection = _row

    mUI.MelSpacer(_row,w=_padding)                          
    mUI.MelLabel(_row,l='Aim:')  

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    directions = ['x+', 'x-', 'y+', 'y-', 'z+', 'z-']

    mUI.MelLabel(_row,l='Fwd:') 

    self.post_fwdMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    for dir in directions:
        self.post_fwdMenu.append(dir)
    
    self.post_fwdMenu.setValue(self._optionDict['aimFwd'])

    mUI.MelSpacer(_row,w=_padding)
    
    mUI.MelLabel(_row,l='Up:')

    self.post_upMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    for dir in directions:
        self.post_upMenu.append(dir)

    self.post_upMenu.setValue(self._optionDict['aimUp'])

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Aim

    # Post Damp
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Damp:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.uiFF_post_damp = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=3.0)

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Damp

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

    # Post Object Scale
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Object Scale:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.uiFF_post_object_scale = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=10.0)

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Object Scale

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

    # Debug
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)

    mUI.MelLabel(_row,l='Additional Options:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mUI.MelLabel(_row,l='Debug:')

    self.uiCB_post_debug = mUI.MelCheckBox(_row,en=True,
                               v = False,
                               label = '',
                               ann='Debug locators will not be deleted so you could see what happened')


    mUI.MelLabel(_row,l='Show Bake:')

    self.uiCB_post_show_bake = mUI.MelCheckBox(_row,en=True,
                               v = False,
                               label = '',
                               ann='Show the bake process')


    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Debug

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

    # Bake Dragger Button
    #
    _row = mUI.MelHLayout(parentColumn,ut='cgmUISubTemplate',padding = _padding*2)
    
    cgmUI.add_Button(_row,'Bake Dragger',
        cgmGEN.Callback(uiFunc_bake_dragger,self),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Bake Dragger',h=30)

    _row.layout()   
    #
    # End Bake Dragger Button

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

def uiFunc_build_post_spring_column(self):
    parentColumn = self._postProcessOptionsColumn

    parentColumn.clear()

    # Aim
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)
    self._post_row_aimDirection = _row

    mUI.MelSpacer(_row,w=_padding)                          
    mUI.MelLabel(_row,l='Aim:')  

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    directions = ['x+', 'x-', 'y+', 'y-', 'z+', 'z-']

    mUI.MelLabel(_row,l='Fwd:') 

    self.post_fwdMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    for dir in directions:
        self.post_fwdMenu.append(dir)
    
    self.post_fwdMenu.setValue(self._optionDict['aimFwd'])

    mUI.MelSpacer(_row,w=_padding)
    
    mUI.MelLabel(_row,l='Up:')

    self.post_upMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    for dir in directions:
        self.post_upMenu.append(dir)

    self.post_upMenu.setValue(self._optionDict['aimUp'])

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Aim

    # Spring
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Spring Force:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.uiFF_post_spring = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=1.0)

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Spring

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

    # Post Damp
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Damp:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.uiFF_post_damp = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=.1)

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Damp

    # Spring
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Angular Spring Force:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.uiFF_post_angularSpring = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=1.0)

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Spring

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

    # Post Damp
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Angular Damp:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.uiFF_post_angularDamp = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=.1)

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Damp

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

    # Post Object Scale
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Object Scale:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.uiFF_post_object_scale = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=10.0)

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Object Scale

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

    # Debug
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)

    mUI.MelLabel(_row,l='Additional Options:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mUI.MelLabel(_row,l='Debug:')

    self.uiCB_post_debug = mUI.MelCheckBox(_row,en=True,
                               v = False,
                               label = '',
                               ann='Debug locators will not be deleted so you could see what happened')


    mUI.MelLabel(_row,l='Show Bake:')

    self.uiCB_post_show_bake = mUI.MelCheckBox(_row,en=True,
                               v = False,
                               label = '',
                               ann='Show the bake process')


    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Debug

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

    # Bake Spring Button
    #
    _row = mUI.MelHLayout(parentColumn,ut='cgmUISubTemplate',padding = _padding*2)
    
    cgmUI.add_Button(_row,'Bake Spring',
        cgmGEN.Callback(uiFunc_bake_spring,self),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Bake Spring',h=30)

    _row.layout()   
    #
    # End Bake Spring Button

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

def uiFunc_build_post_trajectory_aim_column(self):
    parentColumn = self._postProcessOptionsColumn

    parentColumn.clear()

    # Aim
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)
    self._post_row_aimDirection = _row

    mUI.MelSpacer(_row,w=_padding)                          
    mUI.MelLabel(_row,l='Aim:')  

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    directions = ['x+', 'x-', 'y+', 'y-', 'z+', 'z-']

    mUI.MelLabel(_row,l='Fwd:') 

    self.post_fwdMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    for dir in directions:
        self.post_fwdMenu.append(dir)
    
    self.post_fwdMenu.setValue(self._optionDict['aimFwd'])

    mUI.MelSpacer(_row,w=_padding)
    
    mUI.MelLabel(_row,l='Up:')

    self.post_upMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    for dir in directions:
        self.post_upMenu.append(dir)

    self.post_upMenu.setValue(self._optionDict['aimUp'])

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Aim

    # Post Damp
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Damp:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.uiFF_post_damp = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=15)

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Damp

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

    # Debug
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Show Bake:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )   

    self.uiCB_post_show_bake = mUI.MelCheckBox(_row,en=True,
                               v = False,
                               label = '',
                               ann='Show the bake process')


    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Debug

    # Bake Trajectory Aim Button
    #
    _row = mUI.MelHLayout(parentColumn,ut='cgmUISubTemplate',padding = _padding*2)
    
    cgmUI.add_Button(_row,'Bake Trajectory Aim',
        cgmGEN.Callback(uiFunc_bake_trajectory_aim,self),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Bake Trajectory Aim',h=30)

    _row.layout()   
    #
    # End Bake Dragger Button

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

def uiFunc_build_post_keyframe_to_motion_curve_column(self):
    parentColumn = self._postProcessOptionsColumn

    parentColumn.clear()

    # Debug
    #
    _row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)

    mUI.MelLabel(_row,l='Additional Options:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mUI.MelLabel(_row,l='Debug:')

    self.uiCB_post_debug = mUI.MelCheckBox(_row,en=True,
                               v = False,
                               label = '',
                               ann='Debug locators will not be deleted so you could see what happened')


    mUI.MelLabel(_row,l='Show Bake:')

    self.uiCB_post_show_bake = mUI.MelCheckBox(_row,en=True,
                               v = False,
                               label = '',
                               ann='Show the bake process')


    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Debug

    # Bake Trajectory Aim Button
    #
    _row = mUI.MelHLayout(parentColumn,ut='cgmUISubTemplate',padding = _padding*2)
    
    cgmUI.add_Button(_row,'Bake Keyframes to Motion Curve',
        cgmGEN.Callback(uiFunc_bake_keyframe_to_motion_curve,self),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Bake Keyframes to Motion Curve',h=30)

    _row.layout()   
    #
    # End Bake Dragger Button

    mc.setParent(parentColumn)
    cgmUI.add_LineSubBreak()  

def uiFunc_bake_dragger(self):
    for obj in mc.ls(sl=True):
        mc.select(obj)
        postInstance = DRAGGER.Dragger(aimFwd = self.post_fwdMenu.getValue(), aimUp = self.post_upMenu.getValue(), damp = self.uiFF_post_damp.getValue(), objectScale=self.uiFF_post_object_scale.getValue(), debug=self.uiCB_post_debug.getValue(), showBake=self.uiCB_post_show_bake.getValue())
        postInstance.bake()

def uiFunc_bake_spring(self):
    for obj in mc.ls(sl=True):
        mc.select(obj)
        postInstance = SPRING.Spring(aimFwd = self.post_fwdMenu.getValue(), aimUp = self.post_upMenu.getValue(), damp = self.uiFF_post_damp.getValue(), springForce=self.uiFF_post_spring.getValue(), angularDamp = self.uiFF_post_angularDamp.getValue(), angularSpringForce = self.uiFF_post_angularSpring.getValue(), objectScale=self.uiFF_post_object_scale.getValue(), debug=self.uiCB_post_debug.getValue(), showBake=self.uiCB_post_show_bake.getValue())
        postInstance.bake()

def uiFunc_bake_trajectory_aim(self):
    for obj in mc.ls(sl=True):
        mc.select(obj)
        postInstance = TRAJECTORYAIM.TrajectoryAim(aimFwd = self.post_fwdMenu.getValue(), aimUp = self.post_upMenu.getValue(), damp = self.uiFF_post_damp.getValue(), showBake=self.uiCB_post_show_bake.getValue())
        postInstance.bake()

def uiFunc_bake_keyframe_to_motion_curve(self):
    for obj in mc.ls(sl=True):
        mc.select(obj)
        postInstance = K2MC.KeyframeToMotionCurve(debug=self.uiCB_post_debug.getValue(), showBake=self.uiCB_post_show_bake.getValue())
        postInstance.bake()
        
def uiFunc_setPostAim(self):
    aimFwd = self.post_fwdMenu.getValue()
    aimUp = self.post_upMenu.getValue()

    if aimFwd[0] == aimUp[0]:
        log.error('Fwd and Up axis should be different or you may get unexpected results')
        self.post_fwdMenu(edit=True, bgc=[1,.35,.35])
        self.post_upMenu(edit=True, bgc=[1,.35,.35])
    else:
        self.post_fwdMenu(edit=True, bgc=[.35,.35,.35])
        self.post_upMenu(edit=True, bgc=[.35,.35,.35])