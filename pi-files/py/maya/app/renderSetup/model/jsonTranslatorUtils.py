"""
Please have a look to http://json.org/ for the detailed Json syntax
and the official documentation is http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf
"""

class MergePolicy(object):
    """
    The class is the policy to manage a new object instance when decoding a list 
    of render setup object depending of the mer type.
    """
    
    
    
    def __init__(self, getFn, createFn, mergeType, prependToName):
        pass
    
    
    def create(self, dict, typeName):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def _isRenderSetup(encodedData):
    pass


def getObjectNotes(encodedData):
    """
    Get the Notes from any Render Setup Object knowing that all nodes
    could or not contain the 'notes' dynamic attribute.
    """

    pass


def decodeObjectArray(list, policy):
    """
    Decode an array of Render Setups Objects
    
    list is a list of dictionaries (json representation for a array of objects)
    policy encapsulates the behavior to create the render setup object instance based on the merge type
    """

    pass


def encodeObjectArray(objects):
    """
    Encode an array of Render Setups Object as a list for the Json default encoder
    """

    pass


def isRenderSetupTemplate(encodedData):
    pass


def getTypeNameFromDictionary(encodedData):
    """
    Get the root typename stored in the dictionary
    Note: Any node encoding always first encapsulates its data in a dictionary
          where the key is the node type.
    """

    pass


def isRenderSetup(encodedData):
    """
    Is the encodedData defining a Render Setup ?
    Note: The test is not foolproof but should segregate obvious unrelated data
    """

    pass



