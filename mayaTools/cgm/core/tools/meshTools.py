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
from cgm.core.lib.zoo import baseMelUI as zooUI
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
__defaultSize__ = 300, 550

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
    
    #@cgmGeneral.Timer    
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
        
    #@cgmGeneral.Timer   
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
        axisMenu = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l='Sym Axis', subMenu=True,
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

        
        """#>>> Result....
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
                                                                         rb = _rb))     """     
    
        
        #>>> Reset Options
        mUI.MelMenuItemDiv(self.uiMenu_OptionsMenu)
        mUI.MelMenuItem( self.uiMenu_OptionsMenu, l = 'Print base func keys',
                         c = lambda *a:self.get_FunctionOptions())
        mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Dock",
                         cb=self.var_Dock.value,
                         c= lambda *a: self.do_dockToggle())	
    #@cgmGeneral.Timer        
    def build_layoutWrapper(self,parent):
        try:
            uiColumn_main = mUI.MelColumn(self)

            #>>> Tab replacement
            self._l_tabOptions = ['math','cast','utils']	
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
            self.uiContainers_main.append( self.buildTab_math( uiColumn_main) )
            self.uiContainers_main.append( self.buildTab_cast( uiColumn_main) )
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
    #@cgmGeneral.Timer
    def setup_Variables(self):
        try:
            cgmUI.cgmGUI.setup_Variables(self)#Initialize parent ones, then add our own
            self.create_guiOptionVar('BaseObject',defaultValue = '')
            self.create_guiOptionVar('AxisMode', defaultValue = 0)#Register the option var    
            self.create_guiOptionVar('PivotMode', defaultValue = 0)#Register the option var     
            self.create_guiOptionVar('ProxiMode', defaultValue = 1)#Register the option var  
            self.create_guiOptionVar('ProxiResult', defaultValue = 4)#Register the option var              
            self.create_guiOptionVar('ProxiAmount', defaultValue = 0.0)#Register the option var            
            self.create_guiOptionVar('ProxiExpand', defaultValue = 1)#Register the option var                                         
            self.create_guiOptionVar('SpaceMode', defaultValue = 0)#Register the option var     
            self.create_guiOptionVar('ResultMode', defaultValue = 0)#Register the option var     
            self.create_guiOptionVar('Tolerance', defaultValue = .002)#Register the option var
            self.create_guiOptionVar('Multiplier', defaultValue = 1.0)#Register the option var
             
        except Exception,error:
            raise Exception,"{0} setup_Variables failed | {1}".format(self._str_reportStart,error)  
        
    def reload(self):
        """
        This must be in every gui to make docking work
        """
        run()
        
    def reset(self):	
        mUI.Callback(cgmUI.do_resetGuiInstanceOptionVars(self.l_optionVars,run)) 
    def buildTab_cast(self,parent):
        containerName = mUI.MelColumn(parent,vis=True)   
        
        cgmUI.add_Header('Click Mesh')
        _help = mUI.MelLabel(containerName,
                             bgc = dictionary.returnStateColor('help'),
                             align = 'center',
                             label = 'Click to create stuff...',
                             h=20,
                             vis = self.var_ShowHelp.value)	
    
        self.l_helpElements.append(_help)        
        
        
        return containerName
    
    def buildTab_utils(self,parent):
        #>>> Main Help
        containerName = mUI.MelColumn(parent,vis=True)   
        
        cgmUI.add_Header('Proximity Query')
        _help = mUI.MelLabel(containerName,
                             bgc = dictionary.returnStateColor('help'),
                             align = 'center',
                             label = 'Target proximity to selection or mesh',
                             h=20,
                             vis = self.var_ShowHelp.value)	
    
        self.l_helpElements.append(_help)  
        
        try:#        
            #Result Mode Change row 
            _str_section = 'ProxiExpand mode'
            _l_proxiOptions = ['None', 'Grow', 'Soft Select']
            _l_ann = ['',
                      'Use polyTraverse to grow selection',
                      'Use softSelection with linear falloff by the expandAmount Distance']
            
            self.uiRow_ProxiExpandMode = mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 3)
            mUI.MelSpacer(self.uiRow_ProxiExpandMode,w=5)
            mUI.MelLabel(self.uiRow_ProxiExpandMode, label = 'Expand: ',align='right')
            self.uiRow_ProxiExpandMode.setStretchWidget( mUI.MelSeparator(self.uiRow_ProxiExpandMode) )            
    
            self.uiRadioCollection_result = mUI.MelRadioCollection()
            
            self.uiOptions_proximityMode = []		
            
            for i,item in enumerate(_l_proxiOptions):
                self.uiOptions_proximityMode.append(self.uiRadioCollection_result.createButton(self.uiRow_ProxiExpandMode,label=item,
                                                                                               ann = _l_ann[i],
                                                                                               onCommand = mUI.Callback(self.var_ProxiExpand.setValue,i)))
               
            mc.radioCollection(self.uiRadioCollection_result, edit=True, sl=self.uiOptions_proximityMode[self.var_ProxiExpand.value])
       
       
            #mUI.MelLabel(self.uiRow_ProxiExpandMode,l='Amount:',align='right')
            self.uiTF_proxiAmount = mUI.MelTextField(self.uiRow_ProxiExpandMode,backgroundColor = [1,1,1],h=20,
                                                     ut = 'cgmUITemplate',
                                                     w = 30,
                                                     tx = self.var_ProxiAmount.value,
                                                     ec = lambda *a:self.valid_tf_proxiAmount(),
                                                     annotation = "How much to expand by")
            #mUI.MelSpacer(self.uiRow_baseValues,w = 5)       
            mUI.MelSpacer(self.uiRow_ProxiExpandMode,w=5)                 
            self.uiRow_ProxiExpandMode.layout()          
        except Exception,err:
            log.error("{0} {1} failed to load. err: {12}".format(self._str_reportStart,_str_section,err))
        
        try:#        
            #Result Mode Change row 
            _str_section = 'Proxi result'
            _l_proxiOptions = ['objs','face','edge','vtx','mesh']
            _l_ann = ['Select objects intersecting source',
                      'Select faces intersecting source',
                      'Select edges intersecting source',      
                      'Select vertices intersecting source',                                            
                      'Create proxi mesh based of intersections to source']            
            #self.create_guiOptionVar('ResultModeMode', defaultValue = 0)#Register the option var     
            
            self.uiRow_ProxiResult = mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 3)
            mUI.MelSpacer(self.uiRow_ProxiResult,w=5)
            mUI.MelLabel(self.uiRow_ProxiResult, label = 'Result: ',align='right')
            self.uiRow_ProxiResult.setStretchWidget( mUI.MelSeparator(self.uiRow_ProxiResult) )            
    
            self.uiRadioCollection_result = mUI.MelRadioCollection()
            
            self.uiOptions_proximityMode = []		
            
            for i,item in enumerate(_l_proxiOptions):
                self.uiOptions_proximityMode.append(self.uiRadioCollection_result.createButton(self.uiRow_ProxiResult,label=item,
                                                                                               ann = _l_ann[i],                                                                                            
                                                                                               onCommand = mUI.Callback(self.var_ProxiResult.setValue,i)))
            
            mc.radioCollection(self.uiRadioCollection_result, edit=True, sl=self.uiOptions_proximityMode[self.var_ProxiResult.value])
            mUI.MelSpacer(self.uiRow_ProxiResult,w=5)                 
            self.uiRow_ProxiResult.layout()          
        except Exception,err:
            log.error("{0} {1} failed to load. err: {12}".format(self._str_reportStart,_str_section,err))
       
        try:#        
            #Result Mode Change row 
            _str_section = 'Proxi mode'
            _l_proxiOptions = ['Ray Cast','Bounding Box']
            _l_ann = ['rayCast interior -- SLOW',
                      'Bounding box contains -- FASTER']
            #self.create_guiOptionVar('ResultModeMode', defaultValue = 0)#Register the option var     
            
            self.uiRow_ProxiMode = mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 3)
            mUI.MelSpacer(self.uiRow_ProxiMode,w=5)
            mUI.MelLabel(self.uiRow_ProxiMode, label = 'Mode: ',align='right')
            self.uiRow_ProxiMode.setStretchWidget( mUI.MelSeparator(self.uiRow_ProxiMode) )            
    
            self.uiRadioCollection_result = mUI.MelRadioCollection()
            
            self.uiOptions_proximityMode = []		
            
            for i,item in enumerate(_l_proxiOptions):
                self.uiOptions_proximityMode.append(self.uiRadioCollection_result.createButton(self.uiRow_ProxiMode,label=item,
                                                                                            ann = _l_ann[i],
                                                                                            onCommand = mUI.Callback(self.var_ProxiMode.setValue,i)))
            
            mc.radioCollection(self.uiRadioCollection_result, edit=True, sl=self.uiOptions_proximityMode[self.var_ProxiMode.value])
            cgmUI.add_Button(self.uiRow_ProxiMode,'Go',
                             lambda *a:self.targets_proxiMesh())
            mUI.MelSpacer(self.uiRow_ProxiMode,w=5)                 
            self.uiRow_ProxiMode.layout()          
        except Exception,err:
            log.error("{0} {1} failed to load. err: {12}".format(self._str_reportStart,_str_section,err))
   
        
        return containerName
    
    #@cgmGeneral.Timer
    def buildTab_math(self,parent):
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
                                                           w = 50,
                                                           #ec = lambda *a:self._UTILS.puppet_doChangeName(self),
                                                           annotation = "Our base object from which we process things in this tab...")
            mUI.MelSpacer(self.uiRow_baseLoad,w = 5)
            self.uiRow_baseLoad.setStretchWidget(self.uiTextField_baseObject)
            cgmUI.add_Button(self.uiRow_baseLoad,'<<', lambda *a:self.baseObject_set())
            cgmUI.add_Button(self.uiRow_baseLoad, 'Reprocess', 
                             lambda *a:self.baseObject_reprocessSym(),
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
            
            #Result Mode Change row 
            self._l_resultOptions = ['New','Modify','Values']
            _l_ann = ['Create a new object',
                      'Modify the existing base',
                      'Just do the math']
            #self.create_guiOptionVar('ResultModeMode', defaultValue = 0)#Register the option var     
            
            self.uiRow_ResultMode = mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 3)
            mUI.MelSpacer(self.uiRow_ResultMode,w=5)
            mUI.MelLabel(self.uiRow_ResultMode, label = 'result: ',align='right')
            self.uiRow_ResultMode.setStretchWidget( mUI.MelSeparator(self.uiRow_ResultMode) )            

            self.uiRadioCollection_result = mUI.MelRadioCollection()
            
            self.uiOptions_resultMode = []		
            
            for i,item in enumerate(self._l_resultOptions):
                self.uiOptions_resultMode.append(self.uiRadioCollection_result.createButton(self.uiRow_ResultMode,label=item,
                                                                                            ann = _l_ann[i],
                                                                                            onCommand = mUI.Callback(self.var_ResultMode.setValue,i)))
            
            mc.radioCollection(self.uiRadioCollection_result, edit=True, sl=self.uiOptions_resultMode[self.var_ResultMode.value])
            self.uiRow_ResultMode.layout()            
            
            #>>> Values Row...
            self.uiRow_baseValues = mUI.MelHSingleStretchLayout(containerName,expand = True,ut = 'cgmUISubTemplate')
            mUI.MelSpacer(self.uiRow_baseValues,w=5)
            mUI.MelLabel(self.uiRow_baseValues,l='Tolerance:',align='right')
            self.uiTF_tolerance = mUI.MelTextField(self.uiRow_baseValues,backgroundColor = [1,1,1],h=20,
                                                   ut = 'cgmUITemplate',
                                                   w = 50,
                                                   tx = self.var_Tolerance.value,
                                                   ec = lambda *a:self.valid_tf_tolerance(),
                                                   annotation = "Tolerance for symmetry calculation.")
            #mUI.MelSpacer(self.uiRow_baseValues,w = 5)
            self.uiRow_baseValues.setStretchWidget( mUI.MelSpacer(self.uiRow_baseValues) )
            mUI.MelLabel(self.uiRow_baseValues,l='Multiplier:',align='right')
            self.uiTF_multiplier = mUI.MelTextField(self.uiRow_baseValues,backgroundColor = [1,1,1],h=20,
                                                    ut = 'cgmUITemplate',
                                                    w = 50,
                                                    tx = self.var_Multiplier.value,                                                    
                                                    ec = lambda *a:self.valid_tf_multiplier(),
                                                    annotation = "Multiplier for symmetry calculation.")
            
            mUI.MelSpacer(self.uiRow_baseValues,w = 5)    
         
            self.uiRow_baseValues.layout()            

            
            #>>> Select
            mc.setParent(containerName)
            cgmUI.add_Header('Select')

            _help_baseSelect = mUI.MelLabel(containerName,
                                            bgc = dictionary.returnStateColor('help'),
                                            align = 'center',
                                            label = 'Select components on base from sym',
                                            h=20,
                                            vis = self.var_ShowHelp.value)	

            self.l_helpElements.append(_help_baseSelect)               
            
            self.uiRow_baseSelect = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_baseSelect, 'Base Center', 
                             lambda *a:self.baseObject_select('center'),
                             annotationText='Select center line vertices')
            cgmUI.add_Button(self.uiRow_baseSelect, 'Base Pos', 
                             lambda *a:self.baseObject_select('positive'),
                             annotationText='Select positive vertices')
            cgmUI.add_Button(self.uiRow_baseSelect, 'Base Neg', 
                             lambda *a:self.baseObject_select('negative'),
                             annotationText='Select negative vertices')
            cgmUI.add_Button(self.uiRow_baseSelect, 'Base Asym', 
                             lambda *a:self.baseObject_select('asymetrical'),
                             annotationText='Select asymetrical vertices')
            self.uiRow_baseSelect.layout()
            
            self.uiRow_targetSelect = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_targetSelect, 'Target Center', 
                             lambda *a:self.tarObject_select('center'),
                             annotationText='Select center line vertices')
            cgmUI.add_Button(self.uiRow_targetSelect, 'Target Pos', 
                             lambda *a:self.tarObject_select('positive'),
                             annotationText='Select positive vertices')
            cgmUI.add_Button(self.uiRow_targetSelect, 'Target Neg', 
                             lambda *a:self.tarObject_select('negative'),
                             annotationText='Select negative vertices')
            cgmUI.add_Button(self.uiRow_targetSelect, 'Target Asym', 
                             lambda *a:self.tarObject_select('asymetrical'),
                             annotationText='Select asymetrical vertices')
            self.uiRow_targetSelect.layout()            
            
            #>>> Targets
            mc.setParent(containerName)
            cgmUI.add_LineBreak()
            cgmUI.add_Header('Targets to Base')        
            _help_targetsToBase = mUI.MelLabel(containerName,
                                               bgc = dictionary.returnStateColor('help'),
                                               align = 'center',
                                               label = 'Functions using the base object for comparison',
                                               h=20,
                                               vis = self.var_ShowHelp.value)	

            self.l_helpElements.append(_help_targetsToBase) 
            
            #>>> Math...
            self.uiRow_baseMath = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_baseMath, 'Add', 
                             lambda *a:self.baseObject_meshMath('add'),
                             annotationText='Add pos data')
            cgmUI.add_Button(self.uiRow_baseMath, 'Subtract', 
                             lambda *a:self.baseObject_meshMath('subtract'),
                             annotationText='Subtract pos data')
            cgmUI.add_Button(self.uiRow_baseMath, 'Avg', 
                             lambda *a:self.baseObject_meshMath('average'),
                             annotationText='Average pos data')
            self.uiRow_baseMath.layout() 
            
            #>>> Diff...
            self.uiRow_baseDiff = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_baseDiff, 'Diff', 
                             lambda *a:self.baseObject_meshMath('diff'),
                             annotationText='Difference from target to base')
            cgmUI.add_Button(self.uiRow_baseDiff, '+Diff', 
                             lambda *a:self.baseObject_meshMath('+diff'),
                             annotationText='base + (diff * multiplier)')
            cgmUI.add_Button(self.uiRow_baseDiff, '-Diff', 
                             lambda *a:self.baseObject_meshMath('-diff'),
                             annotationText='base - (diff * multiplier)')   
            cgmUI.add_Button(self.uiRow_baseDiff, 'xDiff', 
                             lambda *a:self.baseObject_meshMath('xDiff'),
                             annotationText='x only values of diff')    
            cgmUI.add_Button(self.uiRow_baseDiff, 'yDiff', 
                             lambda *a:self.baseObject_meshMath('yDiff'),
                             annotationText='y only values of diff')    
            cgmUI.add_Button(self.uiRow_baseDiff, 'zDiff', 
                             lambda *a:self.baseObject_meshMath('zDiff'),
                             annotationText='z only values of diff')    
            self.uiRow_baseDiff.layout()             
            
            #>>> Blend...
            self.uiRow_baseBlend = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_baseBlend, 'blend', 
                             lambda *a:self.baseObject_meshMath('blend'),
                             annotationText='~blendshape result if you added as a target using multiplier as weight')
            cgmUI.add_Button(self.uiRow_baseBlend, 'xBlend', 
                             lambda *a:self.baseObject_meshMath('xBlend'),
                             annotationText='x only blendshape target')
            cgmUI.add_Button(self.uiRow_baseBlend, 'yBlend', 
                             lambda *a:self.baseObject_meshMath('yBlend'),
                             annotationText='y only blendshape target')
            cgmUI.add_Button(self.uiRow_baseBlend, 'zBlend', 
                             lambda *a:self.baseObject_meshMath('zBlend'),
                             annotationText='z only blendshape target')                         
            self.uiRow_baseBlend.layout()    
            
            #>>>Blend Slider...
            uiRow_blend = mUI.MelHSingleStretchLayout(containerName ,ut='cgmUITemplate',expand = True, padding = 5)
            mUI.MelSpacer(uiRow_blend,w=5)
            mUI.MelLabel(uiRow_blend,l='Blend:',align='right')            
            self.uiSlider_baseBlend = mUI.MelFloatSlider(uiRow_blend,-1.5,1.5,0,step = .2)
            self.uiSlider_baseBlend.setPostChangeCB(mUI.Callback(self.baseObject_blendSlider))
            cgmUI.add_Button(uiRow_blend,'R',
                             mUI.Callback(self.uiSlider_baseBlend.reset,False),
                             'Reset this slider')
            mUI.MelSpacer(uiRow_blend,w=5)	            
            uiRow_blend.setStretchWidget(self.uiSlider_baseBlend)#Set stretch            
            
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
            
            
            
            #>>> Targets
            mc.setParent(containerName)
            cgmUI.add_LineBreak()
            cgmUI.add_Header('Target Math')        
            _help_targets = mUI.MelLabel(containerName,
                                         bgc = dictionary.returnStateColor('help'),
                                         align = 'center',
                                         label = 'Fuctions between targets. Some Cumulative effects.',
                                         h=20,
                                         vis = self.var_ShowHelp.value)	

            self.l_helpElements.append(_help_targets) 
            
            #>>> Target Math...
            self.uiRow_targetsMath = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_targetsMath, 'Add', 
                             lambda *a:self.targets_meshMath('add'),
                             annotationText='Add pos data')
            cgmUI.add_Button(self.uiRow_targetsMath, 'Subtract', 
                             lambda *a:self.targets_meshMath('subtract'),
                             annotationText='Subtract pos data')
            cgmUI.add_Button(self.uiRow_targetsMath, 'Avg', 
                             lambda *a:self.targets_meshMath('average'),
                             annotationText='Average pos data')
            cgmUI.add_Button(self.uiRow_targetsMath, 'Mult', 
                             lambda *a:self.targets_meshMath('multiply'),
                             annotationText='Multiply pos data')            
            self.uiRow_targetsMath.layout()   
            
            #>>> Diff...
            self.uiRow_targetDiff = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_targetDiff, 'Diff', 
                             lambda *a:self.targets_meshMath('diff'),
                             annotationText='Difference from target to target')
            cgmUI.add_Button(self.uiRow_targetDiff, '+Diff', 
                             lambda *a:self.targets_meshMath('+diff'),
                             annotationText='target + (diff * multiplier)')
            cgmUI.add_Button(self.uiRow_targetDiff, '-Diff', 
                             lambda *a:self.targets_meshMath('-diff'),
                             annotationText='target - (diff * multiplier)')   
            cgmUI.add_Button(self.uiRow_targetDiff, 'xDiff', 
                             lambda *a:self.targets_meshMath('xDiff'),
                             annotationText='x only values of diff')    
            cgmUI.add_Button(self.uiRow_targetDiff, 'yDiff', 
                             lambda *a:self.targets_meshMath('yDiff'),
                             annotationText='y only values of diff')    
            cgmUI.add_Button(self.uiRow_targetDiff, 'zDiff', 
                             lambda *a:self.targets_meshMath('zDiff'),
                             annotationText='z only values of diff')    
            self.uiRow_targetDiff.layout()             
            
            #>>> Blend...
            self.uiRow_targetBlend = mUI.MelHLayout(containerName)
            cgmUI.add_Button(self.uiRow_targetBlend, 'blend', 
                             lambda *a:self.targets_meshMath('blend'),
                             annotationText='~blendshape result if you added as a target using multiplier as weight')
            cgmUI.add_Button(self.uiRow_targetBlend, 'xBlend', 
                             lambda *a:self.targets_meshMath('xBlend'),
                             annotationText='x only blendshape target')
            cgmUI.add_Button(self.uiRow_targetBlend, 'yBlend', 
                             lambda *a:self.targets_meshMath('yBlend'),
                             annotationText='y only blendshape target')
            cgmUI.add_Button(self.uiRow_targetBlend, 'zBlend', 
                             lambda *a:self.targets_meshMath('zBlend'),
                             annotationText='z only blendshape target')                         
            self.uiRow_targetBlend.layout() 
            
            
            #>>>Blend Slider...
            uiRow_blendTargets = mUI.MelHSingleStretchLayout(containerName ,ut='cgmUITemplate',expand = True, padding = 5)
            mUI.MelSpacer(uiRow_blendTargets,w=5)
            mUI.MelLabel(uiRow_blendTargets,l='Blend:',align='right')            
            self.uiSlider_targetsBlend = mUI.MelFloatSlider(uiRow_blendTargets,-1.5,1.5,0,step = .2)
            self.uiSlider_targetsBlend.setPostChangeCB(mUI.Callback(self.targets_blendSlider))
            cgmUI.add_Button(uiRow_blendTargets,'R',
                             mUI.Callback(self.uiSlider_targetsBlend.reset,False),
                             'Reset this slider')
            mUI.MelSpacer(uiRow_blendTargets,w=5)	            
            uiRow_blendTargets.setStretchWidget(self.uiSlider_targetsBlend)#Set stretch              
            
            return containerName
        except Exception,error:
            raise Exception,"{0} buildTab_Asset failed | {1}".format(self._str_reportStart,error)
        
    def valid_tf_tolerance(self):
        _buffer = self.uiTF_tolerance.getValue()
        self.var_Tolerance.value = _buffer
        if self.var_Tolerance.value == _buffer:
            self.uiTF_tolerance.setValue(_buffer)
        else:self.uiTF_tolerance.setValue(self.var_Tolerance.value)
        
    def valid_tf_proxiAmount(self):
        _buffer = self.uiTF_proxiAmount.getValue()
        self.var_ProxiAmount.value = _buffer
        if self.var_ProxiAmount.value == _buffer:
            self.uiTF_proxiAmount.setValue(_buffer)
        else:self.uiTF_proxiAmount.setValue(self.var_ProxiAmount.value)
        
    def valid_tf_multiplier(self):
        _buffer = self.uiTF_multiplier.getValue()
        if _buffer:
            self.var_Multiplier.value = _buffer
            if self.var_Multiplier.value == _buffer:
                self.uiTF_multiplier.setValue(_buffer)
        else:
            var_Multiplier.value = ''
        self.uiTF_multiplier.setValue(self.var_Multiplier.value)
        
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
        _d['multiplier'] = self.var_Multiplier.value
        _d['axis'] = 'xyz'[self.var_AxisMode.value]
        _d['space'] = ['object','world'][self.var_SpaceMode.value]
        _d['pivot'] = ['pivot','world','boundingBox'][ self.var_PivotMode.value]
        cgmGeneral.log_info_dict(_d,"Function Options Found...")
        self._d_funcOptions = _d
        return _d
    
    def targets_meshMath(self,mode = None, multiplier = None):
        _sel = mc.ls(sl=True)
        _d = self.get_FunctionOptions()        
        _ml_objs = cgmMeta.validateObjListArg(_sel,'cgmObject',mayaType='mesh')
        if not _ml_objs:
            log.error("{0}: No selected objects.".format(self._str_reportStart))                
            return False
        if multiplier is None:
            _multiplier = d['multiplier']
        else:
            _multiplier = multiplier        
        try:
            log.info(GEO.meshMath([mObj.mNode for mObj in _ml_objs],
                         mode,
                         space = _d['space'],
                         center =_d['pivot'], 
                         axis=_d['axis'], 
                         tolerance= _d['tolerance'], 
                         resultMode=_d['resultMode'],
                         multiplier=_multiplier,
                         symDict=self._d_baseSym))  
        except Exception,err:
            log.error("{0}: meshMath(targets) fail. err:{1}".format(self._str_reportStart,err))                
    
    def targets_proxiMesh(self):
        _sel = mc.ls(sl=True)
        _ml_objs = cgmMeta.validateObjListArg(_sel,'cgmObject',mayaType='mesh')

        if not _ml_objs:
            log.error("{0}: No selected objects.".format(self._str_reportStart))                
            return False
        
        if len(_ml_objs) < 2:
            log.error("{0}: Must have at least two objects.".format(self._str_reportStart))                
            return False
        
        _base = _ml_objs[-1]
        
        try:
            log.info(GEO.get_proximityGeo(_base.mNode,[mObj.mNode for mObj in _ml_objs[:-1]],
                                          self.var_ProxiMode.value, returnMode= self.var_ProxiResult.value,
                                          expandBy=self.var_ProxiExpand.value, expandAmount=self.var_ProxiAmount.value)) 
        except Exception,err:
            log.error("{0}: create_proximityMeshFromTarget() fail. | err:{1}".format(self._str_reportStart,err))                
                       
    def baseObject_blendSlider(self):
        _multiplier = self.uiSlider_baseBlend(q=True, value=True)
        self.baseObject_meshMath('blend',_multiplier)
        
    def targets_blendSlider(self):
        _multiplier = self.uiSlider_targetsBlend(q=True, value=True)
        self.targets_meshMath('blend',_multiplier)
        
    def baseObject_meshMath(self,mode = None, multiplier = None):
        _sel = mc.ls(sl=True)
        _d = self.get_FunctionOptions()        
        _ml_objs = cgmMeta.validateObjListArg(_sel,'cgmObject',mayaType='mesh')
        if self._mi_baseObject in _ml_objs:
            _ml_objs.remove(self._mi_baseObject)
        if not _ml_objs:
            log.error("{0}: No selected objects.".format(self._str_reportStart))                
            return False
        if multiplier is None:
            _multiplier = d['multiplier']
        else:
            _multiplier = multiplier
            
        for mObj in _ml_objs:
            try:
                log.info(GEO.meshMath([mObj.mNode,
                             self._mi_baseObject.mNode],
                             mode,
                             space = _d['space'],
                             center =_d['pivot'], 
                             axis=_d['axis'], 
                             tolerance= _d['tolerance'], 
                             resultMode=_d['resultMode'],
                             multiplier=_multiplier,
                             symDict=self._d_baseSym) ) 
            except Exception,err:
                log.error("{0}: meshMath(baseObject) fail. {1} | err:{2}".format(self._str_reportStart,mObj.mNode,err))                
                
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
            
    def tarObject_select(self,mode = 'center'):
        if not self._d_baseSym:
            log.error("{0}: nobase sym dict.".format(self._str_reportStart))
            return False      
        
        _sel = mc.ls(sl=True)
        _ml_objs = cgmMeta.validateObjListArg(_sel,'cgmObject',mayaType='mesh')
        if not _ml_objs:
            log.error("{0}: No selected objects.".format(self._str_reportStart))                
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
            for mObj in _ml_objs:
                _obj = mObj.mNode            
                for i in _buffer:
                    _sel.append("{0}.vtx[{1}]".format(_obj,i))
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
        

        