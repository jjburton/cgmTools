"""
A collection of utilities to help manage and inspect the frozen states.
Import all of the utilities to be able to use them.

from maya.debug.frozenUtilities import *
"""

class FrozenOptionsManager(object):
    """
    Helper class to manage scoping of a set of frozen options.
    
        with FrozenOptionsManager() as mgr:
            mgr.setOptions(...)
    """
    
    
    
    def __enter__(self):
        """
        Enter the scope of the manager, remembering current values
        """
    
        pass
    
    
    def __exit__(self, type, value, traceback):
        """
        Exit the scope of the manager, restoring remembered values
        """
    
        pass
    
    
    def __init__(self):
        """
        This is defined in parallel with __enter__ so that either can be used
        """
    
        pass
    
    
    def set_options(self, displayLayers=None, downstream=None, explicitPropagation=None, invisible=None, referencedNodes=None, runtimePropagation=None, upstream=None):
        """
        Initialize the options. Everything that is not explicitly set
        is turned off.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def freeze_nodes(nodes):
    """
    Sets the frozen attribute on the list of nodes passed in to True.
    Returns the list of nodes whose value was set. Usually it will be
    all nodes but some locked nodes may not have been set.
    """

    pass


def unfreeze_nodes(nodes=None):
    """
    Sets the frozen attribute on the list of nodes passed in to False.
    If None is passed in then all nodes with the frozen attribute set
    have it cleared.
    
    Returns the list of nodes whose value was set. Usually it will be
    all nodes but some locked nodes may not have been set.
    """

    pass


def list_frozen():
    """
    Returns a list of all nodes with the frozen attribute set
    """

    pass


def list_frozen_in_scheduling():
    """
    Returns a list of all nodes that were frozen either directly or
    indirectly as a result of the frozen evaluator settings.
    
    If no scheduling graph is available a TypeError is raised.
    If the frozen evaluator is not enabled an AttributeError is raised.
    """

    pass



RE_FROZEN_CLUSTER = None


