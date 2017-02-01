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

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


import maya.cmds as mc


import cgm.core.classes.GuiFactory as cgmUI
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
reload(SEARCH)
#>>> Root settings =============================================================
__version__ = 'Alpha 2.0.01262017'

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
    _checkBoxKeys = ['shared','regular','user','numeric']
    
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

    def build_menus(self):
        self.uiMenu_HelpMenu = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)           
        #pass#...don't want em  
    #def setup_Variables(self):pass
    
        
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
            
    def uiFunc_load_selected(self):
        _str_func = 'uiFunc_load_selected'  
        self._d_attrs = {}
        self._ml_nodes = []
        
        _sel = mc.ls(sl=True)
        
        #Get our raw data
        for o in _sel:
            _type = VALID.get_mayaType(o)
            if VALID.is_transform(o) or VALID.is_shape(o):
                mNode = cgmMeta.validateObjArg(o)
                self._ml_nodes.append( mNode )
                _short = mNode.p_nameShort
                log.debug("|{0}| >> Good obj: {1}".format(_str_func, _short))
                self._d_attrs[_short] = mc.listAttr(_short)
            else:
                log.debug("|{0}| >> Bad obj: {1}".format(_str_func, NAMES.get_short(o)))
                
        if len(self._ml_nodes) < 2:
            self._d_uiCheckBoxes['shared'](edit = True, en=False)
        else:
            self._d_uiCheckBoxes['shared'](edit = True, en=True)    
        self.uiReport_objects()
        self.uiFunc_updateScrollAttrList()

    def uiFunc_updateScrollAttrList(self):
        _str_func = 'uiFunc_updateScrollAttrList'          
        self._l_attrsToLoad = []
        _d_processed = {}
        
        if not self._ml_nodes:
            return False      
        
        #for k in ui._checkBoxKeys:
            #log.info("{0} : {1}".format(k, self._d_uiCheckBoxes[k].getValue()))
        #['shared','keyable','transforms','user','other']
        
        _shared = self._d_uiCheckBoxes['shared'].getValue()
        #_keyable = self._d_uiCheckBoxes['keyable'].getValue()
        _regular = self._d_uiCheckBoxes['regular'].getValue()
        _user = self._d_uiCheckBoxes['user'].getValue()
        _numeric = self._d_uiCheckBoxes['numeric'].getValue()
        _sort = self._d_uiCheckBoxes['sort'].getValue()
        
        
        #_transforms = self._d_uiCheckBoxes['trans'].getValue()        
        #_other = self._d_uiCheckBoxes['other'].getValue()
        
        for mObj in self._ml_nodes:
            _short = mObj.p_nameShort
            _d_processed[_short] = []
            _l_processed = _d_processed[_short] 
                       
            _l = []
            if _regular:
                _l.extend( mc.listAttr(_short, keyable=True) or [])
                if VALID.getTransform(_short):
                    _l.extend(SHARED._d_attrCategoryLists['transform'])                
            else:
                _l = mc.listAttr(_short, settable = True) or []
            
            if _user:_l.extend(mc.listAttr(_short, ud=True) or [])
                
            _l = LISTS.get_noDuplicates(_l)

            
            for a in _l:
                try:
                    if a.count('.')>0:
                        continue
                    _d = ATTR.validate_arg(_short,a)
                    if _numeric:
                        if ATTR.is_numeric(_d):
                            _l_processed.append(a)
                    else:
                        _l_processed.append(a)
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
                        log.info("|{0}| >> '{1}' not shared. removing...".format(_str_func, a))                           
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
                    
                    _alias = ATTR.get_alias(_d)
                    _nice = ATTR.get_nameNice(_d)
                    _long = ATTR.get_nameLong(_d)
                    
                    _l_name = []
                    _l_name.append(_long)
                    
                    if _alias:
                        _l_name.append("--alias({0})".format(_alias) )
                    #if _nice and _nice.lower() != _long:
                        #_l_name.append("--nice({0})".format(_nice))
                    _l_name.append("--({0})--".format(_type) )
                    
                    _l_report.append("".join(_l_name))
                    
                    _l_flags = []
                    
                    if ATTR.is_dynamic(_d):
                        _l_flags.append('u')  
                        
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
                        _v = "{0}".format(ATTR.get_enumValueString(_d))                        
                    else:
                        _v = "{0}".format(ATTR.get(_d))
                    if len(_v)> 10 and _type not in ['msg']:
                        _v = _v[:10] + "...  "
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
                         "Add the attribute names from the text field")
        cgmUI.add_Button(_row_attrCreate,'Report',
                         cgmGEN.Callback(self.uiFunc_report_loaded),                         
                         "Add the attribute names from the text field")        

        cgmUI.add_Button(_row_attrCreate,'Clear',
                         cgmGEN.Callback(self.uiFunc_clear_loaded),                         
                         "Add the attribute names from the text field")
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
            if item in ['shared','regular','user']:_cb = True
            else:_cb = False
            self._d_uiCheckBoxes[item] = mUI.MelCheckBox(_row_attrFlags,label = item,
                                                         v = _cb,
                                                         cc = cgmGEN.Callback(self.uiFunc_updateScrollAttrList))
        _row_attrFlags.layout()
        
        #>>>Manage Attribute Section ---------------------------------------------------------------------------------------
        self.uiScrollList_attr = mUI.MelObjectScrollList(_MainForm, allowMultiSelection=True,
                                                         selectCommand = self.uiFunc_selectAttr)
        
        
        #>>>Keys Row --------------------------------------------------------------------------------------------        
        mc.setParent(_MainForm)
        _header_push = cgmUI.add_Header('Push Values')
       
        
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
        
        _row_valueModes.layout()        
        
        
        
        #>>>Push Values Row --------------------------------------------------------------------------------------------
        self.row_setValue = mUI.MelHLayout(_MainForm,ut='cgmUISubTemplate',padding = 2)
        
        cgmUI.add_Button(self.row_setValue,'<<<All',
                         cgmGEN.Callback(self.uiFunc_load_selected),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Add the attribute names from the text field") 
        cgmUI.add_Button(self.row_setValue,'<Prev',
                         cgmGEN.Callback(self.uiFunc_load_selected),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Add the attribute names from the text field")
        
        cgmUI.add_Button(self.row_setValue,'Current',
                         cgmGEN.Callback(self.uiFunc_pushValue,**{'mode':'current'}),                
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Add the attribute names from the text field")

        cgmUI.add_Button(self.row_setValue,'Next>',
                         cgmGEN.Callback(self.uiFunc_load_selected),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Add the attribute names from the text field")
        cgmUI.add_Button(self.row_setValue,'All>>>',
                         cgmGEN.Callback(self.uiFunc_load_selected),
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Add the attribute names from the text field")

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
                        (_header_push,"left",0),
                        (_header_push,"right",0),                         
                        (_row_keyModes,"left",5),
                        (_row_keyModes,"right",5),  
                        (_row_valueModes,"left",5),
                        (_row_valueModes,"right",5),                          
                        (self.row_setValue,"left",0),
                        (self.row_setValue,"right",0),                          
                        (self.row_setValue,"bottom",5),
                        ],
                  ac = [(_row_attrReport,"top",2,_header),
                        (_row_attrCreate,"top",2,_row_attrReport),
                        (_row_attrFlags,"top",2,_row_attrCreate),
                        (_header_push,"bottom",0,_row_keyModes),                        
                        (_row_keyModes,"bottom",0,_row_valueModes),
                        (_row_valueModes,"bottom",0,self.row_setValue),                        
                        (self.uiScrollList_attr,"top",2,_row_attrFlags),
                        (self.uiScrollList_attr,"bottom",0,_header_push)],
                  attachNone = [(self.row_setValue,"top")])	        
            
        _sel = mc.ls(sl=True)
        if _sel:
            self.uiFunc_load_selected()        

    def uiFunc_selectAttr(self): 
        _str_func = 'uiFunc_selectAttr'        
        if self.uiPopUpMenu_attr:
            self.uiPopUpMenu_attr.clear()
            self.uiPopUpMenu_attr.delete()
            
        self.uiPopUpMenu_attr = mUI.MelPopupMenu(self.uiScrollList_attr,button = 3)

        _popUp = self.uiPopUpMenu_attr   
        

        _indices = self.uiScrollList_attr.getSelectedIdxs()
        log.debug("|{0}| >> indices: {1}".format(_str_func, _indices))                           
        
        _b_single = False
        if len(_indices)==1:_b_single = True
        
        _short = self._ml_nodes[0].p_nameShort
        _dynamic = False
        _numberChanges = False    
        _hidden = False
        _connectionsIn = False
        _connectionsOut = False
        
        print(cgmGEN._str_subLine)
        self._l_attrsSelected = []
        
        for i in _indices:
            _a = self._l_attrsToLoad[i]
            self._l_attrsSelected.append(_a)
            _d = ATTR.validate_arg(_short, _a)
            _v = ATTR.get(_d)
            log.info("{1}.{2} | value: {3}".format(_str_func, _short,_a, _v))                           
            if ATTR.is_dynamic(_d):
                _dynamic = True
                if ATTR.is_numeric(_d):
                    _numberChanges = True
                    log.debug("|{0}| >> {1}.{2}...setting up value change popup".format(_str_func, _short,_a))                           
            if ATTR.is_hidden(_d):
                _hidden = True
            _connectionsIn = ATTR.get_driver(_d,skipConversionNodes=True)
            _connectionsOut = ATTR.get_driven(_d,skipConversionNodes=True)
        
        
        #>>>Pop up menu--------------------------------------------------------------------------------------------        
        mUI.MelMenuItem(_popUp,
                        label ='Set Value',
                        ann = 'Enter value desired in pompt. If message, select object(s) to store',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'value'}))        
        mUI.MelMenuItemDiv(_popUp)
        
        _l_boolToMake = ['keyable','lock','hidden']
        
        for item in _l_boolToMake:
            _menu = mUI.MelMenuItem(_popUp, subMenu = True,
                                label = item.capitalize())
            mUI.MelMenuItem(_menu,
                        label ='True',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{item:True}))        
            mUI.MelMenuItem(_menu,
                        label ='False',
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{item:False}))            
        
        if _connectionsIn:
            _menu = mUI.MelMenuItem(_popUp, subMenu = True,
                                    label = "Connections In")            
            mUI.MelMenuItem(_menu,
                            c = cgmGEN.Callback(mc.select,_connectionsIn),
                            label = NAMES.get_short(_connectionsIn))                
        if _connectionsOut:
            _menu = mUI.MelMenuItem(_popUp, subMenu = True,
                                    label = "Connections Out")            
            for plug in _connectionsOut:
                mUI.MelMenuItem(_menu,
                                c = cgmGEN.Callback(mc.select,plug),
                                label = NAMES.get_short(plug))                 
            
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
        if _numberChanges:
            _l = ['default','min','max','softMin','softMax']
            _menu = mUI.MelMenuItem(_popUp,subMenu = True, 
                                    l='Numeric')
            for item in _l:
                mUI.MelMenuItem(_menu,
                                label =item.capitalize(),
                                c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':item})) 
                
                
        #Values --------------------------------        
        _l = ['convert','duplicate','copyTo','copyTo connect back','copyTo connect','connectTo','moveUp','moveDown']
        _menu = mUI.MelMenuItem(_popUp,subMenu = True, 
                                l='Utilities')
        
        _l_addTypes = ['string','float','enum','vector','int','bool','message']
        _add = mUI.MelMenuItem(_menu,subMenu = True, 
                               l='add')
        for t in _l_addTypes:
            mc.menuItem(parent=_add,
                        l=t,
                        c = cgmGEN.Callback(uiPrompt_addAttr,t))
            
        _convert = mUI.MelMenuItem(_menu,subMenu = True, 
                                   en = _dynamic,                                   
                                   l='convert')
        for t in _l_addTypes:
            mc.menuItem(parent=_convert,
                        l=t,
                        c = cgmGEN.Callback(self.uiFunc_attrManage_fromScrollList,**{'mode':'convert{0}'.format(t.capitalize())})) 
        
        
        
        for item in _l:
            if not _dynamic and item in ['moveUp','moveDown','copyTo','copyTo connect back','copyTo connect']:
                pass
            elif _hidden and item in ['moveUp','moveDown']:
                pass
            else:
                mUI.MelMenuItem(_menu,
                                label =item,
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
        _indices = self.uiScrollList_attr.getSelectedIdxs()
        _mode = kws.get('mode','current')
        _keyMode = self.var_keyMode.value
        _valueMode = self.var_valueMode.value
        
        log.info("|{0}| >> mode: {1} | keyMode: {2} | valueMode: {3}".format(_str_func,_mode,_keyMode,_valueMode))
        log.info("|{0}| >> indicies: {1} ".format(_str_func,_indices))
        
        _v_master = None
        _d_values = {}
        
        #>>Get Attribute values -----------------------------------------------------------------------------------
        _short = self._ml_nodes[0].p_nameShort
        if _valueMode == 0:#PrimeAttr
            _v_master = ATTR.get(_short, self._l_attrsToLoad[_indices[0]])
            log.info("|{0}| >> master value: {1} ".format(_str_func,_v_master))
        else:
            for idx in _indices:
                _a = self._l_attrsToLoad[idx]
                _d_values[_a] = ATTR.get(_short,_a)
            cgmGEN.print_dict(_d_values,'Master Values', 'attrTools')
        
        #>>> Get our driven ------------------------------------------------------------------------------
        _sel = SEARCH.get_selectedFromChannelBox(False) or []
        if not _sel:
            _sel = mc.ls(sl=True) or []
            
        _ml_nodes = self._ml_nodes        
        
        #>>> Bake ------------------------------------------------------------------------------        
        if _mode == 'current':
            pass
            #Get our targets
            #Get our Values
            #Push our values
        
        
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
        
        _d_baseAttr = ATTR.validate_arg(self._ml_nodes[0].mNode,self._l_attrsToLoad[_indices[0]])
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
                #else:
                    #log.info("|{0}| >>  from prompt: {1} ".format(_str_func,_fromPrompt)) 
                    #try:
                        #ATTR.rename(_d_baseAttr,_fromPrompt)
                        #_done = True
                    #except Exception,err:
                        #log.warning("|{0}| >> {1} | new name: {2} | err: {3}".format(_str_func, _str_base, _fromPrompt,err))                           
            elif _mode in ['alias','nameNice']:
                if _mode == 'alias':
                    _plug = ATTR.get_alias(_d_baseAttr)
                else:
                    _plug = ATTR.get_nameNice(_d_baseAttr)
                _kws = {'title':"Enter {0}".format(_mode),'message':'Enter a new {0}.'.format(_mode)}
                if _plug:
                    _kws['text'] = _plug
                
                _fromPrompt = uiPrompt_getValue(**_kws)   
                
                if _fromPrompt is None:
                    log.error("|{0}| >>  Mode: {1} | No value gathered...".format(_str_func,_mode))      
                    return False
                log.info(_fromPrompt)
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
                        
            elif _mode.startswith('convert'):
                _convertString = _mode.split('convert')[-1].lower()
                log.info("|{0}| >>  convert string: {1} ".format(_str_func,_convertString))                                                               
                return False
                
            else:
                log.error("|{0}| >>  Mode: {1} | Not implented...".format(_str_func,_mode))                                               
                return False
        
        if _done:
            self.uiFunc_updateScrollAttrList()
            return True

        for i in _indices:
            _a = self._l_attrsToLoad[i]
            for mNode in self._ml_nodes:
                try:
                    _short = mNode.p_nameShort
                    _d = ATTR.validate_arg(_short,_a)
                    
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
                                if ',' in _fromPrompt:
                                    _fromPrompt = _fromPrompt.split(',')
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
                        elif _mode in ['default','min','max','softMin','softMax']:
                            _d_plugs = {'default':ATTR.set_default,'min':ATTR.set_min,'max':ATTR.set_max,
                                        'softMin':ATTR.set_softMin,'softMax':ATTR.set_softMax}
                            if not _fromPrompt:_fromPrompt=False
                            else:_fromPrompt = float(_fromPrompt)
                            _d_plugs[_mode](_d,_fromPrompt)
                            
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
            _attrs = _v.split(',')
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
        ui()
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
        

