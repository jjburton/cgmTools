
import maya.cmds as cmd


class KeyServer(object):
	'''
	This class is basically an iterator over keys set on the given objects.
	Key times are iterated over in chronological order.  Calling getNodes
	on the iterator will provide a list of nodes that have keys on the
	current frame
	'''
	def __init__( self, nodes, changeTime=True ):
		self._nodes = nodes
		self._changeTime = changeTime
		self._curIndex = 0
		self._keys = list( set( cmd.keyframe( nodes, q=True ) or [] ) )
		self._keys.sort()
		self._keyNodeDict = {}
		self._keyNodeDictHasBeenPopulated = False
	def _populateDict( self ):
		keyNodeDict = self._keyNodeDict
		for node in self._nodes:
			keys = cmd.keyframe( node, q=True )
			if keys:
				for key in set( keys ):
					keyNodeDict.setdefault( key, [] )
					keyNodeDict[ key ].append( node )

		self._keyNodeDictHasBeenPopulated = True
	def getNodesAtTime( self ):
		if not self._keyNodeDictHasBeenPopulated:
			self._populateDict()

		keyNodeDict = self._keyNodeDict

		return keyNodeDict[ self._keys[ self._curIndex ] ][:]
	def __iter__( self ):
		for key in self._keys:
			if self._changeTime:
				cmds.currentTime( key, e=True )

			yield key


#end
