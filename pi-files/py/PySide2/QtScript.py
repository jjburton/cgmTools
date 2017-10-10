from PySide2.QtCore import QObject as _QObject

class _Object(object):
    __dict__ = None


class QScriptClass(_Object):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def engine(*args, **kwargs):
        pass
    
    
    def extension(*args, **kwargs):
        pass
    
    
    def name(*args, **kwargs):
        pass
    
    
    def newIterator(*args, **kwargs):
        pass
    
    
    def property(*args, **kwargs):
        pass
    
    
    def propertyFlags(*args, **kwargs):
        pass
    
    
    def prototype(*args, **kwargs):
        pass
    
    
    def setProperty(*args, **kwargs):
        pass
    
    
    def supportsExtension(*args, **kwargs):
        pass
    
    
    Callable = None
    
    
    Extension = None
    
    
    HandlesReadAccess = None
    
    
    HandlesWriteAccess = None
    
    
    HasInstance = None
    
    
    QueryFlag = None
    
    
    __new__ = None


class QScriptContextInfo(_Object):
    def __copy__(*args, **kwargs):
        pass
    
    
    def __eq__(*args, **kwargs):
        """
        x.__eq__(y) <==> x==y
        """
    
        pass
    
    
    def __ge__(*args, **kwargs):
        """
        x.__ge__(y) <==> x>=y
        """
    
        pass
    
    
    def __gt__(*args, **kwargs):
        """
        x.__gt__(y) <==> x>y
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __le__(*args, **kwargs):
        """
        x.__le__(y) <==> x<=y
        """
    
        pass
    
    
    def __lshift__(*args, **kwargs):
        """
        x.__lshift__(y) <==> x<<y
        """
    
        pass
    
    
    def __lt__(*args, **kwargs):
        """
        x.__lt__(y) <==> x<y
        """
    
        pass
    
    
    def __ne__(*args, **kwargs):
        """
        x.__ne__(y) <==> x!=y
        """
    
        pass
    
    
    def __nonzero__(*args, **kwargs):
        """
        x.__nonzero__() <==> x != 0
        """
    
        pass
    
    
    def __rlshift__(*args, **kwargs):
        """
        x.__rlshift__(y) <==> y<<x
        """
    
        pass
    
    
    def __rrshift__(*args, **kwargs):
        """
        x.__rrshift__(y) <==> y>>x
        """
    
        pass
    
    
    def __rshift__(*args, **kwargs):
        """
        x.__rshift__(y) <==> x>>y
        """
    
        pass
    
    
    def columnNumber(*args, **kwargs):
        pass
    
    
    def fileName(*args, **kwargs):
        pass
    
    
    def functionEndLineNumber(*args, **kwargs):
        pass
    
    
    def functionMetaIndex(*args, **kwargs):
        pass
    
    
    def functionName(*args, **kwargs):
        pass
    
    
    def functionParameterNames(*args, **kwargs):
        pass
    
    
    def functionStartLineNumber(*args, **kwargs):
        pass
    
    
    def functionType(*args, **kwargs):
        pass
    
    
    def isNull(*args, **kwargs):
        pass
    
    
    def lineNumber(*args, **kwargs):
        pass
    
    
    def scriptId(*args, **kwargs):
        pass
    
    
    FunctionType = None
    
    
    NativeFunction = None
    
    
    QtFunction = None
    
    
    QtPropertyFunction = None
    
    
    ScriptFunction = None
    
    
    __new__ = None


class QScriptValueIterator(_Object):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __iter__(*args, **kwargs):
        """
        x.__iter__() <==> iter(x)
        """
    
        pass
    
    
    def flags(*args, **kwargs):
        pass
    
    
    def hasNext(*args, **kwargs):
        pass
    
    
    def hasPrevious(*args, **kwargs):
        pass
    
    
    def name(*args, **kwargs):
        pass
    
    
    def next(*args, **kwargs):
        """
        x.next() -> the next value, or raise StopIteration
        """
    
        pass
    
    
    def previous(*args, **kwargs):
        pass
    
    
    def remove(*args, **kwargs):
        pass
    
    
    def scriptName(*args, **kwargs):
        pass
    
    
    def setValue(*args, **kwargs):
        pass
    
    
    def toBack(*args, **kwargs):
        pass
    
    
    def toFront(*args, **kwargs):
        pass
    
    
    def value(*args, **kwargs):
        pass
    
    
    __new__ = None


class QScriptable(_Object):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def argument(*args, **kwargs):
        pass
    
    
    def argumentCount(*args, **kwargs):
        pass
    
    
    def context(*args, **kwargs):
        pass
    
    
    def engine(*args, **kwargs):
        pass
    
    
    def thisObject(*args, **kwargs):
        pass
    
    
    __new__ = None


class QScriptEngine(_QObject):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def abortEvaluation(*args, **kwargs):
        pass
    
    
    def agent(*args, **kwargs):
        pass
    
    
    def availableExtensions(*args, **kwargs):
        pass
    
    
    def canEvaluate(*args, **kwargs):
        pass
    
    
    def clearExceptions(*args, **kwargs):
        pass
    
    
    def collectGarbage(*args, **kwargs):
        pass
    
    
    def currentContext(*args, **kwargs):
        pass
    
    
    def defaultPrototype(*args, **kwargs):
        pass
    
    
    def evaluate(*args, **kwargs):
        pass
    
    
    def globalObject(*args, **kwargs):
        pass
    
    
    def hasUncaughtException(*args, **kwargs):
        pass
    
    
    def importExtension(*args, **kwargs):
        pass
    
    
    def importedExtensions(*args, **kwargs):
        pass
    
    
    def installTranslatorFunctions(*args, **kwargs):
        pass
    
    
    def isEvaluating(*args, **kwargs):
        pass
    
    
    def newActivationObject(*args, **kwargs):
        pass
    
    
    def newArray(*args, **kwargs):
        pass
    
    
    def newDate(*args, **kwargs):
        pass
    
    
    def newObject(*args, **kwargs):
        pass
    
    
    def newQMetaObject(*args, **kwargs):
        pass
    
    
    def newQObject(*args, **kwargs):
        pass
    
    
    def newRegExp(*args, **kwargs):
        pass
    
    
    def newVariant(*args, **kwargs):
        pass
    
    
    def nullValue(*args, **kwargs):
        pass
    
    
    def objectById(*args, **kwargs):
        pass
    
    
    def popContext(*args, **kwargs):
        pass
    
    
    def processEventsInterval(*args, **kwargs):
        pass
    
    
    def pushContext(*args, **kwargs):
        pass
    
    
    def reportAdditionalMemoryCost(*args, **kwargs):
        pass
    
    
    def setAgent(*args, **kwargs):
        pass
    
    
    def setDefaultPrototype(*args, **kwargs):
        pass
    
    
    def setGlobalObject(*args, **kwargs):
        pass
    
    
    def setProcessEventsInterval(*args, **kwargs):
        pass
    
    
    def toObject(*args, **kwargs):
        pass
    
    
    def toStringHandle(*args, **kwargs):
        pass
    
    
    def uncaughtException(*args, **kwargs):
        pass
    
    
    def uncaughtExceptionBacktrace(*args, **kwargs):
        pass
    
    
    def uncaughtExceptionLineNumber(*args, **kwargs):
        pass
    
    
    def undefinedValue(*args, **kwargs):
        pass
    
    
    AutoCreateDynamicProperties = None
    
    
    AutoOwnership = None
    
    
    ExcludeChildObjects = None
    
    
    ExcludeDeleteLater = None
    
    
    ExcludeSlots = None
    
    
    ExcludeSuperClassContents = None
    
    
    ExcludeSuperClassMethods = None
    
    
    ExcludeSuperClassProperties = None
    
    
    PreferExistingWrapperObject = None
    
    
    QObjectWrapOption = None
    
    
    QObjectWrapOptions = None
    
    
    QtOwnership = None
    
    
    ScriptOwnership = None
    
    
    SkipMethodsInEnumeration = None
    
    
    ValueOwnership = None
    
    
    __new__ = None
    
    
    signalHandlerException = None
    
    
    staticMetaObject = None


class QScriptClassPropertyIterator(_Object):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def flags(*args, **kwargs):
        pass
    
    
    def hasNext(*args, **kwargs):
        pass
    
    
    def hasPrevious(*args, **kwargs):
        pass
    
    
    def id(*args, **kwargs):
        pass
    
    
    def name(*args, **kwargs):
        pass
    
    
    def next(*args, **kwargs):
        pass
    
    
    def object(*args, **kwargs):
        pass
    
    
    def previous(*args, **kwargs):
        pass
    
    
    def toBack(*args, **kwargs):
        pass
    
    
    def toFront(*args, **kwargs):
        pass
    
    
    __new__ = None


class QScriptString(_Object):
    def __copy__(*args, **kwargs):
        pass
    
    
    def __eq__(*args, **kwargs):
        """
        x.__eq__(y) <==> x==y
        """
    
        pass
    
    
    def __ge__(*args, **kwargs):
        """
        x.__ge__(y) <==> x>=y
        """
    
        pass
    
    
    def __gt__(*args, **kwargs):
        """
        x.__gt__(y) <==> x>y
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __le__(*args, **kwargs):
        """
        x.__le__(y) <==> x<=y
        """
    
        pass
    
    
    def __lt__(*args, **kwargs):
        """
        x.__lt__(y) <==> x<y
        """
    
        pass
    
    
    def __ne__(*args, **kwargs):
        """
        x.__ne__(y) <==> x!=y
        """
    
        pass
    
    
    def isValid(*args, **kwargs):
        pass
    
    
    def toArrayIndex(*args, **kwargs):
        pass
    
    
    def toString(*args, **kwargs):
        pass
    
    
    __new__ = None


class QScriptContext(_Object):
    def activationObject(*args, **kwargs):
        pass
    
    
    def argument(*args, **kwargs):
        pass
    
    
    def argumentCount(*args, **kwargs):
        pass
    
    
    def argumentsObject(*args, **kwargs):
        pass
    
    
    def backtrace(*args, **kwargs):
        pass
    
    
    def callee(*args, **kwargs):
        pass
    
    
    def engine(*args, **kwargs):
        pass
    
    
    def isCalledAsConstructor(*args, **kwargs):
        pass
    
    
    def parentContext(*args, **kwargs):
        pass
    
    
    def popScope(*args, **kwargs):
        pass
    
    
    def pushScope(*args, **kwargs):
        pass
    
    
    def returnValue(*args, **kwargs):
        pass
    
    
    def scopeChain(*args, **kwargs):
        pass
    
    
    def setActivationObject(*args, **kwargs):
        pass
    
    
    def setReturnValue(*args, **kwargs):
        pass
    
    
    def setThisObject(*args, **kwargs):
        pass
    
    
    def state(*args, **kwargs):
        pass
    
    
    def thisObject(*args, **kwargs):
        pass
    
    
    def throwError(*args, **kwargs):
        pass
    
    
    def throwValue(*args, **kwargs):
        pass
    
    
    def toString(*args, **kwargs):
        pass
    
    
    Error = None
    
    
    ExceptionState = None
    
    
    ExecutionState = None
    
    
    NormalState = None
    
    
    RangeError = None
    
    
    ReferenceError = None
    
    
    SyntaxError = None
    
    
    TypeError = None
    
    
    URIError = None
    
    
    UnknownError = None


class QScriptEngineAgent(_Object):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def contextPop(*args, **kwargs):
        pass
    
    
    def contextPush(*args, **kwargs):
        pass
    
    
    def engine(*args, **kwargs):
        pass
    
    
    def exceptionCatch(*args, **kwargs):
        pass
    
    
    def exceptionThrow(*args, **kwargs):
        pass
    
    
    def extension(*args, **kwargs):
        pass
    
    
    def functionEntry(*args, **kwargs):
        pass
    
    
    def functionExit(*args, **kwargs):
        pass
    
    
    def positionChange(*args, **kwargs):
        pass
    
    
    def scriptLoad(*args, **kwargs):
        pass
    
    
    def scriptUnload(*args, **kwargs):
        pass
    
    
    def supportsExtension(*args, **kwargs):
        pass
    
    
    DebuggerInvocationRequest = None
    
    
    Extension = None
    
    
    __new__ = None


from . import QtCore as _QtCore

class QScriptExtensionInterface(_QtCore.QFactoryInterface):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def initialize(*args, **kwargs):
        pass
    
    
    __new__ = None


class QScriptProgram(_Object):
    def __copy__(*args, **kwargs):
        pass
    
    
    def __eq__(*args, **kwargs):
        """
        x.__eq__(y) <==> x==y
        """
    
        pass
    
    
    def __ge__(*args, **kwargs):
        """
        x.__ge__(y) <==> x>=y
        """
    
        pass
    
    
    def __gt__(*args, **kwargs):
        """
        x.__gt__(y) <==> x>y
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __le__(*args, **kwargs):
        """
        x.__le__(y) <==> x<=y
        """
    
        pass
    
    
    def __lt__(*args, **kwargs):
        """
        x.__lt__(y) <==> x<y
        """
    
        pass
    
    
    def __ne__(*args, **kwargs):
        """
        x.__ne__(y) <==> x!=y
        """
    
        pass
    
    
    def __nonzero__(*args, **kwargs):
        """
        x.__nonzero__() <==> x != 0
        """
    
        pass
    
    
    def fileName(*args, **kwargs):
        pass
    
    
    def firstLineNumber(*args, **kwargs):
        pass
    
    
    def isNull(*args, **kwargs):
        pass
    
    
    def sourceCode(*args, **kwargs):
        pass
    
    
    __new__ = None


class QScriptValue(_Object):
    def __copy__(*args, **kwargs):
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
    
    
    def __iter__(*args, **kwargs):
        """
        x.__iter__() <==> iter(x)
        """
    
        pass
    
    
    def __nonzero__(*args, **kwargs):
        """
        x.__nonzero__() <==> x != 0
        """
    
        pass
    
    
    def __repr__(*args, **kwargs):
        """
        x.__repr__() <==> repr(x)
        """
    
        pass
    
    
    def call(*args, **kwargs):
        pass
    
    
    def construct(*args, **kwargs):
        pass
    
    
    def data(*args, **kwargs):
        pass
    
    
    def engine(*args, **kwargs):
        pass
    
    
    def equals(*args, **kwargs):
        pass
    
    
    def instanceOf(*args, **kwargs):
        pass
    
    
    def isArray(*args, **kwargs):
        pass
    
    
    def isBool(*args, **kwargs):
        pass
    
    
    def isBoolean(*args, **kwargs):
        pass
    
    
    def isDate(*args, **kwargs):
        pass
    
    
    def isError(*args, **kwargs):
        pass
    
    
    def isFunction(*args, **kwargs):
        pass
    
    
    def isNull(*args, **kwargs):
        pass
    
    
    def isNumber(*args, **kwargs):
        pass
    
    
    def isObject(*args, **kwargs):
        pass
    
    
    def isQMetaObject(*args, **kwargs):
        pass
    
    
    def isQObject(*args, **kwargs):
        pass
    
    
    def isRegExp(*args, **kwargs):
        pass
    
    
    def isString(*args, **kwargs):
        pass
    
    
    def isUndefined(*args, **kwargs):
        pass
    
    
    def isValid(*args, **kwargs):
        pass
    
    
    def isVariant(*args, **kwargs):
        pass
    
    
    def lessThan(*args, **kwargs):
        pass
    
    
    def objectId(*args, **kwargs):
        pass
    
    
    def property(*args, **kwargs):
        pass
    
    
    def propertyFlags(*args, **kwargs):
        pass
    
    
    def prototype(*args, **kwargs):
        pass
    
    
    def scope(*args, **kwargs):
        pass
    
    
    def scriptClass(*args, **kwargs):
        pass
    
    
    def setData(*args, **kwargs):
        pass
    
    
    def setProperty(*args, **kwargs):
        pass
    
    
    def setPrototype(*args, **kwargs):
        pass
    
    
    def setScope(*args, **kwargs):
        pass
    
    
    def setScriptClass(*args, **kwargs):
        pass
    
    
    def strictlyEquals(*args, **kwargs):
        pass
    
    
    def toBool(*args, **kwargs):
        pass
    
    
    def toBoolean(*args, **kwargs):
        pass
    
    
    def toDateTime(*args, **kwargs):
        pass
    
    
    def toInt32(*args, **kwargs):
        pass
    
    
    def toInteger(*args, **kwargs):
        pass
    
    
    def toNumber(*args, **kwargs):
        pass
    
    
    def toObject(*args, **kwargs):
        pass
    
    
    def toQMetaObject(*args, **kwargs):
        pass
    
    
    def toQObject(*args, **kwargs):
        pass
    
    
    def toRegExp(*args, **kwargs):
        pass
    
    
    def toString(*args, **kwargs):
        pass
    
    
    def toUInt16(*args, **kwargs):
        pass
    
    
    def toUInt32(*args, **kwargs):
        pass
    
    
    def toVariant(*args, **kwargs):
        pass
    
    
    KeepExistingFlags = None
    
    
    NullValue = None
    
    
    PropertyFlag = None
    
    
    PropertyFlags = None
    
    
    PropertyGetter = None
    
    
    PropertySetter = None
    
    
    QObjectMember = None
    
    
    ReadOnly = None
    
    
    ResolveFlag = None
    
    
    ResolveFlags = None
    
    
    ResolveFull = None
    
    
    ResolveLocal = None
    
    
    ResolvePrototype = None
    
    
    ResolveScope = None
    
    
    SkipInEnumeration = None
    
    
    SpecialValue = None
    
    
    UndefinedValue = None
    
    
    Undeletable = None
    
    
    UserRange = None
    
    
    __new__ = None


class QScriptExtensionPlugin(_QObject, QScriptExtensionInterface):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def initialize(*args, **kwargs):
        pass
    
    
    def keys(*args, **kwargs):
        pass
    
    
    def setupPackage(*args, **kwargs):
        pass
    
    
    __new__ = None
    
    
    staticMetaObject = None



