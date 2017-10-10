from PySide2.QtCore import QObject as _QObject

class _Object(object):
    __dict__ = None


class QXmlSchema(_Object):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def documentUri(*args, **kwargs):
        pass
    
    
    def isValid(*args, **kwargs):
        pass
    
    
    def load(*args, **kwargs):
        pass
    
    
    def messageHandler(*args, **kwargs):
        pass
    
    
    def namePool(*args, **kwargs):
        pass
    
    
    def setMessageHandler(*args, **kwargs):
        pass
    
    
    def setUriResolver(*args, **kwargs):
        pass
    
    
    def uriResolver(*args, **kwargs):
        pass
    
    
    __new__ = None


class QAbstractMessageHandler(_QObject):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def handleMessage(*args, **kwargs):
        pass
    
    
    def message(*args, **kwargs):
        pass
    
    
    __new__ = None
    
    
    staticMetaObject = None


class QXmlItem(_Object):
    def __copy__(*args, **kwargs):
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __nonzero__(*args, **kwargs):
        """
        x.__nonzero__() <==> x != 0
        """
    
        pass
    
    
    def isAtomicValue(*args, **kwargs):
        pass
    
    
    def isNode(*args, **kwargs):
        pass
    
    
    def isNull(*args, **kwargs):
        pass
    
    
    def toAtomicValue(*args, **kwargs):
        pass
    
    
    def toNodeModelIndex(*args, **kwargs):
        pass
    
    
    __new__ = None


class QXmlNamePool(_Object):
    def __copy__(*args, **kwargs):
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    __new__ = None


class QAbstractXmlNodeModel(_Object):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def attributes(*args, **kwargs):
        pass
    
    
    def baseUri(*args, **kwargs):
        pass
    
    
    def compareOrder(*args, **kwargs):
        pass
    
    
    def createIndex(*args, **kwargs):
        pass
    
    
    def documentUri(*args, **kwargs):
        pass
    
    
    def elementById(*args, **kwargs):
        pass
    
    
    def isDeepEqual(*args, **kwargs):
        pass
    
    
    def kind(*args, **kwargs):
        pass
    
    
    def name(*args, **kwargs):
        pass
    
    
    def namespaceBindings(*args, **kwargs):
        pass
    
    
    def namespaceForPrefix(*args, **kwargs):
        pass
    
    
    def nextFromSimpleAxis(*args, **kwargs):
        pass
    
    
    def nodesByIdref(*args, **kwargs):
        pass
    
    
    def root(*args, **kwargs):
        pass
    
    
    def sendNamespaces(*args, **kwargs):
        pass
    
    
    def sourceLocation(*args, **kwargs):
        pass
    
    
    def stringValue(*args, **kwargs):
        pass
    
    
    def typedValue(*args, **kwargs):
        pass
    
    
    FirstChild = None
    
    
    InheritNamespaces = None
    
    
    NextSibling = None
    
    
    NodeCopySetting = None
    
    
    Parent = None
    
    
    PreserveNamespaces = None
    
    
    PreviousSibling = None
    
    
    SimpleAxis = None
    
    
    __new__ = None


class QXmlResultItems(_Object):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def current(*args, **kwargs):
        pass
    
    
    def hasError(*args, **kwargs):
        pass
    
    
    def next(*args, **kwargs):
        pass
    
    
    __new__ = None


class QXmlSchemaValidator(_Object):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def messageHandler(*args, **kwargs):
        pass
    
    
    def namePool(*args, **kwargs):
        pass
    
    
    def schema(*args, **kwargs):
        pass
    
    
    def setMessageHandler(*args, **kwargs):
        pass
    
    
    def setSchema(*args, **kwargs):
        pass
    
    
    def setUriResolver(*args, **kwargs):
        pass
    
    
    def uriResolver(*args, **kwargs):
        pass
    
    
    def validate(*args, **kwargs):
        pass
    
    
    __new__ = None


class QAbstractXmlReceiver(_Object):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def atomicValue(*args, **kwargs):
        pass
    
    
    def attribute(*args, **kwargs):
        pass
    
    
    def characters(*args, **kwargs):
        pass
    
    
    def comment(*args, **kwargs):
        pass
    
    
    def endDocument(*args, **kwargs):
        pass
    
    
    def endElement(*args, **kwargs):
        pass
    
    
    def endOfSequence(*args, **kwargs):
        pass
    
    
    def namespaceBinding(*args, **kwargs):
        pass
    
    
    def processingInstruction(*args, **kwargs):
        pass
    
    
    def startDocument(*args, **kwargs):
        pass
    
    
    def startElement(*args, **kwargs):
        pass
    
    
    def startOfSequence(*args, **kwargs):
        pass
    
    
    def whitespaceOnly(*args, **kwargs):
        pass
    
    
    __new__ = None


class QXmlName(_Object):
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
    
    
    def isNull(*args, **kwargs):
        pass
    
    
    def localName(*args, **kwargs):
        pass
    
    
    def namespaceUri(*args, **kwargs):
        pass
    
    
    def prefix(*args, **kwargs):
        pass
    
    
    def toClarkName(*args, **kwargs):
        pass
    
    
    def fromClarkName(*args, **kwargs):
        pass
    
    
    def isNCName(*args, **kwargs):
        pass
    
    
    __new__ = None


class QXmlQuery(_Object):
    def __copy__(*args, **kwargs):
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def bindVariable(*args, **kwargs):
        pass
    
    
    def evaluateTo(*args, **kwargs):
        pass
    
    
    def initialTemplateName(*args, **kwargs):
        pass
    
    
    def isValid(*args, **kwargs):
        pass
    
    
    def messageHandler(*args, **kwargs):
        pass
    
    
    def namePool(*args, **kwargs):
        pass
    
    
    def queryLanguage(*args, **kwargs):
        pass
    
    
    def setFocus(*args, **kwargs):
        pass
    
    
    def setInitialTemplateName(*args, **kwargs):
        pass
    
    
    def setMessageHandler(*args, **kwargs):
        pass
    
    
    def setQuery(*args, **kwargs):
        pass
    
    
    def setUriResolver(*args, **kwargs):
        pass
    
    
    def uriResolver(*args, **kwargs):
        pass
    
    
    QueryLanguage = None
    
    
    XPath20 = None
    
    
    XQuery10 = None
    
    
    XSLT20 = None
    
    
    XmlSchema11IdentityConstraintField = None
    
    
    XmlSchema11IdentityConstraintSelector = None
    
    
    __new__ = None


class QSourceLocation(_Object):
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
    
    
    def __repr__(*args, **kwargs):
        """
        x.__repr__() <==> repr(x)
        """
    
        pass
    
    
    def column(*args, **kwargs):
        pass
    
    
    def isNull(*args, **kwargs):
        pass
    
    
    def line(*args, **kwargs):
        pass
    
    
    def setColumn(*args, **kwargs):
        pass
    
    
    def setLine(*args, **kwargs):
        pass
    
    
    def setUri(*args, **kwargs):
        pass
    
    
    def uri(*args, **kwargs):
        pass
    
    
    __new__ = None


class QXmlNodeModelIndex(_Object):
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
    
    
    def additionalData(*args, **kwargs):
        pass
    
    
    def data(*args, **kwargs):
        pass
    
    
    def internalPointer(*args, **kwargs):
        pass
    
    
    def isNull(*args, **kwargs):
        pass
    
    
    def model(*args, **kwargs):
        pass
    
    
    Attribute = None
    
    
    Comment = None
    
    
    Document = None
    
    
    DocumentOrder = None
    
    
    Element = None
    
    
    Follows = None
    
    
    Is = None
    
    
    Namespace = None
    
    
    NodeKind = None
    
    
    Precedes = None
    
    
    ProcessingInstruction = None
    
    
    Text = None
    
    
    __new__ = None


class QAbstractUriResolver(_QObject):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def resolve(*args, **kwargs):
        pass
    
    
    __new__ = None
    
    
    staticMetaObject = None


class QXmlSerializer(QAbstractXmlReceiver):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def atomicValue(*args, **kwargs):
        pass
    
    
    def attribute(*args, **kwargs):
        pass
    
    
    def characters(*args, **kwargs):
        pass
    
    
    def codec(*args, **kwargs):
        pass
    
    
    def comment(*args, **kwargs):
        pass
    
    
    def endDocument(*args, **kwargs):
        pass
    
    
    def endElement(*args, **kwargs):
        pass
    
    
    def endOfSequence(*args, **kwargs):
        pass
    
    
    def namespaceBinding(*args, **kwargs):
        pass
    
    
    def outputDevice(*args, **kwargs):
        pass
    
    
    def processingInstruction(*args, **kwargs):
        pass
    
    
    def setCodec(*args, **kwargs):
        pass
    
    
    def startDocument(*args, **kwargs):
        pass
    
    
    def startElement(*args, **kwargs):
        pass
    
    
    def startOfSequence(*args, **kwargs):
        pass
    
    
    __new__ = None


class QXmlFormatter(QXmlSerializer):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def atomicValue(*args, **kwargs):
        pass
    
    
    def attribute(*args, **kwargs):
        pass
    
    
    def characters(*args, **kwargs):
        pass
    
    
    def comment(*args, **kwargs):
        pass
    
    
    def endDocument(*args, **kwargs):
        pass
    
    
    def endElement(*args, **kwargs):
        pass
    
    
    def endOfSequence(*args, **kwargs):
        pass
    
    
    def indentationDepth(*args, **kwargs):
        pass
    
    
    def processingInstruction(*args, **kwargs):
        pass
    
    
    def setIndentationDepth(*args, **kwargs):
        pass
    
    
    def startDocument(*args, **kwargs):
        pass
    
    
    def startElement(*args, **kwargs):
        pass
    
    
    def startOfSequence(*args, **kwargs):
        pass
    
    
    __new__ = None



