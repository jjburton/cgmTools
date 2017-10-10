class NodeExporter(object):
    """
    # Helper exporter to encode/decode any nodes
    """
    
    
    
    def decode(self, encodedData):
        pass
    
    
    def encode(self):
        pass
    
    
    def setPlugsToIgnore(self, plugsToIgnore):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class RenderSettingsCallbacks(object):
    """
    # Renderers should either extend this class or create a class with the same signature to provide additional render settings callbacks
    """
    
    
    
    def decode(self, rendererData):
        pass
    
    
    def encode(self):
        pass
    
    
    def getNodes(self):
        """
        # Returns the default render settings nodes for the specific renderer
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class AOVCallbacks(object):
    """
    # Renderers should either extend this class or create a class with the same signature to provide additional AOV callbacks
    """
    
    
    
    def decode(self, aovsData, decodeType):
        pass
    
    
    def displayMenu(self):
        """
        # This function is called to display the AOV information for the current renderer
        """
    
        pass
    
    
    def encode(self):
        pass
    
    
    def getAOVName(self, aovNode):
        """
        # From a given AOV node, returns the AOV name
        """
    
        pass
    
    
    def getChildCollectionSelector(self, selectorName, aovName):
        """
        # This function is called to create the selector for the AOV child collection
        """
    
        pass
    
    
    def getCollectionSelector(self, selectorName):
        """
        # This function is called to create the selector for the AOV collection
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    DECODE_TYPE_MERGE = 1
    
    
    DECODE_TYPE_OVERWRITE = 0


class BasicNodeExporter(NodeExporter):
    """
    # Exporter that is used to export the nodes that have been set
    """
    
    
    
    def getNodes(self):
        pass
    
    
    def setNodes(self, nodes):
        pass



def registerCallbacks(renderer, callbacksType, callbacks):
    pass


def getCallbacks(callbacksType):
    pass


def unregisterCallbacks(renderer, callbacksType=None):
    pass



CALLBACKS_TYPE_RENDER_SETTINGS = 0

kDefaultNodeMissing = []

rendererCallbacks = {}

CALLBACKS_TYPE_AOVS = 1


