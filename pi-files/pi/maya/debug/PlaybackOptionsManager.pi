"""
The object is set up to use the Python "with" syntax as follows:

    from maya.debug.PlaybackOptionsManager import PlaybackOptionsManager,PlaybackOptions

    with PlaybackOptionsManager() as mgr:
        mgr.setOption( 'minTime', 1.0 )
        mgr.setOption( 'maxTime', 10.0 )
        mgr.setOption( 'loop', 'once' )
        # Now you know for sure it will play exactly 10 frames, once,
        # regardless of what the user has for their playback options.
        cmds.play( wait=True )
    # And now the user's options are restored

That will ensure the original states are all restored when the
scope completes. There's no other reliable way to do it in Python.
If you need different syntax you can manually call the method to
complete the sequence:

    mgr = PlaybackOptionsManager()
    mgr.setOption( 'minTime', 1.0 )
    mgr.restore()

The first setOption() parameter corresponds to the names of the
parameters of the playbackOptions command:

    cmds.playbackOptions( minTime=... ) => setOption('minTime',...)
"""

class PlaybackOptions(object):
    """
    Helper class to hold and capture all of the playback options
    """
    
    
    
    def __init__(self):
        """
        On creation load in all of the current options. That's all
        this class does. They remember the playback state. The
        member names don't follow PEP8 standards so that they can
        follow the naming convention used in the playbackOptions
        command.
        """
    
        pass
    
    
    def set_options(self):
        """
        Set the playback options to the values in this class
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    ALL_OPTIONS = []


class PlaybackOptionsManager(object):
    """
    #======================================================================
    """
    
    
    
    def __enter__(self):
        """
        #----------------------------------------------------------------------
        """
    
        pass
    
    
    def __exit__(self, type, value, traceback):
        """
        Ensure the state is restored if this object goes out of scope
        """
    
        pass
    
    
    def __init__(self):
        """
        Defining both __enter__ and __init__ so that either one can be used
        """
    
        pass
    
    
    def restore(self):
        """
        Restore the playback options to their original values prior to entering
        this one.  Not necessary to call this when using the "with PlaybackOptionsManager()"
        syntax. Only needed when you explicitly instantiate the options manager.
        Then you have to call this if you want your original state restored.
        """
    
        pass
    
    
    def setOption(option, new_value):
        """
        Method that modifies each of the playback options. The valid options
        come from the class member ALL_OPTIONS.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def _dbg(message):
    """
    Print out a message if the debug mode is enabled, otherwise do nothing
    """

    pass



DEBUG_MODE = False


