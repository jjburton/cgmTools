'''
provides console colouring - currently only NT is supported
'''

STD_OUTPUT_HANDLE = -11

FG_BLUE = 0x01
FG_GREEN = 0x02
FG_CYAN = 0x03
FG_RED = 0x04
FG_MAGENTA = 0x05
FG_YELLOW = 0x06
FG_WHITE = 0x07
BRIGHT = 0x08

BG_BLUE = 0x10
BG_GREEN = 0x20
BG_CYAN = 0x30
BG_RED = 0x40
BG_MAGENTA = 0x50
BG_YELLOW = 0x60
BG_BRIGHT = 0x80

import sys

try:
	import ctypes
	def setConsoleColour( colour ):
		'''
		sets the subsequent console spew to a given colour

		eg. setConsoleColour(BRIGHT | FG_GREEN)
		'''
		std_out_handle = ctypes.windll.kernel32.GetStdHandle( STD_OUTPUT_HANDLE )
		ctypes.windll.kernel32.SetConsoleTextAttribute( std_out_handle, colour )
except:
	def setConsoleColour( colour ):
		pass


class ColouredWriter:
	def __init__( self, colour ):
		self.colour = colour
	def write( self, msg ):
		setConsoleColour( self.colour )
		sys.stdout.write( msg )
		setConsoleColour( FG_WHITE )


def logInColour( msg, colour ):
	print >> ColouredWriter( colour ), msg


'''
create some useful, common colouredWriter instances.  an example for using these:
print >> Error, 'hello, im an error'
'''
Warn = ColouredWriter( BRIGHT | FG_YELLOW )
Error = ColouredWriter( BRIGHT | FG_RED )
Good = ColouredWriter( BRIGHT | FG_GREEN )
BigError = ColouredWriter( BRIGHT | FG_RED | BG_RED )


def logAsWarning( msg ):
	print >> Warn, msg


def logAsError( msg ):
	print >> Error, msg


#end
