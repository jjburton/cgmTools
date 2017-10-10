class MayaToPyItr(object):
    """
    This class turns a non pythonic maya iterator into a standard
    python iterator that can be used with all the standard libs and idioms
    (for loops, list comprehensions, filters and maps).
    it dispatches unknown method calls to the wrapped maya iterator class
    """
    
    
    
    def __getattr__(self, attrname):
        """
        # delegate all unknown methods and attr accesses to the maya iterator
        """
    
        pass
    
    
    def __init__(self, maya_iterator):
        pass
    
    
    def __iter__(self):
        pass
    
    
    def __len__(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class PyDepGraphItr(MayaToPyItr):
    """
    This wraps MItDependencyGraph iterator and turns it into a python iterator
    """
    
    
    
    pass


class PyEditItr(MayaToPyItr):
    """
    A class that wraps the MItEdits to make it work as a python iterator
    Usage Examples:
    
    edits = PyEditItr( om.MItEdits( assembly_mobject ) )
    for edit in edits:
       print(edit.getString())
       if edit.getType() == om.MEdit.kParentEdit:
           pe = edits.parentingEdit()
    
    # get how many edits the standard python way
    print(len(edits))
    
    # list comprehension with filter
    parent_edits = [edits.parentingEdit() for edit in edits if edits.currentEditType() == om.MEdit.kParentEdit]
    
    # map example
    edit_strings = [ e.getString() for e in edits ]
    """
    
    
    
    def __init__(self, mit_edits=None, ar_mobj=None):
        """
        mit_edits om.MItEdits the 
        ar_mobj assembly reference MObject
        """
    
        pass
    
    
    edit_factories = {}


class PyDagItr(MayaToPyItr):
    """
    Wraps MItDag iterator making it function as a standard python
    iterator. A default MItDag iterator will be constructed if none is 
    specified.
    
    Usage Examples:
    # print tabbed dag hierarchy
    dag_objects = PyDagItr()
    for dag_object in dag_objects:
        print('%s%s' % ( '      ' * dag_objects.depth(), dag_object.fullPathName()) )
    """
    
    
    
    def __init__(self, mit_dag="<maya.OpenMaya.MItDag; proxy of <Swig Object of type 'MItDag *' at 0x12b15fe70> >"):
        pass


class PyDepNodesItr(PyDepGraphItr):
    """
    This wraps MItDependencyNodes iterator turning it into a python iterator.
    A default MItDependencyNodes iterator will be constructed if none is 
    specified.
    """
    
    
    
    def __init__(self, mit_dependency_nodes="<maya.OpenMaya.MItDependencyNodes; proxy of <Swig Object of type 'MItDependencyNodes *' at 0x12b15fea0> >", filter=0, miterator_type=None):
        """
        filter and miterator_type are used to determine how to properly reset the
        mit_dependency_nodes iterator they should be the same values used to 
        construct mit_dependency_nodes iterator
        """
    
        pass


class PyAssemblyItr(PyDagItr):
    """
    This iterates over all the scene assembly nodes in the scene
    usage example:
    assemblies = PyAssemblyItr()
    [assembly.name() for assembly in assemblies]
    """
    
    
    
    def __init__(self):
        pass



