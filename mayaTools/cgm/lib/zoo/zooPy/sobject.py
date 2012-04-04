
from __future__ import with_statement

from cStringIO import StringIO
from functools import partial

#some boolean string values - should be lower-case!
BOOL_STR_VALUES = { 'false': False, 'no': False, '0': False }


class RewindableStreamIter(object):
	def __init__( self, iterable ):
		requiredMethodNames = 'tell', 'seek', 'readline'
		for methodName in requiredMethodNames:
			if not hasattr( iterable, methodName ):
				raise TypeError( "The given iterable is missing the required method %s" % methodName )

		self._iterable = iterable
		self._lineStartIdxStack = []
	def __iter__( self ):
		iterable = self._iterable
		lineStartIdxStack = self._lineStartIdxStack

		while True:
			lineStartIdxStack.append( iterable.tell() )
			line = iterable.readline()
			if not line:
				raise StopIteration

			yield line
	def rewind( self ):
		self._iterable.seek( self._lineStartIdxStack.pop() )


def getWhitespacePrefixLen( line, prefixType='\t' ):
	count = 0
	if not line:
		return count

	while line[count] == prefixType:
		count += 1

	return count


def findDigits( line ):
	idx = 0
	isdigit = str.isdigit
	for char in line:
		if not isdigit( char ):
			break

		idx += 1

	return line[ :idx ]


class SObject(object):

	#these are the types supported
	__SUPPORTED_TYPES = str, unicode, int, float, str, bool, long, list, tuple, dict, type(None)
	__SUPPORTED_TYPE_DICT = dict( ((t.__name__, t) for t in __SUPPORTED_TYPES) )
	__SUPPORTED_TYPES_SET = set( __SUPPORTED_TYPES )
	__SUPPORTED_KEY_TYPES = bool, int, long, float, str, unicode
	__SUPPORTED_TYPES_SET_SET = set( __SUPPORTED_KEY_TYPES )

	def __init__( self, *orderedAttrValuePairs, **unorderedAttrValuePairs ):
		'''
		you can initialize with either a list of 2-tuples if attribute ordering is important, or you can just provide
		key-value pairs if ordering is not important
		'''

		#for preserving attribute ordering
		self.__dict__[ '_attrNames' ] = []

		#
		self.__dict__[ '_eqRecursionCounter' ] = 0
		self.__dict__[ '_eqNodesAlreadyCompared' ] = set()

		for attrName, attrValue in orderedAttrValuePairs:
			setattr( self, attrName, attrValue )

		for attrName, attrValue in unorderedAttrValuePairs.iteritems():
			setattr( self, attrName, attrValue )
	def __hash__( self ):
		return id( self )
	def __eq__( self, other ):
		'''
		two SObjects are equal only if all they both possess the same attributes in the same order with
		the same values
		'''
		self._eqRecursionCounter += 1
		try:

			#if we've already visited this node then it must match - otherwise we'd have returned False already
			nodesAlreadyCompared = self._eqNodesAlreadyCompared | other._eqNodesAlreadyCompared
			if self in nodesAlreadyCompared:
				return True

			#add this node to the list of nodes compared already - we do this before the comparison below so that cyclical
			#references don't turn into infinite loops
			self._eqNodesAlreadyCompared.add( self )

			#compare attribute lists - attribute counts must match
			thisAttrNames, otherAttrNames = self.getAttrs(), other.getAttrs()
			if len( thisAttrNames ) != len( otherAttrNames ):
				return False

			#now that we know the attribute counts are the same, zip them together and iterate over them to compare names
			#and values
			for thisAttrName, otherAttrName in zip( thisAttrNames, otherAttrNames ):

				#attribute names must match - attribute ordering is important, so the attribute names must match exactly
				if thisAttrName != otherAttrName:
					return False

				#grab the actual attribute values
				thisAttrValue = getattr( self, thisAttrName )
				otherAttrValue = getattr( other, otherAttrName )
				if thisAttrValue != otherAttrValue:
					return False
		finally:
			self._eqRecursionCounter -= 1

		if self._eqRecursionCounter == 0:
			self._eqNodesAlreadyCompared.clear()

		return True
	def __ne__( self, other ):
		return not self.__eq__( other )
	def __setattr__( self, attr, value ):
		valueType = type( value )

		#type check the value - only certain types are supported
		if valueType is not SObject and valueType not in self.__SUPPORTED_TYPES:
			raise TypeError( "Serialization of the type %s is not yet supported!" % type( value ) )

		if attr not in self.__dict__:
			self.__dict__[ '_attrNames' ].append( attr )

		self.__dict__[ attr ] = value
	def __getitem__( self, item ):
		if hasattr( self, item ):
			return getattr( self, item )

		raise KeyError( "Object contains no such key '%s'!" % item )
	def __contains__( self, attr ):
		return hasattr( self, attr )
	def __str__( self ):
		stringBuffer = StringIO()
		self.serialize( stringBuffer )

		return stringBuffer.getvalue()
	def _roundTrip( self ):
		'''
		serialized the object to a string buffer and then unserializes from the same buffer - mainly
		useful for testing purposes
		'''
		stringBuffer = StringIO()
		self.serialize( stringBuffer )

		#make sure to rewind the buffer!
		stringBuffer.seek( 0 )

		return self.UnserializeStream( stringBuffer )
	@classmethod
	def IsValueSupported( cls, value ):
		'''
		returns whether the given value is supported by SObject.  Values that aren't supported will raise a TypeError when
		they get set as a value
		'''
		return type( value ) in cls.__SUPPORTED_TYPES_SET
	def getAttrs( self ):
		'''
		returns a tuple of attributes present on this object
		'''
		return tuple( self._attrNames )
	def serialize( self, stream, depth=1, serializedObjects=None ):
		if serializedObjects is None:
			serializedObjects = set()

		#write in the uuid for this SObject - we use the uuid for object referencing
		depthPrefix = '\t' * depth

		#track SObjects serialized so we don't get infinite loops if objects self reference
		if self in serializedObjects:
			stream.write( '%s\n' % id( self ) )
			return

		stream.write( '%s:\n' % id( self ) )
		serializedObjects.add( self )

		def serializeContainer( value, valueType, depth ):
			stream.write( '\n' )
			depthPrefix = '\t' * depth
			for v in value:
				vType = type( v )
				if vType is SObject:
					stream.write( '%s(*):' % depthPrefix )
					v.serialize( stream, depth+1, serializedObjects )
				elif vType in supportedTypes:
					stream.write( '%s(%s):' % (depthPrefix, vType.__name__) )
					valueSerializerMap.get( vType, defaultSerializer )( v, vType, depth+1 )
				else:
					raise TypeError( "The type %s isn't supported!" % vType.__name__ )

		def serializeDict( value, valueType, depth ):
			stream.write( '\n' )
			depthPrefix = '\t' * depth
			for k, v in value.iteritems():
				kType = type( k )
				if kType not in supportedKeyTypes:
					raise TypeError( '''The dict key type "%s" isn't supported!''' % kType )

				kStr = '(%s)%s' % (kType.__name__, k)
				vType = type( v )
				if vType is SObject:
					stream.write( '%s%s(*):' % (depthPrefix, kStr) )
					v.serialize( stream, depth+1, serializedObjects )
				elif vType in supportedTypes:
					stream.write( '%s%s(%s):' % (depthPrefix, kStr, vType.__name__) )
					valueSerializerMap.get( vType, defaultSerializer )( v, vType, depth+1 )
				else:
					raise TypeError( "The type %s isn't supported!" % vType.__name__ )

		def defaultSerializer( value, valueType, depth ):

			#escape newline characters
			if valueType is str or valueType is unicode:
				value = value.encode( 'unicode_escape' )

			stream.write( '%s\n' % value )

		valueSerializerMap = { list: serializeContainer, tuple: serializeContainer, dict: serializeDict }
		supportedTypes = self.__SUPPORTED_TYPES_SET
		supportedKeyTypes = self.__SUPPORTED_TYPES_SET

		for attr in self.getAttrs():
			value = getattr( self, attr )
			valueType = type( value )

			if valueType is SObject:
				stream.write( '%s%s(*):' % (depthPrefix, attr) )
				value.serialize( stream, depth+1, serializedObjects )
			else:
				stream.write( '%s%s(%s):' % (depthPrefix, attr, valueType.__name__) )
				if valueType in supportedTypes:
					valueSerializerMap.get( valueType, defaultSerializer )( value, valueType, depth+1 )
				else:
					raise TypeError( "The type %s isn't supported!" % valueTypeName )
	@classmethod
	def UnserializeStream( cls, stream ):
		'''
		expects a file-like object containing the serialized data to parse
		'''
		def getTypeFromTypeStr( typeStr ):
			typeCls = cls.__SUPPORTED_TYPE_DICT.get( typeStr, None )
			if typeCls is not None:
				return typeCls

			if typeStr is '*':
				return SObject

			raise TypeError( 'Unable to find the appropriate type for the type string "%s"' % typeStr )

		lineIter = RewindableStreamIter( stream )
		objectStack = []

		serializedIdToObjDict = {}  #track objects

		def getAttrDataFromLine( line ):
			idx_parenStart = line.find( '(' )
			idx_parenEnd = line.find( ')', idx_parenStart )
			idx_valueStart = line.find( ':', idx_parenEnd )

			attrName = line[ :idx_parenStart ].strip()
			typeStr = line[ idx_parenStart+1:idx_parenEnd ].strip()
			valueStr = line[ idx_valueStart+1:-1 ].lstrip()

			return attrName, typeStr, valueStr

		def getAttrDataFromDictLine( line ):
			idx_parenEnd = line.find( ')' )
			keyTypeStr = line[1:idx_parenEnd]
			keyTypeCls = getTypeFromTypeStr( keyTypeStr )

			keyValueStr, typeStr, valueStr = getAttrDataFromLine( line[idx_parenEnd+1:] )
			key = keyTypeCls( keyValueStr )

			return key, typeStr, valueStr

		def listParser( valueStr, typeCls, depth ):
			value = []
			for line in lineIter:
				lineDepth = getWhitespacePrefixLen( line )
				if lineDepth != depth:
					lineIter.rewind()
					return value

				line = line[ lineDepth: ]
				assert not line[0].isspace()

				_, typeStr, valueStr = getAttrDataFromLine( line )
				if typeStr == '*':
					value.append( objectParser( valueStr, depth+1 ) )
				else:
					typeCls = getTypeFromTypeStr( typeStr )
					v = valueUnserializerMap.get( typeCls, defaultParser )( valueStr, typeCls, depth+1 )
					value.append( v )

			return value

		def tupleParser( valueStr, typeCls, depth ):
			return tuple( listParser( valueStr, typeCls, depth ) )

		def dictParser( valueStr, typeCls, depth ):
			value = {}
			for line in lineIter:
				lineDepth = getWhitespacePrefixLen( line )
				if lineDepth != depth:
					lineIter.rewind()
					return value

				line = line[ lineDepth: ]
				assert not line[0].isspace()

				key, typeStr, valueStr = getAttrDataFromDictLine( line )
				typeCls = getTypeFromTypeStr( typeStr )
				if typeCls is SObject:
					value[ key ] = objectParser( valueStr, depth+1 )
				else:
					value[ key ] = valueUnserializerMap.get( typeCls, defaultParser )( valueStr, typeCls, depth+1 )

			return value

		def boolParser( valueStr, typeCls, depth ):
			return BOOL_STR_VALUES.get( valueStr.lower(), typeCls( valueStr ) )

		def noneParser( valueStr, typeCls, depth ):
			return None

		def defaultParser( valueStr, typeCls, depth ):
			if typeCls is str or typeCls is unicode:
				valueStr = valueStr.decode( 'unicode_escape' )

			return typeCls( valueStr )

		valueUnserializerMap = { list: listParser,
		                         tuple: tupleParser,
		                         dict: dictParser,
		                         type(None): noneParser,
		                         bool: boolParser }

		def objectParser( line, depth=1 ):
			serializedId = int( findDigits( line ) )

			#check to see if the id has already been unserialized
			if serializedId in serializedIdToObjDict:
				return serializedIdToObjDict[ serializedId ]

			#otherwise, construct a new object and track it
			newObj = serializedIdToObjDict[ serializedId ] = SObject()

			#append the new object to the stack
			objectStack.append( newObj )

			for line in lineIter:
				lineDepth = getWhitespacePrefixLen( line )
				if lineDepth != depth:
					lineIter.rewind()
					return objectStack.pop()

				attrName, typeStr, valueStr = getAttrDataFromLine( line )
				if typeStr == '*':
					value = objectParser( valueStr, depth+1 )
				else:
					typeCls = getTypeFromTypeStr( typeStr )
					value = valueUnserializerMap.get( typeCls, defaultParser )( valueStr, typeCls, depth+1 )

				setattr( objectStack[-1], attrName, value )

			return objectStack.pop()

		for line in lineIter:
			return objectParser( line )
	@classmethod
	def Unserialize( cls, theStr ):
		if not isinstance( theStr, basestring ):
			raise TypeError( "Need to pass in a string object!" )

		return cls.UnserializeStream( StringIO( theStr ) )
	def write( self, filepath ):
		with open( filepath, 'w' ) as fStream:
			self.serialize( fStream )
	@classmethod
	def Load( cls, filepath ):
		with open( filepath ) as fStream:
			return cls.UnserializeStream( fStream )
	@classmethod
	def FromDict( cls, theDict, dictObjectMap=None ):
		if dictObjectMap is None:
			dictObjectMap = {}

		theDictId = id( theDict )
		if theDictId in dictObjectMap:
			return dictObjectMap[ theDictId ]

		obj = cls()
		dictObjectMap[ theDictId ] = obj
		supportedTypes = cls.__SUPPORTED_TYPES_SET
		for key, value in theDict.iteritems():
			valueType = type( value )

			if valueType is dict:
				value = dictObjectMap[ id( value ) ] = cls.FromDict( value, dictObjectMap )
			elif valueType is list or valueType is tuple:
				isTuple = valueType is tuple
				if isTuple:
					value = list( value )

				for n, v in enumerate( value ):
					if type( v ) is dict:
						value[n] = dictObjectMap[ id( v ) ] = cls.FromDict( v, dictObjectMap )

				if isTuple:
					value = tuple( value )
			elif not valueType in supportedTypes:
				raise TypeError( "The type %s isn't supported!" % valueType.__name__ )

			setattr( obj, key, value )

		return obj
	def toDict( self, dictObjectMap=None ):
		if dictObjectMap is None:
			dictObjectMap = {}

		if self in dictObjectMap:
			return dictObjectMap[ self ]

		thisDict = dictObjectMap[ self ] = {}
		for key, value in self.iteritems():
			if type( value ) is SObject:
				thisDict[ key ] = value.toDict( dictObjectMap )
			else:
				thisDict[ key ] = value

		return thisDict

	#the following provide the dictionary interface
	def iteritems( self ):
		for attr in self.getAttrs():
			yield attr, getattr( self, attr )
	def items( self ):
		return list( self.iteritems() )
	def iterkeys( self ):
		return iter( self.getAttrs() )
	keys = getAttrs
	def itervalues( self ):
		for attr in self.getAttrs():
			yield getattr( self, attr )
	def values( self ):
		return self.itervalues()


def pickleToSObject( obj, pickledObjDict=None ):
	'''
	attempts to convert the given instance into an sobject.  This will suck all instance attributes from the object and put
	them on an sobject instance.  You can use unpickleFromSObject to turn it back into an instance
	'''
	if pickledObjDict is None:
		pickledObjDict = {}

	objId = id( obj )
	if objId in pickledObjDict:
		return pickledObjDict[ objId ]

	if type( obj ) is SObject:
		pickledObjDict[ objId ] = obj

		return obj

	sobject = pickledObjDict[ objId ] = SObject()
	for attrName, attrValue in obj.__dict__.iteritems():
		if not SObject.IsValueSupported( attrValue ):
			attrValue = pickleToSObject( attrValue )

		setattr( sobject, attrName, attrValue )

	for typeCls in (str, int, long, float, unicode, bool, list, tuple, dict):
		if isinstance( obj, typeCls ):
			sobject.__instance_value_sobject = typeCls( obj )
			break

	return sobject


def unpickleFromSObject( sobject, instanceCls ):
	'''
	unpickles a pickled instance

	example:
	obj = SomeCls()
	sobj = pickleToSObject( obj )
	objCopy = unpickleFromSObject( sobj, SomeCls )
	'''
	base = None
	hasBeenConstructed = False
	for typeCls in (str, int, long, float, unicode, bool, list, tuple, dict):
		if issubclass( instanceCls, typeCls ):
			base = typeCls
			break

	if base is None:
		base = object

	cls = type( 'Temp', (base,), {} )
	try:
		new = cls( getattr( sobject, '__instance_value_sobject'  ) )
	except AttributeError:
		new = cls()

	new.__class__ = instanceCls

	for attr, value in sobject.iteritems():
		new.__dict__[ attr ] = value

	return new


#end
