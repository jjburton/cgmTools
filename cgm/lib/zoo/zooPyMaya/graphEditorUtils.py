
from maya import cmds


class GraphEditor(object):
	DEFUALT_GE_OUTLINER_NAME = 'graphEditor1OutlineEd'

	def __init__( self, editorName=DEFUALT_GE_OUTLINER_NAME ):
		self._name = editorName
		self._mainSC = cmds.outlinerEditor( editorName, q=True, mainListConnection=True )
		self._selectedSC = cmds.outlinerEditor( editorName, q=True, selectionConnection=True )
	def clearSelection( self ):
		cmds.selectionConnection( self._selectedSC, e=True, clear=True )
	def selectDefault( self ):
		self.setSelected( self.getDisplayedNodes() )
	def setSelected( self, nodes ):
		self.clearSelection()
		for node in nodes:
			cmds.selectionConnection( self._selectedSC, e=True, select=node )
	def getDisplayedNodes( self ):
		return cmds.selectionConnection( self._mainSC, q=True, obj=True ) or []
	def getSelected( self ):
		return cmds.selectionConnection( self._selectedSC, q=True, obj=True ) or []
	def getNodesWithSelectedChannels( self ):
		'''
		returns the list of nodes that have one or more of their channels selected
		'''
		nodes = set()
		for name in self.getSelected():
			nodes.add( name[ name.find( '.' ) ] )

		return list( nodes )
	def graphNamedChannels( self, channels ):
		'''
		graphs the named channels on all selected objects should the channel exist
		EXAMPLE:
		self.graphNamedChannels( ['tx', 'ty', 'tz'] )
		'''
		self.clearSelection()
		for node in self.getDisplayedNodes():
			for channel in channels:
				channelPath = '%s.%s' % (node, channel)
				if cmds.objExists( channelPath ):
					cmds.selectionConnection( self._selectedSC, e=True, select=channelPath )
	def toggleSelected( self ):
		selChannels = self.getSelected()
		if selChannels and self.areChannelsHighlighted():
			self.selectDefault()
		else:
			self.graphSelectedCurves()
	def areChannelsHighlighted( self ):
		'''
		returns whether the highlighted channels in the graph editor are attributes or not
		'''
		sel = cmds.selectionConnection( self._selectedSC, q=True, obj=True )
		for s in sel:
			if '.' in s:
				return True

		return False
	def graphSelectedCurves( self ):
		curves = cmds.keyframe( q=True, name=True, sl=True )
		if not curves:
			return

		self.clearSelection()
		for curve in curves:
			channel = cmds.listConnections( '%s.output' % curve, p=True, s=False )
			if cmds.objExists( channel[0] ):
				cmds.selectionConnection( self._selectedSC, e=True, select=channel[0] )


#end
