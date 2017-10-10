from maya.app.renderSetup.views.baseDelegate import *

from PySide2.QtWidgets import QFrame
from PySide2.QtGui import QTextOption
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QHBoxLayout

class Frame(QFrame):
    def __init__(self, item, parent):
        pass
    
    
    staticMetaObject = None


class NameLineEdit(QLineEdit):
    """
    This class is used to display the editable name associated with a 
    collection, layer, or override.
    """
    
    
    
    def __init__(self, item, parent):
        pass
    
    
    def focusInEvent(self, event):
        pass
    
    
    def focusOutEvent(self, event):
        pass
    
    
    def keyPressEvent(self, event):
        pass
    
    
    def nameChanged(self):
        pass
    
    
    def paintEvent(self, event):
        pass
    
    
    staticMetaObject = None


class FrameLayout(QFrame):
    """
    This class defines the FrameLayout which emulates the behaviour of the Maya Python API's maya.cmds.frameLayout function. 
     The only difference is that the render setup version also provides a color bar and background color to differentiate layers, 
     collections, and overrides.
    """
    
    
    
    def __init__(self, item, parent):
        pass
    
    
    def addWidget(self, widget):
        pass
    
    
    def getWidget(self, index):
        pass
    
    
    def initContentFrame(self):
        pass
    
    
    def initFrameLayout(self):
        pass
    
    
    def initMainLayout(self):
        pass
    
    
    def initTitleFrame(self):
        pass
    
    
    def toggleCollapsed(self):
        """
        When the title frame is clicked, this function is called to toggle the collapsed state
        """
    
        pass
    
    
    staticMetaObject = None


class TitleFrame(Frame):
    """
    This class defines the frame for the FrameLayout
    """
    
    
    
    def __init__(self, item, parent):
        pass
    
    
    def mousePressEvent(self, event):
        pass
    
    
    def paintEvent(self, e):
        """
        Draws the disabled or enabled title frame background.
        """
    
        pass
    
    
    FRAME_HEIGHT = 28.0
    
    
    clicked = None
    
    
    staticMetaObject = None


class CollapsibleArrowAndTitle(Frame):
    """
    This class defines the arrow used for a FrameLayout
    """
    
    
    
    def __init__(self, item, parent):
        pass
    
    
    def paintEvent(self, e):
        """
        Draws the color bar and arrow
        """
    
        pass
    
    
    def setArrow(self, isCollapsed):
        """
        Sets the arrow direction
        """
    
        pass
    
    
    ARROW_COLOR = None
    
    
    COLLAPSED_ARROW_OFFSET = 13.0
    
    
    COLOR_BAR_HEIGHT = 28.0
    
    
    COLOR_BAR_WIDTH = 7.0
    
    
    EXPANDED_ARROW_OFFSET = 10.0
    
    
    HEIGHT = 28.0
    
    
    NODE_TYPE_TEXT_RECT = None
    
    
    WIDTH = 33.0
    
    
    staticMetaObject = None



