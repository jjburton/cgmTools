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
#reload(GEO)
#reload(cgmUI)
mUI = cgmUI.mUI
from cgm.core.lib.zoo import baseMelUI as zooUI
from cgm.lib import lists
from cgm.lib import dictionary
from cgm.lib import search
from cgm.core.classes import DraggerContextFactory
from cgm.core.lib import shapeCaster as ShapeCaster
from cgm.core.lib import selection_Utils as selUtils
#reload(selUtils)
#reload(ShapeCaster)
#reload(DraggerContextFactory)
mayaVersion = cgmGeneral.__mayaVersion__

#>>> Root settings =============================================================
__version__ = '0.08182017'
__toolName__ = 'cgmMeshTools'
__description__ = "These are tools for working with mesh"
#__toolURL__ = 'www.cgmonks.com'
#__author__ = 'Josh Burton'
#__owner__ = 'CG Monks'
#__website__ = 'www.cgmonks.com'
__defaultSize__ = 300, 600

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
    TOOLNAME = '__toolName__'

    #@cgmGeneral.Timer    
    def insert_init(self,*args,**kws):
        """ This is meant to be overloaded per gui """
        log.debug(">>> cgmGUI.__init__")	
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        log.info(self.__call__(q=True, title=True))

        self.description = __description__
        self.__version__ = __version__
        self.__toolName__ = __toolName__		
        self.l_allowedDockAreas = ['left']
        self.WINDOW_NAME = __toolName__
        self.WINDOW_TITLE = go.WINDOW_TITLE
        self.DEFAULT_SIZE = __defaultSize__    
        self._str_reportStart = " {0} >> ".format(__toolName__)
        self._d_baseSym = {}
        self._d_funcOptions = {}
        self._mi_baseObject = False
        self._ml_castTargets = []
        self._l_castItems = []
        self.tool_clickMesh = False    
        self._l_spaceOptions = ['Object','World']
        self._l_createOptions = ['locator','joint','jointChain','curve','follicle','group']
        self._l_symAxisOptions = ['yz','xz','xy']
        self._l_latheAxisOptions = ['x','y','z']
        self._l_aimAxisOptions = ['x+','x-','y+','y-','z+','z-']
        self._l_extendMode = ['NONE','segment','radial','disc','cylinder','loliwrap','endCap']
        
        self.setup_Variables()

    def buildMenu_help( self, *args):
        self.uiMenu_HelpMenu.clear()
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Show Help",
                         cb=self.var_ShowHelp.value,
                         c= lambda *a: self.do_showHelpToggle())

        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Docs - meshTools",
                         c='import webbrowser;webbrowser.open("http://docs.cgmonks.com/meshtools.html");')
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Docs - MeshMath",
                         c='import webbrowser;webbrowser.open("http://docs.cgmonks.com/meshtools.html#math");')
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Docs - Casting",
                         c='import webbrowser;webbrowser.open("http://docs.cgmonks.com/meshtools.html#cast");')	
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Docs - Utils",
                         c='import webbrowser;webbrowser.open("http://docs.cgmonks.com/meshtools.html#utils");')	

        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )
        mUI.MelMenuItemDiv( self.uiMenu_HelpMenu )
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="About",
                         c=lambda *a: self.showAbout() )

        # Update Mode
        iMenu_loggerMaster = mUI.MelMenuItem( self.uiMenu_HelpMenu, l='Logger Level', subMenu=True)
        mUI.MelMenuItem( iMenu_loggerMaster, l='Info',
                         c=lambda *a: self.set_loggingInfo())
        mUI.MelMenuItem( iMenu_loggerMaster, l='Debug',
                         c=lambda *a: self.set_loggingDebug())        
    #@cgmGeneral.Timer   
    def buildMenu_options( self, *args):
        self.uiMenu_OptionsMenu.clear()

        try:#>>> Space....
            _str_section = 'Space menu'	
            _ann = 'Set the space for value querying.'
            spaceMenu = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l='Space', subMenu=True,
                                         ann = _ann)
            self.uiRC_space = mUI.MelRadioMenuCollection()
            self.uiOptions_space = []		
            _v = self.var_SpaceMode.value
            for i,item in enumerate(self._l_spaceOptions):
                if i == _v:
                    _rb = True
                else:_rb = False
                self.uiOptions_space.append(self.uiRC_space.createButton(spaceMenu,label=item,
                                                                         ann = _ann,
                                                                         c = mUI.Callback(self.var_SpaceMode.setValue,i),
                                                                         rb = _rb))            
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))


        try:#>>> Create....
            _str_section = 'create options menu'
            _ann = 'What to create when a tool needs it'

            _createMenu = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l='Create', subMenu=True,
                                           ann = _ann)
            self.uiRC_create = mUI.MelRadioMenuCollection()
            self.uiOptions_create = []		
            _v = self.var_ClickCreate.value

            for i,item in enumerate(self._l_createOptions):
                if i == _v:
                    _rb = True
                else:_rb = False
                self.uiOptions_create.append(self.uiRC_create.createButton(_createMenu,label=item,
                                                                           ann = _ann,
                                                                           c = mUI.Callback(self.var_ClickCreate.setValue,i),
                                                                           rb = _rb))   
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))

        """try:#>>> Sym Axis....
            _str_section = 'Sym Axis menu'

            _ann = 'Set the axis for value querying.'
            axisMenu = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l='Sym Axis', subMenu=True,
                                        ann = _ann)
            self.uiRC_axis = mUI.MelRadioMenuCollection()
            self.uiOptions_axis = []		
            _v = self.var_AxisMode.value

            for i,item in enumerate(self._l_symAxisOptions):
                if i == _v:
                    _rb = True
                else:_rb = False
                self.uiOptions_axis.append(self.uiRC_axis.createButton(axisMenu,label=item,
                                                                       ann = _ann,
                                                                       c = mUI.Callback(self.var_AxisMode.setValue,i),
                                                                       rb = _rb))   
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))"""

        try:#>>> Lathe Axis....
            _str_section = 'Lathe menu'	
            _ann = 'Set the lathe axis for casting'
            latheAxisMenu = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l='Lathe Axis', subMenu=True,
                                             ann = _ann)
            self.uiRC_latheAxis = mUI.MelRadioMenuCollection()
            self.uiOptions_latheAxis = []		
            _v = self.var_CastLatheAxis.value

            for i,item in enumerate(self._l_latheAxisOptions):
                if i == _v:
                    _rb = True
                else:_rb = False
                self.uiOptions_latheAxis.append(self.uiRC_latheAxis.createButton(latheAxisMenu,
                                                                                 label=item,
                                                                                 ann = _ann,
                                                                                 c = mUI.Callback(self.var_CastLatheAxis.setValue,i),
                                                                                 rb = _rb))      
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))

        try:#>>> Aim Axis....
            _str_section = 'Aim menu'	
            _ann = 'Set the aim axis for casting'
            aimAxisMenu = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l='Aim Axis', subMenu=True,
                                           ann = _ann)
            self.uiRC_aimAxis = mUI.MelRadioMenuCollection()
            self.uiOptions_aimAxis = []		
            _v = self.var_CastAimAxis.value

            for i,item in enumerate(self._l_aimAxisOptions):
                if i == _v:
                    _rb = True
                else:_rb = False
                self.uiOptions_aimAxis.append(self.uiRC_aimAxis.createButton(aimAxisMenu,
                                                                             label=item,
                                                                             ann = _ann,
                                                                             c = mUI.Callback(self.var_CastAimAxis.setValue,i),
                                                                             rb = _rb))      
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))

        try:#>>> Object Up Axis....
            _str_section = 'Object up menu'	
            _ann = 'Set the object up axis for casting'
            objectUpAxisMenu = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l='Obj Up Axis', subMenu=True,
                                                ann = _ann)
            self.uiRC_objUpAxis = mUI.MelRadioMenuCollection()
            self.uiOptions_objUpAxis = []		
            _v = self.var_CastObjectUp.value

            for i,item in enumerate(self._l_aimAxisOptions):
                if i == _v:
                    _rb = True
                else:_rb = False
                self.uiOptions_objUpAxis.append(self.uiRC_objUpAxis.createButton(objectUpAxisMenu,
                                                                                 label=item,
                                                                                 ann = _ann,
                                                                                 c = mUI.Callback(self.var_CastObjectUp.setValue,i),
                                                                                 rb = _rb))      
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))

        try:#>>> Extend Mode....
            _str_section = 'Object up menu'	
            _ann = 'Set the wrap extend mode'
            extendMenu = mUI.MelMenuItem( self.uiMenu_OptionsMenu, l='Extend Mode', subMenu=True,
                                          ann = _ann)
            self.uiRC_castExtend = mUI.MelRadioMenuCollection()
            self.uiOptions_castExtend = []		
            _v = self.var_CastExtendMode.value

            for i,item in enumerate(self._l_extendMode):
                if i == _v:
                    _rb = True
                else:_rb = False
                self.uiOptions_castExtend.append(self.uiRC_castExtend.createButton(extendMenu,
                                                                                   label=item,
                                                                                   ann = _ann,
                                                                                   c = mUI.Callback(self.var_CastExtendMode.setValue,i),
                                                                                   rb = _rb))      
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))

        #>>> Reset Options
        mUI.MelMenuItemDiv(self.uiMenu_OptionsMenu)
        mUI.MelMenuItem( self.uiMenu_OptionsMenu, l = 'Print base func keys',
                         c = lambda *a:self.get_FunctionOptions())
        mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Dock",
                         #cb=self.var_Dock.value,
                         c= lambda *a: self.do_dock())	
    #@cgmGeneral.Timer        
    def build_layoutWrapper(self,parent):
        try:
            _MainForm = mUI.MelFormLayout(self,ut='cgmUISubTemplate')            
            uiColumn_main = mUI.MelColumn(_MainForm,w=300)

            #>>> Tab replacement
            self._l_tabOptions = ['math','cast','utils']	
            self.create_guiOptionVar('ToolMode', defaultValue = self._l_tabOptions[0])#Register the option var
            mUI.MelSeparator(uiColumn_main,ut = 'cgmUIHeaderTemplate',h=5)
            #Mode Change row 
            self.uiRow_ModeSet = mUI.MelHSingleStretchLayout(uiColumn_main,ut='cgmUISubTemplate',padding = 1)
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
            
            
            _row_cgm = cgmUI.add_cgmFooter(_MainForm)            
            _MainForm(edit = True,
                      af = [(uiColumn_main,"top",0),
                            (uiColumn_main,"left",0),
                            (uiColumn_main,"right",0),                        
                            (_row_cgm,"left",0),
                            (_row_cgm,"right",0),                        
                            (_row_cgm,"bottom",0),
            
                            ],
                      ac = [(uiColumn_main,"bottom",2,_row_cgm),
                            ],
                      attachNone = [(_row_cgm,"top")])            
        except Exception,error:
            raise Exception,"{0} build_layoutWrapper failed | {1}".format(self._str_reportStart,error)
    #@cgmGeneral.Timer
    def setup_Variables(self):
        #cgmUI.cgmGUI.setup_Variables(self)#Initialize parent ones, then add our own
        self.create_guiOptionVar('ShowHelp',defaultValue = 0)
        
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
        self.create_guiOptionVar('ClickMode', defaultValue = 0)#Register the option var
        self.create_guiOptionVar('ClickCreate', defaultValue = 0)#Register the option var
        self.create_guiOptionVar('ClickDrag', defaultValue = 0)#Register the option var
        self.create_guiOptionVar('ClickClamp', defaultValue = 0)#Register the option var

        self.create_guiOptionVar('SelectBuffer', defaultValue = '')

        self.create_guiOptionVar('CastLatheAxis', defaultValue = 2)
        self.create_guiOptionVar('CastAimAxis', defaultValue = 2)
        self.create_guiOptionVar('CastPoints', defaultValue = 9)
        self.create_guiOptionVar('CastXOffset', defaultValue = 0.0)
        self.create_guiOptionVar('CastYOffset', defaultValue = 0.0)
        self.create_guiOptionVar('CastZOffset', defaultValue = 0.0)
        self.create_guiOptionVar('CastMarkHits', defaultValue = 0)
        self.create_guiOptionVar('CastClosedCurve', defaultValue = 1)	    
        self.create_guiOptionVar('CastMinRotate', defaultValue = 0.0)
        self.create_guiOptionVar('CastMinUse', defaultValue = 0)	    
        self.create_guiOptionVar('CastMaxRotate', defaultValue = 0.0)
        self.create_guiOptionVar('CastMaxUse', defaultValue = 0)	  
        self.create_guiOptionVar('CastDegree', defaultValue = 3)	    	    
        self.create_guiOptionVar('CastRange', defaultValue = 100.0)
        self.create_guiOptionVar('CastClosestInRange', defaultValue = 1)

        self.create_guiOptionVar('CastObjectUp', defaultValue = 1)
        self.create_guiOptionVar('CastInsetMult', defaultValue = 0.2)
        self.create_guiOptionVar('CastInsetUse', defaultValue = 0)	    
        self.create_guiOptionVar('CastXRootOffset', defaultValue = 0.0)
        self.create_guiOptionVar('CastYRootOffset', defaultValue = 0.0)
        self.create_guiOptionVar('CastZRootOffset', defaultValue = 0.0)	    
        self.create_guiOptionVar('CastJoin', defaultValue = 1)
        self.create_guiOptionVar('CastExtendMode', defaultValue = 1)
        self.create_guiOptionVar('CastMidMeshCast', defaultValue = 0)
        self.create_guiOptionVar('CastRotateBank', defaultValue = 0.0)


    def reload(self):
        """
        This must be in every gui to make docking work
        """
        run()

    def reset(self):	
        mUI.Callback(cgmUI.do_resetGuiInstanceOptionVars(self.l_optionVars,run)) 

    def buildTab_cast(self,parent):
        containerName = mUI.MelColumn(parent,vis=True) 
        #containerName = mUI.MelScrollLayout(parent,vis=True) 

        cgmUI.add_Header('Cast Targets')
        _help = mUI.MelLabel(containerName,
                             bgc = dictionary.returnStateColor('help'),
                             align = 'center',
                             label = 'Load and remove targets for casting',
                             h=20,
                             vis = self.var_ShowHelp.value)	

        self.l_helpElements.append(_help)

        self.uiList_Targets = mUI.MelObjectScrollList(containerName, ut='cgmUITemplate',
                                                      allowMultiSelection=True, h=100 )
        self.uiList_updateCastTargets()

        try:#Cast targets row
            _str_section = 'Cast Targets Row'
            _uiRow_castTargets = mUI.MelHLayout(containerName,padding = 1)
            cgmUI.add_Button(_uiRow_castTargets, 'Load Selected', 
                             lambda *a:self.castTargets_loadSelected(),
                             annotationText='Select center line vertices')
            cgmUI.add_Button(_uiRow_castTargets, 'Load All', 
                             lambda *a:self.castTargets_loadAll(),
                             annotationText='Select positive vertices')
            cgmUI.add_Button(_uiRow_castTargets, 'Clear All', 
                             lambda *a:self.castTargets_clearAll(),
                             annotationText='Select negative vertices')
            _uiRow_castTargets.layout()      
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))

        #>>>CLICK MESH ========================================================================
        mc.setParent(containerName)
        cgmUI.add_Header('Click Mesh')
        _help = mUI.MelLabel(containerName,
                             bgc = dictionary.returnStateColor('help'),
                             align = 'center',
                             label = 'Click to create stuff...',
                             h=20,
                             vis = self.var_ShowHelp.value)	

        self.l_helpElements.append(_help)    

        try:#Mode ---------------------------------------------------------------------------------------
            _str_section = 'Click Mesh Mode'
            _uiRow_clickMeshMode =  mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)

            mUI.MelSpacer(_uiRow_clickMeshMode,w=2)	
            mUI.MelLabel(_uiRow_clickMeshMode,l='Mode')
            _uiRow_clickMeshMode.setStretchWidget( mUI.MelSeparator(_uiRow_clickMeshMode, w=2) )	    
            self.ClickMeshOptions = ['surface','bisect','midPoint']
            self.uiRadioCollection_clickMesh = mUI.MelRadioCollection()
            self.uiOptions_clickMesh = []	    

            for i,item in enumerate(self.ClickMeshOptions):
                self.uiOptions_clickMesh.append(self.uiRadioCollection_clickMesh.createButton(_uiRow_clickMeshMode,label=item,                                                                                           
                                                                                              onCommand = mUI.Callback(self.var_ClickMode.setValue,i)))


            mUI.MelSpacer(_uiRow_clickMeshMode,w=2)		
            _uiRow_clickMeshMode.layout()      

            mc.radioCollection(self.uiRadioCollection_clickMesh ,edit=True,sl= (self.uiOptions_clickMesh[ (self.var_ClickMode.value) ]))
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))

        try:#Click Mesh Buttons ---------------------------------------------------------------------------------------
            _str_section = 'Click Mesh Buttons'
            _uiRow_clickMeshButtons =  mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)

            mUI.MelSpacer(_uiRow_clickMeshButtons,w=2)	
            #mUI.MelLabel(_uiRow_clickMeshButtons,l='Mode')

            self.uiBool_ClickDrag = mUI.MelCheckBox(_uiRow_clickMeshButtons,
                                                    label = 'Drag',
                                                    annotation = "Stores drag data rather than just clicks",		                           
                                                    value = bool(self.var_ClickDrag.value),
                                                    onCommand = mUI.Callback(self.var_ClickDrag.setValue,1),
                                                    offCommand = mUI.Callback(self.var_ClickDrag.setValue,0))

            mUI.MelLabel(_uiRow_clickMeshButtons,l='Clamp:')	    
            self.uiTF_ClickClamp = mUI.MelTextField(_uiRow_clickMeshButtons,
                                                    w = 30,
                                                    tx = self.var_ClickClamp.value,
                                                    ec = lambda *a:self.valid_tf_clickClamp())	    

            _uiRow_clickMeshButtons.setStretchWidget( mUI.MelSeparator(_uiRow_clickMeshButtons, w=2) )	    

            mUI.MelSpacer(_uiRow_clickMeshButtons,w=2)
            cgmUI.add_Button(_uiRow_clickMeshButtons,'Start',
                             mUI.Callback(self.clickMesh_start))
            cgmUI.add_Button(_uiRow_clickMeshButtons,'Drop',
                             mUI.Callback(self.clickMesh_drop))
            cgmUI.add_Button(_uiRow_clickMeshButtons,'Snap',
                             mUI.Callback(self.clickMesh_snap))            
            mUI.MelSpacer(_uiRow_clickMeshButtons,w=2)		    
            _uiRow_clickMeshButtons.layout()      

            #mc.radioCollection(self.ClickMeshCreateModeCollection ,edit=True,sl= (self.ClickMeshCreateModeCollectionChoices[ (self.ClickMeshModeOptionVar.value) ]))
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))

        mc.setParent(containerName)	
        cgmUI.add_LineSubBreak()
        cgmUI.add_LineBreak()

        #>>>Curve Slice ========================================================================
        mc.setParent(containerName)
        cgmUI.add_Header('Object Cast')
        _help = mUI.MelLabel(containerName,
                             bgc = dictionary.returnStateColor('help'),
                             align = 'center',
                             label = 'Cast curves from selected objects',
                             h=20,
                             vis = self.var_ShowHelp.value)	

        self.l_helpElements.append(_help)  	

        try:#Curve Slice Row 1 ---------------------------------------------------------------------------------------
            _str_section = 'Curve Slice Row 1'
            _uiRow_slice =  mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)

            mUI.MelSpacer(_uiRow_slice,w=2)	

            mUI.MelCheckBox(_uiRow_slice,
                            label = 'mark',
                            annotation = "Leave the hit locators",		                           
                            value = bool(self.var_CastMarkHits.value),
                            onCommand = mUI.Callback(self.var_CastMarkHits.setValue,1),
                            offCommand = mUI.Callback(self.var_CastMarkHits.setValue,0))
            mUI.MelCheckBox(_uiRow_slice,
                            label = 'closed',
                            annotation = "Leave the hit locators",		                           
                            value = bool(self.var_CastClosedCurve.value),
                            onCommand = mUI.Callback(self.var_CastClosedCurve.setValue,1),
                            offCommand = mUI.Callback(self.var_CastClosedCurve.setValue,0))	
            mUI.MelCheckBox(_uiRow_slice,
                            label = 'near',
                            annotation = "Closest hit in range",		                           
                            value = bool(self.var_CastClosestInRange.value),
                            onCommand = mUI.Callback(self.var_CastClosestInRange.setValue,1),
                            offCommand = mUI.Callback(self.var_CastClosestInRange.setValue,0))	
            _uiRow_slice.setStretchWidget( mUI.MelSeparator(_uiRow_slice, w=2) )
            mUI.MelLabel(_uiRow_slice,l='d:')	    
            self.uiIF_CastDegree = mUI.MelIntField(_uiRow_slice,
                                                   w = 20,
                                                   minValue = 1,
                                                   value = self.var_CastDegree.value,
                                                   annotation = 'Degree of curve to create',
                                                   ec = lambda *a:self.valid_intf_castDegree())	 	    
            mUI.MelLabel(_uiRow_slice,l='p:')	    
            self.uiIF_CastPoints = mUI.MelIntField(_uiRow_slice,
                                                   w = 25,
                                                   minValue = 6,
                                                   value = self.var_CastPoints.value,
                                                   annotation = 'How many points to cast',
                                                   ec = lambda *a:self.valid_intf_castPoints())	    

            mUI.MelSpacer(_uiRow_slice,w=2)		    
            _uiRow_slice.layout()    
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))

        try:#Curve Slice Row 2 ---------------------------------------------------------------------------------------
            _str_section = 'Curve Slice Row 2'
            _uiRow_slice =  mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)

            mUI.MelSpacer(_uiRow_slice,w=2)	


            #mUI.MelLabel(_uiRow_slice,l='minRot:')	
            mUI.MelCheckBox(_uiRow_slice,
                            label = '<',
                            annotation = "Use minRotate values",		                           
                            value = bool(self.var_CastMinUse.value),
                            onCommand = mUI.Callback(self.var_CastMinUse.setValue,1),
                            offCommand = mUI.Callback(self.var_CastMinUse.setValue,0))	    
            self.uiFF_CastMinRotate = mUI.MelFloatField(_uiRow_slice,
                                                        w = 40,
                                                        annotation = 'minRotate values',
                                                        precision = 2,
                                                        value = self.var_CastMinRotate.value,
                                                        ec = lambda *a:self.valid_ff_CastMinRotate())

            mUI.MelCheckBox(_uiRow_slice,
                            label = '>',
                            annotation = "Use maxRotate values",		                           
                            value = bool(self.var_CastMaxUse.value),
                            onCommand = mUI.Callback(self.var_CastMaxUse.setValue,1),
                            offCommand = mUI.Callback(self.var_CastMaxUse.setValue,0))	 	    
            self.uiFF_CastMaxRotate = mUI.MelFloatField(_uiRow_slice,
                                                        w = 40,
                                                        annotation = 'maxRotate values',	                                                
                                                        precision = 2,
                                                        value = self.var_CastMaxRotate.value,
                                                        ec = lambda *a:self.valid_ff_CastMaxRotate())		    
            mUI.MelSpacer(_uiRow_slice,w=2)	
            _uiRow_slice.setStretchWidget( mUI.MelSeparator(_uiRow_slice, w=2) )	    	    
            mUI.MelLabel(_uiRow_slice,l='dist:')	    
            self.uiFF_CastRange = mUI.MelFloatField(_uiRow_slice,
                                                    w = 60,
                                                    precision = 1,
                                                    annotation = 'Maximum cast range',
                                                    value = self.var_CastRange.value,
                                                    ec = lambda *a:self.valid_ff_CastRange())		    
            mUI.MelSpacer(_uiRow_slice,w=2)    

            _uiRow_slice.layout()    
            mc.setParent(containerName)
            cgmUI.add_LineSubBreak()	    
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))


        try:#Curve Slice Row 3 ---------------------------------------------------------------------------------------
            _str_section = 'Curve Slice Row 3'
            _uiRow_slice =  mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)

            mUI.MelSpacer(_uiRow_slice,w=2)	
            #mUI.MelLabel(_uiRow_clickMeshButtons,l='Mode')

            mUI.MelLabel(_uiRow_slice,l='Offset:')	    
            self.uiFF_CastXOffset = mUI.MelFloatField(_uiRow_slice,
                                                      w = 40,
                                                      precision = 2,
                                                      value = self.var_CastXOffset.value,
                                                      ec = lambda *a:self.valid_ff_CastXOffset())		    
            self.uiFF_CastYOffset = mUI.MelFloatField(_uiRow_slice,
                                                      w = 40,
                                                      precision = 2,
                                                      value = self.var_CastYOffset.value,
                                                      ec = lambda *a:self.valid_ff_CastYOffset())
            self.uiFF_CastZOffset = mUI.MelFloatField(_uiRow_slice,
                                                      w = 40,
                                                      precision = 2,
                                                      value = self.var_CastZOffset.value,
                                                      ec = lambda *a:self.valid_ff_CastZOffset())	    

            mUI.MelSpacer(_uiRow_slice,w=2)	
            _button_cast = cgmUI.add_Button(_uiRow_slice,"Slice",
                                            mUI.Callback(self.cast_slice))
            _uiRow_slice.setStretchWidget( _button_cast )	    
            mUI.MelSpacer(_uiRow_slice,w=2)		    
            _uiRow_slice.layout()  
            mc.setParent(containerName)
            cgmUI.add_LineSubBreak()	  
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))

        try:#Wrap Row 1 ---------------------------------------------------------------------------------------
            _str_section = 'Wrap Row 1'

            mc.setParent(containerName)
            cgmUI.add_HeaderBreak()	    
            mc.setParent(containerName)
            cgmUI.add_LineSubBreak()	  	    
            _uiRow_wrap =  mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)

            mUI.MelSpacer(_uiRow_wrap,w=2)	
            #mUI.MelLabel(_uiRow_clickMeshButtons,l='Mode')

            mUI.MelLabel(_uiRow_wrap,l='Root:')	    
            _ann = 'Root offset',

            self.uiFF_CastXRoot = mUI.MelFloatField(_uiRow_wrap,
                                                    w = 40,
                                                    precision = 2,
                                                    value = self.var_CastXRootOffset.value,
                                                    ec = lambda *a:self.valid_ff_CastXRootOffset())		    
            self.uiFF_CastYRoot = mUI.MelFloatField(_uiRow_wrap,
                                                    w = 40,
                                                    precision = 2,
                                                    value = self.var_CastYRootOffset.value,
                                                    ec = lambda *a:self.valid_ff_CastYRootOffset())
            self.uiFF_CastZRoot = mUI.MelFloatField(_uiRow_wrap,
                                                    w = 40,
                                                    precision = 2,
                                                    value = self.var_CastZRootOffset.value,
                                                    ec = lambda *a:self.valid_ff_CastZRootOffset())	    

            mUI.MelSpacer(_uiRow_wrap,w=2)

            _uiRow_wrap.setStretchWidget( mUI.MelSeparator(_uiRow_wrap, w=2) )	    	    
            mUI.MelLabel(_uiRow_wrap,l='bank:')	    
            self.uiFF_CastRotateBank = mUI.MelFloatField(_uiRow_wrap,
                                                         w = 60,
                                                         precision = 1,
                                                         annotation = 'Bank rotate casting object',
                                                         value = self.var_CastRotateBank.value,
                                                         ec = lambda *a:self.valid_ff_CastRotateBank())		    


            mUI.MelSpacer(_uiRow_wrap,w=2)		    
            _uiRow_wrap.layout()  
            mc.setParent(containerName)
            cgmUI.add_SectionBreak()
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))  

        try:#Wrap Slice Row 2 ---------------------------------------------------------------------------------------
            _str_section = 'Wrap Slice Row 2'
            _uiRow_slice =  mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)

            mUI.MelSpacer(_uiRow_slice,w=2)	

            mUI.MelCheckBox(_uiRow_slice,
                            label = 'mid',
                            annotation = "Midmesh cast",		                           
                            value = bool(self.var_CastMidMeshCast.value),
                            onCommand = mUI.Callback(self.var_CastMidMeshCast.setValue,1),
                            offCommand = mUI.Callback(self.var_CastMidMeshCast.setValue,0))
            mUI.MelCheckBox(_uiRow_slice,
                            label = 'join',
                            annotation = "Join the cast curves",		                           
                            value = bool(self.var_CastJoin.value),
                            onCommand = mUI.Callback(self.var_CastJoin.setValue,1),
                            offCommand = mUI.Callback(self.var_CastJoin.setValue,0))


            _ann = ''
            mUI.MelCheckBox(_uiRow_slice,
                            label = 'inset',
                            annotation = "Use inset mult",		                           
                            value = bool(self.var_CastInsetUse.value),
                            onCommand = mUI.Callback(self.var_CastInsetUse.setValue,1),
                            offCommand = mUI.Callback(self.var_CastInsetUse.setValue,0))	    
            self.uiFF_CastInsetMult = mUI.MelFloatField(_uiRow_slice,
                                                        w = 40,
                                                        annotation = 'Inset mult',
                                                        precision = 2,
                                                        value = self.var_CastInsetMult.value,
                                                        ec = lambda *a:self.valid_ff_CastInsetMult())

            _button_cast = cgmUI.add_Button(_uiRow_slice,"Wrap",
                                            mUI.Callback(self.cast_wrap))
            _uiRow_slice.setStretchWidget( _button_cast )	 	    

            mUI.MelSpacer(_uiRow_slice,w=2)		    
            _uiRow_slice.layout()    
        except Exception,err:
            log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))

        """
	self.create_guiOptionVar('CastExtendMode', defaultValue = 1)
	self.create_guiOptionVar('CastObjectUp', defaultValue = 1)

	self.create_guiOptionVar('CastInsetMult', defaultValue = '')
	#####self.create_guiOptionVar('CastXRootOffset', defaultValue = 0.0)
	#####self.create_guiOptionVar('CastYRootOffset', defaultValue = 0.0)
	#####self.create_guiOptionVar('CastZRootOffset', defaultValue = 0.0)	    
	#####self.create_guiOptionVar('CastJoin', defaultValue = 1)
	#####self.create_guiOptionVar('CastMidMeshCast', defaultValue = 0)
	#####self.create_guiOptionVar('CastRotateBank', defaultValue = 0.0)	
	"""    
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

            self.uiRow_ProxiExpandMode = mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)
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

            self.uiRow_ProxiResult = mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)
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

            self.uiRow_ProxiMode = mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)
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

            self.uiRow_Pivot = mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)
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
            mUI.MelLabel(self.uiRow_baseValues,l='Tol:',align='right')
            self.uiTF_tolerance = mUI.MelTextField(self.uiRow_baseValues,backgroundColor = [1,1,1],h=20,
                                                   ut = 'cgmUITemplate',
                                                   w = 50,
                                                   tx = self.var_Tolerance.value,
                                                   ec = lambda *a:self.valid_tf_tolerance(),
                                                   annotation = "Tolerance for symmetry calculation.")
            mUI.MelLabel(self.uiRow_baseValues,l='x:',align='right')
            self.uiTF_multiplier = mUI.MelTextField(self.uiRow_baseValues,backgroundColor = [1,1,1],h=20,
                                                    ut = 'cgmUITemplate',
                                                    w = 50,
                                                    tx = self.var_Multiplier.value,                                                    
                                                    ec = lambda *a:self.valid_tf_multiplier(),
                                                    annotation = "Multiplier for symmetry calculation.")
        
            self.uiRow_baseValues.setStretchWidget( mUI.MelSpacer(self.uiRow_baseValues) )
            mUI.MelLabel(self.uiRow_baseValues,l='sym:',align='right')
        
            self.uiRC_symAxis = mUI.MelRadioCollection()
            self.uiOptions_symAxis = []		
        
            for i,item in enumerate(self._l_symAxisOptions):
                self.uiOptions_symAxis.append(self.uiRC_symAxis.createButton(self.uiRow_baseValues,label=item,
                                                                             #ann = _l_ann[i],
                                                                             onCommand = mUI.Callback(self.var_AxisMode.setValue,i)))
        
            mc.radioCollection(self.uiRC_symAxis, edit=True, sl=self.uiOptions_symAxis[self.var_AxisMode.value])
        
            self.uiRow_baseValues.layout()                 

            #Result Mode Change row 
            self._l_resultOptions = ['New','Modify','Values']
            _l_ann = ['Create a new object',
                      'Modify the existing base',
                      'Just do the math']
            #self.create_guiOptionVar('ResultModeMode', defaultValue = 0)#Register the option var     

            self.uiRow_ResultMode = mUI.MelHSingleStretchLayout(containerName,ut='cgmUISubTemplate',padding = 1)
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
       


            try:#>>> Select
                _str_section = 'Base Select'
                
                mc.setParent(containerName)
                cgmUI.add_Header('Base Select')
    
                _help_baseSelect = mUI.MelLabel(containerName,
                                                bgc = dictionary.returnStateColor('help'),
                                                align = 'center',
                                                label = 'Select components on base from sym',
                                                h=20,
                                                vis = self.var_ShowHelp.value)	
    
                self.l_helpElements.append(_help_baseSelect)               
    
                self.uiRow_baseSelect = mUI.MelHLayout(containerName,padding = 1)
                cgmUI.add_Button(self.uiRow_baseSelect, 'Center', 
                                 lambda *a:self.baseObject_select('center'),
                                 annotationText='Select center line vertices')
                cgmUI.add_Button(self.uiRow_baseSelect, 'Pos', 
                                 lambda *a:self.baseObject_select('positive'),
                                 annotationText='Select positive vertices')
                cgmUI.add_Button(self.uiRow_baseSelect, 'Neg', 
                                 lambda *a:self.baseObject_select('negative'),
                                 annotationText='Select negative vertices')
                cgmUI.add_Button(self.uiRow_baseSelect, 'Asym', 
                                 lambda *a:self.baseObject_select('asymmetrical'),
                                 annotationText='Select asymmetrical vertices')
                self.uiRow_baseSelect.layout()
            except Exception,err:
                log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))
            
            try:#>>> Select
                _str_section = 'Target Select'       
                mc.setParent(containerName)
                cgmUI.add_LineBreak()                
                cgmUI.add_Header('Target Select')                
                self.uiRow_targetSelect = mUI.MelHLayout(containerName,padding = 1)
                cgmUI.add_Button(self.uiRow_targetSelect, 'Center', 
                                 lambda *a:self.tarObject_select('center'),
                                 annotationText='Select center line vertices')
                cgmUI.add_Button(self.uiRow_targetSelect, 'Pos', 
                                 lambda *a:self.tarObject_select('positive'),
                                 annotationText='Select positive vertices')
                cgmUI.add_Button(self.uiRow_targetSelect, 'Neg', 
                                 lambda *a:self.tarObject_select('negative'),
                                 annotationText='Select negative vertices')
                self.uiRow_targetSelect.layout()     
                
                mc.setParent(containerName)                
                self.uiRow_targetSelect2 = mUI.MelHLayout(containerName,padding = 1)
                cgmUI.add_Button(self.uiRow_targetSelect2, 'Check Sym', 
                                 lambda *a:self.tarObject_select('asymmetrical'),
                                 annotationText='Select asymmetrical vertices')
                cgmUI.add_Button(self.uiRow_targetSelect2, 'Select Mirror', 
                                 lambda *a:self.tarObject_selectMirrored(),
                                 annotationText='Select mirrored vertices of those selected')
                cgmUI.add_Button(self.uiRow_targetSelect2, 'Select Moved', 
                                 lambda *a:self.tarObject_select('moved'),
                                 annotationText='Select vertices that move')
                self.uiRow_targetSelect2.layout()                       
            except Exception,err:
                log.error("{0} {1} failed to load. err: {2}".format(self._str_reportStart,_str_section,err))
                
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
            self.uiRow_baseMath = mUI.MelHLayout(containerName,padding = 1)
            cgmUI.add_Button(self.uiRow_baseMath, 'Add', 
                             lambda *a:self.baseObject_meshMath('add'),
                             annotationText='Add pos data')
            cgmUI.add_Button(self.uiRow_baseMath, 'Subtract', 
                             lambda *a:self.baseObject_meshMath('subtract'),
                             annotationText='Subtract pos data')
            cgmUI.add_Button(self.uiRow_baseMath, 'Avg', 
                             lambda *a:self.baseObject_meshMath('average'),
                             annotationText='Average pos data')
            cgmUI.add_Button(self.uiRow_baseMath, 'Reset', 
                             lambda *a:self.baseObject_meshMath('reset'),
                             annotationText='Reset target to base')            
            self.uiRow_baseMath.layout() 

            #>>> Diff...
            self.uiRow_baseDiff = mUI.MelHLayout(containerName,padding = 1)
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
            self.uiRow_baseBlend = mUI.MelHLayout(containerName,padding = 1)
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
            self.uiSlider_baseBlend = mUI.MelFloatSlider(uiRow_blend,-1.2,1.2,0,step = .2)
            self.uiSlider_baseBlend.setPostChangeCB(mUI.Callback(self.baseObject_blendSlider))
            cgmUI.add_Button(uiRow_blend,'R',
                             mUI.Callback(self.uiSlider_baseBlend.reset,False),
                             'Reset this slider')
            mUI.MelSpacer(uiRow_blend,w=5)	            
            uiRow_blend.setStretchWidget(self.uiSlider_baseBlend)#Set stretch            

            #>>> Sym...
            self.uiRow_baseSym = mUI.MelHLayout(containerName,padding = 1)
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
            self.uiRow_targetsMath = mUI.MelHLayout(containerName,padding = 1)
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
            cgmUI.add_Button(self.uiRow_targetsMath, 'CopyTo', 
                             lambda *a:self.targets_meshMath('copyTo'),
                             annotationText='Copy vert data from one to another')             
            self.uiRow_targetsMath.layout()   

            #>>> Diff...
            self.uiRow_targetDiff = mUI.MelHLayout(containerName,padding = 1)
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
            self.uiRow_targetBlend = mUI.MelHLayout(containerName,padding = 1)
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
            self.uiSlider_targetsBlend = mUI.MelFloatSlider(uiRow_blendTargets,-1.2,1.2,0,step = .2)
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
            self.var_Multiplier.value = ''
        self.uiTF_multiplier.setValue(self.var_Multiplier.value)

    def valid_tf_clickClamp(self):
        try:
            _buffer = self.uiTF_ClickClamp.getValue()
            self.var_ClickClamp.value = _buffer
            if self.var_ClickClamp.value == _buffer:
                self.uiTF_ClickClamp.setValue(_buffer)
            else:self.uiTF_ClickClamp.setValue(self.var_ClickClamp.value)	    

        except Exception,err:
            log.error("{0} valid_tf_clickClamp failed! err: {1}".format(self._str_reportStart,err))

    def valid_intf_castPoints(self):
        try:
            _buffer = self.uiIF_CastPoints.getValue()
            if _buffer < 6:
                _buffer = 6
            self.var_CastPoints.value = _buffer
            if self.var_CastPoints.value == _buffer:
                self.uiIF_CastPoints.setValue(_buffer)
            else:self.uiIF_CastPoints.setValue(self.var_CastPoints.value)	    

        except Exception,err:
            log.error("{0} valid_intf_castPoints failed! err: {1}".format(self._str_reportStart,err))

    def valid_intf_castDegree(self):
        try:
            _buffer = self.uiIF_CastDegree.getValue()
            if _buffer < 1:
                _buffer = 1
            self.var_CastDegree.value = _buffer
            if self.var_CastDegree.value == _buffer:
                self.uiIF_CastDegree.setValue(_buffer)
            else:self.uiIF_CastDegree.setValue(self.var_CastDegree.value)	    

        except Exception,err:
            log.error("{0} valid_intf_castDegree failed! err: {1}".format(self._str_reportStart,err))   

    def valid_ff_CastXOffset(self):
        try:
            _buffer = self.uiFF_CastXOffset.getValue()
            self.var_CastXOffset.value = _buffer
            if self.var_CastXOffset.value == _buffer:
                self.uiFF_CastXOffset.setValue(_buffer)
            else:self.uiFF_CastXOffset.setValue(self.var_CastXOffset.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastXOffset failed! err: {1}".format(self._str_reportStart,err))  


    def valid_ff_CastXRootOffset(self):
        try:
            _buffer = self.uiFF_CastXRoot.getValue()
            self.var_CastXRootOffset.value = _buffer
            if self.var_CastXRootOffset.value == _buffer:
                self.uiFF_CastXRoot.setValue(_buffer)
            else:self.uiFF_CastXRoot.setValue(self.var_CastXRootOffset.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastXRootOffset failed! err: {1}".format(self._str_reportStart,err)) 
    def valid_ff_CastYRootOffset(self):
        try:
            _buffer = self.uiFF_CastYRoot.getValue()
            self.var_CastYRootOffset.value = _buffer
            if self.var_CastYRootOffset.value == _buffer:
                self.uiFF_CastYRoot.setValue(_buffer)
            else:self.uiFF_CastYRoot.setValue(self.var_CastYRootOffset.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastYRootOffset failed! err: {1}".format(self._str_reportStart,err)) 
    def valid_ff_CastZRootOffset(self):
        try:
            _buffer = self.uiFF_CastZRoot.getValue()
            self.var_CastZRootOffset.value = _buffer
            if self.var_CastZRootOffset.value == _buffer:
                self.uiFF_CastZRoot.setValue(_buffer)
            else:self.uiFF_CastZRoot.setValue(self.var_CastZRootOffset.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastZRootOffset failed! err: {1}".format(self._str_reportStart,err)) 

    def valid_ff_CastXOffset(self):
        try:
            _buffer = self.uiFF_CastXOffset.getValue()
            self.var_CastXOffset.value = _buffer
            if self.var_CastXOffset.value == _buffer:
                self.uiFF_CastXOffset.setValue(_buffer)
            else:self.uiFF_CastXOffset.setValue(self.var_CastXOffset.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastXOffset failed! err: {1}".format(self._str_reportStart,err))  
    def valid_ff_CastYOffset(self):
        try:
            _buffer = self.uiFF_CastYOffset.getValue()
            self.var_CastYOffset.value = _buffer
            if self.var_CastYOffset.value == _buffer:
                self.uiFF_CastYOffset.setValue(_buffer)
            else:self.uiFF_CastYOffset.setValue(self.var_CastYOffset.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastYOffset failed! err: {1}".format(self._str_reportStart,err))  	    
    def valid_ff_CastZOffset(self):
        try:
            _buffer = self.uiFF_CastZOffset.getValue()
            self.var_CastZOffset.value = _buffer
            if self.var_CastZOffset.value == _buffer:
                self.uiFF_CastZOffset.setValue(_buffer)
            else:self.uiFF_CastZOffset.setValue(self.var_CastZOffset.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastZOffset failed! err: {1}".format(self._str_reportStart,err)) 

    def valid_ff_CastInsetMult(self):
        try:
            _buffer = self.uiFF_CastInsetMult.getValue()
            self.var_CastInsetMult.value = _buffer
            if self.var_CastInsetMult.value == _buffer:
                self.uiFF_CastInsetMult.setValue(_buffer)
            else:self.uiFF_CastInsetMult.setValue(self.var_CastInsetMult.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastInsetMult failed! err: {1}".format(self._str_reportStart,err))

    def valid_ff_CastMinRotate(self):
        try:
            _buffer = self.uiFF_CastMinRotate.getValue()
            self.var_CastMinRotate.value = _buffer
            if self.var_CastMinRotate.value == _buffer:
                self.uiFF_CastMinRotate.setValue(_buffer)
            else:self.uiFF_CastMinRotate.setValue(self.var_CastMinRotate.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastMinRotate failed! err: {1}".format(self._str_reportStart,err))  

    def valid_ff_CastMaxRotate(self):
        try:
            _buffer = self.uiFF_CastMaxRotate.getValue()
            self.var_CastMaxRotate.value = _buffer
            if self.var_CastMaxRotate.value == _buffer:
                self.uiFF_CastMaxRotate.setValue(_buffer)
            else:self.uiFF_CastMaxRotate.setValue(self.var_CastMaxRotate.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastMaxRotate failed! err: {1}".format(self._str_reportStart,err))  

    def valid_ff_CastRange(self):
        try:
            _buffer = self.uiFF_CastRange.getValue()
            self.var_CastRange.value = _buffer
            if self.var_CastRange.value == _buffer:
                self.uiFF_CastRange.setValue(_buffer)
            else:self.uiFF_CastRange.setValue(self.var_CastRange.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastMaxRotate failed! err: {1}".format(self._str_reportStart,err)) 

    def valid_ff_CastRotateBank(self):
        try:
            _buffer = self.uiFF_CastRotateBank.getValue()
            self.var_CastRotateBank.value = _buffer
            if self.var_CastRotateBank.value == _buffer:
                self.uiFF_CastRotateBank.setValue(_buffer)
            else:self.uiFF_CastRotateBank.setValue(self.var_CastRotateBank.value)	    
        except Exception,err:
            log.error("{0} valid_ff_CastRotateBank failed! err: {1}".format(self._str_reportStart,err))     

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
        _sel = self.selectCheck()
        _objs = selUtils.get_filtered('transform')        
        _d = self.get_FunctionOptions()        
        _ml_objs = cgmMeta.validateObjListArg(_objs,'cgmObject',mayaType='mesh')
        if not _ml_objs:
            log.error("{0}: No selected objects.".format(self._str_reportStart))                
            return False
        if multiplier is None:
            _multiplier = _d['multiplier']
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
        _sel = self.selectCheck()
        _ml_objs = cgmMeta.validateObjListArg(_sel,'cgmObject',mayaType=['mesh'])

        if not _ml_objs:
            log.error("{0}: No selected objects.".format(self._str_reportStart))                
            return False

        if len(_ml_objs) < 2:
            log.error("{0}: Must have at least two objects.".format(self._str_reportStart))                
            return False

        _base = _ml_objs[0]

        try:
            log.info(GEO.get_proximityGeo(_base.mNode,[mObj.mNode for mObj in _ml_objs[1:]],
                                          self.var_ProxiMode.value, returnMode= self.var_ProxiResult.value,
                                          expandBy=self.var_ProxiExpand.value, expandAmount=self.var_ProxiAmount.value)) 
        except Exception,err:
            log.error("{0}: create_proximityMeshFromTarget() fail. | err:{1}".format(self._str_reportStart,err))                


    def uiList_updateCastTargets(self):
        try:
            self.uiList_Targets.clear()
            self._l_castItems = []

            _d = {}
            for mObj in self._ml_castTargets:
                _d[mObj.mNode] = mObj    
            _keys = _d.keys()
            _keys.sort()
            self._ml_castTargets = [_d[k] for k in _keys]


            for mObj in self._ml_castTargets:
                #self.uiList_Targets.append(item)
                _str = " {1} -- {0}".format(mObj.getMayaType(),mObj.p_nameBase)
                self.uiList_Targets.append(_str)
                self._l_castItems.append(_str)                
                #self.uiList_Targets.append("{0} {1}".format( mObj.getMayaType(),mObj.mNode))
                #presets_SetActive
                popUpMenu = mUI.MelPopupMenu(self.uiList_Targets,button = 3)	
                mUI.MelMenuItem(popUpMenu ,
                                label = 'Select',
                                annotation = 'Select the indicated targets',
                                c = lambda *a: self.castTargets_select())
                mUI.MelMenuItem(popUpMenu ,
                                label = "Remove selected",
                                annotation = 'Remove the indicated objects as targets',                                
                                c = lambda *a: self.castTargets_remove())
                mUI.MelMenuItem(popUpMenu ,
                                label = "Remove nonselected",
                                annotation = 'Remove the non-indicated objects as targets',                                                                
                                c = lambda *a: self.castTargets_removeNonselected())                
        except Exception,err:
            raise Exception,"{0} uiList_updateCastTargets failed | {1}".format(self._str_reportStart,err)

    def baseObject_blendSlider(self):
        _multiplier = self.uiSlider_baseBlend(q=True, value=True)
        self.baseObject_meshMath('blend',_multiplier)

    def targets_blendSlider(self):
        _multiplier = self.uiSlider_targetsBlend(q=True, value=True)
        self.targets_meshMath('blend',_multiplier)

    def castTargets_add(self,l):
        _ml_objs = cgmMeta.validateObjListArg(l,'cgmObject',mayaType=['mesh','nurbsSurface'])

        for mObj in _ml_objs:
            if mObj not in self._ml_castTargets:
                self._ml_castTargets.append(mObj)

        self.uiList_updateCastTargets()

    def castTargets_remove(self):
        selected = self.uiList_Targets.getSelectedItems()
        if not selected:
            log.warning("None selected")
            return False    
        _ml = []
        for s in selected:
            idx = self._l_castItems.index(s)
            _ml.append( self._ml_castTargets[idx])

        for mObj in _ml:
            self._ml_castTargets.remove(mObj)

        self.uiList_updateCastTargets()

    def castTargets_removeNonselected(self):
        selected = self.uiList_Targets.getSelectedItems()
        if not selected:
            log.warning("None selected")
            return False    
        _ml = []
        _ml_remove = []
        for s in selected:
            idx = self._l_castItems.index(s)
            _ml.append( self._ml_castTargets[idx])



        for mObj in self._ml_castTargets:
            if mObj not in _ml:
                _ml_remove.append(mObj)

        for mObj in _ml_remove:
            self._ml_castTargets.remove(mObj)

        self.uiList_updateCastTargets()   

    def selectCheck(self, transforms = False):
        _sel = mc.ls(sl=1)
        if not _sel:
            self.var_SelectBuffer.select()
            _sel = mc.ls(sl=1)
        if _sel:self.var_SelectBuffer.value = _sel
        return _sel

    def castTargets_select(self):
        selected = self.uiList_Targets.getSelectedItems()
        if not selected:
            log.warning("None selected")
            return False    
        _ml = []
        for s in selected:
            idx = self._l_castItems.index(s)
            _ml.append( self._ml_castTargets[idx])

        mc.select([mObj.mNode for mObj in _ml])

        #self.uiList_updateCastTargets()

    def castTargets_loadSelected(self):
        _sel = mc.ls(sl=True)
        self.castTargets_add(_sel)

    def castTargets_clearAll(self):
        self._ml_castTargets = []
        self.uiList_updateCastTargets()

    def castTargets_loadAll(self):
        _l_objs = []
        for l in mc.ls(type='mesh',visible = True), mc.ls(type='nurbsSurface',visible = True):
            for o in l:
                _l_objs.append( cgmMeta.getTransform(o))

        self.castTargets_add(_l_objs)

    def cast_slice(self):
        log.info("cast_slice...")	

        _sel = self.selectCheck()
        _ml_objs = cgmMeta.validateObjListArg(_sel,'cgmObject')
        for mObj in _ml_objs:
            for mObj2 in self._ml_castTargets:
                if mObj.mNode == mObj2.mNode:
                    _ml_objs.remove(mObj)

        if not _ml_objs:
            log.error("{0}: No selected objects.".format(self._str_reportStart))                
            return False	


        if not self._ml_castTargets:
            _l_objs = []
            for l in mc.ls(type='mesh',visible = True), mc.ls(type='nurbsSurface',visible = True):
                for o in l:
                    _l_objs.append( cgmMeta.getTransform(o))
            meshClamp = 100
            if len(_l_objs)<=meshClamp:
                _l_mesh = _l_objs #Still not sure if we wanna do all scene meshes. Need more testing.
            else: 
                raise ValueError("No mesh loaded or too many mesh objects for autoload")
        else: _l_mesh = [mObj.mNode for mObj in self._ml_castTargets]

        _latheAxis = self._l_latheAxisOptions[self.var_CastLatheAxis.value]
        _aimAxis = self._l_aimAxisOptions[self.var_CastAimAxis.value]

        _min = None
        if self.var_CastMinUse.value:
            _min = self.var_CastMinRotate.value
        _max = None
        if self.var_CastMaxUse.value:
            _max = self.var_CastMaxRotate.value

        log.info("Casting Objects: {0}".format([mObj.mNode for mObj in _ml_objs]))	
        log.info("Lathe Axis: {0}".format(_latheAxis))
        log.info("Aim Axis: {0}".format(_aimAxis))
        log.info("Degree: {0}".format(self.var_CastDegree.value))	
        log.info("Points: {0}".format(self.var_CastPoints.value))
        log.info("xOffset: {0}".format(self.var_CastXOffset.value))
        log.info("yOffset: {0}".format(self.var_CastYOffset.value))
        log.info("zOffset: {0}".format(self.var_CastZOffset.value))	
        log.info("MarkHits: {0}".format(self.var_CastMarkHits.value))
        log.info("ClosedCurve: {0}".format(self.var_CastClosedCurve.value))
        log.info("CastClosestInRange: {0}".format(self.var_CastClosestInRange.value))	
        log.info("minRotate: {0}".format(_min))
        log.info("maxRotate: {0}".format(_max))
        log.info("Range: {0}".format(self.var_CastRange.value))

        log.info("Targets: {0}".format(len(_l_mesh)))	
        for mObj in _ml_objs:
            log.info( ShapeCaster.createMeshSliceCurve(_l_mesh, mObj,
                                                       latheAxis=_latheAxis, aimAxis=_aimAxis, 
                                                       points=self.var_CastPoints.value, 
                                                       curveDegree=self.var_CastDegree.value, 
                                                       minRotate=_min, 
                                                       maxRotate=_max, 
                                                       rotateRange=None, 
                                                       posOffset=[self.var_CastXOffset.value,self.var_CastYOffset.value,self.var_CastZOffset.value], 
                                                       markHits=self.var_CastMarkHits.value, 
                                                       #rotateBank=None, 
                                                       closedCurve=self.var_CastClosedCurve.value, 
                                                       maxDistance=self.var_CastRange.value, 
                                                       initialRotate=0, 
                                                       offsetMode='vector', 
                                                       midMeshCast=False, 
                                                       l_specifiedRotates=None, 
                                                       closestInRange=self.var_CastClosestInRange.value, 
                                                       returnDict=False,))

        mc.select([mObj.mNode for mObj in _ml_objs])

    def cast_wrap(self):
        log.info("cast_wrap...")	

        _sel = self.selectCheck()

        _ml_objs = cgmMeta.validateObjListArg(_sel,'cgmObject')
        for mObj in _ml_objs:
            for mObj2 in self._ml_castTargets:
                if mObj.mNode == mObj2.mNode:
                    _ml_objs.remove(mObj)

        if not _ml_objs:
            log.error("{0}: No selected objects.".format(self._str_reportStart))                
            return False	


        if not self._ml_castTargets:
            _l_objs = []
            for l in mc.ls(type='mesh',visible = True), mc.ls(type='nurbsSurface',visible = True):
                for o in l:
                    _l_objs.append( cgmMeta.getTransform(o))
            meshClamp = 100
            if len(_l_objs)<=meshClamp:
                _l_mesh = _l_objs #Still not sure if we wanna do all scene meshes. Need more testing.
            else: 
                raise ValueError("No mesh loaded or too many mesh objects for autoload")
        else: _l_mesh = [mObj.mNode for mObj in self._ml_castTargets]

        _latheAxis = self._l_latheAxisOptions[self.var_CastLatheAxis.value]
        _aimAxis = self._l_aimAxisOptions[self.var_CastAimAxis.value]

        _objectUp = self._l_aimAxisOptions[self.var_CastObjectUp.value]
        _extendMode = self._l_extendMode[self.var_CastExtendMode.value]
        if _extendMode == 'NONE':
            _extendMode = None
        _min = None
        if self.var_CastMinUse.value:
            _min = self.var_CastMinRotate.value
        _max = None
        if self.var_CastMaxUse.value:
            _max = self.var_CastMaxRotate.value

        _insetMult = None
        if self.var_CastInsetUse.value:
            _insetMult = self.var_CastInsetMult.value	    

        log.info("Casting Objects: {0}".format([mObj.mNode for mObj in _ml_objs]))	
        log.info("Lathe Axis: {0}".format(_latheAxis))
        log.info("Aim Axis: {0}".format(_aimAxis))
        log.info("Inset: {0}".format(_insetMult))	
        log.info("Degree: {0}".format(self.var_CastDegree.value))	
        log.info("Points: {0}".format(self.var_CastPoints.value))
        log.info("xOffset: {0}".format(self.var_CastXOffset.value))
        log.info("yOffset: {0}".format(self.var_CastYOffset.value))
        log.info("zOffset: {0}".format(self.var_CastZOffset.value))
        log.info("xRootOffset: {0}".format(self.var_CastXRootOffset.value))
        log.info("yRootOffset: {0}".format(self.var_CastYRootOffset.value))
        log.info("zRootOffset: {0}".format(self.var_CastZRootOffset.value))	
        log.info("ClosedCurve: {0}".format(self.var_CastClosedCurve.value))
        log.info("CastClosestInRange: {0}".format(self.var_CastClosestInRange.value))	
        log.info("minRotate: {0}".format(_min))
        log.info("maxRotate: {0}".format(_max))
        log.info("Range: {0}".format(self.var_CastRange.value))
        log.info("CastJoin: {0}".format(self.var_CastJoin.value))
        log.info("ExtendMode: {0}".format(_extendMode))
        log.info("ObjectUp: {0}".format(_objectUp))
        log.info("MidCast: {0}".format(self.var_CastMidMeshCast.value))
        log.info("Bank: {0}".format(self.var_CastRotateBank.value))

        log.info("Targets: {0}".format(len(_l_mesh)))	
        _ml_pairs = lists.returnListChunks(_ml_objs,2)

        if _extendMode in ['segment']:
            if len(_ml_objs) == 1:
                raise ValueError,"Must have two objects selected for segment casting"
            log.info(_ml_pairs)
            _ml_pairs = lists.parseListToPairs(_ml_objs)
            for p in _ml_pairs:
                log.info(ShapeCaster.createWrapControlShape([mObj.mNode for mObj in p], 
                                                            targetGeo=_l_mesh, 
                                                            latheAxis=_latheAxis, 
                                                            aimAxis=_aimAxis, 
                                                            objectUp=_objectUp, 
                                                            points=self.var_CastPoints.value, 
                                                            curveDegree=self.var_CastDegree.value, 
                                                            insetMult=_insetMult, 
                                                            posOffset=[self.var_CastXOffset.value,self.var_CastYOffset.value,self.var_CastZOffset.value], 
                                                            rootOffset=[self.var_CastXRootOffset.value,self.var_CastYRootOffset.value,self.var_CastZRootOffset.value], 
                                                            rootRotate=None, 
                                                            joinMode=self.var_CastJoin.value, 
                                                            extendMode=_extendMode, 
                                                            closedCurve=self.var_CastClosedCurve.value, 
                                                            l_specifiedRotates=None, 
                                                            maxDistance=self.var_CastRange.value, 
                                                            closestInRange=self.var_CastClosestInRange.value, 
                                                            midMeshCast=self.var_CastMidMeshCast.value, 
                                                            rotateBank=self.var_CastRotateBank.value, 
                                                            joinHits=None, 
                                                            axisToCheck=['x', 
                                                                         'y']))		
        else:
            for mObj in _ml_objs:
                log.info(ShapeCaster.createWrapControlShape(mObj.mNode, 
                                                            targetGeo=_l_mesh, 
                                                            latheAxis=_latheAxis, 
                                                            aimAxis=_aimAxis, 
                                                            objectUp=_objectUp, 
                                                            points=self.var_CastPoints.value, 
                                                            curveDegree=self.var_CastDegree.value, 
                                                            insetMult=_insetMult, 
                                                            posOffset=[self.var_CastXOffset.value,self.var_CastYOffset.value,self.var_CastZOffset.value], 
                                                            rootOffset=[self.var_CastXRootOffset.value,self.var_CastYRootOffset.value,self.var_CastZRootOffset.value], 
                                                            rootRotate=None, 
                                                            joinMode=self.var_CastJoin.value, 
                                                            extendMode=_extendMode, 
                                                            closedCurve=self.var_CastClosedCurve.value, 
                                                            l_specifiedRotates=None, 
                                                            maxDistance=self.var_CastRange.value, 
                                                            closestInRange=self.var_CastClosestInRange.value, 
                                                            midMeshCast=self.var_CastMidMeshCast.value, 
                                                            rotateBank=self.var_CastRotateBank.value, 
                                                            joinHits=None, 
                                                            axisToCheck=['x', 
                                                                         'y']))

        mc.select([mObj.mNode for mObj in _ml_objs])

    def clickMesh_start(self):
        log.info("clickMesh_start...")	
        self.clickMesh_drop()

        if not self._ml_castTargets:
            _l_objs = []
            for l in mc.ls(type='mesh',visible = True), mc.ls(type='nurbsSurface',visible = True):
                for o in l:
                    _l_objs.append( cgmMeta.getTransform(o))
            meshClamp = 100
            if len(_l_objs)<=meshClamp:
                _l_mesh = _l_objs #Still not sure if we wanna do all scene meshes. Need more testing.
            else: 
                raise ValueError("No mesh loaded or too many mesh objects for autoload")
        else: _l_mesh = [mObj.mNode for mObj in self._ml_castTargets]

        log.info("Mode: {0}".format(self.var_ClickMode.value))
        log.info("Drag: {0}".format(self.var_ClickDrag.value))
        log.info("Clamp: {0}".format(self.var_ClickClamp.value))
        log.info("Create: {0}".format(self.var_ClickCreate.value))
        log.info("Targets: {0}".format(len(_l_mesh)))		

        self.tool_clickMesh = DraggerContextFactory.clickMesh( mesh = _l_mesh,
                                                               closestOnly = True,
                                                               dragStore=False,
                                                               clampIntersections = self.var_ClickClamp.value)

        log.info("Resolved Mode: {0}".format(self.tool_clickMesh._l_modes[self.var_ClickMode.value]))
        log.info("Resolved Create: {0}".format(self.tool_clickMesh._createModes[self.var_ClickCreate.value]))

        self.tool_clickMesh.setMode(self.tool_clickMesh._l_modes[self.var_ClickMode.value])
        self.tool_clickMesh.setCreate(self.tool_clickMesh._createModes[self.var_ClickCreate.value])  
        self.tool_clickMesh.setDragStoreMode(self.var_ClickDrag.value)

        log.warning("clickMesh_start >>> ClickMesh initialized") 
        
    def clickMesh_snap(self):
        log.info("clickMesh_snap...")	
        self.clickMesh_drop()
        _l_mesh = []
        if not self._ml_castTargets:
            _l_objs = []
            for l in mc.ls(type='mesh',visible = True), mc.ls(type='nurbsSurface',visible = True):
                for o in l:
                    _l_objs.append( cgmMeta.getTransform(o))
            meshClamp = 100
            if len(_l_objs)<=meshClamp:
                _l_mesh = _l_objs #Still not sure if we wanna do all scene meshes. Need more testing.
            else: 
                raise ValueError("No mesh loaded or too many mesh objects for autoload")
        else: _l_mesh = [mObj.mNode for mObj in self._ml_castTargets]
        
        _toSnap = mc.ls(sl=True) or []
        log.info("clickMesh_snap | targets: {0}".format(_toSnap))
        if not _toSnap:
            raise ValueError,"clickMesh_snap >> Must have targets!"
        DraggerContextFactory.clickMesh( mode = self.var_ClickMode.value,
                                         mesh = _l_mesh,
                                         closestOnly = True,
                                         create = 'locator',
                                         dragStore = False,
                                         toSnap = _toSnap,
                                         )
    
        log.warning("clickMesh_snap >>> ClickMesh initialized")         
        
    def clickMesh_drop(self):
        if self.tool_clickMesh:
            self.tool_clickMesh.finalize()
            self.tool_clickMesh.dropTool()
            self.tool_clickMesh = False    

    def baseObject_meshMath(self,mode = None, multiplier = None):
        _sel = self.selectCheck()
        _objs = selUtils.get_filtered('transform')
        _d = self.get_FunctionOptions()        
        _ml_objs = cgmMeta.validateObjListArg(_objs,'cgmObject',mayaType='mesh')
        if self._mi_baseObject in _ml_objs:
            _ml_objs.remove(self._mi_baseObject)
        if not _ml_objs:
            log.error("{0}: No selected objects.".format(self._str_reportStart))                
            return False
        if multiplier is None:
            _multiplier = _d['multiplier']
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
                                      softSelectMultiply=True,
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
            _report = ["asymmetrical: {0}".format( len(_d_baseSym['asymmetrical']))]     

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
        elif mode == 'asymmetrical':
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
        _d = self.get_FunctionOptions()        
        _sel = mc.ls(sl=True)
        _l_trans = [cgmMeta.getTransform(o) for o in _sel]
        _l_trans = lists.returnListNoDuplicates(_l_trans)
        _ml_objs = cgmMeta.validateObjListArg(_l_trans,'cgmObject',mayaType='mesh')
        if not _ml_objs:
            log.error("{0}: No selected objects.".format(self._str_reportStart))                
            return False
        _buffer = []
        if mode == 'center':
            _buffer =  self._d_baseSym['center']
        elif mode == 'positive':
            _buffer = self._d_baseSym['positive']
        elif mode == 'negative':
            _buffer = self._d_baseSym['negative']
        elif mode == 'moved':
            _d = self.get_FunctionOptions()
            for mObj in _ml_objs:
                _res = GEO.meshMath([mObj.mNode,
                                     self._mi_baseObject.mNode],
                                    'difference',
                                    space = _d['space'],
                                    center =_d['pivot'], 
                                    axis=_d['axis'], 
                                    tolerance= _d['tolerance'], 
                                    resultMode= 'values',
                                    symDict=self._d_baseSym)
                for i,pos in enumerate(_res):
                    if abs(sum(pos)):
                        _buffer.append("{0}.vtx[{1}]".format(mObj.mNode,i))
        elif mode == 'asymmetrical':
            for mObj in _ml_objs:
                _d_targetSym = GEO.get_symmetryDict(mObj.mNode,
                                                    center=_d['pivot'], 
                                                    axis=_d['axis'], 
                                                    tolerance= _d['tolerance'], 
                                                    returnMode = 'names')             
                _asymm = _d_targetSym.get('asymmetrical',[])
                if not _asymm:
                    log.warning("{0}: no asymmetrical verts found on '{1}'.".format(self._str_reportStart,mObj.mNode))
                else:
                    log.warning("{0}:  {2} asymmetrical verts found on '{1}'.".format(self._str_reportStart,mObj.mNode,len(_asymm)))                    
                    _buffer.extend(_asymm)

        
        _sel =[]
        if mode in ['asymmetrical','moved']:
            if _buffer:
                _sel = _buffer
        else:
            if _buffer:
                for mObj in _ml_objs:
                    _obj = mObj.mNode            
                    for i in _buffer:
                        _sel.append("{0}.vtx[{1}]".format(_obj,i))
        mc.select(_sel) 
        
    def tarObject_selectMirrored(self):
        if not self._d_baseSym:
            log.error("{0}: nobase sym dict.".format(self._str_reportStart))
            return False   
        
        _sel = mc.ls(sl=True, flatten = True)
        _l_trans = []
        _tar = []
        for o in _sel:
            if '[' in o:
                _l_trans.append(cgmMeta.getTransform(o))                
                c = int(o.split('[')[-1].split(']')[0])
                _tar.append(c)
        _l_trans = lists.returnListNoDuplicates(_l_trans)
        if not _tar:
            log.error("{0}: No components selected.".format(self._str_reportStart))                
            return False            
        _symMap = self._d_baseSym['symMap']  
        _selSym = []
        for t in _l_trans:
            for c in _tar:
                _cM = _symMap.get(c)
                _selSym.append("{0}.vtx[{1}]".format(t,_cM[0]))
        mc.select(_selSym)       
        
        

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


