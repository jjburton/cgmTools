

from __future__ import with_statement

import inspect

from maya.cmds import *
import maya.cmds as cmd

from zooPy.path import Path
from zooPy.presets import PresetManager, Preset, LOCAL, GLOBAL
from zooPy.names import camelCaseToNice

import apiExtensions

from baseSkeletonBuilder import SkeletonPart, setupAutoMirror, TOOL_NAME, buildSkeletonPartContainer

XTN = 'skeleton'
PRESET_MANAGER = PresetManager( TOOL_NAME, XTN )

VERSION = 0

eval = __builtins__[ 'eval' ]  #restore python's eval...

class NoPartsError(Exception): pass


def generatePresetContents():
	lines = [ 'version=%d' % VERSION ]  #always store some sort of versioning variable

	hasParts = False
	for part in SkeletonPart.IterAllPartsInOrder():
		hasParts = True

		lines.append( '<part>' )
		lines.append( '%s=%s' % (part.__class__.__name__, part.getBuildKwargs()) )
		for item in part:
			itemParent = listRelatives( item, p=True, pa=True )
			if itemParent:
				itemParent = itemParent[0]
			else:
				itemParent = ''

			rad = getAttr( '%s.radius' % item )
			tx, ty, tz = xform( item, q=True, ws=True, rp=True )
			rx, ry, rz = xform( item, q=True, ws=True, ro=True )

			#store out the line of attributes to save for the item - NOTE: attributes are currently stored in a way that makes it possible to add/modify the attributes we need serialized reasonably easily...
			lines.append( '%s,%s=radius:%s;t:%s,%s,%s;r:%s,%s,%s;' % (item, itemParent, rad, tx, ty, tz, rx, ry, rz) )

		lines.append( '</part>' )

	if not hasParts:
		raise NoPartsError( "No parts found in scene!" )

	return '\n'.join( lines )


def writeToPreset( presetName ):
	preset = Preset( LOCAL, TOOL_NAME, presetName, XTN )
	writeToFilepath( preset.path() )


def writeToFilepath( presetFilepath ):
	try:
		contents = generatePresetContents()
	except NoPartsError:
		print "No parts found in the scene!"
		return

	Path( presetFilepath ).write( contents )


def loadFromPreset( presetName ):
	p = Preset( LOCAL, TOOL_NAME, presetName, XTN )
	if not p.exists():
		p = Preset( GLOBAL, TOOL_NAME, presetName, XTN )

	assert p.exists(), "Cannot find a %s preset called %s" % (XTN, presetName)

	return loadFromFilepath( p )


def loadFromFilepath( presetFilepath ):
	'''
	deals with unserializing a skeleton preset definition into the scene
	'''

	assert presetFilepath.exists(), "No preset file found!  %" % presetFilepath
	itemRemapDict = {}
	partList = []

	def cleanUp():
		#removes all items built should an exception occur
		for partType, partItems in partList:
			if partItems:
				delete( partItems[0] )

	lines = presetFilepath.read()
	linesIter = iter( lines )
	version = linesIter.next().strip()

	try:
		for line in linesIter:
			line = line.strip()

			#blank line?  skip...
			if not line:
				continue

			if line == '<part>':
				partTypeAndBuildKwargLine = linesIter.next().strip()
				toks = partTypeAndBuildKwargLine.split( '=' )
				numToks = len( toks )
				if numToks == 1:
					partType, partBuildKwargs = toks[0], {}
				elif numToks == 2:
					partType, partBuildKwargs = toks
					partBuildKwargs = eval( partBuildKwargs )

				partItems = []

				partList.append( (partType, partBuildKwargs, partItems) )

				while True:
					line = linesIter.next().strip()

					#blank line?  skip...
					if not line:
						continue

					#are we done with the part?
					if line == '</part>':
						break

					itemAndParent, attrInfo = line.split( '=' )
					item, parent = itemAndParent.split( ',' )
					attrBlocks = attrInfo.split( ';' )

					#construct the attr dict
					attrDict = {}
					for block in attrBlocks:
						if not block:
							continue

						attrName, attrData = block.split( ':' )
						attrData = [ d for d in attrData.split( ',' ) if d ]
						attrDict[ attrName ] = attrData

					#build the actual joint
					actualItem = apiExtensions.asMObject( createNode( 'joint', n=item ) )

					#insert the item and what it actually maps to in the scene into the itemRemapDict
					itemRemapDict[ item ] = actualItem

					#finally append to the list of items in this part
					partItems.append( (actualItem, parent, attrDict) )
	except StopIteration:
		cleanUp()
		raise IOError( "File is incomplete!" )
	except:
		cleanUp()
		raise

	parts = []
	for partType, partBuildKwargs, partItems in partList:
		items = []
		for (actualItem, parent, attrDict) in partItems:
			actualParent = itemRemapDict.get( parent, None )

			#do parenting if appropriate
			if actualParent is not None:
				cmd.parent( actualItem, actualParent )

			#set the joint size
			if 'radius' in attrDict:
				size = attrDict[ 'radius' ][0]
				setAttr( '%s.radius' % actualItem, float( size ) )

			#move to the appropriate position
			if 't' in attrDict:
				tx, ty, tz = map( float, attrDict[ 't' ] )
				move( tx, ty, tz, actualItem, a=True, ws=True, rpr=True )

			#rotate appropriately
			if 'r' in attrDict:
				rx, ry, rz = map( float, attrDict[ 'r' ] )
				rotate( rx, ry, rz, actualItem, a=True, ws=True )

			#append to the items list - so we can instantiate the part once we've finished building the items
			items.append( actualItem )

		#instantiate the part and append it to the list of parts created
		partClass = SkeletonPart.GetNamedSubclass( partType )
		partContainer = buildSkeletonPartContainer( partClass, partBuildKwargs, items )
		part = partClass( partContainer )
		part.convert( partBuildKwargs )

		parts.append( part )

	setupAutoMirror()
	for part in SkeletonPart.IterAllParts():
		part.visualize()

	return parts


def listPresets():
	return PRESET_MANAGER.listAllPresets( True )


#end
