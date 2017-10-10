from maya.app.renderSetup.views.lightEditor.itemModel import *

from maya.app.renderSetup.views.lightEditor.itemStyle import ItemStyle
from maya.app.renderSetup.views.lightEditor.itemDelegate import AngleFieldDelegate
from maya.app.renderSetup.views.lightEditor.itemDelegate import FloatFieldDelegate
from copy import deepcopy
from maya.app.renderSetup.views.renderSetupButton import RenderSetupButton
from maya.app.renderSetup.views.lightEditor.itemDelegate import ColorPickerDelegate
from maya.app.renderSetup.views.lightEditor.itemDelegate import ColumnDelegate
from maya.app.renderSetup.views.lightEditor.itemDelegate import AttributeDelegate
from maya.app.renderSetup.views.lightEditor.itemDelegate import CheckBoxDelegate
from maya.app.renderSetup.views.lightEditor.itemDelegate import NameDelegate
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.renderSetup.views.lightEditor.itemDelegate import IntFieldDelegate

import PySide2.QtWidgets as _QtWidgets

class Editor(MayaQWidgetDockableMixin, _QtWidgets.QWidget):
    """
    This class implements the dockable light editor.
    """
    
    
    
    def __del__(self):
        pass
    
    
    def __init__(self):
        pass
    
    
    def closeEvent(self, event):
        pass
    
    
    def dispose(self):
        pass
    
    
    def dockCloseEventTriggered(self):
        pass
    
    
    def minimumSizeHint(self):
        pass
    
    
    def setEditorMode(self, mode, layer):
        pass
    
    
    def setSizeHint(self, size):
        pass
    
    
    def sizeHint(self):
        pass
    
    
    EDITOR_GLOBAL_MODE = 0
    
    
    EDITOR_LAYER_MODE = 1
    
    
    MINIMUM_SIZE = None
    
    
    PREFERRED_SIZE = None
    
    
    STARTING_SIZE = None
    
    
    WINDOW_STATE_PREFERENCE = 'renderSetupLightEditorState'
    
    
    staticMetaObject = None
    
    
    visibilityChanged = None


class LookThroughWindow(MayaQWidgetDockableMixin, _QtWidgets.QWidget):
    """
    This class implements the look through window.
    """
    
    
    
    def __del__(self):
        pass
    
    
    def __init__(self, parent):
        pass
    
    
    def closeEvent(self, event):
        pass
    
    
    def dockCloseEventTriggered(self):
        pass
    
    
    def lookThroughLight(self, light):
        """
        Opens a model panel with camera looking through the given light.
        """
    
        pass
    
    
    def minimumSizeHint(self):
        pass
    
    
    def setSizeHint(self, size):
        pass
    
    
    def sizeHint(self):
        pass
    
    
    MINIMUM_SIZE = None
    
    
    PREFERRED_SIZE = None
    
    
    STARTING_SIZE = None
    
    
    WINDOW_STATE_PREFERENCE = 'lookThroughWindowState'
    
    
    staticMetaObject = None


import PySide2.QtCore as _QtCore

class LightEditorUI(_QtCore.QObject):
    """
    Light Editor Window management
    """
    
    
    
    def currentRenderLayer(self):
        pass
    
    
    def isVisible(self):
        pass
    
    
    def openEditor(self, layer=None):
        pass
    
    
    def visibilityUpdate(self):
        pass
    
    
    staticMetaObject = None
    
    
    visibilityChanged = None


class EditorTreeView(_QtWidgets.QTreeView):
    """
    This class implements the editor tree view.
    """
    
    
    
    def __init__(self, parent):
        pass
    
    
    def dispose(self):
        pass
    
    
    def focus(self, item):
        pass
    
    
    def getIndent(self, index):
        pass
    
    
    def loadColumnOrder(self):
        pass
    
    
    def mouseDoubleClickEvent(self, event):
        pass
    
    
    def mousePressEvent(self, event):
        """
        # NOTE: Some back story. The mouse press and mouse double click events here were added because of the high DPI scaling changes.
        # Previously the color bar was being drawn in front of the expand/collapse arrow by some distance. But after the high DPI scaling
        # This actually pushed the color bar at high DPIs off the screen. So to fix this everything needed to be reoriented to be drawn
        # relative to the left of the screen. The problem that this introduced was that the region that handled clicks for the
        # expand/collapse arrows needed to be moved and the only way to do so was to implement the handling of click events ourselves.
        # That is the long explanation of what these two methods are for. The first deals with clicks for expand/collapse, the second
        # deals with editing requests when the user double clicks passed the expand/collapse region.
        """
    
        pass
    
    
    def mouseReleaseEvent(self, event):
        pass
    
    
    def showContextMenu(self, point):
        """
        Displays the right-click context menu actions.
        """
    
        pass
    
    
    staticMetaObject = None


class EditorCentralWidget(_QtWidgets.QWidget):
    """
    This class implements the dockable light editor.
    """
    
    
    
    def __del__(self):
        pass
    
    
    def __init__(self, parent=None):
        pass
    
    
    def dispose(self):
        pass
    
    
    def getLightCreator(self, lightType):
        pass
    
    
    def minimumSizeHint(self):
        pass
    
    
    def newGroup(self):
        pass
    
    
    def newLight(self, lightType):
        """
        Adds a new light to the model.
        """
    
        pass
    
    
    def saveLookThroughWindowState(self):
        pass
    
    
    def selectionChanged(self):
        pass
    
    
    def setAttributeByLabel(self, nodeName, attrLabel, value):
        """
        Set value for attribute with given label on the node with given name.
        """
    
        pass
    
    
    def setEditorMode(self, mode, layer):
        pass
    
    
    def sizeHint(self):
        pass
    
    
    BUTTON_SIZE = 20.0
    
    
    MINIMUM_SIZE = None
    
    
    PREFERRED_SIZE = None
    
    
    STARTING_SIZE = None
    
    
    TAB_LAYOUT_BOTTOM_MARGIN = 2.0
    
    
    TAB_LAYOUT_RIGHT_MARGIN = 2.0
    
    
    staticMetaObject = None



def openEditorUI(layer=None):
    """
    Opens the editor window, creating it if needed
    """

    pass


def editorChanged():
    pass


def editorDestroyed(object=None):
    pass



theLightEditorUI = None

LIGHT_EDITOR_TEXT_GLOBAL_MODE = []

_editorInstance = None

LAYER_TEXT = []

NAME_COLUMN_WIDTH = 150.0

LIGHT_EDITOR_COLUMN_ORDER_OPTION_VAR = 'renderSetup_LightEditorColumnOrder'

LIGHT_EDITOR_TEXT_LAYER_MODE = []

DEFAULT_LAYER_TEXT = []


