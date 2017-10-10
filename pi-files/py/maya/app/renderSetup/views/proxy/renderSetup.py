"""
This file contains all the classes which implement the Qt Model needed to benefit from the
Model/View design from Qt.

The intent is that these classes only forward any requests from the View(s) to the Data Model
without any assumptions or interpretations.
"""

from PySide2.QtCore import *

from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QStandardItemModel
from PySide2.QtGui import QFontMetrics
from PySide2.QtGui import QColor
from PySide2.QtGui import QGuiApplication
from PySide2.QtGui import QFont
from functools import partial
from PySide2.QtGui import QStandardItem

class Template(object):
    """
    Base class for all the proxy classes to offer the template file import
    """
    
    
    
    def acceptableDictionaries(self, templateDirectory):
        """
        Find the list of template files applicable to a specific proxy
        """
    
        pass
    
    
    def findAllTemplateFiles(self, templateDirectory):
        """
        Find the list of all template files
        """
    
        pass
    
    
    def templateActions(self, templateDirectory):
        """
        Build the list of all possible template actions
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class DataModelListObserver(object):
    """
    Mixin class for proxy items so they can observe their underlying
    data model list.
    """
    
    
    
    def __init__(self, *args, **kwargs):
        """
        # As per
        # 
        # https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
        #
        # the signature of __init__() callee methods needs to match the caller.
        # We therefore use the most generic parameter list to accomodate the
        # needs of any other base class in the list of base classes.
        """
    
        pass
    
    
    def addActiveLayerObserver(self):
        pass
    
    
    def addListObserver(self, model):
        pass
    
    
    def ignoreListItemAdded(self):
        pass
    
    
    def listItemAdded(self, listItem):
        """
        React to list item addition to the data model.
        
        If a list item is added to the data model, we create a
        list item proxy and insert it at the proper position.
        """
    
        pass
    
    
    def listItemRemoved(self, listItem):
        """
        React to list item removal from the data model.
        
        If a list item is removed from the data model, we remove the row
        corresponding to its list item proxy.
        """
    
        pass
    
    
    def removeActiveLayerObserver(self):
        pass
    
    
    def removeListObserver(self, model):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


import maya.app.renderSetup.views.pySide.standardItem as standardItem

class ModelProxyItem(Template, standardItem.StandardItem):
    """
    # Because of MAYA-60799, QStandardItem must appear last in the list of
    # base classes.
    """
    
    
    
    def __init__(self, model):
        pass
    
    
    def data(self, role):
        pass
    
    
    def dispose(self):
        pass
    
    
    def equalsDragType(self, dragType):
        pass
    
    
    def findProxyItem(self, name):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def handleDragMoveEvent(self, event):
        pass
    
    
    def handleDropEvent(self, event, sceneView):
        pass
    
    
    def headingWidth(self, heading):
        pass
    
    
    def isActive(self):
        pass
    
    
    def isModelDirty(self):
        """
        # The next function (isModelDirty) is a workaround.
        # It should not be necessary but it is currently because we set tooltips in the treeview
        # and that triggers emitDataChanged which triggers the rebuild or repopulate of the property editor.
        # The proper fix will be to use columns in the treeview where each column has its own static tooltip
        # and the tooltips should no longer be dynamically set by the delegate (views/renderSetupDelegate.py)
        # depending on the lastHitAction
        """
    
        pass
    
    
    def modelChanged(*args, **kwargs):
        pass
    
    
    def onClick(self, view):
        pass
    
    
    def onDoubleClick(self, view):
        pass
    
    
    def setData(self, value, role):
        pass
    
    
    model = None


class RenderSetupProxy(DataModelListObserver, Template, QStandardItemModel):
    """
    # Because of MAYA-60799, QStandardItemModel must appear last in the list of
    # base classes.
    """
    
    
    
    def __eq__(self, o):
        pass
    
    
    def __init__(self, parent=None):
        pass
    
    
    def __ne__(self, o):
        pass
    
    
    def acceptImport(self):
        pass
    
    
    def attachChild(self, renderLayer, pos):
        pass
    
    
    def child(self, row, column=0):
        pass
    
    
    def createListItemProxy(self, renderLayer):
        pass
    
    
    def createRenderLayer(self, renderLayerName):
        pass
    
    
    def data(self, index, role):
        pass
    
    
    def dispose(self):
        pass
    
    
    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        pass
    
    
    def exportSelectedToFile(self, filePath, notes, proxies):
        """
        Export the selected proxies to the file
        """
    
        pass
    
    
    def findProxyItem(self, name):
        pass
    
    
    def flags(self, index):
        pass
    
    
    def importAllFromFile(self, filePath, behavior, prependToName):
        """
        Import a complete render setup from that file
        """
    
        pass
    
    
    def importTemplate(*args, **kwargs):
        pass
    
    
    def isAcceptableTemplate(self, objList):
        """
        Find if the selected filename is a template for the render setup
        """
    
        pass
    
    
    def mimeData(self, indices):
        """
        This method builds the mimeData if the selection is correct
        """
    
        pass
    
    
    def mimeTypes(self):
        pass
    
    
    def refreshModel(self):
        pass
    
    
    def renderSetupAdded(self):
        pass
    
    
    def renderSetupPreDelete(self):
        pass
    
    
    def resetModel(self):
        pass
    
    
    def supportedDropActions(self):
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass
    
    
    model = None
    
    staticMetaObject = None


class SceneItemProxy(DataModelListObserver, ModelProxyItem):
    def __init__(self, model):
        pass
    
    
    def data(self, role):
        pass


class RenderLayerProxy(DataModelListObserver, ModelProxyItem):
    """
    # Because of MAYA-60799, PySide base classes must appear last in the list of
    # base classes.
    """
    
    
    
    def __init__(self, model):
        pass
    
    
    def attachChild(self, collection, pos):
        pass
    
    
    def createCollection(self, collectionName, nodeType):
        pass
    
    
    def createListItemProxy(self, collection):
        pass
    
    
    def data(self, role):
        pass
    
    
    def delete(self):
        pass
    
    
    def dispose(self):
        pass
    
    
    def genericTypeIdx(self):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def handleDragMoveEvent(self, event):
        pass
    
    
    def handleDropEvent(self, event, sceneView):
        pass
    
    
    def importTemplate(*args, **kwargs):
        pass
    
    
    def isAcceptableTemplate(self, objList):
        """
        Find if the selected filename is a template for a render layer
        """
    
        pass
    
    
    def setData(self, value, role):
        pass
    
    
    def supportsAction(self, action, numIndexes):
        pass
    
    
    def toggleVisibilityIfVisible(self):
        """
        # MAYA-66656: this is part of a toggle visibility work around should be removed
        """
    
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass


class OverrideProxy(ModelProxyItem):
    """
    The class provides the Qt model counterpart for the Override
    """
    
    
    
    def __init__(self, model):
        pass
    
    
    def acceptsDrops(self, attribute):
        pass
    
    
    def data(self, role):
        pass
    
    
    def delete(self):
        pass
    
    
    def finalizeOverrideCreation(self, plugName):
        pass
    
    
    def genericTypeIdx(self):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def isAcceptableTemplate(self, objList):
        pass
    
    
    def setData(self, value, role):
        pass
    
    
    def supportsAction(self, action, numIndexes):
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass


class BaseCollectionProxy(DataModelListObserver, ModelProxyItem):
    """
    # Because of MAYA-60799, PySide base classes must appear last in the list of
    # base classes.
    """
    
    
    
    def __init__(self, model):
        pass
    
    
    def addToStaticSelection(self, selection):
        pass
    
    
    def attachChild(self, override, pos):
        pass
    
    
    def attachOverrideProxy(*args, **kwargs):
        pass
    
    
    def createListItemProxy(self, override):
        pass
    
    
    def createOverride(self, overrideTypeId):
        pass
    
    
    def data(self, role):
        pass
    
    
    def delete(self):
        pass
    
    
    def dispose(self):
        pass
    
    
    def genericTypeIdx(self):
        pass
    
    
    def importTemplate(*args, **kwargs):
        pass
    
    
    def isAcceptableTemplate(self, objList):
        """
        Only collections and overrides could be imported in a collection
        """
    
        pass
    
    
    def isFilteredOut(self, name):
        pass
    
    
    def isMissing(self, name):
        pass
    
    
    def listItemAdded(self, listItem):
        pass
    
    
    def listItemRemoved(self, listItem):
        pass
    
    
    def removeFromStaticSelection(self, selection):
        pass
    
    
    def setData(self, value, role):
        pass
    
    
    def staticSelection(self):
        pass
    
    
    def type(self):
        pass


class RenderSettingsCollectionProxy(BaseCollectionProxy):
    def __init__(self, model):
        pass
    
    
    def data(self, role):
        pass
    
    
    def dispose(self):
        pass
    
    
    def equalsDragType(self, dragType):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def isAcceptableTemplate(self, objList):
        pass
    
    
    def isActive(self):
        pass
    
    
    def onDoubleClick(self, view):
        pass
    
    
    def supportsAction(self, action, numIndexes):
        pass
    
    
    def typeIdx(self):
        pass


class LightsProxy(BaseCollectionProxy):
    def __init__(self, model):
        pass
    
    
    def data(self, role):
        pass
    
    
    def dispose(self):
        pass
    
    
    def equalsDragType(self, dragType):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def isAcceptableTemplate(self, objList):
        pass
    
    
    def isActive(self):
        pass
    
    
    def onDoubleClick(self, view):
        pass
    
    
    def supportsAction(self, action, numIndexes):
        pass
    
    
    def typeIdx(self):
        pass


class ConnectionOverrideProxy(OverrideProxy):
    def __init__(self, model):
        pass
    
    
    def acceptsDrops(self, attribute):
        pass
    
    
    def createAttributeUI(self, attribute):
        pass
    
    
    def data(self, role):
        pass


class RelOverrideProxy(OverrideProxy):
    def __init__(self, model):
        pass
    
    
    def createAttributeUI(self, attribute):
        pass


class LightsChildCollectionProxy(BaseCollectionProxy):
    def __init__(self, model):
        pass
    
    
    def data(self, role):
        pass
    
    
    def dispose(self):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def isAcceptableTemplate(self, objList):
        pass
    
    
    def supportsAction(self, action, numIndexes):
        pass
    
    
    def typeIdx(self):
        pass


class AbsOverrideProxy(OverrideProxy):
    def __init__(self, model):
        pass
    
    
    def createAttributeUI(self, attribute):
        pass


class CollectionProxy(BaseCollectionProxy):
    def __init__(self, model):
        pass
    
    
    def data(self, role):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def supportsAction(self, action, numIndexes):
        pass
    
    
    def typeIdx(self):
        pass
    
    
    ABSOLUTE_OVERRIDE = []
    
    
    NO_OVERRIDE = []
    
    
    RELATIVE_OVERRIDE = []


class AOVsProxy(SceneItemProxy):
    def __init__(self, model):
        pass
    
    
    def data(self, role):
        pass
    
    
    def equalsDragType(self, dragType):
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass


class CamerasProxy(SceneItemProxy):
    def __init__(self, model):
        pass
    
    
    def data(self, role):
        pass
    
    
    def equalsDragType(self, dragType):
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass


class AOVChildCollectionProxy(BaseCollectionProxy):
    """
    # Can simplify this with a common base class
    """
    
    
    
    def __init__(self, model):
        pass
    
    
    def data(self, role):
        pass
    
    
    def dispose(self):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def isAcceptableTemplate(self, objList):
        pass
    
    
    def supportsAction(self, action, numIndexes):
        pass
    
    
    def typeIdx(self):
        pass


class AOVCollectionProxy(BaseCollectionProxy):
    """
    # Can simplify this with a common base class
    """
    
    
    
    def __init__(self, model):
        pass
    
    
    def data(self, role):
        pass
    
    
    def dispose(self):
        pass
    
    
    def equalsDragType(self, dragType):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def isAcceptableTemplate(self, objList):
        pass
    
    
    def isActive(self):
        pass
    
    
    def supportsAction(self, action, numIndexes):
        pass
    
    
    def typeIdx(self):
        pass


class MaterialOverrideProxy(ConnectionOverrideProxy):
    def __init__(self, model):
        pass
    
    
    def acceptsDrops(self, attribute):
        pass
    
    
    def createAttributeUI(self, attribute):
        pass


class ShaderOverrideProxy(ConnectionOverrideProxy):
    def __init__(self, model):
        pass
    
    
    def acceptsDrops(self, attribute):
        pass
    
    
    def createAttributeUI(self, attribute):
        pass



def _createCollectionChildProxy(node):
    pass


def _createControlForAttribute(attr, attrLabel, connectable=True):
    """
    Create a UI control for the given attribute, 
    matching its type and considering if it's connectable.
    """

    pass


def getProxy(dataModel):
    """
    # Returns the UI proxy associated with the given data model object. Note that
    # the proxy opaque data is a weakref, thus the () used to access the value.
    """

    pass


def _createCollectionProxy(node):
    """
    Create the appropriate collection proxy using the node type id
    """

    pass



LIGHTS_TYPE_IDX = 6

CAMERAS_TYPE = 1005

RENAME_ACTION = []

kRelativeType = []

ALLFILTER_ACTION = []

LIGHTS_TYPE = 1006

SHADERSFILTER_ACTION = []

PROXY_OPAQUE_DATA = 'ProxyOpaqueData'

RENDER_SETTINGS_TYPE_IDX = 4

CREATE_CONNECTION_OVERRIDE_ACTION = []

RENDER_OVERRIDE_TYPE_IDX = 3

kRenderLayerWarningStr = []

SET_ISOLATE_SELECTED_ACTION = []

RENDER_SETUP_TYPE = 1000

kOverrideWarningStr = []

CAMERASFILTER_ACTION = []

LIGHTS_STR = []

kDragAndDropFailed = []

CAMERAS_STR = []

CREATE_MATERIAL_OVERRIDE_ACTION = []

TRANSFORMSFILTER_ACTION = []

RENDER_LAYER_TYPE_IDX = 1

AOVS_CHILD_COLLECTION_TYPE_IDX = 9

CREATE_COLLECTION_ACTION = []

kRelative = []

AOVS_STR = []

kAbsoluteType = []

LIGHTS_CHILD_COLLECTION_TYPE_IDX = 8

EXPAND_COLLAPSE_ACTION = []

RENDER_OVERRIDE_TYPE = 1003

CUSTOMFILTER_ACTION = []

CAMERAS_TYPE_IDX = 5

TM_SHAPES_SHADERSFILTER_ACTION = []

SET_ENABLED_ACTION = []

kAbsolute = []

COLLECTION_TYPE = 1002

NEWFILTER_ACTION = []

TM_SHAPESFILTER_ACTION = []

SET_VISIBILITY_ACTION = []

MAX_TYPE_IDX = 10

COLLECTION_TYPE_IDX = 2

AOVS_TYPE_IDX = 7

LIGHTSFILTER_ACTION = []

RENDER_SETUP_TYPE_IDX = 0

RENDER_SETTINGS_TYPE = 1004

DELETE_ACTION = []

kNoOverride = []

AOVS_TYPE = 1007

FILTER_MENU = []

SETSFILTER_ACTION = []

RENDER_LAYER_TYPE = 1001

CREATE_ABSOLUTE_OVERRIDE_ACTION = []

SHAPESFILTER_ACTION = []

SET_RENDERABLE_ACTION = []

kDragAndDrop = []

RENDER_SETUP_MIME_TYPE = 'application/renderSetup'

kSelectionTypeError = []

CREATE_RELATIVE_OVERRIDE_ACTION = []

LIGHTS_CHILD_COLLECTION_TYPE = 1008

AOVS_CHILD_COLLECTION_TYPE = 1009

CREATE_SHADER_OVERRIDE_ACTION = []

kCollectionWarningStr = []

RENDER_SETTINGS_STR = []

kRenderSettings = RENDER_SETTINGS_STR

