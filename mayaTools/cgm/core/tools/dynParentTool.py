"""
------------------------------------------
dynParentTool: cgm.core.tools
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
# From Python =============================================================
import copy
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


import maya.cmds as mc


import cgm.core.classes.GuiFactory as cgmUI
from cgm.core import cgm_RigMeta as cgmRigMeta

reload(cgmUI)
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

#>>> Root settings =============================================================
__version__ = 'Alpha 1.0.05232017'

#__toolURL__ = 'www.cgmonks.com'
#__author__ = 'Josh Burton'
#__owner__ = 'CG Monks'
#__website__ = 'www.cgmonks.com'
#__defaultSize__ = 375, 350


class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmDynParentTool_ui'    
    WINDOW_TITLE = 'cgmDynParentTool - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 250,300
    #_checkBoxKeys = ['shared','default','user','others']
    __modes = 'space','orient','follow'
    
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
            #self.create_guiOptionVar('valuesMode',  defaultValue = 'primeNode')                        
            #self.create_guiOptionVar('context',  defaultValue = 'loaded')            
            self.uiScrollList_parents = False

    def build_menus(self):
        #self.uiMenu_context = mUI.MelMenu( l='Context', pmc=self.buildMenu_context)           

        self.uiMenu_help = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)           
    
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
    
        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("http://www.cgmonks.com/tools/maya-tools/cgmmarkingmenu/attrtools-2-0/");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )      
                
    def uiFunc_clear_loaded(self):
        _str_func = 'uiFunc_clear_loaded'  
        self._d_attrs = {}
        self._ml_nodes = []
           
        self.uiReport_objects()
        self.uiScrollList_attr.clear()
        self._d_uiCheckBoxes['shared'](edit = True, en=True)
        

    def uiFunc_load_selected(self, bypassAttrCheck = False):
        _str_func = 'uiFunc_load_selected'  
        self._ml_parents = []
        self._mNode = False
        
        _sel = mc.ls(sl=True)
            
        #Get our raw data
        if _sel:
            mNode = cgmMeta.validateObjArg(_sel[0])
            _short = mNode.p_nameShort            
            log.debug("|{0}| >> Target: {1}".format(_str_func, _short))
            self._mNode = mNode
            
            self._utf_obj(edit=True, l=_short)
            
        else:
            log.warning("|{0}| >> Nothing selected.".format(_str_func))            
            self._utf_obj(edit=True, l='')      
                
        
        self.uiReport_do()
        #self.uiScrollList_attr.clear()        
        #self.uiFunc_updateScrollAttrList()
        

    def uiFunc_updateDynParentDisplay(self):
        _str_func = 'uiFunc_updateDynParentDisplay'  
        self.uiScrollList_parents.clear()
        
        if not self._mNode:
            log.info("|{0}| >> No target.".format(_str_func))                        
            #No obj
            self._utf_obj(edit=True, l='')
            
            for o in self._l_toEnable:
                o(e=True, en=False)
                
        elif not ATTR.get_message(self._mNode.mNode,'dynParentGroup'):
            log.info("|{0}| >> No dynParentGroup".format(_str_func))                        
            #Not dynParentGroup
            _short = self._mNode.p_nameShort            
            self._utf_obj(edit=True, l=_short)
            
            self.uiField_report(edit=True, label = 'No dynParentGroup detected')
            
            for o in self._l_toEnable:
                o(e=True, en=False)                
        else:
            log.info("|{0}| >> dynParentGroup detected...".format(_str_func))
            _d = get_dict(self._mNode.mNode)
            if _d:
                _l_report = ["mode: {0}".format(_d['mode']),'parents: {0}'.format(len(_d['dynParents']))]
                self.uiField_report(edit=True, label = 'DynGroup: {0}'.format(' | '.join(_l_report)))            
                
            else:    
                self.uiField_report(edit=True, label = 'DynGroup found')            
            for o in self._l_toEnable:
                o(e=True, en=True)            
        
    def uiFunc_updateScrollParentList(self):
        _str_func = 'uiFunc_updateScrollParentList'          
        self._l_attrsToLoad = []
        _d_processed = {}
        
        if not self._ml_nodes:
            return False      
        
        #for k in ui._checkBoxKeys:
            #log.info("{0} : {1}".format(k, self._d_uiCheckBoxes[k].getValue()))
        #['shared','keyable','transforms','user','other']
        
        _shared = self._d_uiCheckBoxes['shared'].getValue()
        #_keyable = self._d_uiCheckBoxes['keyable'].getValue()
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
                    self.uiScrollList_attr.append(" // ".join(_l_report))
                except Exception,err:
                    log.info("|{0}| >> {1}.{2} | failed to query. Removing. err: {3}".format(_str_func, _short, a, err))  
                    self._l_attrsToLoad.remove(a)
                log.debug("|{0}| >> {1} : {2}".format(_str_func, _short, a))  
        except Exception,err:
            try:cgmUI.doEndMayaProgressBar(_progressBar)
            except:pass
            raise Exception,err

        #menu(edit=True,cc = uiAttrUpdate)
        cgmUI.doEndMayaProgressBar(_progressBar)
        
        
        #Reselect
        if self._l_attrsSelected:
            _indxs = []
            for a in self._l_attrsSelected:
                log.debug("|{0}| >> Selected? {1}".format(_str_func,a))                              
                if a in self._l_attrsToLoad:
                    self.uiScrollList_attr.selectByIdx(self._l_attrsToLoad.index(a))
                    
                    
                    
        return False
    
        if self.SourceObject and self.SourceObject.update(self.SourceObject.nameLong):
            if self.HideNonstandardOptionVar.value:
                self._l_attrsToLoad.extend(self.SourceObject.transformAttrs)
                self._l_attrsToLoad.extend(self.SourceObject.userAttrs)
                self._l_attrsToLoad.extend(self.SourceObject.keyableAttrs)
    
                self._l_attrsToLoad = lists.returnListNoDuplicates(self._l_attrsToLoad)
            else:
                self._l_attrsToLoad.extend( mc.listAttr(self.SourceObject.nameLong) )
    
            if self.HideTransformsOptionVar.value:
                for a in self.SourceObject.transformAttrs:
                    if a in self._l_attrsToLoad:
                        self._l_attrsToLoad.remove(a)
    
            if self.HideUserDefinedOptionVar.value:
                for a in self.SourceObject.userAttrs:
                    if a in self._l_attrsToLoad:
                        self._l_attrsToLoad.remove(a)	
    
            if self.HideParentAttrsOptionVar.value:
                for a in self._l_attrsToLoad:
                    if (mc.attributeQuery(a, node = self.SourceObject.nameLong, listChildren=True)) is not None:
                        self._l_attrsToLoad.remove(a)
    
            if self.HideCGMAttrsOptionVar.value:
                buffer = []
                for a in self._l_attrsToLoad:
                    if 'cgm' not in a:
                        buffer.append(a)
                if buffer:
                    self._l_attrsToLoad = buffer
    
        if self._l_attrsToLoad:	    
            return True
    
        return False        
            
        
    def uiReport_do(self):
        if self._mNode:
            self.uiFunc_updateDynParentDisplay()
                
        else:
            self.uiField_report(edit=True, label = '...')
            
        return
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
        _header_top = cgmUI.add_Header('cgmDynParentGroup',overrideUpper=True)        

        #>>>Objects Load Row ---------------------------------------------------------------------------------------
        _row_objLoad = mUI.MelHSingleStretchLayout(_MainForm,ut='cgmUITemplate',padding = 5)        
        
        mUI.MelSpacer(_row_objLoad,w=20)
        mUI.MelLabel(_row_objLoad, 
                     l='dynChild:')
        
        _utf_objLoad = mUI.MelLabel(_row_objLoad,ut='cgmUITemplate',l='',
                                    en=False)
        self._utf_obj = _utf_objLoad
        cgmUI.add_Button(_row_objLoad,'<<',
                         cgmGEN.Callback(self.uiFunc_load_selected),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Load selected object.")   
        
        
        _row_objLoad.setStretchWidget(_utf_objLoad)
        mUI.MelSpacer(_row_objLoad,w=20)
        
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
        
        
        
        #>>>Push Values header ---------------------------------------------------------------------------------------        
        mc.setParent(_MainForm)        
        _header_parents = cgmUI.add_Header('Parents')        
        
        #>>> Parents list ---------------------------------------------------------------------------------------
        self.uiScrollList_parents = mUI.MelObjectScrollList(_MainForm, allowMultiSelection=True,en=False)
                                                            #dcc = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}),
                                                            #selectCommand = self.uiFunc_selectAttr)

        self._l_toEnable.append(self.uiScrollList_parents)

        
        #>>> Button Row ---------------------------------------------------------------------------------------
        _row_buttons = mUI.MelHLayout(_MainForm,ut='cgmUISubTemplate',padding = 5,en=False)
        self._l_toEnable.append(_row_buttons)
            
        cgmUI.add_Button(_row_buttons,'Add',
                         cgmGEN.Callback(self.uiFunc_load_selected),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Load selected nodes to the ui. First in selection is prime node.")
        cgmUI.add_Button(_row_buttons,'Remove',
                         cgmGEN.Callback(self.uiFunc_updateScrollParentList),                         
                         "Refresh the attributes in the scroll list. Useful if keyed.")        

        cgmUI.add_Button(_row_buttons,'Clear',
                         cgmGEN.Callback(self.uiFunc_clear_loaded),                         
                         "Clear loaded nodes")
        cgmUI.add_Button(_row_buttons,'Rebuild',
                         cgmGEN.Callback(self.uiFunc_clear_loaded),                         
                         "Clear loaded nodes")        
        _row_buttons.layout()        
        
        
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
                        (_row_buttons,"left",0),
                        (_row_buttons,"right",0),
                        (_header_parents,"left",0),
                        (_header_parents,"right",0),
                        (_row_modeSelect,"left",5),
                        (_row_modeSelect,"right",5),
                        (_row_buttons,"bottom",0),

                        ],
                  ac = [(_row_objLoad,"top",2,_header_top),
                        (_row_report,"top",0,_row_objLoad),
                        (_row_modeSelect,"top",2,_row_report),
                        (_header_parents,"top",2,_row_modeSelect),
                        (self.uiScrollList_parents,"top",0,_header_parents),
                        (self.uiScrollList_parents,"bottom",2,_row_buttons),
                        
                       ],
                  attachNone = [(_row_buttons,"top")])	        
        
        _sel = mc.ls(sl=True)
        if _sel:
            self.uiFunc_load_selected()                

        return
        
        
        
        
        

        
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
        
        return
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
                        ],
                  ac = [(_row_attrReport,"top",2,_header),
                        (_row_attrCreate,"top",2,_row_attrReport),
                        (_row_attrFlags,"top",2,_row_attrCreate),
                        (_row_move,"bottom",0,_header_push),                                                
                        (_header_push,"bottom",2,self.row_setValue),                        
                        #(_row_keyModes,"bottom",0,_row_valueModes),
                        #(_row_valueModes,"bottom",0,self.row_setValue),                        
                        (self.uiScrollList_attr,"top",2,_row_attrFlags),
                        (self.uiScrollList_attr,"bottom",0,_row_move)],
                  attachNone = [(self.row_setValue,"top")])	        
            
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
        
        
        _res_context = get_context(self,self.var_context.value,False)
        
        _primeNode =_res_context['primeNode']
        _l_primeAttrs = _res_context['attrs']
        _l_targets = _res_context['targets'] 
        _l_channelbox = _res_context['channelbox']
        _d_prime = None
        
        print(cgmGEN._str_subLine)
        self._l_attrsSelected = []
        
        
        for i,idx in enumerate(_indices):
            _a = self._l_attrsToLoad[idx]
            self._l_attrsSelected.append(_a)
            _d = ATTR.validate_arg(_short, _a)
            _v = ATTR.get(_d)
            log.info("{1}.{2} | value: {3}".format(_str_func, _short,_a, _v))
            if i == 0:
                _d_prime = _d
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
                        label = "prime: {0}".format(self._l_attrsToLoad[_indices[0]]),
                        en=False)
        mUI.MelMenuItem(_popUp,
                        label ='Set Value',
                        ann = 'Enter value desired in pompt. If message, select object(s) to store',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}))        
        mUI.MelMenuItemDiv(_popUp)
        
        
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
            _d_baseAttr = ATTR.validate_arg(self._ml_nodes[0].mNode,self._l_attrsToLoad[_indices[0]])
        else:
            _d_baseAttr = False
            
        _aType = ATTR.get_type(_d_baseAttr)
        _str_base = NAMES.get_base(_d_baseAttr['combined'])
        _done = False
        #Get attr types...

        if _mode is not None:
            if _mode == 'delete':
                simpleProcess(self, _indices, self._l_attrsToLoad, ATTR.delete)
                _done = True             
            elif _mode == 'rename':
                _fromPrompt = uiPrompt_getValue("Enter Name","Primary attr: '{0}' | type: {1}".format(_str_base,_aType),_d_baseAttr['attr'])                
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
                    ATTR.set_message(self._ml_nodes[0].mNode, self._l_attrsToLoad[_indices[0]], _sel)
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
            _a = self._l_attrsToLoad[i]
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
    _l_context = CONTEXT.get_list('selection')
    _buildD = {}
    
    _len_context = len(_l_context)
    if not _l_context:
        log.error("|{0}| >> Nothing selected.".format(_str_func))                                               
        return False
    
    _buildD['dynChild'] = _l_context[0]
    
    if _len_context > 1:
        _buildD['dynParents'] = _l_context[1:]
    
    #>>>Logging what we're gonna do.
    log.info("|{0}| >> Building....".format(_str_func))                                               
    log.info("|{0}| >> dynChild: {1}".format(_str_func,_buildD['dynChild'])) 
 

    #Initialize group
    _mi_group = cgmRigMeta.cgmDynParentGroup(dynChild = _buildD['dynChild'])
    
    #Add parents
    if _buildD.get('dynParents'):    
        log.info("|{0}| >> dynParents...".format(_str_func))         
        for i,p in enumerate(_buildD['dynParents']):
            log.info("|{0}| >> {1} | {2}".format(_str_func,i,p))   
            _mi_group.addDynParent(p)
    
    _mi_group.rebuild()    
    
    mc.select(_l_context)
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
    log.info("|{0}| >> dynChild: {1}".format(_str_func,mObj.mNode))
    log.info("|{0}| >> dynGroup: {1}".format(_str_func,mGroup.mNode))
    _d['mode'] = mGroup.dynMode
    _d['dynParents'] = mGroup.msgList_get('dynParents')
    _d['dynDrivers'] = mGroup.msgList_get('dynDrivers')
    
    _d['aliases'] = []
    for p in _d['dynParents']:
        _d['aliases'].append(ATTR.get(p,'cgmAlias'))
    
    cgmGEN.log_info_dict(_d,'Data:')
    return _d
    
    
    
    
    
