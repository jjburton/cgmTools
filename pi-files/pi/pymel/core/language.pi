import exceptions

from getpass import getuser as _getuser

class MelCallable(object):
    """
    Class for wrapping up callables created by Mel class' procedure calls.
    
    The class is designed to support chained, "namespace-protected" MEL procedure
    calls, like: Foo.bar.spam(). In this case, Foo, bar and spam would each be MelCallable
    objects.
    """
    
    
    
    def __call__(self, *args, **kwargs):
        pass
    
    
    def __getattr__(self, command):
        pass
    
    
    def __init__(self, head, name):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class Mel(object):
    """
    Acts as a namespace from which MEL procedures can be called as if they
    were python functions.
    
    Automatically formats python arguments into a command string which is
    executed via ``maya.mel.eval``.  An instance of this class is created for
    you as `pymel.core.mel`.
    
    default:
        >>> import maya.mel as mel
        >>> # create the proc
        >>> mel.eval( 'global proc myScript( string $stringArg, float $floatArray[] ){}')
        >>> # run the script
        >>> mel.eval( 'myScript("firstArg", {1.0, 2.0, 3.0})')
    
    pymel:
        >>> from pymel.all import *
        >>> # create the proc
        >>> mel.eval( 'global proc myScript( string $stringArg, float $floatArray[] ){}')
        >>> # run the script
        >>> mel.myScript("firstArg", [1.0, 2.0, 3.0])
    
    The above is a very simplistic example. The advantages of pymel.mel over
    ``maya.mel.eval`` are more readily apparent when we want to pass a python
    object to our mel procedure:
    
    default:
        >>> import maya.cmds as cmds
        >>> node = "lambert1"
        >>> color = cmds.getAttr( node + ".color" )[0]
        >>> mel.eval('myScript("%s",{%f,%f,%f})' % (cmds.nodeType(node), color[0], color[1], color[2])   )
    
    pymel:
        >>> from pymel.all import *
        >>> node = PyNode("lambert1")
        >>> mel.myScript( node.type(), node.color.get() )
    
    In this you can see how `pymel.core.mel` allows you to pass any python
    object directly to your mel script as if it were a python function, with
    no need for formatting arguments.  The resulting code is much more readable.
    
    Another advantage of this class over maya.mel.eval is its handling of mel
    errors.  If a mel procedure fails to execute, you will get the specific mel
    error message in the python traceback, and, if they are enabled,
    line numbers!
    
    For example, in the example below we redeclare the myScript procedure with
    a line that will result in an error:
    
        >>> commandEcho(lineNumbers=1)  # turn line numbers on
        >>> mel.eval( '''
        ... global proc myScript( string $stringArg, float $floatArray[] ){
        ...     float $donuts = `ls -type camera`;}
        ... ''')
        >>> mel.myScript( 'foo', [] )
        Traceback (most recent call last):
            ...
        MelConversionError: Error during execution of MEL script: line 2: ,Cannot convert data of type string[] to type float.,
        Calling Procedure: myScript, in Mel procedure entered interactively.
          myScript("foo",{})
    
    Notice that the error raised is a `MelConversionError`.  There are several
    MEL exceptions that may be raised, depending on the type of error
    encountered: `MelError`, `MelConversionError`, `MelArgumentError`,
    `MelSyntaxError`, and `MelUnknownProcedureError`.
    
    Here's an example showing a `MelArgumentError`, which also demonstrates
    the additional traceback information that is provided for you, including
    the file of the calling script.
    
        >>> mel.startsWith('bar') # doctest: +ELLIPSIS
        Traceback (most recent call last):
          ...
        MelArgumentError: Error during execution of MEL script: Line 1.18: ,Wrong number of arguments on call to startsWith.,
        Calling Procedure: startsWith, in file "..."
          startsWith("bar")
    
    Lastly, an example of `MelUnknownProcedureError`
    
        >>> mel.poop()
        Traceback (most recent call last):
          ...
        MelUnknownProcedureError: Error during execution of MEL script: line 1: ,Cannot find procedure "poop".,
    
    Finally, some limitations: this Mel wrapper class cannot be used in
    situations in which the mel procedure modifies arguments (such as lists)
    in place, and you wish to then see the modified result in the calling code.
    Ie:
    
        >>> origList = []
        >>> newList = ["yet", "more", "things"]
        >>> mel.appendStringArray(origList, newList, 2)
        >>> origList
        []
    
    You will have to fall back to using mel.eval in such situations:
    
        >>> mel.eval('''
        ... string $origList[] = {};
        ... string $newList[] = {"yet", "more", "things"};
        ... appendStringArray($origList, $newList, 2);
        ... /* force a return value */
        ... $origList=$origList;
        ... ''')
        [u'yet', u'more']
    
    .. note::
    
        To remain backward compatible with maya.cmds, `MelError`, the base
        exception class that all these exceptions inherit from, in turn inherits
        from `RuntimeError`.
    """
    
    
    
    def __getattr__(self, command):
        return lambda *args: None
    
    
    def eval(cls, cmd):
        """
        evaluate a string as a mel command and return the result.
        
        Behaves like `maya.mel.eval`, with several improvements:
            - returns `pymel.datatype.Vector` and `pymel.datatype.Matrix`
              classes
            - when an error is encountered a `MelError` exception is raised,
              along with the line number (if enabled) and exact mel error.
        
        >>> mel.eval( 'attributeExists("persp", "translate")' )
        0
        >>> mel.eval( 'interToUI( "fooBarSpangle" )' )
        u'Foo Bar Spangle'
        """
    
        pass
    
    
    def mprint(cls, *args):
        """
        mel print command in case the python print command doesn't cut it
        """
    
        pass
    
    
    def source(cls, script, language='mel'):
        """
        use this to source mel or python scripts.
        
        :Parameters:
            language : {'mel', 'python'}
                When set to 'python', the source command will look for the
                python equivalent of this mel file, if it exists, and attempt
                to import it. This is particularly useful when transitioning
                from mel to python via `pymel.tools.mel2py`, with this simple
                switch you can change back and forth from sourcing mel to
                importing python.
        """
    
        pass
    
    
    def error(msg, showLineNumber=False):
        pass
    
    
    def tokenize(*args):
        pass
    
    
    def trace(msg, showLineNumber=False):
        pass
    
    
    def warning(msg, showLineNumber=False):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    globals = {}
    
    
    proc = None


class _Iterable(object):
    def __iter__(self):
        pass
    
    
    def __subclasshook__(cls, C):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    __abstractmethods__ = frozenset()


class _Container(object):
    def __contains__(self, x):
        pass
    
    
    def __subclasshook__(cls, C):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    __abstractmethods__ = frozenset()


class Env(object):
    """
    A Singleton class to represent Maya current optionVars and settings
    """
    
    
    
    def getAnimEndTime(self):
        pass
    
    
    def getAnimStartTime(self):
        pass
    
    
    def getConstructionHistory(self):
        pass
    
    
    def getMaxTime(self):
        pass
    
    
    def getMinTime(self):
        pass
    
    
    def getPlaybackTimes(self):
        pass
    
    
    def getTime(self):
        pass
    
    
    def getUpAxis(self):
        """
        This flag gets the axis set as the world up direction. The valid
        axis are either 'y' or 'z'.
        """
    
        pass
    
    
    def host(self):
        pass
    
    
    def sceneName(self):
        pass
    
    
    def setAnimEndTime(self, val):
        pass
    
    
    def setAnimStartTime(self, val):
        pass
    
    
    def setConstructionHistory(self, state):
        pass
    
    
    def setMaxTime(self, val):
        pass
    
    
    def setMinTime(self, val):
        pass
    
    
    def setPlaybackTimes(self, playbackTimes):
        pass
    
    
    def setTime(self, val):
        pass
    
    
    def setUpAxis(self, axis, rotateView=False):
        """
        This flag specifies the axis as the world up direction. The valid
        axis are either 'y' or 'z'.
        """
    
        pass
    
    
    def user(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    animEndTime = None
    
    animStartTime = None
    
    maxTime = None
    
    minTime = None
    
    playbackTimes = None
    
    time = None
    
    envVars = {}
    
    
    optionVars = {}


class OptionVarList(tuple):
    def __init__(self, val, key):
        pass
    
    
    def __setitem__(self, key, val):
        pass
    
    
    def append(self, val):
        """
        values appended to the OptionVarList with this method will be added
        to the Maya optionVar at the key denoted by self.key.
        """
    
        pass
    
    
    def appendVar(self, val):
        """
        values appended to the OptionVarList with this method will be added
        to the Maya optionVar at the key denoted by self.key.
        """
    
        pass
    
    
    def __new__(cls, val, key):
        pass
    
    
    __dict__ = None


class Catch(object):
    """
    Reproduces the behavior of the mel command of the same name. if writing
    pymel scripts from scratch, you should use the try/except structure. This
    command is provided for python scripts generated by py2mel.  stores the
    result of the function in catch.result.
    
    >>> if not catch( lambda: myFunc( "somearg" ) ):
    ...    result = catch.result
    ...    print "succeeded:", result
    """
    
    
    
    def __call__(self, func, *args, **kwargs):
        pass
    
    
    def reset(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    result = None
    
    
    success = None


class _Sized(object):
    def __len__(self):
        pass
    
    
    def __subclasshook__(cls, C):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    __abstractmethods__ = frozenset()


class MelError(exceptions.RuntimeError):
    """
    Generic MEL error
    """
    
    
    
    __weakref__ = None


class MelUnknownProcedureError(MelError, exceptions.NameError):
    """
    The called MEL procedure does not exist or has not been sourced
    """
    
    
    
    pass


class MelConversionError(MelError, exceptions.TypeError):
    """
    MEL cannot process a conversion or cast between data types
    """
    
    
    
    pass


class MelArgumentError(MelError, exceptions.TypeError):
    """
    The arguments passed to the MEL script are incorrect
    """
    
    
    
    pass


class MelSyntaxError(MelError, exceptions.SyntaxError):
    """
    The MEL script has a syntactical error
    """
    
    
    
    __weakref__ = None


class _Mapping(_Sized, _Iterable, _Container):
    """
    A Mapping is a generic container for associating key/value
    pairs.
    
    This class provides concrete generic implementations of all
    methods except for __getitem__, __iter__, and __len__.
    """
    
    
    
    def __contains__(self, key):
        pass
    
    
    def __eq__(self, other):
        pass
    
    
    def __getitem__(self, key):
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def get(self, key, default=None):
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
    
        pass
    
    
    def items(self):
        """
        D.items() -> list of D's (key, value) pairs, as 2-tuples
        """
    
        pass
    
    
    def iteritems(self):
        """
        D.iteritems() -> an iterator over the (key, value) items of D
        """
    
        pass
    
    
    def iterkeys(self):
        """
        D.iterkeys() -> an iterator over the keys of D
        """
    
        pass
    
    
    def itervalues(self):
        """
        D.itervalues() -> an iterator over the values of D
        """
    
        pass
    
    
    def keys(self):
        """
        D.keys() -> list of D's keys
        """
    
        pass
    
    
    def values(self):
        """
        D.values() -> list of D's values
        """
    
        pass
    
    
    __abstractmethods__ = frozenset()
    
    
    __hash__ = None


class _MutableMapping(_Mapping):
    """
    A MutableMapping is a generic container for associating
    key/value pairs.
    
    This class provides concrete generic implementations of all
    methods except for __getitem__, __setitem__, __delitem__,
    __iter__, and __len__.
    """
    
    
    
    def __delitem__(self, key):
        pass
    
    
    def __setitem__(self, key, value):
        pass
    
    
    def clear(self):
        """
        D.clear() -> None.  Remove all items from D.
        """
    
        pass
    
    
    def pop(self, key, default='<object object>'):
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised.
        """
    
        pass
    
    
    def popitem(self):
        """
        D.popitem() -> (k, v), remove and return some (key, value) pair
        as a 2-tuple; but raise KeyError if D is empty.
        """
    
        pass
    
    
    def setdefault(self, key, default=None):
        """
        D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
        """
    
        pass
    
    
    def update(*args, **kwds):
        """
        D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
        If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
        In either case, this is followed by: for k, v in F.items(): D[k] = v
        """
    
        pass
    
    
    __abstractmethods__ = frozenset()


class MelGlobals(_MutableMapping, dict):
    """
    A dictionary-like class for getting and setting global variables between mel and python.
    
    An instance of the class is created by default in the pymel namespace as ``melGlobals``.
    
    To retrieve existing global variables, just use the name as a key:
    
    >>> melGlobals['gResourceFileList'] #doctest: +ELLIPSIS
    [u'defaultRunTimeCommands.res.mel', u'localizedPanelLabel.res.mel', ...]
    >>> # works with or without $
    >>> melGlobals['gFilterUIDefaultAttributeFilterList']  #doctest: +ELLIPSIS
    [u'DefaultHiddenAttributesFilter', u'animCurveFilter', ..., u'publishedFilter']
    
    Creating new variables requires the use of the `initVar` function to specify the type:
    
    >>> melGlobals.initVar('string', 'gMyStrVar')
    '$gMyStrVar'
    >>> melGlobals['gMyStrVar'] = 'fooey'
    
    The variable will now be accessible within MEL as a global string.
    """
    
    
    
    def __getitem__(self, variable):
        pass
    
    
    def __iter__(self):
        pass
    
    
    def __len__(self):
        pass
    
    
    def __setitem__(self, variable, value):
        pass
    
    
    def get_dict(self, variable, default=None):
        pass
    
    
    def get(cls, variable, type=None):
        """
        get a MEL global variable.  If the type is not specified, the mel
        ``whatIs`` command will be used to determine it.
        """
    
        pass
    
    
    def getType(cls, variable):
        """
        Get the type of a global MEL variable
        """
    
        pass
    
    
    def initVar(cls, type, variable):
        """
        Initialize a new global MEL variable
        """
    
        pass
    
    
    def keys(cls):
        """
        list all global variables
        """
    
        pass
    
    
    def set(cls, variable, value, type=None):
        """
        set a mel global variable
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    MelGlobalArray = None
    
    
    VALID_TYPES = []
    
    
    __abstractmethods__ = frozenset()
    
    
    melTypeToPythonType = {}
    
    
    typeMap = {}


class OptionVarDict(_MutableMapping):
    """
    A dictionary-like class for accessing and modifying optionVars.
    
        >>> from pymel.all import *
        >>> optionVar['test'] = 'dooder'
        >>> optionVar['test']
        u'dooder'
    
        >>> if 'numbers' not in env.optionVars:
        ...     optionVar['numbers'] = [1,24,7]
        >>> optionVar['numbers'].appendVar( 9 )
        >>> numArray = optionVar.pop('numbers')
        >>> print numArray
        [1L, 24L, 7L, 9L]
        >>> optionVar.has_key('numbers') # previous pop removed the key
        False
    """
    
    
    
    def __call__(self, *args, **kwargs):
        pass
    
    
    def __contains__(self, key):
        """
        # use more efficient method provided by cmds.optionVar
        # (or at least, I hope it's more efficient...)
        """
    
        pass
    
    
    def __delitem__(self, key):
        pass
    
    
    def __getitem__(self, key):
        pass
    
    
    def __iter__(self):
        pass
    
    
    def __len__(self):
        pass
    
    
    def __setitem__(self, key, val):
        pass
    
    
    def has_key(self, key):
        """
        # not provided by MutableMapping
        """
    
        pass
    
    
    def iterkeys(self):
        pass
    
    
    def keys(self):
        pass
    
    
    def pop(self, key):
        pass
    
    
    __abstractmethods__ = frozenset()



def python(*args, **kwargs):
    """
    Derived from mel command `maya.cmds.python`
    """

    pass


def waitCursor(*args, **kwargs):
    """
    This command sets/resets a wait cursor for the entire Maya application. This works as a stack, such that for each
    waitCursor -state oncommand executed there should be a matching waitCursor -state offcommand pending. Warning:If a
    script fails that has turned the wait cursor on, the wait cursor may be left on. You need to turn it off manually from
    the command line by entering and executing the command 'waitCursor -state off'.
    
    Flags:
      - state : st                     (bool)          [create,query]
          Set or reset the wait cursor for the entire Maya application.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.waitCursor`
    """

    pass


def getMelType(pyObj, exactOnly=True, allowBool=False, allowMatrix=False):
    """
    return the name of the closest MEL type equivalent for the given python
    object.
    
    MEL has no true boolean or matrix types, but it often reserves special
    treatment for them in other ways.
    
    To control the handling of these types, use `allowBool` and `allowMatrix`.
    For python iterables, the first element in the array is used to determine
    the type. for empty lists, 'string[]' is returned.
    
        >>> from pymel.all import *
        >>> getMelType( 1 )
        'int'
        >>> p = SCENE.persp
        >>> getMelType( p.translate.get() )
        'vector'
        >>> getMelType( datatypes.Matrix )
        'int[]'
        >>> getMelType( datatypes.Matrix, allowMatrix=True )
        'matrix'
        >>> getMelType( True )
        'int'
        >>> getMelType( True, allowBool=True)
        'bool'
        >>> # make a dummy class
        >>> class MyClass(object): pass
        >>> getMelType( MyClass ) # returns None
        >>> getMelType( MyClass, exactOnly=False )
        'MyClass'
    
    :Parameters:
        pyObj
            can be either a class or an instance.
        exactOnly : bool
            If True and no suitable MEL analog can be found, the function will
            return None.
            If False, types which do not have an exact mel analog will return
            the python type name as a string
        allowBool : bool
            if True and a bool type is passed, 'bool' will be returned.
            otherwise 'int'.
        allowMatrix : bool
            if True and a `Matrix` type is passed, 'matrix' will be returned.
            otherwise 'int[]'.
    
    :rtype: `str`
    """

    pass


def sortCaseInsensitive(*args, **kwargs):
    """
    This command sorts all the strings of an array in a case insensitive way.
    
    
    Derived from mel command `maya.cmds.sortCaseInsensitive`
    """

    pass


def isValidMelType(typStr):
    """
    Returns whether ``typeStr`` is a valid MEL type identifier
    
    :rtype: bool
    """

    pass


def melOptions(*args, **kwargs):
    """
    Set and query options that affect the behavior of Maya's Embedded Language (MEL).                In query mode, return
    type is based on queried flag.
    
    Flags:
      - duplicateVariableWarnings : dvw (bool)          [create,query]
          When turned on, this option will cause a warning to be generated whenever a MEL variable is declared within the same
          scope as another variable with the same name. The warnings will be generated when the script is sourced, not when it is
          executed. Usually these warnings indicate an error in the script. On query the current setting of the option will be
          returned. The corresponding preference optionVar is melDuplicateVariableWarnings.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.melOptions`
    """

    pass


def getMelGlobal(type, variable):
    """
    # for backward compatibility
    """

    pass


def _flatten(iterables):
    pass


def stackTrace(*args, **kwargs):
    """
    Flags:
      - dump : d                       (bool)          []
    
      - parameterCount : pc            (int)           []
    
      - parameterType : pt             (int, int)      []
    
      - parameterValue : pv            (int, int)      []
    
      - state : s                      (bool)          []
    
    
    Derived from mel command `maya.cmds.stackTrace`
    """

    pass


def getLastError(*args, **kwargs):
    """
    Derived from mel command `maya.cmds.getLastError`
    """

    pass


def resourceManager(*args, **kwargs):
    """
    List resources matching certain properties.
    
    Flags:
      - nameFilter : nf                (unicode)       [create]
          List only resources matching the name. Argument may contain ? and \* characters.
    
      - saveAs : s                     (unicode, unicode) [create]
          Saves a copy of the resource (first parameter) as a separate file (second parameter).                              Flag
          can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.resourceManager`
    """

    pass


def scriptJob(*args, **kwargs):
    """
    This command creates a script job, which is a MEL command or script.  This job is attached to the named condition,
    event, or attribute. Each time the condition switches to the desired state (or the trigger is triggered, etc), the
    script is run. Script jobs are tied to the event loop in the interactive application. They are run during idle events.
    This means that script jobs do not exist in the batch application.  The scriptJob command does nothing in batch mode.
    This triggering happens very frequently so for speed considerations no events are forwarded during playback.  This means
    that you cannot use scriptJob -tc tcCallback;to alter animation behaviour. Use an expression instead, or the rendering
    callbacks preRenderMeland postRenderMel. When setting up jobs for conditions, it is invalid to setup jobs for the true
    state, false state, and state change at the same time.  The behaviour is undefined.  The user can only setup jobs for
    the true and/or false state, or only for the state change, but not three at the same time. i.e. if you do: // Set up a
    job that runs for the life of the application. // This job cannot be deleted with the killcommand no matter what.
    scriptJob -e SelectionChangedprint \Annoying Message!\\n\-permanent;// set up a job for the true state scriptJob -ct
    playingBackplayBackCallback;// set up a job for the false state scriptJob -cf playingBackplayBackCallback;then you
    should NOT do scriptJob -cc playingBackplayBackCallback;otherwise it will lead to undefined behaviour. This command can
    also be used to list available conditions and events, and to kill running jobs.
    
    Flags:
      - allChildren : alc              (bool)          [create]
          This flag can only be used in conjunction with the -ac/attributeChange flag.  If it is specified, and the job is
          attached to a compound attribute, then the job will run due to changes to the specified attribute as well as changes to
          its children.
    
      - attributeAdded : aa            (<type 'unicode'>, script) [create]
          Run the script when the named attribute is added. The string must identify both the dependency node and the particular
          attribute.  If the dependency node is deleted, this job is killed (even if the deletion is undoable).
    
      - attributeChange : ac           (<type 'unicode'>, script) [create]
          Run the script when the named attribute changes value. The string must identify both the dependency node and the
          particular attribute.  If the dependency node is deleted, this job is killed (even if the deletion is undoable).
    
      - attributeDeleted : ad          (<type 'unicode'>, script) [create]
          Run the script when the named attribute is deleted. The string must identify both the dependency node and the particular
          attribute.  If the dependency node is deleted, this job is killed (even if the deletion is undoable).
    
      - compressUndo : cu              (bool)          [create]
          If this is set to true, and the scriptJob is undoable, then its action will be bundled with the last user action for
          undo purposes.  For example; if the scriptJob was triggered by a selection change, then pressing undo will undo both the
          scriptJob and the selection change at the same time.
    
      - conditionChange : cc           (<type 'unicode'>, script) [create]
          Run the script when the named condition changes state. The string must be the name of a pre-defined, or a user-defined
          boolean condition.  To get a list of what conditions exist, use the -listConditions flag.
    
      - conditionFalse : cf            (<type 'unicode'>, script) [create]
          Run the script when the named condition becomes false. The string must be the name of a pre-defined, or a user-defined
          boolean condition.  To get a list of what conditions exist, use the -listConditions flag.
    
      - conditionTrue : ct             (<type 'unicode'>, script) [create]
          Run the script when the named condition becomes true. The string must be the name of a pre-defined, or a user-defined
          boolean condition.  To get a list of what conditions exist, use the -listConditions flag.
    
      - connectionChange : con         (<type 'unicode'>, script) [create]
          Run the script when the named attribute changes its connectivity.  The string must identify both the dependency node and
          the particular attribute.  If the dependency node is deleted, this job is killed (even if the deletion is undoable).
    
      - disregardIndex : dri           (bool)          [create]
          This flag can only be used in conjunction with the -ac/attributeChange flag.  If it is specified, and the job is
          attached to a multi (indexed) attribute, then the job will run no matter which attribute in the multi changes.
    
      - event : e                      (<type 'unicode'>, script) [create]
          Run the script when the named event occurs.  This string must be the name of a pre-defined maya event.  To get a list of
          what events exist, use the -listEvents flag.
    
      - exists : ex                    (int)           [create]
          Returns true if a scriptJob with the specified job numberexists, and false otherwise. The job numbershould be a value
          that was returned on creation of a new scriptJob.
    
      - force : f                      (bool)          [create]
          This flag can only be used with -kill, -killAll, or -replacePrevious. It enables the deletion of protected jobs.
    
      - idleEvent : ie                 (script)        [create]
          Run the script every time maya is idle.  WARNING, as long as an idle event is is registered, the application will keep
          calling it and will use up all available CPU time. Use idleEvents with caution.
    
      - kill : k                       (int)           [create]
          Kills the job with the specified job number. Permanent jobs cannot be killed, however, and protected jobs can only be
          killed if the -force flag is used in the command.
    
      - killAll : ka                   (bool)          [create]
          Kills all jobs. Permanent jobs will not be deleted, and protected jobs will only be deleted if the -force flag is used.
    
      - killWithScene : kws            (bool)          [create]
          Attaches the job to the current scene, and when the scene is emptied. The current scene is emptied by opening a new or
          existing scene.
    
      - listConditions : lc            (bool)          [create]
          This causes the command to return a string array containing the names of all existing conditions.  Below is the
          descriptions for all the existing conditions: Events Based on Available Maya FeaturesThese events are true when the
          given feature is available.Event NameMaya FeatureAnimationExistsAnimation AnimationUIExistsUser Interface for
          AnimationBaseMayaExistsAny Basic Maya BaseUIExistsAny Interactive MayaDatabaseUIExistsDeformersExistsDeformer Functions
          DeformersUIExistsUser Interface for DeformersDevicesExistsDevice
          SupportDimensionsExistsDimensioningDynamicsExistsDynamics DynamicsUIExistsUser Interface for
          DynamicsExplorerExistsExplorer ImageUIExistsUser Interface for ImagingKinematicsExistsKinematics KinematicsUIExistsUser
          Interface for KinematicsManipsExistsManipulatorsModelExistsBasic Modeling ToolsModelUIExistsUser Interface for Basic
          ModelingNurbsExistsNurbs Modeling ToolsNurbsUIExistsUser Interface for Nurbs ModelingPolyCoreExistsBasic Polygonal
          SupportPolygonsExistsPolygonal Modeling PolygonsUIExistsUser Interface for Polygonal ModelingPolyTextureExistsPolygonal
          Texturing RenderingExistsBuilt-in Rendering RenderingUIExistsUser Interface for RenderingOther
          EventsautoKeyframeState:true when Maya has autoKeyframing enabledbusy:true when Maya is busy.deleteAllCondition:true
          when in the middle of a delete-all operationflushingScene:true while the scene is being flushed outGoButtonEnabled:true
          when the Go button in the panel context is enabled. hotkeyListChange:true when the list of hotkey definitions has
          changedplayingBack:true when Maya is playing back animation keyframes.playbackIconsCondition:instance of the
          playingBackcondition used on the time sliderreadingFile:true when Maya is reading a file.RedoAvailable:true when there
          are commands available for redo. SomethingSelected:true when some object(s) is selected.UndoAvailable:true when there
          are commands available for undo.
    
      - listEvents : le                (bool)          [create]
          This causes the command to return a string array containing the names of all existing events.  Below is the descriptions
          for all the existing events:angularToleranceChanged:when the tolerance on angular units is changed. This tolerance can
          be changed by:using the MEL command, tolerancewith the -angularflagchanging the pref under Options-GeneralPreferences-
          Modeling tab-Tangential ToleranceangularUnitChanged:when the user changes the angular unit.axisAtOriginChanged:when the
          axis changes at the origin.axisInViewChanged:when the axis changes at a particular view.ColorIndexChanged:when the color
          index values change.constructionHistoryChanged: when construction history is turned on or off.currentContainerChanged:
          when the user set or unset the current container.currentSoundNodeChanged:whenever the sound displayed in the time slider
          changes due to:the sound being removed (or no longer displayed) [RMB in the time slider]a new sound being displayed [RMB
          in the time slider]sound display being toggled [animation options]sound display mode being changed [animation
          options]DagObjectCreated:when a new DAG object is created.deleteAll:when a file new occursDisplayColorChanged:when the
          display color changes.displayLayerChange:when a layer has been created or destroyed.displayLayerManagerChange:when the
          display layer manager has changed.DisplayRGBColorChanged:when the RGB display color changes.glFrameTrigger:for internal
          use only.ChannelBoxLabelSelected:when Channel Box label(first column) selection changes.gridDisplayChanged:for internal
          use only.idle: when Maya is idle and there are no high priority idle tasksidleHigh: when Maya is idle.  This is called
          before low priority idle tasks.  You should almost always use idleinstead.lightLinkingChanged:when any change occurs
          which modifies light linking relationships.lightLinkingChangedNonSG:when any change occurs which modifies light linking
          relationships, except when the change is a change of shading assignment.linearToleranceChanged:when the linear tolerance
          has been changed.  This tolerance can be changed by:using the MEL command, tolerancewith the  -linearflagchanging the
          pref under Options-GeneralPreferences-Modeling tab-Positional TolerancelinearUnitChanged: when the user changes the
          linear unit through the Options menu.MenuModeChanged: when the user changes the menu set for the menu bar in the main
          Maya window (for example, from Modelingto Animation).RecentCommandChanged: for internal use only.NewSceneOpened:when a
          new scene has been opened.PostSceneRead:after a scene has been read. Specifically after a file open, import or all child
          references have been read.nurbsToPolygonsPrefsChanged:when any of the nurbs-to-polygons prefs have changed.  These prefs
          can be changed by:using the Mel command, nurbsToPolygonsPrefchanging the prefs under Polygons-Nurbs To Polygons-Option
          BoxplaybackRangeChanged:when the playback keyframe range changes.playbackRangeSliderChanged:when the animation start/end
          range (i.e. the leftmost or rightmost entry cells in the time slider range, the inner ones adjust the playback range)
          changepreferredRendererChanged:when the preferred renderer changes.quitApplication:when the user has chosen to quit,
          either through the quit MEL command, or through the Exit menu item.Redo:when user has selected redo from the menu and
          there was something to redo.  This callback can be used for updating UI or local storage.  Do not change the state of
          the scene or DG during this callback.renderLayerChange:when creation or deletion of a render layer node has
          occured.renderLayerManagerChange:when the current render layer has changed.RebuildUIValues:for internal use
          only.SceneOpened:when a scene has been opened.SceneSaved:when a scene has been saved.SelectionChanged: when a new
          selection is made.SelectModeChanged: when the selection mode changes.SelectPreferenceChanged: for internal use
          only.SelectPriorityChanged:when the selection priority changes.SelectTypeChanged: when the selection type
          changes.setEditorChanged:obsolete.  No longer used.SetModified:when the set command is used to modify a
          setSequencerActiveShotChanged: when the active sequencer shot is changed.snapModeChanged:when the snap mode changes.
          E.g. changes to grid snapping. timeChanged:when the time changes.timeUnitChanged: when the user changes the time
          unit.ToolChanged: when the user changes the tool/context.PostToolChanged: after the user changes the
          tool/context.NameChanged: when the user changes the name of an object with the rename command.Undo:when user has
          selected undo from the menu and there was something to undo.  This callback can be used for updating UI or local
          storage.  Do not change the state of the scene or DG during this callback.modelEditorChanged: when the user changes the
          options of a model editor.colorMgtEnabledChanged: when the global per-scene color management enabled flag
          changes.colorMgtConfigFileEnableChanged: when the global per-scene color management OCIO configuration enabled flag
          changes.colorMgtPrefsViewTransformChanged: when the global per-scene color management view transform preferences
          transform changes.colorMgtWorkingSpaceChanged: when the global per-scene color management working space
          changes.colorMgtConfigFilePathChanged: when the global per-scene color management OCIO configuration file path
          changes.colorMgtConfigChanged: when the color management mode changes from native to OCIO, or when a different OCIO
          configuration is loaded.colorMgtPrefsReloaded: when all the global per-scene color management settings are
          reloaded.colorMgtUserPrefsChanged: when any user-level color management preference has changed.colorMgtOutputChanged:
          when the color management transform, or its enabled state, has changed.colorMgtOCIORulesChanged: when the type of rules
          in OCIO mode has changed.metadataVisualStatusChanged: for internal use only.shapeEditorTreeviewSelectionChanged: when a
          new selection in shape editor's treeview is made .
    
      - listJobs : lj                  (bool)          [create]
          This causes the command to return a string array containing a description of all existing jobs, along with their job
          numbers.  These numbers can be used to kill the jobs later.
    
      - nodeDeleted : nd               (<type 'unicode'>, script) [create]
          Run the script when the named node is deleted
    
      - nodeNameChanged : nnc          (<type 'unicode'>, script) [create]
          Run the script when the name of the named node changes
    
      - parent : p                     (unicode)       [create]
          Attaches this job to a piece of maya UI.  When the UI is destroyed, the job will be killed along with it.
    
      - permanent : per                (bool)          [create]
          Makes the job un-killable. Permanent jobs exist for the life of the application, or for the life of their parent object.
          The -killWithScene flag does apply to permanent jobs.
    
      - protected : pro                (bool)          [create]
          Makes the job harder to kill. Protected jobs must be killed or replaced intentionally by using the -force flag. The
          -killWithScene flag does apply to protected jobs.
    
      - replacePrevious : rp           (bool)          [create]
          This flag can only be used with the -parent flag.  Before the new scriptJob is created, any existing scriptJobs that
          have the same parent are first deleted.
    
      - runOnce : ro                   (bool)          [create]
          If this is set to true, the script will only be run a single time.  If false (the default) the script will run every
          time the triggering condition/event occurs.  If the -uid or -nd flags are used, runOnce is turned on automatically.
    
      - timeChange : tc                (script)        [create]
          Run the script whenever the current time changes. The script will not be executed if the time is changed by clicking on
          the time slider, whereas scripts triggered by the timeChangedcondition will be executed.
    
      - uiDeleted : uid                (<type 'unicode'>, script) [create]
          Run the script when the named piece of UI is deleted.                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.scriptJob`
    """

    pass


def pythonToMel(arg):
    """
    convert a python object to a string representing an equivalent value in mel
    
    iterables are flattened.
    
    mapping types like dictionaries have their key value pairs flattened:
        { key1 : val1, key2 : val2 }  -- >  ( key1, val1, key2, val2 )
    """

    pass


def evalEcho(*args, **kwargs):
    """
    Derived from mel command `maya.cmds.evalEcho`
    """

    pass


def pythonToMelCmd(*commandAndArgs, **kwargs):
    """
    Given a mel command name, and a set of python args / kwargs, return
    a mel string used to call the given command.
    
    Note that the first member of commandAndArgs is the command name, and is
    required; the remainder are the args to it.  We use this odd signature to
    avoid any name conflicts with mel flag names - ie, the signature used to be:
        pythonToMelCmd(command, *args, **kwargs)
    but this caused problems with the mel "button" function, which has a
    "command" flag.
    """

    pass


def getProcArguments(*args, **kwargs):
    """
    Derived from mel command `maya.cmds.getProcArguments`
    """

    pass


def conditionExists(conditionName):
    """
    Returns True if the named condition exists, False otherwise.
    
    Parameters
    ----------
    conditionName : str
        A type used by `isTrue` and `scriptJob` (*Not* a type used by the
        condition *node*).
    """

    pass


def evalNoSelectNotify(*args, **kwargs):
    """
    Derived from mel command `maya.cmds.evalNoSelectNotify`
    """

    pass


def callbacks(*args, **kwargs):
    """
    This command allows you to add callbacks at key times during UI creation so that the Maya UI can be extended. The list
    of standard Maya hooks, as well as the arguments which will be passed to the callback based on the context are
    enumerated in the describeHookssection below. Custom hooks can also be added if third parties want to add UI
    extensibility to their plugins.
    
    Flags:
      - addCallback : ac               (script)        [create]
          Add a callback for the specified hook. The owner must also be specified when adding callbacks.
    
      - clearAllCallbacks : cac        (bool)          [create]
          Clear all the callbacks for all hooks and owners. This is generally only used during plugin development and testing as
          it affects all callbacks registered by Maya and other third parties.
    
      - clearCallbacks : cc            (bool)          [create]
          Clear all the callbacks for the specified owner. If a hook is specified, only the callbacks for that hook and owner will
          be cleared.
    
      - describeHooks : dh             (bool)          [create]
          List the standard Maya hooks. Below is a list of the hooks and their associated arguments and return values. Custom
          hooks added by third parties are not listed. hyperShadePanelBuildCreateMenuThis hook is called to add content to the
          Hypershade panel create menu. It will be called after the standard Maya node entries have been created. This callback
          does not have any arguments or return values. In order to preserve the desired look in the Maya UI, these callbacks
          should add a menu item divider just before returning using: menuItem -divider true.
          hyperShadePanelBuildCreateSubMenuThis hook is called to get a classification string for the custom renderer shading
          nodes, to prevent them from being listed with the standard Maya nodes. This callback does not have any arguments.
          returns: a classification string, such as rendernode/myrendererhyperShadePanelPluginChangeThis hook is called when a
          plugin change event (loading / unloading) has occurred to inform Maya whether the Hypershade panel needs to be rebuilt.
          classification (string): classification string belonging to a plugin node,     possibly from another pluginchangeType
          (string): either loadPluginor unloadPluginreturns: (int) non-zero if your plugin is responsible for nodes of this
          classification,     and a Hypershade rebuild is requiredcreateRenderNodeSelectNodeCategoriesThis hook is called when the
          Create Render Node dialog is being constructed, and allows a third party to have their nodes selected by default. A flag
          of the form -allWithMyRendererUpis the standard form, and the selection can be set up in the tree lister in the
          callback. There is no return value for this callback. flag (string): flag passed to the Create Render Node dialog
          command with the leading minus (-) removedtreeLister (string): the tree lister widget which should be affectedFor
          example, your callback might look like: global proc myRendererCreateRenderNodeSelectNodeCategoriesCallback(string $flag,
          string $treeLister){     if($flag == allWithMyRendererUp) {         treeLister -e -selectPath myrenderer$treeLister;
          } } createRenderNodePluginChangeThis hook is called when a plugin change event has occurred to decide if the Create
          Render Node dialog needs to be closed. classification (string): classification string belonging to a plugin node,
          possibly from another pluginreturns: (int) non-zero if your plugin is responsible for nodes of this classification,
          and the Create Render Node dialog needs to be closedrenderNodeClassificationThis hook is called to get a classification
          string for the custom renderer shading nodes.  This is used to determine if a given node type belongs to a plugin
          renderer. This callback does not have any arguments. returns: a classification string, such as
          rendernode/myrenderercreateRenderNodeCommandThis hook is called to give plugin renderers the chance to register their
          own command for creating their nodes from the render node treeLister and Node Editor. The callback should determine from
          the classification of the node type in question if it is theirs, and if so, return the appropriate command for creating
          new nodes of that type. postCommand (string): command to be run after the create commandtype (string): nodeTypereturns:
          (string) MEL create commandbuildRenderNodeTreeListerContentThis hook is called to give plugin renderers the chance to
          add their content to the render node tree lister. renderNodeTreeLister (string): the render node tree listerpostCommand
          (string): command to be run post-creationfilterString (string): a space delimited list of
          filtersAETemplateCustomContentThis hook is called to give plugins a chance to add content to the Attribute Editor for
          nodes which source AEdependNodeTemplate. nodeName (string): the name of the node for which the Attribute Editor is being
          constructedfirstConnectedShaderThis hook is called to determine the primary custom shader connected to the given Shading
          Engine. nodeName (string): the name of the Shading Enginereturns (string): the name of the custom shader if
          applicableallConnectedShadersThis hook is called to determine all the shaders connected to the given Shading Engine.
          nodeName (string): the name of the Shading Enginereturns (string): a colon separated list of the connected custom
          shaders (shader1:shader2:shader3)renderLayerPresetMenuThis hook is called to give plugins a chance to add presets to a
          renderLayer node. nodeName (string): the name of the renderLayer nodeaddBakingMenuItemsThis hook is called to give
          plugins a chance to add baking menu items to the global Render - Lighting/Shading menu. menuItemAnchor (string): the
          name of the menuItem which the new baking menu items should be inserted after. addVertexBakingMenuItemsThis hook is
          called to give plugins a chance to add baking menu items to the global Polygon - Color menu. addPrelightMenuItemsThis
          hook is called to give plugins a chance to add pre-lighting menu items to the global Polygon - Color Set Editor menu.
          addRMBBakingMenuItemsThis hook is called to give plugins a chance to add baking menu items to the RMB menu. objectName
          (string): the name of the object the right mouse button event occured on.addMayaRenderingPreferencesThis hook is called
          to give plugins a chance to add custom preferences to the Maya's Rendering Preferences section.
          updateMayaRenderingPreferencesThis hook is called to give plugins a chance to update custom preferences of the Maya's
          Rendering Preferences section. addMayaMuscleMenuItemsThis hook is called to give plugins a chance to add menu items to
          the Maya muscle Displace menu. menuItemAnchor (string): the name of the menuItem which the new Maya muscle menu items
          should be inserted after. addMayaMuscleShelfButtonsThis hook is called to give plugins a chance to add items to the Maya
          muscle shelves. addBackburnerRendererMenuItemsThis hook is called to give plugins a chance to add items to Maya's
          Backburner list of available renderers. Note: The menuItem added must be named with the short name equivalent of the
          renderer. eg: The Maya software renderer adds a menuItem named 'sw'. provideAETemplateForNodeTypeThis hook is called to
          give plugins a chance to provide a UI template for nodes which do not have a corresponding AE'nodeType'Template
          procedure. nodeType (string): the type of the node for which the AE is being constructed. returns (string): the name of
          a MEL command or procedure to use as the AETemplate for the requested node type. AEnewMultiHandlerThis hook is called to
          give plugins a chance to provide a UI creation handler for multi attributes. nodeName (string): the name of the node for
          which the AE is being constructed. atributeName (string): the name of the multi attribute.uiName (string): the UI name
          of the attribute.changedCommand (string): the MEL command or procedure to be executed when the value of the multi
          attribute is changed.elementIndexString (string): a colon separated list of indices at which the elements of the multi
          attribute live.returns (string): if the callback handled the attribute then it should return the full name of the
          topmost UI element that it created, otherwise it should return an empty string.AEreplaceMultiHandlerThis hook is called
          to give plugins a chance to provide an update handler for multi attributes. layoutName (string): the well defined name
          of the Maya UI component which represents the multi attribute (.nodeName (string): the name of the node for which the AE
          is being constructed. atributeName (string): the name of the multi attribute.changedCommand (string): the MEL command or
          procedure to be executed when the value of the multi attribute is changed.elementIndexString (string): a colon separated
          list of indices at which the elements of the multi attribute live.returns (int): Return 1 if the callback handled the
          multi attribute, Return 0 if Maya should provide its default handling.AEnewAttributeHandlerThis hook is called to give
          plugins a chance to provide a UI creation handler for attributes. nodeName (string): the name of the node for which the
          AE is being constructed. atributeName (string): the name of the attribute.uiName (string): the UI name of the
          attribute.changedCommand (string): the MEL command or procedure to be executed when the value of the attribute is
          changed.returns (string): if the callback handled the attribute then it should return the full name of the topmost UI
          element that it created, otherwise it should return an empty string.AEreplaceAttributeHandlerThis hook is called to give
          plugins a chance to provide an update handler for attributes. nodeName (string): the name of the node for which the AE
          is being constructed. atributeName (string): the name of the attribute.changedCommand (string): the MEL command or
          procedure to be executed when the value of the attribute is changed.returns (int): Return 1 if the callback handled the
          attribute, Return 0 if Maya should provide its default handling.provideClassificationStringsThis hook must be supplied
          by all third parties that add nodes to the 'shader/surface' classification namespace. returns (string): a colon
          separated list representing the different plugin node classifications.provideClassificationExclusionStringsThis hook is
          called to give plugins a chance to provide a list of classifications which should be filtered out from a nodeTreeLister
          category. For example a plugin might want to filter out nodes classified as both 'material' and 'legacy' out of the
          'material' category. classification (string): the classification the nodeTreeBuilder is inquiring about.returns
          (string): a colon separated list representing the different classifications that should be excluded from the
          classification the nodeTreeBuilder is inquiring about.provideClassificationStringsForFilteredTreeListerThis hook is
          called by 'createAssignNewMaterialTreeLister' and gives plugins a chance to append to the classification filter passed
          to the Tree Lister builder. It must return a string where each new classification is separated by a white space.
          currentFilterString (string): a white-space-separated string representing the current
          classifications.nodeCanBeUsedAsMaterialThe hook is used by the RMB 'Assign Favorite Material' menu to determine which
          shading nodes can be used as materials. It must return 1 if the node can be used as a material node and 0 otherwise.
          nodeId (string): the node Id of the shading node being queried.nodeOwner (string): the name of the plugin the node
          belongs to.addHeaderContentToMayaLambertianShadersAEThis hook is called to give plugins a chance to add content to the
          header of the Attribute Editor of Maya's Lambertian-derived shaders. nodeName (string): the name of the node for which
          the Attribute Editor is being constructed.provideNodeToAttrConnectionThis hook is called to give plugins a chance to
          provide which output attribute should be used when a node is connected to an input attribute. If an input attribute type
          is given an output attribute of matching type should be returned. If no attribute type is specified (empty string) a
          preferred output attribute of any type can be returned. If no output attribute of matching type is available an empty
          string should be returned. nodeType (string): the node type of the node queried.attributeType (string): the data type of
          the input attribute.returns (string): the name of the output attribute to use.provideNodeToNodeConnectionThis hook is
          called to give plugins a chance to provide which attributes should be connected when a node to node connection is made.
          Both the source and destination attributes should be returned in a colon separated list, e.g.
          src1:dst1:src2:dst2:src3:dst3srcType (string): the node type of the source node.dstType (string): the node type of the
          destination node.returns (string): A colon separated list of source and destination attribute
          names.provideOutputAttributeNameForTextureNodeThis hook is called to give plugins a chance to provide a different output
          attribute name for Texture nodes. If this hook isn't provided 'outColor' is used. nodeName (string): the name of the
          texture node queried.returns (string): the output attribute name of the Texture
          node.addItemsToHypergraphNodePopupMenuThis hook is called to give plugins a chance to add items to the Hypergraph node
          popup menu. nodeName (string): the name of the node for which the Hypergraph node menu is being
          constructed.addItemsToRenderLayerEditorPopupMenuThis hook is called to give plugins a chance to add items to the Render
          Layer Editor popup menu. layerName (string): the name of the render layer for which the popup menu is being
          constructed.preventMaterialDeletionFromCleanUpSceneCommandThis hook is called by the cleanUpScene command and gives the
          plugin a chance to communicate that a material node is still in use and shouldn't be deleted. The hook is called once
          per plug/connection pair of each shader instance. shader (string): the name of the shader node being deleted.plug
          (string): the name of the plug queried.connection (string): the name of the connection
          queried.connectNodeToNodeOverrideCallbackThis hook is called to give plugins a chance to redefine the behavior of drag
          and drop. srcNode (string): the name of the source node (the dragged node).dstNode (string): the name of the destination
          node (the dropped-on node).returns (int): Return 1 if Maya should perform the operation that would normally result from
          this connection. Return 0 to override and provide custom behavior.prepareRenderChangedThis hook is called after an edit
          on a traversal set with the prepareRender command. enableRenderPassMenuOfRenderViewThis hook is called to give plugins a
          chance to tell Maya it should enable the render pass menu of the render view (under File-Load Render Pass).
          'addRenderPassMenuItemsToRenderView' can be used to add items to this menu. returns (int): Return 1 if the plugin wants
          the render pass menu of the render view to be enabled. Return 0 otherwise.addItemsToRenderPassMenuOfRenderViewThis hook
          is called to give plugins a chance to add menu items to the 'render pass' menu of the render view (under File-Load
          Render Pass). 'enableRenderPassMenuOfRenderView' can be used to enable the render pass menu of the render view.
          addItemsToRMBMenuOfTreeListerThis hook is called to give plugins a chance to populate the RMB menu of nodes listed in a
          tree lister. Plugins should add a menu item divider (using: menuItem -divider true) before adding any more items to the
          RMB menu. nodeType (string): The node type of the tree lister node for which the RMB menu is being built.scriptCommand
          (string): The script command associated with the tree lister node for which the RMB menu is being built.returns (int):
          Return 0 if Maya should append its own items to the menu of the current node type. This should be the return value for
          all node types a plugin isn't explicitly interested in. Return 1 if Maya shouldn't add any of its items to the menu of
          the current node type. Note: All menu items related to managing the 'Favorites' section of the tree lister will always
          be added to the RMB menu regardless of the return value (those are treated as special
          cases).saveCustomNodePresetAttributesThis hook is called to give plugins a chance to store extra commands in the node
          preset file being saved. presetNodeToSave (string): The name of the preset node being saved.returns (string): The custom
          procedure to use to generate the mel script to be appended to the nodePreset -custom flag of the current presetNode save
          event (see the documentation of the nodePreset command for more information on the format of the -custom
          flag).addItemToFileMenuThis hook is called to give plugins a chance to add menu items to the main File menu.
          addItemToCreateLightMenuThis hook is called to give plugins a chance to add menu items to the create light menu.
    
      - dumpCallbacks : dc             (bool)          [create]
          Gives a list of all the registered callbacks for all hooks and owners. Can be useful for debugging.
    
      - executeCallbacks : ec          (bool)          [create]
          Execute the callbacks for the specified hook, passing the extra arguments to each callback when it is executed.  Returns
          an array (MEL) or list (Python) containing the return values from each callback that was executed. If a callback returns
          no value, the array will contain an empty string (MEL) or None (Python).
    
      - hook : h                       (unicode)       [create]
          The name of the hook for which the callback should be registered.
    
      - listCallbacks : lc             (bool)          [create]
          Get the list of callbacks for the specified hook name. If the owner is specified, only callbacks for the specified hook
          and owner will be listed.
    
      - owner : o                      (unicode)       [create]
          The name of the owner registering the callback. This is typically a plugin name.
    
      - removeCallback : rc            (script)        [create]
          Remove an existing callback for the specified hook name. The owner must also be specified when removing a callback.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.callbacks`
    """

    pass


def setMelGlobal(type, variable, value):
    pass



melGlobals = MelGlobals()

mel = Mel()

MELTYPES = []

catch = Catch()

optionVar = OptionVarDict()

env = Env()


