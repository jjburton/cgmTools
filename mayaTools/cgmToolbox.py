"""
------------------------------------------
toolbox: cgm.core.tools
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__version__ = '0.1.08222017'

#from __future__ import with_statement

import os
import re
import sys

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from cgm.core import cgm_General as cgmGen

import cgm.core.classes.GuiFactory as cgmUI
#try:
#    import wingdbstub
#except ImportError: pass

import maya.cmds as mc
import maya
import maya.mel as mel
from maya.mel import eval as evalMel

#>>>>> Bridge to get our sub zoo stuff working
from cgm import cgmInitialize
reload(cgmInitialize)
cgmInitialize.setupContributorPaths()

#import cgm.lib.zoo.zooPyMaya.baseMelUI as mUI
import cgm.core.classes.HotkeyFactory as HKEY

#>>>>>

from cgm.lib import guiFactory
#from cgm.lib.zoo.zooPy.path import Path, findFirstInEnv, findInPyPath
from cgm.core.cgmPy import path_Utils as cgmPath
from cgm.lib.zoo.zooPyMaya import baseMelUI as mUI
from cgm.lib.zoo.zooPyMaya.melUtils import printErrorStr
import Red9

#==========================================================================
from cgm.core import cgm_General as cgmGen
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
reload(MMCONTEXT)
from cgm.core.lib import shared_data as SHARED
reload(SHARED)
from cgm.core.tools import locinator as LOCINATOR
import cgm.core.lib.locator_utils as LOC
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import curve_Utils as CURVES
import cgm.core.tools.lib.snap_calls as SNAPCALLS
from cgm.core.tools import meshTools as MESHTOOLS
reload(MESHTOOLS)
import cgm.core.cgmPy.validateArgs as VALID
from cgm.core.lib import node_utils as NODES
from cgm.core.tools import attrTools as ATTRTOOLS
from cgm.core.tools import dynParentTool as DYNPARENTTOOL
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.tools.locinator as LOCINATOR
import cgm.core.lib.arrange_utils as ARRANGE
import cgm.core.lib.rigging_utils as RIGGING
import cgm.core.classes.GuiFactory as cgmUI
import cgm.core.tools.lib.annotations as TOOLANNO
import cgm.core.lib.distance_utils as DIST
import cgm.core.tools.toolbox as TOOLBOX
import cgm.core.lib.skin_utils as SKIN
import cgm.core.lib.constraint_utils as CONSTRAINTS
reload(DIST)
reload(TOOLBOX)
reload(TOOLANNO)
reload(cgmUI)
reload(RIGGING)
mUI = cgmUI.mUI

from cgm.lib.ml import (ml_breakdownDragger,
                        ml_resetChannels,
                        ml_deleteKey,
                        ml_setKey,
                        ml_hold,
                        ml_stopwatch,
                        ml_arcTracer,
                        ml_convertRotationOrder,
                        ml_copyAnim)

_2016 = False
if cgmGen.__mayaVersion__ >=2016:
    _2016 = True
#==========================================================================



def clean_scriptPaths():
    _str_func = 'clean_scriptPaths'
    _buffer = maya.mel.eval( 'getenv MAYA_SCRIPT_PATH' )
    mayaScriptPaths = map( cgmPath.Path, maya.mel.eval( 'getenv MAYA_SCRIPT_PATH' ).split( os.pathsep ) )
    mayaScriptPathsSet = set( mayaScriptPaths )

    _l_good = []
    _l_bad = []
    try:
        for path in mayaScriptPathsSet:
            log.debug("{0}>> Checking {1}".format(_str_func,path))	    
            if path.count('/') == 0:
                log.info("{0}>>Bad path? {1}".format(_str_func,path))

            if path not in _l_good:
                if path.count('.git') == 0:
                    _l_good.append(path)		    
                else:
                    log.info("{0}>> .git in path??: {1}".format(_str_func,path))		    
            else:
                log.info("{0}>> Duplicate path: {1}".format(_str_func,path))

        _loadable = []        
        for i,_p in enumerate(_l_good):
            try:
                maya.mel.eval( 'putenv MAYA_SCRIPT_PATH "%s"' % _p )
                _loadable.append(_p)
                log.info("{0}>> {1}".format(_str_func,_p))				
            except:
                log.error("{0}>> Failed to load: {1}".format(_str_func,_p))

        newScriptPath = os.pathsep.join( [ p for p in _loadable ] )
        maya.mel.eval( 'putenv MAYA_SCRIPT_PATH "%s"' % newScriptPath )
        return True
    except:
        log.error('clean_scriptPaths failure. Restoring: {0}'.format(_buffer))
        maya.mel.eval( 'putenv MAYA_SCRIPT_PATH "%s"' % _buffer )

def clean_pluginPaths():
    _str_func = 'clean_pluginPaths'
    _buffer = maya.mel.eval( 'getenv MAYA_PLUG_IN_PATH' )
    mayaScriptPaths = map( cgmPath.Path, maya.mel.eval( 'getenv MAYA_PLUG_IN_PATH' ).split( os.pathsep ) )
    mayaScriptPathsSet = set( mayaScriptPaths )

    _l_good = []
    _l_bad = []
    try:
        for path in mayaScriptPathsSet:
            log.debug("{0}>> Checking {1}".format(_str_func,path))
            if path.count('/') == 0:
                log.info("{0}>>Bad path? {1}".format(_str_func,path))
            if path not in _l_good:
                _l_good.append(path)
            else:
                log.info("{0}>> Duplicate path: {1}".format(_str_func,path))

        _loadable = []        
        for i,_p in enumerate(_l_good):
            try:
                maya.mel.eval( 'putenv MAYA_PLUG_IN_PATH "%s"' % _p )
                _loadable.append(_p)
                log.info("{0}>> {1}".format(_str_func,_p))		
            except:
                log.error("{0}>> Failed to load: {1}".format(_str_func,_p))

        newScriptPath = os.pathsep.join( [ p for p in _loadable ] )
        maya.mel.eval( 'putenv MAYA_PLUG_IN_PATH "%s"' % newScriptPath )
        return True
    except:
        log.error('clean_pluginPaths failure. Restoring: {0}'.format(_buffer))
        maya.mel.eval( 'putenv MAYA_PLUG_IN_PATH "%s"' % _buffer )

def setupCGMScriptPaths():
    thisFile = cgmPath.Path(__file__)
    #thisPath = os.sep.join(__file__.split(os.sep)[:-1])
    thisPath = thisFile.up().osPath()

    mayaScriptPaths = map( cgmPath.Path, maya.mel.eval( 'getenv MAYA_SCRIPT_PATH' ).split( os.pathsep ) )
    mayaScriptPathsSet = set( mayaScriptPaths )
    _paths = [os.path.join('cgm','mel','zooPy'),
              os.path.join('cgm','mel'),
              os.path.join('cgm','images'),
              os.path.join('cgm','lib','zoo'),
              os.path.join('cgm','lib','zoo','zooMel'),
              os.path.join('cgm','lib','zoo','zooPy'),     
              os.path.join('cgm','core','mel'),
              'Red9']

    for path in _paths:
        fullPath = cgmPath.Path( os.path.join(thisPath, path) )
        if fullPath not in mayaScriptPathsSet:
            log.info("setupCGMScriptPaths>> Path not found. Appending: {0}".format(fullPath))            
            mayaScriptPaths.append( cgmPath.Path(fullPath.asFriendly()) )
            mayaScriptPaths.extend( fullPath.dirs( recursive=True ) )

            mayaScriptPaths = mUI.removeDupes( mayaScriptPaths )
            newScriptPath = os.pathsep.join( [ p for p in mayaScriptPaths ] )
            #for p in mayaScriptPaths:
                #print ("{0} >> {1}".format(p,p.unresolved()))
            maya.mel.eval( 'putenv MAYA_SCRIPT_PATH "%s"' % newScriptPath )

def setupCGMPlugins():
    thisFile = cgmPath.Path( __file__ )
    thisPath = thisFile.up().osPath()

    existingPlugPathStr = maya.mel.eval( 'getenv MAYA_PLUG_IN_PATH;' )
    existingPlugPaths = map( cgmPath.Path, existingPlugPathStr.split( os.pathsep ) )
    existingPlugPathsSet = set( existingPlugPaths )

    #cgmPyPath = thisPath / 'cgm/plugins'
    cgmPyPath = cgmPath.Path( os.path.join(thisPath, 'cgm','plugins') )
    if cgmPyPath not in existingPlugPathsSet:
        log.info("setupCGMPlugins>> cgmPyPath not found. Appending: {0}".format(cgmPyPath))            
        existingPlugPaths.append( cgmPyPath )

        existingPlugPaths = mUI.removeDupes( existingPlugPaths )
        newPlugPathStr = os.pathsep.join( [ p for p in existingPlugPaths ] )
        for p in existingPlugPaths:
            print p
        maya.mel.eval( 'putenv MAYA_PLUG_IN_PATH "%s";' % newPlugPathStr )

"""
def setupDagProcMenu() REMOVED

"""

def setupCGMToolBox():
    setupCGMScriptPaths()
    setupCGMPlugins()
    #setupDagProcMenu()
    #setupCGMMenu()
    uiMainMenu_add()


def setupCGMMenu():
    if not mc.optionVar( ex='cgmVar_ToolboxMainMenu' ):
        mc.optionVar( iv=('cgmVar_ToolboxMainMenu', 1) )

    if not mc.optionVar( q='cgmVar_ToolboxMainMenu' ):
        return

    if not hasattr( maya, '_cgmToolboxMenu' ):
        def cb( *a ):
            import cgmToolbox
            cgmToolbox.buildCGMToolsMenu( *a )

        menu = mUI.MelMainMenu( l='CGM Tools', pmc=cb, tearOff=True )
        setattr( maya, '_cgmToolboxMenu', menu )


def uiMainMenu_add():
    if not hasattr(maya,'_cgmMenu'):
        def build(*a):
            import cgmToolbox
            cgmToolbox.uiBuild_cgmMenu(*a)
        menu = mUI.MelMainMenu(l='CGM', pmc=build, tearOff = True)
        setattr(maya,'_cgmMenu',menu)

class AutoStartInstaller(object):
    '''
    this is effectively a static class to contain all the functionality related to auto install
    '''
    class AutoSetupError(Exception): pass

    def getUserSetupFile( self ):
        pyUserSetup, melUserSetup = None, None
        """try:
            pyUserSetup = cgmPath.Path(cgmPath.findInPyPath( 'userSetup.py'))#findInPyPath)
            log.info("Py user file is '%s'"%pyUserSetup)
        except: log.info ('No py user setup')"""

        try:
            melUserSetup = cgmPath.Path(cgmPath.findFirstInEnv( 'userSetup.mel', 'MAYA_SCRIPT_PATH' ))
            log.info("Mel user file is '%s'"%melUserSetup)
        except: log.info ('No mel user setup')

        return pyUserSetup, melUserSetup

    def isInstalled( self ):
        success = False
        pyUserSetup, melUserSetup = self.getUserSetupFile()
        if pyUserSetup is not None:
            if self.isInstalledPy( pyUserSetup ):
                return True

        if melUserSetup is not None:
            if self.isInstalledMel( melUserSetup ) == True:
                return True

        print ('Not installed')
        return False

    def install( self ):
        success = False
        pyUserSetup, melUserSetup = self.getUserSetupFile()
        log.info("pyUserSetup: {0}".format(pyUserSetup))
        log.info("melUserSetup: {0}".format(melUserSetup))        
        if pyUserSetup is None and melUserSetup is None:
            print 'No py or mel user setup files found.Creating py'
            if not self.createMelUserSetup():#if we can't make a user file, break
                self.log_error("Failed to create Py User File")
                return False
            pyUserSetup, melUserSetup = self.getUserSetupFile()

        success = False
        errors = []

        """if pyUserSetup is not None:
			try:
				self.installPy( pyUserSetup )
				success = True
			except self.AutoSetupError, x:
				errors.append( x )"""

        if not success:
            if melUserSetup is not None:
                try:
                    self.installMel( melUserSetup )
                    success = True
                except self.AutoSetupError, x:
                    errors.append( x )

        if not success:
            print '>>>>>Failed>>>>>>'
            for x in errors:
                log.info("Install error: {0}".format(x))

    def isInstalledPy( self, pyUserSetup ):
        l_lines = ['import cgmToolbox','import cgm.core','cgm.core._reload()']
        l_found = []
        l_missing = []
        with open( pyUserSetup ) as f:
            for i,codeLine in enumerate(l_lines):
                for line in f:
                    if codeLine in line:
                        l_found.append(codeLine)
                        break
                if codeLine not in l_found:
                    l_missing.append(codeLine)
        log.info("Found: %s"%l_found)
        if l_missing:
            log.info("Failed to find: %s"%l_missing)
            return l_missing
        return True		
        """with open( pyUserSetup ) as f:
            for line in f:
                if 'import' in line and 'cgmToolbox' in line:
                    return True
        return False"""

    def installPy( self, pyUserSetup ):
        buffer = self.isInstalledPy( pyUserSetup )
        if buffer == True:
            return

        if pyUserSetup.getWritable():
            with open( pyUserSetup, 'a' ) as f:
                for l in buffer:
                    f.write( '\n\n {0}\n'.format(l) )	
                else:
                    raise self.AutoSetupError( "%s isn't writeable - aborting auto setup!" % pyUserSetup )


        """if self.isInstalledPy( pyUserSetup ):
            return

        if pyUserSetup.getWritable():
            with open( pyUserSetup, 'a' ) as f:
                f.write( '\n\nimport cgmToolbox\n' )
        else:
            raise self.AutoSetupError( "%s isn't writeable - aborting auto setup!" % pyUserSetup )"""

    def isInstalledMel( self, melUserSetup ):
        l_lines = ['import cgmToolbox','import cgm.core','cgm.core._reload()']
        l_found = []
        l_missing = []
        with open( melUserSetup ) as f:
            for i,codeLine in enumerate(l_lines):
                for line in f:
                    if codeLine in line:
                        l_found.append(codeLine)
                        break
                if codeLine not in l_found:
                    l_missing.append(codeLine)
        log.info("Found: %s"%l_found)
        if l_missing:
            log.info("Failed to find: %s"%l_missing)
            return l_missing
        return True

    def installMel( self, melUserSetup ):
        buffer = self.isInstalledMel( melUserSetup )
        if buffer == True:
            return

        if melUserSetup.getWritable():
            with open( melUserSetup, 'a' ) as f:
                for l in buffer:
                    f.write( '\n\npython( "%s" );\n'%l )
        else:
            raise self.AutoSetupError( "%s isn't writeable - aborting auto setup!" % melUserSetup )
    def createMelUserSetup(self):
        try:
            envFile = mc.about(environmentFile = True) or False #Get env variable
            if not envFile: #See if it got anything
                print 'No environmental file found'
            buffer = envFile.split('/')[:-1]#parse to list and pull 'Maya.env'
            buffer.extend(['scripts','userSetup.mel'])
            newLocation =  os.sep.join(buffer)

            f=open(newLocation,'w')
            f.close()
            return True
        except:
            guiFactory.warning("Couldn't create a mel user file")
            return False
    def createPyUserSetup(self):
        try:
            envFile = mc.about(environmentFile = True) or False #Get env variable
            if not envFile: #See if it got anything
                print 'No environmental file found'
            buffer = envFile.split('/')[:-1]#parse to list and pull 'Maya.env'
            buffer.extend(['scripts','userSetup.py'])
            newLocation =  os.sep.join(buffer)

            f=open(newLocation,'w')
            f.close()
            return True
        except:
            guiFactory.warning("Couldn't create a mel user file")
            return False




def buildCGMToolsMenu( *a ):
    menu = maya._cgmToolboxMenu
    menu.clear()

    mUI.MelMenuItem( menu, l='Open Toolbox Window', c=lambda *a: ui() )
    for toolCatName, toolSetupData in TOOL_CATS:
        catMenu = mUI.MelMenuItem( menu, l=toolCatName, sm=True, tearOff=True )
        for toolName, toolDesc, toolCB in toolSetupData:
            mUI.MelMenuItem( catMenu, l=toolName, ann=toolDesc, c=toolCB, tearOff=True )


def loadCGMPlugin( pluginName ):
    try:
        mc.loadPlugin( pluginName, quiet=True )
    except:
        setupCGMToolBox()
        try:
            mc.loadPlugin( pluginName, quiet=True )
        except:
            maya.OpenMaya.MGlobal.displayError( 'Failed to load cgmMirror.py plugin - is it in your plugin path?' )


from cgm.core.tools.lib import tool_chunks as UICHUNKS
reload(UICHUNKS)
@cgmGen.Timer
def uiBuild_cgmMenu( *args ):
    _str_func = 'uiBuild_cgmMenu'
    menu = maya._cgmMenu
    menu.clear()
    reload(UICHUNKS)

    _l_sel = mc.ls(sl=True)
    if _l_sel:_b_sel = True
    _b_sel_pair = False
    _b_sel_few = False
    _len_sel = len(_l_sel)
    if _len_sel  >= 2:
        _b_sel_pair = True
    if _len_sel >2:
        _b_sel_few = True		

    #log.info("|{0}| >> Selected: {1}".format(_str_func,_l_sel))        

    #mUI.MelMenuItem(menu, l='Open Tool Win',
    #                c=lambda *args: ToolboxWindow())
    mc.menuItem(p = menu, l='Open Tool Win',
                c=cgmGen.Callback(ui))

    #>>Snap ----------------------------------------------------------------------
    _snap = mc.menuItem(p=menu,l='Snap',subMenu = True, tearOff = True)  
    UICHUNKS.uiSection_snap(_snap)

    #>>TD ----------------------------------------------------------------------
    _td = mc.menuItem(p=menu,l='TD/Create',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_selection(_td)
    UICHUNKS.uiSection_riggingUtils(_td)	
    UICHUNKS.uiSection_attributes(_td)	
    UICHUNKS.uiSection_rayCast(_td)	    
    UICHUNKS.uiSection_distance(_td)	
    UICHUNKS.uiSection_joints(_td)
    UICHUNKS.uiSection_sdk(_td)
    UICHUNKS.uiSection_shapes(_td)	
    UICHUNKS.uiSection_curves(_td)
    UICHUNKS.uiSection_mesh(_td)
    UICHUNKS.uiSection_skin(_td)
    UICHUNKS.uiSection_nodes(_td)

    #>>>Anim ----------------------------------------------------------------------
    _anim = mc.menuItem(p=menu,l='Anim',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_animUtils(_anim) 

    #>>Layout ----------------------------------------------------------------------
    _layout = mc.menuItem(p=menu,l='Layout',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_layout(_layout)

    #>>Hotkeys ----------------------------------------------------------------------
    _hotkeys = mc.menuItem(p=menu,l='Hotkeys',subMenu = True, tearOff = False)
    UICHUNKS.uiSection_hotkeys(_hotkeys)

    #>>dev ----------------------------------------------------------------------
    _dev = mc.menuItem(p=menu,l='Dev',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_dev(_dev)		

    #>>Help ----------------------------------------------------------------------
    _help = mc.menuItem(p=menu,l='Help',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_help(_help)		


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def loadTDTools( *a ):
    import maya.cmds as mc
    import maya.mel as mel
    mel.eval('python("import maya.cmds as mc;")')
    from cgm.tools import tdTools
    reload(tdTools)
    tdTools.run()

def loadRed9( *a ):
    import Red9
    reload(Red9)
    Red9.start()


def loadAttrTools( *a ):
    from cgm.tools import attrTools as attrTools1
    reload(attrTools1)
    cgmAttrToolsWin = attrTools1.run()

def loadAttrTools2( *a ):
    from cgm.core.tools import attrTools as attrTools
    reload(attrTools)
    attrTools.ui()

def loadCGMMeshTools( *a ):
    from cgm.core.tools import meshTools
    reload(meshTools)
    cgmMeshToolsWin = meshTools.run()

def loadLocinator( *a ):
    from cgm.tools import locinator
    reload(locinator)
    locinator.run()

def loadLocinator2( *a ):
    from cgm.core.tools import locinator as LOCINATOR
    reload(LOCINATOR)
    LOCINATOR.ui()

def loadDynParentTool( *a ):
    from cgm.core.tools import dynParentTool as DYNPARENTTOOL
    reload(DYNPARENTTOOL)
    DYNPARENTTOOL.ui()

def loadNGSKIN():
    try:
        from ngSkinTools.ui.mainwindow import MainWindow
        MainWindow.open()    
    except:
        log.warning("Failed to load. Go get it.")
        webbrowser.open("http://www.ngskintools.com/")

def loadAnimTools( *a ):
    from cgm.tools import animTools
    reload(animTools)
    cgmAnimToolsWin = animTools.run()

def loadSetTools( *a ):
    from cgm.tools import setTools
    reload(setTools)
    cgmSetToolsWin = setTools.run()	

def loadPuppetBox( *a ):
    from cgm.tools import puppetBox
    reload(puppetBox)
    cgmPuppetBoxWin = puppetBox.run()

def loadPuppetBox2( *a ):
    from cgm.tools import puppetBox2
    reload(puppetBox2)
    cgmPuppetBoxWin = puppetBox2.run()	

def loadCGMSimpleGUI( *a ):
    from cgm.core.classes import GuiFactory as uiFactory
    reload(uiFactory)
    uiFactory.cgmGUI()

def reload_cgmCore( *a ):
    try:
        import cgm.core
        cgm.core._reload()	
    except Exception,error:log.warning("[reload_cgmCoreFail]{%s}"%error)


def testMorpheus( *a ):
    from cgm.core.tests import cgmMeta_test as testCGM
    reload(testCGM)
    testCGM.MorpheusBase_Test()


#Zoo stuff =====================================================================
def loadZooToolbox( *a ):
    import zooToolbox
    zooToolbox.ToolboxWindow()

def loadSkinPropagation( *a ):
    from zooPyMaya import refPropagation
    refPropagation.propagateWeightChangesToModel_confirm()

def loadXferAnim( *a ):
    from zooPyMaya import xferAnimUI
    xferAnimUI.XferAnimWindow()

class ToolCB(object):
    def __init__( self, melStr ):
        self.cmdStr = melStr
    def __call__( self, *a ):
        evalMel( self.cmdStr )


#this describes the tools to display in the UI - the nested tuples contain the name of the tool as displayed
#in the UI, and a tuple containing the annotation string and the button press callback to invoke when that
#tool's toolbox button is pressed.
#NOTE: the press callback should take *a as its args
TOOL_CATS = ( ('animation', (('cgm.locinator', "Launch cgmLocinator 2.0",
                              loadLocinator2),
                             ('cgm.dynParentTool', "Launch cgmDynParentTool",
                              loadDynParentTool),                             
                             ('red9.studioTools', "Launch Red 9's tools - hit it twice for now",
                              loadRed9),                             
                             ('zoo.XferAnim', "Tool for transferring animation - from Hamish McKenzie's zooToolbox",
                              loadXferAnim), 
                             ('zoo.Keymaster', "from Hamish McKenzie's zooToolbox - keymaster gives you a heap of tools to manipulate keyframes - scaling around curve pivots, min/max scaling of curves/keys etc...",
                              ToolCB( 'source zooKeymaster; zooKeymasterWin;' )))),

              ('rigging', (('cgm.attrTools', " NEW Attribute tools",
                            loadAttrTools2),                      
                           ('cgm.meshTools', " Mesh tools",
                            loadCGMMeshTools))),

              ('legacy', (('cgm.animTools', " Anim tools",
                           loadAnimTools),
                          ('cgm.SetTools', " Set tools",
                           loadSetTools),
                          ('cgm.locinator', "Tool for creating, updating, locators",
                           loadLocinator),

                          ('cgm.tdTools', "Series of tools for general purpose TD work - curves, naming, position, deformers",
                           loadTDTools),

                          ('cgm.attrTools OLD', " OLD Attribute tools",
                           loadAttrTools))),
              )

class ToolboxTab(mUI.MelColumnLayout):
    def __new__( cls, parent, toolTuples ):
        return mUI.MelColumnLayout.__new__( cls, parent )
    def __init__( self, parent, toolTuples ):
        _MainForm = mUI.MelFormLayout(self)            
        _column = mUI.MelColumnLayout( _MainForm, parent )

        for toolStr, annStr, pressCB in toolTuples:
            assert pressCB is not None
            mUI.MelButton( _column, l=toolStr, ann=annStr, c=pressCB,ut = 'cgmUITemplate' )

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

class ToolboxTabs(mUI.MelTabLayout):
    def __init__( self, parent ):
        n = 0
        for toolCatStr, toolTuples in TOOL_CATS:
            ui = ToolboxTab( self, toolTuples )
            self.setLabel( n, toolCatStr )
            n += 1

"""
class ToolboxWindow(mUI.BaseMelWindow):
    from  cgm.lib import guiFactory
    guiFactory.initializeTemplates()
    USE_Template = 'cgmUITemplate'

    WINDOW_NAME = 'cgmToolbox'
    WINDOW_TITLE = 'cgm.Toolbox'

    DEFAULT_SIZE = 300, 300
    FORCE_DEFAULT_SIZE = True

    DEFAULT_MENU = None

    def __init__( self ):
        from  cgm.lib import guiFactory
        guiFactory.initializeTemplates()
        USE_Template = 'cgmUITemplate'

        self.UI_menu = mUI.MelMenu( l='Setup', pmc=self.buildSetupMenu )
        ToolboxTabs( self )
        self.show()

    def buildSetupMenu( self, *a ):

        self.UI_menu.clear()
        setupMenu = mc.optionVar( q='cgmVar_ToolboxMainMenu' )
        mUI.MelMenuItem( self.UI_menu, l="Create cgm Tools Menu", cb=setupMenu, c=lambda *a: mc.optionVar( iv=('cgmVar_ToolboxMainMenu', not setupMenu) ) )
        mUI.MelMenuItemDiv( self.UI_menu )

        installer = AutoStartInstaller()
        mUI.MelMenuItem( self.UI_menu, l="Auto-Load On Maya Start", cb=installer.isInstalled(), c=lambda *a: AutoStartInstaller().install() )
"""

def uiByTab(tabIndex = 0):
    win = ui()

    win.uiTab_setup.setSelectedTabIdx(tabIndex)

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmToolbox'    
    WINDOW_TITLE = 'cgmToolbox 2.0 - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 450,350
    TOOLNAME = 'toolbox.ui'
    

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

        self.uiPopUpMenu_createShape = None
        self.uiPopUpMenu_color = None
        self.uiPopUpMenu_attr = None
        self.uiPopUpMenu_raycastCreate = None

        self.create_guiOptionVar('matchFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('rayCastFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('aimFrameCollapse',defaultValue = 0)
        self.create_guiOptionVar('aimOptionsFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('objectDefaultsFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('shapeFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('snapFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('tdFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('animFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('layoutFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('distanceFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('colorFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('animOptionsFrameCollapse',defaultValue = 0) 
        self.create_guiOptionVar('transformFrameCollapse',defaultValue = 0) 


        self.var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode', defaultValue = 'world')   
        self.var_keyType = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
        self.var_keyMode = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)
        self.var_resetMode = cgmMeta.cgmOptionVar('cgmVar_ChannelResetMode', defaultValue = 0)
        self.var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
        self.var_createRayCast = cgmMeta.cgmOptionVar('cgmVar_createRayCast', defaultValue = 'locator')        
        self.var_attrCreateType = cgmMeta.cgmOptionVar('cgmVar_attrCreateType', defaultValue = 'float')        
        self.var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
        self.var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
        self.var_createSizeMode = cgmMeta.cgmOptionVar('cgmVar_createSizeMode', defaultValue=0)
        self.var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)
        self.var_createSizeMulti = cgmMeta.cgmOptionVar('cgmVar_createSizeMultiplierValue', defaultValue=1.25)
        self.var_contextTD = cgmMeta.cgmOptionVar('cgmVar_contextTD', defaultValue = 'selection')


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
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = lambda *a:self.buildMenu_first())
        self.uiMenu_Buffers = mUI.MelMenu( l='Buffers', pmc = lambda *a:self.buildMenu_buffer())
        self.uiMenu_Help = mUI.MelMenu(l = 'Help', pmc = lambda *a:self.buildMenu_help())

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     

        setupMenu = mc.optionVar( q='cgmVar_ToolboxMainMenu' )
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Create cgm Tools Menu", cb=setupMenu, c=lambda *a: mc.optionVar( iv=('cgmVar_ToolboxMainMenu', not setupMenu) ) )
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        installer = AutoStartInstaller()
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Auto-Load On Maya Start", cb=installer.isInstalled(), c=lambda *a: AutoStartInstaller().install() )

        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))


        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))   

    def buildMenu_help(self):
        self.uiMenu_Help.clear()
        
        UICHUNKS.uiSection_help(self.uiMenu_Help)        
        
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
                    c= cgmGen.Callback(ui))          

    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        #Match
        #Aim

        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')

        ui_tabs = mUI.MelTabLayout( _MainForm)
        #uiTab_setup = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        self.uiTab_setup = ui_tabs
        uiTab_td = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')
        uiTab_anim = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')        
        uiTab_options = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')       
        uiTab_legacy = mUI.MelFormLayout(ui_tabs,ut='cgmUITemplate')       

        for i,tab in enumerate(['TD','Anim','Settings','Legacy']):
            ui_tabs.setLabel(i,tab)

        self.buildTab_td(uiTab_td)
        self.buildTab_anim(uiTab_anim)
        self.buildTab_options(uiTab_options)
        self.buildTab_legacy(uiTab_legacy)

        #self.buildTab_create(uiTab_create)
        #self.buildTab_update(uiTab_update)

        _row_cgm = cgmUI.add_cgmFooter(_MainForm)  
        _MainForm(edit = True,
                  af = [(ui_tabs,"top",0),
                        (ui_tabs,"left",0),
                        (ui_tabs,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),

                        ],
                  ac = [(ui_tabs,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])  

    def buildSection_shape(self,parent):
        _shapes_frame = mUI.MelFrameLayout(parent,label = 'Controls',vis=True,
                                           collapse=self.var_shapeFrameCollapse.value,
                                           collapsable=True,
                                           enable=True,
                                           useTemplate = 'cgmUIHeaderTemplate',
                                           expandCommand = lambda:self.var_shapeFrameCollapse.setValue(0),
                                           collapseCommand = lambda:self.var_shapeFrameCollapse.setValue(1)
                                           )	
        _shape_inside = mUI.MelColumnLayout(_shapes_frame,useTemplate = 'cgmUISubTemplate')  

        
        #>>>Shape Type Row  -------------------------------------------------------------------------------------
        # _row_shapeType = mUI.MelHSingleStretchLayout(_shape_inside,ut='cgmUISubTemplate',padding = 5)
        _row_shapeType = mUI.MelHSingleStretchLayout(_shape_inside,ut='cgmUISubTemplate')

        mUI.MelSpacer(_row_shapeType,w=5)                                      
        mUI.MelLabel(_row_shapeType,l='Shape:')
        self.uiField_shape = mUI.MelLabel(_row_shapeType,
                                          ann='Change the default create shape',
                                          ut='cgmUIInstructionsTemplate',w=100)

        _row_shapeType.setStretchWidget(self.uiField_shape) 


        mUI.MelLabel(_row_shapeType,l='Default Color:')
        self.uiField_shapeColor = mUI.MelLabel(_row_shapeType,
                                               ann='Change the default create color',                                               
                                               ut='cgmUIInstructionsTemplate',w = 100)



        _row_shapeType.layout()

        #....shape default
        self.uiField_shape(edit=True, label = self.var_curveCreateType.value)
        self.uiField_shapeColor(edit=True, label = self.var_defaultCreateColor.value)


        self.uiPopup_createShape()
        self.uiPopup_createColor()


        #>>>Create Aim defaults mode -------------------------------------------------------------------------------------
        _d = {'aim':self.var_createAimAxis,
              }

        for k in _d.keys():
            _var = _d[k]

            _row = mUI.MelHSingleStretchLayout(_shape_inside,ut='cgmUISubTemplate',padding = 5)

            mUI.MelSpacer(_row,w=5)                      
            mUI.MelLabel(_row,l='Create {0}:'.format(k))
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

        #>>>Create Size Modes -------------------------------------------------------------------------------------
        _row_createSize = mUI.MelHSingleStretchLayout(_shape_inside,ut='cgmUISubTemplate')
        mUI.MelSpacer(_row_createSize,w=5)                                              
        mUI.MelLabel(_row_createSize,l='Size Mode:')
        _row_createSize.setStretchWidget(mUI.MelSeparator(_row_createSize)) 

        uiRC = mUI.MelRadioCollection()
        _on = self.var_createSizeMode.value
        #self.var_createSizeValue
        for i,item in enumerate(['guess','fixed','cast']):
            if i == _on:
                _rb = True
            else:_rb = False

            uiRC.createButton(_row_createSize,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(self.var_createSizeMode.setValue,i))
            mUI.MelSpacer(_row_createSize,w=2)    


        cgmUI.add_Button(_row_createSize,'Size',
                         lambda *a:self.var_createSizeValue.uiPrompt_value('Set Size'),
                         'Set the create size value')   
        cgmUI.add_Button(_row_createSize,'Mutltiplier',
                         lambda *a:self.var_createSizeMulti.uiPrompt_value('Set create size multiplier'),
                         'Set the create size multiplier value') 
        mUI.MelSpacer(_row_createSize,w=5)                                              

        _row_createSize.layout()  

        #>>>Create -------------------------------------------------------------------------------------
        #_row_curveCreate = mUI.MelHSingleStretchLayout(_shape_inside,ut='cgmUISubTemplate') 
        _row_curveCreate = mUI.MelHLayout(_shape_inside,ut='cgmUISubTemplate',padding = 5)   

        cgmUI.add_Button(_row_curveCreate,'Create',
                         lambda *a:TOOLBOX.uiFunc_createCurve(),
                         'Create control curves from stored optionVars. Shape: {0} | Color: {1} | Direction: {2}'.format(self.var_curveCreateType.value,
                                                                                                                         self.var_defaultCreateColor.value,
                                                                                                                         SHARED._l_axis_by_string[self.var_createAimAxis.value]))                    
        #mUI.MelSpacer(_row_curveCreate,w=10)                                              
        cgmUI.add_Button(_row_curveCreate,'One of each',
                         lambda *a:TOOLBOX.uiFunc_createOneOfEach(),
                         'Create one of each curve stored in cgm libraries. Size: {0} '.format(self.var_createSizeValue.value) )       

        _row_curveCreate.layout()  
        
        self.buildRow_resizeObj(_shape_inside)
        self.buildRow_mirrorCurve(_shape_inside)        
        self.buildRow_shapeUtils(_shape_inside)
        self.buildRow_colorControls(_shape_inside)        
        
        
    def buildSection_color(self,parent):
        _frame = mUI.MelFrameLayout(parent,label = 'Color',vis=True,
                                    collapse=self.var_colorFrameCollapse.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:self.var_colorFrameCollapse.setValue(0),
                                    collapseCommand = lambda:self.var_colorFrameCollapse.setValue(1)
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
        
        self.buildRow_color(_inside)
        
    def buildSection_aim(self,parent):
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
                  c = lambda *a:TOOLBOX.SNAPCALLS.snap_action(None,'aim','eachToLast'),
                  ann = "Aim snap in a from:to selection")
    
        mc.button(parent=_row_aim,
                  ut = 'cgmUITemplate',                  
                  l = 'Sel Order',
                  c = lambda *a:TOOLBOX.SNAPCALLS.snap_action(None,'aim','eachToNext'),
                  ann = "Aim in selection order from each to next")
    
        mc.button(parent=_row_aim,
                  ut = 'cgmUITemplate',                                    
                  l = 'First to Mid',
                  c = lambda *a:TOOLBOX.SNAPCALLS.snap_action(None,'aim','firstToRest'),
                  ann = "Aim the first object to the midpoint of the rest")  
        
        mc.button(parent=_row_aim,
                  l = 'AimCast',
                  ut = 'cgmUITemplate',                                                        
                  c = lambda *a:TOOLBOX.SNAPCALLS.aimSnap_start(None),
                  ann = "AimCast snap selected objects")           
    
        _row_aim.layout()   
        
        
        self.buildRow_aimMode(_inside)        
        self.buildSection_objDefaults(_inside,frame=False)
        
            
    def buildSection_snap(self,parent):
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
                  c = lambda *a:TOOLBOX.SNAPCALLS.snap_action(None,'point'),
                  ann = "Point snap in a from:to selection")

        mc.button(parent=_row_base,
                  l = 'Point - closest',
                  ut = 'cgmUITemplate',                    
                  c = lambda *a:TOOLBOX.SNAPCALLS.snap_action(None,'closestPoint'),
                  ann = "Closest point on target")    

        mc.button(parent=_row_base,
                  l = 'Parent',
                  ut = 'cgmUITemplate',                    
                  c = lambda *a:TOOLBOX.SNAPCALLS.snap_action(None,'parent'),
                  ann = "Parent snap in a from:to selection")
        mc.button(parent=_row_base,
                  l = 'Orient',
                  ut = 'cgmUITemplate',                  
                  c = lambda *a:TOOLBOX.SNAPCALLS.snap_action(None,'orient'),
                  ann = "Orient snap in a from:to selection")        
        mc.button(parent=_row_base,
                  l = 'RayCast',
                  ut = 'cgmUITemplate',                                                        
                  c = lambda *a:TOOLBOX.SNAPCALLS.raySnap_start(None),
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
                  c = lambda *a:TOOLBOX.SNAPCALLS.raySnap_start(None),
                  ann = "RayCast snap selected objects")
        mc.button(parent=_row_ray,
                  l = 'AimCast',
                  ut = 'cgmUITemplate',                                                        
                  c = lambda *a:TOOLBOX.SNAPCALLS.aimSnap_start(None),
                  ann = "AimCast snap selected objects")   
        mUI.MelSpacer(_row_ray,w=5)                                              
        _row_ray.layout()    """         

        #>>>Match snap -------------------------------------------------------------------------------------
        self.buildRow_matchMode(_inside)     

        _row_match = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_match,w=5)                                              
        mUI.MelLabel(_row_match,l='MatchSnap:')
        _row_match.setStretchWidget(mUI.MelSeparator(_row_match)) 

        mc.button(parent=_row_match,
                  l = 'Self',
                  ut = 'cgmUITemplate',                                                                    
                  c = cgmGen.Callback(MMCONTEXT.func_process, LOCINATOR.update_obj, None,'each','Match',False,**{'mode':'self'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                  ann = "Update selected objects to match object. If the object has no match object, a loc is created")
        mc.button(parent=_row_match,
                  ut = 'cgmUITemplate',                                                                            
                  l = 'Target',
                  c = cgmGen.Callback(MMCONTEXT.func_process, LOCINATOR.update_obj, None,'each','Match',False,**{'mode':'target'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                  ann = "Update the match object, not the object itself")
        mc.button(parent=_row_match,
                  ut = 'cgmUITemplate',                                                                            
                  l = 'Buffer',
                  #c = cgmGen.Callback(buttonAction,raySnap_start(_sel)),                    
                  c = cgmGen.Callback(LOCINATOR.update_obj,**{'mode':'buffer'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                  ann = "Update the buffer (if exists)")    
        mUI.MelSpacer(_row_match,w=5)                                              
        _row_match.layout()         

        #>>>Arrange snap -------------------------------------------------------------------------------------
        _row_arrange = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_arrange,w=5)                                              
        mUI.MelLabel(_row_arrange,l='Arrange:')
        _row_arrange.setStretchWidget(mUI.MelSeparator(_row_arrange)) 

        mc.button(parent=_row_arrange,
                  l = 'Along line(Even)',
                  ut = 'cgmUITemplate',                                                                                              
                  c = cgmGen.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{}),                                               
                  ann = "Layout on line from first to last item")
        mc.button(parent=_row_arrange,
                  l = 'Along line(Spaced)',
                  ut = 'cgmUITemplate',                                                                                              
                  c = cgmGen.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'spaced'}),                                               
                  ann = "Layout on line from first to last item closest as possible to original position")    
        mUI.MelSpacer(_row_arrange,w=5)                                              
        _row_arrange.layout()         


    def buildRow_mesh(self,parent):
        #>>>Match mode -------------------------------------------------------------------------------------
        _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l='Mesh:')
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        mc.button(parent=_row,
                  l = 'MeshTools',
                  ut = 'cgmUITemplate',
                  c = lambda *a: mc.evalDeferred(MESHTOOLS.go,lp=1),                  
                  ann = "LOCATORS")    
        mc.button(parent=_row,
                  l = 'abSymMesh',
                  ut = 'cgmUITemplate',
                  ann = "abSymMesh by Brendan Ross - fantastic tool for some blendshape work",                                                                                                       
                  c=lambda *a: mel.eval('abSymMesh'),)  
        mc.button(parent=_row,
                  l = 'abTwoFace',
                  ut = 'cgmUITemplate',        
                  ann = "abTwoFace by Brendan Ross - fantastic tool for splitting blendshapes",                                                                                                       
                  c=lambda *a: mel.eval('abTwoFace'),)         

        _row.layout()   

    def buildRow_shapeUtils(self,parent):
        #>>>Match mode -------------------------------------------------------------------------------------
        _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l='Shape:')
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        mc.button(parent=_row,
                  l = 'Parent',
                  ut = 'cgmUITemplate',
                  ann = "shapeParent in place with a from:to selection. Maya's version is not so good",                                                                                                                    
                  c = lambda *a:MMCONTEXT.func_process( RIGGING.shapeParent_in_place, None, 'lastFromRest','shapeParent'),
                  )   
        mc.button(parent=_row,
                  l = 'Combine',
                  ut = 'cgmUITemplate',
                  ann = "Combine selected shapes to the last transform",  
                  c = lambda *a:MMCONTEXT.func_process(MMCONTEXT.func_enumrate_all_to_last, RIGGING.shapeParent_in_place, None,'toFrom', **{'keepSource':False}),
                  )           


        mc.button(parent=_row,
                  ut = 'cgmUITemplate',
                  l = 'Add',
                  ann = "Add selected shapes to the last transform",                   
                  c = lambda *a:MMCONTEXT.func_enumrate_all_to_last(RIGGING.shapeParent_in_place, None,'toFrom', **{}),
                  )       

        mc.button(parent=_row,
                  ut = 'cgmUITemplate',
                  l = 'Replace',
                  ann = "Replace the last transforms shapes with the former ones.",                                                                                                                  
                  c = lambda *a:MMCONTEXT.func_process(
                      RIGGING.shapeParent_in_place,
                      None,'lastFromRest', 'replaceShapes',
                      **{'replaceShapes':True}),)             

        mc.button(parent=_row,
                  ut = 'cgmUITemplate',
                  l = 'Extract',
                  ann = "Extract selected shapes from their respective transforms",                  
                  c = lambda *a:MMCONTEXT.func_context_all(RIGGING.duplicate_shape,'selection','shape'),
                  )    

        mc.button(parent=_row,
                  ut = 'cgmUITemplate',
                  l = 'Describe',
                  ann = "Generate pythonic recreation calls for selected curve shapes", 
                  c =  lambda *a:MMCONTEXT.func_process( CURVES.get_python_call, None, 'all','describe'),                
                  ) 



        _row.layout()   

    def buildRow_skin(self,parent):
        #>>>Match mode -------------------------------------------------------------------------------------
        _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l='skin:')
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        mc.button(parent=_row,
                          l='Copy',
                          ut = 'cgmUITemplate',
                          ann = "Copy skin weights based on targets",                                                                                                                       
                          c = cgmGen.Callback(MMCONTEXT.func_process, SKIN.transfer_fromTo, None, 'firstToRest','Copy skin weights',True,**{}))           

        mc.button(parent=_row,
                  l='abWeightLifter',
                  ut = 'cgmUITemplate',
                  ann = "abWeightLifter by Brendan Ross - really good tool for transferring and working with skin data",                                                                                                                       
                  c=lambda *a: mel.eval('abWeightLifter'),)         
        mc.button(parent=_row,
                  l='ngSkinTools',
                  ut = 'cgmUITemplate',
                  ann = "Read the docs. Give it a chance. Be amazed.",                                                                                                                       
                  c=lambda *a: loadNGSKIN())           

        _row.layout()   
        
        
    def buildRow_constraints(self,parent):
        #>>>Match mode -------------------------------------------------------------------------------------
        _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l='Constraints:')
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        mc.button(parent=_row,
                  l='Get Targets',
                  ut = 'cgmUITemplate',
                  ann = "Get targets of contraints",                                                                                                                       
                  c = cgmGen.Callback(MMCONTEXT.func_process, CONSTRAINTS.get_targets, None, 'each','Get targets',True,**{'select':True}))           

        _row.layout()    
        
    def buildRow_resizeObj(self,parent):
        #>>>Match mode -------------------------------------------------------------------------------------
        _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l='resizeObj:')
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        mc.button(parent=_row,
                  ut = 'cgmUITemplate',                  
                  l = 'Make resizeObj',
                  ann = 'Make control a resize object so you can more easily shape it',                
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_controlResizeObj, None,'each','Resize obj'))        
        mc.button(parent=_row,
                  ut = 'cgmUITemplate', 
                  l = 'Push resizeObj changes',
                  ann = 'Push the control changes back to control',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.push_controlResizeObj, None,'each','Resize obj'))        
        _row.layout() 
        
    def buildRow_mirrorCurve(self,parent):
        #>>>Match mode -------------------------------------------------------------------------------------
        _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l='mirror:')
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        mc.button(parent=_row,
                  ut = 'cgmUITemplate',  
                  l = 'Mirror World Space To target',
                  ann = 'Given a selection of two curves, mirror across X (for now only x)',
                  c = cgmGen.Callback(CURVES.mirror_worldSpace))                   
        _row.layout()   
        

    def buildRow_aimMode(self,parent):
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
                              onCommand = cgmGen.Callback(self.var_aimMode.setValue,item))

            mUI.MelSpacer(_row,w=2)       


        _row.layout()      


    def buildRow_matchMode(self,parent):
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
                              onCommand = cgmGen.Callback(LOCINATOR.uiFunc_change_matchMode,self,i))

            mUI.MelSpacer(_row,w=2)       

        _row.layout()        

    def buildRow_context(self,parent):
        #>>>Match mode -------------------------------------------------------------------------------------
        _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l='Context:')
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        uiRC = mUI.MelRadioCollection()

        _on = self.var_contextTD.value

        for i,item in enumerate(['selection','children','heirarchy','scene']):
            if item == _on:
                _rb = True
            else:_rb = False

            uiRC.createButton(_row,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(self.var_contextTD.setValue,item))

            mUI.MelSpacer(_row,w=2)       

        _row.layout()

    def buildRow_colorControls(self,parent):
        _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate')
        mUI.MelSpacer(_row,w=5)  
        
        uiGrid_colorSwatch_index = mc.gridLayout(aec = False, numberOfRowsColumns=(1,9), cwh = (30,20),cr=True)
        
        i = 0
        for side in ['left','center','right']:
            for typ in ['main','sub','direct']:
                colorName = SHARED._d_side_colors[side][typ]
                colorBuffer = SHARED._d_colors_to_RGB.get(colorName,[0,0,0])
                RIGGING.colorControl
                mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=colorBuffer,                      
                          pc = cgmGen.Callback(MMCONTEXT.func_process,RIGGING.colorControl,None,'each',noSelect = False,**{'direction':side,'controlType':typ, 'transparent':True}),                        
                          annotation = 'Sets color by rgb to {0}'.format(colorName))    
                
                i+=1

        _row.setStretchWidget( mUI.MelSeparator(_row) )
                
        mc.button(parent = _row,
                  ut = 'cgmUITemplate',                                                                                                
                  l='Clr*',
                  ann = "Clear override settings on contextual objects.",                                                                                                                                       
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.override_clear, None, 'each','Clear override',True,**{'context':None}))           
        
        mUI.MelSpacer(_row,w=5)  
        
        _row.layout()
        return
        #_row_index = mUI.MelColumnLayout(parent)
        #mc.columnLayout(columnAttach = ('both',5),backgroundColor = [.2,.2,.2])
        cgmUI.add_Header('Index*')        
        uiGrid_colorSwatch_index = mc.gridLayout(aec = False, numberOfRowsColumns=(2,15), cwh = (27,14),cr=True)
        colorSwatchesList = [1,2,3,11,24,21,12,10,25,4,13,20,8,30,9,5,6,18,15,29,28,7,27,19,23,26,14,17,22,16]
        for i in colorSwatchesList:
            colorBuffer = mc.colorIndex(i, q=True)
            mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=colorBuffer,                      
                      pc = cgmGen.Callback(MMCONTEXT.color_override,i,None,'shape'),                        
                      annotation = 'Sets the color of the object to this')

        #_row.layout() 
        #_row_rbg
        mc.setParent(parent)
        cgmUI.add_Header('RGB*')
        uiGrid_colorSwatch_index = mc.gridLayout(aec = False, numberOfRowsColumns=(2,15), cwh = (27,14),cr=True)
        _IndexKeys = SHARED._d_colorSetsRGB.keys()
        i = 0
        for k1 in _IndexKeys:
            _keys2 = SHARED._d_colorSetsRGB.get(k1,[])
            _sub = False
            if _keys2:_sub = True
            colorBuffer = SHARED._d_colors_to_RGB[k1]
            mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=colorBuffer,                      
                      pc = cgmGen.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[k1],None,'shape'),                        
                      annotation = 'Sets color by rgb to {0}'.format(k1))            
            
            i+=1

            if _sub:                  
                for k2 in _keys2:
                    _buffer = "{0}{1}".format(k1,k2)
                    #log.info( SHARED._d_colors_to_RGB[_buffer] )
                    mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=SHARED._d_colors_to_RGB[_buffer],                      
                              pc = cgmGen.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[_buffer],None,'shape'),                        
                              annotation = 'Sets color by rgb to {0}'.format(k2))            
                    i+=1

    def buildRow_color(self,parent):
        mc.button(parent = parent,
                  ut = 'cgmUITemplate',                                                                                                
                  l='Clear Override*',
                  ann = "Clear override settings on contextual objects.",                                                                                                                                       
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.override_clear, None, 'each','Clear override',True,**{'context':None}))           
        
        #_row_index = mUI.MelColumnLayout(parent)
        #mc.columnLayout(columnAttach = ('both',5),backgroundColor = [.2,.2,.2])
        cgmUI.add_Header('Index*')        
        uiGrid_colorSwatch_index = mc.gridLayout(aec = False, numberOfRowsColumns=(2,10), cwh = (27,14),cr=True)
        colorSwatchesList = [1,2,3,11,24,21,12,10,25,4,13,20,8,30,9,5,6,18,15,29,28,7,27,19,23,26,14,17,22,16]
        for i in colorSwatchesList:
            colorBuffer = mc.colorIndex(i, q=True)
            mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=colorBuffer,                      
                      pc = cgmGen.Callback(MMCONTEXT.color_override,i,None,'shape'),                        
                      annotation = 'Sets the color of the object to this')

        #_row.layout() 
        #_row_rbg
        mc.setParent(parent)
        cgmUI.add_Header('RGB*')
        uiGrid_colorSwatch_index = mc.gridLayout(aec = False, numberOfRowsColumns=(2,10), cwh = (27,14),cr=True)
        _IndexKeys = SHARED._d_colorSetsRGB.keys()
        i = 0
        for k1 in _IndexKeys:
            _keys2 = SHARED._d_colorSetsRGB.get(k1,[])
            _sub = False
            if _keys2:_sub = True
            colorBuffer = SHARED._d_colors_to_RGB[k1]
            mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=colorBuffer,                      
                      pc = cgmGen.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[k1],None,'shape'),                        
                      annotation = 'Sets color by rgb to {0}'.format(k1))            
            
            i+=1

            if _sub:                  
                for k2 in _keys2:
                    _buffer = "{0}{1}".format(k1,k2)
                    #log.info( SHARED._d_colors_to_RGB[_buffer] )
                    mc.canvas(('%s%i' %('colorCanvas_',i)),rgb=SHARED._d_colors_to_RGB[_buffer],                      
                              pc = cgmGen.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[_buffer],None,'shape'),                        
                              annotation = 'Sets color by rgb to {0}{1}'.format(k1,k2))            
                    i+=1
                    
        mc.setParent(parent)
        cgmUI.add_Header('Side defaults*')
        self.buildRow_colorControls(parent)
        
        """
        for k1 in _IndexKeys:
            _keys2 = SHARED._d_colorSetsRGB.get(k1,[])
            _sub = False
            if _keys2:_sub = True
    
            mc.menuItem(parent=uiRGBShape,subMenu = _sub,
                        en = True,
                        ann = "Set overrideColor by {0} to {1}...".format(ctxt,k1),                                                                                                        
                        l=k1,
                        c=cgmGen.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[k1],ctxt,'shape'))
    
            if _sub:
                mc.menuItem(en = True,
                            l=k1,
                            c=cgmGen.Callback(MMCONTEXT.color_override,k1,ctxt,'shape'))                    
                for k2 in _keys2:
                    _buffer = "{0}{1}".format(k1,k2)
                    mc.menuItem(en = True,
                                ann = "Set overrideColor by {0} to {1}".format(ctxt,k2),                                                                                                                                            
                                l=_buffer,
                                c=cgmGen.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[_buffer],ctxt,'shape'))              
          """
        
    def buildSection_animOptions(self,parent):
        _frame = mUI.MelFrameLayout(parent,label = 'Anim Options',vis=True,
                                    collapse=self.var_animOptionsFrameCollapse.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:self.var_animOptionsFrameCollapse.setValue(0),
                                    collapseCommand = lambda:self.var_animOptionsFrameCollapse.setValue(1)
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 


        #>>>KeyMode ====================================================================================
        uiRC = mUI.MelRadioCollection()

        _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row1,w=5)
        mUI.MelLabel(_row1,l='KeyMode')
        _row1.setStretchWidget( mUI.MelSeparator(_row1) )

        uiRC = mUI.MelRadioCollection()
        _on = self.var_keyMode.value

        for i,item in enumerate(['Default','Channelbox']):
            if i == _on:
                _rb = True
            else:_rb = False

            uiRC.createButton(_row1,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(self.var_keyMode.setValue,i))

            mUI.MelSpacer(_row1,w=2)    

        _row1.layout()   
        
        #>>>KeyType ====================================================================================
        uiRC = mUI.MelRadioCollection()

        _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row1,w=5)
        mUI.MelLabel(_row1,l='Key Type')
        _row1.setStretchWidget( mUI.MelSeparator(_row1) )

        uiRC = mUI.MelRadioCollection()
        _on = self.var_keyType.value

        for i,item in enumerate(['reg','breakdown']):
            if i == _on:
                _rb = True
            else:_rb = False

            uiRC.createButton(_row1,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(self.var_keyType.setValue,i))

            mUI.MelSpacer(_row1,w=2)    

        _row1.layout()   
        
        #>>>Reset mode ====================================================================================
        uiRC = mUI.MelRadioCollection()

        _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row1,w=5)
        mUI.MelLabel(_row1,l='Reset Mode')
        _row1.setStretchWidget( mUI.MelSeparator(_row1) )

        uiRC = mUI.MelRadioCollection()
        _on = self.var_resetMode.value

        for i,item in enumerate(['Default','Transform Attrs']):
            if i == _on:
                _rb = True
            else:_rb = False

            uiRC.createButton(_row1,label=item,sl=_rb,
                              onCommand = cgmGen.Callback(self.var_resetMode.setValue,i))

            mUI.MelSpacer(_row1,w=2)    

        _row1.layout()         
        
    def buildSection_transform(self,parent):
        _frame = mUI.MelFrameLayout(parent,label = 'Transform',vis=True,
                                    collapse=self.var_transformFrameCollapse.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:self.var_transformFrameCollapse.setValue(0),
                                    collapseCommand = lambda:self.var_transformFrameCollapse.setValue(1)
                                    )	
        TOOLBOX.TT.buildColumn_main(self,_frame)   
        
    def buildSection_rayCast(self,parent):
        _frame = mUI.MelFrameLayout(parent,label = 'Raycast',vis=True,
                                    collapse=self.var_rayCastFrameCollapse.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:self.var_rayCastFrameCollapse.setValue(0),
                                    collapseCommand = lambda:self.var_rayCastFrameCollapse.setValue(1)
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 


        #>>>Raycast ====================================================================================

        #>>>Cast Mode  -------------------------------------------------------------------------------------
        uiRC = mUI.MelRadioCollection()
        _on = self.var_rayCastMode.value

        _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)


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

        _row_offset = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
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

        _row_orient = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
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
        mUI.MelSpacer(_row_orient,w=5)                                                  
        _row_orient.layout()

        #>>>rayCast -------------------------------------------------------------------------------------
        _row_rayCast = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_rayCast,w=5)                                              
        mUI.MelLabel(_row_rayCast,l='rayCast:')
        _row_rayCast.setStretchWidget(mUI.MelSeparator(_row_rayCast)) 


        self.uiField_rayCastCreate = mUI.MelLabel(_row_rayCast,
                                                  ann='Change the default rayCast create type',
                                                  ut='cgmUIInstructionsTemplate',w=100)        
        self.uiField_rayCastCreate(edit=True, label = self.var_createRayCast.value)

        self.uiPopup_createRayCast()       

        mc.button(parent=_row_rayCast,
                  ut = 'cgmUITemplate',                                                                              
                  l = 'Create',
                  c = lambda a: SNAPCALLS.rayCast_create(None,self.var_createRayCast.value,False),
                  ann = TOOLANNO._d['raycast']['create'])       
        mc.button(parent=_row_rayCast,
                  ut = 'cgmUITemplate',                                                                              
                  l = 'Drag',
                  c = lambda a: SNAPCALLS.rayCast_create(None,self.var_createRayCast.value,True),
                  ann = TOOLANNO._d['raycast']['drag'])       
        """
            mUI.MelLabel(_row_rayCast,
                         l=' | ')

            mc.button(parent=_row_rayCast,
                      ut = 'cgmUITemplate',                                                                              

                    l = 'RayCast Snap',
                    c = lambda *a:SNAPCALLS.raySnap_start(None),
                    ann = "RayCast snap selected objects")
            mc.button(parent=_row_rayCast,
                      ut = 'cgmUITemplate',                                                                                                
                      l = 'AimCast',
                      c = lambda *a:SNAPCALLS.aimSnap_start(None),
                      ann = "AimCast snap selected objects") """   

        mUI.MelSpacer(_row_rayCast,w=5)                                                  
        _row_rayCast.layout()

    def buildSection_objDefaults(self,parent,frame=True):
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
                                  onCommand = cgmGen.Callback(_var.setValue,i))

                mUI.MelSpacer(_row,w=2)       


            _row.layout() 


        #>>>Buttons -------------------------------------------------------------------------------------
        _row_defaults = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5, )

        cgmUI.add_Button(_row_defaults,'Tag selected for aim',
                         lambda *a:MMCONTEXT.func_process(SNAP.verify_aimAttrs, mc.ls(sl=True),'each','Verify aim attributes',True,**{}),)                                       
        _row_defaults.layout() 
    
         

    def buildSection_distance(self,parent):
        _frame = mUI.MelFrameLayout(parent,label = 'Distance',vis=True,
                                    collapse=self.var_distanceFrameCollapse.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:self.var_distanceFrameCollapse.setValue(0),
                                    collapseCommand = lambda:self.var_distanceFrameCollapse.setValue(1)
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 

        #>>>Distance -------------------------------------------------------------------------------------
        _row_dist= mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_dist,w=5)                                              
        mUI.MelLabel(_row_dist,l='Distance:')
        _row_dist.setStretchWidget(mUI.MelSeparator(_row_dist)) 
        
        self.uiFF_distance = mUI.MelFloatField(_row_dist, ut='cgmUISubTemplate', w= 50)
        """self.uiFF_distance = mUI.MelLabel(_row_dist,
                                          l='21231',
                                          ann='Change the default create shape',
                                          ut='cgmUIInstructionsTemplate',w=100)"""        
        mc.button(parent=_row_dist,
                  ut = 'cgmUITemplate',                                                                                                
                  l = 'Measure',
                  c = lambda *a:TOOLBOX.uiFunc_distanceMeastureToField(self),
                  #c = lambda *a:SNAPCALLS.aimSnap_start(None),
                  ann = "Measures distance between selected objects/components")        
        
        _row_dist.layout()
        
        #>>>Vector -------------------------------------------------------------------------------------
        _row_vec= mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_vec,w=5)                                              
        mUI.MelLabel(_row_vec,l='Vector:')        
        _row_vec.setStretchWidget(mUI.MelSeparator(_row_vec)) 

        for a in list('xyz'):
            mUI.MelLabel(_row_vec,l=a)
            self.__dict__['uiFF_vec{0}'.format(a.capitalize())] = mUI.MelFloatField(_row_vec, ut='cgmUISubTemplate', w= 50 )
            
        mc.button(parent=_row_vec,
                  ut = 'cgmUITemplate',                                                                                                
                  l = 'Measure',
                  c = lambda *a:TOOLBOX.uiFunc_vectorMeasureToField(self),
                  ann = "Measures vector between selected objects/components")        
        

        _row_vec.layout()
        
        
        #>>>Near -------------------------------------------------------------------------------------
        _row_near = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_near,w=5)                                              
        mUI.MelLabel(_row_near,l='Near:')
        _row_near.setStretchWidget(mUI.MelSeparator(_row_near)) 

        mc.button(parent=_row_near, 
                  ut = 'cgmUITemplate',                                                                              
                  l = 'Target',
                  ann = "Find nearest target in from:to selection list",
                  c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Near Target',True,**{'mode':'closest','resMode':'object'}),                                                                      
                  )   
        mc.button(parent=_row_near, 
                  ut = 'cgmUITemplate', 
                  l = 'Shape',
                  ann = "Find nearest shape in  from:to selection list",                    
                  c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Near Shape',True,**{'mode':'closest','resMode':'shape'}),                                                                      
                  )               
        mc.button(parent=_row_near, 
                  ut = 'cgmUITemplate',
                  l = 'Surface Point',
                  ann = "Find nearest surface point in from:to selection list",                    
                  c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Near point on surface',True,**{'mode':'closest','resMode':'pointOnSurface'}),                                                                      
                  )     
        mc.button(parent=_row_near, 
                  ut = 'cgmUITemplate',
                  l = 'Surface Loc',
                  ann = "Find nearest surface point in from:to selection list. And loc it.",                                        
                  c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Near point on surface',True,**{'mode':'closest','resMode':'pointOnSurfaceLoc'}),                                                                      
                  )               
        mc.button(parent=_row_near, 
                  ut = 'cgmUITemplate',
                  l = 'Surface Nodes',
                  ann = "Create nearest surface point nodes in from:to selection list",                                        
                  c = cgmGen.Callback(MMCONTEXT.func_process, DIST.create_closest_point_node, None,'firstToEach','Create closest Point Node',True,**{}),                                                                      
                  )      

        mUI.MelSpacer(_row_near,w=5)                                              
        _row_near.layout()   

        #>>>Far -------------------------------------------------------------------------------------
        _row_far = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_far,w=5)                                              
        mUI.MelLabel(_row_far,l='far:')
        _row_far.setStretchWidget(mUI.MelSeparator(_row_far)) 

        mc.button(parent=_row_far, 
                  ut = 'cgmUITemplate',
                  l = 'Target',
                  ann = "Find furthest taregt in from:to selection list",                                        
                  c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Far Target',True,**{'mode':'far','resMode':'object'}),                                                                      
                  )                  
        mc.button(parent=_row_far, 
                  ut = 'cgmUITemplate',
                  l = 'Shape',
                  ann = "Find furthest shape in from:to selection list",                                        
                  c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, None,'firstToRest','Far Shape',True,**{'mode':'far','resMode':'shape'}),                                                                      
                  )   

        mUI.MelSpacer(_row_far,w=5)                                              
        _row_far.layout()           




    def buildSection_rigging(self,parent):
        _frame = mUI.MelFrameLayout(parent,label = 'Rigging',vis=True,
                                    collapse=self.var_tdFrameCollapse.value,
                                    collapsable=True,
                                    enable=True,
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:self.var_tdFrameCollapse.setValue(0),
                                    collapseCommand = lambda:self.var_tdFrameCollapse.setValue(1)
                                    )	
        _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 

        _row_tools1 = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)

        mc.button(parent=_row_tools1,
                  l = 'DynParent Tool',
                  ut = 'cgmUITemplate',
                  c = lambda *a: mc.evalDeferred(DYNPARENTTOOL.ui,lp=1),                  
                  ann = "Tool for modifying and setting up dynamic parent groups")

        mc.button(parent=_row_tools1,
                  l = 'Locinator',
                  ut = 'cgmUITemplate',
                  c = lambda *a: mc.evalDeferred(LOCINATOR.ui,lp=1),                  
                  ann = "LOCATORS")

        _row_tools1.layout()                  


        #>>>Create -------------------------------------------------------------------------------------
        _row_create = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_create,w=5)                                              
        mUI.MelLabel(_row_create,l='Create from selected:')
        _row_create.setStretchWidget(mUI.MelSeparator(_row_create)) 

        mc.button(parent=_row_create,
                  ut = 'cgmUITemplate',                    
                  l = 'Transform',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'each','Create Tranform',**{'create':'null'}))    

        mc.button(parent=_row_create,
                  ut = 'cgmUITemplate',                                        
                  l = 'Joint',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_joint_at, None,'each','Create Joint'))         
        mc.button(parent=_row_create,
                  ut = 'cgmUITemplate',                                        
                  l = 'Locator',
                  c = cgmGen.Callback(MMCONTEXT.func_process, LOC.create, None,'each','Create Loc'))                          
        mc.button(parent=_row_create,
                  ut = 'cgmUITemplate',                                        
                  l = 'Curve',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Curve',**{'create':'curve'}))                          

        mUI.MelSpacer(_row_create,w=5)                                              
        _row_create.layout()  

        #>>>Copy -------------------------------------------------------------------------------------
        _row_copy = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_copy,w=5)                                              
        mUI.MelLabel(_row_copy,l='Copy:')
        _row_copy.setStretchWidget(mUI.MelSeparator(_row_copy)) 

        mc.button(parent=_row_copy,
                  ut = 'cgmUITemplate',                                        
                  l = 'Transform',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.match_transform, None,'eachToFirst','Match Transform'),                    
                  ann = "")
        mc.button(parent=_row_copy,
                  ut = 'cgmUITemplate',                                        
                  l = 'Orienation',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.match_orientation, None,'eachToFirst','Match Orientation'),                    
                  ann = "")

        mc.button(parent=_row_copy,
                  ut = 'cgmUITemplate',                                        
                  l = 'Shapes',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.shapeParent_in_place, None,'lastFromRest','Copy Shapes', **{'snapFirst':True}),
                  ann = "")


        #Pivot stuff -------------------------------------------------------------------------------------------
        mc.button(parent=_row_copy,
                  ut = 'cgmUITemplate',                                                          
                  l = 'rotatePivot',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.copy_pivot, None,'eachToFirst', 'Match RP',**{'rotatePivot':True,'scalePivot':False}),                                               
                  ann = "Copy the rotatePivot from:to")
        mc.button(parent=_row_copy,
                  ut = 'cgmUITemplate',                                        
                  l = 'scalePivot',
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.copy_pivot, None,'eachToFirst', 'Match SP', **{'rotatePivot':False,'scalePivot':True}),                                               
                  ann = "Copy the scalePivot from:to")        


        mUI.MelSpacer(_row_copy,w=5)                                              
        _row_copy.layout()    
        
        TOOLBOX.buildRow_parent(self,_inside)

        #>>>group -------------------------------------------------------------------------------------
        _row_group = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_group,w=5)                                              
        mUI.MelLabel(_row_group,l='Group:')
        _row_group.setStretchWidget(mUI.MelSeparator(_row_group)) 

        mc.button(parent=_row_group,
                  ut = 'cgmUITemplate',                                                          
                  l = 'Just Group',
                  ann = 'Simple grouping. Just like ctrl + g',                        
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.group_me, None,'each','Group',**{'parent':False,'maintainParent':False}),)  
        mc.button(parent=_row_group,
                  ut = 'cgmUITemplate',                                                          
                  l = 'Group Me',
                  ann = 'Group selected objects matching transform as well.',                                        
                  #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.group_me, None,'each','Group',**{'parent':True,'maintainParent':False}))          
        mc.button(parent=_row_group,
                  ut = 'cgmUITemplate',                                                          
                  l = 'In Place',
                  ann = 'Group me while maintaining heirarchal position',                                                        
                  c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.group_me, None,'each','Group In Place',**{'parent':True,'maintainParent':True}))     

        mUI.MelSpacer(_row_group,w=5)                                              
        _row_group.layout()      


        #>>>Attr -------------------------------------------------------------------------------------
        _row_attr = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_attr,w=5)                                              
        mUI.MelLabel(_row_attr,l='Attr:')
        _row_attr.setStretchWidget(mUI.MelSeparator(_row_attr)) 


        self.uiField_attrType = mUI.MelLabel(_row_attr,
                                             ann='Change the default attr type',
                                             ut='cgmUIInstructionsTemplate',w=100)        
        self.uiField_attrType(edit=True, label = self.var_attrCreateType.value)
        mc.button(parent = _row_attr,
                  ut = 'cgmUITemplate',                                                                            
                  l='+',
                  ann = "Add specified attribute type",  
                  c = lambda *a:ATTRTOOLS.uiPrompt_addAttr(self.var_attrCreateType.value))
                  #c = cgmGen.Callback(ATTRTOOLS.uiPrompt_addAttr,self.var_attrCreateType.value,**{}))
        self.uiPopup_createAttr()


        mc.button(parent = _row_attr,
                  ut = 'cgmUITemplate',                                                                            
                  l='cgmAttrTools',
                  ann = "Launch cgmAttrTools - Collection of tools for making creating, editing and managing attributes a little less painful",                                                                                                                       
                  c=cgmGen.Callback(ATTRTOOLS.ui))   

        """
        _add = mc.menuItem(parent=uiAttr,subMenu=True,
                           l='Add',
                           ann = "Add attributes to selected objects...",                                                                                                                              
                           rp='S') 
        _d_attrTypes = {"string":'E','float':'S','enum':'NE','vector':'SW','int':'W','bool':'NW','message':'SE'}
        for _t,_d in _d_attrTypes.iteritems():
            mc.menuItem(parent=_add,
                        l=_t,
                        ann = "Add a {0} attribute(s) to the selected objects".format(_t),                                                                                                       
                        c = cgmGen.Callback(ATTRTOOLS.uiPrompt_addAttr,_t,**{'autoLoadFail':True}),
                        rp=_d)"""

        mc.button(parent = _row_attr,
                  ut = 'cgmUITemplate',                                                                              
                  l = 'Compare Attrs',
                  ann = "Compare the attributes of selected objects. First object is the base of comparison",                                                                                                                                                
                  c = cgmGen.Callback(MMCONTEXT.func_process, ATTR.compare_attrs, None, 'firstToRest','Compare Attrs',True,**{}))           

        mUI.MelSpacer(_row_attr,w=5)                                              
        _row_attr.layout()         


        #>>>
        self.buildRow_shapeUtils(_inside)

        #>>>Joints -------------------------------------------------------------------------------------
        _row_joints = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
        mUI.MelSpacer(_row_joints,w=5)                                              
        mUI.MelLabel(_row_joints,l='Joints:')
        _row_joints.setStretchWidget(mUI.MelSeparator(_row_joints)) 


        mc.button(parent=_row_joints, 
                  ut = 'cgmUITemplate',                                                                              
                  l = '*Show x',
                  ann = "Show the joint axis by current context",                                        
                  c= lambda *a:MMCONTEXT.set_attrs(self,'displayLocalAxis',1,self.var_contextTD.value,'joint',select=False),
                  )               
        mc.button(parent=_row_joints, 
                  ut = 'cgmUITemplate',                                                                              
                  l = '*Hide x',
                  ann = "Hide the joint axis by current context",                                        
                  c= lambda *a:MMCONTEXT.set_attrs(self,'displayLocalAxis',0,self.var_contextTD.value,'joint',select=False),
                  )     


        mc.button(parent = _row_joints,
                  ut = 'cgmUITemplate',                                                                                                
                  l='cometJO',
                  c=lambda *a: mel.eval('cometJointOrient'),
                  ann="General Joint orientation tool  by Michael Comet")   
        mc.button(parent=_row_joints, 
                  ut = 'cgmUITemplate',                                                                              
                  l = 'Freeze',
                  ann = "Freeze the joint orientation - our method as we don't like Maya's",                                        
                  c = cgmGen.Callback(MMCONTEXT.func_process, JOINTS.freezeOrientation, None, 'each','freezeOrientation',False,**{}),                                                                      
                  )            


        mc.button(parent = _row_joints,
                  ut = 'cgmUITemplate',                                                                                                
                  l='seShapeTaper',
                  ann = "Fantastic blendtaper like tool for sdk poses by our pal - Scott Englert",                                                        
                  c=lambda *a: mel.eval('seShapeTaper'),)   

        mUI.MelSpacer(_row_joints,w=5)                                              
        _row_joints.layout()          


        self.buildRow_mesh(_inside)
        self.buildRow_skin(_inside)
        self.buildRow_constraints(_inside)

    def buildTab_anim(self,parent):
        _column = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
        parent(edit = True,
               af = [(_column,"top",0),
                     (_column,"left",0),
                     (_column,"right",0),                        
                     (_column,"bottom",0)])    

        #>>>Shape Creation ====================================================================================
        mc.setParent(_column)

        self.buildSection_snap(_column)
        self.buildSection_aim(_column)

        mc.button(parent = _column,
                  ut = 'cgmUITemplate',                                                                                                
                  l='cgmLocinator',
                  ann = "Launch cgmLocinator - a tool for aiding in the snapping of things",                                                                                                                                       
                  c=lambda *a: LOCINATOR.ui()) 

        mc.button(parent = _column,
                  ut = 'cgmUITemplate',  
                  l='cgmDynParentTool',
                  ann = "Launch cgm's dynParent Tool - a tool for assisting space switching setups and more",                                                                                                                                       
                  c=lambda *a: DYNPARENTTOOL.ui())   
        mc.button(parent = _column,
                  ut = 'cgmUITemplate',  
                  l='cgmTransformTools',
                  ann = "Launch cgmTransformTools - a tool for tweaking values",                                                                                                                                       
                  c=lambda *a: TOOLBOX.TT.ui())  
        
        mc.button(parent = _column,
                  ut = 'cgmUITemplate',  
                  l='autoTangent',
                  ann = "autoTangent by Michael Comet - an oldie but a goodie for those who loathe the graph editor",                                                                                                                                   
                  c=lambda *a: mel.eval('autoTangent'))
        mc.button(parent = _column,
                  ut = 'cgmUITemplate',  
                  l='tweenMachine',
                  ann = "tweenMachine by Justin Barrett - Fun little tweening tool",                                                                                                                                                   
                  c=lambda *a: mel.eval('tweenMachine'))
        mc.button(parent = _column,
                  ut = 'cgmUITemplate',  
                  l='mlArcTracer',
                  ann = "mlArcTracer by Morgan Loomis",                                                                                                                                                                   
                  c=lambda *a: ml_arcTracer.ui())         
        mc.button(parent = _column,
                  ut = 'cgmUITemplate',  
                  l='mlCopyAnim',
                  ann = "mlCopyAnim by Morgan Loomis",                                                                                                                                                                                   
                  c=lambda *a: ml_copyAnim.ui())         
        mc.button(parent = _column,
                  ut = 'cgmUITemplate',  
                  l='mlHold',
                  ann = "mlHold by Morgan Loomis",
                  c=lambda *a: ml_hold.ui())  
        mc.button(parent = _column,
                  ut = 'cgmUITemplate',  
                  l='red9.Studio Tools',
                  ann = "Launch Red 9's tools",
                  c=lambda *a:Red9.start())           




    def buildTab_legacy(self,parent):
        _column = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
        parent(edit = True,
               af = [(_column,"top",0),
                     (_column,"left",0),
                     (_column,"right",0),                        
                     (_column,"bottom",0)])    

        #>>>Shape Creation ====================================================================================
        mc.setParent(_column)

        cgmUI.add_Button(_column,
                         'AnimTools',
                         lambda a:loadAnimTools(),
                         "Old simple anim tool holder")

        cgmUI.add_Button(_column,
                         'SetTools 1.0',
                         lambda a:loadSetTools(),
                         "Old object set tool window. Crashy. Use with caution")        

        cgmUI.add_Button(_column,
                         'Locinator 1.0',
                         lambda a:loadLocinator(),
                         "Original Tool for creating, updating, locators")

        cgmUI.add_Button(_column,
                         'tdTools 1.0',
                         lambda a:loadTDTools(),
                         "Series of tools for general purpose TD work - curves, naming, position, deformers") 

        cgmUI.add_Button(_column,
                         'attrTools 1.0',
                         lambda a:loadAttrTools(),
                         "Old attribute tools")




    def buildTab_td(self,parent):
        _column = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
        parent(edit = True,
               af = [(_column,"top",0),
                     (_column,"left",0),
                     (_column,"right",0),                        
                     (_column,"bottom",0)])    

        #>>>Shape Creation ====================================================================================
        mc.setParent(_column)
        

        """
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
                            c = mmCallback(self.var_contextTD.setValue,item),                                  
                            #c = lambda *a:self.raySnap_setAndStart(self.var_rayCastMode.setValue(i)),                                  
                            rb = _rb)                        
        """




        #>>>Tools -------------------------------------------------------------------------------------  
        self.buildRow_context(_column)                     
        
        self.buildSection_snap(_column)
        cgmUI.add_HeaderBreak()        
        
        self.buildSection_aim(_column)
        cgmUI.add_HeaderBreak()   

        self.buildSection_rigging(_column)
        
        cgmUI.add_SectionBreak()  
        self.buildSection_transform(_column)
        cgmUI.add_SectionBreak()  
                
        self.buildSection_shape(_column)
        cgmUI.add_SectionBreak()            

        self.buildSection_color(_column)
        cgmUI.add_SectionBreak()  

        self.buildSection_rayCast(_column)
        cgmUI.add_SectionBreak()      

        self.buildSection_distance(_column)


    def buildTab_options(self,parent):
        _column = mUI.MelScrollLayout(parent,useTemplate = 'cgmUITemplate') 
        parent(edit = True,
               af = [(_column,"top",0),
                     (_column,"left",0),
                     (_column,"right",0),                        
                     (_column,"bottom",0)])        

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
        self.buildRow_matchMode(_update_inside)     


        #>>>Aim ====================================================================================
        mc.setParent(_column)
        #cgmUI.add_SectionBreak()        
        _aim_frame = mUI.MelFrameLayout(_column,label = 'Aim Options',vis=True,
                                        collapse=self.var_aimOptionsFrameCollapse.value,
                                        collapsable=True,
                                        enable=True,
                                        useTemplate = 'cgmUIHeaderTemplate',
                                        expandCommand = lambda:self.var_aimOptionsFrameCollapse.setValue(0),
                                        collapseCommand = lambda:self.var_aimOptionsFrameCollapse.setValue(1)
                                        )	
        _aim_inside = mUI.MelColumnLayout(_aim_frame,useTemplate = 'cgmUISubTemplate')  


        #>>>Aim mode -------------------------------------------------------------------------------------
        self.buildRow_aimMode(_aim_inside)
        """
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


        _row_aimFlags.layout()"""


        self.buildSection_objDefaults(_column)
        #self.buildSection_rayCast(_column)
        self.buildSection_animOptions(_column)

    def cb_setCreateShape(self,shape):
        self.var_curveCreateType.setValue(shape)
        self.uiField_shape(edit=True,label=shape)
        return True

    def uiPopup_createShape(self):
        if self.uiPopUpMenu_createShape:
            self.uiPopUpMenu_createShape.clear()
            self.uiPopUpMenu_createShape.delete()
            self.uiPopUpMenu_createShape = None

        self.uiPopUpMenu_createShape = mUI.MelPopupMenu(self.uiField_shape,button = 1)
        _popUp = self.uiPopUpMenu_createShape 

        mUI.MelMenuItem(_popUp,
                        label = "Set shape",
                        en=False)     
        mUI.MelMenuItemDiv(_popUp)

        for k,l in CURVES._d_shapeLibrary.iteritems():
            _k = mUI.MelMenuItem(_popUp,subMenu = True,
                                 label = k,
                                 en=True)
            for o in l:
                mUI.MelMenuItem(_k,
                                label = o,
                                ann = "Set the create shape to: {0}".format(o),
                                c=cgmGen.Callback(self.cb_setCreateShape,o))  

    def cb_setCreateColor(self,color):
        self.var_defaultCreateColor.setValue(color)
        self.uiField_shapeColor(edit=True,label=color)
        return True
    def cb_setCreateAttr(self,attr):
        self.var_attrCreateType.setValue(attr)
        self.uiField_attrType(edit=True,label=attr)
        return True

    def cb_setRayCastCreate(self,m):
        self.var_createRayCast.setValue(m)
        self.uiField_rayCastCreate(edit=True,label=m)
        return True

    def uiPopup_createColor(self):
        if self.uiPopUpMenu_color:
            self.uiPopUpMenu_color.clear()
            self.uiPopUpMenu_color.delete()
            self.uiPopUpMenu_color = None

        self.uiPopUpMenu_color = mUI.MelPopupMenu(self.uiField_shapeColor,button = 1)
        _popUp = self.uiPopUpMenu_color 

        mUI.MelMenuItem(_popUp,
                        label = "Set Color",
                        en=False)     
        mUI.MelMenuItemDiv(_popUp)

        for k,l in SHARED._d_colorsByIndexSets.iteritems():
            _k = mUI.MelMenuItem(_popUp,subMenu = True,
                                 label = k,
                                 en=True)
            for o in l:
                mUI.MelMenuItem(_k,
                                label = o,
                                ann = "Set the create color to: {0}".format(o),
                                c=cgmGen.Callback(self.cb_setCreateColor,o))

    def uiPopup_createAttr(self):
        if self.uiPopUpMenu_attr:
            self.uiPopUpMenu_attr.clear()
            self.uiPopUpMenu_attr.delete()
            self.uiPopUpMenu_attr = None

        self.uiPopUpMenu_attr = mUI.MelPopupMenu(self.uiField_attrType,button = 1)
        _popUp = self.uiPopUpMenu_attr 

        mUI.MelMenuItem(_popUp,
                        label = "Set Attr Type",
                        en=False)     
        mUI.MelMenuItemDiv(_popUp)

        for a in ATTR._l_simpleTypes:
            mUI.MelMenuItem(_popUp,
                            label = a,
                            ann = "Set the create attr to: {0}".format(a),
                            c=cgmGen.Callback(self.cb_setCreateAttr,a))

    def uiPopup_createRayCast(self):
        if self.uiPopUpMenu_raycastCreate:
            self.uiPopUpMenu_raycastCreate.clear()
            self.uiPopUpMenu_raycastCreate.delete()
            self.uiPopUpMenu_raycastCreate = None

        self.uiPopUpMenu_raycastCreate = mUI.MelPopupMenu(self.uiField_rayCastCreate,button = 1)
        _popUp = self.uiPopUpMenu_raycastCreate 

        mUI.MelMenuItem(_popUp,
                        label = "Set Create Type",
                        en=False)     
        mUI.MelMenuItemDiv(_popUp)

        for m in  ['locator','joint','jointChain','curve','duplicate','vectorLine','data']:
            mUI.MelMenuItem(_popUp,
                            label = m,
                            ann = "Create {0} by rayCasting".format(m),
                            c=cgmGen.Callback(self.cb_setRayCastCreate,m))        




#always attempt to setup the toolbox on import
setupCGMToolBox()
#end