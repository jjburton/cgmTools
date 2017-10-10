from maya.app.edl.translator import *

class FCP(Translator):
    def __init__(self, fileName):
        pass
    
    
    def formatErrorElement(self, cur_elem):
        """
        Format information about the current element that will be used in an error message.
        So we want the type of element (ex: file, clip etc) and the name/id.
        """
    
        pass
    
    
    def getClip(self, clip_elem):
        """
        Given a clip element or transition item (which is returned b getTrack), return a dictionary with the
        following information:
        id                      = id of the clip. Will be used for linking, referencing clips in the 
                                  browser etc.
        name            = name of the clip item
        duration        = in frames
        enabled         = True/False
        start/end       = define placement of clip in the sequence
        in/out          = define start/end frames of the clip in source media
        file            = eTree SubElement for the <file> tag. Use getFile method to read contents
        transition  = indicates if the clip is a transition, will be True is the clip is a transition item= True
        alignment       = define the placement of a transition, not present for clips
                                  according to FCP/XML doc, valid values are center, start, end, start-black and end-black
        """
    
        pass
    
    
    def getFile(self, file_elem):
        """
        Given a file element (returned by getClip), return a dictionary with the following
        information:
        
        id                      = id of the clip. Can be used to reference a file that's already been
                                  defined somewhere else
        name            = name of file
        pathurl         = path to file (i.e. file://)
        """
    
        pass
    
    
    def getLinks(self):
        """
        Return a list of dictionaries that map ids to elements.
        Each dict is a link group
        """
    
        pass
    
    
    def getMasterClips(self):
        """
        Read the <bin> tag and all master clip and file information. Will
        populate the self.master_clips dictionary.
        """
    
        pass
    
    
    def getSequence(self):
        """
        Read the sequence information from a Final Cut Pro XML hierarchy.
        Assumes that XML has already been parsed with readFromFile method.
        
        Returns dictionary containing the following:
        
        name                    = name of the sequence
        duration                = duration in frames
        framerate               = in frames per second
        timecode                = timecode string
        video_tracks    = list of video track SubElements. Use getTrack to
                                          read the contents
        audio_tracks    = list of audio track SubElements. use getTrack to
                                          read the contents
        """
    
        pass
    
    
    def getTrack(self, track_elem):
        """
        Given a track element (which is returned by getSequence), read the
        relevant information.
        
        Returns dictionary containing the following:
        
        locked          = True/False
        enabled         = True/False
        width           = width in pixels (if specified)
        height          = height in pixels (if specified)
        
        clip_list       = list of clipitem SubElements that are a part of this track.
                                  To read data from the clips, use getClip
        """
    
        pass
    
    
    def readFromFile(self):
        """
        Reads XML file and populates an ElementTree hierarchy
        """
    
        pass
    
    
    def writeClip(self, track_elem, clip_info):
        """
        Add a clip to the specified track. clip_info must contain the following info:
        name            = name of the clip item
        duration        = in frames
        enabled         = True/False
        start/end       = define placement of clip in the sequence
        in/out          = define start/end frames of the clip in source media
        """
    
        pass
    
    
    def writeFile(self, clip_elem, file_info):
        """
        Add a file to the specified clip. file_info must contain the following:
        
        id                                      = used for linking of audio/video
        name or pathurl         = file name or absolute path to the location
        duration                        = media length (sequence frames)
        """
    
        pass
    
    
    def writeFormat(self, seq_elem, width, height):
        """
        Add a format element to the specified sequence.
        """
    
        pass
    
    
    def writeSequence(self, seq_info):
        """
        Write the sequence. We expect seq_info to contain the following information:
        
        name                    = name of the sequence
        duration                = duration in frames
        framerate               = in frames per second
        timecode                = timecode of the sequence (optional)
        """
    
        pass
    
    
    def writeToFile(self):
        """
        Write the XML file in memory to disk
        """
    
        pass
    
    
    def writeTrack(self, seq_elem, track_info):
        """
        Add a track to the specified sequence. track_info must contain the following info:
        
        type            = "audio" or "video"
        name            = name of track
        locked          = True/False
        enabled         = True/False
        """
    
        pass



def indent(elem, level=0):
    """
    This is from ElementTree's Element Library. By default XML is written 
    in the compact form, with no whitespace. So we need to do the indenting
    ourselves to get human-readable XML
    """

    pass



