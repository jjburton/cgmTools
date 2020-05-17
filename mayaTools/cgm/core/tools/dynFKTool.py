"""
------------------------------------------
dynFKTool : cgm.core.tools
Author: David Bokser
email: dbokser@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
cgmSimChain tool
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
from cgm.core.lib import search_utils as SEARCH

import cgm.core.rig.dynamic_utils as RIGDYN

#>>> Root settings =============================================================
__version__ = '0.05052020'
__toolname__ ='cgmSimChain'

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
    DEFAULT_SIZE = 550,350
    TOOLNAME = '{0}.ui'.format(__toolname__)
    
    _mDynFK = False

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

 
    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))

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
    
    def do_dock( self):
        _str_func = 'do_dock'
        #log.info("dockCnt: {0}".format(self.dockCnt))
        #log.debug("uiDock: {0}".format(self.uiDock))                
        #log.debug("area: {0}".format(self.l_allowedDockAreas[self.var_DockSide.value]))
        #log.debug("label: {0}".format(self.WINDOW_TITLE))
        #log.debug("self: {0}".format(self.Get()))                
        #log.debug("content: {0}".format(self.WINDOW_NAME))
        #log.debug("floating: {0}".format(not self.var_Dock.value))
        #log.debug("allowedArea: {0}".format(self.l_allowedDockAreas))
        #log.debug("width: {0}".format(self.DEFAULT_SIZE[0])) 
        try:
            self.uiDock
        except:
            log.debug("|{0}| >> making uiDock attr".format(_str_func)) 
            self.uiDock = False
            
        _dock = '{0}Dock'.format(self.__toolName__)   
        _l_allowed = self.__class__.l_allowedDockAreas
        
  
        _content = self.Get()
            
        if mc.dockControl(_dock,q=True, exists = True):
            log.debug('linking...')
            self.uiDock = _dock
            mc.dockControl(_dock , edit = True, area=_l_allowed[self.var_DockSide.value],
                           label=self.WINDOW_TITLE, content=_content,
                           allowedArea=_l_allowed,
                           width=self.DEFAULT_SIZE[0], height = self.DEFAULT_SIZE[1])                    
        #else:
        else:
            log.debug('creating...')       
            mc.dockControl(_dock , area=_l_allowed[self.var_DockSide.value],
                           label=self.WINDOW_TITLE, content=_content,
                           allowedArea=_l_allowed,
                           width=self.DEFAULT_SIZE[0], height = self.DEFAULT_SIZE[1]) 
            self.uiDock = _dock
        
        
        """log.info("floating: {0}".format(mc.dockControl(_dock, q = True, floating = True)))
        log.info("var_Doc: {0}".format(self.var_Dock.value))
        _floating = mc.dockControl(_dock, q = True, floating = True)
        if _floating and self.var_Dock == 1:
            log.info('mismatch')
            self.var_Dock = 0
        if not _floating and self.var_Dock == 0:
            log.info("mismatch2")
            self.var_Dock = 1"""
        
        mc.dockControl(_dock, edit = True, floating = self.var_Dock.value, width=self.DEFAULT_SIZE[0], height = self.DEFAULT_SIZE[1])
        self.uiDock = _dock   
        _floating = mc.dockControl(_dock, q = True, floating = True)            
        if _floating:
            #log.info("Not visible, resetting position.")
            #mc.dockControl(self.uiDock, e=True, visible = False)
            mc.window(_dock, edit = True, tlc = [200, 200])
        self.var_Dock.toggle()


def buildColumn_main(self,parent, asScroll = False):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """   
    if asScroll:
        _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUIHeaderTemplate') 
    else:
        _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUIHeaderTemplate') 
    

    #>>>Objects Load Row ---------------------------------------------------------------------------------------
    
    mUI.MelSeparator(_inside,ut='cgmUISubTemplate',h=3)

    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)        

    mUI.MelSpacer(_row,w=_padding)

    mUI.MelLabel(_row, 
                 l='Dynamic Chain System:')

    uiTF_objLoad = mUI.MelLabel(_row,ut='cgmUIInstructionsTemplate',l='',
                                en=True)

    self.uiTF_objLoad = uiTF_objLoad
    cgmUI.add_Button(_row,'<<',
                     cgmGEN.Callback(uiFunc_load_selected,self),
                     "Load first selected object.")  
    _row.setStretchWidget(uiTF_objLoad)
    mUI.MelSpacer(_row,w=_padding)

    _row.layout()

    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()

    self.detailsFrame = mUI.MelFrameLayout(_inside, label="Details", collapsable=True, collapse=True,useTemplate = 'cgmUIHeaderTemplate')

    uiFunc_update_details(self)

    # Create Frame

    self.createFrame = mUI.MelFrameLayout(_inside, label="Create", collapsable=True, collapse=False,useTemplate = 'cgmUIHeaderTemplate')

    _create = mUI.MelColumnLayout(self.createFrame,useTemplate = 'cgmUIHeaderTemplate') 

    cgmUI.add_LineSubBreak()

    _row = mUI.MelHSingleStretchLayout(_create,ut='cgmUISubTemplate',padding = _padding)

    mUI.MelSpacer(_row,w=_padding)
    
    _subRow = mUI.MelColumnLayout(_row,useTemplate = 'cgmUIHeaderTemplate') 
    self.itemList = cgmUI.cgmScrollList(_subRow, numberOfRows = 8, height=100)
    self.itemList(edit=True, allowMultiSelection=True)

    mUI.MelSpacer(_row,w=_padding)

    _row.setStretchWidget( _subRow )

    _row.layout()

    mUI.MelSeparator(_create,ut='cgmUISubTemplate',h=5)

    _row = mUI.MelHSingleStretchLayout(_create,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)

    addBtn = cgmUI.add_Button(_row,'Add Selected',
                     cgmGEN.Callback(uiFunc_list_function,self.itemList, 'add selected'),
                     "Load selected objects.")

    cgmUI.add_Button(_row,'Remove Selected',
                     cgmGEN.Callback(uiFunc_list_function,self.itemList, 'remove selected'),
                     "Remove selected objects.")

    cgmUI.add_Button(_row,'Clear',
                     cgmGEN.Callback(uiFunc_list_function,self.itemList, 'clear'),
                     "Clear all objects.")

    _row.setStretchWidget( addBtn )

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()

    cgmUI.add_LineSubBreak()

    _row = mUI.MelHSingleStretchLayout(_create,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)

    _row.setStretchWidget( cgmUI.add_Button(_row,'Make Dynamic Chain',
                     cgmGEN.Callback(uiFunc_make_dynamic_chain,self),
                     "Make Dynamic Chain.") )

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()    

    cgmUI.add_LineSubBreak()

    self.optionsFrame = mUI.MelFrameLayout(_create, label="Options", collapsable=True, collapse=True,useTemplate = 'cgmUIHeaderTemplate')

    _options = mUI.MelColumnLayout(self.optionsFrame,useTemplate = 'cgmUISubTemplate') 

    mUI.MelSeparator(_options,ut='cgmUISubTemplate',h=5)

    _row = mUI.MelHSingleStretchLayout(_options,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)                          
    mUI.MelLabel(_row,l='Base Name: ')        

    self.options_baseName = mUI.MelTextField(_row,
            ann='Name',
            text = 'DynamicChain')

    _row.setStretchWidget( self.options_baseName )

    mUI.MelSpacer(_row,w=_padding)
    _row.layout()

    _row = mUI.MelHSingleStretchLayout(_options,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row,w=_padding)                          
    mUI.MelLabel(_row,l='Name: ')        

    self.options_name = mUI.MelTextField(_row,
            ann='Name',
            text = '')

    _row.setStretchWidget( self.options_name )

    mUI.MelSpacer(_row,w=_padding)
    _row.layout()

    mUI.MelSeparator(_options,ut='cgmUISubTemplate',h=5)

    _row = mUI.MelHSingleStretchLayout(_options,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=_padding)                          
    mUI.MelLabel(_row,l='Direction:')  

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    directions = ['x+', 'x-', 'y+', 'y-', 'z+', 'z-']

    mUI.MelLabel(_row,l='Fwd:') 

    self.fwdMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
    for dir in directions:
        self.fwdMenu.append(dir)
    
    self.fwdMenu.setValue('z+')

    mUI.MelSpacer(_row,w=_padding)
    
    mUI.MelLabel(_row,l='Up:')

    self.upMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
    for dir in directions:
        self.upMenu.append(dir)

    self.upMenu.setValue('y+')

    mUI.MelSpacer(_row,w=_padding)

    _row.layout()

    """
    _row.layout()

    #>>>Report ---------------------------------------------------------------------------------------
    _row_report = mUI.MelHLayout(_inside ,ut='cgmUIInstructionsTemplate',h=20)
    self.uiField_report = mUI.MelLabel(_row_report,
                                       bgc = SHARED._d_gui_state_colors.get('help'),
                                       label = '...',
                                       h=20)
    _row_report.layout() """

    return _inside

def uiFunc_process_preset_change(obj, optionMenu):
    val = optionMenu.getValue()

    if val == "Save Preset":
        result = mc.promptDialog(
                title='Save Preset',
                message='Preset Name:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

        if result == 'OK':
            text = mc.promptDialog(query=True, text=True)
            if mc.nodePreset(isValidName=text):
                mc.nodePreset( save=(obj, text) )
                optionMenu.clear()

                optionMenu.append("Load Preset")
                for a in mc.nodePreset( list=obj ):
                    optionMenu.append(a)
                optionMenu.append("---")
                optionMenu.append("Save Preset")

                optionMenu.setValue(text)
            else:
                print "Invalid name, try again"
                optionMenu.setValue("Load Preset")
    elif mc.nodePreset(isValidName=val):
        if mc.nodePreset(exists=(obj, val)):
            mc.nodePreset( load=(obj, optionMenu.getValue()) )

def uiFunc_make_display_line(parent, label="", text="", button=False, buttonLabel = ">>", buttonCommand=None, buttonInfo="", presetOptions=False, presetObj=None):
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = _padding)        

    mUI.MelSpacer(_row,w=_padding)
    mUI.MelLabel(_row, 
                 l=label)

    uiTF = mUI.MelLabel(_row,ut='cgmUIInstructionsTemplate',l=text,
                                en=True)

    if button:
        cgmUI.add_Button(_row,buttonLabel,
                         buttonCommand,
                         buttonInfo)
    
    _row.setStretchWidget(uiTF)

    if presetOptions:
        presetMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
        presetMenu.append("Load Preset")
        for a in mc.nodePreset( list=presetObj ):
            presetMenu.append(a)
        presetMenu.append("---")
        presetMenu.append("Save Preset")
        presetMenu(edit=True,
            value = "Load Preset",
            cc = cgmGEN.Callback(uiFunc_process_preset_change, presetObj, presetMenu) )
        
    mUI.MelSpacer(_row,w=_padding)

    _row.layout()

    return uiTF

def uiFunc_bake(self, mode):
    pass

def uiFunc_update_details(self):
    if not self._mDynFK:
        return

    self.detailsFrame.clear()

    dat = self._mDynFK.get_dat()

    self.detailsFrame(edit=True, collapse=False)

    _details = mUI.MelColumnLayout(self.detailsFrame,useTemplate = 'cgmUIHeaderTemplate') 

    cgmUI.add_LineSubBreak()

    # Base Name
    uiFunc_make_display_line(_details, label='Base Name:', text=self._mDynFK.baseName, button=False)

    # Direction Info
    _row = mUI.MelHSingleStretchLayout(_details,ut='cgmUISubTemplate',padding = 5)        

    mUI.MelSpacer(_row,w=_padding)

    mUI.MelLabel(_row, l="Direction:")

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mUI.MelLabel(_row, l="Fwd:")

    uiTF = mUI.MelLabel(_row,ut='cgmUISubTemplate',l=self._mDynFK.fwd,
                                en=True)

    mUI.MelLabel(_row, 
                 l="Up:")

    uiTF = mUI.MelLabel(_row,ut='cgmUISubTemplate',l=self._mDynFK.up,
                                en=True)

    mUI.MelSpacer(_row,w=10)
    _row.layout()


    # Nucleus
    uiFunc_make_display_line(_details, label='Nucleus:', text=self._mDynFK.mNucleus[0], button=True, buttonLabel = ">>", buttonCommand=cgmGEN.Callback(uiFunc_select_item,self._mDynFK.mNucleus[0]), buttonInfo="Select nucleus transform.", presetOptions=True, presetObj=self._mDynFK.mNucleus[0])

    uiFunc_make_display_line(_details, label='Hair System:', text=dat['mHairSysShape'].p_nameBase, button=True, buttonLabel = ">>", buttonCommand=cgmGEN.Callback(uiFunc_select_item,dat['mHairSysShape'].p_nameBase), buttonInfo="Select hair system transform.", presetOptions=True, presetObj=dat['mHairSysShape'].p_nameBase)

    _row = mUI.MelHSingleStretchLayout(_details,ut='cgmUISubTemplate',padding = 5)        

    mUI.MelSpacer(_row,w=_padding)

    mUI.MelLabel(_row, 
                 l='Enabled:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.nucleusEnabledCB = mUI.MelCheckBox(_row,en=True,
                               v = True,
                               label = '',
                               ann='Enable Nucleus') 
    self.nucleusEnabledCB(edit=True, changeCommand=cgmGEN.Callback(uiFunc_set_nucleus_enabled,self))
    
    mUI.MelSpacer(_row,w=_padding)
    
    _row.layout()

    # Start Times

    _row = mUI.MelHSingleStretchLayout(_details,ut='cgmUISubTemplate',padding = 5)        

    mUI.MelSpacer(_row,w=_padding)

    mUI.MelLabel(_row, 
                 l='Start Time:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    self.startTimeIF = mUI.MelIntField(_row, v=dat['mNucleus'].startFrame )
    self.startTimeIF(edit=True, changeCommand=cgmGEN.Callback(uiFunc_set_start_time,self, mode='refresh'))
    
    cgmUI.add_Button(_row,'<<',
                     cgmGEN.Callback(uiFunc_set_start_time,self, mode='beginning'),
                     "Set Start To Beginning of Slider.")  

    mUI.MelSpacer(_row,w=_padding)
    
    _row.layout()


    # TimeInput Row ----------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(_details,ut='cgmUISubTemplate')
    mUI.MelSpacer(_row, w=_padding)

    mUI.MelLabel(_row,l='Bake Time:')

    _row.setStretchWidget( mUI.MelSeparator(_row) )

    mUI.MelLabel(_row,l='Start:')

    self.uiFieldInt_start = mUI.MelIntField(_row,'cgmLocWinStartFrameField',
                                            width = 40)
    
    mUI.MelLabel(_row,l='End:')

    self.uiFieldInt_end = mUI.MelIntField(_row,'cgmLocWinEndFrameField',
                                          width = 40)
    
    cgmUI.add_Button(_row,'<<',
                     cgmGEN.Callback(uiFunc_updateTimeRange,self, 'min'),
                     "Set Start To Beginning of Slider.")  
    cgmUI.add_Button(_row,'[   ]',
                     cgmGEN.Callback(uiFunc_updateTimeRange,self, 'slider'),
                     "Set Time to Slider.")  
    cgmUI.add_Button(_row,'>>',
                     cgmGEN.Callback(uiFunc_updateTimeRange,self, 'max'),
                     "Set End To End of Slider.")  

    uiFunc_updateTimeRange(self, mode='slider')

    mUI.MelSpacer(_row, w=_padding)

    _row.layout()   

    mc.setParent(_details)
    cgmUI.add_LineSubBreak()

    allChains = []
    for idx in dat['chains']:
        allChains += dat['chains'][idx]['mObjJointChain']
    allTargets = []
    for idx in dat['chains']:
        allTargets += dat['chains'][idx]['mTargets']

    _row = mUI.MelHLayout(_details,ut='cgmUISubTemplate',padding = _padding*2)
    
    cgmUI.add_Button(_row,'Bake All Joints',
        cgmGEN.Callback(uiFunc_bake,self,'chain', allChains),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Bake All Joints')
    cgmUI.add_Button(_row,'Bake All Targets',
        cgmGEN.Callback(uiFunc_bake,self,'target', allTargets),                         
        'Bake All Targets') 

    _row.layout()    


    _row = mUI.MelHLayout(_details,ut='cgmUISubTemplate',padding = _padding*2)
    
    cgmUI.add_Button(_row,'Connect All Targets',
        cgmGEN.Callback(uiFunc_connect_targets, self),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Connect All Targets')
    cgmUI.add_Button(_row,'Disconnect All Targets',
        cgmGEN.Callback(uiFunc_disconnect_targets, self),                         
        'Disconnect All Targets') 

    _row.layout()   

    # Chains
    for i,chain in enumerate(self._mDynFK.msgList_get('chain')):
        _row = mUI.MelHSingleStretchLayout(_details,ut='cgmUISubTemplate',padding = _padding)        

        mUI.MelSpacer(_row,w=_padding)

        _subChainColumn = mUI.MelColumnLayout(_row,useTemplate = 'cgmUIHeaderTemplate') 

        chainFrame = mUI.MelFrameLayout(_subChainColumn, label=chain.p_nameBase, collapsable=True, collapse=True,useTemplate = 'cgmUIHeaderTemplate')
        
        _chainColumn = mUI.MelColumnLayout(chainFrame,useTemplate = 'cgmUIHeaderTemplate') 

        _row.setStretchWidget(_subChainColumn)

        #mUI.MelSpacer(_row,w=_padding)
        _row.layout()

        mc.setParent(_chainColumn)
        cgmUI.add_LineSubBreak()

        uiFunc_make_display_line(_chainColumn, label='Follicle:', text=cgmMeta.asMeta(chain.mFollicle[0]).p_nameBase, button=True, buttonLabel = ">>", buttonCommand=cgmGEN.Callback(uiFunc_select_item,chain.mFollicle[0]), buttonInfo="Select follicle transform.", presetOptions=True, presetObj = chain.mFollicle[0])
        
        mc.setParent(_chainColumn)
        cgmUI.add_LineSubBreak()

        uiFunc_make_display_line(_chainColumn, label='Group:', text=chain.p_nameShort, button=True, buttonLabel = ">>", buttonCommand=cgmGEN.Callback(uiFunc_select_item,chain.p_nameBase), buttonInfo="Select group transform.")

        mc.setParent(_chainColumn)
        cgmUI.add_LineSubBreak()

        _row = mUI.MelHSingleStretchLayout(_chainColumn,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=_padding)                          
        mUI.MelLabel(_row,l='Orient Up:')  

        _row.setStretchWidget( mUI.MelSeparator(_row) )

        chainDirections = []
        for dir in ['x+', 'x-', 'y+', 'y-', 'z+', 'z-']:
            if chain.fwd[0] != dir[0]:
                chainDirections.append(dir)
        chainDirections.append('None')
       
        upMenu = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
        for dir in chainDirections:
            upMenu.append(dir)

        upMenu.setValue( chain.up )

        upMenu(edit=True, changeCommand=cgmGEN.Callback(uiFunc_set_chain_up,self,i,upMenu))

        mUI.MelSpacer(_row,w=_padding)

        _row.layout()

        _row = mUI.MelHLayout(_chainColumn,ut='cgmUISubTemplate',padding = _padding*2)
        cgmUI.add_Button(_row,'Bake Joints',
            cgmGEN.Callback(uiFunc_bake,self,'chain', chain.msgList_get('mObjJointChain')),                         
            #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
            'Bake All Joints')
        cgmUI.add_Button(_row,'Bake Targets',
            cgmGEN.Callback(uiFunc_bake,self,'target', chain.msgList_get('mTargets')),                         
            'Bake All Targets') 

        _row.layout()    

        _row = mUI.MelHLayout(_chainColumn,ut='cgmUISubTemplate',padding = _padding*2)
    
        cgmUI.add_Button(_row,'Connect Targets',
            cgmGEN.Callback(uiFunc_connect_targets, self, i),                         
            #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
            'Connect All Targets')
        cgmUI.add_Button(_row,'Disconnect Targets',
            cgmGEN.Callback(uiFunc_disconnect_targets, self, i),                         
            'Disconnect All Targets') 

        _row.layout()  

        _row = mUI.MelHLayout(_chainColumn,ut='cgmUISubTemplate',padding = _padding*2)
        cgmUI.add_Button(_row,'Delete Chain',
            cgmGEN.Callback(uiFunc_delete_chain,self, i),                         
            #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
            'Bake All Joints')
        _row.layout()  

        frameDat = [['Targets', 'mTargets'],
                    ['Locators','mLocs'],
                    ['Joint Chain', 'mObjJointChain'],
                    ['Aims', 'mAims'],
                    ['Parents', 'mParents']]

        for dat in frameDat:
            frame = mUI.MelFrameLayout(_chainColumn, label=dat[0], collapsable=True, collapse=True,useTemplate = 'cgmUIHeaderTemplate')
            column = mUI.MelColumnLayout(frame,useTemplate = 'cgmUITemplate',height=75) 
            row = mUI.MelHSingleStretchLayout(column,ut='cgmUIHeaderTemplate',padding = _padding)

            mUI.MelSpacer(row,w=_padding)

            itemList = uiFunc_create_selection_list(row, [x.p_nameShort for x in chain.msgList_get(dat[1])] )

            mUI.MelSpacer(row,w=_padding)

            row.setStretchWidget(itemList)

            row.layout()

    # End Chains

    mc.setParent(_details)
    cgmUI.add_LineSubBreak()

def uiFunc_delete_chain(self, idx):
    self._mDynFK.chain_deleteByIdx(idx)
    uiFunc_update_details(self)

def uiFunc_connect_targets(self, idx=None):
    self._mDynFK.targets_connect(idx)

def uiFunc_disconnect_targets(self, idx=None):
    self._mDynFK.targets_disconnect(idx)

def uiFunc_set_chain_up(self, idx, upMenu):
    #print "Changing up on %s to %s" % ( chain.p_nameBase, upMenu.getValue() )
    axis = upMenu.getValue()
    if axis == 'None':
        axis = None
    else:
        axis = VALID.simpleAxis(axis)
    self._mDynFK.chain_setOrientUpByIdx(idx, axis)

# mode - 'target', 'chain'
def uiFunc_bake(self, mode, mObjs):
    # if mode == 'target':
    #     pass
    # elif mode == 'chain':
    #mObjs = [cgmMeta.asMeta(x) for x in objs]
    for i in range(self.uiFieldInt_start.getValue(),self.uiFieldInt_end.getValue()):
        mc.currentTime(i, edit=True)
        for mObj in mObjs:
            mObj.doSnapTo(mObj.getMessageAsMeta('cgmMatchTarget'))
            mc.setKeyframe(mObj.mNode, at=['translate', 'rotate'])


def uiFunc_updateTimeRange(self, which='slider', mode='slider'):
    _range = SEARCH.get_time(mode)
    if _range:
        if which == "min":
            self.uiFieldInt_start(edit = True, value = _range[0])
        elif which == "max":
            self.uiFieldInt_end(edit = True, value = _range[1])
        elif which == "slider":
            self.uiFieldInt_start(edit = True, value = _range[0])
            self.uiFieldInt_end(edit = True, value = _range[1])

def uiFunc_select_item(item):
    mc.select( item )

def uiFunc_select_list_item(listElement):
    mc.select( listElement.getSelectedItems() )

def uiFunc_create_selection_list(parent, items):
    itemList = cgmUI.cgmScrollList(parent, numberOfRows = 4, height=75)
    itemList.setItems(items)
    itemList(edit=True, selectCommand=cgmGEN.Callback(uiFunc_select_list_item,itemList))

    return itemList

def uiFunc_set_nucleus_enabled(self):
    mc.setAttr('%s.enable' % self._mDynFK.mNucleus[0], self.nucleusEnabledCB.getValue())

def uiFunc_set_start_time(self,mode):
    if mode == 'beginning':
        self.startTimeIF(e=True, v=mc.playbackOptions(q=True, min=True))
    self._mDynFK.get_dat()['mNucleus'].startFrame = self.startTimeIF(q=True, v=True)

def uiFunc_list_function(uiElement, command):
    allItems = uiElement.getItems()
    selectedItems = uiElement.getSelectedItems()

    if command == "add selected":
        uiElement.rebuild()        
        uiElement.setItems( allItems + mc.ls(sl=True) )
    elif command == "remove selected":
        uiElement.rebuild()
        newList = []
        for item in allItems:
            if item not in selectedItems:
                newList.append( item )
        uiElement.setItems( newList )
    elif command == "clear":
        uiElement.rebuild()

def uiFunc_select_nucleus(self):
    mc.select(self._mDynFK.get_dat()['mNucleus'].p_nameBase)

def uiFunc_make_dynamic_chain(self):
    if not self._mDynFK:
        mDynFK = RIGDYN.cgmDynFK(baseName=self.options_baseName.getValue(), name=self.options_name.getValue(),objs=self.itemList.getItems(),fwd=self.fwdMenu.getValue(), up=self.upMenu.getValue(), startFrame=mc.playbackOptions(q=True, min=True))
        mDynFK.profile_load('base')
        uiFunc_load_dyn_chain(self, mDynFK.p_nameBase)
    else:
        self._mDynFK.chain_create(name = self.options_name.getValue(),objs=self.itemList.getItems(),fwd=self.fwdMenu.getValue(), up=self.upMenu.getValue())
        uiFunc_update_details(self)

    self.itemList.rebuild()

def uiFunc_load_dyn_chain(self, chain):
    _str_func = 'uiFunc_load_dyn_chain'  

    self._mDynFK = False

    mDynFK = RIGDYN.cgmDynFK(chain)

    #Get our raw data
    try:
        if mDynFK.mClass == 'cgmDynFK':
            _short = mDynFK.p_nameBase            
            log.debug("|{0}| >> Target: {1}".format(_str_func, _short))
            self._mDynFK = mDynFK
    except:
        log.warning("|{0}| >> Nothing selected.".format(_str_func))            
        uiFunc_clear_loaded(self)

    if self._mDynFK:
        uiFunc_updateTargetDisplay(self)

    #uiFunc_updateFields(self)
    #self.uiReport_do()
    #self.uiFunc_updateScrollAttrList()

def uiFunc_load_selected(self, bypassAttrCheck = False):
    _str_func = 'uiFunc_load_selected'  

    uiFunc_load_dyn_chain(self, mc.ls(sl=True)[0])

def uiFunc_clear_loaded(self):
    _str_func = 'uiFunc_clear_loaded'  
    self._mDynFK = False
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

    if not self._mDynFK:
        log.info("|{0}| >> No target.".format(_str_func))                        
        #No obj
        self.uiTF_objLoad(edit=True, l='',en=False)
        self._mGroup = False

        #for o in self._l_toEnable:
            #o(e=True, en=False)

        self.options_baseName(e=True, enable=True)

        return
    
    self.options_baseName.setValue(self._mDynFK.cgmName)

    self.options_baseName(e=True, enable=False)

    _short = self._mDynFK.p_nameBase
    self.uiTF_objLoad(edit=True, ann=_short)
    
    if len(_short)>20:
        _short = _short[:20]+"..."
    self.uiTF_objLoad(edit=True, l=_short)   
    
    self.uiTF_objLoad(edit=True, en=True)

    uiFunc_update_details(self)
    
    return


 