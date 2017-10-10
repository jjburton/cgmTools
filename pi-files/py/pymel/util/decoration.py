def decorated(origFunc, newFunc, decoration=None):
    """
    Copies the original function's name/docs/signature to the new function, so that the docstrings
    contain relevant information again.
    Most importantly, it adds the original function signature to the docstring of the decorating function,
    as well as a comment that the function was decorated. Supports nested decorations.
    """

    pass


def decorator(func):
    """
    Decorator for decorators. Calls the 'decorated' function above for the decorated function, to preserve docstrings.
    """

    pass


def interface_wrapper(doer, args=[], varargs=None, varkw=None, defaults=None):
    """
    A wrapper which allows factories to programatically create functions with
    precise input arguments, instead of using the argument catch-all:
    
        >>> def f( *args, **kwargs ): #doctest: +SKIP
        ...     pass
    
    The inputs args, varargs, varkw, and defaults match the outputs of inspect.getargspec
    
    :param doer: the function to be wrapped.
    :param args: a list of strings to be used as argument names, in proper order
    :param defaults: a list of default values for the arguments. must be less than or equal
        to args in length. if less than, the last element of defaults will be paired with the last element of args,
        the second-to-last with the second-to-last and so on ( see inspect.getargspec ). Arguments
        which pair with a default become keyword arguments.
    """

    pass



