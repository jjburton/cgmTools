"""
------------------------------------------
baseTool: cgm.core.tools
Author: Josh Burton and David Bokser
email: dbokser@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
mocapBakeTools
================================================================
"""
# From Python =============================================================
import copy
import re
import time
import pprint
import os
import sys
import math
import json

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import maya.cmds as mc

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import transform_utils as TRANS
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import string_utils as STRING
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import euclid
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as CGMPATH
from cgm.lib import lists


#>>> Root settings =============================================================
__version__ = '0.08312017'
__toolname__ ='mocapBakeTool'

_subLineBGC = [.75,.75,.75]
_buttonBGC = [.3,.3,.3]

class cgmListItem(object):
    item = None
    alias = None
    data = None
    #mobj = None

    def __init__(self, init_item, init_alias, init_data = {}):
        self.item = init_item
        self.alias = init_alias
        self.data = init_data
        #self.mobj = init_mobj

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = '{0}_ui'.format(__toolname__)    
    WINDOW_TITLE = '{1} - {0}'.format(__version__,__toolname__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 450,350
    TOOLNAME = '{0}.ui'.format(__toolname__)
    
    parent_source_items = []
    parent_target_items = []
    # orient_source_items = []
    # orient_target_items = []

    parent_links = []
    # orient_links = []

    connection_data = []

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

        self.create_guiOptionVar('mocap_allow_multiple_targets',defaultValue = 0)
        self.create_guiOptionVar('mocap_set_connection_at_bake',defaultValue = 1)

        self.uiPopUpMenu_target = None
        self.uiPopUpMenu_source = None
 
    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))
        self.uiMenu_tools = mUI.MelMenu( l='Tools', pmc = cgmGEN.Callback(self.buildMenu_tools))
        self.uiMenu_help = mUI.MelMenu( l='Help', pmc = cgmGEN.Callback(self.buildMenu_help))

    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                                 c=lambda *a: cgmUI.log_selfReport(self) )

    def buildMenu_tools( self, *args):
        self.uiMenu_tools.clear()
        mUI.MelMenuItem( self.uiMenu_tools, l="Make Constraints",
                                 c=lambda *a: self.uiFunc_make_constraints(self) )


    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options                           

        #mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, checkBox=self.var_mocap_allow_multiple_targets.value, l="Allow multiple targets",
                 c=lambda *a: self.uiFunc_toggle_multiple_targets(self) )#not mc.optionVar(q='cgm_mocap_allow_multiple_targets')))

        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Save Data",
                 c=lambda *a: self.uiFunc_save_data(self) )


        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Load Data",
                 c=lambda *a: self.uiFunc_load_data(self) )

        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'

        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')

        _item_form = mUI.MelFormLayout(_MainForm,ut='cgmUITemplate')
        
        _parent_source = self.buildScrollForm(_item_form, hasHeader=True, buttonArgs = [{'label':'Add Selected', 'command':self.uiFunc_add_to_parent_source, 'annotation':_d_annotations.get('addSource','fix')}, {'label':'Remove Item', 'command':self.uiFunc_remove_from_parent_source, 'annotation':_d_annotations.get('removeSource','fix')}], headerText = 'source', allowMultiSelection=False, selectCommand=self.uiFunc_on_select_parent_source_item, doubleClickCommand=self.uiFunc_toggle_link_parent_targets)
        _parent_target = self.buildScrollForm(_item_form, hasHeader=True, buttonArgs = [{'label':'Add Selected', 'command':self.uiFunc_add_to_parent_target, 'annotation':_d_annotations.get('addTarget','fix')}, {'label':'Remove Item', 'command':self.uiFunc_remove_from_parent_target, 'annotation':_d_annotations.get('removeTarget','fix')}], headerText = 'target', allowMultiSelection=True, selectCommand=self.uiFunc_select_parent_target_link, doubleClickCommand=self.uiFunc_toggle_link_parent_targets)
        
        self.parent_source_scroll = _parent_source[1]
        self.parent_target_scroll = _parent_target[1]


        self.uiPopUpMenu_source = mUI.MelPopupMenu(self.parent_source_scroll,button = 3)

        mUI.MelMenuItem(self.uiPopUpMenu_source,
            ann = 'Select',
            c = cgmGEN.Callback( self.uiFunc_select_from_ui, 0),
            label = "Select")
        mUI.MelMenuItem(self.uiPopUpMenu_source,
            ann = 'Select Link',
            c = cgmGEN.Callback( self.uiFunc_select_from_ui, 2),
            label = "Select Link")
        mUI.MelMenuItem(self.uiPopUpMenu_source,
            ann = 'Clear List',
            c = cgmGEN.Callback( self.uiFunc_clear_list, 0),
            label = "Clear List")
        mUI.MelMenuItem(self.uiPopUpMenu_source,
            ann = 'Select All',
            c = cgmGEN.Callback( self.uiFunc_select_all_in_list, 0),
            label = "Select All")

        self.uiPopUpMenu_target = mUI.MelPopupMenu(self.parent_target_scroll,button = 3)

        mUI.MelMenuItem(self.uiPopUpMenu_target,
            ann = 'Select',
            c = cgmGEN.Callback( self.uiFunc_select_from_ui, 1),
            label = "Select")
        mUI.MelMenuItem(self.uiPopUpMenu_target,
            ann = 'Select Link',
            c = cgmGEN.Callback( self.uiFunc_select_from_ui, 3),
            label = "Select Link")
        mUI.MelMenuItem(self.uiPopUpMenu_target,
            ann = 'Clear List',
            c = cgmGEN.Callback( self.uiFunc_clear_list, 1),
            label = "Clear List")
        mUI.MelMenuItem(self.uiPopUpMenu_source,
            ann = 'Select All',
            c = cgmGEN.Callback( self.uiFunc_select_all_in_list, 1),
            label = "Select All")

        self.parent_target_scroll(e=True, allowMultiSelection=self.var_mocap_allow_multiple_targets.value)

        self.splitFormHorizontal(_item_form, _parent_source[0], _parent_target[0])

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
    
    def buildScrollForm(self, parent, hasHeader = False, buttonArgs = [], headerText = 'Header', allowMultiSelection=True, buttonCommand=None, doubleClickCommand=None, selectCommand=None):
        main_form = mUI.MelFormLayout(parent,ut='cgmUITemplate')

        header = None
        if(hasHeader):
            header = cgmUI.add_Header(headerText, overrideUpper = True)
        
        scroll_list = mUI.MelObjectScrollList( main_form, ut='cgmUITemplate',
                                                  allowMultiSelection=allowMultiSelection, doubleClickCommand=cgmGEN.Callback(doubleClickCommand,self), selectCommand=cgmGEN.Callback(selectCommand,self) )

        buttonLayout = None
        buttons = []
        hasButton = len(buttonArgs) > 0
        if(hasButton):
            #buttonLayout = mUI.MelColumnLayout(main_form,useTemplate = 'cgmUISubTemplate')
            buttonLayout = mUI.MelHLayout(main_form,ut='cgmUISubTemplate',padding = 1,bgc=_subLineBGC)
            for btn in buttonArgs:
                button = cgmUI.add_Button(buttonLayout,btn['label'],
                             cgmGEN.Callback(btn['command'],self),
                             btn['annotation'], bgc=_buttonBGC)
                buttons.append(button)
            buttonLayout.layout()


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
            af += [ (buttonLayout,"bottom",0),
                    (buttonLayout,"left",0),
                    (buttonLayout,"right",0)]
            ac += [(scroll_list,"bottom",0,buttonLayout)]
            attachNone += [(buttonLayout,"top")]
        else:
            af += [ (scroll_list,"bottom",0) ]

        main_form(edit=True, af = af,
                                ac = ac,
                                attachNone = attachNone)
        
        return [main_form, scroll_list, header, buttons]

    def fullForm(self, form_layout, element, padding=0):
        form_layout(edit = True,
          af = [(element,"top",padding),
                (element,"bottom",padding),
                (element, "left", padding),
                (element,"right",padding)])
        return form_layout

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
        mUI.MelLabel(_row,l='Auto Link by')
        _row.setStretchWidget( mUI.MelSeparator(_row) )
    
        cgmUI.add_Button(_row,'Name',
                 cgmGEN.Callback(self.uiFunc_link_by_name,self),
                 _d_annotations.get('linkName','fix'), bgc=_buttonBGC) 
        cgmUI.add_Button(_row,'Distance',
                 cgmGEN.Callback(self.uiFunc_link_by_distance,self),
                 _d_annotations.get('linkDistance','fix'), bgc=_buttonBGC) 
        mUI.MelSpacer(_row,w=5)
        _row.layout()

        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 1,bgc=_subLineBGC)
        mUI.MelSpacer(_row,w=9)
        mUI.MelLabel(_row,l='Set Target Constraint to')
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        cgmUI.add_Button(_row,'Point/Orient',
                 cgmGEN.Callback(self.uiFunc_set_constraint_type,1,True,self),
                 _d_annotations.get('setPointOrient','fix'), bgc=_buttonBGC) 
        cgmUI.add_Button(_row,'A',
                 cgmGEN.Callback(self.uiFunc_set_constraint_type,1,False,self),
                 _d_annotations.get('setPointOrientAll','fix'), bgc=_buttonBGC) 
        mUI.MelSpacer(_row,w=4)
        cgmUI.add_Button(_row,'Orient',
                 cgmGEN.Callback(self.uiFunc_set_constraint_type,0,True,self),
                 _d_annotations.get('setOrient','fix'), bgc=_buttonBGC) 
        cgmUI.add_Button(_row,'A',
                 cgmGEN.Callback(self.uiFunc_set_constraint_type,1,False,self),
                 _d_annotations.get('setOrientAll','fix'), bgc=_buttonBGC) 
        mUI.MelSpacer(_row,w=9)

        _row.layout()


        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5,bgc=_subLineBGC)
        mUI.MelSpacer(_row,w=5)
        mUI.MelLabel(_row,l='Set Connection Pose')
        _row.setStretchWidget( mUI.MelSeparator(_row) )
        self.cb_set_connection_at_bake = mUI.MelCheckBox(_row,
                           v = self.var_mocap_set_connection_at_bake.value,
                           onCommand = lambda *a: self.var_mocap_set_connection_at_bake.setValue(1),
                           offCommand = lambda *a: self.var_mocap_set_connection_at_bake.setValue(0),
                           label="Set On Bake")
        cgmUI.add_Button(_row,'Manual Set',
                 cgmGEN.Callback(self.uiFunc_set_connection_pose,1,self),
                 _d_annotations.get('setConnectionPose','fix'), bgc = [.5,.2,0.2]) 
        mUI.MelSpacer(_row,w=5)

        _row.layout()

        # Bake Options

        timelineInfo = SEARCH.get_time('slider')

        mc.setParent(_inside)
        cgmUI.add_Header("Bake Options", overrideUpper = True)

        cgmUI.add_LineSubBreak()


        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5,bgc=_subLineBGC)
        #self.timeSubMenu.append( _row )
        mUI.MelSpacer(_row,w=5)
        mUI.MelLabel(_row,l='Set Timeline Range')
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        cgmUI.add_Button(_row,'Slider',
                 cgmGEN.Callback(self.uiFunc_updateTimeRange,'slider'),
                 _d_annotations.get('sliderRange','fix'), bgc=_buttonBGC) 
        cgmUI.add_Button(_row,'Sel',
                 cgmGEN.Callback(self.uiFunc_updateTimeRange,'selected'),
                 _d_annotations.get('selectedRange','fix'), bgc=_buttonBGC) 
        cgmUI.add_Button(_row,'Scene',
                 cgmGEN.Callback(self.uiFunc_updateTimeRange,'scene'),
                 _d_annotations.get('sceneRange','fix'), bgc=_buttonBGC) 
        mUI.MelSpacer(_row,w=5)
        _row.layout()


        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate', padding=5,bgc=_subLineBGC)
        mUI.MelSpacer(_row,w=5)
        mUI.MelLabel(_row,l='Bake Range')
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        mUI.MelLabel(_row,l='start')

        self.startFrameField = mUI.MelIntField(_row,'cgmLocWinStartFrameField',
                                           width = 40,
                                           value= timelineInfo[0])

        mUI.MelLabel(_row,l='end')

        self.endFrameField = mUI.MelIntField(_row,'cgmLocWinEndFrameField',
                                         width = 40,
                                         value= timelineInfo[1])

        cgmUI.add_Button(_row,' <<',
                         cgmGEN.Callback(self.uiFunc_bake,'back'),                         
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         _d_annotations.get('<<<','fix'), bgc=_buttonBGC)
    
        cgmUI.add_Button(_row,'Bake',
                         cgmGEN.Callback(self.uiFunc_bake,'all'),                         
                         _d_annotations.get('All','fix'), bgc=_buttonBGC)
        
        
        cgmUI.add_Button(_row,'>>',
                         cgmGEN.Callback(self.uiFunc_bake,'forward'),                         
                         _d_annotations.get('>>>','fix'), bgc=_buttonBGC)

        mUI.MelSpacer(_row,w=5)
        _row.layout()

        mc.setParent(_inside)
        cgmUI.add_LineSubBreak()

        return _inside

    def uiFunc_toggle_multiple_targets(self, *args):
        self.var_mocap_allow_multiple_targets.toggle()
        self.parent_target_scroll(e=True, allowMultiSelection=self.var_mocap_allow_multiple_targets.value)

    def uiFunc_updateTimeRange(self,mode = 'slider'):
        _range = SEARCH.get_time(mode)
        if _range:
            self.startFrameField(edit = True, value = _range[0])
            self.endFrameField(edit = True, value = _range[1])  

    def uiFunc_bake(self, *args):
        mode = args[0]

        bake_range = [self.startFrameField(q=True, value=True), self.endFrameField(q=True, value=True)]
        current_frame = SEARCH.get_time('current')
        if mode == 'back':
            bake_range[1] = min(current_frame, bake_range[0], bake_range[1])
            bake_range[0] = current_frame
        if mode == 'forward':
            bake_range[1] = max(current_frame, bake_range[0], bake_range[1])
            bake_range[0] = current_frame

        mc.currentTime(bake_range[0])
        
        if len(self.connection_data) != len(self.parent_links):
            self.connection_data = self.get_ui_connection_data()

        if self.var_mocap_set_connection_at_bake.value:
            self.uiFunc_set_connection_pose()

        bake(self.connection_data, bake_range[0], bake_range[1]) 

    def uiFunc_set_constraint_type(self, *args):
        
        mode = args[0]
        onlySelected = args[1]

        idxs = []
        if onlySelected:
            idxs = self.parent_target_scroll.getSelectedIdxs()
        else:
            idxs = range( len(self.parent_target_scroll.getAllItems()) )

        # point/orient
        if mode == 0:
            for idx in idxs:
                self.parent_target_items[idx].data["constraintType"] = "o"
            log.debug("orient")
        # orient
        elif mode == 1:
            for idx in idxs:
                self.parent_target_items[idx].data["constraintType"] = "po"

            log.debug("point/orient")

        self.refresh_aliases()

        for idx in idxs:
            self.parent_target_scroll.selectByIdx(idx)
            for link in self.parent_links:
                if link[1] == idx:
                    self.parent_source_scroll.selectByIdx(link[0])

    def uiFunc_clear_list(self, mode):
        if mode == 0:
            self.parent_source_scroll.clear()
        else:
            self.parent_target_scroll.clear()

    def uiFunc_select_all_in_list(self, mode):
        pass
        
    def uiFunc_select_from_ui(self, mode):
      mc.select(cl=True)

      if mode == 0:
        idxs = self.parent_source_scroll.getSelectedIdxs()
        for idx in idxs:
          mc.select(self.parent_source_items[idx].item, add=True)
      if mode == 1:
        idxs = self.parent_target_scroll.getSelectedIdxs()
        for idx in idxs:
          mc.select(self.parent_target_items[idx].item, add=True)
      if mode == 2:
        idxs = self.parent_source_scroll.getSelectedIdxs()
        for idx in idxs:
          mc.select(self.parent_source_items[idx].item, add=True)
          for link in self.parent_links:
            if link[0] == idx:
              mc.select(self.parent_target_items[link[1]].item, add=True)      
      if mode == 3:
        idxs = self.parent_target_scroll.getSelectedIdxs()
        for idx in idxs:
          mc.select(self.parent_target_items[idx].item, add=True)
          for link in self.parent_links:
            if link[1] == idx:
              mc.select(self.parent_source_items[link[0]].item, add=True)

    def uiFunc_link_by_name(self, *args):
        self.parent_links = []

        for i, trg in enumerate(self.parent_target_items):
            wantedLink = []
            closest = sys.maxint
            for j, src in enumerate(self.parent_source_items):
                closeness = STRING.levenshtein(trg.item, src.item)
                if closeness < closest:
                    wantedLink = [j, i]
                    closest = closeness
            
            if not self.has_link(wantedLink, self.parent_links):
                make_link = True
                if not self.var_mocap_allow_multiple_targets.value:
                    current_closest = sys.maxint
                    for link in self.parent_links:
                        if link[0] == wantedLink[0]:
                            closeness = STRING.levenshtein(self.parent_target_items[link[1]].item, self.parent_source_items[link[0]].item)
                            if closeness < current_closest:
                                current_closest = closeness
                    if current_closest < closest:
                        make_link = False

                    # remove current links if we're making a new link
                    remove_indexes = []
                    if make_link:
                        for i, link in enumerate(self.parent_links):
                            if link[0] == wantedLink[0]:
                                remove_indexes.append(i)
                        remove_indexes.reverse()
                        for idx in remove_indexes:
                            del self.parent_links[idx]
                if make_link:
                    self.parent_links.append(wantedLink)

        self.refresh_aliases()


    def uiFunc_link_by_distance(self, *args):
        self.parent_links = []

        for i, trg in enumerate(self.parent_target_items):
            wantedLink = []
            closest = sys.float_info.max
            for j, src in enumerate(self.parent_source_items):
                closeness = DIST.get_distance_between_targets([src.item, trg.item])
                if closeness < closest:
                    wantedLink = [j, i]
                    closest = closeness
            
            if not self.has_link(wantedLink, self.parent_links):
                make_link = True
                if not self.var_mocap_allow_multiple_targets.value:
                    current_closest = sys.float_info.max
                    for link in self.parent_links:
                        if link[0] == wantedLink[0]:
                            closeness = DIST.get_distance_between_targets( [self.parent_target_items[link[1]].item, self.parent_source_items[link[0]].item] )
                            if closeness < current_closest:
                                current_closest = closeness
                    if current_closest < closest:
                        make_link = False

                    # remove current links if we're making a new link
                    remove_indexes = []
                    if make_link:
                        for i, link in enumerate(self.parent_links):
                            if link[0] == wantedLink[0]:
                                remove_indexes.append(i)
                        remove_indexes.reverse()
                        for idx in remove_indexes:
                            del self.parent_links[idx]
                if make_link:
                    self.parent_links.append(wantedLink)

        self.refresh_aliases()

    def uiFunc_add_selected_to_list(self, *args):
        print "Button1"

    # add items to scroll lists
    def uiFunc_add_to_parent_source(self, *args):
        for item in mc.ls(sl=True):
            if not item in [x.item for x in self.parent_source_items]:
                self.parent_source_items.append( cgmListItem(item, item) )
        
        self.parent_source_scroll.setItems( [x.alias for x in self.parent_source_items] )

        self.print_data()

    def uiFunc_add_to_parent_target(self, *args):
        for item in mc.ls(sl=True):
            if not item in [x.item for x in self.parent_target_items]:
                self.parent_target_items.append( cgmListItem(item, item, {"constraintType":"o"}) )

        self.parent_target_scroll.setItems( [x.alias for x in self.parent_target_items] )

        self.print_data()

    def uiFunc_set_connection_pose(self, *args):
        self.connection_data = self.get_ui_connection_data()
        set_connection_offsets(self.connection_data)

    # helper functions
    def save_options(self, *args):
        log.debug("Saving Options")

    def add_link(self, link, link_list):
        if self.has_link(link, link_list):
            return

        trg_index = link[1]

        if( trg_index in [x[1] for x in link_list] ):
            link_list[[x[1] for x in link_list].index(trg_index)] = link
        else:
            link_list.append(link)

    def has_link(self, link, link_list):
        for list_link in link_list:
            if list_link[0] == link[0] and list_link[1] == link[1]:
                return True
        return False

    def remove_link(self, link, link_list):
        for i, list_link in enumerate(link_list):
            if list_link[0] == link[0] and list_link[1] == link[1]:
                del link_list[i]
                break

        self.refresh_aliases()

    def print_data(self, *args):
        log.debug( "==  DATA  ==")
        log.debug( "parent source >> %s" % ','.join([x.item for x in self.parent_source_items]))
        log.debug( "parent target >> %s" % ','.join([x.item for x in self.parent_target_items]))
        for i,link in enumerate(self.parent_links):
            log.debug("link[%i] >> [%i]%s -> [%i]%s" % (i, link[0], self.parent_source_items[link[0]].item, link[1], self.parent_target_items[link[1]].item)) 

    # refresh UI displays
    def refresh_parent_scrolls(self, *args):
        self.parent_source_scroll.setItems( [x.alias for x in self.parent_source_items] )
        self.parent_target_scroll.setItems( [x.alias for x in self.parent_target_items] )

    def parse_alias(self, name):
      split_name = name.split('|')
      for i, new_name in enumerate(split_name):
        if ':' in new_name:
          split_name[i] = '(' + new_name.replace(':', ')')

      return '/'.join(split_name)

    def refresh_aliases(self, *args):
        # refresh parent aliases
        for i, item in enumerate(self.parent_source_items):
            link_items = []
            for link in self.parent_links:
                if link[0] == i:
                  link_items.append( self.parse_alias(self.parent_target_items[link[1]].item) )
            
            if link_items:
                self.parent_source_items[i].alias = "%s -> %s" % ( self.parse_alias(self.parent_source_items[i].item), ','.join(link_items))
            else:
                self.parent_source_items[i].alias = self.parse_alias(self.parent_source_items[i].item)
            self.parent_source_items[i].alias = self.parent_source_items[i].alias
        for i, item in enumerate(self.parent_target_items):
            self.parent_target_items[i].alias = self.parse_alias(self.parent_target_items[i].item)

            for link in self.parent_links:
                if link[1] == i:
                    self.parent_target_items[i].alias += " <- %s  [%s]" % (self.parse_alias(self.parent_source_items[link[0]].item), self.parent_target_items[link[1]].data["constraintType"])
                    break

            #self.parent_target_items[i].alias = self.parent_target_items[i].alias.replace('|', '/')

        self.refresh_parent_scrolls()

    # create live constraints between source and targets
    def uiFunc_make_constraints(self, *args):
        ui_data = self.get_ui_connection_data()
        for conn in ui_data:
            if conn['setPosition']:
                mc.pointConstraint( conn['source'], conn['target'], mo=True )
            if conn['setRotation']:
                mc.orientConstraint( conn['source'], conn['target'], mo=True )

    # saves link data
    def uiFunc_save_data(self, *args):
        basicFilter = "*.ccl"
        file = mc.fileDialog2(fileFilter=basicFilter, dialogStyle=2)[0]

        if file:
            stored_data = [ [x.item for x in self.parent_source_items], [x.data for x in self.parent_source_items], [x.item for x in self.parent_target_items], [x.data for x in self.parent_target_items], self.parent_links, self.connection_data ]
            f = open(file, 'w')
            f.write( json.dumps( stored_data ) )
            f.close()

    # saves link data
    def uiFunc_load_data(self, *args):
        basicFilter = "*.ccl"
        file = mc.fileDialog2(fileFilter=basicFilter, fileMode = 1, dialogStyle=2)[0]

        if file:
            f = open(file, 'r')
            loaded_data = json.loads( f.read() )
            f.close()

            for i, item in enumerate(loaded_data[0]):
                if not item in [x.item for x in self.parent_source_items]:
                    self.parent_source_items.append( cgmListItem(item, item, loaded_data[1][i]) )
            
            self.parent_source_scroll.setItems( [x.alias for x in self.parent_source_items] )

            for i, item in enumerate(loaded_data[2]):
                if not item in [x.item for x in self.parent_target_items]:
                    self.parent_target_items.append( cgmListItem(item, item, loaded_data[3][i]) )

            self.parent_target_scroll.setItems( [x.alias for x in self.parent_target_items] )

            self.parent_links = loaded_data[4]
            self.connection_data = loaded_data[5]

            self.refresh_aliases()

    # remove items from scroll lists
    def uiFunc_remove_from_parent_source(self, *args):
        idx = self.parent_source_scroll.getSelectedIdxs()[0]

        # remove links
        remove_indexes = []
        for i, link in enumerate(self.parent_links):
            if link[0] == idx:
                remove_indexes.append(i)

        #for ridx in remove_indexes:
        for i, link in enumerate(self.parent_links):
            if link[0] > idx:
                link[0] = link[0]-1
                self.parent_links[i] = link

        remove_indexes.reverse()

        for ridx in remove_indexes:
            del self.parent_links[ridx]

        del self.parent_source_items[idx]

        self.print_data()

        self.refresh_aliases()
        #self.refresh_parent_scrolls()

    def uiFunc_remove_from_parent_target(self, *args):
        idxs = self.parent_target_scroll.getSelectedIdxs()

        remove_indexes = []
        for idx in idxs:
            # remove links
            for i, link in enumerate(self.parent_links):
                if link[1] == idx:
                    remove_indexes.append(i)
                if link[1] > idx:
                    link[1] = link[1]-1
                    self.parent_links[i] = link

            del self.parent_target_items[idx]

        remove_indexes.reverse()

        for ridx in remove_indexes:
            del self.parent_links[ridx]

        self.print_data()

        self.refresh_aliases()

    # establish links upon double click
    def uiFunc_toggle_link_parent_targets(self, *args):
        src_index = self.parent_source_scroll.getSelectedIdxs()[0]
        trg_indexes = self.parent_target_scroll.getSelectedIdxs()
        
        # remove existing links from trg if only 1 is allowed
        if not self.var_mocap_allow_multiple_targets.value:
            remove_indexes = []
            for i, link in enumerate(self.parent_links):
                if link[0] == src_index and link[1] != trg_indexes[0]:
                    remove_indexes.append(i)

            remove_indexes.reverse()

            for idx in remove_indexes:
                del self.parent_links[idx]

        links = [[ src_index, x ] for x in trg_indexes]
        for link in links:
            if self.has_link(link, self.parent_links):
                self.remove_link(link, self.parent_links)
            else:
                self.add_link(link, self.parent_links)

        self.refresh_aliases()
        #self.refresh_parent_scrolls()

        for x in trg_indexes:
            self.parent_target_scroll.selectByIdx(x)
        self.parent_source_scroll.selectByIdx(src_index)

        self.print_data()

    # def uiFunc_toggle_link_orient_targets(self, *args):
    #     src_index = self.orient_source_scroll.getSelectedIdxs()[0]
    #     trg_indexes = self.orient_target_scroll.getSelectedIdxs()
        
    #     links = [[ src_index, x ] for x in trg_indexes]
    #     for link in links:
    #         if self.has_link(link, self.orient_links):
    #             self.remove_link(link, self.orient_links)
    #         else:
    #             self.add_link(link, self.orient_links)

    #     self.refresh_aliases()
    #     # self.refresh_orient_scrolls()

    #     for x in trg_indexes:
    #         self.orient_target_scroll.selectByIdx(x)
    #     self.orient_source_scroll.selectByIdx(src_index) 

    #     self.print_data()

    # on select item in scroll list
    def uiFunc_on_select_parent_source_item(self, *args):
        pass

    def uiFunc_on_select_parent_target_item(self, *args):
        pass

    # select associated link items
    def uiFunc_select_parent_source_link(self, *args):
        idx = self.parent_source_scroll.getSelectedIdxs()[0]
        if idx in [x[0] for x in self.parent_links]:
            self.parent_target_scroll.clearSelection()
            for link in self.parent_links:
                if link[0] == idx:
                    self.parent_target_scroll.selectByIdx(link[1])

    def uiFunc_select_parent_target_link(self, *args):
        if len(self.parent_target_scroll.getSelectedIdxs()) > 1:
            return

        idx = self.parent_target_scroll.getSelectedIdxs()[-1]

        if idx in [x[1] for x in self.parent_links]:
            self.parent_target_scroll.clearSelection()
            self.parent_target_scroll.selectByIdx(idx)

            link = self.parent_links[[x[1] for x in self.parent_links].index(idx)]
            self.parent_source_scroll.clearSelection()
            self.parent_source_scroll.selectByIdx(link[0])

    def update_connection_data(self, *args):
        ui_data = self.get_ui_connection_data()

        # cull old links
        old_link_indexes = []
        for i, conn in enumerate(self.connection_data):
            connection_exists = False
            for data in ui_data:
                if data['source'] == conn['source'] and data['target'] == conn['target']:
                    connection_exists = True
            if connection_exists:
                old_link_indexes.append(i)

        old_link_indexes.reverse()

        for i in old_link_indexes:
            del self.connection_data[i]

        # populate with new links
        for data in ui_data:
            connection_exists = False
            for conn in self.connection_data:
                if data['source'] == conn['source'] and data['target'] == conn['target']:
                    connection_exists = True

            if not connection_exists:
                self.connection_data.append(data)

    def get_ui_connection_data(self, *args):
        connection_data = []
        for link in self.parent_links:
            connection_data.append( {   'source':self.parent_source_items[link[0]].item, 
                                        'target':self.parent_target_items[link[1]].item, 
                                        'setPosition':'p' in self.parent_target_items[link[1]].data["constraintType"],
                                        'setRotation':True
                                        } )

        return connection_data

def set_connection_offsets(connection_data):
    '''applies offset positions to the input dictionary
    input >
    [{'source':string, 'target':string, 'setPosition':bool, 'setRotation':bool}...]
    output > 
    [{'source':string, 'target':string, 'setPosition':bool, 'setRotation':bool, 'offsetPosition':(3), 'offsetForward':(3), 'offsetUp':(3)}...]'''
    
    for i, connection in enumerate(connection_data):
        source_pos = POS.get(connection['source'], asEuclid=True)
        target_pos = POS.get(connection['target'], asEuclid=True)

        v = target_pos - source_pos
        connection['positionOffset'] = [v.x, v.y, v.z]

        v = TRANS.transformInverseDirection(connection['source'], TRANS.transformDirection(connection['target'], euclid.Vector3(0,0,1)))
        connection['offsetForward'] = [v.x, v.y, v.z]

        v = TRANS.transformInverseDirection(connection['source'], TRANS.transformDirection(connection['target'], euclid.Vector3(0,1,0)))
        connection['offsetUp'] = [v.x, v.y, v.z]


def bake(connection_data, start, end):
    bake_range = range( int(math.floor(start)), int(math.floor(end+1)))
    if end < start:
        bake_range = range(int(math.floor(end)),int(math.floor(start+1)))
        bake_range.reverse()

    for i in bake_range:
        mc.currentTime(i)
        for conn in connection_data:
            source_pos = POS.get(conn['source'])
            
            if conn['setPosition']:
                positionOffset = euclid.Vector3(0,0,0)
                if 'positionOffset' in conn:
                    pos = conn['positionOffset']
                    positionOffset = euclid.Vector3(pos[0], pos[1], pos[2])
                wanted_position = source_pos + positionOffset
                POS.set(conn['target'], [wanted_position.x, wanted_position.y, wanted_position.z])
                mc.setKeyframe('%s.translate' % conn['target'])
            
            target_pos = POS.get(conn['target'])
            if conn['setRotation']:
                offsetForward = euclid.Vector3(0,0,1)
                if 'offsetForward' in conn:
                    fwd = conn['offsetForward']
                    offsetForward = euclid.Vector3(fwd[0], fwd[1], fwd[2])
                offsetUp = euclid.Vector3(0,1,0)
                if 'offsetUp' in conn:
                    up = conn['offsetUp']
                    offsetUp = euclid.Vector3(up[0], up[1], up[2])
                fwd = TRANS.transformDirection(conn['source'], offsetForward)
                up = TRANS.transformDirection(conn['source'], offsetUp)
                SNAP.aim_atPoint(conn['target'], target_pos + fwd, vectorUp=up, mode='matrix')
                mc.setKeyframe('%s.rotate' % conn['target'])


_d_annotations = {'addSource':'Adds the selected objects to the source list.',
                  'removeSource':'Removed the selected object from the source list.',
                  'addTarget':'Adds the selected object to the target list.',
                  'removeTarget':'Removed the selected object from the target list.',
                  'linkName':'Link source and target by closest name between target and source.',
                  'linkDistance':'Link source and target by shortest distance between target and source.',
                  'setPointOrient':'Set source/target constraints to point/orient',
                  'setPointOrientAll':'Set source/target constraints to point/orient on all targets',
                  'setOrient':'Set source/target constraints to orient',
                  'setOrientAll':'Set source/target constraints to orient on all targets',
                  'setConnectionPose':'Set connection offset based off these source/target positions',
                  'sliderRange':' Push the slider range values to the int fields',
                  'selectedRange': 'Push the selected timeline range (if active)',
                  'sceneRange':'Push scene range values to the int fields',
                  '<<<':'Bake within a context of keys in range prior to the current time',
                  'All':'Bake within a context of the entire range of keys ',
                  '>>>':'Bake within a context of keys in range after the current time',
                  'attach':'Create a loc of the selected object AND start a clickMesh instance to setup an attach point on a mesh in scene'}