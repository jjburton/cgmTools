"""
------------------------------------------
GuiFactory: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Class based ui builder for cgmTools
================================================================
"""
#>>> Root settings =============================================================

__version__ = '0.1.01242013'
__toolName__ = 'cgmGUI'
__toolURL__ = 'www.cgmonks.com'
__description__ = "This is a default cgm gui example"
__author__ = 'Josh Burton'
__owner__ = 'CG Monks'
__website__ = 'www.cgmonks.com'
__defaultSize__ = 200, 300

#>>> From Maya =============================================================
import os
import maya.cmds as mc
import maya.mel as mel
import copy
import time
import pprint
import webbrowser

from cgm.core import cgm_General as cgmGEN
#reload(cgmGEN)
mayaVersion = cgmGEN.__mayaVersion__

# Maya version check
if mayaVersion >= 2011:
    currentGenUI = True
else:
    currentGenUI = False

    
#>>> From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import Red9.core.Red9_CoreUtils as r9Core

from Red9.core import Red9_General as r9General
    
#>>> From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib import (search,
                     guiFactory,
                     dictionary)

from cgm.core.lib.zoo import baseMelUI as mUI
from cgm.core.lib import name_utils as NAMES
from cgm.core.cgmPy import path_Utils as CGMPATH
import cgm.core.cgmPy.validateArgs as VALID 

import cgm.images as cgmImages
mImagesPath = CGMPATH.Path(cgmImages.__path__[0])
#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================


_str_popWindow = 'cgmMM'#...outside to push to killUI
class markingMenu(object):#mUI.BaseMelWindow
    POPWINDOW = _str_popWindow
    
    def __init__(self):	
        """
        Initializes the pop up menu class call
        """
        try:
            self._str_MM = self.__class__.__name__  
            
            log.debug(">>> %s "%(self._str_MM) + "="*75)          
            self.l_optionVars = []		
            self.create_guiOptionVar('clockStart', value = 0.0)  
            self._ui_parentPanel = None
            #>>>> Clock set
            #====================================================================
        
            self.var_clockStart.value = time.clock()
        
            #log.debug( mc.getPanel(withFocus=True)) 
            
            _p = mc.getPanel(withFocus=True)#mc.getPanel(up = True)
            if _p is None:
                log.debug("No panel detected...")
                return
                _p = mc.getPanel(withFocus=True)

            try:
                mc.popupMenu('cgmMM', edit = True, ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = _p, 
                             pmc = lambda *a: self.createUI(),
                             postMenuCommandOnce=True)
                log.debug("|{0}| >> new mm...".format(self._str_MM))  
            except:
                mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0,mm = 1, b =1, aob = 1, p = _p,
                                                 pmc = lambda *a: self.createUI(),
                                                 postMenuCommandOnce=True)
                log.debug("|{0}| >> editing existing...".format(self._str_MM))
                
                

            return
            
            if _p == 'cat':
                log.debug("...panel under pointer {1}...".format(self._str_MM, _p))                    
                _parentPanel = mc.panel(_p,q = True,ctl = True)
                #self._ui_parentPanel = _parentPanel
                log.info("...panel parent: {1}...".format(self._str_MM,_parentPanel))
                if 'MayaWindow' in _parentPanel:
                    _p = 'viewPanes'   

            if not mc.control(_p, ex = True):
                return "{0} doesn't exist!".format(_p)
            else:
                """
                if mayaVersion == 2017:
                    log.warning("2017 Support mode. Must click twice. sSorry. Maya done messed it up.")
                    if not mc.popupMenu('cgmMM',ex = True):
                        mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0,mm = 1, b =1, aob = 1, p = _p,
                                     pmc = lambda *a: mc.evalDeferred(self.createUI,lp=True),                             
                                     postMenuCommandOnce=0)#postMenuCommandOnce=True
                    else:
                        log.info("|{0}| >> editing existing...".format(self._str_MM))  
                        mc.popupMenu('cgmMM', edit = True, ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = _p, 
                                     pmc = lambda *a: mc.evalDeferred(self.createUI,lp=True),                             
                                     postMenuCommandOnce=0)#dai = True,"""
                #else:
                if not mc.popupMenu('cgmMM',ex = True):
                    mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0,mm = 1, b =1, aob = 1, p = _p,
                                 pmc = lambda *a: self.createUI(),                             
                                 postMenuCommandOnce=True)#postMenuCommandOnce=True
                
                else:
                    log.info("|{0}| >> editing existing...".format(self._str_MM))  
                    mc.popupMenu('cgmMM', edit = True, ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = _p, 
                                 pmc = lambda *a: self.createUI(),                            
                                 postMenuCommandOnce=True)#dai = True,            
        except Exception,err:
            print Exception,err
        finally:
            mc.warning( "'{0}' Built. Click for pop up.".format(_str_popWindow))
        
    def createUI(self, parent = 'cgmMM'):
        log.info("|{0}| >> createUI...".format(self._str_MM))  
        #try:mc.menu(parent,e = True, deleteAllItems = True)
        #except Exception,err:
        #    log.error("Failed to delete menu items")
            #for a in err.args():
                #print a
                
        mc.menuItem('test',p = parent)
                
        
        mc.showWindow('cgmMM')
        
    def create_guiOptionVar(self,varName,*args,**kws):
        fullName = "cgmVar_%s_%s"%(self._str_MM ,varName)
        if args:args[0] = fullName
        if kws and 'varName' in kws.keys():kws.pop('varName')
        self.__dict__['var_%s'%varName] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        log.debug('var_%s'%varName)
        if fullName not in self.l_optionVars:
            self.l_optionVars.append(fullName)
        return fullName


def run():
    #cgmGUI().delete()
    win = cgmGUI()


def reloadUI(cls,window):
    #killChildren(window)
    #mc.deleteUI(window)
    #self.close()
    #del(self)
    return cls()
    
def reloadUI2(self):
    try:
        cls = self.__class__
        killChildren(self.WINDOW_NAME)
        self.close()
        del(self)
        return cls()
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def resetUI(cls,window,l_optionVars):
    do_resetGuiInstanceOptionVars(l_optionVars)
    #killChildren(window)

    return cls()
  
        
def getChildren(uiElement):
    l_ = []
    l_toCheck = []
    l_toCheck.extend( mc.lsUI(controls = True, l = True) )
    l_toCheck.extend( mc.lsUI(mi = True, l = True) )
    l_toCheck.extend( mc.lsUI(controlLayouts = True, l = True) )
    l_toCheck.extend( mc.lsUI(collection = True, l = True) )
    l_toCheck.extend( mc.lsUI(rmc = True, l = True) )
    l_toCheck.extend( mc.lsUI(menus = True, l = True) )
    l_toCheck.extend( mc.lsUI(contexts = True, l = True) )
    
    for c in l_toCheck:
        if  uiElement in c.split('|') and not str(c).endswith(uiElement):
            l_.append(c)  
            
    #pprint.pprint(l_)    
    return l_
                
def killChildren(uiElement):
    l_ = getChildren(uiElement)
       
    for c in l_:
        #log.info('deleting old ui: {0}'.format(c))
        try:mc.deleteUI(c)
        except Exception,err:log.debug('failed to delete: {0} | err: {1}'.format(c,err))     

if cgmGEN.__mayaVersion__ > 2016:
    _b_reload = False
else:
    _b_reload = True
    
l_thanksIntervals = [10, 25, 50, 100, 500, 1000]

def uiWindow_thanks(achieve = True):
    if achieve:
        _title = 'Thanks!'
        
        msg = "Achievement Unlocked! \n You've opened a cgm tool [{0}] times  \n since maya last lost its prefs. \n ... \n  Knock on wood. \n ... \n Here's a link to the docs if you've forgotten. \n Please consider supporting us :) \n Build: {1}".format(cgmMeta.cgmOptionVar('cgmVar_loadCount').value, cgmGEN.__RELEASE)
    else:
        _title = 'CGM'
        msg = "You've opened a cgm tool [{0}] times  \n since maya last lost its prefs. \n ... \n Build: {1}".format(cgmMeta.cgmOptionVar('cgmVar_loadCount').value, cgmGEN.__RELEASE)
    
    window = mc.window( title=_title, iconName='About', ut = 'cgmUITemplate',resizeToFitChildren=True)
    column = mUI.MelColumnLayout( window , ut = 'cgmUISubTemplate')
    
    _imageFailPath = os.path.join(mImagesPath.asFriendly(),'cgm_project.png')
    imageRow = mUI.MelHRowLayout(column,bgc=[0,0,0])
    
    #mUI.MelSpacer(imageRow,w=10)
    uiImage_ProjectRow = imageRow
    uiImage_Project= mUI.MelImage(imageRow,w=350, h=50)
    uiImage_Project.setImage(_imageFailPath)    
        
       
    
    mUI.MelLabel(column, label=msg, ut = 'cgmUISubTemplate', h =125)
    mUI.MelSpacer(column, h=10 )
    
    mc.button(parent = column,
              ut = 'cgmUITemplate',
              l='Basic Docs',
              ann = "Basic cgmDocs",
              c=lambda *a: webbrowser.open("http://docs.cgmonks.com/index.html"))    
    mc.button(parent = column,
              ut = 'cgmUITemplate',
              l='MRS Docs',
              ann = "MRS Docs",
              c=lambda *a: webbrowser.open("http://mrsdocs.cgmonastery.com/"))    
    mc.button(parent = column,
              ut = 'cgmUITemplate',
              l='Support our Work',
              ann = "Support our work",
              c=lambda *a: webbrowser.open("https://www.patreon.com/mrsmakers"))
    
    
    
    """
    add_Button(column,'Basic Docs', 'import webbrowser;webbrowser.open(" http://docs.cgmonks.com/index.html")')
    add_Button(column,'MRS Docs', 'import webbrowser;webbrowser.open(" http://docs.cgmonks.com/index.html")')
    add_Button(column,'Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://docs.cgmonks.com/index.html")')
    add_Button(column,'Close', lambda *a: mc.deleteUI("{0}".format(window)))
    mc.setParent( '..' )"""
    
    _row_cgm = add_cgmFooter(column)            
    
    mc.showWindow( window )    
    

    



class cgmGUI(mUI.BaseMelWindow):
    """
    Base CG Monks core gui
    """
    #These feed to Hamish's basemel ui stuff
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmGUI'
    DEFAULT_SIZE = 200, 300
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created
    TOOLNAME = 'cgmGUI'
    WINDOW_TITLE = '%s - %s'%(TOOLNAME,__version__)    
    l_allowedDockAreas = ['right', 'left']
    
    def __init__( self,*a,**kw):
        try:
            _str_func = '__init__[{0}]'.format(self.__class__.TOOLNAME)
                    
            log.info("|{0}| >>...".format(_str_func))        
            
            #Check our tool option var for debug mode to set logger level if so
            if mc.optionVar(exists = "cgmVar_guiDebug") and mc.optionVar(q="cgmVar_guiDebug"):
                log.setLevel(logging.DEBUG)	
                
            #killChildren(self)
            #>>> Standard cgm variables
            #====================	    
            self.l_optionVars = []
            self.l_helpElements = []
            self.l_oldGenElements = []
            self.description = __description__
            self.initializeTemplates() 
            self.setup_baseVariables()	
            self.__toolName__ = 'cgmGUI'
            #>>> Insert our init, overloaded for other tools
            
            self.pg_maya = doStartMayaProgressBar(statusMessage='Building...')
            mc.progressBar(self.pg_maya,edit=True, status = '{0} | Init'.format(self.__toolName__),
                           progress = 2, maxValue= 10)
            
            self.insert_init(self,*a,**kw)
                
            #>>> Menu
            mc.progressBar(self.pg_maya,edit=True,status = '{0} | Menu'.format(self.__toolName__),
                           progress = 6, maxValue= 10)            
            self.build_menus()
    
            #>>> Body
            #====================
            mc.progressBar(self.pg_maya,edit=True,status = '{0} | Layout'.format(self.__toolName__),
                           progress = 8, maxValue= 10)                        
            self.build_layoutWrapper(self)
    
            #====================
            # Show and Dock
            #====================
            #Maya2011 QT docking - from Red9's examples
            #if mayaVersion == 2011:
            #'Maya2011 dock delete'
    
            #log.info(self.l_allowedDockAreas[self.var_DockSide.value])
            """_dock = '{0}Dock'.format(__toolName__)        
            self.uiDock =  mc.dockControl(_dock , area=self.l_allowedDockAreas[self.var_DockSide.value],
                                          label=self.WINDOW_TITLE, content=self.WINDOW_NAME,
                                          floating = self.var_Dock.value,
                                          allowedArea=self.l_allowedDockAreas,
                                          width=self.DEFAULT_SIZE[0], height = self.DEFAULT_HEIGHT)""" 
            
            
            _dock = '{0}Dock'.format(self.__toolName__)            
            if mc.dockControl(_dock, exists=True):
                log.info('Deleting {0}'.format(_dock))
                mc.deleteUI(_dock, control=True)   
            """    
            if self.var_Dock and self.var_Dock.value:
                try:
                    self.do_dock()
                except Exception,err:
                    log.error("|{0}| >> Failed to dock | err: {1}".format(_str_func,err)) 
            """    
            self.show()

            self.post_init(self,*a,**kw)
            
            self.var_uiLoadCount = cgmMeta.cgmOptionVar('cgmVar_loadCount', defaultValue = 1)
            self.var_uiLoadCount.value += 1
            if self.var_uiLoadCount.value in l_thanksIntervals:
                uiWindow_thanks()

        except Exception,err:cgmGEN.cgmException(Exception,err)
        finally:
            mc.progressBar(self.pg_maya, edit=True, endProgress=True)

    def insert_init(self,*args,**kws):
        """ This is meant to be overloaded per gui """
        _str_func = 'insert_init[{0}]'.format(self.__class__.TOOLNAME)            
        log.info("|{0}| >>...".format(_str_func))   
        
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        
        #log.info("WINDOW_NAME: '%s'"%cgmGUI.WINDOW_NAME)
        #log.info("WINDOW_TITLE: '%s'"%cgmGUI.WINDOW_TITLE)
        #log.info("DEFAULT_SIZE: %s"%str(cgmGUI.DEFAULT_SIZE))
        
        self.description = 'This is a series of tools for working with cgm Sets'
        self.__version__ = __version__
        self.__toolName__ = self.__class__.TOOLNAME		
        #self.l_allowedDockAreas = ['right', 'left']
        
        #self.WINDOW_NAME = cgmGUI.WINDOW_NAME
        #self.WINDOW_TITLE = cgmGUI.WINDOW_TITLE
        #self.DEFAULT_SIZE = cgmGUI.DEFAULT_SIZE
    
    def post_init(self,*args,**kws):
        """ This is meant to be overloaded per gui """
        _str_func = 'post_init[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))

    def setup_baseVariables(self):
        _str_func = 'setup_baseVariables[{0}]'.format(self.__class__.TOOLNAME)            
        log.info("|{0}| >>...".format(_str_func)) 
        self.create_guiOptionVar('ShowHelp',defaultValue = 0)
        self.create_guiOptionVar('Dock',defaultValue = 0)
        self.create_guiOptionVar('DockSide',defaultValue = 0)	
        self.create_cgmDebugOptionVar(defaultValue = 0)
        

    def create_guiOptionVar(self,varName,*args,**kws):
        fullName = "cgmVar_%s%s"%(self.__class__.TOOLNAME,varName)
        if args:args[0] = fullName
        if kws and 'varName' in kws.keys():kws.pop('varName')
        self.__dict__['var_%s'%varName] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        log.debug('var_%s'%varName)
        if fullName not in self.l_optionVars:
            self.l_optionVars.append(fullName)
        return fullName

    def create_cgmDebugOptionVar(self,*args,**kws):
        fullName = "cgmVar_guiDebug"
        self.__dict__['var_DebugMode'] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        if fullName not in self.l_optionVars:
            self.l_optionVars.append(fullName)
            
    def set_optionVar(self, optionVar, value = None, uiObject = None):
        if uiObject is not None:
            value = uiObject.getValue()
        optionVar.setValue(value)
        
    #=========================================================================
    # Menu Building
    #=========================================================================
    def build_menus(self):
        _str_func = 'build_menus[{0}]'.format(self.__class__.TOOLNAME)            
        log.info("|{0}| >>...".format(_str_func))   
        
        self.uiMenu_FirstMenu = mUI.MelMenu( l='Root', pmc=self.buildMenu_first)		        
        self.uiMenu_OptionsMenu = mUI.MelMenu( l='Options', pmc=self.buildMenu_options)		
        self.uiMenu_HelpMenu = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)   

    def buildMenu_first( self, *args):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )
        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         #en = _b_reload,
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
                         #c=cgmGEN.Callback(reloadUI,self.__class__,self.WINDOW_NAME))
                         #c=lambda *a: reloadUI(self.__class__,self.WINDOW_NAME))		
                
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         #en = _b_reload,
                         #c = cgmGEN.Callback(resetUI(str(self.WINDOW_NAME))))
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))                         
                         #c=cgmGEN.Callback( resetUI,self.__class__, self.WINDOW_NAME, self.l_optionVars))                         
                         #c=lambda *a: resetUI(self.__class__, self.WINDOW_NAME, self.l_optionVars))    

    def buildMenu_options( self, *args):
        self.uiMenu_OptionsMenu.clear()
        #>>> Reset Options				
        mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Dock",
                         c = lambda *a:mc.evalDeferred(self.do_dock,lp=True))                         

    def buildMenu_help( self, *args):
        self.uiMenu_HelpMenu.clear()
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Show Help",
                         cb=self.var_ShowHelp.value,
                         c = lambda *a:mc.evalDeferred(self.do_showHelpToggle,lp=True))                         

        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Print Tools Help",
                         c=lambda *a: log_selfReport(self) )
        mUI.MelMenuItemDiv( self.uiMenu_HelpMenu )
        
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Log Self",
                         c=lambda *a: log_selfReport(self) )
        
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Thanks",
                         c=lambda *a: uiWindow_thanks() )        

        # Update Mode
        iMenu_loggerMaster = mUI.MelMenuItem( self.uiMenu_HelpMenu, l='Logger Level', subMenu=True)
        mUI.MelMenuItem( iMenu_loggerMaster, l='Info',
                         c = lambda *a:mc.evalDeferred(self.set_loggingInfo,lp=True))                         
                         
        mUI.MelMenuItem( iMenu_loggerMaster, l='Debug',
                         c = lambda *a:mc.evalDeferred(self.set_loggingDebug,lp=True))                         
                         

    def set_loggingInfo(self):
        self.var_DebugMode.value = 0
        log.setLevel(logging.INFO)
        
    def set_loggingDebug(self):
        self.var_DebugMode.value = 1
        log.setLevel(logging.DEBUG)    

    #>> Menu Functions
    #=========================================================================    
    def reset(self):
        do_resetGuiInstanceOptionVars(self.l_optionVars)
        self.__class__()
        #Callback(do_resetGuiInstanceOptionVars,self.l_optionVars,run).__call__()
        #reloadUI(self)
        #self.close()
        #self.build_layoutWrapper(self)
        #reloadGUI(self)
        #run()

    def reload(self):
        _str_func = 'reload[{0}]'.format(self.__toolName__)            
        log.debug("|{0}| >> reload".format(_str_func))
        self.__class__()
        #killChildren(self.WINDOW_NAME)
        #reloadUI(self)
        #reloadGUI(self)
        #self.build_layoutWrapper(self)
        #self.close()
        #run()
        #cgmGUI()
        #self.delete()
        #run()
                   
    def do_dock( self):
        _str_func = 'do_dock'
        #log.info("dockCnt: {0}".format(self.dockCnt))
        #log.debug("uiDock: {0}".format(self.uiDock))                
        #log.debug("area: {0}".format(self.l_allowedDockAreas[self.var_DockSide.value]))
        #log.debug("label: {0}".format(self.WINDOW_TITLE))
        #log.debug("self: {0}".format(self.Get()))                
        #log.debug("content: {0}".format(self.WINDOW_NAME))
        #log.debug("floating: {0}".format(not self.var_Dock.value))
        #log.debug("allowedArea: {0}".format(self.l_allowedDockAreas))
        #log.debug("width: {0}".format(self.DEFAULT_SIZE[0])) 
        try:
            self.uiDock
        except:
            log.debug("|{0}| >> making uiDock attr".format(_str_func)) 
            self.uiDock = False
            
        _dock = '{0}Dock'.format(self.__toolName__)   
        _l_allowed = self.__class__.l_allowedDockAreas
        
  
        _content = self.Get()
            
        if mc.dockControl(_dock,q=True, exists = True):
            log.debug('linking...')
            self.uiDock = _dock
            mc.dockControl(_dock , edit = True, area=_l_allowed[self.var_DockSide.value],
                           label=self.WINDOW_TITLE, content=_content,
                           allowedArea=_l_allowed,
                           width=self.DEFAULT_SIZE[0], height = self.DEFAULT_SIZE[1])                    
        #else:
        else:
            log.debug('creating...')       
            mc.dockControl(_dock , area=_l_allowed[self.var_DockSide.value],
                           label=self.WINDOW_TITLE, content=_content,
                           allowedArea=_l_allowed,
                           width=self.DEFAULT_SIZE[0], height = self.DEFAULT_SIZE[1]) 
            self.uiDock = _dock
        
        
        """log.info("floating: {0}".format(mc.dockControl(_dock, q = True, floating = True)))
        log.info("var_Doc: {0}".format(self.var_Dock.value))
        _floating = mc.dockControl(_dock, q = True, floating = True)
        if _floating and self.var_Dock == 1:
            log.info('mismatch')
            self.var_Dock = 0
        if not _floating and self.var_Dock == 0:
            log.info("mismatch2")
            self.var_Dock = 1"""
        
        mc.dockControl(_dock, edit = True, floating = self.var_Dock.value, width=self.DEFAULT_SIZE[0], height = self.DEFAULT_SIZE[1])
        self.uiDock = _dock   
        _floating = mc.dockControl(_dock, q = True, floating = True)            
        if _floating:
            #log.info("Not visible, resetting position.")
            #mc.dockControl(self.uiDock, e=True, visible = False)
            mc.window(_dock, edit = True, tlc = [200, 200])
        self.var_Dock.toggle()
                

    def do_showHelpToggle( self):
        doToggleInstancedUIItemsShowState(self.var_ShowHelp.value,self.l_helpElements)
        self.var_ShowHelp.toggle()

    def do_DebugModeToggle( self):
        self.var_DebugMode.toggle()	
        if self.var_DebugMode.value:
            log.setLevel(logging.DEBUG)	
            #self.log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
            #self.log.setLevel(logging.INFO)

    def do_DebugEchoTest(self):
        log.info('#'+'='*25)
        log.info('Tool: %s'%self.__toolName__)	
        log.info("Info call")
        log.debug("Debug call")
        log.warning("warning call")


    #=========================================================================
    # Layouts
    #=========================================================================
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        def modeSet( item ):
            i =  self.setModes.index(item)
            self.SetToolsModeOptionVar.set( i )
            self.setMode = i

        MainForm = mUI.MelColumnLayout(parent)
        SetHeader = add_Header('HI')
        
        #self.uiROW_pb = mUI.MelHRowLayout(parent,vis=False)
        #self.uiROW_pb.layout()
        #progressBar_start('cgmUITESTProgressBar',hidden = True)

        self.l_helpElements.extend(add_InstructionBlock(MainForm,"Purge all traces of cgmThinga tools from the object and so and so forth forever, amen.",vis = self.var_ShowHelp.value))        
        add_Button(MainForm)
        add_Button(MainForm,'Debug test', lambda *a: self.do_DebugEchoTest())
        add_Button(MainForm,'Debug test 2', lambda *a: self.do_DebugEchoTest())
        add_Button(MainForm,'Progress bar', lambda *a: progressBar_test(self.uiPB_test))
        self.uiPB_test = mc.progressBar(vis=False)
        
        add_Button(MainForm,'Maya Progress bar', lambda *a: progressBar_test())
        
        
        #add_Button(MainForm,'Reset', lambda *a: resetUI(self))
        #add_Button(MainForm,'Reload', lambda *a: reloadUI(self))
        #add_Button(MainForm,'module Reload', lambda *a: reloadUI(self))
        
        mc.melInfo(p=MainForm,label ='asdf!')

    def initializeTemplates(self):
        initializeTemplates()
        return
        guiBackgroundColor = [.45,.45,.45]
        guiTextFieldColor = [.4,.4,.4]    
        guiHeaderColor = [.25,.25,.25]
        guiSubMenuColor = [.65,.65,.65]
        guiButtonColor = [.35,.35,.35]
        guiHelpBackgroundColor = [0.8, 0.8, 0.8]
        guiHelpBackgroundReservedColor = [0.411765 , 0.411765 , 0.411765]
        guiHelpBackgroundLockedColor = [0.837, 0.399528, 0.01674]

        if mc.uiTemplate( 'cgmUITemplate', exists=True ):
            mc.deleteUI( 'cgmUITemplate', uiTemplate=True )
        mc.uiTemplate('cgmUITemplate')
        mc.separator(dt='cgmUITemplate', height = 10, style = 'none')
        mc.button(dt = 'cgmUITemplate', height = 15, backgroundColor = guiButtonColor,align = 'center')
        mc.window(dt = 'cgmUITemplate', backgroundColor = guiBackgroundColor)
        mc.optionMenu(dt='cgmUITemplate',backgroundColor = guiButtonColor)
        mc.optionMenuGrp(dt ='cgmUITemplate', backgroundColor = guiButtonColor)
        mc.textField(dt = 'cgmUITemplate',backgroundColor = [1,1,1],h=20)
        mc.formLayout(dt='cgmUITemplate', backgroundColor = guiBackgroundColor)    
        mc.textScrollList(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 
        mc.frameLayout(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 

        # Define our header template
        if mc.uiTemplate( 'cgmUIHeaderTemplate', exists=True ):
            mc.deleteUI( 'cgmUIHeaderTemplate', uiTemplate=True )
        mc.uiTemplate('cgmUIHeaderTemplate')
        mc.text(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
        mc.separator(dt='cgmUIHeaderTemplate', height = 5, style = 'none',backgroundColor = guiHeaderColor)
        mc.formLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)    
        mc.rowLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
        mc.rowColumnLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
        mc.columnLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)  
        mc.textScrollList(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor) 
        mc.frameLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor) 

        # Define our sub template
        if mc.uiTemplate( 'cgmUISubTemplate', exists=True ):
            mc.deleteUI( 'cgmUISubTemplate', uiTemplate=True )
        mc.uiTemplate('cgmUISubTemplate')
        mc.formLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.text(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.separator(dt='cgmUISubTemplate', height = 2, style = 'none', backgroundColor = guiSubMenuColor)
        mc.rowLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.rowColumnLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.columnLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.scrollLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.textField(dt = 'cgmUISubTemplate',backgroundColor = [1,1,1],h=20)
        mc.textScrollList(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 
        mc.frameLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 


        # Define our instructional template
        if mc.uiTemplate( 'cgmUIInstructionsTemplate', exists=True ):
            mc.deleteUI( 'cgmUIInstructionsTemplate', uiTemplate=True )
        mc.uiTemplate('cgmUIInstructionsTemplate')
        mc.text(dt = 'cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
        mc.formLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)    
        mc.rowLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
        mc.rowColumnLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
        mc.columnLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)    
        mc.textField(dt = 'cgmUIInstructionsTemplate',backgroundColor = [1,1,1],h=20)
        mc.textScrollList(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor) 
        mc.frameLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor) 

        # Define our Reserved
        if mc.uiTemplate( 'cgmUIReservedTemplate', exists=True ):
            mc.deleteUI( 'cgmUIReservedTemplate', uiTemplate=True )
        mc.uiTemplate('cgmUIReservedTemplate')
        mc.textField(dt = 'cgmUIReservedTemplate', backgroundColor = guiTextFieldColor,h=20)
        mc.formLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)    
        mc.rowLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)
        mc.rowColumnLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)
        mc.columnLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)  
        mc.frameLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor) 

        # Define our Locked
        if mc.uiTemplate( 'cgmUILockedTemplate', exists=True ):
            mc.deleteUI( 'cgmUILockedTemplate', uiTemplate=True )
        mc.uiTemplate('cgmUILockedTemplate')
        mc.textField(dt = 'cgmUILockedTemplate', backgroundColor = guiHelpBackgroundLockedColor, h=20)
        mc.frameLayout(dt='cgmUILockedTemplate', backgroundColor = guiHelpBackgroundLockedColor) 




class cgmGUI2(mUI.BaseMelWindow):
    """
    Base CG Monks core gui
    """
    #These feed to Hamish's basemel ui stuff
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = __toolName__
    WINDOW_TITLE = '%s - %s'%(__toolName__,__version__)
    DEFAULT_SIZE = __defaultSize__
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created
 
    @cgmGEN.Timer
    def __init__( self,*args,**kws):
        #Check our tool option var for debug mode to set logger level if so
        if mc.optionVar(exists = "cgmVar_guiDebug") and mc.optionVar(q="cgmVar_guiDebug"):
            log.setLevel(logging.DEBUG)	
        self.uiDock = False
        self.var_Dock = False
  
        #>>> Standard cgm variables
        #====================	    
        self.l_optionVars = []
        self.l_helpElements = []
        self.l_oldGenElements = []
        self.description = __description__

        self.initializeTemplates() 
        

        #>>> Insert our init, overloaded for other tools
        self.insert_init(self,*args,**kws)
            
        #>>> Menu
        self.setup_baseVariables()	
        self.build_menus()

        #>>> Body
        #====================        
        self.build_layoutWrapper(self)
        self.show()

        #====================
        # Show and Dock
        #====================
        #Maya2011 QT docking - from Red9's examples
        #if mayaVersion == 2011:
        #'Maya2011 dock delete'

            
        #log.info(self.l_allowedDockAreas[self.var_DockSide.value])
        """_dock = '{0}Dock'.format(__toolName__)        
        self.uiDock =  mc.dockControl(_dock , area=self.l_allowedDockAreas[self.var_DockSide.value],
                                      label=self.WINDOW_TITLE, content=self.WINDOW_NAME,
                                      floating = self.var_Dock.value,
                                      allowedArea=self.l_allowedDockAreas,
                                      width=self.DEFAULT_SIZE[0], height = self.DEFAULT_HEIGHT)""" 
        
        """
        _dock = '{0}Dock'.format(self.__toolName__)            
        if mc.dockControl(_dock, exists=True):
            log.info('Deleting {0}'.format(_dock))
            mc.deleteUI(_dock, control=True)   
            
        if self.var_Dock and self.var_Dock.value:
            self.do_dock()"""
            

    def insert_init(self,*args,**kws):
        """ This is meant to be overloaded per gui """
        log.debug(">>> cgmGUI.__init__")	
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        log.debug(self.__call__(q=True, title=True))
        log.info("WINDOW_NAME: '%s'"%cgmGUI.WINDOW_NAME)
        log.info("WINDOW_TITLE: '%s'"%cgmGUI.WINDOW_TITLE)
        log.info("DEFAULT_SIZE: %s"%str(cgmGUI.DEFAULT_SIZE))
        self.description = 'This is a series of tools for working with cgm Sets'
        self.__version__ = __version__
        self.__toolName__ = __toolName__		
        self.l_allowedDockAreas = ['right', 'left']
        self.WINDOW_NAME = cgmGUI.WINDOW_NAME
        self.WINDOW_TITLE = cgmGUI.WINDOW_TITLE
        self.DEFAULT_SIZE = cgmGUI.DEFAULT_SIZE
        
        self.setup_baseVariables()	
        self.build_menus()        

    def setup_Variables(self):
        self.create_guiOptionVar('ShowHelp',defaultValue = 0)
        self.create_guiOptionVar('Dock',defaultValue = 0)
        self.create_guiOptionVar('DockSide',defaultValue = 0)	
        self.create_cgmDebugOptionVar(defaultValue = 0)

    def create_guiOptionVar(self,varName,*args,**kws):
        fullName = "cgmVar_%s%s"%(self.__toolName__,varName)
        if args:args[0] = fullName
        if kws and 'varName' in kws.keys():kws.pop('varName')
        self.__dict__['var_%s'%varName] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        log.debug('var_%s'%varName)
        if fullName not in self.l_optionVars:
            self.l_optionVars.append(fullName)
        return fullName

    def create_cgmDebugOptionVar(self,*args,**kws):
        fullName = "cgmVar_guiDebug"
        self.__dict__['var_DebugMode'] = cgmMeta.cgmOptionVar(varName = fullName, *args,**kws)
        if fullName not in self.l_optionVars:
            self.l_optionVars.append(fullName)
    #=========================================================================
    # Menu Building
    #=========================================================================
    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu( l='Root', pmc=self.buildMenu_first)		        
        self.uiMenu_OptionsMenu = mUI.MelMenu( l='Options', pmc=self.buildMenu_options)		
        self.uiMenu_HelpMenu = mUI.MelMenu( l='Help', pmc=self.buildMenu_help)   

    def buildMenu_first( self, *args):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c=lambda *a: self.reload())		
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c=lambda *a: self.reset())    

    def buildMenu_options( self, *args):
        self.uiMenu_OptionsMenu.clear()
        #>>> Reset Options				
        mUI.MelMenuItem( self.uiMenu_OptionsMenu, l="Dock",
                         c= lambda *a: self.do_dock())	         

    def buildMenu_help( self, *args):
        self.uiMenu_HelpMenu.clear()
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Show Help",
                         cb=self.var_ShowHelp.value,
                         c= lambda *a: self.do_showHelpToggle())

        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Print Tools Help",
                         c=lambda *a: self.printHelp() )
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="Log Self",
                         c=lambda *a: log_selfReport(self) )
        mUI.MelMenuItemDiv( self.uiMenu_HelpMenu )
        mUI.MelMenuItem( self.uiMenu_HelpMenu, l="About",
                         c=lambda *a: self.showAbout() )

        # Update Mode
        iMenu_loggerMaster = mUI.MelMenuItem( self.uiMenu_HelpMenu, l='Logger Level', subMenu=True)
        mUI.MelMenuItem( iMenu_loggerMaster, l='Info',
                         c=lambda *a: self.set_loggingInfo())
        mUI.MelMenuItem( iMenu_loggerMaster, l='Debug',
                         c=lambda *a: self.set_loggingDebug())

    def set_loggingInfo(self):
        self.var_DebugMode.value = 0
        log.setLevel(logging.INFO)
    def set_loggingDebug(self):
        self.var_DebugMode.value = 1
        log.setLevel(logging.DEBUG)    

    #>> Menu Functions
    #=========================================================================    
    def reset(self):	
        mUI.Callback(do_resetGuiInstanceOptionVars(self.l_optionVars,run))

    def reload(self):	
        run()
                   
    def do_dock( self):
        try:
            #log.info("dockCnt: {0}".format(self.dockCnt))
            log.debug("uiDock: {0}".format(self.uiDock))                
            log.debug("area: {0}".format(self.l_allowedDockAreas[self.var_DockSide.value]))
            log.debug("label: {0}".format(self.WINDOW_TITLE))
            log.debug("self: {0}".format(self.Get()))                
            log.debug("content: {0}".format(self.WINDOW_NAME))
            log.debug("floating: {0}".format(not self.var_Dock.value))
            log.debug("allowedArea: {0}".format(self.l_allowedDockAreas))
            log.debug("width: {0}".format(self.DEFAULT_SIZE[0])) 
            
            _dock = '{0}Dock'.format(self.__toolName__)   
            if mc.dockControl(_dock,q=True, exists = True):
                log.debug('linking...')
                self.uiDock = _dock
                mc.dockControl(_dock , edit = True, area=self.l_allowedDockAreas[self.var_DockSide.value],
                               label=self.WINDOW_TITLE, content=self.Get(),
                               allowedArea=self.l_allowedDockAreas,
                               width=self.DEFAULT_SIZE[0], height = self.DEFAULT_SIZE[1])                    
            #else:
            else:
                log.debug('creating...')       
                mc.dockControl(_dock , area=self.l_allowedDockAreas[self.var_DockSide.value],
                               label=self.WINDOW_TITLE, content=self.Get(),
                               allowedArea=self.l_allowedDockAreas,
                               width=self.DEFAULT_SIZE[0], height = self.DEFAULT_SIZE[1])                
            
            
            """log.info("floating: {0}".format(mc.dockControl(_dock, q = True, floating = True)))
            log.info("var_Doc: {0}".format(self.var_Dock.value))
            _floating = mc.dockControl(_dock, q = True, floating = True)
            if _floating and self.var_Dock == 1:
                log.info('mismatch')
                self.var_Dock = 0
            if not _floating and self.var_Dock == 0:
                log.info("mismatch2")
                self.var_Dock = 1"""
            
            mc.dockControl(_dock, edit = True, floating = self.var_Dock.value, width=self.DEFAULT_SIZE[0], height = self.DEFAULT_SIZE[1])
            self.uiDock = _dock   
            _floating = mc.dockControl(_dock, q = True, floating = True)            
            if _floating:
                #log.info("Not visible, resetting position.")
                #mc.dockControl(self.uiDock, e=True, visible = False)
                mc.window(_dock, edit = True, tlc = [200, 200])
            self.var_Dock.toggle()
                
        except Exception,err:
            log.error("Failed to dock: {0}".format(err))

    def do_showHelpToggle( self):
        doToggleInstancedUIItemsShowState(self.var_ShowHelp.value,self.l_helpElements)
        self.var_ShowHelp.toggle()

    def do_DebugModeToggle( self):
        self.var_DebugMode.toggle()	
        if self.var_DebugMode.value:
            log.setLevel(logging.DEBUG)	
            #self.log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
            #self.log.setLevel(logging.INFO)

    def showAbout(self):
        window = mc.window( title="About", iconName='About', ut = 'cgmUITemplate',resizeToFitChildren=True)
        column = mc.columnLayout( adjustableColumn=True )
        add_Header(self.__toolName__,overrideUpper = True)
        mc.text(label='>>>A Part of the cgmTools Collection<<<', ut = 'cgmUIInstructionsTemplate')
        add_HeaderBreak()

        add_TextBlock(self.description)

        add_LineBreak()
        mc.text(label=('%s%s' %('Written by: ',__author__)))
        mc.text(label=('%s%s%s' %('Copyright ',__owner__,', 2011 - 2016')))
        add_LineBreak()
        mc.text(label='Version: %s' % self.__version__)
        mc.text(label='')
        add_Button(column,'Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://docs.cgmonks.com/index.html")')
        add_Button(column,'Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
        mc.setParent( '..' )
        mc.showWindow( window )

    def printHelp(self):pass
        #help(morphyMakerLib)

    def do_DebugEchoTest(self):
        log.info('#'+'='*25)
        log.info('Tool: %s'%self.__toolName__)	
        log.info("Info call")
        log.debug("Debug call")
        log.warning("warning call")


    #=========================================================================
    # Layouts
    #=========================================================================
    def build_layoutWrapper(self,parent):
        def modeSet( item ):
            i =  self.setModes.index(item)
            self.SetToolsModeOptionVar.set( i )
            self.setMode = i

        MainForm = mUI.MelColumnLayout(parent)
        SetHeader = add_Header('HI')

        self.l_helpElements.extend(add_InstructionBlock(MainForm,"Purge all traces of cgmThinga tools from the object and so and so forth forever, amen.",vis = self.var_ShowHelp.value))        
        add_Button(MainForm)
        add_Button(MainForm,'Debug test', lambda *a: self.do_DebugEchoTest())
        add_MelLabel(MainForm,'asdfasdfasdf')

    def initializeTemplates(self):
        guiBackgroundColor = [.45,.45,.45]
        guiTextFieldColor = [.4,.4,.4]    
        guiHeaderColor = [.25,.25,.25]
        guiSubMenuColor = [.65,.65,.65]
        guiButtonColor = [.35,.35,.35]
        guiHelpBackgroundColor = [0.8, 0.8, 0.8]
        guiHelpBackgroundReservedColor = [0.411765 , 0.411765 , 0.411765]
        guiHelpBackgroundLockedColor = [0.837, 0.399528, 0.01674]

        if mc.uiTemplate( 'cgmUITemplate', exists=True ):
            mc.deleteUI( 'cgmUITemplate', uiTemplate=True )
        mc.uiTemplate('cgmUITemplate')
        mc.separator(dt='cgmUITemplate', height = 10, style = 'none')
        mc.button(dt = 'cgmUITemplate', height = 15, backgroundColor = guiButtonColor,align = 'center')
        mc.window(dt = 'cgmUITemplate', backgroundColor = guiBackgroundColor)
        mc.optionMenu(dt='cgmUITemplate',backgroundColor = guiButtonColor)
        mc.optionMenuGrp(dt ='cgmUITemplate', backgroundColor = guiButtonColor)
        mc.textField(dt = 'cgmUITemplate',backgroundColor = [1,1,1],h=20)
        mc.formLayout(dt='cgmUITemplate', backgroundColor = guiBackgroundColor)    
        mc.textScrollList(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 
        mc.frameLayout(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 

        # Define our header template
        if mc.uiTemplate( 'cgmUIHeaderTemplate', exists=True ):
            mc.deleteUI( 'cgmUIHeaderTemplate', uiTemplate=True )
        mc.uiTemplate('cgmUIHeaderTemplate')
        mc.text(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
        mc.separator(dt='cgmUIHeaderTemplate', height = 5, style = 'none',backgroundColor = guiHeaderColor)
        mc.formLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)    
        mc.rowLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
        mc.rowColumnLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
        mc.columnLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)  
        mc.textScrollList(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor) 
        mc.frameLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor) 

        # Define our sub template
        if mc.uiTemplate( 'cgmUISubTemplate', exists=True ):
            mc.deleteUI( 'cgmUISubTemplate', uiTemplate=True )
        mc.uiTemplate('cgmUISubTemplate')
        mc.formLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.text(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.separator(dt='cgmUISubTemplate', height = 2, style = 'none', backgroundColor = guiSubMenuColor)
        mc.rowLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.rowColumnLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.columnLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.scrollLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
        mc.textField(dt = 'cgmUISubTemplate',backgroundColor = [1,1,1],h=20)
        mc.textScrollList(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 
        mc.frameLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 


        # Define our instructional template
        if mc.uiTemplate( 'cgmUIInstructionsTemplate', exists=True ):
            mc.deleteUI( 'cgmUIInstructionsTemplate', uiTemplate=True )
        mc.uiTemplate('cgmUIInstructionsTemplate')
        mc.text(dt = 'cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
        mc.formLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)    
        mc.rowLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
        mc.rowColumnLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
        mc.columnLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)    
        mc.textField(dt = 'cgmUIInstructionsTemplate',backgroundColor = [1,1,1],h=20)
        mc.textScrollList(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor) 
        mc.frameLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor) 

        # Define our Reserved
        if mc.uiTemplate( 'cgmUIReservedTemplate', exists=True ):
            mc.deleteUI( 'cgmUIReservedTemplate', uiTemplate=True )
        mc.uiTemplate('cgmUIReservedTemplate')
        mc.textField(dt = 'cgmUIReservedTemplate', backgroundColor = guiTextFieldColor,h=20)
        mc.formLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)    
        mc.rowLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)
        mc.rowColumnLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)
        mc.columnLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)  
        mc.frameLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor) 

        # Define our Locked
        if mc.uiTemplate( 'cgmUILockedTemplate', exists=True ):
            mc.deleteUI( 'cgmUILockedTemplate', uiTemplate=True )
        mc.uiTemplate('cgmUILockedTemplate')
        mc.textField(dt = 'cgmUILockedTemplate', backgroundColor = guiHelpBackgroundLockedColor, h=20)
        mc.frameLayout(dt='cgmUILockedTemplate', backgroundColor = guiHelpBackgroundLockedColor) 


#=========================================================================
# Define our Colors
#=========================================================================
def setBGColorState(textFieldToChange, newState):
    mc.textField(textFieldToChange,edit = True, bgc = dictionary.returnStateColor(newState))
#=========================================================================
# Define our Templates
#=========================================================================
guiBackgroundColor = [.45,.45,.45]
guiTextFieldColor = [.4,.4,.4]    
guiHeaderColor = [.25,.25,.25]
guiSubMenuColor = [.65,.65,.65]
guiSubSubMenuColor = [.5,.5,.5]
guiButtonColor = [.35,.35,.35]
guiHelpBackgroundColor = [0.8, 0.8, 0.8]
guiBackgroundColorLight = [.85,.85,.85]
guiHelpBackgroundReservedColor = [0.411765 , 0.411765 , 0.411765]
guiHelpBackgroundLockedColor = [0.837, 0.399528, 0.01674]

def initializeTemplates():
    if mc.uiTemplate( 'cgmUITemplate', exists=True ):
        mc.deleteUI( 'cgmUITemplate', uiTemplate=True )
    mc.uiTemplate('cgmUITemplate')
    mc.separator(dt='cgmUITemplate', height = 10, style = 'none')
    mc.button(dt = 'cgmUITemplate', height = 20, backgroundColor = guiButtonColor,align = 'center')
    mc.window(dt = 'cgmUITemplate', backgroundColor = guiBackgroundColor)
    mc.optionMenu(dt='cgmUITemplate',backgroundColor = guiButtonColor)
    mc.optionMenuGrp(dt ='cgmUITemplate', backgroundColor = guiButtonColor)
    mc.textField(dt = 'cgmUITemplate',backgroundColor = [1,1,1],h=20)
    mc.formLayout(dt='cgmUITemplate', backgroundColor = guiBackgroundColor)    
    mc.textScrollList(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 
    mc.frameLayout(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 
    mc.tabLayout(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 
    mc.text(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 

    # Define our header template
    if mc.uiTemplate( 'cgmUIHeaderTemplate', exists=True ):
        mc.deleteUI( 'cgmUIHeaderTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUIHeaderTemplate')
    mc.text(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
    mc.separator(dt='cgmUIHeaderTemplate', height = 5, style = 'none',backgroundColor = guiHeaderColor)
    mc.formLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)    
    mc.rowLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
    mc.rowColumnLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
    mc.columnLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)  
    mc.textScrollList(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor) 
    mc.frameLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor) 
    mc.textField(dt = 'cgmUIHeaderTemplate',backgroundColor = [1,1,1],h=20)
    mc.text(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor) 

    # Define our sub template
    if mc.uiTemplate( 'cgmUISubTemplate', exists=True ):
        mc.deleteUI( 'cgmUISubTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUISubTemplate')
    mc.formLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.text(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.separator(dt='cgmUISubTemplate', height = 2, style = 'none', backgroundColor = guiSubMenuColor)
    mc.rowLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.rowColumnLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.columnLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.scrollLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.textField(dt = 'cgmUISubTemplate',backgroundColor = [1,1,1],h=20)
    mc.textScrollList(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 
    mc.frameLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 
    mc.tabLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 
    mc.text(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 


    # Define our instructional template
    if mc.uiTemplate( 'cgmUIInstructionsTemplate', exists=True ):
        mc.deleteUI( 'cgmUIInstructionsTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUIInstructionsTemplate')
    mc.text(dt = 'cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
    mc.formLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)    
    mc.rowLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
    mc.rowColumnLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
    mc.columnLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)    
    mc.textField(dt = 'cgmUIInstructionsTemplate',backgroundColor = [1,1,1],h=20)
    mc.textScrollList(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor) 
    mc.frameLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor) 

    # Define our Reserved
    if mc.uiTemplate( 'cgmUIReservedTemplate', exists=True ):
        mc.deleteUI( 'cgmUIReservedTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUIReservedTemplate')
    mc.textField(dt = 'cgmUIReservedTemplate', backgroundColor = guiTextFieldColor,h=20)
    mc.formLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)    
    mc.rowLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)
    mc.rowColumnLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)
    mc.columnLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)  
    mc.frameLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor) 
    mc.text(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor) 

    # Define our Locked
    if mc.uiTemplate( 'cgmUILockedTemplate', exists=True ):
        mc.deleteUI( 'cgmUILockedTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUILockedTemplate')
    mc.textField(dt = 'cgmUILockedTemplate', backgroundColor = guiHelpBackgroundLockedColor, h=20)
    mc.frameLayout(dt='cgmUILockedTemplate', backgroundColor = guiHelpBackgroundLockedColor) 
    mc.text(dt='cgmUILockedTemplate', backgroundColor = guiHelpBackgroundLockedColor) 

#=========================================================================
# OptionVars
#=========================================================================
def do_resetGuiInstanceOptionVars(optionVarHolder,commandToRun = False):
    if optionVarHolder:
        do_purgeOptionVars(optionVarHolder)
    if commandToRun:    
        commandToRun()

def do_purgeOptionVars(varHolder):
    """
    Typically self.l_optionVars
    """
    sceneOptionVars = mc.optionVar(list=True)
    if varHolder:
        for var in varHolder:
            if var in sceneOptionVars:
                do_purgeOptionVar(var)

def do_purgeOptionVar(varName):
    if mc.optionVar(exists = varName):    
        mc.optionVar( remove=varName )
        print "'%s' removed"%varName
        return True
    return False
#=========================================================================
# Standard Layout stuff
#=========================================================================
def add_Button(parent, labelText = 'text', commandText = 'mc.warning("Fix this")',annotationText = '',*a,**kw):
    if currentGenUI:
        return 	mUI.MelButton(parent,l=labelText,ut = 'cgmUITemplate',
                                     c= commandText,
                                     height = 20,
                                     align = 'center',
                                     annotation = annotationText,*a,**kw)
    else:
        return mUI.MelButton(parent,l=labelText, backgroundColor = [.75,.75,.75],
                             c= commandText,
                             height = 20,
                             align = 'center',
                             annotation = annotationText,*a,**kw)

def add_Header(text = 'test', align = 'center',overrideUpper = False):
    if not overrideUpper:
        text = text.upper()
    if currentGenUI:
        return mc.text(text, al = align, ut = 'cgmUIHeaderTemplate')
    else:
        return mc.text(('%s%s%s' %('>>> ',text,' <<<')), al = align)

def add_HeaderBreak():
    if currentGenUI:
        return mc.separator(ut='cgmUIHeaderTemplate')
    else:
        return mc.separator(style='double')

def add_LineBreak():
    if currentGenUI:
        return mc.separator(ut='cgmUITemplate')
    else:
        return mc.separator(ut='cgmUITemplate')

def add_LineSubBreak(vis=True):
    if currentGenUI:
        return mc.separator(ut='cgmUISubTemplate',vis=vis)
    else:
        return mc.separator(style='single',vis=vis)

def add_SectionBreak():
    if currentGenUI:
        return mc.separator(ut='cgmUISubTemplate')
    else:
        return mc.separator(style='single')

def add_CheckBox(self,parent,optionVarName,*a,**kw):
    fullName = self.create_guiOptionVar(optionVarName)    

    return mUI.MelCheckBox(parent,
                           v = mc.optionVar(q=fullName),
                           onCommand = lambda *a: mc.optionVar(iv=(fullName,1)),
                           offCommand = lambda *a: mc.optionVar(iv=(fullName,0)),
                           *a,**kw)

def add_MelLabel(parent,text,**kws):
    return mUI.MelLabel(parent,label = text,ut = 'cgmUIInstructionsTemplate',al = 'center', ww = True,**kws)

def add_InstructionBlock(parent,text, align = 'center', vis = False, maxLineLength = 35, **kws):
    # yay, accounting for word wrap...
    if currentGenUI:
        return [mUI.MelLabel(parent,label= text, ut = 'cgmUIInstructionsTemplate',al = 'center', ww = True, visible = vis,**kws)]

    else:
        instructions = []
        textLines = return_SplitLines(text, maxLineLength)
        instructions.append(mUI.MelSeparator(parent,style='single', visible = vis))
        for line in textLines:
            instructions.append(mUI.MelLabel(parent,label = line, h = 15, al = align, visible = vis))
        instructions.append(mUI.MelSeparator(parent,style='single', visible = vis))

        return instruction

def add_InstructionBlockOLD(text, align = 'center', vis = False, maxLineLength = 35):

    # yay, accounting for word wrap...
    if currentGenUI:
        return [mc.text(text, ut = 'cgmUIInstructionsTemplate',al = 'center', ww = True, visible = vis)]

    else:
        instructions = []
        textLines = return_SplitLines(text, maxLineLength)
        instructions.append(mc.separator(style='single', visible = vis))
        for line in textLines:
            instructions.append(mc.text(line, h = 15, al = align, visible = vis))
        instructions.append(mc.separator(style='single', visible = vis))

        return instructions

def add_TextBlock(text, align = 'center'):
    # yay, accounting for word wrap...
    if currentGenUI:
        return [mc.text(text,al = 'center', ww = True, visible = True)]
    else:
        textBlock = []
        textLines = return_SplitLines(text, 50)
        textBlock.append(mc.separator(style = 'single', visible = True))
        for line in textLines:
            textBlock.append(mc.text(line, al = align, visible = True))
        textBlock.append(mc.separator(style = 'single', visible = True))
        return textBlock

def add_cgmFooter(parent = False):
    from cgm import images as cgmImagesFolder
    
    _row_cgm = mUI.MelHRowLayout(parent, bgc = [.20,.20,.20], h = 20)
    try:
        _path_imageFolder = CGMPATH.Path(cgmImagesFolder.__file__).up().asFriendly()
        #_path_image = os.path.join(_path_imageFolder,'cgm_uiFooter_gray.png')
        _path_image = os.path.join(_path_imageFolder,'cgmonastery_uiFooter_gray.png')        
        mc.iconTextButton(style='iconOnly',image =_path_image,
                          c=lambda *a:(webbrowser.open("http://www.cgmonastery.com/")))  
                          #c=lambda *a:(webbrowser.open("http://docs.cgmonks.com/")))  
    except Exception,err:
        log.warning("Failed to add cgmFooter")
        for arg in err.args:
            log.error(arg)
    return _row_cgm

def add_cgMonaseryFooter(parent = False):
    from cgm import images as cgmImagesFolder
    
    _row_cgm = mUI.MelHRowLayout(parent, bgc = [.25,.25,.25], h = 20)
    try:
        _path_imageFolder = CGMPATH.Path(cgmImagesFolder.__file__).up().asFriendly()
        _path_image = os.path.join(_path_imageFolder,'cgmonastery_uiFooter_gray.png')
        mc.iconTextButton(style='iconOnly',image =_path_image,
                          c=lambda *a:(webbrowser.open("http://www.cgmonastery.com/")))  
    except Exception,err:
        log.warning("Failed to add cgmFooter")
        for arg in err.args:
            log.error(arg)
    return _row_cgm


def return_SplitLines(text, size):
    lineList = []
    wordsList = text.split(' ')
    baseCnt = 0
    cnt = 0
    max = len(wordsList)
    while cnt < max:
        buffer = ' '.join(wordsList[baseCnt:cnt + 1])
        if len(buffer) < size:
            cnt+=1
        else:
            baseCnt = cnt+1
            cnt = baseCnt
            lineList.append(buffer)
    if baseCnt < max:
        lineList.append(' '.join(wordsList[baseCnt:]))
    return lineList
#=========================================================================
# OptionVars
#=========================================================================
def doToggleInstancedUIItemsShowState(stateToggle,instanceList = None):
    newstate = not stateToggle
    for i_item in instanceList:
        try:
            i_item(edit = True, visible = newstate)
        except:
            log.warning("'%s' failed to doToggleInstancedUIItemsShowState"%i_item)
    return newstate

def doSetInstancedUIItemsEnableState(state = None,instanceList = None):
    if state is None:
        log.warning("'%s' not a valid argument for doSetInstancedUIItemsEnableState"%str(state))	
        return 
    for i_item in instanceList:
        try:
            i_item(edit = True, enable = state)
        except:
            log.warning("'%s' failed to doSetInstancedUIItemsEnableState"%i_item)
    return state

def doToggleMenuShowState(stateToggle, listOfItems):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Toggle for turning off and on the visibility of a menu section

    ARGUMENTS:
    stateToggle(string) - this should point to the variable holding a (bool) value
    listOfItems(list) - list of menu item names to change

    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if stateToggle:
        newState = False
    else:
        newState = True

    for item in listOfItems:
        uiType = mc.objectTypeUI(item)
        if uiType == 'staticText':
            mc.text(item, edit = True, visible = newState)
        elif uiType == 'separator':
            mc.separator(item, edit = True, visible = newState)
        elif uiType == 'rowLayout':
            mc.rowLayout(item, edit = True, visible = newState)
        elif uiType == 'rowColumnLayout':
            mc.rowColumnLayout(item, edit = True, visible = newState)
        elif uiType == 'columnLayout':
            mc.columnLayout(item, edit = True, visible = newState)
        elif uiType == 'formLayout':
            mc.formLayout(item, edit = True, visible = newState)
            #print ('%s%s%s%s%s%s%s' % ('"python(mc.',uiType,"('",item,"', edit = True, visible = ",newState,'))"'))
            #mel.eval(('%s%s%s%s%s%s%s' % ('"python(mc.',uiType,"('",item,"', edit = True, visible = ",newState,'))"')))
            #mc.separator(item, edit = True, visible = newState)
        else:
            warning('%s%s%s' %('No idea what ', item, ' is'))
    return newState

def doToggleModeState(OptionSelection,OptionList,OptionVarName,ListOfContainers,forceInt = False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    This connects to a cgm rework of tabs in maya gui's. Mainly to be used with a form layout is needed
    with tabs. Tabs and form layouts don't work well together. This is a work around

    ARGUMENTS:
    optionSelection(string) - this should point to the variable holding a (int) value
    optionList(list) - the option selection must be in the optionList
    OptionVarName(string)
    ListOfContainers(list) -- list of containers
    forceInt -- forces the optionVar to set

    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    visOn = OptionList.index(OptionSelection)
    if forceInt:
        mc.optionVar(iv=(OptionVarName,int(visOn)))
    else:
        mc.optionVar(sv=(OptionVarName,OptionSelection))

    for cnt,Container in enumerate(ListOfContainers):
        if cnt == visOn:
            Container(e=True,vis=True)
            #doToggleMenuShowState(Container,True)
        else:
            Container(e=True,vis=False)
            #doToggleMenuShowState(Container,False)
        cnt+=1

def doStartMayaProgressBar(stepMaxValue = 100, statusMessage = 'Calculating....',interruptableState = True,**kws):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Tools to do a maya progress bar. This function and doEndMayaProgressBar are a part of a set. Example
    usage:

    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(int(number))
    for n in range(int(number)):
    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
    break
    mc.progressBar(mayaMainProgressBar, edit=True, status = (n), step=1)

    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

    ARGUMENTS:
    stepMaxValue(int) - max number of steps (defualt -  100)
    statusMessage(string) - starting status message
    interruptableState(bool) - is it interuptible or not (default - True)

    RETURNS:
    mayaMainProgressBar(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    try:mayaMainProgressBar = mel.eval('$tmp = $gMainProgressBar;')
    except:
        return
    mc.progressBar( mayaMainProgressBar,
                    edit=True,
                    beginProgress=True,
                    isInterruptable=interruptableState,
                    status=statusMessage,
                    minValue = 0,
                    step=1,
                    maxValue= stepMaxValue,**kws)
    return mayaMainProgressBar

def doEndMayaProgressBar(mayaMainProgressBar = None):
    if mayaMainProgressBar is None:
        try:mayaMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
        except:
            return
    mc.progressBar(mayaMainProgressBar, edit=True, endProgress=True)
    
def progressBar_test(progressBar=None, cnt = 1000,sleep=.0001):
    if not progressBar:
        progressBar = doStartMayaProgressBar(stepMaxValue=cnt+1)
    
    mc.progressBar(progressBar,edit=True, vis=True)
    for i in range(cnt):
        progressBar_set(progressBar,status='Cnt: {0}'.format(i),progress=i)
        time.sleep(sleep)
        
    mc.progressBar(progressBar,edit=True, vis=False)
    progressBar_end(progressBar)
    
def progressBar_start(progressBar = None,stepMaxValue = 100,
                      statusMessage = 'Calculating....',interruptableState = False
                      ):
    if stepMaxValue < 1:
        stepMaxValue = 1
    if progressBar == None:
        return doStartMayaProgressBar(stepMaxValue,statusMessage,interruptableState)
        
    elif mc.progressBar(progressBar, q=True, exists = True):
        mc.progressBar( progressBar,
                        edit=True,
                        vis=True,
                        beginProgress=True,
                        isInterruptable=interruptableState,
                        status=statusMessage,
                        step=1,
                        minValue = 0,
                        maxValue= stepMaxValue )        
        return progressBar
    
    return mc.progressBar( progressBar,
                           beginProgress=True,
                           isInterruptable=interruptableState,
                           status=statusMessage,
                           step=1,
                           minValue = 0,
                           vis=True,
                           maxValue= stepMaxValue )

def progressBar_iter(progressBar=None,**kws):
    if not progressBar:
        progressBar = progressBar_start(*kws)
        
    if 'step' not in kws.keys():kws['step'] = 1
    if 'beginProgress' not in kws.keys():kws['beginProgress'] = 1
    kws['edit'] = 1
    
    mc.progressBar(progressBar, **kws)

def progressBar_end(progressBar):
    mc.progressBar(progressBar, edit=True, vis=False)    
    mc.progressBar(progressBar, edit=True, endProgress=True)
    
def progressBar_setMaxStepValue(progressBar=None,int_value = 100):
    if not progressBar:progressBar = progressBar_start(*kws)    
    mc.progressBar(progressBar,edit = True, progress = 0, maxValue = int_value)

def progressBar_setMinStepValue(progressBar=None,int_value=100):
    if not progressBar:progressBar = progressBar_start(*kws)    
    mc.progressBar(progressBar,edit = True, minValue = int_value)
    
def progressBar_set(progressBar=None,**kws):
    if not progressBar:progressBar = progressBar_start(*kws)    
    if kws.get('status'):
        str_bfr = kws.get('status')
    if 'beginProgress' not in kws.keys():kws['beginProgress'] = 1
    mc.progressBar(progressBar,edit = True,**kws)


def log_selfReport(self):
    try:
        log.info("="*100)		
        log.info("{0} GUI = {1} {0}".format(cgmGEN._str_headerDiv, self))
        log.info("="*100)	
        l_keys = self.__dict__.keys()
        l_keys.sort()		    
        log.info(" Self Stored: " + cgmGEN._str_subLine)
        for i,str_k in enumerate(l_keys):
            try:
                buffer = self.__dict__[str_k]
                #type(buffer)
                bfr_type = type(buffer)
                if bfr_type in [bool,str,list,tuple]:
                    log.info(cgmGEN._str_baseStart * 2 + "[{0}] : {1} ".format(str_k,buffer))
                if 'var_' in str_k:
                    log.info(cgmGEN._str_baseStart * 2 + "[{3}] | full:{0} | type: {1} | value: {2}".format(buffer.name,buffer.varType,buffer.value,str_k))		
                #log.info(cgmGEN._str_baseStart * 4 + "Type: {0}".format(type(buffer)))
            except Exception,error:
                log.error("log_selfReport >> '{0}' key fail | error: {1}".format(str_k,error))
                
        pprint.pprint(self.__dict__)
        
    except Exception,error:
        log.error("log_self fail | error: {0}".format(error))
        
class Callback(object):
    '''
    BY HAMISH
    stupid little callable object for when you need to "bake" temporary args into a
    callback - useful mainly when creating callbacks for dynamicly generated UI items
    '''
    def __init__( self, func, *a, **kw ):
        self._func = func
        self._args = a
        self._kwargs = kw
    def __call__( self, *args ):
        return self._func( *self._args, **self._kwargs ) 
    
def varBuffer_define(self,optionVar):
    _str_func = 'varBuffer_define'

    sel = mc.ls(sl=True, flatten = True) or []

    if not sel:
        log.error("|{0}| >> No selection found. Cannot define".format(optionVar.name))
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

def varBuffer_remove(self,optionVar,value=None):
    _str_func = 'varBuffer_add'
    try:optionVar.name
    except:optionVar = cgmMeta.cgmOptionVar(optionVar)
    
    if not value:
        value = mc.ls(sl=True, flatten = True) or []
        if not sel:
            log.error("|{0}| >> No selection found. Cannot define")
            return False
    value = VALID.listArg(value)
    for o in value:
        optionVar.remove(o)
        
        
            
            
def uiSection_help(parent):
    _str_func = 'uiSection_help'  
    
    mc.menuItem(parent = parent,
                l='CGM Docs',
                ann = "Find help for various tools",
                c=lambda *a: webbrowser.open("http://docs.cgmonks.com"))  
    
    mc.menuItem(parent = parent,
                l='Report issue',
                ann = "Load a browser page to report a bug",
                c=lambda *a: webbrowser.open("https://bitbucket.org/jjburton/cgmtools/issues/new"))    
    mc.menuItem(parent = parent,
                l='Get Builds',
                ann = "Get the latest builds of cgmTools from bitBucket",
                c=lambda *a: webbrowser.open("https://bitbucket.org/jjburton/cgmtools/downloads/?tab=branches")) 
    _vids = mc.menuItem(parent = parent,subMenu = True,
                        l='Videos')
    
    mc.menuItem(parent = _vids,
                l='cgm',
                ann = "CG Monks Vimeo Channel",
                c=lambda *a: webbrowser.open("http://vimeo.com/cgmonks"))     
    mc.menuItem(parent = _vids,
                l='Red9',
                ann = "Red 9 Vimeo Channel",
                c=lambda *a: webbrowser.open("http://vimeo.com/user9491246"))    
   
    mc.menuItem(parent = parent,
                l='Coding questions',
                ann = "Get help on stack overflow for your coding questions",
                c=lambda *a: webbrowser.open("http://stackoverflow.com"))          
    mc.menuItem(parent = parent,
                l='Enviornment Info',
                ann = "Get your maya/os enviorment info. Useful for bug reporting to tool makers",
                c=lambda *a: cgmGEN.report_enviornment())
    
    
def uiPrompt_getValue(title = None, message = None, text = None, uiSelf = None,style = 'text'):
    _str_func = 'uiPrompt_getValue'
    if title is None:
        _title = 'Need data...'
    else:_title = title
    
    
    _d = {'title':_title, 'button':['OK','Cancel'], 'defaultButton':'OK', 'messageAlign':'center', 'cancelButton':'Cancel','dismissString':'Cancel','style':style}
    if message is None:
        message = "Getting values is better with messages..."
        
    _d['message'] = message
    if text is not None:
        _d['text'] = text
        
    result = mc.promptDialog(**_d)
    
    if result == 'OK':
        _v =  mc.promptDialog(query=True, text=True)
        
        return _v
    else:
        log.info("|{0}| >> Gather value cancelled".format(_str_func))
        return None     

class cgmScrollList(mUI.BaseMelWidget):
    WIDGET_CMD = mc.iconTextScrollList
    KWARG_CHANGE_CB_NAME = 'sc'

    ALLOW_MULTI_SELECTION = True
    def __new__( cls, parent, *a, **kw ):
        if 'ams' not in kw and 'allowMultiSelection' not in kw:
            kw[ 'ams' ] = cls.ALLOW_MULTI_SELECTION
        return mUI.BaseMelWidget.__new__( cls, parent, *a, **kw )
    
    def __init__( self, parent, *a, **kw ):
        mUI.BaseMelWidget.__init__( self, parent, *a, **kw )
        self._appendCB = None
        self._items = []
        # self._ml_scene = []
        # self._ml_loaded = []
        self._l_strings = []
        self._l_itc = []
        self._d_itc =  {}
        self.filterField = None
        self.b_selCommandOn = True
        self.rebuild()
        self.cmd_select = None
        self(e=True, sc = self.selCommand)
        
    def __getitem__( self, idx ):
        return self.getItems()[ idx ]

    def setItems( self, items ):
        self.clear()
        for i in items:
            self.append( i )
    def getItems( self ):
        return self._items

    def getSelectedItem( self ):
        items = self.getSelectedItems()
        if items:
            return items[0]
        else:
            return None

    def getSelectedItems( self ):
        return self( q=True, si=True ) or []
    
    def getSelectedIdx( self ):
        items = self.getSelectedIdxs()
        if items:
            return items[0]
        else:
            return None

    def getSelectedIdxs( self ):
        return [ idx-1 for idx in self( q=True, sii=True ) or [] ]
        
    def selectByIdx( self, idx ):
        self( e=True, selectIndexedItem=idx+1 )  #indices are 1-based in mel land - fuuuuuuu alias!!!

    def selectByValue( self, value):
        self( e=True, selectItem=value )
        
    def append( self, item ):
        self( e=True, append=item )
        self._items.append(item)
        
    def appendItems( self, items ):
        for i in items: self.append( i )
        
    def allowMultiSelect( self, state ):
        self( e=True, ams=state )
    
    def report(self):
        log.debug(cgmGEN.logString_start('report'))                
        log.info("Scene: "+cgmGEN._str_subLine)
        # for i,mObj in enumerate(self._ml_scene):
        #     print ("{0} | {1} | {2}".format(i,self._l_strings[i],mObj))
            
        # log.info("Loaded "+cgmGEN._str_subLine)
        # for i,mObj in enumerate(self._ml_loaded):
        #     print("{0} | {1}".format(i, mObj))
            
        # pprint.pprint(self._ml_scene)
        
    def set_selCallBack(self,func,*args,**kws):
        log.debug(cgmGEN.logString_start('set_selCallBack'))                
        self.selCommand = func
        self.selArgs = args
        self.selkws = kws
    
    def setHLC(self,mBlock=None, color = [1,1,1]):
        log.debug(cgmGEN.logString_start('setHLC'))        
        try:
            _color = [v*.7 for v in color]
            self(e =1, hlc = _color)
            return
        except Exception,err:
            log.error(err)
            
        try:self(e =1, hlc = [.5,.5,.5])
        except:pass
            
    def selCommand(self):
        log.debug(cgmGEN.logString_start('selCommand'))
        l_indices = self.getSelectedIdxs()
        if self.b_selCommandOn and self.cmd_select:
            if len(l_indices)<=1:
                return self.cmd_select()
        return False
    
    def rebuild( self ):
        _str_func = 'rebuild'
        
        log.debug(cgmGEN.logString_start(_str_func))
        self.b_selCommandOn = False
        self( e=True, ra=True )
        
        try:self(e =1, hlc = [.5,.5,.5])
        except:pass        
        
        self._items = []
        # self._ml_scene = []
        # self._ml_loaded = []
        self._l_strings = []
        self._l_str_loaded = []
        self._l_itc = []
        self._d_itc  = {}
        #...
        # _ml,_l_strings = BLOCKGEN.get_uiModuleScollList_dat(showSide=1,presOnly=1)
        
        # self._ml_scene = _ml
        self._l_itc = []
        
        d_colors = {'blue':[.4,.4,1],
                    'red':[.9,.2,.2],
                    'yellow':[.8,.8,0]}
        
        # def getString(pre,string):
        #     i = 1
        #     _check = ''.join([pre,string])
        #     while _check in self._l_strings and i < 100:
        #         _check = ''.join([pre,string,' | NAMEMATCH [{0}]'.format(i)])
        #         i +=1
        #     return _check
        
        # def get_side(mNode):
        #     _cgmDirection = mNode.getMayaAttr('cgmDirection')
        #     if _cgmDirection:
        #         if _cgmDirection[0].lower() == 'l':
        #             return 'left'
        #         return 'right'
        #     return 'center'
        
        # for i,mBlock in enumerate(_ml):
        #     _arg = get_side(mBlock)
        #     _color = d_colors.get(_arg,d_colors['yellow'])
        #     self._l_itc.append(_color)            
        #     self._d_itc[mBlock] = _color
        #     try:
        #         _str_base = mBlock.UTILS.get_uiString(mBlock)#mBlock.p_nameBase#
        #         #_modType = mBlock.getMayaAttr('moduleType')
        #         #if _modType:
        #             #_str_base = _str_base + ' | [{0}]'.format(_modType)
        #     except:_str_base = 'FAIL | {0}'.format(mBlock.mNode)
        #     _pre = _l_strings[i]
        #     self._l_strings.append(getString(_pre,_str_base))
            
        self.update_display()
        
        # if ml_sel:
        #     try:self.selectByBlock(ml_sel)
        #     except Exception,err:
        #         print err
        self.b_selCommandOn = True

    def clear( self ):
        log.debug(cgmGEN.logString_start('clear'))                
        self( e=True, ra=True )
        self._l_str_loaded = []
        self._items = []
        # self._ml_loaded = []
        
    def clearSelection( self,):
        self( e=True, deselectAll=True )
    def set_filterObj(self,obj=None):
        self.filterField = obj

    def update_display(self,searchFilter='',matchCase = False):
        _str_func = 'update_display'
        log.debug(cgmGEN.logString_start(_str_func))
        
        l_items = self.getSelectedItems()
        
        if self.filterField is not None:
            searchFilter = self.filterField.getValue()
        
        self.clear()
        try:
            for i,strEntry in enumerate(r9Core.filterListByString(self._l_strings,
                                                                  searchFilter,
                                                                  matchcase=matchCase)):
                if strEntry in self._l_str_loaded:
                    log.warning("Duplicate string")
                    continue
                self.append(strEntry)
                self._l_str_loaded.append(strEntry)
                idx = self._l_strings.index(strEntry)

        except Exception,err:
            log.error("|{0}| >> err: {1}".format(_str_func, err))  
            for a in err:
                log.error(a)