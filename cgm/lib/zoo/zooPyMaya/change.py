
from baseMelUI import *

from changeIkFk import ChangeIkFkLayout
from changeParent import ChangeParentLayout
from changeRo import ChangeRoLayout


class ChangeLayout(MelColumnLayout):
	def __init__( self, parent ):
		frame = MelFrameLayout( self, l='Change Ik/Fk', cll=True, cl=False )
		ChangeIkFkLayout( frame )

		frame = MelFrameLayout( self, l='Change Parent', cll=True, cl=True )
		ChangeParentLayout( frame )

		frame = MelFrameLayout( self, l='Change Rotation Order', cll=True, cl=True )
		ChangeRoLayout( frame )


class ChangeWindow(BaseMelWindow):
	WINDOW_NAME = 'changeTool'
	WINDOW_TITLE = 'Change Tools'

	DEFAULT_SIZE = 300, 250
	DEFAULT_MENU = 'Help'
	FORCE_DEFAULT_SIZE = True

	def __init__( self ):
		ChangeLayout( self )
		self.show()


#end
