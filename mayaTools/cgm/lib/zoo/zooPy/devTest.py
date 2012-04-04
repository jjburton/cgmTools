
try:
	import wingdbstub
except ImportError: pass

import sys
import inspect

from unittest import TestCase, TestResult

from maya import cmds as cmd

from path import Path
import moduleUtils


### POPULATE THE LIST OF TEST SCRIPTS ###
TEST_SCRIPTS = {}

def _populateTestScripts():
	global TEST_SCRIPTS

	thisScriptDir = Path( __file__ ).up()
	mayaScriptDir = thisScriptDir.up() / 'zooPyMaya'
	pathsToSearch = set( map( Path, sys.path + [ thisScriptDir, mayaScriptDir ] ) )
	for pyPath in pathsToSearch:
		if pyPath.isDir():
			for f in pyPath.files():
				if f.hasExtension( 'py' ):
					if f.name().startswith( 'devTest_' ):
						TEST_SCRIPTS[ f ] = []

_populateTestScripts()


### POPULATE TEST_CASES ###
TEST_CASES = []

def _populateTestCases():
	global TEST_CASES

	for scriptFilepath in TEST_SCRIPTS:
		moduleName = moduleUtils.getFirstModuleNameFromFilepath( scriptFilepath )
		testModule = __import__( moduleName, globals() )

		scriptTestCases = TEST_SCRIPTS[ scriptFilepath ] = []
		for name, obj in testModule.__dict__.iteritems():
			if obj is TestCase:
				continue

			if isinstance( obj, type ):
				if issubclass( obj, TestCase ):
					if obj.__name__.startswith( '_' ):
						continue

					TEST_CASES.append( obj )
					scriptTestCases.append( obj )

_populateTestCases()


def runTestCases( testCases=TEST_CASES ):
	thisPath = Path( __file__ ).up()
	testResults = TestResult()

	for ATestCase in testCases:
		testCase = ATestCase()
		testCase.run( testResults )

	#force a new scene
	cmd.file( new=True, f=True )

	OK = 'Ok'
	BUTTONS = (OK,)
	if testResults.errors:
		print '------------- THE FOLLOWING ERRORS OCCURRED -------------'
		for error in testResults.errors:
			print error[0]
			print error[1]
			print '--------------------------'

		cmd.confirmDialog( t='TEST ERRORS OCCURRED!', m='Errors occurred running the tests - see the script editor for details!', b=BUTTONS, db=OK )
	else:
		print '------------- %d TESTS WERE RUN SUCCESSFULLY -------------' % len( testCases )
		cmd.confirmDialog( t='SUCCESS!', m='All tests were successful!', b=BUTTONS, db=OK )

	return testResults


#end
