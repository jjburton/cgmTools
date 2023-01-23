
from maya.cmds import *

from baseMelUI import *
from mayaDecorators import d_disableViews, d_noAutoKey, d_unifyUndo
from melUtils import printWarningStr


@d_unifyUndo
@d_disableViews
@d_noAutoKey
def changeParent( parent=0, objs=None ):
	if objs is None:
		objs = ls( sl=True, type='transform' ) or []

	#only bother with objects that have a "parent" attribute and whose parent attribute value is not the same as the one we've been passed
	objsToActOn = []
	for obj in objs:
		if objExists( '%s.parent' % obj ):
			objsToActOn.append( obj )

	objs = objsToActOn

	#if there are no objects, bail
	if not objs:
		printWarningStr( "There are no objects to work on - aborting!" )
		return

	#store the initial time so we can restore it at the end
	initialTime = currentTime( q=True )

	#first we need to make sure that any frame with a rotation key needs to have a key on ALL rotation axes - so make this happen
	keyTimes = keyframe( objs, q=True, at=('t', 'r'), tc=True )
	if not keyTimes:
		printWarningStr( "No keys found on the objects - nothing to do!" )
		return

	#remove duplicate key times and sort them
	keyTimes = removeDupes( keyTimes )
	keyTimes.sort()

	#store the objects that each have keys at each key time in a dict so we don't have to query maya again. maya queries are slower than accessing python data structures
	timeObjs = {}
	for time in keyTimes:
		currentTime( time, e=True )
		timeObjs[ time ] = objsWithKeysAtThisTime = []
		for obj in objs:
			keyOnCurrentTime = keyframe( obj, q=True, t=(time,), at=('parent', 't', 'r'), kc=True )
			if keyOnCurrentTime:
				setKeyframe( obj, at=('parent', 't', 'r') )
				objsWithKeysAtThisTime.append( obj )

	#now that we've secured the translation/rotation poses with keys on all axes, change the parent on each keyframe
	for time, objsWithKeysAtThisTime in timeObjs.iteritems():
		currentTime( time, e=True )
		for obj in objsWithKeysAtThisTime:
			pos = xform( obj, q=True, rp=True, ws=True )
			rot = xform( obj, q=True, ro=True, ws=True )

			#change the parent and move/rotate back to the original world space pose
			setAttr( '%s.parent' % obj, parent )

			move( pos[0], pos[1], pos[2], obj, ws=True, rpr=True )
			rotate( rot[0], rot[1], rot[2], obj, ws=True )

			#lock in the pose
			setKeyframe( obj, at=('parent', 't', 'r') )

	#finally restore the initial time
	currentTime( initialTime, e=True )


class ChangeParentLayout(MelColumnLayout):
	def __init__( self, parent ):
		hLayout = MelHSingleStretchLayout( self )

		lbl = MelLabel( hLayout, l='New Parent' )
		self.UI_parent = MelOptionMenu( hLayout )

		hLayout.setStretchWidget( self.UI_parent )
		hLayout.layout()
		hLayout( e=True, af=((lbl, 'top', 0), (lbl, 'bottom', 0)) )

		self.UI_go = MelButton( self, l='Change Parent', c=self.on_go )

		self.on_selectionChange()
		self.setSelectionChangeCB( self.on_selectionChange )

	### EVENT HANDLERS ###
	def on_selectionChange( self, *a ):
		self.UI_parent.clear()

		#populate the parent list - just use the parents from the first object found with a parent attribute
		for obj in ls( sl=True, type='transform' ) or []:
			if objExists( '%s.parent' % obj ):
				curValue = getAttr( '%s.parent' % obj )

				enumStr = addAttr( '%s.parent' % obj, q=True, enumName=True )
				enums = enumStr.split( ':' )
				for enum in enums:
					self.UI_parent.append( enum )

				if enums:
					self.UI_parent.selectByIdx( curValue )
					self.UI_go.enable( True )

				return

		#if we've made it here, there are no objects with a parent attribute, or no objects with parents - either way disable the go button
		self.UI_go.enable( False )
	def on_go( self, *a ):
		changeParent( self.UI_parent.getSelectedIdx() )


class ChangeParentWindow(BaseMelWindow):
	WINDOW_NAME = 'changeParent'
	WINDOW_TITLE = 'Change Parent Tool'

	DEFAULT_MENU = None
	DEFAULT_SIZE = 245, 85
	FORCE_DEFAULT_SIZE = True

	def __init__( self ):
		self.UI_editor = ChangeParentLayout( self )
		self.show()


#end
