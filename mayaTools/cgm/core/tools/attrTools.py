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
log.setLevel(logging.DEBUG)


import maya.cmds as mc


import cgm.core.classes.GuiFactory as cgmUI
reload(cgmUI)
mUI = cgmUI.mUI

from cgm.core.lib import shared_data as SHARED



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
        
        
class uiWin_multiset(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmMultiSet_ui'    
    WINDOW_TITLE = 'cgmMultiSet - {0}'.format(__version__)
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
    
            self.__version__ = __version__
            self.__toolName__ = 'cgmMultiSet'		
            #self.l_allowedDockAreas = []
            self.WINDOW_TITLE = uiWin_multiset.WINDOW_TITLE
            #self.DEFAULT_SIZE = __defaultSize__

    def build_menus(self):
        self.uiMenu_HelpMenu = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)           
        #pass#...don't want em  
    #def setup_Variables(self):pass
    
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        _MainForm = mUI.MelColumnLayout(parent)
        cgmUI.add_Header('Objects')
        cgmUI.add_LineSubBreak()
        
        
        AttrReportRow = mUI.MelHLayout(_MainForm ,ut='cgmUIInstructionsTemplate',h=20)
        self.AttrReportField = mUI.MelLabel(AttrReportRow,
                                            bgc = SHARED._d_gui_state_colors.get('help'),
                                            label = '...',
                                            h=20)
        AttrReportRow.layout()
        
        mc.setParent()
        cgmUI.add_LineBreak()
        mc.setParent()        
        cgmUI.add_SectionBreak()
        

        #>>>Objects Buttons Row ---------------------------------------------------------------------------------------
        _row_attrCreate = mUI.MelHLayout(_MainForm,ut='cgmUISubTemplate',padding = 5)
    
        cgmUI.add_Button(_row_attrCreate,'Load Selected',
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Add the attribute names from the text field")
        cgmUI.add_Button(_row_attrCreate,'Report',
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Add the attribute names from the text field")        

        cgmUI.add_Button(_row_attrCreate,'Clear',
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         "Add the attribute names from the text field")
        _row_attrCreate.layout()  
        
        #Flags
        _row_attrFlags = mUI.MelHSingleStretchLayout(_MainForm,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_attrFlags,w=5)
        mUI.MelLabel(_row_attrFlags,l = 'Flags')
        _row_attrFlags.setStretchWidget( mUI.MelSeparator(_row_attrFlags) )
        for item in ['shared','transforms','user','numeric']:
            mUI.MelCheckBox(_row_attrFlags,label = item)
        
        _row_attrFlags.layout()
        

        
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
        

