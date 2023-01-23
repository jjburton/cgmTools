
from vectors import Vector

_MAX_RECURSE = 35


class BinarySearchTree(list):
	SORT_DIMENSION = 0

	def __init__( self, data ):
		list.__init__( self, data )

		#sort by the desired dimension
		if self.SORT_DIMENSION == 0:
			self.sort()
		else:
			sortDimension = self.SORT_DIMENSION
			self.sort( key=lambda v: v[ sortDimension ] )
	def getBestRange( self, value, data, breakRange=50 ):  #50 is arbitrary, but smaller values than this provide either incremental improvements or possibly even performance degredation
		'''
		returns a 2-tuple containing minIdx, maxIdx indices into the data list, with the given
		value somewhere within the range data[ minIdx:maxIdx ]

		breakRange - this is the delta between minIdx and maxIdx at which the iterative searching halts

		NOTE: the range returned may not be equal to the breakRange, breakRange is simply the
		point at which the search iteration breaks.  It is true however that the range returned
		will always be greater than breakRange/2
		'''

		sortDimension = self.SORT_DIMENSION

		minIdx = 0
		maxIdx = len( data )-1

		rng = maxIdx - minIdx
		while rng >= breakRange:
			half = minIdx + (rng / 2)
			halfValue = data[ half ][ sortDimension ]

			if halfValue == value:  #TODO: see what the cost of this is in the general case...
				return half, half

			if halfValue <= value:
				minIdx = half
			else:
				maxIdx = half

			rng = maxIdx - minIdx

		return minIdx, maxIdx
	def getWithin( self, theVector, tolerance=1e-6, maxCount=None ):
		'''
		returns a list of vectors near theVector within a given tolerance - optionally limiting the
		number of matches to maxCount
		'''

		#do some binary culling before beginning the search - the 50 number is arbitrary,
		#but values less than that don't lead to significant performance improvements, and
		#in fact can lead to performance degredation

		minX = theVector[0] - tolerance
		maxX = theVector[0] + tolerance

		minIdx, maxIdx = self.getBestRange( minX, self )

		#see whether we need to find a different value for the maxIdx - it may be appropriate already and if it is save some cycles by skipping the search
		if self[ maxIdx ][0] <= maxX:
			_x, maxIdx = self.getBestRange( maxX, self[ minIdx: ] )
			maxIdx += minIdx  #because we searched within self[ minIdx: ] so we need to add minIdx to maxIdx

		#we have a good range for appriate x values, now check to see of that subset which y values fit our criteria
		matchingY = []
		minY = theVector[1] - tolerance
		maxY = theVector[1] + tolerance
		for i in self[ minIdx:maxIdx ]:
			if minY <= i[1] <= maxY:
				matchingY.append( i )

		#do the same for z
		matching = []
		minZ = theVector[2] - tolerance
		maxZ = theVector[2] + tolerance
		for i in matchingY:
			if minZ <= i[2] <= maxZ:
				matching.append( i )

		#now the matching vectors is a list of vectors that fall within the bounding box with length of 2*tolerance.
		#we want to reduce this to a list of vectors that fall within the bounding sphere with radius tolerance
		inSphere = []
		sqTolerance = tolerance**2
		for m in matching:

			#this is basically inlined code to get the distance between the point we were given, and all the points
			#in the matching list so we can return in distance sorted order.  inlining the code is faster as is
			#comparing the squared distance to the squared tolerance
			sqD = (theVector[0] - m[0])**2 + (theVector[1] - m[1])**2 + (theVector[2] - m[2])**2
			if sqD <= sqTolerance:
				inSphere.append( (sqD, m) )

		inSphere.sort()

		if maxCount is not None:
			inSphere = inSphere[ :maxCount ]

		return [ v[1] for v in inSphere ]
	def getWithinRatio( self, theVector, ratio=2 ):
		global _MAX_RECURSE

		tolerance = 1
		matching = self.getWithin( theVector, tolerance )

		itCount = 0
		while not matching:
			tolerance *= 1.25
			itCount += 1
			matching = self.getWithin( theVector, tolerance )
			if itCount > _MAX_RECURSE:
				return None

		closestDist = (theVector - matching[0]).get_magnitude()
		if len( matching ) == 1 or not closestDist:
			return matching[ :1 ]

		return self.getWithin( theVector, closestDist*ratio )


#end
