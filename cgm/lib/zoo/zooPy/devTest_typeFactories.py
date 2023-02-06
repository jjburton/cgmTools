
import unittest
import typeFactories


class TestTypeFactories(unittest.TestCase):
	def runTest( self ):
		class ITest(object):
			__metaclass__ = typeFactories.interfaceTypeFactory()
			def something( self, other, thing=None, *a, **kw ): pass
			def otherThing( self ): pass
			attribute = None

		class TestImplementation(ITest):
			def something( self, other, thing=None, *a, **kw ): pass
			def otherThing( self ): pass

		try:  #test differing method arg name
			class BrokenImplementation1(ITest):
				def something( self, OTHER, thing=None, *a, **kw ): pass
				def otherThing( self ): pass

			assert False  #if we get here, it means the class above has successfuly been created, which means the interface factory has failed to catch a broken interface implementation!
		except TypeError: pass

		try:  #test missing default value
			class BrokenImplementation2(ITest):
				def something( self, other, thing, *a, **kw ): pass
				def otherThing( self ): pass

			assert False
		except TypeError: pass

		try:  #test differing default value
			class BrokenImplementation3(ITest):
				def something( self, other, thing=1, *a, **kw ): pass
				def otherThing( self ): pass

			assert False
		except TypeError: pass

		try:  #test missing vkwargs
			class BrokenImplementation4(ITest):
				def something( self, other, thing=None, *a ): pass
				def otherThing( self ): pass

			assert False
		except TypeError: pass

		try:  #test missing method implementation
			class BrokenImplementation5(ITest):
				def something( self, other, thing=None, *a, **kw ): pass

			assert False
		except TypeError: pass

		class DuckImplementation(object):
			def something( self, other, thing=None, *a, **kw ): pass
			def otherThing( self ): pass
			def additional( self ): pass

		class DuckImplementationBroken(object):
			def blah( self ): pass

		assert typeFactories.doesImplement( DuckImplementation, ITest )
		assert not typeFactories.doesImplement( DuckImplementationBroken, ITest )

		def someFunctionToTestCallSigCompare( someArg, anotherArg=1, *vargs, **vkwargs ): pass
		def workingComparison1( someArg, anotherArg=1, *vargs, **vkwargs ): pass
		def workingComparison2( someArg, anotherArg=1, *a, **kw ): pass
		def brokenComparison1( anArg, anotherArg=1, *vargs, **vkwargs ): pass
		def brokenComparison2( someArg, otherArg=1, *vargs, **vkwargs ): pass
		def brokenComparison3( someArg, anotherArg=2, *vargs, **vkwargs ): pass

		assert typeFactories.compareCallSignatures( someFunctionToTestCallSigCompare, workingComparison1 )
		assert typeFactories.compareCallSignatures( someFunctionToTestCallSigCompare, workingComparison2 )
		assert not typeFactories.compareCallSignatures( someFunctionToTestCallSigCompare, brokenComparison1 )
		assert not typeFactories.compareCallSignatures( someFunctionToTestCallSigCompare, brokenComparison2 )
		assert not typeFactories.compareCallSignatures( someFunctionToTestCallSigCompare, brokenComparison3 )


#end
