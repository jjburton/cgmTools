
from zooPy import typeFactories
from zooPy.path import Path
from zooPy.vectors import Vector, Matrix, Axis
from zooPy.names import Parity, Name, camelCaseToNice, stripParity

from maya.cmds import *
from maya import cmds as cmd

from rigUtils import *
from control import *
from skeletonBuilder import *
from mayaDecorators import d_unifyUndo, d_showWaitCursor
from melUtils import printInfoStr, printWarningStr, printErrorStr, referenceFile

import apiExtensions
import skeletonBuilder
import spaceSwitching
import poseSym
import control

from triggered import Trigger, setKillState

AXES = Axis.BASE_AXES

AIM_AXIS = AX_X
ROT_AXIS = AX_Y

#make sure all setDrivenKeys have linear tangents
setDrivenKeyframe = lambda *a, **kw: cmd.setDrivenKeyframe( inTangentType='linear', outTangentType='linear', *a, **kw )


def connectAttrReverse( srcAttr, destAttr, **kw ):
	'''
	puts a reverse node in between the two given attributes
	'''
	revNode = shadingNode( 'reverse', asUtility=True )
	connectAttr( srcAttr, '%s.inputX' % revNode, **kw )
	connectAttr( '%s.outputX' % revNode, destAttr, **kw )

	return revNode


class RigPartError(Exception): pass


def isRigPartContainer( node ):
	if objectType( node, isType='objectSet' ):
		return sets( node, q=True, text=True ) == 'rigPrimitive'

	return False


def getRigPartContainers( compatabilityMode=False ):
	existingContainers = [ node for node in ls( type='objectSet', r=True ) or [] if sets( node, q=True, text=True ) == 'rigPrimitive' ]
	if compatabilityMode:
		existingContainers += [ node.split( '.' )[0] for node in ls( '*._rigPrimitive', r=True ) ]

	return existingContainers


def getNodesCreatedBy( function, *args, **kwargs ):
	'''
	returns a 2-tuple containing all the nodes created by the passed function, and
	the return value of said function

	NOTE: if any container nodes were created, their contents are omitted from the
	resulting node list - the container itself encapsulates them
	'''

	newNodes, ret = apiExtensions.getNodesCreatedBy( function, *args, **kwargs )

	#now remove nodes from all containers from the newNodes list
	newContainers = apiExtensions.filterByType( newNodes, apiExtensions.MFn.kSet )

	#NOTE: nodes are MObject instances at this point
	newNodes = set( [ node for node in newNodes if node is not None ] )
	for c in newContainers:
		for n in sets( c, q=True ) or []:
			if n in newNodes:
				newNodes.remove( n )


	#containers contained by other containers don't need to be returned (as they're already contained by a parent)
	newTopLevelContainers = []
	for c in newContainers:
		parentContainer = sets( c, q=True, parentContainer=True )
		if parentContainer:
			continue

		newTopLevelContainers.append( c )
		newNodes.add( c )


	return newNodes, ret


def buildContainer( typeClass, kwDict, nodes, controls, namedNodes=() ):
	'''
	builds a container for the given nodes, and tags it with various attributes to record
	interesting information such as rig primitive version, and the args used to instantiate
	the rig.  it also registers control objects with attributes, so the control nodes can
	queried at a later date by their name
	'''

	#if typeClass is an instance, then set its container attribute, otherwise instantiate an instance and return it
	if isinstance( typeClass, RigPart ):
		theInstance = typeClass
		typeClass = type( typeClass )
	elif issubclass( typeClass, RigPart ):
		theInstance = typeClass( None )

	#build the container, and add the special attribute to it to
	theContainer = sets( em=True, n='%s_%s' % (typeClass.__name__, kwDict.get( 'idx', 'NOIDX' )), text='rigPrimitive' )
	theInstance.setContainer( theContainer )

	addAttr( theContainer, ln='_rigPrimitive', attributeType='compound', numberOfChildren=7 )
	addAttr( theContainer, ln='typeName', dt='string', parent='_rigPrimitive' )
	addAttr( theContainer, ln='script', dt='string', parent='_rigPrimitive' )
	addAttr( theContainer, ln='version', at='long', parent='_rigPrimitive' )
	addAttr( theContainer, ln='skeletonPart', at='message', parent='_rigPrimitive' )
	addAttr( theContainer, ln='buildKwargs', dt='string', parent='_rigPrimitive' )
	addAttr( theContainer, ln='controls',
	         multi=True,
	         indexMatters=True,
	         attributeType='message',
	         parent='_rigPrimitive' )
	addAttr( theContainer, ln='namedNodes',
	         multi=True,
	         indexMatters=True,
	         attributeType='message',
	         parent='_rigPrimitive' )


	#now set the attribute values...
	setAttr( '%s._rigPrimitive.typeName' % theContainer, typeClass.__name__, type='string' )
	setAttr( '%s._rigPrimitive.script' % theContainer, inspect.getfile( typeClass ), type='string' )
	setAttr( '%s._rigPrimitive.version' % theContainer, typeClass.__version__ )
	setAttr( '%s._rigPrimitive.buildKwargs' % theContainer, str( kwDict ), type='string' )


	#now add all the nodes
	nodes = [ str( node ) if node is not None else node for node in nodes ]
	controls = [ str( node ) if node is not None else node for node in controls ]
	for node in set( nodes ) | set( controls ):
		if node is None:
			continue

		if objectType( node, isAType='dagNode' ):
			sets( node, e=True, add=theContainer )

		#if the node is a rig part container add it to this container otherwise skip it
		elif objectType( node, isAType='objectSet' ):
			if isRigPartContainer( node ):
				sets( node, e=True, add=theContainer )


	#and now hook up all the controls
	controlNames = typeClass.CONTROL_NAMES or []  #CONTROL_NAMES can validly be None, so in this case just call it an empty list
	for idx, control in enumerate( controls ):
		if control is None:
			continue

		connectAttr( '%s.message' % control, '%s._rigPrimitive.controls[%d]' % (theContainer, idx), f=True )

		#set the kill state on the control if its a transform node
		if objectType( control, isAType='transform' ):
			setKillState( control, True )

	#hook up all the named nodes
	for idx, node in enumerate( namedNodes ):
		if node is None:
			continue

		connectAttr( '%s.message' % node, '%s._rigPrimitive.namedNodes[%d]' % (theContainer, idx), f=True )

	return theInstance


class RigPart(typeFactories.trackableClassFactory()):
	'''
	base rig part class.  deals with rig part creation.

	rig parts are instantiated by passing the class a rig part container node

	to create a new rig part, simply call the RigPartClass.Create( skeletonPart, *args )
	where the skeletonPart is the SkeletonPart instance created via the skeleton builder
	'''

	__version__ = 0
	PRIORITY = 0
	CONTROL_NAMES = None
	NAMED_NODE_NAMES = None
	AVAILABLE_IN_UI = False  #determines whether this part should appear in the UI or not...
	ADD_CONTROLS_TO_QSS = True

	AUTO_PICKER = True

	#if you want to customize the name as it appears in the UI, set this to the desired string
	DISPLAY_NAME = None

	def __new__( cls, partContainer, skeletonPart=None ):
		if cls is RigPart:
			clsName = getAttr( '%s._rigPrimitive.typeName' % partContainer )
			cls = cls.GetNamedSubclass( clsName )
			if cls is None:
				raise TypeError( "Cannot determine the part class for the given part container!" )

		return object.__new__( cls )
	def __init__( self, partContainer, skeletonPart=None ):
		if partContainer is not None:
			assert isRigPartContainer( partContainer ), "Must pass a valid rig part container! (received %s - a %s)" % (partContainer, nodeType( partContainer ))

		self._container = partContainer
		self._skeletonPart = skeletonPart
		self._worldPart = None
		self._worldControl = None
		self._partsNode = None
		self._qss = None
		self._idx = None

		if partContainer:
			if skeletonPart is None:
				try:
					self.getSkeletonPart()

				#this isn't fatal, although its not good
				except RigPartError, x:
					printWarningStr( str( x ) )
	def __unicode__( self ):
		return u"%s_%d( %r )" % (self.__class__.__name__, self.getIdx(), self._container)
	__str__ = __unicode__
	def __repr__( self ):
		return repr( unicode( self ) )
	def __hash__( self ):
		'''
		the hash for the container mobject uniquely identifies this rig control
		'''
		return hash( apiExtensions.asMObject( self._container ) )
	def __eq__( self, other ):
		return self._container == other.getContainer()
	def __neq__( self, other ):
		return not self == other
	def __getitem__( self, idx ):
		'''
		returns the control at <idx>
		'''
		connected = listConnections( '%s._rigPrimitive.controls[%d]' % (self._container, idx), d=False )
		if connected:
			assert len( connected ) == 1, "More than one control was found!!!"
			return connected[ 0 ]

		return None
	def __len__( self ):
		'''
		returns the number of controls registered on the rig
		'''
		return getAttr( '%s._rigPrimitive.controls' % self._container, size=True )
	def __iter__( self ):
		'''
		iterates over all controls in the rig
		'''
		for n in range( len( self ) ):
			yield self[ n ]
	def getContainer( self ):
		return self._container
	def setContainer( self, container ):
		self._container = container
	def getNodes( self ):
		'''
		returns ALL the nodes that make up this rig part
		'''
		return sets( self._container, q=True )
	nodes = getNodes
	def isReferenced( self ):
		return referenceQuery( self._container, inr=True )
	@classmethod
	def GetPartName( cls ):
		'''
		can be used to get a "nice" name for the part class
		'''
		if cls.DISPLAY_NAME is None:
			return camelCaseToNice( cls.__name__ )

		return cls.DISPLAY_NAME
	@classmethod
	def InitFromItem( cls, item ):
		'''
		inits the rigPart from a member item - the RigPart instance returned is
		cast to teh most appropriate type
		'''

		if isRigPartContainer( item ):
			typeClassStr = getAttr( '%s._rigPrimitive.typeName' % partContainer )
			typeClass = RigPart.GetNamedSubclass( typeClassStr )

			return typeClass( item )

		cons = listConnections( item, s=False, type='objectSet' )
		if not cons:
			raise RigPartError( "Cannot find a rig container for %s" % item )

		for con in cons:
			if isRigPartContainer( con ):
				typeClassStr = getAttr( '%s._rigPrimitive.typeName' % con )
				typeClass = RigPart.GetNamedSubclass( typeClassStr )

				return typeClass( con )

		raise RigPartError( "Cannot find a rig container for %s" % item )
	@classmethod
	def IterAllParts( cls, skipSubParts=True ):
		'''
		iterates over all RigParts in the current scene

		NOTE: if skipSubParts is True will skip over parts that inherit from RigSubPart - these are assumed to be contained by another part
		'''
		for c in getRigPartContainers():
			if objExists( '%s._rigPrimitive' % c ):
				thisClsName = getAttr( '%s._rigPrimitive.typeName' % c )
				thisCls = RigPart.GetNamedSubclass( thisClsName )

				if thisCls is None:
					raise SkeletonError( "No RigPart called %s" % thisClsName )

				if skipSubParts and issubclass( thisCls, RigSubPart ):
					continue

				if issubclass( thisCls, cls ):
					yield cls( c )
	@classmethod
	def IterAllPartsInOrder( cls, skipSubParts=False ):
		for skeletonPart in SkeletonPart.IterAllPartsInOrder():
			rigPart = skeletonPart.getRigPart()
			if rigPart is None:
				continue

			if skipSubParts and isinstance( rigPart, RigSubPart ):
				continue

			yield rigPart
	@classmethod
	def GetUniqueIdx( cls ):
		'''
		returns a unique index (unique against the universe of existing indices
		in the scene) for the current part class
		'''
		existingIdxs = []
		for part in cls.IterAllParts():
			idx = part.getBuildKwargs()[ 'idx' ]
			existingIdxs.append( idx )

		existingIdxs.sort()
		assert len( existingIdxs ) == len( set( existingIdxs ) ), "There is a duplicate ID! %s, %s" % (cls, existingIdxs)

		#return the first, lowest, available index
		for orderedIdx, existingIdx in enumerate( existingIdxs ):
			if existingIdx != orderedIdx:
				return orderedIdx

		if existingIdxs:
			return existingIdxs[ -1 ] + 1

		return 0
	def createSharedShape( self, name ):
		return asMObject( createNode( 'nurbsCurve', n=name +'#', p=self.sharedShapeParent ) )
	@classmethod
	def Create( cls, skeletonPart, *a, **kw ):
		'''
		you can pass in the following kwargs to control the build process
		addControlsToQss		defaults to cls.ADD_CONTROLS_TO_QSS
		'''

		#check to see if the given skeleton part can actually be rigged by this method
		if not cls.CanRigThisPart( skeletonPart ):
			return

		addControlsToQss = kw.get( 'addControlsToQss', cls.ADD_CONTROLS_TO_QSS )

		buildFunc = getattr( cls, '_build', None )
		if buildFunc is None:
			raise RigPartError( "The rigPart %s has no _build method!" % cls.__name__ )

		assert isinstance( skeletonPart, SkeletonPart ), "Need a SkeletonPart instance, got a %s instead" % skeletonPart.__class__

		if not skeletonPart.compareAgainstHash():
			raise NotFinalizedError( "ERROR :: %s hasn't been finalized!" % skeletonPart )


		#now turn the args passed in are a single kwargs dict
		argNames, vArgs, vKwargs, defaults = inspect.getargspec( buildFunc )
		if defaults is None:
			defaults = []

		argNames = argNames[ 2: ]  #strip the first two args - which should be the instance arg (usually self) and the skeletonPart
		if vArgs is not None:
			raise RigPartError( 'cannot have *a in rig build functions' )

		for argName, value in zip( argNames, a ):
			kw[ argName ] = value

		#now explicitly add the defaults
		for argName, default in zip( argNames, defaults ):
			kw.setdefault( argName, default )


		#generate an index for the rig part - each part must have a unique index
		idx = cls.GetUniqueIdx()
		kw[ 'idx' ] = idx


		#construct an empty instance - empty RigPart instances are only valid inside this method...
		self = cls( None )
		self._skeletonPart = skeletonPart
		self._idx = idx


		#generate a default scale for the rig part
		kw.setdefault( 'scale', getScaleFromSkeleton() / 10.0 )
		self.scale = kw[ 'scale' ]


		#make sure the world part is created first - if its created by the part, then its nodes will be included in its container...
		self.getWorldPart()


		#create the shared shape transform - this is the transform under which all shared shapes are temporarily parented to, and all
		#shapes under this transform are automatically added to all controls returned after the build function returns
		self.sharedShapeParent = asMObject( createNode( 'transform', n='_tmp_sharedShape' ) )
		defaultSharedShape = self.createSharedShape( '%s_sharedAttrs' % cls.GetPartName() )
		kw[ 'sharedShape' ] = defaultSharedShape


		#run the build function
		newNodes, (controls, namedNodes) = getNodesCreatedBy( self._build, skeletonPart, **kw )
		realControls = [ c for c in controls if c is not None ]  #its possible for a build function to return None in the control list because it wants to preserve the length of the control list returned - so construct a list of controls that actually exist
		realNamedNodes = [ c for c in namedNodes if c is not None ]
		if addControlsToQss:
			for c in realControls:
				sets( c, add=self._qss )


		#check to see if there is a layer for the rig controls and add controls to it
		if controls:
			if objExists( 'rig_controls' ) and nodeType( 'rig_controls' ) == 'displayLayer':
				rigLayer = 'rig_controls'
			else:
				rigLayer = createDisplayLayer( name='rig_controls', empty=True )

			editDisplayLayerMembers( rigLayer, controls, noRecurse=True )


		#make sure there are no intermediate shapes
		for c in realControls:
			for shape in listRelatives( c, s=True, pa=True ) or []:
				if getAttr( '%s.intermediateObject' % shape ):
					delete( shape )


		#build the container and initialize the rigPrimtive
		buildContainer( self, kw, newNodes, controls, namedNodes )


		#add shared shapes to all controls, and remove shared shapes that are empty
		sharedShapeParent = self.sharedShapeParent
		sharedShapes = listRelatives( sharedShapeParent, pa=True, s=True ) or []
		for c in realControls:
			if objectType( c, isAType='transform' ):
				for shape in sharedShapes:
					parent( shape, c, add=True, s=True )

		for shape in sharedShapes:
			if not listAttr( shape, ud=True ):
				delete( shape )

		delete( sharedShapeParent )
		del( self.sharedShapeParent )


		#stuff the part container into the world container - we want a clean top level in the outliner
		theContainer = self._container
		sets( theContainer, e=True, add=self._worldPart.getContainer() )


		#make sure the container "knows" the skeleton part - its not always obvious trawling through
		#the nodes in teh container which items are the skeleton part
		connectAttr( '%s.message' % skeletonPart.getContainer(), '%s._rigPrimitive.skeletonPart' % theContainer )


		return self
	@classmethod
	def GetControlName( cls, control ):
		'''
		returns the name of the control as defined in the CONTROL_NAMES attribute
		for the part class
		'''
		cons = listConnections( control.message, s=False, p=True, type='objectSet' )
		for c in cons:
			typeClassStr = getAttr( '%s._rigPrimitive.typeName' % c.node() )
			typeClass = RigPart.GetNamedSubclass( typeClassStr )
			if typeClass.CONTROL_NAMES is None:
				return str( control )

			idx = c[ c.rfind( '[' )+1:-1 ]
			try: name = typeClass.CONTROL_NAMES[ idx ]
			except ValueError:
				printErrorStr( 'type: %s  control: %s' % (typeClass, control) )
				raise RigPartError( "Doesn't have a name!" )

			return name

		raise RigPartError( "The control isn't associated with a rig primitive" )
	@classmethod
	def CanRigThisPart( cls, skeletonPart ):
		return True
	@classmethod
	def GetDefaultBuildKwargList( cls ):
		'''
		returns a list of 2 tuples: argName, defaultValue
		'''
		buildFunc = getattr( cls, '_build', None )
		spec = inspect.getargspec( buildFunc )

		argNames = spec[ 0 ][ 2: ]  #strip the first two items because the _build method is a bound method - so the first item is always the class arg (usually called cls), and the second arg is always the skeletonPart
		defaults = spec[ 3 ]

		if defaults is None:
			defaults = []

		assert len( argNames ) == len( defaults ), "%s has no default value set for one of its args - this is not allowed" % cls

		kwargList = []
		for argName, default in zip( argNames, defaults ):
			kwargList.append( (argName, default) )

		return kwargList
	def isPartContained( self ):
		'''
		returns whether this rig part is "contained" by another rig part.  Ie if a rig part was build from within another
		rig part, then it is contained.  Examples of this are things like the arm rig which builds upon the ikfk sub
		primitive rig - the sub-primitive is contained within the arm rig
		'''
		cons = listConnections( '%s.message' % self._container, s=False, type='objectSet' )
		if cons:
			for con in cons:
				if isRigPartContainer( con ):
					rigPart = RigPart( con )
					if isinstance( rigPart, WorldPart ):
						continue

					return True

		return False
	def getBuildKwargs( self ):
		theDict = eval( getAttr( '%s._rigPrimitive.buildKwargs' % self._container ) )
		return theDict
	def getIdx( self ):
		'''
		returns the index of the part - all parts have a unique index associated
		with them
		'''
		if self._idx is None:
			if self._container is None:
				raise RigPartError( 'No index has been defined yet!' )
			else:
				buildKwargs = self.getBuildKwargs()
				self._idx = buildKwargs[ 'idx' ]

		return self._idx
	def getParity( self ):
		return self.getSkeletonPart().getParity()
	def getSuffix( self ):
		return self.getParity().asName()
	def getParityColour( self ):
		return ColourDesc( 'green 0.7' ) if self.getParity() == Parity.LEFT else ColourDesc( 'red 0.7' )
	def getBuildScale( self ):
		return self.getBuildKwargs().get( 'scale', self.PART_SCALE )
	def getWorldPart( self ):
		if self._worldPart is None:
			self._worldPart = worldPart = WorldPart.Create()
			self._worldControl = worldPart.getControl( 'control' )
			self._partsNode = worldPart.getNamedNode( 'parts' )
			self._qss = worldPart.getNamedNode( 'qss' )

		return self._worldPart
	def getWorldControl( self ):
		if self._worldControl is None:
			self.getWorldPart()

		return self._worldControl
	def getPartsNode( self ):
		if self._partsNode is None:
			self.getWorldPart()

		return self._partsNode
	def getQssSet( self ):
		if self._qss is None:
			self.getWorldPart()

		return self._qss
	def getSkeletonPart( self ):
		'''
		returns the skeleton part this rig part is driving
		'''

		#have we cached the skeleton part already?  if so, early out!
		if self._skeletonPart:
			return self._skeletonPart

		if self._container is None:
			return None

		connected = listConnections( '%s.skeletonPart' % self._container )
		if connected is None:
			raise RigPartError( "There is no skeleton part associated with this rig part!  This can happen for a variety of reasons such as name changes on the skeleton in the model file (if you're using referencing), or a incomplete conversion from the old rig format..." )

		if nodeType( connected[0] ) == 'reference':
			raise RigPartError( "A reference node is connected to the skeletonPart attribute - this could mean the model reference isn't loaded, or a node name from the referenced file has changed - either way I can't determine the skeleton part used by this rig!" )

		#cache the value so we can quickly return it on consequent calls
		self._skeletonPart = skeletonPart = SkeletonPart.InitFromItem( connected[0] )

		return skeletonPart
	def getSkeletonPartParity( self ):
		return self.getSkeletonPart().getParity()
	def getControl( self, attrName ):
		'''
		returns the control named <attrName>.  control "names" are defined by the CONTROL_NAMES class
		variable.  This list is asked for the index of <attrName> and the control at that index is returned
		'''
		if self.CONTROL_NAMES is None:
			raise AttributeError( "The %s rig primitive has no named controls" % self.__class__.__name__ )

		idx = list( self.CONTROL_NAMES ).index( attrName )
		if idx < 0:
			raise AttributeError( "No control with the name %s" % attrName )

		connected = listConnections( '%s._rigPrimitive.controls[%d]' % (self._container, idx), d=False )
		if connected:
			assert len( connected ) == 1, "More than one control was found!!!"
			return connected[ 0 ]

		return None
	def getControlIdx( self, control ):
		'''
		returns the index of the given control - each control is plugged into a given "slot"
		'''
		cons = cmd.listConnections( '%s.message' % control, s=False, p=True ) or []
		for c in cons:
			node = c.split( '.' )[0]
			if not isRigPartContainer( node ):
				continue

			if objExists( node ):
				if node != self._container:
					continue

				idx = int( c[ c.rfind( '[' )+1:-1 ] )

				return idx

		raise RigPartError( "The control %s isn't associated with this rig primitive %s" % (control, self) )
	def getControlName( self, control ):
		'''
		returns the name of the control as defined in the CONTROL_NAMES attribute
		for the part class
		'''
		if self.CONTROL_NAMES is None:
			return str( control )

		controlIdx = self.getControlIdx( control )

		try:
			return self.CONTROL_NAMES[ controlIdx ]
		except IndexError:
			return None

		raise RigPartError( "The control %s isn't associated with this rig primitive %s" % (control, self) )
	def getNamedNode( self, nodeName ):
		'''
		returns the "named node" called <nodeName>.  Node "names" are defined by the NAMED_NODE_NAMES class
		variable.  This list is asked for the index of <nodeName> and the node at that index is returned
		'''
		if self.NAMED_NODE_NAMES is None:
			raise AttributeError( "The %s rig primitive has no named nodes" % self.__class__.__name__ )

		idx = list( self.NAMED_NODE_NAMES ).index( nodeName )
		if idx < 0:
			raise AttributeError( "No node with the name %s" % nodeName )

		connected = listConnections( '%s._rigPrimitive.namedNodes[%d]' % (self._container, idx), d=False )
		if connected:
			assert len( connected ) == 1, "More than one node was found!!!"
			return connected[ 0 ]

		return None
	def delete( self ):
		nodes = sets( self._container, q=True )
		for node in nodes:
			cleanDelete( node )

		if objExists( self._container ):
			delete( self._container )

		#if the skeleton part is referenced, clean all reference edits off skeleton part joints
		skeletonPart = self.getSkeletonPart()
		if skeletonPart.isReferenced():
			skeletonPartJoints = skeletonPart.items

			#now unload the reference
			partReferenceFile = Path( referenceQuery( skeletonPart.getContainer(), filename=True ) )
			file( partReferenceFile, unloadReference=True )

			#remove edits from each joint in the skeleton part
			for j in skeletonPartJoints:
				referenceEdit( j, removeEdits=True, successfulEdits=True, failedEdits=True )

			#reload the referenced file
			file( partReferenceFile, loadReference=True )

	### POSE MIRRORING/SWAPPING ###
	def getOppositePart( self ):
		'''
		Finds the skeleton part opposite to the one this rig part controls, and returns its rig part.

		If no rig part can be found, or if no
		'''
		thisSkeletonPart = self.getSkeletonPart()
		oppositeSkeletonPart = thisSkeletonPart.getOppositePart()

		if oppositeSkeletonPart is None:
			return None

		return oppositeSkeletonPart.getRigPart()
	def getOppositeControl( self, control ):
		'''
		Finds the control that is most likely to be opposite the one given.  It first gets the name of
		the given control.  It then finds the opposite rig part, and then queries it for the control
		with the determined name
		'''
		controlIdx = self.getControlIdx( control )
		oppositePart = self.getOppositePart()
		if oppositePart:
			return oppositePart[ controlIdx ]

		return None
	def setupMirroring( self ):
		for control in self:
			if control is None:
				continue

			oppositeControl = self.getOppositeControl( control )
			pair = poseSym.ControlPair.Create( control, oppositeControl )


def getFilePartDict():
	'''
	returns a dictionary keyed by scene name containing a list of the parts contained in that scene
	'''
	scenePartDict = {}

	#special case!  we want to skip parts that are of this exact type - in older rigs this class was a RigSubPart, not a super class for the biped limb classes
	IkFkBaseCls = RigPart.GetNamedSubclass( 'IkFkBase' )

	for rigPart in RigPart.IterAllParts():
		if IkFkBaseCls:
			if type( rigPart ) is IkFkBaseCls:
				continue

		isReferenced = rigPart.isReferenced()
		if isReferenced:
			rigScene = Path( referenceQuery( rigPart.getContainer(), filename=True ) )
		else:
			rigScene = Path( file( q=True, sn=True ) )

		scenePartDict.setdefault( rigScene, [] )
		partList = scenePartDict[ rigScene ]
		partList.append( rigPart )

	return scenePartDict


def generateNiceControlName( control ):
	niceName = getNiceName( control )
	if niceName is not None:
		return niceName

	try:
		rigPart = RigPart.InitFromItem( control )
		if rigPart is None: raise RigPartError( "null" )
		controlName = rigPart.getControlName( control )
	except RigPartError:
		controlName = str( control )

	controlName = Name( controlName )
	parity = controlName.get_parity()

	if parity == Parity.LEFT:
		controlName = 'Left '+ str( stripParity( controlName )  )
	if parity == Parity.RIGHT:
		controlName = 'Right '+ str( stripParity( controlName )  )
	else:
		controlName = str( controlName )

	return camelCaseToNice( controlName )


def getSpaceSwitchControls( theJoint ):
	'''
	walks up the joint chain and returns a list of controls that drive parent joints
	'''
	parentControls = []

	for p in apiExtensions.iterParents( theJoint ):
		theControl = getItemRigControl( p )
		if theControl is not None:
			parentControls.append( theControl )

	return parentControls


def buildDefaultSpaceSwitching( theJoint, control=None, additionalParents=(), additionalParentNames=(), reverseHierarchy=False, **buildKwargs ):
	if control is None:
		control = getItemRigControl( theJoint )

	theWorld = WorldPart.Create()
	spaces = getSpaceSwitchControls( theJoint )
	spaces.append( theWorld.getControl( 'control' ) )

	#determine default names for the given controls
	names = []
	for s in spaces:
		names.append( generateNiceControlName( s ) )

	additionalParents = list( additionalParents )
	additionalParentNames = list( additionalParentNames )

	for n in range( len( additionalParentNames ), len( additionalParents ) ):
		additionalParentNames.append( generateNiceControlName( additionalParents[ n ] ) )

	spaces += additionalParents
	names += additionalParentNames

	#we don't care about space switching if there aren't any non world spaces...
	if not spaces:
		return

	if reverseHierarchy:
		spaces.reverse()
		names.reverse()

	return spaceSwitching.build( control, spaces, names, **buildKwargs )


def getParentAndRootControl( theJoint ):
	'''
	returns a 2 tuple containing the nearest control up the hierarchy, and the
	most likely control to use as the "root" control for the rig.  either of these
	may be the world control, but both values are guaranteed to be an existing
	control object
	'''
	parentControl, rootControl = None, None
	for p in apiExtensions.iterParents( theJoint ):
		theControl = getItemRigControl( p )
		if theControl is None:
			continue

		if parentControl is None:
			parentControl = theControl

		skelPart = SkeletonPart.InitFromItem( p )
		if isinstance( skelPart, skeletonBuilder.Root ):
			rootControl = theControl

	if parentControl is None or rootControl is None:
		world = WorldPart.Create()
		if parentControl is None:
			parentControl = world.getControl( 'control' )

		if rootControl is None:
			rootControl = world.getControl( 'control' )

	return parentControl, rootControl


def createLineOfActionMenu( controls, joints ):
	'''
	deals with adding a "draw line of action" menu to each control in the controls
	list.  the line is drawn through the list of joints passed
	'''
	if not joints: return
	if not isinstance( controls, (list, tuple) ):
		controls = [ controls ]

	joints = list( joints )
	jParent = getNodeParent( joints[ 0 ] )
	if jParent:
		joints.insert( 0, jParent )

	for c in controls:
		cTrigger = Trigger( c )
		spineConnects = [ cTrigger.connect( j ) for j in joints ]
		Trigger.CreateMenu( c,
		                    "draw line of action",
		                    "zooLineOfAction;\nzooLineOfAction_multi { %s } \"\";" % ', '.join( '"%%%d"'%idx for idx in spineConnects ) )


class RigSubPart(RigPart):
	'''
	'''

	#this attribute describes what skeleton parts the rig primitive is associated with.  If the attribute's value is None, then the rig primitive
	#is considered a "hidden" primitive that has
	SKELETON_PRIM_ASSOC = None


class PrimaryRigPart(RigPart):
	'''
	all subclasses of this class are exposed as available rigging methods to the user
	'''

	AVAILABLE_IN_UI = True


class WorldPart(RigPart):
	'''
	the world part can only be created once per scene.  if an existing world part instance is found
	when calling WorldPart.Create() it will be returned instead of creating a new instance
	'''

	__version__ = 0
	CONTROL_NAMES = 'control', 'exportRelative'
	NAMED_NODE_NAMES = 'parts', 'masterQss', 'qss'

	WORLD_OBJ_MENUS = [ ('toggle rig vis', """{\nstring $childs[] = `listRelatives -pa -type transform #`;\nint $vis = !`getAttr ( $childs[0]+\".v\" )`;\nfor($a in $childs) if( `objExists ( $a+\".v\" )`) if( `getAttr -se ( $a+\".v\" )`) setAttr ( $a+\".v\" ) $vis;\n}"""),
	                    ('draw all lines of action', """string $menuObjs[] = `zooGetObjsWithMenus`;\nfor( $m in $menuObjs ) {\n\tint $cmds[] = `zooObjMenuListCmds $m`;\n\tfor( $c in $cmds ) {\n\t\tstring $name = `zooGetObjMenuCmdName $m $c`;\n\t\tif( `match \"draw line of action\" $name` != \"\" ) eval(`zooPopulateCmdStr $m (zooGetObjMenuCmdStr($m,$c)) {}`);\n\t\t}\n\t}"""),
	                    ('show "export relative" node', """""") ]

	@classmethod
	@d_unifyUndo
	def Create( cls, **kw ):
		for existingWorld in cls.IterAllParts():
			return existingWorld

		#try to determine scale - walk through all existing skeleton parts in the scene
		for skeletonPart in SkeletonPart.IterAllPartsInOrder():
			kw.setdefault( 'scale', skeletonPart.getBuildScale() )
			break

		worldNodes, (controls, namedNodes) = getNodesCreatedBy( cls._build, **kw )
		worldPart = buildContainer( WorldPart, { 'idx': 0 }, worldNodes, controls, namedNodes )

		#check to see if there is a layer for the rig controls and add controls to it
		if objExists( 'rig_controls' ) and nodeType( 'rig_controls' ) == 'displayLayer':
			rigLayer = 'rig_controls'
		else:
			rigLayer = createDisplayLayer( name='rig_controls', empty=True )

		editDisplayLayerMembers( rigLayer, controls, noRecurse=True )

		return worldPart
	@classmethod
	def _build( cls, **kw ):
		scale = kw.get( 'scale', skeletonBuilder.TYPICAL_HEIGHT )
		scale /= 1.5

		world = buildControl( 'main', shapeDesc=ShapeDesc( None, 'hex', AX_Y ), oriented=False, scale=scale, niceName='The World' )

		parts = group( empty=True, name='parts_grp' )
		qss = sets( empty=True, text="gCharacterSet", n="body_ctrls" )
		masterQss = sets( empty=True, text="gCharacterSet", n="all_ctrls" )

		exportRelative = buildControl( 'exportRelative', shapeDesc=ShapeDesc( None, 'cube', AX_Y_NEG ), pivotModeDesc=PivotModeDesc.BASE, oriented=False, size=(1, 0.5, 1), scale=scale )
		parentConstraint( world, exportRelative )
		attrState( exportRelative, ('t', 'r', 's'), *LOCK_HIDE )
		attrState( exportRelative, 'v', *HIDE )
		setAttr( '%s.v' % exportRelative, False )

		#turn scale segment compensation off for all joints in the scene
		for j in ls( type='joint' ):
			setAttr( '%s.ssc' % j, False )

		sets( qss, add=masterQss )

		attrState( world, 's', *NORMAL )
		connectAttr( '%s.scale' % world, '%s.scale' % parts )
		connectAttr( '%s.scaleX' % world, '%s.scaleY' % world )
		connectAttr( '%s.scaleX' % world, '%s.scaleZ' % world )

		#add right click items to the world controller menu
		worldTrigger = Trigger( str( world ) )
		qssIdx = worldTrigger.connect( str( masterQss ) )


		#add world control to master qss
		sets( world, add=masterQss )
		sets( exportRelative, add=masterQss )


		#turn unwanted transforms off, so that they are locked, and no longer keyable
		attrState( world, 's', *NO_KEY )
		attrState( world, ('sy', 'sz'), *LOCK_HIDE )
		attrState( parts, [ 't', 'r', 's', 'v' ], *LOCK_HIDE )


		controls = world, exportRelative
		namedNodes = parts, masterQss, qss

		return controls, namedNodes
	def getSkeletonPart( self ):
		#the world part has no skeleton part...
		return None
	def setupMirroring( self ):
		pair = poseSym.ControlPair.Create( self.getControl( 'control' ) )
		pair.setFlips( 0 )


### <CHEEKY!> ###
'''
these functions get added to the SkeletonPart class as a way of implementing functionality that relies on
the RigPart class - which isn't available in the baseSkeletonPart script (otherwise you'd have a circular
import dependency)
'''

def _getRigContainer( self ):
	'''
	returns the container for the rig part - if this part is rigged.  None is returned otherwise

	NOTE: the container is returned instead of the rig instance because this script can't import
	the RigPart base class without causing circular import statements - there is a getRigPart
	method that is implemented in the baseRigPrimitive script that gets added to this class
	'''
	rigContainerAttrpath = '%s.rigContainer' % self.getContainer()
	if objExists( rigContainerAttrpath ):
		cons = listConnections( rigContainerAttrpath, d=False )
		if cons:
			return cons[0]

	cons = listConnections( '%s.message' % self.getContainer(), s=False, type='objectSet' )
	if cons:
		connectedRigParts = []
		for con in cons:
			if isRigPartContainer( con ):
				connectedRigParts.append( RigPart( con ) )

		#now we have a list of connected rig parts - lets figure out which ones are "top level" parts - ie don't belong to another part
		if connectedRigParts:
			for rigPart in connectedRigParts:
				if not rigPart.isPartContained():
					return rigPart

	return None

def _getRigPart( self ):
	rigContainer = self.getRigContainer()
	if rigContainer:
		return RigPart( self.getRigContainer() )

	return None

SkeletonPart.getRigContainer = _getRigContainer
SkeletonPart.getRigPart = _getRigPart


def _deleteRig( self ):
	rigPart = self.getRigPart()
	rigPart.delete()

SkeletonPart.deleteRig = d_unifyUndo( _deleteRig )

### </CHEEKY!> ###


@d_unifyUndo
def setupMirroring():
	'''
	sets up all controls in the scene for mirroring
	'''
	for rigPart in RigPart.IterAllParts():
		rigPart.setupMirroring()


@d_unifyUndo
@d_showWaitCursor
def buildRigForModel( scene=None, referenceModel=True, deletePlacers=False ):
	'''
	given a model scene whose skeleton is assumed to have been built by the
	skeletonBuilder tool, this function will create a rig scene by referencing
	in said model, creating the rig as best it knows how, saving the scene in
	the appropriate spot etc...
	'''

	#if no scene was passed, assume we're acting on the current scene
	if scene is None:
		scene = Path( cmd.file( q=True, sn=True ) )
	#if the scene WAS passed in, open the desired scene if it isn't already open
	else:
		scene = Path( scene )
		curScene = Path( cmd.file( q=True, sn=True ) )
		if curScene:
			if scene != curScene:
				mel.saveChanges( 'file -f -open "%s"' % scene )
		else: cmd.file( scene, f=True, open=True )

	#if the scene is still none bail...
	if not scene and referenceModel:
		raise SceneNotSavedError( "Uh oh, your scene hasn't been saved - Please save it somewhere on disk so I know where to put the rig.  Thanks!" )

	#backup the current state of the scene, just in case something goes south...
	if scene.exists():
		backupFilename = scene.up() / ('%s_backup.%s' % (scene.name(), scene.getExtension()))
		if backupFilename.exists():
			backupFilename.delete()

		cmd.file( rename=backupFilename )
		cmd.file( save=True, force=True )
		cmd.file( rename=scene )

	#finalize
	failedParts = finalizeAllParts()
	if failedParts:
		confirmDialog( t='Finalization Failure', m='The following parts failed to finalize properly:\n\n%s' % '\n'.join( map( str, failedParts ) ), b='OK', db='OK' )
		return

	#delete placers if desired - NOTE: this should be done after after finalization because placers are often used to define alignment for end joints
	if deletePlacers:
		for part in SkeletonPart.IterAllParts():
			placers = part.getPlacers()
			if placers:
				delete( placers )

	#if desired, create a new scene and reference in the model
	if referenceModel:

		#remove any unknown nodes in the scene - these cause maya to barf when trying to save
		unknownNodes = ls( type='unknown' )
		if unknownNodes:
			delete( unknownNodes )

		#scene.editoradd()
		cmd.file( f=True, save=True )
		cmd.file( f=True, new=True )

		referenceFile( scene, 'model' )

		#rename the scene to the rig
		rigSceneName = '%s_rig.ma' % scene.name()
		rigScene = scene.up() / rigSceneName
		cmd.file( rename=rigScene )
		cmd.file( f=True, save=True, typ='mayaAscii' )
	else:
		rigScene = scene

	buildRigForAllParts()
	setupMirroring()

	return rigScene


@d_unifyUndo
def buildRigForAllParts():
	for part in SkeletonPart.IterAllPartsInOrder():
		part.rig()

	#create a layer for the skeleton
	for rootPart in Root.IterAllParts():
		pass


@d_unifyUndo
def cleanMeshControls( doConfirm=True ):
	shapesRemoved = 0
	for node in getRigPartContainers( True ):

		clsName = getAttr( '%s._rigPrimitive.typeName' % node )
		cls = RigPart.GetNamedSubclass( clsName )

		if cls is None:
			continue

		rigPart = cls( node )
		for c in rigPart:
			for shape in listRelatives( c, s=True, pa=True ) or []:
				if getAttr( '%s.intermediateObject' % shape ):
					delete( shape )
					shapesRemoved += 1

	printInfoStr( "Clean up %d bogus shapes" % shapesRemoved )
	if doConfirm:
		cmd.confirmDialog( t='Done!', m="I'm done polishing your rig!\n%d shapes removed." % shapesRemoved, b='OK', db='OK' )


#end
