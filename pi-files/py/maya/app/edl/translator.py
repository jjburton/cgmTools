"""
Used by Maya's EDL Import/Export feature.
Subclasses must return dictionaries with the appropriate data

Should log errors of the following types:
error = something we cannot recover from
"""

class Translator(object):
    def __init__(self, fileName):
        """
        self.fileName   = name of EDL file to be used for input or output
        self.logger             = logging interface to capture errors/warnings. Modules
                                          that use Translator should register their handlers
                                          with this logger.
        """
    
        pass
    
    
    def getClip(self, clip_elem):
        """
        Given a clip element (which is returned b getTrack), return a dictionary
        with the following information:
        id                      = id of the clip. Will be used for linking
        name            = name of the clip
        duration        = in frames
        enabled         = true/false
        start/end       = defines placement of clip in the sequence
        in/out          = define start/end frames of the clip in source media
        file            = file sub element. Use getFile method to read contents
        """
    
        pass
    
    
    def getFile(self, file_elem):
        """
        Given a file element (returned by getClip), return a dictionary with the 
        following information:
        
        id                      = id of the clip. Can be used to reference a file that's 
                                  already been defined somewhere else
        name            = name of file
        pathurl         = path to file (i.e. file:///)
        """
    
        pass
    
    
    def getSequence():
        """
        Read the sequence information from an EDL file.
        Assumes readFromFile has already been called
        
        Returns dictionary containing the following:
        
        name                    = name of the sequence
        duration                = duration in frames
        framerate               = in frames per second
        video_tracks    = list of video track sub elements. Use getTrack to
                                          read the contents
        audio_tracks    = list of audio track SubElements. use getTrack to
                                          read the contents
        """
    
        pass
    
    
    def getTimecode(self, timecode_elem):
        """
        Given a timecode sub element (which is returned by getSequence or getClip or getFile),
        return the following information:
        
        framerate       = in frames per second
        format          = type of timecode. ex: "smpte"
        """
    
        pass
    
    
    def getTrack(self, track_elem):
        """
        Given a track element (which is returned by getSequence), read the
        relevant track information.
        
        Returns dictionary containing the following:
        
        locked          = true/false
        enabled         = true/false
        width           = width in pixels (if specified)
        height          = height in pixels (if specified)
        
        clip_list       = list of clipitem sub elements that are a part of this track.
                                  To read data from the clips, use getClip
        """
    
        pass
    
    
    def readFromFile(self):
        """
        Read the EDL file from disk into memory.
        """
    
        pass
    
    
    def writeToFile(self):
        """
        Write the in-memory EDL to disk
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



