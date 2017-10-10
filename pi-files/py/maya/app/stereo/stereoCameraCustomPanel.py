def activeModeAvailable(*args):
    """
    Query the custom view to determine if the specified mode is available.
    """

    pass


def currentViewCamera(*args):
    """
    Get the camera that is assigned to the current view.
    """

    pass


def currentViewRigFromEditor(editor):
    pass


def currentViewCameraFromEditor(editor):
    """
    Given an editor retrieve the current camera from that editor.
    """

    pass


def switchToSinglePerspLayout():
    """
    Switch the current view into to single perspective stereo mode.
    """

    pass


def setConvergenceDistanceToSelected(*args):
    """
    Sets the convergence distance on the current viewing camera to the
    the specified selection. If more than one object is selected. It
    takes the average distance between each selection. Note, this only
    works with the standard StereoCamera rig and does not support generic rig
    data types.
    """

    pass


def switchToSelected(*args):
    """
    Switch the viewing camera to the current selection.
    """

    pass


def switchToCameraSet(*args):
    """
    Switch the viewport editor the specified cameraSet name.
    """

    pass


def switchToOutlinerPerspLayout():
    """
    Switch the current view into a outliner / persp viewer mode.
    """

    pass


def swapCamerasState(*args):
    """
    Query the swap bit on the view.
    """

    pass


def stereoCameraViewCallback(*args):
    """
    Main callback point for sending information to the editor command.
    The format of the callback is as follows:
    
    arg1 = the name of the editor
    arg2 = keyword dictionary represented as a string.
    """

    pass


def swapCameras(*args):
    """
    Toggle the swap bit on the view.
    """

    pass


def initialize():
    """
    Main initialization routine for registering a new panel type. This menu
    registers the new panel with Maya. We also install callbacks to monitor
    for new scene changes.
    """

    pass


def switchToCameraCenter(cameraName, editor):
    """
    Additional wrapper layer around switchToCamera. This function switches
    to the current camera and also toggles the view mode to be 'center'
    """

    pass


def uninitialize():
    """
    Main uninitialization routine for deregistering the new panel and removes
    callbacks.
    """

    pass


def switchToCameraRight(cameraName, editor):
    """
    Additional wrapper layer around switchToCamera. This function switches
    to the current camera and also toggles the view mode to be 'right'
    """

    pass


def switchToCamera(*args):
    """
    Switch the viewport editor the specified camera name.
    """

    pass


def checkState(*args):
    """
    This is a callback that is invoked by the menu creation code. It is
    used to determine if the menu item should be checked. The first argument
    is assumed to be the displayMode name to check against and the second
    argument is assumed to be the name of the editor. Both are string types.
    """

    pass


def getValidPanel(editor):
    """
    This function checks the given editor to make sure it is an editor
    that we recognize. If it is not an known editor then we try to
    find an editor that will work.
    """

    pass


def toggleUseCustomBackground(*args):
    """
    Toggle whether the current viewport background should match the background
    that is defined in the user preferences.
    """

    pass


def getValidEditor(panel):
    pass


def adjustBackground(*args):
    """
    Get the camera that is assigned to the current view.
    """

    pass


def addNewCameraToCurrentSet(rigRoot, panel):
    """
    This is the main function for adding camera rigs to a camera
    set. Given a valid stereo rig, add that rig to the current camera
    set. If a camera set does not exist then, create one and make the
    view aware of the camera set.
    """

    pass


def createStereoCameraViewCmdString(command, editor, the_args):
    """
    Packs the given arguments into a python string that can be evaluated
    at runtime.
    
    - the_args is assumed to be represented as a dictionary
    - editor is the custom editor.
    """

    pass


def useCustomBackgroundState(*args):
    """
    Return the state (True/False) of whether we use the display preferences or
    a solid background.
    """

    pass


def selectCamera(*args):
    """
    Select the camera that is in the current view.
    """

    pass


def switchToCameraLeft(cameraName, editor):
    """
    Additional wrapper layer around switchToCamera. This function switches
    to the current camera and also toggles the view mode to be 'left'
    """

    pass



