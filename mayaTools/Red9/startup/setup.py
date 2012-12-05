'''
------------------------------------------
Red9 Studio Pack : Maya Pipeline Solutions
email: rednineinfo@gmail.com
------------------------------------------

This is the heart of the Red9 StudioPack's boot sequence, managing folder structures, 
dependencies and menuItems.
'''



import sys
import os
import maya.cmds as cmds
import maya.mel as mel

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


'''
 Maya Version Mapping History:
 ====================================

 Release         -version    -api        python    -qt      prefs
 ------------------------------------------------------------------
 
  2008          .  2008  .  ??????  .    2.5.1      na    .  2008
  2009          .  2009  .  ??????  .    2.5.1      na    .  2009
  2010          .  2010  .  201000  .    2.6.1      na    .  2010
  2011 Hotfix2  .  2011  .  201102  .    2.6.4     4.5.3  .  2011
  2011 SAP      .  2011  .  201104  .    2.6.4     4.5.3  .  2011.5  2011 binary compliant
  2012          .  2012  .  201200  .    2.6.4     4.7.1  .  2012
  2012 SP2      .  2012  .  201217  .    2.6.4     4.7.1  .  2012
  2013 SP1      .  2013  .  201301  .    2.6.4     4.7.1  .  2013
  2013 SP2      .  2013  .  ??????  .    2.6.4     4.7.1  .  2013
  2013 EXT      .  2013  .  201350  .    2.6.4     4.7.1  .  2013.5  plugin recompile needed
  2014          .  2014  .  201400  .    2.6.4     4.8.2  .  2014

-------------------------------------------------------------------
''' 
def mayaVersion():
    #need to manage this better and use the API version, 
    #eg: 2013.5 returns 2013
    return mel.eval('getApplicationVersionAsFloat')

def mayaVersionRelease():
    return cmds.about(api=True)

def mayaVersionQT():
    try:
        return cmds.about(qt=True)
    except:
        pass
    
def mayaPrefs():
    '''
    Root of Maya prefs folder
    '''
    return os.path.dirname(cmds.about(env=True))

def mayaUpAxis():
    import maya.OpenMaya as OpenMaya
    vect=OpenMaya.MGlobal.upAxis()
    if vect.z:
        return 'z'
    if vect.y:
        return 'y'
      
def menuSetup():
    
    #if exists remove all items, means we can update on the fly by restarting the Red9 pack
    if cmds.menu('redNineMenuItemRoot', exists=True):       
        cmds.deleteUI('redNineMenuItemRoot')    
        log.info("Rebuilding Existing RedNine Menu")

    cmds.menu('redNineMenuItemRoot', l="RedNine",p='MayaWindow',tearOff=True, allowOptionBoxes=True)
    #Add the main Menu items
    cmds.menuItem('redNineAnimItem',l="AnimationToolkit",ann="Main Red9 Animation Toolkit",
                  p='redNineMenuItemRoot', echoCommand=True,
                  c="import Red9.core.Red9_AnimationUtils as r9Anim;r9Anim.AnimationUI.show()")
    cmds.menuItem('redNineSnapItem',l="Simple Snap",ann="Simple Snap transforms",
                  p='redNineMenuItemRoot', echoCommand=True,
                  c="import Red9.core.Red9_AnimationUtils as r9Anim;r9Anim.AnimFunctions.snap()")
    cmds.menuItem('redNineSearchItem',l="SearchUI",ann="Main Red9 Search toolkit",
                  p='redNineMenuItemRoot', echoCommand=True,
                  c="import Red9.core.Red9_CoreUtils as r9Core;r9Core.FilterNode_UI.show()")
    cmds.menuItem('redNineLockChnsItem',l="LockChannels",ann="Manage Channel States",
                  p='redNineMenuItemRoot', echoCommand=True,
                  c="import Red9.core.Red9_CoreUtils as r9Core;r9Core.LockChannels.UI.show()") 
    cmds.menuItem('redNineMetaUIItem',l="MetaNodeUI",ann="MetaNode Scene Searcher",
                  p='redNineMenuItemRoot', echoCommand=True,
                  c="import Red9.core.Red9_Meta as r9Meta;r9Meta.MClassNodeUI.show()") 
    cmds.menuItem('redNineReporterUIItem',l="Scene Reviewer",ann="Launch the Scene Review Reporter",
                  p='redNineMenuItemRoot', echoCommand=True,
                  c="import Red9.core.Red9_Tools as r9Tools;r9Tools.SceneReviewerUI.show()") 
    cmds.menuItem('redNineMoCapItem',l="MouseMoCap",ann="Record the Mouse Input to selected object",
                  p='redNineMenuItemRoot', echoCommand=True,
                  c="import Red9.core.Red9_Tools as r9Tools;r9Tools.RecordAttrs.show()")  
    cmds.menuItem(divider=True)
    cmds.menuItem('redNineHelpItem',l="Red9_Help",ann="Boot the Help Files",
                  p='redNineMenuItemRoot', echoCommand=True,
                  c="Red9.setup.help()")
    cmds.menuItem('redNineBlogItem',l="Red9_Blog",ann="Open Red9Blog",
                  p='redNineMenuItemRoot', echoCommand=True,
                  c="Red9.setup.blog()")
    cmds.menuItem('redNineDebuggerItem',l='Red9 Debugger',sm=True)
    cmds.menuItem('redNineDebugItem',l="systems DEBUG",ann="Turn all the logging to Debug",
                  echoCommand=True, c="Red9.core._setlogginglevel_debug()")
    cmds.menuItem('redNineInfoItem',l="systems INFO",ann="Turn all the logging to Info only",
                  echoCommand=True, c="Red9.core._setlogginglevel_info()")

def red9ButtonBGC(colour):
    '''
    Generic setting for the main button colours in the UI's
    '''
    if colour==1:
        return [0.6, 0.9, 0.65]
    if colour==2:
        return [0.5, 0.5, 0.5]
   
def red9ContactInfo():
    cmds.confirmDialog(title='Red9Info', 
                       message="Contact me at rednineinfo@gmail.com for more information\r\rthanks for trying the toolset",
                       button='thankyou',messageAlign='center')   
    
def red9ModulePath():
    '''   
    Returns the Main path to the Red9 root module folder    
    '''
    return os.path.join(os.path.dirname(os.path.dirname(__file__)),'')

def red9MayaNativePath():
    '''
    Returns the MayaVersioned Hacked script path if valid and found
    '''
    _version=int(mayaVersion())
    path=os.path.join(red9ModulePath(),'startup','maya_native','maya_%s' % str(_version))
   
    if os.path.exists(path):
        return path
    else:
        log.info('Red9MayaHacked Folder not found for this build of Maya : %s' % path)
  
def help():
    '''
    open up the Red9 help docs
    '''
    #import webbrowser;
    #webbrowser.open('%s\docs\Red9-StudioTools Help.pdf' % Red9_ModulesPath())
    helpFile=os.path.join(red9ModulePath(),'docs',r'Red9-StudioTools Help.pdf')
    try:
        os.startfile(helpFile)
    except StandardError, error:
        #fails on linux, need to use os.system(('acroread'+helpFile))
        raise StandardError(error)
    
def blog():
    '''
    open up the Red9 Blog
    '''
    #import webbrowser;
    #webbrowser.open('http://red9-consultancy.blogspot.com/') 
    try:
        os.startfile('http://red9-consultancy.blogspot.com/')
    except:
        os.system('firefox http://red9-consultancy.blogspot.com/')
        log.exception('os.startfile call failed to open Blog')  
    
def addScriptsPath(path):
    '''
    Add additional folders to the ScriptPath
    '''
    scriptsPath=os.environ.get('MAYA_SCRIPT_PATH')
    
    if os.path.exists(path):
        if not path in scriptsPath: 
            log.info( 'Adding To Script Paths : %s' % path)
            os.environ['MAYA_SCRIPT_PATH']+='%s%s' % (os.pathsep,path)
        else:
            log.info('Red9 Script Path already setup : %s' % path)
    else:
        log.debug('Given Script Path is invalid : %s' % path)
          
def addPluginPath():
    '''
    Make sure the plugin path has been added. If run as a module
    this will have already been added
    '''
    path=os.path.join(red9ModulePath(),'plug-ins')
    plugPaths=os.environ.get('MAYA_PLUG_IN_PATH')
    
    if not path in plugPaths: 
        log.info('Adding Red9 Plug-ins to Plugin Paths : %s' % path)
        os.environ['MAYA_PLUG_IN_PATH']+='%s%s' % (os.pathsep,path)
    else:
        log.info ('Red9 Plug-in Path already setup')
              
def addIconsPath():
    '''
    Make sure the icons path has been added. If run as a module
    this will have already been added
    '''
    path=os.path.join(red9ModulePath(),'icons')
    iconsPath=os.environ.get('XBMLANGPATH')
    
    if not path in iconsPath: 
        log.info( 'Adding Red9 Icons To XBM Paths : %s' % path)
        os.environ['XBMLANGPATH']+='%s%s' % (os.pathsep,path)
    else:
        log.info('Red9 Icons Path already setup')
             
def addPythonPackages():
    '''
    Add the packages folder which is where any external modules
    will be stored
    '''
    red9Packages=os.path.join(red9ModulePath(),'packages')
    
    if not red9Packages in sys.path: 
        log.info( 'Adding Red9Packages To Python Paths : %s' % red9Packages)
        sys.path.append(red9Packages)
    else:
        log.info('Red9Packages Path already setup : %s' % red9Packages)

     
def sourceMelFolderContents(path):
    '''
    source all mel files in a given folder
    '''
    for script in [file for file in os.listdir(path) if file.lower().endswith('.mel')]:
        log.info('Sourcing mel script : %s' % script)
        mel.eval('source %s' % script)
            
       
def start(Menu=True):
    '''
    Main entry point for the StudioPack
    '''
    log.info('Red9 StudioPack Setup Calls')
    if Menu:
        try:
            menuSetup()
        except:
            log.debug('Menu Build Failed!')
        
    #Ensure the Plug-in and Icon paths are up   
    addPluginPath()
    addIconsPath()
    
    #Need to add a Mel Folder to the scripts path
    addScriptsPath(os.path.join(red9ModulePath(),'core'))
    
    #Add the Packages folder
    #AddPythonPackages()
    
    #Source Maya Hacked mel files
    hacked=red9MayaNativePath()
    if hacked:
        addScriptsPath(hacked)
        try:
            mel.eval('source Red9_MelCore' ) 
            sourceMelFolderContents(hacked)
        except StandardError, error:
            log.info(error)
    log.info('Red9 StudioPack Complete!')

    
    