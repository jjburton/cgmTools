"""
General utility functions that are not specific to Maya Commands or the 
OpenMaya API.

Note:
By default, handlers are installed for the root logger.  This can be overriden
with env var MAYA_DEFAULT_LOGGER_NAME.
Env vars MAYA_GUI_LOGGER_FORMAT and MAYA_SHELL_LOGGER_FORMAT can be used to 
override the default formatting of logging messages sent to the GUI and 
shell respectively.
"""

class StringTable(object):
    """
    The StringTable object allows access to the application's string catalog which is used, which is used to support application lookup for localized string resources.  The strings in this table may be over written by localized versions, which will then be picked up by scripts that access these values.
    
    This class behaves in the same way as a Dictionary object in Python with respect to getting and setting values.
    Note that StringTable objects just provide access to the single application-wide string table.  So, creating a new StringTable object does not create a new string table inside the application, it is just another interface to the existing global table.
    """
    
    
    
    def __delitem__(*args, **kwargs):
        """
        x.__delitem__(y) <==> del x[y]
        """
    
        pass
    
    
    def __getitem__(*args, **kwargs):
        """
        x.__getitem__(y) <==> x[y]
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __len__(*args, **kwargs):
        """
        x.__len__() <==> len(x)
        """
    
        pass
    
    
    def __setitem__(*args, **kwargs):
        """
        x.__setitem__(i, y) <==> x[i]=y
        """
    
        pass
    
    
    __new__ = None


class Output(object):
    """
    MayaOutput objects
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def flush(*args, **kwargs):
        """
        Flush no-op
        """
    
        pass
    
    
    def write(*args, **kwargs):
        """
        Write the given string
        """
    
        pass
    
    
    def writelines(*args, **kwargs):
        """
        Write the given sequence
        """
    
        pass
    
    
    softspace = None
    
    __new__ = None


import logging

class MayaGuiLogHandler(logging.Handler):
    """
    A python logging handler that displays error and warning
    records with the appropriate color labels within the Maya GUI
    """
    
    
    
    def emit(self, record):
        pass



def guiLogHandler():
    """
    Adds an additional handler to the root logger to print to
    the script editor.  Sets the shell/outputWindow handler to
    only print 'Critical' records, so that the logger's primary
    output is the script editor.
    Returns the handler.
    """

    pass


def _formatGuiResult(obj):
    """
    Gets a string representation of a result object.
    
    To perform an action when a result is about to returned to the script editor
    without modifying Maya's default printing of results, do the following:
    
        import maya.utils
        def myResultCallback(obj):
            # do something here...
            return maya.utils._formatGuiResult(obj)
        maya.utils.formatGuiResult = myResultCallback
    """

    pass


def helpNonVerbose(thing, title='Python Library Documentation: %s', forceload=0):
    """
    Utility method to return python help in the form of a string
    
    thing - str or unicode name to get help on
    title - format string for help result
    forceload - argument to pydoc.resolve, force object's module to be reloaded from file
    
    returns formated help string
    """

    pass


def getPossibleCompletions(input):
    """
    Utility method to handle command completion
    Returns in a list all of the possible completions that apply
    to the input string
    """

    pass


def shellLogHandler():
    """
    Adds an additional handler to the root logger to print to sys.stdout
    Returns the handler.
    """

    pass


def _mayadisplayhook(*args, **kwargs):
    """
    Display hook function used to capture interpreter results
    """

    pass


def _fixConsoleLineNumbers(tbStack):
    pass


def loadStringResourcesForFile(scriptPath, resourceFileName):
    """
    Load a string resource.
    
    The 'scriptPath' argument must be a string containing the full path of to 
    a language resource file. The 'resourceFileName' is the _res.py that must be loaded.
    
    If the _res.py fails to be found or executed successfully, the method returns False.
    Otherwise it returns True.
    """

    pass


def formatGuiResult(obj):
    pass


def _guiResultHook(obj):
    """
    In GUI mode, called by the command engine to stringify a result for display.
    """

    pass


def executeInMainThreadWithResult(*args, **kwargs):
    """
    Runs Python code in the main thread and waits for the return code.
    
    There are two different ways to call this function.  The first is to
    supply a single string argument which contains the Python code to execute.
    In that case the code is interpreted.
    
    The second way to call this routine is to pass it a "callable" object.
    When that is the case, then the remaining regular arguments and keyword
    arguments will be passed to the callable object
    
    Note that if this routine is called from the main thread, then it will
    simply execute the given Python on the spot and return the result
    """

    pass


def formatGuiException(exceptionType, exceptionObject, traceBack, detail=2):
    """
    Format a trace stack into a string.
    
        exceptionType   : Type of exception
        exceptionObject : Detailed exception information
        traceBack       : Exception traceback stack information
        detail          : 0 = no trace info, 1 = line/file only, 2 = full trace
                          
    To perform an action when an exception occurs without modifying Maya's 
    default printing of exceptions, do the following::
    
        import maya.utils
        def myExceptCB(etype, value, tb, detail=2):
            # do something here...
            return maya.utils._formatGuiException(etype, value, tb, detail)
        maya.utils.formatGuiException = myExceptCB
    """

    pass


def processIdleEvents(*args, **kwargs):
    """
    Run commands from the idle queue.
    
    In general there should be no need to call this method.  It is included here
    as it allows for testing of code that uses the idle events for processing.
    Use this method with caution as will change the behaviour of Maya by 
    possibly forcing refreshes or causing other code run before it normally would.
    This may make Maya unrepsonsive.
    
    This function will return True if all items on the idle queue have been 
    processed.  It will return False if only some of the items have been processed.
    There are several cases in which not all items on the idle queue will execute,
    such as when there is an item with exclusive priority.
    
    This function does not take any arguments.
    """

    pass


def executeDeferred(*args, **kwargs):
    """
    Delays the execution of the given script or function until Maya is idle.
    
    This function runs code using the idle event loop.  This means that the
    main thread must become idle before this python code will be executed.
    
    There are two different ways to call this function.  The first is to
    supply a single string argument which contains the Python code to execute.
    In that case the code is interpreted.
    
    The second way to call this routine is to pass it a "callable" object.
    When that is the case, then the remaining regular arguments and keyword
    arguments will be passed to the callable object
    """

    pass


def _decodeStack(tbStack):
    pass


def _dumpCurrentFrames():
    """
    # crash handling
    """

    pass


def _prefixTraceStack(tbStack, prefix='# '):
    """
    prefix with '#', being sure to get internal newlines. do not prefix first line
    as that will be added automatically.
    """

    pass


def _guiExceptHook(exceptionType, exceptionObject, traceBack, detail=2):
    """
    Whenever Maya receives an error from the command engine it comes into here
    to format the message for display. 
    Formatting is performed by formatGuiException.
        exceptionType   : Type of exception
        exceptionObject : Detailed exception information
        traceBack       : Exception traceback stack information
        detail          : 0 = no trace info, 1 = line/file only, 2 = full trace
    """

    pass


def loadStringResourcesForModule(moduleName):
    """
    Load the string resources associated with the given module
    
    Note that the argument must be a string containing the full name of the 
    module (eg "maya.app.utils").  The module of that name must have been 
    previously imported.
    
    The base resource file is assumed to be in the same location as the file
    defining the module and will have the same name as the module except with
    _res.py appended to it.  So, for the module foo, the resource file should
    be foo_res.py.  
    
    If Maya is running in localized mode, then the standard location for 
    localized scripts will also be searched (the location given by the 
    command cmds.about( localizedResourceLocation=True ))
    
    Failure to find the base resources for the given module will trigger an 
    exception. Failure to find localized resources is not an error.
    """

    pass



appLoggerName = ''

_shellLogHandler = None

_guiLogHandler = MayaGuiLogHandler()


