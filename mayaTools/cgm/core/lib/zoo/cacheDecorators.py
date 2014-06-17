'''
'''


def d_initCache(f):
	def __init__(*args, **kwargs):
		self = args[0]
		self._CACHE_ = {}

		return f(*args, **kwargs)

	__init__.__name__ = f.__name__
	__init__.__doc__ = f.__doc__

	return __init__
initCache = d_initCache


def d_cacheValue(f):
	def cachedRetValFunc(*args, **kwargs):
		self = args[0]
		try:
			return self._CACHE_[ f ]
		except KeyError:
			val = f(*args, **kwargs)
			self._CACHE_[ f ] = val
			return val
		#it may be a parent class has caching turned on, but the child class does not...
		except AttributeError:
			return f(*args, **kwargs)

	cachedRetValFunc.__name__ = f.__name__
	cachedRetValFunc.__doc__ = f.__doc__

	return cachedRetValFunc
cacheValue = d_cacheValue


def d_cacheValueWithArgs(f):
	def cachedRetValFunc(*args, **kwargs):
		self = args[0]
		funcArgsTuple = (f.__name__,)+tuple(args[1:])
		try:
			return self._CACHE_[funcArgsTuple]
		except KeyError:
			val = f(*args, **kwargs)
			self._CACHE_[funcArgsTuple] = val
			return val
		except TypeError:
			return f(*args, **kwargs)
		except AttributeError:
			return f(*args, **kwargs)

	cachedRetValFunc.__name__ = f.__name__
	cachedRetValFunc.__doc__ = f.__doc__

	return cachedRetValFunc
cacheValueWithArgs = d_cacheValueWithArgs


def d_resetCache(f):
	def resetCacheFunc(*args, **kwargs):
		self = args[ 0 ]
		retval = f(*args, **kwargs)
		try:
			self._CACHE_.clear()
			return retval
		except AttributeError:
			return retval

	resetCacheFunc.__name__ = f.__name__
	resetCacheFunc.__doc__ = f.__doc__

	return resetCacheFunc
resetCache = d_resetCache


#end