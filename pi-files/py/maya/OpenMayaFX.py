from __builtin__ import property as _swig_property
from __builtin__ import object as _object

class MDynSweptTriangle(_object):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def area(*args, **kwargs):
        pass
    
    
    def normal(*args, **kwargs):
        pass
    
    
    def normalToPoint(*args, **kwargs):
        pass
    
    
    def uvPoint(*args, **kwargs):
        pass
    
    
    def vertex(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    thisown = None
    
    __swig_destroy__ = None


class MnObject(_object):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    thisown = None
    
    __swig_destroy__ = None


class new_instancemethod(_object):
    """
    instancemethod(function, instance, class)
    
    Create an instance method object.
    """
    
    
    
    def __call__(*args, **kwargs):
        """
        x.__call__(...) <==> x(...)
        """
    
        pass
    
    
    def __cmp__(*args, **kwargs):
        """
        x.__cmp__(y) <==> cmp(x,y)
        """
    
        pass
    
    
    def __delattr__(*args, **kwargs):
        """
        x.__delattr__('name') <==> del x.name
        """
    
        pass
    
    
    def __get__(*args, **kwargs):
        """
        descr.__get__(obj[, type]) -> value
        """
    
        pass
    
    
    def __getattribute__(*args, **kwargs):
        """
        x.__getattribute__('name') <==> x.name
        """
    
        pass
    
    
    def __hash__(*args, **kwargs):
        """
        x.__hash__() <==> hash(x)
        """
    
        pass
    
    
    def __repr__(*args, **kwargs):
        """
        x.__repr__() <==> repr(x)
        """
    
        pass
    
    
    def __setattr__(*args, **kwargs):
        """
        x.__setattr__('name', value) <==> x.name = value
        """
    
        pass
    
    
    __func__ = None
    
    __self__ = None
    
    im_class = None
    
    im_func = None
    
    im_self = None
    
    __new__ = None


class MDynamicsUtil(_object):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def addNodeTypeToRunup(*args, **kwargs):
        pass
    
    
    def evalDynamics2dTexture(*args, **kwargs):
        pass
    
    
    def hasValidDynamics2dTexture(*args, **kwargs):
        pass
    
    
    def inRunup(*args, **kwargs):
        pass
    
    
    def removeNodeTypeFromRunup(*args, **kwargs):
        pass
    
    
    def runupIfRequired(*args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    thisown = None
    
    __swig_destroy__ = None


from . import OpenMaya

class MFnNObjectData(OpenMaya.MFnData):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def create(*args, **kwargs):
        pass
    
    
    def getClothObjectPtr(*args, **kwargs):
        pass
    
    
    def getCollide(*args, **kwargs):
        pass
    
    
    def getParticleObjectPtr(*args, **kwargs):
        pass
    
    
    def getRigidObjectPtr(*args, **kwargs):
        pass
    
    
    def isCached(*args, **kwargs):
        pass
    
    
    def setCached(*args, **kwargs):
        pass
    
    
    def setObjectPtr(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MnSolver(_object):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def addNObject(*args, **kwargs):
        pass
    
    
    def createNSolver(*args, **kwargs):
        pass
    
    
    def makeAllCollide(*args, **kwargs):
        pass
    
    
    def removeAllCollisions(*args, **kwargs):
        pass
    
    
    def removeNObject(*args, **kwargs):
        pass
    
    
    def setAirDensity(*args, **kwargs):
        pass
    
    
    def setDisabled(*args, **kwargs):
        pass
    
    
    def setGravity(*args, **kwargs):
        pass
    
    
    def setGravityDir(*args, **kwargs):
        pass
    
    
    def setMaxIterations(*args, **kwargs):
        pass
    
    
    def setStartTime(*args, **kwargs):
        pass
    
    
    def setSubsteps(*args, **kwargs):
        pass
    
    
    def setWindDir(*args, **kwargs):
        pass
    
    
    def setWindNoiseIntensity(*args, **kwargs):
        pass
    
    
    def setWindSpeed(*args, **kwargs):
        pass
    
    
    def solve(*args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    thisown = None
    
    __swig_destroy__ = None


class MFnInstancer(OpenMaya.MFnDagNode):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def allInstances(*args, **kwargs):
        pass
    
    
    def instancesForParticle(*args, **kwargs):
        pass
    
    
    def particleCount(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MHairSystem(_object):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    def getCollisionObject(*args, **kwargs):
        pass
    
    
    def getFollicle(*args, **kwargs):
        pass
    
    
    def registerCollisionSolverCollide(*args, **kwargs):
        pass
    
    
    def registerCollisionSolverPreFrame(*args, **kwargs):
        pass
    
    
    def registeringCallableScript(*args, **kwargs):
        pass
    
    
    def setRegisteringCallableScript(*args, **kwargs):
        pass
    
    
    def unregisterCollisionSolverCollide(*args, **kwargs):
        pass
    
    
    def unregisterCollisionSolverPreFrame(*args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    thisown = None
    
    __swig_destroy__ = None


class MFnFluid(OpenMaya.MFnDagNode):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def create2D(*args, **kwargs):
        pass
    
    
    def create3D(*args, **kwargs):
        pass
    
    
    def density(*args, **kwargs):
        pass
    
    
    def emitIntoArrays(*args, **kwargs):
        pass
    
    
    def expandToInclude(*args, **kwargs):
        pass
    
    
    def falloff(*args, **kwargs):
        pass
    
    
    def fuel(*args, **kwargs):
        pass
    
    
    def getColorMode(*args, **kwargs):
        pass
    
    
    def getColors(*args, **kwargs):
        pass
    
    
    def getCoordinateMode(*args, **kwargs):
        pass
    
    
    def getCoordinates(*args, **kwargs):
        pass
    
    
    def getDensityMode(*args, **kwargs):
        pass
    
    
    def getDimensions(*args, **kwargs):
        pass
    
    
    def getFalloffMode(*args, **kwargs):
        pass
    
    
    def getForceAtPoint(*args, **kwargs):
        pass
    
    
    def getFuelMode(*args, **kwargs):
        pass
    
    
    def getResolution(*args, **kwargs):
        pass
    
    
    def getTemperatureMode(*args, **kwargs):
        pass
    
    
    def getVelocity(*args, **kwargs):
        pass
    
    
    def getVelocityMode(*args, **kwargs):
        pass
    
    
    def gridSize(*args, **kwargs):
        pass
    
    
    def index(*args, **kwargs):
        pass
    
    
    def isAutoResize(*args, **kwargs):
        pass
    
    
    def isResizeToEmitter(*args, **kwargs):
        pass
    
    
    def pressure(*args, **kwargs):
        pass
    
    
    def setColorMode(*args, **kwargs):
        pass
    
    
    def setCoordinateMode(*args, **kwargs):
        pass
    
    
    def setDensityMode(*args, **kwargs):
        pass
    
    
    def setFalloffMode(*args, **kwargs):
        pass
    
    
    def setFuelMode(*args, **kwargs):
        pass
    
    
    def setSize(*args, **kwargs):
        pass
    
    
    def setTemperatureMode(*args, **kwargs):
        pass
    
    
    def setVelocityMode(*args, **kwargs):
        pass
    
    
    def temperature(*args, **kwargs):
        pass
    
    
    def toGridIndex(*args, **kwargs):
        pass
    
    
    def updateGrid(*args, **kwargs):
        pass
    
    
    def velocityGridSizes(*args, **kwargs):
        pass
    
    
    def voxelCenterPosition(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None
    
    
    kCenterGradient = 7
    
    
    kConstant = 0
    
    
    kDynamicColorGrid = 2
    
    
    kDynamicGrid = 2
    
    
    kFixed = 0
    
    
    kGradient = 3
    
    
    kGrid = 1
    
    
    kNegXGradient = 4
    
    
    kNegYGradient = 5
    
    
    kNegZGradient = 6
    
    
    kNoFalloffGrid = 0
    
    
    kStaticColorGrid = 1
    
    
    kStaticFalloffGrid = 1
    
    
    kStaticGrid = 1
    
    
    kUseShadingColor = 0
    
    
    kXGradient = 1
    
    
    kYGradient = 2
    
    
    kZGradient = 3
    
    
    kZero = 0


class MFnParticleSystem(OpenMaya.MFnDagNode):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def acceleration(*args, **kwargs):
        pass
    
    
    def age(*args, **kwargs):
        pass
    
    
    def betterIllum(*args, **kwargs):
        pass
    
    
    def castsShadows(*args, **kwargs):
        pass
    
    
    def count(*args, **kwargs):
        pass
    
    
    def create(*args, **kwargs):
        pass
    
    
    def deformedParticleShape(*args, **kwargs):
        pass
    
    
    def disableCloudAxis(*args, **kwargs):
        pass
    
    
    def emission(*args, **kwargs):
        pass
    
    
    def emit(*args, **kwargs):
        pass
    
    
    def evaluateDynamics(*args, **kwargs):
        pass
    
    
    def flatShaded(*args, **kwargs):
        pass
    
    
    def getPerParticleAttribute(*args, **kwargs):
        pass
    
    
    def hasEmission(*args, **kwargs):
        pass
    
    
    def hasLifespan(*args, **kwargs):
        pass
    
    
    def hasOpacity(*args, **kwargs):
        pass
    
    
    def hasRgb(*args, **kwargs):
        pass
    
    
    def isDeformedParticleShape(*args, **kwargs):
        pass
    
    
    def isPerParticleDoubleAttribute(*args, **kwargs):
        pass
    
    
    def isPerParticleIntAttribute(*args, **kwargs):
        pass
    
    
    def isPerParticleVectorAttribute(*args, **kwargs):
        pass
    
    
    def isValid(*args, **kwargs):
        pass
    
    
    def lifespan(*args, **kwargs):
        pass
    
    
    def mass(*args, **kwargs):
        pass
    
    
    def opacity(*args, **kwargs):
        pass
    
    
    def originalParticleShape(*args, **kwargs):
        pass
    
    
    def particleIds(*args, **kwargs):
        pass
    
    
    def particleName(*args, **kwargs):
        pass
    
    
    def position(*args, **kwargs):
        pass
    
    
    def position0(*args, **kwargs):
        pass
    
    
    def position1(*args, **kwargs):
        pass
    
    
    def primaryVisibility(*args, **kwargs):
        pass
    
    
    def radius(*args, **kwargs):
        pass
    
    
    def radius0(*args, **kwargs):
        pass
    
    
    def radius1(*args, **kwargs):
        pass
    
    
    def receiveShadows(*args, **kwargs):
        pass
    
    
    def renderType(*args, **kwargs):
        pass
    
    
    def rgb(*args, **kwargs):
        pass
    
    
    def saveInitialState(*args, **kwargs):
        pass
    
    
    def setCount(*args, **kwargs):
        pass
    
    
    def setPerParticleAttribute(*args, **kwargs):
        pass
    
    
    def surfaceShading(*args, **kwargs):
        pass
    
    
    def tailSize(*args, **kwargs):
        pass
    
    
    def threshold(*args, **kwargs):
        pass
    
    
    def velocity(*args, **kwargs):
        pass
    
    
    def visibleInReflections(*args, **kwargs):
        pass
    
    
    def visibleInRefractions(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None
    
    
    kBlobby = 2
    
    
    kCloud = 0
    
    
    kMultiPoint = 3
    
    
    kMultiStreak = 4
    
    
    kNumeric = 5
    
    
    kPoints = 6
    
    
    kSpheres = 7
    
    
    kSprites = 8
    
    
    kStreak = 9
    
    
    kTube = 1


class MFnField(OpenMaya.MFnDagNode):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def attenuation(*args, **kwargs):
        pass
    
    
    def falloffCurve(*args, **kwargs):
        pass
    
    
    def getForceAtPoint(*args, **kwargs):
        pass
    
    
    def isFalloffCurveConstantOne(*args, **kwargs):
        pass
    
    
    def magnitude(*args, **kwargs):
        pass
    
    
    def maxDistance(*args, **kwargs):
        pass
    
    
    def perVertex(*args, **kwargs):
        pass
    
    
    def setAttenuation(*args, **kwargs):
        pass
    
    
    def setMagnitude(*args, **kwargs):
        pass
    
    
    def setMaxDistance(*args, **kwargs):
        pass
    
    
    def setPerVertex(*args, **kwargs):
        pass
    
    
    def setUseMaxDistance(*args, **kwargs):
        pass
    
    
    def useMaxDistance(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MRenderLineArray(_object):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def assign(*args, **kwargs):
        pass
    
    
    def deleteArray(*args, **kwargs):
        pass
    
    
    def length(*args, **kwargs):
        pass
    
    
    def renderLine(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    thisown = None
    
    __swig_destroy__ = None


class MDynSweptLine(_object):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def length(*args, **kwargs):
        pass
    
    
    def normal(*args, **kwargs):
        pass
    
    
    def tangent(*args, **kwargs):
        pass
    
    
    def vertex(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    thisown = None
    
    __swig_destroy__ = None


class MFnNIdData(OpenMaya.MFnData):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def create(*args, **kwargs):
        pass
    
    
    def getObjectPtr(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MFnPfxGeometry(OpenMaya.MFnDagNode):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def getBoundingBox(*args, **kwargs):
        pass
    
    
    def getLineData(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MFnDynSweptGeometryData(OpenMaya.MFnData):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def create(*args, **kwargs):
        pass
    
    
    def lineCount(*args, **kwargs):
        pass
    
    
    def sweptLine(*args, **kwargs):
        pass
    
    
    def sweptTriangle(*args, **kwargs):
        pass
    
    
    def triangleCount(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MRenderLine(_object):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def assign(*args, **kwargs):
        pass
    
    
    def getColor(*args, **kwargs):
        pass
    
    
    def getFlatness(*args, **kwargs):
        pass
    
    
    def getIncandescence(*args, **kwargs):
        pass
    
    
    def getLine(*args, **kwargs):
        pass
    
    
    def getParameter(*args, **kwargs):
        pass
    
    
    def getTransparency(*args, **kwargs):
        pass
    
    
    def getTwist(*args, **kwargs):
        pass
    
    
    def getWidth(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    thisown = None
    
    __swig_destroy__ = None


class MFnVolumeAxisField(MFnField):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def detailTurbulence(*args, **kwargs):
        pass
    
    
    def direction(*args, **kwargs):
        pass
    
    
    def directionalSpeed(*args, **kwargs):
        pass
    
    
    def invertAttenuation(*args, **kwargs):
        pass
    
    
    def setDirection(*args, **kwargs):
        pass
    
    
    def setDirectionalSpeed(*args, **kwargs):
        pass
    
    
    def setInvertAttenuation(*args, **kwargs):
        pass
    
    
    def setSpeedAlongAxis(*args, **kwargs):
        pass
    
    
    def setSpeedAroundAxis(*args, **kwargs):
        pass
    
    
    def setSpeedAwayFromAxis(*args, **kwargs):
        pass
    
    
    def setSpeedAwayFromCenter(*args, **kwargs):
        pass
    
    
    def setTurbulence(*args, **kwargs):
        pass
    
    
    def setTurbulenceFrequency(*args, **kwargs):
        pass
    
    
    def setTurbulenceOffset(*args, **kwargs):
        pass
    
    
    def setTurbulenceSpeed(*args, **kwargs):
        pass
    
    
    def speedAlongAxis(*args, **kwargs):
        pass
    
    
    def speedAroundAxis(*args, **kwargs):
        pass
    
    
    def speedAwayFromAxis(*args, **kwargs):
        pass
    
    
    def speedAwayFromCenter(*args, **kwargs):
        pass
    
    
    def turbulence(*args, **kwargs):
        pass
    
    
    def turbulenceFrequency(*args, **kwargs):
        pass
    
    
    def turbulenceOffset(*args, **kwargs):
        pass
    
    
    def turbulenceSpeed(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MnRigid(MnObject):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def createNRigid(*args, **kwargs):
        pass
    
    
    def getBounce(*args, **kwargs):
        pass
    
    
    def getFriction(*args, **kwargs):
        pass
    
    
    def getInverseMass(*args, **kwargs):
        pass
    
    
    def getNumVertices(*args, **kwargs):
        pass
    
    
    def getPositions(*args, **kwargs):
        pass
    
    
    def getThickness(*args, **kwargs):
        pass
    
    
    def getVelocities(*args, **kwargs):
        pass
    
    
    def setBounce(*args, **kwargs):
        pass
    
    
    def setCollisionFlags(*args, **kwargs):
        pass
    
    
    def setFriction(*args, **kwargs):
        pass
    
    
    def setPositions(*args, **kwargs):
        pass
    
    
    def setThickness(*args, **kwargs):
        pass
    
    
    def setTopology(*args, **kwargs):
        pass
    
    
    def setVelocities(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MFnAirField(MFnField):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def componentOnly(*args, **kwargs):
        pass
    
    
    def direction(*args, **kwargs):
        pass
    
    
    def enableSpread(*args, **kwargs):
        pass
    
    
    def inheritRotation(*args, **kwargs):
        pass
    
    
    def inheritVelocity(*args, **kwargs):
        pass
    
    
    def setComponentOnly(*args, **kwargs):
        pass
    
    
    def setDirection(*args, **kwargs):
        pass
    
    
    def setEnableSpread(*args, **kwargs):
        pass
    
    
    def setInheritRotation(*args, **kwargs):
        pass
    
    
    def setInheritVelocity(*args, **kwargs):
        pass
    
    
    def setSpeed(*args, **kwargs):
        pass
    
    
    def setSpread(*args, **kwargs):
        pass
    
    
    def speed(*args, **kwargs):
        pass
    
    
    def spread(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MFnRadialField(MFnField):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def radialType(*args, **kwargs):
        pass
    
    
    def setType(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MFnDragField(MFnField):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def direction(*args, **kwargs):
        pass
    
    
    def setDirection(*args, **kwargs):
        pass
    
    
    def setUseDirection(*args, **kwargs):
        pass
    
    
    def useDirection(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MFnUniformField(MFnField):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def direction(*args, **kwargs):
        pass
    
    
    def setDirection(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MnCloth(MnObject):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def createNCloth(*args, **kwargs):
        pass
    
    
    def getBounce(*args, **kwargs):
        pass
    
    
    def getFriction(*args, **kwargs):
        pass
    
    
    def getInverseMass(*args, **kwargs):
        pass
    
    
    def getNumVertices(*args, **kwargs):
        pass
    
    
    def getPositions(*args, **kwargs):
        pass
    
    
    def getThickness(*args, **kwargs):
        pass
    
    
    def getVelocities(*args, **kwargs):
        pass
    
    
    def setAddCrossLinks(*args, **kwargs):
        pass
    
    
    def setAirTightness(*args, **kwargs):
        pass
    
    
    def setBendAngleDropoff(*args, **kwargs):
        pass
    
    
    def setBendAngleScale(*args, **kwargs):
        pass
    
    
    def setBendResistance(*args, **kwargs):
        pass
    
    
    def setBendRestAngleFromPositions(*args, **kwargs):
        pass
    
    
    def setBounce(*args, **kwargs):
        pass
    
    
    def setCollisionFlags(*args, **kwargs):
        pass
    
    
    def setComputeRestAngles(*args, **kwargs):
        pass
    
    
    def setComputeRestLength(*args, **kwargs):
        pass
    
    
    def setDamping(*args, **kwargs):
        pass
    
    
    def setDisableGravity(*args, **kwargs):
        pass
    
    
    def setDragAndLift(*args, **kwargs):
        pass
    
    
    def setFriction(*args, **kwargs):
        pass
    
    
    def setIncompressibility(*args, **kwargs):
        pass
    
    
    def setInputMeshAttractAndRigidStrength(*args, **kwargs):
        pass
    
    
    def setInputMeshAttractDamping(*args, **kwargs):
        pass
    
    
    def setInputMeshAttractPositions(*args, **kwargs):
        pass
    
    
    def setInverseMass(*args, **kwargs):
        pass
    
    
    def setLinksRestLengthFromPositions(*args, **kwargs):
        pass
    
    
    def setMaxIterations(*args, **kwargs):
        pass
    
    
    def setMaxSelfCollisionIterations(*args, **kwargs):
        pass
    
    
    def setPositions(*args, **kwargs):
        pass
    
    
    def setPressure(*args, **kwargs):
        pass
    
    
    def setPressureDamping(*args, **kwargs):
        pass
    
    
    def setPumpRate(*args, **kwargs):
        pass
    
    
    def setRestitutionAngle(*args, **kwargs):
        pass
    
    
    def setRestitutionTension(*args, **kwargs):
        pass
    
    
    def setSealHoles(*args, **kwargs):
        pass
    
    
    def setSelfCollideWidth(*args, **kwargs):
        pass
    
    
    def setSelfCollisionFlags(*args, **kwargs):
        pass
    
    
    def setSelfCollisionSoftness(*args, **kwargs):
        pass
    
    
    def setSelfCrossoverPush(*args, **kwargs):
        pass
    
    
    def setSelfTrappedCheck(*args, **kwargs):
        pass
    
    
    def setShearResistance(*args, **kwargs):
        pass
    
    
    def setStartPressure(*args, **kwargs):
        pass
    
    
    def setStretchAndCompressionResistance(*args, **kwargs):
        pass
    
    
    def setTangentialDrag(*args, **kwargs):
        pass
    
    
    def setThickness(*args, **kwargs):
        pass
    
    
    def setTopology(*args, **kwargs):
        pass
    
    
    def setTrackVolume(*args, **kwargs):
        pass
    
    
    def setVelocities(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MFnVortexField(MFnField):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def axis(*args, **kwargs):
        pass
    
    
    def setAxis(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MFnNewtonField(MFnField):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def minDistance(*args, **kwargs):
        pass
    
    
    def setMinDistance(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MFnGravityField(MFnField):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def direction(*args, **kwargs):
        pass
    
    
    def setDirection(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MnParticle(MnObject):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def createNParticle(*args, **kwargs):
        pass
    
    
    def getBounce(*args, **kwargs):
        pass
    
    
    def getFriction(*args, **kwargs):
        pass
    
    
    def getInverseMass(*args, **kwargs):
        pass
    
    
    def getNumVertices(*args, **kwargs):
        pass
    
    
    def getPositions(*args, **kwargs):
        pass
    
    
    def getThickness(*args, **kwargs):
        pass
    
    
    def getVelocities(*args, **kwargs):
        pass
    
    
    def setBounce(*args, **kwargs):
        pass
    
    
    def setCollide(*args, **kwargs):
        pass
    
    
    def setDamping(*args, **kwargs):
        pass
    
    
    def setDisableGravity(*args, **kwargs):
        pass
    
    
    def setDragAndLift(*args, **kwargs):
        pass
    
    
    def setFriction(*args, **kwargs):
        pass
    
    
    def setIncompressibility(*args, **kwargs):
        pass
    
    
    def setInverseMass(*args, **kwargs):
        pass
    
    
    def setLiquidRadiusScale(*args, **kwargs):
        pass
    
    
    def setLiquidSimulation(*args, **kwargs):
        pass
    
    
    def setMaxIterations(*args, **kwargs):
        pass
    
    
    def setMaxSelfCollisionIterations(*args, **kwargs):
        pass
    
    
    def setPositions(*args, **kwargs):
        pass
    
    
    def setRestDensity(*args, **kwargs):
        pass
    
    
    def setSelfCollide(*args, **kwargs):
        pass
    
    
    def setSelfCollideWidth(*args, **kwargs):
        pass
    
    
    def setSelfCollisionSoftness(*args, **kwargs):
        pass
    
    
    def setSurfaceTension(*args, **kwargs):
        pass
    
    
    def setThickness(*args, **kwargs):
        pass
    
    
    def setTopology(*args, **kwargs):
        pass
    
    
    def setVelocities(*args, **kwargs):
        pass
    
    
    def setViscosity(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None


class MFnTurbulenceField(MFnField):
    def __init__(self, *args):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def frequency(*args, **kwargs):
        pass
    
    
    def phase(*args, **kwargs):
        pass
    
    
    def setFrequency(*args, **kwargs):
        pass
    
    
    def setPhase(*args, **kwargs):
        pass
    
    
    def className(*args, **kwargs):
        pass
    
    
    thisown = None
    
    __swig_destroy__ = None



def MDynamicsUtil_runupIfRequired(*args, **kwargs):
    pass


def MFnParticleSystem_className(*args, **kwargs):
    pass


def MnObject_swigregister(*args, **kwargs):
    pass


def MRenderLineArray_swigregister(*args, **kwargs):
    pass


def MFnNObjectData_className(*args, **kwargs):
    pass


def MFnNIdData_className(*args, **kwargs):
    pass


def MRenderLine_className(*args, **kwargs):
    pass


def MHairSystem_swigregister(*args, **kwargs):
    pass


def MFnDragField_className(*args, **kwargs):
    pass


def MHairSystem_className(*args, **kwargs):
    pass


def MnSolver_swigregister(*args, **kwargs):
    pass


def MDynamicsUtil_addNodeTypeToRunup(*args, **kwargs):
    pass


def MFnAirField_swigregister(*args, **kwargs):
    pass


def MFnDragField_swigregister(*args, **kwargs):
    pass


def MDynamicsUtil_swigregister(*args, **kwargs):
    pass


def MFnNewtonField_className(*args, **kwargs):
    pass


def MFnUniformField_swigregister(*args, **kwargs):
    pass


def MFnTurbulenceField_swigregister(*args, **kwargs):
    pass


def MHairSystem_getFollicle(*args, **kwargs):
    pass


def MHairSystem_setRegisteringCallableScript(*args, **kwargs):
    pass


def MFnFluid_swigregister(*args, **kwargs):
    pass


def MFnVolumeAxisField_swigregister(*args, **kwargs):
    pass


def MFnVortexField_className(*args, **kwargs):
    pass


def MFnAirField_className(*args, **kwargs):
    pass


def MFnDynSweptGeometryData_className(*args, **kwargs):
    pass


def _swig_repr(self):
    pass


def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    pass


def MDynSweptTriangle_swigregister(*args, **kwargs):
    pass


def MnCloth_swigregister(*args, **kwargs):
    pass


def MFnDynSweptGeometryData_swigregister(*args, **kwargs):
    pass


def MFnTurbulenceField_className(*args, **kwargs):
    pass


def MDynSweptTriangle_className(*args, **kwargs):
    pass


def MFnRadialField_className(*args, **kwargs):
    pass


def MnParticle_swigregister(*args, **kwargs):
    pass


def MFnPfxGeometry_className(*args, **kwargs):
    pass


def MnRigid_swigregister(*args, **kwargs):
    pass


def MFnNObjectData_swigregister(*args, **kwargs):
    pass


def MFnNewtonField_swigregister(*args, **kwargs):
    pass


def MFnVortexField_swigregister(*args, **kwargs):
    pass


def _swig_setattr_nondynamic_method(set):
    pass


def MFnGravityField_swigregister(*args, **kwargs):
    pass


def MHairSystem_registeringCallableScript(*args, **kwargs):
    pass


def MHairSystem_registerCollisionSolverCollide(*args, **kwargs):
    pass


def MDynamicsUtil_hasValidDynamics2dTexture(*args, **kwargs):
    pass


def _swig_getattr(self, class_type, name):
    pass


def weakref_proxy(*args, **kwargs):
    """
    proxy(object[, callback]) -- create a proxy object that weakly
    references 'object'.  'callback', if given, is called with a
    reference to the proxy when 'object' is about to be finalized.
    """

    pass


def MFnNIdData_swigregister(*args, **kwargs):
    pass


def MFnInstancer_swigregister(*args, **kwargs):
    pass


def MDynSweptLine_swigregister(*args, **kwargs):
    pass


def MFnUniformField_className(*args, **kwargs):
    pass


def MRenderLineArray_className(*args, **kwargs):
    pass


def MDynamicsUtil_removeNodeTypeFromRunup(*args, **kwargs):
    pass


def MHairSystem_registerCollisionSolverPreFrame(*args, **kwargs):
    pass


def MDynamicsUtil_evalDynamics2dTexture(*args, **kwargs):
    pass


def MHairSystem_getCollisionObject(*args, **kwargs):
    pass


def MFnField_className(*args, **kwargs):
    pass


def MFnPfxGeometry_swigregister(*args, **kwargs):
    pass


def MFnFluid_className(*args, **kwargs):
    pass


def MFnGravityField_className(*args, **kwargs):
    pass


def MDynSweptLine_className(*args, **kwargs):
    pass


def MHairSystem_unregisterCollisionSolverCollide(*args, **kwargs):
    pass


def MRenderLine_swigregister(*args, **kwargs):
    pass


def MDynamicsUtil_inRunup(*args, **kwargs):
    pass


def MFnParticleSystem_swigregister(*args, **kwargs):
    pass


def MFnRadialField_swigregister(*args, **kwargs):
    pass


def MFnField_swigregister(*args, **kwargs):
    pass


def MFnVolumeAxisField_className(*args, **kwargs):
    pass


def MFnInstancer_className(*args, **kwargs):
    pass


def _swig_setattr(self, class_type, name, value):
    pass


def MHairSystem_unregisterCollisionSolverPreFrame(*args, **kwargs):
    pass



_newclass = 1


