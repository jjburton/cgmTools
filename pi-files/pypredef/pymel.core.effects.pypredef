def air(*args, **kwargs):
    """
    The air field simulates the effects of moving air. The affected objects will be accelerated or decelerated so that their
    velocities match that of the air. With the '-vco true' flag thrown, only accelerations are applied. By parenting an air
    field to a moving part of an object (ie. a foot of a character) and using '-i 1 -m 0 -s .5 -vco true' flags, one can
    simulate the movement of air around the foot as it moves, since the TOTAL velocity vector of the field would be only
    based on the movement of the foot. This can be done while the character walks through leaves or dust on the ground. For
    each listed object, the command creates a new field. The transform is the associated dependency node. Use connectDynamic
    to cause the field to affect a dynamic object. If fields are created,  this command returns the field names. If a field
    was queried, the results of the query are returned. If a field was edited, the field name is returned. If the -pos flag
    is specified, a field is created at the position specified. If not, if object names are provided or the active selection
    list is non-empty, the command creates a field for every object in the list and calls addDynamic to add it to the
    object; otherwise the command defaults to -pos 0 0 0. Setting the -pos flag with objects named on the command line is an
    error.
    
    Flags:
      - attenuation : att              (float)         [query,edit]
          Attentuation rate of field The air field attenuates so as to taper the field's magnitude to zero when the maximum
          distance is reached. Thus, attenuation has no effect unless useMaxDistance is true and a positive maximum distance has
          been set.
    
      - directionX : dx                (float)         [query,edit]
    
      - directionY : dy                (float)         [query,edit]
    
      - directionZ : dz                (float)         [query,edit]
          Direction that the air will try to match the affected particles' velocity to. NOTE: This is not the velocity; this is
          only the direction. Use the -s flag to set the speed.
    
      - enableSpread : es              (bool)          [query,edit]
          This tells the system whether or not to use the spread angle given by '-sp'. If this is 'false' then all connected
          objectswithin the maximum distance will be affected. Also, if this is set to 'false', all affected objects are forced to
          match their velocities along the direction vector. If this is set to 'true' and spread is used, then the direction of
          the force is along the direction from the field to the object.
    
      - fanSetup : fs                  (bool)          [edit]
          Similar to 'windSetup' except that the effects of a fan or a person blowing air are approximated. The user can pass the
          same flags on the command line to adjust them from the defaults. These are the values that get set to approximate a
          'fan': inheritVelocity 1.0 inheritRotation true componentOnly false enableSpread true spread .5 (45 degrees from center
          )
    
      - inheritRotation : iro          (bool)          [query,edit]
          If this is set to 'true', then the direction vector described with -dx, -dy, and -dz will be considered local to the
          owning object. Therefore, if the owning object's transform undergoes any rotation (by itself or one of its parents), the
          direction vector of the air field will undergo that same rotation.
    
      - inheritVelocity : iv           (float)         [query,edit]
          Amount (from 0 to 1) of the field-owner's velocity added to the vector determined by the direction and speed flags. The
          combination of these two vectors makes up the TOTAL velocity vector for the air field. This allows the air to be
          determined directly by the motion of the owning object.
    
      - magnitude : m                  (float)         [query,edit]
          The speed along the direction vector that the air is moving. Use this in conjunction with the -dx -dy -dz flags.
    
      - maxDistance : mxd              (float)         [query,edit]
          Maximum distance at which field is exerted. -1 indicates that the field has no maximum distance.
    
      - name : n                       (unicode)       [query,edit]
          name of field
    
      - perVertex : pv                 (bool)          [query,edit]
          Per-vertex application. If this flag is set true, then each individual point (CV, particle, vertex,etc.) of the chosen
          object exerts an identical copy of the force field. If this flag is set to false, then the force is exerted only from
          the geometric center of the set of points.
    
      - position : pos                 (float, float, float) [query,edit]
          Position in space where you want to place a field. The field then emanates from this position in space rather than from
          an object. Note that you can both use -pos (creating a field at a position) and also provide object names.
    
      - speed : s                      (float)         [query,edit]
          How fast the affected objects' speed reaches the speed (based on the -mag, -dx, -dy, -dz flags) of the air field. This
          value gets clamped internally to be between 0.0 and 1.0.  A value of 0.0 will make the air field have no effect. A value
          of 1.0 will try to match the air field's speed much quicker, but not necessarily immediately.
    
      - spread : sp                    (float)         [query,edit]
          This represents the angle from the direction vector within which objects will be affected. The values are in the range
          of 0 to 1. A value of 0 will result in an effect only exactly in front of the air field along the direction vector. A
          value of 1 will result in any object in front of the owning object, 90 degrees in all direction from the direction
          vector.
    
      - torusSectionRadius : tsr       (float)         [query,edit]
    
      - velocityComponentOnly : vco    (bool)          [query,edit]
          If this is 'false', the air will accelerate or decelerate the affected objects so that their velocities will eventually
          match the TOTAL velocity vector of the air field. If this is 'true', only ACCELERTION is applied to the affected objects
          so that their velocity component along the TOTAL velocity vector matches or is greater in magnitude than the TOTAL
          velocity vector. This will not slow objects down to match velocities, only speed them up to match components. This is
          most useful when using the -iv flag with a value 0.
    
      - volumeExclusion : vex          (bool)          [query,edit]
    
      - volumeOffset : vof             (float, float, float) [query,edit]
    
      - volumeShape : vsh              (unicode)       [query,edit]
    
      - volumeSweep : vsw              (float)         [query,edit]
    
      - wakeSetup : wks                (bool)          [edit]
          Like the 'windSetup' and 'fanSetup', 'wakeSetup' sets certain values in the field to approximate the movement of air
          near a moving object, such as  a character's foot or hand. The values that are set are: inheritVelocity 1.0
          inheritRotation false componentOnly true enableSpread false speed 0.0
    
      - windSetup : wns                (bool)          [edit]
          This will set some of the values above in a way that approximates the effects of a basic wind. This allows the user to
          then change certain values as he/she wishes on the same command line. First the preset values get set, and then any
          other flags that were passed get taken into account. These are the values that get set to approximate 'wind':
          inheritVelocity 0.0 inheritRotation true componentOnly false enableSpread false                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.air`
    """

    pass


def radial(*args, **kwargs):
    """
    A radial field pushes objects directly towards or directly away from it, like a magnet. The transform is the associated
    dependency node. Use connectDynamic to cause the field to affect a dynamic object. If fields are created, this command
    returns the names of each of the fields. If a field was queried, the results of the query are returned. If a field was
    edited, the field name is returned. If object names are provided or the active selection list is non-empty, the command
    creates a field for every object in the list and calls addDynamic to add it to the object. If the list is empty, the
    command defaults to -pos 0 0 0. Setting the -pos flag with objects named on the command line is an error.
    
    Flags:
      - attenuation : att              (float)         [query,edit]
          Attentuation rate of field
    
      - magnitude : m                  (float)         [query,edit]
          Strength of field.
    
      - maxDistance : mxd              (float)         [query,edit]
          Maximum distance at which field is exerted. -1 indicates that the field has no maximum distance.
    
      - name : n                       (unicode)       [query,edit]
          name of field
    
      - perVertex : pv                 (bool)          [query,edit]
          Per-vertex application. If this flag is set true, then each individual point (CV, particle, vertex,etc.) of the chosen
          object exerts an identical copy of the force field. If this flag is set to false, then the froce is exerted only from
          the geometric center of the set of points.
    
      - position : pos                 (float, float, float) [query,edit]
          Position in space where you want to place a field. The field then emanates from this position in space rather than from
          an object. Note that you can both use -pos (creating a field at a position) and also provide object names.
    
      - torusSectionRadius : tsr       (float)         []
    
      - type : typ                     (float)         [query,edit]
          Type of radial field (0 - 1).  This controls the algorithm by which the field is attenuated. Type 1, provided for
          backward compatibility, specifies the same algorithm as Alias | Wavefront Dynamation. A value between 0 and 1 yields a
          linear blend.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
      - volumeExclusion : vex          (bool)          []
    
      - volumeOffset : vof             (float, float, float) []
    
      - volumeShape : vsh              (unicode)       []
    
      - volumeSweep : vsw              (float)         []
    
    
    Derived from mel command `maya.cmds.radial`
    """

    pass


def getFluidAttr(*args, **kwargs):
    """
    Returns values of built-in fluid attributes such as density, velocity, etc., for individual grid cells or for all cells
    in the grid.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          Specifies the fluid attribute for which to display values.  Valid attributes are force, velocity, density, falloff,
          fuel, color, and temperature.  (Note that getting force values is an alternate way of getting velocity values at one
          time step.)
    
      - lowerFace : lf                 (bool)          [create]
          Only valid with -at velocity.  Since velocity values are stored on the edges of each voxel and not at the center, using
          voxel based indices to set velocity necessarily affects neighboring voxels.  Use this flag to only set velocity
          components on the lower left three faces of a voxel, rather than all six.
    
      - xIndex : xi                    (int)           [create]
          Only return values for cells with this X index
    
      - xvalue : x                     (bool)          []
          Only get the first component of the vector-valued attribute specified by the -at/attributeflag.
    
      - yIndex : yi                    (int)           [create]
          Only return values for cells with this Y index
    
      - yvalue : y                     (bool)          []
          Only get the second component of the vector-valued attribute specified by the -at/attributeflag.
    
      - zIndex : zi                    (int)           [create]
          Only return values for cells with this Z index
    
      - zvalue : z                     (bool)          []
          Only get the third component of the vector-valued attribute specified by the -at/attributeflag.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.getFluidAttr`
    """

    pass


def setDynamic(*args, **kwargs):
    """
    setDynamic sets the isDynamic attribute of particle objects on or off.  If no objects are specified, it sets the
    attribute for any selected objects.  If -all is thrown, it sets the attribute for all particle objects in the scene. By
    default it sets the attribute true (on); if the -off flag is thrown, it sets the attribute false (off). WARNING:
    setDynamic is obsolescent.  This is the last version of Maya in which it will be supported.
    
    Flags:
      - allOnWhenRun : awr             (bool)          [create]
          Obsolete, no longer suppported or necessary.
    
      - disableAllOnWhenRun : dwr      (bool)          [create]
          Obsolete, no longer suppported or necessary.
    
      - setAll : all                   (bool)          [create]
          Set for all objects.
    
      - setOff : off                   (bool)          [create]
          Sets isDynamic false.
    
      - setOn : on                     (bool)          [create]
          Sets isDynamic true.  This flag is set by default.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.setDynamic`
    """

    pass


def resampleFluid(*args, **kwargs):
    """
    A command to extend the fluid grid, keeping the voxels the same size, and keeping the existing contents of the fluid in
    the same place. Note that the fluid transform is also modified to make this possible.            In query mode, return
    type is based on queried flag.
    
    Flags:
      - resampleDepth : rd             (int)           [create,query,edit]
          Change depth resolution to this value
    
      - resampleHeight : rh            (int)           [create,query,edit]
          Change height resolution to this value
    
      - resampleWidth : rw             (int)           [create,query,edit]
          Change width resolution to this value                              Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.resampleFluid`
    """

    pass


def particleExists(*args, **kwargs):
    """
    This command is used to query if a particle or soft object with the given name exists. Either the transform or shape
    name can be used as well as the name of the soft object.
    
    
    Derived from mel command `maya.cmds.particleExists`
    """

    pass


def saveInitialState(*args, **kwargs):
    """
    saveInitialState saves the current state of dynamics objects as the initial state.  A dynamic object is a particle
    shape, rigid body, rigid constraint or rigid solver.  If no objects are specified, it saves the initial state for any
    selected objects. It returns the names of the objects for which initial state was saved.
    
    Flags:
      - attribute : atr                (unicode)       [create]
          Save the initial state of the specified attribute only. This is a multi-use flag.
    
      - saveall : all                  (bool)          [create]
          Save the initial state for all dynamics objects in the scene.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.saveInitialState`
    """

    pass


def addPP(*args, **kwargs):
    """
    Adds per-point (per-cv, per-vertex, or per-particle) attribute capability for an attribute of an emitter or field.  The
    -atr flag identifies the attribute.  If no attribute is named, addPP returns a warning and does nothing. The command
    adds any other necessary attributes wherever they are needed, and makes all necessary connections.  If any of the
    attributes already exist, the command simply connects to them.  The command also toggles any relevant attributes in the
    emitter or field to indicate that per-point capability is being used. The command adds a separate per-point attribute to
    the owning object for each emitter/field.  For example, for emission rate, there is a separate ratePP for each emitter.
    These attributes are named according to the convention emitter/field nameattr namePP.  For example, if a particle shape
    owned an emitter smoke, that shape would get attribute smokeRatePP.The name of the object must be the emitter or field
    for which per-point capability is to be added (or the name of its parent transform).  The addPP command adds the per-
    point capability for that emitter or field but not for any others owned by the same object.  If per-point capability is
    not supported for a named object, the command will trigger a warning, but will continue executing for any other objects
    which were valid. If no objects are named, addPP uses any objects in the current selection list for which the specified
    attribute is applicable.  (For example, it would add per-point rate for all selected emitters.) If addPP detects that
    the owner object has left-over attributes from a deleted emitter, it will remove those attributes before adding the new
    ones.  Thus, you can delete the emitter, make a new one, and run addPP again, and addPP will clean up after the deleted
    emitter.  This is most commonly used if you have a geometry emitter and then decide to change the geometry.  Likewise,
    if addPP detects that some cvs or vertices have been added to the geometry, then it will expand the corresponding multi-
    attributes as necessary.  However, if it detects that some cvs/vertices have been removed, it will not remove any
    entries from the multi.  See the user manual for more discussion.
    
    Modifications:
      - returns a list of PyNode objects
    
    Flags:
      - attribute : atr                (unicode)       [create]
          Name of attribute to which you wish to add PP capability. Currently the only attribute supported is rate (for emitters).
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.addPP`
    """

    pass


def addDynamic(*args, **kwargs):
    """
    Makes the objectspecified as second argument the source of an existing field or emitter specified as the first argument.
    In practical terms, what this means is that a field will emanate its force from its owner object, and an emitter will
    emit from its owner object. addDynamic makes the specified field or emitter a child of the owner's transform (adding it
    to the model if it was not already there), and makes the necessary attribute connections. If either of the arguments is
    omitted, addDynamic searches the selection list for objects to use instead. If more than one possible owner or
    field/emitter is selected, addDynamic will do nothing. If the specified field/emitter already has a source, addDynamic
    will remove the current source and replace it with the newly specified source. If a subset of the owner object's
    cvs/particles/vertices is selected, addDynamic will add the field/emitter to that subset only.
    
    Modifications:
      - returns a list of PyNode objects
    
    
    Derived from mel command `maya.cmds.addDynamic`
    """

    pass


def expression(*args, **kwargs):
    """
    This command describes an expression that belongs to the current scene. The expression is a block of code of unlimited
    length with a C-like syntax that can perform conversions, mathematical operations, and logical decision making on any
    numeric attribute(s) in the scene.  One expression can read and alter any number of numeric attributes.  Theoretically,
    every expression in a scene can be combined into one long expression, but it is recommended that they are separated for
    ease of use and editing, as well as efficiency.If this command is being sent by the command line or in a script, then
    the user should be sure to embed escaped newlines (\n), tabs (\t) for clarity when reading them in the expression
    editor.  Also, quotes in an expression must be escaped (\) so that they are not confused by the system as the end of
    your string.  When using the expression editor, these characters are escaped for you unless they are already within
    quotes.Note, expressions that alter or use per-particle attributes of a particle shape should use the 'dynExpression'
    command.
    
    Flags:
      - alwaysEvaluate : ae            (int)           [create,query,edit]
          If this is TRUE (the default), then the expression will be evaluated whenever time changes regardless of whether the
          other inputs have changed, and an output is requested.  If it is FALSE, then the expression will only be evaluated if
          one or more of the inputs changes and an output is requested.  Note, if 'time' or 'frame' are inputs, then the
          expression will act as if this was set to TRUE.
    
      - animated : an                  (int)           [query,edit]
    
      - attribute : a                  (unicode)       [query,edit]
    
      - name : n                       (unicode)       [create,query,edit]
          Sets the name of the dependency graph node to use for the expression
    
      - object : o                     (unicode)       [create,query,edit]
          Sets the defaultobject for the expression.  This allows the expression writer to not type the object name for
          frequently-used objects.  See the examples below.
    
      - safe : sf                      (unicode)       [query]
          Returns true if no potential side effect can occurs running that expression. Safe expression will be optimized to
          evaluate only when needed even if flagged alwaysEvaluate.
    
      - shortNames : sn                (bool)          [create,query,edit]
          When used with the -q/query flag, tells the command to return the expression with attribute names as short as possible.
          The default is to return the FULL attribute name, regardless of how the user entered it into the expression, including
          the object names.  With this flag set, attribute names are returned as their short versions, and any attribute that
          belongs to the default object, if there is one specified, will not display the object's name.
    
      - string : s                     (unicode)       [create,query,edit]
          Set the expression string
    
      - timeDependent : td             (unicode)       [query]
          Returns true if expression refer to 'time' or 'frame' keywords. Those reference force the connection to time. If the
          expression is flagged as safe and not time dependend, then they will always evaluate on depend, even if alwaysEvaluate
          is on. Otherwise time change will dirty the expression.
    
      - unitConversion : uc            (unicode)       [query,edit]
          Insert specified unit conversion nodes at creation: all, none,or angularOnly.Default is all.For angularOnly, will insert
          unit conversion nodes only for angular attributes (allowing degrees-to-radians conversion).  This is for performance
          tuning. If queried, returns the option used when the expression was created or last edited.                  Flag can
          have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.expression`
    """

    pass


def fluidEmitter(*args, **kwargs):
    """
    Creates an emitter object. If object names are provided or if objects are selected, applies the emitter to the
    named/selected object(s)in the scene.  Fluid will then be emitted from each. If no objects are named or selected, or if
    the -pos option is specified, creates a positional emitter. If an emitter was created, the command returns the name of
    the object owning the emitter, and the name of emitter shape. If an emitter was queried, the command returns the results
    of the query.
    
    Flags:
      - cycleEmission : cye            (unicode)       [query,edit]
          Possible values are noneand frame.Cycling emission restarts the random number stream after a specified interval.  This
          can either be a number of frames or a number of emitted particles.  In each case the number is specified by the
          cycleInterval attribute. Setting cycleEmission to frameand cycleInterval to 1 will then re-start the random stream every
          frame. Setting cycleInterval to values greater than 1 can be used to generate cycles for games work.
    
      - cycleInterval : cyi            (int)           [query,edit]
          Specifies the number of frames or particles between restarts of the random number stream.  See cycleEmission.  Has no
          effect if cycleEmission is set to None.
    
      - densityEmissionRate : der      (float)         [query,edit]
          Rate at which density is emitted.
    
      - fluidDropoff : fdr             (float)         [query,edit]
          Fluid Emission Dropoff in volume
    
      - fuelEmissionRate : fer         (float)         [query,edit]
          Rate at which  is emitted.
    
      - heatEmissionRate : her         (float)         [query,edit]
          Rate at which density is emitted.
    
      - maxDistance : mxd              (float)         [query,edit]
          Maximum distance at which emission ends.
    
      - minDistance : mnd              (float)         [query,edit]
          Minimum distance at which emission starts.
    
      - name : n                       (unicode)       [query,edit]
    
      - position : pos                 (float, float, float) [query,edit]
          Positional emitter at world space location (x,y,z).
    
      - rate : r                       (float)         [query,edit]
          Rate at which particles emitted (can be non-integer). For point emission this is rate per point per unit time. For
          surface emission it is rate per square unit of area per unit time.
    
      - torusSectionRadius : tsr       (float)         [query,edit]
          Section radius for a torus volume.  Applies only to torus. Similar to the section radius in the torus modelling
          primitive.
    
      - type : typ                     (unicode)       [query,edit]
          Type of emitter. The choices are omni | dir | direction | surf | surface | curve | curv. The default is omni. The full
          definition of these types are: omnidirectional point emitter, directional point emitter, surface emitter, or curve
          emitter.
    
      - volumeOffset : vof             (float, float, float) [query,edit]
          Volume offset of the emitter.  Volume offset translates the emission volume by the specified amount from the actual
          emitter location.  This is in the emitter's local space.
    
      - volumeShape : vsh              (unicode)       [query,edit]
          Volume shape of the emitter.  Sets/edits/queries the field's volume shape attribute.  If set to any value other than
          none, determines a 3-D volume within which particles are generated. Values are: cube,sphere,cylinder,cone,torus.
    
      - volumeSweep : vsw              (float)         [query,edit]
          Volume sweep of the emitter.  Applies only to sphere, cone, cylinder, and torus.  Similar effect to the sweep attribute
          in modelling.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.fluidEmitter`
    """

    pass


def goal(*args, **kwargs):
    """
    Specifies the given objects as being goals for the given particle object.  If the goal objects are geometry, each
    particle in the particle object will each try to follow or match its position to that of a certain vertex/CV/lattice
    point of the goal.  If the goal object is another particle object, each particle will try to follow a paricle of the
    goal. In any other case, all the particles will try to follow the current location of the goal object's transform.  You
    can get this latter behavior for a geometry or particle object too by using -utr true. The goal weight can be keyframed.
    It lives on the particle object to which the goal was added and is a multi-attribute.
    
    Flags:
      - goal : g                       (unicode)       [create,query]
          This flag specifies string to be a goal of the particle object on the command line or the currently selected particle
          object.  This flag can be used multiple times to specify multiple goals for a particle object.  Query is for use by the
          attribute editor.
    
      - index : i                      (bool)          [query]
          Returns array of multi-attribute indices for the goals. Intended for use by the Attribute Editor.
    
      - useTransformAsGoal : utr       (bool)          [create]
          Use transform of specified object instead of the shape. Meaningful only for particle and geometry objects.  Can only be
          passed once, applies to all objects passed with -g.
    
      - weight : w                     (float)         [create]
          This specifies the goal weight as a value from 0 to 1.  A value of 0 means that the goal's position will have no effect
          on the particle object, while a weight of 1 will make the particle object try to follow the goal object exactly.  This
          flag can only be passed once and sets the weight for every goal passed with the -g/-goal flag.                  Flag can
          have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.goal`
    """

    pass


def stroke(*args, **kwargs):
    """
    The stroke command creates a new Paint Effects stroke node.
    
    Flags:
      - name : n                       (unicode)       [create]
          Sets the name of the stroke to the input string
    
      - pressure : pr                  (bool)          [create]
          On creation, allows the copying of the pressure mapping settings from the Paint Effects Tool. Default is false.
    
      - seed : s                       (int)           [create]
          Sets the random seed for this stroke.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.stroke`
    """

    pass


def dynExpression(*args, **kwargs):
    """
    This command describes an expression that belongs to the specified particle shape.  The expression is a block of code of
    unlimited length with a C-like syntax that can perform conversions, mathematical operations, and logical decision making
    on any numeric attribute(s) or per-particle attribute(s) in the scene.  One expression can read and alter any number of
    these attributes.  Every particle shape in your scene has three expressions, one for the runtimeBeforeDynamics, one for
    the runtimeAfterDynamics and one for creation time.  The create expression gets executed for every particle in the
    object whose age is 0.0.  The runtime expression gets executed for each particle with an age greater then 0.0.  Unlike
    expressions created with the expressioncommand, particle expressions always exist and are a part of the owning particle
    object's shape.  They default to empty strings, but they are always there.  Because of this, there is no need to use the
    '-e' flag.  Every call to the dynExpression command is considered an edit by default.  Per-particle attributes are those
    attributes of a particle shape that have a potentially different value for each particle in the object.  Examples of
    these include positionand velocity. If this command is being sent by the command line or in a script, then the user
    should be sure to embed escaped newlines (\n), tabs (\t) for clarity when reading them in the expression editor.  Also,
    quotes in an expression must be escaped (\) so that they are not confused by the system as the end of your string.  When
    using the expression editor, these characters are escaped for you unless they are already within quotes. This type of
    expression is executed during the evaluation of the dynamics.  If an output of the expression is requested before that,
    then the dynamics will be force to compute at that time.  If dynamics is disabled, then these expressions will have no
    effect.
    
    Flags:
      - creation : c                   (bool)          [create,query,edit]
          Tells the command that the string passed will be a creation expression for the particle shape.  This means that this
          expression will be executed when a particle is emitted or at the beginning of the scene for existing particles.
    
      - name : n                       (unicode)       []
    
      - runtime : r                    (bool)          []
    
      - runtimeAfterDynamics : rad     (bool)          [create,query,edit]
          Tells the command that the string passed will be a runtime expression for the particle shape.  This expression will be
          executed after dynamics whenever a particle's age is greater then zero (0).
    
      - runtimeBeforeDynamics : rbd    (bool)          [create,query,edit]
          Tells the command that the string passed will be a runtime expression for the particle shape.  This expression will be
          executed before dynamics whenever a particle's age is greater then zero (0).
    
      - string : s                     (unicode)       [create,edit]
          Set the expression string. This is queriable with the -q/query flag and the -rbd/runtimeBeforeDynamics, the
          -rab/runtimeAfterDynamics or the -c/creation flag.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.dynExpression`
    """

    pass


def emitter(*args, **kwargs):
    """
    Creates an emitter object. If object names are provided or if objects are selected, applies the emitter to the
    named/selected object(s)in the scene.  Particles will then be emitted from each. If no objects are named or selected, or
    if the -pos option is specified, creates a positional emitter. If an emitter was created, the command returns the name
    of the object owning the emitter, and the name of emitter shape. If an emitter was queried, the command returns the
    results of the query. Keyframeable attributes of the emitter node: rate, directionX, directionY, directionZ,
    minDistance, maxDistance, spread.
    
    Flags:
      - alongAxis : alx                (float)         [query,edit]
          Initial velocity multiplier in the direction along the central axis of the volume.  See the diagrams in the
          documentation.  Applies only to volume emitters.
    
      - aroundAxis : arx               (float)         [query,edit]
          Initial velocity multiplier in the direction around the central axis of the volume.  See the diagrams in the
          documentation.  Applies only to volume emitters.
    
      - awayFromAxis : afx             (float)         [query,edit]
          Initial velocity multiplier in the direction away from the central axis of the volume.  See the diagrams in the
          documentation.  Used only with the cylinder, cone, and torus volume emitters.
    
      - awayFromCenter : afc           (float)         [query,edit]
          Initial velocity multiplier in the direction away from the center point of a cube or sphere volume emitter. Used only
          with the cube and sphere volume emitters.
    
      - cycleEmission : cye            (unicode)       [query,edit]
          Possible values are noneand frame.Cycling emission restarts the random number stream after a specified interval.  This
          can either be a number of frames or a number of emitted particles.  In each case the number is specified by the
          cycleInterval attribute. Setting cycleEmission to frameand cycleInterval to 1 will then re-start the random stream every
          frame. Setting cycleInterval to values greater than 1 can be used to generate cycles for games work.
    
      - cycleInterval : cyi            (int)           [query,edit]
          Specifies the number of frames or particles between restarts of the random number stream.  See cycleEmission.  Has no
          effect if cycleEmission is set to None.
    
      - directionX : dx                (float)         [query,edit]
          x-component of emission direction. Used for directional emitters, and for volume emitters with directionalSpeed.
    
      - directionY : dy                (float)         [query,edit]
          y-component of emission direction. Used for directional emitters, and for volume emitters with directionalSpeed.
    
      - directionZ : dz                (float)         [query,edit]
          z-component of emission direction. Used for directional emitters, and for volume emitters with directionalSpeed.
    
      - directionalSpeed : drs         (float)         [query,edit]
          For volume emitters only, adds a component of speed in the direction specified by the directionX, Y, and Z attributes.
          Applies only to volume emitters. Does not apply to other types of emitters.
    
      - maxDistance : mxd              (float)         [query,edit]
          Maximum distance at which emission ends.
    
      - minDistance : mnd              (float)         [query,edit]
          Minimum distance at which emission starts.
    
      - name : n                       (unicode)       [query,edit]
    
      - needParentUV : nuv             (bool)          [query,edit]
          If aNeedParentUV is true, compute parentUV value from each triangle or each line segment, then send out to the target
          particle object. You also need to add parentU and parentV attributes to the particle object to store these values.
    
      - normalSpeed : nsp              (float)         [query,edit]
          Normal speed multiple for point emission. For each emitted particle, multiplies the component of the velocity normal to
          the surface or curve by this amount. Surface and curve emitters only.
    
      - position : pos                 (float, float, float) [query,edit]
          Positional emitter at world space location (x,y,z).
    
      - randomDirection : rnd          (float)         [query,edit]
          Magnitude of a random component of the speed from volume emission.
    
      - rate : r                       (float)         [query,edit]
          Rate at which particles emitted (can be non-integer). For point emission this is rate per point per unit time. For
          surface emission it is rate per square unit of area per unit time.
    
      - scaleRateByObjectSize : sro    (bool)          [query,edit]
          Applies to curve and surface emitters, only. If true, number of particles is determined by object size (area or length)
          times rate value.  If false, object size is ignored and the rate value is used without modification. The former is the
          way Maya behaved prior to version 3.0.
    
      - scaleSpeedBySize : ssz         (bool)          [query,edit]
          Indicates whether the scale of a volume emitter affects its velocity.
    
      - speed : spd                    (float)         [query,edit]
          Speed multiple.  Multiplies the velocity of the emitted particles by this amount. Does not apply to volume emitters.
          For that emitter type, use directionalSpeed.
    
      - speedRandom : srn              (float)         [query,edit]
          Identifies a range of random variation for the speed of each generated particle.  If set to a non-zero value, speed
          becomes the mean value of the generated particles, whose speeds vary by a random amount up to plus or minus
          speedRandom/2. For example, speed 5 and speedRandom 2 will make the speeds vary between 4 and 6.
    
      - spread : sp                    (float)         [query,edit]
          Random spread (0-1), as a fraction of 90 degrees, along specified direction.   Directional emitters only.
    
      - tangentSpeed : tsp             (float)         [query,edit]
          Tangent speed multiple for point emission. For each emitted particle, multiplies the component of the velocity tangent
          to the surface  or curve by this amount. Surface and curve emitters only.
    
      - torusSectionRadius : tsr       (float)         [query,edit]
          Section radius for a torus volume.  Applies only to torus. Similar to the section radius in the torus modelling
          primitive.
    
      - type : typ                     (unicode)       [query,edit]
          Type of emitter. The choices are omni | dir | direction | surf | surface | curve | curv. The default is omni. The full
          definition of these types are: omnidirectional point emitter, directional point emitter, surface emitter, or curve
          emitter.
    
      - volumeOffset : vof             (float, float, float) [query,edit]
          Volume offset of the emitter.  Volume offset translates the emission volume by the specified amount from the actual
          emitter location.  This is in the emitter's local space.
    
      - volumeShape : vsh              (unicode)       [query,edit]
          Volume shape of the emitter.  Sets/edits/queries the field's volume shape attribute.  If set to any value other than
          none, determines a 3-D volume within which particles are generated. Values are: cube,sphere,cylinder,cone,torus.
    
      - volumeSweep : vsw              (float)         [query,edit]
          Volume sweep of the emitter.  Applies only to sphere, cone, cylinder, and torus.  Similar effect to the sweep attribute
          in modelling.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.emitter`
    """

    pass


def particleFill(*args, **kwargs):
    """
    This command generates an nParticle system that fills the selected object with a grid of particles.
    
    Flags:
      - closePacking : cp              (bool)          [create]
          If this is on then the particles are positioned as closely as possible in a hexagonal close packing arrangement.
          Otherwise particles are packed in a uniform grid lattice.
    
      - doubleWalled : dw              (bool)          [create]
          This flag should be used if the thickness of the object to fill has been modeled( for example a mug ). Otherwise the
          particles will be created inside the wall. Note that doubleWalled will not handle some cases very well. For example a
          double walled donut shape may get the center region of the donut filled. In cases like this it may be better to make the
          internal wall a separate mesh then fill that without using doubleWalled.
    
      - maxX : mxx                     (float)         [create]
          The fill max bounds of the particles in X relative to the X bounds of the object. A value of zero is totally empty and
          one is totally full. The default value is 1, or fully filled.
    
      - maxY : mxy                     (float)         [create]
          The fill max bounds of the particles in Y relative to the Y bounds of the object. A value of zero is totally empty and
          one is totally full. The default value is 1, or fully filled.
    
      - maxZ : mxz                     (float)         [create]
          The fill max bounds of the particles in Z relative to the Z bounds of the object. A value of zero is totally empty and
          one is totally full. The default value is 1, or fully filled.
    
      - minX : mnx                     (float)         [create]
          The fill lower bounds of the particles in X relative to the X bounds of the object. A value of zero is totally full and
          one is totally empty. The default value is 0, or fully filled.
    
      - minY : mny                     (float)         [create]
          The fill lower bounds of the particles in Y relative to the Y bounds of the object. A value of zero is totally full and
          one is totally empty. The default value is 0, or fully filled.
    
      - minZ : mnz                     (float)         [create]
          The fill lower bounds of the particles in Z relative to the Z bounds of the object. A value of zero is totally full and
          one is totally empty. The default value is 0, or fully filled.
    
      - particleDensity : pd           (float)         [create]
          This controls the size of the particles. At a value of 1.0 the particle size will exactly match the grid spacing
          determined by the resolution parameter and the object bounds. Particles which overlap the surface will be rejected even
          if the center of the particle is inside.
    
      - resolution : rs                (int)           [create]
          This determines the total number of particles generated. It represent the resolution along the largest axis of the
          object's bounding box. For a cube shape the total potential particles will be the cube of the resolution. For other
          shapes it will be less. The default value for this flag is 10, so 1000 particles could be generated for a cube shape.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.particleFill`
    """

    pass


def dynExport(*args, **kwargs):
    """
    Export particle data to disk files. For cache export (-format cache), dynExport also sets three attributes of the
    current dynGlobals node.  It sets the useParticleRenderCache attribute to true, and the
    min/maxFrameOfLastParticleRenderCache attributes to correspond to the min and max frames. Exported .pda or .pdb files
    are assigned a name of form object name.frame.extension, where extensionis pdaor pdb.The naming convention for .pdc
    files is similar but does not use frame numbers, it uses a more precise representation of the time instead. By default,
    the pda and pdb formats export all per-particle attributes, and all integer or float type attributes except those which
    are hidden or not storable. (Exception: level of detail is not exported, by default) The pdc format exports all
    attributes which the particle object needs for its state cache. To specify only selected attributes, use the -atr flag
    (which is multi-use).  In general, it is recommended not to use this flag with pdc type, since you need all the
    attributes in order for the cache to be useful. dynExport exports data for the current frame, or for a range of frames
    specified with -mnf and -mxf. If you are not already at the start frame, dynExport will run up the scene for you. VERY
    VERY IMPORTANT NOTE:If you use dynExport in -prompt mode, it does NOT automatically force evaluation of your objects.
    You must do this yourself from your script.  The easiest way is to request each particle object's countattribute each
    frame.  You must request the count attribute for each object you want to export, because their solvers run independently
    of one another.  In interactive mode, objects WILL get evaluated automatically and you don't have to worry about any of
    this. When exporting a particle object whose particles are created from collisions involving particles in another
    particle object(s), you must make sure you simultaneously export all the particle objects involved in the dependency
    chain otherwise you will get an empty cache file. For non-per-particle attributes, pda and pdb formats write the
    identical value once for each particle.  The following types of non-per-particle attributes can be exported: float,
    double, doubleLinear, doubleAngle, byte, short, long, enum.  The first four are exported as Real(in PDB parlance), and
    the last four as Integer.In the pda and pdb formats, particleIdand particleId0are exported as Integer, and are exported
    under the names idand id0respectively.  All other attributes are exported under their long names.
    
    Flags:
      - allObjects : all               (bool)          [create]
          Ignore the selection list and export all particle objects. If you also specify an object name, the -all flag will be
          ignored.
    
      - attribute : atr                (unicode)       [create]
          Name of attribute to be exported. If any specified object does not have one of the specified attributes, dynExport will
          issue an error and not do the export.
    
      - format : f                     (unicode)       [create]
          Desired format: binarypdb), asciipda), or cachepdc). The pdc format is for use by the Maya particle system to cache
          particle data.  The pda and pdb format options are intended for pipelines involving other software (for example, sending
          the data to some program written in-house); Maya cannot read pda or pdb files. There is no formal description of the PDB
          format, but the ExploreMe/particles/readpdb directory contains the source and Makefile for a small, simple C program
          called readpdbwhich reads it. Note that you must compile and run readpdb on the platform which you exported the files
          on.
    
      - maxFrame : mxf                 (time)          [create]
          Ending frame to be exported.
    
      - minFrame : mnf                 (time)          [create]
          Starting frame to be exported. The export operation will play the scene through from min frame to max frame as it
          exports.
    
      - onlyUpdateParticles : oup      (bool)          []
    
      - overSampling : os              (int)           [create]
          OverSampling to be used during export.
    
      - path : p                       (unicode)       [create]
          This option allows you to specify a subdirectory of the workspace particlesdirectory where you want the exported files
          to be stored. By default, files are stored in the workspace particles directory, i.e., -path is relative to that
          directory. Please Read This: This is a change from previous versions of Maya in which the path was relative to the
          workspace root directory.) You can set the particlesdirectory anywhere you want using the project window or workspace
          -fr command. (In this way, you can use an absolute path for export). The -path flag cannot handle strings which include
          /or \, in other words, it lets you go down only one level in the directory hierarchy. If you specify a path which
          doesn't exist, the action will create it if possible; if it can't create the path it will warn you and fail. If you are
          using a project for which a particle data directory is not defined, dynExport will create a default one called
          particlesand add it to your workspace.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.dynExport`
    """

    pass


def uniform(*args, **kwargs):
    """
    A uniform field pushes objects in a fixed direction.  The field strength, but not the field direction, depends on the
    distance from the object to the field location. The transform is the associated dependency node. Use connectDynamic to
    cause the field to affect a dynamic object. If fields are created, this command returns the names of each of the fields.
    If a field was queried, the results of the query are returned. If a field was edited, the field name is returned. If
    object names are provided or the active selection list is non-empty, the command creates a field for every object in the
    list and calls addDynamic to add it to the object. If the list is empty, the command defaults to -pos 0 0 0. Setting the
    -pos flag with objects named on the command line is an error.
    
    Flags:
      - attenuation : att              (float)         [query,edit]
          Attentuation rate of field
    
      - directionX : dx                (float)         [query,edit]
          X-component of direction.
    
      - directionY : dy                (float)         [query,edit]
          Y-component of direction.
    
      - directionZ : dz                (float)         [query,edit]
          Z-component of direction
    
      - magnitude : m                  (float)         [query,edit]
          Strength of field.
    
      - maxDistance : mxd              (float)         [query,edit]
          Maximum distance at which field is exerted. -1 indicates that the field has no maximum distance.
    
      - name : n                       (unicode)       [query,edit]
          name of field
    
      - perVertex : pv                 (bool)          [query,edit]
          Per-vertex application. If this flag is set true, then each individual point (CV, particle, vertex,etc.) of the chosen
          object exerts an identical copy of the force field. If this flag is set to false, then the force is exerted only from
          the geometric center of the set of points.
    
      - position : pos                 (float, float, float) [query,edit]
          Position in space where you want to place a field. The gravity then emanates from this position in space rather than
          from an object. Note that you can both use -pos (creating a field at a position) and also provide object names.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - torusSectionRadius : tsr       (float)         [query,edit]
    
      - volumeExclusion : vex          (bool)          [query,edit]
    
      - volumeOffset : vof             (float, float, float) [query,edit]
    
      - volumeShape : vsh              (unicode)       [query,edit]
    
      - volumeSweep : vsw              (float)         [query,edit]
    
    
    Derived from mel command `maya.cmds.uniform`
    """

    pass


def emit(*args, **kwargs):
    """
    The emitaction allows users to add particles to an existing particle object without the use of an emitter.  At the same
    time, it allows them to set any per-particle attribute for the particles that are created with the action.The particles
    created do not become a part of the initial state for the particle object, and will disappear when the scene is rewound
    unless they are saved into the initial state by the user explicitly.  In addition, a particle object will accept
    particles from an emit action ONLY at frames greater than or equal to its start frame.  For example, if you want to use
    the emit action to create particles at frame -5, you must set startFrame for that particle shape to -5 or less.Unlike
    many commands or actions, the emit action uses the order of its flags as important information as to how it works.  The
    -objectand -positionflags can appear anywhere in the argument list.  The -attributeand the value flags are interpreted
    based on their order.  Any value flags after an -attribute flag and before the next -attribute flag will set the values
    for the attribute specified by the closest -attribute flag before them in the argument list.  See the Examplessection
    below for more detail on how these flags work.Currently, no creation expression is executed for the new particles unless
    they are created from within a particle expression defined with the dynExpressioncommand or the Expression Editor.  If
    you want any particular values put into the particles at the time they are created, then those values should be set
    using the -attribute, -vectorValue, and -floatValueflags.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          Specifies the attribute on the particle object that any value flags following it and before the next -attribute flag
          will be associated with.  The same attribute can be specified later in the command to pick up where the first one left
          off. The attributes used must be per-particle attributes.  This will accept both long and short names for the
          attributes. Note the per-particle attribute must already exist on the particle object prior to being specified via this
          command flag.
    
      - floatValue : fv                (float)         [create]
          Sets the float value to be used for the currentattribute of the currentparticle.  By current attribute, it is meant the
          attribute specified by the most recent -attribute flag.  By current particle, it is meant the particle in the list of
          -position flags that corresponds to the number of values that  have been set for the currentattribute.  If the current
          attribute is a vector-per-particle attribute, then the float value specified will be used for all three components of
          the vector.
    
      - object : o                     (unicode)       [create]
          This flag takes the name of a particleShape or the transform directly above it in the DAG as its parent.  It specifies
          which object to add the particles to.  This flag must be passed, as the selection list is ignored for this action.
    
      - position : pos                 (float, float, float) [create]
          Specifies the positions in the particle object's space (usually world space) where the particles are to be created. One
          particle is created for each occurence of this flag.
    
      - vectorValue : vv               (float, float, float) [create]
          Sets the vector value to be used for the currentattribute of the currentparticle.  By current attribute, it is meant the
          attribute specified by the most recent -attribute flag.  By current particle, it is meant the particle in the list of
          -position flags that corresponds to the number of values that have been set for the currentattribute.  If the current
          attribute is a float-per-particle attribute, then the length of the vector described by this flag will be used.  The
          length is described as SQR( xVal2+ yVal2+ zVal2.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.emit`
    """

    pass


def dynControl(*args, **kwargs):
    """
    Flags:
      - autoCreate : ac                (bool)          []
    
      - oversample : os                (int)           []
    
      - particleCache : pc             (bool)          []
    
      - particleLOD : pld              (float)         []
    
      - particlesOn : po               (bool)          []
    
      - rigidOn : ro                   (bool)          []
    
      - seed : sd                      (int)           []
    
      - startTime : st                 (time)          []
    
      - traceDepth : td                (int)           []
    
    
    Derived from mel command `maya.cmds.dynControl`
    """

    pass


def constrain(*args, **kwargs):
    """
    This command constrains rigid bodies to the world or other rigid bodies.                 In query mode, return type is
    based on queried flag.
    
    Flags:
      - barrier : br                   (bool)          [create,query]
          Creates a barrier constraint.  This command requires one rigid bodies.
    
      - damping : d                    (float)         [create,query,edit]
          Sets the damping constant. Default value: 0.1 Range: -1000.0 to 1000.0
    
      - directionalHinge : dhi         (bool)          [create,query]
          Creates a directional hinge constraint.  This command requires two rigid bodies. The directional hinge always maintains
          the initial direction of its axis.
    
      - hinge : hi                     (bool)          [create,query]
          Creates a hinge constraint.  This command requires one or two rigid bodies.
    
      - interpenetrate : i             (bool)          [create,query,edit]
          Allows (or disallows) the rigid bodies defined in the constrain to ipenetrate.
    
      - nail : na                      (bool)          [create,query]
          Creates a nail constraint.  This command requires one rigid body.
    
      - name : n                       (unicode)       [create,query,edit]
          Names the rigid constraint.
    
      - orientation : o                (float, float, float) [create,query,edit]
          Set initial orientation of the constraint in world space.  This command is only valid with hinge and barrier constraints
          Default value: 0.0 0.0 0.0
    
      - pinConstraint : pin            (bool)          [create,query]
          Creates a pin constraint.  This command requires two rigid bodies.
    
      - position : p                   (float, float, float) [create,query,edit]
          Set initial position of the constraint in world space. Default value: 0.0 0.0 0.0 for uni-constraints, midpoint of
          bodies for deul constraint.
    
      - restLength : rl                (float)         [create,query,edit]
          Sets the rest length. Default value: 1.0
    
      - spring : s                     (bool)          [create,query]
          Creates a spring constraint.  This command requires one or two rigidies.
    
      - stiffness : st                 (float)         [create,query,edit]
          Sets the springs stiffness constant. Default value: 5.0                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.constrain`
    """

    pass


def vortex(*args, **kwargs):
    """
    A vortex field pulls objects in a circular direction, like a whirlpool or tornado.   Objects affected by the vortex
    field tend to rotate around the axis specified by -ax, -ay, and -az. The transform is the associated dependency node.
    Use connectDynamic to cause the field to affect a dynamic object. If fields are created, this command returns the names
    of each of the fields. If a field was queried, the results of the query are returned. If a field was edited, the field
    name is returned. If object names are provided or the active selection list is non-empty, the command creates a field
    for every object in the list and calls addDynamic to add it to the object. If the list is empty, the command defaults to
    -pos 0 0 0. Setting the -pos flag with objects named on the command line is an error.
    
    Flags:
      - attenuation : att              (float)         [query,edit]
          Attentuation rate of field
    
      - axisX : ax                     (float)         [query,edit]
          X-component of vortex axis
    
      - axisY : ay                     (float)         [query,edit]
          Y-component of vortex axis
    
      - axisZ : az                     (float)         [query,edit]
          Z-component of vortex axis
    
      - magnitude : m                  (float)         [query,edit]
          Strength of field.
    
      - maxDistance : mxd              (float)         [query,edit]
          Maximum distance at which field is exerted. -1 indicates that the field has no maximum distance.
    
      - name : n                       (unicode)       [query,edit]
          name of field
    
      - perVertex : pv                 (bool)          [query,edit]
          Per-vertex application. If this flag is set true, then each individual point (CV, particle, vertex,etc.) of the chosen
          object exerts an identical copy of the force field. If this flag is set to false, then the force is exerted only from
          the geometric center of the set of points.
    
      - position : pos                 (float, float, float) [query,edit]
          Position in space where you want to place a field. The gravity then emanates from this position in space rather than
          from an object. Note that you can both use -pos (creating a field at a position) and also provide object names.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - torusSectionRadius : tsr       (float)         [query,edit]
    
      - volumeExclusion : vex          (bool)          [query,edit]
    
      - volumeOffset : vof             (float, float, float) [query,edit]
    
      - volumeShape : vsh              (unicode)       [query,edit]
    
      - volumeSweep : vsw              (float)         [query,edit]
    
    
    Derived from mel command `maya.cmds.vortex`
    """

    pass


def dynCache(*args, **kwargs):
    """
    Cache the current state of all particle shapes at the current time.
    
    
    Derived from mel command `maya.cmds.dynCache`
    """

    pass


def fluidCacheInfo(*args, **kwargs):
    """
    A command to get information about the fluids cache. Get the startFrame and resolution for InitialConditions. Get the
    endFrame as well for a playback cache. Note that for the playback cache, it will look at the current time (or last frame
    if the current time is past end of cache)                 In query mode, return type is based on queried flag.
    
    Flags:
      - attribute : at                 (unicode)       [create,query,edit]
          Modifier to the hasDataflag, used to query whether a cache has data (at the current time) for a specific fluid
          attribute.  Valid attribute values are density, velocity, temperature, fuel, color, coordinates(for texture
          coordinates), falloff.
    
      - cacheTime : t                  (time)          [create,query,edit]
          Only valid with the -hasData flag.  The time the -hasData flag uses when it queries the cache to see if there is data.
    
      - endFrame : ef                  (bool)          [create,query,edit]
          Returns end time of cache as float.
    
      - hasCache : hc                  (bool)          [create,query,edit]
          Returns true if fluid has specified cache, false if not.
    
      - hasData : hd                   (bool)          [create,query,edit]
          Queries whether a given cache has data in it at the time specified by the -time flag.  (If not -time flag is present,
          -hasData assumes the current time.) When used with the attributeflag, indicates if data for the specified attribute
          exists in the cache.  When used without the attributeflag, hasDataindicates whether there is data in the cache for any
          of the valid fluid attributes.
    
      - initialConditions : ic         (bool)          [create,query,edit]
          Specifies the cache to be queried is the Initial Conditionscache.
    
      - playback : pb                  (bool)          [create,query,edit]
          Specifies the cache to be queried is the Playbackcache.
    
      - resolution : re                (bool)          [create,query,edit]
          Returns cache resolution as float[].
    
      - startFrame : sf                (bool)          [create,query,edit]
          Returns start time for cache as float.                             Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.fluidCacheInfo`
    """

    pass


def spring(*args, **kwargs):
    """
    The spring command can do any of the following:\* create a new spring object (shape plus transform).  The shape contains
    springs between the points (particles, cvs, etc.) of the objects selected or listed on the command line.\* create new
    springs and add them to an existing spring object\* edit or query certain attributes of an existing spring objectOne
    spring objectmay have hundreds or even thousands of individual springs. Certain attributes of the spring object specify
    exactly where the springs are attached to which other objects.Springs may be attached to the following: particles,
    vertices of soft bodies, CVs or edit points of curves or surfaces, vertices of polygonal objects, and points of
    lattices. In the case where one endpoint of a spring is non-dynamic (a CV, edit point, etc.), the spring does not affect
    its motion, but the motion of the point affects the spring. A spring will be created only if at least one of the
    endpoints is dynamic: for example, a spring will never be created between two CVs. A single spring object can hold
    springs which are incident to any number of other objects.The spring has creation-only flags and editable flags.
    Creation-only flags (minDistance, maxDistance, add, exclusive, all, wireframe, walklength, checkExisting) can be used
    only when creating new springs (including adding springs to existing spring object).  Editable flags modify attributes
    of an existing spring object.If a spring object is created, this command returns the names of the shape and transform.
    If a spring object is queried, the command returns the results of the query.
    
    Flags:
      - addSprings : add               (bool)          [create]
          If specified, springs will be added to the existing selected set of springs. (Default is to create a new spring object.)
    
      - allPoints : all                (bool)          [create,edit]
          If True, sets the mode of spring application to All.  This will add springs between all points selected. (Default is
          False.)
    
      - count : ct                     (bool)          [query]
          Return the number of springs in the shape.  Query-only. We maintain this flag only for compatibility with earlier
          versions of Maya.  To get the count of springs, it is much faster and simpler to use the spring shape's count attribute:
          getAttr shapeName.count.
    
      - damp : dmp                     (float)         []
    
      - damping : d                    (float)         [create,query,edit]
          Damping factor for the springs created in the spring object. (Default = 0.2 )
    
      - dampingPS : dPS                (float)         [create,query,edit]
          Damping factor for the springs created in the spring object. This will initialize all the entries in dampingPS to the
          specified value. In both the flag and the attribute name, PSstands for per-spring.(Default = 0.2 )
    
      - endForceWeight : efw           (float)         [create,query,edit]
          Amount of the force of the spring that gets applied to the point to which the spring ends. Valid range is from 0.0 to
          1.0. (Default = 1.0 )
    
      - exclusive : exc                (bool)          [create]
          If true, tells the command to create springs only between pairs of points which are not in the same object. (Default is
          False.)
    
      - length : l                     (float)         [create,query,edit]
          Vestigial form of restLength.Please use restLengthinstead.
    
      - maxDistance : mxd              (float)         [create,edit]
          Maximum distance between two points that a spring would be considered.
    
      - minDistance : mnd              (float)         [create]
          Minimum distance between two points that a spring would be considered. (Default = 0.0. See Defaults for more information
          on this flag's default.)
    
      - minMax : mm                    (bool)          [create]
          If True, sets the mode of the spring application to Min/Max. This will add springs between all points from the specified
          point groups that are between the minimum and maximum distance values set with min and max. (Default is False.) Note:
          This gets automatically set if either the min or max flags are used.
    
      - name : n                       (unicode)       [create,query]
          Name of spring object.
    
      - noDuplicate : nd               (bool)          [create]
          Check for existing springs and don't add a new spring between two points already connected by a spring in the same
          object. Only the object the command is working on is checked.  This flag is relevant only when using -add. (Default =
          false)
    
      - restLength : rl                (float)         [create,query,edit]
          Per-object rest length for the new springs. Springs can use either their per-object or per-spring rest length.  See the
          -lPS and -ulp flags.
    
      - restLengthPS : rPS             (float)         [create,query,edit]
          Per-spring rest length for the new springs. This will initialize all the entries in restLengthPS to the specified value.
          If this flag is not thrown, each rest length will be initialized to the distance between the two  points at the time the
          spring is created (i.e., the initial length of the spring).   When playing back, springs can use either their per-spring
          or per-object rest length.  See the -rl and -urp flags. In both the flag and the attribute name, PSstands for per-
          spring.
    
      - startForceWeight : sfw         (float)         [create,query,edit]
          Amount of the force of the spring that gets applied to the point from which the spring starts. Valid range is from 0.0
          to 1.0. (Default = 1.0 )
    
      - stiffness : s                  (float)         [create,query,edit]
          Stiffness of the springs created in the spring object. (Default = 1.0 ) -damp float Vestigial form of damping.Please use
          dampinginstead.
    
      - stiffnessPS : sPS              (float)         [create,query,edit]
          Stiffness of the springs created in the spring object. This will initialize all the entries in stiffnessPS to the
          specified value. In both the flag and the attribute name, PSstands for per-spring.(Default = 1.0 )
    
      - strength : str                 (float)         []
    
      - useDampingPS : udp             (bool)          [create,query,edit]
          Specifies whether to use dampingPS (per spring damping). If set to false, the per object damping attribute value will be
          used. This flag simply sets the useDampingPS attribute of the spring shape. In both the flag and the attribute name,
          PSstands for per-spring.(Default = false )
    
      - useRestLengthPS : urp          (bool)          [create,query,edit]
          Specifies whether to use restLengthPS (per spring restLength). If set to false, the per object restLength attribute
          value will be used. This flag simply sets the useRestLengthPS attribute of the spring shape. In both the flag and the
          attribute name, PSstands for per-spring.(Default = false )
    
      - useStiffnessPS : usp           (bool)          [create,query,edit]
          Specifies whether to use stiffnessPS (per spring stiffness). If set to false, the per object stiffness attribute value
          will be used. This flag simply sets the useStiffnessPS attribute of the spring shape. In both the flag and the attribute
          name, PSstands for per-spring.(Default = false )
    
      - walkLength : wl                (int)           [create]
          This flag is valid only when doing wireframe creation. It will create springs between pairs of points connected by the
          specified number of edges.  For example, if walk length is 2, each pair of points separated by no more than 2 edges will
          get a spring.  Walk length measures the distance between pairs of vertices just like the number of blocks measures the
          distance between two intersections in a city.
    
      - wireframe : wf                 (bool)          [create]
          If True, sets the mode of the spring application to Wireframe. This is valid only for springs created on a soft body. It
          will add springs along all edges connecting the adjacent points (vertices or CV's) of curves and surfaces. (Default is
          False.)                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.spring`
    """

    pass


def saveFluid(*args, **kwargs):
    """
    A command to save the current state of the fluid to the initial state cache. The grids to be saved are determined by the
    cache attributes: cacheDensity, cacheVelocity, etc. These attributes are normally set from the options on Set Initial
    State. The cache must be set up before invoking this command.             In query mode, return type is based on queried
    flag.
    
    Flags:
      - currentTime : ct               (int)           [create,query,edit]
          cache state of fluid at current time
    
      - endTime : et                   (int)           [create,query,edit]
          end Time for cacheing
    
      - startTime : st                 (int)           [create,query,edit]
          start Time for cacheing                                    Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.saveFluid`
    """

    pass


def dynPaintEditor(*args, **kwargs):
    """
    Create a editor window that can be painted into
    
    Flags:
      - activeOnly : ao                (bool)          [query,edit]
          For Scene mode, this determines if only the active strokes will be refreshed.
    
      - autoSave : autoSave            (bool)          [query,edit]
          For Canvas mode, this determines if the buffer will be saved to a disk file after every stroke. Good for painting
          textures and viewing the results in shaded display in the model view.
    
      - camera : cam                   (unicode)       [query,edit]
          Sets the name of the camera which the Paint Effects panel looks through.
    
      - canvasMode : cm                (bool)          [query,edit]
          Sets the Paint Effects panel into Canvas mode if true.
    
      - canvasUndo : cu                (bool)          [edit]
          Does a fast undo in Canvas mode. This is a special undo because we are not using any history when we paint in Canvas
          mode so we provide a single level undo for the Canvas.
    
      - changeCommand : cc             (unicode, unicode, unicode, unicode) [create,query,edit]
          Parameters: First string: commandSecond string: editorNameThird string: editorCmdFourth string: updateFuncCall the
          command when something changes in the editor The command should have this prototype :  command(string $editor, string
          $editorCmd, string $updateFunc, int $reason)  The possible reasons could be : 0: no particular reason1: scale color2:
          buffer (single/double)3: axis 4: image displayed5: image saved in memory
    
      - clear : cl                     (float, float, float) [edit]
          Clears the buffer (if in Canvas mode) to the floating point values (R,G,B).
    
      - control : ctl                  (bool)          [query]
          Query only. Returns the top level control for this editor. Usually used for getting a parent to attach popup menus.
          Caution: It is possible for an editor to exist without a control. The query will return NONEif no control is present.
    
      - currentCanvasSize : ccs        (bool)          [query]
          In Query mode, this returns the (X,Y) resolution of the current canvas.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - displayAppearance : dsa        (unicode)       [query,edit]
          Sets the display appearance of the model panel.  Possible values are wireframe, points, boundingBox, smoothShaded,
          flatShaded.  This flag may be used with the -interactive and -default flags.  Note that only wireframe, points, and
          boundingBoxare valid for the interactive mode.
    
      - displayFog : dfg               (bool)          [query,edit]
          For Scene mode, this determines if fog will be displayed in the Paint Effects panel when refreshing the scene. If fog is
          on, but this is off, fog will only be drawn on the strokes, not the rest of the scene.
    
      - displayImage : di              (int)           [query,edit]
          Set a particular image in the Editor Image Stack as the current Editor Image. Images are added to the Editor Image Stack
          using the si/saveImageflag.
    
      - displayLights : dsl            (unicode)       [query,edit]
          Sets the lighting for shaded mode.  Possible values are selected, active, all, default.
    
      - displayStyle : dst             (unicode)       [create,query,edit]
          Set the mode to display the image. Valid values are: colorto display the basic RGB imagemaskto display the mask
          channellumto display the luminance of the image
    
      - displayTextures : dtx          (bool)          [query,edit]
          Turns on or off display of textures in shaded mode
    
      - docTag : dtg                   (unicode)       [create,query,edit]
          Attaches a tag to the editor.
    
      - doubleBuffer : dbf             (bool)          [create,query,edit]
          Set the display in double buffer mode
    
      - drawAxis : da                  (bool)          [create,query,edit]
          Set or query whether the axis will be drawn.
    
      - drawContext : drc              (bool)          [query]
          Returns the name of the context.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - fastUpdate : fu                (int)           []
    
      - fileName : fil                 (unicode)       [query,edit]
          This sets the file to which the canvas will be saved.
    
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
    
      - iconGrab : ig                  (bool)          [edit]
          This puts the Paint Effects panel into Grab Icon mode where the user is expected to drag out a section of the screen to
          be made into an icon.
    
      - loadImage : li                 (unicode)       [edit]
          load an image from disk and set it as the current Editor Image
    
      - lockMainConnection : lck       (bool)          [create,edit]
          Locks the current list of objects within the mainConnection, so that only those objects are displayed within the editor.
          Further changes to the original mainConnection are ignored.
    
      - mainListConnection : mlc       (unicode)       [create,query,edit]
          Specifies the name of a selectionConnection object that the editor will use as its source of content. The editor will
          only display items contained in the selectionConnection object.
    
      - menu : mn                      (unicode)       [create]
          Sets the name of the script used to build a menu in the editor. The script takes the editor name as an argument.
    
      - nbImages : nim                 (bool)          [query]
          returns the number of images
    
      - newImage : ni                  (int, int, float, float, float) [query,edit]
          Starts a new image in edit mode, setting the resolution to the integer values (X,Y) and clearing the buffer to the
          floating point values (R,G,B). In Query mode, this returns the (X,Y) resolution of the current Image.
    
      - paintAll : pa                  (float)         [edit]
          Redraws the buffer in current refresh mode.
    
      - panel : pnl                    (unicode)       [create,query]
          Specifies the panel for this editor. By default if an editor is created in the create callback of a scripted panel it
          will belong to that panel. If an editor does not belong to a panel it will be deleted when the window that it is in is
          deleted.
    
      - parent : p                     (unicode)       [create,query,edit]
          Specifies the parent layout for this editor. This flag will only have an effect if the editor is currently un-parented.
    
      - redrawLast : rl                (bool)          [edit]
          Redraws the last stroke again. Useful when it's brush has just changed. This feature does a fast undo and redraws the
          stroke again.
    
      - refresh : ref                  (bool)          [edit]
          requests a refresh of the current Editor Image.
    
      - refreshMode : rmd              (int)           [query,edit]
          Sets the refresh mode to the specified value. 0 - Do not draw strokes on refresh, 1 - Redraw strokes in wireframe mode,
          2 - Redraw strokes in final rendered mode.
    
      - removeAllImages : ra           (bool)          [edit]
          remove all the Editor Images from the Editor Image Stack
    
      - removeImage : ri               (bool)          [edit]
          remove the current Editor Image from the Editor Image Stack
    
      - rollImage : rig                (float, float)  [edit]
          In Canvas mode, this rolls the image by the floating point values (X,Y). X and Y are between 0 (no roll) and 1 (full
          roll). A value of .5 rolls the image 50% (ie. the border moves to the center of the screen.
    
      - saveAlpha : sa                 (bool)          [query,edit]
          For Canvas mode, this determines if the alpha will be saved when storing the canvas to a disk file.
    
      - saveBumpmap : sbm              (unicode)       [query,edit]
          Saves the current buffer as a bump map to the specified file.
    
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
    
      - singleBuffer : sbf             (bool)          [create,query,edit]
          Set the display in single buffer mode
    
      - snapShot : snp                 (bool)          [edit]
          Takes a snapshot of the current camera view.
    
      - stateString : sts              (bool)          [query]
          Query only flag. Returns the MEL command that will create an editor to match the current editor state. The returned
          command string uses the string variable $editorName in place of a specific name.
    
      - swap : swp                     (int)           []
    
      - tileSize : ts                  (int)           [edit]
          Sets the size of the tile for the hardware texture redraw of the display buffer.
    
      - unParent : up                  (bool)          [create,edit]
          Specifies that the editor should be removed from its layout. This cannot be used in query mode.
    
      - undoCache : uc                 (bool)          [edit]
          By default the last image is cached for undo. If this is set false, then undoing will be disabled in canvas mode and
          undo in scene mode will force a full refresh. Less memory will be used if this is set false before the first clear or
          refresh of the current scene.
    
      - unlockMainConnection : ulk     (bool)          [create,edit]
          Unlocks the mainConnection, effectively restoring the original mainConnection (if it is still available), and dynamic
          updates.
    
      - updateMainConnection : upd     (bool)          [create,edit]
          Causes a locked mainConnection to be updated from the orginal mainConnection, but preserves the lock state.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - wrap : wr                      (bool, bool)    [query,edit]
          For Canvas mode, should the buffer wrap in U, and V (respectively) when painting.
    
      - writeImage : wi                (unicode)       [edit]
          write the current Editor Image to disk
    
      - zoom : zm                      (float)         [query,edit]
          Zooms the Canvas image by the specified value.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.dynPaintEditor`
    """

    pass


def event(*args, **kwargs):
    """
    The event command assigns collision events to a particle object. Collision events are stored in multi-attributes in the
    particle shape. The event command returns the event name.
    
    Flags:
      - count : ct                     (int)           [query,edit]
          Collision number (for each particle) to which this event applies. Zero (the default) indicates that it applies to all
          collisions.
    
      - delete : d                     (bool)          [create]
          Delete the specified event.
    
      - dieAtCollision : die           (bool)          [query,edit]
          Particle dies at the collision specified by count.If no count value is given, die at first collision.
    
      - emit : em                      (int)           [query,edit]
          Emit n additional particles into the assigned target object. The original (colliding) particle survives as well, and
          remains in its original object.  The new particles have age zero and mass equal to the emitting particle. They use the
          velocity inheritance parameter of the target object.
    
      - idNumber : id                  (int)           []
    
      - list : ls                      (bool)          [create]
          List all events for the chosen shape, like this: event1Name event2Name ... If no shape identified, list all events for
          all shapes, like this: shape1Name event1Name shape2Name event2Name... Returns a string array.
    
      - name : n                       (unicode)       [create,query,edit]
          Assign a name to an event you are creating, or identify an event you wish to edit, query, or delete. See examples.
    
      - proc : pr                      (script)        [create,query,edit]
          Specify a MEL proc to be called each time the event occurs. This must be a global proc with arguments as follows: global
          proc procName( string obj, int id, string objHit ); Arguments passed in are the name of the particle object, the id of
          the particle which collided, and the name of the object collided with.  You can use particle -id -q to get values of the
          particle's attributes.
    
      - random : r                     (bool)          [query,edit]
          Used with -split and -emit flags.  If -random is set true and -split or -emit is set to n, then a random number of
          particles uniformly distributed between 1 and n will be created at the event.
    
      - rename : re                    (unicode)       [query]
          Assign a new name to an event you are editing. See examples.
    
      - select : s                     (bool)          []
          This flag is obsolete.  See the -name flag.
    
      - split : spl                    (int)           [query,edit]
          Colliding particle splits into specified number of new particles. These new particles become part of the assigned target
          object. If no target has been assigned, they become part of the same object.  The new particles inherit the current age
          of the particle that split.  They use the velocity inheritance parameter of the target object.  If you set both emit and
          split, the event will do both: first emit new particles, then split the original one. This is a change from earlier
          versions where emit and split were mutually exclusive.
    
      - spread : sp                    (float)         [query,edit]
          Particles created at collision will spread out a random amount from the rebound direction of the colliding particle.
          The spread is specified as a fraction (0-1) of 90 degrees.  If spread is set at 0 (the default) all the new particles
          created may coincide.
    
      - target : t                     (unicode)       [query,edit]
          Target object for emitting or split particles. New particles created through the -emit or -split flags join this object.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.event`
    """

    pass


def volumeAxis(*args, **kwargs):
    """
    A volume axis field can push particles in four directions, defined with respect to a volume: along the axis, away from
    the axis or center, around the axis, and in a user-specified direction.  These are analogous to the emission speed
    controls of volume emitters. The volume axis field also contains a wind turbulence model (different from the turbulence
    field) that simulates an evolving flow of liquid or gas. The turbulence has a build in animation that is driven by a
    connection to a time node. The transform is the associated dependency node. Use connectDynamic to cause the field to
    affect a dynamic object. If fields are created, this command returns the names of each of the fields. If a field was
    queried, the results of the query are returned. If a field was edited, the field name is returned. If object names are
    provided or the active selection list is non-empty, the command creates a field for every object in the list and calls
    addDynamic to add it to the object. If the list is empty, the command defaults to -pos 0 0 0. Setting the -pos flag with
    objects named on the command line is an error.
    
    Flags:
      - alongAxis : alx                (float)         [query,edit]
          Initial velocity multiplier in the direction along the central axis of the volume.  See the diagrams in the
          documentation.
    
      - aroundAxis : arx               (float)         [query,edit]
          Initial velocity multiplier in the direction around the central axis of the volume.  See the diagrams in the
          documentation.
    
      - attenuation : att              (float)         [query,edit]
          Attentuation rate of field with distance. For sphere volumes, distance is computed from the center of the sphere.  For
          cone, cylinder, and cube volumes, it is computed from the vertical axis of the volume.  For torus volumes, it is
          computed from the ring in the middle of the solid portion of the torus.
    
      - awayFromAxis : afx             (float)         [query,edit]
          Initial velocity multiplier in the direction away from the central axis of the volume.  See the diagrams in the
          documentation.  Used only with the cylinder, cone, and torus volumes.
    
      - awayFromCenter : afc           (float)         [query,edit]
          Initial velocity multiplier in the direction away from the center point of a cube or sphere volume. Used only with the
          cube and sphere volumes.
    
      - detailTurbulence : dtr         (float)         [query,edit]
          The relative intensity of a second higher frequency turbulence. This can be used to create fine features in large scale
          flows. Both the speed and the frequency on this second turbulence are higher than the primary turbulence. When the
          detailTurbulence is non-zero the simulation may run a bit slower, due to the computation of a second turbulence.
    
      - directionX : dx                (float)         [query,edit]
          x-component of force direction.  Used with directional speed.
    
      - directionY : dy                (float)         [query,edit]
          y-component of force direction.  Used with directional speed.
    
      - directionZ : dz                (float)         [query,edit]
          z-component of force direction.  Used with directional speed.
    
      - directionalSpeed : drs         (float)         [query,edit]
          Adds a component of speed in the direction specified by the directionX, Y, and Z attributes.
    
      - invertAttenuation : ia         (bool)          [query,edit]
          If this attribute is FALSE, the default, then the attenuation makes the field's effect decrease as the affected point is
          further from the volume's axis and closer to its edge.  If the is set to TRUE, then the effect of the field increases in
          this case, making the full effect of the field felt at the volume's edge.
    
      - magnitude : m                  (float)         [query,edit]
          Strength of field.
    
      - maxDistance : mxd              (float)         [query,edit]
          Maximum distance at which field is exerted. A zero or negative value will turn off the field effect completely. For
          sphere volumes, distance is computed from the center of the sphere.  For cone, cylinder, and cube volumes, it is
          computed from the vertical axis of the volume.  For torus volumes, it is computed from the ring in the middle of the
          solid portion of the torus.
    
      - name : n                       (unicode)       [query,edit]
          name of field
    
      - perVertex : pv                 (bool)          [query,edit]
          No effect for this type of field.
    
      - position : pos                 (float, float, float) [query,edit]
          Position in space where you want to place the volume.
    
      - torusSectionRadius : tsr       (float)         [query,edit]
    
      - turbulence : trb               (float)         [query,edit]
          Adds a force simulating a turbulent wind that evolves over time.
    
      - turbulenceFrequencyX : tfx     (float)         [query,edit]
          The repeats of the turbulence function in X.
    
      - turbulenceFrequencyY : tfy     (float)         [query,edit]
          The repeats of the turbulence function in Y.
    
      - turbulenceFrequencyZ : tfz     (float)         [query,edit]
          The repeats of the turbulence function in Z.
    
      - turbulenceOffsetX : tox        (float)         [query,edit]
          The translation of the turbulence function in X.
    
      - turbulenceOffsetY : toy        (float)         [query,edit]
          The translation of the turbulence function in Y.
    
      - turbulenceOffsetZ : toz        (float)         [query,edit]
          The translation of the turbulence function in Z.
    
      - turbulenceSpeed : trs          (float)         [query,edit]
          The rate of change of the turbulence over time. The turbulence loops seamlessly every 1.0/turbulenceSpeed seconds. To
          animate this rate attach a new time node to the time input on the volumeAxisNode then animate the time value on the time
          node.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
      - volumeExclusion : vex          (bool)          [query,edit]
    
      - volumeOffset : vof             (float, float, float) [query,edit]
    
      - volumeShape : vsh              (unicode)       [query,edit]
    
      - volumeSweep : vsw              (float)         [query,edit]
    
    
    Derived from mel command `maya.cmds.volumeAxis`
    """

    pass


def rigidBody(*args, **kwargs):
    """
    This command creates a rigid body from a polygonal or nurbs surface.
    
    Flags:
      - active : act                   (bool)          [create,query,edit]
          Creates a rigid body that is active.  An active rigid body accepts and causes collisions and is effected by dynamic
          fields.  This is the default.
    
      - angularVelocity : av           (bool)          [query]
          Current angular velocity of rigid body.
    
      - applyForceAt : afa             (unicode)       [create,query,edit]
          Determines how forces are applied to the rigid body. The choices are centerOfMass | boundingBox | verticesOrCVs.
          Default: boundingBox
    
      - bounciness : b                 (float)         [create,query,edit]
          Sets the restitution (or bounciness) of the rigid body. Range:   0.0 - 2.0 Default: 0.6
    
      - cache : c                      (bool)          [create,query,edit]
          Turns caching on (1) or off (0) for the rigid body. Default: off
    
      - centerOfMass : com             (float, float, float) [create,query,edit]
          Sets the center of mass (x,y,z) of the rigid body. Default: actual center of mass.
    
      - collisions : cl                (bool)          [create,query,edit]
          Truns collisions on/off for the rigid body.  If the collisions are turned of the rigid body will not collide with any
          other rigid body. Default: on.
    
      - contactCount : cc              (bool)          [query]
          returns the current contact count for the rigid body.
    
      - contactName : cn               (bool)          [query]
          returns all the rigid body names which are in contact with this shape.  One name for each contact will be returned.
    
      - contactPosition : cp           (bool)          [query]
          returns all the contact position.  One position for each contact will be returned.
    
      - damping : dp                   (float)         [create,query,edit]
          Sets the damping value of the rigid body. Range:   -2.0 - 2.0 Default: 0.0
    
      - deleteCache : dc               (bool)          [edit]
          Deletes the cache (if one exists) of the rigid body.
    
      - dynamicFriction : df           (float)         [create,query,edit]
          Sets the dynamic friction for the rigid body. Range:   0.0 - 1.0 Default: 0.2
    
      - force : f                      (bool)          [query]
          Current force on the rigid body.
    
      - ignore : ig                    (bool)          [create,query,edit]
          Causes the rigid body to be ignored in the rigid solver. Default: off
    
      - impulse : i                    (float, float, float) [create,edit]
          Applies an impulse (instantaneous) force on a rigid body. Default: 0.0 0.0 0.0
    
      - impulsePosition : imp          (float, float, float) [create,edit]
          The position at which the impulse is applied. Default: the bodies center of mass.
    
      - initialAngularVelocity : iav   (float, float, float) [create,query,edit]
          Sets the initial angular velocity of the rigid body. Default: 0.0 0.0 0.0
    
      - initialVelocity : iv           (float, float, float) [create,query,edit]
          Sets the initial velocity of the rigid body. Default: 0.0 0.0 0.0
    
      - layer : l                      (int)           [create,query,edit]
          Sets the collision layer of the rigid body.  Only rigid bodies in the same collision layer can collide with each other.
          Range:   = 0 Default: 0.
    
      - lockCenterOfMass : lcm         (bool)          [create,query,edit]
          Locks the center of mass for the rigid body. Default: off
    
      - mass : m                       (float)         [create,query,edit]
          Sets the mass of the rigid body. Range:   0 Default: 1.0
    
      - name : n                       (unicode)       [create,query,edit]
          Assigns the rigid body the given name.
    
      - orientation : o                (float, float, float) [create,query,edit]
          Sets the initial orientation (x,y,z) of the rigid body. Default: current orientation.
    
      - particleCollision : pc         (bool)          [create,query,edit]
          Turns the ability for a rigid body to collide with particles on and off.  The particles will exert a force on the rigid
          body. Default: off
    
      - passive : pas                  (bool)          [create,query,edit]
          Creates a rigid body that is passive.  A passive rigid body does not react to collisions but active rigid bodies can
          collide with it. Dynamic Fields will not effect a passive rigid body.  Only passive rigid bodies can be keyframed.
    
      - position : p                   (float, float, float) [create,query,edit]
          Sets the initial position (x,y,z) of the rigid body. Default: current position.
    
      - removeShape : rs               (unicode)       []
    
      - solver : slv                   (unicode)       [create,query,edit]
          The name of the solver which this rigid node is to resided.  If the solver does not exists then the rigid body will not
          be created.  If the edit flag is thrown add the solver exists, the rigid body will be moved to that solver.
    
      - spinImpulse : si               (float, float, float) [create,edit]
          Applies an spin impulse (instantaneous rotational) force on a rigid body. Default: 0.0 0.0 0.0
    
      - standInObject : sio            (unicode)       [create,query,edit]
          Causes the simulator to use a stand in object for the simulation. The choices are none | cube | sphere. The default is
          none. Default: none
    
      - staticFriction : sf            (float)         [create,query,edit]
          Sets the static friction for the rigid body. Range:   0.0 - 1.0 Default: 0.2
    
      - tesselationFactor : tf         (int)           [create,query]
          Sets the tesselation factor for a rigid body surface. Range:   = 10 Default: 200.
    
      - velocity : vel                 (bool)          [query]
          Current velocity of rigid body.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.rigidBody`
    """

    pass


def particleRenderInfo(*args, **kwargs):
    """
    This action provides information access to the particle render subclasses. These are derived from TdynRenderBase. This
    action is used primarily by the Attribute Editor to gather information about attributes used for rendering. In query
    mode, return type is based on queried flag.
    
    Flags:
      - attrList : al                  (int)           [query]
          Return the list of attributes used by this render type.
    
      - attrListAll : ala              (bool)          [query]
          Return a complete list of all render attributes used by the particle object. This also includes the per particle
          attributes.
    
      - name : n                       (int)           [query]
          Return the name of the render subclass using the render type.
    
      - renderTypeCount : rtc          (bool)          [query]
          Return the count of registered render classes for particle.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.particleRenderInfo`
    """

    pass


def particleInstancer(*args, **kwargs):
    """
    This command is used to create a particle instancer node and set the proper attributes in the particle shape and in the
    instancer node.  It will also create the connections needed between the particle shape and the instancer node.
    
    Flags:
      - addObject : a                  (bool)          [create,edit]
          This flag indicates that objects specified by the -object flag will be added to the instancer node as instanced objects.
    
      - aimAxis : aa                   (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the aim axis of the instanced objects.
    
      - aimDirection : ad              (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the aim direction of the instanced objects.
    
      - aimPosition : ap               (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the aim position of the instanced objects.
    
      - aimUpAxis : aua                (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the aim up axis of the instanced objects.
    
      - aimWorldUp : awu               (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the aim world up of the instanced objects.
    
      - attributeMapping : am          (bool)          [query]
          This flag queries the particle attribute mapping list.
    
      - cycle : c                      (unicode)       [create,query,edit]
          This flag sets or queries the cycle attribute for the instancer node.  The options are none, sequential. The default is
          none.
    
      - cycleStartObject : sto         (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the cycle start object of the instanced objects.
    
      - cycleStep : cs                 (float)         [create,query,edit]
          This flag sets or queries the cycle step attribute for the instancer node.  This attribute indicates the size of the
          step in frames or seconds (see cycleStepUnits).
    
      - cycleStepUnits : csu           (unicode)       [create,query,edit]
          This flag sets or queries the cycle step unit attribute for the instancer node. The options are framesor seconds.  The
          default is frames.
    
      - index : i                      (int)           [query]
          This flag is used to query the name of the ith instanced object.
    
      - instanceId : id                (unicode)       [query]
          This flag queries the particle attribute name to be used for the id of the instanced objects.
    
      - levelOfDetail : lod            (unicode)       [create,query,edit]
          This flag sets or queries the level of detail of the instanced objects.  The options are geometry, boundingBoxor
          boundingBoxes.  The default is geometry.
    
      - name : n                       (unicode)       [create,query]
          This flag sets or queries the name of the instancer node.
    
      - object : obj                   (unicode)       [create,query,edit]
          This flag indicates which objects will be add/removed from the list of instanced objects.  The flag is used in
          conjuction with the -addObject and -remove flags.  If neither of these flags is specified on the command line then
          -addObject is assumed.
    
      - objectIndex : oi               (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the object index of the instanced objects.
    
      - particleAge : age              (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the age of the instanced objects.
    
      - position : p                   (unicode)       [create,query,edit]
          DEFAULT worldPositionThis flag sets or queries the particle attribute name to be used for the positions of the instanced
          objects.  By default the attribute is worldPosition.
    
      - removeObject : rm              (bool)          [edit]
          This flag indicates that objects specified by the -object flag will be removed from the instancer node as instanced
          objects.
    
      - rotation : r                   (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the rotation of the instanced objects.
    
      - rotationOrder : ro             (unicode)       [create,query,edit]
          This flag specifies the rotation order associated with the rotation flag.  The options are XYZ, XZY, YXZ, YZX, ZXY, or
          ZYX.  By default the attribute is XYZ.
    
      - rotationType : rt              (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the rotation type of the instanced objects.
    
      - rotationUnits : ru             (unicode)       [create,query,edit]
          This flag specifies the rotation units associated with the rotation flag.  The options are degrees or radians.  By
          default the attribute is degrees.
    
      - scale : sc                     (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the scale of the instanced objects.
    
      - shear : sh                     (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the shear of the instanced objects.
    
      - visibility : vis               (unicode)       [create,query,edit]
          This flag sets or queries the particle attribute name to be used for the visibility of the instanced objects.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.particleInstancer`
    """

    pass


def getParticleAttr(*args, **kwargs):
    """
    This action will return either an array of values, or the average value and maximum offset, for a specied per-particle
    attribute of a particle object or component.  If a particle component is specified on the command line, values are
    returned for that component only.  If an object name is given instead, values are returned for all particles in that
    object.  If no object name is passed, but a particle object or component is selected, values are returned for the
    selection. If you list components, they must all be from the same particle object; the action ignores all objects after
    the first.  Likewise if you list more than one object, the actiion will return values only for the first one.
    
    Flags:
      - array : a                      (bool)          [create]
          Tells the action whether you want a full array of data. If set true, the action returns an array of floats containing
          the values for all the specified particles.  If set false (the default), the action returns the average value and the
          maximum offset from the average over the component.  If the attribute is a vector attribute, the action returns six
          values: Average X, Average Y, Average Z, Maximum offset in X, Y, and Z of component.
    
      - attribute : at                 (unicode)       [create]
          Tells the action which attribute you want the value of. Must be a per-particle attribute.
    
      - object : o                     (unicode)       [create]
          This flag is obsolete.  Instead of using it, please pass the name of the object and/or components you want on the
          command line. See the examples.Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.getParticleAttr`
    """

    pass


def newton(*args, **kwargs):
    """
    A Newton field pulls an object towards the exerting object with force dependent on the exerting object's mass, using
    Newton's universal law of gravitation. The transform is the associated dependency node. Use connectDynamic to cause the
    field to affect a dynamic object. If fields are created, this command returns the names of each of the fields. If a
    field was queried, the results of the query are returned. If a field was edited, the field name is returned. If object
    names are provided or the active selection list is non-empty, the command creates a field for every object in the list
    and calls addDynamic to add it to the object. If the list is empty, the command defaults to -pos 0 0 0. Setting the -pos
    flag with objects named on the command line is an error.
    
    Flags:
      - attenuation : att              (float)         [query,edit]
          Attentuation rate of field
    
      - magnitude : m                  (float)         [query,edit]
          Strength of field.
    
      - maxDistance : mxd              (float)         [query,edit]
          Maximum distance at which field is exerted. -1 indicates that the field has no maximum distance.
    
      - minDistance : mnd              (float)         [query,edit]
          Minimum distance at which field is exerted. Distance is in the denominator of the field force equation. Setting md to a
          small positive number avoids bizarre behavior when the distance gets extremely small.
    
      - name : n                       (unicode)       [query,edit]
          name of field
    
      - perVertex : pv                 (bool)          [query,edit]
          Per-vertex application. If this flag is set true, then each individual point (CV, particle, vertex,etc.) of the chosen
          object exerts an identical copy of the force field. If this flag is set to false, then the froce is exerted only from
          the geometric center of the set of points.
    
      - position : pos                 (float, float, float) [query,edit]
          Position in space where you want to place a field. The newton then emanates from this position in space rather than from
          an object. Note that you can both use -pos (creating a field at a position) and also provide object names.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - torusSectionRadius : tsr       (float)         []
    
      - volumeExclusion : vex          (bool)          []
    
      - volumeOffset : vof             (float, float, float) []
    
      - volumeShape : vsh              (unicode)       []
    
      - volumeSweep : vsw              (float)         []
    
    
    Derived from mel command `maya.cmds.newton`
    """

    pass


def loadFluid(*args, **kwargs):
    """
    A command to set builtin fluid attributes such as Density, Velocity, etc for all cells in the grid from the initial
    state cache                  In query mode, return type is based on queried flag.
    
    Flags:
      - currentTime : ct               (bool)          [create,query,edit]
          This flag is now obsolete. Move the cache clip in the Trax editor to view different frames of the playback cache.
    
      - frame : f                      (float)         [create,query,edit]
          This flag is now obsolete. Move the cache clip in the Trax editor to view different frames of the playback cache.
    
      - initialConditions : ic         (bool)          [create,query,edit]
          load initial conditions cache                              Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.loadFluid`
    """

    pass


def dynGlobals(*args, **kwargs):
    """
    This node edits and queries the attributes of the active dynGlobals node in the scene. There can be only one active node
    of this type. The active dynGlobals node is the first one that was created, either with a createNodecommand or by
    accessing/editing any of the attributes on the node through this command.
    
    Flags:
      - active : a                     (bool)          [query]
          This flag returns the name of the active dynGlobals node in the the scene.  Only one dynGlobals node is active. It is
          the first on created.  Any additional dynGlobals nodes will be ignored.
    
      - listAll : la                   (bool)          [query]
          This flag will list all of the dynGlobals nodes in the scene.
    
      - overSampling : os              (int)           [query,edit]
          This flag will set the current overSampling value for all of the particle in the scene.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dynGlobals`
    """

    pass


def expressionEditorListen(*args, **kwargs):
    """
    Listens for messages for the Expression Editor, at its request, and communicates them to it.  This action is for
    internal use only and should not be called by users.  This action should be called only by the Expression Editor.
    
    Flags:
      - listenFile : lf                (unicode)       [create]
          Listen for changes to the file argument.
    
      - listenForAttr : la             (unicode)       [create]
          Listen for changes to the attributes of the node argument.
    
      - listenForExpression : le       (unicode)       [create]
          Listen for changes to the named expression
    
      - listenForName : ln             (unicode)       [create]
          Listen for name changes for the node argument.
    
      - stopListenForAttr : sla        (unicode)       [create]
          Stop listening for changes to the attributes of the node argument.
    
      - stopListenForExpression : sle  (unicode)       [create]
          Stop listening for changes to the named expression
    
      - stopListenForName : sln        (unicode)       [create]
          Stop listening for name changes for the node argument.                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.expressionEditorListen`
    """

    pass


def nBase(*args, **kwargs):
    """
    Edits one or more nBase objects. Note that nBase objects include nCloth, nRigid and nParticle objects, but the options
    on this command do not currently apply to nParticle objects.
    
    Flags:
      - clearCachedTextureMap : cct    (unicode)       [create,edit]
          Clear the cached texture map for the specified attribute from the nBase.
    
      - clearStart : cs                (bool)          [create,edit]
          Indicates that start state should be cleared
    
      - stuffStart : ss                (bool)          [create,edit]
          Indicates that current state should be stuffed into the start state
    
      - textureToVertex : ttv          (unicode)       [create,edit]
          Transfer the texture map data for the specified attribute into the related per-vertex attribute.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.nBase`
    """

    pass


def rigidSolver(*args, **kwargs):
    """
    This command sets the attributes for the rigid solver            In query mode, return type is based on queried flag.
    
    Flags:
      - autoTolerances : at            (bool)          [query,edit]
          Turns the auto tolerance calculation on and off.  The auto tolerances calculation will override the default or user
          defined values of the step size and collision tolerance value that is calculated based on the objects in the scene.
          Default: 0 (off)
    
      - bounciness : b                 (bool)          [query,edit]
          Turns bounciness on and off for the an the objects in the simulation. Default value: on
    
      - cacheData : cd                 (bool)          [query,edit]
          Turns the cache on fall all rigid bodies in the system. Default value: off
    
      - collide : c                    (bool)          [query,edit]
          Disallows the interpenetration of the two rigid bodies listed. Default: Collide is on for all bodies.
    
      - collisionTolerance : ct        (float)         [query,edit]
          Sets the collision tolerance.  This is the error at which two objects are considered to have collided. Range:   0.0005 -
          1.000 Default: 0.02
    
      - contactData : ctd              (bool)          [query,edit]
          Turns the contact data information on/off for all rigid bodies. Default value: off
    
      - create : cr                    (bool)          [create]
          Creates a new rigid solver.
    
      - current : cu                   (bool)          [create]
          Sets rigid solver as the current solver.
    
      - deleteCache : deleteCache      (bool)          [query,edit]
          Deletes the cache for all rigid bodies in the system.
    
      - displayCenterOfMass : dcm      (bool)          [query,edit]
          Displays the center of mass icon. Default value: on
    
      - displayConstraint : dc         (bool)          [query,edit]
          Displays the constraint vectors. Default value: on
    
      - displayVelocity : dv           (bool)          [query,edit]
          Displays the velocity vectors. Default value: off
    
      - dynamics : d                   (bool)          [query,edit]
          Turns dynamics on and off for the an the objects in the simulation. Default value: on
    
      - friction : f                   (bool)          [query,edit]
          Turns friction on and off for the an the objects in the simulation. Default value: on
    
      - interpenetrate : i             (bool)          [query,edit]
          Allows the two rigid bodies listed to interpenetrate. Default: interpenetration is off for all bodies.
    
      - interpenetrationCheck : ic     (bool)          [edit]
          Checks for interpenetrating rigid bodies in the scene.
    
      - name : n                       (unicode)       []
    
      - rigidBodies : rb               (bool)          [query]
          Returns a list of rigid bodies in the solver.
    
      - rigidBodyCount : rbc           (bool)          [query]
          Returns the number of rigid bodies in the solver.
    
      - showCollision : sc             (bool)          [query,edit]
          Displays the colliding objects in a different color.
    
      - showInterpenetration : si      (bool)          [query,edit]
          Displays the interpenetrating objects in a different color.
    
      - solverMethod : sm              (int)           [query,edit]
          Sets the solver method.  The choices are 0 | 1 | 2. 0 = Euler (fastest/least acurate), 1 = Runge-Kutta ( slower/more
          acurate), 2 = adaptive Runge-Kutta (slowest/most acurate). The default is 2 (adaptive Runge-Kutta)
    
      - startTime : stt                (float)         [create,query,edit]
          Sets the start time for the solver.
    
      - state : st                     (bool)          [query,edit]
          Turns the rigid solver on or off.
    
      - statistics : sta               (bool)          [query,edit]
          Turns the statistic information on/off for all rigid bodies. Default value: off
    
      - stepSize : s                   (float)         [query,edit]
          Sets the solvers step size.  This is the maximum size of a single step the solver will take at one time. Range:   0.0004
          - 0.100 Default: 0.0333
    
      - velocityVectorScale : vs       (float)         [query,edit]
          scales the velocity vector display. Default value: 1.0                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.rigidSolver`
    """

    pass


def soft(*args, **kwargs):
    """
    Makes a soft body from the object(s) passed on the command line or in the selection list.  The geometry can be a NURBS,
    polygonal, lattice object.  The resulting soft body is made up of a hierarchy with a particle shape and a geometry
    shape, thus: T    / \  T   G /      P        Dynamics are applied to the particle shape and the resulting particle
    positions then drive the locations of the geometry's CVs, vertices, or lattice points. With the convert option, the
    particle shape and its transform are simply inserted below the original shape's hierarchy. With the duplicate option,
    the original geometry's transform and shape are duplicated underneath its parent, and the particle shape is placed under
    the duplicate.  Note that any animation on the hierarchy will affect the particle shape as well.  If you do not want
    then, then reparent the structure outside the hierarchy. When duplicating, the soft portion (the duplicate) is given the
    name copyOf+ original object name.  The particle portion is always given the name original object name+ Particles.None
    of the flags of the soft command can be queried.  The soft -q command is used only to identify when an object is a soft
    body, or when two objects are part of the same soft body. See the examples.
    
    Flags:
      - convert : c                    (bool)          [create]
          This tells the command that you want the original object to be the actual deformed object.  The particle shape portion
          of the soft body will be inserted in the same hierarchy as the original, under the same parent (with one additional
          intervening transform which is initially the identity).  If no flags are passed, then this is assumed.  The combination
          -c -h 1 is not valid; if you have this in your scripts, remove the -h 1.
    
      - duplicate : d                  (bool)          [create]
          This tells the command that you want to make a copy of the original object and use the copy as the deforming geometry.
          Input connections to the original object are duplicated.  You would do this if you wanted to keep the original object in
          your scene and also have a copy of it that was a soft body. This flag and -dh are mutually exclusive.
    
      - duplicateHistory : dh          (bool)          [create]
          This is the same as -d, except that upstream history, is duplicated as well, instead of just input connections. This
          flag and -d are mutually exclusive.
    
      - goal : g                       (float)         [create]
          This is the same as -d, but in addition it tells the command that you want the resulting soft body to try to follow the
          original geometry, using the set goal weight as the value that controls how strongly it is to follow it.  A value of 1.0
          will try to follow exactly, and a value of 0.0 will not follow at all. The default value is 0.5.  This value must be
          from 0.0 to 1.0. You could use -d with -g, but it is redundant.  If you want history to be duplicated, you can use -dh
          and -g together.
    
      - hideOriginal : h               (bool)          [create]
          This flag is used only when duplicating (-d, -g, or -dh).  If set to true, whichever of the two objects is NOT the soft
          object will be hidden. In other words, with -d -h true, the original object will be hidden; with -d -c -h 1 the
          duplicate object will be hidden. You would typically do this if you want to use the non-dynamic object as a goal for the
          soft one (see -g) but you do not want it visible in the scene. The flags -h 1 and -c are mutually exclusive.
    
      - name : n                       (unicode)       []
          This flag is obsolete.  If you wish to give your new soft object a name, use the rename command (or from the UI, use the
          outliner).                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.soft`
    """

    pass


def colorAtPoint(*args, **kwargs):
    """
    The colorAtPointcommand is used to query textures or ocean           shaders at passed in uv coordinates.       (For
    ocean shaders uv is x and z in worldspace ).           The return value is a floating point array whose size is
    determined by either the number of input uv arguments passed in and the           the queried value.  One can query
    alpha only, rgb only, or rgba values.           The returned array is only single indexed, so if rgb is specified then
    the index for red values would be index \* 3. Blue is index \* 3 + 1, and           green is index \* 3 + 2. For rgba
    use a multiple of 4 instead of 3.           For alpha only one can simply use the index.           There are two basic
    argument formats that may be used:           colorAtPoint -u 0 -v 0   -u .2 -v .1  etc.. for all points           or
    colorAtPoint -mu 0 -mv 0  -xu 1 -xv 1 -su 10 -sv 10 // samples 100 points           If one is sampling several points
    and they are all in a regular grid           formation it is more efficient to call this routine with the latter
    method, which uses a min/max uv and number of samples, rather than           a long argument list of uv coords.
    return values (-o A or RGB or RGBA )individual UV coordinates to sample (-u float  -v float )(numbers of calls to -u and
    -v must match)uniform grid of points to sample (-su int -sv int)(may not use this in combination with -u or -v)bounds
    for sample grid  (-mu float  -mv float -xu float -xv float)
    
    Flags:
      - coordU : u                     (float)         [create]
          Input u coordinate to sample texture at.
    
      - coordV : v                     (float)         [create]
          Input v coordinate to sample texture at.
    
      - maxU : xu                      (float)         [create]
          DEFAULT 1.0 Maximum u bounds to sample.
    
      - maxV : xv                      (float)         [create]
          DEFAULT 1.0 Maximum v bounds to sample.
    
      - minU : mu                      (float)         [create]
          DEFAULT 0.0 Minimum u bounds to sample.
    
      - minV : mv                      (float)         [create]
          DEFAULT 0.0 Minimum v bounds to sample.
    
      - output : o                     (unicode)       [create]
          Type of data to output:         A        = alpha only         RGB  = color only         RGBA = color and alpha
    
      - samplesU : su                  (int)           [create]
          DEFAULT 1 The number of points to sample in the U dimension.
    
      - samplesV : sv                  (int)           [create]
          DEFAULT 1 The number of points to sample in the V dimension.                               Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.colorAtPoint`
    """

    pass


def setParticleAttr(*args, **kwargs):
    """
    This action will set the value of the chosen attribute for every particle or selected component in the selected or
    passed particle object. Components should not be passed to the command line. For setting the values of components, the
    components must be selected and only the particle object's names should be passed to this action. If the attribute is a
    vector attribute and the -vv flag is passed, then the three floats passed will be used to set the values.  If the
    attribute is a vector and the -fv flag is pass and the -vv flag is not passed, then the float will be repeated for each
    of the X, Y, and Z values of the attribute.  Similarly, if the attribute is a float attribute and a vector value is
    passed, then the length of the vector passed will be used for the value. Note:  The attribute passed must be a Per-
    Particle attribute.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          Tells the action which attribute you want to set
    
      - floatValue : fv                (float)         [create]
          Tells what you want the value to be set to of a float attribute
    
      - object : o                     (unicode)       [create]
          If this flag is passed and the STRING is the name of a particle object's transform or shape, then ONLY that object will
          be edited, ignoring the selection list or command line, and ALL of its particles' values will be changed for the
          specified attribute.
    
      - randomFloat : rf               (float)         [create]
          Tells the command to add a random value from -FLOAT to +FLOAT to the results of each particle.  The default is 0.0.
    
      - randomVector : rv              (float, float, float) [create]
          Tells the command to add a random value from -x,-y,-zto x,y,zto the results of each particle. The default 0 0 0.
    
      - relative : r                   (bool)          [create]
          If this is set to TRUE (the default is FALSE), then the float or vector value will be added to the current value for
          each particle.
    
      - vectorValue : vv               (float, float, float) [create]
          Tells what you want the value to be set to of a vector attribute                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.setParticleAttr`
    """

    pass


def pfxstrokes(*args, **kwargs):
    """
    This command will loop through all the Paint Effects strokes, including pfxHair nodes, and write the current state of
    all the tubes to a file. For normal stroke nodes tubes must be ON in the brush or there will be no output. For pfxHair
    nodes there will always be output, but the format is different than for stroke nodes(however one can assign a brush with
    tubes = ON to a pfxHair node, in which case it will output the same format as strokes). The general file format is
    ASCII, using commas to separate numerical values and newlines between blocks of data. The format used for pfxHair nodes
    presents the hair curves points in order from root to tip of the hair. The hairs follow sequentially in the following
    fashion: NumCvs pointX,pointY,pointZ, normalX,normalY,normalZ, width, colorR,colorG,colorB, paramU pointX,pointY,pointZ,
    normalX,normalY,normalZ, width, colorR,colorG,colorB, paramU etc... NumCvs pointX,pointY,pointZ,
    normalX,normalY,normalZ, width, colorR,colorG,colorB, paramU etc.. The format used to output files for brushes with
    tubes=ON is more complex. The tubes can branch and the order the segments are written is the same order they are drawn
    in. Slowly drawing a tall grass brush in the paint effects panel can help to illustrate the order the segments will
    appear in the file. New tubes can start growingbefore others are finished. There is no line for NumCvs. Instead all data
    for each segment appears on each line. The data on each line is the same as passed into the paint effects runtime
    function. See the argument list of paintRuntimeFunc.mel for the order and a description of these parameters. The
    parameters match up exactly in the order they appear on a line of the output file with the order of arguments to this
    function. If one wishes to parse the output file and connect the segments together into curves the branchId, parentId
    and siblingCnt parameters can help when sorting which segment connects to which line. Using the -postCallback option
    will write out the tubes data after it has been proessed by the runTime callback.
    
    Flags:
      - filename : fn                  (unicode)       [create]
          The output file.
    
      - postCallback : pc              (bool)          [create]
          Output information to the file after the Runtime Callback MEL function has been invoked. The default is to output the
          information prior to the callback.
    
      - selected : sl                  (bool)          [create]
          Only loop through the selected strokes.                                    Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.pfxstrokes`
    """

    pass


def getDefaultBrush(*args, **kwargs):
    """
    The command returns the name of the default Paint Effects brush.
    
    
    Derived from mel command `maya.cmds.getDefaultBrush`
    """

    pass


def connectDynamic(*args, **kwargs):
    """
    Dynamic connection specifies that the force fields, emitters, or collisions of an object affect another dynamic object.
    The dynamic object that is connected to a field, emitter, or collision object is influenced by those fields, emitters
    and collision objects. Connections are made to individual fields, emitters, collisions.  So, if an object owns several
    fields, if the user wants some of the fields to affect an object, s/he can specify each field with a -fflag; but if the
    user wants to connect all the fields owned by an object, s/he can specify the object name with the -fflag. The same is
    true for emitters and collisions. Different connection types (i.e., for fields vs. emitters) between the same pair of
    objects are logically independent. In other words, an object can be influenced by another object's fields without being
    influenced by its emitters or collisions. Each connected object must be a dynamic object. The object connected to can be
    any object that owns fields, emitters, etc.; it need not be dynamic. Objects that can own influences are particles,
    geometry objects (nurbs and polys) and lattices.  You can specify either the shape name or the transform name of the
    object to be influenced.
    
    Flags:
      - addScriptHandler : ash         (script)        [create]
          Registers a script that will be given a chance to handle calls to the dynamicConnect command. This flag allows other
          dynamics systems to override the behaviour of the connectDynamic command. You must pass a Python function as the
          argument for this flag, and that function must take the following keyword arguments: fields, emitters, collisionObjects
          and objects. The python function must return True if it has handled the call to connectDynamic. In the case that the
          script returns true, the connectDynamic command will not do anything as it assumes that the work was handled by the
          script. If all of the callbacks return false, the connectDynamic command will proceed as normal.  The addScriptHandler
          flag may not be used with any other flags. When the flag is used, the command will return a numerical id that can be
          used to deregister the callback later (see the removeScriptHandler flag)
    
      - collisions : c                 (unicode)       [create]
          Connects each object to the collision models of the given object.
    
      - delete : d                     (bool)          [create]
          Deletes existing connections.
    
      - emitters : em                  (unicode)       [create]
          Connects each object to the emitters of the given object.
    
      - fields : f                     (unicode)       [create]
          Connects each object to the fields of the given object.
    
      - removeScriptHandler : rsh      (int)           [create]
          This flag is used to remove a callback that was previously registered with the addScriptHandler flag. The argument to
          this flag is the numerical id returned by dynamicConnect when the addScriptHandler flag was used. If this flag is called
          with an invalid id, then the command will do nothing.  This flag may not be used with any other flag.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.connectDynamic`
    """

    pass


def drag(*args, **kwargs):
    """
    Drag exerts a friction, or braking force proportional to the speed of a moving object. If direction is not enabled, the
    drag acts opposite to the current velocity of the object. If direction is enabled, it acts opposite to the component of
    the velocity in the specified direction. The force is independent of the position of the affected object. The transform
    is the associated dependency node. Use connectDynamic to cause the field to affect a dynamic object. If fields are
    created, this command returns the names of each of the fields. If a field was queried, the results of the query are
    returned. If a field was edited, the field name is returned. If object names are provided or the active selection list
    is non-empty, the command creates a field for every object in the list and calls addDynamic to add it to the object. If
    the list is empty, the command defaults to -pos 0 0 0. Setting the -pos flag with objects named on the command line is
    an error.
    
    Flags:
      - attenuation : att              (float)         [query,edit]
          Attentuation rate of field
    
      - directionX : dx                (float)         [query,edit]
          X-component of direction.
    
      - directionY : dy                (float)         [query,edit]
          Y-component of direction.
    
      - directionZ : dz                (float)         [query,edit]
          Z-component of direction
    
      - magnitude : m                  (float)         [query,edit]
          Strength of field.
    
      - maxDistance : mxd              (float)         [query,edit]
          Maximum distance at which field is exerted. -1 indicates that the field has no maximum distance.
    
      - name : n                       (unicode)       [query,edit]
          name of field
    
      - perVertex : pv                 (bool)          [query,edit]
          Per-vertex application. If this flag is set true, then each individual point (CV, particle, vertex,etc.) of the chosen
          object exerts an identical copy of the force field. If this flag is set to false, then the force is exerted only from
          the geometric center of the set of points.
    
      - position : pos                 (float, float, float) [query,edit]
          Position in space where you want to place a field. The gravity then emanates from this position in space rather than
          from an object. Note that you can both use -pos (creating a field at a position) and also provide object names.
    
      - torusSectionRadius : tsr       (float)         [query,edit]
    
      - useDirection : ud              (bool)          [query,edit]
          Enable/disable direction. Drag will use -dx/-dy/-dz arguments if and only if this flag is set true.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - volumeExclusion : vex          (bool)          [query,edit]
    
      - volumeOffset : vof             (float, float, float) [query,edit]
    
      - volumeShape : vsh              (unicode)       [query,edit]
    
      - volumeSweep : vsw              (float)         [query,edit]
    
    
    Derived from mel command `maya.cmds.drag`
    """

    pass


def truncateHairCache(*args, **kwargs):
    """
    This command sets the end time of a hair cache to the current time. If the current time is less than the end time of the
    cache, the cache is truncated so that only the portion of the cache up to and including the current time is preserved.
    In query mode, return type is based on queried flag.
    
    
    Derived from mel command `maya.cmds.truncateHairCache`
    """

    pass


def truncateFluidCache(*args, **kwargs):
    """
    This command sets the end time of a fluid cache to the current time. If the current time is less than the end time of
    the cache, the cache is truncated so that only the portion of the cache up to and including the current time is
    preserved.                 In query mode, return type is based on queried flag.
    
    
    Derived from mel command `maya.cmds.truncateFluidCache`
    """

    pass


def paintEffectsDisplay(*args, **kwargs):
    """
    Command to set the global display methods for paint effects items                In query mode, return type is based on
    queried flag.
    
    Flags:
      - meshDrawEnable : me            (bool)          [create,query]
          Set whether mesh draw is enabled on objects                                Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.paintEffectsDisplay`
    """

    pass


def gravity(*args, **kwargs):
    """
    A gravity field simulates the Earth's gravitational force.   It pulls objects in a fixed direction (generally downward)
    entirely independent of their position or mass. The transform is the associated dependency node. Use connectDynamic to
    cause the field to affect a dynamic object. If fields are created, this command returns the names of each of the fields.
    If a field was queried, the results of the query are returned. If a field was edited, the field name is returned. If
    object names are provided or the active selection list is non-empty, the command creates a field for every object in the
    list and calls addDynamic to add it to the object. If the list is empty, the command defaults to -pos 0 0 0. Setting the
    -pos flag with objects named on the command line is an error. The default for -dx -dy -dz is always the opposite of the
    current up direction. For example, if the current up direction is (0,1,0) (a standard Maya configuration), then the
    gravity default is -dx 0 -dy -1 -dz 0.  The default for -a is 9.8.  9.8 meters per second squared happens to be standard
    Earth gravity, but in fact Maya interprets this value as centimeters per second squared.  If we were to use it as meters
    per second squared then with default Maya units, your particles would vanish almost in the wink of an eye. If you want a
    different value, set it in the gravity option box.
    
    Flags:
      - attenuation : att              (float)         [query,edit]
          Attentuation rate of field
    
      - directionX : dx                (float)         [query,edit]
          X-component of direction.
    
      - directionY : dy                (float)         [query,edit]
          Y-component of direction.
    
      - directionZ : dz                (float)         [query,edit]
          Z-component of direction
    
      - magnitude : m                  (float)         [query,edit]
          Strength of field.
    
      - maxDistance : mxd              (float)         [query,edit]
          Maximum distance at which field is exerted. -1 indicates that the field has no maximum distance.
    
      - name : n                       (unicode)       [query,edit]
          name of field
    
      - perVertex : pv                 (bool)          [query,edit]
          Per-vertex application. If this flag is set true, then each individual point (CV, particle, vertex,etc.) of the chosen
          object exerts an identical copy of the force field. If this flag is set to false, then the force is exerted only from
          the geometric center of the set of points.
    
      - position : pos                 (float, float, float) [query,edit]
          Position in space where you want to place a field. The gravity then emanates from this position in space rather than
          from an object. Note that you can both use -pos (creating a field at a position) and also provide object names.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - torusSectionRadius : tsr       (float)         [query,edit]
    
      - volumeExclusion : vex          (bool)          [query,edit]
    
      - volumeOffset : vof             (float, float, float) [query,edit]
    
      - volumeShape : vsh              (unicode)       [query,edit]
    
      - volumeSweep : vsw              (float)         [query,edit]
    
    
    Derived from mel command `maya.cmds.gravity`
    """

    pass


def collision(*args, **kwargs):
    """
    The collision command causes particles to collide with geometry. It also allows you to specify values for the surface
    properties (friction and resilience) of the collision.  These values are stored in the geoConnector node for the
    geometry object.  Unlike earlier versions of Maya, there is no separate collision node.If a soft object is in the
    selection list, the collision command assumes that you want to make it a collider.  In order to make the soft object
    collide with something use, use connectDynamic -c.  The collision menu option sorts this out using the lead object rule
    and issues the necessary commands. On creation, this command returns a string arrayof the geometry names that were setup
    for particle collision.When the command is used to query information, there are several possible return types. These
    include: If the -resilience or -friction flag is passed on the command line and a single collision geometry is either
    selected or on the command line, then resilience or friction value for that collision geometry is returned as a single
    floatvalue.If the -resilience or -friction flag is passed on the command line and a single collision geometry and a
    single particle object are either selected or on the command line, then two results might occur. If the particle object
    is not set up to collide with the geometry, then an error is displayed stating that.  If the objects are set up to
    collide with each other, then the resilience or friction value that the particle object is using for collisions with the
    geometry is returned as a single floatvalue.  This can be different than the geometry's resilience and friction, because
    the user may break the connection from the geometry's geoConnector node's resilience or friction to the particle, and
    set a different value in the particle's collisionResilience, collisionFriction or collisionOffset attribute that is used
    for that geometry.  This allows the user to make each particle respond to the same surface differently. If neither flag
    is pass on the command line and a single geometry and single particle object are either selected or on the command line,
    then a single integervalue of 1 is returned if the objects are set up to collide with each other, and 0 is returned if
    they are not. Lastly, if no flags are passed on the command line and a single particle object is either selected or on
    the command line, then a string arraywith the names of all geometries that the particle object will collide against and
    the multiIndex that the geometries are connected to is returned.  The array is formatted as follows: pPlaneShape1:0
    pPlaneShape2:2 nurbsSphereShape1:3 ...where the number following the :is the multiIndex.
    
    Flags:
      - friction : f                   (float)         [query,edit]
          Friction of the surface.  This is the amount of the colliding particle's velocity parallel to the surface which is
          removed when the particle collides. A value of 0 will mean that no tangential velocity is lost, while a value of 1 will
          cause the particle to reflect straight along the normal of the surface.
    
      - name : n                       (unicode)       []
          This flag is obsolete.  In maya 2.0, there is no longer a separate collision node,thus there is nothing to name.  See
          the collision documentation.  This flag is included only to allow scripts written with older versions of Maya to run. It
          will give you a warning message but will not do anything.
    
      - offset : o                     (float)         []
    
      - resilience : r                 (float)         [query,edit]
          Resilience of the surface.  This is the amount of the colliding particle's velocity reflected along the normal of the
          surface.  A value of 1 will give perfect reflection, while a value of 0 will have no reflection along the normal of the
          surface.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.collision`
    """

    pass


def nSoft(*args, **kwargs):
    """
    Makes a nSoft body from the object(s) passed on the command line or in the selection list.  The geometry can be a NURBS,
    polygonal, lattice object.  The resulting nSoft body is made up of a hierarchy with a particle shape and a geometry
    shape, thus: T    / \  T   G /      P        Dynamics are applied to the particle shape and the resulting particle
    positions then drive the locations of the geometry's CVs, vertices, or lattice points. With the convert option, the
    particle shape and its transform are simply inserted below the original shape's hierarchy. With the duplicate option,
    the original geometry's transform and shape are duplicated underneath its parent, and the particle shape is placed under
    the duplicate.  Note that any animation on the hierarchy will affect the particle shape as well.  If you do not want
    them, then reparent the structure outside the hierarchy. When duplicating, the nSoft portion (the duplicate) is given
    the name copyOf+ original object name.  The particle portion is always given the name original object name+
    Particles.None of the flags of the nSoft command can be queried.  The nSoft -q command is used only to identify when an
    object is a nSoft body, or when two objects are part of the same nSoft body. See the examples.
    
    Flags:
      - convert : c                    (bool)          [create]
          This tells the command that you want the original object to be the actual deformed object.  The particle shape portion
          of the nSoft body will be inserted in the same hierarchy as the original, under the same parent (with one additional
          intervening transform which is initially the identity).  If no flags are passed, then this is assumed.  The combination
          -c -h 1 is not valid; if you have this in your scripts, remove the -h 1.
    
      - duplicate : d                  (bool)          [create]
          This tells the command that you want to make a copy of the original object and use the copy as the deforming geometry.
          Input connections to the original object are duplicated.  You would do this if you wanted to keep the original object in
          your scene and also have a copy of it that was a nSoft body. This flag and -dh are mutually exclusive.
    
      - duplicateHistory : dh          (bool)          [create]
          This is the same as -d, except that upstream history, is duplicated as well, instead of just input connections. This
          flag and -d are mutually exclusive.
    
      - goal : g                       (float)         [create]
          This is the same as -d, but in addition it tells the command that you want the resulting nSoft body to try to follow the
          original geometry, using the set goal weight as the value that controls how strongly it is to follow it.  A value of 1.0
          will try to follow exactly, and a value of 0.0 will not follow at all. The default value is 0.5.  This value must be
          from 0.0 to 1.0. You could use -d with -g, but it is redundant.  If you want history to be duplicated, you can use -dh
          and -g together.
    
      - hideOriginal : h               (bool)          [create]
          This flag is used only when duplicating (-d, -g, or -dh).  If set to true, whichever of the two objects is NOT the nSoft
          object will be hidden. In other words, with -d -h true, the original object will be hidden; with -d -c -h 1 the
          duplicate object will be hidden. You would typically do this if you want to use the non-dynamic object as a goal for the
          nSoft one (see -g) but you do not want it visible in the scene. The flags -h 1 and -c are mutually exclusive.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - name : n                       (unicode)       []
    
    
    Derived from mel command `maya.cmds.nSoft`
    """

    pass


def setFluidAttr(*args, **kwargs):
    """
    Sets values of built-in fluid attributes such as density, velocity, etc., for individual grid cells or for all cells in
    the grid.
    
    Flags:
      - addValue : ad                  (bool)          []
          Add specified value to attribute
    
      - attribute : at                 (unicode)       [create]
          Specifies the fluid attribute for which to set values.  Valid attributes are velocity, density, fuel, color, falloff,
          and temperature.
    
      - clear : cl                     (bool)          []
          Set this attribute to 0
    
      - floatRandom : fr               (float)         []
          If this was a scalar (e.g. density) attribute, use a random value in +-VALUE If fv is specified, it is used as the base
          value and combined with the random value. If the fv flag is not specified, the  base is assumed to be 0.
    
      - floatValue : fv                (float)         []
          If this was a scalar (e.g. density) attribute, use this value
    
      - lowerFace : lf                 (bool)          [create]
          Only valid with -at velocity.  Since velocity values are stored on the edges of each voxel and not at the center, using
          voxel based indices to set velocity necessarily affects neighboring voxels.  Use this flag to only set velocity
          components on the lower left three faces of a voxel, rather than all six.
    
      - reset : re                     (bool)          []
          Set this attribute to default value
    
      - vectorRandom : vr              (float, float, float) []
          If this was a vector (e.g. velocity) attribute, use a random value in +-VALUE If vv is specified, it is used as the base
          value and combined with the random value. If the vv flag is not specified, the  base is assumed to be 0,0,0.
    
      - vectorValue : vv               (float, float, float) []
          If this was a vector (e.g. velocity) attribute, use this value
    
      - xIndex : xi                    (int)           [create]
          Only return values for cells with this X index
    
      - xvalue : x                     (bool)          []
          Only set the first component of the vector-valued attribute specified by the -at/attributeflag.
    
      - yIndex : yi                    (int)           [create]
          Only return values for cells with this Y index
    
      - yvalue : y                     (bool)          []
          Only set the second component of the vector-valued attribute specified by the -at/attributeflag.
    
      - zIndex : zi                    (int)           [create]
          Only return values for cells with this Z index
    
      - zvalue : z                     (bool)          []
          Only set the third component of the vector-valued attribute specified by the -at/attributeflag.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.setFluidAttr`
    """

    pass


def arrayMapper(*args, **kwargs):
    """
    Create an arrayMapper node and connect it to a target object. If the -type flag is used, then this command also creates
    an external node used for computing the output values. If the input attribute does not already exist, it will be
    created. The output attribute must exists. If    a flag is omitted, the selection list will be used to supply the needed
    objects. If none are found, that action is omitted.
    
    Flags:
      - destAttr : da                  (unicode)       [create]
          Specifies the attribute which will be the downstream connection for the output data from the mapper node. The attribute
          type will be used to determine which output attribute to use: float array gets outValuePP, vector array gets outColorPP.
          If the flag is omitted, no output connection is made.
    
      - inputU : iu                    (unicode)       [create]
          Specifies the upstream attribute to connect to the mapper's uCoordPP attribute. If the flag is omitted, no input
          connection is made.
    
      - inputV : iv                    (unicode)       [create]
          Specifies the upstream attribute to connect to the mapper's vCoordPP attribute. If the flag is omitted, no input
          connection is made.
    
      - mapTo : mt                     (unicode)       [create]
          Specifies an existing node to be used to compute the output values. This node must be of the appropriate type.
          Currently, only ramp nodes may be used.
    
      - target : t                     (unicode)       [create]
          Specifies the target object to be connected to.
    
      - type : ty                      (unicode)       [create]
          Specifies the node type to create which will be used to compute the output values. Currently, only ramp is valid. If the
          flag is omitted, no connection is made and the external node is not created.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.arrayMapper`
    """

    pass


def nParticle(*args, **kwargs):
    """
    The nParticle command creates a new nParticle object from a list of world space points. If an nParticle object is
    created, the command returns the names of the new particle shape and its associated particle object dependency node. If
    an object was queried, the results of the query are returned. Per particle attributes can be queried using the
    particleId or the order of the particle in the particle array. If an object was edited, nothing is returned.
    
    Flags:
      - attribute : at                 (unicode)       [query,edit]
          Used in per particle attribute query and edit. Specifies the name of the attribute being queried or edited.
    
      - cache : ch                     (bool)          [create,query,edit]
          Turns caching on/off for the particle shape.
    
      - conserve : c                   (float)         [query,edit]
          Conservation of momentum control (between 0 and 1).  Specifies the fraction of the particle shape's existing momentum
          which is conserved from frame to frame. A value of 1 (the default) corresponds to true Newtonian physics, in which
          momentum is conserved.
    
      - count : ct                     (bool)          [query]
          Returns the number of particles in the object.
    
      - deleteCache : dc               (bool)          [create]
          Deletes the particle shapes cache. This command is not undoable.
    
      - dynamicAttrList : dal          (bool)          [query]
          Returns a list of the dynamic attributes in the object.
    
      - floatValue : fv                (float)         [edit]
          Used only in per particle attribute edit.  Specifies that the edit is of a float attribute and must be followed by the
          new float value.
    
      - gridSpacing : grs              (float)         [create,query]
          Spacing between particles in the grid.
    
      - inherit : i                    (float)         [query,edit]
          Inherit this fraction (0-1) of emitting object's velocity.
    
      - jitterBasePoint : jbp          (float, float, float) [create,query]
          Base point (center point) for jitters.  The command will create one swatch of jitters for each base point.  It will pair
          up other flags with base points in the order they are given in the command line.  If not enough instances of the other
          flags are availble, the last one on the line with be used for all other instances of -jpb.
    
      - jitterRadius : jr              (float)         [create,query]
          Max radius from the center to place the particle instances.
    
      - lowerLeft : ll                 (float, float, float) [create,query]
          Lower left point of grid.
    
      - name : n                       (unicode)       [query,edit]
          name of particle object
    
      - numJitters : nj                (int)           [create,query]
          Number of jitters (instances) per particle.
    
      - order : order                  (int)           [query,edit]
          Used in per particle attribute query and edit. Specifies the zero-based order (index) of the particle whose attribute is
          being queried  or edited in the particle array. Querying the value of a per particle attribute requires the -attribute
          and -id or -order flags and their arguments to precede the -q flag.
    
      - particleId : id                (int)           [query,edit]
          Used in per particle attribute query and edit. Specifies the id of the particle whose attribute is being queried or
          edited. Querying the value of a per particle attribute requires the -attribute and -id or -order flags and their
          arguments to precede the -q flag.
    
      - perParticleDouble : ppd        (bool)          [query]
          Returns a list of the per-particle double attributes, excluding initial-state, cache, and information-only attributes.
    
      - perParticleVector : ppv        (bool)          [query]
          Returns a list of the per-particle vector attributes, excluding initial-state, cache, and information-only attributes.
    
      - position : p                   (float, float, float) []
          World-space position of each particle.
    
      - shapeName : sn                 (unicode)       [query,edit]
          Specify the shape name used for geometry instancing. DO not confuse this with the -n flag which names the particle
          object.
    
      - upperRight : ur                (float, float, float) [create,query]
          Upper right point of grid.
    
      - vectorValue : vv               (float, float, float) [edit]
          Used only in per particle attribute edit.  Specifies that the edit is of a vector attribute and must be followed by all
          three float values for the vector.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.nParticle`
    """

    pass


def fluidVoxelInfo(*args, **kwargs):
    """
    Provides basic information about the mapping of a fluid voxel grid into world- or object space of the fluid.  Use this
    command to determine the center point of a voxel, or to find the voxel containing a given point, among other things.
    
    Flags:
      - checkBounds : cb               (bool)          [create]
          If this flag is on, and the voxel index of a point that is out of bounds is requested, then we return nothing.
    
      - inBounds : ib                  (int, int, int) [create]
          Are the three ints representing the x, y, z indices of a voxel within the bounds of the fluid's voxel grid?  True if
          yes, false if not.  (For 2D fluids, pass in z=0 for the third argument.  See examples.)
    
      - objectSpace : os               (bool)          [create]
          Whether the queried value should be returned in object space (TRUE), or world space (FALSE, the default).
    
      - radius : r                     (float)         [create]
          Modifier for the -voxel flag.  Returns a list of index triples identifying voxels that fall within the given radius of
          the point specified by the -voxel flag.
    
      - voxel : v                      (float, float, float) [create]
          Returns array of three ints representing the x, y, z indices of the voxel within which the given point position is
          contained. If the checkBounds flag is on, and the point is out of bounds, we return nothing. Otherwise, even if the
          point is out of bounds, index values are returned. When combined with the -radius flag, returns an array of index
          triples representing a list of voxels within a given radius of the given point position.
    
      - voxelCenter : vc               (bool)          [create]
          The center position of the specified voxels.  Returns an array of floats (three for each of the indices in the query).
          (Valid only with the -xIndex, -yIndex, and -zIndex flags.)
    
      - xIndex : xi                    (int)           [create]
          Only return values for cells with this X index
    
      - yIndex : yi                    (int)           [create]
          Only return values for cells with this Y index
    
      - zIndex : zi                    (int)           [create]
          Only return values for cells with this Z index                             Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.fluidVoxelInfo`
    """

    pass


def turbulence(*args, **kwargs):
    """
    A turbulence field causes irregularities (also called 'noise' or 'jitter') in the motion of affected objects. Use
    connectDynamic to cause the field to affect a dynamic object. If fields are created, this command returns the names of
    each of the fields. If a field was queried, the results of the query are returned. If a field was edited, the field name
    is returned. If object names are provided or the active selection list is non-empty, the command creates a field for
    every object in the list and calls addDynamic to add it to the object. If the list is empty, the command defaults to
    -pos 0 0 0. Setting the -pos flag with objects named on the command line is an error.
    
    Flags:
      - attenuation : att              (float)         [query,edit]
          Attentuation rate of field
    
      - frequency : f                  (float)         [query,edit]
          Frequency of turbulence field. This determines how often motion is disrupted.
    
      - magnitude : m                  (float)         [query,edit]
          Strength of field. As this increases, the affected objects will move faster.
    
      - maxDistance : mxd              (float)         [query,edit]
          Maximum distance at which field is exerted.
    
      - name : n                       (unicode)       [query,edit]
          name of field
    
      - noiseLevel : nsl               (int)           [query,edit]
          If the noiseLevel parameter is greater than zero, the field will do multiple lookups in the table.  Each additional
          lookup is weighted using noiseRatio (which see).  The noiseLevel is the number of additional lookups, so if noiseLevel
          is 0, there is just one lookup.  A value of 0 (the default) corresponds to the way the field behaved prior to Maya 3.0.
    
      - noiseRatio : nsr               (float)         [query,edit]
          If noiseLevel is greater than zero, then noiseRatio is the relative magnitude for each consecutive noise evaluation.
          These are cumulative: for example, if noiseRatio is 0.5, then the first evaluation is weighted 0.5, the second 0.25, and
          so on. Has no effect if noiseLevel is zero.
    
      - perVertex : pv                 (bool)          [query,edit]
          Per-vertex application. If this flag is set true, then each individual point (CV, particle, vertex,etc.) of the chosen
          object exerts an identical copy of the force field. If this flag is set to false, then the force is exerted only from
          the geometric center of the set of points.
    
      - phase : p                      (float)         [query,edit]
          Phase shift of turbulence field. This influences the direction of the disruption.  This flag is obsolete and is retained
          only for backward compatibility.  It is replaced by -phaseX, -phaseY, and -phaseZ.  Setting -phase is identical to
          setting -phaseZ (the phase shift was always in the Z dimension).
    
      - phaseX : px                    (float)         [query,edit]
          X component of phase shift of turbulence field. This influences the direction of the disruption.
    
      - phaseY : py                    (float)         [query,edit]
          Y component of phase shift of turbulence field. This influences the direction of the disruption.
    
      - phaseZ : pz                    (float)         [query,edit]
          Z component of phase shift of turbulence field. This influences the direction of the disruption.
    
      - position : pos                 (float, float, float) [query,edit]
          Position in space where you want to place a field. The field then emanates from this position in space rather than from
          an object. Note that you can both use -pos (creating a field at a position) and also provide object names.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - torusSectionRadius : tsr       (float)         [query,edit]
    
      - volumeExclusion : vex          (bool)          [query,edit]
    
      - volumeOffset : vof             (float, float, float) [query,edit]
    
      - volumeShape : vsh              (unicode)       [query,edit]
    
      - volumeSweep : vsw              (float)         [query,edit]
    
    
    Derived from mel command `maya.cmds.turbulence`
    """

    pass


def dynPref(*args, **kwargs):
    """
    This action modifies and queries the current state of autoCreate rigid bodies, run up to current time, and  run up
    from(previous time or start time). In query mode, return type is based on queried flag.
    
    Flags:
      - autoCreate : ac                (bool)          [create,query]
          If on, autoCreate rigid bodies.
    
      - echoCollision : ec             (bool)          [create,query]
          If on, will cause particle systems to echo to the Script Editor the command that they are running for each particle
          collision event. If off, only the output of the command will be echoed.
    
      - runupFrom : rf                 (int)           [create,query]
          If on, run up from previous time; if 2, run up from start time
    
      - runupToCurrentTime : rt        (bool)          [create,query]
          If on, run up the scene to current time
    
      - saveOnQuit : sq                (bool)          [create,query]
          If on, save the current values of preferences to userPrefs file.
    
      - saveRuntimeState : sr          (bool)          [create,query]
          If on, runtime state as well as initial state of all particle objects will be saved to file. If off, only initial state
          will be saved.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dynPref`
    """

    pass


def runup(*args, **kwargs):
    """
    runup plays the scene through a frame of frames, forcing dynamic objects to evaluate as it does so.   If no max frame is
    specified, runup runs up to the current time.
    
    Flags:
      - cache : cch                    (bool)          [create]
          Cache the state after the runup.
    
      - fromPreviousFrame : fpf        (bool)          [create]
          Run up the animation from the previously evaluated frame. If no flag is supplied this is the default.
    
      - fromStartFrame : fsf           (bool)          [create]
          Run up the animation from the start frame. If no flag is supplied -fromPreviousFrame is the default.
    
      - maxFrame : mxf                 (time)          [create]
          Ending time for runup, in current user time units. The runup will always start at the minimum start frame for all
          dynamic objects.
    
      - state : st                     (bool)          [create]
          Turns runup and cache on/off.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.runup`
    """

    pass


def particle(*args, **kwargs):
    """
    The particle command creates a new particle object from a list of world space points. If a particle object is created,
    the command returns the names of the new particle shape and its associated particle object dependency node. If an object
    was queried, the results of the query are returned. Per particle attributes can be queried using the particleId or the
    order of the particle in the particle array. If an object was edited, nothing is returned.
    
    Flags:
      - attribute : at                 (unicode)       [query,edit]
          Used in per particle attribute query and edit. Specifies the name of the attribute being queried or edited.
    
      - cache : ch                     (bool)          [create,query,edit]
          Turns caching on/off for the particle shape.
    
      - conserve : c                   (float)         [query,edit]
          Conservation of momentum control (between 0 and 1).  Specifies the fraction of the particle shape's existing momentum
          which is conserved from frame to frame. A value of 1 (the default) corresponds to true Newtonian physics, in which
          momentum is conserved.
    
      - count : ct                     (bool)          [query]
          Returns the number of particles in the object.
    
      - deleteCache : dc               (bool)          [create]
          Deletes the particle shapes cache. This command is not undoable.
    
      - dynamicAttrList : dal          (bool)          [query]
          Returns a list of the dynamic attributes in the object.
    
      - floatValue : fv                (float)         [edit]
          Used only in per particle attribute edit.  Specifies that the edit is of a float attribute and must be followed by the
          new float value.
    
      - gridSpacing : grs              (float)         [create,query]
          Spacing between particles in the grid.
    
      - inherit : i                    (float)         [query,edit]
          Inherit this fraction (0-1) of emitting object's velocity.
    
      - jitterBasePoint : jbp          (float, float, float) [create,query]
          Base point (center point) for jitters.  The command will create one swatch of jitters for each base point.  It will pair
          up other flags with base points in the order they are given in the command line.  If not enough instances of the other
          flags are availble, the last one on the line with be used for all other instances of -jpb.
    
      - jitterRadius : jr              (float)         [create,query]
          Max radius from the center to place the particle instances.
    
      - lowerLeft : ll                 (float, float, float) [create,query]
          Lower left point of grid.
    
      - name : n                       (unicode)       [query,edit]
          name of particle object
    
      - numJitters : nj                (int)           [create,query]
          Number of jitters (instances) per particle.
    
      - order : order                  (int)           [query,edit]
          Used in per particle attribute query and edit. Specifies the zero-based order (index) of the particle whose attribute is
          being queried  or edited in the particle array. Querying the value of a per particle attribute requires the -attribute
          and -id or -order flags and their arguments to precede the -q flag.
    
      - particleId : id                (int)           [query,edit]
          Used in per particle attribute query and edit. Specifies the id of the particle whose attribute is being queried or
          edited. Querying the value of a per particle attribute requires the -attribute and -id or -order flags and their
          arguments to precede the -q flag.
    
      - perParticleDouble : ppd        (bool)          [query]
          Returns a list of the per-particle double attributes, excluding initial-state, cache, and information-only attributes.
    
      - perParticleVector : ppv        (bool)          [query]
          Returns a list of the per-particle vector attributes, excluding initial-state, cache, and information-only attributes.
    
      - position : p                   (float, float, float) []
          World-space position of each particle.
    
      - shapeName : sn                 (unicode)       [query,edit]
          Specify the shape name used for geometry instancing. DO not confuse this with the -n flag which names the particle
          object.
    
      - upperRight : ur                (float, float, float) [create,query]
          Upper right point of grid.
    
      - vectorValue : vv               (float, float, float) [edit]
          Used only in per particle attribute edit.  Specifies that the edit is of a vector attribute and must be followed by all
          three float values for the vector.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.particle`
    """

    pass



