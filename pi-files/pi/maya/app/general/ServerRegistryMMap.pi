"""
Provides an interface to the commandPort mmap registry file which is used to 
keep track of commandPorts on Windows.
"""

class ServerRegistryMMap:
    """
    Windows only, manage the server registry mmap file.  This maps command 
    port names to port numbers. Is not intended to be used between 
    Maya instances.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def __str__(self):
        pass
    
    
    def addServer(self, serverName, port):
        """
        Add a new server record to the file
        """
    
        pass
    
    
    def findServer(self, serverName):
        """
        Returns the index of the server name if it is already in the file
        otherwise return -1
        """
    
        pass
    
    
    def firstFreeSlot(self):
        """
        Returns the first free slot, or None on failure
        """
    
        pass
    
    
    def getBitmap(self):
        """
        Gets the active server bitmap
        """
    
        pass
    
    
    def getServer(self, i):
        """
        Gets the ith server record, name is padded with zeros to 108 bytes
        """
    
        pass
    
    
    def offsetToRecord(self, i):
        """
        returns the byte offset to the ith record
        """
    
        pass
    
    
    def removeServer(self, serverName):
        """
        remove a server from the file
        Returns True on success, False otherwise
        """
    
        pass
    
    
    def servers(self):
        """
        Get the list of active servers
        """
    
        pass
    
    
    def setBitmap(self, bitmap):
        """
        Updates the active server bitmap
        """
    
        pass
    
    
    def setServer(self, i, serverName, port):
        """
        Updates the ith server record
        """
    
        pass
    
    
    instance = None



def getInstance():
    """
    ServerRegistryMMap is a singleton class, the mmap file is opened when the instance is
    created and it is not closed until this module is removed from memory (Maya exit).
    Any instances of which start up after this one will then be able to see the contents of
    the file.
    
    Returns the ServerRegistryMMap singleton
    """

    pass


def registerServer(serverName, addrFamily):
    """
    Allocate and register a server mapping for the supplied name. 
    Note: Only used on MS Windows, other platforms can use a normal socket file.
    
    serverName - ie 'commandPort1'
    addrFamily - socket.AF_*
    Returns (host,port) for the corresponding INET server
    """

    pass



