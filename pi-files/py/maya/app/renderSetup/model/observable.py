class Observable(object):
    """
    Observable class (subjects in the Observer Pattern:
    
    https://en.wikipedia.org/wiki/Observer_pattern
    
    ).  Observers are held through weak references.  It is not necessary
    for observers to remove themselves from ListItem subjects when they are
    about to be destroyed (in their __del__ method).  A ListItem subject
    will clean up these zombie observers on next invocation of its
    itemChanged().
    
    Notification of observers can carry information with it, by passing
    optional arguments to itemChanged() notification method.  It is therefore
    possible (though not mandatory) to define an interface for a list item
    change and all its observers so that observers use the arguments in the
    callback to understand what changed in the list item.  This implies
    that all observers must implement the same interface.  The simplest use
    is to pass in no arguments to itemChanged(), in which case observers
    can perform an overall refresh.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def addItemObserver(self, obs):
        """
        Add an observers to this item.
        
        Observers must be bound methods (e.g. given an instance c of class
        C, c.methodName), and are kept as weak references.
        """
    
        pass
    
    
    def itemChanged(self, *posArgs, **kwArgs):
        """
        Call item changed callbacks.
        
        The order in which observers are called is not specified.
        """
    
        pass
    
    
    def removeItemObserver(self, obs):
        """
        Remove an observer from this item.
        
        ValueError is raised by the remove item observer method if the
        argument observer is not found.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



