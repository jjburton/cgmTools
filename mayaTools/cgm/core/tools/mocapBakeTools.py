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

#>>> Root settings =============================================================
__version__ = '0.08312017'
__toolname__ ='mocapBakeTool'

_subLineBGC = [.75,.75,.75]

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
        self.uiMenu_help = mUI.MelMenu( l='Help', pmc = cgmGEN.Callback(self.buildMenu_help))

    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                                 c=lambda *a: cgmUI.log_selfReport(self) )

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
        #_source_column = self.buildSourceColumn_main(_MainForm,False)

        _item_form = mUI.MelFormLayout(_MainForm,ut='cgmUITemplate')

        _parent_frame = mUI.MelFrameLayout(_item_form,label = 'Parent',vis=True,
                            collapsable=False,
                            enable=True,
                            #ann='Contextual MRS functionality',
                            useTemplate = 'cgmUIHeaderTemplate'
                            )
        
        _orient_frame = mUI.MelFrameLayout(_item_form,label = 'Orient',vis=True,
                    collapsable=False,
                    enable=True,
                    #ann='Contextual MRS functionality',
                    useTemplate = 'cgmUIHeaderTemplate'
                    )

        self.splitFormVertical(_item_form, _parent_frame, _orient_frame)

        _parent_form = mUI.MelFormLayout(_parent_frame,ut='cgmUITemplate')
        
        _parent_source = self.buildScrollForm(_parent_form, hasButton=True, hasHeader=True, buttonLabel='Add Selected', headerText = 'source', buttonCommand=uiFunc_button_command1)
        _parent_target = self.buildScrollForm(_parent_form, hasButton=True, hasHeader=True, buttonLabel='Add Selected', headerText = 'target', buttonCommand=uiFunc_button_command2)
        
        self.splitFormHorizontal(_parent_form, _parent_source[0], _parent_target[0])

        _orient_form = mUI.MelFormLayout(_orient_frame,ut='cgmUITemplate')
        
        _orient_source = self.buildScrollForm(_orient_form, hasButton=True, hasHeader=True, buttonLabel='Add Selected', headerText = 'source', buttonCommand=uiFunc_button_command1)
        _orient_target = self.buildScrollForm(_orient_form, hasButton=True, hasHeader=True, buttonLabel='Add Selected', headerText = 'target', buttonCommand=uiFunc_button_command1)
        
        self.splitFormHorizontal(_orient_form, _orient_source[0], _orient_target[0])

        _options_column = self.buildOptions(_MainForm,False)
        _footer = cgmUI.add_cgmFooter(_options_column)        

        _MainForm(edit = True,
                  af = [(_item_form,"top",0),
                        (_item_form,"left",0),
                        (_item_form, "right", 0),
                        (_options_column,"left",0),
                        (_options_column,"right",0),                       
                        (_options_column,"bottom",0)],
                  ac = [(_item_form,"bottom",2,_options_column)],
                  attachNone = [(_options_column,"top")])
        
    def buildScrollForm(self, parent, hasHeader = False, hasButton = False, buttonLabel = 'Button', headerText = 'Header', buttonCommand=None):
        main_form = mUI.MelFormLayout(parent,ut='cgmUITemplate')

        header = None
        if(hasHeader):
            header = cgmUI.add_Header(headerText, overrideUpper = True)
        
        scroll_list = mUI.MelObjectScrollList( main_form, ut='cgmUITemplate',
                                                  allowMultiSelection=True )

        button = None
        if(hasButton):
            button = cgmUI.add_Button(main_form,buttonLabel,
                         cgmGEN.Callback(buttonCommand,self),
                         "Help.")


        af = [(scroll_list,"left",0), (scroll_list,"right",0)]
        ac = []
        attachNone = []

        if(hasHeader):
            af += [ (header,"top",0),
                    (header,"left",0),
                    (header,"right",0) ]
            ac += [(scroll_list,"top",0,header)]
            attachNone += [(header,"bottom")]
        else:
            af += [ (scroll_list,"top",0) ]

        if(hasButton):
            af += [ (button,"bottom",0),
                    (button,"left",0),
                    (button,"right",0)]
            ac += [(scroll_list,"bottom",0,button)]
            attachNone += [(button,"top")]
        else:
            af += [ (scroll_list,"bottom",0) ]

        main_form(edit=True, af = af,
                                ac = ac,
                                attachNone = attachNone)
        
        return [main_form, scroll_list, header, button]

    def splitFormHorizontal(self, form_layout, element1, element2, division = 50, padding = 0):
        form_layout(edit = True,
          af = [(element1,"top",padding),
                (element1,"bottom",padding),
                (element1, "left", padding),
                (element2,"top",padding),
                (element2,"bottom",padding),
                (element2,"right",padding)],
          ac = [(element2,"left",padding,element1)],
          ap = [(element1, 'right', padding, division)])
        return form_layout

    def splitFormVertical(self, form_layout, element1, element2, division = 50, padding = 0):
        form_layout(edit = True,
          af = [(element1,"left",padding),
                (element1,"right",padding),
                (element1, "top", padding),
                (element2,"left",padding),
                (element2,"right",padding),
                (element2,"bottom",padding)],
          ac = [(element2,"top",padding,element1)],
          ap = [(element1, 'bottom', padding, division)])
        return form_layout

    def buildOptions(self,parent, asScroll = False):
 
        if asScroll:
            _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUISubTemplate') 
        else:
            _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
        
        #>>>Objects Load Row ---------------------------------------------------------------------------------------
        
        mc.setParent(_inside)
        cgmUI.add_LineSubBreak()

        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5,bgc=_subLineBGC)

        mUI.MelSpacer(_row,w=5)
        mUI.MelLabel(_row,l='Link by')
        _row.setStretchWidget( mUI.MelSeparator(_row) )
    

        #mUI.MelSpacer(_row_objLoad,w=10)
        
        '''
        mUI.MelLabel(_row_objLoad, 
                     l='Source:')
        
        uiTF_objLoad = mUI.MelLabel(_row_objLoad,ut='cgmUITemplate',l='',
                                    en=True)
        
        self.uiTF_objLoad = uiTF_objLoad
        cgmUI.add_Button(_row_objLoad,'<<',
                         cgmGEN.Callback(uiFunc_load_selected,self),
                         "Load first selected object.")  
        
        _row_objLoad.setStretchWidget(uiTF_objLoad)
        '''
        cgmUI.add_Button(_row,'Name',
                 cgmGEN.Callback(self.uiFunc_link_by_name,self),
                 "Create links by closest name") 
        cgmUI.add_Button(_row,'Distance',
                 cgmGEN.Callback(self.uiFunc_link_by_distance,self),
                 "Create links by shortest distance") 
        mUI.MelSpacer(_row,w=5)



        cgmUI.add_Button(_inside,'<<',
                 cgmGEN.Callback(uiFunc_load_selected,self),
                 "Load first selected object.") 
        cgmUI.add_Button(_inside,'<<',
                 cgmGEN.Callback(uiFunc_load_selected,self),
                 "Load first selected object.") 

        _row_objLoad2 = mUI.MelHRowLayout(_inside,ut='cgmUITemplate',padding = 5)

        cgmUI.add_Button(_row_objLoad2,'<<',
                 cgmGEN.Callback(uiFunc_load_selected,self),
                 "Load first selected object.") 
        cgmUI.add_Button(_row_objLoad2,'<<',
                 cgmGEN.Callback(uiFunc_load_selected,self),
                 "Load first selected object.") 
        #mUI.MelSpacer(_row_objLoad,w=10)

        _row.layout()
        _row_objLoad2.layout()
        #uiFunc_load_selected(self)

        return _inside

    def uiFunc_link_by_name(self):
        print "Linking by name"

    def uiFunc_link_by_distance(self):
        print "Linking by distance"

    def uiFunc_add_selected_to_list(self):
        print "Button1"

'''
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

    #uiFunc_updateFields(self)
    #self.uiReport_do()
    #self.uiFunc_updateScrollAttrList()

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

'''
 