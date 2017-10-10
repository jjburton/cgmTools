"""
Utility to contain the DG state information captured by a correctness
analysis. It reads the information from a file and provides analysis
tools, such as comparison.

State information is in JSON format for easy storage, parsing, and comparison.
Data is stored in a method that provides a parsing clue for what types of
values are stored on the plug:
    isinstance(VALUE, numbers.Number) : Simple numeric value
    type(VALUE) is list : List of simple numeric values (matrix or vector)
    type(VALUE) is dict : Named data type, with a named parser

    {
        "state" :
        {
            "file" : "NAME_OF_FILE",
            "time" : "TIME_AND_DATE_OF_STATE_CAPTURE",
            "dirty" :
            {
                "connections" : [ LIST_OF_ALL_DIRTY_CONNECTIONS ],
                "data" : [ LIST_OF_ALL_DIRTY_DATA_PLUGS ]
            },
            "data" :
            {
                NODE :
                {
                    PLUG : PLUG_VALUE,
                    PLUG : [ PLUG_MATRIX ],
                    PLUG : { "mesh" : { MESH_DATA } },
                    ...
                },
                ...
            },
            "screenshot" : FILE_WHERE_SCREENSHOT_IS_SAVED
        }
"""

class DGState(object):
    """
    State object containing all data values that come out of the dbpeek
    command using the 'data' operation for simple data values and the
    dbpeek 'mesh' operation for mesh geometry.
    
    results_files: Where the intermediate results are stored. None means don't store them.
    image_file:    Where the screenshot is stored. None means don't store it.
    state:         Data state information from the scene.
    """
    
    
    
    def __init__(self):
        """
        Create a new state object.
        """
    
        pass
    
    
    def compare(self, other, verbose):
        """
        Compare two state information collections and return a count of the
        number of differences. The first two fields (node,plug) are used to
        uniquely identify the line so that we are sure we are comparing the
        same two things.
        
        The 'clean' flag in column 2 is omitted from the comparison since
        the DG does funny things with the flag to maintain the holder/writer
        states of the data.
        
        other:      Other DGstate to compare against
        verbose:    If True then print the differences as they are found
        
        If verbose is False return the 3-tuple of integers (additionCount, changeCount, removalCount)
        If verbose is True return the 3-tuple of lists (additions, changes, removals)
        """
    
        pass
    
    
    def filter_state(self, plug_filter):
        """
        Take the current state information and filter out all of the plugs
        not on the plug_filter list. This is used to restrict the output to
        the set of plugs the EM is evaluating.
        
        plug_filter: Dictionary of nodes whose values are dictionaries of
                    root level attributes that are to be used for the
                    purpose of the comparison.
        
                    None means no filter, i.e. accept all plugs.
        """
    
        pass
    
    
    def get_md5(self):
        """
        Get the md5 checksum from the image file, if it exists.
        Return '' if the image file wasn't generated for an easy match.
        """
    
        pass
    
    
    def read_graph(self, graph_file):
        """
        Read the graph configuration from a file. If this graph plug list
        exists when doing the comparison then only plugs on the list will
        be considered, otherwise everything will be checked.
        
        The format of the file is a sequence of nodes followed by their
        attributes demarcated by leading tabs:
            NODE1
                ATTRIBUTE1
                ATTRIBUTE2
                ...
            NODE2
                ATTRIBUTE1
                ATTRIBUTE2
                ...
            ...
        """
    
        pass
    
    
    def read_state(self, results_file=None, image_file=None):
        """
        Read in the results from a previous state capture from the given results and
        image files.
        
        results_file : Name of file from which to load the results.
                       Do not load anything if None.
        image_file   : Name of file from which to load the current viewport screenshot.
                       Do not load anything if None.
        """
    
        pass
    
    
    def scan_scene(self, do_eval, data_types):
        """
        Read in the state information from the current scene.
        Create a new state object, potentially saving results offline if
        requested.
        
        do_eval      : True means force evaluation of the plugs before checking
                       state. Used in DG mode since not all outputs used for
                       (e.g.) drawing will be in the datablock after evaluation.
        data_types   : Type of data to look for - {mesh, vertex, number, vector, screen}
                       If screen is in the list the 'image_file' argument must also be specified.
        """
    
        pass
    
    
    def store_state(self, results_file=None, image_file=None):
        """
        Store the existing state in the files passed in.
        
        results_file: Destination for the raw numerical data for comparison
        image_file:   Destination for the viewport screenshot
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    RE_INVERSE_MATRIX = 'InverseMatrix'
    
    
    SCREENSHOT_NODE = '__screenShot__'
    
    
    SCREENSHOT_PLUG_IMF = '__screenShot__.imf'
    
    
    SCREENSHOT_PLUG_MAG = '__screenShot__.mag'
    
    
    SCREENSHOT_PLUG_MD5 = '__screenShot__.md5'



SIGNIFICANT_DIGITS_INVERSE = 0.9

MD5_DEFAULT = 'md5'

NO_SIGNIFICANT_DIGITS_MATCH = 0

IMF_DIFF_MIN_DIFFERENCE = '5'

MD5_AS_DEFAULT_COMPARATOR = False

MD5_BLOCKSIZE = 33024

RE_ROOT_ATTRIBUTE = None

RE_IMF_IDENTICAL = None

RE_IMF_COMPARE = None

IMAGEMAGICK_METRIC = 'FUZZ'

IMAGEMAGICK_MATCH_TOLERANCE = 500

RE_IMG_COMPARE = None

SIGNIFICANT_DIGITS = 1.9

ALL_SIGNIFICANT_DIGITS_MATCH = 999

IMF_DIFF_MATCH_TOLERANCE = 1.0


