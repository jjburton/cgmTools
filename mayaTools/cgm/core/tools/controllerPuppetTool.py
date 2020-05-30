"""
------------------------------------------
controllerPuppetTool: cgm.core.tools
Author: David Bokser
email: dbokser@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
UI for controller puppet
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

from cgm.core.classes import GamePad
from cgm.core.tools import controllerPuppet as controllerPuppet

#>>> Root settings =============================================================
__version__ = '0.1.5292020'
__toolname__ ='controllerPuppetTool'


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

        self.controllerPuppet = None
        self._parentCamera = None

        self.connectionDict = { 'RStickHorizontal':{},
                                'RStickVertical':{},
                                'LStickHorizontal':{},
                                'LStickVertical':{},
                                'RTrigger':{},
                                'LTrigger':{} }
 
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
    
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()

    controllerConnections = [ ['Left Stick Horizontal', 'LStickHorizontal'], ['Left Stick Vertical', 'LStickVertical'], ['Right Stick Horizontal', 'RStickHorizontal'], ['Right Stick Vertical', 'RStickVertical'], ['Left Trigger', 'LTrigger'], ['Right Trigger', 'RTrigger'] ]

    for con in controllerConnections:
        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = _padding)        

        mUI.MelSpacer(_row,w=_padding)

        _subColumn = mUI.MelColumnLayout(_row,useTemplate = 'cgmUIHeaderTemplate') 

        _conFrame = mUI.MelFrameLayout(_subColumn, label=con[0], collapsable=True, collapse=True,useTemplate = 'cgmUIHeaderTemplate')
        
        _conColumn = mUI.MelColumnLayout(_conFrame,useTemplate = 'cgmUIHeaderTemplate') 

        uiFunc_build_controller_connection_column(self, _conColumn, con[1])

        _row.setStretchWidget(_subColumn)

        mUI.MelSpacer(_row,w=_padding)

        _row.layout()

        mc.setParent(_inside)
        cgmUI.add_LineSubBreak()

    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()

    # Start GamePad Button
    #
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = _padding*2)
    
    self.animDrawBtn = cgmUI.add_Button(_row,'Start GamePad',
        cgmGEN.Callback(toggle_controller,self),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Start Gamepad Button',h=50)

    _row.layout()    
    #
    # End Recording Button

    return _inside

def uiFunc_build_controller_connection_column(self, parent, connection):
    mc.setParent(parent)
    cgmUI.add_LineSubBreak()

    # Connection Column
    #
    connectionColumn = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
    #
    # End Connection Column

    _row = mUI.MelHLayout(parent,ut='cgmUISubTemplate',padding = 0)
    
    btn = cgmUI.add_Button(_row,'Add Connection',
        cgmGEN.Callback(add_connection,self, connectionColumn, connection),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Start Gamepad Button',h=25)

    _row.layout()

def add_connection(self, parent, connection):
    for obj in mc.ls(sl=True):
        for attr in mc.channelBox('mainChannelBox', q=True, sma=True ):
            connectionString = '{0}.{1}'.format(obj, attr)
            self.connectionDict[connection][connectionString] = {'min':0, 'max':1, 'damp':10}

            # Add Connection
            #
            _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

            mUI.MelSpacer(_row,w=_padding)
            mUI.MelLabel(_row,l='Target:')

            conLabel = mUI.MelLabel(_row,ut='cgmUIInstructionsTemplate',l=connectionString,en=False)

            _row.setStretchWidget( conLabel )

            mUI.MelLabel(_row,l='Min:')
            ff_min = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, precision = 2, v=self.connectionDict[connection][connectionString]['min'])

            mUI.MelLabel(_row,l='Max:')
            ff_max = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, precision = 2, v=self.connectionDict[connection][connectionString]['max'])

            mUI.MelLabel(_row,l='Damp:')
            ff_damp = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, precision = 2, v=self.connectionDict[connection][connectionString]['damp'])


            ff_min(edit=True, cc=cgmGEN.Callback(uiFunc_change_connection,self,connection, connectionString, ff_min, ff_max, ff_damp))
            ff_max(edit=True, cc=cgmGEN.Callback(uiFunc_change_connection,self,connection, connectionString, ff_min, ff_max, ff_damp))
            ff_damp(edit=True, cc=cgmGEN.Callback(uiFunc_change_connection,self,connection, connectionString, ff_min, ff_max, ff_damp))


            cgmUI.add_Button(_row,'X',
                             cgmGEN.Callback(uiFunc_remove_connection,self,_row, obj, attr),
                             "Remove connection.")  

            mUI.MelSpacer(_row,w=_padding)

            _row.layout()
            #
            # End Add Connection

def uiFunc_change_connection(self, connection, connectionString, minUI, maxUI, dampUI):
    self.connectionDict[connection][connectionString]['min'] = minUI.getValue()
    self.connectionDict[connection][connectionString]['max'] = maxUI.getValue()
    self.connectionDict[connection][connectionString]['damp'] = dampUI.getValue()

def uiFunc_remove_connection(self,row, obj, attr):
    mc.deleteUI(row)

def toggle_controller(self):
    if self.controllerPuppet != None:
        self.animDrawBtn(edit=True, label="Start Controller", bgc=[.35,.35,.35])
        stop_controller(self)
    else:
        self.animDrawBtn(edit=True, label="Stop Controller", bgc=[.35,1,.35])
        mc.refresh()
        start_controller(self)

def start_controller(self):
    self.controllerPuppet = controllerPuppet.ControllerPuppet(self.connectionDict)

def stop_controller(self):
    if self.controllerPuppet:
        self.controllerPuppet.stop()

