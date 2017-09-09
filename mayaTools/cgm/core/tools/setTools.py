"""
------------------------------------------
transformTools: cgm.core.tools
Author: Josh Burton
email: jjburton@cgmonks.com

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
log.setLevel(logging.INFO)

import maya.cmds as mc

import cgm.core.classes.GuiFactory as cgmUI
from cgm.core import cgm_RigMeta as cgmRigMeta
mUI = cgmUI.mUI

from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.search_utils as SEARCH


"""
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import name_utils as NAMES
import cgm.core.lib.position_utils as POS
import cgm.core.lib.transform_utils as TRANS
from cgm.core.lib import list_utils as LISTS
from cgm.core.tools.markingMenus.lib import contextual_utils as CONTEXT
from cgm.core.cgmPy import str_Utils as STRINGS
from cgm.core.tools import attrTools as ATTRTOOLS
from cgm.core.rigger.lib import spacePivot_utils as SPACEPIVOT
from cgm.core.cgmPy import path_Utils as CGMPATH
import cgm.core.lib.math_utils as MATH
from cgm.lib import lists"""

#>>> Root settings =============================================================
__version__ = '0.09052017'


_l_setTypes = ['NONE',
               'animation',
               'layout',
               'modeling',
               'td',
               'fx',
               'lighting']    

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmSetTools_ui'    
    WINDOW_TITLE = 'cgmSetTools - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 285,400
    TOOLNAME = 'setTools.ui'
     
    
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
        
        uiSetupOptionVars(self)
        
        
        self.l_objectSets = []
        self.l_setModes = ['<<< All Loaded Sets >>>','<<< Active Sets >>>']
        self.setMode = 0
        
        #self.uiPopUpMenu_createShape = None
        #self.uiPopUpMenu_color = None
        #self.uiPopUpMenu_attr = None
        #self.uiPopUpMenu_raycastCreate = None

        #self.create_guiOptionVar('matchFrameCollapse',defaultValue = 0) 
        #self.create_guiOptionVar('rayCastFrameCollapse',defaultValue = 0) 
        #self.create_guiOptionVar('aimFrameCollapse',defaultValue = 0) 

    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))
        #self.uiMenu_Buffers = mUI.MelMenu( l='Buffers', pmc = cgmGEN.Callback(self.buildMenu_buffer))

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

        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')            
        
        _column = buildSetsForm_main(self,_MainForm)
        
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
        
        
def uiFunc_modeSet( self, item ):
    i =  self.setModes.index(item)
    self.SetToolsModeOptionVar.set( i )
    self.setMode = i

def uiSetupOptionVars(self):
    #self.HideSetGroupOptionVar = OptionVarFactory('cgmVar_HideSetGroups', defaultValue = 1)
    #self.HideNonQssOptionVar = OptionVarFactory('cgmVar_HideNonQss', defaultValue = 1)		
    
    self.var_ActiveSets = cgmMeta.cgmOptionVar('cgmVar_activeObjectSets', defaultValue = [''])
    self.var_ActiveSetRefs = cgmMeta.cgmOptionVar('cgmVar_activeObjectSetRefs', defaultValue = [''])
    self.var_ActiveSetTypes = cgmMeta.cgmOptionVar('cgmVar_activeObjectSetTypes', defaultValue = [''])
    self.var_setMode = cgmMeta.cgmOptionVar('cgmVar_objectSetMode', defaultValue = 0)
    self.var_hideNonQSS = cgmMeta.cgmOptionVar('cgmVar_objectSetHideNonQSS', defaultValue = 1)
    self.var_hideAnimLayerSets = cgmMeta.cgmOptionVar('cgmVar_HideAnimLayerSets', defaultValue = 1)
    self.var_hideMayaSets= cgmMeta.cgmOptionVar('cgmVar_HideMayaObjectSets', defaultValue = 1)
    
def uiFunc_createSet(self):
    _str_func = 'uiFunc_createSet'
    log.warning("|{0}| >> Finish...".format(_str_func))  
    
def uiFunc_setAllSets(self,active = False):
    _str_func = 'uiFunc_setAllSets'
    log.warning("|{0}| >> Finish...".format(_str_func)) 
    
def uiFunc_multiSetsAction(self,mode = None):
    _str_func = 'uiFunc_multiSetsAction'
    log.warning("|{0}| >> Finish...".format(_str_func)) 
    
def uiFunc_multiSetsSetType(self,setType = None, qss = None):
    _str_func = 'uiFunc_multiSetsSetType'
    log.warning("|{0}| >> Finish...".format(_str_func)) 
uiFunc_multiSetsSetType
    
def buildSetsForm_main(self,parent):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """
    def modeSet( item ):
        i =  self.l_setModes.index(item)
        self.var_setMode.setValue( i )
        self.setMode = i    
        
    _MainForm = mUI.MelFormLayout(parent, useTemplate = 'cgmUISubTemplate')


    #>>>  Snap Section
    _Header = cgmUI.add_Header('Sets')
    
    #>> Logic ----------------------------------------------------------------------------------------
    activeState = True
    i = 1
    if self.l_objectSets:
        for b in self.l_objectSets:
            if b not in self.var_ActiveSets.value:
                activeState = False
    else:
        activeState = False    
        
    #>>>All Sets Row ----------------------------------------------------------------------------------
    _uiRow_allSets = mUI.MelHSingleStretchLayout(_MainForm, bgc = cgmUI.guiBackgroundColor)
    
    """
    mc.button(parent=_uiRow_allSets ,
              ut = 'cgmUITemplate',                                                                                                
              l = '+',
              c = cgmGEN.Callback(uiFunc_valuesTweak,self,'+'),
              ann = "Adds value relatively to current")   """
    
    mUI.MelSpacer(parent = _uiRow_allSets, w = 5)
    
    mUI.MelCheckBox(parent = _uiRow_allSets,
                    annotation = 'Sets all sets active',
                    value = activeState,
                    onCommand =  cgmGEN.Callback(uiFunc_setAllSets,self,True),
                    offCommand = cgmGEN.Callback(uiFunc_setAllSets,self,False))
    
    # Mode toggle box
    self.SetModeOptionMenu = mUI.MelOptionMenu(_uiRow_allSets,cc=modeSet)
                                               #cc = lambda *a:uiFunc_modeSet(self))
    for m in self.l_setModes:
        self.SetModeOptionMenu.append(m)
    
    self.SetModeOptionMenu.selectByIdx(self.setMode,False)
    
    _uiRow_allSets.setStretchWidget(self.SetModeOptionMenu)
    
    mUI.MelSpacer(parent = _uiRow_allSets, w = 2)
    mc.button(parent=_uiRow_allSets ,
                 ut = 'cgmUITemplate',                                                                                                
                 l = 'K',
                 c = cgmGEN.Callback(uiFunc_multiSetsAction,self,'key'),
                 ann = "Key all sets")
    
    #mUI.MelSpacer(parent = _uiRow_allSets, w = 2)
    mc.button(parent=_uiRow_allSets ,
                 ut = 'cgmUITemplate',                                                                                                
                 l = 'D',
                 c = cgmGEN.Callback(uiFunc_multiSetsAction,self,'delete'),
                 ann = "Delete all keys of sets") 
    
    #mUI.MelSpacer(parent = _uiRow_allSets, w = 2)
    mc.button(parent=_uiRow_allSets ,
                 ut = 'cgmUITemplate',                                                                                                
                 l = 'R',
                 c = cgmGEN.Callback(uiFunc_multiSetsAction,self,'reset'),
                 ann = "Reset all active sets") 
    
    mUI.MelSpacer(parent = _uiRow_allSets, w = 5)    
    _uiRow_allSets.layout()
    
    #>>>Pop up menu ----------------------------------------------------------------------------------
    allPopUpMenu = mUI.MelPopupMenu(self.SetModeOptionMenu ,button = 3)

    allCategoryMenu = mUI.MelMenuItem(allPopUpMenu,
                                      label = 'Make Type:',
                                      sm = True)

    multiMakeQssMenu = mUI.MelMenuItem(allPopUpMenu,
                                       label = 'Make Qss',
                                       c = cgmGEN.Callback(uiFunc_multiSetsSetType,self,**{'qss':True}))
    multiMakeNotQssMenu = mUI.MelMenuItem(allPopUpMenu,
                                          label = 'Clear Qss State',
                                          c = cgmGEN.Callback(uiFunc_multiSetsSetType,self,**{'qss':False}))
    #Mulit set type
    for n in _l_setTypes:
        mUI.MelMenuItem(allCategoryMenu,
                        label = n,
                        c = cgmGEN.Callback(uiFunc_multiSetsSetType,self,**{'setType':n}))
                        
                        #c = Callback(setToolsLib.doMultiSetType,self,self.SetToolsModeOptionVar.value,n))    


    #>>>Scroll List ----------------------------------------------------------------------------------
    SetListScroll = mUI.MelScrollLayout(_MainForm,cr = 1, ut = 'cgmUISubTemplate')
    
    self.uiScrollList_objectSets = SetListScroll
    SetMasterForm = mUI.MelFormLayout(SetListScroll)
    SetListColumn = mUI.MelColumnLayout(SetMasterForm, adj = True, rowSpacing = 1)
    
    NewSetRow = mUI.MelHLayout(_MainForm)
    mc.button(parent=NewSetRow ,
                  ut = 'cgmUITemplate',                                                                                                
                  l = 'Create Set',
                  c = lambda *a:uiFunc_createSet(self),
                  ann = 'Create new buffer from selected buffer')    
    mc.button(parent=NewSetRow ,
              ut = 'cgmUITemplate',                                                                                                
              l = 'Update',
              c = lambda *a:uiUpdate_objectSets(self),
              ann = 'Force the ui to update')	    
    NewSetRow.layout()

    """
    NewSetRow = guiFactory.doButton2(MainForm,
                                     'Create Set',
                                     lambda *a:setToolsLib.doCreateSet(self),
                                     'Create new buffer from selected buffer')	"""    
    
    
    _MainForm(edit = True,
             af = [(_Header,"top",0),
                   (_Header,"left",0),
                   (_Header,"right",0),
                   (_uiRow_allSets,"left",0),
                   (_uiRow_allSets,"right",0),
                   (SetListScroll,"left",0),
                   (SetListScroll,"right",0),
                   (NewSetRow,"left",0),
                   (NewSetRow,"right",0),
                   (NewSetRow,"bottom",0)],
             ac = [(_uiRow_allSets,"top",0,_Header),
                   (SetListScroll,"top",2,_uiRow_allSets),
                   (SetListScroll,"bottom",0,NewSetRow)],
             attachNone = [(NewSetRow,"top")])       

    return _MainForm


    #>>> Sets building section
    allPopUpMenu = MelPopupMenu(self.SetModeOptionMenu ,button = 3)

    allCategoryMenu = MelMenuItem(allPopUpMenu,
                                  label = 'Make Type:',
                                  sm = True)

    multiMakeQssMenu = MelMenuItem(allPopUpMenu,
                                   label = 'Make Qss',
                                   c = Callback(setToolsLib.doMultiSetQss,self,True))
    multiMakeNotQssMenu = MelMenuItem(allPopUpMenu,
                                      label = 'Clear Qss State',
                                      c = Callback(setToolsLib.doMultiSetQss,self,False))		
    #Mulit set type
    for n in self.setTypes:
        MelMenuItem(allCategoryMenu,
                    label = n,
                    c = Callback(setToolsLib.doMultiSetType,self,self.SetToolsModeOptionVar.value,n))


    #>>> Sets building section
    SetListScroll = MelScrollLayout(MainForm,cr = 1, ut = 'cgmUISubTemplate')
    SetMasterForm = MelFormLayout(SetListScroll)
    SetListColumn = MelColumnLayout(SetMasterForm, adj = True, rowSpacing = 3)

    self.objectSetsDict = {}
    self.activeSetsCBDict = {}

    for b in self.objectSets:
        #Store the info to a dict
        try:
            i = self.setInstancesFastIndex[b] # get the index
            sInstance = self.setInstances[i] # fast link to the instance
        except:
            raise StandardError("'%s' failed to query an active instance"%b)

        #see if the no no fields are enabled
        enabledMenuLogic = True
        if sInstance.mayaSetState or sInstance.refState:				
            enabledMenuLogic = False


        tmpSetRow = MelFormLayout(SetListColumn,height = 20)

        #Get check box state
        activeState = False
        if sInstance.nameShort in self.ActiveObjectSetsOptionVar.value:
            activeState = True
        tmpActive = MelCheckBox(tmpSetRow,
                                annotation = 'make set as active',
                                value = activeState,
                                onCommand =  Callback(setToolsLib.doSetSetAsActive,self,i),
                                offCommand = Callback(setToolsLib.doSetSetAsInactive,self,i))

        self.activeSetsCBDict[i] = tmpActive

        tmpSel = guiFactory.doButton2(tmpSetRow,
                                      ' s ',
                                      Callback(setToolsLib.doSelectSetObjects,self,i),
                                      'Select the set objects')


        tmpName = MelTextField(tmpSetRow, w = 100,ut = 'cgmUIReservedTemplate', text = sInstance.nameShort,
                               editable = enabledMenuLogic)

        tmpName(edit = True,
                ec = Callback(setToolsLib.doUpdateSetName,self,tmpName,i)	)


        tmpAdd = guiFactory.doButton2(tmpSetRow,
                                      '+',
                                      Callback(setToolsLib.doAddSelected,self,i),
                                      'Add selected  to the set',
                                      en = not sInstance.refState)
        tmpRem= guiFactory.doButton2(tmpSetRow,
                                     '-',
                                     Callback(setToolsLib.doRemoveSelected,self,i),
                                     'Remove selected  to the set',
                                     en = not sInstance.refState)
        tmpKey = guiFactory.doButton2(tmpSetRow,
                                      'k',
                                      Callback(setToolsLib.doKeySet,self,i),			                              
                                      'Key set')
        tmpDeleteKey = guiFactory.doButton2(tmpSetRow,
                                            'd',
                                            Callback(setToolsLib.doDeleteCurrentSetKey,self,i),			                              			                                
                                            'delete set key')	

        tmpReset = guiFactory.doButton2(tmpSetRow,
                                        'r',
                                        Callback(setToolsLib.doResetSet,self,i),			                              			                                
                                        'Reset Set')
        mc.formLayout(tmpSetRow, edit = True,
                      af = [(tmpActive, "left", 4),
                            (tmpReset,"right",2)],
                      ac = [(tmpSel,"left",0,tmpActive),
                            (tmpName,"left",2,tmpSel),
                            (tmpName,"right",4,tmpAdd),
                            (tmpAdd,"right",2,tmpRem),
                            (tmpRem,"right",2,tmpKey),
                            (tmpKey,"right",2,tmpDeleteKey),
                            (tmpDeleteKey,"right",2,tmpReset)
                            ])

        MelSpacer(tmpSetRow, w = 2)

        #Build pop up for text field
        popUpMenu = MelPopupMenu(tmpName,button = 3)
        MelMenuItem(popUpMenu,
                    label = "<<<%s>>>"%b,
                    enable = False)

        if not enabledMenuLogic:
            if sInstance.mayaSetState:
                MelMenuItem(popUpMenu,
                            label = "<Maya Default Set>",
                            enable = False)				
            if sInstance.refState:
                MelMenuItem(popUpMenu,
                            label = "<Referenced>",
                            enable = False)		

        qssState = sInstance.qssState
        qssMenu = MelMenuItem(popUpMenu,
                              label = 'Qss',
                              cb = qssState,
                              en = enabledMenuLogic,
                              c = Callback(self.setInstances[i].isQss,not qssState))

        categoryMenu = MelMenuItem(popUpMenu,
                                   label = 'Make Type:',
                                   sm = True,
                                   en = enabledMenuLogic)

        for n in self.setTypes:
            MelMenuItem(categoryMenu,
                        label = n,
                        c = Callback(setToolsLib.guiDoSetType,self,i,n))


        MelMenuItem(popUpMenu ,
                    label = 'Copy Set',
                    c = Callback(setToolsLib.doCopySet,self,i))

        MelMenuItem(popUpMenu ,
                    label = 'Purge',
                    en = enabledMenuLogic,
                    c = Callback(setToolsLib.doPurgeSet,self,i))

        MelMenuItemDiv(popUpMenu)
        MelMenuItem(popUpMenu ,
                    label = 'Delete',
                    en = enabledMenuLogic,
                    c = Callback(setToolsLib.doDeleteSet,self,i))	



    NewSetRow = guiFactory.doButton2(MainForm,
                                     'Create Set',
                                     #lambda *a:setToolsLib.doCreateSet(self),
                                     lambda *a:uiUpdate_objectSets(self),
                                     'Create new buffer from selected buffer')	

    SetMasterForm(edit = True,
                  af = [(SetListColumn,"top",0),
                        (SetListColumn,"left",0),
                        (SetListColumn,"right",0),
                        (SetListColumn,"bottom",0)])

    MainForm(edit = True,
             af = [(SetHeader,"top",0),
                   (SetHeader,"left",0),
                   (SetHeader,"right",0),
                   (HelpInfo,"left",0),
                   (HelpInfo,"right",0),
                   (AllSetsRow,"left",0),
                   (AllSetsRow,"right",0),
                   (SetListScroll,"left",0),
                   (SetListScroll,"right",0),
                   (NewSetRow,"left",4),
                   (NewSetRow,"right",4),
                   (NewSetRow,"bottom",4)],
             ac = [(HelpInfo,"top",0,SetHeader),
                   (AllSetsRow,"top",2,HelpInfo),
                   (SetListScroll,"top",2,AllSetsRow),
                   (SetListScroll,"bottom",0,NewSetRow)],
             attachNone = [(NewSetRow,"top")])    
    
    return MainForm

def uiBuild_objectSetRow(self, parent = None, index = None):
    _str_func = 'uiBuild_objectSetRow'
    
    #Get our data
    try:_mObjectSet = self._ml_sets[i]
    except:
        log.error("|{0}| >> Filed to find data for index: {1}".format(_str_func,index))
        return False
    
    _index = index
    
    
    #Store the info to a dict
    _row = mUI.MelHSingleStretchLayout(parent)#bgc = cgmUI.guiBackgroundColor
        
    """
    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = '+',
              c = cgmGEN.Callback(uiFunc_valuesTweak,self,'+'),
              ann = "Adds value relatively to current")   """
    
    mUI.MelSpacer(parent = _row, w = 5)
    
    mUI.MelCheckBox(parent = _row,
                    annotation = 'Sets all sets active',
                    value = activeState,
                    onCommand =  cgmGEN.Callback(uiFunc_setAllSets,self,True),
                    offCommand = cgmGEN.Callback(uiFunc_setAllSets,self,False))
    
    # Mode toggle box
    self.SetModeOptionMenu = mUI.MelOptionMenu(_row,cc=modeSet)
                                               #cc = lambda *a:uiFunc_modeSet(self))
    for m in self.l_setModes:
        self.SetModeOptionMenu.append(m)
    
    self.SetModeOptionMenu.selectByIdx(self.setMode,False)
    
    _row.setStretchWidget(self.SetModeOptionMenu)
    
    mUI.MelSpacer(parent = _row, w = 2)
    mc.button(parent=_row ,
                 ut = 'cgmUITemplate',                                                                                                
                 l = 'K',
                 c = cgmGEN.Callback(uiFunc_multiSetsAction,self,'key'),
                 ann = "Key all sets")
    
    #mUI.MelSpacer(parent = _row, w = 2)
    mc.button(parent=_row ,
                 ut = 'cgmUITemplate',                                                                                                
                 l = 'D',
                 c = cgmGEN.Callback(uiFunc_multiSetsAction,self,'delete'),
                 ann = "Delete all keys of sets") 
    
    #mUI.MelSpacer(parent = _row, w = 2)
    mc.button(parent=_row ,
                 ut = 'cgmUITemplate',                                                                                                
                 l = 'R',
                 c = cgmGEN.Callback(uiFunc_multiSetsAction,self,'reset'),
                 ann = "Reset all active sets") 
    
    mUI.MelSpacer(parent = _row, w = 5)    
    _row.layout()

    
    
    return

    #see if the no no fields are enabled
    enabledMenuLogic = True
    if sInstance.mayaSetState or sInstance.refState:				
        enabledMenuLogic = False


    tmpSetRow = MelFormLayout(SetListColumn,height = 20)

    #Get check box state
    activeState = False
    if sInstance.nameShort in self.ActiveObjectSetsOptionVar.value:
        activeState = True
    tmpActive = MelCheckBox(tmpSetRow,
                            annotation = 'make set as active',
                            value = activeState,
                            onCommand =  Callback(setToolsLib.doSetSetAsActive,self,i),
                            offCommand = Callback(setToolsLib.doSetSetAsInactive,self,i))

    self.activeSetsCBDict[i] = tmpActive

    tmpSel = guiFactory.doButton2(tmpSetRow,
                                  ' s ',
                                  Callback(setToolsLib.doSelectSetObjects,self,i),
                                  'Select the set objects')


    tmpName = MelTextField(tmpSetRow, w = 100,ut = 'cgmUIReservedTemplate', text = sInstance.nameShort,
                           editable = enabledMenuLogic)

    tmpName(edit = True,
            ec = Callback(setToolsLib.doUpdateSetName,self,tmpName,i)	)


    tmpAdd = guiFactory.doButton2(tmpSetRow,
                                  '+',
                                  Callback(setToolsLib.doAddSelected,self,i),
                                  'Add selected  to the set',
                                  en = not sInstance.refState)
    tmpRem= guiFactory.doButton2(tmpSetRow,
                                 '-',
                                 Callback(setToolsLib.doRemoveSelected,self,i),
                                 'Remove selected  to the set',
                                 en = not sInstance.refState)
    tmpKey = guiFactory.doButton2(tmpSetRow,
                                  'k',
                                  Callback(setToolsLib.doKeySet,self,i),			                              
                                  'Key set')
    tmpDeleteKey = guiFactory.doButton2(tmpSetRow,
                                        'd',
                                        Callback(setToolsLib.doDeleteCurrentSetKey,self,i),			                              			                                
                                        'delete set key')	

    tmpReset = guiFactory.doButton2(tmpSetRow,
                                    'r',
                                    Callback(setToolsLib.doResetSet,self,i),			                              			                                
                                    'Reset Set')
    mc.formLayout(tmpSetRow, edit = True,
                  af = [(tmpActive, "left", 4),
                        (tmpReset,"right",2)],
                  ac = [(tmpSel,"left",0,tmpActive),
                        (tmpName,"left",2,tmpSel),
                        (tmpName,"right",4,tmpAdd),
                        (tmpAdd,"right",2,tmpRem),
                        (tmpRem,"right",2,tmpKey),
                        (tmpKey,"right",2,tmpDeleteKey),
                        (tmpDeleteKey,"right",2,tmpReset)
                        ])

    MelSpacer(tmpSetRow, w = 2)

    #Build pop up for text field
    popUpMenu = MelPopupMenu(tmpName,button = 3)
    MelMenuItem(popUpMenu,
                label = "<<<%s>>>"%b,
                enable = False)

    if not enabledMenuLogic:
        if sInstance.mayaSetState:
            MelMenuItem(popUpMenu,
                        label = "<Maya Default Set>",
                        enable = False)				
        if sInstance.refState:
            MelMenuItem(popUpMenu,
                        label = "<Referenced>",
                        enable = False)		

    qssState = sInstance.qssState
    qssMenu = MelMenuItem(popUpMenu,
                          label = 'Qss',
                          cb = qssState,
                          en = enabledMenuLogic,
                          c = Callback(self.setInstances[i].isQss,not qssState))

    categoryMenu = MelMenuItem(popUpMenu,
                               label = 'Make Type:',
                               sm = True,
                               en = enabledMenuLogic)

    for n in self.setTypes:
        MelMenuItem(categoryMenu,
                    label = n,
                    c = Callback(setToolsLib.guiDoSetType,self,i,n))


    MelMenuItem(popUpMenu ,
                label = 'Copy Set',
                c = Callback(setToolsLib.doCopySet,self,i))

    MelMenuItem(popUpMenu ,
                label = 'Purge',
                en = enabledMenuLogic,
                c = Callback(setToolsLib.doPurgeSet,self,i))

    MelMenuItemDiv(popUpMenu)
    MelMenuItem(popUpMenu ,
                label = 'Delete',
                en = enabledMenuLogic,
                c = Callback(setToolsLib.doDeleteSet,self,i))	    


def uiUpdate_objectSets(self):
    """ 
    Gets sccene set objects, and sorts the data in to the class as varaibles
    """ 
    _str_func = 'uiUpdate_objectSets'
    
    _d_sets = SEARCH.get_objectSetsDict()
    pprint.pprint(_d_sets)
    
    self.uiScrollList_objectSets.clear()
    
    for oSet in _d_sets.get('all',[]):
        print oSet
        _l = mUI.MelLabel(self.uiScrollList_objectSets,
                          label = oSet)
    
    
    
    return
    self.refPrefixes = self.objectSetsRaw['referenced'].keys()
    self.refSetsDict = self.objectSetsRaw['referenced'] or {}
    self.setTypesDict = self.objectSetsRaw['cgmTypes'] or {}
    self.setGroups = self.objectSetsRaw['objectSetGroups'] or []
    #Set Group stuff
    self.setGroupName = False

    for s in self.setGroups:
        if s in self.refSetsDict.get('From Scene'):
            self.setGroupName = s
            self.setsGroup = SetFactory(s)
            break

    self.mayaSets = self.objectSetsRaw['maya'] or []
    self.qssSets = self.objectSetsRaw['qss'] or []

    self.sortedSets = []
    self.objectSets = []
    self.activeSets = []

    #Sort sets we want to actually load
    self.sortedSets = []

    #Sort for activeRefs
    tmpActiveRefSets = []
    if self.ActiveRefsOptionVar.value:
        for r in self.ActiveRefsOptionVar.value:
            #If value, let's add or subtract based on if our set refs are found
            if self.refSetsDict.get(r):
                tmpActiveRefSets.extend(self.refSetsDict.get(r))

    #Sort for active types  
    tmpActiveTypeSets = []
    if self.setTypesDict.keys() and self.ActiveTypesOptionVar.value:
        for t in self.setTypesDict.keys():
            if t in self.ActiveTypesOptionVar.value and self.setTypesDict.get(t):	    
                tmpActiveTypeSets.extend(self.setTypesDict.get(t))

    if tmpActiveTypeSets and tmpActiveRefSets:
        self.sortedSets = lists.returnMatchList(tmpActiveTypeSets,tmpActiveRefSets)
    elif tmpActiveTypeSets:
        self.sortedSets = tmpActiveTypeSets
    else:
        self.sortedSets = tmpActiveRefSets


    #Next step, hiding. First get our cull lists
    if self.sortedSets:
        self.objectSets = self.sortedSets
    else:
        self.objectSets = self.objectSetsRaw['all']

    # Start pulling out stuff by making a list we can iterate through as culling from a list you're iterating through doesn't work
    bufferList = copy.copy(self.objectSets)

    # Hide Set groups
    if mc.optionVar(q='cgmVar_HideSetGroups'):
        for s in self.setGroups:
            try:self.objectSets.remove(s)
            except:pass


    # Hide animLayer Sets
    if mc.optionVar(q='cgmVar_HideAnimLayerSets'):
        for s in bufferList:
            if search.returnObjectType(s) == 'animLayer':
                try:self.objectSets.remove(s)
                except:pass


    # Hide Maya Sets
    if mc.optionVar(q='cgmVar_HideMayaSets'):
        for s in self.mayaSets:
            try:self.objectSets.remove(s)
            except:pass


    # Hide non qss Sets
    #print self.qssSets
    #print self.objectSets
    if mc.optionVar(q='cgmVar_HideNonQss'):
        #print "sorting for qss"
        for s in bufferList:
            if s not in self.qssSets and s not in self.setGroups:
                try:self.objectSets.remove(s)
                except:pass 


    #Refresh our active lists    
    if self.ActiveObjectSetsOptionVar.value:
        for o in self.objectSets:
            if o in self.ActiveObjectSetsOptionVar.value:
                self.activeSets.append(o) 

    self.setInstances = {}
    self.setInstancesFastIndex = {}

    #If we have object sets to load, we're gonna initialize em
    if self.objectSets:
        #Counter build
        mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(self.objectSetsRaw),"Getting Set info")

        for i,o in enumerate(self.objectSets):
            if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                break
            mc.progressBar(mayaMainProgressBar, edit=True, status = ("On set %s"%(o)), step=1)                    	

            self.setInstances[i] = SetFactory(o) #Store the instance so we only have to do it once
            sInstance = self.setInstances[i] #Simple link to keep the code cleaner

            self.setInstancesFastIndex[o] = i #Store name to index for fast lookup of index on the fly

        guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

    # Set Group creation if they don't have em
    #if mc.optionVar( q='cgmVar_MaintainLocalSetGroup' ) and not self.setGroupName:
    #    initializeSetGroup(self)

    #if mc.optionVar( q='cgmVar_MaintainLocalSetGroup' ):
    #    doGroupLocal(self)