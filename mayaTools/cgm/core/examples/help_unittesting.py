"""
------------------------------------------
cgm.core.examples
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Help for learning the basis of unittesting

TODO: Module and test setup
================================================================
"""
#>>The basic premise of unit testing is is a series of assertations to make sure that things that we tried to make happen did
assert 1==1
#Nothing, 1 does indeed equal 1 so nothing happens
assert 1==2
#// Error: Encountered exception:  // 

#Okay, so it is great to know that there is something wrong but this doesn't help much if this is in a long line of code
#Instead, we can offer an exception message with it
assert 1==2,"No, 1 != 2"

"""
Help for learning basic unitTesting

CG Monks
-Josh Burton
01.25.2014

www.cgmonks.com
"""

#That's better. what else can we do with it, let's do a little meta
mi_n1Created = cgmMeta.cgmNode(nodeType = 'transform')#create a transform
mi_n1Initialized = cgmMeta.cgmNode(mi_n1Created.mNode)#Initialze that same transform to a new instance
assert mi_n1Created == mi_n1Initialized,"Created and intialzed nodes not the same"
#Well, that's handy to  know...

mi_n1Created.ty = 2
assert mi_n1Created == mi_n1Initialized,"Created and intialzed nodes not the same"
#They're still the same...because we only moved one, not changed what it is
assert mi_n1Created.ty == mi_n1Initialized.ty#We moved the one, so we moved both

mi_n2Created = cgmMeta.cgmNode(nodeType = 'transform')#create a newtransform
assert mi_n1Created !=  mi_n2Created,"n1 and n2 are same nodes"#

#Let's look at a real example. This is from cgm.core.cgmPy.validateArgs.ut_isFloatEquivalent
#Because of Maya's finicky returns for some values - 0's especially, we wanted a good way to verify values. 
#this is the test for the that function (which also in the same module)
def ut_isFloatEquivalent():
    assert isFloatEquivalent(-4.11241646134e-07,0.0),"sc>0.0 fail"
    assert isFloatEquivalent(-4.11241646134e-07,0.00001),"sc>0.00001 fail"
    assert isFloatEquivalent(-4.11241646134e-07,-0.0),"sc>0.00001 fail"
    assert isFloatEquivalent(0.0,-0.0),"0.0>-0.0 fail"
    assert isFloatEquivalent(0.0,0),"0.0>0 fail"
    return True

from cgm.core.cgmPy import validateArgs as cgmValid
cgmValid.ut_isFloatEquivalent()


