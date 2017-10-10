import exceptions

from operator import itemgetter
from pymel.util.conditions import Condition

class ApiUndoItem(object):
    """
    A simple class that reprsents an undo item to be undone or redone.
    """
    
    
    
    def __init__(self, setter, redoArgs, undoArgs, redoKwargs=None, undoKwargs=None):
        pass
    
    
    def doIt(self):
        pass
    
    
    def redoIt(self):
        pass
    
    
    def undoIt(self):
        pass


class ApiArgUtil(object):
    def __init__(self, apiClassName, methodName, methodIndex=0):
        """
        If methodInfo is None, then the methodIndex will be used to lookup the methodInfo from apiClassInfo
        """
    
        pass
    
    
    def argInfo(self):
        pass
    
    
    def argList(self):
        pass
    
    
    def canBeWrapped(self):
        pass
    
    
    def castInput(self, argName, input, cls):
        pass
    
    
    def castReferenceResult(self, argtype, outArg):
        pass
    
    
    def castResult(self, instance, result):
        pass
    
    
    def fromInternalUnits(self, result, instance=None):
        pass
    
    
    def getDefaults(self):
        """
        get a list of defaults
        """
    
        pass
    
    
    def getGetterInfo(self):
        pass
    
    
    def getInputTypes(self):
        pass
    
    
    def getMethodDocs(self):
        pass
    
    
    def getOutputTypes(self):
        pass
    
    
    def getPrototype(self, className=True, methodName=True, outputs=False, defaults=False):
        pass
    
    
    def getPymelName(self):
        pass
    
    
    def getReturnType(self):
        pass
    
    
    def hasOutput(self):
        pass
    
    
    def inArgs(self):
        pass
    
    
    def initReference(self, argtype):
        pass
    
    
    def isDeprecated(self):
        pass
    
    
    def isStatic(self):
        pass
    
    
    def iterArgs(self, inputs=True, outputs=True, infoKeys=[]):
        pass
    
    
    def outArgs(self):
        pass
    
    
    def toInternalUnits(self, arg, input):
        pass
    
    
    def castInputEnum(cls, apiClassName, enumName, input):
        pass
    
    
    def isValidEnum(enumTuple):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class ApiUndo(object):
    """
    this is based on a clever prototype that Dean Edmonds posted on python_inside_maya
    awhile back.  it works like this:
    
        - using the API, create a garbage node with an integer attribute,
          lock it and set it not to save with the scene.
        - add an API callback to the node, so that when the special attribute
          is changed, we get a callback
        - the API queue is a list of simple python classes with undoIt and
          redoIt methods.  each time we add a new one to the queue, we increment
          the garbage node's integer attribute using maya.cmds.
        - when maya's undo or redo is called, it triggers the undoing or
          redoing of the garbage node's attribute change (bc we changed it using
          MEL/maya.cmds), which in turn triggers our API callback.  the callback
          runs the undoIt or redoIt method of the class at the index taken from
          the numeric attribute.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def append(self, cmdObj):
        pass
    
    
    def execute(self, cmdObj, *args):
        pass
    
    
    def flushCallback(self, undoOrRedoAvailable, *args):
        pass
    
    
    def flushUndo(self, *args):
        pass
    
    
    def installUndoStateCallbacks(self):
        pass
    
    
    def __new__(cls, *p, **k):
        """
        # redefine __new__
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class Flag(Condition):
    def __init__(self, longName, shortName, truthValue=True):
        """
        Conditional for evaluating if a given flag is present.
        
        Will also check that the given flag has the required
        truthValue (True, by default). If you don't care
        about the truthValue (ie, you want to have the condition
        evaluate to true as long as the flag is present),
        set truthValue to None.
        """
    
        pass
    
    
    def __str__(self):
        pass
    
    
    def eval(self, kwargs):
        pass


import pymel.util as util

class MetaMayaTypeWrapper(util.metaReadOnlyAttr):
    """
    A metaclass to wrap Maya api types, with support for class constants
    """
    
    
    
    def __new__(cls, classname, bases, classdict):
        """
        Create a new class of metaClassConstants type
        """
    
        pass
    
    
    ClassConstant = None


class ApiTypeRegister(object):
    """
    "
    Use this class to register the classes and functions used to wrap api methods.
    
    there are 4 dictionaries of functions maintained by this class:
        - inCast : for casting input arguments to a type that the api method expects
        - outCast: for casting the result of the api method to a type that pymel expects (outCast expect two args (self, obj) )
        - refInit: for initializing types passed by reference or via pointer
        - refCast: for casting the pointers to pymel types after they have been passed to the method
    
    To register a new type call `ApiTypeRegister.register`.
    """
    
    
    
    def getPymelType(cls, apiType):
        """
        We need a way to map from api name to pymelName.  we start by looking up types which are registered
        and then fall back to naming convention for types that haven't been registered yet. Perhaps pre-register
        the names?
        """
    
        pass
    
    
    def isRegistered(cls, apiTypeName):
        pass
    
    
    def register(cls, apiTypeName, pymelType, inCast=None, outCast=None, apiArrayItemType=None):
        """
        pymelType is the type to be used internally by pymel.  apiType will be hidden from the user
        and converted to the pymel type.
        apiTypeName is the name of an apiType as a string
        if apiArrayItemType is set, it should be the api type that represents each item in the array
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    arrayItemTypes = {}
    
    
    doc = {}
    
    
    inCast = {}
    
    
    outCast = {}
    
    
    refCast = {}
    
    
    refInit = {}
    
    
    types = {}


class Callback(object):
    """
    Enables deferred function evaluation with 'baked' arguments.
    Useful where lambdas won't work...
    
    It also ensures that the entire callback will be be represented by one
    undo entry.
    
    Example::
    
        import pymel as pm
        def addRigger(rigger, **kwargs):
            print "adding rigger", rigger
    
        for rigger in riggers:
            pm.menuItem(
                label = "Add " + str(rigger),
                c = Callback(addRigger,rigger,p=1))   # will run: addRigger(rigger,p=1)
    """
    
    
    
    def __call__(self, *args):
        pass
    
    
    def __init__(self, func, *args, **kwargs):
        pass
    
    
    def formatRecentError(cls, index=0):
        pass
    
    
    def logCallbackError(cls, callback, exception=None, trace=None, creationTrace=None):
        pass
    
    
    def printRecentError(cls, index=0):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    CallbackErrorLog = None
    
    
    MAX_RECENT_ERRORS = 10
    
    
    recentErrors = []


class VirtualClassError(exceptions.Exception):
    __weakref__ = None


class VirtualClassInfo(tuple):
    """
    VirtualClassInfo(vclass, parent, nameRequired, isVirtual, preCreate, create, postCreate)
    """
    
    
    
    def __getnewargs__(self):
        """
        Return self as a plain tuple.  Used by copy and pickle.
        """
    
        pass
    
    
    def __getstate__(self):
        """
        Exclude the OrderedDict from pickling
        """
    
        pass
    
    
    def __repr__(self):
        """
        Return a nicely formatted representation string
        """
    
        pass
    
    
    def __new__(_cls, vclass, parent, nameRequired, isVirtual, preCreate, create, postCreate):
        """
        Create new instance of VirtualClassInfo(vclass, parent, nameRequired, isVirtual, preCreate, create, postCreate)
        """
    
        pass
    
    
    __dict__ = None
    
    create = None
    
    isVirtual = None
    
    nameRequired = None
    
    parent = None
    
    postCreate = None
    
    preCreate = None
    
    vclass = None


class VirtualClassManager(object):
    def __init__(self):
        pass
    
    
    def getVirtualClass(self, baseClass, obj, name=None, fnDepend=None):
        """
        Returns the virtual class to use for the given baseClass + obj, or
        the original baseClass if no virtual class matches.
        """
    
        pass
    
    
    def getVirtualClassInfo(self, vclass):
        """
        Given a virtual class, returns it's registered VirtualClassInfo
        """
    
        pass
    
    
    def register(self, vclass, nameRequired=False, isVirtual='_isVirtual', preCreate='_preCreateVirtual', create='_createVirtual', postCreate='_postCreateVirtual'):
        """
        Register a new virtual class
        
        Allows a user to create their own subclasses of leaf PyMEL node classes,
        which are returned by `general.PyNode` and all other pymel commands.
        
        The process is fairly simple:
            1.  Subclass a PyNode class.  Be sure that it is a leaf class,
                meaning that it represents an actual Maya node type and not an
                abstract type higher up in the hierarchy.
            2.  Add an _isVirtual classmethod that accepts two arguments: an
                MObject/MDagPath instance for the current object, and its name.
                It should return True if the current object meets the
                requirements to become the virtual subclass, or else False.
            3.  Add optional _preCreate, _create, and _postCreate methods.  For
                more on these, see below
            4.  Register your subclass by calling
                factories.registerVirtualClass. If the _isVirtual callback
                requires the name of the object, set the keyword argument
                nameRequired to True. The object's name is not always
                immediately available and may take an extra calculation to
                retrieve, so if nameRequired is not set the name argument
                passed to your callback could be None.
        
        The creation of custom nodes may be customized with the use of
        isVirtual, preCreate, create, and postCreate functions; these are
        functions (or classmethods) which are called before / during / after
        creating the node.
        
        The isVirtual method is required - it is the callback used on instances
        of the base (ie, 'real') objects to determine whether they should be
        considered an instance of this virtual class. It's input is an MObject
        and an optional name (if nameRequired is set to True). It should return
        True to indicate that the given object is 'of this class', False
        otherwise. PyMEL code should not be used inside the callback, only API
        and maya.cmds. Keep in mind that once your new type is registered, its
        test will be run every time a node of its parent type is returned as a
        PyMEL node class, so be sure to keep your tests simple and fast.
        
        The preCreate function is called prior to node creation and gives you a
        chance to modify the kwargs dictionary; they are fed the kwargs fed to
        the creation command, and return either 1 or 2 dictionaries; the first
        dictionary is the one actually passed to the creation command; the
        second, if present, is passed to the postCreate command.
        
        The create method can be used to override the 'default' node creation
        command;  it is given the kwargs given on node creation (possibly
        altered by the preCreate), and must return the string name of the
        created node. (...or any another type of object (such as an MObject),
        as long as the postCreate and class.__init__ support it.)
        
        The postCreate function is called after creating the new node, and
        gives you a chance to modify it.  The method is passed the PyNode of
        the newly created node, as well as the second dictionary returned from
        the preCreate function as kwargs (if it was returned). You can use
        PyMEL code here, but you should avoid creating any new nodes.
        
        By default, any method named '_isVirtual', '_preCreateVirtual',
        '_createVirtual', or '_postCreateVirtual' on the class is used; if
        present, these must be classmethods or staticmethods.
        
        Other methods / functions may be used by passing a string or callable
        to the preCreate / postCreate kwargs.  If a string, then the method
        with that name on the class is used; it should be a classmethod or
        staticmethod present at the time it is registered.
        
        The value None may also be passed to any of these args (except isVirtual)
        to signal that no function is to be used for these purposes.
        
        If more than one subclass is registered for a node type, the registered
        callbacks will be run newest to oldest until one returns True. If no
        test returns True, then the standard node class is used. Also, for each
        base node type, if there is already a virtual class registered with the
        same name and module, then it is removed. (This helps alleviate
        registered callbacks from piling up if, for instance, a module is
        reloaded.)
        
        Overriding methods of PyMEL base classes should be performed with care,
        because certain methods are used internally and altering their results
        may cause PyMEL to error or behave unpredictably.  This is particularly
        true for special methods like __setattr__, __getattr__, __setstate__,
        __getstate__, etc.  Some methods are considered too dangerous to modify,
        and registration will fail if the user defines an override for them;
        this set includes __init__, __new__, and __str__.
        
        For a usage example, see examples/customClasses.py
        
        :parameters:
        nameRequired : `bool`
            True if the _isVirtual callback requires the string name to operate
            on. The object's name is not always immediately avaiable and may
            take an extra calculation to retrieve.
        isVirtual: `str` or callable
            the function to determine whether an MObject is an instance of this
            class; should take an MObject and name, returns True / or False
        preCreate: `str` or callable
            the function used to modify kwargs before being passed to the
            creation function
        create: `str` or callable
            function to use instead of the standard node creation method;
            takes whatever args are given to the cl
        postCreate: `str` or callable
            the function used to modify the PyNode after it is created.
        """
    
        pass
    
    
    def unregister(self, vcls):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    INVALID_ATTRS = set()


class MetaMayaComponentWrapper(MetaMayaTypeWrapper):
    """
    A metaclass for creating components.
    """
    
    
    
    def __new__(cls, classname, bases, classdict):
        pass


class ApiRedoUndoItem(ApiUndoItem):
    """
    Similar to the base ApiUndoItem, but allows specifying a separate
    function for the redoer and the undoer
    """
    
    
    
    def __init__(self, redoer, redoArgs, undoer, undoArgs, redoKwargs=None, undoKwargs=None):
        pass
    
    
    def undoIt(self):
        pass


class CallbackWithArgs(Callback):
    def __call__(self, *args, **kwargs):
        pass


class _MetaMayaCommandWrapper(MetaMayaTypeWrapper):
    """
    A metaclass for creating classes based on a maya command.
    
    Not intended to be used directly; instead, use the descendants: MetaMayaNodeWrapper, MetaMayaUIWrapper
    """
    
    
    
    def docstring(cls, melCmdName):
        pass
    
    
    def getMelCmd(cls, classdict):
        """
        Retrieves the name of the mel command the generated class wraps, and whether it is an info command.
        
        Intended to be overridden in derived metaclasses.
        """
    
        pass
    
    
    def isMelMethod(cls, methodName, parentClassList):
        """
        Deteremine if the passed method name exists on a parent class as a mel method
        """
    
        pass
    
    
    def __new__(cls, classname, bases, classdict):
        pass


class MetaMayaUIWrapper(_MetaMayaCommandWrapper):
    """
    A metaclass for creating classes based on on a maya UI type/command.
    """
    
    
    
    def getMelCmd(cls, classdict):
        pass
    
    
    def __new__(cls, classname, bases, classdict):
        pass


class MetaMayaNodeWrapper(_MetaMayaCommandWrapper):
    """
    A metaclass for creating classes based on node type.  Methods will be added to the new classes
    based on info parsed from the docs on their command counterparts.
    """
    
    
    
    def getMelCmd(cls, classdict):
        """
        Retrieves the name of the mel command for the node that the generated class wraps,
        and whether it is an info command.
        
        Derives the command name from the mel node name - so '__melnode__' must already be set
        in classdict.
        """
    
        pass
    
    
    def __new__(cls, classname, bases, classdict):
        pass



def removeMayaType(mayaType):
    """
    Remove a type from the MayaTypes lists.
    
    - mayaTypesToApiTypes
    - mayaTypesToApiEnums
    """

    pass


def clearPyNodeTypes():
    pass


def addApiDocs(apiClass, methodName, overloadIndex=None, undoable=True):
    """
    decorator for adding API docs
    """

    pass


def toApiTypeStr(obj, default=None):
    pass


def toApiFunctionSet(obj):
    pass


def addPyNode(dynModule, mayaType, parentMayaType, extraAttrs=None):
    """
    create a PyNode type for a maya node.
    """

    pass


def loadApiCache():
    pass


def unwrapToPyNode(res):
    """
    unwraps a 1-item list, and returns a PyNode object
    """

    pass


def createflag(cmdName, flag):
    """
    create flag decorator
    """

    pass


def addApiDocsCallback(apiClass, methodName, overloadIndex=None, undoable=True, origDocstring=''):
    pass


def removePyNode(dynModule, mayaType):
    pass


def makeEditFlagMethod(inFunc, flag, newMethodName=None, docstring='', cmdName=None):
    pass


def toPyUI(res):
    """
    returns a PyUI object
    """

    pass


def apiClassNameToPymelClassName(apiName, allowGuess=True):
    """
    Given the name of an api class, such as MFnTransform, MSpace, MAngle,
    returns the name of the corresponding pymel class.
    
    If allowGuessing, and we cannot find a registered type that matches, will
    try to do string parsing to guess the pymel name.
    
    Returns None if it was unable to determine the name.
    """

    pass


def getUncachedCmds():
    pass


def isValidPyNode(arg):
    pass


def _setApiCacheGlobals():
    pass


def removePyNodeType(pyNodeTypeName):
    pass


def toPyUIList(res):
    """
    returns a list of PyUI objects
    """

    pass


def toApiTypeEnum(obj, default=None):
    pass


def addPyNodeCallback(dynModule, mayaType, pyNodeTypeName, parentPyNodeTypeName, extraAttrs=None):
    pass


def addMayaType(mayaType, apiType=None):
    """
    Add a type to the MayaTypes lists. Fill as many dictionary caches as we have info for.
    
    - mayaTypesToApiTypes
    - mayaTypesToApiEnums
    """

    pass


def splitToPyNodeList(res):
    """
    converts a whitespace-separated string of names to a list of PyNode objects
    """

    pass


def wrapApiMethod(apiClass, methodName, newName=None, proxy=True, overloadIndex=None):
    """
    create a wrapped, user-friendly API method that works the way a python method should: no MScriptUtil and
    no special API classes required.  Inputs go in the front door, and outputs come out the back door.
    
    
    Regarding Undo
    --------------
    
    The API provides many methods which are pairs -- one sets a value
    while the other one gets the value.  the naming convention of these
    methods follows a fairly consistent pattern.  so what I did was
    determine all the get and set pairs, which I can use to automatically
    register api undo items:  prior to setting something, we first *get*
    it's existing value, which we can later use to reset when undo is
    triggered.
    
    This API undo is only for PyMEL methods which are derived from API
    methods.  it's not meant to be used with plugins.  and since it just
    piggybacks maya's MEL undo system, it won't get cross-mojonated.
    
    Take `MFnTransform.setTranslation`, for example. PyMEL provides a wrapped copy of this as
    `Transform.setTranslation`.   when pymel.Transform.setTranslation is
    called, here's what happens in relation to undo:
    
        #. process input args, if any
        #. call MFnTransform.getTranslation() to get the current translation.
        #. append to the api undo queue, with necessary info to undo/redo
           later (the current method, the current args, and the current
           translation)
        #. call MFnTransform.setTranslation() with the passed args
        #. process result and return it
    
    
    :Parameters:
    
        apiClass : class
            the api class
        methodName : string
            the name of the api method
        newName : string
            optionally provided if a name other than that of api method is desired
        proxy : bool
            If True, then __apimfn__ function used to retrieve the proxy class. If False,
            then we assume that the class being wrapped inherits from the underlying api class.
        overloadIndex : None or int
            which of the overloaded C++ signatures to use as the basis of our wrapped function.
    """

    pass


def addMelDocs(cmdName, flag=None):
    """
    decorator for adding docs
    """

    pass


def saveApiMelBridgeCache():
    pass


def addPyNodeType(pyNodeType, parentPyNode):
    pass


def makeQueryFlagMethod(inFunc, flag, newMethodName=None, docstring='', cmdName=None, returnFunc=None):
    pass


def mergeApiClassOverrides():
    pass


def functionFactory(funcNameOrObject, returnFunc=None, module=None, rename=None, uiWidget=False):
    """
    create a new function, apply the given returnFunc to the results (if any)
    Use pre-parsed command documentation to add to __doc__ strings for the
    command.
    """

    pass


def toPyTypeList(moduleName, objectName):
    """
    Returns a function which casts the members of it's iterable
    argument to the given class.
    """

    pass


def getComponentTypes():
    """
    # Keep around for debugging/info gathering...
    """

    pass


def loadCmdCache():
    pass


def _addCmdDocs(func, cmdName):
    pass


def isValidPyNodeName(arg):
    pass


def raiseError(typ, *args):
    pass


def isMayaType(mayaType):
    """
    Whether the given type is a currently-defined maya node name
    """

    pass


def queryflag(cmdName, flag):
    """
    query flag decorator
    """

    pass


def mayaTypeToApiType(mayaType):
    """
    Get the Maya API type from the name of a Maya type
    """

    pass


def toPyNode(res):
    """
    returns a PyNode object
    """

    pass


def listForNoneQuery(res, kwargs, flags):
    """
    convert a None to an empty list on the given query flags
    """

    pass


def editflag(cmdName, flag):
    """
    edit flag decorator
    """

    pass


def toPyType(moduleName, objectName):
    """
    Returns a function which casts it's single argument to
    an object with the given name in the given module (name).
    
    The module / object are given as strings, so that the module
    may be imported when the function is called, to avoid
    making factories dependent on, say, pymel.core.general or
    pymel.core.uitypes
    """

    pass


def makeCreateFlagMethod(inFunc, flag, newMethodName=None, docstring='', cmdName=None, returnFunc=None):
    pass


def fixCallbacks(inFunc, commandFlags, funcName=None):
    """
    Prior to maya 2011, when a user provides a custom callback functions for a
    UI elements, such as a checkBox, when the callback is triggered it is passed
    a string instead of a real python values.
    
    For example, a checkBox changeCommand returns the string 'true' instead of
    the python boolean True. This function wraps UI commands to correct the
    problem and also adds an extra flag to all commands with callbacks called
    'passSelf'.  When set to True, an instance of the calling UI class will be
    passed as the first argument.
    
    if inFunc has been renamed, pass a funcName to lookup command info in apicache.cmdlist
    """

    pass


def _setCmdCacheGlobals():
    pass


def saveApiCache():
    pass


def createFunctions(moduleName, returnFunc=None):
    pass


def addCmdDocsCallback(cmdName, docstring=''):
    pass


def _getTimeRangeFlags(cmdName):
    """
    used parsed data and naming convention to determine which flags are callbacks
    """

    pass


def _getApiOverrideNameAndData(classname, pymelName):
    pass


def loadCmdDocCache():
    pass


def toPyNodeList(res):
    """
    returns a list of PyNode objects
    """

    pass


def addCustomPyNode(dynModule, mayaType, extraAttrs=None):
    """
    create a PyNode, also adding each member in the given maya node's inheritance if it does not exist.
    
    This function is used for creating PyNodes via plugins, where the nodes parent's might be abstract
    types not yet created by pymel.  also, this function ensures that the newly created node types are
    added to pymel.all, if that module has been imported.
    """

    pass


def _addApiDocs(wrappedApiFunc, apiClass, methodName, overloadIndex=None, undoable=True):
    pass


def registerVirtualClass(self, vclass, nameRequired=False, isVirtual='_isVirtual', preCreate='_preCreateVirtual', create='_createVirtual', postCreate='_postCreateVirtual'):
    """
    Register a new virtual class
    
    Allows a user to create their own subclasses of leaf PyMEL node classes,
    which are returned by `general.PyNode` and all other pymel commands.
    
    The process is fairly simple:
        1.  Subclass a PyNode class.  Be sure that it is a leaf class,
            meaning that it represents an actual Maya node type and not an
            abstract type higher up in the hierarchy.
        2.  Add an _isVirtual classmethod that accepts two arguments: an
            MObject/MDagPath instance for the current object, and its name.
            It should return True if the current object meets the
            requirements to become the virtual subclass, or else False.
        3.  Add optional _preCreate, _create, and _postCreate methods.  For
            more on these, see below
        4.  Register your subclass by calling
            factories.registerVirtualClass. If the _isVirtual callback
            requires the name of the object, set the keyword argument
            nameRequired to True. The object's name is not always
            immediately available and may take an extra calculation to
            retrieve, so if nameRequired is not set the name argument
            passed to your callback could be None.
    
    The creation of custom nodes may be customized with the use of
    isVirtual, preCreate, create, and postCreate functions; these are
    functions (or classmethods) which are called before / during / after
    creating the node.
    
    The isVirtual method is required - it is the callback used on instances
    of the base (ie, 'real') objects to determine whether they should be
    considered an instance of this virtual class. It's input is an MObject
    and an optional name (if nameRequired is set to True). It should return
    True to indicate that the given object is 'of this class', False
    otherwise. PyMEL code should not be used inside the callback, only API
    and maya.cmds. Keep in mind that once your new type is registered, its
    test will be run every time a node of its parent type is returned as a
    PyMEL node class, so be sure to keep your tests simple and fast.
    
    The preCreate function is called prior to node creation and gives you a
    chance to modify the kwargs dictionary; they are fed the kwargs fed to
    the creation command, and return either 1 or 2 dictionaries; the first
    dictionary is the one actually passed to the creation command; the
    second, if present, is passed to the postCreate command.
    
    The create method can be used to override the 'default' node creation
    command;  it is given the kwargs given on node creation (possibly
    altered by the preCreate), and must return the string name of the
    created node. (...or any another type of object (such as an MObject),
    as long as the postCreate and class.__init__ support it.)
    
    The postCreate function is called after creating the new node, and
    gives you a chance to modify it.  The method is passed the PyNode of
    the newly created node, as well as the second dictionary returned from
    the preCreate function as kwargs (if it was returned). You can use
    PyMEL code here, but you should avoid creating any new nodes.
    
    By default, any method named '_isVirtual', '_preCreateVirtual',
    '_createVirtual', or '_postCreateVirtual' on the class is used; if
    present, these must be classmethods or staticmethods.
    
    Other methods / functions may be used by passing a string or callable
    to the preCreate / postCreate kwargs.  If a string, then the method
    with that name on the class is used; it should be a classmethod or
    staticmethod present at the time it is registered.
    
    The value None may also be passed to any of these args (except isVirtual)
    to signal that no function is to be used for these purposes.
    
    If more than one subclass is registered for a node type, the registered
    callbacks will be run newest to oldest until one returns True. If no
    test returns True, then the standard node class is used. Also, for each
    base node type, if there is already a virtual class registered with the
    same name and module, then it is removed. (This helps alleviate
    registered callbacks from piling up if, for instance, a module is
    reloaded.)
    
    Overriding methods of PyMEL base classes should be performed with care,
    because certain methods are used internally and altering their results
    may cause PyMEL to error or behave unpredictably.  This is particularly
    true for special methods like __setattr__, __getattr__, __setstate__,
    __getstate__, etc.  Some methods are considered too dangerous to modify,
    and registration will fail if the user defines an override for them;
    this set includes __init__, __new__, and __str__.
    
    For a usage example, see examples/customClasses.py
    
    :parameters:
    nameRequired : `bool`
        True if the _isVirtual callback requires the string name to operate
        on. The object's name is not always immediately avaiable and may
        take an extra calculation to retrieve.
    isVirtual: `str` or callable
        the function to determine whether an MObject is an instance of this
        class; should take an MObject and name, returns True / or False
    preCreate: `str` or callable
        the function used to modify kwargs before being passed to the
        creation function
    create: `str` or callable
        function to use instead of the standard node creation method;
        takes whatever args are given to the cl
    postCreate: `str` or callable
        the function used to modify the PyNode after it is created.
    """

    pass


def addFlagCmdDocsCallback(cmdName, flag, docstring):
    pass


def _addFlagCmdDocs(func, cmdName, flag, docstring=''):
    pass



virtualClasses = VirtualClassManager()

nodeHierarchy = []

apiEnumsToPyComponents = {}

apiTypesToApiClasses = {}

pyNodeNamesToPyNodes = {}

uiClassList = []

apiUndo = ApiUndo()

EXCLUDE_METHODS = []

_DEBUG_API_WRAPS = False

simpleCommandWraps = {}

mayaTypesToApiEnums = {}

_apiCacheInst = None

DOC_WIDTH = 120

classToMelMap = {}

overrideMethods = {}

pyNodeTypesHierarchy = {}

apiClassOverrides = {}

cmdlist = {}

_cmdCacheInst = None

apiToMelData = {}

apiClassNamesToPyNodeNames = {}

Always = None

moduleCmds = {}

_apiMelBridgeCacheInst = None

docCacheLoaded = True

apiTypesToApiEnums = {}

nodeTypeToInfoCommand = {}

_logger = None

apiClassInfo = {}

nodeCommandList = []

mayaTypesToApiTypes = {}

apiEnumsToApiTypes = {}


