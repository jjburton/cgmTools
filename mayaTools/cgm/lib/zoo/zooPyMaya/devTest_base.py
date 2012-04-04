
import unittest

from maya import standalone

try:
	standalone.initialize()
except: pass

from maya import cmds as cmd

from zooPy.path import Path

TEST_DIRECTORY = Path( __file__ ).up() / '_devTest_testScenes_'  #location for maya files written by tests


def d_makeNewScene( sceneName ):
	'''
	simple decorator macro - will create a new scene and save it so that it exists on disk
	before the function is run, and gets saved once the function exits - saves having to
	re-write the 4 lines of code it takes to do this on every test method...
	'''
	def decorate(f):
		def newF( self, *a, **kw ):
			cmd.file( new=True, f=True )
			filename = (TEST_DIRECTORY / 'maya' / sceneName).setExtension( 'ma' )
			cmd.file( rename=filename )
			cmd.file( save=True )

			ret = f( self, *a, **kw )

			cmd.file( save=True )

			return ret

		return newF

	return decorate


class BaseTest(unittest.TestCase):
	'''
	base class for maya tests - doesn't really do anything except provide a cleanup routine that will delete
	all files saved to the TEST_DIRECTORY after the testCase has been run
	'''
	_CLEANUP = True

	def setUp( self ):
		mayaDir = TEST_DIRECTORY / 'maya'
		mayaDir.create()
	def new( self ):
		cmd.file( new=True, f=True )
	def tearDown( self ):
		'''
		cleans out all files under the TEST_DIRECTORY folder after the tests have run
		'''
		cmd.file( new=True, f=True )

		#if the user doesn't want us to cleanup, don't!
		if not self._CLEANUP:
			return

		print '--- CLEANING UP TEST FILES ---'
		for f in TEST_DIRECTORY.files( recursive=True ):

			#delete the file
			f.delete()


#end
