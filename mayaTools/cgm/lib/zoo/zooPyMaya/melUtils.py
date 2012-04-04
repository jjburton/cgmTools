
import maya.mel
from maya import cmds as cmd
from maya.OpenMaya import MGlobal

from zooPy.exceptionHandlers import generateTraceableStrFactory
from zooPy.path import Path

melEval = maya.mel.eval

generateInfoStr, printInfoStr = generateTraceableStrFactory( '*** INFO ***', MGlobal.displayInfo )
generateWarningStr, printWarningStr = generateTraceableStrFactory( '', MGlobal.displayWarning )
generateErrorStr, printErrorStr = generateTraceableStrFactory( '', MGlobal.displayError )

mayaVar = float( melEval( 'getApplicationVersionAsFloat()' ) )


def pyArgToMelArg( arg ):
	#given a python arg, this method will attempt to convert it to a mel arg string
	if isinstance( arg, basestring ):
		return u'"%s"' % cmd.encodeString( arg )

	#if the object is iterable then turn it into a mel array string
	elif hasattr( arg, '__iter__' ):
		return '{%s}' % ','.join( map( pyArgToMelArg, arg ) )

	#either lower case bools or ints for mel please...
	elif isinstance( arg, bool ):
		return str( arg ).lower()

	#otherwise try converting the sucka to a string directly
	return unicode( arg )


class Mel( object ):
	'''
	creates an easy to use interface to mel code as opposed to having string formatting
	operations all over the place in scripts that call mel functionality
	'''
	def __init__( self, echo=False ):
		self.echo = echo
	def __getattr__( self, attr ):
		if attr.startswith( '__' ) and attr.endswith( '__' ):
			return self.__dict__[attr]

		#construct the mel cmd execution method
		echo = self.echo
		def melExecutor( *args ):
			strArgs = map( pyArgToMelArg, args )
			cmdStr = '%s(%s);' % (attr, ','.join( strArgs ))

			if echo:
				print cmdStr

			try:
				retVal = melEval( cmdStr )
			except RuntimeError:
				print 'cmdStr: %s' % cmdStr
				return

			return retVal

		melExecutor.__name__ = attr

		return melExecutor
	def source( self, script ):
		return melEval( 'source "%s";' % script )
	def eval( self, cmdStr ):
		if self.echo:
			print cmdStr

		try:
			return melEval( cmdStr )
		except RuntimeError:
			print 'ERROR :: trying to execute the cmd:'
			print cmdStr
			raise

mel = Mel()
melecho = Mel(echo=True)


class CmdQueue(list):
	'''
	the cmdQueue is generally used as a bucket to store a list of maya commands to execute.  for whatever
	reason executing individual maya commands through python causes each command to get put into the undo
	queue - making tool writing a pain.  so for scripts that have to execute maya commands one at a time,
	consider putting them into a CmdQueue object and executing the object once you're done generating
	commands...  to execute a CmdQueue instance, simply call it
	'''
	def __init__( self ):
		list.__init__(self)
	def __call__( self, echo=False ):
		m = mel
		if echo:
			m = melecho

		fp = Path( "%TEMP%/cmdQueue.mel" )
		f = open( fp, 'w' )
		f.writelines( '%s;\n' % l for l in self )
		f.close()
		print fp

		m.source( fp )


def referenceFile( filepath, namespace, silent=False ):
	filepath = Path( filepath )
	cmd.file( filepath, r=True, prompt=silent, namespace=namespace )


def openFile( filepath, silent=False ):
	filepath = Path( filepath )
	ext = filepath.getExtension().lower()
	if ext == 'ma' or ext == 'mb':
		mel.saveChanges( 'file -f -prompt %d -o "%s"' % (silent, filepath) )
		mel.addRecentFile( filepath, 'mayaAscii' if Path( filepath ).hasExtension( 'ma' ) else 'mayaBinary' )


def importFile( filepath, silent=False ):
	filepath = Path( filepath )
	ext = filepath.getExtension().lower()
	if ext == 'ma' or ext == 'mb':
		cmd.file( filepath, i=True, prompt=silent, rpr='__', type='mayaAscii', pr=True, loadReferenceDepth='all' )


#end
