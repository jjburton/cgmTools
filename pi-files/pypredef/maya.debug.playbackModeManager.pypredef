"""
Holds the helper class playbackModeManager used to change and restore
the playbackOptions within a scope. Load with:

        from maya.debug.playbackModeManager import playbackModeManager
"""

class playbackModeManager(object):
    """
    Helper class that maintains the playback mode information.
    
    It maintains state information for all playback options so that they can be
    modified within a scope and have the original settings restored on completion.
    
    Calling any of the setXXX() methods
    
    The object is set up to use the Python "with" syntax as follows:
    
        with playbackModeManager() as mgr:
            mgr.setOption( minTime=newStartFrame )
    
    That will ensure the original states are all restored. There's no other
    reliable way to do it in Python. If you need different scoping that can't
    be put into a nice code block like this you can manually call the methods
    to complete the sequence:
    
        mgr = playbackModeManager()
            ...
        mgr.setOption( minTime=newStartFrame )
            ...
        mgr.restore()
    
    You may also be interested in this utility method that will playback the
    entire range from the start in 'wait' mode. Two reasons you want this:
        1. If you don't play in 'wait' mode then your manager can go out of
           scope while playback is running.
        2. Playing in 'wait' mode starts from the current frame and it does
           not rewind if you're already at the end.
    
        ...
        mgr.playAll()
        ...
    """
    
    
    
    def __enter__(self):
        """
        Beginning of scope object for "with" statement. __init__ does all intialization
        """
    
        pass
    
    
    def __exit__(self, theType, theValue, traceback):
        """
        Ensure the state is restored if this object goes out of scope
        """
    
        pass
    
    
    def __init__(self):
        """
        Defining both __enter__ and __init__ so that either one can be used
        """
    
        pass
    
    
    def playAll(self):
        """
        Playback the entire animation sequence, returning the elapsed time when it is done
        """
    
        pass
    
    
    def playLimitedRange(self, maxFrames, fromStart=False):
        """
        Playback the given animation range, returning the elapsed time when it is done.
        The time range is only set temporarily for this playback sequence.
        If you wish to permanently change the time range use setOption().
        
        maxFrames: Maximum number of frames to play. If maxTime-currentTime is less
                   than this number then the entire frame range will play,
                   otherwise it will play currentTime to currentTime+maxFrames-1
        fromStart: When set to True this will first move the playback to where the
                   current time was when the manager was created. This allows you
                   to get consistent limited length playbacks from an arbitrary
                   starting frame.
        """
    
        pass
    
    
    def playRange(self, minTime, maxTime):
        """
        Playback the given animation range, returning the elapsed time when it is done.
        The time range is only set temporarily for this playback sequence.
        If you wish to permanently change the time range use setOption().
        """
    
        pass
    
    
    def restore(self):
        """
        Restore the playback options to their original values (i.e. the ones
        present when this object was constructed).
        
        It's necessary to call this when using the "with playbackModeManager()"
        syntax. It's only needed when you explicitly instantiate the mode manager.
        Then you have to call this if you want your original state restored,
        or wait for the unknown point in the future where this object is
        destroyed.
        """
    
        pass
    
    
    def setOption(self, animationEndTime=None, animationStartTime=None, blockingAnim=None, byValue=None, framesPerSecond=None, loop=None, maxPlaybackSpeed=None, maxTime=None, minTime=None, playbackSpeed=None, view=None):
        """
        Mirror the arguments used by the playbackOptions command. A value of
        "None" means "don't set this particular value".
        
        raises ValueError if the playbackOption command failed.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def _dbg(message):
    """
    Print the message if in debug mode
    """

    pass



DEBUG_MODE = False


