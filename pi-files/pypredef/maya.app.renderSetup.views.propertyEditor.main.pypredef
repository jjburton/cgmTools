from maya.app.renderSetup.views.propertyEditor.renderLayer import *
from maya.app.renderSetup.views.renderSetupButton import *

from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QMenu
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QPen
from copy import deepcopy
from maya.app.renderSetup.views.propertyEditor.staticCollection import StaticCollection
from maya.app.renderSetup.views.frameLayout import TitleFrame
from maya.app.renderSetup.views.baseDelegate import BaseDelegate
from PySide2.QtGui import QFontMetrics
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QStyleOptionViewItem
from PySide2.QtWidgets import QWidgetItem
from PySide2.QtWidgets import QStyledItemDelegate
from maya.app.renderSetup.views.propertyEditor.collection import Collection
from PySide2.QtWidgets import QAbstractItemView
from maya.app.renderSetup.views.propertyEditor.override import Override
from maya.app.renderSetup.views.propertyEditor.expressionLabels import ExcludeExpressionLabel
from maya.app.general.mayaMixin import MayaQDockWidget
from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QStandardItem
from PySide2.QtGui import QAbstractTextDocumentLayout
from maya.app.renderSetup.views.propertyEditor.expressionLabels import IncludeExpressionLabel
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCore import QItemSelectionModel
from maya.app.renderSetup.views.frameLayout import FrameLayout
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QScrollArea
from PySide2.QtWidgets import QDockWidget
from PySide2.QtWidgets import QShortcut
from maya.app.renderSetup.views.propertyEditor.lightsCollection import LightsCollection
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QTextEdit
from PySide2.QtCore import QTimer
from maya.app.renderSetup.views.renderSetupDelegate import RenderSetupDelegate
from maya.app.renderSetup.views.frameLayout import Frame
from PySide2.QtCore import QPoint
from PySide2.QtWidgets import QListWidget
from PySide2.QtCore import QItemSelection
from PySide2.QtWidgets import QSpacerItem
from maya.app.renderSetup.views.propertyEditor.collectionFilterLineEdit import CollectionFilterLineEdit
from maya.app.renderSetup.views.baseDelegate import createPixmap
from PySide2.QtWidgets import QFrame
from maya.app.renderSetup.views.frameLayout import CollapsibleArrowAndTitle
from PySide2.QtCore import QRect
from PySide2.QtGui import QPalette
from PySide2.QtCore import QPointF
from PySide2.QtGui import QTextDocument
from maya.app.renderSetup.views.propertyEditor.collectionStaticSelectionWidget import HTMLDelegate
from PySide2.QtWidgets import QHBoxLayout
from maya.app.renderSetup.views.propertyEditor.collectionStaticSelectionWidget import CollectionStaticSelectionWidget
from PySide2.QtCore import QObject
from PySide2.QtWidgets import QComboBox
from maya.app.renderSetup.views.frameLayout import NameLineEdit
from PySide2.QtGui import QTextOption
from PySide2.QtCore import Slot
from PySide2.QtGui import QFont
from PySide2.QtCore import QPersistentModelIndex
from functools import partial
from PySide2.QtWidgets import QCheckBox
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2.QtWidgets import QAction
from PySide2.QtGui import QCursor

class PropertyEditor(MayaQWidgetDockableMixin, QWidget):
    """
    This class represents the property editor which displays the selected render setup item's property information.
    
    
    Note: The Qt should never called any 'deferred' actions because all the design is based on synchronous notifications
          and any asynchronous events will change the order of execution of these events.
    
          For example when the selection in the Render Setup Window is changed (so the Property Editor must be updated). 
          The delete must be synchronous on the 'unselected' layouts otherwise they will be updated along with selected ones. 
          The two main side effects are that lot of unnecessary processings are triggered (those one the deleted layouts) 
          and the infamous 'C++ already deleted' issue appears because the Data Model & Qt Model objects were deleted 
          but not their corresponding Layout (instance used by the Property Editor to display a render setup object).
    """
    
    
    
    def __del__(self):
        pass
    
    
    def __init__(self, treeView, parent):
        pass
    
    
    def dispose(self):
        pass
    
    
    def itemChanged(self, item):
        """
        When an item in the model changes, update the control and 
        frameLayout that make use of that item (if one exists).
        """
    
        pass
    
    
    def minimumSizeHint(self):
        pass
    
    
    def populateFields(self, item):
        pass
    
    
    def rebuild(self):
        """
        regenerate our collection/override/layer controls.
        """
    
        pass
    
    
    def renderSetupAdded(self):
        """
        RenderSetup node was created
        """
    
        pass
    
    
    def renderSetupPreDelete(self):
        """
        RenderSetup node is about to be deleted
        """
    
        pass
    
    
    def selectionChanged(self, selected, deselected):
        """
        On selection changed we lazily regenerate our collection/override/layer 
        controls.
        """
    
        pass
    
    
    def setSizeHint(self, size):
        pass
    
    
    def sizeHint(self):
        pass
    
    
    def triggerRebuild(self):
        pass
    
    
    def triggerRepopulate(self, item):
        pass
    
    
    MINIMUM_SIZE = None
    
    
    PREFERRED_SIZE = None
    
    
    staticMetaObject = None


class PropertyEditorScrollArea(QScrollArea):
    def sizeHint(self):
        pass
    
    
    STARTING_SIZE = None
    
    
    staticMetaObject = None



def getCppPointer(*args, **kwargs):
    pass



kFiltersToolTip = []

kStaticSelectTooltipStr = []

kDragDropFilter = []

kExpressionTooltipStr1 = []

kInclude = []

kInverse = []

kStaticRemoveTooltipStr = []

kIncludeHierarchyTooltipStr = []

kAdd = []

kInvalidAttribute = []

kExpressionTooltipStr = []

kCreateExpression = []

kExpressionSelectTooltipStr = []

kRemove = []

kByTypeFilter = []

kLayer = []

kAddOverride = []

kSelectAll = []

kStaticAddTooltipStr = []

kDragAttributeFromAE = []

kCollectionFilters = []

kIncompatibleAttribute = []

kAddToCollection = []

kExpressionTooltipStr3 = []

kIncludeHierarchy = []

kSelect = []

kExpressionTooltipStr4 = []

kAddOverrideTooltipStr = []

kRelativeWarning = []

kExpressionTooltipStr2 = []

kDragAttributesFromAE = []


