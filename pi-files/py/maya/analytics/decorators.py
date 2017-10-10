"""
Collection of decorators for use with Maya analaytics.
There are three decorators defined here. You should use
all three so that your decorators become easily self-documented.

    @addMethodDocs        # Embed method docs into class docs
    @addHelp            # Print class docs from a method
    @makeAnalytic        # Flag the class as being an analytic
    class MyAnalytic(AnalyticBase):
        ...
"""

from maya.analytics.utilities import add_analytic

def __removeIndentation(theString, number=1):
    """
    Utility function to remove the leading documentation indentation in a documentation string.
    Presumes that the leading two tabs or 8 spaces are not part of the formatted documentation
    but leaves all other leading spaces. That's why a simple lstrip() couldn't be used.
    
    'number' is the number of indentation levels to remove. An indentation level is presumed
    to be either a single tab or 4 spaces. Normally you'd have number=2 for class methods and
    number=1 for regular methods.
    
    Returns a list of lines so that the caller can indent them the way they want.
    """

    pass


def make_static_analytic(cls):
    """
    Class decorator to add a discoverable static method that marks the
    class as being an analytic to run statically (i.e. that does not
    pertain to a particular scene).
        @make_static_anayltic
        class MYCLASS:
            ...
    """

    pass


def __removeIndentationFromLine(theString, number=1):
    """
    Utility function to remove the leading documentation indentation in a line of text pulled
    from a class method's "__doc__". Presumes that the leading two tabs or 8 spaces are not
    part of the formatted documentation but leaves all other leading spaces. That's why a
    simple lstrip() couldn't be used.
    
    'number' is the number of indentation levels to remove. An indentation level is presumed
    to be either a single tab or 4 spaces.
    """

    pass


def addHelp(cls):
    """
    Class decorator to add a static method addHelp() to a class that prints
    out the class.__fulldocs__ string. Use it in conjunction with @addMethodDocs
    to provide a static help method that prints out documentation for all
    exposed methods.
        @addHelp
        class MYCLASS:
            ...
    """

    pass


def addMethodDocs(cls):
    """
    Class decorator to add method docs to the class.__doc__.
        @addMethodDocs
        class MYCLASS:
            ...
    This won't report methods with a leading underscore so
    use that naming convention to prevent them from being shown.
    """

    pass


def makeAnalytic(cls):
    """
    Class decorator to add a discoverable static method that marks the
    class as being an analytic to run on a scene.
        @makeAnayltic
        class MYCLASS:
            ...
    """

    pass



