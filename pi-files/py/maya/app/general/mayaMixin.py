"""
* MayaQWidgetBaseMixin      Mixin that should be applied to all custom QWidgets created for Maya
                            to automatically handle setting the objectName and parenting
                            
* MayaQWidgetDockableMixin  Mixin that adds dockable capabilities within Maya controlled with
                            the show() function
"""

from PySide2.QtWidgets import *
from PySide2.QtGui import *

from PySide2.QtCore import QPoint
from PySide2.QtCore import QSize
from PySide2.QtCore import Qt
from PySide2.QtCore import Signal

class MayaQWidgetBaseMixin(object):
    """
    Handle common actions for Maya Qt widgets during initialization:
        * auto-naming a Widget so it can be looked up as a string through
          maya.OpenMayaUI.MQtUtil.findControl()
        * parenting the widget under the main maya window if no parent is explicitly
          specified so not to have the Window disappear when the instance variable
          goes out of scope
    
    Integration Notes:
        Inheritance ordering: This class must be placed *BEFORE* the Qt class for proper execution
        This is needed to workaround a bug where PyQt/PySide does not call super() in its own __init__ functions
    
    Example:
        class MyQWidget(MayaQWidgetBaseMixin, QPushButton):
            def __init__(self, parent=None):
                super(MyQWidget, self).__init__(parent=parent)
                self.setText('Push Me')
        myWidget = MyQWidget()
        myWidget.show()
        print myWidget.objectName()
    """
    
    
    
    def __init__(self, parent=None, *args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class MayaQDockWidget(MayaQWidgetBaseMixin, QDockWidget):
    """
    QDockWidget tailored for use with Maya.
    Mimics the behavior performed by Maya's internal QMayaDockWidget class and the dockControl command
    
    :Signals:
        closeEventTriggered: emitted when a closeEvent occurs
    
    :Known Issues:
        * Manually dragging the DockWidget to dock in the Main MayaWindow will have it resize to the 'sizeHint' size
          of the child widget() instead of preserving its existing size.
    """
    
    
    
    def __init__(self, parent=None, *args, **kwargs):
        pass
    
    
    def closeEvent(self, evt):
        """
        Hide the QDockWidget and trigger the closeEventTriggered signal
        """
    
        pass
    
    
    def moveEvent(self, event):
        pass
    
    
    def resizeEvent(self, event):
        pass
    
    
    def setArea(self, area):
        """
        Set the docking area
        """
    
        pass
    
    
    closeEventTriggered = None
    
    
    staticMetaObject = None
    
    
    windowStateChanged = None


class MayaQWidgetDockableMixin(MayaQWidgetBaseMixin):
    """
    Handle Maya dockable actions controlled with the show() function.
    
    Integration Notes:
        Inheritance ordering: This class must be placed *BEFORE* the Qt class for proper execution
        This is needed to workaround a bug where PyQt/PySide does not call super() in its own __init__ functions
    
    Example:
        class MyQWidget(MayaQWidgetDockableMixin, QPushButton):
            def __init__(self, parent=None):
                super(MyQWidget, self).__init__(parent=parent)
                self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred )
                self.setText('Push Me')
        myWidget = MyQWidget()
        myWidget.show(dockable=True)
        myWidget.show(dockable=False)
        print myWidget.showRepr()
    """
    
    
    
    def dockArea(self):
        """
        Return area if the widget is currently docked to the Maya MainWindow
        Will return None if not dockable
        
        :Return: str
        """
    
        pass
    
    
    def dockCloseEventTriggered(self):
        """
        Triggered when QDockWidget.closeEventTriggered() signal is triggered.
        Stub function.  Override to perform actions when this happens.
        """
    
        pass
    
    
    def floatingChanged(self, isFloating):
        """
        Triggered when QDockWidget.topLevelChanged() signal is triggered.
        Stub function.  Override to perform actions when this happens.
        """
    
        pass
    
    
    def hide(self, *args, **kwargs):
        """
        Hides the widget.  Will hide the parent widget if it is a QDockWidget.
        Overrides standard QWidget.hide()
        """
    
        pass
    
    
    def isDockable(self):
        """
        Return if the widget is currently dockable (under a QDockWidget)
        
        :Return: bool
        """
    
        pass
    
    
    def isFloating(self):
        """
        Return if the widget is currently floating (under a QDockWidget)
        Will return True if is a standalone window OR is a floating dockable window.
        
        :Return: bool
        """
    
        pass
    
    
    def raise_(self):
        """
        Raises the widget to the top.  Will raise the parent widget if it is a QDockWidget.
        Overrides standard QWidget.raise_()
        """
    
        pass
    
    
    def setDockableParameters(self, dockable=None, floating=None, area=None, allowedArea=None, width=None, height=None, x=None, y=None, save=None, module=None, plugins=None, uiScript=None, *args, **kwargs):
        """
        Set the dockable parameters.
        
        :Parameters:
            dockable (bool)
                Specify if the window is dockable (default=False)
            floating (bool)
                Should the window be floating or docked (default=True)
            area (string)
                Default area to dock into (default='left')
                Options: 'top', 'left', 'right', 'bottom'
            allowedArea (string)
                Allowed dock areas (default='all')
                Options: 'top', 'left', 'right', 'bottom', 'all'
            width (int)
                Width of the window
            height (int)
                Height of the window
            x (int)
                left edge of the window
            y (int)
                top edge of the window
                
        :See: show(), hide(), and setVisible()
        """
    
        pass
    
    
    def setSizeHint(self, size):
        """
        Virtual method used to pass the user settable width and height down to the widget whose 
        size policy controls the actual size most of the time.
        """
    
        pass
    
    
    def setVisible(self, makeVisible, *args, **kwargs):
        """
        Show/hide the QWidget window.  Overrides standard QWidget.setVisible() to pass along additional arguments
        
        :See: show() and hide()
        """
    
        pass
    
    
    def setWindowTitle(self, val):
        """
        Sets the QWidget's title and also it's parent QDockWidget's title if dockable.
        
        :Return: None
        """
    
        pass
    
    
    def show(self, *args, **kwargs):
        """
        Show the QWidget window.  Overrides standard QWidget.show()
        
        :See: setDockableParameters() for a list of parameters
        """
    
        pass
    
    
    def showRepr(self):
        """
        Present a string of the parameters used to reproduce the current state of the
        widget used in the show() command.
        
        :Return: str
        """
    
        pass
    
    
    closeEventTriggered = None
    
    
    windowStateChanged = None



def wrapInstance(*args, **kwargs):
    pass



_qtImported = 'PySide2'


