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


class RenderSetupFindCollectionsCmd(_MPxCommand):
    """
    Command that finds collections, the members of which match any of the 
    provided DAG objects. This command takes an optional flag:
    
    -inRenderLayers (mandatory flag) which only searches for collections under
    the specified render layer.
    
    Examples:
    // Finds from the "layer1" and "layer2" render layers, the collections 
    // that "pSphere1" and "pCube1" belong to
    renderSetupFindCollections "pSphere1" "pCube1" -inRenderLayers "layer1" "layer2"
    """
    
    
    
    def doIt(self, args):
        pass
    
    
    def isUndoable(self):
        pass
    
    
    def creator():
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    kCmdName = 'renderSetupFindCollections'
    
    
    kInRenderLayersFlag = '-irl'
    
    
    kInRenderLayersFlagLong = '-inRenderLayers'
    
    
    kInRenderLayersFlags = set()


class RenderLayerMembersCmd(_MPxCommand):
    """
    Command that filters a list of passed in DAG node nodes and returns the 
    filtered results based on the flags you set. This command is query only.
    The flags for this command are:
    
    -notIn: keep objects that do not belong to the provided render layers
    (default false, keep only objects that are render layer members in list. 
    When notIn is set to false, passing in a list of DAG nodes is optional).
    
    -renderLayers <renderLayers>: the render layers to check for membership 
    (-notIn false) or not check for membership (-notIn true).
    
    Example:
    // Isolate objects in the provided list ("pSphere1", "pCube1"), that are 
    // not in any of the provided render layers
    renderLayerMembers "pSphere1" "pCube1" -notIn true -renderLayers "layer1" "layer2"
    """
    
    
    
    def doIt(self, args):
        pass
    
    
    def isUndoable(self):
        pass
    
    
    def creator():
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    kCmdName = 'renderLayerMembers'
    
    
    kNotInFlag = '-ni'
    
    
    kNotInFlagLong = '-notIn'
    
    
    kNotInFlags = set()
    
    
    kRenderLayersFlag = '-rl'
    
    
    kRenderLayersFlagLong = '-renderLayers'
    
    
    kRenderLayersFlags = set()


class RenderSetupCmd(_MPxCommand):
    """
    Command that will be used for querying and editing the render setup 
    state. At present a user can only query the list of render layers with
    "renderSetup -query -renderLayers".
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
    
    kCmdName = 'renderSetup'
    
    
    kRenderLayersFlag = '-rl'
    
    
    kRenderLayersFlagLong = '-renderLayers'


class RenderSetupLegacyLayerCmd(_MPxCommand):
    """
    Command used to query the renderLayer associated to a specific renderSetupLayer
        Usage:
    "renderSetupLegacyLayer renderSetupLayerName".
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
    
    kCmdName = 'renderSetupLegacyLayer'



def getMembersAsLongNames(renderLayers):
    pass


def getCollections(renderLayers):
    """
    # Returns the collection models under the specified render layers
    """

    pass


def renderSetupFindCollections(objectNodeNames, renderLayerNames):
    pass


def inRenderLayers(*args, **kwargs):
    pass


def notInRenderLayers(*args, **kwargs):
    pass


def renderLayerMembers(objectNodeNames, renderLayerNames, notInRenderLayers=False):
    pass


def getLongName(name):
    pass


def longNamesToNamesDict(names):
    pass


def isCollectionMember(objectNodeName, collections):
    pass



kInvalidNodeName = []

kNotInNeedAListToFilter = []


