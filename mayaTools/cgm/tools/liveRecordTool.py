"""
------------------------------------------
liveRecordTool : cgm.tools
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

from cgm.tools import liveRecord
from cgm.tools import dragger as DRAGGER

#>>> Root settings =============================================================
__version__ = '0.1.05172020'
__toolname__ ='cgmAnimDraw'

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

        self._liveRecordTool = None
        self._mTransformTarget = False

        self._optionDict = {
            'mode' : 'position',
            'plane' : 'screen',
            'planeObject' : None,
            'aimFwd' : 'z+',
            'aimUp' : 'y+',
            'loopTime' : False,
            'debug' : False,
            'postBlendFrames' : 6
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

    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = _padding)        

    mUI.MelSpacer(_row,w=_padding)

    _subColumn = mUI.MelColumnLayout(_row,useTemplate = 'cgmUIHeaderTemplate') 

    _optionFrame = mUI.MelFrameLayout(_subColumn, label='Options', collapsable=True, collapse=True,useTemplate = 'cgmUIHeaderTemplate')
    
    self._optionColumn = mUI.MelColumnLayout(_optionFrame,useTemplate = 'cgmUIHeaderTemplate') 

    uiFunc_build_options_column(self)

    _row.setStretchWidget(_subColumn)

    mUI.MelSpacer(_row,w=_padding)

    #mUI.MelSpacer(_row,w=_padding)
    _row.layout()

    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()

    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = _padding*2)
    
    self.liveRecordBtn = cgmUI.add_Button(_row,'Start Recording Context',
        cgmGEN.Callback(uiFunc_toggleContext,self),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Start Live Record',h=50)

    _row.layout()    

    return _inside

def uiFunc_build_options_column(self):
    mc.setParent(self._optionColumn)
    cgmUI.add_LineSubBreak()

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

    mc.setParent(self._optionColumn)
    cgmUI.add_LineSubBreak()    

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

    mc.setParent(self._optionColumn)
    cgmUI.add_LineSubBreak()    

    _row = mUI.MelHSingleStretchLayout(self._optionColumn,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)                          
    mUI.MelLabel(_row,l='Plane:')  

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    planeOptions = ['screen', 'planeX', 'planeY', 'planeZ', 'axisX', 'axisY', 'axisZ', 'custom']
   
    self.planeMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
    for option in planeOptions:
        self.planeMenu.append(option)

    self.planeMenu.setValue( self._optionDict['plane'] )

    self.planeMenu(edit=True, changeCommand=cgmGEN.Callback(uiFunc_set_plane,self))

    cgmUI.add_Button(_row,'Visualize',
                     cgmGEN.Callback(uiFunc_visualize_plane,self),
                     "Create a plane in the scene that matches your selection.") 

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()

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

    mc.setParent(self._optionColumn)
    cgmUI.add_LineSubBreak()   

def uiFunc_visualize_plane(self):
    pass

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

def uiFunc_setModeOption(self, option, val):
    self._optionDict[option] = val

    if option == 'mode':
        if val == 'aim':
            self._row_aimDirection(edit=True, vis=True)
            self.planeMenu.clear()
            for option in ['screen', 'custom']:
                self.planeMenu.append(option)

            self.planeMenu.setValue( self._aimPlane )
            uiFunc_set_plane(self)
        else:
            self._row_aimDirection(edit=True, vis=False)
            self.planeMenu.clear()
            for option in ['screen', 'planeX', 'planeY', 'planeZ', 'axisX', 'axisY', 'axisZ', 'custom']:
                self.planeMenu.append(option)

            self.planeMenu.setValue( self._positionPlane )
            uiFunc_set_plane(self)

    uiFunc_update_args_live(self)

def uiFunc_update_args_live(self):
    if self._liveRecordTool:
        self._liveRecordTool.mode = self._optionDict['mode']
        self._liveRecordTool.plane = self._optionDict['plane']
        self._liveRecordTool.planeObject = self._optionDict['planeObject']
        self._liveRecordTool.aimFwd = self._optionDict['aimFwd']
        self._liveRecordTool.aimUp = self._optionDict['aimUp']
        self._liveRecordTool.postBlendFrames = self._optionDict['postBlendFrames']
        self._liveRecordTool.loopTime = self._optionDict['loopTime']
        self._liveRecordTool.debug = self._optionDict['debug']

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

    uiFunc_update_args_live(self)   

def uiFunc_create_planeObject(self):
    mc.polyPlane(name='customDrawPlane', sx=2, sy=2)
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

        uiFunc_updateObjectDisplay(self.uiTF_planeObject, self._optionDict['planeObject'] )
    else:
        log.warning("|{0}| >> Nothing selected.".format(_str_func))            
        uiFunc_clear_loaded(self.uiTF_planeObject)

    uiFunc_update_args_live(self)   

def uiFunc_toggleContext(self):
    _str_func = 'liveRecordTool.uiFunc_toggleContext'

    if self._liveRecordTool:
        self._liveRecordTool.quit()
        uiFunc_exit_draw_context(self)
    else:
        uiFunc_load_selected(self)
        if not self._mTransformTarget:
            log.error("No object selected. Can't start draw context")
            return

        self._liveRecordTool = liveRecord.LiveRecord(plane=self._optionDict['plane'], mode=self._optionDict['mode'], planeObject = self._optionDict['planeObject'], aimFwd = self._optionDict['aimFwd'], aimUp = self._optionDict['aimUp'], postBlendFrames=self._optionDict['postBlendFrames'], loopTime=self._optionDict['loopTime'], debug=self._optionDict['debug'], onStart=cgmGEN.Callback(uiFunc_recordingStarted,self), onComplete=cgmGEN.Callback(uiFunc_recordingCompleted,self), onExit=cgmGEN.Callback(uiFunc_exit_draw_context,self))
        self._liveRecordTool.activate()
        self.liveRecordBtn(e=True, label='Stop Recording Context', bgc=[.35,1,.35])

def uiFunc_exit_draw_context(self):
    self._mTransformTarget = None
    uiFunc_clear_loaded(self.uiTF_objLoad)
    self._liveRecordTool = None
    self.liveRecordBtn(e=True, label='Start Recording Context', bgc=[.35,.35,.35])
    
def uiFunc_recordingStarted(self):
    _str_func = 'liveRecordTool.uiFunc_recordingStarted'

    log.debug("|{0}| >> Starting Recording in UI".format(_str_func))

    self.liveRecordBtn(e=True, label='Recording in Process', bgc=[1,.35,.35])

def uiFunc_recordingCompleted(self):
    _str_func = 'liveRecordTool.uiFunc_recordingCompleted'
    log.debug("|{0}| >> Starting Recording in UI".format(_str_func))
    self.liveRecordBtn(e=True, label='Stop Recording Context', bgc=[.35,1,.35])

def uiFunc_load_selected(self, bypassAttrCheck = False):
    _str_func = 'uiFunc_load_selected'  
    self._mTransformTarget = False

    _sel = mc.ls(sl=True,type='transform')

    #Get our raw data
    if _sel:
        mNode = cgmMeta.validateObjArg(_sel[0])
        _short = mNode.p_nameBase            
        log.debug("|{0}| >> Target: {1}".format(_str_func, _short))
        self._mTransformTarget = mNode

        uiFunc_updateObjectDisplay(self.uiTF_objLoad, self._mTransformTarget)
    else:
        log.warning("|{0}| >> Nothing selected.".format(_str_func))            
        uiFunc_clear_loaded(self.uiTF_objLoad)

def uiFunc_clear_loaded(uiElement):
    _str_func = 'uiFunc_clear_loaded'  
    uiElement(edit=True, l='',en=False)      
     
def uiFunc_updateObjectDisplay(uiElement, mObj):
    _str_func = 'uiFunc_updateObjectDisplay'  

    if not object:
        log.info("|{0}| >> No target.".format(_str_func))                        
        #No obj
        #self.uiTF_objLoad(edit=True, l='',en=False)
        uiElement(edit=True, l='',en=False)

        return
    
    #_short = self._mTransformTarget.p_nameBase
    _short = mObj.p_nameBase
    uiElement(edit=True, ann=_short)
    
    if len(_short)>20:
        _short = _short[:20]+"..."
    uiElement(edit=True, l=_short)   
    
    uiElement(edit=True, en=True)
    
    return