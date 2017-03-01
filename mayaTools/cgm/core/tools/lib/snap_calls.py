"""
------------------------------------------
snap_calls: cgm.core.tools.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__version__ = '0.1.02282017'

import webbrowser

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import maya.cmds as mc
import maya
import maya.mel as mel


from cgm.core import cgm_General as cgmGen
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
from cgm.core.lib import shared_data as SHARED
from cgm.core.tools import locinator as LOCINATOR
from cgm.core.lib import snap_utils as SNAP

import cgm.core.classes.GuiFactory as cgmUI
reload(cgmUI)
mUI = cgmUI.mUI

_2016 = False
if cgmGen.__mayaVersion__ >=2016:
    _2016 = True
    
    
var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode', defaultValue = 'world') 
var_snapPivotMode = cgmMeta.cgmOptionVar('cgmVar_snapPivotMode', defaultValue = 0)        

#var_resetMode = cgmMeta.cgmOptionVar('cgmVar_ChannelResetMode', defaultValue = 0)
#var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)
#var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)        
var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)
#var_objDefaultOutAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultOutAxis', defaultValue = 3)                        
#var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])
#var_contextTD = cgmMeta.cgmOptionVar('cgmVar_contextTD', defaultValue = 'selection')   



"""self.create_guiOptionVar('snapPivotMode', defaultValue = 0)
self.create_guiOptionVar('rayCastMode', defaultValue = 0)
self.create_guiOptionVar('rayCastOffset', defaultValue = 0)
self.create_guiOptionVar('rayCastCreate', defaultValue = 0)
self.create_guiOptionVar('rayCastOffsetDist', defaultValue = 1.0) """ 

def snap_action(objects = None, snapMode = 'point',selectionMode = 'eachToLast'):
    """
    """
    _str_func = 'snap_action'
    
    if snapMode == 'aim':
        aim_axis = SHARED._l_axis_by_string[var_objDefaultAimAxis.value]
        up_axis = SHARED._l_axis_by_string[var_objDefaultUpAxis.value]
                
        kws = {'aimAxis':aim_axis, 'upAxis':up_axis, 'mode':var_aimMode.value}
        
        if selectionMode == 'firstToRest':
            MMCONTEXT.func_process(SNAP.aim_atMidPoint, objects ,selectionMode,'Snap aim', **kws)
        else:
            MMCONTEXT.func_process(SNAP.aim, objects ,selectionMode,'Snap aim', **kws)
    else:
        kws = {'position' : False, 'rotation' : False, 'rotateAxis' : False,'rotateOrder' : False,'scalePivot' : False,
               'pivot' : 'rp', 'space' : 'w', 'mode' : 'xform'}
        
        if snapMode == 'point':
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
        
        _pivotMode = var_snapPivotMode.value
        
        if not _pivotMode:pass#0 handled by default
        elif _pivotMode == 1:
            kws['pivot'] = 'sp'
        elif _pivotMode == 2:
            kws['pivot'] = 'boundingBox'
        else:
            raise ValueError,"Uknown pivotMode: {0}".format(_pivotMode)        
    
        MMCONTEXT.func_process(SNAP.go, objects ,selectionMode, 'Snap', **kws)
    
    
    return

from cgm.core.classes import DraggerContextFactory as cgmDrag
reload(cgmDrag)
def aimSnap_start(targets=[]):
    raySnap_start(targets, None, False, snap=False, aim=True)
    
def rayCast_create(targets = [],create = None, drag=False):
    raySnap_start(targets,create = create, drag = drag)
    
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
            cgmGen.log_info_dict(kws,"RayCast args")        
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
    cgmGen.log_info_dict(kws,"RayCast args")
    
    cgmDrag.clickMesh(**kws)
    return


class ui_optionVars(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'SnapOptionVars_ui'    
    WINDOW_TITLE = 'Snap OptionVars - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 400,350
    
    def insert_init(self,*args,**kws):
            if kws:log.debug("kws: %s"%str(kws))
            if args:log.debug("args: %s"%str(args))
            log.info(self.__call__(q=True, title=True))
    
            self.__version__ = __version__
            self.__toolName__ = 'SnapOptionVars'		
            #self.l_allowedDockAreas = []
            self.WINDOW_TITLE = ui_optionVars.WINDOW_TITLE
            self.DEFAULT_SIZE = ui_optionVars.DEFAULT_SIZE
            
            
            self.create_guiOptionVar('matchFrameCollapse',defaultValue = 0) 
            self.create_guiOptionVar('rayCastFrameCollapse',defaultValue = 0) 
            self.create_guiOptionVar('aimFrameCollapse',defaultValue = 0) 
            self.create_guiOptionVar('objectDefaultsFrameCollapse',defaultValue = 0) 
            
            
            self.var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode', defaultValue = 'world')   
            
                  
            self.var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
            self.var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)
            self.var_objDefaultOutAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultOutAxis', defaultValue = 3)
            
            self.var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])            
            self.var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
            self.var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetMode', defaultValue=0)
            self.var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0) 
            self.var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)
            self.var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)
            
            self.var_matchModeMove = cgmMeta.cgmOptionVar('cgmVar_matchModeMove', defaultValue = 1)
            self.var_matchModeRotate = cgmMeta.cgmOptionVar('cgmVar_matchModeRotate', defaultValue = 1)
            #self.var_matchModePivot = cgmMeta.cgmOptionVar('cgmVar_matchModePivot', defaultValue = 0)
            self.var_matchMode = cgmMeta.cgmOptionVar('cgmVar_matchMode', defaultValue = 2)    
            self.var_locinatorTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_locinatorTargetsBuffer',defaultValue = [''])
            
    def build_menus(self):
        self.uiMenu_Buffers = mUI.MelMenu( l='Buffers', pmc = cgmGen.Callback(self.buildMenu_buffer))
   
    def buildMenu_buffer(self):
        self.uiMenu_Buffers.clear()  
    
        uiMenu = self.uiMenu_Buffers
        
        _d = {'RayCast':self.var_rayCastTargetsBuffer,
              'Match':self.var_locinatorTargetsBuffer}
        
        for k in _d.keys():
            var = _d[k]
            _ui = mc.menuItem(p=uiMenu, subMenu = True,
                              l = k)
            
            mc.menuItem(p=_ui, l="Define",
                        c= cgmGen.Callback(cgmUI.varBuffer_define,self,var))                                
        
            mc.menuItem(p=_ui, l="Add Selected",
                        c= cgmGen.Callback(cgmUI.varBuffer_add,self,var))        
                                
            mc.menuItem(p=_ui, l="Remove Selected",
                        c= cgmGen.Callback(cgmUI.varBuffer_remove,self,var))        
                        
        
            mc.menuItem(p=_ui,l='----------------',en=False)
            mc.menuItem(p=_ui, l="Report",
                        c= cgmGen.Callback(var.report))        
            mc.menuItem(p=_ui, l="Select Members",
                        c= cgmGen.Callback(var.select))        
            mc.menuItem(p=_ui, l="Clear",
                        c= cgmGen.Callback(var.clear))  
        
        mc.menuItem(p=uiMenu, l="--------------",en=False)
        mc.menuItem(p=uiMenu, l="Reload",
                    c= cgmGen.Callback(ui_optionVars))          
    
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        #Match
        #Aim
        _column = mUI.MelColumnLayout(parent,useTemplate = 'cgmUITemplate') 
        
        
        #>>>Match ====================================================================================
        _update_frame = mUI.MelFrameLayout(_column,label = 'Match Options',vis=True,
                                         collapse=self.var_matchFrameCollapse.value,
                                         collapsable=True,
                                         enable=True,
                                         useTemplate = 'cgmUIHeaderTemplate',
                                         expandCommand = lambda:self.var_matchFrameCollapse.setValue(0),
                                         collapseCommand = lambda:self.var_matchFrameCollapse.setValue(1)
                                         )	
        _update_inside = mUI.MelColumnLayout(_update_frame,useTemplate = 'cgmUISubTemplate')  
        
        
        #>>>Match mode -------------------------------------------------------------------------------------
        _row = mUI.MelHSingleStretchLayout(_update_inside,ut='cgmUISubTemplate',padding = 5)
        
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
                              onCommand = cgmGen.Callback(LOCINATOR.uiFunc_change_matchMode,self,i))
            
            mUI.MelSpacer(_row,w=2)       
        
        
        _row.layout()        
        
        
        #>>>Aim ====================================================================================
        mc.setParent(_column)
        cgmUI.add_SectionBreak()        
        _aim_frame = mUI.MelFrameLayout(_column,label = 'Aim Options',vis=True,
                                         collapse=self.var_aimFrameCollapse.value,
                                         collapsable=True,
                                         enable=True,
                                         useTemplate = 'cgmUIHeaderTemplate',
                                         expandCommand = lambda:self.var_aimFrameCollapse.setValue(0),
                                         collapseCommand = lambda:self.var_aimFrameCollapse.setValue(1)
                                         )	
        _aim_inside = mUI.MelColumnLayout(_aim_frame,useTemplate = 'cgmUISubTemplate')  
        
        
        #>>>Aim mode -------------------------------------------------------------------------------------
        _row_aimFlags = mUI.MelHSingleStretchLayout(_aim_inside,ut='cgmUISubTemplate',padding = 5)
        
        mUI.MelSpacer(_row_aimFlags,w=5)                      
        mUI.MelLabel(_row_aimFlags,l='Aim Mode:')
        _row_aimFlags.setStretchWidget( mUI.MelSeparator(_row_aimFlags) )
        
        uiRC = mUI.MelRadioCollection()
        
        _on = self.var_aimMode.value

        for i,item in enumerate(['local','world','matrix']):
            if item == _on:
                _rb = True
            else:_rb = False
            
            uiRC.createButton(_row_aimFlags,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(self.var_aimMode.setValue,item))
            
            mUI.MelSpacer(_row_aimFlags,w=2)       
        
        
        _row_aimFlags.layout()
        
        
        
        #>>>Obj Defaults ====================================================================================
        mc.setParent(_column)
        cgmUI.add_SectionBreak()
        _defaults_frame = mUI.MelFrameLayout(_column,label = 'Object Defaults Options',vis=True,
                                         collapse=self.var_objectDefaultsFrameCollapse.value,
                                         collapsable=True,
                                         enable=True,
                                         useTemplate = 'cgmUIHeaderTemplate',
                                         expandCommand = lambda:self.var_objectDefaultsFrameCollapse.setValue(0),
                                         collapseCommand = lambda:self.var_objectDefaultsFrameCollapse.setValue(1)
                                         )	
        _defaults_inside = mUI.MelColumnLayout(_defaults_frame,useTemplate = 'cgmUISubTemplate')  
        

        #>>>Aim defaults mode -------------------------------------------------------------------------------------
        _d = {'aim':self.var_objDefaultAimAxis,
              'up':self.var_objDefaultUpAxis,
              'out':self.var_objDefaultOutAxis}
        
        for k in _d.keys():
            _var = _d[k]
            
            _row = mUI.MelHSingleStretchLayout(_defaults_inside,ut='cgmUISubTemplate',padding = 5)
                    
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
                                  onCommand = cgmGen.Callback(_var.setValue,i))
                
                mUI.MelSpacer(_row,w=2)       
            
            
            _row.layout() 
            
        
        #>>>Buttons -------------------------------------------------------------------------------------
        _row_defaults = mUI.MelHLayout(_defaults_inside,ut='cgmUISubTemplate',padding = 5, )
        
        cgmUI.add_Button(_row_defaults,'Tag selected for aim',
                         lambda *a:MMCONTEXT.func_process(SNAP.verify_aimAttrs, mc.ls(sl=True),'each','Verify aim attributes',True,**{}),)                                       
        _row_defaults.layout() 
        
        
        #>>>Raycast ====================================================================================
        mc.setParent(_column)
        cgmUI.add_SectionBreak()
        _raycast_frame = mUI.MelFrameLayout(_column,label = 'RayCast Options',vis=True,
                                         collapse=self.var_rayCastFrameCollapse.value,
                                         collapsable=True,
                                         enable=True,
                                         useTemplate = 'cgmUIHeaderTemplate',
                                         expandCommand = lambda:self.var_rayCastFrameCollapse.setValue(0),
                                         collapseCommand = lambda:self.var_rayCastFrameCollapse.setValue(1)
                                         )	
        _raycast_inside = mUI.MelColumnLayout(_raycast_frame,useTemplate = 'cgmUISubTemplate') 
        
        
        #>>>Cast Mode  -------------------------------------------------------------------------------------
        uiRC = mUI.MelRadioCollection()
        _on = self.var_rayCastMode.value
        
        _row1 = mUI.MelHSingleStretchLayout(_raycast_inside,ut='cgmUISubTemplate',padding = 5)
        
        
        mUI.MelSpacer(_row1,w=5)
        
        mUI.MelLabel(_row1,l='Cast')
        _row1.setStretchWidget( mUI.MelSeparator(_row1) )
        
        uiRC = mUI.MelRadioCollection()
        _on = self.var_rayCastMode.value

        for i,item in enumerate(['close','mid','far','all','x','y','z']):
            if i == _on:
                _rb = True
            else:_rb = False
            
            uiRC.createButton(_row1,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(self.var_rayCastMode.setValue,i))
            
            mUI.MelSpacer(_row1,w=2)    
     
        _row1.layout() 
                 
        #>>>offset Mode  -------------------------------------------------------------------------------------
        uiRC = mUI.MelRadioCollection()
        _on = self.var_rayCastOffsetMode.value        
        
        _row_offset = mUI.MelHSingleStretchLayout(_raycast_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_offset,w=5)                              
        mUI.MelLabel(_row_offset,l='Offset')
        _row_offset.setStretchWidget( mUI.MelSeparator(_row_offset) )  
                
        for i,item in enumerate(['None','Distance','snapCast']):
            if i == _on:
                _rb = True
            else:_rb = False
            
            uiRC.createButton(_row_offset,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(self.var_rayCastOffsetMode.setValue,i))
            
            mUI.MelSpacer(_row1,w=2)   
                
                         
        _row_offset.layout()
        
        
        #>>>offset Mode  -------------------------------------------------------------------------------------
        uiRC = mUI.MelRadioCollection()
        _on = self.var_rayCastOrientMode.value        
        
        _row_orient = mUI.MelHSingleStretchLayout(_raycast_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_orient,w=5)                              
        mUI.MelLabel(_row_orient,l='Orient')
        _row_orient.setStretchWidget( mUI.MelSeparator(_row_orient) )  
                
        for i,item in enumerate(['None','Normal']):
            if i == _on:
                _rb = True
            else:_rb = False
            
            uiRC.createButton(_row_orient,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(self.var_rayCastOrientMode.setValue,i))
            
            mUI.MelSpacer(_row1,w=2)   
                         
        cgmUI.add_Button(_row_orient,'Set drag interval',
                         lambda *a:self.var_rayCastDragInterval.uiPrompt_value('Set drag interval'),
                         'Set the rayCast drag interval by ui prompt')   
        cgmUI.add_Button(_row_orient,'Set Offset',
                         lambda *a:self.var_rayCastOffsetDist.uiPrompt_value('Set offset distance'),
                         'Set the the rayCast offset distance by ui prompt')         
        
        _row_orient.layout()        

        
        
        """
        self.var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])            
        #self.var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
        self.var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffset', defaultValue=0)
        self.var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0) 
        self.var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)
        #self.var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)        
        
        """
        
        
        
            
        return
"""
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
                                c = cgmGen.Callback(self.var_objDefaultAimAxis.setValue,i),
                                rb = _rb)  
"""
    
    
    