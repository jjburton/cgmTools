
import inspect


def trackableTypeFactory( metaclassSuper=type ):
	'''
	returns a metaclass that will track subclasses.  All classes of the type returned by this factory will
	have the following class methods implemented:
		IterSubclasses()
		GetSubclasses()
		GetNamedSubclass( name )

	usage:
		class SomeClass( metaclass=trackableTypeFactory() ): pass
		class SomSubclass( SomeClass ): pass

		print SomeClass.GetSubclasses()

	NOTE: the metaclass that is returned inherits from the metaclassSuper arg, which defaults to type.  So
	if you want to mix together metaclasses, you can inherit from a subclass of type
	'''
	_SUB_CLASS_LIST = []  #stores the list of all subclasses in the order they're created
	_SUB_CLASS_DICT = {}  #makes for fast lookups of named subclasses

	def IterSubclasses( cls ):
		'''
		iterates over all subclasses
		'''
		for c in _SUB_CLASS_LIST:
			if c is cls:  #skip the class we're calling this on
				continue

			if issubclass( c, cls ):
				yield c

	def GetSubclasses( cls ):
		'''
		returns a list of subclasses
		'''
		return list( cls.IterSubclasses() )

	def GetNamedSubclass( cls, name ):
		'''
		returns the first subclass found with the given name
		'''
		return _SUB_CLASS_DICT.get( name, None )

	class _TrackableType(metaclassSuper):
		def __new__( cls, name, bases, attrs ):
			newCls = metaclassSuper.__new__( cls, name, bases, attrs )
			_SUB_CLASS_LIST.append( newCls )
			_SUB_CLASS_DICT.setdefault( name, newCls )  #set default so subclass name clashes are resolved using the first definition parsed

			#insert the methods above into the newCls unless the names are already taken on the newCls
			if not hasattr( newCls, 'IterSubclasses' ):
				newCls.IterSubclasses = classmethod( IterSubclasses )

			if not hasattr( newCls, 'GetSubclasses' ):
				newCls.GetSubclasses = classmethod( GetSubclasses )

			if not hasattr( newCls, 'GetNamedSubclass' ):
				newCls.GetNamedSubclass = classmethod( GetNamedSubclass )

			return newCls

	return _TrackableType


def compareCallSignatures( func1, func2, matchDefaults=True ):
	'''
	given two function objects, this will compare the call signatures of each function and
	return True if they match.  If matchDefaults is True, default argument values must match
	'''
	args1, vargs1, kwargs1, defaults1 = inspect.getargspec( func1 )
	args2, vargs2, kwargs2, defaults2 = inspect.getargspec( func2 )

	if args1 != args2:
		return False

	if bool( vargs1 ) != bool( vargs2 ):
		return False

	if bool( kwargs1 ) != bool( kwargs2 ):
		return False

	if matchDefaults:
		if defaults1 != defaults2:
			return False

	return True


def interfaceTypeFactory( metaclassSuper=type ):
	'''
	returns an "Interface" metaclass.  Interface classes work as you'd expect.  Every method implemented
	on the interface class must be implemented on subclasses otherwise a TypeError will be raised at
	class creation time.

	usage:
		class IFoo( metaclass=interfaceTypeFactory() ):
			def bar( self ): pass

		subclasses must implement the bar method

	NOTE: the metaclass that is returned inherits from the metaclassSuper arg, which defaults to type.  So
	if you want to mix together metaclasses, you can inherit from a subclass of type.  For example:
		class IFoo( metaclass=interfaceTypeFactory( trackableTypeFactory() ) ):
			def bar( self ): pass

		class Foo(IFoo):
			def bar( self ): return None

		print( IFoo.GetSubclasses() )
	'''
	class _AbstractType(metaclassSuper):
		_METHODS_TO_IMPLEMENT = None
		_INTERFACE_CLASS = None

		def _(): pass
		_FUNC_TYPE = type( _ )

		def __new__( cls, name, bases, attrs ):
			newCls = metaclassSuper.__new__( cls, name, bases, attrs )

			#if this hasn't been defined, then cls must be the interface class
			if cls._METHODS_TO_IMPLEMENT is None:
				cls._METHODS_TO_IMPLEMENT = methodsToImplement = []
				cls._INTERFACE_CLASS = newCls
				for name, obj in attrs.items():
					if type( obj ) is cls._FUNC_TYPE:
						methodsToImplement.append( name )

			#otherwise it is a subclass that should be implementing the interface
			else:
				if cls._INTERFACE_CLASS in bases:
					for methodName in cls._METHODS_TO_IMPLEMENT:

						#if the newCls' methodName attribute is the same method as the interface
						#method, then the method hasn't been implemented.  Its done this way because
						#the newCls may be inheriting from multiple classes, one of which satisfies
						#the interface - so we can't just look up the methodName in the attrs dict
						methodImplementation = getattr( newCls, methodName, None )
						methodAbstract = getattr( cls._INTERFACE_CLASS, methodName )
						if methodImplementation.im_func is methodAbstract.im_func:
							raise TypeError( "The class %s doesn't implement the required method %s!" % (name, methodName) )

						if not compareCallSignatures( methodImplementation, methodAbstract ):
							raise TypeError( "The call signature of %s.%s doesn't match the interface method!" % (name, methodName) )

			return newCls

	return _AbstractType


def doesImplement( theCls, theInterfaceCls ):
	'''
	will test whether theCls implements the methods on theInterfaceCls
	'''
	for methodName in theInterfaceCls._METHODS_TO_IMPLEMENT:
		methodAbstract = getattr( theInterfaceCls, methodName )
		methodImplementation = getattr( theCls, methodName, None )

		if methodImplementation is None:
			return False

		if type( methodImplementation ) is not type( methodAbstract ):
			return False

		#check function signature
		if not compareCallSignatures( methodImplementation, methodAbstract ):
			return False

	return True


def trackableClassFactory( superClass=object ):
	'''
	returns a class that tracks subclasses.  for example, if you had classB(classA)
	ad you wanted to track subclasses, you could do this:

	class classB(trackableClassFactory( classA )):
		...

	a classmethod called GetSubclasses is created in the returned class for
	querying the list of subclasses

	NOTE: this is a convenience function for versions of python that don't support
	the metaclass class constructor keyword.  Python 2.6 and before need you to
	use the __metaclass__ magic class attribute to define a metaclass
	'''
	class TrackableClass(superClass): __metaclass__ = trackableTypeFactory()
	return TrackableClass


#end
