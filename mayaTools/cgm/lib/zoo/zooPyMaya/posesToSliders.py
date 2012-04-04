
from maya.cmds import *

from zooPy.misc import removeDupes

import melUtils
import triggered


def create( trigger,
            control=None,
            linear=True,
            optimize=True,
            preserve=False,
            defaultValue=0,
            maxValue=10 ):
	'''
	converts poses stored as triggered menu commands on trigger to set driven keys on the given control.  If control is
	None then the trigger itself is used.
	'''
	if not isinstance( trigger, triggered.Trigger ):
		trigger = triggered.Trigger( trigger )

	if control is None:
		control = trigger

	cmdData = trigger.menus()

	#gather data about the cmds first
	menuIdxs = []
	menuNames = {}
	connectsUsedByCmds = {}
	cmdStrs = {}
	resolvedCmdStrs = {}
	sliderNames = {}
	sliderBreakdownValues = {}
	for menuIdx, menuName, cmdStr in cmdData:
		menuIdxs.append( menuIdx )
		menuNames[menuIdx] = menuName
		cmdStrs[menuIdx] = cmdStr
		connectsUsedByCmds[menuIdx] = [ trigger[connectIdx] for connectIdx in trigger.getConnectsUsedByCmd( cmdStr ) ]
		resolvedCmdStrs[menuIdx] = trigger.resolve( cmdStr )

		#determine the slider name from the menu name
		sliderName = menuNames[menuIdx]
		while sliderName.startswith( '_' ):
			sliderName = sliderName[1:]

		underscoreIdx = sliderName.rfind( '_' )
		if underscoreIdx != -1:
			try: sliderBreakdownValues[menuIdx] = float( sliderName[underscoreIdx+1:] )
			except ValueError: pass
			sliderName = sliderName[:underscoreIdx]
		else:
			sliderBreakdownValues[menuIdx] = maxValue

		sliderNames[menuIdx] = sliderName

	def setToDefaultPose(): melUtils.mel.eval( resolvedCmdStrs[ menuIdxs[0] ] )
	setToDefaultPose()

	#get a list of all target objects, so we know what objects to build SDK curves for
	allUsedConnectIdxs = []
	for connectsUsed in connectsUsedByCmds.values():
		allUsedConnectIdxs += connectsUsed

	allUsedConnects = removeDupes( allUsedConnectIdxs )

	#the user may want to preserve existing sdk data on the target objects...
	if not preserve:
		for connect in allUsedConnects:
			deleteSliders( connect )

	#delete any existing sliders
	for menuIdx in menuIdxs:
		sliderName = sliderNames[menuIdx]
		attrpath = '%s.%s' % (control, sliderName)
		if objExists( attrpath ):
			deleteAttr( attrpath )

	#now build the sliders
	for menuIdx in menuIdxs:
		sliderName = sliderNames[menuIdx]
		breakdownVal = sliderBreakdownValues[menuIdx]

		#create the attribute if it doesn't already exist
		attrpath = '%s.%s' % (control, sliderName)
		if not objExists( attrpath ):
			addAttr( control, ln=sliderName, at='double', min=0, max=0, dv=0 )
			setAttr( attrpath, k=True )

		#now that the attribute is created, see what its limits are, and whether the current limit values should push
		#those limits further
		curMin = addAttr( attrpath, q=True, min=True )
		curMax = addAttr( attrpath, q=True, max=True )

		if breakdownVal < curMin:
			addAttr( attrpath, e=True, min=breakdownVal )
		elif breakdownVal > curMax:
			addAttr( attrpath, e=True, max=breakdownVal )

	#now build the SDKs, we know the attributes exist, so we don't need to worry about them
	sliders = []
	sliderKeyCounts = []
	for menuIdx in menuIdxs[1:]:
		attrpath = '%s.%s' % (control, sliderNames[menuIdx])
		breakdownVal = sliderBreakdownValues[menuIdx]

		#return to default pose
		setAttr( attrpath, defaultValue )
		setToDefaultPose()
		for connect in connectsUsedByCmds[menuIdx]:
			setDrivenKeyframe( connect, cd=attrpath )

		#go into the pose and set its SDK key
		setAttr( attrpath, breakdownVal )
		melUtils.mel.eval( resolvedCmdStrs[menuIdx] )
		for connect in connectsUsedByCmds[menuIdx]:
			setDrivenKeyframe( connect, cd=attrpath )

		setAttr( attrpath, defaultValue )

	for connect in allUsedConnectIdxs:
		setCurveInfinityToLinear( connect )
		if optimize:
			deleteStaticChannels( connect )

		if linear:
			setTangentsTo( connect, 'linear' )


def getSDKCurve( obj, objAttr, driver, driverAttr ):
	'''
	returns the name of the animCurve for an attribute driven by an SDK if one exists, otherwise None
	'''
	driverAttrpath = '%s.%s' % (driver, driverAttr)
	attrs = listAttr( obj, k=True, v=True, s=True, m=True )
	for attr in attrs:
		animCurves = getSDKCurves( obj, objAttr )
		for c in animCurves:
			if isConnected( driverAttrpath, '%s.input' % c ):
				return c


def getSDKCurves( obj, attr ):
	'''
	returns all the SDK animCurves for an attribute on an object
	'''
	attrpath = '%s.%s' % (obj, attr)
	sdks = []

	if objExists( attrpath ):
		return sdks

	cons = listConnections( attrpath, d=False, scn=True ) or []
	blends = []

	for c in cons:
		if objType( c, isAType='animCurve' ):

			#so we know its controlled by an animcurve, but is the animcurve driven by something?
			isAnimCurveDriven = listConnections( '%s.input' % c, d=False, scn=True )
			if isAnimCurveDriven:
				sdks.append( c )
		elif objType( c, isAType='blendWeighted' ):
			blends.append( c )

	for b in blends:
		sdks += listConnections( b, d=False, scn=True, type='animCurve' )

	return sdks


def getSDKCurvesDrivenByObj( obj ):
	curves = []
	attrs = listAttr( obj, k=True, v=True, s=True, m=True ) or []
	for attr in attrs:
		curves += getSDKCurves( obj, attr )

	return removeDupes( curves )


def setTangentsTo( obj, typeStr ):
	'''
	changes the tangents to spline
	'''
	attrs = listAttr( obj, k=True, v=True, s=True, m=True )
	for attr in attrs:
		animCurves = getSDKCurves( obj, attr )
		for c in animCurves:
			if keyframe( q=True, sl=True ):
				selectKey( clear=True )

			keyTangent( c, f=':', itt=typeStr, ott=typeStr )


def setCurveInfinityToLinear( obj ):
	'''
	changes the infinity states of all SDK curves to linear for a given object
	'''
	attrs = listAttr( obj, k=True, v=True, s=True, m=True )
	for attr in attrs:
		animCurves = getSDKCurves( obj, attr )
		for c in animCurves:
			if keyframe( q=True, sl=True ):
				selectKey( clear=True )

			keyTangent( c, f=':', itt='spline', ott='spline' )
			selectKey( c, index=0 )
			setInfinity( pri='linear', poi='linear' )


def deleteSliders( obj ):
	'''
	deletes all SDK information for a given object
	'''
	attrs = listAttr( obj, k=True, v=True, s=True, m=True )
	for attr in attrs:
		animCurves = getSDKCurves( obj, attr )
		blends = listConnections( '%s.%s' % (obj, attr), d=False, type='blendWeighted', scn=True ) or []
		if animCurves + blends:
			for a in animCurves:
				if objExists( a ):
					delete( a )


def deleteStaticChannels( obj ):
	'''
	deletes all static SDK channels
	'''
	staticCurves = findStaticChannels( obj )

	for curve in staticCurves:
		curveValue = keyframe( curve, index=0, q=True, vc=True )[0]
		connectedTo = listConnections( '%s.output' % curve, scn=True, s=False, p=True )[0]
		delete( curve )
		if objExists( connectedTo ):
			setAttr( connectedTo, curveValue )


def findStaticChannels( obj ):
	'''
	returns a list of static channels - if no object is specified, a list of all static channels in the scene is
	returned, otherwise only channels for a given object are returned
	'''
	curves = getSDKCurvesDrivenByObj( obj )
	static = []

	def getKeyValue( keyIdx ): return keyframe( curve, index=keyIdx, q=True, vc=True )[0]
	for curve in curves:
		firstValue = getKeyValue( 0 )
		numKeys = keyframe( curve, q=True, kc=True )
		isStatic = True

		for keyIdx in range( 1, numKeys ):
			if getKeyValue( keyIdx ) == firstValue:
				isStatic = False
				break

		if isStatic:
			static.append( curve )

	return static


#end
