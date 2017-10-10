from PySide2.QtCore import QEvent
from PySide2.QtGui import QColor
from PySide2.QtGui import QImage
from PySide2.QtWidgets import QStyleOptionButton
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QAbstractButton
from PySide2.QtWidgets import QToolTip
from PySide2.QtGui import QPixmap
from PySide2.QtGui import QPainter
from PySide2.QtCore import QSize
from PySide2.QtWidgets import QStyle
from PySide2.QtGui import QIcon

class RenderSetupButton(QAbstractButton):
    """
    This class represents a render setup button which is an icon button that produces a brighter version of the icon when hovered over.
    """
    
    
    
    def __init__(self, parent, icon, size=20.0):
        pass
    
    
    def drawControl(self, element, option, painter, widget=None):
        """
        Draws the icon button
        """
    
        pass
    
    
    def enterEvent(self, event):
        pass
    
    
    def event(self, event):
        pass
    
    
    def generatedIconPixmap(self, iconMode, pixmap, option):
        """
        Draws the icon button brighter when hovered over.
        """
    
        pass
    
    
    def leaveEvent(self, event):
        pass
    
    
    def paintEvent(self, e):
        """
        Draws the render setup button
        """
    
        pass
    
    
    def sizeHint(self):
        pass
    
    
    ADJUSTMNET = 50
    
    
    DEFAULT_BUTTON_SIZE = 20.0
    
    
    HIGH_LIMIT = 205
    
    
    LOW_LIMIT = 30
    
    
    MAX_VALUE = 255
    
    
    staticMetaObject = None



def qRgba(*args, **kwargs):
    pass


def qAlpha(*args, **kwargs):
    pass



