"""
This module wraps around Maya's internal commands and api functions
for querying polygon objects. It provides a class base abstraction to
store vertex and faces. 

The main class is polyUtilMeshQuery.  When called this class will hold
onto empty list of mesh primitives.  It must be initialized with a
Maya mesh object by calling the gatherFromMesh method.  After that
point all list objects will be populated with the current values of
the mesh at the instance in time that it was queried.

The class does not store any pointer to Maya objects in the scene. So
it acts as a container for stats on the mesh.  This can then be used
in unit tests to make comparison between mesh states or simply as a
convenient way to access the mesh data.
"""

class polyUtilMeshQuery:
    def __init__(self, state_init={}):
        """
        Main class initialization. By default, itt takes no arguments
        and simply initializes the mesh data structures to empty. However,
        callers can optionally pass in a dictionary object which is used
        to populate the data value.
        
        This class is used for some unit tests and the unit tests need
        a way to save the current polygon state, revert it back to
        that state and compare it between states. So the parameter
        above is a dictionary form of this class.  See __str__ for
        more more information.
        """
    
        pass
    
    
    def __str__(self):
        """
        Output this class in a string format.
        """
    
        pass
    
    
    def asDictionary(self):
        """
        Returns this class as a dictionary object. That is suitable
        for the initialization method of this class.
        """
    
        pass
    
    
    def gatherFromMesh(self, meshStrName, smooth=False):
        """
        Given a mesh shape name, gather up statistics of that mesh in
        python friendly data structure.  Currently it only gathers the
        following components:
           - vertices
           - face data
        
        It is possible to ask for the smooth version of the mesh by
        setting the smooth flag to True.
        """
    
        pass



