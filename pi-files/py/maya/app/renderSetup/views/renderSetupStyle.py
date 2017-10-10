from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QCommonStyle
from PySide2.QtGui import QPen
from PySide2.QtGui import QColor
from PySide2.QtCore import Qt
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import QStyle

class RenderSetupStyle(QCommonStyle):
    """
    This class defines the RenderSetup style and is only used when style sheets and the delegate are not sufficient.
    """
    
    
    
    def __init__(self, parent):
        pass
    
    
    def drawComplexControl(self, control, option, painter, widget=None):
        pass
    
    
    def drawControl(self, element, option, painter, widget=None):
        pass
    
    
    def drawItemPixmap(self, painter, rectangle, alignment, pixmap):
        pass
    
    
    def drawItemText(self, painter, rectangle, alignment, palette, enabled, text, textRole=PySide2.QtGui.QPalette.ColorRole.NoRole):
        pass
    
    
    def drawPrimitive(self, element, option, painter, widget=None):
        """
        Draws the given primitive element with the provided painter using the style options specified by option.
        """
    
        pass
    
    
    def generatedIconPixmap(self, iconMode, pixmap, option):
        pass
    
    
    def hitTestComplexControl(self, control, option, position, widget=None):
        pass
    
    
    def itemPixmapRect(self, rectangle, alignment, pixmap):
        pass
    
    
    def itemTextRect(self, metrics, rectangle, alignment, enabled, text):
        pass
    
    
    def pixelMetric(self, metric, option=None, widget=None):
        pass
    
    
    def polish(self, *args, **kwargs):
        pass
    
    
    def sizeFromContents(self, ct, opt, contentsSize, widget=None):
        pass
    
    
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        pass
    
    
    def subControlRect(self, control, option, subControl, widget=None):
        pass
    
    
    def subElementRect(self, element, option, widget=None):
        pass
    
    
    def unpolish(self, *args, **kwargs):
        pass
    
    
    DROP_INDICATOR_COLOR = None
    
    
    DROP_INDICATOR_LEFT_OFFSET = -25.0
    
    
    DROP_INDICATOR_WIDTH = 3.0
    
    
    staticMetaObject = None



