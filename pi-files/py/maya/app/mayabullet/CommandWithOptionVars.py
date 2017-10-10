from maya.app.mayabullet.Trace import Trace

class CommandWithOptionVars(object):
    """
    Base class that handles Maya Commands.  Tailored for MenuItems.
     * Executes command from menu
     * Displays option box dialog
     * Gets/Sets OptionVars
    
    This is the Base Class for handling all that is needed for menuItem, the
    menuItem OptionBox w/ Dialog, and commandline calls. One can derive a class
    for individual menuItems/actions with minimal code as shown below.
    
    :Examples:
    MenuItem using prefs: CommandWithOptionVars().executeCommandCB()
    MenuItemOptionBox:    CommandWithOptionVars().createOptionDialog()
    Commandline:          CommandWithOptionVars().command()
    Cmdline w/ override:  CommandWithOptionVars().command(myoption='AAA')
    """
    
    
    
    def __init__(*args, **kw):
        pass
    
    
    def addOptionDialogWidgets(*args, **kw):
        pass
    
    
    def createOptionDialog(*args, **kw):
        pass
    
    
    def executeCommandAndHideOptionBoxCB(*args, **kw):
        pass
    
    
    def executeCommandAndSaveCB(*args, **kw):
        pass
    
    
    def executeCommandCB(*args, **kw):
        pass
    
    
    def getOptionVars(*args, **kw):
        pass
    
    
    def getWidgetValues(*args, **kw):
        pass
    
    
    def hideOptionBoxCB(*args, **kw):
        pass
    
    
    def optionBoxClosing(*args, **kw):
        pass
    
    
    def resetOptionBoxToDefaultsCB(*args, **kw):
        pass
    
    
    def saveOptionBoxPreferencesCB(*args, **kw):
        pass
    
    
    def setOptionVars(*args, **kw):
        pass
    
    
    def setWidgetValues(*args, **kw):
        pass
    
    
    def updateOptionBox(*args, **kw):
        pass
    
    
    def visibilityChangedCB(*args, **kw):
        pass
    
    
    def command(*args, **kw):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def retrieveOptionVars(*args, **kw):
    pass



logger = None


