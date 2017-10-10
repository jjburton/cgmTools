"""
Module containing the class responsible for getting names of plugs, nodes,
and DAG paths in a potentially unique and anonymous way.
"""

class ObjectNamer(object):
    """
    Utility object to remap object names onto something appropriate.
    The simplest mapping is to return the name itself. If that's all
    you are ever going to do then don't use this class.
    
    The main use for this class is to anonymize names that might be
    considered sensitive. The anonymizing mode will ensure that the
    real name always matches the same generated name, and will give
    some minimal information within the name itself. (e.g. a file
    name will be called file_001, a directory name might be called
    dir_031, and a Maya transform node could be called transform_042.
    
    If you know how many objects you will be naming you can call
    ObjectNamer.set_max_objects(). This will guarantee that the formatting
    of the anonymized names can be lexically sorted correctly by using
    a zero-padded integer numbering system. This is useful because
    "file02" comes before "file10" but "file2" comes after it.
    
    The following anonymizer modes are supported:
    
        ObjectNamer( ObjectNamer.MODE_NAME )
            Names have no specific type. The are anonymized generically
                MySecretObject -> name01
        ObjectNamer( ObjectNamer.MODE_PLUG )
            Names are assumed to be Maya plug names. The node name part is
            anonymized but the attribute name is left as-is.
                MySecretNode.translateX -> node001.translateX
        ObjectNamer( ObjectNamer.MODE_NODE )
            Names are assumed to be Maya node names. The node name part is
            anonymized using the node type as a root if this module is
            executed inside of Maya, otherwise the generic 'node' is used.
                In Maya:    MySecretTransform -> transform001
                Standalone: MySecretTransform -> node001
        ObjectNamer( ObjectNamer.MODE_PATH )
            Names are assumed to be file paths. The first sections of the path
            are anonymized as directories, the final one is anonymized as a
            file. Paths with trailing separators (e.g. "/") are assumed to be
            directories. Paths are made into canonical form so all backslashes
            are replaced by forward slashes on Windows.
                root/parent/child/MySecretFile.ma -> dir1/dir2/dir3/file1.ma
                root/parent/child/MySecretDir/    -> dir1/dir2/dir3/dir4/
    
    Class members:
        name_type        : Naming method to use (MODE_NAME, MODE_PLUG, MODE_NODE, MODE_PATH)
        anonymous        : If True all names will be anonnymized, else used as-is
        maya_cmds        : If Maya commands are available they can be accessed through this
        name_fmt         : Formatting string for anonymous names - includes the proper
                           number of expected leading zeroes based on max object count
        anonymized_names : Directory of already assigned anonymous names (ORIGINAL : ANONYMOUS_NAME)
        unique_id        : Directory of unique IDs to use for anonymizing.
                          Key is the type of object, value is the next unique ID for it.
    
        Usage:
            import ObjectNamer
            oNamer = ObjectNamer.ObjectNamer( ObjectNamer.MODE_NAME, anonymous=True )
            oNamer.set_max_objects( 100 )
            print oNamer.name( "My Funky Thing" )
            # Result = "name_01"
            print oNamer.name( "Some Other Stuff" )
            # Result = "name_02"
            print oNamer.name( "My Funky Thing" )
            # Result = "name_01"
            noNamer = ObjectNamer.ObjectNamer( ObjectNamer.MODE_NAME, anonymous=False )
            print oNamer.name( "My Funky Thing" )
            # Result = "My Funky Thing"
    """
    
    
    
    def __init__(self, name_type, anonymous):
        """
        Create a namer.
            name_type:  NODE_{NAME,PLUG,NODE,PATH}
            anonymous: True means don't use the original names, anonymize them
        """
    
        pass
    
    
    def clear(self):
        """
        Erase all of the currently remembered names. Resets the unique IDs
        back to the original. Names generated after a clear() may not be
        unique compared to names generated before the clear().
        """
    
        pass
    
    
    def name(self, original_name):
        """
        Get the name which corresponds to "original_name". In the case of
        non-anonymized names that will just be the original name.
        """
    
        pass
    
    
    def set_max_objects(self, max_objects):
        """
        Set the maximum number of objects expected to be named with this
        namer. This allows creation of a consistent number of leading
        zeroes on anonymized ID values for easy sorting.
        
        If max_objects is 0 then use the %d format with no leading zeroes.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    MODE_NAME = 0
    
    
    MODE_NODE = 2
    
    
    MODE_PATH = 3
    
    
    MODE_PLUG = 1
    
    
    NAME_DIRECTORY = 'dir'
    
    
    NAME_FILE = 'file'
    
    
    NAME_GENERIC = 'name'
    
    
    NAME_NAMESPACE = 'namespace'
    
    
    NAME_NODE = 'node'
    
    
    NAME_UNDERWORLD = 'underworld'
    
    
    SEP_ATTRIBUTE = r'\.'
    
    
    SEP_DRIVE = ':'
    
    
    SEP_NAMESPACE = ':'
    
    
    SEP_NODE = r'\|'
    
    
    SEP_PATH = '/'
    
    
    SEP_UNDERWORLD = '->'



