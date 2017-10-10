import exceptions

"""
A quick example::

    from pymel.api.plugins import Command
    class testCmd(Command):
        def doIt(self, args):
            print "doIt..."

    testCmd.register()
    cmds.testCmd()
    testCmd.deregister()

An example of a plugin which creates a node::

    import math

    import pymel.api.plugins as plugins
    import maya.OpenMaya as om

    class PymelSineNode(plugins.DependNode):
        '''Example node adapted from maya's example sine node plugin

        Shows how much easier it is to create a plugin node using pymel.api.plugins
        '''
        # For quick testing, if _typeId is not defined, pymel will create one by
        # hashing the node name. For longer-term uses, you should explicitly set
        # own typeId like this
        #
        # (NOTE - if using the automatic typeId generation, the hashlib python
        # builtin library must be functional / working from within maya... due
        # to dynamic library linking issues (ie, libssl, libcrypto), this
        # may not always be the case out-of-the-box on some linux distros
        _typeId = om.MTypeId(0x900FF)

        # by default, the name of the node will be the name of the class - to
        # override and set your own maya node name, do this:
        #_name = 'PymelSineNode'

        @classmethod
        def initialize(cls):
            # input
            nAttr = om.MFnNumericAttribute()
            cls.input = nAttr.create( "input", "in", om.MFnNumericData.kFloat, 0.0 )
            nAttr.setStorable(1)
            cls.addAttribute( cls.input )

            # output
            cls.output = nAttr.create( "output", "out", om.MFnNumericData.kFloat, 0.0 )
            nAttr.setStorable(1)
            nAttr.setWritable(1)
            cls.addAttribute( cls.output )

            # set attributeAffects relationships
            cls.attributeAffects( cls.input, cls.output )

        def compute(self, plug, dataBlock):
            if ( plug == self.output ):
                dataHandle = dataBlock.inputValue( self.input )
                inputFloat = dataHandle.asFloat()
                result = math.sin( inputFloat )
                outputHandle = dataBlock.outputValue( self.output )
                outputHandle.setFloat( result )
                dataBlock.setClean( plug )
                return om.MStatus.kSuccess
            return om.MStatus.kUnknownParameter

    ## initialize the script plug-in
    def initializePlugin(mobject):
        PymelSineNode.register(mobject)

    # uninitialize the script plug-in
    def uninitializePlugin(mobject):
        PymelSineNode.deregister(mobject)
"""

from maya.OpenMayaMPx import MPxTransform as _mpx
from maya.OpenMayaMPx import MPxLocatorNode as _mpxCls

class _DummyPluginNodesMaker(object):
    def __enter__(self):
        pass
    
    
    def __exit__(self, type, value, traceback):
        pass
    
    
    def __init__(self, dummyClasses=None, alreadyCreated=None):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class PluginError(exceptions.Exception):
    """
    #===============================================================================
    # Errors
    #===============================================================================
    """
    
    
    
    __weakref__ = None


class PyNodeMethod(object):
    """
    Used as a decorator, placed on methods on a plugin node class, to signal
    that these methods should be placed on to PyNode objects constructed for
    the resulting depend nodes.
    
    >>> class FriendlyNode(DependNode):
    ...     _typeId = om.MTypeId(654748)
    ...     @PyNodeMethod
    ...     def introduce(self):
    ...         print "Hi, I'm an instance of a MyNode PyNode - my name is %s!" % self.name()
    >>> FriendlyNode.register()
    >>> import pymel.core as pm
    >>> frank = pm.createNode('FriendlyNode', name='Frank')
    >>> frank.introduce()
    Hi, I'm an instance of a MyNode PyNode - my name is Frank!
    """
    
    
    
    def __init__(self, func, name=None):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class BasePluginMixin(object):
    def create(cls):
        pass
    
    
    def deregister(cls, plugin=None):
        """
        If using from within a plugin module's ``initializePlugin`` or
        ``uninitializePlugin`` callback, pass along the MObject given to these
        functions.
        """
    
        pass
    
    
    def getMpxType(cls):
        pass
    
    
    def getTypeId(cls, nodeName=None):
        """
        # Defined here just so it can be shared between MPxTransformationMatrix
        # and DependNode
        """
    
        pass
    
    
    def isRegistered(cls):
        pass
    
    
    def mayaName(cls):
        pass
    
    
    def register(cls, plugin=None):
        """
        Used to register this MPx object wrapper with the maya plugin.
        
        By default the command will be registered to a dummy plugin provided by pymel.
        
        If using from within a plugin module's ``initializePlugin`` or
        ``uninitializePlugin`` callback, pass along the MObject given to these
        functions.
        
        When implementing the derived MPx wrappers, do not override this -
        instead, override _registerOverride
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


import maya.OpenMayaMPx as mpx

class DependNode(BasePluginMixin, mpx.MPxNode):
    def getTypeEnum(cls):
        pass
    
    
    def initialize(cls):
        pass
    
    
    def isAbstractClass(cls):
        pass


class Command(BasePluginMixin, mpx.MPxCommand):
    """
    create a subclass of this with a doIt method
    """
    
    
    
    def createSyntax(cls):
        pass


class TransformationMatrix(BasePluginMixin, mpx.MPxTransformationMatrix):
    def deregister(cls, plugin=None):
        pass
    
    
    def register(cls, plugin=None):
        pass


class PluginRegistryError(PluginError):
    pass


class ManipulatorNode(DependNode, mpx.MPxManipulatorNode):
    pass


class CameraSet(DependNode, mpx.MPxCameraSet):
    pass


class AlreadyRegisteredError(PluginRegistryError):
    pass


class LocatorNode(DependNode, _mpxCls):
    pass


class Assembly(DependNode, mpx.MPxAssembly):
    pass


class Transform(DependNode, _mpx):
    pass


class IkSolverNode(DependNode, mpx.MPxIkSolverNode):
    pass


class SurfaceShape(DependNode, mpx.MPxSurfaceShape):
    pass


class HardwareShader(DependNode, mpx.MPxHardwareShader):
    pass


class SpringNode(DependNode, mpx.MPxSpringNode):
    pass


class FieldNode(DependNode, mpx.MPxFieldNode):
    pass


class ParticleAttributeMapperNode(DependNode, mpx.MPxParticleAttributeMapperNode):
    pass


class EmitterNode(DependNode, mpx.MPxEmitterNode):
    pass


class MotionPathNode(DependNode, mpx.MPxMotionPathNode):
    pass


class Constraint(DependNode, mpx.MPxConstraint):
    pass


class NotRegisteredError(PluginRegistryError):
    pass


class ManipContainer(DependNode, mpx.MPxManipContainer):
    pass


class BlendShape(DependNode, mpx.MPxBlendShape):
    pass


class ImagePlane(DependNode, mpx.MPxImagePlane):
    pass


class HwShaderNode(DependNode, mpx.MPxHwShaderNode):
    pass


class SkinCluster(DependNode, mpx.MPxSkinCluster):
    pass


class GeometryFilter(DependNode, mpx.MPxGeometryFilter):
    pass


class PolyTrg(DependNode, mpx.MPxPolyTrg):
    pass


class ObjectSet(DependNode, mpx.MPxObjectSet):
    pass


class DeformerNode(DependNode, mpx.MPxDeformerNode):
    pass


class ComponentShape(SurfaceShape, mpx.MPxComponentShape):
    pass


class FluidEmitterNode(EmitterNode, mpx.MPxFluidEmitterNode):
    pass



def enumToStr():
    """
    Returns a dictionary mapping from an MPxNode node type enum to it's
    string name.
    Useful for debugging purposes.
    """

    pass


def _guessEnumStrFromMpxClass(className):
    pass


def _loadPlugin():
    pass


def _suggestNewMPxValues(classes=None):
    pass


def loadAllMayaPlugins():
    """
    will load all maya-installed plugins
    
    WARNING: tthe act of loading all the plugins may crash maya, especially if
    done from a non-GUI session
    """

    pass


def _pluginModule():
    pass


def _buildAll():
    pass


def _getPlugin(object=None):
    pass


def uninitializePlugin(mobject):
    """
    do not call directly
    """

    pass


def unloadAllPlugins(skipErrors=False, exclude=('DirectConnect',)):
    pass


def _buildMpxNamesToMayaNodes(hierarchy=None):
    pass


def _createDummyPluginNodeClasses():
    """
    Registers with the dummy pymel plugin a dummy node type for each MPxNode
    subclass
    
    returns a dictionary mapping from MPx class to a pymel dummy class of that
    type
    """

    pass


def allMPx():
    """
    Returns a list of all MPx classes
    """

    pass


def _buildPluginHierarchy(dummyClasses=None):
    """
    Dynamically query the mel node hierarchy for all plugin node types
    
    This command must be run from within a running maya session - ie, where
    maya.cmds, etc are accessible.
    """

    pass


def pluginCommands(pluginName, reportedOnly=False):
    """
    Returns the list of all commands that the plugin provides, to the best
    of our knowledge.
    
    Note that depending on your version of maya, this may not actually be the
    list of all commands provided.
    """

    pass


def _buildMpxNamesToApiEnumNames(dummyClasses=None, dummyNodes=None):
    pass


def mayaPlugins():
    """
    all maya plugins in the maya install directory
    """

    pass


def _pluginName():
    pass


def _unloadPlugin():
    pass


def initializePlugin(mobject):
    """
    do not call directly
    """

    pass


def _pluginFile():
    pass



mpxNamesToApiEnumNames = {}

missingMPx = []

pluginMayaTypes = set()

mpxNamesToMayaNodes = {}

mpxClassesToMpxEnums = {}

_enumToStr = None

registered = set()

UNREPORTED_COMMANDS = {}

pyNodeMethods = {}

_allMPx = []

NON_CREATABLE = set()

mpxNamesToEnumNames = {}

_new = []


