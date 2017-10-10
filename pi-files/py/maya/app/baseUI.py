class StandardInput:
    """
    Implements a basic user interface for Python sys.stdin
    
    When a Python call tries to read from sys.stdin in Maya's interactive GUI
    mode, then this object will receive the read call and present the user
    with a basic modal UI that will let them respond to the request for input
    """
    
    
    
    def read(self):
        """
        Read a line of input.  This will prompt the user for multiple 
        lines of input
        """
    
        pass
    
    
    def readline(self):
        """
        Read a line of input.  This will prompt the user for a single line of
        input
        """
    
        pass



