"""
This module provides camera set support to the stereo camera
plug-in. Camera sets allow the users to break a single camera shot
into layers. Instead of drawing all objects with a single camera, you
can isolate the camera to only focus on certain objects and layer another
camera into the viewport that draws the other objects.  

For instance, a set of stereo parameters may make the background
objects divergent beyond the tolerable range of the human perceptual
system. However, you like the settings because the main focus is in
the foreground and the depth is important to the visual look of the
scene.  You can use camera sets to break apart the shot into a
foreground stereo camera and background stereo camera. The foreground
stereo camera will retain the original parameters; however, it will
only focus on the foreground elements.  The background stereo camera
will have a different set of stereo parameters and will only draw the
background element.
"""

def __attachToCameraSet(rigRoot, cameraSet, objectSet=None):
    """
    Attach the rigRoot to the cameraSet and assign it to the camera
    set.  If an objectSet is provided then also attach it to the same layer
    """

    pass


def _gatherSelObjects():
    """
    Private method that gets the active selection list, finds all selected
    transforms and returns two lists:
    1) a list of cameras attached to camera sets stuff into a python set in the
       form  (cameraSet, cameraSet layerId, cameraName, objectSet)
    2) a list of objects to attach to the items found in 1)
    """

    pass


def isCameraSet(cameraSet):
    """
    Returns true if the object is a camera set.  This is simply
    a wrapper objectType -isa
    """

    pass


def breakLinks():
    pass


def _callFromDefinition(definitions, rigType, keywords, args):
    """
    Call the custom callback for this object.
    """

    pass


def parentToLayer0Rig(rigRoot, cameraSet=None):
    """
    When adding a new layer to a camera set, the most common desired
    placement of that new rig is under the primary camera, which is
    at layer 0. This function performs the task of looking up the
    transform at layer 0 and parenting the new rig under its
    transform.
    """

    pass


def _getDefinition(rigType):
    """
    Get the definition for this object.
    """

    pass


def addNewRigToSet(newRigRoot, currentRigRootOrCameraSet, objectSet=None):
    """
    This is the main function for adding cameras/rigs to a camera
    set. Given a valid stereo rig, add that rig to the specified
    camera set. The second argument to this function can either be the
    existing rig root that we are layering or the current camera set.
    
    If it is the camera set then simply append the newRigRoot to the
    camera set. If it is a rig then create a new camera set attach
    the current rig to the set and then append the newRigRoot to
    that set.
    
    We return the camera set on exit.
    """

    pass


def makeLinks():
    pass


def notifyCameraSetCreateFinished(cameraSet, rigType='StereoCamera'):
    """
    Developers who need to customize camera sets have requested the ability to
    receive nofications when we have finished created a camera set. This
    is the function that kick-starts that notification.
    """

    pass


def _makeOrSet(cameraSet, layerId, objectSet, setObj, add=True):
    pass



