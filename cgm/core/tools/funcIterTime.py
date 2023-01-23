"""
------------------------------------------
funcIterTime: cgm.core
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------
================================================================
"""


# From Python =============================================================
import pprint
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import locator_utils as LOC
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
#import cgm.core.lib.shared_data as CORESHARE
#import cgm.core.lib.string_utils as CORESTRINGS
from cgm.core.lib import search_utils as SEARCH
#import cgm.core.classes.GuiFactory as cgmUI
#import cgm.core.mrs.lib.animate_utils as MRSANIMUTILS
import cgm.core.lib.list_utils as CORELIST

__version__ = cgmGEN.__RELEASESTRING
_l_contextTime = ['back',
                  #'previous',
                  #'current',
                  'input',
                  #'bookEnd',
                  #'next',
                  'forward',
                  'slider',
                  'scene',
                  'selected']
_d_timeShorts = {'combined':'comb',
                 'interval':'int',
                 'back':'<-',
                 'previous':'|<',
                 'bookEnd':'|--|',
                 'current':'now',
                 'selected':'sel',
                 'next':'>|',
                 'slider':'[ ]',
                 'input': '[...]',
                 'forward':'->'}
_l_contextKeys = [#'each',
                  #'combined',
                  'keys',
                  'interval']


#_l_contextTime = MRSANIMUTILS._l_contextTime + ['input']

import cgm.core.classes.GuiFactory as CGMUI
#reload(cgmUI)
CGMUI.initializeTemplates()
mUI = CGMUI.mUI

from cgm.lib import lists
log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start
_d_annotations = {'me':'Create a loc from selected objects',
                  'mid':'Create a loc at the bb midpoint of a single target or the mid point of multiple targets',
                  'closestPoint':'Create a loc at the closest point on the targets specified - curve, mesh, nurbs',
                  'closestTarget':'Create a loc at the closest target',
                  'rayCast':'Begin a clickMesh instance to cast a single locator in scene',
                  'updateSelf':'Update the selected objects',
                  'updateTarget':'Update the selected targets if possible',
                  'updateBuffer':'Update objects loaded to the buffer',
                  'sliderRange':' Push the slider range values to the int fields',
                  'selectedRange': 'Push the selected timeline range (if active)',
                  'sceneRange':'Push scene range values to the int fields',
                  '<<<':'Bake within a context of keys in range prior to the current time',
                  'All':'Bake within a context of the entire range of keys ',
                  '>>>':'Bake within a context of keys in range after the current time',
                  'attach':'Create a loc of the selected object AND start a clickMesh instance to setup an attach point on a mesh in scene'}

class fOverTimeBAK:
    def __init__(self, frame_start = None, frame_end=None, interval=None):
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.interval = interval
        self.frames = []
        self.errors = []
        self.func = None
        self._args = None
        self._kws = None

    def set_func(self, func, *args, **kws):
        self.func = func
        self._args = args
        self._kws = kws

    def get_func(self,func = None,*args,**kwargs):
        if self.func:
            return self.func, self._args, self._kws
        if func == None:
            raise ValueError("{} | Need a function".format(self.__class__))

        return func,args,kwargs
 
    def run(self, function = None, *args, **kwargs):
        current_time = mc.currentTime(query=True)
        current_frame = self.frame_start
        while current_frame <= self.frame_end:
            mc.currentTime(current_frame)            
            try:
                if self.func:
                    self.func()
                else:                
                    function(*args, **kwargs)
            except Exception as e:
                self.errors.append((current_frame, e, args, kwargs))
            current_frame += self.interval
        mc.currentTime(current_time)

    def run_frames(self, function = None, *args, **kwargs):
        if not self.frames:
            raise ValueError("{} | No frames set".format(self.__class__))

        current_time = mc.currentTime(query=True)
        for f in self.frames:
            mc.currentTime(f)
            try:
                if self.func:
                    self.func()
                else:                
                    function(*args, **kwargs)
            except Exception as e:
                self.errors.append((f, e, args, kwargs))
        mc.currentTime(current_time)
        
    @cgmGEN.Wrap_exception
    def run_on_current_frame(self, function=None, *args, **kwargs):
        current_frame = mc.currentTime(query=True)
        try:
            if self.func:
                self.func()
            else:
                function(current_frame, *args, **kwargs)
        except Exception as e:
            self.errors.append((current_frame, e, args, kwargs))

    def pre_run(self):
        pass
    def post_run(self):
        pass

    def set_start(self,frame_start):
        self.frame_start = frame_start
    def set_end(self,frame_end):
        self.frame_end = frame_end
    def set_interval(self,interval):
        self.interval = interval

    def print_errors(self):
        if self.errors:
            print("{} | Errors occurred during processing:".__class__)
            for error in self.errors:
                print("Frame {}: {} with args={} and kwargs={}".format(error[0],error[1],error[2],error[3]))

class overload_call:
    def __init__(self, frame_start = None, frame_end=None, interval=None):
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.interval = interval
        self.frames = []
        self.errors = []
        
        self.showBake = False
        
        self.call = None
        self.func_pre = None
        self.func_post = None
        
        self.call_args = []
        self.call_kws = {}
        self.pre_args = []
        self.pre_kws = {}
                
        self.post_args = []
        self.post_kws = {}       

    #@cgmGEN.Wrap_exception
    #@cgmGEN.Timer    
    def run(self):
        _str_func = 'run[{0}]'.format(self.__class__.__name__)            
        log.debug("|{0}| >>...".format(_str_func))
        
        #pprint.pprint(self.__dict__)            
            
        current_time = mc.currentTime(query=True)
        current_frame = self.frame_start
        
        if not self.pre_run():
            mc.warning(log_msg(_str_func,"pre failed"))
            return False
        
        while current_frame <= self.frame_end:
            self.updateFrame()

            mc.currentTime(current_frame)            
                
            current_frame += self.interval
        mc.currentTime(current_time)
        self.post_run()
        
    #@cgmGEN.Wrap_exception
    #@cgmGEN.Timer
    def run_frames(self):
        _str_func = 'run_frames[{0}]'.format(self.__class__.__name__)            
        log.debug("|{0}| >>...".format(_str_func))
        
        if not self.frames:
            raise ValueError("{} | No frames set".format(self.__class__))
        
        if not self.pre_run():
            mc.warning(log_msg(_str_func,"pre failed"))
            return False
        
        current_time = mc.currentTime(query=True)
        for f in self.frames:
            mc.currentTime(f)
            self.updateFrame()

        mc.currentTime(current_time)
        self.post_run()
        
    def updateFrame(self):
        _str_func = 'updateFrame[{0}]'.format(self.__class__.__name__)            
        log.debug("|{0}| >>...".format(_str_func))
        
        try:self.call( *self.call_args, **self.call_kws )
        except Exception as err:
            log.info("Frame: {}".format(mc.currentTime(query=True)))            
            try:log.info("Func: {0}".format(self.call.__name__))
            except:log.info("Func: {0}".format(self.call))
            if self.call_args:
                log.info("args: {0}".format(self.call_args))
            if self.call_kws:
                log.info("kws: {0}".format(self.call_kws))
            for a in err.args:
                log.info(a)
                
    #@cgmGEN.Wrap_exception
    #@cgmGEN.Timer    
    def run_on_current_frame(self, function=None, *args, **kwargs):
        _str_func = 'run_on_current_frame[{0}]'.format(self.__class__.__name__)            
        log.debug("|{0}| >>...".format(_str_func))
        
        if not self.pre_run():
            mc.warning(log_msg(_str_func,"pre failed"))
            return False
        
        self.updateFrame()
        
        self.post_run()
        
    #@cgmGEN.Wrap_exception
    #@cgmGEN.Timer    
    def pre_run(self):
        _str_func = 'pre_run[{0}]'.format(self.__class__.__name__)            
        log.debug("|{0}| >>...".format(_str_func))
        
        if not self.showBake:
            mc.refresh(su=1)
            
        mc.undoInfo(openChunk=True,chunkName="undo{0}".format(self.call.__name__))
        self._autoKey = mc.autoKeyframe(q=True,state=True)            
        
        if self.func_pre:
            try:
                return self.func_pre( *self.pre_args, **self.pre_kws )
            except Exception as err:
                try:log.info("Func: {0}".format(self.func_pre.__name__))
                except:
                    log.info("Func: {0}".format(self.func_pre))
                if self.pre_args:
                    log.info("args: {0}".format(self.pre_args))
                if self.pre_kws:
                    log.info("kws: {0}".format(self.pre_kws))
                for a in err.args:
                    log.info(a)
                return False
        
        return True
    
    #@cgmGEN.Wrap_exception    
    #@cgmGEN.Timer
    def post_run(self):
        _str_func = 'post_run[{0}]'.format(self.__class__.__name__)            
        log.debug("|{0}| >>...".format(_str_func))
        try:
            if self.func_post:
                try:return self.func_post( *self.post_args, **self.post_kws )
                except Exception as err:
                    try:log.info("Func: {0}".format(self.func_post.__name__))
                    except:log.info("Func: {0}".format(self.func_post))
                if self.post_args:
                    log.info("args: {0}".format(self.post_args))
                if self.post_kws:
                    log.info("kws: {0}".format(self.post_kws))
                for a in err.args:
                    log.info(a)
        
        finally:
            mc.refresh(su=0)        
            if self._autoKey:#turn back on if it was
                mc.autoKeyframe(state=True)        
            mc.undoInfo(closeChunk=True,chunkName="undo{0}".format(self.call.__name__))

    def set_start(self,frame_start):
        self.frame_start = frame_start
    def set_end(self,frame_end):
        self.frame_end = frame_end
    def set_interval(self,interval):
        self.interval = interval
        
    def set_func(self,func = None,*args,**kws):
        self.call = func
        self.call_args = args
        self.call_kws = kws
        
    def set_pre(self,func = None,*args,**kws):
        self.func_pre = func
        self.pre_args = args
        self.pre_kws = kws
                
    def set_post(self,func = None,*args,**kws):
        self.func_post = func
        self.post_args = args
        self.post_kws = kws


    def print_errors(self):
        if self.errors:
            print("{} | Errors occurred during processing:".__class__)
            for error in self.errors:
                print("Frame {error[0]}: {error[1]} with args={error[2]} and kwargs={error[3]}")


class ui(CGMUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    _toolname = 'FuncIterTime'
    TOOLNAME = 'ui_FuncIterTime'
    WINDOW_NAME = "{}UI".format(TOOLNAME)
    WINDOW_TITLE = 'FIT | {0}'.format(__version__)
    DEFAULT_SIZE = 225, 350
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created

 
    def insert_init(self, *args, **kws):
        self.mFIT = overload_call()
        self.uiButton_bake = None
        self.ml_watch = []
        
        self.create_guiOptionVar('keysMode', defaultValue='loc')
        self.create_guiOptionVar('interval', defaultValue=1.0)
        self.create_guiOptionVar('showBake', defaultValue=0)
        self.create_guiOptionVar('context_keys', defaultValue='each')
        self.create_guiOptionVar('context_time', defaultValue='current')
        
        self.WINDOW_TITLE = ui.WINDOW_TITLE
        self.DEFAULT_SIZE = ui.DEFAULT_SIZE
    
    def post_init(self,*args,**kws):
        self.mFIT.call = self.uiFunc
        
    
    def log_dat(self):
        _str_func = 'log_self[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        pprint.pprint(self.mFIT.__dict__)        
        
    def watchTargets_set(self,arg = None):
        _str_func = '[{0}]watchTargets_set'.format(self.__class__.TOOLNAME)                    
        if not arg:
            arg = mc.ls(sl=1)
        self.ml_watch = cgmMeta.validateObjListArg(arg, noneValid=True)
        print("{} | Watch Targets: ".format(_str_func))
        pprint.pprint(self.ml_watch)
        
    def watchTargets_clear(self):
        _str_func = '[{0}]watchTargets_clear'.format(self.__class__.TOOLNAME)                            
        self.ml_watch = []
        mc.warning("{} | Watch Targets cleared ".format(_str_func))
    
    def build_menus(self):
        self.uiMenu_options = mUI.MelMenu( l='Options', pmc = cgmGEN.Callback(self.buildMenu_options) )        
        #self.uiMenu_FileMenu = mUI.MelMenu(l='File', pmc = cgmGEN.Callback(self.buildMenu_file))
        self.uiMenu_DevMenu = mUI.MelMenu(l='Dev', pmc = cgmGEN.Callback(self.buildMenu_dev))
        
    def uiFunc(self,*args,**kws):
        print('{} | do something here...'.format(mc.currentTime(q=True)))

        
    def buildMenu_options( self, *args):
        self.uiMenu_options.clear()   
        _menu = self.uiMenu_options
        
        
        #Dyn mode...
        uiDyn = mc.menuItem(p=_menu, l='ShowBake ', subMenu=True)        
        uiRC = mc.radioMenuItemCollection()
        _v = self.var_showBake.value
        
        for i in range(2):
            if i == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(p=uiDyn,collection = uiRC,
                        label=bool(i),
                        c = cgmGEN.Callback(self.var_showBake.setValue,i),
                        rb = _rb)
            
            
        mUI.MelMenuItemDiv(_menu,l='WatchTargets')
        mUI.MelMenuItem(_menu,
                        l='Set',
                        ann = 'Set watch targets',
                        c = lambda *a:self.watchTargets_set(),
                        )
        mUI.MelMenuItem(_menu,
                        l='Clear',
                        ann = 'clear watch targets',
                        c = lambda *a:self.watchTargets_clear(),
                        )
        return
 
        
    def buildMenu_file(self):
        self.uiMenu_FileMenu.clear()
        mUI.MelMenuItemDiv(self.uiMenu_FileMenu, l="Options")
        
        _menu = self.uiMenu_FileMenu
        #Context ...---------------------------------------------------------------------------------
        _starDir = mUI.MelMenuItem(_menu, l="StartDir",tearOff=True,
                                   subMenu = True)
        
        uiRC = mc.radioMenuItemCollection()

        
        _on = self.var_startDirMode.value
        for i,item in enumerate(self._l_startDirModes):
            if i == _on:_rb = True
            else:_rb = False
            mUI.MelMenuItem(_starDir,label=item,
                            collection = uiRC,
                            ann = _d_ann.get(item),
                            c = cgmGEN.Callback(self.uiFunc_setDirMode,i),                                  
                            rb = _rb)        
        
        mUI.MelMenuItemDiv(self.uiMenu_FileMenu, l="Utils")

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save",
                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_save)))
                         
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_save_actions,self)))

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save As",
                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_saveAs)))
        
        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Load",
                          c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_load)))
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_load_actions,self)))
                        
    def uiFunc_setDirMode(self,v):
        _str_func = 'uiFunc_setDirMode[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        _path = startDir_getBase(self._l_startDirModes[v])
        if _path:
            self.var_startDirMode.setValue(v)
            print(_path)
        
    
    def buildMenu_dev(self):
        self.uiMenu_DevMenu.clear()
        
        _menu = self.uiMenu_DevMenu
        mUI.MelMenuItem( _menu, l="Ui | ...",
                         c=lambda *a: self.log_self())               
        mUI.MelMenuItem( _menu, l="Dat | class",
                         c=lambda *a: self.log_dat())        

    def log_self(self):
        _str_func = 'log_self[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        pprint.pprint(self.__dict__)
        
    def set_func(self,func=None,*args,**kws):
        self.mFIT.call = func
        self.mFIT.call_args = args
        self.mFIT.call_kws = kws
        
        self.uiUpdate_base()
        
    def set_pre(self,func=None,*args,**kws):
        self.mFIT.func_pre = func
        self.mFIT.pre_args = args
        self.mFIT.pre_kws = kws
                
    def set_post(self,func=None,*args,**kws):
        self.mFIT.func_post = func
        self.mFIT.post_args = args
        self.mFIT.post_kws = kws
                
        
    def uiBuild_top(self):
        _str_func = 'uiUpdate_top[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        self.uiSection_top.clear()
        #CGMUI.add_Header('Put stuff here')
        mUI.MelLabel(self.uiSection_top, label = "You can add functions: \n uiFIT.set_func | set_pre | set_post")
    
    def uiUpdate_base(self):
        if self.mFIT.call:
            self.uiButton_current(edit=True,label = self.mFIT.call.__name__)
    
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        #Declare form frames...------------------------------------------------------
        _MainForm = mUI.MelFormLayout(parent,ut='CGMUITemplate')#mUI.MelColumnLayout(ui_tabs)

        #_inside = mUI.MelColumn(_MainForm,ut='CGMUITemplate')
        _inside = mUI.MelScrollLayout(_MainForm,ut='CGMUITemplate')
        
        #Top Section -----------
        self.uiSection_top = mUI.MelColumn(_inside, w = 180, 
                                           useTemplate = 'cgmUISubTemplate',vis=True)         
        self.uiBuild_top()
        
        self.uiButton_current = mUI.MelButton(_inside, label = 'Current',ut='cgmUITemplate',
                                              c = cgmGEN.Callback(self.mFIT.run_on_current_frame,self.mFIT),                                 
                                              )
        
        
        self.buildFrame_timeContext(_inside)
        """
        #Bake frame...------------------------------------------------------
        self.create_guiOptionVar('bake',defaultValue = 0)
        mVar_frame = self.var_bake
        
        _frame = mUI.MelFrameLayout(_inside,label = 'Bake',vis=True,
                                    collapse=mVar_frame.value,
                                    collapsable=True,
                                    enable=True,
                                    w=180,
                                    #ann='Contextual MRS functionality',
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:mVar_frame.setValue(0),
                                    collapseCommand = lambda:mVar_frame.setValue(1)
                                    )	
        self.uiFrame_bake = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
        self.uiFrame_buildBake()"""
        

        

        #Progress bar... ----------------------------------------------------------------------------
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)

        _row_cgm = CGMUI.add_cgmFooter(_MainForm)            

        #Form Layout--------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_inside,"top",0),
                        (_inside,"left",0),
                        (_inside,"right",0),
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),
                        (_row_cgm,"bottom",0),
                        ],
                  ac = [(_inside,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])
        
        
    def uiFrame_buildBake(self):
        self.uiFrame_bake.clear()
        
        _frame_inside = self.uiFrame_bake
        #>>>Update Row ---------------------------------------------------------------------------------------
        mc.setParent(_frame_inside)
        _row_timeSet = mUI.MelHLayout(_frame_inside,ut='cgmUISubTemplate',padding = 1)
    
        CGMUI.add_Button(_row_timeSet,'Slider',
                         cgmGEN.Callback(self.uiFunc_updateTimeRange,'slider'),                         
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         _d_annotations.get('sliderRange','fix sliderRange'))
        CGMUI.add_Button(_row_timeSet,'Sel',
                                 cgmGEN.Callback(self.uiFunc_updateTimeRange,'selected'),                         
                                 #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                                 _d_annotations.get('selectedRange','fix selectedRange'))        
    
        CGMUI.add_Button(_row_timeSet,'Scene',
                         cgmGEN.Callback(self.uiFunc_updateTimeRange,'scene'),                         
                         _d_annotations.get('sceneRange','fix sceneRange'))
  
        
        _row_timeSet.layout()          
        
        # TimeInput Row ----------------------------------------------------------------------------------
        _row_time = mUI.MelHRowLayout(_frame_inside,ut='cgmUISubTemplate')
        mUI.MelSpacer(_row_time)
        mUI.MelLabel(_row_time,l='start')
    
        self.uiFieldInt_start = mUI.MelIntField(_row_time,
                                                width = 40)
        #_row_time.setStretchWidget( mUI.MelSpacer(_row_time) )
        mUI.MelLabel(_row_time,l='end')
    
        self.uiFieldInt_end = mUI.MelIntField(_row_time,
                                              width = 40)
        
        mUI.MelLabel(_row_time,l='int')        
        self.uiFF_interval = mUI.MelFloatField(_row_time,precision = 1,
                                               value = self.var_interval.getValue(),
                                               width = 40, min=0.1)
        
        self.uiFF_interval(edit =True, cc = lambda *a:self.var_interval.setValue(self.uiFF_interval.getValue()))
        
        self.uiFunc_updateTimeRange()
    
        mUI.MelSpacer(_row_time)
        _row_time.layout()   

        #>>>Update Row ---------------------------------------------------------------------------------------
        mc.setParent(_frame_inside)
        CGMUI.add_LineSubBreak()
        
        _row_bake = mUI.MelHLayout(_frame_inside,ut='cgmUISubTemplate',padding = 1)
    
        CGMUI.add_Button(_row_bake,' <<<',
                         cgmGEN.Callback(self.uiFunc_bake,'back'),                         
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         _d_annotations.get('<<<','fix'))
    
        CGMUI.add_Button(_row_bake,'Range',
                         cgmGEN.Callback(self.uiFunc_bake,'range'),                         
                         _d_annotations.get('All','fix'))
        
        
        CGMUI.add_Button(_row_bake,'>>>',
                         cgmGEN.Callback(self.uiFunc_bake,'forward'),                         
                         _d_annotations.get('>>>','fix'))    
        
        _row_bake.layout()
        
        mUI.MelButton(_frame_inside,label = 'Selected Time',
                      ut='cgmUITemplate',
                      c = cgmGEN.Callback(self.uiFunc_bake,'selected'),                         
                      ann=_d_annotations.get('Selected','fix'))
        
        
    def buildFrame_timeContext(self,parent):
        def setContext_time(self,arg):
            self.var_context_time.setValue(arg)
            updateHeader(self)
        def setContext_keys(self,arg):
            self.var_context_keys.setValue(arg)
            updateHeader(self)        
            
        def updateHeader(self):
            self.uiFrame_time(edit=True, label = "Freq: [{0}] | Time: [{1}]".format(self.var_context_keys.value,
                                                                                          self.var_context_time.value))
            
            if self.uiButton_bake:
                self.uiButton_bake(edit=True, label = "Bake: {}".format(self.var_context_time.value))
            
        try:self.var_timeContextFrameCollapse
        except:self.create_guiOptionVar('timeContextFrameCollapse',defaultValue = 0)
        mVar_frame = self.var_timeContextFrameCollapse
        
        _frame = mUI.MelFrameLayout(parent,label = 'Bake',vis=True,
                                    collapse=mVar_frame.value,
                                    collapsable=True,
                                    enable=True,
                                    w=180,                                    
                                    #ann='Contextual MRS functionality',
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:mVar_frame.setValue(0),
                                    collapseCommand = lambda:mVar_frame.setValue(1)
                                    )	
        self.uiFrame_time = _frame
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
        
        #>>>Anim ===================================================================================== 
        #>>>Keys Context Options -------------------------------------------------------------------------------
        #bgc=_subLineBGC
        _rowContextKeys = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        #_rowContextKeys = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5,bgc=_subLineBGC)
    
    
        mUI.MelSpacer(_rowContextKeys,w=5)                          
        #mUI.MelLabel(_rowContextKeys,l='Keys: ')
        _rowContextKeys.setStretchWidget( mUI.MelSeparator(_rowContextKeys) )
    
        uiRC = mUI.MelRadioCollection()
    
        mVar = self.var_context_keys
        _on = mVar.value
    
        for i,item in enumerate(_l_contextKeys):
            if item == _on:
                _rb = True
            else:_rb = False
            _label = str(_d_timeShorts.get(item,item))
            uiRC.createButton(_rowContextKeys,label=_label,sl=_rb,
                              ann = "Set keys context to: {0}".format(item),                          
                              onCommand = cgmGEN.Callback(setContext_keys,self,item))
        
        
        self.uiFF_interval = mUI.MelFloatField(_rowContextKeys,precision = 1,
                                               value = self.var_interval.getValue(),
                                               width = 40, min=0.1)
        
        self.uiFF_interval(edit =True, cc = lambda *a:self.var_interval.setValue(self.uiFF_interval.getValue()))        
        
        mUI.MelSpacer(_rowContextKeys,w=2)                          
        
        _rowContextKeys.layout()    
    
        #>>>Time Context Options -------------------------------------------------------------------------------

        mVar = self.var_context_time
        _on = mVar.value
        
        import cgm.core.lib.list_utils as LISTS
        _split = LISTS.get_chunks(_l_contextTime,3)
        
        for s in _split:
            _rowContextTime = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=3,)            
            for i,item in enumerate(s):
                _label = str(_d_timeShorts.get(item,item))
                mUI.MelButton(_rowContextTime,label=_label,
                              ann = "Set time context to: {0}".format(item),
                              ut='cgmUITemplate',
                              c = cgmGEN.Callback(setContext_time,self,item)) 
            _rowContextTime.layout()
            mUI.MelSpacer(_inside,h=3)
        updateHeader(self)
        
        
        """
        # TimeInput Row ----------------------------------------------------------------------------------
        _row_time = mUI.MelHRowLayout(_inside,ut='cgmUISubTemplate')
        mUI.MelSpacer(_row_time)
        mUI.MelLabel(_row_time,l='start')
    
        self.uiFieldInt_start = mUI.MelIntField(_row_time,
                                                width = 40)
        #_row_time.setStretchWidget( mUI.MelSpacer(_row_time) )
        mUI.MelLabel(_row_time,l='end')
    
        self.uiFieldInt_end = mUI.MelIntField(_row_time,
                                              width = 40)
        
        
        self.uiFunc_updateTimeRange()
    
        mUI.MelSpacer(_row_time)
        _row_time.layout()                   
        """
        #cgmUI.add_Header("Input Time")        
        
        #>>>Update Row ---------------------------------------------------------------------------------------
        mc.setParent(_inside)
        _row_timeSet = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 3)
        mUI.MelSpacer(_row_timeSet,w=2)                          
        mUI.MelLabel(_row_timeSet,label="Input Utils")
        _row_timeSet.setStretchWidget( mUI.MelSeparator(_row_timeSet) )
    
        CGMUI.add_Button(_row_timeSet,'Slider',
                         cgmGEN.Callback(self.uiFunc_updateTimeRange,'slider'),                         
                         #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                         _d_annotations.get('sliderRange','fix sliderRange'))
        CGMUI.add_Button(_row_timeSet,'Sel',
                                 cgmGEN.Callback(self.uiFunc_updateTimeRange,'selected'),                         
                                 #lambda *a: attrToolsLib.doAddAttributesToSelected(self),
                                 _d_annotations.get('selectedRange','fix selectedRange'))        
    
        CGMUI.add_Button(_row_timeSet,'Scene',
                         cgmGEN.Callback(self.uiFunc_updateTimeRange,'scene'),                         
                         _d_annotations.get('sceneRange','fix sceneRange'))
        
        mUI.MelSpacer(_row_timeSet,w=2)                          
        _row_timeSet.layout()
        mUI.MelSpacer(_inside,h=3)
        
        
        _row_timeSet2 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 3)
        mUI.MelSpacer(_row_timeSet2,w=2)
        
        _row_timeSet2.setStretchWidget( mUI.MelSeparator(_row_timeSet2) )        
        
        mUI.MelLabel(_row_timeSet2,l='start')
        self.uiFieldInt_start = mUI.MelIntField(_row_timeSet2,
                                                width = 40)
        
        mUI.MelLabel(_row_timeSet2,l='end')
        self.uiFieldInt_end = mUI.MelIntField(_row_timeSet2,
                                              width = 40)
        _row_timeSet2.layout()
        mUI.MelSpacer(_inside,h=3)
        
        
        
        
        _row_timeSet3 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 3)
        mUI.MelSpacer(_row_timeSet3,w=2)                          
                
        mUI.MelButton(_row_timeSet3,label='Q',
                      ann='Query the time context',
                      c=cgmGEN.Callback(self.uiFunc_bake,**{'debug':True}))     
        
        _row_timeSet3.setStretchWidget( mUI.MelSeparator(_row_timeSet3) )        
        self.uiButton_bake = mUI.MelButton(_row_timeSet3,l='Bake',
                                           ut='cgmUITemplate',
                                           w=150,
                                           c = cgmGEN.Callback(self.uiFunc_bake),                         
                                           ann=_d_annotations.get('All','fix'))
        mUI.MelSpacer(_row_timeSet3,w=2)                          
        _row_timeSet3.layout()
        
        
        self.uiFunc_updateTimeRange()  
        
        

        
        
    def uiFunc_updateTimeRange(self,mode = 'slider'):
        _range = SEARCH.get_time(mode)
        if _range:
            self.uiFieldInt_start(edit = True, value = _range[0])
            self.uiFieldInt_end(edit = True, value = _range[1])            

    def uiFunc_bake(self, debug=False):
        _str_func = '[{0}] bake'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        var_keys = self.var_context_keys.getValue()
        var_time = self.var_context_time.getValue()
        
        #Initial range...
        if var_time == 'input':
            _range = [self.uiFieldInt_start.getValue(),self.uiFieldInt_end.getValue()]
        else:
            _range = SEARCH.get_time(var_time)        
        
        if var_keys == 'keys':
            if not self.ml_watch:
                return mc.warning("{} | Must have watch targets for keys mode".format(_str_func))
            
            cgmGEN._reloadMod(SEARCH)
            l_keys  = []
            for mObj in self.ml_watch:
                _keys = SEARCH.get_key_indices_from( mObj.mNode ,mode = var_time)
                #pprint.pprint(_keys)
                l_keys.extend(_keys)
                
            
            l_keys = CORELIST.get_noDuplicates(l_keys)
            self.mFIT.frames = l_keys
            
            
            if debug:
                pprint.pprint(vars())
                return        
            
            self.mFIT.run_frames()
            return

        
        if debug:
            pprint.pprint(vars())
            return        
        
        
        if not _range:
            return log.warning("No frames in range")
        
        self.mFIT.frame_start = _range[0]
        self.mFIT.frame_end = _range[1]
        self.mFIT.interval = self.uiFF_interval.getValue()

        self.mFIT.run()
        
        return
        
        
        if mode == 'selectedRange':
            _kws = {'boundingBox':False,'keysMode':self.var_keysMode.value,'keysDirection':mode,
                    'timeMode':'selected'}
        else:
            _kws = {'boundingBox':False,'keysMode':self.var_keysMode.value,'keysDirection':mode,
                    'timeMode':'custom','timeRange':[self.uiFieldInt_start(q=True, value = True),self.uiFieldInt_end(q=True, value = True)]}
        
        
        pprint.pprint(_kws)    
        #MMCONTEXT.func_process(bake_match, _targets,'all','Bake',False,**_kws)       








