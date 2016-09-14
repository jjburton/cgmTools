
parityTestsL = ["l", "left", "lft", "lf", "lik"]
parityTestsR = ["r", "right", "rgt", "rt", "rik"]
DEFAULT_THRESHOLD = 1


class Parity(int):
	PARITIES = NONE, LEFT, RIGHT = None, 0, 1

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


class Name(object):
	'''
	Name objects are strings that are used to identify something such as an object or a filepath.
	this class creates some useful ways of comparing and manipulating Name objects
	'''
	PREFIX_DELIMETERS = ':|'
	PUNCTUATION = '_. '

	def __init__( self, nameItem='' ):
		#NOTE: this value should never be set directly...  instead use the set method or the string property
		self._string = str( nameItem )
		self.item = nameItem
		self.prefix = None

		#determines what characters denote a prefix boundary - so if it were set to ':' then apples:bananas would have the string 'apples:' as its prefix
		self.prefixDelimeters = self.PREFIX_DELIMETERS
		self.punctuation = self.PUNCTUATION
	def __str__( self ):
		return self._string
	__repr__ = __str__
	def __eq__( self, other ):
		return int( self.likeness( other ) )
	def __ne__( self, other ):
		return not self.__eq__( other )
	def __getitem__( self, item ):
		return self.split()[item]
	def __setitem__( self, item, newItem ):
		token = self[ item ]
		nameStr = str( self )
		startIdx = nameStr.find( token )
		endIdx = startIdx + len( token )

		#splice together a new string and we're done...
		self._string = '%s%s%s' % ( nameStr[:startIdx], newItem, nameStr[endIdx:] )
	def pop( self, item, stripSurroundingPunctuation=True ):
		PUNCTUATION = self.PUNCTUATION

		token = self[ item ]
		nameStr = str( self )
		startIdx = nameStr.find( token )
		endIdx = startIdx + len( token )

		'''
		#now strip surrounding whitespace or punctuation
		if stripSurroundingPunctuation:
			puncEndOffset = 0
			hasEndPunc = False
			for char in nameStr[ endIdx: ]:
				if char in PUNCTUATION:
					puncEndOffset += 1
					hasEndPunc = True
				else: break

			reversedStartChunk = ''.join( reversed( list( nameStr[ :startIdx ] ) ) )

			puncStartOffset = 0
			hasStartPunc = False

			for char in reversedStartChunk:
				if char in PUNCTUATION:
					puncStartOffset -= 1
					hasStartPunc = True
				else: break

			if hasStartPunc and hasEndPunc:
				startIdx -= max( 0, puncStartOffset )
				endIdx += puncEndOffset
				'''

		newNameStr = '%s%s' % ( nameStr[:startIdx], nameStr[endIdx:] )

		removeStart = startIdx
		#for n, char in enumerate( newNameStr[ startIdx: ] ):


		#splice together a new string and we're done...
		self._string = '%s%s' % ( nameStr[:startIdx], nameStr[endIdx:] )
	def __nonzero__( self ):
		try:
			self._string[0]
			return True
		except IndexError: return False
	def set( self, newString ):
		self._string = newString
	string = property(__str__, set)
	def get_parity( self ):
		'''
		doing this comparison is a little faster than using the cache lookup - and parity gets hammered on in likeness determination
		'''
		try: return self._parity
		except AttributeError:
			self._parity, self._parityStr = hasParity( self.split() )

		return self._parity
	parity = property( get_parity )
	def strip_parity( self ):
		return str( stripParity( self ) )
	def swap_parity( self ):
		return self.__class__( swapParity(self) )
	def cache_prefix( self, delimeters=None ):
		'''strips any namespace or path data from the name string - by default the stripping is done
		"in place", but if the inPlace variable is set to true, then a new Name object is returned'''
		self.prefix = ''
		string = self._string.strip()
		lastMatch = -1
		if delimeters is None:
			delimeters = self.prefixDelimeters

		for char in delimeters:
			matchPos = string.rfind(char)
			if matchPos > lastMatch:
				lastMatch = matchPos

		#store the prefix string
		if lastMatch != -1:
			self.prefix = string[:lastMatch+1]
			self._string = string[lastMatch+1:]

		return self.prefix
	def uncache_prefix( self ):
		if self.prefix != None:
			self._string = self.prefix + self._string
		return self._string
	def get_prefix( self, delimeters=None ):
		'''strips any namespace or path data from the name string - by default the stripping is done
		"in place", but if the inPlace variable is set to true, then a new Name object is returned'''
		if self.prefix is None:
			return self.cache_prefix( delimeters )
		else: return self.prefix
	def likeness( self, other, parityMatters=False, stripFirst=True ):
		'''
		given two Name objects this method will return a "likeness" factor based on how similar
		the two name strings are.  it compares name tokens - tokens are defined by either camel case
		or any character defined in the self.punctuation variable.  so for example:
		thisStringHas_a_fewTokens

		has the tokens: this, String, Has, a, few, Tokens

		given two names, the more tokens that match, the higher the likeness.  the tokens don't have
		to match exactly - a few tests are done such as case difference, subset test and numeric comparison
		'''
		#do stripping if required
		#if stripFirst: self.cache_prefix()

		#if the names match exactly, return the highest likeness
		if str(self) == str(other): return 1

		srcTokens = self.split()[:]
		tgtTokens = other.split()[:]

		if parityMatters:
			if self.parity != other.parity:
				return 0

		#if the split result is exact, early out
		if srcTokens == tgtTokens: return 1

		exactMatchWeight = 1.025
		totalWeight = 0
		numSrcToks, numTgtToks = len(srcTokens), len(tgtTokens)

		for srcTok in srcTokens:
			bestMatch,bestMatchIdx = 0,-1
			isSrcDigit = srcTok.isdigit()
			for n,tgtTok in enumerate(tgtTokens):
				tokSize = len(tgtTok)
				isTgtDigit = tgtTok.isdigit()

				#if one is a number token and the other isn't - there is no point proceeding as they're not going to match
				#letter tokens should not match number tokens - i guess it would be possible to test whether the word token
				#was a number name, but this would be expensive, and would only help fringe cases
				if isSrcDigit != isTgtDigit:
					continue

				#first, check to see if the names are the same
				if srcTok == tgtTok:
					bestMatch = tokSize * exactMatchWeight
					bestMatchIdx = n
					break

				#are the tokens numeric tokens?  if so, we need to figure out how similar they are numerically - numbers that are closer to one another should result in a better match
				elif isSrcDigit and isTgtDigit:
					srcInt,tgtInt = int(srcTok),int(tgtTok)
					largest = max( abs(srcInt), abs(tgtInt) )
					closeness = 1

					if srcInt != tgtInt: closeness = ( largest - abs( srcInt-tgtInt ) ) / float(largest)
					bestMatch = tokSize * closeness
					bestMatchIdx = n
					break

				#are the names the same bar case differences?
				elif srcTok.lower() == tgtTok.lower():
					bestMatch = tokSize
					bestMatchIdx = n
					break

				#so now test to see if any of the tokens are "sub-words" of each other - ie if you have something_otherthing an_other
				#the second token, "otherthing" and "other", the second is a subset of the first, so this is a rough match
				else:
					srcTokSize = len(srcTok)
					lowSrcTok,lowTgtTok = srcTok.lower(),tgtTok.lower()
					smallestWordSize = min( srcTokSize, tokSize )
					subWordWeight = 0

					#the weight is calculated as a percentage of matched letters
					if srcTokSize > tokSize: subWordWeight = tokSize * tokSize / float(srcTokSize)
					else: subWordWeight = srcTokSize * srcTokSize / float(tokSize)

					if srcTokSize > 2 and tokSize > 2:
						#make sure the src and tgt tokens are non-trivial (ie at least 3 letters)
						if lowSrcTok.find(lowTgtTok) != -1 or lowTgtTok.find(lowSrcTok) != -1:
							bestMatch = subWordWeight
							bestMatchIdx = n

			#remove the best match from the list - so it doesn't get matched to any other tokens
			if bestMatchIdx != -1:
				tgtTokens.pop(bestMatchIdx)
				numTgtToks -= 1

			totalWeight += bestMatch

		#get the total number of letters in the "words" of the longest name - we use this for a likeness baseline
		lenCleanSrc = len(self._string)-self._string.count('_')
		lenCleanTgt = len(other._string)-other._string.count('_')
		#lenCleanSrc = len(''.join(self.split()))
		#lenCleanTgt = len(''.join(other.split()))
		lenClean = max( lenCleanSrc, lenCleanTgt )

		return totalWeight / ( lenClean*exactMatchWeight )
	def strip( self, inPlace=True ):
		'''strips any namespace or path data from the name string - by default the stripping is done
		"in place", but if the inPlace variable is set to false, then a new Name object is returned'''
		string = self._string.strip()
		for char in self.prefixDelimeters:
			lastMatch = string.rfind(char)
			if lastMatch != -1:
				string = string[lastMatch+1:]

		#if we're to perform the operation in place, then modify the self._string variable and return
		if inPlace:
			self._string = string
			return self

		return self.__class__( string )
	def split( self, aString=None ):
		'''
		retuns a list of name tokens.  tokens are delimited by either camel case separation,
		digit grouping, or any character present in the self.punctuation variable - the list of
		tokens is returned
		'''
		if aString is None:
			aString = self._string

		try:
			tokens = [aString[0]]
		except IndexError: return []

		prevCharCaseWasLower = aString[0].islower()
		prevCharWasDigit = aString[0].isdigit()

		#step through the string and look for token split cases
		for char in aString[1:]:
			isLower = char.islower()
			if char in self.punctuation:
				tokens.append('')
				prevCharCaseWasLower = True
				prevCharWasDigit = False
				continue
			if char.isdigit():
				if prevCharWasDigit: tokens[-1] += char
				else: tokens.append(char)
				prevCharCaseWasLower = True
				prevCharWasDigit = True
				continue
			if prevCharWasDigit:
				tokens.append(char)
				prevCharWasDigit = False
				prevCharCaseWasLower = isLower
				continue
			elif prevCharCaseWasLower and not isLower: tokens.append(char)
			else: tokens[-1] += char

			prevCharWasDigit = False
			prevCharCaseWasLower = isLower

		#finally get rid of any empty/null array entries - this could be done above but is easier (maybe even faster?) to do as a post step
		return [tok for tok in tokens if tok ]
	def redo_split( self, aString=None ):
		#forces a rebuild of the token cache
		return self.split()


def hasParity( nameToks, popParityToken=True ):
	'''
	returns a parity number for a given name.  parity is 0 for none, 1 for left, and 2 for right
	'''
	lowerToks = [ tok.lower() for tok in nameToks ]
	lowerToksSet = set( lowerToks )
	existingParityToksL = lowerToksSet.intersection( set( parityTestsL ) )

	if len( existingParityToksL ):
		parityStr = existingParityToksL.pop()
		if popParityToken:
			idx = lowerToks.index( parityStr )
			nameToks.pop( idx )

		return Parity.LEFT, parityStr

	existingParityToksR = lowerToksSet.intersection( set( parityTestsR ) )
	if len( existingParityToksR ):
		parityStr = existingParityToksR.pop()
		if popParityToken:
			idx = lowerToks.index( parityStr )
			nameToks.pop( idx )

		return Parity.RIGHT, parityStr

	return Parity.NONE, None


def swapParity( name ):
	if not isinstance( name, Name ):
		name = Name( name )

	nameToks = name.split()
	lowerToks = [tok.lower() for tok in nameToks]
	lowerToksSet = set(lowerToks)

	allParityTests = [ parityTestsL, parityTestsR ]

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


def stripParity( name ):
	if not isinstance( name, Name ):
		name = Name( name )

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


def getCommonPrefix( strs ):
	'''
	returns the longest prefix common to all given strings
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


def matchCase( theStr, caseToMatch ):
	matchedCase = []
	lastCaseWasLower = True
	for charA,charB in zip(theStr,caseToMatch):
		lastCaseWasLower = charB.islower()
		a = (charA.upper(), charA.lower()) [ lastCaseWasLower ]
		matchedCase.append(a)

	lenA, lenB = len(theStr), len(caseToMatch)
	if lenA > lenB:
		remainder = theStr[lenB:]
		if lastCaseWasLower: remainder = remainder.lower()
		matchedCase.extend( remainder )

	return ''.join( matchedCase )


def matchNames( srcList, tgtList, strip=True, parity=True, unique=False, opposite=False, threshold=DEFAULT_THRESHOLD, **kwargs ):
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


def matchNamesDict( srcList, tgtList, **kwargs ):
	matches = matchNames(srcList, tgtList, **kwargs)
	matchDict = {}
	for src, tgt in zip(srcList, matches):
		matchDict[src] = tgt

	return matchDict


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


INVALID_CHARS = """`~!@#$%^&*()-+=[]\\{}|;':"/?><., """
def stripInvalidChars( theString, cleanDoubles=True, stripTrailing=True ):
	'''
	strips "invalid" characters from the given string, replacing them with an "_" character.  if
	cleanDoubles is true, then any double "_" occurances are replaced with a single "_"
	'''
	for char in INVALID_CHARS:
		theString = theString.replace( char, '_' )

	if cleanDoubles:
		cleaned = theString
		while True:
			cleaned = theString.replace( '__', '_' )
			if cleaned == theString: break
			theString = cleaned

		theString = cleaned

	if stripTrailing:
		while theString.endswith( '_' ):
			theString = theString[ :-1 ]

	return theString


#end