
from baseMelUI import *
from apiExtensions import iterParents
from melUtils import mel, melecho

import maya.cmds as cmd
import mappingEditor
import mappingUtils
import animClip


class XferAnimMappingLayout(mappingEditor.MappingLayout):
	def build_srcMenu( self, *a ):
		super( XferAnimMappingLayout, self ).build_srcMenu( *a )
		cmd.menuItem( l='Auto-Generate Offsets', c=self.on_autoMap )
	def on_autoMap( self, *a ):
		animClip.autoGeneratePostTraceScheme( self.getMapping() )


class XferAnimForm(MelVSingleStretchLayout):
	def __init__( self, parent ):
		MelVSingleStretchLayout.__init__( self, parent )

		self._clip = None
		self.UI_mapping = XferAnimMappingLayout( self )

		vLayout = MelVSingleStretchLayout( self )
		hLayout = MelHLayout( vLayout )
		vLayout.setStretchWidget( hLayout )

		colLayout = MelColumnLayout( hLayout )
		self.UI_radios = MelRadioCollection()
		self.RAD_dupe = self.UI_radios.createButton( colLayout, l="duplicate nodes", align='left', sl=True, cc=self.on_update )
		self.RAD_copy = self.UI_radios.createButton( colLayout, l="copy/paste keys", align='left', cc=self.on_update )
		self.RAD_trace = self.UI_radios.createButton( colLayout, l="trace objects", align='left', cc=self.on_update )

		colLayout = MelColumnLayout( hLayout )
		self.UI_check1 = MelCheckBox( colLayout, l="instance animation" )
		self.UI_check2 = MelCheckBox( colLayout, l="match rotate order", v=True )
		self.UI_check3 = MelCheckBox( colLayout, l="" )
		hLayout.layout()

		self.UI_traceOptionsLayout = hLayout = MelHRowLayout( self )
		self.UI_keysOnly = MelCheckBox( hLayout, l="keys only", v=True, cc=self.on_update )
		self.UI_withinRange = MelCheckBox( hLayout, l="within range:", v=False, cc=self.on_update )
		MelLabel( hLayout, l="start ->" )
		self.UI_start = MelTextField( hLayout, en=False, tx='!', w=50 )
		cmd.popupMenu( p=self.UI_start, b=3, pmc=self.buildTimeMenu )

		MelLabel( hLayout, l="end ->" )
		self.UI_end = MelTextField( hLayout, en=False, tx='!', w=50 )
		cmd.popupMenu( p=self.UI_end, b=3, pmc=self.buildTimeMenu )
		hLayout.layout()

		vLayout.layout()

		self.UI_button = MelButton( self, l='Xfer Animation', c=self.on_xfer )

		self.setStretchWidget( self.UI_mapping )
		self.layout()

		self.on_update()  #set initial state
	def setMapping( self, mapping ):
		self.UI_mapping.setMapping( mapping )
	def setClip( self, clip, mapping=None ):
		self._clip = clip

		#populate the source objects from the file
		self.UI_mapping.replaceSrcItems( clip.getNodes() )

		self.RAD_dupe( e=True, en=True, l="times from clip" )
		self.RAD_copy( e=True, en=True, sl=True, l="load clip at current time" )
		self.RAD_trace( e=True, en=False, vis=False )

		self.UI_check1( e=True, l="additive key values" )
		self.UI_check2( e=True, l="import as world space", v=False )
		self.UI_check3( e=True, vis=0 )
		self.UI_traceOptionsLayout.setVisibility( False )

		self.UI_button.setLabel( 'Load Clip' )

		self.on_update()

	### MENU BUILDERS ###
	def buildTimeMenu( self, parent, uiItem ):
		cmd.menu( parent, e=True, dai=True )
		cmd.setParent( parent, m=True )

		cmd.menuItem( l="! - use current range", c=lambda a: cmd.textField( uiItem, e=True, tx='!' ) )
		cmd.menuItem( l=". - use current frame", c=lambda a: cmd.textField( uiItem, e=True, tx='.' ) )
		cmd.menuItem( l="$ - use scene range", c=lambda a: cmd.textField( uiItem, e=True, tx='$' ) )

	### EVENT HANDLERS ###
	def on_update( self, *a ):
		sel = cmd.ls( sl=True, dep=True )

		if not self._clip is not None:
			if self.RAD_dupe.getValue():
				self.UI_check1.setEnabled( True )
			else:
				self.UI_check1( e=True, en=False, v=False )

		if self.RAD_trace.getValue():
			self.UI_keysOnly.setEnabled( True )
			self.UI_check2.getValue()
			self.UI_check3( e=True, vis=True, v=True, l="process post-trace cmds" )
		else:
			self.UI_keysOnly( e=True, en=False )
			self.UI_check3( e=True, vis=False, v=False )

		if  self.UI_keysOnly.getValue():
			self.UI_withinRange.setEnabled( True )
		else:
			self.UI_withinRange( e=True, en=False, v=False )

		enableRange = self.RAD_copy.getValue() or self.RAD_trace.getValue()
		keysOnly = self.UI_keysOnly.getValue()
		withinRange = self.UI_withinRange.getValue()
		if enableRange and not keysOnly or withinRange:
			self.UI_start.setEnabled( True )
			self.UI_end.setEnabled( True )
		else:
			self.UI_start.setEnabled( False )
			self.UI_end.setEnabled( False )
	def on_xfer( self, *a ):
		mapping = self.UI_mapping.getMapping()

		isDupe = self.RAD_dupe.getValue()
		isCopy = self.RAD_copy.getValue()
		isTraced = self.RAD_trace.getValue()

		instance = additive = self.UI_check1.getValue()
		traceKeys = self.UI_keysOnly.getValue()
		matchRo = worldSpace = self.UI_check2.getValue()
		startTime = self.UI_start.getValue()
		endTime = self.UI_end.getValue()
		processPostCmds = self.UI_check3.getValue()

		if startTime.isdigit():
			startTime = int( startTime )
		else:
			if startTime == '!': startTime = cmd.playbackOptions( q=True, min=True )
			elif startTime == '.': startTime = cmd.currentTime( q=True )
			elif startTime == '$': startTime = cmd.playbackOptions( q=True, animationStartTime=True )

		if endTime.isdigit():
			endTime = int( endTime )
		else:
			if endTime == '!': endTime = cmd.playbackOptions( q=True, max=True )
			elif endTime == '.': endTime = cmd.currentTime( q=True )
			elif endTime == '$': endTime = cmd.playbackOptions( q=True, animationEndTime=True )

		withinRange = self.UI_withinRange.getValue()
		if withinRange:
			applySettings = animClip.AnimClip.ApplySettings( (0, endTime-startTime) )
		else:
			applySettings = None

		if self._clip is not None:
			mapping = self.UI_mapping.getMapping()
			assert isinstance( self._clip, animClip.BaseClip )
			self._clip.setMapping( mapping ).apply( mapping.tgts, worldSpace=worldSpace, additive=additive )
		elif isDupe:
			clip = animClip.AnimCurveDuplicator( instance, matchRo )
			clip.apply( mapping )
		elif isCopy:
			clip = animClip.AnimClip.Generate( mapping.srcs )
			assert isinstance( clip, animClip.AnimClip )
			clip.apply( mapping, applySettings )
		elif isTraced:
			clip = animClip.Tracer( traceKeys, processPostCmds, startTime, endTime )
			clip.apply( mapping, True )


class XferAnimWindow(BaseMelWindow):
	WINDOW_NAME = 'xferAnim'
	WINDOW_TITLE = 'Xfer Anim'

	DEFAULT_SIZE = 375, 450
	DEFAULT_MENU = None

	def __new__( cls, mapping=None, clip=None ):
		return BaseMelWindow.__new__( cls )
	def __init__( self, mapping=None, clip=None ):
		BaseMelWindow.__init__( self )
		self.editor = XferAnimForm( self )
		if clip is not None:
			assert isinstance( clip, animClip.BaseClip )
			self.editor.setClip( clip )

		if mapping is not None:
			self.editor.setMapping( mapping )

		self.show()


#end
