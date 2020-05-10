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
from cgm.core.lib import search_utils as SEARCH

import cgm.core.rig.dynamic_utils as RIGDYN

#>>> Root settings =============================================================
__version__ = '0.05052020'
__toolname__ ='dynFKTool'

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
    _row_objLoad = mUI.MelHSingleStretchLayout(_inside,ut='cgmUITemplate',padding = 5)        

    mUI.MelSpacer(_row_objLoad,w=10)
    mUI.MelLabel(_row_objLoad, 
                 l='Dynamic Chain System:')

    uiTF_objLoad = mUI.MelLabel(_row_objLoad,ut='cgmUITemplate',l='',
                                en=True)

    self.uiTF_objLoad = uiTF_objLoad
    cgmUI.add_Button(_row_objLoad,'<<',
                     cgmGEN.Callback(uiFunc_load_selected,self),
                     "Load first selected object.")  
    _row_objLoad.setStretchWidget(uiTF_objLoad)
    mUI.MelSpacer(_row_objLoad,w=10)

    _row_objLoad.layout()

    self.detailsFrame = mUI.MelFrameLayout(_inside, label="Details", collapsable=True, collapse=True)

    uiFunc_update_details(self)

    # Create Frame

    self.createFrame = mUI.MelFrameLayout(_inside, label="Create", collapsable=True, collapse=False)

    _create = mUI.MelColumnLayout(self.createFrame,useTemplate = 'cgmUISubTemplate') 

    self.itemList = cgmUI.cgmScrollList(_create, numberOfRows = 8, height=100)
    self.itemList(edit=True, allowMultiSelection=False)

    cgmUI.add_Button(_create,'Add Selected',
                     cgmGEN.Callback(uiFunc_add_selected,self),
                     "Load selected objects.")

    cgmUI.add_LineSubBreak()

    cgmUI.add_Button(_create,'Make Dynamic Chain',
                     cgmGEN.Callback(uiFunc_make_dynamic_chain,self),
                     "Make Dynamic Chain.")

    cgmUI.add_LineSubBreak()

    self.optionsFrame = mUI.MelFrameLayout(_create, label="Options", collapsable=True, collapse=True)

    """
    _row_objLoad.layout()

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
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUITemplate',padding = 5)        

    mUI.MelSpacer(_row,w=10)
    mUI.MelLabel(_row, 
                 l=label)

    uiTF = mUI.MelLabel(_row,ut='cgmUITemplate',l=text,
                                en=True)

    if button:
        cgmUI.add_Button(_row,buttonLabel,
                         buttonCommand,
                         buttonInfo)  
    _row.setStretchWidget(uiTF)
    mUI.MelSpacer(_row,w=10)

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
        mUI.MelSpacer(_row,w=10)

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

    _details = mUI.MelColumnLayout(self.detailsFrame,useTemplate = 'cgmUISubTemplate') 

    # Base Name
    uiFunc_make_display_line(_details, label='Base Name:', text=self._mDynFK.baseName, button=False)

    # Direction Info
    _row = mUI.MelHSingleStretchLayout(_details,ut='cgmUITemplate',padding = 5)        

    mUI.MelSpacer(_row,w=10)
    mUI.MelLabel(_row, 
                 l="Fwd:")

    uiTF = mUI.MelLabel(_row,ut='cgmUITemplate',l=self._mDynFK.fwd,
                                en=True)

    _row.setStretchWidget(mUI.MelSpacer(_row,w=10))

    mUI.MelLabel(_row, 
                 l="Up:")

    uiTF = mUI.MelLabel(_row,ut='cgmUITemplate',l=self._mDynFK.up,
                                en=True)

    mUI.MelSpacer(_row,w=10)
    _row.layout()


    # Nucleus
    uiFunc_make_display_line(_details, label='Nucleus:', text=dat['mNucleus'].p_nameBase, button=True, buttonLabel = ">>", buttonCommand=cgmGEN.Callback(uiFunc_select_item,dat['mNucleus'].p_nameBase), buttonInfo="Select nucleus transform.", presetOptions=True, presetObj=dat['mNucleus'].p_nameBase)

    uiFunc_make_display_line(_details, label='Hair System:', text=dat['mHairSysShape'].p_nameBase, button=True, buttonLabel = ">>", buttonCommand=cgmGEN.Callback(uiFunc_select_item,dat['mHairSysShape'].p_nameBase), buttonInfo="Select hair system transform.", presetOptions=True, presetObj=dat['mHairSysShape'].p_nameBase)
    # Start Times

    _rowStartTimes = mUI.MelHSingleStretchLayout(_details,ut='cgmUITemplate',padding = 5)        

    mUI.MelSpacer(_rowStartTimes,w=10)
    mUI.MelLabel(_rowStartTimes, 
                 l='Start Time:')

    _rowStartTimes.setStretchWidget(mUI.MelSpacer(_rowStartTimes,w=10))

    self.startTimeIF = mUI.MelIntField(_rowStartTimes, v=dat['mNucleus'].startFrame )
    self.startTimeIF(edit=True, changeCommand=cgmGEN.Callback(uiFunc_set_start_time,self))
    
    mUI.MelSpacer(_rowStartTimes,w=10)
    _rowStartTimes.layout()

    # TimeInput Row ----------------------------------------------------------------------------------
    _row_time = mUI.MelHSingleStretchLayout(_details,ut='cgmUISubTemplate')
    mUI.MelSpacer(_row_time)
    mUI.MelLabel(_row_time,l='start')

    self.uiFieldInt_start = mUI.MelIntField(_row_time,'cgmLocWinStartFrameField',
                                            width = 40)
    _row_time.setStretchWidget( mUI.MelSpacer(_row_time) )
    mUI.MelLabel(_row_time,l='end')

    self.uiFieldInt_end = mUI.MelIntField(_row_time,'cgmLocWinEndFrameField',
                                          width = 40)
    
    uiFunc_updateTimeRange(self)

    mUI.MelSpacer(_row_time)
    _row_time.layout()   


    allChains = []
    for idx in dat['chains']:
        allChains += dat['chains'][idx]['mObjJointChain']
    allTargets = []
    for idx in dat['chains']:
        allTargets += dat['chains'][idx]['mTargets']

    _row_bake = mUI.MelHLayout(_details,ut='cgmUISubTemplate',padding = 1)
    cgmUI.add_Button(_row_bake,'Bake All Joints',
        cgmGEN.Callback(uiFunc_bake,self,'chain', allChains),                         
        #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
        'Bake All Joints')
    cgmUI.add_Button(_row_bake,'Bake All Targets',
        cgmGEN.Callback(uiFunc_bake,self,'target', allTargets),                         
        'Bake All Targets') 

    _row_bake.layout()    

    # Chains
    for idx in dat['chains']:
        chainDat = dat['chains'][idx]

        _row_chains = mUI.MelHSingleStretchLayout(_details,ut='cgmUITemplate',padding = 5)        

        mUI.MelSpacer(_row_chains,w=10)
        chainFrame = mUI.MelFrameLayout(_row_chains, label=chainDat['mGrp'].p_nameBase, collapsable=True, collapse=True)
        
        _chainColumn = mUI.MelColumnLayout(chainFrame,useTemplate = 'cgmUISubTemplate') 
        _row_chains.setStretchWidget(chainFrame)

        mUI.MelSpacer(_row_chains,w=10)
        _row_chains.layout()

        uiFunc_make_display_line(_chainColumn, label='Follicle:', text=chainDat['mFollicle'].p_nameShort, button=True, buttonLabel = ">>", buttonCommand=cgmGEN.Callback(uiFunc_select_item,chainDat['mFollicle'].p_nameBase), buttonInfo="Select follicle transform.", presetOptions=True, presetObj = chainDat['mFollicle'].p_nameBase)
        uiFunc_make_display_line(_chainColumn, label='Group:', text=chainDat['mGrp'].p_nameShort, button=True, buttonLabel = ">>", buttonCommand=cgmGEN.Callback(uiFunc_select_item,chainDat['mGrp'].p_nameBase), buttonInfo="Select group transform.")

        _row_bake = mUI.MelHLayout(_chainColumn,ut='cgmUISubTemplate',padding = 1)
        cgmUI.add_Button(_row_bake,'Bake Joints',
            cgmGEN.Callback(uiFunc_bake,self,'chain', chainDat['mObjJointChain']),                         
            #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
            'Bake All Joints')
        cgmUI.add_Button(_row_bake,'Bake Targets',
            cgmGEN.Callback(uiFunc_bake,self,'target', chainDat['mTargets']),                         
            'Bake All Targets') 

        _row_bake.layout()    

        frameDat = [['Targets', 'mTargets'],
                    ['Locators','mLocs'],
                    ['Joint Chain', 'mObjJointChain'],
                    ['Aims', 'mAims'],
                    ['Parents', 'mParents']]

        for dat in frameDat:
            frame = mUI.MelFrameLayout(_chainColumn, label=dat[0], collapsable=True, collapse=True)
            column = mUI.MelColumnLayout(frame,useTemplate = 'cgmUISubTemplate') 
            uiFunc_create_selection_list(column, [x.p_nameShort for x in chainDat[dat[1]]] )

    # End Chains

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


def uiFunc_updateTimeRange(self, mode='slider'):
    _range = SEARCH.get_time(mode)
    if _range:
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


def uiFunc_set_start_time(self):
    self._mDynFK.get_dat()['mNucleus'].startFrame = self.startTimeIF(q=True, v=True)

def uiFunc_add_selected(self):
    self.itemList.setItems(mc.ls(sl=True))

def uiFunc_select_nucleus(self):
    mc.select(self._mDynFK.get_dat()['mNucleus'].p_nameBase)

def uiFunc_make_dynamic_chain(self):
    if not self._mDynFK:
        mDynFK = RIGDYN.cgmDynFK(baseName='hair')
        mDynFK.profile_load('base')
        uiFunc_load_dyn_chain(self, mDynFK.p_nameBase)
    else:
        pass


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
        return
    
    _short = self._mDynFK.p_nameBase
    self.uiTF_objLoad(edit=True, ann=_short)
    
    if len(_short)>20:
        _short = _short[:20]+"..."
    self.uiTF_objLoad(edit=True, l=_short)   
    
    self.uiTF_objLoad(edit=True, en=True)

    uiFunc_update_details(self)
    
    return


 