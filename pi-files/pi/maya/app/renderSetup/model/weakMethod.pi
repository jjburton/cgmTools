"""
Weak references to bound methods cannot be created directly: if no
strong reference to the bound method is kept, the bound method object is
immediately garbage collected, and the weak reference immediately points to
a dead object and returns None.  See:

http://stackoverflow.com/questions/599430/why-doesnt-the-weakref-work-on-this-bound-method

This module supports the intent, namely a bound method that can only be called
while its object is alive, and keeps its object by weak reference.
"""

class Method(object):
    """
    Wraps a method such that the bound method's object is held only by
    weak reference.
    """
    
    
    
    def __call__(self, *posArgs, **kwArgs):
        pass
    
    
    def __eq__(self, other):
        """
        # As per recommendations
        # https://docs.python.org/2/reference/datamodel.html#object.__eq__
        # implement both __eq__ and __ne__
        """
    
        pass
    
    
    def __init__(self, method):
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def isAlive(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def create(method):
    """
    # Convenience function.
    """

    pass



