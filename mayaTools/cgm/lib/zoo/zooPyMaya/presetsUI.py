
from zooPy import presets
from zooPy.path import Path

from baseMelUI import *

import maya.cmds as cmd


def addExploreToMenuItems( filepath ):
	if filepath is None:
		return

	filepath = Path( filepath )
	if not filepath.exists():
		filepath = filepath.getClosestExisting()

	if filepath is None:
		return

	cmd.menuItem(l="Explore to location...", c=lambda x: mel.zooExploreTo( filepath ), ann='open an explorer window to the location of this file/directory')

	cmd.menuItem(l="CMD prompt to location...", c=lambda x: mel.zooCmdTo( filepath ), ann='open a command prompt to the location of this directory')


class PresetOptionMenu(MelOptionMenu):
	def __init__( self, parent, tool, extension, *a, **kw ):
		MelOptionMenu.__init__( self, parent, *a, **kw )

		self.setChangeCB( self.on_change )

		self._manager = presets.PresetManager( tool, extension )
		self._presets = {}
		self.update()
	def update( self ):
		self.clear()
		for locale, presets in self._manager.listAllPresets( True ).iteritems():
			for preset in presets:
				self.append( preset.name() )
				self._presets[ preset.name() ] = preset
	def getValue( self ):
		valueStr = MelOptionMenu.getValue( self )
		return self._presets.get( valueStr, None )

	### EVENT HANDLERS ###
	def on_change( self, *a ):
		self.sendEvent( 'presetChanged', self.getValue() )


class PresetLayout(MelFormLayout):
	ALLOW_MULTI_SELECTION = True

	def __new__( cls, parent, *a, **kw ):
		return MelFormLayout.__new__( cls, parent )
	def __init__( self, parent, tool, locale=presets.LOCAL, ext=presets.DEFAULT_XTN ):
		MelFormLayout.__init__( self, parent )

		self.tool = tool
		self.locale = locale
		self.ext = ext
		self.presetManager = presets.PresetManager(tool, ext)

		self.populate()
	def populate( self ):
		children = self( q=True, ca=True )
		if children is not None:
			for c in children:
				cmd.deleteUI( c )

		other = self.other()
		otherLbl = "<-- %s" % other

		cmd.setParent( self )
		self.UI_lbl_title = cmd.text(l='Managing "%s" presets' % self.ext)
		self.UI_lbl_presets = cmd.text(l="%s presets" % self.locale)
		self.UI_button_swap = cmd.button(h=18, l="view %s presets" % other, c=self.swap)
		self.UI_tsl_presets = cmd.textScrollList(allowMultiSelection=self.ALLOW_MULTI_SELECTION, sc=self.updateButtonStatus)
		self.UI_button_1 = cmd.button(l="move to %s" % other, c=self.move)
		self.UI_button_2 = cmd.button(l="copy to %s" % other, c=self.copy)
		self.UI_button_3 = cmd.button(l="rename", c=self.rename)
		self.UI_button_4 = cmd.button(l="delete", c=self.delete)

		self.POP_filemenu = cmd.popupMenu(b=3, p=self.UI_tsl_presets, pmc=self.popup_filemenu)

		self( e=True,
			  af=((self.UI_lbl_title, "top", 5),
				  (self.UI_lbl_title, "left", 5),

				  (self.UI_lbl_presets, "left", 10),

				  (self.UI_button_swap, "right", 5),
				  (self.UI_tsl_presets, "left", 5),
				  (self.UI_tsl_presets, "right", 5),
				  (self.UI_button_1, "left", 5),
				  (self.UI_button_2, "right", 5),
				  (self.UI_button_3, "left", 5),
				  (self.UI_button_3, "bottom", 5),
				  (self.UI_button_4, "right", 5),
				  (self.UI_button_4, "bottom", 5)),
			  ac=((self.UI_lbl_presets, "top", 10, self.UI_lbl_title),
				  (self.UI_button_swap, "top", 7, self.UI_lbl_title),
				  (self.UI_button_1, "bottom", 0, self.UI_button_3),
				  (self.UI_button_swap, "left", 10, self.UI_lbl_presets),
				  (self.UI_tsl_presets, "top", 10, self.UI_lbl_presets),
				  (self.UI_tsl_presets, "bottom", 5, self.UI_button_1),
				  (self.UI_button_2, "bottom", 0, self.UI_button_4)),
			  ap=((self.UI_button_1, "right", 0, 50),
				  (self.UI_button_2, "left", 0, 50),
				  (self.UI_button_3, "right", 0, 50),
				  (self.UI_button_4, "left", 0, 50)) )

		self.updateList()
	def other( self ):
		'''
		returns the "other" locale
		'''
		return presets.LOCAL if self.locale == presets.GLOBAL else presets.GLOBAL
	def updateList( self ):
		'''
		refreshes the preset list
		'''
		presets = self.presetManager.listPresets(self.locale)
		cmd.textScrollList(self.UI_tsl_presets, e=True, ra=True)
		self.presets = presets
		for p in presets:
			cmd.textScrollList(self.UI_tsl_presets, e=True, a=p[-1])

		self.updateButtonStatus()
	def updateButtonStatus( self, *args ):
		selected = self.selected()
		numSelected = len(selected)

		if numSelected == 0:
			cmd.button(self.UI_button_1, e=1, en=0)
			cmd.button(self.UI_button_2, e=1, en=0)
			cmd.button(self.UI_button_3, e=1, en=0)
			cmd.button(self.UI_button_4, e=1, en=0)
		elif numSelected == 1:
			cmd.button(self.UI_button_1, e=1, en=1)
			cmd.button(self.UI_button_2, e=1, en=1)
			cmd.button(self.UI_button_3, e=1, en=1)
			cmd.button(self.UI_button_4, e=1, en=1)
		else:
			cmd.button(self.UI_button_1, e=1, en=1)
			cmd.button(self.UI_button_2, e=1, en=1)
			cmd.button(self.UI_button_3, e=1, en=0)
			cmd.button(self.UI_button_4, e=1, en=1)
	def selected( self ):
		'''
		returns the selected presets as Path instances - if nothing is selected, an empty list is returned
		'''
		try:
			selectedIdxs = [idx-1 for idx in cmd.textScrollList(self.UI_tsl_presets, q=True, sii=True)]
			selected = [self.presets[n] for n in selectedIdxs]
			return selected
		except TypeError: return []
	def getSelectedPresetNames( self ):
		selected = cmd.textScrollList( self.UI_tsl_presets, q=True, si=True ) or []
		return [ Path( s ).name() for s in selected ]
	def getSelectedPresetName( self ):
		try: return self.getSelectedPresetNames()[ 0 ]
		except IndexError:
			return None
	def copy( self, *args ):
		files = []
		for s in self.selected():
			files.append( s.copy() )

		self.sendEvent( 'presetsCopied', files )
	def delete( self, *args ):
		files = self.selected()
		for s in files:
			s.delete()

		self.updateList()
		self.sendEvent( 'presetsDeleted', files )
	def move( self, *args ):
		files = []
		movedFiles = []
		for s in self.selected():
			ff = s.move()
			movedFiles.append( ff )

		self.updateList()
		self.sendEvent( 'presetsMoved', files )
	def rename( self, *args ):
		'''
		performs the prompting and renaming of presets
		'''
		selected = self.selected()[0]

		BUTTONS = OK, CANCEL = 'Ok', 'Cancel'
		ans = cmd.promptDialog( m='new name', tx=selected.name(), b=BUTTONS, db=OK )
		if ans != OK:
			return

		newName = cmd.promptDialog( q=True, tx=True )
		if not newName:
			return

		if not newName.endswith('.'+ self.ext):
			newName += '.'+ self.ext

		renamedPreset = selected.rename( newName )
		self.updateList()
		self.sendEvent( 'presetRenamed', selected, renamedPreset )
	def swap( self, *args ):
		'''
		performs the swapping from the local to global locale
		'''
		self.locale = self.otherLocale()
		self.populate()
	def syncall( self, *a ):
		'''
		syncs to ALL global presets for the current tool
		'''
		pass
	def on_notepad( self, filepath ):
		filepath = Path( filepath )
		subprocess.Popen( 'notepad "%s"' % filepath.asNative(), cwd=filepath.up() )
	def popup_filemenu( self, parent, *args ):
		cmd.menu(parent, e=True, dai=True)
		cmd.setParent(parent, m=True)

		other = self.otherLocale()
		items = self.selected()
		numItems = len(items)
		if numItems:
			cmd.menuItem(l='copy to %s' % other, c=self.copy)
			cmd.menuItem(l='move to %s' % other, c=self.move)

			if len(items) == 1:
				filepath = items[0].resolve()
				cmd.menuItem(d=True)
				cmd.menuItem(l='open in notepad', c=lambda *x: self.on_notepad( filepath ))

				cmd.menuItem(d=True)
				addExploreToMenuItems(filepath)

			cmd.menuItem(d=True)
			cmd.menuItem(l='delete', c=self.delete)

		#if no files are selected, prompt the user to select files
		if numItems == 0:
			cmd.menuItem(en=False, l='select a preset file')

PresetForm = PresetLayout


class PresetWindow(BaseMelWindow):
	WINDOW_NAME = 'presetWindow'
	WINDOW_TITLE = 'Preset Manager'

	DEFAULT_SIZE = 275, 325
	DEFAULT_MENU = None

	FORCE_DEFAULT_SIZE = True

	def __new__( cls, *a, **kw ):
		return BaseMelWindow.__new__( cls )
	def __init__( self, tool, locale=presets.LOCAL, ext=presets.DEFAULT_XTN ):
		BaseMelWindow.__init__( self )

		self.editor = PresetForm( self, tool, locale, ext )

		self.show()
	def presetsCopied( self, presets ):
		pass
	def presetsDeleted( self, presets ):
		pass
	def presetsMoved( self, presets ):
		pass
	def presetRenamed( self, preset, renamedPreset ):
		pass


#end
