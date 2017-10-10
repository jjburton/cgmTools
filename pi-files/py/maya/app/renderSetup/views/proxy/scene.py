from PySide2.QtCore import *

from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QStandardItemModel
from PySide2.QtWidgets import QFileDialog
from PySide2.QtGui import QColor
from PySide2.QtGui import QGuiApplication
from PySide2.QtGui import QStandardItem

import maya.app.renderSetup.views.pySide.standardItem as standardItem

class ModelProxyItem(standardItem.StandardItem):
    def __init__(self, name):
        pass
    
    
    def addActiveLayerObserver(self):
        pass
    
    
    def data(self, role):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def isActive(self):
        pass
    
    
    def onClick(self, sceneView):
        pass
    
    
    def onDoubleClick(self, sceneView):
        pass
    
    
    def removeActiveLayerObserver(self):
        pass
    
    
    def setData(self, value, role):
        pass


class SceneProxy(QStandardItemModel):
    def __del__(self):
        pass
    
    
    def __init__(self, parent=None):
        pass
    
    
    def data(self, index, role):
        pass
    
    
    def dispose(self):
        pass
    
    
    def flags(self, index):
        pass
    
    
    def refreshModel(self):
        pass
    
    
    def resetModel(self):
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass
    
    
    staticMetaObject = None


class SceneItemProxyItem(ModelProxyItem):
    def __init__(self, name):
        pass
    
    
    def data(self, role):
        pass


class SceneProxyItem(ModelProxyItem):
    def __init__(self, name):
        pass
    
    
    def data(self, role):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def setData(self, value, role):
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass


class SceneRenderSettingsProxyItem(SceneItemProxyItem):
    def __init__(self, name):
        pass
    
    
    def data(self, role):
        pass
    
    
    def defaultRenderGlobalsChanged(self, msg, mplug, otherMplug, clientData):
        pass
    
    
    def dispose(self):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def isActive(self):
        pass
    
    
    def onDoubleClick(self, sceneView):
        pass
    
    
    def refresh(self, imposeRefresh):
        pass
    
    
    def reset(self):
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass


class SceneAovsProxyItem(SceneItemProxyItem):
    def __init__(self, name):
        pass
    
    
    def data(self, role):
        pass
    
    
    def getActionButton(self, column):
        pass
    
    
    def getActionButtonCount(self):
        pass
    
    
    def onDoubleClick(self, sceneView):
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass


class SceneCamerasProxyItem(SceneItemProxyItem):
    def __init__(self, name):
        pass
    
    
    def data(self, role):
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass


class SceneLightProxyItem(SceneItemProxyItem):
    def __init__(self, name):
        pass
    
    
    def data(self, role):
        pass
    
    
    def isActive(self):
        pass
    
    
    def onDoubleClick(self, sceneView):
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass


class SceneSelectionSetsProxyItem(SceneItemProxyItem):
    def __init__(self, name):
        pass
    
    
    def data(self, role):
        pass
    
    
    def type(self):
        pass
    
    
    def typeIdx(self):
        pass



SELECTION_SETS_STR = []

NODE_VISIBLE = 258

DEFAULT_PRESET_ACTION = []

SCENE_CATEGORY_LIGHTS_TYPE_IDX = 4

AOVS_STR = []

SCENE_CATEGORY_TYPE = 1001

NODE_FRAME_ANIMATION = 261

LIGHTS_STR = []

SCENE_CATEGORY_CAMERAS_TYPE_IDX = 3

CAMERAS_STR = []

NODE_START_FRAME = 259

SCENE_CATEGORY_RENDER_SETTINGS_TYPE_IDX = 2

GLOBAL_PRESETS_ACTION = []

SCENE_CATEGORY_CAMERAS_TYPE = 1003

AOVS_MENU = []

SCENE_CATEGORY_AOVS_TYPE = 1005

NODE_END_FRAME = 260

SCENE_CATEGORY_SELECTION_SETS_TYPE_IDX = 6

EXPAND_COLLAPSE_ACTION = []

SCENE_CATEGORY_TYPE_IDX = 1

USER_PRESETS_ACTION = []

RS_DEFAULT_RENDER_GLOBALS = 'defaultRenderGlobals'

EXPORT_CURRENT_ACTION = []

SCENE_CATEGORY_RENDER_SETTINGS_TYPE = 1002

MAX_TYPE_IDX = 8

RS_INVALID_NODE_NAME = []

NODE_RENDERABLE = 262

SET_RENDERABLE_ACTION = []

ROW_HEIGHT = 30

SCENE_CATEGORY_LIGHTS_TYPE = 1004

SCENE_CATEGORY_AOVS_TYPE_IDX = 5

PRESET_MENU = []

NODE_TYPE = 256

SET_VISIBILITY_ACTION = []

SCENE_STR = []

SCENE_CATEGORY_SELECTION_SETS_TYPE = 1006

RS_END_FRAME = 'endFrame'

RS_START_FRAME = 'startFrame'

SCENE_TYPE_IDX = 0

RS_ANIMATION = 'animation'

NODE_ACTIVE_FRAME = 263

SCENE_TYPE = 1000

NODE_ACCEPTS_DRAG = 257

RENDER_SETTINGS_STR = []


