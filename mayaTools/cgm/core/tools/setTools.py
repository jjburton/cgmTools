"""
------------------------------------------
transformTools: cgm.core.tools
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

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
log.setLevel(logging.INFO)

import maya.cmds as mc

import cgm.core.classes.GuiFactory as cgmUI
from cgm.core import cgm_RigMeta as cgmRigMeta
mUI = cgmUI.mUI

from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.search_utils as SEARCH


"""
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import name_utils as NAMES
import cgm.core.lib.position_utils as POS
import cgm.core.lib.transform_utils as TRANS
from cgm.core.lib import list_utils as LISTS
from cgm.core.tools.markingMenus.lib import contextual_utils as CONTEXT
from cgm.core.cgmPy import str_Utils as STRINGS
from cgm.core.tools import attrTools as ATTRTOOLS
from cgm.core.rigger.lib import spacePivot_utils as SPACEPIVOT
from cgm.core.cgmPy import path_Utils as CGMPATH
import cgm.core.lib.math_utils as MATH
from cgm.lib import lists"""

#>>> Root settings =============================================================
__version__ = '0.09112017'

_l_setTypes = ['NONE',
               'animation',
               'layout',
               'modeling',
               'td',
               'fx',
               'lighting']    

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmSetTools_ui'    
    WINDOW_TITLE = 'cgmSetTools - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 300,400
    TOOLNAME = 'setTools.ui'
     
    
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
        
        uiSetupOptionVars(self)
        
        self.ml_objectSets = []
        self.d_activeStateCBs = {}
        
        self.d_itemScrollLists = {}
        self.d_itemLists = {}
        
        self.l_objectSets = []
        self.d_refSets = {}
        self.l_setModes = ['<<< All Loaded Sets >>>','<<< Active Sets >>>']
        self.setMode = 0
        
        #self.uiPopUpMenu_createShape = None
        #self.uiPopUpMenu_color = None
        #self.uiPopUpMenu_attr = None
        #self.uiPopUpMenu_raycastCreate = None

        #self.create_guiOptionVar('matchFrameCollapse',defaultValue = 0) 
        #self.create_guiOptionVar('rayCastFrameCollapse',defaultValue = 0) 
        #self.create_guiOptionVar('aimFrameCollapse',defaultValue = 0) 

    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Options', pmc = cgmGEN.Callback(self.buildMenu_first))
        #self.uiMenu_Buffers = mUI.MelMenu( l='Buffers', pmc = cgmGEN.Callback(self.buildMenu_buffer))

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Force Update",
                         c = lambda *a:self.uiUpdate_objectSets())  
        
        #Modes -------------------------------------------------------------------------------------        
        _build = mc.menuItem(parent = self.uiMenu_FirstMenu, subMenu = True,
                             label = 'Modes')
        
        _anim = self.var_animMode.value
        mc.menuItem( parent = _build,
                     l="Anim",
                     cb=_anim,
                     c=lambda *a: uiFunc_setOptionVarAndUpdate(self, self.var_animMode, not _anim ))
        _setup = self.var_setupMode.value
        mc.menuItem( parent = _build,
                     l="Setup",
                     cb=_setup,
                     c=lambda *a: uiFunc_setOptionVarAndUpdate(self, self.var_setupMode, not _setup ))            
        
        
        #Hide -------------------------------------------------------------------------------------
        _menu_hide = mUI.MelMenuItem( self.uiMenu_FirstMenu, l='Auto Hide', subMenu=True)
        #self.var_hideNonQSS = cgmMeta.cgmOptionVar('cgmVar_objectSetHideNonQSS', defaultValue = 1)
        #self.var_hideAnimLayerSets = cgmMeta.cgmOptionVar('cgmVar_HideAnimLayerSets', defaultValue = 1)
        #self.var_hideMayaSets= cgmMeta.cgmOptionVar('cgmVar_HideMayaObjectSets', defaultValue = 1)     
        
        #guiFactory.appendOptionVarList(self,'cgmVar_MaintainLocalSetGroup')
        _animLayerSets = self.var_hideAnimLayerSets.value
        _nonQss = self.var_hideNonQSS.value
        _mayaSets = self.var_hideMayaSets.value
        
        mc.menuItem( parent = _menu_hide,
                     l="Anim LayerSets",
                     cb=_animLayerSets,
                     c=lambda *a: uiFunc_setOptionVarAndUpdate(self, self.var_hideAnimLayerSets, not _animLayerSets ))        
        mc.menuItem( parent = _menu_hide,
                     l="non Qss",
                     cb=_nonQss,
                     c=lambda *a: uiFunc_setOptionVarAndUpdate(self, self.var_hideNonQSS, not _nonQss ))        
        mc.menuItem( parent = _menu_hide,
                     l="Maya Sets",
                     cb=_mayaSets,
                     c=lambda *a: uiFunc_setOptionVarAndUpdate(self, self.var_hideMayaSets, not _mayaSets ))        
        

    
        #MelMenuItem( HidingMenu, l="Set Groups",
        #             cb= self.HideSetGroupOptionVar.value,
        #             c= lambda *a: setToolsLib.uiToggleOptionCB(self,self.HideSetGroupOptionVar))        
        
        #Reference Prefixes -----------------------------------------------------------------------------
        _refKeys = self.d_refSets.keys()
        _activeRefs = self.var_ActiveSetRefs.getValue()
        _str_activeSetRefs = self.var_ActiveSetRefs.name
        if _refKeys:# and len(_refKeys) > 1:
        
            refMenu = mUI.MelMenuItem( self.uiMenu_FirstMenu, l='Load Refs:', subMenu=True)
            
        
            mUI.MelMenuItem( refMenu, l = 'All',
                             c=lambda *a: uiFunc_setOptionVarAndUpdate(self, self.var_ActiveSetRefs,_refKeys ))        
            
                         #c = Callback(setToolsLib.doSetAllRefState,self,True))	
                         
            mUI.MelMenuItemDiv( refMenu )
            reload(cgmUI)
        
            for i,n in enumerate(_refKeys):
        
                activeState = False
                if n in _activeRefs:
                    activeState = True
        
                mUI.MelMenuItem( refMenu, l = n,
                                 cb = activeState,
                                 #c= cgmGEN.Callback(cgmUI.varBuffer_toggle,self,_str_activeSetRefs,n))                                                                          
                                 c=cgmGEN.Callback(self.uiFunc_toggleListValueOptionVarAndUpdate, _str_activeSetRefs,n))        
                                 #c= uiFunc_toggleListValueOptionVarAndUpdate(self, self.var_ActiveSetRefs,n))                                  
                                 #c=lambda *a: uiFunc_toggleListValueOptionVarAndUpdate(self, self.var_ActiveSetRefs,n))        
                                 #cc=lambda *a: uiFunc_toggleListValueOptionVarAndUpdate(self, self.var_ActiveSetRefs,n)
                                 #c=cgmGEN.Callback(self.log_n,n))
                                 #cc=cgmGEN.Callback(log.info, n))
                
        
            mUI.MelMenuItemDiv( refMenu )
            mUI.MelMenuItem( refMenu, l = 'Clear',
                             c=lambda *a: uiFunc_setOptionVarAndUpdate(self, self.var_ActiveSetRefs,[''] ))        
                             #c = Callback(setToolsLib.doSetAllRefState,self,False))	        
        
        
         

        mc.menuItem( parent = self.uiMenu_FirstMenu,
                     l="Log Self",
                     c=lambda *a: cgmUI.log_selfReport(self))  
        
        mc.menuItem( parent = self.uiMenu_FirstMenu,
                     l="Dock",
                     c=lambda *a: self.do_dock())
        
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
    
    def uiFunc_toggleListValueOptionVarAndUpdate(self, optionVar = None, value=None ):
        _str_func = 'uiFunc_setOptionVarAndUpdate'
        log.warning("|{0}| >> optionVar: {1} | value: {2}".format(_str_func,optionVar,value)) 
        try:optionVar.value
        except:optionVar = cgmMeta.cgmOptionVar(optionVar)
        if value in optionVar.value:
            optionVar.remove(value)
        else:
            optionVar.append(value)
        
        self.uiUpdate_objectSets()
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'    

        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')            
        
        _column = buildSetsForm_main(self,_MainForm)
        
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)   
        
        _MainForm(edit = True,
                  af = [(_column,"top",0),
                        (_column,"left",0),
                        (_column,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(_column,"bottom",2,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])   
        
    def uiUpdate_objectSets(self):
        """ 
        Gets sccene set objects, and sorts the data in to the class as varaibles
        """ 
        _str_func = 'uiUpdate_objectSets'
        
        _d_sets = SEARCH.get_objectSetsDict()
        #pprint.pprint(_d_sets)
        
        self.uiScrollList_objectSets.clear()
        self.d_itemScrollLists = {}
        self.d_itemLists = {}       
        self.ml_objectSets = []
        self.l_objectSets = []        
        self.d_activeStateCBs = {}
        self.d_refSets = {}        
        
        l_running = []
        
        #Filter our list --------------------------------------------------------------------------------
        if self.var_hideNonQSS.value:
            l_running.extend(_d_sets['qss'])
        else:
            l_running.extend(_d_sets['all'])
            
        if self.var_hideMayaSets.value:
            for s in l_running:
                if s in _d_sets['maya']:
                    l_running.remove(s)
        
        if self.var_hideAnimLayerSets.value:
            for s in l_running:
                if VALID.get_mayaType(s) == 'animLayer':
                    l_running.remove(s)  
                    
        
        if _d_sets['referenced']:
            activePrefixes = self.var_ActiveSetRefs.value
            for k,l in _d_sets['referenced'].iteritems():
                if k =='From Scene':
                    continue
                if k not in self.d_refSets.keys():
                    #self.var_ActiveSetRefs.append(k)
                    self.d_refSets[k] = []                
                if k not in activePrefixes:
                    for s in l:
                        if s in l_running:
                            l_running.remove(s)
                    
            
            
        #self.var_hideAnimLayerSets = cgmMeta.cgmOptionVar('cgmVar_HideAnimLayerSets', defaultValue = 1)
        #self.var_hideMayaSets= cgmMeta.cgmOptionVar('cgmVar_HideMayaObjectSets', defaultValue = 1)        
        
        for oSet in l_running:
            uiBuild_objectSetRow(self,self.uiScrollList_objectSets, oSet)
        
        return
        self.refPrefixes = self.objectSetsRaw['referenced'].keys()
        self.refSetsDict = self.objectSetsRaw['referenced'] or {}
        self.setTypesDict = self.objectSetsRaw['cgmTypes'] or {}
        self.setGroups = self.objectSetsRaw['objectSetGroups'] or []
        #Set Group stuff
        self.setGroupName = False
    
        for s in self.setGroups:
            if s in self.refSetsDict.get('From Scene'):
                self.setGroupName = s
                self.setsGroup = SetFactory(s)
                break
    
        self.mayaSets = self.objectSetsRaw['maya'] or []
        self.qssSets = self.objectSetsRaw['qss'] or []
    
        self.sortedSets = []
        self.objectSets = []
        self.activeSets = []
    
        #Sort sets we want to actually load
        self.sortedSets = []
    
        #Sort for activeRefs
        tmpActiveRefSets = []
        if self.ActiveRefsOptionVar.value:
            for r in self.ActiveRefsOptionVar.value:
                #If value, let's add or subtract based on if our set refs are found
                if self.refSetsDict.get(r):
                    tmpActiveRefSets.extend(self.refSetsDict.get(r))
    
        #Sort for active types  
        tmpActiveTypeSets = []
        if self.setTypesDict.keys() and self.ActiveTypesOptionVar.value:
            for t in self.setTypesDict.keys():
                if t in self.ActiveTypesOptionVar.value and self.setTypesDict.get(t):	    
                    tmpActiveTypeSets.extend(self.setTypesDict.get(t))
    
        if tmpActiveTypeSets and tmpActiveRefSets:
            self.sortedSets = lists.returnMatchList(tmpActiveTypeSets,tmpActiveRefSets)
        elif tmpActiveTypeSets:
            self.sortedSets = tmpActiveTypeSets
        else:
            self.sortedSets = tmpActiveRefSets
    
    
        #Next step, hiding. First get our cull lists
        if self.sortedSets:
            self.objectSets = self.sortedSets
        else:
            self.objectSets = self.objectSetsRaw['all']
    
        # Start pulling out stuff by making a list we can iterate through as culling from a list you're iterating through doesn't work
        bufferList = copy.copy(self.objectSets)
    
        # Hide Set groups
        if mc.optionVar(q='cgmVar_HideSetGroups'):
            for s in self.setGroups:
                try:self.objectSets.remove(s)
                except:pass
    
    
        # Hide animLayer Sets
        if mc.optionVar(q='cgmVar_HideAnimLayerSets'):
            for s in bufferList:
                if search.returnObjectType(s) == 'animLayer':
                    try:self.objectSets.remove(s)
                    except:pass
    
    
        # Hide Maya Sets
        if mc.optionVar(q='cgmVar_HideMayaSets'):
            for s in self.mayaSets:
                try:self.objectSets.remove(s)
                except:pass
    
    
        # Hide non qss Sets
        #print self.qssSets
        #print self.objectSets
        if mc.optionVar(q='cgmVar_HideNonQss'):
            #print "sorting for qss"
            for s in bufferList:
                if s not in self.qssSets and s not in self.setGroups:
                    try:self.objectSets.remove(s)
                    except:pass 
    
    
        #Refresh our active lists    
        if self.ActiveObjectSetsOptionVar.value:
            for o in self.objectSets:
                if o in self.ActiveObjectSetsOptionVar.value:
                    self.activeSets.append(o) 
    
        self.setInstances = {}
        self.setInstancesFastIndex = {}
    
        #If we have object sets to load, we're gonna initialize em
        if self.objectSets:
            #Counter build
            mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(self.objectSetsRaw),"Getting Set info")
    
            for i,o in enumerate(self.objectSets):
                if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                    break
                mc.progressBar(mayaMainProgressBar, edit=True, status = ("On set %s"%(o)), step=1)                    	
    
                self.setInstances[i] = SetFactory(o) #Store the instance so we only have to do it once
                sInstance = self.setInstances[i] #Simple link to keep the code cleaner
    
                self.setInstancesFastIndex[o] = i #Store name to index for fast lookup of index on the fly
    
            guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
    
        # Set Group creation if they don't have em
        #if mc.optionVar( q='cgmVar_MaintainLocalSetGroup' ) and not self.setGroupName:
        #    initializeSetGroup(self)
    
        #if mc.optionVar( q='cgmVar_MaintainLocalSetGroup' ):
        #    doGroupLocal(self)        
        
    def uiFunc_createSet(self):
        _str_func = 'uiFunc_createSet'   
        _ls = mc.ls(sl=True,flatten = True)
        mObjectSet = cgmMeta.cgmObjectSet(qssState = True,nameOnCall=True)
        for o in _ls:
            mObjectSet.append(o)
        log.info("|{0}| >> Created: {1}".format(_str_func,mObjectSet.p_nameShort))  
        
        mc.evalDeferred(self.uiUpdate_objectSets,lp=True)
        
    def uiFunc_rename(self,mObjectSet = None):
        _str_func = 'uiFunc_rename'  
        _current = mObjectSet.p_nameShort
        
        mObjectSet.uiPrompt_rename()
        log.info("|{0}| >> Renamed: {1} to : {2}".format(_str_func,_current, mObjectSet.p_nameShort))   
        
        mc.evalDeferred(self.uiUpdate_objectSets,lp=True)
        
        
    def uiFunc_setType(self,mObjectSet = None, setType = None):
        _str_func = 'uiFunc_setType'  
        
        
        mc.evalDeferred(self.uiUpdate_objectSets,lp=True)
        
        if setType in ['NONE',None]:
            mObjectSet.doSetType()            
        else:
            mObjectSet.doSetType(setType)  
            
        log.info("|{0}| >> objectSet {1} set to type: {2}".format(_str_func,mObjectSet.p_nameShort,setType))   
            
        
    def uiFunc_delete(self,mObjectSet = None):
        _str_func = 'uiFunc_delete' 
        _str = mObjectSet.p_nameShort
        mObjectSet.delete()
        log.warning("|{0}| >> deleted: {1}".format(_str_func, _str))   
        mc.evalDeferred(self.uiUpdate_objectSets,lp=True)
        
    def uiFunc_setAllActiveState(self,value = None):
        for mSet,cb in self.d_activeStateCBs.iteritems():
            cb.setValue(value)
            _str = mSet.p_nameShort

            if value:
                self.var_ActiveSets.append(_str)
            else:
                self.var_ActiveSets.remove(_str)
                
    def uiFunc_multiSetsFunction(self,mode=''):
        _str_func = 'uiFunc_multiSetsFunction' 
        
        ml_sets = []
        if not self.var_setMode.value:
            ml_sets = self.ml_objectSets
        else:
            for s in self.var_ActiveSets.value:
                ml_sets.append(cgmMeta.cgmObjectSet(s))
        
        if not ml_sets:
            log.error("|{0}| >> No loaded or active sets.".format(_str_func))               
            return False
        
        l_sel = False
        if mode == 'select':
            l_sel = []
        for mSet in ml_sets:
            try:
                if mode == 'key':
                    mSet.key()
                elif mode == 'delete':
                    mSet.deleteKey()
                elif mode == 'reset':
                    mSet.reset()
                elif mode == 'select':
                    l_sel.extend(mSet.getList())
                else:
                    log.error("|{0}| >> unknown mode: {1}".format(_str_func, mode))   
                    return False
            except Exception,err:
                log.error("|{0}| >> Failed: {1} | mode: {2} | err: {3}".format(_str_func,mSet, mode,err)) 
        
        if l_sel:
            mc.select(l_sel)
                
    def uiFunc_setActiveState(self,mObjectSet = None,value = None):
        _str_func = 'uiFunc_setActiveState' 
        _str = mObjectSet.p_nameShort
        
        if value:
            self.var_ActiveSets.append(_str)
        else:
            self.var_ActiveSets.remove(_str)
            
        log.info("|{0}| >> objectSet: {1} | value: {2}".format(_str_func, _str, value))   
        #mc.evalDeferred(self.uiUpdate_objectSets,lp=True)    
           
    def uiFunc_itemList_showToggle(self,mObjectSet = None):
        _str_func = 'uiFunc_itemList_showToggle' 
        _str = mObjectSet.p_nameShort
        
        _list = self.d_itemScrollLists[mObjectSet]
        _vis = _list(q=True, vis=True)
        
        if _vis:
            _list(e=True, vis = False)
        else:
            _list.clear()
            l_items = mObjectSet.getList()
            l_items.sort()
            self.d_itemLists[mObjectSet] = l_items
            for o in l_items:
                _list.append(str(o))                
            _list(e=True, vis = True)
            
    def uiFunc_itemList_dc(self,mObjectSet = None):
        _str_func = 'uiFunc_itemList_dc' 
        _str = mObjectSet.p_nameShort
        _list = self.d_itemScrollLists[mObjectSet]
        
        _indices = _list.getSelectedIdxs() or []
        
        _l = []
        l_buffer = self.d_itemLists[mObjectSet]
        
        for i in _indices:
            v = l_buffer[i]
            #log.info("|{0}| >> indices: {1} | objectSet: {2} | v: {3}".format(_str_func, _indices,_str, v))  
            _l.append(v)
            print(v)
        mc.select(_l)
        return _l
        #mc.evalDeferred(self.uiUpdate_objectSets,lp=True)            
            
            
    def uiFunc_copy(self,mObjectSet = None):
        _str_func = 'uiFunc_copy'  
        mCopy = mObjectSet.copy()
        mc.evalDeferred(self.uiUpdate_objectSets,lp=True) 
        
        
            
def uiFunc_modeSet( self, item ):
    i =  self.setModes.index(item)
    self.SetToolsModeOptionVar.set( i )
    self.setMode = i

def uiSetupOptionVars(self):
    #self.HideSetGroupOptionVar = OptionVarFactory('cgmVar_HideSetGroups', defaultValue = 1)
    #self.HideNonQssOptionVar = OptionVarFactory('cgmVar_HideNonQss', defaultValue = 1)		
    
    self.var_ActiveSets = cgmMeta.cgmOptionVar('cgmVar_activeObjectSets', defaultValue = [''])
    self.var_ActiveSetRefs = cgmMeta.cgmOptionVar('cgmVar_activeObjectSetRefs', defaultValue = [''])
    self.var_ActiveSetTypes = cgmMeta.cgmOptionVar('cgmVar_activeObjectSetTypes', defaultValue = [''])
    self.var_setMode = cgmMeta.cgmOptionVar('cgmVar_objectSetMode', defaultValue = 1)
    self.var_animMode = cgmMeta.cgmOptionVar('cgmVar_setToolsAnimMode', defaultValue = 1)
    self.var_setupMode = cgmMeta.cgmOptionVar('cgmVar_setToolsSetupMode', defaultValue = 1)
    
    self.var_hideNonQSS = cgmMeta.cgmOptionVar('cgmVar_objectSetHideNonQSS', defaultValue = 1)
    self.var_hideAnimLayerSets = cgmMeta.cgmOptionVar('cgmVar_HideAnimLayerSets', defaultValue = 1)
    self.var_hideMayaSets= cgmMeta.cgmOptionVar('cgmVar_HideMayaObjectSets', defaultValue = 1)
    


def uiFunc_setOptionVarAndUpdate(self, optionVar = None, value=None ):
    _str_func = 'uiFunc_setOptionVarAndUpdate'
    
    optionVar.setValue(value)
    self.uiRow_allSets(edit = True, visible = self.var_animMode.value)    
    
    
    self.uiUpdate_objectSets()
    
def uiFunc_toggleListValueOptionVarAndUpdate(self, optionVar = None, value=None ):
    _str_func = 'uiFunc_setOptionVarAndUpdate'
    log.warning("|{0}| >> optionVar: {1} | value: {2}".format(_str_func,optionVar,value)) 
    if value in optionVar.value:
        optionVar.remove(value)
    else:
        optionVar.append(value)
    
    self.uiUpdate_objectSets()
    
    
def uiFunc_setAllSets(self,active = False):
    _str_func = 'uiFunc_setAllSets'
    log.warning("|{0}| >> Finish...".format(_str_func)) 
    
def uiFunc_multiSetsAction(self,mode = None):
    _str_func = 'uiFunc_multiSetsAction'
    log.warning("|{0}| >> Finish...".format(_str_func)) 
    
def uiFunc_setActiveState(self, index = None, arg=None ):
    _str_func = 'uiFunc_setActiveState'
    log.warning("|{0}| >> Finish...".format(_str_func)) 
    
def uiFunc_multiSetsSetType(self,setType = None, qss = None):
    _str_func = 'uiFunc_multiSetsSetType'
    log.warning("|{0}| >> Finish...".format(_str_func)) 



    
def buildSetsForm_main(self,parent):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """
    _str_func = 'buildSetsForm_main'
    def modeSet( item ):
        i =  self.l_setModes.index(item)
        self.var_setMode.setValue( i )
        self.setMode = i    
        
    _MainForm = mUI.MelFormLayout(parent, useTemplate = 'cgmUISubTemplate')


    #>>>  Snap Section
    _Header = cgmUI.add_Header('Sets')
    
    #>> Logic ----------------------------------------------------------------------------------------
    activeState = True
    i = 1
    if self.l_objectSets:
        for b in self.l_objectSets:
            if b not in self.var_ActiveSets.value:
                activeState = False
    else:
        activeState = False    
        
    #>>>All Sets Row ----------------------------------------------------------------------------------
    _uiRow_allSets = mUI.MelHSingleStretchLayout(_MainForm, visible = self.var_animMode.value, bgc = cgmUI.guiBackgroundColor)
    self.uiRow_allSets = _uiRow_allSets
    """
    mc.button(parent=_uiRow_allSets ,
              ut = 'cgmUITemplate',                                                                                                
              l = '+',
              c = cgmGEN.Callback(uiFunc_valuesTweak,self,'+'),
              ann = "Adds value relatively to current")   """
    
    mUI.MelSpacer(parent = _uiRow_allSets, w = 5)
    
    mUI.MelCheckBox(parent = _uiRow_allSets,
                    annotation = 'Sets all sets active',
                    value = activeState,
                    onCommand =  cgmGEN.Callback(self.uiFunc_setAllActiveState,True),
                    offCommand = cgmGEN.Callback(self.uiFunc_setAllActiveState,False))
    
    # Mode toggle box
    self.SetModeOptionMenu = mUI.MelOptionMenu(_uiRow_allSets,cc=modeSet)
                                               #cc = lambda *a:uiFunc_modeSet(self))
    for m in self.l_setModes:
        self.SetModeOptionMenu.append(m)
    
    self.SetModeOptionMenu.selectByIdx(self.var_setMode.value,False)
    
    _uiRow_allSets.setStretchWidget(self.SetModeOptionMenu)
    
    mUI.MelSpacer(parent = _uiRow_allSets, w = 2)
    
    mc.button(parent=_uiRow_allSets ,
                     ut = 'cgmUITemplate',                                                                                                
                     l = 'S',
                     c = cgmGEN.Callback(self.uiFunc_multiSetsFunction,'select'),
                     ann = "Select all sets")    
    
    mc.button(parent=_uiRow_allSets ,
                 ut = 'cgmUITemplate',                                                                                                
                 l = 'K',
                 c = cgmGEN.Callback(self.uiFunc_multiSetsFunction,'key'),
                 ann = "Key all sets")
    
    #mUI.MelSpacer(parent = _uiRow_allSets, w = 2)
    mc.button(parent=_uiRow_allSets ,
                 ut = 'cgmUITemplate',                                                                                                
                 l = 'D',
                 c = cgmGEN.Callback(self.uiFunc_multiSetsFunction,'delete'),
                 ann = "Delete all keys of sets") 
    
    #mUI.MelSpacer(parent = _uiRow_allSets, w = 2)
    mc.button(parent=_uiRow_allSets ,
                 ut = 'cgmUITemplate',                                                                                                
                 l = 'R',
                 c = cgmGEN.Callback(self.uiFunc_multiSetsFunction,'reset'),
                 ann = "Reset all active sets") 
    
    mUI.MelSpacer(parent = _uiRow_allSets, w = 5)    
    _uiRow_allSets.layout()
    
    #>>>Pop up menu ----------------------------------------------------------------------------------
    allPopUpMenu = mUI.MelPopupMenu(self.SetModeOptionMenu ,button = 3)

    allCategoryMenu = mUI.MelMenuItem(allPopUpMenu,
                                      label = 'Make Type:',
                                      sm = True)

    multiMakeQssMenu = mUI.MelMenuItem(allPopUpMenu,
                                       label = 'Make Qss',
                                       c = cgmGEN.Callback(uiFunc_multiSetsSetType,self,**{'qss':True}))
    multiMakeNotQssMenu = mUI.MelMenuItem(allPopUpMenu,
                                          label = 'Clear Qss State',
                                          c = cgmGEN.Callback(uiFunc_multiSetsSetType,self,**{'qss':False}))
    #Mulit set type
    for n in _l_setTypes:
        mUI.MelMenuItem(allCategoryMenu,
                        label = n,
                        c = cgmGEN.Callback(uiFunc_multiSetsSetType,self,**{'setType':n}))
                        
                        #c = Callback(setToolsLib.doMultiSetType,self,self.SetToolsModeOptionVar.value,n))    


    #>>>Scroll List ----------------------------------------------------------------------------------
    SetListScroll = mUI.MelScrollLayout(_MainForm,cr = 1, ut = 'cgmUISubTemplate')
    
    self.uiScrollList_objectSets = SetListScroll
    SetMasterForm = mUI.MelFormLayout(SetListScroll)
    SetListColumn = mUI.MelColumnLayout(SetMasterForm, adj = True, rowSpacing = 1)
    
    NewSetRow = mUI.MelHLayout(_MainForm)
    mc.button(parent=NewSetRow ,
                  ut = 'cgmUITemplate',                                                                                                
                  l = 'Create Set',
                  c = lambda *a:self.uiFunc_createSet(),
                  ann = 'Create new buffer from selected buffer')    
    """mc.button(parent=NewSetRow ,
              ut = 'cgmUITemplate',                                                                                                
              l = 'Update',
              c = lambda *a:self.uiUpdate_objectSets(),
              ann = 'Force the ui to update')"""	    
    NewSetRow.layout()

    """
    NewSetRow = guiFactory.doButton2(MainForm,
                                     'Create Set',
                                     lambda *a:setToolsLib.doCreateSet(self),
                                     'Create new buffer from selected buffer')	"""    
    
    
    _MainForm(edit = True,
             af = [(_Header,"top",0),
                   (_Header,"left",0),
                   (_Header,"right",0),
                   (_uiRow_allSets,"left",0),
                   (_uiRow_allSets,"right",0),
                   (SetListScroll,"left",0),
                   (SetListScroll,"right",0),
                   (NewSetRow,"left",0),
                   (NewSetRow,"right",0),
                   (NewSetRow,"bottom",0)],
             ac = [(_uiRow_allSets,"top",0,_Header),
                   (SetListScroll,"top",2,_uiRow_allSets),
                   (SetListScroll,"bottom",0,NewSetRow)],
             attachNone = [(NewSetRow,"top")])       

    
    try:self.uiUpdate_objectSets()
    except Exception,err:
        log.warning("|{0}| >> Failed to initial load. | err: {1}".format(_str_func,err)) 
    return _MainForm


    #>>> Sets building section
    allPopUpMenu = MelPopupMenu(self.SetModeOptionMenu ,button = 3)

    allCategoryMenu = MelMenuItem(allPopUpMenu,
                                  label = 'Make Type:',
                                  sm = True)

    multiMakeQssMenu = MelMenuItem(allPopUpMenu,
                                   label = 'Make Qss',
                                   c = Callback(setToolsLib.doMultiSetQss,self,True))
    multiMakeNotQssMenu = MelMenuItem(allPopUpMenu,
                                      label = 'Clear Qss State',
                                      c = Callback(setToolsLib.doMultiSetQss,self,False))		
    #Mulit set type
    for n in self.setTypes:
        MelMenuItem(allCategoryMenu,
                    label = n,
                    c = Callback(setToolsLib.doMultiSetType,self,self.SetToolsModeOptionVar.value,n))


    #>>> Sets building section
    SetListScroll = MelScrollLayout(MainForm,cr = 1, ut = 'cgmUISubTemplate')
    SetMasterForm = MelFormLayout(SetListScroll)
    SetListColumn = MelColumnLayout(SetMasterForm, adj = True, rowSpacing = 3)

    self.objectSetsDict = {}
    self.activeSetsCBDict = {}

    for b in self.objectSets:
        #Store the info to a dict
        try:
            i = self.setInstancesFastIndex[b] # get the index
            sInstance = self.setInstances[i] # fast link to the instance
        except:
            raise StandardError("'%s' failed to query an active instance"%b)

        #see if the no no fields are enabled
        enabledMenuLogic = True
        if sInstance.mayaSetState or sInstance.refState:				
            enabledMenuLogic = False


        tmpSetRow = MelFormLayout(SetListColumn,height = 20)

        #Get check box state
        activeState = False
        if sInstance.nameShort in self.ActiveObjectSetsOptionVar.value:
            activeState = True
        tmpActive = MelCheckBox(tmpSetRow,
                                annotation = 'make set as active',
                                value = activeState,
                                onCommand =  Callback(setToolsLib.doSetSetAsActive,self,i),
                                offCommand = Callback(setToolsLib.doSetSetAsInactive,self,i))

        self.activeSetsCBDict[i] = tmpActive

        tmpSel = guiFactory.doButton2(tmpSetRow,
                                      ' s ',
                                      Callback(setToolsLib.doSelectSetObjects,self,i),
                                      'Select the set objects')


        tmpName = MelTextField(tmpSetRow, w = 100,ut = 'cgmUIReservedTemplate', text = sInstance.nameShort,
                               editable = enabledMenuLogic)

        tmpName(edit = True,
                ec = Callback(setToolsLib.doUpdateSetName,self,tmpName,i)	)


        tmpAdd = guiFactory.doButton2(tmpSetRow,
                                      '+',
                                      Callback(setToolsLib.doAddSelected,self,i),
                                      'Add selected  to the set',
                                      en = not sInstance.refState)
        tmpRem= guiFactory.doButton2(tmpSetRow,
                                     '-',
                                     Callback(setToolsLib.doRemoveSelected,self,i),
                                     'Remove selected  to the set',
                                     en = not sInstance.refState)
        tmpKey = guiFactory.doButton2(tmpSetRow,
                                      'k',
                                      Callback(setToolsLib.doKeySet,self,i),			                              
                                      'Key set')
        tmpDeleteKey = guiFactory.doButton2(tmpSetRow,
                                            'd',
                                            Callback(setToolsLib.doDeleteCurrentSetKey,self,i),			                              			                                
                                            'delete set key')	

        tmpReset = guiFactory.doButton2(tmpSetRow,
                                        'r',
                                        Callback(setToolsLib.doResetSet,self,i),			                              			                                
                                        'Reset Set')
        mc.formLayout(tmpSetRow, edit = True,
                      af = [(tmpActive, "left", 4),
                            (tmpReset,"right",2)],
                      ac = [(tmpSel,"left",0,tmpActive),
                            (tmpName,"left",2,tmpSel),
                            (tmpName,"right",4,tmpAdd),
                            (tmpAdd,"right",2,tmpRem),
                            (tmpRem,"right",2,tmpKey),
                            (tmpKey,"right",2,tmpDeleteKey),
                            (tmpDeleteKey,"right",2,tmpReset)
                            ])

        MelSpacer(tmpSetRow, w = 2)

        #Build pop up for text field
        popUpMenu = MelPopupMenu(tmpName,button = 3)
        MelMenuItem(popUpMenu,
                    label = "<<<%s>>>"%b,
                    enable = False)

        if not enabledMenuLogic:
            if sInstance.mayaSetState:
                MelMenuItem(popUpMenu,
                            label = "<Maya Default Set>",
                            enable = False)				
            if sInstance.refState:
                MelMenuItem(popUpMenu,
                            label = "<Referenced>",
                            enable = False)		

        qssState = sInstance.qssState
        qssMenu = MelMenuItem(popUpMenu,
                              label = 'Qss',
                              cb = qssState,
                              en = enabledMenuLogic,
                              c = Callback(self.setInstances[i].isQss,not qssState))

        categoryMenu = MelMenuItem(popUpMenu,
                                   label = 'Make Type:',
                                   sm = True,
                                   en = enabledMenuLogic)

        for n in self.setTypes:
            MelMenuItem(categoryMenu,
                        label = n,
                        c = Callback(setToolsLib.guiDoSetType,self,i,n))


        MelMenuItem(popUpMenu ,
                    label = 'Copy Set',
                    c = Callback(setToolsLib.doCopySet,self,i))

        MelMenuItem(popUpMenu ,
                    label = 'Purge',
                    en = enabledMenuLogic,
                    c = Callback(setToolsLib.doPurgeSet,self,i))

        MelMenuItemDiv(popUpMenu)
        MelMenuItem(popUpMenu ,
                    label = 'Delete',
                    en = enabledMenuLogic,
                    c = Callback(setToolsLib.doDeleteSet,self,i))	



    NewSetRow = guiFactory.doButton2(MainForm,
                                     'Create Set',
                                     #lambda *a:setToolsLib.doCreateSet(self),
                                     lambda *a:self.uiUpdate_objectSets(),
                                     'Create new buffer from selected buffer')	

    SetMasterForm(edit = True,
                  af = [(SetListColumn,"top",0),
                        (SetListColumn,"left",0),
                        (SetListColumn,"right",0),
                        (SetListColumn,"bottom",0)])

    MainForm(edit = True,
             af = [(SetHeader,"top",0),
                   (SetHeader,"left",0),
                   (SetHeader,"right",0),
                   (HelpInfo,"left",0),
                   (HelpInfo,"right",0),
                   (AllSetsRow,"left",0),
                   (AllSetsRow,"right",0),
                   (SetListScroll,"left",0),
                   (SetListScroll,"right",0),
                   (NewSetRow,"left",4),
                   (NewSetRow,"right",4),
                   (NewSetRow,"bottom",4)],
             ac = [(HelpInfo,"top",0,SetHeader),
                   (AllSetsRow,"top",2,HelpInfo),
                   (SetListScroll,"top",2,AllSetsRow),
                   (SetListScroll,"bottom",0,NewSetRow)],
             attachNone = [(NewSetRow,"top")])    
    
    return MainForm

def uiBuild_objectSetRow(self, parent = None, objectSet = None):
    _str_func = 'uiBuild_objectSetRow'
    
    #Get our data --------------------------------------------------------------------------
    try:mObjectSet = cgmMeta.validateObjArg(objectSet,'cgmObjectSet')
    except Exception,err:
        log.error("|{0}| >> Failed to validate objectSet: {1}".format(_str_func,objectSet))
        log.error(err)
        return False
    
    
    if mObjectSet not in self.ml_objectSets:
        self.ml_objectSets.append(mObjectSet)
    index = self.ml_objectSets.index(mObjectSet)
    log.info("|{0}| >> objectSet: {1} | index: {2}".format(_str_func,objectSet, index))
    _short = mObjectSet.p_nameShort    
    _base = mObjectSet.p_nameBase
    
    #Get check box state
    b_activeState = False
    if mObjectSet.p_nameShort in self.var_ActiveSets.value:
        b_activeState = True
        
    #see if the no no fields are enabled
    b_editable = True
    refPrefix = mObjectSet.getReferencePrefix()
    
    if refPrefix:
        if refPrefix not in self.d_refSets.keys():
            self.d_refSets[refPrefix] = []
        self.d_refSets[refPrefix].append(mObjectSet)
        
    if mObjectSet.mayaSetState or refPrefix:				
        b_editable = False    
        
    b_animMode = self.var_animMode.value
    b_setupMode = self.var_setupMode.value
    b_qssState = mObjectSet.qssState
    
    #Build our row -----------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent)#bgc = cgmUI.guiBackgroundColor
        
    """
    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = '+',
              c = cgmGEN.Callback(uiFunc_valuesTweak,self,'+'),
              ann = "Adds value relatively to current")   """
    
    mUI.MelSpacer(parent = _row, w = 5)
    
    _cb = mUI.MelCheckBox(parent = _row,
                          annotation = 'Sets as active',
                          value = b_activeState,
                          onCommand =  cgmGEN.Callback(self.uiFunc_setActiveState,mObjectSet,True),
                          offCommand = cgmGEN.Callback(self.uiFunc_setActiveState,mObjectSet,False))
    
    self.d_activeStateCBs[mObjectSet] = _cb
    

    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = 's',
              c = cgmGEN.Callback(mObjectSet.select),
              ann = "Select members")
    
    if b_setupMode:
        _ref = mObjectSet.isReferenced()
        mc.button(parent=_row ,
                         ut = 'cgmUITemplate',                                                                                                
                         l = '+',
                         c = cgmGEN.Callback(mObjectSet.addSelected),
                         en = not _ref,
                         ann = "Add selected to objectSet: {0}".format(_short))    
        mc.button(parent=_row ,
                      ut = 'cgmUITemplate',                                                                                                
                      l = '-',
                      en = not _ref,                      
                      c = cgmGEN.Callback(mObjectSet.removeSelected),
                      ann = "Remove selected from objectSet: {0}".format(_short))  
        mc.button(parent=_row ,
                  ut = 'cgmUITemplate',                                                                                                
                  l = 'e',
                  c = cgmGEN.Callback(self.uiFunc_itemList_showToggle,mObjectSet),
                  ann = "Work with items in our list: {0}".format(_short))
    
    _uiTF_name = mUI.MelTextField(_row, w = 100,ut = 'cgmUIReservedTemplate', text = mObjectSet.p_nameBase,
                                  ann = _short,
                                  editable = False)
    
    _row.setStretchWidget(_uiTF_name)
    #_uiTF_name(edit = True,
               #ec = cgmGEN.Callback(ui.,self,tmpName,i)	)    
    
    #cgmMeta.cgmObjectSet().rese
    #Basics...
   
    if b_animMode:
        mc.button(parent=_row ,
                      ut = 'cgmUITemplate',                                                                                                
                      l = 'k',
                      c = cgmGEN.Callback(mObjectSet.key),
                      ann = "Key objectSet: {0}".format(_short))   
        
        mc.button(parent=_row ,
                      ut = 'cgmUITemplate',                                                                                                
                      l = 'd',
                      c = cgmGEN.Callback(mObjectSet.deleteKey),
                      ann = "Delete current keyes for objectSet: {0}".format(_short))   
    
    mc.button(parent=_row ,
                  ut = 'cgmUITemplate',                                                                                                
                  l = 'r',
                  c = cgmGEN.Callback(mObjectSet.reset),
                  ann = "Reset objectSet: {0}".format(_short))       
    mUI.MelSpacer(parent = _row, w = 5)    
    _row.layout()
    
    #Popup menu -------------------------------------------------------------------------
    #Build pop up for text field
    _popUpMenu = mUI.MelPopupMenu(_uiTF_name,button = 3)
    
    mUI.MelMenuItem(_popUpMenu,
                label = "<<<{0}>>>".format(_short),
                enable = False)
    
    if not b_editable:
        if mObjectSet.mayaSetState:
            mUI.MelMenuItem(_popUpMenu,
                        label = "<Maya Default Set>",
                        enable = False)				
        if refPrefix:
            mUI.MelMenuItem(_popUpMenu,
                        label = "<Referenced>",
                        enable = False)		
    
    #cgmMeta.cgmObjectSet().selectSelf
    qssMenu = mUI.MelMenuItem(_popUpMenu,
                              label = 'Qss',
                              cb = b_qssState,
                              en = b_editable,
                              c = cgmGEN.Callback(mObjectSet.makeQss,not b_qssState))

    categoryMenu = mUI.MelMenuItem(_popUpMenu,
                                   label = 'Make Type:',
                                   sm = True,
                                   en = b_editable)
    
    mUI.MelMenuItem(_popUpMenu,
                        label = 'Select set',
                        c = cgmGEN.Callback(mObjectSet.selectSelf))      
    mUI.MelMenuItem(_popUpMenu,
                    label = 'Purge',
                    en = b_editable,
                    c = cgmGEN.Callback(mObjectSet.purge))  
    
    mUI.MelMenuItem(_popUpMenu,
                    label = 'Rename',
                    en = b_editable,
                    c = cgmGEN.Callback(self.uiFunc_rename, mObjectSet))  
    mUI.MelMenuItem(_popUpMenu,
                    label = 'Copy',
                    en = b_editable,
                    c = cgmGEN.Callback(self.uiFunc_copy, mObjectSet))    
    mUI.MelMenuItem(_popUpMenu,
                    label = 'Log',
                    c = cgmGEN.Callback(mObjectSet.log))  
    mUI.MelMenuItemDiv( _popUpMenu )
    
    mUI.MelMenuItem(_popUpMenu,
                    label = 'Delete',
                    en = b_editable,
                    c = cgmGEN.Callback(self.uiFunc_delete, mObjectSet))       
   
    #Category menus --------------------------------------------------------------------
    for n in _l_setTypes:
        mUI.MelMenuItem(categoryMenu,
                        label = n,
                        c = cgmGEN.Callback(self.uiFunc_setType, mObjectSet, n))       
    
    
    #ItemsList -------------------------------------------------------------------------
    if b_setupMode:
        l_items = mObjectSet.getList()
        self.d_itemLists[mObjectSet] = l_items        
        height = 50
        if len(l_items) > 3:
            height = 150
        uiItemList = mUI.MelObjectScrollList(parent, allowMultiSelection=True,en=True,
                                             bgc = [.9,.9,.9],height = height, vis=False,
                                             sc = cgmGEN.Callback(self.uiFunc_itemList_dc, mObjectSet),
                                             dcc = cgmGEN.Callback(self.uiFunc_itemList_dc, mObjectSet))
                                             #selectCommand = self.uiFunc_selectParent_inList)
        self.d_itemScrollLists[mObjectSet] = uiItemList

    return


    for n in self.setTypes:
        MelMenuItem(categoryMenu,
                    label = n,
                    c = Callback(setToolsLib.guiDoSetType,self,i,n))


    MelMenuItem(popUpMenu ,
                label = 'Copy Set',
                c = Callback(setToolsLib.doCopySet,self,i))

    MelMenuItem(popUpMenu ,
                label = 'Purge',
                en = enabledMenuLogic,
                c = Callback(setToolsLib.doPurgeSet,self,i))

    MelMenuItemDiv(popUpMenu)
    MelMenuItem(popUpMenu ,
                label = 'Delete',
                en = enabledMenuLogic,
                c = Callback(setToolsLib.doDeleteSet,self,i))	    
    
    return



    


