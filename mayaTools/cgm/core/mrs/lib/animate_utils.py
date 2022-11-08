"""
------------------------------------------
cgm.core.mrs.lib.animate
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
__MAYALOCAL = 'MRSANIMUTILS'

# From Python =============================================================
import copy
import re
import pprint
import time
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
_b_debug = log.isEnabledFor(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel    

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import Red9.core.Red9_CoreUtils as r9Core

import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgm_General as cgmGEN
from cgm.core.classes import GuiFactory as CGMUI
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.search_utils as SEARCH
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.math_utils as MATH
from Red9.core import Red9_AnimationUtils as r9Anim
import cgm.core.mrs.lib.general_utils as BLOCKGEN
import cgm.core.classes.GuiFactory as cgmUI
import cgm.core.lib.constraint_utils as CONSTRAINT

mUI = cgmUI.mUI
#reload(cgmGEN)
"""
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.rig.general_utils as CORERIGGEN
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core import cgm_RigMeta as cgmRigMeta
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.lib.locator_utils as LOC
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.position_utils as POS
import cgm.core.rig.joint_utils as JOINT
import cgm.core.rig.ik_utils as IK
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.mrs.lib.builder_utils as BUILDUTILS
import cgm.core.lib.shapeCaster as SHAPECASTER
reload(SHAPECASTER)
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.cgm_RigMeta as cgmRIGMETA"""


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.1.04192019'


_d_contexts = {'control':{'short':'ctrl'},
               'part':{},
               'puppet':{'short':'char'},
               'scene':{},
               'list':{}}
_l_contexts = ['control','part','puppet','scene','list']
_l_contextTime = ['back','previous','current','bookEnd','next','forward','slider','selected']
_d_timeShorts = {'back':'<-',
                 'previous':'|<',
                 'bookEnd':'|--|',
                 'current':'now',
                 'selected':'sel',
                 'next':'>|',
                 'slider':'[ ]',
                 'forward':'->'}
_l_contextKeys = ['each','combined']


def log_start(str_func):
    log.debug("|{0}| >> ...".format(str_func)+'/'*60)

def ik_bankRollShapes(self):
    try:
        _str_func = 'bankRollShapes'
        log.debug(cgmGEN.logString_sub(_str_func))        

    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

_d_contextAttrs = {'poseMatchMethod':{'dv':'base'},
                   'time':{'dv':'current'},
                   'mode':{'dv':_l_contexts[0]},
                   'keys':{'dv':'each'}}

def get_contextDict(prefix=False):
    _res = {}
    for a,d in _d_contextAttrs.iteritems():
        _name = None
        try:
            if prefix:
                _name = "cgmVar_mrsContext_{0}_{1}".format(prefix,a) 
            else:
                _name = "cgmVar_mrsContext_{0}".format(a)
            
            if a in ['poseMatchMethod']:
                _res[a] = cgmMeta.cgmOptionVar(_name).value
            else:
                _res['context'+a.capitalize()] = cgmMeta.cgmOptionVar(_name).value
                
        except Exception,err:
            log.warning("Failed to query context: {0} | {1}".format(_name,err))
            
    _l_order = ['core','children','siblings','mirror']
    
    for k in _l_order:
        _name = None
        try:
            if prefix:
                _name = 'cgmVar_mrsContext_' + prefix + '_' + k
            else:
                _name = 'cgmVar_mrsContext_'  + k
                
            _res['context'+k.capitalize()] = cgmMeta.cgmOptionVar(_name).value
        except Exception,err:
            log.warning("Failed to query context: {0} | {1}".format(_name,err))
    
    if prefix:
        _res['contextPrefix'] = prefix
        
    #pprint.pprint(_res)
    return _res
            
def uiSetup_context(self,prefix=False):
    self._l_contexts = _l_contexts
    self._l_contextTime = _l_contextTime
    self._l_contextKeys = _l_contextKeys
    
    for a,d in _d_contextAttrs.iteritems():
        if prefix:
            _name = "cgmVar_mrsContext_{0}_{1}".format(prefix,a) 
        else:
            _name = "cgmVar_mrsContext_{0}".format(a)
        
        self.__dict__['var_mrsContext_{0}'.format(a)] = cgmMeta.cgmOptionVar(_name, defaultValue = d['dv'])
        log.info(cgmGEN.logString_msg('uiSetup_context', self.__dict__['var_mrsContext_{0}'.format(a)]))
            
    return
    try:self.var_poseMatchMethod
    except:
        if toolSpecific:
            _name = "cgmVar_%s%s"%(self.__class__.TOOLNAME,'poseMatchMethod')            
        else:
            _name = "cgmVar_{0}".format('poseMatchMethod')
            self.var_poseMatchMethod = cgmMeta.cgmOptionVar('cgmVar_poseMatchMethod', defaultValue = 'base')
        
    try:self.var_mrsContext
    except:self.var_mrsContext = cgmMeta.cgmOptionVar('cgmVar_mrsContext_mode',
                                                      defaultValue = _l_contexts[0])
    try:self.var_mrsContext_time
    except:self.var_mrsContext_time = cgmMeta.cgmOptionVar('cgmVar_mrsContext_time',
                                                      defaultValue = 'current')
    try:self.var_mrsContext_keys
    except:self.var_mrsContext_keys = cgmMeta.cgmOptionVar('cgmVar_mrsContext_keys',
                                                      defaultValue = 'each')
        
def uiColumn_context(self,parent,header=False):
    #>>>Context set -------------------------------------------------------------------------------    
    _column = mUI.MelColumn(parent,useTemplate = 'cgmUITemplate') 
    
    if header:
        _header = cgmUI.add_Header('Context')
        
    
    _rowContext = mUI.MelHLayout(_column,ut='cgmUISubTemplate',padding=10)

    uiRC = mUI.MelRadioCollection()
    
    mVar = self.var_mrsContext_mode
    _on = mVar.value

    for i,item in enumerate(_l_contexts):
        if item == _on:
            _rb = True
        else:_rb = False
        _label = str(_d_contexts[item].get('short',item))
        uiRC.createButton(_rowContext,label=_label,sl=_rb,
                          ann = "Set context: {0}".format(item),
                          onCommand = cgmGEN.Callback(mVar.setValue,item))

        #mUI.MelSpacer(_row,w=1)       
    _rowContext.layout() 
    
    #>>>Context Options -------------------------------------------------------------------------------
    _rowContextSub = mUI.MelHSingleStretchLayout(_column,ut='cgmUISubTemplate',padding = 5)
    _d = {'children':'chldrn',
          'siblings':'sblg',
          'mirror':'mrr'}
    
    mUI.MelSpacer(_rowContextSub,w=5)                          
    mUI.MelLabel(_rowContextSub,l='Options:')
    _rowContextSub.setStretchWidget( mUI.MelSeparator(_rowContextSub) )
    
    _d_defaults = {}
    _l_order = ['core','children','siblings','mirror']
    self._dCB_contextOptions = {}
    for k in _l_order:
        _plug = 'cgmVar_mrsContext_' + self.__class__.TOOLNAME + '_'+ k
        _selfPlug = 'var_mrsContext_'+k
        try:self.__dict__[_selfPlug]
        except:
            _default = _d_defaults.get(k,0)
            #log.debug("{0}:{1}".format(_plug,_default))
            self.__dict__[_selfPlug] = cgmMeta.cgmOptionVar(_plug, defaultValue = _default)

        l = _d.get(k,k)
        
        _cb = mUI.MelCheckBox(_rowContextSub,label=l,
                              annotation = 'Include {0} in context.'.format(k),
                              value = self.__dict__[_selfPlug].value,
                              onCommand = cgmGEN.Callback(self.__dict__[_selfPlug].setValue,1),
                              offCommand = cgmGEN.Callback(self.__dict__[_selfPlug].setValue,0))
        self._dCB_contextOptions[k] = _cb
        
    mUI.MelSpacer(_rowContextSub,w=5)                      
        
    _rowContextSub.layout()
    
    return _column


def get_sharedDatObject(**kws):
    global MRSDAT
    if MRSDAT:
        log.debug('existing global MRSDAT')
        return MRSDAT
    
    log.warning('new MRSDAT')
    return dat(**kws)

class dat(object):
    def __init__(self,datTarget=None,datString='dat',update=False):
        _str_func = 'dat.__init__'
        global MRSDAT
        #if MRSDAT and not update:
            #self = MRSDAT
            #return
        self.dat = {}
        
        self.datTarget = None
        self.datString = datString
        self.d_context = {}
        self.d_buffer = {}
        self.d_timeContext = {}
        self.d_parts = {}
        self.d_timeSnips = {}
        self._ml_listNodes = []
        
        if datTarget:
            self.datTarget = datTarget
            if self.datString not in self.datTarget.__dict__.keys():
                self.datTarget.__dict__[self.datString] = self.dat
                
        else:
            pass
            """
            try:self.var_mrsContext_mode
            except:self.var_mrsContext_mode = cgmMeta.cgmOptionVar('cgmVar_mrsContext_mode',
                                                              defaultValue = 'control')
            try:self.var_mrsContext_time
            except:self.var_mrsContext_time = cgmMeta.cgmOptionVar('cgmVar_mrsContext_time',
                                                              defaultValue = 'current')
            try:self.var_mrsContext_keys
            except:self.var_mrsContext_keys = cgmMeta.cgmOptionVar('cgmVar_mrsContext_keys',
                                                              defaultValue = 'each')
            
            _l_order = ['children','siblings','mirror','core']
            for k in _l_order:
                _plug = 'cgmVar_mrsContext_' + k
                _selfPlug = 'var_mrsContext_' + k
                try:self.__dict__[_selfPlug]
                except:
                    self.__dict__[_selfPlug] = cgmMeta.cgmOptionVar(_plug, defaultValue = 0)
                    """
        self.clear()
        
        MRSDAT = self
        
    def clear(self):
        _str_func='dat.clear'        
        log.debug(cgmGEN.logString_start(_str_func))
        self.dat = {'mPuppets':[],
                    'mModules':[],
                    'mControls':[],
                    'sControls':[]}
        self.d_parts = {}
        self.d_timeContext = {}
        self._sel = []
        self._ml_sel = []        
        self.d_timeSnips = {}
        
    #@cgmGEN.Timer
    def get_all(self,update=False):
        _str_func='dat.get_all'
        log.debug(cgmGEN.logString_start(_str_func))        
        self.dat = get_buffer_dat(update)
        return self.dat
    
    #@cgmGEN.Timer
    def puppets_scene(self,update=False):
        _str_func='dat.puppets_scene'
        log.debug(cgmGEN.logString_start(_str_func))
        
        if update:self.clear()
            
        if not self.dat.get('mPuppets'):
            log.debug("|{0}| >> No puppets buffered...".format(_str_func))
            mPuppets_scene = r9Meta.getMetaNodes(mTypes = 'cgmRigPuppet',nTypes=['network'])
            if not mPuppets_scene:
                return False
            
            for mPuppet in mPuppets_scene:
                self.puppet_get(mPuppet, update)
    
    #@cgmGEN.Timer
    def module_get(self, mModule, update=False):
        _str_func='dat.module_get'
        log.debug(cgmGEN.logString_start(_str_func))
        
        if  self.dat.get(mModule):
            log.debug(cgmGEN.logString_msg('using buffer...'))                        
            if not update:
                return self.dat[mModule]                    
                #return self.dat.get(mModule,{})
                
        if not mModule in self.dat['mModules']:
            self.dat['mModules'].append(mModule)
            
        try:
            _progressBar = CGMUI.doStartMayaProgressBar()
            _res = self.dat

            _str = "{0}".format(mModule)
            log.debug(cgmGEN.logString_start(_str))
            
            _m = {}

            #Mirror...
            _m['mMirror'] = mModule.UTILS.mirror_get(mModule)

            #Children...
            ml_children = mModule.UTILS.moduleChildren_get(mModule) or []
            _m['mChildren'] = ml_children
            if _b_debug:
                log.debug(cgmGEN.logString_msg('children'))                
                for i,mObj in enumerate(ml_children):
                    log.debug("{0} | {1}".format(i,mObj))
                log.debug(cgmGEN._str_subLine)
            
            #Controls...
            ml_controls = mModule.UTILS.controls_get(mModule)#rigNull.moduleSet.getMetaList()
            _m['mControls'] = ml_controls
            try:_m['mCore'] = mModule.mControlsCore
            except:_m['mCore'] = ml_controls
            
            for mObj in ml_controls:
                if CONSTRAINT.get_constraintsTo(mObj.mNode):
                    try:
                        _m['mControls'].remove(mObj)
                        log.warning("Constrained: {0}".format(mObj))
                        _m['mCore'].remove(mObj)
                    except:pass
                        

                
            """
            l_controls = []
            len_controls = len(ml_controls)
            
            if ml_controls:
                for i,mObj in enumerate(ml_controls):
                    _str = "{0} | {1}".format(i,mObj)
                    log.debug(_str)
                    CGMUI.progressBar_set(_progressBar,step=1,
                                          maxValue = len_controls,
                                          status = _str)
                    
                    #l_controls.append(mObj.mNode)
                    _res[mObj] = {}
                    _res[mObj]['mMirror'] = mObj.getMessageAsMeta('mirrorControl')
                    
            #_m['sControls'] = l_controls
            log.debug(cgmGEN._str_subLine)"""
            
            #Siblings...
            ml_siblings = mModule.UTILS.siblings_get(mModule) or []
            _m['mSiblings'] = ml_siblings
            """
            if _b_debug:
                log.debug(cgmGEN.logString_msg('siblings'))                
                for iii,mObj in enumerate(ml_siblings):
                    log.debug("{0} | {1}".format(iii,mObj))
                log.debug(cgmGEN._str_subLine)"""
                
            self.dat[mModule] = _m
            return self.dat[mModule]
        except Exception,err:
            log.error(err)
        finally:
            CGMUI.doEndMayaProgressBar()
            
    def report_contextDat(self):
        if not self.d_context:
            return False
        
        context = self.d_context.get('context')# or self.var_mrsContext.value
        b_children = self.d_context.get('children')# or self.var_mrsContext_children.value
        b_siblings = self.d_context.get('siblings')# or self.var_mrsContext_siblings.value
        b_mirror = self.d_context.get('mirror')# or self.var_mrsContext_mirror.value
        b_core = self.d_context.get('core')# or self.var_mrsContext_core.value
        
        log.info("context: {0} | children: {1} | siblings: {2} | mirror: {3} | core: {4}".format(context,b_children,b_siblings,b_mirror,b_core))
        
        log.info("controls: {0}".format(len(self.d_context['mControls'])))
        log.info("modules: {0}".format(len(self.d_context['mModules'])))
        for i,v in enumerate(self.d_context['mModules']):
            log.info("[{0}] : {1}".format(i,v))
        log.info(cgmGEN._str_subLine)
        log.info("puppets: {0}".format(len(self.d_context['mPuppets'])))
        for i,v in enumerate(self.d_context['mPuppets']):
            log.info("[{0}] : {1}".format(i,v))
        log.info(cgmGEN._str_subLine)
        
        if self.d_context.get('mModulesBase'):
            log.info("baseModules: {0}".format(len(self.d_context['mModulesBase'])))
            for i,v in enumerate(self.d_context['mModulesBase']):
                log.info("[{0}] : {1}".format(i,v))
            log.info(cgmGEN._str_subLine)            
        pprint.pprint(self.d_context)
        
        #for i,v in enumerate(self.d_context['res']):
        #    log.info("[{0}] : {1}".format(i,v))
        
    def report_timeDat(self):
        if not self.d_timeContext:
            return False

        d_timeContext = self.d_timeContext
        
        _context = self.d_timeContext.get('context')# or self.var_mrsContext.value
        _contextTime = self.d_timeContext.get('contextTime')# or self.var_mrsContext_time.value
        _contextKeys = self.d_timeContext.get('contextKeys')# or self.var_mrsContext_keys.value
        _frame = self.d_timeContext['frameInitial']
        

        _keys = d_timeContext.keys()
        _keys.sort()    
        if _context not in ['control']:
            log.info("Context: {0} | keys: {1} | sources: {2}".format(_context, len(d_timeContext.keys()),
                                                                      len(d_timeContext['partControls'])))
            log.info(cgmGEN.logString_sub(None,'Sources'))
            for mObj,l in d_timeContext['partControls'].iteritems():
                log.info("[{0}] || controls: {1}".format(mObj,len(l)))        
            log.info(cgmGEN.logString_sub(None,'Keys'))
            for k in _keys:
                log.info("{0} : {1}".format(k,d_timeContext[k]))
            log.info(cgmGEN._str_subLine)
            
            #pprint.pprint(d_timeContext['partControls'])
                
        else:
            log.info("Context: {0} | Time: {1} | keys: {2}".format(_context, _contextTime, len(d_timeContext.keys())))        
            for k in _keys:
                log.info("{0} : {1}".format(k,d_timeContext[k]))
            log.info(cgmGEN._str_subLine)
        pprint.pprint(d_timeContext['res'])

            
    #@cgmGEN.Timer
    def control_get(self, mObj, update=False):
        _str_func='dat.control_get'
        log.debug(cgmGEN.logString_start(_str_func))
        _res = self.dat
        
        if mObj in self.dat['mControls']:
            log.debug(cgmGEN.logString_msg('using buffer...'))
            d = self.dat.get(mObj)
            if not update and d:return d
        else:
            self.dat['mControls'].append(mObj)
        
        _d = {}
        
        if mObj.getMessage('rigNull'):
            mModule = mObj.rigNull.module
            #d_mModule = self.module_get(mModule,update)
            _d['mModule'] = mModule
            
            if mModule.getMessage('modulePuppet'):
                mPuppet = mModule.modulePuppet
                #d_mPuppet = self.puppet_get(mPuppet,update)
                _d['mPuppet'] = mPuppet

        elif mObj.getMessage('puppet'):
            mPuppet = mObj.puppet
            #d_mPuppet = self.puppet_get(mPuppet,update)
            _d['mPuppet'] = mPuppet
            _d['mModule'] = False
            
        _d['mMirror'] = mObj.getMessageAsMeta('mirrorControl')
        
        self.dat[mObj] = _d
        
        if CONSTRAINT.get_constraintsTo(mObj.mNode):
            try:
                self.dat['mControls'].remove(mObj)
                log.warning("Constrained: {0}".format(mObj))
            except:pass        
        return _d

    #@cgmGEN.Timer
    def puppet_get(self, mPuppet, update=False):
        _str_func='dat.puppet_get'
        log.debug(cgmGEN.logString_start(_str_func))
        if not mPuppet.mNode:
            log.warning("dead: {0} ...".format(mPuppet))
            
            try:self.dat.pop(mPuppet)
            except:pass
            return False
        
        if self.dat.get(mPuppet):
            log.debug(cgmGEN.logString_msg('using buffer...'))                        
            if not update:
                return self.dat[mPuppet]           
            
        if mPuppet not in self.dat['mPuppets']:
            self.dat['mPuppets'].append(mPuppet)
        
        try:
            log.debug("{0} ...".format(mPuppet))
            _p = {}
            
            ml_modules = mPuppet.UTILS.modules_get(mPuppet)
            _p['mModules'] = ml_modules
            _p['mChildren'] = []
            _p['mControls'] = []
            _p['mPuppetControls'] = mPuppet.UTILS.controls_get(mPuppet)
            _p['sControls'] = []
            _p['mControls'] = mPuppet.UTILS.controls_get(mPuppet,True)
            _p['mCore'] = mPuppet.UTILS.controls_get(mPuppet,core=True)

            self.dat[mPuppet] = _p
            return _p
        except Exception,err:
            log.error(err)

    def get_buffer(self,context,children,siblings):
        pass
    
    def select_lastContext(self):
        _str_func='select_lastContext'
        log.info("|{0}| {1} >>  ".format(_str_func, self)+ '-'*80)        
        ml_buffer = self.d_context.get('mControls')
        if ml_buffer:
            l_buffer = [mObj.mNode for mObj in ml_buffer]
            mc.select(l_buffer)
            return ml_buffer
        return False
    
    #@cgmGEN.Timer
    def context_get(self, mObj = None, addMirrors = False, mirrorQuery = False, **kws):
        _str_func='context_get'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
                        
        _keys = kws.keys()
        
        #pprint.pprint(kws)
        
        d_globalContext = get_contextDict(kws.get('contextPrefix',False))

        context = kws.get('contextMode',d_globalContext['contextMode'])
        b_children = kws.get('contextChildren', d_globalContext['contextChildren']) 
        b_siblings = kws.get('contextSiblings', d_globalContext['contextSiblings'])
        b_mirror = kws.get('contextMirror',d_globalContext['contextMirror'])
        b_core = kws.get('contextCore',d_globalContext['contextCore'])
        
        
        #pprint.pprint(d_globalContext)
        #_contextTime = kws.get('contextTime') or self.var_mrsContext_time.value
        #_contextKeys = kws.get('contextKeys') or self.var_mrsContext_keys.value

        if context == 'puppet' and b_siblings:
            log.warning("Context puppet + siblings = scene mode")
            context = 'scene'
            b_siblings = False
        
        log.info("|{0}| >> context: {1} | children: {2} | siblings: {3} | mirror: {4} | core: {5}".format(_str_func,context,b_children,b_siblings,b_mirror,b_core))
        
        #>>  Individual objects....===============================================================
        sel = mc.ls(sl=True)
        ml_sel = cgmMeta.asMeta(sl=1,noneValid=True) or []
        ml_check = copy.copy(ml_sel)
        
        self._sel = sel
        self._ml_sel = ml_sel
        log.info("Selected: {0}".format(len(self._sel)))
        self.d_context = {'mControls':[],
                          'mControlsMirror':[],
                          'mPuppets':[],
                          'mModules':[],
                          'b_puppetPart':False,
                          'mModulesMirror':[],
                          'mModulesBase':[]}
        
        res = []
        #------------------------------------------------------
        _cap = 5
        
        if context == 'list':
            if not self._ml_listNodes:
                log.error("No nodes selected")
                return False
            
            ml_modules = []
            ml_puppets = []
            for mObj in self._ml_listNodes:
                log.info(mObj)
                if mObj.mNode:
                    _mClass = mObj.getMayaAttr('mClass')
                    if _mClass == 'cgmRigPuppet':
                        log.info('cgmRigPuppet: {0}'.format(mObj))
                        ml_puppets.append(mObj)
                    elif _mClass == 'cgmRigModule':
                        log.info('cgmRigModule: {0}'.format(mObj))                        
                        ml_modules.append(mObj)
                        
            if not ml_modules and not ml_puppets:
                log.error("List | no modules or puppets found")
                return False
                
                        
            if ml_puppets:
                log.info("|{0}| >> list puppet...".format(_str_func))
                context = 'puppet'
                for mPuppet in ml_puppets:
                    if mPuppet not in self.d_context['mPuppets']:
                        self.d_context['mPuppets'].append(mPuppet)
                    res.append(mPuppet)
            else:
                log.info("|{0}| >> list modules...".format(_str_func))
                context = 'part'
                for mModule in ml_modules:
                    if mModule not in self.d_context['mModules']:
                        self.d_context['mModules'].append(mModule)
                        self.d_context['mModulesBase'].append(mModule)                    
                    res.append(mModule)                

        elif context == 'scene':
            try:
                if self.d_buffer.get['scene']:
                    self.d_context = self.d_buffer['scene']
                    return self.d_buffer['scene']['mControls']
            except:
                log.debug("|{0}| >> no buffer...".format(_str_func))
                

            log.debug("|{0}| >> Scene mode...".format(_str_func))
            if not self.dat.get('mPuppets'):
                log.debug("|{0}| >> No puppets buffered...".format(_str_func))
                mPuppets_scene = r9Meta.getMetaNodes(mTypes = 'cgmRigPuppet',nTypes=['network'])
                if not mPuppets_scene:
                    log.error("No puppets in scene.")
                    return False
                else:
                    self.puppets_scene(True)
                    
            self.d_context['mPuppets'] = self.dat['mPuppets']#r9Meta.getMetaNodes(mTypes = 'cgmRigPuppet')
            #self.d_context['mModules'] = self.dat['mModules']
            #for mPuppet in self.d_context['mPuppets']:
                #self.d_context['mControls'].extend(self.d_parts[mPuppet])
        
            #self.d_context['mControls'] = self.dat['mControls']
            
            log.debug(cgmGEN.logString_msg("Scene current bail..."))
            #if _b_debug:
                #pprint.pprint(self.d_context)
            
            self.d_buffer['scene'] = self.d_context
            
            ml=[]
            for mPuppet in self.d_context['mPuppets']:
                log.debug("|{0}| >> puppet: {1}".format(_str_func,mPuppet))                    
                d_ = self.puppet_get(mPuppet)                            
                ml.extend(d_['mControls'])
                self.d_context['mModules'].extend(d_['mModules'])
            self.d_context['mControls'] = ml
            self.d_context['res'] = self.d_context['mPuppets'] 
            
            return self.d_context['mControls'] 
            
        else:
            if mObj:
                res.append(mObj)
                ml_check = [mObj]
                
            for i,mObj in enumerate(ml_check):
                log.debug(cgmGEN.logString_sub(_str_func,"First pass check: {0}".format(mObj)))
                
                if context != 'control' and i > _cap:
                    log.debug("|{0}| >> Large number of items selected, stopping processing at {1}".format(_str_func,i))              
                    break
                
                #>>> Module --------------------------------------------------------------------------
                d_mObj = self.control_get(mObj)
                mModule = d_mObj.get('mModule')
                mPuppet = d_mObj.get('mPuppet')
                
                if mObj not in self.d_context['mControls']:
                    log.debug(cgmGEN.logString_msg("Not in context..."))
                    self.d_context['mControls'].append(mObj)
                    if context == 'control':
                        res.append(mObj)
                        
                if mModule and not self.d_context['mModulesBase']:
                    self.d_context['mModulesBase'].append(mModule)
                        
                if context == 'part':
                    if mModule:
                        if mModule not in self.d_context['mModules']:
                            self.d_context['mModules'].append(mModule)
                        res.append(mModule)
                        
                if mPuppet not in self.d_context['mPuppets']:
                    self.d_context['mPuppets'].append(mPuppet)
                    
                if context == 'puppet':
                    res.append(mPuppet)
                else:
                    res.append(mObj)

        #before we get mirrors we're going to buffer our main modules so that mirror calls don't get screwy
        if not self.d_context['mModulesBase']:
            self.d_context['mModulesBase'] = copy.copy(self.d_context['mModules'])
        ls=[]
        
        #process...
        log.debug(cgmGEN.logString_sub(_str_func,"Initial Process..."))
        
        #if context == 'control' and b_siblings:
            #if b_mirror or addMirrors:
                #log.warning("Context control + siblings = part mode")
                #context = 'part'
                #b_siblings = False
                
        if context == 'control':
            if b_siblings:
                ml_new = []
                for mObj in self.d_context['mControls']:
                    d_control = self.control_get(mObj)
                    mModule = d_control.get('mModule')
                    if mModule not in self.d_context['mModules']:
                        self.d_context['mModules'].append(mModule)
                        d_mModule = self.module_get(mModule)                            
                        ml_new.extend(d_mModule['mControls'])
                
                self.d_context['mControls'] = ml_new
                
            if  b_mirror or addMirrors:
                log.debug(cgmGEN._str_subLine)        
                log.debug("|{0}| >> Context mirror check...".format(_str_func))
                ml_mirror = []
                for mObj in self.d_context['mControls']:
                    d_control = self.control_get(mObj)
                    mMirror = d_control.get('mMirror')
                    if mMirror:
                        log.debug("|{0}| >> Found mirror for: {1}".format(_str_func,mObj))
                        ml_mirror.append(mMirror)
                        
                if ml_mirror:
                    res.extend(ml_mirror)
                    self.d_context['mControls'].extend(ml_mirror)
                    self.d_context['mControlsMirror'].extend(ml_mirror)
                    
        elif context == 'part':
            if b_siblings:
                log.debug(cgmGEN._str_subLine)        
                log.debug("|{0}| >> sibling check...".format(_str_func))
                
                log.debug(cgmGEN._str_hardBreak)
                log.debug("|{0}| >> JOSH ... part siblings won't work right until you tag build profile for matching ".format(_str_func))
                log.debug(cgmGEN._str_hardBreak)        
                
                res = []
                for mModule in self.d_context['mModules']:
                    res.append(mModule)
                    d_mModule = self.module_get(mModule)                            
                    
                    log.debug("|{0}| >> sibling check: {1}".format(_str_func,mModule))
                    mSib = d_mModule['mSiblings']
                    if mSib:res.extend(mSib)
                self.d_context['mModules'].extend(res)#...push new data back
                
            if b_children:
                for mModule in self.d_context['mModules']:
                    log.debug("|{0}| >> child check: {1}".format(_str_func,mModule))
                    d_mModule = self.module_get(mModule) or {}
                    for mChild in d_mModule.get('mChildren',[]):
                        if mChild not in self.d_context['mModules']:
                            d_mModule = self.module_get(mChild)
                            self.d_context['mModules'].append(mChild)
                            
            if  b_mirror or addMirrors:
                ml_mirrors =[]
                for mModule in self.d_context['mModules']:
                    d_mModule = self.module_get(mModule) or {}
                    mMirror = d_mModule.get('mMirror')#mModule.atUtils('mirror_get')
                    if mMirror:
                        log.debug("|{0}| >> Mirror: {1}".format(_str_func,mMirror))
                        if mMirror not in self.d_context['mModules']:
                            ml_mirrors.append(mMirror)
                
                for mModule in ml_mirrors:
                    if mModule not in self.d_context['mModules']:
                        self.d_context['mModules'].append(mModule)
                self.d_context['mModulesMirror'] = ml_mirrors
            
            
            ml = []
            for mModule in self.d_context['mModules']:
                d_mModule = self.module_get(mModule)
                ml_add = d_mModule['mControls']
                if b_core:
                    ml_core =  d_mModule.get('mCore')
                    if ml_core:
                        ml_add = ml_core
                ml.extend(ml_add)
            self.d_context['mControls'] = ml
            
        elif context == 'puppet':
            log.debug("|{0}| >> puppet check...".format(_str_func))
            
            ml = []
            for mPuppet in self.d_context['mPuppets']:
                log.info("|{0}| >> puppet: {1}".format(_str_func,mPuppet))
                if not mPuppet or mPuppet.getMayaAttr('mClass') != 'cgmRigPuppet':
                    self.d_context['mPuppets'].remove(mPuppet)
                    log.error('Bad puppet: {0}'.format(mPuppet))
                    continue
                
                d_ = self.puppet_get(mPuppet)
                if b_core:
                    ml.extend(d_['mCore'])
                else:
                    ml.extend(d_['mControls'])
                self.d_context['mModules'].extend(d_['mModules'])
            self.d_context['mControls'] = ml                
            

        self.d_context['res'] = res
        
        #log.info(self)
        for mObj in self.d_context['mControls']:
            if CONSTRAINT.get_constraintsTo(mObj.mNode):
                try:
                    self.d_context['mControls'].remove(mObj)
                    log.warning("Constrained: {0}".format(mObj))
                except:pass        
        return self.d_context['mControls']
    
    #@cgmGEN.Timer
    def get_noDup(self,l):
        return LISTS.get_noDuplicates(l)
    
    #@cgmGEN.Timer
    def get_contextBAK(self, mObj = None, addMirrors = False, mirrorQuery = False, **kws):
        try:
            
            _str_func='get_context'
            log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
                            
            _keys = kws.keys()
            
            context = kws.get('context') or self.var_mrsContext.value
            b_children = kws.get('children') or self.var_mrsContext_children.value
            b_siblings = kws.get('siblings') or self.var_mrsContext_siblings.value
            b_mirror = kws.get('mirror') or self.var_mrsContext_mirror.value
            
            #_contextTime = kws.get('contextTime') or self.var_mrsContext_time.value
            #_contextKeys = kws.get('contextKeys') or self.var_mrsContext_keys.value

            if context == 'puppet' and b_siblings:
                log.warning("Context puppet + siblings = scene mode")
                context = 'scene'
                b_siblings = False
            
            log.debug("|{0}| >> context: {1} | children: {2} | siblings: {3} | mirror: {4}".format(_str_func,context,b_children,b_siblings,b_mirror))
            
            #>>  Individual objects....===============================================================
            sel = mc.ls(sl=True)
            ml_sel = cgmMeta.asMeta(mc.ls(sl=True))
            ml_check = copy.copy(ml_sel)
            self._sel = sel
            self._ml_sel = ml_sel
            self.d_context = {'mControls':[],
                              'mControlsMirror':[],
                              'mPuppets':[],
                              'mModules':[],
                              'b_puppetPart':False,
                              'mModulesMirror':[],
                              'mModulesBase':[]}
            
            
            res = []
            #------------------------------------------------------
            _cap = 5
            
            if context == 'scene':
                try:return self.d_buffer['scene']
                except:
                    log.debug("|{0}| >> no buffer...".format(_str_func))
                    

                log.debug("|{0}| >> Scene mode...".format(_str_func))
                if not self.dat.get('mPuppets'):
                    log.debug("|{0}| >> No puppets buffered...".format(_str_func))
                    mPuppets_scene = r9Meta.getMetaNodes(mTypes = 'cgmRigPuppet',nTypes=['network'])
                    if not mPuppets_scene:
                        log.error("No puppets in scene.")
                        return False
                    else:
                        self.puppets_scene(True)
                        
                self.d_context['mPuppets'] = self.dat['mPuppets']#r9Meta.getMetaNodes(mTypes = 'cgmRigPuppet')
                #self.d_context['mModules'] = self.dat['mModules']
                for mPuppet in self.d_context['mPuppets']:
                    self.d_context['mControls'].extend(self.dat[mPuppet].get('mControls'))
            
                #self.d_context['mControls'] = self.dat['mControls']
                
                log.debug(cgmGEN.logString_msg("Scene current bail..."))
                #if _b_debug:
                    #pprint.pprint(self.d_context)
                
                self.d_buffer['scene'] = self.d_context
                return self.d_context['mPuppets']
                
            else:
                if mObj:
                    res.append(mObj)
                    ml_check = [mObj]
                    
                for i,mObj in enumerate(ml_check):
                    log.debug(cgmGEN.logString_sub(_str_func,"First pass check: {0}".format(mObj)))
                    
                    if i > _cap:
                        log.debug("|{0}| >> Large number of items selected, stopping processing at {1}".format(_str_func,i))              
                        break
                    
                    #>>> Module --------------------------------------------------------------------------
                    d_mObj = self.control_get(mObj)
                    mModule = d_mObj['mModule']
                    mPuppet = d_mObj['mPuppet']
                    
                    if mObj not in self.d_context['mControls']:
                        log.debug(cgmGEN.logString_msg("Not in context..."))
                        self.d_context['mControls'].append(mObj)
                        if context == 'control':
                            res.append(mObj)
                            
                    if context == 'part':
                        if mModule:
                            if mModule not in self.d_context['mModules']:
                                self.d_context['mModules'].append(mModule)
                            res.append(mModule)                
                    
                    if context == 'puppet':
                        if mPuppet not in self.d_context['mPuppets']:
                            self.d_context['mPuppets'].append(mPuppet)
                        res.append(mPuppet)
                    else:
                        res.append(mObj)
    
                    """
                    if mObj.getMessage('rigNull'):
                        if mObj not in self.d_context['mControls']:
                            self.d_context['mControls'].append(mObj)
                            if context == 'control':
                                res.append(mObj)
                        
                        d_mObj = self.control_get(mObj)
                        mModule = d_mObj['mModule']
                        
                        if mModule not in self.d_context['mModules']:
                            self.d_context['mModules'].append(mModule)
                            if context == 'part':
                                res.append(mModule)
                        
                        if mModule.getMessage('modulePuppet'):
                            mPuppet = mModule.modulePuppet
                            if mPuppet not in self.d_context['mPuppets']:
                                self.d_context['mPuppets'].append(mPuppet)
                                if context == 'puppet':
                                    res.append(mPuppet)
                    elif mObj.getMessage('puppet'):
                        mPuppet = mObj.puppet
                        if mPuppet not in self.d_context['mPuppets']:
                            self.d_context['mPuppets'].append(mPuppet)
                            self.d_context['b_puppetPart'] = True
                            if context in ['puppet','scene']:
                                res.append(mPuppet)
                            else:
                                res.append(mObj)"""
                            #elif context == 'control':
                            #res.append(mObj)
        
            #before we get mirrors we're going to buffer our main modules so that mirror calls don't get screwy
            self.d_context['mModulesBase'] = copy.copy(self.d_context['mModules'])
            ls=[]
            #pprint.pprint(res)
            #pprint.pprint(self.d_context)
            
            #process...
            log.debug(cgmGEN.logString_sub(_str_func,"Initial Process..."))
            
            if context == 'control' and b_siblings:
                if b_mirror or addMirrors:
                    log.warning("Context control + siblings = part mode")
                    context = 'part'
                    b_siblings = False            
            
            if b_siblings:
                log.debug(cgmGEN._str_subLine)        
                log.debug("|{0}| >> sibling check...".format(_str_func))
                if context == 'part':
                    log.debug(cgmGEN._str_hardBreak)
                    log.debug("|{0}| >> JOSH ... part siblings won't work right until you tag build profile for matching ".format(_str_func))
                    log.debug(cgmGEN._str_hardBreak)        
                    
                    res = []
                    for mModule in self.d_context['mModules']:
                        res.append(mModule)
                        log.debug("|{0}| >> sibling check: {1}".format(_str_func,mModule))
                        mSib = self.dat[mModule]['mSibling']
                        if mSib:res.append(mSib)
                    self.d_context['mModules'].extend(res)#...push new data back
                    
                elif context == 'control':
                    res = []
                    for mControl in self.d_context['mControls']:
                        log.debug("|{0}| >> sibling gathering for control | {1}".format(_str_func,mModule))
                        res.extend(self.dat[mModule]['mControls'])
                    self.d_context['mControls'] = res
                        
            if b_children:
                log.debug(cgmGEN._str_subLine)        
                log.debug("|{0}| >> Children check...".format(_str_func))
                
                if self.d_context['b_puppetPart']:
                    for mPuppet in self.d_context['mPuppets']:
                        self.d_context['mModules'].extend(self.dat[mPuppet]['mModules'])
                        """
                        for mModule in mPuppet.atUtils('modules_get'):
                            if mModule not in self.d_context['mModules']:
                                self.d_context['mModules'].append(mModule)"""            
        
                
                if context == 'part':
                    for mModule in self.d_context['mModules']:
                        log.debug("|{0}| >> child check: {1}".format(_str_func,mModule))
                        for mChild in self.dat[mModule]['mChildren']:
                            if mChild not in self.d_context['mModules']:
                                self.d_context['mModules'].append(mChild)                        

                
            if  b_mirror or addMirrors:
                log.debug(cgmGEN._str_subLine)        
                log.debug("|{0}| >> Context mirror check...".format(_str_func))
                if context == 'control':
                    ml_mirror = []
                    for mControl in self.d_context['mControls']:
                        mMirror = self.dat[mControl].get('mMirror')
                        if mMirror:
                            log.debug("|{0}| >> Found mirror for: {1}".format(_str_func,mControl))
                            ml_mirror.append(mMirror)
                            
                    if ml_mirror:
                        res.extend(ml_mirror)
                        self.d_context['mControls'].extend(ml_mirror)
                        self.d_context['mControlsMirror'].extend(ml_mirror)
                    
                elif context == 'part':
                    ml_mirrors =[]
                    for mModule in self.d_context['mModules']:
                        mMirror = self.dat[mModule]['mMirror']#mModule.atUtils('mirror_get')
                        if mMirror:
                            log.debug("|{0}| >> Mirror: {1}".format(_str_func,mMirror))
                            if mMirror not in self.d_context['mModules']:
                                #res.append(mMirror)
                                ml_mirrors.append(mMirror)
                    
                    for mModule in ml_mirrors:
                        if mModule not in self.d_context['mModules']:
                            self.d_context['mModules'].append(mModule)
                    self.d_context['mModulesMirror'] = ml_mirrors
                    
                
                

            if context in ['puppet','scene']:
                for mPuppet in self.d_context['mPuppets']:
                    for mModule in self.dat[mPuppet]['mModules']:#for mModule in mPuppet.atUtils('modules_get'):
                        if mModule not in self.d_context['mModules']:
                            self.d_context['mModules'].append(mModule)
            
            
            #pprint.pprint(self.d_context)
            self.d_context['res'] = res
            if _b_debug:
                log.debug(cgmGEN.logString_sub("first pass context..."))
                pprint.pprint(self.d_context)
                
            #Second pass ===================================================================
            log.debug(cgmGEN.logString_sub(_str_func,"Second Process..."))
            
            if context != 'control':
                log.debug("|{0}| >> Reaquiring control list...".format(_str_func))
                ls = []
                ml = []
                
                if self.d_context['b_puppetPart']:
                    log.info("|{0}| >> puppetPart mode...".format(_str_func))
                    for mPuppet in self.d_context['mPuppets']:
                        ml.extend(self.dat[mPuppet]['mPuppetControls'])
                        #ls.extend([mObj.mNode for mObj in mPuppet.UTILS.controls_get(mPuppet)])
                
                if context == 'part':
                    if mirrorQuery:
                        for mPart in self.d_context['mModules']:
                            ml.extend(self.dat[mPart]['mMirror']['mControls'])
                            #ls.extend([mObj.mNode for mObj in mPart.UTILS.controls_get(mPart,'mirror')])            
                    else:
                        for mPart in self.d_context['mModules']:
                            ml.extend(self.dat[mPart]['mControls'])
                            #ls.extend(mPart.rigNull.moduleSet.getList())
                            
                elif context in ['puppet','scene']:
                    for mPuppet in self.d_context['mPuppets']:
                        ml.extend(self.dat[mPuppet]['mControls'])
                        #_l = [mObj.mNode for mObj in mPuppet.UTILS.controls_get(mPuppet,walk=True)]
                        #ls.extend(_l)
                        #ls.extend(mPuppet.puppetSet.getList())
                        #mPuppet.puppetSet.select()
                        #ls.extend(mc.ls(sl=True))
                        
                self.d_context['mControls'] = ml
            
            self.d_context['mControls'] = LISTS.get_noDuplicates(self.d_context['mControls'])
            if _b_debug:
                log.debug(cgmGEN.logString_sub("second pass context..."))
                pprint.pprint(self.d_context)            
            return self.d_context['mControls']
        except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
        
    #@cgmGEN.Timer
    def contextTime_get(self,mirrorQuery=False,**kws):
        try:        
            _str_func='contextTime_get'
            log.debug(cgmGEN.logString_start(_str_func))
            _res = {}
            
            if not self.d_context:
                log.debug(cgmGEN.logString_sub(_str_func,'No context, acquiring...'))                
                self.context_get(mirrorQuery = mirrorQuery,**kws)
            
            self.d_timeContext['partControls'] = {}
            log.debug(cgmGEN.logString_sub(_str_func,'Get controls'))
            
            d_globalContext = get_contextDict(kws.get('contextPrefix',False))
            
            _context = kws.get('contextMode',d_globalContext['contextMode'])
            _contextTime = kws.get('contextTime',d_globalContext['contextTime']) 
            _contextKeys = kws.get('contextKeys',d_globalContext['contextKeys'])
            
            _frame = SEARCH.get_time('current')
            self.d_timeContext['frameInitial'] = _frame
            
            if _contextTime == 'selected':
                if not SEARCH.get_time('selected'):
                    return False,"Time Context: selected | No time selected."
                
            if _context in ['puppet','scene'] and _contextTime in ['bookEnd']:
                log.error("Unsupported context/time combo (bad mojo!) | context:{0} | contextTime:{1}".format(_context,_contextTime))
                return False,"Unsupported context/time combo (bad mojo!) | context:{0} | contextTime:{1}".format(_context,_contextTime)            
            
            log.debug("|{0}| >> context: {1} | {2} - {3} | {4}".format(_str_func,_context,_contextKeys,_contextTime, ' | '.join(kws)))
            
            #First gcather our controls
            _keys = kws.keys()
            
            context = _context
            b_children = kws.get('contextMirror',d_globalContext['contextMirror'])
            b_siblings =kws.get('contextSiblings',d_globalContext['contextSiblings'])
            b_mirror = kws.get('contextMirror',d_globalContext['contextMirror'])
            b_core = kws.get('contextCore',d_globalContext['contextCore'])

            if _context == 'control' and b_siblings:
                if b_mirror:
                    log.warning("Context control + siblings = part mode")
                    _context = 'part'
                    b_siblings = False
                    
            if _context == 'puppet' and b_siblings:
                log.warning("Context puppet + siblings = scene mode")
                _context = 'scene'

            def addSourceControls(self,mObj,controls):
                if not self.d_timeContext['partControls'].get(mObj):
                    log.debug("New partControl list: {0}".format(mObj))
                    self.d_timeContext['partControls'][mObj] = []
                
                _l = self.d_timeContext['partControls'][mObj]
                for c in controls:
                    if c not in _l:
                        #log.debug("New control: {0}".format(c))                    
                        _l.append(c)
                self.d_timeContext['partControls'][mObj] = _l            
                    
            
            if _context != 'control':
                log.debug("|{0}| >> Reaquiring control list...".format(_str_func))
                ls = []
    
                if self.d_context['b_puppetPart']:
                    log.info("|{0}| >> puppetPart mode...".format(_str_func))
                    for mPuppet in self.d_context['mPuppets']:
                        _ml = self.dat[mPuppet]['mPuppetControls']
                        _l = [mObj.mNode for mObj in _ml]
                        #_l = [mObj.mNode for mObj in mPuppet.UTILS.controls_get(mPuppet)]
                        ls.extend(_l)
                        addSourceControls(self,mPuppet,_l)
                
                if _context == 'part':
                    for mPart in self.d_context['mModules']:
                        log.debug("|{0}| >> part... {1}".format(_str_func,mPart))
                        d_mModule = self.module_get(mPart)
                        ml_add = d_mModule['mControls']
                        if b_core:
                            ml_core =  d_mModule.get('mCore')
                            if ml_core:
                                ml_add = ml_core
                        
                        _l = [mObj.mNode for mObj in ml_add]
                        #_l = [mObj.mNode for mObj in self.dat[mPart]['mControls']]
                        ls.extend(_l)
                        addSourceControls(self,mPart,_l)
                    
                    
                    if mirrorQuery:
                        for mPart in self.d_context['mModules']:
                            mMirror = self.dat[mPart]['mMirror']
                            if mMirror:
                                d_mModule = self.module_get(mMirror)
                                ml_add = d_mModule['mControls']
                                if b_core:
                                    ml_core =  d_mModule.get('mCore')
                                    if ml_core:
                                        ml_add = ml_core
                                        
                                    _l = [mObj.mNode for mObj in ml_add]
                                    ls.extend(_l)
                                    addSourceControls(self,mPart,_l)                                
                                """
                                _ml = self.dat[mMirror]['mControls']
                                _l = [mObj.mNode for mObj in _ml]
                                ls.extend(_l)
                                addSourceControls(self,mPart,_l)"""
     
                            
                elif _context in ['puppet','scene']:
                    """
                    if mirrorQuery:
                        for mPuppet in self.d_context['mPuppets']:
                            addSourceControls(self,mPuppet,
                                              [mObj.mNode for mObj in self.dat[mPuppet]['mPuppetControls']])
                            
                            for mPart in mPuppet.UTILS.modules_get(mPuppet):
                                _l = [mObj.mNode for mObj in mPart.UTILS.controls_get(mPart,'mirror')]
                                ls.extend(_l)
                                addSourceControls(self,mPart,_l)"""
                                
                    for mPuppet in self.d_context['mPuppets']:
                        d_ = self.puppet_get(mPuppet)
                        ml = []
                        if b_core:
                            ml.extend(d_['mCore'])
                        else:
                            ml.extend(d_['mControls'])                        
                        
                        _l =  [mObj.mNode for mObj in ml]
                        addSourceControls(self,mPuppet,_l)
                        ls.extend(_l)
                        """
                        for mPart in mPuppet.UTILS.modules_get(mPuppet):
                            #_l = [mObj.mNode for mObj in mPart.UTILS.controls_get(mPart)]
                            _l = mPart.rigNull.moduleSet.getList()
                            ls.extend(_l)
                            addSourceControls(self,mPart,_l)"""
                                
                            #mPuppet.puppetSet.select()
                            #ls.extend(mc.ls(sl=True))
                        
                self.d_timeContext['sControls'] = ls
            else:
                self.d_timeContext['sControls'] = [mObj.mNode for mObj in self.d_context['mControls']]
                self.d_timeContext['mControls'] = self.d_context['mControls']
                
                self.d_timeContext['partControls']['control'] = self.d_timeContext['sControls']
     
            self.d_timeContext['sControls'] = LISTS.get_noDuplicates(self.d_timeContext['sControls'])
            #self.d_timeContext['mControls'] = cgmMeta.validateObjListArg(self.d_timeContext['sControls'])
            
            #pprint.pprint(self.d_timeContext)
            #return
            #================================================================================================
            log.debug(cgmGEN.logString_sub(_str_func,'Find keys'))
            self.l_sources = []
            
            def addSource(self,mObj,key,res):
                if not _res.get(key):
                    log.debug("New frame: {0}".format(key))                
                    res[key]=[]
                
                _l = res[key]
                if mObj not in _l:
                    _l.append(mObj)
                if mObj not in self.l_sources:
                    self.l_sources.append(mObj)
                    
                res[key] = _l
                
            if _contextTime == 'current':
                _controls = self.d_timeContext['sControls']
                _res[_frame] = _controls
            else:
                if _context == 'control':
                    for mObj in self.d_timeContext['mControls']:
                        _keys = SEARCH.get_key_indices_from( mObj.mNode,mode = _contextTime)
                        if _keys:
                            log.debug("{0} | {1}".format(mObj.p_nameShort,_keys))
                            for k in _keys:
                                addSource(self,mObj,k,_res)
                elif _context in ['part','puppet','scene']:
                    d_tmp = {}
                    l_keys = []
                    #First pass we collect all the keys...
                    for mPart,controls in self.d_timeContext['partControls'].iteritems():
                        d_tmp[mPart] = []
                        _l = d_tmp[mPart]
                        for c in controls:
                            _keys = SEARCH.get_key_indices_from( c,mode = _contextTime)
                            if _keys:
                                log.debug("{0} | {1}".format(c,_keys))
                                for k in _keys:
                                    #addSource(self,mPart,k,_res)
                                    if k not in d_tmp[mPart]:d_tmp[mPart].append(k)
                                    if k not in l_keys:l_keys.append(k)
                    #Second pass we do any special processing in case a given set of controls gives us more data that we want...                
                    if _context in ['part']:
                        if _contextTime in ['next','previous']:
                            log.debug(cgmGEN.logString_sub(_str_func,'Second pass | {0}'.format(_contextTime)))                        
                            for mPart,keys in d_tmp.iteritems():
                                if not keys:
                                    continue
                                if _contextTime== 'next':
                                    _match = MATH.find_valueInList(_frame,keys,'next')
                                else:
                                    _match = MATH.find_valueInList(_frame,keys,'previous')
                                d_tmp[mPart] = [_match]
                    elif _context == 'puppet':
                        if _contextTime in ['next','previous']:
                            log.debug(cgmGEN.logString_sub(_str_func,'Second pass | {0}'.format(_contextTime)))
                            if _contextTime== 'next':
                                _match = MATH.find_valueInList(_frame,l_keys,'next')
                            else:
                                _match = MATH.find_valueInList(_frame,l_keys,'previous')                        
                            
                            for mPart,keys in d_tmp.iteritems():
                                d_tmp[mPart] = [_match]                    
                        
                    
                    for mPart,keys in d_tmp.iteritems():
                        for k in keys:
                            addSource(self,mPart,k,_res)
                            
                    
                                    
                                    
            #We have to cull some data in some cases....
            if _contextTime not in ['all']:
                if _contextTime in ['next','previous'] and _context !='control' and 'cat'=='dog':
                    #We only want one value here...
                    if _contextTime== 'next':
                        _match = MATH.find_valueInList(_frame,_res.keys(),'next')
                    else:
                        _match = MATH.find_valueInList(_frame,_res.keys(),'previous')
                    
                    for k in _res.keys():
                        if k != _match:
                            _res.pop(k)
                else:
                    _range = SEARCH.get_time('slider')
                    for k in _res.keys():
                        if k < _range[0] or k > _range[1]:
                            log.debug("Out of range: {0}".format(k))
                            _res.pop(k)
    
            if _contextKeys == 'combined':
                log.debug(cgmGEN.logString_sub(_str_func,'Combining keys'))
                
                if _context == 'control':
                    for k in _res.keys():
                        _res[k]= self.l_sources                
                else:
                    mSources = self.d_timeContext['partControls'].keys()
                    for k in _res.keys():
                        _res[k]= mSources
                
                if _contextTime in ['next','previous']:
                    log.debug(cgmGEN.logString_sub(_str_func,'Combined final cull | {0}'.format(_contextTime)))
                    if _contextTime== 'next':
                        _match = MATH.find_valueInList(_frame,_res.keys(),'next')
                    else:
                        _match = MATH.find_valueInList(_frame,_res.keys(),'previous')
                    
                    for k in _res.keys():
                        if k != _match:
                            _res.pop(k)                
            
            #if _b_debug:
                #pprint.pprint(_res)
                
            self.d_timeContext['res'] = _res
                
            return _res
        except Exception,err:
            pprint.pprint(self.d_timeContext)
            cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

    #@cgmGEN.Timer
    def snapShot_get(self,key=None):
        _str_func='get_contextTimeDat'
        log.debug(cgmGEN.logString_start(_str_func))
        if not self.d_timeContext:
            return log.error("Time context needed")
        
        _res = {}
        if key is None:
            key = self.d_timeContext['frameInitial']
            
        for mPart,controls in self.d_timeContext['partControls'].iteritems():
            _d = {}
            for c in controls:
                _d_c = {}
                for a in mc.listAttr(c, keyable=True, unlocked=True):
                    _d_c[a] = ATTR.get(c,a)
                    
                _d[c] = _d_c

            _res[mPart] = _d
            
        pprint.pprint(_res)
        self.d_timeSnips[key] = _res
        
    def snapShot_set(self,key=None):
        _str_func='get_contextTimeDat'
        log.debug(cgmGEN.logString_start(_str_func))
        if not self.d_timeContext:
            return log.error("Time context needed")
        _res = {}
        if key is None:
            key = self.d_timeContext['frameInitial']
            
        dat = self.d_timeSnips.get(key)
        if not dat:
            return log.error("Key empty: {0}".format(key))
            
            
        for mPart,controls in self.d_timeContext['partControls'].iteritems():
            log.debug(cgmGEN.logString_sub(_str_func,'mPart: {0}'.format(mPart)))
            _dat = dat[mPart]
            for c in controls:
                _d_c = _dat[c]
                for a,v in _d_c.iteritems():
                    ATTR.set(c,a,v)
                    
    #@cgmGEN.Timer
    def mirrorData(self,mode=''):
        ml_nodes = self.d_context['mControls']
        if not ml_nodes:
            raise ValueError,"Must have controls in context"
        
        l_strings = self.d_context.get('sControls')
        if not l_strings:
            l_strings = [mObj.mNode for mObj in ml_nodes]
            self.d_context['sControls']=l_strings
            
        r9Anim.MirrorHierarchy().mirrorData(l_strings,mode = mode)
        
    #@cgmGEN.Timer
    def key(self,):
        ml_nodes = self.d_context['mControls']
        if not ml_nodes:
            raise ValueError,"Must have controls in context"
        
        l_strings = self.d_context.get('sControls')
        if not l_strings:
            l_strings = [mObj.mNode for mObj in ml_nodes]
            self.d_context['sControls']=l_strings
            
        for o in l_strings:#self.mDat.d_context['sControls']:
            mc.setKeyframe(o)        
        
        
        
def _uiCB_getPoseInputNodes(self,**kws):
    '''
    Node passed into the __PoseCalls in the UI
    '''
    _dat = {
        'contextMode' : kws.get('context') or self.var_mrsContext_mode.value,
        'contextChildren' : kws.get('children') or self.var_mrsContext_children.value,
        'contextSiblings' : kws.get('siblings') or self.var_mrsContext_siblings.value,
        'contextMirror' : kws.get('mirror') or self.var_mrsContext_mirror.value,
        'contextCore' : kws.get('core') or self.var_mrsContext_core.value,        
    }
    #_contextSettings = MRSANIMUTILS.get_contextDict(self.__class__.TOOLNAME)
    print len(mc.ls(sl=1))
    #pprint.pprint(_dat)
    _ml_controls = self.mDat.context_get(**_dat)
    #pprint.pprint(_ml_controls)
    log.info("Controls: {0}".format(len(_ml_controls)))        
    # posenodes = []
    #_sel = mc.ls(sl=1)
    #pprint.pprint(_sel)        
    return [mObj.mNode for mObj in _ml_controls]
        
#@cgmGEN.Timer
def get_buffer_dat(update = False):
    """
    Data gather for available blocks.

    :parameters:

    :returns
        _d_modules, _d_categories, _l_unbuildable
        _d_modules(dict) - keys to modules
        _d_categories(dict) - categories to list of entries
        _l_unbuildable(list) - list of unbuildable modules
    """
    _str_func = 'get_modules_dict'    

    
    try:
        _progressBar = CGMUI.doStartMayaProgressBar()
        
        _res = {}
        _b_debug = log.isEnabledFor(logging.DEBUG)
        
        log.debug(cgmGEN.logString_start(_str_func,'Puppets'))
        ml_puppets = r9Meta.getMetaNodes(mTypes = 'cgmRigPuppet',nTypes=['network'])
        
        _res['mPuppets'] = ml_puppets
        _res['mModules'] = []
        _res['mControls'] = []
        
        log.debug(cgmGEN.logString_msg(_str_func,'Puppets: '))
        len_puppets = len(ml_puppets)
        for i,mPuppet in enumerate(ml_puppets):
            log.debug("{0} | {1}".format(i,mPuppet))
            _res[mPuppet] = {}
            _p = _res[mPuppet]
            ml_modules = mPuppet.UTILS.modules_get(mPuppet)
            _p['mModules'] = ml_modules
            _p['mChildren'] = []
            _p['mControls'] = []
            _p['sControls'] = []
            _p['mPuppetControls'] = mPuppet.UTILS.controls_get(mPuppet)
            _p['mControls'].extend(_p['mPuppetControls'])
            
            len_modules = len(ml_modules)
            for ii,mModule in enumerate(ml_modules):
                _str = "{0} | {1}".format(ii,mModule)
                log.debug(cgmGEN.logString_start(_str))
                
                if _progressBar:
                    CGMUI.progressBar_set(_progressBar,step=1,
                                          maxValue = len_modules,
                                          status = _str)
                _res[mModule] = {}
                _m = _res[mModule]
                
                if mModule not in _p['mChildren']:
                    _p['mChildren'].append(mModule)                
                
                if mModule not in _res['mModules']:
                    _res['mModules'].append(mModule)
                    
                #Mirror...
                _m['mMirror'] = mModule.UTILS.mirror_get(mModule)
    
                
                #Children...
                ml_children = mModule.UTILS.moduleChildren_get(mModule)
                _m['mChildren'] = ml_children
                log.debug(cgmGEN.logString_msg('children'))                
                for iii,mObj in enumerate(ml_children):
                    if mObj not in _p['mChildren']:
                        _p['mChildren'].append(mObj)                
                    log.debug("{0} | {1}".format(iii,mObj))
                log.debug(cgmGEN._str_subLine)
                
                #Controls...
                ml_controls = mModule.rigNull.moduleSet.getMetaList()
                _m['mControls'] = ml_controls
                #l_controls = []
                #if ml_controls:
                    #for mObj in ml_controls:
                        #l_controls.append(mObj.mNode)
                #_m['sControls'] = l_controls
                
                len_controls = len(ml_controls)
                log.debug(cgmGEN.logString_msg('controls'))                
                for iii,mObj in enumerate(ml_controls):
                    _str = "{0} | {1}".format(iii,mObj)
                    log.debug(_str)
                    if _progressBar:
                        CGMUI.progressBar_set(_progressBar,step=1,
                                              maxValue = len_controls,
                                              status = _str)
                    
                    
                    try:_res['mControls'].index(mObj)
                    except:_res['mControls'].append(mObj)

                    #if mObj not in _res['mControls']:
                        #_res['mControls'].append(mObj)
                        
                    try:_p['mControls'].index(mObj)
                    except: _p['mControls'].append(mObj)
                    #if mObj not in _p['mControls']:
                        #_p['mControls'].append(mObj)
                        #_p['sControls'].append(mObj.mNode)
                        
                    _res[mObj] = {}
                    _res[mObj]['mMirror'] = mObj.getMessageAsMeta('mirrorControl')
                    _res[mObj]['mPuppet'] = mPuppet
                    _res[mObj]['mModule'] = mModule
                    
                log.debug(cgmGEN._str_subLine)            
                
                #Siblings...
                ml_siblings = mModule.UTILS.siblings_get(mModule) or []
                _m['mSiblings'] = ml_siblings
                if _b_debug:
                    log.debug(cgmGEN.logString_msg('siblings'))                
                    for iii,mObj in enumerate(ml_siblings):
                        log.debug("{0} | {1}".format(iii,mObj))
                    log.debug(cgmGEN._str_subLine)
                    

        #pprint.pprint(_res)
        CGM_MRSANIMATE_DAT = _res
        return _res
    except Exception,err:
        log.error(err)
    finally:
        CGMUI.doEndMayaProgressBar()


global MRSDAT
MRSDAT = dat(update=True)



#UI List ================================================================================

        
