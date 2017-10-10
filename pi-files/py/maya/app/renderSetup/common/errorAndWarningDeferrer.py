class ErrorAndWarningDeferrer:
    """
    # Note: this class was introduced as a work around. The problem is that the 
    # render setup plugin is being loaded in loadPreferredRenderGlobalsPreset,
    # and at that point, no warnings/errors can be displayed, so we decided to
    # queue up the warnings/errors for display when the render setup window was
    # opened.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def displayErrorsAndWarnings(self, clearLog=True):
        pass
    
    
    def registerError(self, error):
        pass
    
    
    def registerWarning(self, warning):
        pass



def instance():
    pass



_instance = None


