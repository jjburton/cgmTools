"""
Helper class that maintains the EM mode information. Given a string
to specifies an EM mode combination (type +/- evaluators) it will
handle the details regarding translating the mode description into
actions and turning the mode on and off.

String syntax is an abbreviated evaluation mode followed by zero or
more evaluator directives. Regex is [MODE]{[+-]EVALUATOR}*[/NODETYPE

Examples:
    dg            : Turn the EM off and go back to DG mode
    ems           : Turn the EM on and put it into serial mode
    emp           : Turn the EM on and put it into parallel mode
    emp+null      : Turn the EM on and enable the null evaluator
    emp-dynamics  : Turn the EM on and disable the dynamics evaluator
    emp-dynamics+deformer
                  : Turn the EM on, disable the dynamics evaluator, and
                    enable the deformer evaluator
    +cache        : Retain the current EM mode, enable the cache evaluator
    ems+null/transform : Turn the EM on to serial mode and enable the null evaluator
                         for all transform node types.

Calling the setMode() method will put the EM into the named mode.
Calling it again will exit that mode and put it into the new mode,
including unloading any plugins that had to be loaded. Destruction
or reassignment of the manager will restore the EM to the state it
had just before the first time the mode was set.

The node types enabled by any mentioned evaluators is remembered and
restored on exit. Any evaluators not explicitly appearing in the
evaluator directive list will not have its state remembered.

The plugin loading is not magic, it's a hardcoded list in this file.
Update it if you want to handle any new plugins.

The object is set up to use the Python "with" syntax as follows:

    with emModeManager() as mgr:
        mgr.setMode( someMode )

That will ensure the original states are all restored. There's no other
reliable way to do it in Python. If you need different syntax you can
manually call the method to complete the sequence:

    mgr = emModeManager()
    mgr.setMode( someMode )
    mgr.restore()
"""

class emModeManager(object):
    """
    Class for managing the EM state in a 'with' format. Remembers and
    restores the EM mode, active evaluators, and the node types enabled on
    those evaluators.
    """
    
    
    
    def __enter__(self):
        """
        #----------------------------------------------------------------------
        """
    
        pass
    
    
    def __exit__(self, type, value, traceback):
        """
        Ensure the state is restored if this object goes out of scope
        """
    
        pass
    
    
    def __init__(self):
        """
        Defining both __enter__ and __init__ so that either one can be used
        """
    
        pass
    
    
    def restore_state(self):
        """
        Restore the evaluation manager to its original mode prior to creation
        of this object. Using the "with" syntax this will be called automatically.
        You only need to call explicitly when you instantiate the mode manager
        as an object.
        
        For now the state is brute-force restored to what the original was without
        regards to current settings. The assumptions are that the states are
        independent, and the performance is good enough that it's not necessary to
        remember just the things that were changed.
        """
    
        pass
    
    
    def setMode(self, modeName):
        """
        Ensure the EM has a named mode set. See class docs for details on mode names.
        The changes are cumulative so long as they don't conflict so this only sets
        the mode to serial:
            self.setMode('emp')
            self.setMode('ems')
        however this will enable both evaluators
            self.setMode('+deformer')
            self.setMode('+cache')
        
        Changes can also be put into one single string:
            self.setMode( 'ems+deformer+cache' )
        
        Lastly by using the '/' character as a separator the enabled node types on
        evaluators can also be manipulated:
            self.setMode( 'ems+deformer+cache/+expression-transform' )
        
        raises SyntaxError if the mode name is not legal
        """
    
        pass
    
    
    def rebuild(include_scheduling=False):
        """
        Invalidate the EM and rebuild it.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def _hasEvaluationManager():
    """
    Check to see if the evaluation manager is available
    """

    pass


def _dbg(message):
    """
    Print a message only if debugging mode is turned on
    """

    pass


def as_list(thing):
    """
    Simple utility to ensure the thing is a list, return None as an empty list
    """

    pass



IN_DEBUG_MODE = False

RE_MODE = None

RE_EVALUATORS = None

EVALUATOR_PLUGINS = {}


