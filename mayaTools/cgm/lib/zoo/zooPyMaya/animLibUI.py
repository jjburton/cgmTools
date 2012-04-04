
import maya.cmds as cmd
from zooPy import presets

from baseMelUI import *

import animLib
import animClip
import mappingUtils
import xferAnimUI


def getSelectedChannelBoxAttrNames():
	attrNames = cmd.channelBox( 'mainChannelBox', q=True, sma=True ) or []
	attrNames += cmd.channelBox( 'mainChannelBox', q=True, ssa=True ) or []
	attrNames += cmd.channelBox( 'mainChannelBox', q=True, sha=True ) or []

	return attrNames


class AnimClipChannelEditorLayout(MelVSingleStretchLayout):
	def __init__( self, parent, clipPreset ):
		MelVSingleStretchLayout.__init__( self, parent )

		self.clipPreset = clipPreset
		self.clipContents = clipPreset.path().unpickle()
		self._dirty = False

		#build the UI
		hLayout = MelHLayout( self )
		vLayout = MelVSingleStretchLayout( hLayout )
		self.UI_objList = UI_objList = MelObjectScrollList( vLayout )
		UI_removeObjs = MelButton( vLayout, l='Remove Selected Objects' )
		vLayout.setStretchWidget( UI_objList )
		vLayout.layout()

		vLayout = MelVSingleStretchLayout( hLayout )
		self.UI_attrList = UI_attrList = MelObjectScrollList( vLayout )
		UI_removeAttrs = MelButton( vLayout, l='Remove Selected Attributes' )
		vLayout.setStretchWidget( UI_attrList )
		vLayout.layout()

		UI_objList.allowMultiSelect( True )
		UI_attrList.allowMultiSelect( True )


		hLayout.expand = True
		hLayout.layout()

		self.setStretchWidget( hLayout )

		#populate the object list
		for obj in clipPreset.nodes():
			UI_objList.append( obj )


		#build callbacks for the lists
		def objSelected():
			objs = UI_objList.getSelectedItems()
			if not objs:
				return

			UI_attrList.clear()
			attrsAlreadyAdded = set()
			for obj in objs:
				attrDict = clipDict[ obj ]
				for attrName, attrValue in attrDict.iteritems():
					if attrName in attrsAlreadyAdded:
						continue

					self.UI_attrList.append( attrName )
					attrsAlreadyAdded.add( attrName )

				if attrDict:
					self.UI_attrList.selectByIdx( 0, True )

		UI_objList.setChangeCB( objSelected )
		def removeObjs( *a ):
			objs = UI_objList.getSelectedItems()
			if not objs:
				return

			performUpdate = False
			for obj in objs:
				if obj in clipDict:
					self._dirty = True
					performUpdate = True
					clipDict.pop( obj )

			if performUpdate:
				UI_objList.clear()
				UI_attrList.clear()
				for obj in clipDict:
					UI_objList.append( obj )

				if clipDict:
					UI_objList.selectByIdx( 0, True )

		UI_removeObjs.setChangeCB( removeObjs )
		def removeAttrs( *a ):
			objs = UI_objList.getSelectedItems()
			if not objs:
				return

			attrs = UI_attrList.getSelectedItems()
			if not attrs:
				return

			performUpdate = False
			for obj in objs:
				subDict = clipDict[ obj ]
				for attr in attrs:
					self._dirty = True
					performUpdate = True
					if attr in subDict:
						subDict.pop( attr )

			if performUpdate:
				objSelected()

		UI_removeAttrs.setChangeCB( removeAttrs )


		#set the initial state
		if len( self.UI_objList ):
			UI_objList.selectByIdx( 0, True )


		#build the save/cancel UI...
		hLayout = MelHLayout( self )
		MelButton( hLayout, l='Save', c=self.on_save )
		MelButton( hLayout, l='Cancel', c=lambda *a: self.sendEvent( 'delete' ) )
		hLayout.layout()

		self.setDeletionCB( self.on_cancel )
		self.layout()
	def askToSave( self ):
		#check to see if changes were made, and if so, ask if the user wants to save them...
		if self._dirty:
			BUTTONS = YES, NO, CANCEL = 'Yes', 'No', 'Cancel'
			ret = cmd.confirmDialog( t='Overwrite Clip?',
			                         m='Are you sure you want to overwrite the %s clip called %s?' % (self.clipPreset.EXT,
			                                                                                          self.clipPreset.name()),
			                         b=BUTTONS, db=CANCEL )
			if ret == CANCEL:
				return False
			elif ret == YES:
				self.clipPreset.pickle( self.presetDict )
				self._dirty = False

		return True

	### EVENT HANDLERS ###
	def on_cancel( self, *a ):
		self.askToSave()
	def on_save( self, *a ):
		if self.askToSave():
			self.sendEvent( 'delete' )


class AnimClipChannelEditorWindow(BaseMelWindow):
	WINDOW_NAME = 'animClipEditor'
	WINDOW_TITLE = 'Anim Clip Editor'

	DEFAULT_MENU = None
	DEFAULT_SIZE = 400, 250

	FORCE_DEFAULT_SIZE = False

	def __init__( self, clipPreset ):
		BaseMelWindow.__init__( self )
		AnimClipChannelEditorLayout( self, clipPreset )
		self.show()


class ClipWidget(MelIconRadioButton):
	def __new__( cls, parent, collection, clipPreset ):
		return MelIconRadioButton.__new__( cls, parent,
		                                   collection=collection,
		                                   l=clipPreset.niceName(),
		                                   w=animLib.ICON_SIZE,
		                                   h=animLib.ICON_SIZE + 25,
		                                   style='iconAndTextVertical',
		                                   ann='%s: %s %s clip' % (clipPreset.niceName(), clipPreset.locale(), clipPreset.EXT) )
	def __init__( self, parent, collection, clipPreset ):
		assert isinstance( clipPreset, animLib.BaseClipPreset )
		self.clipPreset = clipPreset
		self.setImage( clipPreset.icon() )
		self.setChangeCB( self.onSelect )

		if clipPreset.locale() == presets.GLOBAL:
			self.setColour( (1,0.05,0) )

		MelPopupMenu( self, pmc=self.buildMenu )
	def buildMenu( self, parent, *args ):
		cmd.setParent( parent, m=True )
		cmd.menu( parent, e=True, dai=True )

		cmd.menuItem( l=self.clipPreset.name(), boldFont=True, c=self.onSelect )
		cmd.menuItem( d=True )

		cmd.menuItem( l='over-write clip', c=self.onOverwrite )
		cmd.menuItem( l='re-generate icon', c=self.onIcon )
		cmd.menuItem( d=True )
		cmd.menuItem( l='delete', c=lambda *x: self.delete() )
		cmd.menuItem( l='rename', c=self.onRename )
		cmd.menuItem( d=True )

		#cmd.menuItem( l='select items in clip', c=self.onSelectClipItems )
		cmd.menuItem( l='map names manually', c=self.onMapping )
		#cmd.menuItem( d=True )
		#cmd.menuItem( l='edit clip', c=self.onEdit )
		if self.clipPreset.locale() == presets.LOCAL:
			cmd.menuItem( d=True )
			cmd.menuItem( l='publish to global -->', c=self.onPublish )
	def onOverwrite( self, *a ):
		self.sendEvent( 'clipOverwrite', self.clipPreset )
		self.refresh()
	def onIcon( self, *a ):
		animLib.generateIcon( self.clipPreset )
		self.refresh()
	def onSelect( self, *a ):
		self.sendEvent( 'clipSelected', self.clipPreset )
	def onPublish( self, *a ):
		self.sendEvent( 'clipPublished', self.clipPreset )
	def onRename( self, *a ):
		self.sendEvent( 'clipRenamed', self.clipPreset )
	def onSelectClipItems( self, *a ):
		mappedNodes = mappingUtils.matchNames( self.clipPreset.nodes(), cmd.ls() )
		cmd.select( mappedNodes )
	def onMapping( self, *a ):
		mapping = mappingUtils.matchNames( self.clipPreset.nodes(), cmd.ls( sl=True ) )
		xferAnimUI.XferAnimWindow( mapping, self.clipPreset.clip() )
	def onEdit( self, *a ):
		AnimClipChannelEditorWindow( self.clipPreset )
	def delete( self ):
		self.clipPreset.delete()

		super( ClipWidget, self ).delete()


class ClipsLayout(MelShelfLayout):
	def __new__( cls, parent, libraryManager ):
		return MelShelfLayout.__new__( cls, parent )
	def __init__( self, parent, libraryManager ):
		self._collection = MelIconRadioCollection()
		self._libraryManager = libraryManager
		self._filterStr = None
		self._libraries = None

		self._showAnim = True
		self._showPose = True
		self._showLocal = True
		self._showGlobal = True

		MelPopupMenu( self, pmc=self.buildMenu )
	def setLibraries( self, libraries ):
		self._libraries = libraries
		self.populate()
	def getClips( self ):
		clips = {}
		for library in self._libraries:
			allClips = self._libraryManager.getLibraryClips( library )
			clips[library] = libraryClips = []
			if self._showLocal:
				libraryClips.extend( allClips[presets.LOCAL] )

			if self._showGlobal:
				libraryClips.extend( allClips[presets.GLOBAL] )

		return clips
	def populate( self ):
		self.clear()

		filterStr = self._filterStr
		clips = self.getClips()

		clipTypesToShow = []
		if self._showAnim: clipTypesToShow.append( animLib.AnimClipPreset )
		if self._showPose: clipTypesToShow.append( animLib.PoseClipPreset )

		for library, clips in clips.iteritems():
			for clip in clips:
				if type( clip ) not in clipTypesToShow:
					continue

				clipName = clip.niceName()
				addClip = True
				if filterStr:
					addClip = filterStr in clipName

				if addClip:
					ClipWidget( self, self._collection, clip )
	def getFilter( self ):
		return self._filterStr
	def setFilter( self, filterStr, showAnim=True, showPose=True, showLocal=True, showGlobal=True ):
		self._filterStr = filterStr
		self._showAnim = showAnim
		self._showPose = showPose
		self._showLocal = showLocal
		self._showGlobal = showGlobal
		self.populate()
	def buildMenu( self, parent, *args ):
		cmd.setParent( parent, m=True )
		cmd.menu( parent, e=True, dai=True )

		cmd.menuItem( l='new pose clip', c=lambda *x: self.sendEvent( 'newClip', animLib.PoseClipPreset ) )
		cmd.menuItem( l='new anim clip', c=lambda *x: self.sendEvent( 'newClip', animLib.AnimClipPreset ) )


class ClipApplyLayout(MelVSingleStretchLayout):
	def __init__( self, parent ):
		self.clipPreset = None

		hLayout = MelHSingleStretchLayout( self )
		self.UI_icon = MelImage( hLayout, w=animLib.ICON_SIZE, h=animLib.ICON_SIZE )
		self.UI_clipName = MelLabel( hLayout )
		hLayout.setExpand( True )
		hLayout.setStretchWidget( self.UI_clipName )

		self.UI_opt_currentTime = MelCheckBox( self, l='load clip at current time', v=True )
		self.UI_opt_worldSpace = MelCheckBox( self, l='load clip in world space', v=False, cc=self.update )
		#self.UI_opt_attrSelection = MelCheckBox( self, l='use attribute selection', v=False )
		self.UI_opt_additive = MelCheckBox( self, l='load clip additively', v=False )

		self.setStretchWidget( MelSpacer( self ) )

		#setup the slider - we hide this piece of UI if the preset isn't a pose clip
		self.UI_slider = MelFloatSlider( self, 0, 1, 0 )
		self.UI_slider.setPreChangeCB( self.preDrag )
		self.UI_slider.setChangeCB( self.onDrag )
		self.UI_slider.setPostChangeCB( self.postDrag )

		self.UI_applyAll = MelButton( self, l='Apply To All In Clip', c=self.onApplyAll, en=False )
		self.UI_apply = MelButton( self, l='Apply To Selection', c=self.onApply, en=False )
		self.layout()

		self.update()
		self.setSelectionChangeCB( self.updateApplyButtons )
	def update( self, *a ):
		uisToEnable = self.UI_opt_currentTime, self.UI_opt_worldSpace, self.UI_opt_additive
		for ui in uisToEnable:
			ui.setEnabled( not self.clipPreset is None )

		if self.clipPreset is None:
			self.UI_slider.setVisibility( False )
			self.UI_icon.setImage( '' )
			self.UI_clipName.setLabel( 'select a clip' )
		else:
			self.UI_icon( e=True, w=animLib.ICON_SIZE, h=animLib.ICON_SIZE, image=self.clipPreset.icon() )
			self.UI_clipName.setLabel( '%s\n\n%s %s clip' % (self.clipPreset.niceName(), self.clipPreset.locale(), self.clipPreset.EXT) )

			#hide the slider if the clip type isn't a pose clip
			if type( self.clipPreset ) is animLib.PoseClipPreset:
				self.UI_opt_additive.setVisibility( True )
				self.UI_slider.setVisibility( True )
			else:
				self.UI_slider.setVisibility( False )
				if self.UI_opt_worldSpace.getValue():
					self.UI_opt_additive( e=True, v=False, en=False )
				else:
					self.UI_opt_additive.setEnabled( True )

		self.updateApplyButtons()
	def updateApplyButtons( self ):
		if self.clipPreset is None:
			self.UI_applyAll.setEnabled( False )
			return

		self.UI_applyAll.setEnabled( True )

		sel = cmd.ls( sl=True )
		self.UI_apply.setEnabled( sel )
		self.UI_slider.setEnabled( sel )
	def setClipPreset( self, clipPreset ):
		self.clipPreset = clipPreset
		self.update()
	def getApplyKwargs( self ):
		kwargs = {}
		applySettings = animClip.AnimClip.ApplySettings( None, cmd.currentTime( q=True ) if self.UI_opt_currentTime.getValue() else None )
		kwargs['applySettings'] = applySettings
		kwargs['worldSpace'] = self.UI_opt_worldSpace.getValue()
		kwargs['additive'] = self.UI_opt_additive.getValue()
		#if self.UI_opt_attrSelection.getValue():
			#kwargs['attrs'] = getSelectedChannelBoxAttrNames()

		return kwargs
	def onApplyAll( self, *a ):
		theClip = self.clipPreset.clip()
		theClip.applyToNodes( cmd.ls(), **self.getApplyKwargs() )
	def onApply( self, *a ):
		theClip = self.clipPreset.clip()
		theClip.applyToSelection( **self.getApplyKwargs() )

	### SLIDER EVENT HANDLERS ###
	def preDrag( self ):
		self._objs = objs = cmd.ls( sl=True )

		theClip = self.clipPreset.clip()
		mapping = mappingUtils.matchNames( theClip.getNodes(), objs )

		#generate a new clip based on the current pose of the current selection - we're going to blend between it and the stored pose clip
		self._preClip = theClip.Generate( objs )

		#now setup a mapping between the selection and the nodes stored in the clip and set the mapping
		self._mappedClip = theClip.setMapping( mapping )
		self._applyKwargs = self.getApplyKwargs()

		#pop out the additive kwarg - we want the additive-ness applied during the clip blending NOT when we call clip.apply
		self._additive = self._applyKwargs.pop( 'additive' )

		#open an undo chunk and close it when the slider finishes dragging...
		self._chunkOpened = cmd.undoInfo( openChunk=True )
	def onDrag( self, value ):
		value = float( value )

		#now blend between the initial clip and the clip stored on disk
		blendedClip = self._preClip.blend( self._mappedClip, value, self._additive )
		blendedClip.apply( self._objs, **self._applyKwargs )
	def postDrag( self, value ):
		try:
			self.onDrag( float( value ) )

			#tidy up
			del self._objs
			del self._preClip
			del self._additive
			del self._mappedClip
			del self._applyKwargs
		finally:

			#close the undo chunk - we need to make sure all the slider shinanigans happens in a single undo chunk
			if hasattr( self, '_chunkOpened' ):
				cmd.undoInfo( closeChunk=True )
				del self._chunkOpened

			self.UI_slider.reset()


class AnimLibLayout(MelHSingleStretchLayout):
	def __init__( self, parent ):
		MelHSingleStretchLayout.__init__( self, parent )

		AnimClipChannelEditorWindow.Close()

		self._libraryManager = animLib.LibraryManager()

		vLayout = MelVSingleStretchLayout( self )
		MelLabel( vLayout, l='clip libraries' )

		hLayout = MelHSingleStretchLayout( vLayout )
		MelLabel( hLayout, l='filter' )
		self.UI_filter = MelTextField( hLayout, cc=self.on_filter )
		MelButton( hLayout, l='clear', c=lambda *a: self.UI_filter.clear() )
		hLayout.setStretchWidget( self.UI_filter )

		self.UI_libraries = MelObjectScrollList( vLayout, ams=True )
		self.UI_libraries.setChangeCB( self.on_selectLibrary )
		self.UI_newLibrary = MelButton( vLayout, l='new library', w=150, c=self.on_newLibrary )
		vLayout.setStretchWidget( self.UI_libraries )


		#this is the layout for everything on the right side of the library list
		paneLayout = MelVSingleStretchLayout( self )
		paneLayout.setPadding( 1 )

		#add clip filter UI
		hLayout = MelHSingleStretchLayout( paneLayout )
		MelSpacer( hLayout )
		MelLabel( hLayout, l='filter clips' )
		self.UI_filterClips = MelTextField( hLayout, cc=self.on_filterClips )
		MelButton( hLayout, l='clear', c=lambda *a: self.UI_filterClips.clear() )
		hLayout.setStretchWidget( self.UI_filterClips )

		hLayout = MelHLayout( paneLayout )
		spacer = MelSpacer( hLayout, w=25 )
		self.UI_filter_anim = MelCheckBox( hLayout, l='show anim clips', v=True, cc=self.on_filterClips )
		self.UI_filter_pose = MelCheckBox( hLayout, l='show pose clips', v=True, cc=self.on_filterClips )

		self.UI_filter_local = MelCheckBox( hLayout, l='show local clips', v=True, cc=self.on_filterClips )
		self.UI_filter_global = MelCheckBox( hLayout, l='show global clips', v=True, cc=self.on_filterClips )
		hLayout.setWeight( spacer, 0 )
		hLayout.layout()


		#add the libraries
		self.UI_panes = MelHSingleStretchLayout( paneLayout )
		self.UI_panes.setExpand( True )
		self.UI_panes.setPadding( 1 )

		clipsLayout = MelVSingleStretchLayout( self.UI_panes )
		clipsLayout.setPadding( 2 )
		self.UI_clips = ClipsLayout( clipsLayout, self._libraryManager )

		MelButton( clipsLayout, l='new pose clip', c=self.on_newPose )
		MelButton( clipsLayout, l='new anim clip', c=self.on_newAnim )
		clipsLayout.setStretchWidget( self.UI_clips )
		clipsLayout.layout()

		self.UI_applyOptions = ClipApplyLayout( self.UI_panes )
		self.UI_panes.setStretchWidget( clipsLayout )

		paneLayout.setStretchWidget( self.UI_panes )

		self.setPadding( 1 )
		self.setExpand( True )
		self.setStretchWidget( paneLayout )

		self.populateLibraries()
		self.setDeletionCB( self.on_close )
	def populateLibraries( self ):
		UI_libraries = self.UI_libraries
		UI_libraries.clear()

		libraryNames = self._libraryManager.getLibraryNames()
		for library in libraryNames:
			UI_libraries.append( library )

		if libraryNames:
			self.UI_libraries.selectByIdx( 0, True )

		self.UI_libraries.setFocus()
	def getGenerateKwargs( self ):
		kwargs = { 'worldSpace': True }  #worldspace is always true...  we always want worldspace data available in clips
		#if self.UI_opt_attrSelection.getValue():
			#attrs = getSelectedChannelBoxAttrNames()
			#if attrs:
				#kwargs[ 'attrs' ] = attrs

		return kwargs
	def newClip( self, clipType ):
		theLibrary = self.UI_libraries.getSelectedItems()
		if not theLibrary:
			return

		theLibrary = theLibrary[0]

		BUTTONS = OK, CANCEL = 'OK', 'Cancel'
		typeLabel = clipType.EXT
		ans = cmd.promptDialog( t='enter %s name' % typeLabel, m='enter the %s name:' % typeLabel, b=BUTTONS, db=OK )
		if ans == CANCEL:
			return

		objs = cmd.ls( sl=True )
		name = cmd.promptDialog( q=True, tx=True )
		newClip = clipType( presets.LOCAL, theLibrary, name )
		newClip.write( objs, **self.getGenerateKwargs() )

		#add the clip to the UI
		self.UI_clips.populate()
	def clipOverwrite( self, clipPreset ):
		newClip = type( clipPreset )( clipPreset.locale(), clipPreset.library(), clipPreset.name() )
		newClip.write( cmd.ls( sl=True ), **self.getGenerateKwargs() )
	def clipSelected( self, clipPreset ):
		self.UI_applyOptions.setClipPreset( clipPreset )
	def clipPublished( self, clipPreset ):
		clipPreset.move()
		self.populateLibraries()
	def clipRenamed( self, clipPreset ):
		BUTTONS = OK, CANCEL = 'Ok', 'Cancel'
		ans = cmd.promptDialog( t='new name', m='enter new name', tx=clipPreset.name(), b=BUTTONS, db=OK )
		if ans != OK:
			return

		name = cmd.promptDialog( q=True, tx=True )
		if not name:
			return

		clipPreset = clipPreset.rename( name )
		self.clipSelected( clipPreset )

	### EVENT HANDLERS ###
	def on_close( self, *a ):
		AnimClipChannelEditorWindow.Close()
	def on_selectLibrary( self, *a ):
		sel = self.UI_libraries.getSelectedItems()
		if sel:
			self.UI_clips.setLibraries( sel )
	def on_newLibrary( self, *a ):
		BUTTONS = OK, CANCEL = 'OK', 'Cancel'
		ans = cmd.promptDialog( t='enter library name', m='enter the library name:', b=BUTTONS, db=OK )
		if ans == CANCEL:
			return

		name = cmd.promptDialog( q=True, tx=True )
		self._libraryManager.createLibrary( name )

		self.populateLibraries()

		self.UI_libraries.clearSelection()
		self.UI_libraries.selectByValue( name )
	def on_newPose( self, *args ):
		self.newClip( animLib.PoseClipPreset )
	def on_newAnim( self, *args ):
		self.newClip( animLib.AnimClipPreset )
	def on_filter( self, *a ):
		self.UI_libraries.setFilter( self.UI_filter.getValue() )

		#if there are no selected items, check to see if there are any items and if so select the first one
		if not self.UI_libraries.getSelectedIdxs():
			if self.UI_libraries.getItems():
				self.UI_libraries.selectByIdx( 0, True )
	def on_filterClips( self, *a ):
		showAnim = self.UI_filter_anim.getValue()
		showPose = self.UI_filter_pose.getValue()
		if not showAnim and not showPose:
			showAnim = True
			self.UI_filter_anim.setValue( True, False )

		showLocal = self.UI_filter_local.getValue()
		showGlobal = self.UI_filter_global.getValue()
		if not showLocal and not showGlobal:
			showLocal = True
			self.UI_filter_local.setValue( True, False )

		self.UI_clips.setFilter( self.UI_filterClips.getValue(), showAnim, showPose, showLocal, showGlobal )


class AnimLibWindow(BaseMelWindow):
	WINDOW_NAME = 'animLibraryWindow'
	WINDOW_TITLE = 'Animation Library'

	DEFAULT_SIZE = 750, 400
	FORCE_DEFAULT_SIZE = True

	DEFAULT_MENU = None
	HELP_MENU = None

	def __init__( self ):
		BaseMelWindow.__init__( self )

		self.UI_editor = AnimLibLayout( self )
		self.show()

animLib.LibraryManager().createLibrary( 'default' )


#end
