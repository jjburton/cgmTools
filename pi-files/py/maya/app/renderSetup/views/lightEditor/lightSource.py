from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from maya.app.renderSetup.views.lightEditor.node import Attribute
from maya.app.renderSetup.views.lightEditor.node import Node
from maya.app.renderSetup.views.lightEditor.node import NodeAttributes

class LightAttributes(NodeAttributes):
    def __init__(self):
        pass


class LightSource(Node):
    """
    This class wraps a light source node in Maya.
    """
    
    
    
    def __del__(self):
        pass
    
    
    def __init__(self, model, transformObj, shapeObj, attributes):
        pass
    
    
    def data(self, role, column):
        pass
    
    
    def dispose(self):
        pass
    
    
    def doDelete(self):
        pass
    
    
    def enable(*args, **kwargs):
        pass
    
    
    def flags(self, index):
        pass
    
    
    def getLightType(self):
        pass
    
    
    def getShape(self):
        pass
    
    
    def getShapeName(self):
        pass
    
    
    def initialize(self, shapeObj):
        """
        Initialize the light source with a given light shape object.
        Note that initialize supports to be called multiple times with different shapes.
        This will occure if the light type is changed on the light source.
        """
    
        pass
    
    
    def isolate(self, value):
        pass
    
    
    def mayaName(self):
        pass
    
    
    def nameChanged(self, oldName):
        pass
    
    
    def nodesToDelete(self):
        pass
    
    
    def typeId(self):
        pass



GROUP_BAR_COLOR = None

ITEM_ROLE_ENABLED = 257

LIGHT_TEXT_COLOR_OVERRIDEN_BY_US = None

LIGHT_COLLECTION_PREFIX = 'LightEditor_'

ITEM_ROLE_ISOLATED = 258

LIGHT_TEXT_COLOR_ANIMATED = None

ITEM_ROLE_TYPE = 256

kLightCollectionNameError = []

TYPE_ID_GROUP_ITEM = 2

ITEM_ROLE_COLOR_BAR = 260

TYPE_ID_LIGHT_ITEM = 1

TYPE_ID_UNDEFINED = 0

LIGHT_TEXT_COLOR = None

ITEM_ROLE_ATTR_HIDDEN = 262

ITEM_ROLE_LIGHT_TYPE = 259

ITEM_ROLE_ATTR_TYPE = 261

LIGHT_TEXT_COLOR_LOCKED = None

ENABLE_LIGHT_SOURCE_CMD = []

LIGHT_COLLECTION_SUFFIX = '_col'

LIGHT_COLOR = None

GROUP_COLOR = None

LIGHT_BAR_COLOR = None


