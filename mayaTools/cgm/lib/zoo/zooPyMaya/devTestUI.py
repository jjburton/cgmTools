
from zooPy.misc import removeDupes
from zooPy.devTest import TEST_CASES, runTestCases

from baseMelUI import *


class DevTestLayout(MelVSingleStretchLayout):
	def __init__( self, parent, *a, **kw ):
		MelVSingleStretchLayout.__init__( self, parent, *a, **kw )

		self.UI_tests = UI_tests = MelObjectScrollList( self, ams=True )
		self.UI_run = UI_run = MelButton( self, l='Run Tests', c=self.on_test )

		for testCls in TEST_CASES:
			UI_tests.append( testCls )

		self.setStretchWidget( UI_tests )
		self.layout()

	### EVENT HANDLERS ###
	def on_test( self, *a ):
		'''
		run the selected tests - the modules are reloaded before running the tests so
		its easy to iterate when writing the tests
		'''
		runTestCases( self.UI_tests.getSelectedItems() )


class DevTestWindow(BaseMelWindow):
	WINDOW_NAME = 'devTestWindow'
	WINDOW_TITLE = 'Maya Devtest Runner'

	DEFAULT_MENU = None
	DEFAULT_SIZE = 300, 300
	FORCE_DEFAULT_SIZE = True

	def __init__( self ):
		BaseMelWindow.__init__( self )

		DevTestLayout( self )
		self.show()


#end
