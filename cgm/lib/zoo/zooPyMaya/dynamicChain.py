
from maya.cmds import *
from baseMelUI import *
from melUtils import printWarningStr
from control import attrState, LOCK_HIDE, Axis
from mayaDecorators import d_unifyUndo
from names import camelCaseToNice
from apiExtensions import getNodesCreatedBy


class DynamicChain(object):
	'''
	provides a high level interface to interact with existing dynamic chain setups in the current scene

	to create a new dynamic chain instance, use DynamicChain.Create
	to instantiate a previously created chain use DynamicChain( dynamicChainNode )

	the dynamic chain node simply describes what nodes to create the dynamic chain on, and provide a place
	to store persistent properties.  To build the dynamic chain setup you need to call dynChain.construct()
	on a DynamicChain instance.  Similarly you can turn a dynamic chain "off" by calling dynChain.mute()
	'''

	#used to identify the sets used by this tool to describe the dynamic chain setups
	SET_NODE_IDENTIFIER = 'zooDynamicChain'

	@classmethod
	@d_unifyUndo
	def Create( cls, objs ):
		'''
		constructs a new DynamicChain instance

		NOTE: this only creates the description of the dynamic chain - if you want the dynamic chain to be
		"turned on", you'll need to call construct() on the instance returned
		'''
		if not objs:
			raise ValueError( "Must provide a list of objects to construct the DynamicChain on" )

		node = sets( empty=True, text=cls.SET_NODE_IDENTIFIER )
		node = rename( node, '%s_dynChain#' % objs[0].split( '|' )[-1].split( ':' )[-1] )

		addAttr( node, ln='transforms', at='message', indexMatters=True, multi=True )
		for n, obj in enumerate( objs ):
			connectAttr( '%s.message' % obj, '%s.transforms[%d]' % (node, n) )

		#add attributes to the set node - adding them to the set means user set attributes are preserved across muting and unmuting of the chain
		addAttr( node, ln='stiffness', at='double', min=0, max=1, dv=0.15, keyable=True )
		addAttr( node, ln='lengthFlex', at='double', min=0, max=1, dv=0, keyable=True )
		addAttr( node, ln='damping', at='double', min=0, max=25, dv=0, keyable=True )
		addAttr( node, ln='drag', at='double', min=0, max=1, dv=0.1, keyable=True )
		addAttr( node, ln='friction', at='double', min=0, max=1, dv=0.5, keyable=True )
		addAttr( node, ln='gravity', at='double', min=0, max=10, dv=1, keyable=True )
		addAttr( node, ln='turbStrength', at='double', min=0, max=1, dv=0, keyable=True )
		addAttr( node, ln='turbFreq', at='double', min=0, max=2, dv=0.2, keyable=True )
		addAttr( node, ln='turbSpeed', at='double', min=0, max=2, dv=0.2, keyable=True )
		addAttr( node, ln='proxyRoot', at='message' )

		self = cls( node )

		return self
	@classmethod
	def Iter( cls ):
		'''
		iterates over all dynamic chains in the current scene
		'''
		for node in ls( type='objectSet' ):
			if sets( node, q=True, text=True ) == cls.SET_NODE_IDENTIFIER:
				yield cls( node )

	def __init__( self, container ):
		self._node = container
	def getNode( self ):
		return self._node
	def getObjs( self ):
		'''
		returns the objects involved in the dynamic chain
		'''
		objs = []
		nControls = getAttr( '%s.transforms' % self._node, size=True )
		for n in range( nControls ):
			cons = listConnections( '%s.transforms[%d]' % (self._node, n), d=False )
			if cons:
				objs.append( cons[0] )

		return objs
	def getProxyRoot( self ):
		'''
		returns the
		'''
		cons = listConnections( '%s.proxyRoot' % self._node, d=False )
		if cons:
			return cons[0]

		return None
	@d_unifyUndo
	def construct( self ):
		'''
		builds the actual dynamic hair network
		'''
		setNode = self._node
		objs = self.getObjs()

		#before we do anything, check to see whether the selected objects have any incoming connections
		warnAboutDisconnections = False
		for obj in objs:

			#check the object for incoming connections - if it has any, remove them
			for chan in ('t', 'r'):
				for ax in Axis.BASE_AXES:
					cons = listConnections( '%s.%s%s' % (obj, chan, ax), d=False )
					if cons:
						warnAboutDisconnections = True
						if objectType( cons[0], isAType='animCurve' ):
							delete( cons[0] )
						else:
							raise TypeError( "The object %s has non anim curve incoming connections - aborting!  Please remove connections manually before proceeding" % obj )

		if warnAboutDisconnections:
			printWarningStr( "Some of the objects had incoming connections (probably from animation).  These connections have been broken!  undo if you want them back" )

		#wrap the creation of the nodes in a function - below this we execute this function via a wrapper which returns a list of new nodes created
		#this is done so we can easily capture the nodes created and store them in the set that describes this dynamic chain
		def doCreate():
			positions = []
			for obj in objs:
				positions.append( xform( obj, q=True, ws=True, rp=True ) )

			#the objs may not be in the same hierarchy, so create a proxy chain that IS in a heirarchy
			proxyJoints = []
			for obj in objs:
				select( cl=True )
				j = createNode( 'joint' )
				j = rename( j, '%s_dynChainProxy#' % obj.split( ':' )[-1].split( '|' )[-1] )
				if proxyJoints:
					parent( j, proxyJoints[-1] )

				delete( parentConstraint( obj, j ) )
				proxyJoints.append( j )

				#constrain the original to the proxy
				parentConstraint( j, obj )

			#hook up the proxy root to a special message attribute so we can easily find the proxy chain again for things like baking etc...
			connectAttr( '%s.message' % proxyJoints[0], '%s.proxyRoot' % setNode )

			#build a linear curve
			linearCurve = curve( d=1, p=positions )
			linearCurveShape = listRelatives( linearCurve, s=True, pa=True )[0]
			select( linearCurve )
			maya.mel.eval( 'makeCurvesDynamicHairs 1 0 1;' )

			#find the dynamic curve shape
			cons = listConnections( '%s.worldSpace' % linearCurveShape, s=False )
			if not cons:
				printWarningStr( "Cannot find follicle" )
				return

			follicleShape = cons[0]
			cons = listConnections( '%s.outHair' % follicleShape, s=False )
			if not cons:
				printWarningStr( "Cannot find hair system!" )
				return

			hairSystemNode = cons[0]
			setAttr( '%s.startFrame' % hairSystemNode, playbackOptions( q=True, min=True ) )
			cons = listConnections( '%s.outCurve' % follicleShape, s=False )
			if not cons:
				printWarningStr( "Cannot find out curve!" )
				return

			dynamicCurve = cons[0]
			dynamicCurveParent = listRelatives( dynamicCurve, p=True, pa=True )  #grab the dynamic curve's shape

			select( dynamicCurve )
			maya.mel.eval( 'displayHairCurves "current" 1;' )

			follicle = listRelatives( linearCurve, p=True, pa=True )[0]
			objParent = listRelatives( objs[0], p=True, pa=True )
			if objParent:
				objParent = objParent[0]
				parent( follicle, objParent )
				parent( proxyJoints[0], objParent )

			setAttr( '%s.overrideDynamics' % follicle, 1 )
			setAttr( '%s.pointLock' % follicle, 1 )

			#hook up all the attributes
			connectAttr( '%s.stiffness' % setNode, '%s.stiffness' % follicle )
			connectAttr( '%s.lengthFlex' % setNode, '%s.lengthFlex' % follicle )
			connectAttr( '%s.damping' % setNode, '%s.damp' % follicle )
			connectAttr( '%s.drag' % setNode, '%s.drag' % hairSystemNode )
			connectAttr( '%s.friction' % setNode, '%s.friction' % hairSystemNode )
			connectAttr( '%s.gravity' % setNode, '%s.gravity' % hairSystemNode )
			connectAttr( '%s.turbStrength' % setNode, '%s.turbulenceStrength' % hairSystemNode )
			connectAttr( '%s.turbFreq' % setNode, '%s.turbulenceFrequency' % hairSystemNode )
			connectAttr( '%s.turbSpeed' % setNode, '%s.turbulenceSpeed' % hairSystemNode )

			splineIkHandle = ikHandle( sj=proxyJoints[0], ee=proxyJoints[-1], curve=dynamicCurve, sol='ikSplineSolver', ccv=False )[0]

			#for some reason the dynamic curve gets re-parented by the ikHandle command (weird) so set the parent back to what it was originally
			parent( dynamicCurve, dynamicCurveParent )

		newNodes, returnValue = getNodesCreatedBy( doCreate )

		#stuff the nodes created into the set that describes this dynamic chain - just add transform nodes...
		for aNode in newNodes:
			if objectType( aNode, isAType='transform' ):
				sets( aNode, e=True, add=setNode )
	@d_unifyUndo
	def mute( self ):
		'''
		deletes the hair nodes but retains the settings and objects involved in the hair
		'''

		#we need to lock the set node before deleting its contents otherwise maya will delete the set
		lockNode( self._node, lock=True )

		#now delete the set contents
		delete( sets( self._node, q=True ) )

		#finally unlock the node again
		lockNode( self._node, lock=False )
	def getMuted( self ):
		'''
		returns whether this dynamic chain is muted or not
		'''
		return not bool( sets( self._node, q=True ) )
	def setMuted( self, state ):
		if state:
			self.mute()
		else:
			self.construct()
	@d_unifyUndo
	def bake( self, keyEveryNthFrame=4 ):
		'''
		if this dynamic chain isn't muted, this will bake the motion to keyframes and mute
		the dynamic hair

		keyEveryNthFrame describes how often keys are baked - set to 1 to bake every frame
		'''

		#grab the range
		timeRange = playbackOptions( q=True, min=True ), playbackOptions( q=True, max=True )

		#bake the simulation - NOTE: we DON'T use the keyEveryNthFrame value for the sampleBy arg here because otherwise maya only samples every nth frame which doesn't perform teh simulation properly.  yay maya!
		bakeSimulation( self.getObjs(), t=timeRange, sampleBy=1, preserveOutsideKeys=True, simulation=True, disableImplicitControl=True, sparseAnimCurveBake=True )

		#because of the sampling problem above, we now need to respect the user value specified for keyEveryNthFrame manually
		if keyEveryNthFrame > 1:
			pass

		#finally turn this chain off...
		self.mute()
	@d_unifyUndo
	def delete( self ):
		'''
		deletes the dynamic chain
		'''
		nodesInSet = sets( self._node, q=True ) or []
		for node in nodesInSet:
			if objExists( node ):
				delete( node )

		#the node shouldn't actually exist anymore - maya should have deleted it automatically after the last object in it was deleted.  but
		#in the interests of thoroughness, lets make sure.  who knows what sort of crazy corner cases exist
		if objExists( self._node ):

			#check to see if the set node is referenced - if it is, it will be un-deletable
			if not referenceQuery( self._node, inr=True ):
				delete( self._node )


class DynamicChainScrollList(MelObjectScrollList):
	def itemAsStr( self, item ):
		isMuted = item.getMuted()
		if isMuted:
			return '[ muted ] %s' % item.getNode()

		return item.getNode()


class DynamicChainEditor(MelColumnLayout):
	def __init__( self, parent ):
		self._chain = None
		MelColumnLayout.__init__( self, parent )
	def setChain( self, dynamicChain ):
		self.clear()
		self._chain = dynamicChain

		if dynamicChain is None:
			return

		dynChainNode = dynamicChain.getNode()
		MelLabel( self, l='Editing Dynamic Chain: %s' % dynChainNode )
		MelSeparator( self, h=15 )

		attrs = listAttr( dynChainNode, k=True ) or []
		for attr in attrs:
			attrpath = '%s.%s' % (dynChainNode, attr)

			niceAttrName = camelCaseToNice( attr )

			#query the attribute type and build UI for the types we care about presenting to the user
			attrType = getAttr( attrpath, type=True )
			ui = None
			if attrType == 'bool':
				ui = MelCheckBox( self, l=niceAttrName )
			elif attrType == 'double':
				min, max = addAttr( attrpath, q=True, min=True ), addAttr( attrpath, q=True, max=True )
				ui = LabelledFloatSlider( self, min, max, ll=niceAttrName, llw=65 ).getWidget()

			if ui is None:
				continue

			connectControl( ui, attrpath )

		MelSeparator( self, h=15 )

		hLayout = MelHSingleStretchLayout( self )
		lbl = MelLabel( hLayout, l='Key Every N Frames' )
		self.UI_nFrame = MelIntField( hLayout, v=4, min=1, max=10, step=1 )
		self.UI_bake = MelButton( hLayout, l='Bake To Keys', c=self.on_bake )

		hLayout( e=True, af=((lbl, 'top', 0), (lbl, 'bottom', 0)) )
		hLayout.padding = 10
		hLayout.setStretchWidget( self.UI_bake )
		hLayout.layout()

	### EVENT HANDLERS ###
	def on_bake( self, *a ):
		if self._chain:
			self._chain.bake( self.UI_nFrame.getValue() )

		self.sendEvent( 'on_mute' )


class DynamicChainLayout(MelHSingleStretchLayout):
	def __init__( self, parent ):
		vLayout = MelVSingleStretchLayout( self )

		self.UI_dynamicChains = DynamicChainScrollList( vLayout )
		self.UI_dynamicChains.setWidth( 175 )
		self.UI_dynamicChains.setChangeCB( self.on_chainListSelectionChange )

		self.UI_create = MelButton( vLayout, l='Create Chain From Selection', c=self.on_create )
		self.UI_mute = MelButton( vLayout, l='Toggle Mute On Highlighted', c=self.on_mute )
		MelSeparator( vLayout, h=15 )
		self.UI_delete = MelButton( vLayout, l='Delete Highlighted', c=self.on_delete )

		vLayout.padding = 0
		vLayout.setStretchWidget( self.UI_dynamicChains )
		vLayout.layout()

		self.UI_editor = DynamicChainEditor( self )

		self.padding = 10
		self.expand = True
		self.setStretchWidget( self.UI_editor )
		self.layout()

		self.populate()

		#hook up callbacks
		self.setSelectionChangeCB( self.on_sceneSelectionChange )
		self.setSceneChangeCB( self.on_sceneChange )

		#run the selection callback to update the UI
		self.on_sceneSelectionChange()
	def populate( self ):
		initialSelection = self.UI_dynamicChains.getSelectedItems()

		self.UI_dynamicChains.clear()
		chains = list( DynamicChain.Iter() )
		for dynamicChain in chains:
			self.UI_dynamicChains.append( dynamicChain )

		if initialSelection:
			if initialSelection[0] in self.UI_dynamicChains:
				self.UI_dynamicChains.selectByValue( initialSelection[0], False )
		elif chains:
			self.UI_dynamicChains.selectByValue( chains[0], False )

		#run the highlight callback to update the UI
		self.on_chainListSelectionChange()

	### EVENT HANDLERS ###
	def on_sceneSelectionChange( self, *a ):
		areNodesSelected = bool( ls( sl=True, type='transform' ) )
		self.UI_create.setEnabled( areNodesSelected )
	def on_sceneChange( self, *a ):
		self.populate()
	def on_chainListSelectionChange( self, *a ):
		sel = self.UI_dynamicChains.getSelectedItems()
		areItemsSelected = bool( sel )

		if areItemsSelected:
			self.UI_editor.setChain( sel[0] )
		else:
			self.UI_editor.setChain( None )

		#set enable state on UI that is sensitive to whether we have highlighted items in the dynamic chain list
		self.UI_mute.setEnabled( areItemsSelected )
		self.UI_delete.setEnabled( areItemsSelected )
	def on_create( self, *a ):
		selection = ls( sl=True, type='transform' )
		dynamicChain = DynamicChain.Create( selection )
		dynamicChain.setMuted( False )
		self.populate()

		self.UI_dynamicChains.selectByValue( dynamicChain, True )
	def on_mute( self, *a ):
		sel = self.UI_dynamicChains.getSelectedItems()
		if sel:
			muteStateToSet = not sel[0].getMuted()
			for s in sel:
				s.setMuted( muteStateToSet )

		self.populate()
	def on_delete( self, *a ):
		sel = self.UI_dynamicChains.getSelectedItems()
		if sel:
			for s in sel:
				s.delete()

		self.populate()


class DynamicChainWindow(BaseMelWindow):
	WINDOW_NAME = 'zooDynamicChainMaker'
	WINDOW_TITLE = 'Dynamic Chain Maker'

	DEFAULT_MENU = None
	DEFAULT_SIZE = 500, 325
	FORCE_DEFAULT_SIZE = True

	def __init__( self ):
		DynamicChainLayout( self )
		self.show()


#end
