
import os
import sys

from zooPy import dependencies
from zooPy.path import Path

import maya
import maya.cmds as cmd

import melUtils
import baseMelUI


def flush():

	pluginPaths = map( Path, melUtils.melEval( 'getenv MAYA_PLUG_IN_PATH' ).split( os.pathsep ) )  #NOTE: os.environ is different from the getenv call, and getenv isn't available via python...  yay!

	#before we do anything we need to see if there are any plugins in use that are python scripts - if there are, we need to ask the user to close the scene
	#now as you might expect maya is a bit broken here - querying the plugins in use doesn't return reliable information - instead we ask for all loaded
	#plugins, to which maya returns a list of extension-less plugin names.  We then have to map those names back to disk by searching the plugin path and
	#determining whether the plugins are binary or scripted plugins, THEN we need to see which the scripted ones are unloadable.
	loadedPluginNames = cmd.pluginInfo( q=True, ls=True ) or []
	loadedScriptedPlugins = []
	for pluginName in loadedPluginNames:
		for p in pluginPaths:
			possiblePluginPath = (p / pluginName).setExtension( 'py' )
			if possiblePluginPath.exists():
				loadedScriptedPlugins.append( possiblePluginPath[-1] )

	initialScene = None
	for plugin in loadedScriptedPlugins:
		if not cmd.pluginInfo( plugin, q=True, uo=True ):
			BUTTONS = YES, NO = 'Yes', 'NO'
			ret = cmd.confirmDialog( t='Plugins in Use!', m="Your scene has python plugins in use - these need to be unloaded to properly flush.\n\nIs it cool if I close the current scene?  I'll prompt to save your scene...\n\nNOTE: No flushing has happened yet!", b=BUTTONS, db=NO )
			if ret == NO:
				print "!! FLUSH ABORTED !!"
				return

			initialScene = cmd.file( q=True, sn=True )

			#prompt to make new scene if there are unsaved changes...
			melUtils.mel.saveChanges( 'file -f -new' )

			break

	#now unload all scripted plugins
	for plugin in loadedScriptedPlugins:
		cmd.unloadPlugin( plugin )  #we need to unload the plugin so that it gets reloaded (it was flushed) - it *may* be nessecary to handle the plugin reload here, but we'll see how things go for now

	#lastly, close all windows managed by baseMelUI - otherwise callbacks may fail...
	for melUI in baseMelUI.BaseMelWindow.IterInstances():
		melUI.delete()

	#determine the location of maya lib files - we don't want to flush them either
	mayaLibPath = Path( maya.__file__ ).up( 2 )

	#flush all modules
	dependencies.flush( [ mayaLibPath ] )

	if initialScene and not cmd.file( q=True, sn=True ):
		if Path( initialScene ).exists():
			cmd.file( initialScene, o=True )

	print "WARNING: You'll need to close and re-open any python based tools that are currently open..."


def reconnect():

	#try to import wing
	import wingdbstub
	wingdbstub.Ensure()

	import time
	try:
		debugger = wingdbstub.debugger
	except AttributeError:
		print "No debugger found!"
	else:
		if debugger is not None:
			debugger.StopDebug()
			time.sleep( 1 )
			debugger.StartDebug()


#end
