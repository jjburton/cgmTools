

class Name(str):
	'''
	class to make working with tokenizable names easier.  The interface is similar to the path.Path class
	'''
	def __new__( cls, name='', splitDelimiter=':', caseMatters=False ):
		if isinstance( name, cls ):
			return name

		if len( splitDelimiter ) != 1:
			raise Value( 'The split delimiter must be a single character!  Got "%s"' % splitDelimiter )

		new = str.__new__( cls, name )
		new._splits = tuple( name.split( splitDelimiter ) )
		new._delimiter = splitDelimiter
		new._caseMatters = caseMatters

		return new
	def __getitem__( self, item ):
		return self._splits[ item ]
	def __getslice__( self, theSlice ):
		return self._toksToPath( self._splits[ theSlice ] )
	def __len__( self ):
		return len( self._splits )
	def __contains__( self, item ):
		if not self._caseMatters:
			return item.lower() in [ s.lower() for s in self._splits ]

		return item in list( self._splits )
	def __hash__( self ):
		if not self._caseMatters:
			return hash( tuple( [ s.lower() for s in self._splits ] ) )

		return hash( self._splits )
	def _toksToPath( self, toks ):
		return type( self )( self._delimiter.join( toks ), self._delimiter, self._caseMatters )
	def isEqual( self, other ):
		other = type( self )( other, self._delimiter, self._caseMatters )

		if self._caseMatters:
			return self._splits == other._splits

		for t, o in zip( self, other ):
			if t.lower() != o.lower():
				return False

		return True
	__eq__ = isEqual
	def __ne__( self, other ):
		return not self.isEqual( other )
	def doesCaseMatter( self ):
		return self._caseMatters
	def split( self ):
		'''
		returns the splits tuple - ie the path tokens
		'''
		return list( self._splits )
	def up( self, levels=1 ):
		if not levels:
			return self

		toks = self._splits
		levels = max( min( levels, len(toks)-1 ), 1 )

		return self._toksToPath( toks[ :-levels ] )
	def replace( self, search, replace='' ):
		idx = self.index( search, caseMatters )
		toks = list( self.split() )
		toks[ idx ] = replace

		return self._toksToPath( toks )
	def find( self, search ):
		if self._caseMatters:
			toks = self.split()
		else:
			toks = [ s.lower() for s in self.split() ]
			search = search.lower()

		idx = toks.index( search )

		return idx
	index = find
	def startswith( self, other ):
		other = type( self )( other, self._delimiter, self._caseMatters )

		selfToks = self.split()
		otherToks = other.split()

		if len( otherToks ) > len( selfToks ):
			return False

		if not self._caseMatters:
			otherToks = [ t.lower() for t in otherToks ]
			selfToks = [ t.lower() for t in selfToks ]

		for tokOther, tokSelf in zip( otherToks, selfToks ):
			if tokOther != tokSelf:
				return False

		return True
	def endswith( self, other ):
		other = type( self )( other, self._delimiter, self._caseMatters )

		selfToks = list( self._splits )
		otherToks = list( other.split() )

		selfToks.reverse()
		otherToks.reverse()
		if not self._caseMatters:
			otherToks = [ t.lower() for t in otherToks ]
			selfToks = [ t.lower() for t in selfToks ]

		for tokOther, tokSelf in zip( otherToks, selfToks ):
			if tokOther != tokSelf:
				return False

		return True
	def likeness( self, tgt ):
		if str(self) == str(tgt):
			return 1

		if not isinstance( tgt, Name ):
			tgt = type( self )( tgt )

		srcTokens = self.split()
		tgtTokens = tgt.split()

		#if the split result is exact, early out
		if srcTokens == tgtTokens:
			return 1

		totalWeight = 0
		numSrcToks, numTgtToks = len(srcTokens), len(tgtTokens)

		for srcTok in srcTokens:
			bestMatch, bestMatchIdx = 0, -1
			isSrcDigit = srcTok.isdigit()
			for n, tgtTok in enumerate( tgtTokens ):

				#if one is a number token and the other isn't - there is no point proceeding as they're not going to match
				#letter tokens should not match number tokens
				isTgtDigit = tgtTok.isdigit()
				if isSrcDigit != isTgtDigit:
					continue

				#first, check to see if the names are the same
				tokSize = len( tgtTok )
				if srcTok == tgtTok:
					bestMatch = tokSize
					bestMatchIdx = n

				#are the tokens numeric tokens?  if so, we need to figure out how similar they are numerically - numbers
				#that are closer to one another should result in a better match
				elif isSrcDigit and isTgtDigit:
					srcInt, tgtInt = int(srcTok), int(tgtTok)
					largest = max( abs(srcInt), abs(tgtInt) )
					closeness = 1

					if srcInt != tgtInt:
						try:
							closeness = ( largest - abs( srcInt-tgtInt ) ) / float(largest)
						except ZeroDivisionError:
							closeness = 0

					bestMatch = tokSize * closeness
					bestMatchIdx = n

				#are the names the same bar case differences?
				elif srcTok.lower() == tgtTok.lower():
					bestMatch = tokSize
					bestMatchIdx = n

				#so now test to see if any of the tokens are "sub-words" of each other - ie if you have something_otherthing an_other
				#the second token, "otherthing" and "other", the second is a subset of the first, so this is a rough match
				else:
					srcTokSize = len(srcTok)
					lowSrcTok, lowTgtTok = srcTok.lower(), tgtTok.lower()
					smallestWordSize = min( srcTokSize, tokSize )
					subWordWeight = 0

					#the weight is calculated as a percentage of matched letters
					if srcTokSize > tokSize:
						subWordWeight = tokSize * tokSize / float(srcTokSize)
					else:
						subWordWeight = srcTokSize * srcTokSize / float(tokSize)

					#make sure the src and tgt tokens are non-trivial (ie more than 4 letters)
					if srcTokSize > 3 and tokSize > 3:
						if lowTgtTok in lowSrcTok or lowSrcTok in lowTgtTok:
							bestMatch = subWordWeight
							bestMatchIdx = n

			#remove the best match from the list - so it doesn't get matched to any other tokens
			if bestMatchIdx != -1:
				tgtTokens.pop( bestMatchIdx )
				numTgtToks -= 1

			totalWeight += bestMatch

		#get the total number of letters in the "words" of the longest name - we use this for a likeness baseline
		lenCleanSrc = sum( len( tok ) for tok in self )
		lenCleanTgt = sum( len( tok ) for tok in tgt )
		lenClean = max( lenCleanSrc, lenCleanTgt )

		return float( totalWeight ) / lenClean
	def toNice( self, separator=' ' ):
		return separator.join( self.split() )


def splitAtCamelCase( theStr, splitDelimiter ):
	'''
	will tokenize a camel cased string with an optional extra split delimiter
	'''
	try:
		prevCharCaseWasLower = theStr[0].islower()
		prevCharWasDigit = theStr[0].isdigit()
	except IndexError:
		return []

	#step through the string and look for token split cases
	toks = [theStr[0]]
	for char in theStr[1:]:
		if char == splitDelimiter:
			toks.append( '' )
			prevCharCaseWasLower = True
			prevCharWasDigit = False
		elif char.isdigit():
			if prevCharWasDigit:
				toks[-1] += char
			else:
				toks.append( char )

			prevCharCaseWasLower = True
			prevCharWasDigit = True
		elif prevCharWasDigit:
			toks.append( char )
			prevCharWasDigit = False
			prevCharCaseWasLower = char.islower()
		elif char.isupper() and prevCharCaseWasLower:
			toks.append( char )
			prevCharCaseWasLower = False
			prevCharWasDigit = False
		else:
			toks[-1] += char
			prevCharWasDigit = False
			prevCharCaseWasLower = char.islower()

	return [tok for tok in toks if tok ]


class CamelCaseName(Name):
	'''
	subclass for dealing with camel case names
	'''
	def __new__( cls, name='', splitDelimiter='_', caseMatters=False ):
		new = Name.__new__( cls, name, splitDelimiter, caseMatters )
		new._splits = splitAtCamelCase( name, splitDelimiter )

		return new
	def _toksToPath( self, toks ):
		toks = []
		for tok in self:
			if not tok[0].isupper():
				tok = tok[0].upper() + tok[1:]

		return CamelCaseName( ''.join( toks ), self._delimiter, self._caseMatters )



#end
