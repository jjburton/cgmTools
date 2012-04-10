
'''
This module abstracts and packages up the maya UI that is available to script in a more
object oriented fashion.  For the most part the framework tries to make working with maya
UI a bit more like proper UI toolkits where possible.

For more information there is some high level documentation on how to use this code here:
http://www.macaronikazoo.com/?page_id=311
'''

import re
import inspect

import maya
import maya.cmds as cmd

from maya.OpenMaya import MGlobal

from zooPy import names
from zooPy import typeFactories
from zooPy.misc import removeDupes, Callback, iterBy
from zooPy.path import Path

import melUtils

mayaVer = int( maya.mel.eval( 'getApplicationVersionAsFloat' ) )

_DEBUG = True

#try to import wing...
try:
	import wingdbstub
except:
	_DEBUG = False


class MelUIError(Exception): pass


#this maps ui type strings to actual command objects - they're not always called the same
TYPE_NAMES_TO_CMDS = { u'staticText': cmd.text,
                       u'field': cmd.textField,
                       u'cmdScrollField': cmd.scrollField,
                       u'commandMenuItem': cmd.menuItem,
                       u'dividorMenuItem': cmd.menuItem }

#stores a list of widget cmds that don't have docTag support - classes that wrap this command need to skip encoding the classname into the docTag.  obviously.
WIDGETS_WITHOUT_DOC_TAG_SUPPORT = [ cmd.popupMenu ]


class BaseMelUI(unicode):
	'''
	This is a wrapper class for a mel widget to make it behave a little more like an object.  It
	inherits from str because thats essentially what a mel widget is - a name coupled with a mel
	command.  To interact with the widget the mel command is called with the UI name as the first arg.

	As a shortcut objects of this type are callable - the args taken depend on the specific command,
	and can be found in the mel docs.

	example:
	class AButtonClass(BaseMelUI):
		WIDGET_CMD = cmd.button

	aButton = AButtonClass( parentName, label='hello' )
	aButton( edit=True, label='new label!' )
	'''

	__metaclass__ = typeFactories.trackableTypeFactory( typeFactories.instanceTrackerTypeFactory() )

	#this should be set to the mel widget command used by this widget wrapped - ie cmd.button, or cmd.formLayout
	WIDGET_CMD = cmd.control

	#if not None, this is used to set the default width of the widget when created
	DEFAULT_WIDTH = None

	#default heights in 2011 aren't consistent - buttons are 24 pixels high by default (this is a minimum possible value too) while input fields are 20
	DEFAULT_HEIGHT = None if mayaVer < 2011 else 24

	#this is the name of the kwarg used to set and get the "value" of the widget - most widgets use the "value" or "v" kwarg, but others have special names.  three cheers for mel!
	KWARG_VALUE_NAME = 'v'
	KWARG_VALUE_LONG_NAME = 'value'

	#populate this dictionary with variable names you want created on instances.  values are default values.  having this dict saves having to override __new__ and __init__ methods on subclasses just to create instance variables on creation
	#the variables are also popped out of the **kw arg by both __new__ and __init__, so specifying variable names and default values here is the equivalent of making them available on the constructor method
	_INSTANCE_VARIABLES = {}

	#this is the name of the "main" change command kwarg.  some widgets have multiple change callbacks that can be set, and they're not abstracted, but this is the name of the change cb name you want to be referenced by the setChangeCB method
	KWARG_CHANGE_CB_NAME = 'cc'

	@classmethod
	def Exists( cls, theControl ):
		if isinstance( theControl, BaseMelUI ):
			return theControl.exists()

		return cmd.control( theControl, q=True, exists=True )
	@classmethod
	def IterWidgetClasses( cls, widgetCmd ):
		if widgetCmd is None:
			return

		for subCls in BaseMelUI.IterSubclasses():
			if subCls.WIDGET_CMD is widgetCmd:
				yield subCls

	def __new__( cls, parent, *a, **kw ):
		WIDGET_CMD = cls.WIDGET_CMD
		kw.pop( 'p', None )  #pop any parent specified in teh kw dict - set it explicitly to the parent specified
		if parent is not None:
			kw[ 'parent' ] = parent

		#pop out any instance variables defined in the _INSTANCE_VARIABLES dict
		instanceVariables = {}
		for attrName, attrDefaultValue in cls._INSTANCE_VARIABLES.iteritems():
			instanceVariables[ attrName ] = kw.pop( attrName, attrDefaultValue )

		#set default sizes if applicable
		width = kw.pop( 'w', kw.pop( 'width', cls.DEFAULT_WIDTH ) )
		if isinstance( width, int ):
			kw[ 'width' ] = width

		height = kw.pop( 'h', kw.pop( 'height', cls.DEFAULT_HEIGHT ) )
		if isinstance( height, int ):
			kw[ 'height' ] = height

		#not all mel widgets support docTags...  :(
		if WIDGET_CMD not in WIDGETS_WITHOUT_DOC_TAG_SUPPORT:
			#store the name of this class in the widget's docTag - we can use this to re-instantiate the widget once it's been created
			kw.pop( 'dtg', kw.pop( 'docTag', None ) )
			kw[ 'docTag' ] = docTag=cls.__name__

		#pop out the change callback if its been passed in with the kw dict, and run it through the setChangeCB method so it gets registered appropriately
		changeCB = kw.pop( cls.KWARG_CHANGE_CB_NAME, None )

		#get the leaf name for the parent
		parentNameTok = str( parent ).split( '|' )[-1]

		#this has the potential to be slow: it generates a unique name for the widget we're about to create, the benefit of doing this is that we're
		#guaranteed the widget LEAF name will be unique.  I'm assuming maya also does this, but I'm unsure.  if there are weird ui naming conflicts
		#it might be nessecary to uncomment this code
		formatStr = '%s%d__'#+ parentNameTok
		baseName, n = cls.__name__, cls.GetUniqueId()
		uniqueName = formatStr % (baseName, n)
		while WIDGET_CMD( uniqueName, q=True, exists=True ):
			n += 1
			uniqueName = formatStr % (baseName, n)

		WIDGET_CMD( uniqueName, **kw )

		new = unicode.__new__( cls, uniqueName )
		new.parent = parent
		new._cbDict = cbDict = {}

		#add the instance variables to the instance
		for attrName, attrValue in instanceVariables.iteritems():
			new.__dict__[ attrName ] = attrValue

		#if the changeCB is valid, add it to the cd dict
		if changeCB:
			new.setCB( cls.KWARG_CHANGE_CB_NAME, changeCB )

		return new
	def __init__( self, parent, *a, **kw ):
		pass
	def __call__( self, *a, **kw ):
		return self.WIDGET_CMD( unicode( self ), *a, **kw )
	def setChangeCB( self, cb ):
		self.setCB( self.KWARG_CHANGE_CB_NAME, cb )
	def getChangeCB( self ):
		return self.getCB( self.KWARG_CHANGE_CB_NAME )
	def setCB( self, cbFlagName, cb ):
		if cb is None:
			if cbFlagName in self._cbDict:
				self._cbDict.pop( cbFlagName )
		else:
			self.WIDGET_CMD( self, **{ 'e': True, cbFlagName: cb } )
			self._cbDict[ cbFlagName ] = cb
	def getCB( self, cbFlagName ):
		return self._cbDict.get( cbFlagName, None )
	def _executeCB( self, cbFlagName=None ):
		if cbFlagName is None:
			cbFlagName = self.KWARG_CHANGE_CB_NAME

		cb = self.getCB( cbFlagName )
		if cb is None:
			return

		if callable( cb ):
			try:
				cb()
			except Exception, x:
				melUtils.printErrorStr( "The %s callback failed" % cbFlagName )
	def getFullName( self ):
		'''
		returns the fullname to the UI widget
		'''
		parents = list( self.iterParents() )
		parents.reverse()
		parents.append( self )

		parents = [ uiFullName.split( '|' )[ -1 ] for uiFullName in parents ]

		return '|'.join( parents )
	def sendEvent( self, methodName, *methodArgs, **methodKwargs ):
		'''
		events are nothing more than a tuple containing a methodName, argument list and
		keyword dict that gets propagated up the UI hierarchy.

		Each widget in the hierarchy is asked whether it has a method of the given name,
		and if it does, the method is called with the argumentList and keywordDict and
		propagation ends.
		'''
		self.parent.processEvent( methodName, methodArgs, methodKwargs )
	def processEvent( self, methodName, methodArgs, methodKwargs ):
		method = getattr( self, methodName, None )
		if callable( method ):
			#run the method in the buff if we're in debug mode
			if _DEBUG:
				method( *methodArgs, **methodKwargs )
			else:
				try:
					method( *methodArgs, **methodKwargs )
				except:
					melUtils.printErrorStr( 'Event Failed: %s, %s, %s' % (methodName, methodArgs, methodKwargs) )
					import traceback
					traceback.print_exc()
		else:
			self.parent.processEvent( methodName, methodArgs, methodKwargs )
	def getVisibility( self ):
		return self( q=True, vis=True )
	def setVisibility( self, visibility=True ):
		'''
		hides the widget
		'''
		self( e=True, vis=visibility )
	def hide( self ):
		self.setVisibility( False )
	def show( self ):
		self.setVisibility( True )
	def setWidth( self, width ):
		self( e=True, width=width )
	def getWidth( self ):
		return self( q=True, width=True )
	def setHeight( self, height ):
		self( e=True, height=height )
	def getHeight( self ):
		return self( q=True, height=True )
	def setSize( self, widthHeight ):
		self( e=True, w=widthHeight[ 0 ], h=widthHeight[ 1 ] )
	def getSize( self ):
		w = self( q=True, w=True )
		h = self( q=True, h=True )

		return w, h
	def getColour( self ):
		return self( q=True, bgc=True )
	getColor = getColour
	def setColour( self, colour ):
		if mayaVer > 2011:
			self( e=True, bgc=colour, enableBackground=True )
		else:
			initialVis = self( q=True, vis=True )
			self( e=True, bgc=colour, vis=False )
			if initialVis:
				self( e=True, vis=True )
	setColor = setColour
	def resetColour( self ):
		self( e=True, enableBackground=False )
	resetColor = resetColour
	def getParent( self ):
		'''
		returns the widget's parent.

		NOTE: its not possible to change a widget's parent once its been created
		'''
		return self.parent  #cmd.control( self, q=True, parent=True )
	def iterParents( self ):
		'''
		returns a generator that walks up the widget hierarchy
		'''
		try:
			parent = self.parent
			while True:
				yield parent

				#if the parent isn't an instance of BaseMelUI (the user has mixed baseMelUI and plain old mel) this should throw an attribute error
				try:
					parent = parent.parent

				#in which case, try to cast the widget as a BaseMelUI instance and yield that instead
				except AttributeError:
					parent = BaseMelUI.FromStr( cmd.control( parent, q=True, parent=True ) )

		except RuntimeError: return
	def getTopParent( self ):
		'''
		returns the top widget at the top of this widget's hierarchy
		'''
		parent = self.parent
		while True:
			try:
				parent = parent.parent
			except AttributeError: return parent
	def getParentOfType( self, parentClass, exactMatch=False ):
		'''
		if exactMatch is True the class of the parent must be the parentClass, otherwise it checks
		whether the parent is a subclass of parentClass
		'''
		for parent in self.iterParents():
			if exactMatch:
				if parent.__class__ is parentClass:
					return parent
			else:
				if issubclass( parent.__class__, parentClass ):
					return parent
	def exists( self ):
		return cmd.control( self, ex=True )
	def delete( self ):
		cmd.deleteUI( self )
	def setSelectionChangeCB( self, cb, compressUndo=True, **kw ):
		'''
		creates a scriptJob to monitor selection, and fires the given callback when the selection changes
		the scriptJob is parented to this widget so it dies when the UI is closed

		NOTE: selection callbacks don't take any args
		'''
		return cmd.scriptJob( compressUndo=compressUndo, parent=self, event=('SelectionChanged', cb), **kw )
	def setSceneChangeCB( self, cb, compressUndo=True, **kw ):
		'''
		creates a scriptJob which will fire when the currently open scene changes
		the scriptJob is parented to this widget so it dies when the UI is closed

		NOTE: scene change callbacks don't take any args
		'''
		return cmd.scriptJob( compressUndo=compressUndo, parent=self, event=('SceneOpened', cb), **kw )
	def setTimeChangeCB( self, cb, compressUndo=True, **kw ):
		'''
		creates a scriptJob which will fire when the current time changes
		the scriptJob is parented to this widget so it dies when the UI is closed

		NOTE: time change callbacks don't take any args
		'''
		return cmd.scriptJob( compressUndo=compressUndo, parent=self, event=('timeChanged', cb), **kw )
	def setAttributeChangeCB( self, attrpath, cb, compressUndo=True, allChildren=False, disregardIndex=False, **kw ):
		'''
		creates a scriptjob which will fire when the given attribute gets changed
		'''
		return cmd.scriptJob( compressUndo=compressUndo, parent=self, attributeChange=(attrpath, cb), allChildren=allChildren, disregardIndex=disregardIndex, **kw )
	def setDeletionCB( self, cb, compressUndo=True, **kw ):
		'''
		define a callback that gets triggered when this piece of UI gets deleted
		'''
		return cmd.scriptJob( compressUndo=compressUndo, uiDeleted=(self, cb), **kw )
	def setUndoCB( self, cb, compressUndo=True, **kw ):
		'''
		define a callback that gets triggered when an undo event is issued
		'''
		return cmd.scriptJob( compressUndo=compressUndo, parent=self, event=('Undo', cb), **kw )
	@classmethod
	def FromStr( cls, theStr ):
		'''
		given a ui name, this will cast the string as a widget instance
		'''

		#if the instance is in the instance list, return it
		for instance in cls.IterInstances():
			if str( instance ) == theStr:
				return instance
		else:
			theStrLeaf = theStr.split( '|' )[-1]
			for instance in cls.IterInstances():
				if str( instance ) == theStrLeaf:
					return instance

		try:
			uiTypeStr = cmd.objectTypeUI( theStr )
		except RuntimeError:
			try:
				uiTypeStr = cmd.objectTypeUI( theStr.split( '|' )[ -1 ] )
			except RuntimeError:
				uiTypeStr = ''

		uiCmd = TYPE_NAMES_TO_CMDS.get( uiTypeStr, getattr( cmd, uiTypeStr, cmd.control ) )

		theCls = None
		if uiCmd not in WIDGETS_WITHOUT_DOC_TAG_SUPPORT:
			#see if the data stored in the docTag is a valid class name - it might not be if teh user has used the docTag for something (why would they? there is no need, but still check...)
			try:
				possibleClassName = uiCmd( theStr, q=True, docTag=True )

			#menu item dividers have a weird type name when queried - "dividorMenuItem", which is a menuItem technically, but you can't query its docTag, so this catch statement is exclusively for this case as far as I know...
			except RuntimeError: pass
			else:
				theCls = BaseMelUI.GetNamedSubclass( possibleClassName )

		#if the data stored in the docTag doesn't map to a subclass, then we'll have to guess at the best class...
		if theCls is None:
			#melUtils.printInfoStr( cmd.objectTypeUI( theStr ) )  ##NOTE: the typestr isn't ALWAYS the same name as the function used to interact with said control, so this debug line can be useful for spewing object type names...

			theCls = BaseMelUI  #at this point default to be an instance of the base widget class
			candidates = list( BaseMelUI.IterWidgetClasses( uiCmd ) )
			if candidates:
				theCls = candidates[ 0 ]

		new = unicode.__new__( theCls, theStr )  #we don't want to run initialize on the object - just cast it appropriately
		new._cbDict = cbDict = {}

		#we need to manually add it to the instance list though - because its not being constructed in the usual way
		cls.AppendInstance( new )

		#try to grab the parent...
		try:
			new.parent = cmd.control( theStr, q=True, parent=True )
		except RuntimeError: new.parent = None

		return new


class BaseMelLayout(BaseMelUI):
	'''
	base class for layout UI
	'''
	WIDGET_CMD = cmd.layout

	DEFAULT_WIDTH = None
	DEFAULT_HEIGHT = None

	def getChildren( self ):
		'''
		returns a list of all children UI items
		'''
		children = self( q=True, ca=True ) or []
		children = [ BaseMelUI.FromStr( c ) for c in children ]

		return children
	def getNumChildren( self ):
		return len( self.getChildren() )
	def printUIHierarchy( self ):
		def printChildren( children, depth ):
			for child in children:
				melUtils.printInfoStr( '%s%s' % ('  ' * depth, child) )
				if isinstance( child, BaseMelLayout ):
					printChildren( child.getChildren(), depth+1 )

		melUtils.printInfoStr( self )
		printChildren( self.getChildren(), 1 )
	def clear( self ):
		'''
		deletes all children from the layout
		'''
		for childUI in self.getChildren():
			cmd.deleteUI( childUI )


class MelFormLayout(BaseMelLayout):
	WIDGET_CMD = cmd.formLayout
	ALL_EDGES = 'top', 'left', 'right', 'bottom'

	def getOtherEdges( self, edges ):
		otherEdges = list( self.ALL_EDGES )
		for edge in edges:
			if edge in otherEdges:
				otherEdges.remove( edge )

		return otherEdges


class MelSingleLayout(MelFormLayout):
	'''
	Simple layout that causes the child to stretch to the extents of the layout in all directions.

	NOTE: make sure to call layout() after the child has been created to setup the layout data
	'''

	_INSTANCE_VARIABLES = { 'padding': 0 }

	def __init__( self, parent, padding=0, *a, **kw ):
		MelFormLayout.__init__( self, parent, *a, **kw )
		self._padding = padding
	def getPadding( self ):
		return self._padding
	def setPadding( self, padding ):
		self._padding = padding
		self.layout()
	def layout( self ):
		children = self.getChildren()

		assert len( children ) == 1, "Can only support one child!"

		padding = self._padding
		theChild = children[ 0 ]
		self( e=True, af=((theChild, 'top', padding), (theChild, 'left', padding), (theChild, 'right', padding), (theChild, 'bottom', padding)) )


class _AlignedFormLayout(MelFormLayout):
	_EDGES = 'left', 'right'

	def setPadding( self, padding ):
		self.padding = padding
	def setExpand( self, expand ):
		'''
		make sure to call layout() after changing the expand value
		'''
		self.expand = expand
	def getOtherEdges( self ):
		return MelFormLayout.getOtherEdges( self, self._EDGES )
	def layoutExpand( self, children ):
		edge1, edge2 = self._EDGES

		try:
			padding = self.padding
		except AttributeError:
			padding = 0

		otherEdges = self.getOtherEdges()
		otherEdge1, otherEdge2 = otherEdges

		for child in children:
			self( e=True, af=((child, otherEdge1, padding), (child, otherEdge2, padding)) )


class MelHLayout(_AlignedFormLayout):
	'''
	emulates a horizontal layout sizer - the only caveat is that you need to explicitly call
	the layout method to setup sizing.

	NOTE: you need to call layout() once the children have been created to initialize the
	layout relationships

	example:
		row = MelHLayout( self )

		MelButton( row, l='apples' )
		MelButton( row, l='bananas' )
		MelButton( row, l='oranges' )

		row.layout()
	'''
	_INSTANCE_VARIABLES = { '_weights': {},
	                        'padding': 0,

	                        #if True the layout will expand to fill the layout in the "other" direction.  Ie HLayouts will expand vertically and VLayouts will expand horizontally to the extents of the layout
	                        'expand': False }

	def setWeight( self, widget, weight=1 ):
		self._weights[ widget ] = weight
	def getHeight( self ):
		return max( [ ui.getHeight() for ui in self.getChildren() ] )
	def getWidth( self ):
		return sum( [ ui.getWidth() for ui in self.getChildren() ] )
	def layout( self, expand=None ):
		if expand is not None:
			self.expand = expand

		padding = self.padding
		children = self.getChildren()

		weightsDict = self._weights

		weightsList = []
		for child in children:
			weight = weightsDict.get( child, 1 )
			weightsList.append( weight )

		weightSum = float( sum( weightsList ) )
		#if not weightSum:
			#return

		weightAccum = 0
		positions = []
		for weight in weightsList:
			actualWeight = 100 * weightAccum / weightSum
			weightAccum += weight
			positions.append( actualWeight )

		edge1, edge2 = self._EDGES
		positions.append( 100 )
		for n, child in enumerate( children ):
			self( e=True, ap=((child, edge1, padding, positions[n]), (child, edge2, padding, positions[n+1])) )

		#if any children have a weight of zero, set the next item in the list to attach to the widget instead of a position
		for n, weight in enumerate( weightsList ):
			if weight == 0:
				thisW = children[ n ]
				try:
					nextW = children[ n+1 ]
					self( e=True, ac=(nextW, edge1, padding, thisW), an=(thisW, edge2) )
				except IndexError:
					prevW = children[ n-1 ]
					self( e=True, ac=(prevW, edge2, padding, thisW), an=(thisW, edge1) )

		if self.expand:
			self.layoutExpand( children )


class MelVLayout(MelHLayout):
	_EDGES = 'top', 'bottom'

	def getHeight( self ):
		return sum( [ ui.getHeight() for ui in self.getChildren() ] )
	def getWidth( self ):
		return max( [ ui.getWidth() for ui in self.getChildren() ] )


class MelHRowLayout(_AlignedFormLayout):
	'''
	Simple row layout - the rowLayout mel command isn't so hot because you have to know ahead
	of time how many columns to build, and dynamic sizing is rubbish.  This makes writing a
	simple row of widgets super easy.

	NOTE: like all subclasses of MelFormLayout, make sure to call .layout() after children
	have been built
	'''
	_INSTANCE_VARIABLES = { 'padding': 5,

	                        #if True the layout will expand to fill the layout in the "other" direction.  Ie HLayouts will expand vertically and VLayouts will expand horizontally to the extents of the layout
	                        'expand': False }

	def layout( self, expand=None ):
		if expand is not None:
			self.expand = expand

		padding = self.padding
		children = self.getChildren()

		edge1, edge2 = self._EDGES
		for n, child in enumerate( children ):
			if n:
				self( e=True, ac=(child, edge1, padding, children[ n-1 ]) )
			else:
				self( e=True, af=(child, edge1, 0) )

		if self.expand:
			self.layoutExpand( children )


class MelVRowLayout(MelHRowLayout):
	_EDGES = 'top', 'bottom'


class MelHSingleStretchLayout(_AlignedFormLayout):
	'''
	Provides an easy interface to a common layout pattern where a single widget in the
	row/column is stretchy and the others are statically sized.

	Make sure to call setStretchWidget() before calling layout()
	'''
	_stretchWidget = None
	_INSTANCE_VARIABLES = { 'padding': 5,

	                        #if True the layout will expand to fill the layout in the "other" direction.  Ie HLayouts will expand vertically and VLayouts will expand horizontally to the extents of the layout
	                        'expand': False }

	def setStretchWidget( self, widget ):
		if not isinstance( widget, BaseMelUI ):
			widget = BaseMelUI.FromStr( widget )

		self._stretchWidget = widget
		self.layout()
	def layout( self, expand=None ):
		if expand is not None:
			self.expand = expand

		padding = self.padding
		children = self.getChildren()

		stretchWidget = self._stretchWidget
		if stretchWidget is None:
			stretchWidget = children[ 0 ]

		idx = children.index( stretchWidget )

		leftChildren = children[ :idx ]
		rightChildren = children[ idx+1: ]

		edge1, edge2 = self._EDGES
		for n, child in enumerate( leftChildren ):
			if n:
				self( e=True, ac=(child, edge1, padding, children[ n-1 ]) )
			else:
				self( e=True, af=(child, edge1, 0) )

		if rightChildren:
			self( e=True, af=(rightChildren[-1], edge2, 0) )
			for n, child in enumerate( rightChildren[ :-1 ] ):
				self( e=True, ac=(child, edge2, padding, rightChildren[ n+1 ]) )

		if leftChildren and rightChildren:
			self( e=True, ac=((stretchWidget, edge1, padding, leftChildren[-1]), (stretchWidget, edge2, padding, rightChildren[0])) )
		elif leftChildren and not rightChildren:
			self( e=True, ac=(stretchWidget, edge1, padding, leftChildren[-1]), af=(stretchWidget, edge2, 0) )
		elif not leftChildren and rightChildren:
			self( e=True, af=(stretchWidget, edge1, 0), ac=(stretchWidget, edge2, padding, rightChildren[0]) )

		if self.expand:
			self.layoutExpand( children )


class MelVSingleStretchLayout(MelHSingleStretchLayout):
	_EDGES = 'top', 'bottom'

	_INSTANCE_VARIABLES = { 'padding': 5,
	                        'expand': True }


class MelColumnLayout(BaseMelLayout):
	WIDGET_CMD = cmd.columnLayout
	STRETCHY = True

	def __new__( cls, parent, *a, **kw ):
		stretchy = kw.pop( 'adjustableColumn', kw.pop( 'adj', cls.STRETCHY ) )
		kw.setdefault( 'adjustableColumn', stretchy )

		return BaseMelLayout.__new__( cls, parent, *a, **kw )

MelColumn = MelColumnLayout


class MelRowLayout(BaseMelLayout): WIDGET_CMD = cmd.rowLayout
MelRow = MelRowLayout


class MelGridLayout(BaseMelLayout):
	WIDGET_CMD = cmd.gridLayout

	AUTO_GROW = True
	def __new__( cls, parent, **kw ):
		autoGrow = kw.pop( 'autoGrow', self.AUTO_GROW )
		kw.setdefault( 'ag', autoGrow )

		return BaseMelLayout.__new__( cls, parent, **kw )

MelGrid = MelGridLayout


class MelScrollLayout(BaseMelLayout):
	WIDGET_CMD = cmd.scrollLayout

	def __new__( cls, parent, *a, **kw ):
		kw.setdefault( 'childResizable', kw.pop( 'cr', True ) )
		return BaseMelLayout.__new__( cls, parent, *a, **kw )

MelScroll = MelScrollLayout


class MelHScrollLayout(MelScrollLayout):
	_ORIENTATION_ATTR = 'verticalScrollBarThickness'
	def __new__( cls, parent, *a, **kw ):
		kw[ cls._ORIENTATION_ATTR ] = 0
		return MelScrollLayout.__new__( cls, parent, *a, **kw )


class MelVScrollLayout(MelHScrollLayout):
	_ORIENTATION_ATTR = 'horizontalScrollBarThickness'


class MelTabLayout(BaseMelLayout):
	WIDGET_CMD = cmd.tabLayout

	def __init__( self, parent, *a, **kw ):
		BaseMelLayout.__init__( self, parent, *a, **kw )

		ccCB = kw.get( 'changeCommand', kw.get( 'cc', None ) )
		self.setChangeCB( ccCB )

		pscCB = kw.get( 'preSelectCommand', kw.get( 'psc', None ) )
		self.setPreSelectCB( pscCB )

		dccCB = kw.get( 'doubleClickCommand', kw.get( 'dcc', None ) )
		self.setDoubleClickCB( dccCB )
	def numTabs( self ):
		return self( q=True, numberOfChildren=True )
	__len__ = numTabs
	def setLabel( self, idx, label ):
		self( e=True, tabLabelIndex=(idx+1, label) )
	def getLabel( self, idx ):
		self( q=True, tabLabelIndex=idx+1 )
	def getSelectedTab( self ):
		return self( q=True, selectTab=True )
	def setSelectedTab( self, child, executeChangeCB=True ):
		self( e=True, selectTab=child )
		if executeChangeCB:
			self._executeCB( 'selectCommand' )
	def getSelectedTabIdx( self ):
		return self( q=True, selectTabIndex=True )-1  #indices are 1-based...  fuuuuuuu alias!
	def setSelectedTabIdx( self, idx, executeChangeCB=True ):
		self( e=True, selectTabIndex=idx+1 )  #indices are 1-based...  fuuuuuuu alias!
		if executeChangeCB:
			self._executeCB( 'selectCommand' )
	def setChangeCB( self, cb ):
		self.setCB( 'selectCommand', cb )
	def setPreSelectCB( self, cb ):
		self.setCB( 'preSelectCommand', cb )
	def setDoubleClickCB( self, cb ):
		self.setCB( 'doubleClickCommand', cb )


class MelPaneLayout(BaseMelLayout):
	WIDGET_CMD = cmd.paneLayout

	PREF_OPTION_VAR = None

	POSSIBLE_CONFIGS = \
	                 CFG_SINGLE, CFG_HORIZ2, CFG_VERT2, CFG_HORIZ3, CFG_VERT3, CFG_TOP3, CFG_LEFT3, CFG_BOTTOM3, CFG_RIGHT3, CFG_HORIZ4, CFG_VERT4, CFG_TOP4, CFG_LEFT4, CFG_BOTTOM4, CFG_RIGHT4, CFG_QUAD = \
	                 "single", "horizontal2", "vertical2", "horizontal3", "vertical3", "top3", "left3", "bottom3", "right3", "horizontal4", "vertical4", "top4", "left4", "bottom4", "right4", "quad"

	CONFIG = CFG_VERT2

	KWARG_CHANGE_CB_NAME = 'separatorMovedCommand'

	def __init__( self, parent, configuration=None, *a, **kw ):
		kw.setdefault( 'separatorMovedCommand', self.on_resize )

		if configuration is None:
			assert self.CONFIG in self.POSSIBLE_CONFIGS
			configuration = self.CONFIG

		kw[ 'configuration' ] = configuration
		kw.pop( 'cn', None )

		BaseMelLayout.__init__( self, parent, *a, **kw )
		self( e=True, **kw )

		if self.PREF_OPTION_VAR:
			if cmd.optionVar( ex=self.PREF_OPTION_VAR ):
				storedSize = cmd.optionVar( q=self.PREF_OPTION_VAR )
				for idx, size in enumerate( iterBy( storedSize, 2 ) ):
					self.setPaneSize( idx, size )
	def __getitem__( self, idx ):
		idx += 1  #indices are 1-based...  fuuuuuuu alias!
		kw = { 'q': True, 'pane%d' % idx: True }

		return BaseMelUI.FromStr( self( **kw ) )
	def __setitem__( self, idx, ui ):
		idx += 1  #indices are 1-based...  fuuuuuuu alias!
		return self( e=True, setPane=(ui, idx) )
	def getConfiguration( self ):
		return self( q=True, configuration=True )
	def setConfiguration( self, ui ):
		return self( e=True, configuration=ui )
	def getPaneUnderPointer( self ):
		return BaseMelUI.FromStr( self( q=True, paneUnderPointer=True ) )
	def getPaneActive( self ):
		return BaseMelUI.FromStr( self( q=True, activePane=True ) )
	def getPaneActiveIdx( self ):
		return self( q=True, activePaneIndex=True ) - 1  #indices are 1-based...
	def getPaneSize( self, idx ):
		idx += 1
		return self( q=True, paneSize=idx )
	def setPaneSize( self, idx, size ):
		idx += 1
		size = idx, size[0], size[1]

		return self( e=True, paneSize=size )
	def setPaneWidth( self, idx, size ):
		idx += 1
		curSize = self.getPaneSize( idx )
		return self( e=True, paneSize=(idx, curSize[0], size) )
	def setPaneHeight( self, idx, size ):
		idx += 1
		curSize = self.getPaneSize( idx )

		return self( e=True, paneSize=(idx, size, curSize[1]) )

	### EVENT HANDLERS ###
	def on_resize( self, *a ):
		if self.PREF_OPTION_VAR:
			size = self.getPaneSize( 0 )
			cmd.optionVar( clearArray=self.PREF_OPTION_VAR )
			for i in size:
				cmd.optionVar( iva=(self.PREF_OPTION_VAR, i) )


class MelFrameLayout(BaseMelLayout):
	WIDGET_CMD = cmd.frameLayout

	def setCollapseCB( self, cb ):
		BaseMelLayout.setChangeCB( self, cb )
	def getCollapseCB( self ):
		return BaseMelLayout.getChangeCB( self )
	def setExpandCB( self, cb ):
		self.setCB( 'expandCommand', cb )
	def getExpandCB( self ):
		return self.getCB( 'expandCommand' )
	def getCollapse( self ):
		return self( q=True, collapse=True )
	def setCollapse( self, state, executeChangeCB=True ):
		self( e=True, collapse=state )
		if executeChangeCB:
			if state:
				collapseCB = self.getCollapseCB()
				if callable( collapseCB ):
					collapseCB()
			else:
				expandCB = self.getExpandCB()
				if callable( expandCB ):
					expandCB()


class MelShelfLayout(BaseMelLayout):
	WIDGET_CMD = cmd.shelfLayout


class BaseMelWidget(BaseMelUI):
	def setValue( self, value, executeChangeCB=True ):
		try:
			kw = { 'e': True, self.KWARG_VALUE_NAME: value }
			self.WIDGET_CMD( self, **kw )
		except TypeError, x:
			melUtils.printErrorStr( 'Running setValue method using %s command' % self.WIDGET_CMD )
			raise

		if executeChangeCB:
			self._executeCB()
	def getValue( self ):
		kw = { 'q': True, self.KWARG_VALUE_NAME: True }
		return self.WIDGET_CMD( self, **kw )
	def enable( self, state=True ):
		try: self( e=True, enable=bool( state ) )  #explicitly cast here in case we've been passed a non-bool.  the maya.cmds binding interprets any non-boolean object as True it seems...
		except: pass
	def disable( self ):
		self.enable( False )
	def getAnnotation( self ):
		return self( q=True, ann=True )
	def setAnnotation( self, annotation ):
		self( e=True, ann=annotation )
	setEnabled = enable
	def getEnabled( self ):
		try: return self( q=True, enable=True )
		except: return True
	def editable( self, state=True ):
		try: self( e=True, editable=bool( state ) )
		except: pass
	def setEditable( self, state ):
		self.editable( state )
	def getEditable( self ):
		return bool( self( q=True, ed=True ) )
	def setFocus( self ):
		cmd.setFocus( self )


class MelLabel(BaseMelWidget):
	WIDGET_CMD = cmd.text
	KWARG_VALUE_NAME = 'l'
	KWARG_VALUE_LONG_NAME = 'label'

	def bold( self, state=True ):
		self( e=True, font='boldLabelFont' if state else 'plainLabelFont' )
	getLabel = BaseMelWidget.getValue
	setLabel = BaseMelWidget.setValue


class MelSpacer(MelLabel):
	def __new__( cls, parent, w=1, h=1 ):
		w = max( w, 1 )
		h = max( h, 1 )

		return MelLabel.__new__( cls, parent, w=w, h=h, l='' )


class MelButton(BaseMelWidget):
	WIDGET_CMD = cmd.button
	KWARG_CHANGE_CB_NAME = 'c'

	def bold( self, state=True ):
		self( e=True, font='boldLabelFont' if state else 'plainLabelFont' )
	def getLabel( self ):
		return self( q=True, l=True )
	def setLabel( self, label ):
		initialWidth = self.getWidth()
		self( e=True, l=label )

		#seems maya screws with the width of the widget when setting the label - yay!
		self.setWidth( initialWidth )


class _Image(object):
	def setImage( self, imagePath, findInPaths=True ):
		self( e=True, image=str( imagePath ) )
	def getImage( self ):
		return self( q=True, image=True )
	def refresh( self ):
		img = self.getImage()
		self.setImage( '' )
		self.setImage( img )


class MelImage(BaseMelWidget, _Image):
	WIDGET_CMD = cmd.image


class MelIconButton(MelButton, _Image):
	WIDGET_CMD = cmd.iconTextButton


class MelShelfButton(MelIconButton):
	WIDGET_CMD = cmd.shelfButton


class MelIconCheckBox(MelIconButton):
	WIDGET_CMD = cmd.iconTextCheckBox
	KWARG_CHANGE_CB_NAME = 'cc'


class MelCheckBox(BaseMelWidget):
	WIDGET_CMD = cmd.checkBox

	def __new__( cls, parent, *a, **kw ):
		#this craziness is so we can default the label to nothing instead of the widget's name...  dumb, dumb, dumb
		labelArgs = 'l', 'label'
		for f in kw.keys():
			if f == 'label':
				kw[ 'l' ] = kw.pop( 'label' )
				break

		kw.setdefault( 'l', '' )

		return BaseMelWidget.__new__( cls, parent, *a, **kw )


class MelRadioButton(BaseMelWidget):
	WIDGET_CMD = cmd.radioButton

	def getLabel( self ):
		return self( q=True, label=True )
	def setLabel( self, label ):
		self( e=True, label=label )
	def select( self ):
		self( e=True, select=True )
	def isSelected( self ):
		return self( q=True, select=True )
	getValue = isSelected


class MelRadioCollection(unicode):
	WIDGET_CMD = cmd.radioCollection
	BUTTON_CLS = MelRadioButton

	def __new__( cls ):
		new = unicode.__new__( cls, cls.WIDGET_CMD() )
		new._items = []

		return new
	def addButton( self, button ):
		'''
		adds the given button to this collection
		'''
		self._items.append( button( e=True, collection=self ) )
	def createButton( self, parent, *a, **kw ):
		'''
		creates a new radio button and adds it to the collection
		'''
		button = self.BUTTON_CLS( parent, collection=self, *a, **kw )
		self._items.append( button )

		return button
	def getItems( self ):
		'''
		returns the radio buttons in the collection
		'''
		return self._items[:]
	def count( self ):
		'''
		returns the items in the collection
		'''
		return len( self._items )
	def getSelected( self ):
		'''
		returns the selected MelRadio button instance
		'''
		selItemStr = self.WIDGET_CMD( self, q=True, sl=True )
		for item in self._items:
			if str( item ) == selItemStr:
				return item
			
class MelIconRadioButton(BaseMelWidget, _Image):
	WIDGET_CMD = cmd.iconTextRadioButton


class MelIconRadioCollection(MelRadioCollection):
	WIDGET_CMD = cmd.iconTextRadioCollection
	BUTTON_CLS = MelIconRadioButton


class MelSeparator(BaseMelWidget):
	WIDGET_CMD = cmd.separator


class MelIntField(BaseMelWidget):
	WIDGET_CMD = cmd.intField
	DEFAULT_WIDTH = 30


class MelFloatField(BaseMelWidget): WIDGET_CMD = cmd.floatField
class MelTextField(BaseMelWidget):
	WIDGET_CMD = cmd.textField
	DEFAULT_WIDTH = 150
	KWARG_VALUE_NAME = 'tx'
	KWARG_VALUE_LONG_NAME = 'text'

	def setValue( self, value, executeChangeCB=True ):
		if not isinstance( value, unicode ):
			value = unicode( value )

		BaseMelWidget.setValue( self, value, executeChangeCB )
	def clear( self, executeChangeCB=True ):
		self.setValue( '', executeChangeCB )


class MelTextScrollField(MelTextField):
	WIDGET_CMD = cmd.scrollField


class MelScrollField(MelTextField):
	WIDGET_CMD = cmd.scrollField


class MelNameField(MelTextField):
	WIDGET_CMD = cmd.nameField

	def getValue( self ):
		obj = self( q=True, o=True )
		if obj:
			return obj

		return None
	getObj = getValue
	def setValue( self, obj, executeChangeCB=True ):
		if not isinstance( obj, basestring ):
			obj = str( obj )

		self( e=True, o=obj )

		if executeChangeCB:
			self._executeCB()
	setObj = setValue
	def clear( self ):
		self.setValue( None )


class MelPalette(BaseMelWidget):
	WIDGET_CMD = cmd.palettePort

	def setColour( self, colour, cell=0 ):
		val = [cell] + list( colour )[:3]
		self( e=True, rgb=val, redraw=True )
	setColor = setColour
	def getColour( self, cell=0 ):
		self( setCurCell=cell )
		return self( q=True, rgb=True )
	getColor = getColour


class MelObjectSelector(MelFormLayout):
	def __new__( cls, parent, label='Node->', obj=None, labelWidth=None ):
		return MelFormLayout.__new__( cls, parent )
	def __init__( self, parent, label='Node->', obj=None, labelWidth=None ):
		MelFormLayout.__init__( self, parent )

		self.UI_label = MelButton( self, l=label, c=self.on_setValue )
		self.UI_obj = MelNameField( self )

		if labelWidth is not None:
			self.UI_label.setWidth( labelWidth )

		if obj is not None:
			self.UI_obj.setValue( obj )

		self( e=True,
		      af=((self.UI_label, 'left', 0),
		          (self.UI_obj, 'right', 0)),
		      ac=((self.UI_obj, 'left', 0, self.UI_label)) )

		self.UI_menu = MelPopupMenu( self.UI_label, pmc=self.buildMenu )
		self.UI_menu = MelPopupMenu( self.UI_obj, pmc=self.buildMenu )
	def buildMenu( self, menu, menuParent ):
		cmd.menu( menu, e=True, dai=True )

		obj = self.getValue()
		enabled = cmd.objExists( obj ) if obj else False
		MelMenuItem( menu, label='select obj', en=enabled, c=self.on_select )
		MelMenuItemDiv( menu )
		MelMenuItem( menu, label='clear obj', c=self.on_clear )
	def getValue( self ):
		return self.UI_obj.getValue()
	def setValue( self, value, executeChangeCB=True ):
		return self.UI_obj.setValue( value, executeChangeCB )
	def setChangeCB( self, cb ):
		return self.UI_obj.setChangeCB( cb )
	def getChangeCB( self ):
		return self.UI_obj.getChangeCB()
	def clear( self ):
		self.UI_obj.clear()
	def getLabel( self ):
		return self.UI_label.getValue()
	def setLabel( self, label ):
		self.UI_label.setValue( label )

	### EVENT HANDLERS ###
	def on_setValue( self, *a ):
		sel = cmd.ls( sl=True )
		if sel:
			self.setValue( sel[ 0 ] )
	def on_select( self, *a ):
		cmd.select( self.getValue() )
	def on_clear( self, *a ):
		self.clear()


class _BaseSlider(BaseMelWidget):
	DISABLE_UNDO_ON_DRAG = False

	def __new__( cls, parent, minValue=0, maxValue=100, defaultValue=None, *a, **kw ):
		changeCB = kw.pop( 'changeCommand', kw.pop( 'cc', None ) )
		dragCB = kw.pop( 'dragCommand', kw.pop( 'dc', None ) )

		new = BaseMelWidget.__new__( cls, parent, minValue=minValue, maxValue=maxValue, *a, **kw )

		new._isDragging = False

		new._preChangeCB = None
		new._postChangeCB = None
		new._changeCB = changeCB

		return new
	def __init__( self, parent, minValue=0, maxValue=100, defaultValue=None, *a, **kw ):
		BaseMelWidget.__init__( self, parent, *a, **kw )

		kw = {}
		kw[ 'changeCommand' ] = self.on_change
		kw[ 'dragCommand' ] = self.on_drag

		self( e=True, **kw )

		self._defaultValue = defaultValue
		self._initialUndoState = cmd.undoInfo( q=True, state=True )
	def setPreChangeCB( self, cb ):
		'''
		the callback executed when the slider is first pressed.  the preChangeCB should take no args
		'''
		self._preChangeCB = cb
	def getPreChangeCB( self ):
		return self._preChangeCB
	def setChangeCB( self, cb ):
		'''
		the callback that is executed when the value is changed.  the changeCB should take a single value arg
		'''
		self._changeCB = cb
	def getChangeCB( self ):
		return self._changeCB
	def setPostChangeCB( self, cb ):
		'''
		the callback executed when the slider is released.  the postChangeCB should take a single value arg just like the changeCB
		'''
		self._postChangeCB = cb
	def getPostChangeCB( self ):
		return self._postChangeCB
	def reset( self, executeChangeCB=True ):
		value = self._defaultValue
		if value is None:
			value = self( q=True, min=True )

		self.setValue( value, executeChangeCB )

	### EVENT HANDLERS ###
	def on_change( self, value ):
		self._isDragging = False

		#restore undo if thats what we need to do
		if self.DISABLE_UNDO_ON_DRAG:
			if self._initialUndoState:
				cmd.undoInfo( stateWithoutFlush=True )

		if callable( self._postChangeCB ):
			self._postChangeCB( value )
	def on_drag( self, value ):
		if self._isDragging:
			if callable( self._changeCB ):
				self._changeCB( value )
		else:
			self._initialUndoState = cmd.undoInfo( q=True, state=True )
			if self.DISABLE_UNDO_ON_DRAG:
				cmd.undoInfo( stateWithoutFlush=False )

			if callable( self._preChangeCB ):
				self._preChangeCB()

			self._isDragging = True


class MelFloatSlider(_BaseSlider):
	WIDGET_CMD = cmd.floatSlider


class MelIntSlider(_BaseSlider):
	WIDGET_CMD = cmd.intSlider


class MelTextScrollList(BaseMelWidget):
	'''
	NOTE: you probably want to use the MelObjectScrollList instead!
	'''

	WIDGET_CMD = cmd.textScrollList
	KWARG_CHANGE_CB_NAME = 'sc'

	ALLOW_MULTI_SELECTION = False

	def __new__( cls, parent, *a, **kw ):
		if 'ams' not in kw and 'allowMultiSelection' not in kw:
			kw[ 'ams' ] = cls.ALLOW_MULTI_SELECTION

		return BaseMelWidget.__new__( cls, parent, *a, **kw )
	def __init__( self, parent, *a, **kw ):
		BaseMelWidget.__init__( self, parent, *a, **kw )

		self._appendCB = None
	def __getitem__( self, idx ):
		return self.getItems()[ idx ]
	def __contains__( self, value ):
		return value in self.getItems()
	def __len__( self ):
		return self( q=True, numberOfItems=True )
	def setItems( self, items ):
		self.clear()
		for i in items:
			self.append( i )
	def getItems( self ):
		return self( q=True, ai=True )
	def getAllItems( self ):
		return self( q=True, ai=True )
	def setAppendCB( self, cb ):
		self._appendCB = cb
	def getSelectedItems( self ):
		return self( q=True, si=True ) or []
	def getSelectedIdxs( self ):
		return [ idx-1 for idx in self( q=True, sii=True ) or [] ]
	def selectByIdx( self, idx, executeChangeCB=False ):
		self( e=True, selectIndexedItem=idx+1 )  #indices are 1-based in mel land - fuuuuuuu alias!!!
		if executeChangeCB:
			self._executeCB()
	def attemptToSelect( self, idx, executeChangeCB=False ):
		'''
		attempts to select the item at index idx - if the specific index doesn't exist,
		it tries to select the closest item to the given index
		'''
		if len( self ) == 0:
			if executeChangeCB:
				self._executeCB()

			return

		if idx >= len( self ):
			idx = len( self ) - 1  #set to the end most item

		if idx < 0:
			idx = 0

		self.selectByIdx( idx, executeChangeCB )
	def selectByValue( self, value, executeChangeCB=False ):
		self( e=True, selectItem=value )
		if executeChangeCB:
			self._executeCB()
	def append( self, item ):
		self( e=True, append=item )
	def appendItems( self, items ):
		for i in items: self.append( i )
	def removeByIdx( self, idx ):
		self( e=True, removeIndexedItem=idx+1 )
	def removeByValue( self, value ):
		self( e=True, removeItem=value )
	def removeSelectedItems( self ):
		for idx in self.getSelectedIdxs():
			self.removeByIdx( idx )
	def allowMultiSelect( self, state ):
		self( e=True, ams=state )
	def clear( self ):
		self( e=True, ra=True )
	def clearSelection( self, executeChangeCB=False ):
		self( e=True, deselectAll=True )
		if executeChangeCB:
			self._executeCB()
	def moveSelectedItemsUp( self, count=1 ):
		'''
		moves selected items "up" <count> units
		'''

		#these are the selected items as they appear in the UI - we need to map them to "real" indices
		selIdxs = self.getSelectedIdxs()
		selItems = self.getSelectedItems()
		items = self.getAllItems()
		realIdxs = []
		for selItem in selItems:
			for n, item in enumerate( items ):
				if selItem is item:
					realIdxs.append( n )
					break

		count = min( count, realIdxs[ 0 ] )  #we can't move more units up than the smallest selected index
		if not count:
			return

		realIdxs.sort()
		for idx in realIdxs:
			item = items.pop( idx )
			items.insert( idx-count, item )

		self.setItems( items )

		#re-setup selection
		self.clearSelection()
		for item in selItems:
			self.selectByValue( item, False )
	def moveSelectedItemsDown( self, count=1 ):
		'''
		moves selected items "down" <count> units
		'''

		#these are the selected items as they appear in the UI - we need to map them to "real" indices
		selIdxs = self.getSelectedIdxs()
		selItems = self.getSelectedItems()
		items = self.getAllItems()
		realIdxs = []
		for selItem in selItems:
			for n, item in enumerate( items ):
				if selItem is item:
					realIdxs.append( n )
					break

		realIdxs.sort()
		maxIdx = len( items )-1
		count = min( count, maxIdx - realIdxs[-1] )  #we can't move more units down than the largest selected index
		if not count:
			return

		realIdxs.reverse()
		for idx in realIdxs:
			item = items.pop( idx )
			items.insert( idx+count, item )

		self.setItems( items )

		#re-setup selection
		self.clearSelection()
		for item in selItems:
			self.selectByValue( item, False )


class MelObjectScrollList(MelTextScrollList):
	'''
	Unlike MelTextScrollList, this class will actually store and return python objects and display them using either
	their native string representation (ie __str__) which is done by passing the object to itemAsStr which is an
	overridable instance method.  It also lets you set selection by passing either python objects, the string
	representations for those objects or indices.

	It also provides the ability to set filters on the data.  What the widget stores and what it displays can be
	different, making it easy to write UI to access internal data without having to write glue code to convert
	to/from UI representation.

	NOTE: you almost always want to use this class over the MelTextScrollList class...  its just better.
	'''

	#if true the objects are displayed without their namespaces
	DISPLAY_NAMESPACES = False
	DISPLAY_NICE_NAMES = False

	#should we perform caseless filtering?
	FILTER_CASELESS = True

	def __init__( self, parent, *a, **kw ):
		MelTextScrollList.__init__( self, parent, *a, **kw )

		self._items = []
		self._visibleItems = []
		self._filterStr = None
		self._compiledFilter = None
	def __contains__( self, item ):
		return item in self._visibleItems
	def itemAsStr( self, item ):
		itemStr = str( item )
		if not self.DISPLAY_NAMESPACES:
			withoutNamespace = str( item ).split( ':' )[ -1 ]
			itemStr = withoutNamespace.split( '|' )[ -1 ]

		if self.DISPLAY_NICE_NAMES:
			itemStr = names.camelCaseToNice( itemStr )

		return itemStr
	def getFilter( self ):
		return self._filterStr
	def setFilter( self, filterStr, updateUI=True ):
		if not filterStr:
			self._filterStr = None
			self._compiledFilter = None
		else:
			self._filterStr = filterStr

			#build the compiled regular expression
			reArgs = [ filterStr ]
			if self.FILTER_CASELESS:
				reArgs.append( re.IGNORECASE )

			self._compiledFilter = re.compile( *reArgs )

		#update the UI
		if updateUI:
			self.update()
	def clearFilter( self ):
		self.setFilter( None )
	def doesItemPassFilter( self, item ):
		return self.doesItemStrPassFilter( self.itemAsStr( item ) )
	def doesItemStrPassFilter( self, itemStr ):
		if not self._filterStr:
			return True

		if self.FILTER_CASELESS:
			itemStr = itemStr.lower()

		if self._filterStr in itemStr:
			return True

		if self._compiledFilter is None:
			return True

		try:
			if self._compiledFilter.match( itemStr ):
				return True
		except: return True

		return False
	def getItems( self ):
		'''
		returns the list of visible items
		NOTE: if the widget has a filter set, this won't return ALL items, just
		the visible ones.  To get a list of all items, use getAllItems()
		'''
		return self._visibleItems[:]  #return a copy of the visible items list
	def getAllItems( self ):
		return self._items[:]  #return a copy of the items list
	def getSelectedItems( self ):
		selectedIdxs = self.getSelectedIdxs()
		return [ self._visibleItems[ idx ] for idx in selectedIdxs ]
	def selectByValue( self, value, executeChangeCB=False ):
		if value in self._visibleItems:
			idx = self._visibleItems.index( value ) + 1  #mel indices are 1-based...
			self( e=True, sii=idx )
		else:
			valueStr = self.itemAsStr( value )
			for idx, item in enumerate( self._visibleItems ):
				if self.itemAsStr( item ) == valueStr:
					self( e=True, sii=idx+1 )  #mel indices are 1-based...

		if executeChangeCB:
			self._executeCB()
	def selectItems( self, items, executeChangeCB=False ):
		'''
		provides an efficient way of selecting many items at once
		'''
		visibleSet = set( self._visibleItems )
		itemsSet = set( items )

		#get a list of items that are guaranteed to be in the UI
		itemsToSelect = itemsSet.intersection( visibleSet )
		for idx, item in enumerate( self._visibleItems ):
			if item in itemsToSelect:
				self( e=True, sii=idx+1 )

		if executeChangeCB:
			self._executeCB()
	def append( self, item, executeAppendCB=True ):
		self._items.append( item )

		itemStr = self.itemAsStr( item )
		if self.doesItemStrPassFilter( itemStr ):
			self._visibleItems.append( item )
			self( e=True, append=itemStr )

		if executeAppendCB:
			if callable( self._appendCB ):
				self._appendCB( item )
	def removeByIdx( self, idx ):
		'''
		removes an item by its index in the visible list of items
		'''

		#first pop the item out of the list of visible items
		item = self._visibleItems.pop( idx )
		self( e=True, removeIndexedItem=idx+1 )

		#now pop the item out of the _items list
		idx = self._items.index( item )
		self._items.pop( idx )
	def removeByValue( self, value ):
		if value in self._items:
			idx = self._items.index( value )
			self._items.pop( idx )

			if value in self._visibleItems:
				idx = self._visibleItems.index( value )
				self._visibleItems.pop( idx )
				self( e=True, rii=idx+1 )  #mel indices are 1-based...
		else:
			valueStr = self.itemAsStr( value )
			for itemList in (self._visibleItems, self._items):
				for idx, item in enumerate( itemList ):
					if self.itemAsStr( item ) == valueStr:
						itemList.pop( idx )
						self( e=True, rii=idx+1 )  #mel indices are 1-based...
	def clear( self ):
		self._items = []
		self._visibleItems = []
		self( e=True, ra=True )
	def update( self, maintainSelection=True ):
		'''
		removes and re-adds the items in the UI
		'''
		selItems = self.getSelectedItems()

		#remove all items from the list
		self._visibleItems = []
		self( e=True, ra=True )

		#now re-generate their string representations
		for item in self.getAllItems():
			itemStr = self.itemAsStr( item )
			if self.doesItemStrPassFilter( itemStr ):
				self._visibleItems.append( item )
				self( e=True, append=itemStr )

		if maintainSelection:
			for item in selItems:
				for idx, visItem in enumerate( self._visibleItems ):
					if item is visItem:
						self.selectByIdx( idx, False )


class MelSetMemebershipList(MelObjectScrollList):
	ALLOWED_NODE_TYPES = None  #if None then ANY node type is allowed in the set - otherwise only types in the iterable are allowed to be added to the set
	ALLOW_MULTI_SELECTION = True

	def __init__( self, parent, **kw ):
		MelObjectScrollList.__init__( self, parent, **kw )
		self.objectSets = []
		self( e=True, dcc=self.on_doubleClickItem )
		self.POP_ops = MelPopupMenu( self, pmc=self.buildMenu )

		self._addHandler = None
	def getSets( self ):
		return self.objectSets[:]
	def setSets( self, objectSets ):
		if not isinstance( objectSets, list ):
			objectSets = [ objectSets ]

		self.objectSets = objectSets
		self.update()
	def getAllItems( self ):
		items = cmd.sets( self.objectSets, q=True ) or []
		items.sort()

		return removeDupes( items )
	def _addItems( self, items ):
		handler = self._addHandler
		isHandlerCallable = callable( self._addHandler )

		items = self.filterItems( items )
		if items:
			for objectSet in self.objectSets:
				if isHandlerCallable:
					handler( objectSet, items )
				else:
					cmd.sets( items, add=objectSet )

		self.update()
	def _setItems( self, items ):
		items = self.filterItems( items )
		if items:
			for objectSet in self.objectSets:
				cmd.sets( clear=objectSet )

		self._addItems( items )
	def _removeItems( self, items ):
		if items:
			for objectSet in self.objectSets:
				cmd.sets( items, remove=objectSet )


		self.update()
	def _removeAllItems( self ):
		for objectSet in self.objectSets:
			cmd.sets( clear=objectSet )

		self.update()
	def buildMenu( self, menu, menuParent ):
		cmd.menu( menu, e=True, dai=True )
		MelMenuItem( menu, l='ADD selected objects to set', c=self.on_addItem )
		MelMenuItem( menu, l='REPLACE set items with selected objects', c=self.on_replaceItem )
		MelMenuItem( menu, l='REMOVE selected objects from set', c=self.on_removeItem )
		MelMenuItemDiv( menu )
		MelMenuItem( menu, l='remove HIGHLIGHTED objects from set', c=self.on_removeHighlighted )
		MelMenuItemDiv( menu )
		MelMenuItem( menu, l='SELECT highlighted objects', c=self.on_doubleClickItem )
		MelMenuItemDiv( menu )
		MelMenuItem( menu, l='update UI', c=self.on_update )
		MelMenuItem( menu, cb=self.DISPLAY_NAMESPACES, l='Show Namespaces', c=self.on_showNameSpaces )
		MelMenuItem( menu, cb=self.DISPLAY_NICE_NAMES, l='Show Nice Names', c=self.on_showNiceNames )
	def removeItems( self, items ):
		curItems = self.getItems()
		if curItems:
			newItems = curItems.difference( items )
			if len( curItems ) == len( newItems ):
				return

			self.setItems( newItems )
	def filterItems( self, items ):
		if not self.ALLOWED_NODE_TYPES:
			return items

		filteredItems = []
		for item in items:
			if nodeType in self.ALLOWED_NODE_TYPES:
				if cmd.objectType( item, isAType=nodeType ):
					filteredItems.append( item )

		return filteredItems

	### EVENT HANDLERS ###
	def on_doubleClickItem( self, *a ):
		sel = self.getSelectedItems()
		if sel:
			cmd.select( sel )
	def on_addItem( self, *a ):
		self._addItems( cmd.ls( sl=True ) )
	def on_replaceItem( self, *a ):
		self._setItems( cmd.ls( sl=True ) )
	def on_removeItem( self, *a ):
		self._removeItems( cmd.ls( sl=True ) )
	def on_removeHighlighted( self, *a ):
		self._removeItems( self.getSelectedItems() )
	def on_update( self, *a ):
		self.update()
	def on_showNameSpaces( self, *a ):
		self.DISPLAY_NAMESPACES = not self.DISPLAY_NAMESPACES
		self.update()
	def on_showNiceNames( self, *a ):
		self.DISPLAY_NICE_NAMES = not self.DISPLAY_NICE_NAMES
		self.update()


class MelTreeView(BaseMelWidget):
	'''
	Thanks to Dave Shaw for the majority of this implementation
	'''
	WIDGET_CMD = cmd.treeView

	#the valid button "types"
	BUTTON_TYPES = BT_PUSH_BUTTON, BT_2STATE, BT_3STATE = 'pushButton', '2StateButton', '3StateButton'

	#the valid button "states"
	BUTTON_STATES = BS_UP, BS_DOWN, BS_BETWEEN = 'buttonUp', 'buttonDown', 'buttonThirdState'

	def __init__( self, parent, *a, **kw ):
		BaseMelWidget.__init__( self, parent, *a, **kw )

		self( e=True, **kw )
		self._pressCBs = {}
	def addItem( self, itemName, itemParent=None ):
		self( edit=True, addItem=(itemName, itemParent) )
	def doesItemExist( self, itemName ):
		return self( q=True, itemExists=itemName )
	def getItemIndex( self, itemName ):
		return self( q=True, itemIndex=itemName )
	def getItemParent( self, itemName ):
		return self( q=True, itemParent=itemName )
	def isItemSelected( self, itemName ):
		return self( q=True, itemSelected=itemName )
	def setButtonLabel( self, itemName, buttonIndex, label ):
		self( e=True, buttonTextIcon=(itemName, buttonIndex, label) )
	def setButtonState( self, itemName, buttonIndex, state ):
		'''
		There are only 3 valid states:
		buttonUp - button is up
		buttonDown - button is down
		buttonThirdState - button is in state three (used by the "3StateButton" button style)
		'''
		if state not in self.BUTTON_STATES:
			raise TypeError( "Invalid button state: %s" % state )

		self( e=True, buttonState=(a_item, a_button, a_state) )
	def setButtonStyle( self, itemName, buttonIndex, style ):
		'''
		Possible button types:
		pushButton - two possible states, button is reset to up upon release
		2StateButton - two possible states, button changes state on click
		3StateButton - three button states, button changes state on click
		'''
		if style not in self.BUTTON_TYPES:
			raise TypeError( "Invalid button style: %s" % style )

		self( e=True, buttonStyle=(itemName, buttonIndex, style) )
	def removeAll( self ):
		self( e=True, removeAll=True )
	def setPressCommand( self, buttonIndex, cb ):
		'''
		Sets the python callback function to be invoked when the button at <buttonIndex> is pressed.  The callback should
		take two args - the first is the itemName that the button pressed belongs to, and the second is the button press state
		that has just been activated
		'''

		#generate a likely unique name for a global proc - treeView press commands have to be mel proc names and can't be python
		#callbacks.  This hack makes it easier to work with tree view callbacks and keep everything in python
		melCmdName = '__%s_pressCB%d' % (self, buttonIndex)

		#construct the mel proc
		melCmd = """global proc %s( string $str, int $index ) {
		python( "from zooPyMaya import baseMelUI; baseMelUI.BaseMelUI.FromStr( '%s' )._executePressCB( %d, '"+ $str +"', "+ $index +" );" );
		}""" % (melCmdName, self, buttonIndex)

		#execute the proc we just constructed
		maya.mel.eval( melCmd )

		#store the python function we want to execute - NOTE: the function needs to take 3 args: func( str, int ) - see treeView docs for details
		self._pressCBs[ buttonIndex ] = cb

		#tell the widget what its press callback is...
		self( e=True, pressCommand=(buttonIndex, melCmdName) )
	def getPressCommand( self, buttonIndex ):
		try:
			return self._pressCBs[ buttonIndex ]
		except KeyError:
			return None
	def _executePressCB( self, a_button, *a ):
		self._pressCBs[ a_button ]( *a )
	def getItemChildren( self, itemName ):
		return self( q=True, children=itemName )
	def clearSelection( self ):
		self( e=True, clearSelection=True )


class _MelBaseMenu(BaseMelWidget):
	DYNAMIC = False

	KWARG_VALUE_NAME = 'l'
	KWARG_VALUE_LONG_NAME = 'label'

	KWARG_CHANGE_CB_NAME = 'pmc'

	DEFAULT_WIDTH = None
	DEFAULT_HEIGHT = None

	STATIC_CHOICES = []  #if you populate this variable you'll have the options automatically appear in the list unless its a DYNAMIC menu

	def __init__( self, parent, *a, **kw ):
		super( _MelBaseMenu, self ).__init__( parent, *a, **kw )
		if self.DYNAMIC:
			if 'pmc' not in kw and 'postMenuCommand' not in kw:  #make sure there isn't a pmc passed in
				self( e=True, pmc=self._build )
		else:
			for item in self.STATIC_CHOICES:
				self.append( item )
	def __len__( self ):
		return self( q=True, numberOfItems=True )
	def __contains__( self, item ):
		return item in self.getItems()
	def _build( self, menu, menuParent ):
		'''
		converts the menu and menuParent args into proper MelXXX instance
		'''
		menu = BaseMelWidget.FromStr( menu )  #this should be the same as "self"...
		menuParent = BaseMelWidget.FromStr( menuParent )

		self.build( menu, menuParent )
	def build( self, menu, menuParent ):
		pass
	def getMenuItems( self ):
		itemNames = self( q=True, itemArray=True ) or []
		return [ MelMenuItem.FromStr( itemName ) for itemName in itemNames ]
	def getItems( self ):
		return [ menuItem.getValue() for menuItem in self.getMenuItems() ]
	def append( self, strToAppend ):
		return MelMenuItem( self, label=strToAppend )
	def clear( self ):
		for menuItem in self.getMenuItems():
			cmd.deleteUI( menuItem )


class MelMenu(_MelBaseMenu):
	WIDGET_CMD = cmd.menu
	DYNAMIC = True
	_DEFAULT_MENU_PARENT = None

	def __new__( cls, *a, **kw ):
		return _MelBaseMenu.__new__( cls, cls._DEFAULT_MENU_PARENT, *a, **kw )
	def __init__( self, *a, **kw ):
		super( _MelBaseMenu, self ).__init__( self._DEFAULT_MENU_PARENT, *a, **kw )
		if self.DYNAMIC:
			if 'pmc' not in kw and 'postMenuCommand' not in kw:  #make sure there isn't a pmc passed in
				self( e=True, pmc=self._build )
	def iterParents( self ):
		return iter([])
	def getFullName( self ):
		return str( self )
	def _build( self, *a ):
		self.build()
	def build( self, *a ):
		pass
	def clear( self ):
		_MelBaseMenu.clear( self )
		self( e=True, dai=True )


class MelMainMenu(MelMenu):
	'''
	creates a new menu parented to the maya main window
	'''

	_DEFAULT_MENU_PARENT = 'MayaWindow'


class MelOptionMenu(_MelBaseMenu):
	WIDGET_CMD = cmd.optionMenu

	KWARG_VALUE_NAME = 'v'
	KWARG_VALUE_LONG_NAME = 'value'
	KWARG_CHANGE_CB_NAME = 'cc'

	DYNAMIC = False

	def __getitem__( self, idx ):
		return self.getItems()[ idx ]
	def __setitem__( self, idx, value ):
		menuItems = self.getMenuItems()
		menuItems[ idx ].setValue( value )
	def getMenuItems( self ):
		itemNames = self( q=True, itemListShort=True ) or []
		return [ MelMenuItem.FromStr( itemName ) for itemName in itemNames ]
	def selectByIdx( self, idx, executeChangeCB=True ):
		self( e=True, select=idx+1 )  #indices are 1-based in mel land - fuuuuuuu alias!!!
		if executeChangeCB:
			self._executeCB()
	def selectByValue( self, value, executeChangeCB=True ):
		idx = self.getItems().index( value )
		self.selectByIdx( idx, executeChangeCB )
	def setValue( self, value, executeChangeCB=True ):
		self.selectByValue( value, executeChangeCB )
	def getSelectedIdx( self ):
		return self( q=True, select=True ) - 1  #indices are 1-based in mel land - fuuuuuuu alias!!!


class MelObjectMenu(MelOptionMenu):
	def __new__( cls, parent, *a, **kw ):
		new = MelOptionMenu.__new__( cls, parent, *a, **kw )
		new._objs = []

		return new
	def _itemAsStr( self, item ):
		return str( item )
	def __setitem__( self, idx, value ):
		menuItems = self.getMenuItems()
		menuItems[ idx ].setValue( self._itemAsStr( value ) )
	def append( self, obj ):
		MelOptionMenu.append( self, obj )
		self._objs.append( obj )
	def getItems( self ):
		return self._objs
	def clear( self ):
		MelOptionMenu.clear( self )
		self._objs = []


class MelPopupMenu(_MelBaseMenu):
	WIDGET_CMD = cmd.popupMenu
	DYNAMIC = True

	def iterParents( self ):
		return iter([])
	def getFullName( self ):
		return str( self )
	def clear( self ):
		self( e=True, dai=True )  #clear the menu


class MelMenuItem(BaseMelWidget):
	WIDGET_CMD = cmd.menuItem

	KWARG_VALUE_NAME = 'l'
	KWARG_VALUE_LONG_NAME = 'label'

	KWARG_CHANGE_CB_NAME = 'pmc'

	DEFAULT_WIDTH = None
	DEFAULT_HEIGHT = None

	def iterParents( self ):
		return iter([])
	def getFullName( self ):
		return str( self )
	
class MelRadioMenuButton(MelMenuItem):
	WIDGET_CMD = cmd.menuItem

	def getLabel( self ):
		return self( q=True, label=True )
	def setLabel( self, label ):
		self( e=True, label=label )
	def select( self ):
		self( e=True, select=True )
	def isSelected( self ):
		return self( q=True, select=True )
	getValue = isSelected


class MelRadioMenuCollection(unicode):
	WIDGET_CMD = cmd.radioMenuItemCollection
	BUTTON_CLS = MelRadioMenuButton

	def __new__( cls ):
		new = unicode.__new__( cls, cls.WIDGET_CMD() )
		new._items = []

		return new
	def addButton( self, button ):
		'''
		adds the given button to this collection
		'''
		self._items.append( button( e=True, collection=self ) )
	def createButton( self, parent, *a, **kw ):
		'''
		creates a new radio button and adds it to the collection
		'''
		button = self.BUTTON_CLS( parent, collection=self, *a, **kw )
		self._items.append( button )

		return button
	def getItems( self ):
		'''
		returns the radio buttons in the collection
		'''
		return self._items[:]
	def count( self ):
		'''
		returns the items in the collection
		'''
		return len( self._items )
	def getSelected( self ):
		'''
		returns the selected MelRadio button instance
		'''
		selItemStr = self.WIDGET_CMD( self, q=True, sl=True )
		for item in self._items:
			if str( item ) == selItemStr:
				return item

class MelMenuItemDiv(MelMenuItem):
	def __new__( cls, parent, *a, **kw ):
		kw[ 'divider' ] = True
		return super( MelMenuItemDiv, cls ).__new__( cls, parent, *a, **kw )


class MelIteratorUI(object):
	def __init__( self, iterableObject, maxRange=None, **kw ):
		self.progress = 0
		self.items = iterableObject
		if maxRange is None:
			maxRange = len( iterableObject )

		self._maxRange = maxRange

		cmd.progressWindow( progress=0, isInterruptable=True, minValue=0, maxValue=maxRange, **kw )
	def __iter__( self ):
		progressWindow = cmd.progressWindow

		maxRange = self._maxRange
		progress = 0

		try:
			for item in self.items:
				yield item

				if progressWindow( q=True, ic=True ):
					return

				progress += 1
				progressWindow( e=True, progress=progress )
		finally:
			self.close()
	def __del__( self ):
		self.close()
	def isCancelled( self ):
		return cmd.progressWindow( q=True, ic=True )
	def close( self ):
		cmd.progressWindow( e=True, ep=True )


def makePathSceneRelative( filepath ):
		#make sure it is actually an absolute path...
		if filepath.isAbs():
			curSceneDir = Path( cmd.file( q=True, sn=True ) ).up()
			filepath = filepath - curSceneDir

		return filepath


def buildLabelledWidget( parent, label, labelWidth, WidgetClass, *a, **kw ):
	layout = MelHSingleStretchLayout( parent )
	lblKw = { 'align': 'left' }
	if label:
		lblKw[ 'l' ] = label

	if labelWidth:
		lblKw[ 'w' ] = labelWidth

	lbl = MelLabel( layout, **lblKw )
	ui = WidgetClass( layout, *a, **kw )

	layout.setStretchWidget( ui )
	layout.layout()

	return ui, lbl, layout


def labelledUIClassFactory( baseCls ):
	'''
	this class factory creates "labelled" widget classes.  a labelled widget class acts just like the baseCls instance except
	that it has a label

	NOTE: the following constructor keywords can be used:
		llabel, ll			sets the text label for the widget
		llabelWidth, llw	sets the label width
		llabelAlign, lla	sets the label alignment

		the keyword "label" isn't used because the class might be wrapping a widget that validly has a label such as MelButton or MelCheckbox
	'''
	clsName = 'Labelled%s' % baseCls.__name__.replace( 'Mel', '' )
	class _tmp(MelHSingleStretchLayout):
		_IS_SETUP = False

		def __new__( cls, parent, *a, **kw ):

			#extract any specific keywords from the dict before setting up the instance
			label = kw.pop( 'llabel', kw.pop( 'll', '<-no label->' ) )
			labelWidth = kw.pop( 'llabelWidth', kw.pop( 'llw', None ) )
			labelAlign = kw.pop( 'llabelAlign', kw.pop( 'lla', 'left' ) )

			self = MelHSingleStretchLayout.__new__( cls, parent )

			self.UI_lbl = lbl = MelLabel( self, l=label, align=labelAlign )
			if labelWidth:
				lbl.setWidth( labelWidth )

			self.ui = ui = baseCls( self, *a, **kw )

			self.setStretchWidget( ui )
			self.layout()
			self( e=True, af=((lbl, 'top', 0), (lbl, 'bottom', 0)) )

			#these functions are built within the constructor scope for a few reasons
			#first we get access to the ui object without having to go via a __getattr__ call
			#second we can't put all the functionality into the __getattr__ and __setattr__ methods on the _tmp class because they will interfere with the super class' constructor (where most of the work is done)
			#so basically construct these functions here and store them as _get and _set, and have the real __getattr__ and __setattr__ methods look for them once the instance has been properly constructed
			def _get( self, attr ):
				if attr in self.__dict__:
					return self.__dict__[ attr ]

				val = getattr( ui, attr, None )
				if val is None:
					raise AttributeError( "No attribute '%s' was found on the object or its '%s' widget member" % (attr, baseCls) )

				return val
			def _set( self, attr, value ):
				if attr in self.__dict__:
					setattr( self, attr, value )

				setattr( ui, attr, value )

			self._get = _get
			self._set = _set
			self._IS_SETUP = True

			return self
		def __getattr__( self, attr ):
			if self._IS_SETUP:
				return self._get( self, attr )

			return super( MelHSingleStretchLayout, self ).__getattr__( attr )
		def __setattr__( self, attr, value ):
			if self._IS_SETUP:
				self._set( self, attr, value )
				return

			super( MelHSingleStretchLayout, self ).__setattr__( attr, value )

		#add some convenience methods for querying and setting the label and label width - they're named deliberately named awkwardly, see the class doc above for more information
		def getLlabel( self ):
			self.UI_lbl.getValue()
		def setLlabel( self, label ):
			self.UI_lbl.setValue( label )
		def getLlabelWidth( self ):
			self.UI_lbl.setWidth()
		def setLlabelWidth( self, width ):
			self.UI_lbl.setWidth( width )
		def getWidget( self ):
			return self.ui

	_tmp.__name__ = clsName
	_tmp.__doc__ = baseCls.__doc__

	return _tmp


#now construct some Labelled classes
LabelledTextField = labelledUIClassFactory( MelTextField )
LabelledIntField = labelledUIClassFactory( MelIntField )
LabelledFloatField = labelledUIClassFactory( MelFloatField )
LabelledFloatSlider = labelledUIClassFactory( MelFloatSlider )
LabelledIntSlider = labelledUIClassFactory( MelIntSlider )
LabelledOptionMenu = labelledUIClassFactory( MelOptionMenu )


class MayaNode(object): pass

UI_FOR_PY_TYPES = { bool: MelCheckBox,
                    int: MelIntField,
                    float: MelFloatField,
                    basestring: MelTextField,
                    list: MelTextScrollList,
                    tuple: MelTextScrollList,
                    MayaNode: MelObjectSelector }

def getBuildUIMethodForObject( obj, typeMapping=None ):
	if typeMapping is None:
		typeMapping = UI_FOR_PY_TYPES

	objType = obj if type( obj ) is type else type( obj )

	#first see if there is an exact type match in the dict
	buildClass = None
	try: buildClass = typeMapping[ objType ]
	except KeyError:
		#if not, see if there is an inheritance match - its possible there may by multiple matches
		#however, so we need to check them all and see which is the most appropriate

		mro = list( inspect.getmro( objType ) )
		bestMatch = None
		for aType, aBuildClass in typeMapping.iteritems():
			if aType in mro:
				bestMatch = mro.index( aType )

			if bestMatch:
				buildClass = aBuildClass
				break

	return buildClass


def buildUIForObject( obj, parent, typeMapping=None ):
	'''
	'''

	buildClass = getBuildUIMethodForObject( obj, typeMapping )

	if buildClass is None:
		raise MelUIError( "there is no build class defined for object's of type %s (%s)" % (type( obj ), obj) )

	ui = buildClass( parent )
	ui.setValue( obj )

	return ui


class BaseMelWindow(BaseMelUI):
	'''
	This is a wrapper class for a mel window to make it behave a little more like an object.  It
	inherits from str because thats essentially what a mel widget is.

	Objects of this class are callable.  Calling an object is basically the same as passing the given
	args to the cmd.window maya command:

	aWindow = BaseMelWindow()
	aWindow( q=True, exists=True )

	is the same as doing:
	aWindow = cmd.window()
	cmd.window( aWindow, q=True, exists=True )
	'''
	WINDOW_NAME = 'unnamed_window'
	WINDOW_TITLE = 'Unnamed Tool'
	MIN_BUTTON = False
	MAX_BUTTON = False
	USE_Template = 	None

	RETAIN = False

	DEFAULT_SIZE = 250, 250
	DEFAULT_MENU = 'File'
	DEFAULT_MENU_IS_HELP = False

	#set this class variable to a 3-tuple containing toolName, authorEmailAddress, helpPage
	#if you don't have a help page you can set the third tuple value to None
	#example:
	#HELP_MENU = 'testTool', 'mel@macaronikazoo.com', 'http://www.macaronikazoo.com/docs/Space_Switching'
	HELP_MENU = None

	FORCE_DEFAULT_SIZE = True

	@classmethod
	def Exists( cls ):
		'''
		returns whether there is an instance of this class already open
		'''
		return cmd.window( cls.WINDOW_NAME, ex=True )
	@classmethod
	def Get( cls ):
		'''
		returns the existing instance
		'''
		return cls.FromStr( cls.WINDOW_NAME )
	@classmethod
	def Close( cls ):
		'''
		closes the window (if it exists)
		'''
		if cls.Exists():
			cmd.deleteUI( cls.WINDOW_NAME )

	def __new__( cls, *a, **kw ):
		kw.setdefault( 'title', cls.WINDOW_TITLE )
		kw.setdefault( 'widthHeight', cls.DEFAULT_SIZE )
		kw.setdefault( 'menuBar', True )
		kw.setdefault( 'retain', cls.RETAIN )
		kw.setdefault( 'useTemplate', cls.USE_Template )
		kw.setdefault( 'minimizeButton', cls.MIN_BUTTON )
		kw.setdefault( 'maximizeButton', cls.MAX_BUTTON )
		
		if cmd.window( cls.WINDOW_NAME, ex=True ):
			cmd.deleteUI( cls.WINDOW_NAME )

		new = unicode.__new__( cls, cmd.window( cls.WINDOW_NAME, **kw ) )
		cmd.window( new, e=True, docTag=cls.__name__ )   #store the classname in the
		if cls.DEFAULT_MENU is not None:
			MelMenu( l=cls.DEFAULT_MENU, helpMenu=cls.DEFAULT_MENU_IS_HELP )

		if cls.HELP_MENU:
			toolName, authorEmail, helpPage = cls.HELP_MENU
			helpMenu = new.getMenu( 'Help' )
			MelMenuItem( helpMenu, l="Help...", en=helpPage is not None, c=lambda x: cmd.showHelp(helpPage, absolute=True) )
			#MelMenuItemDiv( helpMenu )
			#bugReporterUI.addBugReporterMenuItems( toolName, assignee=authorEmail, parent=helpMenu )

		return new
	def __init__( self, *a, **kw ): pass
	def __call__( self, *a, **kw ):
		return cmd.window( self, *a, **kw )
	def setTitle( self, newTitle ):
		cmd.window( self.WINDOW_NAME, e=True, title=newTitle )
	def getMenus( self ):
		menus = self( q=True, menuArray=True ) or []
		return [ MelMenu.FromStr( m ) for m in menus ]
	def getMenu( self, menuName, createIfNotFound=True ):
		'''
		returns the UI name for the menu with the given name
		'''
		for m in self.getMenus():
			if m.getValue() == menuName:
				return m

		if createIfNotFound:
			return MelMenu( l=menuName, helpMenu='help' in menuName.lower() )
	def getLayout( self ):
		'''
		returns the layout parented to this window
		'''
		layoutNameStart = '%s|' % self
		existingLayouts = cmd.lsUI( controlLayouts=True, long=True )
		for existingLayout in existingLayouts:
			if existingLayout.startswith( layoutNameStart ):
				toks = existingLayout.split( '|' )

				return BaseMelLayout.FromStr( '%s|%s' % (self, toks[1]) )
	def exists( self ):
		return cmd.window( self.WINDOW_NAME, q=True, ex=True )
	def show( self, state=True, forceDefaultSize=None ):
		'''
		if forceDefaultSize is None - it uses the FORCE_DEFAULT_SIZE class attribute
		'''
		if state:
			cmd.showWindow( self )
		else:
			self( e=True, visible=False )

		if forceDefaultSize is None:
			forceDefaultSize = self.FORCE_DEFAULT_SIZE

		if forceDefaultSize:
			self( e=True, widthHeight=self.DEFAULT_SIZE )
	def layout( self ):
		'''
		forces the window to re calc layouts for children
		'''
		curWidth = self( q=True, width=True )
		self( e=True, width=curWidth+1 )
		self( e=True, width=curWidth )
	def processEvent( self, methodName, methodArgs, methodKwargs ):
		method = getattr( self, methodName, None )
		if callable( method ):
			method( *methodArgs, **methodKwargs )
	def close( self ):
		self.Close()


###
### PROCEDURAL UI BUILDING ###
###


class UITypeError(TypeError): pass

class PyFuncLayout(MelColumnLayout):
	'''
	builds a default layout for a function - makes it easy to build UI for functions

	call by passing a python function object on construction like so:

	def sweet( this=12, isA=True, test=100 ): pass
	PyFuncLayout( parentLayout, sweet )

	NOTE: the UI building looks for a bunch of special attributes on the function that
	can help control the presentation

	_hideArgs = []  #this is a list of attribute names that won't be presented in the UI
	_show = False   #defaults to False - controls whether the function appears when building UI for a module (otherwise ignored)
	_expand = False #defaults to False - controls whether the frame layout for function is expanded or not by default when building UI for a module (ignored otherwise)
	'''
	def __init__( self, parent, func ):
		MelColumnLayout.__init__( self, parent )

		hideArgNames = []
		if hasattr( func, '_hideArgs' ):
			hideArgNames = list( func._hideArgs )

		self.argUIDict = {}  #stores the argName->UI mapping
		self.func = func  #stores the function passed in

		argNames, vargName, vkwargName, defaults = inspect.getargspec( func )

		numDefaults = len( defaults )
		numArgsWithoutDefaults = len( argNames ) - numDefaults

		#pad the defaults with empty strings for args that have no default - it'll be up to the user to write appropriate python expressions
		defaults = ([ '' ] * numArgsWithoutDefaults) + list( defaults )

		labels = []
		for argName, default in zip( argNames, defaults ):
			if argName in hideArgNames:
				continue

			hLayout = MelHLayout( self )

			lbl = MelLabel( hLayout, l=names.camelCaseToNice( argName ) )
			labels.append( lbl )

			ui = buildUIForObject( default, hLayout )
			ui.setChangeCB( Callback( self.changeCB, argName ) )

			hLayout.setWeight( lbl, 0 )
			hLayout.layout()

			#finally stuff the ui into the argUIDict
			self.argUIDict[ argName ] = ui

		maxWidth = max( [ lbl.getWidth() for lbl in labels ] ) + 10  #10 for padding...
		for lbl in labels:
			lbl.setWidth( maxWidth )

		MelButton( self, l='Execute %s' % names.camelCaseToNice( func.__name__ ), c=self.execute )
	def changeCB( self, argName ):
		melUtils.printInfoStr( '%s arg changed!' % argName )
	def getArgDict( self ):
		argDict = {}
		for argName, ui in self.argUIDict.iteritems():
			argDict[ argName ] = ui.getValue()

		#we need to get the args that have no default values and eval the values from the ui - it is assumed they're valid python expressions
		argNames, vargName, vkwargName, defaults = inspect.getargspec( self.func )

		numArgsWithoutDefaults = len( argNames ) - len( defaults )
		for argName in argNames[ :numArgsWithoutDefaults ]:
			uiStr = ui.getValue()
			if not uiStr:
				raise UITypeError( "No value given for %s arg" % argName )

			argDict[ argName ] = eval( uiStr )

		return argDict
	def execute( self, *a ):
		try:
			self.func( **self.getArgDict() )
		except UITypeError:
			cmd.confirmDialog( "No value was entered for one of the args!", b='OK', db='OK')


class PyFuncWindow(BaseMelWindow):
	'''
	this is basically just a wrapper around the PyFuncLayout above.  Its called
	in a similar way:

	def sweet( this=12, isA=True, test=100 ): pass
	PyFuncWindow( sweet )
	'''

	WINDOW_NAME = 'funcWindow'
	DEFAULT_MENU = None

	FORCE_DEFAULT_SIZE = False

	def __init__( self, func ):
		PyFuncLayout( self, func )

		self.setTitle( '%s Window' % names.camelCaseToNice( func.__name__ ) )
		self.show()


class PyModuleLayout(MelColumnLayout):
	'''
	builds a window for an entire module
	'''
	def __init__( self, parent, module, showAll=False ):
		def func(): pass
		funcType = type( func )

		#track the number of expanded frame layouts - we want to make sure at least one is expanded...
		numExpanded = 0

		self.funcUIDict = {}
		for objName, obj in module.__dict__.iteritems():
			if not isinstance( obj, funcType ):
				continue

			#skip any obj that already has UI built
			if obj in self.funcUIDict:
				continue

			show = False
			if hasattr( obj, '_show' ):
				show = obj._show

			#if we're not showing all, check the show state and skip accordingly
			if not showAll:
				if not show:
					continue

			expand = False
			if hasattr( obj, '_expand' ):
				expand = obj._expand

			if expand:
				numExpanded += 1

			frame = MelFrameLayout( self, label=names.camelCaseToNice( objName ), cl=not expand, cll=True )
			ui = PyFuncLayout( frame, obj )
			self.funcUIDict[ obj ] = ui

		#if there are no expanded frames - expand the first one...
		if not numExpanded:
			children = self.getChildren()
			children[ 0 ].setCollapse( False )


class PyModuleWindow(BaseMelWindow):
	'''
	this is basically just a wrapper around the PyFuncLayout above.  Its called
	in a similar way:

	def sweet( this=12, isA=True, test=100 ): pass
	PyFuncWindow( sweet )
	'''

	WINDOW_NAME = 'moduleWindow'
	DEFAULT_MENU = None

	def __init__( self, module, showAll=False ):
		PyModuleLayout( self, module, showAll )

		self.setTitle( '%s Window' % names.camelCaseToNice( module.__name__ ) )
		self.show()


#end
