from maya.app.renderSetup.model.nodeNotes import *

from maya.app.renderSetup.model.serializableNode import SerializableNode
from maya.app.renderSetup.model.observable import Observable
from itertools import izip

from . import nodeList

class ChildNode(Observable, NodeNotes, SerializableNode, nodeList.ListItem):
    """
    The class provides the basic functionality for any child nodes
    """
    
    
    
    def __init__(self):
        pass
    
    
    def acceptImport(self):
        pass
    
    
    def addOpaqueData(self, key, data):
        pass
    
    
    def getImportedStatus(self):
        pass
    
    
    def getOpaqueData(self, key):
        pass
    
    
    def hasOpaqueData(self, key):
        pass
    
    
    def removeOpaqueData(self, key):
        pass
    
    
    def setImportedStatus(self, value):
        pass
    
    
    def setName(self, newName):
        """
        Rename render setup node.
        """
    
        pass
    
    
    def creator():
        """
        # Awkwardly, abstract base classes seem to need a creator method.
        """
    
        pass
    
    
    def initializer():
        pass
    
    
    kTypeId = None
    
    
    kTypeName = 'childNode'


class TreeOrderedItem(object):
    """
    Override tree mixin class.
    
    A render layer can be considered as the root of a tree of overrides,
    with collections (and nested collections) as internal tree nodes, and
    overrides as leaf nodes.  This base class implements ordering on
    collections and overrides.  An override that is higher-priority will
    supercede the effect of a lower-priority override, and transitively any
    override in a higher-priority partition will supercede the effects of
    any override in a lower-priority partition.
    
    In a given list, an item is higher-priority if it occurs after another
    item (closer to the back) in the same list.  If the items are from
    different lists, we move up the tree hierarchy until we can compare two
    items from the same list.
    
    Note that in the render setup hierarchy, only collections and overrides
    are ordered; render layers are not.
    """
    
    
    
    def __gt__(self, b):
        """
        Return whether this item is higher-priority than the argument.
        
        For well-balanced override trees, the average time complexity of
        this method is O(log(n)), for n overrides and collections.
        Pathological cases (n collections strung out in a linear hierarchy,
        or n overrides in a collection strung out in a linear list) will
        cause O(n) time complexity.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


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


class EditImportedStatusCmd(_MPxCommand):
    """
    Command to unapply and reapply a change of the imported status.
    
    This command is a private implementation detail of this module and should
    not be called otherwise.
    """
    
    
    
    def __init__(self, node, imported):
        pass
    
    
    def doIt(self, args):
        pass
    
    
    def isUndoable(self):
        pass
    
    
    def redoIt(self):
        pass
    
    
    def undoIt(self):
        pass
    
    
    def creator():
        pass
    
    
    def execute(node, imported):
        """
        Unapply the change of the imported status flag.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    imported = None
    
    
    kCmdName = 'editImportedStatus'
    
    
    node = None



_IMPORTED_ATTRIBUTE_SHORT_NAME = 'imp'

kRename = []

kOrderingFailure = "Nodes '%s' and '%s' cannot be ordered."

kCmdPrivate = []


