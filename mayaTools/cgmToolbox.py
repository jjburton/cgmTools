
from __future__ import with_statement

import os
import re
import sys

try:
	#try to connect to wing - otherwise don't worry
	import wingdbstub
except ImportError: pass

import maya.cmds as mc
import maya
from maya.mel import eval as evalMel

from cgm.lib import guiFactory
from cgm.lib.zoo.zooPy.path import Path, findFirstInEnv, findInPyPath
from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.lib.zoo.zooPyMaya.melUtils import printErrorStr


def setupCGMScriptPaths():
	thisFile = Path( __file__ )
	thisPath = thisFile.up()

	mayaScriptPaths = map( Path, maya.mel.eval( 'getenv MAYA_SCRIPT_PATH' ).split( os.pathsep ) )
	mayaScriptPathsSet = set( mayaScriptPaths )
	cgmMelPath = thisPath / '/cgm/mel'

	if cgmMelPath not in mayaScriptPathsSet:
		mayaScriptPaths.append( cgmMelPath )
		mayaScriptPaths.extend( cgmMelPath.dirs( recursive=True ) )

		mayaScriptPaths = removeDupes( mayaScriptPaths )
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

		existingPlugPaths = removeDupes( existingPlugPaths )
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
	if not cmd.optionVar( ex='cgmToolboxMainMenu' ):
		cmd.optionVar( iv=('cgmToolboxMainMenu', 1) )

	if not cmd.optionVar( q='cgmToolboxMainMenu' ):
		return

	if not hasattr( maya, '_cgmToolboxMenu' ):
		def cb( *a ):
			import cgmToolbox
			cgmToolbox.buildCGMMenu( *a )

		menu = MelMainMenu( l='CGM Tools', pmc=cb, tearOff=True )
		setattr( maya, '_cgmToolboxMenu', menu )


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
		with open( melUserSetup ) as f:
			for line in f:
				if 'import' in line and 'cgmToolbox' in line:
					return True
	def installMel( self, melUserSetup ):
		if self.isInstalledMel( melUserSetup ):
			return

		if melUserSetup.getWritable():
			with open( melUserSetup, 'a' ) as f:
				f.write( '\n\npython( "import cgmToolbox" );\n' )
		else:
			raise self.AutoSetupError( "%s isn't writeable - aborting auto setup!" % melUserSetup )


def buildCGMMenu( *a ):
	menu = maya._cgmToolboxMenu
	menu.clear()

	MelMenuItem( menu, l='Open Toolbox Window', c=lambda *a: ToolboxWindow() )
	for toolCatName, toolSetupData in TOOL_CATS:
		catMenu = MelMenuItem( menu, l=toolCatName, sm=True, tearOff=True )
		for toolName, toolDesc, toolCB in toolSetupData:
			MelMenuItem( catMenu, l=toolName, ann=toolDesc, c=toolCB, tearOff=True )


def loadCGMPlugin( pluginName ):
	try:
		cmd.loadPlugin( pluginName, quiet=True )
	except:
		setupCGMToolBox()
		try:
			cmd.loadPlugin( pluginName, quiet=True )
		except:
			maya.OpenMaya.MGlobal.displayError( 'Failed to load cgmMirror.py plugin - is it in your plugin path?' )

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def loadTDTools( *a ):
	import cgm
	import maya.cmds as mc
	import maya.mel as mel
	mel.eval('python("import maya.cmds as mc;")')
	from cgm.tools import tdTools
	reload(tdTools)
	tdTools.run()

def loadAttrTools( *a ):
	import cgm
	from cgm.tools import attrTools
	reload(attrTools)
	attrTools.run()
	
def loadLocinator( *a ):
	import cgm
	from cgm.tools import locinator
	reload(locinator)
	locinator.run()

def loadNamingTools( *a ):
	import cgm
	from cgm.tools import namingTools
	reload(namingTools)
	namingTools.run()
	
def loadPolyUniteTool( *a ):
	import cgm
	from cgm.tools import polyUniteTool
	reload(polyUniteTool)
	polyUniteTool.run()

class ToolCB(object):
	def __init__( self, melStr ):
		self.cmdStr = melStr
	def __call__( self, *a ):
		evalMel( self.cmdStr )


#this describes the tools to display in the UI - the nested tuples contain the name of the tool as displayed
#in the UI, and a tuple containing the annotation string and the button press callback to invoke when that
#tool's toolbox button is pressed.
#NOTE: the press callback should take *a as its args
TOOL_CATS = ( ('animation', (('Locinator', "Tool for creating, updating, locators",
                            loadLocinator),
                             
                             )),
              
              ('rigging', (('Locinator', "Tool for creating, updating, locators",
                            loadLocinator),

						   ('TD Tools', "Series of tools for general purpose TD work - curves, naming, position, deformers",
                            loadTDTools),
                           
                           ('PolyUnite Tool', "Stand alone poly unite tool for Plastic",
                            loadPolyUniteTool),
                           )),

              ('dev', (('Naming Tools', " Autoname and Standard naming tools",
                        loadNamingTools),
                       
                       ('Attribute Tools', " Attribute tools",
                        loadAttrTools),                       
                       
                       )),

              )


class ToolboxTab(MelColumnLayout):
	def __new__( cls, parent, toolTuples ):
		return MelColumnLayout.__new__( cls, parent )
	def __init__( self, parent, toolTuples ):
		MelColumnLayout.__init__( self, parent )

		for toolStr, annStr, pressCB in toolTuples:
			assert pressCB is not None
			MelButton( self, l=toolStr, ann=annStr, c=pressCB,ut = 'cgmUITemplate' )


class ToolboxTabs(MelTabLayout):
	def __init__( self, parent ):
		n = 0
		for toolCatStr, toolTuples in TOOL_CATS:
			ui = ToolboxTab( self, toolTuples )
			self.setLabel( n, toolCatStr )
			n += 1


class ToolboxWindow(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_Template = 'cgmUITemplate'
	
	WINDOW_NAME = 'cgmToolbox'
	WINDOW_TITLE = 'cgm.Toolbox'

	DEFAULT_SIZE = 400, 300
	FORCE_DEFAULT_SIZE = True

	DEFAULT_MENU = None

	def __init__( self ):
		from  cgm.lib import guiFactory
		guiFactory.initializeTemplates()
		USE_Template = 'cgmUITemplate'
		
		self.UI_menu = MelMenu( l='Setup', pmc=self.buildSetupMenu )
		ToolboxTabs( self )
		self.show()
	def buildSetupMenu( self, *a ):
		
		self.UI_menu.clear()
		setupMenu = cmd.optionVar( q='cgmToolboxMainMenu' )
		MelMenuItem( self.UI_menu, l="Create cgm Tools Menu", cb=setupMenu, c=lambda *a: cmd.optionVar( iv=('cgmToolboxMainMenu', not setupMenu) ) )
		MelMenuItemDiv( self.UI_menu )

		installer = AutoStartInstaller()
		MelMenuItem( self.UI_menu, l="Auto-Load On Maya Start", cb=installer.isInstalled(), c=lambda *a: AutoStartInstaller().install() )


#always attempt to setup the toolbox on import
setupCGMToolBox()

#end
