from pymel.util.external.BeautifulSoup import BeautifulSoup
from pymel.mayautils import getMayaLocation
from HTMLParser import HTMLParser
from pymel.util.external.BeautifulSoup import NavigableString

class CommandModuleDocParser(HTMLParser):
    def __init__(self, category, version=None):
        pass
    
    
    def handle_starttag(self, tag, attrs):
        pass
    
    
    def parse(self):
        pass


class NodeHierarchyDocParser(HTMLParser):
    def __init__(self, version=None):
        pass
    
    
    def handle_data(self, data):
        pass
    
    
    def handle_starttag(self, tag, attrs):
        pass
    
    
    def parse(self):
        pass


class ApiDocParser(object):
    def __init__(self, apiModule, version=None, verbose=False, enumClass="<type 'tuple'>", docLocation=None):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def formatMsg(self, *args):
        pass
    
    
    def getClassFilename(self):
        pass
    
    
    def getClassPath(self):
        pass
    
    
    def getDoxygenVersion(self, soup):
        pass
    
    
    def getMethodNameAndOutput(self, proto):
        pass
    
    
    def getOperatorName(self, methodName):
        pass
    
    
    def getPymelMethodNames(self):
        pass
    
    
    def handleEnumDefaults(self, default, type):
        pass
    
    
    def handleEnums(self, type):
        pass
    
    
    def isBadEnum(self, type):
        pass
    
    
    def isGetMethod(self):
        pass
    
    
    def isObsolete(self, proto):
        pass
    
    
    def isSetMethod(self):
        pass
    
    
    def parse(self, apiClassName):
        pass
    
    
    def parseEnums(self, proto):
        pass
    
    
    def parseMethod(self, proto):
        pass
    
    
    def parseMethodArgs(self, proto, returnType, names, types, typeQualifiers):
        pass
    
    
    def parseType(self, tokens):
        pass
    
    
    def parseTypes(self, proto):
        pass
    
    
    def setClass(self, apiClassName):
        pass
    
    
    def xprint(self, *args):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    DEPRECATED_MSG = []
    
    
    DOXYGEN_VER_RE = None
    
    
    MISSING_TYPES = []
    
    
    NOT_TYPES = []
    
    
    OBSOLETE_MSG = []
    
    
    OTHER_TYPES = []
    
    
    PYMEL_ENUM_DEFAULTS = {}
    
    
    TYPEDEF_RE = None


class CommandDocParser(HTMLParser):
    """
    #---------------------------------------------------------------
    #        Doc Parser
    #---------------------------------------------------------------
    """
    
    
    
    def __init__(self, command):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def addFlagData(self, data):
        pass
    
    
    def endFlag(self):
        pass
    
    
    def handle_data(self, data):
        pass
    
    
    def handle_endtag(self, tag):
        pass
    
    
    def handle_entityref(self, name):
        pass
    
    
    def handle_starttag(self, tag, attrs):
        pass
    
    
    def startFlag(self, data):
        pass



def printTree(tree, depth=0):
    pass


def mayaIsRunning():
    """
    Returns True if maya.cmds have  False otherwise.
    
    Early in interactive startup it is possible for commands to exist but for Maya to not yet be initialized.
    
    :rtype: bool
    """

    pass


def _iskeyword(*args, **kwargs):
    """
    x.__contains__(y) <==> y in x.
    """

    pass


def mayaDocsLocation(version=None):
    pass



FLAGMODES = ()

_logger = None


