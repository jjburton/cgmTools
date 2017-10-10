"""
This module implements a context and an associated decorator to run 
code with the root or a given Maya namespace as current.
It must decorate every function that involves render setup
nodes creation and renaming.
"""

class NamespaceGuard:
    """
    Safe way to set namespace using the 'with' statement.
    It will set the namespace back to the previously used namespace on exit from the block.
    The namespace changes WILL affect undo stack. Make sure to wrap it in an 
    undo chunk if needed.
    
    Example:
        with NamespaceGuard(ROOT_NAMESPACE):
            someCreateNodeFunction()
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, type, value, traceback):
        pass
    
    
    def __init__(self, namespace):
        pass



def guard(name):
    pass


def RootNamespaceGuard():
    pass


def root(f):
    pass



ROOT_NAMESPACE = ':'


