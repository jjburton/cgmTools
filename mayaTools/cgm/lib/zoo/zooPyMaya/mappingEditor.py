
from zooPy import names
from zooPy.path import Path
from zooPy import presets
from zooPy.strUtils import Mapping

import presetsUI

from baseMelUI import *
from mappingUtils import findItem

TOOL_NAME = 'zoo'
TOOL_VER = 1
EXT = 'mapping'


class MappingLayout(MelHLayout):
	'''
	Acts as a generic UI for editing "mappings".  A mapping is basically just a dictionaries in maya,
	but they're used for things like animation transfer and weight transfer between one or more
	differing name sets.

	Mappings can be stored out to presets.
	'''

	#args for controlling the name mapping algorithm - see the names.matchNames method for documentation on what these variables actually control
	STRIP_NAMESPACES = True
	PARITY_MATCH = True
	UNIQUE_MATCHING = False
	MATCH_OPPOSITE_PARITY = False

	#defines whether namespaces are hidden from the list view of the data - defaults to True.  the namespaces are still stored, they just aren't displayed
	HIDE_NAMESPACES = True

	#if this is set to True, then sources can be mapped to multiple targets
	ALLOW_MULTI_SELECTION = True

	def __new__( cls, parent, *a, **kw ):
		return MelHLayout.__new__( cls, parent )
	def __init__( self, parent, srcItems=None, tgtItems=None ):
		MelHLayout.__init__( self, parent )
		self.expand = True

		self._srcToTgtDict = {}
		self._previousMappingFile = None

		szLeft = MelVLayout( self )
		szRight = MelVLayout( self )

		szLeft.expand = True
		szRight.expand = True

		self.UI_srcButton = srcBut = MelButton( szLeft, l='Source Items (click for menu)' )
		self.UI_tgtButton = tgtBut = MelButton( szRight, l='Target Items (click for menu)' )

		szLeft.setWeight( srcBut, 0 )
		szRight.setWeight( tgtBut, 0 )

		szHLeft = MelHLayout( szLeft )
		szHLeft.expand = True
		szHRight = MelHLayout( szRight )
		szHRight.expand = True

		vLayout = MelVLayout( szHLeft )
		self.UI_but_srcUp = MelButton( vLayout, label='up', vis=True, width=22, c=self.on_src_up )
		self.UI_but_srcDn = MelButton( vLayout, label='dn', vis=True, width=22, c=self.on_src_dn )
		vLayout.layout()
		szHLeft.setWeight( vLayout, 0 )

		self.UI_srcs = srcs = MelObjectScrollList( szHLeft, deleteKeyCommand=self.on_delete, doubleClickCommand=self.on_selectSrc )
		self.UI_srcs.setChangeCB( self.on_selectItemSrc )

		self.UI_tgts = MelObjectScrollList( szHRight, deleteKeyCommand=self.on_delete, doubleClickCommand=self.on_selectTgt, ams=True )
		self.UI_tgts.setChangeCB( self.on_selectItemTgt )

		#vLayout = MelVLayout( szHRight )
		#self.UI_but_tgtUp = MelButton( vLayout, label='up', vis=False, width=1, c=self.on_tgt_up )
		#self.UI_but_tgtDn = MelButton( vLayout, label='dn', vis=False, width=1, c=self.on_tgt_dn )
		#vLayout.layout()

		szLeft.layout()
		szRight.layout()
		szHLeft.layout()
		szHRight.layout()
		self.layout()

		MelPopupMenu( self.UI_srcs, pmc=self.build_srcMenu )
		MelPopupMenu( self.UI_tgts, pmc=self.build_tgtMenu )

		MelPopupMenu( self.UI_srcButton, pmc=self.build_srcMenu )
		MelPopupMenu( self.UI_tgtButton, pmc=self.build_tgtMenu )

		MelPopupMenu( self.UI_srcButton, b=1, pmc=self.build_srcMenu )
		MelPopupMenu( self.UI_tgtButton, b=1, pmc=self.build_tgtMenu )

		if srcItems is not None:
			self.addSrcItems( srcItems )

		if tgtItems is not None:
			self.addTgtItems( tgtItems )

	@property
	def srcs( self ):
		return self.UI_srcs.getItems()
	@property
	def tgts( self ):
		return self.UI_tgts.getItems()
	def showUpDownButtons( self ):
		self.UI_but_srcUp.show()
		self.UI_but_srcDn.show()
	def hideUpDownButtons( self ):
		self.UI_but_srcUp.hide()
		self.UI_but_srcDn.hide()
	def setSrcsLabel( self, newLabel ):
		self.UI_srcButton.setLabel( newLabel )
	def setTgtsLabel( self, newLabel ):
		self.UI_tgtButton.setLabel( newLabel )
	def getUnmappedSrcs( self ):
		return list( set( self.srcs ).difference( self.getMapping().srcs ) )
	def getUnmappedTgts( self ):
		return list( set( self.tgts ).difference( self.getMapping().tgts ) )
	def getMapping( self ):
		return Mapping.FromDict( self._srcToTgtDict )
	def setMapping( self, mapping ):
		if isinstance( mapping, dict ):
			self._srcToTgtDict = mapping
		elif isinstance( mapping, Mapping ):
			self._srcToTgtDict = mapping.asDict()
		else:
			raise TypeError, "unsupported mapping type %s" % type( mapping )

		self.refresh()
	def getSelectedSrc( self ):
		'''
		returns the name of the src item selected.  None if nothing is selected
		'''
		try:
			return self.UI_srcs.getSelectedItems()[ 0 ]
		except IndexError: return None
	def getSelectedTgts( self ):
		return self.UI_tgts.getSelectedItems()
	def mapSrcItem( self, src ):
		self._srcToTgtDict[ src ] = names.matchNames( [ src ], self.tgts, self.STRIP_NAMESPACES, self.PARITY_MATCH, self.UNIQUE_MATCHING, self.MATCH_OPPOSITE_PARITY )
	def mapAllSrcItems( self ):
		for src in self.srcs:
			self.mapSrcItem( src )
	def addSrcItems( self, items ):
		if items:
			self.UI_srcs.appendItems( list( sorted( items ) ) )
			for i in items:
				self.mapSrcItem( i )
	def replaceSrcItems( self, items ):
		self.UI_tgts.clear()
		self.addSrcItems( items )
	def addTgtItems( self, items ):
		if items:
			self.UI_tgts.appendItems( items )

			performMapping = bool( self.UI_tgts.getItems() )
			if performMapping:
				self.mapAllSrcItems()
	def clear( self ):
		self._srcToTgtDict = {}
		self.UI_srcs.clear()
		self.UI_tgts.clear()
	def clearSrcs( self ):
		self._srcToTgtDict = {}
		self.UI_srcs.clear()
	def clearTgts( self ):
		self._srcToTgtDict = {}
		self.UI_tgts.clear()
	def refresh( self ):
		theSrcs = []
		theTgts = []
		for src in sorted( self._srcToTgtDict.keys() ):
			theSrcs.append( src )
			theTgts += self._srcToTgtDict[ src ]

		theSrcs = removeDupes( theSrcs )
		theTgts = removeDupes( theTgts )

		self.UI_srcs.setItems( theSrcs )
		self.UI_tgts.setItems( theTgts )
	def saveMappingToFile( self, filepath ):
		filepath = Path( filepath ).setExtension( EXT )
		filedata = self.getMapping()
		filepath.pickle( filedata )
	def saveMappingPreset( self, presetName ):
		filepath = presets.Preset( presets.LOCAL, TOOL_NAME, presetName, EXT )
		self.saveMappingToFile( filepath.path() )
	def loadMappingFile( self, filepath ):
		mapping = Path( filepath ).unpickle()
		mapping = Mapping.FromDict( mapping )
		if self.ALLOW_MULTI_SELECTION:
			self._srcToTgtDict = mapping.asDict()
		else:
			self._srcToTgtDict = mapping.asFlatDict()

		self.refresh()
	def loadMappingPreset( self, presetName ):
		filepath = presets.findPreset( presetName, TOOL_NAME, EXT )
		self.loadMappingFile( filepath )

	### MENU BUILDERS ###
	def build_srcMenu( self, *a ):
		cmd.setParent( a[ 0 ], menu=True )
		cmd.menu( a[ 0 ], e=True, dai=True )

		cmd.menuItem( l='Add Selected Objects', c=self.on_addSrc )
		cmd.menuItem( l='Replace With Selected Objects', c=self.on_replaceSrc )
		cmd.menuItem( d=True )
		cmd.menuItem( l='Remove Highlighted Item', c=self.on_removeSrcItem )
		cmd.menuItem( d=True )
		cmd.menuItem( l='Select All Objects', c=self.on_selectAllSrc )
		cmd.menuItem( d=True )
		cmd.menuItem( l='Save Mapping...', c=self.on_saveMapping )
		cmd.menuItem( l='Load Mapping...', sm=True )
		pm = presets.PresetManager( TOOL_NAME, EXT )
		presetDict = pm.listAllPresets( True )

		for loc in presets.LOCAL, presets.GLOBAL:
			for f in presetDict[ loc ]:
				cmd.menuItem( l=f.name(), c=Callback( self.loadMappingFile, f.path() ) )

		cmd.menuItem( d=True )
		cmd.menuItem( l='Manage Mappings...', c=lambda *x: presetsUI.load( TOOL_NAME, presets.LOCAL, EXT ) )

		cmd.setParent( '..', menu=True )
		cmd.menuItem( d=True )
		cmd.menuItem( l='Swap Mapping', c=self.on_swap )
	def build_tgtMenu( self, *a ):
		cmd.setParent( a[ 0 ], menu=True )
		cmd.menu( a[ 0 ], e=True, dai=True )

		cmd.menuItem( l='Add Selected Objects', c=self.on_addTgt )
		cmd.menuItem( l='Replace With Selected Objects', c=self.on_replaceTgt )
		cmd.menuItem( d=True )
		cmd.menuItem( l='Select All Objects', c=self.on_selectAllTgt )
		cmd.menuItem( l='Select Highlighted Objects', c=self.on_selectTgt )
		cmd.menuItem( d=True )
		cmd.menuItem( l='Remove Highlighted Items', c=self.on_removeTgtItem )
		cmd.menuItem( d=True)
		cmd.menuItem( l='Swap Mapping', c=self.on_swap )

	### EVENT CALLBACKS ###
	def on_selectAllSrc( self, *a ):
		cmd.select( cl=True )
		for s in self.UI_srcs.getItems():
			s = str( s )
			if cmd.objExists( s ):
				cmd.select( s, add=True )
	def on_selectAllTgt( self, *a ):
		cmd.select( cl=True )
		for t in self.UI_tgts.getItems():
			t = str( t )
			if cmd.objExists( t ):
				cmd.select( t, add=True )
	def on_selectItemSrc( self, *a ):
		self.UI_tgts.clearSelection()
		src = self.getSelectedSrc()
		if src:
			try: tgts = self._srcToTgtDict[ src ]
			except KeyError:
				return

			for t in tgts:
				if t: self.UI_tgts.selectByValue( t )
	def on_addSrc( self, *a ):
		self.addSrcItems( cmd.ls( sl=True ) )
	def on_replaceSrc( self, *a ):
		self._srcToTgtDict = {}
		self.UI_srcs.clear()
		self.on_addSrc()
	def on_removeSrcItem( self, *a ):
		sel = self.getSelectedSrc()
		try:
			self._srcToTgtDict.pop( sel )
		except KeyError: pass

		try:
			self.UI_srcs.removeByValue( sel )
		except IndexError: pass
	def on_selectSrc( self, *a ):
		src = self.getSelectedSrc()
		if src:
			#if the object doesnt' exist in teh scene - try to find it
			src = findItem( src )
			if src is not None:
				cmd.select( src )
	def on_src_up( self, *a ):
		self.UI_srcs.moveSelectedItemsUp()
	def on_src_dn( self, *a ):
		self.UI_srcs.moveSelectedItemsDown()
	def on_selectItemTgt( self, *a ):
		src = self.getSelectedSrc()
		if src:
			self._srcToTgtDict[ src ] = self.UI_tgts.getSelectedItems()
		else:
			self.UI_tgts.clearSelection()
	def on_delete( self, *a ):
		src = self.getSelectedSrc()
		if src:
			del( self._srcToTgtDict[ src ] )
			self.on_selectItemSrc()
	def on_addTgt( self, *a ):
		self.addTgtItems( cmd.ls( sl=True ) )
	def on_replaceTgt( self, *a ):
		self._srcToTgtDict = {}
		self.UI_tgts.clear()
		self.on_addTgt()
		self.mapAllSrcItems()
	def on_removeTgtItem( self, *a ):
		selTgts = self.getSelectedTgts()
		for aSrc, tgts in self._srcToTgtDict.iteritems():
			newTgts = [ tgt for tgt in tgts if tgt not in selTgts ]
			self._srcToTgtDict[ aSrc ] = newTgts

		idxs = self.UI_tgts.getSelectedIdxs()
		for idx in reversed( sorted( idxs ) ):
			self.UI_tgts.removeByIdx( idx )
	def on_selectTgt( self, *a ):
		tgts = self.getSelectedTgts()
		if tgts:
			existingTgts = []
			for t in tgts:
				t = findItem( t )
				if t is not None:
					existingTgts.append( t )

			if existingTgts:
				cmd.select( existingTgts )
	def on_tgt_up( self, *a ):
		self.UI_tgts.moveSelectedItemsUp()
	def on_tgt_dn( self, *a ):
		self.UI_tgts.moveSelectedItemsDown()
	def on_swap( self, *a ):
		curMapping = Mapping.FromDict( self._srcToTgtDict )
		curMapping.swap()

		if self.ALLOW_MULTI_SELECTION:
			self._srcToTgtDict = curMapping.asDict()
		else:
			self._srcToTgtDict = curMapping.asFlatDict()

		self.refresh()
	def on_saveMapping( self, *a ):
		ret = cmd.promptDialog( m='Enter a name for the mapping', t='Enter Name', b=('Ok', 'Cancel'), db='Ok' )
		if ret == 'Ok':
			self.saveMappingPreset( cmd.promptDialog( q=True, tx=True ) )
	def on_loadMapping( self, *a ):
		previous = presets.getPresetDirs( presets.LOCAL, TOOL_NAME )[ 0 ]
		if self._previousMappingFile is not None:
			previous = self._previousDir

		filename = cmd.fileDialog( directoryMask=( "%s/*.%s" % (previous, EXT) ) )
		filepath = Path( filename )

		self._previousMappingFile = filepath.up()
		self.loadMappingFile( filepath )


class MappingEditor(BaseMelWindow):
	'''
	'''
	WINDOW_NAME = 'mappingEditorUI'
	WINDOW_TITLE = 'Mapping Editor'

	DEFAULT_SIZE = 400, 600

	def __new__( cls, *a, **kw ):
		return BaseMelWindow.__new__( cls )
	def __init__( self, srcItems=None, tgtItems=None ):
		BaseMelWindow.__init__( self )
		self.editor = MappingLayout( self, srcItems, tgtItems )
		self.show()
	def getMapping( self ):
		return self.editor.getMapping()


#end
