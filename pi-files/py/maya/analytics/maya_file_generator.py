def get_maya_files(generator):
    """
    Help function for the MayaFileGenerator class that runs the generator
    and then packages up the results in a directory-centric format.
    
    generator : A MayaFileGenerator function call, already constructed but not used
    
    returns a list of ( DIRECTORY, [FILES] ) pairs consisting of
        all matching files from generation using the passed-in generator.
    
    theGen = MayaFileGenerator("Maya/projects", skipFiles=['temp\w'])
    for (the_dir,files_in_dir) in get_maya_files(theGen):
        print the_dir
        for the_file in files_in_dir:
            print ' -- ',the_file
    """

    pass


def maya_file_generator(root_path, skip=None, descend=True):
    """
    Generator to walk all Maya files in or below a specific directory.
    
    root_path  : Path or list of paths to walk, looking for Maya files
    skip       : A list of regular expression strings indicating path patterns
                 to skip.  Match begins anywhere in the string so the leading
                 "^" is necessary if you wish to check for a prefix. Some
                 example expressions include:
    
                 '.mb$'         : Skip all Maya Binary files
                 '/references/' : Skip all files in a subdirectory called "references"
                 '_version.*'   : Skip all files with a version number in the name
    
    descend    : Recurse into subdirectories
    
    Returns list of filepaths in any of the root_paths not matching the skip patterns.
    
    Usage:
    Find all Maya files under "root/projects" that aren't temporary files,
    defined as those named temp.ma, temp.mb, or that live in a temp/ subdirectory.
    
        from maya.analytics.maya_file_generator import maya_file_generator
        for path in maya_file_generator('Maya/projects', skip=['^temp.m{a,b}$','/temp/']):
            print path
    
        for path in maya_file_generator(['Maya/projects/default','Maya/projects/zombie']):
            print path
    """

    pass



