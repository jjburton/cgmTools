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


class ListCmdBase(_MPxCommand):
    """
    Base class for list commands that write to node lists.
    
    This command is intended as a base class for concrete list commands.
    """
    
    
    
    def doIt(self, args):
        pass
    
    
    def isUndoable(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    nodeList = None


class PopCmd(ListCmdBase):
    """
    Remove and return the last item from a list.
    
    This command is a private implementation detail of this module and should
    not be called otherwise.
    """
    
    
    
    def __init__(self, nodeList):
        pass
    
    
    def doIt(self, args):
        pass
    
    
    def redoIt(self):
        pass
    
    
    def undoIt(self):
        pass
    
    
    def creator():
        pass
    
    
    def execute(nodeList):
        """
        Remove and return the last list item from the node list, and add an
        entry to the undo queue.
        """
    
        pass
    
    
    kCmdName = 'popListItem'
    
    
    listItem = None


class RemoveCmd(ListCmdBase):
    """
    Remove an item from a list.
    
    This command is a private implementation detail of this module and should
    not be called otherwise.
    """
    
    
    
    def __init__(self, nodeList, listItem):
        pass
    
    
    def redoIt(self):
        pass
    
    
    def undoIt(self):
        pass
    
    
    def creator():
        pass
    
    
    def execute(nodeList, listItem):
        """
        Remove the list item from the node list, and add an entry to the
        undo queue.
        """
    
        pass
    
    
    kCmdName = 'removeListItem'
    
    
    listItem = None


class AppendCmd(ListCmdBase):
    """
    Append an item to a list.
    
    This command is a private implementation detail of this module and should
    not be called otherwise.
    """
    
    
    
    def __init__(self, nodeList, listItem):
        pass
    
    
    def redoIt(self):
        pass
    
    
    def undoIt(self):
        pass
    
    
    def creator():
        pass
    
    
    def execute(nodeList, listItem):
        """
        Append the item to the list, and add an entry to the undo queue.
        """
    
        pass
    
    
    kCmdName = 'appendListItem'
    
    
    listItem = None


class InsertCmd(ListCmdBase):
    """
    Insert a list item before a given position in a list.
    
    This command is a private implementation detail of this module and should
    not be called otherwise.
    """
    
    
    
    def __init__(self, nodeList, ndx, listItem):
        pass
    
    
    def redoIt(self):
        pass
    
    
    def undoIt(self):
        pass
    
    
    def creator():
        pass
    
    
    def execute(nodeList, ndx, listItem):
        """
        Insert the list item into the node list before position ndx, and
        add an entry to the undo queue.
        """
    
        pass
    
    
    kCmdName = 'insertListItem'
    
    
    listItem = None
    
    
    ndx = None


class PrependCmd(ListCmdBase):
    """
    Add an item to the head of the list.
    
    This command is a private implementation detail of this module and should
    not be called otherwise.
    """
    
    
    
    def __init__(self, nodeList, listItem):
        pass
    
    
    def redoIt(self):
        pass
    
    
    def undoIt(self):
        pass
    
    
    def creator():
        pass
    
    
    def execute(nodeList, listItem):
        """
        Prepend the item to the list, and add an entry to the undo queue.
        """
    
        pass
    
    
    kCmdName = 'prependListItem'
    
    
    listItem = None


class InsertBeforeCmd(ListCmdBase):
    """
    Insert a list item before another.
    
    This command is a private implementation detail of this module and should
    not be called otherwise.
    """
    
    
    
    def __init__(self, nodeList, nextItem, listItem):
        pass
    
    
    def redoIt(self):
        pass
    
    
    def undoIt(self):
        pass
    
    
    def creator():
        pass
    
    
    def execute(nodeList, nextItem, listItem):
        """
        Insert the list item into the node list before nextItem, and add an
        entry to the undo queue.
        """
    
        pass
    
    
    kCmdName = 'insertListItemBefore'
    
    
    listItem = None
    
    
    nextItem = None



def prepend(list, x):
    """
    Add x to the head of the list.
    
    This function is a convenience for insert(list, 0, x).  It has O(1) time
    complexity.
    """

    pass


def forwardListGenerator(list):
    """
    # Not a write operation, but needed by the implementation of insert().
    """

    pass


def append(list, x):
    """
    Append node x to the list.
    
    This function has O(1) time complexity.
    """

    pass


def pop(list):
    """
    Pop the last node from the list.
    
    The method disconnects the last node from list and returns it.  It has
    O(1) time complexity.
    """

    pass


def insertBefore(list, nextItem, x):
    """
    Insert node x before item nextItem in list.
    
    If nextItem is None, element x will be appended to the list.  This function
    has O(1) time complexity.
    """

    pass


def insert(list, ndx, x):
    """
    Insert node x before position ndx in list.
    
    Positions run from 0 to n-1, for a list of length n.  Inserting at
    position 0 calls prepend(), and thus has O(1) time complexity.
    Inserting mid-list has O(n) time complexity.  Inserting at position n
    or beyond appends to the list, with O(n) time complexity.  To append to
    the list use append() directly, as it has O(1) time complexity.
    """

    pass


def remove(list, x):
    """
    Remove node x from the list.
    
    This function will detach the node x from the list if x is an element
    of the list, otherwise nothing will be done.
    
    It has O(1) time complexity.
    """

    pass



kListCmdPrivate = []


