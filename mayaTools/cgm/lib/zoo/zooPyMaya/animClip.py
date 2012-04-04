
import maya
import maya.OpenMayaAnim
import maya.cmds as cmd
from maya.cmds import getAttr, setAttr, deleteAttr, objExists, createNode, xform, move, rotate, setKeyframe

from zooPy import strUtils
from zooPy.vectors import Vector, Matrix
from mayaDecorators import d_unifyUndo, d_noAutoKey, d_maintainSceneSelection
import cmdStrResolver
import mappingUtils
import constants

class AnimLibError(Exception): pass


def iterAtTimes( timeValues ):
	initialTime = cmd.currentTime( q=True )
	for time in timeValues:
		if time is None:
			continue

		maya.OpenMayaAnim.MAnimControl.setCurrentTime( maya.OpenMaya.MTime( time ) )
		yield time

	cmd.currentTime( initialTime )


class AttributeData(object):
	def __init__( self, attrPath ):
		self._value = getAttr( attrPath )
	def apply( self, attrPath, sourceRange, applyStart, additive=False ):
		if additive:
			setAttr( attrPath, getAttr( attrPath ) + self._value )
		else:
			setAttr( attrPath, self._value )


class KeyframeData(tuple):
	DATA_IDX = TIME, VALUE, ITT, OTT, ITX, ITY, OTX, OTY, BREAKDOWN, TAN_LOCK, WEIGHT_LOCK, WEIGHTED, PRE_INF, POST_INF, CURVE_TYPE = range(15)

	def __new__( cls, attrPath ):
		animCurveNode = cmd.listConnections( attrPath, type='animCurve', d=False )
		if animCurveNode is None:
			return AttributeData( attrPath )

		animCurveNode = animCurveNode[0]
		times = getAttr( '%s.ktv[*].keyTime' % animCurveNode )
		values = getAttr( '%s.ktv[*].keyValue' % animCurveNode )

		itt = getAttr( '%s.kit[*]' % animCurveNode )
		ott = getAttr( '%s.kot[*]' % animCurveNode )

		itx = getAttr( '%s.kix[*]' % animCurveNode )
		ity = getAttr( '%s.kiy[*]' % animCurveNode )
		otx = getAttr( '%s.kox[*]' % animCurveNode )
		oty = getAttr( '%s.koy[*]' % animCurveNode )

		brk = getAttr( '%s.keyBreakdown[*]' % animCurveNode )
		tlk = getAttr( '%s.keyTanLocked[*]' % animCurveNode )
		wlk = getAttr( '%s.keyWeightLocked[*]' % animCurveNode )

		#if there is only one value in the array attributes above, maya in its infinite wisdom returns the value as a float, not a single element list.  well done.
		if not isinstance( times, list ):
			times = [times]
			values = [values]
			itt = [itt]
			ott = [ott]
			itx = [itx]
			ity = [ity]
			otx = [otx]
			oty = [oty]
			brk = [brk]
			tlk = [tlk]
			wlk = [wlk]

		weighted = getAttr( '%s.wgt' % animCurveNode )
		preInf = getAttr( '%s.pre' % animCurveNode )
		postInf = getAttr( '%s.pst' % animCurveNode )
		curveType = cmd.nodeType( animCurveNode )

		return tuple.__new__( cls, (times, values, itt, ott, itx, ity, otx, oty, brk, tlk, wlk, weighted, preInf, postInf, curveType) )
	def constructNode( self, timeOffset=0 ):
		'''
		constructs an animCurve node using the data stored on the instance

		returns the node created
		'''
		animCurveNode = createNode( self[ self.CURVE_TYPE ] )

		#massage the time values
		times = [ t+timeOffset for t in self[ self.TIME ] ]
		values = self[ self.VALUE ]
		maxIdxVal = len( values ) - 1

		setKeyframe = cmd.setKeyframe
		for time, value in zip( times, values ):
			setKeyframe( animCurveNode, t=time, v=value )

		#set key data
		setAttr( '%s.wgt' % animCurveNode, self[ self.WEIGHTED ] )
		setAttr( '%s.pre' % animCurveNode, self[ self.PRE_INF ] )
		setAttr( '%s.pst' % animCurveNode, self[ self.POST_INF ] )

		setAttr( '%s.keyBreakdown[0:%d]' % (animCurveNode, maxIdxVal), *self[ self.BREAKDOWN ] )
		setAttr( '%s.keyTanLocked[0:%d]' % (animCurveNode, maxIdxVal), *self[ self.TAN_LOCK ] )
		setAttr( '%s.keyWeightLocked[0:%d]' % (animCurveNode, maxIdxVal), *self[ self.WEIGHT_LOCK ] )

		setAttr( '%s.kix[0:%d]' % (animCurveNode, maxIdxVal), *self[ self.ITX ] )
		setAttr( '%s.kiy[0:%d]' % (animCurveNode, maxIdxVal), *self[ self.ITY ] )
		setAttr( '%s.kox[0:%d]' % (animCurveNode, maxIdxVal), *self[ self.OTX ] )
		setAttr( '%s.koy[0:%d]' % (animCurveNode, maxIdxVal), *self[ self.OTY ] )

		setAttr( '%s.kit[0:%d]' % (animCurveNode, maxIdxVal), *self[ self.ITT ] )
		setAttr( '%s.kot[0:%d]' % (animCurveNode, maxIdxVal), *self[ self.OTT ] )

		return animCurveNode
	def apply( self, attrPath, sourceRange, applyStart, additive=False ):
		'''
		used to put the animation data on this instance to an actual attribute

		sourceRange should be a 2-tuple representing the 0-based time range of the animation data to apply
		applyStart should be the start time at which to place the animation
		'''

		#if the attrPath isn't settable, bail - maya sometimes crashes if you try to pasteKey on a non-settable attr
		if not getAttr( attrPath, se=True ):
			return

		keyCmdKwargs = {}
		if sourceRange:
			keyCmdKwargs[ 't' ] = sourceRange

		animCurveNode = self.constructNode( applyStart )
		if additive:
			if cmd.keyframe( attrPath, q=True, kc=True ):
				for t in cmd.keyframe( animCurveNode, q=True ):
					val = cmd.keyframe( attrPath, t=(t,), q=True, vc=True, eval=True ) or [getAttr( attrPath )]
					cmd.keyframe( animCurveNode, t=(t,), e=True, vc=val[0], relative=True )
			else:
				cmd.keyframe( animCurveNode, e=True, vc=getAttr( attrPath ), relative=True )

		try:
			cmd.copyKey( animCurveNode, clipboard='api', **keyCmdKwargs )
			cmd.pasteKey( attrPath, option='replace', clipboard='api' )
		finally:
			cmd.delete( animCurveNode )


class NodeKeyServer(object):
	def __init__( self, nodes, visitKeys=True, attrs=None, range=(None, None) ):
		self._nodes = nodes

		#if True then each key time is actually visted during iteration
		self._visit = visitKeys

		#stores the attributes to key keys from
		self._attrs = attrs

		#if not None, only keys between the given range (inclusive) will be visited
		self._range = range

		#stores the objects stored at each time
		self._timeNodesDict = None
	def _generateTimeNodesDict( self ):
		if self._timeNodesDict is not None:
			return self._timeNodesDict

		self._timeNodesDict = timeNodesDict = {}

		nodes = self._nodes
		nodesWithKeys = set()
		keyTimes = self.getKeyTimes()
		for keyTime in keyTimes:
			timeNodesDict[ keyTime ] = nodesAtTime = []
			for node in nodes:
				if cmd.keyframe( node, t=(keyTime,), q=True, kc=True ):
					nodesWithKeys.add( node )
					nodesAtTime.append( node )

		timeNodesDict[None] = list( set( nodes ).difference( nodesWithKeys ) )

		return keyTimes, timeNodesDict
	def __iter__( self ):
		keyTimes, timeNodesDict = self._generateTimeNodesDict()

		#we yield None first so that if there are nodes without keys they get handled first
		self._currentTime = None
		yield None

		iterFunction = iterAtTimes if self._visit else iter
		startTime, endTime = self._range
		for keyTime in iterFunction( keyTimes ):
			if startTime is not None:
				if keyTime < startTime:
					continue

			self._currentTime = keyTime
			yield keyTime

			if endTime is not None:
				if keyTime > endTime:
					break

		del self._currentTime
	def getNodes( self ):
		'''
		returns the list of nodes that are at the time currently being iterated at
		'''
		if not hasattr( self, '_currentTime' ):
			raise TypeError( "Not currently iterating!  You can only query the nodes while iterating" )

		return tuple( self._timeNodesDict[ self._currentTime ] )
	def getKeyTimes( self ):
		try:
			return self._keyTimes
		except AttributeError: pass

		keyframeKwargs = {}
		if self._attrs:
			keyframeKwargs[ 'at' ] = self._attrs

		self._keyTimes = keyTimes = tuple( sorted( set( cmd.keyframe( self._nodes, q=True, **keyframeKwargs ) ) ) )

		return keyTimes
	def getRange( self ):
		keyTimes = self.getKeyTimes()

		return keyTimes[0], keyTimes[-1]


class AttrpathKeyServer(NodeKeyServer):
	def __init__( self, attrpaths, visitKeys=False ):
		super( AttrpathKeyServer, self ).__init__( attrpaths, visitKeys )
	def _get( self, idx ):
		attrpaths = super( AttrpathKeyServer, self ).getNodes()
		nodes = set( attrpath.split('.')[idx] for attrpath in attrpaths )

		return tuple( nodes )
	def getNodes( self ):
		return self._get( 0 )
	def getAttrNames( self ):
		return self._get( 1 )


def _getAttrNames( obj, attrNamesToSkip=() ):
	'''
	returns a list of attribute names on the given node to slurp animation data from.  Attributes will be keyable and
	visible in the channelBox
	'''

	#grab attributes
	objAttrs = cmd.listAttr( obj, keyable=True, visible=True, scalar=True ) or []

	#also grab alias' - its possible to pass in an alias name, so we need to test against them as well
	aliass = cmd.aliasAttr( obj, q=True ) or []

	#because the aliasAttr cmd returns a list with the alias, attr pairs in a flat list, we need to iterate over the list, skipping every second entry
	itAliass = iter( aliass )
	for attr in itAliass:
		objAttrs.append( attr )
		itAliass.next()

	filteredAttrs = []
	for attr in objAttrs:
		skipAttr = False
		for skipName in attrNamesToSkip:
			if attr == skipName:
				skipAttr = True
			elif attr.startswith( skipName +'[' ) or attr.startswith( skipName +'.' ):
				skipAttr = True

		if skipAttr:
			continue

		filteredAttrs.append( attr )

	return filteredAttrs


#defines a mapping between node type, and the function used to get a list of attributes from that node to save to the clip.  by default getObjAttrNames( obj ) is called
GET_ATTR_BY_NODE_TYPE = { 'blendShape': lambda obj: getObjAttrNames( obj, ('envelope', 'weight', 'inputTarget') ) }


def getNodeAttrNames( node ):
	nodeType = cmd.nodeType( node )

	return GET_ATTR_BY_NODE_TYPE.get( nodeType, _getAttrNames )( node )


def getPlaybackRange():
	'''
	returns a 2-tuple of startTime, endTime.  The values are taken from the visible playback unless there is a time selection.
	If there is a time selection, then its range is returned instead
	'''
	if cmd.timeControl( 'timeControl1', q=True, rv=True ):  #NOTE: timeControl1 is the name of maya's default, global timeControl widget...
		return cmd.timeControl( 'timeControl1', q=True, range=True )

	return int( cmd.playbackOptions( q=True, min=True ) ), int( cmd.playbackOptions( q=True, max=True ) )


class BaseClip(object):
	class ApplySettings(object):
		def __init__( self, sourceRange=None, applyStart=None ):
			'''
			sourceRange is the 0-based range from the clip
			applyStart is the frame at which animation should be pasted - if it is None animation is pasted at the current time
			'''
			self.sourceRange = sourceRange
			self.applyStart = applyStart
		def getTimeOffset( self, originalRange=(0,None) ):
			originalStart, originalEnd = originalRange
			sourceRange = self.sourceRange
			applyStart = self.applyStart

			timeOffset = -originalStart  #if the original clip started at frame 1 then we need to offset all times by -1...
			if applyStart is not None:
				timeOffset += applyStart

			if sourceRange:
				if sourceRange[1] < sourceRange[0]:
					raise ValueError( "Bad sourceRange specified: %s, %s" % sourceRange )

				timeOffset -= sourceRange[0]  #because we want the first frame

			return timeOffset
		def generateKeyTransformDict( self, keyTimes, originalRange=(0,None) ):
			'''
			given a list of keyTimes this method will transform the keytimes based on the settings stored on this instance
			'''
			timeOffset = self.getTimeOffset( originalRange )
			sourceRange = self.sourceRange

			keyTransformDict = {}
			keyTimes.sort()
			for keyTime in keyTimes:

				#if there is a specified source range, make sure we're within it
				if sourceRange is not None:
					if sourceRange[0] is not None:
						if keyTime - originalRange[0] < sourceRange[0]:
							continue
					if sourceRange[1] is not None:
						if keyTime - originalRange[0] > sourceRange[1]:
							break

				keyTransformDict[keyTime + timeOffset] = keyTime

			return keyTransformDict

	def setMapping( self, mapping ):
		'''
		subclasses should implement this - it should change the key for all the data stored in the clip to whatever is
		given in the mapping.  This method should return a new Clip with the mapping applied
		'''
	def applyToNodes( self, nodes, **kw ):
		mapping = mappingUtils.matchNames( self.getNodes(), nodes )
		self.setMapping( mapping ).apply( nodes, **kw )
	def applyToSelection( self, **kw ):
		selection = cmd.ls( sl=True ) or []
		self.applyToNodes( selection, **kw )


class TransformClip(BaseClip):
	'''
	stores actual transform data for the given list of nodes
	'''
	_ATTRS = ('t', 'r')

	@classmethod
	def Generate( cls, nodes ):
		originalRange = getPlaybackRange()
		keyTimeDataDict = {}

		nodesWithKeys = set()

		attrs = cls._ATTRS
		keyServer = NodeKeyServer( nodes, attrs=attrs )
		for keyTime in keyServer:
			nodesAtTime = keyServer.getNodes()
			keyTimeDataDict[ keyTime ] = nodeDataDict = {}
			for node in nodesAtTime:
				nodesWithKeys.add( node )

				#skip non-transform nodes...  duh
				if not cmd.objectType( node, isAType='transform' ):
					continue

				pos = xform( node, q=True, ws=True, rp=True )
				rot = xform( node, q=True, ws=True, ro=True )
				nodeDataDict[ node ] = pos, rot, getAttr( '%s.ro' % node )

		return cls( keyTimeDataDict, originalRange )

	def __init__( self, keyTimeDataDict, originalRange ):
		self._originalRange = originalRange
		self._keyTimeDataDict = keyTimeDataDict
	def getNodes( self ):
		nodes = set()
		for _x, nodeDataDict in self._keyTimeDataDict.iteritems():
			nodes.update( set( nodeDataDict.keys() ) )

		return list( nodes )
	def getPostProcessCmdDict( self ):
		cmdDict = {}
		for node in self.getNodes():
			postProcessCmdAttrpath = '%s.xferPostTraceCmd' % node
			if objExists( postProcessCmdAttrpath ):
				cmdDict[ node ] = getAttr( postProcessCmdAttrpath )

		return cmdDict
	def setMapping( self, mapping ):
		newKeyTimeDataDict = {}
		for _t, nodeDict in self._keyTimeDataDict.iteritems():
			newNodeDict = {}
			for src, tgt in mapping.iteritems():
				if not tgt:
					continue

				if src in nodeDict:
					newNodeDict[ tgt ] = nodeDict[ src ]

			if newNodeDict:
				newKeyTimeDataDict[ _t ] = newNodeDict

		return TransformClip( newKeyTimeDataDict, self._originalRange )
	@d_unifyUndo
	@d_noAutoKey
	@d_maintainSceneSelection
	def apply( self, nodes=None, applySettings=None, additive=False ):
		if nodes is None:
			nodes = self.getNodes()

		if applySettings is None:
			applySettings = self.ApplySettings()

		if not nodes:
			return

		#this is a touch ugly - but we want to make a copy of the keyTimeDict because we want to pop out the None value
		#before transforming the key times
		keyTimeDataDict = {}
		keyTimeDataDict.update( self._keyTimeDataDict )

		nodesWithoutKeys = keyTimeDataDict.pop( None, [] )

		attrs = self._ATTRS
		keyTimes = sorted( keyTimeDataDict.keys() )

		postCmdDict = self.getPostProcessCmdDict()

		#ok so this is a little ugly - not sure how to make it cleaner however.  Anyhoo, here we need to transform the key times
		#but we need the original key times because we use them as a lookup to the nodes with keys at that time...  so we build
		#a dictionary to store the mapping
		transformedKeyTimes = applySettings.generateKeyTransformDict( keyTimes, self._originalRange )
		sortedKeyTimes = sorted( transformedKeyTimes.keys() )

		"""#if we're applying additively then grab the initial transform values and add them to the stored values
		if additive:
			for transformedKeyTime in iterAtTimes( sortedKeyTimes ):
				keyTime = transformedKeyTimes[ transformedKeyTime ]
				nodesAtTimeDict = self._keyTimeDataDict[keyTime]
				newNodesAtTimeDict = self._keyTimeDataDict[keyTime] = {}
				for node, (pos, rot, storedRotateOrder) in nodesAtTimeDict.items():
					initialPos = Vector( xform( node, q=True, ws=True, rp=True ) )
					initialRot = Vector( xform( node, q=True, ws=True, ro=True ) )
					newNodesAtTimeDict[node] = initialPos+pos, initialRot+rot, storedRotateOrder"""

		for transformedKeyTime in iterAtTimes( sortedKeyTimes ):
			keyTime = transformedKeyTimes[ transformedKeyTime ]
			nodesAtTimeDict = self._keyTimeDataDict[ keyTime ]
			for node, (pos, rot, storedRotateOrder) in nodesAtTimeDict.iteritems():
				move( pos[0], pos[1], pos[2], node, ws=True, a=True, rpr=True )

				roAttrpath = '%s.ro' % node
				initialRotateOrder = getAttr( roAttrpath )
				rotateOrderMatches = initialRotateOrder == storedRotateOrder

				#if the rotation order is different, we need to compensate - we check because its faster if we don't have to compensate
				if rotateOrderMatches:
					rotate( rot[0], rot[1], rot[2], node, ws=True, a=True )
				else:
					setAttr( '%s.ro' % node, storedRotateOrder )
					rotate( rot[0], rot[1], rot[2], node, ws=True, a=True )
					xform( node, rotateOrder=constants.ROTATE_ORDER_STRS[ initialRotateOrder ], preserve=True )

				if keyTime is not None:
					setKeyframe( node, t=(transformedKeyTime,), at=attrs )

		#make sure to filter rotation curves
		for node in nodes:
			cmd.filterCurve( '%s.rx' % node, '%s.ry' % node, '%s.rz' % node, filter='euler' )


class ChannelClip(BaseClip):
	'''
	stores raw keyframe data for all animated channels on the given list of nodes
	'''

	@classmethod
	def Generate( cls, nodes ):
		'''
		generates a new AnimClip instance from the given list of nodes
		'''
		originalRange = getPlaybackRange()
		nodeDict = {}
		for node in nodes:
			nodeDict[ node ] = dataDict = {}
			for attrName in getNodeAttrNames( node ):
				dataDict[ attrName ] = KeyframeData( '%s.%s' % (node, attrName) )

		return cls( nodeDict, originalRange )

	def __init__( self, nodeDict, originalRange ):
		self._originalRange = originalRange
		self._nodeDict = nodeDict
	def getNodes( self ):
		return self._nodeDict.keys()
	def setMapping( self, mapping ):
		newNodeDict = {}
		for src, tgt in mapping.iteritems():
			if src in self._nodeDict:
				newNodeDict[ tgt ] = self._nodeDict[ src ]

		return ChannelClip( newNodeDict, self._originalRange )
	@d_unifyUndo
	@d_noAutoKey
	@d_maintainSceneSelection
	def apply( self, nodes=None, applySettings=None, additive=False ):
		'''
		will apply the animation data stored in this clip to the given mapping targets

		applySettings expects an AnimClip.ApplySettings instance or None
		'''
		if nodes is None:
			nodes = self._nodeDict.keys()

		if applySettings is None:
			applySettings = self.ApplySettings()

		timeOffset = applySettings.getTimeOffset( self._originalRange )
		for node in nodes:
			if node in self._nodeDict:
				dataDict = self._nodeDict[ node ]
				for attrName, keyData in dataDict.iteritems():
					attrPath = '%s.%s' % (node, attrName)
					try:
						keyData.apply( attrPath, applySettings.sourceRange, timeOffset, additive )

					#usually happens if the attrPath doesn't exist or is locked...
					except RuntimeError: continue


class AnimClip(BaseClip):
	'''
	stores both a ChannelClip instance and a TransformClip instance for the given list of nodes
	'''
	@classmethod
	def Generate( cls, nodes, worldSpace=False ):
		channelClip = ChannelClip.Generate( nodes )
		transformClip = None
		if worldSpace:
			transformClip = TransformClip.Generate( [node for node in nodes if cmd.objectType( node, isAType='transform' )] )

		return cls( channelClip, transformClip )

	def __init__( self, channelClip, transformClip ):
		self._channelClip = channelClip
		self._transformClip = transformClip
	def getNodes( self ):
		nodes = self._channelClip.getNodes()
		if self._transformClip:
			nodes += self._transformClip.getNodes()

		return list( set( nodes ) )
	def setMapping( self, mapping ):
		cc = self._channelClip.setMapping( mapping )
		if self._transformClip:
			return AnimClip( cc, self._transformClip.setMapping( mapping ) )

		return AnimClip( cc, None )
	@d_unifyUndo
	def apply( self, nodes=None, applySettings=None, worldSpace=False, additive=False ):
		self._channelClip.apply( nodes, applySettings, additive )
		if worldSpace and self._transformClip:
			self._transformClip.apply( nodes, applySettings, additive )


class PoseClip(BaseClip):
	@classmethod
	def Generate( cls, nodes, worldSpace=True ):
		'''
		generates a new AnimClip instance from the given list of nodes
		'''
		nodeDict = {}
		worldNodeDict = {}
		for node in nodes:
			nodeDict[ node ] = dataDict = {}
			for attrName in getNodeAttrNames( node ):
				dataDict[ attrName ] = getAttr( '%s.%s' % (node, attrName) )

			if worldSpace:
				if cmd.objectType( node, isAType='transform' ):
					pos = xform( node, q=True, ws=True, rp=True )
					rot = xform( node, q=True, ws=True, ro=True )
					worldNodeDict[ node ] = pos, rot, getAttr( '%s.ro' % node )

		return cls( nodeDict, worldNodeDict )

	def __init__( self, attrDict, worldAttrDict ):
		self._nodeAttrDict = attrDict
		self._nodeWorldDict = worldAttrDict
	def getNodes( self ):
		return self._nodeAttrDict.keys()
	def setMapping( self, mapping ):
		assert isinstance( mapping, strUtils.Mapping )
		newNodeAttrDict = {}
		newNodeWorldDict = {}
		for src, tgt in mapping.iteritems():
			if src in self._nodeAttrDict:
				newNodeAttrDict[ tgt ] = self._nodeAttrDict[ src ]

			if src in self._nodeWorldDict:
				newNodeWorldDict[ tgt ] = self._nodeWorldDict[ src ]

		return PoseClip( newNodeAttrDict, newNodeWorldDict )
	@d_unifyUndo
	@d_noAutoKey
	@d_maintainSceneSelection
	def apply( self, nodes=None, applySettings=None, worldSpace=False, additive=False ):
		if nodes is None:
			nodes = self._nodeAttrDict.iterkeys()

		for node in nodes:
			if node in self._nodeAttrDict:
				for attr, value in self._nodeAttrDict[ node ].iteritems():
					attrpath = '%s.%s' % (node, attr)
					if objExists( attrpath ):
						if additive:
							value += getAttr( attrpath )

						setAttr( attrpath, value, clamp=True )

			if worldSpace:
				if node in self._nodeWorldDict:
					if cmd.objectType( node, isAType='transform' ):
						pos, rot, rotateOrder = self._nodeWorldDict[node]
						if additive:
							pos = Vector( pos ) + Vector( xform( node, q=True, ws=True, rp=True ) )

						move( pos[0], pos[1], pos[2], node, ws=True, a=True, rpr=True )

						roAttrpath = '%s.ro' % node
						initialRotateOrder = getAttr( roAttrpath )
						rotateOrderMatches = initialRotateOrder == rotateOrder

						if rotateOrderMatches:
							if additive:
								rot = Vector( rot ) + Vector( xform( node, q=True, ws=True, ro=True ) )

							rotate( rot[0], rot[1], rot[2], node, ws=True, a=True )
						else:
							if additive:
								xform( node, ro=constants.ROTATE_ORDER_STRS[ rotateOrder ], p=True )
								rot = Vector( rot ) + Vector( xform( node, q=True, ws=True, ro=True ) )

							setAttr( roAttrpath, rotateOrder )
							rotate( rot[0], rot[1], rot[2], node, ws=True, a=True )
							xform( node, ro=constants.ROTATE_ORDER_STRS[ initialRotateOrder ], p=True )
	def blend( self, other, amount, additive=False ):
		assert isinstance( other, PoseClip )

		#this simplifies the code below as we don't have to check which values exist in one dict and not the other
		for key, value in self._nodeAttrDict.iteritems():
			other._nodeAttrDict.setdefault( key, value )

		for key, value in other._nodeAttrDict.iteritems():
			self._nodeAttrDict.setdefault( key, value )

		#build new dicts by blending values from the two clips
		newNodeAttrDict = {}
		for node, nodeAttrDict in self._nodeAttrDict.iteritems():
			otherNodeAttrDict = other._nodeAttrDict[ node ]
			newNodeAttrDict[ node ] = newAttrDict = {}
			for attr, value in nodeAttrDict.iteritems():
				if attr in otherNodeAttrDict:
					otherValue = otherNodeAttrDict[ attr ]
				else:
					otherValue = value

				if additive:
					newAttrDict[ attr ] = value + (otherValue * amount)
				else:
					newAttrDict[ attr ] = (value * (1-amount)) + (otherValue * amount)

		newWorldAttrDict = {}
		for node, (pos, rot, ro) in self._nodeWorldDict.iteritems():
			if node in other._nodeWorldDict:
				otherPos, otherRot, otherRo = other._nodeWorldDict[node]
				#if ro != otherRo things get a bit more complicated...
				if additive:
					blendedPos = Vector( pos ) + (Vector( otherPos ) * amount)
					blendedRot = Vector( rot ) + (Vector( otherRot ) * amount)
				else:
					blendedPos = (Vector( pos ) * (1-amount)) + (Vector( otherPos ) * amount)
					blendedRot = (Vector( rot ) * (1-amount)) + (Vector( otherRot ) * amount)

				newWorldAttrDict[node] = list(blendedPos), list(blendedRot), ro

		return PoseClip( newNodeAttrDict, newWorldAttrDict )


def generateClipFromSelection( clipType=AnimClip, worldSpace=False ):
	return clipType.Generate( cmd.ls( sl=True ), worldSpace )


class TangencyCopier(object):
	'''
	manages copying tangency information from one animCurve to another.  It refers to keys using key times
	not key indices so it works to some degree even if the two animCurves are quite different
	'''
	def __init__( self, srcAttrpath, tgtAttrpath ):
		srcAnimCurve, tgtAnimCurve = None, None
		srcCurves = cmd.listConnections( srcAttrpath, type='animCurve', d=False )
		if srcCurves:
			srcAnimCurve = srcCurves[0]

		tgtCurves = cmd.listConnections( tgtAttrpath, type='animCurve', d=False )
		if tgtCurves:
			tgtAnimCurve = tgtCurves[0]

		self._src = srcAnimCurve
		self._tgt = tgtAnimCurve
	def iterSrcTgtKeyIndices( self, start=None, end=None ):
		src, tgt = self._src, self._tgt
		srcIndices = getAttr( '%s.keyTimeValue' % src, multiIndices=True ) or []
		tgtIndices = getAttr( '%s.keyTimeValue' % tgt, multiIndices=True ) or []

		srcTimeValues = getAttr( '%s.keyTimeValue[*]' % src ) or []
		tgtTimeValues = getAttr( '%s.keyTimeValue[*]' % tgt ) or []

		tgtDataDict = {}
		for tgtIdx, (tgtTime, tgtValue) in zip( tgtIndices, tgtTimeValues ):
			tgtDataDict[ tgtTime ] = tgtIdx, tgtValue

		for srcIdx, (srcTime, srcValue) in zip( srcIndices, srcTimeValues ):

			#keep looping if a start time has been specified AND the time being visited comes before this time
			if start is not None and srcTime < start:
				continue

			#break out of the loop if an end time has been specified AND the time being visited comes after this time
			if end is not None and srcTime > end:
				break

			#check to see if a key exists on the tgt at the time being visited
			if srcTime in tgtDataDict:
				yield (srcIdx, srcValue), tgtDataDict[ srcTime ]
	def copy( self, start=None, end=None ):
		src, tgt = self._src, self._tgt
		if src is None or tgt is None:
			return

		setAttr( '%s.weightedTangents' % tgt, getAttr( '%s.weightedTangents' % src ) )
		for srcData, tgtData in self.iterSrcTgtKeyIndices( start, end ):
			srcIdx, srcValue = srcData
			tgtIdx, tgtValue = tgtData

			setAttr( '%s.keyTanLocked[%d]' % (tgt, tgtIdx), getAttr( '%s.keyTanLocked[%d]' % (src, srcIdx) ) )
			setAttr( '%s.keyWeightLocked[%d]' % (tgt, tgtIdx), getAttr( '%s.keyWeightLocked[%d]' % (src, srcIdx) ) )
			setAttr( '%s.keyTanInX[%d]' % (tgt, tgtIdx), getAttr( '%s.keyTanInX[%d]' % (src, srcIdx) ) )
			setAttr( '%s.keyTanInY[%d]' % (tgt, tgtIdx), getAttr( '%s.keyTanInY[%d]' % (src, srcIdx) ) )
			setAttr( '%s.keyTanOutX[%d]' % (tgt, tgtIdx), getAttr( '%s.keyTanOutX[%d]' % (src, srcIdx) ) )
			setAttr( '%s.keyTanOutY[%d]' % (tgt, tgtIdx), getAttr( '%s.keyTanOutY[%d]' % (src, srcIdx) ) )
			setAttr( '%s.keyTanInType[%d]' % (tgt, tgtIdx), getAttr( '%s.keyTanInType[%d]' % (src, srcIdx) ) )
			setAttr( '%s.keyTanOutType[%d]' % (tgt, tgtIdx), getAttr( '%s.keyTanOutType[%d]' % (src, srcIdx) ) )
			setAttr( '%s.keyBreakdown[%d]' % (tgt, tgtIdx), getAttr( '%s.keyBreakdown[%d]' % (src, srcIdx) ) )


class Tracer(object):
	'''
	does intra-scene tracing
	'''
	def __init__( self, keysOnly=True, processPostCmds=True, start=None, end=None, skip=1 ):

		#if we're not tracing keys, then we're baking.  In this case, if start and end haven't been specified, then
		#we assume the user wants the current timeline baked
		if not keysOnly:
			if start is None:
				start = cmd.playbackOption( q=True, min=True )

			if end is None:
				start = cmd.playbackOption( q=True, min=True )

		self._keysOnly = keysOnly
		self._processPostCmds = processPostCmds
		self._start = start
		self._end = end
		self._skip = skip
	def _getTargetNodeInitialRotateOrderDict( self, mapping ):
		targetNodeInitialRotateOrderDict = {}

		#pre-lookup this data - otherwise we have to do a maya query within the loop below
		for node, targetNode in mapping.iteritems():
			targetRotateOrder = getAttr( '%s.ro' % targetNode )
			storedRotateOrder = getAttr( '%s.ro' % node )
			rotateOrderMatches = storedRotateOrder == targetRotateOrder
			targetNodeInitialRotateOrderDict[ targetNode ] = rotateOrderMatches, storedRotateOrder, constants.ROTATE_ORDER_STRS[ targetRotateOrder ]

		return targetNodeInitialRotateOrderDict
	@d_unifyUndo
	@d_noAutoKey
	@d_maintainSceneSelection
	def apply( self, mapping, copyTangencyData=True ):
		if not isinstance( mapping, strUtils.Mapping ):
			mapping = strUtils.Mapping( *mapping )

		targetNodeInitialRotateOrderDict = self._getTargetNodeInitialRotateOrderDict( mapping )
		postCmdDict = {}
		if self._processPostCmds:
			for tgt in mapping.tgts:
				postCmdDict[ tgt ] = PostTraceNode( tgt )

		if self._keysOnly:
			keyServer = NodeKeyServer( mapping.keys() )
		else:
			keyServer = iterAtTimes( range( self._start, self._end, self._skip ) )
			nodes = mapping.keys()
			keyServer.getNodes = lambda: nodes

		startTime = None
		for keyTime in keyServer:
			if startTime is None:
				startTime = keyTime

			nodesAtTime = set( keyServer.getNodes() )
			for node, targetNode in mapping.iteritems():
				if node not in nodesAtTime:
					continue

				pos = xform( node, q=True, ws=True, rp=True )
				rot = xform( node, q=True, ws=True, ro=True )
				move( pos[0], pos[1], pos[2], targetNode, ws=True, a=True, rpr=True )

				rotateOrderMatches, storedRotateOrder, targetRotateOrderStr = targetNodeInitialRotateOrderDict[ targetNode ]

				#if the rotation order is different, we need to compensate - we check because its faster if we don't have to compensate
				if rotateOrderMatches:
					rotate( rot[0], rot[1], rot[2], targetNode, ws=True, a=True )
				else:
					setAttr( '%s.ro' % targetNode, storedRotateOrder )
					rotate( rot[0], rot[1], rot[2], targetNode, ws=True, a=True )
					xform( targetNode, rotateOrder=targetRotateOrderStr, preserve=True )

				if targetNode in postCmdDict:
					postCmdDict[targetNode].execute()

				if keyTime is not None:
					setKeyframe( targetNode, at=TransformClip._ATTRS )

		endTime = keyTime
		if copyTangencyData:
			for src, tgt in mapping.iteritems():
				srcCurves = cmd.listConnections( src, type='animCurve', d=False, c=True ) or []
				iterSrcCurves = iter( srcCurves )
				for srcAttrpath in iterSrcCurves:
					srcCurve = iterSrcCurves.next()
					attrname = '.'.join( srcAttrpath.split( '.' )[ 1: ] )
					destAttrpath = '%s.%s' % (tgt, attrname)
					TangencyCopier( srcAttrpath, destAttrpath ).copy( startTime, endTime )


def bakeManualRotateDelta( src, ctrl, presetStr ):
	'''
	When you need to apply motion from a skeleton that is completely different from a skeleton driven
	by the rig you're working with (transferring motion from old assets to newer assets for example)
	you can manually align the control to the joint and then use this function to generate offset
	rotations and bake a post trace cmd.
	'''
	srcInvMat = Matrix( getAttr( '%s.worldInverseMatrix' % src ) )
	ctrlMat = Matrix( getAttr( '%s.worldMatrix' % ctrl ) )

	#generate the offset matrix as
	mat_o = ctrlMat * srcInvMat

	#now figure out the euler rotations for the offset
	ro = getAttr( '%s.ro' % ctrl )
	rotDelta = constants.MATRIX_ROTATION_ORDER_CONVERSIONS_TO[ ro ]( mat_o, True )

	#now get the positional delta
	posDelta = Vector( xform( src, q=True, ws=True, rp=True ) ) - Vector( xform( ctrl, q=True, ws=True, rp=True ) )
	posDelta *= -1
	ctrlParentInvMat = Matrix( getAttr( '%s.parentInverseMatrix' % ctrl ) )
	posDelta = posDelta * ctrlParentInvMat

	#construct a list to use for the format str
	formatArgs = tuple( rotDelta ) + tuple( posDelta )

	#build the post trace cmd str
	PostTraceNode( ctrl ).setCmd( presetStr % formatArgs )

	return rotDelta


def autoGeneratePostTraceScheme( mapping ):
	cmdStr = 'rotate -r -os %0.2f %0.2f %0.2f #; move -r -os %0.4f %0.4f %0.4f #;'
	cmdFunc = bakeManualRotateDelta

	for src, tgt in mapping.iteritems():
		if not src:
			continue

		if not tgt:
			continue

		t, r = getAttr( '%s.t' % tgt )[0], getAttr( '%s.r' % tgt )[0]

		try: setAttr( '%s.t' % tgt, *t )
		except RuntimeError: pass

		try: setAttr( '%s.r' % tgt, *r )
		except RuntimeError: pass


class PostTraceNode(unicode):
	_POST_TRACE_ATTR_NAME = 'xferPostTraceCmd'
	def __new__( cls, node ):
		new = unicode.__new__( cls, node )
		try:
			new._cmdStr = getAttr( '%s.%s' % (node, cls._POST_TRACE_ATTR_NAME) )
		except ValueError: new._cmdStr = ''

		return new
	def getCmd( self ):
		return self._cmdStr
	def setCmd( self, cmdStr ):
		self._cmdStr = cmdStr
		attrpath = '%s.%s' % (self, self._POST_TRACE_ATTR_NAME)
		if not cmd.objExists( attrpath ):
			cmd.addAttr( self, ln=self._POST_TRACE_ATTR_NAME, dt='string' )

		setAttr( attrpath, cmdStr, typ='string' )
	def execute( self, connects=(), optionals=() ):
		if self._cmdStr:
			cmdStrResolver.resolveAndExecute( self._cmdStr, self, connects, optionals )
	def clear( self ):
		deleteAttr( '%s.%s' % (self, POST_TRACE_ATTR_NAME) )


class AnimCurveDuplicator(object):
	'''
	deals with duplicating anim curves
	'''
	def __init__( self, instanceCurves=False, matchRotateOrder=True ):
		self._instance = instanceCurves
		self._matchRo = matchRotateOrder
	@d_unifyUndo
	@d_maintainSceneSelection
	def apply( self, mapping ):
		for src, tgt in mapping.iteritems():
			for attrname in getNodeAttrNames( src ):
				tgtAttrpath = '%s.%s' % (tgt, attrname)
				if objExists( tgtAttrpath ):
					srcAttrpath = '%s.%s' % (src, attrname)
					srcCurve = cmd.listConnections( srcAttrpath, type='animCurve', d=False )
					if srcCurve:
						srcCurve = srcCurve[0]
						if not self._instance:
							srcCurve = cmd.duplicate( srcCurve )[0]

						cmd.connectAttr( '%s.output' % srcCurve, tgtAttrpath, f=True )

			if self._matchRo:
				tgtRoAttrpath = '%s.ro' % tgt
				if objExists( tgtRoAttrpath ):
					srcRoAttrpath = '%s.ro' % tgt
					if objExists( srcRoAttrpath ):
						setAttr( tgtRoAttrpath, getAttr( srcRoAttrpath ) )


#end
