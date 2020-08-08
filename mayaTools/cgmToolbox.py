"""
------------------------------------------
toolbox: cgm.core.tools
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__version__ = '0.1.09042017'

#from __future__ import with_statement

import os
import re
import sys
import webbrowser
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
cgmInitialize.setupContributorPaths()

#import cgm.lib.zoo.zooPyMaya.baseMelUI as mUI
import cgm.core.classes.HotkeyFactory as HKEY

#>>>>>

from cgm.lib import guiFactory
from cgm.core.cgmPy import path_Utils as cgmPath
from cgm.lib.zoo.zooPyMaya import baseMelUI as mUI
from cgm.lib.zoo.zooPyMaya.melUtils import printErrorStr
import Red9

#==========================================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
from cgm.core.lib import shared_data as SHARED
import cgm.core.tools.toolbox as TOOLBOX

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
    uiMainMenu_rebuild()


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
    def build(*a):
        log.info("Building Top CGM Menu...")
        import cgmToolbox
        cgmToolbox.uiBuild_cgmMenu(*a)
        
    if not hasattr(maya,'_cgmMenu'):
        log.info('No _cgmMenu found')

        menu = mUI.MelMainMenu(l='CGM', pmc=build, tearOff = True, postMenuCommandOnce=True)
        setattr(maya,'_cgmMenu',menu)

def uiMainMenu_rebuild():
    if hasattr(maya,'_cgmMenu'):
        try:mc.deleteUI(getattr(maya,'_cgmMenu'))
        except:pass
        delattr(maya,'_cgmMenu')
    
    reload(UICHUNKS)
    uiMainMenu_add()


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
        l_lines = ['import cgmToolbox','import cgm.core.tools.lib.tool_chunks as TOOLCHUNKS','TOOLCHUNKS.loadLocalPython()']
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
        l_lines = ['import cgmToolbox','import cgm.core.tools.lib.tool_chunks as TOOLCHUNKS','TOOLCHUNKS.loadLocalPython()']
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


import cgm.core.tools.lib.tool_chunks as UICHUNKS
#reload(UICHUNKS)
#@cgmGen.Timer
def uiBuild_cgmMenu( *args ):
    _str_func = 'uiBuild_cgmMenu'
    menu = maya._cgmMenu
    menu.clear()
    
    #reload(UICHUNKS)
    log.info("|{0}| >> building...".format(_str_func))        
    
    """
    _l_sel = mc.ls(sl=True)
    if _l_sel:_b_sel = True
    _b_sel_pair = False
    _b_sel_few = False
    _len_sel = len(_l_sel)
    if _len_sel  >= 2:
        _b_sel_pair = True
    if _len_sel >2:
        _b_sel_few = True"""

    #log.info("|{0}| >> Selected: {1}".format(_str_func,_l_sel))        

    #mUI.MelMenuItem(menu, l='Open Tool Win',
    #                c=lambda *args: ToolboxWindow())
    
    mc.menuItem(p = menu, l='Open Tool Win',
                c= lambda *a:mc.evalDeferred(callUI,lp=1))
    
    
    #Utils ==========================================================================
    mUI.MelMenuItemDiv(menu,label='General')

    #>>Snap ----------------------------------------------------------------------
    _snap = mc.menuItem(p=menu,l='Snap',subMenu = True, tearOff = True)  
    UICHUNKS.uiSection_snap(_snap)
    
    _create = mc.menuItem(p=menu,l='Create',subMenu = True, tearOff = True,
                          ann= 'Create objects from selected objects or components')  
    UICHUNKS.uiSection_createFromSel(_create)
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
    UICHUNKS.uiSection_utils(_td)    
        
    #>>>Anim ----------------------------------------------------------------------
    _anim = mc.menuItem(p=menu,l='Anim',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_animUtils(_anim) 
    UICHUNKS.uiSection_layout(_anim)

    #>>Layout ----------------------------------------------------------------------
    #_layout = mc.menuItem(p=menu,l='Layout',subMenu = True, tearOff = True)
    #UICHUNKS.uiSection_layout(_layout)
    
    #>>Hotkeys ----------------------------------------------------------------------
    _hotkeys = mc.menuItem(p=menu,l='Hotkeys',subMenu = True, tearOff = False)
    UICHUNKS.uiSection_hotkeys(_hotkeys)    
    
    
    UICHUNKS.LIGHTLOOMLITE.uiMenu(menu)   
    
        
    #>>MRS ==========================================================================
    mUI.MelMenuItemDiv(menu,label='MRS')
    
    _manage = mc.menuItem(p=menu,l='Manage',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_mrsManage(_manage)    
    
    _TD = mc.menuItem(p=menu,l='TD',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_mrsTD(_TD)    
    
    _Dyn = mc.menuItem(p=menu,l='Dynamics',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_mrsDynamics(_Dyn)    
    
    _Move = mc.menuItem(p=menu,l='Move',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_mrsMove(_Move)    
    
    _Learn = mc.menuItem(p=menu,l='Learn',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_mrsLearn(_Learn)    
    
    
    
    #>>Mrs ----------------------------------------------------------------------
    #_layout = mc.menuItem(p=menu,l='MRS',subMenu = True, tearOff = True)
    #UICHUNKS.uiSection_mrs(_layout)        
    
    
    #>>MRS ==========================================================================
    mUI.MelMenuItemDiv(menu,label='Extra')    

    #>>LightStudio ----------------------------------------------------------------------
    #_layout = mc.menuItem(p=menu,l='LightStudio',subMenu = True, tearOff = True)




    #>>dev ----------------------------------------------------------------------
    _dev = mc.menuItem(p=menu,l='Dev',subMenu = True, tearOff = True)
    UICHUNKS.uiSection_dev(_dev)
    
    #>>utils ----------------------------------------------------------------------
    #_utils = mc.menuItem(p=menu,l='Dev',subMenu = True, tearOff = True)
    
    #>>Git ----------------------------------------------------------------------
    _git = mc.menuItem(p=menu,l='Git',subMenu = True, tearOff = True)
    #cgmUI.uiSection_help(_help)
    UICHUNKS.uiSection_git(_git)    

    #>>Help ----------------------------------------------------------------------
    _help = mc.menuItem(p=menu,l='Help',subMenu = True, tearOff = True)
    #cgmUI.uiSection_help(_help)
    UICHUNKS.uiSection_help(_help)
    
    mUI.MelMenuItemDiv(menu)    
    mc.menuItem(p = menu, l='Rebuild',
                ann='Rebuild the top menu',
                c = lambda *a: mc.evalDeferred(uiMainMenu_rebuild,lp=0))

"""
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

uiByTab = TOOLBOX.uiByTab
#ui = TOOLBOX.ui

def callUI():
    reload(TOOLBOX)
    ui()
    
class ui(TOOLBOX.ui):
    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     

        setupMenu = mc.optionVar( q='cgmVar_ToolboxMainMenu' )
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Create cgm Tools Menu", cb=setupMenu, c=lambda *a: mc.optionVar( iv=('cgmVar_ToolboxMainMenu', not setupMenu) ) )
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )
        
        try:
            installer = AutoStartInstaller()
            mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Auto-Load On Maya Start", cb=installer.isInstalled(), c=lambda *a: AutoStartInstaller().install() )
        except Exception,err:
            log.warning("Not loaded from cgmToolbox. No autoinstaller options")
            
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )
        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Dock",
                         c = lambda *a:self.do_dock())
        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Rebuild Main Menu",
                                 c = lambda *a:uiMainMenu_rebuild())
        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))   
        
#always attempt to setup the toolbox on import
setupCGMToolBox()
#end