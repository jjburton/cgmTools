
from baseMelUI import *
from maya.cmds import *
from melUtils import printWarningStr

#this dict stores attribute values for the selection - attributeChange scriptjobs fire when an attribute changes
#but don't pass in pre/post values, or even the name of the attribute that has changed.  So when the scriptjobs
#are first setup, their attribute values are stored in this dict and are updated when they change
PRE_ATTR_VALUES = {}


class AttrpathCallback(object):
	'''
	callable object that gets executed when the value of the attrpath changes
	'''

	#defines whether the instance should early out when called or not
	ENABLED = True

	def __init__( self, ui, attrpath ):
		self.ui = ui
		self.attrpath = attrpath

		#setup the initial value of the attrpath in the global attr value dict
		time = currentTime( q=True )
		PRE_ATTR_VALUES[ attrpath ] = getAttr( attrpath )
	def __call__( self ):
		if not self.ENABLED:
			return

		#if autokey is turned on, bail - this + autokey = potentially weird behaviour
		#NOTE: the tool will turn autokey off automatically when loaded - so if its on, its because the user has turned it back on.  Also
		#worth noting - this tool will restore the initial autokey state when closed/turned off...
		if autoKeyframe( q=True ):
			printWarningStr( "Autokey is enabled - This tool doesn't play nice with autokey!  Please turn it off!" )
			return

		#if there are no entries in here - bail, they've already been handled
		if not PRE_ATTR_VALUES:
			return

		#put the following into a single undo chunk
		try:
			undoInfo( openChunk=True )
			for attrpath, preValue in PRE_ATTR_VALUES.iteritems():
				curValue = getAttr( attrpath )
				valueDelta = curValue - preValue

				#if there was no delta, keep loopin
				if not valueDelta:
					continue

				#if there are no keyframes on this attribute - keep loopin
				if not keyframe( attrpath, q=True, kc=True ):
					continue

				keyframe( attrpath, e=True, t=(), vc=valueDelta, relative=True )

			PRE_ATTR_VALUES.clear()
		finally:
			undoInfo( closeChunk=True )

		#setup an idle event to re-populate the PRE_ATTR_VALUES dict when everything has finished processing
		scriptJob( runOnce=True, idleEvent=self.ui.on_selectionChange )


class PosePropagatorLayout(MelHLayout):
	def __init__( self, parent ):
		MelHLayout.__init__( self, parent )

		self._initialAutoKeyState = autoKeyframe( q=True, state=True )

		self.UI_dummyParent = None  #this is some dummy UI to store attribute change scriptjobs - this easily ensures things get teared down if the tool gets closed
		self.UI_on = MelButton( self, h=100, c=self.on_toggleEnable )

		self.layout()
		self.updateState()

		#fire the selection change to update the current selection state
		self.on_selectionChange()

		self.setSceneChangeCB( self.on_selectionChange )
		self.setSelectionChangeCB( self.on_selectionChange )
		self.setTimeChangeCB( self.on_timeChange )
		self.setDeletionCB( self.on_delete )
	def setEnableState( self, state=True ):
		'''
		sets the on/off state of the tool and updates UI accordingly
		'''

		#we need to disable autokey when running this tool - but we want to restore the initial autokey state when
		#the tool is either turned off or closed, so we need to store the initial auto key state on the instance
		if state:
			self._initialAutoKeyState = autoKeyframe( q=True, state=True )
			autoKeyframe( e=True, state=False )
		else:
			autoKeyframe( e=True, state=self._initialAutoKeyState )

		AttrpathCallback.ENABLED = state
		self.updateState()
	def updateState( self ):
		self.UI_on.setLabel( 'currently on: turn OFF' if AttrpathCallback.ENABLED else 'turn ON' )
		self.UI_on.setColour( (1, 0, 0) if AttrpathCallback.ENABLED else (0.6, 0.6, 0.6) )

	### EVENT HANDLERS ###
	def on_toggleEnable( self, *a ):
		self.setEnableState( not AttrpathCallback.ENABLED )
	def on_enable( self, *a ):
		self.setEnableState( True )
	def on_disable( self, *a ):
		self.setEnableState( False )
	def on_sceneChange( self ):
		'''
		turn the tool off, and update state
		'''
		self.setEnableState( False )
		self.on_selectionChange()
	def on_selectionChange( self ):
		'''
		delete the old attribute change callbacks and add new ones for the current selection
		'''
		if self.UI_dummyParent is not None:
			self.UI_dummyParent.delete()
			PRE_ATTR_VALUES.clear()

		#create a dummy piece of UI to "hold" on to the scriptjobs
		self.UI_dummyParent = UI_dummyParent = MelButton( self, l='', w=1, h=1, vis=False )
		for obj in ls( sl=True ):
			for attr in listAttr( obj, keyable=True ):
				attrpath = '%s.%s' % (obj, attr)
				if objExists( attrpath ):
					UI_dummyParent.setAttributeChangeCB( attrpath, AttrpathCallback( self, attrpath ), False )
	def on_timeChange( self ):
		'''
		when the time changes we need to refresh the values in the PRE_ATTR_VALUES dict
		'''
		time = currentTime( q=True )
		PRE_ATTR_VALUES.clear()
		for attrpath in PRE_ATTR_VALUES.keys():
			PRE_ATTR_VALUES[ attrpath ] = getAttr( attrpath )
	def on_delete( self ):
		autoKeyframe( e=True, state=self._initialAutoKeyState )


class PosePropagatorWindow(BaseMelWindow):
	WINDOW_NAME = 'posePropagatorWindow'
	WINDOW_TITLE = 'Pose Propagator'

	DEFAULT_MENU = None
	DEFAULT_SIZE = 275, 140
	FORCE_DEFAULT_SIZE = True

	def __init__( self ):
		self.UI_editor = PosePropagatorLayout( self )
		self.UI_editor.setEnableState( AttrpathCallback.ENABLED )
		self.show()


#end
