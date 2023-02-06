
from baseRigPrimitive import *


class StretchRig(RigSubPart):
	'''
	creates stretch attribs on the given control, and makes all given joints stretchy
	-------

	control		the character prefix used to identify the character
	parity		which side is the arm on?  l (left) or r (right)
	axis 		the stretch axis used by the joints in the limb.  default: x
	parity		the parts node is simply an object that miscellanous dag nodes are parented under - if not specified, miscellanous objects are simply left in worldspace
	'''

	__version__ = 0
	NAMED_NODE_NAMES = 'autoLengthBlender', 'ikfkBlender', 'lengthMods', 'lengthClamp'
	ADD_CONTROLS_TO_QSS = False

	def _build( self, skeletonPart, control, joints, ikFkBlendAttrpath=None, axis=BONE_AIM_AXIS, parity=Parity.LEFT, elbowPos=1, connectEndJoint=False, **kw ):
		'''
		ikFkBlendAttrpath		this should be the attribute that turns ik on when its value is 1, and off when its value is 0
		'''
		#do some sanity checking
		if not joints:
			raise RigPartError( "No joints supplied - you must supply a list of joints to stretch!" )

		if ikFkBlendAttrpath is None:
			ikFkBlendAttrpath = '%s.ikBlend' % control

		if axis is None:
			raise NotImplemented( 'auto axis support not written yet - complain loudly!' )


		#setup some current unit variables, and take parity into account
		stretchAuto = "autoStretch"
		stretchName = "stretch"
		parityFactor = parity.asMultiplier()

		addAttr( control, ln=stretchAuto, at='double', min=0, max=1, dv=1 )
		addAttr( control, ln=stretchName, at='double', min=-10, max=10, dv=0 )
		attrState( control, (stretchAuto, stretchName), keyable=True )


		#build the network for distributing stretch from the fk controls to the actual joints
		plusNodes = []
		initialNodes = []
		fractionNodes = []
		allNodes = []

		for c in joints:
			md = shadingNode( 'multiplyDivide', asUtility=True, name='%s_fraction_pos' % str( c ) )
			fractionNodes.append( md )

		startObj = joints[0]
		endObj = control

		clientLengths = [ 0 ]
		totalLength = 0
		for n, c in enumerate( joints[ :-1 ] ):
			thisPos = Vector( xform( c, q=True, ws=True, rp=True ) )
			nextPos = Vector( xform( joints[ n+1 ], q=True, ws=True, rp=True ) )
			l = (thisPos - nextPos).length()
			clientLengths.append( l )
			totalLength += l


		#build the network to measure limb length
		loc_a = group( empty=True )
		loc_b = group( empty=True )
		measure = loc_b

		parent( loc_b, loc_a )
		parent( loc_a, self.getPartsNode() )
		constraint_a = pointConstraint( startObj, loc_a )[ 0 ]

		aim = aimConstraint( endObj, loc_a, aimVector=(1,0,0) )[ 0 ]
		setAttr( '%s.tx' % loc_b, totalLength )
		constraint_b = pointConstraint( endObj, loc_b )[ 0 ]
		attrState( [ loc_a, loc_b ], ('t', 'r'), *LOCK_HIDE )


		#create the stretch network
		autoLengthBlender = shadingNode( 'blendColors', asUtility=True, n='auto_length_blender' )
		fkikBlender = shadingNode( 'blendColors', asUtility=True, n='fkik_blender' )  #turns auto length off when using fk
		lengthMods = shadingNode( 'plusMinusAverage', asUtility=True, n='length_mods' )  #adds all lengths together
		lengthClamp = shadingNode( 'clamp', asUtility=True, n='length_clamp' )  #clamps the min/max length for the limb
		manualStretchMult = shadingNode( 'multiplyDivide', asUtility=True, n='manualStretch_range_multiplier' )  #multiplys manual stretch to a sensible range


		#NOTE: the second term attribute of the length condition node holds the initial length for the limb, and is thus connected to the false attribute of all condition nodes
		setAttr( '%s.input2X' % manualStretchMult, totalLength / 10 )
		setAttr( '%s.minR' % lengthClamp, totalLength )
		setAttr( '%s.color2R' % autoLengthBlender, totalLength )
		setAttr( '%s.color2R' % fkikBlender, totalLength )
		setAttr( '%s.maxR' % lengthClamp, totalLength * 5 )

		connectAttr( '%s.tx' % measure, '%s.inputR' % lengthClamp, f=True )
		connectAttr( ikFkBlendAttrpath, '%s.blender' % fkikBlender, f=True )
		connectAttr( '%s.outputR' % lengthClamp, '%s.color1R' % fkikBlender, f=True )
		connectAttr( '%s.outputR' % fkikBlender, '%s.color1R' % autoLengthBlender, f=True )
		connectAttr( '%s.%s' % (control, stretchAuto), '%s.blender' % autoLengthBlender, f=True )
		connectAttr( '%s.outputR' % autoLengthBlender, '%s.input1D[ 0 ]' % lengthMods, f=True )

		connectAttr( '%s.%s' % (control, stretchName), '%s.input1X' % manualStretchMult, f=True )
		connectAttr( '%s.outputX' % manualStretchMult, '%s.input1D[ 1 ]' % lengthMods, f=True )


		#connect the stretch distribution network up - NOTE this loop starts at 1 because we don't need to connect the
		#start of the limb chain (ie the bicep or the thigh) as it doesn't move
		if connectEndJoint:
			jIter = enumerate( joints )
		else:
			jIter = enumerate( joints[ :-1 ] )

		for n, c in enumerate( joints ):
			if n == 0:
				continue

			setAttr( '%s.input2X' % fractionNodes[ n ], clientLengths[ n ] / totalLength * parityFactor )

			#now connect the inital coords to the plus node - then connect the
			connectAttr( '%s.output1D' % lengthMods, '%s.input1X' % fractionNodes[ n ], f=True )

			#try to unlock the tx attr
			if getAttr( '%s.tx' % joints[ n ], lock=True ):
				if referenceQuery( joints[ n ], inr=True ):
					raise TypeError( "The tx attribute is locked, and the %s node is referenced - maya doesn't let you unlock attributes on referenced nodes!" % joints[n] )

				setAttr( '%s.tx' % joints[ n ], lock=False )

			#then connect the result of the plus node to the t(axis) pos of the limb joints
			connectAttr( '%s.outputX' % fractionNodes[ n ], '%s.tx' % joints[ n ], f=True )


		#now if we have only 3 joints, that means we have a simple limb structure
		#in which case, lets build an elbow pos network
		if len( joints ) == 3 and elbowPos:
			default = clientLengths[ 1 ] / totalLength * parityFactor
			isNeg = default < 0

			default = abs( default )
			addAttr( control, ln='elbowPos', at='double', min=0, max=1, dv=default )
			setAttr( '%s.elbowPos' % control, keyable=True )

			elbowPos = shadingNode( 'reverse', asUtility=True, n='%s_elbowPos' % joints[ 1 ] )
			if isNeg:
				mult = shadingNode( 'multiplyDivide', asUtility=True )
				setAttr( '%s.input2' % mult, -1, -1, -1 )
				connectAttr( '%s.elbowPos' % control, '%s.inputX' % elbowPos, f=True )
				connectAttr( '%s.elbowPos' % control, '%s.input1X' % mult, f=True )
				connectAttr( '%s.outputX' % elbowPos, '%s.input1Y' % mult, f=True )
				connectAttr( '%s.outputY' % mult, '%s.input2X' % fractionNodes[2], f=True )
				connectAttr( '%s.outputX' % mult, '%s.input2X' % fractionNodes[1], f=True )
			else:
				connectAttr( '%s.elbowPos' % control, '%s.inputX' % elbowPos, f=True )
				connectAttr( '%s.outputX' % elbowPos, '%s.input2X' % fractionNodes[2], f=True )
				connectAttr( '%s.elbowPos' % control, '%s.input2X' % fractionNodes[1], f=True )

		controls = ()
		namedNodes = autoLengthBlender, fkikBlender, lengthMods, lengthClamp

		return controls, namedNodes


#end
