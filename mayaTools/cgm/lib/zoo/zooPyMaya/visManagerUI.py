
from zooPy.misc import Callback

import maya.cmds as cmd

import skinCluster
import visManager
import baseMelUI
import presetsUI
import melUtils

mel = melUtils.mel
melecho = melUtils.melecho
name = __name__
ui = None


class VisManagerUI(baseMelUI.BaseMelWindow):
	WINDOW_NAME = "visManagerUI"
	WINDOW_TITLE = 'vis set manager'

	DEFAULT_SIZE = 254, 375
	SPACER = "    "
	EXPANDED = "[-] "
	COLLAPSED = "[+]"
	def __init__( self ):
		baseMelUI.BaseMelWindow.__init__( self )

		mel.zooVisManUtils()
		mel.zooVisInitialSetup()

		self.setSceneChangeCB( self.populate )
		self.UI_form = cmd.formLayout(docTag=0)
		self.UI_check_state = cmd.checkBox(v=self.state(), al="left", l="turn ON", cc=self.on_state_change)
		self.UI_button_marks = cmd.button(l="bookmarks")
		self.UI_tsl_sets = cmd.textScrollList(ams=1, dcc=self.on_collapse, nr=18, sc=self.on_select)

		self.POP_marks = cmd.popupMenu(p=self.UI_button_marks, b=1, aob=1, pmc=self.popup_marks)
		self.POP_marks_sh = cmd.popupMenu(p=self.UI_button_marks, sh=1, b=1, aob=1, pmc=self.popup_marks_add)
		self.POP_sets = cmd.popupMenu(p=self.UI_tsl_sets, b=3, pmc=self.popup_sets)

		self.reparentUI = None

		cmd.formLayout(self.UI_form, e=True,
				   af=((self.UI_check_state, "top", 3),
					 (self.UI_check_state, "left", 3),
					 (self.UI_button_marks, "top", 0),
					 (self.UI_button_marks, "right", 0),
					 (self.UI_tsl_sets, "left", 0),
					 (self.UI_tsl_sets, "bottom", 0)),
				   ac=((self.UI_button_marks, "left", 5, self.UI_check_state),
					 (self.UI_tsl_sets, "top", 0, self.UI_button_marks)),
				   ap=((self.UI_tsl_sets, "right", 0, 100)) )

		self.populate()
		self.show()
	def __del__( self ):
		if self.reparentUI is not None:
			if cmd.window(self.reparentUI, ex=True):
				cmd.deleteUI(self.reparentUI)
	def populate( self ):
		sets = mel.zooVisManListHeirarchically()

		cmd.textScrollList(self.UI_tsl_sets, e=True, ra=True)
		while True:
			try:
				vset = sets.pop(0)
				name = self.EXPANDED
				childSets = mel.zooSetRelatives(vset, 0, 0, 1)
				depth = len(mel.zooSetRelatives(vset, 0, 1, 1))  #count the number of parents to see how deep in the tree the set is

				if not childSets: name = self.SPACER
				if cmd.objExists("%s.isoCollapse" % vset):
					#if this set is collapsed we need to remove all its children from the list and change the name prefix
					name = self.COLLAPSED
					for toRemove in childSets: sets.remove(toRemove)

				name += self.SPACER * depth
				name += vset
				cmd.textScrollList(self.UI_tsl_sets, e=True, a=name)
			except IndexError: break

		self.updateSelection()
	def updateSelection( self ):
		'''
		updates the tsl to reflect the sets that are currently active if any
		'''
		cmd.textScrollList(self.UI_tsl_sets, e=True, da=True)

		displayNames = cmd.textScrollList(self.UI_tsl_sets, q=True, ai=True)
		activeISOs = mel.zooVisManGetActiveSets()
		toSelect = []

		for iso in activeISOs:
			for name in displayNames:
				if name.rfind(iso) != -1:
					toSelect.append(name)
					break

		for item in toSelect:
			cmd.textScrollList(self.UI_tsl_sets, e=True, si=item)
	def selection( self ):
		selection = cmd.textScrollList(self.UI_tsl_sets, q=True, si=True)
		if not selection: return []

		clean = []
		for s in selection:
			idxName = s.rfind(' ')
			if idxName == -1: clean.append(s)
			else: clean.append(s[idxName+1:])

		return clean
	def state( self ):
		return mel.zooVisManGetState()
	def on_state_change( self, *args ):
		mel.zooVisManSetVisState( cmd.checkBox(self.UI_check_state, q=True, v=True) )
	def on_select( self, *args ):
		mel.zooVisManSetActiveSets( self.selection() )
	def on_collapse( self, *args ):
		selSets = self.selection()
		state = not mel.zooVisManGetCollapseState(selSets[0])
		for s in selSets:
			mel.zooVisManSetCollapseState(s, state)

		self.populate()
	def on_reparent( self, *args ):
		self.reparentUI = ParentChooserUI( self.selection() )
	def on_new( self, *args ):
		parent = ''
		try: parent = self.selection()[0]
		except IndexError: pass

		ret = cmd.promptDialog(t="new isoSet", message="set name", b=("OK", "Cancel"), db="OK")
		text = cmd.promptDialog(q=True, tx=True)

		if ret != "OK": return
		if text == "": return

		newSet = mel.zooVisManCreateSet(parent, text, cmd.ls(sl=True))
		cmd.select(cl=True)

		self.populate()
	def on_delete( self, *args ):
		for vset in self.selection():
			if cmd.objExists(vset):
				mel.zooVisManDeleteSet(vset)

		self.populate()
	def on_add( self, *args ):
		mel.zooVisManAddToSet(self.selection(), cmd.ls(sl=True))
	def on_remove( self, *args ):
		mel.zooVisManRemFromSet(self.selection(), cmd.ls(sl=True))
	def on_set_select( self, *args ):
		mel.zooVisManSelectFrom(self.selection())
	def on_joint_affected_faces( self, recursive=False ):
		'''
		'''
		faces = []
		selJoints = cmd.ls(sl=True, type='joint')
		for j in selJoints:
			faces += skinCluster.jointFacesForMaya(j, 0.1)

		if recursive:
			for j in cmd.listRelatives(selJoints, ad=True, type='joint'):
				faces += skinCluster.jointFacesForMaya(j, 0.1)

		mel.zooVisManAddToSet(self.selection(), faces)
	def on_create_bookmark( self, *args ):
		ans = cmd.promptDialog(m='', t='', b=('OK', 'Cancel'), db='OK')
		if ans != 'OK': return
		markName = cmd.promptDialog(q=True, tx=True)
		mel.zooVisManCreateBookmark(markName, self.selection())
	def on_activate_mark( self, markName, add ):
		mel.zooVisManActivateBookmark(markName, add)
		self.updateSelection()
	def on_eazel( self, *args ):
		curState = cmd.optionVar(q='zooVisManEazel') if cmd.optionVar(ex='zooVisManEazel') else True
		cmd.optionVar(iv=('zooVisManEazel', not curState))
	def popup_marks( self, parent, *args, **kwargs ):
		cmd.setParent(parent, m=True)
		cmd.menu(parent, e=True, dai=True)

		add = kwargs.get('add', False )
		marks = mel.zooVisManListBookmarks()
		for mark in marks:
			cmd.menuItem(l=mark, c=Callback(self.on_activate_mark, mark, add))

		cmd.menuItem(d=1)
		cmd.menuItem(l='create bookmark', c=self.on_create_bookmark)
	def popup_marks_add( self, parent, *args ):
		self.popup_marks(parent, add=True)
	def popup_sets( self, parent, *args ):
		cmd.setParent(parent, m=True)
		cmd.menu(parent, e=True, dai=True)

		items = self.selection()
		addEazel = cmd.optionVar(q='zooVisManEazel') if cmd.optionVar(ex='zooVisManEazel') else True
		enable = bool(items)

		cmd.menuItem(en=enable, l="+ selection to vis set", c=self.on_add)
		cmd.menuItem(en=enable, l="- selection from vis set", c=self.on_remove)
		cmd.menuItem(en=enable, l="select items in vis set", c=self.on_set_select)
		cmd.menuItem(en=enable, l="parent to...", c=self.on_reparent)

		cmd.menuItem(d=True)
		cmd.menuItem(l="new vis set", c=self.on_new)
		cmd.menuItem(en=enable, l="remove vis set", c=self.on_delete)
		cmd.menuItem(d=True)

		cmd.menuItem(l="always show eazel", cb=addEazel, c=self.on_eazel)
		cmd.menuItem(d=True)

		cmd.menuItem(l="merge all sets (nasty hack)", c="mel.hackyMergeSets()")
		cmd.menuItem(l="add faces affected by joint", c=self.on_joint_affected_faces)
		cmd.menuItem(l="add faces affected by joint heirarchy", c=self.on_joint_affected_faces)
		cmd.menuItem(d=True)

		#build the preset list...
		visPresets = presetsUI.listAllPresets( visManager.TOOL_NAME, visManager.EXTENSION, True )
		cmd.menuItem(l="build sets from preset", sm=True)
		for locale, pList in visPresets.iteritems():
			for p in pList:
				cmd.menuItem(l=p.name(), c=Callback(self.import_preset, p.name(), locale, True, True))
		cmd.setParent('..', m=True)

		cmd.menuItem(l="import preset volumes", sm=True)
		for locale, pList in visPresets.iteritems():
			for p in pList:
				cmd.menuItem(l=p.name(), c=Callback(self.import_preset, p.name(), locale, False, False))
		cmd.setParent('..', m=True)
		selected = cmd.ls(sl=True)
		cmd.menuItem(en=len(selected)==1, l="export volume preset", c=self.export_preset)
		cmd.menuItem(l="manage presets", c=lambda *x: presetsUI.load(visManager.TOOL_NAME, visManager.DEFAULT_LOCALE, visManager.EXTENSION))
		cmd.menuItem(d=True)

		cmd.menuItem(l='create sphere volume', c=lambda *x: assets.createExportVolume(assets.ExportManager.kVOLUME_SPHERE))
		cmd.menuItem(l='create cube volume', c=lambda *x: assets.createExportVolume(assets.ExportManager.kVOLUME_CUBE))
	def import_preset( self, presetName, locale, createSets, deleteVolumes ):
		visManager.importPreset(presetName, locale, createSets, deleteVolumes)
		self.populate()
	def export_preset( self, *args ):
		BUTTONS = OK, CANCEL = 'Ok', 'Cancel'
		ans = cmd.promptDialog( t="volume preset name", m="enter a name for the volume preset", b=BUTTONS, db=OK )
		if ans != OK:
			return

		name = cmd.promptDialog( q=True, tx=True )
		if not name:
			return

		selected = cmd.ls( sl=True )
		visManager.exportPreset( name, selected[0] )

		#now delete the vis volumes
		cmd.delete( selected[0] )


class ParentChooserUI(baseMelUI.BaseMelWindow):
	WINDOW_NAME = "visManagerParentChooser"
	WINDOW_TITLE = "vis set manager"
	NO_PARENT = '--no parent--'

	DEFAULT_SIZE = 180, 200

	def __init__( self, setsToReparent ):
		baseMelUI.BaseMelWindow.__init__( self )

		allSets = set( mel.zooVisManListHeirarchically() )
		allSets.difference_update( set(setsToReparent) )

		self.UI_form = cmd.formLayout()
		self.UI_tsl = cmd.textScrollList(ams=0, nr=18)
		self.UI_button_parent = cmd.button(l="parent")

		cmd.textScrollList(self.UI_tsl, e=True, dcc='%s.ui.reparentUI.on_done()' % name)
		cmd.button(self.UI_button_parent, e=True, c='%s.ui.reparentUI.on_done()' % name)

		#
		cmd.textScrollList(self.UI_tsl, e=True, a=self.NO_PARENT)
		for vset in allSets:
			cmd.textScrollList(self.UI_tsl, e=True, a=vset)

		cmd.formLayout(self.UI_form, e=True,
				   af=((self.UI_tsl, "top", 0),
					   (self.UI_tsl, "left", 0),
					   (self.UI_tsl, "right", 0),
					   (self.UI_button_parent, "left", 0),
					   (self.UI_button_parent, "right", 0),
					   (self.UI_button_parent, "bottom", 0)),
				   ac=((self.UI_tsl, "bottom", 0, self.UI_button_parent)) )

		#select the no parent option
		cmd.textScrollList(self.UI_tsl, e=True, si=self.NO_PARENT)
		self.show()
	def selection( self ):
		sel = cmd.textScrollList(self.UI_tsl, q=True, si=True)
		try: return sel[0]
		except IndexError: return self.NO_PARENT
	def on_done( self ):
		sel = self.selection()
		if sel == self.NO_PARENT: sel = ''

		mel.zooVisManSetParent(ui.selection(), sel)
		ui.populate()
		cmd.deleteUI(self.WINDOW_NAME)


def load():
	global ui
	ui = VisManagerUI()


#end
