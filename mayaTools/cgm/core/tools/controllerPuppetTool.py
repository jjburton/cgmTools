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
import pprint
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import maya.cmds as mc

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta

from cgm.core.tools import controllerPuppet as controllerPuppet

import json

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

        self.recentOptionStore = cgmMeta.cgmOptionVar("cgmVar_controllerPuppet_recent", varType = "string", defaultValue=json.dumps([]) )
        self.recentMappings = json.loads( self.recentOptionStore.getValue() )

        self.connectionDict = { 'name':'Default',
                                'RStickHorizontal':{},
                                'RStickVertical':{},
                                'LStickHorizontal':{},
                                'LStickVertical':{},
                                'RTrigger':{},
                                'LTrigger':{} }

        self.mappingList = []
 
    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     

        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Save Mappings",
                         c = cgmGEN.Callback(uiFunc_save,self) )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Load Mappings",
                         c = cgmGEN.Callback(uiFunc_load,self) )

        recent = mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Recent",subMenu=True )

        for mapping in self.recentMappings:
            mUI.MelMenuItem( recent, l=mapping,
                             c = cgmGEN.Callback(uiFunc_load,self,mapping) )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        #self._d_uiCheckBoxes = {}
    
        #_MainForm = mUI.MelFormLayout(parent,ut='cgmUISubTemplate')
        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        _mainScroll = mUI.MelScrollLayout(_MainForm,useTemplate = 'cgmUIHeaderTemplate') 

        _mappingFrame = mUI.MelFrameLayout(_mainScroll, label='Create Mapping', collapsable=True, collapse=False,useTemplate = 'cgmUIHeaderTemplate')
        
        self.mappingColumn = mUI.MelColumnLayout(_mappingFrame,useTemplate = 'cgmUISubTemplate') 

        buildColumn_create_mapping(self)

        _loadMappingFrame = mUI.MelFrameLayout(_mainScroll, label='Load Mappings', collapsable=True, collapse=False,useTemplate = 'cgmUIHeaderTemplate')
        
        self.loadMappingColumn = mUI.MelColumnLayout(_loadMappingFrame,useTemplate = 'cgmUISubTemplate') 

        _row = mUI.MelHSingleStretchLayout(self.loadMappingColumn,ut='cgmUISubTemplate',padding = _padding, height=75+_padding)

        mUI.MelSpacer(_row,w=_padding)

        _colorColumn = mUI.MelColumnLayout(_row,useTemplate = 'cgmUIHeaderTemplate', height=75 )
        self.mappingListTSL = cgmUI.cgmScrollList(_colorColumn, numberOfRows = 4, height=75)

        mUI.MelSpacer(_row,w=_padding)

        _row.setStretchWidget(_colorColumn)

        _row.layout()

        mc.setParent(self.loadMappingColumn)
        cgmUI.add_LineSubBreak()

        _row = mUI.MelHLayout(self.loadMappingColumn,ut='cgmUISubTemplate',padding = _padding*2)
        cgmUI.add_Button(_row,'Load From File',
            cgmGEN.Callback(uiFunc_load,self),
            #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
            'Load a mapping from file',h=30)
        cgmUI.add_Button(_row,'Remove Mapping',
            cgmGEN.Callback(uiFunc_remove_mapping,self),
            'Remove selected mapping',h=30) 

        _row.layout() 

        mc.setParent(self.loadMappingColumn)
        cgmUI.add_LineSubBreak()

        # Start GamePad Button
        #
        #_row = mUI.MelHLayout(_mainScroll,ut='cgmUISubTemplate',padding = _padding*2)
        
        self.animDrawBtn = cgmUI.add_Button(_mainScroll,'Start GamePad',
            cgmGEN.Callback(start_controller,self),                         
            #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
            'Start Gamepad Button',h=50)

        #_row.layout()    
        #
        # End Recording Button

        _row_cgm = cgmUI.add_cgmFooter(_MainForm)            
        _MainForm(edit = True,
                  af = [(_mainScroll,"top",0),
                        (_mainScroll,"left",0),
                        (_mainScroll,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(_mainScroll,"bottom",2,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])          

def uiFunc_add_mapping_to_list(self):
    self.mappingList.append( copy.copy(self.connectionDict) )
    uiFunc_update_mapping_list(self)

def uiFunc_update_mapping_list(self):
    self.mappingListTSL.clear()
    self.mappingListTSL.setItems( [x['name'] for x in self.mappingList] )

def uiFunc_remove_mapping(self):
    self.mappingList.pop(self.mappingListTSL.getSelectedIdx())
    uiFunc_update_mapping_list(self)

def uiFunc_save(self):
    log.info("Saving")
    basicFilter = "*.cfg"
    filename = mc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, fm=0)
    if not filename:
        return
    filename = filename[0]
    f = open(filename, 'w')
    f.write( json.dumps(self.mappingList) )
    f.close()

    if not filename in self.recentMappings:
        self.recentMappings.append(filename)
        self.recentOptionStore.setValue( json.dumps(self.recentMappings) )

def uiFunc_load(self, filename = None):
    log.info("Loading")
    basicFilter = "*.cfg"

    if filename is None:
        filename = mc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, fm=1)
        if not filename:
            return
        filename = filename[0]
        if not filename in self.recentMappings:
            self.recentMappings.append(filename)
            self.recentOptionStore.setValue( json.dumps(self.recentMappings) )

    f = open(filename, 'r')
    self.mappingList = json.loads(f.read())

    uiFunc_update_mapping_list(self)

def buildColumn_create_mapping(self):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """   
    self.mappingColumn.clear()

    # if asScroll:
    #     _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUISubTemplate') 
    # else:
    #     _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
    
    #>>>Objects Load Row ---------------------------------------------------------------------------------------
    _inside = self.mappingColumn

    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()

    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = _padding)        
    
    mUI.MelSpacer(_row,w=_padding)

    mUI.MelLabel(_row,l='Name:')

    self.nameTF = mUI.MelTextField(_row, text=self.connectionDict['name'], editable = True, bgc=[0,0,0], cc=cgmGEN.Callback(uiFunc_update_connectionDict_name,self))

    _row.setStretchWidget(self.nameTF)

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()

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

    # Add/Clear Mapping Buttons
    #
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = _padding*2)
    
    cgmUI.add_Button(_row,'Add Mapping',
        cgmGEN.Callback(uiFunc_add_mapping_to_list,self),                         
        'Add Mapping Button',h=30)

    cgmUI.add_Button(_row,'Clear Mapping',
        cgmGEN.Callback(uiFunc_clear_connection_dict,self),                         
        'Add Mapping Button',h=30)

    _row.layout()
    #
    # End Add/Clear Mapping Buttons

    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()

    return _inside

def uiFunc_build_controller_connection_column(self, parent, connection):
    mc.setParent(parent)
    cgmUI.add_LineSubBreak()

    # Connection Column
    #
    connectionColumn = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate')

    for label in self.connectionDict[connection]:
        add_connection_row(self, connectionColumn, connection, label, self.connectionDict[connection][label])
    #
    # End Connection Column

    _row = mUI.MelHLayout(parent,ut='cgmUISubTemplate',padding = _padding)
    
    btn = cgmUI.add_Button(_row,'Add Connection',
        cgmGEN.Callback(add_connection,self, connectionColumn, connection),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Add Connection Button',h=25)

    btn = cgmUI.add_Button(_row,'Clear All',
        cgmGEN.Callback(uiFunc_clear_connections,self, connectionColumn, connection),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Clear Connections Button',h=25)
    _row.layout()

    mc.setParent(parent)
    cgmUI.add_LineSubBreak()

def add_connection_row(self, parent, connection, label, connectionInfo):
    # Add Connection
    #
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row,l='Target:')

    conLabel = mUI.MelLabel(_row,ut='cgmUIInstructionsTemplate',l=label,en=False)

    _row.setStretchWidget( conLabel )

    mUI.MelLabel(_row,l='Min:')
    ff_min = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, precision = 2, v=connectionInfo['min'])

    mUI.MelLabel(_row,l='Max:')
    ff_max = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, precision = 2, v=connectionInfo['max'])

    mUI.MelLabel(_row,l='Damp:')
    ff_damp = mUI.MelFloatField(_row, ut='cgmUISubTemplate', w= 50, precision = 2, v=connectionInfo['damp'])

    ff_min(edit=True, cc=cgmGEN.Callback(uiFunc_change_connection,self,connection, label, ff_min, ff_max, ff_damp))
    ff_max(edit=True, cc=cgmGEN.Callback(uiFunc_change_connection,self,connection, label, ff_min, ff_max, ff_damp))
    ff_damp(edit=True, cc=cgmGEN.Callback(uiFunc_change_connection,self,connection, label, ff_min, ff_max, ff_damp))

    cgmUI.add_Button(_row,'X',
                     cgmGEN.Callback(uiFunc_remove_connection,self,_row, connection, label),
                     "Remove connection.")  

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()
    #
    # End Add Connection

def uiFunc_clear_connections(self, parent, connection):
    parent.clear()
    self.connectionDict[connection] = {}

def uiFunc_clear_connection_dict(self):
    self.connectionDict = { 'name':'Default',
                            'RStickHorizontal':{},
                            'RStickVertical':{},
                            'LStickHorizontal':{},
                            'LStickVertical':{},
                            'RTrigger':{},
                            'LTrigger':{} }

    buildColumn_create_mapping(self)

def add_connection(self, parent, connection):
    for obj in mc.ls(sl=True):
        for attr in mc.channelBox('mainChannelBox', q=True, sma=True ):
            connectionString = '{0}.{1}'.format(obj, attr)
            self.connectionDict[connection][connectionString] = {'min':-1, 'max':1, 'damp':10}

            add_connection_row(self, parent, connection, connectionString, self.connectionDict[connection][connectionString])

def uiFunc_update_connectionDict_name(self):
    self.connectionDict['name'] = self.nameTF.getValue()

def uiFunc_change_connection(self, connection, connectionString, minUI, maxUI, dampUI):
    self.connectionDict[connection][connectionString]['min'] = minUI.getValue()
    self.connectionDict[connection][connectionString]['max'] = maxUI.getValue()
    self.connectionDict[connection][connectionString]['damp'] = dampUI.getValue()

def uiFunc_remove_connection(self,row,connection,label):
    if label in self.connectionDict[connection]:
        del self.connectionDict[connection][label]
    mc.deleteUI(row)

def start_controller(self):
    self.animDrawBtn(edit=True, en=False)
    self.animDrawBtn(edit=True, label="Stop Controller", bgc=[.35,1,.35])
    mc.refresh()
    self.controllerPuppet = controllerPuppet.ControllerPuppet(self.mappingList, onEnded=cgmGEN.Callback(stop_controller,self))
    self.controllerPuppet.start()

def stop_controller(self):
    self.controllerPuppet = None
    self.animDrawBtn(edit=True, en=True)

    self.animDrawBtn(edit=True, label="Start Controller", bgc=[.35,.35,.35])

