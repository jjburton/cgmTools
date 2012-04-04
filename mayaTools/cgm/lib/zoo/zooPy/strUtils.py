
import name


class Parity(int):
	PARITIES = NONE, LEFT, RIGHT = None, 0, 1
	TESTS = { LEFT: ["l", "left", "lft", "lf", "lik"],
	          RIGHT: ["r", "right", "rgt", "rt", "rik"] }

	#odd indices are left sided, even are right sided
	NAMES = [ '_L', '_R',
	          '_A_L', '_A_R',
	          '_B_L', '_B_R',
	          '_C_L', '_C_R',
	          '_D_L', '_D_R' ]

	def __new__( cls, idx ):
		return int.__new__( cls, idx )
	def __eq__( self, other ):
		if other is None:
			return False

		return self % 2 == int( other ) % 2
	def __nonzero__( self ):
		return self % 2
	def __ne__( self, other ):
		return not self.__eq__( other )
	def asMultiplier( self ):
		return (-1) ** self
	def asName( self ):
		return self.NAMES[ self ]
	def isOpposite( self, other ):
		return (self % 2) != (other % 2)

Parity.LEFT, Parity.RIGHT = Parity( Parity.LEFT ), Parity( Parity.RIGHT )


class ParityName(name.CamelCaseName):
	def hasParity( self ):
		'''
		returns a 2-tuple containing the Parity instance and the specific parity token found
		'''
		lowerToks = [ tok.lower() for tok in self.split() ]
		lowerToksSet = set( lowerToks )
		existingParityToksL = lowerToksSet.intersection( set( Parity.TESTS[Parity.LEFT] ) )

		if existingParityToksL:
			parityStr = existingParityToksL.pop()

			return Parity.LEFT, parityStr

		existingParityToksR = lowerToksSet.intersection( set( Parity.TESTS[Parity.RIGHT] ) )
		if existingParityToksR:
			parityStr = existingParityToksR.pop()

			return Parity.RIGHT, parityStr

		return Parity.NONE, None
	def getParity( self ):
		return self.hasParity()[0]
	def swapParity( self ):
		toks = self.split()
		lowerToks = [tok.lower() for tok in toks]
		lowerToksSet = set(lowerToks)

		allParityTests = Parity.TESTS[Parity.LEFT], Parity.TESTS[Parity.RIGHT]

		for parityTests, otherTests in zip( allParityTests, reversed( allParityTests ) ):
			parityTokensPresent = lowerToksSet.intersection( set(parityTests) )

			if parityTokensPresent:
				#this is the caseless parity token
				parityToken = parityTokensPresent.pop()

				idxInName = lowerToks.index( parityToken )
				idxInTokens = parityTests.index( parityToken )

				#this gets us the parity token with case - so we can make sure the swapped parity token has the same case...
				parityToken = nameToks[ idxInName ]

				name[ idxInName ] = matchCase( otherTests[ idxInTokens ], parityToken )

				return name

		return name
	def stripParity( self ):
		nameToks = name.split()
		lowerToks = [ tok.lower() for tok in nameToks ]
		lowerToksSet = set( lowerToks )

		for parityTests in (parityTestsL, parityTestsR):
			parityTokensPresent = lowerToksSet.intersection( set( parityTests ) )

			if parityTokensPresent:
				parityToken = parityTokensPresent.pop()
				idxInName = lowerToks.index( parityToken )
				name[ idxInName ] = ''

				return name

		return name


def matchNames( srcList, tgtList, strip=True, parity=True, unique=False, opposite=False, threshold=1, **kwargs ):
	'''
	given two lists of strings, this method will return a list (the same size as the first - source list)
	with the most appropriate matches found in the second (target) list.  the args are:

	strip: strips off any prefixes before doing the match - see the Name.__init__ method for details on prefixes

	parity: parity tokens are substrings which identify what side of a body a control might lie on.  see the
	    global defines at the start of this script for examples of parity tokens

	unique: performs unique matches - ie each tgt will only be matched at most to one src

	opposite: if parity is True, only items of the same parity will be matched.  if opposite is on, then items
	    with non-zero parity will be matched to items of the other non-zero parity - ie left is mapped to right

	threshold: determines the minimum likeness for two names to be matched.  the likeness factor is described in Name.likeness

	nomatch: teh object used when no match occurs - defaults to Name()
	'''
	if isinstance(srcList, basestring): srcList = [srcList]
	if isinstance(tgtList, basestring): tgtList = [tgtList]

	#build the Name objects for the strings
	srcNames = [ Name(name) for name in srcList ]
	tgtNames = [ Name(name) for name in tgtList ]
	numSrc, numTgt = len(srcList), len(tgtList)
	nomatch = kwargs.get('nomatch', Name())

	#cache prefixes so they don't affect name matching - caching them stores them on the name instance so we can retrieve them later
	if strip:
		for a in srcNames: a.cache_prefix()
		for a in tgtNames: a.cache_prefix()

	matches = []
	for name in srcNames:
		foundExactMatch = False
		likenessList = []
		for n, tgt in enumerate(tgtNames):
			likeness = name.likeness(tgt, parity)
			if likeness >= 1:
				#the pop is safe here coz we're bailing
				matches.append(tgt)
				if unique: tgtNames.pop(n)
				foundExactMatch = True
				break

			likenessList.append(likeness)

		#early out
		if foundExactMatch:
			continue

		#find the idx of the highest likeness
		bestIdx = -1
		for n, curLikeness in enumerate(likenessList):
			if curLikeness > likenessList[bestIdx]: bestIdx = n

		#for th,tn in zip(likenessList,tgtNames): print th,name.split(),tn.split()
		#print '%s   ->   %s'%(name,tgtNames[bestIdx])
		#print '--------------\n'
		if bestIdx >= 0 and likenessList[bestIdx] > threshold:
			#are we performing unique matching?  if so, remove the best target match from the target list
			if unique: matches.append(tgtNames.pop(bestIdx))
			else: matches.append(tgtNames[bestIdx])
		else: matches.append(nomatch)

	#re-apply any prefixes we stripped
	if strip: matches = [ a.item for a in matches ]

	return matches


ABBRVS_TO_EXPAND = {'max': 'maximum',
				  'min': 'minimum'}

def camelCaseToNice( theString, abbreviationsToExpand=None, niceParityNames=True ):
	asName = Name( theString )
	words = asName.split()

	if niceParityNames:
		#does the name have parity?  if so use the "nice" version of the parity string
		parity = asName.get_parity()

		if parity is not Parity.NONE:
			niceParityStr = (parityTestsL, parityTestsR)[ parity ][ 1 ]
			if abbreviationsToExpand is None: abbreviationsToExpand = {}
			abbreviationsToExpand[ asName._parityStr ] = niceParityStr

	if abbreviationsToExpand is None:
		words = [ w.capitalize() for w in words ]
	else:
		words = [ abbreviationsToExpand.get(w.lower(), w).capitalize() for w in words ]

	return ' '.join( words )

class Mapping(object):
	def __init__( self, srcList, tgtList ):
		self.srcs = srcList[:]
		self.tgts = tgtList[:]
	def __iter__( self ):
		return iter( self.srcs )
	def __len__( self ):
		return len( self.srcs )
	def __contains__( self, item ):
		return item in self.asDict()
	def __getitem__( self, item ):
		return self.asDict()[ item ]
	def __setitem__( self, item, value ):
		if isinstance( value, basestring ):
			value = [ value ]

		asDict = self.asDict()
		asDict[ item ] = value
		self.setFromDict( asDict, self.srcs )
	def iteritems( self ):
		return iter( zip( self.srcs, self.tgts ) )
	def iterkeys( self ):
		return self.asDict().iterkeys()
	def itervalues( self ):
		return self.asDict().itervalues()
	def keys( self ):
		return self.asDict().keys()
	def values( self ):
		return self.asDict().values()
	def swap( self ):
		'''
		swaps sources and targets - this is done in place
		'''
		self.srcs, self.tgts = self.tgts, self.srcs
		return self
	def copy( self ):
		'''
		returns a copy of the mapping object
		'''
		return self.__class__.FromMapping( self )
	def pop( self, index=-1 ):
		src = self.srcs.pop( index )
		tgt = self.tgts.pop( index )

		return src, tgt
	def insert( self, index, src, tgt ):
		self.srcs.insert( index, src )
		self.tgts.insert( index, tgt )
	def append( self, src, tgt ):
		self.srcs.append( src )
		self.tgts.append( tgt )
	def moveItem( self, index, places=1 ):
		src, tgt = self.pop( index )
		self.insert( index + places, src, tgt )
	def moveItemUp( self, index, places=1 ):
		places = abs( places )
		return self.moveItem( index, -places )
	def moveItemDown( self, index, places=1 ):
		places = abs( places )
		return self.moveItem( index, places )
	def setFromDict( self, mappingDict, ordering=() ):
		'''
		Sets the mapping from a mapping dictionary.  If an ordering iterable is given then the ordering
		of those sources is preserved.
		'''
		srcs = []
		tgts = []
		def appendTgt( src, tgt ):
			if isinstance( tgt, basestring ):
				srcs.append( src )
				tgts.append( tgt )
			elif isinstance( tgt, (list, tuple) ):
				for t in tgt:
					srcs.append( src )
					tgts.append( t )

		for src in ordering:
			tgt = mappingDict.pop( src )
			appendTgt( src, tgt )

		for src, tgt in mappingDict.iteritems():
			appendTgt( src, tgt )

		self.srcs = srcs
		self.tgts = tgts
	def asStr( self ):
		return '\n'.join( [ '%s  ->  %s' % m for m in self.iteritems() ] )
	@classmethod
	def FromDict( cls, mappingDict, ordering=() ):
		new = Mapping( [], [] )
		new.setFromDict( mappingDict, ordering )

		return new
	@classmethod
	def FromMapping( cls, mapping ):
		return cls( mapping.srcs, mapping.tgts )
	def asDict( self ):
		matchDict = {}
		for src, tgt in zip(self.srcs, self.tgts):
			try: matchDict[ src ].append( tgt )
			except KeyError: matchDict[ src ] = [ tgt ]

		return matchDict
	def asFlatDict( self ):
		matchDict = {}
		for src, tgt in zip(self.srcs, self.tgts):
			matchDict[ src ] = tgt

		return matchDict


def getCommonPrefix( strs ):
	'''
	returns the longest prefix common to all given strings

	example:
	>>> getCommonPrefix( ['something', 'someStuff', 'soma'] )
	som
	'''
	class PrefixDifference(Exception): pass

	prefix = ''
	first = strs[ 0 ]

	for n, s in enumerate( first ):
		try:
			for aStr in strs[ 1: ]:
				if s != aStr[ n ]:
					raise PrefixDifference

			prefix += s
		except PrefixDifference:
			return prefix


def matchCase( theStr, strToGetCaseFrom ):
	'''
	given an arbitrary string, this function will return a string with matching case of strToGetCaseFrom where possible.
	If the strToGetCaseFrom is shorter than the input string, then the remainder of theStr will match the case of the
	last character of strToGetCaseFrom

	example:
	>>> matchCase( 'somelowercasestr', 'SomeLowerCase' )
	SomeLowerCasestr
	'''
	matchedCase = []
	lastCaseWasLower = True
	for charA, charB in zip( theStr, strToGetCaseFrom ):
		tgtCaseIsLower = charB.islower()
		matchedCase.append( charA.lower() if tgtCaseIsLower else charA.upper() )

	lenA, lenB = len(theStr), len(strToGetCaseFrom)
	if lenA > lenB:
		remainder = theStr[lenB:]
		if tgtCaseIsLower:
			remainder = remainder.lower()

		matchedCase.append( remainder )

	return ''.join( matchedCase )


def stripInvalidChars( theStr,
                       invalidChars="""`~!@#$%^&*()-+=[]\\{}|;':"/?><., """,
                       replaceChar='_',
                       cleanDoubles=True,
                       stripTrailing=True ):
	'''
	strips "invalid" characters from the given string, replacing them with the replaceChar character.  If cleanDoubles
	is True, then any double replaceChar occurances are replaced with a single replaceChar after the invalid characters
	have been replaced
	'''
	cleanStr = theStr
	for char in invalidChars:
		cleanStr = cleanStr.replace( char, replaceChar )

	if cleanDoubles and replaceChar:
		doubleChar = replaceChar + replaceChar
		while doubleChar in cleanStr:
			cleanStr = cleanStr.replace( doubleChar, replaceChar )

	if stripTrailing:
		while cleanStr.endswith( '_' ):
			cleanStr = cleanStr[ :-1 ]

	return cleanStr


def camelCaseToNice( someString, tokenSeparator=' ' ):
	return name.CamelCaseName( someString ).toNice( tokenSeparator )


#end
