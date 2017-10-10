"""
Helper methods for handling assembly initial representation.
Called from the sceneAssembly plug-in code.
"""

class assemblyReferenceInitialRep:
    """
    This utility class is invoked by the sceneAssembly plug-in to manage
    the save, restore and query of the initial representation information
    for scene assemblies.  An assembly's initial representation is the
    representation that will be activated when the assembly is first loaded.
    
    Each top level scene assembly node will remember the active configuration
    of its hierarchy at the time it is saved.  When the assembly is re-opened,
    the stored configuration will be used to restore this state.
    
    The interface to this class is defined by the following methods:
    
       writer(): will create an initialRep definition on a top level assembly
       This is based on the current activiation state of the assembly hierarchy
       when the method is called.  The scene assembly plug-in will call
       the writer() method just before file save.  
       
       reader(): will load in an initialRep definition from a top level assembly.
       The data loaded will be used by subsequent calls to getInitialRep for the
       assemblies in its hierarchy. The scene assembly plug-in will invoke
       the reader() as part of the top level assembly's postLoad routine.  
       
       getInitialRep(): queries the initialRep data currently available for a given
       assembly.  The routine uses the data that was stored on the associated top
       level assembly, and loaded in by the reader() method.  The scene assembly plug-in
       will use the initialRep information to determine the initial activation
       state of the subassembly when it is first loaded. 
       
       clear(): will clear the initialRep definition for a top level assembly.
       Subsequent calls to getInitialRep() will return emtpy values.
       The scene assembly plug-in will call clear() when the initial representation
       data for a top level assembly is no longer required (after all assemblies in its
       hierarchy have finished activating).
       
    Internally the initialRep information is stored in a hierarchical
    python dictionary, which has nested entries corresponding to the
    assembly hierarchy. 
    
    The dictionary is persisted using a JSON structure which can be readily mapped
    to the internal python dictionary structure.
    The JSON structure is stored as string data on the 'initialRep' attribute on
    top level assembly nodes.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def clear(self, rootAssemblyName):
        """
        Remove the initialRep data associated with the 
        specified root assembly
        """
    
        pass
    
    
    def getInitialRep(self, targetAssemblyName):
        """
        Get the initialRep data associated with the 
        specified target assembly
        """
    
        pass
    
    
    def reader(self, rootAssemblyName):
        """
        Given a top level assembly, read the initialRep data
        for its hierarchy of subassemblies (stored in an
        attribute on the node).  The data is loaded into a
        dictionary and can be accessed by calls to the getInitialRep
        method.  
        Each call to reader() will reset and replace any previously
        stored data for this root assembly.
        If the data is no longer required, it can also be removed by
        calling clear() directly.
        """
    
        pass
    
    
    def writer(self, rootAssemblyName):
        """
        Given a top level assembly, format the initialRep data for
        its hierarchy of subassemblies and store it in the
        initialRep attribute on the top level assembly node.
        """
    
        pass
    
    
    def className():
        pass
    
    
    def enableDebugOutput(value):
        """
        Enable or disable debug output
        """
    
        pass
    
    
    initialRepDictionaries = {}
    
    
    kRepKey = 'rep'
    
    
    kSubKey = 'sub'
    
    
    kWantDebugOutput = False



