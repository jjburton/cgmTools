import exceptions

"""
Redefine format warning to avoid getting garbage at end of line when raised directly from Maya console
and define a UserWarning class that does only print it's message (no line or module info)
"""

class ExecutionWarning(exceptions.UserWarning):
    """
    Simple Warning class that doesn't print any information besides warning message
    """
    
    
    
    __weakref__ = None



def deprecated(funcOrMessage, className=None):
    """
    the decorator can either receive parameters or the function directly.
    
    If passed a message, the message will be appended to the standard deprecation warning and should serve to further
    clarify why the function is being deprecated and/or suggest an alternative function
    
    the className parameter is optional and should be included if the function is a method, since the name of the class
    cannot be automatically determined.
    """

    pass


def formatwarning(message, category, filename, lineno, line=None):
    """
    Redefined format warning for maya.
    """

    pass


def warn(*args, **kwargs):
    """
    Default Maya warn which uses ExecutionWarning as the default warning class.
    """

    pass



