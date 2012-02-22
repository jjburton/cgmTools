

class Callback(object):
	'''
	stupid little callable object for when you need to "bake" temporary args into a
	callback - useful mainly when creating callbacks for dynamicly generated UI items
	'''
	def __init__( self, func, *a, **kw ):
		self._func = func
		self._args = a
		self._kwargs = kw
	def __call__( self, *args ):
		return self._func( *self._args, **self._kwargs )


def removeDupes( iterable ):
	'''
	performs order preserving, fast duplicate item removal
	'''
	unique = set()
	newIterable = iterable.__class__()
	for item in iterable:
		if item not in unique: newIterable.append(item)
		unique.add(item)

	return newIterable


def iterBy( iterable, count ):
	'''
	returns an generator which will yield "chunks" of the iterable supplied of size "count".  eg:
	for chunk in iterBy( range( 7 ), 3 ): print chunk

	results in the following output:
	[0, 1, 2]
	[3, 4, 5]
	[6]
	'''
	cur = 0
	i = iter( iterable )
	while True:
		try:
			toYield = []
			for n in range( count ): toYield.append( i.next() )
			yield toYield
		except StopIteration:
			if toYield: yield toYield
			break


#end
