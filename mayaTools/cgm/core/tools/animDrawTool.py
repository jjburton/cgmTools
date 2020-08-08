"""
------------------------------------------
animDrawTool : cgm.tools
Author: David Bokser
email: dbokser@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

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

from cgm.core.tools import animDraw
from cgm.core.tools import dragger as DRAGGER
from cgm.core.tools import trajectoryAim as TRAJECTORYAIM
from cgm.core.tools import keyframeToMotionCurve as K2MC
from cgm.core.tools import spring as SPRING

from cgm.core.tools import animFilterTool as AFT

#>>> Root settings =============================================================
__version__ = '0.1.05172020'
__toolname__ ='cgmAnimDraw'

_padding = 5

_planeOptionsPosition = ['screen', 'planeX', 'planeY', 'planeZ', 'axisX', 'axisY', 'axisZ', 'custom', 'object']
_planeOptionsAim = ['screen', 'planeX', 'planeY', 'planeZ', 'custom', 'object']

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

        self._animDrawTool = None
        self._mTransformTargets = []

        self._optionDict = {
            'mode' : 'position',
            'plane' : 'screen',
            'planeObject' : None,
            'aimFwd' : 'z+',
            'aimUp' : 'y+',
            'loopTime' : False,
            'debug' : False,
            'postBlendFrames' : 6,
            'recordMode' : 'replace'
        }

        self._positionPlane = self._optionDict['plane']
        self._aimPlane = self._optionDict['plane']


 
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
    _row_objLoad = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = _padding)        

    mUI.MelSpacer(_row_objLoad,w=_padding)
    mUI.MelLabel(_row_objLoad, 
                 l='Target:')

    self.uiTF_objLoad = mUI.MelLabel(_row_objLoad,ut='cgmUIInstructionsTemplate',l='',en=True)

    _row_objLoad.setStretchWidget(self.uiTF_objLoad)
    mUI.MelSpacer(_row_objLoad,w=_padding)

    _row_objLoad.layout()

    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()

    # Options Frame
    #
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = _padding)        

    mUI.MelSpacer(_row,w=_padding)

    _subColumn = mUI.MelColumnLayout(_row,useTemplate = 'cgmUIHeaderTemplate') 

    _optionFrame = mUI.MelFrameLayout(_subColumn, label='Options', collapsable=True, collapse=True,useTemplate = 'cgmUIHeaderTemplate')
    
    self._optionColumn = mUI.MelColumnLayout(_optionFrame,useTemplate = 'cgmUIHeaderTemplate') 

    uiFunc_build_options_column(self)

    _row.setStretchWidget(_subColumn)

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Options Frame

    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()

    # Recording Button
    #
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = _padding*2)
    
    self.animDrawBtn = cgmUI.add_Button(_row,'Start Recording Context',
        cgmGEN.Callback(uiFunc_toggleContext,self),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Start Live Record',h=50)

    _row.layout()    
    #
    # End Recording Button

    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()

    # Instructions Label
    #
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = _padding*2)
    self._infoLayout = _row

    self._infoLayout(edit=True, vis=False)

    mUI.MelLabel(_row,ut='cgmUIInstructionsTemplate',l='Left Drag: Draw  -  Ctrl Left Drag: Reposition  -  Right Click: Cache Data',en=True)

    _row.layout()
    #
    # End Instructions

    # Post Process Frame
    #
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = _padding)        

    mUI.MelSpacer(_row,w=_padding)

    _subColumn = mUI.MelColumnLayout(_row,useTemplate = 'cgmUIHeaderTemplate') 

    _postProcessFrame = mUI.MelFrameLayout(_subColumn, label='Post Process Animation', collapsable=True, collapse=True,useTemplate = 'cgmUIHeaderTemplate')
    
    self._postProcessColumn = mUI.MelColumnLayout(_postProcessFrame,useTemplate = 'cgmUIHeaderTemplate') 

    AFT.uiFunc_build_post_process_column(self, self._postProcessColumn)

    _row.setStretchWidget(_subColumn)

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Post Process Frame

    return _inside

def uiFunc_build_options_column(self):
    mc.setParent(self._optionColumn)
    cgmUI.add_LineSubBreak()

    # Mode
    #
    _row = mUI.MelHSingleStretchLayout(self._optionColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)                      
    mUI.MelLabel(_row,l='Mode:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    uiRC = mUI.MelRadioCollection()

    _on = self._optionDict['mode']

    for i,item in enumerate(['position','aim']):
        if item == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(uiFunc_setModeOption,self,'mode', item))

        mUI.MelSpacer(_row,w=_padding)       

    _row.layout()  
    #
    # End Mode

    mc.setParent(self._optionColumn)
    cgmUI.add_LineSubBreak()    

    # Plane
    #
    _row = mUI.MelHSingleStretchLayout(self._optionColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)                          
    mUI.MelLabel(_row,l='Plane:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )
   
    self.planeMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
    for option in _planeOptionsPosition:
        self.planeMenu.append(option)

    self.planeMenu.setValue( self._optionDict['plane'] )

    self.planeMenu(edit=True, changeCommand=cgmGEN.Callback(uiFunc_set_plane,self))

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Plane

    # Aim
    #
    _row = mUI.MelHSingleStretchLayout(self._optionColumn,ut='cgmUISubTemplate',padding = 5, vis=False)
    self._row_aimDirection = _row

    mUI.MelSpacer(_row,w=_padding)                          
    mUI.MelLabel(_row,l='Aim:')  

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    directions = ['x+', 'x-', 'y+', 'y-', 'z+', 'z-']

    mUI.MelLabel(_row,l='Fwd:') 

    self.fwdMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setAim,self))
    for dir in directions:
        self.fwdMenu.append(dir)
    
    self.fwdMenu.setValue(self._optionDict['aimFwd'])

    mUI.MelSpacer(_row,w=_padding)
    
    mUI.MelLabel(_row,l='Up:')

    self.upMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setAim,self))
    for dir in directions:
        self.upMenu.append(dir)

    self.upMenu.setValue(self._optionDict['aimUp'])

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Aim

    # mc.setParent(self._optionColumn)
    # cgmUI.add_LineSubBreak()    

    # Plane Object
    #
    _row = mUI.MelHSingleStretchLayout(self._optionColumn,ut='cgmUISubTemplate',padding = 5)
    self._row_planeObject = _row

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Plane Object:')

    self.uiTF_planeObject = mUI.MelLabel(_row,ut='cgmUIInstructionsTemplate',l='',en=False)

    _row.setStretchWidget( self.uiTF_planeObject )

    cgmUI.add_Button(_row,'<<',
                     cgmGEN.Callback(uiFunc_load_planeObject,self),
                     "Load first selected object.")  

    cgmUI.add_Button(_row,'Create',
                     cgmGEN.Callback(uiFunc_create_planeObject,self),
                     "Load first selected object.") 

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()

    self._row_planeObject(edit=True, vis=False)
    #
    # End Plane Object

    # Record Mode
    #
    _row = mUI.MelHSingleStretchLayout(self._optionColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)                          
    mUI.MelLabel(_row,l='Record Mode:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )
   
    self.recordMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
    for option in ['replace', 'combine']:
        self.recordMenu.append(option)

    self.recordMenu.setValue( self._optionDict['recordMode'] )

    self.recordMenu(edit=True, changeCommand=cgmGEN.Callback(uiFunc_set_record_mode,self))

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Record Mode

    # Loop Time
    #
    _row = mUI.MelHSingleStretchLayout(self._optionColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Loop Time:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.uiCB_loopTime = mUI.MelCheckBox(_row,en=True,
                               v = self._optionDict['loopTime'],
                               label = '',
                               ann='Should time loop to start after reaching the end',
                               cc=cgmGEN.Callback(uiFunc_set_loop_time,self))

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Loop Time

    # Post Blend Frames
    #
    _row = mUI.MelHSingleStretchLayout(self._optionColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Post Blend Frames:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.uiIF_postBlendFrames = mUI.MelIntField(_row, ut='cgmUISubTemplate', w= 50, v=self._optionDict['postBlendFrames'], cc=cgmGEN.Callback(uiFunc_set_post_blend_frames,self))

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Post Blend Frames

    # Debug
    #
    _row = mUI.MelHSingleStretchLayout(self._optionColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Debug:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.uiCB_debug = mUI.MelCheckBox(_row,en=True,
                               v = self._optionDict['loopTime'],
                               label = '',
                               ann='Various debug junk might stick around after recording',
                               cc=cgmGEN.Callback(uiFunc_set_debug,self))

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Debug

    mc.setParent(self._optionColumn)
    cgmUI.add_LineSubBreak()   

#def uiFunc_build_post_process_column(self):
    #parentColumn = self._postProcessColumn
    
    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()

    ## Post Process Action
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)
    #self._post_row_aimDirection = _row

    #mUI.MelSpacer(_row,w=_padding)                          
    #mUI.MelLabel(_row,l='Action:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #actions = ['Dragger', 'Spring', 'Trajectory Aim', 'Keys to Motion Curve']

    #self.post_actionMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAction,self))
    #for dir in actions:
        #self.post_actionMenu.append(dir)
    
    #self.post_actionMenu.setValue(actions[0])

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Post Process Action

    ## Post Process Options Frame
    ##
    #self._postProcessOptionsColumn = mUI.MelColumnLayout(parentColumn,useTemplate = 'cgmUISubTemplate') 
    ##
    ## Post Process Options Frame

    #uiFunc_setPostAction(self)

#def uiFunc_setPostAction(self):
    #postAction = self.post_actionMenu.getValue()

    #if postAction == 'Dragger':
        #uiFunc_build_post_dragger_column(self)
    #elif postAction == 'Spring':
        #uiFunc_build_post_spring_column(self)
    #elif postAction == 'Trajectory Aim':
        #uiFunc_build_post_trajectory_aim_column(self)
    #elif postAction == 'Keys to Motion Curve':
        #uiFunc_build_post_keyframe_to_motion_curve_column(self)

#def uiFunc_build_post_dragger_column(self):
    #parentColumn = self._postProcessOptionsColumn

    #parentColumn.clear()

    ## Aim
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)
    #self._post_row_aimDirection = _row

    #mUI.MelSpacer(_row,w=_padding)                          
    #mUI.MelLabel(_row,l='Aim:')  

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #directions = ['x+', 'x-', 'y+', 'y-', 'z+', 'z-']

    #mUI.MelLabel(_row,l='Fwd:') 

    #self.post_fwdMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    #for dir in directions:
        #self.post_fwdMenu.append(dir)
    
    #self.post_fwdMenu.setValue(self._optionDict['aimFwd'])

    #mUI.MelSpacer(_row,w=_padding)
    
    #mUI.MelLabel(_row,l='Up:')

    #self.post_upMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    #for dir in directions:
        #self.post_upMenu.append(dir)

    #self.post_upMenu.setValue(self._optionDict['aimUp'])

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Aim

    ## Post Damp
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)
    #mUI.MelLabel(_row,l='Damp:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #self.uiFF_post_damp = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=3.0)

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Damp

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

    ## Post Object Scale
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)
    #mUI.MelLabel(_row,l='Object Scale:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #self.uiFF_post_object_scale = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=10.0)

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Object Scale

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

    ## Debug
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)

    #mUI.MelLabel(_row,l='Additional Options:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #mUI.MelLabel(_row,l='Debug:')

    #self.uiCB_post_debug = mUI.MelCheckBox(_row,en=True,
                               #v = False,
                               #label = '',
                               #ann='Debug locators will not be deleted so you could see what happened')


    #mUI.MelLabel(_row,l='Show Bake:')

    #self.uiCB_post_show_bake = mUI.MelCheckBox(_row,en=True,
                               #v = False,
                               #label = '',
                               #ann='Show the bake process')


    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Debug

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

    ## Bake Dragger Button
    ##
    #_row = mUI.MelHLayout(parentColumn,ut='cgmUISubTemplate',padding = _padding*2)
    
    #cgmUI.add_Button(_row,'Bake Dragger',
        #cgmGEN.Callback(uiFunc_bake_dragger,self),                         
        ##lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        #'Bake Dragger',h=30)

    #_row.layout()   
    ##
    ## End Bake Dragger Button

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

#def uiFunc_build_post_spring_column(self):
    #parentColumn = self._postProcessOptionsColumn

    #parentColumn.clear()

    ## Aim
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)
    #self._post_row_aimDirection = _row

    #mUI.MelSpacer(_row,w=_padding)                          
    #mUI.MelLabel(_row,l='Aim:')  

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #directions = ['x+', 'x-', 'y+', 'y-', 'z+', 'z-']

    #mUI.MelLabel(_row,l='Fwd:') 

    #self.post_fwdMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    #for dir in directions:
        #self.post_fwdMenu.append(dir)
    
    #self.post_fwdMenu.setValue(self._optionDict['aimFwd'])

    #mUI.MelSpacer(_row,w=_padding)
    
    #mUI.MelLabel(_row,l='Up:')

    #self.post_upMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    #for dir in directions:
        #self.post_upMenu.append(dir)

    #self.post_upMenu.setValue(self._optionDict['aimUp'])

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Aim

    ## Spring
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)
    #mUI.MelLabel(_row,l='Spring Force:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #self.uiFF_post_spring = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=1.0)

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Spring

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

    ## Post Damp
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)
    #mUI.MelLabel(_row,l='Damp:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #self.uiFF_post_damp = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=.1)

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Damp

    ## Spring
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)
    #mUI.MelLabel(_row,l='Angular Spring Force:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #self.uiFF_post_angularSpring = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=1.0)

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Spring

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

    ## Post Damp
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)
    #mUI.MelLabel(_row,l='Angular Damp:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #self.uiFF_post_angularDamp = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=.1)

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Damp

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

    ## Post Object Scale
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)
    #mUI.MelLabel(_row,l='Object Scale:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #self.uiFF_post_object_scale = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=10.0)

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Object Scale

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

    ## Debug
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)

    #mUI.MelLabel(_row,l='Additional Options:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #mUI.MelLabel(_row,l='Debug:')

    #self.uiCB_post_debug = mUI.MelCheckBox(_row,en=True,
                               #v = False,
                               #label = '',
                               #ann='Debug locators will not be deleted so you could see what happened')


    #mUI.MelLabel(_row,l='Show Bake:')

    #self.uiCB_post_show_bake = mUI.MelCheckBox(_row,en=True,
                               #v = False,
                               #label = '',
                               #ann='Show the bake process')


    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Debug

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

    ## Bake Spring Button
    ##
    #_row = mUI.MelHLayout(parentColumn,ut='cgmUISubTemplate',padding = _padding*2)
    
    #cgmUI.add_Button(_row,'Bake Spring',
        #cgmGEN.Callback(uiFunc_bake_spring,self),                         
        ##lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        #'Bake Spring',h=30)

    #_row.layout()   
    ##
    ## End Bake Spring Button

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

#def uiFunc_build_post_trajectory_aim_column(self):
    #parentColumn = self._postProcessOptionsColumn

    #parentColumn.clear()

    ## Aim
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)
    #self._post_row_aimDirection = _row

    #mUI.MelSpacer(_row,w=_padding)                          
    #mUI.MelLabel(_row,l='Aim:')  

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #directions = ['x+', 'x-', 'y+', 'y-', 'z+', 'z-']

    #mUI.MelLabel(_row,l='Fwd:') 

    #self.post_fwdMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    #for dir in directions:
        #self.post_fwdMenu.append(dir)
    
    #self.post_fwdMenu.setValue(self._optionDict['aimFwd'])

    #mUI.MelSpacer(_row,w=_padding)
    
    #mUI.MelLabel(_row,l='Up:')

    #self.post_upMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate', changeCommand=cgmGEN.Callback(uiFunc_setPostAim,self))
    #for dir in directions:
        #self.post_upMenu.append(dir)

    #self.post_upMenu.setValue(self._optionDict['aimUp'])

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Aim

    ## Post Damp
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)
    #mUI.MelLabel(_row,l='Damp:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #self.uiFF_post_damp = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, v=15)

    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Damp

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

    ## Debug
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)
    #mUI.MelLabel(_row,l='Show Bake:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )   

    #self.uiCB_post_show_bake = mUI.MelCheckBox(_row,en=True,
                               #v = False,
                               #label = '',
                               #ann='Show the bake process')


    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Debug

    ## Bake Trajectory Aim Button
    ##
    #_row = mUI.MelHLayout(parentColumn,ut='cgmUISubTemplate',padding = _padding*2)
    
    #cgmUI.add_Button(_row,'Bake Trajectory Aim',
        #cgmGEN.Callback(uiFunc_bake_trajectory_aim,self),                         
        ##lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        #'Bake Trajectory Aim',h=30)

    #_row.layout()   
    ##
    ## End Bake Dragger Button

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

#def uiFunc_build_post_keyframe_to_motion_curve_column(self):
    #parentColumn = self._postProcessOptionsColumn

    #parentColumn.clear()

    ## Debug
    ##
    #_row = mUI.MelHSingleStretchLayout(parentColumn,ut='cgmUISubTemplate',padding = 5)

    #mUI.MelSpacer(_row,w=_padding)

    #mUI.MelLabel(_row,l='Additional Options:')

    #_row.setStretchWidget( mUI.MelSeparator(_row) )

    #mUI.MelLabel(_row,l='Debug:')

    #self.uiCB_post_debug = mUI.MelCheckBox(_row,en=True,
                               #v = False,
                               #label = '',
                               #ann='Debug locators will not be deleted so you could see what happened')


    #mUI.MelLabel(_row,l='Show Bake:')

    #self.uiCB_post_show_bake = mUI.MelCheckBox(_row,en=True,
                               #v = False,
                               #label = '',
                               #ann='Show the bake process')


    #mUI.MelSpacer(_row,w=_padding)

    #_row.layout()
    ##
    ## End Debug

    ## Bake Trajectory Aim Button
    ##
    #_row = mUI.MelHLayout(parentColumn,ut='cgmUISubTemplate',padding = _padding*2)
    
    #cgmUI.add_Button(_row,'Bake Keyframes to Motion Curve',
        #cgmGEN.Callback(uiFunc_bake_keyframe_to_motion_curve,self),                         
        ##lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        #'Bake Keyframes to Motion Curve',h=30)

    #_row.layout()   
    ##
    ## End Bake Dragger Button

    #mc.setParent(parentColumn)
    #cgmUI.add_LineSubBreak()  

#def uiFunc_bake_dragger(self):
    #for obj in mc.ls(sl=True):
        #mc.select(obj)
        #postInstance = DRAGGER.Dragger(aimFwd = self.post_fwdMenu.getValue(), aimUp = self.post_upMenu.getValue(), damp = self.uiFF_post_damp.getValue(), objectScale=self.uiFF_post_object_scale.getValue(), debug=self.uiCB_post_debug.getValue(), showBake=self.uiCB_post_show_bake.getValue())
        #postInstance.bake()

#def uiFunc_bake_spring(self):
    #for obj in mc.ls(sl=True):
        #mc.select(obj)
        #postInstance = SPRING.Spring(aimFwd = self.post_fwdMenu.getValue(), aimUp = self.post_upMenu.getValue(), damp = self.uiFF_post_damp.getValue(), springForce=self.uiFF_post_spring.getValue(), angularDamp = self.uiFF_post_angularDamp.getValue(), angularSpringForce = self.uiFF_post_angularSpring.getValue(), objectScale=self.uiFF_post_object_scale.getValue(), debug=self.uiCB_post_debug.getValue(), showBake=self.uiCB_post_show_bake.getValue())
        #postInstance.bake()

#def uiFunc_bake_trajectory_aim(self):
    #for obj in mc.ls(sl=True):
        #mc.select(obj)
        #postInstance = TRAJECTORYAIM.TrajectoryAim(aimFwd = self.post_fwdMenu.getValue(), aimUp = self.post_upMenu.getValue(), damp = self.uiFF_post_damp.getValue(), showBake=self.uiCB_post_show_bake.getValue())
        #postInstance.bake()

#def uiFunc_bake_keyframe_to_motion_curve(self):
    #for obj in mc.ls(sl=True):
        #mc.select(obj)
        #postInstance = K2MC.KeyframeToMotionCurve(debug=self.uiCB_post_debug.getValue(), showBake=self.uiCB_post_show_bake.getValue())
        #postInstance.bake()

def uiFunc_set_post_blend_frames(self):
    self._optionDict['postBlendFrames'] = self.uiIF_postBlendFrames.getValue()
    uiFunc_update_args_live(self)

def uiFunc_set_loop_time(self):
    self._optionDict['loopTime'] = self.uiCB_loopTime.getValue()
    uiFunc_update_args_live(self)

def uiFunc_set_record_mode(self):
    self._optionDict['recordMode'] = self.recordMenu.getValue()
    uiFunc_update_args_live(self)

def uiFunc_set_debug(self):
    self._optionDict['debug'] = self.uiCB_debug.getValue()
    uiFunc_update_args_live(self)    

def uiFunc_setAim(self):
    aimFwd = self.fwdMenu.getValue()
    aimUp = self.upMenu.getValue()
    self._optionDict['aimFwd'] = aimFwd
    self._optionDict['aimUp'] = aimUp
    if aimFwd[0] == aimUp[0]:
        log.error('Fwd and Up axis should be different or you may get unexpected results')
        self.fwdMenu(edit=True, bgc=[1,.35,.35])
        self.upMenu(edit=True, bgc=[1,.35,.35])
    else:
        self.fwdMenu(edit=True, bgc=[.35,.35,.35])
        self.upMenu(edit=True, bgc=[.35,.35,.35])

    uiFunc_update_args_live(self)

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

def uiFunc_setModeOption(self, option, val):
    self._optionDict[option] = val

    if option == 'mode':
        if val == 'aim':
            self._row_aimDirection(edit=True, vis=True)
            self.planeMenu.clear()
            for option in _planeOptionsAim:
                self.planeMenu.append(option)

            self.planeMenu.setValue( self._aimPlane )
            uiFunc_set_plane(self)
        else:
            self._row_aimDirection(edit=True, vis=False)
            self.planeMenu.clear()
            for option in _planeOptionsPosition:
                self.planeMenu.append(option)

            self.planeMenu.setValue( self._positionPlane )
            uiFunc_set_plane(self)

    uiFunc_update_args_live(self)

def uiFunc_update_args_live(self):
    if self._animDrawTool:
        self._animDrawTool.mode = self._optionDict['mode']
        self._animDrawTool.plane = self._optionDict['plane']
        self._animDrawTool.planeObject = self._optionDict['planeObject']
        self._animDrawTool.aimFwd = self._optionDict['aimFwd']
        self._animDrawTool.aimUp = self._optionDict['aimUp']
        self._animDrawTool.postBlendFrames = self._optionDict['postBlendFrames']
        self._animDrawTool.loopTime = self._optionDict['loopTime']
        self._animDrawTool.debug = self._optionDict['debug']
        self._animDrawTool.recordMode = self._optionDict['recordMode']

def uiFunc_set_plane(self):
    self._optionDict['plane'] = self.planeMenu.getValue()
    if self._optionDict['mode'] == 'position':
        self._positionPlane = self._optionDict['plane']
    elif self._optionDict['mode'] == 'aim':
        self._aimPlane = self._optionDict['plane']

    if self.planeMenu.getValue() == 'custom':
        self._row_planeObject(edit=True, vis=True)
    else:
        self._row_planeObject(edit=True, vis=False)
    
    if self.planeMenu.getValue() == 'object':
        self._row_aimDirection(edit=True, vis=True)
    else:
        if not self._optionDict['mode'] == 'aim':
            self._row_aimDirection(edit=True, vis=False)


    uiFunc_update_args_live(self)   

def uiFunc_create_planeObject(self):
    animDraw.makePlaneCurve()
    uiFunc_load_planeObject(self)

def uiFunc_load_planeObject(self):
    _str_func = 'uiFunc_load_planeObject'  
    self._optionDict['planeObject']  = None

    _sel = mc.ls(sl=True,type='transform')

    #Get our raw data
    if _sel:
        mNode = cgmMeta.validateObjArg(_sel[0])
        _short = mNode.p_nameBase            
        log.debug("|{0}| >> Target: {1}".format(_str_func, _short))
        self._optionDict['planeObject']  = mNode

        uiFunc_updateObjectDisplay(self.uiTF_planeObject, [self._optionDict['planeObject']] )
    else:
        log.warning("|{0}| >> Nothing selected.".format(_str_func))            
        uiFunc_clear_loaded(self.uiTF_planeObject)

    uiFunc_update_args_live(self)   

def uiFunc_toggleContext(self):
    _str_func = 'animDrawTool.uiFunc_toggleContext'

    if self._animDrawTool:
        self._animDrawTool.quit()
        uiFunc_exit_draw_context(self)
    else:
        uiFunc_load_selected(self)
        if not self._mTransformTargets:
            log.error("No object selected. Can't start draw context")
            return

        self._animDrawTool = animDraw.AnimDraw(plane=self._optionDict['plane'], mode=self._optionDict['mode'], planeObject = self._optionDict['planeObject'], aimFwd = self._optionDict['aimFwd'], aimUp = self._optionDict['aimUp'], postBlendFrames=self._optionDict['postBlendFrames'], loopTime=self._optionDict['loopTime'], debug=self._optionDict['debug'], recordMode = self._optionDict['recordMode'], onStart=cgmGEN.Callback(uiFunc_recordingStarted,self), onComplete=cgmGEN.Callback(uiFunc_recordingCompleted,self), onReposition=cgmGEN.Callback(uiFunc_recordingCompleted,self),onExit=cgmGEN.Callback(uiFunc_exit_draw_context,self))
        self._animDrawTool.activate()
        self.animDrawBtn(e=True, label='Stop Recording Context', bgc=[.35,1,.35])
        self._infoLayout(edit=True, vis=True)

def uiFunc_exit_draw_context(self):
    self._mTransformTargets = None
    uiFunc_clear_loaded(self.uiTF_objLoad)
    self._animDrawTool = None
    self.animDrawBtn(e=True, label='Start Recording Context', bgc=[.35,.35,.35])
    self._infoLayout(edit=True, vis=False)

def uiFunc_recordingStarted(self):
    _str_func = 'animDrawTool.uiFunc_recordingStarted'

    log.debug("|{0}| >> Starting Recording in UI".format(_str_func))

    self.animDrawBtn(e=True, label='Recording in Process', bgc=[1,.35,.35])

def uiFunc_recordingCompleted(self):
    _str_func = 'animDrawTool.uiFunc_recordingCompleted'
    log.debug("|{0}| >> Ending Recording in UI".format(_str_func))
    self.animDrawBtn(e=True, label='Stop Recording Context', bgc=[.35,1,.35])

def uiFunc_load_selected(self, bypassAttrCheck = False):
    _str_func = 'uiFunc_load_selected'  
    self._mTransformTargets = False

    _sel = mc.ls(sl=True,type='transform')

    #Get our raw data
    if _sel:
        mNodes = cgmMeta.validateObjListArg(_sel)
        _short = ', '.join([mNode.p_nameBase for mNode in mNodes])
        log.debug("|{0}| >> Target: {1}".format(_str_func, _short))
        self._mTransformTargets = mNodes

        uiFunc_updateObjectDisplay(self.uiTF_objLoad, self._mTransformTargets)
    else:
        log.warning("|{0}| >> Nothing selected.".format(_str_func))            
        uiFunc_clear_loaded(self.uiTF_objLoad)

def uiFunc_clear_loaded(uiElement):
    _str_func = 'uiFunc_clear_loaded'  
    uiElement(edit=True, l='',en=False)      
     
def uiFunc_updateObjectDisplay(uiElement, mObjs):
    _str_func = 'uiFunc_updateObjectDisplay'  

    if not mObjs:
        log.info("|{0}| >> No target.".format(_str_func))                        
        #No obj
        #self.uiTF_objLoad(edit=True, l='',en=False)
        uiElement(edit=True, l='',en=False)

        return
    
    #_short = self._mTransformTargets.p_nameBase
    _short = ', '.join([mNode.p_nameBase for mNode in mObjs])
    uiElement(edit=True, ann=_short)
    
    if len(_short)>20:
        _short = _short[:20]+"..."
    uiElement(edit=True, l=_short)   
    
    uiElement(edit=True, en=True)
    
    return