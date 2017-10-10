"""
This module provides the override base and concrete classes, as well as
utility functions to operate on overrides.
"""

class RelOverrideComputeClass:
    """
    Specialization for work around
    """
    
    
    
    def compute(self, plug, dataBlock):
        pass


class _MPxCommand(object):
    """
    Base class for custom commands.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def doIt(*args, **kwargs):
        """
        Called by Maya to execute the command.
        """
    
        pass
    
    
    def hasSyntax(*args, **kwargs):
        """
        Called by Maya to determine if the command provides an MSyntax object describing its syntax.
        """
    
        pass
    
    
    def isUndoable(*args, **kwargs):
        """
        Called by Maya to determine if the command supports undo.
        """
    
        pass
    
    
    def redoIt(*args, **kwargs):
        """
        Called by Maya to redo a previously undone command.
        """
    
        pass
    
    
    def syntax(*args, **kwargs):
        """
        Returns the command's MSyntax object, if it has one.
        """
    
        pass
    
    
    def undoIt(*args, **kwargs):
        """
        Called by Maya to undo a previously executed command.
        """
    
        pass
    
    
    def appendToResult(*args, **kwargs):
        """
        Append a value to the result to be returned by the command.
        """
    
        pass
    
    
    def clearResult(*args, **kwargs):
        """
        Clears the command's result.
        """
    
        pass
    
    
    def currentResult(*args, **kwargs):
        """
        Returns the command's current result.
        """
    
        pass
    
    
    def currentResultType(*args, **kwargs):
        """
        Returns the type of the current result.
        """
    
        pass
    
    
    def displayError(*args, **kwargs):
        """
        Display an error message.
        """
    
        pass
    
    
    def displayInfo(*args, **kwargs):
        """
        Display an informational message.
        """
    
        pass
    
    
    def displayWarning(*args, **kwargs):
        """
        Display a warning message.
        """
    
        pass
    
    
    def isCurrentResultArray(*args, **kwargs):
        """
        Returns true if the command's current result is an array of values.
        """
    
        pass
    
    
    def setResult(*args, **kwargs):
        """
        Set the value of the result to be returned by the command.
        """
    
        pass
    
    
    commandString = None
    
    historyOn = None
    
    __new__ = None
    
    
    kDouble = 1
    
    
    kLong = 0
    
    
    kNoArg = 3
    
    
    kString = 2


from . import childNode

class Override(childNode.TreeOrderedItem, childNode.ChildNode):
    """
    Override node base class.
    
    An override represents a non-destructive change to a scene property
    that can be reverted or disabled.  Render setup uses overrides to describe
    changes that apply in a single render layer, and are unapplied when
    switching to another render layer.  When working within a render layer, an
    override can be preserved but disabled, to remove its effect.
    
    The override node base class cannot be directly created in Maya.  It is
    derived from the ListItem base class, so that overrides can be inserted
    in a list.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def activate(self):
        pass
    
    
    def attrValuePlugName(self):
        pass
    
    
    def attributeName(self):
        pass
    
    
    def deactivate(self):
        pass
    
    
    def enabledChanged(self):
        pass
    
    
    def getApplyOverrides(self):
        """
        Return the list of apply override nodes that correspond to this override.
        """
    
        pass
    
    
    def getRenderLayer(self):
        pass
    
    
    def isAbstractClass(self):
        pass
    
    
    def isAcceptableChild(self, model):
        """
        Check if the model could be a child
        """
    
        pass
    
    
    def isEnabled(self):
        pass
    
    
    def isSelfEnabled(self):
        pass
    
    
    def isValid(self):
        pass
    
    
    def postConstructor(self):
        pass
    
    
    def setAttributeName(self, attributeName):
        """
        Set the name of the attribute to be overridden.
        """
    
        pass
    
    
    def setSelfEnabled(self, value):
        pass
    
    
    def typeId(self):
        pass
    
    
    def typeName(self):
        pass
    
    
    def creator(cls):
        """
        # Awkwardly, abstract base classes seem to need a creator method.
        """
    
        pass
    
    
    def initializer():
        pass
    
    
    attrName = None
    
    
    enabled = None
    
    
    kTypeId = None
    
    
    kTypeName = 'override'
    
    
    parentEnabled = None
    
    
    parentNumIsolatedChildren = None
    
    
    selfEnabled = None


class LeafClass:
    """
    To be used by leaf classes only
    """
    
    
    
    def isAbstractClass(self):
        pass


class AbsOverrideComputeClass:
    """
    Specialization for work around
    """
    
    
    
    def compute(self, plg, dataBlock):
        pass


class ValueOverride(Override):
    """
    Override node base class for all value overrides.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def apply(*args, **kwargs):
        pass
    
    
    def applyInsertOne(*args, **kwargs):
        pass
    
    
    def getOverridden(self):
        """
        Return the list of nodes being overridden.
        
        The items in the return list are triplets of (MObject, attrName, ovrNext).
        MObject is the object being overridden, attrName is the name of the attribute 
        being overridden and ovrNext is the override node in the position of the next 
        override in the apply override list.
        
        Returns an empty list if no attribute is being overridden.
        """
    
        pass
    
    
    def unapply(*args, **kwargs):
        pass
    
    
    def initializer():
        pass
    
    
    kTypeId = None
    
    
    kTypeName = 'valueOverride'


class UnapplyCmd(_MPxCommand):
    """
    Command to unapply and reapply an override.
    
    This command is a private implementation detail of this module and should
    not be called otherwise.
    """
    
    
    
    def __init__(self, override):
        pass
    
    
    def doIt(self, args):
        pass
    
    
    def isUndoable(self):
        pass
    
    
    def redoIt(*args, **kwargs):
        pass
    
    
    def undoIt(*args, **kwargs):
        pass
    
    
    def creator():
        pass
    
    
    def execute(override):
        """
        Unapply the override, and add an entry to the undo queue.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    kCmdName = 'unapplyOverride'
    
    
    override = None


class AbsOverride(LeafClass, AbsOverrideComputeClass, ValueOverride):
    """
    Absolute override node.
    
    This concrete override node type implements an absolute override
    (replace value) for an attribute.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def finalize(self, plugName):
        """
        Finalize the creation of an override by setting all needed information
        """
    
        pass
    
    
    def getAttrValue(self):
        pass
    
    
    def isValid(self):
        pass
    
    
    def setAttrValue(self, value):
        pass
    
    
    def initializer():
        pass
    
    
    kAttrValueLong = 'attrValue'
    
    
    kAttrValueShort = 'atv'
    
    
    kTypeId = None
    
    
    kTypeName = 'absOverride'


class RelOverride(LeafClass, RelOverrideComputeClass, ValueOverride):
    """
    Relative override node to transform a attribute using:
    
    newValue = originalValue * multiply + offset
    
    This concrete override node type implements a relative override
    for a float scalar attribute.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def finalize(self, plugName):
        """
        Finalize the creation of an override by setting all needed information
        """
    
        pass
    
    
    def getMultiply(self):
        pass
    
    
    def getOffset(self):
        pass
    
    
    def isValid(self):
        pass
    
    
    def multiplyPlugName(self):
        pass
    
    
    def offsetPlugName(self):
        pass
    
    
    def setMultiply(self, value):
        pass
    
    
    def setOffset(self, value):
        pass
    
    
    def initializer():
        pass
    
    
    kMultiplyLong = 'multiply'
    
    
    kMultiplyShort = 'mul'
    
    
    kOffsetLong = 'offset'
    
    
    kOffsetShort = 'ofs'
    
    
    kTypeId = None
    
    
    kTypeName = 'relOverride'



def delete(*args, **kwargs):
    pass


def create(*args, **kwargs):
    pass


def fillVector(value, dimension):
    """
    Return a list of specified dimension initialized with value.
    
    If dimension is 0, return the argument value as a scalar.
    """

    pass



kUnconnectableAttr = []

kLockedPlug = []

kUnapplyCmdPrivate = []


