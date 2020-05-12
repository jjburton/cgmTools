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
#reload(POS)
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
import cgm.core.lib.math_utils as MATH
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
        
def buildColumn_main(self,parent,asScroll=False):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """
    self._d_transformAttrFields = {}
    self._d_transformRows = {}
    self._d_transformCBs = {}
    self._mTransformTarget = False
    
    if asScroll:
        _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUISubTemplate') 
    else:
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
    mc.text('VALUES',align = 'center',bgc = cgmUI.guiBackgroundColor)
    #cgmUI.add_Header('Values')
    cgmUI.add_SectionBreak()
    
    buildRow_vector(self,_inside,'translate')
    buildRow_vector(self,_inside,'position')
    buildRow_vector(self,_inside,'rotate')
    buildRow_vector(self,_inside,'orient')        
    buildRow_vector(self,_inside,'rotateAxis')
    buildRow_vector(self,_inside,'jointOrient')    
    buildRow_vector(self,_inside,'scale')
    buildRow_vector(self,_inside,'scaleLossy',tweak=False)
    buildRow_vector(self,_inside,'scalePivot',tweak=False)
    
    uiFunc_load_selected(self)
    return _inside

def buildRow_vector(self,parent,label='translate',tweak=True):
    #>>>Vector -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row ,w=5)                                              
    mUI.MelLabel(_row ,l=label + ':')        
    _row.setStretchWidget(mUI.MelSeparator(_row )) 
    _base_str = 'uiff_{0}'.format(label)
    
    self._d_transformAttrFields[label] = {}
    self._d_transformRows[label] = _row
    
    self._d_transformCBs[label] = mUI.MelCheckBox(_row,en=tweak,
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
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row ,w=5)                                              
    mUI.MelLabel(_row ,l='Tweak Values:')        
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
              ann = "Zero out the fields. Uncheck all tweak check boxes") 
    
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

    _sel = mc.ls(sl=True,type='transform')

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
        return False
    _short = self._mTransformTarget.mNode
    
    #_space = self.var_sourceTransSpaceMode.value
    #log.info("|{0}| >> Getting data. Space: {1} ".format(_str_func, _space))
    
    #_pos = POS.get(_short,'rp',_space)
    _info = POS.get_info(_short)
    
    #pprint.pprint(_info)
    #pprint.pprint(self._d_transformAttrFields)
    _d_sectionToDatKey = {'rotate':'rotateLocal',
                          'orient':'rotation'}
    
    for section in self._d_transformAttrFields.keys():
        log.info("|{0}| >> On {1}".format(_str_func,section))
        _s = section
        if _s in ['translate','rotate','position','rotateAxis','scalePivot','orient']:
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
    elif not _b_lockSource and self._mTransformTarget:
        if self._mTransformTarget not in _ml_targets:
            _ml_targets.insert(0,self._mTransformTarget)
    
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
        
    _d_fieldValues = {}
    
    #>>>Simple values
    _s = section    
    if not key:
        for a in 'XYZ':
            _v = self._d_transformAttrFields[_s][a].getValue()
            _d_fieldValues[a]  = _v
    else:
        try:
            _v = self._d_transformAttrFields[_s][key].getValue()
            _d_fieldValues[key] = _v
        
        except Exception,err:
            log.error("|{0}| >> Failed to get key data. Section: {0} | key: {1}...".format(_str_func,_s,key))                
            log.error(err)   
        
    #log.warning("|{0}| >> Haven't setup for {1}...".format(_str_func,_s))   
        
    #if _s in ['translate','rotate','scale','jointOrient','rotateAxis']:
    #pprint.pprint(_d_fieldValues)
    
    if _s in ['translate','rotate','scale','jointOrient','rotateAxis']:
        for a,v in _d_fieldValues.iteritems():
            _a = _s + a
            log.info("|{0}| >> Trying attr: {1} | v: {2}... ".format(_str_func,_a,v))                        
            for mObj in _ml_targets:
                if not ATTR.has_attr(mObj.mNode,_s):
                    log.info("|{0}| >> Object lacks {2} attr : {1}... ".format(_str_func,mObj.mNode,_s))                                                        
                    return
                log.info("|{0}| >> Trying Object: {1}... ".format(_str_func,mObj.mNode))                                    
                try:ATTR.set(mObj.mNode,_a,v)        
                except Exception,err:
                    log.error("|{0}| >> Failed to get set data. Object: {0} | a: {1} | v: {2}...".format(_str_func,mObj.mNode,_a,v))                
                    log.error(err)
    elif _s == 'position':
        for mObj in _ml_targets:
            log.info("|{0}| >> Trying Object: {1} | [{2}]... ".format(_str_func,mObj.mNode,_s)) 
            pos = TRANS.position_get(mObj.mNode)
            log.info("|{0}| >> pre pos: [{1}] ".format(_str_func,pos)) 
            
            for k,v in _d_fieldValues.iteritems():
                pos['XYZ'.index(k)] = v
            log.info("|{0}| >> pos pos: [{1}] ".format(_str_func,pos))   
            try:
                TRANS.position_set(mObj.mNode, pos)     
            except Exception,err:
                log.error("|{0}| >> Failed to get set data. Object: {0} | section: {2}...".format(_str_func,mObj.mNode,_s))                
                log.error(err) 
    elif _s == 'orient':
        for mObj in _ml_targets:
            log.info("|{0}| >> Trying Object: {1} | [{2}]... ".format(_str_func,mObj.mNode,_s)) 
            val = TRANS.orient_get(mObj.mNode)
            log.info("|{0}| >> pre val: [{1}] ".format(_str_func,val)) 
        
            for k,v in _d_fieldValues.iteritems():
                val['XYZ'.index(k)] = v
            log.info("|{0}| >> post val: [{1}] ".format(_str_func,val))   
            try:
                TRANS.orient_set(mObj.mNode, val)     
            except Exception,err:
                log.error("|{0}| >> Failed to get set data. Object: {0} | section: {2}...".format(_str_func,mObj.mNode,_s))                
                log.error(err)         
    elif _s == 'scaleLossy':
        log.warning("|{0}| >> NOTE - Scale lossy is pushed to local scale on targets ".format(_str_func,mObj.mNode,_s))                     
        for mObj in _ml_targets:
            log.info("|{0}| >> Trying Object: {1} | [{2}]... ".format(_str_func,mObj.mNode,_s))
            scale = TRANS.scaleLossy_get(mObj.mNode)
            log.info("|{0}| >> pre scale: [{1}] ".format(_str_func,scale)) 
        
            for k,v in _d_fieldValues.iteritems():
                scale['XYZ'.index(k)] = v
            log.info("|{0}| >> post scale: [{1}] ".format(_str_func,scale))   
            try:
                TRANS.scaleLocal_set(mObj.mNode, scale)     
            except Exception,err:
                log.error("|{0}| >> Failed to get set data. Object: {0} | section: {1} ...".format(_str_func,mObj.mNode,_s))                
                log.error(err)
    elif _s == 'scalePivot':
        for mObj in _ml_targets:
            log.info("|{0}| >> Trying Object: {1} | [{2}]... ".format(_str_func,mObj.mNode,_s))
            piv = TRANS.scalePivot_get(mObj.mNode)
            #pos = TRANS.position_get(mObj.mNode)
            log.info("|{0}| >> pre piv: [{1}] ".format(_str_func,piv)) 
        
            for k,v in _d_fieldValues.iteritems():
                piv['XYZ'.index(k)] = v
                
            #piv = MATH.list_subtract(piv,pos)
            log.info("|{0}| >> post piv: [{1}] ".format(_str_func,piv))   
            try:
                TRANS.scalePivot_set(mObj.mNode, piv)     
            except Exception,err:
                log.error("|{0}| >> Failed to get set data. Object: {0} | section: {1} ...".format(_str_func,mObj.mNode,_s))                
                log.error(err)        
    else:
        log.warning("|{0}| >> Haven't setup for {1}...".format(_str_func,_s))   
    
    

def uiFunc_valuesTweak(self,mode = '+'):
    _str_func = 'uiFunc_valuesTweak'
    
    if mode == 'zero':
        log.info("|{0}| >> Zeroing ".format(_str_func))           
        for a in 'XYZ':
            self.__dict__['uiff_transformTweak{0}'.format(a)].setValue(0)
        for k,cb in self._d_transformCBs.iteritems():
            cb.setValue(0)
        return 
    
    _ml_targets = uiFunc_getTargets(self)
    if not _ml_targets:
        raise ValueError,"Must have targets"    

    _l_toTweak = []
    for k,cb in self._d_transformCBs.iteritems():
        if cb.getValue():
            _l_toTweak.append(k)
            
    _tweak = []
    for a in 'XYZ':
        _tweak.append(self.__dict__['uiff_transformTweak{0}'.format(a)].getValue())
    
    #pprint.pprint([mode,_l_toTweak,_tweak])
    
    if mode == '+':
        _tweak_call = MATH.list_add
    else:
        _tweak_call = MATH.list_subtract
    
    for mObj in _ml_targets:
        for attr in _l_toTweak:
            if attr in ['translate','rotate','scale','jointOrient','rotateAxis']:
                _v = ATTR.get(mObj.mNode, attr)
                log.info("|{0}| >> pre tweak: [{1}] ".format(_str_func,_v)) 
                _v = _tweak_call(_v,_tweak)
                log.info("|{0}| >> post tweak: [{1}] ".format(_str_func,_v))                                 
                ATTR.set(mObj.mNode, attr,_v)
               
            elif attr == 'position':
                _v = TRANS.position_get(mObj.mNode)
                log.info("|{0}| >> pre tweak: [{1}] ".format(_str_func,_v)) 
                _v = _tweak_call(_v,_tweak)
                log.info("|{0}| >> post tweak: [{1}] ".format(_str_func,_v))                 
                TRANS.position_set(mObj.mNode, _v)  
            elif attr == 'orient':
                _v = TRANS.orient_get(mObj.mNode)
                log.info("|{0}| >> pre tweak: [{1}] ".format(_str_func,_v)) 
                _v = _tweak_call(_v,_tweak)
                log.info("|{0}| >> post tweak: [{1}] ".format(_str_func,_v))                                 
                TRANS.orient_set(mObj.mNode, _v)                  
            else:
                log.warning("|{0}| >> Haven't setup for {1}...".format(_str_func,_s))           
        
        
    
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
    if self.uiPopUpMenu_dynChild:
        self.uiPopUpMenu_dynChild.clear()
        self.uiPopUpMenu_dynChild.delete()
        self.uiPopUpMenu_dynChild = None

 