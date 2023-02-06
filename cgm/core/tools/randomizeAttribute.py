"""
------------------------------------------
randomizeAttribute: cgm.core.tools
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------
================================================================
"""


# From Python =============================================================
import pprint
import logging
import random

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import locator_utils as LOC
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
#import cgm.core.lib.shared_data as CORESHARE
#import cgm.core.lib.string_utils as CORESTRINGS
from cgm.core.lib import search_utils as SEARCH
import cgm.core.classes.GuiFactory as cgmUI
from cgm.core.lib import math_utils as MATH

#import cgm.core.mrs.lib.animate_utils as MRSANIMUTILS
import cgm.core.lib.list_utils as CORELIST

__version__ = cgmGEN.__RELEASESTRING


import cgm.core.classes.GuiFactory as CGMUI
mUI = CGMUI.mUI

from . import funcIterTime as FIT

log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start

_d_annotations = {'Set post blend':'Set the post blend time duration',
                  'Set pre blend':'Set the pre  blend time duration',
                  }
_l_toolModes  = ['absolute',
                 'nudge']
_l_blendModes = ['none','pre','peak','post']

_d_shorts = {'absolute':'abs',
             'relative':'rel'}
d_attrNames = {'tx':'translateX',
               'ty':'translateY',
               'tz':'translateZ',
               'rx':'rotateX',
               'ry':'rotateY',
               'rz':'rotateZ',
               'sx':'scaleX',
               'sy':'scaleY',
               'sz':'scaleZ',               
               }



class ui(FIT.ui):
    USE_Template = 'cgmUITemplate'
    _toolname = 'RandomizeAttribute'
    TOOLNAME = 'ui_RandomizeAttribute'
    WINDOW_NAME = "{}UI".format(TOOLNAME)
    WINDOW_TITLE = 'RandomizeAttribute| {0}'.format(__version__)
    DEFAULT_SIZE = 400, 350
    #DEFAULT_MENU = None
    RETAIN = True
    #MIN_BUTTON = False
    #MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = False  #always resets the size of the window when its re-created

 
    def insert_init(self, *args, **kws):
        FIT.ui.insert_init(self,*args,**kws)
        #super(FOT.ui, self).insert_init(*args, **kws)
        self.create_guiOptionVar('random_mode', defaultValue='absolute')
        self.create_guiOptionVar('blend_mode', defaultValue='peak')
        self.create_guiOptionVar('preOffset', defaultValue=-3.0)
        self.create_guiOptionVar('postOffset', defaultValue=3.0)
        
        self.l_attrs = []
        self.ml_targets = []
        self.d_activeAttrs = []
        
        #self.create_guiOptionVar('keysMode', defaultValue='loc')
        #self.create_guiOptionVar('interval', defaultValue=1.0)
        #self.create_guiOptionVar('showBake', defaultValue=0)
        #self.create_guiOptionVar('context_keys', defaultValue='each')
        #self.create_guiOptionVar('context_time', defaultValue='current')

    def post_init(self,*args,**kws):
        self.mFIT.set_func(self.uiFunc_call,[],{})
        self.mFIT.set_pre(self.uiFunc_pre,[],{})
        self.mFIT.set_post(self.uiFunc_post,[],{})
        
        self.uiFunc_attrs_add()
        pass#...clearing parent call here
    
    def log_dat(self):
        _str_func = 'log_self[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        pprint.pprint(self.mFIT.__dict__)        
                
    def uiFunc_attrs_add(self):
        _str_func = 'uiFunc_attrs_add[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        l_attrs = SEARCH.get_selectedFromChannelBox(attributesOnly = 1)
        if not l_attrs:
            return mc.warning( cgmGEN.logString_msg(_str_func,"No attributes Selected"))
        
        for a in l_attrs:
            if a not in self.l_attrs:
                self.l_attrs.append(a)
                
        self.uiFunc_refreshAttrList()
        
    def uiFunc_post(self,*args,**kws):
        _str_func = 'uiFunc_post[{0}]'.format(self.__class__.TOOLNAME)
        
        for mObj in self.ml_targets:
            mc.dgdirty(mObj.mNode)#...mark it dirty to update in viewport without a time change

    def uiFunc_pre(self,*args,**kws):
        _str_func = 'uiFunc_pre[{0}]'.format(self.__class__.TOOLNAME)                    
        #print('{} | do something here...'.format(mc.currentTime(q=True)))
        ml = cgmMeta.validateObjListArg(mc.ls(sl=1),default_mType='cgmObject')
        pprint.pprint(ml)
        
        if not ml:
            mc.warning( log_msg(_str_func,"Nothing selected"))
            return False
        
        self.ml_targets = ml
        self.d_activeAttrs = {}
        
        for i,a in enumerate(self.l_attrs):
            if self._dCB_attrs[i].getValue():
                self.d_activeAttrs[a] = {'min':self._dMin_attrs[i].getValue(),
                                         'max':self._dMax_attrs[i].getValue()}

        if not self.d_activeAttrs:
            return mc.warning( cgmGEN.logString_msg(_str_func,"No active Attrs"))        
        pprint.pprint([self.ml_targets,self.d_activeAttrs, self.var_random_mode.getValue()])
        
        
        _mode = self.var_random_mode.getValue()
        #...add validation to some arg values
        
        return True
    
    def uiFunc_call(self,*args,**kws):
        #print('{} | do something here...'.format(mc.currentTime(q=True)))
        _targets =  self.ml_targets
        _attrs = self.d_activeAttrs
        _mode = self.var_random_mode.getValue()
        _blend_mode = self.var_blend_mode.getValue()

        #pprint.pprint(vars())
        
        _current_time = mc.currentTime(query=True)
        for a,d in self.d_activeAttrs.items():
            for mObj in _targets:
                _node = mObj.mNode
                _value = random.uniform(d['min'],d['max'])
                print("{} | min: {} | max: {} | mode: {} | blend: {}".format(_value, d['min'], d['max'], _mode, _blend_mode))
                
                
                #Do our blend setup stuff ---
                #Query our pre,post values BEFORE we change the curve                
                if _blend_mode in ['pre','peak']:
                    _pre_time = _current_time + self.uiFF_preOffset.getValue()
                    _pre_value = SEARCH.get_anim_value_by_time(_node,[a], _pre_time)

                    mc.setKeyframe( _node, t=[_pre_time], at=a, v=_pre_value )
                    
                    
                if _blend_mode in ['post','peak']:
                    _post_time = _current_time + self.uiFF_postOffset.getValue()
                    _post_value = SEARCH.get_anim_value_by_time(_node,[a], _post_time)
                    
                    mc.setKeyframe( _node, t=[_post_time], at=a, v=_post_value )
                
                #...regular stuff
                if _mode == 'absolute':
                    print("{} | min: {} | max: {} | mode: {} | blend: {}".format(_value, d['min'], d['max'], _mode, _blend_mode))                    
                    #ATTR.set(_node, a, _value)
                elif _mode == 'nudge':
                    _base = SEARCH.get_anim_value_by_time(_node,[a], _current_time) or ATTR.get(_node, a)
                    print("{} | base: {} | min: {} | max: {} | mode: {} | blend: {}".format(_value, _base, d['min'], d['max'], _mode, _blend_mode))                    
                    
                    _value = _value + _base
                    #ATTR.set(_node, a, _value + _base)
                
                if not SEARCH.get_anim_value_by_time(_node,[a], _current_time):
                    ATTR.set(_node,a,_value)
                else:
                    mc.setKeyframe( _node, t=[_current_time], at=a, v=_value )
                #mc.setKeyframe(_node, at=a)
        
    def uiFunc_attrs_clear(self):
        _str_func = 'uiFunc_attrs_clear[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        self.l_attrs = []
        self.uiFunc_refreshAttrList()
        
    def uiFunc_flipBlend(self,mode = '<'):
        _str_func = 'uiFunc_flipBlend[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        if mode == 'f':
            _pre = -self.uiFF_postOffset.getValue()
            _post = -self.uiFF_preOffset.getValue()
            
            self.uiFF_preOffset.setValue(_pre)
            self.uiFF_postOffset.setValue(_post)

            
        elif mode == '<':
            self.uiFF_preOffset.setValue(-self.uiFF_postOffset.getValue())
            
        else:
            self.uiFF_postOffset.setValue(-self.uiFF_preOffset.getValue())
        
        self.var_postOffset.setValue(self.uiFF_postOffset.getValue())
        self.var_preOffset.setValue(self.uiFF_preOffset.getValue())
            
        
    def uiFunc_removeData(self,idx=None):
        _str_func = 'uiFunc_removeData[{0}]'.format(self.__class__.TOOLNAME)
        log.debug(log_start(_str_func))
        
        try:
            _a = self.l_attrs[idx]
        except:
            raise ValueError("{} | invalid idx: {}".format(_str_func,idx))
            
        result = mc.confirmDialog(title="Removing a| Dat {}".format(_a),
                                  message= "Remove: {}".format(_a),
                                  button=['OK','Cancel'],
                                  defaultButton='OK',
                                  cancelButton='Cancel',
                                  dismissString='Cancel')
        
        if result != 'OK':
            log.error("|{}| >> Cancelled.".format(_str_func))
            return False        
        
        if idx is not None:
            self.l_attrs.remove(_a)
            self.uiFunc_refreshAttrList()            
            return
        
        
    #@cgmGEN.Wrap_exception
    def uiFunc_refreshAttrList(self):
        _str_func = 'uiFunc_refreshAttrList[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        self._dCB_attrs = {}
        self._dMin_attrs = {}
        self._dMax_attrs = {}
        
        self.uiFrame_attrs.clear()
        
        if not self.l_attrs:
            mc.warning( cgmGEN.logString_msg(_str_func,"No attributes registered"))
            return
        
        self.l_attrs = sorted(self.l_attrs)
        
        for i,a in enumerate(self.l_attrs):
            try:
                #Row...
                _label = d_attrNames.get(a,a)
                
                if MATH.is_even(i):
                    _ut = 'cgmUIInstructionsTemplate'
                else:
                    _ut = 'cgmUISubTemplate'
                    
                _row = mUI.MelHSingleStretchLayout(self.uiFrame_attrs,ut = _ut)            
                
                mUI.MelSpacer(_row,w=5)

                _cb = mUI.MelCheckBox(_row,l=_label,
                                      #w=30,
                                     #annotation = d_dat.get('ann',k),
                                     value = 1)
                self._dCB_attrs[i] = _cb
                _row.setStretchWidget(_cb)
                
                
                self._dMin_attrs[i]  = mUI.MelFloatField(_row,precision = 1,
                                                         value = -1,
                                                         width = 40)
                self._dMax_attrs[i]  = mUI.MelFloatField(_row,precision = 1,
                                                         value = 1,
                                                         width = 40)
                
                
                mUI.MelButton(_row, label = '-',
                              ann= _d_annotations.get("Remove Attrs",'fix'),
                              c = cgmGEN.Callback(self.uiFunc_removeData,i))
                
                mUI.MelSpacer(_row,w=5)                
                _row.layout()
                
                #mUI.MelSeparator(self.uiFrame_attrs,h=1)
            except Exception as err:
                log.error(err)
        #self.uiFrame_attrs.layout()
        
    def uiFunc_setToggles(self,arg):
        for i,mCB in list(self._dCB_attrs.items()):
            mCB.setValue(arg)
            
    def uiBuild_top(self):
        _str_func = 'uiUpdate_top[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        self.uiSection_top.clear()
        
        _inside = self.uiSection_top
        
        #>>>Mode  Options -------------------------------------------------------------------------------
        _rowRandomMode = mUI.MelHSingleStretchLayout(_inside,ut='cgmUIHeaderTemplate',padding = 5)
    
        mUI.MelSpacer(_rowRandomMode,w=5)                          
        mUI.MelLabel(_rowRandomMode,l='Mode: ')
        _rowRandomMode.setStretchWidget( mUI.MelSeparator(_rowRandomMode) )
    
        uiRC = mUI.MelRadioCollection()
    
        mVar = self.var_random_mode
        _on = mVar.value
    
        for i,item in enumerate(_l_toolModes):
            if item == _on:
                _rb = True
            else:_rb = False
            _label = str(_d_shorts.get(item,item))
            uiRC.createButton(_rowRandomMode,label=_label,sl=_rb,
                              ann = "Set keys context to: {0}".format(item),                          
                              onCommand = cgmGEN.Callback(mVar.setValue,item))

        mUI.MelSpacer(_rowRandomMode,w=2)                          
        
        _rowRandomMode.layout()
        #............................................................................
        
        #>>>Mode  Options -------------------------------------------------------------------------------
        _rowBlendMode = mUI.MelHSingleStretchLayout(_inside,ut='cgmUITemplate',padding = 5)
    
        mUI.MelSpacer(_rowBlendMode,w=5)                          
        #mUI.MelLabel(_rowBlendMode,l='Blend: ')
        _rowBlendMode.setStretchWidget( mUI.MelSeparator(_rowBlendMode) )
        
    
        uiRC = mUI.MelRadioCollection()
    
        mVar = self.var_blend_mode
        _on = mVar.value
    
        for i,item in enumerate(_l_blendModes):
            if item == _on:
                _rb = True
            else:_rb = False
            _label = str(_d_shorts.get(item,item))
            uiRC.createButton(_rowBlendMode,label=_label,sl=_rb,
                              ann = "Set keys context to: {0}".format(item),                          
                              onCommand = cgmGEN.Callback(mVar.setValue,item))



        self.uiFF_preOffset= mUI.MelFloatField(_rowBlendMode,precision = 1,ut='cgmUITemplate',
                                                 value = self.var_preOffset.getValue(),
                                                 ann = _d_annotations.get('Set pre blend','fix'),                                                                           
                                                 width = 40, )
        
        self.uiFF_preOffset(edit =True, cc = lambda *a:self.var_preOffset.setValue(self.uiFF_preOffset.getValue()))
        
        mUI.MelButton(_rowBlendMode, label = '>',ut='cgmUITemplate',
                      ann = "Send pre value to post",                      
                      c = cgmGEN.Callback(self.uiFunc_flipBlend,'>'))
        mUI.MelButton(_rowBlendMode, label = 'f',ut='cgmUITemplate',
                      ann = "flip pre/post Values",                      
                      c = cgmGEN.Callback(self.uiFunc_flipBlend,'f'))        
        mUI.MelButton(_rowBlendMode, label = '<',ut='cgmUITemplate',
                      ann = "Send post value to pre",
                      c = cgmGEN.Callback(self.uiFunc_flipBlend,'<'))

            
        self.uiFF_postOffset= mUI.MelFloatField(_rowBlendMode,precision = 1,ut='cgmUITemplate',
                                                 value = self.var_postOffset.getValue(),
                                                 ann = _d_annotations.get('Set post blend','fix'),                                                                                                                            
                                                 width = 40, )
        
        self.uiFF_postOffset(edit =True, cc = lambda *a:self.var_postOffset.setValue(self.uiFF_postOffset.getValue()))


        mUI.MelSpacer(_rowBlendMode,w=2)                          
        _rowBlendMode.layout()
        mUI.MelSpacer(_inside,h=2)
        #............................................................................        
        

        
        #--------------------------------------------------------------
        _row = mUI.MelHLayout(_inside, h=30, padding=5 )
        mUI.MelButton(_row, label = 'All',ut='cgmUITemplate',
                      c = cgmGEN.Callback(self.uiFunc_setToggles,1))
        mUI.MelButton(_row, label = 'None',ut='cgmUITemplate',
                      c = cgmGEN.Callback(self.uiFunc_setToggles,0))
        mUI.MelSeparator(_row,w=10)
        mUI.MelButton(_row, label = 'Clear',ut='cgmUITemplate',
                      c = cgmGEN.Callback(self.uiFunc_attrs_clear))
        mUI.MelButton(_row, label = 'Add',ut='cgmUITemplate',
                      c = cgmGEN.Callback(self.uiFunc_attrs_add))                         
        #mUI.MelButton(_row, label = 'Remove',ut='cgmUITemplate',
        #              c = cgmGEN.Callback(self.uiFunc_removeData))
        _row.layout()        
        
        """
        mUI.MelButton(_inside,l='Get Attrs',
                      ut='cgmUITemplate',
                      #w=150,
                      c = cgmGEN.Callback(self.uiFunc_attrs_add),                         
                      ann=_d_annotations.get('Get Attrs','fix'))
                      """
        self.uiFrame_attrs = mUI.MelColumnLayout(_inside,useTemplate = 'cgmUISubTemplate') 
        
        
        mc.setParent(_inside)
        cgmUI.add_HeaderBreak()
    