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

from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import name_utils as NAMES
import cgm.core.lib.position_utils as POS
reload(POS)
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.transform_utils as TRANS
from cgm.core.lib import list_utils as LISTS
from cgm.core.tools.markingMenus.lib import contextual_utils as CONTEXT
from cgm.core.cgmPy import str_Utils as STRINGS
from cgm.core.tools import attrTools as ATTRTOOLS
from cgm.core.rigger.lib import spacePivot_utils as SPACEPIVOT
from cgm.core.cgmPy import path_Utils as CGMPATH
from cgm.lib import lists
#>>> Root settings =============================================================
__version__ = '0.08312017'

__l_spaceModes = SHARED._d_spaceArgs.keys()
__l_pivots = SHARED._d_pivotArgs.keys()

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmTransformTools_ui'    
    WINDOW_TITLE = 'cgmTransformTools - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 425,350
    TOOLNAME = 'transformTools.ui'
    
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
        #self._d_uiCheckBoxes = {}
    
        #_MainForm = mUI.MelFormLayout(parent,ut='cgmUISubTemplate')
        buildColumn_main(self,parent)

def buildColumn_main(self,parent):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """
    self._d_transformAttrFields = {}
    self._d_transformRows = {}
    self._d_transformCBs = {}
    self._mTransformTarget = False
    
    _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
    
    #>>>Objects Load Row ---------------------------------------------------------------------------------------
    _row_objLoad = mUI.MelHSingleStretchLayout(_inside,ut='cgmUITemplate',padding = 5)        

    mUI.MelSpacer(_row_objLoad,w=10)
    mUI.MelLabel(_row_objLoad, 
                 l='Source:')

    uiTF_objLoad = mUI.MelLabel(_row_objLoad,ut='cgmUITemplate',l='',
                                en=True)

    #self.uiPopUpMenu_dynChild = mUI.MelPopupMenu(_utf_objLoad,button = 1)
    #mc.menuItem(self.uiPopUpMenu_dynChild,l='Select',c=lambda *a:(self._mNode.select()))

    self.uiTF_objLoad = uiTF_objLoad
    cgmUI.add_Button(_row_objLoad,'<<',
                     cgmGEN.Callback(uiFunc_load_selected,self),
                     "Load first selected object.")  
    cgmUI.add_Button(_row_objLoad,'Update',
                     cgmGEN.Callback(uiFunc_updateFields,self),
                     "Update with current values.")     
    cgmUI.add_Button(_row_objLoad,'Ctxt',
                     cgmGEN.Callback(uiFunc_getTargets,self),
                     "Get Targets")    
    _row_objLoad.setStretchWidget(uiTF_objLoad)
    mUI.MelSpacer(_row_objLoad,w=10)
    """
    _row_objLoad.layout()

    #>>>Report ---------------------------------------------------------------------------------------
    _row_report = mUI.MelHLayout(_inside ,ut='cgmUIInstructionsTemplate',h=20)
    self.uiField_report = mUI.MelLabel(_row_report,
                                       bgc = SHARED._d_gui_state_colors.get('help'),
                                       label = '...',
                                       h=20)
    _row_report.layout() """
    
    #buildRow_space(self,_inside,'source',__l_spaceModes)
    #buildRow_space(self,_inside,'targets',__l_spaceModes)
    buildRow_lockSource(self,_inside)
    
    buildRow_tweak(self, _inside)
    mc.setParent(_inside)    
    cgmUI.add_SectionBreak()  

    mc.setParent(_inside)
    
    cgmUI.add_Header('Values')
    cgmUI.add_SectionBreak()
    
    buildRow_vector(self,_inside,'translate')
    buildRow_vector(self,_inside,'position')
    buildRow_vector(self,_inside,'rotate')    
    buildRow_vector(self,_inside,'rotateAxis')
    buildRow_vector(self,_inside,'jointOrient')    
    buildRow_vector(self,_inside,'scale')
    buildRow_vector(self,_inside,'scaleLossy')
    buildRow_vector(self,_inside,'scalePivot')
    
    uiFunc_load_selected(self)
    
def buildRow_vector(self,parent,label='translate'):
    #>>>Vector -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row ,w=5)                                              
    mUI.MelLabel(_row ,l=label + ':')        
    _row.setStretchWidget(mUI.MelSeparator(_row )) 
    _base_str = 'uiff_{0}'.format(label)
    
    self._d_transformAttrFields[label] = {}
    self._d_transformRows[label] = _row
    
    self._d_transformCBs[label] = mUI.MelCheckBox(_row,
                                                  ann='Tweak the {0} value with relative buttons above'.format(label))
    
    for a in list('xyz'):
        mUI.MelLabel(_row ,l=a)
        _field = mUI.MelFloatField(_row , ut='cgmUISubTemplate', w= 60 )
        self.__dict__['{0}{1}'.format(_base_str,a.capitalize())] = _field
        self._d_transformAttrFields[label][a.capitalize()] = _field
        mc.button(parent=_row ,
                  ut = 'cgmUITemplate',                                                                                                
                  l = '>',
                  c = cgmGEN.Callback(uiFunc_valuesSend,self,label,a.capitalize()),
                  #c = lambda *a:uiFunc_valuesSend(self,label,a),
                  #c = lambda *a:TOOLBOX.uiFunc_vectorMeasureToField(self),
                  ann = "Send to targets")             

    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = '>>>',
              c = cgmGEN.Callback(uiFunc_valuesSend,self,label,None),
              #c = lambda *a:TOOLBOX.uiFunc_vectorMeasureToField(self),
              ann = "Measures vector between selected objects/components")        
    mUI.MelSpacer(_row ,w=5)                                              

    _row.layout()
    
def buildRow_tweak(self,parent):
    #>>>Vector -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5,en=False)
    mUI.MelSpacer(_row ,w=5)                                              
    mUI.MelLabel(_row ,l='Relative:')        
    _row.setStretchWidget(mUI.MelSeparator(_row )) 
    _base_str = 'uiff_transformTweak'
    
    #self._d_transformAttrFields[label] = {}
    #self._d_transformRows[label] = _row
    
    for a in list('xyz'):
        mUI.MelLabel(_row ,l=a)
        _field = mUI.MelFloatField(_row , ut='cgmUISubTemplate', w= 60 )
        self.__dict__['{0}{1}'.format(_base_str,a.capitalize())] = _field          

    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = '+',
              c = cgmGEN.Callback(uiFunc_valuesTweak,self,'+'),
              ann = "Adds value relatively to current") 
    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = '-',
              c = cgmGEN.Callback(uiFunc_valuesTweak,self,'-'),
              ann = "Subracts value relatively to current")         
    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = 'Zero',
              c = cgmGEN.Callback(uiFunc_valuesTweak,self,'zero'),
              ann = "Zero out the fields") 
    
    mUI.MelSpacer(_row ,w=5)                                              

    _row.layout() 
    
def buildRow_lockSource(self,parent):
    
    _plug = 'var_transformLockSource'
    
    self.__dict__[_plug] = cgmMeta.cgmOptionVar('cgmVar_transformLockSource', defaultValue = 1)        
    
    mPlug = self.__dict__[_plug]
    
    #>>>Row ====================================================================================
    uiRC = mUI.MelRadioCollection()

    _row1 = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row1,w=5)
    mUI.MelLabel(_row1,l='Lock Source: ')
    
    _row1.setStretchWidget( mUI.MelSeparator(_row1) )

    uiRC = mUI.MelRadioCollection()
    _on = mPlug.value

    for i,item in enumerate(['off','on']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row1,label=item,sl=_rb,
                          ann = "When locked, the source object will not be affected by value changes via the ui",
                          onCommand = cgmGEN.Callback(mPlug.setValue,i))

        mUI.MelSpacer(_row1,w=2)    

    _row1.layout()
    
def buildRow_space(self,parent,optionVarPrefix = 'source', options = __l_spaceModes):
    
    _plug = 'var_{0}TransSpaceMode'.format(optionVarPrefix)
    
    self.__dict__[_plug] = cgmMeta.cgmOptionVar('cgmVar_{0}TransSpaceMode'.format(optionVarPrefix), defaultValue = options[0])        
    
    mPlug = self.__dict__[_plug]
    
    #>>>Row ====================================================================================
    uiRC = mUI.MelRadioCollection()

    _row1 = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row1,w=5)
    mUI.MelLabel(_row1,l='{0} Space Mode'.format(optionVarPrefix.capitalize()))
    
    _row1.setStretchWidget( mUI.MelSeparator(_row1) )

    uiRC = mUI.MelRadioCollection()
    _on = mPlug.value

    for i,item in enumerate(options):
        if item == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row1,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(mPlug.setValue,item))

        mUI.MelSpacer(_row1,w=2)    

    _row1.layout()
     
def uiFunc_load_selected(self, bypassAttrCheck = False):
    _str_func = 'uiFunc_load_selected'  
    #self._ml_ = []
    self._mTransformTarget = False

    _sel = mc.ls(sl=True)

    #Get our raw data
    if _sel:
        mNode = cgmMeta.validateObjArg(_sel[0])
        _short = mNode.p_nameBase            
        log.debug("|{0}| >> Target: {1}".format(_str_func, _short))
        self._mTransformTarget = mNode

        uiFunc_updateTargetDisplay(self)
    else:
        log.warning("|{0}| >> Nothing selected.".format(_str_func))            
        uiFunc_clear_loaded(self)

    uiFunc_updateFields(self)
    #self.uiReport_do()
    #self.uiFunc_updateScrollAttrList()

def uiFunc_updateFields(self):
    _str_func = 'uiFunc_updateFields'
    #_type = VALID.get_mayaType(_short)
    
    if not self._mTransformTarget:
        raise ValueError,"No source"
    _short = self._mTransformTarget.mNode
    
    #_space = self.var_sourceTransSpaceMode.value
    #log.info("|{0}| >> Getting data. Space: {1} ".format(_str_func, _space))
    
    #_pos = POS.get(_short,'rp',_space)
    _info = POS.get_info(_short)
    
    pprint.pprint(_info)
    #pprint.pprint(self._d_transformAttrFields)
    _d_sectionToDatKey = {'rotate':'rotation'}
    
    for section in self._d_transformAttrFields.keys():
        log.info("|{0}| >> On {1}".format(_str_func,section))
        _s = section
        if _s in ['translate','rotate','position','rotateAxis','scalePivot']:
            _k = _d_sectionToDatKey.get(_s,_s)
            for i,v in enumerate(_info[_k]):
                self._d_transformAttrFields[_s]['XYZ'[i]].setValue(v)   
                
        elif _s == 'jointOrient':
            if ATTR.has_attr(_short,'jointOrient'):
                self._d_transformRows[_s](edit=True, vis=True)
                _v = ATTR.get(_short,'jointOrient')
                log.info("|{0}| >> jointOrient: {1}".format(_str_func,_v))                
                for i,v in enumerate(_v):
                    self._d_transformAttrFields[_s]['XYZ'[i]].setValue(v)
            else:
                self._d_transformRows[_s](edit=True, vis=False)
        elif _s == 'scale':
            for i,v in enumerate(ATTR.get(_short,'scale')):
                self._d_transformAttrFields[_s]['XYZ'[i]].setValue(v)  
        elif _s == 'scaleLossy':
            for i,v in enumerate(TRANS.scaleLossy_get(_short)):
                self._d_transformAttrFields[_s]['XYZ'[i]].setValue(v)            
        else:
            log.info("|{0}| >> Missing query for {1}".format(_str_func,section))
            
             
        
def uiFunc_getTargets(self):
    _str_func = 'uiFunc_getTargets'
    _b_lockSource = cgmMeta.cgmOptionVar('cgmVar_transformLockSource', defaultValue = 1).getValue()
    
    _targets = mc.ls(sl=True)
    _ml_targets = []
    if _targets:
        _ml_targets = cgmMeta.validateObjListArg(_targets,'cgmObject')
        
    if _b_lockSource and self._mTransformTarget:
        log.info("|{0}| >> lock Source on. Checking list".format(_str_func))
        if self._mTransformTarget in _ml_targets:
            _ml_targets.remove(self._mTransformTarget)
            log.info("|{0}| >> Removed source...".format(_str_func))            
        
    
    if not _ml_targets:
        log.info("|{0}| >> No targets selected".format(_str_func))                
        
    log.info("|{0}| >> targets...".format(_str_func))                
    for mObj in _ml_targets:
        print(mObj.mNode)
    
    return _ml_targets
    #_mTransformTargetself._mTransformTarget
    #pprint.pprint(vars())

def uiFunc_valuesSend(self,section=None,key=None):
    _str_func = 'uiFunc_valuesSend'
    
    _ml_targets = uiFunc_getTargets(self)
    if not _ml_targets:
        raise ValueError,"Must have targets"
    
    pprint.pprint(vars())
    
    _d_setAttrValues = {}
    
    if section in ['translate','rotate','scale']:
        _s = section
        if not key:
            for a in 'XYZ':
                _v = self._d_transformAttrFields[_s][a].getValue()
                _d_setAttrValues[_s+a]  = _v
        else:
            try:
                _v = self._d_transformAttrFields[_s][key].getValue()
                _d_setAttrValues[_s+key] = _v
            
            except Exception,err:
                log.error("|{0}| >> Failed to get key data. Section: {0} | key: {1}...".format(_str_func,section,key))                
                log.error(err)
          
    else:
        log.warning("|{0}| >> Havent' setup for {1}...".format(_str_func,section))                
    
    for a,v in _d_setAttrValues.iteritems():
        for mObj in _ml_targets:
            try:ATTR.set(mObj.mNode,a,_v)        
            except Exception,err:
                log.error("|{0}| >> Failed to get set data. Object: {0} | a: {1} | v: {2}...".format(_str_func,mObj.mNode,a,v))                
                log.error(err)
    
    pass

def uiFunc_valuesTweak(self,mode = '+'):
    _str_func = 'uiFunc_valuesTweak'
    pprint.pprint(vars())
    pass

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
    _str_func = 'uiFunc_updateDynParentDisplay'  
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
    if self.uiPopUpMenu_dynChild:
        self.uiPopUpMenu_dynChild.clear()
        self.uiPopUpMenu_dynChild.delete()
        self.uiPopUpMenu_dynChild = None

 
class uiOLD(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmTransformTools_ui'    
    WINDOW_TITLE = 'cgmTransformTools - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 250,300
    #_checkBoxKeys = ['shared','default','user','others']
    #__modes = 'space','orient','follow'
    
    def insert_init(self,*args,**kws):
            if kws:log.debug("kws: %s"%str(kws))
            if args:log.debug("args: %s"%str(args))
            log.info(self.__call__(q=True, title=True))
    
            self.__version__ = __version__
            self.__toolName__ = 'cgmMultiSet'		
            #self.l_allowedDockAreas = []
            self.WINDOW_TITLE = ui.WINDOW_TITLE
            self.DEFAULT_SIZE = ui.DEFAULT_SIZE

            self.uiPopUpMenu_parent = False
            self._l_toEnable = []
            self.create_guiOptionVar('dynParentMode',  defaultValue = ui.__modes[0])       
            self.uiScrollList_parents = False
            self._mNode = False
            self._mGroup = False
            self.uiPopUpMenu_dynChild = None
            
    def build_menus(self):
        self.uiMenu_switch = mUI.MelMenu( l='Switch', pmc=self.buildMenu_switch) 
        self.uiMenu_pivot = mUI.MelMenu( l='Pivot', pmc=self.buildMenu_pivot)         
        self.uiMenu_help = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)         
    
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
    
        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("https://docs.google.com/document/d/1ztN9wZfYunvGlao2iRL5WSc9oJTN021Bk6LNZqhbrL8/edit?usp=sharing");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )   
        mUI.MelMenuItem( self.uiMenu_help, l="Update Parent D",
                         c=lambda *a: self.uiFunc_updateDynParentDisplay )      
        
    def buildMenu_switch(self, *args):
        self.uiMenu_switch.clear()
        
        self._ml_objList = cgmMeta.validateObjListArg( CONTEXT.get_list(getTransform=True) )        
        uiMenu_changeSpace(self,self.uiMenu_switch,True)   
        
    def buildMenu_pivot(self, *args):
        self.uiMenu_pivot.clear()
        
        mUI.MelMenuItem( self.uiMenu_pivot, l="Add Single",
                         c=lambda *a: self.uiFunc_spacePivot_add(1) ) 
        mUI.MelMenuItem( self.uiMenu_pivot, l="Add Multiple",
                         c=lambda *a: self.uiFunc_spacePivot_addFromPrompt() )         
        mUI.MelMenuItem( self.uiMenu_pivot, l="Clear",
                         c=lambda *a: self.uiFunc_spacePivot_clear() )         
    

                
    def uiFunc_clear_loaded(self):
        _str_func = 'uiFunc_clear_loaded'  
        self._mNode = False
        self._mGroup = False
        self._utf_obj(edit=True, l='',en=False)      
        self.uiField_report(edit=True, l='...')
        #self.uiReport_objects()
        self.uiScrollList_parents.clear()
        
        for o in self._l_toEnable:
            o(e=True, en=False)        
        

    def uiFunc_load_selected(self, bypassAttrCheck = False):
        _str_func = 'uiFunc_load_selected'  
        self._ml_parents = []
        self._mNode = False
        
        _sel = mc.ls(sl=True)
            
        #Get our raw data
        if _sel:
            mNode = cgmMeta.validateObjArg(_sel[0])
            _short = mNode.p_nameBase            
            log.debug("|{0}| >> Target: {1}".format(_str_func, _short))
            self._mNode = mNode

            self.uiFunc_updateDynParentDisplay()
        else:
            log.warning("|{0}| >> Nothing selected.".format(_str_func))            
            self.uiFunc_clear_loaded()
            
        #self.uiReport_do()
        #self.uiFunc_updateScrollAttrList()
        

    def uiFunc_updateDynParentDisplay(self):
        _str_func = 'uiFunc_updateDynParentDisplay'  
        self.uiScrollList_parents.clear()
        
        if not self._mNode:
            log.info("|{0}| >> No target.".format(_str_func))                        
            #No obj
            self._utf_obj(edit=True, l='',en=False)
            self._mGroup = False
            
            for o in self._l_toEnable:
                o(e=True, en=False)
                
        _d = get_dict(self._mNode.mNode)
        
        self._utf_obj(edit=True, en=True)
        
        if self.uiPopUpMenu_dynChild:
            self.uiPopUpMenu_dynChild.clear()
            self.uiPopUpMenu_dynChild.delete()
            self.uiPopUpMenu_dynChild = None
        
        if _d:
            log.info("|{0}| >> dynParentGroup detected...".format(_str_func))
            
            _short = l=_d['dynChild'].p_nameBase
            self._utf_obj(edit=True, ann=_short)
            if len(_short)>20:
                _short = _short[:20]+"..."
            self._utf_obj(edit=True, l=_short)    
                                   
            self._mNode = _d['dynChild']
            self._mGroup = _d['dynGroup']
            
            _l_report = ["mode: {0}".format(_d['mode']),'targets: {0}'.format(len(_d['dynParents']))]
            
            if self._mNode.isReferenced():
                _l_report.insert(0,"Referenced!")
            self.uiField_report(edit=True, label = 'DynGroup: {0}'.format(' | '.join(_l_report)))                 
            
            self._uiList_modeButtons[_d['mode']].select()        
            
            for o in self._l_toEnable:
                o(e=True, en=True)  
                
            self.uiFunc_updateScrollParentList()
        else:
            log.info("|{0}| >> No dynParentGroup".format(_str_func))                        
            #Not dynParentGroup
            _short = self._mNode.p_nameShort            
            self._utf_obj(edit=True, ann=_short)
            if len(_short)>20:
                _short = _short[:20]+"..."
            self._utf_obj(edit=True, l=_short)
    
            self.uiField_report(edit=True, label = 'No dynParentGroup detected')
    
            for o in self._l_toEnable:
                o(e=True, en=False)               
                   
        self.uiPopUpMenu_dynChild = mUI.MelPopupMenu(self._utf_obj,button = 1)
        mc.menuItem(parent = self.uiPopUpMenu_dynChild,l='Select Loaded',c=lambda *a:(self._mNode.select()))
        if self._mGroup:
            mc.menuItem(parent = self.uiPopUpMenu_dynChild,l='Select dynGroup',c=lambda *a:(self._mGroup.select()))
        else:
            mc.menuItem(parent = self.uiPopUpMenu_dynChild,l='Select dynGroup',en=False)
            
        if _d and _d.get('dynParents'):
            mc.menuItem(parent = self.uiPopUpMenu_dynChild,l='Select dynParents',c=lambda *a:(mc.select([mObj.mNode for mObj in _d['dynParents']])))
        else:
            mc.menuItem(parent = self.uiPopUpMenu_dynChild,l='Select dynParents',en=False)
        
    def uiFunc_updateScrollParentList(self):
        _str_func = 'uiFunc_updateScrollParentList'          
        self.uiScrollList_parents.clear()
        
        if not self._mGroup:
            return False      
        
        ml_parents = self._mGroup.msgList_get('dynParents')
        
        _l_dat = []
        _len = len(ml_parents)        
        
        if not ml_parents:
            return False
        
        #...menu...
        _progressBar = cgmUI.doStartMayaProgressBar(_len,"Processing...")
        _mode = self._mGroup.dynMode
        
        try:
            for i,mObj in enumerate(ml_parents):
                _short = mObj.p_nameShort
                log.debug("|{0}| >> scroll list update: {1}".format(_str_func, _short))  
                
                mc.progressBar(_progressBar, edit=True, status = ("{0} Processing Parent: {1}".format(_str_func,_short)), step=1)                    
                
                _l_report = [str(i)]
                
                _alias = ATTR.get(_short,'cgmAlias')
                if _alias:
                    _l_report.append("{0} ({1})".format(_alias,mObj.p_nameBase))
                    #_l_report.append('alias ({0})'.format(_alias))
                else:
                    _l_report.append(mObj.p_nameBase)
                    
                #if i == ATTR.get(self)
                if _mode == 0:
                    if self._mNode.space == i:
                        _l_report.append('((Space))')
                elif _mode == 1:
                    if self._mNode.orientTo == i:
                        _l_report.append('((Orient))')
                else:
                    if self._mNode.orientTo == i:
                        _l_report.append('((Orient))')
                    if self._mNode.follow == i:
                        _l_report.append('((Follow))')

                if mObj.isReferenced():
                    _l_report.append("Referenced")
                _str = " \ ".join(_l_report)
                log.debug("|{0}| >> str: {1}".format(_str_func, _str))  
                
                self.uiScrollList_parents.append(_str)

        except Exception,err:
            try:
                log.error("|{0}| >> err: {1}".format(_str_func, err))  
                cgmUI.doEndMayaProgressBar(_progressBar)
            except:
                raise Exception,err

        cgmUI.doEndMayaProgressBar(_progressBar)
        
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        self._d_uiCheckBoxes = {}
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUISubTemplate')
        _header_top = cgmUI.add_Header('cgmDynParentGroup',overrideUpper=True)        

        #>>>Objects Load Row ---------------------------------------------------------------------------------------
        _row_objLoad = mUI.MelHSingleStretchLayout(_MainForm,ut='cgmUITemplate',padding = 5)        
        
        mUI.MelSpacer(_row_objLoad,w=10)
        mUI.MelLabel(_row_objLoad, 
                     l='dynChild:')
        
        _utf_objLoad = mUI.MelLabel(_row_objLoad,ut='cgmUITemplate',l='',
                                    en=True)
        
        #self.uiPopUpMenu_dynChild = mUI.MelPopupMenu(_utf_objLoad,button = 1)
        #mc.menuItem(self.uiPopUpMenu_dynChild,l='Select',c=lambda *a:(self._mNode.select()))
           
        
        self._utf_obj = _utf_objLoad
        cgmUI.add_Button(_row_objLoad,'<<',
                         cgmGEN.Callback(self.uiFunc_load_selected),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Load selected object.")   
        
        
        _row_objLoad.setStretchWidget(_utf_objLoad)
        mUI.MelSpacer(_row_objLoad,w=10)
        
        _row_objLoad.layout()
        
        #>>>Report ---------------------------------------------------------------------------------------
        _row_report = mUI.MelHLayout(_MainForm ,ut='cgmUIInstructionsTemplate',h=20)
        self.uiField_report = mUI.MelLabel(_row_report,
                                           bgc = SHARED._d_gui_state_colors.get('help'),
                                           label = '...',
                                           h=20)
        _row_report.layout()        
        
        
        #>>>Mode Row ---------------------------------------------------------------------------------------
        _row_modeSelect = mUI.MelHSingleStretchLayout(_MainForm,ut='cgmUISubTemplate',padding = 5,en=True)
        
        mUI.MelLabel(_row_modeSelect,l="Mode:")
        _row_modeSelect.setStretchWidget(mUI.MelSeparator(_row_modeSelect))
        
        _uiRC_mode = mUI.MelRadioCollection()
        _v = self.var_dynParentMode.value
        
        _d_annos = {'space':'Will use objects loaded to the ui',
                    'follow':'Will use any selected objects primNode type',
                    'orientTo':'Will use any objects below primeNode heirarchally and matching type'}
        self._uiList_modeButtons = []
        for i,item in enumerate(ui.__modes):
            _button = _uiRC_mode.createButton(_row_modeSelect,
                                              label=item,
                                              ann=_d_annos.get(item,'Fill out the dict!'),
                                              cc = cgmGEN.Callback(self.var_dynParentMode.setValue,item))
            if item == _v:
                _button.select()
            self._uiList_modeButtons.append(_button)
                  
        
        self._uiRC_mode = _uiRC_mode
        _row_modeSelect.layout()
        
        #self._l_toEnable.append(_row_modeSelect)
        #if self.CreateAttrTypeOptionVar.value:
        
        #>>> Group Buttons Row ---------------------------------------------------------------------------------------
        _row_groupsButtons = mUI.MelHLayout(_MainForm,ut='cgmUISubTemplate',padding = 2,en=True)
    
        cgmUI.add_Button(_row_groupsButtons,'Rebuild',
                         cgmGEN.Callback(self.uiFunc_dynGroup_rebuild),                         
                         "Rebuild a dynParentGroup. If it doens't exist, create it.")        
    
        cgmUI.add_Button(_row_groupsButtons,'Clear',
                         cgmGEN.Callback(self.uiFunc_dynGroup_clear),                         
                         "Remove a dynParentGroup")
        
        cgmUI.add_Button(_row_groupsButtons,'Copy',
                         cgmGEN.Callback(self.uiFunc_dynGroup_copy),                         
                         "Copy the loaded dynParentGroup data to selected objects")
        
        _row_groupsButtons.layout()           
        
        
        #>>>Push Values header ---------------------------------------------------------------------------------------        
        mc.setParent(_MainForm)        
        _header_parents = cgmUI.add_Header('Parents')        
        
        #>>> Parents list ---------------------------------------------------------------------------------------
        self.uiScrollList_parents = mUI.MelObjectScrollList(_MainForm, allowMultiSelection=True,en=False,
                                                            dcc = self.uiFunc_dc_fromList,
                                                            selectCommand = self.uiFunc_selectParent_inList)
        
                                                            #dcc = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}),

        self._l_toEnable.append(self.uiScrollList_parents)

        
        #>>> Parent Buttons Row ---------------------------------------------------------------------------------------
        _row_parentsButtons = mUI.MelHLayout(_MainForm,ut='cgmUISubTemplate',padding = 2,en=False)
        self._l_toEnable.append(_row_parentsButtons)
            
        cgmUI.add_Button(_row_parentsButtons,'Add',
                         cgmGEN.Callback(self.uiFunc_dynGroup_addParents),                         
                         "Add selected objects as dynParent nodes")     
        cgmUI.add_Button(_row_parentsButtons,'Remove',
                         cgmGEN.Callback(self.uiFunc_dynGroup_removeParents),                        
                         "Refresh the attributes in the scroll list. Useful if keyed.")   
        cgmUI.add_Button(_row_parentsButtons,'Move Up',
                         cgmGEN.Callback(self.uiFunc_dynParents_reorder,0),                        
                         "Refresh the attributes in the scroll list. Useful if keyed.")         
        cgmUI.add_Button(_row_parentsButtons,'Move Dn',
                         cgmGEN.Callback(self.uiFunc_dynParents_reorder,1),                        
                         "Refresh the attributes in the scroll list. Useful if keyed.") 
        _row_parentsButtons.layout()   
    
        
        
        #>>>CGM Row
        # bgc = [.5972,0,0]
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)
        """_row_cgm = mUI.MelRow(_MainForm, bgc = [.25,.25,.25], h = 20)
        from cgm.core.cgmPy import path_Utils as CGMPATH
        from cgm import images as cgmImagesFolder
        _path_imageFolder = CGMPATH.Path(cgmImagesFolder.__file__).up()
        _path_image = os.path.join(_path_imageFolder,'cgm_uiFooter_gray.png')
        mc.iconTextButton(style='iconOnly',image1=_path_image,
                          c=lambda *a:(log.info('test')))"""
                    #c=lambda *args:(r9Setup.red9ContactInfo()),h=22,w=200)            
        #>>> Layout form ---------------------------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_header_top,"top",0),
                        (_header_top,"left",0),
                        (_header_top,"right",0),                        
                        (_row_objLoad,"left",0),
                        (_row_objLoad,"right",0),
                        (_row_report,"left",0),
                        (_row_report,"right",0),                        
                        (self.uiScrollList_parents,"left",0),
                        (self.uiScrollList_parents,"right",0),
                        (_row_parentsButtons,"left",0),
                        (_row_parentsButtons,"right",0),
                        (_row_groupsButtons,"left",0),
                        (_row_groupsButtons,"right",0),                        
                        (_header_parents,"left",0),
                        (_header_parents,"right",0),
                        (_row_modeSelect,"left",5),
                        (_row_modeSelect,"right",5),
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),

                        ],
                  ac = [(_row_objLoad,"top",2,_header_top),
                        (_row_report,"top",0,_row_objLoad),
                        (_row_modeSelect,"top",2,_row_report),
                        (_row_groupsButtons,"top",2,_row_modeSelect),                        
                        (_header_parents,"top",2,_row_groupsButtons),
                        (self.uiScrollList_parents,"top",0,_header_parents),
                        (self.uiScrollList_parents,"bottom",2,_row_parentsButtons),
                        (_row_parentsButtons,"bottom",2,_row_cgm),
                        
                       ],
                  attachNone = [(_row_cgm,"top")])	        
        
        _sel = mc.ls(sl=True)
        if _sel:
            self.uiFunc_load_selected()                

        return
 
    #@cgmGEN.Timer
    def uiFunc_selectParent_inList(self): 
        _str_func = 'uiFunc_selectParent_inList'        
        if self.uiPopUpMenu_parent:
            self.uiPopUpMenu_parent.clear()
            self.uiPopUpMenu_parent.delete()
            self.uiPopUpMenu_parent = None        
            
        ml_parents = self._mGroup.msgList_get('dynParents')
        _indices = self.uiScrollList_parents.getSelectedIdxs() or []
        log.debug("|{0}| >> indices: {1}".format(_str_func, _indices))    
        
        if not _indices:
            return
        
        self.uiPopUpMenu_parent = mUI.MelPopupMenu(self.uiScrollList_parents,button = 3)
        _popUp = self.uiPopUpMenu_parent           
                
        if len(_indices) == 1:
            _b_single = True
            
            log.debug("|{0}| >> Single pop up mode".format(_str_func))  
            _short = ml_parents[_indices[0]].p_nameShort
            mUI.MelMenuItem(_popUp,
                            label = "Single: {0}".format(_short),
                            en=False)            
        else:
            log.debug("|{0}| >> Multi pop up mode".format(_str_func))  
            mUI.MelMenuItem(_popUp,
                            label = "Mutli",
                            en=False)  
            _b_single = False
            
        
        if _b_single:
            mUI.MelMenuItem(_popUp,
                            label ='Alias',
                            ann = 'Enter value desired in prompt',
                            c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'alias'}))
            mUI.MelMenuItem(_popUp,
                            label ='Clear Alias',
                            ann = 'Remove any alias',
                            c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'aliasClear'}))

        mUI.MelMenuItem(_popUp,
                        label ='Select',
                        ann = 'Select specified indice parents',
                        c = cgmGEN.Callback(self.uiFunc_parentManage_fromScrollList,**{'mode':'select'}))  
        mUI.MelMenuItem(_popUp,
                        label ='Move Up',
                        ann = 'Move selected up in list',
                        c = cgmGEN.Callback(self.uiFunc_dynParents_reorder,0)) 
        mUI.MelMenuItem(_popUp,
                        label ='Move Down',
                        ann = 'Move selected down in list',
                        c = cgmGEN.Callback(self.uiFunc_dynParents_reorder,1)) 
        
        self._ml_objList = cgmMeta.validateObjListArg( CONTEXT.get_list(getTransform=True) )        
        uiMenu_changeSpace(self,_popUp)
        
        return
        
                
 
 
    def uiFunc_parentManage_fromScrollList(self,**kws):          
        
        _str_func = 'uiFunc_parentManage_fromScrollList'
        _indices = self.uiScrollList_parents.getSelectedIdxs()
                
        _mode = kws.get('mode',None)
        _fromPrompt = None
        
        if not self._mGroup:
            log.error("|{0}| >> No Group Loaded".format(_str_func))                                                        
            return False
        
        ml_parents = self._mGroup.msgList_get('dynParents')
            
        
        if not _indices:
            log.error("|{0}| >> Nothing selected".format(_str_func))                                                        
            return False
        
        _ml_targets = [ml_parents[i] for i in _indices]
        log.debug("|{0}| >> targets: {1}".format(_str_func,[mObj.mNode for mObj in _ml_targets]))                                                        
        
        
        _done = False

        if _mode is not None:
            log.debug("|{0}| >> mode: {1}".format(_str_func,_mode))  
            
            if _mode == 'alias':
                _fromPrompt = ATTRTOOLS.uiPrompt_getValue("Enter Alias","Type in your alias to be used in the marking menu")
                if _fromPrompt is None:
                    log.error("|{0}| >>  Mode: {1} | No value gathered...".format(_str_func,_mode)) 
                    return False
                else:
                    log.info("|{0}| >>  from prompt: {1} ".format(_str_func,_fromPrompt))  
                    _fromPrompt = STRINGS.strip_invalid(_fromPrompt,',[]{}()', functionSwap = False, noNumberStart = False)
                
                if _fromPrompt:
                    for mObj in _ml_targets:
                        if mObj.hasAttr('cgmAlias'):
                            ATTR.set(mObj.mNode,'cgmAlias',value= _fromPrompt)
                        else:
                            mObj.addAttr('cgmAlias',value = _fromPrompt)
                    #self._mGroup.rebuild()
                    self._mGroup.update_enums()
                    self.uiFunc_updateDynParentDisplay()
            elif _mode == 'aliasClear':
                for mObj in _ml_targets:
                    mObj.delAttr('cgmAlias')    
                #self._mGroup.rebuild()
                self._mGroup.update_enums()                
                self.uiFunc_updateDynParentDisplay()                
                    
            elif _mode == 'select':
                mc.select([mObj.mNode for mObj in _ml_targets])
                
            elif _mode == 'switchTo':
                _dynMode = self._mGroup.dynMode
                if _dynMode == 0:
                    self._mGroup.doSwitchSpace('space',_indices[0])
                elif _dynMode == 1:
                    self._mGroup.doSwitchSpace('orientTo',_indices[0])
                else:
                    self._mGroup.doSwitchSpace('orientTo',_indices[0])
                    
                    
            

            else:
                log.error("|{0}| >>  Mode: {1} | Not implented...".format(_str_func,_mode))                                               
                return False
            
        self.uiFunc_updateDynParentDisplay()
        return True

        
    def uiFunc_get_buildDict(self):
        _str_func = 'uiFunc_get_buildDict' 
        _d = {}

        _idx = self._uiRC_mode.getSelectedIndex()
        _d['dynMode'] = _idx
        
        cgmGEN.log_info_dict(_d,_str_func)
        return _d
        
            
    def uiFunc_dynGroup_rebuild(self):
        _str_func = 'uiFunc_dynGroup_rebuild' 
        
        if not self._mNode:
            log.error("|{0}| >> No dyChild loaded to ui".format(_str_func))                                            
            return False
        
        if self._mNode.isReferenced():
            log.error("|{0}| >> Does not work on referenced nodes".format(_str_func))                                            
            return False
        
        _d_exists = get_dict(self._mNode.mNode)
        _d_build = self.uiFunc_get_buildDict()
        _d_build['dynChild'] = self._mNode
        if _d_exists and _d_exists.get('dynMode') != _d_build.get('dynMode'):
            log.error("|{0}| >> Modes don't match".format(_str_func))                                            
            
        
        
        #Build...
        verify_obj(self._mNode, _d_build.get('dynMode'))
        
        
        self.uiFunc_updateDynParentDisplay()
        
        
    def uiFunc_dynGroup_clear(self):
        _str_func = 'uiFunc_dynGroup_clear' 
    
        if not self._mGroup:
            log.error("|{0}| >> No dynGroup loaded to ui".format(_str_func))                                            
            return False    
        
        if self._mGroup.isReferenced():
            log.error("|{0}| >> Does not work on referenced dynGroups".format(_str_func))                                            
            return False        
        
        self._mGroup.doPurge()
        
        self.uiFunc_updateDynParentDisplay()
        
    def uiFunc_dynGroup_copy(self):
        _str_func = 'uiFunc_dynGroup_copy' 
    
        if not self._mNode:
            log.error("|{0}| >> No dyChild loaded to ui".format(_str_func))                                            
            return False  
        if not self._mGroup:
            log.error("|{0}| >> No dynGroup loaded to ui".format(_str_func))                                            
            return False              
        if self._mGroup.isReferenced():
            log.error("|{0}| >> Does not work on referenced dynGroups".format(_str_func))                                            
            return False
        
        _l_context = CONTEXT.get_list('selection')
        _ml_copyTo = []
        for o in _l_context:
            mObj = cgmMeta.validateObjArg(o)
            if mObj == self._mNode:
                log.error("|{0}| >> Cannot copy to self".format(_str_func))                                            
            elif not VALID.is_transform(o):
                log.error("|{0}| >> Not a transform: {1}".format(_str_func,o))                                                            
            else:
                _ml_copyTo.append(mObj)
        
        if not _ml_copyTo:
            log.error("|{0}| >> No acceptable targets found".format(_str_func))                                            
            return False
        
        _d_build = {}
        for mObj in _ml_copyTo:
            if ATTR.get_message(mObj.mNode,'dynParentGroup'):
                mObj.dynParentGroup.doPurge()
                
            _d_build['dynChild'] = mObj.mNode
            _d_build['dynMode'] = self._mGroup.dynMode
            _d_build['dynParents'] = self._mGroup.msgList_get('dynParents')
            _mi_group = cgmRigMeta.cgmDynParentGroup(**_d_build)
            
    def uiFunc_dynGroup_addParents(self):
        _str_func = 'uiFunc_dynGroup_addParents' 
    
        if not self._mGroup:
            log.error("|{0}| >> No dynGroup loaded to ui".format(_str_func))                                            
            return False    
        
        if self._mGroup.isReferenced():
            log.error("|{0}| >> Does not work on referenced dynGroups".format(_str_func))                                            
            return False
        
        _l_context = CONTEXT.get_list('selection',getTransform=True)
        _ml_add = []
        for o in _l_context:
            mObj = cgmMeta.validateObjArg(o)
            if mObj == self._mNode:
                log.error("|{0}| >> Cannot add self as parent".format(_str_func))                                            
            elif not VALID.is_transform(o):
                log.error("|{0}| >> Not a transform: {1}".format(_str_func,o))                                                            
            else:
                _ml_add.append(mObj)  
                
        if not _ml_add:
            log.error("|{0}| >> No eligible targets selected".format(_str_func))                                                                        
            return False
        
        for mObj in _ml_add:
            self._mGroup.addDynParent(mObj)
            
        self._mGroup.rebuild()
        self.uiFunc_updateDynParentDisplay()
        
    def uiFunc_dc_fromList(self):
        _str_func = 'uiFunc_dc_fromList'   
    
        if not self._mGroup:
            log.error("|{0}| >> No dynGroup loaded to ui".format(_str_func))                                            
            return False          
    
        ml_parents = self._mGroup.msgList_get('dynParents')
        _indices = self.uiScrollList_parents.getSelectedIdxs() or []
    
        if _indices:
            ml_parents[_indices[0]].select()
                        
    def uiFunc_dynGroup_removeParents(self):
        _str_func = 'uiFunc_dynGroup_removeParents'   
        
        if not self._mGroup:
            log.error("|{0}| >> No dynGroup loaded to ui".format(_str_func))                                            
            return False          
        
        if self._mGroup.isReferenced():
            log.error("|{0}| >> Does not work on referenced dynGroups".format(_str_func))                                            
            return False        

        _l_context = CONTEXT.get_list('selection')
        _ml_remove = []
        ml_parents = self._mGroup.msgList_get('dynParents')
        
        for o in _l_context:
            mObj = cgmMeta.validateObjArg(o)
            if mObj == self._mNode:
                log.error("|{0}| >> Cannot remove self as parent".format(_str_func))                                            
            elif not VALID.is_transform(o):
                log.error("|{0}| >> Not a transform: {1}".format(_str_func,o))                                                            
            else:
                _ml_remove.append(mObj)  
                
        _indices = self.uiScrollList_parents.getSelectedIdxs() or []
        if _indices:
            for i in _indices:
                if ml_parents[i] not in _ml_remove:
                    _ml_remove.append(ml_parents[i])
    
        if not _ml_remove:
            log.error("|{0}| >> No eligible targets selected".format(_str_func))                                                                        
            return False  
        
        log.error("|{0}| >> To remove: {1}".format(_str_func,_ml_remove))                                            
        self._mGroup.clearParents()
        
        for mObj in _ml_remove:
            _short = mObj.mNode
            log.info(mObj.mNode)
            for i,mP in enumerate(ml_parents):
                if mP.mNode == _short:
                    ml_parents.pop(i)
                
        for mObj in ml_parents:
            self._mGroup.addDynParent(mObj)
        
        self._mGroup.rebuild()        
            
        self.uiFunc_updateDynParentDisplay()
        
    def uiFunc_dynParents_reorder(self,direction = 0):
        """
        direction(int) - 0 is is negative (up), 1 is positive (dn)

        """
        _str_func = 'uiFunc_dynGroup_removeParents'   
        
        if not self._mGroup:
            log.error("|{0}| >> No dynGroup loaded to ui".format(_str_func))                                            
            return False          
        if self._mGroup.isReferenced():
            log.error("|{0}| >> Does not work on referenced dynGroups".format(_str_func))                                            
            return False        
        _l_context = CONTEXT.get_list('selection')
        _ml_remove = []
        ml_parents = self._mGroup.msgList_get('dynParents')
        _l_parents = [mObj.mNode for mObj in ml_parents]
      
        _indices = self.uiScrollList_parents.getSelectedIdxs() or []
        
        if not _indices:
            log.error("|{0}| >> No targets specified in parent list".format(_str_func))                                            
            return False  
        
        _to_move = []
        for i in _indices:
            _to_move.append(_l_parents[i])
            
        _initialValue = _l_parents[_indices[0]]
        
        _to_move = lists.reorderListInPlace(_l_parents,_to_move,direction)
        
        self._mGroup.clearParents()
        
        for o in _l_parents:
            self._mGroup.addDynParent(o)
        
        self._mGroup.rebuild()
        self.uiFunc_updateDynParentDisplay()
        
        
        self.uiScrollList_parents.selectByIdx(_l_parents.index(_initialValue))
        return True
            
                    
    def uiFunc_spacePivot_add(self,count=1):
        _str_func = 'uiFunc_spacePivot_clear' 
    
        if not self._mGroup:
            log.error("|{0}| >> No dynGroup loaded to ui".format(_str_func))                                            
            return False  
        if self._mGroup.isReferenced():
            log.error("|{0}| >> Does not work on referenced dynGroups".format(_str_func))                                            
            return False        
        
        ml_pivots = SPACEPIVOT.add(self._mNode.mNode, False, count=1)
        

        for mPivot in ml_pivots:
            self._mGroup.addDynParent(mPivot.mNode)
        
        self._mGroup.rebuild()
        self.uiFunc_updateDynParentDisplay()   
        
        return 
    def uiFunc_spacePivot_addFromPrompt(self):
        _str_func = 'uiFunc_spacePivot_addFromPrompt'
        
        if not self._mGroup:
            log.error("|{0}| >> No dynGroup loaded to ui".format(_str_func))                                            
            return False  
        if self._mGroup.isReferenced():
            log.error("|{0}| >> Does not work on referenced dynGroups".format(_str_func))                                            
            return False            
        
        _fromPrompt = ATTRTOOLS.uiPrompt_getValue("Enter Number","How many space pivots do you want?")
        if _fromPrompt is None:
            log.error("|{0}| >>  Count: {1} | No value gathered...".format(_str_func,_mode)) 
            return False       
        
        try:_fromPrompt = int(_fromPrompt)
        except:pass
        
        _v = VALID.valueArg(_fromPrompt,noneValid=True)
        if not _v:
            log.error("|{0}| >>  Invalid: {1} | No value gathered...".format(_str_func,_fromPrompt)) 
            return False
        log.info("|{0}| >>  Count: {1}...".format(_str_func,_v)) 
        
        ml_pivots = SPACEPIVOT.add(self._mNode.mNode, False, count=_v)
        
        for mPivot in ml_pivots:
            self._mGroup.addDynParent(mPivot.mNode)
        
        self._mGroup.rebuild()
        self.uiFunc_updateDynParentDisplay()          
        
    def uiFunc_spacePivot_clear(self):
        _str_func = 'uiFunc_spacePivot_clear' 
    
        if not self._mNode:
            log.error("|{0}| >> No dynChild loaded to ui".format(_str_func))                                            
            return False    
        if self._mNode.isReferenced():
            log.error("|{0}| >> Does not work on referenced nodes".format(_str_func))                                            
            return False 
        
        if SPACEPIVOT.clear(self._mNode.mNode):
            self._mGroup.rebuild()
        self.uiFunc_updateDynParentDisplay()   
        
        return         
        
    def reorder(self, direction = 0):
        """   
        :Acknowledgement:
        Thank you to - http://www.the-area.com/forum/autodesk-maya/mel/how-can-we-reorder-an-attribute-in-the-channel-box/
    
        Reorders attributes on an object
    
        :parameters:
            node(str) -- 
            attrs(list) must be attributes on the object
            direction(int) - 0 is is negative (up on the channelbox), 1 is positive (up on the channelbox)
    
        :returns
            status(bool)
        """
        _str_func = 'reorder'    
        
        attrs = VALID.listArg(attrs)
        
        for a in attrs:
            assert mc.objExists(node+'.'+a) is True, "|{0}|>> . '{1}.{2}' doesn't exist. Swing and a miss...".format(_str_func,node,a)
            
        _l_user = mc.listAttr(node,userDefined = True)
        _to_move = []
        
        for a in _l_user:
            if not is_hidden(node,a):
                _to_move.append(a)
    
        log.info(_to_move)
        _to_move = lists.reorderListInPlace(_to_move,attrs,direction)
        log.info(_to_move)
        
        #To reorder, we need delete and undo in the order we want
        _d_locks = {}
        _l_relock = []    
        
            
        

def verify_obj(obj = None, mode = 0):
    """
    Given an object selection. Verify selection of first object with a dynParent group and add the subsequent 
    nodes if any as parents.
    
    :parameters
        self(instance): cgmMarkingMenu

    :returns
        info(dict)
    """   
    _str_func = "verify_obj"
    _buildD = {}
    
    if not obj:
        _l_context = CONTEXT.get_list('selection')
        
        _len_context = len(_l_context)
        if not _l_context:
            log.error("|{0}| >> Nothing selected.".format(_str_func))                                               
            return False
        
        _buildD['dynChild'] = _l_context[0]
        
        if _len_context > 1:
            _buildD['dynParents'] = _l_context[1:]
    else:
        _buildD['dynChild'] = obj
    
    #>>>Logging what we're gonna do.
    log.info("|{0}| >> Building....".format(_str_func))                                               
    log.info("|{0}| >> dynChild: {1}".format(_str_func,_buildD['dynChild'])) 

    #Initialize group
    _mi_group = cgmRigMeta.cgmDynParentGroup(dynChild = _buildD['dynChild'], dynMode=mode)
    
    #Add parents
    if _buildD.get('dynParents'):    
        log.info("|{0}| >> dynParents...".format(_str_func))         
        for i,p in enumerate(_buildD['dynParents']):
            log.info("|{0}| >> {1} | {2}".format(_str_func,i,p))   
            _mi_group.addDynParent(p)
    
    _mi_group.rebuild()    
    
    #mc.select(_l_context)
    return True    


def get_dict(obj = None):
    """
    Given an object selection. Get a data dict of the dynParentGroup on that object
    
    :parameters
        obj(string): Node or selection based

    :returns
        info(dict)
    """   
    _str_func = "get_dict"
    if not obj:
        _l_context = CONTEXT.get_list('selection')
        if not _l_context:
            log.error("|{0}| >> Nothing selected.".format(_str_func))                                                           
            return False
        obj = _l_context[0]
        
    _d = {}
    
    mGroup = False
    mObj = False
    if ATTR.get_message(obj,'dynParentGroup'):
        log.info("|{0}| >> dynParentGroup found...".format(_str_func))  
        mObj = cgmMeta.validateObjArg(obj)
        mGroup = mObj.dynParentGroup
    elif ATTR.get(obj,'mClass') == 'cgmDynParentGroup':
        log.info("|{0}| >> is dynParentGroup...".format(_str_func))   
        mGroup = cgmMeta.validateObjArg(obj)
        mObj = cgmMeta.validateObjArg(mGroup.dynChild)
    else:
        log.info("|{0}| >> No data found for: {1}".format(_str_func,obj))   
        return False
    
    log.info(cgmGEN._str_hardLine)
    #log.info("|{0}| >> dynChild: {1}".format(_str_func,mObj.mNode))
    #log.info("|{0}| >> dynGroup: {1}".format(_str_func,mGroup.mNode))
    _d['mode'] = mGroup.dynMode
    _d['dynParents'] = mGroup.msgList_get('dynParents')
    _d['dynDrivers'] = mGroup.msgList_get('dynDrivers')
    _d['dynChild'] = mObj
    _d['dynGroup'] = mGroup
    
    _d['aliases'] = []
    for p in _d['dynParents']:
        _d['aliases'].append(ATTR.get(p,'cgmAlias'))
    
    #cgmGEN.log_info_dict(_d,'Data:')
    return _d

def get_state(obj = None):
    """
    Given an object selection. Get a data dict of the dynParentGroup on that object
    
    :parameters
        obj(string): Node or selection based

    :returns
        info(dict)
d_DynParentGroupModeAttrs = {0:['space'],
                             1:['orientTo'],
                             2:['orientTo','follow']}        
        
        
        
    """   
    _str_func = "get_state"
    
    _d = get_dict(obj)
    
    if not _d:
        return False 
    
    _mGroup = _d['dynGroup']
    _mode = _d['mode']
    _dynChild = _d['dynChild']
    
    if _mode == 0:
        return _dynChild.space
    elif _mode == 1:
        return _dynChild.orientTo
    else:
        return _dynChild.orientTo, _dynChild.follow
    
    
def uiMenu_changeSpace(self, parent, showNoSel = False):
    _str_func = 'uiMenu_changeSpace'
    #uiMatch = mc.menuItem(p=parent, l='Match Mode ', subMenu=True)
    
    __int_maxObjects = 10
    timeStart_objectList = time.clock()    
    
    try:_ml_objList = self._ml_objList
    except:
        log.debug("|{0}| >> Generating new _ml_objList".format(_str_func))   
        _ml_objList = cgmMeta.validateObjListArg( CONTEXT.get_list(getTransform=True) )
    try:self.d_objectsInfo
    except:
        self.d_objectsInfo = {}
        
    if not _ml_objList:
        if showNoSel:mUI.MelMenuItem( parent, l="Nothing Selected")    
        return
    
    #>>  Individual objects....  ============================================================================
    if _ml_objList:
        self._d_mObjInfo = {}
        #first we validate
        #First we're gonna gather all of the data
        #------------------------------------------------------
        for i,mObj in enumerate(_ml_objList):
            _short = mObj.mNode
            if i >= __int_maxObjects:
                log.warning("|{0}| >> More than {0} objects select, only loading first  for speed".format(_str_func, __int_maxObjects))                                
                break
            d_buffer = {}
            
            #>>> Space switching ------------------------------------------------------------------	
            _dynParentGroup = ATTR.get_message(mObj.mNode,'dynParentGroup')
            if _dynParentGroup:
                i_dynParent = cgmMeta.validateObjArg(_dynParentGroup[0],'cgmDynParentGroup',True)
                d_buffer['dynParent'] = {'mi_dynParent':i_dynParent,'attrs':[],'attrOptions':{}}#Build our data gatherer					    
                if i_dynParent:
                    for a in cgmRigMeta.d_DynParentGroupModeAttrs[i_dynParent.dynMode]:
                        if mObj.hasAttr(a):
                            d_buffer['dynParent']['attrs'].append(a)
                            lBuffer_attrOptions = []
                            #for i,o in enumerate(cgmMeta.cgmAttr(mObj.mNode,a).p_enum):
                            for i,o in enumerate(ATTR.get_enumList(_short,a)):
                                lBuffer_attrOptions.append(o)
                            d_buffer['dynParent']['attrOptions'][a] = lBuffer_attrOptions
            self._d_mObjInfo[mObj] = d_buffer


        #=========================================================================================
        #>> Find Common options ------------------------------------------------------------------
        timeStart_commonOptions = time.clock()    
        l_commonAttrs = []
        d_commonOptions = {}
        bool_firstFound = False
        for mObj in self._d_mObjInfo.keys():
            if 'dynParent' in self._d_mObjInfo[mObj].keys():
                attrs = self._d_mObjInfo[mObj]['dynParent'].get('attrs') or []
                attrOptions = self._d_mObjInfo[mObj]['dynParent'].get('attrOptions') or {}
                if self._d_mObjInfo[mObj].get('dynParent'):
                    if not l_commonAttrs and not bool_firstFound:
                        log.debug('first found')
                        l_commonAttrs = attrs
                        state_firstFound = True
                        d_commonOptions = attrOptions
                    elif attrs:
                        log.debug(attrs)
                        for a in attrs:
                            if a in l_commonAttrs:
                                for option in d_commonOptions[a]:			
                                    if option not in attrOptions[a]:
                                        d_commonOptions[a].remove(option)

        log.debug("|{0}| >> Common Attrs: {1}".format(_str_func, l_commonAttrs))                
        log.debug("|{0}| >> Common Options: {1}".format(_str_func, d_commonOptions))    
        log.debug("|{0}| >> Common options build time: {1}".format(_str_func,  '%0.3f seconds  ' % (time.clock()-timeStart_commonOptions)))    
        

        #>> Build ------------------------------------------------------------------
        int_lenObjects = len(self._d_mObjInfo.keys())
        _b_acted = False
        
        # Mutli
        if int_lenObjects == 1:
            #MelMenuItem(parent,l="-- Object --",en = False)	    					
            use_parent = parent
            state_multiObject = False
        elif l_commonAttrs:
            #MelMenuItem(parent,l="-- Objects --",en = False)	    			
            #iSubM_objects = mUI.MelMenuItem(parent,l="Objects(%s)"%(int_lenObjects),subMenu = True)
            iSubM_objects = mc.menuItem(p=parent,l="Objects(%s)"%(int_lenObjects),subMenu = True)
            
            use_parent = iSubM_objects
            state_multiObject = True		
            if l_commonAttrs and [d_commonOptions.get(a) for a in l_commonAttrs]:
                for atr in d_commonOptions.keys():
                    #tmpMenu = mUI.MelMenuItem( parent, l="multi Change %s"%atr, subMenu=True)
                    tmpMenu = mc.menuItem( p=parent, l="multi Change %s"%atr, subMenu=True)                    
                    for i,o in enumerate(d_commonOptions.get(atr)):
                        mc.menuItem(p=tmpMenu,l = "%s"%o,
                                    c = cgmGEN.Callback(func_multiChangeDynParent,self._d_mObjInfo,atr,o))
                
        # Individual ----------------------------------------------------------------------------
        #log.debug("%s"%[k.getShortName() for k in self._d_mObjInfo.keys()])
        for mObj in self._d_mObjInfo.keys():
            _short = mObj.p_nameShort
            d_buffer = self._d_mObjInfo.get(mObj) or False
            if d_buffer:
                if state_multiObject:
                    #iTmpObjectSub = mUI.MelMenuItem(use_parent,l=" %s  "%mObj.getBaseName(),subMenu = True)
                    iTmpObjectSub = mc.menuItem(p=use_parent,l=" %s  "%mObj.getBaseName(),subMenu = True)                    
                else:
                    mc.menuItem(p=parent,l="-- %s --"%_short,en = False)
                    iTmpObjectSub = use_parent
                if d_buffer.get('dynParent'):
                    _b_acted = True
                    mi_dynParent = d_buffer['dynParent'].get('mi_dynParent')
                    d_attrOptions = d_buffer['dynParent'].get('attrOptions') or {}			
                    for a in d_attrOptions.keys():
                        if mObj.hasAttr(a):
                            lBuffer_attrOptions = []
                            tmpMenu = mc.menuItem( p=iTmpObjectSub, l="Change %s"%a, subMenu=True)
                            v = ATTR.get("%s.%s"%(_short,a))
                            for i,o in enumerate(ATTR.get_enumList(_short,a)):#enumerate(cgmMeta.cgmAttr(mObj.mNode,a).p_enum)
                                if i == v:b_enable = False
                                else:b_enable = True
                                mc.menuItem(p=tmpMenu,l = "%s"%o,en = b_enable,
                                            c = cgmUI.Callback(mi_dynParent.doSwitchSpace,a,i))
                else:
                    log.debug("|{0}| >> lacks dynParent: {1}".format(_str_func, _short))                
                    
        if not _b_acted:
            if showNoSel:mUI.MelMenuItem( parent, l="Invalid Selection")    
    log.debug("|{0}| >> Object list build: {1}".format(_str_func,  '%0.3f seconds  ' % (time.clock()-timeStart_objectList)))    

def func_multiChangeDynParent(_d_mObjInfo,attr,option):
    """
    execute a command and let the menu know not do do the default button action but just kill the ui
    """	
    cgmGEN.log_info_dict(_d_mObjInfo,"Data...")
    l_objects = [i_o.getShortName() for i_o in _d_mObjInfo.keys()]
    log.info("func_multiChangeDynParent>> attr: '%s' | option: '%s' | objects: %s"%(attr,option,l_objects))
    timeStart_tmp = time.clock()
    for i_o in _d_mObjInfo.keys():
        try:
            mi_dynParent = _d_mObjInfo[i_o]['dynParent'].get('mi_dynParent')
            mi_dynParent.doSwitchSpace(attr,option)
        except Exception,error:
            log.error("func_multiChangeDynParent>> '%s' failed. | %s"%(i_o.getShortName(),error))    

    log.info(">"*10  + ' func_multiChangeDynParent =  %0.3f seconds  ' % (time.clock()-timeStart_tmp) + '<'*10)  
    mc.select(l_objects)
    
    
    
