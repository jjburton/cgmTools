def plugSrc(dstPlug):
    """
    Return the source of a connected destination plug.
    
    If the destination is unconnected, returns None.
    """

    pass


def nameToExistingUserNode(name):
    pass


def createGenericAttr(longName, shortName):
    pass


def createDstMsgAttr(longName, shortName):
    """
    Create a destination (a.k.a. input, or writable) message attribute.
    """

    pass


def transferPlug(src, dst):
    """
    Transfer the connection or value set on plug 'src' on to the plug 'dst'.
    """

    pass


def createSrcMsgAttr(longName, shortName):
    """
    Create a source (a.k.a. output, or readable) message attribute.
    """

    pass


def nameToUserNode(name):
    pass


def canOverrideNode(node):
    pass


def _isDestination(plug):
    """
    Returns True if the given plug is a destination plug, and False otherwise.
    
    If the plug is a compond attribute it returns True if any of it's children is a 
    destination plug.
    """

    pass


def findPlug(userNode, attr):
    """
    Return plug corresponding to attr on argument userNode.
    
    If the argument userNode is None, or the attribute is not found, None
    is returned.
    """

    pass


def getSrcNodeName(dst):
    """
    Get the name of the node connected to the argument dst plug.
    """

    pass


def getSrcNode(dst):
    """
    Get the node connected to the argument dst plug.
    """

    pass


def disconnectSrc(src):
    """
    Disconnect a source (readable) plug from all its destinations.
    
    Note that a single plug can be both source and destination, so this
    interface makes the disconnection intent explicit.
    """

    pass


def getDstUserNodes(src):
    """
    Get the user nodes connected to the argument src plug.
        Note: Only applies to MPxNode derived nodes
    
    If the src plug is unconnected, None is returned.
    """

    pass


def getSrcUserNode(dst):
    """
    Get the user node connected to the argument dst plug.
        Note: Only applies to MPxNode derived nodes
    
    If the dst plug is unconnected, None is returned.
    """

    pass


def connectMsgToDst(userNode, dst):
    """
    Connect the argument userNode's message attribute to the
    argument dst plug.
    
    If the userNode is None the dst plug is disconnected
    from its sources.
    
    If the dst plug is None the userNode's message plug
    is disconnected from its destinations
    """

    pass


def disconnectDst(dst):
    """
    Disconnect a destination (writable) plug from its source.
    
    Note that a single plug can be both source and destination, so this
    interface makes the disconnection intent explicit.
    """

    pass


def _transferConnectedPlug(src, dst):
    pass


def deleteNode(node):
    """
    Remove the argument node from the graph.
    
    This function is undoable.
    """

    pass


def disconnect(src, dst):
    pass


def connect(src, dst):
    """
    Connect source plug to destination plug.
    
    If the dst plug is None, the src plug will be disconnected from all its
    destinations (if any).  If the src plug is None, the dst plug will be
    disconnected from its source (if any).  If both are None, this function
    does nothing.  If the destination is already connected, it will be
    disconnected.
    """

    pass


def plugDst(srcPlug):
    """
    Return the destinations of a connected source plug.
    
    If the source is unconnected, returns None.
    """

    pass



kPlugTypeMismatch = []

kNoSuchNode = []

kSupportedSimpleTypes = set()

kSupportedVectorTypes = set()


