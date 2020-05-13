"""
------------------------------------------
attrTools: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
2.0 rewrite
================================================================
"""
# From Python =============================================================
import copy
import re
import pprint
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


import maya.cmds as mc


import cgm.core.classes.GuiFactory as cgmUI
#reload(cgmUI)
mUI = cgmUI.mUI

from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import name_utils as NAMES
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import list_utils as LISTS
from cgm.core.tools.markingMenus.lib import contextual_utils as CONTEXT
from cgm.core.cgmPy import str_Utils as STRINGS
import Red9.core.Red9_CoreUtils as r9Core

#reload(STRINGS)
#reload(SEARCH)
#>>> Root settings =============================================================
__version__ = '2.0.11222019'

#__toolURL__ = 'www.cgmonks.com'
#__author__ = 'Josh Burton'
#__owner__ = 'CG Monks'
#__website__ = 'www.cgmonks.com'
#__defaultSize__ = 375, 350



class uiWin_addAttr(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmAddAttr_ui'    
    WINDOW_TITLE = 'cgmAddAttr - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 375,150
    
    def insert_init(self,*args,**kws):
            if kws:log.debug("kws: %s"%str(kws))
            if args:log.debug("args: %s"%str(args))
            log.info(self.__call__(q=True, title=True))
    
            self.description = 'Tool to add attributes'
            self.__version__ = __version__
            self.__toolName__ = 'cgmAddAttr'		
            self.l_allowedDockAreas = []
            self.WINDOW_TITLE = uiWin_addAttr.WINDOW_TITLE
            #self.DEFAULT_SIZE = __defaultSize__

    def buildMenu_help( self, *args):
            self.uiMenu_HelpMenu.clear()
            mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Show Help",
                             cb=self.var_ShowHelp.value,
                             c= lambda *a: self.do_showHelpToggle())

    def build_menus(self):pass#...don't want em  
    
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        _MainForm = mUI.MelColumnLayout(parent)
        cgmUI.add_Header('Create')
        cgmUI.add_LineSubBreak()

        #>>>Create Row ---------------------------------------------------------------------------------------
        _row_attrCreate = mUI.MelHSingleStretchLayout(_MainForm,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_attrCreate)
    
        mUI.MelLabel(_row_attrCreate,l='Names:',align='right')
        self.AttrNamesTextField = mUI.MelTextField(_row_attrCreate,backgroundColor = [1,1,1],h=20,
                                                   #ec = lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                                                   annotation = "Names for the attributes. Create multiple with a ','. \n Message nodes try to connect to the last object in a selection \n For example: 'Test1;Test2;Test3'")
        cgmUI.add_Button(_row_attrCreate,'Add',
                             #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                             "Add the attribute names from the text field")
        mUI.MelSpacer(_row_attrCreate,w=2)
    
        _row_attrCreate.setStretchWidget(self.AttrNamesTextField)
        _row_attrCreate.layout()  
        
        uiRow_attributeTypes(self,_MainForm)

        log.info("|{0}| >> Selected: {1}".format(_str_func, self.rc_attrTypes.getSelectedIndex()))
        
        
class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmAttrTools_ui'    
    WINDOW_TITLE = 'cgmAttrTools - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 375,300
    _checkBoxKeys = ['shared','default','user','others']
    
    def insert_init(self,*args,**kws):
            if kws:log.debug("kws: %s"%str(kws))
            if args:log.debug("args: %s"%str(args))
            log.info(self.__call__(q=True, title=True))
    
            self.__version__ = __version__
            self.__toolName__ = 'cgmMultiSet'		
            #self.l_allowedDockAreas = []
            self.WINDOW_TITLE = ui.WINDOW_TITLE
            self.DEFAULT_SIZE = ui.DEFAULT_SIZE
            self._d_attrs = {}
            self._ml_nodes = []
            self._l_attrsSelected = []
            self.uiPopUpMenu_attr = False
            
            self.create_guiOptionVar('keysMode',  defaultValue = 'each')
            self.create_guiOptionVar('valuesMode',  defaultValue = 'primeNode')                        
            self.create_guiOptionVar('context',  defaultValue = 'loaded')            
            

    def build_menus(self):
        self.uiMenu_context = mUI.MelMenu( l='Context', pmc=self.buildMenu_context)           
        self.uiMenu_valueModes = mUI.MelMenu( l='Values', pmc=self.buildMenu_values)           
        self.uiMenu_keysModes = mUI.MelMenu( l='Keys', pmc=self.buildMenu_keys)           
        self.uiMenu_utils = mUI.MelMenu( l='Utils', pmc=self.buildMenu_utils)           
        
        self.uiMenu_help = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)           
        #pass#...don't want em  
    #def setup_Variables(self):pass
    
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
    
        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("http://docs.cgmonks.com/attrtools.html");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )      
    
    def buildMenu_context( self, *args):
        self.uiMenu_context.clear()
        
        uiRC = mc.radioMenuItemCollection(parent = self.uiMenu_context)
        #self.uiOptions_menuMode = []		
        _v = self.var_context.value
        
        _d_annos = {'loaded':'Will use objects loaded to the ui',
                    'selection':'Will use any selected objects primNode type',
                    'children':'Will use any objects below primeNode heirarchally and matching type',
                    'heirarchy':'Will use any objects in primNode heirarchy and matching type',
                    'scene':'Will use any objects in scene matching primeNode type'}

        for i,item in enumerate(['loaded','selection','children','heirarchy','scene']):
            if item == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(parent=self.uiMenu_context,collection = uiRC,
                        label=item,
                        ann=_d_annos.get(item,'Fill out the dict!'),
                        c = cgmGEN.Callback(self.var_context.setValue,item),                                  
                        rb = _rb)                        
        
        mUI.MelMenuItemDiv(parent=self.uiMenu_context)
        mc.menuItem(parent=self.uiMenu_context,collection = uiRC,
                    label='Report',
                    ann='Print the current context report.',
                    c = cgmGEN.Callback(get_context, self, _v, True))          
        
        """#>>> Reset Options		
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c=lambda *a: self.reload())		
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c=lambda *a: self.reset())"""   
        
    def buildMenu_keys( self, *args):
        self.uiMenu_keysModes.clear()
        
        uiRC = mc.radioMenuItemCollection(parent = self.uiMenu_keysModes)
        #self.uiOptions_menuMode = []		
        _v = self.var_keysMode.value
        
        _d_annos = {'primeNode':'Any keys on prime node',
                    'each':'Each contextual nodes will take values on own keys',
                    'combined':'Combine keys of conextual nodes and prime'}        

        for i,item in enumerate(['primeNode','each','combined']):
            if item == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(parent=self.uiMenu_keysModes,collection = uiRC,
                        label=item,
                        ann=_d_annos.get(item,'Fill out the dict!'),                        
                        c = cgmGEN.Callback(self.var_keysMode.setValue,item),                                  
                        rb = _rb) 
            
        mUI.MelMenuItemDiv(parent=self.uiMenu_keysModes)
        mc.menuItem(parent=self.uiMenu_keysModes,collection = uiRC,
                    label='Report',
                    ann='Print the current values report.',
                    c = cgmGEN.Callback(get_keys, self, self.var_context.value, 'all',True))  
        
    def buildMenu_utils( self, *args):
        self.uiMenu_utils.clear()
        
        _en = False
        if  self.var_context.value == 'selection':
            _en = True
            
        mUI.MelMenuItemDiv(parent=self.uiMenu_utils,label = 'Selection')
        mUI.MelMenuItem(parent=self.uiMenu_utils,
                    label='Channelbox Bridge',
                    ann='Copy the selected channelbox attributes to the prime node and drive this node from that',
                    en = True,
                    c = cgmGEN.Callback(self.uiFunc_channelBoxBridge))          
        

        
        return
        
        uiRC = mc.radioMenuItemCollection(parent = self.uiMenu_valueModes)
        #self.uiOptions_menuMode = []		
        _v = self.var_valuesMode.value
        
        _d_annos = {'primeAttr':'First attribute values will be pushed',
                    'primeAttrPer':'First attribute value per key will be pushed',
                    'primeNode':'Values from primeNode will be pushed',
                    'primeNodePer':'Values from primenode per key will be pushed',
                    'each':'Values from each object will be pushed',
                    }        

        for i,item in enumerate(['primeAttr','primeAttrPer','primeNode','primeNodePer','each']):
            if item == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(parent=self.uiMenu_valueModes,collection = uiRC,
                        label=item,
                        ann=_d_annos.get(item,'Fill out the dict!'),                        
                        c = cgmGEN.Callback(self.var_valuesMode.setValue,item),                                  
                        rb = _rb)
            
        mUI.MelMenuItemDiv(parent=self.uiMenu_valueModes)
        mc.menuItem(parent=self.uiMenu_valueModes,collection = uiRC,
                    label='Report',
                    ann='Print the current values report.',
                    c = cgmGEN.Callback(get_values, self, self.var_context.value, True))           

    def buildMenu_values( self, *args):
        self.uiMenu_valueModes.clear()
        
        uiRC = mc.radioMenuItemCollection(parent = self.uiMenu_valueModes)
        #self.uiOptions_menuMode = []		
        _v = self.var_valuesMode.value
        
        _d_annos = {'primeAttr':'First attribute values will be pushed',
                    'primeAttrPer':'First attribute value per key will be pushed',
                    'primeNode':'Values from primeNode will be pushed',
                    'primeNodePer':'Values from primenode per key will be pushed',
                    'each':'Values from each object will be pushed',
                    }        

        for i,item in enumerate(['primeAttr','primeAttrPer','primeNode','primeNodePer','each']):
            if item == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(parent=self.uiMenu_valueModes,collection = uiRC,
                        label=item,
                        ann=_d_annos.get(item,'Fill out the dict!'),                        
                        c = cgmGEN.Callback(self.var_valuesMode.setValue,item),                                  
                        rb = _rb)
            
        mUI.MelMenuItemDiv(parent=self.uiMenu_valueModes)
        mc.menuItem(parent=self.uiMenu_valueModes,collection = uiRC,
                    label='Report',
                    ann='Print the current values report.',
                    c = cgmGEN.Callback(get_values, self, self.var_context.value, True))           
            
    def uiFunc_clear_loaded(self):
        _str_func = 'uiFunc_clear_loaded'  
        self._d_attrs = {}
        self._ml_nodes = []
           
        self.uiReport_objects()
        self.uiScrollList_attr.clear()
        self._d_uiCheckBoxes['shared'](edit = True, en=True)
        
    def uiFunc_report_loaded(self):
        _str_func = 'cgmAttrTools'  
        
        if not self._ml_nodes:
            log.info("|{0}| >> No objects loaded".format(_str_func))
        else:
            log.info("|{0}| >> Loaded...".format(_str_func))            
            
            for i,mObj in enumerate(self._ml_nodes):
                _short = mObj.p_nameShort
                log.info("|{0}| >> {1} : {2} | attrs: {3}...".format(_str_func,i,_short, len(self._d_attrs[_short])))
        
        
        log.info("|{0}| >> scroll listattrs...".format(_str_func,))        
        for a in self._l_attrsToLoad:
            log.info("|{0}| >> {1} ...".format(_str_func,a))     
            
    def uiFunc_load(self, nodes, attrs):
        _str_func = 'uiFunc_load'  
        
        log.info("|{0}| >> nodes: {1} | attrs: {2}".format(_str_func, nodes, attrs))
        
        mc.select(nodes)
        self._l_attrsSelected = VALID.listArg(attrs)
        
        self.uiFunc_load_selected(True)
        
    def uiFunc_load_selected(self, bypassAttrCheck = False):
        _str_func = 'uiFunc_load_selected'  
        self._d_attrs = {}
        self._ml_nodes = []
        
        _sel = mc.ls(sl=True)
        if bypassAttrCheck is not True:
            _sel_attrs = SEARCH.get_selectedFromChannelBox(True)
            if _sel_attrs:#...push any selected channels to preselect
                self._l_attrsSelected = _sel_attrs
            
        #Get our raw data
        for o in _sel:
            _type = VALID.get_mayaType(o)
            #if VALID.is_transform(o) or VALID.is_shape(o):
            mNode = cgmMeta.validateObjArg(o)
            self._ml_nodes.append( mNode )
            _short = mNode.p_nameShort
            log.debug("|{0}| >> Good obj: {1}".format(_str_func, _short))
            self._d_attrs[_short] = mc.listAttr(_short)
            #else:
                #log.debug("|{0}| >> Bad obj: {1}".format(_str_func, NAMES.get_short(o)))
                
        if len(self._ml_nodes) < 2:
            self._d_uiCheckBoxes['shared'](edit = True, en=False)
        else:
            self._d_uiCheckBoxes['shared'](edit = True, en=True)    
        self.uiReport_objects()
        self.uiScrollList_attr.clear()        
        self.uiFunc_updateScrollAttrList()
        
    def uiFunc_connect(self, fromAttr, toAttr):
        _str_func = 'uiFunc_connect'          
        try:
            ATTR.connect(fromAttr,toAttr)
        except Exception,err:
            log.info("|{0}| >> fromAttr: {1} | toAttr: {2} || err: {3}".format(_str_func, fromAttr, toAttr, err))
        self.uiFunc_updateScrollAttrList()
    
    def uiFunc_breakConnection(self, combined):
        _str_func = 'uiFunc_breakConnection'          
        try:
            ATTR.break_connection(combined)
        except Exception,err:
            log.info("|{0}| >> combined: {1} || err: {3}".format(_str_func, combined, err))
        self.uiFunc_updateScrollAttrList()
        
        
        
    def uiFunc_updateDisplay(self):
        _str_func = 'uiFunc_updateDisplay'  
        
        self._l_attrsLoaded = []
        
        self.uiScrollList_attr.clear()
        _filter = self.uiField_attrFilter.getValue()
        log.info(_filter)
        
        for i,a in enumerate(r9Core.filterListByString(self._l_attrsProcessed,
                                                       _filter,
                                                       matchcase=False)):

            self.uiScrollList_attr.append(self._d_attrStrings.get(a,a))
            self._l_attrsLoaded.append(a)
            
        pprint.pprint(self._l_attrsLoaded)
        
    def uiFunc_updateScrollAttrList(self):
        try:
            _str_func = 'uiFunc_updateScrollAttrList'          
            self._l_attrsToLoad = []
            self._l_attrsLoaded = []
            self._l_attrsProcessed = []
            self._l_attrsStrings = []
            self._d_attrStrings = {}
            
            _d_processed = {}
            
            if not self._ml_nodes:
                return False      
            
            #for k in ui._checkBoxKeys:
                #log.info("{0} : {1}".format(k, self._d_uiCheckBoxes[k].getValue()))
            #['shared','keyable','transforms','user','other']
            
            _shared = self._d_uiCheckBoxes['shared'].getValue()
            _default = self._d_uiCheckBoxes['default'].getValue()
            _user = self._d_uiCheckBoxes['user'].getValue()
            _others = self._d_uiCheckBoxes['others'].getValue()
            _sort = self._d_uiCheckBoxes['sort'].getValue()
            
            if _user:
                self.row_move(edit =True, vis = True)
            else:
                self.row_move(edit = True, vis = False)
            
            #_transforms = self._d_uiCheckBoxes['trans'].getValue()        
            #_other = self._d_uiCheckBoxes['other'].getValue()
            
            for mObj in self._ml_nodes:
                _short = mObj.p_nameShort
                _d_processed[_short] = []
                _l_processed = _d_processed[_short] 
                _is_transform = VALID.is_transform(_short)           
                _l = mc.listAttr(_short, settable=True) or []
                if _is_transform:
                    _l.extend(SHARED._d_attrCategoryLists['transform']) 
                else:
                    _l.extend(mc.listAttr(_short, inUse=True) or [])
                """if _default:
                    _l.extend( mc.listAttr(_short) or [])
                    #if VALID.getTransform(_short):
                        #_l.extend(SHARED._d_attrCategoryLists['transform'])                
                
                #if _user:_l.extend(mc.listAttr(_short, ud=True) or [])
                
                if _others:
                    _l.extend( mc.listAttr(_short, settable=True) or [])"""
                    
                    
                _l = LISTS.get_noDuplicates(_l)
    
                for a in _l:
                    try:
                        if a.count('.')>0:
                            continue
                        _d = ATTR.validate_arg(_short,a)
                        _dyn = ATTR.is_dynamic(_d)
                        _hidden = ATTR.is_hidden(_d)
                        
                        if _default:
                            if _is_transform:
                                if not _hidden and not _dyn:
                                    _l_processed.append(a)
                                if _d['attr'] in SHARED._d_attrCategoryLists['transform'] or _d['attr'] in ['translate','rotate','scale']:
                                    _l_processed.append(a)
                            else:
                                if a not in ['isHistoricallyInteresting','nodeState','binMembership','caching','frozen']:
                                    _l_processed.append(a)
                        if _user and _dyn:
                            _l_processed.append(a)
                        if _others and a not in _l_processed:
                            _l_processed.append(a)
                        """if _numeric:
                            if ATTR.is_numeric(_d):
                                _l_processed.append(a)
                        else:
                            _l_processed.append(a)"""
                    except Exception,err:
                        log.warning("|{0}| >> Failed to process: {1} : {2} || err:{3}".format(_str_func, _short, a,err))
    
            for a in ['ghostDriver','hyperLayout','attributeAliasList']:
                if a in _l_processed:_l_processed.remove(a)
            
            
            if _shared and len(self._ml_nodes)>1:
                self._l_attrsToLoad = _d_processed[self._ml_nodes[0].p_nameShort]#...start with our first object
                _l_good = []
                for mObj in self._ml_nodes[1:]:
                    _l = _d_processed[mObj.p_nameShort]
                    for a in self._l_attrsToLoad:
                        if a not in _l:
                            log.debug("|{0}| >> '{1}' not shared. removing...".format(_str_func, a))                           
                            #self._l_attrsToLoad.remove(a)
                        else:
                            _l_good.append(a)
                self._l_attrsToLoad = LISTS.get_noDuplicates(_l_good)
                
            else:
                for k,l in _d_processed.iteritems():
                    self._l_attrsToLoad.extend(l)
                    
                self._l_attrsToLoad = LISTS.get_noDuplicates(self._l_attrsToLoad)
            
            if _sort:
                self._l_attrsToLoad.sort()
            
            """for a in self._l_attrsToLoad:
                log.info("|{0}| >> {1} : {2}".format(_str_func, _short, a))   
            log.info(cgmGEN._str_subLine)"""
    
            #...menu...
            log.debug("|{0}| >> List....".format(_str_func,))                
            self.uiScrollList_attr.clear()
            _len = len(self._ml_nodes)
            
            if not self._l_attrsToLoad:
                return False
            
            _progressBar = cgmUI.doStartMayaProgressBar(len(self._l_attrsToLoad),"Processing...")
            try:
                for a in self._l_attrsToLoad:
                    if _progressBar:
                        mc.progressBar(_progressBar, edit=True, status = ("{0} Processing attribute: {1}".format(_str_func,a)), step=1)                    
                    
                    try:
                        _short = self._ml_nodes[0].p_nameShort
                        _d = ATTR.validate_arg(_short,a)
                        
                        _l_report = []
                        
                        _type = ATTR.get_type(_d)
                        _type = SHARED._d_attrTypes_toShort.get(_type,_type)
                        _user = False
                        
                        _l_flags = []
                        
                        if ATTR.is_dynamic(_d):
                            _user = True
                            _l_flags.append('u')                      
                        
                        _alias = ATTR.get_alias(_d)
                        _nice = ATTR.get_nameNice(_d)
                        _long = ATTR.get_nameLong(_d)
                        
                        _l_name = []
                        _l_name.append(_long)
                        
                        if _alias:
                            _l_name.append("--alias({0})".format(_alias) )
                        if _user and _nice and _nice != _long:
                            if _nice != ATTR.get_nameNice_string(_long):
                                _l_name.append("--nice({0})".format(_nice))
                        _l_name.append("--({0})--".format(_type) )
                        
                        _l_report.append("".join(_l_name))
                        
    
                            
                        if ATTR.is_hidden(_d):
                            _l_flags.append('h')
                        else:
                            _l_flags.append('v')                     
                        
                        if ATTR.is_keyable(_d):
                            _l_flags.append('k')   
                            
                        if ATTR.is_locked(_d):
                            _l_flags.append('l')
                                                   
                        """if ATTR.is_readable(_d):
                            _l_flags.append('R')
                        if ATTR.is_writable(_d):
                            _l_flags.append('W')"""
                        if _l_flags:
                            #_l_report.append("flg {0}".format(''.join(_l_flags)))
                            _l_report.append(' '.join(_l_flags))
                            
                        if ATTR.get_driver(_d):
                            if ATTR.is_keyed(_d):
                                _l_report.append("<anim" )                        
                            else:
                                _l_report.append("<<<" )
                        if ATTR.get_driven(_d):
                            _l_report.append(">>>" )
                            
    
                        if ATTR.is_numeric(_d):
                            _d_flags = ATTR.get_numericFlagsDict(_d)
                            if _d_flags.get('default') not in [False,None]:
                                _l_report.append("dv={0}".format(_d_flags.get('default')))
                            if _d_flags.get('min') not in [False,None]:
                                _l_report.append("m={0}".format(_d_flags.get('min'))) 
                            if _d_flags.get('max') not in [False,None]:
                                _l_report.append("M={0}".format(_d_flags.get('max')))     
                            if _d_flags.get('softMin') not in [False,None]:
                                _l_report.append("sm={0}".format(_d_flags.get('softMin')))
                            if _d_flags.get('softMax') not in [False,None]:
                                _l_report.append("sM={0}".format(_d_flags.get('softMax')))                                
                            
                        if _type == 'enum':
                            _v = ATTR.get(_d)
                            _options = ATTR.get_enum(_d).split(':')
                            _options[_v] = "[ {0} ]".format(_options[_v])
                            _v = (' , '.join(_options))
                        else:
                            _v = "{0}".format(ATTR.get(_d))
                            for chk in [':']:
                                if chk in _v:
                                    _v = 'NONDISPLAYABLE'
                                    continue
                            if len(_v)> 20 and _type not in ['msg']:
                                _v = _v[:20] + "...  "
                        _l_report.append(_v)
                            
                        #_str = " -- ".join(_l_report)
                        #self._l_attrsStrings.append(" // ".join(_l_report))
                        #self.uiScrollList_attr.append(" // ".join(_l_report))
                        self._l_attrsProcessed.append(a)
                        self._d_attrStrings[a] = " // ".join(_l_report)
                        
                    except Exception,err:
                        log.info("|{0}| >> {1}.{2} | failed to query. Removing. err: {3}".format(_str_func, _short, a, err))  
                        self._l_attrsToLoad.remove(a)
                    log.debug("|{0}| >> {1} : {2}".format(_str_func, _short, a))  
            except Exception,err:
                log.error(err)
            finally:
                cgmUI.doEndMayaProgressBar(_progressBar)

            #menu(edit=True,cc = uiAttrUpdate)
            
            self.uiFunc_updateDisplay()
            
            #Reselect
            try:
                if self._l_attrsSelected:
                    _indxs = []
                    for a in self._l_attrsSelected:
                        log.debug("|{0}| >> Selected? {1}".format(_str_func,a))                              
                        if a in self._l_attrsLoaded:
                            self.uiScrollList_attr.selectByIdx(self._l_attrsLoaded.index(a))
            except:
                log.error("Failed to reselect")
                        
                        
            return False
        except Exception,err:cgmGEN.cgmException(Exception,err)

        
    def uiReport_objects(self):
        if self._d_attrs:
            if len(self._ml_nodes) == 1:
                _short = self._ml_nodes[0].p_nameShort
                _str_report = ' | '.join([_short,
                                         "attrs: {0}".format(len(self._d_attrs[_short]))])
            else:
                _l = [mObj.p_nameBase for mObj in self._ml_nodes]                
                _str_report = '<{0}> , '.format(_l[0]) + ' , '.join(_l[1:])
                if len(_str_report) >= 100:
                    _str_report = "{0} Objects. Report to see them all".format(len(self._ml_nodes))
            self.uiField_attrReport(edit=True, label = _str_report)   
        else:
            self.uiField_attrReport(edit=True, label = '...')
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        self._d_uiCheckBoxes = {}
        
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUISubTemplate')
        
        _header = cgmUI.add_Header('Objects')
        #cgmUI.add_LineSubBreak()
        
        
        _row_attrReport = mUI.MelHLayout(_MainForm ,ut='cgmUIInstructionsTemplate',h=20)
        self.uiField_attrReport = mUI.MelLabel(_row_attrReport,
                                               bgc = SHARED._d_gui_state_colors.get('help'),
                                               label = '...',
                                               h=20)
        _row_attrReport.layout()
        
        #mc.setParent()
        #cgmUI.add_LineBreak()
        #mc.setParent()        
        #cgmUI.add_SectionBreak()
        

        #>>>Objects Buttons Row ---------------------------------------------------------------------------------------
        _row_attrCreate = mUI.MelHLayout(_MainForm,ut='cgmUISubTemplate',padding = 5)
    
        cgmUI.add_Button(_row_attrCreate,'Load Selected',
                         cgmGEN.Callback(self.uiFunc_load_selected),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Load selected nodes to the ui. First in selection is prime node.")
        cgmUI.add_Button(_row_attrCreate,'Refresh',
                         cgmGEN.Callback(self.uiFunc_updateScrollAttrList),                         
                         "Refresh the attributes in the scroll list. Useful if keyed.")        

        cgmUI.add_Button(_row_attrCreate,'Clear',
                         cgmGEN.Callback(self.uiFunc_clear_loaded),                         
                         "Clear loaded nodes")
        _row_attrCreate.layout()  
        
        #Flags ---------------------------------------------------------------------------------------------
        _row_attrFlags = mUI.MelHSingleStretchLayout(_MainForm,ut='cgmUISubTemplate',padding = 5)
        
        mUI.MelSpacer(_row_attrFlags,w=5)
        self._d_uiCheckBoxes['sort'] = mUI.MelCheckBox(_row_attrFlags,label = 'Sort',
                                                       v=True,
                                                       cc = cgmGEN.Callback(self.uiFunc_updateScrollAttrList))                

        mUI.MelLabel(_row_attrFlags,l = 'Show')
        _row_attrFlags.setStretchWidget( mUI.MelSeparator(_row_attrFlags) )
        for item in ui._checkBoxKeys:
            if item in ['shared','default','user']:_cb = True
            else:_cb = False
            self._d_uiCheckBoxes[item] = mUI.MelCheckBox(_row_attrFlags,label = item,
                                                         v = _cb,
                                                         cc = cgmGEN.Callback(self.uiFunc_updateScrollAttrList))
        _row_attrFlags.layout()
        
        #>>>Manage Attribute Section ---------------------------------------------------------------------------------------
        self.uiScrollList_attr = mUI.MelObjectScrollList(_MainForm, allowMultiSelection=True,
                                                         dcc = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}),
                                                         selectCommand = self.uiFunc_selectAttr)
        
        #Search --------------------------------------------------------------------------------
        _textField = mUI.MelTextField(_MainForm,
                                      ann='Filter Attrs',
                                      w=50,
                                      bgc = [.3,.3,.3],
                                      en=True,
                                      text = '')
        self.uiField_attrFilter = _textField
        self.uiField_attrFilter(edit=True,
                                tcc = lambda *a: self.uiFunc_updateDisplay())        
        
        """#>>>Keys Row --------------------------------------------------------------------------------------------        
       
        
        self.create_guiOptionVar('keyMode',defaultValue = 0)       
        
        self.rc_keyMode = mUI.MelRadioCollection()
        _l_keyModes = ['primeAttr','primeObj','each','combined']
        #build our sub section options
        _row_keyModes = mUI.MelHSingleStretchLayout(_MainForm,ut='cgmUISubTemplate',padding = 5)
        mUI.MelLabel(_row_keyModes,l = 'Keys')
        _row_keyModes.setStretchWidget( mUI.MelSeparator(_row_keyModes) )
        
        _on = self.var_keyMode.value
        
        for cnt,item in enumerate(_l_keyModes):
            if cnt == _on:_rb = True
            else:_rb = False
            self.rc_keyMode.createButton(_row_keyModes,label=_l_keyModes[cnt],sl=_rb,
                                         onCommand = cgmGEN.Callback(self.var_keyMode.setValue,cnt))
            mUI.MelSpacer(_row_keyModes,w=2)
    
        
        _row_keyModes.layout()        
        
        #>>>Values Mode Row --------------------------------------------------------------------------------------------        
        
        self.create_guiOptionVar('valueMode',defaultValue = 0)       
        _row_valueModes = mUI.MelHSingleStretchLayout(_MainForm,ut='cgmUISubTemplate',padding = 5)
        
        self.rc_valueMode = mUI.MelRadioCollection()
        _l_valueModes = ['primeAttr','primeObj']
        #build our sub section options
        mUI.MelLabel(_row_valueModes,l = 'Values')
        _row_valueModes.setStretchWidget( mUI.MelSeparator(_row_valueModes) )
        
        _on = self.var_valueMode.value
    
        for cnt,item in enumerate(_l_valueModes):
            if cnt == _on:_rb = True
            else:_rb = False
            self.rc_valueMode.createButton(_row_valueModes,label=_l_valueModes[cnt],sl=_rb,
                                         onCommand = cgmGEN.Callback(self.var_valueMode.setValue,cnt))
            mUI.MelSpacer(_row_valueModes,w=2)        
        
        _row_valueModes.layout()  """ 
        
        #>>>Objects Buttons Row ---------------------------------------------------------------------------------------
        _row_move = mUI.MelHLayout(_MainForm,ut='cgmUISubTemplate',padding = 5, vis = False)
        self.row_move = _row_move
    
        cgmUI.add_Button(_row_move,'Move Up',
                         cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'moveUp'}),                                                     
                         "Load selected nodes to the ui. First in selection is prime node.")
        cgmUI.add_Button(_row_move,'Move Down',
                         cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'moveDown'}),                                                     
                         "Refresh the attributes in the scroll list. Useful if keyed.")        
        _row_move.layout()      
        
        #>>>Push Values header ---------------------------------------------------------------------------------------        
        mc.setParent(_MainForm)        
        _header_push = cgmUI.add_Header('Push Values')
        
        #>>>Push Values Row --------------------------------------------------------------------------------------------
        self.row_setValue = mUI.MelHLayout(_MainForm,ut='cgmUISubTemplate',padding = 2)
        
        cgmUI.add_Button(self.row_setValue,'<<Back',
                         cgmGEN.Callback(self.uiFunc_pushValue,**{'mode':'back'}),                
                         "Push values to all previous frames") 
        cgmUI.add_Button(self.row_setValue,'<Prev',
                         cgmGEN.Callback(self.uiFunc_pushValue,**{'mode':'previous'}),                
                         "Push current values to the previous key")
        
        cgmUI.add_Button(self.row_setValue,'Current',
                         cgmGEN.Callback(self.uiFunc_pushValue,**{'mode':'current'}),                
                         "Push current values in context")
        cgmUI.add_Button(self.row_setValue,'All',
                         cgmGEN.Callback(self.uiFunc_pushValue,**{'mode':'all'}),                
                         "Push current values in context")


        cgmUI.add_Button(self.row_setValue,'Next>',
                         cgmGEN.Callback(self.uiFunc_pushValue,**{'mode':'next'}),                
                         "Push current values to the next key")
        cgmUI.add_Button(self.row_setValue,'Fwd>>',
                         cgmGEN.Callback(self.uiFunc_pushValue,**{'mode':'forward'}),                
                         "Push values to all future keys")

        self.row_setValue.layout()
        
        
        #>>>Footer
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)
        
        _MainForm(edit = True,
                  af = [(_header,"top",0),
                        (_header,"left",0),
                        (_header,"right",0),
                        (self.uiScrollList_attr,"left",0),
                        (self.uiScrollList_attr,"right",0),
                        (_row_attrReport,"left",0),
                        (_row_attrReport,"right",0),
                        (_row_attrCreate,"left",0),
                        (_row_attrCreate,"right",0),
                        (_row_attrFlags,"left",0),
                        (_row_attrFlags,"right",0),
                        (self.uiField_attrFilter,"left",0),
                        (self.uiField_attrFilter,"right",0),                        
                         
                        (_row_move,"left",0),
                        (_row_move,"right",0),                        
                        (_header_push,"left",0),
                        (_header_push,"right",0),                         
                        #(_row_keyModes,"left",5),
                        #(_row_keyModes,"right",5),  
                        #(_row_valueModes,"left",5),
                        #(_row_valueModes,"right",5),                          
                        (self.row_setValue,"left",0),
                        (self.row_setValue,"right",0),                          
                        (self.row_setValue,"bottom",2),
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),                        
                        ],
                  ac = [(_row_attrReport,"top",2,_header),
                        (_row_attrCreate,"top",2,_row_attrReport),
                        (_row_attrFlags,"top",2,_row_attrCreate),
                        (self.uiField_attrFilter,"top",2,_row_attrFlags),
                        
                        (_row_move,"bottom",0,_header_push),                                                
                        (_header_push,"bottom",2,self.row_setValue),
                        (self.row_setValue,"bottom",2,_row_cgm),                                                
                        #(_row_keyModes,"bottom",0,_row_valueModes),
                        #(_row_valueModes,"bottom",0,self.row_setValue),                        
                        (self.uiScrollList_attr,"top",2,self.uiField_attrFilter),
                        (self.uiScrollList_attr,"bottom",0,_row_move)],
                  attachNone = [(_row_cgm,"top")])	        
            
        _sel = mc.ls(sl=True)
        if _sel:
            self.uiFunc_load_selected()        
    #@cgmGEN.Timer
    def uiFunc_selectAttr(self): 
        _str_func = 'uiFunc_selectAttr'        
        if self.uiPopUpMenu_attr:
            self.uiPopUpMenu_attr.clear()
            self.uiPopUpMenu_attr.delete()
            self.uiPopUpMenu_attr = None
            
        _indices = self.uiScrollList_attr.getSelectedIdxs() or []
        log.debug("|{0}| >> indices: {1}".format(_str_func, _indices))                           
        if not _indices:
            return
        
        self.uiPopUpMenu_attr = mUI.MelPopupMenu(self.uiScrollList_attr,button = 3)
        _popUp = self.uiPopUpMenu_attr     
        
        
        _b_single = False
        if len(_indices)==1:_b_single = True
        
        _short = self._ml_nodes[0].p_nameShort
        _dynamic = False
        _numberChanges = False    
        _hidden = False
        _connectionsIn = False
        _connectionsOut = False
        _type = None
        
        _res_context = get_context(self,self.var_context.value,False)
        
        _primeNode =_res_context['primeNode']
        _l_primeAttrs = _res_context['attrs']
        _l_targets = _res_context['targets'] 
        _l_channelbox = _res_context['channelbox']
        _d_prime = None
        
        print(cgmGEN._str_subLine)
        self._l_attrsSelected = []
        
        
        for i,idx in enumerate(_indices):
            _a = self._l_attrsLoaded[idx]
            self._l_attrsSelected.append(_a)
            _d = ATTR.validate_arg(_short, _a)
            _v = ATTR.get(_d)
            log.info("{1}.{2} | value: {3}".format(_str_func, _short,_a, _v))
            if i == 0:
                _d_prime = _d
                _type = ATTR.get_type(_d_prime)
                if ATTR.is_dynamic(_d):
                    _dynamic = True
                    if ATTR.is_numeric(_d):
                        _numberChanges = True
                        log.debug("|{0}| >> {1}.{2}...setting up value change popup".format(_str_func, _short,_a))                           
                if ATTR.is_hidden(_d):
                    _hidden = True
                _l_connectionsIn = ATTR.get_driver(_d,skipConversionNodes=True)
                if _l_connectionsIn:
                    _connectionsIn = True
                _l_connectionsOut = ATTR.get_driven(_d,skipConversionNodes=True)
                if _l_connectionsOut:
                    _connectionsOut = True
        
                
        #>>>Pop up menu--------------------------------------------------------------------------------------------        
        mUI.MelMenuItem(_popUp,
                        label = "prime: {0}".format(self._l_attrsLoaded[_indices[0]]),
                        en=False)
        mUI.MelMenuItem(_popUp,
                        label ='Set Value',
                        ann = 'Enter value desired in pompt. If message, select object(s) to store',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}))
        mUI.MelMenuItemDiv(_popUp)
        
        if _type == 'enum':
            mUI.MelMenuItem(_popUp,
                            label ='Set Enum',
                            ann = 'Enter value desired in prompt',
                            c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'enumOptions'}))                
        
        
        #Standard Flags--------------------------------
        _flags = mUI.MelMenuItem(_popUp, subMenu = True,
                                label = 'Standard Flags')  
        
        mUI.MelMenuItem(_flags,
                        label ='Lock and Hide',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'lock':True,'hidden':True}))         
        mUI.MelMenuItem(_flags,
                        label ='Unlock and Show',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'lock':False,'hidden':False}))         
        
        _l_boolToMake = ['keyable','lock','hidden']
        
        
        for item in _l_boolToMake:
            _menu = mUI.MelMenuItem(_flags, subMenu = True,
                                label = item.capitalize())
            mUI.MelMenuItem(_menu,
                        label ='True',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{item:True}))        
            mUI.MelMenuItem(_menu,
                        label ='False',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{item:False}))    
        
        
        #Connections --------------------------------
        #_connections = mUI.MelMenuItem(_popUp, subMenu = True,
                                       #label = "Connections")
        
        _in = mUI.MelMenuItem(_popUp, subMenu = True,
                              label = "In")
        _out = mUI.MelMenuItem(_popUp, subMenu = True,
                               label = "Out")
        
        #...in -------------------------------------------------------------------------------------
        
        if _connectionsIn:
            _inShort = NAMES.get_short(_l_connectionsIn)
            _d_in = ATTR.validate_arg(_l_connectionsIn)
            mUI.MelMenuItem(_in,
                            en = False,
                            label = "Driver: " + NAMES.get_short(_l_connectionsIn))
            
            mUI.MelMenuItem(_in,
                            c = cgmGEN.Callback(mc.select,_l_connectionsIn),
                            ann = 'Select connection: {0}'.format(_inShort),
                            label = 'Select')
            mUI.MelMenuItem(_in,
                            c = cgmGEN.Callback(self.uiFunc_load,_d_in['node'],_d_in['attr']),
                            ann = 'Load connection: {0}'.format(_inShort),
                            label = 'Load')            
            mUI.MelMenuItem(_in,
                            c = cgmGEN.Callback(self.uiFunc_breakConnection,_d_prime['combined']),                                            
                            ann = 'Break connection: {0}'.format(_inShort),
                            label = 'Break')          
        
        
        '''_set2 = mUI.MelMenuItem(_in, subMenu = True,
                               ann = "Connect something in to our prime attr or node",
                               label = "Connect")'''
        _set = _in
        mUI.MelMenuItemDiv(_set)
        
        mUI.MelMenuItem(_set,
                        en=False,
                        label = "Connect to "+ _short + " attrs...")   
        
        _b_multiTarget = False    
        _b_severalTarget = False
        _len_targets = len(_l_targets)
        
        if _len_targets >= 1:
            if _l_targets[0] != _short:
                _b_severalTarget = True
                _b_multiTarget = True                
            if _len_targets >= 2:
                _b_multiTarget = True
            
        _b_multiAttr = False
        if len(_l_primeAttrs) > 1:
            _b_multiAttr = True
        
        _b_attrLenMatch = False
        _len_channelbox = len(_l_channelbox)
        _len_primAttrs = len(_l_primeAttrs)
        if _len_primAttrs and _len_channelbox and _len_primAttrs == _len_channelbox:
            log.debug("|{0}| >>  Have prime attrs and cb attrs, lens match".format(_str_func))                  
            _b_attrLenMatch = True            
            #for a in _l_primeAttrs:
                #if a in _l_channelbox:
                    #_b_attrLenMatch = False
                    #break
        elif _len_primAttrs == 1 and _l_channelbox:
            log.debug("|{0}| >>  1 prime attr and channel box".format(_str_func))                              
            _children = ATTR.get_children(_short,_l_primeAttrs[0])
            if len(_children) == _len_channelbox:
                _b_attrLenMatch = True
        else:
            log.debug("|{0}| >> Didn't hit match check".format(_str_func))                              
            
        log.debug("|{0}| >> _b_attrLenMatch: {1}".format(_str_func,_b_attrLenMatch))   
        
        _l_a = _l_primeAttrs + _l_channelbox
        _l_a = LISTS.get_noDuplicates(_l_a)
        
        if _l_primeAttrs and _l_targets:
            for a in ['all'] + _l_a:
                if a == 'all':
                    _all =  mUI.MelMenuItem(_set, subMenu = True,
                                            en = _b_multiTarget,
                                            ann = "Connect all primeAttrs to primeNode {0} from target".format(_short),
                                            label = 'From all')
                    if _b_multiTarget:                
                        for o in _l_targets:
                            if o != _short:
                                _t_short = NAMES.get_base(o)
                                _oMenu = mUI.MelMenuItem(_all,
                                                         ann = "Connect all to: {0}".format(o),
                                                         c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'connectToPrime','driver':[_t_short]}),                                                     
                                                         label = _t_short) 
                    _cb =  mUI.MelMenuItem(_set, subMenu = True,
                                           en = _b_attrLenMatch,
                                           ann = "Connect primeAttrs of primeNode {0} from target's channelbox attrs: {1}".format(_short,_l_channelbox),
                                           label = 'From Channelbox ({0})'.format(_len_channelbox))
                    if _b_attrLenMatch:                    
                        for o in _l_targets:
                            _t_short = NAMES.get_base(o)
                            _oMenu = mUI.MelMenuItem(_cb,
                                                     ann = "Connect all from channelbox of: {0}".format(o),
                                                     c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'connectToPrimeFromChannelbox','driver':_t_short}),                                                     
                                                     label = _t_short)                         
                elif _b_multiAttr:
                    _primeAttr = mUI.MelMenuItem(_set, subMenu = True,
                                                 ann = "Connect to primeNode {0}.{1}".format(_short,a),
                                                 label = a)
                    mUI.MelMenuItem(_primeAttr,
                                    en=False,
                                    label = "Driver")                  
                    for o in _l_targets:
                        _t_short = NAMES.get_base(o)
                        _oMenu = mUI.MelMenuItem(_primeAttr, subMenu = True,
                                                 ann = "Connect in selected attribute or primaryAttr to others",
                                                 label = _t_short)
                        for a1 in _l_primeAttrs:
                            if _short == o and a1 == a:
                                continue
                            if a in ATTR.get_children(_short,a1):
                                continue
                            mUI.MelMenuItem(_oMenu,
                                            ann = "Connect in selected attribute or primaryAttr to others",
                                            c = cgmGEN.Callback(self.uiFunc_connect,"{0}.{1}".format(o,a1),"{0}.{1}".format(_short,a)),                                            
                                            label = a1)                    
                    
            
            
        #...Out -------------------------------------------------------------------------------------
        #mUI.MelMenuItem(_out, 
                        #label = "Set")
        if _connectionsOut:
            mUI.MelMenuItem(_out,
                            en=False,
                            label = "Driven from primeAttrs({0})".format(_len_primAttrs))                 
            mUI.MelMenuItemDiv(_out)
            for _p in _l_connectionsOut:
                _outShort = NAMES.get_short(_p)
                log.debug("|{0}| >> connectOut...{1} | short: {2}".format(_str_func, _p, _outShort))
                
                _d_out = ATTR.validate_arg(_p)
                _outMenu = mUI.MelMenuItem(_out,subMenu = True,
                                           label = _outShort)
        
                mUI.MelMenuItem(_outMenu,
                                c = cgmGEN.Callback(mc.select,_l_connectionsOut),
                                ann = 'Select connection: {0}'.format(_outShort),
                                label = 'Select')
                mUI.MelMenuItem(_outMenu,
                                c = cgmGEN.Callback(self.uiFunc_load,_d_out['node'],_d_out['attr']),
                                ann = 'Load connection: {0}'.format(_outShort),
                                label = 'Load')            
                mUI.MelMenuItem(_outMenu,
                                c = cgmGEN.Callback(self.uiFunc_breakConnection,_p),                                            
                                ann = 'Break connection: {0}'.format(_outShort),
                                label = 'Break')   
        
        mUI.MelMenuItemDiv(_out)
        mUI.MelMenuItem(_out,
                        en=False,
                        label = "Connect from "+ _short + " attrs...")
        
        
        if _l_primeAttrs and _l_targets:
            for a in ['all'] + _l_a:
                if a == 'all':
                    _all =  mUI.MelMenuItem(_out, subMenu = True,
                                            en = _b_multiTarget,
                                            ann = "Connect all primeAttrs to primeNode {0} from target".format(_short),
                                            label = 'To all')
                    if _b_multiTarget:                
                        for o in _l_targets:
                            if o != _short:
                                _t_short = NAMES.get_base(o)
                                _oMenu = mUI.MelMenuItem(_all,
                                                         ann = "Connect all to: {0}".format(o),
                                                         c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'connectFromPrime','driven':[_t_short]}),                                                     
                                                         label = _t_short) 
                        mUI.MelMenuItem(_all,
                                        en = _b_severalTarget,
                                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'connectFromPrime','driven':_l_targets}),                                                                                             
                                        ann = "Connect all selected attribute or primaryAttr to others",
                                        label = 'All targets')   
                                
                    _cb =  mUI.MelMenuItem(_out, subMenu = True,
                                           en = _b_attrLenMatch,
                                           ann = "Connect primeAttrs of primeNode {0} to target's channelbox attrs: {1}".format(_short,_l_channelbox),
                                           label = 'To Channelbox ({0})'.format(_len_channelbox))
                    
                    if _b_attrLenMatch:                    
                        for o in _l_targets:
                            _t_short = NAMES.get_base(o)
                            _oMenu = mUI.MelMenuItem(_cb,
                                                     ann = "Connect all to channelbox of: {0}".format(o),
                                                     c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'connectFromPrimeToChannelbox','driven':[_t_short]}),                                                     
                                                     label = _t_short)  
                        mUI.MelMenuItem(_cb,
                                        en = _b_severalTarget,
                                        ann = "Connect to each selected objects channelbox",
                                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'connectFromPrimeToChannelbox','driven':_l_targets}),                                                                                             
                                        label = 'All targets')                           
                            
                elif _b_multiAttr:
                    _primeAttr = mUI.MelMenuItem(_out, subMenu = True,
                                                 ann = "Connect to primeNode {0}.{1}".format(_short,a),
                                                 label = a)
                    mUI.MelMenuItem(_primeAttr,
                                    en=False,
                                    label = "Driven")                  
                    for o in _l_targets:
                        _t_short = NAMES.get_base(o)
                        _oMenu = mUI.MelMenuItem(_primeAttr, subMenu = True,
                                                 ann = "Connect in selected attribute or primaryAttr to others",
                                                 label = _t_short)
                        for a1 in _l_primeAttrs:
                            if _short == o and a1 == a:
                                continue
                            if a in ATTR.get_children(_short,a1):
                                continue
                            mUI.MelMenuItem(_oMenu,
                                            ann = "Connect in selected attribute or primaryAttr to others",
                                            c = cgmGEN.Callback(self.uiFunc_connect,"{0}.{1}".format(_short,a),"{0}.{1}".format(o,a1)),                                            
                                            label = a1)  
                    _all = mUI.MelMenuItem(_primeAttr, subMenu = True,
                                           ann = "Connect out selected attribute or primaryAttr to others",
                                           label = 'All targets')
                    for a1 in _l_primeAttrs:
                        mUI.MelMenuItem(_all,
                                        ann = "Connect in selected attribute or primaryAttr to others",
                                        c = cgmGEN.Callback(self.uiFunc_connect,"{0}.{1}".format(_short,a),"{0}.{1}".format(o,a1)),                                            
                                        label = a1)                    
        
        
            
        #Name --------------------------------
        _menu = mUI.MelMenuItem(_popUp,subMenu = True, 
                                ann="Only active with single attribute selection",
                                l='Name')
        mUI.MelMenuItem(_menu,
                        en = _dynamic * _b_single,
                        label ='Rename',
                        ann = 'Only valid for user attributes',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'rename'}))                
        
        mUI.MelMenuItem(_menu,
                        en = _b_single,
                        label ='Alias',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'alias'}))
        mUI.MelMenuItem(_menu,
                        en = _b_single,
                        label ='Nice',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'nameNice'}))            
    
        #Values --------------------------------        
        _l = ['default','min','max','softMin','softMax']
        _menu = mUI.MelMenuItem(_popUp,subMenu = True, 
                                en = _numberChanges,
                                ann="Only userDefined numeric attributes supported",                                
                                l='Numeric')
        if _numberChanges:
            for item in _l:
                mUI.MelMenuItem(_menu,
                                label =item.capitalize(),
                                c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':item})) 
                    
                
        #Values --------------------------------        
        #_l = ['duplicate','copyTo','copyTo connect back','copyTo connect','connectTo','moveUp','moveDown']
        _l = ['duplicate']
        
        _d_utils = {'duplicate':'Duplicate the attribute including values, connections to the same object',
              }
        _menu = mUI.MelMenuItem(_popUp,subMenu = True, 
                                l='Utilities')
        
        _l_addTypes = ['string','float','enum','vector','int','bool','message']
        _add = mUI.MelMenuItem(_menu,subMenu = True, 
                               l='add')
        for t in _l_addTypes:
            mc.menuItem(parent=_add,
                        l=t,
                        ann = "Add a {0} attribute to the loaded object".format(t),
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'addAttr','type':t}))                         
                        #c = cgmGEN.Callback(uiPrompt_addAttr,t))
            
        
        _convert = mUI.MelMenuItem(_menu,subMenu = True, 
                                   en = _dynamic,                                   
                                   l='convert')
        for t in _l_addTypes:
            mc.menuItem(parent=_convert,
                        l=t,
                        ann = "Convert select attributes to type: {0}".format(t),                        
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'convert{0}'.format(t.capitalize())})) 
        
        _copy = mUI.MelMenuItem(_menu,subMenu = True, 
                                #en = _dynamic,                                   
                                l='copy')
        for t in ['to','connectBack','connectTo']:
            mc.menuItem(parent=_copy,
                        l=t,
                        ann = "Copy selected attribute by {0}".format(t),                        
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'copy{0}'.format(t.capitalize())})) 
        
        
        for item,a in _d_utils.iteritems():
            if not _dynamic and item in ['copyTo','copyTo connect back','copyTo connect']:
                pass
            else:
                mUI.MelMenuItem(_menu,
                                label =item,
                                ann = a,
                                c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':item}))        

        mUI.MelMenuItem(_popUp,
                        en=_dynamic,
                        l='Delete',
                        ann='Only user defined attrs are deletable',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'delete'}),        
                        )           
    
        _l_toDo = ['min','max','softMin','softMax','default','alias','rename']
        
    def uiFunc_pushValue(self,**kws):
        _str_func = 'uiFunc_pushValue'
        _mode = kws.get('mode','current')
        _keyMode = self.var_keysMode.value
        _valuesMode = self.var_valuesMode.value
        _context = self.var_context.value
        
        log.info("|{0}| >> mode: {1} | context: {2} | keyMode: {3} | valuesMode: {4}".format(_str_func,_mode,_context,_keyMode,_valuesMode))        
        
        if _mode == 'current' and _valuesMode == 'each':
            log.warning("|{0}| >>  This doesn't do anything on current mode as each item already has these values.".format(_str_func))      
            return False
        
        
        #>>> Get our driven ------------------------------------------------------------------------------
        _res = get_context(self, self.var_context.value)
        _primeNode =_res['primeNode']
        _l_primeAttrs = _res['attrs']
        _l_targets = _res['targets']
        
        
        #>>Get Attribute values -----------------------------------------------------------------------------------
        _d_values = get_values(self, _res)
        cgmGEN.print_dict(_d_values,"Values",__name__)
                
        #>>> Bake ------------------------------------------------------------------------------        
        if _mode == 'current':
            if _valuesMode == 'each':
                log.warning("|{0}| >>  This doesn't do anything on current mode as each item already has these values.".format(_str_func))      
                """ for o, d in _d_values.iteritems():
                    for a,v in d.iteritems():
                        log.info("|{0}| >>  {1}.{2} --> {3}".format(_str_func,o,a,v))"""      
            else:
                for a,v in _d_values.iteritems():
                    log.debug("|{0}| >>  {1}.{2} --> {3}".format(_str_func,_primeNode,a,v))      
                    for o in _l_targets:
                        try:ATTR.set(o,a,v)
                        except Exception,err:
                            log.error("|{0}| >>  Failed to set: {1}.{2} --> {3} | {4}".format(_str_func,_primeNode,a,v,err))      
                            
        else:
            _d_keys = get_keys(self,_res,_mode)    
            cgmGEN.print_dict(_d_keys,"Processed keys",__name__)
            if _valuesMode == 'each':
                for o, l_keys in _d_keys.iteritems():
                    for k in l_keys:
                        for a,v in _d_values[o].iteritems():
                            log.info("|{0}| >>  f{1} : {2}.{3} --> {4}".format(_str_func,k,o,a,v))
                            try:ATTR.set_keyframe(o,a,v,k)
                            except Exception,err:
                                log.error("|{0}| >>  failed to set... f{1} : {2}.{3} --> {4} | {5}".format(_str_func,k,o,a,v, err))
                            
            else:
                if _valuesMode.endswith('Per'):
                    log.warning("|{0}| >>  Per mode....".format(_str_func))
                    initialTimeState = mc.currentTime(q=True)
                    
                    for o,l_keys in _d_keys.iteritems():
                        for k in l_keys:       
                            mc.currentTime(k)
                            _d_tmp = get_values(self, _res)
                            for a,v in _d_tmp.iteritems():
                                if o in _l_targets:
                                    log.info("|{0}| >>  f{1} : {2}.{3} --> {4}".format(_str_func,k,o,a,v))
                                    try:ATTR.set_keyframe(o,a,v,k)
                                    except Exception,err:
                                        log.error("|{0}| >>  failed to set... f{1} : {2}.{3} --> {4} | {5}".format(_str_func,k,o,a,v, err))
                                
                            
                    mc.currentTime(initialTimeState)
                    
                else:
                    for o,l_keys in _d_keys.iteritems():
                        for k in l_keys:
                            for a,v in _d_values.iteritems():
                                if o in _l_targets:
                                    log.info("|{0}| >>  f{1} : {2}.{3} --> {4}".format(_str_func,k,o,a,v))
                                    try:ATTR.set_keyframe(o,a,v,k)
                                    except Exception,err:
                                        log.error("|{0}| >>  failed to set... f{1} : {2}.{3} --> {4} | {5}".format(_str_func,k,o,a,v, err))
                                        
                                #try:ATTR.set(o,a,v)
                                #except Exception,err:
                                    #log.error("|{0}| >>  Failed to set: {1}.{2} --> {3} | {4}".format(_str_func,_primeNode,a,v,err))      

        self.uiFunc_updateScrollAttrList()
        return
            
    def uiFunc_channelBoxBridge(self):
        _str_func = 'uiFunc_channelBoxBridge'
        log.debug("|{0}| ...".format(_str_func))
        
        _res_context = get_context(self,'selection',True)

        _primeNode =_res_context['primeNode']
        _l_primeAttrs = _res_context['attrs']
        _l_targets = _res_context['targets']        
        _l_channelbox = _res_context['channelbox'] 
        
        if not _l_channelbox:
            raise ValueError,"Must have attributes selected from the channel box"
        if not len(_l_targets) > 1:
            raise ValueError,"Must have more than one target"
        
        for o in _l_targets[1:]:
            if o == _primeNode:pass
            log.debug(cgmGEN.logString_sub(_str_func,o))
            for a in _l_channelbox:
                log.debug(cgmGEN.logString_sub(_str_func,a))
                ATTR.copy_to(o,a,_primeNode,a, outConnections=False,inConnection=True,driven='source')
                
        
    def uiFunc_attrManage_fromScrollList(self,**kws):
        def simpleProcess(self, indicies, attrs, func,**kws):
            for i in indicies:
                _a = attrs[i]
                for mNode in self._ml_nodes:
                    try:
                        _short = mNode.p_nameShort
                        _d = ATTR.validate_arg(_short,_a)
                        if not _d:
                            log.warning("|{0}| >> not validated. skipping: {1}.{2}".format(_str_func, _short,_a))                           
                            continue
                        
                        func(_d,**kws)
                    except Exception,err:
                        log.error("|{0}| >> {1}.{2} failed to process: {3}".format(_str_func, _short,_a,err))            
        
        _str_func = 'attrManage_fromScrollList'
        _indices = self.uiScrollList_attr.getSelectedIdxs()
                
        _keyable = kws.get('keyable',None)
        _lock = kws.get('lock',None)
        _hidden = kws.get('hidden',None)
        _mode = kws.get('mode',None)
        _fromPrompt = None
        
        _res_context = get_context(self,self.var_context.value,False)

        _primeNode =_res_context['primeNode']
        _l_primeAttrs = _res_context['attrs']
        _l_targets = _res_context['targets']        
        _l_channelbox = _res_context['channelbox'] 
        
        if _indices:
            _d_baseAttr = ATTR.validate_arg(self._ml_nodes[0].mNode,self._l_attrsLoaded[_indices[0]])
        else:
            _d_baseAttr = False
            
        _aType = ATTR.get_type(_d_baseAttr)
        _str_base = NAMES.get_base(_d_baseAttr['combined'])
        _done = False
        #Get attr types...

        if _mode is not None:
            if _mode == 'delete':
                simpleProcess(self, _indices, self._l_attrsLoaded, ATTR.delete)
                _done = True             
            elif _mode == 'rename':
                _fromPrompt = uiPrompt_getValue("Enter Name","Primary attr: '{0}' | type: {1}".format(_str_base,_aType),_d_baseAttr['attr'])                
                if _fromPrompt is None:
                    log.error("|{0}| >>  Mode: {1} | No value gathered...".format(_str_func,_mode))      
                    return False
            elif _mode == 'enumOptions':
                _fromPrompt = uiPrompt_getValue("Enter EnumOptions ',' separated","Primary attr: '{0}' | type: {1}".format(_str_base,_aType),ATTR.get_enum(_d_baseAttr['combined']))                
                if _fromPrompt is None:
                    log.error("|{0}| >>  Mode: {1} | No value gathered...".format(_str_func,_mode))      
                    return False            
            elif _mode == 'addAttr':
                uiPrompt_addAttr(kws['type'],_l_targets)
                _done = True
            elif _mode == 'connectToPrime':
                _driver = [kws['driver'] ]
                
                for o in _driver:
                    for a in _l_primeAttrs:
                        try:
                            ATTR.connect("{0}.{1}".format(o,a), "{0}.{1}".format(_primeNode,a))
                        except Exception,err:
                            log.error("|{0}| >> {1}.{2} failed to process: {3}".format(_str_func, _primeNode,a,err))                   
                _done = True
            elif _mode == 'connectToPrimeFromChannelbox':
                _driver = [kws['driver'] ]
                len_primeAttrs = len(_l_primeAttrs)
                if len_primeAttrs == 1 and len_primeAttrs != len(_l_channelbox):
                    for o in _driver:
                        try:
                            for i,a in enumerate(ATTR.get_children(_d_baseAttr)):
                                ATTR.connect("{0}.{1}".format(o,_l_channelbox[i]),"{0}.{1}".format(_primeNode,a))                        
                        except Exception,err:
                            log.error("|{0}| >> {1}.{2} failed to process: {3}".format(_str_func, _primeNode,a,err))                    
                else:
                    for o in _driver:
                        for i,a in enumerate(_l_primeAttrs):
                            try:
                                ATTR.connect("{0}.{1}".format(o,_l_channelbox[i]),"{0}.{1}".format(_primeNode,a))
                            except Exception,err:
                                log.error("|{0}| >> {1}.{2} failed to process: {3}".format(_str_func, _primeNode,a,err))                   
                _done = True                
            elif _mode == 'connectFromPrime':
                _driven = kws['driven'] 
                for o in _driven:
                    for a in _l_primeAttrs:
                        try:
                            ATTR.connect("{0}.{1}".format(_primeNode,a),"{0}.{1}".format(o,a))
                        except Exception,err:
                            log.error("|{0}| >> {1}.{2} failed to process: {3}".format(_str_func, _primeNode,a,err))                   
                _done = True
            elif _mode == 'connectFromPrimeToChannelbox':
                _driven = kws['driven'] 
                len_primeAttrs = len(_l_primeAttrs)
                if len_primeAttrs == 1 and len_primeAttrs != len(_l_channelbox):
                    for o in _driven:
                        try:
                            for i,a in enumerate(ATTR.get_children(_d_baseAttr)):
                                ATTR.connect( "{0}.{1}".format(_primeNode,a),"{0}.{1}".format(o,_l_channelbox[i]))                        
                        except Exception,err:
                            log.error("|{0}| >> {1}.{2} failed to process: {3}".format(_str_func, _primeNode,a,err))                    
                else:
                    for o in _driven:
                        for i,a in enumerate(_l_primeAttrs):
                            try:
                                ATTR.connect("{0}.{1}".format(_primeNode,a),"{0}.{1}".format(o,_l_channelbox[i]))
                            except Exception,err:
                                log.error("|{0}| >> {1}.{2} failed to process: {3}".format(_str_func, _primeNode,a,err))                   
                _done = True                     
            elif _mode in ['alias','nameNice','duplicate','copyTo','copyConnectback','copyConnectto']:
                if _mode == 'alias':
                    _plug = ATTR.get_alias(_d_baseAttr)
                elif _mode == 'duplicate':
                    _plug = _d_baseAttr['attr']+'DUP'                 
                elif _mode == 'nameNice':
                    _plug = ATTR.get_nameNice(_d_baseAttr)
                else:
                    _plug = ATTR.get_nameLong(_d_baseAttr)
                _kws = {'title':"Enter {0}".format(_mode),'message':'Enter a new {0} name.'.format(_mode)}
                if _plug:
                    _kws['text'] = _plug
                
                _fromPrompt = uiPrompt_getValue(**_kws)   
                
                if _fromPrompt is None:
                    log.error("|{0}| >>  Mode: {1} | No value gathered...".format(_str_func,_mode))      
                    return False
                
                
            elif _mode in ['default','min','max','softMin','softMax']:
                _d_plugs = {'default':ATTR.get_default,'min':ATTR.get_min,'max':ATTR.get_max,
                            'softMin':ATTR.get_softMin,'softMax':ATTR.get_softMax}
                
                _plug = _d_plugs[_mode](_d_baseAttr)

                _kws = {'title':"Enter {0}".format(_mode),'message':'Enter a new {0}.'.format(_mode)}
                if _plug:
                    _kws['text'] = _plug
            
                _fromPrompt = uiPrompt_getValue(**_kws)   
            
                if _fromPrompt is None:
                    log.error("|{0}| >>  Mode: {1} | No value gathered...".format(_str_func,_mode))      
                    return False
                log.info(_fromPrompt)  
                
            elif _mode == 'value':
                if _aType == 'message':
                    _sel = mc.ls(sl=True)
                    if not _sel:
                        log.error("|{0}| >>  Mode: {1} | No selection".format(_str_func,_mode))                                                                       
                        return False
                    log.info("|{0}| >>  Mode: {1} | storing {2}".format(_str_func,_mode,_sel))  
                    #self._ml_nodes[0].__dict__[self._l_attrsToLoad[_indices[0]]] = _sel
                    ATTR.set_message(self._ml_nodes[0].mNode, self._l_attrsLoaded[_indices[0]], _sel)
                    _done = True
                else:
                    _fromPrompt = uiPrompt_getValue("Enter Value","Primary attr: '{0}' | type: {1} | v: {2}".format(_str_base,_aType, ATTR.get(_d_baseAttr)))
                    if _fromPrompt is None:
                        log.error("|{0}| >>  Mode: {1} | No value gathered...".format(_str_func,_mode))      
                        return False
                    else:
                        log.info("|{0}| >>  from prompt: {1} ".format(_str_func,_fromPrompt))  
                        
                    _fromPrompt = STRINGS.strip_invalid(_fromPrompt,'[]{}()', functionSwap = False, noNumberStart = False)
                    if ',' in _fromPrompt:
                        _fromPrompt = _fromPrompt.split(',')                
                    #log.info(_fromPrompt)  
                    
            elif _mode.startswith('convert'):
                _convertString = _mode.split('convert')[-1].lower()
                log.info("|{0}| >>  convert string: {1} ".format(_str_func,_convertString))                                                               
                
            elif _mode in ['moveUp','moveDown']:
                pass
            else:
                log.error("|{0}| >>  Mode: {1} | Not implented...".format(_str_func,_mode))                                               
                return False
            
        if _done:
            self.uiFunc_updateScrollAttrList()
            return True

        for i in _indices:
            _a = self._l_attrsLoaded[i]
            #for mNode in self._ml_nodes:
            for node in _l_targets:
                try:
                    _short = NAMES.get_short(node)
                    _d = ATTR.validate_arg(_short,_a)
                    log.info("|{0}| >> on...{1}.{2}".format(_str_func, _short,_a))                                                                   
                    
                    if _mode in ['duplicate','copyTo','copyConnectto','copyConnectback']:
                        if not _fromPrompt:raise ValueError,"Must have new name"
                        if _mode == 'duplicate':ATTR.copy_to(self._ml_nodes[0].mNode,_d['attr'],_d['node'], _fromPrompt,outConnections=False,inConnection = True)                                                 
                        if _mode == 'copyTo':ATTR.copy_to(self._ml_nodes[0].mNode,_d['attr'],_d['node'], _fromPrompt,outConnections=False,inConnection = True)
                        if _mode == 'copyConnectto':ATTR.copy_to(self._ml_nodes[0].mNode,_d['attr'],_d['node'], _fromPrompt,outConnections=False,inConnection = True,driven='target')
                        if _mode == 'copyConnectback':ATTR.copy_to(self._ml_nodes[0].mNode,_d['attr'],_d['node'], _fromPrompt,outConnections=False,inConnection = True,driven='source')                        
                        continue

                    #...the remainder of these happen after validation of attr
                    if not _d or not mc.objExists(_d['combined']):
                        log.warning("|{0}| >> not validated. skipping: {1}.{2}".format(_str_func, _short,_a))                           
                        continue
                    
                    if _keyable is not None:
                        log.warning("|{0}| >> {1}.{2} keyable: {3}".format(_str_func, _short,_a,_keyable))                                               
                        ATTR.set_keyable(_d,_keyable)
                    if _lock is not None:
                        log.warning("|{0}| >> {1}.{2} lock: {3}".format(_str_func, _short,_a,_lock))                           
                        ATTR.set_lock(_d,_lock)        
                    if _hidden is not None:
                        log.warning("|{0}| >> {1}.{2} hidden: {3}".format(_str_func, _short,_a,_hidden))                                               
                        ATTR.set_hidden(_d,_hidden)
                        
                    if _mode is not None:
                        if _mode == 'value':
                            _v = None
                            try:
                                _v = ATTR.validate_value(_d,value =_fromPrompt)
                            except Exception,err:
                                log.error("|{0}| >> {1}.{2} | Mode: {3} | Failed to validate value from prompt: {4} | err: {5}".format(_str_func, _short,_a,_mode,_fromPrompt,err))                                               
                                continue
                            if _v is not None:
                                ATTR.set(_d, value = _v)
                        elif _mode == 'enumOptions':
                            if ':' not in _fromPrompt:
                                raise ValueError,"enumOptions should be separated by ':'"
                            _v = '"'.split(_fromPrompt)
                            pprint.pprint([_fromPrompt,_v])
                            ATTR.set(_d, value = _fromPrompt)
                        elif _mode == 'alias':
                            if not _fromPrompt:_fromPrompt=False
                            ATTR.set_alias(_d, _fromPrompt)
                        elif _mode == 'nameNice':
                            if not _fromPrompt:_fromPrompt=False
                            ATTR.renameNice(_d, _fromPrompt)                            
                        elif _mode == 'rename':
                            if not _fromPrompt:raise ValueError,"Must have new name"
                            ATTR.rename(_d, _fromPrompt) 
                        elif _mode in ['moveUp','moveDown']:
                            if _mode == 'moveUp':
                                _direction = 0
                            else:
                                _direction = 1
                            if ATTR.is_dynamic(_d):
                                ATTR.reorder(_short, _a, _direction)
                            else:
                                log.error("|{0}| >> {1}.{2} | Mode: {3} | Attr must be userDefined to be dynamic".format(_str_func, _short,_a,_mode))                                                                               
                        
                        elif _mode in ['default','min','max','softMin','softMax']:
                            _d_plugs = {'default':ATTR.set_default,'min':ATTR.set_min,'max':ATTR.set_max,
                                        'softMin':ATTR.set_softMin,'softMax':ATTR.set_softMax}
                            if not _fromPrompt:_fromPrompt=False
                            else:_fromPrompt = float(_fromPrompt)
                            _d_plugs[_mode](_d,_fromPrompt)
                            
                        elif _mode.startswith('convert'):
                            if not ATTR.is_dynamic(_d):
                                log.error("|{0}| >> {1}.{2} | Mode: {3} | Not dynamic. Continuing to next...".format(_str_func, _short,_a,_mode))                                               
                            ATTR.convert_type(_d,_convertString) 
                            
                        else:
                            log.error("|{0}| >> {1}.{2} | Mode: {3} | Not implented or failed to meet criteria".format(_str_func, _short,_a,_mode))                                               
                            
                except Exception,err:
                    log.error("|{0}| >> {1}.{2} failed to process: {3}".format(_str_func, _short,_a,err))                                               
        self.uiFunc_updateScrollAttrList()
                    

def uiPrompt_addAttr(attrType = None, nodes = None, title = None, message = None, text = None, uiSelf = None, autoLoadFail = False):
    _str_func = 'uiPrompt_addAttr'
    if title is None:
        _title = 'Add {0} attrs...'.format(attrType)
    else:_title = title
    
    if nodes is None:
        nodes = mc.ls(sl=True)
    _str_nodes = ",".join([NAMES.get_base(n) for n in nodes])
    
    _d = {'title':_title, 'button':['OK','Cancel'], 'defaultButton':'OK', 'messageAlign':'center', 'cancelButton':'Cancel','dismissString':'Cancel'}
    if message is None:
        message = "Targets: {0}\nEnter new attr name. Multiples by comma".format(_str_nodes)
    _d['message'] = message
    if text is not None:
        _d['text'] = text
        
    result = mc.promptDialog(**_d)
    
    if result == 'OK':
        _v =  mc.promptDialog(query=True, text=True)
        _l_fails = []
        if ',' in _v:
            _attrs = [x.strip() for x in _v.split(',')]
            for a in _attrs:
                for node in nodes:
                    try:
                        ATTR.add(node, a, attrType,keyable = True, hidden = False)    
                    except Exception,err:
                        _l_fails.append(node)
                        log.error("|{0}| >> Add failure. Node: {1} | Attr: {2} | Type: {3} | err: {4}".format(_str_func,node, a, attrType,err))
        else:
            for node in nodes:
                try:
                    ATTR.add(node, _v, attrType,keyable = True, hidden = False)
                except Exception,err:
                    _l_fails.append(node)
                    log.error("|{0}| >> Add failure. Node: {1} | Attr: {2} | Type: {3} | err: {4}".format(_str_func,node, _v, attrType,err))
                    
        if autoLoadFail and _l_fails:
            mc.select(_l_fails)

            try:ui()
            except Exception,err:
                log.error(err)
    else:
        log.info("|{2}| >> Add {0} attr cancelled. Nodes: {1}".format(attrType,_str_nodes,_str_func))
        return None     
    
def uiPrompt_getValue(title = None, message = None, text = None, uiSelf = None):
    _str_func = 'uiPrompt_getValue'
    if title is None:
        _title = 'Need data...'
    else:_title = title
    
    
    _d = {'title':_title, 'button':['OK','Cancel'], 'defaultButton':'OK', 'messageAlign':'center', 'cancelButton':'Cancel','dismissString':'Cancel'}
    if message is None:
        message = "Getting values is better with messages..."
        
    _d['message'] = message
    if text is not None:
        _d['text'] = text
        
    result = mc.promptDialog(**_d)
    
    if result == 'OK':
        _v =  mc.promptDialog(query=True, text=True)
        
        return _v
    else:
        log.info("|{0}| >> Gather value cancelled".format(_str_func))
        return None     
        
        
def uiRow_attributeTypes(self,parent):	
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Attr type row
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    self.attrTypes = ['string','float','int','double3','bool','enum','message']
    attrShortTypes = ['str','float','int','[000]','bool','enum','msg']

    self.rc_attrTypes = mUI.MelRadioCollection()

    #build our sub section options
    _row = mUI.MelHLayout(parent,ut='cgmUISubTemplate',padding = 5)
    for cnt,item in enumerate(self.attrTypes):
        if item == 'float':_rb = True
        else:_rb = False
        self.rc_attrTypes.createButton(_row,label=attrShortTypes[cnt],sl=_rb)
                                                                      #onCommand = Callback(self.CreateAttrTypeOptionVar.set,item)))
        mUI.MelSpacer(_row,w=2)

    #if self.CreateAttrTypeOptionVar.value:
        #mc.radioCollection(self.rc_attrTypes ,edit=True,sl= (self.rc_attrTypeChoices[ self.attrTypes.index(self.CreateAttrTypeOptionVar.value) ]))

    _row.layout()
    

def uiScrollListFUNC_update(self,menu,selectAttr = None):
    def uiAttrUpdate(item):
        #uiSelectActiveAttr(self,item)
        pass
    
    menu.clear()
    attrs=[]
    for a in self.loadAttrs:
        if a not in ['attributeAliasList']:
            attrs.append(a)

    if attrs:
        if self.SortModifyOptionVar.value:
            attrs.sort()    
        # Get the attributes list
        if attrs:
            for a in attrs:
                menu.append(a)
            #uiSelectActiveAttr(self,attrs[-1])
        else:
            menu.clear()
        #Select if we can
        if selectAttr in attrs:            
            index = attrs.index(selectAttr)
            self.ObjectAttributesOptionMenu.selectByIdx(index ) 
            #uiSelectActiveAttr(self,selectAttr)
        else:
            pass
            #uiSelectActiveAttr(self,attrs[0])
        menu(edit=True,cc = uiAttrUpdate)    
    
    
def uiUpdateObjectAttrMenu(self,menu,selectAttr = False):
    """ 
    Updates the attribute menu of a loaded object in the modify section

    Keyword arguments:
    menu(string) -- Menu name
    selectAttr(string) -- Name of an attr (False ignores)
    """ 
    def uiAttrUpdate(item):
        uiSelectActiveAttr(self,item)

    menu.clear()
    attrs=[]
    for a in self.loadAttrs:
        if a not in ['attributeAliasList']:
            attrs.append(a)

    if attrs:
        if self.SortModifyOptionVar.value:
            attrs.sort()    
        # Get the attributes list
        if attrs:
            for a in attrs:
                menu.append(a)
            uiSelectActiveAttr(self,attrs[-1])
        else:
            menu.clear()
        #Select if we can
        if selectAttr in attrs:            
            index = attrs.index(selectAttr)
            self.ObjectAttributesOptionMenu.selectByIdx(index ) 
            uiSelectActiveAttr(self,selectAttr)
        else:
            uiSelectActiveAttr(self,attrs[0])
        menu(edit=True,cc = uiAttrUpdate)
        
        
def get_keys(self, context = None, mode = 'all', report = False):
    """
    :parameters
        self(instance): cgmMarkingMenu

    :returns
        info(dict)
    """   
    _str_func = 'get_keys'
    
    
    if type(context) in [dict]:
        _res_context = context
    else:
        _res_context = get_context(self,context,False)

    _primeNode =_res_context['primeNode']
    _l_primeAttrs = _res_context['attrs']
    _l_targets = _res_context['targets']
    
    _mode = self.var_keysMode.value
    
    _d_annos = {'selectedAttrs':'Only keys on selected attrs',
                'primeNode':'Any keys on prime node',
                'each':'Each contextual nodes will take values on own keys',
                'combined':'Combine keys of conextual nodes and prime'}       
    
    
    _d_keys = {}
    
    log.info("|{0}| >> mode: {1}".format(_str_func,_mode))  
    
    if _mode in ['each']:
        for o in _l_targets:
            _d_keys[o] = SEARCH.get_key_indices_from(o,mode)
    elif _mode in ['primeNode']:
        _keys = SEARCH.get_key_indices_from(_primeNode,mode)
        for o in _l_targets:
            _d_keys[o] = _keys
    elif _mode in ['combined']:
        _l_keys = []
        for o in _l_targets:
            _l_keys.extend(SEARCH.get_key_indices_from(o,mode))
        _l_keys = LISTS.get_noDuplicates(_l_keys)
           
        for o in _l_targets:
            _d_keys[o] = _l_keys
        
            #_keys = _source + _loc
            #_keys = lists.returnListNoDuplicates(_keys)            
        pass
    else:
        log.error("|{0}| >> unknown mode:{1} ".format(_str_func,_mode))  

    
    if report:
        log.info(cgmGEN._str_hardLine)
        cgmGEN.print_dict(_d_keys,"Keys",__name__)
        
    for o,keys in _d_keys.iteritems():
        if not keys:log.error("|{0}| >> Failed to find keys for: {1} | mode: {2} ".format(_str_func,o,_mode))       
        
    return _d_keys
        
def get_values(self, context = None, report = False):
    """
    :parameters
        self(instance): cgmMarkingMenu

    :returns
        info(dict)
    """   
    _str_func = 'get_values'

    if type(context) in [dict]:
        _res_context = context
    else:
        _res_context = get_context(self,context,False)

    _primeNode =_res_context['primeNode']
    _l_primeAttrs = _res_context['attrs']
    _l_targets = _res_context['targets']
    
    _mode = self.var_valuesMode.value
    
    _d_values = {}
    
    if _mode in ['primeAttr','primeAttrPer']:
        log.info("|{0}| >> primeAttr mode: {1}.{2} ".format(_str_func,_primeNode, _l_primeAttrs[0]))  
        
        _v = ATTR.get(_primeNode,_l_primeAttrs[0])
        _d_values[_l_primeAttrs[0]] = _v 
        for a in _l_primeAttrs[1:]:
            _a = "{0}.{1}".format(_primeNode,a)     
            try:
                _validated_v = ATTR.validate_value(_primeNode,a,_v)
                if _validated_v is not None:
                    _d_values[a] = _validated_v  
            except:
                log.info("|{0}| >> Attr failed to validate value: {1} | for attr: {2}.{3}".format(_str_func,_v,_primeNode,a))  
                
            
    elif _mode in ['primeNode','primeNodePer']:
        log.info("|{0}| >> primeNode mode: {1} ".format(_str_func,_primeNode))
        for a in _l_primeAttrs:
            _a = "{0}.{1}".format(_primeNode,a)
            _d_values[a] = ATTR.get(_a)
    else:
        log.info("|{0}| >> each object mode. Targets: {1} ".format(_str_func,len(_l_targets)))  
        for o in _l_targets:
            _d_values[o] = {}
            _d = _d_values[o]
            for a in _l_primeAttrs:
                _d[a] = ATTR.get(o,a)
    
    if report:
        log.info(cgmGEN._str_hardLine)
        cgmGEN.print_dict(_d_values,"Values",__name__)

    return _d_values

def Callback(uiInstance, func, *a,**kws):
    cgmGEN.Callback(func,*a,**kws)
    uiInstance.uiFunc_updateScrollAttrList()

def get_context(self, context = None, report = False):
    """
    :parameters
        self(instance): cgmMarkingMenu

    :returns
        info(dict)
    """   
    _str_func = 'get_context'
    
    _l_targets = []
    _sel = mc.ls(sl=True)
    _sel_attrs = SEARCH.get_selectedFromChannelBox(True) or []

    #_primeNode -----------------------------------------------------------------------------------
    _primeNode = None
    _trans = False
    _type = None
    if self._ml_nodes:
        _primeNode = self._ml_nodes[0].mNode
    elif _sel:
        _primeNode = _sel[0]
    else:
        log.error("|{0}| >> No nodes stored. Nothing selected. Try again. ".format(_str_func))  
        return False
    
    #_primeAttrs -----------------------------------------------------------------------------------
    _l_primeAttrs = []
    _indices = self.uiScrollList_attr.getSelectedIdxs()
    if _indices:
        for i in _indices:
            _l_primeAttrs.append(self._l_attrsLoaded[i])
    elif _sel_attrs:
        _l_primeAttrs = _sel_attrs
    else:
        log.error("|{0}| >> Attrs found. using all settable ".format(_str_func))  
        _l_primeAttrs = mc.listAttr(_primeNode, settable = True)
        
    #if _sel_attrs:
        #_l_primeAttrs.extend(_sel_attrs)
        #_l_primeAttrs = LISTS.get_noDuplicates(_l_primeAttrs)
        
    if _primeNode:
        _type = VALID.get_mayaType(_primeNode)
        _trans = VALID.is_transform(_primeNode)
    if context == 'loaded':
        if not self._ml_nodes:
            log.error("|{0}| >> No nodes stored to ui. ".format(_str_func))            
            return False
        
        for mNode in self._ml_nodes:
            _l_targets.append(mNode.mNode)
            #for a in _l_primeAttrs:
                #_l_targets.append( "{0}.{1}".format(mNode.mNode, a))
    else:
        _l_targets = CONTEXT.get_list(context,None,_trans)#..._type
        
    if report:
        log.info(cgmGEN._str_hardLine)
        log.info("|{0}| >> context: {1}.... ".format(_str_func,context))
        log.info("|{0}| >> primeNode: {1} | type: {2}.... ".format(_str_func,_primeNode,_type))
        log.info("|{0}| >> primeAttrs({1})... ".format(_str_func,len(_l_primeAttrs)))
        
        for i,a in enumerate(_l_primeAttrs):
            log.info("|{0}| >> {1} | {2}".format(_str_func,i,a))        
        log.info(cgmGEN._str_subLine)    
        log.info("|{0}| >> targets({1})... ".format(_str_func,len(_l_targets)))        
        for i,o in enumerate(_l_targets):
            log.info("|{0}| >> {1} | {2}".format(_str_func,i,NAMES.get_short(o)))
            
        log.info("|{0}| >> channelbox attrs({1})... ".format(_str_func,len(_sel_attrs)))                    
        for i,a in enumerate(_sel_attrs):
            log.info("|{0}| >> {1} | {2}".format(_str_func,i,a))
    return {'primeNode':_primeNode,'attrs':_l_primeAttrs,'targets':_l_targets,'channelbox':_sel_attrs}
        
    
def contextual_set(attr = None, value = None, context = 'selection', mType = None):
    """
    
    
    :parameters
        self(instance): cgmMarkingMenu

    :returns
        info(dict)
    """   
    _str_func = "contextual_set"
    _context = context.lower()
    _l_context = CONTEXT.get_list(_context, mType)
    
    log.debug("|{0}| >> attr: {1} | value: {2} | mType: {3} | context: {4}".format(_str_func,attr,value,mType,_context))             
        
    for o in _l_context:
        try:
            ATTR.set(o,attr,value)
        except Exception,err:
            log.error("|{0}| >> set fail. obj:{1} | attr:{2} | value:{3} | error: {4} | {5}".format(_str_func,NAMES.get_short(o),attr,value,err,Exception))
    
    mc.select(_l_context)
    return True    
        

