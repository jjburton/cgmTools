def projectionManip(*args, **kwargs):
    """
    Various commands to set the manipulator to interesting positions.                In query mode, return type is based on
    queried flag.
    
    Flags:
      - fitBBox : fb                   (bool)          [create]
          Fit the projection manipulator size and position to the shading group bounding box. The orientation is not modified.
    
      - projType : pt                  (int)           [create]
          Set the projection type to the given value. Projection type values are: 1 = planar.2 = spherical.3 = cylindrical.4 =
          ball.5 = cubic.6 = triplanar.7 = concentric.8 = camera.
    
      - switchType : st                (bool)          [create]
          Loop over the allowed types. If the hardware shading is on, it loops over the hardware shadeable types (planar,
          cylindrical, spherical), otherwise, it loops over all the types. If there is no given value, it loops over the different
          projection types.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.projectionManip`
    """

    pass


def lsThroughFilter(*args, **kwargs):
    """
    List all objects in the world that pass a given filter.
    
    Modifications:
      - returns an empty list when the result is None
      - returns wrapped classes
    
    Flags:
      - item : it                      (unicode)       [create]
          Run the filter on specified node(s), using the fast version of this command.
    
      - nodeArray : na                 (bool)          [create]
          Fast version that runs an entire array of nodes through the filter at one time.
    
      - reverse : rv                   (bool)          [create]
          Only available in conjunction with nodeArray flag. Reverses the order of nodes in the returned arrays if true.
    
      - selection : sl                 (bool)          [create]
          Run the filter on selected nodes only, using the fast version of this command.
    
      - sort : so                      (unicode)       [create]
          Only available in conjunction with nodeArray flag. Orders the nodes in the returned array. Current options are: byName,
          byType, and byTime.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.lsThroughFilter`
    """

    pass


def frameBufferName(*args, **kwargs):
    """
    Returns the frame buffer name for a given renderPass renderLayer and camera combination. Optionally, this command can
    apply a name truncation algorithm so that the frameBuffer name will respect the maximum length imposed by the
    destination file format, if applicable.
    
    Flags:
      - autoTruncate : a               (bool)          [create]
          use this flag to apply a name truncation algorithm so that the frameBuffer name will respect the maximum length imposed
          by the destination file format, if applicable.
    
      - camera : c                     (unicode)       [create]
          Specify a camera
    
      - renderLayer : l                (unicode)       [create]
          Specify a renderer layer
    
      - renderPass : p                 (unicode)       [create]
          Specify a renderer pass                                    Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.frameBufferName`
    """

    pass


def lookThru(*args, **kwargs):
    """
    This command sets a particular camera to look through in a view. This command may also be used to view the negative z
    axis of lights or other DAG objects. The standard camera tools can then be used to place the object. Note: if there are
    multiple objects under the transform selected, cameras and lights take precedence. In query mode, return type is based
    on queried flag.
    
    Flags:
      - farClip : fc                   (float)         [create]
          Used when setting clip far plane for a new look thru camera. Will not affect the attributes of an existing camera. Clip
          values must come before shape or view.
    
      - nearClip : nc                  (float)         [create]
          Used when setting near clip plane for a new look thru camera. Will not affect the attributes of an existing camera. Clip
          values must come before shape or view.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.lookThru`
    """

    pass


def glRenderEditor(*args, **kwargs):
    """
    Create a glRender view. This is a special view used for hardware rendering. This command is used to create and reparent
    the view as needed to support panels. See the glRender command for controlling the specific behavior of the hardware
    rendering. In query mode, return type is based on queried flag.
    
    Flags:
      - control : ctl                  (bool)          [query]
          Query only. Returns the top level control for this editor. Usually used for getting a parent to attach popup menus.
          Caution: It is possible for an editor to exist without a control. The query will return NONEif no control is present.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Attaches a tag to the editor.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - filter : f                     (unicode)       [create,query,edit]
          Specifies the name of an itemFilter object to be used with this editor. This filters the information coming onto the
          main list of the editor.
    
      - forceMainConnection : fmc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object. This is a variant of the -mainListConnection flag in
          that it will force a change even when the connection is locked. This flag is used to reduce the overhead when using the
          -unlockMainConnection , -mainListConnection, -lockMainConnection flags in immediate succession.
    
      - highlightConnection : hlc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its highlight list. Not all
          editors have a highlight list. For those that do, it is a secondary selection list.
    
      - lockMainConnection : lck       (bool)          [create,edit]
          Locks the current list of objects within the mainConnection, so that only those objects are displayed within the editor.
          Further changes to the original mainConnection are ignored.
    
      - lookThru : lt                  (unicode)       [create,query,edit]
          Specify which camera the glRender view should be using.
    
      - mainListConnection : mlc       (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object.
    
      - panel : pnl                    (unicode)       [create,query]
          Specifies the panel for this editor. By default if an editor is created in the create callback of a scripted panel it
          will belong to that panel. If an editor does not belong to a panel it will be deleted when the window that it is in is
          deleted.
    
      - parent : p                     (unicode)       [create,query,edit]
          Specifies the parent layout for this editor. This flag will only have an effect if the editor is currently un-parented.
    
      - selectionConnection : slc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its own selection list. As the
          user selects things in this editor, they will be selected in the selectionConnection object. If the object undergoes
          changes, the editor updates to show the changes.
    
      - stateString : sts              (bool)          [query]
          Query only flag. Returns the MEL command that will create an editor to match the current editor state. The returned
          command string uses the string variable $editorName in place of a specific name.
    
      - unParent : up                  (bool)          [create,edit]
          Specifies that the editor should be removed from its layout. This cannot be used in query mode.
    
      - unlockMainConnection : ulk     (bool)          [create,edit]
          Unlocks the mainConnection, effectively restoring the original mainConnection (if it is still available), and dynamic
          updates.
    
      - updateMainConnection : upd     (bool)          [create,edit]
          Causes a locked mainConnection to be updated from the orginal mainConnection, but preserves the lock state.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - viewCameraName : vcn           (bool)          [query]
          Returns the name of the current camera used by the glRenderPanel. This is a query only flag.                  Flag can
          have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.glRenderEditor`
    """

    pass


def viewSet(*args, **kwargs):
    """
    This command positions the camera to one of the pre-defined positions. If the fit flag is set in conjunction with persp,
    top, side, or front, the view is fitbased on the list of selected objects (if there are any) or on all the objects if
    nothing is selected. Notice that the fit flag cannot be set in conjunction with view along axis commands like viewX. If
    a camera is not specified, the camera in the active view will be used. If no flag is specified, the camera is set to the
    home position. In query mode, return type is based on queried flag.
    
    Flags:
      - animate : an                   (bool)          [create]
          Specifies that the transition between camera positions should be animated.
    
      - back : b                       (bool)          [create]
          Moves the camera to the back position.
    
      - bottom : bo                    (bool)          [create]
          Moves the camera to the bottom position.
    
      - fit : fit                      (bool)          [create,query]
          Apply a viewFit after positioning camera to persp, top, side, or front.
    
      - fitFactor : ff                 (float)         [create]
          Specifies how much of the view should be filled with the fitteditems
    
      - front : f                      (bool)          [create]
          Moves the camera to the front position.
    
      - home : h                       (bool)          [create]
          Executes the camera's home attribute command. Before the string is executed, all occurances of %camerawill be replaced
          by the camera's name. Use the camera command to set a camera's home command.
    
      - keepRenderSettings : krs       (bool)          [create,query]
          Retain the 'renderable' flag vaue on the view. Especially important if it switches from perspective to orthographic and
          then back again.
    
      - leftSide : ls                  (bool)          [create]
          Moves the camera to the left side position.
    
      - namespace : ns                 (unicode)       [create]
          Specifies a namespace that should be excluded. All objects in the specified namespace will be excluded from the fit
          process.
    
      - nextView : nv                  (bool)          [create,query]
          Moves the camera to the next position.
    
      - persp : p                      (bool)          [create]
          Moves the camera to the persp position.
    
      - previousView : pv              (bool)          [create,query]
          Moves the camera to the previous position.
    
      - rightSide : rs                 (bool)          [create]
          Moves the camera to the right side position.
    
      - side : s                       (bool)          [create]
          Moves the camera to the (right) side position (deprecated).
    
      - t : t                          (bool)          []
    
      - top : t                        (bool)          [create]
          Moves the camera to the top position.
    
      - viewNegativeX : vnx            (bool)          [create]
          Moves the camera to view along negative X axis.
    
      - viewNegativeY : vny            (bool)          [create]
          Moves the camera to view along negative Y axis.
    
      - viewNegativeZ : vnz            (bool)          [create]
          Moves the camera to view along negative Z axis.
    
      - viewX : vx                     (bool)          [create]
          Moves the camera to view along X axis.
    
      - viewY : vy                     (bool)          [create]
          Moves the camera to view along Y axis.
    
      - viewZ : vz                     (bool)          [create]
          Moves the camera to view along Z axis.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.viewSet`
    """

    pass


def renderQualityNode(*args, **kwargs):
    """
    The renderQualityNode creates a render quality node and registers it with the model.  The createNode command will not
    register nodes of this type correctly.
    
    Flags:
      - name : n                       (unicode)       []
    
      - parent : p                     (unicode)       []
    
      - shared : s                     (bool)          []
    
      - skipSelect : ss                (bool)          []
    
    
    Derived from mel command `maya.cmds.renderQualityNode`
    """

    pass


def render(*args, **kwargs):
    """
    The render command is used to start off a MayaSoftware rendering session of the currently active camera. If a rendering
    is already in progress, then this command stops the rendering. This command is not undoable.
    
    Flags:
      - abortMissingTexture : amt      (bool)          [create]
          Abort renderer when encountered missing texture. Only available when -batch is set
    
      - batch : b                      (bool)          [create]
          Run in batch mode. Compute the images for all renderable cameras. This is the mel equivalent of running maya in batch
          mode with the -render flag set. All other flags are ignored when -batch is used.
    
      - keepPreImage : kpi             (bool)          [create]
          Keep the renderings prior to post-process around. Only available when -batch is set
    
      - layer : l                      (unicode)       [create]
          Render the specified render layer. Only this render layer will be rendered, regardless of the renderable attribute value
          of the render layer. The layer name will be appended to the output image file name. The specified render layer becomes
          the current render layer before rendering, and remains as current render layer after the rendering.
    
      - nglowpass : ngl                (bool)          [create]
          Overwrite glow pass capabilities (can turn off glow pass globally by setting this value to false)
    
      - nshadows : nsh                 (bool)          [create]
          Shadowing capabilities (can turn off shadow globally by setting this value to false)
    
      - replace : rep                  (bool)          [create]
          Replace the rendered image if it already exists. Only available when -batch is set
    
      - xresolution : x                (int)           [create]
          Overwrite x resolution
    
      - yresolution : y                (int)           [create]
          Overwrite y resolution                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.render`
    """

    pass


def pointLight(*args, **kwargs):
    """
    The pointLight command is used to edit the parameters of existing pointLights, or to create new ones. The default
    behaviour is to create a new pointlight.
    
    Maya Bug Fix:
      - name flag was ignored
    
    Flags:
      - decayRate : d                  (int)           [create,query,edit]
          decay rate of the light (0-no decay, 1-slow, 2-realistic, 3-fast)
    
      - discRadius : drs               (float)         [create,query,edit]
          radius of the disc around the light
    
      - exclusive : exc                (bool)          [create,query,edit]
          This flag is obsolete.
    
      - intensity : i                  (float)         [create,query,edit]
          intensity of the light (expressed as a percentage)
    
      - name : n                       (unicode)       [create,query,edit]
          specify the name of the light
    
      - position : pos                 (float, float, float) [create,query,edit]
          This flag is obsolete.
    
      - rgb : rgb                      (float, float, float) [create,query,edit]
          color of the light (0-1)
    
      - rotation : rot                 (float, float, float) [create,query,edit]
          This flag is obsolete.
    
      - shadowColor : sc               (float, float, float) [create,query,edit]
          the shadow color
    
      - shadowDither : sd              (float)         [create,query,edit]
          dither the shadow
    
      - shadowSamples : sh             (int)           [create,query,edit]
          number of shadow samples.
    
      - softShadow : ss                (bool)          [create,query,edit]
          soft shadow
    
      - useRayTraceShadows : rs        (bool)          [create,query,edit]
          ray trace shadows                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.pointLight`
    """

    pass


def renderLayerPostProcess(*args, **kwargs):
    """
    Post process the results when rendering is done with. Presently this generates a layered PSD file using individual iff
    files.            In query mode, return type is based on queried flag.
    
    Flags:
      - keepImages : ki                (bool)          [create,query]
          When set to on, the original iff images are kept after the conversion to PSD. Default is to remove them.
    
      - sceneName : sn                 (unicode)       [create,query]
          Specifies the scene name for interactive batch rendering.                                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.renderLayerPostProcess`
    """

    pass


def editRenderLayerAdjustment(*args, **kwargs):
    """
    This command is used to create, edit, and query adjustments to render layers. An adjustment allows different attribute
    values or connections to be used depending on the active render layer.
    
    Flags:
      - attributeLog : alg             (bool)          [query]
          Output all adjustments for the specified layer sorted by attribute name.
    
      - layer : lyr                    (PyNode)        [create,query]
          Specified layer in which the adjustments will be modified. If not specified the active render layer will be used.
    
      - nodeLog : nlg                  (bool)          [query]
          Output all adjustments for the specified layer sorted by node name.
    
      - remove : r                     (bool)          [create]
          Remove the specified adjustments from the render layer. If an adjustment is removed from the current layer, the
          specified plug will revert back to it's master value determined by the default render layer.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.editRenderLayerAdjustment`
    """

    pass


def hwRender(*args, **kwargs):
    """
    Renders an image or a sequence using the hardware rendering engine
    
    Flags:
      - acceleratedMultiSampleSupport : ams (bool)          [query]
          This flag when used with query will return whether the graphics supports     hardware accelerated multi-sampling.
    
      - activeTextureCount : atc       (bool)          [query]
          This flag when used with query will return the number of textures that     have been bound to the graphics by the
          hardware renderer.
    
      - camera : cam                   (unicode)       [create,query]
          Specify the camera to use.  Use the first available camera if the camera         given is not found.
    
      - currentFrame : cf              (bool)          [create,query]
          Render the current frame.
    
      - currentView : cv               (bool)          [create,query]
          When turned on, only the current view will be rendered.
    
      - edgeAntiAliasing : eaa         (int, int)      [create,query]
          Enables multipass rendering. Controls for the number of exposures rendered per frame are provided in the form of two
          associated flag arguments. The first specifies the sampling algorithm: 0 - Uniform Weighted Grid Sampling1 - Rotated
          Grid Super Sampling (RGSS)2 - Gaussian Weighted SamplingUse of a sampling method other than the others listed above,
          will result in use of the default sample method of Uniform Weighted Grid Sampling. The second argument specifies a
          number of samples to use. For each sampling algorithm there is a fixed set of sample counts available: 0 - Uniform
          Weighted Grid Sampling1 Sample3 Samples4 Samples5 Samples7 Samples9 Samples16 Samples25 Samples36 Samples1 - Rotated
          Grid Super Sampling (RGSS)1 Sample4 Samples5 Samples2 - Gaussian Weighted Sampling1 Sample3 Samples4 Samples5 Samples7
          Samples9 Samples16 Samples25 Samples36 SamplesUsing a sampling count other than the allowable options for the given
          sampling method will result in using the default sample count of 5. The values passed via the command will override
          settings stored in the hardwareRenderGlobals node.
    
      - fixFileNameNumberPattern : fnp (bool)          [create,query]
          This flag allows the user to take the hardwareRenderGlobals     filename as the initial filename pattern,     fix the
          frame number pattern in the filename in a unique way,     returns the new filename pattern.  This does not change the
          hardwareRenderGlobals's filename.
    
      - frame : f                      (float)         [create]
          Specify the frame to render.
    
      - fullRenderSupport : frs        (bool)          [create,query]
          This flag may be used in the create or query context.     In the create context, it will force the renderer to abort and
          not     render any frames if the hardware is not fully supported.         In the query context, it will return whether
          full quality rendering     is supported on the current graphics system. Please see the graphics     card qualification
          charts for an explanation of limited support.
    
      - height : h                     (int)           [create,query]
          Height. If not used, the height is taken from the render globals settings.
    
      - imageFileName : ifn            (bool)          [create,query]
          This flag let people query the image name for a specified frame.     The frame can be specified using the -frameflag.
          When no -frameis used, the     current frame number is used.
    
      - layer : l                      (PyNode)        [create,query]
          Render the specified render layer.         Only this render layer will be rendered,         regardless of the renderable
          attribute value of the render layer.         The layer name will be appended to the output image file name.         The
          specified render layer becomes the current render layer before rendering,         and remains as current render layer
          after the rendering.
    
      - limitedRenderSupport : lrs     (bool)          [query]
          This flag when used with query will return whether limited rendering is supported         on the current graphics
          system. Please see the graphics card qualification         charts for the current definition of limited support.
    
      - lowQualityLighting : lql       (bool)          [create,query]
          Disable lighting evaluation per pixel (fragment).         Note: The values passed via the command will override settings
          stored in     the hardware render globals node.
    
      - noRenderView : nrv             (bool)          [create,query]
          When turned on, the render view is not updated after image computation
    
      - notWriteToFile : nwf           (bool)          [create,query]
          This flag is set to true if the user does not want to write     the image to a file.  It is set to false, otherwise.
          The default value of the flag is false.
    
      - printGeometry : pg             (bool)          [create,query]
          Print the geomety objects as they get translated.
    
      - renderHardwareName : rhw       (bool)          [query]
          This flag will create a graphics context and return the name of the     graphics hardware being used. The graphics
          hardware is determined by     creating an off screen buffer and querying the GL_RENDERER string     from OpenGL. If the
          off screen buffer cannot be created an empty     string is returned.
    
      - renderRegion : reg             (int, int, int, int) [create,query]
          Render region. The parameters are 4 integers, indicating             left right bottom top     of the region.
    
      - renderSelected : rs            (bool)          [create,query]
          Only renders the selected objects.
    
      - textureResolution : res        (int)           [create,query]
          Specify the desired resolution of baked textures.
    
      - width : w                      (int)           [create,query]
          Width. If not used, the width is taken from the render globals settings.
    
      - writeAlpha : a                 (bool)          [create,query]
          Read the alpha channel of color buffer and return as tif file.
    
      - writeDepth : d                 (bool)          [create,query]
          Read the depth buffer and return as tif file.                              Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.hwRender`
    """

    pass


def psdExport(*args, **kwargs):
    """
    Writes the Photoshop file layer set into different formats.  The output         file depth (bit per channel ) can be
    different from that of the input.         If the input is 16 bpc and output is 8 bpc, there will be data loss.
    In query mode, return type is based on queried flag.
    
    Dynamic library stub function
    
    Flags:
      - alphaChannelIdx : aci          (int)           [create,query]
          Index of the alpha channel to output, if not supplied, writes out the default alpha channel.  The index is zero based.
          This is useful to write out specific alpha channels available as Additional Alpha Channelsof Photoshop.
    
      - bytesPerChannel : bpc          (int)           [create,query]
          Output file depth. Any of these keyword: 0 for choosing depth based on input1 for 8 bits per channel2 for 16 bits per
          channelDefault is 0.
    
      - emptyLayerSet : els            (bool)          [create,query]
          Option to check if the given layer set is empty or not.  This should be used in query mode and input file name and layer
          set names should be specified.
    
      - format : format                (unicode)       [create,query]
          Output file format. Any of these keyword: iff, sgi, pic, tif, als, gif, rla, jpgDefault is iff.
    
      - layerName : lyn                (unicode)       [create,query]
          Name of the layer to output.
    
      - layerSetName : lsn             (unicode)       [create,query]
          Name of the layer set to output, if not supplied, writes out the Composite image.
    
      - outFileName : ofn              (unicode)       [create,query]
          Name(with path) of the output file.
    
      - preMultiplyAlpha : pma         (bool)          [create,query]
          Option to multiply RGB colors with alpha values.  If (r,g,b,a) is the value of pixel, it will be changed to (r\*a, g\*a,
          b\*a, a) when this flag is used.
    
      - psdFileName : ifn              (unicode)       [create,query]
          Name(with path) of the input Photoshop file. Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.psdExport`
    """

    pass


def soloMaterial(*args, **kwargs):
    """
    Shows a preview of a specified material node output attribute.
    
    Flags:
      - attr : a                       (unicode)       [create,query]
          The attr flag specifies a node attribute to solo.
    
      - last : l                       (bool)          [create,query]
          Whether to solo the last material node and attribute.
    
      - node : n                       (unicode)       [create,query]
          The node flag specifies the node to solo.
    
      - unsolo : us                    (bool)          [create,query]
          Whether to remove soloing.                                 Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.soloMaterial`
    """

    pass


def layeredTexturePort(*args, **kwargs):
    """
    This command creates a 3dPort that displays an image representing the layered texture node specified.
    
    Flags:
      - annotation : ann               (unicode)       [create,query,edit]
          Annotate the control with an extra string value.
    
      - backgroundColor : bgc          (float, float, float) [create,query,edit]
          The background color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0. When setting backgroundColor, the background is automatically enabled, unless
          enableBackground is also specified with a false value.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Add a documentation flag to the control.  The documentation flag has a directory structure like hierarchy. Eg. -dt
          render/multiLister/createNode/material
    
      - dragCallback : dgc             (script)        [create,edit]
          Adds a callback that is called when the middle mouse button is pressed.  The MEL version of the callback is of the form:
          global proc string[] callbackName(string $dragControl, int $x, int $y, int $mods) The proc returns a string array that
          is transferred to the drop site. By convention the first string in the array describes the user settable message type.
          Controls that are application defined drag sources may ignore the callback. $mods allows testing for the key modifiers
          CTL and SHIFT. Possible values are 0 == No modifiers, 1 == SHIFT, 2 == CTL, 3 == CTL + SHIFT. In Python, it is similar,
          but there are two ways to specify the callback.  The recommended way is to pass a Python function object as the
          argument.  In that case, the Python callback should have the form: def callbackName( dragControl, x, y, modifiers ): The
          values of these arguments are the same as those for the MEL version above. The other way to specify the callback in
          Python is to specify a string to be executed.  In that case, the string will have the values substituted into it via the
          standard Python format operator.  The format values are passed in a dictionary with the keys dragControl, x, y,
          modifiers.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(x)d %(y)d %(modifiers)d'
    
      - dropCallback : dpc             (script)        [create,edit]
          Adds a callback that is called when a drag and drop operation is released above the drop site.  The MEL version of the
          callback is of the form: global proc callbackName(string $dragControl, string $dropControl, string $msgs[], int $x, int
          $y, int $type) The proc receives a string array that is transferred from the drag source. The first string in the msgs
          array describes the user defined message type. Controls that are application defined drop sites may ignore the callback.
          $type can have values of 1 == Move, 2 == Copy, 3 == Link. In Python, it is similar, but there are two ways to specify
          the callback.  The recommended way is to pass a Python function object as the argument.  In that case, the Python
          callback should have the form: def pythonDropTest( dragControl, dropControl, messages, x, y, dragType ): The values of
          these arguments are the same as those for the MEL version above. The other way to specify the callback in Python is to
          specify a string to be executed.  In that case, the string will have the values substituted into it via the standard
          Python format operator.  The format values are passed in a dictionary with the keys dragControl, dropControl, messages,
          x, y, type.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(dropControl)s %(messages)r %(x)d %(y)d %(type)d'
    
      - enable : en                    (bool)          [create,query,edit]
          The enable state of the control.  By default, this flag is set to true and the control is enabled.  Specify false and
          the control will appear dimmed or greyed-out indicating it is disabled.
    
      - enableBackground : ebg         (bool)          [create,query,edit]
          Enables the background color of the control.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - fullPathName : fpn             (bool)          [query]
          Return the full path name of the widget, which includes all the parents
    
      - height : h                     (int)           [create,query,edit]
          The height of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
    
      - highlightColor : hlc           (float, float, float) [create,query,edit]
          The highlight color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0.
    
      - isObscured : io                (bool)          [query]
          Return whether the control can actually be seen by the user. The control will be obscured if its state is invisible, if
          it is blocked (entirely or partially) by some other control, if it or a parent layout is unmanaged, or if the control's
          window is invisible or iconified.
    
      - manage : m                     (bool)          [create,query,edit]
          Manage state of the control.  An unmanaged control is not visible, nor does it take up any screen real estate.  All
          controls are created managed by default.
    
      - noBackground : nbg             (bool)          [create,edit]
          Clear/reset the control's background. Passing true means the background should not be drawn at all, false means the
          background should be drawn.  The state of this flag is inherited by children of this control.
    
      - node : n                       (PyNode)        [create]
          Specifies the name of the newLayeredTexture node this port will represent.
    
      - numberOfPopupMenus : npm       (bool)          [query]
          Return the number of popup menus attached to this control.
    
      - parent : p                     (unicode)       [create,query]
          The parent layout for this control.
    
      - popupMenuArray : pma           (bool)          [query]
          Return the names of all the popup menus attached to this control.
    
      - preventOverride : po           (bool)          [create,query,edit]
          If true, this flag disallows overriding the control's attribute via the control's right mouse button menu.
    
      - selectedAlphaControl : sac     (unicode)       [create]
          Specifies the name of the UI-control that represents the currently selected layer's alpha.
    
      - selectedBlendModeControl : sbc (unicode)       [create]
          Specifies the name of the UI-control that represents the currently selected layer's blend mode.
    
      - selectedColorControl : scc     (unicode)       [create]
          Specifies the name of the UI-control that represents the currently selected layer's color.
    
      - selectedIsVisibleControl : svc (unicode)       [create]
          Specifies the name of the UI-control that represents the currently selected layer's visibility.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - visible : vis                  (bool)          [create,query,edit]
          The visible state of the control.  A control is created visible by default.  Note that a control's actual appearance is
          also dependent on the visible state of its parent layout(s).
    
      - visibleChangeCommand : vcc     (script)        [create,query,edit]
          Command that gets executed when visible state of the control changes.
    
      - width : w                      (int)           [create,query,edit]
          The width of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.layeredTexturePort`
    """

    pass


def panZoom(*args, **kwargs):
    """
    The panZoom command pans/zooms the 2D film. The panZoom command can be applied to either a perspective or an
    orthographic camera. When no camera name is supplied, this command is applied to the camera in the active view.
    
    Flags:
      - absolute : abs                 (bool)          [create]
          This flag modifies the behavior of the distance and zoomRatio flags. If specified, the distance and zoomRatio value will
          be applied directly.
    
      - downDistance : d               (float)         [create]
          Set the amount of down pan distance in inches
    
      - leftDistance : l               (float)         [create]
          Set the amount of left pan distance in inches
    
      - relative : rel                 (bool)          [create]
          This flag modifies the behavior of the distance and zoomRatio flags. If specified, the distance or zoomRatio value is
          used multiply the camera's existing value. By default the relative flag is always on.
    
      - rightDistance : r              (float)         [create]
          Set the amount of right pan distance in inches
    
      - upDistance : u                 (float)         [create]
          Set the amount of up pan distance in inches
    
      - zoomRatio : z                  (float)         [create]
          Set the amount of zoom ratio                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.panZoom`
    """

    pass


def editRenderLayerMembers(*args, **kwargs):
    """
    This command is used to query and edit memberships to render layers. Only transform and geometry nodes may be members.
    At render time, all descendants of the members of a render layer will also be included in the render layer.
    
    Flags:
      - fullNames : fn                 (bool)          [query]
          (Query only.) If set then return the full DAG paths of the objects in the layer.  Otherwise return just the name of the
          object.
    
      - noRecurse : nr                 (bool)          [create]
          If set then only add selected objects to the render layer.  Otherwise all descendants of the selected objects will also
          be added. This flag may be applied to adding or removing objects from the layer.
    
      - remove : r                     (bool)          [create]
          Remove the specified objects from the render layer.                                Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.editRenderLayerMembers`
    """

    pass


def renderSettings(*args, **kwargs):
    """
    Query interface to the common tab of the render settings
    
    Flags:
      - camera : cam                   (unicode)       [create]
          Specify a camera that you want to replace the current renderable camera
    
      - customTokenString : cts        (unicode)       [create]
          Specify a custom key-value string to use to replace custom tokens in the file name. Use with firstImageName or
          lastImageName. Basic tokens (Scene, Layer, RenderLayer, Camera, Version, Extension) will be automatically expanded. Any
          other tokens must be specified here to be expanded. The format of the string is a space separated list of tokens-value
          pairs. For example, if the file name string is myFile_myToken_myOtherToken_vthen the argument to this flag string should
          take the form myToken=myTokenValue myOtherToken=myOtherTokenValue.
    
      - firstImageName : fin           (bool)          [create]
          Returns the first image name
    
      - fullPath : fp                  (bool)          [create]
          Returns the full path for the image using the current project. Use with firstImageName, lastImageName, or
          genericFrameImageName.
    
      - fullPathTemp : fpt             (bool)          [create]
          Returns the full path for the preview render of the image using the current project. Use with firstImageName,
          lastImageName, or genericFrameImageName.
    
      - genericFrameImageName : gin    (unicode)       [create]
          Returns the generic frame image name with the custom specified frame index token
    
      - imageGenericName : ign         (bool)          [create]
          Returns the image generic name
    
      - lastImageName : lin            (bool)          [create]
          Returns the last image name
    
      - layer : lyr                    (unicode)       [create]
          Specify a render layer name that you want to replace the current render layer
    
      - leaveUnmatchedTokens : lut     (bool)          [create]
          Do not remove unmatched tokens from the name string. Use with firstImageName or lastImageName.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.renderSettings`
    """

    pass


def psdChannelOutliner(*args, **kwargs):
    """
    Create a psdChannelOutliner control which is capable of displaying a tree structure upto one level.
    
    Dynamic library stub function
    
    Flags:
      - addChild : ach                 (unicode, unicode) [edit]
          This flag should be used along with the -psdParent/ppaflag. A string item gets added as a child to the parent specifed
          with -psdParent/ppaflag. The next string assigns an associated image name.
    
      - allItems : all                 (bool)          [query]
          Returns all the items in the form parent.child.
    
      - annotation : ann               (unicode)       [create,query,edit]
          Annotate the control with an extra string value.
    
      - backgroundColor : bgc          (float, float, float) [create,query,edit]
          The background color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0. When setting backgroundColor, the background is automatically enabled, unless
          enableBackground is also specified with a false value.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Add a documentation flag to the control.  The documentation flag has a directory structure like hierarchy. Eg. -dt
          render/multiLister/createNode/material
    
      - doubleClickCommand : dcc       (unicode)       [create,edit]
          Specify the command to be executed when an item is double clicked.
    
      - dragCallback : dgc             (script)        [create,edit]
          Adds a callback that is called when the middle mouse button is pressed.  The MEL version of the callback is of the form:
          global proc string[] callbackName(string $dragControl, int $x, int $y, int $mods) The proc returns a string array that
          is transferred to the drop site. By convention the first string in the array describes the user settable message type.
          Controls that are application defined drag sources may ignore the callback. $mods allows testing for the key modifiers
          CTL and SHIFT. Possible values are 0 == No modifiers, 1 == SHIFT, 2 == CTL, 3 == CTL + SHIFT. In Python, it is similar,
          but there are two ways to specify the callback.  The recommended way is to pass a Python function object as the
          argument.  In that case, the Python callback should have the form: def callbackName( dragControl, x, y, modifiers ): The
          values of these arguments are the same as those for the MEL version above. The other way to specify the callback in
          Python is to specify a string to be executed.  In that case, the string will have the values substituted into it via the
          standard Python format operator.  The format values are passed in a dictionary with the keys dragControl, x, y,
          modifiers.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(x)d %(y)d %(modifiers)d'
    
      - dropCallback : dpc             (script)        [create,edit]
          Adds a callback that is called when a drag and drop operation is released above the drop site.  The MEL version of the
          callback is of the form: global proc callbackName(string $dragControl, string $dropControl, string $msgs[], int $x, int
          $y, int $type) The proc receives a string array that is transferred from the drag source. The first string in the msgs
          array describes the user defined message type. Controls that are application defined drop sites may ignore the callback.
          $type can have values of 1 == Move, 2 == Copy, 3 == Link. In Python, it is similar, but there are two ways to specify
          the callback.  The recommended way is to pass a Python function object as the argument.  In that case, the Python
          callback should have the form: def pythonDropTest( dragControl, dropControl, messages, x, y, dragType ): The values of
          these arguments are the same as those for the MEL version above. The other way to specify the callback in Python is to
          specify a string to be executed.  In that case, the string will have the values substituted into it via the standard
          Python format operator.  The format values are passed in a dictionary with the keys dragControl, dropControl, messages,
          x, y, type.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(dropControl)s %(messages)r %(x)d %(y)d %(type)d'
    
      - enable : en                    (bool)          [create,query,edit]
          The enable state of the control.  By default, this flag is set to true and the control is enabled.  Specify false and
          the control will appear dimmed or greyed-out indicating it is disabled.
    
      - enableBackground : ebg         (bool)          [create,query,edit]
          Enables the background color of the control.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - fullPathName : fpn             (bool)          [query]
          Return the full path name of the widget, which includes all the parents
    
      - height : h                     (int)           [create,query,edit]
          The height of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
    
      - highlightColor : hlc           (float, float, float) [create,query,edit]
          The highlight color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0.
    
      - isObscured : io                (bool)          [query]
          Return whether the control can actually be seen by the user. The control will be obscured if its state is invisible, if
          it is blocked (entirely or partially) by some other control, if it or a parent layout is unmanaged, or if the control's
          window is invisible or iconified.
    
      - manage : m                     (bool)          [create,query,edit]
          Manage state of the control.  An unmanaged control is not visible, nor does it take up any screen real estate.  All
          controls are created managed by default.
    
      - noBackground : nbg             (bool)          [create,edit]
          Clear/reset the control's background. Passing true means the background should not be drawn at all, false means the
          background should be drawn.  The state of this flag is inherited by children of this control.
    
      - numberOfItems : ni             (bool)          [query]
          Total number of items in the control.
    
      - numberOfPopupMenus : npm       (bool)          [query]
          Return the number of popup menus attached to this control.
    
      - parent : p                     (unicode)       [create,query]
          The parent layout for this control.
    
      - popupMenuArray : pma           (bool)          [query]
          Return the names of all the popup menus attached to this control.
    
      - preventOverride : po           (bool)          [create,query,edit]
          If true, this flag disallows overriding the control's attribute via the control's right mouse button menu.
    
      - psdParent : ppa                (unicode)       [edit]
          Adds an item string to the controls which is treated as parent.
    
      - removeAll : ra                 (bool)          [edit]
          Removes all the items from the control.
    
      - removeChild : rc               (unicode)       [edit]
          Deletes the particular child of the parent as specifed in -psdParent/ppaflag.
    
      - selectCommand : sc             (unicode)       [create,edit]
          Specify the command to be executed when an item is selected.
    
      - selectItem : si                (bool)          [query]
          Returns the selected items.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - visible : vis                  (bool)          [create,query,edit]
          The visible state of the control.  A control is created visible by default.  Note that a control's actual appearance is
          also dependent on the visible state of its parent layout(s).
    
      - visibleChangeCommand : vcc     (script)        [create,query,edit]
          Command that gets executed when visible state of the control changes.
    
      - width : w                      (int)           [create,query,edit]
          The width of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.psdChannelOutliner`
    """

    pass


def ambientLight(*args, **kwargs):
    """
    The ambientLight command is used to edit the parameters of existing ambientLights, or to create new ones. The default
    behaviour is to create a new ambientlight.
    
    Maya Bug Fix:
      - name flag was ignored
    
    Flags:
      - ambientShade : ambientShade    (float)         [create,query,edit]
          ambientShade
    
      - discRadius : drs               (float)         [create,query,edit]
          radius of the disc around the light
    
      - exclusive : exc                (bool)          [query,edit]
    
      - intensity : i                  (float)         [create,query,edit]
          intensity of the light (expressed as a percentage)
    
      - name : n                       (unicode)       [create,query,edit]
          specify the name of the light
    
      - position : pos                 (float, float, float) [query,edit]
    
      - rgb : rgb                      (float, float, float) [create,query,edit]
          color of the light (0-1)
    
      - rotation : rot                 (float, float, float) [query,edit]
    
      - shadowColor : sc               (float, float, float) [create,query,edit]
          the shadow color
    
      - shadowDither : sd              (float)         [create,query,edit]
          dither the shadow
    
      - shadowSamples : sh             (int)           [create,query,edit]
          number of shadow samples.
    
      - softShadow : ss                (bool)          [create,query,edit]
          soft shadow
    
      - useRayTraceShadows : rs        (bool)          [create,query,edit]
          ray trace shadows                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.ambientLight`
    """

    pass


def orbit(*args, **kwargs):
    """
    The orbit command revolves the camera(s) horizontally and/or vertically in the perspective window. The rotation axis is
    with respect to the camera. To revolve horizontally: the rotation axis is the camera up direction vector. To revolve
    vertically: the rotation axis is the camera left direction vector. When both the horizontal and the vertical angles are
    supplied on the command line, the camera is firstly revolved horizontally, then revolved vertically. This command may be
    applied to more than one camera; objects that are not cameras are ignored. When no camera name supplied, this command is
    applied to all currently active cameras.
    
    (<function orbit at 0x154a6ac80>, <function addCmdDocsCallback at 0x1546e3578>, ('orbit', ''), {})
    
    Flags:
      - horizontalAngle : ha           (float)         [create]
          Angle to revolve horizontally.
    
      - pivotPoint : pp                (float, float, float) [create]
          Used as the pivot point in the world space.
    
      - rotationAngles : ra            (float, float)  [create]
          Angle to revolve horizontally and vertically.
    
      - verticalAngle : va             (float)         [create]
          Angle to revolve vertically.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.orbit`
    """

    pass


def nodePreset(*args, **kwargs):
    """
    Command to save and load preset settings for a node. This command allows you to take a snapshot of the values of all
    attributes of a node and save it to disk as a preset with user specified name. Later the saved preset can be loaded and
    applied onto a different node of the same type. The end result is that the node to which the preset is applied takes on
    the same values as the node from which the preset was generated had at the time of the snapshot.
    
    Flags:
      - attributes : atr               (unicode)       [create]
          A white space separated string of the named attributes to save to the preset file. If not specified, all attributes will
          be stored.
    
      - custom : ctm                   (unicode)       [create]
          Specifies a MEL script for custom handling of node attributes that are not handled by the general save preset mechanism
          (ie. multis, dynamic attributes, or connections). The identifiers #presetName and #nodeName will be expanded before the
          script is run. The script must return an array of strings which will be saved to the preset file and issued as commands
          when the preset is applied to another node. The custom script can query #nodeName in determining what should be saved to
          the preset, or issue commands to query the selected node in deciding how the preset should be applied.
    
      - delete : delete                (PyNode, <type 'unicode'>) [create]
          Deletes the existing preset for the node specified by the first argument with the name specified by the second argument.
    
      - exists : ex                    (PyNode, <type 'unicode'>) [create]
          Returns true if the node specified by the first argument already has a preset with a name specified by the second
          argument. This flag can be used to check if the user is about to overwrite an existing preset and thereby provide the
          user with an opportunity to choose a different name.
    
      - isValidName : ivn              (unicode)       [create]
          Returns true if the name consists entirely of valid characters for a preset name. Returns false if not. Because the
          preset name will become part of a file name and part of a MEL procedure name, some characters must be disallowed. Only
          alphanumeric characters and underscore are valid characters for the preset name.
    
      - list : ls                      (PyNode)        [create]
          Lists the names of all presets which can be loaded onto the specified node.
    
      - load : ld                      (PyNode, <type 'unicode'>) [create]
          Sets the settings of the node specified by the first argument according to the preset specified by the second argument.
          Any attributes on the node which are the destinations of connections or whose children (multi children or compound
          children) are destinations of connections will not be changed by the preset.
    
      - save : sv                      (PyNode, <type 'unicode'>) [create]
          Saves the current settings of the node specified by the first argument to a preset of the name specified by the second
          argument. If a preset for that node with that name already exists, it will be overwritten with no warning. You can use
          the -exists flag to check if the preset already exists. If an attribute of the node is the destination of a connection,
          the value of the attribute will not be written as part of the preset.                                Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.nodePreset`
    """

    pass


def exclusiveLightCheckBox(*args, **kwargs):
    """
    This command creates a checkBox that controls a light's exclusive non-exclusive status.  An exclusive light is one that
    is not hooked up to the default-light-list, thus it does not illuminate all objects be default.  However an exclusive
    light can be linked to an object.
    
    Flags:
      - annotation : ann               (unicode)       [create,query,edit]
          Annotate the control with an extra string value.
    
      - backgroundColor : bgc          (float, float, float) [create,query,edit]
          The background color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0. When setting backgroundColor, the background is automatically enabled, unless
          enableBackground is also specified with a false value.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Add a documentation flag to the control.  The documentation flag has a directory structure like hierarchy. Eg. -dt
          render/multiLister/createNode/material
    
      - dragCallback : dgc             (script)        [create,edit]
          Adds a callback that is called when the middle mouse button is pressed.  The MEL version of the callback is of the form:
          global proc string[] callbackName(string $dragControl, int $x, int $y, int $mods) The proc returns a string array that
          is transferred to the drop site. By convention the first string in the array describes the user settable message type.
          Controls that are application defined drag sources may ignore the callback. $mods allows testing for the key modifiers
          CTL and SHIFT. Possible values are 0 == No modifiers, 1 == SHIFT, 2 == CTL, 3 == CTL + SHIFT. In Python, it is similar,
          but there are two ways to specify the callback.  The recommended way is to pass a Python function object as the
          argument.  In that case, the Python callback should have the form: def callbackName( dragControl, x, y, modifiers ): The
          values of these arguments are the same as those for the MEL version above. The other way to specify the callback in
          Python is to specify a string to be executed.  In that case, the string will have the values substituted into it via the
          standard Python format operator.  The format values are passed in a dictionary with the keys dragControl, x, y,
          modifiers.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(x)d %(y)d %(modifiers)d'
    
      - dropCallback : dpc             (script)        [create,edit]
          Adds a callback that is called when a drag and drop operation is released above the drop site.  The MEL version of the
          callback is of the form: global proc callbackName(string $dragControl, string $dropControl, string $msgs[], int $x, int
          $y, int $type) The proc receives a string array that is transferred from the drag source. The first string in the msgs
          array describes the user defined message type. Controls that are application defined drop sites may ignore the callback.
          $type can have values of 1 == Move, 2 == Copy, 3 == Link. In Python, it is similar, but there are two ways to specify
          the callback.  The recommended way is to pass a Python function object as the argument.  In that case, the Python
          callback should have the form: def pythonDropTest( dragControl, dropControl, messages, x, y, dragType ): The values of
          these arguments are the same as those for the MEL version above. The other way to specify the callback in Python is to
          specify a string to be executed.  In that case, the string will have the values substituted into it via the standard
          Python format operator.  The format values are passed in a dictionary with the keys dragControl, dropControl, messages,
          x, y, type.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(dropControl)s %(messages)r %(x)d %(y)d %(type)d'
    
      - enable : en                    (bool)          [create,query,edit]
          The enable state of the control.  By default, this flag is set to true and the control is enabled.  Specify false and
          the control will appear dimmed or greyed-out indicating it is disabled.
    
      - enableBackground : ebg         (bool)          [create,query,edit]
          Enables the background color of the control.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - fullPathName : fpn             (bool)          [query]
          Return the full path name of the widget, which includes all the parents
    
      - height : h                     (int)           [create,query,edit]
          The height of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
    
      - highlightColor : hlc           (float, float, float) [create,query,edit]
          The highlight color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0.
    
      - isObscured : io                (bool)          [query]
          Return whether the control can actually be seen by the user. The control will be obscured if its state is invisible, if
          it is blocked (entirely or partially) by some other control, if it or a parent layout is unmanaged, or if the control's
          window is invisible or iconified.
    
      - label : l                      (unicode)       []
    
      - light : lt                     (PyNode)        [create]
          The light that is to be made exclusive/non-exclusive.
    
      - manage : m                     (bool)          [create,query,edit]
          Manage state of the control.  An unmanaged control is not visible, nor does it take up any screen real estate.  All
          controls are created managed by default.
    
      - noBackground : nbg             (bool)          [create,edit]
          Clear/reset the control's background. Passing true means the background should not be drawn at all, false means the
          background should be drawn.  The state of this flag is inherited by children of this control.
    
      - numberOfPopupMenus : npm       (bool)          [query]
          Return the number of popup menus attached to this control.
    
      - parent : p                     (unicode)       [create,query]
          The parent layout for this control.
    
      - popupMenuArray : pma           (bool)          [query]
          Return the names of all the popup menus attached to this control.
    
      - preventOverride : po           (bool)          [create,query,edit]
          If true, this flag disallows overriding the control's attribute via the control's right mouse button menu.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - visible : vis                  (bool)          [create,query,edit]
          The visible state of the control.  A control is created visible by default.  Note that a control's actual appearance is
          also dependent on the visible state of its parent layout(s).
    
      - visibleChangeCommand : vcc     (script)        [create,query,edit]
          Command that gets executed when visible state of the control changes.
    
      - width : w                      (int)           [create,query,edit]
          The width of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.exclusiveLightCheckBox`
    """

    pass


def getRenderTasks(*args, **kwargs):
    """
    Command to return render tasks to render an image source.  Image source can depend on upstream image sources that result
    from renderings of 3D scene, or 2D renderings (e.g. render targets). This command obtains the graph of image source
    render dependencies, and creates render tasks according to these dependencies.  A render task has context, which can be
    camera, render layer, and resolution, or other, renderer-specific context.  Because of image source overrides, the
    render task context depends on the path through the render dependency graph, with the most upstream override for a
    context item applied.  As there can be multiple paths through a render dependency graph to a render dependency, there
    can be multiple render tasks for a given render dependency.
    
    Flags:
      - camera : c                     (unicode)       [create]
          Camera node to use in the render context for the image source render task.
    
      - renderLayer : rl               (unicode)       [create]
          Render layer to use in the render context for the image source render task.                                Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.getRenderTasks`
    """

    pass


def spotLight(*args, **kwargs):
    """
    TlightCmd is the base class for other light commands. TnonAmbientLightCmd is a class that looks like a command but is
    not.  It is a base class for the extended/nonExtended lights. This is abstract and not a real command. It is inherited
    by several lights: TpointLight, TdirectionalLight, TspotLight etc. The spotLight command is used to edit the parameters
    of existing spotLights, or to create new ones. The default behaviour is to create a new spotlight.
    
    Maya Bug Fix:
      - name flag was ignored
    
    Flags:
      - barnDoors : bd                 (bool)          [create,query,edit]
          Are the barn doors enabled?
    
      - bottomBarnDoorAngle : bbd      (float)         [create,query,edit]
          Angle of the bottom of the barn door.
    
      - coneAngle : ca                 (float)         [create,query,edit]
          angle of the spotLight
    
      - decayRate : d                  (int)           [create]
          Decay rate of the light (0-no decay, 1-slow, 2-realistic, 3-fast)
    
      - discRadius : drs               (float)         [create,query]
          Radius of shadow disc.
    
      - dropOff : do                   (float)         [create,query,edit]
          dropOff of the spotLight
    
      - exclusive : exc                (bool)          [create,query]
          True if the light is exclusively assigned
    
      - intensity : i                  (float)         [create,query]
          Intensity of the light
    
      - leftBarnDoorAngle : lbd        (float)         [create,query,edit]
          Angle of the left of the barn door.
    
      - name : n                       (unicode)       [create,query]
          Name of the light
    
      - penumbra : p                   (float)         [create,query,edit]
          specify penumbra region
    
      - position : pos                 (float, float, float) [create,query]
          Position of the light
    
      - rgb : rgb                      (float, float, float) [create,query]
          RGB colour of the light
    
      - rightBarnDoorAngle : rbd       (float)         [create,query,edit]
          Angle of the right of the barn door.
    
      - rotation : rot                 (float, float, float) [create,query]
          Rotation of the light for orientation, where applicable
    
      - shadowColor : sc               (float, float, float) [create,query]
          Color of the light's shadow
    
      - shadowDither : sd              (float)         [create,query]
          Shadow dithering value.
    
      - shadowSamples : sh             (int)           [create,query]
          Numbr of shadow samples to use
    
      - softShadow : ss                (bool)          [create,query]
          True if soft shadowing is to be enabled
    
      - topBarnDoorAngle : tbd         (float)         [create,query,edit]
          Angle of the top of the barn door.
    
      - useRayTraceShadows : rs        (bool)          [create,query]
          True if ray trace shadows are to be used                  Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.spotLight`
    """

    pass


def perCameraVisibility(*args, **kwargs):
    """
    The perCameraVisibility command creates, queries and removes visibility relationships between DAG objects and cameras.
    These relationships are applied in any viewport that uses the cameras involved. (They are not used e.g. in rendering.)
    Objects can be set to be exclusive to a camera (meaning they will only be displayed in viewports using that camera; they
    will be hidden in other viewports) or hidden from a camera (meaning they will be not visible in any viewport using the
    camera).
    
    Flags:
      - camera : c                     (PyNode)        [create,query]
          Specify the camera for the operation.
    
      - exclusive : ex                 (bool)          [create,query]
          Set objects as being exclusive to the given camera.
    
      - hide : hi                      (bool)          [create,query]
          Set objects as being hidden from the given camera.
    
      - remove : rm                    (bool)          [create]
          Used with exclusive or hide, removes the objects instead of adding them.
    
      - removeAll : ra                 (bool)          [create]
          Remove all exclusivity/hidden objects for all cameras.
    
      - removeCamera : rc              (bool)          [create]
          Remove all exclusivity/hidden objects for the given camera.                                Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.perCameraVisibility`
    """

    pass


def viewHeadOn(*args, **kwargs):
    """
    The viewHeadOn command positions the specified camera so it is looking downthe normal of the live object, and fitted to
    the live object. If the live object is a surface, an arbitrary normal is chosen.
    
    
    Derived from mel command `maya.cmds.viewHeadOn`
    """

    pass


def renderGlobalsNode(*args, **kwargs):
    """
    The renderGlobalsNode creates a render globals node and registers it with the model. The createNode command will not
    register nodes of this type correctly.
    
    Flags:
      - name : n                       (unicode)       []
    
      - parent : p                     (unicode)       []
    
      - renderQuality : rq             (unicode)       [create]
          Set the quality to be the renderQuality node with the given name.
    
      - renderResolution : rr          (unicode)       [create]
          Set the resolution to be the resolution node with the given name.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - shared : s                     (bool)          []
    
      - skipSelect : ss                (bool)          []
    
    
    Derived from mel command `maya.cmds.renderGlobalsNode`
    """

    pass


def renderPassRegistry(*args, **kwargs):
    """
    query information related with render passes.
    
    Flags:
      - channels : ch                  (int)           [create]
          Specify the number of channels for query.
    
      - isPassSupported : ips          (bool)          [create]
          Return whether the pass is supported by the renderer This flag must be specified by the flag -passID firstly. The
          renderer whose default value is the current renderer is specified by the flag renderer.
    
      - passID : pi                    (unicode)       [create]
          Specify the render pass ID for query.
    
      - passName : pn                  (bool)          [create]
          Get the pass name for the passID. This flag must be specified by the flag -passID firstly.
    
      - renderer : r                   (unicode)       [create]
          Specify a renderer when using this command. By default the current renderer is specified.
    
      - supportedChannelCounts : scc   (bool)          [create]
          List channel counts supported by the renderer(specified by the flag -renderer) and the specified pass ID. This flag must
          be specified by the flag -passID firstly.
    
      - supportedDataTypes : sdt       (bool)          [create]
          List frame buffer types supported by the renderer(specified by the flag -renderer), the specified passID and channels.
          This flag must be specified by the flag -passID and -channels firstly.
    
      - supportedPassSemantics : ps    (bool)          [create]
          List pass semantics supported by the specified passID. This flag must be specified by the flag -passId firstly.
    
      - supportedRenderPassNames : spn (bool)          [create]
          List render pass names supported by the renderer(specified by the flag -renderer).
    
      - supportedRenderPasses : srp    (bool)          [create]
          List render passes supported by the renderer(specified by the flag -renderer).                             Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.renderPassRegistry`
    """

    pass


def setRenderPassType(*args, **kwargs):
    """
    This command will set the passID of a renderPass node and create the custom attributes specified by the corresponding
    render pass definition.  If the render pass node already has a passID assigned to it, attributes that are no longer
    required become hidden, and new attributes are unhidden and/or created as needed.  This allows passIDs to be changed
    back and forth without losing attribute data.  It also allows common attributes to be transported from one render pass
    type to another.
    
    Flags:
      - defaultDataType : d            (bool)          [create]
          If set, the render pass will use its default data type.
    
      - numChannels : n                (int)           [create]
          Specify the number of channels to use in the render pass. Note that this flag is only valid if there is an
          implementation supporting the requested number of channels.
    
      - type : t                       (unicode)       [create]
          Specify the pass type to assign to the pass node(s).                               Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.setRenderPassType`
    """

    pass


def editRenderLayerGlobals(*args, **kwargs):
    """
    Edit the parameter values common to all render layers.  Some of these paremeters, eg. baseId and mergeType, are stored
    as preferences and some, eg. currentRenderLayer, are stored in the file.
    
    Flags:
      - baseId : bi                    (int)           [create,query]
          Set base layer ID.  This is the number at which new layers start searching for a unique ID.
    
      - currentRenderLayer : crl       (PyNode)        [create,query]
          Set current render layer. This will will update the renderLayerManger and all DAG objects to identify them as members of
          the render layer. This flag may also be used in conjunction with useCurrentto automatically add new DAG objects to the
          active layer. The isCurrentRenderLayerChangingcondition can be used to determine when the current layer is being changed
          and adjustments are being applied to the scene.
    
      - enableAutoAdjustments : eaa    (bool)          [create,query]
          Set whether or not to enable automatic creation of adjustments when certain attributes (ie. surface render stats,
          shading group assignment, or render settings) are changed.
    
      - mergeType : mt                 (int)           [create,query]
          Set file import merge type.  Valid values are 0, none, 1, by number, and 2, by name.
    
      - useCurrent : uc                (bool)          [create,query]
          Set whether or not to enable usage of the current render layer as the destination for all new nodes.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.editRenderLayerGlobals`
    """

    pass


def doBlur(*args, **kwargs):
    """
    The doBlur command  will invoke the blur2d, which is a Maya stand-alone application to do 2.5 motion blur given the
    color image and the motion vector file.  For a given input colorFile name, e.g. xxx.iff, the output blurred image will
    be xxx_blur.iffin the same directory as the input colorFile.  There is currently no control over the name of the output
    blurred image.
    
    Flags:
      - colorFile : c                  (unicode)       [create]
          Name of the input color image to be blurred.
    
      - length : l                     (float)         [create]
          Scale applied on the motion vector. Ranges from 0 to infinity.
    
      - memCapSize : o                 (float)         []
    
      - sharpness : s                  (float)         [create]
          Determines  the shape of the blur filter. The higher the value, the narrower the filter, the sharper the blur. The lower
          the value, the wider the filter, the more spread out the blur. Ranges from 0 to infinity.
    
      - smooth : m                     (float)         [create]
          Filter size to smooth the blurred image. The higher the value, the more anti-aliased the alpha channel. Ranges from 1.0
          to 5.0.
    
      - smoothColor : r                (bool)          [create]
          Whether to smooth the color or not.
    
      - vectorFile : v                 (unicode)       [create]
          Name of the input motion vector file.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.doBlur`
    """

    pass


def spotLightPreviewPort(*args, **kwargs):
    """
    This command creates a 3dPort that displays an image representing the illumination provided by the spotLight. It is a
    picture of a plane being illuminated by a light. The optional argument is the name of the 3dPort.
    
    Flags:
      - annotation : ann               (unicode)       [create,query,edit]
          Annotate the control with an extra string value.
    
      - backgroundColor : bgc          (float, float, float) [create,query,edit]
          The background color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0. When setting backgroundColor, the background is automatically enabled, unless
          enableBackground is also specified with a false value.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Add a documentation flag to the control.  The documentation flag has a directory structure like hierarchy. Eg. -dt
          render/multiLister/createNode/material
    
      - dragCallback : dgc             (script)        [create,edit]
          Adds a callback that is called when the middle mouse button is pressed.  The MEL version of the callback is of the form:
          global proc string[] callbackName(string $dragControl, int $x, int $y, int $mods) The proc returns a string array that
          is transferred to the drop site. By convention the first string in the array describes the user settable message type.
          Controls that are application defined drag sources may ignore the callback. $mods allows testing for the key modifiers
          CTL and SHIFT. Possible values are 0 == No modifiers, 1 == SHIFT, 2 == CTL, 3 == CTL + SHIFT. In Python, it is similar,
          but there are two ways to specify the callback.  The recommended way is to pass a Python function object as the
          argument.  In that case, the Python callback should have the form: def callbackName( dragControl, x, y, modifiers ): The
          values of these arguments are the same as those for the MEL version above. The other way to specify the callback in
          Python is to specify a string to be executed.  In that case, the string will have the values substituted into it via the
          standard Python format operator.  The format values are passed in a dictionary with the keys dragControl, x, y,
          modifiers.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(x)d %(y)d %(modifiers)d'
    
      - dropCallback : dpc             (script)        [create,edit]
          Adds a callback that is called when a drag and drop operation is released above the drop site.  The MEL version of the
          callback is of the form: global proc callbackName(string $dragControl, string $dropControl, string $msgs[], int $x, int
          $y, int $type) The proc receives a string array that is transferred from the drag source. The first string in the msgs
          array describes the user defined message type. Controls that are application defined drop sites may ignore the callback.
          $type can have values of 1 == Move, 2 == Copy, 3 == Link. In Python, it is similar, but there are two ways to specify
          the callback.  The recommended way is to pass a Python function object as the argument.  In that case, the Python
          callback should have the form: def pythonDropTest( dragControl, dropControl, messages, x, y, dragType ): The values of
          these arguments are the same as those for the MEL version above. The other way to specify the callback in Python is to
          specify a string to be executed.  In that case, the string will have the values substituted into it via the standard
          Python format operator.  The format values are passed in a dictionary with the keys dragControl, dropControl, messages,
          x, y, type.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(dropControl)s %(messages)r %(x)d %(y)d %(type)d'
    
      - enable : en                    (bool)          [create,query,edit]
          The enable state of the control.  By default, this flag is set to true and the control is enabled.  Specify false and
          the control will appear dimmed or greyed-out indicating it is disabled.
    
      - enableBackground : ebg         (bool)          [create,query,edit]
          Enables the background color of the control.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - fullPathName : fpn             (bool)          [query]
          Return the full path name of the widget, which includes all the parents
    
      - height : h                     (int)           [create,query,edit]
          The height of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
    
      - highlightColor : hlc           (float, float, float) [create,query,edit]
          The highlight color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0.
    
      - isObscured : io                (bool)          [query]
          Return whether the control can actually be seen by the user. The control will be obscured if its state is invisible, if
          it is blocked (entirely or partially) by some other control, if it or a parent layout is unmanaged, or if the control's
          window is invisible or iconified.
    
      - manage : m                     (bool)          [create,query,edit]
          Manage state of the control.  An unmanaged control is not visible, nor does it take up any screen real estate.  All
          controls are created managed by default.
    
      - noBackground : nbg             (bool)          [create,edit]
          Clear/reset the control's background. Passing true means the background should not be drawn at all, false means the
          background should be drawn.  The state of this flag is inherited by children of this control.
    
      - numberOfPopupMenus : npm       (bool)          [query]
          Return the number of popup menus attached to this control.
    
      - parent : p                     (unicode)       [create,query]
          The parent layout for this control.
    
      - popupMenuArray : pma           (bool)          [query]
          Return the names of all the popup menus attached to this control.
    
      - preventOverride : po           (bool)          [create,query,edit]
          If true, this flag disallows overriding the control's attribute via the control's right mouse button menu.
    
      - spotLight : sl                 (PyNode)        [create]
          Name of the spotLight.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - visible : vis                  (bool)          [create,query,edit]
          The visible state of the control.  A control is created visible by default.  Note that a control's actual appearance is
          also dependent on the visible state of its parent layout(s).
    
      - visibleChangeCommand : vcc     (script)        [create,query,edit]
          Command that gets executed when visible state of the control changes.
    
      - width : w                      (int)           [create,query,edit]
          The width of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
    
      - widthHeight : wh               (int, int)      [create]
          The width and height of the port.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.spotLightPreviewPort`
    """

    pass


def surfaceShaderList(*args, **kwargs):
    """
    Add/Remove a relationship between an object and the current shading group. In query mode, return type is based on
    queried flag.
    
    Flags:
      - add : add                      (PyNode)        [create]
          add object(s) to shader group list.
    
      - remove : rm                    (PyNode)        [create]
          remove object(s) to shader group list.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.surfaceShaderList`
    """

    pass


def camera(*args, **kwargs):
    """
    Create, edit, or query a camera with the specified properties. The resulting camera can be repositioned using the
    viewPlace command. Many of the camera settings only affect the resulting rendered image. E.g. the F/Stop, shutter speed,
    the film related options, etc. Scaling the camera icon does not change any camera properties.
    
    Flags:
      - aspectRatio : ar               (float)         [create,query,edit]
          The ratio of the film back width to the film back height.
    
      - cameraScale : cs               (float)         [create,query,edit]
          Scale the camera.
    
      - centerOfInterest : coi         (float)         [create,query,edit]
          Set the linear distance from the camera's eye point to the center of interest.
    
      - clippingPlanes : cp            (bool)          [create,query,edit]
          Activate manual clipping planes.
    
      - depthOfField : dof             (bool)          [create,query,edit]
          Determines whether a depth of field calculation is performed to give varying focus depending on the distance of the
          objects.
    
      - displayFieldChart : dfc        (bool)          [create,query,edit]
          Activate display of the video field chart when looking through the camera.
    
      - displayFilmGate : dfg          (bool)          [create,query,edit]
          Activate display of the film gate icons when looking through the camera.
    
      - displayFilmOrigin : dfo        (bool)          [create,query,edit]
          Activate the display of the film origin guide when looking through the camera.
    
      - displayFilmPivot : dfp         (bool)          [create,query,edit]
          Activate display of the film pivot guide when looking through the camera.
    
      - displayGateMask : dgm          (bool)          [create,query,edit]
          Display the gate mask, file or resolution, as a shaded area to the edge of the viewport.
    
      - displayResolution : dr         (bool)          [create,query,edit]
          Activate display of the current rendering resolution (as defined in the render globals) when looking through the camera.
    
      - displaySafeAction : dsa        (bool)          [create,query,edit]
          Activate display of the video Safe Action guide when looking through the camera.
    
      - displaySafeTitle : dst         (bool)          [create,query,edit]
          Activate display of the video Safe Title guide when looking through the camera.
    
      - fStop : fs                     (float)         [create,query,edit]
          A real lens normally contains a diaphragm or other stop which blocks some of the light that would otherwise pass through
          it. This stop is usually approximately round, and its diameter as seen from the front of the lens is called the lens
          diameter. The lens diameter is often described by its relation to the focal length of the lens. A lens whose diameter is
          one-eighth its local length is said to have an F-stop of 8. This is an optical property of the lens.
    
      - farClipPlane : fcp             (float)         [create,query,edit]
          Specify the distance to the far clipping plane.
    
      - farFocusDistance : ffd         (float)         [create,query,edit]
          Linear distance to the far focus plane.
    
      - filmFit : ff                   (unicode)       [create,query,edit]
          This describes how the digital image (in pixels) relates to the film back. Since the film back is defined in terms of
          real numbers with some arbitrary film aspect, and the digital image is defined in integer pixels with an equally
          arbitrary (and different) resolution, relating the two can get complicated. There are 4 choices: horizontal In this case
          the digital image is made to fit the film back exactly in the horizontal direction. This then gives each pixel a
          horizontal size = (film back width) / (horizontal resolution). The pixel height is then = (pixel width) / (pixel aspect
          ratio). Now that the pixel has a size, resolution gives us a complete image. That image will match the film back exactly
          in width. It will almost never match in height, either being too tall or too short. By playing with the numbers you can
          get it pretty close though.verticalThis is the same idea as horizontal fit, only applied vertically. Thus the digital
          image will match the film back exactly in height, but miss in width.fillThis is a convenience item. The system
          calculates both horizontal and vertical fits and then applies the one that makes the digital image larger than the film
          back.overscanOverscanning the film gate in the camera view allows us to choreograph action outside of the frustum from
          within the camera view without having to resort to a dolly or zoom. This feature is also essential for animating image
          planes.
    
      - filmFitOffset : ffo            (float)         [create,query,edit]
          Since we know from the above that the digital image may not match the film back exactly, we now have the question of how
          to position one relative to the other. Thus fit offset. Normally the centers are aligned. Fit offset lets you move the
          smaller image within the larger one. Specify the distance for film offset (inches).
    
      - filmRollOrder : fro            (unicode)       [create,query,edit]
          Specifies how the roll is applied with respect to the pivot value. Rotate-TranslateThe film back is first rotated then
          translated by the pivot point value.Translate-RotateThe film back is first translated then rotated by the film roll
          value.
    
      - filmRollValue : frv            (float)         [create,query,edit]
          This specifies that amount of rotation around the film back. The roll value is specified in degrees. The rotation occurs
          around the specified pivot point. This value is used to compute a film roll matrix, which is a component of the post-
          projection matrix.
    
      - filmTranslateH : fth           (float)         [create,query,edit]
          The horizontal film translation. Values are normalized to the viewing area.
    
      - filmTranslateV : ftv           (float)         [create,query,edit]
          The vertical film translation. Values are normalized to the viewing area.
    
      - focalLength : fl               (float)         [create,query,edit]
          This is the distance along the lens axis between the lens and the film plane when focal distanceis infinitely large.
          This is an optical property of the lens. This double precision parameter is always specified in millimeters.
    
      - focusDistance : fd             (float)         [create,query,edit]
          Set the focus at a certain distance in front of the camera.
    
      - homeCommand : hc               (unicode)       [create,query,edit]
          Specify the command to execute when viewSet -homeis applied to this camera. All occurances of %camerawill be replaced
          with the cameras name before viewSet runs the command.
    
      - horizontalFieldOfView : hfv    (float)         [create,query,edit]
          This is the film back width as seen by the lens when focused at infinity (ie., focal length away) measured as an angle.
          Note that it has nothing to do with pixels or the digital image or any aspects. Angle of view is a derived field, that
          is, it is not used internally by Alias and can be completely determined from other information. It is included as a
          convenience for the user. Its derivation is aov = 2 \* atan( fbw / (2 \* f) ) where aovis the angle of view, fbwis the
          film back width and fis the focal length.
    
      - horizontalFilmAperture : hfa   (float)         [create,query,edit]
          The horizontal width of the camera's film plane. The camera's film is located on the film plane. The extent of the film
          which will be exposed to an image of the scene in front of the lens is limited to a rectangular area described by the
          film back. This double precision parameter is always specified in inches.
    
      - horizontalFilmOffset : hfo     (float)         [create,query,edit]
          Horizontal offset from the center of the film back. Normally the film back will be centered on the lens axis. However,
          this need not be so. Film offset is the displacement of the center of the film back from the lens axis, also measured in
          inches. Note that offsetting the film back will distort the image, but will not alter the focus. This double precision
          parameter is always specified in inches.
    
      - horizontalPan : hpn            (float)         [create,query,edit]
          Horizontal 2D camera pan (inches)
    
      - horizontalRollPivot : hrp      (float)         [create,query,edit]
          The horizontal pivot point from the center of the film back. The pivot point is used during rotation of the film back.
          The pivot is the point where the rotation occurs around. This double precision parameter corresponds to the normalized
          viewport. This value is a part of the post projection matrix.
    
      - horizontalShake : hs           (float)         [create,query,edit]
          Another horizontal offset from the center of the film back, which can be used and stored on the camera in addition to
          the horizonal film offset attribute.  This allows for film-based camera shake internal to the camera.  This works in
          exactly the same units and coordinates that the film offset attribute does. The effect of this attribute is toggled by
          the shake enabled attribute.
    
      - journalCommand : jc            (bool)          [create,query,edit]
          Journal interactive camera commands. Commands can be undone when a camera is journaled.
    
      - lensSqueezeRatio : lsr         (float)         [create,query,edit]
          This is presently just an information field in the camera editor is meant to convey the horizontal distortion of the
          anamorphic lens normally used with some film formats. If it were used, it would do something like pixel aspect. Remember
          however that lens distortion (intentional or not) is slightly different than the output hardware's quantization. The
          fact that a netdistortion parameter could be used for both may or may not confuse the issue.
    
      - lockTransform : lt             (bool)          [create,query,edit]
          Lock the camera. When a camera is locked, its transformation information, that is, its Translate and Rotate properties
          cannot be adjusted, and the center of interest point cannot be moved. For orthographic cameras, Orthographic Width is
          also locked. For camera groups, Aim and Up locator's translate is also locked. For stereo cameras, the root camera is
          locked.
    
      - motionBlur : mb                (bool)          [create,query,edit]
          Determines whether the camera's image is motion blured (as opposed to an object's image). For example, if you want to
          blur the camera movement when you are performing a flyby.
    
      - name : n                       (unicode)       [query,edit]
    
      - nearClipPlane : ncp            (float)         [create,query,edit]
          Specify the distance to the NEAR clipping plane.
    
      - nearFocusDistance : nfd        (float)         [create,query,edit]
          Linear distance to the near focus plane.
    
      - orthographic : o               (bool)          [create,query,edit]
          Activate the orthographic camera.
    
      - orthographicWidth : ow         (float)         [create,query,edit]
          Set the orthographic projection width.
    
      - overscan : ovr                 (float)         [create,query,edit]
          Set the percent of overscan.
    
      - panZoomEnabled : pze           (bool)          [create,query,edit]
          Toggle camera 2D pan and zoom
    
      - position : p                   (float, float, float) [create,query,edit]
          Three linear values can be specified to translate the camera.
    
      - postScale : pts                (float)         [create,query,edit]
          The post-scale value.  This value multiplied against the computed projection matrix. It is applied after the the film
          roll.
    
      - preScale : prs                 (float)         [create,query,edit]
          The pre-scale value. The value is multiplied against the computed projection matrix. It is applied before the film roll.
    
      - renderPanZoom : rpz            (bool)          [create,query,edit]
          Toggle camera 2D pan and zoom in render
    
      - rotation : rot                 (float, float, float) [create,query,edit]
          Three angular values can be specified to rotate the camera.
    
      - shakeEnabled : se              (bool)          [create,query,edit]
          Toggles the effect of the horizontal and vertical shake attributes.
    
      - shakeOverscan : so             (float)         [create,query,edit]
          Controls the amount of overscan in the output rendered image. For use when adding film-based camera shake.  Acts as a
          multiplier to the film aperture on the camera.
    
      - shakeOverscanEnabled : soe     (bool)          [create,query,edit]
          Toggles the effect of the shake overscan attribute.
    
      - shutterAngle : sa              (float)         [create,query,edit]
          Specify the shutter angle (degrees).
    
      - startupCamera : sc             (bool)          [create,query,edit]
          A startup camera is marked undeletable and implicit. This flag can be used to set or query the startup state of a
          camera. There must always be at least one startup camera.
    
      - stereoHorizontalImageTranslate : hit (float)         [create,query,edit]
          A film-back offset for use in stereo camera rigs.
    
      - stereoHorizontalImageTranslateEnabled : she (bool)          [create,query,edit]
          Toggles the effect of the stereo HIT attribute.
    
      - verticalFieldOfView : vfv      (float)         [create,query,edit]
          Set the vertical field of view.
    
      - verticalFilmAperture : vfa     (float)         [create,query,edit]
          The vertical height of the camera's film plane. This double precision parameter is always specified in inches.
    
      - verticalFilmOffset : vfo       (float)         [create,query,edit]
          Vertical offset from the center of the film back. This double precision parameter is always specified in inches.
    
      - verticalLock : vl              (bool)          [create,query,edit]
          Lock the size of the vertical film aperture.
    
      - verticalPan : vpn              (float)         [create,query,edit]
          Vertical 2D camera pan (inches)
    
      - verticalRollPivot : vrp        (float)         [create,query,edit]
          Vertical pivot point used for rotating the film back. This double precision parameter corresponds to the normalized
          viewport. This value is used to compute the film roll matrix, which is a component of the post projection matrix.
    
      - verticalShake : vs             (float)         [create,query,edit]
          Vertical offset from the center of the film back.  See horizontal shake attribute description.  This is toggled by the
          shake enabled attribute.
    
      - worldCenterOfInterest : wci    (float, float, float) [create,query,edit]
          Camera world center of interest point.
    
      - worldUp : wup                  (float, float, float) [create,query,edit]
          Camera world up vector.
    
      - zoom : zom                     (float)         [create,query,edit]
          The percent over the film viewable frustum to display                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.camera`
    """

    pass


def dolly(*args, **kwargs):
    """
    The dolly command moves a camera along the viewing direction in the world space. The viewing-direction and up-direction
    of the camera are not altered. There are two modes of operation: Relative mode: for a perspective camera, the camera is
    moved along its viewing direction, and the distance of travel is computed with respect to the current position of the
    camera in the world space. In relative mode, when the camera is moved, its COI is moved along with it, and is kept at
    the same distance, in front of the camera, as before applying the dolly operation. For orthographic camera, the viewing
    width of the camera is changed by scaling its ortho width by the new value specified on the command line. Absolute mode:
    for a perspective camera, the camera is moved along its viewing direction, to the distance that is computed with respect
    to the current position of the world center of interest (COI) of the camera. In the absolute mode, when the camera is
    moved, the COI of the camera is not moved with the camera, but it is fixed at its current location in space. For
    orthographic camera, the viewing width of the camera is changed by replacing its ortho width with the new value
    specified on the command line. This command may be applied to more than one cameras; objects that are not cameras are
    ignored. When no camera name supplied on the command line, this command is applied to all currently active cameras. The
    dolly command can be applied to either a perspective or an orthographic camera.
    
    Flags:
      - absolute : abs                 (bool)          [create]
          This flag modifies the behavior of the distance and orthoScale flags. When used in conjunction with the distance flag,
          the distance argument specifies how far the camera's eye point should be set from the camera's center of interest. When
          used with the orthoScale flag, the orthoScale argument specifies the camera's new ortho width.
    
      - distance : d                   (float)         [create]
          Unit distance to dolly a perspective camera.
    
      - dollyTowardsCenter : dtc       (bool)          [create]
          This flag controls whether the dolly is performed towards the center of the view (if true), or towards the point where
          the user clicks (if false). By default, dollyTowardsCenter is on.
    
      - orthoScale : os                (float)         [create]
          Scale to change the ortho width of an orthographic camera.
    
      - relative : rel                 (bool)          [create]
          This flag modifies the behavior of the distance and orthoScale flags. When used in conjunction with the distance flag,
          the camera eye and center of interest are both moved by the amount specified by the distance flag's argument. When used
          with the orthoScale flag, the orthoScale argument is used multiply the camera's ortho width.By default the relative flag
          is always on.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dolly`
    """

    pass


def directionalLight(*args, **kwargs):
    """
    The directionalLight command is used to edit the parameters of existing directionalLights, or to create new ones. The
    default behaviour is to create a new directionallight.
    
    Maya Bug Fix:
      - name flag was ignored
    
    Flags:
      - decayRate : d                  (int)           [create,query,edit]
          decay rate of the light (0-no decay, 1-slow, 2-realistic, 3-fast)
    
      - discRadius : drs               (float)         [create,query,edit]
          radius of the disc around the light
    
      - exclusive : exc                (bool)          [query,edit]
    
      - intensity : i                  (float)         [create,query,edit]
          intensity of the light (expressed as a percentage)
    
      - name : n                       (unicode)       [create,query,edit]
          specify the name of the light
    
      - position : pos                 (float, float, float) [query,edit]
    
      - rgb : rgb                      (float, float, float) [create,query,edit]
          color of the light (0-1)
    
      - rotation : rot                 (float, float, float) [query,edit]
    
      - shadowColor : sc               (float, float, float) [create,query,edit]
          the shadow color
    
      - shadowDither : sd              (float)         [create,query,edit]
          dither the shadow
    
      - shadowSamples : sh             (int)           [create,query,edit]
          number of shadow samples.
    
      - softShadow : ss                (bool)          [create,query,edit]
          soft shadow
    
      - useRayTraceShadows : rs        (bool)          [create,query,edit]
          ray trace shadows                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.directionalLight`
    """

    pass


def lightList(*args, **kwargs):
    """
    Add/Remove a relationship between an object and the current light. Soon to be replaced by the connect-attribute command.
    In query mode, return type is based on queried flag.
    
    Flags:
      - add : add                      (PyNode)        [create]
          add object(s) to light list.
    
      - remove : rm                    (PyNode)        [create]
          remove object(s) to light list.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.lightList`
    """

    pass


def makebot(*args, **kwargs):
    """
    The makebot command takes an image file and produces a block ordered texture (BOT) file, to be used for texture caching.
    If a relative pathname is specified for the input image file, project management rules apply.  If a relative pathname is
    specified for the output BOT file, project management rules apply and gets put into the sourceImages directory.
    
    Flags:
      - checkdepends : c               (bool)          [create]
          the BOT file should only be generated if it doesn't already exists, or if it is older than the source file
    
      - checkres : r                   (int)           [create]
          the BOT file should only be generated if its resolution (maximum of width and height) is larger than the minimum value
          specified by the argument
    
      - input : i                      (unicode)       [create]
          input image file
    
      - nooverwrite : nov              (bool)          [create]
          If -c and/or -r indicate that the BOT file should be generated but if already exists, then this flag will prevent the
          file from being overwritten
    
      - output : o                     (unicode)       [create]
          output BOT file
    
      - verbose : v                    (bool)          [create]
          Makebot will provide feedback if this flag is specified                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.makebot`
    """

    pass


def binMembership(*args, **kwargs):
    """
    Command to assign nodes to bins.
    
    Flags:
      - addToBin : add                 (unicode)       [create]
          Add the nodes in a node list to a bin.
    
      - exists : ex                    (unicode)       [create]
          Query if a node exists in a bin.  The exists flag can take only one node.
    
      - inheritBinsFromNodes : ibn     (PyNode)        [create]
          Let the node in the flag's argument inherit bins from nodes in the specified node list.  The node list is specified as
          the object of the command.
    
      - isValidBinName : ivn           (unicode)       [create]
          Query if the specified bin name is valid.  If so, return true. Otherwise, return false.
    
      - listBins : lb                  (bool)          [create,query]
          Query and return a list of bins a list of nodes belong to. If a bin contains any of the nodes in the selection list,
          then it should be included in the returned bin list.
    
      - makeExclusive : mke            (unicode)       [create]
          Make the specified nodes belong exclusively in the specified bin.
    
      - notifyChanged : nfc            (bool)          [create]
          This flag is used to notify that binMembership has been changed.
    
      - removeFromBin : rm             (unicode)       [create]
          Remove the nodes in a node list from a bin.                                Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.binMembership`
    """

    pass


def layeredShaderPort(*args, **kwargs):
    """
    This command creates a 3dPort that displays an image representing the layered shader node specified.
    
    Flags:
      - annotation : ann               (unicode)       [create,query,edit]
          Annotate the control with an extra string value.
    
      - backgroundColor : bgc          (float, float, float) [create,query,edit]
          The background color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0. When setting backgroundColor, the background is automatically enabled, unless
          enableBackground is also specified with a false value.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Add a documentation flag to the control.  The documentation flag has a directory structure like hierarchy. Eg. -dt
          render/multiLister/createNode/material
    
      - dragCallback : dgc             (script)        [create,edit]
          Adds a callback that is called when the middle mouse button is pressed.  The MEL version of the callback is of the form:
          global proc string[] callbackName(string $dragControl, int $x, int $y, int $mods) The proc returns a string array that
          is transferred to the drop site. By convention the first string in the array describes the user settable message type.
          Controls that are application defined drag sources may ignore the callback. $mods allows testing for the key modifiers
          CTL and SHIFT. Possible values are 0 == No modifiers, 1 == SHIFT, 2 == CTL, 3 == CTL + SHIFT. In Python, it is similar,
          but there are two ways to specify the callback.  The recommended way is to pass a Python function object as the
          argument.  In that case, the Python callback should have the form: def callbackName( dragControl, x, y, modifiers ): The
          values of these arguments are the same as those for the MEL version above. The other way to specify the callback in
          Python is to specify a string to be executed.  In that case, the string will have the values substituted into it via the
          standard Python format operator.  The format values are passed in a dictionary with the keys dragControl, x, y,
          modifiers.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(x)d %(y)d %(modifiers)d'
    
      - dropCallback : dpc             (script)        [create,edit]
          Adds a callback that is called when a drag and drop operation is released above the drop site.  The MEL version of the
          callback is of the form: global proc callbackName(string $dragControl, string $dropControl, string $msgs[], int $x, int
          $y, int $type) The proc receives a string array that is transferred from the drag source. The first string in the msgs
          array describes the user defined message type. Controls that are application defined drop sites may ignore the callback.
          $type can have values of 1 == Move, 2 == Copy, 3 == Link. In Python, it is similar, but there are two ways to specify
          the callback.  The recommended way is to pass a Python function object as the argument.  In that case, the Python
          callback should have the form: def pythonDropTest( dragControl, dropControl, messages, x, y, dragType ): The values of
          these arguments are the same as those for the MEL version above. The other way to specify the callback in Python is to
          specify a string to be executed.  In that case, the string will have the values substituted into it via the standard
          Python format operator.  The format values are passed in a dictionary with the keys dragControl, dropControl, messages,
          x, y, type.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(dropControl)s %(messages)r %(x)d %(y)d %(type)d'
    
      - enable : en                    (bool)          [create,query,edit]
          The enable state of the control.  By default, this flag is set to true and the control is enabled.  Specify false and
          the control will appear dimmed or greyed-out indicating it is disabled.
    
      - enableBackground : ebg         (bool)          [create,query,edit]
          Enables the background color of the control.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - fullPathName : fpn             (bool)          [query]
          Return the full path name of the widget, which includes all the parents
    
      - height : h                     (int)           [create,query,edit]
          The height of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
    
      - highlightColor : hlc           (float, float, float) [create,query,edit]
          The highlight color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0.
    
      - isObscured : io                (bool)          [query]
          Return whether the control can actually be seen by the user. The control will be obscured if its state is invisible, if
          it is blocked (entirely or partially) by some other control, if it or a parent layout is unmanaged, or if the control's
          window is invisible or iconified.
    
      - manage : m                     (bool)          [create,query,edit]
          Manage state of the control.  An unmanaged control is not visible, nor does it take up any screen real estate.  All
          controls are created managed by default.
    
      - noBackground : nbg             (bool)          [create,edit]
          Clear/reset the control's background. Passing true means the background should not be drawn at all, false means the
          background should be drawn.  The state of this flag is inherited by children of this control.
    
      - node : n                       (PyNode)        [create]
          Specifies the name of the newLayeredShader node this port will represent.
    
      - numberOfPopupMenus : npm       (bool)          [query]
          Return the number of popup menus attached to this control.
    
      - parent : p                     (unicode)       [create,query]
          The parent layout for this control.
    
      - popupMenuArray : pma           (bool)          [query]
          Return the names of all the popup menus attached to this control.
    
      - preventOverride : po           (bool)          [create,query,edit]
          If true, this flag disallows overriding the control's attribute via the control's right mouse button menu.
    
      - selectedColorControl : scc     (unicode)       [create]
          Specifies the name of the UI-control that represents the currently selected layer's color.
    
      - selectedTransparencyControl : stc (unicode)       [create]
          Specifies the name of the UI-control that represents the currently selected layer's transparency.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - visible : vis                  (bool)          [create,query,edit]
          The visible state of the control.  A control is created visible by default.  Note that a control's actual appearance is
          also dependent on the visible state of its parent layout(s).
    
      - visibleChangeCommand : vcc     (script)        [create,query,edit]
          Command that gets executed when visible state of the control changes.
    
      - width : w                      (int)           [create,query,edit]
          The width of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.layeredShaderPort`
    """

    pass


def renderThumbnailUpdate(*args, **kwargs):
    """
    Toggle the updating of object thumbnails. These are visible in tools like the Attribute Editor and Hypershade. All
    thumbnails everywhere will not update to reflect changes to the object until this command is used to toggle to true
    unless a specific thumbnail is forced to render using the -forceUpdate flag. In query mode, return type is based on
    queried flag.
    
    Flags:
      - forceUpdate : fu               (unicode)       [create]
          Force the thumbnail to update.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.renderThumbnailUpdate`
    """

    pass


def glRender(*args, **kwargs):
    """
    This command provides access to the Hardware Render Manager (HRM). There is one-and-only-one HRM in maya. The HRM
    controls the rendering performed in the hardware render buffer window. This command allows shell scripts, to modify the
    render state, and to initiate a render request. In query mode, return type is based on queried flag.
    
    Flags:
      - accumBufferPasses : abp        (int)           [query,edit]
          Set the number of accum buffer render passes.
    
      - alphaSource : alphaSource      (unicode)       [query,edit]
          Control the alpha source when writing image files. Valid values include: off, alpha, red, green, blue, luminance, clamp,
          invClamp.
    
      - antiAliasMethod : aam          (unicode)       [query,edit]
          Set the method used for anti-aliasing polygons: off, uniform, gaussian.
    
      - cameraIcons : ci               (bool)          [query,edit]
          Set display status of camera icons.
    
      - clearClr : cc                  (float, float, float) [query,edit]
          Set the viewport clear color (0 - 1).
    
      - collisionIcons : coi           (bool)          [query,edit]
          Set display status of collison model icons.
    
      - crossingEffect : ce            (bool)          [query,edit]
          Enable/disable image filtering with a convolution filter.
    
      - currentFrame : cf              (bool)          [query]
          Returns the current frame being rendered.
    
      - drawStyle : ds                 (unicode)       [query,edit]
          Set the object drawing style: boundingBox, points, wireframe, flatShaded, smoothShaded.
    
      - edgeSmoothness : es            (float)         [query,edit]
          Controls the amount of edge smoothing. A value of 0.0 gives no smoothing, 1.0 gives default smoothing, and any other
          value scales the amount of default smoothing. Must enable the accumulation buffer.
    
      - emitterIcons : ei              (bool)          [query,edit]
          Set display status of emitter icons.
    
      - fieldIcons : fii               (bool)          [query,edit]
          Set display status of field icons.
    
      - flipbookCallback : fc          (unicode)       [query,edit]
          Register a procedure to be called after the render sequence has completed. Used to build the flipbook pulldown menu. See
          the example section for more details about how to build this procedure.
    
      - frameEnd : fe                  (int)           [query,edit]
          Set the last frame to be rendered.
    
      - frameIncrement : fi            (int)           [query,edit]
          Set the frame increment during rendering.
    
      - frameStart : fs                (int)           [query,edit]
          Set the first frame to be rendered.
    
      - fullResolution : fr            (bool)          [query,edit]
          Enable/disable rendering to full image output resolution. Must set a valid image output resolution (-is).
    
      - grid : gr                      (bool)          [query,edit]
          Set display status of the grid.
    
      - imageDirectory : id            (unicode)       [query,edit]
          Set the directory for the image files.
    
      - imageName : imageName          (unicode)       [query,edit]
          Set the base name of the image files.
    
      - imageSize : imageSize          (int, int, float) [query,edit]
          Set the image output size. Takes width, height and aspect ratio. Pass 0,0,0 to use current port size. The image size
          must be equal to or greater then the viewport size. Large images will be tiled if full resolution rendering has been
          enabled (-fr/fullResolution).
    
      - lightIcons : li                (bool)          [query,edit]
          Set display status of light icons.
    
      - lightingMode : lm              (unicode)       [query,edit]
          Set the lighting mode used for rendering: all, selected, default.
    
      - lineSmoothing : ls             (bool)          [query,edit]
          Enable/disable anti-aliased lines.
    
      - offScreen : os                 (bool)          [query,edit]
          When set, this toggle allow HRM to use an offscreen buffer to render the view. This allows HRM to work when the
          application is iconified, or obscured
    
      - renderFrame : rf               (unicode)       [query,edit]
          Render the current frame. Requires the name of the view in which to render.
    
      - renderSequence : rs            (unicode)       [query,edit]
          Render the current frame sequence. Requires the name of the view in which to render.
    
      - sharpness : sh                 (float)         [query,edit]
          Control the sharpness level of the convolution filter.
    
      - shutterAngle : sa              (float)         [query,edit]
          Set the shutter angle used for motion blur (0 - 1). A value of 0.0 gives no blurring, 0.5 gives correct blurring, and
          1.0 gives continuous blurring. Must enable the accumulation buffer.
    
      - textureDisplay : txd           (bool)          [query,edit]
          Enable/disable texture map display.
    
      - transformIcons : ti            (bool)          [query,edit]
          Set display status of transform icons.
    
      - useAccumBuffer : uab           (bool)          [query,edit]
          Enable/disable the accumulation buffer.
    
      - viewport : vp                  (int, int, float) [query,edit]
          Set the viewport size. Pass in the width, height and aspect ratio. This size will be used for all test rendering and
          image output size unless full resolution (-fr) has been set and a valid image output size (-is) has been set.
    
      - writeDepthMap : wdm            (bool)          [query,edit]
          Enable/disable writing of zdepth to image files.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.glRender`
    """

    pass


def renderer(*args, **kwargs):
    """
    Command to register renders.  This command allows you to specify the UI name and procedure names for renderers. The
    command also allow you to query the UI name and the procedure names for the registered renders.              In query
    mode, return type is based on queried flag.
    
    Flags:
      - addGlobalsNode : agn           (unicode)       [create,query,edit]
          This flag allows the user to add a globals node the specified renderer uses.
    
      - addGlobalsTab : agt            (unicode, unicode, unicode) [create,edit]
          Add a tab associated with the specified renderer for the unified render globals window.
    
      - batchRenderOptionsProcedure : bro (unicode)       [create,query,edit]
          Set or query the batch render options procedure associated with the specified renderer.
    
      - batchRenderOptionsStringProcedure : bso (unicode)       [create,query,edit]
          Set or query the argument string that will be used with the command line utility 'Render' when doing a batch render
    
      - batchRenderProcedure : br      (unicode)       [create,query,edit]
          Set or query the batch render procedure associated with the specified renderer.
    
      - cancelBatchRenderProcedure : cbr (unicode)       [create,query,edit]
          Set or query returns the cancel batch render procedure associated with the specified renderer.
    
      - changeIprRegionProcedure : cir (unicode)       [create,query,edit]
          Set or query the change IPR region procedure associated with the specified renderer.
    
      - commandRenderProcedure : cr    (unicode)       [create,query,edit]
          Set or query the command line rendering procedure associated with the specified renderer.
    
      - exists : ex                    (bool)          [query,edit]
          The flag returns true if the specified renderer is registered in the registry, and it returns false otherwise.
    
      - globalsNodes : gn              (bool)          [create,query,edit]
          This flag returns the list of render globals nodes the specified renderer uses.
    
      - globalsTabCreateProcNames : gtc (bool)          [create,query,edit]
          This flag returns the names of procedures that are used to create the unified render globals window tabs that are
          associated with the specified renderer.
    
      - globalsTabLabels : gtl         (bool)          [create,query,edit]
          This flag returns the labels of unified render globals window tabs that are associated with the specified renderer.
    
      - globalsTabUpdateProcNames : gtu (bool)          [create,query,edit]
          This flag returns the names of procedures that are used to update the unified render globals window tabs that are
          associated with the specified renderer.
    
      - iprOptionsMenuLabel : ipm      (unicode)       [create,query,edit]
          Set or query the label for the IPR update options menu which is under the render view's IPR menu.
    
      - iprOptionsProcedure : io       (unicode)       [create,query,edit]
          Set or query the IPR render options procedure associated with the specified renderer.
    
      - iprOptionsSubMenuProcedure : ips (unicode)       [create,query,edit]
          Set or query the procedure for creating the sub menu for the IPR update options menu which is under the render view's
          IPR menu.
    
      - iprRenderProcedure : ipr       (unicode)       [create,query,edit]
          Set or query the IPR render command associated with the specified renderer.
    
      - iprRenderSubMenuProcedure : irs (unicode)       [create,query,edit]
          Set or query the procedure for creating the sub menu for the IPR render menu which is under the render view's IPR menu.
    
      - isRunningIprProcedure : isr    (unicode)       [create,query,edit]
          Set or query the isRunningIpr command associated with the specified renderer.
    
      - logoCallbackProcedure : lgc    (unicode)       [create,query,edit]
          Set or query the procedure which is a callback associated to the logo for the specified renderer.   For example, the
          logo and the callback can be used in the unified render globals window beside the Render UsingoptionMenu.
    
      - logoImageName : log            (unicode)       [create,query,edit]
          Set or query the logo image name for the specified renderer. The logo is a image representing the renderer.
    
      - materialViewRendererList : mvl (bool)          [query,edit]
          Returns the names of material view renderers that are currently registered.
    
      - materialViewRendererPause : mvp (bool)          [query,edit]
          Specifies whether to pause the material viewer. Useful for globally halting updates to the material viewer. The material
          view renderer will remain suspended while the viewer is paused.
    
      - materialViewRendererSuspend : mvs (bool)          [query,edit]
          Specifies whether to suspend or resume the material view renderer. Useful for temporarily stopping the material view
          renderer while another rendering task is running.
    
      - namesOfAvailableRenderers : ava (bool)          [query,edit]
          Returns the names of renderers that are currently registered.
    
      - pauseIprRenderProcedure : psi  (unicode)       [create,query,edit]
          Set or query the pause IPR render procedure associated with the specified renderer.
    
      - polyPrelightProcedure : pp     (unicode)       [create,query,edit]
          Set or query the polygon prelight procedure associated with the specified renderer.
    
      - refreshIprRenderProcedure : rfi (unicode)       [create,query,edit]
          Set or query the refresh IPR render procedure associated with the specified renderer.
    
      - renderDiagnosticsProcedure : rd (unicode)       [create,query,edit]
          Set or query the render diagnostics procedure associated with the specified renderer.
    
      - renderGlobalsProcedure : rg    (unicode)       [create,query,edit]
          This flag is obsolete.  It will be removed in the next release.
    
      - renderMenuProcedure : rm       (unicode)       [create,query,edit]
          This flag is obsolete. It will be removed in the next release.
    
      - renderOptionsProcedure : ro    (unicode)       [create,query,edit]
          Set or query the render options procedure associated with the specified renderer.
    
      - renderProcedure : r            (unicode)       [create,query,edit]
          Set or query the render command associated with the specified renderer.
    
      - renderRegionProcedure : rr     (unicode)       [create,query,edit]
          Set or query the render region procedure associated with the specified renderer.
    
      - renderSequenceProcedure : rs   (unicode)       []
    
      - rendererUIName : ui            (unicode)       [create,query,edit]
          Set or query the rendererUIName for the specified renderer. The rendererUIName is the name of the renderer as it would
          appear in menus.
    
      - renderingEditorsSubMenuProcedure : res (unicode)       [create,query,edit]
          Set or query the procedure reponsible for creating renderer specific editors submenu under the Rendering Editorsmenu for
          the specified renderer.
    
      - showBatchRenderLogProcedure : brl (unicode)       [create,query,edit]
          Set or query the log file batch procedure associated with the specified renderer.
    
      - showBatchRenderProcedure : sbr (unicode)       [create,query,edit]
          Set or query the show batch render procedure associated with the specified renderer.
    
      - showRenderLogProcedure : srl   (unicode)       [create,query,edit]
          Set or query the log file render procedure associated with the specified renderer.
    
      - startIprRenderProcedure : sti  (unicode)       [create,query,edit]
          Set or query the start IPR render procedure associated with the specified renderer.
    
      - stopIprRenderProcedure : spi   (unicode)       [create,query,edit]
          Set or query the stop IPR render procedure associated with the specified renderer.
    
      - textureBakingProcedure : tb    (unicode)       [create,query,edit]
          Set or query the texture baking procedure associated with the specified renderer.
    
      - unregisterRenderer : unr       (bool)          [query,edit]
          Unregister the specified renderer.                                 Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.renderer`
    """

    pass


def uvLink(*args, **kwargs):
    """
    This command is used to make, break and query UV linking relationships between UV sets on objects and textures that use
    those UV sets. If no make, break or query flag is specified and both uvSet and texture flags are present, the make flag
    is assumed to be specified. If no make, break or query flag is specified and only one of the uvSet and texture flags is
    present, the query flag is assumed to be specified. The term texturein the context of UV linking is a bit of an
    oversimplification. In fact, UV sets can be linked to any node which takes UV coordinates as input. However in most
    cases it will be a texture to which you wish to link a UV set.
    
    Flags:
      - b : b                          (bool)          [create]
          The presence of this flag on the command indicates that the command is being invoked to break links between UV sets and
          textures.
    
      - isValid : iv                   (bool)          [create]
          This flag is used to verify whether or not a texture or UV set is valid for the purposes of UV linking. It should be
          used in conjunction with either the -texture flag or the -uvSet flag, but not both at the same time.
    
      - make : m                       (bool)          [create]
          The presence of this flag on the command indicates that the command is being invoked to make links between UV sets and
          textures.
    
      - queryObject : qo               (PyNode)        [create]
          This flag should only be used in conjunction with a query of a texture. This flag is used to indicate that the results
          of the query should be limited to UV sets of the object specified by this flag.
    
      - texture : t                    (PyNode)        [create]
          The argument to the texture flag specifies the texture to be used by the command in performing the action.
    
      - uvSet : uvs                    (PyNode)        [create]
          The argument to the uvSet flag specifies the UV set to be used by the command in performing the action.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.uvLink`
    """

    pass


def createRenderLayer(*args, **kwargs):
    """
    Create a new render layer.  The render layer number will be assigned based on the first unassigned number not less than
    the base index number found in the render layer global parameters.  Normally all objects and their descendants will be
    added to the new render layer but if '-noRecurse' is specified then only the objects themselves will be added. Only
    transforms and geometry will be added to the new render layer.
    
    Modifications:
      - returns a PyNode object
    
    Flags:
      - empty : e                      (bool)          [create]
          If set then create an empty render layer. The global flag or specified member list will take precidence over  use of
          this flag.
    
      - g : g                          (bool)          [create]
          If set then create a layer that contains all DAG objects in the scene. Any future objects created will also
          automatically become members of this layer. The global flag will take precidence over use of the empty flag or specified
          member list.
    
      - makeCurrent : mc               (bool)          [create]
          If set then make the new render layer the current one.
    
      - name : n                       (unicode)       [create]
          Name of the new render layer being created.
    
      - noRecurse : nr                 (bool)          [create]
          If set then only add specified objects to the render layer.  Otherwise all descendants will also be added.
    
      - number : num                   (int)           [create]
          Number for the new render layer being created.                             Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.createRenderLayer`
    """

    pass


def renderPartition(*args, **kwargs):
    """
    Set or query the model's current partition. When flag qis not used, a partion name must be passed as an argument. In
    this case the current partition is set to that name.
    
    
    Derived from mel command `maya.cmds.renderPartition`
    """

    pass


def hwReflectionMap(*args, **kwargs):
    """
    This command creates a hwReflectionMap node for having reflection on textured surfaces that currently have their boolean
    attribute displayHWEnvironment set to true.
    
    Flags:
      - backTextureName : bkn          (unicode)       [query]
          This flag specifies the file texture name for the back side of the cube.Default is noneWhen queried, this flag returns a
          string.
    
      - bottomTextureName : bmn        (unicode)       [query]
          This flag specifies the file texture name for the bottom side of the cube.Default is noneWhen queried, this flag returns
          a string.
    
      - cubeMap : cm                   (bool)          [query]
          If on, the reflection of the textures is done using the cube mapping.Default is false. The reflection is done using
          sphere mapping.When queried, this flag returns a boolean.
    
      - decalMode : dm                 (bool)          [query]
          If on, the reflection color replaces the surface shading.Default is false. The reflection is multiplied to the surface
          shading.When queried, this flag returns a boolean.
    
      - enable : en                    (bool)          [query]
          If on, enable the corresponding hwReflectionMap node.Default is false.When queried, this flag returns a boolean.
    
      - frontTextureName : ftn         (unicode)       [query]
          This flag specifies the file texture name for the front side of the cube.Default is noneWhen queried, this flag returns
          a string.
    
      - leftTextureName : ltn          (unicode)       [query]
          This flag specifies the file texture name for the left side of the cube.Default is noneWhen queried, this flag returns a
          string.
    
      - rightTextureName : rtn         (unicode)       [query]
          This flag specifies the file texture name for the right side of the cube.Default is noneWhen queried, this flag returns
          a string.
    
      - sphereMapTextureName : smn     (unicode)       [query]
          This flag specifies the file texture name for the sphere mapping option.Default is noneWhen queried, this flag returns a
          string.
    
      - topTextureName : tpn           (unicode)       [query]
          This flag specifies the file texture name for the top side of the cube.Default is noneWhen queried, this flag returns a
          string.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.hwReflectionMap`
    """

    pass


def rampColorPort(*args, **kwargs):
    """
    This command creates a control that displays an image representing the ramp node specified, and supports editing of that
    node.
    
    Flags:
      - annotation : ann               (unicode)       [create,query,edit]
          Annotate the control with an extra string value.
    
      - backgroundColor : bgc          (float, float, float) [create,query,edit]
          The background color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0. When setting backgroundColor, the background is automatically enabled, unless
          enableBackground is also specified with a false value.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Add a documentation flag to the control.  The documentation flag has a directory structure like hierarchy. Eg. -dt
          render/multiLister/createNode/material
    
      - dragCallback : dgc             (script)        [create,edit]
          Adds a callback that is called when the middle mouse button is pressed.  The MEL version of the callback is of the form:
          global proc string[] callbackName(string $dragControl, int $x, int $y, int $mods) The proc returns a string array that
          is transferred to the drop site. By convention the first string in the array describes the user settable message type.
          Controls that are application defined drag sources may ignore the callback. $mods allows testing for the key modifiers
          CTL and SHIFT. Possible values are 0 == No modifiers, 1 == SHIFT, 2 == CTL, 3 == CTL + SHIFT. In Python, it is similar,
          but there are two ways to specify the callback.  The recommended way is to pass a Python function object as the
          argument.  In that case, the Python callback should have the form: def callbackName( dragControl, x, y, modifiers ): The
          values of these arguments are the same as those for the MEL version above. The other way to specify the callback in
          Python is to specify a string to be executed.  In that case, the string will have the values substituted into it via the
          standard Python format operator.  The format values are passed in a dictionary with the keys dragControl, x, y,
          modifiers.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(x)d %(y)d %(modifiers)d'
    
      - dropCallback : dpc             (script)        [create,edit]
          Adds a callback that is called when a drag and drop operation is released above the drop site.  The MEL version of the
          callback is of the form: global proc callbackName(string $dragControl, string $dropControl, string $msgs[], int $x, int
          $y, int $type) The proc receives a string array that is transferred from the drag source. The first string in the msgs
          array describes the user defined message type. Controls that are application defined drop sites may ignore the callback.
          $type can have values of 1 == Move, 2 == Copy, 3 == Link. In Python, it is similar, but there are two ways to specify
          the callback.  The recommended way is to pass a Python function object as the argument.  In that case, the Python
          callback should have the form: def pythonDropTest( dragControl, dropControl, messages, x, y, dragType ): The values of
          these arguments are the same as those for the MEL version above. The other way to specify the callback in Python is to
          specify a string to be executed.  In that case, the string will have the values substituted into it via the standard
          Python format operator.  The format values are passed in a dictionary with the keys dragControl, dropControl, messages,
          x, y, type.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(dropControl)s %(messages)r %(x)d %(y)d %(type)d'
    
      - enable : en                    (bool)          [create,query,edit]
          The enable state of the control.  By default, this flag is set to true and the control is enabled.  Specify false and
          the control will appear dimmed or greyed-out indicating it is disabled.
    
      - enableBackground : ebg         (bool)          [create,query,edit]
          Enables the background color of the control.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - fullPathName : fpn             (bool)          [query]
          Return the full path name of the widget, which includes all the parents
    
      - height : h                     (int)           [create,query,edit]
          The height of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
    
      - highlightColor : hlc           (float, float, float) [create,query,edit]
          The highlight color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0.
    
      - isObscured : io                (bool)          [query]
          Return whether the control can actually be seen by the user. The control will be obscured if its state is invisible, if
          it is blocked (entirely or partially) by some other control, if it or a parent layout is unmanaged, or if the control's
          window is invisible or iconified.
    
      - manage : m                     (bool)          [create,query,edit]
          Manage state of the control.  An unmanaged control is not visible, nor does it take up any screen real estate.  All
          controls are created managed by default.
    
      - noBackground : nbg             (bool)          [create,edit]
          Clear/reset the control's background. Passing true means the background should not be drawn at all, false means the
          background should be drawn.  The state of this flag is inherited by children of this control.
    
      - node : n                       (PyNode)        [create]
          Specifies the name of the newRamp texture node this port will represent.
    
      - numberOfPopupMenus : npm       (bool)          [query]
          Return the number of popup menus attached to this control.
    
      - parent : p                     (unicode)       [create,query]
          The parent layout for this control.
    
      - popupMenuArray : pma           (bool)          [query]
          Return the names of all the popup menus attached to this control.
    
      - preventOverride : po           (bool)          [create,query,edit]
          If true, this flag disallows overriding the control's attribute via the control's right mouse button menu.
    
      - selectedColorControl : sc      (unicode)       [create,edit]
          Set the name of the control (if any) which is to be used to show the color of the currently selected entry in the ramp.
          This control will automatically update as the user selects different entries in the ramp, and will modify the selected
          entry if edited. The type of control must be an attrColorSliderGrp.
    
      - selectedInterpControl : si     (unicode)       [create,edit]
          Set the name of the control (if any) which is to be used to show the interpolation of the currently selected entry in
          the ramp. This control will automatically update as the user selects different entries in the ramp, and will modify the
          selected entry if edited. The type of control must be an attrEnumOptionMenuGrp.
    
      - selectedPositionControl : sp   (unicode)       [create,edit]
          Set the name of the control (if any) which is to be used to show the position of the currently selected entry in the
          ramp. This control will automatically update as the user selects different entries in the ramp, and will modify the
          selected entry if edited. The type of control must be an attrFieldSliderGrp.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - verticalLayout : vl            (bool)          [create,query,edit]
          Set the preview's layout.
    
      - visible : vis                  (bool)          [create,query,edit]
          The visible state of the control.  A control is created visible by default.  Note that a control's actual appearance is
          also dependent on the visible state of its parent layout(s).
    
      - visibleChangeCommand : vcc     (script)        [create,query,edit]
          Command that gets executed when visible state of the control changes.
    
      - width : w                      (int)           [create,query,edit]
          The width of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.rampColorPort`
    """

    pass


def roll(*args, **kwargs):
    """
    The roll command rotates a camera about its viewing direction, a positive angle produces clockwise camera rotation,
    while a negative angle produces counter-clockwise camera rotation. The default mode is relative and the rotation is
    applied with respect to the current orientation of the camera. When mode is set to absolute, the rotation is applied
    with respect to the plane constructed from the following three vectors in the world space: the world up vector, the
    camera view vector, and the camera up vector. The rotation angle is specified in degrees. The roll command can be
    applied to either a perspective or an orthographic camera. This command may be applied to more than one camera; objects
    that are not cameras are ignored. When no camera name supplied, this command is applied to all currently active cameras.
    
    Flags:
      - absolute : abs                 (bool)          [create]
          Set to absolute mode.
    
      - degree : d                     (float)         [create]
          Set the amount of the rotation angle.
    
      - relative : rel                 (bool)          [create]
          Set to relative mode.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.roll`
    """

    pass


def ogsRender(*args, **kwargs):
    """
    Renders an image or a sequence using the OGS rendering engine
    
    Flags:
      - activeMultisampleType : mst    (unicode)       [query,edit]
          Query the current active multisample type.
    
      - activeRenderOverride : cro     (unicode)       [query,edit]
          Set or query the current active render override.
    
      - activeRenderTargetFormat : fpt (unicode)       [query,edit]
          Query the current active floating point target format.
    
      - availableFloatingPointTargetFormat : afp (bool)          [query,edit]
          Returns the names of available floating point render target format.
    
      - availableMultisampleType : amt (bool)          [query,edit]
          Returns the names of available multisample type.
    
      - availableRenderOverrides : aro (bool)          [query,edit]
          Returns the names of available render overrides.
    
      - camera : cam                   (unicode)       [create,query,edit]
          Specify the camera to use.  Use the first available camera if the camera     given is not found.
    
      - currentFrame : cf              (bool)          [create,query,edit]
          Render the current frame.
    
      - currentView : cv               (bool)          [create,query,edit]
          When turned on, only the current view will be rendered.
    
      - enableFloatingPointRenderTarget : efp (bool)          [query,edit]
          Enable/disable floating point render target.
    
      - enableMultisample : ems        (bool)          [query,edit]
          Enable/disable multisample.
    
      - frame : f                      (float)         [create,edit]
          Specify the frame to render.
    
      - height : h                     (int)           [create,query,edit]
          The height flag pass the height to the ogsRender command. If not used,     the height is taken from the render globals
          settings.
    
      - layer : l                      (PyNode)        [create,query,edit]
          Render the specified render layer.         Only this render layer will be rendered,         regardless of the renderable
          attribute value of the render layer.         The layer name will be appended to the output image file name.         The
          specified render layer becomes the current render layer before rendering,         and remains as current render layer
          after the rendering.
    
      - noRenderView : nrv             (bool)          [create,query,edit]
          When turned on, the render view is not updated after image computation
    
      - width : w                      (int)           [create,query,edit]
          The width flag pass the width to the ogsRender command. If not used,     the width is taken from the render globals
          settings.                              Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.ogsRender`
    """

    pass


def hwRenderLoad(*args, **kwargs):
    """
    Empty command used to force the dynamic load of HR render
    
    
    Derived from mel command `maya.cmds.hwRenderLoad`
    """

    pass


def defaultLightListCheckBox(*args, **kwargs):
    """
    This command creates a checkBox that controls whether a shadingGroup is connected/disconnected from the
    defaultLightList.
    
    Flags:
      - annotation : ann               (unicode)       [create,query,edit]
          Annotate the control with an extra string value.
    
      - backgroundColor : bgc          (float, float, float) [create,query,edit]
          The background color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0. When setting backgroundColor, the background is automatically enabled, unless
          enableBackground is also specified with a false value.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Add a documentation flag to the control.  The documentation flag has a directory structure like hierarchy. Eg. -dt
          render/multiLister/createNode/material
    
      - dragCallback : dgc             (script)        [create,edit]
          Adds a callback that is called when the middle mouse button is pressed.  The MEL version of the callback is of the form:
          global proc string[] callbackName(string $dragControl, int $x, int $y, int $mods) The proc returns a string array that
          is transferred to the drop site. By convention the first string in the array describes the user settable message type.
          Controls that are application defined drag sources may ignore the callback. $mods allows testing for the key modifiers
          CTL and SHIFT. Possible values are 0 == No modifiers, 1 == SHIFT, 2 == CTL, 3 == CTL + SHIFT. In Python, it is similar,
          but there are two ways to specify the callback.  The recommended way is to pass a Python function object as the
          argument.  In that case, the Python callback should have the form: def callbackName( dragControl, x, y, modifiers ): The
          values of these arguments are the same as those for the MEL version above. The other way to specify the callback in
          Python is to specify a string to be executed.  In that case, the string will have the values substituted into it via the
          standard Python format operator.  The format values are passed in a dictionary with the keys dragControl, x, y,
          modifiers.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(x)d %(y)d %(modifiers)d'
    
      - dropCallback : dpc             (script)        [create,edit]
          Adds a callback that is called when a drag and drop operation is released above the drop site.  The MEL version of the
          callback is of the form: global proc callbackName(string $dragControl, string $dropControl, string $msgs[], int $x, int
          $y, int $type) The proc receives a string array that is transferred from the drag source. The first string in the msgs
          array describes the user defined message type. Controls that are application defined drop sites may ignore the callback.
          $type can have values of 1 == Move, 2 == Copy, 3 == Link. In Python, it is similar, but there are two ways to specify
          the callback.  The recommended way is to pass a Python function object as the argument.  In that case, the Python
          callback should have the form: def pythonDropTest( dragControl, dropControl, messages, x, y, dragType ): The values of
          these arguments are the same as those for the MEL version above. The other way to specify the callback in Python is to
          specify a string to be executed.  In that case, the string will have the values substituted into it via the standard
          Python format operator.  The format values are passed in a dictionary with the keys dragControl, dropControl, messages,
          x, y, type.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(dropControl)s %(messages)r %(x)d %(y)d %(type)d'
    
      - enable : en                    (bool)          [create,query,edit]
          The enable state of the control.  By default, this flag is set to true and the control is enabled.  Specify false and
          the control will appear dimmed or greyed-out indicating it is disabled.
    
      - enableBackground : ebg         (bool)          [create,query,edit]
          Enables the background color of the control.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - fullPathName : fpn             (bool)          [query]
          Return the full path name of the widget, which includes all the parents
    
      - height : h                     (int)           [create,query,edit]
          The height of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
    
      - highlightColor : hlc           (float, float, float) [create,query,edit]
          The highlight color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0.
    
      - isObscured : io                (bool)          [query]
          Return whether the control can actually be seen by the user. The control will be obscured if its state is invisible, if
          it is blocked (entirely or partially) by some other control, if it or a parent layout is unmanaged, or if the control's
          window is invisible or iconified.
    
      - label : l                      (unicode)       []
    
      - manage : m                     (bool)          [create,query,edit]
          Manage state of the control.  An unmanaged control is not visible, nor does it take up any screen real estate.  All
          controls are created managed by default.
    
      - noBackground : nbg             (bool)          [create,edit]
          Clear/reset the control's background. Passing true means the background should not be drawn at all, false means the
          background should be drawn.  The state of this flag is inherited by children of this control.
    
      - numberOfPopupMenus : npm       (bool)          [query]
          Return the number of popup menus attached to this control.
    
      - parent : p                     (unicode)       [create,query]
          The parent layout for this control.
    
      - popupMenuArray : pma           (bool)          [query]
          Return the names of all the popup menus attached to this control.
    
      - preventOverride : po           (bool)          [create,query,edit]
          If true, this flag disallows overriding the control's attribute via the control's right mouse button menu.
    
      - shadingGroup : sg              (PyNode)        [create,edit]
          The shading group that is to be connected/disconnected from the defaultLightList.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - visible : vis                  (bool)          [create,query,edit]
          The visible state of the control.  A control is created visible by default.  Note that a control's actual appearance is
          also dependent on the visible state of its parent layout(s).
    
      - visibleChangeCommand : vcc     (script)        [create,query,edit]
          Command that gets executed when visible state of the control changes.
    
      - width : w                      (int)           [create,query,edit]
          The width of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.defaultLightListCheckBox`
    """

    pass


def iprEngine(*args, **kwargs):
    """
    Command to create or edit an iprEngine.  A iprEngine is an object that watches for changes to shading networks and
    automatically reshades to generate an up-to-date image.
    
    Flags:
      - copy : cp                      (unicode)       [edit]
          Copies the deep raster file, as well as its related files, to the new location.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - diagnostics : dig              (bool)          []
    
      - estimatedMemory : mem          (bool)          [query]
          Displays the estimated memory being used by IPR.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - iprImage : ipr                 (unicode)       [create,query,edit]
          Specify the ipr image to use.
    
      - motionVectorFile : mvf         (bool)          [query]
          Returns the name of the motion vector file used by IPR.
    
      - object : obj                   (PyNode)        [create,query,edit]
          The objects to be tuned.
    
      - region : r                     (int, int, int, int) [create,query,edit]
          The coordinates of the region to be tuned. The integers are in the sequence left bottom right topor x1,y2  x2,y2
    
      - relatedFiles : rel             (bool)          [query]
          Returns the names for the related files, e.g, the non-glow-non-blur image, the motion vector file, and the depth-map
          files.
    
      - releaseIprImage : rii          (bool)          [edit]
          The ipr image should be released and memory should    be freed.
    
      - resolution : res               (bool)          [query]
          The width and height of the ipr file.
    
      - scanlineIncrement : sli        (unicode)       [create,query,edit]
          Set the scanline increment percentage.  If the height of the region being update is 240 pixels, and the
          scanlineIncrement is 10% then the image will refresh blocks of 24 scanlines.
    
      - showProgressBar : spb          (bool)          [create,query,edit]
          Show progress bar during tuning.
    
      - startTuning : st               (bool)          [create,query,edit]
          An ipr image has been specified and now changes to shading    networks should force an image to be produced.
    
      - stopTuning : spt               (bool)          [create,query,edit]
          Tuning should cease but ipr image should not be closed.
    
      - underPixel : un                (int, int)      [edit]
          Get list of objects under the pixel sprcified.
    
      - update : u                     (bool)          [create,edit]
          Force an update.
    
      - updateDepthOfField : udf       (bool)          [create,edit]
          Force a refresh of depth-of-field.
    
      - updateLightGlow : ulg          (bool)          [create,query,edit]
          Automatically update when light glow changes.
    
      - updateMotionBlur : umb         (bool)          [create,query,edit]
          Automatically update when 2.5D motion blur changes.
    
      - updatePort : up                (unicode)       [create,query,edit]
          The name of the port that is to be updated when pixel values are recomputed.  (not currently supported)
    
      - updateShaderGlow : usg         (bool)          [create,query,edit]
          Automatically update when shader glow changes.
    
      - updateShading : us             (bool)          [create,query,edit]
          Automatically update shading.
    
      - updateShadowMaps : usm         (bool)          [create,edit]
          Force the shadow maps to be generated and an update to occur.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.iprEngine`
    """

    pass


def convertTessellation(*args, **kwargs):
    """
    Command to translate the basic tessellation attributes to advanced. If a camera flag is specified the translation will
    be based on the distance the surface is from the camera. The closer the surface is to the camera the more triangles
    there will be in the tessellation. If the -allCamerasflags is specified, the renderable camera closest to the surface
    will be used to set the tessellation. The camera tessellation estimate is also dependent on the current render
    resolution; a higher resolution the result in a more finely tessellated surface. Multiple NURB surfaces may be specified
    on the command line, or if no command arguments are specified the surfaces on the active list will be used. This command
    operates by calculating the chord height such that smooth tessellation is achieved when the surface is rendered.  The
    advanced tessellation setting will be enabled on each surface specified, the primary tessellation parameters will be
    set, and chord height will be used as the secondary criteria.
    
    Flags:
      - allCameras : acm               (bool)          [create]
          Specifies that all renderable cameras should be used in calculating     the screen based tessellation.
    
      - camera : cam                   (PyNode)        [create]
          Specifies the camera which should be used in calculating the screen     based tessellation.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.convertTessellation`
    """

    pass


def convertIffToPsd(*args, **kwargs):
    """
    Converts iff file to PSD file of given size              In query mode, return type is based on queried flag.
    
    Flags:
      - iffFileName : ifn              (unicode)       [create,query]
          Input iff file name
    
      - psdFileName : pfn              (unicode)       [create,query]
          Output file name
    
      - xResolution : xr               (int)           [create,query]
          X resolution of the image
    
      - yResolution : yr               (int)           [create,query]
          Y resolution of the image                                  Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.convertIffToPsd`
    """

    pass


def viewCamera(*args, **kwargs):
    """
    The viewCamera command is used to position a camera to look directly at the side or top of another camera. This is
    primarily useful for the user when he or she is setting depth-of-field and clipping planes, if they are being used. The
    default behaviour: If no other flags are specified, the camera in the active panel is moved and the -t is presumed. If
    there is a camera selected, it is used as the target camera.
    
    Flags:
      - move : m                       (PyNode)        [create]
          Specifies which camera needs to move.
    
      - sideView : s                   (bool)          [create]
          Position camera to look at the side of the target camera.
    
      - topView : t                    (bool)          [create]
          Position camera to look at the top of the target camera (default).                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.viewCamera`
    """

    pass


def shadingConnection(*args, **kwargs):
    """
    Sets the connection state of a connection between nodes that are used in shading. Specify the destination attribute of
    the connection. In query mode, return type is based on queried flag.
    
    Flags:
      - connectionState : cs           (bool)          [create,query,edit]
          Specifies the state of the connection. On/True/1 means the connection is still active. Off/False/0 means the connection
          is inactive.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.shadingConnection`
    """

    pass


def viewClipPlane(*args, **kwargs):
    """
    The viewClipPlane command can be used to query or set a camera's clip planes. If a camera is not specified, the camera
    in the active view will be used. The near and far clip plane flags may be used in conjunction with the auto clip plane
    flag. In query mode, return type is based on queried flag.
    
    Flags:
      - autoClipPlane : acp            (bool)          [create,query]
          Compute the clip planes such that all object's in the camera's viewing frustum will be visible.
    
      - farClipPlane : fcp             (float)         [create,query]
          Set or query the far clip plane.
    
      - nearClipPlane : ncp            (float)         [create,query]
          Set or query the near clip plane.
    
      - surfacesOnly : so              (bool)          [create]
          This flag is to be used in conjunction with the auto clip plane flag. Only the bounding boxes of surfaces will be used
          to compute the camera's clipping planes.                  Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.viewClipPlane`
    """

    pass


def lightlink(*args, **kwargs):
    """
    This command is used to make, break and query light linking relationships between lights/sets of lights and objects/sets
    of objects. If no make, break or query flag is specified and both lights and objects flags are present, the make flag is
    assumed to be specified. If no make, break or query flag is specified and only one of the lights and objects flags is
    present, the query flag is assumed to be specified. You can specify as many lights and objects as you like, using the
    multiuse -light and -object flags. A better way to perform light linking is to make sets of lights and sets of geometry.
    If you create a set which contains lights (such as the ceiling lights in your scene) and a set which contains geometry
    (such as the geometry of your character), you can then link the setcontaining lights with the setcontaining geometry in
    order to get those lights to illuminate those pieces of geometry. In addition, you can add and remove lights and
    geometry from their respective sets without having to make and break light links.
    
    Flags:
      - b : b                          (bool)          [create]
          The presence of this flag on the command indicates that the command is being invoked to break links between lights and
          renderable objects.
    
      - hierarchy : h                  (bool)          [create]
          When querying, specifies whether the result should include the hierarchy of transforms above shapes linked to the
          queried light/object. The transforms considered part of the hierarchy do not include the transform immediately above the
          shape. Default is true.
    
      - light : l                      (PyNode)        [create]
          The argument to the light flag specifies a node to be used by the command in performing the action as if the node is a
          light. This is a multiuse flag -- many light nodes can be specified in a single invocation of the lightlink command.
    
      - make : m                       (bool)          [create]
          The presence of this flag on the command indicates that the command is being invoked to make links between lights and
          renderable objects.
    
      - object : o                     (PyNode)        [create]
          The argument to the object flag specifies a node to be used by the command in performing the action as if the node is an
          object. This is a multiuse flag -- many object nodes can be specified in a single invocation of the lightlink command.
    
      - sets : set                     (bool)          [create]
          When querying, specifies whether the result should include sets linked to the queried light/object. Default is true.
    
      - shadow : shd                   (bool)          []
    
      - shapes : shp                   (bool)          [create]
          When querying, specifies whether the result should include shapes linked to the queried light/object. Default is true.
    
      - transforms : t                 (bool)          [create]
          When querying, specifies whether the result should include transforms immediately above shapes linked to the queried
          light/object. Default is true.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
      - useActiveLights : ual          (bool)          []
    
      - useActiveObjects : uao         (bool)          []
    
    
    Derived from mel command `maya.cmds.lightlink`
    """

    pass


def createLayeredPsdFile(*args, **kwargs):
    """
    Creates a  layered PSD file with image names as input to individual layers
    
    Dynamic library stub function
    
    Flags:
      - imageFileName : ifn            (unicode, unicode, unicode) [create]
          Layer name, blend mode, Image file name  The image in the file will be transferred to layer specified. The image file
          specified can be in any of the formats supported by maya (ex. iff, jpg, gif, tif etc.). The blend mode options are :
          Normal, Dissolve, Dark, Multiply, Color Burn, Linear Burn, Lighten, Screen, Color Dodge, Linear Dogde, Overlay, Soft
          Light, Hard Light, Dissolve, Vivid Light, Linear Light, Pin Light, Hard Mix, Difference, Exclusion, Hue, Saturation,
          Color,  Luminosity
    
      - psdFileName : psf              (unicode)       [create]
          PSD file name.
    
      - xResolution : xr               (int)           [create]
          X - resolution of the image.
    
      - yResolution : yr               (int)           [create]
          Y - resolution of the image.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.createLayeredPsdFile`
    """

    pass


def viewFit(*args, **kwargs):
    """
    The viewFit command positions the specified camera so its point-of-view contains all selected objects other than itself.
    If no objects are selected, everything is fit to the view (excepting cameras, lights, and sketching plannes). The fit-
    factor, if specified, determines how much of the view should be filled. If a camera is not specified, the camera in the
    active view will be used. After the camera is moved, its center of interest is set to the center of the bounding box of
    the objects.
    
    Flags:
      - allObjects : all               (bool)          [create]
          Specifies that all objects are to be fit regardless of the active list.
    
      - animate : an                   (bool)          [create]
          Specifies that the transition between camera positions should be animated.
    
      - center : c                     (bool)          [create]
          Specifies that the camera moves to the center of the selected object, but does not move the camera closer.
    
      - fitFactor : f                  (float)         [create]
          Specifies how much of the view should be filled with the fitteditems.
    
      - namespace : ns                 (unicode)       [create]
          Specifies a namespace that should be excluded. All objects in the specified namespace will be excluded from the fit
          process.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
      - panel : p                      (unicode)       []
    
    
    Derived from mel command `maya.cmds.viewFit`
    """

    pass


def preferredRenderer(*args, **kwargs):
    """
    Command to set the preferred renderer. This command also allows you to query the preferred renderer and to set the
    current renderer equal to the preferred renderer. It also allows users to specify a preferred fallback renderer.
    In query mode, return type is based on queried flag.
    
    Flags:
      - fallback : f                   (unicode)       [create,query]
          Sets the preferred fallback renderer.
    
      - makeCurrent : mc               (bool)          [create]
          Sets the current renderer equal to the preferred one.                              Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.preferredRenderer`
    """

    pass


def swatchRefresh(*args, **kwargs):
    """
    The swatchRefreshcommand causes image source node swatches to be refreshed on screen.  The purpose of this command is to
    provide a mechanism to trigger a swatch refresh in cases that are not subject to dirty propagation in the dependency
    graph.  This command only works with imageSource-derived node types. Invoking this command with no arguments will cause
    all imageSource swatches to be refreshed.
    
    
    Derived from mel command `maya.cmds.swatchRefresh`
    """

    pass


def cameraSet(*args, **kwargs):
    """
    This command manages camera set nodes. Camera sets allow the users to break a single camera shot into layers. Instead of
    drawing all objects with a single camera, you can isolate the camera to only focus on certain objects and layer another
    camera into the viewport that draws the other objects. The situation to use camera sets primarily occurs when building
    stereoscopic scenes. For example, a set of stereo parameters may make the background objects divergent beyond the
    tolerable range of the human perceptual system. However, you like the settings because the main focus is in the
    foreground and the depth is important to the visual look of the scene.  You can use camera sets to break apart the shot
    into a foreground stereo camera and background stereo camera. The foreground stereo camera will retain the original
    parameters; however, it will only focus on the foreground elements.  The background stereo camera will have a different
    set of stereo parameters and will only draw the background element. Camera sets can be viewed using the stereo viewer
    and are currently only designed to work with stereo camera rigs.
    
    Flags:
      - active : a                     (bool)          [create,query,edit]
          Gets / sets the active camera layer.
    
      - appendTo : atl                 (bool)          [create,edit]
          Append a new camera and/or object set to then end of the cameraSet layer list. This flag cannot be used in conjunction
          with insert flag. Additionally, it requires the camera and/or objectSet flag to be used.
    
      - camera : cam                   (PyNode)        [create,query,edit]
          Set/get the camera for a particular layer. When in query mode, You must specify the layer with the layer flag.
    
      - clearDepth : cd                (bool)          [create,query,edit]
          Specifies if the drawing buffer should be cleared before beginning the draw for that layer.
    
      - deleteAll : da                 (bool)          [create,edit]
          Delete all camera layers
    
      - deleteLayer : d                (bool)          [create,edit]
          Delete a layer from the camera set. You must specify the layer using the layer flag.
    
      - insertAt : ins                 (bool)          [create,edit]
          Inserts the specified camera and/or object set at the specified layer. This flag cannot be used in conjunction with the
          append flag. Additionally, this flag requires layer and camera (or objectSet) flag to be used.
    
      - layer : l                      (int)           [create,query,edit]
          Specifies the layer index to be used when accessing layer information
    
      - name : n                       (PyNode)        [create,query]
          Gets or sets the name for the created camera set.
    
      - numLayers : nl                 (bool)          [create,query]
          Returns the number of layers defined in the specified cameraSet
    
      - objectSet : os                 (PyNode)        [create,query,edit]
          Set/get the objectSet for a particular layer. When in query mode, you must specify the layer with the layer flag.
    
      - order : o                      (int)           [create,query,edit]
          Set the order in which a particular layer is processed. This flag must be used in conjunction with the layer flag.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.cameraSet`
    """

    pass


def resolutionNode(*args, **kwargs):
    """
    The resolutionNode creates a render resolution node and registers it with the model.  The createNode command will not
    register nodes of this type correctly.
    
    Flags:
      - name : n                       (unicode)       []
    
      - parent : p                     (unicode)       []
    
      - shared : s                     (bool)          []
    
      - skipSelect : ss                (bool)          []
    
    
    Derived from mel command `maya.cmds.resolutionNode`
    """

    pass


def batchRender(*args, **kwargs):
    """
    The batchRender command is used to spawn off a separate rendering session of the current maya file. If no mayaFile is
    specified, it'll ask you whether you want the current job killed. The batchRender will spawn a separate maya process in
    which commands will be communicated to it through a commandPort. If Maya is unable to find an available port an error
    will be produced. Maya will attempt to use ports 7835 through 7844.
    
    Flags:
      - filename : f                   (unicode)       [create]
          Filename to be rendered; if empty, a temporary filename will be created.
    
      - melCommand : mc                (unicode)       [create]
          Mel command to execute to run a renderer other than the software renderer.
    
      - numProcs : n                   (int)           [create]
          Number of processors to use (0 means use all available processors).
    
      - preRenderCommand : prc         (unicode)       [create]
          Command to be run prior to invoking mentalray standalone renderer.
    
      - remoteRenderMachine : rm       (unicode)       [create]
          Name of remote render machine. Not available on Windows.
    
      - renderCommandOptions : rco     (unicode)       [create]
          Arguments to the render command for mentalray standalone rendering.
    
      - showImage : si                 (bool)          [create]
          Show progress of the current rendering job.
    
      - status : st                    (unicode)       []
    
      - useRemoteRender : um           (bool)          [create]
          If remote rendering is desired. Not available on Windows.
    
      - useStandalone : us             (bool)          [create]
          Batch rendering is to be done with mentalray standalone
    
      - verbosity : v                  (int)           [create]
          Defines the verbosity level to report the batch rendering status:1: display only one start message, then one message
          when all frames are rendered.2: display only start and end frame messages.3: display all messages (default).Flag can
          have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.batchRender`
    """

    pass


def shadingNode(*args, **kwargs):
    """
    This command creates a new node in the dependency graph of the specified type. The shadingNode command classifies any DG
    node as a shader, texture light, post process, or utility so that it can be properly organized in the multi-lister.
    Recall that any DG node can be used a part of a a shader, texture or light - regardless of how it is classified by this.
    command. These classifications are provided for convenience in the UI.
    
    Flags:
      - asLight : al                   (bool)          [create]
          classify the current DG node as a light
    
      - asPostProcess : app            (bool)          [create]
          classify the current DG node as a post process
    
      - asRendering : ar               (bool)          [create]
          classify the current DG node as a rendering node
    
      - asShader : asShader            (bool)          [create]
          classify the current DG node as a shader
    
      - asTexture : at                 (bool)          [create]
          classify the current DG node as a texture
    
      - asUtility : au                 (bool)          [create]
          classify the current DG node as a utility
    
      - isColorManaged : icm           (bool)          [create]
          classify the current DG node as being color managed
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace doesn't exist, we will create the namespace.
    
      - parent : p                     (unicode)       [create]
          Specifies the parent in the DAG under which the new node belongs.
    
      - shared : s                     (bool)          [create]
          This node is shared across multiple files, so only create it if it does not already exist.
    
      - skipSelect : ss                (bool)          [create]
          This node is not to be selected after creation, the original selection will be preserved.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.shadingNode`
    """

    pass


def listCameras(*args, **kwargs):
    """
    Command to list all cameras. If no flags are given, both perspective and orthographic cameras will be displayed. This
    command returns an array of camera names. When the transform name uniquely identifies the camera it is used, otherwise
    the shape name will be returned.
    
    Flags:
      - orthographic : o               (bool)          [create]
          Display all orthographic cameras.
    
      - perspective : p                (bool)          [create]
          Display all perspective cameras.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.listCameras`
    """

    pass


def showShadingGroupAttrEditor(*args, **kwargs):
    """
    The showShadingGroupAttrEditor command opens up the attribute editor for the current object's shading-group information.
    
    
    Derived from mel command `maya.cmds.showShadingGroupAttrEditor`
    """

    pass


def imagePlane(*args, **kwargs):
    """
    The imagePlane command allows querying of various properties of         an image plane and any movie in use by the image
    plane. It also supports         creating and edit.         The object passed to the command may either be an imagePlane
    node,         or a camera, in which case the command uses the image plane attached         to the camera (if any). If no
    object is passed in, the current         selection is used.         Currently, most movie related queries work only on
    64 bit Windows systems.
    
    Flags:
      - camera : c                     (unicode)       [create,query,edit]
          When creating, it will try to attach the created image plane to the specified camera. If the given camera is invalid,
          creating will fail. When querying, it will query which camera current image plane is attaching to. If it has no camera
          attached to (free image plane), it will return an empty string. When edit, it will make the image plane attach to the
          new specified camera. If the camera given is invalid, it will do nothing. When the image plane is attached to a camera,
          the image plane's transform node will be set identity. The detach command will not restore the original position of the
          image plane. but the undo command will restore the original position of the image plane.
    
      - counter : cn                   (bool)          []
          Query the 'counter' flag of the movie's timecode format. If this is true, the timecode returned by the -timeCode flag
          will be a simple counter. If false, the returned timecode will be an array of integers (hours, minutes, seconds,
          frames).
    
      - detach : d                     (bool)          [edit]
          This flag can only be used in the edit mode, when this flag is used in edit, it will detach current image plane from any
          camera it attaches to and make it a free image plane.
    
      - dropFrame : df                 (bool)          [query]
          Query the 'drop frame' flag of the movie's timecode format.
    
      - fileName : fn                  (unicode)       [create,edit]
          Set the image name for image plane to read.
    
      - frameDuration : fd             (int)           [query]
          Query the frame duration of the movie's timecode format.
    
      - height : h                     (float)         [create,query,edit]
          Height of the image plane. When creating, if this flag is not specified, it will use 10.0 as default height.
    
      - imageSize : iz                 (int, int)      [query]
          Get size of the loaded image.
    
      - lookThrough : lt               (unicode)       [create,query,edit]
          The camera currently used for image plane to look through.
    
      - maintainRatio : mr             (bool)          [create,query,edit]
          Let the image plane respect the picture aspect ratio. When creating, if this flag is not specified, it will use true as
          default value.
    
      - name : n                       (unicode)       [create,query]
          Set the image plane node name when creating or return the image plane name when querying.
    
      - negTimesOK : nt                (bool)          [query]
          Query the 'neg times OK' flag of the movie's timecode format.
    
      - numFrames : nf                 (int)           [query]
          Query the whole number of frames per second of the movie's timecode format.
    
      - quickTime : qt                 (bool)          [query]
          Query whether the image plane is using a QuickTime movie.
    
      - showInAllViews : sia           (bool)          [create,query,edit]
          The flag is used to show the current image plane in all views or not.
    
      - timeCode : tc                  (int)           [query]
          Query the whole number of frames per second of the movie's timecode format.
    
      - timeCodeTrack : tt             (bool)          [query]
          Query whether the movie on the image plane has a timecode track.
    
      - timeScale : ts                 (int)           [query]
          Query the timescale of the movie's timecode format.
    
      - twentyFourHourMax : tf         (bool)          [query]
          Query the '24 hour max' flag of the movie's timecode format.
    
      - width : w                      (float)         [create,query,edit]
          Width of the image plane. When creating, if this flag is not specified, it will use 10.0 as default width.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.imagePlane`
    """

    pass


def viewLookAt(*args, **kwargs):
    """
    The viewLookAt command positions the specified camera so it is looking at the centroid of all selected objects. If no
    objects are specified the camera will look at the ground plane.
    
    Flags:
      - position : pos                 (float, float, float) [create]
          Position in world space to make the camera look at.                  Flag can have multiple arguments, passed either as
          a tuple or a list.
    
    
    Derived from mel command `maya.cmds.viewLookAt`
    """

    pass


def psdTextureFile(*args, **kwargs):
    """
    Creates a Photoshop file with UVSnap shot image and the layer set names as the input.
    
    Dynamic library stub function
    
    Flags:
      - channelRGB : chc               (unicode, int, int, int, int) [create]
          (M) Layer set names, index, red, green and blue values are given as input. Using this flag, the layers created can be
          filled with specified colors.  This is a multi use flag.  The index specifies the placement order of layer sets in the
          created file.
    
      - channels : chs                 (unicode, int, bool) [create]
          (M) Layer set names and index are given as input. This is a multi use flag. A layer set with the given name will be
          created.  The second argument is the index which specifies the placement order of layer sets in the created file. The
          third argument is a boolean, if truea layer is created inside the layer set , falsecreates an  empty layer set
    
      - imageFileName : ifn            (unicode, unicode, int) [create]
          Image file name, Layerset name and index.  The image in the file will be transferred to layer set specified.  The index
          specifies the placement order of layer sets in the created psd file.  The image file specified can be in any of the
          formats supported by maya (ex. iff, jpg, gif, tif etc.)
    
      - psdFileName : psf              (unicode)       [create]
          PSD file name.
    
      - snapShotImageName : ssi        (unicode)       [create]
          Image file name on the disk containing UV snapshot / reference image.
    
      - uvSnapPostionTop : uvt         (bool)          [create]
          Specifies the position of UV snapshot image layer  in the PSD file. Truepositions this layer at the top and
          Falsepositions the layer at the bottom next to the background layer in the PSD file
    
      - xResolution : xr               (int)           [create]
          X - resolution of the image.
    
      - yResolution : yr               (int)           [create]
          Y - resolution of the image.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.psdTextureFile`
    """

    pass


def displacementToPoly(*args, **kwargs):
    """
    Command bakes geometry with displacement mapping into a polygonal object.
    
    Flags:
      - findBboxOnly : fbb             (bool)          [create,query,edit]
          When used, only the bounding box scale for the displaced object is found.                                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.displacementToPoly`
    """

    pass


def checkDefaultRenderGlobals(*args, **kwargs):
    """
    To query whether or not the defaultRenderGlobals node has been modified since the last file save, use `ls -modified`. To
    force the scene to be dirty/clean use `file -modified`                  In query mode, return type is based on queried
    flag.
    
    
    Derived from mel command `maya.cmds.checkDefaultRenderGlobals`
    """

    pass


def createSurfaceShader(shadertype, name=None):
    """
    create a shader and shading group
    """

    pass


def viewPlace(*args, **kwargs):
    """
    This command positions the camera as specified. The lookAt and viewDirection flags are mutually exclusive, as are the
    ortho and perspective flags. If this command switches a camera from ortho to perspective or the other way around without
    specifying a new field of view, then one is calculated based on a heuristic involving the selected objects. If the
    camera is not specified on the command line, the command will check to see if there is a camera on the active list. The
    user should be aware that some positions will be unattainable. For example, using a new camera located at the origin and
    specifying a lookAt of [0 0 -5] and an up of [1 1 1]. In these cases, the camera will always aim at the lookAt, and the
    new up direction will be determined by transforming the specified up into camera space and then projecting this vector
    onto a plane defined by the camera's up and right vectors. Using the example above, the new up vector will be [1 1 0].
    
    Flags:
      - animate : an                   (bool)          [create]
          If set to true then animate the camera transition from current position to the final one.
    
      - eyePoint : eye                 (float, float, float) [create]
          The new eye point in world coordinates.
    
      - fieldOfView : fov              (float)         [create]
          The new field of view (in degrees, for perspective cameras, and in world distance for ortho cameras)
    
      - lookAt : la                    (float, float, float) [create]
          The new look-at point in world coordinates.
    
      - ortho : o                      (bool)          [create]
          Sets the camera to be orthgraphic.
    
      - perspective : p                (bool)          [create]
          Sets the camera to be perspective.
    
      - upDirection : up               (float, float, float) [create]
          The new up direction vector.
    
      - viewDirection : vd             (float, float, float) [create]
          The new view direction vector.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.viewPlace`
    """

    pass


def renderWindowEditor(*args, **kwargs):
    """
    Create a editor window that can receive the result of the rendering process
    
    Flags:
      - autoResize : ar                (bool)          [create,query,edit]
          Lets the render view editor automatically resize the viewport or not.
    
      - blendMode : blm                (int)           [create,query,edit]
          Sets the blend mode for the render view. New image sent to the render view will be blended with the previous image in
          the render view, and the composited image will appear.
    
      - caption : cap                  (unicode)       [create,query,edit]
          Sets the caption which appears at the bottom of the render view.
    
      - changeCommand : cc             (unicode, unicode, unicode, unicode) [create,query,edit]
          Parameters: First string: commandSecond string: editorNameThird string: editorCmdFourth string: updateFuncCall the
          command when something changes in the editor The command should have this prototype :  command(string $editor, string
          $editorCmd, string $updateFunc, int $reason)  The possible reasons could be : 0: no particular reason1: scale color2:
          buffer (single/double)3: axis 4: image displayed5: image saved in memory
    
      - clear : cl                     (int, int, float, float, float) [create,query,edit]
          Clear the image with the given color at the given resolution. Argumnets are respecively: width height red green blue.
    
      - cmEnabled : cme                (bool)          [query,edit]
          Turn on or off applying color management in the View.  If set, the color management configuration set in the current
          view is used.
    
      - colorManage : com              (bool)          [edit]
          When used with the writeImage flag, causes the written image to be color-managed using the settings from the view color
          manager attached to the view.
    
      - compDisplay : cd               (int)           [create,query,edit]
          0 : disable compositing.1 : displays the composited image immediately. For example, when foreground layer tile is sent
          to the render view window, the composited tile is displayed in the render view window, and the original foreground layer
          tile is not displayed.2 : display the un-composited image, and keep the composited image for the future command. For
          example, when foreground layer tile is sent to the render view window, the original foreground layer tile is not
          displayed, and the composited tile is stored in a buffer.3 : show the current composited image. If there is a composited
          image in the buffer, display it.
    
      - compImageFile : cif            (unicode)       [create,query,edit]
          Open the given image file and blend with the buffer as if the image was just rendered.
    
      - control : ctl                  (bool)          [query]
          Query only. Returns the top level control for this editor. Usually used for getting a parent to attach popup menus.
          Caution: It is possible for an editor to exist without a control. The query will return NONEif no control is present.
    
      - currentCamera : crc            (unicode)       [create,query,edit]
          Get or set the current camera. (used when redoing last render)
    
      - currentCameraRig : crg         (unicode)       [create,query,edit]
          Get or set the current camera rig name. If a camera rig is specified, it will be used when redoing the last render as
          opposed to the currentCamera value, as the currentCamera value will hold the child camera last used for rendering the
          camera rig.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - displayImage : di              (int)           [query,edit]
          Set a particular image in the Editor Image Stack as the current Editor Image. Images are added to the Editor Image Stack
          using the si/saveImageflag.
    
      - displayImageViewCount : dvc    (int)           [query]
          Query the number of views stored for a given image in the Editor Image Stack. This is not the same as querying using
          viewImageCountwhich returns the number of views for the current rendered image.
    
      - displayStyle : dst             (unicode)       [create,query,edit]
          Set the mode to display the image. Valid values are: colorto display the basic RGB imagemaskto display the mask
          channellumto display the luminance of the image
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Attaches a tag to the editor.
    
      - doubleBuffer : dbf             (bool)          [create,query,edit]
          Set the display in double buffer mode
    
      - drawAxis : da                  (bool)          [create,query,edit]
          Set or query whether the axis will be drawn.
    
      - editorName : en                (bool)          [query]
          Returns the name of the editor, or an empty string if the editor has not been created yet.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - exposure : exp                 (float)         [query,edit]
          The exposure value used by the color management of the current view.
    
      - filter : f                     (unicode)       [create,query,edit]
          Specifies the name of an itemFilter object to be used with this editor. This filters the information coming onto the
          main list of the editor.
    
      - forceMainConnection : fmc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object. This is a variant of the -mainListConnection flag in
          that it will force a change even when the connection is locked. This flag is used to reduce the overhead when using the
          -unlockMainConnection , -mainListConnection, -lockMainConnection flags in immediate succession.
    
      - frameImage : fi                (bool)          [create,query,edit]
          Frames the image inside the window.
    
      - frameRegion : fr               (bool)          [create,query,edit]
          Frames the region inside the window.
    
      - gamma : ga                     (float)         [query,edit]
          The gamma value used by the color management of the current view.
    
      - highlightConnection : hlc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its highlight list. Not all
          editors have a highlight list. For those that do, it is a secondary selection list.
    
      - loadImage : li                 (unicode)       [edit]
          load an image from disk and set it as the current Editor Image
    
      - lockMainConnection : lck       (bool)          [create,edit]
          Locks the current list of objects within the mainConnection, so that only those objects are displayed within the editor.
          Further changes to the original mainConnection are ignored.
    
      - mainListConnection : mlc       (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object.
    
      - marquee : mq                   (float, float, float, float) [create,query,edit]
          The arguments define the four corners of a rectangle: top left bottom right. The rectangle defines a marquee for the
          render computation.
    
      - nbImages : nim                 (bool)          [query]
          returns the number of images
    
      - nextViewImage : nvi            (bool)          [create,edit]
          The render editor has the capability to render multiple cameras within a single view. This is different from image
          binning where an image is saved. Multiple image views are useful for comparing two different camera renders side-by-
          side. The nextViewImage flag tells the editor that it should prepare its internal image storage mechanism to store to
          the next view location.
    
      - panel : pnl                    (unicode)       [create,query]
          Specifies the panel for this editor. By default if an editor is created in the create callback of a scripted panel it
          will belong to that panel. If an editor does not belong to a panel it will be deleted when the window that it is in is
          deleted.
    
      - parent : p                     (unicode)       [create,query,edit]
          Specifies the parent layout for this editor. This flag will only have an effect if the editor is currently un-parented.
    
      - pcaption : pca                 (unicode)       [create,query,edit]
          Get or set the permanent caption which appears under the image that is currently showing in the render editor.
    
      - realSize : rs                  (bool)          [create,query,edit]
          Display the image with a one to one pixel match.
    
      - refresh : ref                  (bool)          [edit]
          requests a refresh of the current Editor Image.
    
      - removeAllImages : ra           (bool)          [edit]
          remove all the Editor Images from the Editor Image Stack
    
      - removeImage : ri               (bool)          [edit]
          remove the current Editor Image from the Editor Image Stack
    
      - resetRegion : rr               (bool)          [create,query,edit]
          Forces a reset of any marquee/region.
    
      - resetViewImage : rvi           (bool)          [create,edit]
          The render editor has the capability to render multiple cameras within a single view. This is different from image
          binning where an image is saved. Multiple image views are useful for comparing two different camera renders side-by-
          side. The resetViewImage flag tells the editor that it should reset its internal image storage mechanism to the first
          image. This would happen at the very start of a render view render.
    
      - saveImage : si                 (bool)          [edit]
          save the current Editor Image to memory. Saved Editor Images are stored in an Editor Image Stack. The most recently
          saved image is stored in position 0, the second most recently saved image in position 1, and so on... To set the current
          Editor Image to a previously saved image use the di/displayImageflag.
    
      - scaleBlue : sb                 (float)         [create,query,edit]
          Define the scaling factor for the blue component in the View. The default value is 1 and can be between -1000 to +1000
    
      - scaleGreen : sg                (float)         [create,query,edit]
          Define the scaling factor for the green component in the View. The default value is 1 and can be between -1000 to +1000
    
      - scaleRed : sr                  (float)         [create,query,edit]
          Define the scaling factor for the red component in the View. The default value is 1 and can be between -1000 to +1000
    
      - selectionConnection : slc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its own selection list. As the
          user selects things in this editor, they will be selected in the selectionConnection object. If the object undergoes
          changes, the editor updates to show the changes.
    
      - showRegion : srg               (int, int)      [create,query,edit]
          Shows the current region at the given resolution. The two parameters define the width and height.
    
      - singleBuffer : sbf             (bool)          [create,query,edit]
          Set the display in single buffer mode
    
      - snapshot : snp                 (unicode, int, int) [create,query,edit]
          Makes a copy of the camera of the model editor at the given size. First argument is the editor name, second is the
          width, third is the height.
    
      - snapshotMode : snm             (bool)          []
    
      - stateString : sts              (bool)          [query]
          Query only flag. Returns the MEL command that will create an editor to match the current editor state. The returned
          command string uses the string variable $editorName in place of a specific name.
    
      - stereo : s                     (int)           [create,query,edit]
          Puts the editor into stereo image mode.  The effective resolution of the output image is twice the size of the
          horizontal size. The orientation of the images can be set using the stereoOrientation flag.
    
      - stereoImageOrientation : sio   (unicode, unicode) [create,query,edit]
          Specifies the orientation of stereo camera renders.  The first argument specifies the orientation value for the
          firstleft image and the second argument specifies the orientation value for the right image. The orientation values are
          'normal', the image appears as seen throught he camera, or 'mirrored', the image is mirrored horizontally.
    
      - stereoMode : sm                (unicode)       [create,query,edit]
          Specifies how the image is displayed in the view.  By default the stereo is rendered with a side by side image.  The
          rendered image is a single image that is twice the size of a normal image, 'both'. Users can also choose to display as
          'redcyan', 'redcyanlum', 'leftonly', 'rightonly', or 'stereo'.  both - displays both the left and right redcyan -
          displays the images as a red/cyan pair. redcyanlum - displays the luminance of the images as a red/cyan pair. leftonly -
          displays the left side only rightonly - displays the right side only stereo - mode that supports Crystal Eyes(tm) or
          Zscreen (tm) renders
    
      - toggle : tgl                   (bool)          [create,query,edit]
          Turns the ground plane display on/off.
    
      - unParent : up                  (bool)          [create,edit]
          Specifies that the editor should be removed from its layout. This cannot be used in query mode.
    
      - unlockMainConnection : ulk     (bool)          [create,edit]
          Unlocks the mainConnection, effectively restoring the original mainConnection (if it is still available), and dynamic
          updates.
    
      - updateMainConnection : upd     (bool)          [create,edit]
          Causes a locked mainConnection to be updated from the orginal mainConnection, but preserves the lock state.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - viewImageCount : vic           (int)           [create,query,edit]
          The render editor has the capability to render multiple cameras within a single view. This is different from image
          binning where an image is saved. Multiple image views are useful for comparing two different camera renders side-by-
          side. The viewImageCount flag tells the editor that it should prepare its internal image storage mechanism for a given
          number of views.
    
      - viewTransformName : vtn        (unicode)       [query,edit]
          Sets/gets the view transform to be applied if color management is enabled in the current view.
    
      - writeImage : wi                (unicode)       [edit]
          write the current Editor Image to disk                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.renderWindowEditor`
    """

    pass


def sampleImage(*args, **kwargs):
    """
    The sampleImage command is used to control parameters of sample images, such as swatches in the multilister. The fast
    option turns on or off some rendering cheats which speed up the render but may cause edges to look ragged. The
    resolution option specifies the width in pixels of the image which will be rendered for the specified node. Note that
    the width of the image is also the height of the image since sample images are square.
    
    Flags:
      - fastSample : f                 (bool)          [create]
          If fast but rough rendering for sampleImage is to be used
    
      - resolution : r                 (<type 'int'>, PyNode) [create]
          The first argument to this flag specifies a resolution in pixels. The second argument specifies a dependency node. The
          effect of this flag is that further sample image renderings for the specified node will be made at the specified
          resolution.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.sampleImage`
    """

    pass


def renderInfo(*args, **kwargs):
    """
    The renderInfo commands sets geometric properties of surfaces of the selected object. In query mode, return type is
    based on queried flag.
    
    Flags:
      - castShadows : cs               (bool)          [create]
          Determines if object casts shadow or not.
    
      - chordHeight : ch               (float)         [create]
          Tessellation subdivision criteria.
    
      - chordHeightRatio : chr         (float)         [create]
          Tessellation subdivision criteria.
    
      - doubleSided : ds               (bool)          [create]
          Determines if object double or single sided.
    
      - edgeSwap : es                  (bool)          [create]
          Tessellation subdivision criteria.
    
      - minScreen : ms                 (float)         [create]
          Tessellation subdivision criteria.
    
      - name : n                       (unicode)       []
    
      - opposite : o                   (bool)          [create]
          Determines if the normals of the object is to be reversed.
    
      - smoothShading : ss             (bool)          [create]
          Determines if smooth shaded, or flat shaded - applies only to polysets.
    
      - unum : un                      (int)           [create]
          Tessellation subdivision criteria.
    
      - useChordHeight : uch           (bool)          [create]
          Tessellation subdivision criteria.
    
      - useChordHeightRatio : ucr      (bool)          [create]
          Tessellation subdivision criteria.
    
      - useDefaultLights : udl         (bool)          [create]
          Obsolete flag.
    
      - useMinScreen : ums             (bool)          [create]
          Tessellation subdivision criteria.
    
      - utype : ut                     (int)           [create]
          Tessellation subdivision criteria.
    
      - vnum : vn                      (int)           [create]
          Tessellation subdivision criteria.
    
      - vtype : vt                     (int)           [create]
          Tessellation subdivision criteria.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.renderInfo`
    """

    pass


def cameraView(*args, **kwargs):
    """
    This command creates a preset view for a camera which is then independent of the camera. The view stores a camera's eye
    point, center of interest point, up vector, tumble pivot, horizontal aperture, vertical aperature, focal length,
    orthographic width, and whether the camera is orthographic or perspective by default. Or you can only store 2D pan/zoom
    attributes by setting the bookmarkType to 1. These settings can be applied to any other camera through the set camera
    flag. This command can be used for creation or edit of camera view objects.  This command can only be executed with one
    of the add bookmark, or remove bookmark and one of set camera, or the set view flags set.
    
    Flags:
      - addBookmark : ab               (bool)          [create,edit]
          Associate this view with the camera specified or the camera in the active model panel. This flag can be used for
          creation or edit.
    
      - animate : an                   (bool)          [edit]
    
      - bookmarkType : typ             (int)           [create]
          Specify the bookmark type, which can be: 0. 3D bookmark; 1. 2D Pan/Zoom bookmark.
    
      - camera : c                     (PyNode)        [edit]
          Specify the camera to use. This flag should be used in conjunction with the add bookmark, remove bookmark, set camera,
          or set view flags. If this flag is not specified the camera in the active model panel will be used.
    
      - name : n                       (unicode)       [create]
          Set the name of the view. This flag can only be used for creation.
    
      - removeBookmark : rb            (bool)          [edit]
          Remove the association of this view with the camera specified or the camera in the active model panel. This can only be
          used with edit.
    
      - setCamera : sc                 (bool)          [edit]
          Set this view into a camera specified by the camera flag or the camera in the active model panel. This flag can only be
          used with edit.
    
      - setView : sv                   (bool)          [edit]
          Set the camera view to match a camera specified or the active model panel. This flag can only be used with edit.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.cameraView`
    """

    pass


def getRenderDependencies(*args, **kwargs):
    """
    Command to return dependencies of an image source.  Image sources (such as render targets) can depend on other upstream
    image sources that result from renderings of 3D scene, or renderings of 2D compositing graphs. This command returns
    these dependencies, so that they can be analyzed and rendered.
    
    
    Derived from mel command `maya.cmds.getRenderDependencies`
    """

    pass


def nodeIconButton(*args, **kwargs):
    """
    This control supports up to 3 icon images and 4 different display styles.  The icon image displayed is the one that best
    fits the current size of the control given its current style. This command creates a button that can be displayed with
    different icons, with or without a text label. If the button is drag and dropped onto other controls (e.g., HyperShade),
    the command will be executed and the return string will be used as the name of a dropped node.
    
    Flags:
      - align : al                     (unicode)       [create,query,edit]
          The label alignment.  Alignment values are left, right, and center. By default, the label is aligned center. Currently
          only available when -st/style is set to iconAndTextCentered.
    
      - annotation : ann               (unicode)       [create,query,edit]
          Annotate the control with an extra string value.
    
      - backgroundColor : bgc          (float, float, float) [create,query,edit]
          The background color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0. When setting backgroundColor, the background is automatically enabled, unless
          enableBackground is also specified with a false value.
    
      - command : c                    (script)        [create,query,edit]
          Command executed when the control is pressed. The command should return a string which will be used to facilitate node
          drag and drop.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - disabledImage : di             (unicode)       [create,query,edit]
          Image used when the button is disabled. Image size must be the same as the image specified with the i/imageflag. This is
          a Windows only flag.
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Add a documentation flag to the control.  The documentation flag has a directory structure like hierarchy. Eg. -dt
          render/multiLister/createNode/material
    
      - dragCallback : dgc             (script)        [create,edit]
          Adds a callback that is called when the middle mouse button is pressed.  The MEL version of the callback is of the form:
          global proc string[] callbackName(string $dragControl, int $x, int $y, int $mods) The proc returns a string array that
          is transferred to the drop site. By convention the first string in the array describes the user settable message type.
          Controls that are application defined drag sources may ignore the callback. $mods allows testing for the key modifiers
          CTL and SHIFT. Possible values are 0 == No modifiers, 1 == SHIFT, 2 == CTL, 3 == CTL + SHIFT. In Python, it is similar,
          but there are two ways to specify the callback.  The recommended way is to pass a Python function object as the
          argument.  In that case, the Python callback should have the form: def callbackName( dragControl, x, y, modifiers ): The
          values of these arguments are the same as those for the MEL version above. The other way to specify the callback in
          Python is to specify a string to be executed.  In that case, the string will have the values substituted into it via the
          standard Python format operator.  The format values are passed in a dictionary with the keys dragControl, x, y,
          modifiers.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(x)d %(y)d %(modifiers)d'
    
      - dropCallback : dpc             (script)        [create,edit]
          Adds a callback that is called when a drag and drop operation is released above the drop site.  The MEL version of the
          callback is of the form: global proc callbackName(string $dragControl, string $dropControl, string $msgs[], int $x, int
          $y, int $type) The proc receives a string array that is transferred from the drag source. The first string in the msgs
          array describes the user defined message type. Controls that are application defined drop sites may ignore the callback.
          $type can have values of 1 == Move, 2 == Copy, 3 == Link. In Python, it is similar, but there are two ways to specify
          the callback.  The recommended way is to pass a Python function object as the argument.  In that case, the Python
          callback should have the form: def pythonDropTest( dragControl, dropControl, messages, x, y, dragType ): The values of
          these arguments are the same as those for the MEL version above. The other way to specify the callback in Python is to
          specify a string to be executed.  In that case, the string will have the values substituted into it via the standard
          Python format operator.  The format values are passed in a dictionary with the keys dragControl, dropControl, messages,
          x, y, type.  The dragControlvalue is a string and the other values are integers (eg the callback string could be print
          '%(dragControl)s %(dropControl)s %(messages)r %(x)d %(y)d %(type)d'
    
      - enable : en                    (bool)          [create,query,edit]
          The enable state of the control.  By default, this flag is set to true and the control is enabled.  Specify false and
          the control will appear dimmed or greyed-out indicating it is disabled.
    
      - enableBackground : ebg         (bool)          [create,query,edit]
          Enables the background color of the control.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - flipX : fx                     (bool)          [create,query,edit]
          Is the image flipped horizontally?
    
      - flipY : fy                     (bool)          [create,query,edit]
          Is the image flipped vertically?
    
      - font : fn                      (unicode)       [create,query,edit]
          The font for the text.  Valid values are boldLabelFont, smallBoldLabelFont, tinyBoldLabelFont, plainLabelFont,
          smallPlainLabelFont, obliqueLabelFont, smallObliqueLabelFont, fixedWidthFontand smallFixedWidthFont.
    
      - fullPathName : fpn             (bool)          [query]
          Return the full path name of the widget, which includes all the parents
    
      - height : h                     (int)           [create,query,edit]
          The height of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
    
      - highlightColor : hlc           (float, float, float) [create,query,edit]
          The highlight color of the control. The arguments correspond to the red, green, and blue color components. Each
          component ranges in value from 0.0 to 1.0.
    
      - image : i                      (unicode)       [create,query,edit]
          If you are not providing images with different sizes then you may use this flag for the control's image. If the
          iconOnlystyle is set, the icon will be scaled to the size of the control.
    
      - image1 : i1                    (unicode)       [create,query,edit]
    
      - image2 : i2                    (unicode)       [create,query,edit]
    
      - image3 : i3                    (unicode)       [create,query,edit]
          This control supports three icons. The icon that best fits the current size of the control will be displayed.
    
      - imageOverlayLabel : iol        (unicode)       [create,query,edit]
          A short string, up to 6 characters, representing a label that will be displayed on top of the image.
    
      - isObscured : io                (bool)          [query]
          Return whether the control can actually be seen by the user. The control will be obscured if its state is invisible, if
          it is blocked (entirely or partially) by some other control, if it or a parent layout is unmanaged, or if the control's
          window is invisible or iconified.
    
      - label : l                      (unicode)       [create,query,edit]
          The text that appears in the control.
    
      - labelOffset : lo               (int)           [create,query,edit]
          The label offset. Default is 0. Currently only available when -st/style is set to iconAndTextCentered.
    
      - ltVersion : lt                 (unicode)       [create,query,edit]
          This flag is used to specify the Maya LT version that this control feature was introduced, if the version flag is not
          specified, or if the version flag is specified but its argument is different. This value is only used by Maya LT, and
          otherwise ignored. The argument should be given as a string of the version number (e.g. 2013, 2014). Currently only
          accepts major version numbers (e.g. 2013 Ext 1, or 2013.5 should be given as 2014).
    
      - manage : m                     (bool)          [create,query,edit]
          Manage state of the control.  An unmanaged control is not visible, nor does it take up any screen real estate.  All
          controls are created managed by default.
    
      - marginHeight : mh              (int)           [create,query,edit]
          The number of pixels above and below the control content. The default value is 1 pixel.
    
      - marginWidth : mw               (int)           [create,query,edit]
          The number of pixels on either side of the control content. The default value is 1 pixel.
    
      - noBackground : nbg             (bool)          [create,edit]
          Clear/reset the control's background. Passing true means the background should not be drawn at all, false means the
          background should be drawn.  The state of this flag is inherited by children of this control.
    
      - numberOfPopupMenus : npm       (bool)          [query]
          Return the number of popup menus attached to this control.
    
      - overlayLabelBackColor : olb    (float, float, float, float) [create,query,edit]
          The RGBA color of the shadow behind the label defined by imageOverlayLabel. Default is 50% transparent black: 0 0 0 .5
    
      - overlayLabelColor : olc        (float, float, float) [create,query,edit]
          The RGB color of the label defined by imageOverlayLabel. Default is a light grey: .8 .8 .8
    
      - parent : p                     (unicode)       [create,query]
          The parent layout for this control.
    
      - popupMenuArray : pma           (bool)          [query]
          Return the names of all the popup menus attached to this control.
    
      - preventOverride : po           (bool)          [create,query,edit]
          If true, this flag disallows overriding the control's attribute via the control's right mouse button menu.
    
      - rotation : rot                 (float)         [create,query,edit]
          The rotation value of the image in radians.
    
      - style : st                     (unicode)       [create,query,edit]
          The draw style of the control.  Valid styles are iconOnly, textOnly, iconAndTextHorizontal, iconAndTextVertical, and
          iconAndTextCentered. (Note: iconAndTextCenteredis only available on Windows). If the iconOnlystyle is set, the icon will
          be scaled to the size of the control.
    
      - useAlpha : ua                  (bool)          [create,query,edit]
          Is the image using alpha channel?
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - version : ver                  (unicode)       [create,query,edit]
          Specify the version that this control feature was introduced. The argument should be given as a string of the version
          number (e.g. 2013, 2014). Currently only accepts major version numbers (e.g. 2013 Ext 1, or 2013.5 should be given as
          2014).
    
      - visible : vis                  (bool)          [create,query,edit]
          The visible state of the control.  A control is created visible by default.  Note that a control's actual appearance is
          also dependent on the visible state of its parent layout(s).
    
      - visibleChangeCommand : vcc     (script)        [create,query,edit]
          Command that gets executed when visible state of the control changes.
    
      - width : w                      (int)           [create,query,edit]
          The width of the control.  The control will attempt to be this size if it is not overruled by parent layout conditions.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.nodeIconButton`
    """

    pass


def setDefaultShadingGroup(*args, **kwargs):
    """
    The setDefaultShadingGroup command is used to change which shading group is considered the current default shading
    group. Subsequently created objects will be assigned to the new default group. In query mode, return type is based on
    queried flag.
    
    
    Derived from mel command `maya.cmds.setDefaultShadingGroup`
    """

    pass


def psdEditTextureFile(*args, **kwargs):
    """
    Edits the existing PSD file. Addition and deletion of the channels (layer sets) are supported.
    
    Dynamic library stub function
    
    Flags:
      - addChannel : adc               (unicode)       [create]
          Adds an empty layer set with the given name to a already existing PSD file.
    
      - addChannelColor : acc          (unicode, float, float, float) [create]
          (M) Specifies the filled color of  the layer which is created in a layer set given by the layer name.
    
      - addChannelImage : aci          (unicode, unicode) [create]
          (M) Specifies the image file name whose image needs to be added as a layer to a given layer set which is the first
          string.
    
      - deleteChannel : deleteChannel  (unicode)       [create]
          (M) Deletes the channels (layer sets) from a PSD file. This is a multiuse flag.
    
      - psdFileName : psf              (unicode)       [create]
          PSD file name.
    
      - snapShotImage : ssi            (unicode)       [create]
          Image file name on the disk containing UV snapshot / reference image.
    
      - uvSnapPostionTop : uvt         (bool)          [create]
          Specifies the position of UV snapshot image layer  in the PSD file. Truepositions this layer at the top and
          Falsepositions the layer at the bottom next to the background layer in the PSD file                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.psdEditTextureFile`
    """

    pass


def assignViewportFactories(*args, **kwargs):
    """
    Sets viewport factories for displays as materials or textures.           In query mode, return type is based on queried
    flag.
    
    Flags:
      - materialFactory : mf           (unicode)       [create,query,edit]
          Set or query the materialFactory for the node type.
    
      - nodeType : nt                  (unicode)       [create,query,edit]
          The node type.
    
      - textureFactory : tf            (unicode)       [create,query,edit]
          Set or query the textureFactory for the node type.                                 Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.assignViewportFactories`
    """

    pass


def textureWindow(*args, **kwargs):
    """
    This command is used to create a UV Editor and to query or edit the texture editor settings. The UV Editor displays
    texture mapped polygon objects in 2D texture space. Only active objects are visible in this window. The UV Editor has
    the ability to display two types of images. The Texture Image is a visualisation of the current texture and associated
    placement parameters. The Editor Image is a user specified image loaded from disk. A UV Editor can be invoked by
    selecting the Window -UV Texture Editor...menu item from the main maya menu listing that appears at the top of the maya
    window. It can also be invoked by selecting the Panel -UV Editoritem under the Panelsmenu item that appears at the top
    right hand corner of the view. As a UV Editor typically exists at start-up time, and as only one of these can exist at
    any given time, this command is normally used to query and edit the editor settings.
    
    Flags:
      - backFacingColor : bfc          (float, float, float, float) [create,query,edit]
          Sets or queries the RGBA back facing color.
    
      - capture : cpt                  (unicode)       [edit]
          Perform an one-time capture of the viewport to the named image file on disk.
    
      - captureSequenceNumber : csn    (int)           [edit]
          When a number greater or equal to 0 is specified each subsequent refresh will save an image file to disk if the capture
          flag has been enabled.  The naming of the file is:  {root name}.#.{extension}  if the name {root name}.{extension} is
          used for the capture flag argument. The value of # starts at the number specified to for this argument and increments
          for each subsequent refresh.  Sequence capture can be disabled by specifying a number less than 0 or an empty file name
          for the capture flag.
    
      - changeCommand : cc             (unicode, unicode, unicode, unicode) [create,query,edit]
          Parameters: First string: commandSecond string: editorNameThird string: editorCmdFourth string: updateFuncCall the
          command when something changes in the editor The command should have this prototype :  command(string $editor, string
          $editorCmd, string $updateFunc, int $reason)  The possible reasons could be : 0: no particular reason1: scale color2:
          buffer (single/double)3: axis 4: image displayed5: image saved in memory
    
      - checkerDensity : cd            (int)           [create,query,edit]
          Sets the density of the checker and identification pattern.
    
      - clearImage : ci                (bool)          [edit]
          Clears the current Editor Image
    
      - cmEnabled : cme                (bool)          [query,edit]
          Turn on or off applying color management in the editor.  If set, the color management configuration set in the current
          editor is used.
    
      - control : ctl                  (bool)          [query]
          Query only. Returns the top level control for this editor. Usually used for getting a parent to attach popup menus.
          Caution: It is possible for an editor to exist without a control. The query will return NONEif no control is present.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - displayAxes : dax              (bool)          [query,edit]
          Specify true to display the grid axes.
    
      - displayCheckered : dct         (bool)          [create,query,edit]
          Display a unique checker and identification pattern for each uv tiles
    
      - displayDistortion : ddt        (bool)          [create,query,edit]
          Display the layout in shaded colors to indentify areas with stretched/squashed UVs
    
      - displayDivisionLines : ddl     (bool)          [query,edit]
          Specify true to display the subdivision lines between grid lines.
    
      - displayGridLines : dgl         (bool)          [query,edit]
          Specify true to display the grid lines.
    
      - displayImage : di              (int)           [query,edit]
          Set a particular image in the Editor Image Stack as the current Editor Image. Images are added to the Editor Image Stack
          using the si/saveImageflag.
    
      - displayLabels : dl             (bool)          [query,edit]
          Specify true to display the grid line numeric labels.
    
      - displayPreselection : dps      (bool)          [create,query,edit]
          Turns the pre-selection display on/off.
    
      - displaySolidMap : dsm          (bool)          [create,query,edit]
          Display an solid over lay for the active texture map.
    
      - displayStyle : dst             (unicode)       [create,query,edit]
          Set the mode to display the image. Valid values are: colorto display the basic RGB imagemaskto display the mask
          channellumto display the luminance of the image
    
      - distortionPerObject : dpo      (bool)          [create,query,edit]
          Turns the per-object distortion display on/off.
    
      - divisions : d                  (int)           [create,query,edit]
          Sets the number of subdivisions between main grid lines
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Attaches a tag to the editor.
    
      - doubleBuffer : dbf             (bool)          [create,query,edit]
          Set the display in double buffer mode
    
      - drawAxis : da                  (bool)          [create,query,edit]
          Set or query whether the axis will be drawn.
    
      - drawSubregions : dsr           (bool)          [create,query,edit]
          Turns the subregion display on/off.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - exposure : exp                 (float)         [query,edit]
          The exposure value used by the color management of the current editor.
    
      - filter : f                     (unicode)       [create,query,edit]
          Specifies the name of an itemFilter object to be used with this editor. This filters the information coming onto the
          main list of the editor.
    
      - forceMainConnection : fmc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object. This is a variant of the -mainListConnection flag in
          that it will force a change even when the connection is locked. This flag is used to reduce the overhead when using the
          -unlockMainConnection , -mainListConnection, -lockMainConnection flags in immediate succession.
    
      - forceRebake : frb              (bool)          [create,edit]
          Forces the current cache texture to refresh.
    
      - frameAll : fa                  (bool)          [create]
          This will zoom on the whole scene.
    
      - frameSelected : fs             (bool)          [create]
          This will zoom on the currently selected objects.
    
      - frontFacingColor : ffc         (float, float, float, float) [create,query,edit]
          Sets or queries the RGBA front facing color.
    
      - gamma : ga                     (float)         [query,edit]
          The gamma value used by the color management of the current editor.
    
      - highlightConnection : hlc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its highlight list. Not all
          editors have a highlight list. For those that do, it is a secondary selection list.
    
      - imageBaseColor : ibc           (float, float, float) [create,query,edit]
          The base color of the image, default is white 1.0 1.0 1.0
    
      - imageDisplay : id              (bool)          [query,edit]
          Turns on or off Texture Image display
    
      - imageNames : imn               (bool)          [query]
          The image names for all Texture Images available for display, if any.
    
      - imageNumber : imageNumber      (int)           [query,edit]
          Sets the number of the Texture Image to display This depends on the number of textures corresponding to the current
          selection. If there are N textures, then the possible Texture Image numbers are 0 to N-1.
    
      - imagePixelSnap : ip            (bool)          [query,edit]
          Sets a mode so that uv transformations in the UV Texture Editor will cause uv values to snap to image pixel corners.
          Which pixels are used depends on whether a Texture Image or an Editor Image is being displayed, if both are displayed
          the Texture Image pixels will be used.
    
      - imageRatio : imr               (bool)          [query,edit]
          Sets the window to draw using the Texture Image's height versus width ratio. If the width is greater than the height
          than than the width is set to be 1 unitin the window and the height is adjusted by width divided by height. This only
          affects the display of a Texture Image, not an Editor Image.
    
      - imageSize : imageSize          (bool)          [query]
          Returns the size of the Texture Image currently being display. The values returned are width followed by height. Image
          size can only be queried.
    
      - imageTileRange : itr           (float, float, float, float) [query,edit]
          Sets the UV range of the display. The 4 values specify the minimum U, V and maximum U, V in that order. When viewing a
          Texture Image, these values affect how many times the image is tiled based on appropriate parameters (e.g. Repeat UV,
          Mirror, Wrap, etc...) When viewing an Editor Image these values determine the visible size of the image. For example,
          setting the range to ( 0, 0, 2, 1 ) will cause the Editor Image to be loaded into a 2x1 rectangle, distorting it as
          necessary to fill the available space.
    
      - imageUnfiltered : iuf          (bool)          [query,edit]
          Sets the Texture Image to draw unfiltered. The image will appear pixelatedwhen the display resolution is higher than the
          resolution of the image.
    
      - internalFaces : internalFaces  (bool)          [create,query,edit]
          Display contained faces by the selected components.
    
      - isolateSelectSetUpdated : isu  (bool)          []
    
      - labelPosition : lp             (unicode)       [query,edit]
          The position of the grid's numeric labels. Valid values are axisand edge.
    
      - loadImage : li                 (unicode)       [edit]
          load an image from disk and set it as the current Editor Image
    
      - lockMainConnection : lck       (bool)          [create,edit]
          Locks the current list of objects within the mainConnection, so that only those objects are displayed within the editor.
          Further changes to the original mainConnection are ignored.
    
      - mainListConnection : mlc       (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object.
    
      - maxResolution : mrs            (int)           [create,query,edit]
          This flag will set the current cached texture's maximum resolution.
    
      - nbImages : nim                 (bool)          [query]
          returns the number of images
    
      - numUvSets : nuv                (bool)          [create,query,edit]
          This flag will return the number of uv sets for selected objects in the texture window.
    
      - numberOfImages : ni            (int)           [query]
          The number of Texture Images currently available for display.
    
      - panel : pnl                    (unicode)       [create,query]
          Specifies the panel for this editor. By default if an editor is created in the create callback of a scripted panel it
          will belong to that panel. If an editor does not belong to a panel it will be deleted when the window that it is in is
          deleted.
    
      - parent : p                     (unicode)       [create,query,edit]
          Specifies the parent layout for this editor. This flag will only have an effect if the editor is currently un-parented.
    
      - realSize : rs                  (bool)          [create]
          This will display the image with the size of the internal buffer. Note: This argument no long has any affect on image
          display.
    
      - refresh : ref                  (bool)          [edit]
          requests a refresh of the current Editor Image.
    
      - relatedFaces : rf              (bool)          [create,query,edit]
          Display connected faces by the selected components.
    
      - removeAllImages : ra           (bool)          [edit]
          remove all the Editor Images from the Editor Image Stack
    
      - removeImage : ri               (bool)          [edit]
          remove the current Editor Image from the Editor Image Stack
    
      - rendererString : rds           (unicode)       [create,query,edit]
          Set or query the string describing the current renderer.
    
      - reset : r                      (bool)          [create]
          Resets the ground plane to its default values.
    
      - saveImage : si                 (bool)          [edit]
          save the current Editor Image to memory. Saved Editor Images are stored in an Editor Image Stack. The most recently
          saved image is stored in position 0, the second most recently saved image in position 1, and so on... To set the current
          Editor Image to a previously saved image use the di/displayImageflag.
    
      - scaleBlue : sb                 (float)         [create,query,edit]
          Define the scaling factor for the blue component in the View. The default value is 1 and can be between -1000 to +1000
    
      - scaleGreen : sg                (float)         [create,query,edit]
          Define the scaling factor for the green component in the View. The default value is 1 and can be between -1000 to +1000
    
      - scaleRed : sr                  (float)         [create,query,edit]
          Define the scaling factor for the red component in the View. The default value is 1 and can be between -1000 to +1000
    
      - selectInternalFaces : sif      (bool)          [create,query,edit]
          Add to selectionList the faces which are contained by (internal to) selected components.
    
      - selectRelatedFaces : srf       (bool)          [create]
          Add to selectionList the faces which are connected to (non-internally related to) selected components.
    
      - selectionConnection : slc      (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will synchronize with its own selection list. As the
          user selects things in this editor, they will be selected in the selectionConnection object. If the object undergoes
          changes, the editor updates to show the changes.
    
      - setUvSet : suv                 (int)           [create,edit]
          This flag will set the current uv set on one given selected object within the texture window.
    
      - singleBuffer : sbf             (bool)          [create,query,edit]
          Set the display in single buffer mode
    
      - size : s                       (float)         [create,query,edit]
          Sets the size of the grid.
    
      - spacing : sp                   (float)         [create]
          Sets the spacing between main grid lines.
    
      - stateString : sts              (bool)          [query]
          Query only flag. Returns the MEL command that will create an editor to match the current editor state. The returned
          command string uses the string variable $editorName in place of a specific name.
    
      - style : st                     (int)           [query,edit]
          This flag is obsolete and should not be used.
    
      - tileLabels : tlb               (bool)          [create,query,edit]
          Turns the texture tile label display on/off.
    
      - toggle : tgl                   (bool)          [create,query,edit]
          Turns the ground plane display on/off.
    
      - toggleExposure : tge           (bool)          [edit]
          Toggles between the current and the default exposure value of the editor.
    
      - toggleGamma : tgg              (bool)          [edit]
          Toggles between the current and the default gamma value of the editor.
    
      - unParent : up                  (bool)          [create,edit]
          Specifies that the editor should be removed from its layout. This cannot be used in query mode.
    
      - unlockMainConnection : ulk     (bool)          [create,edit]
          Unlocks the mainConnection, effectively restoring the original mainConnection (if it is still available), and dynamic
          updates.
    
      - updateMainConnection : upd     (bool)          [create,edit]
          Causes a locked mainConnection to be updated from the orginal mainConnection, but preserves the lock state.
    
      - useFaceGroup : uf              (bool)          [create,query,edit]
          Display faces that are associated with the groupId that is set on the mesh node that is drawn. (The attribute
          displayFacesWithGroupId
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - uvSets : uvs                   (bool)          [create,query,edit]
          This flag will return strings containing uv set and object name pairs for selected objects in the texture window. The
          syntax of each pair is objectName | uvSetName, where | is a literal character.
    
      - viewPortImage : vpi            (bool)          [create,edit]
          Toggles the view port/ caching texture images.
    
      - viewTransformName : vtn        (unicode)       [query,edit]
          Sets the view pipeline to be applied if color management is enabled in the current editor.
    
      - writeImage : wi                (unicode)       [edit]
          write the current Editor Image to disk                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.textureWindow`
    """

    pass


def prepareRender(*args, **kwargs):
    """
    This command is used to register, manage and invoke render traversals. Render traversals are used to configure a scene
    to prepare it for rendering. This command has special support for scene assembly nodes.  To render scene assembly nodes,
    a rendering traversal can activate an appropriate representation, for each assembly node in the scene.  When rendering
    is done, this command can correspondingly restore the representation that was active before rendering on each assembly.
    Render traversals are grouped into traversal sets.  A render traversal set includes callbacks, or render traversals, for
    one or more of the following steps of rendering, ordered by decreasing level of granularity. A render traversal callback
    is an arbitrary script, either MEL or Python, that can transform the Maya scene for rendering purposes.
    preRenderTraversal run once per render, before any rendering is performed.postRenderTraversal run once per render, after
    all rendering has been performed.preRenderLayerTraversal run before rendering each render layer.postRenderLayerTraversal
    run after rendering each render layer.preRenderFrameTraversal run before rendering each frame.postRenderFrameTraversal
    run after rendering each frame.During a render view or batch render, Maya will run the render traversals from the same
    traversal set, the default traversal set.  Traversal sets are named, so multiple traversal sets can be registered with
    this command, and the default render traversal set can be switched to any one of these registered traversal sets.  When
    changing the default traversal set, the different render traversal callbacks (preRender, preRenderLayer, preRenderFrame,
    postRender, postRenderLayer, postRenderFrame) are switched as a unit. At render time, the software rendering code
    invokes the callbacks of the default traversal set.  The prepareRender scripting capability allows for the development
    of multiple rendering preparation scripts, including from plugins, to provide extensibility rather than being
    constrained to a single implementation. A special traversal set is the nulltraversal set.  It is the initial default
    traversal set, and cannot be deregistered.  It performs no work, and does not save and restore the assembly node active
    representation configuration.  It will provide WYSIWYG (What You See Is What You Get) rendering of assembly nodes,
    without switching to a different representation to render. Render traversals are invoked by Maya using this command's
    create mode. This is done by Maya's rendering infrastructure, and should not be required unless developing new render
    views or batch render code.  Most uses of this command will simply use the edit mode to register render traversals into
    a render traversal set, or the query mode to query the names of the render traversals in a render traversal set. The
    prepareRender command has support for saving and restoring the active representation of assembly nodes in the scene.
    Use the saveAssemblyConfig flag to indicate that the render traversal set requires saving the assembly node active
    representation before rendering begins, and should restore the assembly node active representation after rendering ends.
    It is the responsibility of render traversals that modify the scene in ways other than changing the active
    representation on assembly nodes to restore the scene to its previous state, most likely using the postRender,
    postRenderLayer, and postRenderFrame traversals. Note that Maya does not call the prepareRender -restore command on
    batch render completion, since batch rendering is done on a copy of the scene which is discarded once rendering
    terminates.  Implementors of render traversals may wish to check whether they are running in batch mode, to implement
    the same optimization.            In query mode, return type is based on queried flag.
    
    Flags:
      - defaultTraversalSet : dt       (unicode)       [query,edit]
          Set or query the default traversal set.  The prepareRender command performs operations on the default traversal set,
          unless the -traversalSet flag is used to specify an explicit traversal set.
    
      - deregister : d                 (unicode)       [edit]
          Deregister a registered traversal set.  If the deregistered traversal set is the default traversal set, the new default
          traversal set will be the nulltraversal set.
    
      - invokePostRender : ior         (bool)          [create]
          Invoke the postRender render traversal for a given traversal set.  The traversal set will be the default traversal set,
          unless the -traversalSet flag is used to specify an explicit traversal set.
    
      - invokePostRenderFrame : iof    (bool)          [create]
          Invoke the postRenderFrame render traversal for a given traversal set.  The traversal set will be the default traversal
          set, unless the -traversalSet flag is used to specify an explicit traversal set.
    
      - invokePostRenderLayer : iol    (bool)          [create]
          Invoke the postRenderLayer render traversal for a given traversal set.  The traversal set will be the default traversal
          set, unless the -traversalSet flag is used to specify an explicit traversal set.
    
      - invokePreRender : irr          (bool)          [create]
          Invoke the preRender render traversal for a given traversal set.  The traversal set will be the default traversal set,
          unless the -traversalSet flag is used to specify an explicit traversal set.
    
      - invokePreRenderFrame : irf     (bool)          [create]
          Invoke the preRenderFrame render traversal for a given traversal set.  The traversal set will be the default traversal
          set, unless the -traversalSet flag is used to specify an explicit traversal set.
    
      - invokePreRenderLayer : irl     (bool)          [create]
          Invoke the preRenderLayer render traversal for a given traversal set.  The traversal set will be the default traversal
          set, unless the -traversalSet flag is used to specify an explicit traversal set.
    
      - invokeSettingsUI : isu         (bool)          [create]
          Invoke the settings UI callback to populate a layout with UI controls, for a given traversal set.  The current UI parent
          will be a form layout, which the callback can query using the setParent command.  The traversal set will be the default
          traversal set, unless the -traversalSet flag is used to specify an explicit traversal set.
    
      - label : lbl                    (unicode)       [query,edit]
          Set or query the label for a given traversal set.  The label is used for UI display purposes, and can be localized.  The
          traversal set will be the default, unless the -traversalSet flag is used to specify an explicit traversal set.
    
      - listTraversalSets : lt         (bool)          [query]
          Query the supported render traversal sets.
    
      - postRender : por               (script)        [query,edit]
          Set or query the postRender render traversal for a given traversal set.  This traversal is run after a render.  The
          traversal set will be the default traversal set, unless the -traversalSet flag is used to specify an explicit traversal
          set.
    
      - postRenderFrame : pof          (script)        [query,edit]
          Set or query the postRenderFrame render traversal for a given traversal set.  This traversal is run after the render of
          a single frame, with a render layer.  The traversal set will be the default traversal set, unless the -traversalSet flag
          is used to specify an explicit traversal set.
    
      - postRenderLayer : pol          (script)        [query,edit]
          Set or query the postRenderLayer render traversal for a given traversal set.  This traversal is run after a render layer
          is rendered, within a render.  The traversal set will be the default traversal set, unless the -traversalSet flag is
          used to specify an explicit traversal set.
    
      - preRender : prr                (script)        [query,edit]
          Set or query the preRender render traversal for a given traversal set.  This traversal is run before a render.  The
          traversal set will be the default traversal set, unless the -traversalSet flag is used to specify an explicit traversal
          set.
    
      - preRenderFrame : prf           (script)        [query,edit]
          Set or query the preRenderFrame render traversal for a given traversal set.  This traversal is run before the render of
          a single frame, with a render layer.  The traversal set will be the default traversal set, unless the -traversalSet flag
          is used to specify an explicit traversal set.
    
      - preRenderLayer : prl           (script)        [query,edit]
          Set or query the preRenderLayer render traversal for a given traversal set.  This traversal is run before a render layer
          is rendered, within a render.  The traversal set will be the default traversal set, unless the -traversalSet flag is
          used to specify an explicit traversal set.
    
      - restore : rtr                  (bool)          [create]
          Clean up after rendering, including restoring the assembly active representation configuration for the whole scene, if
          the saveAssemblyConfig flag for the traversal set is true.  The traversal set will be the default traversal set, unless
          the -traversalSet flag is used to specify an explicit traversal set.
    
      - saveAssemblyConfig : sac       (bool)          [query,edit]
          Set or query whether or not the assembly active representation configuration for the whole scene should be saved for a
          given traversal set.  The traversal set will be the default, unless the -traversalSet flag is used to specify an
          explicit traversal set.
    
      - settingsUI : sui               (script)        [query,edit]
          Set or query the settings UI callback for a given traversal set.  The traversal set will be the default traversal set,
          unless the -traversalSet flag is used to specify an explicit traversal set.
    
      - setup : stp                    (bool)          [create]
          Setup render preparation, including saving the assembly active representation configuration for the whole scene, if the
          saveAssemblyConfig flag for the traversal set is true.  Any previously-saved configuration will be overwritten.  The
          traversal set will be the default traversal set, unless the -traversalSet flag is used to specify an explicit traversal
          set.
    
      - traversalSet : ts              (unicode)       [create,query,edit]
          Set or query properties for the specified registered traversal set.
    
      - traversalSetInit : tsi         (script)        [query,edit]
          Set or query the traversal set initialisation callback for a given traversal set. The traversal set will be the default
          traversal set, unless the -traversalSet flag is used to specify an explicit traversal set. This callback is invoked
          whenever the specified traversal set becomes the default. traversal set.                               Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.prepareRender`
    """

    pass


def track(*args, **kwargs):
    """
    The track command translates a camera horizontally or vertically in the world space. The viewing-direction and up-
    direction of the camera are not altered. There is no translation in the viewing direction. The track command can be
    applied to either a perspective or an orthographic camera. When no camera name is supplied, this command is applied to
    the camera in the active view.
    
    (<function track at 0x154ae7050>, <function addCmdDocsCallback at 0x1546e3578>, ('track', ''), {})
    
    Flags:
      - down : d                       (float)         [create]
          Set the amount of down translation in unit distance.
    
      - left : l                       (float)         [create]
          Set the amount of left translation in unit distance.
    
      - right : r                      (float)         [create]
          Set the amount of right translation in unit distance.
    
      - upDistance01 : u               (float)         [create]
          Set the amount of up translation in unit distance. This is equivalent to using up/upDistance02 flag.
    
      - upDistance02 : up              (float)         [create]
          Set the amount of up translation in unit distance. This is equivalent to using u/upDistance01 flag.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.track`
    """

    pass


def surfaceSampler(*args, **kwargs):
    """
    Maps surface detail from a source surface to a new texture map on a target surface. Both objects must be selected when
    the command is invoked, with the source surface selected first, and the target last.
    
    Flags:
      - camera : cam                   (PyNode)        [create]
          Specify the camera to use for camera specific lighting calculations such as specular highlights or reflections.
    
      - fileFormat : ff                (unicode)       [create]
          The image format as a file extension (e.g. dds). This must be included once for every output map specified.
    
      - filename : fn                  (unicode)       [create]
          The filename to use when creating the map. This must be included once for every output map specified.
    
      - filterSize : fs                (float)         [create]
          The filter size to use in pixels. Larger values (e.g. over 2.0) will produce smoother/softer results, while values
          closer to 1.0 will produce sharper results.
    
      - filterType : ft                (int)           [create]
          The filter type to use. 0 is a Guassian filter, 1 is a triangular filter, 2 is a box filter.
    
      - flipU : fu                     (bool)          [create]
          Flip the U coordinate of the generated image.
    
      - flipV : fv                     (bool)          [create]
          Flip the V coordinate of the generated image.
    
      - ignoreMirroredFaces : imf      (bool)          [create]
          Stops reverse wound (i.e. mirrored) faces from contributing to the map generation.
    
      - ignoreTransforms : it          (bool)          [create]
          Controls whether transforms are used (meaning the search is performed in worldspace), or not (meaning the search is
          performed in object space).
    
      - mapHeight : mh                 (int)           [create]
          Pixel width of the generated map. This must be included once for every output map specified.
    
      - mapMaterials : mm              (bool)          [create]
          Where appropriate (e.g. normal maps), this controls whether the material should be included when sampling the map
          attribute. This must be included once for every output map specified.
    
      - mapOutput : mo                 (unicode)       [create]
          Specifies a new output map to create. One of normal, displacementdiffuseRGB, litAndShadedRGB, or alpha
    
      - mapSpace : sp                  (unicode)       [create]
          The space to generate the map in. Valid keyword is object. Default is tangent space. This must be included once for
          every output map specified.
    
      - mapWidth : mw                  (int)           [create]
          Pixel width of the generated map. Some output image formats require even or power of 2. This must be included once for
          every output map specified.
    
      - maxSearchDistance : msd        (float)         [create]
          Controls the maximum distance away from a target surface that will be searched for source surfaces. A value of 0
          indicates no limit. When generated maps include artifacts from the other sideof an object, try setting this value to a
          distance approximately equal to the radius of the object. If this flag is included, it must be included once for every
          target.
    
      - maximumValue : max             (float)         [create]
          The maximum value to include in the map. This allows control of how floating point values (like displacement) are
          quantised into integer image formats.
    
      - overscan : os                  (int)           [create]
          The number of additional pixels to render around UV borders. This will help to minimise texel filtering artifacts on UV
          seams. When mipmaps are going to be generated for the texture a higher value may be necessary (in addition to a
          filterSize greater than 1).
    
      - searchCage : sc                (unicode)       [create]
          Specifies a search envelope surface to use as a search guide when looking for source surfaces. If this flag is included,
          it must be included once for every target.
    
      - searchMethod : sm              (int)           [create]
          Controls the search method used to match sample points on a target surface to points on the sources. 0 is closest to
          envelope, 1 is prefer any intersection inside envelope to intersections outside it, and 2 is only use intersections
          inside envelope.
    
      - searchOffset : so              (float)         [create]
          Specifies a fixed offset from a target surface to use as the starting point when looking for source surfaces. This value
          is only used when no search cage is specified for a given target. If this flag is included, it must be included once for
          every target.
    
      - shadows : sh                   (bool)          [create]
          Where appropriate (e.g. lit and shaded), this controls whether shadows are included in the calculation. Currently only
          depth map shadows are supported.
    
      - source : s                     (unicode)       [create]
          Specifies a surface to use as a sampling source
    
      - sourceUVSpace : sus            (unicode)       [create]
          Specifies that the transfer of data between the surfaces should be done in UV space and specifies the name of the UV set
          on the source surface(s) that should be used as the transfer space.
    
      - superSampling : ss             (int)           [create]
          Controls the number of sampling points calculated for each output value. The algorithm will use 2 ^ n squared samples
          for each point (so a value of 0 will use a single sample, while a value of 3 will calculate 64 samples for each point).
    
      - target : t                     (unicode)       [create]
          Specified a surface to sample output information for.
    
      - targetUVSpace : tus            (unicode)       [create]
          Specifies that the transfer of data between the surfaces should be done in UV space and specifies the name of the UV set
          on the target surface(s) that should be used as the transfer space.
    
      - useGeometryNormals : ugn       (bool)          [create]
          Controls whether geometry or surface normals are used for surface searching. Using geometry normals will ensure a smooth
          mapping but can introduce distorted mappings where there are large distances between the source and target surfaces.
          Surface normals can introduce overlapping or discontinuous mappings, but does allow map distortion to be influenced by
          surface normal direction.
    
      - uvSet : uv                     (unicode)       [create]
          The name of the UV set to use when creating output maps. If this flag is included, it must be included once for every
          target.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.surfaceSampler`
    """

    pass


def tumble(*args, **kwargs):
    """
    The tumble command revolves the camera(s) by varying the azimuth and elevation angles in the perspective window. When
    both the azimuth and the elevation angles are supplied on the command line, the camera is firstly tumbled for the
    azimuth angle, then tumbled for the elevation angle. When no camera name is supplied, this command is applied to the
    camera in the active view. The camera's rotate pivot will override a specified pivot point if the rotate pivot is not at
    the camera's eye point.
    
    (<function tumble at 0x154ae7668>, <function addCmdDocsCallback at 0x1546e3578>, ('tumble', ''), {})
    
    Flags:
      - azimuthAngle : aa              (float)         [create]
          Degrees to change the azimuth angle.
    
      - elevationAngle : ea            (float)         [create]
          Degrees to change the elevation angle.
    
      - localTumble : lt               (int)           [create]
          Describes what point the camera will tumble around: 0 for the camera's tumble pivot, 1 for the camera's center of
          interest, and 2 for the camera's local axis, offset by its tumble pivot.
    
      - pivotPoint : pp                (float, float, float) [create]
          Three dimensional point used as the pivot point in the world space.
    
      - rotationAngles : ra            (float, float)  [create]
          Two values in degrees to change the azimuth and elevation angles.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.tumble`
    """

    pass


def renderManip(*args, **kwargs):
    """
    This command creates manipulators for cameras or lights.                 In query mode, return type is based on queried
    flag.
    
    Flags:
      - camera : cam                   (bool, bool, bool, bool, bool) [query,edit]
          Query or edit the visiblity status of the component camera manipulators. The order of components are: cycling index,
          center of interest, pivot, clipping planes, and unused.
    
      - light : lt                     (bool, bool, bool) [query,edit]
          Query or edit the visiblity status of the component light manipulators. The order of components are: cycling index,
          center of interest, and pivot.
    
      - spotLight : slt                (bool, bool, bool, bool, bool, bool, bool) [query,edit]
          Query or edit the visiblity status of the component spot light manipulators. The order of components are: cycling index,
          center of interest, pivot, cone angle, penumbra, look through barn doors, and decay regions.
    
      - state : st                     (bool)          [query,edit]
          Query or edit the state of manipulators on an camera, ambient light, directional light, point light, or spot light. This
          flag's default value is on.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.renderManip`
    """

    pass


def shadingNetworkCompare(*args, **kwargs):
    """
    This command allows you to compare two shading networks.
    
    Flags:
      - byName : nam                   (bool)          [create]
          Indicates whether the comparison should consider node names. If true, two shading networks will be considered equivalent
          only if the names of corresponding nodes are the same, ignoring namespaces. If false, two shading networks will be
          considered equivalent even if corresponding nodes are named differently. Default is 'false'.
    
      - byValue : val                  (bool)          [create]
          Indicates whether the comparison should consider the values of unconnected attributes. If true, two shading networks
          will be considered equivalent only if corresponding, unconnected attributes are the same type and have the same value.
          Only attributes of type 'int', 'bool', 'float', and 'string' will have their values compared. If false, two shading
          networks will be considered equivalent even if corresponding, unconnected attributes have different values or are
          different types. Default is 'true'.
    
      - delete : delete                (bool)          [create]
          Deletes the specified comparison from memory.
    
      - equivalent : eq                (bool)          [query]
          Returns an int. 1 if the shading networks in the specified comparison are equivalent. 0 otherwise.
    
      - network1 : n1                  (bool)          [query]
          Returns a string[]. Returns an empty string array if the shading networks in the specified comparison are not
          equivalent. Otherwise returns the nodes in the first shading network.
    
      - network2 : n2                  (bool)          [query]
          Returns a string[]. Returns an empty string array if the shading networks in the specified comparison are not
          equivalent. Otherwise returns the nodes in the second shading network.
    
      - upstreamOnly : up              (bool)          [create]
          Indicates whether the comparison should consider nodes which are connected downstream from shading network nodes. If
          true, only those nodes which are upstream from the shading group will be considered. If, following only downstream
          connections, there is no connection path from a node to one of the shader attributes on the shading group, the node will
          not be considered. If false, a node will be considered if a connection path can found, following either upstream or
          downstream connections, which terminates with an input connection to one of the shading groups shader attributes. These
          dangling nodes do not directly contribute to the color, displacement, or volume characteristics of the shading group.
          Default is 'false'.                             Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.shadingNetworkCompare`
    """

    pass


def convertSolidTx(*args, **kwargs):
    """
    Command to convert a texture on a surface to a file texture. The first argument is a rendering node or attribute. If
    only the node is specified, the outColor attribute will be sampled. If the node does not have an outColor attribute, the
    first attribute on the node which is: readable, not writable, not hidden, connectable, and not a multi is used. If
    lighting is to be baked, a shading group must be specified as the texture. The current selection will be used if a
    texture and surface are not specified. An image file will be generated for each object and stored in your image segment
    of your project. The filename will be formatted using the texture and surface names as follows: However, if force is off
    and there is a name collision a version number will be determined and the filename will be formatted as follows:
    
    Flags:
      - alpha : al                     (bool)          [create]
          Specify whether to compute the transparency when baking lighting. The conversion will sample both the color and
          transparency of the shading network; the alpha channel of the file texture will be set to correspond to the result from
          sampling the transparency. By default transparency is not computed.
    
      - antiAlias : aa                 (bool)          [create]
          Perform anti-aliasing on the resulting image. Convert solid texture will generally take four times longer than without
          anti-aliasing. By default this flag is off.
    
      - backgroundColor : bc           (int, int, int) [create]
          Set the background color to a specific value. Default is to use the shader default color to fill the background. Valid
          values range from 0 to 255 if the pixel format is 8 bits per channel, or 0 to 65535 if the pixel format is 16 bits per
          channel. This flag automatically sets -backgroundMode to color. Default is black: 0 0 0.
    
      - backgroundMode : bm            (unicode)       [create]
          Defines how the background of the texture should be filled. Three modes are available: shaderor 1: uses the default
          shader color. coloror 2: uses the color given by -backgroundColor flag. extendor 3: extends outwards the color along the
          seam edges. Default is shader.
    
      - camera : cam                   (PyNode)        [create]
          Specify a camera to use in baking lighting. If a camera is not specified the camera in the active view will be used.
    
      - componentRange : cr            (bool)          [create]
          If one or more components have been selected to use, then if this flag is set, then the uv range of the components is
          used to fit into the texture map resolution. By default this flag is set to false.
    
      - doubleSided : ds               (bool)          [create]
          Specify whether the sampler should flip the surface normal if the sample point faces away from the camera. Note:
          flipping the normal will make the result dependent on the camera (ie. one camera may flip normals where different camera
          wouldn't). It's not recommended that doubleSided be used in combination with shadows. By default this flag is false.
    
      - fileFormat : fil               (unicode)       [create]
          File format to be used for output. IFF is the default if unspecified. Other valid formats are:als: Alias PIXcin:
          Cineoneps: EPSgif: GIFiff: Maya IFFjpg: JPEGyuv: Quantelrla: Wavefront RLAsgi: SGIsi: SoftImage (.pic)tga: Targatif:
          TIFFbmp: Windows Bitmap
    
      - fileImageName : fin            (unicode)       [create]
          Specify the output path and name of file texture image. If the file name doesn't contain a directory separator, the
          image will be written to source images of the current project. The file will not be versioned if it already exists.
    
      - fillTextureSeams : fts         (bool)          [create]
          Specify whether or not to overscan the polygon beyond its outer edges, when creating the file texture, in order to fill
          the texture seams. Default is true.
    
      - force : f                      (bool)          [create]
          If the output image already exists overwrite it. By default this flag is off.
    
      - fullUvRange : fur              (bool)          [create]
          Sample using the full uv range of the surface. This flag cannot be used with the -uvr flag. A 2D texture placement node
          will be created and connected to the file texture. The placement's translate and coverage will be set according to the
          full UV range of the surface.
    
      - name : n                       (unicode)       [create]
          Set the name of the file texture node. Name conflict resolution will be used to determine valid names when multiple
          objects are specified.
    
      - pixelFormat : pf               (unicode)       [create]
          Specifies the pixel format of the image. Note that not all file formats support all pixel formats. Available options: 8:
          8 bits per channel, unsigned (0-255) 16: 16 bits per channel, unsigned (0-65535) Default is 8.
    
      - resolutionX : rx               (int)           [create]
          Set the horizontal image resolution. If this flag is not specified, the resolution will be set to 256.
    
      - resolutionY : ry               (int)           [create]
          Set the vertical image resolution. If this flag is not specified, the resolution will be set to 256.
    
      - reuseDepthMap : rdm            (bool)          [create]
          Specify whether or not to reuse all the generated dmaps. Default is false.
    
      - samplePlane : sp               (bool)          [create]
          Specify whether to sample using a virtual plane. This virtual plane has texture coordinates in the rectangle defined by
          the -samplePlaneRange flag. If the -samplePlaneRange flag is not set then the virtual plane defaults to having texture
          coordinates in the (0,0) to (1,1) square. If this option is set than all surface based arguments will be ignored.
    
      - samplePlaneRange : spr         (float, float, float, float) [create]
          Specify the uv range of the texture coordinates used to sample if the -samplePlane option is set. There are four
          arguments corresponding to uMin, uMax, vMin and vMax. By default the virtual plane is from uMin 0 to uMax 1, and vMin 0
          to vMax 1.
    
      - shadows : sh                   (bool)          [create]
          Specify whether to compute shadows when baking lighting. Disk based shadow maps will be used. Only lights with depth map
          shadows enabled will contribute to the shading. By default shadows are not computed.
    
      - uvBBoxIntersect : ubi          (bool)          [create]
          This flag is obsolete.
    
      - uvRange : uvr                  (float, float, float, float) [create]
          Specify the uv range in which samples will be computed. There are four arguments corresponding to uMin, uMax, vMin and
          vMax. Each value should be specified based on the surface's uv space. A 2D texture placement node will be created and
          connected to the file texture. The placement's frame translate and coverage will be set according to the uv range
          specified. By default the entire uv range of the surface will be used.
    
      - uvSetName : uv                 (unicode)       [create]
          Specify which uv set has to be used as the driving parametrization for convert solid.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.convertSolidTx`
    """

    pass



