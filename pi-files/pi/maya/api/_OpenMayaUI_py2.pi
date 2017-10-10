class MTextureEditorDrawInfo(object):
    """
    Drawing state for drawing to the UV texture window with custom shapes.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    drawingFunction = None
    
    __new__ = None
    
    
    kDrawEdgeForSelect = 4
    
    
    kDrawEverything = 2
    
    
    kDrawFacetForSelect = 5
    
    
    kDrawFunctionFirst = 1
    
    
    kDrawFunctionLast = 6
    
    
    kDrawUVForSelect = 6
    
    
    kDrawVertexForSelect = 3
    
    
    kDrawWireframe = 1


class MPxSurfaceShapeUI(object):
    """
    Base class for the UI portion of all user defined shapes.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def canDrawUV(*args, **kwargs):
        """
        canDrawUV() -> bool
        
        Called by Maya to determine if this surface shape supports UV drawing.
        """
    
        pass
    
    
    def drawUV(*args, **kwargs):
        """
        drawUV(view, info) -> self
        
        This method is called when the surface shape is selected and the texture view is open.  Users should override this method if their custom shape supports UVs.
        
        * view (M3dView) - Texture view in which to draw UVs.
        * info (MTextureEditorDrawInfo) - Drawing parameters.
        """
    
        pass
    
    
    def material(*args, **kwargs):
        """
        material(path) -> MMaterial
        
        COMMENT
        """
    
        pass
    
    
    def materials(*args, **kwargs):
        """
        materials(path, componentFilter, materials, componentSet=None) -> self
        
        Returns the material associated with this shape.
        The user must supply a DAG path as a shape can have several materials if instanced.
        
        * path (MDagPath) - the path for which to get the material
        """
    
        pass
    
    
    def select(*args, **kwargs):
        """
        select(selectInfo, selectionList, worldSpaceSelectPts) -> bool
        
        This routine must be overriden if the shape is to support interactive object and/or component selection. The implementation of this method should call selectInfo.addSelection with information about the selected item and its selection mask. For single click selection, detected using the selectInfo.singleSection() method, the hit point should also be passed as an argument to selectInfo.addSelection().
        
        Returns True if something was selected.
        
        * selectInfo (MSelectInfo) - the Selection state information.
        * selectionList [OUT] (MSelectionList) - List of items selected by this method. Do not update directly: use MSelectInfo.addSelection instead.
        * worldSpaceSelectPts [OUT] (MPointArray) - List of points used to sort corresponding selections in single-select mode. (Closest to camera wins.) Do not update directly: use MSelectInfo.addSelection instead.
        """
    
        pass
    
    
    def selectUV(*args, **kwargs):
        """
        selectUV(view, selType, xmin, ymin, xmax, ymax, singleSelect, selList) -> bool
        
        This method is called when the user performs a selection within the texture view.  The method is called only when the surface shape is member of the active selection list.
        
        Maya provides the current viewport instance, the type of the selection, the extents of the selection rectangle (in viewport coordinates), and if the selection mode is single selection. The API user is expected to fill the selection list and return a result of True if 'something was selected'.
        
        To properly use this method, you must make sure that you have a valid component type that Maya can recognize. Selection tests can be done using a pick buffer or by spatially determining the selected objects.
        
        Currently Maya does not know how to manipulate custom UV components. This method only provides the facilities to visualize what has been selected in the viewport.  The API user is responsible for implementing commands that can manipulate the currently selected UVs.
        
        Returns True if something was selected.
        
        * view (M3dView) - the texture drawing view
        * selType (int) - the selection type
        * xmin (int) - minimum x coordinate value of the selection rectangle.
        * ymin (int) - minimum y coordinate value of the selection rectangle.
        * xmax (int) - maximum x coordinate value of the selection rectangle.
        * ymax (int) - maximum y coordinate value of the selection rectangle.
        * singleSelect (bool) - indicates if the user is in single selection mode.
        * selList [OUT] (MSelectionList) - the selection list to be populated.
        
        Valid selection types:
          kSelectMeshUVs      The UV selection type is UVs.
          kSelectMeshVerts    The UV selection type is vertices.
          kSelectMeshFaces    The UV selection type is faces.
          kSelectMeshEdges    The UV selection type is edges.
        """
    
        pass
    
    
    def snap(*args, **kwargs):
        """
        snap(snapInfo) -> bool
        
        Maya calls this method when snapping to the shape's vertices.
        If you wish your custom shape to support point snapping then you must override this method and have it call snapInfo's MSelectInfo.setSnapPoint() method to set the point to be snapped to.
        If setSnapPoint() is called multiple times then the point closest to the cursor will be used.
        
        Returns True if a vertex was found to be snapped to was selected.
        
        * snapInfo (MSelectInfo) - the Selection state information.
        """
    
        pass
    
    
    def surfaceShape(*args, **kwargs):
        """
        surfaceShape() -> MPxSurfaceShape
        
        Returns the non-ui shape associated with current instance.
        """
    
        pass
    
    
    def surfaceShapeUI(*args, **kwargs):
        """
        surfaceShapeUI(path) -> MPxSurfaceShapeUI
        
        This is a static method that can be used to find the corresponding MPxSurfaceShapeUI for the specified path.  If an MPxSurfaceShapeUI does not exist then one is created.
        
        This function can only be used for custom surface shapes and the function will return NULL if the provided path is not a custom surface shape.
        
        * path (MDagPath) - The full path to a surface shape, including the shape.
        """
    
        pass
    
    
    __new__ = None
    
    
    kSelectMeshEdges = 3
    
    
    kSelectMeshFaces = 2
    
    
    kSelectMeshUVs = 0
    
    
    kSelectMeshVerts = 1


class _MFnBase(object):
    """
    Base class for function sets.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def hasObj(*args, **kwargs):
        """
        Returns True if the function set is compatible with the specified Maya object.
        """
    
        pass
    
    
    def object(*args, **kwargs):
        """
        Returns a reference to the object to which the function set is currently attached, or MObject.kNullObj if none.
        """
    
        pass
    
    
    def setObject(*args, **kwargs):
        """
        Attaches the function set to the specified Maya object.
        """
    
        pass
    
    
    def type(*args, **kwargs):
        """
        Returns the type of the function set.
        """
    
        pass
    
    
    __new__ = None


class MDrawRequest(object):
    """
    This class encapsulates all the information needed to fulfill a request to draw an object or part of an object.
    This class is used by the draw methods of MPxSurfaceShapeUI derived objects.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def planeColor(*args, **kwargs):
        """
        planeColor(table) -> int
        
        Get which color is used for the specified color table.
        
        * table (int) - color table
        
        See M3dView.colorAtIndex() for a list of color tables.
        """
    
        pass
    
    
    def setPlaneColor(*args, **kwargs):
        """
        setPlaneColor(value, table) -> self
        
        Set which color to use for the specified color table.
        
        * value (int) - index into the color table
        * table (int) - color table
        
        See M3dView.colorAtIndex() for a list of color tables.
        """
    
        pass
    
    
    color = None
    
    component = None
    
    displayCullOpposite = None
    
    displayCulling = None
    
    displayStatus = None
    
    displayStyle = None
    
    drawData = None
    
    drawLast = None
    
    isTransparent = None
    
    material = None
    
    matrix = None
    
    multiPath = None
    
    token = None
    
    view = None
    
    __new__ = None


class RenderParameters(object):
    """
    Provides information on how to render the image.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    baseColor = None
    
    showAlphaMask = None
    
    unfiltered = None
    
    __new__ = None


class MMaterialArray(object):
    """
    An array of MMaterial.
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
        append(element) -> self
        
        Adds a new element to the end of the array.
        
        * element (MMaterial) - the value for the new last element.
        """
    
        pass
    
    
    def clear(*args, **kwargs):
        """
        clear() -> self
        
        Clear the contents of the array. After this operation the length will be 0.  This does not change the amount of memory allocated to the array, only the number of valid elements in it.
        """
    
        pass
    
    
    def copy(*args, **kwargs):
        """
        copy(source) -> self
        
        Copy the contents of the source array to this array.
        
        * source (MMaterialArray) - array to copy from.
        """
    
        pass
    
    
    def insert(*args, **kwargs):
        """
        insert(element, index) -> self
        
        Inserts a new value into the array at the given index. The initial element at that index, and all following elements, are shifted towards the last.
        
        * element (MMaterial) - the new value to insert into the array.
        * index (int) - the index of the element to set.
        """
    
        pass
    
    
    def remove(*args, **kwargs):
        """
        remove(index) -> self
        
        Removes the element in the array at the given index.
        
        * index (int) - the index of the element to remove.
        """
    
        pass
    
    
    def set(*args, **kwargs):
        """
        set(element, index) -> self
        
        Sets the value of the specified element to the given attribute spec.
        
        * element (MMaterial) - the new value for the specified element.
        * index (int) - the index of the element to be set.
        """
    
        pass
    
    
    def setLength(*args, **kwargs):
        """
        setLength(length) -> self
        
        Set the length of the array. This will grow and shrink the array as desired. Elements that are grown have uninitialized values, while those which are shrunk will lose the data contained in the deleted elements
        
        * length (int) - the new size of the array.
        """
    
        pass
    
    
    sizeIncrement = None
    
    __new__ = None


class M3dView(object):
    """
    M3dView provides methods for working with 3D model views.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def beginGL(*args, **kwargs):
        """
        beginGL() -> self
        
        Setup port for native OpenGL drawing calls.
        """
    
        pass
    
    
    def beginProjMatrixOverride(*args, **kwargs):
        """
        beginProjMatrixOverride(projectionMatrix) -> self
        
        Begin overriding the projection matrix used in openGL drawing.
        This override is enabled until endProjMatrixOverride() is called.
        
        * projectionMatrix (MMatrix) - Projection matrix used in openGL drawing
        """
    
        pass
    
    
    def beginSelect(*args, **kwargs):
        """
        beginSelect(buffer=None, size=0) -> self
        
        Start selecting. The buffer passed is used to record selection hits.
        
        * buffer (bytearray) - OpenGl pick buffer
        * size (int) - Buffer size
        """
    
        pass
    
    
    def beginXorDrawing(*args, **kwargs):
        """
        beginXorDrawing(drawOrthographic=True, disableDepthTesting=True, lineWidth=1.0, stipplePattern=kStippleNone, lineColor=MColor(1, 1, 1)) -> self
        
        Setup the context for exclusive-or (XOR) drawing.
        
        In XOR drawing the color values of the pixels being drawn is exclusive-ored with the color values already present in the view. The advantage of this is that exclusive-oring the same pixels with the same color values a second time will restore the pixels to their original colors, making it possible to temporarily display and erase lines without having to redraw the entire view. This makes XOR drawing particularly useful for drawing guidelines for tools.
        
        One disadvantage of XOR drawing is that the final color after the exclusive-or will not match your drawing color, except when the original color of the pixel was black. For example, XORing a white line across a red background will result in a cyan line and XORing it across a changing background will result in a line of changing colors. However in most situations where you would use XOR drawing the color of the lines is irrelevant just so long as they are visible.
        
        It is an error to call beginXorDrawing() again before calling endXorDrawing() first.
        
        * drawOrthographic (bool) - Draw using orthographic projection. Default is True.
        * disableDepthTesting (bool) - Disable depth testing during draw. Default is True.
        * lineWidth (float) - Set up line width. Default is 1.
        * stipplePattern (int) - Line stipple pattern. Default is kStippleNone.
        * lineColor (MColor) - Line color. Default is white (1,1,1).
        
        Valid stipple patterns:
          kStippleNone      No stipple. Solid line
          kStippleDashed    Dashed line stipple
        """
    
        pass
    
    
    def colorAtIndex(*args, **kwargs):
        """
        colorAtIndex(index, table=kActiveColors) -> MColor
        
        Returns the value of the color at the given index in the application's color table.
        
        
        * index (int) - Index of the color to retrieve
        * table (int) - Table to index into
        
        Valid color tables:
          kActiveColors        Colors for active objects
          kDormantColors       Colors for dormant objects
          kTemplateColor       Colors for templated objects
          kBackgroundColor     Colors for background color
        """
    
        pass
    
    
    def colorMask(*args, **kwargs):
        """
        colorMask() -> [bool, bool, bool, bool]
        
        Get the current color mask
        """
    
        pass
    
    
    def disallowPolygonOffset(*args, **kwargs):
        """
        disallowPolygonOffset() -> bool
        
        Returns the current state of the disallow polygon offset bit.  See setDisallowPolygonOffset for more information.
        """
    
        pass
    
    
    def display(*args, **kwargs):
        """
        display() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the OpenGL context for this view.
        On 32-bit OS X this is an AGLContext.
        On 64-bit OS X this is an NSOpenGLContext pointer.
        On Windows this is an HGLRC.
        """
    
        pass
    
    
    def displayStyle(*args, **kwargs):
        """
        displayStyle() -> int
        
        Return the display style for this 3d view.  kBoundingBox     Bounding box display.
          kFlatShaded      Flat shaded display.
          kGouraudShaded   Gouraud shaded display.
          kWireFrame       Wire frame display.
          kPoints          Points only display.
        """
    
        pass
    
    
    def drawText(*args, **kwargs):
        """
        drawText(text, position, textPosition=kLeft) -> self
        
        Draws the given text at the given spot in the default font.  This method is provided as a convienient way to draw OpenGL text.
        
        * text (string) - Text to draw
        * position (MPoint) - Position in space to draw at
        * textPosition (int) - Text position relative to the point
        
        Valid textPosition values:
          kLeft      Draw text to the left of the point
          kCenter    Draw text centered around the point
          kRight     Draw text to the right of the point
        """
    
        pass
    
    
    def endGL(*args, **kwargs):
        """
        endGL() -> self
        
        End OpenGL drawing.
        """
    
        pass
    
    
    def endProjMatrixOverride(*args, **kwargs):
        """
        endProjMatrixOverride() -> self
        
        End projection matrix override enabled by beginProjMatrixOverride().
        """
    
        pass
    
    
    def endSelect(*args, **kwargs):
        """
        endSelect() -> int
        
        Finish a selection sequence. Result is stored in the buffer passed  in the beginSelect call.
        """
    
        pass
    
    
    def endXorDrawing(*args, **kwargs):
        """
        endXorDrawing() -> self
        
        Reset the context to non-exclusive-or (non-XOR) screen drawing.
        
        If endXorDrawing() is called without first calling beginXorDrawing() an error will result.
        """
    
        pass
    
    
    def filteredObjectList(*args, **kwargs):
        """
        filteredObjectList() -> MSelectionList
        
        Returns a selection list containing all of the objects that remain after filtering is applied to the view.
        """
    
        pass
    
    
    def getCamera(*args, **kwargs):
        """
        getCamera() -> MDagPath
        
        Get the camera for this view.
        """
    
        pass
    
    
    def getColorIndexAndTable(*args, **kwargs):
        """
        getColorIndexAndTable(glindex) -> [int, int]
        
        Returns the index and color table representing the given OpenGL color-index value. This method is useful when converting color indices obtained from glReadPixels(GL_COLOR_INDEX) to Maya color-index values suitable for use with the colorAtIndex and setDrawColor methods.
        
        * glindex (int) - Value of the OpenGL color-index to retrieve
        """
    
        pass
    
    
    def getLightCount(*args, **kwargs):
        """
        getLightCount(visible=True) -> int
        
        Get the number of lights for the view.
        
        * visible (bool) - Specify whether to count visible lights only. By Default this is set True.
        """
    
        pass
    
    
    def getLightIndex(*args, **kwargs):
        """
        getLightIndex(lightNumber) -> int
        
        Get the internal light index for a given light number
        
        * lightNumber (int) - Number of the light interested in
        """
    
        pass
    
    
    def getLightPath(*args, **kwargs):
        """
        getLightPath(lightNumber) -> MDagPath
        
        Get the path to a certain light.
        
        * lightNumber (int) - Number of the light interested in
        """
    
        pass
    
    
    def getLightingMode(*args, **kwargs):
        """
        getLightingMode() -> int
        
        Get the current lighting mode for the view:
          kLightAll         All lights
          kLightSelected    Selected lights
          kLightActive      Active lights
          kLightDefault     Default light
          kUnused1          Not currently used in Maya
          kLightNone        No lights / lighting disabled
        """
    
        pass
    
    
    def getRendererName(*args, **kwargs):
        """
        getRendererName() -> int
        
        Get the name of the current renderer being used for drawing to this view:
          kDefaultQualityRenderer   Equivalent to when the renderer name is "base_OpenGL_Renderer" when queried from the "modelEditor" command
          kHighQualityRenderer      Equivalent to when the renderer name is "hwRender_OpenGL_Renderer" when queried from the "modelEditor" command
          kViewport2Renderer        Equivalent to the viewport 2.0 renderer
          kExternalRenderer         An externally defined renderer name has been set.
        """
    
        pass
    
    
    def getScreenPosition(*args, **kwargs):
        """
        getScreenPosition() -> [int, int]
        
        Returns the current position of this view window in screen coordinates.
        
        This is useful for finding out the exact location of the window as it appears on the screen. These values are in UI coordinate space so the y value increases from bottom to top.
        """
    
        pass
    
    
    def initNames(*args, **kwargs):
        """
        initNames() -> self
        
        Reset the name stack. Valid only when beginSelect() has been called.
        """
    
        pass
    
    
    def isLightVisible(*args, **kwargs):
        """
        isLightVisible(lightNumber) -> bool
        
        Find out if a light is visible in the view
        
        * lightNumber (int) - Number of the light interested in
        """
    
        pass
    
    
    def isShadeActiveOnly(*args, **kwargs):
        """
        isShadeActiveOnly() -> bool
        
        Returns True if this view's display style is shaded for objects that are active and wireframe otherwise.
        """
    
        pass
    
    
    def isVisible(*args, **kwargs):
        """
        isVisible() -> bool
        
        Returns True if this viewport is visible.
        """
    
        pass
    
    
    def loadName(*args, **kwargs):
        """
        loadName(int) -> self
        
        Replace the top of the name stack with the given name. Valid only when beginSelect() has been called.
        
        * name (int) - Name to be loaded onto the top of the stack.
        """
    
        pass
    
    
    def modelViewMatrix(*args, **kwargs):
        """
        modelViewMatrix() -> MMatrix
        
        Returns the modelview matrix currently being used by OpenGL in the current view
        """
    
        pass
    
    
    def multipleDrawEnabled(*args, **kwargs):
        """
        multipleDrawEnabled() -> bool
        
        This method returns the multiple draw enable state for this view.
        """
    
        pass
    
    
    def multipleDrawPassCount(*args, **kwargs):
        """
        multipleDrawPassCount() -> int
        
        This method returns the number of multiple draw passes that are going to be made. By default a 1 is returned.
        """
    
        pass
    
    
    def numActiveColors(*args, **kwargs):
        """
        numActiveColors() -> int
        
        Returns the number of active object colors in the internal application color table.
        """
    
        pass
    
    
    def numDormantColors(*args, **kwargs):
        """
        numDormantColors() -> int
        
        Returns the number of dormant object colors in the internal application color table.
        """
    
        pass
    
    
    def numUserDefinedColors(*args, **kwargs):
        """
        numUserDefinedColors() -> int
        
        Returns the number of user defined colors in the internal application color table.  These colors may be changed by the user and assigned to specific objects.  See the methods of MFnDagNode for information on assigning user defined colors to individual objects.
        
        The user defined colors are not a color table of their own.  They exist in the active and dormant color tables.
        """
    
        pass
    
    
    def objectDisplay(*args, **kwargs):
        """
        objectDisplay() -> int
        
        Returns a display object mask that indicates which object types are drawn in the current view:
          kDisplayEverything            Show everything
          kDisplayNurbsCurves           Show nurbs curves
          kDisplayNurbsSurfaces         Show nurbs surfaces
          kDisplayMeshes                Show meshes
          kDisplayPlanes                Show planes
          kDisplayLights                Show lights
          kDisplayCameras               Show camera
          kDisplayJoints                Show joints
          kDisplayIkHandles             Show IK handles
          kDisplayDeformers             Show deformers
          kDisplayDynamics              Show dynamics
          kDisplayLocators              Show locators
          kDisplayDimensions            Show dimensions
          kDisplaySelectHandles         Show selection handles
          kDisplayPivots                Show pivots
          kDisplayTextures              Show textures
          kDisplayGrid                  Show the grid
          kDisplayCVs                   Show NURBS CVs
          kDisplayHulls                 Show NURBS hulls
          kDisplayStrokes               Show strokes
          kDisplaySubdivSurfaces        Show subdivision surfaces
          kDisplayFluids                Show fluids
          kDisplayFollicles             Show follcles
          kDisplayHairSystems           Show hair systems
          kDisplayImagePlane            Show image plane
          kDisplayNCloths               Show nCloths
          kDisplayNRigids               Show nRigids
          kDisplayDynamicConstraints    Show nDynamicConstraints
          kDisplayManipulators          Show Manipulators
          kDisplayNParticles            Show nParticles
          kExcludeMotionTrails          Show motion trails
          kExcludePluginShapes          Show plugin shapes
        """
    
        pass
    
    
    def objectListFilterName(*args, **kwargs):
        """
        objectListFilterName() -> string
        
        Get the current object list filter name. If none then an emptystring will be returned.
        """
    
        pass
    
    
    def playblastPortHeight(*args, **kwargs):
        """
        playblastPortHeight() -> int
        
        Returns the port height of current playblast.
        Valid only when playblast command has been called.
        Otherwise, an invalid value 0 is returned.
        """
    
        pass
    
    
    def playblastPortWidth(*args, **kwargs):
        """
        playblastPortWidth() -> int
        
        Returns the port width of current playblast.
        Valid only when playblast command has been called.
        Otherwise, an invalid value 0 is returned.
        """
    
        pass
    
    
    def pluginObjectDisplay(*args, **kwargs):
        """
        pluginObjectDisplay(pluginDisplayFilter) -> bool
        
        Returns True if the plugin display filter specified by the pluginDisplayFilter is enabled in the current view.
        
        * pluginDisplayFilter (string) - The name of the plugin display filter.
        """
    
        pass
    
    
    def popName(*args, **kwargs):
        """
        popName() -> self
        
        Removes the top of the name stack. Valid only when beginSelect() has been called.
        """
    
        pass
    
    
    def popViewport(*args, **kwargs):
        """
        popViewport() -> self
        
        Pops the current viewport off of the viewport stack.
        """
    
        pass
    
    
    def portHeight(*args, **kwargs):
        """
        portHeight() -> int
        
        Returns the height of the current viewport.
        """
    
        pass
    
    
    def portWidth(*args, **kwargs):
        """
        portWidth() -> int
        
        Returns the width of the current viewport.
        """
    
        pass
    
    
    def projectionMatrix(*args, **kwargs):
        """
        projectionMatrix() -> MMatrix
        
        Returns the projection matrix currently being used by OpenGL in the current view
        """
    
        pass
    
    
    def pushName(*args, **kwargs):
        """
        pushName(int) -> self
        
        Pushes a new name on the name stack. Valid only when beginSelect() has been called.
        
        * name (int) - Name to be loaded onto the top of the stack.
        """
    
        pass
    
    
    def pushViewport(*args, **kwargs):
        """
        pushViewport(x, y, width, height) -> self
        
        Set the current viewport dimensions. Will keep track of the last viewport dimensions on a stack.
        When finished with this viewport, the current dimensions should be removed from the top of stack using M3dView.popViewport().
        
        * x (int) - Lower left corner of viewport (x coordinate).
        * y (int) - Lower left corner of viewport (y coordinate).
        * width (int) - Width of the viewport.
        * height (int) - Height of the viewport.
        """
    
        pass
    
    
    def readBufferTo2dTexture(*args, **kwargs):
        """
        readBufferTo2dTexture(x, y, width, height) -> self
        
        Read the depth values from the frame buffer for a given view into a predefined OpenGL 2d texture. It is assumed that such a texture has been created and bound before making this call.
        
        * x (int) - Start position x to read.
        * y  (int) - Start position y to read.
        * width (int) - Number of pixels in x to read.
        * height (int) - Number of pixels in y to read.
        """
    
        pass
    
    
    def readColorBuffer(*args, **kwargs):
        """
        readColorBuffer(image, readRGBA=False) -> self
        
        Read the RGB values from the frame buffer for a given view.
        The buffer is read in a pixel format which is BGRA by default, such that each channel is one byte in size.
        
        * image (MImage) - The image contains the frame buffer pixels.
        * readRGBA (bool) - Read the image back in RGBA format. By default the format is BGRA.
        """
    
        pass
    
    
    def readDepthMap(*args, **kwargs):
        """
        readDepthMap(x, y, width, heigth, bufferPtr, depthMapPrecision) -> self
        
        Read the depth values from the frame buffer for a given view.
        The buffer is read into a block of data as defined as an argument. The data block size must be large enough to accomodate ( view width * view height * depth map precision ) bytes of data.
        
        * x (int) - Start position x to read.
        * y (int) - Start position y to read.
        * width (int) - Number of pixels in x to read.
        * height (int) - Number of pixels in y to read.
        * bufferPtr (byterray) - Pointer to depth data allocated by the caller.
        * depthMapPrecision (int) - Enumerated depth precision:
            kDepth_8          8 bits.
            kDepth_Float      Floating point.
        """
    
        pass
    
    
    def refresh(*args, **kwargs):
        """
        refresh(all=False, force=False, offscreen=False) -> self
        
        
        Refresh the this view.
        
        * all (bool) - If True then refresh all views, otherwise refresh this view.
        * force (bool) - If True then force views to refresh even if they do not require it.
        * offscreen (bool) - Should the buffer be redrawn if it's offscreen?
        """
    
        pass
    
    
    def renderOverrideName(*args, **kwargs):
        """
        renderOverrideName() -> string
        
        Get the current render override name. If none then an empty string will be returned.
        """
    
        pass
    
    
    def rendererString(*args, **kwargs):
        """
        rendererString() -> string
        
        Get the string name of the current renderer being used for drawing to this view
        """
    
        pass
    
    
    def scheduleRefresh(*args, **kwargs):
        """
        scheduleRefresh() -> self
        
        Schedule a forced refresh for this 3d-view. This method may be called safely at any time from any thread. The refresh will occur on the main thread when Maya next becomes idle. If a refresh has already been scheduled for this view but has not yet occurred then this method will do nothing.
        """
    
        pass
    
    
    def selectMode(*args, **kwargs):
        """
        selectMode() -> bool
        
        Tells if this M3dView is in selection mode.
        """
    
        pass
    
    
    def setCamera(*args, **kwargs):
        """
        setCamera(camera) -> self
        
        Set the camera for this view.
        
        * camera (MDagPath) - Dag path of the camera for this view
        """
    
        pass
    
    
    def setColorMask(*args, **kwargs):
        """
        setColorMask(r, g, b, a) -> self
        
        Set the current color mask.
        
        * r (bool) - Red color mask flag.
        * g (bool) - Green color mask flag.
        * b (bool) - Blue color mask flag.
        * a (bool) - Alpha color mask flag.
        """
    
        pass
    
    
    def setDisallowPolygonOffset(*args, **kwargs):
        """
        setDisallowPolygonOffset(v) -> self
        
        Certain Maya actions will use glPolygonOffset to offset polygons drawing into the depth buffer.  This method controls this behavior. When True, it prevents Maya from altering the polygon offset parameters.
        
        * v (bool) - enable/disable the polygon offset
        """
    
        pass
    
    
    def setDisplayStyle(*args, **kwargs):
        """
        setDisplayStyle(style, activeOnly=False) -> self
        
        Sets the display style for this view.
        
        * style (int) - The display style to be set for this view
        See displayStyle() description for a list a valid display style
        """
    
        pass
    
    
    def setDrawColor(*args, **kwargs):
        """
        setDrawColor(index, table=kActiveColors) -> self
        setDrawColor(color) -> self
        
        Set the color to draw in.  The index argument is an index into the application's color tables.  Valid values range between zero and the size of the table minus one.  The size of the active and dormant color tables can be found using methods of this class.  The background and template color tables are both of size one.
        
        These indices do not directly correspond to those of the underlying OpenGL color index mode.  Using the glIndex call directly is not recommended and may cause unpredictable results.  This method should be used instead.
        
        Note that this method will work in either RGBA mode or color index mode.
        
        * index (int) - index of the color to draw in
        * table (int) - color table to index into
        See colorAtIndex() description of a list a valid color table
        
        Or
        Set the color to draw in.
        It is a convenient replacement for glColor3.
        
        * color (MColor) - color to draw in
        """
    
        pass
    
    
    def setDrawColorAndAlpha(*args, **kwargs):
        """
        setDrawColorAndAlpha(color) -> self
        
        Set the color to draw in.
        It is a convenient replacement for glColor4.
        
        * color (MColor) - color to draw in
        """
    
        pass
    
    
    def setMultipleDrawEnable(*args, **kwargs):
        """
        setMultipleDrawEnable(enable) -> self
        
        This method enables/disables multiple camera drawing for this view. If multiple draw is disabled, then this view will behave like a normal Maya view.
        
        * enable (bool) - If True, then multiple draw is enabled.
        """
    
        pass
    
    
    def setMultipleDrawPassCount(*args, **kwargs):
        """
        setMultipleDrawPassCount(count) -> self
        
        This method sets the number of multiple draw passes when multiple draw is enabled.
        
        * count (int) - The number of multiple draw passes.
        """
    
        pass
    
    
    def setObjectDisplay(*args, **kwargs):
        """
        setObjectDisplay(displayMask) -> self
        
        Sets a display object mask that indicates which object types are drawn in current view. By default every thing is displayed.
        
        * displayMask (int) - A combination of display object mask
        See objectDisplay() description for a list of valid display mask
        """
    
        pass
    
    
    def setObjectListFilterName(*args, **kwargs):
        """
        setObjectListFilterName(name) -> self
        
        Set the name of the object list filter (MObjectListFilter) to use.
        
        The filter must be registered before it can be used.
        
        If the name is an empty string then any existing filter will be removed.
        
        Any previously set filter will be replaced with the new one.
        
        * name (string) - Name of the filter.
        """
    
        pass
    
    
    def setPluginObjectDisplay(*args, **kwargs):
        """
        setPluginObjectDisplay(pluginDisplayFilter, on) -> self
        
        Enables or disables a user-defined display filter (i.e. one which was registered using MFnPlugin.registerDisplayFilter() or the 'pluginDisplayFilter' command).
        
        In Default Viewport, the plug-in will have to check the state of the user-defined display filter in the node's draw code.
        In Viewport 2.0, nodes will be filtered automatically based on the classification associated with the filter.
        During selection/snapping, the plugin will have to check the state of the filter in the node's select/snap code.
        
        * pluginDisplayFilter (string) - The name of the plugin display filter.
        * on (bool) - Enable or disable the plugin display filter.
        """
    
        pass
    
    
    def setRenderOverrideName(*args, **kwargs):
        """
        setRenderOverrideName(name) -> self
        
        Set the name of a render override (MRenderOverride) to use.
        
        The override must be registered before it can be used.
        
        The override cannot be set unless the view is set to be using the Viewport 2.0 renderer.
        
        If the override name is an empty string then the any existing override will be removed.
        
        * name (string) - name Name of the override.
        """
    
        pass
    
    
    def setShowObjectFilterNameInHUD(*args, **kwargs):
        """
        setShowObjectFilterNameInHUD(show) -> self
        
        Sets whether or not to display the object filter UI name in the heads up display when an object filter is active. This string is concatenated with the camera name.
        
        * show (bool) - If True, show the filter UI name in the HUD
        """
    
        pass
    
    
    def setShowViewSelectedChildren(*args, **kwargs):
        """
        setShowViewSelectedChildren(show) -> self
        
        This method changes the way that view selected works. By default, view selected with show all of the children of the objects in the view selected set. If False is passed to this method, then only the obejcts in the view selected set and their shapes will be drawn.
        
        * show (bool) - True if all of the children of view selected objects should be displayed. True is the default behavior for view selected.
        """
    
        pass
    
    
    def setUserDefinedColor(*args, **kwargs):
        """
        setUserDefinedColor(index, color) -> self
        
        Sets the user defined color at the given index.  Valid indices range between zero and the number of user defined colors.
        Returns an index into the application's color table
        
        * index (int) - index into the user defined color
        * color (MColor) - color to set to
        """
    
        pass
    
    
    def setViewSelectedPrefix(*args, **kwargs):
        """
        setViewSelectedPrefix(prefix) -> self
        
        Sets the prefix for the camera name as displayed in the heads up display when view selected is enabled. The prefix is concatenated with the camera name.
        The default value is "isolate: "
        
        * prefix (string) - The prefix to use.
        """
    
        pass
    
    
    def showObjectFilterNameInHUD(*args, **kwargs):
        """
        showObjectFilterNameInHUD() -> bool
        
        Returns whether the object filter UI name is shown in the heads up display when an object filter is active.
        """
    
        pass
    
    
    def showViewSelectedChildren(*args, **kwargs):
        """
        showViewSelectedChildren() -> bool
        
        Returns turn if view selected shows all of the children of the obejcts that are flagged for view selected.
        """
    
        pass
    
    
    def textureMode(*args, **kwargs):
        """
        textureMode() -> bool
        
        Tells if this M3dView is in texture mode.
        """
    
        pass
    
    
    def twoSidedLighting(*args, **kwargs):
        """
        twoSidedLighting() -> bool
        
        Return True if the Two-sided lighting mode is enabled.
        """
    
        pass
    
    
    def updateViewingParameters(*args, **kwargs):
        """
        updateViewingParameters() -> self
        
        This method tells the camera to set the view's transformation matrix.
        """
    
        pass
    
    
    def userDefinedColorIndex(*args, **kwargs):
        """
        userDefinedColorIndex(index) -> int
        
        Returns the index for the given user-defined color.  Valid values for the index argument range between zero and the number of user-defined colors minus one.
        
        The index returned gives the location of the specified color inside the active and dormant color tables (the index is the same in both tables).
        
        * index (int) - Index into user-defined colors
        """
    
        pass
    
    
    def usingDefaultMaterial(*args, **kwargs):
        """
        usingDefaultMaterial() -> bool
        
        Returns True if the view is currently displaying objects using the default material.
        """
    
        pass
    
    
    def usingMipmappedTextures(*args, **kwargs):
        """
        usingMipmappedTextures() -> bool
        
        Returns if the view is using mipmapped texture display.
        """
    
        pass
    
    
    def viewIsFiltered(*args, **kwargs):
        """
        viewIsFiltered() -> bool
        
        Returns True if the view is filtered.
        """
    
        pass
    
    
    def viewSelectedPrefix(*args, **kwargs):
        """
        viewSelectedPrefix() -> string
        
        Returns the prefix used when displaying the camera name in the heads up display when view selected in on
        """
    
        pass
    
    
    def viewToObjectSpace(*args, **kwargs):
        """
        viewToObjectSpace(x_pos, y_pos, localMatrixInverse, oPt, oVector) -> self
        
        Takes a point in port coordinates and returns a corresponding ray in object coordinates.
        
        * x_pos (int) - the x position of the point in port coordinates
        * y_pos (int) - the y position of the point in port coordinates
        * localMatrixInverse (MMatrix) - the inclusive matrix inverse of the object in question
        * oPt [OUT] (MPoint) - the source of the ray in object space
        * oVector [OUT] (MVector) - the direction of the ray in object space
        """
    
        pass
    
    
    def viewToWorld(*args, **kwargs):
        """
        viewToWorld(x_pos, y_pos, worldPt, worldVector) -> self
        viewToWorld(x_pos, y_pos, nearClipPt, farClipPt) -> self
        
        Takes a point in port coordinates and returns a corresponding ray in world coordinates.
        
        * x_pos (int) - the x position of the point in port coordinates
        * y_pos (int) - the y position of the point in port coordinates
        * worldPt [OUT] (MPoint) - the source of the ray
        * worldVector [OUT] (MVector) - the direction of the ray
        
        Or
        Takes a point in port coordinates and returns a point on the near and far clipping planes.
        
        * x_pos (int) - the x position of the point in port coordinates
        * y_pos (int) - the y position of the point in port coordinates
        * nearClipPt [OUT] (MPoint) - point on near clipping plane
        * farClipPt [OUT] (MPoint) - point on far clipping plane
        """
    
        pass
    
    
    def viewport(*args, **kwargs):
        """
        viewport() -> [int, int, int, int]
        
        Get the current viewport dimensions.
        """
    
        pass
    
    
    def widget(*args, **kwargs):
        """
        widget() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the view's Qt widget.
        """
    
        pass
    
    
    def window(*args, **kwargs):
        """
        window() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the native window for this view.
        """
    
        pass
    
    
    def wireframeOnShaded(*args, **kwargs):
        """
        wireframeOnShaded() -> bool
        
        Return whether we draw wireframe in shaded mode.
        """
    
        pass
    
    
    def wireframeOnlyInShadedMode(*args, **kwargs):
        """
        wireframeOnlyInShadedMode() -> bool
        
        Return whether we are in shaded mode, but that only non shaded drawing should occur (wireframe).
        
        In general it will return True only when the current renderer is "hwRender_OpenGL_Renderer". See the M3dView.rendererString() method for more details.
        """
    
        pass
    
    
    def worldToView(*args, **kwargs):
        """
        worldToView(worldPt) -> [int, int, bool]
        
        Converts a point in world space to port space.
        Returns the x and y coordinates of the world point in port space and if the point is not clipped.
        
        * worldPt (MPoint) - the point to world space
        """
    
        pass
    
    
    def writeColorBuffer(*args, **kwargs):
        """
        writeColorBuffer(image, x=0, y=0) -> self
        
        Overwrite the RGB values for the frame buffer for a given view.
        Expected input is a block of RGBA, such that each channel is one byte in size.
        
        * image (MImage) - The image containing the block of pixels to write
        * x (int) - The location in screen space of the lower left corner (X) of the image to write. The default value is 0.
        * y (int) - The location in screen space of the lower left corner (Y) of the image to write. The default value is 0.
        """
    
        pass
    
    
    def xray(*args, **kwargs):
        """
        xray() -> bool
        
        Return True if the X-Ray mode is enabled.
        """
    
        pass
    
    
    def xrayJoints(*args, **kwargs):
        """
        xrayJoints() -> bool
        
        Return True if the X-Ray Joints mode is enabled.
        """
    
        pass
    
    
    def active3dView(*args, **kwargs):
        """
        active3dView() -> M3dView
        
        Returns the active view in the form of a class (M3dView) that can operate on it.
        """
    
        pass
    
    
    def activeAffectedColor(*args, **kwargs):
        """
        activeAffectedColor() -> MColor
        
        Returns the color for active affected objects.
        """
    
        pass
    
    
    def activeTemplateColor(*args, **kwargs):
        """
        activeTemplateColor() -> MColor
        
        Returns the color for active template objects.
        """
    
        pass
    
    
    def applicationShell(*args, **kwargs):
        """
        applicationShell() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the native handle for Maya's main window.
        """
    
        pass
    
    
    def backgroundColor(*args, **kwargs):
        """
        backgroundColor() -> MColor
        
        Returns the value of the background color.
        """
    
        pass
    
    
    def backgroundColorBottom(*args, **kwargs):
        """
        backgroundColorBottom() -> MColor
        
        Returns the value of the background gradient bottom color.
        """
    
        pass
    
    
    def backgroundColorTop(*args, **kwargs):
        """
        backgroundColorTop() -> MColor
        
        Returns the value of the background gradient top color.
        """
    
        pass
    
    
    def displayStatus(*args, **kwargs):
        """
        displayStatus(path) -> int
        
        Returns the display status of the given DAG path.
        
        * path (MDagPath) - the DAG path to get.
        
        Valid display status:
          kActive               Object is active (selected).
          kLive                 Object is live (construction surface).
          kDormant              Object is dormant.
          kInvisible            Object is invisible (not drawn).
          kHilite               Object is hilited (has selectable components).
          kTemplate             Object is templated (Not renderable).
          kActiveTemplate       Object is active and templated.
          kActiveComponent      Object has active components.
          kLead                 Last selected object.
          kIntermediateObject   Construction object (not drawn).
          kActiveAffected       Affected by active object(s).
          kNoStatus             Object does not have a valid display status.
        """
    
        pass
    
    
    def get3dView(*args, **kwargs):
        """
        get3dView(index) -> M3dView
        
        Returns the 3D view at the given index.
        
        * index (int) - index of the view to get
        """
    
        pass
    
    
    def getM3dViewFromModelEditor(*args, **kwargs):
        """
        getM3dViewFromModelEditor(name) -> M3dView
        
        Given the name of a model editor, get the M3dView used by that editor. If this fails, then a editor with the given name could not be located.
        
        * name (string) - The name of the model editor.
        """
    
        pass
    
    
    def getM3dViewFromModelPanel(*args, **kwargs):
        """
        getM3dViewFromModelPanel(name) -> M3dView
        
        Given the name of a model panel, get the M3dView used by that panel. If this fails, then a panel with the given name could not be located.
        
        * name (string) - The name of the model panel.
        """
    
        pass
    
    
    def hiliteColor(*args, **kwargs):
        """
        hiliteColor() -> MColor
        
        Returns the color for hilited objects.
        """
    
        pass
    
    
    def isBackgroundGradient(*args, **kwargs):
        """
        isBackgroundGradient() -> bool
        
        Returns whether a gradient is being used as the background color.
        """
    
        pass
    
    
    def leadColor(*args, **kwargs):
        """
        leadColor() -> MColor
        
        Returns the color for lead objects.
        """
    
        pass
    
    
    def liveColor(*args, **kwargs):
        """
        liveColor() -> MColor
        
        Returns the color for live objects.
        """
    
        pass
    
    
    def numberOf3dViews(*args, **kwargs):
        """
        numberOf3dViews() -> int
        
        Returns the number of 3D views currently in existance.
        """
    
        pass
    
    
    def referenceLayerColor(*args, **kwargs):
        """
        referenceLayerColor() -> MColor
        
        Returns the color for objects which belong to a display layer whose display type is Reference. This color is also used for objects whose display override is set to Reference.
        """
    
        pass
    
    
    def scheduleRefreshAllViews(*args, **kwargs):
        """
        scheduleRefreshAllViews() -> None
        
        Schedule a forced refresh for all 3d-views. This method may be called safely at any time from any thread. The refresh will occur on the main thread when Maya next becomes idle. If a refresh has already been scheduled but has not yet occurred then this method will do nothing.
        """
    
        pass
    
    
    def templateColor(*args, **kwargs):
        """
        templateColor() -> MColor
        
        Returns the value of the template color.
        """
    
        pass
    
    
    __new__ = None
    
    
    kActive = 0
    
    
    kActiveAffected = 10
    
    
    kActiveColors = 0
    
    
    kActiveComponent = 7
    
    
    kActiveTemplate = 6
    
    
    kBackgroundColor = 6
    
    
    kBoundingBox = 0
    
    
    kCenter = 1
    
    
    kDefaultQualityRenderer = 0
    
    
    kDepth_8 = 0
    
    
    kDepth_Float = 1
    
    
    kDisplayCVs = 131072
    
    
    kDisplayCameras = 32
    
    
    kDisplayDeformers = 256
    
    
    kDisplayDimensions = 4096
    
    
    kDisplayDynamicConstraints = 134217728
    
    
    kDisplayDynamics = 512
    
    
    kDisplayEverything = -1
    
    
    kDisplayFluids = 2097152
    
    
    kDisplayFollicles = 4194304
    
    
    kDisplayGrid = 65536
    
    
    kDisplayHairSystems = 8388608
    
    
    kDisplayHulls = 262144
    
    
    kDisplayIkHandles = 128
    
    
    kDisplayImagePlane = 16777216
    
    
    kDisplayJoints = 64
    
    
    kDisplayLights = 16
    
    
    kDisplayLocators = 2048
    
    
    kDisplayManipulators = 268435456
    
    
    kDisplayMeshes = 4
    
    
    kDisplayNCloths = 33554432
    
    
    kDisplayNParticles = 536870912
    
    
    kDisplayNRigids = 67108864
    
    
    kDisplayNurbsCurves = 1
    
    
    kDisplayNurbsSurfaces = 2
    
    
    kDisplayParticleInstancers = 1024
    
    
    kDisplayPivots = 16384
    
    
    kDisplayPlanes = 8
    
    
    kDisplaySelectHandles = 8192
    
    
    kDisplayStrokes = 524288
    
    
    kDisplaySubdivSurfaces = 1048576
    
    
    kDisplayTextures = 32768
    
    
    kDormant = 2
    
    
    kDormantColors = 2
    
    
    kExcludeMotionTrails = 1073741824
    
    
    kExcludePluginShapes = -2147483648
    
    
    kExternalRenderer = 3
    
    
    kFlatShaded = 1
    
    
    kGouraudShaded = 2
    
    
    kHighQualityRenderer = 1
    
    
    kHilite = 4
    
    
    kIntermediateObject = 9
    
    
    kInvisible = 3
    
    
    kLead = 8
    
    
    kLeft = 0
    
    
    kLightActive = 2
    
    
    kLightAll = 0
    
    
    kLightDefault = 3
    
    
    kLightNone = 5
    
    
    kLightSelected = 1
    
    
    kLive = 1
    
    
    kNoStatus = 11
    
    
    kPoints = 4
    
    
    kRight = 2
    
    
    kStippleDashed = 1
    
    
    kStippleNone = 0
    
    
    kTemplate = 5
    
    
    kTemplateColor = 5
    
    
    kUnused1 = 4
    
    
    kViewport2Renderer = 2
    
    
    kWireFrame = 3


class MPxDragAndDropBehavior(object):
    """
    This is the base class for user defined drag and drop behaviors.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectAttrToAttr(*args, **kwargs):
        """
        connectAttrToAttr(sourcePlug, destinationPlug, force) -> None
        
        This method is called by the defaultNavigation command to connect a source attribute to a destination attribute.
        
        If this method is overidden it should attempt to determine what the user probably wants this connection to be, and set up the connection appropriately. If the force argument is true it is intended to notify the user to break any existing connections to the plug, similar to what the mel command 'connectAttr' -f flag is used for.
        
        * sourcePlug (MPlug) - Source plug in the connection.
        * destinationPlug (MPlug) - Destination plug in the connection.
        * force (bool) - Tells whether or not to break any existing connections to the destination attribute.
        """
    
        pass
    
    
    def connectAttrToNode(*args, **kwargs):
        """
        connectAttrToNode(sourcePlug, destinationNode, force) -> None
        
        This method is called by the defaultNavigation command to connect a source attribute to a destination node.
        
        You should override this method if you can determine from the type of source node and attribute and the type of destination node what the user is trying to do and you know the appropriate connections that must be made for the end result to be what the user expects.
        
        * sourcePlug (MPlug) - Source plug in the connection.
        * destinationNode (MObject) - Destination node for the connection.
        * force (bool) - Tells whether or not to break any existing connections to the destination node.
        """
    
        pass
    
    
    def connectNodeToAttr(*args, **kwargs):
        """
        connectNodeToAttr(sourceNode, destinationPlug, force) -> None
        
        This method is called by the defaultNavigation command to connect a source node to a destination attribute.
        
        You should override this method if you can determine from the type of source node and the type of destination node and attribute what the user is trying to do and you know the appropriate connections that must be made for the end result to be what the user expects.
        
        * sourceNode (MObject) - Source node in the connection.
        * destinationPlug (MPlug) - Destination plug for the connection.
        * force (bool) - Tells whether or not to break any existing connections to the destination attribute.
        """
    
        pass
    
    
    def connectNodeToNode(*args, **kwargs):
        """
        connectNodeToNode(sourceNode, destinationNode, force) -> None
        
        This method is called by the defaultNavigation command to connect a source node to a destination node.
        
        You should override this method if you can determine from the type of source node and the type of destination node what the user is trying to do and you know the appropriate connections that must be made for the end result to be what the user expects.
        
        * sourceNode (MObject) - Source node in the connection.
        * destinationNode (MObject) - Destination node for the connection.
        * force (bool) - Tells whether or not to break any existing connections to the destination node.
        """
    
        pass
    
    
    def shouldBeUsedFor(*args, **kwargs):
        """
        shouldBeUsedFor(sourceNode, destinationNode, sourcePlug, destinationPlug) -> bool
        
        This method must be overridden in order to use a drag and drop behavior.
        
        The overridden method will be called by the defaultNavigation command to determine wether or not to use this drag and drop behavior to finish a connection. If the user would like to handle the connection between sourceNode/Plug and destinationNode/Plug then this routine must pass back true, otherwise the routine must pass back false in order for the default connection mechanism to work between these two nodes. sourcePlug and destinationPlug may be null depending on if there were any attributes given in the drag and drop. Use the isNull() method on MPlug to assure the plugs are valid.
        
        * sourceNode (MObject) - The source node of the drag and drop or the node being dragged.
        * destinationNode (MObject) - the destination node of the drag and drop or the node being dropped upon.
        * sourcePlug (MPlug) - The source plug of the drag and drop or the plug being dragged (this may be null).
        * destinationPlug (MPlug) - The destination plug of the drag and drop or the plug being dropped upon (this may be null).
        """
    
        pass
    
    
    __new__ = None


class MDrawData(object):
    """
    The MDrawData class holds geometry specific information for user defined shapes which maya does not intrinsicly know about.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def geometry(*args, **kwargs):
        """
        geometry() -> long
        
        Returns a long containing a C++ 'void' pointer which points to the geometry associated with this draw data object.
        The geometry is set using the getDrawData method of MPxSurfaceShapeUI.
        """
    
        pass
    
    
    __new__ = None


class _MSwatchRenderBase(object):
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


class _MPxNode(object):
    """
    Base class for user defined dependency nodes.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addExternalContentForFileAttr(*args, **kwargs):
        """
        addExternalContentForFileAttr(table, attr) -> bool
        
        This method is a helper for derived clases implementing getExternalContent().  It augments the external content info table passed in with an entry describing external content whose location is described by the specified attribute.
        
        The method will not overwrite existing items, i.e. items with the same key. (attribute name).  In this context, overwriting an item means the caller has called this function twice with the same attribute, or that two separate but identically named attributes were used.  If replacing an entry is the desired effect, it is the caller's responsibility to erase the previous item first.
        
        * table [OUT] (MExternalContentInfoTable) - table The table in which the new entry will be added.
        * attr (MObject) - The attribute for which the plug value will be queried for a location.
        
        Returns True if an item was sucessfully added to the table.  False if the attribute does not describe a non-empty location, or an item with the same key was already present in the table.
        """
    
        pass
    
    
    def compute(*args, **kwargs):
        """
        compute(plug, dataBlock) -> self
        
        This method should be overridden in user defined nodes.
        
        Recompute the given output based on the nodes inputs.  The plug represents the data value that needs to be recomputed, and the data block holds the storage for all of the node's attributes.
        
        The MDataBlock will provide smart handles for reading and writing this node's attribute values.  Only these values should be used when performing computations.
        
        When evaluating the dependency graph, Maya will first call the compute method for this node.  If the plug that is provided to the compute indicates that that the attribute was defined by the Maya parent node, the compute method should return None.  When this occurs, Maya will call the internal Maya node from which the user-defined node is derived to compute the plug's value.
        
        This means that a user defined node does not need to be concerned with computing inherited output attributes.  However, if desired, these can be safely recomputed by this method to change the behaviour of the node.
        
        * plug (MPlug) - plug representing the attribute that needs to be recomputed.
        * block (MDataBlock) - data block containing storage for the node's attributes.
        """
    
        pass
    
    
    def connectionBroken(*args, **kwargs):
        """
        connectionBroken( plug, otherPlug, asSrc) -> self
        
        This method gets called when connections are broken with attributes of this node.
        
        * plug (MPlug) - attribute on this node.
        * otherPlug (MPlug) - attribute on other node.
        * asSrc (bool) - is this plug a source of the connection.
        """
    
        pass
    
    
    def connectionMade(*args, **kwargs):
        """
        connectionMade(plug, otherPlug, asSrc) -> self
        
        This method gets called when connections are made to attributes of this node.
        
        * plug (MPlug) - attribute on this node.
        * otherPlug (MPlug) - attribute on other node.
        * asSrc (bool) - is this plug a source of the connection.
        """
    
        pass
    
    
    def copyInternalData(*args, **kwargs):
        """
        copyInternalData(node) -> self
        
        This method is overriden by nodes that store attribute data in some internal format.
        
        On duplication this method is called on the duplicated node with the node being duplicated passed as the parameter.  Overriding this method gives your node a chance to duplicate any internal data you've been storing and manipulating outside of normal attribute data.
        
        * node (MPxNode) - the node that is being duplicated.
        """
    
        pass
    
    
    def dependsOn(*args, **kwargs):
        """
        dependsOn( plug, otherPlug) -> bool/None
        
        This method may be overridden by the user defined node. It should only be required to override this on rare occasions.
        
        This method determines whether a specific attribute depends on another attribute.
        
        You should return None to specify that Maya should determines the dependency (default).
        
        This is mainly to define dependency of dynamic attributes, since attributeAffects does not work with dynamic attributes.
        
        * plug (MPlug) - attribute on this node.
        * otherPlug (MPlug) - attribute on other node.
        """
    
        pass
    
    
    def doNotWrite(*args, **kwargs):
        """
        doNotWrite() -> bool
        
        use this method to query the "do not write" state of this proxy node. True is returned if this node will not be saved when the maya model is written out.
        """
    
        pass
    
    
    def forceCache(*args, **kwargs):
        """
        forceCache(ctx=fsNormal) -> MDataBlock
        
        Get the datablock for this node. If there is no datablock then one will be created.
        NOTE: This should be used only in places where fast access to the datablock outside of a compute is critical such as the transformUsing method of MPxSurfaceShape.
        
        * ctx (MDGContext) - The context in which the node will evaluate.
        """
    
        pass
    
    
    def getExternalContent(*args, **kwargs):
        """
        getExternalContent(table) -> self
        
        The table populated by this method must include the location of all the content (files) used by this node, including those that do not exist.  See MExternalContentInfoTable for details.
        
        Keys used to add items to this table will be the same that get passed to setExternalContent through its MExternalContentLocationTable parameter to perform a batched change of content location.
        
        When implementing getExternalContent, you are responsible for forwarding the call to the base class when it makes sense to do so, so that base classes  can also add their external content to the table.
        
        The default implementation does nothing.
        
        * table [OUT] (MExternalContentInfoTable) - Content information table that this method must populate.
        """
    
        pass
    
    
    def getFilesToArchive(*args, **kwargs):
        """
        getFilesToArchive(shortName=False, unresolvedName=False, markCouldBeImageSequence=False) -> list of strings
        
        Use this method to return all external files used by this node. This file list will be used by the File > Archive zip feature, maya.exe -archive and the `file -q -list` mel command.
        
        Only include files that exist.
        
        If shortName is True, return just the filename portion of the path. Otherwise, return a full path.
        
        If unresolvedName is True, return the path before any resolution has been done (i.e leave it as a relative path, include unexpanded environment variables,  tildes, ".."s etc). Otherwise, resolve the file     path and return an absolute path (to resolve with standard Maya path resolution, use MFileObject.resolvedFullName()).
        
        * shortName (bool) - If True, only add the filename of the path.
        * unresolvedName (bool) - If True, add paths before any resolution, rather than absolute paths.
        * markCouldBeImageSequence (bool) - If True, append an asterisk after any file path that could be an image sequence (note: only used by maya.exe -archive).
        """
    
        pass
    
    
    def getInternalValueInContext(*args, **kwargs):
        """
        getInternalValueInContext(plug, dataHandle, ctx) -> bool
        
        This method is overriden by nodes that store attribute data in some internal format.
        
        The internal state of attributes can be set or queried using the setInternal and internal methods of MFnAttribute.
        
        When internal attribute values are queried via getAttr or MPlug.getValue() this method is called.
        
        * plug (MPlug) - the attribute that is being queried.
        * dataHandle [OUT] (MDataHandle) - the dataHandle to store the attribute value.
        * ctx (MDGContext) - the context the method is being evaluated in.
        """
    
        pass
    
    
    def internalArrayCount(*args, **kwargs):
        """
        internalArrayCount(plug, ctx) -> int
        
        This method is overriden by nodes that have internal array attributes which are not stored in Maya's datablock. This method is used by Maya to determine the non-sparse count of array elements during file io. If the internal array is stored sparsely, you should return the maximum index of the array plus one. If the internal array is non-sparse then return the length of the array.
        
        This method does not need to be implemented for attributes that are stored in the datablock since Maya will use the datablock size.
        
        If this method is overriden, it should return -1 for attributes which it does not handle. Maya will use the datablock size to determine the array length when -1 is returned.
        
        * plug (MPlug) - the array plug.
        * ctx (MDGContext) - the context.
        """
    
        pass
    
    
    def isAbstractClass(*args, **kwargs):
        """
        isAbstractClass() -> bool
        
        Override this class to return True if this node is an abstract node. An abstract node can only be used as a base class.  It cannot be created using the 'createNode' command.
        
        It is not necessary to override this method.
        """
    
        pass
    
    
    def isPassiveOutput(*args, **kwargs):
        """
        isPassiveOutput(plug) -> bool
        
        This method may be overridden by the user defined node if it wants to provide output attributes which do not prevent value modifications to the destination attribute. For example, output plugs on animation curve nodes are passive. This allows the attributes driven by the animation curves to be set to new values by the user.
        
        * plug (MPlug) - plug representing output in question.
        """
    
        pass
    
    
    def legalConnection(*args, **kwargs):
        """
        legalConnection(plug, otherPlug, asSrc) -> bool/None
        
        This method allows you to check for legal connections being made to attributes of this node.
        
        You should return None to specify that maya should handle this connection if you are unable to determine if it is legal.
        
        * plug (MPlug) - attribute on this node.
        * otherPlug (MPlug) - attribute on other node.
        * asSrc (bool) - is this plug a source of the connection.
        """
    
        pass
    
    
    def legalDisconnection(*args, **kwargs):
        """
        legalDisconnection(plug, otherPlug, arsSrc) -> bool/None
        
        This method allows you to check for legal disconnections being made to attributes of this node.
        
        You should return None to specify that maya should handle this disconnection if you are unable to determine if it is legal.
        
        * plug (MPlug) - attribute on this node.
        * otherPlug (MPlug) - attribute on other node.
        * asSrc (boool) - is this plug a source of the connection.
        """
    
        pass
    
    
    def name(*args, **kwargs):
        """
        name() -> string
        
        Returns the name of this particular instance of this class.  Each objectin the dependency graph has a name.  This name will be used by the UIand by MEL.
        
        It is not necessary to override this method.
        
        Returns the name of the node
        """
    
        pass
    
    
    def passThroughToMany(*args, **kwargs):
        """
        passThroughToMany(plug, plugArray) -> bool
        
        This method is overriden by nodes that want to control the traversal behavior of some Maya search algorithms which traverse the history/future of shape nodes looking for directly related nodes. In particular, the Artisan paint code uses this method when searching for paintable nodes, and the disk cache code uses this method when searching for upstream cacheFile nodes.
        
        If this method is not implemented or returns False, the base class Maya implementation of this method calls passThroughToOne and returns the results of that call.
        
        * plug (MPlug) - the plug.
        * plugArray (MPlugArray) - the corresponding plugs.
        """
    
        pass
    
    
    def passThroughToOne(*args, **kwargs):
        """
        passThroughToOne(plug) -> plug
        
        This method may be overriden by nodes that have a one-to-one relationship between an input attribute and a corresponding output attribute. This method is used by Maya to perform the following capabilities:
        
        - When this node is deleted, the delete command will rewire the source of the input attribute to the destination of the output attribute if the source and destination are connected to nodes that are not deleted.
        - History traversal algorithms such as the bakePartialHistory command use this method to direct its traversal through a shape's construction history.
        - The base class Maya implementation of passThroughToAll will call this method if passThroughToAll returns False.
        
        * plug (MPlug) - the plug.
        """
    
        pass
    
    
    def postConstructor(*args, **kwargs):
        """
        postConstructor() -> self
        
        Internally maya creates two objects when a user defined node is created, the internal MObject and the user derived object.
        The association between the these two objects is not made until after the MPxNode constructor is called. This implies that no MPxNode member function can be called from the MPxNode constructor.
        The postConstructor will get called immediately after the constructor when it is safe to call any MPxNode member function.
        """
    
        pass
    
    
    def setDependentsDirty(*args, **kwargs):
        """
        setDependentsDirty(plug, plugArray) -> self
        
        This method can be overridden in user defined nodes to specify which plugs should be set dirty based upon an input plug which Maya is marking dirty. The list of plugs for Maya to mark dirty is returned by the plug array. This method handles both dynamic as well as non-dynamic plugs and is useful in the following ways:
        
        
        
        - Allows attributeAffects-style relationships to be handled for dynamically-added attributes. Since MPxNode.attributeAffects() can only be used with non-dynamic attributes, use of this method allows a way for all attributes of a node to affect one another, both dynamic and non-dynamic.
        
        - Provides more flexible relationships than what is available with MPxNode.attributeAffects(). For example, you may wish to not dirty plugs when the current frame is one. However, as the routine is called during dirty propagation, there are restrictions on what can be done within the routine, most importantly you must not cause any dependency graph computation. For details, see the IMPORTANT NOTE below.
        
        
        
        This method is designed to work harmoniously with MPxNode.attributeAffects() on the same node. Alternately, you can do all affects relationships within a yourNode.setDependentsDirty() implementation.
        
        The body of a user-implemented setDependentsDirty() implementation might look like the following example, which causes the plug called "B" to be set dirty whever plug "A" is changed, i.e. A affects B.
        
        * plug (MPlug) - plug which is being set dirty by Maya.
        * plugArray the programmer should add any plugs which they want to set dirty to this list.
        """
    
        pass
    
    
    def setDoNotWrite(*args, **kwargs):
        """
        setDoNotWrite(bool) -> self
        
        Use this method to mark the "do not write" state of this proxy node.  If set, this node will not be saved when the Maya model is written out. 
        
        NOTES:
        1. Plug-in "requires" information will be written out with the model when saved.  But a subsequent reload and resave of the file will cause these to go away.
        2. If this node is a DAG and has a parent or children, the "do not write" flag of the parent or children will not be set. It is the developer's responsibility to ensure that the resulting scene file is capable of being read in without errors due to unwritten nodes.
        """
    
        pass
    
    
    def setExternalContent(*args, **kwargs):
        """
        setExternalContent(table) -> self
        
        This is useful in the context of content relocation.  This will be called while the scene is being loaded to apply path changes performed externally. Consequently, interaction with the rest of the scene must be kept to a minimum.  It is however valid to call this method outside of scene loading contexts.
        
        The keys in the map must be the same as the ones provided by the node in getExternalContent.  The values are the new locations.
        
        When implementing setExternalContent, you are responsible for forwarding the call to the base class when it makes sense to do so, so that base classes  can also set their external content.
        
        The default implementation does nothing.
        
        * table Key->location table with new content locations.
        """
    
        pass
    
    
    def setExternalContentForFileAttr(*args, **kwargs):
        """
        setExternalContentForFileAttr(attr, table) -> bool
        
        This method is a helper for derived clases implementing setExternalContent().  It assigns a value to a plug with the one from the table whose key is the same as the passed in attribute name.
        
        The method will not write to the plug if the attribute is not found in the  table.
        
        * attr (MObject) - The attribute of the plug we want to write to.
        * table (MExternalContentLocationTable) - A table which may hold or not the value for a given plug.
        
        Returns True if the plug was successfully written to. False if no entry in the table was named after the attribute or if no plug was found.
        """
    
        pass
    
    
    def setInternalValueInContext(*args, **kwargs):
        """
        setInternalValueInContext(plug, dataHandle, ctx) -> bool
        
        This method is overriden by nodes that store attribute data in some internal format.
        
        The internal state of attributes can be set or queried using the setInternal and internal methods of MFnAttribute.
        
        When internal attribute values are set via setAttr or MPlug.setValue() this method is called.
        
        Another use for this method is to impose attribute limits.
        
        * plug (MPlug) - the attribute that is being set.
        * dataHandle (MDataHandle) - the dataHandle containing the value to set.
        * ctx (MDGContext) - the context the method is being evaluated in.
        """
    
        pass
    
    
    def setMPSafe(*args, **kwargs):
        """
        setMPSafe(bool) -> self
        
        Set a flag to specify if a user defined shading node is safe for multi-processor rendering. For a shading node to be MP safe, it cannot access any shared global data and should only use attributes in the datablock to get input data and store output data. 
        
        This flag does NOT mark a node thread safe for parallel DG evaluation in Viewport 2.0.  To mark a node thread safe for parallel DG evaluation see the setNodeTypeFlag mel command. 
        
        NOTE: This should be called from the postConstructor() method for shading node plug-ins only. If a shading node is non-safe, then it will only be useful during single processor rendering.
        """
    
        pass
    
    
    def shouldSave(*args, **kwargs):
        """
        shouldSave(plug) -> bool/None
        
        This method may be overridden by the user defined node.  It should only be required to override this on rare occasions.
        
        This method determines whether a specific attribute of this node should be written out during a file save.  The default behavior is to only write the value if it differs from the default and is not being supplied by a connection.  This behavior should be sufficient in most cases.
        This method is not called for ramp attributes since they should always be written.
        
        * plug (MPlug) - plug representing the attribute to be saved.
        """
    
        pass
    
    
    def thisMObject(*args, **kwargs):
        """
        thisMObject() -> MObject
        
        Returns the MObject associated with this user defined node.  This makes it possible to use MFnDependencyNode or to construct plugs to this node's attributes.
        """
    
        pass
    
    
    def type(*args, **kwargs):
        """
        type() -> int
        
        Returns the type of node that this is.  This is used to differentiate user defined nodes that are derived off different MPx base classes.
        
        It is not necessary to override this method.
        
          kDependNode                    Custom node derived from MPxNode
          kLocatorNode                   Custom locator derived from MPxLocatorNode
          kDeformerNode                  Custom deformer derived from MPxDeformerNode
          kManipContainer                Custom container derived from MPxManipContainer
          kSurfaceShape                  Custom shape derived from MPxSurfaceShape
          kFieldNode                     Custom field derived from MPxFieldNode
          kEmitterNode                   Custom emitter derived from MPxEmitterNode
          kSpringNode                    Custom spring derived from MPxSpringNode
          kIkSolverNode                  Custom IK solver derived from MPxIkSolverNode
          kHardwareShader                Custom shader derived from MPxHardwareShader
          kHwShaderNode                  Custom shader derived from MPxHwShaderNode
          kTransformNode                 Custom transform derived from MPxTransform
          kObjectSet                     Custom set derived from MPxObjectSet
          kFluidEmitterNode              Custom fluid emitter derived from MpxFluidEmitterNode
          kImagePlaneNode                Custom image plane derived from MPxImagePlane
          kParticleAttributeMapperNode   Custom particle attribute mapper derived from MPxParticleAttributeMapperNode
          kCameraSetNode                 Custom director derived from MPxCameraSet
          kConstraintNode                Custom constraint derived from MPxConstraint
          kManipulatorNode               Custom manipulator derived from MPxManipulatorNode
          kClientDeviceNode              Custom threaded device derived from MPxThreadedDeviceNode
          kThreadedDeviceNode            Custom threaded device node
          kAssembly                      Custom assembly derived from MPxAssembly
          kSkinCluster                                  Custom deformer derived from MPxSkinCluster
          kGeometryFilter                               Custom deformer derived from MPxGeometryFilter
                 kBlendShape                                    Custom deformer derived from MPxBlendShape
        """
    
        pass
    
    
    def typeId(*args, **kwargs):
        """
        typeId() -> MTypeId
        
        Returns the TYPEID of this node.
        """
    
        pass
    
    
    def typeName(*args, **kwargs):
        """
        typeName() -> string
        
        Returns the type name of this node.  The type name identifies the node type to the ASCII file format
        """
    
        pass
    
    
    def addAttribute(*args, **kwargs):
        """
        addAttribute(attr) -> None
        
        This method adds a new attribute to a user defined node type during the type's initialization.
        
        This method will only work during the static initialization method of the user defined node class.  The initialization method is the one that is passed into  MFnPlugin.registerNode(). The attributes must first be created using one of the MFnAttribute classes, and can then be added using this method.
        
        For compound attributes, the proper way to use this method is by calling it with the parent attribute. If a compound attribute is passed, this method will add all of its children.
        NOTE: A failure will occur if you attempt to call addAttribute() on the children of a compound attribute.
        
        * attr (MObject) - new attribute to add.
        """
    
        pass
    
    
    def attributeAffects(*args, **kwargs):
        """
        attributeAffects(whenChanges, isAffected) -> None
        
        This method specifies that a particular input attribute affects a specific output attribute.  This is required to make evaluation efficient.  When an input changes, only the affected outputs will be computed. Output attributes cannot be keyable - if they are keyable, this method will fail.
        
        This method must be called for every attribute dependency when initializing the node's attributes.  The attributes must first be added using the MPxNode.addAttribute() method.  Failing to call this method will cause the node not to update when its inputs change. If there are no calls to this method in a node's initialization, then the compute method will never be called.
        
        This method will only work during the static initialization method of the user defined node class.  The initialization method is the one that is passed into MFnPlugin.registerNode().  As a result, it does not work with dynamic attributes. For an alternate solution which handles dynamic as well as non-dynamic attributes refer to MPxNode.setDependentsDirty.()
        
        * whenChanges (MObject) - input attribute - MObject that points to an input attribute that has already been added.
        * isAffected (MObject) - affected output attribute - MObject that points to an output attribute that has already been added.
        """
    
        pass
    
    
    def inheritAttributesFrom(*args, **kwargs):
        """
        inheritAttributesFrom(parentClassName) -> None
        
        This method allows a class of plugin node to inherit all of the attributes of a second class of plugin node.
        
        This method will only work during the static initialization method of the user defined node class and must be called before any other attributes have been added.  The initialization method is the one that is passed into  MFnPlugin.registerNode().
        
        A plugin node may only inherit attributes from one other class of plugin node. Attempting to call this method multiple times within a node's initialization method will result in an error.
        
        Both node classes must be registered using the same MPxNode type, listed in MPxNode.type().
        
        * parentClassName (string) - class of node to inherit attributes from.
        """
    
        pass
    
    
    __new__ = None
    
    
    kAssembly = 22
    
    
    kBlendShape = 25
    
    
    kCameraSetNode = 16
    
    
    kClientDeviceNode = 20
    
    
    kConstraintNode = 17
    
    
    kDeformerNode = 2
    
    
    kDependNode = 0
    
    
    kEmitterNode = 6
    
    
    kFieldNode = 5
    
    
    kFluidEmitterNode = 13
    
    
    kGeometryFilter = 24
    
    
    kHardwareShader = 9
    
    
    kHwShaderNode = 10
    
    
    kIkSolverNode = 8
    
    
    kImagePlaneNode = 14
    
    
    kLast = 26
    
    
    kLocatorNode = 1
    
    
    kManipContainer = 3
    
    
    kManipulatorNode = 18
    
    
    kMotionPathNode = 19
    
    
    kObjectSet = 12
    
    
    kParticleAttributeMapperNode = 15
    
    
    kSkinCluster = 23
    
    
    kSpringNode = 7
    
    
    kSurfaceShape = 4
    
    
    kThreadedDeviceNode = 21
    
    
    kTransformNode = 11


class _MMessage(object):
    """
    Base class for message callbacks.
    """
    
    
    
    def currentCallbackId(*args, **kwargs):
        """
        currentCallbackId() -> id
        
        Returns the callback ID of the currently executing callback. If called
        outside of a callback, an invalid MCallbackId and failed status will
        be returned.
        """
    
        pass
    
    
    def nodeCallbacks(*args, **kwargs):
        """
        nodeCallbacks(node) -> ids
        
        Returns a list of callback IDs registered to a given node.
        
         * node (MObject) - Node to query for callbacks.
         * ids (MCallbackIdArray) - Array to store the list of callback IDs.
        """
    
        pass
    
    
    def removeCallback(*args, **kwargs):
        """
        removeCallback(id) -> None
        
        Removes the specified callback from Maya.
        This method must be called for all callbacks registered by a
        plug-in before that plug-in is unloaded.
        
         * id (MCallbackId) - identifier of callback to be removed
        """
    
        pass
    
    
    def removeCallbacks(*args, **kwargs):
        """
        removeCallbacks(ids) -> None
        
        Removes all of the specified callbacks from Maya.
        This method must be called for all callbacks registered by a
        plug-in before that plug-in is unloaded.
        
         * idList (MCallbackIdArray) - list of callbacks to be removed.
        """
    
        pass
    
    
    kDefaultAction = 0
    
    
    kDoAction = 2
    
    
    kDoNotDoAction = 1


class ShaderContext(object):
    """
    Provides contextual information about the current invocation of the shader.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    path = None
    
    shadingEngine = None
    
    __new__ = None


class MDrawInfo(object):
    """
    This class is used by the getDrawRequests method of MPxSurfaceShapeUI to specify the current object drawing state for a user defined shape.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def canDrawComponent(*args, **kwargs):
        """
        canDrawComponent(isDisplayOn, compMask) -> bool
        
        Convenience method to test if components specified by the given mask can be drawn.
        
        * isDisplayOn (bool) - component display is on
        * mask (MSelectionMask) - component mask to test
        """
    
        pass
    
    
    def completelyInside(*args, **kwargs):
        """
        completelyInside() -> bool
        
        Returns True if the object being drawn is inside the viewing frustum.
        """
    
        pass
    
    
    def displayStatus(*args, **kwargs):
        """
        displayStatus() -> int
        
        Returns the status of the object to draw.
        See M3dView.displayStatus() for a list of status.
        """
    
        pass
    
    
    def displayStyle(*args, **kwargs):
        """
        displayStyle() -> int
        
        Returns the display appearance.
        See M3dView.displayStyle() for a list of styles.
        """
    
        pass
    
    
    def getPrototype(*args, **kwargs):
        """
        getPrototype(drawHandler) -> MDrawRequest
        
        This method creates a draw request based on the current draw state.
        
        The draw request is placed onto maya's drawing queue (MDrawRequestQueue) where it can be processed in turn. The drawHandler argument is the shape that will be doing the drawing which is the object calling this function.
        
        * drawHandler (MPxSurfaceShapeUI) - the ui object that is doing the drawing
        """
    
        pass
    
    
    def inSelect(*args, **kwargs):
        """
        inSelect() -> bool
        
        Returns True during any interactive refresh, as when user is interacting with the scene in any way including camera changes, object or component TRS changes, etc. Use userChangingViewContext for determining whether user is changing the view using view context tools such as tumble, dolly or track.
        """
    
        pass
    
    
    def inUserInteraction(*args, **kwargs):
        """
        inUserInteraction() -> bool
        
        Returns True during any interactive refresh, as when user is changing the view using view context tools such as tumble, dolly or track.  Useful for changing drawing mode to something simpler to speed up interaction re-draw.  Use inUserInteraction for determining whether user is interacting with the scene in any way.
        """
    
        pass
    
    
    def inclusiveMatrix(*args, **kwargs):
        """
        inclusiveMatrix() -> MMatrix
        
        Returns the world space inclusive matrix.
        """
    
        pass
    
    
    def multiPath(*args, **kwargs):
        """
        multiPath() -> MDagPath
        
        Returns the path to the object to be drawn.
        """
    
        pass
    
    
    def objectDisplayStatus(*args, **kwargs):
        """
        objectDisplayStatus(displayObj) -> bool
        
        Determines whether the specified objects are allowed to be displayed.
        
        * displayObj (int) - display object mask. See M3dView.objectDisplay() for a list of valid masks.
        """
    
        pass
    
    
    def pluginObjectDisplayStatus(*args, **kwargs):
        """
        pluginObjectDisplayStatus(pluginDisplayFilter) -> bool
        
        Determines whether the specified plugin object is allowed to be displayed.
        
        * pluginDisplayFilter (string) - The name of the plugin display filter which is registered by pluginDisplayFilter command.
        """
    
        pass
    
    
    def projectionMatrix(*args, **kwargs):
        """
        projectionMatrix() -> MMatrix
        
        Returns the camera*projection matrix.
        """
    
        pass
    
    
    def setMultiPath(*args, **kwargs):
        """
        setMultiPath(path) -> self
        
        Sets the path of the object to be drawn.
        
        * path (MDagPath) - the path of the object to be drawn
        """
    
        pass
    
    
    def userChangingViewContext(*args, **kwargs):
        """
        userChangingViewContext() -> bool
        
        Returns True during any interactive refresh, as when user is interacting with the scene in any way including camera changes, object or component TRS changes, etc. Use userChangingViewContext for determining whether user is changing the view using view context tools such as tumble, dolly or track.
        """
    
        pass
    
    
    def view(*args, **kwargs):
        """
        view() -> M3dView
        
        Returns the view that the drawing will take place.
        """
    
        pass
    
    
    __new__ = None


class MMaterial(object):
    """
    This class is used in the draw functions of user defined shapes (see MPxSurfaceShapeUI) for setting up and querying materials in shaded mode drawing.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def applyTexture(*args, **kwargs):
        """
        applyTexture(view, data) -> self
        
        For materials that have texture, this method must be used before the OpenGL drawing to apply the texture to the current view.
        This method should be called from within your MPxSurfaceShapeUI.draw() method.
        
        * view (M3dView) - the view in which the textured drawing is to take place
        * data (MDrawData) - the draw data from the draw request
        """
    
        pass
    
    
    def evaluateDiffuse(*args, **kwargs):
        """
        evaluateDiffuse() -> self
        
        Perform necessary evaluation to be able to get diffuse back.
        """
    
        pass
    
    
    def evaluateEmission(*args, **kwargs):
        """
        evaluateEmission() -> self
        
        Perform necessary evaluation to be able to get emission back.
        """
    
        pass
    
    
    def evaluateMaterial(*args, **kwargs):
        """
        evaluateMaterial(view, path) -> self
        
        Evaluate a material. Must be called before evaluating or getting any material properties.
        
        * view (M3dView) - the view
        * path (MDagPath) - path to the object
        """
    
        pass
    
    
    def evaluateShininess(*args, **kwargs):
        """
        evaluateShininess() -> self
        
        Perform necessary evaluation to be able to get shininess back.
        """
    
        pass
    
    
    def evaluateSpecular(*args, **kwargs):
        """
        evaluateSpecular() -> self
        
        Perform necessary evaluation to be able to get specular back.
        """
    
        pass
    
    
    def evaluateTexture(*args, **kwargs):
        """
        evaluateTexture(data) -> self
        
        Evaluate texturing related information. Must be called before getting any texture properties such as getHasTransparency(), getTextureTransformation() and applyTexture().
        
        This method should be called from MPxSurfaceShapeUI.getDrawRequests().
        The draw data argument is the MDrawData for the request that will carry the texture information to the MPxSurfaceShapeUI.draw() method.
        
        * data (MDrawData) - draw request data to carry the texture information
        """
    
        pass
    
    
    def getDiffuse(*args, **kwargs):
        """
        getDiffuse() -> MColor
        
        Get the GL diffuse color.
        """
    
        pass
    
    
    def getEmission(*args, **kwargs):
        """
        getEmission() -> MColor
        
        Get the GL emission color.
        """
    
        pass
    
    
    def getHasTransparency(*args, **kwargs):
        """
        getHasTransparency() -> bool
        
        Returns True if material or texture has transparency, False otherwise.
        """
    
        pass
    
    
    def getHwShaderNode(*args, **kwargs):
        """
        getHwShaderNode() -> MPxHwShaderNode
        
        Get the hardware shader node.
        """
    
        pass
    
    
    def getShininess(*args, **kwargs):
        """
        getShininess() -> float
        
        Get the GL shininess.
        """
    
        pass
    
    
    def getSpecular(*args, **kwargs):
        """
        getSpecular() -> MColor
        
        Get the GL specular color.
        """
    
        pass
    
    
    def getTextureTransformation(*args, **kwargs):
        """
        getTextureTransformation(data, texXform) -> self
        getTextureTransformation(data) -> [float, float, float, float, float, float]
        
        Get the current textures transformation.
        
        * data (MDrawData) - the draw data from the draw request
        * texXform [OUT] (MMatrix) - storage for the texture transformation
        
        Or
        * data (MDrawData) - the draw data from the draw request
        Returns the transformations values:
           rotateUV (float) - storage for rotatation value of the UV coordinates
           scaleU (float) - storage for u scale value
           scaleV (float) - storage for v scale value
           translateU (float) - storage for u translation value
           translateV (float) - storage for v translation value
           rotateFrame (float) - storage for rotatation value of the frame coordinates
        """
    
        pass
    
    
    def materialIsTextured(*args, **kwargs):
        """
        materialIsTextured() -> bool
        
        Returns True if the material is textured, False otherwise.
        """
    
        pass
    
    
    def setMaterial(*args, **kwargs):
        """
        setMaterial(path, hasTransparency) -> self
        
        Set the current GL material.
        
        * path (MDagPath) - path to the object
        * hasTransparency (bool) - whether the material has transparency
        """
    
        pass
    
    
    def shadingEngine(*args, **kwargs):
        """
        shadingEngine() -> MObject
        
        Get the shading engined associated with this material.
        """
    
        pass
    
    
    def textureImage(*args, **kwargs):
        """
        textureImage(image, color, chan, dagPath, xRes=-1, yRes=-1) -> self
        
        For materials that have texture, this method will attempt to retrieve the pixel map for a given mapped channel of that material.
        Will fails If the channel is not mapped.
        
        The material types that can be queried include:
          - Lambert
          - Phong
          - PhongE
          - Anisotropic
          - Blinn
        
        Currently only channels mapped to single file textures is supported.
        
        * image [OUT] (MImage) - The image retrieved. If no image could be retrieve, the value will not change.
        * color [OUT] (MColor) - Either the mapped or unmapped color. If the channel is mapped then an RGBA value of (1,1,1,1) will be returned, otherwise the unmapped channel's current color value will be returned.
        * chan (int) - Texture channel to check.
        * dagPath (MDagPath) - Optional dag path to object. An object path is required to produce texture maps from non-2D procedural textures.
        * xRes (int) - Optional width of image to create. The minimal allowed value is 2. This parameter only applies to procedural textures. The dimension in X will be 128 by default, if a value less than 2 is specified.
        * yRes (int) - Optional height of image to create. The minimal allowed value is 2. This parameter only applies to procedural textures. The dimension in Y will be 128 by default, if a value less than 2 is specified.
        
        Valid Texture channel:
          kColor
          kTransparency
          kAmbientColor
          kIncandescence
          kBumpMap
          kDiffuse
          kTransluscence
          kRoughness           PhongE only
          kHighlightSize       PhongE only
          kWhiteness           PhongE only
          kCosinePower         Phong only
          kEccentricity        Blinn only
          kSpecularRollOff     Blinn only
          kSpecularColor       Blinn and Phong(E) only
          kReflectivity        Blinn and Phong(E) only
          kReflectedColor      Blinn and Phong(E) only
        """
    
        pass
    
    
    def defaultMaterial(*args, **kwargs):
        """
        defaultMaterial() -> MMaterial
        
        Get the default material. There will always be a default material in the scene and therefore the result of this function should always succeed.  The default material will correspond to the initialShadingGroup node that is in the scene.
        """
    
        pass
    
    
    __new__ = None
    
    
    kAmbientColor = 2
    
    
    kBumpMap = 4
    
    
    kColor = 0
    
    
    kCosinePower = 10
    
    
    kDiffuse = 5
    
    
    kEccentricity = 11
    
    
    kHighlightSize = 8
    
    
    kIncandescence = 3
    
    
    kReflectedColor = 15
    
    
    kReflectivity = 14
    
    
    kRoughness = 7
    
    
    kSpecularColor = 13
    
    
    kSpecularRollOff = 12
    
    
    kTransluscence = 6
    
    
    kTransparency = 1
    
    
    kWhiteness = 9


class MPxHwShaderNode(_MPxNode):
    """
    Base class for user defined hardware shaders.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def bind(*args, **kwargs):
        """
        bind(request, view) -> self
        
        This method is invoked for hardware rendering to Maya's 3D view.
        
        This is the preferred method of interactive feedback and performance. the "gl" version should be used for batch hardware rendering.
        
        This method is called to set up the OpenGL state.  It would typically ensure that textures were bound and that any specific OpenGL extensions are enabled.  A status code of MS::kSuccess should be returned unless there was a problem during the display, such as insufficient memory or required input data is missing or invalid.
        
        * request (MDrawRequest) - the draw request.
        * view (M3dView) - the view in which to draw.
        """
    
        pass
    
    
    def colorsPerVertex(*args, **kwargs):
        """
        colorsPerVertex() -> int
        
        This method returns the number of color values per vertex that the hw shader node would like to receive from Maya.  Maya will attempt to provide all the color data that the shader would like but it will never provide more data that is actually available in the shape.  The color sets returned by getColorSetNames() will override the number of color sets specified by colorsPerVertex(). If you do not override this method or getColorSetNames(), Maya will provide no colors per vertex.
        
        Returns the number of color values desired
        """
    
        pass
    
    
    def currentPath(*args, **kwargs):
        """
        currentPath() -> MDagPath
        
        This method returns a reference to the current path that the shader is invoked for.
        
        The path is only valid before a call to any of the attribute specifying routines:
        
           normalsPerVertex()
           colorsPerVertex()
           getColorSetNames()
           texCoordsPerVertex()
           getTexCoordSetNames()
           hasTransparency()
           provideVertexIDs()
        
        The path is not guaranteed to be valid at any other time.
        
        This method allows the plugin to return attribute queries which are relative to a specific path or object.
        
        For example, the plugin can retrieve the MObject from the path, then use the MFnMesh class on the MObject, assuming the object is a polygonal surface. Through MFnMesh the code can query the actual number of texture coordinate sets on the surface and return appropriate values for the getTexCoordSetNames() routine.
        
        The [gl]bind(), [gl]unbind() and [gl]geometry() routines already have access to a dag path which is the same path as the one which can be retrieved via this method.
        
        For performance reasons, it is recommended that for those methods the MDagPath passed in as an argument should be used.
        
        Returns an MDagPath. Note that this path can be invalid
        Use MDagPath.isValid() to confirm the validity of the path.
        """
    
        pass
    
    
    def currentShadingEngine(*args, **kwargs):
        """
        currentShadingEngine() -> MObject
        
        This method returns an MObject to the shading engine that is currently being rendered. This method will only return a valid MObject during the following calls:
        
          normalsPerVertex()
          colorsPerVertex()
          getColorSetNames()
          texCoordsPerVertex()
          getTexCoordSetNames()
          hasTransparency()
          provideVertexIDs()
          getAvailableImages()
          bind(), glBind()
          geometry(), glGeometry()
          unbind(), glUnbind()
        """
    
        pass
    
    
    def dirtyMask(*args, **kwargs):
        """
        dirtyMask() -> int
        
        This method returns a "dirty" mask that indicates which geometry items have changed from the last invocation of the plugin to draw. The mask is valid at the time that geometry() or glGeometry() is called and at no other time.
        
        Note that this mask is relative to the geometry for the current object (path) being drawn by the shader. The current path is the MDagPath argument passed in via the geometry routines.
        
        In general the mask will mark the geometry as not being dirty.
        
        Scenarios where the geometry will be marked dirty include:
        
          Whenever a geometry attribute changes. For example positions or normals are modified.
          Whenever the attributes being requested changes from the previous invocation of the shader. For example, if in the previous invocation the plugin asks for position only, and in the current invocation asks for position and normals, then the geometry attributes returned will have changed and thus be marked "dirty".
        
        Returns the dirty mask which can be bit 'AND'ed against the values:
          kDirtyNone
          kDirtyVertexArray
          kDirtyNormalArray
          kDirtyColorArrays
          kDirtyTexCoordArrays
          kDirtyAll
        """
    
        pass
    
    
    def geometry(*args, **kwargs):
        """
        geometry(request, view, prim, writable, indexCount, indexArray, vertexCount, vertexIDs, vertexArray, normalCount, normalArrays, colorCount, colorArrays, texCoordCount, texCoordArrays) -> self
        
        This method is invoked for hardware rendering to Maya's 3D view.
        
        This is the preferred method of interactive feedback and performance. the "gl" version should be used for batch hardware rendering.
        
        This method does all the actual OpenGL drawing.  The arguments contain all the data to successfully call glDrawElements or glDrawRangeElements.  It is possible that there will be multiple calls to this method surrounded by a single call to bind() and unbind().
        
        Note 1.
        The array of vertex IDs returned corresponds to each triangle's vertex. This allows access to associated blind data per vertex. The vertexIDs array allows querying of information such as color per vertex etc.
        
        Note 2.
        The arrays passed to this method can contain sparse information.  Check array positions against None to ensure that the array information item is valid.
        
        It is necessary to use the indexArray to access information contained in the data arrays.
        
        * request (MDrawRequest) - the draw request.
        * view (M3dView) - the view in which to draw.
        * prim (int) - the type of primitive to draw.  This is one of the values accepted by glBegin().  Typically it will be GL_TRIANGLES but it could be any of the others.
        * writable (int) this is a mask which indicates which of the various array arguments can be modified in place.  If a bit in writable is set then you can modify corresponding data array (after casting it to a non-const type).  If the bit is not set in writable then you must not> modify the data since it points to internal Maya storage.  You can test the bits in writeable against the values
        :  kWriteNone
          kWriteVertexArray
          kWriteNormalArray
          kWriteColorArrays
          kWriteTexCoordArrays
          kWriteAll
        * indexCount (int) - specifies both the number of indices to draw and the size of the indexArray argument.
        * indexArray (buffer of int values) - the array of index values.  This array is in a format suitable for passing as the indices argument to glDrawElements() or glDrawRangeElements().  See the OpenGL documentation for details on calling these routines.
        * vertexCount (int) - the number of elements in the vertexArray, the normalArray, each of the colorArrays, and each of the texCoordArrays.
        * vertexIDs (buffer - int values) - the component IDs of the vertices in vertexArray. This array is only provided if it was requested by overriding the provideVertexIDs() method to return True.
        * vertexArray (buffer - float values) - the array of vertex data.  Currently, this is always 3 element floating point values.  This data is in a format suitable for passing to glVertexPointer().  See the OpenGL documentation for details.
        * normalCount (int) - the number of individual "normal" arrays that are being provided in normalArrays.  See the description of normalsPerVertex method below for details.
        * normalArrays (array of buffer - float values) - the normal (and tangent) data suitable. There may be 0, 1, 2, or 3 "normal" arrays.  See the description of the normalsPerVertex method below for details.
        * colorCount (int) - the number of individual color arrays.
        * colorArrays (array of buffer - float values) - the arrays of color data.  The first set of color data is pointed to by colorArrays[0].  Each color array contains vertexCount color values, each of which is 4 floating point values long and represents the red, green, blue, and alph values on a 0 to 1 scale.  Each individual array is suitable for passing to glColorPointer().
        * texCoordCount (int) - the number of texture coordinate arrays. Each array contains one set of UV texture coordinates.
        * texCoordArrays (array of buffer - float values) - the arrays of texture coordinate data. The first set of texture coordinate data is pointed to by texCoordArrays[0].  Each array contains vertexCount coordinate values, each of which is 2 floating point values long.  Each individual array is suitable for passing to glTexCoordPointer().
        """
    
        pass
    
    
    def getAvailableImages(*args, **kwargs):
        """
        getAvailableImages(uvSetName) -> list of strings/None
        
        Maya will call this method to get your shader's list of images which are available for use in the UV texture editor for the UV set specified. Typically, this list will include one entry for each texture using the specified UV set, however, your shader is free to return as many images as you wish (for example, blending between two textures, texture alpha masks, artificially shaded views of bump/normal maps, etc). Your shader's renderImage() method will be used to render the images themselves.
        
        * uvSetName (string) - Name of a UV set the channel list should be filtered against.
        
        Returns the names of the images this shader defines which are valid for the uvSetName specified.
        Returns None if method is not implemented : Use the default behaviour.
        """
    
        pass
    
    
    def getColorSetNames(*args, **kwargs):
        """
        getColorSetNames(names) -> int
        
        This method returns an array of color per vertex set names. Maya will attempt to provide color per vertex data from these maps in the corresponding array element in the colorArrays argument to the geometry method.  For example, if the names[2] is "cpv56" then colorArrays[2] will be the array of values from cpv56, or None if the shape being rendered does not have a color set of that name. Ifthis method is not overridden an empty list of names will be returned,and Maya will use colorsPerVertex() to determine how many color setsto provide.
        
        * names [IN/OUT] (list of string) - a string array holding the names of the color per vertex sets from which color data should be extracted.
        
        Returns the number of elements in the names array.
        """
    
        pass
    
    
    def getTexCoordSetNames(*args, **kwargs):
        """
        getTexCoordSetNames(names) -> int
        
        This method returns an array of texture coordinate set names. Maya will attempt to provide texture coordinates from these maps in the corresponding array element in the texCoordArrays argument to the geometry method.  For example, if the names[2] is "uvSet3" then texCoordArrays[2] will be the array of values from uvSet3. If this method is not overridden an empty list of names will be returned, and Maya will use texCoordsPerVertex() to determine how many uv sets to provide.
        
        * names [IN/OUT] (list of string) - a string array holding the names of the uvSets from which texture coordinate data should be extracted.
        
        Returns the number of elements in the names array.
        """
    
        pass
    
    
    def glBind(*args, **kwargs):
        """
        glBind(shapePath) -> self
        
        This method should only be overridden for hardware rendering.
        
        The implementation can assume the graphics context and model view projection matrix have already been set.
        
        This method will be invoked once per frame and should be overridden to allocate any resources needed for the draw. For example, binding vertex programs, fragment programs, or allocating textures. A status code of MS::kSuccess should be returned unless there was a problem such as insufficient memory or required input data is missing or        invalid.
        
        * shapePath (MDagPath) - Path to the surface being drawn.
        """
    
        pass
    
    
    def glGeometry(*args, **kwargs):
        """
        glGeometry(shapePath, prim, writable, indexCount, indexArray, vertexCount, vertexIDs, vertexArray, normalCount, normalArrays, colorCount, colorArrays, texCoordCount, texCoordArrays) -> self
        
        This method should only be overridden for hardware rendering.
        
        The implementation can assume graphics context and model view projection matrix have already been set.
        
        This method does all the actual OpenGL drawing.  The arguments contain all the data to successfully call glDrawElements or glDrawRangeElements.  It is possible that there will be multiple calls to this method surrounded by a single call to bind() and unbind().
        
        Note 1.
        The array of vertex IDs returned corresponds to each triangle's vertex. This allows access to associated blind data per vertex. The vertexIDs array allows querying of information such as color per vertex etc.
        
        Note 2.
        The arrays passed to this method can contain sparse information.  Check array positions against None to ensure that the array information item is valid.
        
        It is necessary to use the indexArray to access information contained in the data arrays.
        
        * shapePath (MDagPath) - Path to the surface being drawn.
        See geometry() description for detail on the other parameters.
        """
    
        pass
    
    
    def glUnbind(*args, **kwargs):
        """
        glUnbind(shapePath) -> self
        
        This method should only be overridden for hardware rendering.
        
        The implementation can assume the graphics context and model view projection matrix have already been set.
        
        This method will be invoked once per frame and should be overridden to deallocate any resources used to draw. It's important that all resources be released when a batch hardware render has occured because the graphics context will be deleted. It may be desireable to override the other version of bind/unbind to keep track of whether the draw is for the 3D view or the batch hardware renderer. This information could then be used to better track the reuse of resources and optimize performance.
        
        A status code of MS::kSuccess should be returned unless there was a problem.
        
        * shapePath (MDagPath) - Path to the surface being drawn.
        """
    
        pass
    
    
    def hasTransparency(*args, **kwargs):
        """
        hasTransparency() -> bool
        
        This method returns a boolean value that indicates whether the object will be drawn transparently or not.  Transparent objects must be drawn after all the opaque objects in the scene or they will not display correctly.  Maya uses the return value to determine when it can draw this shape.
        
        Note : The functionality in this method has been subsumed by the transparencyOptions() method. It is recommended that shader node writers use this newer method as it provides greater control over how transparency is interpreted by Maya's refresh mechanism.
        
        For backward compatibility, if this method is specified and returns True, it will override the transparencyOptions() method.
        
        Returns True if the object will be transparent or False if it will not.
        """
    
        pass
    
    
    def invertTexCoords(*args, **kwargs):
        """
        invertTexCoords() -> bool
        
        Specifies whether this shader requires inverted texture coordinates. (i.e. where the top-left hand corner of UV space is (0,0) instead of the bottom-left corner).
        
        By default, this method will return False to ensure compatibility with existing shader code.
        """
    
        pass
    
    
    def normalsPerVertex(*args, **kwargs):
        """
        normalsPerVertex() -> int
        
        Specifies how many normals per vertex the HW shader would like Maya to provide.  This can range from 0 to 3.  The first normal is the surface normal.  The second "normal" is the primary tangent (generally the "u" direction).  The third "normal" is the secondary tangent or the binormal (generally the "v" direction). Together, the normal, tangent and binormal form an orthogonal basis frequently named "tangent space basis".
        
        The tangent and binormal vectors are guaranteed to be normalized and orthogonal to the surface normal. Please note that extracting the tangent and/or binormal requires expensive calculations, that will slow down refresh time substantially. In a future version, Maya may cache the resulting tangent space basis; in the meantime, only ask for more than one normal per vertex if they are absolutely required.
        
        Also note that the tangent and binormal calculation requires a uv map. Currently, they are always computed from the first available uv map; if there is no uv mapping on the surface, Maya will only provide surface normals in the geometry call, regardless of the value returned by normalsPerVertex().
        
        If you do not override this method, Maya will provide 1 normal per vertex.
        
        Maya will automatically and silently clamp the result of this function to the [0,3] range.
        
        COMPATIBILITY NOTE: Automatic tangent space basis calculation is only supported starting with Maya 4.0.1. Maya 4.0 supported a different scheme that was much more complicated and no longer supported.
        
        Returns the number of normal values desired. (0 = none, 1 = surface normal only, 2 = surface normal + tangent, 3 = surface normal + tangent + binormal)
        """
    
        pass
    
    
    def provideVertexIDs(*args, **kwargs):
        """
        provideVertexIDs() -> bool
        
        This method returns a boolean value that indicates whether a map of the vertex IDs will be provided to the geometry method.
        
        Returns True if vertex IDs should be provided to the geometry method.
        """
    
        pass
    
    
    def renderImage(*args, **kwargs):
        """
        renderImage(imageName, region, parameters) -> [int, int]/None
        renderImage(uiDrawManager, imageName, region, parameters) -> [int, int]/None
        
        This method allows you to to render the background image used for this shader in the UV texture editor. The image requested will be one of the image names returned by your shader's getAvailableImages() method.
        
        The implementation must return the dimensions of the image in the 'imageWidth' and 'imageHeight' parameters so that Maya can perform pixel snapping and other resolution-dependent operations.
        
        The implementation can assume OpenGL context, model view projection matrix, and texture transformations have already been set. A default color of white will be set, however you are free to change this. The magnification filter will be set to either point or bilinear based on user configuration and should not be modified. The values of GL_TEXTURE_WRAP_S and GL_TEXTURE_WRAP_T are undefined on entry, and your implementation is responsible for setting them to appropriate values (e.g. GL_REPEAT).
        
        The arguments contain the name of the image to render, and the vertex and texture coordinate values to use at each corner of the rectangular image being rendered. Your implementation is responsible for restoring the original the value of any OpenGL state that is modified.
        
        * imageName (string) - Name of the image to render. This corresponds to one of the image names returned by your shader's getAvailableImages() method.
        * region (float[2][2]) - Rectangular region to be rendered. The values of this parameter should be used to populate the vertex and texture coordinates of the rectangle being rendered.
        * parameters (RenderParamters) - Additional parameters on how to render the image. The values reflect the image settings of the UV editor.
        
        A second version with the uiDrawManager parameter allows you to to render the background image used for this shader in the UV texture editor in viewport 2.0.
        
        * uiDrawManager (MUIDrawManager) - The UI draw manager, it can be used to draw some simple geometry
        
        Returns None if method is not implemented : No rendering will occur.
        """
    
        pass
    
    
    def renderSwatchImage(*args, **kwargs):
        """
        renderSwatchImage(image) -> self/None
        
        If the shader specifies to override swatch rendering, then this method must be overridden in order to draw anything into a swatch.
        
        The shader will only draw a swatch if it has been registered to do so, by providing a valid classification during MFnPlugin::registerNode(). The shader should provide a classification that defines a swatch rendering node such as : "shader/surface/utility/:drawdb/shader/surface/myCustomShader:swatch/myCustomShaderSwatchGenerator" and have "myCustomShaderSwatchGenerator" registered has a swatch renderer : MSwatchRenderRegister.registerSwatchRender("myCustomShaderSwatchGenerator", MHWShaderSwatchGenerator.createObj );
        
        The default implementation is to draw nothing. The basic logic to draw a swatch is as follows:
        
          Determine the size of the swatch required. This is the dimensions of the MImage passed in as an argument. The pixels for the MImage will have been pre-allocated. The format of the pixels is 32-bit R,G,B,A, with 8-bits per channel.
          Either use an offscreen "swatch context" provided to you or use your own offscreen context. The provided context is available via the MHardwareRenderer class method makeSwatchContextCurrent(). Note that the swatch context may be smaller than the desired image size. In this case the rendering dimensions will be clamped.
          Either use swatch geometry provided to you, or use your own swatch geometry. The provided geometry is available via the method MHardwareRenderer::referenceDefaultGeometry(). The possible "default" geometries are either a sphere, cube or plane.
          Either use the provided "default" light and "default" camera or set up your own. Use the methods (getSwatchOrthoCameraSetting(), getSwatchLightDirection()) on MHardwareRenderer to get these defaults.
          Read back the swatch context into the provided MImage. The convenience method MHardwareRenderer::readSwatchContextPixels() can be used. By default the format of the MImage and the swatch context are the same, so the user does not need to worry about this. The context will read into the pre-allocated MImage pixels.
          Unreference any swatch geometry used for rendering using MHardwareRenderer::dereferenceGeometry().
        
        * image [IN/OUT] (MImage) - Image object to which this method must write the rendered swatch. On input the image's dimensions are already set and pixel storage already allocated.
        
        Returns None if method is not implemented : No rendering will occur.
        """
    
        pass
    
    
    def supportsBatching(*args, **kwargs):
        """
        supportsBatching() -> bool
        
        Specifies whether or not this shader supports batched rendering of shapes.
        
        In normal rendering, a shader is invoked using bind/geometry/unbind (or glBind/glGeometry/glUnbind) once for each shape being rendered. When a shader is used in batched rendering mode however, bind is called once, a series of geometry calls are made for each shape being rendered, followed by a single call to unbind (and similarly for glBind, glGeometry and glUnbind). As shader binding/unbinding can be expensive, batched rendering can significantly improve rendering performance. The more (particularly expensive) operations that can be moved out of the geometry/glGeometry methods the greater the performance improvement is. Ideally, only shape specific operations (such as binding geometry arrays and shape matrices) should be left in the geometry methods.
        
        It is important to note that your shader can only use batched rendering mode if there is no shape (i.e. dag path) specific code in bind, glBind, unbind, or glUnbind. If any of these methods perform shape specific processing, this code must either be moved into geometry/glGeometry, or you must return False in this method to indicate batching should be disabled for this shader.
        
        By default, this method will return False to ensure compatibility with existing shader code.
        """
    
        pass
    
    
    def texCoordsPerVertex(*args, **kwargs):
        """
        texCoordsPerVertex() -> int
        
        This method returns the number of texture coordinate values per vertex that the hw shader node would like to receive from Maya. Maya will attempt to provide all the texture coordinate data that the shader would like but it will never provide more data than is actually available in the shape.  The uv sets returned by getTexCoordSetNames() will override the number of uv sets specified by texCoordsPerVertex(). If you do not override this method or getTexCoordSetNames(), Maya will provide no texture coordinates per vertex.
        
        Note: Currently, Maya only retains 2 dimensional texture coordinate data but this may change in a future release.
        
        Returns the number of texture coordinate values desired
        """
    
        pass
    
    
    def transparencyOptions(*args, **kwargs):
        """
        transparencyOptions() -> int
        
        This method returns transparency options for usage as hints for Maya's internal draw during a given rendering pass. Parameters are returned via an integer containing masked out bits. By default the mask is set to 0, meaning that the drawing should be treated as regular opaque object drawing. This will generally mean one call per draw pass.
        
        Options to control transparency are specified by returning one or more masks specified by the values
        :
        
          kIsTransparent : Draw as a transparent object. If no transparency overrides are specified, then control of how to draw during a given pass is determined internally by Maya's refresh algorithm, and options the user can set per modelling viewport.
          kNoTransparencyFrontBackCull : When kisTransparent is set and this flag is set, do not perform transparency drawing using the internal 2-pass front-face + back-face culling algorithm.
          kNoTransparencyPolygonSort : When kisTransparent is set and this flag is set, do not perform transparency drawing using the internal 2-pass drawing of back-to-front sorted triangles.
        
        Note : Setting the "hasTransparency()" method to True will override this method. This is for backward compatibility with behaviour on existing hardware shader nodes. It is recommended that shaders use the "transparencyOptions()" override, and not longer use the older "hasTransparency()" override from their shader classes.
        
        Retuns an integer containing the appropriate options set via masks.
        """
    
        pass
    
    
    def unbind(*args, **kwargs):
        """
        unbind(request, view) -> self
        
        This method is invoked for hardware rendering to Maya's 3D view.
        
        This is the preferred method of interactive feedback and performance. the "gl" version should be used for batch hardware rendering.
        
        This method is called to restore the OpenGL state.  Specifically, it must disable any OpenGL extensions that the matching bind() method may have enabled.  This is necessary to ensure that the rest of Maya's drawing code continues to work correctly.  A status code of MS::kSuccess should be returned unless there was a problem such as insufficient memory or required input data is missing or invalid.
        
        The arguments passed to this method are the same ones that were passed to the bind() method.
        
        * request (MDrawRequest) - the draw request.
        * view (M3dView) - the view in which to draw.
        """
    
        pass
    
    
    def getHwShaderNode(*args, **kwargs):
        """
        getHwShaderNode(object) -> MPxHwShaderNode
        
        This is a static convenience method to be able to get an MPxHwShaderNode from an MObject provided by a swatch generator class (Class derived from MSwatchRenderRegister).
        
        * object (MObject) - The object to examine.
        """
    
        pass
    
    
    __new__ = None
    
    
    kDirtyAll = 15
    
    
    kDirtyColorArrays = 4
    
    
    kDirtyNone = 0
    
    
    kDirtyNormalArray = 2
    
    
    kDirtyTexCoordArrays = 8
    
    
    kDirtyVertexArray = 1
    
    
    kIsTransparent = 1
    
    
    kNoTransparencyFrontBackCull = 2
    
    
    kNoTransparencyPolygonSort = 4
    
    
    kWriteAll = 15
    
    
    kWriteColorArrays = 4
    
    
    kWriteNone = 0
    
    
    kWriteNormalArray = 2
    
    
    kWriteTexCoordArrays = 8
    
    
    kWriteVertexArray = 1
    
    
    outColor = None
    
    
    outColorB = None
    
    
    outColorG = None
    
    
    outColorR = None
    
    
    outGlowColor = None
    
    
    outGlowColorB = None
    
    
    outGlowColorG = None
    
    
    outGlowColorR = None
    
    
    outMatteOpacity = None
    
    
    outMatteOpacityB = None
    
    
    outMatteOpacityG = None
    
    
    outMatteOpacityR = None
    
    
    outTransparency = None
    
    
    outTransparencyB = None
    
    
    outTransparencyG = None
    
    
    outTransparencyR = None


class MPxLocatorNode(_MPxNode):
    """
    Base class for user defined locators.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def boundingBox(*args, **kwargs):
        """
        boundingBox() -> MBoundingBox
        
        This method should be overridden to return a bounding box for the locator.
        If this method is overridden, then MPxLocatorNode.isBounded should also be overridden to return True.
        """
    
        pass
    
    
    def closestPoint(*args, **kwargs):
        """
        closestPoint(rayPoint, rayDir) -> MPoint
        
        Returns the point on the locator, in the locator's local space, which is closest along the specified ray.
        
        By default, the locator's origin (0, 0, 0) is returned.
        
        This is currently only used by Maya during single selection. See useClosestPointForSelection() for further details on that.
        
        * rayPoint (MPoint) - The base point defining the ray in space
        * rayDir (MVector) - The ray direction in space
        """
    
        pass
    
    
    def color(*args, **kwargs):
        """
        color(status) -> int
        
        This method returns the index of the color that is the default draw color for the given display status.  The index should be used with the methods of M3dView.  The value is not an index into the OpenGL color table. 
        
        The index that is returned will be into the active, dormant, or template color tables depending on the display status passed in.
        
        * displayStatus (int) - display status. See M3dView.displayStatus() for a list of valid status.
        """
    
        pass
    
    
    def colorRGB(*args, **kwargs):
        """
        colorRGB(status) -> MColor
        
        This method returns the RGB values of the default draw color for the given display status.
        
        * displayStatus (int) - display status. See M3dView.displayStatus() for a list of valid status.
        """
    
        pass
    
    
    def draw(*args, **kwargs):
        """
        draw(view, path, style, status) -> self
        
        Overriding this method allows the drawing of custom geometry using standard OpenGL calls.  The OpenGL state should be left in the same state that it was in previously.  The OpenGL routine glPushAttrib may be used to make this easier.
        
        When this routine is called, the following conditions may be assumed:
         - the correct transform matrix will be loaded for the locator, so the geometry should be drawn in local space
         - the correct default color will be set for wire frame drawing given the object's state (eg active, dormant, etc.)
         - the object is not invisible or hidden
         - if the object has a bounding box, then the bounding box is at least partially in the frustum
        
        
        As a convenience, this draw method will also be used by OpenGL's selection mechanism to determine whether this object gets selected by a particular mouse event.  The user does not need to write a separate selection routine.
        
        * view (M3dView) - 3D view that is being drawn into.
        * path (MDagPath) - to the parent (transform node) of this locator in the DAG.
        If there is a shape node parented directly beneath the transform node, you can access it 
        by calling MDagPath.extendToShape(). 
        * style (int) - style to draw object in. See M3dView.displayStyle() for a list of valid styles.
        * status (int) - selection status of object. See M3dView.displayStatus() for a list of valid status.
        """
    
        pass
    
    
    def drawLast(*args, **kwargs):
        """
        drawLast() -> bool
        
        Indicates that this locator should be the last item draw in a given refresh cycle.  Objects drawn out-of-order will not preserve the proper transparency sorting.  Conflicts among multiple objects with the drawLast indicator set to TRUE will be resolved by their order in the Outliner, where they will be drawn top-to-bottom.
        
        The default return value is True.
        """
    
        pass
    
    
    def excludeAsLocator(*args, **kwargs):
        """
        excludeAsLocator() -> bool
        
        When the modelPanel is set to not draw locators, returing True will also not draw the custom locator. If False is returned, the custom locator will also be drawn.
        
        The default return value is True.
        """
    
        pass
    
    
    def getShapeSelectionMask(*args, **kwargs):
        """
        getShapeSelectionMask() -> MSelectionMask
        
        This routine can be overridden to provide information aboutthe selection mask of the locator. By default the selection maskfor locators is returned.
        """
    
        pass
    
    
    def isBounded(*args, **kwargs):
        """
        isBounded() -> bool
        
        This method should be overridden to return True if the user supplies a bounding box routine.  Supplying a bounding box routine makes refresh and selection more efficient.
        """
    
        pass
    
    
    def isTransparent(*args, **kwargs):
        """
        isTransparent() -> bool
        
        Indicates that this locator uses transparency during ::draw method calls. Objects with transparency must be drawn in a special queue, i.e. after all opaque objects are drawn.
        
        The default return value is False.
        """
    
        pass
    
    
    def useClosestPointForSelection(*args, **kwargs):
        """
        useClosestPointForSelection() -> bool
        
        Determines whether Maya should call closestPoint() when doing single selection.
        
        When doing single selection Maya generally chooses the object closest to the selection ray. For locators it first does a hit test by calling the locator's draw method to determine if any part of it lies within the selection box. If the hit test succeeds Maya will add the locator to the list of objects being considered for selection and will use the center of the locator (i.e. its local origin) in determining its distance from the selection ray. This works well for locators which mark a single point in space, with no offset, but may not work as well for more complex locators.
        
        If this method is overridden to return True, then rather than using the locator's center to determine its distance from the selection ray, Maya will pass the ray to the closestPoint() method and use the point it returns. Note that you will have override closestPoint() as well to provide an appropriate point.
        """
    
        pass
    
    
    __new__ = None
    
    
    boundingBoxCenterX = None
    
    
    boundingBoxCenterY = None
    
    
    boundingBoxCenterZ = None
    
    
    center = None
    
    
    instObjGroups = None
    
    
    intermediateObject = None
    
    
    inverseMatrix = None
    
    
    isTemplated = None
    
    
    localPosition = None
    
    
    localPositionX = None
    
    
    localPositionY = None
    
    
    localPositionZ = None
    
    
    localScale = None
    
    
    localScaleX = None
    
    
    localScaleY = None
    
    
    localScaleZ = None
    
    
    matrix = None
    
    
    nodeBoundingBox = None
    
    
    nodeBoundingBoxMax = None
    
    
    nodeBoundingBoxMaxX = None
    
    
    nodeBoundingBoxMaxY = None
    
    
    nodeBoundingBoxMaxZ = None
    
    
    nodeBoundingBoxMin = None
    
    
    nodeBoundingBoxMinX = None
    
    
    nodeBoundingBoxMinY = None
    
    
    nodeBoundingBoxMinZ = None
    
    
    nodeBoundingBoxSize = None
    
    
    nodeBoundingBoxSizeX = None
    
    
    nodeBoundingBoxSizeY = None
    
    
    nodeBoundingBoxSizeZ = None
    
    
    objectColor = None
    
    
    objectGroupColor = None
    
    
    objectGroupId = None
    
    
    objectGroups = None
    
    
    objectGrpCompList = None
    
    
    parentInverseMatrix = None
    
    
    parentMatrix = None
    
    
    underWorldObject = None
    
    
    useObjectColor = None
    
    
    visibility = None
    
    
    worldInverseMatrix = None
    
    
    worldMatrix = None
    
    
    worldPosition = None
    
    
    worldPositionX = None
    
    
    worldPositionY = None
    
    
    worldPositionZ = None


class MSelectInfo(MDrawInfo):
    """
    Selection state information used in MPxSurfaceShapeUI.select.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addSelection(*args, **kwargs):
        """
        addSelection(item, point, list, points, mask, isComponent) -> self
        
        Adds components or objects to the active selection list.
        
        * item (MSelectionList) - The component or object to add to the list
        * point (MPoint) - The world space point representing the selected object. This is used during single-click selection when the click overlaps multiple objects in order to determine which point is closest to the camera.
        * list [OUT] (MSelectionList) - The selection list to add the item(s) to
        * points [OUT] (MPointArray) - A copy of the points of all currently selected components in the list (if components are selected)
        * mask (MSelectionMask) - Mask used to determine selection priority
        * isComponent (bool) - Indicates whether item to be added is an object or a component
        """
    
        pass
    
    
    def getAlignmentMatrix(*args, **kwargs):
        """
        getAlignmentMatrix() -> MMatrix
        
        Returns the alignment matrix.
        This method is used to find ray object intersection.
        """
    
        pass
    
    
    def getLocalRay(*args, **kwargs):
        """
        getLocalRay() -> [MPoint, MVector]
        
        Returns the selection ray defined by its starting point (MPoint) and its direction (MVector).
        This method is used to find ray object intersection.
        """
    
        pass
    
    
    def isRay(*args, **kwargs):
        """
        isRay() -> bool
        
        Returns True if there is a selection ray.
        This method isused to find ray object intersection.
        """
    
        pass
    
    
    def selectClosest(*args, **kwargs):
        """
        selectClosest() -> bool
        
        Returns True if we want to select the closest object.
        """
    
        pass
    
    
    def selectForHilite(*args, **kwargs):
        """
        selectForHilite(mask) -> bool
        
        Given the selection mask, can this object be selected for the hilite list.
        
        * mask (MSelectionMask) - the mask to test
        """
    
        pass
    
    
    def selectOnHilitedOnly(*args, **kwargs):
        """
        selectOnHilitedOnly() -> bool
        
        Returns True if you can only select components if the object is hilited.
        """
    
        pass
    
    
    def selectPath(*args, **kwargs):
        """
        selectPath() -> MDagPath
        
        Returns a path to the item that is being selected.
        """
    
        pass
    
    
    def selectRect(*args, **kwargs):
        """
        selectRect() -> [int, int, int, int]
        
        Get the current selection rectangle dimensions, defined by:
          its lower left corner - x coordinate,
          its lower left corner - y coordinate,
          its width,
          its height.
        """
    
        pass
    
    
    def selectable(*args, **kwargs):
        """
        selectable(mask) -> bool
        
        Given the selection mask, this method determines if the object is selectable.
        
        * mask (MSelectionMask) - the mask to test
        """
    
        pass
    
    
    def selectableComponent(*args, **kwargs):
        """
        selectableComponent(displayed, mask) -> bool
        
        Given the selection mask, this method determines if the component is selectable.
        
        * displayed (bool) - is the component displayed
        * mask (MSelectionMask) - selection mask
        """
    
        pass
    
    
    def setSnapPoint(*args, **kwargs):
        """
        setSnapPoint(point) -> bool
        
        When a snapping operation is being performed the shape's overridden MPxSurfaceShapeUI.snap() method can call this method to set the point to be snapped to. If setSnapPoint() is called multiple times then the point passed in which is nearest to the current cursor location will be used. So the shape can either compute the snap point itself and call setSnapPoint() once or it can make a series of calls and let setSnapPoint() determine the closest of those for itself.
        
        * point (MPoint) - The point to be snapped to, must be given in world space coordinates.
        """
    
        pass
    
    
    def singleSelection(*args, **kwargs):
        """
        singleSelection() -> bool
        
        This method determines if we want to select a single object.
        """
    
        pass
    
    
    def view(*args, **kwargs):
        """
        view() -> M3dView
        
        Returns the view that the current selection is taking place in.
        """
    
        pass
    
    
    highestPriority = None
    
    __new__ = None


class MHWShaderSwatchGenerator(_MSwatchRenderBase):
    """
    Hardware shader swatch generator utility class.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
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
    
    
    def createObj(*args, **kwargs):
        """
        createObj(obj, renderObj, res) -> MSwatchRenderBase
        
        Class constructor.
        Saves the Node object and image resolution as data members for future use.
        
        * obj (MObject) - The node object for which the swatch needs to be generated.
        * renderObj (MObject) - The node used to actually compute the swatch. In most situations, this can be the same as <b>obj</b>. This parameter can be used to request the computation of the swatch on another node, and display the swatch on the obj node.* resolution (int) - The expected resolution of the swatch image.
        """
    
        pass
    
    
    def getSwatchBackgroundColor(*args, **kwargs):
        """
        getSwatchBackgroundColor() -> MColor
        
        Returns the default background color for the hardware rendered swatch.
        """
    
        pass
    
    
    def initialize(*args, **kwargs):
        """
        initialize() -> string
        
        This method sets a swatch name, and registers a new swatch generator creation function for the swatch name.
        The string returned from this method can be used for node classification purpose.
        """
    
        pass
    
    
    __new__ = None


class _MFnDependencyNode(_MFnBase):
    """
    Function set for operating on dependency nodes.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def absoluteName(*args, **kwargs):
        """
        Returns the absolute name of this node.  The absolute name of a node is the full namespace path starting at (and including) the root namespace, down to (and including) the node itself.  Regardless of relative name mode, absoluteName() will always return a full namespace path prefixed with a leading colon (the root namespace).
        """
    
        pass
    
    
    def addAttribute(*args, **kwargs):
        """
        Adds a new dynamic attribute to the node.
        """
    
        pass
    
    
    def addExternalContentForFileAttr(*args, **kwargs):
        """
        Adds content info to the specified table from a file path attribute.
        """
    
        pass
    
    
    def attribute(*args, **kwargs):
        """
        Returns an attribute of the node, given either its index or name.
        """
    
        pass
    
    
    def attributeClass(*args, **kwargs):
        """
        Returns the class of the specified attribute.
        """
    
        pass
    
    
    def attributeCount(*args, **kwargs):
        """
        Returns the number of attributes on the node.
        """
    
        pass
    
    
    def canBeWritten(*args, **kwargs):
        """
        Returns true if the node will be written to file.
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        Creates a new node of the given type.
        """
    
        pass
    
    
    def dgCallbackIds(*args, **kwargs):
        """
        Returns DG timing information for a specific callback type, broken down by callbackId.
        """
    
        pass
    
    
    def dgCallbacks(*args, **kwargs):
        """
        Returns DG timing information broken down by callback type.
        """
    
        pass
    
    
    def dgTimer(*args, **kwargs):
        """
        Returns a specific DG timer metric for a given timer type.
        """
    
        pass
    
    
    def dgTimerOff(*args, **kwargs):
        """
        Turns DG timing off for this node.
        """
    
        pass
    
    
    def dgTimerOn(*args, **kwargs):
        """
        Turns DG timing on for this node.
        """
    
        pass
    
    
    def dgTimerQueryState(*args, **kwargs):
        """
        Returns the current DG timer state for this node.
        """
    
        pass
    
    
    def dgTimerReset(*args, **kwargs):
        """
        Resets all DG timers for this node.
        """
    
        pass
    
    
    def findAlias(*args, **kwargs):
        """
        Returns the attribute which has the given alias.
        """
    
        pass
    
    
    def findPlug(*args, **kwargs):
        """
        Returns a plug for the given attribute.
        """
    
        pass
    
    
    def getAffectedAttributes(*args, **kwargs):
        """
        Returns all of the attributes which are affected by the specified attribute.
        """
    
        pass
    
    
    def getAffectingAttributes(*args, **kwargs):
        """
        Returns all of the attributes which affect the specified attribute.
        """
    
        pass
    
    
    def getAliasAttr(*args, **kwargs):
        """
        Returns the node's alias attribute, which is a special attribute used to store information about the node's attribute aliases.
        """
    
        pass
    
    
    def getAliasList(*args, **kwargs):
        """
        Returns all of the node's attribute aliases.
        """
    
        pass
    
    
    def getConnections(*args, **kwargs):
        """
        Returns all the plugs which are connected to attributes of this node.
        """
    
        pass
    
    
    def getExternalContent(*args, **kwargs):
        """
        Gets the external content (files) that this node depends on.
        """
    
        pass
    
    
    def hasAttribute(*args, **kwargs):
        """
        Returns True if the node has an attribute with the given name.
        """
    
        pass
    
    
    def hasUniqueName(*args, **kwargs):
        """
        Returns True if the node's name is unique.
        """
    
        pass
    
    
    def isFlagSet(*args, **kwargs):
        """
        Returns the state of the specified node flag.
        """
    
        pass
    
    
    def isNewAttribute(*args, **kwargs):
        """
        Returns True if the specified attribute was added in the current scene, and not by by one of its referenced files.
        """
    
        pass
    
    
    def isTrackingEdits(*args, **kwargs):
        """
        Returns True if the node is referenced or in an assembly that is tracking edits.
        """
    
        pass
    
    
    def name(*args, **kwargs):
        """
        Returns the node's name.
        """
    
        pass
    
    
    def plugsAlias(*args, **kwargs):
        """
        Returns the alias for a plug's attribute.
        """
    
        pass
    
    
    def removeAttribute(*args, **kwargs):
        """
        Removes a dynamic attribute from the node.
        """
    
        pass
    
    
    def reorderedAttribute(*args, **kwargs):
        """
        Returns one of the node's attribute, based on the order in which they are written to file.
        """
    
        pass
    
    
    def setAlias(*args, **kwargs):
        """
        Adds or removes an attribute alias.
        """
    
        pass
    
    
    def setDoNotWrite(*args, **kwargs):
        """
        Used to prevent the node from being written to file.
        """
    
        pass
    
    
    def setExternalContent(*args, **kwargs):
        """
        Changes the location of external content.
        """
    
        pass
    
    
    def setExternalContentForFileAttr(*args, **kwargs):
        """
        Sets content info in the specified attribute from the table.
        """
    
        pass
    
    
    def setFlag(*args, **kwargs):
        """
        Sets the state of the specified node flag.
        """
    
        pass
    
    
    def setName(*args, **kwargs):
        """
        Sets the node's name.
        """
    
        pass
    
    
    def setUuid(*args, **kwargs):
        """
        Sets the node's UUID.
        """
    
        pass
    
    
    def userNode(*args, **kwargs):
        """
        Returns the MPxNode object for a plugin node.
        """
    
        pass
    
    
    def uuid(*args, **kwargs):
        """
        Returns the node's UUID.
        """
    
        pass
    
    
    def allocateFlag(*args, **kwargs):
        """
        Allocates a flag on all nodes for use by the named plugin and returns the flag's index.
        """
    
        pass
    
    
    def classification(*args, **kwargs):
        """
        Returns the classification string for the named node type.
        """
    
        pass
    
    
    def deallocateAllFlags(*args, **kwargs):
        """
        Deallocates all node flags which are currently allocated to the named plugin.
        """
    
        pass
    
    
    def deallocateFlag(*args, **kwargs):
        """
        Deallocates the specified node flag, which was previously allocated by the named plugin using allocateFlag().
        """
    
        pass
    
    
    isDefaultNode = None
    
    isFromReferencedFile = None
    
    isLocked = None
    
    isShared = None
    
    namespace = None
    
    pluginName = None
    
    typeId = None
    
    typeName = None
    
    __new__ = None
    
    
    kExtensionAttr = 3
    
    
    kInvalidAttr = 4
    
    
    kLocalDynamicAttr = 1
    
    
    kNormalAttr = 2
    
    
    kTimerInvalidState = 3
    
    
    kTimerMetric_callback = 0
    
    
    kTimerMetric_callbackNotViaAPI = 6
    
    
    kTimerMetric_callbackViaAPI = 5
    
    
    kTimerMetric_compute = 1
    
    
    kTimerMetric_computeDuringCallback = 7
    
    
    kTimerMetric_computeNotDuringCallback = 8
    
    
    kTimerMetric_dirty = 2
    
    
    kTimerMetric_draw = 3
    
    
    kTimerMetric_fetch = 4
    
    
    kTimerMetrics = 9
    
    
    kTimerOff = 0
    
    
    kTimerOn = 1
    
    
    kTimerType_count = 2
    
    
    kTimerType_inclusive = 1
    
    
    kTimerType_self = 0
    
    
    kTimerTypes = 3
    
    
    kTimerUninitialized = 2


class MUiMessage(_MMessage):
    """
    Class used to register callbacks for UI related messages.
    """
    
    
    
    def add3dViewDestroyMsgCallback(*args, **kwargs):
        """
        add3dViewDestroyMsgCallback(panelName, function, clientData=None) -> id
        
                This method registers a callback for when a particular 3d view gets
        destroyed. The callback is called before the destruction of the view.
        
        The callback function will be passed any client data that was
        provided when the callback was registered
        
         * panelName (string) - Name of panel to which to attach the callback
         * function - callable which will be passed a string indicating the name
           of the panel that contain the 3d view and the clientData object
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def add3dViewPostRenderMsgCallback(*args, **kwargs):
        """
        add3dViewPostRenderMsgCallback(panelName, function, clientData=None) -> id
        
        This method registers a callback for when the 3d view is
        about to display it's rendered contents to the viewport.
        It is called for every refresh of the view, after the scene is drawn,
        but before any 2d adornments are drawn.
        
        The callback function will be passed any client data that was
        provided when the callback was registered.
        
         * panelName (string) - Name of panel to which to attach the callback
         * function - callable which will be passed a string indicating the name
           of the panel that contain the 3d view and the clientData object
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def add3dViewPreRenderMsgCallback(*args, **kwargs):
        """
        add3dViewPreRenderMsgCallback(panelName, function, clientData=None) -> id
        
        This method registers a callback for when a particular 3d view is
        about to render it's contents. It is called before the scene is drawn,
        but after the background has been drawn.
        
        The callback function will be passed any client data that was
        provided when the callback was registered.
        
         * panelName (string) - Name of panel to which to attach the callback
         * function - callable which will be passed a string indicating the name
           of the panel that contain the 3d view and the clientData object
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def add3dViewRenderOverrideChangedCallback(*args, **kwargs):
        """
        add3dViewRenderOverrideChangedCallback(panelName, function, clientData=None) -> id
        
        This method registers a callback for when the render override for a
        particular 3d view changes.
        
        The callback function will be passed any client data that was
        provided when the callback was registered.
        
         * panelName (string) - Name of panel to which to attach the callback
         * function - callable which will be passed 3 strings indicating: the name of
           the panel that contain the 3d view, the name of the old override used to draw
           in the 3d view, the name of the new override used to draw in the 3d view
           , and the clientData object
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def add3dViewRendererChangedCallback(*args, **kwargs):
        """
        add3dViewRendererChangedCallback(panelName, function, clientData=None) -> id
        
        This method registers a callback for when the renderer for a particular 3d
        view changes.
        
        The callback function will be passed any client data that was
        provided when the callback was registered.
        
         * panelName (string) - Name of panel to which to attach the callback
         * function - callable which will be passed 3 strings indicating: the name
           of the panel that contain the 3d view, the name of the old renderer used
           to draw the 3d view, the name of the new renderer used to draw the 3d view
           , and the clientData object
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def addCameraChangedCallback(*args, **kwargs):
        """
        addCameraChangedCallback(panelName, function, clientData=None) -> id
        
        This method registers a callback for cameras being changed in
        3d views.  The callback is called when the camera changes for the
        given panel, not when attributes on the panel's camera change.
        
        The callback function will be passed any client data that was
        provided when the callback was registered.
        
         * panelName (string) - the name of panel to which to attach the
           callback.
         * function - callable which will be passed a string indicating the
           name of the panel that had the camera change, a MObject containing
           the current camera used by the panel and the clientData object
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass
    
    
    def addUiDeletedCallback(*args, **kwargs):
        """
        addUiDeletedCallback(uiName, function, clientData=None) -> id
        
        This method registers a callback for UI deleted messages.
        The callback function will be passed any client data that was
        provided when the callback was registered.
        
         * uiName (string) - the name of the UI object to register the
           callback for
         * function - callable which will be passed the clientData object
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass


class MPaintMessage(_MMessage):
    """
    Class used to register callbacks for paint related messages.
    """
    
    
    
    def addVertexColorCallback(*args, **kwargs):
        """
        addVertexColorCallback(function, clientData=None) -> id
        
        Adds a new callback on vertex color paint.
        
        Note: the 'colors' parameter supplied to the callback function contains a color per vertex, even if the type of the component being painted is faces. To interpret the colors when faces are being painted, it will be necessary to query the vertex count of each face and step over that many vertices while iterating the array.
        
        The callback function will be passed any client data that was
        provided when the callback was registered.
        
         * function - callable which will be passed:
           The DAG path of the object being painted (MDagPath)
           The components (e.g. vertices, faces) being painted (MObject)
           The plug being painted (MPlug)
           The colors that were applied to the components (MColorArray)
         * clientData - User defined data passed to the callback function
        
         * return: Identifier used for removing the callback.
        """
    
        pass


class MPxHardwareShader(_MPxNode):
    """
    Base class for user defined hardware shaders.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def getAvailableImages(*args, **kwargs):
        """
        getAvailableImages(context, uvSetName) -> list of string/None
        
        Maya will call this method to get your shader's list of images which are available for use in the UV texture editor for the UV set specified. Typically, this list will include one entry for each texture using the specified UV set, however, your shader is free to return as many images as you wish (for example, blending between two textures, texture alpha masks, artificially shaded views of bump/normal maps, etc). Your shader's renderImage() method will be used to render the images themselves.
        
        * context (ShaderContext) - Context of the draw request (e.g. the surface being shaded, shading engine making the request)
        * uvSetName (string) - Name of a UV set the channel list should be filtered against.
        
        Returns the names of the images this shader defines which are valid for the uvSetName specified.
        Returns None if method is not implemented : Use the default behaviour.
        """
    
        pass
    
    
    def profile(*args, **kwargs):
        """
        profile() -> MRenderProfile
        
        Override this method to specify the renderers your shader supports. If this method is not overridden, Maya will assume your shader supports only Maya's iternal OpenGL based renderer.
        
        Note that this method is called inside the rendering loop and as such, you should make this method as fast as possible - typically just returning a static/precalculated value.
        
        Return a reference to the render profile for this Shader. Your shader class should create this once (usually for the whole class) and return the same object each time this method is called.
        """
    
        pass
    
    
    def renderImage(*args, **kwargs):
        """
        renderImage(context, imageName, region, parameters) -> [int, int]/None
        renderImage(context, uiDrawManager, imageName, region, parameters) -> [int, int]/None
        
        This method allows you to to render the background image used for this shader in the UV texture editor. The image requested will be one of the image names returned by your shader's getAvailableImages() method.
        
        The implementation must return the dimensions of the image in the 'imageWidth' and 'imageHeight' parameters so that Maya can perform pixel snapping and other resolution-dependent operations.
        
        The implementation can assume OpenGL context, model view projection matrix, and texture transformations have already been set. A default color of white will be set, however you are free to change this. The magnification filter will be set to either point or bilinear based on user configuration and should not be modified. The values of GL_TEXTURE_WRAP_S and GL_TEXTURE_WRAP_T are undefined on entry, and your implementation is responsible for setting them to appropriate values (e.g. GL_REPEAT).
        
        The arguments contain the name of the image to render, and the vertex and texture coordinate values to use at each corner of the rectangular image being rendered. Your implementation is responsible for restoring the original the value of any OpenGL state that is modified.
        
        * context (ShaderContext) - Context of the draw request (e.g. the surface being shaded, shading engine making the request)
        * imageName (string) - Name of the image to render. This corresponds to one of the image names returned by your shader's getAvailableImages() method.
        * region (float[2][2]) - Rectangular region to be rendered. The values of this parameter should be used to populate the vertex and texture coordinates of the rectangle being rendered.
        * parameters (RenderParamters) - Additional parameters on how to render the image. The values reflect the image settings of the UV editor.
        
        A second version with the uiDrawManager parameter allows you to to render the background image used for this shader in the UV texture editor in viewport 2.0.
        
        * uiDrawManager (MUIDrawManager) - The UI draw manager, it can be used to draw some simple geometry
        
        Returns None if method is not implemented : No rendering will occur.
        """
    
        pass
    
    
    def renderSwatchImage(*args, **kwargs):
        """
        renderSwatchImage(image) -> self
        
        If the shader specifies to override swatch rendering, then this method must be overridden in order to draw anything into a swatch.
        
        The shader will only draw a swatch if it has been registered to do so, by providing a valid classification during MFnPlugin::registerNode(). The shader should provide a classification that defines a swatch rendering node such as : "shader/surface/utility/:drawdb/shader/surface/myCustomShader:swatch/myCustomShaderSwatchGenerator" and have "myCustomShaderSwatchGenerator" registered has a swatch renderer : MSwatchRenderRegister.registerSwatchRender("myCustomShaderSwatchGenerator", MHWShaderSwatchGenerator.createObj );
        
        The default implementation is to draw nothing. The basic logic to draw a swatch is as follows:
        
          Determine the size of the swatch required. This is the dimensions of the MImage passed in as an argument. The pixels for the MImage will have been pre-allocated. The format of the pixels is 32-bit R,G,B,A, with 8-bits per channel.
          Either use an offscreen "swatch context" provided to you or use your own offscreen context. The provided context is available via the MHardwareRenderer class method makeSwatchContextCurrent(). Note that the swatch context may be smaller than the desired image size. In this case the rendering dimensions will be clamped.
          Either use swatch geometry provided to you, or use your own swatch geometry. The provided geometry is available via the method MHardwareRenderer::referenceDefaultGeometry(). The possible "default" geometries are either a sphere, cube or plane.
          Either use the provided "default" light and "default" camera or set up your own. Use the methods (getSwatchOrthoCameraSetting(), getSwatchLightDirection()) on MHardwareRenderer to get these defaults.
          Read back the swatch context into the provided MImage. The convenience method MHardwareRenderer::readSwatchContextPixels() can be used. By default the format of the MImage and the swatch context are the same, so the user does not need to worry about this. The context will read into the pre-allocated MImage pixels.
          Unreference any swatch geometry used for rendering using MHardwareRenderer::dereferenceGeometry().
        
        * image [IN/OUT] (MImage) - Image object to which this method must write the rendered swatch. On input the image's dimensions are already set and pixel storage already allocated.
        
        Returns None if method is not implemented : No rendering will occur.
        """
    
        pass
    
    
    def setUniformParameters(*args, **kwargs):
        """
        setUniformParameters(parameters, remapCurrentValues=True, dagModifier=None) -> self
        
        Call this method to set the list of uniform parameters this shader uses. Once set, you can use these parameters to access the cached values of shader parameters, including testing when the value has been updated (to minimise the shader state changes). When using this method to manage uniform parameters, Maya will handle the underlyintg attributes, serialization and user interface for you.It is important to call this method whenever the shader parameters are modified (including at load time).This is an optional method - shader implementations are still free to manage uniform (i.e. shader-level) parameters independently if they wish.* parameters (MUniformParameterList) - the list of uniform parameters for this shader
        * remapCurrentValues (bool) - if True (the default), Maya will attempt to initialise the value of new parameters based on any equivalently named parameters that currently exist on the node. Otherwise, the parameters will be setup using default values. Unless you wish to forcibly reset parameter values, the default value of True should be used.
        * dagModifier (MDagModifier) - an optional DG modifier to use when managing the attributes used to represent the geometry parameters on this shader.
        """
    
        pass
    
    
    def setVaryingParameters(*args, **kwargs):
        """
        setVaryingParameters(parameters, remapCurrentValues=True, dagModifier=None) -> self
        
        Call this method to set the list of varying parameters this shader uses. Once set, you can use these parameters directly to access geometry data for surfaces being shaded. When using this method to manage shader varying parameters, there is no need to override populateRequirements or handle the node interface as Maya will handle parameter setup, presentation and configuration for you.
        
        It is important to call this method whenever the shader parameters are modified (including at load time).
        
        This is an optional method - shader implementations are still free to manage geometry parameters independently if they wish.
        
        * parameters (MUniformParameterList) - the list of varying parameters for this shader
        * remapCurrentValues (bool) - if True (the default), Maya will attempt to initialise the value of new parameters based on any equivalently named parameters that currently exist on the node. Otherwise, the parameters will be setup using default values. Unless you wish to forcibly reset parameter values, the default value of True should be used.
        * dagModifier (MDagModifier) - an optional DG modifier to use when managing the attributes used to represent the geometry parameters on this shader.
        """
    
        pass
    
    
    def transparencyOptions(*args, **kwargs):
        """
        transparencyOptions() -> int
        
        This method returns transparency options for usage as hints for Maya's internal draw during a given rendering pass. Parameters are returned via an integer containing masked out bits. By default the mask is set to 0, meaning that the drawing should be treated as regular opaque object drawing. This will generally mean one call per draw pass.
        
        Options to control transparency are specified by returning one or more masks specified by the following values :
          - kIsTransparent : Draw as a transparent object. If no transparency overrides are specified, then control of how to draw during a given pass is determined internally by Maya's refresh algorithm, and options the user can set per modelling viewport.
          - kNoTransparencyFrontBackCull : When kisTransparent is set and this flag is set, do not perform transparency drawing using the internal 2-pass front-face + back-face culling algorithm.
          - kNoTransparencyPolygonSort : When kisTransparent is set and this flag is set, do not perform transparency drawing using the internal 2-pass drawing of back-to-front sorted triangles.
        """
    
        pass
    
    
    def findResource(*args, **kwargs):
        """
        findResource(name, shaderPath) -> string
        
        This is a static utility to find the full path to a shader resource (typically a texture). This method will search the list of paths in the MAYA_HW_SHADER_RESOURCE_PATH environment variable, resolving relative paths based on the directory containing the shader.
        
        * name (string) - The name of the resource to look for (e.g. 'normals.dds')
        * shaderPath (string) - The full path to the current shader (e.g. 'C:/shaders/myshader.fx')
        
        
        Return the full path of the resource (e.g. 'C:/shaders/textures/normals.dds').
        """
    
        pass
    
    
    def getHardwareShader(*args, **kwargs):
        """
        getHardwareShader(object) -> TODO
        
        This is a static convenience method to be able to get an MPxHardwareShader from an MObject provided by a swatch generator class (Class derived from MSwatchRenderRegister).
        
        * object (MObject) - The object to examine.
        
        Return a MPxHardwareShader. If the method failed for any reason then None will be returned.
        """
    
        pass
    
    
    __new__ = None
    
    
    kIsTransparent = 1
    
    
    kNoTransparencyFrontBackCull = 2
    
    
    kNoTransparencyPolygonSort = 4
    
    
    outColor = None
    
    
    outColorB = None
    
    
    outColorG = None
    
    
    outColorR = None


class _MFnDagNode(_MFnDependencyNode):
    """
    Function set for operating on DAG nodes.
    
    __init__()
    Initializes a new, empty MFnDagNode functionset.
    
    __init__(MObject)
    Initializes a new MFnDagNode functionset and attaches it to a
    DAG node.
    
    __init__(MDagPath)
    Initializes a new MFnDagNode functionset and attaches it to a
    DAG path.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addChild(*args, **kwargs):
        """
        addChild(node, index=kNextPos, keepExistingParents=False) -> self
        
        Makes a node a child of this one.
        """
    
        pass
    
    
    def child(*args, **kwargs):
        """
        child(index) -> MObject
        
        Returns the specified child of this node.
        """
    
        pass
    
    
    def childCount(*args, **kwargs):
        """
        childCount() -> int
        
        Returns the number of nodes which are children of this one.
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(type, name=None, parent=MObject.kNullObj) -> MObject
        
        Creates a new DAG node of the specified type, with the given name.
        The type may be either a type name or a type ID. If no name is given
        then a unique name will be generated by combining the type name with
        an integer.
        
        If a parent is given then the new node will be parented under it and
        the functionset will be attached to the newly-created node. The
        newly-created node will be returned.
        
        If no parent is given and the new node is a transform, it will be
        parented under the world and the functionset will be attached to the
        newly-created transform. The newly-created transform will be returned.
        
        If no parent is given and the new node is not a transform then a
        transform node will be created under the world, the new node will be
        parented under it, and the functionset will be attached to the
        transform. The transform will be returned.
        """
    
        pass
    
    
    def dagPath(*args, **kwargs):
        """
        dagPath() -> MDagPath
        
        Returns the DAG path to which this function set is attached. Raises a TypeError if the function set is attached to an MObject rather than a path.
        """
    
        pass
    
    
    def dagRoot(*args, **kwargs):
        """
        dagRoot() -> MObject
        
        Returns the root node of the first path leading to this node.
        """
    
        pass
    
    
    def duplicate(*args, **kwargs):
        """
        duplicate(instance=False, instanceLeaf=False) -> MObject
        
        Duplicates the DAG hierarchy rooted at the current node.
        """
    
        pass
    
    
    def fullPathName(*args, **kwargs):
        """
        fullPathName() -> string
        
        Returns the full path of the attached object, from the root of the DAG on down.
        """
    
        pass
    
    
    def getAllPaths(*args, **kwargs):
        """
        getAllPaths() -> MDagPathArray
        
        Returns all of the DAG paths which lead to the object to which this function set is attached.
        """
    
        pass
    
    
    def getConnectedSetsAndMembers(*args, **kwargs):
        """
        getConnectedSetsAndMembers(instance, renderableSetsOnly) -> (MObjectArray, MObjectArray)
        
        Returns a tuple containing an array of sets and an array of the
        components of the DAG object which are in those sets. If the entire object is in a set, then the corresponding entry in the comps array will have no elements in it.
        """
    
        pass
    
    
    def getPath(*args, **kwargs):
        """
        getPath() -> MDagPath
        
        Returns the DAG path to which this function set is attached, or the first path to the node if the function set is attached to an MObject.
        """
    
        pass
    
    
    def hasChild(*args, **kwargs):
        """
        hasChild(node) -> bool
        
        Returns True if the specified node is a child of this one.
        """
    
        pass
    
    
    def hasParent(*args, **kwargs):
        """
        hasParent(node) -> bool
        
        Returns True if the specified node is a parent of this one.
        """
    
        pass
    
    
    def instanceCount(*args, **kwargs):
        """
        instanceCount(indirect) -> int
        
        Returns the number of instances for this node.
        """
    
        pass
    
    
    def isChildOf(*args, **kwargs):
        """
        isChildOf(node) -> bool
        
        Returns True if the specified node is a parent of this one.
        """
    
        pass
    
    
    def isInstanced(*args, **kwargs):
        """
        isInstanced(indirect=True) -> bool
        
        Returns True if this node is instanced.
        """
    
        pass
    
    
    def isInstancedAttribute(*args, **kwargs):
        """
        isInstancedAttribute(attr) -> bool
        
        Returns True if the specified attribute is an instanced attribute of this node.
        """
    
        pass
    
    
    def isParentOf(*args, **kwargs):
        """
        isParentOf(node) -> bool
        
        Returns True if the specified node is a child of this one.
        """
    
        pass
    
    
    def parent(*args, **kwargs):
        """
        parent(index) -> MObject
        
        Returns the specified parent of this node.
        """
    
        pass
    
    
    def parentCount(*args, **kwargs):
        """
        parentCount() -> int
        
        Returns the number of parents this node has.
        """
    
        pass
    
    
    def partialPathName(*args, **kwargs):
        """
        partialPathName() -> string
        
        Returns the minimum path string necessary to uniquely identify the attached object.
        """
    
        pass
    
    
    def removeChild(*args, **kwargs):
        """
        removeChild(node) -> self
        
        Removes the child, specified by MObject, reparenting it under the world.
        """
    
        pass
    
    
    def removeChildAt(*args, **kwargs):
        """
        removeChildAt(index) -> self
        
        Removes the child, specified by index, reparenting it under the world.
        """
    
        pass
    
    
    def setObject(*args, **kwargs):
        """
        setObject(MObject or MDagPath) -> self
        
        Attaches the function set to the specified node or DAG path.
        """
    
        pass
    
    
    def transformationMatrix(*args, **kwargs):
        """
        transformationMatrix() -> MMatrix
        
        Returns the object space transformation matrix for this DAG node.
        """
    
        pass
    
    
    boundingBox = None
    
    inModel = None
    
    inUnderWorld = None
    
    isInstanceable = None
    
    isIntermediateObject = None
    
    objectColor = None
    
    objectColorRGB = None
    
    objectColorType = None
    
    useObjectColor = None
    
    __new__ = None
    
    
    kNextPos = 255


class _MFnTransform(_MFnDagNode):
    """
    Function set for operating on transform nodes.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def clearRestPosition(*args, **kwargs):
        """
        Clears the transform's rest position matrix.
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        Creates a new transform node and attaches it to the function set.
        """
    
        pass
    
    
    def enableLimit(*args, **kwargs):
        """
        Enables or disables a specified limit type.
        """
    
        pass
    
    
    def isLimited(*args, **kwargs):
        """
        Returns True if the specified limit type is enabled.
        """
    
        pass
    
    
    def limitValue(*args, **kwargs):
        """
        Returns the value of the specified limit.
        """
    
        pass
    
    
    def resetFromRestPosition(*args, **kwargs):
        """
        Resets the transform from its rest position matrix.
        """
    
        pass
    
    
    def restPosition(*args, **kwargs):
        """
        Returns the transform's rest position matrix.
        """
    
        pass
    
    
    def rotateBy(*args, **kwargs):
        """
        Adds an MEulerRotation or MQuaternion to the transform's rotation.
        """
    
        pass
    
    
    def rotateByComponents(*args, **kwargs):
        """
        Adds to the transform's rotation using the individual components of an MEulerRotation or MQuaternion.
        """
    
        pass
    
    
    def rotateOrientation(*args, **kwargs):
        """
        Returns the MQuaternion which orients the local rotation space.
        """
    
        pass
    
    
    def rotatePivot(*args, **kwargs):
        """
        Returns the transform's rotate pivot.
        """
    
        pass
    
    
    def rotatePivotTranslation(*args, **kwargs):
        """
        Returns the transform's rotate pivot translation.
        """
    
        pass
    
    
    def rotation(*args, **kwargs):
        """
        Returns the transform's rotation as an MEulerRotation or MQuaternion.
        """
    
        pass
    
    
    def rotationComponents(*args, **kwargs):
        """
        Returns the transform's rotation as the individual components of an MEulerRotation or MQuaternion.
        """
    
        pass
    
    
    def rotationOrder(*args, **kwargs):
        """
        Returns the order of rotations when the transform's rotation is expressed as an MEulerRotation.
        """
    
        pass
    
    
    def scale(*args, **kwargs):
        """
        Returns a list containing the transform's XYZ scale components.
        """
    
        pass
    
    
    def scaleBy(*args, **kwargs):
        """
        Multiplies the transform's XYZ scale components by a sequence of three floats.
        """
    
        pass
    
    
    def scalePivot(*args, **kwargs):
        """
        Returns the transform's scale pivot.
        """
    
        pass
    
    
    def scalePivotTranslation(*args, **kwargs):
        """
        Returns the transform's scale pivot translation.
        """
    
        pass
    
    
    def setLimit(*args, **kwargs):
        """
        Sets the value of the specified limit.
        """
    
        pass
    
    
    def setRestPosition(*args, **kwargs):
        """
        Sets the transform's rest position matrix.
        """
    
        pass
    
    
    def setRotateOrientation(*args, **kwargs):
        """
        Sets the MQuaternion which orients the local rotation space.
        """
    
        pass
    
    
    def setRotatePivot(*args, **kwargs):
        """
        Sets the transform's rotate pivot.
        """
    
        pass
    
    
    def setRotatePivotTranslation(*args, **kwargs):
        """
        Sets the transform's rotate pivot translation.
        """
    
        pass
    
    
    def setRotation(*args, **kwargs):
        """
        Sets the transform's rotation using an MEulerRotation or MQuaternion.
        """
    
        pass
    
    
    def setRotationComponents(*args, **kwargs):
        """
        Sets the transform's rotation using the individual components of an MEulerRotation or MQuaternion.
        """
    
        pass
    
    
    def setRotationOrder(*args, **kwargs):
        """
        Sets the transform's rotation order.
        """
    
        pass
    
    
    def setScale(*args, **kwargs):
        """
        Sets the transform's scale components.
        """
    
        pass
    
    
    def setScalePivot(*args, **kwargs):
        """
        Sets the transform's scale pivot.
        """
    
        pass
    
    
    def setScalePivotTranslation(*args, **kwargs):
        """
        Sets the transform's scale pivot translation.
        """
    
        pass
    
    
    def setShear(*args, **kwargs):
        """
        Sets the transform's shear.
        """
    
        pass
    
    
    def setTransformation(*args, **kwargs):
        """
        Sets the transform's attribute values to represent the given transformation matrix.
        """
    
        pass
    
    
    def setTranslation(*args, **kwargs):
        """
        Sets the transform's translation.
        """
    
        pass
    
    
    def shear(*args, **kwargs):
        """
        Returns a list containing the transform's shear components.
        """
    
        pass
    
    
    def shearBy(*args, **kwargs):
        """
        Multiplies the transform's shear components by a sequence of three floats.
        """
    
        pass
    
    
    def transformation(*args, **kwargs):
        """
        Returns the transformation matrix represented by this transform.
        """
    
        pass
    
    
    def translateBy(*args, **kwargs):
        """
        Adds an MVector to the transform's translation.
        """
    
        pass
    
    
    def translation(*args, **kwargs):
        """
        Returns the transform's translation as an MVector.
        """
    
        pass
    
    
    __new__ = None
    
    
    kRotateMaxX = 13
    
    
    kRotateMaxY = 15
    
    
    kRotateMaxZ = 17
    
    
    kRotateMinX = 12
    
    
    kRotateMinY = 14
    
    
    kRotateMinZ = 16
    
    
    kScaleMaxX = 1
    
    
    kScaleMaxY = 3
    
    
    kScaleMaxZ = 5
    
    
    kScaleMinX = 0
    
    
    kScaleMinY = 2
    
    
    kScaleMinZ = 4
    
    
    kShearMaxXY = 7
    
    
    kShearMaxXZ = 9
    
    
    kShearMaxYZ = 11
    
    
    kShearMinXY = 6
    
    
    kShearMinXZ = 8
    
    
    kShearMinYZ = 10
    
    
    kTranslateMaxX = 19
    
    
    kTranslateMaxY = 21
    
    
    kTranslateMaxZ = 23
    
    
    kTranslateMinX = 18
    
    
    kTranslateMinY = 20
    
    
    kTranslateMinZ = 22


class MFnManip3D(_MFnTransform):
    """
    MFnManip3D allows the creation and manipulation of 3D manipulators.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def rotateXYZValue(*args, **kwargs):
        """
        rotateXYZValue(valIndex) -> MEulerRotation
        
        Gets the rotation for the active manipulator.
        
        * valIndex (int) - rotation index of the manipulator
        """
    
        pass
    
    
    def deleteManipulator(*args, **kwargs):
        """
        deleteManipulator(manip) -> None
        
        Delete a manipulator.  This method should be used to delete manipulators that have been created using base manipulator create() methods.
        
        * manip (MObject) - the manipulator to be deleted
        """
    
        pass
    
    
    def drawPlaneHandles(*args, **kwargs):
        """
        drawPlaneHandles() -> bool
        
        This method returns the global option that says if the planar manipulator handles should be drawn or not.Setting this will affect the drawing of all manipulators that support the planar handles.
        """
    
        pass
    
    
    def globalSize(*args, **kwargs):
        """
        globalSize() -> float
        
        Returns the global manipulator size.
        """
    
        pass
    
    
    def handleSize(*args, **kwargs):
        """
        handleSize() -> float
        
        Returns the manipulator handle size.
        """
    
        pass
    
    
    def lineSize(*args, **kwargs):
        """
        lineSize() -> float
        
        Returns the manipulator line size.
        """
    
        pass
    
    
    def setDrawPlaneHandles(*args, **kwargs):
        """
        setDrawPlaneHandles(bool) -> None
        
        Sets the global option to display planar handles or not on supported manipulators.
        """
    
        pass
    
    
    def setGlobalSize(*args, **kwargs):
        """
        setGlobalSize(float) -> None
        
        Sets the global manipulator size.
        """
    
        pass
    
    
    def setHandleSize(*args, **kwargs):
        """
        setHandleSize(float) -> None
        
        Sets the manipulator handle size.
        """
    
        pass
    
    
    def setLineSize(*args, **kwargs):
        """
        setLineSize(float) -> None
        
        Sets the manipulator line size.
        """
    
        pass
    
    
    isOptimizePlaybackOn = None
    
    isVisible = None
    
    manipScale = None
    
    __new__ = None


class MFnDirectionManip(MFnManip3D):
    """
    The DirectionManip allows the user to specify a direction, as defined by the vector from the start point to the manipulator position.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectToDirectionPlug(*args, **kwargs):
        """
        connectToDirectionPlug(directionPlug) -> self
        
        Connect to the direction plug. The data type corresponding to the directionPlug is MFnNumericData.k3Double.
        
        * directionPlug (MPlug) - the direction plug
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, directionName=None) -> MObject
        
        Creates a new DirectionManip.
        This function set's object is set to be the new manipulator.
        
        This method should only be used to create a non-composite DirectionManip.
        
        The name that appears in the feedback line is specified by the directionName argument.
        
        * manipName (string) - Name of the manip for UI purposes.
        * directionName (string) - Label for the direction value which appears in the feedback line.
        """
    
        pass
    
    
    def directionIndex(*args, **kwargs):
        """
        directionIndex() -> int
        
        Returns the index of the direction. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def endPointIndex(*args, **kwargs):
        """
        endPointIndex() -> int
        
        Returns the index of the end point of the DirectionManip. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def setDirection(*args, **kwargs):
        """
        setDirection(direction) -> self
        
        Sets the direction of the DirectionManip.
        
        * direction (MVector) - the direction of the DirectionManip
        """
    
        pass
    
    
    def setDrawStart(*args, **kwargs):
        """
        setDrawStart(bool) -> self
        
        Sets whether or not to draw the start of the DirectionManip.
        The start of the DirectionManip is indicated by a grey dot.
        By default the start is not drawn.
        """
    
        pass
    
    
    def setNormalizeDirection(*args, **kwargs):
        """
        setNormalizeDirection(bool) -> self
        
        Sets whether or not to the direction should be normalized.
        By default the direction is normalized.
        """
    
        pass
    
    
    def setStartPoint(*args, **kwargs):
        """
        setStartPoint(startPoint) -> self
        
        Sets the start point of the DirectionManip.
        
        * startPoint (MPoint) - the start point of the DirectionManip
        """
    
        pass
    
    
    def startPointIndex(*args, **kwargs):
        """
        startPointIndex() -> int
        
        Returns the index of the start point of the DirectionManip. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    __new__ = None


class MFnStateManip(MFnManip3D):
    """
    The StateManip allows the user to switch between multiple states. It is drawn as a circle with a notch. Each click on the circle increments the value of the state (modulo the maximum number of states). This manipulator generates an integer value corresponding to the state of the manip.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectToStatePlug(*args, **kwargs):
        """
        connectToStatePlug(statePlug) -> self
        
        Connect to the state plug. The data type corresponding to the statePlug is a int integer.
        
        * statePlug (MPlug) - the state plug
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, stateName=None) -> MObject
        
        Creates a new StateManip.
        This function set's object is set to be the new manipulator.
        
        This method should only be used to create a non-composite StateManip.
        
        The name that appears in the feedback line is specified by the stateName argument.
        
        * manipName (string) - Name of the manip for UI purposes.
        * stateName (string) - Label for the state value which appears in the feedback line.
        """
    
        pass
    
    
    def positionIndex(*args, **kwargs):
        """
        positionIndex() -> int
        
        Returns the index of the position of the StateManip. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def setInitialState(*args, **kwargs):
        """
        setInitialState(initialState) -> self
        
        Sets the initial state of the StateManip.
        
        * initialState (int) - initial state of the StateManip
        """
    
        pass
    
    
    def state(*args, **kwargs):
        """
        state() -> int
        
        Returns the current state.
        """
    
        pass
    
    
    def stateIndex(*args, **kwargs):
        """
        stateIndex() -> int
        
        Returns the index of the state. The data type corresponding to this index is a int integer.
        """
    
        pass
    
    
    maxStates = None
    
    __new__ = None


class MFnFreePointTriadManip(MFnManip3D):
    """
    The FreePointTriadManip provides a moveable point, which can be moved anywhere, and has axes for constrained x, y, and z movement and obeys grid snapping, point snapping, and curve snapping. The FreePointTriadManip generates the 3D position of the moveable point. It is useful for specifying the position of an object in space.
    
    Note that only the MFnNumericData::k3Double data type is supportedwhen connecting to a pointPlug via connectToPointPlug.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectToPointPlug(*args, **kwargs):
        """
        connectToPointPlug(pointPlug) -> self
        
        Connect to the point plug. The data type corresponding to the pointPlug is MFnNumericData.k3Double.
        
        * pointPlug (MPlug) - the point plug
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, pointName=None) -> MObject
        
        Creates a new FreePointTriadManip.
        This function set's object is set to be the new manipulator.
        
        This method should only be used to create a non-composite FreePointTriadManip.
        
        The name that appears in the feedback line is specified by the pointName argument.
        
        * manipName (string) - Name of the manip for UI purposes.
        * pointName (string) - Label for the position value which appears in the feedback line.
        """
    
        pass
    
    
    def pointIndex(*args, **kwargs):
        """
        pointIndex() -> int
        
        Returns the index of the point of the FreePointTriadManip. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def setDirection(*args, **kwargs):
        """
        setDirection(direction) -> self
        
        Sets the orientation of the FreePointTriadManip.
        
        * direction (MVector) - the new direction for freePointTriadManip.
        """
    
        pass
    
    
    def setDrawArrowHead(*args, **kwargs):
        """
        setDrawArrowHead(state) -> self
        
        Sets whether or not drawArrowHead is on.
        
        * state (bool) - whether or not drawArrowHead is on
        """
    
        pass
    
    
    def setGlobalTriadPlane(*args, **kwargs):
        """
        setGlobalTriadPlane(whichPlane) -> self
        
        Sets which plane to use as the global triad plane. The global triad plane does not change until the context switches.
        
        * whichPlane (int) - which plane to use as the global triad plane
        
        Valid plane values:
          kYZPlane       Y-Z Plane
          kXZPlane       X-Z Plane
          kXYPlane       X-Y Plane
          kViewPlane     View Plane
        """
    
        pass
    
    
    def setPoint(*args, **kwargs):
        """
        setPoint(pointValue) -> self
        
        Set the point manipulator value to the given vector.  This method can be called in the MPxManipContainer.connectToDependNode() method to set the initial position for the manipulator.
        
        * pointValue (MPoint) - The new value of the point manipValue
        """
    
        pass
    
    
    isDrawAxesOn = None
    
    isKeyframeAllOn = None
    
    isSnapModeOn = None
    
    __new__ = None
    
    
    kViewPlane = 3
    
    
    kXYPlane = 2
    
    
    kXZPlane = 1
    
    
    kYZPlane = 0


class MFnCircleSweepManip(MFnManip3D):
    """
    The CircleSweepManip allows the user to manipulate a point constrained to move around a circle, in order to specify a sweep angle. This manipulator generates a single floating point value corresponding to the sweep angle.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def angleIndex(*args, **kwargs):
        """
        angleIndex() -> int
        
        Returns the index for the angle of CircleSweepManip. The data type corresponding to this index is a double.
        """
    
        pass
    
    
    def axisIndex(*args, **kwargs):
        """
        axisIndex() -> int
        
        Returns the index for the axis of CircleSweepManip. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def centerIndex(*args, **kwargs):
        """
        centerIndex() -> int
        
        Returns the index for the center of the CircleSweepManip. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def connectToAnglePlug(*args, **kwargs):
        """
        connectToAnglePlug(anglePlug) -> self
        
        Connect to the angle plug. The data type corresponding to the anglePlug is a double. (Note that MFnUnitAttribute.kAngle is used to specify an angle attribute.)
        
        * anglePlug (MPlug) - the angle plug
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, angleName=None) -> MObject
        
        Creates a new CircleSweepManip.
        This function set's object is set to be the new manipulator.
        
        This method should only be used to create a non-composite CircleSweepManip.
        
        The name that appears in the feedback line is specified by the angleName argument.
        
        * manipName (string) - Name of the manip for UI purposes.
        * angleName (string) - Label for the angle value which appears in the feedback line.
        """
    
        pass
    
    
    def endCircleIndex(*args, **kwargs):
        """
        endCircleIndex() -> int
        
        Returns the index for the end of the circle of CircleSweepManip. The data type corresponding to this index is a double.
        """
    
        pass
    
    
    def setAngle(*args, **kwargs):
        """
        setAngle(angle) -> self
        
        Sets the angle of the CircleSweepManip.
        
        * angle (MAngle) - the angle of the CircleSweepManip
        """
    
        pass
    
    
    def setCenterPoint(*args, **kwargs):
        """
        setCenterPoint(centerPoint) -> self
        
        Sets the center point of the CircleSweepManip.
        
        * centerPoint (MPoint) - the center point of the CircleSweepManip
        """
    
        pass
    
    
    def setDrawAsArc(*args, **kwargs):
        """
        setDrawAsArc(state) -> self
        
        Sets whether or not to draw as arc.
        
        * state (bool) - whether or not to draw as arc
        """
    
        pass
    
    
    def setNormal(*args, **kwargs):
        """
        setNormal(normal) -> self
        
        Sets the normal of the CircleSweepManip.
        
        * normal (MVector) - the normal of the CircleSweepManip
        """
    
        pass
    
    
    def setRadius(*args, **kwargs):
        """
        setRadius(radius) -> self
        
        Sets the radius of the CircleSweepManip.
        
        * radius (float) - the radius of the CircleSweepManip
        """
    
        pass
    
    
    def startCircleIndex(*args, **kwargs):
        """
        startCircleIndex() -> int
        
        Returns the index for the start of the circle of CircleSweepManip. The data type corresponding to this index is a double.
        """
    
        pass
    
    
    endPoint = None
    
    startPoint = None
    
    __new__ = None


class MFnRotateManip(MFnManip3D):
    """
    This class provides access to the built-in Maya rotate manipulator.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectToRotationCenterPlug(*args, **kwargs):
        """
        connectToRotationCenterPlug(rotationCenterPlug) -> self
        
        Create a 1-1 association of the rotation center on the manipulator and the rotationCenterPlug parameter.  When both the rotation center is attached to a plug and the displayWithNode() method has been called, the manipulator will display with the node regardless of the connection made to the rotation center.
        
        The plug must have a data type of MFnNumericData.k3Double.
        
        * rotationCenterPlug (MPlug) - The plug to connect the rotation center to
        """
    
        pass
    
    
    def connectToRotationPlug(*args, **kwargs):
        """
        connectToRotationPlug(rotationPlug) -> self
        
        Create a 1-1 connection from the rotation manipVal to the rotationPlug parameter.  Any changes to the rotation manipVal will be immediately reflected in the connected plug.  Connecting to the "rotation" plug on a transform node will produce similar behavior to the built-in rotation manipulator.
        
        The plug must have a data type of MFnNumericData.k3Double.
        
        * rotationPlug (MPlug) - The plug to connect the rotation value to
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, rotationName=None) -> MObject
        
        Creates a new RotateManip, and attaches this function set to the new manipulator.
        
        This method should only be used to create a non-composite manipulator, meaning that the manipulator is standalone and not part of a container.
        
        When the manipulator is being used, the feedback line will display a string including rotationName, indicating that this manipulator is in use.
        
        * manipName (string) - Name of the manip for UI purposes.
        * rotationName (string) - Label for the rotation value displayed in the feedback line.
        """
    
        pass
    
    
    def displayWithNode(*args, **kwargs):
        """
        displayWithNode(node) -> self
        
        Configures the manipulator to display with the node, causing the position of the manipulator to follow the position of the node whenever the node is moved.  The node must be a DAG object.
        
        * node (MObject) - The node the manipulator should display with
        """
    
        pass
    
    
    def rotationCenterIndex(*args, **kwargs):
        """
        rotationCenterIndex() -> int
        
        Returns the index of the rotation center for this manipulator.
        
        Note that the rotation center is only used for positioning the display of the manipulator, and has no effect on the rotation values generated by the manipulator.
        """
    
        pass
    
    
    def rotationIndex(*args, **kwargs):
        """
        rotationIndex() -> int
        
        Returns the index of the rotation manipVal for the manipulator.  When plugToManip conversion functions are used to produce the rotation manipVal, the manipulator data must be of the type MFnNumericData.k3Double, with X,Y, and Z rotations given in radians.  This is easily accomplished by using the MEulerRotation class to manage the rotations.
        """
    
        pass
    
    
    def setInitialRotation(*args, **kwargs):
        """
        setInitialRotation(rotation) -> self
        
        Sets the initial rotation for the rotate manipulator.  Setting the initial rotation will prevent the manipulator from jumping back to the default rotation when there is already an existing rotation on the target plug.
        
        * rotation (MEulerRotation) - The initial rotation
        """
    
        pass
    
    
    def setRotationCenter(*args, **kwargs):
        """
        setRotationCenter(rotationCenter) -> self
        
        Sets the position of the rotation center for the manipulator.
        
        The value set by this method is ignored if a plug has been connected to the rotationCenterPlug. This value is only relevant when there is no plug connection to rotationCenterPlug nor node associated with the manip (see connectToRotationCenterPlug and displayWithNode, respectively).
        
        Note that the rotation center is only used for positioning the display of the manipulator, and has no effect on the rotation values generated by the manipulator.
        
        * rotationCenter (MPoint) - The world space position of the rotation center.
        """
    
        pass
    
    
    isSnapModeOn = None
    
    rotateMode = None
    
    snapIncrement = None
    
    __new__ = None
    
    
    kGimbal = 2
    
    
    kObjectSpace = 0
    
    
    kWorldSpace = 1


class MFnDiscManip(MFnManip3D):
    """
    The DiscManip allows the user to rotate a disc in order to specify a rotation about an axis. This manipulator generates a single floating point value corresponding to the rotation.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def angleIndex(*args, **kwargs):
        """
        angleIndex() -> int
        
        Returns the index of the angle. The data type corresponding to this index is a double.
        """
    
        pass
    
    
    def axisIndex(*args, **kwargs):
        """
        axisIndex() -> int
        
        Returns the index of the axis of the DiscManip. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def centerIndex(*args, **kwargs):
        """
        centerIndex() -> int
        
        Returns the index of the center of the DiscManip. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def connectToAnglePlug(*args, **kwargs):
        """
        connectToAnglePlug(directionPlug) -> self
        
        Connect to the angle plug. The data type corresponding to the anglePlug is a double. (Note that MFnUnitAttribute.kAngle is used to specify an angle attribute.)
        
        * anglePlug (MPlug) - the angle plug
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, angleName=None) -> MObject
        
        Creates a new DiscManip.
        This function set's object is set to be the new manipulator.
        
        This method should only be used to create a non-composite DiscManip.
        
        The name that appears in the feedback line is specified by the angleName argument.
        
        * manipName (string) - Name of the manip for UI purposes.
        * angleName (string) - Label for the angle value which appears in the feedback line.
        """
    
        pass
    
    
    def setAngle(*args, **kwargs):
        """
        setAngle(angle) -> self
        
        Sets the angle of the DiscManip.
        
        * angle (MAngle) - the angle of the DiscManip
        """
    
        pass
    
    
    def setCenterPoint(*args, **kwargs):
        """
        setCenterPoint(centerPoint) -> self
        
        Sets the center point of the DiscManip.
        
        * centerPoint (MPoint) - the center point of the DiscManip
        """
    
        pass
    
    
    def setNormal(*args, **kwargs):
        """
        setNormal(normal) -> self
        
        Sets the normal of the DiscManip.
        
        * normal (MVector) - the normal of the DiscManip
        """
    
        pass
    
    
    def setRadius(*args, **kwargs):
        """
        setRadius(radius) -> self
        
        Sets the radius of the DiscManip.
        
        * radius (float) - the radius of the DiscManip
        """
    
        pass
    
    
    __new__ = None


class MFnToggleManip(MFnManip3D):
    """
    The ToggleManip allows the user to switch between two modes or some on/off state. It is drawn as a circle with or without a dot. When the mode is on, the dot is drawn in the circle; when the mode is off, the circle is drawn without the dot. This manipulator generates a boolean value corresponding to whether or not the mode is on or off.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectToTogglePlug(*args, **kwargs):
        """
        connectToTogglePlug(togglePlug) -> self
        
        Connect to the toggle plug. The data type corresponding to the togglePlug is a boolean value.
        
        * togglePlug (MPlug) - the toggle plug
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, toggleName=None) -> MObject
        
        Creates a new ToggleManip.
        This function set's object is set to be the new manipulator.
        
        This method should only be used to create a non-composite ToggleManip.
        
        The name that appears in the feedback line is specified by the toggleName argument.
        
        * manipName (string) - Name of the manip for UI purposes.
        * toggleName (string) - Label for the toggle value which appears in the feedback line.
        """
    
        pass
    
    
    def directionIndex(*args, **kwargs):
        """
        directionIndex() -> int
        
        Returns the index of the direction. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def lengthIndex(*args, **kwargs):
        """
        lengthIndex() -> int
        
        Returns the index of the length of the ToggleManip. The data type corresponding to this index is a double.
        """
    
        pass
    
    
    def startPointIndex(*args, **kwargs):
        """
        startPointIndex() -> int
        
        Returns the index of the start point of the ToggleManip. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def toggleIndex(*args, **kwargs):
        """
        toggleIndex() -> int
        
        Returns the index of the toggle of the ToggleManip. The data type corresponding to this index is a boolean.
        """
    
        pass
    
    
    direction = None
    
    length = None
    
    startPoint = None
    
    toggle = None
    
    __new__ = None


class MFnPointOnCurveManip(MFnManip3D):
    """
    The PointOnCurveManip allows the user to manipulate a point constrained to move along a curve, in order to specify the "u" curve parameter value. This manipulator generates a single floating point value corresponding to the curve parameter.the sweep angle.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectToCurvePlug(*args, **kwargs):
        """
        connectToCurvePlug(curvePlug) -> self
        
        Connect to the curve plug. The data type corresponding to the curvePlug is MFnData::kNurbsCurve.
        
        * curvePlug (MPlug) - the curve plug
        """
    
        pass
    
    
    def connectToParamPlug(*args, **kwargs):
        """
        connectToParamPlug(paramPlug) -> self
        
        Connect to the param plug. The data type corresponding to the paramPlug is a double.
        
        * paramPlug (MPlug) - the param plug
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, paramName=None) -> MObject
        
        Creates a new PointOnCurveManip.
        This function set's object is set to be the new manipulator.
        
        This method should only be used to create a non-composite PointOnCurveManip.
        
        The name that appears in the feedback line is specified by the paramName argument.
        
        * manipName (string) - Name of the manip for UI purposes.
        * paramName (string) - Label for the parameter value that appears in the feedback line.
        """
    
        pass
    
    
    def curveIndex(*args, **kwargs):
        """
        curveIndex() -> int
        
        Returns the index of the curve. The data type corresponding to this index is MFnData::kNurbsCurve.
        """
    
        pass
    
    
    def curvePoint(*args, **kwargs):
        """
        curvePoint() -> MPoint
        
        Returns the curve point.
        """
    
        pass
    
    
    def paramIndex(*args, **kwargs):
        """
        paramIndex() -> int
        
        Returns the index of the parameter of the PointOnCurveManip. The data type corresponding to this index is a double.
        """
    
        pass
    
    
    isDrawCurveOn = None
    
    parameter = None
    
    __new__ = None


class MFnCurveSegmentManip(MFnManip3D):
    """
    The CurveSegmentManip allows the user to manipulate two points on a curve, in order to specify a curve segment. This manipulator generates two floating point values, which correspond to the parameters of the start and end of the curve segment.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectToCurvePlug(*args, **kwargs):
        """
        connectToCurvePlug(curvePlug) -> self
        
        Connect to the curve plug. The data type corresponding to the curvePlug is MFnData.kNurbsCurve.
        
        * curvePlug (MPlug) - the curve plug
        """
    
        pass
    
    
    def connectToEndParamPlug(*args, **kwargs):
        """
        connectToEndParamPlug(endParamPlug) -> self
        
        Connect to the endParam plug. The data type corresponding to the endParamPlug is a double.
        
        * endParamPlug (MPlug) - the endParam plug
        """
    
        pass
    
    
    def connectToStartParamPlug(*args, **kwargs):
        """
        connectToStartParamPlug(startParamPlug) -> self
        
        Connect to the startParam plug. The data type corresponding to the startParamPlug is a double.
        
        * startParamPlug (MPlug) - the startParam plug
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, startParamName=None, endParamName=None) -> MObject
        
        Creates a new CurveSegmentManip.
        This function set's object is set to be the new manipulator.
        
        This method should only be used to create a non-composite CurveSegmentManip.
        
        The names that appears in the feedback line are specified by the startParamName and endParamName arguments.
        
        * manipName (string) - Name of the manip for UI purposes.
        * startParamName (string) - Label for the startParam value which appears in the feedback line.
        * endParamName (string) - Label for the endParam value which appears in the feedback line.
        """
    
        pass
    
    
    def curveIndex(*args, **kwargs):
        """
        curveIndex() -> int
        
        Returns the index of the curve. The data type corresponding to this index is MFnData.kNurbsCurve.
        """
    
        pass
    
    
    def endParamIndex(*args, **kwargs):
        """
        endParamIndex() -> int
        
        Returns the index of the end parameter of the CurveSegmentManip. The data type corresponding this index is a double.
        """
    
        pass
    
    
    def startParamIndex(*args, **kwargs):
        """
        startParamIndex() -> int
        
        Returns the index of the start parameter of the CurveSegmentManip. The data type corresponding to this index is a double.
        """
    
        pass
    
    
    endParameter = None
    
    startParameter = None
    
    __new__ = None


class MFnScaleManip(MFnManip3D):
    """
    This class provides access to the built-in Maya scale manipulator.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectToScaleCenterPlug(*args, **kwargs):
        """
        connectToScaleCenterPlug(scaleCenterPlug) -> self
        
        Create a 1-1 association of the scale center on the manipulator and the scaleCenterPlug parameter.  When both the scale center is attached to a plug and the displayWithNode() method has been called, the manipulator will display with the node regardless of the connection made to the scale center.
        
        The plug must have a data type of MFnNumericData.k3Double.
        
        * scaleCenterPlug (MPlug) - The plug to connect the scale center to
        """
    
        pass
    
    
    def connectToScalePlug(*args, **kwargs):
        """
        connectToScalePlug(scalePlug) -> self
        
        Create a 1-1 connection from the scale manipVal to the scalePlug parameter.  Any changes to the scale manipVal will be immediately reflected in the connected plug.  Connecting to the "scale" plug on a transform node will produce similar behavior to the built-in scale manipulator.
        
        The plug must have a data type of MFnNumericData.k3Double.
        
        * scalePlug (MPlug) - The plug to connect the scale value to
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, scaleName=None) -> MObject
        
        Creates a new ScaleManip, and attaches this function set to the new manipulator.
        
        This method should only be used to create a non-composite manipulator, meaning that the manipulator is standalone and not part of a container.
        
        When the manipulator is being used, the feedback line will display a string including scaleName, indicating that this manipulator is in use.
        
        * manipName (string) - Name of the manip for UI purposes.
        * scaleName (string) - Label for the scale value displayed in the feedback line.
        """
    
        pass
    
    
    def displayWithNode(*args, **kwargs):
        """
        displayWithNode(node) -> self
        
        Configures the manipulator to display with the node, causing the position of the manipulator to follow the position of the node whenever the node is moved.  The node must be a DAG object.
        
        * node (MObject) - The node the manipulator should display with
        """
    
        pass
    
    
    def scaleCenterIndex(*args, **kwargs):
        """
        scaleCenterIndex() -> int
        
        Returns the index of the scale center manipVal for this manipulator.
        
        Note that the scale center is only used for display of the manipulator and has no effect on scale values produced by the manipulator.
        """
    
        pass
    
    
    def scaleIndex(*args, **kwargs):
        """
        scaleIndex() -> int
        
        Returns the index of the scale manipVal for this manipulator.
        """
    
        pass
    
    
    def setInitialScale(*args, **kwargs):
        """
        setInitialScale(scale) -> self
        
        Sets the initial scale for the scale manipulator.  Setting the initial scale will prevent the manipulator from jumping back to the default scale when there is already an existing scale on the target plug.
        
        * scale (MVector) - The initial scale
        """
    
        pass
    
    
    isSnapModeOn = None
    
    orientation = None
    
    orientationMode = None
    
    snapIncrement = None
    
    __new__ = None
    
    
    kArbitraryOrientation = 1
    
    
    kDefaultOrientation = 0


class MFnDistanceManip(MFnManip3D):
    """
    The DistanceManip allows the user to manipulate a point that is constrained to move along a line. This manipulator generates a single floating point value. Scaling factors can be used to determine how the manipulator appears when it is drawn.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectToDistancePlug(*args, **kwargs):
        """
        connectToDistancePlug(directionPlug) -> self
        
        Connect to the distance plug. The data type corresponding to the distancePlug is a double. (Note that MFnUnitAttribute.kDistance is used to specify a distance attribute.)
        
        * distancePlug (MPlug) - the distance plug
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, distanceName=None) -> MObject
        
        Creates a new DistanceManip.
        This function set's object is set to be the new manipulator.
        
        This method should only be used to create a non-composite DistanceManip.
        
        The name that appears in the feedback line is specified by the distanceName argument.
        
        * manipName (string) - Name of the manip for UI purposes.
        * distanceName (string) - Label for the distance value which appears in the feedback line.
        """
    
        pass
    
    
    def currentPointIndex(*args, **kwargs):
        """
        currentPointIndex() -> int
        
        Returns the index of the current point of the DistanceManip. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def directionIndex(*args, **kwargs):
        """
        directionIndex() -> int
        
        Returns the index of the direction. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    def distanceIndex(*args, **kwargs):
        """
        distanceIndex() -> int
        
        Returns the index of the distance. The data type corresponding to this index is a double.
        """
    
        pass
    
    
    def setDirection(*args, **kwargs):
        """
        setDirection(direction) -> self
        
        Sets the direction of the DistanceManip.
        
        * direction (MVector) - the direction of the DistanceManip
        """
    
        pass
    
    
    def setStartPoint(*args, **kwargs):
        """
        setStartPoint(startPoint) -> self
        
        Sets the start point of the DistanceManip.
        
        * startPoint (MPoint) - the start point of the DistanceManip
        """
    
        pass
    
    
    def startPointIndex(*args, **kwargs):
        """
        startPointIndex() -> int
        
        Returns the index of the start point of the DistanceManip. The data type corresponding to this index is MFnNumericData.k3Double.
        """
    
        pass
    
    
    isDrawLineOn = None
    
    isDrawStartOn = None
    
    scalingFactor = None
    
    __new__ = None


class MFnPointOnSurfaceManip(MFnManip3D):
    """
    The PointOnSurfaceManip allows the user to manipulate a point constrained to move along a surface, in order to specify the (u, v) surface parameter values. This manipulator generates two floating point values corresponding to the surface (u, v) parameters.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectToParamPlug(*args, **kwargs):
        """
        connectToParamPlug(paramPlug) -> self
        
        Connect to the param plug. The data type corresponding to the paramPlug is MFnNumericData.k2Double.
        
        * paramPlug (MPlug) - the param plug
        """
    
        pass
    
    
    def connectToSurfacePlug(*args, **kwargs):
        """
        connectToSurfacePlug(surfacePlug) -> self
        
        Connect to the surface plug. The data type corresponding to the surfacePlug is MFnData.kNurbsSurface.
        
        * surfacePlug (MPlug) - the surface plug
        """
    
        pass
    
    
    def create(*args, **kwargs):
        """
        create(manipName=None, paramName=None) -> MObject
        
        Creates a new PointOnSurfaceManip.
        This function set's object is set to be the new manipulator.
        
        This method should only be used to create a non-composite PointOnSurfaceManip.
        
        The name that appears in the feedback line is specified by the paramName argument.
        
        * manipName (string) - Name of the manip for UI purposes.
        * paramName (string) - Label for the parameter value which appears in the feedback line
        """
    
        pass
    
    
    def paramIndex(*args, **kwargs):
        """
        paramIndex() -> int
        
        Returns the index of the parameter of the PointOnSurfaceManip. The data type corresponding to this index is MFnNumericData.k2Double.
        """
    
        pass
    
    
    def setDrawArrows(*args, **kwargs):
        """
        setDrawArrows(state) -> self
        
        Sets whether or not the arrows should be drawn.
        
        * state (bool) - whether or not the arrows should be drawn
        """
    
        pass
    
    
    def surfaceIndex(*args, **kwargs):
        """
        surfaceIndex() -> int
        
        Returns the index of the surface. The data type corresponding to this index is MFnData.kNurbsSurface.
        """
    
        pass
    
    
    isDrawSurfaceOn = None
    
    uParam = None
    
    vParam = None
    
    __new__ = None



