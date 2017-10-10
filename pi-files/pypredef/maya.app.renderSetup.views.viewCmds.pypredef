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


class RenderSetupSelectCmd(_MPxCommand):
    """
    Command that can be used to select render setup elements as well as to
    query the elements in the render setup selection.
    
    Five optional flags can be used with this command:
    
    -additive (-a) adds elements to the selection (without clearing it)
    
    -deselect (-d) removes elements from the current selection
    
    -renderLayers is a query only flag that specifies that renderLayers 
    should be returned as part of the query
    
    -collections is a query only flag that specifies that collections should 
    be returned as part of the query
    
    -overrides is a query only flag that specifies that overrides should be 
    returned as part of the query
    
    By default the selection is cleared before selecting elements. Also the
    additive and deselect flags cannot be used in conjunction.
    
    Sample Usage:
    // Select "renderSetupLayer1" and "renderSetupLayer2" 
    renderSetupSelect "renderSetupLayer1" "renderSetupLayer2"
    
    // Add "renderSetupLayer1" and "renderSetupLayer2" to the selection
    renderSetupSelect -additive "renderSetupLayer1" "renderSetupLayer2"
    
    // Deselect "renderSetupLayer1" and "renderSetupCollection2" from the selection
    renderSetupSelect -deselect "renderSetupLayer1" "renderSetupCollection2"
    
    // Query the selected render setup items
    renderSetupSelect -query
    
    // Query the selected render setup items that are renderLayers and 
    // overrides
    renderSetupSelect -query -renderLayers -overrides
    """
    
    
    
    def doIt(self, args):
        pass
    
    
    def isUndoable(self):
        pass
    
    
    def createSyntax():
        pass
    
    
    def creator():
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    kAddFlag = '-a'
    
    
    kAddFlagLong = '-additive'
    
    
    kCmdName = 'renderSetupSelect'
    
    
    kCollectionsFlag = '-c'
    
    
    kCollectionsFlagLong = '-collections'
    
    
    kDeselectFlag = '-d'
    
    
    kDeselectFlagLong = '-deselect'
    
    
    kOverridesFlag = '-o'
    
    
    kOverridesFlagLong = '-overrides'
    
    
    kRenderLayersFlag = '-rl'
    
    
    kRenderLayersFlagLong = '-renderLayers'



def getRenderSetupView():
    pass


def getSelectionModel():
    pass


def getRenderSetupWindow():
    pass


def getSelectedCollections():
    pass


def getSelection(renderLayers=False, collections=False, overrides=False):
    pass


def _itemMatches(item, renderLayers, overrides, collections):
    pass


def inSelectedRenderLayers(*args, **kwargs):
    """
    Tests for nodes in any currently selected layer.
    args: an array of nodes to test
    kwargs:
        attributes: an array of attributes to test
    """

    pass


def notInSelectedRenderLayers(*args, **kwargs):
    """
    Tests for nodes not in any currently selected layer.
    args: an array of nodes to test
    kwargs:
        attributes: an array of attributes to test
    """

    pass



kParsingError = []

kAddAndDeselectEditOnly = []

kNotEditableFlags = []

kAddAndDeselectNoTogether = []

kSelectionEditFailed = []


