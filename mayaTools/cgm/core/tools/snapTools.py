"""
------------------------------------------
snapTools: cgm.core.tools
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
log.setLevel(logging.INFO)

import maya.cmds as mc

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

from cgm.core.lib import shared_data as SHARED
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
import cgm.core.lib.transform_utils as TRANS
from cgm.core.cgmPy import path_Utils as CGMPATH
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
import cgm.core.lib.rayCaster as RAYS
from cgm.core.lib import name_utils as NAMES
from cgm.core.lib import distance_utils as DIST
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.math_utils as COREMATH
import cgm.core.lib.position_utils as POS
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.locinator as LOCINATOR
import cgm.core.lib.arrange_utils as ARRANGE
import cgm.core.tools.lib.snap_calls as SNAPCALLS
from cgm.core.lib import snap_utils as SNAP
from cgm.core.tools.lib import tool_chunks as UICHUNKS
#reload(SNAPCALLS)
#reload(RAYS)
#reload(UICHUNKS)

#>>> Root settings =============================================================
__version__ = 'Alpha - 0.11282017'
__toolname__ ='cgmSnap'

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
        self.uiMenu_Buffers = mUI.MelMenu( l='Buffers', pmc = lambda *a:UICHUNKS.uiOptionMenu_buffers(self,False))
        self.uiMenu_Help = mUI.MelMenu(l = 'Help', pmc = lambda *a:self.buildMenu_help())

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     

        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        
    def buildMenu_help(self):
        self.uiMenu_Help.clear()
        
        cgmUI.uiSection_help(self.uiMenu_Help)
        
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        #self._d_uiCheckBoxes = {}
    
        #_MainForm = mUI.MelFormLayout(parent,ut='cgmUISubTemplate')
        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        _column = buildColumn_main(self,_MainForm,True)

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
        
def uiQuery_advancedSnap(self):
    _res = {}
    
    _res['sl'] = mc.ls(sl=True)
    _res['objPivot'] = self.uiSelector_objPivot.getValue()
    _res['objMode'] = self.uiSelector_objMode.getValue()
    _res['targetPivot'] = self.uiSelector_targetPivot.getValue()
    _res['targetMode'] = self.uiSelector_targetMode.getValue()
    
    _l_order = ['position','rotation','rotateAxis','rotateOrder','scalePivot','rotatePivot']
    for k in _l_order:
        _plug = 'cgmVar_snapAdvanced_' + k
        _res[k] = cgmMeta.cgmOptionVar(_plug).getValue()
    
    #pprint.pprint(_res)
    return _res

def buildSection_advancedSnap(self,parent):
    log.debug("buildSection_advancedSnap...")
    try:self.var_advancedSnapFrameCollapse
    except:self.create_guiOptionVar('advancedSnapFrameCollapse',defaultValue = 0)
    
    _frame = mUI.MelFrameLayout(parent,label = 'Advanced Snap',vis=True,
                                collapse=self.var_advancedSnapFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_advancedSnapFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_advancedSnapFrameCollapse.setValue(1)
                                )
    
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    #>>>Settings -------------------------------------------------------------------------------------
    _l_pivotArgs = ['rp','sp','closestPoint','boundingBox','axisBox','groundPos','castCenter','castFar','castNear','castAllFar','castAllNear']
    _l_pivotModes = ['center'] + [v for v in SHARED._l_axis_by_string]
    
    #Object Pivot ----------------------------------------------------------------------------------
    _plug = 'cgmVar_snapAdvanced_' + 'objectPivot'
    try:self.__dict__[_plug]
    except:
        _default = 'rp'
        log.debug("{0}:{1}".format(_plug,_default))
        self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = _default)


    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row,w=10)    
    mUI.MelLabel(_row, label = 'Obj Piv:')
    #cc = Callback(puppetBoxLib.uiModuleOptionMenuSet,self,self.moduleDirectionMenus,self.moduleDirections,'cgmDirection',i)
    self.uiSelector_objPivot = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
    for a in _l_pivotArgs:
        self.uiSelector_objPivot.append(a)
        
    self.uiSelector_objPivot(edit=True,
                             value = self.__dict__[_plug].getValue(),
                             cc = cgmGEN.Callback(self.set_optionVar, self.__dict__[_plug], None, self.uiSelector_objPivot))

    #Object Mode----------------------------------------------------------------------------------
    _plug = 'cgmVar_snapAdvanced_' + 'objectMode'
    try:self.__dict__[_plug]
    except:
        _default = 'center'
        log.debug("{0}:{1}".format(_plug,_default))
        self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = _default)
            
    mUI.MelLabel(_row, label = 'Mode:')
    self.uiSelector_objMode = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
    for a in _l_pivotModes:
        self.uiSelector_objMode.append(a)
    self.uiSelector_objMode(edit=True,
                             value = self.__dict__[_plug].getValue(),
                             cc = cgmGEN.Callback(self.set_optionVar, self.__dict__[_plug], None, self.uiSelector_objMode))

        
    _row.setStretchWidget(mUI.MelSeparator(_row))

    mc.button(parent=_row,
              l = 'loc',
              ut = 'cgmUITemplate',                                    
              c= lambda *a:uiFunc_createLoc(self,True),
              ann = "Create a special loc at the object")
    mUI.MelSpacer(_row,w=10)
    _row.layout()
    
    #Object Pivot ----------------------------------------------------------------------------------
    _plug = 'cgmVar_snapAdvanced_' + 'targetPivot'
    try:self.__dict__[_plug]
    except:
        _default = 'rp'
        log.debug("{0}:{1}".format(_plug,_default))
        self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = _default)
    
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row,w=10)

    mUI.MelLabel(_row, label = 'Tar Piv:')
    self.uiSelector_targetPivot = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
    for a in _l_pivotArgs:
        self.uiSelector_targetPivot.append(a)
    self.uiSelector_targetPivot(edit=True,
                             value = self.__dict__[_plug].getValue(),
                             cc = cgmGEN.Callback(self.set_optionVar, self.__dict__[_plug], None, self.uiSelector_targetPivot))

        
    #Object Pivot ----------------------------------------------------------------------------------
    _plug = 'cgmVar_snapAdvanced_' + 'targetMode'
    try:self.__dict__[_plug]
    except:
        _default = 'center'
        log.debug("{0}:{1}".format(_plug,_default))
        self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = _default)
        
    mUI.MelLabel(_row, label = 'Mode:')
    self.uiSelector_targetMode = mUI.MelOptionMenu(_row,useTemplate = 'cgmUITemplate')
    for a in _l_pivotModes:
        self.uiSelector_targetMode.append(a)
        
    self.uiSelector_targetMode(edit=True,
                             value = self.__dict__[_plug].getValue(),
                             cc = cgmGEN.Callback(self.set_optionVar, self.__dict__[_plug], None, self.uiSelector_targetMode))

        
        
    _row.setStretchWidget(mUI.MelSeparator(_row))
        
    mc.button(parent=_row,
              l = 'loc',
              ut = 'cgmUITemplate',                                    
              c= lambda *a:uiFunc_createLoc(self,False),
              ann = "Create a special loc at the object")
    
    mUI.MelSpacer(_row,w=10)    
    _row.layout()
    
    #Options ----------------------------------------------------------------------------------
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    
    _d = {'position':'pos',
          'rotation':'rot',
          'rotateAxis':'ra',
          'rotateOrder':'ro',
          'scalePivot':'sp',
          'rotatePivot':'rp'}
    _d_defaults = {'position':1}
    _l_order = ['position','rotation','rotateAxis','rotateOrder','scalePivot','rotatePivot']
    self._dCB_snapOptions = {}
    for k in _l_order:
        _plug = 'cgmVar_snapAdvanced_' + k
        try:self.__dict__[_plug]
        except:
            _default = _d_defaults.get(k,0)
            log.debug("{0}:{1}".format(_plug,_default))
            self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = _default)
        
        l = k
        _buffer = _d.get(k)
        if _buffer:l = _buffer
        _cb = mUI.MelCheckBox(_row,label=l,
                              annotation = 'Snap: {0}'.format(k),
                              value = self.__dict__[_plug].value,
                              onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                              offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
        self._dCB_snapOptions[k] = _cb

    mc.button(parent=_row,
              l = 'Snap',
              ut = 'cgmUITemplate',                                    
              c= lambda *a:uiFunc_snap(self),
              ann = "Snap via the ui settings")
    mc.button(parent=_row,
              l = 'Seq',
              ut = 'cgmUITemplate',                                    
              c= lambda *a:uiFunc_snapOrdered(self),
              ann = "Snap from each to next. Processes pairs in reverse order for dependencies")    
    mc.button(parent=_row,
              l = 'Query',
              ut = 'cgmUITemplate',
              c= lambda *a:uiQuery_advancedSnap(self),
              #c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
              ann = "Query current settings")    
    _row.layout()
    log.debug("<< buildSection_advancedSnap...")

def buildSection_aim(self,parent):
    try:self.var_aimFrameCollapse
    except:self.create_guiOptionVar('aimFrameCollapse',defaultValue = 0)
    
    _frame = mUI.MelFrameLayout(parent,label = 'Aim',vis=True,
                                collapse=self.var_aimFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_aimFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_aimFrameCollapse.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    #>>>Aim snap -------------------------------------------------------------------------------------    
    _row_aim = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)

    mc.button(parent=_row_aim,
              l = 'Aim',
              ut = 'cgmUITemplate',                                    
              c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToLast'),
              ann = "Aim snap in a from:to selection")

    mc.button(parent=_row_aim,
              ut = 'cgmUITemplate',                  
              l = 'Sel Order',
              c = lambda *a:SNAPCALLS.snap_action(None,'aim','eachToNext'),
              ann = "Aim in selection order from each to next")

    mc.button(parent=_row_aim,
              ut = 'cgmUITemplate',                                    
              l = 'First to Mid',
              c = lambda *a:SNAPCALLS.snap_action(None,'aim','firstToRest'),
              ann = "Aim the first object to the midpoint of the rest")  
    
    mc.button(parent=_row_aim,
              l = 'AimCast',
              ut = 'cgmUITemplate',                                                        
              c = lambda *a:SNAPCALLS.aimSnap_start(None),
              ann = "AimCast snap selected objects")           

    _row_aim.layout()   
    
    
    buildRow_aimMode(self,_inside)        
    buildSection_objDefaults(self,_inside,frame=False)
    
def buildSection_objDefaults(self,parent,frame=True):
    try:self.var_objDefaultAimAxis
    except:self.var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
    try:self.var_objDefaultUpAxis
    except:self.var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)
    try:self.var_objDefaultOutAxis
    except:self.var_objDefaultOutAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultOutAxis', defaultValue = 3)    
    if frame:
        _frame = mUI.MelFrameLayout(parent,label = 'Obj Defaults',vis=True,
                                    collapse=self.var_objectDefaultsFrameCollapse.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:self.var_objectDefaultsFrameCollapse.setValue(0),
                                    collapseCommand = lambda:self.var_objectDefaultsFrameCollapse.setValue(1)
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    else:
        _inside = parent


    #>>>Aim defaults mode -------------------------------------------------------------------------------------
    _d = {'aim':self.var_objDefaultAimAxis,
          'up':self.var_objDefaultUpAxis,
          'out':self.var_objDefaultOutAxis}

    for k in _d.keys():
        _var = _d[k]

        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l='Obj {0}:'.format(k))
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        uiRC = mUI.MelRadioCollection()

        _on = _var.value

        for i,item in enumerate(SHARED._l_axis_by_string):
            if i == _on:
                _rb = True
            else:_rb = False

            uiRC.createButton(_row,label=item,sl=_rb,
                              onCommand = cgmGEN.Callback(_var.setValue,i))

            mUI.MelSpacer(_row,w=2)       


        _row.layout() 


    #>>>Buttons -------------------------------------------------------------------------------------
    _row_defaults = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5, )

    cgmUI.add_Button(_row_defaults,'Tag selected for aim',
                     lambda *a:MMCONTEXT.func_process(SNAP.verify_aimAttrs, mc.ls(sl=True),'each','Verify aim attributes',True,**{}),)                                       
    _row_defaults.layout() 

     
def buildRow_aimMode(self,parent):
    try:self.var_aimMode
    except:self.var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode', defaultValue = 'world')   

    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Aim Mode:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    uiRC = mUI.MelRadioCollection()

    _on = self.var_aimMode.value

    for i,item in enumerate(['local','world','matrix']):
        if item == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(self.var_aimMode.setValue,item))

        mUI.MelSpacer(_row,w=2)       


    _row.layout()      

def buildRow_matchMode(self,parent):
    try:self.var_matchModeMove
    except:self.var_matchModeMove = cgmMeta.cgmOptionVar('cgmVar_matchModeMove', defaultValue = 1)
    try:self.var_matchModeRotate
    except:self.var_matchModeRotate = cgmMeta.cgmOptionVar('cgmVar_matchModeRotate', defaultValue = 1)
    try:self.var_matchMode
    except:self.var_matchMode = cgmMeta.cgmOptionVar('cgmVar_matchMode', defaultValue = 2)
    
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Match Mode:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )

    uiRC = mUI.MelRadioCollection()

    _on = self.var_matchMode.value

    for i,item in enumerate(['point','orient','point/orient']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(LOCINATOR.uiFunc_change_matchMode,self,i))

        mUI.MelSpacer(_row,w=2)       

    _row.layout()
    
def buildSection_snap(self,parent):
    try:self.var_snapFrameCollapse
    except:self.create_guiOptionVar('snapFrameCollapse',defaultValue = 0) 

    _frame = mUI.MelFrameLayout(parent,label = 'Snap',vis=True,
                                collapse=self.var_snapFrameCollapse.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:self.var_snapFrameCollapse.setValue(0),
                                collapseCommand = lambda:self.var_snapFrameCollapse.setValue(1)
                                )	
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 


    #>>>Base snap -------------------------------------------------------------------------------------
    _row_base = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)

    mc.button(parent=_row_base,
              l = 'Point',
              ut = 'cgmUITemplate',
              c = lambda *a:SNAPCALLS.snap_action(None,'point'),
              ann = "Point snap in a from:to selection")

    mc.button(parent=_row_base,
              l = 'Point - closest',
              ut = 'cgmUITemplate',                    
              c = lambda *a:SNAPCALLS.snap_action(None,'closestPoint'),
              ann = "Closest point on target")    

    mc.button(parent=_row_base,
              l = 'Parent',
              ut = 'cgmUITemplate',                    
              c = lambda *a:SNAPCALLS.snap_action(None,'parent'),
              ann = "Parent snap in a from:to selection")
    mc.button(parent=_row_base,
              l = 'Orient',
              ut = 'cgmUITemplate',                  
              c = lambda *a:SNAPCALLS.snap_action(None,'orient'),
              ann = "Orient snap in a from:to selection")        
    mc.button(parent=_row_base,
              l = 'RayCast',
              ut = 'cgmUITemplate',                                                        
              c = lambda *a:SNAPCALLS.raySnap_start(None),
              ann = "RayCast snap selected objects")
    _row_base.layout() 

    
    """
    #>>>Ray snap -------------------------------------------------------------------------------------
    _row_ray = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_ray,w=5)                                              
    mUI.MelLabel(_row_ray,l='CastSnap:')
    _row_ray.setStretchWidget(mUI.MelSeparator(_row_ray)) 

    mc.button(parent=_row_ray,
              l = 'RayCast',
              ut = 'cgmUITemplate',                                                        
              c = lambda *a:SNAPCALLS.raySnap_start(None),
              ann = "RayCast snap selected objects")
    mc.button(parent=_row_ray,
              l = 'AimCast',
              ut = 'cgmUITemplate',                                                        
              c = lambda *a:SNAPCALLS.aimSnap_start(None),
              ann = "AimCast snap selected objects")   
    mUI.MelSpacer(_row_ray,w=5)                                              
    _row_ray.layout()    """         

    #>>>Match snap -------------------------------------------------------------------------------------
    buildRow_matchMode(self,_inside)     

    _row_match = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_match,w=5)                                              
    mUI.MelLabel(_row_match,l='MatchSnap:')
    _row_match.setStretchWidget(mUI.MelSeparator(_row_match)) 

    mc.button(parent=_row_match,
              l = 'Self',
              ut = 'cgmUITemplate',                                                                    
              c = cgmGEN.Callback(MMCONTEXT.func_process, LOCINATOR.update_obj, None,'each','Match',False,**{'mode':'self'}),#'targetPivot':self.var_matchModePivot.value                                                                      
              ann = "Update selected objects to match object. If the object has no match object, a loc is created")
    mc.button(parent=_row_match,
              ut = 'cgmUITemplate',                                                                            
              l = 'Target',
              c = cgmGEN.Callback(MMCONTEXT.func_process, LOCINATOR.update_obj, None,'each','Match',False,**{'mode':'target'}),#'targetPivot':self.var_matchModePivot.value                                                                      
              ann = "Update the match object, not the object itself")
    mc.button(parent=_row_match,
              ut = 'cgmUITemplate',                                                                            
              l = 'Buffer',
              #c = cgmGEN.Callback(buttonAction,raySnap_start(_sel)),                    
              c = cgmGEN.Callback(LOCINATOR.update_obj,**{'mode':'buffer'}),#'targetPivot':self.var_matchModePivot.value                                                                      
              ann = "Update the buffer (if exists)")    
    mUI.MelSpacer(_row_match,w=5)                                              
    _row_match.layout()         

    #>>>Linear snap -------------------------------------------------------------------------------------
    _row_arrange = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_arrange,w=5)                                              
    mUI.MelLabel(_row_arrange,l='Linear:')
    _row_arrange.setStretchWidget(mUI.MelSeparator(_row_arrange)) 

    mc.button(parent=_row_arrange,
              l = 'Even',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('linearEven'))
    mc.button(parent=_row_arrange,
              l = 'Spaced',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'spaced'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('linearSpaced'))
    
    mUI.MelSpacer(_row_arrange,w=5)                                              
    _row_arrange.layout()
    

    #>>>Cubic snap -------------------------------------------------------------------------------------
    _row_arrange = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_arrange,w=5)                                              
    mUI.MelLabel(_row_arrange,l='Cubic:')
    _row_arrange.setStretchWidget(mUI.MelSeparator(_row_arrange)) 

    mc.button(parent=_row_arrange,
              l = 'Curve[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubic'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('cubicEven'))
    mc.button(parent=_row_arrange,
              l = 'Arc[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubicArc'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('cubicArcEven'))
    mc.button(parent=_row_arrange,
              l = 'Arc[Spaced]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'spaced','curve':'cubicArc'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('cubicArcSpaced'))
    mUI.MelSpacer(_row_arrange,w=5)
    _row_arrange.layout()


    #>>>Arrange snap -------------------------------------------------------------------------------------
    _row_arrange = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_arrange,w=5)                                              
    mUI.MelLabel(_row_arrange,l='Curve Rebuild:')
    _row_arrange.setStretchWidget(mUI.MelSeparator(_row_arrange)) 

    mc.button(parent=_row_arrange,
              l = '2[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubicRebuild','spans':2}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild2Even'))
    mc.button(parent=_row_arrange,
              l = '2[Spaced]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'spaced','curve':'cubicRebuild','spans':2}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild2Spaced'))
    mc.button(parent=_row_arrange,
              l = '3[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubicRebuild','spans':2}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild3Even'))
    mc.button(parent=_row_arrange,
              l = '3[Spaced]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'spaced','curve':'cubicRebuild','spans':3}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild3Spaced'))    

    mUI.MelSpacer(_row_arrange,w=5)                                              
    _row_arrange.layout()
        
def buildColumn_main(self,parent, asScroll = False):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """   
    if asScroll:
        _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
    else:
        _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUITemplate') 
    
    buildSection_snap(self, _inside)
    buildSection_aim(self,_inside)
    buildSection_advancedSnap(self,_inside)
    
    return _inside

def uiFunc_createLoc(self,selfMode = False):
    try:
        _d = uiQuery_advancedSnap(self)
        _sel = _d.pop('sl')
        if not _sel:
            return log.error("Nothing selected")
        
        if len(_sel) == 1:
            targets = None
        else:
            targets = _sel[1:]
            
        obj = _sel[0]
        _d['queryMode'] = True
        
        if selfMode:
            _d['objLoc'] = True
        else:
            _d['targetLoc'] = True
            
        #cgmGEN.func_snapShot(vars())
        SNAPCALLS.snap( obj,targets, **_d)
        
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def uiFunc_snap(self):
    try:
        _d = uiQuery_advancedSnap(self)
        _sel = _d.pop('sl')
        if not _sel:
            return log.error("Nothing selected")
        
        if len(_sel) == 1:
            targets = None
        else:
            targets = _sel[1:]
        obj = _sel[0]
        SNAPCALLS.snap( obj,targets, **_d)
        
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def uiFunc_snapOrdered(self):
    try:
        _d = uiQuery_advancedSnap(self)
        _sel = _d.pop('sl')
        if not _sel:
            return log.error("Nothing selected")
        
        #if len(_sel) == 1:
        #    targets = None
        #else:
        #    targets = _sel[1:]
        #obj = _sel[0]
        #SNAPCALLS.snap( obj,targets, **_d)
        targets = _sel
        #targets.reverse()
        #reload(MMCONTEXT)
        MMCONTEXT.func_process(SNAPCALLS.snap,targets,'eachToNextReverse',**_d)
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
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


#>>> Core functions =====================================================================================
