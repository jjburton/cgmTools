
from zooPy.vectors import Vector, Matrix, Axis, AX_X, AX_Y, AX_Z

from rigUtils import MATRIX_ROTATION_ORDER_CONVERSIONS_FROM, MATRIX_ROTATION_ORDER_CONVERSIONS_TO
from mayaDecorators import d_unifyUndo
import apiExtensions

import maya
from maya.cmds import *
from maya.OpenMaya import MGlobal

AXES = Axis.BASE_AXES

#try to load the zooMirror.py plugin
try:
	loadPlugin( 'zooMirror.py', quiet=True )
except:
	import zooToolbox
	zooToolbox.loadZooPlugin( 'zooMirror.py' )


def getLocalRotMatrix( obj ):
	'''
	returns the local matrix for the given obj
	'''
	localMatrix = Matrix( getAttr( '%s.matrix' % obj ), 4 )
	localMatrix.set_position( (0, 0, 0) )

	return localMatrix


def getWorldRotMatrix( obj ):
	'''
	returns the world matrix for the given obj
	'''
	worldMatrix = Matrix( getAttr( '%s.worldMatrix' % obj ), 4 )
	worldMatrix.set_position( (0, 0, 0) )

	return worldMatrix


def setWorldRotMatrix( obj, matrix ):
	'''
	given a world matrix, will set the transforms of the object
	'''
	parentInvMatrix = Matrix( getAttr( '%s.parentInverseMatrix' % obj ) )
	localMatrix = matrix * parentInvMatrix

	setLocalRotMatrix( obj, localMatrix )


@d_unifyUndo
def setLocalRotMatrix( obj, matrix ):
	'''
	given a world matrix, will set the transforms of the object
	'''

	roo = getAttr( '%s.rotateOrder' % obj )
	rot = MATRIX_ROTATION_ORDER_CONVERSIONS_TO[ roo ]( matrix, True )

	#try to set the rotation - check whether all the rotation channels are settable
	if getAttr( '%s.r' % obj, se=True ):
		setAttr( '%s.r' % obj, *rot )


def mirrorMatrix( matrix, axis=AX_X, orientAxis=AX_X ):
	'''
	axis is the axis things are flipped across
	orientAxis is the axis that gets flipped when mirroring orientations
	'''
	assert isinstance( matrix, Matrix )
	mirroredMatrix = Matrix( matrix )

	#make sure we've been given a Axis instances...  don't bother testing, just do it, and make it absolute (non-negative - mirroring in -x is the same as mirroring in x)
	mirrorAxis = abs( Axis( axis ) )
	axisA = abs( Axis( orientAxis ) )

	#flip all axes
	axisB, axisC = axisA.otherAxes()
	mirroredMatrix[ axisB ][ mirrorAxis ] = -matrix[ axisB ][ mirrorAxis ]
	mirroredMatrix[ axisC ][ mirrorAxis ] = -matrix[ axisC ][ mirrorAxis ]

	#the above flipped all axes - but this results in a changing of coordinate system handed-ness, so flip one of the axes back
	nonMirrorAxisA, nonMirrorAxisB = mirrorAxis.otherAxes()
	mirroredMatrix[ axisA ][ nonMirrorAxisA ] = -mirroredMatrix[ axisA ][ nonMirrorAxisA ]
	mirroredMatrix[ axisA ][ nonMirrorAxisB ] = -mirroredMatrix[ axisA ][ nonMirrorAxisB ]

	#if the input matrix was a 4x4 then mirror translation
	if matrix.size == 4:
		mirroredMatrix[3][ mirrorAxis ] = -matrix[3][ mirrorAxis ]

	return mirroredMatrix


def getKeyableAttrs( obj ):
	attrs = listAttr( obj, keyable=True )
	if attrs is None:
		return []

	for attrToRemove in ('translate', 'translateX', 'translateY', 'translateZ', \
	                     'rotate', 'rotateX', 'rotateY', 'rotateZ'):
		try:
			attrs.remove( attrToRemove )
		except ValueError: pass

	return attrs


class CommandStack(list):
	def append( self, func, *a, **kw ):
		list.append( self, (func, a, kw) )
	def execute( self ):
		for func, a, kw in self:
			func( *a, **kw )


class ControlPair(object):
	'''
	sets up a relationship between two controls so that they can mirror/swap/match one
	another's poses.

	NOTE: when you construct a ControlPair setup (using the Create classmethod)
	'''

	#NOTE: these values are copied from the zooMirror script - they're copied because the plugin generally doesn't exist on the pythonpath so we can't rely on an import working....
	FLIP_AXES = (), (AX_X, AX_Y), (AX_X, AX_Z), (AX_Y, AX_Z)

	@classmethod
	def GetPairNode( cls, obj ):
		'''
		given a transform will return the pair node the control is part of
		'''

		if obj is None:
			return None

		if objectType( obj, isAType='transform' ):
			cons = listConnections( '%s.message' % obj, s=False, type='controlPair' )
			if not cons:
				return None

			return cons[0]

		if nodeType( obj ) == 'controlPair':
			return obj

		return None
	@classmethod
	@d_unifyUndo
	def Create( cls, controlA, controlB=None, axis=None ):
		'''
		given two controls will setup the relationship between them

		NOTE: if controlB isn't given then it will only be able to mirror its current
		pose.  This is usually desirable on "central" controls like spine, head and
		neck controls
		'''

		#make sure we've been given transforms - mirroring doesn't make a whole lotta sense on non-transforms
		if not objectType( controlA, isAType='transform' ):
			return None

		if controlB:

			#if controlA is the same node as controlB then set controlB to None - this makes it more obvious the pair is singular
			#NOTE: cmpNodes compares the actual MObjects, not the node names - just in case we've been handed a full path and a partial path that are the same node...
			if apiExtensions.cmpNodes( controlA, controlB ):
				controlB = None
			elif not objectType( controlB, isAType='transform' ):
				return None

		#see if we have a pair node for the controls already
		pairNode = cls.GetPairNode( controlA )
		if pairNode:
			#if no controlB has been given see whether the pairNode we've already got also has no controlB - if so, we're done
			if not controlB:
				new = cls( pairNode )
				if not new.controlB:
					return new

			#if controlB HAS been given, check whether to see whether it has the same pairNode - if so, we're done
			if controlB:
				pairNodeB = cls.GetPairNode( controlB )
				if pairNode == pairNodeB:
					return cls( pairNode )

		#otherwise create a new one
		pairNode = createNode( 'controlPair' )
		connectAttr( '%s.message' % controlA, '%s.controlA' % pairNode )
		if controlB:
			connectAttr( '%s.message' % controlB, '%s.controlB' % pairNode )

		#name the node
		nodeName = '%s_mirrorConfig' if controlB is None else '%s_%s_exchangeConfig' % (controlA, controlB)
		pairNode = rename( pairNode, nodeName )

		#instantiate it and run the initial setup code over it
		new = cls( pairNode )
		new.setup( axis )

		return new

	def __init__( self, pairNodeOrControl ):
		self.node = pairNode = self.GetPairNode( pairNodeOrControl )
		self.controlA = None
		self.controlB = None

		cons = listConnections( '%s.controlA' % pairNode, d=False )
		if cons:
			self.controlA = cons[0]

		cons = listConnections( '%s.controlB' % pairNode, d=False )
		if cons:
			self.controlB = cons[0]

		#make sure we have a control A
		if self.controlA is None:
			raise TypeError( "Could not find controlA - need to!" )
	def __eq__( self, other ):
		if isinstance( other, ControlPair ):
			other

		return self.node == other.node
	def __ne__( self, other ):
		return not self.__eq__( other )
	def __hash__( self ):
		return hash( self.node )
	def getAxis( self ):
		return Axis( getAttr( '%s.axis' % self.node ) )
	@d_unifyUndo
	def setAxis( self, axis ):
		setAttr( '%s.axis' % self.node, axis )
	def getFlips( self ):
		axes = getAttr( '%s.flipAxes' % self.node )
		return list( self.FLIP_AXES[ axes ] )
	@d_unifyUndo
	def setFlips( self, flips ):
		if isinstance( flips, int ):
			setAttr( '%s.flipAxes' % self.node, flips )
	def getWorldSpace( self ):
		return getAttr( '%s.worldSpace' % self.node )
	@d_unifyUndo
	def setWorldSpace( self, state ):
		setAttr( '%s.worldSpace' % self.node, state )
	def isSingular( self ):
		if self.controlB is None:
			return True

		#a pair is also singular if controlA is the same as controlB
		#NOTE: cmpNodes does a rigorous comparison so it will catch a fullpath and a partial path that point to the same node
		if apiExtensions.cmpNodes( self.controlA, self.controlB ):
			return True

		return False
	def neverDoT( self ):
		return getAttr( '%s.neverDoT' % self.node )
	def neverDoR( self ):
		return getAttr( '%s.neverDoR' % self.node )
	def neverDoOther( self ):
		return getAttr( '%s.neverDoOther' % self.node )
	@d_unifyUndo
	def setup( self, axis=None ):
		'''
		sets up the initial state of the pair node
		'''

		if axis:
			axis = abs( Axis( axis ) )
			setAttr( '%s.axis' % self.node, axis )

		#if we have two controls try to auto determine the orientAxis and the flipAxes
		if self.controlA and self.controlB:
			worldMatrixA = getWorldRotMatrix( self.controlA )
			worldMatrixB = getWorldRotMatrix( self.controlB )

			#so restPoseB = restPoseA * offsetMatrix
			#restPoseAInv * restPoseB = restPoseAInv * restPoseA * offsetMatrix
			#restPoseAInv * restPoseB = I * offsetMatrix
			#thus offsetMatrix = restPoseAInv * restPoseB
			offsetMatrix = worldMatrixA.inverse() * worldMatrixB

			AXES = AX_X.asVector(), AX_Y.asVector(), AX_Z.asVector()
			flippedAxes = []
			for n in range( 3 ):
				axisNVector = Vector( offsetMatrix[ n ][ :3 ] )

				#if the axes are close to being opposite, then consider it a flipped axis...
				if axisNVector.dot( AXES[n] ) < -0.8:
					flippedAxes.append( n )

			for n, flipAxes in enumerate( self.FLIP_AXES ):
				if tuple( flippedAxes ) == flipAxes:
					setAttr( '%s.flipAxes' % self.node, n )
					break

		#this is a bit of a hack - and not always true, but generally singular controls built by skeleton builder will work with this value
		elif self.controlA:
			setAttr( '%s.flipAxes' % self.node, 0 )
			self.setWorldSpace( False )
	def mirrorMatrix( self, matrix ):
		matrix = mirrorMatrix( matrix, self.getAxis() )
		for flipAxis in self.getFlips():
			matrix.setRow( flipAxis, -Vector( matrix.getRow( flipAxis ) ) )

		return matrix
	@d_unifyUndo
	def swap( self, t=True, r=True, other=True, cmdStack=None ):
		'''
		mirrors the pose of each control, and swaps them
		'''
		executeImmediately = False
		if cmdStack is None:
			cmdStack = CommandStack()
			executeImmediately = True

		#if there is no controlB, then perform a mirror instead...
		if not self.controlB:
			self.mirror()
			return

		worldSpace = self.getWorldSpace()

		#do the other attributes first - the parent attribute for example will change the position so we need to set it before setting transforms
		if other:
			if not self.neverDoOther():
				if not self.isSingular():
					for attr in getKeyableAttrs( self.controlA ):
						attrPathA = '%s.%s' % (self.controlA, attr)
						attrPathB = '%s.%s' % (self.controlB, attr)
						if objExists( attrPathA ) and objExists( attrPathB ):
							attrValA = getAttr( attrPathA )
							attrValB = getAttr( attrPathB )

							#make sure the attributes are settable before trying setAttr
							if getAttr( attrPathA, se=True ):
								cmdStack.append( setAttr, attrPathA, attrValB )

							if getAttr( attrPathB, se=True ):
								cmdStack.append( setAttr, attrPathB, attrValA )

		#do rotation
		if r:
			if not self.neverDoR():
				if worldSpace:
					getMatrix = getWorldRotMatrix
					setMatrix = setWorldRotMatrix
				else:
					getMatrix = getLocalRotMatrix
					setMatrix = setLocalRotMatrix

				worldMatrixA = getMatrix( self.controlA )
				worldMatrixB = getMatrix( self.controlB )

				newB = self.mirrorMatrix( worldMatrixA )
				newA = self.mirrorMatrix( worldMatrixB )

				cmdStack.append( setMatrix, self.controlA, newA )
				cmdStack.append( setMatrix, self.controlB, newB )

		#do position
		if t:
			if not self.neverDoT():
				axis = self.getAxis()
				if worldSpace:
					newPosA = xform( self.controlB, q=True, ws=True, rp=True )
					newPosB = xform( self.controlA, q=True, ws=True, rp=True )
				else:
					newPosA = list( getAttr( '%s.t' % self.controlB )[0] )
					newPosB = list( getAttr( '%s.t' % self.controlA )[0] )

				newPosA[ axis ] = -newPosA[ axis ]
				newPosB[ axis ] = -newPosB[ axis ]

				if worldSpace:
					if getAttr( '%s.t' % self.controlA, se=True ):
						cmdStack.append( move, newPosA[0], newPosA[1], newPosA[2], self.controlA, ws=True, rpr=True )
					if getAttr( '%s.t' % self.controlB, se=True ):
						cmdStack.append( move, newPosB[0], newPosB[1], newPosB[2], self.controlB, ws=True, rpr=True )
				else:
					if getAttr( '%s.t' % self.controlA, se=True ):
						cmdStack.append( setAttr, '%s.t' % self.controlA, *newPosA )

					if getAttr( '%s.t' % self.controlB, se=True ):
						cmdStack.append( setAttr, '%s.t' % self.controlB, *newPosB )

		if executeImmediately:
			cmdStack.execute()
	@d_unifyUndo
	def mirror( self, controlAIsSource=True, t=True, r=True, other=True ):
		'''
		mirrors the pose of controlA (or controlB if controlAIsSource is False) and
		puts it on the "other" control

		NOTE: if controlAIsSource is True, then the pose of controlA is mirrored
		and put on to controlB, otherwise the reverse is done
		'''

		if self.isSingular():
			control = otherControl = self.controlA
		else:
			if controlAIsSource:
				control = self.controlB
				otherControl = self.controlA
			else:
				control = self.controlA
				otherControl = self.controlB

		#do the other attributes first - the parent attribute for example will change the position so we need to set it before setting transforms
		if other:
			if not self.neverDoOther():
				if not self.isSingular():
					for attr in getKeyableAttrs( otherControl ):
						attrPath = '%s.%s' % (control, attr)
						otherAttrPath = '%s.%s' % (otherControl, attr)

						if objExists( attrPath ):
							if getAttr( attrPath, se=True ):
								setAttr( attrPath, getAttr( otherAttrPath ) )

		worldSpace = self.getWorldSpace()

		#do rotation
		if r:
			if not self.neverDoR():
				if worldSpace:
					getMatrix = getWorldRotMatrix
					setMatrix = setWorldRotMatrix
				else:
					getMatrix = getLocalRotMatrix
					setMatrix = setLocalRotMatrix

				matrix = getMatrix( otherControl )
				newMatrix = self.mirrorMatrix( matrix )
				setMatrix( control, newMatrix )

		#do position
		if t:
			if not self.neverDoT():
				if worldSpace:
					pos = xform( otherControl, q=True, ws=True, rp=True )
					pos[ self.getAxis() ] = -pos[ self.getAxis() ]
					try:
						move( pos[0], pos[1], pos[2], control, ws=True, rpr=True )
					except RuntimeError: pass
				else:
					pos = list( getAttr( '%s.t' % otherControl )[0] )
					pos[ self.getAxis() ] = -pos[ self.getAxis() ]
					try:
						setAttr( '%s.t' % control, *pos )
					except RuntimeError: pass
	@d_unifyUndo
	def match( self, controlAIsSource=True, t=True, r=True, other=True ):
		'''
		pushes the pose of controlA (or controlB if controlAIsSource is False) to the
		"other" control

		NOTE: if controlAIsSource is True, then the pose of controlA is mirrored and
		copied and put on to controlB, otherwise the reverse is done
		'''

		#if this is a singular pair, bail - there's nothing to do
		if self.isSingular():
			return

		#NOTE:
		#restPoseB = restPoseA * offsetMatrix
		#and similarly:
		#so restPoseB * offsetMatrixInv = restPoseA

		if controlAIsSource:
			worldMatrix = getWorldRotMatrix( self.controlA )
			control = self.controlB
		else:
			worldMatrix = getWorldRotMatrix( self.controlB )
			control = self.controlA

		newControlMatrix = self.mirrorMatrix( worldMatrix )

		setWorldRotMatrix( control, newControlMatrix, t=False )
		setWorldRotMatrix( control, worldMatrix, r=False )


def getPairNodesFromObjs( objs ):
	'''
	given a list of objects, will return a minimal list of pair nodes
	'''
	pairs = set()
	for obj in objs:
		pairNode = ControlPair.GetPairNode( obj )
		if pairNode:
			pairs.add( pairNode )

	return list( pairs )


def getPairsFromObjs( objs ):
	return [ ControlPair( pair ) for pair in getPairNodesFromObjs( objs ) ]


def getPairsFromSelection():
	return getPairsFromObjs( ls( sl=True ) )


def iterPairAndObj( objs ):
	'''
	yields a 2-tuple containing the pair node and the initializing object
	'''
	pairNodesVisited = set()
	for obj in apiExtensions.sortByHierarchy( objs ):
		pairNode = ControlPair.GetPairNode( obj )
		if pairNode:
			if pairNode in pairNodesVisited:
				continue

			pair = ControlPair( pairNode )

			yield pair, obj
			pairNodesVisited.add( pairNode )


@d_unifyUndo
def setupMirroringFromNames( mandatoryTokens=('control', 'ctrl') ):
	'''
	sets up control pairs for all parity based controls in the scene as determined by their names.
	'''
	import names

	#stick the tokens in a set and ensure they're lower-case
	mandatoryTokens = set( [ tok.lower() for tok in mandatoryTokens ] )

	visitedTransforms = set()
	for t in ls( type='transform' ):
		if t in visitedTransforms:
			continue

		visitedTransforms.add( t )

		tName = names.Name( t )
		if tName.get_parity() is names.Parity.NONE:
			continue

		containsMandatoryToken = False
		for tok in tName.split():
			if tok.lower() in mandatoryTokens:
				containsMandatoryToken = True
				break

		if not containsMandatoryToken:
			continue

		otherT = names.Name( tName ).swap_parity()  #swap_parity changes the parity of the instance - Name objects are mutable...  ugh!  should re-write it
		if otherT:
			if objExists( str( otherT ) ):
				visitedTransforms.add( str( otherT ) )

				#sort the controls into left and right - we want the left to be controlA and right to be controlB
				controlPairs = [(tName.get_parity(), tName), (otherT.get_parity(), otherT)]
				controlPairs.sort()

				leftT, rightT = str( controlPairs[0][1] ), str( controlPairs[1][1] )

				ControlPair.Create( leftT, rightT )
				print 'creating a control pair on %s -> %s' % (leftT, rightT)


#end
