import exceptions

"""
This module contains the UI code for the QuickRig tool.

It also holds several utility methods that are used by the tool.  These are
used to automatically perform tasks such as guides creation, guides mirroring,
skeleton creation, joint orientation, rig creation, etc.
"""

from maya.common.ui import LayoutManager
from maya.common.utils import getSourceNodeFromPlug
from maya.common.utils import getIndexAfterLastValidElement
from maya.common.ui import showMessageBox
from functools import partial
from maya.common.utils import getSourceNode
from maya.common.ui import showConfirmationDialog
from functools import wraps
from maya.common.utils import getSourceNodes

class PieceWiseLinearFunction:
    """
    This class handles interpolation between an array of points.
    """
    
    
    
    def __init__(self, points):
        pass
    
    
    def evaluate(self, value):
        pass


class QuickRigTool:
    """
    This is the main UI class for the QuickRig tool.
    
    It handles creation of the UI and provides various callbacks to handle
    user interactions.
    """
    
    
    
    def __init__(self, windowName='quickRigWindowId'):
        """
        Simple constructor.
        
        It does not create the UI.  UI creation is deferred until create() is
        called
        """
    
        pass
    
    
    def create(self):
        """
        This method completely builds the UI.  It shows the resulting window
        when it is fully created.
        """
    
        pass
    
    
    def updateUI(self):
        """
        This method performs a full UI refresh.
        
        It refreshes the character list and its associated buttons.  It also
        refreshes the HumanIK tool.
        """
    
        pass


class HIKManipulationScope:
    """
    This class is a simple manager that sets a manipulation mode when entering
    and resets the previous manipulation mode when exiting.
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
    
    def __init__(self, manipulationMode):
        pass
    
    
    def setManipulationMode(self, mode):
        pass


class HIKContext(object):
    """
    Simple Context Manager for restoring HIK Animation settings and managing HIK callbacks
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
    
    def __init__(self, NodeList):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class Vector3:
    """
    This class is a minimalist vector class.
    
    It only does the strict minimum needed by this tool and is not meant to be
    a generic vector class.
    """
    
    
    
    def __add__(self, other):
        pass
    
    
    def __getitem__(self, key):
        pass
    
    
    def __init__(self, *args):
        pass
    
    
    def __mul__(self, other):
        pass
    
    
    def __setitem__(self, key, value):
        pass
    
    
    def __sub__(self, other):
        pass
    
    
    def cross(self, other):
        pass
    
    
    def dot(self, other):
        pass
    
    
    def length(self):
        pass
    
    
    def project(self, target):
        pass


class UserException(exceptions.Exception):
    """
    This class is the exception class for errors caused by improper user
    interaction.
    """
    
    
    
    def __init__(self, message):
        pass
    
    
    __weakref__ = None



def qrGetGuidesNode(character):
    """
    This method returns the name of the guides node associated with the given
    character, if any.
    """

    pass


def callback_step2_CreateGuides(*args, **kwargs):
    pass


def removeOutput_step5(input):
    pass


def createContainer():
    """
    This method creates a container object which fields can be assigned
    dynamically.
    
    For instance, the object returned by this method will allow:
    
    obj = createContainer()
    obj.newAttribute = 'my new attribute value'
    """

    pass


def callback_step5_BindSkin(*args, **kwargs):
    pass


def qrSetGuidesColor(guidesNode, color):
    """
    This method sets the color on all the guides.
    """

    pass


def hikUpdateTool():
    """
    This method refreshes the HumanIK tool UI so that it fits the current
    HumanIK character.
    """

    pass


def getCharacterDefiniton(character):
    """
    This method gets the HumanIK information from the given character.
    
    It uses the character and HumanIK commands to do so, even though all of
    this information would be available from the skeleton settings.
    """

    pass


def getInput_step4(input):
    pass


def computeTStance(definition, positions, useTStanceCorrection):
    """
    This method computes the T-stance position for a given character, given
    the position of the guides.
    
    It leaves the joints that can be corrected using effectors in their current
    direction, but adjusts the bone length to match the guides.
    
    It returns a map of HumanIK / guide names to the T-stance position.
    """

    pass


def hikGetControlRig(character):
    """
    This method returns the control rig of the given HumanIK character if it
    exists, or the empty string otherwise.
    """

    pass


def qrDeleteGuidesNode(character):
    """
    This method deletes the guides from the given character, if any.
    
    It returns True if the guides were deleted, False otherwise.
    """

    pass


def qrGetDefaultTweakParameters():
    """
    This method returns the default tweak parameters for modifying the result
    of the skeletonEmbed command.
    
    At the moment, these are hard-coded, but eventually they should be
    configurable.
    """

    pass


def callback_step3_MirrorGuidesLeftToRight(*args, **kwargs):
    pass


def hikRenameDefinition(character):
    """
    This method opens the dialog allowing the user to rename the given HumanIK
    character.
    """

    pass


def getOutput_step2(input):
    pass


def callback_step1_SelectAllMeshes(tool):
    """
    # This callback can work without any pre-condition.
    """

    pass


def getInput_step5(input):
    pass


def isCloseEnough(a, b, epsilon=1e-06):
    """
    This method checks whether two values are close to one another within a
    given tolerance.
    """

    pass


def hikGetJointNodeName(character, jointName):
    """
    This method returns the joint node name in the given HumanIK character for
    the given generic HumanIK joint name.
    
    It does so by following the connection to the character node from the the
    required joint node.
    """

    pass


def callback_step3_ShowAllGuides(*args, **kwargs):
    pass


def convertFoot(tweakParameters, kneePosition, anklePosition, footPosition):
    """
    This method takes the position of the foot guides coming out of the
    embedding algorithm (knee, ankle and foot) and maps them to foot joints
    that fits what HumanIK expects.
    """

    pass


def listMirroredJoints(mapGuideToScene, guidesNode, items, leftToRight):
    """
    This methods creates and returns two lists of joints from the list given as
    'items'.  The first list contains tuples where the first element is the
    source joint and the second element is its mirror counterpart.  The second
    list contains the name of joints that do not have a mirror counterpart,
    i.e. center joints.
    
    The direction of source to destination is determined by the truth value of
    the 'leftToRight' parameter.
    
    This method is used when a set of selected joints must be mirrored to be
    applied to their mirror counterpart.
    """

    pass


def callback_AutoRig(tool):
    pass


def centerJoints(center, axis, joints):
    """
    This method centers a list of joints so they lie directly on the mirror plane.
    """

    pass


def getInputs(tool, level, deleteOutput):
    pass


def qrSetSkeletonRootNode(character, skeletonRootNode):
    """
    This method associates the skeleton root node to the given character.
    """

    pass


def callback_step0_RenameCharacter(tool):
    pass


def getInput_step3(input):
    pass


def detachSkinFromMesh(meshes):
    """
    This method unbinds the skin for all the meshes in the given list, if any.
    """

    pass


def positionHikControlRig(definition, positions):
    """
    This method sets the positions of the HumanIK control rig effectors.
    """

    pass


def qruiGetCharacter(tool):
    """
    ###############################################################################
    #                                                                             #
    #  Quick Rig UI utility tools (methods and classes)                           #
    #                                                                             #
    #  These are very specific to the way the QuickRig UI is built.               #
    #                                                                             #
    ###############################################################################
    """

    pass


def getOutput_step1(input):
    pass


def getInput_step1(input):
    pass


def qrGetGuidesColorFromGuidesNode(guidesNode):
    """
    This method sets the color from the guides node.
    
    It returns the color of the root of all the guides.
    """

    pass


def qruiRefreshMeshes(tool):
    pass


def getSelectedShapes(shapeTypes=None):
    """
    This method returns the list of all currently selected shapes.
    
    It returns the actual shapes, i.e. the name of the shape nodes, not the
    transform nodes.
    """

    pass


def callbackUtil_step3_MirrorGuides(input, leftToRight):
    pass


def qrSetGuidesNode(character, guidesNode):
    """
    This method associates the guides node to the given character.
    """

    pass


def qrGetBoundingBoxFromGuidesNode(guidesNode):
    """
    This method extracts from the guides node an object representing the
    bounding box of the mesh(es) used for embedding.
    """

    pass


def qruiGetGuidesColor(tool):
    pass


def convertSpine(tweakParameters, spineCount, wantHipsTranslation, hipsPosition, backPosition, shouldersPosition):
    """
    This method takes the position of the spine guides coming out of the
    embedding algorithm (hips, back and shoulders) and maps them to spine
    joints that fits what HumanIK expects.
    """

    pass


def mirrorJoints(center, axis, joints):
    """
    This method applies mirroring to a list of joints.
    """

    pass


def callback_step3_HideAllGuides(*args, **kwargs):
    pass


def getSelectedMeshes():
    """
    This method returns the list of all currently selected meshes.
    
    It returns the actual meshes, i.e. the name of the shape nodes, not the
    transform nodes.
    """

    pass


def degrees(*args, **kwargs):
    """
    degrees(x)
    
    Convert angle x from radians to degrees.
    """

    pass


def listAveragedJoints(mapGuideToScene):
    """
    This methods creates and returns two lists of joints from the list given as
    'items'.  The first list contains unique tuples where the second element is
    the mirror counterpart of the first element.  The second list contains the
    name of joints that do not have a mirror counterpart, i.e. center joints.
    
    This method is used when all of the joints need to be averaged with their
    mirror counterpart, relative to their position with regards to the mirror
    plane.
    """

    pass


def callback_scriptJob_uiDeleted(tool):
    pass


def hikInitialize():
    """
    This method makes sure the HumanIK tool is loaded and visible.
    """

    pass


def hikGetEffectorNodeName(character, effectorName):
    """
    This method returns the effector node name in the given HumanIK character
    for the given generic HumanIK effector name.
    """

    pass


def removeOutput_step2(input):
    pass


def enableXRayJoints(enabled):
    """
    This method enables "X-Ray Joints" option on all viewports.
    """

    pass


def qrMirrorGuides(guidesNode, center, axis, leftToRight, guides):
    """
    This method mirrors the given guides with regards to the center.
    
    Each guide in the given guides can either be:
    - A center guide (in which case the guide is brought to the center plane)
    - A symmetry guide (in which case it serves at a source that is applied to
      its corresponding symmetric guide)
    - Not a guide (in which case nothing is done)
    """

    pass


def qruiRefreshGuidesColor(tool):
    pass


def qrGetRequiredGuides(skeletonParameters):
    """
    This method returns a list of the guides corresponding to the given skeleton parameters.
    
    It should be in sync with the output of:
    - qrGetGuidesFromEmbedding( )
    """

    pass


def averageJoints(center, axis, joints):
    """
    This method averages a list of joints so that they become perfectly
    symmetric with regards to the mirror plane.
    """

    pass


def callback_step0_ChangeMode(tool):
    pass


def callback_step0_DeleteCharacter(*args, **kwargs):
    pass


def setDefaultOptionsGVB(resolution):
    """
    This method sets the necessary variables to have reasonable default
    parameters to perform geodesic voxel binding that gives good results on a
    wide majority of cases.
    """

    pass


def removeOutput_step4(input):
    pass


def qrSetGuidesVisibility(guidesNode, visible):
    """
    This method sets the visibility attributes on all the guide nodes.
    """

    pass


def qrInitialize():
    """
    This method makes sure all of the needed dependencies are loaded and
    initialized.
    
    This makes sure skinning shapes scripts are loaded, as well as HumanIK
    scripts.
    """

    pass


def hikNoneString():
    """
    This method returns the string to display when no character is selected.
    """

    pass


def callback_step0_CreateCharacter(tool):
    pass


def hikCreateCharacter(nameHint):
    """
    This method creates a new HumanIK character trying to use the given name
    hint to name the new character.
    """

    pass


def callback_step3_SelectAllGuides(*args, **kwargs):
    pass


def qrAddInfoAttribute(character):
    """
    This method adds the Quick Rig info attribute to the character node.
    
    This attribute is a compound that holds information about meshes and guides
    associated with this character.
    """

    pass


def callback_step0_UpdateCharacterButtons(tool):
    """
    ###############################################################################
    #                                                                             #
    #  UI callbacks                                                               #
    #                                                                             #
    ###############################################################################
    """

    pass


def convertHand(tweakParameters, elbowPosition, handPosition):
    """
    This method takes the position of the hand guides coming out of the
    embedding algorithm (elbow and hand) and maps them to hand joints that
    fits what HumanIK expects.
    """

    pass


def hikDeleteWholeCharacter(character):
    """
    This method deletes the given HumanIK character.
    
    It deletes its control rig (if any), its skeleton (if any) and its
    character definition.
    """

    pass


def qrGetGuidesPositions(character):
    """
    This method returns position of each guide node associated with the given
    character, if any.
    """

    pass


def hikCreateControlRig(character):
    """
    This method creates a control rig for the given HumanIK character.
    """

    pass


def convertNeck(tweakParameters, neckCount, shouldersPosition, headPosition, boundingBox):
    """
    This method takes the position of the neck guides coming out of the
    embedding algorithm (shoulders and neck) and maps them to neck joints that
    fits what HumanIK expects.
    """

    pass


def getOutput_step5(input):
    pass


def fabs(*args, **kwargs):
    """
    fabs(x)
    
    Return the absolute value of the float x.
    """

    pass


def qrGetSkeletonRootNode(character):
    """
    This method returns the root node of the skeleton associated with the given
    character, if any.
    """

    pass


def qrGetSceneCharacters():
    """
    This method returns a list of names for all HumanIK characters in the
    current scene that have been created using the Quick Rig tool.
    """

    pass


def tool_to_input(level, deleteOutput=True):
    """
    This decorator takes a function which takes "callback input" and wraps it
    into a function which takes the tool as an input.
    
    Callback input is extracted from the character and the tool based on the
    given level required, each level corresponding to a step of the rigging
    process.  The decorator handles making sure that output of further steps is
    deleted if allowed by the user.
    """

    pass


def positionHikSkeleton(orderedJoints, skeletonNodes, positions, jointOrients):
    """
    This method sets the positions and joint orientations for a HumanIK skeleton.
    """

    pass


def callback_step4_CreateSkeleton(*args, **kwargs):
    pass


def qrIsCharacter(character):
    """
    This method checks whether the character was created using the Quick Rig
    tool and therefore can be edited by the tool.
    """

    pass


def callback_step1_AddSelectedMeshes(*args, **kwargs):
    pass


def getInput_step0(input):
    pass


def convertReference(minCorner, maxCorner):
    """
    This method takes the position of bounding box corners and maps them to
    a reference joint that HumanIK expects.
    """

    pass


def qruiSetGuidesColor(tool, color):
    pass


def qrAddMeshes(character, meshesToAdd):
    """
    This method adds the given meshes to the current character.
    """

    pass


def callback_step3_MirrorGuidesRightToLeft(*args, **kwargs):
    pass


def sqrt(*args, **kwargs):
    """
    sqrt(x)
    
    Return the square root of x.
    """

    pass


def OpenQuickRigUI():
    """
    This method is the entry point of the Quick Rig tool.
    
    It creates the Quick Rig tool window and brings it up.
    """

    pass


def qrGetGuidesFromEmbedding(skeletonParameters, tweakParameters, embedding):
    """
    This method takes the embedding returned by the skeletonEmbed command and
    converts it to the skeleton guides.
    
    It can add spine, neck and shoulder (clavicle) joints if requested.
    """

    pass


def getOutput_step3(input):
    pass


def callback_step3_ChooseGuidesColor(tool):
    """
    # This callback can work without any pre-condition.
    """

    pass


def qrClearMeshes(character):
    """
    This method removes all of the meshes associated with the given character.
    """

    pass


def convertShoulder(tweakParameters, shoulderCount, shouldersPosition, leftShoulderPosition, rightShoulderPosition):
    """
    This method takes the position of the shoulder guides coming out of the
    embedding algorithm (shoulders and left/right shoulder) and maps them to
    clavicle joints that fits what HumanIK expects.
    """

    pass


def qrGetGuidesNodesFromGuidesNode(guidesNode):
    """
    This method extracts from the guides node a dictionary associating a guide
    name to the name of the node representing it in the current embedding.
    """

    pass


def qrRefreshMeshes(character):
    """
    This method makes sure meshes associated with the given character are
    stored properly in the character.
    
    It makes sure everything connected is actually a mesh, no mesh is
    duplicated and the mesh array is tightly packed.
    """

    pass


def callback_step3_EnableXRayJoints(tool):
    """
    # This callback can work without any pre-condition.
    """

    pass


def hikSetCurrentCharacter(character):
    """
    This method sets the given HumanIK character as the global current HumanIK
    character.
    """

    pass


def callback_step4_DeleteSkeleton(*args, **kwargs):
    pass


def createReferential(xVector, zTargetVector, zBackupTargetVector):
    """
    This method create a rotation matrix representing a referential
    described by the given vectors.
    
    The matrix will take a point in the local referential and convert it to
    "world" referential.
    
    The X axis of the referential will be oriented towards the given xVector.
    The Z axis will be oriented towards the given zTargetVector, but it will
    be made orthogonal to the X axis.  The Y axis will be chosen as a
    complement of the two others to create a right-handed system.
    """

    pass


def createHikSkeleton(character, skeletonParameters):
    """
    This method creates a HumanIK skeleton from a set of parameters
    corresponding to what can be set in the HumanIK skeleton generation tool.
    
    It uses the skeleton generator node, but deletes it when its done.
    """

    pass


def getOutput_step0(input):
    pass


def callback_scriptJob_deleteAll(tool):
    pass


def hikGetSceneCharacters():
    """
    This method returns a list of names for all HumanIK characters in the
    current scene.
    """

    pass


def callback_step0_RefreshCharacterList(tool):
    pass


def removeOutput_step1(input):
    pass


def qruiEnableGuidesColor(tool, enabled):
    pass


def qrAverageGuides(guidesNode, center, axis):
    """
    This method averages guides with regards to the center.
    """

    pass


def hikGetCurrentCharacter():
    """
    This method returns the name of the current HumanIK character.
    """

    pass


def callback_step2_ShowSegmentationHelp(tool):
    """
    # This callback can work without any pre-condition.
    """

    pass


def callback_step5_DeleteSkin(*args, **kwargs):
    pass


def removeOutput_step3(input):
    pass


def getOutput_step4(input):
    pass


def removeOutput_step0(input):
    pass


def qrCreateGuidesNode(embedding):
    """
    This method creates a node in the scene that will store the embedding
    information returned by the skeletonEmbed command.
    
    It will create a root joint to which will be parented one joint for each
    joint in the embedding.  It will also store bounding box information
    as an attribute on that root joint.
    """

    pass


def callback_step1_ClearMeshes(*args, **kwargs):
    pass


def hikGetSkeletonGeneratorNode(character):
    """
    This method returns the name of the skeleton generator node associated with
    the given HumanIK character if it exists, or the empty string otherwise.
    """

    pass


def callback_step2_DeleteGuides(*args, **kwargs):
    pass


def hikDeleteControlRig(character):
    """
    This method deletes the control rig (if any) for the given HumanIK
    character.
    """

    pass


def getInput_step2(input):
    pass


def callback_step5_BindOptions(*args, **kwargs):
    pass


def hikGetSkeletonNodesMap(character):
    """
    This method returns the scene joints for the skeleton associated with the
    given character, if any.
    """

    pass


def checkIfSkinExists(meshes):
    """
    This method returns True if any of the mesh in the given list has an
    associated skin cluster, False otherwise.
    """

    pass


def computeJointOrients(hikInfos, positions, useOrientation, orientTowardsChild):
    """
    This method computes the joint orientations for a given character, given
    the position of the guides.
    
    It returns a map of HumanIK / guide names to the desired referential.
    """

    pass


def computeNeededJointOrient(targetMatrix, currentMatrix):
    """
    This method compute the value needed for the joint orient attribute so that
    the given joint orientation is the one given by the target, knowing that
    its current rotation is given by the current matrix.
    """

    pass


def qrGetMeshes(character):
    """
    This method returns the list of meshes associated with the given character,
    if any.
    """

    pass


def qrDeleteSkeleton(character):
    """
    This method deletes the skeleton from the given character, if any.
    
    It returns True if the skeleton was deleted, False otherwise.
    """

    pass



kTweakFootToeRatio = 0.4

kDisabledGuidesColor = []

kFrameMarginHeight = 4

kFrameParam = {}

kGuidesColor = []

kRowLayoutHeight = 21

kSymmetryOptions = []

kResolutions = []

kCharacterUpAxis = 1

kColorSwatchHeight = 30

kMeshesAttributeName = 'meshes'

kOptionsTextWidth = 90

kTweakFootUseCorrectedAnkleForToe = False

kGuidesAttributeName = 'guides'

kFrameMarginWidth = 25

kColorSwatchColorHeight = 15

kOrientJointsOptions = []

kQuickRigInfoAttributeName = 'quickRigInfo'

kCharacterDownDirection = 0

kOptionsButtonWidth = 40

kSkinBindingOptions = []

kTweakShoulderRatio = 0.6

kSkeletonFieldWidth = 60

kTweakFootAnkleRatio = 0.2

kSkeletonAttributeName = 'skeleton'

kTweakFoot = True

kTweakNeckLastRatio = 0.45

kTweakNeckFirstRatio = 0.25


