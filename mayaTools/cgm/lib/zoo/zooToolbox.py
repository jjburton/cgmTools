
from __future__ import with_statement

import os
import re
import sys

try:
	#try to connect to wing - otherwise don't worry
	import wingdbstub
except ImportError: pass


import maya
from maya.mel import eval as evalMel

from zooPy.path import Path, findFirstInEnv, findInPyPath
from zooPyMaya.baseMelUI import *
from zooPyMaya.melUtils import printErrorStr


def setupZooScriptPaths():
	thisFile = Path( __file__ )
	thisPath = thisFile.up()

	mayaScriptPaths = map( Path, maya.mel.eval( 'getenv MAYA_SCRIPT_PATH' ).split( os.pathsep ) )
	mayaScriptPathsSet = set( mayaScriptPaths )
	zooMelPath = thisPath / 'zooMel'

	if zooMelPath not in mayaScriptPathsSet:
		mayaScriptPaths.append( zooMelPath )
		mayaScriptPaths.extend( zooMelPath.dirs( recursive=True ) )

		mayaScriptPaths = removeDupes( mayaScriptPaths )
		newScriptPath = os.pathsep.join( [ p.unresolved() for p in mayaScriptPaths ] )

		maya.mel.eval( 'putenv MAYA_SCRIPT_PATH "%s"' % newScriptPath )


def setupZooPlugins():
	thisFile = Path( __file__ )
	thisPath = thisFile.up()

	existingPlugPathStr = maya.mel.eval( 'getenv MAYA_PLUG_IN_PATH;' )
	existingPlugPaths = map( Path, existingPlugPathStr.split( os.pathsep ) )
	existingPlugPathsSet = set( existingPlugPaths )

	zooPyPath = thisPath / 'zooPyMaya'

	if zooPyPath not in existingPlugPathsSet:
		existingPlugPaths.append( zooPyPath )

		existingPlugPaths = removeDupes( existingPlugPaths )
		newPlugPathStr = os.pathsep.join( [ p.unresolved() for p in existingPlugPaths ] )

		maya.mel.eval( 'putenv MAYA_PLUG_IN_PATH "%s";' % newPlugPathStr )


def setupDagProcMenu():
	'''
	sets up the modifications to the dagProcMenu script
	'''
	try:
		dagMenuScriptpath = findFirstInEnv( 'dagMenuProc.mel', 'MAYA_SCRIPT_PATH' )
	except:
		MGlobal.displayWarning( "Cannot find the dagMenuProc.mel script - aborting auto-override!" )
		return

	tmpScriptpath = Path( cmd.internalVar( usd=True ) ) / 'zoo_dagMenuProc_override.mel'

	def writeZooLines( fStream, parentVarStr, objectVarStr ):
		fStream.write( '\n/// ZOO TOOLBOX MODS ########################\n' )
		fStream.write( '\tsetParent -m $parent;\n' )
		fStream.write( '\tmenuItem -d 1;\n' )
		fStream.write( '\tpython( "from zooPyMaya import triggeredUI" );\n' )
		fStream.write( """\tint $killState = python( "triggeredUI.buildMenuItems( '"+ %s +"', '"+ %s +"' )" );\n""" % (parentVarStr, objectVarStr) )
		fStream.write( '\tif( $killState ) return;\n' )
		fStream.write( '/// END ZOO TOOLBOX MODS ####################\n\n' )

	globalProcDefRex = re.compile( "^global +proc +dagMenuProc *\( *string *(\$[a-zA-Z0-9_]+), *string *(\$[a-zA-Z0-9_]+) *\)" )
	with open( dagMenuScriptpath ) as f:
		dagMenuScriptLineIter = iter( f )
		with open( tmpScriptpath, 'w' ) as f2:
			hasDagMenuProcBeenSetup = False
			for line in dagMenuScriptLineIter:
				f2.write( line )

				globalProcDefSearch = globalProcDefRex.search( line )
				if globalProcDefSearch:
					parentVarStr, objectVarStr = globalProcDefSearch.groups()
					selHierarchyRex = re.compile( 'uiRes *\( *"m_dagMenuProc.kSelectHierarchy" *\)' )

					if '{' in line:
						writeZooLines( f2, parentVarStr, objectVarStr )
						hasDagMenuProcBeenSetup = True

					if not hasDagMenuProcBeenSetup:
						for line in dagMenuScriptLineIter:
							f2.write( line )
							if '{' in line:
								writeZooLines( f2, parentVarStr, objectVarStr )
								hasDagMenuProcBeenSetup = True
								break

		if not hasDagMenuProcBeenSetup:
			printErrorStr( "Couldn't auto setup dagMenuProc!  AWOOGA!" )
			return

		evalMel( 'source "%s";' % tmpScriptpath )
		evalMel( 'source "%s";' % tmpScriptpath )


def setupZooToolBox():
	setupZooScriptPaths()
	setupZooPlugins()
	setupDagProcMenu()
	setupZooMenu()


def setupZooMenu():
	if not cmd.optionVar( ex='zooToolboxMainMenu' ):
		cmd.optionVar( iv=('zooToolboxMainMenu', 1) )

	if not cmd.optionVar( q='zooToolboxMainMenu' ):
		return

	if not hasattr( maya, '_zooToolboxMenu' ):
		def cb( *a ):
			import zooToolbox
			zooToolbox.buildZooMenu( *a )

		menu = MelMainMenu( l='Zoo Tools', pmc=cb, tearOff=True )
		setattr( maya, '_zooToolboxMenu', menu )


class AutoStartInstaller(object):
	'''
	this is effectively a static class to contain all the functionality related to auto install
	'''
	class AutoSetupError(Exception): pass

	def getUserSetupFile( self ):
		pyUserSetup, melUserSetup = None, None
		try:
			pyUserSetup = findInPyPath( 'userSetup.py' )
		except: pass

		try:
			melUserSetup = findFirstInEnv( 'userSetup.mel', 'MAYA_SCRIPT_PATH' )
		except: pass

		return pyUserSetup, melUserSetup
	def isInstalled( self ):
		success = False
		pyUserSetup, melUserSetup = self.getUserSetupFile()
		if pyUserSetup is not None:
			if self.isInstalledPy( pyUserSetup ):
				return True

		if melUserSetup is not None:
			if self.isInstalledMel( melUserSetup ):
				return True

		return False
	def install( self ):
		success = False
		pyUserSetup, melUserSetup = self.getUserSetupFile()
		if pyUserSetup is None and melUserSetup is None:
			return

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
			for x in errors:
				printErrorStr( str(x) )
	def isInstalledPy( self, pyUserSetup ):
		with open( pyUserSetup ) as f:
			for line in f:
				if 'import' in line and 'zooToolbox' in line:
					return True

		return False
	def installPy( self, pyUserSetup ):
		if self.isInstalledPy( pyUserSetup ):
			return

		if pyUserSetup.getWritable():
			with open( pyUserSetup, 'a' ) as f:
				f.write( '\n\nimport zooToolbox\n' )
		else:
			raise self.AutoSetupError( "%s isn't writeable - aborting auto setup!" % pyUserSetup )
	def isInstalledMel( self, melUserSetup ):
		with open( melUserSetup ) as f:
			for line in f:
				if 'import' in line and 'zooToolbox' in line:
					return True
	def installMel( self, melUserSetup ):
		if self.isInstalledMel( melUserSetup ):
			return

		if melUserSetup.getWritable():
			with open( melUserSetup, 'a' ) as f:
				f.write( '\n\npython( "import zooToolbox" );\n' )
		else:
			raise self.AutoSetupError( "%s isn't writeable - aborting auto setup!" % melUserSetup )


def buildZooMenu( *a ):
	menu = maya._zooToolboxMenu
	menu.clear()

	MelMenuItem( menu, l='Open Toolbox Window', c=lambda *a: ToolboxWindow() )
	for toolCatName, toolSetupData in TOOL_CATS:
		catMenu = MelMenuItem( menu, l=toolCatName, sm=True, tearOff=True )
		for toolName, toolDesc, toolCB in toolSetupData:
			MelMenuItem( catMenu, l=toolName, ann=toolDesc, c=toolCB, tearOff=True )


def loadZooPlugin( pluginName ):
	try:
		cmd.loadPlugin( pluginName, quiet=True )
	except:
		setupZooToolBox()
		try:
			cmd.loadPlugin( pluginName, quiet=True )
		except:
			maya.OpenMaya.MGlobal.displayError( 'Failed to load zooMirror.py plugin - is it in your plugin path?' )


def loadSkeletonBuilderUI( *a ):
	from zooPyMaya import skeletonBuilderUI
	skeletonBuilderUI.SkeletonBuilderWindow()


def loadSpaceSwitching( *a ):
	from zooPyMaya import spaceSwitchingUI
	spaceSwitchingUI.SpaceSwitchingWindow()


def loadWeightSave( *a ):
	from zooPyMaya import skinWeightsUI
	skinWeightsUI.SkinWeightsWindow()


def loadPoseSym( *a ):
	from zooPyMaya import poseSymUI
	poseSymUI.PoseSymWindow()


def loadSkinPropagation( *a ):
	from zooPyMaya import refPropagation
	refPropagation.propagateWeightChangesToModel_confirm()


def loadPicker( *a ):
	from zooPyMaya import picker
	picker.PickerWindow()


def loadAnimLib( *a ):
	from zooPyMaya import animLibUI
	animLibUI.AnimLibWindow()


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
TOOL_CATS = ( ('animation', (('Animation Library', 'Animation library tool', loadAnimLib),
                             ('Animation Transfer', 'zooXferAnim is an animation transfer utility.  It allows transfer of animation using a variety of different methods, instancing, duplication, copy/paste, import/export and tracing.  Its also fully externally scriptable for integration into an existing production pipeline.',
                              loadXferAnim),

                             ('Graph Filters', 'zooGraphFilter provides a quick and easy way of filtering out certain channels on many objects in the graph editor.',
                              ToolCB('zooGraphFilter')),

                             ('Key Commands', 'zooKeyCommands is a simple little tool that lets you run a MEL command on an object for each keyframe the object has.  It basically lets you batch a command for each keyframe.',
                              ToolCB('source zooKeyCommandsWin')),

                             ('Grease Monkey', 'zooGreaseMonkey is a neat little script that allows you to draw in your camera viewport.  It lets you add as many frames as you want at various times in your scene.  You can use it to thumbnail your animation in your viewport, you can use it to plot paths, you could even use it to do a simple 2d based animation if you wanted',
                              ToolCB('zooGreaseMonkey')),

                             ('Picker - Selection Map', 'Picker tool - provides a way to create buttons that select scene objects, or run arbitrary code',
                              loadPicker),

                             ('Pose Sym - Mirroring Tool', 'Tool for doing pose-based mirroring',
                              loadPoseSym),
                             )),

              ('rigging', (('Skeleton Builder - auto rigger', "Skeleton Builder is what zooCST initially set out to be",
                            loadSkeletonBuilderUI),

						   ('Space Switching', "Sets up space switching for a given object",
                            loadSpaceSwitching),

						   ('Weight Save', "Saves out skinning weights to disk and will load them based on positioning or vertex index",
                            loadWeightSave),

						   ('Skinning Propagation', "Propagates skinning changes made to referenced geometry to the file it lives in",
                            loadSkinPropagation),

                           ('zooTriggered', 'zooTriggered is one of the most powerful rigging companions around.  It allows the rigger to attach name independent MEL commands to an object.  These commands can be run either on the selection of the object, or by right clicking over that object',
                            ToolCB('zooTriggered')),

                           ('zooKeymaster - Keyframe Manipulation', 'keymaster gives you a heap of tools to manipulate keyframes - scaling around curve pivots, min/max scaling of curves/keys etc...',
                            ToolCB( 'source zooKeymaster; zooKeymasterWin;' )),

                           ('zooSurgeon', 'zooSurgeon will automatically cut up a skinned mesh and parent the cut up "proxy" objects to the skeleton.  This allows for near instant creation of a fast geometrical representation of a character.',
                            ToolCB('zooSurgeon')),

                           ('VisMan - Visibility Set Tool', 'visMan is a tool for creating and using heirarchical visibility sets in your scene.  a visibility set holds a collection of items, be it components, objects or anything else that normally fits into a set.',
                            ToolCB('zooVisMan')),

                           ('zooCST', 'The ghetto version of Skeleton Builder',
                            ToolCB('zooCST')),
                           )),

              ('general', (('zooAutoSave', '''zooAutoSave is a tool that will automatically save your scene after a certain number of selections.  Maya doesn't provide a timer, so its not possible to write a time based autosave tool, but it makes more sense to save automatically after you've done a certain number of "things"''',
                            ToolCB('zooAutoSave')),

                           ('zooShots', 'zooShots is a camera management tool.  It lets you create a bunch of cameras in your scene, and "edit" them together in time.  The master camera then cuts between each "shot" camera.  All camera attributes are maintained over the cut - focal length, clipping planes, fstop etc...',
                            ToolCB('zooShots')),

                           ('zooHUDCtrl', 'zooHUDCtrl lets you easily add stuff to your viewport HUD.  It supports custom text, filename, current frame, camera information, object attribute values, and if you are using zooShots, it will also print out shot numbers to your HUD.',
                            ToolCB('zooHUDCtrl')),
                           )),

              ('hotkeys', (('Align - align selected objects',
                            'snaps two objects together - first select the master object, then the object you want to snap, then hit the hotkey',
                            ToolCB( 'zooHotkeyer zooAlign \"{zooAlign \\\"-load 1\\\";\\\nstring $sel[] = `ls -sl`;\\\nfor( $n=1; $n<`size $sel`; $n++ ) zooAlignSimple $sel[0] $sel[$n];}\" \"\" \"-default a -alt 1 -enableMods 1 -ann aligns two objects\"')),

                           ('Reset Selected',
                            'Resets keyable attribute values to their defaults for all selected nodes',
                            ToolCB( "zooHotkeyer zooResetAttrs \"python( \\\"from zooPyMaya import resetAttrs; resetAttrs.resetAttrsForSelection()\\\" );\" \"\" \"-default s -enableMods 1 -alt 1 -ann resets keyable attributes for selection\";" )),

                           ('Set Menu - selection set menu',
                            'zooSetMenu us a marking menu that lets you quickly interact with all quick selection sets in your scene.',
                            ToolCB( "zooHotkeyer zooSetMenu \"zooSetMenu;\" \"zooSetMenuKillUI;\" \"-default y -enableMods 0 -ann zooSetMenu lets you quickly interact with selection sets in your scene through a marking menu interface\";" )),

                           ('Tangent Works - tangency manipulation menu',
                            'zooTangentWks is a marking menu script that provides super fast access to common tangent based operations.  Tangent tightening, sharpening, change tangent types, changing default tangents etc...',
                            ToolCB( "zooHotkeyer zooTangentWks \"zooTangentWks;\" \"zooTangentWksKillUI;\" \"-default q -enableMods 0 -ann tangent works is a marking menu script to speed up working with the graph editor\";" )),

                           ('Set Key Menu - key creation menu',
                            'zooSetKey is a tool designed to replace the set key hotkey.  It is a marking menu script that lets you perform a variety of set key based operations - such as push the current key to the next key, perform a euler filter on all selected objects etc...',
                            ToolCB( "zooHotkeyer zooSetkey \"zooSetkey;\" \"zooSetkeyKillUI;\" \"-default s -enableMods 0 -ann designed to replace the set key hotkey, this marking menu script lets you quickly perform all kinda of set key operations\";" )),

                           ('Key Master - key manipulation menu',
                            'zooKeyMaster is a marking menu to help push and pull keys around quickly both in time and in value',
                            ToolCB( "zooHotkeyer zooKeymaster \"zooKeymasterMenu;\" \"zooKeymasterMenuKillUI;\" \"-default z -enableMods 0 -ann creates the zooKeymaster marking menu\";" )),

                           ('zooCam - Camera Menu',
                            'zooCam is a marking menu that lets you quickly swap between any camera in your scene.  It is integrated tightly with zooShots, so you can quickly navigate between shot cameras, master cameras, or any other in-scene camera.',
                            ToolCB( "zooHotkeyer zooCam \"zooCam;\" \"zooCamKillUI;\" \"-default l -enableMods 0 -ann zooCam marking menu script for managing in scene cameras\";" )),

                           ('Toggle Shading',
                            'toggles viewport shading',
                            ToolCB( "zooHotkeyer zooToggleShading \"zooToggle shading;\" \"\" \"-default 1 -enableMods 1 -ann toggles viewport shading\"" )),

                           ('Toggle Texturing',
                            'toggles viewport texturing',
                            ToolCB( "zooHotkeyer zooToggleTexture \"zooToggle texturing;\" \"\" \"-default 2 -enableMods 1 -ann toggles viewport texturing\"" )),

                           ('Toggle Lights',
                            'toggles viewport lighting',
                            ToolCB( "zooHotkeyer zooToggleLights \"zooToggle lighting;\" \"\" \"-default 3 -enableMods 1 -ann toggles viewport lighting\"" )),
                           )) )


class ToolboxTab(MelColumnLayout):
	def __new__( cls, parent, toolTuples ):
		return MelColumnLayout.__new__( cls, parent )
	def __init__( self, parent, toolTuples ):
		MelColumnLayout.__init__( self, parent )

		for toolStr, annStr, pressCB in toolTuples:
			assert pressCB is not None
			MelButton( self, l=toolStr, ann=annStr, c=pressCB )


class ToolboxTabs(MelTabLayout):
	def __init__( self, parent ):
		n = 0
		for toolCatStr, toolTuples in TOOL_CATS:
			ui = ToolboxTab( self, toolTuples )
			self.setLabel( n, toolCatStr )
			n += 1


class ToolboxWindow(BaseMelWindow):
	WINDOW_NAME = 'zooToolBox'
	WINDOW_TITLE = 'zooToolBox    ::macaroniKazoo::'

	DEFAULT_SIZE = 400, 300
	FORCE_DEFAULT_SIZE = True

	DEFAULT_MENU = None

	def __init__( self ):
		self.UI_menu = MelMenu( l='Setup', pmc=self.buildSetupMenu )
		ToolboxTabs( self )
		self.show()
	def buildSetupMenu( self, *a ):
		self.UI_menu.clear()
		setupMenu = cmd.optionVar( q='zooToolboxMainMenu' )
		MelMenuItem( self.UI_menu, l="Create Zoo Tools Menu", cb=setupMenu, c=lambda *a: cmd.optionVar( iv=('zooToolboxMainMenu', not setupMenu) ) )
		MelMenuItemDiv( self.UI_menu )

		installer = AutoStartInstaller()
		MelMenuItem( self.UI_menu, l="Auto-Load On Maya Start", cb=installer.isInstalled(), c=lambda *a: AutoStartInstaller().install() )


#always attempt to setup the toolbox on import
setupZooToolBox()


#end
