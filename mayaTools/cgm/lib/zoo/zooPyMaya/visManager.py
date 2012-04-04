
import datetime

from zooPy import presets

import maya.cmds as cmd
import melUtils

from mayaDecorators import d_showWaitCursor

mel = melUtils.mel
melecho = melUtils.melecho

TOOL_NAME = 'visManager'
TOOL_VERSION = 1
EXTENSION = presets.DEFAULT_XTN
DEFAULT_LOCALE = presets.LOCAL


def exportPreset( presetName, visHierarchyTop, locale=DEFAULT_LOCALE ):
	'''
	exports a vis hierarchy preset file - this file contains a node hierarchy which represents a vis hierarchy.
	each empty transform node in the group represents a set, and each volume in the structure represents a face
	selection used to determine vis set membership
	'''
	exportDict = {}

	#simply returns the
	def getVolumesAndEmptyGroups( node ):
		children = cmd.listRelatives(node, type='transform', path=True)
		volumes = []
		groups = []
		for child in children:
			shapes = cmd.listRelatives(child, shapes=True, type='nurbsSurface', path=True)
			if shapes:
				type = int( cmd.getAttr('%s.exportVolume' % child) )
				pos = cmd.xform(child, q=True, ws=True, rp=True)
				rot = cmd.xform(child, q=True, ws=True, ro=True)
				scale = cmd.getAttr('%s.s' % child)[0]
				volumes.append( (child, type, pos, rot, scale) )
			else: groups.append( child )

		return volumes, groups

	topVolumes, topGroups = getVolumesAndEmptyGroups(visHierarchyTop)
	parentQueue = [(visHierarchyTop, topGroups)]

	#create the first entry
	toExport = [(visHierarchyTop, None, topVolumes)]

	while True:
		try:
			curNode = topGroups.pop(0)
			curParent = cmd.listRelatives(curNode, p=True)[0]
			curVolumes, curChildren = getVolumesAndEmptyGroups(curNode)
			topGroups.extend(curChildren)
			toExport.append( (curNode, curParent, curVolumes) )
		except IndexError: break

	exportDict['preset'] = toExport
	thePreset = presets.Preset(locale, TOOL_NAME, presetName, EXTENSION)
	thePreset.pickle(exportDict)


@d_showWaitCursor
def importPreset( presetName, locale=DEFAULT_LOCALE, createSets=True, deleteAfterImport=True ):
	thePreset = presets.Preset(locale, TOOL_NAME, presetName, EXTENSION)
	presetData = thePreset.unpickle()
	volumesList = presetData['preset']

	#if we're creating the vis sets, then we need to grab a list of meshes in the scene
	allMeshes = set(cmd.ls(type='mesh'))

	#this dict tracks what the names were when they were written out, vs what names they are
	#after building them in scene - names can change due to clashes etc...
	nodesDict = {}

	#this dict tracks teh nodes and their corresponding set representation (should one exist...)
	setDict = {}
	for node, parent, volumesData in volumesList:
		curNode = cmd.group(empty=True)
		curNode = cmd.rename(curNode, node)

		#if the parent exists in the node list (it should always exist except for the top node...
		try: curNode = cmd.parent(curNode, nodesDict[parent])[0]
		except KeyError: pass

		nodesDict[node] = curNode
		volumes = []

		#build the volumes - place and parent them appropriately
		for volume, type, pos, rot, scale in volumesData:
			newVolume = createExportVolume( int(type) )
			cmd.move(pos[0], pos[1], pos[2], newVolume, a=True, ws=True, rpr=True)
			cmd.rotate(rot[0], rot[1], rot[2], newVolume, a=True, ws=True)
			cmd.setAttr('%s.s' % newVolume, *scale)
			newVolume = cmd.rename(newVolume, volume)
			cmd.parent(newVolume, curNode)
			volumes.append(newVolume)

		if createSets:
			items = []
			setParent = ''
			try: setParent = setDict[parent]
			except KeyError: pass

			for vol in volumes: items.extend( findFacesInVolumeForMaya(allMeshes, vol) )
			newSet = mel.zooVisManCreateSet(setParent, node, items)
			setDict[node] = newSet

	if deleteAfterImport:
		cmd.delete( nodesDict[ volumesList[0][0] ] )

	#return the created volumes
	return nodesDict.keys(),


#end