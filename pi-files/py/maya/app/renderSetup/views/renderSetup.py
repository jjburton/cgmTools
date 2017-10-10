class SelectionObserver(object):
    def __init__(self, selectionModel):
        pass
    
    
    def selectionChanged(self, selected, deselected):
        """
        Notify render setup selection observers.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def renderSetupWindowChanged():
    pass


def saveWindowState(editor, optionVar):
    pass


def renderSetupWindowDestroyed(object=None):
    pass


def propertyEditorClosed():
    pass


def renderSetupWindowClosed():
    pass


def windowClosed(editor):
    pass


def createUI(restore=False):
    """
    # Sets up up the render layers UI
    """

    pass


def propertyEditorDestroyed(object=None):
    pass


def propertyEditorChanged():
    pass



propertyEditor = None

renderSetupWindow = propertyEditor
selectionObserver = propertyEditor

