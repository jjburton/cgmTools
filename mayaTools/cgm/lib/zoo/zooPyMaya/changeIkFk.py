
import re
import rigPrimitives

from maya.cmds import *

from baseMelUI import *
from mayaDecorators import d_disableViews, d_noAutoKey, d_unifyUndo, d_restoreTime
from melUtils import printWarningStr
from triggered import Trigger
from rigUtils import findPolePosition, alignFast

_FK_CMD_NAME = 'switch to FK'.lower()
_IK_CMD_NAME = 'switch to IK'.lower()


def cropValues( valueList, minVal=None, maxVal=None ):
	'''
	assumes the input list is sorted

	NOTE: the input list is modified in place and nothing is returned
	'''
	if minVal is not None:
		while valueList:
			if valueList[0] < minVal:
				valueList.pop( 0 )
			else: break

	if maxVal is not None:
		while valueList:
			if valueList[-1] > maxVal:
				valueList.pop()
			else: break


def getJointsFromIkHandle( handle ):

	#get the joints the ik control drives - we need these to get keyframes from so we know which frames to trace the ik control on
	joints = ikHandle( handle, q=True, jl=True )
	effector = ikHandle( handle, q=True, ee=True )
	cons = listConnections( '%s.tx' % effector, d=False )
	if not cons:
		printWarningStr( "Could not find the end effector control!" )
		return

	joints.append( cons[0] )

	return joints


def getControlsFromObjs( control ):
	'''
	attempts to retrieve the pole vector control, the ik handle and all fk controls given an ik rig control.  The
	information is returned in a 3 tuple containing:

	ikHandle, poleControl, fkControls
	'''
	errorValue = None, None, None, None

	try:
		part = rigPrimitives.RigPart.InitFromItem( control )

		return part.getControl( 'control' ), part.getIkHandle(), part.getControl( 'poleControl' ), part.getFkControls()
	except rigPrimitives.RigPartError: pass

	#so if the control we've been given isn't a rig primitive, lets try to extract whatever information we can from right click commands - if any exist
	trigger = Trigger( ikControl )
	switchCmdStr = None
	for n, cmdName, cmdStr in trigger.iterMenus():
		if cmdName.lower() == _IK_CMD_NAME:
			switchCmdStr = trigger.resolve( cmdStr )
			break

	if switchCmdStr is None:
		printWarningStr( "Cannot find the %s command - aborting!" % _IK_CMD_NAME )
		return errorValue

	#extract the control handle from the switch command - it may or may not exist, depending on which
	rexStr = re.compile( '-ikHandle \%([a-ZA-Z0-9_:|]+)', re.IGNORECASE | re.MULTILINE )
	match = rexStr.search( switchCmdStr )
	if not match:
		if match.groups()[0]:
			control = match.groups()[0]

	#extract the ik handle from the switch command
	rexStr = re.compile( '-ikHandle \%([a-ZA-Z0-9_:|]+)', re.IGNORECASE | re.MULTILINE )
	match = rexStr.search( switchCmdStr )
	if not match:
		printWarningStr( "Could not determine the ik handle from the given control" )
		return errorValue

	handle = match.groups()[0]
	if handle is None:
		printWarningStr( "Could not find the ik handle at the given connect index!" )
		return errorValue

	#now extract the pole control from the switch command
	rexStr = re.compile( '-pole \%([a-ZA-Z0-9_:|]+)', re.IGNORECASE | re.MULTILINE )
	match = rexStr.search( switchCmdStr )
	if not match:
		printWarningStr( "Could not determine the pole vector control from the given control" )
		return errorValue

	poleControl = match.groups()[0]
	if poleControl is None:
		printWarningStr( "Could not find the ik handle at the given connect index!" )
		return errorValue

	return control, poleControl, handle, getJointsFromIkHandle( handle )


@d_unifyUndo
@d_disableViews
@d_noAutoKey
@d_restoreTime
def switchAnimationToFk( control, handle=None, attrName='ikBlend', onValue=1, offValue=0, key=True, startFrame=None, endFrame=None ):

	#grab the key times for keys set on the t or r channels on the ik control - these are the frames we want to switch to fk on
	keyTimes = keyframe( control, q=True, at=('t', 'r'), tc=True )
	if not keyTimes:
		switchToFk( control, handle, attrName, offValue, key )
		printWarningStr( "No keys found on the ik control - nothing to do!" )
		return

	#remove duplicate key times and sort them
	keyTimes = removeDupes( keyTimes )
	keyTimes.sort()
	cropValues( keyTimes, startFrame, endFrame )

	joints = getJointsFromIkHandle( handle )
	for time in keyTimes:
		currentTime( time, e=True )
		switchToFk( control, handle, attrName, onValue, offValue, key, joints )

	select( joints[-1] )


@d_unifyUndo
@d_disableViews
@d_noAutoKey
@d_restoreTime
def switchAnimationToIk( control, poleControl=None, handle=None, attrName='ikBlend', onValue=1, key=True, startFrame=None, endFrame=None ):

	#get the joints the ik control drives - we need these to get keyframes from so we know which frames to trace the ik control on
	joints = getJointsFromIkHandle( handle )
	if not joints:
		printWarningStr( "Cannot find the fk controls for the given ik control" )
		return

	#grab the key times for keys set on the t or r channels on the ik control - these are the frames we want to switch to fk on
	keyTimes = keyframe( joints, q=True, at=('t', 'r'), tc=True )
	if not keyTimes:
		switchToIk( ikControl, poleControl, handle, attrName, onValue, key )
		printWarningStr( "No keys found on the fk controls - nothing to do!" )
		return

	#remove duplicate key times and sort them
	keyTimes = removeDupes( keyTimes )
	keyTimes.sort()
	cropValues( keyTimes, startFrame, endFrame )

	#clear out the keys for the ik control
	cutKey( control, poleControl, t=(keyTimes[0], keyTimes[-1]), cl=True )

	startFrame = keyTimes[0]
	currentTime( startFrame, e=True )
	setKeyframe( control, poleControl, t=(startFrame,) )

	for time in keyTimes:
		currentTime( time, e=True )
		switchToIk( control, poleControl, handle, attrName, onValue, key, joints, _isBatchMode=True )

	setKeyframe( control, t=keyTimes, at=attrName, v=onValue )

	select( control )


def switchToFk( control, handle=None, attrName='ikBlend', onValue=1, offValue=0, key=False, joints=None ):
	if handle is None:
		handle = control

	if handle is None or not objExists( handle ):
		printWarningStr( "no ikHandle specified" )
		return

	#if we weren't passed in joints - discover them now
	if joints is None:
		joints = getJointsFromIkHandle( handle )

	#make sure ik is on before querying rotations
	setAttr( '%s.%s' % (control, attrName), onValue )
	rots = []
	for j in joints:
		rot = getAttr( "%s.r" % j )[0]
		rots.append( rot )

	#now turn ik off and set rotations for the joints
	setAttr( '%s.%s' % (control, attrName), offValue )
	for j, rot in zip( joints, rots ):
		for ax, r in zip( ('x', 'y', 'z'), rot ):
			if getAttr( '%s.r%s' % (j, ax), se=True ):
				setAttr( '%s.r%s' % (j, ax), r )

	alignFast( joints[2], handle )
	if key:
		setKeyframe( joints )
		setKeyframe( '%s.%s' % (control, attrName) )


def switchToIk( control, poleControl=None, handle=None, attrName='ikBlend', onValue=1, key=False, joints=None, _isBatchMode=False ):
	if handle is None:
		handle = control

	if handle is None or not objExists( handle ):
		printWarningStr( "no ikHandle specified" )
		return

	#if we weren't passed in joints - discover them now
	if joints is None:
		joints = getJointsFromIkHandle( handle )

	alignFast( control, joints[2] )
	if poleControl:
		if objExists( poleControl ):
			pos = findPolePosition( joints[2], joints[1], joints[0] )
			move( pos[0], pos[1], pos[2], poleControl, a=True, ws=True, rpr=True )
			setKeyframe( poleControl )

	setAttr( '%s.%s' % (control, attrName), onValue )
	if key:
		setKeyframe( control, at=('t', 'r') )
		if not _isBatchMode:
			setKeyframe( control, at=attrName )


class ChangeIkFkLayout(MelColumnLayout):
	def __init__( self, parent ):
		self.UI_control = MelObjectSelector( self, 'control ->', None, 100 )
		self.UI_pole = MelObjectSelector( self, 'pole control ->', None, 100 )
		self.UI_handle = MelObjectSelector( self, 'IK handle ->', None, 100 )

		self.UI_control.setChangeCB( self.on_controlChanged )

		hLayout = MelHLayout( self )
		self.UI_toFk = MelButton( hLayout, l='Switch to FK', c=self.on_toFk )
		self.UI_toIk = MelButton( hLayout, l='Switch to IK', c=self.on_toIk )
		hLayout.layout()

		self.on_controlChanged()
	def setControl( self, control ):
		self.UI_control.setValue( control )

	### EVENT HANDLERS ###
	def on_controlChanged( self ):
		control = self.UI_control.getValue()
		if control:
			self.UI_toFk.setEnabled( True )
			self.UI_toIk.setEnabled( True )
			control, handle, poleControl, _tmp = getControlsFromObjs( control )
			self.UI_control.setValue( control, False )
			if handle:
				self.UI_handle.setValue( handle, False )

			if poleControl:
				self.UI_pole.setValue( poleControl, False )
		else:
			self.UI_toFk.setEnabled( False )
			self.UI_toIk.setEnabled( False )

	### EVENT HANDLERS ###
	def on_sceneChange( self, a ):
		self.UI_control.clear()
		self.UI_pole.clear()
		self.UI_handle.clear()
	def on_toFk( self, *a ):
		control = self.UI_control.getValue()
		if control:
			switchAnimationToFk( control, self.UI_handle.getValue() )
	def on_toIk( self, *a ):
		control = self.UI_control.getValue()
		if control:
			switchAnimationToIk( control, self.UI_pole.getValue(), self.UI_handle.getValue() )


class ChangeIkFkWindow(BaseMelWindow):
	WINDOW_NAME = 'changeIkFkWindow'
	WINDOW_TITLE = 'Ik Fk Switcher'

	DEFAULT_SIZE = 400, 150
	DEFAULT_MENU = None

	FORCE_DEFAULT_SIZE = True

	def __init__( self ):
		self.UI_editor = ChangeIkFkLayout( self )
		self.show()
	def setControl( self, control ):
		self.UI_editor.setControl( control )


def loadSelectedInTool():
	sel = ls( sl=True, type='transform' )
	if sel:
		if not ChangeIkFkWindow.Exists():
			ChangeIkFkWindow()

		for layout in ChangeIkFkLayout.IterInstances():
			layout.setControl( sel[0] )


#end
