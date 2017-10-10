import exceptions

class GhostObjsOkHere(object):
    def __enter__(self):
        pass
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
    
    def OK(cls):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class _GhostObjMaker(object):
    """
    Context used to get an mobject which we can query within this context.
    
    Automatically does any steps need to create and destroy the mobj within
    the context
    
    (Note - None may be returned in the place of any mobj)
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
    
    def __init__(self, mayaTypes, dagMod=None, dgMod=None, manipError=True, multi=False):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


from . import startup

class ApiMelBridgeCache(startup.SubItemCache):
    CACHE_TYPES = {}
    
    
    COMPRESSED = True
    
    
    DESC = 'the API-MEL bridge'
    
    
    NAME = 'mayaApiMelBridge'
    
    
    STORAGE_TYPES = {}
    
    
    USE_VERSION = False


class ApiCache(startup.SubItemCache):
    def __init__(self, docLocation=None):
        pass
    
    
    def addMayaType(self, mayaType, apiType=None, updateObj=None):
        """
        Add a type to the MayaTypes lists. Fill as many dictionary caches as we have info for.
        
            - mayaTypesToApiTypes
            - mayaTypesToApiEnums
        
        if updateObj is given, this instance will first be updated from it,
        before the mayaType is added.
        """
    
        pass
    
    
    def extraDicts(self):
        pass
    
    
    def melBridgeContents(self):
        pass
    
    
    def read(self, raw=False):
        pass
    
    
    def rebuild(self):
        """
        Rebuild the api cache from scratch
        
        Unlike 'build', this does not attempt to load a cache file, but always
        rebuilds it by parsing the docs, etc.
        """
    
        pass
    
    
    def removeMayaType(self, mayaType, updateObj=None):
        """
        Remove a type from the MayaTypes lists.
        
            - mayaTypesToApiTypes
            - mayaTypesToApiEnums
        
        if updateObj is given, this instance will first be updated from it,
        before the mayaType is added.
        """
    
        pass
    
    
    API_TO_MFN_OVERRIDES = {}
    
    
    COMPRESSED = True
    
    
    CRASH_TYPES = {}
    
    
    DEFAULT_API_TYPE = 'kDependencyNode'
    
    
    DESC = 'the API cache'
    
    
    EXTRA_GLOBAL_NAMES = ()
    
    
    MAYA_TO_API_OVERRIDES = {}
    
    
    NAME = 'mayaApi'
    
    
    USE_VERSION = True


class InvalidNodeTypeError(exceptions.Exception):
    __weakref__ = None


class ApiEnum(tuple):
    def __repr__(self):
        pass
    
    
    def __str__(self):
        pass
    
    
    def pymelName(self):
        pass
    
    
    __dict__ = None


class ManipNodeTypeError(InvalidNodeTypeError):
    pass



def _getRealMayaTypes(**kwargs):
    pass


def _getAbstractMayaTypes(**kwargs):
    pass


def getInheritance(mayaType, checkManip3D=True, checkCache=True, updateCache=True):
    """
    Get parents as a list, starting from the node after dependNode, and
    ending with the mayaType itself.
    
    Raises a ManipNodeTypeError if the node type fed in was a manipulator
    """

    pass


def _getAllMayaTypes(**kwargs):
    pass


def nodeToApiName(nodeName):
    pass


def getLowerCaseMapping(names):
    pass


def _makeDgModGhostObject(mayaType, dagMod, dgMod):
    pass


def isPluginNode(nodeName):
    """
    # if we have MNodeClass, this is easy...
    """

    pass


def _getMayaTypes(real=True, abstract=True, basePluginTypes=True, addAncestors=True, noManips=True, noPlugins=False, returnRealAbstract=False):
    """
    Returns a list of maya types
    
    Parameters
    ----------
    real : bool
        Include the set of real/createable nodes
    abstract : bool
        Include the set of abstract nodes (as defined by allNodeTypes(includeAbstract=True)
    basePluginTypes : bool
        Include the set of "base" plugin maya types (these are not returned by
        allNodeTypes(includeAbstract=True), and so, even though these types are
        abstract, this set shares no members with those added by the abstract
        flag
    addAncestors : bool
        If true, add to the list of nodes returned all of their ancestors as
        well
    noManips : bool
        If true, filter out any manipulator node types
    noPlugins : bool
        If true, filter out any nodes defined in plugins (note - if
        basePluginTypes is True, and noPlugins is False, the basePluginTypes
        will still be returned, as these types are not themselves defined in
        the plugin)
    returnRealAbstract : bool
        if True, will return two sets, realNodes and abstractNodes; otherwise,
        returns a single set of all the desired nodes (more precisely, realNodes
        is defined as the set of directly createdable nodes matching the
        criteria, and abstract are all non-createable nodes matching the
        criteria)
    """

    pass


def _defaultdictdict(cls, val=None):
    pass



NUCLEUS_MFNDAG_BUG = False

apiSuffixes = []

API_NAME_MODIFIERS = []

mpxNamesToApiEnumNames = {}

_ABSTRACT_SUFFIX = ' (abstract)'

replace = 'vertice'

_logger = None

find = 'vert(?!(ex|ice))'

_fixedLineages = {}

_ASSET_PREFIX = 'adskAssetInstanceNode_'

_cachedInheritances = {}


