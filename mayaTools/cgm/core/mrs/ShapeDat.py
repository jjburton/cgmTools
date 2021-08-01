"""
SHAPEDAT
Josh Burton 
www.cgmonks.com


"""
__MAYALOCAL = 'SHAPEDAT'


# From Python =============================================================
import copy
import os
import pprint
import getpass
import json

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

#import maya.OpenMaya as OM
#import maya.OpenMayaAnim as OMA

# From Red9 =============================================================
#from Red9.core import Red9_Meta as r9Meta
#import Red9.core.Red9_CoreUtils as r9Core

#import Red9.packages.configobj as configobj
#import Red9.startup.setup as r9Setup    

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.lib import position_utils as POS
from cgm.core.classes import GuiFactory as CGMUI
mUI = CGMUI.mUI
from cgm.core.lib import shared_data as SHARED
from cgm.core.mrs.lib import general_utils as BLOCKGEN

#reload(cgmUI)
#import cgm.core.cgmPy.path_Utils as PATHS
#import cgm.core.lib.path_utils as COREPATHS
#reload(COREPATHS)
#import cgm.core.lib.math_utils as COREMATH
#import cgm.core.lib.string_utils as CORESTRINGS
#import cgm.core.lib.shared_data as CORESHARE
import cgm.core.lib.rigging_utils as CORERIG

#import cgm.core.tools.lib.project_utils as PU
#import cgm.core.lib.mayaSettings_utils as MAYASET
#import cgm.core.mrs.lib.scene_utils as SCENEUTILS
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.locator_utils as LOC
#from cgm.core.mrs.lib import general_utils as BLOCKGEN
from cgm.core.lib import math_utils as MATH
#from cgm.core.lib import transform_utils as TRANS
from cgm.core.lib import distance_utils as DIST

log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start

__version__ = cgmGEN.__RELEASE
__toolname__ ='ShapeDat'
_padding = 5

d_shapeDat_options = {"form":['formHandles'],
                      "loft":['loftHandles','loftShapes'],
                     }
d_shapeDatShort = {'formHandles':'handles',
                   "loftHandles":'handles',
                   'loftShapes':'shapes'}
d_shapeDatLabels = {'formHandles':{'ann':"Setup expected qss sets", 'label':'form'},
                    'loftHandles':{'ann':"Wire for mirroring", 'label':'loft'},
                    'loftShapes':{'ann':"Connect bind joints to rig joints", 'label':'shapes'},}
         
class ui(CGMUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = "{}UI".format(__toolname__)
    WINDOW_TITLE = 'ShapeDat | {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 200,300
    
    def insert_init(self,*args,**kws):
        self._loadedFile = ""
        self.dat = None
        
    def build_menus(self):
        self.uiMenu_FileMenu = mUI.MelMenu(l='File', pmc = cgmGEN.Callback(self.buildMenu_file))
        self.uiMenu_SetupMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_setup))

    def buildMenu_file(self):
        self.uiMenu_FileMenu.clear()                      

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_save_actions,self)))

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save As",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_save_as_actions,self)))
        
        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Load",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_load_actions,self)))
    def buildMenu_setup(self):pass
    
    
    def uiStatus_refresh(self):
        _str_func = 'uiStatus_refresh[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        if not self.dat:
            self.uiStatus_top(edit=True,bgc = SHARED._d_gui_state_colors.get('warning'),label = 'No Data')
            #self.uiStatus_bottom(edit=True,bgc = SHARED._d_gui_state_colors.get('warning'),label = 'No Data')
            
            self.uiData_base(edit=True,vis=0)
            self.uiData_base.clear()
            
        else:
            self.uiData_base.clear()
            
            _base = self.dat['base']
            _str = "Source: {}".format(_base['source'])
            self.uiStatus_top(edit=True,bgc = SHARED._d_gui_state_colors.get('connected'),label = _str)
            
            self.uiData_base(edit=True,vis=True)
            
            mUI.MelLabel(self.uiData_base, label = "Base", h = 13, 
                         ut='cgmUIHeaderTemplate',align = 'center')
            
            for a in ['type','blockType','shapers','subs']:
                mUI.MelLabel(self.uiData_base, label = "{} : {}".format(a,self.dat['base'].get(a)),
                             bgc = SHARED._d_gui_state_colors.get('help'))                
            
            
            #_str = "blockType: {}".format(_base.get('blockType','No blockType'))
            #self.uiStatus_bottom(edit=True,bgc = SHARED._d_gui_state_colors.get('connected'),label = _str)            
                
    def uiFunc_dat_get(self):
        _str_func = 'uiFunc_dat_get[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        _sel = mc.ls(sl=1)
        
        mBlock = BLOCKGEN.block_getFromSelected()
        if not mBlock:
            return log.error("No blocks selected")
        
        sDat = dat_get(mBlock)
        self.dat = sDat
        
        self.uiStatus_refresh()
        if _sel:mc.select(_sel)
        
    def uiFunc_dat_set(self,mBlocks = None,**kws):
        _str_func = 'uiFunc_dat_set[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))        
        
        if not mBlocks:
            mBlocks = BLOCKGEN.block_getFromSelected(multi=True)
            
        if not mBlocks:
            return log.error("No blocks selected")
        
        if not self.dat:
            return log.error("No dat loaded")
            
        
        if not kws:
            kws = {}
            for k,cb in self._dCB_reg.iteritems():
                kws[k] = cb.getValue()
            
            pprint.pprint(kws)
        
        
        
        mc.undoInfo(openChunk=True)

        
        for mBlock in mBlocks:
            log.info(log_sub(_str_func,mBlock.mNode))
            try:dat_set(mBlock, self.dat, **kws)
            except Exception,err:
                log.error("{} | err: {}".format(mBlock.mNode, err))
                    
        mc.undoInfo(closeChunk=True)
        
        return
        for d in ['form','loft']:
            l = d_shapeDat_options[d]
            mUI.MelLabel(_inside, label = '{0}'.format(d.upper()), h = 13, 
                         ut='cgmUIHeaderTemplate',align = 'center')
            for k in l:
                d_dat = d_shapeDatLabels.get(k,{})
                
        for d,l in MRSBATCH.d_mrsPost_calls.iteritems():
            for k in l:# _l_post_order:
                log.debug("|{0}| >> {1}...".format(_str_func,k)+'-'*20)
                
                #self._dCB_reg[k].getValue():#self.__dict__['cgmVar_mrsPostProcess_{0}'.format(k)].getValue():
                l_join.insert(2,"'{0}' : {1} ,".format(k,int(self._dCB_reg[k].getValue())))        
        
    
    def uiFunc_dat(self,mode='Select Source'):
        _str_func = 'uiFunc_print[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))  
        
        if not self.dat:
            return log.error("No dat loaded selected")
        
        if mode == 'Select Source':
            mc.select(self.dat['base']['source'])
    
    def uiFunc_printDat(self,mode='all'):
        _str_func = 'uiFunc_print[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))  
        
        if not self.dat:
            return log.error("No dat loaded selected")    
        
        sDat = self.dat
        
        print(log_sub(_str_func,mode))
        if mode == 'all':
            pprint.pprint(self.dat)
        elif mode == 'settings':
            pprint.pprint(sDat['settings'])
        elif mode == 'base':
            pprint.pprint(sDat['base'])
        elif mode == 'settings':
            pprint.pprint(sDat['settings'])
        elif mode == 'formHandles':
            pprint.pprint(sDat['handles']['form'])        
        elif mode == 'loftHandles':
            pprint.pprint(sDat['handles']['loft'])  
        elif mode == 'sub':
            pprint.pprint(sDat['handles']['sub'])
        elif mode == 'subShapes':
            pprint.pprint(sDat['handles']['subShapes'])
        elif mode == 'subRelative':
            pprint.pprint(sDat['handles']['subRelative'])            
            
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        #Declare form frames...------------------------------------------------------
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        _inside = mUI.MelScrollLayout(_MainForm)

        #SetHeader = cgmUI.add_Header('{0}'.format(_strBlock))
        self.uiStatus_top = mUI.MelButton(_inside,
                                         vis=True,
                                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_get)),
                                         bgc = SHARED._d_gui_state_colors.get('warning'),
                                         label = 'No Data',
                                         h=20)                
        
        
        
        #mc.setParent(_MainForm)
        """
        self.uiStatus_bottom = mUI.MelButton(_MainForm,
                                             bgc=SHARED._d_gui_state_colors.get('warning'),
                                             #c=lambda *a:self.uiFunc_updateStatus(),
                                             ann="...",
                                             label='...',
                                             h=20)"""
  
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)

        
    
        
        
                
        #checkboxes frame...------------------------------------------------------------
        self._dCB_reg = {}
        for d in ['form','loft']:
            l = d_shapeDat_options[d]
            mUI.MelLabel(_inside, label = '{0}'.format(d.upper()), h = 13, 
                         ut='cgmUIHeaderTemplate',align = 'center')
            #mc.setParent(_inside)
            #cgmUI.add_Header(d)
            for k in l:
                d_dat = d_shapeDatLabels.get(k,{})
                
                _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
                mUI.MelSpacer(_row,w=10)    
                
                mUI.MelLabel(_row, label = '{0}:'.format( d_dat.get('label',k) ))
                _row.setStretchWidget(mUI.MelSeparator(_row))
    
                _plug = 'cgmVar_shapeDat_' + k#d_shapeDatShort.get(k,k)
                try:self.__dict__[_plug]
                except:
                    log.debug("{0}:{1}".format(_plug,1))
                    self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = 1)
        
                l = k
                _buffer = k#d_shapeDatShort.get(k)
                if _buffer:l = _buffer
                _cb = mUI.MelCheckBox(_row,
                                      #annotation = d_dat.get('ann',k),
                                      value = self.__dict__[_plug].value,
                                      onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                                      offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
                self._dCB_reg[k] = _cb
                mUI.MelSpacer(_row,w=10)    
                
                _row.layout()

        
        
        _button = mc.button(parent=_inside,
                            l = 'Load',
                            ut = 'cgmUITemplate',
                            c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_set)),
                            ann = 'Build with MRS')        
        
        #data frame...------------------------------------------------------
        try:self.var_shapeDat_dataFrameCollapse
        except:self.create_guiOptionVar('shapeDat_dataFrameCollapse',defaultValue = 0)
        mVar_frame = self.var_shapeDat_dataFrameCollapse
        
        _frame = mUI.MelFrameLayout(_inside,label = 'Data',vis=True,
                                    collapse=mVar_frame.value,
                                    collapsable=True,
                                    enable=True,
                                    #ann='Contextual MRS functionality',
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:mVar_frame.setValue(0),
                                    collapseCommand = lambda:mVar_frame.setValue(1)
                                    )	
        self.uiFrame_data = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
        
        
        self.uiData_base = mUI.MelColumn(self.uiFrame_data ,useTemplate = 'cgmUISubTemplate',vis=False) 

        mUI.MelLabel(self.uiFrame_data, label = "Select", h = 13, 
                     ut='cgmUIHeaderTemplate',align = 'center')
        
        for util in ['Select Source']:
            mUI.MelButton(self.uiFrame_data,
                          c = cgmGEN.Callback(self.uiFunc_dat,util),
                          ann="...",
                          label=util,
                          ut='cgmUITemplate',
                          h=20)                            
        
        
        
        
        mUI.MelLabel(self.uiFrame_data, label = "PPRINT", h = 13, 
                     ut='cgmUIHeaderTemplate',align = 'center')
        
        for a in ['settings','base','formHandles','loftHandles','sub','subShapes','subRelative','all']:
            mUI.MelButton(self.uiFrame_data,
                          c = cgmGEN.Callback(self.uiFunc_printDat,a),
                          ann="...",
                          label=a,
                          ut='cgmUITemplate',
                          h=20)                    
        

        _row_cgm = CGMUI.add_cgmFooter(_MainForm)            

        #Form Layout--------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_inside,"top",0),
                        (_inside,"left",0),
                        (_inside,"right",0),
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(_inside,"bottom",0,_row_cgm),
                        #(_button,"bottom",0,_row_cgm),
                        #(self.uiPB_test,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])    
    

        self.uiFunc_dat_get()
        
       
   





class data(object):
    '''
    Class to handle blockShape data.
    '''    
    
    def __init__(self, mBlock = None, filepath = None, **kws):
        """

        """
        _str_func = 'data.__buffer__'
        log.debug(log_start(_str_func))
        
        self.str_filepath = None
        self.data = {}
        self.mBlock = None
        
        
    def get(self, mBlock = None):
        _str_func = 'data.get'
        log.debug(log_start(_str_func))
    
    
    def set(self, mBlock = None):
        _str_func = 'data.set'
        log.debug(log_start(_str_func))
        
        


def dat_set(mBlock,data,
            settings = True,
            formHandles = True,
            loftHandles = True,
            loftShapes=True,
            loftHandleMode = 'world',
            shapeMode = 'ws',
            loops=2):
    _str_func = 'dat_get'
    log.debug(log_start(_str_func))
    
    _str_block = mBlock.mNode
    ml_handles = None
    
    #Logic checks....
    b_dataAddLever = False
    b_targetAddLever = False
    l_skips = []
    _dataForward = 0
    _dataSkip = 0
    
    if data['base'].get('addLeverBase') not in ['none']:
        print("data has addLeverBase")
        b_dataAddLever = True
    else:
        print("data has no addLeverBase")
        
    if mBlock.hasAttr('addLeverBase') and mBlock.addLeverBase:
        print("mBlock has addLeverBase")
        b_targetAddLever = True        
    else:
        print("mBlock has no addLeverBase")
        
    if not b_targetAddLever and b_dataAddLever:
        print("Target doesn't, data does. dataSkip 1 [0]")
        _dataSkip = 1
            
    if  b_targetAddLever and not b_dataAddLever:
        print("Target does, data doesn't. Pull data forward")
        _dataForward = -1
        if 0 not in l_skips:
            l_skips.append(0)        
        
    
    #First part of block reset to get/load data------------------------------------------------------
    pos = mBlock.p_position
    orient = mBlock.p_orient
    scale = mBlock.blockScale
    
    mBlock.p_position = 0,0,0
    mBlock.p_orient = 0,0,0
    mBlock.blockScale = 1.0

    def get_loftShapes(ml_handles):
        _res = {}
        
        for i,mObj in enumerate(ml_handles):
            _res[i] = {'mLoft': mObj.getMessageAsMeta('loftCurve'),
                       'mSubShapers':mObj.msgList_get('subShapers'),
                       }

    
        return _res
        
    def get_handles(ml_handles):
        if ml_handles:
            log.info("Found...")
            return ml_handles
        
        ml_handles = mBlock.msgList_get('formHandles')
        return ml_handles
    
    if settings:
        log.info(log_sub(_str_func,'Settings...'))
        
        for a,v in data['settings'].iteritems():
            
            if a in l_enumLists:
                ATTR.datList_connect(_str_block,a,v,enum=1)
            elif a in l_datLists:
                ATTR.datList_connect(_str_block,a,v)
            else:
                ATTR.set(_str_block, a, v)
            

        if mBlock.blockState < 1:
            mBlock.p_blockState = 1
            
        
        
    #Form Handles and shapes -----------------------------------------------------------    
    if formHandles: 
        log.info(log_sub(_str_func,'FormHandles...'))
        ml_handles = get_handles(ml_handles)
        
        if mBlock in ml_handles:
            raise ValueError,"mBlock cannot be in handles"
        
        pprint.pprint(ml_handles)
        
        dat_form = data['handles']['form']

            
        for ii in range(len(ml_handles)+1):#...since the end affects the mids we need to lop through
            for i, mObj in enumerate(ml_handles):
                if i in l_skips:
                    continue
                
                if _dataForward:
                    i = i-1
                if _dataSkip:
                    i = i+1
                    
                print i
                #mObj.translate = dat_form[i]['trans']
                #mObj.rotate = dat_form[i]['rot']
                mObj.p_position = dat_form[i]['pos']
                mObj.p_orient = dat_form[i]['orient']
                
                mObj.scaleX = dat_form[i]['scale'][0]
                mObj.scaleY = dat_form[i]['scale'][1]
                try:mObj.scaleZ = dat_form[i]['scale'][2]
                except:pass

    
    #loft handles and shapes -----------------------------------------------------------
    if loftHandles or loftShapes:
        log.info(log_sub(_str_func,'loftHandles...'))
        if not ml_handles:
            ml_handles = get_handles(ml_handles)
            
            
            
        dat_loft = data['handles']['loft']
        dat_shapes = data['handles']['loftShapes']
        
        dat_sub = data['handles']['sub']
        dat_subShapes = data['handles']['subShapes']
        dat_subRel = data['handles']['subRelative']
        

        md_loftShapes = get_loftShapes(ml_handles)
        
        
        for i,mObj in enumerate(ml_handles):
            if i in l_skips:
                continue
            
                    
            _mLoft = md_loftShapes[i].get('mLoft')
            _mSubShapers = md_loftShapes[i].get('mSubShapers',[])
            
            
            if _dataForward:
                i = i-1
            if _dataSkip:
                i = i+1
                
            if _mLoft:
                if loftHandles:
                    for iii in range(loops):
                        if loftHandleMode == 'local':
                            _mLoft.translate = dat_loft[i]['trans']
                            _mLoft.rotate = dat_loft[i]['rot']                        
                        else:
                            _mLoft.p_position = dat_loft[i]['pos']
                            _mLoft.p_orient = dat_loft[i]['orient']       
                            
                        _mLoft.scale = dat_loft[i]['scale']
                            
                    #mObj.p_position = dat_loft[i]['pos']
                    
                if loftShapes:
                    log.info(log_sub(_str_func,'loft loftShape {}...'.format(i)))
                    #for iii in range(loops):
                    shapes_set(_mLoft, dat_shapes[i],shapeMode)                    
            
            
            if _mSubShapers:
                if loftHandles:
                    _datLast = None
                    for iii in range(loops):
                        for ii,mObj in enumerate(_mSubShapers):
                            if loftHandles:
                                try:
                                    _datTmp = dat_sub[i][ii]
                                    _datLast = _datTmp
                                except:
                                    log.warning("Missing sub dat: {} | using last".format(ii))
                                    _datTmp = _datLast
                                    
                                try:
                                    if loftHandleMode == 'local':
                                        mObj.translate = _datTmp['trans']
                                        mObj.rotate = _datTmp['rot']                        
                                    else:
                                        mObj.p_position = _datTmp['pos']
                                        mObj.p_orient = _datTmp['orient']                    
                                        
                                    #mObj.p_position = _datTmp['pos']
                                    mObj.scale = _datTmp['scale']
                                except Exception, err:
                                    pprint.pprint(_datTmp)
                                    log.error("loft handle loop: {} | i: {} | ii:{} | err: {}".format(iii,i,ii,err))
                        
                        
                        #Relative set
                        try:
                            relativePointDat_setFromObjs([mObj.mNode for mObj in _mSubShapers],
                                                         ml_handles[i].mNode,
                                                         ml_handles[i+1].mNode,
                                                         dat_subRel[i] ) 
                        except Exception,err:
                            log.error("loft handle loop: {} | i: {} | ii:{} | err: {}".format(iii,i,ii,err))
                            
                    

                if loftShapes:
                    log.info(log_sub(_str_func,'sub loftShapes...'))
                    for iii in range(loops):
                        for ii,mObj in enumerate(_mSubShapers):
                            try:
                                shapes_set(mObj, dat_subShapes[i][ii],shapeMode)
                            except Exception, err:
                                log.error("loft shape loop: {} | i: {} | ii:{} | err: {}".format(iii,i,ii,err))
    #if loftShapes:
    #    log.info(log_sub(_str_func,'loftShapes...'))
        
    #Restore our block...-----------------------------------------------------------------
    mBlock.p_position = pos
    mBlock.p_orient = orient         
    mBlock.blockScale = scale         
            
l_dataAttrs = ['blockType','addLeverBase', 'addLeverEnd','cgmName']
l_enumLists = ['loftList']
l_datLists = ['numSubShapers']

def dat_get(mBlock=None):
    _str_func = 'dat_get'
    log.debug(log_start(_str_func))
    
    _str_block = mBlock.mNode
    
    #Check state. must be form state
    if mBlock.blockState < 1:
        raise ValueError,"Must be in form state"
    
    _type = mBlock.blockType
    _supported = ['limb','segment','handle']
    if _type not in _supported:
        raise TypeError,"{} type not supported. | Supported: {}".format(_type,_supported)
    
    #First part of block reset to get/load data------------------------------------------------------
    pos = mBlock.p_position
    orient = mBlock.p_orient
    
    mBlock.p_position = 0,0,0
    mBlock.p_orient = 0,0,0

    
    def get_attr(obj,a,d = {}):
        try:
            if a in l_enumLists:
                if ATTR.datList_exists(_str_block,a):
                    _d[a] = ATTR.datList_get(_str_block,a,enum=1)
            elif a in l_datLists:
                if ATTR.datList_exists(_str_block,a):
                    _d[a] = ATTR.datList_get(_str_block,a)                
            elif ATTR.get_type(obj, a) == 'enum':
                d[a] = ATTR.get_enumValueString(_str_block, a)
            else:
                d[a] = ATTR.get(_str_block, a)
        except:pass        
    
    #Form count
    _res = {}
    
    #Settings ... ---------------------------------------------------------------------------
    _d = {}
    _res['settings'] = _d
    
    for a in ['loftSetup','loftShape','numShapers','numSubShapers','shapersAim','shapeDirection','loftList']:
        get_attr(_str_block,a,_d)
    
            
    #Dat ... ---------------------------------------------------------------------------
    _d = {}
    _res['base'] = _d
    
    for a in l_dataAttrs:
        get_attr(_str_block,a,_d)
    
    _d['source']= mBlock.p_nameBase
    _d['type'] = _d.pop('cgmName','none')
            
    #FormHandles ... ---------------------------------------------------------------------------
    _d = {}
    _d['form'] = []
    _d['loft'] = []
    _d['loftShapes'] = []
    
    _d['sub'] = []
    _d['subShapes'] = []    
    _d['subRelative'] = []    
    
    _res['handles'] = _d
    
    ml_handles = mBlock.msgList_get('formHandles')
    #pprint.pprint(ml_handles)
    
    _res['base']['shapers'] = len(ml_handles)
    _res['base']['subs'] = []
    _num_subs = _res['base']['subs']
    
    
    def getCVS(mObj):
        _obj = mObj.mNode
        _res = {}
        
        _l_shapes_source = mc.listRelatives(_obj,shapes=True,fullPath=True)

        for i,s in enumerate(_l_shapes_source):
            _l_ep_source = mc.ls("{0}.cv[*]".format(s),flatten = True)
            for i,ep in enumerate(_l_ep_source):
                _pos = POS.get(ep,space='os')
            
    def get(mObj):
        d = {'pos':mObj.p_position,
             'orient':mObj.p_orient,
             'rot':mObj.rotate,
             'trans':mObj.translate,
             'scale':mObj.scale}
        return d
    
    for i, mObj in enumerate(ml_handles):
        _d['form'].append( get(mObj))
        _l_shapes = []
        _l_loft = []
        
        mLoftCurve = mObj.getMessageAsMeta('loftCurve')
        
        ml_loft = []
        
        #LoftCurve.....--------------------------------------------------------
        if mLoftCurve:
            _d['loft'].append(get(mLoftCurve))
            _d['loftShapes'].append(shapes_get(mLoftCurve,'all'))
        else:
            _d['loft'].append(False)
            _d['loftShapes'].append(False)            
        
        #sub..--------------------------------------------------------
        ml_subShapers = mObj.msgList_get('subShapers')
        #If subShapes, process them
        if ml_subShapers:
            l_subShapes = []
            l_sub = []
            for ii,mObj in enumerate(ml_subShapers):
                l_subShapes.append( shapes_get(mObj,'all'))
                l_sub.append( get(mObj))
            
            _d['subRelative'].append( relativePointDat_getFromObjs([mObj.mNode for mObj in ml_subShapers],
                                                           ml_handles[i].mNode,ml_handles[i+1].mNode) )
            _d['subShapes'].append( l_subShapes )
            _d['sub'].append( l_sub )
            _num_subs.append(len(ml_subShapers))
        else:
            _d['sub'].append(False)
            _d['subShapes'].append(False)               
            _d['subRelative'].append(False)               
            _num_subs.append(0)

    #pprint.pprint(_res)
    
    #Restore our block...-----------------------------------------------------------------
    mBlock.p_position = pos
    mBlock.p_orient = orient      
    return _res
    
    
def shapes_get(mObj, mode = 'os'):
    _str_func = 'shapes_get'
    log.debug(log_start(_str_func))
        
    _obj = mObj.mNode
    _res = {}
    _l_shapes_source = mc.listRelatives(_obj,shapes=True,fullPath=True)

    for i,s in enumerate(_l_shapes_source):
        _l_ep_source = mc.ls("{0}.cv[*]".format(s),flatten = True)
        
        #Object Space
        if mode in ['os','all']:
            if not _res.get('os'):
                _res['os'] = []
                
            _d = []
            _res['os'].append(_d)
            for i,ep in enumerate(_l_ep_source):
                _d.append(POS.get(ep,space='os'))
        
        #WorldSpace
        if mode in ['ws','all']:
            if not _res.get('ws'):
                _res['ws'] = []        
            _d = []
            _res['ws'].append(_d)
            for i,ep in enumerate(_l_ep_source):
                _d.append(POS.get(ep,space='ws'))        
            
    #pprint.pprint(_res)
    return _res

def shapes_set(mObj, dat, mode = 'os'):
    _str_func = 'shapes_set'
    log.debug(log_start(_str_func))
    
    _dat = dat[mode]
    _obj = mObj.mNode
    _l_shapes_source = mc.listRelatives(_obj,shapes=True,fullPath=True)
    
    if len(_l_shapes_source) != len(_dat):
        raise ValueError,"Len of source shape ({0}) != dat ({1})".format(len(_l_shapes_source),len(_dat)) 
    
    for i,s in enumerate(_l_shapes_source):
        _l_ep_source = mc.ls("{0}.cv[*]".format(s),flatten = True)
        _l_pos = _dat[i]
        
        if len(_l_ep_source) != len(_l_pos):
            raise ValueError,"Len of source shape {} | ({}) != dat ({})".format(i,len(_l_ep_source),len(_l_pos))         
        
        for ii,ep in enumerate(_l_ep_source):
            POS.set(ep, _l_pos[ii],space=mode)  
            

def relativePointDat_getFromObjs(targets, start,end, vUp = [0,0,-1]):
    """
    pTar - point of the target
    pStart - Start point
    pEnd - endPoint
    dBase - base distance start to end
    pCrv - closest point on crv
    dCrv - distance to point on crv
    vCrv - vector from crv to point
    vUp - vector up (not using this yet)
    
    """
    _str_func = 'relativePointDat_getFromObj'
    log.debug(log_start(_str_func))
    _res = {'tar':[]}
    
    ml_targets = cgmMeta.validateObjListArg(targets)
    mStart = cgmMeta.validateObjArg(start)
    mEnd = cgmMeta.validateObjArg(end)
    
    
    #p1, p2, pTar
    _res['pStart'] = mStart.p_position
    _pEnd = mEnd.p_position
    
    
    #distance between p1 p2
    _res['dBase'] = DIST.get_distance_between_points(_res['pStart'],_pEnd)
    _res['vBase'] = MATH.get_vector_of_two_points(_res['pStart'],_pEnd)
    _res['vUp'] = vUp
    
    #closest point on linear curve between those
    _crv = CORERIG.create_at(l_pos=[_res['pStart'],_pEnd],create='curveLinear')
    
    for mObj in ml_targets:
        _dObj = {}
        _p = mObj.p_position
        _r = DIST.get_closest_point(_p, _crv, loc=False)
        _close = _r[0]
        _d2 = _r[1]
        #_d2 = DIST.get_distance_between_points(_close, _res['pTar'])
        _vecCrv = MATH.get_vector_of_two_points(_close, _p)
        
        #get dist from start to closest
        _dObj['dClose'] = DIST.get_distance_between_points(_res['pStart'],_close)
        
        _dObj['dCrv'] = _d2
        _dObj['vCrv'] = _vecCrv
        
        _res['tar'].append(_dObj)
    
    mc.delete(_crv)
    
    for k in ['pStart']:
        _res.pop(k)
        
    #pprint.pprint(_res)

    return _res


def relativePointDat_setFromObjs(targets, start, end, d = {}):
    """
    pTar - point of the target
    pStart - Start point
    pEnd - endPoint
    dBase - base distance start to end
    pCrv - closest point on crv
    dCrv - distance to point on crv
    vCrv - vector from crv to point
    vUp - vector up (not using this yet)
    
    """
    _str_func = 'relativePointDat_setFromObjs'
    log.debug(log_start(_str_func))
    _res = {}
    
    ml_targets = cgmMeta.validateObjListArg(targets)
    mStart = cgmMeta.validateObjArg(start)
    mEnd = cgmMeta.validateObjArg(end)
    
    l_tarDat = d.get('tar',[])
    if len(ml_targets) < len(l_tarDat):
        raise ValueError,"must have same number of targets as data"
    
    _pStart = mStart.p_position
    _pEnd = mEnd.p_position    
    
    #Get factor -------------------------------------------------------------
    _dCurrent = DIST.get_distance_between_points(_pStart,_pEnd)
    _fac = _dCurrent / d['dBase'] 
    
    
    #transform vector ------------------------------------------------------
    
    vCurrent = MATH.get_vector_of_two_points(_pStart,_pEnd,True)
    vOffset =   MATH.dotproduct(MATH.Vector3(d['vBase'][0],d['vBase'][1],d['vBase'][2]), vCurrent)
    
    #vOffset =   MATH.Vector3(d['vBase'][0],d['vBase'][1],d['vBase'][2]) - vCurrent
    
    for i,mTarget in enumerate(ml_targets):
        dUse = l_tarDat[i] 
        vNew =  MATH.Vector3(dUse['vCrv'][0],dUse['vCrv'][1],dUse['vCrv'][2] ) * (vOffset)
        
        
        #Get relative closest point - start > vector * dClose * factor
        _close = DIST.get_pos_by_vec_dist(_pStart, vCurrent, dUse['dClose'] * _fac)
        #LOC.create(position=_close,name="close")
        
        _new = DIST.get_pos_by_vec_dist(_close, vNew, dUse['dCrv'] * _fac)
        
        
        mTarget.p_position = _new
    
    
    
    #pprint.pprint(vars())

    return _res

def relativePointDat_get(point, pStart,pEnd):
    _str_func = 'relativePointDat_get'
    log.debug(log_start(_str_func))
    
    _res = {}
    
    
    
    
    return _res