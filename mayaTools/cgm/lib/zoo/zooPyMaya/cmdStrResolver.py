
import re
import maya


def resolve( cmdStr, obj, connects, optionals=() ):
	'''
	NOTE: both triggered and xferAnim use this function to resolve command strings as well
	'''
	INVALID = '<invalid connect>'
	cmdStr = str( cmdStr )

	#resolve # tokens - these represent self
	cmdStr = cmdStr.replace( '#', str( obj ) )

	#resolve ranged connect array tokens:  @<start>,<end> - these represent what is essentially a list slice - although they're end value inclusive unlike python slices...
	compile = re.compile
	arrayRE = compile( '(@)([0-9]+),(-*[0-9]+)' )
	def arraySubRep( matchobj ):
		char,start,end = matchobj.groups()
		start = int( start )
		end = int( end ) + 1
		if end == 0:
			end = None

		try:
			return '{ "%s" }' % '","'.join( connects[ start:end ] )
		except IndexError:
			return "<invalid range: %s,%s>" % (start, end)

	cmdStr = arrayRE.sub( arraySubRep, cmdStr )

	#resolve all connect array tokens:  @ - these are represent a mel array for the entire connects array excluding self
	allConnectsArray = '{ "%s" }' % '","'.join( [con for con in connects[1:] if con != INVALID] )
	cmdStr = cmdStr.replace( '@', allConnectsArray )

	#resolve all single connect tokens:  %<x> - these represent single connects
	connectRE = compile('(%)(-*[0-9]+)')
	def connectRep( matchobj ):
		char, idx = matchobj.groups()
		try:
			return connects[ int(idx) ]
		except IndexError:
			return INVALID

	cmdStr = connectRE.sub( connectRep, cmdStr )

	#finally resolve any optional arg list tokens:  %opt<x>%
	optionalRE = compile( '(\%opt)(-*[0-9]+)(\%)' )
	def optionalRep( matchobj ):
		charA, idx, charB = matchobj.groups()
		try:
			return optionals[ int(idx) ]
		except IndexError:
			return '<invalid optional>'

	cmdStr = optionalRE.sub( optionalRep, cmdStr )

	return cmdStr


def resolveAndExecute( cmdStr, obj, connects, optionals=() ):
	return maya.mel.eval( resolve( cmdStr, obj, connects, optionals ) )


#end
