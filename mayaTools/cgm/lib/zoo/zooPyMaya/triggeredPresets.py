
import maya.cmds as cmd

from zooPy import sobject
from zooPy import presets

from zooPyMaya import triggered
from zooPyMaya import mappingUtils

TOOL_NAME = presets.DEFAULT_TOOL
XTN = 'trigger'

PRESET_MANAGER = presets.PresetManager( TOOL_NAME, XTN )


def writeToPreset( presetName, triggers=None ):
	thePreset = presets.Preset( presets.LOCAL, TOOL_NAME, presetName, XTN )
	writeToFilepath( thePreset.path(), triggers )

	return thePreset


def writeToFilepath( filepath, triggers=None ):
	if triggers is None:
		triggers = triggered.Trigger.All( True, True )

	root = sobject.SObject()
	root.triggerDict = triggerDict = {}

	#store all the nodes that are used by the triggers - both the trigger nodes themselves and all connects
	allNodes = set()

	for trigger in triggers:
		triggerDict[ trigger.obj ] = st = sobject.SObject()
		allNodes.add( trigger.obj )

		assert isinstance( trigger, triggered.Trigger )
		triggerCmd = trigger.getCmd()
		if triggerCmd:
			st.cmd = trigger.getCmd()

		connects = trigger.connects()[1:]  #chop off the first as it is always the "zero-th" connect
		if connects:
			st.connectsDict = connectsDict = {}
			for nodeName, connectIdx in connects:
				connectsDict[connectIdx] = nodeName
				allNodes.add( nodeName )

		menus = trigger.menus()
		if menus:
			st.killState = trigger.getKillState()
			st.menus = []
			for menuIdx, menuName, menuCmdStr in menus:
				st.menus.append( (menuName, menuCmdStr) )

	root.allNodes = list( sorted( allNodes ) )

	root.write( filepath )


def loadFromPreset( preset, searchDomain=None ):
	return loadFromFilepath( preset.path(), searchDomain )


def loadFromFilepath( filepath, searchDomain=None ):
	'''
	the searchDomain should be either None or a list of the nodes that encompass the nodes stored in the file.  If the
	searchDomain is None then it defaults to all transforms in the scene
	'''
	if searchDomain is None:
		searchDomain = cmd.ls( type='transform' ) or []

	root = sobject.SObject.Load( filepath )
	mapping = mappingUtils.matchNames( root.allNodes, searchDomain )

	for nodeName, triggerData in root.triggerDict.iteritems():
		actualNode = mapping[ nodeName ]
		if actualNode:
			actualNode = actualNode[0]
			trigger = triggered.Trigger( actualNode )
			if hasattr( triggerData, 'cmd' ):
				trigger.setCmd( triggerData.cmd )

			#now hook up connects
			connectIdxRemap = {}
			if hasattr( triggerData, 'connectsDict' ):
				connectIdxs = sorted( triggerData.connectsDict.keys() )
				for connectIdx in connectIdxs:
					connectNodeName = triggerData.connectsDict[connectIdx]
					actualIdx = trigger.connect( connectNodeName )

					#if the connect idx differs then we need to fix the command strings to use the new idx
					if actualIdx != connectIdx:
						connectIdxRemap[connectIdx] = actualIdx

			#now setup menus
			if hasattr( triggerData, 'menus' ):
				trigger.setKillState( triggerData.killState )
				for menuName, menuCmd in triggerData.menus:
					trigger.createMenu( menuName, menuCmd )

			#replace connect indices
			if connectIdxRemap:
				trigger.replaceConnectInCmd( connectIdxRemap )
				trigger.replaceConnectInMenuCmds( connectIdxRemap )


def listPresets():
	return PRESET_MANAGER.listAllPresets( True )


#end
