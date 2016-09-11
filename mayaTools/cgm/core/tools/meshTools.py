"""
------------------------------------------
HotkeyFactory: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
Issues:
-runtime command only available in mel
================================================================
"""
# From Python =============================================================
import copy
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgmPy.validateArgs as cgmValid
import cgm.core.cgm_General as cgmGeneral
import cgm.core.classes.GuiFactory as cgmUI
from cgm.core.lib import geo_Utils as GEO
reload(GEO)
reload(cgmUI)
mUI = cgmUI.mUI
import cgm.lib.zoo.zooPyMaya.baseMelUI as zooUI
from cgm.lib import dictionary
mayaVersion = cgmGeneral.__mayaVersion__

#>>> Root settings =============================================================
__version__ = 'Alpha - 09.09.2016'
__toolName__ = 'cgmMeshTools'
__description__ = "These are tools for working with mesh"
#__toolURL__ = 'www.cgmonks.com'
#__author__ = 'Josh Burton'
#__owner__ = 'CG Monks'
#__website__ = 'www.cgmonks.com'
__defaultSize__ = 300, 500

def run():
    win = go()  
    
class go(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = __toolName__    
    WINDOW_TITLE = '{0} - {1}'.format(__toolName__,__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = __defaultSize__
    
    @cgmGeneral.Timer    
    def insert_init(self,*args,**kws):
        """ This is meant to be overloaded per gui """
        log.debug(">>> cgmGUI.__init__")	
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        log.info(self.__call__(q=True, title=True))

        self.description = __description__
        self.__version__ = __version__
        self.dockCnt = '%sDock'%__toolName__	
        self.__toolName__ = __toolName__		
        self.l_allowedDockAreas = ['right', 'left']
        self.WINDOW_NAME = __toolName__
        self.WINDOW_TITLE = go.WINDOW_TITLE
        self.DEFAULT_SIZE = __defaultSize__    
        self.dockCnt = '%sDock'%__toolName__
        self._str_reportStart = " {0} >> ".format(__toolName__)
        self._d_baseSym = {}
        self._d_funcOptions = {}
        self._mi_baseObject = False
        
    @cgmGeneral.Timer   
    def buildMenu_options( self, *args):
        self.uiMenu_OptionsMenu.clear()
        
        #>>> Space....
        self._l_spaceOptions = ['Object','World']
        _ann = 'Set the space for value querying.'
        spaceMenu = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l='Space', subMenu=True,
                                     ann = _ann)
        self.uiRC_space = mUI.MelRadioMenuCollection()
        self.uiOptions_space = []		
                    
        for i,item in enumerate(self._l_spaceOptions):
            if i == self.var_SpaceMode.value:
                _rb = True
            else:_rb = False
            self.uiOptions_space.append(self.uiRC_space.createButton(spaceMenu,label=item,
                                                                     ann = _ann,
                                                                     c = mUI.Callback(self.var_SpaceMode.setValue,i),
                                                                     rb = _rb))            
        
        #>>> Axis....
        self._l_axisOptions = ['yz','xz','xy']

        _ann = 'Set the axis for value querying.'
        axisMenu = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l='Axis', subMenu=True,
                                     ann = _ann)
        self.uiRC_axis = mUI.MelRadioMenuCollection()
        self.uiOptions_axis = []		
                    
        for i,item in enumerate(self._l_axisOptions):
            if i == self.var_AxisMode.value:
                _rb = True
            else:_rb = False
            self.uiOptions_axis.append(self.uiRC_axis.createButton(axisMenu,label=item,
                                                                     ann = _ann,
                                                                     c = mUI.Callback(self.var_AxisMode.setValue,i),
                                                                     rb = _rb))            

        
        #>>> Result....
        self._l_resultMode = ['new','modify','values']

        _ann = 'Set the Result mode...'
        axisMenu = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l='Result Mode', subMenu=True,
                                     ann = _ann)
        self.uiRC_resultMode = mUI.MelRadioMenuCollection()
        self.uiOptions_axis = []		
                    
        for i,item in enumerate(self._l_resultMode):
            if i == self.var_ResultMode.value:
                _rb = True
            else:_rb = False
            self.uiOptions_axis.append(self.uiRC_resultMode.createButton(axisMenu,label=item,
                                                                         ann = _ann,
                                                                         c = mUI.Callback(self.var_ResultMode.setValue,i),
                                                                         rb = _rb))          
    
        
        #>>> Reset Options
        mUI.MelMenuItemDiv(self.uiMenu_OptionsMenu)
        mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Dock",
                         cb=self.var_Dock.value,
                         c= lambda *a: self.do_dockToggle())	
    @cgmGeneral.Timer        
    def build_layoutWrapper(self,parent):
        try:
            uiColumn_main = mUI.MelColumn(self)

            #>>> Tab replacement
            self._l_tabOptions = ['base','math','utils']	
            self.create_guiOptionVar('ToolMode', defaultValue = self._l_tabOptions[0])#Register the option var
            mUI.MelSeparator(uiColumn_main,ut = 'cgmUIHeaderTemplate',h=5)
            #Mode Change row 
            self.uiRow_ModeSet = mUI.MelHSingleStretchLayout(uiColumn_main,ut='cgmUISubTemplate',padding = 3)
            mUI.MelSpacer(self.uiRow_ModeSet,w=5)
            mUI.MelLabel(self.uiRow_ModeSet, label = 'Choose Mode: ',align='right')
            self.uiRow_ModeSet.setStretchWidget( mUI.MelSeparator(self.uiRow_ModeSet) )		
            self.uiRow_ModeSet.layout()

            self.uiRadioCollection_main = mUI.MelRadioCollection()
            self.uiOptions_main = []		

            #build our sub section options
            self.uiContainers_main = []
            self.uiContainers_main.append( self.buildTab_base( uiColumn_main) )
            self.uiContainers_main.append( self.buildTab_math( uiColumn_main) )
            self.uiContainers_main.append( self.buildTab_utils( uiColumn_main) )
            
            for item in self._l_tabOptions:
                self.uiOptions_main.append(self.uiRadioCollection_main.createButton(self.uiRow_ModeSet,label=item,
                                                                                    onCommand = mUI.Callback(cgmUI.doToggleModeState,item,self._l_tabOptions,
                                                                                                             self.var_ToolMode.name,self.uiContainers_main)))
            self.uiRow_ModeSet.layout()
            mc.radioCollection(self.uiRadioCollection_main, edit=True, sl=self.uiOptions_main[self._l_tabOptions.index(self.var_ToolMode.value)])

            #self.asset_autoLoad()#Autoload asset	
            #self.reports_updateAll()
            #self.presets_updateLists()
            self.baseObject_set(self.var_BaseObject.value)
            
        except Exception,error:
            raise Exception,"{0} build_layoutWrapper failed | {1}".format(self._str_reportStart,error)
    @cgmGeneral.Timer
    def setup_Variables(self):
        try:
            cgmUI.cgmGUI.setup_Variables(self)#Initialize parent ones, then add our own
            self.create_guiOptionVar('BaseObject',defaultValue = '')
            self.create_guiOptionVar('AxisMode', defaultValue = 0)#Register the option var    
            self.create_guiOptionVar('PivotMode', defaultValue = 0)#Register the option var                 
            self.create_guiOptionVar('SpaceMode', defaultValue = 0)#Register the option var     
            self.create_guiOptionVar('ResultMode', defaultValue = 0)#Register the option var     
            self.create_guiOptionVar('Tolerance', defaultValue = .002)#Register the option var
            self.create_guiOptionVar('Multiplier', defaultValue = 0.0)#Register the option var
            
            
            #self.create_guiOptionVar('PresetFrameCollapse',defaultValue = 1)
            #self.create_guiOptionVar('FaceBuildOption',defaultValue = False, varType = 'bool')	    
            #self.create_guiOptionVar('BlendShapesOption',defaultValue = 0, varType = 'int')	    
            #self.create_guiOptionVar('FaceSetupTypeOption',defaultValue = 0, varType = 'int')	    
        except Exception,error:
            raise Exception,"{0} setup_Variables failed | {1}".format(self._str_reportStart,error)  
        
    def reload(self):
        """
        This must be in every gui to make docking work
        """
        run()
        
    def reset(self):	
        mUI.Callback(cgmUI.do_resetGuiInstanceOptionVars(self.l_optionVars,run)) 
    def buildTab_math(self,parent):
        return mUI.MelColumn(parent,vis=True) 
    def buildTab_utils(self,parent):
        return mUI.MelColumn(parent,vis=True) 
    @cgmGeneral.Timer
    def buildTab_base(self,parent):
        try:
            #ui_customizeMainForm = mUI.MelFormLayout(self.Get(),numberOfDivisions=100)
            #uiScroll_customize = mUI.MelScrollLayout(ui_customizeMainForm)				
            #uiWrapper_Customize = uiScroll_customize
            #>>> Main Help
            containerName = mUI.MelColumn(parent,vis=True)   
            self.uiReport_CustomizeHelp = mUI.MelLabel(containerName,
                                                       bgc = dictionary.returnStateColor('help'),
                                                       align = 'center',
                                                       label = 'Add a base object and do other functions based on that',
                                                       h=20,
                                                       vis = self.var_ShowHelp.value)	

            self.l_helpElements.append(self.uiReport_CustomizeHelp)
            
            mc.setParent(containerName)
            cgmUI.add_Header('Base Object')
            
            #>>> Load To Field
            
            #>>> Change name Row
            self.uiRow_baseLoad = mUI.MelHSingleStretchLayout(containerName,expand = True,ut = 'cgmUISubTemplate')
            mUI.MelSpacer(self.uiRow_baseLoad,w=5)
            mUI.MelLabel(self.uiRow_baseLoad,l='Base:',align='right')
            self.uiTextField_baseObject = mUI.MelTextField(self.uiRow_baseLoad,backgroundColor = [1,1,1],h=20,
                                                           ut = 'cgmUITemplate',
                                                           #ec = lambda *a:self._UTILS.puppet_doChangeName(self),
                                                           annotation = "Our base object from which we process things in this tab...")
            mUI.MelSpacer(self.uiRow_baseLoad,w = 5)
            self.uiRow_baseLoad.setStretchWidget(self.uiTextField_baseObject)
            cgmUI.add_Button(self.uiRow_baseLoad,'<<', lambda *a:self.baseObject_set())
            cgmUI.add_Button(self.uiRow_baseLoad, 'Reprocess', 
                             lambda *a:self.get_FunctionOptions(),
                             annotationText='')               
            mUI.MelSpacer(self.uiRow_baseLoad,w = 5)            
            self.uiRow_baseLoad.layout()	
            

            #>>> Base Report			
            self.uiReport_base = mUI.MelLabel(containerName,
                                              bgc = dictionary.returnStateColor('help'),
                                              align = 'center',
                                              label = '...',
                                              h=20)

            
            #Mode Change row 
            self._l_pivotOptions = ['Pivot','World','BoundingBox']
            self.create_guiOptionVar('PivotMode', defaultValue = 0)#Register the option var     
            
            self.uiRow_Pivot = mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 3)
            mUI.MelSpacer(self.uiRow_Pivot,w=5)
            mUI.MelLabel(self.uiRow_Pivot, label = 'symMode: ',align='right')
            self.uiRow_Pivot.setStretchWidget( mUI.MelSeparator(self.uiRow_Pivot) )            

            self.uiRadioCollection_pivot = mUI.MelRadioCollection()
            
            self.uiOptions_pivot = []		
            
            for i,item in enumerate(self._l_pivotOptions):
                self.uiOptions_pivot.append(self.uiRadioCollection_pivot.createButton(self.uiRow_Pivot,label=item,
                                                                                    onCommand = mUI.Callback(self.var_PivotMode.setValue,i)))
            
            mc.radioCollection(self.uiRadioCollection_pivot, edit=True, sl=self.uiOptions_pivot[self.var_PivotMode.value])
            self.uiRow_Pivot.layout()
            
            
            #>>> Values Row...
            self.uiRow_baseValues = mUI.MelHSingleStretchLayout(containerName,expand = True,ut = 'cgmUISubTemplate')
            mUI.MelSpacer(self.uiRow_baseValues,w=5)
            mUI.MelLabel(self.uiRow_baseValues,l='Tolerance:',align='right')
            self.uiTF_tolerance = mUI.MelTextField(self.uiRow_baseValues,backgroundColor = [1,1,1],h=20,
                                                   ut = 'cgmUITemplate',
                                                   w = 75,
                                                   tx = self.var_Tolerance.value,
                                                   #ec = lambda *a:self._UTILS.puppet_doChangeName(self),
                                                   annotation = "Tolerance for symmetry calculation.")
            #mUI.MelSpacer(self.uiRow_baseValues,w = 5)
            self.uiRow_baseValues.setStretchWidget( mUI.MelSpacer(self.uiRow_baseValues) )
            mUI.MelLabel(self.uiRow_baseValues,l='Multiplier:',align='right')
            self.uiTF_multiplier = mUI.MelTextField(self.uiRow_baseValues,backgroundColor = [1,1,1],h=20,
                                                    ut = 'cgmUITemplate',
                                                    w = 75,
                                                    tx = self.var_Multiplier.value,                                                    
                                                    #ec = lambda *a:self._UTILS.puppet_doChangeName(self),
                                                    annotation = "Multiplier for symmetry calculation.")
            
            mUI.MelSpacer(self.uiRow_baseValues,w = 5)    
         
            self.uiRow_baseValues.layout()            

            
            #>>> Select
            mc.setParent(containerName)
            cgmUI.add_Header('Base Select')

            _help_baseSelect = mUI.MelLabel(containerName,
                                            bgc = dictionary.returnStateColor('help'),
                                            align = 'center',
                                            label = 'Select components on base from sym',
                                            h=20,
                                            vis = self.var_ShowHelp.value)	

            self.l_helpElements.append(_help_baseSelect)               
            
            self.uiRow_baseSelect = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_baseSelect, 'Center', 
                             lambda *a:self.baseObject_select('center'),
                             annotationText='')
            cgmUI.add_Button(self.uiRow_baseSelect, 'Pos', 
                             lambda *a:self.baseObject_select('positive'),
                             annotationText='')
            cgmUI.add_Button(self.uiRow_baseSelect, 'Neg', 
                             lambda *a:self.baseObject_select('negative'),
                             annotationText='')
            cgmUI.add_Button(self.uiRow_baseSelect, 'Asym', 
                             lambda *a:self.baseObject_select('asymetrical'),
                             annotationText='')            
            self.uiRow_baseSelect.layout()
            
            #>>> Targets
            mc.setParent(containerName)
            cgmUI.add_LineBreak()
            cgmUI.add_Header('Targets')        
            _help_targets = mUI.MelLabel(containerName,
                                         bgc = dictionary.returnStateColor('help'),
                                         align = 'center',
                                         label = 'Functions using the base object for comparison',
                                         h=20,
                                         vis = self.var_ShowHelp.value)	

            self.l_helpElements.append(_help_targets) 
            
            #>>> Math...
            self.uiRow_baseMath = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_baseMath, 'Add', 
                             lambda *a:self.baseObject_meshMath('add'),
                             annotationText='')
            cgmUI.add_Button(self.uiRow_baseMath, 'Subtract', 
                             lambda *a:self.baseObject_meshMath('subtract'),
                             annotationText='')
            cgmUI.add_Button(self.uiRow_baseMath, 'Avg', 
                             lambda *a:self.baseObject_meshMath('average'),
                             annotationText='')            
            self.uiRow_baseMath.layout() 
            
            #>>> Math...
            self.uiRow_baseDiff = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_baseDiff, 'Diff', 
                             lambda *a:self.baseObject_meshMath('diff'),
                             annotationText='')
            cgmUI.add_Button(self.uiRow_baseDiff, '+Diff', 
                             lambda *a:self.baseObject_meshMath('+diff'),
                             annotationText='')      
            cgmUI.add_Button(self.uiRow_baseDiff, '-Diff', 
                             lambda *a:self.baseObject_meshMath('-diff'),
                             annotationText='')   
            cgmUI.add_Button(self.uiRow_baseDiff, 'xDiff', 
                             lambda *a:self.baseObject_meshMath('xDiff'),
                             annotationText='')    
            cgmUI.add_Button(self.uiRow_baseDiff, 'yDiff', 
                             lambda *a:self.baseObject_meshMath('yDiff'),
                             annotationText='')    
            cgmUI.add_Button(self.uiRow_baseDiff, 'zDiff', 
                             lambda *a:self.baseObject_meshMath('zDiff'),
                             annotationText='')                
            self.uiRow_baseDiff.layout()             
            
            #>>> Math...
            self.uiRow_baseBlend = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_baseBlend, 'blend', 
                             lambda *a:self.baseObject_meshMath('blend'),
                             annotationText='')
            cgmUI.add_Button(self.uiRow_baseBlend, 'xBlend', 
                             lambda *a:self.baseObject_meshMath('xBlend'),
                             annotationText='')
            cgmUI.add_Button(self.uiRow_baseBlend, 'yBlend', 
                             lambda *a:self.baseObject_meshMath('yBlend'),
                             annotationText='')
            cgmUI.add_Button(self.uiRow_baseBlend, 'zBlend', 
                             lambda *a:self.baseObject_meshMath('zBlend'),
                             annotationText='')                         
            self.uiRow_baseBlend.layout()             
            
            #>>> Sym...
            self.uiRow_baseSym = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_baseSym, 'Flip', 
                             lambda *a:self.baseObject_meshMath('flip'),
                             annotationText='')
            cgmUI.add_Button(self.uiRow_baseSym, 'SymPos', 
                             lambda *a:self.baseObject_meshMath('symPos'),
                             annotationText='')
            cgmUI.add_Button(self.uiRow_baseSym, 'SymNeg', 
                             lambda *a:self.baseObject_meshMath('symNeg'),
                             annotationText='')             
            self.uiRow_baseSym.layout()             
            
            return containerName
        except Exception,error:
            raise Exception,"{0} buildTab_Asset failed | {1}".format(self._str_reportStart,error)
        
    def baseObject_set(self, base = None):
        #self.uiTextField_baseObject
        _sel = mc.ls(sl=1)
        _base = base
        if _sel and _base == None:
            _base = _sel[0]
        #elif self.var_BaseObject.value:
            #_base = self.var_BaseObject.value
            
        if _base:
            try:
                self._mi_baseObject = cgmMeta.cgmObject(_base)
                self.uiTextField_baseObject.setValue(_base)
                self.var_BaseObject.value = _base
                self.baseObject_reprocessSym()
            except Exception,err:
                log.warning("{0} No base found: {1}".format(self._str_reportStart, err))
                self._mi_baseObject = False
                self.uiTextField_baseObject.setValue('')
                self.var_BaseObject.value = ''
                self._d_baseSym = {}
        else:
            self._mi_baseObject = False
            log.warning("{0} No base found".format(self._str_reportStart))
        
    def get_FunctionOptions(self):
        self._d_funcOptions = {}
        
        _d = self._d_funcOptions
        _d['resultMode'] = ['new','modify','values'][self.var_ResultMode.value]
        _d['tolerance'] = self.var_Tolerance.value
        _d['multiplier'] = None #self.var_Multiplier.value
        _d['axis'] = 'xyz'[self.var_AxisMode.value]
        _d['space'] = ['object','world'][self.var_SpaceMode.value]
        _d['pivot'] = ['pivot','world','boundingBox'][ self.var_PivotMode.value]
        cgmGeneral.log_info_dict(_d,"Function Options Found...")
        self._d_funcOptions = _d
        return _d
        
    def baseObject_meshMath(self,mode = None):
        _sel = mc.ls(sl=True)
        _d = self.get_FunctionOptions()        
        _ml_objs = cgmMeta.validateObjListArg(_sel,'cgmObject',mayaType='mesh')
        if self._mi_baseObject in _ml_objs:
            _ml_objs.remove(self._mi_baseObject)
        if not _ml_objs:
            log.error("{0}: No selected objects.".format(self._str_reportStart))                
            return False
        for mObj in _ml_objs:
            try:
                GEO.meshMath(mObj.mNode,
                             self._mi_baseObject.mNode,
                             mode,
                             space = _d['space'],
                             center =_d['pivot'], 
                             axis=_d['axis'], 
                             tolerance= _d['tolerance'], 
                             resultMode=_d['resultMode'],
                             multiplier=_d['multiplier'],
                             symDict=self._d_baseSym)  
            except Exception,err:
                log.error("{0}: meshMath fail. {1} | err:{2}".format(self._str_reportStart,mObj.mNode,err))                
                
    def baseObject_reprocessSym(self):
        try:
            _d = self.get_FunctionOptions()
            _d_baseSym = GEO.get_symmetryDict(self._mi_baseObject.mNode,
                                              center=_d['pivot'], 
                                              axis=_d['axis'], 
                                              tolerance= _d['tolerance'], 
                                              returnMode = 'indices') 
            self._d_baseSym = _d_baseSym
            
            #...fix our report 
            _report = ["Asymetrical: {0}".format( len(_d_baseSym['asymmetrical']))]     
            
            self.uiReport_base(edit = True, label = '||'.join(_report) )
            
        except Exception,err:
            log.error("{0} failed to reprocessSym: {1}".format(self._str_reportStart,err))
            self._d_baseSym = {}
            self.uiReport_base(edit = True, label = "..." )
            
    def baseObject_select(self,mode = 'center'):
        if not self._mi_baseObject:
            log.error("{0}: no base object loaded.".format(self._str_reportStart))
            return False
        if not self._d_baseSym:
            log.error("{0}: nobase sym dict.".format(self._str_reportStart))
            return False            
        
        if mode == 'center':
            _buffer =  self._d_baseSym['center']
        elif mode == 'positive':
            _buffer = self._d_baseSym['positive']
        elif mode == 'negative':
            _buffer = self._d_baseSym['negative']
        elif mode == 'asymetrical':
            _buffer = self._d_baseSym['asymmetrical']
            if not _buffer:
                log.error("{0}: no asymmetrical verts found.".format(self._str_reportStart))                

        if _buffer:
            _sel =[]
            for i in _buffer:
                _sel.append("{0}.vtx[{1}]".format(self._mi_baseObject.mNode,i))
            mc.select(_sel)
        
class EXMAPLE(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = __toolName__    
    WINDOW_TITLE = '{0} - {1}'.format(__toolName__,__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = __defaultSize__
    
    def insert_init(self,*args,**kws):
        """ This is meant to be overloaded per gui """
        log.debug(">>> cgmGUI.__init__")	
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        log.info(self.__call__(q=True, title=True))

        self.description = __description__
        self.__version__ = __version__
        self.dockCnt = '%sDock'%__toolName__	
        self.__toolName__ = __toolName__		
        self.l_allowedDockAreas = ['right', 'left']
        self.WINDOW_NAME = __toolName__
        self.WINDOW_TITLE = go.WINDOW_TITLE
        self.DEFAULT_SIZE = __defaultSize__    
        self.dockCnt = '%sDock'%__toolName__
        self._str_reportStart = " {0} >> ".format(__toolName__)
        
        #self.log_selfReport()
        
    def setup_Variables(self):
        try:
            cgmUI.cgmGUI.setup_Variables(self)#Initialize parent ones, then add our own
            #self.create_guiOptionVar('ActiveAsset',defaultValue = '')
            #self.create_guiOptionVar('PresetFrameCollapse',defaultValue = 1)
            #self.create_guiOptionVar('FaceBuildOption',defaultValue = False, varType = 'bool')	    
            #self.create_guiOptionVar('BlendShapesOption',defaultValue = 0, varType = 'int')	    
            #self.create_guiOptionVar('FaceSetupTypeOption',defaultValue = 0, varType = 'int')	    
        except Exception,error:
            raise Exception,"{0} setup_Variables failed | {1}".format(self._str_reportStart,error)  
        
    def reload(self):
        """
        This must be in every gui to make docking work
        """
        run()
        
    def reset(self):	
        mUI.Callback(gui.do_resetGuiInstanceOptionVars(self.l_optionVars,run)) 
        

        