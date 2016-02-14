
from __future__ import with_statement

import os
import re
import sys

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from cgm.core import cgm_General as cgmGeneral

try:
    #try to connect to wing - otherwise don't worry
    import wingdbstub
except ImportError: pass

import maya.cmds as mc
import maya
from maya.mel import eval as evalMel

#>>>>> Bridge to get our sub zoo stuff working
from cgm import cgmInitialize
reload(cgmInitialize)
cgmInitialize.setupContributorPaths()

import cgm.lib.zoo.zooPyMaya.baseMelUI as zooUI
import cgm.core.classes.HotkeyFactory as HKEY

#>>>>>

from cgm.lib import guiFactory
from cgm.lib.zoo.zooPy.path import Path, findFirstInEnv, findInPyPath
from cgm.lib.zoo.zooPyMaya import baseMelUI as mUI
from cgm.lib.zoo.zooPyMaya.melUtils import printErrorStr
import Red9

def setupCGMScriptPaths():
    thisFile = Path( __file__ )
    thisPath = thisFile.up()

    mayaScriptPaths = map( Path, maya.mel.eval( 'getenv MAYA_SCRIPT_PATH' ).split( os.pathsep ) )
    mayaScriptPathsSet = set( mayaScriptPaths )

    for path in '/cgm/mel','/cgm/images','/cgm/lib/zoo','/Red9':
        fullPath = thisPath / path
        if fullPath not in mayaScriptPathsSet:
            mayaScriptPaths.append( fullPath )
            mayaScriptPaths.extend( fullPath.dirs( recursive=True ) )

            mayaScriptPaths = mUI.removeDupes( mayaScriptPaths )
            newScriptPath = os.pathsep.join( [ p.unresolved() for p in mayaScriptPaths ] )

            maya.mel.eval( 'putenv MAYA_SCRIPT_PATH "%s"' % newScriptPath )



def setupCGMPlugins():
    thisFile = Path( __file__ )
    thisPath = thisFile.up()

    existingPlugPathStr = maya.mel.eval( 'getenv MAYA_PLUG_IN_PATH;' )
    existingPlugPaths = map( Path, existingPlugPathStr.split( os.pathsep ) )
    existingPlugPathsSet = set( existingPlugPaths )

    cgmPyPath = thisPath / 'cgm/plugins'

    if cgmPyPath not in existingPlugPathsSet:
        existingPlugPaths.append( cgmPyPath )

        existingPlugPaths = mUI.removeDupes( existingPlugPaths )
        newPlugPathStr = os.pathsep.join( [ p.unresolved() for p in existingPlugPaths ] )

        maya.mel.eval( 'putenv MAYA_PLUG_IN_PATH "%s";' % newPlugPathStr )

"""
def setupDagProcMenu() REMOVED

"""

def setupCGMToolBox():
    setupCGMScriptPaths()
    setupCGMPlugins()
    #setupDagProcMenu()
    setupCGMMenu()


def setupCGMMenu():
    if not mc.optionVar( ex='cgmVar_ToolboxMainMenu' ):
        mc.optionVar( iv=('cgmVar_ToolboxMainMenu', 1) )

    if not mc.optionVar( q='cgmVar_ToolboxMainMenu' ):
        return

    if not hasattr( maya, '_cgmToolboxMenu' ):
        def cb( *a ):
            import cgmToolbox
            cgmToolbox.buildCGMMenu( *a )

        menu = mUI.MelMainMenu( l='CGM Tools', pmc=cb, tearOff=True )
        setattr( maya, '_cgmToolboxMenu', menu )


class AutoStartInstaller(object):
    '''
    this is effectively a static class to contain all the functionality related to auto install
    '''
    class AutoSetupError(Exception): pass

    def getUserSetupFile( self ):
        pyUserSetup, melUserSetup = None, None
        try:
            pyUserSetup = findFirstInEnv( 'userSetup.py' )#findInPyPath
        except: print ('No py user setup')

        try:
            melUserSetup = findFirstInEnv( 'userSetup.mel', 'MAYA_SCRIPT_PATH' )
            print "Mel user file is '%s'"%melUserSetup
        except: print ('No mel user setup')

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
            if not self.createPyUserSetup():#if we can't make a user file, break
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
                printErrorStr( str(x) )

    def isInstalledPy( self, pyUserSetup ):
        with open( pyUserSetup ) as f:
            for line in f:
                if 'import' in line and 'cgmToolbox' in line:
                    return True
        return False

    def installPy( self, pyUserSetup ):
        if self.isInstalledPy( pyUserSetup ):
            return

        if pyUserSetup.getWritable():
            with open( pyUserSetup, 'a' ) as f:
                f.write( '\n\nimport cgmToolbox\n' )
        else:
            raise self.AutoSetupError( "%s isn't writeable - aborting auto setup!" % pyUserSetup )
        
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

    def createPyUserSetup(self):
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



def buildCGMMenu( *a ):
    menu = maya._cgmToolboxMenu
    menu.clear()

    mUI.MelMenuItem( menu, l='Open Toolbox Window', c=lambda *a: ToolboxWindow() )
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

def startWingServer( *a ):
    from cgm.core.lib.wing import mayaWingServer as mWingServer
    reload(mWingServer)
    mWingServer.startServer()

def loadAttrTools( *a ):
    from cgm.tools import attrTools
    reload(attrTools)
    cgmAttrToolsWin = attrTools.run()

def loadLocinator( *a ):
    from cgm.tools import locinator
    reload(locinator)
    locinator.run()

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

def loadPolyUniteTool( *a ):
    from cgm.tools import polyUniteTool
    reload(polyUniteTool)
    polyUniteTool.run()

def purgeCGMOptionVars( *a ):
    from cgm.lib import optionVars
    optionVars.purgeCGM()	

def connectToWingIDE( *a ):
    try: 
        reload(cgmDeveloperLib) 
    except:
        from cgm.lib import cgmDeveloperLib
    cgmDeveloperLib.connectToWing()

def testMorpheus( *a ):
    from cgm.core.tests import cgmMeta_test as testCGM
    reload(testCGM)
    testCGM.MorpheusBase_Test()

def loadMorpheusMaker( *a ):
    try:
        print("Trying to load Morheus Maker 2014")
        from morpheusRig_v2.core.tools import MorpheusMaker as mMaker
        reload(mMaker)    
        mMaker.go()	
    except Exception,error:
        log.error("You appear to be missing the Morpheus pack. Or maybe angered the spirits...")
        raise Exception,error




def loadLocalCGMPythonSetup( *a ):
    evalMel('python("from cgm.core import cgm_Meta as cgmMeta;from cgm.core import cgm_General as cgmGeneral;from cgm.core.rigger import RigFactory as Rig;from cgm.core import cgm_PuppetMeta as cgmPM;import Red9.core.Red9_Meta as r9Meta;import cgm.core;cgm.core._reload();import maya.cmds as mc;")')
#Unittest =====================================================================
def unittest_All( *a ):
    from cgm.core.tests import cgmMeta_test as testCGM
    reload(testCGM)
    testCGM.ut_AllTheThings()

def unittest_cgmMeta( *a ):
    from cgm.core.tests import cgmMeta_test as testCGM
    reload(testCGM)
    testCGM.ut_cgmMeta()

def unittest_cgmPuppet( *a ):
    from cgm.core.tests import cgmMeta_test as testCGM
    reload(testCGM)
    testCGM.ut_cgmPuppet()  

def unittest_cgmLimb( *a ):
    from cgm.core.tests import cgmMeta_test as testCGM
    reload(testCGM)
    testCGM.ut_cgmLimb()  


#Help stuff =====================================================================
def reset_hotkeys( *a ):
    from cgm.core.classes import HotkeyFactory as HKEY
    reload(HKEY)
    HKEY.hotkeys_resetAll()
        
def goTo_keyframeCoop( *a ):
    try:
        import webbrowser
        webbrowser.open("http://keyframeco-op.com/")
    except Exception,error:
        log.warning("[Failed to load Keyframe Co-op]{%s}"%error)

def goTo_cgmVimeo( *a ):
    try:
        import webbrowser
        webbrowser.open("http://vimeo.com/cgmonks")
    except Exception,error:
        log.warning("[Failed to load cgm vimeo]{%s}"%error)

def goTo_red9Vimeo( *a ):
    try:
        import webbrowser
        webbrowser.open("http://vimeo.com/user9491246")
    except Exception,error:
        log.warning("[Failed to load red9 vimeo]{%s}"%error)

def goTo_stackOverflow( *a ):
    try:
        import webbrowser
        webbrowser.open("http://stackoverflow.com")
    except Exception,error:
        log.warning("[Failed to load stackOverflow]{%s}"%error)

def get_enviornmentInfo( *a ):
    try:
        cgmGeneral.report_enviornment()
    except Exception,error:
        log.warning("[Failed to report enviornment]{%s}"%error)

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
TOOL_CATS = ( ('animation', (('cgm.animTools', " Anim tools",
                              loadAnimTools),
                             ('cgm.locinator', "Tool for creating, updating, locators",
                              loadLocinator),
                             ('cgm.SetTools', " Set tools",
                              loadSetTools),
                             ('red9.studioTools', "Launch Red 9's tools - hit it twice for now",
                              loadRed9),                             
                             ('zoo.XferAnim', "Tool for transferring animation - from Hamish McKenzie's zooToolbox",
                              loadXferAnim), 
                             ('zoo.Keymaster', "from Hamish McKenzie's zooToolbox - keymaster gives you a heap of tools to manipulate keyframes - scaling around curve pivots, min/max scaling of curves/keys etc...",
                              ToolCB( 'source zooKeymaster; zooKeymasterWin;' )),

                             )),

              ('rigging', (('cgm.locinator', "Tool for creating, updating, locators",
                            loadLocinator),

                           ('cgm.tdTools', "Series of tools for general purpose TD work - curves, naming, position, deformers",
                            loadTDTools),

                           ('cgm.attrTools', " Attribute tools",
                            loadAttrTools),

                           ('cgm.PolyUniteTool', "Stand alone poly unite tool for Plastic",
                            loadPolyUniteTool),                        

                           )),

              ('layout', (('zoo.Shots', "from Hamish McKenzie's zooToolbox -  zooShots is a camera management tool.  It lets you create a bunch of cameras in your scene, and 'edit' them together in time.  The master camera then cuts between each 'shot' camera.  All camera attributes are maintained over the cut - focal length, clipping planes, fstop etc...",
                           ToolCB('zooShots')),
                          ('zoo.HUDCtrl', "from Hamish McKenzie's zooToolbox -  zooHUDCtrl lets you easily add stuff to your viewport HUD. ",
                           ToolCB('zooHUDCtrl')),
                          )),

              ('hotkeys', (('Zoo Set Menu - selection set menu',
                            'zooSetMenu us a marking menu that lets you quickly interact with all quick selection sets in your scene.',
                            zooUI.Callback(HKEY.cgmHotkeyer, 'zooSetMenu', 'zooSetMenu;', 'zooSetMenuKillUI;','zooSetMenu lets you quickly interact with selection sets in your scene through a marking menu interface','mel','y')),                            
                            #ToolCB( "zooHotkeyer zooSetMenu \"zooSetMenu;\" \"zooSetMenuKillUI;\" \"-default y -enableMods 0 -ann zooSetMenu lets you quickly interact with selection sets in your scene through a marking menu interface\";" )),

                           ('Set Menu - menu for cgm.setTools',
                            'Menu for working with cgm.SetTools. There are a wide fariety of tools for them..',
                            zooUI.Callback(HKEY.cgmHotkeyer, 'cgmSetToolsMM', 'cgmSetToolsMM;', 'cgmSetToolsMMKillUI;','cgmSnap marking menu', 'mel','d')),                            
                            #ToolCB( "zooHotkeyer cgmSetToolsMM \"cgmSetToolsMM;\" \"cgmSetToolsMMKillUI;\" \"-default d -enableMods 0 -ann zooSetMenu lets you quickly interact with selection sets in your scene through a marking menu interface\";" )),

                           ('Tangent Works - tangency manipulation menu',
                            'zooTangentWks is a marking menu script that provides super fast access to common tangent based operations.  Tangent tightening, sharpening, change tangent types, changing default tangents etc...',
                            zooUI.Callback(HKEY.cgmHotkeyer, 'zooTangentWks',  'zooTangentWks;', 'zooTangentWksKillUI;','tangent works is a marking menu script to speed up working with the graph editor','mel','q')),                            
                            #ToolCB( "zooHotkeyer zooTangentWks \"zooTangentWks;\" \"zooTangentWksKillUI;\" \"-default q -enableMods 0 -ann tangent works is a marking menu script to speed up working with the graph editor\";" )),

                           ('Snap Tools - snap tools menu',
                            'cgmSnapToolsMM is a tool for accessing snapping tools from a marking menu...',
                            zooUI.Callback(HKEY.cgmHotkeyer, 'cgmSnap',  'cgmSnapMM;', 'cgmSnapMMKillUI;','cgmSnap marking menu','mel','t')),
                           
                           ('NEW Set Key Menu - key creation menu',
                            'cgmPuppet key menu - wip',
                            zooUI.Callback(HKEY.cgmHotkeyer, 'cgmPuppetKey', 'cgmPuppetKeyMM;', 'cgmPuppetKeyMMKillUI;','New moduler marking menu for the s key','mel','s')),

                           ('Set Key Menu - key creation menu',
                            'cgmLibrary tools for dealing with keys',
                            zooUI.Callback(HKEY.cgmHotkeyer, 'cgmSetKeyMM',  'cgmSetKeyMM;', 'cgmSetKeyMMKillUI;','designed to replace the set key hotkey, this marking menu script lets you quickly perform all kinda of set key operations', 'mel','s')),                            
                            #ToolCB( "zooHotkeyer cgmSetKeyMM \"cgmSetKeyMM;\" \"cgmSetKeyMMKillUI;\" \"-default s -enableMods 0 -ann designed to replace the set key hotkey, this marking menu script lets you quickly perform all kinda of set key operations\";" )),

                           ('Reset Hotkeys', "Reset all hotkeys in current hotkeySet(2016+) or in maya for below 2016",
                            reset_hotkeys),                            
                           )),

              ('dev', (('Purge CGM Option Vars', " Purge all cgm option vars. Warning will break any open tools",
                        purgeCGMOptionVars),
                       #('Connect to Wing IDE', " Attempts to connect to Wing IDE",
                       #                       connectToWingIDE), 
                       ('Start Wing Server', " Opens a command port for Wing IDE",
                        startWingServer),   
                       ('Load Local CGM Python', " Sets up standard cgm ptyhon imports for use in the script editor",
                        loadLocalCGMPythonSetup),                        
                       ('Simple cgmGUI', " Base cgmGUI",
                        loadCGMSimpleGUI),
                       ('cgm.MorpheusMaker', " Morpheus maker tool",
                        loadMorpheusMaker),
                       ('zooToolbox', " Open zooToolbox Window",
                        loadZooToolbox),        
                       ('unitTest - cgm', " WARNING - Opens new file...Unit test cgm.core",
                        unittest_All),  
                       ('unitTest - cgmMeta', " WARNING - Opens new file...Unit test cgm.core",
                        unittest_cgmMeta),   
                       ('unitTest - cgmPuppet', " WARNING - Opens new file...Unit test cgm.core",
                        unittest_cgmPuppet),   
                       ('unitTest - cgmLimb', " WARNING - Opens new file...Unit test cgm.core",
                        unittest_cgmLimb),                           
                       )),
              ('help', (('CG Monks Vimeo', " Tutorials and more ",
                         goTo_cgmVimeo), 
                        ('Red9 Vimeo', " Tutorials and more ",
                         goTo_red9Vimeo),   
                        ('Stack Overflow', " This is where we go when code-stumped... ",
                         goTo_stackOverflow),                          
                        ('Enviornment Info', " What's your maya enviornment? ",
                         get_enviornmentInfo),                           
                        ))
              )


class ToolboxTab(mUI.MelColumnLayout):
    def __new__( cls, parent, toolTuples ):
        return mUI.MelColumnLayout.__new__( cls, parent )
    def __init__( self, parent, toolTuples ):
        mUI.MelColumnLayout.__init__( self, parent )

        for toolStr, annStr, pressCB in toolTuples:
            assert pressCB is not None
            mUI.MelButton( self, l=toolStr, ann=annStr, c=pressCB,ut = 'cgmUITemplate' )


class ToolboxTabs(mUI.MelTabLayout):
    def __init__( self, parent ):
        n = 0
        for toolCatStr, toolTuples in TOOL_CATS:
            ui = ToolboxTab( self, toolTuples )
            self.setLabel( n, toolCatStr )
            n += 1


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


#always attempt to setup the toolbox on import
setupCGMToolBox()
#end