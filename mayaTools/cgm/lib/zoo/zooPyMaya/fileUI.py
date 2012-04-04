
from baseMelUI import *

from zooPy.path import Path
from zooPy.misc import Callback

import presetsUI

from melUtils import printWarningStr, openFile, importFile, referenceFile

PRESET_ID_STR = 'zoo'
PRESET_EXTENSION = 'filter'


class FileScrollList(MelObjectScrollList):
	def __init__( self, parent, *a, **kw ):
		self._rootDir = None
		self._displayRelativeToRoot = True
		MelObjectScrollList.__init__( self, parent, *a, **kw )
	def itemAsStr( self, item ):
		if self._displayRelativeToRoot and self._rootDir:
			return str( Path( item ) - self._rootDir )

		return str( item )
	def getRootDir( self ):
		return self._rootDir
	def setRootDir( self, rootDir ):
		self._rootDir = Path( rootDir )
		self.update()
	def getDisplayRelative( self ):
		return self._displayRelativeToRoot
	def setDisplayRelative( self, state=True ):
		self._displayRelativeToRoot = state
		self.update()


class FileListLayout(MelVSingleStretchLayout):
	ENABLE_IMPORT = True
	ENABLE_REFERENCE = True

	def __new__( cls, parent, *a, **kw ):
		return BaseMelWidget.__new__( cls, parent )
	def __init__( self, parent, directory=None, files=None, recursive=True ):
		self.expand = True
		self.padding = 2

		self._files = []
		self._recursive = recursive

		self._extensionSets = []
		self._extensionsToDisplay = []
		self._ignoreSubstrings = [ 'incrementalSave' ]

		self._enableOpen = True
		self._enableImport = True
		self._enableReference = True

		#this allows clients who subclass this class to set additional filter change callbacks - perhaps
		#for things like saving the filter string in user preferences, or doing additional work...
		self._filterChangeCB = None

		hLayout = MelHSingleStretchLayout( self )
		MelLabel( hLayout, l='Directory' )
		self.UI_dir = MelTextField( hLayout, tx=directory, cc=self.on_dirChange )
		MelButton( hLayout, l='Browse', w=80, c=self.on_browse )
		hLayout.setStretchWidget( self.UI_dir )
		hLayout.layout()

		hLayout = MelHSingleStretchLayout( self )
		MelLabel( hLayout, l='Filter' )
		self.UI_filter = MelTextField( hLayout, cc=self.on_filterChanged )
		if not self._extensionSets:
			for exts in self._extensionSets:
				self.UI_filter = MelOptionMenu( hLayout, l='', cc=self.on_changeExtensionSet )
				self.UI_filter.append( ' '.join( exts ) )

		hLayout.setStretchWidget( self.UI_filter )
		hLayout.layout()

		self.UI_files = FileScrollList( self, ams=True, dcc=self.on_doubleClick, h=75 )

		### ADD POPUPS
		cmd.popupMenu( parent=self.UI_filter, b=3, pmc=self.popup_filterPresets )
		cmd.popupMenu( parent=self.UI_files, b=3, pmc=self.popup_files )

		if files is None:
			self.populateFiles()
		else:
			self.setFiles( files )

		self.setStretchWidget( self.UI_files )
		self.layout()
	def __contains__( self, item ):
		return item in self.UI_files
	def setDir( self, dir, update=True ):
		self.UI_dir.setValue( str( dir ), update )
	def getDir( self ):
		return Path( self.UI_dir.getValue() )
	def getRecursive( self ):
		return self._recursive
	def setRecursive( self, state=True, update=True ):
		self._recursive = state
		if update:
			self.populateFiles()
	def getExtensionsToDisplay( self ):
		return self._extensionsToDisplay[:]
	def setExtensionsToDisplay( self, extensionList, update=True ):
		self._extensionsToDisplay = extensionList[:]
		if update:
			self.populateFiles()
	def getIgnoreSubstrings( self ):
		return self._ignoreSubstrings[:]
	def setIgnoreSubstrings( self, substringList, update=True ):
		self._ignoreSubstrings = substringList[:]
		if update:
			self.populateFiles()
	def populateFiles( self ):
		self.setFiles( list( self.getDir().files( recursive=self.getRecursive() ) ) )
	def getDisplayRelative( self ):
		return self.UI_files.getDisplayRelative()
	def setDisplayRelative( self, state=True ):
		self.UI_files.setDisplayRelative( state )
	def getFilter( self ):
		return self.UI_filter.getValue()
	def setFilter( self, filterStr, update=True ):
		self.UI_filter.setValue( filterStr, update )
	def setFilterChangeCB( self, cb ):
		self._filterChangeCB = cb
	def setSelectionChangeCB( self, cb ):
		self.UI_files.setChangeCB( cb )
	def getSelectedFiles( self ):
		return self.UI_files.getSelectedItems()
	def setSelectedFiles( self, files, executeChangeCB=False ):

		#make sure all files are Path instances
		files = map( Path, files )

		self.UI_files.selectItems( files, executeChangeCB )
	def getFiles( self ):
		'''
		returns the files being listed
		'''
		return self.UI_files.getItems()
	def setFiles( self, files ):
		'''
		sets the file list to the given iterable
		'''
		self.UI_files.clear()
		self.addFiles( files )
	def addFiles( self, files ):
		'''
		adds files to the UI without clearing
		'''
		self._files = []
		for f in files:

			#if the file doesn't have the right extension - bail
			if self._extensionsToDisplay:
				if f.getExtension().lower() not in self._extensionsToDisplay:
					continue

			skip = False
			for invalid in self._ignoreSubstrings:
				if invalid.lower() in str( f ).lower():
					skip = True
					break

			if skip:
				continue

			self._files.append( f )

		self.UI_files.setItems( self._files )

	### MENU BUILDERS ###
	def popup_filterPresets( self, parent, *args ):
		cmd.setParent( parent, m=True )
		cmd.menu( parent, e=True, dai=True )

		hasItems = False
		allFilterPresets = presetsUI.listAllPresets( PRESET_ID_STR, PRESET_EXTENSION )
		for locale, filterPresets in allFilterPresets.iteritems():
			for item in filterPresets:
				itemName = item.name()
				cmd.menuItem( l=itemName, c=Callback( self.setFilter, itemName ) )
				hasItems = True

		if hasItems:
			cmd.menuItem( d=True )

		cmd.menuItem( l='clear', c=Callback( self.setFilter, '' ) )
		if self.getFilter():
			cmd.menuItem( d=True )
			cmd.menuItem( l='save filter preset', c=self.on_filterSave )
			cmd.menuItem( l='manager filter presets', c=self.on_filterManage )
	def popup_files( self, parent, *args ):
		cmd.setParent( parent, m=True )
		cmd.menu( parent, e=True, dai=True )

		files = self.getSelectedFiles()
		if len( files ) == 1:
			if self._enableOpen:
				cmd.menuItem( l='open file', c=lambda *x: self.on_open( files[ 0 ] ) )

			if self._enableImport:
				cmd.menuItem( l='import file', c=lambda *x: self.on_import( files[ 0 ] ) )

			if self._enableReference:
				cmd.menuItem( l='reference file', c=lambda *x: self.on_reference( files[ 0 ] ) )

			cmd.menuItem( d=True )
			presetsUI.addExploreToMenuItems( files[ 0 ] )
		else:
			cmd.menuItem( l="please select a single file" )

		cmd.menuItem( d=True )
		cmd.menuItem( cb=self.getDisplayRelative(), l="Display Relative Paths", c=lambda *x: self.setDisplayRelative( not self.getDisplayRelative() ) )
		cmd.menuItem( cb=self.getRecursive(), l="Recursive Directory Listing", c=lambda *x: self.setRecursive( not self.getRecursive() ) )

	### EVENT CALLBACKS ###
	def on_open( self, theFile ):
		openFile( theFile )
	def on_import( self, theFile ):
		importFile( theFile )
	def on_reference( self, theFile ):
		referenceFile( theFile, 'ref' )
	def on_dirChange( self, theDir=None ):
		if theDir is None:
			theDir = self.getDir()

		theDir = Path( theDir )
		self.UI_files.setRootDir( theDir )

		self.populateFiles()
	def on_browse( self, *args ):
		startDir = cmd.workspace( q=True, rootDirectory=True )
		cmd.workspace( dir=startDir )

		def tempCB( filename, filetype ):
			self.setDir( filename )
			self.on_dirChange( filename )

		cmd.fileBrowserDialog( mode=4, fileCommand=tempCB, an="Choose_Location" )
	def on_filterChanged( self, *args ):
		self.UI_files.setFilter( self.UI_filter.getValue() )
		if self._filterChangeCB:
			try:
				self._filterChangeCB()
			except:
				printWarningStr( "The filter change callback %s failed!" % self._filterChangeCB )
	def on_changeExtensionSet( self, *args ):
		self._extensionsToDisplay = cmd.optionMenu( self.UI_filter, q=True, v=True ).split()
		self.populateFiles()
	def on_doubleClick( self, *args ):
		openFile( self.getSelectedFiles()[ 0 ] )
	def on_filterSave( self, *args ):
		presetName = self.UI_filter.getValue()
		presetsUI.PresetManager( PRESET_ID_STR, PRESET_EXTENSION ).savePreset( presetName, '', presetsUI.LOCAL  )
	def on_filterManage( self, *args ):
		presetsUI.load( PRESET_ID_STR, presetsUI.LOCAL, PRESET_EXTENSION )


class FileUIWindow(BaseMelWindow):
	WINDOW_NAME = 'fileUITestWindow'
	WINDOW_TITLE = 'File UI Test Window'

	DEFAULT_MENU = None
	DEFAULT_SIZE = 350, 400

	def __init__( self ):
		editor = FileListLayout( self )
		editor.setDir( cmd.workspace( q=True, rootDirectory=True ) )
		self.show()


#end