"""
Contains the Logger class. Creates an interface to log errors, warnings,
debugging, and log messages that allows for indented nesting.
"""

class Logger(object):
    """
    Utility class to allow printing of errors, warnings, and logger with the
    ability to silence everything. The logger are tagged with a prefix that
    lets you easily tell what kind of logger they are.
    """
    
    
    
    def __init__(self, debugging=False, file_name=None):
        """
        Create the Logger object with an initial output state.
        
        file_name: If not None then the output will go to the named file
        debugging: If True then output debugging and log messages.
                   Default is just to print errors and warnings.
        """
    
        pass
    
    
    def debug(self, message):
        """
        Print out a message flagged as debugging information
        """
    
        pass
    
    
    def error(self, message):
        """
        Print out a message as an error
        """
    
        pass
    
    
    def indent(self, indent_change=1):
        """
        Change the indentation level for the output
        """
    
        pass
    
    
    def log(self, message):
        """
        Print out a message as information
        """
    
        pass
    
    
    def warning(self, message):
        """
        Print out a message as a warning
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



