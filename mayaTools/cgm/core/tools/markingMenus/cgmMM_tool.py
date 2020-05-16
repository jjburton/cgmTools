import maya.cmds as mc
import maya.mel as mel
import pprint
import time
import webbrowser
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGEN
#reload(cgmGEN)
#from cgm.core.tools.markingMenus import cgmMMTemplate as mmTemplate
from cgm.core.lib.zoo import baseMelUI as mUI
import cgm.core.classes.GuiFactory as cgmUI
#reload(cgmUI)
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import position_utils as POS
from cgm.core.lib import shape_utils as SHAPES
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import locator_utils as LOC
from cgm.core.lib import attribute_utils as ATTRS
from cgm.core.tools import locinator as LOCINATOR
import cgm.core.lib.arrange_utils as ARRANGE
import cgm.core.lib.transform_utils as TRANS
import cgm.core.tools.markingMenus.lib.mm_utils as MMUTILS

import cgm.core.tools.toolbox as TOOLBOX
import cgmToolbox
from cgm.core.tools import dynParentTool as DYNPARENTTOOL
from cgm.core.mrs import Builder as RBUILDER
from cgm.core.lib import node_utils as NODES
import cgm.core.mrs.Animate as MRSANIMATE
from cgm.lib import search
from cgm.lib import locators
from cgm.tools.lib import tdToolsLib#...REFACTOR THESE!!!!
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
from cgm.core.tools import meshTools
from cgm.core.tools import attrTools as ATTRTOOLS
import cgm.core.tools.setTools as SETTOOLS
import cgm.core.rig.general_utils as RIGGEN
import cgm.core.lib.name_utils as NAMES
from cgm.core.tools.lib import tool_chunks as UICHUNKS
import cgm.core.tools.lib.tool_calls as TOOLCALLS
from cgm.core.tools.lib import snap_calls as UISNAPCALLS
import cgm.core.tools.lib.annotations as TOOLANNO
import cgm.core.rig.joint_utils as JOINTS
"""
reload(UICHUNKS)
reload(MMPuppet)
reload(LOCINATOR)
reload(ATTRS)
reload(LOC)
reload(SNAP)
reload(SHAPES)
reload(SHARED)
reload(RIGGING)
reload(ATTRTOOLS)
reload(meshTools)
reload(MMCONTEXT)
reload(RBUILDER)"""

from cgm.core.lib.ml_tools import (ml_breakdownDragger,
                                   ml_resetChannels,
                                   ml_deleteKey,
                                   ml_setKey,
                                   ml_hold,
                                   ml_stopwatch,
                                   ml_arcTracer,
                                   ml_convertRotationOrder,
                                   ml_copyAnim)

def run():
    try:
        cgmMarkingMenu()
        #mmWindow = cgmMarkingMenu()
    except Exception,err:
        log.error("Failed to load. err:{0}".format(err))
        #for a in err.args():
        #    print a
        
_str_popWindow = 'cgmMM'#...outside to push to killUI

class cgmMarkingMenu2(cgmUI.markingMenu):
    POPWINDOW = _str_popWindow
    
    def createUI2(self):
        #try:mc.menu(parent,e = True, deleteAllItems = True)
        #except Exception,err:
        #    log.error("Failed to delete menu items")
        #    for a in err.args():
        #        print a
                
        self.var_clockStart.value = time.clock()
                
        
        mc.showWindow('cgmMM')
        
class cgmMarkingMenu(cgmUI.markingMenu):
    POPWINDOW = _str_popWindow

    def varBuffer_define(self,optionVar):
        _str_func = 'varBuffer_define'

        sel = mc.ls(sl=True, flatten = True) or []

        if not sel:
            log.error("|{0}| >> No selection found. Cannot define")
            return False

        optionVar.clear()

        for o in sel:
            optionVar.append(NAMES.get_short(o))
        return True

    def varBuffer_add(self,optionVar):
        _str_func = 'varBuffer_add'

        sel = mc.ls(sl=True, flatten = True) or []
        if not sel:
            log.error("|{0}| >> No selection found. Cannot define")
            return False

        for o in sel:
            optionVar.append(o)

    def varBuffer_remove(self,optionVar):
        _str_func = 'varBuffer_add'

        sel = mc.ls(sl=True, flatten = True) or []
        if not sel:
            log.error("|{0}| >> No selection found. Cannot define")
            return False

        for o in sel:
            optionVar.remove(o)

    def button_action(self, command = None):
        """
        execute a command and let the menu know not do do the default button action but just kill the ui
        """	
        log.info("{0} >> buttonAction: {1}".format(self._str_MM,command))                    
        self.var_mmAction.value=1			
        if command:
            try:command()
            except Exception,err:
                log.info("{0} button >> error {1}".format(self._str_MM, err))     
    
    def button_CallBack(self, func, *a, **kws ):
        print func
        if a:print a
        if kws:print kws
        mmCallback(func,*a,**kws)
        MMUTILS.kill_mmTool()
        

    def toggleVarAndReset(self, optionVar):
        try:
            self.mmActionOptionVar.value=1						
            optionVar.toggle()
            log.info("{0}.toggleVarAndReset>>> {1} : {2}".format(self._str_MM,optionVar.name,optionVar.value))
        except Exception,error:
            log.error(error)
            print "MM change var and reset failed!"

    def reset(self):
        log.info("{0} >> reset".format(self._str_MM))        
        mUI.Callback(cgmUI.do_resetGuiInstanceOptionVars(self.l_optionVars,False))
        #MMUTILS.killUI()

    def report(self):
        cgmUI.log_selfReport(self)
        log.debug("{0} >> Children...".format(self._str_MM))  
        #for c in self.get_uiChildren():
            #log.debug(c)
    
    @cgmGEN.Timer        
    def createUI(self):        
        """
        try:mc.menu(parent,e = True, deleteAllItems = True)
        except Exception,err:
            log.error("Failed to delete menu items")
            for a in err.args():
                print a"""
        parent = 'cgmMM'
        _str_func = "createUI"
        self.setup_optionVars()
        #pprint.pprint(self.__dict__)
        
        self._d_radial_menu = {}
        self._l_res = []
        self._l_sel = mc.ls(sl=True,flatten=True, shortNames = False)
        self._b_sel = False
        self._l_contextTypes = []
        
        if self._l_sel:self._b_sel = True
        self._b_sel_pair = False
        self._b_sel_few = False
        self._len_sel = len(self._l_sel)
        if self._len_sel  >= 2:
            self._b_sel_pair = True
        if self._len_sel >2:
            self._b_sel_few = True
            
        self.mmCallback = mmCallback
        
        log.debug("|{0}| >> build_menu".format(self._str_MM))                
        
        
        #Radial Section --------------------------------------------------------------
        _mode = self.var_menuMode.value
        if _mode == 0:
            log.debug("|{0}| >> td mode...".format(self._str_MM))  
            
            if self.var_contextTD.value == 'selection':
                """
                log.debug("|{0}| >> selection mode...".format(self._str_MM))  
                for o in self._l_sel:
                    _t = VALID.get_mayaType(o)
                    if _t not in self._l_contextTypes:
                        self._l_contextTypes.append( _t)
                    log.debug("|{0}| >> obj: {1} | type: {2}...".format(self._str_MM, o, _t))  """
            self.bUI_radialRoot_td(parent)
        elif _mode == 1:
            log.debug("|{0}| >> anim mode...".format(self._str_MM))                                        
            self.bUI_radialRoot_anim(parent)
        elif _mode == 2:
            log.debug("|{0}| >> sets mode...".format(self._str_MM))                                        
            self.bUI_radialRoot_anim(parent)        
        elif _mode == 3:
            log.debug("|{0}| >> puppet mode...".format(self._str_MM))
            self.bUI_radialRoot_puppet(parent)  
            MRSANIMATE.mmUI_radial(self, parent)
        elif _mode == 4:
            log.debug("|{0}| >> dev mode...".format(self._str_MM))                                        
            self.bUI_radialRoot_dev(parent)
        else:
            log.error("Don't know what to do with mode: {0}".format(_mode))
            
        
        
        #Bottom section --------------------------------------------------------------
                                      
        #mc.menuItem(parent=parent,l = "-"*25,en = False)
        mc.menuItem(p=parent,l = "-"*25,en = False)
        
        if _mode == 0:
            log.debug("|{0}| >> td mode bottom...".format(self._str_MM))  
            self.bUI_menuBottom_td(parent)
        elif _mode == 1:
            log.debug("|{0}| >> anim mode bottom...".format(self._str_MM))
            self.bUI_menuBottom_anim(parent)
        elif _mode == 2:
            log.debug("|{0}| >> sets mode bottom...".format(self._str_MM))
            #MMPuppet.uiOptionMenu_build(self, parent)
            self.bUI_menuBottom_sets(parent)            
        elif _mode == 3:
            log.debug("|{0}| >> puppet mode bottom...".format(self._str_MM))
            MRSANIMATE.mmUI_lower(self, parent)
            
        elif _mode == 4:
            log.debug("|{0}| >> dev mode bottom...".format(self._str_MM))              
          
        try:#>>> Menu mode
            self.l_menuModes = ['td','anim','sets','puppet','dev']
            _str_section = 'menu mode toggle'
    
            uiMenu_menuMode = mc.menuItem( p=parent, l='Mode', subMenu=True)    
            uiRC_menuMode = mc.radioMenuItemCollection()#mUI.MelRadioMenuCollection()
            #self.uiOptions_menuMode = []		
            _v = self.var_menuMode.value
            
            for i,item in enumerate(self.l_menuModes):
                if i == _v:
                    _rb = True
                else:_rb = False
                """self.uiOptions_menuMode.append(self.uiRC_menuMode.createButton(uiMenu_menuMode,label=item,
                                                                               c = mmCallback(self.var_menuMode.setValue,i),
                                                                               rb = _rb))"""   
                mc.menuItem(parent=uiMenu_menuMode,collection = uiRC_menuMode, 
                            l=item,
                            #c = lambda *a:self.var_menuMode.setValue(i),
                            #c = mmCallback(self.var_menuMode.setValue,i),
                            c = cgmGEN.Callback(self.var_menuMode.setValue,i),                            
                            rb = _rb)                
        except Exception,err:
            log.error("|{0}| failed to load. err: {1}".format(_str_section,err))	        
                 
        
        #>>>Help menu -------------------------------------------------------------------------------------
        uiHelp = mc.menuItem(p=parent, l='Help', subMenu=True)
        
        mc.menuItem(p=uiHelp,l='Report',
                    c = cgmGEN.Callback(self.report))
        
        mc.menuItem(p=uiHelp, l="Docs",
                    c = lambda *a: webbrowser.open("http://www.cgmonks.com/tools/maya-tools/cgmmarkingmenu/"))                            
                    #c='import webbrowser;webbrowser.open("http://www.cgmonks.com/tools/maya-tools/cgmmarkingmenu/");')        
        
        mc.menuItem(p=uiHelp,l = 'Reset Options',
                    c=cgmGEN.Callback(self.button_action,self.reset))           
        mc.menuItem(p=uiHelp,l = 'Force Kill MM',
                    c=lambda *a:MMUTILS.kill_mmTool())
                    #c=cgmGEN.Callback(self.button_action,self.reset))   
        mc.menuItem(p=uiHelp, l="Reload marking menu lib",
                    c=lambda *a:self.reloadLib())
        mc.menuItem(p=uiHelp,l='Reload local python',
                    c = lambda *a: mel.eval('python("from cgm.core import cgm_Meta as cgmMeta;from cgm.core import cgm_Deformers as cgmDeformers;from cgm.core import cgm_General as cgmGen;from cgm.core.rigger import RigFactory as Rig;from cgm.core import cgm_PuppetMeta as cgmPM;from cgm.core import cgm_RigMeta as cgmRigMeta;import Red9.core.Red9_Meta as r9Meta;import cgm.core;cgm.core._reload();import maya.cmds as mc;import cgm.core.cgmPy.validateArgs as cgmValid")'))        
        
        #>>>Lower menu footer -------------------------------------------------------------------------------------        
        mc.menuItem(p=parent,l = 'cgmMM - {0}'.format(self.l_menuModes[self.var_menuMode.value]),en=False)
        
        #pprint.pprint(self.__dict__)
        #mc.showWindow('cgmMM')
    
    #@cgmGEN.Timer    
    def setup_optionVars(self):
        self.create_guiOptionVar('menuMode', defaultValue = 0)            
        self.var_keyType = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
        self.var_keyMode = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)
        self.var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode', defaultValue = 'world')        
        self.var_resetMode = cgmMeta.cgmOptionVar('cgmVar_ChannelResetMode', defaultValue = 0)
        self.var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
        self.var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)
        self.var_objDefaultOutAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultOutAxis', defaultValue = 3)                        
        self.var_contextTD = cgmMeta.cgmOptionVar('cgmVar_contextTD', defaultValue = 'selection')
        
        self.var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])            
        self.var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
        self.var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetMode', defaultValue=0)
        self.var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0) 
        self.var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)
        self.var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2) 

        LOCINATOR.uiSetupOptionVars(self)
        #MMPuppet.uiSetupOptionVars(self)
        TOOLBOX.uiSetupOptionVars_curveCreation(self)
        
    def reloadLib(self):
        reload(cgmUI)
        reload(MMUTILS)
        reload(DYNPARENTTOOL)
        reload(MRSANIMATE)
        
    #@cgmGEN.Timer
    def bUI_radialRoot_td(self,parent):
        #Radial---------------------------------------------------
        self.bUI_radial_snap(parent,'N')
        ###self.bUI_radial_dynParent(parent,'NW')
        self.bUI_radial_tdUtils(parent,'NW')
        self.bUI_radial_create(parent,'NE')
        self.bUI_radial_rayCreate(parent,'E')
        self.bUI_radial_copy(parent,'W')
        LOCINATOR.uiRadialMenu_root(self,parent,'SE',cgmGEN.Callback)      
        
        mc.menuItem(p=parent,
                    en = self._b_sel,
                    l = 'Reset',
                    c = lambda *a:RIGGEN.reset_channels_fromMode(mode=self.var_resetMode.value,
                                                                 selectedChannels=1),
                    #c = mmCallback(ml_resetChannels.main,**{'transformsOnly': self.var_resetMode.value}),
                    rp = "S")           
        
        
    #@cgmGEN.Timer    
    def bUI_radialRoot_anim(self,parent):
        self.bUI_radial_snap(parent,'N')
        
        mc.menuItem(p=parent,
                   en = self._b_sel,
                   l = 'dragBetween',
                   c = lambda *a:ml_breakdownDragger.drag(),
                   #c = mmCallback(ml_breakdownDragger.drag),
                   rp = "SE")        
        mc.menuItem(p=parent,
                    en = self._b_sel,
                    l = 'Reset',
                    c = lambda *a:RIGGEN.reset_channels_fromMode(mode=self.var_resetMode.value),
                    #c = mmCallback( ml_resetChannels.main,**{'transformsOnly': self.var_resetMode.value}),
                    rp = "S")   
 
        
        mc.menuItem(p=parent,l='Key',subMenu=True,
                    en = self._b_sel,
                    rp = 'E')
        
        
        if self._b_sel:
            mc.menuItem(l = 'Regular',
                        c = lambda*a:setKey('default'),
                        #c= mmCallback(setKey,'default'),
                        rp = "E")            
            mc.menuItem(l = 'Breakdown',
                        c=lambda*a:setKey('breakdown'),
                        #c= mmCallback(setKey,'breakdown'),
                        rp = "SE")  
            mc.menuItem(l = 'Delete',
                        c = lambda*a:deleteKey(),
                        #c= mmCallback(deleteKey),
                        rp = "N")     
            
        LOCINATOR.uiRadialMenu_root(self,parent,'NE')
        
    def bUI_radialRoot_sets(self,parent):
        self.bUI_radial_snap(parent,'N')
        """
        var_mmSetToolsMode = cgmMeta.cgmOptionVar('cgmVar_SetToolsMarkingMenuMode', defaultValue = 0)
        val_mmSetToolsMode = var_mmSetToolsMode.value
        
        _b_sel = self._b_sel
        
        if val_mmSetToolsMode:
            if val_mmSetToolsMode == 1:
                _mode = 'active'
            else:
                _mode = 'loaded'
            _sel_sets = SETTOOLS.uiFunc_multiSetsAction(_mode, action='query')
            if _sel_sets:
                _b_sel = True"""
                
        mc.menuItem(p=parent,
                   en = _b_sel,
                   l = 'dragBetween',
                   #c = lambda*a:SETTOOLS.uiFunc_selectAndDo(ml_breakdownDragger.drag),
                   c = lambda *a:ml_breakdownDragger.drag(),                   
                   rp = "SE")        
        mc.menuItem(p=parent,
                    en = _b_sel,
                    l = 'Reset',
                    #c = lambda *a:SETTOOLS.uiFunc_selectAndDo(ml_resetChannels.main,**{'transformsOnly': self.var_resetMode.value}),                    
                    c = lambda *a:RIGGEN.reset_channels_fromMode(self.var_resetMode.value),
                    rp = "S")   
 
        
        mc.menuItem(p=parent,l='Key',subMenu=True,
                    en = _b_sel,
                    rp = 'E')
        
        if _b_sel:
            mc.menuItem(l = 'Regular',
                        c = lambda*a:SETTOOLS.uiFunc_selectAndDo(setKey,'default'),
                        #c = lambda*a:setKey('default'),
                        rp = "E")            
            mc.menuItem(l = 'Breakdown',
                        c = lambda*a:SETTOOLS.uiFunc_selectAndDo(setKey,'breakdown'),                        
                        #c=lambda*a:setKey('breakdown'),
                        rp = "SE")  
            mc.menuItem(l = 'Delete',
                        c = lambda*a:SETTOOLS.uiFunc_selectAndDo(deleteKey),                                                
                        #c = lambda*a:deleteKey(),
                        rp = "N")     
            
        LOCINATOR.uiRadialMenu_root(self,parent,'NE')
        
    def bUI_radialRoot_puppet(self,parent):
        self.bUI_radial_snap(parent,'N')    
    
        mc.menuItem(p=parent,
                    en = self._b_sel,
                    l = 'dragBetween',
                    c = lambda *a:ml_breakdownDragger.drag(),
                    #c = mmCallback(ml_breakdownDragger.drag),
                    rp = "SE")        
        mc.menuItem(p=parent,
                    en = self._b_sel,
                    l = 'Reset',
                    c = lambda *a:RIGGEN.reset_channels_fromMode(mode=self.var_resetMode.value,
                                                                selectedChannels=1),
                    rp = "S")   
  
        mc.menuItem(p=parent,l='Key',subMenu=True,
                    en = self._b_sel,
                    rp = 'E')
        
        if self._b_sel:
            mc.menuItem(l = 'Regular',
                        c = lambda *a:setKey('default'),
                        #c= mmCallback(setKey,'default'),
                        rp = "E")            
            mc.menuItem(l = 'Breakdown',
                        c = lambda *a:setKey('breakdown'),
                        #c= mmCallback(setKey,'breakdown'),
                        rp = "SE")  
            mc.menuItem(l = 'Delete',
                        c = lambda *a:deleteKey(),
                        #c= mmCallback(deleteKey),
                        rp = "N")     
            
        LOCINATOR.uiRadialMenu_root(self,parent,'NE')        
        MRSANIMATE.mmUI_radial(self, parent)
        
    def bUI_radialRoot_dev(self,parent):
        #Radial---------------------------------------------------
        self.bUI_radial_snap(parent,'N')
        self.bUI_radial_dynParent(parent,'NW')
        self.bUI_radial_create(parent,'N')
        self.bUI_radial_copy(parent,'W')
        self.bUI_radial_control(parent,'SW')
        self.bUI_radial_arrange(parent,'SE')
        #Bottom---------------------------------------------------
        
    def bUI_menuBottom_sets(self,parent):
        DYNPARENTTOOL.uiMenu_changeSpace(self,parent)             
        #mc.menuItem(p=parent,l = 'cgmSetTools',
        #            c = lambda *a:TOOLCALLS.setTools())
        
        #Sets menu ================================================================================
        mc.menuItem(p=parent,l = "- Object Sets -",en = False)
        mc.menuItem(p=parent,l = 'UI',
                    c=lambda*a:mc.evalDeferred(TOOLCALLS.setTools,lp=True)                    
                    #c = lambda *a:TOOLCALLS.setTools(),
                    )
        
        var_mmSetToolsMode = cgmMeta.cgmOptionVar('cgmVar_SetToolsMarkingMenuMode', defaultValue = 0)
        
        var_ActiveSets = cgmMeta.cgmOptionVar('cgmVar_activeObjectSets', defaultValue = [''])
        len_active = len(var_ActiveSets.value)
        
        var_LoadedSets = cgmMeta.cgmOptionVar('cgmVar_loadedObjectSets', defaultValue = [''])        
        len_loaded = len(var_LoadedSets.value)
        
        
        uiRC = mc.radioMenuItemCollection()
        #self.uiOptions_menuMode = []		
        _v = var_mmSetToolsMode.value
    
        for i,item in enumerate(['none',
                                 "Active ({0})".format(len_active),
                                 "Loaded ({0})".format(len_loaded)]):
            if i == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(p=parent,collection = uiRC,
                        label=item,
                        c = cgmGEN.Callback(var_mmSetToolsMode.setValue,i),
                        rb = _rb)                    
        
        mc.menuItem(p=parent,l = "-"*25,en = False)        

        mc.menuItem(p=parent,l = 'Key',
                    c = lambda*a:SETTOOLS.uiFunc_selectAndDo(setKey,'default'))
        mc.menuItem(p=parent,l = 'Tween',
                    c = lambda *a:SETTOOLS.uiFunc_multiSetsAction(None,'tween'))                    
                    #c = lambda*a:SETTOOLS.uiFunc_selectAndDo(ml_breakdownDragger.drag))
                    #c = lambda*a:SETTOOLS.uiFunc_selectAndDo(setKey,'breakdown'))
        mc.menuItem(p=parent,l = 'Delete Key',
                    c = lambda*a:SETTOOLS.uiFunc_selectAndDo(deleteKey))
        
        
        
        
        #c = lambda*a:SETTOOLS.uiFunc_selectAndDo(ml_breakdownDragger.drag),
        
        mc.menuItem(p=parent,l = 'Select',
                    c = lambda *a:SETTOOLS.uiFunc_multiSetsAction(None,'select'))
        mc.menuItem(p=parent,l = 'Reset',
                    c = lambda *a:SETTOOLS.uiFunc_selectAndDo(RIGGEN.reset_channels_fromMode,self.var_resetMode.value))                   
        mc.menuItem(p=parent,l = 'Report',
                    c = lambda *a:SETTOOLS.uiFunc_multiSetsAction(None,'report'))
        

        mc.menuItem(p=parent,l = "-"*25,en = False)        
        
        
        #uiUtils= mc.menuItem(parent = parent, l='Utilities', subMenu=True)
        #UICHUNKS.uiSection_animUtils(uiUtils)        

        #mc.menuItem(p=parent,l = "-"*25,en = False)
        

        #uiOptions = mc.menuItem(parent = parent, l='Options', subMenu=True)
        
        #self.bUI_optionMenu_keyType(uiOptions) 
        #self.bUI_optionMenu_keyMode(uiOptions)
        #self.bUI_optionMenu_resetMode(uiOptions)
        #LOCINATOR.uiOptionMenu_matchMode(self,uiOptions)        
        #

        
    def bUI_menuBottom_anim(self,parent):
        DYNPARENTTOOL.uiMenu_changeSpace(self,parent)             
        
        uiUtils= mc.menuItem(parent = parent, l='Utilities', subMenu=True)
        
        UICHUNKS.uiSection_animUtils(uiUtils)        

        mc.menuItem(p=parent,l = "-"*25,en = False)
                    
        uiOptions = mc.menuItem(parent = parent, l='Options', subMenu=True)
        
        self.bUI_optionMenu_keyType(uiOptions) 
        self.bUI_optionMenu_keyMode(uiOptions)
        self.bUI_optionMenu_resetMode(uiOptions)
        LOCINATOR.uiOptionMenu_matchMode(self,uiOptions)        
        self.bUI_optionMenu_aimMode(uiOptions)
        self.bUI_optionMenu_objDefaults(uiOptions)
        self.bUI_optionMenu_rayCast(uiOptions)
        
        uiBuffers = mc.menuItem(parent = parent, l='Buffers', subMenu=True)
        LOCINATOR.uiBuffer_control(self, uiBuffers)
        self.bUI_rayCastBuffer(uiBuffers)
        
    #@cgmGEN.Timer    
    def bUI_menuBottom_td(self,parent):
        """
        _contextMode = self.var_contextTD.value
        
        UICHUNKS.uiSection_selection(parent)

        #UICHUNKS.uiSection_distance(parent,self._l_sel,self._b_sel_pair)	

        
        if 'joint' in self._l_contextTypes or _contextMode != 'selection':
            uiJoints = mc.menuItem(parent = parent, l='Joints', subMenu=True)
            
                           
            mc.menuItem(l='Axis*', subMenu = True)
            mc.menuItem(l='Show',
                        c = lambda *a:MMCONTEXT.set_attrs(self,'displayLocalAxis',1,self.var_contextTD.value,'joint'))
                        
            mc.menuItem(l='Hide',
                        c = lambda *a:MMCONTEXT.set_attrs(self,'displayLocalAxis',0,self.var_contextTD.value,'joint'))
                        
            mc.menuItem(parent = uiJoints,
                        l='cometJO',
                        c=lambda *a: mel.eval('cometJointOrient'),
                        ann="General Joint orientation tool\n by Michael Comet")  
            
            mc.menuItem(parent=uiJoints, 
                        l = 'Freeze Orient',
                        ann = "Freeze the joint orientation",                                        
                        c = lambda *a:MMCONTEXT.func_process(JOINTS.freezeOrientation, None, 'each','FreezeOrientation',True,**{}),                                                                      
                        )    
            
            #-----------------------------------------------------------------------------
            UICHUNKS.uiSection_sdk(parent)
                       
        
        #-----------------------------------------------------------------------------
        _go = False
        if _contextMode == 'selection':
            for n in ['mesh','nurbsSurface','nurbsCurve','transform','joint']:
                if n in  self._l_contextTypes:
                    _go = True
                    break
        elif not self._b_sel:
            pass
        else:_go = True
        
        if _go:
            UICHUNKS.uiSection_arrange(parent,self._len_sel, self._b_sel_pair)
            #>>>Shape ==============================================================================================
            UICHUNKS.uiSection_shapes(parent,self._l_sel,self._b_sel_pair)

            #>>>Curve ==============================================================================================
            UICHUNKS.uiSection_curves(parent)
            
                      
            #>>>Mesh ==============================================================================================
            UICHUNKS.uiSection_mesh(parent)
            
        
            #>>>Skin ==============================================================================================
            UICHUNKS.uiSection_skin(parent)
            

        #>>>Nodes ==============================================================================================
        UICHUNKS.uiSection_nodes(parent)
        
"""
        mc.menuItem(parent = parent, l='cgmToolbox',
                    ann=TOOLANNO.cgmToolbox.get('ui'),
                    c=lambda *a:TOOLBOX.ui())
        
        mc.menuItem(parent = parent, l='Locinator',
                    c=lambda *a:TOOLCALLS.locinator())
        
        mc.menuItem(parent = parent, l='SetTools',
                    c=lambda *a:TOOLCALLS.setTools())
        
        mc.menuItem(parent = parent, l='cgmJointTools',
                    c=lambda *a:TOOLCALLS.jointTools())
        
        mc.menuItem(parent = parent, l='DynParentTool',
                    c=lambda *a:TOOLCALLS.dynParentTool())
        
        mc.menuItem(parent = parent, l='AttrTools',
                    c=lambda *a:TOOLCALLS.attrTools())
        
        mc.menuItem(parent = parent, l='cgmSnap',
                    c=lambda *a:TOOLCALLS.cgmSnapTools())
        
        mc.menuItem(parent = parent,
                    l='mrsBuilder',
                    c=lambda *a: mc.evalDeferred(TOOLCALLS.mrsUI))
        mc.menuItem(parent = parent,
                    l='mrsAnimate',
                    c=lambda *a: mc.evalDeferred(TOOLCALLS.mrsANIMATE))
        #UICHUNKS.uiSection_arrange(parent,self._len_sel, self._b_sel_pair)
        #UICHUNKS.uiSection_shapes(parent,self._l_sel,self._b_sel_pair)
        #UICHUNKS.uiSection_curves(parent)
        #UICHUNKS.uiSection_mesh(parent)
        #UICHUNKS.uiSection_nodes(parent)
        
        #-----------------------------------------------------------------------------         
        mc.menuItem(p=parent,l = "-"*25,en = False)
        mc.menuItem(parent = parent, l='Options',
                    ann='Open cgmToolbox where many options are accessible',
                    c=lambda *a:TOOLBOX.uiByTab(2))
        
        #uiOptions = mc.menuItem(parent = parent, l='Options', subMenu=True)
        #self.bUI_optionMenu_contextTD(uiOptions)
        #self.bUI_optionMenu_objDefaults(uiOptions)
        #self.bUI_optionMenu_aimMode(uiOptions)
        #self.bUI_optionMenu_resetMode(uiOptions)
        #self.bUI_optionMenu_rayCast(uiOptions)
        #LOCINATOR.uiOptionMenu_matchMode(self,uiOptions)
        
        #mc.menuItem(parent = uiOptions, l='Option UI', 
        #            c=lambda *a:cgmToolbox.uiByTab(2))
        
        #uiBuffers = mc.menuItem(parent = parent, l='Buffers', subMenu=True)
        #LOCINATOR.uiBuffer_control(self, uiBuffers)
        #self.bUI_rayCastBuffer(uiBuffers)
        
    def bUI_optionMenu_keyType(self, parent):
        try:#>>> KeyType 
            _str_section = 'key type'
    
            uiMenu = mc.menuItem(p=parent, l='Key Type', subMenu=True)    
            uiRC = mc.radioMenuItemCollection()
            #self.uiOptions_menuMode = []		
            _v = self.var_keyType.value
            
            for i,item in enumerate(['reg','breakdown']):
                if i == _v:
                    _rb = True
                else:_rb = False
                mc.menuItem(p=uiMenu,collection = uiRC,
                            label=item,
                            c = mmCallback(self.var_keyType.setValue,i),
                            rb = _rb)                
        except Exception,err:
            log.error("|{0}| failed to load. err: {1}".format(_str_section,err))    
            
    def bUI_optionMenu_keyMode(self, parent):
        try:#>>> KeyMode 
            _str_section = 'key mode'
    
            uiMenu =mc.menuItem(p=parent, l='Key Mode', subMenu=True)    
            uiRC = mc.radioMenuItemCollection()
            #self.uiOptions_menuMode = []		
            _v = self.var_keyMode.value
            
            for i,item in enumerate(['Default','Channelbox']):
                if i == _v:
                    _rb = True
                else:_rb = False
                mc.menuItem(p=uiMenu,collection = uiRC,
                            label=item,
                            c = mmCallback(self.var_keyMode.setValue,i),
                            rb = _rb)                
        except Exception,err:
            log.error("|{0}| failed to load. err: {1}".format(_str_section,err))
            
    def bUI_optionMenu_aimMode(self, parent):
            try:#>>> KeyMode 
                _str_section = 'aim mode'
        
                uiMenu =mc.menuItem(p=parent, l='Aim Mode', subMenu=True)    
                uiRC = mc.radioMenuItemCollection()
                #self.uiOptions_menuMode = []		
                _v = self.var_aimMode.value
                
                for i,item in enumerate(['local','world','matrix']):
                    if item == _v:
                        _rb = True
                    else:_rb = False
                    mc.menuItem(p=uiMenu,collection = uiRC,
                                label=item,
                                c = mmCallback(self.var_aimMode.setValue,item),
                                rb = _rb)                
            except Exception,err:
                log.error("|{0}| failed to load. err: {1}".format(_str_section,err))  
                
    def bUI_optionMenu_resetMode(self, parent):
        try:#>>> KeyMode 
            _str_section = 'reset mode'
    
            uiMenu = mc.menuItem(p=parent, l='Reset Mode', subMenu=True)    
            uiRC = mc.radioMenuItemCollection()
            #self.uiOptions_menuMode = []		
            _v = self.var_resetMode.value
            
            for i,item in enumerate(SHARED.l_resetModes):
                if i == _v:
                    _rb = True
                else:_rb = False
                mc.menuItem(p=uiMenu,collection = uiRC,
                            label=item,
                            c = mmCallback(self.var_resetMode.setValue,i),
                            rb = _rb)                
        except Exception,err:
            log.error("|{0}| failed to load. err: {1}".format(_str_section,err)) 
            
    
    #@cgmGEN.Timer           
    def bUI_optionMenu_objDefaults(self, parent):
            #uiMenu_objDefault = mc.menuItem(parent= parent, l='Object Default', subMenu=True)
            #mc.setParent(parent)        
            uiMenu_objDefault = mc.menuItem(parent = parent, l='Object', subMenu=True)
            
            try:#>>> Obj Aim 
                _str_section = 'Aim Axis'
        
                uiMenuAim = mc.menuItem( parent = uiMenu_objDefault, l='Obj Aim', subMenu=True)    
                uiRC = mc.radioMenuItemCollection(parent = uiMenuAim)
                
                #self.uiOptions_menuMode = []		
                _v = self.var_objDefaultAimAxis.value
                
                for i,item in enumerate(SHARED._l_axis_by_string):
                    if i == _v:
                        _rb = True
                    else:_rb = False
                    mc.menuItem(parent = uiMenuAim,collection = uiRC,
                                label=item,   
                                c = mmCallback(self.var_objDefaultAimAxis.setValue,i),
                                rb = _rb)                
            except Exception,err:
                log.error("|{0}| failed to load. err: {1}".format(_str_section,err)) 
                
                
            try:#>>> Obj Up 
                _str_section = 'Up Axis'
        
                uiMenuUp = mc.menuItem( parent = uiMenu_objDefault, l='Obj Up', subMenu=True)    
                uiRC = mc.radioMenuItemCollection(parent = uiMenuUp)
                #self.uiOptions_menuMode = []		
                _v = self.var_objDefaultUpAxis.value
                
                for i,item in enumerate(SHARED._l_axis_by_string):
                    if i == _v:
                        _rb = True
                    else:_rb = False
                    mc.menuItem(parent = uiMenuUp,collection = uiRC,
                                label=item,                                   
                                #c = mmCallback(self.raySnap_setAndStart_reg,self.var_rayCastMode,i),
                                c = mmCallback(self.var_objDefaultUpAxis.setValue,i),                                      
                                #c = lambda *a:self.var_objDefaultUpAxis.setValue(i),                                  
                                rb = _rb)                
            except Exception,err:
                log.error("|{0}| failed to load. err: {1}".format(_str_section,err))
                
            try:#>>> Obj Out 
                _str_section = 'Out Axis'
        
                uiMenuOut = mc.menuItem(p=uiMenu_objDefault, l='Obj Out', subMenu=True)    
                uiRC = mc.radioMenuItemCollection()
                #self.uiOptions_menuMode = []		
                _v = self.var_objDefaultOutAxis.value
                
                for i,item in enumerate(SHARED._l_axis_by_string):
                    if i == _v:
                        _rb = True
                    else:_rb = False
                    mc.menuItem(parent = uiMenuOut,collection = uiRC,
                                label=item,                                   
                                #c = mmCallback(self.raySnap_setAndStart_reg,self.var_rayCastMode,i),  
                                c = mmCallback(self.var_objDefaultOutAxis.setValue,i),                                                                            
                                #c = lambda *a:self.var_objDefaultOutAxis.setValue(i),                                  
                                rb = _rb)                
            except Exception,err:
                log.error("|{0}| failed to load. err: {1}".format(_str_section,err))     
                           
            
            mc.menuItem( parent = uiMenu_objDefault, l='Tag selected for aim',
                         c = lambda *a:MMCONTEXT.func_process(SNAP.verify_aimAttrs, self._l_sel,'each','Verify aim attributes',True,**{}),)                                                                    
                
            
    #@cgmGEN.Timer
    def bUI_optionMenu_contextTD(self, parent):
        uiMenu_context = mc.menuItem( parent = parent, l='Context:', subMenu=True)    
        
        try:#>>>
            _str_section = 'Contextual TD mode'
            uiRC = mc.radioMenuItemCollection()
            #self.uiOptions_menuMode = []		
            _v = self.var_contextTD.value
            
            for i,item in enumerate(['selection','children','heirarchy','scene']):
                if item == _v:
                    _rb = True
                else:_rb = False
                mc.menuItem(parent=uiMenu_context,collection = uiRC,
                            label=item,
                            #c = lambda *a:ui_CallAndKill(self.var_contextTD.setValue,item),
                            c = mmCallback(self.var_contextTD.setValue,item),                                  
                            rb = _rb)                
        except Exception,err:
            log.error("|{0}| failed to load. err: {1}".format(_str_section,err))
            
    #@cgmGEN.Timer
    def bUI_optionMenu_rayCast(self, parent):
        uiMenu_rayCast = mc.menuItem( parent = parent, l='rayCast', subMenu=True)    
        mc.menuItem(p= uiMenu_rayCast, l='Set Drag Interval',
                    c = lambda *a:self.var_rayCastDragInterval.uiPrompt_value('Set aim tolerance'))         
        try:#>>> Cast Mode 
            _str_section = 'Cast mode'
    
            uiMenu = mc.menuItem( p=uiMenu_rayCast, l='Cast', subMenu=True)    
            uiRC = mc.radioMenuItemCollection()
            #self.uiOptions_menuMode = []		
            _v = self.var_rayCastMode.value
            
            for i,item in enumerate(['closest','midpoint','far','pierce','xPlane','yPlane','zPlane']):
                if i == _v:
                    _rb = True
                else:_rb = False
                mc.menuItem(parent=uiMenu,collection = uiRC,
                            label=item,
                            c = mmCallback(self.var_rayCastMode.setValue,i),                                  
                            #c = lambda *a:self.raySnap_setAndStart(self.var_rayCastMode.setValue(i)),                                  
                            rb = _rb)                
        except Exception,err:
            log.error("|{0}| failed to load. err: {1}".format(_str_section,err))
            
        try:#>>> Offset Mode 
            _str_section = 'Offset mode'
    
            uiMenu = mc.menuItem( p=uiMenu_rayCast, l='Offset', subMenu=True)    
            uiRC = mc.radioMenuItemCollection()
            #self.uiOptions_menuMode = []		
            _v = self.var_rayCastOffsetMode.value
            
            for i,item in enumerate(['None','Distance','snapCast']):
                if i == _v:
                    _rb = True
                else:_rb = False
                mc.menuItem(parent=uiMenu,collection = uiRC,
                            label=item,
                            c = mmCallback(self.var_rayCastOffsetMode.setValue,i),
                            #c = lambda *a:self.raySnap_setAndStart(self.var_rayCastOffsetMode.setValue(i)),                                  
                            rb = _rb)       
            
            mc.menuItem(p= uiMenu_rayCast, l='Set Offset',
                        c = lambda *a:self.var_rayCastOffsetDist.uiPrompt_value('Set offset'))
        except Exception,err:
            log.error("|{0}| failed to load. err: {1}".format(_str_section,err)) 
            
        try:#>>> Orient Mode 
            _str_section = 'Orient mode'
    
            uiMenu = mc.menuItem( p=uiMenu_rayCast, l='Orient', subMenu=True)    
            uiRC = mc.radioMenuItemCollection()
            #self.uiOptions_menuMode = []		s
            _v = self.var_rayCastOrientMode.value
            
            for i,item in enumerate(['None','Normal']):
                if i == _v:
                    _rb = True
                else:_rb = False
                mc.menuItem(parent=uiMenu,collection = uiRC,
                            label=item,
                            c = mmCallback(self.var_rayCastOrientMode.setValue,i),
                            #c = lambda *a:self.raySnap_setAndStart(self.var_rayCastOffsetMode.setValue(i)),                                  
                            rb = _rb)         
        except Exception,err:
            log.error("|{0}| failed to load. err: {1}".format(_str_section,err))  

    def bUI_radial_dynParent(self,parent,direction = None):
        """
        Menu to work with dynParent setup from cgm
        """
        _r = mc.menuItem(parent=parent,subMenu = True,
                         en = False,
                         l = 'dynParent',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         rp = direction)
        
    def bUI_rayCastBuffer(self,parent):
        try:#>>> Cast Buffer 
            _str_section = 'Cast Buffer'
    
            uiMenu = mc.menuItem(p=parent, l='Cast Buffer', subMenu=True)    
            mc.menuItem(p=uiMenu, l="Define",
                        c = lambda *a:self.varBuffer_define(self.var_rayCastTargetsBuffer))
        
            mc.menuItem(p=uiMenu, l="Add Selected",
                             c = lambda *a:self.varBuffer_add(self.var_rayCastTargetsBuffer))
        
            mc.menuItem(p=uiMenu, l="Remove Selected",
                             c = lambda *a:self.varBuffer_remove(self.var_rayCastTargetsBuffer))
        
            mc.menuItem(p=uiMenu,l='----------------',en=False)
            mc.menuItem(p=uiMenu, l="Report",
                        c = lambda *a:self.var_rayCastTargetsBuffer.report())            
            mc.menuItem(p=uiMenu, l="Select Members",
                        c = lambda *a:self.var_rayCastTargetsBuffer.select())
            mc.menuItem(p=uiMenu, l="Clear",
                        c = lambda *a:self.var_rayCastTargetsBuffer.clear())
            
        except Exception,err:
            log.error("|{0}| failed to load. err: {1}".format(_str_section,err))  
            
    #@cgmGEN.Timer     
    def bUI_radial_create(self,parent,direction = None):
        """
        Menu to create items from selected objects
        """
        _r =mc.menuItem(parent=parent,subMenu = True,
                        en = True,
                        l = 'Create',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        rp = direction)  
              
        #---------------------------------------------------------------------------

        mc.menuItem(parent=_r,
                    en = self._b_sel,
                    l = 'Null here',
                    #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                    c = lambda *a:self.button_action_per_sel(RIGGING.create_at,'Create Transform'),
                    rp = "N")        
        mc.menuItem(parent=_r,
                    en = self._b_sel,
                    l = 'Joint here',
                    #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                    c = lambda *a:self.button_action_per_sel(RIGGING.create_joint_at,'Create Joint'),
                    rp = "NW")   
        
        _crv = mc.menuItem(parent=_r,subMenu = True,
                                   l = 'Curve: ',#'Control Curve',
                                   en = self._b_sel_pair,
                                   rp = "S")        
        mc.menuItem(parent=_crv,
                    l = 'Cubic',
                    c = lambda *a:self.bc_create_curve(),
                    rp = "S")
        mc.menuItem(parent=_crv,
                    l = 'Linear',
                    c = lambda *a:self.bc_create_curve(linear=True),
                    rp = "SE")
        
        _control = mc.menuItem(parent=_r,subMenu = True,
                               l = 'Control: {0}'.format(self.var_curveCreateType.value),#'Control Curve',
                               rp = "W") 
        mc.menuItem(parent=_control,
                    l = 'Create: {0}'.format(self.var_curveCreateType.value),#'Control Curve',
                    c = lambda *a:TOOLBOX.uiFunc_createCurve(),
                    rp = "W")  
        mc.menuItem(parent=_control,
                    l = 'Change options'.format(self.var_curveCreateType.value),#'Control Curve',
                    c = lambda *a:TOOLBOX.ui(),
                    rp = "SW")          
        
        #Mid..............................................................................
        _mid = mc.menuItem(parent=_r,subMenu = True,
                           l = 'Mid: ',#'Control Curve',
                           en = self._b_sel_pair,
                           rp = "E")
        
        mc.menuItem(parent=_mid,
                  ut = 'cgmUITemplate',                    
                  l = 'Null',
                  rp = 'NE',
                  c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Tranform at mid',**{'create':'null','midPoint':'True'}))    
        mc.menuItem(parent=_mid,
                  ut = 'cgmUITemplate',                    
                  l = 'Joint',
                  rp = 'E',
                  c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Tranform at mid',**{'create':'joint','midPoint':'True'}))    
        mc.menuItem(parent=_mid,
                  ut = 'cgmUITemplate',                    
                  l = 'Loc',
                  rp = 'SE',
                  c = lambda *a:MMCONTEXT.func_process(LOC.create, self._l_sel,'all','midPointLoc',False,**{'mode':'midPoint'}),)                                                                      
        
        
        
        
        
        #>>Locator ------------------------------------------------------------------------------------------
        _l = mc.menuItem(parent=_r,subMenu=True,
                         l = 'Locator',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         #c = mmCallback(MMCONTEXT.func_process, LOC.create, self._l_sel,'each'),
                         rp = "NE")
        
        mc.menuItem(parent=_l,
                    l = 'World Center',
                    c = lambda *a:LOC.create(),
                    rp = "S")          
        mc.menuItem(parent=_l,
                    l = 'Selected',
                    en = self._b_sel,
                    c = lambda *a:MMCONTEXT.func_process(LOC.create, self._l_sel,'each'),
                    rp = "N")           
        mc.menuItem(parent=_l,
                    l = 'Mid point',
                    en = self._b_sel_pair,                    
                    c = lambda *a:MMCONTEXT.func_process(LOC.create, self._l_sel,'all','midPointLoc',False,**{'mode':'midPoint'}),                                                                      
                    rp = "NE")            
        mc.menuItem(parent=_l,
                    l = 'closest Point',
                    en = self._b_sel_pair,                    
                    c = lambda *a:MMCONTEXT.func_process(LOC.create, self._l_sel,'all','closestPoint',False,**{'mode':'closestPoint'}),                                                                      
                    rp = "NW") 
        mc.menuItem(parent=_l,
                    l = 'closest Target',
                    en = self._b_sel_few,                    
                    c = lambda *a:MMCONTEXT.func_process(LOC.create, self._l_sel,'all','closestTarget',False,**{'mode':'closestTarget'}),                                                                      
                    rp = "W")   
        mc.menuItem(parent=_l,
                    l = 'rayCast',
                    c = lambda *a:self.rayCast_create('locator',False),
                    rp = "SE")           
        
        #>>Nodes ------------------------------------------------------------------------------------------        

        
    #@cgmGEN.Timer 
    def bUI_radial_rayCreate(self,parent,direction = None):
            """
            Menu to create items from selected objects
            """
            _r = mc.menuItem(parent=parent,subMenu = True,
                             en = True,
                             l = 'Ray',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             rp = direction)  
            
            #if not self._b_sel:
                #return        
            #---------------------------------------------------------------------------
                
            if self.var_rayCastTargetsBuffer.value:
                _add = "(Buffer Cast)"
            else:_add = ""
            
            self.bUI_radial_rayCast(_r,'Cast{0}'.format(_add),'NE')        
            self.bUI_radial_rayCast(_r,'Drag{0}'.format(_add),'SE',drag = True)   
            
    #@cgmGEN.Timer     
    def bUI_radial_curve(self,parent,direction = None):
        _r = mc.menuItem(parent=parent,subMenu = True,
                         en = self._b_sel,
                         l = 'Shapes',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         rp = direction)  
        if not self._b_sel:
            return        
        #---------------------------------------------------------------------------
        mc.menuItem(parent=_r,
                    l = 'Shapeparent',
                    en = self._b_sel_pair,
                    c = lambda *a:MMCONTEXT.func_enumrate_all_to_last(RIGGING.shapeParent_in_place, self._l_sel,'toFrom'),
                    rp = "W")   
        _d_combine = {'keepCurve':False}
        mc.menuItem(parent=_r,
                    en = self._b_sel_pair,
                    l = 'Combine',
                    #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                    c = lambda *a:MMCONTEXT.func_enumrate_all_to_last(RIGGING.shapeParent_in_place, self._l_sel,'toFrom', **_d_combine),
                    rp = "NW") 
        mc.menuItem(parent=_r,
                    en = False,                    
                    l = 'Replace',
                    rp = "SW")        
        mc.menuItem(parent=_r,
                    en = False,
                    l = 'Describe',
                    rp = "SE")  
        
        _color = mc.menuItem(parent=_r,subMenu=True,
                             en = True,
                             l = 'Color',
                             #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                             #c = mmCallback(self.button_action_per_sel,locators.locMeObject,'Locator'),
                             rp = "S")
        _center = mc.menuItem(parent=_color,subMenu=True,
                              en = True,
                              l = 'Center',
                              #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                              c = lambda *a:MMCONTEXT.color_shape('red',self.var_contextTD.value,'shape'),
                              rp = "S")
        
        mc.menuItem(parent=_center,
                    en = True,
                    l = 'Sub',
                    #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                    c = lambda *a:MMCONTEXT.color_shape('redLight',self.var_contextTD.value,'shape'),
                    rp = "SE")  
        mc.menuItem(parent=_center,
                    en = True,
                    l = 'Extra',
                    #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                    c = lambda *a:MMCONTEXT.color_shape('redDark',self.var_contextTD.value,'shape'),
                    rp = "SW")        
        
        
    def bUI_radial_aim(self,parent,direction = None):
        _r = mc.menuItem(parent=parent,subMenu = True,
                         en = False,
                         l = 'Aim',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         rp = direction)
        
    def bUI_radial_rayCast(self,parent,label = 'Cast Create', direction = None, drag = False):
        _r =mc.menuItem(parent=parent,subMenu = True,
                        en = True,
                        l = label,
                        rp = direction)
        #self._l_pivotModes = ['rotatePivot','scalePivot','boundingBox']
        _l_toBuild = [{'l':'locators',
                       'rp':'N',
                       'c':lambda *a:self.rayCast_create('locator',drag)},
                      {'l':'joint',
                       'rp':'NE',
                       'c':lambda *a:self.rayCast_create('joint',drag)},
                      {'l':'joint chain',
                       'rp':'E',
                       'c':lambda *a:self.rayCast_create('jointChain',drag)},
                      {'l':'curve',
                       'rp':'SE',
                       'c':lambda *a:self.rayCast_create('curve',drag)},
                      {'l':'Duplicate',
                        'rp':'W',
                        'c':lambda *a:self.rayCast_create('duplicate',drag)},
                      {'l':'vector',
                       'rp':'SW',
                       'c':lambda *a:self.rayCast_create('vectorLine',drag)},   
                      {'l':'data',
                        'rp':'NW',
                        'c':lambda *a:self.rayCast_create('data',drag)},                      
                      {'l':'follicle',
                       'rp':'S',
                       'c':lambda *a:self.rayCast_create('follicle',drag)}]    
        
        for i,m in enumerate(_l_toBuild): 
            mc.menuItem(parent=_r,
                        en = True,
                        l = m['l'],
                        c = m['c'],
                        rp = m['rp'])         
        
    def optionRadial_pivotMode(self,parent,direction = None):
        _r = mc.menuItem(parent=parent,subMenu = True,
                         en = True,
                         l = 'Pivot Mode',
                         rp = direction)
        #self._l_pivotModes = ['rotatePivot','scalePivot','boundingBox']
        _l_toBuild = [{'l':'rotatePivot',
                       'rp':'W',
                       #'c':mmCallback(self.raySnap_setAndStart,self.var_rayCastMode.setValue(0))},
                       'c':lambda *a:self.var_snapPivotMode.setValue(0)},                       
                      {'l':'scalePivot',
                       'rp':'SW',
                       'c':lambda *a:self.var_snapPivotMode.setValue(1)},
                      {'l':'boundingBox',
                       'rp':'S',
                       'c':lambda *a:self.var_snapPivotMode.setValue(2)},
                      {'l':'closest',
                       'rp':'SE',
                       'c':lambda *a:self.var_snapPivotMode.setValue(3)},
                      {'l':'closeUI',
                       'rp':'NE',
                       'c':'pass'}]                      
        for i,m in enumerate(_l_toBuild):
            if i == self.var_snapPivotMode.value:
                m['l'] = m['l'] + '--(Active)'
                
            mc.menuItem(parent=_r,
                        en = True,
                        l = m['l'],
                        c = m['c'],
                        rp = m['rp'])  
            
    
    def raySnap_setAndStart(self,func,):
        func
        raySnap_start(self._l_sel)
    def rayCast_create(self,create = None,drag=False):
        raySnap_start(self._l_sel,create = create, drag = drag)
        
    def raySnap_setAndStart_reg(self,var,value):
            var.setValue(value)
            raySnap_start(self._l_sel)    
            
    def optionRadial_rayCastMode(self,parent,direction = None):
        _r = mc.menuItem(parent=parent,subMenu = True,
                             en = True,
                             l = 'RayCast Mode',
                             rp = direction)
        #self._l_pivotModes = ['rotatePivot','scalePivot','boundingBox']
        _l_toBuild = [{'l':'closest',
                       'rp':'W',
                       'c':lambda *a:self.raySnap_setAndStart(self.var_rayCastMode.setValue(0))},
                      {'l':'midpoint',
                       'rp':'SW',
                       'c':lambda *a:self.raySnap_setAndStart(self.var_rayCastMode.setValue(1))},
                      {'l':'far',
                       'rp':'S',
                       'c':lambda *a:self.raySnap_setAndStart(self.var_rayCastMode.setValue(2))},
                      {'l':'closeUI',
                       'rp':'NE',
                       'c':'pass'}]
        
        for i,m in enumerate(_l_toBuild):
            if i == self.var_rayCastMode.value:
                m['l'] = m['l'] + '--(Active)'
                
            mc.menuItem(parent=_r,
                        en = True,
                        l = m['l'],
                        c = m['c'],
                        rp = m['rp'])  
            
    def optionRadial_rayCastOffset(self,parent,direction = None):
        _r = mc.menuItem(parent=parent,subMenu = True,
                         en = True,
                         l = 'RayCast Offset',
                         rp = direction)
        #self._l_pivotModes = ['rotatePivot','scalePivot','boundingBox']
        _l_toBuild = [{'l':'None',
                       'rp':'NW',
                       'c':lambda *a:self.raySnap_setAndStart(self.var_rayCastOffsetMode.setValue(0))},
                      {'l':'Distance',
                       'rp':'SW',
                       'c':lambda *a:self.raySnap_setAndStart(self.var_rayCastOffsetMode.setValue(1))},
                      {'l':'snapCast',
                       'rp':'W',
                       'c':lambda *a:self.raySnap_setAndStart(self.var_rayCastOffsetMode.setValue(2))},
                      {'l':'Set Distance -- ({0})'.format(self.var_rayCastOffsetDist.value),
                       'rp':'S',
                       'c':lambda *a:self.raySnap_setAndStart(self.var_rayCastOffsetDist.uiPrompt_value('Set offset'))},
                      {'l':'closeUI',
                       'rp':'NE',
                       'c':'pass'}]
        
        for i,m in enumerate(_l_toBuild):
            if i == self.var_rayCastOffsetMode.value:
                m['l'] = m['l'] + '--(Active)'
                
            mc.menuItem(parent=_r,
                        en = True,
                        l = m['l'],
                        c = m['c'],
                        rp = m['rp'])  
            
    def bUI_radial_arrange(self,parent,direction = None):
        _r = mc.menuItem(parent=parent,subMenu = True,
                         en = False,
                         l = 'Arrange',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         rp = direction)  
        
    def bUI_radial_locinator(self,parent,direction = None):
        _r = mc.menuItem(parent=parent,subMenu = True,
                         en = self._b_sel,
                         l = 'Locinator',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         rp = direction)  
        if not self._b_sel:
            return        
        #---------------------------------------------------------------------------
        mc.menuItem(parent=_r,
                    l = 'Loc me',
                    c = lambda *a:MMCONTEXT.func_process(LOC.create, self._l_sel,'firstToRest','Match Transform'),                    
                    rp = "N")         
    
    def bUI_radial_copy(self,parent,direction = None):
        _r = mc.menuItem(parent=parent,subMenu = True,
                         en = self._b_sel_pair,
                         l = 'Copy',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         rp = direction)  
        if not self._b_sel_pair:
            return        
        #---------------------------------------------------------------------------
        mc.menuItem(parent=_r,
                    l = 'Transform',
                    c = lambda *a:MMCONTEXT.func_process(RIGGING.match_transform, self._l_sel,'eachToFirst','Match Transform'),                    
                    rp = "N")          
        mc.menuItem(parent=_r,
                    l = 'Orienation',
                    c = lambda *a:MMCONTEXT.func_process(RIGGING.match_orientation, self._l_sel,'eachToFirst','Match Orientation'),                    
                    rp = "NW")
        
        mc.menuItem(parent=_r,
                    l = 'Shapes',
                    c = lambda *a:MMCONTEXT.func_process(RIGGING.shapeParent_in_place, self._l_sel,'lastFromRest','Copy Shapes', **{'snapFirst':True}),
                    rp = "SW")        
        
        mc.menuItem(parent=_r,
                    l = 'Constraints',
                    en=False,
                    #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                    #c = lambda *a:MMCONTEXT.func_process(RIGGING.match_orientation, self._l_sel,'eachToFirst','Match Orientation'),                    
                    rp = "E") 
        
        _piv = mc.menuItem(parent=_r,subMenu=True,
                           l = 'Pivot',
                           rp = "W")    
        
        mc.menuItem(parent = _piv,
                    l = 'rp',
                    c = lambda *a:MMCONTEXT.func_process(RIGGING.copy_pivot, self._l_sel,'eachFromFirst', 'Match RP',**{'rotatePivot':True,'scalePivot':False}),                                               
                    rp = "W")         
        mc.menuItem(parent = _piv,
                    l = 'sp',
                    c = lambda *a:MMCONTEXT.func_process(RIGGING.copy_pivot, self._l_sel,'eachFromFirst', 'Match SP', **{'rotatePivot':False,'scalePivot':True}),                                               
                    rp = "SW")         
        

        mc.menuItem(parent=_r,subMenu=True,
                    en=False,                    
                    l = 'Attrs',
                    rp = "S")        

    def bUI_radial_control(self,parent,direction = None):
        _r = mc.menuItem(parent=parent,subMenu = True,
                         en = self._b_sel,
                         l = 'Control',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         rp = direction) 
        if not self._b_sel:
            return        
        #---------------------------------------------------------------------------   
        mc.menuItem(parent=_r,
                   en = self._b_sel_pair,
                   l = 'Combine Curves',
                   #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                   #c = mmCallback(self.copy_pivot,True, False,'Rotate Pivot'),
                   rp = "W")   
        mc.menuItem(parent=_r,
                    en = self._b_sel_pair,
                    l = 'ParentShape',
                    #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                    #c = mmCallback(self.copy_pivot,True, False,'Rotate Pivot'),
                    rp = "SW")      
        mc.menuItem(parent=_r,
                    en = False,
                    l = 'Replace Curves',
                    #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                    #c = mmCallback(self.copy_pivot,True, False,'Rotate Pivot'),
                    rp = "NW")
        mc.menuItem(parent=_r,subMenu = True,
                        en = False,
                        l = 'Color',
                        #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                        #c = mmCallback(self.copy_pivot,True, False,'Rotate Pivot'),
                        rp = "E")         
        
    def button_action_per_sel(self,func,calling = None):
        for o in self._l_sel:
            _res = func(o)
            log.debug("|{0}| : '{1}' | result: '{2}'".format(calling,o,_res)) 
            self._l_res.append(_res)
        mc.select(self._l_res)
        
    def button_action_each_to_last_sel(self,calling = None):
        pass    
    
    def action_logged(self,func,calling=None):
        _res = func
        log.debug("|{0}| | result: '{1}'".format(calling,_res)) 
        return _res
    
    def log_info(self,msg=None,calling = None):
        log.info("|{0}| >> {1}".format(calling,msg)) 
        
    def bc_create_groupMe(self, calling = None):
        for o in self._l_sel:
            _res = self.action_logged( RIGGING.group_me(o,True,True), "|{0}| : {1}".format(calling,o) )
            self._l_res.append(_res)
        mc.select(self._l_res)
        
    def bc_create_curve(self, calling = None, linear = False):
        _str_func = 'bc_create_curve'
        if linear:
            curveBuffer = RIGGING.create_at(self._l_sel, 'curveLinear')            
        else:
            curveBuffer = RIGGING.create_at(self._l_sel, 'curve')
        """    
        l_pos = []
        for i,o in enumerate(self._l_sel):
            p = POS.get(o)
            log.info("|{0}| >> {3}: {1} | pos: {2}".format(_str_func,o,p,i)) 
            l_pos.append(p)
            
        if len(l_pos) <= 1:
            raise ValueError,"Must have more than one position to create curve"
        
        knot_len = len(l_pos)+3-1		
        curveBuffer = mc.curve (d=3, ep = l_pos, k = [i for i in range(0,knot_len)], os=True)  """
        log.info("|{0}| >> created: {1}".format(_str_func,curveBuffer))         
        mc.select(curveBuffer)

    
    def bc_copy_pivot(self,rotatePivot = False, scalePivot = False, calling=None):        
        for o in self._l_sel[1:]:
            _msg = "|{0}| : {1}".format(calling,o)
            try:
                self.action_logged( RIGGING.copy_pivot(o,self._l_sel[0],rotatePivot,scalePivot), _msg  )
            except Exception,err:
                log.error("|{0}| ||| Failure >>> err:s[{1}]".format(_msg,err))
                
        mc.select(self._l_sel)
    #@cgmGEN.Timer    
    def bUI_radial_tdUtils(self,parent,direction = None):
        """
        Radial menu for td Utils 
        """
        _r = mc.menuItem(parent=parent,subMenu = True,
                         l = 'Utils',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         rp = direction)
      
        #---------------------------------------------------------------------------
        mc.menuItem(parent=_r,
                    l = 'shapeParent',
                    en = self._b_sel_pair,
                    c = lambda *a:MMCONTEXT.func_process(RIGGING.shapeParent_in_place, self._l_sel, 'lastFromRest'),
                    rp = "NE")         
        
        
        _gSet = mc.menuItem(parent=_r,subMenu=True,
                            l='Group',
                            rp='NW')
        
        mc.menuItem(parent=_gSet,
                    en = self._b_sel,
                    l = 'Just Group',
                    #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                    c = lambda *a:MMCONTEXT.func_process(RIGGING.group_me, self._l_sel,'each','Group',**{'parent':False,'maintainParent':False}),                                             
                    rp = "N")  
        mc.menuItem(parent=_gSet,
                    en = self._b_sel,
                    l = 'Group Me',
                    #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                    c = lambda *a:MMCONTEXT.func_process(RIGGING.group_me, self._l_sel,'each','Group',**{'parent':True,'maintainParent':False}),                                             
                    rp = "W")          
        mc.menuItem(parent=_gSet,
                    en = self._b_sel,
                    l = 'In Place',
                    c = lambda *a:MMCONTEXT.func_process(RIGGING.group_me, self._l_sel,'each','Group In Place',**{'parent':True,'maintainParent':True}),                                                                 
                    rp = "NW")    

        
        _p = mc.menuItem(parent=_r, subMenu = True,
                         en=self._b_sel_few,
                         l = 'Parent',
                         rp = 'W')       
        if self._b_sel_few:
            mc.menuItem(parent=_p, #subMenu = True,
                             l = 'Reverse',
                             c = lambda *a:TRANS.parent_orderedTargets(),                                             
                             rp = 'S')
            mc.menuItem(parent=_p, #subMenu = True,
                             l = 'Ordered',
                             c = lambda *a:TRANS.parent_orderedTargets(reverse=True),                                             
                             rp = 'SW')   
        

        _attr = mc.menuItem(parent=_r,subMenu=True,
                            l='Attr',
                            rp='SW')     
        _add = mc.menuItem(parent=_attr,subMenu=True,
                           l='Add',
                           en=self._b_sel,
                           #c = mmCallback(ATTRTOOLS.uiWin_multiSetAttr),
                           rp='S') 
        _d_attrTypes = {"string":'E','float':'S','enum':'NE','vector':'SW','int':'W','bool':'NW','message':'SE'}
        for _t,_d in _d_attrTypes.iteritems():
            mc.menuItem(parent=_add,
                        l=_t,
                        c = lambda *a:ATTRTOOLS.uiPrompt_addAttr(_t,**{'autoLoadFail':True}),
                        rp=_d)             
        
        
        mc.menuItem(parent=_attr,
                    l='Manage',
                    en=False,
                    #c = mmCallback(ATTRTOOLS.uiWin_multiSetAttr),
                    rp='W')       
        mc.menuItem(parent=_attr,
                    l='attrTools 2.0',
                    c=lambda *a: mc.evalDeferred(ATTRTOOLS.ui),                               
                    #c = mmCallback(ATTRTOOLS.ui),
                    rp='SW')          
        mc.menuItem(parent=_attr, #subMenu = True,
                    l = 'Compare Attrs',
                    en=self._b_sel_pair,
                    c = lambda *a:MMCONTEXT.func_process(ATTRS.compare_attrs, self._l_sel, 'firstToRest','Compare Attrs',True,**{}),                                                                      
                    rp = 'N')         
               
        
    #@cgmGEN.Timer    
    def bUI_radial_snap(self,parent,direction = None):
        """
        Radial menu for snap functionality
        """
        self.create_guiOptionVar('snapPivotMode', defaultValue = 0)
        #self.create_guiOptionVar('rayCastMode', defaultValue = 0)
        #self.create_guiOptionVar('rayCastOffset', defaultValue = 0)
        #self.create_guiOptionVar('rayCastCreate', defaultValue = 0)
        #self.create_guiOptionVar('rayCastOffsetDist', defaultValue = 1.0)

        _r = mc.menuItem(parent=parent,subMenu = True,
                         l = 'Snap',
                         #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                         rp = direction)
    
        #---------------------------------------------------------------------------
    
        _pnt = mc.menuItem(parent=_r,subMenu = True,
                           l = 'Point',
                           rp = 'NW')
        mc.menuItem(parent=_pnt,
                    l = 'Object',
                    en = self._b_sel_pair,
                    c = lambda *a:snap_action(self,'point'),
                    #c = mmCallback(snap_action,self,'point'),
                    rp = 'NW')
        mc.menuItem(parent=_pnt,
                    l = 'Closest on Target',
                    en = self._b_sel_pair,
                    c = lambda *a:snap_action(self,'closestPoint'),
                    #c = mmCallback(snap_action,self,'closestPoint'),
                    rp = 'W')
        mc.menuItem(parent=_pnt,
                  l = 'Along line(Even)',
                  en = self._b_sel_few,
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{}),                                               
                  ann = ARRANGE._d_arrangeLine_ann.get('linearEven'),
                  rp = 'SW')
        mc.menuItem(parent=_pnt,
                  l = 'Along line(Spaced)',
                  en = self._b_sel_few,                  
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'spaced'}),                                               
                  ann = ARRANGE._d_arrangeLine_ann.get('linearSpaced'),
                  rp = 'S')
        mc.menuItem(parent=_pnt,
                  l = 'Along Curve(Even)',
                  en = self._b_sel_few,                  
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubic'}),                                               
                  ann = ARRANGE._d_arrangeLine_ann.get('cubicEven'),
                  rp = 'SE')
        mc.menuItem(parent=_pnt,
                  l = 'Along Arc(Even)',
                  en = self._b_sel_few,                  
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubicArc'}),                                               
                  ann = ARRANGE._d_arrangeLine_ann.get('cubicArcEven'),
                  rp = 'E')
        mc.menuItem(parent=_pnt,
                  l = 'Along Cubic Rebuild 2(Even)',
                  en = self._b_sel_few,                  
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubicRebuild'}),                                               
                  ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild2Even'),
                  rp = 'NE')
        
        mc.menuItem(parent=_r,
                        l = 'Parent',
                        en = self._b_sel_pair,    
                        c = lambda *a:snap_action(self,'parent'),                        
                        #c = mmCallback(snap_action,self,'parent'),
                        rp = 'N')
        mc.menuItem(parent=_r,
                        l = 'Orient',
                        en = self._b_sel_pair,   
                        c = lambda *a:snap_action(self,'orient'),                                                
                        #c = mmCallback(snap_action,self,'orient'),
                        rp = 'NE')

        mc.menuItem(parent=_r,
                        l = 'RayCast',
                        en = self._b_sel,
                        #c = mmCallback(buttonAction,raySnap_start(_sel)),
                        c = lambda *a:raySnap_start(self._l_sel),                                                
                        #c = mmCallback(raySnap_start,self._l_sel),
                        rp = 'W')	
        mc.menuItem(parent=_r,
                        l = 'AimCast',
                        en = self._b_sel,                        
                        #c = mmCallback(buttonAction,raySnap_start(_sel)),  
                        c = lambda *a:aimSnap_start(self._l_sel),                                                
                        #c = mmCallback(aimSnap_start,self._l_sel),
                        rp = 'E')
        if self._b_sel_few:
            _aim = mc.menuItem(parent=_r,subMenu = True,
                            l = 'Aim Special',
                            #c = mmCallback(buttonAction,raySnap_start(_sel)),                    
                            #c = mmCallback(snap_action(self,'aim'),
                            rp = 'SE')
            mc.menuItem(parent=_aim,
                        l = 'All to last',
                        #c = mmCallback(buttonAction,raySnap_start(_sel)),         
                        c = lambda *a:snap_action(self,'aim','eachToLast'),                                                
                        #c = mmCallback(snap_action,self,'aim','eachToLast'),
                        rp = 'E') 
            mc.menuItem(parent=_aim,
                        l = 'Selection Order',
                        #c = mmCallback(buttonAction,raySnap_start(_sel)),      
                        c = lambda *a:snap_action(self,'aim','eachToNext'),                                                
                        #c = mmCallback(snap_action,self,'aim','eachToNext'),
                        rp = 'SE')
            mc.menuItem(parent=_aim,
                        l = 'First to Midpoint',
                        #c = mmCallback(buttonAction,raySnap_start(_sel)),  
                        c = lambda *a:snap_action(self,'aim','firstToRest'),                                                
                        #c = mmCallback(snap_action,self,'aim','firstToRest'),
                        rp = 'S')             
        else:
            mc.menuItem(parent=_r,
                        l = 'Aim',
                        en = self._b_sel_pair,
                        #c = mmCallback(buttonAction,raySnap_start(_sel)),
                        c = lambda *a:snap_action(self,'aim','eachToLast'),                                                
                        #c = mmCallback(snap_action,self,'aim','eachToLast'),
                        rp = 'SE')     
        
        """mc.menuItem(parent=_r,
                    l = 'Match',
                    en=self._b_sel,
                    #c = mmCallback(buttonAction,raySnap_start(_sel)),                    
                    c = mmCallback(MMCONTEXT.func_process, LOCINATOR.update_obj, self._l_sel,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,}),#'targetPivot':self.var_matchModePivot.value                                                                      
                    rp = 'SW')"""      
        _match= mc.menuItem(parent=_r,subMenu = True,
                            l = 'Match',
                            rp = 'SW')         
        mc.menuItem(parent=_match,
                    l = 'Self',
                    en=self._b_sel,
                    c = lambda *a:MMCONTEXT.func_process(LOCINATOR.update_obj, self._l_sel,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'self'}),#'targetPivot':self.var_matchModePivot.value                                                                                          
                    #c = mmCallback(MMCONTEXT.func_process, LOCINATOR.update_obj, self._l_sel,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'self'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                    rp = 'SW')     
        mc.menuItem(parent=_match,
                    l = 'Target',
                    en=self._b_sel,
                    c = lambda *a: MMCONTEXT.func_process(LOCINATOR.update_obj, self._l_sel,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'target'}),#'targetPivot':self.var_matchModePivot.value                                                                                          
                    #c = mmCallback(MMCONTEXT.func_process, LOCINATOR.update_obj, self._l_sel,'each','Match',False,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'target'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                    rp = 'W')           
        mc.menuItem(parent=_match,
                    l = 'Buffer',
                    #c = mmCallback(buttonAction,raySnap_start(_sel)),   
                    c = lambda a: LOCINATOR.update_obj(**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'buffer'}),#'targetPivot':self.var_matchModePivot.value                                                                                          
                    #c = mmCallback(LOCINATOR.update_obj,**{'move':self.var_matchModeMove.value,'rotate':self.var_matchModeRotate.value,'mode':'buffer'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                    rp = 'S')  

def killUI():
    log.debug("killUI...")
    _var_mode = cgmMeta.cgmOptionVar('cgmVar_cgmMarkingMenu_menuMode', defaultValue = 0)
    log.debug('mode: {0}'.format(_var_mode))    
    if _var_mode.value in [0,1,2,3]:
        log.debug('animMode killUI')
        
        #IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked')
        #mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction')
    
        sel = mc.ls(sl=1)
    
        #>>> Timer stuff
        #=============================================================================
        var_clockStart = cgmMeta.cgmOptionVar('cgmVar_cgmMarkingMenu_clockStart', defaultValue = 0.0)    
        f_seconds = time.clock()-var_clockStart.value
        log.debug(">"*10  + '   cgmMarkingMenu =  %0.3f seconds  ' % (f_seconds) + '<'*10)    
    
        if sel and f_seconds <= .5:#and not mmActionOptionVar.value:
            log.debug("|{0}| >> low time. Set key...".format('cgmMM'))
            setKey()    
    
    try:
        #mmTemplate.killChildren(_str_popWindow)
        if mc.popupMenu('cgmMM',ex = True):
            try:mc.menu('cgmMM',e = True, deleteAllItems = True)
            except Exception,err:
                log.error("Failed to delete menu items")   
                
            mc.deleteUI('cgmMM') 
            
        #pprint.pprint(vars())      
            
    except Exception,err:
        log.error(err)   
    finally:
        pass
    
    
    
        
from cgm.core.classes import DraggerContextFactory as cgmDrag
#reload(cgmDrag)

def aimSnap_start(targets=[]):
    raySnap_start(targets, None, False, snap=False, aim=True)

def raySnap_start(targets = [], create = None, drag = False, snap=True, aim=False):
    
    _str_func = 'raySnap_start'
    _toSnap = False
    _toAim = False
    
    if snap:
        if not create or create == 'duplicate':
            targets = mc.ls(sl=True)#...to use g to do again?...    
            _toSnap = targets

            log.debug("|{0}| | targets: {1}".format(_str_func,_toSnap))
            if not _toSnap:
                if create == 'duplicate':
                    log.error("|{0}| >> Must have targets to duplicate!".format(_str_func))
                return
    
    if aim:
        _toAim = targets

    var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
    var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetMode', defaultValue=0)
    var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0)
    var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])
    var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0) 
    var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
    var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)      
    var_objDefaultOutAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultOutAxis', defaultValue = 0)      
    var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)
    var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode',defaultValue='world')
    
    _rayCastMode = var_rayCastMode.value
    _rayCastOffsetMode = var_rayCastOffsetMode.value
    _rayCastTargetsBuffer = var_rayCastTargetsBuffer.value
    _rayCastOrientMode = var_rayCastOrientMode.value
    _objDefaultAimAxis = var_objDefaultAimAxis.value
    _objDefaultUpAxis = var_objDefaultUpAxis.value
    _objDefaultOutAxis = var_objDefaultOutAxis.value
    _rayCastDragInterval = var_rayCastDragInterval.value
    
    log.debug("|{0}| >> Mode: {1}".format(_str_func,_rayCastMode))
    log.debug("|{0}| >> offsetMode: {1}".format(_str_func,_rayCastOffsetMode))
    
    kws = {'mode':'surface', 'mesh':None,'closestOnly':True, 'create':'locator','dragStore':False,'orientMode':None,
           'objAimAxis':SHARED._l_axis_by_string[_objDefaultAimAxis], 'objUpAxis':SHARED._l_axis_by_string[_objDefaultUpAxis],'objOutAxis':SHARED._l_axis_by_string[_objDefaultOutAxis],
           'aimMode':var_aimMode.value,
           'timeDelay':.1, 'offsetMode':None, 'dragInterval':_rayCastDragInterval, 'offsetDistance':var_rayCastOffsetDist.value}#var_rayCastOffsetDist.value
    
    if _rayCastTargetsBuffer:
        log.debug("|{0}| >> Casting at buffer {1}".format(_str_func,_rayCastMode))
        kws['mesh'] = _rayCastTargetsBuffer
        
    if _toSnap:
        kws['toSnap'] = _toSnap
    elif create:
        kws['create'] = create

    if _toAim:
        kws['toAim'] = _toAim
        
    if _rayCastOrientMode == 1:
        kws['orientMode'] = 'normal'
        
    if create == 'duplicate':
        kws['toDuplicate'] = _toSnap        
        if _toSnap:
            kws['toSnap'] = False
        else:
            log.error("|{0}| >> Must have target with duplicate mode!".format(_str_func))
            cgmGEN.log_info_dict(kws,"RayCast args")        
            return
        
    if drag:
        kws['dragStore'] = drag
    
    if _rayCastMode == 1:
        kws['mode'] = 'midPoint'
    elif _rayCastMode == 2:
        kws['mode'] = 'far'
    elif _rayCastMode == 3:
        kws['mode'] = 'surface'
        kws['closestOnly'] = False
    elif _rayCastMode == 4:
        kws['mode'] = 'planeX'
    elif _rayCastMode == 5:
        kws['mode'] = 'planeY'   
    elif _rayCastMode == 6:
        kws['mode'] = 'planeZ'        
    elif _rayCastMode != 0:
        log.warning("|{0}| >> Unknown rayCast mode: {1}!".format(_str_func,_rayCastMode))
        
    if _rayCastOffsetMode == 1:
        kws['offsetMode'] = 'distance'
    elif _rayCastOffsetMode == 2:
        kws['offsetMode'] = 'snapCast'
    elif _rayCastOffsetMode != 0:
        log.warning("|{0}| >> Unknown rayCast offset mode: {1}!".format(_str_func,_rayCastOffsetMode))
    cgmGEN.log_info_dict(kws,"RayCast args")
    
    cgmDrag.clickMesh(**kws)
    return

    log.warning("raySnap_start >>> ClickMesh initialized")
    
def snap_action(self, snapMode = 'point',selectionMode = 'eachToLast'):
    
    if snapMode == 'aim':
        aim_axis = SHARED._l_axis_by_string[self.var_objDefaultAimAxis.value]
        up_axis = SHARED._l_axis_by_string[self.var_objDefaultUpAxis.value]
                
        kws = {'aimAxis':aim_axis, 'upAxis':up_axis, 'mode':self.var_aimMode.value}
        
        if selectionMode == 'firstToRest':
            MMCONTEXT.func_process(SNAP.aim_atMidPoint, self._l_sel ,selectionMode,'Snap aim', **kws)
        else:
            MMCONTEXT.func_process(SNAP.aim, self._l_sel ,selectionMode,'Snap aim', **kws)
    else:
        kws = {'position' : False, 'rotation' : False, 'rotateAxis' : False,'rotateOrder' : False,
               
               'scalePivot' : False,
               'pivot' : 'rp', 'space' : 'w', 'mode' : 'xform'}
        
        if snapMode in ['point','closestPoint']:
            kws['position'] = True
        elif snapMode == 'orient':
            kws['rotation'] = True
        elif snapMode == 'parent':
            kws['position'] = True
            kws['rotation'] = True
        elif snapMode == 'aim':
            kws['rotation'] = True
        else:
            raise ValueError,"Unknown mode!"
        
        _pivotMode = self.var_snapPivotMode.value
        
        if snapMode == 'closestPoint':
            kws['pivot'] = 'closestPoint'
        else:
            if not _pivotMode:pass#0 handled by default
            elif _pivotMode == 1:
                kws['pivot'] = 'sp'
            elif _pivotMode == 2:
                kws['pivot'] = 'boundingBox'
            else:
                raise ValueError,"Uknown pivotMode: {0}".format(_pivotMode)        
    
        MMCONTEXT.func_process(SNAP.go, self._l_sel ,selectionMode,'Snap',noSelect=False, **kws)
    
    
    return
    '''
    _str_func = 'snap_action'
    for o in self._l_sel[:-1]:
        _msg = "|{0}| >> mode: {1} | obj: {2} |target: {3}".format(_str_func,mode,o,self._l_sel[-1])
        try:
            kws = {'obj' : o, 'target' : self._l_sel[-1],
                   'position' : False, 'rotation' : False, 'rotateAxis' : False,'rotateOrder' : False,'scalePivot' : False,
                   'pivot' : 'rp', 'space' : 'w', 'mode' : 'xform'}
            
            if mode == 'point':
                kws['position'] = True
            elif mode == 'orient':
                kws['rotation'] = True
            elif mode == 'parent':
                kws['position'] = True
                kws['rotation'] = True
            elif mode == 'aim':
                kws['rotation'] = True
            else:
                raise ValueError,"Unknown mode!"
            
            _pivotMode = self.var_snapPivotMode.value
            
            if not _pivotMode:pass#0 handled by default
            elif _pivotMode == 1:
                kws['pivot'] = 'sp'
            elif _pivotMode == 2:
                kws['pivot'] = 'boundingBox'
            else:
                raise ValueError,"Uknown pivotMode: {0}".format(_pivotMode)
            
            if mode == 'aim':
                #var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
                #var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)  
                
                aim_axis = SHARED._l_axis_by_string[self.var_objDefaultAimAxis.value]
                up_axis = SHARED._l_axis_by_string[self.var_objDefaultUpAxis.value]
                self.action_logged( SNAP.aim(o, self._l_sel[-1], aim_axis, up_axis), _msg  )
            else:
                self.action_logged( SNAP.go(**kws), _msg  )
        except Exception,err:
            log.error("|{0}| ||| Failure >>> err:s[{1}]".format(_msg,err))
    mc.select(self._l_sel)    
    '''
    


    
def setKey(keyModeOverride = None):
    _str_func = "setKey"        
    KeyTypeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
    KeyModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)	
    selection = False
    
    log.debug("|{0}| >> keyType: {1} | keyMode: {2} |  keyModeOverride: {3}".format(_str_func,KeyTypeOptionVar.value,KeyModeOptionVar.value,keyModeOverride))  
    
    if not KeyModeOptionVar.value:#This is default maya keying mode
        selection = mc.ls(sl=True) or []
        if not selection:
            return log.warning('cgmPuppetKey.setKey>>> Nothing l_selected!')
           
            
        """if not KeyTypeOptionVar.value:
            mc.setKeyframe(selection)
        else:
            mc.setKeyframe(breakdown = True)"""
    else:#Let's check the channel box for objects
        selection = SEARCH.get_selectedFromChannelBox(False) or []
        if not selection:
            log.debug("|{0}| >> No channel box selection. ".format(_str_func))
            selection = mc.ls(sl=True) or []
            
            
    if not selection:
        return log.warning('cgmPuppetKey.setKey>>> Nothing selected!')
    
            
    if keyModeOverride:
        log.debug("|{0}| >> Key override mode. ".format(_str_func))
        if keyModeOverride== 'breakdown':
            mc.setKeyframe(selection,breakdown = True)     
        else:
            mc.setKeyframe(selection)
            
    else:
        if not KeyTypeOptionVar.value:
            mc.setKeyframe(selection)
        else:
            mc.setKeyframe(selection,breakdown = True)     

	

def deleteKey():
    KeyTypeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
    KeyModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)	

    if not KeyModeOptionVar.value:#This is default maya keying mode
        selection = mc.ls(sl=True) or []
        if not selection:
            return log.warning('cgmPuppetKey.deleteKey>>> Nothing l_selected!')
        
        mel.eval('timeSliderClearKey;')
        """
        if not KeyTypeOptionVar.value:
            mc.cutKey(selection)
        else:
            mc.cutKey(selection)"""
    else:#Let's check the channel box for objects
        selection = search.returnSelectedAttributesFromChannelBox(False) or []
        if not selection:
            selection = mc.ls(sl=True) or []
            if not selection:
                return log.warning('cgmPuppetKey.deleteKey>>> Nothing l_selected!')
        """
        if not KeyTypeOptionVar.value:
            mc.cutKey(selection)	    
        else:
            mc.cutKey(selection,breakdown = True)"""
        mel.eval('timeSliderClearKey;')
            
            
def ui_CallAndKill(func, *a, **kws ):
    try:
        _str_func = 'ui_CallAndKill'
        MMUTILS.kill_mmTool()
        try:return func( *a, **kws )
        except Exception,err:
            try:log.info("Func: {0}".format(func.__name__))
            except:log.info("Func: {0}".format(_func))
            if a:
                log.info("args: {0}".format(a))
            if kws:
                log.info("kws: {0}".format(kws))
            for a in err.args:
                log.info(a)
            raise Exception,err
    except Exception,err:
        log.info("Failed...")
        print Exception
        #pprint.pprint(err)

class mmCallback(object):
    '''
    Callback with kill ui
    '''
    def __init__( self, func, *a, **kw ):
        self._func = func
        self._args = a
        self._kwargs = kw
    def __call__( self, *args ):
        try:
            _res = self._func( *self._args, **self._kwargs )
            MMUTILS.kill_mmTool()            
            return _res
        except Exception,err:
            #MMUTILS.killUI()            
            #try:log.info("Func: {0}".format(self._func.__name__))
            #except:log.info("Func: {0}".format(self._func))
            if self._args:
                log.info("args: {0}".format(self._args))
            if self._kwargs:
                log.info("kws: {0}".format(self._kwargs))
            for a in err.args:
                log.info(a)
            #raise Exception,err
        finally:
            log.debug('mmCallback closed')
            del self

	
