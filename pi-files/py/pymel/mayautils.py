"""
These do not require initialization of maya.standalone
"""

from pymel.util.path import path as _path

def recurseMayaScriptPath(roots=[], verbose=False, excludeRegex=None, errors='warn', prepend=False):
    """
    Given a path or list of paths, recurses through directories appending to
    the ``MAYA_SCRIPT_PATH`` environment variable any found directories containing
    mel scripts.
    
    The root directories, if given, are always added to the ``MAYA_SCRIPT_PATH``,
    even if they don't contain any mel scripts.
    
    :Parameters:
        roots : str or list of str
            a single path or list of paths to recurse. if left to its default, will use the current
            ``MAYA_SCRIPT_PATH`` values
    
        verobse : bool
            verbose on or off
    
        excludeRegex : str
            string to be compiled to a regular expression of paths to skip.  This regex only needs to match
            the folder name
    """

    pass


def executeDeferred(func, *args, **kwargs):
    """
    This is a wrap for maya.utils.executeDeferred.  Maya's version does not execute at all when in batch mode, so this
    function does a simple check to see if we're in batch or interactive mode.  In interactive it runs maya.utils.executeDeferred,
    and if we're in batch mode, it just executes the function.
    
    Use this function in your userSetup.py file if:
        1. you are importing pymel there
        2. you want to execute some code that relies on maya.cmds
        3. you want your userSetup.py to work in both interactive and standalone mode
    
    Example userSetup.py file::
    
        from pymel.all import *
        def delayedStartup():
           print "executing a command"
           pymel.about(apiVersion=1)
        mayautils.executeDeferred( delayedStartup )
    
    Takes a single parameter which should be a callable function.
    """

    pass


def getUserPrefsDir():
    """
    Get the prefs directory below the Maya application directory
    """

    pass


def source(file, searchPath=None, recurse=False):
    """
    Execute a python script.
    
    Search for a python script in the specified path and execute it using
    ``execfile``.
    
    :Parameters:
        searchPath : list of str
            list of directories in which to search for ``file``.
            uses ``sys.path`` if no path is specified
        
        recurse : bool
            whether to recurse into directories in ``searchPath``
    """

    pass


def getUserScriptsDir():
    """
    Get the scripts directory below the Maya application directory
    """

    pass


def getMayaLocation(version=None):
    """
    Get the path to the Maya install directory.
    
    .. note:: The Maya location is defined as the directory above /bin.
    
    Uses the ``MAYA_LOCATION`` environment variable and ``sys.executable`` path.
    
    Returns None if not found.
    
    :Parameters:
        version : bool
            if passed, will attempt to find a matching Maya location.  If the
            version found above does not match the requested version, 
            this function uses a simple find/replace heuristic to modify the path and test
            if the desired version exists.
    
    :rtype: str or None
    """

    pass


def getMayaAppDir(versioned=False):
    """
    Get the path to the current user's Maya application directory.
    
    First checks ``MAYA_APP_DIR``, then tries OS-specific defaults.
    
    Returns None, if not found
    
    :Parameters:
        versioned : bool
            if True, the current Maya version including '-x64' suffix, if applicable,
            will be appended.
    
    :rtype: str or None
    """

    pass



_logger = None

sep = ':'


