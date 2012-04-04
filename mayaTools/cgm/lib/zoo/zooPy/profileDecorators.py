import cProfile as prof
import pstats
import os
import time


def d_profile(f):
	'''
	writes out profiling info on the decorated function.  the profile results are dumped in a file
	called something like "_profile__<moduleName>.<functionName>.txt"
	'''
	def newFunc( *a, **kw ):
		def run(): f( *a, **kw )
		baseDir = os.path.split( __file__ )[0]

		tmpFile = os.path.join( baseDir, 'profileResults.tmp' )
		prof.runctx( 'run()', globals(), locals(), tmpFile )

		try:
			module = f.__module__
		except AttributeError:
			module = 'NOMODULE'

		dumpFile = os.path.join( baseDir, '_profile__%s.%s.txt' % (module, f.__name__) )
		dumpF = file( dumpFile, 'w' )
		stats = pstats.Stats( tmpFile )
		stats.sort_stats( 'time', 'calls', 'name' )
		stats.stream = dumpF
		stats.print_stats()

		stats.sort_stats( 'cumulative', 'time' )
		stats.print_stats()
		dumpF.close()

		#remove the tmpFile
		os.remove( tmpFile )
		print 'LOGGED PROFILING STATS TO', dumpFile

	newFunc.__name__ = f.__name__
	newFunc.__doc__ = f.__doc__

	return newFunc


def d_timer(f):
	'''
	simply reports the time taken by the decorated function
	'''
	def newFunc( *a, **kw ):
		s = time.clock()
		ret = f( *a, **kw )
		print 'Time Taken by %s:  %0.3g' % (f.__name__, time.clock()-s)

		return ret

	newFunc.__name__ = f.__name__
	newFunc.__doc__ = f.__doc__

	return newFunc


#end
