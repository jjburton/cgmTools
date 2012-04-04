
from unittest import TestCase
from name import Name, CamelCaseName

class TestNames(TestCase):
	def runTest( self ):
		names = [ ('a_simple_case', '_', ['a', 'simple', 'case']),
		          ('a__slightly_more_complicated_case', '_', ['a', '', 'slightly', 'more', 'complicated', 'case']),
		          ('_a_', '_', ['', 'a', '']),
		          ]

		for name, delim, expectedTokens in names:
			asName = Name( name, delim )
			assert asName.split() == expectedTokens
			assert asName.up() == delim.join( expectedTokens[:-1] )
			assert asName.up(2) == delim.join( expectedTokens[:-2] )
			for n, tok in enumerate( expectedTokens ):
				assert asName[n] == tok

		camelNames = [ ('thisIsCamel', '_', ['this', 'Is', 'Camel']),
		              ('ThisHasLOTSOFCaps', '_', ['This', 'Has', 'LOTSOFCaps']),
		              ('SomeNumbers123In_thisOne456', '_', ['Some', 'Numbers', '123', 'In', 'this', 'One', '456']),
		              ]

		for name, delim, expectedTokens in camelNames:
			asName = CamelCaseName( name )
			assert len( asName ) == len( expectedTokens )
			assert asName.split() == expectedTokens
			assert asName.up() == ''.join( expectedTokens[:-1] )
			assert asName.up(2) == ''.join( expectedTokens[:-2] )
			for n, tok in enumerate( expectedTokens ):
				assert asName[n] == tok


#end
