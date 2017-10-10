"""
Maya-related functions, which are useful to both `api` and `core`, including `mayaInit` which ensures
that maya is initialized in standalone mode.
"""

from pymel.util.shell import shellOutput
from pymel.versions import shortName
from pymel.versions import installName
from pymel.util.shell import refreshEnviron
from pymel.mayautils import getUserPrefsDir
from collections import namedtuple
from pymel.util.common import subpackages

class PymelCache(object):
    def path(self):
        pass
    
    
    def read(self):
        pass
    
    
    def write(self, data):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    COMPRESSED = True
    
    
    DESC = ''
    
    
    NAME = ''
    
    
    USE_VERSION = True


class SubItemCache(PymelCache):
    """
    Used to store various maya information
    
    ie, api / cmd data parsed from docs
    
    To implement, create a subclass, which overrides at least the NAME, DESC,
    and _CACHE_NAMES attributes, and implements the rebuild method.
    
    Then to access data, you should initialize an instance, then call build;
    build will load the data from the cache file if possible, or call rebuild
    to build the data from scratch if not.  If the data had to be rebuilt,
    a new file cache will be saved.
    
    The data may then be accessed through attributes on the instance, with
    the names given in _CACHE_NAMES.
    
    >>> class NodeCache(SubItemCache):
    ...     NAME = 'mayaNodes'
    ...     DESC = 'the maya nodes cache'
    ...     COMPRESSED = False
    ...     _CACHE_NAMES = ['nodeTypes']
    ...     AUTO_SAVE = False
    ...     def rebuild(self):
    ...         import maya.cmds
    ...         self.nodeTypes = maya.cmds.allNodeTypes(includeAbstract=True)
    >>> cacheInst = NodeCache()
    >>> cacheInst.build()
    >>> 'polyCube' in cacheInst.nodeTypes
    True
    """
    
    
    
    def __init__(self):
        pass
    
    
    def build(self):
        """
        Used to rebuild cache, either by loading from a cache file, or rebuilding from scratch.
        """
    
        pass
    
    
    def cacheNames(self):
        pass
    
    
    def contents(self):
        """
        # was called 'caches'
        """
    
        pass
    
    
    def initVal(self, name):
        pass
    
    
    def itemType(self, name):
        pass
    
    
    def load(self):
        """
        Attempts to load the data from the cache on file.
        
        If it succeeds, it will update itself, and return the loaded items;
        if it fails, it will return None
        """
    
        pass
    
    
    def rebuild(self):
        """
        Rebuild cache from scratch
        
        Unlike 'build', this does not attempt to load a cache file, but always
        rebuilds it by parsing the docs, etc.
        """
    
        pass
    
    
    def save(self, obj=None):
        """
        Saves the cache
        
        Will optionally update the caches from the given object (which may be
        a dictionary, or an object with the caches stored in attributes on it)
        before saving
        """
    
        pass
    
    
    def update(self, obj, cacheNames=None):
        """
        Update all the various data from the given object, which should
        either be a dictionary, a list or tuple with the right number of items,
        or an object with the caches stored in attributes on it.
        """
    
        pass
    
    
    AUTO_SAVE = True
    
    
    DEFAULT_TYPE = None
    
    
    ITEM_TYPES = {}
    
    
    STORAGE_TYPES = {}



def initMEL():
    pass


def setupFormatting():
    pass


def mayaInit(forversion=None):
    """
    Try to init Maya standalone module, use when running pymel from an external Python inerpreter,
    it is possible to pass the desired Maya version number to define which Maya to initialize
    
    
    Part of the complexity of initializing maya in standalone mode is that maya does not populate os.environ when
    parsing Maya.env.  If we initialize normally, the env's are available via maya (via the shell), but not in python
    via os.environ.
    
    Note: the following example assumes that MAYA_SCRIPT_PATH is not set in your shell environment prior to launching
    python or mayapy.
    
    >>> import maya.standalone            #doctest: +SKIP
    >>> maya.standalone.initialize()      #doctest: +SKIP
    >>> import maya.mel as mm             #doctest: +SKIP
    >>> print mm.eval("getenv MAYA_SCRIPT_PATH")    #doctest: +SKIP
    /Network/Servers/sv-user.luma-pictures.com/luma .....
    >>> import os                         #doctest: +SKIP
    >>> 'MAYA_SCRIPT_PATH' in os.environ  #doctest: +SKIP
    False
    
    The solution lies in `refreshEnviron`, which copies the environment from the shell to os.environ after maya.standalone
    initializes.
    
    :rtype: bool
    :return: returns True if maya.cmds required initializing ( in other words, we are in a standalone python interpreter )
    """

    pass


def mayaStartupHasStarted():
    """
    Returns True if maya.app.startup has begun running, False otherwise.
    
    It's possible that maya.app.startup is in the process of running (ie,
    in maya.app.startup.basic, calling executeUserSetup) - unlike mayaStartup,
    this will attempt to detect if this is the case.
    """

    pass


def encodeFix():
    """
    # Fix for non US encodings in Maya
    """

    pass


def getConfigFile():
    pass


def parsePymelConfig():
    pass


def _load(filename):
    pass


def _dump(data, filename, protocol=-1):
    pass


def mayaStartupHasRun():
    """
    Returns True if maya.app.startup has already finished, False otherwise.
    """

    pass


def fixMayapy2011SegFault():
    """
    # Have all the checks inside here, in case people want to insert this in their
    # userSetup... it's currently not always on
    """

    pass


def finalize():
    pass


def _moduleJoin(*args):
    """
    Joins with the base pymel directory.
    :rtype: string
    """

    pass


def initAE():
    pass



pymel_options = {}

_finalizeCalled = True

isInitializing = False

_logger = None

with_statement = None


