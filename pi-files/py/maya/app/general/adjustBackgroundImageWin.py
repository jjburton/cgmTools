class TselectionWin(object):
    """
    Base class for a dialog which works on the user's selection
    """
    
    
    
    def __del__(self):
        pass
    
    
    def __init__(self, title, selectionFilter='<function <lambda>>', objects=[]):
        """
        selectionFilter - function which returns True if object is selectable
        """
    
        pass
    
    
    def activate(self, window):
        """
        Call this method once the window is created
        """
    
        pass
    
    
    def close(self):
        pass
    
    
    def getWindowTitle(self):
        pass
    
    
    def onSelectionChanged(self, *args):
        """
        Called anytime the selection list changes,
        self.objects is updated and window title is updated.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class TadjustBackgroundImageWin(TselectionWin):
    """
    Adjust the background image for a container Dialog
    """
    
    
    
    def __init__(self, editor):
        pass
    
    
    def hyperGraphCmd(self, *args, **kwargs):
        pass
    
    
    def loadImage(self, theFile):
        pass
    
    
    def onAdjustImagePositionHorizontal(self, val):
        pass
    
    
    def onAdjustImagePositionVertical(self, val):
        pass
    
    
    def onAdjustImageScale(self, val):
        pass
    
    
    def onFitToHeight(self, arg):
        pass
    
    
    def onFitToWidth(self, arg):
        pass
    
    
    def onImageFieldChange(self, val):
        pass
    
    
    def onLoadImage(self):
        pass
    
    
    def onSelectionChanged(self, *args):
        """
        override selection callback
        """
    
        pass
    
    
    def show(self):
        """
        Build and show the dialog
        """
    
        pass
    
    
    def update(self):
        """
        update the ui after something has changed
        """
    
        pass



def adjustBackgroundImageWin(editor):
    """
    Main entry point.  Create and show the adjust-background-image dialog.
    """

    pass



