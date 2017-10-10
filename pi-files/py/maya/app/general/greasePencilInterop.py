"""
# Grease Pencil interop file
#
"""

def readArchive(archivePath, tempDirectory):
    """
    # Reads an archive and extracts the xml file and the
    # file textures. We return a string that contains the
    # frame information along with the path to the
    # extracted files
    """

    pass


def writeArchive(archivePath, frameData):
    """
    # Write a zip file containing the file textures and
    # the xml info file
    """

    pass


def readXmlFile(xmlFilePath, fileList):
    """
    # Read an xml file to extract frames(time,filePath). The frame information is converted
    # to a string so that it can be passed to C++. The second parameter 'fileList' is used
    # to make sure all frame files referred exist
    """

    pass


def writeXmlFile(xmlFilePath, timeList, fileList, layerList, durationList):
    """
    # Write out an xml file containing frame information. Each
    # frame has a time and a file path
    """

    pass


def _writeXmlSettings():
    """
    # Settings are hard coded for now
    """

    pass



kLayerKeyword = 'layer'

kFileKeyword = 'file'

kSettingKeyword = 'setting'

kFramesKeyword = 'frames'

kFrameKeyword = 'frame'

kGreasePencilKeyword = 'greasepencil'

kDurationKeyword = 'duration'

kTimeKeyword = 'time'

kFPSKeyword = 'fps'

kSettingsKeyword = 'settings'


