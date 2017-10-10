class MGeometry(object):
    """
    Class for working with geometric structures used to draw objects.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addIndexBuffer(*args, **kwargs):
        """
        addIndexBuffer(MIndexBuffer) -> bool
        
        Buffers cannot be added to the same object twice.Adds a index buffer to this MGeometry object.
        The buffer can only be added to this object once but may be added to others.
        """
    
        pass
    
    
    def addVertexBuffer(*args, **kwargs):
        """
        addVertexBuffer(MVertexBuffer) -> bool
        
        Adds a vertex buffer to this MGeometry object.
        The buffer can only be added to this object once but may be added to others.
        """
    
        pass
    
    
    def createIndexBuffer(*args, **kwargs):
        """
        createIndexBuffer(int) -> MIndexBuffer
        
        Creates a index buffer which is bound to this MGeometry object and cannot be used with any other.
        The buffer is automatically added to the MGeometry object so there is no need to call addIndexBuffer().
        See MGeometry.dataTypeString() for a list of valid data types.
        """
    
        pass
    
    
    def createVertexBuffer(*args, **kwargs):
        """
        createVertexBuffer(MVertexBufferDescriptor) -> MVertexBuffer
        
        Creates a vertex buffer which is bound to this MGeometry object and cannot be used with any other.
        The buffer is automatically added to the MGeometry object so there is no need to call addVertexBuffer().
        """
    
        pass
    
    
    def deleteIndexBuffer(*args, **kwargs):
        """
        deleteIndexBuffer(int) -> bool
        
        Remove a index buffer from this object.
        If the buffer was bound to this object (see createIndexBuffer()) then it will become inactive and any attempt to call any of its methods will result in an exception.
        """
    
        pass
    
    
    def deleteVertexBuffer(*args, **kwargs):
        """
        deleteVertexBuffer(int) -> bool
        
        Remove a vertex buffer from this object.
        If the buffer was bound to this object (see createVertexBuffer()) then it will become inactive and any attempt to call any of its methods will result in an exception.
        """
    
        pass
    
    
    def indexBuffer(*args, **kwargs):
        """
        indexBuffer(int) -> MIndexBuffer
        
        Get the index buffer stored at the given index.
        """
    
        pass
    
    
    def indexBufferCount(*args, **kwargs):
        """
        indexBufferCount() -> int
        
        Get the number of index buffers contained in this MGeometry object.
        """
    
        pass
    
    
    def vertexBuffer(*args, **kwargs):
        """
        vertexBuffer(int) -> MVertexBuffer
        
        Get the vertex buffer stored at the given index.
        """
    
        pass
    
    
    def vertexBufferCount(*args, **kwargs):
        """
        vertexBufferCount() -> int
        
        Get the number of vertex buffers contained in this MGeometry object.
        """
    
        pass
    
    
    def dataTypeString(*args, **kwargs):
        """
        dataTypeString(int) -> string
        
        Get the string name (e.g. 'Unsigned Char') for the following data type values:
        
          kInvalidType     Invalid element type (default value)
          kFloat           IEEE single precision floating point
          kDouble          IEEE double precision floating point
          kChar            Signed char
          kUnsignedChar    Unsigned char
          kInt16           Signed 16-bit integer
          kUnsignedInt16   Unsigned 16-bit integer
          kInt32           Signed 32-bit integer
          kUnsignedInt32   Unsigned 32-bit integer
        """
    
        pass
    
    
    def drawModeString(*args, **kwargs):
        """
        drawModeString(int) -> string
        
        Get the string name (e.g. 'Wireframe, Shaded, Textured') for a combination of the following draw mode values:
        
          kWireframe      Draw in wireframe mode
          kShaded         Draw in shaded mode
          kTextured       Draw in textured mode
          kBoundingBox    Draw in bounding box mode
          kSelectionOnly  Draw only in selection mode
        
        The draw mode value kAll is a combination of the following modes: kWireframe, kShaded, kTextured, and kBoundingBox
        """
    
        pass
    
    
    def primitiveString(*args, **kwargs):
        """
        primitiveString(int) -> string
        
        Get the string name (e.g. 'Triangles') for the following primitive values:
        
          kInvalidPrimitive        Default value is not valid
          kPoints                  List of points
          kLines                   List of lines
          kLineStrip               A line strip
          kTriangles               List of triangles
          kTriangleStrip           A triangle strip
          kAdjacentTriangles       A list of triangle with adjacency
          kAdjacentTriangleStrip   A triangle strip with adjacency
          kAdjacentLines           A list of lines with adjacency
          kAdjacentLineStrip       A line strip with adjacency
          kPatch                   A patch
        """
    
        pass
    
    
    def semanticString(*args, **kwargs):
        """
        semanticString(int) -> string
        
        Get the string name (e.g. 'Color') for the following semantic values:
        
          kInvalidSemantic    Invalid data type (default value)
          kPosition           Position vector
          kNormal             Normal vector
          kTexture            Texture coordinate tuple
          kColor              Color tuple
          kTangent            Tangent vector
          kBitangent          Bi-normal vector
          kTangentWithSign    Tangent vector with winding order sign
        """
    
        pass
    
    
    __new__ = None
    
    
    kAdjacentLineStrip = 9
    
    
    kAdjacentLines = 8
    
    
    kAdjacentTriangleStrip = 7
    
    
    kAdjacentTriangles = 6
    
    
    kAll = 15
    
    
    kBitangent = 6
    
    
    kBoundingBox = 8
    
    
    kChar = 3
    
    
    kColor = 4
    
    
    kDouble = 2
    
    
    kFloat = 1
    
    
    kInt16 = 5
    
    
    kInt32 = 7
    
    
    kInvalidPrimitive = 0
    
    
    kInvalidSemantic = 0
    
    
    kInvalidType = 0
    
    
    kLineStrip = 3
    
    
    kLines = 2
    
    
    kNormal = 2
    
    
    kPatch = 10
    
    
    kPoints = 1
    
    
    kPosition = 1
    
    
    kSelectionOnly = 16
    
    
    kShaded = 2
    
    
    kTangent = 5
    
    
    kTangentWithSign = 7
    
    
    kTexture = 3
    
    
    kTextured = 4
    
    
    kTriangleStrip = 5
    
    
    kTriangles = 4
    
    
    kUnsignedChar = 4
    
    
    kUnsignedInt16 = 6
    
    
    kUnsignedInt32 = 8
    
    
    kWireframe = 1


class MSelectionInfo(object):
    """
    This class gives informations on the selection.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def selectForHilite(*args, **kwargs):
        """
        selectForHilite(mask) -> bool
        
        Given the selection mask, determines if this shape can be selected for the hilite list.
        
        * mask (MSelectionMask) - The mask to test.
        """
    
        pass
    
    
    def selectable(*args, **kwargs):
        """
        selectable(mask) -> bool
        
        Given the selection mask, determines if the shape is selectable.
        
        * mask (MSelectionMask) - The mask to test.
        """
    
        pass
    
    
    def selectableComponent(*args, **kwargs):
        """
        selectableComponent(displayed, mask) -> bool
        
        Given the selection mask, determines if the component is selectable.
        
        * displayed (bool) - Is the component displayed.
        * mask (MSelectionMask) - The mask to test.
        """
    
        pass
    
    
    alignmentMatrix = None
    
    isRay = None
    
    isSingleSelection = None
    
    localRay = None
    
    selectClosest = None
    
    selectOnHilitedOnly = None
    
    selectRect = None
    
    __new__ = None


class MTextureManager(object):
    """
    Class which manages texture.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def acquireDepthTexture(*args, **kwargs):
        """
        acquireDepthTexture(textureName, image, generateMipMaps=True, normalizationDesc=None) -> MTexture
        acquireDepthTexture(textureName, pixelData, width, height, generateMipMaps=True, normalizationDesc=None) -> MTexture
        
        Ask the renderer to acquire a hardware texture.
        
        Acquire a hardware texture from an MImage's depth buffer:
        * textureName (string) - Name of the texture to create
        * image (MImage) - Contains block of system memory data containing depth map information
        * generateMipMaps (bool) - Generate the mipmap levels
        * normalizationDesc (MDepthNormalizationDescription) - Optional information to perform normalization on the depth values. Default value is None
        
        Acquire a hardware texture from an array of depth values:
        * textureName (string) - Name of the texture to create
        * pixelData (float*) - Contains block of system memory data containing depth information
        * width (unsigned int) - Width of the texture
        * height (unsigned int) - Height of the texture
        * generateMipMaps (bool) - Generate the mipmap levels
        * normalizationDesc (MDepthNormalizationDescription) - Optional information to perform normalization on the depth values. Default value is None
        """
    
        pass
    
    
    def acquireTexture(*args, **kwargs):
        """
        acquireTexture(filePath, mipmapLevels=0, layerName="", alphaChannelIdx=-1) -> MTexture
        acquireTexture(textureName, plug, width, height, generateMipMaps=True) -> MTexture
        acquireTexture(textureName, textureDesc, pixelData, generateMipMaps=True) -> MTexture
        acquireTexture(fileNode, allowBackgroundLoad=False) -> MTexture
        
        Ask the renderer to acquire a hardware texture.
        
        Acquire a hardware texture from an image file:
        * filePath (string) - Image file name
        * mipmapLevels (int) - Mipmap generation levels
        * layerName (string) - The name of the layer to load, this is only relevant for PSD files, otherwise it will have no effect
        * alphaChannelIdx (int) - The index of the alpha channel to load, this is only relevant for PSD files, otherwise it will have no effect
        
        If a plug to a file texture node is provided then the name, width, height and
        generateMipMaps parameters will be ignored as this information will be
        based on the image on disk associated with texture node. If uv tiling is
        enabled, currently only the first tile will be returned.
        Otherwise, an attempt to bake a texture will be made using the Maya's software
        renderer convert-to-solid-texture functionality.
        * textureName (string) - Name of the texture to create
        * plug (MPlug) - Plug which is attached with a texture
        * width (int) - Width of the texture
        * height (int) - Height of the texture
        * generateMipMaps (bool) - Generate the mipmap levels
        
        Acquire a hardware texture by providing a texture description and a block of system memory data which matches the texture description:
        * textureName (string) - Name of the texture to create
        * textureDesc (MTextureDescription) - Description of the texture
        * pixelData (void*) - Block of system memory data which matches the texture description
        * generateMipMaps (bool) - Generate the mipmap levels
        Acquire the texture associated with a given texture node. Currently only file texture nodes are supported.
        If uv tiling is enabled, currently only the first tile will be returned.
        * textureNode (MObject) - Node to acquire texture from
        * allowBackgroundLoad (bool) - Allow for background texture loading. The default value is false.
        """
    
        pass
    
    
    def acquireTiledTexture(*args, **kwargs):
        """
        acquireTiledTexture(textureName, tilePaths, tilePositions, undefinedColor, width, height) -> [MTexture, failedTilePaths, uvScaleOffset]
        
        Ask the renderer to acquire a tiled hardware texture.
        
        * textureName (string) - Name to give to the texture
        * tilePaths (list of strings) - Set of path names to UV tiles
        * tilePositions (MFloatArray) - Set of lower left coordinates for each UV tile
        * undefinedColor (MColor) - Color to fill tile region with if the image for a given UV tile cannot be acquired
        * maxWidth (unsigned int) - Maximum width of the output texture. The value is clamped to a minimum of 256
        * maxHeight (unsigned int) - Maximum height of the output texture. The value is clamped to a minimum of 256
        * failedTilePaths [OUT] (list of strings) - List of files which were not written to the output texture
        * uvScaleOffset [OUT] (MFloatArray) - Transform to map to the uv range of the output texture
        """
    
        pass
    
    
    def addImagePath(*args, **kwargs):
        """
        addImagePath(string) -> self
        
        Adds an additional search path for looking up images on disk.
        """
    
        pass
    
    
    def imagePaths(*args, **kwargs):
        """
        imagePaths() -> list of strings
        
        Get the current set of image search paths.
        """
    
        pass
    
    
    def releaseTexture(*args, **kwargs):
        """
        releaseTexture(MTexture) -> self
        
        Deletes the MTexture and releases the reference to the underlying texture which is held by the MTexture object.
        """
    
        pass
    
    
    def saveTexture(*args, **kwargs):
        """
        saveTexture(MTexture, string) -> self
        
        Ask the renderer to save a hardware texture to disk.
        """
    
        pass
    
    
    __new__ = None


class MColorManagementUtilities(object):
    """
    Utilities class for color management
    """
    
    
    
    def getColorTransformCacheIdForInputSpace(*args, **kwargs):
        """
        getColorTransformCacheIdForInputSpace(inputSpaceName) -> transformId
        
        Utility function to retrieve the id of a color transform
        based on the input color space name provided.
        
        The color transform id corresponds to a color transform that
        converts colors from the input color space specified to the scene
        rendering space
        
        For example, given the name of the input color space of a node,
        this function retrieves the id of the color transform to be used
        for mapping colors from input space to rendering space.  For nodes
        that have such a color space attribute, the transform id is meant
        to be written by a file translator plug-in to a renderer file
        alongside the node information. This id corresponds to a color
        transform contained in the color transform data retrieved by
        MRenderUtilities::getColorTransformData.
        
        * inputSpaceName (string) - Name of the color space of the node.
        
        Returns identifier of the color transform required to be 
        applied to the node.
        """
    
        pass
    
    
    def getColorTransformCacheIdForOutputTransform(*args, **kwargs):
        """
        getColorTransformCacheIdForOutputTransform() -> transformId
        
        Utility function to retrieve the id of the color transform to be applied on the final output.
        
        The color transform id corresponds to a color transform that
        converts colors of the rendered image to a target color space.
        
        This id corresponds to a color transform contained in the color
        transform data retrieved by the MColorTransformData class.
        
        Returns identifier of the color transform required to be 
        applied on the rendered image
        """
    
        pass
    
    
    def getColorTransformData(*args, **kwargs):
        """
        getColorTransformData() -> (size, data)
        
        Obtain a reference to opaque data containing the color transform
        information needed to render the scene.
        
        This block of data is meant to be written by a file translator
        plug-in to a renderer file.  With the help of the SynColor SDK and
        this block of data, the external renderer can  reproduce the same
        color transformations as in Maya
        
        Returns the color transform data block info (bytearray).
        """
    
        pass
    
    
    def isColorManagementAvailable(*args, **kwargs):
        """
        isColorManagementAvailable() -> Boolean
        
        Returns whether color management is available for the current scene.
        
        True if color management is enabled.
        """
    
        pass
    
    
    def isColorManagementEnabled(*args, **kwargs):
        """
        isColorManagementEnabled() -> Boolean
        
        Returns whether color management is enabled for the current scene.
        
        True if color management is enabled.
        """
    
        pass


class MGeometryUtilities(object):
    """
    Utilities for Viewport 2.0
    """
    
    
    
    def acquireReferenceGeometry(*args, **kwargs):
        """
        acquireReferenceGeometry(shape, requirements) -> MGeometry
        
        Acquire reference geometry with required buffers.
        
        The user is responsible for releasing the geometry when it is no longer needed, by calling MGeometryUtilities::releaseReferenceGeometry().
        
        
        * shape (int) - The shape of the requested geometry.
        * requirements (MGeometryRequirements) - The list of required index and vertex buffers.
        
        Valid geometry shapes:
          kDefaultSphere   Sphere with radius 1, centered at 0,0,0.
          kDefaultPlane    Plane with width and height of 1, centered at 0,0,0. Assuming Y-Up orientation: width = x-axis, and height = y-axis.
          kDefaultCube     Cube with width, height and depth of 1, centered at 0,0,0.
        """
    
        pass
    
    
    def displayStatus(*args, **kwargs):
        """
        displayStatus(path) -> DisplayStatus
        
        Returns the display status of the given DAG path. Note that the last selected object will have status kLead
        instead of kActive and if only one object is selected the status will be kLead.
        
        * path (MDagPath) - The DAG path to get.
        """
    
        pass
    
    
    def releaseReferenceGeometry(*args, **kwargs):
        """
        releaseReferenceGeometry(geometry) -> None
        
        Release a generated reference geometry.
        
        * geometry (MGeometry) - The geometry to delete.
        """
    
        pass
    
    
    def wireframeColor(*args, **kwargs):
        """
        wireframeColor(path) -> MColor
        
        Returns the wireframe color used in Viewport 2.0 for the given DAG path.
        
        * path (MDagPath) - The DAG path to get wireframe color.
        """
    
        pass
    
    
    kActive = 0
    
    
    kActiveAffected = 10
    
    
    kActiveComponent = 7
    
    
    kActiveTemplate = 6
    
    
    kDefaultCube = 2
    
    
    kDefaultPlane = 1
    
    
    kDefaultSphere = 0
    
    
    kDormant = 2
    
    
    kHilite = 4
    
    
    kIntermediateObject = 9
    
    
    kInvisible = 3
    
    
    kLead = 8
    
    
    kLive = 1
    
    
    kNoStatus = 11
    
    
    kTemplate = 5


class MShaderCompileMacro(object):
    """
    Structure to define a shader compiler macro.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    definition = None
    
    name = None
    
    __new__ = None


class MVertexBufferDescriptor(object):
    """
    Describes properties of a vertex buffer.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    dataType = None
    
    dataTypeSize = None
    
    dimension = None
    
    name = None
    
    offset = None
    
    semantic = None
    
    semanticName = None
    
    stride = None
    
    __new__ = None


class MSubSceneContainer(object):
    """
    Container for render items generated by MPxSubSceneOverride.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __len__(*args, **kwargs):
        """
        x.__len__() <==> len(x)
        """
    
        pass
    
    
    def add(*args, **kwargs):
        """
        add(item) -> bool
        
        Add a render item to the set of render items that will be used to draw the DAG object associated with the override that owns this container. Each item in the container must have a unique name and the same render item may not be used in the container more than once. When Viewport 2.0 draws the associated DAG object, it will process all render items in this container.
        Any items that have valid geometry and a valid shader will be drawn as long as they pass all filtering tests for the active viewport.
        
        On successful add, Maya assumes ownership of the render item and the caller should not call MRenderItem.destroy() on the item. Callers are free to hold the render item for easy access. Note that any MRenderItem objects added to MSubSceneContainer become invalid after the render item is removed from the container. Attempts to use such object will result in instability. Further note that it is invalid to modify any render item owned by this container outside of MPxSubSceneOverride.update().
        Attempts to do so will result in unpredictable behavior.
        
        * item (MRenderItem) - The item to add.
        """
    
        pass
    
    
    def clear(*args, **kwargs):
        """
        clear() -> self
        
        Remove all render items from this container. After calling, any render items owned by this container will be invalid.
        """
    
        pass
    
    
    def count(*args, **kwargs):
        """
        count() -> int
        
        Get the number of render items in the container.
        """
    
        pass
    
    
    def find(*args, **kwargs):
        """
        find(name) -> MRenderItem
        
        Get a render item by name from the container. The ownership of the render item remains with the container and callers should not call MRenderItem.destroy() on it. The render items may be cached and will remain valid until removed from the container.
        
        * name (string) - The name of the render item to retrieve.
        """
    
        pass
    
    
    def getIterator(*args, **kwargs):
        """
        getIterator() -> MSubSceneContainerIterator
        
        Get an iterator for the container.
        Caller is responsible for deleting the iterator when it is no longer needed.
        """
    
        pass
    
    
    def remove(*args, **kwargs):
        """
        remove(name) -> bool
        
        Remove a render item by name from the set of render items used to draw the object associated with the override that owns this container. Note that on successful removal any render item that was removed become invalid and any attempts to use such items will result in instability.
        
        * name (string) - The name of the render item to remove.
        """
    
        pass
    
    
    __new__ = None


class MTextureAssignment(object):
    """
    Structure to hold the information required to set a texture parameter on a shader using a texture as input.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    texture = None
    
    __new__ = None


class MComponentDataIndexing(object):
    """
    Class for storing index mapping when vertices are shared.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def componentType(*args, **kwargs):
        """
        componentType() -> MComponentType
        
        Get the component type that the vertex indices represent.
        """
    
        pass
    
    
    def indices(*args, **kwargs):
        """
        indices() -> MUintArray
        
        Get the array of vertex indices for the component.
        """
    
        pass
    
    
    def setComponentType(*args, **kwargs):
        """
        setComponentType(MComponentType) -> self
        
        Set the component type that the vertex indices represent.
        """
    
        pass
    
    
    __new__ = None
    
    
    kFaceVertex = 0


class MVertexBufferDescriptorList(object):
    """
    A list of MVertexBufferDescriptor objects.
    """
    
    
    
    def __getitem__(*args, **kwargs):
        """
        x.__getitem__(y) <==> x[y]
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __len__(*args, **kwargs):
        """
        x.__len__() <==> len(x)
        """
    
        pass
    
    
    def append(*args, **kwargs):
        """
        append(MVertexBufferDescriptor) -> bool
        
        Add a descriptor to the list. Creates and stores a copy which is owned by the list.
        """
    
        pass
    
    
    def clear(*args, **kwargs):
        """
        clear() -> self
        
        Clear the list.
        """
    
        pass
    
    
    def remove(*args, **kwargs):
        """
        remove(index) -> bool
        
        Remove a descriptor from the list and delete it.
        """
    
        pass
    
    
    __new__ = None


class MUIDrawManager(object):
    """
    Main interface for drawing simple geometry in Viewport 2.0 and Maya Hardware Renderer 2.0
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def arc(*args, **kwargs):
        """
        arc(center, start, end, normal, radius, filled=False) -> self
        
        Draw an arc. The arc is within the plane determined by a normal vector.
        The arc sweeps in CCW from the vector that is the projection of the given start vector onto the arc plane,
        and ends at the vector that is the projection of the given end vector onto the arc plane.
        
        * center (MPoint) - Center of the arc.
        * start (MVector) - Start vector, its projection onto the arc plane is the start of the arc.
        * end (MVector) - End vector, its projection onto the arc plane is the end of the arc.
        * normal (MVector) - Normal vector of the arc plane.
        * radius (float) - Radius of the arc.
        * filled (bool) - If true the arc will be filled otherwise it will just be drawn as an outline.
        """
    
        pass
    
    
    def arc2d(*args, **kwargs):
        """
        arc2d(center, start, end, radius, filled=False) -> self
        
        Draw a 2D arc on the screen. The arc is always facing the camera.
        The arc sweeps in CCW from the start vector and ends at the end vector.
        
        * center (MPoint) - Center of the arc, only x-y components(in pixels) are used.
        * start (MVector) - Start vector, only x-y components are used.
        * end (MVector) - End vector, only x-y components are used.
        * radius (float) - Radius(in pixels) of the arc.
        * filled (bool) - If true the arc will be filled otherwise it will just be drawn as an outline.
        """
    
        pass
    
    
    def beginDrawInXray(*args, **kwargs):
        """
        beginDrawInXray() -> self
        
        The drawables to be drawn between calls to beginDrawInXray() and endDrawInXray() will display
        on the top of other geometries in the scene, as the depth test is disabled for these drawables.
        These methods can be used to drawing objects such as locators.
        Note only the drawables meet following conditions would be affected by these two APIs.
          1. Created by method MUIDrawManager::mesh();
          2. The first input parameter in MUIDrawManager::mesh() must be one of kTriangles, kLines and kPoints.
        Any other drawables to be drawn between calls to beginDrawInXray() and endDrawInXray() would display as normal.
        If several meshes are drawn between these two APIs, occlusion order is decided by their specification order.
        """
    
        pass
    
    
    def beginDrawable(*args, **kwargs):
        """
        beginDrawable(selectability = kAutomatic, selectionName = 0) -> self
        
        Resets all draw state, such as color and line style, to defaults and indicates the start of a sequence of drawing operations.
        All drawing operations must take place between calls to beginDrawable() and endDrawable().
        
        The behavior when calling with no (default) parameters depends on the context:
         - In MPxManipulatorNode.drawUI() context, the geometries will be marked as unselectable.
         - In any other context, like MPxDrawOverride.addUIDrawables(), the geometries will be marked as selectable and can be used for shape selection.Provide parameters (kSelectable, selectionName) with manipulators to specify they are selectable and their selection handle names.
        Provide kNonSelectable as selectability to specify locators are not selectable.
        
        
        * selectability (int) - Selectability of the handle to be drawn.
          kNonSelectable  Geometries cannot be used for selection
          kSelectable     Use geometries for selection
          kAutomatic      Use geometries for selection when not in manipulator context
        * selectionName (int) - Selection name for manipulators, usually derived from MPxManipulatorNode.glFirstHandle().
        """
    
        pass
    
    
    def box(*args, **kwargs):
        """
        box(center, up, right, scaleX=1.0, scaleY=1.0, scaleZ=1.0, filled=False) -> self
        
        Draw a box.
        
        * center (MPoint) - Center position for the box.
        * up (MVector) - The top of the box will be facing this direction.
        * right (MVector) - The side of the box will be facing this direction.
        * scaleX (float) - X size of the box.
        * scaleY (float) - Y size of the box.
        * scaleZ (float) - Z size of the box.
        * filled (bool) - If true the box will be filled otherwise it will just be drawn as an outline.
        """
    
        pass
    
    
    def circle(*args, **kwargs):
        """
        circle(center, normal, radius, filled=False) -> self
        
        Draw a circle.
        The circle is drawn within the plane determined by a normal vector.
        
        * center (MPoint) - Center of the circle.
        * normal (MVector) - Normal vector of the circle plane.
        * radius (float) - Radius of the circle.
        * filled (bool) - If true the circle will be filled otherwise it will just be drawn as an outline.
        """
    
        pass
    
    
    def circle2d(*args, **kwargs):
        """
        circle2d(center, radius, filled=False) -> self
        
        Draw a 2D circle on the screen.
        The circle is always facing the camera.
        
        * center (MPoint) - Center of the circle, only x-y components(in pixels) are used.
        * radius (float) - Radius(in pixels) of the circle.
        * filled (bool) - If true the circle will be filled otherwise it will just be drawn as an outline.
        """
    
        pass
    
    
    def cone(*args, **kwargs):
        """
        cone(base, direction, radius, height, filled=False) -> self
        
        Draw a cone.
        
        * base (MPoint) - Base position for the cone.
        * direction (MVector) - The cone's tip will point in this direction.
        * radius (float) - Radius of the cone.
        * height (float) - Height of the cone.
        * filled (bool) - If true the cone will be filled otherwise it will just be drawn as an outline.
        """
    
        pass
    
    
    def depthPriority(*args, **kwargs):
        """
        depthPriority() -> int
        
        Get the current depth priority value for primitive drawing.
        
        If the method failed to execute a value of 0 will be returned.
        """
    
        pass
    
    
    def endDrawInXray(*args, **kwargs):
        """
        endDrawInXray() -> self
        
        Pair with beginDrawInXray().
        """
    
        pass
    
    
    def endDrawable(*args, **kwargs):
        """
        endDrawable() -> self
        
        Indicates the end of a sequence of drawing operations.
        All internal drawing state, such as color and line style, are reset to defaults.
        """
    
        pass
    
    
    def icon(*args, **kwargs):
        """
        icon(position, name, scale)) -> self
        
        Draw an icon at a given 3d position.
        
        * position (MPoint) - 3d location of the icon..
        * name (MString) - The name of an icon. The list
         of available icon names can be found using the
        MUIDrawManager::getIconNames() method.
        * scale (float) - Uniform scaling factor for the icon.
        """
    
        pass
    
    
    def line(*args, **kwargs):
        """
        line(startPoint, endPoint) -> self
        
        Draw a straight line between two points.
        
        * startPoint (MPoint) - The start point of the line.
        * endPoint (MPoint) - The end point of the line.
        """
    
        pass
    
    
    def line2d(*args, **kwargs):
        """
        line2d(startPoint, endPoint) -> self
        
        Draw a straight line between two points.
        
        * startPoint (MPoint) - The start point of the line, only x-y components(in pixels) are used.
        * endPoint (MPoint) - The end point of the line, only x-y components(in pixels) are used.
        """
    
        pass
    
    
    def lineList(*args, **kwargs):
        """
        lineList(points, draw2D) -> self
        
        Draw a series of line segments in 3D or 2D.
        
        * points (MPointArray) - Array of point positions. Pairs of points are interpreted as line segments.
        If an odd number of points is specified then the last point will not be drawn, as it
        does not form a line segment.
        * draw2D (bool) Draw in 2D or 3D.
        """
    
        pass
    
    
    def lineStrip(*args, **kwargs):
        """
        lineStrip(points, draw2D) -> self
        
        Draw a series of connected line segments in 3D or 2D
        
        * points (MPointArray) - Array of point positions. Each point in the array is connected
        to form a line strip.
        * draw2D (bool) Draw in 2D or 3D.
        """
    
        pass
    
    
    def mesh(*args, **kwargs):
        """
        mesh(mode, position, normal=None, color=None, index=None, texcoord=None) -> self
        
        Draw custom geometric shapes from an array of vertices.
        
        If the optional normal or color arrays are provided they must contain a single value per element
        of the positions array (i.e. all three arrays must be the same length).
        
        The optional index array specifies the order in which the vertex positions (and their corresponding normals
        and colors) should be drawn. Vertices can be reused by having their indices appear multiple times, so the index
        array may be longer (or shorter) than the other three arrays.
        
        If the index array is not provided then the vertices will be drawn in the order in which they appear in the positions array.
        
        * mode (int) - Primitive mode
          kPoints       Point list
          kLines        Line list
          kLineStrip    Line strip
          kClosedLine   Closed line
          kTriangles    Triangle list
          kTriStrip     Triangle strip
        * position (MPointArray) - List of the vertex positions.
        * normal (MVectorArray) - List of the vertex normals.
        * color (MColorArray) - List of the vertex colors.
        * index (MUintArray) - List of the vertex indices.
        * texcoord (MPointArray) - List of the vertex texture coordinates.
        """
    
        pass
    
    
    def mesh2d(*args, **kwargs):
        """
        mesh2d(mode, position, color=None, index=None, texcoord=None) -> self
        
        Draw custom 2d geometric shapes from an array of vertices.
        
        If the optional color arrays are provided they must contain a single value per element of the positions
        array (i.e. both arrays must be the same length).
        
        The optional index array specifies the order in which the vertex positions (and their corresponding colors)
        should be drawn. Vertices can be reused by having their indices appear multiple times, so the index array may
        be longer (or shorter) than the other two arrays.
        
        If the index array is not provided then the vertices will be drawn in the order in which they appear in the positions array.
        
        * mode (int) - Primitive mode
          kPoints       Point list
          kLines        Line list
          kLineStrip    Line strip
          kClosedLine   Closed line
          kTriangles    Triangle list
          kTriStrip     Triangle strip
        * position (MPointArray) - List of the vertex positions, only x-y components of the point are used.
        * color (MColorArray) - List of the vertex colors.
        * index (MUintArray) - List of the vertex indices.
        * texcoord (MPointArray) - List of the vertex texture coordinates.
        """
    
        pass
    
    
    def point(*args, **kwargs):
        """
        point(point) -> self
        
        Draw a point.
        
        * point (MPoint) - Position of the point.
        """
    
        pass
    
    
    def point2d(*args, **kwargs):
        """
        point2d(point) -> self
        
        Draw a point.
        
        * point (MPoint) - Position of the point, only x-y components(in pixels) are used.
        """
    
        pass
    
    
    def points(*args, **kwargs):
        """
        points(points, draw2D) -> self
        
        Draw a series of points in 3D or 2D.
        
        * points (MPointArray) - Array of point positions.
        * draw2D (bool) Draw in 2D or 3D.
        """
    
        pass
    
    
    def rect(*args, **kwargs):
        """
        rect(center, up, normal, scaleX, scaleY, filled=False) -> self
        
        Draw a rectangle.
        The rectangle is within the plane determined by a normal vector, and a up vector is given to determine the X-Y direction.
        
        * center (MPoint) - Center of the rectangle.
        * up (MVector) - Up vector of the rectangle.
        * normal (MVector) - Normal vector of the rectangle plane.
        * scaleX (float) - Scale factor in X-direction.
        * scaleY (float) - Scale factor in Y-direction.
        * filled (bool) - If true the rectangle will be filled otherwise it will just be drawn as an outline.
        """
    
        pass
    
    
    def rect2d(*args, **kwargs):
        """
        rect2d(center, up, scaleX, scaleY, filled=False) -> self
        
        Draw a 2D rectangle on the screen.
        The rectangle is always facing the camera, and a up vector is given to determine the X-Y direction
        
        * center (MPoint) - Center of the rectangle, only x-y components(in pixels) are used.
        * up (MVector) - Up vector of the rectangle, only x-y components are used.
        * scaleX (float) - Scale factor in X-direction.
        * scaleY (float) - Scale factor in Y-direction.
        * filled (bool) - If true the rectangle will be filled otherwise it will just be drawn as an outline.
        """
    
        pass
    
    
    def setColor(*args, **kwargs):
        """
        setColor(color) -> self
        
        Set the draw color. This will remain in effect until the next call to setColor(), setColorIndex() or endDrawable().
        
        For text this color will be used as the foreground color. Background color can be specified directly in the call to text().
        
        
        Default: (0.7, 0.7, 0.7, 1)
        """
    
        pass
    
    
    def setColorIndex(*args, **kwargs):
        """
        setColorIndex(index) -> self
        
        Set the color index for the later primitive and text drawing.
        For default, it will use (0.7, 0.7, 0.7, 1) as default color.
        
        * index (int) - Color index
        """
    
        pass
    
    
    def setDepthPriority(*args, **kwargs):
        """
        setDepthPriority(priority) -> self
        
        Set the depth priority for primitive drawing.
        
        The MRenderItem class lists some sample internal priorities which may be used.
        
        * priority (int) - Depth priority.
        """
    
        pass
    
    
    def setFontIncline(*args, **kwargs):
        """
        setFontIncline(fontIncline) -> self
        
        Set the incline of font to be used when drawing text.
        
        * fontIncline (int) - The font incline to use.
        """
    
        pass
    
    
    def setFontLine(*args, **kwargs):
        """
        setFontLine(fontLine) -> self
        
        Set the line of font to be used when drawing text.
        
        * fontLine (int) - The font line to use.
        """
    
        pass
    
    
    def setFontName(*args, **kwargs):
        """
        setFontName(faceName) -> self
        
        Set the face name of font to be used when drawing text.
        
        * faceName (string) - The font face name(case-insensitive) to use, All system font faces are supported. "helvetica" is the default for invalid input.
        """
    
        pass
    
    
    def setFontSize(*args, **kwargs):
        """
        setFontSize(fontSize) -> self
        
        Set the size of font to be used when drawing text.
        
        * fontSize (int) - The font height(in pixel) to use.
        """
    
        pass
    
    
    def setFontStretch(*args, **kwargs):
        """
        setFontStretch(fontStretch) -> self
        
        Set the stretch of font to be used when drawing text.
        
        * fontStretch (int) - The font stretch to use.
        """
    
        pass
    
    
    def setFontWeight(*args, **kwargs):
        """
        setFontWeight(fontWeight) -> self
        
        Set the weight of font to be used when drawing text.
        
        * weight (int) - The font weight to use.
        """
    
        pass
    
    
    def setLineStyle(*args, **kwargs):
        """
        setLineStyle(style) -> self
        setLineStyle(factor, pattern) -> self
        
        Set the line style for the primitive drawing (line, rect, box...)
        
        * style (int) - Line style type.
          kSolid         Solid line
          kShortDotted   Short Dotted line
          kShortDashed   Short dashed line
          kDashed        Dashed line
          kDashed        Dotted line
        
        Or set the dashed line pattern for the primitive drawing (line, rect, box...)
        
        * factor (int) - a multiplier for each bit in the line stipple pattern.
        * pattern (int) - a bit pattern indicating which fragments of a line will be drawn
        """
    
        pass
    
    
    def setLineWidth(*args, **kwargs):
        """
        setLineWidth(value) -> self
        
        Set the line width for the primitive drawing (line, rect, box...)
        
        * value (float) - Line width in pixels.
        """
    
        pass
    
    
    def setPaintStyle(*args, **kwargs):
        """
        setPaintStyle(style) -> self
        
        Set the paint style for filled primitive drawing.
        
        * style (int) - Paint style type.
          kFlat      Solid
          kStippled  Stippled
          kShaded    Shaded with lighting
        """
    
        pass
    
    
    def setPointSize(*args, **kwargs):
        """
        setPointSize(value) -> self
        
        Set the point size for the point drawing.
        
        * value (float) - Point size in pixels.
        """
    
        pass
    
    
    def setTexture(*args, **kwargs):
        """
        setTexture(texture) -> self
        
        Set the active texture to apply when drawing a mesh.
        This will remain in effect until the next call to setTexture().
        
        * texture (MTexture) - The texture which will affect the later drawing.
        """
    
        pass
    
    
    def setTextureMask(*args, **kwargs):
        """
        setTextureMask(mask) -> self
        
        Set the channel mask to used when applying a texture to a mesh.
        This will remain in effect until the next call to setTextureMask().
        
        Fails when mask is not supported.
        
        * mask (int) - The channel mask which will affect the later drawing.
                Currently, only MBlendState.kRGBAChannels, MBlendState.kRGBChannels and MBlendState.kAlphaChannel are supported.
        """
    
        pass
    
    
    def setTextureSampler(*args, **kwargs):
        """
        setTextureSampler(filter, address) -> self
        
        Set the filter and address mode used when applying a texture to a mesh.
        This will remain in effect until the next call to setTextureSampler().
        
        Fails when filter and address combination is not supported.
        
        * filter (int) - The filter which will affect the later drawing.
                Currently, only MSamplerState.kMinMagMipPoint and MSamplerState.kMinMagMipLinear are supported.
        * address (int) - The canonical range which will affect the later drawing.
                Currently, only MSamplerState.kTexWrap and MSamplerState.kTexClamp are supported.
        """
    
        pass
    
    
    def sphere(*args, **kwargs):
        """
        sphere(center, radius, filled=False) -> self
        
        Draw a sphere.
        
        * center (MPoint) - Center of the sphere.
        * radius (float) - Radius of the sphere.
        * filled (bool) - If true the sphere will be filled otherwise it will just be drawn as a wireframe.
        """
    
        pass
    
    
    def text(*args, **kwargs):
        """
        text(position, text, alignment=kLeft, backgroundSize=None, backgroundColor=None, dynamic=False) -> self
        
        Draw a screen facing and horizontal aligned text in viewport 2.0.
        It has a fixed size in screen space.
        
        * position (MPoint) - Position of the text to be drawn, it is 3d object space.
        * text (string) - Content of the text string.
        * alignment (TextAlignment) - Alignment of the text.
                 - "kLeft", background box's left bottom will be located at "position".         In width direction, text area will be aligned to the left side of background.
                 In height direction, text are will be aligned in the middle of background.
                 - "kCenter", background box' center bottom will be located at "position".         Text area's center and background box's center will be the same point.
                 - "kRight", background box's right bottom will be located at "position".         In width direction, text area will be aligned to the right side of background.
                 In height direction, text are will be aligned in the middle of background.
        * backgroundSize ([int, int]) - The background box size of the text.
                 Default is None, in this case there will be no background, just shows the text.
                 If it is specified with smaller size than text, the text will be clipped.
                 It is a int array with size 2, like "backgroundSize = [ width, height ]"
                 Size unit is the screen pixel.
        * backgroundColor (MColor) - The color of the background, it can be transparent.
                 If None is passed, background will be fully transparent.
        * dynamic (bool) - This is mostly used for performance.
                 If the text draw is not changed frequently, we can leave it as default value false.
                                If the text draw is changing very often like it is showing some dynamic numbers,
                 in this case making dynamic true will give better performance.
        """
    
        pass
    
    
    def text2d(*args, **kwargs):
        """
        text2d(position, text, alignment=kLeft, backgroundSize=None, backgroundColor=None, dynamic=False) -> self
        
        Draw a text on the screen.
        
        * position (MPoint) - Position of the text to be drawn, it is in screen space, only x-y components are used.
        * text Content of the text string.
        * alignment (TextAlignment) - Alignment of the text.
                 - "kLeft", background box's left bottom will be located at "position".         In width direction, text area will be aligned to the left side of background.
                 In height direction, text are will be aligned in the middle of background.
                 - "kCenter", background box' center bottom will be located at "position".         Text area's center and background box's center will be the same point.
                 - "kRight", background box's right bottom will be located at "position".         In width direction, text area will be aligned to the right side of background.
                 In height direction, text are will be aligned in the middle of background.
        * backgroundSize ([int, int]) - The background box size of the text.
                 Default is None, in this case there will be no background, just shows the text.
                 If it is specified with smaller size than text, the text will be clipped.
                 It is a int array with size 2, like "backgroundSize = [ width, height ]"
                 Size unit is the screen pixel.
        * backgroundColor (MColor) - The color of the background, it can be transparent.
                 If None is passed, background will be fully transparent.
        * dynamic (bool) - This is mostly used for performance.
                 If the text draw is not changed frequently, we can leave it as default value false.
                                If the text draw is changing very often like it is showing some dynamic numbers,
                 in this case making dynamic true will give better performance.
        """
    
        pass
    
    
    def getFontList(*args, **kwargs):
        """
        getFontList() -> list of strings
        
        Get the names of all font faces that are available on current system.
        The names can then be used for MUIDrawManager::setFontName().
        """
    
        pass
    
    
    def getIconNames(*args, **kwargs):
        """
        getIconNames() -> list of strings
        
        Get list of icon names. The names can be used
        for drawing icons using the MUIDrawManager::icon() method.
        """
    
        pass
    
    
    __new__ = None
    
    
    kAutomatic = 2
    
    
    kCenter = 1
    
    
    kClosedLine = 3
    
    
    kDashed = 3
    
    
    kDefaultFontSize = 12
    
    
    kDotted = 4
    
    
    kFlat = 0
    
    
    kInclineItalic = 1
    
    
    kInclineNormal = 0
    
    
    kInclineOblique = 2
    
    
    kLeft = 0
    
    
    kLineNone = 0
    
    
    kLineOverline = 1
    
    
    kLineStrikeoutLine = 3
    
    
    kLineStrip = 2
    
    
    kLineUnderline = 2
    
    
    kLines = 1
    
    
    kNonSelectable = 0
    
    
    kPoints = 0
    
    
    kRight = 2
    
    
    kSelectable = 1
    
    
    kShaded = 2
    
    
    kShortDashed = 2
    
    
    kShortDotted = 1
    
    
    kSmallFontSize = 9
    
    
    kSolid = 0
    
    
    kStippled = 1
    
    
    kStretchCondensed = 75
    
    
    kStretchExpanded = 125
    
    
    kStretchExtraCondensed = 62
    
    
    kStretchExtraExpanded = 150
    
    
    kStretchSemiCondensed = 87
    
    
    kStretchSemiExpanded = 112
    
    
    kStretchUltraCondensed = 50
    
    
    kStretchUltraExpanded = 200
    
    
    kStretchUnstretched = 100
    
    
    kTriStrip = 5
    
    
    kTriangles = 4
    
    
    kWeightBlack = 87
    
    
    kWeightBold = 75
    
    
    kWeightDemiBold = 63
    
    
    kWeightLight = 25
    
    
    kWeightNormal = 50


class MRenderTarget(object):
    """
    An instance of a render target that may be used with Viewport 2.0.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def rawData(*args, **kwargs):
        """
        rawData() -> [long, rowPitch, slicePitch]
        
        Get a copy of the raw data mapped to the target.
        The caller must deallocate the system memory (using freeRawData()) as the target itself does not keep any references to it.
        
        * rowPitch [OUT] (int) - The row pitch of the data. It represents the number of bytes of one line of the target data.
        * slicePitch [OUT] (int) - The slice pitch of the data. It represents the number of bytes of the whole target data.
        """
    
        pass
    
    
    def resourceHandle(*args, **kwargs):
        """
        resourceHandle() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the draw API dependent handle for a render target.
        For OpenGL, a pointer to an OpenGL texture identifier is returned.
        For DirectX, a reference to a Direct3D "view" of a target is returned.
        """
    
        pass
    
    
    def targetDescription(*args, **kwargs):
        """
        targetDescription() -> MRenderTargetDescription
        
        Get target description.
        """
    
        pass
    
    
    def updateDescription(*args, **kwargs):
        """
        updateDescription(MRenderTargetDescription) -> self
        
        Change the description of a render target.
        """
    
        pass
    
    
    def freeRawData(*args, **kwargs):
        """
        freeRawData(long) -> None
        Deallocate system memory - retrieved from rawData().
        """
    
        pass
    
    
    __new__ = None


class MBlendState(object):
    """
    Container class for an acquired GPU blend state.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def desc(*args, **kwargs):
        """
        desc() -> MBlendStateDesc
        
        Get the blend state descriptor that was used to create the state object.
        """
    
        pass
    
    
    def resourceHandle(*args, **kwargs):
        """
        resourceHandle() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the draw API dependent handle for a blend state.
        For OpenGL, such a handle does not exist and a NULL pointer will be returned.
        For DirectX, a pointer to a Direct3D state will be returned.
        """
    
        pass
    
    
    __new__ = None
    
    
    kAdd = 1
    
    
    kAlphaChannel = 8
    
    
    kBlendFactor = 14
    
    
    kBlueChannel = 4
    
    
    kBothInvSourceAlpha = 13
    
    
    kBothSourceAlpha = 12
    
    
    kDestinationAlpha = 7
    
    
    kDestinationColor = 9
    
    
    kGreenChannel = 2
    
    
    kInvBlendFactor = 15
    
    
    kInvDestinationAlpha = 8
    
    
    kInvDestinationColor = 10
    
    
    kInvSourceAlpha = 6
    
    
    kInvSourceColor = 4
    
    
    kMax = 5
    
    
    kMaxTargets = 8
    
    
    kMin = 4
    
    
    kNoChannels = 0
    
    
    kOne = 2
    
    
    kRGBAChannels = 15
    
    
    kRGBChannels = 7
    
    
    kRedChannel = 1
    
    
    kReverseSubtract = 3
    
    
    kSourceAlpha = 5
    
    
    kSourceAlphaSat = 11
    
    
    kSourceColor = 3
    
    
    kSubtract = 2
    
    
    kZero = 1


class MRenderOverride(object):
    """
    Class which defines a 2d geometry quad render.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def cleanup(*args, **kwargs):
        """
        cleanup() -> self
        
        Perform any cleanup required following the execution of render operations.
        """
    
        pass
    
    
    def getFrameContext(*args, **kwargs):
        """
        getFrameContext() -> MFrameContext
        
        Return a frame context. The context is not available if called before setup() or after cleanup().
        The context should never be deleted by the plug-in as it is owned by the render override.
        """
    
        pass
    
    
    def name(*args, **kwargs):
        """
        name() -> string
        
        Returns the name of the override.
        """
    
        pass
    
    
    def nextRenderOperation(*args, **kwargs):
        """
        nextRenderOperation() -> bool
        
        Iterate to the next operation. If there are no more operations then this method should return false.
        """
    
        pass
    
    
    def renderOperation(*args, **kwargs):
        """
        renderOperation() -> MRenderOperation
        
        Return the current operation being iterated over.
        """
    
        pass
    
    
    def setup(*args, **kwargs):
        """
        setup(destination) -> self
        
        Perform any setup required before render operations are to be executed.
        """
    
        pass
    
    
    def startOperationIterator(*args, **kwargs):
        """
        startOperationIterator() -> bool
        
        Query if there are any operations to iterate over.
        """
    
        pass
    
    
    def supportedDrawAPIs(*args, **kwargs):
        """
        supportedDrawAPIs() -> int
        
        Returns the draw APIs supported by this override.
        See MRenderer.drawAPI() description for the list of draw APIs.
        """
    
        pass
    
    
    def uiName(*args, **kwargs):
        """
        uiName() -> string
        
        Returns the user interface name for the override.
        """
    
        pass
    
    
    __new__ = None


class MRenderTargetAssignment(object):
    """
    Structure to hold the information required to set a texture parameter on a shader using a render target as input.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    target = None
    
    __new__ = None


class MComponentDataIndexingList(object):
    """
    A list of MComponentDataIndexing objects.
    """
    
    
    
    def __getitem__(*args, **kwargs):
        """
        x.__getitem__(y) <==> x[y]
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __len__(*args, **kwargs):
        """
        x.__len__() <==> len(x)
        """
    
        pass
    
    
    def append(*args, **kwargs):
        """
        append(MComponentDataIndexing) -> bool
        
        Add a MComponentDataIndexing to the list. Creates and stores a copy which is owned by the list.
        """
    
        pass
    
    
    def clear(*args, **kwargs):
        """
        clear() -> self
        
        Clear the list.
        """
    
        pass
    
    
    def remove(*args, **kwargs):
        """
        remove(index) -> bool
        
        Remove a MComponentDataIndexing from the list.
        """
    
        pass
    
    
    __new__ = None


class MPxDrawOverride(object):
    """
    Base class for user defined drawing of nodes.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addUIDrawables(*args, **kwargs):
        """
        addUIDrawables(objPath, drawManager, frameContext, data) -> self
        
        Provides access to the MUIDrawManager, which can be used to queue up operations to draw simple UI shapes like lines, circles, text, etc.
        
        This method will only be called when hasUIDrawables() is overridden to return True.
        It is called after prepareForDraw() and carries the same restrictions on the sorts of operations it can perform.
        
        * objPath (MDagPath) - The path to the object being drawn.
        * drawManager (MUIDrawManager) - The UI draw manager, it can be used to draw some simple geometry including text.
        * frameContext (MFrameContext) - Frame level context information.
        * data (MUserData) - Data cached by prepareForDraw().
        """
    
        pass
    
    
    def boundingBox(*args, **kwargs):
        """
        boundingBox(objPath, cameraPath) -> MBoundingBox
        
        Called by Maya whenever the bounding box of the drawable object is needed.
        This method should return the object space bounding box for the object to be drawn.
        
        Note that this method will not be called if the isBounded() method returns a value of False.
        
        * objPath (MDagPath) - The path to the object being drawn
        * cameraPath (MDagPath) - The path to the camera that is being used to draw
        
        Returns The object space bounding box of object drawn in the draw callback
        """
    
        pass
    
    
    def disableInternalBoundingBoxDraw(*args, **kwargs):
        """
        disableInternalBoundingBoxDraw() -> bool
        
        Returns True to disable bounding box drawing. The default value is False.
        
        Indicates whether to disable the automatic drawing of bounding boxes when the display mode has been set to bounding box display.
        
        
        Note that bounding box drawing is also disabled if the isBounded() method has been set to False.
        As noted the boundingBox() method is never called under this condition.
        As such with no bounding box information provided it is not possible to automatically draw due to insufficient information provided.
        """
    
        pass
    
    
    def excludedFromPostEffects(*args, **kwargs):
        """
        excludedFromPostEffects() -> bool
        
        Returns False to indicate inclusion in post effects. The default value is true.
        
        Indicates whether or not the draw code should be called for any additional passes required to perform post effects.
        
        
        Note that the appropriate pass identifier and pass semantic can be queried at draw time via the MPassContext data structure.
        Also note that if the pass requires a shader override that it can be obtained from the MDrawContext data structure provided at draw time.
        """
    
        pass
    
    
    def handleTraceMessage(*args, **kwargs):
        """
        handleTraceMessage(message) -> self
        
        When debug tracing is enabled via MPxDrawOverride::traceCallSequence(),
        this method will be called for each trace message.
        
        The default implementation will print the message
        to stderr.
        
        * message - A string which will provide feedback on either an
        internal or plug-in call location. To help distinguish which
        draw override a message is associated with, the full path
        name for the DAG object (associated with the draw override) may
        be included as part of the string.
        """
    
        pass
    
    
    def hasUIDrawables(*args, **kwargs):
        """
        hasUIDrawables() -> bool
        
        Query whether 'addUIDrawables()' will be called or not.
        
        In order for any override for the addUIDrawables() method to be called this method must also be overridden to return True.
        
        This method should not be overridden if addUIDrawables() has not also been overridden as there may be associated wasted overhead.
        """
    
        pass
    
    
    def isBounded(*args, **kwargs):
        """
        isBounded(objPath, cameraPath) -> bool
        
        Returns True if object is bounded.
        
        Called by Maya to determine if the drawable object is bounded or not. If the object is not bounded then it will never
        be culled by the current camera frustum used for drawing.
        
        The default implementation will always return True.
        This method can be overridden in derived classes to customize the behaviour.
        
        Note that if this method returns False then the boundingBox() method will not be called as no bounds are required in this case.
        
        * objPath (MDagPath) - The path to the object whose transform is needed.
        * cameraPath (MDagPath) - The path to the camera that is being used to draw.
        """
    
        pass
    
    
    def isTransparent(*args, **kwargs):
        """
        isTransparent() -> bool
        
        Returns True to indicate inclusion in transparency passes. The default value is false.
        
        Indicates whether or not the draw method should be called for each transparency pass(front-culling and back-culling).
        """
    
        pass
    
    
    def prepareForDraw(*args, **kwargs):
        """
        prepareForDraw(objPath, cameraPath, frameContext, oldData) -> MUserData
        
        Called by Maya each time the object needs to be drawn. Any data needed from the Maya dependency graph must be retrieved and cached in this stage. It is invalid to pull data from the Maya dependency graph in the draw callback method and Maya may become unstable if that is attempted.
        
        Implementors may allow Maya to handle the data caching by returning a pointer to the data from this method. The pointer must be to a class derived from MUserData. This same pointer will be passed to the draw callback. On subsequent draws, the pointer will also be passed back into this method so that the data may be modified and reused instead of reallocated. If a different pointer is returned Maya will delete the old data. If the cache should not be maintained between draws, set the delete after use flag on the user data. In all cases, the lifetime and ownership of the user data is handled by Maya and the user should not try to delete the data themselves. Data caching occurs per-instance of the associated DAG object. The lifetime of the user data can be longer than the associated node, instance or draw override. Due to internal caching, the user data can be deleted after an arbitrary long time. One should therefore be careful to not access stale objects from the user data destructor. If it is not desirable to allow Maya to handle data caching, simply return NULL in this method and ignore the user data parameter in the draw callback method.
        
        * objPath (MDagPath) - The path to the object being drawn
        * cameraPath (MDagPath) - The path to the camera that is being used to draw
        * frameContext (MFrameContext) - Frame level context information
        * oldData (MUserData) - Data cached by the previous draw of the instance
        
        Returns the data to be passed to the draw callback method
        """
    
        pass
    
    
    def refineSelectionPath(*args, **kwargs):
        """
        refineSelectionPath(selectInfo, hitItem, path, components, objectMask) -> bool
        
        This method is called during the hit test phase of the viewport 2.0 selection and is used to override the selected path, the selected components or simply reject the selection.
        Should return True if the selection candidate is acceptable.
        
        One can decide to change the selected path (ie: select the bottom-most transform instead of the proposed path).
        One can decide to remove or add component to the proposed selected list.
        One can decide to change the selection mask of the object (ie: override the selection mask returned by a component converter).
        One can decide that the proposed selection (path or component) is not acceptable and discard it (ie: return False).
        
        The default implementation makes no changes to 'path', 'components' or 'objectMask' and returns True (i.e. the selection is accepted).
        
        * selectInfo (MSelectionInfo) - The selection info
        * hitItem (MRenderItem) - The render item hit
        * path [IN/OUT] (MDagPath) - The selected path
        * components [IN/OUT] (MObject) - The selected components
        * objectMask [IN/OUT] (MSelectionMask) - The object selection mask
        """
    
        pass
    
    
    def supportedDrawAPIs(*args, **kwargs):
        """
        supportedDrawAPIs() -> DrawAPI
        
        Returns the draw API supported by this override.
        """
    
        pass
    
    
    def traceCallSequence(*args, **kwargs):
        """
        traceCallSequence() -> bool
        
        This method allows a way for a plug-in to examine
        the basic call sequence for a draw override.
        
        The default implementation returns false meaning no
        tracing will occur.
        """
    
        pass
    
    
    def transform(*args, **kwargs):
        """
        transform(objPath, cameraPath) -> MMatrix
        
        Returns The world space transformation matrix.
        
        Called by Maya whenever the world space transform is needed for the object to be drawn by the draw callback.
        The default implementation simply returns the transformation defined by the parent transform nodes in Maya.
        Override to get custom behaviour.
        
        * objPath (MDagPath) - The path to the object whose transform is needed.
        * cameraPath (MDagPath) - The path to the camera that is being used to draw.
        """
    
        pass
    
    
    def updateSelectionGranularity(*args, **kwargs):
        """
        updateSelectionGranularity(path, selectionContext) -> self
        
        This is method is called during the pre-filtering phase of the viewport 2.0 selection and is used to setup the selection context of the given DAG object.
        
        This is useful to specify the selection level, which defines what can be selected on the object :
          MSelectionContext.kNone        Nothing can be selected
          MSelectionContext.kObject      Object can be selected as a whole
          MSelectionContext.kComponent   Parts of the object - such as vertex, edge or face - are selectable
        This is used to discard objects that are not selectable given the current selection mode (see MGlobal.selectionMode()).
        
        The default implementation leaves the selection level set at its default value, which is kObject.
        
         path (MDagPath) - The path to the instance to update the selection context for
         selectionContext [OUT] (MSelectionContext) - The selection context
        """
    
        pass
    
    
    __new__ = None


class MSamplerStateDesc(object):
    """
    Descriptor for a complete sampler state.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def setDefaults(*args, **kwargs):
        """
        setDefaults() -> self
        
        Set all values for the target blend state to their default values.
        """
    
        pass
    
    
    addressU = None
    
    addressV = None
    
    addressW = None
    
    borderColor = None
    
    comparisonFn = None
    
    coordCount = None
    
    elementIndex = None
    
    filter = None
    
    maxAnisotropy = None
    
    maxLOD = None
    
    minLOD = None
    
    mipLODBias = None
    
    __new__ = None


class MVertexBuffer(object):
    """
    Vertex buffer for use with MGeometry.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def acquire(*args, **kwargs):
        """
        acquire(size, writeOnly) -> long
        
        Get a pointer to memory for the buffer.
        
        * size (int) - The size of the buffer to acquire.
        * writeOnly (bool) - Specified if the returned memory should be uninitialized or filled with actual buffer content.
                             When the current buffer content is not needed, it is preferable to set the writeOnly flag to true for better performance.
        """
    
        pass
    
    
    def commit(*args, **kwargs):
        """
        commit(long) -> self
        
        Commit the data stored in the memory given by acquire() to the buffer.
        If this method is not called, the acquired buffer will not be used in drawing.
        The pointer must be the same pointer returned from acquire().
        """
    
        pass
    
    
    def descriptor(*args, **kwargs):
        """
        descriptor() -> MVertexBufferDescriptor
        
        Get the the buffer descriptor.
        """
    
        pass
    
    
    def hasCustomResourceHandle(*args, **kwargs):
        """
        hasCustomResourceHandle() -> bool
        
        Returns true if this vertex buffer is using a custom resource handle set
        by the plugin using MVertexBuffer.setResourceHandle(long, int).
        """
    
        pass
    
    
    def lockResourceHandle(*args, **kwargs):
        """
        lockResourceHandle() -> self
        
        Lock the resource handle. The pointer returned from resourceHandle() is
        guaranteed to exist between lockResourceHandle() and unlockResourceHandle().
        
        MVertexBuffer may store data in system memory, GPU memory or both. Direct
        access to the GPU representation of the data is possible through the
        buffer's resourceHandle(). If the GPU representation of the data is to be
        directly modified using an external graphics or compute API, then
        lockResourceHandle() must be called on the MVertexBuffer once, before any
        modifications to the buffer are made.
        
        While a resource handle is locked, any external modifications to the GPU
        buffer will be recognized by Maya.
        
        While a resource handle is locked, consolidated world will take longer to
        consolidate the corresponding object. After unlocking a resource handle,
        consolidated world will take longer to consolidate the corresponding object
        one more time, the first time the unlocked resource handle is consolidated.
        
        Calling lockResourceHandle() and unlockResourceHandle() on a custom resource
        handle has no effect.
        
        Reallocating or deleting the GPU representation of the data between
        lockResourceHandle() and unlockResourceHandle() will result in undefined
        behavior. acquire(), commit() and update() may reallocate the GPU representation.
        unload() may delete the GPU representation.
        
        map() and unmap() will work if they are called between lockResourceHandle()
        and unlockResourceHandle(). They operate on the GPU representation.
        """
    
        pass
    
    
    def map(*args, **kwargs):
        """
        map() -> long
        
        Get a read-only pointer to the existing content of the buffer.
        Writing new content in this memory block is not supported and can lead to unexpected behavior.
        """
    
        pass
    
    
    def resourceHandle(*args, **kwargs):
        """
        resourceHandle() -> long
        
        Returns a long containing a C++ 'float' pointer which points to the graphics device dependent handle to the vertex buffer.
        """
    
        pass
    
    
    def setResourceHandle(*args, **kwargs):
        """
        setResourceHandle(long, int) -> self
        
        Set the graphics-device-dependent hardware buffer resource handle.
        """
    
        pass
    
    
    def unload(*args, **kwargs):
        """
        unload() -> self
        
        If the buffer is resident in GPU memory, calling this method will move it to system memory and free the GPU memory.
        """
    
        pass
    
    
    def unlockResourceHandle(*args, **kwargs):
        """
        unlockResourceHandle() -> self
        
        Unlock the resource handle. The pointer returned from resourceHandle is not
        guaranteed to exist any more.
        See lockResourceHandle() for more details.
        """
    
        pass
    
    
    def unmap(*args, **kwargs):
        """
        unmap() -> self
        
        Release the data exposed by map(). If this method is not called, the buffer will not be recycled.
        """
    
        pass
    
    
    def update(*args, **kwargs):
        """
        update(buffer, destOffset, numVerts, truncateIfSmaller) -> self
        
        Set a portion (or all) of the contents of the MVertexBuffer using the data in the provided software buffer.
        The internal hardware buffer will be allocated or reallocated to fit if required, according to the vertex size from the descriptor.
        
        * buffer (long) - The input data buffer, starting with the first vertex to copy.
        * destOffset (int) - The offset (in vertices) from the beginning of the buffer to start writing to.
        * numVerts (int) - The number of vertices to copy.
        * truncateIfSmaller (bool) - If true and offset+numVerts is less than the pre-existing size of the buffer,
                                     then the buffer contents will be truncated to the new size. Truncating the buffer size
                                     will not cause a reallocation and will not lose data before the destOffset.
        """
    
        pass
    
    
    def vertexCount(*args, **kwargs):
        """
        vertexCount() -> int
        
        Get the size of the vertex buffer.
        """
    
        pass
    
    
    __new__ = None


class MRasterizerState(object):
    """
    Container class for an acquired complete GPU rasterizer state.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def desc(*args, **kwargs):
        """
        desc() -> MRasterizerStateDesc
        
        Get the rasterizer state descriptor that was used to create the state object.
        """
    
        pass
    
    
    def resourceHandle(*args, **kwargs):
        """
        resourceHandle() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the draw API dependent handle for a rasterizer state.
        For OpenGL, such a handle does not exist and a NULL pointer will be returned.
        For DirectX, a pointer to a Direct3D state will be returned.
        """
    
        pass
    
    
    __new__ = None
    
    
    kCullBack = 3
    
    
    kCullFront = 2
    
    
    kCullNone = 1
    
    
    kFillSolid = 3
    
    
    kFillWireFrame = 2


class MShaderInstance(object):
    """
    An instance of a shader that may be used with Viewport 2.0.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def activatePass(*args, **kwargs):
        """
        activatePass(MDrawContext, int) -> self
        Activates the given pass of the shader.
        Must be called between calls to bind() and unbind().
        """
    
        pass
    
    
    def addInputFragment(*args, **kwargs):
        """
        addInputFragment(fragmentName, outputName, inputName) -> self
        
        Connect a fragment that has been registered with the fragment manager to an input on the existing MShaderInstance.
        Use this method to add shader instructions to an existing MShaderInstance.
        The code defined in the fragment will be compiled and executed on the GPU to compute the value for the input parameter.
        
        * fragmentName (string) - The name of a fragment that has been registered with the MFragmentManager.
        * outputName (string) - The name of the output on the registered fragment to connect to.
        * inputName (string) - The name of the input parameter on the MShaderInstance to connect to.
        """
    
        pass
    
    
    def addOutputFragment(*args, **kwargs):
        """
        addOutputFragment(fragmentName, inputName) -> self
        
        Connect a fragment that has been registered with the fragment manager to an output on the existing MShaderInstance.
        The code defined in the fragment will be compiled and executed on the GPU to modify the value returned by the original shader.
        For example, use this method to add additional alpha or conditionals to the output color.
        
        * fragmentName (string) - The name of a fragment that has been registered with the MFragmentManager.
        * inputName (string) - The name of the input parameter on the fragment to connect the shaders output to.
        """
    
        pass
    
    
    def annotation(*args, **kwargs):
        """
        annotation(parameterName, annotationName) -> int / float / string
        
        Returns the value of a named parameter annotation.
        
         * parameterName (string) - The name of the parameter.
         * annotationName (string) - The name of the annotation.
        """
    
        pass
    
    
    def bind(*args, **kwargs):
        """
        bind(MDrawContext) -> self
        Binds the shader instance to the draw context, so that it is the active shader.
        """
    
        pass
    
    
    def clone(*args, **kwargs):
        """
        clone() -> MShaderInstance
        
        Clone the shader. This will return a new MShaderInstance object which is identical to the existing shader.
        """
    
        pass
    
    
    def createShaderInstanceWithColorManagementFragment(*args, **kwargs):
        """
        createShaderInstanceWithColorManagementFragment(inputColorSpace) -> MShaderInstance
        
        Return a new shader instance with Color Management fragment added, which is based on the callee.
        The callee shader instance is the one used for rendering a render item with image(a MPxNode with image, etc.)
        The new shader is completely independent of the original shader. 
        Setting parameter values on either shader after calling this function will have no effect on the other.
        The function won't keep a copy of input parameter.
        
        
        When the returned new shader instance is no longer needed, MShaderManager.releaseShader() 
        should be called to notify the shader manager that the caller is done with the shader.
        
         * inputColorSpace (string) - The color space the current image is in
        """
    
        pass
    
    
    def getPassCount(*args, **kwargs):
        """
        getPassCount(MDrawContext) -> int
        Returns the number of draw passes defined by the shader.
        None if the shader instance or draw context was invalid.
        """
    
        pass
    
    
    def isArrayParameter(*args, **kwargs):
        """
        isArrayParameter(string) -> bool
        
        Determine whether the named parameter is an array.
        """
    
        pass
    
    
    def isTransparent(*args, **kwargs):
        """
        isTransparent() -> bool
        
        Return whether the shader will render with transparency.
        """
    
        pass
    
    
    def parameterDefaultValue(*args, **kwargs):
        """
        parameterDefaultValue(parameterName) -> bool / int / float / tuple of float
        
        Returns the default value of named parameter, None if no default value.
        """
    
        pass
    
    
    def parameterList(*args, **kwargs):
        """
        parameterList() -> list of string
        
        Get the names of all parameters that are settable on this shader instance.
        """
    
        pass
    
    
    def parameterSemantic(*args, **kwargs):
        """
        parameterSemantic(parameterName) -> string
        
        Returns the semantic associated to a named parameter.
        """
    
        pass
    
    
    def parameterType(*args, **kwargs):
        """
        parameterType(string) -> int
        
        Get the type of the named parameter, returns kInvalid if parameter is not found.
        """
    
        pass
    
    
    def passAnnotation(*args, **kwargs):
        """
        passAnnotation(pass, annotationName) -> int / float / string
        
        Returns the value of the current technique's pass annotation.
        
         * pass (int) - The index of the pass.
         * annotationName (string) - The name of the pass annotation.
        """
    
        pass
    
    
    def postDrawCallback(*args, **kwargs):
        """
        postDrawCallback() -> function/None
        
        Returns the post-draw callback function set for the this shader instance.
        Returns None if the callback function is not set or is not a python function.
        """
    
        pass
    
    
    def preDrawCallback(*args, **kwargs):
        """
        preDrawCallback() -> function/None
        
        Returns the pre-draw callback function set for the this shader instance.
        Returns None if the callback function is not set or is not a python function.
        """
    
        pass
    
    
    def requiredVertexBuffers(*args, **kwargs):
        """
        requiredVertexBuffers(MVertexBufferDescriptorList) -> self
        Get the vertex buffer descriptors that describe the buffers required
        by a given shader instance.
        """
    
        pass
    
    
    def resourceName(*args, **kwargs):
        """
        resourceName(parameterName) -> string
        
        Returns the resource name of a named texture parameter.
        The resource name of a texture parameter can be specified in the effect file using the 'ResourceName' annotation.
        It allows users to define a default texture using an external file.
        If no resource was defined for a texture, this function returns an empty string.
        """
    
        pass
    
    
    def semantic(*args, **kwargs):
        """
        semantic(string) -> string
        
        Return the semantic for a named parameter.
        """
    
        pass
    
    
    def setArrayParameter(*args, **kwargs):
        """
        setArrayParameter(parameterName, sequence of bool, int) -> self
        setArrayParameter(parameterName, sequence of int, int) -> self
        setArrayParameter(parameterName, sequence of float, int) -> self
        setArrayParameter(parameterName, sequence of MMatrix, int) -> self
        
        Set the value of a named array parameter.
        """
    
        pass
    
    
    def setIsTransparent(*args, **kwargs):
        """
        setIsTransparent(bool) -> self
        
        Set whether the shader will render with transparency.
        """
    
        pass
    
    
    def setParameter(*args, **kwargs):
        """
        setParameter(parameterName, bool) -> self
        setParameter(parameterName, int) -> self
        setParameter(parameterName, float) -> self
        setParameter(parameterName, list of float) -> self
        setParameter(parameterName, MFloatVector) -> self
        setParameter(parameterName, MMatrix) -> self
        setParameter(parameterName, MFloatMatrix) -> self
        setParameter(parameterName, MTexture) -> self
        setParameter(parameterName, MRenderTarget) -> self
        setParameter(parameterName, MSamplerState) -> self
        
        Set the value of the named parameter.
        """
    
        pass
    
    
    def techniqueAnnotation(*args, **kwargs):
        """
        techniqueAnnotation(annotationName) -> int / float / string
        
        Returns the value of the current technique annotation.
        
         * annotationName (string) - The name of the technique annotation.
        """
    
        pass
    
    
    def techniqueNames(*args, **kwargs):
        """
        techniqueNames() -> list of strings
        
        Returns a list of the technique names for the effect.
        """
    
        pass
    
    
    def uiName(*args, **kwargs):
        """
        uiName(parameterName) -> string
        
        Returns the UI name associated with a named parameter.
        The UI name can be specified in shader using the 'UIName' annotation.
        The UI name can be used to specify the name that will be displayed in the Attribute Editor.
        """
    
        pass
    
    
    def uiWidget(*args, **kwargs):
        """
        uiWidget(parameterName) -> string
        
        Returns the UI widget type associated with a named parameter.
        The UI widget type can be specified in shader using the 'UIWidget' annotation.The UI widget can be used to specify which widget should be used to control the parameter in the Attribute Editor.
        """
    
        pass
    
    
    def unbind(*args, **kwargs):
        """
        unbind(MDrawContext) -> self
        Unbinds the shader instance from the draw context.
        """
    
        pass
    
    
    def updateParameters(*args, **kwargs):
        """
        updateParameters(MDrawContext) -> self
        Updates the bound shader instance with the current parameter data.
        """
    
        pass
    
    
    __new__ = None
    
    
    kBoolean = 1
    
    
    kFloat = 3
    
    
    kFloat2 = 4
    
    
    kFloat3 = 5
    
    
    kFloat4 = 6
    
    
    kFloat4x4Col = 8
    
    
    kFloat4x4Row = 7
    
    
    kInteger = 2
    
    
    kInvalid = 0
    
    
    kSampler = 13
    
    
    kTexture1 = 9
    
    
    kTexture2 = 10
    
    
    kTexture3 = 11
    
    
    kTextureCube = 12


class MRenderer(object):
    """
    Main interface class to the Viewport 2.0 renderer
    """
    
    
    
    def GPUDeviceHandle(*args, **kwargs):
        """
        GPUDeviceHandle() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the GPU "device".In the case that the drawing API is OpenGL then the "device" is a handle to an OpenGL context.
        In the case that the drawing API is DirectX then the "device" is a pointer to a DirectX device.
        """
    
        pass
    
    
    def GPUmaximumPrimitiveCount(*args, **kwargs):
        """
        GPUmaximumPrimitiveCount() -> int
        
        Returns the maximum number of primitives that can be drawn per draw call by the GPU device.
        0 if device has not been initialized.
        """
    
        pass
    
    
    def GPUmaximumVertexBufferSize(*args, **kwargs):
        """
        GPUmaximumVertexBufferSize() -> int
        
        Returns the maximum number of vertices allowed in a vertex buffer by the GPU device.
        0 if device has not been initialized.
        """
    
        pass
    
    
    def activeRenderOverride(*args, **kwargs):
        """
        activeRenderOverride() -> string
        
        Returns the name of the active override.
        """
    
        pass
    
    
    def copyTargetToScreen(*args, **kwargs):
        """
        copyTargetToScreen(MRenderTarget) -> bool
        
        Copy a render target to the screen.
        If the target's dimensions are not the same as the active viewport it will be scaled up or down as necessary to fill the entire viewport.
        """
    
        pass
    
    
    def deregisterOverride(*args, **kwargs):
        """
        deregisterOverride(MRenderOverride) -> None
        
        Deregister an existing render override on the renderer.
        The renderer will remove this override from it's list of registered overrides.
        """
    
        pass
    
    
    def disableChangeManagementUntilNextRefresh(*args, **kwargs):
        """
        disableChangeManagementUntilNextRefresh() -> None
        
        Calling this method will cause Viewport 2.0 to stop processing all changes to the Maya scene until the next viewport refresh.
        """
    
        pass
    
    
    def drawAPI(*args, **kwargs):
        """
        drawAPI() -> int
        
        Returns the current drawing API. Returns 'kNone' if the renderer is not initialized.
        
          MRenderer.kNone          Uninitialized device
          MRenderer.kOpenGL        OpenGL
          MRenderer.kDirectX11     Direct X 11
          MRenderer.kAllDevices    All : OpenGL and Direct X 11
        """
    
        pass
    
    
    def drawAPIIsOpenGL(*args, **kwargs):
        """
        drawAPIIsOpenGL() -> bool
        
        Returns whether the current drawing API is OpenGL or not
        """
    
        pass
    
    
    def drawAPIVersion(*args, **kwargs):
        """
        drawAPIVersion() -> int
        
        Returns the version of drawing API.
        """
    
        pass
    
    
    def findRenderOverride(*args, **kwargs):
        """
        findRenderOverride(string) -> MRenderOverride
        
        Returns a reference to an existing render override registered with the renderer.
        """
    
        pass
    
    
    def getFragmentManager(*args, **kwargs):
        """
        getFragmentManager() -> MFragmentManager
        
        Returns the fragment manager or None if the renderer is not initialized properly.
        """
    
        pass
    
    
    def getRenderTargetManager(*args, **kwargs):
        """
        getRenderTargetManager() -> MRenderTargetManager
        
        Returns the render target manager or None if the renderer is not initialized properly.
        """
    
        pass
    
    
    def getShaderManager(*args, **kwargs):
        """
        getShaderManager() -> MShaderManager
        
        Returns the shader manager or None if the renderer is not initialized properly.
        """
    
        pass
    
    
    def getTextureManager(*args, **kwargs):
        """
        getTextureManager() -> MTextureManager
        
        Returns the texture manager or None if the renderer is not initialized properly.
        """
    
        pass
    
    
    def needEvaluateAllLights(*args, **kwargs):
        """
        needEvaluateAllLights() -> None
        
        Notify the Viewport 2.0 renderer that it should evaluate all lights marked dirty, regardless of the light limit.For example, if there are 8 lights accessible because of the Viewport 2.0 light limit option, Only the first 8 non-ambient lights created will be evaluated.Call this method to instruct Viewport 2.0 to evaluate all dirty lights regardless of the light limit option.
        
        Note that this method does NOT perform any DG evaluation when it is called.The actual evaluation does not occur until the next viewport refresh. This method is threadsafe. The viewport refresh will occur asynchronously.Multiple calls to this method will get merged.
        
        Call this method may decrease performance in Viewport 2.0 during the next viewport refresh.Once this method is called, all unused lights that are marked dirty will be evaluated in the next viewport refresh.
        
        An example application of this method is to obtain light information while ignoring the light limit.If this method is not called, information on unused lights cannot be obtained via MDrawContext, even if LightFilter is set to kFilteredToLightLimit.This is because unused lights are not evaluated automatically by Viewport 2.0 by default.
        """
    
        pass
    
    
    def outputTargetSize(*args, **kwargs):
        """
        outputTargetSize() -> [int, int]
        
        Get target size in format [width, height].
        """
    
        pass
    
    
    def registerOverride(*args, **kwargs):
        """
        registerOverride(MRenderOverride) -> None
        
        Register the override as being usable by the renderer.
        If the override is already registered it will not be registered again.
        """
    
        pass
    
    
    def renderOverrideCount(*args, **kwargs):
        """
        renderOverrideCount() -> int
        
        Returns the number of registered render overrides.
        """
    
        pass
    
    
    def renderOverrideName(*args, **kwargs):
        """
        renderOverrideName() -> string
        
        Get the current render override name used for batch rendering.
        If there is no override then an empty string will be returned.
        """
    
        pass
    
    
    def setGeometryDrawDirty(*args, **kwargs):
        """
        setGeometryDrawDirty(object, topologyChanged=True) -> None
        
        Notify the Viewport 2.0 renderer that the geometry (size, shape, etc.) of object has changed, causing the object to be updated in the viewport.
        
        * object (MObject) - DAG object which has been modified.
        * topologyChanged (bool) - has the object topology changed
        """
    
        pass
    
    
    def setLightRequiresShadows(*args, **kwargs):
        """
        setLightRequiresShadows(object, flag) -> bool
        
        This method allows for plug-in writers to indicate that the shadow map contents for a given light are required, regardless of the light limit.
        Returns True if the method added or removed the request successfully.
        
        * object (MObject) - Light to request shadow update for
        * flag (bool) - Indicate if an update is requested. When set to true a request is added, and when set false any existing request is removed.
        """
    
        pass
    
    
    def setLightsAndShadowsDirty(*args, **kwargs):
        """
        setLightsAndShadowsDirty() -> None
        
        Notify the Viewport 2.0 renderer that something has changed which requires re-evaluation of lighting and shadows.
        """
    
        pass
    
    
    def setRenderOverrideName(*args, **kwargs):
        """
        setRenderOverrideName(string) -> bool
        
        Set the name of a render override (MRenderOverride) for batch rendering.
        """
    
        pass
    
    
    kA8 = 23
    
    
    kA8B8G8R8 = 58
    
    
    kAllDevices = 7
    
    
    kB5G5R5A1 = 39
    
    
    kB5G6R5 = 40
    
    
    kB8G8R8A8 = 55
    
    
    kB8G8R8X8 = 56
    
    
    kBC6H_SF16 = 18
    
    
    kBC6H_UF16 = 17
    
    
    kBC7_UNORM = 19
    
    
    kBC7_UNORM_SRGB = 20
    
    
    kD24S8 = 0
    
    
    kD24X8 = 1
    
    
    kD32_FLOAT = 2
    
    
    kDXT1_UNORM = 5
    
    
    kDXT1_UNORM_SRGB = 6
    
    
    kDXT2_UNORM = 7
    
    
    kDXT2_UNORM_PREALPHA = 9
    
    
    kDXT2_UNORM_SRGB = 8
    
    
    kDXT3_UNORM = 10
    
    
    kDXT3_UNORM_PREALPHA = 12
    
    
    kDXT3_UNORM_SRGB = 11
    
    
    kDXT4_SNORM = 14
    
    
    kDXT4_UNORM = 13
    
    
    kDXT5_SNORM = 16
    
    
    kDXT5_UNORM = 15
    
    
    kDirectX11 = 2
    
    
    kL16 = 34
    
    
    kL8 = 28
    
    
    kNone = 0
    
    
    kNumberOfRasterFormats = 73
    
    
    kOpenGL = 1
    
    
    kOpenGLCoreProfile = 4
    
    
    kR10G10B10A2_UINT = 54
    
    
    kR10G10B10A2_UNORM = 53
    
    
    kR16G16B16A16_FLOAT = 62
    
    
    kR16G16B16A16_SINT = 66
    
    
    kR16G16B16A16_SNORM = 64
    
    
    kR16G16B16A16_UINT = 65
    
    
    kR16G16B16A16_UNORM = 63
    
    
    kR16G16_FLOAT = 44
    
    
    kR16G16_SINT = 48
    
    
    kR16G16_SNORM = 46
    
    
    kR16G16_UINT = 47
    
    
    kR16G16_UNORM = 45
    
    
    kR16_FLOAT = 29
    
    
    kR16_SINT = 33
    
    
    kR16_SNORM = 31
    
    
    kR16_UINT = 32
    
    
    kR16_UNORM = 30
    
    
    kR1_UNORM = 22
    
    
    kR24G8 = 3
    
    
    kR24X8 = 4
    
    
    kR32G32B32A32_FLOAT = 70
    
    
    kR32G32B32A32_SINT = 72
    
    
    kR32G32B32A32_UINT = 71
    
    
    kR32G32B32_FLOAT = 67
    
    
    kR32G32B32_SINT = 69
    
    
    kR32G32B32_UINT = 68
    
    
    kR32G32_FLOAT = 59
    
    
    kR32G32_SINT = 61
    
    
    kR32G32_UINT = 60
    
    
    kR32_FLOAT = 41
    
    
    kR32_SINT = 43
    
    
    kR32_UINT = 42
    
    
    kR8G8B8A8_SINT = 52
    
    
    kR8G8B8A8_SNORM = 50
    
    
    kR8G8B8A8_UINT = 51
    
    
    kR8G8B8A8_UNORM = 49
    
    
    kR8G8B8X8 = 57
    
    
    kR8G8_SINT = 38
    
    
    kR8G8_SNORM = 36
    
    
    kR8G8_UINT = 37
    
    
    kR8G8_UNORM = 35
    
    
    kR8_SINT = 27
    
    
    kR8_SNORM = 25
    
    
    kR8_UINT = 26
    
    
    kR8_UNORM = 24
    
    
    kR9G9B9E5_FLOAT = 21


class MLightParameterInformation(object):
    """
    Class for providing lighting information that may be used with Viewport 2.0.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def arrayParameterCount(*args, **kwargs):
        """
        arrayParameterCount(string) -> int
        
        Return the array size of a parameter. If the parameter is not an array then a value of 0 is returned.
        """
    
        pass
    
    
    def getParameter(*args, **kwargs):
        """
        getParameter(int) -> MIntArraygetParameter(int) -> MFloatArraygetParameter(int) -> MMatrixgetParameter(int) -> MSamplerStateDescgetParameter(int) -> MTexturegetParameter(string) -> MIntArraygetParameter(string) -> MFloatArraygetParameter(string) -> MMatrixgetParameter(string) -> MSamplerStateDescgetParameter(string) -> MTexture
        
        Get parameter value by name or by semantic.
        If more than one parameter matches the semantic, the value of the first matching parameter found will be returned.
        """
    
        pass
    
    
    def getParameterTextureHandle(*args, **kwargs):
        """
        getParameterTextureHandle(int) -> longgetParameterTextureHandle(string) -> long
        
        Get a resource handle for a texture parameter by name or by semantic.
        Returns a long containing a C++ 'void' pointer which points to the resource handle.
        """
    
        pass
    
    
    def lightPath(*args, **kwargs):
        """
        lightPath() -> MDagPath
        
        Returns the DagPath to the scene light. Will return an unitialized DagPath for default lights.
        """
    
        pass
    
    
    def lightType(*args, **kwargs):
        """
        lightType() -> string
        
        Get the classification of the light node.
        """
    
        pass
    
    
    def parameterList(*args, **kwargs):
        """
        parameterList() -> list of string
        
        Get the names of all light parameters that are accessible.
        """
    
        pass
    
    
    def parameterNames(*args, **kwargs):
        """
        parameterNames(int) -> list of string
        
        Get the name of all parameters on the light which are tagged with the stock semantic.
        """
    
        pass
    
    
    def parameterSemantic(*args, **kwargs):
        """
        parameterSemantic(string) -> int
        
        Get the stock semantic for a named parameter:
          MDrawContext.kNoSemantic       No semantic
          MDrawContext.kLightEnabled     Light is enabled
          MDrawContext.kWorldPosition    World space position
          MDrawContext.kWorldDirection   World space direction
          MDrawContext.kIntensity        Intensity
          MDrawContext.kColor            Color
          MDrawContext.kEmitsDiffuse     Emits diffuse lighting
          MDrawContext.kEmitsSpecular    Emits specular lighting
          MDrawContext.kDecayRate        Decay rate
          MDrawContext.kDropoff          Dropoff
          MDrawContext.kCosConeAngle     Cosine of the cone angle
          MDrawContext.kIrradianceIn     Incoming irradiance
          MDrawContext.kShadowMap        Shadow map
          MDrawContext.kShadowSamp       Shadow map sampler
          MDrawContext.kShadowBias       Shadow map bias
          MDrawContext.kShadowMapSize    Shadow map size
          MDrawContext.kShadowViewProj   Shadow map view projection matrix
          MDrawContext.kShadowColor      Shadow color
          MDrawContext.kGlobalShadowOn   Global toggle for whether shadows are enabled or not
          MDrawContext.kShadowOn         Local toggle per light for whether shadows are enabled or not
          MDrawContext.kShadowDirty      Indicates if the contents of the shadow map are out-of-date or uninitialized
        """
    
        pass
    
    
    def parameterType(*args, **kwargs):
        """
        parameterType(string) -> int
        
        Get the type of the named parameter, returns kInvalid if parameter is not found.
        
          MDrawContext.kInvalid        Invalid element type (default value)
          MDrawContext.kBoolean        Boolean
          MDrawContext.kInteger        Signed 32-bit integer
          MDrawContext.kFloat          IEEE single precision floating point
          MDrawContext.kFloat2         IEEE single precision floating point (x2)
          MDrawContext.kFloat3         IEEE single precision floating point (x3)
          MDrawContext.kFloat4         IEEE single precision floating point (x4)
          MDrawContext.kFloat4x4Row    IEEE single precision floating point row-major matrix (4x4)
          MDrawContext.kFloat4x4Col    IEEE single precision floating point column-major matrix (4x4)
          MDrawContext.kTexture2       2D texture
          MDrawContext.kSampler        Sampler
        """
    
        pass
    
    
    __new__ = None
    
    
    kBoolean = 1
    
    
    kColor = 5
    
    
    kCosConeAngle = 10
    
    
    kDecayRate = 8
    
    
    kDropoff = 9
    
    
    kEmitsDiffuse = 6
    
    
    kEmitsSpecular = 7
    
    
    kFloat = 3
    
    
    kFloat2 = 4
    
    
    kFloat3 = 5
    
    
    kFloat4 = 6
    
    
    kFloat4x4Col = 8
    
    
    kFloat4x4Row = 7
    
    
    kGlobalShadowOn = 18
    
    
    kInteger = 2
    
    
    kIntensity = 4
    
    
    kInvalid = 0
    
    
    kIrradianceIn = 11
    
    
    kLightEnabled = 1
    
    
    kNoSemantic = 0
    
    
    kSampler = 10
    
    
    kShadowBias = 14
    
    
    kShadowColor = 17
    
    
    kShadowDirty = 20
    
    
    kShadowMap = 12
    
    
    kShadowMapSize = 15
    
    
    kShadowOn = 19
    
    
    kShadowSamp = 13
    
    
    kShadowViewProj = 16
    
    
    kStartShadowParameters = 11
    
    
    kTexture2 = 9
    
    
    kWorldDirection = 3
    
    
    kWorldPosition = 2


class MPxComponentConverter(object):
    """
    Base class for user defined component converter.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addIntersection(*args, **kwargs):
        """
        addIntersection(intersection) -> self
        
        Maya calls this function for every selection hit on the render item.
        The intersection gives information on the component that was hit.
        
        * intersection (MIntersection) - The selection intersection.
        """
    
        pass
    
    
    def component(*args, **kwargs):
        """
        component() -> MObject
        
        Once all of the geometry hits have been passed to the converter through calls to addIntersection(), Maya will call this method to retrieve the components corresponding to those hits.
        
        Returns the component selection.
        """
    
        pass
    
    
    def initialize(*args, **kwargs):
        """
        initialize(renderItem) -> self
        
        Maya calls this function to allow the converter to initialize itself for the selection on the given render item.
        
        * renderItem (MRenderItem) - The render item.
        """
    
        pass
    
    
    def selectionMask(*args, **kwargs):
        """
        selectionMask() -> MSelectionMask
        
        Maya calls this function to allow the converter to specify the type of components it can handle..
        
        Returns the selection mask.
        """
    
        pass
    
    
    __new__ = None


class MRenderItem(object):
    """
    A single renderable entity.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def associateWithIndexBuffer(*args, **kwargs):
        """
        associateWithIndexBuffer(MIndexBuffer) -> bool
        
        Use to indicate that a particular index buffer should be used with this render item.
        This method must be called from MPxGeometryOverride in order to link index buffers generated in
        the MGeometry class with specific render items.
        Without an index buffer, a render item cannot draw.
        """
    
        pass
    
    
    def availableShaderParameters(*args, **kwargs):
        """
        availableShaderParameters() -> list of string
        
        Returns the list of available shader parameters.
        This is useful for OverrideNonMaterialItem to retrieve default parameters.
        """
    
        pass
    
    
    def boundingBox(*args, **kwargs):
        """
        boundingBox(space=kObject) -> MBoundingBox
        
        Returns the bounding box for the geometry data of the render item.
        Returns None if the render item is unbounded or does not have a valid associated geometry.
        
        * space (Space) - The requested space of the bounding box.
        """
    
        pass
    
    
    def castsShadows(*args, **kwargs):
        """
        castsShadows() -> bool
        
        Get the castsShadows state of the render item.
        """
    
        pass
    
    
    def component(*args, **kwargs):
        """
        component() -> MObject
        
        Get the optional component for the render item.
        """
    
        pass
    
    
    def customData(*args, **kwargs):
        """
        customData() -> MUserData
        
        Retrieve custom data from the render item, returns None if no such data has ever been set on the render item.
        """
    
        pass
    
    
    def depthPriority(*args, **kwargs):
        """
        depthPriority() -> int
        
        Get the depth priority of the render item.
        The higher the depth priority the closer it will be drawn to the camera.
        """
    
        pass
    
    
    def drawMode(*args, **kwargs):
        """
        drawMode() -> int
        
        Get the draw mode for the render item.
        See MGeometry.drawModeString() for a list of valid draw modes.
        """
    
        pass
    
    
    def enable(*args, **kwargs):
        """
        enable(bool) -> self
        
        Enable or disable the render item for rendering.
        """
    
        pass
    
    
    def excludedFromPostEffects(*args, **kwargs):
        """
        excludedFromPostEffects() -> bool
        
        Get whether this item is excluded from post-effects like SSAO and depth-of-field.
        """
    
        pass
    
    
    def geometry(*args, **kwargs):
        """
        geometry() -> MGeometry
        
        Access full geometry data for the render item.
        Returns None if geometry has not been generated yet.
        """
    
        pass
    
    
    def getShader(*args, **kwargs):
        """
        getShader() -> MShaderInstance
        
        Get the shader used by this render item.
        The return value may be None if no shader is set on the render item.
        """
    
        pass
    
    
    def getShaderParameters(*args, **kwargs):
        """
        getShaderParameters(name) -> bool / int / float / tuple of floats
        
        Get the value of a shader parameter.
        This is useful for OverrideNonMaterialItem to retrieve default parameters.
        Use availableShaderParameters() to get the list of available parameters.
        """
    
        pass
    
    
    def isConsolidated(*args, **kwargs):
        """
        isConsolidated() -> bool
        
        Get the consolidated state of the render item.
        """
    
        pass
    
    
    def isEnabled(*args, **kwargs):
        """
        isEnabled() -> bool
        
        Get the enable state of the render item.
        """
    
        pass
    
    
    def isShaderFromNode(*args, **kwargs):
        """
        isShaderFromNode() -> bool
        
        Return True if the shader instance was set by evaluating the shading network of
        a surface shader node (either standard or custom) in the scene via setShaderFromNode().
        """
    
        pass
    
    
    def name(*args, **kwargs):
        """
        name() -> string
        
        Get the name of the render item.
        """
    
        pass
    
    
    def primitive(*args, **kwargs):
        """
        primitive() -> int
        
        Get the primitive type drawn by the render item.
        See MGeometry.primitiveString() for a list of valid primitive types.
        """
    
        pass
    
    
    def primitiveAndStride(*args, **kwargs):
        """
        primitiveAndStride() -> [int, int]
        
        Get the primitive type drawn by the render item, as well as its stride.
        See MGeometry.primitiveString() for a list of valid primitive types.
        """
    
        pass
    
    
    def receivesShadows(*args, **kwargs):
        """
        receivesShadows() -> bool
        
        Get the receivesShadows state of the render item.
        """
    
        pass
    
    
    def requiredVertexBuffers(*args, **kwargs):
        """
        requiredVertexBuffers() -> MVertexBufferDescriptorList
        
        Get a list of vertex buffer descriptors that describe the buffers required to draw the given render item.
        These are determined by the shader that will be used to draw the render item and so this method will return
        a non-empty list as long as there is a shader assigned to the render item.
        """
    
        pass
    
    
    def selectionMask(*args, **kwargs):
        """
        selectionMask() -> MSelectionMask
        
        Get the render item selection mask.
        """
    
        pass
    
    
    def setCastsShadows(*args, **kwargs):
        """
        setCastsShadows(bool) -> self
        
        Set the castsShadows state of the render item.
        """
    
        pass
    
    
    def setCustomData(*args, **kwargs):
        """
        setCustomData(MUserData) -> self
        
        Associate custom user data with this render item.
        If deleteAfterUse() is true on the data, then the data object will automatically be deleted when the render item is deleted.
        Otherwise, the lifetime of the user data object is the responsibility of the caller.
        """
    
        pass
    
    
    def setDepthPriority(*args, **kwargs):
        """
        setDepthPriority(int) -> self
        
        Set the depth priority of the render item.
        The higher the depth priority the closer it will be drawn to the camera.
        """
    
        pass
    
    
    def setDrawMode(*args, **kwargs):
        """
        setDrawMode(int) -> self
        
        Set the draw mode for the render item.
        If the draw mode is all, the render item will be drawn regardless of the viewport draw mode.
        Otherwise the render item will only be drawn when the viewport is set to draw objects in the specified mode.
        See MGeometry.drawModeString() for a list of valid draw modes.
        """
    
        pass
    
    
    def setExcludedFromPostEffects(*args, **kwargs):
        """
        setExcludedFromPostEffects(bool) -> self
        
        Set whether this item should be excluded from post-effects like SSAO and depth-of-field.
        Render items default to being excluded from post-effects.
        """
    
        pass
    
    
    def setMatrix(*args, **kwargs):
        """
        setMatrix(MMatrix) -> bool
        
        Override the object to world transformation matrix to use when drawing this render item.
        If unset, the render item will draw using the transformation matrix of the associated Maya DAG node.
        Pass None to this method to remove the override
        """
    
        pass
    
    
    def setReceivesShadows(*args, **kwargs):
        """
        setReceivesShadows(bool) -> self
        
        Set the receivesShadows state of the render item.
        """
    
        pass
    
    
    def setSelectionMask(*args, **kwargs):
        """
        setSelectionMask(mask) -> selfsetSelectionMask(type) -> self
        
        Set the render item selection mask.
        
        * mask (MSelectionMask) - The selection mask.
        * type (int) - The selection type (see MSelectionMask.addMask() for a list of values).
        """
    
        pass
    
    
    def setShader(*args, **kwargs):
        """
        setShader(shader, customStreamName=None) -> bool
        
        Set shader to use when drawing this render item.
        If no shader is ever set the render item will not draw.
        The render item makes a copy of the instance so it is safe to delete the instance after
        assignment without affecting any render items the instance was assigned to.
        
        * shader (MShaderInstance) - The shader to use when drawing this item.
        * customStreamName (string) - If specified, shader will generate geometry requirements with the given name.
        """
    
        pass
    
    
    def setShaderFromNode(*args, **kwargs):
        """
        setShaderFromNode(shaderNode, shapePath, linkLostCb=None, linkLostUserData=None, nonTextured=False) -> self
        
        Set shader to use when drawing this render item. If no shader is ever set this render item will not draw. This method sets the shader instance to a render item by evaluating the shading network of a surface shader node (either standard or custom) in the scene.
        
        This method only affects items explicitly created by the plug-in.
        
        If the surface shader node is None or unsupported by neither Maya nor the plug-in, this method will clear the shader assignment on the render item, which will thus not be drawn.
        
        The shape path is used as the object context during shading network evaluation to ensure that the shader instance fits its requirements. If it is invalid, a shader instance to fit basic requirements is still created but will not include any requirements which are geometry dependent.
        
        The linkLostCb will be invoked whenever the link to the surface shader node is lost. The link can be lost in a number of ways, e.g. shader nodes are deleted or shading network connections are modified. However, the linkLostCb won't be invoked for a change to shading group level connection; if needed, it is the DG node's responsibility to monitor any changes to shading group level connection by MPxNode::connectionMade and MPxNode::connectionBroken.
        
        There is no guarantee that the surface shader node is still valid after the link is lost. The linkLostCb should check the validity and assign the render item with a shader instance appropriately.
        
        After the shader instance is set, its parameter values can be automatically updated by Viewport 2.0 whenever the related shading attributes changed, therefore access to the shader instance is not provided in order to avoid unexpected behavior.
        
         * shaderNode (MObject) - The surface shader node.
         * shapePath (MDagPath) - The path to the instance of the assigned geometry.
         * linkLostCb (callable) - Function to be invoked whenever the link to the surface shader node is lost.
         * linkLostUserData (MUserData) - User supplied data to be passed into the link lost callback.
         * nonTextured (bool) - Whether or not a non-textured effect instance is needed. The default value is false.
        """
    
        pass
    
    
    def sourceDagPath(*args, **kwargs):
        """
        sourceDagPath() -> MDagPath
        
        Retrieve the MDagPath for the instance of the object that generated this render item.
        
         If there are many object instances contributing due to consolidation then only one dag path out of all the objects is returned.
        
        The method sourceIndexMapping() should be used if the item is consolidatedto access the corresponding dag paths for the objects making up this item.
        """
    
        pass
    
    
    def sourceIndexMapping(*args, **kwargs):
        """
        sourceIndexMapping() -> MGeometryIndexMapping
        
        Get the geometry index mapping of the objects contained by this consolidated render item.
        Multiple geometries can be concatenated to improve rendering performance.
        You can access the index mapping of the geometries in order to render them separately.
        The index mapping gives you the name, and index start and length of each geometry.
        """
    
        pass
    
    
    def type(*args, **kwargs):
        """
        type() -> int
        
        Get the type of the render item.
        
          MRenderItem.MaterialSceneItem
             A render item which represents an object in the scene that should interact with the rest of the scene and viewport settings (e.g. a shaded piece of geometry which should be considered in processes like shadow computation, viewport effects, etc.). Inclusion in such processes can also still be controlled through the appropriate methods provided by this class.
          MRenderItem.NonMaterialSceneItem
             A render item which represents an object in the scene that should not interact with the rest of the scene and viewport settings, but that is also not part of the viewport UI (e.g. a curve or a bounding box which should not be hidden when 'Viewport UI' is hidden but which should also not participate in processes like shadow computation, viewport effects, etc.).
          MRenderItem.DecorationItem
             A render item which should be considered to be part of the viewport UI (e.g. selection wireframe, components, etc.).
          MRenderItem.InternalItem
             A render item which was created by Maya for internal purposes (e.g. A render item created as the result of a shader being assigned to a DAG node).
          MRenderItem.InternalMaterialItem
                        An internally created MaterialSceneItem for non-textured mode display.
          MRenderItem.InternalTexturedMaterialItem
             An internally created MaterialSceneItem for textured mode display.
          MRenderItem.InternalUnsupportedMaterialItem
             An internally created MaterialSceneItem for showing an unsupported material
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(name, type, primitive) -> MRenderItem
        create(item) -> MRenderItem
        
        Static MRenderItem creation utility.
        
        Create new render item:
        * name (string) - The name of the render item (should be non-empty).
        * type (int) - The type of the render item.
        * primitive (int) - The primitive type of the render item.
        
        See MRenderItem.type() for a list of valid render item types.
        Internal types are not allowed and will result no item being created.
        See MGeometry.primitiveString() for a list of valid primitive types.
        
        Create new render item and copy all parameters from the incoming MRenderItem:
        * item (MRenderItem) - The item to copy.
        """
    
        pass
    
    
    def destroy(*args, **kwargs):
        """
        destroy(item) -> None
        
        Static MRenderItem destruction utility.
        Destroys the internal data structures associated with this MRenderItem.
        Any attempt to use the MRenderItem after this will result in an exception.
        """
    
        pass
    
    
    DecorationItem = 2
    
    
    InternalItem = 3
    
    
    InternalMaterialItem = 4
    
    
    InternalTexturedMaterialItem = 5
    
    
    InternalUnsupportedMaterialItem = 6
    
    
    MaterialSceneItem = 0
    
    
    NonMaterialSceneItem = 1
    
    
    OverrideNonMaterialItem = 7
    
    
    __new__ = None
    
    
    sActiveLineDepthPriority = 9
    
    
    sActivePointDepthPriority = 17
    
    
    sActiveWireDepthPriority = 5
    
    
    sDormantFilledDepthPriority = 0
    
    
    sDormantPointDepthPriority = 14
    
    
    sDormantWireDepthPriority = 2
    
    
    sHiliteWireDepthPriority = 4
    
    
    sSelectionDepthPriority = 21


class MDepthStencilState(object):
    """
    Container class for an acquired complete GPU depth stencil state.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def desc(*args, **kwargs):
        """
        desc() -> MDepthStencilStateDesc
        
        Get the depth-stencil state descriptor that was used to create the state object.
        """
    
        pass
    
    
    def resourceHandle(*args, **kwargs):
        """
        resourceHandle() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the draw API dependent handle for a depth-stencil state.
        For OpenGL, such a handle does not exist and a NULL pointer will be returned.
        For DirectX, a pointer to a Direct3D state will be returned.
        """
    
        pass
    
    
    __new__ = None
    
    
    kDecrementStencil = 8
    
    
    kDecrementStencilSat = 5
    
    
    kIncrementStencil = 7
    
    
    kIncrementStencilSat = 4
    
    
    kInvertStencil = 6
    
    
    kKeepStencil = 1
    
    
    kReplaceStencil = 3
    
    
    kZeroStencil = 2


class MPxGeometryOverride(object):
    """
    Base for user-defined classes to prepare geometry for drawing.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addUIDrawables(*args, **kwargs):
        """
        addUIDrawables(path, drawManager, frameContext) -> self
        
        For each instance of the object, besides the render items updated in updateRenderItems() there is also a render item list for rendering simple UI elements.
        This stage gives the plugin access to MUIDrawManager which aids in drawing simple geometry like line, circle, rectangle, text, etc.
        
        Overriding this methods is not always necessary, but if you want to override it, please also override 'hasUIDrawables()' to make it return True or the overridden method will not be called.
        
        If you are not going to override this function, please don't make 'hasUIDrawables()' return True or there may be some wasted performance overhead.
        
        Implementation of this method here is empty.
        
        * path (MDagPath) - The path to the instance to update auxiliary items for.
        * drawManager (MUIDrawManager) - The draw manager used to draw simple geometry.
        * frameContext (MFrameContext) - Frame level context information.
        """
    
        pass
    
    
    def cleanUp(*args, **kwargs):
        """
        cleanUp() -> self
        
        Called after all other stages are completed. Clean up any cached data stored from the updateDG() phase.
        """
    
        pass
    
    
    def handleTraceMessage(*args, **kwargs):
        """
        handleTraceMessage(message) -> self
        
        When debug tracing is enabled via MPxGeometryOverride::traceCallSequence(),
        this method will be called for each trace message.
        
        The default implementation will print the message
        to stderr.
        
        * message - A string which will provide feedback on either an
        internal or plug-in call location. To help distinguish which
        geometry override a message is associated with, the full path
        name for the DAG object (associated with the geometry override) may
        be included as part of the string.
        """
    
        pass
    
    
    def hasUIDrawables(*args, **kwargs):
        """
        hasUIDrawables() -> bool
        
        Query whether 'addUIDrawables()' will be called or not.
        
        In order for any override for the addUIDrawables() method to be called this method must also be overridden to return True.
        
        This method should not be overridden if addUIDrawables() has not also been overridden as there may be associated wasted overhead.
        """
    
        pass
    
    
    def isIndexingDirty(*args, **kwargs):
        """
        isIndexingDirty(item) -> bool
        
        Returns True if the index buffer needs to be updated.
        
        This method is called for each render item on the assocated DAG object whenever the object changes. This method is passed a render item. This method should return True if the indexing for the render item has changed since the last frame. Note that returning False from isIndexingDirty may NOT prevent populate geometry from requiring that an index buffer is updated.
        
        * item (MRenderItem) - The render item in question.
        """
    
        pass
    
    
    def isStreamDirty(*args, **kwargs):
        """
        isStreamDirty(desc) -> bool
        
        Returns True if the vertex buffer needs to be updated.
        
        This method is called for each geometry stream on the assocated DAG object whenever the object changes. This method is passed a vertex buffer descriptor representing one stream on the object to be updated. This method should return True if it is safe to reuse the existing buffer rather than filling a new buffer with data. Note that returning False from isStreamDirty may NOT prevent populateGeometry from requiring that a stream be updated.
        
        * desc (MVertexBufferDescriptor) - The description of the vertex buffer.
        """
    
        pass
    
    
    def populateGeometry(*args, **kwargs):
        """
        populateGeometry(requirements, renderItems, data) -> self
        
        Implementations of this method should create and populate vertex and index buffers on the MGeometry instance 'data' in order to fulfill all of the geometry requirements defined by the 'requirements' parameter. Failure to do so will result in the object either drawing incorrectly or not drawing at all. See the documentation of MGeometryRequirements and MGeometry for more details on the usage of these classes. The geometry requirements will ask for index buffers on demand. Implementations can force the geometry requirements to update index buffers by calling MRenderer.setGeometryDrawDirty() with topologyChanged setting to True.
        
        * requirements (MGeometryRequirements) - The requirements that need to be satisfied.
        * renderItems (MRenderItemList) - The list of render items that need to be updated.
        * data [OUT] (MGeometry) - The container for the geometry data
        """
    
        pass
    
    
    def refineSelectionPath(*args, **kwargs):
        """
        refineSelectionPath(selectInfo, hitItem, path, components, objectMask) -> bool
        
        This method is called during the hit test phase of the viewport 2.0 selection and is used to override the selected path, the selected components or simply reject the selection.
        Should return True if the selection candidate is acceptable.
        
        One can decide to change the selected path (ie: select the bottom-most transform instead of the proposed path).
        One can decide to remove or add component to the proposed selected list.
        One can decide to change the selection mask of the object (ie: override the selection mask returned by a component converter).
        One can decide that the proposed selection (path or component) is not acceptable and discard it (ie: return False).
        
        The default implementation makes no changes to 'path', 'components' or 'objectMask' and returns True (i.e. the selection is accepted).
        
        * selectInfo (MSelectionInfo) - The selection info
        * hitItem (MRenderItem) - The render item hit
        * path [IN/OUT] (MDagPath) - The selected path
        * components [IN/OUT] (MObject) - The selected components
        * objectMask [IN/OUT] (MSelectionMask) - The object selection mask
        """
    
        pass
    
    
    def supportedDrawAPIs(*args, **kwargs):
        """
        supportedDrawAPIs() -> DrawAPI
        
        Returns the draw API supported by this override.
        """
    
        pass
    
    
    def traceCallSequence(*args, **kwargs):
        """
        traceCallSequence() -> bool
        
        This method allows a way for a plug-in to examine
        the basic call sequence for a geometry override.
        
        The default implementation returns false meaning no
        tracing will occur.
        """
    
        pass
    
    
    def updateDG(*args, **kwargs):
        """
        updateDG() -> self
        
        Perform any work required to translate the geometry data that needs to get information from the dependency graph.  This should be the only place that dependency graph evaluation occurs. Any data retrieved should be cached for later stages.
        """
    
        pass
    
    
    def updateRenderItems(*args, **kwargs):
        """
        updateRenderItems(path, list) -> self
        
        This method is called for each instance of the associated DAG object whenever the object changes. The method is passed the path to the instance and the current list of render items associated with that instance. By default the list will contain one render item for each shader assigned to the instance. Implementations of this method method may add, remove or modify items in the list. Note that removal of items created by Maya for assigned shaders is not allowed and will fail. As an alternative this method can disable those items so that they do not draw.
        
        * path (MDagPath) - The path to the instance to update render items for
        * list [IN/OUT] (MRenderItemList) - The current render item list, items may be modified, added or removed.
        """
    
        pass
    
    
    def updateSelectionGranularity(*args, **kwargs):
        """
        updateSelectionGranularity(path, selectionContext) -> self
        
        This is method is called during the pre-filtering phase of the viewport 2.0 selection and is used to setup the selection context of the given DAG object.
        
        This is useful to specify the selection level, which defines what can be selected on the object :
          MSelectionContext.kNone        Nothing can be selected
          MSelectionContext.kObject      Object can be selected as a whole
          MSelectionContext.kComponent   Parts of the object - such as vertex, edge or face - are selectable
        This is used to discard objects that are not selectable given the current selection mode (see MGlobal.selectionMode()).
        
        The default implementation leaves the selection level set at its default value, which is kObject.
        
         path (MDagPath) - The path to the instance to update the selection context for
         selectionContext [OUT] (MSelectionContext) - The selection context
        """
    
        pass
    
    
    def pointSnappingActive(*args, **kwargs):
        """
        pointSnappingActive() -> bool
        
        Returns True if selection has been launched to find snap points.
        To participate, you need to have at least one render item with point geometry
        and MSelectionMask.kSelectPointsForGravity set in MRenderItem.selectableMask().
        - The granularity must be set to MSelectionContext.kComponent in updateSelectionGranularity()
        - A component converter is not necessary in this scenario.
        - refineSelectionPath() will not be called. All points present in the render item will be
        considered suitable locations for snapping.
        """
    
        pass
    
    
    __new__ = None


class MVertexBufferArray(object):
    """
    Array of Vertex buffers.
    """
    
    
    
    def __getitem__(*args, **kwargs):
        """
        x.__getitem__(y) <==> x[y]
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __len__(*args, **kwargs):
        """
        x.__len__() <==> len(x)
        """
    
        pass
    
    
    def append(*args, **kwargs):
        """
        append(MVertexBuffer, name) -> self
        
        Add a new vertex buffer to the list.
        """
    
        pass
    
    
    def clear(*args, **kwargs):
        """
        clear() -> self
        
        Clear the array.
        """
    
        pass
    
    
    def getBuffer(*args, **kwargs):
        """
        getBuffer(string) -> MVertexBuffer
        
        Get vertex buffer by name.
        """
    
        pass
    
    
    def getName(*args, **kwargs):
        """
        getName(int) -> string
        
        Get the name of the buffer at desired index.
        """
    
        pass
    
    
    __new__ = None


class MPassContext(object):
    """
    Class to allow access to pass context information.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def hasShaderOverride(*args, **kwargs):
        """
        hasShaderOverride() -> bool
        
        Return if there is a shader instance override set for the current pass.
        """
    
        pass
    
    
    def passIdentifier(*args, **kwargs):
        """
        passIdentifier() -> string
        
        Return the identifier for the pass context.
        """
    
        pass
    
    
    def passSemantics(*args, **kwargs):
        """
        passSemantics() -> list of string
        
        Return an array of semantics for the pass context.
        """
    
        pass
    
    
    def shaderOverrideInstance(*args, **kwargs):
        """
        shaderOverrideInstance() -> MShaderInstance
        
        Return the shader instance override set for the current pass.
        
        When the returned new shader instance is no longer needed, MShaderManager::releaseShader() should be called to notify the shader manager that the caller is done with the shader.
        """
    
        pass
    
    
    __new__ = None
    
    
    kBeginRenderSemantic = 'beginRender'
    
    
    kBeginSceneRenderSemantic = 'beginSceneRender'
    
    
    kColorPassSemantic = 'colorPass'
    
    
    kCullBackSemantic = 'cullBack'
    
    
    kCullFrontSemantic = 'cullFront'
    
    
    kDOFPassSemantic = 'dofPass'
    
    
    kDepthPassSemantic = 'depthPass'
    
    
    kEndRenderSemantic = 'endRender'
    
    
    kEndSceneRenderSemantic = 'endSceneRender'
    
    
    kMaterialOverrideSemantic = 'materialOverride'
    
    
    kMotionVectorPassSemantic = 'motionVectorPass'
    
    
    kNonPEPatternPassSemantic = 'nonPEPatternPass'
    
    
    kNormalDepthPassSemantic = 'normalDepthPass'
    
    
    kOpaqueGeometrySemantic = 'opaqueGeometry'
    
    
    kOpaqueUISemantic = 'opaqueUIList'
    
    
    kPEPatternPassSemantic = 'PEPatternPass'
    
    
    kPostUIGeometrySemantic = 'postUIGeometry'
    
    
    kPreUIGeometrySemantic = 'preUIGeometry'
    
    
    kSelectionPassSemantic = 'selectionPass'
    
    
    kShadowPassSemantic = 'shadowPass'
    
    
    kTransparentGeometrySemantic = 'transparentGeometry'
    
    
    kTransparentPeelAndAvgSemantic = 'transparentPeelAndAvg'
    
    
    kTransparentPeelSemantic = 'transparentPeel'
    
    
    kTransparentUISemantic = 'transparentUIList'
    
    
    kTransparentWeightedAvgSemantic = 'transparentWeightedAvg'
    
    
    kUIGeometrySemantic = 'uiGeometry'
    
    
    kUserPassSemantic = 'userPass'
    
    
    kXrayUISemantic = 'xrayUIList'


class MSamplerState(object):
    """
    Container class for an acquired complete GPU sampler state.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def desc(*args, **kwargs):
        """
        desc() -> MSamplerStateDesc
        
        Get the sampler state descriptor that was used to create the state object.
        """
    
        pass
    
    
    def resourceHandle(*args, **kwargs):
        """
        resourceHandle() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the draw API dependent handle for a sampler state.
        For OpenGL, such a handle does not exist and a NULL pointer will be returned.
        For DirectX, a pointer to a Direct3D state will be returned.
        """
    
        pass
    
    
    __new__ = None
    
    
    kAnisotropic = 85
    
    
    kMinLinear_MagMipPoint = 16
    
    
    kMinLinear_MagPoint_MipLinear = 17
    
    
    kMinMagLinear_MipPoint = 20
    
    
    kMinMagMipLinear = 21
    
    
    kMinMagMipPoint = 0
    
    
    kMinMagPoint_MipLinear = 1
    
    
    kMinPoint_MagLinear_MipPoint = 4
    
    
    kMinPoint_MagMipLinear = 5
    
    
    kTexBorder = 4
    
    
    kTexClamp = 3
    
    
    kTexMirror = 2
    
    
    kTexWrap = 1


class MPxVertexBufferGenerator(object):
    """
    Base class for user defined vertex buffer generators.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def createVertexStream(*args, **kwargs):
        """
        createVertexStream(object, vertexBuffer, targetIndexing, sharedIndexing, sourceStreams) -> self
        
        This method gets called to allow the generator to fill in the data for a custom vertex stream. Use the requirements in the vertexBuffer to get the description of the stream. Use vertexBuffer.acquire() and vertexBuffer.commit() to fill the buffer. 
        
        * object (MObject) - The dag object being evaluated.
        * vertexBuffer [IN/OUT] (MVertexBuffer) - The vertex buffer to fill.
        * targetIndexing (MComponentDataIndexing) - Vertex index mapping from targetIndexing.getComponentType() space to vertex buffer space.
        * sharedIndexing (MComponentDataIndexing) - Vertex index mapping in the declared MComponentDataIndexing::MComponentType space.
        * sourceStreams (MVertexBufferArray) - Array of Vertex Buffers that can be used to create the new stream.
        """
    
        pass
    
    
    def getSourceIndexing(*args, **kwargs):
        """
        getSourceIndexing(object, sourceIndexing) -> self
        
        This function is called to allow the vertex buffer generator to provide its vertex indexing information as well as the space the vertices are in.  The indexing and the component type are stored in the  sourceIndexing argument.  This indexing information is to allow the system to identify any potential  vertex sharing that is common across all vertex requirements. 
        
        * object (MObject) - The object being evaluated.
        * sourceIndexing [OUT] (MComponentDataIndexing) - Vertex index mapping in the declared MComponentDataIndexing::MComponentType space.
        """
    
        pass
    
    
    def getSourceStreams(*args, **kwargs):
        """
        getSourceStreams(object, sourceStreams) -> self
        
        This function is called to allow the vertex buffer generator to provide the list of stream names that it requires. The names will be used to fill the array of vertex buffers that will be passed to createVertexStream. 
        
        * object (MObject) - The dag object being evaluated.
        * sourceStreams [OUT] (list of strings) - Array of strings.
        """
    
        pass
    
    
    __new__ = None


class MIndexBufferDescriptor(object):
    """
    Describes an indexing scheme.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    component = None
    
    dataType = None
    
    indexType = None
    
    name = None
    
    primitive = None
    
    primitiveStride = None
    
    __new__ = None
    
    
    kControlVertex = 6
    
    
    kCustom = 14
    
    
    kEdgeLine = 1
    
    
    kEditPoint = 5
    
    
    kFaceCenter = 4
    
    
    kHullEdgeCenter = 10
    
    
    kHullEdgeLine = 7
    
    
    kHullFaceCenter = 9
    
    
    kHullTriangle = 8
    
    
    kHullUV = 11
    
    
    kSubDivEdge = 12
    
    
    kTangent = 13
    
    
    kTriangle = 3
    
    
    kTriangleEdge = 2
    
    
    kVertexPoint = 0


class MShaderManager(object):
    """
    Provides access to MShaderInstance objects for use in Viewport 2.0.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addShaderIncludePath(*args, **kwargs):
        """
        addShaderIncludePath(string) -> self
        
        Add a path to the list of paths used for searching for shader include files.
        """
    
        pass
    
    
    def addShaderPath(*args, **kwargs):
        """
        addShaderPath(string) -> self
        
        Add a path to the list of shader search paths.
        """
    
        pass
    
    
    def clearEffectCache(*args, **kwargs):
        """
        clearEffectCache() -> self
        Clear the effect cache.
        This will allow all relevant effects to be updated when the implementation of a shader fragment or fragment graph has been modified.
        """
    
        pass
    
    
    def getEffectsBufferShader(*args, **kwargs):
        """
        getEffectsBufferShader(buffer, size, techniqueName, macros=None, useEffectCache=True, preCb=None, postCb=None) -> MShaderInstance
        
        Get a new instance of a shader generated from a block of memory containing device-specific source code (as char*).
        
        * buffer (const void*) - A pointer to the block of memory from which to load the effect.
        * size (unsigned int) - The size of the effect to load in bytes.
        * techniqueName (string) - The name of a technique in the effect. If an empty string is specified then the first technique in the effect will be used.
        * macros (sequence of MShaderCompileMacro) - Sequence of shader macros. The default value is None, meaning that no macros are specified.
        * useEffectCache (bool) - Use the internal effect cache to prevent reloading the effect every time it is requested. The default value is True.
        * preCb (function) - A function, or other Python callable, to be called before render items are drawn with this shader.
        * postCb (function) - A function, or other Python callable, to be called after render items are drawn with this shader.
              see MShaderManager.getEffectsFileShader() for details on the preCb and postCb functions
        """
    
        pass
    
    
    def getEffectsFileShader(*args, **kwargs):
        """
        getEffectsFileShader(effecsFileName, techniqueName, macros=None, useEffectCache=True, preCb=None, postCb=None) -> MShaderInstance
        
        Get a new instance of a shader generated from an effects file stored on disk.
        
        * effectsFileName (string) - The effects file.
        * techniqueName (string) - The name of a technique in the effects file. If an empty string is specified then the first technique in the effects file will be used.
        * macros (sequence of MShaderCompileMacro) - Sequence of shader macros. The default value is None, meaning that no macros are specified.
        * useEffectCache (bool) - Use the internal effect cache to prevent reloading the effect file every time it is requested. The default value is True.
        * preCb (function) - A function, or other Python callable, to be called before render items are drawn with this shader.
                  def preCb(MDrawContext, MRenderItemList, MShaderInstance)
        * postCb (function) - A function, or other Python callable, to be called after render items are drawn with this shader.
                  def postCb(MDrawContext, MRenderItemList, MShaderInstance)
        """
    
        pass
    
    
    def getEffectsTechniques(*args, **kwargs):
        """
        getEffectsTechniques(effecsFileName, macros=None, useEffectCache=True) -> tuple of strings
        
        Analyzes a given effect file to extract the names of the techniques that are defined.
        
        * effectsFileName (string) - The effects file.
        * macros (sequence of MShaderCompileMacro) - Sequence of shader macros. The default value is None, meaning that no macros are specified.
        * useEffectCache (bool) - Use the internal effect cache to prevent reloading the effect every time it is requested. The default value is True.
        """
    
        pass
    
    
    def getFragmentShader(*args, **kwargs):
        """
        getFragmentShader(fragmentName, structOutputName, decorateFragment, preCb=None, postCb=None) -> MShaderInstance
        
        Get a new instance of a shader generated from a named shader fragment or fragment graph.
        
        * fragmentName (string) - The name of the fragment to generate a shader from.
        * structOutputName (string) - If the output of the fragment is a struct, use this parameter to specify which member of the struct to use.
                                                                         This parameter is ignored if the output of the fragment is not a struct.
        * decorateFragment (bool) - If True, Maya state fragments will be added.
        * preCb (function) - A function, or other Python callable, to be called before render items are drawn with this shader.
        * postCb (function) - A function, or other Python callable, to be called after render items are drawn with this shader.
              see MShaderManager.getEffectsFileShader() for details on the preCb and postCb functions
        """
    
        pass
    
    
    def getShaderFromNode(*args, **kwargs):
        """
        getShaderFromNode(shaderNode, path, linkLostCb=None, linkLostUserData=None, preCb=None, postCb=None, nonTextured=False) -> MShaderInstance
        
        Get the shader instance assigned to a shader node.
        
        * shaderNode (MObject) - The surface shader node.
        * path (MDagPath) - The path to the instance of the assigned geometry.
        * linkLostCb (function) - A function, or other Python callable, to be called when this shader instance is no longer connected to the node it was translated for.
                  def linkLostCb(MShaderInstance, MUserData)
        * linkLostUserData (MUserData) - User supplied data to be passed into the link lost callback.
               This data will not be deleted internally and the lifetime must be managed by the caller.
               The link lost callback will only be called once so it is safe to delete this data anytime after the callback has been triggered.
        * preCb (function) - A function, or other Python callable, to be called before render items are drawn with this shader.
        * postCb (function) - A function, or other Python callable, to be called after render items are drawn with this shader.
              see MShaderManager.getEffectsFileShader() for details on the preCb and postCb functions.
        * nonTextured (bool) - Whether or not a non-textured effect instance is needed. The default value is false.
        """
    
        pass
    
    
    def getStockShader(*args, **kwargs):
        """
        getStockShader(shaderId, preCb=None, postCb=None) -> MShaderInstance
        
        Get a new instance of a stock shader.
        
        * shaderId (int) - The Id of stock shader.
        * preCb (function) - A function, or other Python callable, to be called before render items are drawn with this shader.
        * postCb (function) - A function, or other Python callable, to be called after render items are drawn with this shader.
              see MShaderManager.getEffectsFileShader() for details on the preCb and postCb functions
        
        List of available stock shader:
          k3dSolidShader                  An instance of a solid color shader for 3d rendering
          k3dBlinnShader                  An instance of a Blinn shader for 3d rendering
          k3dDefaultMaterialShader        An instance of a stock "default material" shader for 3d rendering
          k3dSolidTextureShader           An instance of a stock solid texture shader for 3d rendering
          k3dCPVFatPointShader            An instance of a stock color per vertex fat point shader for 3d rendering
          k3dColorLookupFatPointShader    An instance of a stock fat point shader using a 1D color texture lookup.
          k3dShadowerShader               An instance of a stock shader which can be used when rendering shadow maps
          k3dFatPointShader               An instance of a stock fat point shader for 3d rendering
          k3dThickLineShader              An instance of a stock thick line shader for 3d rendering
          k3dCPVThickLineShader           An instance of a color per vertex stock thick line shader for 3d rendering
          k3dDashLineShader               An instance of a stock dash line shader for 3d rendering
          k3dCPVDashLineShader            An instance of a color per vertex stock dash line shader for 3d rendering
          k3dStippleShader                An instance of a stipple shader for drawing 3d filled triangles
          k3dThickDashLineShader          An instance of a stock thick dash line shader for 3d rendering.
          k3dCPVThickDashLineShader       An instance of a color per vertex stock thick dash line shader for 3d rendering.
          k3dDepthShader                  An instance of a stock shader that can be used for 3d rendering of depth
          k3dCPVSolidShader               An instance of a stock solid color per vertex shader for 3d rendering
          k3dIntegerNumericShader         An instance of a stock shader for drawing single integer values per vertex for 3d rendering.
          k3dFloatNumericShader           An instance of a stock shader for drawing single float values values per vertex for 3d rendering.
          k3dFloat2NumericShader          An instance of a stock shader for drawing 2 float values per vertex for 3d rendering.
          k3dFloat3NumericShader          An instance of a stock shader for drawing 3 float values per vertex for 3d rendering.
          k3dPointVectorShader            An instance of a stock shader that can be used for 3d rendering of lines based on a point and a vector stream
        """
    
        pass
    
    
    def releaseShader(*args, **kwargs):
        """
        releaseShader(MShaderInstance) -> None
        Deletes the MShaderInstance and releases its reference to the underlying shader which is held by the MShaderInstance object.
        """
    
        pass
    
    
    def removeEffectFromCache(*args, **kwargs):
        """
        removeEffectFromCache(effecsFileName, techniqueName, macros=None) -> self
        Remove an effect from the cache.
        This is particulary useful when calling the getEffectsTechniques() and/or getEffectsFileShader() with the flag useEffectCache set to True for maximum performance, and will allow reloading the effect from the disk when the shader file has been modified.
        * effectsFileName (string) - The effects file.
        * techniqueName (string) - The name of a technique in the effects file. If an empty string is specified then the first technique in the effects file will be used.
        * macros (sequence of MShaderCompileMacro) - Sequence of shader macros. The default value is None, meaning that no macros are specified.
        """
    
        pass
    
    
    def shaderIncludePaths(*args, **kwargs):
        """
        shaderIncludePaths() -> list of strings
        
        Query the list of search paths user for searching for shader include files.
        """
    
        pass
    
    
    def shaderPaths(*args, **kwargs):
        """
        shaderPaths() -> list of strings
        
        Query the list of shader search paths.
        """
    
        pass
    
    
    def getLastError(*args, **kwargs):
        """
        getLastError() -> string
        
        Get the description of the last error encountered by the shader manager regarding an effect.
        This includes fragment and effect loading, technique query, and shader binding.
        """
    
        pass
    
    
    def getLastErrorSource(*args, **kwargs):
        """
        getLastErrorSource(displayLineNumber=False, filterSource=False, numSurroundingLines=2) -> string
        
        Get the source of the shader that generated the last error. See getLastError().
         * displayLineNumber (bool) - If True, add the number line at the beginning of each line. The default is False.
         * filterSource (bool) - If True, only display the lines surrounding the error(s). The default is False.
         * numSurroundingLines (int) - The number of leading and trailing lines to display around filtered source. The default is 2.
        """
    
        pass
    
    
    def isSupportedShaderSemantic(*args, **kwargs):
        """
        isSupportedShaderSemantic(string) -> bool
        Return if a given string is a supported shader semantic.
        """
    
        pass
    
    
    __new__ = None
    
    
    k3dBlinnShader = 1
    
    
    k3dCPVDashLineShader = 13
    
    
    k3dCPVFatPointShader = 4
    
    
    k3dCPVShader = 4
    
    
    k3dCPVSolidShader = 18
    
    
    k3dCPVThickDashLineShader = 16
    
    
    k3dCPVThickLineShader = 11
    
    
    k3dColorLookupFatPointShader = 5
    
    
    k3dColorOpacityLookupFatPointShader = 7
    
    
    k3dDashLineShader = 12
    
    
    k3dDefaultMaterialShader = 2
    
    
    k3dDepthShader = 17
    
    
    k3dFatPointShader = 9
    
    
    k3dFloat2NumericShader = 21
    
    
    k3dFloat3NumericShader = 22
    
    
    k3dFloatNumericShader = 20
    
    
    k3dIntegerNumericShader = 19
    
    
    k3dOpacityLookupFatPointShader = 6
    
    
    k3dPointVectorShader = 23
    
    
    k3dShadowerShader = 8
    
    
    k3dSolidShader = 0
    
    
    k3dSolidTextureShader = 3
    
    
    k3dStippleShader = 14
    
    
    k3dThickDashLineShader = 15
    
    
    k3dThickLineShader = 10


class MPxIndexBufferMutator(object):
    """
    Base class for user defined index buffer mutators.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def mutateIndexing(*args, **kwargs):
        """
        mutateIndexing(sourceIndexBuffers, vertexBuffers, indexBuffer) -> (int, int)
        
        This method gets called to allow the generator to mutate the data for a custom index stream using information stored in the vertex buffers.
        
        * sourceIndexBuffers (MComponentDataIndexingList) - Current values for the index buffers.
        * vertexBuffers (MVertexBufferArray) - All vertex buffers generated for this primitive.
        * indexBuffer [OUT] (MIndexBuffer) - The index buffer to fill.
        
        Returns the type of primitive of the generated indexing and the stride of the generated indexing, only valid when the returned primitive type is kPatch
        See MGeometry.primitiveString() description for a list of valid primitive types.
        """
    
        pass
    
    
    __new__ = None


class MPxSubSceneOverride(object):
    """
    Base class for Viewport 2.0 drawing of DAG nodes which represent sub-scenes.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addInstanceTransform(*args, **kwargs):
        """
        addInstanceTransform(renderItem, transform) -> int
        
        Returns The instance ID for the new instance. This ID can be used to change the matrix or remove it. A return value of 0 indicates an error (render item does not support instancing or invalid state). 0 is never a valid instance ID.
        
        Add an additional instance for a render item.  Will convert the MRenderItem to instanced rendering if not already done. The render item should already have it's other properties set (including shader and geometry).  A render item converted to instanced rendering will ignore its typical matrix from setMatrix().
        
        * renderItem (MRenderItem) - The render item to add a new instance to.
        * transform (MMatrix) - The transformation matrix of the new instance.
        """
    
        pass
    
    
    def furtherUpdateRequired(*args, **kwargs):
        """
        furtherUpdateRequired(frameContext) -> bool
        
        Returns True if further update is required. The default value return is False.
        
        This method is called by Maya following update() to allow the override to indicate whether further processing is required.
        
        If so, then requiresUpdate() and update() will be called again at a later time. In general this will occur when no active processing is occuring (when "idle").
        
        It is the responsibility of the plug-in to ensure that this method does not continuously request further updates as it may block the execution of other idle time events.
        
        * frameContext (MFrameContext) - Context information for the current frame.
        """
    
        pass
    
    
    def getInstancedSelectionPath(*args, **kwargs):
        """
        getInstancedSelectionPath(renderItem, intersection, dagPath) -> bool
        
        Returns True if a dag path was found for the instantiable render item.
        
        This method is called by Maya following selection to allow specifying the selection path for a single instantiable render item. It is identical to getSelectionPath() but includes MIntersection information to properly distinguish between instances when the viewport is in GPU acceleration mode.
        
        In GPU acceleration mode, the renderItem will be the one of the master instance and the value of intersection.instanceID() will match the value returned by addInstanceTransform(). In regular non GPU accelerated mode, the renderItem will be the one directly associated with the instance. If intersection.instanceID() is equal to -1, then the geometry was not GPU accelerated.
        
        * renderItem (MRenderItem) - Render item found inside the selection frustum, or master item in GPU accelerated mode.
        * intersection (MIntersection) - Extra information to help find out how the render item got selected.
        * dagPath [OUT] (MDagPath) - the MDagPath associated with the provided render item.
        """
    
        pass
    
    
    def getSelectionPath(*args, **kwargs):
        """
        getSelectionPath(renderItem, dagPath) -> bool
        
        Returns True if a dag path was found for the render item.
        
        This method is called by Maya following selection to allow specifying the selection path for a single render item. It will be called once for each MRenderItem submitted in MPxSubSceneOverride.update() that intersects the selection frustum. If none of the MRenderItem intersects, then this callback will remain silent.
        
        When selection filtering is active, or in case of single click selection it is possible that the item will not be in the final selection list.
        
        The default implementation will return the first path to the associated DAG object. Specialization is required to provide support for multiple instances of the DAG object.
        
        Note: If your SubScene override plugin supports instancing, then you should overload getInstancedSelectionPath() instead to get all the necessary information to be able to return a proper path.
        
        * renderItem (MRenderItem) - Render item found inside the selection frustum.
        * dagPath [OUT] (MDagPath) - the MDagPath associated with the provided render item.
        """
    
        pass
    
    
    def removeAllInstances(*args, **kwargs):
        """
        removeAllInstances(renderItem) -> self
        
        Remove all instances for a render item. This render item will remain set up for instancing and will render nothing until new instances are added.
        
        * renderItem (MRenderItem) - The render item to operate on.
        """
    
        pass
    
    
    def removeExtraInstanceData(*args, **kwargs):
        """
        removeExtraInstanceData(renderItem, parameterName) -> self
        
        Remove an entire extra instance data stream from the instanced render item.
        
        * renderItem (MRenderItem) - The render item to operate on.
        * parameterName (string) - The name of the parameter associated with the extra instance data stream.
        """
    
        pass
    
    
    def removeInstance(*args, **kwargs):
        """
        removeInstance(renderItem, instanceId) -> self
        
        Remove one instance of a render item.
        
        * renderItem (MRenderItem) - The render item to operate on.
        * instanceId (int) - The instance ID of the instance to remove. This must be a value returned by addInstanceTransform.
        """
    
        pass
    
    
    def requiresUpdate(*args, **kwargs):
        """
        requiresUpdate(container, frameContext) -> bool
        
        On each frame Maya will give each instantiated MPxSubSceneOverride object a chance to update its set of render items. Before beginning the update process for a specific override, Maya will first call this method to give the override a chance to indicate whether or not an update is necessary. If this method returns False, MPxSubSceneOverride.update() will not be called.
        
        The set of render items for this override must not be modified in this method.
        
        * container (MSubSceneContainer) - The container for this override
        * frameContext (MFrameContext) - Context information for the current frame
        
        Returns True if Maya should trigger the update process for this override
        """
    
        pass
    
    
    def setExtraInstanceData(*args, **kwargs):
        """
        setExtraInstanceData(renderItem, parameterName, data, instanceId=None) -> self
        
        Adds an extra stream of instanced data to an instanced render item. Once a render item has been instanced, additional per-instance data may be bound to a parameter on the shader for that item. Supported shader parameter types for instanced data include: float, float2, float3 and float4. Once a stream of instanced data is specified for a shader parameter, the original value of that parameter will be ignored in favor of the per-instance data specified in this method.
        
        If the render item has not been set up for instancing or if an invalid parameter was specified this method will fail. The size of the data array must be x*numberOfInstances where x is the size of the channel (1-4). If the size is wrong, the method will fail.
        
        More than one stream of extra instance data may be specified for an instanced render item. The number of streams will be limited by the number of texture co-ordinate channels available from the underlying graphics system (and note that the instanced matrix occupies four streams). If too many streams are used then a red error shader will be displayed instead of the expected shader.
        
        * renderItem (MRenderItem) - The render item to operate on.
        * parameterName (string) - The name of the parameter on the shader to fill with the instanced data.
        * data (MFloatArray) - The instanced data stream.
        * instanceId (int) - The instance ID of the instance to set the data for.
        """
    
        pass
    
    
    def setGeometryForRenderItem(*args, **kwargs):
        """
        setGeometryForRenderItem(renderItem, vertexBuffers, indexBuffer=None, objectBox=None) -> self
        
        Call this method to provide the geometry for a render item. Although the render item will add a reference to each buffer, ultimate ownership of the geometric data remains with the caller. This method may only be called on render items which have been generated by this override and it may only be called during update(). Buffers may be shared among multiple render items. This method will replace any geometry currently associated with the render item with the newly provided geometry.
        
        The bounding box parameter to this method is optional. If None, Maya will attempt to calculate the box automatically. Note that this may require a read-back of vertex data from the graphics card which can be a very slow operation. It is better to supply a correct bounding box whenever possible.
        
        It is the responsibility of the caller to ensure that the buffers provided fulfill the geometry requirements of the shader for the render item. If the requirements are not met, the render item will not draw. If there is no shader assigned to the render item, this method will fail.
        
        When a geometry is completely defined by its vertex buffers, like when drawing all points in a MGeometry.kPoints render item, it is possible to provide an empty MIndexBuffer or None for the indexBuffer parameter. The geometry will then be drawn using a non-indexed draw call like glDrawArrays() or ID3D11DeviceContext::Draw().
        
        * renderItem (MRenderItem) - The render item to provide geometry for.
        * vertexBuffers (MVertexBufferArray) - The vertex buffers for the geometry.
        * indexBuffer (MIndexBuffer) - The index buffer for the geometry, may be None.
        * objectBox (MBoundingBox) - Object-space bounding box, may be None.
        """
    
        pass
    
    
    def setInstanceTransformArray(*args, **kwargs):
        """
        setInstanceTransformArray(renderItem, matrixArray) -> self
        
        Sets the entire instance array for a render item.  Will convert the MRenderItem to instanced rendering if not already done.  Any pre-existing instances will be removed. The render item should already have it's other properties set (including shader and geometry). A render item converted to instanced rendering will ignore its typical matrix from setMatrix().
        This function is provided as a simpler alternative to addInstanceTransform() for when the ability to update or remove individual instances is not required. However additional instances may still be added via addInstanceTransform() and those may be individually updated or removed.
        
        * renderItem (MRenderItem) - The render item to set the instance matrix array for.
        * matrixArray (MMatrixArray) - The transformation matrix array for all the instances.
        """
    
        pass
    
    
    def supportedDrawAPIs(*args, **kwargs):
        """
        supportedDrawAPIs() -> DrawAPI
        
        Returns the draw API supported by this override.
        """
    
        pass
    
    
    def update(*args, **kwargs):
        """
        update(container, frameContext) -> self
        
        This method is called by Maya on each frame as long as the implementation of MPxSubSceneOverride.requiresUpdate() returns True. In this method, the MSubSceneContainer should be populated with the render items that are required to draw the associated DAG object. The render items will remain in the container until they are explicitly removed or the associated object is deleted. Render items in the container may also be modified at this time. 
        
        All render items in the container upon completion of this method will be processed for drawing. Any such items which pass all filtering tests for the active viewport will draw. At a minimum, render items must be enabled, have a valid shader and valid geometry in order to draw in Viewport 2.0. 
        
        It is the responsibility of this method to call MRenderer.setLightsAndShadowsDirty() to trigger recomputation of any shadow maps in the scene (if required). 
        
        * container (MSubSceneContainer) - The container for this override
        * frameContext (MFrameContext) - Context information for the current frame
        """
    
        pass
    
    
    def updateInstanceTransform(*args, **kwargs):
        """
        updateInstanceTransform(renderItem, instanceId, transform) -> self
        
        Update the instance transform matrix for one instance of a render item.
        
        * renderItem (MRenderItem) - The render item to operate on.
        * instanceId (int) - The instance ID of the instance to update. This must be a value returned by addInstanceTransform.
        * transform (MMatrix) - The new transformation matrix for the instance.
        """
    
        pass
    
    
    def updateSelectionGranularity(*args, **kwargs):
        """
        updateSelectionGranularity(path, selectionContext) -> self
        
        This method is called during the pre-filtering phase of the viewport 2.0 selection and is used to allow derived classes to modify the selection context of the given DAG object.
        
        This is useful to specify the selection level, which defines what can be selected on the object :
          MSelectionContext.kNone        Nothing can be selected
          MSelectionContext.kObject      Object can be selected as a whole
          MSelectionContext.kComponent   Parts of the object - such as vertex, edge or face - are selectable
        This is used to discard objects that are not selectable given the current selection mode (see MGlobal.selectionMode()).
        
        Implementation of this method here is empty, and default selection level is set to kObject.
        
         path (MDagPath) - The path to the instance to update the selection context for
         selectionContext [OUT] (MSelectionContext) - The selection context
        """
    
        pass
    
    
    def pointSnappingActive(*args, **kwargs):
        """
        pointSnappingActive() -> bool
        
        Returns True if selection has been launched to find snap points.
        To participate, you need to have at least one render item with point geometry
        and MSelectionMask.kSelectPointsForGravity set in MRenderItem.selectableMask().
        - The granularity must be set to MSelectionContext.kComponent in updateSelectionGranularity()
        - A component converter is not necessary in this scenario.
        - getSelectionPath() will not be called. All points present in the render item will be
        considered suitable locations for snapping.
        """
    
        pass
    
    
    __new__ = None


class MPxVertexBufferMutator(object):
    """
    Base class for user defined vertex buffer generators.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def modifyVertexStream(*args, **kwargs):
        """
        modifyVertexStream(object, vertexBuffer, targetIndexing) -> self
        
        This method gets called to allow the mutator to alter the data for a custom vertex stream.
        Use the requirements in the vertexBuffer to get the description of the stream.
        Use vertexBuffer.aquire() and vertexBuffer.commit() to fill the buffer.
        
        * object (MObject) - The object being evaluated.
        * vertexBuffer [IN/OUT] (MVertexBuffer) - The vertex buffer to alter.
        * targetIndexing (MComponentDataIndexing) - Vertex index mapping from targetIndexing.getComponentType() space to vertex buffer space.
        """
    
        pass
    
    
    __new__ = None


class MIndexBufferDescriptorList(object):
    """
    A list of MIndexBufferDescriptor objects.
    """
    
    
    
    def __getitem__(*args, **kwargs):
        """
        x.__getitem__(y) <==> x[y]
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __len__(*args, **kwargs):
        """
        x.__len__() <==> len(x)
        """
    
        pass
    
    
    def append(*args, **kwargs):
        """
        append(MIndexBufferDescriptor) -> bool
        
        Add a descriptor to the list. Creates and stores a copy which is owned by the list.
        """
    
        pass
    
    
    def clear(*args, **kwargs):
        """
        clear() -> self
        
        Clear the list.
        """
    
        pass
    
    
    def remove(*args, **kwargs):
        """
        remove(index) -> bool
        
        Remove a descriptor from the list and delete it.
        """
    
        pass
    
    
    __new__ = None


class MCameraOverride(object):
    """
    Camera override description. Provides information for specifying a camera override for a render operation.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    mCameraPath = None
    
    mFarClippingPlane = None
    
    mHiddenCameraList = None
    
    mNearClippingPlane = None
    
    mProjectionMatrix = None
    
    mUseFarClippingPlane = None
    
    mUseHiddenCameraList = None
    
    mUseNearClippingPlane = None
    
    mUseProjectionMatrix = None
    
    mUseViewMatrix = None
    
    mViewMatrix = None
    
    __new__ = None


class MPxPrimitiveGenerator(object):
    """
    Base class for user defined primitive generators.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def computeIndexCount(*args, **kwargs):
        """
        computeIndexCount(object, component) -> int
        
        This function is called to allow the primitive generator to provide the number of vertices it will use.
        
        * object (MObject) - The object being evaluated.
        * component (MObject) - The components to use.
        """
    
        pass
    
    
    def generateIndexing(*args, **kwargs):
        """
        generateIndexing(object, component, sourceIndexing, targetIndexing, indexBuffer) -> (int, int)
        
        This method gets called to allow the generator to fill in the data for a custom index stream.
        
        * object (MObject) - The object being evaluated.
        * component (MObject) - The components to use when building the index buffer. 
        * sourceIndexing (MComponentDataIndexingList) - Vertex index mapping in the declared MComponentDataIndexing::MComponentType space.
        * targetIndexing (MComponentDataIndexingList) - Vertex index mapping from targetIndexing.getComponentType() space to vertex buffer space.
        * indexBuffer [OUT] (MIndexBuffer) - The index buffer to fill.
        
        Returns the type of primitive of the generated indexing and the stride of the generated indexing, only valid when the returned primitive type is kPatch
        See MGeometry.primitiveString() description for a list of valid primitive types.
        """
    
        pass
    
    
    __new__ = None


class MRenderProfile(object):
    """
    The MRenderProfile class describes the rendering APIs and algorithms supported by a given rendering entity (e.g. a shading node, a renderer).
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addRenderer(*args, **kwargs):
        """
        addRenderer(renderer) -> selfaddRenderer(name, version) -> self
        
        Add an internal renderer to this profile:
        * renderer (int) - One of Maya's internal renderers:
          kMayaSoftware,
          kMayaOpenGL,
          kMayaD3D
        
        Or add a custom renderer to this profile:
        * name (string) - The name of the renderer,
        * version (float) = The version of the renderer or rendering API.
        The name and version specified must correspond to a renderer registered with Maya. Currently, only Maya's internal renderers (just named after the APIs they use: 'OpenGL', 'D3D', or 'Software') are supported. When registering support for Maya's internal renderers, it's simpler to use the other version of this method.
        """
    
        pass
    
    
    def hasRenderer(*args, **kwargs):
        """
        hasRenderer(renderer) -> boolhasRenderer(name, version) -> bool
        
        Check if a Maya renderer is listed in this profile:
        * renderer (int) - One of Maya's internal renderers, see addRenderer().
        
        Or check if a custom renderer is in this render profile:
        * name (string) - The name of the renderer,
        * version (float) = The version of the renderer or rendering API.
        see addRenderer()
        """
    
        pass
    
    
    def numberOfRenderers(*args, **kwargs):
        """
        numberOfRenderers() -> int
        
        Return the number of renderers in this profile.
        """
    
        pass
    
    
    __new__ = None
    
    
    kMayaD3D = 2
    
    
    kMayaOpenGL = 1
    
    
    kMayaSoftware = 0


class MDrawRegistry(object):
    """
    Access the registry associating node types with custom draw classes
    """
    
    
    
    def deregisterComponentConverter(*args, **kwargs):
        """
        deregisterComponentConverter(renderItemName) -> None
        
        Deregister an implementation of MPxComponentConverter.
        """
    
        pass
    
    
    def deregisterDrawOverrideCreator(*args, **kwargs):
        """
        deregisterDrawOverrideCreator(drawClassification, registrantId) -> None
        
        Deregister an implementation of MPxDrawOverride.
        """
    
        pass
    
    
    def deregisterGeometryOverrideCreator(*args, **kwargs):
        """
        deregisterGeometryOverrideCreator(drawClassification, registrantId) -> None
        
        Deregister an implementation of MPxGeometryOverride.
        """
    
        pass
    
    
    def deregisterIndexBufferMutator(*args, **kwargs):
        """
        deregisterIndexBufferMutator(primitiveType) -> None
        
        Deregister an implementation of MPxIndexBufferMutator.
        """
    
        pass
    
    
    def deregisterPrimitiveGenerator(*args, **kwargs):
        """
        deregisterPrimitiveGenerator(primitiveType) -> None
        
        Deregister an implementation of MPxPrimitiveGenerator.
        """
    
        pass
    
    
    def deregisterShaderOverrideCreator(*args, **kwargs):
        """
        deregisterShaderOverrideCreator(drawClassification, registrantId) -> None
        
        Deregister an implementation of MPxShaderOverride.
        """
    
        pass
    
    
    def deregisterShadingNodeOverrideCreator(*args, **kwargs):
        """
        deregisterShadingNodeOverrideCreator(drawClassification, registrantId) -> None
        
        Deregister an implementation of MPxShadingNodeOverride.
        """
    
        pass
    
    
    def deregisterSubSceneOverrideCreator(*args, **kwargs):
        """
        deregisterSubSceneOverrideCreator(drawClassification, registrantId) -> None
        
        Deregister an implementation of MPxSubSceneOverride.
        """
    
        pass
    
    
    def deregisterSurfaceShadingNodeOverrideCreator(*args, **kwargs):
        """
        deregisterSurfaceShadingNodeOverrideCreator(drawClassification, registrantId) -> None
        
        Deregister an implementation of MPxSurfaceShadingNodeOverride.
        """
    
        pass
    
    
    def deregisterVertexBufferGenerator(*args, **kwargs):
        """
        deregisterVertexBufferGenerator(bufferName) -> None
        
        Deregister an implementation of MPxVertexBufferGenerator.
        """
    
        pass
    
    
    def deregisterVertexBufferMutator(*args, **kwargs):
        """
        deregisterVertexBufferMutator(bufferName) -> None
        
        Deregister an implementation of MPxVertexBufferMutator.
        """
    
        pass
    
    
    def registerComponentConverter(*args, **kwargs):
        """
        registerComponentConverter(renderItemName, creator) -> None
        
        Register an implementation of MPxComponentConverter to use with render items that have the specified name.
        """
    
        pass
    
    
    def registerDrawOverrideCreator(*args, **kwargs):
        """
        registerDrawOverrideCreator(drawClassification, registrantId, creator) -> None
        
        Register an implementation of MPxDrawOverride to use with DAG objects that have the specified, draw-specific classification string.
        """
    
        pass
    
    
    def registerGeometryOverrideCreator(*args, **kwargs):
        """
        registerGeometryOverrideCreator(drawClassification, registrantId, creator) -> None
        
        Register an implementation of MPxGeometryOverride to use with nodes that have the specified, draw-specific classification string.
        """
    
        pass
    
    
    def registerIndexBufferMutator(*args, **kwargs):
        """
        registerIndexBufferMutator(primitiveType, creator) -> None
        
        Register an implementation of MPxIndexBufferMutator to generate custom primitive types for shapes.
        """
    
        pass
    
    
    def registerPrimitiveGenerator(*args, **kwargs):
        """
        registerPrimitiveGenerator(primitiveType, creator) -> None
        
        Register an implementation of MPxPrimitiveGenerator to generate custom primitive types for shapes.
        """
    
        pass
    
    
    def registerShaderOverrideCreator(*args, **kwargs):
        """
        registerShaderOverrideCreator(drawClassification, registrantId, creator) -> None
        
        Register an implementation of MPxShaderOverride to use with nodes that have the specified, draw-specific classification string.
        """
    
        pass
    
    
    def registerShadingNodeOverrideCreator(*args, **kwargs):
        """
        registerShadingNodeOverrideCreator(drawClassification, registrantId, creator) -> None
        
        Register an implementation of MPxShadingNodeOverride to use with nodes that have the specified, draw-specific classification string.
        """
    
        pass
    
    
    def registerSubSceneOverrideCreator(*args, **kwargs):
        """
        registerSubSceneOverrideCreator(drawClassification, registrantId, creator) -> None
        
        Register an implementation of MPxSubSceneOverride to use with DAG objects that have the specified, draw-specific classification string.
        """
    
        pass
    
    
    def registerSurfaceShadingNodeOverrideCreator(*args, **kwargs):
        """
        registerSurfaceShadingNodeOverrideCreator(drawClassification, registrantId, creator) -> None
        
        Register an implementation of MPxSurfaceShadingNodeOverride to use with surface shaders that have the specified, draw-specific classification string.
        """
    
        pass
    
    
    def registerVertexBufferGenerator(*args, **kwargs):
        """
        registerVertexBufferGenerator(bufferName, creator) -> None
        
        Register an implementation of MPxVertexBufferGenerator to provide custom vertex streams for shapes.
        """
    
        pass
    
    
    def registerVertexBufferMutator(*args, **kwargs):
        """
        registerVertexBufferMutator(bufferName, creator) -> None
        
        Register an implementation of MPxVertexBufferMutator to provide custom vertex streams for shapes.
        """
    
        pass


class MIndexBuffer(object):
    """
    Index buffer for use with MGeometry.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def acquire(*args, **kwargs):
        """
        acquire(size, writeOnly) -> long
        
        Get a pointer to memory for the buffer.
        
        * size (int) - The size of the buffer to acquire.
        * writeOnly (bool) - Specified if the returned memory should be uninitialized or filled with actual buffer content.
                             When the current buffer content is not needed, it is preferable to set the writeOnly flag to true for better performance.
        """
    
        pass
    
    
    def commit(*args, **kwargs):
        """
        commit(long) -> self
        
        Commit the data stored in the memory given by acquire() to the buffer.
        If this method is not called, the acquired buffer will not be used in drawing.
        The pointer must be the same pointer returned from acquire().
        """
    
        pass
    
    
    def dataType(*args, **kwargs):
        """
        dataType() -> int
        
        Get the data type of the buffer.
        See MGeometry.dataTypeString() for a list of valid data types.
        """
    
        pass
    
    
    def hasCustomResourceHandle(*args, **kwargs):
        """
        hasCustomResourceHandle() -> bool
        
        Returns true if this index buffer is using a custom resource handle set
        by the plugin using MIndexBuffer.setResourceHandle(long, int).
        """
    
        pass
    
    
    def lockResourceHandle(*args, **kwargs):
        """
        lockResourceHandle() -> self
        
        Lock the resource handle. The pointer returned from resourceHandle() is
        guaranteed to exist between lockResourceHandle() and unlockResourceHandle().
        
        MIndexBuffer may store data in system memory, GPU memory or both. Direct
        access to the GPU representation of the data is possible through the
        buffer's resourceHandle(). If the GPU representation of the data is to be
        directly modified using an external graphics or compute API, then
        lockResourceHandle() must be called on the MIndexBuffer once, before any
        modifications to the buffer are made.
        
        While a resource handle is locked, any external modifications to the GPU
        buffer will be recognized by Maya.
        
        While a resource handle is locked, consolidated world will take longer to
        consolidate the corresponding object. After unlocking a resource handle,
        consolidated world will take longer to consolidate the corresponding object
        one more time, the first time the unlocked resource handle is consolidated.
        
        Calling lockResourceHandle() and unlockResourceHandle() on a custom resource
        handle has no effect.
        
        Reallocating or deleting the GPU representation of the data between
        lockResourceHandle() and unlockResourceHandle() will result in undefined
        behavior. acquire(), commit() and update() may reallocate the GPU representation.
        unload() may delete the GPU representation.
        
        map() and unmap() will work if they are called between lockResourceHandle()
        and unlockResourceHandle(). They operate on the GPU representation.
        """
    
        pass
    
    
    def map(*args, **kwargs):
        """
        map() -> long
        
        Get a read-only pointer to the existing content of the buffer.
        Writing new content in this memory block is not supported and can lead to unexpected behavior.
        """
    
        pass
    
    
    def resourceHandle(*args, **kwargs):
        """
        resourceHandle() -> long
        
        Returns a long containing a C++ 'float' pointer which points to the graphics device dependent handle to the vertex indexing data.
        """
    
        pass
    
    
    def setResourceHandle(*args, **kwargs):
        """
        setResourceHandle(long, int) -> selfset the graphics-device-dependent hardware buffer resource handle.
        """
    
        pass
    
    
    def size(*args, **kwargs):
        """
        size() -> int
        
        Get the size of the buffer in units of dataType(). Returns 0 if unallocated.
        """
    
        pass
    
    
    def unload(*args, **kwargs):
        """
        unload() -> self
        
        If the buffer is resident in GPU memory, calling this method will move it to system memory and free the GPU memory.
        """
    
        pass
    
    
    def unlockResourceHandle(*args, **kwargs):
        """
        unlockResourceHandle() -> self
        
        Unlock the resource handle. The pointer returned from resourceHandle is not
        guaranteed to exist any more.
        See lockResourceHandle() for more details.
        """
    
        pass
    
    
    def unmap(*args, **kwargs):
        """
        unmap() -> self
        
        Release the data exposed by map(). If this method is not called, the buffer will not be recycled.
        """
    
        pass
    
    
    def update(*args, **kwargs):
        """
        update(buffer, destOffset, numIndices, truncateIfSmaller) -> self
        
        Set a portion (or all) of the contents of the MIndexBuffer using the data in the provided software buffer.
        The internal hardware buffer will be allocated or reallocated to fit if required, according to the vertex size from the descriptor.
        
        * buffer (long) - The input data buffer, starting with the first vertex to copy.
        * destOffset (int) - The offset (in indices) from the beginning of the buffer to start writing to.
        * numIndices (int) - The number of indices to copy.
        * truncateIfSmaller (bool) - If true and offset+numVerts is less than the pre-existing size of the buffer,
                                     then the buffer contents will be truncated to the new size. Truncating the buffer size
                                     will not cause a reallocation and will not lose data before the destOffset.
        """
    
        pass
    
    
    __new__ = None


class MSubSceneContainerIterator(object):
    """
    Iterator over render items of MSubSceneContainer object.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def destroy(*args, **kwargs):
        """
        destroy() -> self
        
        Call this method to delete the iterator. After calling, the iterator will be invalid.
        Users of MSubSceneContainer iterators are responsible for deleting the iterators after use.
        """
    
        pass
    
    
    def next(*args, **kwargs):
        """
        next() -> MRenderItem
        
        Advance the iterator to the next render item in the associated MSubSceneContainer and return it.
        
        Returns the next render item in the container or None if no more items.
        """
    
        pass
    
    
    def reset(*args, **kwargs):
        """
        reset() -> self
        
        Reset the iterator to the beginning of the associated MSubSceneContainer.
        The next call to the next() method will return the first render item in the container.
        """
    
        pass
    
    
    __new__ = None


class MVaryingParameter(object):
    """
    The MVaryingParameter class provides a high-level interface to hardware shader varying parameters. By defining your shader's varying data through this class, you allow Maya to handle the attributes, editing, serialisation, requirements setup, and cache management for you in a standard way that ensure you'll be able to leverage future performance and functionality improvements.
    
    To remove any ambiguity between constructors, the mandatory parameters of the third one have been swizzled:
    MVaryingParameter()
    MVaryingParameter(
           name,
           type,
           minDimension=1,
           maxDimension=1,
           semantic=kNoSemantic,
           invertTexCoords=False,
           semanticName=None)
    MVaryingParameter(
           dimension,
           minDimension,
           maxDimension,
           name,
           type,
           semantic=kNoSemantic,
           destinationSet=None,
           invertTexCoords=False,
           semanticName=None)
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addElement(*args, **kwargs):
        """
        addElement(child) -> self
        
        Add a child element to this parameter.
        This operation is only valid for parameters of type kStructure.
        
        * child (MVaryingParameter) - the parameter to add to the structure.
        """
    
        pass
    
    
    def copy(*args, **kwargs):
        """
        copy(source) -> self
        
        Copy data from source parameter.
        
        * source (MVaryingParameter) - The source parameter to copy from
        """
    
        pass
    
    
    def destinationSetName(*args, **kwargs):
        """
        destinationSetName() -> string
        
        Get the destination Set of this parameter.
        """
    
        pass
    
    
    def dimension(*args, **kwargs):
        """
        dimension() -> int
        
        Get the dimension of this parameter.
        """
    
        pass
    
    
    def elementSize(*args, **kwargs):
        """
        elementSize() -> int
        
        Get the size in bytes of one element of this parameter.
        """
    
        pass
    
    
    def getElement(*args, **kwargs):
        """
        getElement(index) -> MVaryingParameter
        
        Get an element within a structure.
        This operation is only valid for parameters of type kStructure.
        
        * index (int) - The index of the structure element to return.
        """
    
        pass
    
    
    def maximumStride(*args, **kwargs):
        """
        maximumStride() -> int
        
        Get the maximum stride of this parameter in bytes.
        For parameter that accept a range of element counts, this corresponds to the maximum number of elements the parameter supports.
        """
    
        pass
    
    
    def name(*args, **kwargs):
        """
        name() -> string
        
        Get the name of this parameter.
        """
    
        pass
    
    
    def numElements(*args, **kwargs):
        """
        numElements() -> int
        
        Get the number of elements in this structure.
        This operation is only valid for parameters of type kStructure.
        """
    
        pass
    
    
    def removeElements(*args, **kwargs):
        """
        removeElements() -> self
        
        Remove all child elements from a structure.
        This operation is only valid for parameters of type kStructure.
        """
    
        pass
    
    
    def semantic(*args, **kwargs):
        """
        semantic() -> int
        
        Get the semantic of this parameter.
        
        Available values:
          kNoSemantic,
          kPosition,
          kNormal,
          kTexCoord,
          kColor,
          kWeight,
          kTangent,
          kBinormal
        """
    
        pass
    
    
    def semanticName(*args, **kwargs):
        """
        semanticName() -> string
        
        Get the semantic name assigned to this parameter.
        The semanticName is used to identify a custom vertex stream request in order to fill the stream with the appropriate data requested by a shader override.
        """
    
        pass
    
    
    def setSource(*args, **kwargs):
        """
        setSource(semantic, name) -> self
        
        While the source of geometry parameters is usually configured by the artist through Maya's user interface, this method allows you to programatically set the source of a geometry parameter, including both the data type (e.g. position, normal, etc) and an optional set name (e.g. UV set 'map1'). This is useful for implementing custom default values or shader operations.
        
        * type (int) - the type of data to populate this parameter with (see semantic())
        * name (string) - the specific data set to use for parameter types which support data sets, such as UV and color.
        """
    
        pass
    
    
    def sourceSemantic(*args, **kwargs):
        """
        sourceSemantic() -> int
        
        Get the type of data (e.g. position, normal, uv) currently populating this parameter.
        This method will only return a useful value when called on leaf-level parameters (e.g. structures do not have sources, only the elements of a structure have sources).
        See semantic() for the list of values.
        """
    
        pass
    
    
    def sourceSetName(*args, **kwargs):
        """
        sourceSetName() -> string
        
        If the current data type supports data sets (e.g. uv sets, color sets), get the name of the data set populating this parameter. This method will only return a useful value when called on leaf-level parameters (e.g. structures do not have sources, only the elements of a structure have sources).
        """
    
        pass
    
    
    def type(*args, **kwargs):
        """
        type() -> int
        
        Get the type of this parameter.
        
        Available values:
          kInvalidParameter,
          kStructure,
          kFloat,
          kDouble,
          kChar,
          kUnsignedChar,
          kInt16,
          kUnsignedInt16,
          kInt32,
          kUnsignedInt32
        """
    
        pass
    
    
    def updateId(*args, **kwargs):
        """
        updateId() -> int
        
        Get the update id.
        The update id is increased every time the parameter sources or sourceSet are changed. A plugin can compare the update id value between subsequent calls to this function to know if the source has changed since the last call.
        """
    
        pass
    
    
    __new__ = None
    
    
    kBinormal = 8
    
    
    kChar = 3
    
    
    kColor = 4
    
    
    kDouble = 2
    
    
    kFloat = 1
    
    
    kInt16 = 5
    
    
    kInt32 = 7
    
    
    kInvalidParameter = -1
    
    
    kNoSemantic = 0
    
    
    kNormal = 2
    
    
    kPosition = 1
    
    
    kStructure = 0
    
    
    kTangent = 7
    
    
    kTexCoord = 3
    
    
    kUnsignedChar = 4
    
    
    kUnsignedInt16 = 6
    
    
    kUnsignedInt32 = 8
    
    
    kWeight = 5


class MInitContext(object):
    """
    Initialization context used by advanced initalization method.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    dagPath = None
    
    shader = None
    
    __new__ = None


class MSwatchRenderBase(object):
    """
    Swatch Render Base class.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def cancelParallelRendering(*args, **kwargs):
        """
        cancelParallelRendering() -> self
        
        Method to cancel the parallel rendering.
        The derived classes should provide the implementation accordingly if required.
        """
    
        pass
    
    
    def doIteration(*args, **kwargs):
        """
        doIteration() -> bool
        
        Method called from the MSwatchRenderRegister for generation of swatch image. The doIteration function is called repeatedly (during idle events) until it returns true. Using this swatch image can be generated in stages.
        
        This method should be overridden in derived classes which can compute the swatches in several steps.
        
        Returns False as long as the swatch computation is not completed.
        """
    
        pass
    
    
    def finishParallelRender(*args, **kwargs):
        """
        finishParallelRender() -> self
        
        Method to update the swatch image when the parallel rendering is finished.
        If swatch is rendered parallel, this method must be called after parallel rendering finished.
        """
    
        pass
    
    
    def image(*args, **kwargs):
        """
        image() -> MImage
        
        This method returns the render swatch as an image.
        """
    
        pass
    
    
    def node(*args, **kwargs):
        """
        node() -> MObject
        
        This method returns the node that is used to compute the swatch.
        """
    
        pass
    
    
    def renderParallel(*args, **kwargs):
        """
        renderParallel() -> bool
        
        Method indicates if the swatch is rendered parallel.
        Default is False.
        """
    
        pass
    
    
    def resolution(*args, **kwargs):
        """
        resolution() -> int
        
        This method returns the expected resolution of the swatch.
        """
    
        pass
    
    
    def swatchNode(*args, **kwargs):
        """
        swatchNode() -> MObject
        
        This method returns the node for which the swatch is required to be generated.
        """
    
        pass
    
    
    def cancelCurrentSwatchRender(*args, **kwargs):
        """
        cancelCurrentSwatchRender() -> None
        
        The method cancels the swatch which is being rendered in parallel, and push the swatch render item back to the render queue after. 
        
        The render plugins should make sure that MSwatchRenderBase.cancelParallelRendering() is implemented acoordingly.
        """
    
        pass
    
    
    renderQuality = None
    
    __new__ = None


class MRenderTargetDescription(object):
    """
    Class which provides a description of a hardware render target.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def allowsUnorderedAccess(*args, **kwargs):
        """
        allowsUnorderedAccess() -> bool
        
        Query whether unordered access is supported.
        """
    
        pass
    
    
    def arraySliceCount(*args, **kwargs):
        """
        arraySliceCount() -> int
        
        Query the number of array slices defined by the description.
        """
    
        pass
    
    
    def compatibleWithDescription(*args, **kwargs):
        """
        compatibleWithDescription(MRenderTargetDescription) -> bool
        
        Determine if another target with a given description is 'compatible' with a target using this description.
        """
    
        pass
    
    
    def height(*args, **kwargs):
        """
        height() -> int
        
        Query the height of a 2D render target slice.
        """
    
        pass
    
    
    def isCubeMap(*args, **kwargs):
        """
        isCubeMap() -> bool
        
        Query whether this is a cube map target.
        """
    
        pass
    
    
    def multiSampleCount(*args, **kwargs):
        """
        multiSampleCount() -> int
        
        Query the multi-sample count defined by the description.
        """
    
        pass
    
    
    def name(*args, **kwargs):
        """
        name() -> string
        
        Query the name identifier for the target description.
        """
    
        pass
    
    
    def rasterFormat(*args, **kwargs):
        """
        rasterFormat() -> int
        
        Query the raster format defined by the description.
        """
    
        pass
    
    
    def setAllowsUnorderedAccess(*args, **kwargs):
        """
        setAllowsUnorderedAccess(bool) -> self
        
        Set the flag for unordered data access for the target.
        """
    
        pass
    
    
    def setArraySliceCount(*args, **kwargs):
        """
        setArraySliceCount(int) -> self
        
        Set array slice count of the target.
        """
    
        pass
    
    
    def setHeight(*args, **kwargs):
        """
        setHeight(int) -> self
        
        Set height of the target.
        """
    
        pass
    
    
    def setIsCubeMap(*args, **kwargs):
        """
        setIsCubeMap(bool) -> self
        
        Set cube map flag for the target.
        """
    
        pass
    
    
    def setMultiSampleCount(*args, **kwargs):
        """
        setMultiSampleCount(int) -> self
        
        Set multisample count of the target.
        """
    
        pass
    
    
    def setName(*args, **kwargs):
        """
        setName(string) -> self
        
        Set name of the target.
        """
    
        pass
    
    
    def setRasterFormat(*args, **kwargs):
        """
        setRasterFormat(int) -> self
        
        Set the raster format of the target.
        """
    
        pass
    
    
    def setWidth(*args, **kwargs):
        """
        setWidth(int) -> self
        
        Set width of the target.
        """
    
        pass
    
    
    def width(*args, **kwargs):
        """
        width() -> int
        
        Query the width of a 2D render target slice.
        """
    
        pass
    
    
    __new__ = None


class MTargetBlendDesc(object):
    """
    Descriptor for a blend state for a single render target.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def setDefaults(*args, **kwargs):
        """
        setDefaults() -> self
        
        Set all values for the target blend state to their default values.
        """
    
        pass
    
    
    alphaBlendOperation = None
    
    alphaDestinationBlend = None
    
    alphaSourceBlend = None
    
    blendEnable = None
    
    blendOperation = None
    
    destinationBlend = None
    
    sourceBlend = None
    
    targetWriteMask = None
    
    __new__ = None


class MInitFeedback(object):
    """
    Data to pass back to Maya after initialization.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    customData = None
    
    __new__ = None


class MRenderOperation(object):
    """
    Class which defines a rendering operation.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def enableSRGBWrite(*args, **kwargs):
        """
        enableSRGBWrite() -> bool
        
        Return whether to enable GPU based gamma correction during pixel writes.
        """
    
        pass
    
    
    def name(*args, **kwargs):
        """
        name() -> string
        
        Returns the name of the render operator.
        """
    
        pass
    
    
    def operationType(*args, **kwargs):
        """
        operationType() -> int
        
        Returns the type of a render operator.
        """
    
        pass
    
    
    def targetOverrideList(*args, **kwargs):
        """
        targetOverrideList() -> list of MRenderTarget
        
        Return a list of render target which will be used as the target overrides for the operation.
        """
    
        pass
    
    
    def viewportRectangleOverride(*args, **kwargs):
        """
        viewportRectangleOverride() -> MFloatPoint
        
        Query for a viewport rectangle override.
        """
    
        pass
    
    
    __new__ = None
    
    
    kClear = 0
    
    
    kHUDRender = 4
    
    
    kPresentTarget = 5
    
    
    kQuadRender = 2
    
    
    kSceneRender = 1
    
    
    kUserDefined = 3


class MGeometryIndexMapping(object):
    """
    A mapping of geometry index.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def component(*args, **kwargs):
        """
        component(int) -> MObject
        
        Get the component of a geometry.
        """
    
        pass
    
    
    def dagPath(*args, **kwargs):
        """
        dagPath(int) -> MDagPath
        
        Get the MDagPath of a geometry.
        """
    
        pass
    
    
    def geometryCount(*args, **kwargs):
        """
        geometryCount() -> int
        
        Get the number of geometry described by the mapping.
        """
    
        pass
    
    
    def indexLength(*args, **kwargs):
        """
        indexLength(int) -> int
        
        Get the index length of a geometry.
        The index length represents the length of the geometry index data in the index buffer of the consolidated render item.
        """
    
        pass
    
    
    def indexStart(*args, **kwargs):
        """
        indexStart(int) -> int
        
        Get the index start of a geometry.
        The index start represents the offset of the geometry index data in the index buffer of the consolidated render item.
        """
    
        pass
    
    
    __new__ = None


class MRenderParameters(object):
    """
    Base class for render operation functionsets.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def getParameter(*args, **kwargs):
        """
        getParameter(parameterName, bool) -> self
        getParameter(parameterName, int) -> self
        getParameter(parameterName, float) -> self
        getParameter(parameterName, list of float) -> self
        getParameter(parameterName, MFloatVector) -> self
        getParameter(parameterName, MMatrix) -> self
        getParameter(parameterName, MFloatMatrix) -> self
        getParameter(parameterName, MTextureAssignment) -> self
        getParameter(parameterName, MRenderTargetAssignment) -> self
        getParameter(parameterName, MSamplerStateDesc) -> self
        
        Get the value of the named parameter.
        """
    
        pass
    
    
    def isArrayParameter(*args, **kwargs):
        """
        isArrayParameter(string) -> bool
        
        Determine whether the named parameter is an array.
        """
    
        pass
    
    
    def parameterList(*args, **kwargs):
        """
        parameterList() -> list of string
        
        Get the names of all parameters that are settable on this shader instance.
        """
    
        pass
    
    
    def parameterType(*args, **kwargs):
        """
        parameterType(string) -> int
        
        Get the type of the named parameter, returns kInvalid if parameter is not found.
        """
    
        pass
    
    
    def semantic(*args, **kwargs):
        """
        semantic(string) -> string
        
        Return the semantic for a named parameter.
        """
    
        pass
    
    
    def setArrayParameter(*args, **kwargs):
        """
        setArrayParameter(parameterName, sequence of bool, int) -> self
        setArrayParameter(parameterName, sequence of int, int) -> self
        setArrayParameter(parameterName, sequence of float, int) -> self
        setArrayParameter(parameterName, sequence of MMatrix, int) -> self
        
        Set the value of a named array parameter.
        """
    
        pass
    
    
    def setParameter(*args, **kwargs):
        """
        setParameter(parameterName, bool) -> self
        setParameter(parameterName, int) -> self
        setParameter(parameterName, float) -> self
        setParameter(parameterName, list of float) -> self
        setParameter(parameterName, MFloatVector) -> self
        setParameter(parameterName, MMatrix) -> self
        setParameter(parameterName, MFloatMatrix) -> self
        setParameter(parameterName, MTextureAssignment) -> self
        setParameter(parameterName, MRenderTargetAssignment) -> self
        setParameter(parameterName, MSamplerState) -> self
        
        Set the value of the named parameter.
        """
    
        pass
    
    
    __new__ = None


class MFragmentManager(object):
    """
    Provides facilities for managing fragments for use with Viewport 2.0.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addFragmentGraphFromBuffer(*args, **kwargs):
        """
        addFragmentGraphFromBuffer(buffer) -> string
        
        Add a new fragment graph to the manager.
        The fragment graph is defined as XML stored in a string buffer.Returns name of the registered fragment graph, or empty string on failure.
        
        - buffer (string) - String containing an XML description of the fragment graph.
        """
    
        pass
    
    
    def addFragmentGraphFromFile(*args, **kwargs):
        """
        addFragmentGraphFromFile(fileName) -> string
        
        Add a new fragment graph to the manager.
        The fragment graph is defined as XML stored in the given file.Returns name of the registered fragment graph, or empty string on failure.
        
        - fileName (string) - The name of the file containing the fragment graph description.
        """
    
        pass
    
    
    def addFragmentPath(*args, **kwargs):
        """
        addFragmentPath(path) -> bool
        
        Add a path to the list of fragment search paths used when parsing the file path for any
        methods which add fragments to the manager from files on disk.
        """
    
        pass
    
    
    def addShadeFragmentFromBuffer(*args, **kwargs):
        """
        addShadeFragmentFromBuffer(buffer, hidden) -> string
        
        Add a new fragment to the manager.
        The fragment is defined as XML stored in a string buffer.
        Returns name of the registered fragment, or empty string on failure.
        
        - buffer (string) - String containing an XML description of the fragment.
        - hidden (bool) - If True, this fragment will not appear in the list returned by fragmentList()
                          and it will not be possible to query the XML for it using getFragmentXML().
        """
    
        pass
    
    
    def addShadeFragmentFromFile(*args, **kwargs):
        """
        addShadeFragmentFromFile(fileName, hidden) -> string
        
        Add a new fragment to the manager.
        The fragment is defined as XML stored in the given file.
        Returns name of the registered fragment, or empty string on failure.
        
        - fileName (string) - The name of the file containing the fragment description.
        - hidden (bool) - If True, this fragment will not appear in the list returned by fragmentList()
                          and it will not be possible to query the XML for it using getFragmentXML().
        """
    
        pass
    
    
    def fragmentList(*args, **kwargs):
        """
        fragmentList() -> list of string
        
        Returns a list of the names of all registered fragments and fragment graphs.
        """
    
        pass
    
    
    def getEffectOutputDirectory(*args, **kwargs):
        """
        getEffectOutputDirectory() -> string
        
        Get the directory to be used for effect file output.
        """
    
        pass
    
    
    def getFragmentXML(*args, **kwargs):
        """
        getFragmentXML(fragmentName) -> string
        getFragmentXML(shadingNode, includeUpstreamNodes=False, objectContext=None) -> string
        
        Get the XML representation of the named fragment or fragment graph.
        Return None if failed
        - fragmentName (string) - The name of the fragment to get the XML for.
        
        Get XML code for the fragment graph Maya would use to represent the given shading node in Viewport 2.0.
        Return None if failed
        - shadingNode (MObject) - The node to get the XML code for.
        - includeUpstreamNodes (bool) - Return the XML for the entire fragment graph rooted at the given shading node if True.
        - objectContext (MDagPath) - Optional path to an instance that is associated with the shading node to provide object context.
        """
    
        pass
    
    
    def getIntermediateGraphOutputDirectory(*args, **kwargs):
        """
        getIntermediateGraphOutputDirectory() -> string
        
        Get the directory to be used for intermediate fragment graph output.
        """
    
        pass
    
    
    def hasFragment(*args, **kwargs):
        """
        hasFragment(string) -> bool
        
        Returns True if a fragment of the given name has been registered with the fragment manager.
        """
    
        pass
    
    
    def removeFragment(*args, **kwargs):
        """
        removeFragment(fragmentName) -> bool
        
        Remove a named fragment or fragment graph from the fragment manager. This
        can be used to remove registered fragments on plug-in unload.
        
        Any fragment may be removed including those defined by Maya. In this way
        users may replace default Maya fragments with custom fragments. When
        replacing an existing Maya fragment it is important to maintain the same
        fragment interface (i.e. input and output parameters) otherwise Maya's
        behavior will be undefined. Maya's behavior will also be undefined if a
        default Maya fragment is removed without replacing it.
        
        Returns True if the fragment was successfuly removed from the fragment manager.
        """
    
        pass
    
    
    def setEffectOutputDirectory(*args, **kwargs):
        """
        setEffectOutputDirectory(string) -> self
        
        Set the path to use for dumping final effect files.
        """
    
        pass
    
    
    def setIntermediateGraphOutputDirectory(*args, **kwargs):
        """
        setIntermediateGraphOutputDirectory(string) -> self
        
        Set the path to use for dumping intermediate fragment graph XML files.
        """
    
        pass
    
    
    __new__ = None


class MFrameContext(object):
    """
    This class contains some global information for the current render frame.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def classificationExclusions(*args, **kwargs):
        """
        classificationExclusions() -> [classification strings]
        
        Get a list of drawdb strings for object which are excluded from display
        """
    
        pass
    
    
    def getBackgroundParameters(*args, **kwargs):
        """
        getBackgroundParameters() -> [displayGradient, clearColorFlag, clearDepthFlag, clearStencilFlag, clearColor1, clearColor2, clearDepthValue, clearStencilValue]
        
        Get parameters related to how the background is cleared
        """
    
        pass
    
    
    def getCurrentCameraPath(*args, **kwargs):
        """
        getCurrentCameraPath() -> MDagPath
        
        Get the path to the camera being used to render the current frame.
        """
    
        pass
    
    
    def getCurrentColorRenderTarget(*args, **kwargs):
        """
        getCurrentColorRenderTarget() -> MRenderTarget
        
        Get current color render target.
        Calling code is responsible for invoking MRenderTargetManager::releaseRenderTarget() to release the reference to the target after use.
        """
    
        pass
    
    
    def getCurrentDepthRenderTarget(*args, **kwargs):
        """
        getCurrentDepthRenderTarget() -> MRenderTarget
        
        Get current depth render target.
        Calling code is responsible for invoking MRenderTargetManager::releaseRenderTarget() to release the reference to the target after use.
        """
    
        pass
    
    
    def getDOFParameters(*args, **kwargs):
        """
        getDOFParameters() -> [enabled, focalDistance, alpha]
        
        Get the parameters generated by Maya for the circle-of-confusion depth shader used
        for a pass used when computing depth of field.
        
        
        This pass is indicated by the pass semantic MPassContext::kDOFPassSemantic.
        The shader fragment used is called cocDepthSurface.
        The XML wrapper can be queried from MFragmentManager or using the 'ogs -xml maya_CocDepthSurface' command.
        """
    
        pass
    
    
    def getDisplayStyle(*args, **kwargs):
        """
        getDisplayStyle() -> int
        
        The DisplayStyle enums can be use to test the bit field for the enabling of any
        of the listed display modes. For example to test for wireframe on shaded the test
        would be test against the bit for kGourandShaded or kFlatShaded as well as testing
        against the bit for kWireframe.
        
          MFrameContext.kGouraudShaded        Shaded display.
          MFrameContext.kWireFrame            Wire frame display.
          MFrameContext.kBoundingBox          Bounding box display.
          MFrameContext.kTextured             Textured display.
          MFrameContext.kDefaultMaterial      Default material display.
          MFrameContext.kXrayJoint            X-ray joint display.
          MFrameContext.kXray                 X-ray display.
          MFrameContext.kTwoSidedLighting     Two-sided lighting enabled.
          MFrameContext.kFlatShaded              Flat shading display.
          MFrameContext.kShadeActiveOnly      Shade active object only.
          MFrameContext.kXrayActiveComponents X-ray active components.
          MFrameContext.kBackfaceCulling                 Backface culling enabled.
          MFrameContext.kSmoothWireframe             Smooth wireframe enabled.
        """
    
        pass
    
    
    def getEnvironmentParameters(*args, **kwargs):
        """
        getEnvironmentParameters() -> [bool, string]
        
        Get parameters for currently used environment. Note that this information is set
        per viewport and so might change between draw calls if multiple viewports are
        displayed at the same time.
        Return the destination (type and name) that the renderer is drawing to.
        """
    
        pass
    
    
    def getGlobalLineWidth(*args, **kwargs):
        """
        getGlobalLineWidth() -> float
        
        Get global line width.
        """
    
        pass
    
    
    def getHwFogParameters(*args, **kwargs):
        """
        getHwFogParameters() -> [enabled, mode, start, end, density, color]
        
        Get all the hardware fog parameters.
        
        Hardware fog parameters include:
        
        - hardware fog enabled
        - hardware fog mode: Linear, Exponential, Exponential squared.
          The possible values are:
             MFrameContext::kFogLinear : Linear fog
             MFrameContext::kFogExp : Exponential fog
             MFrameContext::kFogExp2 : Exponential squared fog
        - hardware fog start: The near distance used in the linear fog.
        - hardware fog end: The far distance used in the linear fog.
        - hardware fog density: The density of the exponential fog.
        - hardware fog color: (r, g, b, a).
        """
    
        pass
    
    
    def getLightLimit(*args, **kwargs):
        """
        getLightLimit() -> int
        
        Get the current light limit.
        """
    
        pass
    
    
    def getLightingMode(*args, **kwargs):
        """
        getLightingMode() -> int
        
        Get the current light mode.
        
          MFrameContext.kNoLighting           Use no light
          MFrameContext.kAmbientLight      Use global ambient light
          MFrameContext.kLightDefault      Use default light
          MFrameContext.kSelectedLights    Use lights which are selected
          MFrameContext.kSceneLights       Use all lights in the scene
          MFrameContext.kCustomLights      Use a custom set of lights which are not part of the scene. Currently this applies for use in the Hypershade Material Viewer panel
        """
    
        pass
    
    
    def getMatrix(*args, **kwargs):
        """
        getMatrix(int) -> MMatrix
        
        Get a matrix value of a certain type.
        Note that not all types are available for querying in MFrameContext.
        Return None if matrix type not available from MFrameContext.
        For a list of matrix type, see MDrawContext.semanticToMatrixType() description.
        """
    
        pass
    
    
    def getPostEffectEnabled(*args, **kwargs):
        """
        getPostEffectEnabled(int) -> bool
        
        Returns if a given post effect is currently enabled.
        
          MFrameContext.kAmbientOcclusion    Screen-space ambient occlusion
          MFrameContext.kMotionBlur          2D Motion blur
          MFrameContext.kGammaCorrection     Gamma correction
          MFrameContext.kDepthOfField        Depth of field
          MFrameContext.kAntiAliasing        Hardware multi-sampling
        """
    
        pass
    
    
    def getRenderOverrideInformation(*args, **kwargs):
        """
        getRenderOverrideInformation() -> [overrideName]
        
        Get information about any render override
        """
    
        pass
    
    
    def getTransparencyAlgorithm(*args, **kwargs):
        """
        getTransparencyAlgorithm() -> int
        
        Get the current transparency algoritm.
        
          MFrameContext.kUnsorted            Unsorted transparent object drawing
          MFrameContext.kObjectSorting       Object sorting of transparent objects
          MFrameContext.kWeightedAverage     Weight average transparency
          MFrameContext.kDepthPeeling        Depth-peel transparency
        """
    
        pass
    
    
    def getTuple(*args, **kwargs):
        """
        getTuple(int) -> MDoubleArray
        
        Get a tuple (vector, position or single) value of a certain type.
        Note that not all types are available for querying in MFrameContext.
        Return None if unknown tuple type.
        """
    
        pass
    
    
    def getViewportDimensions(*args, **kwargs):
        """
        getViewportDimensions() -> [originX, originY, width, height]
        
        Get the viewport dimensions. The origin is the upper left corner of the viewport.
        """
    
        pass
    
    
    def objectTypeExclusions(*args, **kwargs):
        """
        objectTypeExclusions() -> long
        
        Get the object type exclusions as a bitfield.
                The bitfield can be tested using the bits defined by class statics starting with kExclude.
        """
    
        pass
    
    
    def renderingDestination(*args, **kwargs):
        """
        renderingDestination() -> [int, destinationName]
        
        Return the destination (type and name) that the renderer is drawing to.
        
          MFrameContext.k3dViewport    Rendering to an interactive 3d viewport
          MFrameContext.k2dViewport    Rendering to an interactive 2d viewport such as the render view
          MFrameContext.kImage         Rendering to an image
        """
    
        pass
    
    
    def inUserInteraction(*args, **kwargs):
        """
        inUserInteraction() -> bool
        
        Returns True during any interactive refresh, as when user is interacting with the scene
        in any way including camera changes, object or component TRS changes, etc.
        """
    
        pass
    
    
    def semanticToMatrixType(*args, **kwargs):
        """
        semanticToMatrixType(string) -> int
        
        Given a semantic name return the corresponding matrix enumeration that can be used to retrieve a matrix value via the getMatrix() method.
        
          MFrameContext.kWorldMtx                        Object to world matrix
          MFrameContext.kWorldTransposeMtx               Object to world matrix transpose
          MFrameContext.kWorldInverseMtx                 Object to world matrix inverse
          MFrameContext.kWorldTranspInverseMtx           Object to world matrix transpose inverse (adjoint)
          MFrameContext.kViewMtx                         World to view matrix
          MFrameContext.kViewTransposeMtx                World to view matrix tranpose
          MFrameContext.kViewInverseMtx                  World to view matrix inverse
          MFrameContext.kViewTranspInverseMtx            World to view matrix transpose inverse (adjoint)
          MFrameContext.kProjectionMtx                   Projection matrix
          MFrameContext.kProjectionTranposeMtx           Projection matrix tranpose
          MFrameContext.kProjectionInverseMtx            Projection matrix inverse
          MFrameContext.kProjectionTranspInverseMtx      Projection matrix tranpose inverse (adjoint)
          MFrameContext.kViewProjMtx                     View * projection matrix
          MFrameContext.kViewProjTranposeMtx             View * projection matrix tranpose
          MFrameContext.kViewProjInverseMtx              View * projection matrix inverse
          MFrameContext.kViewProjTranspInverseMtx        View * projection matrix tranpose inverse (adjoint)
          MFrameContext.kWorldViewMtx                    World * view matrix
          MFrameContext.kWorldViewTransposeMtx           World * view matrix transpose
          MFrameContext.kWorldViewInverseMtx             World * view matrix inverse
          MFrameContext.kWorldViewTranspInverseMtx       World * view matrix transpose inverse (adjoint)
          MFrameContext.kWorldViewProjMtx                World * view * projection matrix
          MFrameContext.kWorldViewProjTransposeMtx       World * view * projection matrix transpose
          MFrameContext.kWorldViewProjInverseMtx         World * view * projection matrix inverse
          MFrameContext.kWorldViewProjTranspInverseMtx   World * view * projection matrix tranpose inverse (adjoint)
        """
    
        pass
    
    
    def semanticToTupleType(*args, **kwargs):
        """
        semanticToTupleType(string) -> int
        
        Given a semantic name return the corresponding tuple enumeration that can be used to retrieve a value via the getTuple() method.
        
          MFrameContext.kViewPosition         View position
          MFrameContext.kViewDirection        View direction vector
          MFrameContext.kViewUp               View up vector
          MFrameContext.kViewRight            View right vector
          MFrameContext.kViewportPixelSize    Viewport size in pixels (single value)
          MFrameContext.kViewNearClipValue    Camera near clip value (single value)
          MFrameContext.kViewFarClipValue     Camera far clip value (single value)
          MFrameContext.kViewUnnormlizedNearClipValue Unnormalized camera near clip value (single value)
                 MFrameContext.kViewUnnormalizedFarClipValue Unnormalized camera far clip value (single value)
        """
    
        pass
    
    
    def shadeTemplates(*args, **kwargs):
        """
        shadeTemplates() -> bool
        
        Returns the display preference indicating whether templated objects should be drawn shaded.
        """
    
        pass
    
    
    def userChangingViewContext(*args, **kwargs):
        """
        userChangingViewContext() -> bool
        
        Returns True during any interactive refresh, as when user is    changing the view using view context
        tools such as tumble, dolly or track.
        """
    
        pass
    
    
    def wireOnShadedMode(*args, **kwargs):
        """
        wireOnShadedMode() -> int
        
        Returns the global user display preference which indicates how wireframe should be drawn on top of objects while in shaded mode.
        
        Please refer to documentation on the 'Wireframe-on-shaded' option under the 'Display->View' tab in the preferences window.
        
        Note that 'viewport in wireframe on shaded mode' is a different option which is per viewport. This can be tested by testing if
        a shaded mode is set as well as wireframe mode. Refer to the enumerations DisplayStyle and the method getDisplayStyle().
        
        
          MFrameContext.kWireframeOnShadedFull      Draw wireframe
          MFrameContext.kWireFrameOnShadedReduced   Draw wireframe but with reduced quality
          MFrameContext.kWireFrameOnShadedNone      Do not draw wireframe
        """
    
        pass
    
    
    __new__ = None
    
    
    k2dViewport = 1
    
    
    k3dViewport = 0
    
    
    kAmbientLight = 1
    
    
    kAmbientOcclusion = 0
    
    
    kAntiAliasing = 4
    
    
    kBackfaceCulling = 2048
    
    
    kBoundingBox = 4
    
    
    kCustomLights = 5
    
    
    kDefaultMaterial = 16
    
    
    kDepthOfField = 3
    
    
    kDepthPeeling = 3
    
    
    kExcludeAll = 18446744073709551615L
    
    
    kExcludeCVs = 131072L
    
    
    kExcludeCameras = 32L
    
    
    kExcludeClipGhosts = 17179869184L
    
    
    kExcludeDeformers = 256L
    
    
    kExcludeDimensions = 4096L
    
    
    kExcludeDynamicConstraints = 134217728L
    
    
    kExcludeDynamics = 512L
    
    
    kExcludeFluids = 2097152L
    
    
    kExcludeFollicles = 4194304L
    
    
    kExcludeGreasePencils = 34359738368L
    
    
    kExcludeGrid = 65536L
    
    
    kExcludeHUD = 8589934592L
    
    
    kExcludeHairSystems = 8388608L
    
    
    kExcludeHoldOuts = 2147483648L
    
    
    kExcludeHulls = 262144L
    
    
    kExcludeIkHandles = 128L
    
    
    kExcludeImagePlane = 16777216L
    
    
    kExcludeJoints = 64L
    
    
    kExcludeLights = 16L
    
    
    kExcludeLocators = 2048L
    
    
    kExcludeManipulators = 268435456L
    
    
    kExcludeMeshes = 4L
    
    
    kExcludeMotionTrails = 1073741824L
    
    
    kExcludeNCloths = 33554432L
    
    
    kExcludeNParticles = 536870912L
    
    
    kExcludeNRigids = 67108864L
    
    
    kExcludeNone = 0L
    
    
    kExcludeNurbsCurves = 1L
    
    
    kExcludeNurbsSurfaces = 2L
    
    
    kExcludeParticleInstancers = 1024L
    
    
    kExcludePivots = 16384L
    
    
    kExcludePlanes = 8L
    
    
    kExcludePluginShapes = 4294967296L
    
    
    kExcludeSelectHandles = 8192L
    
    
    kExcludeStrokes = 524288L
    
    
    kExcludeSubdivSurfaces = 1048576L
    
    
    kExcludeTextures = 32768L
    
    
    kFlatShaded = 256
    
    
    kFogExp = 1
    
    
    kFogExp2 = 2
    
    
    kFogLinear = 0
    
    
    kGammaCorrection = 2
    
    
    kGouraudShaded = 1
    
    
    kImage = 2
    
    
    kLightDefault = 2
    
    
    kMotionBlur = 1
    
    
    kNoLighting = 0
    
    
    kObjectSorting = 1
    
    
    kProjectionInverseMtx = 10
    
    
    kProjectionMtx = 8
    
    
    kProjectionTranposeMtx = 9
    
    
    kProjectionTranspInverseMtx = 11
    
    
    kSceneLights = 4
    
    
    kSelectedLights = 3
    
    
    kShadeActiveOnly = 512
    
    
    kSmoothWireframe = 4096
    
    
    kTextured = 8
    
    
    kTwoSidedLighting = 128
    
    
    kUnsorted = 0
    
    
    kViewColorTransformEnabled = 2
    
    
    kViewDirection = 1
    
    
    kViewFarClipValue = 6
    
    
    kViewInverseMtx = 6
    
    
    kViewMtx = 4
    
    
    kViewNearClipValue = 5
    
    
    kViewPosition = 0
    
    
    kViewProjInverseMtx = 14
    
    
    kViewProjMtx = 12
    
    
    kViewProjTranposeMtx = 13
    
    
    kViewProjTranspInverseMtx = 15
    
    
    kViewRight = 3
    
    
    kViewTranspInverseMtx = 7
    
    
    kViewTransposeMtx = 5
    
    
    kViewUnnormalizedFarClipValue = 8
    
    
    kViewUnnormlizedNearClipValue = 7
    
    
    kViewUp = 2
    
    
    kViewportPixelSize = 4
    
    
    kWeightedAverage = 2
    
    
    kWireFrame = 2
    
    
    kWireFrameOnShadedNone = 2
    
    
    kWireFrameOnShadedReduced = 1
    
    
    kWireframeOnShadedFull = 0
    
    
    kWorldInverseMtx = 2
    
    
    kWorldMtx = 0
    
    
    kWorldTranspInverseMtx = 3
    
    
    kWorldTransposeMtx = 1
    
    
    kWorldViewInverseMtx = 18
    
    
    kWorldViewMtx = 16
    
    
    kWorldViewProjInverseMtx = 22
    
    
    kWorldViewProjMtx = 20
    
    
    kWorldViewProjTranspInverseMtx = 23
    
    
    kWorldViewProjTransposeMtx = 21
    
    
    kWorldViewTranspInverseMtx = 19
    
    
    kWorldViewTransposeMtx = 17
    
    
    kXray = 64
    
    
    kXrayActiveComponents = 1024
    
    
    kXrayJoint = 32


class MTextureDescription(object):
    """
    Texture description. Provides sufficient information to describe how a block of data can be interpreted as a texture.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def setToDefault2DTexture(*args, **kwargs):
        """
        setToDefault2DTexture() -> self
        
        Utility to set texture description to describe a 0 size 2-dimensional texture.
        """
    
        pass
    
    
    fArraySlices = None
    
    fBytesPerRow = None
    
    fBytesPerSlice = None
    
    fDepth = None
    
    fEnvMapType = None
    
    fFormat = None
    
    fHeight = None
    
    fMipmaps = None
    
    fTextureType = None
    
    fWidth = None
    
    __new__ = None
    
    
    kCubeMap = 4
    
    
    kDepthTexture = 6
    
    
    kEnvCrossHoriz = 5
    
    
    kEnvCrossVert = 4
    
    
    kEnvCubemap = 6
    
    
    kEnvHemiSphere = 2
    
    
    kEnvLatLong = 3
    
    
    kEnvNone = 0
    
    
    kEnvSphere = 1
    
    
    kImage1D = 0
    
    
    kImage1DArray = 1
    
    
    kImage2D = 2
    
    
    kImage2DArray = 3
    
    
    kNumberOfEnvMapTypes = 7
    
    
    kNumberOfTextureTypes = 7
    
    
    kVolumeTexture = 5


class MPxShaderOverride(object):
    """
    Base class for user defined shading effect draw overrides.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def activateKey(*args, **kwargs):
        """
        activateKey(context, key) -> self
        
        This is the activateKey callback.
        
        This method is called during the draw phase before invoking any draw() callback that are sharing a common shader key.
        
        The default implementation is empty.
        """
    
        pass
    
    
    def addGeometryRequirement(*args, **kwargs):
        """
        addGeometryRequirement(MVertexBufferDescriptor) -> self
        
        During the initialization phase the geometry requirements for the shading effect can be updated. The update is
        accomplished by calling this method once for each new data stream that needs to be added to the list of requirements.
        
        If the geometry has multiple fields of the same type associated with it (e.g. multiple UV sets) the 'name' attribute
        of the vertex descriptor can be used to select the desired one. If that member is empty or does not match any of the
        fields then the default field of that type will be used.
        """
    
        pass
    
    
    def addGeometryRequirements(*args, **kwargs):
        """
        addGeometryRequirements(MVertexBufferDescriptorList) -> self
        
        
        During the initialization phase the geometry requirements for the shading effect can be updated. The update is
        accomplished by calling this method with a list containing descriptions of all data streams that are required by the shader.
        
        If the geometry has multiple fields of the same type associated with it (e.g. multiple UV sets) the 'name' attribute
        of the vertex descriptor can be used to select the desired one. If that member is empty or does not match any of the
        fields then the default field of that type will be used.
        
        This method will attempt to add as many requirements as possible from the list, skipping invalid ones.
        If kInvalidParameter is returned it means at least one requirement failed to be added.
        """
    
        pass
    
    
    def addIndexingRequirement(*args, **kwargs):
        """
        addIndexingRequirement(MIndexBufferDescriptor) -> self
        
        During the initialization phase the indexing requirements for the shading effect can be updated. The update is accomplished by
        calling this method once for each new index stream required by the shader.
        
        A shader override can specify the type of primitive it supports.  If the shader relies on a special primitive type like kPatch
        it should use this method to indicate that requirement to the system.  Not all fields on the MIndexBufferDescriptor need to be
        filled in when using this method.  Only the name(), primitive(), and primitiveStride() values are important for a shader to report
        as requirements.
        
        The primitive type must be specified if the shader requires a primitive type different then a standard point, line, or triangle list
        or strip. The primitiveStride must be specified if using the kPatch primitive type. Valid values range from 1 - 32.
        The name can be specified to trigger a custom MPxPrimitiveGenerator plugin to be used to produce the desired primitive tessellation.
        When requesting custom primitives you should register an MPxPrimitiveGenerator that knows how to produce the custom primitive needed
        by the shader.
        """
    
        pass
    
    
    def addShaderSignature(*args, **kwargs):
        """
        addShaderSignature(signature, signatureSize) -> selfaddShaderSignature(MShaderInstance) -> self
        
        During the initialization phase, the "signature" for the shader may be set. Certain Draw APIs (like DirectX 11) require a
        signature to allow a shading effect to be properly activated. The signature will be used if the override uses
        MPxShaderOverride.drawGeometry() in the draw phase in order to perform drawing. If drawing is done manually, adding a shader
        signature is not necessary.
        """
    
        pass
    
    
    def boundingBoxExtraScale(*args, **kwargs):
        """
        boundingBoxExtraScale() -> float
        
        Returns the Extra scale factor.
        
        Override this method to supply an extra scale factor to be applied to the object space bounding box of any objects
        which use the shader associated with this override. This is to allow the shader to indicate that the bounding box should
        be bigger than just the base geometry; normally due to shading effects like displacement. Note that the value returned
        here will only be used to put a lower bound on the extra scale applied to the bounding box. It may be made larger due to
        the demands of other shaders associated with the object.
        
        This method will be called any time a change occurs which may affect the bounding box of associated objects. It is acceptable
        to access the Maya dependency graph within calls to this method as it will never be called during draw.
        
        The default implementation returns the unit scale factor (1.0).
        """
    
        pass
    
    
    def draw(*args, **kwargs):
        """
        draw(context, renderItemList) -> bool
        
        This is the draw callback, the method is called during the draw phase.
        
        The expected implementation of this method is to do shader setup and then call drawGeometry() to allow Maya to handle the actual geometry drawing. It is however possible to do all shader setup and geometry draw here directly by accessing the hardware resource handles for geometry and index buffers through the geometry associated with each render item in the render item list.
        
        No dependency graph evaluation should occur during this phase. If data from Maya is needed here it must be cached on this object (or elsewhere) during the update phase.
        
        This method should return True on successful draw. If False is returned, Maya will attempt to draw using the default internal draw mechanism.
        
        Information about the current GPU state may be accessed through the MDrawContext object passed to this method. The MRenderItemList object contains one render item for each object that is meant to be drawn by this method.
        
        * context [IN/OUT] (MDrawContext) - The current draw context
        * renderItemList (MRenderItemList) - The list of renderable items to draw
        
        Returns True if draw was successful, False otherwise.
        """
    
        pass
    
    
    def drawGeometry(*args, **kwargs):
        """
        drawGeometry(MDrawContext) -> self
        
        This method may be called from draw() and will cause Maya to immediately draw the current geometry using the current state of the draw API.
        """
    
        pass
    
    
    def endUpdate(*args, **kwargs):
        """
        endUpdate() -> self
        
        This is the final part of the update phase.
        
        This method is called by Maya to allow the plugin to clean up any data or state from the previous update stages.
        No dependency graph evaluation, nor graphics device access should be performed during this phase.
        """
    
        pass
    
    
    def handlesConsolidatedGeometry(*args, **kwargs):
        """
        handlesConsolidatedGeometry() -> bool
        
        Returns True if the shader instance should disable the consolidation
        for the geometry it is applied to.
        
        Override this method if the shader instance should disable the consolidation
        for the geometry it is applied to.This is to prevent inconsistency between consolidated and non-consolidated geometry,
        particularly useful for shading effects that compute displacement based on
        the World position.
        
        The default implementation returns true indicating that the shader instance
        should not be disable the consolidation of the geometry.
        """
    
        pass
    
    
    def handlesDraw(*args, **kwargs):
        """
        handlesDraw(context) -> bool
        
        Returns True if shader handles drawing.
        
        This method indicates whether the shader will handle the drawing based on the context passed in.
        
        The default implementation will check the pass context. If the pass semantic is specified to be a color pass
        and the pass has no shader override (MPassContext.hasShaderOverride() returns False) then this method will return True.
        """
    
        pass
    
    
    def initialize(*args, **kwargs):
        """
        initialize(shader) -> string
        initialize(initContext, initFeedback) -> string
        
        Initialization occurs when Maya determines that the hardware shader needs to be rebuilt. Any initialization
        work may be performed here. Also, this is the only time that calls to addGeometryRequirement() may occur.
        
        Note: There are two versions of the initialize method. Derived classes should override exactly one of them.
        
        The default implementation returns a constant string.
        """
    
        pass
    
    
    def isTransparent(*args, **kwargs):
        """
        isTransparent() -> bool
        
        Returns True if semi-transparent drawing should occur.
        
        During the update phase the override will be called to return whether it will be drawing with semi-transparency.
        
        This call occurs after updateDevice() which allows for any device evaluation to occur to determine the transparency state.
        
        The default return value is False.
        """
    
        pass
    
    
    def nonTexturedShaderInstance(*args, **kwargs):
        """
        nonTexturedShaderInstance() -> MShaderInstancenonTexturedShaderInstance() -> (MShaderInstance, bool)
        
        Returns an override shader instance to be used when drawing in non-textured
        mode. If None is returned an internally defined non-modifiable shader
        instance is used.
        
        A second optional boolean value 'monitorNode' can be returned as well which will indicate
        that the associated shader node requires monitoring to call back to the override
        during the update phase.
        
        Note that if transparency is required at initialization time then
        the method setIsTransparent() should be called
        within this method.
        
        The default implementation returns None indicating that no shader instance will be used.
        """
    
        pass
    
    
    def overridesDrawState(*args, **kwargs):
        """
        overridesDrawState() -> bool
        
        Returns True if the override overrides the draw state.
        
        During the draw phase this method will be called to determine whether the override will override the draw state when drawing.
        
        This call occurs after updateDevice() which allows for any device evaluation to occur to determine if the override will
        override the draw state.
        
        The Viewport 2.0 renderer will skip setting the draw state for plugins that will override the draw state when drawing.
        Note that the MPxShaderOverride.terminateKey() should still return the draw state to the value it had when activateKey was called.
        
        The default return value is False.
        """
    
        pass
    
    
    def overridesNonMaterialItems(*args, **kwargs):
        """
        overridesNonMaterialItems() -> bool
        
        Returns True if the shader instance should also be used to render non material items.
        
        Override this method if the shader instance should also be used to render
        non material items such as the wireframe and the selected edges/vertices components.
        This is particularly useful for shading effects that compute displacement for
        which the object geometry will not match the rendered material, making selection
        difficult.
        
        The default implementation returns False indicating that the shader instance
        should not be used for non material items.
        """
    
        pass
    
    
    def rebuildAlways(*args, **kwargs):
        """
        rebuildAlways() -> bool
        
        Returns True if the shader and geometry should be rebuilt on every update.
        
        If this method returns True, it will force shader and geometry data to be rebuilt on any change to the shader.
        This may be necessary for shaders that request specific named data sets like UVs or CPVs.
        Any change to the required data set means that geometry needs to be rebuilt.
        
        The default return value is False.
        """
    
        pass
    
    
    def setGeometryRequirements(*args, **kwargs):
        """
        setGeometryRequirements(MShaderInstance) -> self
        
        
        During the initialization phase the geometry requirements for the shading effect can be updated. The update can be
        accomplished by calling this method with a shader instance (MShaderInstance). The geometry requirements are copied
        from the MShaderInstance and used as the current shading effect requirements. If there are any requirements already
        specified for the shading effect, they will be replaced.
        
        This method should not be used in conjunction with addGeometryRequirement() and addGeometryRequirements() methods.
        The reason is that when rendering the vertex format used must exactly match the one used for the shader instance.
        If any additional requirements are added, the geometry may not draw properly.
        
        The corresponding addShaderSignature() method, which takes an MShaderInstance as an input argument, should also be
        called during initialization if the utility method drawGeometry() is used by the plug-in.
        """
    
        pass
    
    
    def shaderInstance(*args, **kwargs):
        """
        shaderInstance() -> MShaderInstance
        
        Returns the Shader instance.
        
        Override this method if a shader instance (MShaderInstance) is to be used for drawing.
        
        The default implementation returns None indicating that no shader instance will be used.
        """
    
        pass
    
    
    def supportedDrawAPIs(*args, **kwargs):
        """
        supportedDrawAPIs() -> DrawAPI
        
        Returns The draw API supported by this override.
        
        Returns the draw API supported by this override. The returned value may be formed as the bitwise 'or'
        of render drawAPI elements to indicate that the override supports multiple draw APIs. See MRenderer.drawAPI().
        This method returns 'MRender.kOpenGL' by default.
        """
    
        pass
    
    
    def supportsAdvancedTransparency(*args, **kwargs):
        """
        supportsAdvancedTransparency() -> bool
        
        Returns True if advanced tranparency algorithm is supported.
        
        During the update phase the override will be called to return whether it supports advanced transparency algorithms
        (such as depth peeling).
        """
    
        pass
    
    
    def terminateKey(*args, **kwargs):
        """
        terminateKey(context, key) -> self
        
        This is the terminateKey callback.
        
        This method is called during the draw phase after invoking draw() callbacks that are sharing a common shader key.
        
        The default implementation is empty.
        """
    
        pass
    
    
    def updateDG(*args, **kwargs):
        """
        updateDG(object) -> self
        
        This is the first part of the update phase.
        
        Perform any work required to update the shading effect which is related to evaluating the dependency graph.
        This should be the only place that dependency graph evaluation occurs. Data retrieved from Maya may be cached
        on the override for use in later stages.
        """
    
        pass
    
    
    def updateDevice(*args, **kwargs):
        """
        updateDevice() -> self
        
        This is the second part of the update phase.
        
        Perform any work required to update the shading effect which is related to accessing the underlying graphics
        device. This is the only place that the graphics device may be safely accessed other than at draw time.
        """
    
        pass
    
    
    __new__ = None


class MVaryingParameterList(object):
    """
    MVaryingParameterList specify the surface component level data used by a hardware shader, allowing Maya to handle setting up the node and user interfaces to the data, the population and access of cached data, etc.
    """
    
    
    
    def __getitem__(*args, **kwargs):
        """
        x.__getitem__(y) <==> x[y]
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __len__(*args, **kwargs):
        """
        x.__len__() <==> len(x)
        """
    
        pass
    
    
    def append(*args, **kwargs):
        """
        append(element) -> bool
        
        Append a new parameter to this end of this list.
        
        * element (MVaryingParameter) - The new parameter to append
        """
    
        pass
    
    
    def copy(*args, **kwargs):
        """
        copy(source) -> self
        
        Copy data from source list.
        
        * source (MVaryingParameterList) - The source list to copy from
        """
    
        pass
    
    
    def setElement(*args, **kwargs):
        """
        setElement(n, element) -> bool
        
        Set the nth parameter in this list.
        
        * n (int) - The index of the element to set
        * element (MVaryingParameter) - The value to set
        """
    
        pass
    
    
    def setLength(*args, **kwargs):
        """
        setLength(length) -> bool
        
        Set the number of parameters in this list. If this is greater than the current number of parameters in the list, the caller is responsible for setting the new parameters to valid values using setElement.
        
        * length (int) - The number of parameters in this list.
        """
    
        pass
    
    
    __new__ = None


class MBlendStateDesc(object):
    """
    Descriptor for a blend state for a single render target.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def setDefaults(*args, **kwargs):
        """
        setDefaults() -> self
        
        Set all values for the blend state to their default values.
        """
    
        pass
    
    
    alphaToCoverageEnable = None
    
    blendFactor = None
    
    independentBlendEnable = None
    
    multiSampleMask = None
    
    targetBlends = None
    
    __new__ = None


class MStateManager(object):
    """
    Class to allow efficient access to GPU state information.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def getBlendState(*args, **kwargs):
        """
        getBlendState() -> MBlendState
        
        Gets the current active blend state from the device.
        """
    
        pass
    
    
    def getDepthStencilState(*args, **kwargs):
        """
        getDepthStencilState() -> MDepthStencilState
        
        Gets the current depth-stencil blend state from the device.
        """
    
        pass
    
    
    def getRasterizerState(*args, **kwargs):
        """
        getRasterizerState() -> MRasterizerState
        
        Gets the current active rasterizer state from the device.
        """
    
        pass
    
    
    def getSamplerState(*args, **kwargs):
        """
        getSamplerState(shader, samplerIndex) -> MSamplerState
        
        Gets the current active sampler state from the device.
        * shader (ShaderType) - The shader this sampler will apply to.
        * samplerIndex (int) - The index of the sampler to set with the given shader state.
        """
    
        pass
    
    
    def setBlendState(*args, **kwargs):
        """
        setBlendState(MBlendState) -> self
        
        Sets the active blend state on the device.
        """
    
        pass
    
    
    def setDepthStencilState(*args, **kwargs):
        """
        setDepthStencilState(MDepthStencilState) -> self
        
        Sets the active depth-stencil state on the device.
        """
    
        pass
    
    
    def setRasterizerState(*args, **kwargs):
        """
        setRasterizerState(MRasterizerState) -> self
        
        Sets the active rasterizer state on the device.
        """
    
        pass
    
    
    def setSamplerState(*args, **kwargs):
        """
        setSamplerState(shader, samplerIndex, samplerState) -> self
        
        Sets the active sampler state for any of the texture samplers on the device.
        * shader (ShaderType) - The shader this sampler will apply to, e.g. kPixelShader.
        * samplerIndex (int) - The index of the sampler to set with the given shader state.
        * samplerState (MSamplerState) - The sampler state container object that was previously acquired.
        """
    
        pass
    
    
    def acquireBlendState(*args, **kwargs):
        """
        acquireBlendState(MBlendStateDesc) -> MBlendState
        
        Acquires an immutable unique blend state matching the blend state descriptor.
        """
    
        pass
    
    
    def acquireDepthStencilState(*args, **kwargs):
        """
        acquireDepthStencilState(MDepthStencilStateDesc) -> MDepthStencilState
        
        Acquires an immutable unique depth-stencil state matching the blend state descriptor.
        """
    
        pass
    
    
    def acquireRasterizerState(*args, **kwargs):
        """
        acquireRasterizerState(MRasterizerStateDesc) -> MRasterizerState
        
        Acquires an immutable unique rasterizer state matching the rasterizer state descriptor.
        """
    
        pass
    
    
    def acquireSamplerState(*args, **kwargs):
        """
        acquireSamplerState(MSamplerStateDesc) -> MSamplerState
        
        Acquires an immutable unique sampler state matching the blend state descriptor.
        """
    
        pass
    
    
    def getMaxSamplerCount(*args, **kwargs):
        """
        getMaxSamplerCount() -> int
        
        Get the maximum number of simulataneous texture coordinate interpolation channels.
        """
    
        pass
    
    
    def releaseBlendState(*args, **kwargs):
        """
        releaseBlendState(MBlendState) -> None
        
        Deletes the MBlendState and releases the reference to the underlying state object which is held by the MBlendState object.
        """
    
        pass
    
    
    def releaseDepthStencilState(*args, **kwargs):
        """
        releaseDepthStencilState(MDepthStencilState) -> None
        
        Deletes the MDepthStencilState and releases the reference to the underlying state object which is held by the MDepthStencilState object.
        """
    
        pass
    
    
    def releaseRasterizerState(*args, **kwargs):
        """
        releaseRasterizerState(MRasterizerState) -> None
        
        Deletes the MRasterizerState and releases the reference to the underlying state object which is held by the MRasterizerState object.
        """
    
        pass
    
    
    def releaseSamplerState(*args, **kwargs):
        """
        releaseSamplerState(MSamplerState) -> None
        
        Deletes the MSamplerState and releases the reference to the underlying state object which is held by the MSamplerState object.
        """
    
        pass
    
    
    __new__ = None
    
    
    kCompareAlways = 8
    
    
    kCompareEqual = 3
    
    
    kCompareGreater = 5
    
    
    kCompareGreaterEqual = 7
    
    
    kCompareLess = 2
    
    
    kCompareLessEqual = 4
    
    
    kCompareNever = 1
    
    
    kCompareNotEqual = 6
    
    
    kDomainShader = 5
    
    
    kGeometryShader = 2
    
    
    kHullShader = 4
    
    
    kNoShader = 0
    
    
    kPixelShader = 3
    
    
    kVertexShader = 1


class MRenderTargetManager(object):
    """
    Provides access to MRenderTarget objects for use in Viewport 2.0.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def acquireRenderTarget(*args, **kwargs):
        """
        acquireRenderTarget(MRenderTargetDescription) -> MRenderTarget
        Acquire an instance of a render target.
        When the object is no longer needed, releaseRenderTarget() should be called
        to notify the target manager that the caller is done with the render target.
        """
    
        pass
    
    
    def acquireRenderTargetFromScreen(*args, **kwargs):
        """
        acquireRenderTargetFromScreen(string) -> MRenderTarget
        Acquire an instance of a render target with the same characteristics as the current on-screen target.
        When the object is no longer needed, releaseRenderTarget() should be called
        to notify the target manager that the caller is done with the render target.
        """
    
        pass
    
    
    def formatSupportsSRGBWrite(*args, **kwargs):
        """
        formatSupportsSRGBWrite(int) -> bool
        This method will perform a check to determine whether gamma correction can be performed
        by the GPU when writing pixels to a render target of a given format.
        """
    
        pass
    
    
    def releaseRenderTarget(*args, **kwargs):
        """
        releaseRenderTarget(MRenderTarget) -> self
        Deletes the MRenderTarget and releases the reference to the underlying target which is held by the MRenderTarget object.
        """
    
        pass
    
    
    __new__ = None


class MUniformParameter(object):
    """
    The MUniformParameter class provides a high-level interface to hardware shader uniform parameters. By defining your shader's uniform parameters through this class, you allow Maya to handle the attributes, editing, serialisation, and caching for you in a standard way that ensure you'll be able to leverage future performance and functionlity improvements.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def asBool(*args, **kwargs):
        """
        asBool(context) -> bool
        
        Get the value of this uniform parameter as a boolean value.
        Because some parameters can be shape-dependent, the method requires access to the current context being rendered.
        
        * context (MDrawContext) - Draw context being used for render.
        """
    
        pass
    
    
    def asFloat(*args, **kwargs):
        """
        asFloat(context) -> float
        
        Get the value of this uniform parameter as a float.
        Because some parameters can be shape-dependent, the method requires access to the current context being rendered.
        
        * context (MDrawContext) - Draw context being used for render.
        """
    
        pass
    
    
    def asFloatArray(*args, **kwargs):
        """
        asFloatArray(context) -> tuple of floats
        
        Get the value of this uniform parameter as one or more floating point values.
        Because some parameters can be shape-dependent, the method requires access to the current context being rendered.
        
        * context (MDrawContext) - Draw context being used for render.
        """
    
        pass
    
    
    def asInt(*args, **kwargs):
        """
        asInt(context) -> int
        
        Get the value of this uniform parameter as an integer.
        Because some parameters can be shape-dependent, the method requires access to the current context being rendered.
        
        * context (MDrawContext) - Draw context being used for render.
        """
    
        pass
    
    
    def asString(*args, **kwargs):
        """
        asString(context) -> string
        
        Get the value of this uniform parameter as a string.
        Because some parameters can be shape-dependent, the method requires access to the current context being rendered.
        
        * context (MDrawContext) - Draw context being used for render.
        """
    
        pass
    
    
    def copy(*args, **kwargs):
        """
        copy(source) -> self
        
        Copy data from source parameter.
        
        * source (MUniformParameter) - The source parameter to copy from
        """
    
        pass
    
    
    def hasChanged(*args, **kwargs):
        """
        hasChanged(context) -> bool
        
        Has the value of this parameter changed since the last time it was accessed?
        This allows your shader to minimise state changes by only updating modified parameters.
        
        * context (MDrawContext) - Draw context being used for render.
        """
    
        pass
    
    
    def isATexture(*args, **kwargs):
        """
        isATexture() -> bool
        
        Returns True if this parameter represents a texture, False otherwise.
        """
    
        pass
    
    
    def name(*args, **kwargs):
        """
        name() -> string
        
        Get the name of this parameter.
        """
    
        pass
    
    
    def numColumns(*args, **kwargs):
        """
        numColumns() -> int
        
        Get the number of columns in this parameter.
        """
    
        pass
    
    
    def numElements(*args, **kwargs):
        """
        numElements() -> int
        
        Get the number of elements in this parameter (including rows and columns).
        """
    
        pass
    
    
    def numRows(*args, **kwargs):
        """
        numRows() -> int
        
        Get the number of rows in this parameter.
        """
    
        pass
    
    
    def plug(*args, **kwargs):
        """
        plug() -> MPlug
        
        Get the plug managed by this parameter.
        """
    
        pass
    
    
    def semantic(*args, **kwargs):
        """
        semantic() -> int
        
        Get the semantic of this parameter.
        
        The list of available semantic values can be obtained with the following commands:
          print filter(lambda k: k.startswith('kSemantic'), dir(maya.api.OpenMayaRender.MUniformParameter))
        """
    
        pass
    
    
    def setBool(*args, **kwargs):
        """
        setBool(value) -> self
        
        Set the value of this uniform parameter as a boolean value.
        Note that it is not possible to set shape-dependent parameters.
        
        * value (bool) - the new value for this parameter.
        """
    
        pass
    
    
    def setDirty(*args, **kwargs):
        """
        setDirty() -> self
        
        Mark the data for this parameter as dirty. This will force the parameter to report that it has been changed the next time it is accessed. This allows external events (e.g. device lost, texture management, etc) to force a shader to re-set parameters tied to externally managed resources.
        """
    
        pass
    
    
    def setFloat(*args, **kwargs):
        """
        setFloat(value) -> self
        
        Set the value of this uniform parameter as a float.
        Note that it is not possible to set shape-dependent parameters.
        
        * value (float) - the new float value for this parameter.
        """
    
        pass
    
    
    def setFloatArray(*args, **kwargs):
        """
        setFloatArray(value) -> self
        
        Set the value of this uniform parameter as one or more floating point values.
        Note that it is not possible to set shape-specific parameters.
        
        * value (tuple of floats) - a tuple of floats holding the new floating point value(s) for this parameter.
        """
    
        pass
    
    
    def setInt(*args, **kwargs):
        """
        setInt(value) -> self
        
        Set the value of this uniform parameter as an integer value.
        Note that it is not possible to set shape-dependent parameters.
        
        * value (int) - the new value for this parameter.
        """
    
        pass
    
    
    def setString(*args, **kwargs):
        """
        setString(value) -> self
        
        Set the value of this uniform parameter as a string.
        Note that it is not possible to set shape-dependent parameters.
        
         * value (string) - the new string value for this parameter.
        """
    
        pass
    
    
    def source(*args, **kwargs):
        """
        source() -> MPlug
        
        Get the source plug connected to this parameter. Other than textures, this will typically be an invalid plug.
        """
    
        pass
    
    
    def type(*args, **kwargs):
        """
        type() -> int
        
        Get the type of this parameter.
        
        Available values:
          kTypeUnknown,
          kTypeBool,
          kTypeInt,
          kTypeFloat,
          kType1DTexture,
          kType2DTexture,
          kType3DTexture,
          kTypeCubeTexture,
          kTypeEnvTexture,
          kTypeString,
          kTypeEnum
        """
    
        pass
    
    
    def userData(*args, **kwargs):
        """
        userData() -> int
        
        Get the user data for this parameter. User data can be used to store plugin specific information that you want to associate with this parameter. Typically this will be used to store a handle to the effect parameter.
        """
    
        pass
    
    
    enumFieldNames = None
    
    keyable = None
    
    rangeMax = None
    
    rangeMin = None
    
    softRangeMax = None
    
    softRangeMin = None
    
    uiHidden = None
    
    uiNiceName = None
    
    __new__ = None
    
    
    kSemanticBackgroundColor = 46
    
    
    kSemanticBump = 11
    
    
    kSemanticBumpTexture = 30
    
    
    kSemanticColor = 9
    
    
    kSemanticColorTexture = 28
    
    
    kSemanticEnvironment = 12
    
    
    kSemanticFrameNumber = 47
    
    
    kSemanticHWSEdgeLevel = 52
    
    
    kSemanticHWSFaceLevel = 51
    
    
    kSemanticHWSFrontCCW = 55
    
    
    kSemanticHWSHighlighting = 57
    
    
    kSemanticHWSInstancedDraw = 56
    
    
    kSemanticHWSObjectLevel = 50
    
    
    kSemanticHWSOccluder = 54
    
    
    kSemanticHWSPrimitiveBase = 48
    
    
    kSemanticHWSPrimitiveCountPerInstance = 49
    
    
    kSemanticHWSVertexLevel = 53
    
    
    kSemanticLocalViewer = 44
    
    
    kSemanticNormal = 10
    
    
    kSemanticNormalTexture = 29
    
    
    kSemanticNormalizationTexture = 31
    
    
    kSemanticObjectDir = 1
    
    
    kSemanticObjectPos = 5
    
    
    kSemanticOpaqueDepthTexture = 33
    
    
    kSemanticProjectionDir = 4
    
    
    kSemanticProjectionInverseMatrix = 20
    
    
    kSemanticProjectionInverseTransposeMatrix = 21
    
    
    kSemanticProjectionMatrix = 19
    
    
    kSemanticProjectionPos = 8
    
    
    kSemanticProjectionTransposeMatrix = 37
    
    
    kSemanticTime = 34
    
    
    kSemanticTranspDepthTexture = 32
    
    
    kSemanticUnknown = 0
    
    
    kSemanticViewDir = 3
    
    
    kSemanticViewInverseMatrix = 17
    
    
    kSemanticViewInverseTransposeMatrix = 18
    
    
    kSemanticViewMatrix = 16
    
    
    kSemanticViewPos = 7
    
    
    kSemanticViewProjectionInverseMatrix = 41
    
    
    kSemanticViewProjectionInverseTransposeMatrix = 43
    
    
    kSemanticViewProjectionMatrix = 40
    
    
    kSemanticViewProjectionTransposeMatrix = 42
    
    
    kSemanticViewTransposeMatrix = 36
    
    
    kSemanticViewportPixelSize = 45
    
    
    kSemanticWorldDir = 2
    
    
    kSemanticWorldInverseMatrix = 14
    
    
    kSemanticWorldInverseTransposeMatrix = 15
    
    
    kSemanticWorldMatrix = 13
    
    
    kSemanticWorldPos = 6
    
    
    kSemanticWorldTransposeMatrix = 35
    
    
    kSemanticWorldViewInverseMatrix = 23
    
    
    kSemanticWorldViewInverseTransposeMatrix = 24
    
    
    kSemanticWorldViewMatrix = 22
    
    
    kSemanticWorldViewProjectionInverseMatrix = 26
    
    
    kSemanticWorldViewProjectionInverseTransposeMatrix = 27
    
    
    kSemanticWorldViewProjectionMatrix = 25
    
    
    kSemanticWorldViewProjectionTransposeMatrix = 39
    
    
    kSemanticWorldViewTransposeMatrix = 38
    
    
    kType1DTexture = 4
    
    
    kType2DTexture = 5
    
    
    kType3DTexture = 6
    
    
    kTypeBool = 1
    
    
    kTypeCubeTexture = 7
    
    
    kTypeEnum = 10
    
    
    kTypeEnvTexture = 8
    
    
    kTypeFloat = 3
    
    
    kTypeInt = 2
    
    
    kTypeString = 9
    
    
    kTypeUnknown = 0


class MRasterizerStateDesc(object):
    """
    Descriptor for a complete rasterizer state.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def setDefaults(*args, **kwargs):
        """
        setDefaults() -> self
        
        Set all values for the rasterizer state to their default values.
        """
    
        pass
    
    
    antialiasedLineEnable = None
    
    cullMode = None
    
    depthBias = None
    
    depthBiasClamp = None
    
    depthBiasIsFloat = None
    
    depthClipEnable = None
    
    fillMode = None
    
    frontCounterClockwise = None
    
    multiSampleEnable = None
    
    scissorEnable = None
    
    slopeScaledDepthBias = None
    
    __new__ = None


class MDepthNormalizationDescription(object):
    """
    Information required to perform normalization of values stored in the depth buffer of an MImage with respect to clipping plane range.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    fDepthBias = None
    
    fDepthScale = None
    
    fFarClipDistance = None
    
    fNearClipDistance = None
    
    __new__ = None


class MDepthStencilStateDesc(object):
    """
    Descriptor for a complete depth-stencil state.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def setDefaults(*args, **kwargs):
        """
        setDefaults() -> self
        
        Set all values for the depth stencil state to their default values.
        """
    
        pass
    
    
    backFace = None
    
    depthEnable = None
    
    depthFunc = None
    
    depthWriteEnable = None
    
    frontFace = None
    
    stencilEnable = None
    
    stencilReadMask = None
    
    stencilReferenceVal = None
    
    stencilWriteMask = None
    
    __new__ = None


class MAttributeParameterMapping(object):
    """
    Class for defining relationship between Maya attributes and fragment parameters.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def allowConnection(*args, **kwargs):
        """
        allowConnection() -> bool
        
        This method returns true if Maya is allowed to connect other shade fragments to the parameter named by this mapping.
        """
    
        pass
    
    
    def allowRename(*args, **kwargs):
        """
        allowRename() -> bool
        
        This method returns true if the parameter named by this mapping may be renamed in the final shading effect.
        If false, name collisions of parameters will be unresolved and results will be unpredictable.
        """
    
        pass
    
    
    def attributeName(*args, **kwargs):
        """
        attributeName() -> string
        
        Get the attribute name for this mapping.
        """
    
        pass
    
    
    def parameterName(*args, **kwargs):
        """
        parameterName() -> string
        
        Get the parameter name for this mapping.
        """
    
        pass
    
    
    def resolvedParameterName(*args, **kwargs):
        """
        resolvedParameterName() -> string
        
        Get the resolved parameter name for this mapping. After the fragment has been joined with other
        fragments to form the final shading effect its parameters are renamed to prevent name collisions.
        This returns the name of the parameter on the final shading effect.
        This name is useful in MPxShadingNodeOverride::updateShader() for setting parameter values manually.
        
        If the fragment has not yet been joined with other fragments, this will return the same string as parameterName().
        """
    
        pass
    
    
    __new__ = None


class MRenderUtilities(object):
    """
    Utilities class for rendering in Viewport 2.0
    """
    
    
    
    def acquireSwatchDrawContext(*args, **kwargs):
        """
        acquireSwatchDrawContext() -> MDrawContext
        acquireSwatchDrawContext(colorTarget) -> MDrawContext
        acquireSwatchDrawContext(colorTarget, depthTarget) -> MDrawContext
        
        Acquire a draw context fit for rendering a swatch.
        The caller is responsible for releasing the draw context when it is no longer needed, by calling MRenderUtilities::releaseDrawContext().
        
        * colorTarget (MRenderTarget) -  The color target for swatch drawing.
        * depthTarget (MRenderTarget) -  The depth target for swatch drawing.
        If targets are not provided, the caller is responsible for properly setting up render targets.
        Specifying targets also insures that the proper GL context is made active when using GL devices.
        """
    
        pass
    
    
    def acquireUVTextureDrawContext(*args, **kwargs):
        """
        acquireUVTextureDrawContext() -> MDrawContext
        acquireUVTextureDrawContext(colorTarget) -> MDrawContext
        acquireUVTextureDrawContext(colorTarget, depthTarget) -> MDrawContext
        
        Acquire a draw context fit for rendering a texture for the UV editor.
        The caller is responsible for releasing the draw context when it is no longer needed, by calling MRenderUtilities::releaseDrawContext().
        
        * colorTarget (MRenderTarget) -  The color target for UV texture drawing.
        * depthTarget (MRenderTarget) -  The depth target for UV texture drawing.
        If targets are not provided, the caller is responsible for properly setting up render targets.
        Specifying targets also insures that the proper GL context is made active when using GL devices.
        """
    
        pass
    
    
    def blitTargetToGL(*args, **kwargs):
        """
        blitTargetToGL(target, region, unfiltered) -> None
        
        Blit the data from a target to current GL context.
        
        * target (MRenderTarget) - The source target to get the data from.
        * region (float[2][2]) - Rectangular region to be rendered - [ [x1, y1], [x2, y2] ].
        * unfiltered (bool) - Render with hardware filtering or sharply defined pixels.
        """
    
        pass
    
    
    def blitTargetToImage(*args, **kwargs):
        """
        blitTargetToImage(target, image) -> None
        
        Copy the data from a target to an image.
        
        * target (MRenderTarget) - The source target to get the data from.
        * image (MImage) - The destination image to copy the data to.
        """
    
        pass
    
    
    def drawSimpleMesh(*args, **kwargs):
        """
        drawSimpleMesh(context, vertexBuffer, indexBuffer, primitiveType, start, count) -> None
        
        Render a simple mesh.
        
        * context (MDrawContext) - The draw context to use for render.
        * vertexBuffer (MVertexBuffer) - The vertex buffer for the mesh.
        * indexBuffer (MIndexBuffer) - The index buffer for the mesh.
        * primitiveType (int) - The primitive type of the mesh. See MGeometry.primitiveString()
        * start (int) - The location of the first index read from the index buffer.
        * count (int) - The number of indices to draw.
        """
    
        pass
    
    
    def releaseDrawContext(*args, **kwargs):
        """
        releaseDrawContext(context) -> None
        releaseDrawContext(context, releaseTargets) -> None
        
        Release a draw context.
        
        * context (MDrawContext) - The draw context to release.
        * releaseTargets (bool) - Removes the current draw targets from the device, defaults to true.
        If releaseTargets is requested, the device will have NULL targets on function exit.
        """
    
        pass
    
    
    def renderMaterialViewerGeometry(*args, **kwargs):
        """
        renderMaterialViewerGeometry(shape, shaderNode, image, cameraMode=kPerspectiveCamera, lightRig=kDefaultLights) -> None
        
        Do an off-screen render replicating the results shown by the Material Viewer window of Hypershade..
        
        * shape (str) Shape to render. Valid values include "meshSphere", "meshPlane", "meshShaderball", "meshTeapot", and "meshCloth".
        * shaderNode (MObject) The shader node to use on the geometry.
        * image (MImage) The image where the result should be stored.
        * cameraMode (int) The camera to use for rendering. Defaults to MRenderUtilities.kPerspectiveCamera.
        * lightRig (int) The light rig to use for rendering. Defaults to MRenderUtilities.kDefaultLights.
        """
    
        pass
    
    
    def swatchBackgroundColor(*args, **kwargs):
        """
        swatchBackgroundColor() -> MColor
        
        Returns the default background color for the hardware rendered swatch.
        """
    
        pass
    
    
    kAmbientLight = 2
    
    
    kDefaultLights = 0
    
    
    kOrthogonalCameraCloseUp = 2
    
    
    kOrthogonalCameraWithMargin = 1
    
    
    kPerspectiveCamera = 0
    
    
    kSwatchLight = 1


class MTextureUpdateRegion(object):
    """
    Structure to represent an update region for a texture.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    fXRangeMax = None
    
    fXRangeMin = None
    
    fYRangeMax = None
    
    fYRangeMin = None
    
    fZRangeMax = None
    
    fZRangeMin = None
    
    __new__ = None


class MStencilOpDesc(object):
    """
    Descriptor for a depth-stencil operation.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def setDefaults(*args, **kwargs):
        """
        setDefaults() -> self
        
        Set all values for the stencil operation state to their default values.
        """
    
        pass
    
    
    stencilDepthFailOp = None
    
    stencilFailOp = None
    
    stencilFunc = None
    
    stencilPassOp = None
    
    __new__ = None


class MAttributeParameterMappingList(object):
    """
    A list of MAttributeParameterMapping objects.
    """
    
    
    
    def __getitem__(*args, **kwargs):
        """
        x.__getitem__(y) <==> x[y]
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __len__(*args, **kwargs):
        """
        x.__len__() <==> len(x)
        """
    
        pass
    
    
    def append(*args, **kwargs):
        """
        append(MAttributeParameterMapping) -> self
        
        Add a mapping to the list. The list makes a copy; ownership of the original is left with the caller.
        """
    
        pass
    
    
    def clear(*args, **kwargs):
        """
        clear() -> self
        
        Clear all mappings from the list.
        """
    
        pass
    
    
    def findByAttributeName(*args, **kwargs):
        """
        findByAttributeName(attributeName) -> MAttributeParameterMapping
        
        Find a mapping by attribute name.
        This will return the first mapping found with a matching attribute name.
        """
    
        pass
    
    
    def findByParameterName(*args, **kwargs):
        """
        findByParameterName(parameterName) -> MAttributeParameterMapping
        
        Find a mapping by parameter name.
        This will return the first mapping found with a matching parameter name.
        """
    
        pass
    
    
    __new__ = None


class MRenderItemList(object):
    """
    A list of MRenderItem objects.
    """
    
    
    
    def __getitem__(*args, **kwargs):
        """
        x.__getitem__(y) <==> x[y]
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __len__(*args, **kwargs):
        """
        x.__len__() <==> len(x)
        """
    
        pass
    
    
    def append(*args, **kwargs):
        """
        append(MVertexBufferDescriptor) -> bool
        
        Add the item to the list. The list assumes ownership of the item.
        """
    
        pass
    
    
    def clear(*args, **kwargs):
        """
        clear() -> self
        
        Clear the list.
        """
    
        pass
    
    
    def indexOf(*args, **kwargs):
        """
        indexOf(name) -> int
        indexOf(name, type) -> int
        indexOf(name, primitive, mode) -> int
        
        Find the index of the first render item in the list matching the given search parameters.
        
        * name (string) - The name of the render item.
        * type (int) - The type of the render item.
        * primitive (int) - The primitive type of the render item.
        * mode (int) - The draw mode of the render item.
        
        See MRenderItem.type() for a list of valid render item types.
        See MGeometry.primitiveString() for a list of valid primitive types.
        See MGeometry.drawModeString() for a list of valid draw modes.
        """
    
        pass
    
    
    def remove(*args, **kwargs):
        """
        remove(index) -> bool
        
        Remove the item at the specified index. Item is deleted.
        """
    
        pass
    
    
    __new__ = None


class MGeometryExtractor(object):
    """
    Class for extracting renderable geometry.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def populateIndexBuffer(*args, **kwargs):
        """
        populateIndexBuffer(data, primitiveCount, indexDesc) -> self
        
        Fill a buffer with geometry indexing data.
        This method will use the information provided in the MIndexBufferDescriptor argument to populate the buffer with the desired indexing data.  The descriptor will describe the surface index type, the primitive type, and the data type.  The populateIndexBuffer method will generate a buffer that matches the request.
        The length of the buffer should be at least the as big as the value returned by minimumBufferSize().
        
        * data (buffer) - The buffer you want filled.
        * primitiveCount (int) - The number of primitives you expect to be filled in the buffer.
        * indexDesc (MIndexBufferDescriptor) - The description of the buffer you are requesting.
        """
    
        pass
    
    
    def populateVertexBuffer(*args, **kwargs):
        """
        populateVertexBuffer(data, vertexCount, bufferDesc) -> self
        
        Fill a buffer with vertex data.
        This method will use the information provided in the MVertexBufferDescriptor argument to populate the buffer with the desired vertex data.  The descriptor will describe the buffer's name, semantic, and data type.
        The populateVertexBuffer method will supply a buffer that matches the request.  The length of the buffer should be at least (vertexCount * bufferDesc.stride()).
        Values for normals, tangents and bitangents are all normalized.
        
        * data (buffer) - The buffer you want filled.
        * vertexCount (int) - The vertex count you expect to be filled in the buffer.
        * bufferDesc (MVertexBufferDescriptor) - The description of the buffer you are requesting.
        """
    
        pass
    
    
    def primitiveCount(*args, **kwargs):
        """
        primitiveCount(indexDesc) -> int
        
        Returns the number of primitives (triangles, lines, points, etc.) that will be produced for the given indexing requirements.
        Call this method before calling populateIndexBuffer to determine the minimum size the buffer passed into populateIndexBuffer needs to be.
        
        * indexDesc (MIndexBufferDescriptor) - The description of the index buffer you request the count for.
        """
    
        pass
    
    
    def vertexCount(*args, **kwargs):
        """
        vertexCount() -> int
        
        Returns the number of vertices that will be produced for the vertex requirement.
        Call this method before calling populateVertexBuffer to determine the minimum size the buffer passed into populateVertexBuffer needs to be.
        """
    
        pass
    
    
    def minimumBufferSize(*args, **kwargs):
        """
        minimumBufferSize(primitiveCount, primitive, primitiveStride=0) -> int
        
        Get the minimum buffer size required by populateIndexBuffer().
        
        * primitiveCount (int) - The number of primitives.
        * primitive (int) - The primitive type. See MGeometry.primitiveString() for list of primitive types.
        * primitiveStride (int) - The number of control points in a patch when the type is kPatch.
        """
    
        pass
    
    
    __new__ = None
    
    
    kPolyGeom_BaseMesh = 2
    
    
    kPolyGeom_Normal = 0
    
    
    kPolyGeom_NotSharing = 1


class MSelectionContext(object):
    """
    This class gives control on the viewport 2.0 selection behavior.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    selectionLevel = None
    
    __new__ = None
    
    
    kComponent = 2
    
    
    kNone = 0
    
    
    kObject = 1


class MTexture(object):
    """
    Class which includes texture data.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def bytesPerPixel(*args, **kwargs):
        """
        bytesPerPixel() -> int
        
        Get the number of bytes per pixel in the texture.
        """
    
        pass
    
    
    def hasAlpha(*args, **kwargs):
        """
        hasAlpha() -> bool
        
        Get whether the texture has an alpha channel.
        """
    
        pass
    
    
    def hasTransparentAlpha(*args, **kwargs):
        """
        hasTransparentAlpha() -> bool
        
        Get whether the texture has semi-transparent texels.
        """
    
        pass
    
    
    def hasZeroAlpha(*args, **kwargs):
        """
        hasZeroAlpha() -> bool
        
        Get whether the texture has any texels with an alpha value of 0.0.
        """
    
        pass
    
    
    def name(*args, **kwargs):
        """
        name() -> string
        
        Get the name of the texture.
        """
    
        pass
    
    
    def rawData(*args, **kwargs):
        """
        rawData() -> (long, rowPitch, slicePitch)
        
        Returns a long containing a C++ 'void' pointer which points to the raw data mapped to the texture.
        The caller must deallocate the system memory (using freeRawData()) as the texture itself does not keep any references to it.
        
        * rowPitch [OUT] (int) - The row pitch of the data. It represents the number of bytes of one line of the texture data.
        * slicePitch [OUT] (int) - The slice pitch of the data. It represents the number of bytes of the whole texture data.
        """
    
        pass
    
    
    def resourceHandle(*args, **kwargs):
        """
        resourceHandle() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the texture.
        """
    
        pass
    
    
    def setHasAlpha(*args, **kwargs):
        """
        setHasAlpha(bool) -> self
        
        Specify that the texture has an alpha channel.
        """
    
        pass
    
    
    def setHasTransparentAlpha(*args, **kwargs):
        """
        setHasTransparentAlpha(bool) -> self
        
        Specify that the texture has texels with an alpha value greater than or equal to 0.0 and less than 1.0.
        """
    
        pass
    
    
    def setHasZeroAlpha(*args, **kwargs):
        """
        setHasZeroAlpha(bool) -> self
        
        Specify that the texture has texels with an alpha value of 0.0.
        """
    
        pass
    
    
    def textureDescription(*args, **kwargs):
        """
        textureDescription() -> MTextureDescription
        
        Get texture description.
        """
    
        pass
    
    
    def update(*args, **kwargs):
        """
        update(pixelData, generateMipMaps, rowPitch=0, region=None) -> self
        update(image, generateMipMaps) -> selfupdate(textureNode) -> self
        
        Update the contents of an image with new data.
        
        From pixel data:
        * pixelData (void*) - Data to update the texture with.
        * generateMipMaps (bool) - Indicate if mip-maps levels for the texture be rebuilt.
        * rowPitch (int) The row pitch of the incoming data.
        * region (MTextureUpdateRegion) - Texture sub-region to update. If a None is passed in then the input data is assumed to be updating the entire texture.
        From an image:
        * image (MImage) - Image containing data to update the texture with.
        * generateMipMaps (bool) - Indicate if mip-maps levels for the texture be rebuilt.
        From a texture node:
        * textureNode (MObject) - File texture node
        """
    
        pass
    
    
    def freeRawData(*args, **kwargs):
        """
        freeRawData(long) -> None
        Deallocate system memory - retrieved from rawData().
        """
    
        pass
    
    
    __new__ = None


class MUniformParameterList(object):
    """
    MUniformParameterList specify the list of uniform shader parameters used by a hardware shader, allowing Maya to handle setting up the node and user interfaces to the data, the population and access of cached data, etc.
    """
    
    
    
    def __getitem__(*args, **kwargs):
        """
        x.__getitem__(y) <==> x[y]
        """
    
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __len__(*args, **kwargs):
        """
        x.__len__() <==> len(x)
        """
    
        pass
    
    
    def append(*args, **kwargs):
        """
        append(element) -> bool
        
        Append a new parameter to this end of this list.
        
        * element (MUniformParameter) - The new parameter to append
        """
    
        pass
    
    
    def copy(*args, **kwargs):
        """
        copy(source) -> self
        
        Copy data from source list.
        
        * source (MUniformParameterList) - The source list to copy from
        """
    
        pass
    
    
    def setElement(*args, **kwargs):
        """
        setElement(n, element) -> bool
        
        Set the nth parameter in this list.
        
        * n (int) - The index of the element to set
        * element (MUniformParameter) - The value to set
        """
    
        pass
    
    
    def setLength(*args, **kwargs):
        """
        setLength(length) -> bool
        
        Set the number of parameters in this list. If this is greater than the current number of parameters in the list, the caller is responsible for setting the new parameters to valid values using setElement.
        
        * length (int) - The number of parameters in this list.
        """
    
        pass
    
    
    __new__ = None


class MIntersection(object):
    """
    This class gives a description of an intersection when a selection hit occurs.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    barycentricCoordinates = None
    
    edgeInterpolantValue = None
    
    index = None
    
    instanceID = None
    
    intersectionPoint = None
    
    selectionLevel = None
    
    __new__ = None


class MPxShadingNodeOverride(object):
    """
    Base class for user defined shading node overrides.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def allowConnections(*args, **kwargs):
        """
        allowConnections() -> bool
        
        Returns True if connections should be allowed to parameters of the fragment that do not have custom mappings that
        specifically prevent connections.
        
        An override may prevent Maya from connecting fragments to specific parameters of the fragment for this
        override by providing custom attribute parameter mappings. It is also possible to prevent connections to all
        parameters on the fragment by overriding this method to return False.
        In that case, the fragment for this override will become a final fragment, and nothing will be connected to it.
        This is equivalent to creating an attribute parameter mapping for every parameter on the fragment and setting
        the allowConnection flag on each mapping to False.
        
        This method is called once only, just after creation of the override.
        """
    
        pass
    
    
    def fragmentName(*args, **kwargs):
        """
        fragmentName() -> string
        
        Override this method to return the name of the fragment or fragment graph to use for rendering the shading node associated with this override. This fragment will be automatically connected to the other fragments for the other nodes in the shading network to produce a complete shading effect.
        
        A fragment with the returned name must already exist in the fragment manager for rendering to succeed. If the fragment does not exist, the associated node will not contribute to shading.
        
        The parameter values for the fragment will be automatically populated from the attribute values on the node wherever the name and type of a parameter on the fragment match the name and type of an attribute on the node.
        
        The fragment will only be connected to the other fragments in the graph if the output parameter of the fragment has the same name as the output attribute of the node that is connected to the rest of the shading network. To support multiple output attributes of a node, the fragment should return a "struct" type parameter. The names of the members of the struct should match the names of the output attributes for which support is desired. The fragment must compute all output attributes on every execution.
        
        Returns the name of the fragment to use
        """
    
        pass
    
    
    def getCustomMappings(*args, **kwargs):
        """
        getCustomMappings(mappings) -> self
        
        Maya will automatically match parameters on the shade fragment specified by this override with attributes on the
        associated Maya node as long as the names and types match. In order to specify custom attribute parameter mappings,
        override this method.
        
        This method will be called before Maya performs its automatic matching so it can be used to prevent that process by
        defining mappings for parameters that would normally be mapped automatically.
        Such mappings will take precedence over automatic mappings.
        
        It is an error to provide more than one mapping per fragment parameter.
        Only the first such mapping will be used.
        
        The same attribute may be used for multiple parameters.
        
        By default, this method defines no custom mappings.
        
        * mappings [OUT] (MAttributeParameterMappingList) - An attribute parameter mapping list; fill with any desired custom mappings.
        """
    
        pass
    
    
    def outputForConnection(*args, **kwargs):
        """
        outputForConnection(sourcePlug, destinationPlug) -> string
        
        Returns the name of an output parameter on the fragment for the override.
        
        When Maya attempts to connect the fragment for this override to the fragment for another node in the shading network,
        it will call this method to get the name of the output on the fragment to use for the connection.
        By default, this will simply return the name of the output attribute on the node for the override that is driving the connection.
        Override this method to specify that a different output of the fragment should be used instead.
        This method may also be overridden to get information about how and where the fragment is being connected.
        
        If the output of the fragment is of "struct" type, this method should return the name of one of the members of the struct.
        
        This method is called after getCustomMappings().
        
        If the name returned does not match the name of any output parameter (or struct member in the case of struct output) on the
        fragment for this override then the fragment will not be connected to the overall shading effect.
        
        * sourcePlug (MPlug) - The plug on the node for this override which is the source of the connection.
                               By default the name of the attribute for this plug is returned.
        * destinationPlug (MPlug) - The plug on the node which is the destination of the connection.
        """
    
        pass
    
    
    def supportedDrawAPIs(*args, **kwargs):
        """
        supportedDrawAPIs() -> DrawAPI
        
        Returns the draw API supported by this override.
        """
    
        pass
    
    
    def updateDG(*args, **kwargs):
        """
        updateDG() -> self
        
        This method is called every time Maya needs to update the parameter values on the final shading effect of which the fragment
        produced by this override is a part. In this method implementations should query and cache any values needed for setting
        parameters on the final shading effect in updateShader().
        """
    
        pass
    
    
    def updateShader(*args, **kwargs):
        """
        updateShader(shader, mappings) -> self
        
        This method is called every time Maya needs to update the parameter values on the final shading effect of which the fragment
        produced by this override is a part. Implementations may use the information from the mappings list to set parameter values on
        the shader. The list contains all parameter mappings for the override, both automatic and custom. Although it is possible to set
        the value for any parameter on the shader it is an error to do so for parameters which are not defined by the fragment for this
        override and doing so may result in unpredictable behaviour.
        
        The default implementation does nothing. Note that values for parameters with valid attribute parameter mappings will be set
        automatically. This method need only be overridden if custom behaviour is required.
        
        For performance, consider caching the resolved parameter names of parameters needing update the first time this method is called.
        This will avoid searching the mappings list and then retrieving the resolved name from the mapping on each update. Resolved names
        are guaranteed to remain constant until the next time fragmentName() is called. Const pointers to individual mappings may also be
        cached in this way and are valid for the same duration.
        Do not attempt to cache mappings created in the getCustomMappings() method.
        
        It is an error to attempt to access the Maya dependency graph from within updateShader().
        Any attempt to do so will result in instability. Required data should be retrieved and cached in updateDG().
        
        * shader (MShaderInstance) - The shader instance.
        * mappings (MAttributeParameterMappingList) - The attribute parameter mappings for this override.
        """
    
        pass
    
    
    def valueChangeRequiresFragmentRebuild(*args, **kwargs):
        """
        valueChangeRequiresFragmentRebuild(plug) -> bool
        
        Returns True if a change in attribute values should cause a rebuild of the complete shading effect.
        
        This method will be called by Maya when it detects changes in the attribute values of nodes in the shading network.
        If this method returns True, Maya will assume that the change means that a new configuration of the total fragment graph
        is necessary and it will trigger a rebuild of the complete shading effect. This will cause fragmentName() to be invoked
        again at which point a different fragment name could be returned.
        
        For example, if a texture node has multiple modes, each implemented with a different fragment, then a change to the active
        mode would require the shading effect to be rebuilt in order to switch which fragment is used.
        
        The plug parameter passed in is Maya's best attempt at informing the implementation of what changed. However due to the
        nature of the change management system a single source plug cannot always be determined in which case the plug may be NULL.
        
        The default implementation returns False.
        
        * plug (MPlug) - The plug that changed, may be None.
        """
    
        pass
    
    
    __new__ = None


class MGeometryRequirements(object):
    """
    Geometry requirements.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addIndexingRequirement(*args, **kwargs):
        """
        addIndexingRequirement(MIndexBufferDescriptor) -> self
        
        Add a new indexing requirement to the list of indexing requirements.
        """
    
        pass
    
    
    def addVertexRequirement(*args, **kwargs):
        """
        addVertexRequirement(MVertexBufferDescriptor) -> self
        
        Add a new vertex requirement to the list of vertex requirements.
        """
    
        pass
    
    
    def indexingRequirements(*args, **kwargs):
        """
        indexingRequirements() -> MIndexBufferDescriptorList
        
        Get a list of descriptors that specify the geometry indexing requirements of an object.
        """
    
        pass
    
    
    def vertexRequirements(*args, **kwargs):
        """
        vertexRequirements() -> MVertexBufferDescriptorList
        
        Get a list of descriptors that specify the vertex geometry requirements of this object.
        """
    
        pass
    
    
    __new__ = None


class MUserRenderOperation(MRenderOperation):
    """
    Class which defines a user defined rendering operation.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addUIDrawables(*args, **kwargs):
        """
        addUIDrawables(drawManager, frameContext) -> self
        
        Provides access to the MUIDrawManager, which can be used to queue up operations to draw simple UI shapes like lines, circles, text, etc.
        
        This method will only be called when hasUIDrawables() is overridden to return true.
        
        * drawManager (MUIDrawManager) - The UI draw manager, it can be used to draw some simple geometry including text.
        * frameContext (MFrameContext) - Frame level context information
        """
    
        pass
    
    
    def cameraOverride(*args, **kwargs):
        """
        cameraOverride() -> MCameraOverride
        
        Query for a camera override.
        """
    
        pass
    
    
    def hasUIDrawables(*args, **kwargs):
        """
        hasUIDrawables() -> bool
        
        Query whether addUIDrawables() should be called or not.
        """
    
        pass
    
    
    def requiresLightData(*args, **kwargs):
        """
        requiresLightData() -> bool
        
        Indicates whether light data from the renderer is required for this user operation.
        """
    
        pass
    
    
    __new__ = None


class MQuadRender(MRenderOperation):
    """
    Class which defines a 2d geometry quad render.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def blendStateOverride(*args, **kwargs):
        """
        blendStateOverride() -> MBlendState
        
        Query if a blend state override is performed by this quad operation.
        """
    
        pass
    
    
    def clearOperation(*args, **kwargs):
        """
        clearOperation() -> MClearOperation
        
        Get the scene clear operation.
        """
    
        pass
    
    
    def depthStencilStateOverride(*args, **kwargs):
        """
        depthStencilStateOverride() -> MDepthStencilState
        
        Query if a depth-stencil state override is performed by this quad operation.
        """
    
        pass
    
    
    def rasterizerStateOverride(*args, **kwargs):
        """
        rasterizerStateOverride() -> MRasterizerState
        
        Query if a rasterizer state override is performed by this quad operation.
        """
    
        pass
    
    
    def shader(*args, **kwargs):
        """
        shader() -> MShaderInstance
        
        Get the shader to use when rendering a quad.
        """
    
        pass
    
    
    mClearOperation = None
    
    __new__ = None


class MDrawContext(MFrameContext):
    """
    Class to allow access to hardware draw context information.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def copyCurrentColorRenderTarget(*args, **kwargs):
        """
        copyCurrentColorRenderTarget(string) -> MRenderTarget
        
        Get a copy of the current color render target.
        When the object is no longer needed, MRenderTargetManager::releaseRenderTarget() should be called
        to notify the target manager that the caller is done with the render target.
        """
    
        pass
    
    
    def copyCurrentColorRenderTargetToTexture(*args, **kwargs):
        """
        copyCurrentColorRenderTargetToTexture() -> MTexture
        
        Get a copy of the current color render target as a texture.
        When the texture is no longer needed, MTextureManager::releaseTexture() should be called.
        """
    
        pass
    
    
    def copyCurrentDepthRenderTarget(*args, **kwargs):
        """
        copyCurrentDepthRenderTarget(string) -> MRenderTarget
        
        Get a copy of the current depth render target.
        When the object is no longer needed, MRenderTargetManager::releaseRenderTarget() should be called
        to notify the target manager that the caller is done with the render target.
        """
    
        pass
    
    
    def copyCurrentDepthRenderTargetToTexture(*args, **kwargs):
        """
        copyCurrentDepthRenderTargetToTexture() -> MTexture
        
        Get a copy of the current depth render target as a texture.
        When the texture is no longer needed, MTextureManager::releaseTexture() should be called.
        """
    
        pass
    
    
    def getDepthRange(*args, **kwargs):
        """
        getDepthRange() -> [float, float]
        
        Get the depth range which specifies the mapping of depth values from normalized device coordinates to window coordinates.
        The depth range values are normally 0.0 and 1.0.
        """
    
        pass
    
    
    def getFrameStamp(*args, **kwargs):
        """
        getFrameStamp() -> long
        
        Returns the current frame stamp.
        """
    
        pass
    
    
    def getFrustumBox(*args, **kwargs):
        """
        getFrustumBox() -> MBoundingBox
        
        Get the bounding box of the current view frustum in world space.
        """
    
        pass
    
    
    def getLightInformation(*args, **kwargs):
        """
        getLightInformation(lightNumber, lightFilter=kFilteredToLightLimit) -> [positions, direction, intensity, color, hasDirection, hasPosition]
        
        Return common lighting information for a given active light.
        """
    
        pass
    
    
    def getLightParameterInformation(*args, **kwargs):
        """
        getLightParameterInformation(lightNumber, lightFilter=kFilteredToLightLimit) -> MLightParameterInformation
        
        Return parameter information for a given active light.
        """
    
        pass
    
    
    def getPassContext(*args, **kwargs):
        """
        getPassContext() -> MPassContext
        
        Access the current pass context.
        """
    
        pass
    
    
    def getRenderTargetSize(*args, **kwargs):
        """
        getRenderTargetSize() -> [int, int]
        
        Get the size of the render target (output buffer) being rendered into.
        The dimensions of the target are in pixels
        """
    
        pass
    
    
    def getSceneBox(*args, **kwargs):
        """
        getSceneBox() -> MBoundingBox
        
        Get a bounding box of the scene in world space.
        """
    
        pass
    
    
    def getStateManager(*args, **kwargs):
        """
        getStateManager() -> MStateManager
        
        Access the GPU state manager for the current draw context.
        """
    
        pass
    
    
    def numberOfActiveLights(*args, **kwargs):
        """
        numberOfActiveLights(lightFilter=kFilteredToLightLimit) -> int
        
        Return the number of available lights to render the scene,
        only considering lights which pass the filter option.
        """
    
        pass
    
    
    def viewDirectionAlongNegZ(*args, **kwargs):
        """
        viewDirectionAlongNegZ() -> bool
        
        Return whether the view direction is pointing down the -Z axis.
        """
    
        pass
    
    
    __new__ = None
    
    
    kFilteredIgnoreLightLimit = 1
    
    
    kFilteredToLightLimit = 0


class MPxSurfaceShadingNodeOverride(MPxShadingNodeOverride):
    """
    Base class for user defined surface shading node overrides.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def bumpAttribute(*args, **kwargs):
        """
        bumpAttribute() -> string
        
        Returns the name of the attribute that accepts bump connections from bump nodes.
        
        This method is called after getCustomMappings() to allow the plugin to provide surface-shader specific information.
        If required, the override may return the name of the attribute on the node that accepts connections from bump nodes for
        doing bump or normal mapping (often this is "normalCamera"). A special mapping will be created linking this attribute
        to the parameter named "Nw" (world space normal) on the fragment. The special mapping will ensure that the extra fragments
        needed for bump mapping are set up correctly. If there is no "Nw" parameter on the fragment the mapping will not be created
        and bump mapping will not work for the associated shader.
        
        The default implementation returns the empty string (no bump).
        """
    
        pass
    
    
    def primaryColorParameter(*args, **kwargs):
        """
        primaryColorParameter() -> string
        
        Returns the name of the fragment parameter to use as the primary color.
        
        This method is called just after getCustomMappings() to allow the plugin to provide extra surface shader-specific
        information. If required, the override may return the name of a 3-float parameter on the fragment that should be marked
        as the primary color. If the viewport is set to hide textures (shaded mode) then the specified parameter will be set
        using the "default color" value from the texture which is connected to the associated attribute on the Maya node.
        
        The default implementation returns the empty string (no primary color).
        
        The name must correspond to a parameter on the fragment that is mapped to an attribute on the node either automatically
        or through custom attribute parameter mappings.
        """
    
        pass
    
    
    def transparencyParameter(*args, **kwargs):
        """
        transparencyParameter() -> string
        
        Returns the name of the fragment parameter that should drive transparency.
        
        This method is called just after getCustomMappings() to allow the plugin to provide extra surface shader-specific
        information. If required, the override may return the name of a single float or 3-float parameter on the fragment that
        should be marked as the parameter that drives the transparency of the surface shader. The values of this parameter will
        be watched so that scene objects using this shader will be correctly marked and sorted for transparent drawing.
        
        The default implementation returns the empty string (no transparency).
        
        The name must correspond to a parameter on the fragment that is mapped to an attribute on the node either automatically
        or through custom attribute parameter mappings.
        """
    
        pass
    
    
    __new__ = None


class MHUDRender(MRenderOperation):
    """
    Class which defines rendering the 2D heads-up-display.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addUIDrawables(*args, **kwargs):
        """
        addUIDrawables(drawManager2D, frameContext) -> self
        
        Provides access to the 2D version of MUIDrawManager, which can be used to queue up operations to draw simple UI shapes like lines, circles, text, etc.
        
        This method will only be called when hasUIDrawables() is overridden to return true.
        
        * drawManager2D (MUIDrawManager) - A UI draw manager which can be used to draw simple 2D geometry, including text. When passing coordinates to the draw manager's methods, only X and Y have meaning. The origin (0, 0) is in the lower-left corner of the view.
        * frameContext (MFrameContext) - Frame level context information.
        """
    
        pass
    
    
    def hasUIDrawables(*args, **kwargs):
        """
        hasUIDrawables() -> bool
        
        Query whether addUIDrawables() should be called or not.
        """
    
        pass
    
    
    def name(*args, **kwargs):
        """
        name() -> string
        
        Returns the unique name for a hud render operation.
        Note that all HUD operations share the same name since they need not be distinguished from one another.
        """
    
        pass
    
    
    __new__ = None


class MPresentTarget(MRenderOperation):
    """
    Class which defines the operation of presenting a target for final output.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def presentDepth(*args, **kwargs):
        """
        presentDepth() -> bool
        
        Query whether the present operation will display depth values.
        """
    
        pass
    
    
    def setPresentDepth(*args, **kwargs):
        """
        setPresentDepth(bool) -> self
        
        Set whether the operation will present depth values.
        """
    
        pass
    
    
    def setTargetBackBuffer(*args, **kwargs):
        """
        setTargetBackBuffer(int) -> self
        
        Set the desired back-buffer to use on the output target.
        see MPresentTarget.targetBackBuffer() description for the list of available back-buffers.
        """
    
        pass
    
    
    def targetBackBuffer(*args, **kwargs):
        """
        targetBackBuffer() -> int
        
        Query the desired back-buffer to use on the output target.
        
          MPresentTarget.kCenterBuffer   Default or 'center' buffer
          MPresentTarget.kLeftBuffer     Left back-buffer
          MPresentTarget.kRightBuffer    Right back-buffer
        """
    
        pass
    
    
    __new__ = None
    
    
    kCenterBuffer = 0
    
    
    kLeftBuffer = 1
    
    
    kRightBuffer = 2


class MClearOperation(MRenderOperation):
    """
    Class which defines the operation of clearing render target channels.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def clearColor(*args, **kwargs):
        """
        clearColor() -> [float, float, float, float]
        
        Query the first clear color values.
        """
    
        pass
    
    
    def clearColor2(*args, **kwargs):
        """
        clearColor2() -> [float, float, float, float]
        
        Query the second clear color values.
        """
    
        pass
    
    
    def clearDepth(*args, **kwargs):
        """
        clearDepth() -> float
        
        Query the clear depth value.
        """
    
        pass
    
    
    def clearGradient(*args, **kwargs):
        """
        clearGradient() -> bool
        
        Query if the clear should clear with a vertical color gradient.
        """
    
        pass
    
    
    def clearStencil(*args, **kwargs):
        """
        clearStencil() -> int
        
        Query the stencil clear value.
        """
    
        pass
    
    
    def mask(*args, **kwargs):
        """
        mask() -> int
        
        Query the clear mask.
        """
    
        pass
    
    
    def overridesColors(*args, **kwargs):
        """
        overridesColors() -> bool
        
        Query whether clear colors are set by the override or come from Maya's preferences.
        """
    
        pass
    
    
    def setClearColor(*args, **kwargs):
        """
        setClearColor([float, float, float, float]) -> self
        
        Set the first clear color values.
        """
    
        pass
    
    
    def setClearColor2(*args, **kwargs):
        """
        setClearColor2([float, float, float, float]) -> self
        
        Set the second clear color values.
        """
    
        pass
    
    
    def setClearDepth(*args, **kwargs):
        """
        setClearDepth(float) -> self
        
        Set the clear depth value.
        """
    
        pass
    
    
    def setClearGradient(*args, **kwargs):
        """
        setClearGradient(bool) -> self
        
        Set whether to clear with a vertical color gradient.
        """
    
        pass
    
    
    def setClearStencil(*args, **kwargs):
        """
        setClearStencil(int) -> self
        
        Set the clear stencil value.
        """
    
        pass
    
    
    def setMask(*args, **kwargs):
        """
        setMask(int) -> self
        
        Set the clear mask to define which channels to clear.
        """
    
        pass
    
    
    def setOverridesColors(*args, **kwargs):
        """
        setOverridesColors(bool) -> self
        
        Set the enabled state to control whether the clear operation overrides Maya's color preferences.
        """
    
        pass
    
    
    __new__ = None
    
    
    kClearAll = -1
    
    
    kClearColor = 1
    
    
    kClearDepth = 2
    
    
    kClearNone = 0
    
    
    kClearStencil = 4


class MSceneRender(MRenderOperation):
    """
    Class which defines a scene render.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addPostUIDrawables(*args, **kwargs):
        """
        addPostUIDrawables(drawManager, frameContext) -> self
        
        Provides access to the MUIDrawManager, which can be used to queue up operations to draw simple UI shapes like lines, circles, text, etc.
        
        This method will only be called when hasUIDrawables() is overridden to return true and kRenderPostSceneUIItems is set in the MSceneFilterOption mask returned by renderFilterOverride().
        
        UI drawables added in this method will be rendered after the scene render.
        
        * drawManager (MUIDrawManager) - The UI draw manager, it can be used to draw some simple geometry including text.
        * frameContext (MFrameContext) - Frame level context information
        """
    
        pass
    
    
    def addPreUIDrawables(*args, **kwargs):
        """
        addPreUIDrawables(drawManager, frameContext) -> self
        
        Provides access to the MUIDrawManager, which can be used to queue up operations to draw simple UI shapes like lines, circles, text, etc.
        
        This method will only be called when hasUIDrawables() is overridden to return true and kRenderPreSceneUIItems is set in the MSceneFilterOption mask returned by renderFilterOverride().
        
        UI drawables added in this method will be rendered before the scene render.
        
        * drawManager (MUIDrawManager) - The UI draw manager, it can be used to draw some simple geometry including text.
        * frameContext (MFrameContext) - Frame level context information
        """
    
        pass
    
    
    def cameraOverride(*args, **kwargs):
        """
        cameraOverride() -> MCameraOverride
        
        Query for a camera override.
        """
    
        pass
    
    
    def clearOperation(*args, **kwargs):
        """
        clearOperation() -> MClearOperation
        
        Get the scene clear operation.
        """
    
        pass
    
    
    def cullingOverride(*args, **kwargs):
        """
        cullingOverride() -> int
        
        Query for a face culling override.
        
          MSceneRender.kNoCullingOverride    No culling override
          MSceneRender.kCullNone             Don't perform culling
          MSceneRender.kCullBackFaces        Cull back faces
          MSceneRender.kCullFrontFaces       Cull front faces
        """
    
        pass
    
    
    def displayModeOverride(*args, **kwargs):
        """
        displayModeOverride() -> int
        
        Query for any display mode override.
        
          MSceneRender.kNoDisplayModeOverride  No display mode override
          MSceneRender.kWireFrame              Display wireframe
          MSceneRender.kShade                  Display shaded textured
          MSceneRender.kFlatShaded             Display flat shaded
          MSceneRender.kShadeActiveOnly        Shade active objects. Only applicable if kShade or kFlatShaded is enabled.
          MSceneRender.kBoundingBox            Display bounding boxes
          MSceneRender.kDefaultMaterial        Use default material. Only applicable if kShade or kFlatShaded is enabled.
          MSceneRender.kTextured               Display textured. Only applicable if kShade or kFlatShaded is enabled.
        """
    
        pass
    
    
    def fragmentName(*args, **kwargs):
        """
        fragmentName() -> String
        
        Query the name of the fragment used to render the scene.
        """
    
        pass
    
    
    def getObjectTypeExclusions(*args, **kwargs):
        """
        getObjectTypeExclusions() -> long
        
        Query for any object type exclusions.
        
          MFrameContext.kExcludeNone                 Exclude no object types
          MFrameContext.kExcludeNurbsCurves          Exclude NURBS curves
          MFrameContext.kExcludeNurbsSurfaces        Exclude NURBS surface
          MFrameContext.kExcludeMeshes               Exclude polygonal meshes
          MFrameContext.kExcludePlanes               Exclude planes
          MFrameContext.kExcludeLights               Exclude lights
          MFrameContext.kExcludeCameras              Exclude camera
          MFrameContext.kExcludeJoints               Exclude joints
          MFrameContext.kExcludeIkHandles            Exclude IK handles
          MFrameContext.kExcludeDeformers            Exclude all deformations
          MFrameContext.kExcludeDynamics             Exclude all dynamics objects (emiters, cloth)
          MFrameContext.kExcludeParticleInstancers   Exclude all Particle Instancers
          MFrameContext.kExcludeLocators             Exclude locators
          MFrameContext.kExcludeDimensions           Exclude all measurement objects
          MFrameContext.kExcludeSelectHandles        Exclude selection handles
          MFrameContext.kExcludePivots               Exclude pivots
          MFrameContext.kExcludeTextures             Exclude texure placement objects
          MFrameContext.kExcludeGrid                 Exclude grid drawing
          MFrameContext.kExcludeCVs                  Exclude NURBS control vertices
          MFrameContext.kExcludeHulls                Exclude NURBS hulls
          MFrameContext.kExcludeStrokes              Exclude PaintFX strokes
          MFrameContext.kExcludeSubdivSurfaces       Exclude subdivision surfaces
          MFrameContext.kExcludeFluids               Exclude fluid objects
          MFrameContext.kExcludeFollicles            Exclude hair follicles
          MFrameContext.kExcludeHairSystems          Exclude hair system
          MFrameContext.kExcludeImagePlane           Exclude image planes
          MFrameContext.kExcludeNCloths              Exclude N-cloth objects
          MFrameContext.kExcludeNRigids              Exclude rigid-body objects
          MFrameContext.kExcludeDynamicConstraints   Exclude rigid-body constraints
          MFrameContext.kExcludeManipulators         Exclude manipulators
          MFrameContext.kExcludeNParticles           Exclude N-particle objects
          MFrameContext.kExcludeMotionTrails         Exclude motion trails
          MFrameContext.kExcludeHoldOuts                                Exclude Hold-Outs
          MFrameContext.kExcludePluginShapes                    Exclude plug-in shapes
          MFrameContext.kExcludeHUD                                 Exclude HUD
          MFrameContext.kExcludeClipGhosts                      Exclude animation clip ghosts
          MFrameContext.kExcludeGreasePencils           Exclude grease-pencil draw
          MFrameContext.kExcludeAll                  Exclude all listed object types
        """
    
        pass
    
    
    def getParameters(*args, **kwargs):
        """
        getParameters() -> MRenderParameters
        
        Method to return the operation's parameter set.
        """
    
        pass
    
    
    def hasUIDrawables(*args, **kwargs):
        """
        hasUIDrawables() -> bool
        
        Query whether addUIDrawables() should be called or not.
        """
    
        pass
    
    
    def lightModeOverride(*args, **kwargs):
        """
        lightModeOverride() -> int
        
        Query for any lighting mode override.
        
          MSceneRender.kNoLightingModeOverride  No lighting mode override
          MSceneRender.kNoLight                 Use no light
          MSceneRender.kAmbientLight            Use global ambient light
          MSceneRender.kLightDefault            Use default light
          MSceneRender.kSelectedLights          Use lights which are selected
          MSceneRender.kSceneLights             Use all lights in the scene
        """
    
        pass
    
    
    def objectSetOverride(*args, **kwargs):
        """
        objectSetOverride() -> MSelectionList
        
        Query for override for the set of objects to view.
        
        Visibility takes into account the current states of each object, any displayfilters, and camera frustum culling.
        
        Note that the override only applies to rendering but not selection.
        
        By default NULL is returned which indicates that no override is present.
        """
    
        pass
    
    
    def objectTypeExclusions(*args, **kwargs):
        """
        objectTypeExclusions() -> int
        
        Query for any object type exclusions.
        Refer to the MObjectTypeExclusions enumeration on MSceneRender for possible values
        
        This method is deprecated. Use getObjectTypeExclusions instead.
        """
    
        pass
    
    
    def postEffectsOverride(*args, **kwargs):
        """
        postEffectsOverride() -> int
        
        Query for post effects override.
        
          MSceneRender.kPostEffectDisableNone        Use current render settings options
          MSceneRender.kPostEffectDisableSSAO        Disable SSAO post effect
          MSceneRender.kPostEffectDisableMotionBlur  Disable motion blur post effect
          MSceneRender.kPostEffectDisableDOF         Disable depth-of-field post effect
          MSceneRender.kPostEffectDisableAll         Disable all post effects
        """
    
        pass
    
    
    def postRender(*args, **kwargs):
        """
        postRender() -> self
        
        Method to allow for the operation to clean up itself after being executed.
        
        By default this method performs no action
        """
    
        pass
    
    
    def postSceneRender(*args, **kwargs):
        """
        postSceneRender(context) -> self
        
        Method to allow for the operation to update itself after a scene rendering ends.
        
        This method will be called after computing shadow maps, and after a color pass.
        
        * context (MDrawContext) - Draw context after rendering has completed
        
        By default this method performs no action
        """
    
        pass
    
    
    def preRender(*args, **kwargs):
        """
        preRender() -> self
        
        Method to allow for the operation to update itself before being executed. In general this would be used to update any operation parameters.
        
        
        No context information is available at this point.
        
        By default this method performs no action
        """
    
        pass
    
    
    def preSceneRender(*args, **kwargs):
        """
        preSceneRender(context) -> self
        
        Method to allow for the operation to update itself before a scene rendering begins.
        
        This method will be called before computing shadow maps, and before a color pass.
        
        * context (MDrawContext) - Draw context before rendering begins
        
        By default this method performs no action
        """
    
        pass
    
    
    def renderFilterOverride(*args, **kwargs):
        """
        renderFilterOverride() -> int
        
        Query which elements of a scene render will be drawn based on semantic meaning.
        
          MSceneRender.kNoSceneFilterOverride
          MSceneRender.kRenderPreSceneUIItems             Render UI items before scene render like grid or user added pre-scene UI items
          MSceneRender.kRenderOpaqueShadedItems           Render only opaque shaded objects but not their wireframe or components
          MSceneRender.kRenderTransparentShadedItems      Render only transparent shaded objects but not their wireframe or components
          MSceneRender.kRenderShadedItems                         Render only shaded (opaque and transparent) objects but not their wireframe or components
          MSceneRender.kRenderPostSceneUIItems            Render UI items after scene render like wireframe and components for surfaces as well as non-surface objects.
          MSceneRender.kRenderUIItems                             kRenderPreSceneUIItems | kRenderPostSceneUIItems
          MSceneRender.kRenderAllItems                            Render all items.
        """
    
        pass
    
    
    def shaderOverride(*args, **kwargs):
        """
        shaderOverride() -> MShaderInstance
        
        Query for a scene level shader override.
        """
    
        pass
    
    
    def shadowEnableOverride(*args, **kwargs):
        """
        shadowEnableOverride() -> bool/None
        
        Query for shadow display override.
        By default a None value is returned indicating that no override is specified.
        """
    
        pass
    
    
    mClearOperation = None
    
    __new__ = None
    
    
    kAmbientLight = 2
    
    
    kBoundingBox = 16
    
    
    kCullBackFaces = 2
    
    
    kCullFrontFaces = 3
    
    
    kCullNone = 1
    
    
    kDefaultMaterial = 32
    
    
    kExcludeAll = -1
    
    
    kExcludeCVs = 131072
    
    
    kExcludeCameras = 32
    
    
    kExcludeDeformers = 256
    
    
    kExcludeDimensions = 4096
    
    
    kExcludeDynamicConstraints = 134217728
    
    
    kExcludeDynamics = 512
    
    
    kExcludeFluids = 2097152
    
    
    kExcludeFollicles = 4194304
    
    
    kExcludeGrid = 65536
    
    
    kExcludeHairSystems = 8388608
    
    
    kExcludeHoldOuts = -2147483648
    
    
    kExcludeHulls = 262144
    
    
    kExcludeIkHandles = 128
    
    
    kExcludeImagePlane = 16777216
    
    
    kExcludeJoints = 64
    
    
    kExcludeLights = 16
    
    
    kExcludeLocators = 2048
    
    
    kExcludeManipulators = 268435456
    
    
    kExcludeMeshes = 4
    
    
    kExcludeMotionTrails = 1073741824
    
    
    kExcludeNCloths = 33554432
    
    
    kExcludeNParticles = 536870912
    
    
    kExcludeNRigids = 67108864
    
    
    kExcludeNone = 0
    
    
    kExcludeNurbsCurves = 1
    
    
    kExcludeNurbsSurfaces = 2
    
    
    kExcludeParticleInstancers = 1024
    
    
    kExcludePivots = 16384
    
    
    kExcludePlanes = 8
    
    
    kExcludeSelectHandles = 8192
    
    
    kExcludeStrokes = 524288
    
    
    kExcludeSubdivSurfaces = 1048576
    
    
    kExcludeTextures = 32768
    
    
    kFlatShaded = 4
    
    
    kLightDefault = 3
    
    
    kNoCullingOverride = 0
    
    
    kNoDisplayModeOverride = 0
    
    
    kNoLight = 1
    
    
    kNoLightingModeOverride = 0
    
    
    kNoSceneFilterOverride = 0
    
    
    kPostEffectDisableAll = -1
    
    
    kPostEffectDisableDOF = 4
    
    
    kPostEffectDisableMotionBlur = 2
    
    
    kPostEffectDisableNone = 0
    
    
    kPostEffectDisableSSAO = 1
    
    
    kRenderAllItems = -1
    
    
    kRenderNonShadedItems = 9
    
    
    kRenderOpaqueShadedItems = 2
    
    
    kRenderPostSceneUIItems = 8
    
    
    kRenderPreSceneUIItems = 1
    
    
    kRenderShadedItems = 6
    
    
    kRenderTransparentShadedItems = 4
    
    
    kRenderUIItems = 9
    
    
    kSceneLights = 5
    
    
    kSelectedLights = 4
    
    
    kShadeActiveOnly = 8
    
    
    kShaded = 2
    
    
    kTextured = 64
    
    
    kWireFrame = 1



