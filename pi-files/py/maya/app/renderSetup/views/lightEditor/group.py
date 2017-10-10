from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from maya.app.renderSetup.views.lightEditor.node import Attribute
from maya.app.renderSetup.views.lightEditor.node import Node
from maya.app.renderSetup.views.lightEditor.node import NodeAttributes

class GroupAttributes(NodeAttributes):
    def __init__(self):
        pass


class Group(Node):
    """
    This class wraps a group node (objectSet) in Maya.
    """
    
    
    
    def __del__(self):
        pass
    
    
    def __init__(self, model, mayaObj, attributes):
        pass
    
    
    def child(self, i):
        pass
    
    
    def childCount(self):
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
    
    
    def hasChild(self, child):
        pass
    
    
    def insertChild(self, child, row=-1):
        pass
    
    
    def isolate(self, value):
        pass
    
    
    def mayaName(self):
        pass
    
    
    def nodesToDelete(self):
        pass
    
    
    def removeChild(self, child):
        pass
    
    
    def syncWithChildren(self):
        pass
    
    
    def typeId(self):
        pass



GROUP_BAR_COLOR = None

ITEM_ROLE_ENABLED = 257

LIGHT_TEXT_COLOR_OVERRIDEN_BY_US = None

ITEM_ROLE_ISOLATED = 258

LIGHT_TEXT_COLOR_ANIMATED = None

ITEM_ROLE_TYPE = 256

LIGHT_TEXT_COLOR = None

TYPE_ID_GROUP_ITEM = 2

ITEM_ROLE_COLOR_BAR = 260

TYPE_ID_LIGHT_ITEM = 1

TYPE_ID_UNDEFINED = 0

ENABLE_LIGHT_EDITOR_GROUP_CMD = []

ITEM_ROLE_ATTR_HIDDEN = 262

ITEM_ROLE_LIGHT_TYPE = 259

ITEM_ROLE_ATTR_TYPE = 261

LIGHT_TEXT_COLOR_LOCKED = None

LIGHT_COLOR = None

GROUP_COLOR = None

LIGHT_BAR_COLOR = None


