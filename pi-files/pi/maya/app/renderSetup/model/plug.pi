from itertools import izip

class Plug(object):
    """
    Helper class to allow seamless value assignment from one plug to another, 
    while correctly handling and abstracting away plug type.
    
    "self.type" returns the type of the plug.
        This is necessary to determine how to read and write the plug.
    "self.value" returns the value of the plug.
    "self.value = otherValue" will set the value of the plug to otherValue.
        This mutator assumes otherValue to be the same type as self.type
    
    "self.overrideType" returns the type of the override that should be created to override this plug.
    """
    
    
    
    def __init__(self, plugOrNode, attrName=None):
        """
        Constructors:
        Plug(MPlug)
        Plug(string (full plug name))
        Plug(MObject, MObject)
        Plug(MObject, string (attribute name))
        Plug(string (node name), string (attribute name))
        """
    
        pass
    
    
    def __str__(self):
        pass
    
    
    def accepts(self, other):
        """
        Returns true if plug would accept a connection with other plug
        i.e. plug and other plug are type compatible for connection.
        """
    
        pass
    
    
    def applyOverrideType(self, overType):
        pass
    
    
    def attribute(self):
        """
        Returns the attribute (MFnAttribute) of the plug
        """
    
        pass
    
    
    def cloneAttribute(self, nodeObj, longName, shortName):
        """
        Creates a new attribute on a node by cloning this plug's attribute.
        """
    
        pass
    
    
    def copyValue(self, other):
        """
        Sets the value of plug 'self' to the value contained in plug 'other' 
        The 'other' plug can be either a Plug or a MPlug.
        """
    
        pass
    
    
    def createAttributeFrom(self, nodeObj, longName, shortName, limits=None):
        """
        Creates a new attribute on a node by cloning this plug's attribute. 
        
        Note: None for a limit value means that there is no limit. For example,
              if min is None, it means that there is no minimum limit.
        """
    
        pass
    
    
    def getAttributeLimits(self):
        """
        Get the limits of the plug
        """
    
        pass
    
    
    def isOvrSupported(self):
        pass
    
    
    def localizedTypeString(self):
        pass
    
    
    def overrideType(self, overType):
        pass
    
    
    def setAttributeLimits(self, limits):
        pass
    
    
    def createAttribute(nodeObj, longName, shortName, dict):
        """
        Create a new attribute on a node using the given names and properties dictonary. 
        Returns an MObject to the new attribute. Use MFnDependencyNode.addAttribute() 
        to add the returned object as a new dynamic attribute on a node.
        """
    
        pass
    
    
    def getNames(plugName):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    attributeName = None
    
    hasLimits = None
    
    isConnectable = None
    
    isLocked = None
    
    isNumeric = None
    
    isUnit = None
    
    isValid = None
    
    isVector = None
    
    name = None
    
    nodeName = None
    
    plug = None
    
    type = None
    
    uiUnitValue = None
    
    value = None
    
    kAngle = 12
    
    
    kArray = 14
    
    
    kBool = 5
    
    
    kByte = 4
    
    
    kColor = 6
    
    
    kDistance = 13
    
    
    kDouble = 2
    
    
    kEnum = 7
    
    
    kFloat = 1
    
    
    kInt = 3
    
    
    kInvalid = 0
    
    
    kLast = 15
    
    
    kMessage = 10
    
    
    kObject = 9
    
    
    kString = 8
    
    
    kTime = 11



def toInternalUnits(type, value):
    pass


def toUiUnits(type, value):
    pass


def findPlug(node, attr):
    """
    Return a Plug instance if the MPlug was found, None otherwise.
    """

    pass



kPlugHasConnectedParent = []

kPlugHasConnectedChild = []

kUnsupportedAttribute = []

kCompoundTypeStr = []

kUnknownType = []

kArityMismatch = []

kNotOverridablePlug = []

kPlugWithoutLimits = []

kVectorTypeStr = []


