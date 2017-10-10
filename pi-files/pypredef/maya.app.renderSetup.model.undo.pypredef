"""
This module provides a context manager that provides for convenient undo
macro commands (called "chunks" in Maya terminology).  It ensures that
only the top-level call to the undo context manager will open and close
a chunk, thus providing a single, named entry on the undo stack.
"""

class NotifyCtxMgr:
    """
    Safe way to manage group undo chunks using the 'with' command.
    
    It will close the chunk automatically on exit from the block.
    Supports post undo and post redo notification callables.
    
    Example:
        with NotifyCtxMgr('Create Poly Cubes', postRedo, postUndo):
            cmds.polyCube()
            cmds.polyCube()
        # Will undo both polyCube() creation calls, and call postUndo.
        cmds.undo()
    
    If a single callable is given, it will be called post undo and post redo.
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, type, value, traceback):
        pass
    
    
    def __init__(self, name, postRedo, postUndo=None):
        pass
    
    
    openChunk = True


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


class CtxMgr:
    """
    Safe way to manage group undo chunks using the 'with' command.
    It will close the chunk automatically on exit from the block
    
    Example:
        with CtxMgr('Create Poly Cubes'):
            cmds.polyCube()
            cmds.polyCube()
        cmds.undo() # Will undo both polyCube() creation calls.
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, type, value, traceback):
        pass
    
    
    def __init__(self, name='unnamedOperation'):
        pass
    
    
    openChunk = True


class SuspendUndo:
    """
    Safe way to suspend and resume undo logging using the 'with' command.
    It will automatically resume undo on exit from the block
    
    Example:
        with SuspendUndo():
            cmds.polyCube()
            cmds.polyCube()
        cmds.undo() # Will not undo the creation calls.
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, type, value, traceback):
        pass
    
    
    def __init__(self):
        pass


class NotifyPostRedoCmd(_MPxCommand):
    """
    Helper command notify after redo.
    
    This command is a private implementation detail of this module and should
    not be called otherwise.
    """
    
    
    
    def __init__(self, callable):
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
    
    
    def execute(callable):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    callable = None
    
    
    kCmdName = 'notifyPostRedo'


class NotifyPostUndoCmd(_MPxCommand):
    """
    Helper command notify after undo.
    
    This command is a private implementation detail of this module and should
    not be called otherwise.
    """
    
    
    
    def __init__(self, callable):
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
    
    
    def execute(callable):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    callable = None
    
    
    kCmdName = 'notifyPostUndo'



def notify(chunkName, postRedo, postUndo=None):
    """
    Undo decorator to name and group in a single chunk all commands
    inside the decorated callable.
    
    The postRedo and postUndo callables are called at end of redo (and do),
    and at end of undo, respectively.  If a single callable is given, it
    will be called both at end of redo and at end of undo.
    """

    pass


def suspend():
    """
    Undo decorator to suspend and resume undo for all commands
    inside the decorated callable.
    """

    pass


def chunk(chunkName):
    """
    Undo decorator to name and group in a single chunk all commands
    inside the decorated callable.
    """

    pass



