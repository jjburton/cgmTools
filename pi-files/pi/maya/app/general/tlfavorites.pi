from functools import partial

class TLFavoriteStore(object):
    """
    Manages syncing treeLister favorites to a file
    """
    
    
    
    def __init__(self, fname):
        pass
    
    
    def attachClient(self, lister):
        """
        Add a treeLister instance as a client of this favorites store.
        Any changes from the lister will propagate to other clients.
        """
    
        pass
    
    
    def get(self):
        """
        returns the list of favorites
        """
    
        pass
    
    
    def removeClient(self, lister):
        pass
    
    
    def update(self, lister, path, isAdded):
        """
        updates the persistant favorite store 
        
        lister  - name of the treeLister which has added/removed the favorite
        path    - item path to be updated
        isAdded - True means add to store, False means remove
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def addPath(path, key):
    """
    Add a path to key pair.
    """

    pass


def detachStore(lister):
    """
    Disconnects the given tree lister from the favorites store.  The
    lister will no longer be updated when the store changes.
    """

    pass


def attachStore(lister, fpath):
    """
    Connects the TLFavoriteStore instance for the specified file path
    to the specified tree lister.  Populates the treeLister with the
    stored favorites.
    
    lister   - the treeLister 
    fpath    - full path to the favorites file
    """

    pass


def readFavorites(fname):
    """
    returns the favorites from the specified file 
    as a MEL-friendly flattened list 
    ["path","key","path2","key2",...]
    """

    pass



_header = '# This file contains favorites for a treeLister.\n# To work with renderCreateBarUI it must python eval() to a list of\n# 2-tuples of strings [(u"path","nodeType")]\n'

_pathToStoredKey = {}

_storesByFilename = {}


