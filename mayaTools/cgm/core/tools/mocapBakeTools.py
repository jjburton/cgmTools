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
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
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
import cgm.core.lib.string_utils as STRING

#>>> Root settings =============================================================
__version__ = '0.08312017'
__toolname__ ='mocapBakeTool'

_subLineBGC = [.75,.75,.75]

class cgmListItem(object):
    item = None
    alias = None
    #mobj = None

    def __init__(self, init_item, init_alias):
        self.item = init_item
        self.alias = init_alias
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
    DEFAULT_SIZE = 425,350
    TOOLNAME = '{0}.ui'.format(__toolname__)
    
    parent_source_items = []
    parent_target_items = []
    orient_source_items = []
    orient_target_items = []

    parent_links = []
    orient_links = []

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

        self._multiple_parent_target_cb = mUI.MelMenuItem( self.uiMenu_FirstMenu, checkBox=False, l="Allow multiple parent targets",
                 c = cgmGEN.Callback(self.save_options))

        self._multiple_orient_target_cb = mUI.MelMenuItem( self.uiMenu_FirstMenu, checkBox=True, l="Allow multiple orient targets",
                 c = cgmGEN.Callback(self.save_options))

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
        
        _parent_source = self.buildScrollForm(_parent_form, hasHeader=True, buttonArgs = [{'label':'Remove Item', 'command':self.uiFunc_remove_from_parent_source}, {'label':'Add Selected', 'command':self.uiFunc_add_to_parent_source}], headerText = 'source', allowMultiSelection=False, selectCommand=self.uiFunc_on_select_parent_source_item, doubleClickCommand=self.uiFunc_toggle_link_parent_targets)
        _parent_target = self.buildScrollForm(_parent_form, hasHeader=True, buttonArgs = [{'label':'Remove Item', 'command':self.uiFunc_remove_from_parent_target}, {'label':'Add Selected', 'command':self.uiFunc_add_to_parent_target}], headerText = 'target', allowMultiSelection=True, selectCommand=self.uiFunc_on_select_parent_target_item, doubleClickCommand=self.uiFunc_toggle_link_parent_targets)
        
        self.parent_source_scroll = _parent_source[1]
        self.parent_target_scroll = _parent_target[1]

        self.splitFormHorizontal(_parent_form, _parent_source[0], _parent_target[0])

        _orient_form = mUI.MelFormLayout(_orient_frame,ut='cgmUITemplate')
        
        _orient_source = self.buildScrollForm(_orient_form, hasHeader=True, buttonArgs = [{'label':'Remove Item', 'command':self.uiFunc_remove_from_orient_source}, {'label':'Add Selected', 'command':self.uiFunc_add_to_orient_source}], headerText = 'source', allowMultiSelection=False, selectCommand=self.uiFunc_on_select_orient_source_item, doubleClickCommand=self.uiFunc_toggle_link_orient_targets)
        _orient_target = self.buildScrollForm(_orient_form, hasHeader=True, buttonArgs = [{'label':'Remove Item', 'command':self.uiFunc_remove_from_orient_target}, {'label':'Add Selected', 'command':self.uiFunc_add_to_orient_target}], headerText = 'target', allowMultiSelection=True, selectCommand=self.uiFunc_on_select_orient_target_item, doubleClickCommand=self.uiFunc_toggle_link_orient_targets)

        self.orient_source_scroll = _orient_source[1]
        self.orient_target_scroll = _orient_target[1]
        
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
            buttonLayout = mUI.MelColumnLayout(main_form,useTemplate = 'cgmUISubTemplate')
            for btn in buttonArgs:
                button = cgmUI.add_Button(buttonLayout,btn['label'],
                             cgmGEN.Callback(btn['command'],self),
                             "Help.")
                buttons.append(button)


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


        '''
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
        
        '''
        _row.layout()
        
        #_row_objLoad2.layout()
        

        #uiFunc_load_selected(self)

        return _inside

    def uiFunc_link_by_name(self, *args):
        for i, trg in enumerate(self.parent_target_items):
            wantedLink = []
            closest = sys.maxint
            for j, src in enumerate(self.parent_source_items):
                closeness = STRING.levenshtein(trg.item, src.item)
                if closeness < closest:
                    wantedLink = [j, i]
                    closest = closeness
            
            if not self.has_link(wantedLink, self.parent_links):
                self.parent_links.append(wantedLink)

        for i, trg in enumerate(self.orient_target_items):
            wantedLink = []
            closest = sys.maxint
            for j, src in enumerate(self.orient_source_items):
                closeness = STRING.levenshtein(trg.item, src.item)
                if closeness < closest:
                    wantedLink = [j, i]
                    closest = closeness
            
            if not self.has_link(wantedLink, self.orient_links):
                self.orient_links.append(wantedLink)

        self.refresh_aliases()
        self.refresh_parent_scrolls()
        self.refresh_orient_scrolls()

    def uiFunc_link_by_distance(self, *args):
        print "Linking by distance"

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
                self.parent_target_items.append( cgmListItem(item, item) )

        self.parent_target_scroll.setItems( [x.alias for x in self.parent_target_items] )

        self.print_data()

    def uiFunc_add_to_orient_source(self, *args):
        for item in mc.ls(sl=True):
            if not item in [x.item for x in self.orient_source_items]:
                self.orient_source_items.append( cgmListItem(item, item) )
        
        self.orient_source_scroll.setItems( [x.alias for x in self.orient_source_items] )

        self.print_data()

    def uiFunc_add_to_orient_target(self, *args):
        for item in mc.ls(sl=True):
            if not item in [x.item for x in self.orient_target_items]:
                self.orient_target_items.append( cgmListItem(item, item) )
        
        self.orient_target_scroll.setItems( [x.alias for x in self.orient_target_items] )

        self.print_data()

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

    def refresh_orient_scrolls(self, *args):
        self.orient_source_scroll.setItems( [x.alias for x in self.orient_source_items] )
        self.orient_target_scroll.setItems( [x.alias for x in self.orient_target_items] )

    def refresh_aliases(self, *args):
        # refresh parent aliases
        for i, item in enumerate(self.parent_source_items):
            link_items = []
            for link in self.parent_links:
                if link[0] == i:
                    link_items.append( self.parent_target_items[link[1]].item )
            
            if link_items:
                self.parent_source_items[i].alias = "%s -> %s" % (self.parent_source_items[i].item, ','.join(link_items))
            else:
                self.parent_source_items[i].alias = self.parent_source_items[i].item

        for i, item in enumerate(self.parent_target_items):
            self.parent_target_items[i].alias = self.parent_target_items[i].item

            for link in self.parent_links:
                if link[1] == i:
                    self.parent_target_items[i].alias += " <- %s" % self.parent_source_items[link[0]].item
                    break

        # refresh orient aliases
        for i, item in enumerate(self.orient_source_items):
            link_items = []
            for link in self.orient_links:
                if link[0] == i:
                    link_items.append( self.orient_target_items[link[1]].item )
            
            if link_items:
                self.orient_source_items[i].alias = "%s -> %s" % (self.orient_source_items[i].item, ','.join(link_items))
            else:
                self.orient_source_items[i].alias = self.orient_source_items[i].item

        for i, item in enumerate(self.orient_target_items):
            self.orient_target_items[i].alias = self.orient_target_items[i].item

            for link in self.orient_links:
                if link[1] == i:
                    self.orient_target_items[i].alias += " <- %s" % self.orient_source_items[link[0]].item
                    break

        self.refresh_parent_scrolls()
        self.refresh_orient_scrolls()

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
        self.refresh_parent_scrolls()

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


        remove_indexes.reverse()

        for ridx in remove_indexes:
            del self.parent_links[ridx]

        del self.parent_target_items[idx]

        self.print_data()

        self.refresh_aliases()
        self.refresh_parent_scrolls()

    def uiFunc_remove_from_orient_source(self, *args):
        idx = self.orient_source_scroll.getSelectedIdxs()[0]

        # remove links
        remove_indexes = []
        for i, link in enumerate(self.orient_links):
            if link[0] == idx:
                remove_indexes.append(i)

        #for ridx in remove_indexes:
        for i, link in enumerate(self.orient_links):
            if link[0] > idx:
                link[0] = link[0]-1
                self.orient_links[i] = link

        remove_indexes.reverse()

        for ridx in remove_indexes:
            del self.orient_links[ridx]

        del self.orient_source_items[idx]

        self.print_data()

        self.refresh_aliases()
        self.refresh_orient_scrolls()

    def uiFunc_remove_from_orient_target(self, *args):
        idxs = self.orient_target_scroll.getSelectedIdxs()

        remove_indexes = []
        for idx in idxs:
            # remove links
            for i, link in enumerate(self.orient_links):
                if link[1] == idx:
                    remove_indexes.append(i)
                if link[1] > idx:
                    link[1] = link[1]-1
                    self.orient_links[i] = link


        remove_indexes.reverse()

        for ridx in remove_indexes:
            del self.orient_links[ridx]

        del self.orient_target_items[idx]

        self.print_data()

        self.refresh_aliases()
        self.refresh_orient_scrolls()

    # establish links upon double click
    def uiFunc_toggle_link_parent_targets(self, *args):
        src_index = self.parent_source_scroll.getSelectedIdxs()[0]
        trg_indexes = self.parent_target_scroll.getSelectedIdxs()
        
        links = [[ src_index, x ] for x in trg_indexes]
        for link in links:
            if self.has_link(link, self.parent_links):
                self.remove_link(link, self.parent_links)
            else:
                self.add_link(link, self.parent_links)

        self.refresh_aliases()
        self.refresh_parent_scrolls()

        for x in trg_indexes:
            self.parent_target_scroll.selectByIdx(x)
        self.parent_source_scroll.selectByIdx(src_index)

        self.print_data()

    def uiFunc_toggle_link_orient_targets(self, *args):
        src_index = self.orient_source_scroll.getSelectedIdxs()[0]
        trg_indexes = self.orient_target_scroll.getSelectedIdxs()
        
        links = [[ src_index, x ] for x in trg_indexes]
        for link in links:
            if self.has_link(link, self.orient_links):
                self.remove_link(link, self.orient_links)
            else:
                self.add_link(link, self.orient_links)

        self.refresh_aliases()
        self.refresh_orient_scrolls()

        for x in trg_indexes:
            self.orient_target_scroll.selectByIdx(x)
        self.orient_source_scroll.selectByIdx(src_index) 

        self.print_data()

    # on select item in scroll list
    def uiFunc_on_select_parent_source_item(self, *args):
        pass

    def uiFunc_on_select_parent_target_item(self, *args):
        pass

    def uiFunc_on_select_orient_source_item(self, *args):
        pass

    def uiFunc_on_select_orient_target_item(self, *args):
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
        idx = self.parent_target_scroll.getSelectedIdxs()[-1]

        if idx in [x[1] for x in self.parent_links]:
            self.parent_target_scroll.clearSelection()
            self.parent_target_scroll.selectByIdx(idx)

            link = self.parent_links[[x[1] for x in self.parent_links].index(idx)]
            self.parent_source_scroll.clearSelection()
            self.parent_source_scroll.selectByIdx(link[0])

    def uiFunc_select_orient_source_link(self, *args):
        idx = self.orient_source_scroll.getSelectedIdxs()[0]
        if idx in [x[0] for x in self.orient_links]:
            self.orient_target_scroll.clearSelection()
            for link in self.orient_links:
                if link[0] == idx:
                    self.orient_target_scroll.selectByIdx(link[1])

    def uiFunc_select_orient_target_link(self, *args):
        idx = self.orient_target_scroll.getSelectedIdxs()[-1]

        if idx in [x[1] for x in self.orient_links]:
            self.orient_target_scroll.clearSelection()
            self.orient_target_scroll.selectByIdx(idx)

            link = self.orient_links[[x[1] for x in self.orient_links].index(idx)]
            self.orient_source_scroll.clearSelection()
            self.orient_source_scroll.selectByIdx(link[0])

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
 