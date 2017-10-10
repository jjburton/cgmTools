def nurbsUVSet(*args, **kwargs):
    """
    Allows user to toggle between implicit and explicit UVs on a NURBS object. Also provides a facility to create, delete,
    rename and set the current explicit UVSet. An implicit UVSet is non-editable. It uses the parametric make-up of the
    NURBS object to determine the location of UVs (isoparm intersections). NURBS objects also support explicit UVSets which
    are similar to the UVs of a polygonal object. UVs are created at the knots (isoparm intersections) of the object and are
    fully editable. In order to access UV editing capabilities on a NURBS object an explicit UVSet must be created and set
    as the current UVSet.
    
    Flags:
      - create : c                     (bool)          [create,query,edit]
          Creates an explicit UV set on the specified surface. If the surface already has an explicit UV set this flag will do
          nothing. Use the -ue/useExplicit flag to set/unset the explicit UV set as the current UV set.
    
      - useExplicit : ue               (bool)          [create,query,edit]
          Toggles the usage of explicit/implicit UVs. When true, explicit UVs will be used, otherwise the object will use implicit
          UVs.                              Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.nurbsUVSet`
    """

    pass


def polyPlatonicSolid(*args, **kwargs):
    """
    The polyPlatonicSolid command creates a new polygonal platonic solid.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the platonic solid. Q: When queried, this flag returns a float[3].
    
      - caching : cch                  (bool)          [query,edit]
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (int)           [create]
          This flag alows a specific UV mechanism to be selected, while creating. The valid values are 0, 1,  2 ,3 or 4. 0 implies
          that no UVs will be generated (No texture to be applied). 1 implies UVs should be created for the object as a whole
          without any normalization. The solid will be unwrapped and then the texture will be applied without any distortion. In
          the unwrapped solid, the shared edges will have shared UVs. 2 implies UVs are created separately for each of the faces
          of the solid. 3 implies the UVs should be normalized. This will normalize the U and V direction separately, thereby
          resulting in distortion of textures. 4 implies UVs are created so that the texture will not be distorted when applied.
          The texture lying outside the UV range will be truncated (since that cannot be squeezed in, without distorting the
          texture. For better understanding of these options, you may have to open the texture view windowC: Default is 4
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - radius : r                     (float)         [create,query,edit]
          This flag specifies the radius of the platonic solid. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - sideLength : l                 (float)         [create,query,edit]
          This flag specifies the side length of platonic solid. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - solidType : st                 (int)           [create]
          This flag allows a specific platonic solid to be selected for creation of mesh, The valid values are 0, 1, 2 and 3. 0
          implies dodecahedron to be created. 1 implies icosahedron to be created. 2 implies octahedron to be created. 3 implies
          tertrahedron to be created. C: Default is 0
    
      - texture : tx                   (int)           [create]
          This flag is obsolete and will be removed in the next release. The -cuv/createUVs flag should be used instead.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyPlatonicSolid`
    """

    pass


def polyCone(*args, **kwargs):
    """
    The cone command creates a new polygonal cone.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the cone. Q: When queried, this flag returns a float[3].
    
      - caching : cch                  (bool)          [query,edit]
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (int)           [create]
          This flag alows a specific UV mechanism to be selected, while creating the cone. The valid values are 0, 1,  2 or 3. 0
          implies that no UVs will be generated (No texture to be applied). 1 implies UVs should be created for the object as a
          whole without any normalization. The cone will be unwrapped and then the texture will be applied without any distortion.
          In the unwrapped cone, the shared edges will have shared UVs. 2 implies the UVs should be normalized. This will
          normalize the U and V direction separately, thereby resulting in distortion of textures. 3 implies UVs are created so
          that the texture will not be distorted when applied. The texture lying outside the UV range will be truncated (since
          that cannot be squeezed in, without distorting the texture. For better understanding of these options, you may have to
          open the texture view windowC: Default is 2
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - height : h                     (float)         [create,query,edit]
          This flag specifies the height of the cone. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - radius : r                     (float)         [create,query,edit]
          This flag specifies the radius of the cone. C: Default is 0.5. Q: When queried, this flag returns a float.
    
      - roundCap : rcp                 (bool)          [query,edit]
    
      - subdivisionsAxis : sa          (int)           [query,edit]
    
      - subdivisionsCap : sc           (int)           [query,edit]
    
      - subdivisionsHeight : sh        (int)           [query,edit]
    
      - subdivisionsX : sx             (int)           [create,query,edit]
          This specifies the number of subdivisions in the X direction for the cone. C: Default is 20. Q: When queried, this flag
          returns an int.
    
      - subdivisionsY : sy             (int)           [create,query,edit]
          This flag specifies the number of subdivisions in the Y direction for the cone. C: Default is 1. Q: When queried, this
          flag returns an int.
    
      - subdivisionsZ : sz             (int)           [create,query,edit]
          This flag specifies the number of subdivisions in the Z direction for the cone. C: Default is 0. Q: When queried, this
          flag returns an int.
    
      - texture : tx                   (bool)          [create]
          This flag is obsolete and will be removed in the next release. The -cuv/createUVs flag should be used instead.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyCone`
    """

    pass


def moveVertexAlongDirection(*args, **kwargs):
    """
    The command moves the selected vertex ( control vertex ) in the specified unit direction by the given magnitude. The
    vertex(ices) may also be moved in the direction of unit normal ( -n flag ). For NURBS surface vertices the direction of
    movement could also be either in tangent along U or tangent along V.  The flags -n, -u, -v and -d are mutually
    exclusive, ie. the selected vertices can be all moved in only -n or -u or -v or -d.
    
    Flags:
      - direction : d                  (float, float, float) [create]
          move the vertex along the direction as specified. The direction is normalized.
    
      - magnitude : m                  (float)         [create]
          move by the specified magnitude in the direction vector.
    
      - normalDirection : n            (float)         [create]
          move components in the direction of normal by the given magnitude at the respective components. The normal is
          'normalized'.
    
      - uDirection : u                 (float)         [create]
          move components in the direction of tangent along U at the respective components where appropriate. The flag is ignored
          for polygons, NURBS curves. The u direction is normalized.
    
      - uvNormalDirection : uvn        (float, float, float) [create]
          move in the triad space [u,v,n] at the respective components by the specified displacements. The flag is ignored for
          polygons, NURBS curves.
    
      - vDirection : v                 (float)         [create]
          move components in the direction of tangent along V at the respective components where appropriate. The flag is ignored
          for polygons, NURBS curves.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.moveVertexAlongDirection`
    """

    pass


def intersect(*args, **kwargs):
    """
    The intersect command creates a curve on surface where all surfaces intersect with each other. By default, the curve on
    surface is created for both surfaces. However, by using the -fs flag, only the first surface will have a curve on
    surface. Also, the intersection curve can be created as a 3D curve rather than a curve on surface.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curveOnSurface : cos           (bool)          [create]
          If possible, create 2D curve as a result.
    
      - firstSurface : fs              (bool)          [query,edit]
          Creates a curve-on-surface on the first surface only or on all surfaces (default).
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.                  Advanced flags
    
      - tolerance : tol                (float)         [create,query,edit]
          Tolerance to fit to. Default:0.01                  Common flags
    
    
    Derived from mel command `maya.cmds.intersect`
    """

    pass


def polyAutoProjection(*args, **kwargs):
    """
    Projects a map onto an object, using several orthogonal projections simultaneously.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createNewMap : cm              (bool)          [create,query]
          Create a new UV set, as opposed to editing the current one, or the one given by the -uvSetName flag.
    
      - frozen : fzn                   (bool)          []
    
      - insertBeforeDeformers : ibd    (bool)          [create]
          This flag specifies if the projection node should be inserted before or after deformer nodes already applied to the
          shape. Inserting the projection after the deformer leads to texture swimming during animation and is most often
          undesirable. C: Default is on.
    
      - layout : l                     (int)           [create,query,edit]
          What layout algorithm should be used: 0 UV pieces are set to no layout. 1 UV pieces are aligned along the U axis. 2 UV
          pieces are moved in a square shape.
    
      - layoutMethod : lm              (int)           [create,query,edit]
          Set which layout method to use: 0 Block Stacking. 1 Shape Stacking.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledGlobal Values
    
      - optimize : o                   (int)           [create,query,edit]
          Use two different flavors for the cut generation. 0 Every face is assigned to the best plane. This optimizes the map
          distortion. 1 Small UV pieces are incorporated into larger ones, when the extra distortion introduced is reasonable.
          This tends to produce fewer UV pieces.
    
      - percentageSpace : ps           (float)         [create,query,edit]
          When layout is set to square, this value is a percentage of the texture area which is added around each UV piece. It can
          be used to ensure each UV piece uses different pixels in the texture. Maximum value is 5 percent.
    
      - pivot : pvt                    (float, float, float) [create,query,edit]
          This flag specifies the pivot for scaling and rotation. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - pivotX : pvx                   (float)         [create,query,edit]
          This flag specifies the X pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotY : pvy                   (float)         [create,query,edit]
          This flag specifies the Y pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotZ : pvz                   (float)         [create,query,edit]
          This flag specifies the Z pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - planes : p                     (int)           [create,query,edit]
          Number of intermediate projections used. Valid numbers are 4, 5, 6, 8, and 12. C: Default is 6.
    
      - projectBothDirections : pb     (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: projections are mirrored on directly opposite faces. If off:
          projections are not mirrored on opposite faces. C: Default is off. Q: When queried, this flag returns an integer.
    
      - rotate : ro                    (float, float, float) [create,query,edit]
          This flag specifies the rotation angles around X, Y, Z. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - rotateX : rx                   (float)         [create,query,edit]
          This flag specifies the rotation angle around X. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateY : ry                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Y. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateZ : rz                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Z. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - scale : s                      (float, float, float) [create,query,edit]
          This flag specifies the scaling vector. C: Default is 1.0 1.0 1.0. Q: When queried, this flag returns a float[3].
    
      - scaleMode : sc                 (int)           [create,query,edit]
          How to scale the pieces, after projections: 0 No scale is applied. 1 Uniform scale to fit in unit square. 2 Non
          proportional scale to fit in unit square.
    
      - scaleX : sx                    (float)         [create,query,edit]
          This flag specifies X for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleY : sy                    (float)         [create,query,edit]
          This flag specifies Y for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleZ : sz                    (float)         [create,query,edit]
          This flag specifies Z for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - skipIntersect : si             (bool)          [create,query,edit]
          When on, self intersection of UV pieces are not tested. This makes the projection faster and produces fewer pieces, but
          may lead to overlaps in UV space.
    
      - translate : t                  (float, float, float) [create,query,edit]
          This flag specifies the translation vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - translateX : tx                (float)         [create,query,edit]
          This flag specifies the X translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateY : ty                (float)         [create,query,edit]
          This flag specifies the Y translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateZ : tz                (float)         [create,query,edit]
          This flag specifies the Z translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - uvSetName : uvs                (unicode)       [create,query]
          Specifies the name of the UV set to edit uvs on. If not specified will use the current UV set if it exists.When
          createNewMap is on, the name is used to generate a new unique UV set name.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is on. Q: When queried, this flag returns an integer.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyAutoProjection`
    """

    pass


def polyNormalizeUV(*args, **kwargs):
    """
    Normalizes the UVs of input polyFaces. The existing UVs of the faces are normalized between 0 and 1.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - centerOnTile : cot             (bool)          []
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createNewMap : cm              (bool)          [create,query]
          Create a new UV set, as opposed to editing the current one, or the one given by the uvSetName flag.
    
      - frozen : fzn                   (bool)          []
    
      - insertBeforeDeformers : ibd    (bool)          [create]
          This flag specifies if the polyNormalizeUV node should be inserted before or after deformer nodes already applied to the
          shape. Inserting the node after the deformer leads to texture swimming during animation and is most often undesirable.
          C: Default is on.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - normalizeType : nt             (int)           [create,query,edit]
          Options for normalize. 0Separate1CollectiveC:  Default is 1. Q:  When queried returns an int.
    
      - preserveAspectRatio : pa       (bool)          [create,query,edit]
          Scale uniform along u and v. C: Default is on. Q: When queried returns an int.
    
      - uvSetName : uvs                (unicode)       [create,query]
          Specifies the name of the UV set to edit uvs on. If not specified will use the current UV set if it exists. When
          createNewMap is on, the name is used to generate a new unique UV set name.                  Common flags
    
      - worldSpace : ws                (bool)          []
    
    
    Derived from mel command `maya.cmds.polyNormalizeUV`
    """

    pass


def polyCopyUV(*args, **kwargs):
    """
    Copy some UVs from a UV set into another.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createNewMap : cm              (bool)          [create,query,edit]
          This flag when set true will create a new map with a the name passed in, if the map does not already exist.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - uvSetName : uvs                (unicode)       [create,query,edit]
          Specifies name of the output uv set to modify. Default is the current UV set.
    
      - uvSetNameInput : uvi           (unicode)       [create,query,edit]
          Specifies name of the input uv set to read the UV description from. Default is the current UV set.
          Common flags
    
      - worldSpace : ws                (bool)          []
    
    
    Derived from mel command `maya.cmds.polyCopyUV`
    """

    pass


def polyConnectComponents(*args, **kwargs):
    """
    Splits polygon edges according to the selected components. The selected components are gathered into connected 'paths'
    that define continuous splits. Mixed components (vertices, edges and faces) can be used at once. The connection rules
    are: \* Edges can connect to other edges in the same face or to vertices in the same face (that are not in the edge
    itself) or to faces connected to other edges in the same face. \* Vertices can connect to edges (as above) or to
    vertices in the same face (that are not joined to the first vertex by an edge) or to faces adjacent to a face that uses
    the vertex (except those that also use the vertex). \* Faces can connect to vertices or edges (as above) or to adjacent
    faces.
    
    Flags:
      - adjustEdgeFlow : aef           (float)         []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - insertWithEdgeFlow : ief       (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyConnectComponents`
    """

    pass


def polyBevel3(*args, **kwargs):
    """
    Bevel edges.
    
    Flags:
      - angleTolerance : at            (float)         [create,query,edit]
          This flag specifies the angle beyond which additional faces may be inserted to avoid possible twisting of faces. If the
          bevel produces unwanted faces, try increasing the angle tolerance. C: Default is 5 degrees. Q: When queried, this flag
          returns a double.
    
      - autoFit : af                   (bool)          [create,query,edit]
          Computes a smooth roundness, new faces round off a smooth angle. C: Default is on. Q: When queried, this flag returns an
          int.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - chamfer : c                    (bool)          []
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - depth : d                      (float)         []
    
      - fillNgons : fn                 (bool)          []
    
      - forceParallel : fp             (bool)          []
    
      - fraction : f                   (float)         []
    
      - frozen : fzn                   (bool)          []
    
      - maya2015 : m15                 (bool)          []
    
      - maya2016SP3 : m16              (bool)          []
    
      - mergeVertexTolerance : mvt     (float)         []
    
      - mergeVertices : mv             (bool)          []
    
      - miterAlong : mia               (int)           []
    
      - mitering : m                   (int)           []
    
      - miteringAngle : ma             (float)         []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - offset : o                     (float)         [create,query,edit]
          This flag specifies the offset distance for the beveling. C: Default is 0.2. Q: When queried, this flag returns a float.
    
      - offsetAsFraction : oaf         (bool)          [create,query,edit]
          This flag specifies whether the offset is a fraction or an absolute value. If a fraction, the offset can range between 0
          and 1, where 1 is the maximum possible offset C: Default is false. Q: When queried, this flag returns an int.
    
      - roundness : r                  (float)         [create,query,edit]
          This flag specifies the roundness of bevel. A roundness of 0 means that all new faces are coplanar. This value is only
          used if the autoFit value is off. C: Default is 0.5. Q: When queried, this flag returns a float.
    
      - segments : sg                  (int)           [create,query,edit]
          This flag specifies the number of segments used for the beveling. C: Default is 1. Q: When queried, this flag returns an
          int.
    
      - smoothingAngle : sa            (float)         []
    
      - subdivideNgons : sn            (bool)          []
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flags specifies the used reference. If on : the offset flag is taken in world reference. If off : the offset flag
          is taken in object reference (the default). C: Default is off. Q: When queried, this flag returns an int. Common
          flagsCommon flags
    
    
    Derived from mel command `maya.cmds.polyBevel3`
    """

    pass


def extendCurve(*args, **kwargs):
    """
    This command extends a curve or creates a new curve as an extension
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curveOnSurface : cos           (bool)          [create]
          If possible, create 2D curve as a result.
    
      - distance : d                   (float)         [create,query,edit]
          The distance to extend Used only for extendMethod is byDistance. Default:1
    
      - extendMethod : em              (int)           [create,query,edit]
          The method with which to extend: 0 - based on distance, 2 - to a 3D point Default:0
    
      - extensionType : et             (int)           [create,query,edit]
          The type of extension: 0 - linear, 1 - circular, 2 - extrapolate Default:0
    
      - frozen : fzn                   (bool)          []
    
      - inputPoint : ip                (float, float, float) [create,query,edit]
          The point to extend to (optional)
    
      - join : jn                      (bool)          [create,query,edit]
          If true, join the extension to original curve Default:true
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - noChanges : nc                 (bool)          []
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - pointX : px                    (float)         [create,query,edit]
          X of the point to extend to Default:0
    
      - pointY : py                    (float)         [create,query,edit]
          Y of the point to extend to Default:0
    
      - pointZ : pz                    (float)         [create,query,edit]
          Z of the point to extend to Default:0
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.
    
      - removeMultipleKnots : rmk      (bool)          [create,query,edit]
          If true remove multiple knots at join Used only if join is true. Default:false
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - start : s                      (int)           [create,query,edit]
          Which end of the curve to extend. 0 - end, 1 - start, 2 - both Default:1                  Common flags
    
    
    Derived from mel command `maya.cmds.extendCurve`
    """

    pass


def polyFlipUV(*args, **kwargs):
    """
    Flip (mirror) the UVs (in texture space) of input polyFaces, about either the U or V axis..
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createNewMap : cm              (bool)          [create,query]
          Create a new UV set, as opposed to editing the current one, or the one given by the uvSetName flag.
    
      - flipType : ft                  (int)           [create,query,edit]
          Flip along U or V direction. 0Horizontal1VerticalC: Default is 0. Q: When queried returns an int.
    
      - frozen : fzn                   (bool)          []
    
      - insertBeforeDeformers : ibd    (bool)          [create]
          This flag specifies if the polyFlipUV node should be inserted before or after deformer nodes already applied to the
          shape. Inserting the node after the deformer leads to texture swimming during animation and is most often undesirable.
          C: Default is on.
    
      - local : l                      (bool)          [create,query,edit]
          Flips in the local space of the input faces. C: Default is on. Q: When queried returns an int.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - uvSetName : uvs                (unicode)       [create,query]
          Specifies the name of the UV set to edit uvs on. If not specified will use the current UV set if it exists.When
          createNewMap is on, the name is used to generate a new unique UV set name.                  Common flags
    
      - worldSpace : ws                (bool)          []
    
    
    Derived from mel command `maya.cmds.polyFlipUV`
    """

    pass


def polyUVRectangle(*args, **kwargs):
    """
    Given two vertices, does one of the following: 1) If the vertices define opposite corners of a rectangular area of
    quads, assigns a grid of UVs spanning the 0-1 area to that rectangle. 2) If the vertices define an edge in a rectangular
    and topologically cylindrical area of quads, assigns UVs spanning the 0-1 area to that cylindrical patch, using the
    defined edge as the U=0 edge.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyUVRectangle`
    """

    pass


def polyProjectCurve(*args, **kwargs):
    """
    The polyProjectCurve command creates curves by projecting a selected curve onto a selected poly mesh.  The direction of
    projection will be the current view direction unless the direction vector is specified with the -direction/-d flag.
    
    Flags:
      - addUnderTransform : aut        (bool)          []
    
      - automatic : automatic          (bool)          []
    
      - baryCoord : bc                 (float, float, float) []
    
      - baryCoord1 : bc1               (float)         []
    
      - baryCoord2 : bc2               (float)         []
    
      - baryCoord3 : bc3               (float)         []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - curveSamples : cs              (int)           []
    
      - direction : d                  (float, float, float) []
    
      - directionX : dx                (float)         []
    
      - directionY : dy                (float)         []
    
      - directionZ : dz                (float)         []
    
      - face : f                       (int)           []
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          []
    
      - pointsOnEdges : poe            (bool)          []
    
      - tolerance : tol                (float)         []
    
      - triangle : t                   (int)           []
    
    
    Derived from mel command `maya.cmds.polyProjectCurve`
    """

    pass


def extendSurface(*args, **kwargs):
    """
    This command extends a surface or creates a new surface as an extension.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - distance : d                   (float)         [create,query,edit]
          The distance to extend (for by distance only) Default:1
    
      - extendDirection : ed           (int)           [create,query,edit]
          Which parametric direction of the surface to extend ( 0 - U, 1 - V, 2 - both ) Default:0
    
      - extendMethod : em              (int)           [create,query,edit]
          The extend method (0 - distance) Default:0
    
      - extendSide : es                (int)           [create,query,edit]
          Which end of the surface to extend ( 0 - end, 1 - start, 2 - both ) Default:1
    
      - extensionType : et             (int)           [create,query,edit]
          The type of extension (0 - tangent, 2 - extrapolate) Default:0
    
      - frozen : fzn                   (bool)          []
    
      - join : jn                      (bool)          [create,query,edit]
          Join extension to original Default:true                  Common flags
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - noChanges : nc                 (bool)          []
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
    
    Derived from mel command `maya.cmds.extendSurface`
    """

    pass


def polyContourProjection(*args, **kwargs):
    """
    Performs a contour stretch UV projection onto an object.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createNewMap : cm              (bool)          [create,query,edit]
          This flag when set true will create a new map with the name passed in, if the map does not already exist.
    
      - flipRails : fr                 (bool)          [create,query,edit]
          If true, flip which curves are the rails of the birail surface.
    
      - frozen : fzn                   (bool)          []
    
      - insertBeforeDeformers : ibd    (bool)          [create]
          This flag specifies if the projection node should be inserted before or after deformer nodes already applied to the
          shape. Inserting the projection after the deformer leads to texture swimming during animation and is most often
          undesirable. C: Default is on.
    
      - method : m                     (int)           [create,query,edit]
          Sets which projection method to use. Valid values are 0: Walk Contours 1: NURBS Projection
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - offset0 : o0                   (float)         [create,query,edit]
          Sets the offset on edge 0 of the NURBS surface.
    
      - offset1 : o1                   (float)         [create,query,edit]
          Sets the offset on edge 1 of the NURBS surface.
    
      - offset2 : o2                   (float)         [create,query,edit]
          Sets the offset on edge 2 of the NURBS surface.
    
      - offset3 : o3                   (float)         [create,query,edit]
          Sets the offset on edge 3 of the NURBS surface.
    
      - reduceShear : rs               (float)         [create,query,edit]
          Sets the 'reduce shear' parameter of the projection.
    
      - smoothness0 : s0               (float)         [create,query,edit]
          Sets the smoothness of edge 0 of the NURBS surface.
    
      - smoothness1 : s1               (float)         [create,query,edit]
          Sets the smoothness of edge 1 of the NURBS surface.
    
      - smoothness2 : s2               (float)         [create,query,edit]
          Sets the smoothness of edge 2 of the NURBS surface.
    
      - smoothness3 : s3               (float)         [create,query,edit]
          Sets the smoothness of edge 3 of the NURBS surface.
    
      - userDefinedCorners : udc       (bool)          [create,query,edit]
          If true, the four vertices specified by user will be taken as corners to do the projection.
    
      - uvSetName : uvs                (unicode)       []
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on : all geometrical values are taken in world reference. If off : all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyContourProjection`
    """

    pass


def attachCurve(*args, **kwargs):
    """
    This attach command is used to attach curves. Once the curves are attached, there will be multiple knots at the joined
    point(s). These can be kept or removed if the user wishes. If there are two curves, the end of the first curve is
    attached to the start of the second curve. If there are more than two curves, closest endpoints are joined. Note: if the
    command is done with Keep Original off, the first curve is replaced by the attached curve. All other curves will remain,
    the command does not delete them.
    
    Flags:
      - blendBias : bb                 (float)         [create,query,edit]
          Skew the result toward the first or the second curve depending on the blend factory being smaller or larger than 0.5.
          Default:0.5
    
      - blendKnotInsertion : bki       (bool)          [create,query,edit]
          If set to true, insert a knot in one of the original curves (relative position given by the parameter attribute below)
          in order to produce a slightly different effect. Default:false
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - keepMultipleKnots : kmk        (bool)          [create,query,edit]
          If true, keep multiple knots at the join parameter. Otherwise remove them. Default:true
    
      - method : m                     (int)           [create,query,edit]
          Attach method (connect-0, blend-1) Default:0
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - parameter : p                  (float)         [create,query,edit]
          The parameter value for the positioning of the newly inserted knot. Default:0.1
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - reverse1 : rv1                 (bool)          [create,query,edit]
          If true, reverse the first input curve before doing attach. Otherwise, do nothing to the first input curve before
          attaching. NOTE: setting this attribute to random values will cause unpredictable results and is not supported.
          Default:false
    
      - reverse2 : rv2                 (bool)          [create,query,edit]
          If true, reverse the second input curve before doing attach. Otherwise, do nothing to the second input curve before
          attaching. NOTE: setting this attribute to random values will cause unpredictable results and is not supported.
          Default:false                  Common flags
    
    
    Derived from mel command `maya.cmds.attachCurve`
    """

    pass


def globalStitch(*args, **kwargs):
    """
    This command computes a globalStitch of NURBS surfaces. There should be at least one  NURBS surface. The NURBS
    surface(s) should be untrimmed.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          []
    
      - frozen : fzn                   (bool)          []
    
      - lockSurface : lk               (bool)          [create,query,edit]
          Keep the NURBS surface at the specified multi index unchanged by the fitting. Default:false
    
      - maxSeparation : ms             (float)         [create,query,edit]
          Maximum separation that will still be stitched. Default:0.1
    
      - modificationResistance : mr    (float)         [create,query,edit]
          Modification resistance weight for surface CVs. Default:1e-1
    
      - name : n                       (unicode)       []
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          []
    
      - replaceOriginal : rpo          (bool)          []
    
      - sampling : sam                 (int)           [create,query,edit]
          Sampling when stitching edges. Default:1
    
      - stitchCorners : sc             (int)           [create,query,edit]
          Stitch corners of surfaces. 0 - off 1 - closest point 2 - closest knot Default:1
    
      - stitchEdges : se               (int)           [create,query,edit]
          Stitch edges of surfaces. 0 - off 1 - closest point 2 - matching params Default:1
    
      - stitchPartialEdges : spe       (bool)          [create,query,edit]
          Toggle on (off) partial edge stitching. Default:false
    
      - stitchSmoothness : ss          (int)           [create,query,edit]
          Set type of smoothness of edge join. 0 - off 1 - tangent 2 - normal Default:0                  Advanced flags
    
    
    Derived from mel command `maya.cmds.globalStitch`
    """

    pass


def polyHelix(*args, **kwargs):
    """
    The polyHelix command creates a new polygonal helix.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the helix. Q: When queried, this flag returns a float[3].
    
      - caching : cch                  (bool)          [query,edit]
    
      - coils : c                      (float)         [create,query,edit]
          This flag specifies the number of coils in helix. C: Default is 1.0 Q: When queried, this flag returns a float.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (int)           [create]
          This flag alows a specific UV mechanism to be selected, while creating the helix. The valid values are 0, 1,  2 or 3. 0
          implies that no UVs will be generated (No texture to be applied). 1 implies UVs should be created for the object as a
          whole without any normalization. The helix will be unwrapped and then the texture will be applied without any
          distortion. In the unwrapped helix, the shared edges will have shared UVs. 2 implies the UVs should be normalized. This
          will normalize the U and V direction separately, thereby resulting in distortion of textures. 3 implies UVs are created
          so that the texture will not be distorted when applied. The texture lying outside the UV range will be truncated (since
          that cannot be squeezed in, without distorting the texture. For better understanding of these options, you may have to
          open the texture view windowC: Default is 2.
    
      - direction : d                  (int)           [create]
          This flag alows a direction of coil to be selected, while creating the helix. The valid values are 0 or 1. 0 implies
          clockwise direction. 1 implies counterclockwise direction. C: Default is 1
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - height : h                     (float)         [create,query,edit]
          This flag specifies the height of the helix. C: Default is 2.0. Q: When queried, this flag returns a float.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - radius : r                     (float)         [create,query,edit]
          This flag specifies the radius of helix tube. C: Default is 1.0. Q: When queried, this flag returns an float.
    
      - roundCap : rcp                 (bool)          [query,edit]
    
      - subdivisionsAxis : sa          (int)           [create,query,edit]
          This specifies the number of subdivisions around the axis of the helix. C: Default is 8. Q: When queried, this flag
          returns an int.
    
      - subdivisionsCaps : sc          (int)           [create,query,edit]
          This flag specifies the number of subdivisions along the thickness of the coil. C: Default is 0. Q: When queried, this
          flag returns an int.
    
      - subdivisionsCoil : sco         (int)           [create,query,edit]
          This flag specifies the number of subdivisions along the coil of the helix. C: Default is 50. Q: When queried, this flag
          returns an int.
    
      - texture : tx                   (int)           [create]
          This flag is obsolete and will be removed in the next release. The -cuv/createUVs flag should be used instead.
    
      - useOldInitBehaviour : oib      (bool)          [query,edit]
    
      - width : w                      (float)         [create,query,edit]
          This specifies the width of the helix. C: Default is 1.0. Q: When queried, this flag returns an float.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyHelix`
    """

    pass


def polyUnite(*args, **kwargs):
    """
    This command creates a new poly as an union of a list of polys If no objects are specified in the command line, then the
    objects from the active list are used.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - centerPivot : cp               (bool)          []
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - mergeUVSets : muv              (int)           [create]
          Specify how UV sets will be merged on the output mesh. The choices are 0 | 1 | 2. 0 = Do not merge. Each UV set on each
          mesh will become a new UV set in the output. 1 = Merge by name. UV sets with the same name will be merged. 2 = Merge by
          UV links. UV sets will be merged so that UV linking on the input meshes continues to work. The default is 1 (merge by
          name).                  Common flags
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          []
    
      - objectPivot : op               (bool)          []
    
    
    Derived from mel command `maya.cmds.polyUnite`
    """

    pass


def polyDelVertex(*args, **kwargs):
    """
    Deletes vertices. Joins two edges which have a common vertex. The vertices must be connected to exactly two edges (so-
    called winged).
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyDelVertex`
    """

    pass


def querySubdiv(*args, **kwargs):
    """
    Queries a subdivision surface based on a set of query parameters and updates the selection list with the results.
    
    Flags:
      - action : a                     (int)           [create]
          Specifies the query parameter:         1 = find all tweaked verticies at level         2 = find all sharpened vertices
          at level         3 = find all sharpened edges at level         4 = find all faces at level If the attribute levelis not
          specified then the query is applied to the current component display level. If the attribute level is specified then the
          query is applied to that level, either absolute or relative to the current level based on the relativeflag state.
    
      - level : l                      (int)           [create]
          Specify the level of the subdivision surface on which to perform the operation.
    
      - relative : r                   (bool)          [create]
          If set, level flag refers to the level relative to the current component display level.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.querySubdiv`
    """

    pass


def polyMapSew(*args, **kwargs):
    """
    Sew border edges in texture space. Selected edges must be map borders.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyMapSew`
    """

    pass


def polyMirrorFace(*args, **kwargs):
    """
    Mirror all the faces of the selected object.
    
    Flags:
      - axis : a                       (int)           []
    
      - axisDirection : ad             (int)           []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - cutMesh : cm                   (bool)          []
    
      - direction : d                  (int)           [create]
          This flag specifies the mirror direction. C: Default is 0
    
      - firstNewFace : fnf             (int)           []
    
      - flipUVs : fuv                  (int)           []
    
      - frozen : fzn                   (bool)          []
    
      - lastNewFace : lnf              (int)           []
    
      - mergeMode : mm                 (int)           [create]
          This flag specifies the behaviour of the mirror with respect to the border edges. Valid values are 0-5, corresponding to
          +X, -X, +Y, -Y, +Z, -Z direction respectively. If the mode is 0, the border edges will not be merged (co-incident
          vertices will be present). If the mode is 1, the border vertices/edges will be merged If the mode is 2, the border edges
          will be extruded and connected. C: Default is 0
    
      - mergeThreshold : mt            (float)         [create]
          This flag specifies the tolerance value for merging borders. C: Default is 0.1
    
      - mergeThresholdType : mtt       (int)           [create]
          This flag specifies if the merge threshold is calculated automatically based on the average length of the border edges.
    
      - mirrorAxis : ma                (int)           [create]
          This flag specifies what method to use to define the mirror axis
    
      - mirrorPlaneCenter : pc         (float, float, float) []
    
      - mirrorPlaneCenterX : pcx       (float)         []
    
      - mirrorPlaneCenterY : pcy       (float)         []
    
      - mirrorPlaneCenterZ : pcz       (float)         []
    
      - mirrorPlaneRotate : ro         (float, float, float) []
    
      - mirrorPlaneRotateX : rx        (float)         []
    
      - mirrorPlaneRotateY : ry        (float)         []
    
      - mirrorPlaneRotateZ : rz        (float)         []
    
      - mirrorPosition : mps           (float)         [create]
          This flag specifies the position of the custom mirror axis plane
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - pivot : p                      (float, float, float) [create]
          This flag specifies the pivot for the mirror. C: Default is computed using the bounding box of the object
    
      - pivotX : px                    (float)         [create]
          This flag specifies the X pivot for the mirror. C: Default is computed using the bounding box of the object
    
      - pivotY : py                    (float)         [create]
          This flag specifies the Y pivot for the mirror. C: Default is computed using the bounding box of the object
    
      - pivotZ : pz                    (float)         [create]
          This flag specifies the Z pivot for the mirror. C: Default is computed using the bounding box of the object
    
      - scalePivotX : spx              (float)         []
    
      - scalePivotY : spy              (float)         []
    
      - scalePivotZ : spz              (float)         []
    
      - smoothingAngle : sa            (float)         []
    
      - userSpecifiedPivot : pu        (bool)          []
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyMirrorFace`
    """

    pass


def bezierInfo(*args, **kwargs):
    """
    This command provides a queryable interface for Bezier curve shapes.
    
    Flags:
      - anchorFromCV : afc             (int)           [create]
          Returns the Bezier anchor index from a given CV index
    
      - cvFromAnchor : cfa             (int)           [create]
          Returns the CV index for a given Bezier anchor index
    
      - isAnchorSelected : ias         (bool)          [create]
          Returns 1 if an anchor CV is currently selected. 0, otherwise.
    
      - isTangentSelected : its        (bool)          [create]
          Returns 1 if a tangent CV is currently selected. 0, otherwise.
    
      - onlyAnchorsSelected : oas      (bool)          [create]
          Returns 1 if the only CV components selected are anchor CVs. 0, otherwise.
    
      - onlyTangentsSelected : ots     (bool)          [create]
          Returns 1 if the only CV components selected are tangent CVs. 0, otherwise.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.bezierInfo`
    """

    pass


def freeFormFillet(*args, **kwargs):
    """
    This command creates a free form surface fillet across two surface trim edges or isoparms or curve on surface. The
    fillet surface creation has blend controls in the form of bias and depth. The bias value scales the tangents at the two
    ends across the two selected curves. The depth values controls the curvature of the fillet across the two selected
    curves. The default values of depth, bias are 0.5 and 0.5 respectively.
    
    Flags:
      - bias : b                       (float)         [create,query,edit]
          Bias value for fillet Default:0.5
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - depth : d                      (float)         [create,query,edit]
          Depth value for fillet Default:0.5
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)
    
      - positionTolerance : pt         (float)         [create,query,edit]
          C(0) Tolerance For Filleted Surface creation Default:0.1
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.                  Advanced flags
    
      - tangentTolerance : tt          (float)         [create,query,edit]
          G(1) continuity Tolerance For Filleted Surface creation Default:0.1                  Common flags
    
    
    Derived from mel command `maya.cmds.freeFormFillet`
    """

    pass


def subdMapSewMove(*args, **kwargs):
    """
    This command can be used to Move and Sew together separate UV pieces along geometric edges. UV pieces that correspond to
    the same geometric edge, are merged together by moving the smaller piece to the larger one. The argument is a UV
    selection list.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - limitPieceSize : lps           (bool)          [create,query,edit]
          When on, this flag specifies that the face number limit described above should be used.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - numberFaces : nf               (int)           [create,query,edit]
          Maximum number of faces in a UV piece. When trying to combine two UV pieces into a single one, the merge operation is
          rejected if the smaller piece has more faces than the number specified by this flag.This flag is only used when
          limitPieceSizeis set to on.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          If true, performs the operation in world space coordinates as opposed to local space.                  Advanced flags
    
    
    Derived from mel command `maya.cmds.subdMapSewMove`
    """

    pass


def polyQuad(*args, **kwargs):
    """
    Merges selected triangles of a polygonal object into four-sided faces.
    
    Flags:
      - angle : a                      (float)         [create,query,edit]
          Angle threshold above which two triangles are not merged. C: Default is 30 degrees. The range is [0.0, 180.0]. Q: When
          queried, this flag returns a float.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - keepGroupBorder : kgb          (bool)          [create,query,edit]
          Keep facet group border : If on, the borders of selected faces are maintained, otherwise the borders of selected facets
          may be modified. C: Default is on. Q: When queried, this flag returns an int.
    
      - keepHardEdges : khe            (bool)          [create,query,edit]
          Keep hard edges : If on, the hard edges of selected faces are maintained, otherwise they may be deleted between two
          triangles. C: Default is on. Q: When queried, this flag returns an int.
    
      - keepTextureBorders : ktb       (bool)          [create,query,edit]
          Keep texture border : If on, the borders of texture maps are maintained, otherwise the boreders of texture maps may be
          modified. C: Default is on. Q: When queried, this flag returns an int.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyQuad`
    """

    pass


def applyMetadata(*args, **kwargs):
    """
    Define the values of a particular set of metadata on selected objects. This command is used in preservation of metadata
    through Maya file formats (.ma/.mb). If any metadata already exists it will be kept and merged with the new metadata,
    overwriting duplicate entries. (i.e. if this command specifies data at index N and you already have a value at index N
    then the one this command specifies will be the new value and the old one will cease to exist.)  Unlike the
    editMetadatacommand it is not necessary to first use the addMetadatacommand or API equivalent to attach a metadata
    stream to the object, this command will do both assignment of structure and of metadata values. You do have to use the
    dataStructurecommand or API equivalent to create the structure being assigned first though.  The formatted input will be
    in a form expected by the data associations serializer (see adsk::Data::AssociationsSerializer for more information).
    The specific serialization type will be the default 'raw' if the formatflag is not used.  For example the rawformat
    input string channel face\n[STREAMDATA]\nendChannels\nendAssociationswith no flags is equivalent to the input
    [STREAMDATA]\nendChannelswith the channelflag set to 'face'
    
    Flags:
      - format : fmt                   (unicode)       [create]
          Name of the data association format type to use in the value flag parsing. Default value is raw.
    
      - scene : scn                    (bool)          [create]
          Use this flag when you want to apply metadata to the scene as a whole rather than to any individual nodes. If you use
          this flag and have nodes selected the nodes will be ignored and a warning will be displayed.
    
      - value : v                      (unicode)       [create]
          String containing all of the metadata to be assigned to the selected object.                               Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.applyMetadata`
    """

    pass


def offsetSurface(*args, **kwargs):
    """
    The offset command creates new offset surfaces from the selected surfaces. The default method is a surface offset, which
    offsets relative to the surface itself. The CV offset method offsets the CVs directly rather than the surface, so is
    usually slightly less accurate but is faster. The offset surface will always have the same degree, number of CVs and
    knot spacing as the original surface.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - distance : d                   (float)         [create,query,edit]
          Offset distance Default:1.0
    
      - frozen : fzn                   (bool)          []
    
      - method : m                     (int)           [create,query,edit]
          Offset method 0 - Surface Fit 1 - CV Fit Default:0                  Common flags
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.                  Advanced flags
    
    
    Derived from mel command `maya.cmds.offsetSurface`
    """

    pass


def polySlideEdge(*args, **kwargs):
    """
    Moves an edge loop selection along the edges connected to the sides of its vertices.
    
    Flags:
      - absolute : a                   (bool)          [create]
          This flag specifies whether or not the command uses absolute mode If in absolute then all vertices will move the same
          distance (the specified percentage of the smallest edge) C: Default is off
    
      - direction : d                  (int)           [create]
          This flag specifies the direction of the slide edge movement 0: is left direction (relative) 1: is right direction
          (relative) 2: is normal direction (relative) C: Default is 0
    
      - edgeDirection : ed             (float)         [create]
          This flag specifies the relative percentage to move along the edges on either side of the vertices along the edge loop
          C: Default is 0.0
    
      - symmetry : sym                 (bool)          [create]
          This flag specifies whether or not the command will do a symmetrical slide. Only takes effect when symmetry is enabled.
          C: Default is off                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polySlideEdge`
    """

    pass


def polyCube(*args, **kwargs):
    """
    The cube command creates a new polygonal cube.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the cube. Q: When queried, this flag returns a float[3].
    
      - caching : cch                  (bool)          [query,edit]
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (int)           [create]
          This flag alows a specific UV mechanism to be selected, while creating the cube. The valid values are 0, 1,  2 ,3 or 4.
          0 implies that no UVs will be generated (No texture to be applied). 1 implies UVs should be created for the object as a
          whole without any normalization. The cube will be unwrapped and then the texture will be applied without any distortion.
          In the unwrapped cube, the shared edges will have shared UVs. 2 implies UVs are created separately for each of the faces
          of the cube. 3 implies the UVs should be normalized. This will normalize the U and V direction separately, thereby
          resulting in distortion of textures. 4 implies UVs are created so that the texture will not be distorted when applied.
          The texture lying outside the UV range will be truncated (since that cannot be squeezed in, without distorting the
          texture. For better understanding of these options, you may have to open the texture view windowC: Default is 4
    
      - depth : d                      (float)         [create,query,edit]
          This flag specifies the depth of the cube. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - height : h                     (float)         [create,query,edit]
          This flag specifies the height of the cube. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - subdivisionsDepth : sd         (int)           [query,edit]
    
      - subdivisionsHeight : sh        (int)           [query,edit]
    
      - subdivisionsWidth : sw         (int)           [query,edit]
    
      - subdivisionsX : sx             (int)           [create,query,edit]
          This specifies the number of subdivisions in the X direction for the cube. C: Default is 1. Q: When queried, this flag
          returns an int.
    
      - subdivisionsY : sy             (int)           [create,query,edit]
          This flag specifies the number of subdivisions in the Y direction for the cube. C: Default is 1. Q: When queried, this
          flag returns an int.
    
      - subdivisionsZ : sz             (int)           [create,query,edit]
          This flag specifies the number of subdivisions in the Z direction for the cube. C: Default is 1. Q: When queried, this
          flag returns an int.
    
      - texture : tx                   (int)           [create]
          This flag is obsolete and will be removed in the next release. The -cuv/createUVs flag should be used instead.
    
      - width : w                      (float)         [create,query,edit]
          This flag specifies the width of the cube. C: Default is 1.0. Q: When queried, this flag returns a float.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyCube`
    """

    pass


def polyPlanarProjection(*args, **kwargs):
    """
    Projects a map onto an object, using an orthogonal projection. The piece of the map defined from isu, isv, icx, icy
    area, is placed at pcx, pcy, pcz location.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createNewMap : cm              (bool)          [create,query,edit]
          This flag when set true will create a new map with a the name passed in, if the map does not already exist.
    
      - frozen : fzn                   (bool)          []
    
      - imageCenter : ic               (float, float)  [create,query,edit]
          This flag specifies the center point of the 2D model layout. C: Default is 0.5 0.5. Q: When queried, this flag returns a
          float[2].
    
      - imageCenterX : icx             (float)         [create,query,edit]
          This flag specifies X for the center point of the 2D model layout. C: Default is 0.5. Q: When queried, this flag returns
          a float.
    
      - imageCenterY : icy             (float)         [create,query,edit]
          This flag specifies Y for the center point of the 2D model layout. C: Default is 0.5. Q: When queried, this flag returns
          a float.
    
      - imageScale : imageScale        (float, float)  [create,query,edit]
          This flag specifies the UV scale : Enlarges or reduces the 2D version of the model in U or V space relative to the 2D
          centerpoint. C: Default is 1.0 1.0. Q: When queried, this flag returns a float[2].
    
      - imageScaleU : isu              (float)         [create,query,edit]
          This flag specifies the U scale : Enlarges or reduces the 2D version of the model in U space relative to the 2D
          centerpoint. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - imageScaleV : isv              (float)         [create,query,edit]
          This flag specifies the V scale : Enlarges or reduces the 2D version of the model in V space relative to the 2D
          centerpoint. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - insertBeforeDeformers : ibd    (bool)          [create]
          This flag specifies if the projection node should be inserted before or after deformer nodes already applied to the
          shape. Inserting the projection after the deformer leads to texture swimming during animation and is most often
          undesirable. C: Default is on.
    
      - keepImageRatio : kir           (bool)          []
    
      - mapDirection : md              (unicode)       [create]
          This flag specifies the mapping direction. 'x', 'y' and 'z' projects the map along the corresponding axis. 'c' projects
          along the current camera viewing direction. 'p' does perspective projection if current camera is perspective. 'b'
          projects along the best plane fitting the objects selected.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - perInstance : pi               (bool)          []
    
      - projectionCenter : pc          (float, float, float) [create,query,edit]
          This flag specifies the origin point from which the map is projected. C: Default is 0.0 0.0 0.0. Q: When queried, this
          flag returns a float[3].
    
      - projectionCenterX : pcx        (float)         [create,query,edit]
          This flag specifies X for the origin point from which the map is projected. C: Default is 0.0. Q: When queried, this
          flag returns a float.
    
      - projectionCenterY : pcy        (float)         [create,query,edit]
          This flag specifies Y for the origin point from which the map is projected. C: Default is 0.0. Q: When queried, this
          flag returns a float.
    
      - projectionCenterZ : pcz        (float)         [create,query,edit]
          This flag specifies Z for the origin point from which the map is projected. C: Default is 0.0. Q: When queried, this
          flag returns a float.
    
      - projectionHeight : ph          (float)         []
    
      - projectionHorizontalSweep : phs (float)         []
    
      - projectionScale : ps           (float, float)  [create,query,edit]
          This flag specifies the width and the height of the map relative to the 3D projection axis. C: Default is 1.0 1.0. Q:
          When queried, this flag returns a float[2].
    
      - projectionScaleU : psu         (float)         [create,query,edit]
          This flag specifies the width of the map relative to the 3D projection axis. C: Default is 1.0. Q: When queried, this
          flag returns a float.
    
      - projectionScaleV : psv         (float)         [create,query,edit]
          This flag specifies the height of the map relative to the 3D projection axis. C: Default is 1.0. Q: When queried, this
          flag returns a float.
    
      - radius : r                     (float)         []
    
      - rotate : ro                    (float, float, float) [create,query,edit]
          This flag specifies the mapping rotate angles. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - rotateX : rx                   (float)         [create,query,edit]
          This flag specifies X mapping rotate angle. C: Default is 0.0. Q: When queried, this flag returns a float[3].
    
      - rotateY : ry                   (float)         [create,query,edit]
          This flag specifies Y mapping rotate angle. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateZ : rz                   (float)         [create,query,edit]
          This flag specifies Z mapping rotate angle. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotationAngle : ra             (float)         [create,query,edit]
          This flag specifies the rotation angle in the mapping space. When the angle is positive, then the map rotates
          counterclockwise on the mapped model, whereas when it is negative then the map rotates clockwise on the mapped model. C:
          Default is 10.0. Q: When queried, this flag returns a float.
    
      - seamCorrect : sc               (bool)          []
    
      - smartFit : sf                  (bool)          []
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyPlanarProjection`
    """

    pass


def polyExtrudeEdge(*args, **kwargs):
    """
    Extrude edges separately or together.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createCurve : cc               (bool)          []
    
      - divisions : d                  (int)           [create,query,edit]
          This flag specifies the number of subdivisions. C: Default is 1 Q: When queried, this flag returns an int.
    
      - frozen : fzn                   (bool)          []
    
      - gain : ga                      (float)         []
    
      - inputCurve : inc               (PyNode)        [create]
          This flag specifies the name of the curve to be used as input for extrusion C: The selected edges will be extruded along
          the curve. It will be useful to set a higher value (greater than 4) for the '-d/-divisions' flag, to get good results.
          The normal of the surface has to be aligned with the direction of the curve.  The extrusion is evenly distributed in the
          curve's parameter space, and not on the curve's geometry space
    
      - keepFacesTogether : kft        (bool)          [create,query,edit]
          This flag specifies how to extrude edgess. If on, edges are pulled together (connected ones stay connected), otherwise
          they are pulled independentely. C: Default is on. Q: When queried, this flag returns an int.
    
      - localCenter : lc               (int)           []
    
      - localDirection : ld            (float, float, float) [create,query,edit]
          This flag specifies the local slant axis (see local rotation). C: Default is 0.0 0.0 1.0. Q: When queried, this flag
          returns a float[3].
    
      - localDirectionX : ldx          (float)         [create,query,edit]
          This flag specifies X for the local slant axis. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localDirectionY : ldy          (float)         [create,query,edit]
          This flag specifies Y for the local slant axis. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localDirectionZ : ldz          (float)         [create,query,edit]
          This flag specifies Z for the local slant axis. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localRotate : lr               (float, float, float) [create,query,edit]
          This flag specifies the local rotations : (slantRot, slantRoll, twistRot). C: Default is 0.0 0.0 0.0. Q: When queried,
          this flag returns a float[3]. Local rotation (slantRot, slantRoll, twistRot).
    
      - localRotateX : lrx             (float)         [create,query,edit]
          This flag specifies local rotation X angle (Slant Rot around slantAxis). C: Default is 0.0. The range is [0, 360]. Q:
          When queried, this flag returns a float.
    
      - localRotateY : lry             (float)         [create,query,edit]
          This flag specifies local rotation Y angle (Slant Roll of slantAxis). C: Default is 0.0. The range is [0, 180]. Q: When
          queried, this flag returns a float.
    
      - localRotateZ : lrz             (float)         [create,query,edit]
          This flag specifies local rotation Z angle (Twist around normal). C: Default is 0.0. The range is [0, 360]. Q: When
          queried, this flag returns a float.
    
      - localScale : ls                (float, float, float) [create,query,edit]
          This flag specifies the local scaling vector. C: Default is 1.0 1.0 1.0. Q: When queried, this flag returns a float[3].
    
      - localScaleX : lsx              (float)         [create,query,edit]
          This flag specifies X for local scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localScaleY : lsy              (float)         [create,query,edit]
          This flag specifies Y for local scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localScaleZ : lsz              (float)         [create,query,edit]
          This flag specifies Z for local scaling vector : Flattening. C: Default is 1.0. The range is [0.0, 1.0]. Q: When
          queried, this flag returns a float.
    
      - localTranslate : lt            (float, float, float) [create,query,edit]
          This flag specifies the local translation vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - localTranslateX : ltx          (float)         [create,query,edit]
          This flag specifies the X local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localTranslateY : lty          (float)         [create,query,edit]
          This flag specifies the Y local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localTranslateZ : ltz          (float)         [create,query,edit]
          This flag specifies the Z local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - offset : off                   (float)         []
    
      - pivot : pvt                    (float, float, float) [create,query,edit]
          This flag specifies the pivot for scaling and rotation. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - pivotX : pvx                   (float)         [create,query,edit]
          This flag specifies the X pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotY : pvy                   (float)         [create,query,edit]
          This flag specifies the Y pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotZ : pvz                   (float)         [create,query,edit]
          This flag specifies the Z pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
          Local Values
    
      - random : ran                   (float)         [create,query,edit]
          This flag specifies the random value for all parameters. C: Default is 0.0. The range is [-10.0, 10.0]. Q: When queried,
          this flag returns a float.
    
      - rotate : ro                    (float, float, float) [create,query,edit]
          This flag specifies the rotation angles around X, Y, Z. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - rotateX : rx                   (float)         [create,query,edit]
          This flag specifies the rotation angle around X. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateY : ry                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Y. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateZ : rz                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Z. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - scale : s                      (float, float, float) [create,query,edit]
          This flag specifies the scaling vector. C: Default is 1.0 1.0 1.0. Q: When queried, this flag returns a float[3].
    
      - scaleX : sx                    (float)         [create,query,edit]
          This flag specifies X for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleY : sy                    (float)         [create,query,edit]
          This flag specifies Y for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleZ : sz                    (float)         [create,query,edit]
          This flag specifies Z for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - smoothingAngle : sma           (float)         [create,query,edit]
          This flag specifies smoothingAngle threshold used to determine whether newly created edges are hard or soft. C: Default
          is 30.0. The range is [0, 180]. Q: When queried, this flag returns a float. Global Values
    
      - taper : tp                     (float)         []
    
      - taperCurve_FloatValue : cfv    (float)         []
    
      - taperCurve_Interp : ci         (int)           []
    
      - taperCurve_Position : cp       (float)         []
    
      - thickness : tk                 (float)         []
    
      - translate : t                  (float, float, float) [create,query,edit]
          This flag specifies the translation vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - translateX : tx                (float)         [create,query,edit]
          This flag specifies the X translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateY : ty                (float)         [create,query,edit]
          This flag specifies the Y translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateZ : tz                (float)         [create,query,edit]
          This flag specifies the Z translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - twist : twt                    (float)         []
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyExtrudeEdge`
    """

    pass


def polyInstallAction(*args, **kwargs):
    """
    Installs/uninstalls several things to help the user to perform the specified action : PickmaskInternal selection
    constraintsDisplay attributes
    
    Flags:
      - commandName : cn               (bool)          [query]
          return as a string the name of the command previously installed
    
      - convertSelection : cs          (bool)          [create]
          convert all polys selected in object mode into their full matching component selection. For example : if a polyMesh is
          selected, polyInstallAction -cs polyCloseBorderwill select all border edges.
    
      - installConstraint : ic         (bool)          [create,query]
          C: install selection pickmask and internal constraints for actionnameQ: returns 1 if any internal constraint is set for
          current action
    
      - installDisplay : id            (bool)          [create,query]
          C: install display attributes for actionnameQ: returns 1 if any display is set for current action
    
      - keepInstances : ki             (bool)          [create]
          Convert components for all selected instances rather than only the first selected instance.
    
      - uninstallConstraint : uc       (bool)          [create]
          uninstall internal constraints previously installed
    
      - uninstallDisplay : ud          (bool)          [create]
          uninstall display attributes previously installed                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyInstallAction`
    """

    pass


def nurbsBoolean(*args, **kwargs):
    """
    This command performs a boolean operation.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - nsrfsInFirstShell : nsf        (int)           [create]
          The number of selection items comprising the first shell.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - operation : op                 (int)           [create,query,edit]
          Type of Boolean operation. Default:0
    
      - smartConnection : sc           (bool)          [create]
          Look for any of the selection items having a boolean operation as history. Default is true.                  Advanced
          flags
    
      - tolerance : tlb                (float)         [create,query,edit]
          fitting tolerance. Default:0.01                  Common flags
    
    
    Derived from mel command `maya.cmds.nurbsBoolean`
    """

    pass


def bezierCurveToNurbs(*args, **kwargs):
    """
    The bezierCurveToNurbs command attempts to convert an existing NURBS curve to a Bezier curve.
    
    
    Derived from mel command `maya.cmds.bezierCurveToNurbs`
    """

    pass


def sphere(*args, **kwargs):
    """
    The sphere command creates a new sphere. The number of spans in the in each direction of the sphere is determined by the
    useTolerance attribute. If -ut is true then the -tolerance attribute will be used. If -ut is false then the -sections
    attribute will be used.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          The primitive's axis
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting surface: 1 - linear, 3 - cubic Default:3
    
      - endSweep : esw                 (float)         [create,query,edit]
          The angle at which to end the surface of revolution. Default is 2Pi radians, or 360 degrees. Default:6.2831853
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - heightRatio : hr               (float)         [create,query,edit]
          Ratio of heightto widthDefault:2.0
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - pivot : p                      (float, float, float) [create,query,edit]
          The primitive's pivot point
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)Advanced flags
    
      - radius : r                     (float)         [create,query,edit]
          The radius of the object Default:1.0
    
      - sections : s                   (int)           [create,query,edit]
          The number of sections determines the resolution of the surface in the sweep direction. Used only if useTolerance is
          false. Default:8
    
      - spans : nsp                    (int)           [create,query,edit]
          The number of spans determines the resolution of the surface in the opposite direction. Default:1
    
      - startSweep : ssw               (float)         [create,query,edit]
          The angle at which to start the surface of revolution Default:0
    
      - tolerance : tol                (float)         [create,query,edit]
          The tolerance with which to build the surface. Used only if useTolerance is true Default:0.01
    
      - useTolerance : ut              (bool)          [create,query,edit]
          Use the specified tolerance to determine resolution. Otherwise number of sections will be used. Default:false
          Common flags
    
    
    Derived from mel command `maya.cmds.sphere`
    """

    pass


def angleBetween(*args, **kwargs):
    """
    Returns the axis and angle required to rotate one vector onto another. If the construction history (ch) flag is ON, then
    the name of the new dependency node is returned.
    
    Flags:
      - caching : cch                  (bool)          []
    
      - constructionHistory : ch       (bool)          [create]
          Turn construction history on or off.  If true, a dependency node will be created and its name is returned. Default:false
    
      - euler : er                     (bool)          [create]
          return the rotation as 3 Euler angles instead of axis + angle
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       []
    
      - nodeState : nds                (int)           []
    
      - vector1 : v1                   (float, float, float) [create]
          vector to compute the rotation from
    
      - vector1X : v1x                 (float)         []
    
      - vector1Y : v1y                 (float)         []
    
      - vector1Z : v1z                 (float)         []
    
      - vector2 : v2                   (float, float, float) [create]
          vector to compute the rotation to                  Flag can have multiple arguments, passed either as a tuple or a list.
    
      - vector2X : v2x                 (float)         []
    
      - vector2Y : v2y                 (float)         []
    
      - vector2Z : v2z                 (float)         []
    
    
    Derived from mel command `maya.cmds.angleBetween`
    """

    pass


def canCreateManip(*args, **kwargs):
    """
    This command returns true if there can be a manipulator made for the specified selection, false otherwise.
    
    
    Derived from mel command `maya.cmds.canCreateManip`
    """

    pass


def polyClean(*args, **kwargs):
    """
    polyClean will attempt to remove components that are invalid in the description of a poly mesh.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - cleanEdges : ce                (bool)          [create,query,edit]
          If true, the operation will look for and delete edges that are not associated with any face in the mesh.
    
      - cleanPartialUVMapping : cpm    (bool)          [create,query,edit]
          If true, the operation will look for any faces on the mesh that do not have complete UV mapping.  Maya requires that all
          vertices that make up a mesh face have valid UV data associated with them, or that none of the vertices withing the face
          have associated UVs.
    
      - cleanVertices : cv             (bool)          [create,query,edit]
          If true, the operation will look for and delete vertices that are not associated with any face in the mesh.
          Common flags
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyClean`
    """

    pass


def pointPosition(*args, **kwargs):
    """
    This command returns the world or local space position for any type of point object. Valid selection items are: - curve
    and surface CVs - poly vertices - lattice points - particles - curve and surface edit points - curve and surface
    parameter points - poly uvs - rotate/scale/joint pivots - selection handles - locators, param locators and arc length
    locators It works on the selected object or you can specify the object in the command. By default, if no flag is
    specified then the world position is returned.
    
    Flags:
      - local : l                      (bool)          [create]
          Return the point in local space coordinates.
    
      - world : w                      (bool)          [create]
          Return the point in world space coordinates.                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.pointPosition`
    """

    pass


def cone(*args, **kwargs):
    """
    The cone command creates a new cone and/or a dependency node that creates one, and returns their names.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          The primitive's axis
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting surface: 1 - linear, 3 - cubic Default:3
    
      - endSweep : esw                 (float)         [create,query,edit]
          The angle at which to end the surface of revolution. Default is 2Pi radians, or 360 degrees. Default:6.2831853
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - heightRatio : hr               (float)         [create,query,edit]
          Ratio of heightto widthDefault:2.0
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - pivot : p                      (float, float, float) [create,query,edit]
          The primitive's pivot point
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)Advanced flags
    
      - radius : r                     (float)         [create,query,edit]
          The radius of the object Default:1.0
    
      - sections : s                   (int)           [create,query,edit]
          The number of sections determines the resolution of the surface in the sweep direction. Used only if useTolerance is
          false. Default:8
    
      - spans : nsp                    (int)           [create,query,edit]
          The number of spans determines the resolution of the surface in the opposite direction. Default:1
    
      - startSweep : ssw               (float)         [create,query,edit]
          The angle at which to start the surface of revolution Default:0
    
      - tolerance : tol                (float)         [create,query,edit]
          The tolerance with which to build the surface. Used only if useTolerance is true Default:0.01
    
      - useOldInitBehaviour : oib      (bool)          [create,query,edit]
          Create the cone with base on the origin as in Maya V8.0 and below Otherwise create cone centred at origin Default:false
    
      - useTolerance : ut              (bool)          [create,query,edit]
          Use the specified tolerance to determine resolution. Otherwise number of sections will be used. Default:false
          Common flags
    
    
    Derived from mel command `maya.cmds.cone`
    """

    pass


def pointOnCurve(*args, **kwargs):
    """
    This command returns information for a point on a NURBS curve. If no flag is specified, it assumes p/position by
    default.
    
    Flags:
      - caching : cch                  (bool)          []
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.                  Flag can have multiple arguments, passed either as a tuple or
          a list.
    
      - curvatureCenter : cc           (bool)          [create]
          Returns the (x,y,z) center of curvature of the specified point on the curve
    
      - curvatureRadius : cr           (bool)          [create]
          Returns the radius of curvature of the specified point on the curve
    
      - frozen : fzn                   (bool)          []
    
      - nodeState : nds                (int)           []
    
      - normal : no                    (bool)          [create]
          Returns the (x,y,z) normal of the specified point on the curve
    
      - normalizedNormal : nn          (bool)          [create]
          Returns the (x,y,z) normalized normal of the specified point on the curve
    
      - normalizedTangent : nt         (bool)          [create]
          Returns the (x,y,z) normalized tangent of the specified point on the curve
    
      - parameter : pr                 (float)         [query,edit]
          The parameter value on curve Default:0.0
    
      - position : p                   (bool)          [create]
          Returns the (x,y,z) position of the specified point on the curve
    
      - tangent : t                    (bool)          [create]
          Returns the (x,y,z) tangent of the specified point on the curve
    
      - turnOnPercentage : top         (bool)          [query,edit]
          Whether the parameter is normalized (0,1) or not Default:false                  Common flags
    
    
    Derived from mel command `maya.cmds.pointOnCurve`
    """

    pass


def polyUVSet(*args, **kwargs):
    """
    Command to do the following to uv sets:         - delete an existing uv set.         - rename an existing uv set.     -
    create a new empty uv set.     - copy the values from one uv set to a another       pre-existing uv set.         - set
    the current uv set to a pre-existing uv set.     - modify sharing between instances of per-instance uv sets         -
    query the current uv set.         - set the current uv set to the last uv set added to an object.     - query the names
    of all uv sets.
    
    Flags:
      - allUVSets : auv                (bool)          [query,edit]
          This flag when used in in a query will return a list of all of the uv set names
    
      - allUVSetsIndices : uvn         (bool)          [query,edit]
          This flag when queried will return a list of the logical plug indices of all the uv sets in the sparse uv set array.
    
      - allUVSetsWithCount : awc       (bool)          [query,edit]
          This flag when used in a query will return a list of all of the uv set family names, with a count appended to the
          perInstance sets indicating the number of instances in the uv set shared by the specified or selected shape.
    
      - copy : cp                      (bool)          [create,query,edit]
          This flag when used will result in the copying of the uv set corresponding to name specified with the uvSet flag to the
          uvset corresponding to the name specified with the newUVSet flag
    
      - create : cr                    (bool)          [create,query,edit]
          This flag when used will result in the creation of an empty uv set corresponding to the name specified with the uvSet
          flag. If a uvSet with that name already exists, then no new uv set will be created.
    
      - currentLastUVSet : luv         (bool)          [create,query,edit]
          This flag when used will set the current uv set that the object needs to work on, to be the last uv set added to the
          object. If no uv set exists for the object, then no uv set name will be returned.
    
      - currentPerInstanceUVSet : cpi  (bool)          [query,edit]
          This is a query-only flag for use when the current uv set is a per-instance uv set family. This returns the member of
          the set family that corresponds to the currently select instance.
    
      - currentUVSet : cuv             (bool)          [create,query,edit]
          This flag when used will set the current uv set that the object needs to work on, to be the uv set corresponding to the
          name specified with the uvSet flag. This does require that a uvSet with the specified name exist. When queried, this
          returns the current uv set.
    
      - delete : d                     (bool)          [create,query,edit]
          This flag when used will result in the deletion of the uv set corresponding to the name specified with the uvSet flag.
    
      - newUVSet : nuv                 (unicode)       [create,query,edit]
          Specifies the name that the uv set corresponding to the name specified with the uvSet flag, needs to be renamed to.
    
      - perInstance : pi               (bool)          [create,query,edit]
          This flag can be used in conjunction with the create flag to indicate whether or not the uv set is per-instance. When
          you create a per-instance uv set, the set will be applied as shared between all selected instances of the shape unless
          the unshared flag is used. The perInstance flag can be used in query mode with the currentUVSet or allUVSets  flag to
          indicate that the set family names (i.e. not containing instance identifiers) will be returned by the query. In query
          mode, this flag can accept a value.
    
      - projections : pr               (bool)          [query,edit]
          This flag when used in a query will return a list of polygon uv projection node names. The order of the list is from
          most-recently-applied to least-recently-applied.
    
      - rename : rn                    (bool)          [create,query,edit]
          This flag when used will result in the renaming of the uv set corresponding to the name specified with the uvSet flag to
          the name specified using the newUVSet flag.
    
      - shareInstances : si            (bool)          [create,query,edit]
          This flag is used to modify the sharing of per-instance uv sets within a given uv set family so that all selected
          instances share the specified set. In query mode, it returns a list of the instances that share the set specified by the
          uvSet flag.
    
      - unshared : us                  (bool)          [create,query,edit]
          This flag can be used in conjunction with the create and perInstance flags to indicate that the newly created per-
          instance set should be created with a separate set per instance.
    
      - uvSet : uvs                    (unicode)       [create,query,edit]
          Specifies the name of the uv set that this command needs to work on. This flag has to be specified for this command to
          do anything meaningful other than query the current uv set. Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.polyUVSet`
    """

    pass


def polyInfo(*args, **kwargs):
    """
    Command queries topological information on polygonal objects and components. So, the command will require the following
    to be specified:         - selection list to query
    
    Flags:
      - edgeToFace : ef                (bool)          [create]
          Returns the faces that share the specified edge. Requires edges to be selected.
    
      - edgeToVertex : ev              (bool)          [create]
          Returns the vertices defining an edge. Requires edges to be selected.
    
      - faceNormals : fn               (bool)          [create]
          Returns face normals of the specified object. If faces are selected the command returns the face normals of selected
          faces. Else it returns the face normals of all the faces of the object.
    
      - faceToEdge : fe                (bool)          [create]
          Returns the edges defining a face. Requires faces to be selected.
    
      - faceToVertex : fv              (bool)          [create]
          Returns the vertices defining a face. Requires faces to be selected.
    
      - invalidEdges : ie              (bool)          [create]
          Find all edges that are not associated with any face in the mesh.
    
      - invalidVertices : iv           (bool)          [create]
          Find all vertices that are not associated with any face in the mesh.
    
      - laminaFaces : lf               (bool)          [create]
          Find all lamina faces in the specified objects.
    
      - nonManifoldEdges : nme         (bool)          [create]
          Find all non-manifold edges in the specified objects.
    
      - nonManifoldUVEdges : nue       (bool)          [create]
          Find all non-manifold UV edges in the specified objects.
    
      - nonManifoldUVs : nuv           (bool)          [create]
          Find all non-manifold UVs in the specified objects.
    
      - nonManifoldVertices : nmv      (bool)          [create]
          Find all non-manifold vertices in the specified objects.
    
      - vertexToEdge : ve              (bool)          [create]
          Returns the Edges connected to a vertex. Requires vertices to be selected.
    
      - vertexToFace : vf              (bool)          [create]
          Returns the faces that share the specified vertex. Requires vertices to be selected.                               Flag
          can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyInfo`
    """

    pass


def reverseCurve(*args, **kwargs):
    """
    The reverseCurve command reverses the direction of a curve or curve-on-surface.  A string is returned containing the
    pathname of the newly reversed curve and the name of the resulting dependency node.  The reversed curve has the same
    parameter range as the original curve.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curveOnSurface : cos           (bool)          [create]
          If possible, create 2D curve as a result.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - noChanges : nc                 (bool)          []
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
    
    Derived from mel command `maya.cmds.reverseCurve`
    """

    pass


def blend2(*args, **kwargs):
    """
    This command creates a surface by blending between given curves. This is an enhancement (more user control) compared to
    blend which is now obsolete.
    
    Flags:
      - autoAnchor : aa                (bool)          [create,query,edit]
          If true and both paths are closed, automatically determine the value on the right rail so that they match Default:true
    
      - autoNormal : an                (bool)          [create,query,edit]
          If true, the direction of each starting tangent is computed based on given geometry. Default:true
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - crvsInFirstRail : cfr          (int)           []
    
      - flipLeftNormal : fln           (bool)          [create,query,edit]
          If true, flip the starting tangent off the left boundary. Default:false
    
      - flipRightNormal : frn          (bool)          [create,query,edit]
          If true, flip the starting tangent off the right boundary. Default:false
    
      - frozen : fzn                   (bool)          []
    
      - leftAnchor : la                (float)         [create,query,edit]
          The reference parameter on the left boundary where the blend surface starts in the case of the closed rail. Default:0.0
    
      - leftEnd : le                   (float)         [create,query,edit]
          The reference parameter on the left boundary where the blend surface ends. Default:1.0
    
      - leftStart : ls                 (float)         [create,query,edit]
          The reference parameter on the left boundary where the blend surface starts. Default:0.0
    
      - multipleKnots : mk             (bool)          [create,query,edit]
          If true, use the new blend which produces fully multiple interior knots Default:true
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)Advanced flags
    
      - positionTolerance : pt         (float)         [create,query,edit]
          The positional C(0) tolerance of the blend surface to the adjacent surfaces. Default:0.1
    
      - reverseLeft : rvl              (bool)          [create,query,edit]
          If true, reverse the direction off the left boundary.  autoDirection must be false for this value to be considered.
          Default:false
    
      - reverseRight : rvr             (bool)          [create,query,edit]
          If true, reverse the direction of the right boundary.  autoDirection must be false for this value to be considered.
          Default:false
    
      - rightAnchor : ra               (float)         [create,query,edit]
          The reference parameter on the right boundary where the blend surface starts in the case of the closed rail. Default:0.0
    
      - rightEnd : re                  (float)         [create,query,edit]
          The reference parameter on the right boundary where the blend surface ends. Default:1.0
    
      - rightStart : rs                (float)         [create,query,edit]
          The reference parameter on the right boundary where the blend surface starts. Default:0.0
    
      - tangentTolerance : tt          (float)         [create,query,edit]
          The tangent G(1) continuity tolerance of the blend surface to the adjacent surfaces. Default:0.1                  Common
          flags
    
    
    Derived from mel command `maya.cmds.blend2`
    """

    pass


def polyCreateFacet(*args, **kwargs):
    """
    Create a new polygonal object with the specified face, which will be closed. List of arguments must have at least 3
    points.
    
    Flags:
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - hole : hl                      (bool)          [create]
          Add a hole. The following points will define a hole. Holes can be defined either clockwise or counterclockwise.  Note
          that this flag is not recommended for use in Python.  When specifying facets with the point flag in Python, pass in an
          empty point ()when you want to start specifying a hole.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - point : p                      (float, float, float) [create]
          Adds a new point to the face. Coordinates of points are given in world reference.  The point flag may also be passed
          with no arguments.  That indicates that the following points will specify a hole.  Passing the point flag with no
          arguments is the same as using the holeflag, except that it will work in Python.
    
      - subdivision : s                (int)           [create,query,edit]
          This flag specifies the level of subdivision. Subdivides edges into the given number of edges. C: Default is 1 (no
          subdivision). Q: When queried, this flag returns an int.
    
      - texture : tx                   (int)           [create,query,edit]
          Specifies how the face is mapped. 0 - None; 1 - Normalize; 2 - Unitize C: Default is 0 (no mapping). Q: When queried,
          this flag returns an intCommon flags
    
    
    Derived from mel command `maya.cmds.polyCreateFacet`
    """

    pass


def polyProjection(*args, **kwargs):
    """
    Creates a mapping on the selected polygonal faces.  When construction         history is created, the name of the new
    node is returned.  In other cases,         the command returns nothing.
    
    Flags:
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off (where applicable).
    
      - createNewMap : cm              (bool)          [create]
          Create new map if it does not exist.
    
      - imageCenterX : icx             (float)         [create]
          Specifies the X (U) translation of the projected UVs.         Default is 0.5.
    
      - imageCenterY : icy             (float)         [create]
          Specifies the Y (V) translation of the projected UVs.         Default is 0.5.
    
      - imageScaleU : isu              (float)         [create]
          Specifies the U scale factor of the projected UVs.         Default is 1.
    
      - imageScaleV : isv              (float)         [create]
          Specifies the V scale factor of the projected UVs.         Default is 1.
    
      - insertBeforeDeformers : ibd    (bool)          [create]
          Specifies if the projection node should be inserted         before or after deformer nodes already applied to the shape.
          Inserting the projection after the deformer leads to texture         swimming during animation and is most often
          undesirable.         Default is on.
    
      - keepImageRatio : kir           (bool)          [create]
          Specifies if the xy scaling in the planar projection has to be         uniform.  By setting this flag, the texture
          aspect ratio is         preserved.  This flag is ignored for cylindrical and spherical         projections.
    
      - mapDirection : md              (unicode)       [create]
          Specifies the direction of the projection.  By specifying this flag, the         projection placement values (pcx, pcy,
          pcz, rx, ry, rz, psu, psv) are         internally computed.  If both this flag and the projection values are
          specified, the projection values are ignored.         Valid Values are :                 X
          Projects along the X Axis                 Y                       Projects along the Y Axis                 Z
          Projects along the Z Axis                 bestPlane       Projects on the best plane fitting the object
          camera          Projects along the viewing direction                 perspective Creates perspective projection if
          current camera is perspective         Default is bestPlane.
    
      - projectionCenterX : pcx        (float)         [create]
          Specifies the X coordinate of the center of the projection manipulator.
    
      - projectionCenterY : pcy        (float)         [create]
          Specifies the Y coordinate of the center of the projection manipulator.
    
      - projectionCenterZ : pcz        (float)         [create]
          Specifies the Z coordinate of the center of the projection manipulator.
    
      - projectionScaleU : psu         (float)         [create]
          Specifies the U scale component of the projection manipulator.
    
      - projectionScaleV : psv         (float)         [create]
          Specifies the V scale component of the projection manipulator.
    
      - rotateX : rx                   (float)         [create]
          Specifies the X-axis rotation of the projection manipulator.
    
      - rotateY : ry                   (float)         [create]
          Specifies the Y-axis rotation of the projection manipulator.
    
      - rotateZ : rz                   (float)         [create]
          Specifies the Z-axis rotation of the projection manipulator.
    
      - rotationAngle : ra             (float)         [create]
          Specifies the rotation of the projected UVs in the UV space.         Default is 0.
    
      - seamCorrect : sc               (bool)          [create]
          Specifies if seam correction has to be done for spherical         and cylindrical projections.  This flag is ignored, if
          the         planar projection is specified.
    
      - smartFit : sf                  (bool)          [create]
          Specifies if the projection manipulator has to be placed         fitting the object.  Used for cylindrical and spherical
          projections.  For smart fitting the planar projection, the         mapDirection flag has to be used, since there are
          several         options for smart fitting a planar projection.
    
      - type : t                       (unicode)       [create]
          Specify the type of mapping to be performed.         Valid values for the STRING are
          planarcylindricalsphericalDefault is planar.
    
      - uvSetName : uvs                (unicode)       [create]
          Specifies name of the uv set to work on.                                   Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyProjection`
    """

    pass


def grid(*args, **kwargs):
    """
    This command changes the size and spacing of lines on the ground plane displayed in the perspective and orthographic
    views. This command lets you reset the ground plane, change its size and grid line spacing, grid subdivisions and
    display options. In query mode, return type is based on queried flag.
    
    Flags:
      - default : df                   (bool)          [query]
          Used to specify/query default values.
    
      - displayAxes : da               (bool)          [query]
          Specify true to display the grid axes.
    
      - displayAxesBold : dab          (bool)          [query]
          Specify true to accent the grid axes by drawing them with a thicker line.
    
      - displayDivisionLines : ddl     (bool)          [query]
          Specify true to display the subdivision lines between grid lines.
    
      - displayGridLines : dgl         (bool)          [query]
          Specify true to display the grid lines.
    
      - displayOrthographicLabels : dol (bool)          [query]
          Specify true to display the grid line numeric labels in the orthographic views.
    
      - displayPerspectiveLabels : dpl (bool)          [query]
          Specify true to display the grid line numeric labels in the perspective view.
    
      - divisions : d                  (int)           [query]
          Sets the number of subdivisions between major grid lines. The default is 5. If the spacing is 5 units, setting divisions
          to 5 will cause division lines to appear 1 unit apart.
    
      - orthographicLabelPosition : olp (unicode)       [query]
          The position of the grid's numeric labels in orthographic views. Valid values are    axisand edge.
    
      - perspectiveLabelPosition : plp (unicode)       [query]
          The position of the grid's numeric labels in perspective views. Valid values are    axisand edge.
    
      - reset : r                      (bool)          []
          Resets the ground plane to its default values
    
      - size : s                       (float)         [query]
          Sets the size of the grid in linear units.  The default is 12 units.
    
      - spacing : sp                   (float)         [query]
          Sets the spacing between major grid lines in linear units. The default is 5 units.
    
      - style : st                     (int)           [query]
          This flag is obsolete and should not be used.
    
      - toggle : tgl                   (bool)          [query]
          Turns the ground plane display off in all windows, including orthographic windows.  Default is true.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.grid`
    """

    pass


def detachSurface(*args, **kwargs):
    """
    The detachSurface command detaches a surface into pieces, given a list of parameter values and a direction.  You can
    also specify which pieces to keep and which to discard using the -kflag. The names of the newly detached surface(s) are
    returned.  If history is on, the name of the resulting dependency node is also returned. You can only detach in either U
    or V (not both) with a single detachSurface operation. You can use this command to open a closed surface at a particular
    parameter value.  You would use this command with only one -pflag. If you are specifying -kflags, then you must specify
    one, none or all -kflags.  If you are specifying all -kflags, there must be one more -kflag than -pflags.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - direction : d                  (int)           [create,query,edit]
          Direction in which to detach: 0 - V direction, 1 - U direction Default:1
    
      - frozen : fzn                   (bool)          []
    
      - keep : k                       (bool)          [create,query,edit]
          Keep the detached pieces. Default:true
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - parameter : p                  (float)         [create,query,edit]
          Parameter at which to detach. Default:0.0                  Common flags
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
    
    Derived from mel command `maya.cmds.detachSurface`
    """

    pass


def polyMapCut(*args, **kwargs):
    """
    Cut along edges of the texture mapping. The cut edges become map borders.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - moveRatio : mr                 (float)         []
    
      - moveratio : mvr                (float)         [query,edit]
          Cut open ratio related to the neighbor edge length of cut edge.                  Common flags
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyMapCut`
    """

    pass


def rebuildCurve(*args, **kwargs):
    """
    This command rebuilds a curve by modifying its parameterization. In some cases the shape may also change. The
    rebuildType (-rt) determines how the curve is to be rebuilt. The optional second curve can be used to specify a
    reference parameterization.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting curve 1 - linear, 2 - quadratic, 3 - cubic, 5 - quintic, 7 - heptic Default:3
    
      - endKnots : end                 (int)           [create,query,edit]
          End conditions for the curve 0 - uniform end knots, 1 - multiple end knots, Default:0
    
      - fitRebuild : fr                (bool)          [create,query,edit]
          If true use the least squares fit rebuild. Otherwise use the convert method. Default:true
    
      - frozen : fzn                   (bool)          []
    
      - keepControlPoints : kcp        (bool)          [create,query,edit]
          If true, the CVs will remain the same. This forces uniform parameterization unless rebuildType is matchKnots.
          Default:false
    
      - keepEndPoints : kep            (bool)          [create,query,edit]
          If true, keep the endpoints the same. Default:true
    
      - keepRange : kr                 (int)           [create,query,edit]
          Determine the parameterization for the resulting curve. 0 - reparameterize the resulting curve from 0 to 1, 1 - keep the
          original curve parameterization, 2 - reparameterize the result from 0 to number of spans Default:1
    
      - keepTangents : kt              (bool)          [create,query,edit]
          If true, keep the end tangents the same. Default:true
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - noChanges : nc                 (bool)          []
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.
    
      - rebuildType : rt               (int)           [create,query,edit]
          How to rebuild the input curve. 0 - uniform, 1 - reduce spans, 2 - match knots, 3 - remove multiple knots, 4 - curvature
          5 - rebuild ends 6 - clean Default:0
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - smartSurfaceCurveRebuild : scr (bool)          [create,query,edit]
          If true, curve on surface is rebuild in 3D and 2D info is kept Default:false
    
      - smooth : sm                    (float)         []
    
      - spans : s                      (int)           [create,query,edit]
          The number of spans in resulting curve Used only if rebuildType is uniform. Default:4
    
      - tolerance : tol                (float)         [create,query,edit]
          The tolerance with which to rebuild. Default:0.01                  Common flags
    
    
    Derived from mel command `maya.cmds.rebuildCurve`
    """

    pass


def hasMetadata(*args, **kwargs):
    """
    This command is used to query for the presence of metadata elements on a node, components, or scene. The command works
    at all levels of metadata presence, from the existence of any metadata at all on a node or scene right down to the
    presence of metadata values set on a particular metadata Stream index.  Filter FlagschannelName- Only look for metadata
    on one particular Channel typestreamName- Only look for metadata on one particular named Stream. When used in
    conjunction with channelNamethen ignore Streams with a matching name but a different Channel typeindex- Only look for
    metadata on one or more specific Index values of a Stream. Requires use of the streamNameflag. Does not require the
    indexTypeflag as that will be inferred by the streamName.startIndex/endIndex- Same as indexbut using an entire range of
    Index values rather than a single oneindexType- Only look for metadata using a particular Index type. Can have its scope
    narrowed by other filter flags as well.ignoreDefault- Treat any metadata that still has the default value (e.g. 0 for
    numerics, for strings) the same as metadata that isn't present. This means that any metadata with default values will
    not be reported. It is useful for quickly finding values that you have changed. When this flag is set you can also use
    the memberNamefilter to narrow down the check to a particular member of the metadata Structure. Without that filter it
    will only skip over metadata where every member of the Structure has a non-default value.memberName- Only look at one
    particular Member in the metadata in a Structure. Only used when checking for non-default values as existence is based
    on the entire Structure, not any particular Member.Operation Flagsnormal mode- Return True for every specified location
    containing metadata. This combines with the filter flags as follows:no flag- True if there is any metadata at all on the
    node or scenechannelName- True if there is any metadata at all on the Channel         with the given namestreamName-
    True if there is any metadata at all on the Stream         with the given nameindex/startIndex/endIndex- An array of
    booleans ordered the same         as the natural ordering of the Index values (i.e. specifying index 3, 2, and 4
    in that order will still return booleans in the order for indices 2,3,4)         where True means that there is metadata
    assigned at that Index. This form is         better suited with the asListmodification since with that variation it
    is easier to tell exactly which indices have the metadata.asList- Adding this flag switches the return values from a
    single boolean or array of booleans to an array of strings indicating exactly which metadata elements have values. The
    return values of the command are changed to be the following:no flag- List of Channel names with metadatachannelName-
    List of Stream names in the Channel with metadatastreamName- List of Index values on the Stream with
    metadataindex/startIndex/endIndex- List of Index values with metadata,         restricted to the set of specified Index
    values.
    
    Flags:
      - asList : al                    (bool)          [create]
          Use this flag when you want to return string values indicating where the metadata lives rather than boolean values. See
          the command description for more details on what this flag will return.
    
      - channelName : cn               (unicode)       [create,query]
          Filter the metadata selection to only recognize metadata belonging to the specified named Channel (e.g. vertex). This
          flag is ignored if the components on the selection list are being used to specify the metadata of interest. In query
          mode, this flag can accept a value.
    
      - channelType : cht              (unicode)       [create,query]
          Obsolete - use the 'channelName' flag instead. In query mode, this flag can accept a value.
    
      - endIndex : eix                 (unicode)       [create]
          The metadata is stored in a Stream, which is an indexed list. If you have mesh components selected then the metadata
          indices are implicit in the list of selected components. If you select only the node or scene then this flag may be used
          in conjunction with the startIndexflag to specify a range of indices from which to retrieve the metadata. It is an error
          to have the value of startIndexbe greater than that of endIndex.  See also the indexflag for an alternate way to specify
          multiple indices. This flag can only be used on index types that support a range (e.g. integer values - it makes no
          sense to request a range between two strings)  In query mode, this flag can accept a value.
    
      - ignoreDefault : id             (bool)          [create]
          Use this flag when you want to skip over any metadata that has only default values. i.e. the metadata may exist but it
          hasn't had a new value set yet (non-zero for numerics, non-empty strings, etc.) See the command description for more
          details on how this flag filters the search.
    
      - index : idx                    (unicode)       [create,query]
          In the typical case metadata is indexed using a simple integer value. Certain types of data may use other index types.
          e.g. a vertexFacecomponent will use a pairindex type, which is two integer values; one for the face ID of the component
          and the second for the vertex ID.  The indexflag takes a string, formatted in the way the specified indexTyperequires.
          All uses of the indexflag have the same indexType. If the type was not specified it is assumed to be a simple integer
          value.  In query mode, this flag can accept a value.
    
      - indexType : idt                (unicode)       [create,query]
          Name of the index type the new Channel should be using. If not specified this defaults to a simple integer index. Of the
          native types only a mesh vertexFacechannel is different, using a pairindex type. In query mode, this flag can accept a
          value.
    
      - memberName : mn                (unicode)       [create]
          Name of the Structure member being checked. The names of the members are set up in the Structure definition, either
          through the description passed in through the dataStructurecommand or via the API used to create that Structure. As the
          assignment of metadata is on a per-structure basis this flag only needs to be specified when querying for non-default
          values. If you query for non-default values and omit this flag then it checks that any of the members have a non-default
          value.
    
      - scene : scn                    (bool)          [create,query]
          Use this flag when you want to add metadata to the scene as a whole rather than to any individual nodes. If you use this
          flag and have nodes selected the nodes will be ignored and a warning will be displayed.
    
      - startIndex : six               (unicode)       [create]
          The metadata is stored in a Stream, which is an indexed list. If you have mesh components selected then the metadata
          indices are implicit in the list of selected components. If you select only the node or scene then this flag may be used
          in conjunction with the endIndexflag to specify a range of indices from which to retrieve the metadata. It is an error
          to have the value of startIndexbe greater than that of endIndex.  See also the indexflag for an alternate way to specify
          multiple indices. This flag can only be used on index types that support a range (e.g. integer values - it makes no
          sense to request a range between two strings)  In query mode, this flag can accept a value.
    
      - streamName : stn               (unicode)       [create,query]
          Name of the metadata Stream. Depending on context it could be the name of a Stream to be created, or the name of the
          Stream to pass through the filter. In query mode, this flag can accept a value.Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.hasMetadata`
    """

    pass


def polyMoveUV(*args, **kwargs):
    """
    Moves selected UV coordinates in 2D space. As the selected UVs are adjusted, the way the image is mapped onto the object
    changes accordingly. This command manipulates the UV values without changing the 3D geometry of the object.
    
    Flags:
      - axisLen : l                    (float, float)  []
    
      - axisLenX : lx                  (float)         []
    
      - axisLenY : ly                  (float)         []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - pivot : pvt                    (float, float)  [create,query,edit]
          This flag specifies the pivot for scaling and rotation. C: Default is 0.0 0.0. Q: When queried, this flag returns a
          float[2].
    
      - pivotU : pvu                   (float)         [create,query,edit]
          This flag specifies U for the pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a
          float.
    
      - pivotV : pvv                   (float)         [create,query,edit]
          This flag specifies V for the pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a
          float.
    
      - random : ran                   (float)         [create,query,edit]
          This flag specifies the random value for all parameters. C: Default is 0.0. The range is [-10.0, 10.0]. Q: When queried,
          this flag returns a float. Common flags
    
      - rotationAngle : ra             (float)         [create,query,edit]
          Angle of rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - scale : s                      (float, float)  [create,query,edit]
          This flag specifies the scaling vector. C: Default is 1.0 1.0. Q: When queried, this flag returns a float.
    
      - scaleU : su                    (float)         [create,query,edit]
          This flag specifies U for the scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleV : sv                    (float)         [create,query,edit]
          This flag specifies V for the scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - translate : t                  (float, float)  [create,query,edit]
          This flag specifies the translation vector. C: Default is 0.0 0.0. Q: When queried, this flag returns a float[2].
    
      - translateU : tu                (float)         [create,query,edit]
          This flag specifies the U translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateV : tv                (float)         [create,query,edit]
          This flag specifies the V translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyMoveUV`
    """

    pass


def polyWedgeFace(*args, **kwargs):
    """
    Extrude faces about an axis. The axis is the average of all the selected edges. If the edges are not aligned, the wedge
    may not look intuitive.  To separately wedge faces about different wedge axes, the command should be issued as many
    times as the wedge axes. (as in the second example)
    
    Flags:
      - axis : ax                      (float, float, float) [create]
          This flag (along with -center) can be used instead of the -edge flag to specify the axis about which the wedge is
          performed. The flag expects three coordinates that form a vector about which the rotation is performed.
    
      - axisX : asx                    (float)         []
    
      - axisY : asy                    (float)         []
    
      - axisZ : asz                    (float)         []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - center : cen                   (float, float, float) [create]
          This flag (along with -axis) can be used instead of the -edge flag to specify the location about which the wedge is
          performed. The flag expects three coordinates that define the center of rotation.
    
      - centerX : ctx                  (float)         []
    
      - centerY : cty                  (float)         []
    
      - centerZ : ctz                  (float)         []
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - divisions : d                  (int)           [create]
          This flag specifies the number of subdivisions along the extrusion.
    
      - edge : ed                      (int)           [create]
          This flag specifies the edgeId that should be used to perform the wedge about. Multiple edges can be specified. The
          wedge operation is performed about an axis that is the average of all the edges. It is recommended that only colinear
          edges are used, otherwise the result may not look intuitive. Instead of specifying the -edge flag, the wedge can be
          performed about a point and axis. See the -center and -axis flags for details.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - wedgeAngle : wa                (float)         [create]
          This flag specifies the angle of rotation.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyWedgeFace`
    """

    pass


def polyMultiLayoutUV(*args, **kwargs):
    """
    place the UVs of the selected polygonal objects so that they do not overlap.
    
    Flags:
      - flipReversed : fr              (bool)          [create]
          If this flag is turned on, the reversed UV pieces are fliped.
    
      - gridU : gu                     (int)           [create]
          The U size of the grids.
    
      - gridV : gv                     (int)           [create]
          The V size of the grids.
    
      - layout : l                     (int)           [create]
          How to move the UV pieces, after cuts are applied: 0 No move is applied. 1 Layout the pieces along the U axis. 2 Layout
          the pieces in a square shape. 3 Layout the pieces in grids. 4 Layout the pieces in nearest regions.
    
      - layoutMethod : lm              (int)           [create]
          // -lm/layoutMethod     layoutMethod  integer//      (C, E, Q) Which layout method to use: //              0 Block
          Stacking. //              1 Shape Stacking.
    
      - offsetU : ou                   (float)         [create]
          Offset the layout in the U direction by the given value.
    
      - offsetV : ov                   (float)         [create]
          Offset the layout in the V direction by the given value.
    
      - percentageSpace : ps           (float)         [create]
          When layout is set to square, this value is a percentage of the texture area which is added around each UV piece. It can
          be used to ensure each UV piece uses different pixels in the texture. Maximum value is 5 percent.
    
      - prescale : psc                 (int)           [create]
          Prescale the shell before laying it out. 0 No scale is applied. 1 Object space scaling applied. 2 World space scaling
          applied.
    
      - rotateForBestFit : rbf         (int)           [create]
          How to rotate the pieces, before move: 0 No rotation is applied. 1 Only allow 90 degree rotations. 2 Allow free
          rotations.
    
      - scale : sc                     (int)           [create]
          How to scale the pieces, after move: 0 No scale is applied. 1 Uniform scale to fit in unit square. 2 Non proportional
          scale to fit in unit square.
    
      - sizeU : su                     (float)         [create]
          Scale the layout in the U direction by the given value.
    
      - sizeV : sv                     (float)         [create]
          Scale the layout in the V direction by the given value.
    
      - uvSetName : uvs                (unicode)       [create]
          Specifies the name of the uv set to edit uvs on. If not specified will use the current uv set if it exists.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyMultiLayoutUV`
    """

    pass


def nurbsEditUV(*args, **kwargs):
    """
    Command edits uvs on NURBS objects. When used with the query flag, it returns the uv values associated with the
    specified components.
    
    Flags:
      - angle : a                      (float)         [create,query]
          Specifies the angle value (in degrees) that the uv values are to be rotated by.
    
      - pivotU : pu                    (float)         [create,query]
          Specifies the pivot value, in the u direction, about which the scale or rotate is to be performed.
    
      - pivotV : pv                    (float)         [create,query]
          Specifies the pivot value, in the v direction, about which the scale or rotate is to be performed.
    
      - relative : r                   (bool)          [create,query]
          Specifies whether this command is editing the values relative to the currently existing values. Default is true;
    
      - rotation : rot                 (bool)          [create,query]
          Specifies whether this command is editing the values with rotation values
    
      - scale : s                      (bool)          [create,query]
          Specifies whether this command is editing the values with scale values
    
      - scaleU : su                    (float)         [create,query]
          Specifies the scale value in the u direction.
    
      - scaleV : sv                    (float)         [create,query]
          Specifies the scale value in the v direction.
    
      - uValue : u                     (float)         [create,query]
          Specifies the value, in the u direction - absolute if relative flag is false..
    
      - vValue : v                     (float)         [create,query]
          Specifies the value, in the v direction - absolute if relative flag is false..                             Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.nurbsEditUV`
    """

    pass


def coarsenSubdivSelectionList(*args, **kwargs):
    """
    Coarsens a subdivision surface set of components based on the selection list. The selected components are selected at a
    coarser level.
    
    
    Derived from mel command `maya.cmds.coarsenSubdivSelectionList`
    """

    pass


def polyOutput(*args, **kwargs):
    """
    Dumps a description of internal memory representation of poly objects. If no objects are specified in the command line,
    then the objects from the active list are used. If information on the geometry in the history of a poly shape is
    desired, then the plug of interest needs to be specified in the command line. Default behaviour is to print only a
    summary. Use the flags above to get more details on a specific part of the object.
    
    Flags:
      - allValues : a                  (bool)          [create]
          Shortcut for setting all the flags above
    
      - color : c                      (bool)          [create]
          Prints the color per vertex. In case of multiple sets, all sets are printed.
    
      - colorDesc : cd                 (bool)          [create]
          Print the color per vertex description. Each integer is an entry in the color array.
    
      - edge : e                       (bool)          [create]
          Print the edge description.
    
      - edgeFace : ef                  (bool)          [create]
          Prints the edge to face adjascency list. Only available if the information is already computed on the object.
    
      - face : f                       (bool)          [create]
          Print the faces description
    
      - faceNorm : fn                  (bool)          [create]
          Prints the normals per face. Only available if the information is already computed on the object.
    
      - force : fo                     (bool)          [create]
          Force evaluation of missing pieces before printing.
    
      - group : g                      (bool)          [create]
          Print the groups of the object.
    
      - noOutput : no                  (bool)          [create]
          Dont output any data.  Would be useful if you want to just evaluate the data, for testing purposes.
    
      - normDesc : nd                  (bool)          [create]
          Prints the normals per vertex description. Each integer is an entry in the vertNorm array. Only available if the
          information is already computed on the object.
    
      - outputFile : of                (unicode)       []
    
      - triangle : t                   (bool)          [create]
          Prints the triangles per face. Only available if the information is already computed on the object.
    
      - uvDesc : uvd                   (bool)          [create]
          Print the UV description. Each integer is an entry in the uvValue array.
    
      - uvValue : uv                   (bool)          [create]
          Prints the UV positions. In case of multiple UV sets, all sets are printed.
    
      - vert : v                       (bool)          [create]
          Prints the vertex positions.
    
      - vertEdge : ve                  (bool)          [create]
          Prints the vertex to edge adjascency list. Only available if the information is already computed on the object.
    
      - vertNorm : vn                  (bool)          [create]
          Prints the normals per vertex. Only available if the information is already computed on the object.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyOutput`
    """

    pass


def pointOnSurface(*args, **kwargs):
    """
    This command returns information for a point on a surface. If no flag is specified, this command assumes p/position by
    default. If more than one flag is specifed, then a string array is returned.
    
    Flags:
      - caching : cch                  (bool)          []
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.                  Flag can have multiple arguments, passed either as a tuple or
          a list.
    
      - frozen : fzn                   (bool)          []
    
      - nodeState : nds                (int)           []
    
      - normal : no                    (bool)          [create,query,edit]
          Returns the (x,y,z) normal of the specified point on the surface
    
      - normalizedNormal : nn          (bool)          [create,query,edit]
          Returns the (x,y,z) normalized normal of the specified point on the surface
    
      - normalizedTangentU : ntu       (bool)          [create,query,edit]
          Returns the (x,y,z) normalized U tangent of the specified point on the surface
    
      - normalizedTangentV : ntv       (bool)          [create,query,edit]
          Returns the (x,y,z) normalized V tangent of the specified point on the surface
    
      - parameterU : u                 (float)         [query,edit]
          The U parameter value on surface Default:0.0
    
      - parameterV : v                 (float)         [query,edit]
          The V parameter value on surface Default:0.0
    
      - position : p                   (bool)          [create,query,edit]
          Returns the (x,y,z) positon of the specified point on the surface
    
      - tangentU : tu                  (bool)          [create,query,edit]
          Returns the (x,y,z) U tangent of the specified point on the surface
    
      - tangentV : tv                  (bool)          [create,query,edit]
          Returns the (x,y,z) V tangent of the specified point on the surface
    
      - turnOnPercentage : top         (bool)          [query,edit]
          Whether the parameter is normalized (0,1) or not Default:false                  Common flags
    
    
    Derived from mel command `maya.cmds.pointOnSurface`
    """

    pass


def polyMapSewMove(*args, **kwargs):
    """
    This command can be used to Move and Sew together separate UV pieces along geometric edges. UV pieces that correspond to
    the same geometric edge, are merged together by moving the smaller piece to the larger one.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - limitPieceSize : lps           (bool)          [create,query,edit]
          When on, this flag specifies that the face number limit described above should be used.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - numberFaces : nf               (int)           [create,query,edit]
          Maximum number of faces in a UV piece. When trying to combine two UV pieces into a single one, the merge operation is
          rejected if the smaller piece has more faces than the number specified by this flag.This flag is only used when
          limitPieceSizeis set to on.
    
      - uvSetName : uvs                (unicode)       [create,query]
          Specifies the name of the uv set to edit uvs on. If not specified will use the current uv set if it exists.
          Common flags
    
      - worldSpace : ws                (bool)          []
    
    
    Derived from mel command `maya.cmds.polyMapSewMove`
    """

    pass


def torus(*args, **kwargs):
    """
    The torus command creates a new torus and/or a dependency node that creates one, and returns their names.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          The primitive's axis
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting surface: 1 - linear, 3 - cubic Default:3
    
      - endSweep : esw                 (float)         [create,query,edit]
          The angle at which to end the surface of revolution. Default is 2Pi radians, or 360 degrees. Default:6.2831853
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - heightRatio : hr               (float)         [create,query,edit]
          Ratio of heightto widthDefault:2.0
    
      - minorSweep : msw               (float)         [create,query,edit]
          The sweep angle for the minor circle in the torus Default:6.2831853
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - pivot : p                      (float, float, float) [create,query,edit]
          The primitive's pivot point
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)Advanced flags
    
      - radius : r                     (float)         [create,query,edit]
          The radius of the object Default:1.0
    
      - sections : s                   (int)           [create,query,edit]
          The number of sections determines the resolution of the surface in the sweep direction. Used only if useTolerance is
          false. Default:8
    
      - spans : nsp                    (int)           [create,query,edit]
          The number of spans determines the resolution of the surface in the opposite direction. Default:1
    
      - startSweep : ssw               (float)         [create,query,edit]
          The angle at which to start the surface of revolution Default:0
    
      - tolerance : tol                (float)         [create,query,edit]
          The tolerance with which to build the surface. Used only if useTolerance is true Default:0.01
    
      - useTolerance : ut              (bool)          [create,query,edit]
          Use the specified tolerance to determine resolution. Otherwise number of sections will be used. Default:false
          Common flags
    
    
    Derived from mel command `maya.cmds.torus`
    """

    pass


def smoothCurve(*args, **kwargs):
    """
    The smooth command smooths the curve at the given control points.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - smoothness : s                 (float)         [create,query,edit]
          smoothness factor Default:10.0                  Common flags
    
    
    Derived from mel command `maya.cmds.smoothCurve`
    """

    pass


def extrude(*args, **kwargs):
    """
    This command computes a surface given a profile curve and possibly a path curve. There are three ways to extrude a
    profile curve. The most basic method is called a distanceextrude where direction and length are specified. No path curve
    is necessary in this case. The second method is called flatextrude. This method sweeps the profile curve down the path
    curve without changing the orientation of the profile curve. Finally, the third method is called tubeextrude. This
    method sweeps a profile curve down a path curve while the profile curve rotates so that it maintains a relationship with
    the path curve.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degreeAlongLength : dl         (int)           [create,query,edit]
          Surface degree along the distance when a distance extrude is performed Default:1
    
      - direction : d                  (float, float, float) [create,query,edit]
          The direction in which to extrude. Use only for distance extrudeType and useProfileNormal off
    
      - directionX : dx                (float)         [create,query,edit]
          X of the direction Default:0
    
      - directionY : dy                (float)         [create,query,edit]
          Y of the direction Default:1
    
      - directionZ : dz                (float)         [create,query,edit]
          Z of the direction Default:0
    
      - extrudeType : et               (int)           [create,query,edit]
          The extrude type (distance-0, flat-1, or tube-2) Default:2
    
      - fixedPath : fpt                (bool)          [create,query,edit]
          If true, the resulting surface will be placed at the path curve. Otherwise, the resulting surface will be placed at the
          profile curve. Default:false
    
      - frozen : fzn                   (bool)          []
    
      - length : l                     (float)         [create,query,edit]
          The distance to extrude. Use only for distance extrudeType Default:1
    
      - mergeItems : mi                (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - pivot : p                      (float, float, float) [create,query,edit]
          The pivot point used for tube extrudeType
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.
    
      - rebuild : rb                   (bool)          [create]
          Rebuild the input curve(s) before using them in the operation.  Use nurbsCurveRebuildPref to set the parameters for the
          conversion.                  Advanced flags
    
      - reverseSurfaceIfPathReversed : rsp (bool)          [create,query,edit]
          If true, extrude type is tube (2) and path has been internally reversed then computed surface is reversed in the
          direction corresponding to the path. Default:false
    
      - rotation : ro                  (float)         [create,query,edit]
          Amount to rotate the profile curve as it sweeps along the path curve. Default:0.0
    
      - scale : sc                     (float)         [create,query,edit]
          Amount to scale the profile curve as it sweeps along the path curve. Default:1.0
    
      - subCurveSubSurface : scs       (bool)          [create,query,edit]
          If true, curve range on the path will get applied to the resulting surface instead of cut before the extrude.
          Default:false
    
      - useComponentPivot : ucp        (int)           [create,query,edit]
          Use closest endpoint of the path - 0, component pivot - 1 or the center of the bounding box of the profile - 2 Default:0
    
      - useProfileNormal : upn         (bool)          [create,query,edit]
          If true, use the profile curve normal for the direction in which to extrude. Use only for distance or tube extrudeType.
          Default:false                  Common flags
    
    
    Derived from mel command `maya.cmds.extrude`
    """

    pass


def bezierAnchorState(*args, **kwargs):
    """
    The bezierAnchorState command provides an easy interface to modify anchor states: - Smooth/Broken anchor tangents -
    Even/Uneven weighted anchor tangents
    
    Flags:
      - even : ev                      (bool)          [create]
          Sets selected anchors (or attached tangent handles) to even weighting when true, uneven otherwise.
    
      - smooth : sm                    (bool)          [create]
          Sets selected anchors (or attached tangent handles) to smooth when true, broken otherwise.                  Flag can
          have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.bezierAnchorState`
    """

    pass


def polyGeoSampler(*args, **kwargs):
    """
    This command performs a render sampling of surface color and transparency for each selected vertex or face and stores
    the sampled data as either the color value, or uses the sampled data to displace the affected vertices or faces by a
    sampled data value. Transparency is not used for displacement, and displacement is performed along vertex normals. The
    sampled data value used can be pre-scaled by a user defined amount. Additionally, the normals chosen for sampling can be
    overridden using a flatshading option. This option basically means to always use the normals of the faces when computing
    sampling values. This may be a desired if the user wishes to override an edge smoothness factor. Basically with the
    flatshading option on, edges are always considered to be hard. Note that displacement sampling will result in the
    -sampleByFace option to be turned off, since a displacement of a vertex always affects the faces the vertex is connected
    to. Finally, it is possible to force the storage of shared colors per vertex, and / or force the usage of unshared UV
    values. The computation of the resulting color is as follows: resulting-RGB = (sampled-RGB \* scale-factor);         if
    (color blend is none)                 resulting-RGB = geometry-RGB         else if (color blend is add)
    resulting-RGB = geometry-RGB + sampled-RGB;         else if (color blend is subtract)                 resulting-RGB =
    geometry-RGB - sampled-RGB;         else if (color blend is multiply)                 resulting-RGB = geometry-RGB \*
    sampled-RGB;         else if (color blend is divide)                 resulting-RGB = geometry-RGB / sampled-RGB;
    else if (color blend is average)                 resulting-RGB = (geometry-RGB \* 1/2) + (sampled-RGB \* 1/2);
    if (clamp option set)                 clamp resulting-RGB between minimum-RGB and maximum-RGB, The analogous computation
    is done for computing the resulting alpha value. The command requires that there be a camera selected in your scene in
    order to work properly in -batch or -prompt mode.
    
    Flags:
      - alphaBlend : abl               (unicode)       [create,edit]
          When specified, indicates the type of alpha blend to be applied. Options are: none, overwrite, add, subtract, multiply,
          divide, average. This option only applies when colors are being set. The default if this argument is not specified is
          overwrite. The noneoptions to not overwrite the existing value.
    
      - averageColor : ac              (bool)          [create,edit]
          When used, will mean to force the storage of shared colors for vertex level sampling. By default vertex level sampling
          stores unshared colors.
    
      - clampAlphaMax : amx            (float)         [create,edit]
          When used, will mean to clamp the storage of alpha to a maximum
    
      - clampAlphaMin : amn            (float)         [create,edit]
          When used, will mean to clamp the storage of alpha to a minimum
    
      - clampRGBMax : cmx              (float, float, float) [create,edit]
          When used, will mean to clamp the storage of RGB color to a maximum
    
      - clampRGBMin : cmn              (float, float, float) [create,edit]
          When used, will mean to clamp the storage of RGB color to a minimum
    
      - colorBlend : cbl               (unicode)       [create,edit]
          When specified, indicates the type of color blend to be applied. Options are: none, overwrite, add, subtract, multiply,
          divide, average. This option only applies when colors are being set. The default if this argument is not specified is
          overwrite. The noneoptions to not overwrite the existing value.
    
      - colorDisplayOption : cdo       (bool)          [create,edit]
          Change the display options on the mesh to display the vertex colors.
    
      - computeShadows : cs            (bool)          [create,edit]
          When used, shadow maps will be computed, saved, and reused during the sampling process.
    
      - displaceGeometry : dg          (bool)          [create,edit]
          When used, geometry will be displaced along the normals at the sampling positions, as opposed to storing color values.
          The default is to store colors.
    
      - flatShading : fs               (bool)          [create,edit]
          When used, flat shaded sampling will be computed. The default is smooth shading.
    
      - ignoreDoubleSided : ids        (bool)          [create,edit]
          When specified, the double sided flag will be ignored for prelighting.
    
      - lightingOnly : lo              (bool)          [create,edit]
          When used, incoming illumination will be computed as opposed to surface color an tranparency
    
      - reuseShadows : rs              (bool)          [create,edit]
          When used, if shadow maps were previosly computed and saved, then they will be reused during the sampling process. The
          computeShadows option must be enabled for this option to apply.
    
      - sampleByFace : bf              (bool)          [create,edit]
          When used, sample will occur at a per face level versus a per vertex level, which is the default behaviour
    
      - scaleFactor : sf               (float)         [create,edit]
          When used, will scale the sampled value by the specified amount. The default scale factor is 1.0. Negative values are
          acceptable for displacement, but not for color values.
    
      - shareUV : su                   (bool)          [create,edit]
          When used, UVs are shared at a vertex when sampled. By default UVs are forced to be unshared.
    
      - useLightShadows : ul           (bool)          [create,edit]
          When used, will use each lights shadow map options. Otherwise these options will be overrridden when the computeShadows,
          and/or reusedShadows option is enabled.                                   Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyGeoSampler`
    """

    pass


def makeSingleSurface(*args, **kwargs):
    """
    This command performs a stitch and tessellate operation.
    
    Flags:
      - caching : cch                  (bool)          []
    
      - chordHeight : cht              (float)         [query,edit]
          Chord height is the absolute distance in OBJECT space which the center of a polygon edge can deviate from the actual
          center of the surface span. Only used if Format is General and if useChordHeight is true. Default:0.1
    
      - chordHeightRatio : chr         (float)         [query,edit]
          Chord height ratio is the ratio of the chord length of a surface span to the chord height.  (This is a length to height
          ratio). 0 is a very loose fit. 1 is a very tight fit. (See also description of chord height.) Always used if Format is
          Standard Fit.  Otherwise, only used if Format is General and useChordHeightRatio is true. Default:0.9
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - delta : d                      (float)         [query,edit]
          3D delta. Only used if Format is Standard Fit. Default:0.1
    
      - edgeSwap : es                  (bool)          [query,edit]
          Edge swap.  This attribute enables an algorithm which determines the optimal method with which to tessellate a
          quadrilateral into triangles. Only used if Format is General. Default:false
    
      - format : f                     (int)           [query,edit]
          Format: 0 - Triangle Count, 1 - Standard Fit, 2 - General, 3 - CVs Default:1
    
      - fractionalTolerance : ft       (float)         [query,edit]
          Fractional tolerance. Only used if Format is Standard Fit. Default:0.01
    
      - frozen : fzn                   (bool)          []
    
      - matchNormalDir : mnd           (bool)          [query,edit]
          Only used when the format is CVs.  Order the cvs so that the normal matches the direction of the original surface if set
          to true. Default:false
    
      - minEdgeLength : mel            (float)         [query,edit]
          Minimal edge length. Only used if Format is Standard Fit. Default:0.001
    
      - name : n                       (unicode)       [create]
          Name the resulting object.
    
      - nodeState : nds                (int)           []
    
      - normalizeTrimmedUVRange : ntr  (bool)          [query,edit]
          This attribute is only applicable when a trimmed NURBS surface is used as the input surface. When true, the UV texture
          coordinates on the trimmed input surface are normalized and applied to the output surface as they are for the untrimmed
          version of the input surface. (The texture coordinates on the entire untrimmed surface are mapped to the entire output
          surface.) When false, the UV texture coordinates on the trimmed input surface are applied to the output surface as they
          are for the trimmed input surface.  (Only the texture coordinates visible on the trimmed input surface are mapped to the
          output surface.) Default:true
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - polygonCount : pc              (int)           [query,edit]
          The number of polygons to produce. Only used if Format is Triangle Count. Default:200
    
      - polygonType : pt               (int)           [query,edit]
          Polygon type: 0 - Triangles, 1 - Quads Default:0
    
      - stitchTolerance : st           (float)         [edit]
          Stitch tolerance. Default:0.1
    
      - uNumber : un                   (int)           [query,edit]
          Initial number of isoparms in U.  Used in conjunction with the uType attribute. Only used if Format is General.
          Default:3
    
      - uType : ut                     (int)           [query,edit]
          Initial U type tessellation criteria (3 types). Type 0 - Per surface # of isoparms in 3D.  This type places a specific
          number of iso-parametric subdivision lines across the surface, equally spaced in 3D space. Type 1 - Per surface # of
          isoparms.  This type places a specific number of iso-parametric subdivision lines across the surface, equally spaced in
          parameter space. Type 2 - Per span # of isoparms.  This type places a specific number of iso-parametric subdivision
          lines across each surface span, equally spaced in parameter space. (This is the closest option to the Alias Studio
          tessellation parameters.) This attribute is only used if Format is General. Default:3
    
      - useChordHeight : uch           (bool)          [query,edit]
          True means use chord height. Only used if Format is General. Default:false
    
      - useChordHeightRatio : ucr      (bool)          [query,edit]
          True means use chord height ratio. Default:true
    
      - vNumber : vn                   (int)           [query,edit]
          Initial number of isoparms in V.  Used in conjunction with the vType attribute. Only used if Format is General.
          Default:3
    
      - vType : vt                     (int)           [query,edit]
          Initial V type tessellation criteria (3 types). See description for the uType attribute. Only used if Format is General.
          Default:3                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.makeSingleSurface`
    """

    pass


def polyDelFacet(*args, **kwargs):
    """
    Deletes faces. If the result is split into disconnected pieces, the pieces (so-called shells) are still considered to be
    one object. Notice : The last face cannot be deleted.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyDelFacet`
    """

    pass


def subdToPoly(*args, **kwargs):
    """
    This command tessellates a subdivision surface and produces polygon. The name of the new polygon is returned. If
    construction history is ON, then the name of the new dependency node is returned as well.
    
    Flags:
      - addUnderTransform : aut        (bool)          [create,query]
          If true then add the result underneath a transform node
    
      - applyMatrixToResult : amr      (bool)          [create,query,edit]
          If true, the matrix on the input geometry is applied to the object and the resulting geometry will have identity matrix
          on it.  If false the conversion is done on the local space object and the resulting geometry has the input object's
          matrix on it. Default:true
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - connectShaders : cs            (bool)          [create]
          If true, all shader assignment will be copied from the original subdiv surface to the converted polygonal surface.
          Default:true
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off (where applicable).
    
      - copyUVTopology : cut           (bool)          [create,query,edit]
          Copy over uv topology (shared/unshared) from the original subdivision surface to the converted polygonal mesh.
          Default:false
    
      - depth : d                      (int)           [create,query,edit]
          The depth at which constant-depth tessellates the surface Default:0
    
      - extractPointPosition : epp     (bool)          [create,query,edit]
          Determines how the position of a mesh point is calculated If on the position of the mesh point is returned. If off the
          position of the point of the surface is returned. Default:false
    
      - format : f                     (int)           [create,query,edit]
          Format: 0 - Uniform1 - Adaptive2 - Polygon Count3 - VerticesDefault:0
    
      - frozen : fzn                   (bool)          []
    
      - inSubdCVId : inSubdCVId        (int, int)      [create,query,edit]
          Input CV Id
    
      - inSubdCVIdLeft : isl           (int)           [create,query,edit]
          Higher 32 bit integer of the input CV Id
    
      - inSubdCVIdRight : isr          (int)           [create,query,edit]
          Lower 32 bit integer of the input CV Id
    
      - maxPolys : mp                  (int)           [create,query,edit]
          The maximum number of polygons at which by polygons tessellates. If this attribute is greater than zero, it will
          override the sample count and depth attributes. Default:0
    
      - name : n                       (unicode)       [create]
          Name the resulting object.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the depend node (where applicable).                  Advanced flags
    
      - outSubdCVId : os               (int, int)      [create,query,edit]
          Output CV Id
    
      - outSubdCVIdLeft : osl          (int)           [create,query,edit]
          Higher 32 bit integer of the output CV Id
    
      - outSubdCVIdRight : osr         (int)           [create,query,edit]
          Lower 32 bit integer of the output CV Id
    
      - outv : ov                      (int)           [create,query,edit]
          Out Vertices corresponding to the inSubDCVs.
    
      - preserveVertexOrdering : pvo   (bool)          [create,query,edit]
          Preserve vertex ordering in conversion Default:true
    
      - sampleCount : sc               (int)           [create,query,edit]
          The number of samples per face Default:1
    
      - shareUVs : suv                 (bool)          [create,query,edit]
          Force sharing of uvs on all common vertices - the value of this attribute gets overridden by the value of the
          copyUVTopology attribute. Default:false
    
      - subdNormals : un               (bool)          [create,query,edit]
          Keep subdiv surface normals Default:false                  Common flags
    
    
    Derived from mel command `maya.cmds.subdToPoly`
    """

    pass


def attachSurface(*args, **kwargs):
    """
    This attach command is used to attach surfaces. Once the surfaces are attached, there will be multiple knots at the
    joined point(s). These can be kept or removed if the user wishes. The end of the first surface is attached to the start
    of the second surface in the specified direction. Note: if the command is done with Keep Original off there will be an
    extra surface in the model (the second surface). The command does not delete it. The first surface is replaced by the
    attached surface.
    
    Flags:
      - blendBias : bb                 (float)         [create,query,edit]
          Skew the result toward the first or the second curve depending on the blend factory being smaller or larger than 0.5.
          Default:0.5
    
      - blendKnotInsertion : bki       (bool)          [create,query,edit]
          If set to true, insert a knot in one of the original curves (relative position given by the parameter attribute below)
          in order to produce a slightly different effect. Default:false
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - directionU : du                (bool)          [create,query,edit]
          If true attach in U direction of surface and V direction otherwise. Default:true
    
      - frozen : fzn                   (bool)          []
    
      - keepMultipleKnots : kmk        (bool)          [create,query,edit]
          If true, keep multiple knots at the join parameter. Otherwise remove them. Default:true
    
      - method : m                     (int)           [create,query,edit]
          Attach method (connect-0, blend-1) Default:0
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - parameter : p                  (float)         [create,query,edit]
          The parameter value for the positioning of the newly inserted knot. Default:0.1
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - reverse1 : rv1                 (bool)          [create,query,edit]
          If true, reverse the direction (specified by directionU) of the first input surface before doing attach. Otherwise, do
          nothing to the first input surface before attaching. NOTE: setting this attribute to random values will cause
          unpredictable results and is not supported. Default:false
    
      - reverse2 : rv2                 (bool)          [create,query,edit]
          If true, reverse the direction (specified by directionU) of the second input surface before doing attach. Otherwise, do
          nothing to the second input surface before attaching. NOTE: setting this attribute to random values will cause
          unpredictable results and is not supported. Default:false
    
      - swap1 : sw1                    (bool)          [create,query,edit]
          If true, swap the UV directions of the first input surface before doing attach. Otherwise, do nothing to the first input
          surface before attaching. NOTE: setting this attribute to random values will cause unpredictable results and is not
          supported. Default:false
    
      - swap2 : sw2                    (bool)          [create,query,edit]
          If true, swap the UV directions of the second input surface before doing attach. Otherwise, do nothing to the second
          input surface before attaching. NOTE: setting this attribute to random values will cause unpredictable results and is
          not supported. Default:false
    
      - twist : tw                     (bool)          [create,query,edit]
          If true, reverse the second surface in the opposite direction (specified by directionU) before doing attach. This will
          avoid twists in the attached surfaces. Otherwise, do nothing to the second input surface before attaching. NOTE: setting
          this attribute to random values will cause unpredictable results and is not supported. Default:false
          Common flags
    
    
    Derived from mel command `maya.cmds.attachSurface`
    """

    pass


def polyPoke(*args, **kwargs):
    """
    Introduces a new vertex in the middle of the selected face, and connects it to the rest of the vertices of the face.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - localTranslate : lt            (float, float, float) [create]
          Translate the new vertex in the local face coordinate.
    
      - localTranslateX : ltx          (float)         [create]
          Translate the new vertex in the local face coordinate along X.
    
      - localTranslateY : lty          (float)         [create]
          Translate the new vertex in the local face coordinate along Y.
    
      - localTranslateZ : ltz          (float)         [create]
          Translate the new vertex in the local face coordinate along Z.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - translate : t                  (float, float, float) [create]
          Translate the new vertex in the world space.
    
      - translateX : tx                (float)         [create]
          Translate the new vertex in the world space along X.
    
      - translateY : ty                (float)         [create]
          Translate the new vertex in the world space along Y.
    
      - translateZ : tz                (float)         [create]
          Translate the new vertex in the world space along Z.
    
      - worldSpace : ws                (bool)          [create]
          This flag specifies if the operation has to be performed in the world space or not.                  Common flags
    
    
    Derived from mel command `maya.cmds.polyPoke`
    """

    pass


def uvSnapshot(*args, **kwargs):
    """
    Builds an image containg the UVs of the selected objects.
    
    Flags:
      - antiAliased : aa               (bool)          [create]
          When this flag is set, lines are antialiased.
    
      - blueColor : b                  (int)           [create]
          Blue component of line drawing. Default is 255.
    
      - entireUVRange : euv            (bool)          [create]
          When this flag is set, the generated image will contain the entire uv range. Default is UV in 0-1 range.
    
      - fileFormat : ff                (unicode)       [create]
          Output file format. Any of those keyword:                                 iff, sgi, pic, tif, als, gif, rla, jpgDefault
          is iff.
    
      - greenColor : g                 (int)           [create]
          Green component of line drawing. Default is 255.
    
      - name : n                       (unicode)       [create]
          Name of the file to be created.
    
      - overwrite : o                  (bool)          [create]
          When this flag is set, existing file can be ovewritten.
    
      - redColor : r                   (int)           [create]
          Red component of line drawing. Default is 255.
    
      - uMax : umx                     (float)         [create]
          Optional User Specified Max value for U. Default value is 1. This will take precedence over the entire range-euv flag.
    
      - uMin : umn                     (float)         [create]
          Optional User Specified Min value for U. Default value is 0. This will take precedence over the entire range-euv flag.
    
      - uvSetName : uvs                (unicode)       [create]
          Name of the uv set to use. Default is the current one.
    
      - vMax : vmx                     (float)         [create]
          Optional User Specified Max value for V. Default value is 1. This will take precedence over the entire range-euv flag.
    
      - vMin : vmn                     (float)         [create]
          Optional User Specified Min value for V. Default value is 0. This will take precedence over the entire range-euv flag.
    
      - xResolution : xr               (int)           [create]
          Horizontal size of the image. Default is 512.
    
      - yResolution : yr               (int)           [create]
          Vertical size of the image. Default is 512.                                Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.uvSnapshot`
    """

    pass


def polyCut(*args, **kwargs):
    """
    This command splits a mesh, or a set of poly faces, along a plane. The position and orientation of the plane can be
    adjusted using the appropriate flags listed above.  In addition, the cut operation can also delete the faces lying on
    one side of the cutting plane, or extract those faces by an offset amount.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - cutPlaneCenter : pc            (float, float, float) [create]
          This flag specifies the position of the cutting plane.
    
      - cutPlaneCenterX : pcx          (float)         [create]
          This flag specifies the X position of the cutting plane.
    
      - cutPlaneCenterY : pcy          (float)         [create]
          This flag specifies the Y position of the cutting plane.
    
      - cutPlaneCenterZ : pcz          (float)         [create]
          This flag specifies the Z position of the cutting plane.
    
      - cutPlaneHeight : ph            (float)         [create]
          This flag specifies the height of the cutting plane. This is used only for displaying the manipulator, and has no effect
          on the cut operation.
    
      - cutPlaneRotate : ro            (float, float, float) [create]
          This flag specifies the orientation of the cutting plane.
    
      - cutPlaneRotateX : rx           (float)         [create]
          This flag specifies the X rotation of the cutting plane.
    
      - cutPlaneRotateY : ry           (float)         [create]
          This flag specifies the Y rotation of the cutting plane.
    
      - cutPlaneRotateZ : rz           (float)         [create]
          This flag specifies the Z rotation of the cutting plane.
    
      - cutPlaneSize : ps              (float, float)  [create]
          This flag specifies the size of the cutting plane. This is used only for displaying the manipulator, and has no effect
          on the cut operation.
    
      - cutPlaneWidth : pw             (float)         [create]
          This flag specifies the width of the cutting plane. This is used only for displaying the manipulator, and has no effect
          on the cut operation.
    
      - cuttingDirection : cd          (unicode)       [create]
          This flag specifies the direction of the cutting plane. Valid values are x, y, zA value of xwill cut the object along
          the YZ plane cutting through the center of the bounding box. A value of ywill cut the object along the ZX plane cutting
          through the center of the bounding box. A value of zwill cut the object along the XY plane cutting through the center of
          the bounding box.
    
      - deleteFaces : df               (bool)          [create]
          This flag specifies if the cut faces should be deleted or not.
    
      - extractFaces : ef              (bool)          [create]
          This flag specifies if the cut faces should be extracted or not.
    
      - extractOffset : eo             (float, float, float) [create]
          This flag specifies the offset by which the cut faces will be extracted.  This flag has no effect when the
          extractFacesis turned off.
    
      - extractOffsetX : eox           (float)         [create]
          This flag specifies the offset in X by which the cut faces will be extracted.  This flag has no effect when the
          extractFacesis turned off.
    
      - extractOffsetY : eoy           (float)         [create]
          This flag specifies the offset in Y by which the cut faces will be extracted.  This flag has no effect when the
          extractFacesis turned off.
    
      - extractOffsetZ : eoz           (float)         [create]
          This flag specifies the offset in Z by which the cut faces will be extracted.  This flag has no effect when the
          extractFacesis turned off.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - onObject : oo                  (bool)          []
    
      - worldSpace : ws                (bool)          [create]
          This flag is ignored.  polyCut command always works on worldSpace.                  Common flags
    
    
    Derived from mel command `maya.cmds.polyCut`
    """

    pass


def arcLengthDimension(*args, **kwargs):
    """
    This command is used to create an arcLength dimension to display the arcLength of a curve/surface at a specified point
    on the curve/surface.
    
    
    Derived from mel command `maya.cmds.arcLengthDimension`
    """

    pass


def polyMergeFacet(*args, **kwargs):
    """
    The second face becomes a hole in the first face.The new holed face is located either on the first, last, or between
    both selected faces, depending on the mode. Both faces must belong to the same object.Facet flags are mandatory.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - firstFacet : ff                (int)           [create,query,edit]
          The number of the first (outer) face to merge.
    
      - frozen : fzn                   (bool)          []
    
      - mergeMode : mm                 (int)           [create,query,edit]
          This flag specifies how faces are merged: 0: moves second face to first one 1: moves both faces to average 2: moves
          first face to second one 3, 4, 5: same as above, except faces are projected but not centred 6: Nothing moves. C: Default
          is None (6).
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - secondFacet : sf               (int)           [create,query,edit]
          The number of the second (hole) face to merge.                  Common flags
    
    
    Derived from mel command `maya.cmds.polyMergeFacet`
    """

    pass


def tolerance(*args, **kwargs):
    """
    This command sets tolerances used by modelling operations that require a tolerance, such as surface fillet. Linear
    tolerance is also known as positionaltolerance. Angular tolerance is also known as tangentialtolerance. In query mode,
    return type is based on queried flag.
    
    Flags:
      - angular : a                    (float)         [create,query]
          Sets the angular, or tangentialtolerance.
    
      - linear : l                     (float)         [create,query]
          Sets the linear, or positonaltolerance.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.tolerance`
    """

    pass


def plane(*args, **kwargs):
    """
    The command creates a sketch plane (also known as a construction plane) in space.  To create an object (such as a NURBS
    curve, joint chain or polygon) on a construction plane, you need to first make the plane live. See also the makeLive
    command.
    
    Flags:
      - length : l                     (float)         [create]
          The length of plane. linearmeans that this flag can handle values with units.
    
      - name : n                       (unicode)       [create]
          Name the resulting object.
    
      - position : p                   (float, float, float) [create]
          3D position where the centre of the plane is positioned. linearmeans that this flag can handle values with units.
    
      - rotation : r                   (float, float, float) [create]
          The rotation of plane. anglemeans that this flag can handle values with units.
    
      - size : s                       (float)         [create]
          The combined size (size x size) of plane. linearmeans that this flag can handle values with units.
    
      - width : w                      (float)         [create]
          The width of plane. linearmeans that this flag can handle values with units.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.plane`
    """

    pass


def polyReduce(*args, **kwargs):
    """
    Simplify a polygonal object by reducing geometry while preserving the overall shape of the mesh. The algorithm for
    polyReduce was changed in 2014 to use a new algorithm derived from Softimage. However, the command still defaults to
    using the old algorithm for backwards compatibility.  Therefore, we recommend setting the version flag to 1 for best
    results as the new algorithm is better at preserving geometry features.  Additionally, some flags only apply to a
    specific algorithm and this is documented for each flag.
    
    Flags:
      - border : b                     (float)         []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - cachingReduce : cr             (bool)          [create,query,edit]
          Cache intermediate reductions for speed at the expense of memory. It is recommended that caching be enabled when using
          the new algorithm. (-version 1)  However, caching is not recommended when using then old algorithm because it can cause
          stability issues. C: Default is false. Q: When queried, this flag returns a boolean.
    
      - colorWeights : cwt             (float)         [create,query,edit]
          This flag only applies when using the old algorithm and is provided for backwards compatibility. How much consideration
          vertex color is given in the reduction algorithm. A higher weight means the reduction will try harder to preserve vertex
          coloring. C: Default is 0. Q: When queried, this flag returns a float.
    
      - compactness : com              (float)         [create,query,edit]
          This flag only applies when using the old algorithm and is provided for backwards compatibility. Tolerance for
          compactness for the generated triangles A value of 0 will accept all triangles during decimation A value close to 0 will
          attempt to eliminate triangles that have collinear edges (zero area triangles) A value closer to 1 will attempt to
          eliminate triangles that are not strictly equilateral (of equal lengths) The closer to 1.0, the more expensive the
          computation Q: When queried, this flag returns a float.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - detail : d                     (float)         []
    
      - frozen : fzn                   (bool)          []
    
      - geomWeights : gwt              (float)         [create,query,edit]
          This flag only applies when using the old algorithm and is provided for backwards compatibility. How much consideration
          vertex positions are given in the reduction algorithm.  A higher weight means the reduction will try harder to preserve
          geometry. C: Default is 1. Q: When queried, this flag returns a float.
    
      - invertVertexWeights : iwt      (bool)          [create,query,edit]
          This flag controls how weight map values are interpreted. If true, a vertex weight of 1.0 means a vertex is unlikely to
          be reduced. If false, a vertex weight of 0.0 means a vertex is unlikely to be reduced. This flag only applies when using
          the new algorithm. (-version 1) C: Default is true. Q: When queried, this flag returns a boolean.
    
      - keepBorder : kb                (bool)          [create,query,edit]
          If true, reduction will try to retain geometric borders and the border of the selection. C: Default is true. Q: When
          queried, this flag returns a boolean.
    
      - keepBorderWeight : kbw         (float)         [create,query,edit]
          If keepBorder is on, this flag specifies the weight to assign to borders.  Setting this value to 0 will disable border
          preservation and a value of 1 will exactly preserve all border vertices which is useful for matching adjacent meshes.
          This flag only applies when using the new algorithm. (-version 1) C: Default is 0.5. Q: When queried, this flag returns
          a float.
    
      - keepColorBorder : kcb          (bool)          [create,query,edit]
          If true, reduction will try to retain color borders.  These are determined according to color Ids.  This flag only
          applies when using the new algorithm. (-version 1) C: Default is true. Q: When queried, this flag returns a boolean.
    
      - keepColorBorderWeight : kcw    (float)         [create,query,edit]
          If keepColorBorder is on, this flag specifies the weight to assign to color borders.  Setting this value to 0 will
          disable color border preservation and a value of 1 will exactly preserve all color borders.  This flag only applies when
          using the new algorithm. (-version 1) C: Default is 0.5. Q: When queried, this flag returns a float.
    
      - keepCreaseEdge : kce           (bool)          [create,query,edit]
          If true, reduction will try to retain crease edges. C: Default is true.  This flag only applies when using the new
          algorithm. (-version 1) C: Default is true. Q: When queried, this flag returns a boolean.
    
      - keepCreaseEdgeWeight : cew     (float)         [create,query,edit]
          If keepCreaseEdge is on, this flag specifies the weight to assign to crease edges.  Setting this value to 0 will disable
          crease edge preservation and a value of 1 will exactly preserve all crease edges. This flag only applies when using the
          new algorithm. (-version 1) C: Default is 0.5. Q: When queried, this flag returns a float.
    
      - keepFaceGroupBorder : kfb      (bool)          [create,query,edit]
          If true, reduction will try to retain borders of face groups, which are mostly used to define material assignments.
          This flag only applies when using the new algorithm. (-version 1) C: Default is true. Q: When queried, this flag returns
          a boolean.
    
      - keepFaceGroupBorderWeight : kfw (float)         [create,query,edit]
          If keepFaceGroupBorder is on, this flag specifies the weight to assign to material borders.  Setting this value to 0
          will disable group border preservation and a value of 1 will exactly preserve all group borders.  This flag only applies
          when using the new algorithm. (-version 1) C: Default is 0.5. Q: When queried, this flag returns a float.
    
      - keepHardEdge : khe             (bool)          [create,query,edit]
          If true, reduction will try to retain hard edges. C: Default is true. Q: When queried, this flag returns a boolean.
    
      - keepHardEdgeWeight : khw       (float)         [create,query,edit]
          If keepHardEdge is on, this flag specifies the weight to assign to hard edges.  Setting this value to 0 will disable
          hard edge preservation and a value of 1 will exactly preserve all hard edges. This flag only applies when using the new
          algorithm. (-version 1) C: Default is 0.5. Q: When queried, this flag returns a float.
    
      - keepMapBorder : kmb            (bool)          [create,query,edit]
          If true, reduction will try to retain UV borders.  A UV border is present if the faces on either side of the edge do not
          share UV Ids. C: Default is true. Q: When queried, this flag returns a boolean.
    
      - keepMapBorderWeight : kmw      (float)         [create,query,edit]
          If keepMapBorder is on, this flag specifies the weight to assign to UV map borders.  Setting this value to 0 will
          disable UV map border preservation and a value of 1 will exactly preserve all UV borders. This flag only applies when
          using the new algorithm. (-version 1) C: Default is 0.5. Q: When queried, this flag returns a float.
    
      - keepOriginalVertices : kev     (bool)          [create,query,edit]
          This flag only applies when using the old algorithm and is provided for backwards compatibility. If true, vertices will
          try to retain their original positions and will not be repositioned for optimal shape. NOTE: In the newer algorithm
          vertices always retain their exact original positions. (though the Ids will change) C: Default is false. Q: When
          queried, this flag returns a boolean.
    
      - keepQuadsWeight : kqw          (float)         [create,query,edit]
          This flag controls how much consideration is given to oreserving quad faces during reduction.  A higher weight means the
          reduction will try harder to keep quad faces and avoid creation of triangles. If the version flag is set to 1 (-version
          1) and the keepQuadsWeight flag is set to 1.0 then a special quad reduction algorithm is used that does a better job of
          preserving quads. Howver, this special quad reduction algorithm does not support symmetry so those flags will be ignored
          when the keepQuadsWeight flag is set to 1.0. C: Default is 0. Q: When queried, this flag returns a float.
    
      - line : l                       (float)         []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - percentage : p                 (float)         [create,query,edit]
          This flag specifies how many vertices to remove during reduction as a percentage of the original mesh.  This flag only
          applies if the termination flag is set to 0 or when using the old algorithm. C: Default is 0. 100 will remove every
          possible vertex, 0 will remove none. Q: When queried, this flag returns a float.
    
      - preserveLocation : pl          (bool)          [create]
          This flag guarantees that if the original geometry is preserved, the new geometry will have the same location. C:
          Default is false.
    
      - preserveTopology : top         (bool)          [create,query,edit]
          this flag guarantees that the topological type will be preserved during reduction.  In particular, if the input is
          manifold then the output will be manifold.  This option also prevents holes in the mesh from being closed off. This flag
          only applies when using the new algorithm. (-version 1) C: Default is true. Q: When queried, this flag returns a
          boolean.
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace) (not available in all commands). NOTE: This flag is intended for use by the Reducemenu
          item. If 'polyReduce -rpo 0' is executed from the command line, Shader information will not be copied from the original
          mesh to the result.
    
      - sharpness : shp                (float)         [create,query,edit]
          Sharpness controls the balance between preserving small, sharp details versus larger shapes.  At low values, details
          that are small relative to the general shape of the object are more likely to be collapsed.  At high values, they are
          more likely to be kept.  This flag only applies when using the new algorithm. (-version 1) C: Default is 0. Q: When
          queried, this flag returns a float.
    
      - symmetryPlane : sym            (float, float, float, float) []
    
      - symmetryPlaneW : sw            (float)         [create,query,edit]
          W value of the symmetry plane.  This flag only applies when using the new algorithm (-version 1) and the
          useVirtualSymmetry flag is set to 2. C: Default is 0. Q: When queried, this flag returns a float.
    
      - symmetryPlaneX : sx            (float)         [create,query,edit]
          X value of the symmetry plane.  This flag only applies when using the new algorithm (-version 1) and the
          useVirtualSymmetry flag is set to 2. C: Default is 0. Q: When queried, this flag returns a float.
    
      - symmetryPlaneY : sy            (float)         [create,query,edit]
          Y value of the symmetry plane.  This flag only applies when using the new algorithm (-version 1) and the
          useVirtualSymmetry flag is set to 2. C: Default is 0. Q: When queried, this flag returns a float.
    
      - symmetryPlaneZ : sz            (float)         [create,query,edit]
          Z value of the symmetry plane.  This flag only applies when using the new algorithm (-version 1) and the
          useVirtualSymmetry flag is set to 2. C: Default is 0. Q: When queried, this flag returns a float.
    
      - symmetryTolerance : stl        (float)         [create,query,edit]
          Tolerance to use when applying symmetry. For each vertex of the mesh, we find its exact symmetric point, then we look
          for the closest vertex to the exact symmetry up to the tolerance distance.  Higher values risk finding more spurious
          symmetries, lower values might miss symmetries. The value is distance in object space.  This flag only applies when
          using the new algorithm (-version 1) and the useVirtualSymmetry flag is not set to 0. C: Default is 0. Q: When queried,
          this flag returns a float.
    
      - termination : trm              (int)           [create,query,edit]
          This flag specifies the termination condition to use when reducing the mesh.  This flag only applies to the new
          algorithm. (-version 1) 0 Percentage 1 Vertex count 2 Triangle count C: Default is 0. Q: When queried, this flag returns
          an integer.
    
      - triangleCount : tct            (int)           [create,query,edit]
          This flag specifies a target number of triangles to retain after reduction. Note that other factors such as quad and
          feature preservation may take precendence and cause the actual number of triangles to be different. This flag only
          applies when using the new algorithm (-version 1) and the termination flag is set to 2. C: Default is 0. Q: When
          queried, this flag returns an integer.
    
      - triangulate : t                (bool)          [create,query,edit]
          This flag only applies when using the old algorithm and is provided for backwards compatibility. This attribute
          specifies if the geometry or the selected faces has to be triangulated, before performing reduction. C: Default is true.
          Q: When queried, this flag returns a boolean.
    
      - useVirtualSymmetry : uvs       (int)           [create,query,edit]
          This flag controls whether symmetry is preserved during the reduction. This flag only applies when using the new
          algorithm (-version 1) and the keepQuadsWeight flag is less than 1.0. 0 No symmetry preservation 1 Automatic. Try to
          find suitable symmetry during reduction. 2 Plane.  Specify a symmetry plane to use during reduction. C: Default is 0. Q:
          When queried, this flag returns an integer.
    
      - uvWeights : uwt                (float)         [create,query,edit]
          This flag only applies when using the old algorithm and is provided for backwards compatibility. How much consideration
          uv positions are given in the reduction algorithm. A higher weight means the reduction will try harder to preserve uv
          positions. C: Default is 0. Q: When queried, this flag returns a float.
    
      - version : ver                  (int)           [create,query,edit]
          Version of the poly reduce algorithm to use. 0 Old algorithm used in Maya 2013 and prior for backwards compatibility 1
          New algorithm derived from Softimage and used in Maya 2014 and later The default is 0 for backwards compatibility but
          for best results it is recommended that the new algorithm is used as it is better at preserving mesh details. Some flags
          only apply to a specific algorithm and this is documented for each flag. C: Default is 0 for backwards compatibility. Q:
          When queried, this flag returns an integer.
    
      - vertexCount : vct              (int)           [create,query,edit]
          This flag specifies a target number of vertices to retain after reduction. Note that other factors such as quad and
          feature preservation may take precendence and cause the actual number of vertices to be different. This flag only
          applies when using the new algorithm (-version 1) and the termination flag is set to 1. C: Default is 0. Q: When
          queried, this flag returns an integer.
    
      - vertexMapName : vmp            (unicode)       [create,query]
          Name of a color set to be added to the output mesh that stores a mapping from vertices in the output mesh to vertices in
          the input mesh.  The color set is RGB.  The original vertex Id that maps to an output vertex is of a vertex is 65536\*r
          + g where r and g are the red and green channel at a vertex. The blue channel is always zero.  Each vertex in the output
          mesh has a shared color. This flag only applies when using the new algorithm. (-version 1) Q: When queried, this flag
          returns a string.
    
      - vertexWeightCoefficient : vwc  (float)         [create,query,edit]
          This flag specifies a constant value to multiply to each weight map value. A value of zero turns off the weight map.
          This flag only applies when using the new algorithm. (-version 1) C: Default is 1. Q: When queried, this flag returns a
          float.
    
      - weightCoefficient : wc         (float)         [create,query,edit]
          This flag only applies when using the old algorithm and is provided for backwards compatibility. The weight of each
          vertex is multiplied with this coefficient when the reduction is performed.  This value does not have to be edited,
          normally.  It gives finer control over the weighted reduction. This attribute is replaced by vertexWeightCoefficient in
          the new algorithm when the version flag is set to 1. C: Default is 10000. Q: When queried, this flag returns a float.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyReduce`
    """

    pass


def planarSrf(*args, **kwargs):
    """
    This command computes a planar trimmed surface given planar boundary curves that form a closed region.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting surface: 1 - linear, 3 - cubic Default:3
    
      - frozen : fzn                   (bool)          []
    
      - keepOutside : ko               (bool)          [create,query,edit]
          If true, keep the regions outside the given curves. Default:false
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.                  Advanced flags
    
      - tolerance : tol                (float)         [create,query,edit]
          The distance tolerance for the cvs of the curves to be in the same plane. Default:0.01                  Common flags
    
    
    Derived from mel command `maya.cmds.planarSrf`
    """

    pass


def subdMatchTopology(*args, **kwargs):
    """
    Command matches topology across multiple subdiv surfaces - at all levels.
    
    Flags:
      - frontOfChain : foc             (bool)          [create]
          This command is used to specify that the new addTopology node should be placed ahead (upstream) of existing deformer and
          skin nodes in the shape's history (but not ahead of existing tweak nodes). The input to the addTopology node will be the
          upstream shape rather than the visible downstream shape, so the behavior of this flag is the most intuitive if the
          downstream deformers are in their reset (hasNoEffect) position when the new deformer is added.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.subdMatchTopology`
    """

    pass


def duplicateSurface(*args, **kwargs):
    """
    The duplicateSurface command takes a surface patch (face) and and returns the 3D surface. Connected patches are returned
    as a single surface.
    
    Flags:
      - caching : cch                  (bool)          []
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off (where applicable).
    
      - faceCountU : fcu               (int)           []
    
      - faceCountV : fcv               (int)           []
    
      - firstFaceU : ffu               (int)           []
    
      - firstFaceV : ffv               (int)           []
    
      - frozen : fzn                   (bool)          []
    
      - local : l                      (bool)          [create]
          Copy the transform of the surface and connect to the local space version instead.
    
      - mergeItems : mi                (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           []
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node (where applicable).                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.duplicateSurface`
    """

    pass


def bevel(*args, **kwargs):
    """
    The bevel command creates a new bevel surface for the specified curve. The curve can be any nurbs curves.
    
    Flags:
      - bevelShapeType : bst           (int)           [create,query,edit]
          Shape type: 1 - straight cut, 2 - curve out, 3 - curve in Default:1
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - cornerType : ct                (int)           [create,query,edit]
          Corner type: 1 - linear, 2 - circular Default:2
    
      - depth : d                      (float)         [create,query,edit]
          The depth for bevel Default:0.5
    
      - extrudeDepth : ed              (float)         [create,query,edit]
          The extrude depth for bevel Default:1.0
    
      - frozen : fzn                   (bool)          []
    
      - joinSurfaces : js              (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - numberOfSides : ns             (int)           []
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.                  Advanced flags
    
      - tolerance : tol                (float)         [create,query,edit]
          The tolerance for bevel offsets Default:0.01
    
      - width : w                      (float)         [create,query,edit]
          The width for bevel Default:0.5                  Common flags
    
    
    Derived from mel command `maya.cmds.bevel`
    """

    pass


def reverseSurface(*args, **kwargs):
    """
    The reverseSurface command reverses one or both directions of a surface or can be used to swapthe U and V directions
    (this creates the effect of reversing the surface normal). The name of the newly reversed surface and the name of the
    resulting dependency node is returned. The resulting surface has the same parameter ranges as the original surface. This
    command also handles selected surface isoparms. For a selected isoparm, imagine that the isoparm curve is reversed after
    the operation. E.g. reverseSurface surface.v[0.1] will reverse in the U direction.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - direction : d                  (int)           [create,query,edit]
          The direction to reverse the surface in: 0 - U, 1 - V, 2 - Both U and V, 3 - Swap Default:0                  Common
          flags
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - noChanges : nc                 (bool)          []
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
    
    Derived from mel command `maya.cmds.reverseSurface`
    """

    pass


def polySubdivideEdge(*args, **kwargs):
    """
    Subdivides an edge into two or more subedges. Default : divide edge into two edges of equal length.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - divisions : dv                 (int)           [create,query,edit]
          The maximum number of vertices to be inserted in each edge. This number may be reduced if it creates edges shorter than
          the specified minimum length. C: Default is 1 (divide edges in half). Q: When queried, this flag returns an int.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - size : s                       (float)         [create,query,edit]
          The minimum length of each subedge created. If the given subdivision creates edges that are shorter than this length,
          the number of divisions is changed to respect min length. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polySubdivideEdge`
    """

    pass


def nurbsToSubdiv(*args, **kwargs):
    """
    This command converts a NURBS surface and produces a subd surface. The name of the new subdivision surface is returned.
    If construction history is ON, then the name of the new dependency node is returned as well.
    
    Flags:
      - addUnderTransform : aut        (bool)          []
    
      - caching : cch                  (bool)          []
    
      - collapsePoles : cp             (bool)          []
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off (where applicable).
    
      - frozen : fzn                   (bool)          []
    
      - matchPeriodic : mp             (bool)          []
    
      - maxPolyCount : mpc             (int)           []
    
      - name : n                       (unicode)       [create]
          Name the resulting object.
    
      - nodeState : nds                (int)           []
    
      - object : o                     (bool)          [create]
          Create the result, or just the depend node (where applicable).                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
      - reverseNormal : rn             (bool)          []
    
    
    Derived from mel command `maya.cmds.nurbsToSubdiv`
    """

    pass


def subdCleanTopology(*args, **kwargs):
    """
    Command cleans topology of subdiv surfaces - at all levels. It cleans the geometry of vertices that satisfy the
    following conditions:                 - Zero edits                 - Default uvs (uvs obtained by subdividing parent
    face).                 - No creases.
    
    
    Derived from mel command `maya.cmds.subdCleanTopology`
    """

    pass


def polyAppend(*args, **kwargs):
    """
    Appends a new face to the selected polygonal object. The first argument must be a border edge. The new face will be
    automatically closed. Only works with one object selected.
    
    Flags:
      - append : a                     (float, float, float) [create]
          Appends to the given polygon object.  The append flag should be used multiple times to specify the edges, points, and
          holes that make up the new face that is being added.  You may specify an edge by passing a single argument which will be
          the edges index.  A point is specified with three arguments which are the coordinates of the point in the objects local
          space.  Pass no arguments indicates that the values which follow shall specify a hole.  In Python, pass an empty tuple
          to specify no arguments.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - edge : ed                      (int)           [create]
          Adds the given edge of the selected object to the new face. This edge must be a border, which will be then shared by the
          new face and the neighboring one. The new face is oriented according to the orientation of the given edge(s).  Note that
          this flag should be avoided in Python.  You may use the appendflag instead and pass one argument.
    
      - hole : hl                      (bool)          [create]
          Add a hole. The following points and edges will define a hole.  Note that this flag should be avoided in Python.  You
          may use the appendflag instead and pass an empty tuple ().
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - point : p                      (float, float, float) [create]
          Adds a new point to the new face. Coordinates of free points are given in the local object reference.  Note that this
          flag should be avoided in Python.  You may use the appendflag instead and pass three arguments.
    
      - subdivision : s                (int)           [create,query,edit]
          This flag specifies the level of subdivisions. Automatically subdivides new edges into the given number of edges.
          Existing edges cannot be subdivided. C : Default is 1 (no subdivision). Q: When queried, this flag returns an int.
    
      - texture : tx                   (int)           [create,query,edit]
          Specifies how new faces are mapped. 0 - None; 1 - Normalize; 2 - Unitize C: Default is 0 (no mapping). Q: When queried,
          this flag returns an intCommon flags
    
    
    Derived from mel command `maya.cmds.polyAppend`
    """

    pass


def polyDuplicateEdge(*args, **kwargs):
    """
    Duplicates a series of connected edges (edgeLoop)
    
    Flags:
      - adjustEdgeFlow : aef           (float)         []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - deleteEdge : de                (bool)          []
    
      - endVertexOffset : evo          (float)         []
    
      - frozen : fzn                   (bool)          []
    
      - insertWithEdgeFlow : ief       (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - offset : of                    (float)         [create]
          Weight value controlling the relative positioning of the new edges. The range of values is [0.0, 1.0].
    
      - smoothingAngle : sma           (float)         [create]
          Subdivide new edges will be soft if less then this angle. C: Default is 180.0
    
      - splitType : stp                (int)           [create,query,edit]
          Choose between 2 different types of splits.  If this is set to 0 then the split type will be absolute.  This is where
          each of the splits will maintain an equal distance from the associated vertices.  If this is set to 1 then the split
          type will be relative. This is where each split will be made at an equal percentage along the length of the edge.
          Common flags
    
      - startVertexOffset : svo        (float)         []
    
    
    Derived from mel command `maya.cmds.polyDuplicateEdge`
    """

    pass


def polyCloseBorder(*args, **kwargs):
    """
    Closes open borders of objects. For each border edge given, a face is created to fill the hole the edge lies on.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyCloseBorder`
    """

    pass


def getMetadata(*args, **kwargs):
    """
    This command is used to retrieve the values of metadata elements from a node or scene. It is restricted to returning a
    single structure member at a time. For convenience the detail required is only enough to find a single Member of a
    single Structure on a single metadata Channel.  In the simplest case if there is a single Stream on one metadata Channel
    which uses a Structure with only one Member then all that is required is the name of the object containing the metadata.
    In the most complex case the 'channelName', 'streamName', and 'memberName' are all required to narrow down the metadata
    to a single unique Member.  In general for scripting it's a good idea to use all flags anyway since there could be
    metadata added anywhere. The shortcuts are mainly for quick entry when entering commands directly in the script editor
    or command line.  When an Index is specified where data is not present the command fails with a message telling you
    which Index or Indices didn't have values. Use the hasMetadatacommand first to determine where metadata exists if you
    need to know in advance where to find valid metadata.  Filter FlagschannelName- Only look for metadata on one particular
    Channel typestreamName- Only look for metadata on one particular named Stream. When used in conjunction with
    channelNamethen ignore Streams with a matching name but a different Channel typeindex- Only look for metadata on one or
    more specific Index values of a Stream. Requires use of the streamNameflag. Does not require the indexTypeflag as that
    will be inferred by the streamName.startIndex/endIndex- Same as indexbut using an entire range of Index values rather
    than a single one. Not valid for index types not supporting ranges (e.g. strings)indexType- Only look for metadata using
    a particular Index type. Can have its scope narrowed by other filter flags as well.memberName- The particular Member in
    the metadata in a Structure to retrieve. If this is not specified the Structure can only have a single Member.Metadata
    on meshes is special in that the Channel types vertex, edge, face, and vertexFaceare directly connected to the
    components of the same name. To make getting these metadata Channels easier you can simply select or specify on the
    command line the corresponding components rather than using the channelNameand index/startIndex/endIndexflags. For
    example the selection myMesh.vtx[8:10]corresponds to channelName = vertexand either index = 8, 9, 10as a multi-use flag
    or setIndex = 8, endIndex=10.  Only a single node or scene and unique metadata Structure Member are allowed in a single
    command. This keeps the data simple at the possible cost of requiring multiple calls to the command to get more than one
    Structure Member's value.  When the data is returned it will be in Index order with an entire Member appearing together.
    For example if you were retrieving float[3] metadata on three components you would get the nine values back in the
    order: index[0]-float[0], index[0]-float[1], index[0]-float[2], index[1]-float[0], index[1]-float[1], index[1]-float[2],
    index[2]-float[0], index[2]-float[1], index[2]-float[2]. In the Python implementation the float[3] values will be an
    array each so you would get back three float[3] arrays.
    
    Flags:
      - channelName : cn               (unicode)       [create,query]
          Filter the metadata selection to only recognize metadata belonging to the specified named Channel (e.g. vertex). This
          flag is ignored if the components on the selection list are being used to specify the metadata of interest. In query
          mode, this flag can accept a value.
    
      - channelType : cht              (unicode)       [create,query]
          Obsolete - use the 'channelName' flag instead. In query mode, this flag can accept a value.
    
      - dataType : dt                  (bool)          [create]
          Used with the flag 'streamName' and 'memberName' to query the dataType of the specfied member.
    
      - endIndex : eix                 (unicode)       [create]
          The metadata is stored in a Stream, which is an indexed list. If you have mesh components selected then the metadata
          indices are implicit in the list of selected components. If you select only the node or scene then this flag may be used
          in conjunction with the startIndexflag to specify a range of indices from which to retrieve the metadata. It is an error
          to have the value of startIndexbe greater than that of endIndex.  See also the indexflag for an alternate way to specify
          multiple indices. This flag can only be used on index types that support a range (e.g. integer values - it makes no
          sense to request a range between two strings)  In query mode, this flag can accept a value.
    
      - index : idx                    (unicode)       [create,query]
          In the typical case metadata is indexed using a simple integer value. Certain types of data may use other index types.
          e.g. a vertexFacecomponent will use a pairindex type, which is two integer values; one for the face ID of the component
          and the second for the vertex ID.  The indexflag takes a string, formatted in the way the specified indexTyperequires.
          All uses of the indexflag have the same indexType. If the type was not specified it is assumed to be a simple integer
          value.  In query mode, this flag can accept a value.
    
      - indexType : idt                (unicode)       [create,query]
          Name of the index type the new Channel should be using. If not specified this defaults to a simple integer index. Of the
          native types only a mesh vertexFacechannel is different, using a pairindex type. In query mode, this flag can accept a
          value.
    
      - listChannelNames : lcn         (bool)          [create]
          Query the channel names on the shape. This flag can be used with some flags to filter the results. It can be used with
          the flag 'streamName' to get the channel with the specfied stream and the flag 'memberName' to get the channel in which
          the stream contains the specified member. It cannot be used with the flag 'channelName'.
    
      - listMemberNames : lmn          (bool)          [create]
          Query the member names on the shape. This flag can be used with some flags to filter the results. It can be used with
          'streamName' to get the member which is in the specified stream and the flag 'channelName' to get the member which is
          used in the specfied channel. It cannot be used with the flag 'memberName'.
    
      - listStreamNames : lsn          (bool)          [create]
          Query the stream names on the shape. This flag can be used with some flags to filter the results. It can be used with
          the flag 'channelName' to get the stream names on the specified channel and the flag 'memberName' to get the stream
          names which has the specified member. It cannot be used with the flag 'streamName'.
    
      - memberName : mn                (unicode)       [create]
          Name of the Structure member being retrieved. The names of the members are set up in the Structure definition, either
          through the description passed in through the dataStructurecommand or via the API used to create that Structure. This
          flag is only necessary when selected Structures have more than one member.
    
      - scene : scn                    (bool)          [create,query]
          Use this flag when you want to add metadata to the scene as a whole rather than to any individual nodes. If you use this
          flag and have nodes selected the nodes will be ignored and a warning will be displayed.
    
      - startIndex : six               (unicode)       [create]
          The metadata is stored in a Stream, which is an indexed list. If you have mesh components selected then the metadata
          indices are implicit in the list of selected components. If you select only the node or scene then this flag may be used
          in conjunction with the endIndexflag to specify a range of indices from which to retrieve the metadata. It is an error
          to have the value of startIndexbe greater than that of endIndex.  See also the indexflag for an alternate way to specify
          multiple indices. This flag can only be used on index types that support a range (e.g. integer values - it makes no
          sense to request a range between two strings)  In query mode, this flag can accept a value.
    
      - streamName : stn               (unicode)       [create,query]
          Name of the metadata Stream. Depending on context it could be the name of a Stream to be created, or the name of the
          Stream to pass through the filter. In query mode, this flag can accept a value.Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.getMetadata`
    """

    pass


def polySelect(*args, **kwargs):
    """
    This command makes different types of poly component selections.  The return value is an integer array containing the
    id's of the components in the selection in order. If a given type of selection loops back on itself then this is
    indicated by the start id appearing twice, once at the start and once at the end.
    
    Flags:
      - add : add                      (bool)          [create,query]
          Indicates that the specified items should be added to the active list without removing existing items from the active
          list.
    
      - addFirst : af                  (bool)          [create,query]
          Indicates that the specified items should be added to the front of the active list without removing existing items from
          the active list.
    
      - asSelectString : ass           (bool)          [create,query]
          Changes the return type from an integer array to a string array which can be used as a selection string.
    
      - deselect : d                   (bool)          [create,query]
          Indicates that the specified items should be removed from the active list if they are on the active list.
    
      - edgeBorder : eb                (int)           [create,query]
          Select all conected border edges starting at the given edge.
    
      - edgeBorderPath : ebp           (int, int)      [create,query]
          Given two edges on the same border, this will select the edges on the border in the path between them.
    
      - edgeBorderPattern : bpt        (int, int)      [create,query]
          Given two edges on the same border, this will check how many edges there are between the given edges and then continue
          that pattern of selection around the border.
    
      - edgeLoop : el                  (int)           [create,query]
          Select an edge loop starting at the given edge.
    
      - edgeLoopOrBorder : elb         (int)           [create,query]
          Select an edge loop or all conected border edges, depending on whether the edge is on a border or not, starting at the
          given edge.
    
      - edgeLoopOrBorderPattern : lbp  (int, int)      [create,query]
          Given two edges either on the same edge loop or on the same edge border, this will check how many edges there are
          between the given edges and then continue that pattern of selection around the edge loop or edge border.
    
      - edgeLoopPath : elp             (int, int)      [create,query]
          Given two edges that are on the same edge loop, this will select the shortest path between them on the loop.
    
      - edgeLoopPattern : lpt          (int, int)      [create,query]
          Given two edges on the same edge loop, this will check how many edges there are between the given edges and then
          continue that pattern of selection around the edge loop.
    
      - edgeRing : er                  (int)           [create,query]
          Select an edge ring starting at the given edge.
    
      - edgeRingPath : erp             (int, int)      [create,query]
          Given two edges that are on the same edge ring, this will select the shortest path between them on the ring.
    
      - edgeRingPattern : rpt          (int, int)      [create,query]
          Given two edges on the same edge ring, this will check how many edges there are between the given edges and then
          continue that pattern of selection around the edge ring.
    
      - edgeUVLoopOrBorder : euv       (int)           [create,query]
          Select an edge loop or border, terminating at UV borders.
    
      - everyN : en                    (int)           []
    
      - extendToShell : ets            (int)           [create,query]
          Select the poly shell given a face id.
    
      - noSelection : ns               (bool)          [create,query]
          If this flag is used then the selection is not changed at all.
    
      - replace : r                    (bool)          [create,query]
          Indicates that the specified items should replace the existing items on the active list.
    
      - shortestEdgePath : sep         (int, int)      [create,query]
          Given two vertices, this will select the shortest path between them in the 3d object space.
    
      - shortestEdgePathUV : spu       (int, int)      [create,query]
          Given two UVs, this will select the shortest path between them in the 2d texture space.
    
      - shortestFacePath : sfp         (int, int)      [create,query]
          Given two faces, this will select the shortest path between them in the 3d object space.
    
      - toggle : tgl                   (bool)          [create,query]
          Indicates that those items on the given list which are on the active list should be removed from the active list and
          those items on the given list which are not on the active list should be added to the active list.                  Flag
          can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polySelect`
    """

    pass


def polyMergeEdge(*args, **kwargs):
    """
    Sews two border edges together.The new edge is located either on the first, last, or between both selected edges,
    depending on the mode. Both edges must belong to the same object, and orientations must match (i.e. normals on
    corresponding faces must point in the same direction).Edge flags are mandatory.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - firstEdge : fe                 (int)           [create,query,edit]
          The number of the first edge to merge.
    
      - frozen : fzn                   (bool)          []
    
      - mergeMode : mm                 (int)           [create,query,edit]
          This flag specifies how to merge, merge mode : at first edge : 0, in between : 1, at last edge : 2. C: Default is in
          between.
    
      - mergeTexture : mt              (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - secondEdge : se                (int)           [create,query,edit]
          The number of the second edge to merge.                  Common flags
    
    
    Derived from mel command `maya.cmds.polyMergeEdge`
    """

    pass


def revolve(*args, **kwargs):
    """
    This command creates a revolved surface by revolving the given profile curve about an axis.  The profile curve can be a
    curve, curve-on-surface, surface isoparm, or trim edge.
    
    Flags:
      - autoCorrectNormal : acn        (bool)          [create,query,edit]
          If this is set to true we will attempt to reverse the direction of the axis in case it is necessary to do so for the
          surface normals to end up pointing to the outside of the object. Default:false
    
      - axis : ax                      (float, float, float) [create,query,edit]
          Revolve axis
    
      - axisChoice : aco               (int)           [create,query,edit]
          Only used for computed axis/pivot case.  As we are computing the axis for a planar curve, we have two choices for the
          major axis based axis.  We will choose the axis corresponding to the longer dimension of the object (0), or explicitly
          choose one or the other (choices 1 and 2). Default:0
    
      - axisX : axx                    (float)         [create,query,edit]
          X of the axis Default:1
    
      - axisY : axy                    (float)         [create,query,edit]
          Y of the axis Default:0
    
      - axisZ : axz                    (float)         [create,query,edit]
          Z of the axis Default:0
    
      - bridge : br                    (bool)          [create,query,edit]
          If true, we will close a partial revolve to get a pie shaped surface.  The surface will be closed, but not periodic the
          way it is in the full revolve case. Default:false
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - computePivotAndAxis : cpa      (int)           [create,query,edit]
          If this is set to 2, we will compute the axis, use the curve position and radius to compute the pivot for the revolve
          internally.  The value of the pivot and axis attributes are ignored.  If this is set to 1, we will take the supplied
          axis, but compute the pivot.  If this is set to 0, we will take both the supplied axis and pivot. Default:0
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting surface. Default:3
    
      - endSweep : esw                 (float)         [create,query,edit]
          The value for the end sweep angle, in the current units.  This must be no more than the maximum, 360 degrees, or 2 Pi
          radians. Default:6.2831853
    
      - frozen : fzn                   (bool)          []
    
      - mergeItems : mi                (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - pivot : p                      (float, float, float) [create,query,edit]
          Revolve pivot point
    
      - pivotX : px                    (float)         [create,query,edit]
          X of the pivot Default:0
    
      - pivotY : py                    (float)         [create,query,edit]
          Y of the pivot Default:0
    
      - pivotZ : pz                    (float)         [create,query,edit]
          Z of the pivot Default:0
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)
    
      - radius : r                     (float)         [create,query,edit]
          The pivot point will be this distance away from the bounding box of the curve, if computedPivot is set to true.  The
          value of the pivot attribute is ignored. Default:1
    
      - radiusAnchor : ra              (float)         [create,query,edit]
          The position on the curve for the anchor point so that we can compute the pivot using the radius value.  If in 0 - 1
          range, its on the curve, normalized parameter range.  If 0 or 1, its computed based on the bounding box. Default:-1
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.
    
      - rebuild : rb                   (bool)          [create]
          Rebuild the input curve(s) before using them in the operation.  Use nurbsCurveRebuildPref to set the parameters for the
          conversion.
    
      - sections : s                   (int)           [create,query,edit]
          Number of sections of the resulting surface (if tolerance is not used). Default:8
    
      - startSweep : ssw               (float)         [create,query,edit]
          The value for the start sweep angle, in the current units.  This must be no more than the maximum, 360 degrees, or 2 Pi
          radians. Default:0
    
      - tolerance : tol                (float)         [create,query,edit]
          Tolerance to build to (if useTolerance attribute is set) Default:0.01
    
      - useLocalPivot : ulp            (bool)          [create,query,edit]
          If true, then the pivot of the profile curve is used as the start point of the axis of revolution.
          Advanced flags
    
      - useTolerance : ut              (bool)          [create,query,edit]
          Use the tolerance, or the number of sections to control the sections. Default:false                  Common flags
    
    
    Derived from mel command `maya.cmds.revolve`
    """

    pass


def nurbsCopyUVSet(*args, **kwargs):
    """
    This is only a sample command for debugging purposes, which makes a copy of the implicit st parameterization on a nurbs
    surface to be the 1st explicit uvset.
    
    
    Derived from mel command `maya.cmds.nurbsCopyUVSet`
    """

    pass


def subdivDisplaySmoothness(*args, **kwargs):
    """
    Sets or querys the display smoothness of subdivision surfaces on the selection list or of all subdivision surfaces if
    the -all option is set.  Smoothness options are; rough, medium, or fine.  Rough is the default.
    
    Flags:
      - all : boolean                  (If set, change smoothness for all subdivision surfaces) [create,query]
    
      - smoothness : s                 (int)           [create,query]
          Smoothness - 1 rough, 2 medium, 3 fine                             Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.subdivDisplaySmoothness`
    """

    pass


def subdAutoProjection(*args, **kwargs):
    """
    Projects a texture map onto an object, using several orthogonal projections simultaneously. The argument is a face
    selection list.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - layout : l                     (int)           [create,query,edit]
          What layout algorithm should be used: 0 UV pieces are aligned along the U axis. 1 UV pieces are moved in a square shape.
    
      - layoutMethod : lm              (int)           [create,query,edit]
          Which layout method to use: 0 Block Stacking. 1 Shape Stacking.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - optimize : o                   (int)           [create,query,edit]
          Use two different flavors for the cut generation. 0 Every face is assigned to the best plane. This optimizes the map
          distortion. 1 Small UV pieces are incorporated into larger ones, when the extra distortion introduced is reasonable.
          This tends to produce fewer UV pieces.
    
      - percentageSpace : ps           (float)         [create,query,edit]
          When layout is set to square, this value is a percentage of the texture area which is added around each UV piece. It can
          be used to ensure each UV piece uses different pixels in the texture. Maximum value is 5 percent.
    
      - planes : p                     (int)           [create,query,edit]
          Number of intermediate projections used. Valid numbers are 4, 5, 6, 8, and 12. C: Default is 6.
    
      - scale : sc                     (int)           [create,query,edit]
          How to scale the pieces, after projections: 0 No scale is applied. 1 Uniform scale to fit in unit square. 2 Non
          proportional scale to fit in unit square.
    
      - skipIntersect : si             (bool)          [create,query,edit]
          When on, self intersection of UV pieces are not tested. This makes the projection faster and produces fewer pieces, but
          may lead to overlaps in UV space.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off.                  Advanced flags
    
    
    Derived from mel command `maya.cmds.subdAutoProjection`
    """

    pass


def subdMirror(*args, **kwargs):
    """
    This command takes a subdivision surface, passed as the argument, and produces a subdivision surface that is a mirror.
    Returns the name of the subdivision surface created and optionally the DG node that does the mirroring.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off (where applicable).
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Name the resulting object.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the depend node (where applicable).                  Advanced flags
    
      - xMirror : xm                   (bool)          [create,query,edit]
          Mirror the vertices in X Default:false
    
      - yMirror : ym                   (bool)          [create,query,edit]
          Mirror the vertices in Y Default:false
    
      - zMirror : zm                   (bool)          [create,query,edit]
          Mirror the vertices in Z Default:false                  Common flags
    
    
    Derived from mel command `maya.cmds.subdMirror`
    """

    pass


def polyAppendVertex(*args, **kwargs):
    """
    Appends a new face to the selected polygonal object. The direction of the normal is given by the vertex order: the face
    normal points towards the user when the vertices rotate counter clockwise. Note that holes must be described in the
    opposite direction. Only works with one object selected.
    
    Flags:
      - append : a                     (float, float, float) [create]
          Append a vertex or a point to the selected object, or mark the start of a hole.  This flag may also be used in place of
          the hole, vertexand pointflags. If no argument is passed to the appendflag, then it marks the beginning of a hole (use
          an empty tuple in Python '()').  If one argument is passed, then the argument is considered to be an index into the
          vertices of the selected object, as with the vertexflag.  If three arguments are passed, then it is interpreted as the
          coordinates of a new point which will be inserted, as with the pointflag.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - hole : h                       (bool)          [create]
          Add a hole. The following points and edges will define a hole.  Note that this flag should be avoided in Python.  You
          may use the appendflag instead and pass an empty tuple '()' to specify the start of a hole.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - point : p                      (float, float, float) [create]
          Adds a new point to the new face. Coordinates of free points are given in the local object reference.  Note that this
          flag should be avoided in Python.  You may use the appendflag instead and pass three arguments.
    
      - texture : tx                   (int)           [create,query,edit]
          Specifies how new faces are mapped. 0 - None; 1 - Normalize; 2 - Unitize C: Default is 0 (no mapping). Q: When queried,
          this flag returns an int
    
      - vertex : v                     (int)           [create]
          Adds the given vertex of the selected object to the new face.  Note that this flag should be avoided in Python.  You may
          use the appendflag instead and pass one argument.                  Common flags
    
    
    Derived from mel command `maya.cmds.polyAppendVertex`
    """

    pass


def curve(*args, **kwargs):
    """
    The curve command creates a new curve from a list of control vertices (CVs).  A string is returned containing the
    pathname to the newly created curve.  You can create a curve from points either in world space or object (local) space,
    either with weights or without. You can replace an existing curve by using the -r/replaceflag.  You can append a point
    to an existing curve by using the -a/appendflag. To create a curve-on-surface, use the curveOnSurface command. To change
    the degree of a curve, use the rebuildCurve command. To change the of parameter range curve, use the rebuildCurve
    command.
    
    Maya Bug Fix:
      - name parameter only applied to transform. now applies to shape as well
    
    Flags:
      - append : a                     (bool)          [create]
          Appends point(s) to the end of an existing curve. If you use this flag, you must specify the name of the curve to append
          to, at the end of the command.  (See examples below.)
    
      - bezier : bez                   (bool)          [create]
          The created curve will be a bezier curve.
    
      - degree : d                     (float)         [create]
          The degree of the new curve.  Default is 3.  Note that you need (degree+1) curve points to create a visible curve span.
          eg. you must place 4 points for a degree 3 curve.
    
      - editPoint : ep                 (float, float, float) [create]
          The x, y, z position of an edit point.  linearmeans that this flag can take values with units.  This flag can not be
          used with the -point or the -pointWeight flags.
    
      - knot : k                       (float)         [create]
          A knot value in a knot vector.  One flag per knot value. There must be (numberOfPoints + degree - 1) knots and the knot
          vector must be non-decreasing.
    
      - name : n                       (unicode)       []
    
      - objectSpace : os               (bool)          [create]
          Points are in object, or localspace.  This is the default. You cannot specify both -osand -wsin the same command.
    
      - periodic : per                 (bool)          [create]
          If on, creates a curve that is periodic.  Default is off.
    
      - point : p                      (float, float, float) [create]
          The x, y, z position of a point.  linearmeans that this flag can take values with units.
    
      - pointWeight : pw               (float, float, float, float) [create]
          The x,y,z and w values of a point, where the w is a weight value. A rational curve will be created if this flag is used.
          linearmeans that this flag can take values with units.
    
      - replace : r                    (bool)          [create]
          Replaces an entire existing curve. If you use this flag, you must specify the name of the curve to replace, at the end
          of the command.  (See examples below.)
    
      - worldSpace : ws                (bool)          [create]
          Points are in world space.  The default is -os. You cannot specify both -osand -wsin the same command.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.curve`
    """

    pass


def cylinder(*args, **kwargs):
    """
    The cylinder command creates a new cylinder and/or a dependency node that creates one, and returns their names.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          The primitive's axis
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting surface: 1 - linear, 3 - cubic Default:3
    
      - endSweep : esw                 (float)         [create,query,edit]
          The angle at which to end the surface of revolution. Default is 2Pi radians, or 360 degrees. Default:6.2831853
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - heightRatio : hr               (float)         [create,query,edit]
          Ratio of heightto widthDefault:2.0
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - pivot : p                      (float, float, float) [create,query,edit]
          The primitive's pivot point
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)Advanced flags
    
      - radius : r                     (float)         [create,query,edit]
          The radius of the object Default:1.0
    
      - sections : s                   (int)           [create,query,edit]
          The number of sections determines the resolution of the surface in the sweep direction. Used only if useTolerance is
          false. Default:8
    
      - spans : nsp                    (int)           [create,query,edit]
          The number of spans determines the resolution of the surface in the opposite direction. Default:1
    
      - startSweep : ssw               (float)         [create,query,edit]
          The angle at which to start the surface of revolution Default:0
    
      - tolerance : tol                (float)         [create,query,edit]
          The tolerance with which to build the surface. Used only if useTolerance is true Default:0.01
    
      - useTolerance : ut              (bool)          [create,query,edit]
          Use the specified tolerance to determine resolution. Otherwise number of sections will be used. Default:false
          Common flags
    
    
    Derived from mel command `maya.cmds.cylinder`
    """

    pass


def polySetToFaceNormal(*args, **kwargs):
    """
    This command takes selected polygonal vertices or vertex-faces and changes their normals. If the option userNormal is
    used, the new normal values will be the face normals arround the vertices/vertex-faces. Otherwise the new normal values
    will be default values according to the internal calculation.
    
    Flags:
      - setUserNormal : su             (bool)          [create]
          when this flag is presented, user normals will be created on each vertex face and the values will be the face normal
          value. Otherwise the normal values will be the internal computing results. Default is false.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polySetToFaceNormal`
    """

    pass


def polySewEdge(*args, **kwargs):
    """
    Merge border edges within a given threshold.Perform pair-wise comparison of selected edges. Pairs whose corresponding
    vertices meet threshold conditions and whose orientations are aligned (i.e. their respective normals point in the same
    direction) are merged, as are the vertices (in other words, vertices are shared). Resulting mesh may have extra vertices
    or edges to ensure geometry is valid. Edges must be on the same object to be merged. Default : share only vertices lying
    exactly at the same place. (polySewEdge -t 0.0)
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - texture : tx                   (bool)          [create,query,edit]
          If true : texture is sewn as well as the 3d edge. C: Default is true. Q: When queried, this flag returns an int.
    
      - tolerance : t                  (float)         [create,query,edit]
          The tolerance to sew edges (edge distance) C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: tolerance value is taken in world reference. If off: tolerance value
          is considered  in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polySewEdge`
    """

    pass


def multiProfileBirailSurface(*args, **kwargs):
    """
    The cmd creates a railed surface by sweeping the profiles using two rail curves. The two rails are the last two
    arguments. For examples, if 5 curves are specified, they will correspond to curve1curve2curve3rail1rail2. In this case,
    the cmd creates a railed surface by sweeping the profile curve1to profile curve2, profile curve2to profile curve3along
    the two rail curves rail1, rail2. There must be atleast 3 profile curves followed by the two rail curves. The profile
    curves must intersect the two rail curves. The constructed may be made tangent continuous to the first and last profile
    using the flags -tp1, -tp2 provided the profiles are surface curves i.e. isoparms, curve on surface or trimmed edge.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)Advanced flags
    
      - tangentContinuityProfile1 : tp1 (bool)          [create,query,edit]
          Tangent continuous across the first profile. The profile must be a surface curve. Default:false
    
      - tangentContinuityProfile2 : tp2 (bool)          [create,query,edit]
          Tangent continuous across the last profile. The profile must be a surface curve. Default:false
    
      - transformMode : tm             (int)           [create,query,edit]
          transform mode ( Non proportional, proportional ). Non proportional is default value. Default:0                  Common
          flags
    
    
    Derived from mel command `maya.cmds.multiProfileBirailSurface`
    """

    pass


def polyForceUV(*args, **kwargs):
    """
    A set of functionalities can be called through this command.  The input for this command is a set of faces.  Based on
    the arguments passed, the UVs for these selected faces can be created. Project UVs based on the camera:(UV creation)
    Based on the current view direction/orientation, the UVs are generated and assigned to the faces.  Any previously
    assigned UV information will be lost. Best Plane Projection:(UV creation) The UVs are computed based on the plane
    defined by the user, and is applied to the selected faces.  This tool has 2 phases.  In the first phase, the faces to be
    mapped (faces to which UVs are to be created) are selected. In the second phase, the points (vertices, CVs) that define
    the projecting plane are selected.  Any previously assigned UV information will be lost. Unitize:(UV creation) A new set
    of unitized UVs are generated and assigned to the faces.         Any previously assigned UV information will be lost.
    Unshare:(UV creation) Force the specified UV to be unshared by possibly creating new UVs.  Any previously assigned UV
    information will be lost.
    
    Flags:
      - cameraProjection : cp          (bool)          [create]
          Project the UVs based on the camera position/orientation
    
      - createNewMap : cm              (bool)          [create]
          Create new map if it does not exist.
    
      - flipHorizontal : fh            (bool)          [create]
          OBSOLETE flag.  Use polyFlipUV instead.
    
      - flipVertical : fv              (bool)          [create]
          OBSOLETE flag.  Use polyFlipUV instead.
    
      - g : g                          (bool)          [create]
          OBSOLETE flag.
    
      - local : l                      (bool)          [create]
          OBSOLETE flag.
    
      - normalize : nor                (unicode)       [create]
          OBSOLETE flag.  Use polyNormalizeUV instead.
    
      - numItems : ni                  (int)           [create]
          This flag is only used for the best plane texturingof polygonal faces.  This flag should be followed by a
          selection list. If not specified, the selected objects will         be used (in the order they were selected). This flag
          specifies the number of items (leading) in the         selection list that should be used for the mapping.         The
          trailing items will be used for computing the         plane (See example below).  The best plane texturingis better
          suited for using interactively from within its context.         You can type setToolTo polyBestPlaneTexturingContextin
          the command window OR (EditPolygons-Texture-BestPlaneTexturing         from the Menu) to enter its context.
    
      - preserveAspectRatio : par      (bool)          [create]
          OBSOLETE flag.
    
      - unitize : uni                  (bool)          [create]
          To unitize the UVs of the selected faces
    
      - unshare : u                    (bool)          [create]
          To unshare tye specified UV
    
      - uvSetName : uvs                (unicode)       [create]
          Specifies name of the uv set to work on                                    Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyForceUV`
    """

    pass


def projectCurve(*args, **kwargs):
    """
    The projectCurve command creates curves on surface where all selected curves project onto the selected surfaces.
    Projection can be done using the surface normals or the user can specify the vector to project along. Note: the user
    does not have to specify the curves and surfaces in any particular order in the command line.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - direction : d                  (float, float, float) [create,query,edit]
          Direction of projection. Available only if useNormal is false.
    
      - directionX : dx                (float)         [create,query,edit]
          X direction of projection. Default:0.0
    
      - directionY : dy                (float)         [create,query,edit]
          Y direction of projection. Default:0.0
    
      - directionZ : dz                (float)         [create,query,edit]
          Z direction of projection. Default:1.0
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.                  Advanced flags
    
      - tolerance : tol                (float)         [create,query,edit]
          Tolerance to fit to. Default:0.01
    
      - useNormal : un                 (bool)          [create,query,edit]
          True if the surface normal is to be used and false if the direction vector should be used instead. Default:false
          Common flags
    
    
    Derived from mel command `maya.cmds.projectCurve`
    """

    pass


def polyMoveVertex(*args, **kwargs):
    """
    Modifies vertices of a polygonal object. Translate, rotate or scale vertices in local or world space.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - gain : ga                      (float)         []
    
      - localDirection : ld            (float, float, float) [create,query,edit]
          This flag specifies the X axis for local space. C: Default is 0.0 0.0 1.0. Q: When queried, this flag returns a
          float[3].
    
      - localDirectionX : ldx          (float)         [create,query,edit]
          This flag specifies X coord for thr X axis. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localDirectionY : ldy          (float)         [create,query,edit]
          This flag specifies Y coord for thr X axis. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localDirectionZ : ldz          (float)         [create,query,edit]
          This flag specifies Z coord for thr X axis. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localTranslate : lt            (float, float, float) [create,query,edit]
          Local translation vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - localTranslateX : ltx          (float)         [create,query,edit]
          Local translation X coord. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localTranslateY : lty          (float)         [create,query,edit]
          Local translation Y coord. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localTranslateZ : ltz          (float)         [create,query,edit]
          Local translation Z coord : Move along the vertex normal. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - pivot : pvt                    (float, float, float) [create,query,edit]
          This flag specifies the pivot for scaling and rotation. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - pivotX : pvx                   (float)         [create,query,edit]
          This flag specifies the X pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotY : pvy                   (float)         [create,query,edit]
          This flag specifies the Y pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotZ : pvz                   (float)         [create,query,edit]
          This flag specifies the Z pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
          Local Values
    
      - random : ran                   (float)         [create,query,edit]
          This flag specifies the random value for all parameters. C: Default is 0.0. The range is [-10.0, 10.0]. Q: When queried,
          this flag returns a float.
    
      - rotate : ro                    (float, float, float) [create,query,edit]
          This flag specifies the rotation angles around X, Y, Z. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - rotateX : rx                   (float)         [create,query,edit]
          This flag specifies the rotation angle around X. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateY : ry                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Y. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateZ : rz                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Z. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - scale : s                      (float, float, float) [create,query,edit]
          This flag specifies the scaling vector. C: Default is 1.0 1.0 1.0. Q: When queried, this flag returns a float[3].
    
      - scaleX : sx                    (float)         [create,query,edit]
          This flag specifies X for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleY : sy                    (float)         [create,query,edit]
          This flag specifies Y for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleZ : sz                    (float)         [create,query,edit]
          This flag specifies Z for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - translate : t                  (float, float, float) [create,query,edit]
          This flag specifies the translation vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - translateX : tx                (float)         [create,query,edit]
          This flag specifies the X translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateY : ty                (float)         [create,query,edit]
          This flag specifies the Y translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateZ : tz                (float)         [create,query,edit]
          This flag specifies the Z translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int. Global
          ValuesCommon flags
    
    
    Derived from mel command `maya.cmds.polyMoveVertex`
    """

    pass


def manipOptions(*args, **kwargs):
    """
    Changes the global manipulator parameters                In query mode, return type is based on queried flag.
    
    Flags:
      - forceRefresh : fr              (bool)          [create]
          Force a refresh if there is any deferred evaluation.
    
      - handleSize : hs                (float)         [create,query]
          Sets the maximum handles size in pixels, for small handles
    
      - hideManipOnCtrl : hmc          (bool)          [create,query]
          Hide transform manip when the Ctrl key is pressed.
    
      - hideManipOnShift : hms         (bool)          [create,query]
          Hide transform manip when the Shift key is pressed.
    
      - hideManipOnShiftCtrl : hsc     (bool)          [create,query]
          Hide transform manip when the Shift and Ctrl keys are both pressed.
    
      - linePick : lp                  (float)         [create,query]
          Set the width of picking zone for long handles
    
      - lineSize : ls                  (float)         [create,query]
          Set the width of long handles (drawn as lines)
    
      - middleMouseRepositioning : mm  (bool)          []
    
      - pivotRotateHandleOffset : pro  (int)           [create,query]
          Set the offset of the pivot rotation handle.
    
      - planeHandleOffset : pho        (int)           [create,query]
          Set the offset of the planar drag handles.
    
      - pointSize : ps                 (float)         [create,query]
          Set the size of points (used to display previous states)
    
      - preselectHighlight : psh       (bool)          [create,query]
          Set whether manip handles should be highlighted when moving mouse.
    
      - refreshMode : rm               (int)           [create,query]
          Set the global refresh mode.
    
      - relative : r                   (bool)          [create]
          All values are interpreted as multiplication factors instead of final values.
    
      - rememberActiveHandle : rah     (bool)          [create,query]
          Set whether manip handles should be remembered after selection change.
    
      - rememberActiveHandleAfterToolSwitch : rhs (bool)          [create,query]
          Set whether manip handles should be remembered after manipulator change.
    
      - scale : s                      (float)         [create,query]
          Global scaling factor of all manipulators
    
      - showExtrudeSliders : ses       (bool)          []
    
      - showPivotRotateHandle : spr    (int)           [create,query]
          Toggles the visibility of the pivot rotation handle.
    
      - showPlaneHandles : sph         (int)           [create,query]
          Toggles the visibility of the planar drag handles.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.manipOptions`
    """

    pass


def nurbsToPolygonsPref(*args, **kwargs):
    """
    This command sets the values used by the nurbs-to-polygons (or tesselate) preference.  This preference is used by Maya
    menu items and is saved between Maya sessions. To query any of the flags, use the -queryflag. For more information on
    the flags, see the node documentation for the nurbsTessellatenode. In query mode, return type is based on queried flag.
    
    Flags:
      - chordHeight : cht              (float)         [create,query]
    
      - chordHeightRatio : chr         (float)         [create,query]
    
      - delta3D : d                    (float)         [create,query]
    
      - edgeSwap : es                  (bool)          [create,query]
    
      - format : f                     (int)           [create,query]
          Valid values are 0, 1 and 2.
    
      - fraction : ft                  (float)         [create,query]
    
      - matchRenderTessellation : mrt  (int)           [create,query]
    
      - merge : m                      (int)           [create,query]
    
      - mergeTolerance : mt            (float)         [create,query]
    
      - minEdgeLen : mel               (float)         [create,query]
    
      - polyCount : pc                 (int)           [create,query]
    
      - polyType : pt                  (int)           [create,query]
    
      - uNumber : un                   (int)           [create,query]
    
      - uType : ut                     (int)           [create,query]
    
      - useChordHeight : uch           (bool)          [create,query]
    
      - useChordHeightRatio : ucr      (bool)          [create,query]
    
      - vNumber : vn                   (int)           [create,query]
    
      - vType : vt                     (int)           [create,query]
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.nurbsToPolygonsPref`
    """

    pass


def polyCylindricalProjection(*args, **kwargs):
    """
    Projects a cylindrical map onto an object.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createNewMap : cm              (bool)          [create,query,edit]
          This flag when set true will create a new map with a the name passed in, if the map does not already exist.
    
      - frozen : fzn                   (bool)          []
    
      - imageCenter : ic               (float, float)  [create,query,edit]
          This flag specifies the center point of the 2D model layout. C: Default is 0.5 0.5. Q: When queried, this flag returns a
          float[2].
    
      - imageCenterX : icx             (float)         [create,query,edit]
          This flag specifies X of the center point of the 2D model layout. C: Default is 0.5. Q: When queried, this flag returns
          a float.
    
      - imageCenterY : icy             (float)         [create,query,edit]
          This flag specifies Y of the center point of the 2D model layout. C: Default is 0.5. Q: When queried, this flag returns
          a float.
    
      - imageScale : imageScale        (float, float)  [create,query,edit]
          This flag specifies the UV scale : Enlarges or reduces the 2D version of the model in U or V space relative to the 2D
          centerpoint. C: Default is 1.0 1.0. Q: When queried, this flag returns a float[3].
    
      - imageScaleU : isu              (float)         [create,query,edit]
          This flag specifies the U scale : Enlarges or reduces the 2D version of the model in U space relative to the 2D
          centerpoint. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - imageScaleV : isv              (float)         [create,query,edit]
          This flag specifies the U scale : Enlarges or reduces the 2D version of the model in V space relative to the 2D
          centerpoint. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - insertBeforeDeformers : ibd    (bool)          [create]
          This flag specifies if the projection node should be inserted before or after deformer nodes already applied to the
          shape. Inserting the projection after the deformer leads to texture swimming during animation and is most often
          undesirable. C: Default is on.
    
      - keepImageRatio : kir           (bool)          []
    
      - mapDirection : md              (unicode)       []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - perInstance : pi               (bool)          []
    
      - projectionCenter : pc          (float, float, float) [create,query,edit]
          This flag specifies the point of origin from which the map is projected. C: Default is 0.0 0.0 0.0. Q: When queried,
          this flag returns a float[3].
    
      - projectionCenterX : pcx        (float)         [create,query,edit]
          This flag specifies the X of the origin's point from which the map is projected. C: Default is 0.0. Q: When queried,
          this flag returns a float.
    
      - projectionCenterY : pcy        (float)         [create,query,edit]
          This flag specifies the Y of the origin's point from which the map is projected. C: Default is 0.0. Q: When queried,
          this flag returns a float.
    
      - projectionCenterZ : pcz        (float)         [create,query,edit]
          This flag specifies the Z of the origin's point from which the map is projected. C: Default is 0.0. Q: When queried,
          this flag returns a float.
    
      - projectionHeight : ph          (float)         []
    
      - projectionHorizontalSweep : phs (float)         []
    
      - projectionScale : ps           (float, float)  [create,query,edit]
          This flag specifies the width and the height of the map relative to the 3D projection axis. C: Default is 180.0 1.0. Q:
          When queried, this flag returns a float[2].
    
      - projectionScaleU : psu         (float)         [create,query,edit]
          This flag specifies the width of the map relative to the 3D projection axis : the scale aperture. C: Default is 180.0.
          The range is [0, 360]. Q: When queried, this flag returns a float.
    
      - projectionScaleV : psv         (float)         [create,query,edit]
          This flag specifies the height of the map relative to the 3D projection axis : the scale height. C: Default is 1.0. Q:
          When queried, this flag returns a float.
    
      - radius : r                     (float)         []
    
      - rotate : ro                    (float, float, float) [create,query,edit]
          This flag specifies mapping's rotate angles. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - rotateX : rx                   (float)         [create,query,edit]
          This flag specifies X for mapping's rotate angles. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateY : ry                   (float)         [create,query,edit]
          This flag specifies Y for mapping's rotate angles. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateZ : rz                   (float)         [create,query,edit]
          This flag specifies Z for mapping's rotate angles. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotationAngle : ra             (float)         [create,query,edit]
          This flag specifies the angle for the rotation. When the angle is positive, then the map rotates counterclockwise on the
          mapped model, whereas when it is negative then the map rotates clockwise on the mapped model. C: Default is 0.0. Q: When
          queried, this flag returns a float.
    
      - seamCorrect : sc               (bool)          [create,query,edit]
          This flag specifies to perform a seam correction on the mapped faces.
    
      - smartFit : sf                  (bool)          [create]
          This flag specifies if the manipulator should be placed best fitting the object, or be placed on the specified position
          with the specified transformation values. Default is on.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on : all geometrical values are taken in world reference. If off : all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyCylindricalProjection`
    """

    pass


def propMove(*args, **kwargs):
    """
    Performs a proportional translate, scale or rotate operation on any number of objects. The percentages to rotate, scale
    or translate by can be specified using either the -p flags or -px, -py, -pz flags. Each selected object must have a
    corresponding -p or -px, -py, -pz flag. The rotate, scale or translate performed is relative.
    
    Flags:
      - percent : p                    (float)         [create]
          The percentage effect that the specified x,y,z has on an object. This flag must be specified once for each object, ie.
          if there are 4 objects specified, there must be 4 -pflags, (otherwise a percentage of 1.0 will be used).  This flag
          generally has a range between 0.0 and 1.0, but can be any float value.
    
      - percentX : px                  (float)         [create]
          The percentage effect that the specified x has on an object. This flag is specified one per object. The value ranges
          between 0.0 and 1.0, but can be any float value. If the -p flag has been specified, this flag usage is invalid.
    
      - percentY : py                  (float)         [create]
          The percentage effect that the specified y has on an object. This flag is specified one per object. The value ranges
          between 0.0 and 1.0, but can be any float value. If the -p flag has been specified, this flag usage is invalid.
    
      - percentZ : pz                  (float)         [create]
          The percentage effect that the specified z has on an object. This flag is specified one per object. The value ranges
          between 0.0 and 1.0, but can be any float value. If the -p flag has been specified, this flag usage is invalid.
    
      - pivot : pi                     (float, float, float) [create]
          Specify the pivot about which a rotation or scale will occur. The change in pivot lasts only as long as the current
          'propMove' command, and so must be used in conjunction with one of the above move flags for any effect to be noticeable.
    
      - rotate : r                     (float, float, float) [create]
          Proportionally rotate each object by the given angles. The rotation values are scaled by the percentage specified by
          that object's corresponding -percentflag. All angles are in degrees. The rotation is about the pivot specified by the
          -pivotflag, or (0, 0, 0) if the -pivotflag is not present.
    
      - scale : s                      (float, float, float) [create]
          Proportionally scale each object by the given amounts. The scale values are scaled by the percentage specified by that
          object's corresponding -percentflag. The position and size of each object is measured relative to the pivot specified by
          the -pivotflag, and defaults to each object's individual pivot. In the case of control vertices, or some other object
          component, the default is the parent object's pivot.
    
      - translate : t                  (float, float, float) [create]
          Proportionally translate each object by the given amounts. The translation values are scaled by the percentage specified
          by that object's corresponding -percentflag. The -pivotflag has no effect on translation.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
      - worldSpace : ws                (bool)          []
    
    
    Derived from mel command `maya.cmds.propMove`
    """

    pass


def insertKnotCurve(*args, **kwargs):
    """
    The insertKnotCurve command inserts knots into a curve given a list of parameter values. The number of knots to add at
    each parameter value and whether the knots are added or complemented can be specified. The name of the curve is
    returned. If construction history is on, the name of the resulting dependency node is also returned. An edit point will
    appear where you insert the knot. Also, the number of spans and CVs in the curve will increase in the area where the
    knot is inserted. You can insert up to degreeknots at a curve parameter that isn't already an edit point. eg. for a
    degree three curve, you can insert up to 3 knots. Use this operation if you need more CVs in a local area of the curve.
    Use this operation (or hardenPoint) if you want to create a corner in a curve.
    
    Flags:
      - addKnots : add                 (bool)          [create,query,edit]
          Whether to add knots or complement.  Complement means knots will be added to reach the specified number of knots.
          Default:true
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curveOnSurface : cos           (bool)          [create]
          If possible, create 2D curve as a result.
    
      - frozen : fzn                   (bool)          []
    
      - insertBetween : ib             (bool)          [create,query,edit]
          If set to true, and there is more than one parameter value specified, the knots will get inserted at equally spaced
          intervals between the given parameter values, rather than at the parameter values themselves. Default:false
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - numberOfKnots : nk             (int)           [create,query,edit]
          How many knots to insert.  At any point on the curve, there can be a maximum of degreeknots. Default:1
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - parameter : p                  (float)         [create,query,edit]
          Parameter value(s) where knots are added Default:0.0                  Common flags
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
    
    Derived from mel command `maya.cmds.insertKnotCurve`
    """

    pass


def polyMoveFacet(*args, **kwargs):
    """
    Modifies facet of a polygonal object. Translate, move, rotate or scale facets.
    
    Flags:
      - attraction : att               (float)         [create,query,edit]
          This flag specifies the attraction, related to magnet. C: Default is 0.0. The range is [-2.0, 2.0]. Q: When queried,
          this flag returns a float.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - gain : ga                      (float)         []
    
      - gravity : g                    (float, float, float) [create,query,edit]
          This flag specifies the gravity vector. C: Default is 0.0 -1.0 0.0. Q: When queried, this flag returns a float[3].
    
      - gravityX : gx                  (float)         [create,query,edit]
          This flag specifies X for the gravity vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - gravityY : gy                  (float)         [create,query,edit]
          This flag specifies Y for the gravity vector. C: Default is -1.0. Q: When queried, this flag returns a float.
    
      - gravityZ : gz                  (float)         [create,query,edit]
          This flag specifies Z for the gravity vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localCenter : lc               (int)           []
    
      - localDirection : ld            (float, float, float) [create,query,edit]
          This flag specifies the X axis for local space. C: Default is 0.0 0.0 1.0. Q: When queried, this flag returns a
          float[3].
    
      - localDirectionX : ldx          (float)         [create,query,edit]
          This flag specifies X coord of the X axis. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localDirectionY : ldy          (float)         [create,query,edit]
          This flag specifies Y coord of the X axis. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localDirectionZ : ldz          (float)         [create,query,edit]
          This flag specifies Z coord of the X axis. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localRotate : lr               (float, float, float) [create,query,edit]
          This flag specifies the local rotations : (slantRot, slantRoll, twistRot). C: Default is 0.0 0.0 0.0. Q: When queried,
          this flag returns a float[3]. Local rotation (slantRot, slantRoll, twistRot).
    
      - localRotateX : lrx             (float)         [create,query,edit]
          This flag specifies local rotation X angle (Slant Rot around slantAxis). C: Default is 0.0. The range is [0, 360]. Q:
          When queried, this flag returns a float.
    
      - localRotateY : lry             (float)         [create,query,edit]
          This flag specifies local rotation Y angle (Slant Roll of slantAxis). C: Default is 0.0. The range is [0, 180]. Q: When
          queried, this flag returns a float.
    
      - localRotateZ : lrz             (float)         [create,query,edit]
          This flag specifies local rotation Z angle (Twist around normal). C: Default is 0.0. The range is [0, 360]. Q: When
          queried, this flag returns a float.
    
      - localScale : ls                (float, float, float) [create,query,edit]
          This flag specifies the local scaling vector. C: Default is 1.0 1.0 1.0. Q: When queried, this flag returns a float[3].
    
      - localScaleX : lsx              (float)         [create,query,edit]
          This flag specifies X for local scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localScaleY : lsy              (float)         [create,query,edit]
          This flag specifies Y for local scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localScaleZ : lsz              (float)         [create,query,edit]
          This flag specifies Z for local scaling vector : Flattening. C: Default is 1.0. The range is [0.0, 1.0]. Q: When
          queried, this flag returns a float. Dynamic Values
    
      - localTranslate : lt            (float, float, float) [create,query,edit]
          This flag specifies the local translation vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - localTranslateX : ltx          (float)         [create,query,edit]
          This flag specifies the X local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localTranslateY : lty          (float)         [create,query,edit]
          This flag specifies the Y local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localTranslateZ : ltz          (float)         [create,query,edit]
          This flag specifies the Z local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - magnX : mx                     (float)         [create,query,edit]
          This flag specifies X for the magnet vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - magnY : my                     (float)         [create,query,edit]
          This flag specifies Y for the magnet vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - magnZ : mz                     (float)         [create,query,edit]
          This flag specifies Z for the magnet vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - magnet : m                     (float, float, float) [create,query,edit]
          This flag specifies the magnet vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - offset : off                   (float)         [create,query,edit]
          This flag specifies the local offset. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivot : pvt                    (float, float, float) [create,query,edit]
          This flag specifies the pivot for scaling and rotation. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - pivotX : pvx                   (float)         [create,query,edit]
          This flag specifies the X pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotY : pvy                   (float)         [create,query,edit]
          This flag specifies the Y pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotZ : pvz                   (float)         [create,query,edit]
          This flag specifies the Z pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
          Local Values
    
      - random : ran                   (float)         [create,query,edit]
          This flag specifies the random value for all parameters. C: Default is 0.0. The range is [-10.0, 10.0]. Q: When queried,
          this flag returns a float. Global Values
    
      - rotate : ro                    (float, float, float) [create,query,edit]
          This flag specifies the rotation angles around X, Y, Z. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - rotateX : rx                   (float)         [create,query,edit]
          This flag specifies the rotation angle around X. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateY : ry                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Y. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateZ : rz                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Z. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - scale : s                      (float, float, float) [create,query,edit]
          This flag specifies the scaling vector. C: Default is 1.0 1.0 1.0. Q: When queried, this flag returns a float[3].
    
      - scaleX : sx                    (float)         [create,query,edit]
          This flag specifies X for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleY : sy                    (float)         [create,query,edit]
          This flag specifies Y for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleZ : sz                    (float)         [create,query,edit]
          This flag specifies Z for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - translate : t                  (float, float, float) [create,query,edit]
          This flag specifies the translation vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - translateX : tx                (float)         [create,query,edit]
          This flag specifies the X translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateY : ty                (float)         [create,query,edit]
          This flag specifies the Y translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateZ : tz                (float)         [create,query,edit]
          This flag specifies the Z translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - weight : w                     (float)         [create,query,edit]
          This flag specifies the weight, related to gravity. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on : all geometrical values are taken in world reference. If off : all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyMoveFacet`
    """

    pass


def polyEditEdgeFlow(*args, **kwargs):
    """
    Edit edges of a polygonal object to respect surface curvature.
    
    Flags:
      - adjustEdgeFlow : aef           (float)         [create]
          The weight value of the edge vertices to be positioned. 0: Concave 0:  Middle point 1:  Surface continuity 1: Convex
          Default is 1.0
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - edgeFlow : ef                  (bool)          [create]
          True to enable edge flow. Otherwise, the edge flow is disabled. Default is true.                  Common flags
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyEditEdgeFlow`
    """

    pass


def polyMoveEdge(*args, **kwargs):
    """
    Modifies edges of a polygonal object. Translate, move, rotate or scale edges.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - gain : ga                      (float)         []
    
      - localCenter : lc               (int)           [create,query,edit]
          This flag specifies the local center on the edge : 0 - Middle point, 1 - Start point, 2 - End point. C: Default is 0
          (Middle point).
    
      - localDirection : ld            (float, float, float) [create,query,edit]
          This flag specifies the X axis for local space. C: Default is 0.0 0.0 1.0.
    
      - localDirectionX : ldx          (float)         [create,query,edit]
          This flag specifies X coord of the X axis. C: Default is 0.0.
    
      - localDirectionY : ldy          (float)         [create,query,edit]
          This flag specifies Y coord of the X axis. C: Default is 0.0.
    
      - localDirectionZ : ldz          (float)         [create,query,edit]
          This flag specifies Z coord of the X axis. C: Default is 1.0.
    
      - localRotate : lr               (float, float, float) [create,query,edit]
          This flag specifies the local rotations : (twistRot, slantRot, slantRoll). C: Default is 0.0 0.0 0.0. Local rotation
          (twistRot, slantRot, slantRoll).
    
      - localRotateX : lrx             (float)         [create,query,edit]
          This flag specifies local rotation X angle (Twist around normal) C: Default is 0.0. The range is [0, 360].
    
      - localRotateY : lry             (float)         [create,query,edit]
          This flag specifies local rotation Y angle (Slant Rot around slantAxis). C: Default is 0.0. The range is [0, 360].
    
      - localRotateZ : lrz             (float)         [create,query,edit]
          This flag specifies local rotation Z angle (Slant Roll of slantAxis). C: Default is 0.0. The range is [0, 180].
    
      - localScale : ls                (float, float, float) [create,query,edit]
          This flag specifies the local scaling vector. C: Default is 1.0 1.0 1.0.
    
      - localScaleX : lsx              (float)         [create,query,edit]
          This flag specifies X for local scaling vector. C: Default is 1.0.
    
      - localScaleY : lsy              (float)         [create,query,edit]
          This flag specifies Y for local scaling vector. C: Default is 1.0.
    
      - localScaleZ : lsz              (float)         [create,query,edit]
          This flag specifies Z for local scaling vector. C: Default is 1.0.
    
      - localTranslate : lt            (float, float, float) [create,query,edit]
          This flag specifies the local translation vector. C: Default is 0.0 0.0 0.0.
    
      - localTranslateX : ltx          (float)         [create,query,edit]
          This flag specifies the local X translation. C: Default is 0.0.
    
      - localTranslateY : lty          (float)         [create,query,edit]
          This flag specifies the local Y translation. C: Default is 0.0.
    
      - localTranslateZ : ltz          (float)         [create,query,edit]
          This flag specifies the local Z translation. C: Default is 0.0.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledGlobal Values
    
      - pivot : pvt                    (float, float, float) [create,query,edit]
          This flag specifies the pivot for scaling and rotation. C: Default is 0.0 0.0 0.0.
    
      - pivotX : pvx                   (float)         [create,query,edit]
          This flag specifies the X pivot for scaling and rotation. C: Default is 0.0.
    
      - pivotY : pvy                   (float)         [create,query,edit]
          This flag specifies the Y pivot for scaling and rotation. C: Default is 0.0.
    
      - pivotZ : pvz                   (float)         [create,query,edit]
          This flag specifies the Z pivot for scaling and rotation. C: Default is 0.0.
    
      - random : ran                   (float)         [create,query,edit]
          This flag specifies the random value for all parameters. C: Default is 0.0. The range is [-10.0, 10.0]. Local Values
    
      - rotate : ro                    (float, float, float) [create,query,edit]
          This flag specifies the rotation angles around X, Y, Z. C: Default is 0.0 0.0 0.0.
    
      - rotateX : rx                   (float)         [create,query,edit]
          This flag specifies the rotation angle around X. C: Default is 0.0.
    
      - rotateY : ry                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Y. C: Default is 0.0.
    
      - rotateZ : rz                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Z. C: Default is 0.0.
    
      - scale : s                      (float, float, float) [create,query,edit]
          This flag specifies the scaling vector. C: Default is 1.0 1.0 1.0.
    
      - scaleX : sx                    (float)         [create,query,edit]
          This flag specifies X for scaling vector. C: Default is 1.0.
    
      - scaleY : sy                    (float)         [create,query,edit]
          This flag specifies Y for scaling vector. C: Default is 1.0.
    
      - scaleZ : sz                    (float)         [create,query,edit]
          This flag specifies Z for scaling vector. C: Default is 1.0.
    
      - translate : t                  (float, float, float) [create,query,edit]
          This flag specifies the translation vector. C: Default is 0.0 0.0 0.0.
    
      - translateX : tx                (float)         [create,query,edit]
          This flag specifies the X translation vector. C: Default is 0.0.
    
      - translateY : ty                (float)         [create,query,edit]
          This flag specifies the Y translation vector. C: Default is 0.0.
    
      - translateZ : tz                (float)         [create,query,edit]
          This flag specifies the Z translation vector. C: Default is 0.0.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on : all geometrical values are taken in world reference. If off : all
          geometrical values are taken in object reference. C: Default is off.                  Common flags
    
    
    Derived from mel command `maya.cmds.polyMoveEdge`
    """

    pass


def polyTransfer(*args, **kwargs):
    """
    Transfer information from one polygonal object to another one. Both objects must have identical topology, that is same
    vertex, edge, and face numbering. The flags specify which of the vertices, UV sets or vertex colors will be copied.
    
    Flags:
      - alternateObject : ao           (unicode)       [create,query,edit]
          Name of the alternate object.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - uvSets : uv                    (bool)          [create,query,edit]
          When true, the UV sets are copied from the alternate object. C: Default is on.
    
      - vertexColor : vc               (bool)          [create,query,edit]
          When true, the colors per vertex are copied from the alternate object. C: Default is off.
    
      - vertices : v                   (bool)          [create,query,edit]
          When true, the vertices positions are copied from the alternate object. C: Default is off.                  Common flags
    
    
    Derived from mel command `maya.cmds.polyTransfer`
    """

    pass


def circle(*args, **kwargs):
    """
    The circle command creates a circle or partial circle (arc)
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - center : c                     (float, float, float) [create,query,edit]
          The center point of the circle.
    
      - centerX : cx                   (float)         [create,query,edit]
          X of the center point. Default:0
    
      - centerY : cy                   (float)         [create,query,edit]
          Y of the center point. Default:0
    
      - centerZ : cz                   (float)         [create,query,edit]
          Z of the center point. Default:0
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting circle: 1 - linear, 3 - cubic Default:3
    
      - first : fp                     (float, float, float) [create,query,edit]
          The start point of the circle if fixCenter is false. Determines the orientation of the circle if fixCenter is true.
    
      - firstPointX : fpx              (float)         [create,query,edit]
          X of the first point. Default:1
    
      - firstPointY : fpy              (float)         [create,query,edit]
          Y of the first point. Default:0
    
      - firstPointZ : fpz              (float)         [create,query,edit]
          Z of the first point. Default:0
    
      - fixCenter : fc                 (bool)          [create,query,edit]
          Fix the center of the circle to the specified center point. Otherwise the circle will start at the specified first
          point. Default:true
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - normal : nr                    (float, float, float) [create,query,edit]
          The normal of the plane in which the circle will lie.
    
      - normalX : nrx                  (float)         [create,query,edit]
          X of the normal direction. Default:0
    
      - normalY : nry                  (float)         [create,query,edit]
          Y of the normal direction. Default:0
    
      - normalZ : nrz                  (float)         [create,query,edit]
          Z of the normal direction. Default:1
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.                  Advanced flags
    
      - radius : r                     (float)         [create,query,edit]
          The radius of the circle. Default:1.0
    
      - sections : s                   (int)           [create,query,edit]
          The number of sections determines the resolution of the circle. Used only if useTolerance is false. Default:8
    
      - sweep : sw                     (float)         [create,query,edit]
          The sweep angle determines the completeness of the circle. A full circle is 2Pi radians, or 360 degrees.
          Default:6.2831853
    
      - tolerance : tol                (float)         [create,query,edit]
          The tolerance with which to build a circle. Used only if useTolerance is true Default:0.01
    
      - useTolerance : ut              (bool)          [create,query,edit]
          Use the specified tolerance to determine resolution. Otherwise number of sections will be used. Default:false
          Common flags
    
    
    Derived from mel command `maya.cmds.circle`
    """

    pass


def constructionHistory(*args, **kwargs):
    """
    This command turns construction history on or off.               In query mode, return type is based on queried flag.
    
    Flags:
      - toggle : tgl                   (bool)          [create,query]
          Turns construction history on or off.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.constructionHistory`
    """

    pass


def polySubdivideFacet(*args, **kwargs):
    """
    Subdivides a face into quads or triangles. In quad mode, a center point is introduced at the center of each face and
    midpoints are inserted on all the edges of each face. New faces (all quadrilaterals) are built by adding edges from the
    midpoints towards the center. In triangle mode, only the center point is created; new faces (all triangles) are created
    by connecting the center point to all the existing vertices of the face. Default : one subdivision step in quad mode
    (polySubdFacet -dv 1 -m 0;)
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - divisions : dv                 (int)           [create,query,edit]
          This number specifies how many times to recursively subdivide the selected faces. For example, with divisions set to 3
          in quad mode, each initial quadrilateral will be recursively subdivided into 4 subfaces 3 times, yielding a total of 4
          \* 4 \* 4 = 64 faces. C: Default is 1. Q: When queried, this flag returns an int.
    
      - divisionsU : duv               (int)           []
    
      - divisionsV : dvv               (int)           []
    
      - frozen : fzn                   (bool)          []
    
      - mode : m                       (int)           [create,query,edit]
          The subdivision mode. 0: subdivision into quads 1: subdivision into triangles C: Default is 0. Q: When queried, this
          flag returns an int.                  Common flags
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - subdMethod : sbm               (int)           []
    
    
    Derived from mel command `maya.cmds.polySubdivideFacet`
    """

    pass


def unfold(*args, **kwargs):
    """
    None
    
    Flags:
      - applyToShell : applyToShell    (bool)          [create]
          Specifies that the selected components should be only work on shells that have something have been selected or pinned.
    
      - areaWeight : aw                (float)         [create]
          Surface driven importance. 0 treat all faces equal. 1 gives more importance to large ones.
    
      - globalBlend : gb               (float)         [create]
          This allows the user to blend between a local optimization method (globalBlend = 0.0) and a global optimization method
          (globalBlend = 1.0). The local optimization method looks at the ratio between the triangles on the object and the
          triangles in UV space.  It has a side affect that it can sometimes introduce tapering problems.  The global optimization
          is much slower, but takes into consideration the entire object when optimizing uv placement.
    
      - globalMethodBlend : gmb        (float)         [create]
          The global optimization method uses two functions to compute a minimization.  The first function controls edge stretch
          by using edges lengths between xyz and uv.  The second function penalizes the first function by preventing
          configurations where triangles would overlap.  For every surface there is a mix between these two functions that will
          give the appropriate response. Values closer to 1.0 give more weight to the edge length function. Values closer to 0.0
          give more weight to surface area.  The default value of '0.5' is a even mix between these two values.
    
      - iterations : i                 (int)           [create]
          Maximum number of iterations for each connected UV piece.
    
      - optimizeAxis : oa              (int)           [create]
          Degree of freedom for optimization 0=Optimize freely, 1=Move vertically only, 2=Move horzontally only
    
      - pinSelected : ps               (bool)          [create]
          Specifies that the selected components should be pinned instead the unselected components.
    
      - pinUvBorder : pub              (bool)          [create]
          Specifies that the UV border should be pinned when doing the solve. By default only unselected components are pinned.
    
      - scale : s                      (float)         [create]
          Ratio between 2d and 3d space.
    
      - stoppingThreshold : ss         (float)         [create]
          Minimum distorsion improvement between two steps in %.
    
      - useScale : us                  (bool)          [create]
          Adjust the scale or not.                                   Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.unfold`
    """

    pass


def polyBevel(*args, **kwargs):
    """
    Bevel edges.
    
    Flags:
      - angleTolerance : at            (float)         [create,query,edit]
          This flag specifies the angle beyond which additional faces may be inserted to avoid possible twisting of faces. If the
          bevel produces unwanted faces, try increasing the angle tolerance. C: Default is 5 degrees. Q: When queried, this flag
          returns a double.
    
      - autoFit : af                   (bool)          [create,query,edit]
          Computes a smooth roundness, new faces round off a smooth angle. C: Default is on. Q: When queried, this flag returns an
          int.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - fillNgons : fn                 (bool)          []
    
      - fraction : f                   (float)         []
    
      - frozen : fzn                   (bool)          []
    
      - maya2015 : m15                 (bool)          []
    
      - mergeVertexTolerance : mvt     (float)         []
    
      - mergeVertices : mv             (bool)          []
    
      - miteringAngle : ma             (float)         []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - offset : o                     (float)         [create,query,edit]
          This flag specifies the offset distance for the beveling. C: Default is 0.2. Q: When queried, this flag returns a float.
    
      - offsetAsFraction : oaf         (bool)          [create,query,edit]
          This flag specifies whether the offset is a fraction or an absolute value. If a fraction, the offset can range between 0
          and 1, where 1 is the maximum possible offset C: Default is false. Q: When queried, this flag returns an int.
    
      - roundness : r                  (float)         [create,query,edit]
          This flag specifies the roundness of bevel. A roundness of 0 means that all new faces are coplanar. This value is only
          used if the autoFit value is off. C: Default is 0.5. Q: When queried, this flag returns a float.
    
      - segments : sg                  (int)           [create,query,edit]
          This flag specifies the number of segments used for the beveling. C: Default is 1. Q: When queried, this flag returns an
          int.
    
      - smoothingAngle : sa            (float)         []
    
      - useLegacyBevelAlgorithm : com  (bool)          []
    
      - uvAssignment : ua              (int)           []
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flags specifies the used reference. If on : the offset flag is taken in world reference. If off : the offset flag
          is taken in object reference (the default). C: Default is off. Q: When queried, this flag returns an int. Common
          flagsCommon flags
    
    
    Derived from mel command `maya.cmds.polyBevel`
    """

    pass


def rebuildSurface(*args, **kwargs):
    """
    This command rebuilds a surface by modifying its parameterization. In some cases the shape of the surface may also
    change. The rebuildType (-rt) attribute determines how the surface is rebuilt. The optional second surface can be used
    to specify a reference parameterization.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degreeU : du                   (int)           [create,query,edit]
          The degree of the resulting surface in the u direction 0 - maintain current, 1 - linear, 2 - quadratic, 3 - cubic, 5 -
          quintic, 7 - heptic Default:3
    
      - degreeV : dv                   (int)           [create,query,edit]
          The degree of the resulting surface in the v direction 0 - maintain current, 1 - linear, 2 - quadratic, 3 - cubic, 5 -
          quintic, 7 - heptic Default:3
    
      - direction : dir                (int)           [create,query,edit]
          The direction in which to rebuild: 0 - U, 1 - V, 2 - Both U and V Default:2
    
      - endKnots : end                 (int)           [create,query,edit]
          End conditions for the surface 0 - uniform end knots, 1 - multiple end knots, Default:0
    
      - fitRebuild : fr                (int)           [create,query,edit]
          Specify the type of rebuild method to be used: 0 - Convert Classic, the default and original convert method. 1 - Fit
          using the least squares fit method. 2 - Convert Match, alternate matching convert method. 3 - Convert Grid, uses a grid-
          based fit algorithm. Default:0
    
      - frozen : fzn                   (bool)          []
    
      - keepControlPoints : kcp        (bool)          [create,query,edit]
          Use the control points of the input surface. This forces uniform parameterization unless rebuildType is 2 (match knots)
          Default:false
    
      - keepCorners : kc               (bool)          [create,query,edit]
          The corners of the resulting surface will not change from the corners of the input surface. Default:true
    
      - keepRange : kr                 (int)           [create,query,edit]
          Determine the parameterization for the resulting surface. 0 - reparameterize the resulting surface from 0 to 1; 1 - keep
          the original surface parameterization; 2 - reparameterize the result from 0 to number of spans Default:1
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - noChanges : nc                 (bool)          []
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)
    
      - rebuildType : rt               (int)           [create,query,edit]
          The rebuild type: 0 - uniform, 1 - reduce spans, 2 - match knots, 3 - remove multiple knots, 4 - force non rational 5 -
          rebuild ends 6 - trim convert (uniform) 7 - into Bezier mesh Default:0
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - spansU : su                    (int)           [create,query,edit]
          The number of spans in the u direction in resulting surface. Used only when rebuildType is 0 - uniform. If 0, keep the
          same number of spans as the original surface. Default:4
    
      - spansV : sv                    (int)           [create,query,edit]
          The number of spans in the v direction in resulting surface. Used only when rebuildType is 0 - uniform. If 0, keep the
          same number of spans as the original surface. Default:4
    
      - tolerance : tol                (float)         [create,query,edit]
          The tolerance with which to rebuild Default:0.01                  Common flags
    
    
    Derived from mel command `maya.cmds.rebuildSurface`
    """

    pass


def singleProfileBirailSurface(*args, **kwargs):
    """
    This cmd creates a railed surface by sweeping the profile curve along the two rail curves. One of the requirements for
    surface creation is the profile curve must intersect the two rail curves. If the profile is a surface curve i.e.
    isoparm, curve on surface or trimmed edge then tangent continuity across the surface underlying the profile may be
    enabled using the flag -tp1 true. The first argument represetns the profile curve, the second and third the rails.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)Advanced flags
    
      - tangentContinuityProfile1 : tp1 (bool)          [create,query,edit]
          Need to be tangent continuous across the profile. The profile must be a surface curve. Default:false
    
      - transformMode : tm             (int)           [create,query,edit]
          transform mode ( Non proportional, proportional ). Non proportional is default value. Default:0                  Common
          flags
    
    
    Derived from mel command `maya.cmds.singleProfileBirailSurface`
    """

    pass


def subdTransferUVsToCache(*args, **kwargs):
    """
    The subdivision surface finer level uvs will get copied to the polygonToSubd node sent in as argument. The command takes
    a single subdivision surface and a single polygonToSubd node as input. Additional inputs will be ignored. Please note
    that this command is an internal command and is to be used with care, directly by the user
    
    
    Derived from mel command `maya.cmds.subdTransferUVsToCache`
    """

    pass


def polyExtrudeFacet(*args, **kwargs):
    """
    Extrude faces. Faces can be extruded separately or together, and manipulations can be performed either in world or
    object space.
    
    Flags:
      - attraction : att               (float)         [create,query,edit]
          This flag specifies the attraction, related to magnet. C: Default is 0.0. The range is [-2.0, 2.0]. Q: When queried,
          this flag returns a float.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createCurve : cc               (bool)          []
    
      - divisions : d                  (int)           [create,query,edit]
          This flag specifies the number of subdivisions. C: Default is 1 Q: When queried, this flag returns an int.
    
      - frozen : fzn                   (bool)          []
    
      - gain : ga                      (float)         []
    
      - gravity : g                    (float, float, float) [create,query,edit]
          This flag specifies the gravity vector. C: Default is 0.0 -1.0 0.0. Q: When queried, this flag returns a float[3].
    
      - gravityX : gx                  (float)         [create,query,edit]
          This flag specifies X for the gravity vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - gravityY : gy                  (float)         [create,query,edit]
          This flag specifies Y for the gravity vector. C: Default is -1.0. Q: When queried, this flag returns a float.
    
      - gravityZ : gz                  (float)         [create,query,edit]
          This flag specifies Z for the gravity vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - inputCurve : inc               (PyNode)        [create]
          This flag specifies the name of the curve to be used as input for extrusion C: The selected faces will be extruded along
          the curve. It will be useful to set a higher value (greater than 4) for the '-d/-divisions' flag, to get good results.
          The normal of the surface has to be aligned with the direction of the curve.  The extrusion is evenly distributed in the
          curve's parameter space, and not on the curve's geometry space
    
      - keepFacesTogether : kft        (bool)          [create,query,edit]
          This flag specifies how to extrude faces. If on, faces are pulled together (connected ones stay connected and only
          outside edges form new faces), otherwise they are pulled independently (each edge on selected faces creates a new face
          and manipulations are performed on each selected face separately). C: Default is on. Q: When queried, this flag returns
          an int.
    
      - keepFacetTogether : xft        (bool)          []
    
      - localCenter : lc               (int)           []
    
      - localDirection : ld            (float, float, float) [create,query,edit]
          This flag specifies the local slant axis (see local rotation). C: Default is 0.0 0.0 1.0. Q: When queried, this flag
          returns a float[3].
    
      - localDirectionX : ldx          (float)         [create,query,edit]
          This flag specifies X for the local slant axis. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localDirectionY : ldy          (float)         [create,query,edit]
          This flag specifies Y for the local slant axis. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localDirectionZ : ldz          (float)         [create,query,edit]
          This flag specifies Z for the local slant axis. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localRotate : lr               (float, float, float) [create,query,edit]
          This flag specifies the local rotations : (slantRot, slantRoll, twistRot). C: Default is 0.0 0.0 0.0. Q: When queried,
          this flag returns a float[3]. Local rotation (slantRot, slantRoll, twistRot).
    
      - localRotateX : lrx             (float)         [create,query,edit]
          This flag specifies local rotation X angle (Slant Rot around slantAxis). C: Default is 0.0. The range is [0, 360]. Q:
          When queried, this flag returns a float.
    
      - localRotateY : lry             (float)         [create,query,edit]
          This flag specifies local rotation Y angle (Slant Roll of slantAxis). C: Default is 0.0. The range is [0, 180]. Q: When
          queried, this flag returns a float.
    
      - localRotateZ : lrz             (float)         [create,query,edit]
          This flag specifies local rotation Z angle (Twist around normal). C: Default is 0.0. The range is [0, 360]. Q: When
          queried, this flag returns a float.
    
      - localScale : ls                (float, float, float) [create,query,edit]
          This flag specifies the local scaling vector. C: Default is 1.0 1.0 1.0. Q: When queried, this flag returns a float[3].
    
      - localScaleX : lsx              (float)         [create,query,edit]
          This flag specifies X for local scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localScaleY : lsy              (float)         [create,query,edit]
          This flag specifies Y for local scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localScaleZ : lsz              (float)         [create,query,edit]
          This flag specifies Z for local scaling vector : Flattening. C: Default is 1.0. The range is [0.0, 1.0]. Q: When
          queried, this flag returns a float. Dynamic Values
    
      - localTranslate : lt            (float, float, float) [create,query,edit]
          This flag specifies the local translation vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - localTranslateX : ltx          (float)         [create,query,edit]
          This flag specifies the X local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localTranslateY : lty          (float)         [create,query,edit]
          This flag specifies the Y local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localTranslateZ : ltz          (float)         [create,query,edit]
          This flag specifies the Z local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - magnX : mx                     (float)         [create,query,edit]
          This flag specifies X for the magnet vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - magnY : my                     (float)         [create,query,edit]
          This flag specifies Y for the magnet vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - magnZ : mz                     (float)         []
    
      - magnet : m                     (float, float, float) [create,query,edit]
          This flag specifies the magnet vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - maya2012 : m12                 (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - offset : off                   (float)         [create,query,edit]
          This flag specifies the local offset. Each edge of each selected face moves towards the inside of the face by given
          distance (in local reference). C: Default is 0.0.
    
      - pivot : pvt                    (float, float, float) [create,query,edit]
          This flag specifies the pivot for scaling and rotation. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - pivotX : pvx                   (float)         [create,query,edit]
          This flag specifies the X pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotY : pvy                   (float)         [create,query,edit]
          This flag specifies the Y pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotZ : pvz                   (float)         [create,query,edit]
          This flag specifies the Z pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
          Local Values
    
      - random : ran                   (float)         [create,query,edit]
          This flag specifies the random value for all parameters. C: Default is 0.0. The range is [-10.0, 10.0]. Q: When queried,
          this flag returns a float.
    
      - rotate : ro                    (float, float, float) [create,query,edit]
          This flag specifies the rotation angles around X, Y, Z. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - rotateX : rx                   (float)         [create,query,edit]
          This flag specifies the rotation angle around X. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateY : ry                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Y. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateZ : rz                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Z. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - scale : s                      (float, float, float) [create,query,edit]
          This flag specifies the scaling vector. C: Default is 1.0 1.0 1.0. Q: When queried, this flag returns a float[3].
    
      - scaleX : sx                    (float)         [create,query,edit]
          This flag specifies X for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleY : sy                    (float)         [create,query,edit]
          This flag specifies Y for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleZ : sz                    (float)         [create,query,edit]
          This flag specifies Z for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - smoothingAngle : sma           (float)         [create,query,edit]
          This flag specifies smoothingAngle threshold used to determine whether newly created edges are hard or soft. C: Default
          is 30.0. The range is [0, 180]. Q: When queried, this flag returns a float. Global Values
    
      - taper : tp                     (float)         []
    
      - taperCurve_FloatValue : cfv    (float)         []
    
      - taperCurve_Interp : ci         (int)           []
    
      - taperCurve_Position : cp       (float)         []
    
      - thickness : tk                 (float)         []
    
      - translate : t                  (float, float, float) [create,query,edit]
          This flag specifies the translation vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - translateX : tx                (float)         [create,query,edit]
          This flag specifies the X translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateY : ty                (float)         [create,query,edit]
          This flag specifies the Y translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateZ : tz                (float)         [create,query,edit]
          This flag specifies the Z translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - twist : twt                    (float)         []
    
      - weight : w                     (float)         [create,query,edit]
          This flag specifies the weight, related to gravity. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyExtrudeFacet`
    """

    pass


def polyCylinder(*args, **kwargs):
    """
    The cylinder command creates a new polygonal cylinder.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the cylinder. Q: When queried, this flag returns a float[3].
    
      - caching : cch                  (bool)          [query,edit]
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (int)           [create]
          This flag alows a specific UV mechanism to be selected, while creating the primitive. The valid values are 0, 1,  2 or
          3. 0 implies that no UVs will be generated (No texture to be applied). 1 implies UVs should be created for the object as
          a whole without any normalization. The primitive will be unwrapped and then the texture will be applied without any
          distortion. In the unwrapped primitive, the shared edges will have shared UVs. 2 implies the UVs should be normalized.
          This will normalize the U and V direction separately, thereby resulting in distortion of textures. 3 implies UVs are
          created so that the texture will not be distorted when applied. The texture lying outside the UV range will be truncated
          (since that cannot be squeezed in, without distorting the texture. For better understanding of these options, you may
          have to open the texture view windowC: Default is 2.
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - height : h                     (float)         [create,query,edit]
          This flag specifies the height of the cylinder. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - radius : r                     (float)         [create,query,edit]
          This flag specifies the radius of the cylinder. C: Default is 0.5. Q: When queried, this flag returns a float.
    
      - roundCap : rcp                 (bool)          [query,edit]
    
      - subdivisionsAxis : sa          (int)           [query,edit]
    
      - subdivisionsCaps : sc          (int)           [query,edit]
    
      - subdivisionsHeight : sh        (int)           [query,edit]
    
      - subdivisionsX : sx             (int)           [create,query,edit]
          This specifies the number of subdivisions in the X direction for the cylinder. C: Default is 20. Q: When queried, this
          flag returns an int.
    
      - subdivisionsY : sy             (int)           [create,query,edit]
          This flag specifies the number of subdivisions in the Y direction for the cylinder. C: Default is 1. Q: When queried,
          this flag returns an int.
    
      - subdivisionsZ : sz             (int)           [create,query,edit]
          This flag specifies the number of subdivisions in the Z direction for the cylinder. C: Default is 1. Q: When queried,
          this flag returns an int.
    
      - texture : tx                   (int)           [create]
          This flag is obsolete and will be removed in the next release. The -cuv/createUVs flag should be used instead.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyCylinder`
    """

    pass


def polyLayoutUV(*args, **kwargs):
    """
    Move UVs in the texture plane to avoid overlaps.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - flipReversed : fr              (bool)          [create,query,edit]
          If this flag is turned on, the reversed UV pieces are fliped.
    
      - frozen : fzn                   (bool)          []
    
      - gridU : gu                     (int)           []
    
      - gridV : gv                     (int)           []
    
      - layout : l                     (int)           [create,query,edit]
          How to move the UV pieces, after cuts are applied: 0 No move is applied. 1 Layout the pieces along the U axis. 2 Layout
          the pieces in a square shape.
    
      - layoutMethod : lm              (int)           [create,query,edit]
          Which layout method to use: 0 Block Stacking. 1 Shape Stacking.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - percentageSpace : ps           (float)         [create,query,edit]
          When layout is set to square, this value is a percentage of the texture area which is added around each UV piece. It can
          be used to ensure each UV piece uses different pixels in the texture. Maximum value is 5 percent.
    
      - rotateForBestFit : rbf         (int)           [create,query,edit]
          0 No rotation is applied. 1 Only allow 90 degree rotations. 2 Allow free rotations.
    
      - scale : sc                     (int)           [create,query,edit]
          How to scale the pieces, after move and cuts: 0 No scale is applied. 1 Uniform scale to fit in unit square. 2 Non
          proportional scale to fit in unit square.
    
      - separate : se                  (int)           [create,query,edit]
          Which UV edges should be cut: 0 No cuts. 1 Cut only along folds. 2 Make all necessary cuts to avoid all intersections.
    
      - uvSetName : uvs                (unicode)       [create,query]
          Specifies the name of the uv set to edit uvs on. If not specified will use the current uv set if it exists.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          If true, performs the operation in world space coordinates as opposed to local space.                  Common flags
    
    
    Derived from mel command `maya.cmds.polyLayoutUV`
    """

    pass


def polyMoveFacetUV(*args, **kwargs):
    """
    Modifies the map by moving all UV values associated with the selected face(s). The UV coordinates of the model are
    manipulated without changing the vertices of the 3D object.
    
    Flags:
      - axisLen : l                    (float, float)  [create,query,edit]
          Axis Length vector, used to draw the manip handles. C: Default is 1.0, 1.0 Q: When queried, this flag returns a
          float[2].
    
      - axisLenX : lx                  (float)         [create,query,edit]
          Axis Length in X, used to draw the manip handles. C: Default is 1.0 Q: When queried, this flag returns a float.
    
      - axisLenY : ly                  (float)         [create,query,edit]
          Axis Length in Y, used to draw the manip handles. C: Default is 1.0 Q: When queried, this flag returns a float.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - pivot : pvt                    (float, float)  [create,query,edit]
          This flag specifies the pivot for scaling and rotation. C: Default is 0.0 0.0. Q: When queried, this flag returns a
          float[2].
    
      - pivotU : pvu                   (float)         [create,query,edit]
          This flag specifies U for the pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a
          float.
    
      - pivotV : pvv                   (float)         [create,query,edit]
          This flag specifies V for the pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a
          float.
    
      - random : ran                   (float)         [create,query,edit]
          This flag specifies the random value for all parameters. C: Default is 0.0. The range is [-10.0, 10.0]. Q: When queried,
          this flag returns a float.
    
      - rotationAngle : ra             (float)         [create,query,edit]
          Angle of rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - scale : s                      (float, float)  [create,query,edit]
          This flag specifies the scaling vector. C: Default is 1.0 1.0. Q: When queried, this flag returns a float.
    
      - scaleU : su                    (float)         [create,query,edit]
          This flag specifies U for the scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleV : sv                    (float)         [create,query,edit]
          This flag specifies V for the scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - translate : t                  (float, float)  [create,query,edit]
          This flag specifies the translation vector. C: Default is 0.0 0.0. Q: When queried, this flag returns a float[2].
    
      - translateU : tu                (float)         [create,query,edit]
          This flag specifies the U translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateV : tv                (float)         [create,query,edit]
          This flag specifies the V translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyMoveFacetUV`
    """

    pass


def nurbsCurveToBezier(*args, **kwargs):
    """
    The nurbsCurveToBezier command attempts to convert an existing NURBS curve to a Bezier curve.
    
    
    Derived from mel command `maya.cmds.nurbsCurveToBezier`
    """

    pass


def changeSubdivComponentDisplayLevel(*args, **kwargs):
    """
    Explicitly forces the subdivision surface to display components at a particular level of refinement.
    
    Flags:
      - level : l                      (int)           [create,query]
          Specifies the display level of components.
    
      - relative : r                   (bool)          [create,query]
          If set, level refers to the relative display level                                 Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.changeSubdivComponentDisplayLevel`
    """

    pass


def polyBlindData(*args, **kwargs):
    """
    Command creates blindData types (basically creates an instance of TdnPolyBlindData). When used with the query flag, it
    returns the data types that define this blindData type. This command is to be used create a blindData node \*and\* to
    edit the same.. The associationType flag \*has\* to be specified at all times.. This is because if an instance of the
    specified BD typeId exists in the history chain but if the associationType is not the same, then a new polyBlindData
    node is created.. For object level blind data, only the object itself must be specified. A new compound attribute
    BlindDataNNNN will be created on the object. Blind data attribute names must be unique across types for object level
    blind data. So, the command will require the following to be specified:     - typeId,     - associationType     -
    longDataName or shortDataName of data being edited.     - The actual data being specified.     - The components that
    this data is to be attached to.
    
    Flags:
      - associationType : at           (unicode)       [create,edit]
          Specifies the dataTypes that are part of BlindData node being created. Allowable associations are objectfor any object,
          and vertexedgeand facefor mesh objects. Other associations for other geometry types may be added.
    
      - binaryData : bnd               (unicode)       [create,edit]
          Specifies the data type is a binary data value
    
      - booleanData : bd               (bool)          [create,edit]
          Specifies the data type is a boolean logic value
    
      - delete : delete                (bool)          [create,edit]
          Specifies that this will remove the blind data if found
    
      - doubleData : dbd               (float)         [create,edit]
          Specifies the data type is a floating point double value
    
      - int64Data : lid                (int)           [create,edit]
          Specifies the data type is an 64-bit integer value
    
      - intData : ind                  (int)           [create,edit]
          Specifies the data type is an integer value
    
      - longDataName : ldn             (unicode)       [create,edit]
          Specifies the long name of the data that is being modified by this command.
    
      - rescan : res                   (bool)          [create,edit]
          Enables a rescan of blind data nodes for cached information
    
      - reset : rst                    (bool)          [create,edit]
          Specifies that this command will reset the given attribute to default value
    
      - shape : sh                     (bool)          [create,edit]
          For object association only, apply blind data to the shape(s) below this node instead of the node itself
    
      - shortDataName : sdn            (unicode)       [create,edit]
          Specifies the short name of the data that is being modified by this command.
    
      - stringData : sd                (unicode)       [create,edit]
          Specifies the data type is a string value
    
      - typeId : id                    (int)           [create,edit]
          Specifies the typeId of the BlindData type being created                                   Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyBlindData`
    """

    pass


def filletCurve(*args, **kwargs):
    """
    The curve fillet command creates a fillet curve between two curves. If no objects are specified in the command line,
    then the first two active curves are used. The fillet created can be circular (with a radius) or freeform (with a type
    of tangent or blend).
    
    Flags:
      - bias : b                       (float)         [create,query,edit]
          Adjusting the bias value causes the fillet curve to be skewed to one of the input curves. Available only if blendControl
          is true. Default:0.0
    
      - blendControl : bc              (bool)          [create,query,edit]
          If true then depth and bias can be controlled. Otherwise, depth and bias are not available options. Default:false
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - circular : cir                 (bool)          [create,query,edit]
          Curve fillet will be created as circular if true or freeform if false. Default:true
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curveParameter1 : cp1          (float)         [create,query,edit]
          Parameter where fillet curve will contact the primary input curve. Default:0.0
    
      - curveParameter2 : cp2          (float)         [create,query,edit]
          Parameter where fillet curve will contact the secondary input curve. Default:0.0
    
      - depth : d                      (float)         [create,query,edit]
          Adjusts the depth of the fillet curve. Available only if blendControl is true. Default:0.5
    
      - freeformBlend : fb             (bool)          [create,query,edit]
          The freeform type is blend if true or tangent if false. Available if the fillet type is freeform. Default:false
    
      - frozen : fzn                   (bool)          []
    
      - join : jn                      (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - radius : r                     (float)         [create,query,edit]
          The radius if creating a circular fillet. Default:1.0                  Common flags
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - trim : t                       (bool)          []
    
    
    Derived from mel command `maya.cmds.filletCurve`
    """

    pass


def doubleProfileBirailSurface(*args, **kwargs):
    """
    The arguments are 4 cuves called profile1profile2rail1rail2. This command builds a railed surface by sweeping profile
    profile1along the two given rail curves rail1, rail2until profile2is reached. By using the -blend control, the railed
    surface creation could be biased more towards one of the two profile curves. The curves ( both profiles and rails )
    could also be surface curves ( isoparams, curve on surfaces ). If the profile curves are surface curves the surface
    constructed could be made tangent continuous to the surfaces underlying the profiles using the flags -tp1, -tp2
    respectively. Current Limitation: Its necessary that the two profile curves intersect the rail curves for successful
    surface creation.
    
    Flags:
      - blendFactor : bl               (float)         [create,query,edit]
          A blend factor applied in between the two profiles. The amount of influence 'inputProfile1' has in the surface creation.
          Default:0.5
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)Advanced flags
    
      - tangentContinuityProfile1 : tp1 (bool)          [create,query,edit]
          Need tangent continuity across the input profile at inputProfile1. Default:false
    
      - tangentContinuityProfile2 : tp2 (bool)          [create,query,edit]
          Need tangent continuity across the input curve at inputProfile2. Default:false
    
      - transformMode : tm             (int)           [create,query,edit]
          transform mode ( Non proportional, proportional ). Non proportional is default value. Default:0                  Common
          flags
    
    
    Derived from mel command `maya.cmds.doubleProfileBirailSurface`
    """

    pass


def showMetadata(*args, **kwargs):
    """
    This command is used to show metadata values which is in the specified channels vertex, edge, face, and vertexFacein the
    viewport. You can view the data by three ways: color: draw color on the components. ray: draw a ray on the components.
    string: draw 2d strings on the components. For example, if the metadata of shape.vtx[1]is (1, 0, 0), you can turn on the
    visualization with all three modes. On colormode, you can see a red vertex which is on the position of shape.vtx[1]. On
    raymode, you can see a ray with the direction (1, 0, 0). On stringmode, you can see strings 1 0 0below the vertex in the
    viewport.  To use coloror raymode, you should make the member of the data structure with three or less items, such as
    float[3]. The three items are mapped to RGBas a color, or XYZas a vector. The structure with two items works similarly.
    The only difference is that the third value will always be zero. However, if the structure has only one item, the value
    is mapped to all three variables. That means if the structure is intand its value is 1, the color will be white(1, 1, 1)
    and the vector will be (1, 1, 1).  You can get the current status of the flags on the query mode (using -query). But you
    can query only the status of one flag in a single command and you cannot set values on the query mode.  You can use the
    command on some specified objects, or run it with no arguments to make changes on all objects in the scene. The object
    must be a mesh shape. Components are not allowed as the command arguments.
    
    Flags:
      - auto : a                       (bool)          [create,query]
          Similar to the flag -range, but uses the min/max value from the metadata in the same stream and member instead of the
          specified input value. In query mode, you can use the flag to query if autois on.
    
      - dataType : dt                  (unicode)       [create,query]
          In create mode, when used with the flags streamand member, specify a member to show. If the flag offis used, specify the
          member to turn off. In query mode, when used with the flags streamand member, query the visualization state of the
          specified member. Only one member of each shape can be visualized at a time. In query mode, this flag can accept a
          value.
    
      - interpolation : i              (bool)          [create,query]
          In create mode, enable/disable interpolation for colormethod. When interpolation is on, the components will be displayed
          in the interpolated color, which is computed by averaging their metadata values. In query mode, query the current state
          of interpolation flag of the selected objects.
    
      - isActivated : ia               (bool)          [create,query]
          Used to check if the given stream is activated. If some shapes are selected, query their states. If no shape is
          selected, query the states of all shapes in the scene.
    
      - listAllStreams : las           (bool)          [create,query]
          Used with object names to list all streams of the specified objects. no matter if they are visible in the viewport. Or
          you can use the flag individually to list all streams in the scene. Due to the fact that different objects may have the
          same stream name, the returned list will merge the duplicated stream names automatically.
    
      - listMembers : lm               (bool)          [create,query]
          Used with the flag 'stream' to get the member list in the specified stream.
    
      - listValidMethods : lvm         (bool)          [create,query]
          List the valid visual methods that can be set for the current stream and member. Some data type cannot be displayed by
          some methods. For example, if the data type is string, it cannot be displayed by coloror by ray. In other words, only
          the method stringwill be returned when you list the methods.
    
      - listVisibleStreams : lvs       (bool)          [create,query]
          Used with object names to list the name of the current visible streams of the specified object. Or you can use the flag
          with no object name to list all visible streams in the scene.
    
      - member : mb                    (unicode)       [create,query]
          In create mode, when used with the flags streamand dataType, specify a member to show. If the flag offis on, specify the
          member to turn off. In query mode, when used with the flags streamand dataType, query the visualization state of the
          specified member. Only one member of each shape can be visualized at a time. In query mode, this flag can accept a
          value.
    
      - method : m                     (unicode)       [create,query]
          Determine the method of visualization: colorconvert metadata to a color value and draw the components with the color
          rayconvert metadata to a vector and draw this vector line which starts from the center of the component stringdisplay
          the metadata through 2d string beside the component in the viewport The argument must be a string and must be one of the
          three words. The default method is color. If the data type is string, you can only show it with stringmethod. In query
          mode, you can use the flag with no arguments to query the method of a specified stream and member.
    
      - off : boolean                  (In create mode, turn off the member which is specified
    by the flags) [create,query]
          stream, memberand dataType.
    
      - range : r                      (float, float)  [create,query]
          Specify the range of data to use. The value which is out of the range will be clamped to the min/max value. If the
          method of visualization is color, the range will be mapped to the color. That means the min value will be displayed in
          black while the max value will be in white. In query mode, you can use the flag individually to query the current range.
    
      - rayScale : rs                  (float)         [create,query]
          Specify the scale of the ray to display it with a proper length.
    
      - stream : s                     (unicode)       [create,query]
          In create mode, when used with the flags memberand dataType, specify a member to show. If the flag offis used, specify
          the member to turn off. In query mode, when used with the flags memberand dataType, query the visualization state of the
          specified member. When used with the flag listMembers, query the members in the specified stream. Only one member of
          each shape can be visualized at a time. In query mode, this flag can accept a value.Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.showMetadata`
    """

    pass


def nurbsToPoly(*args, **kwargs):
    """
    This command tesselates a NURBS surface and produces a polygonal surface. The name of the new polygonal surface is
    returned. If construction history is ON, then the name of the new dependency node is returned as well.
    
    Flags:
      - caching : cch                  (bool)          []
    
      - chordHeight : cht              (float)         [query,edit]
          Chord height is the absolute distance in OBJECT space which the center of a polygon edge can deviate from the actual
          center of the surface span. Only used if Format is General and if useChordHeight is true. Default:0.1
    
      - chordHeightRatio : chr         (float)         [query,edit]
          Chord height ratio is the ratio of the chord length of a surface span to the chord height.  (This is a length to height
          ratio). 0 is a very loose fit. 1 is a very tight fit. (See also description of chord height.) Always used if Format is
          Standard Fit.  Otherwise, only used if Format is General and useChordHeightRatio is true. Default:0.9
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curvatureTolerance : cvt       (int)           []
    
      - delta : d                      (float)         [query,edit]
          3D delta. Only used if Format is Standard Fit. Default:0.1
    
      - edgeSwap : es                  (bool)          [query,edit]
          Edge swap.  This attribute enables an algorithm which determines the optimal method with which to tessellate a
          quadrilateral into triangles. Only used if Format is General. Default:false
    
      - explicitTessellationAttributes : eta (bool)          []
    
      - format : f                     (int)           [query,edit]
          Format: 0 - Triangle Count, 1 - Standard Fit, 2 - General, 3 - CVs Default:1
    
      - fractionalTolerance : ft       (float)         [query,edit]
          Fractional tolerance. Only used if Format is Standard Fit. Default:0.01
    
      - frozen : fzn                   (bool)          []
    
      - matchNormalDir : mnd           (bool)          [query,edit]
          Only used when the format is CVs.  Order the cvs so that the normal matches the direction of the original surface if set
          to true. Default:false
    
      - matchRenderTessellation : mrt  (bool)          []
    
      - minEdgeLength : mel            (float)         [query,edit]
          Minimal edge length. Only used if Format is Standard Fit. Default:0.001
    
      - name : n                       (unicode)       [create]
          Name the resulting object.
    
      - nodeState : nds                (int)           []
    
      - normalizeTrimmedUVRange : ntr  (bool)          [query,edit]
          This attribute is only applicable when a trimmed NURBS surface is used as the input surface. When true, the UV texture
          coordinates on the trimmed input surface are normalized and applied to the output surface as they are for the untrimmed
          version of the input surface. (The texture coordinates on the entire untrimmed surface are mapped to the entire output
          surface.) When false, the UV texture coordinates on the trimmed input surface are applied to the output surface as they
          are for the trimmed input surface.  (Only the texture coordinates visible on the trimmed input surface are mapped to the
          output surface.) Default:true
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
      - polygonCount : pc              (int)           [query,edit]
          The number of polygons to produce. Only used if Format is Triangle Count. Default:200
    
      - polygonType : pt               (int)           [query,edit]
          Polygon type: 0 - Triangles, 1 - Quads Default:0
    
      - smoothEdge : ues               (bool)          []
    
      - smoothEdgeRatio : esr          (float)         []
    
      - uDivisionsFactor : nuf         (float)         []
    
      - uNumber : un                   (int)           [query,edit]
          Initial number of isoparms in U.  Used in conjunction with the uType attribute. Only used if Format is General.
          Default:3
    
      - uType : ut                     (int)           [query,edit]
          Initial U type tessellation criteria (3 types). Type 0 - Per surface # of isoparms in 3D.  This type places a specific
          number of iso-parametric subdivision lines across the surface, equally spaced in 3D space. Type 1 - Per surface # of
          isoparms.  This type places a specific number of iso-parametric subdivision lines across the surface, equally spaced in
          parameter space. Type 2 - Per span # of isoparms.  This type places a specific number of iso-parametric subdivision
          lines across each surface span, equally spaced in parameter space. (This is the closest option to the Alias Studio
          tessellation parameters.) This attribute is only used if Format is General. Default:3
    
      - useChordHeight : uch           (bool)          [query,edit]
          True means use chord height. Only used if Format is General. Default:false
    
      - useChordHeightRatio : ucr      (bool)          [query,edit]
          True means use chord height ratio. Default:true
    
      - useSurfaceShader : uss         (bool)          []
    
      - vDivisionsFactor : nvf         (float)         []
    
      - vNumber : vn                   (int)           [query,edit]
          Initial number of isoparms in V.  Used in conjunction with the vType attribute. Only used if Format is General.
          Default:3
    
      - vType : vt                     (int)           [query,edit]
          Initial V type tessellation criteria (3 types). See description for the uType attribute. Only used if Format is General.
          Default:3                  Common flags
    
    
    Derived from mel command `maya.cmds.nurbsToPoly`
    """

    pass


def nurbsSelect(*args, **kwargs):
    """
    Performs selection operations on NURBS objects.If any of the border flags is set, then the appropriate borders are
    selected. Otherwise the current CV selection is used, or all CVs if the surfaces is selected as an object.The
    growSelection, shrinkSelection, borderSelection flags are then applied in that order.In practice, it is recommended to
    use one flag at a time, except for the border flags.
    
    Flags:
      - borderSelection : bs           (bool)          [create]
          Extract the border of the current CV selection.
    
      - bottomBorder : bb              (bool)          [create]
          Selects the bottom border of the surface (V=0).
    
      - growSelection : gs             (int)           [create]
          Grows the CV selection by the given number of CV
    
      - leftBorder : lb                (bool)          [create]
          Selects the left border of the surface (U=0).
    
      - rightBorder : rb               (bool)          [create]
          Selects the right border of the surface (U=MAX).
    
      - shrinkSelection : ss           (int)           [create]
          Shrinks the CV selection by the given number of CV
    
      - topBorder : tb                 (bool)          [create]
          Selects the top border of the patches (V=MAX).                             Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.nurbsSelect`
    """

    pass


def polySeparate(*args, **kwargs):
    """
    This command creates new objects from the given poly. A new object will be created for each section of the mesh that is
    distinct (no edges connect it to the rest of the mesh). This command can only separate one object at a time.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - endFace : ef                   (int)           []
    
      - frozen : fzn                   (bool)          []
    
      - inPlace : inp                  (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node (where applicable).                  Common flags
    
      - removeShells : rs              (bool)          []
    
      - separateSpecificShell : sss    (int)           []
    
      - startFace : sf                 (int)           []
    
      - userSpecifiedShells : uss      (bool)          []
    
    
    Derived from mel command `maya.cmds.polySeparate`
    """

    pass


def polyAverageNormal(*args, **kwargs):
    """
    Set normals of vertices or vertex-faces to an average value when the vertices within a given threshold. First, it sorts
    out the containing edges, and set them to be soft, if it is possible, so to let the normals appear to be merged. The
    remained components then are sorted into lumps where vertices in each lump are within the given threshold. For all
    vertices and vertex-faces, set their normals to the average normal in the lump. Selected vertices may or may not on the
    same object. If objects are selected, it is assumed that all vertices are selected. If edges or faces are selected, it
    is assumed that the related vertex-faces are selected.
    
    Flags:
      - allowZeroNormal : azn          (bool)          [create]
          Specifies whether to allow zero normals to be created. By default it is false. If it is false, replaceNormal is needed.
    
      - distance : d                   (float)         [create]
          Specifies the distance threshold. All vertices within the threshold are considered when computing an average normal. By
          default it is 0.0.
    
      - postnormalize : pon            (bool)          [create]
          Specifies whether to normalize the resulting normals. By default it is true.
    
      - prenormalize : prn             (bool)          [create]
          Specifies whether to normalize the normals before averaging. By default it is true.
    
      - replaceNormalXYZ : xyz         (float, float, float) [create]
          If the allowZeroNormalis false, this value is used to replace the zero normals. By default it is (1, 0, 0).
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyAverageNormal`
    """

    pass


def polyFlipEdge(*args, **kwargs):
    """
    Command to flip the edges shared by 2 adjacent triangles. When used with the edit flag, new edges can be added to the
    same node, instead of creating a separate node in the chain.
    
    
    Derived from mel command `maya.cmds.polyFlipEdge`
    """

    pass


def subdListComponentConversion(*args, **kwargs):
    """
    This command converts subdivision surface components from one or more types to another one or more types, and returns
    the list of the conversion. It doesn't change the currently selected objects. Use the -in/internalflag to specify
    conversion to connectedvs. containedcomponents.  For example, if the internal flag is specified when converting from
    subdivision surface vertices to faces, then only faces that are entirely contained by the vertices will be returned.  If
    the internal flag is not specified, then all faces that are connected to the vertices will be returned.
    
    Flags:
      - border : bo                    (bool)          [create]
          Convert to a border.
    
      - fromEdge : fe                  (bool)          [create]
          Indicates the component type to convert from: Edges
    
      - fromFace : ff                  (bool)          [create]
          Indicates the component type to convert from: Faces
    
      - fromUV : fuv                   (bool)          [create]
          Indicates the component type to convert from: UVs
    
      - fromVertex : fv                (bool)          [create]
          Indicates the component type to convert from: Vertex
    
      - internal : internal            (bool)          [create]
          Applicable when converting from smallercomponent types to larger ones. Specifies conversion to connectedvs.
          containedcomponents. See examples below.
    
      - toEdge : te                    (bool)          [create]
          Indicates the component type to convert to: Edges
    
      - toFace : tf                    (bool)          [create]
          Indicates the component type to convert to: Faces
    
      - toUV : tuv                     (bool)          [create]
          Indicates the component type to convert to: UVs
    
      - toVertex : tv                  (bool)          [create]
          Indicates the component type to convert to: Vertices
    
      - uvShell : uvs                  (bool)          [create]
          Will return uv components within the same UV shell.  Only works with flags -tuv and -fuv.
    
      - uvShellBorder : uvb            (bool)          [create]
          Will return uv components on the border within the same UV shell.  Only works with flags -tuv and -fuv.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.subdListComponentConversion`
    """

    pass


def arclen(*args, **kwargs):
    """
    This command returns the arclength of a curve if the history flag is not set (the default).  If the history flag is set,
    a node is created that can produce the arclength, and is connected and its name returned.  Having the construction
    history option on makes this command useful for expressions.
    
    Modifications:
      - returns a PyNode object for flags:  constructionHistory
    
    Flags:
      - caching : cch                  (bool)          []
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off (where applicable).                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       []
    
      - nodeState : nds                (int)           []
    
    
    Derived from mel command `maya.cmds.arclen`
    """

    pass


def nurbsToSubdivPref(*args, **kwargs):
    """
    This command sets the values used by the nurbs-to-subdivision surface preference.  This preference is used by the nurbs
    creation commands and is saved between Maya sessions. To query any of the flags, use the -queryflag. For more
    information on the flags, see the node documentation for the nurbsToSubdivProcnode. In query mode, return type is based
    on queried flag.
    
    Flags:
      - bridge : br                    (int)           [create,query]
          Valid values are 0, 1, 2 or 3.
    
      - capType : ct                   (int)           [create,query]
          Valid values are 0 or 1.
    
      - collapsePoles : cp             (bool)          [create,query]
    
      - matchPeriodic : mp             (bool)          [create,query]
    
      - maxPolyCount : mpc             (int)           [create,query]
    
      - offset : o                     (float)         [create,query]
    
      - reverseNormal : rn             (bool)          [create,query]
    
      - solidType : st                 (int)           [create,query]
          Valid values are 0, 1 or 2.
    
      - trans00 : t00                  (float)         [create,query]
    
      - trans01 : t01                  (float)         [create,query]
    
      - trans02 : t02                  (float)         [create,query]
    
      - trans10 : t10                  (float)         [create,query]
    
      - trans11 : t11                  (float)         [create,query]
    
      - trans12 : t12                  (float)         [create,query]
    
      - trans20 : t20                  (float)         [create,query]
    
      - trans21 : t21                  (float)         [create,query]
    
      - trans22 : t22                  (float)         [create,query]
    
      - trans30 : t30                  (float)         [create,query]
    
      - trans31 : t31                  (float)         [create,query]
    
      - trans32 : t32                  (float)         [create,query]
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.nurbsToSubdivPref`
    """

    pass


def polyPrism(*args, **kwargs):
    """
    The prism command creates a new polygonal prism.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the prism. Q: When queried, this flag returns a float[3].
    
      - caching : cch                  (bool)          [query,edit]
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (int)           [create]
          This flag alows a specific UV mechanism to be selected, while creating the primitive. The valid values are 0, 1,  2 or
          3. 0 implies that no UVs will be generated (No texture to be applied). 1 implies UVs should be created for the object as
          a whole without any normalization. The primitive will be unwrapped and then the texture will be applied without any
          distortion. In the unwrapped primitive, the shared edges will have shared UVs. 2 implies the UVs should be normalized.
          This will normalize the U and V direction separately, thereby resulting in distortion of textures. 3 implies UVs are
          created so that the texture will not be distorted when applied. The texture lying outside the UV range will be truncated
          (since that cannot be squeezed in, without distorting the texture. For better understanding of these options, you may
          have to open the texture view windowC: Default is 2.
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - length : l                     (float)         [create,query,edit]
          This flag specifies the length of the prism. C: Default is 2.0. Q: When queried, this flag returns a float.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - numberOfSides : ns             (int)           [create,query,edit]
          This specifies the number of sides for the prism. C: Default is 3. Q: When queried, this flag returns an int.
    
      - numderOfSides : nsi            (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - sideLength : w                 (float)         [create,query,edit]
          This flag specifies the edge length of the prism. C: Default is 2.0. Q: When queried, this flag returns a float.
    
      - subdivisionsCaps : sc          (int)           [create,query,edit]
          This flag specifies the subdivisions on the caps for the prism. C: Default is 2. Q: When queried, this flag returns an
          int.
    
      - subdivisionsHeight : sh        (int)           [create,query,edit]
          This specifies the subdivisions along the height for the prism. C: Default is 1. Q: When queried, this flag returns an
          int.
    
      - texture : tx                   (int)           [create]
          This flag is obsolete and will be removed in the next release. The -cuv/createUVs flag should be used instead.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyPrism`
    """

    pass


def circularFillet(*args, **kwargs):
    """
    The cmd is used to compute the rolling ball surface fillet ( circular fillet ) between two given NURBS surfaces. To
    generate trim curves on the surfaces, use -cos true.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curveOnSurface : cos           (bool)          [create]
          If possible, create 2D curve as a result.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.                  Advanced flags
    
      - positionTolerance : pt         (float)         [create,query,edit]
          C(0) Tolerance For Fillet Surface Default:0.01
    
      - primaryRadius : pr             (float)         [create,query,edit]
          primary Radius Default:1.0
    
      - secondaryRadius : sr           (float)         [create,query,edit]
          secondary Radius Default:1.0
    
      - tangentTolerance : tt          (float)         [create,query,edit]
          G(1) Tolerance For Fillet Surface Default:0.01                  Common flags
    
    
    Derived from mel command `maya.cmds.circularFillet`
    """

    pass


def polyCollapseEdge(*args, **kwargs):
    """
    Turns each selected edge into a point.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyCollapseEdge`
    """

    pass


def refineSubdivSelectionList(*args, **kwargs):
    """
    Refines a subdivision surface set of components based on the selection list. The selected components are subdivided. The
    selection list after the command is the newly created components at the finer subdivision level.
    
    
    Derived from mel command `maya.cmds.refineSubdivSelectionList`
    """

    pass


def polySelectConstraint(*args, **kwargs):
    """
    Changes the global polygonal selection constraints.              In query mode, return type is based on queried flag.
    
    Flags:
      - angle : a                      (int)           [create,query]
          0(off) 1(on).
    
      - anglePropagation : ap          (bool)          [create,query]
          If true, selection will be extended to all connected components whose normal is close to any of the normals of the
          original selection (see angleTolerance)
    
      - angleTolerance : at            (float)         [create,query]
          When angle propagation is turned on, this controls what is the maximum difference of the normal vectors where the
          selection propagates.
    
      - anglebound : ab                (float, float)  [create,query]
          min and max angles.  The given value should be in the current units that Maya is using.  See the examples for how to
          check the current unit. For vertices :    angle between the 2 edges owning the vertex. For edges :        angle between
          the 2 faces owning the edge.
    
      - border : bo                    (bool)          [create,query]
          If true, selection will be extended to all connected border components so that the whole loopis selected. It also
          removes all nonborder components from the existing selection (compatibility mode)
    
      - borderPropagation : bp         (bool)          [create,query]
          If true, selection will be extended to all connected border components so that the whole loopis selected.
    
      - convexity : c                  (int)           [create,query]
          0(off) 1(concave) 2(convex).
    
      - crease : cr                    (bool)          [create,query]
          If true, selection will be extended to all connected creased components.
    
      - disable : dis                  (bool)          [create]
          Toggles offall constraints for all component types, but leaves the other constraint parameters. This flag may be used
          together with other ones toggling some constraints on: if so, all constraints are disabled first (no matter the position
          of the -disable flag in the command line) then the specified ones are activated.
    
      - dist : d                       (int)           [create,query]
          0(off) 1(to point) 2(to axis) 3(to plane).
    
      - distaxis : da                  (float, float, float) [create,query]
          axis. (Normal to the plane in case of distance to plane).
    
      - distbound : db                 (float, float)  [create,query]
          min and max distances.
    
      - distpoint : dp                 (float, float, float) [create,query]
          point. (Axis/plane origin in case of distance to axis/plane).
    
      - edgeDistance : ed              (int)           [create]
          Maximum distance (number of edges) to extend the edge selection for Contiguous Edgespropagate mode. 0 means to ignore
          the distance constraint.
    
      - geometricarea : ga             (int)           [create,query]
          0(off) 1(on).
    
      - geometricareabound : gab       (float, float)  [create,query]
          min and max areas.
    
      - holes : h                      (int)           [create,query]
          0(off) 1(holed) 2(non holed).
    
      - length : l                     (int)           [create,query]
          0(off) 1(on).
    
      - lengthbound : lb               (float, float)  [create,query]
          min and max lengths.
    
      - loopPropagation : lp           (bool)          [create,query]
          If true, edge selection will be extended to a loop.
    
      - max2dAngle : m2a               (float)         [create]
          Maximum angle between two consecutive edges in the 2d tangent plane for Contiguous Edgespropagate mode.
    
      - max3dAngle : m3a               (float)         [create]
          Maximum angle between two consecutive edges in 3d space for Contiguous Edgespropagate mode.
    
      - mode : m                       (int)           [create,query]
          0(Off) 1(Next) 2(Current and Next) 3(All and Next). Off :             no constraints are used at all. Next :
          constraints will be used to filter next selections. Current and Next :    constraints will be aplied on current
          selection and then used to filter next selections. All and Next :        all items satisfying constraints are selected.
    
      - nonmanifold : nm               (int)           [create,query]
          0(off) 1(on)
    
      - oppositeEdges : oe             (bool)          []
    
      - order : order                  (int)           [create,query]
          0(off) 1(on).
    
      - orderbound : orb               (int, int)      [create,query]
          min and max orders. number of owning edges.
    
      - orient : o                     (int)           [create,query]
          0(off) 1(orientation) 2(direction).
    
      - orientaxis : oa                (float, float, float) [create,query]
          axis.
    
      - orientbound : ob               (float, float)  [create,query]
          min and max angles.  The given value should be in the current units that Maya is using.  See the examples for how to
          check the current unit.
    
      - planarity : p                  (int)           [create,query]
          0(off) 1(non planar) 2(planar).
    
      - propagate : pp                 (int)           [create,query]
          0(Off) 1(More) 2(Less) 3(Border) 4(Contiguous Edges). More :        will add current selection border to current
          selection. Less :        will remove current selection border from current selection. Border :    will keep only current
          selection border. Contiguous Edges :    Add edges aligned with the current edges selected. The direction and number of
          edges selected is controlled by the -m2a, -m3a, and -ed flags.
    
      - random : r                     (int)           [create,query]
          0(off) 1(on).
    
      - randomratio : rr               (float)         [create,query]
          ratio [0,1].
    
      - returnSelection : rs           (bool)          [create]
          If true, current selection will not be modified, instead the new selection will be returned as result.
    
      - ringPropagation : rp           (bool)          [create,query]
          If true, edge selection will be extended to a ring.
    
      - shell : sh                     (bool)          [create,query]
          If true, selection will be extended to all connected components so that the whole piece of object is selected.
    
      - size : sz                      (int)           [create,query]
          0(off) 1(triangles) 2(quads) 3(nsided).
    
      - smoothness : sm                (int)           [create,query]
          0(off) 1(hard) 2(smooth).
    
      - stateString : sts              (bool)          [query]
          Query only flag. Returns the MEL command that would restore all the current settings.
    
      - textured : tx                  (int)           [create,query]
          0(off) 1(mapped) 2(unmapped).
    
      - texturedarea : ta              (int)           [create,query]
          0(off) 1(Area specified is unsigned) 2(Area specified is signed).
    
      - texturedareabound : tab        (float, float)  [create,query]
          min and max areas.
    
      - textureshared : ts             (int)           [create,query]
          0(off) 1(on). This option will select any uvs on the currentMap which are shared by more than one vertex
    
      - topology : tp                  (int)           [create,query]
          0(off) 1(non triangulatable) 2(lamina) 3(non triangulatable and lamina)
    
      - type : t                       (int)           [create,query]
          0x0000(none) 0x0001(vertex) 0x8000(edge) 0x0008(face) 0x0010(texture coordinates)
    
      - uvShell : uv                   (bool)          [create,query]
          If true, selection will be extended to all connected components in UV space
    
      - visibility : v                 (int)           [create,query]
          0(off) 1(on).
    
      - visibilityangle : va           (float)         [create,query]
          angle [0,360].
    
      - visibilitypoint : vp           (float, float, float) [create,query]
          point.
    
      - where : w                      (int)           [create,query]
          0(off) 1(on border) 2(inside).
    
      - wholeSensitive : ws            (bool)          [create,query]
          Tells how to select faces : either by picking anywhere inside the face (if true) or by picking on the face center marker
          (if false).                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polySelectConstraint`
    """

    pass


def editMetadata(*args, **kwargs):
    """
    This command is used to set metadata elements onto or remove metadata elements from an object. Before using this command
    you must first attach a metadata stream type to the object using the addMetadatacommand or an API equivalent. The
    command has four basic variations: Set per-component metadata on meshesRemove per-component metadata on meshesSet
    generic metadata on any objectRemove generic metadata on any objectThe difference between the setand removevariations
    (1,3 vs. 2,4) is that setrequires both a member name to be set and a new value to be set. (The reason removal doesn't
    use a member name is that you can only remove an entire metadata structural element, you cannot remove only a single
    member from it.)  When metadata values are set or removed the action is performed on every selected component or index.
    This provides an easy method to set or remove a bunch of metadata en masse.  The general usage (variations 3, 4) lets
    you select specific pieces of metadata through the channelNameand indexflags. Note that since indexis a multi-use flag
    you can select many different elements from the same Channel and set or remove the metadata on all of them in one
    command.  Metadata on meshes is special in that the Channel types vertex, edge, face, and vertexFaceare directly
    connected to the components of the same name. To make setting these metadata Channels easier you can simply select or
    specify on the command line the corresponding components rather than using the channelNameand indexflags. For example
    the selection myMesh.vtx[8:10]corresponds to channelName = vertexand index = 8, 9, 10(as a multi-use flag).  Note that
    the metadata is assigned to an object and except in the special case of mesh geometry does not flow through the
    dependency graph. In meshes the metadata will move from node to node wherever the geometry is connected, although it
    will not adjust itself automatically for changes in topology. Internal data is arranged to minimize the amount of
    copying no matter how many other nodes are connected to it.  Only a single node or scene, component type, channel type,
    and value type are allowed in a single command. This keeps the data simple at the possible cost of requiring multiple
    calls to the command to set more than one structure member's value.  Certain nodes have metadata supplied by input
    attributes. If you edit one of those with an incoming connection on such an attribute then the metadata edit will not be
    applied directly it will be put into an 'editMetadata' node for application during DG evaluation. Since the details of
    the metadata are not known until the evaluation happens less rigorous compatibility checking is performed. The
    editMetadata node has its own facilities for verifying and reporting illegal metadata edits. Successive edits to the
    same metadata in this way appends each edit to the same editMetadata node.
    
    Flags:
      - channelName : cn               (unicode)       [create,query]
          Filter the metadata selection to only recognize metadata belonging to the specified named Channel (e.g. vertex). This
          flag is ignored if the components on the selection list are being used to specify the metadata of interest. In query
          mode, this flag can accept a value.
    
      - channelType : cht              (unicode)       [create,query]
          Obsolete - use the 'channelName' flag instead. In query mode, this flag can accept a value.
    
      - endIndex : eix                 (unicode)       [create]
          The metadata is stored in a Stream, which is an indexed list. If you have mesh components selected then the metadata
          indices are implicit in the list of selected components. If you select only the node or scene then this flag may be used
          in conjunction with the startIndexflag to specify a range of indices from which to retrieve the metadata. It is an error
          to have the value of startIndexbe greater than that of endIndex.  See also the indexflag for an alternate way to specify
          multiple indices. This flag can only be used on index types that support a range (e.g. integer values - it makes no
          sense to request a range between two strings)  In query mode, this flag can accept a value.
    
      - index : idx                    (unicode)       [create,query]
          In the typical case metadata is indexed using a simple integer value. Certain types of data may use other index types.
          e.g. a vertexFacecomponent will use a pairindex type, which is two integer values; one for the face ID of the component
          and the second for the vertex ID.  The indexflag takes a string, formatted in the way the specified indexTyperequires.
          All uses of the indexflag have the same indexType. If the type was not specified it is assumed to be a simple integer
          value.  In query mode, this flag can accept a value.
    
      - indexType : idt                (unicode)       [create,query]
          Name of the index type the new Channel should be using. If not specified this defaults to a simple integer index. Of the
          native types only a mesh vertexFacechannel is different, using a pairindex type. In query mode, this flag can accept a
          value.
    
      - memberName : mn                (unicode)       [create]
          Name of the Structure member being edited. The names of the members are set up in the Structure definition, either
          through the description passed in through the dataStructurecommand or via the API used to create that Structure.
    
      - remove : rem                   (bool)          [create]
          If the removeflag is set then the metadata will be removed rather than have values set. In this mode the memberName,
          value, and stringValueflags are ignored. memberNameis ignored because when deleting metadata all members of a structure
          must be removed as a group. The others are ignored since when deleting you don't need a value to be set.
    
      - scene : scn                    (bool)          [create,query]
          Use this flag when you want to add metadata to the scene as a whole rather than to any individual nodes. If you use this
          flag and have nodes selected the nodes will be ignored and a warning will be displayed.
    
      - startIndex : six               (unicode)       [create]
          The metadata is stored in a Stream, which is an indexed list. If you have mesh components selected then the metadata
          indices are implicit in the list of selected components. If you select only the node or scene then this flag may be used
          in conjunction with the endIndexflag to specify a range of indices from which to retrieve the metadata. It is an error
          to have the value of startIndexbe greater than that of endIndex.  See also the indexflag for an alternate way to specify
          multiple indices. This flag can only be used on index types that support a range (e.g. integer values - it makes no
          sense to request a range between two strings)  In query mode, this flag can accept a value.
    
      - streamName : stn               (unicode)       [create,query]
          Name of the metadata Stream. Depending on context it could be the name of a Stream to be created, or the name of the
          Stream to pass through the filter. In query mode, this flag can accept a value.Flag can have multiple arguments, passed
          either as a tuple or a list.
    
      - stringValue : sv               (unicode)       [create]
          String value to be set into the specified metadata locations. This flag can only be used when the data member is a
          numeric type. If the member has N dimensions (e.g. string[2]) then this flag must appear N times (e.g. 2 times) The same
          values are applied to the specified metadata member on all affected components or metadata indices. Only one of the
          value, and stringValue flags can be specified at once and the type must match the type of the structure member named by
          the memberflag.
    
      - value : v                      (float)         [create]
          Numeric value to be set into the specified metadata locations. This flag can only be used when the data member is a
          numeric type. If the member has N dimensions (e.g. float[3]) then this flag must appear N times (e.g. 3 times) The same
          values are applied to the specified metadata member on all affected components or metadata indices. All numeric member
          types should use this type of value specification, i.e. everything except string and matrix types. Only one of the
          value, and stringValue flags can be specified at once and the type must match the type of the structure member named by
          the memberflag.
    
    
    Derived from mel command `maya.cmds.editMetadata`
    """

    pass


def subdLayoutUV(*args, **kwargs):
    """
    Move UVs in the texture plane to avoid overlaps.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - flipReversed : fr              (bool)          [create,query,edit]
          If this flag is turned on, the reversed UV pieces are fliped.
    
      - frozen : fzn                   (bool)          []
    
      - layout : l                     (int)           [create,query,edit]
          How to move the UV pieces, after cuts are applied: 0 No move is applied. 1 Layout the pieces along the U axis. 2 Layout
          the pieces in a square shape.
    
      - layoutMethod : lm              (int)           [create,query,edit]
          Which layout method to use: 0 Block Stacking. 1 Shape Stacking.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - percentageSpace : ps           (float)         [create,query,edit]
          When layout is set to square, this value is a percentage of the texture area which is added around each UV piece. It can
          be used to ensure each UV piece uses different pixels in the texture. Maximum value is 5 percent.
    
      - rotateForBestFit : rbf         (int)           [create,query,edit]
          0 No rotation is applied. 1 Only allow 90 degree rotations. 2 Allow free rotations.
    
      - scale : sc                     (int)           [create,query,edit]
          How to scale the pieces, after move and cuts: 0 No scale is applied. 1 Uniform scale to fit in unit square. 2 Non
          proportional scale to fit in unit square.
    
      - separate : se                  (int)           [create,query,edit]
          Which UV edges should be cut: 0 No cuts. 1 Cut only along folds. 2 Make all necessary cuts to avoid all intersections.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          If true, performs the operation in world space coordinates as opposed to local space.                  Advanced flags
    
    
    Derived from mel command `maya.cmds.subdLayoutUV`
    """

    pass


def transferShadingSets(*args, **kwargs):
    """
    Command to transfer shading set assignments between meshes. The last mesh in the list receives the shading assignments
    from the other meshes.            In query mode, return type is based on queried flag.
    
    Flags:
      - sampleSpace : spa              (int)           [create,query,edit]
          Selects which space the attribute transfer is performed in. 0 is world space, 1 is model space. The default is world
          space.
    
      - searchMethod : sm              (int)           [create,query,edit]
          Specifies which search method to use when correlating points. 0 is closest along normal, 3 is closest to point. The
          default is closest to point.                                   Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.transferShadingSets`
    """

    pass


def polySplitVertex(*args, **kwargs):
    """
    Use this command to split one or more vertices.A mesh is made up of one or more faces.  The faces are defined by edges
    which connect vertices together.  Typically a face will share vertices and edges with adjacent faces in the same mesh.
    Sharing vertices and edges helps reduce the amount of memory used by a mesh.  It also ensures that when a face is moved,
    all the connected faces move together.Sometimes you may want to separate a face from its connected faces so that it may
    be moved in isolation.  There are three ways to accomplish this depending upon which parts of the face you want to
    extract:polySplitVertexsplit one or more vertices so that each face that shared the vertex acquires its own copy of the
    vertexpolySplitEdgesplit one or more edges so that each face that shared the vertex acquires its own copy of the
    edgepolyChipOffcompletely extract the face so that it has its own vertices and edgesNotice that the area of affect of
    each operation is different.  polySplitVertex will affect all the edges and faces that shared the vertex.  This is the
    broadest effect.  polySplitEdge will only affect the faces which shared the edge and polyChipOff will affect a specific
    face.  If we just count vertices to measure the effect of each command when splitting all components of a face, starting
    from a 3x3 plane which has 16 vertices and we were to split the middle face:polySplitVertex applied to the four vertices
    would end up creating 12 new verticespolySplitEdge applied to the four edges would end up creating 4 new
    verticespolyChipOff applied to the middle face would end up creating 4 new verticesNote that polySplitVertex may create
    non-manifold geometry as a part of this operation. You can use Polygons-Cleanup afterwards to to clean up any non-
    manifold geometry.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - worldSpace : ws                (bool)          []
          Not used by this command                  Common flags
    
    
    Derived from mel command `maya.cmds.polySplitVertex`
    """

    pass


def dataStructure(*args, **kwargs):
    """
    Takes in a description of the structure and creates it, adding it to the list of available data structures. The
    structure definition can either be supplied in the asStringflag or exist in a file that is referenced by the asFileflag.
    If the removeflag is specified with a nameflag then the data structure will be removed. This is to keep all structure
    operations in a single command rather than create separate commands to create, remove, and query the data structures.
    When you use the removeAllflag then every existing metadata structure is removed. Use with care! Note that removed
    structures may still be in use in metadata Streams after removal, they are just no longer available for the creation of
    new Streams.  Both the creation modes and the remove mode are undoable.  Creation of an exact duplicate of an existing
    structure (including name) will succeed silently without actually creating a new structure. Attempting to create a new
    non-duplicate structure with the same name as an existing structure will fail as there is no way to disambiguate two
    structures with the same name.  Querying modes are defined to show information both on the created structures and the
    structure serialization formats that have been registered. The serialization formats preserve the structure information
    as text (e.g. raw, XML, JSON). Since the rawstructure type is built in it will be assumed when none are specified.
    General query with no flags will return the list of names of all currently existing structures.  Querying the formatflag
    will return the list of all registered structure serialization formats.  Querying with the formatsupplied before the
    queryflag will show the detailed description of that particular structure serialization format.  Querying the
    asStringflag with a structure name and serialization format supplied before the queryflag will return a string
    representing the named data structure in the serialization format specified by the formatflag. Even if the format is the
    same as the one that created the structure the query return string may not be identical since the queried value is
    formatted in a standard way - original formatting is not preserved.  Querying the asFileflag with a structure name
    supplied before the queryflag will return the original file from which the structure was generated. If the structure was
    created using the asStringflag or through the API then an empty string will be returned.  Querying the nameflag returns
    the list of all structures created so far.
    
    Flags:
      - asFile : af                    (unicode)       [create,query]
          Specify a file that contains the serialized data which describes the structure.  The format of the data is specified by
          the 'format' flag.
    
      - asString : asString            (unicode)       [create,query]
          Specify the string containing the serialized data which describes the structure. The format of the data is specified by
          the 'format' flag.
    
      - dataType : dt                  (bool)          [create,query]
          Used with the flag 'listMemberNames' to query the type of the member. The type is appended after each relative member in
          the array. For example, if the format is name=idStructure:int32=id:string=namethe returned array is id int32 name
          string.
    
      - format : fmt                   (unicode)       [create,query]
          Format of data to expect in the structure description. rawis supported natively and will be assumed if the format type
          is omitted. Others are available via plug-in. You can query the available formats by using this flag in query mode. In
          query mode, this flag can accept a value.
    
      - listMemberNames : lmn          (unicode)       [create,query]
          Query the member names in the dataStructure. The member names will be returned in an array. The name of the data
          structure will not be returned. To get the type of each member, use 'dataType' together. Then the type of the member
          will be appended in the array after their relative member. For example, if the format is
          name=idStructure:int32=id:string=namethe returned array is id int32 name string.
    
      - name : n                       (unicode)       [query]
          Query mode only.  Name of the data structure to be queried, or set to list the available names. In query mode, this flag
          can accept a value.
    
      - remove : rem                   (bool)          [create]
          Remove the named data structure. It's an error if it doesn't exist.
    
      - removeAll : ral                (bool)          [create]
          Remove all metadata structures. This flag can not be used in conjunction with any other flags.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.dataStructure`
    """

    pass


def polyBoolOp(*args, **kwargs):
    """
    This command creates a new poly as the result of a boolean operation on input polys : union, intersection, difference.
    Only for difference, the order of the selected objects is important : result = object1 - object2. If no objects are
    specified in the command line, then the objects from the active list are used.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - classification : cls           (int)           []
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - faceAreaThreshold : fat        (float)         []
    
      - frozen : fzn                   (bool)          []
    
      - mergeUVSets : muv              (int)           []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node (where applicable).
    
      - operation : op                 (int)           [create]
          1=union, 2=difference, 3=intersection                  Common flags
    
      - preserveColor : pcr            (bool)          []
    
      - useThresholds : uth            (bool)          []
    
      - vertexDistanceThreshold : vdt  (float)         []
    
    
    Derived from mel command `maya.cmds.polyBoolOp`
    """

    pass


def polyDuplicateAndConnect(*args, **kwargs):
    """
    This command duplicates the input polygonal object, connects up the outMesh attribute of the original polygonal shape to
    the inMesh attribute of the newly created duplicate shape and copies over the shader assignments from the original shape
    to the new duplicated shape. The command will fail if no objects are selected or sent as argument or if the object sent
    as argument is not a polygonal object.
    
    Flags:
      - removeOriginalFromShaders : ros (bool)          [create]
          Used to specify if the original object should be removed from the shaders (shadingGroups) that it is a member of. The
          shader associations will get transferred to the duplicated object, before they are removed from the original. If this
          flag is specified then the original polygonal object will be drawn in wireframe mode even if all objects are being drawn
          in shaded mode.
    
      - renameChildren : rc            (bool)          [create]
          rename the children nodes of the hierarchy, to make them unique.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyDuplicateAndConnect`
    """

    pass


def polySphericalProjection(*args, **kwargs):
    """
    Projects a spherical map onto an object.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createNewMap : cm              (bool)          [create,query,edit]
          This flag when set true will create a new map with a the name passed in, if the map does not already exist.
    
      - frozen : fzn                   (bool)          []
    
      - imageCenter : ic               (float, float)  [create,query,edit]
          This flag specifies the center point of the 2D model layout. C: Default is 0.5 0.5. Q: When queried, this flag returns a
          float[2].
    
      - imageCenterX : icx             (float)         [create,query,edit]
          This flag specifies X for the center point of the 2D model layout. C: Default is 0.5. Q: When queried, this flag returns
          a float.
    
      - imageCenterY : icy             (float)         [create,query,edit]
          This flag specifies Y for the center point of the 2D model layout. C: Default is 0.5. Q: When queried, this flag returns
          a float.
    
      - imageScale : imageScale        (float, float)  [create,query,edit]
          This flag specifies the UV scale : Enlarges or reduces the 2D version of the model in U or V space relative to the 2D
          centerpoint. C: Default is 1.0 1.0. Q: When queried, this flag returns a float[2].
    
      - imageScaleU : isu              (float)         [create,query,edit]
          This flag specifies the U scale : Enlarges or reduces the 2D version of the model in U space relative to the 2D
          centerpoint. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - imageScaleV : isv              (float)         [create,query,edit]
          This flag specifies the V scale : Enlarges or reduces the 2D version of the model in V space relative to the 2D
          centerpoint. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - insertBeforeDeformers : ibd    (bool)          [create]
          This flag specifies if the projection node should be inserted before or after deformer nodes already applied to the
          shape. Inserting the projection after the deformer leads to texture swimming during animation and is most often
          undesirable. C: Default is on.
    
      - keepImageRatio : kir           (bool)          []
    
      - mapDirection : md              (unicode)       []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - perInstance : pi               (bool)          []
    
      - projectionCenter : pc          (float, float, float) [create,query,edit]
          This flag specifies the origin point from which the map is projected. C: Default is 0.0 0.0 0.0. Q: When queried, this
          flag returns a float[3].
    
      - projectionCenterX : pcx        (float)         [create,query,edit]
          This flag specifies X for the origin point from which the map is projected. C: Default is 0.0. Q: When queried, this
          flag returns a float.
    
      - projectionCenterY : pcy        (float)         [create,query,edit]
          This flag specifies Y for the origin point from which the map is projected. C: Default is 0.0. Q: When queried, this
          flag returns a float.
    
      - projectionCenterZ : pcz        (float)         [create,query,edit]
          This flag specifies Z for the origin point from which the map is projected. C: Default is 0.0. Q: When queried, this
          flag returns a float.
    
      - projectionHeight : ph          (float)         []
    
      - projectionHorizontalSweep : phs (float)         []
    
      - projectionScale : ps           (float, float)  [create,query,edit]
          This flag specifies the width and the height of the map relative to the 3D projection axis. C: Default is 180.0 90.0. Q:
          When queried, this flag returns a float[2].
    
      - projectionScaleU : psu         (float)         [create,query,edit]
          This flag specifies the width of the map relative to the 3D projection axis : the scale aperture. The range is [0, 360].
          C: Default is 180.0. Q: When queried, this flag returns a float.
    
      - projectionScaleV : psv         (float)         [create,query,edit]
          This flag specifies the height of the map relative to the 3D projection axis : the scale height. C: Default is 90.0. Q:
          When queried, this flag returns a float.
    
      - radius : r                     (float)         []
    
      - rotate : ro                    (float, float, float) [create,query,edit]
          This flag specifies the mapping rotate angles. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - rotateX : rx                   (float)         [create,query,edit]
          This flag specifies X mapping rotate angle. C: Default is 0.0. Q: When queried, this flag returns a float[3].
    
      - rotateY : ry                   (float)         [create,query,edit]
          This flag specifies Y mapping rotate angle. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateZ : rz                   (float)         [create,query,edit]
          This flag specifies Z mapping rotate angle. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotationAngle : ra             (float)         [create,query,edit]
          This flag specifies the rotation angle in the mapping space. When the angle is positive, then the map rotates
          counterclockwise on the mapped model, whereas when it is negative then the map rotates clockwise on the mapped model. C:
          Default is 10.0. Q: When queried, this flag returns a float.
    
      - seamCorrect : sc               (bool)          [create,query,edit]
          This flag specifies to perform a seam correction on the mapped faces.
    
      - smartFit : sf                  (bool)          [create]
          This flag specifies if the manipulator should be placed best fitting the object, or be placed on the specified position
          with the specified transformation values. Default is on.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on : all geometrical values are taken in world reference. If off : all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polySphericalProjection`
    """

    pass


def polySmooth(*args, **kwargs):
    """
    Smooth a polygonal object. This command works on polygonal objects or faces.
    
    Flags:
      - boundaryRule : bnr             (int)           []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - continuity : c                 (float)         [create,query,edit]
          This flag specifies the smoothness parameter. The minimum value of 0.0 specifies that the faces should only be
          subdivided. Maximum value of 1.0 smooths the faces as much as possible. C: Default is 1.0 Q: When queried, this flag
          returns a float.
    
      - degree : deg                   (int)           []
    
      - divisions : dv                 (int)           [create,query,edit]
          This flag specifies the number of recursive smoothing steps. C: Default is 1. Q: When queried, this flag returns an int.
    
      - divisionsPerEdge : dpe         (int)           []
    
      - frozen : fzn                   (bool)          []
    
      - keepBorder : kb                (bool)          [create,query,edit]
          If on, the border of the object will not move during smoothing operation. C: Default is on. Q: When queried, this flag
          returns an int.
    
      - keepHardEdge : khe             (bool)          [create,query,edit]
          If true, vertices on hard edges will not be modified. C: Default is false. Q: When queried, this flag returns a boolean.
    
      - keepMapBorders : kmb           (int)           []
    
      - keepSelectionBorder : ksb      (bool)          [create,query,edit]
          If true, vertices on border of the selection will not be modified. C: Default is false. Q: When queried, this flag
          returns a boolean.
    
      - keepTesselation : xkt          (bool)          []
    
      - keepTessellation : kt          (bool)          [create,query,edit]
          If true, the object will be tessellated consistently at each frame. If false, non-starlike faces will be triangulated
          before being subdivided, to avoid self-overlapping faces. C: Default is true. Q: When queried, this flag returns a
          boolean.
    
      - method : mth                   (int)           []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - osdCreaseMethod : ocr          (int)           [create,query,edit]
          Controls how boundary edges and vertices are interpolated.
    
      - osdFvarBoundary : ofb          (int)           [create,query,edit]
          Controls how boundaries are treated for face-varying data (UVs and Vertex Colors).
    
      - osdFvarPropagateCorners : ofc  (bool)          [create,query,edit]
    
      - osdSmoothTriangles : ost       (bool)          [create,query,edit]
          Apply a special subdivision rule be applied to all triangular faces that was empirically determined to make triangles
          subdivide more smoothly.
    
      - osdVertBoundary : ovb          (int)           [create,query,edit]
          Controls how boundary edges and vertices are interpolated.
    
      - propagateEdgeHardness : peh    (bool)          [create,query,edit]
          If true, edges which are a result of smoothed edges will be given the same value for their edge hardness.  New
          subdivided edges will always be smooth. C: Default is false. Q: When queried, this flag returns a boolean.
    
      - pushStrength : ps              (float)         []
    
      - roundness : ro                 (float)         []
    
      - smoothUVs : suv                (bool)          []
    
      - subdivisionLevels : sl         (int)           []
    
      - subdivisionType : sdt          (int)           [create,query,edit]
          The subdivision method used for smoothing. C: Default is 0. 0: Maya Catmull-Clark 1: OpenSubdiv Catmull-Clark
          Common flags
    
    
    Derived from mel command `maya.cmds.polySmooth`
    """

    pass


def polyNormal(*args, **kwargs):
    """
    Control the normals of an object. This command works on faces or polygonal objects.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - normalMode : nm                (int)           [create,query,edit]
          This flag specifies the normal mode. 0: reverse; (This flag is being phased out and is included for backwards
          compatibility only.) 1: propagate; (This flag is being phased out and is included for backwards compatibility only.) 2:
          conform; (This flag is being phased out and is included for backwards compatibility only.) 3: reverse and cut; Reverse
          the normal(s) on the selected face(s). Selected faces are cut along their collective border and a new shell is created.
          The normals in the new shell are reversed from what they were before the action. 4: reverse and propagate; Reverse the
          normal(s) on the selected face(s) and propagate this direction to all other faces in the shell. C: Default is 0 (reverse
          mode). Q: When queried, this flag returns an int.                  Common flags
    
      - userNormalMode : unm           (bool)          []
    
    
    Derived from mel command `maya.cmds.polyNormal`
    """

    pass


def smoothTangentSurface(*args, **kwargs):
    """
    The smoothTangentSurface command smooths the surface along an isoparm at each parameter value. The name of the surface
    is returned and if history is on, the name of the resulting dependency node is also returned. This command only applies
    to parameter values with a multiple knot value. (If the given parameter value has no multiple knot associated with it,
    then the dependency node is created but the surface doesn't change.) When would you use this?  If you have a surface
    consisting of a number of Bezier patches or any isoparms with more than a single knot multiplicity, you could get into a
    situation where a tangent break occurs.  So, it only makes sense to do this operation on the knot isoparms, and not
    anywhere in between, because the surface is already smooth everywhere in between. If you have a cubic or higher degree
    surface, asking for the maximal smoothness will give you tangent, curvature, etc. up to the degree-1 continuity.  Asking
    for tangent will just give you tangent continuity. It should be mentioned that this is C, not Gcontinuity we're talking
    about, so technically, you can still see visual tangent breaks if the surface is degenerate. Note: A single
    smoothTangentSurface command cannot smooth in both directions at once; you must use two separate commands to do this.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - direction : d                  (int)           [create,query,edit]
          Direction in which to smooth knot: 0 - V direction, 1 - U direction Default:1
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - parameter : p                  (float)         [create,query,edit]
          Parameter value(s) where knots are added Default:0.0
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - smoothness : s                 (int)           [create,query,edit]
          Smoothness to get: 0 - Tangent, 1 - Maximum (based on the degree) Default:1                  Common flags
    
    
    Derived from mel command `maya.cmds.smoothTangentSurface`
    """

    pass


def projectTangent(*args, **kwargs):
    """
    The project tangent command is used to align (for tangents) a curve to two other curves or a surface. A surface isoparm
    may be selected to define the direction (U or V) to align to. The end of the curve must intersect with these other
    objects. Curvature continuity may also be applied if required. Tangent continuity means the end of the curve is modified
    to be tangent at the point it meets the other objects. Curvature continuity means the end of the curve is modified to be
    curvature continuous as well as tangent. If the normal tangent direction is used, the curvature continuity and rotation
    do not apply. Also, curvature continuity is only available if align to a surface (not with 2 curves).
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curvature : c                  (bool)          [create,query,edit]
          Curvature continuity is on if true and off otherwise. Default:false
    
      - curvatureScale : cs            (float)         [create,query,edit]
          Curvature scale applied to curvature of curve to align. Available if curvature option is true. Default:0.0
    
      - frozen : fzn                   (bool)          []
    
      - ignoreEdges : ie               (bool)          [create,query,edit]
          If false, use the tangents of the trim edge curves if the surface is trimmed. If true, use the tangents of the
          underlying surface in the U/V directions. Default:false
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - reverseTangent : rt            (bool)          [create,query,edit]
          Reverse the tangent direction if true and leave it the way it is if false. Default:false
    
      - rotate : ro                    (float)         [create,query,edit]
          Amount by which the tangent of the curve to align will be rotated. Available only if the normal direction (3) is not
          used for tangentDirection. Default:0.0
    
      - tangentDirection : td          (int)           [create,query,edit]
          Tangent align direction type legal values: 1=u direction (of surface or use first curve), 2=v direction (of surface or
          use second curve), 3=normal direction (at point of intersection). Default:1
    
      - tangentScale : ts              (float)         [create,query,edit]
          Tangent scale applied to tangent of curve to align. Default:1.0                  Common flags
    
    
    Derived from mel command `maya.cmds.projectTangent`
    """

    pass


def nurbsPlane(*args, **kwargs):
    """
    The nurbsPlane command creates a new NURBS Plane and return the name of the new surface. It creates an unit plane with
    center at origin by default.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          The primitive's axis
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting surface 1 - linear, 2 - quadratic, 3 - cubic, 5 - quintic, 7 - heptic Default:3
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - lengthRatio : lr               (float)         [create,query,edit]
          The ratio of lengthto widthof the plane. Default:1.0
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - patchesU : u                   (int)           [create,query,edit]
          The number of spans in the U direction. Default:1
    
      - patchesV : v                   (int)           [create,query,edit]
          The number of spans in the V direction. Default:1
    
      - pivot : p                      (float, float, float) [create,query,edit]
          The primitive's pivot point
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)Advanced flags
    
      - width : w                      (float)         [create,query,edit]
          The width of the plane Default:1.0                  Common flags
    
    
    Derived from mel command `maya.cmds.nurbsPlane`
    """

    pass


def polyColorMod(*args, **kwargs):
    """
    Modifies the attributes of a poly color set.
    
    Flags:
      - alphaScale_FloatValue : afv    (float)         []
    
      - alphaScale_Interp : ai         (int)           []
    
      - alphaScale_Position : ap       (float)         []
    
      - baseColorName : bcn            (unicode)       [create]
          The name of the color set to be modified.
    
      - blueScale_FloatValue : bfv     (float)         []
    
      - blueScale_Interp : bi          (int)           []
    
      - blueScale_Position : bp        (float)         []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - greenScale_FloatValue : gfv    (float)         []
    
      - greenScale_Interp : gi         (int)           []
    
      - greenScale_Position : gp       (float)         []
    
      - huev : h                       (float)         [create]
          Rotates hue value of the final color.
    
      - intensityScale_FloatValue : nfv (float)         []
    
      - intensityScale_Interp : ni     (int)           []
    
      - intensityScale_Position : np   (float)         []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - redScale_FloatValue : rfv      (float)         []
    
      - redScale_Interp : ri           (int)           []
    
      - redScale_Position : rp         (float)         []
    
      - satv : s                       (float)         [create]
          scales the saturation of the final color.
    
      - value : v                      (float)         [create]
          Scales the final color value.                  Common flags
    
    
    Derived from mel command `maya.cmds.polyColorMod`
    """

    pass


def polyAverageVertex(*args, **kwargs):
    """
    Moves the selected vertices of a polygonal object to round its shape. Translate, move, rotate or scale vertices.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - iterations : i                 (int)           [create,query,edit]
          Number of rounding steps.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If true: all geometrical values are taken in world reference. If false: all
          geometrical values are taken in object reference. C: Default is false.                  Common flags
    
    
    Derived from mel command `maya.cmds.polyAverageVertex`
    """

    pass


def curveOnSurface(*args, **kwargs):
    """
    The curve-on-surface command creates a new curve-on-surface from a list of control vertices (CVs).  A string is returned
    containing the pathname to the newly created curve-on-surface. You can replace an existing curve by using the
    -r/replaceflag. You can append points to an existing curve-on-surface by using the -a/appendflag. See also the curve
    command, which describes how to query curve attributes.
    
    Flags:
      - append : a                     (bool)          [create]
          Appends point(s) to the end of an existing curve. If you use this flag, you must specify the name of the curve to append
          to, at the end of the command.  (See examples below.)
    
      - degree : d                     (float)         [create]
          The degree of the new curve.  Default is 3.  Note that you need degree+1 curve points to create a visible curve span,
          eg. you must place 4 points for a degree 3 curve.
    
      - knot : k                       (float)         [create]
          A knot value in a knot vector. One flag per knot value. There must be (numberOfPoints + degree - 1) knots and the knot
          vector must be non-decreasing.
    
      - name : n                       (unicode)       []
    
      - periodic : per                 (bool)          [create]
          If on, creates a curve that is periodic.  Default is off.
    
      - positionUV : uv                (float, float)  [create]
          The uv position of a point.
    
      - replace : r                    (bool)          [create]
          Replaces an entire existing curve. If you use this flag, you must specify the name of the curve to replace, at the end
          of the command.  (See examples below.)                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.curveOnSurface`
    """

    pass


def subdEditUV(*args, **kwargs):
    """
    Command edits uvs on subdivision surfaces. When used with the query flag, it returns the uv values associated with the
    specified components.
    
    Flags:
      - angle : a                      (float)         [create,query]
          Specifies the angle value (in degrees) that the uv values are to be rotated by.
    
      - pivotU : pu                    (float)         [create,query]
          Specifies the pivot value, in the u direction, about which the scale or rotate is to be performed.
    
      - pivotV : pv                    (float)         [create,query]
          Specifies the pivot value, in the v direction, about which the scale or rotate is to be performed.
    
      - relative : r                   (bool)          [create,query]
          Specifies whether this command is editing the values relative to the currently existing values. Default is true;
    
      - rotation : rot                 (bool)          [create,query]
          Specifies whether this command is editing the values with rotation values
    
      - scale : s                      (bool)          [create,query]
          Specifies whether this command is editing the values with scale values
    
      - scaleU : su                    (float)         [create,query]
          Specifies the scale value in the u direction.
    
      - scaleV : sv                    (float)         [create,query]
          Specifies the scale value in the v direction.
    
      - uValue : u                     (float)         [create,query]
          Specifies the value, in the u direction - absolute if relative flag is false..
    
      - uvSetName : uvs                (unicode)       [create,query]
          Specifies the name of the uv set to edit uvs on. If not specified will use the current uv set if it exists.
    
      - vValue : v                     (float)         [create,query]
          Specifies the value, in the v direction - absolute if relative flag is false..                             Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.subdEditUV`
    """

    pass


def curveIntersect(*args, **kwargs):
    """
    You must specify two curves to intersect. This command either returns the parameter values at which the given pair of
    curves intersect, or returns a dependency node that provides the intersection information. If you want to find the
    intersection of the curves in a specific direction you must use BOTH the -useDirectionflag and the directionflag.
    
    Flags:
      - caching : cch                  (bool)          []
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - direction : d                  (float, float, float) [query,edit]
          The direction that the input curves are projected in before intersecting.  This vector is only used if useDirectionflag
          is true.
    
      - directionX : dx                (float)         []
    
      - directionY : dy                (float)         []
    
      - directionZ : dz                (float)         []
    
      - frozen : fzn                   (bool)          []
    
      - nodeState : nds                (int)           []
    
      - tolerance : tol                (float)         [query,edit]
          The tolerance that the intersection is calculated with. For example, given two curves end-to-end, the ends must be
          within tolerance for an intersection to be returned. Default:0.001
    
      - useDirection : ud              (bool)          [query,edit]
          If true, use direction flag.  The input curves are first projected in a specified direction and then intersected. If
          false, this command will only find true 3D intersections. Default:false                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.curveIntersect`
    """

    pass


def textCurves(*args, **kwargs):
    """
    The textCurves command creates NURBS curves from a text string using the specified font. A single letter can be made up
    of more than one NURBS curve. The number of curves per letter varies with the font.
    
    Flags:
      - caching : cch                  (bool)          []
    
      - constructionHistory : ch       (bool)          []
    
      - deprecatedFontName : dfn       (bool)          []
    
      - font : f                       (unicode)       [create]
          The font to use.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           []
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - text : t                       (unicode)       [create]
          The string to create the curves for.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.textCurves`
    """

    pass


def polyTriangulate(*args, **kwargs):
    """
    Triangulation breaks polygons down into triangles, ensuring that all faces are planar and non-holed. Triangulation of
    models can be beneficial in many areas.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyTriangulate`
    """

    pass


def hardenPointCurve(*args, **kwargs):
    """
    The hardenPointCurve command changes the knots of a curve given a list of control point indices so that the knot
    corresponding to that control point gets the specified multiplicity.  Multiplicity of -1 is the universal value used for
    multiplicity equal to the degree of the curve.limitationsThe CV whose multiplicity is being raised needs to have its
    neighbouring CVs of multiplicity 1.  How many neighbours depends on the degree of the curve and the difference in CV
    multiplicities before and after this operation.  For example, if you're changing a CV of multiplicity 1 into a CV of
    multiplicity 3, you will need the 4 neighbouring CVs (2 on each side) to be of multiplicity 1.  The CVs that do not
    satisfy that requirement will be ignored.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - multiplicity : m               (int)           [create,query,edit]
          the required multiplicity of the curve knot Default:-1                  Common flags
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
    
    Derived from mel command `maya.cmds.hardenPointCurve`
    """

    pass


def stitchSurface(*args, **kwargs):
    """
    The stitchSurface command aligns two surfaces together to be G(0) and/or G(1) continuous by ajusting only the Control
    Vertices of the surfaces. The two surfaces can be stitched by specifying the two isoparm boundary edges that are to
    stitched together. The edge to which the two surfaces are stitched together is obtained by doing a weighted average of
    the two edges. The weights for the two edges is specified using the flags -wt0, -wt1 respectively.
    
    Flags:
      - bias : b                       (float)         [create,query,edit]
          Blend CVs in between input surface and result from stitch. A value of 0.0 returns the input surface. Default:1.0
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - cascade : c                    (bool)          [create]
          Cascade the created stitch node. (Only if the surface has a stitch history) Default is 'false'.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - cvIthIndex : ci                (int)           [create,query,edit]
          The ith boundary CV index on the input surface. Default:-1
    
      - cvJthIndex : cj                (int)           [create,query,edit]
          The jth boundary CV index on the input surface. Default:-1
    
      - fixBoundary : fb               (bool)          [create,query,edit]
          Fix Boundary CVs while solving for any G1 constraints. Default:false
    
      - frozen : fzn                   (bool)          []
    
      - keepG0Continuity : kg0         (bool)          [create]
          Stitch together with positional continuity. Default is 'true'.
    
      - keepG1Continuity : kg1         (bool)          [create]
          Stitch together with tangent continuity. Default is 'false'.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - numberOfSamples : ns           (int)           [create]
          The number of samples on the edge. Default is 20.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - parameterU : u                 (float)         [create,query,edit]
          The U parameter value on surface for a point constraint. Default:-10000
    
      - parameterV : v                 (float)         [create,query,edit]
          The V parameter value on surface for a point constraint. Default:-10000
    
      - positionalContinuity : pc      (bool)          [create,query,edit]
          Toggle on (off) G0 continuity at edge corresponding to multi index. Default:true
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).
    
      - stepCount : sc                 (int)           [create,query,edit]
          Step count for the number of discretizations. Default:20
    
      - tangentialContinuity : tc      (bool)          [create,query,edit]
          Toggle on (off) G1 continuity across edge corresponding to multi index. Default:false
    
      - togglePointNormals : tpn       (bool)          [create,query,edit]
          Toggle on (off) normal point constraints on the surface. Default:false
    
      - togglePointPosition : tpp      (bool)          [create,query,edit]
          Toggle on (off) position point constraints on the surface. Default:true
    
      - toggleTolerance : tt           (bool)          [create,query,edit]
          Toggle on (off) so as to use Tolerance or specified steps for discretization. Default:false
    
      - tolerance : tol                (float)         [create,query,edit]
          Tolerance to use while discretizing the edge. Default:0.1                  Common flags
    
      - weight0 : wt0                  (float)         [create]
          The weighting factor for the first edge. Default is 0.5.
    
      - weight1 : wt1                  (float)         [create]
          The weighting factor for the second edge. Default is 0.5.                  Advanced flags
    
    
    Derived from mel command `maya.cmds.stitchSurface`
    """

    pass


def polyCrease(*args, **kwargs):
    """
    Command to set the crease values on the edges or vertices of a poly.  The crease values are used by the smoothing
    algorithm.
    
    Flags:
      - createHistory : ch             (bool)          [create,query,edit]
          For objects that have no construction history, this flag can be used to force the creation of construction history for
          creasing.  By default, history is not created if the object has no history.  Regardless of this flag, history is always
          created if the object already has history.
    
      - operation : op                 (int)           [create,query,edit]
          Operation to perform.  Valid values are: 0: Crease the specified components. 1: Remove the crease values for the
          specified components. 2: Remove all crease values from the mesh. Default is 0.
    
      - relativeValue : rv             (float)         [create,query,edit]
          Specifies a new relative value for all selected vertex and edge components. This flag can not be used at the same time
          as either the value or vertexValue flags.
    
      - value : v                      (float)         [create,query,edit]
          Specifies the crease value for the selected edge components. When specified multiple times, the values are assigned
          respectively to the specified edges.
    
      - vertexValue : vv               (float)         [create,query,edit]
          Specifies the crease value for the selected vertex components. When specified multiple times, the values are assigned
          respectively to the specified vertices.                              Flag can have multiple arguments, passed either as
          a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyCrease`
    """

    pass


def polyMergeUV(*args, **kwargs):
    """
    Merge UVs of an object based on their distance. UVs are merge only if they belong to the same 3D vertex.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - distance : d                   (float)         [create,query,edit]
          This flag specifies the maximum distance to merge UVs. C: Default is 0.0. Q: When queried, this flag returns a double.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - uvSetName : uvs                (unicode)       [create,query]
          Specifies the name of the uv set to edit uvs on. If not specified will use the current uv set if it exists.
          Common flags
    
      - worldSpace : ws                (bool)          []
    
    
    Derived from mel command `maya.cmds.polyMergeUV`
    """

    pass


def polySelectConstraintMonitor(*args, **kwargs):
    """
    Manage the window to display/edit the polygonal selection constraint parameters
    
    Flags:
      - changeCommand : cc             (unicode, unicode) [create]
          Specifies the mel callback to refresh the window. First argument is the callback, second is the window name.
    
      - create : c                     (bool)          [create]
          Specifies the Monitor should be created
    
      - delete : d                     (bool)          [create]
          Specifies that the Monitor should be removed                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.polySelectConstraintMonitor`
    """

    pass


def polyCollapseTweaks(*args, **kwargs):
    """
    A command that updates a mesh's vertex tweaks by applying its tweak data (stored on the mesh node) onto its respective
    vertex data. This command is only useful in cases where no construction history is associated with the shape node. If a
    mesh name is not specified as input, a singly selected mesh (if any) will have its tweaked vertices baked. In query
    mode, return type is based on queried flag.
    
    Flags:
      - hasVertexTweaks : hvt          (bool)          [create,query]
          Determines whether an individual mesh has vertex tweaks.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyCollapseTweaks`
    """

    pass


def polyCBoolOp(*args, **kwargs):
    """
    This command creates a new poly as the result of a boolean operation on input polys : union, intersection, difference.
    Only for difference, the order of the selected objects is important : result = object1 - object2. If no objects are
    specified in the command line, then the objects from the active list are used.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - classification : cls           (int)           []
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - faceAreaThreshold : fat        (float)         []
    
      - frozen : fzn                   (bool)          []
    
      - mergeUVSets : muv              (int)           []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node (where applicable).
    
      - operation : op                 (int)           [create]
          1=union, 2=difference, 3=intersection                  Common flags
    
      - preserveColor : pcr            (bool)          []
    
      - useCarveBooleans : ucb         (bool)          []
    
      - useThresholds : uth            (bool)          []
    
      - vertexDistanceThreshold : vdt  (float)         []
    
    
    Derived from mel command `maya.cmds.polyCBoolOp`
    """

    pass


def untrim(*args, **kwargs):
    """
    Untrim the surface.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curveOnSurface : cos           (bool)          [create]
          If possible, create 2D curve as a result.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - noChanges : nc                 (bool)          [create,query,edit]
          If set then the operation node will be automatically put into pass-through mode.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).
    
      - untrimAll : all                (bool)          [query,edit]
          if true, untrim all the trims for the surface else untrim only the last trim                  Advanced flags
    
    
    Derived from mel command `maya.cmds.untrim`
    """

    pass


def insertKnotSurface(*args, **kwargs):
    """
    The insertKnotSurface command inserts knots (aka isoparms) into a surface given a list of parameter values.  The number
    of knots to add at each parameter value and whether the knots are added or complemented can be specified. The name of
    the surface is returned and if history is on, the name of the resulting dependency node is also returned. You must
    specify one, none or all number of knots with the -nkflag. eg. if you specify none, then the default (one) knot will be
    added at each specified parameter value.  If you specify one -nkvalue then that number of knots will be added at each
    parameter value. Otherwise, you must specify the same number of -nkflags as -pflags, defining the number of knots to be
    added at each specified parameter value. You can insert up to degreeknots at a parameter value that isn't already an
    isoparm.  eg. for a degree 3 surface, you can insert up to 3 knots. Use this operation if you need more CVs in a local
    area of the surface. Use this operation if you want to create a corner in the surface. Note: A single insertKnotSurface
    command cannot insert in both directions at once; you must use two separate commands to do this.
    
    Flags:
      - addKnots : add                 (bool)          [create,query,edit]
          Whether to add knots or complement.  Complement means knots will be added to reach the specified number of knots.
          Default:true
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - direction : d                  (int)           [create,query,edit]
          Direction in which to insert knot: 0 - V direction, 1 - U direction Default:1
    
      - frozen : fzn                   (bool)          []
    
      - insertBetween : ib             (bool)          [create,query,edit]
          If set to true, and there is more than one parameter value specified, the knots will get inserted at equally spaced
          intervals between the given parameter values, rather than at the parameter values themselves. Default:false
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - numberOfKnots : nk             (int)           [create,query,edit]
          How many knots to insert Default:1
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - parameter : p                  (float)         [create,query,edit]
          Parameter value(s) where knots are added Default:0.0                  Common flags
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
    
    Derived from mel command `maya.cmds.insertKnotSurface`
    """

    pass


def polyClipboard(*args, **kwargs):
    """
    The command allows the user to copy and paste certain polygonal attributes to a clipboard. These attributes are:  1)
    Shader (shading engine) assignment.  2) Texture coordinate (UV) assignment.  3) Color value assignment. Any combination
    of attributes can be chosen for the copy or paste operation. If the attribute has not been copied to the clipboard, then
    naturally it cannot be pasted from the clipboard. The copy option will copy the attribute assignments from a single
    source polygonal dag object or polygon component. If the source does not have the either UV or color attributes, then
    nothing will be copied to the clipboard. The paste option will paste the attribute assignments to one or more polygon
    components or polygonal dag objects. If the destination does not have either UV or color attributes, then new values
    will be assigned as needed. Additionally, there is the option to clear the clipboard contents
    
    Flags:
      - clear : cl                     (bool)          [create]
          When used, will mean to clear the specified attribute argument(s).
    
      - color : clr                    (bool)          [create]
          When used, will be to copy or paste color attributes
    
      - copy : cp                      (bool)          [create]
          When used, will mean to copy the specified attribute argument(s).
    
      - paste : ps                     (bool)          [create]
          When used, will mean to paste the specified attribute argument(s).
    
      - shader : sh                    (bool)          [create]
          When used, will be to copy or paste shader attributes
    
      - uvCoordinates : uv             (bool)          [create]
          When used, will be to copy or paste texture coordinate attributes                                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyClipboard`
    """

    pass


def polySphere(*args, **kwargs):
    """
    The sphere command creates a new polygonal sphere.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the sphere. Q: When queried, this flag returns a float[3].
    
      - caching : cch                  (bool)          [query,edit]
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (int)           [create]
          This flag alows a specific UV mechanism to be selected, while creating the sphere. The valid values are 0, 1, or 2. 0
          implies that no UVs will be generated (No texture to be applied). 1 implies UVs are created with pinched at poles 2
          implies UVs are created with sawtooth at poles For better understanding of these options, you may have to open the
          texture view windowC: Default is 2
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - radius : r                     (float)         [create,query,edit]
          This flag specifies the radius of the sphere. C: Default is 0.5. Q: When queried, this flag returns a float.
    
      - subdivisionsAxis : sa          (int)           [query,edit]
    
      - subdivisionsHeight : sh        (int)           [query,edit]
    
      - subdivisionsX : sx             (int)           [create,query,edit]
          This specifies the number of subdivisions in the X direction for the sphere. C: Default is 20. Q: When queried, this
          flag returns an int.
    
      - subdivisionsY : sy             (int)           [create,query,edit]
          This flag specifies the number of subdivisions in the Y direction for the sphere. C: Default is 20. Q: When queried,
          this flag returns an int.
    
      - texture : tx                   (int)           [create]
          This flag is obsolete and will be removed in the next release. The -cuv/createUVs flag should be used instead.
          Common flags
    
    
    Derived from mel command `maya.cmds.polySphere`
    """

    pass


def polyBlendColor(*args, **kwargs):
    """
    Takes two color sets and blends them together into a third specified color set.
    
    Flags:
      - baseColorName : bcn            (unicode)       [query,edit]
          Name of the color set to blend from
    
      - blendFunc : bfn                (int)           [query,edit]
          Type of blending function to use
    
      - blendWeightA : bwa             (float)         [query,edit]
          Blend weight for linear and bilinear blending functions
    
      - blendWeightB : bwb             (float)         [query,edit]
          Blend weight for bilinear and channel blending functions
    
      - blendWeightC : bwc             (float)         [query,edit]
          Blend weight for channel functions
    
      - blendWeightD : bwd             (float)         [query,edit]
          Blend weight for channel functions
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - dstColorName : dst             (unicode)       [query,edit]
          Name of the color set to copy to
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabled
    
      - srcColorName : src             (unicode)       [query,edit]
          Name of the color set to copy from                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.polyBlendColor`
    """

    pass


def polySplitRing(*args, **kwargs):
    """
    Splits a series of ring edges of connected quads and inserts connecting edges between them.
    
    Flags:
      - adjustEdgeFlow : aef           (float)         []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - direction : dr                 (bool)          [create]
          The direction to associate the absoluteWeights on the edge. By toggling the boolean value, the new edges can be
          positioned either to the start or the end vertex of the edge thats split. Default is on
    
      - divisions : div                (int)           [create]
          If the splitType is set to 2 then this is used to control how many new edge loops are inserted.  This number has to be
          at least 1.
    
      - enableProfileCurve : epc       (bool)          []
    
      - fixQuads : fq                  (bool)          []
    
      - frozen : fzn                   (bool)          []
    
      - insertWithEdgeFlow : ief       (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - profileCurveInputOffset : pio  (float)         []
    
      - profileCurveInputScale : pis   (float)         []
    
      - profileCurve_FloatValue : pfv  (float)         []
    
      - profileCurve_Interp : pi       (int)           []
    
      - profileCurve_Position : pp     (float)         []
    
      - rootEdge : re                  (int)           [create]
          The edge id of the object, to be used as a reference for the flags absoluteWeight and direction. Default is -1
    
      - smoothingAngle : sma           (float)         [create]
          Subdivide new edges will be soft if less then this angle. Default is 180.0
    
      - splitType : stp                (int)           [create]
          Choose between 3 different types of splits.  If this is set to 0 then the split type will be absolute.  This is where
          each of the splits will maintain an equal distance from the associated vertices.  If this set to 1 then the split type
          will be relative. This is where each split will be made at an equal percentage along the length of the edge.  If this is
          set to 2 then the edge will be split one or more times.  The number of times is controlled by the -div/-divisions flag.
          For an absolute or relative type of split the user can adjust the weight to position where the split occurrs.  If the
          split is a multi split then the splits will be spaced out evenly.
    
      - useEqualMultiplier : uem       (bool)          []
    
      - useFaceNormalsAtEnds : fne     (bool)          []
    
      - weight : wt                    (float)         [create]
          The weight value of the new vertex to be positioned at the first edge. The same weight value is used for all the edges
          split. Default is 0.5                  Common flags
    
      - worldSpace : ws                (bool)          []
    
    
    Derived from mel command `maya.cmds.polySplitRing`
    """

    pass


def polyEditUV(*args, **kwargs):
    """
    Command edits uvs on polygonal objects. When used with the query flag, it returns the uv values associated with the
    specified components.
    
    Flags:
      - angle : a                      (float)         [create,query]
          Specifies the angle value (in degrees) that the uv values are to be rotated by.
    
      - pivotU : pu                    (float)         [create,query]
          Specifies the pivot value, in the u direction, about which the scale or rotate is to be performed.
    
      - pivotV : pv                    (float)         [create,query]
          Specifies the pivot value, in the v direction, about which the scale or rotate is to be performed.
    
      - relative : r                   (bool)          [create,query]
          Specifies whether this command is editing the values relative to the currently existing values. Default is true;
    
      - rotation : rot                 (bool)          [create,query]
          Specifies whether this command is editing the values with rotation values
    
      - scale : s                      (bool)          [create,query]
          Specifies whether this command is editing the values with scale values
    
      - scaleU : su                    (float)         [create,query]
          Specifies the scale value in the u direction.
    
      - scaleV : sv                    (float)         [create,query]
          Specifies the scale value in the v direction.
    
      - uValue : u                     (float)         [create,query]
          Specifies the value, in the u direction - absolute if relative flag is false..
    
      - uvSetName : uvs                (unicode)       [create,query]
          Specifies the name of the uv set to edit uvs on. If not specified will use the current uv set if it exists.
    
      - vValue : v                     (float)         [create,query]
          Specifies the value, in the v direction - absolute if relative flag is false..                             Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyEditUV`
    """

    pass


def closeCurve(*args, **kwargs):
    """
    The closeCurve command closes a curve, making it periodic. The pathname to the newly closed curve and the name of the
    resulting dependency node are returned.  If a curve is not specified in the command, then the first active curve will be
    used.
    
    Flags:
      - blendBias : bb                 (float)         [create,query,edit]
          Skew the result toward the first or the second curve depending on the blend value being smaller or larger than 0.5.
          Default:0.5
    
      - blendKnotInsertion : bki       (bool)          [create,query,edit]
          If set to true, insert a knot in one of the original curves (relative position given by the parameter attribute below)
          in order to produce a slightly different effect. Default:false
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curveOnSurface : cos           (bool)          [create]
          If possible, create 2D curve as a result.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - parameter : p                  (float)         [create,query,edit]
          The parameter value for the positioning of the newly inserted knot. Default:0.1
    
      - preserveShape : ps             (int)           [create,query,edit]
          0 - without preserving the shape 1 - preserve shape 2 - blend Default:1                  Common flags
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
    
    Derived from mel command `maya.cmds.closeCurve`
    """

    pass


def trim(*args, **kwargs):
    """
    This command trims a surface to its curves on surface by first splitting the surface and then selecting which regions to
    keep or discard.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - locatorU : lu                  (float)         [create,query,edit]
          u parameter value to position a locator on the surface. Default:0.5
    
      - locatorV : lv                  (float)         [create,query,edit]
          v parameter value to position a locator on the surface. Default:0.5
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.                  Advanced flags
    
      - replaceOriginal : rpo          (bool)          []
    
      - selected : sl                  (int)           [create,query,edit]
          Specify whether to keep or discard selected regions. Default:0
    
      - shrink : sh                    (bool)          [create,query,edit]
          If true, shrink underlying surface to outer boundaries of trimmed surface. Default:false
    
      - tolerance : tol                (float)         [create,query,edit]
          The tolerance with which to trim. Default:0.001                  Common flags
    
    
    Derived from mel command `maya.cmds.trim`
    """

    pass


def polyColorBlindData(*args, **kwargs):
    """
    This command applies false color to the selected polygonal components and objects, depending on whether or not blind
    data exists for the selected components (or, in the case of poly objects, dynamic attributes), and, depending on the
    color mode indicated, what the values are. It is possible to color objects based on whether or not the data exists, if
    the data matches a specific value or range of values, or grayscale color the data according to what the actual value is
    in relation to the specified min and max. This command also has a query mode in which the components and/or objects are
    returned in a string array to allow for selection filtering.
    
    Flags:
      - aboveMaxColorBlue : amb        (float)         [create]
          Specifies blue component of color to use for data that is above max
    
      - aboveMaxColorGreen : amg       (float)         [create]
          Specifies green component of color to use for data that is above max
    
      - aboveMaxColorRed : amr         (float)         [create]
          Specifies red component of color to use for data that is above max
    
      - attrName : n                   (unicode)       [create]
          Specifies the name of the data that is being examined by this command.
    
      - belowMinColorBlue : bmb        (float)         [create]
          Specifies blue component of color to use for data that is below min
    
      - belowMinColorGreen : bmg       (float)         [create]
          Specifies green component of color to use for data that is below min
    
      - belowMinColorRed : bmr         (float)         [create]
          Specifies red component of color to use for data that is below min
    
      - clashColorBlue : ccb           (float)         [create]
          Specifies blue component color to use for data which clashes
    
      - clashColorGreen : ccg          (float)         [create]
          Specifies green component color to use for data which clashes
    
      - clashColorRed : ccr            (float)         [create]
          Specifies red component color to use for data which clashes
    
      - colorBlue : cb                 (float)         [create]
          Specifies blue component of color to use for given data
    
      - colorGreen : cg                (float)         [create]
          Specifies green component of color to use for given data
    
      - colorRed : cr                  (float)         [create]
          Specifies red component of color to use for given data
    
      - dataType : dt                  (unicode)       [create]
          Specifies the type for this id
    
      - enableFalseColor : efc         (bool)          [create]
          Turns false coloring on or off for all poly objects in the scene
    
      - maxColorBlue : mxb             (float)         [create]
          Specifies blue component of color to use for max value for grayscale
    
      - maxColorGreen : mxg            (float)         [create]
          Specifies green component of color to use for max value for grayscale
    
      - maxColorRed : mxr              (float)         [create]
          Specifies red component of color to use for max value for grayscale
    
      - maxValue : mxv                 (float)         [create]
          Specifies the max value for grayscale or discrete range data
    
      - minColorBlue : mnb             (float)         [create]
          Specifies blue component of color to use for min value for grayscale
    
      - minColorGreen : mng            (float)         [create]
          Specifies green component of color to use for min value for grayscale
    
      - minColorRed : mnr              (float)         [create]
          Specifies red component of color to use for min value for grayscale
    
      - minValue : mnv                 (float)         [create]
          Specifies the min value for grayscale or discrete range data
    
      - mode : m                       (int)           [create]
          Specifies the mode: 0 : binary - only components and objects that have the data will be colored1 : discrete value - a
          value is specified. Data that matches this value will be colored2 : discrete range - values that fall within the given
          range will be colored3 : unsigned set mode - if ( givenValue actualValue ) then data will be colored4 : unsigned not set
          mode - if ( !(givenValue actualValue) ) then data will be colored5 : unsigned equal mode - if ( givenValue ==
          actualValue ) then data will be colored6 : grayscale mode - a min value, max value, min color, max color, below min
          color, and     above max color are given. Data is colored according to how it relates to these values.7 : as color mode
          - if the blind data consists of 3 doubles, ranged 0-1, the components are colored as the data specifies
    
      - noColorBlue : ncb              (float)         [create]
          Specifies blue component of color to use for no data assigned
    
      - noColorGreen : ncg             (float)         [create]
          Specifies green component of color to use for no data assigned
    
      - noColorRed : ncr               (float)         [create]
          Specifies red component of color to use for no data assigned
    
      - numIdTypes : num               (int)           [create]
          Specifies how many attrs are in this id type
    
      - queryMode : q                  (bool)          [create]
          If on, do not color and return selection as string array instead. Any data that would be colored normally (except for
          'no color' and out of range colors) is returned
    
      - typeId : id                    (int)           [create]
          Specifies the typeId of the BlindData type being created
    
      - useMax : umx                   (bool)          [create]
          Specifies whether the max should be used for discrete ranges
    
      - useMin : umn                   (bool)          [create]
          Specifies whether the min should be used for discrete ranges
    
      - value : v                      (unicode)       [create]
          The value of the data                              Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyColorBlindData`
    """

    pass


def polyChipOff(*args, **kwargs):
    """
    Extract facets. Faces can be extracted separately or together, and manipulations can be performed either in world or
    object space.
    
    Flags:
      - attraction : att               (float)         [create,query,edit]
          This flag specifies the attraction, related to magnet. C: Default is 0.0. The range is [-2.0, 2.0]. Q: When queried,
          this flag returns a float.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - duplicate : dup                (bool)          [create,query,edit]
          If on, facets are duplicated, otherwise original facets are removed. C: Default is on. Q: When queried, this flag
          returns an int.
    
      - frozen : fzn                   (bool)          []
    
      - gain : ga                      (float)         []
    
      - gravity : g                    (float, float, float) [create,query,edit]
          This flag specifies the gravity vector. C: Default is 0.0 -1.0 0.0. Q: When queried, this flag returns a float[3].
    
      - gravityX : gx                  (float)         [create,query,edit]
          This flag specifies X for the gravity vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - gravityY : gy                  (float)         [create,query,edit]
          This flag specifies Y for the gravity vector. C: Default is -1.0. Q: When queried, this flag returns a float.
    
      - gravityZ : gz                  (float)         [create,query,edit]
          This flag specifies Z for the gravity vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - keepFacesTogether : kft        (bool)          [create,query,edit]
          This flag specifies how to chip off facets. If on, facets are pulled together (connected ones stay connected), otherwise
          they are pulled independentely. C: Default is on. Q: When queried, this flag returns an int.
    
      - keepFacetTogether : xft        (bool)          []
    
      - localCenter : lc               (int)           []
    
      - localDirection : ld            (float, float, float) [create,query,edit]
          This flag specifies the local slant axis (see local rotation). C: Default is 0.0 0.0 1.0. Q: When queried, this flag
          returns a float[3].
    
      - localDirectionX : ldx          (float)         [create,query,edit]
          This flag specifies X for the local slant axis. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localDirectionY : ldy          (float)         [create,query,edit]
          This flag specifies Y for the local slant axis. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localDirectionZ : ldz          (float)         [create,query,edit]
          This flag specifies Y for the local slant axis. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localRotate : lr               (float, float, float) [create,query,edit]
          This flag specifies the local rotations : (slantRot, slantRoll, twistRot). C: Default is 0.0 0.0 0.0. Q: When queried,
          this flag returns a float[3]. Local rotation (slantRot, slantRoll, twistRot).
    
      - localRotateX : lrx             (float)         [create,query,edit]
          This flag specifies local rotation X angle (Slant Rot around slantAxis). C: Default is 0.0. The range is [0, 360]. Q:
          When queried, this flag returns a float.
    
      - localRotateY : lry             (float)         [create,query,edit]
          This flag specifies local rotation Y angle (Slant Roll of slantAxis). C: Default is 0.0. The range is [0, 180]. Q: When
          queried, this flag returns a float.
    
      - localRotateZ : lrz             (float)         [create,query,edit]
          This flag specifies local rotation Z angle (Twist around normal). C: Default is 0.0. The range is [0, 360]. Q: When
          queried, this flag returns a float.
    
      - localScale : ls                (float, float, float) [create,query,edit]
          This flag specifies the local scaling vector. C: Default is 1.0 1.0 1.0. Q: When queried, this flag returns a float[3].
    
      - localScaleX : lsx              (float)         [create,query,edit]
          This flag specifies X for local scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localScaleY : lsy              (float)         [create,query,edit]
          This flag specifies Y for local scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - localScaleZ : lsz              (float)         [create,query,edit]
          This flag specifies Z for local scaling vector : Flattening. C: Default is 1.0. The range is [0.0, 1.0]. Q: When
          queried, this flag returns a float. Dynamic Values
    
      - localTranslate : lt            (float, float, float) [create,query,edit]
          This flag specifies the local translation vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - localTranslateX : ltx          (float)         [create,query,edit]
          This flag specifies the X local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localTranslateY : lty          (float)         [create,query,edit]
          This flag specifies the Y local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - localTranslateZ : ltz          (float)         [create,query,edit]
          This flag specifies the Z local translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - magnX : mx                     (float)         [create,query,edit]
          This flag specifies X for the magnet vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - magnY : my                     (float)         [create,query,edit]
          This flag specifies Y for the magnet vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - magnZ : mz                     (float)         [create,query,edit]
          This flag specifies Z for the magnet vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - magnet : m                     (float, float, float) [create,query,edit]
          This flag specifies the magnet vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - offset : off                   (float)         [create,query,edit]
          This flag specifies the local offset. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivot : pvt                    (float, float, float) [create,query,edit]
          This flag specifies the pivot for scaling and rotation. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - pivotX : pvx                   (float)         [create,query,edit]
          This flag specifies the X pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotY : pvy                   (float)         [create,query,edit]
          This flag specifies the Y pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - pivotZ : pvz                   (float)         [create,query,edit]
          This flag specifies the Z pivot for scaling and rotation. C: Default is 0.0. Q: When queried, this flag returns a float.
          Local Values
    
      - random : ran                   (float)         [create,query,edit]
          This flag specifies the random value for all parameters. C: Default is 0.0. The range is [-10.0, 10.0]. Q: When queried,
          this flag returns a float. Global Values
    
      - rotate : ro                    (float, float, float) [create,query,edit]
          This flag specifies the rotation angles around X, Y, Z. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a
          float[3].
    
      - rotateX : rx                   (float)         [create,query,edit]
          This flag specifies the rotation angle around X. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateY : ry                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Y. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateZ : rz                   (float)         [create,query,edit]
          This flag specifies the rotation angle around Z. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - scale : s                      (float, float, float) [create,query,edit]
          This flag specifies the scaling vector. C: Default is 1.0 1.0 1.0. Q: When queried, this flag returns a float[3].
    
      - scaleX : sx                    (float)         [create,query,edit]
          This flag specifies X for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleY : sy                    (float)         [create,query,edit]
          This flag specifies Y for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - scaleZ : sz                    (float)         [create,query,edit]
          This flag specifies Z for scaling vector. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - translate : t                  (float, float, float) [create,query,edit]
          This flag specifies the translation vector. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - translateX : tx                (float)         [create,query,edit]
          This flag specifies the X translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateY : ty                (float)         [create,query,edit]
          This flag specifies the Y translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - translateZ : tz                (float)         [create,query,edit]
          This flag specifies the Z translation vector. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - weight : w                     (float)         [create,query,edit]
          This flag specifies the weight, related to gravity. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyChipOff`
    """

    pass


def subdPlanarProjection(*args, **kwargs):
    """
    Base class for the command to create a mapping on the selected subdivision faces. Projects a map onto an object, using
    an orthogonal projection. The piece of the map defined from isu, isv, icx, icy area, is placed at pcx, pcy, pcz
    location.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - createNewMap : cm              (bool)          [create,query,edit]
          This flag when set true will create a new map with a the name passed in, if the map does not already exist.
    
      - frozen : fzn                   (bool)          []
    
      - imageCenter : ic2              (float, float)  [create,query,edit]
          This flag specifies the center point of the 2D model layout. C: Default is 0.5 0.5. Q: When queried, this flag returns a
          float[2].
    
      - imageCenterX : icx             (float)         [create,query,edit]
          This flag specifies X for the center point of the 2D model layout. C: Default is 0.5. Q: When queried, this flag returns
          a float.
    
      - imageCenterY : icy             (float)         [create,query,edit]
          This flag specifies Y for the center point of the 2D model layout. C: Default is 0.5. Q: When queried, this flag returns
          a float.
    
      - imageScale : is2               (float, float)  [create,query,edit]
          This flag specifies the UV scale : Enlarges or reduces the 2D version of the model in U or V space relative to the 2D
          centerpoint. C: Default is 1.0 1.0. Q: When queried, this flag returns a float[2].
    
      - imageScaleU : isu              (float)         [create,query,edit]
          This flag specifies the U scale : Enlarges or reduces the 2D version of the model in U space relative to the 2D
          centerpoint. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - imageScaleV : isv              (float)         [create,query,edit]
          This flag specifies the V scale : Enlarges or reduces the 2D version of the model in V space relative to the 2D
          centerpoint. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - insertBeforeDeformers : ibd    (bool)          [create]
          This flag specifies if the projection node should be inserted before or after deformer nodes already applied to the
          shape. Inserting the projection after the deformer leads to texture swimming during animation and is most often
          undesirable. C: Default is on.
    
      - keepImageRatio : kir           (bool)          [create]
          True means keep any image ratio
    
      - mapDirection : md              (unicode)       [create]
          This flag specifies the mapping direction. 'x', 'y' and 'z' projects the map along the corresponding axis. 'c' projects
          along the current camera viewing direction. 'p' does perspective projection if current camera is perspective. 'b'
          projects along the best plane fitting the objects selected.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - projectionCenter : pc          (float, float, float) [create,query,edit]
          This flag specifies the origin point from which the map is projected. C: Default is 0.0 0.0 0.0. Q: When queried, this
          flag returns a float[3].
    
      - projectionCenterX : pcx        (float)         [create,query,edit]
          This flag specifies X for the origin point from which the map is projected. C: Default is 0.0. Q: When queried, this
          flag returns a float.
    
      - projectionCenterY : pcy        (float)         [create,query,edit]
          This flag specifies Y for the origin point from which the map is projected. C: Default is 0.0. Q: When queried, this
          flag returns a float.
    
      - projectionCenterZ : pcz        (float)         [create,query,edit]
          This flag specifies Z for the origin point from which the map is projected. C: Default is 0.0. Q: When queried, this
          flag returns a float.
    
      - projectionHeight : ph          (float)         [create,query,edit]
          This flag specifies the height of the map relative to the 3D projection axis. C: Default is 1.0 Q: When queried, this
          flag returns a float.
    
      - projectionScale : ps           (float, float)  [create,query,edit]
          This flag specifies the width and the height of the map relative to the 3D projection axis. C: Default is 1.0 1.0. Q:
          When queried, this flag returns a float[2].
    
      - projectionWidth : pw           (float)         [create,query,edit]
          This flag specifies the width of the map relative to the 3D projection axis. C: Default is 1.0 Q: When queried, this
          flag returns a float.
    
      - rotate : ro                    (float, float, float) [create,query,edit]
          This flag specifies the mapping rotate angles. C: Default is 0.0 0.0 0.0. Q: When queried, this flag returns a float[3].
    
      - rotateX : rx                   (float)         [create,query,edit]
          This flag specifies X mapping rotate angle. C: Default is 0.0. Q: When queried, this flag returns a float[3].
    
      - rotateY : ry                   (float)         [create,query,edit]
          This flag specifies Y mapping rotate angle. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotateZ : rz                   (float)         [create,query,edit]
          This flag specifies Z mapping rotate angle. C: Default is 0.0. Q: When queried, this flag returns a float.
    
      - rotationAngle : ra             (float)         [create,query,edit]
          This flag specifies the rotation angle in the mapping space. When the angle is positive, then the map rotates
          counterclockwise on the mapped model, whereas when it is negative then the map rotates lockwise on the mapped model. C:
          Default is 10.0. Q: When queried, this flag returns a float.
    
      - smartFit : sf                  (bool)          [create]
          True means use the smart fit algorithm
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Advanced flags
    
    
    Derived from mel command `maya.cmds.subdPlanarProjection`
    """

    pass


def offsetCurve(*args, **kwargs):
    """
    The offset command creates new offset curves from the selected curves. The connecting type for breaks in offsets is off
    (no connection), circular (connect with an arc) or linear (connect linearly resulting in a sharp corner). If loop
    cutting is on then any loops in the offset curves are trimmed away. For the default cut radius of 0.0 a sharp corner is
    created at each intersection. For values greater than 0.0 a small arc of that radius is created at each intersection.
    The cut radius value is only valid when loop cutting is on. Offsets (for planar curves) are calculated in the plane of
    that curve and 3d curves are offset in 3d. The subdivisionDensity flag is the maximum number of times the offset object
    can be subdivided (i.e. calculate the offset until the offset comes within tolerance or the iteration reaches this
    maximum.) The reparameterize option allows the offset curve to have a different parameterization to the original curve.
    This avoids uneven parameter distributions in the offset curve that can occur with large offsets of curves, but is more
    expensive to compute.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - connectBreaks : cb             (int)           [create,query,edit]
          Connect breaks method (between gaps): 0 - off, 1 - circular, 2 - linear Default:2
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - cutLoop : cl                   (bool)          [create,query,edit]
          Do loop cutting. Default:false
    
      - cutRadius : cr                 (float)         [create,query,edit]
          Loop cut radius. Only used if cutLoop attribute is set true. Default:0.0
    
      - distance : d                   (float)         [create,query,edit]
          Offset distance Default:1.0
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - normal : nr                    (float, float, float) [create,query,edit]
          Offset plane normal
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.                  Advanced flags
    
      - reparameterize : rp            (bool)          [create,query,edit]
          Do reparameterization. It is not advisable to change this value. Default:false
    
      - stitch : st                    (bool)          [create,query,edit]
          Stitch curve segments together. It is not advisable to change this value. Default:true
    
      - subdivisionDensity : sd        (int)           [create,query,edit]
          Maximum subdivision density per span Default:5
    
      - tolerance : tol                (float)         [create,query,edit]
          Tolerance Default:0.01
    
      - useGivenNormal : ugn           (bool)          [create,query,edit]
          Use the given normal (or, alternativelly, geometry normal) Default:1                  Common flags
    
    
    Derived from mel command `maya.cmds.offsetCurve`
    """

    pass


def surface(*args, **kwargs):
    """
    The cmd creates a NURBS spline surface (rational or non rational). The surface is created by specifying control vertices
    (CV's) and knot sequences in the U and V direction.  You cannot query the properties of the surface using this command.
    See examples below.
    
    Maya Bug Fix:
      - name parameter only applied to transform. now applies to shape as well
    
    Flags:
      - degreeU : du                   (int)           [create]
          Degree in surface U direction.  Default is degree 3.
    
      - degreeV : dv                   (int)           [create]
          Degree in surface V direction.  Default is degree 3.
    
      - formU : fu                     (unicode)       [create]
          The string for open is open, for closed is closedor for periodic is periodicin U.
    
      - formV : fv                     (unicode)       [create]
          The string for open is open, for closed is closedor for periodic is periodicin V.
    
      - knotU : ku                     (float)         [create]
          Knot value(s) in U direction.  One flag per knot value. There must be (numberOfPointsInU + degreeInU - 1) knots and the
          knot vector must be non-decreasing.
    
      - knotV : kv                     (float)         [create]
          Knot value(s) in V direction.  One flag per knot value. There must be (numberOfPointsInV + degreeInV - 1) knots and the
          knot vector must be non-decreasing.
    
      - name : n                       (unicode)       [create]
          Name to use for new transforms.
    
      - objectSpace : ob               (bool)          [create]
          Should the operation happen in objectSpace?
    
      - point : p                      (float, float, float) [create]
          To specify non rational CV with (x, y, z) values.  linearmeans that this flag can take values with units.  Note that you
          must specify (degree+1) surface points in any direction to create a visible surface span.  eg.  if the surface is degree
          3 in the U direction, you must specify 4 CVs in the U direction. Points are specified in rows of U and columns of V.  If
          you want to incorporate units, add the unit name to the value, eg. -p 3.3in 5.5ft 6.6yd
    
      - pointWeight : pw               (float, float, float, float) [create]
          To specify rational CV with (x, y, z, w) values.  linearmeans that this flag can take values with units.  Note that you
          must specify (degree+1) surface points in any direction to create a visible surface span.  eg.  if the surface is degree
          3 in the U direction, you must specify 4 CVs in the U direction. Points are specified in rows of U and columns of V.
    
      - worldSpace : ws                (bool)          [create]
          Should the operation happen in worldSpace?                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.surface`
    """

    pass


def transferAttributes(*args, **kwargs):
    """
    Samples the attributes of a source surface (first argument) and transfers them onto a target surface (second argument).
    
    Flags:
      - after : af                     (bool)          [create,edit]
          If the default behavior for insertion/appending into/onto the existing chain is not the desired behavior then this flag
          can be used to force the command to place the deformer node after the selected node in the chain even if a new geometry
          shape has to be created in order to do so. Works in create mode (and edit mode if the deformer has no geometry added
          yet).
    
      - afterReference : ar            (bool)          [create,edit]
          The -afterReference flag is used to specify deformer ordering in a hybrid way that choses between -before and -after
          automatically. If the geometry being deformed is referenced then the -after mode is used when adding the new deformer,
          otherwise the -before mode is used. The net effect when using -afterReference to build deformer chains is that internal
          shape nodes in the deformer chain will only appear at reference file boundaries, leading to lightweight deformer
          networks that may be more amicable to reference swapping.
    
      - before : bf                    (bool)          [create,edit]
          If the default behavior for insertion/appending into/onto the existing chain is not the desired behavior then this flag
          can be used to force the command to place the deformer node before the selected node in the chain even if a new geometry
          shape has to be created in order to do so. Works in create mode (and edit mode if the deformer has no geometry added
          yet).
    
      - colorBorders : clb             (int)           [create,edit]
          Controls whether color borders are preserved when transferring color data. If this is non-zero, any color borders will
          be mapped onto the nearest edge on the target geometry. 0 means any color borders will be smoothly blended onto the
          vertices of the target geometry.
    
      - deformerTools : dt             (bool)          [query]
          Returns the name of the deformer tool objects (if any) as string string ...
    
      - exclusive : ex                 (unicode)       [create,query]
          Puts the deformation set in a deform partition.
    
      - flipUVs : fuv                  (int)           [create,edit]
          Controls how sampled UV data is flipped before being transferred to the target. 0 means no flipping; 1 means UV data is
          flipped in the U direction; 2 means UV data is flipped in the V direction; and 3 means it is flipped in both directions.
          In conjunction with mirroring, this allows the creation of symmetric UV mappings (e.g. the left hand side of the
          character on one side of the UV map, the right hand side on the other).
    
      - frontOfChain : foc             (bool)          [create,edit]
          This command is used to specify that the new deformer node should be placed ahead (upstream) of existing deformer and
          skin nodes in the shape's history (but not ahead of existing tweak nodes). The input to the deformer will be the
          upstream shape rather than the visible downstream shape, so the behavior of this flag is the most intuitive if the
          downstream deformers are in their reset (hasNoEffect) position when the new deformer is added. Works in create mode (and
          edit mode if the deformer has no geometry added yet).
    
      - geometry : g                   (unicode)       [query,edit]
          The specified object will be added to the list of objects being deformed by this deformer object, unless the -rm flag is
          also specified. When queried, this flag returns string string string ...
    
      - geometryIndices : gi           (bool)          [query]
          Complements the -geometry flag in query mode. Returns the multi index of each geometry.
    
      - ignoreSelected : ignoreSelected (bool)          [create]
          Tells the command to not deform objects on the current selection list
    
      - includeHiddenSelections : ihs  (bool)          [create]
          Apply the deformer to any visible and hidden objects in the selection list. Default is false.
    
      - matchChoice : mch              (int)           [create,edit]
          When using topological component matching, selects between possible matches. If the meshes involved in the transfer
          operation have symmetries in their topologies, there may be more than one possible topological match. Maya scores the
          possible matches (by comparing the shapes of the meshes) and assigns them an index, starting at zero. Match zero, the
          default, is considered the best, but in the event that Maya chooses the wrong one, changing this value will allow the
          user to explore the other matches.
    
      - name : n                       (unicode)       [create]
          Used to specify the name of the node being created.
    
      - parallel : par                 (bool)          [create,edit]
          Inserts the new deformer in a parallel chain to any existing deformers in the history of the object. A blendShape is
          inserted to blend the parallel results together. Works in create mode (and edit mode if the deformer has no geometry
          added yet).
    
      - prune : pr                     (bool)          [edit]
          Removes any points not being deformed by the deformer in its current configuration from the deformer set.
    
      - remove : rm                    (bool)          [edit]
          Specifies that objects listed after the -g flag should be removed from this deformer.
    
      - sampleSpace : spa              (int)           [create,edit]
          Selects which space the attribute transfer is performed in. 0 is world space, 1 is model space, 4 is component-based, 5
          is topology-based. The default is world space.
    
      - searchMethod : sm              (int)           [create,edit]
          Specifies which search method to use when correlating points. 0 is closest along normal, 3 is closest to point. The
          default is closest to point.
    
      - searchScaleX : ssx             (float)         [create,edit]
          Specifies an optional scale that should be applied to the x-axis of the target model before transferring data. A value
          of 1.0 (the default) means no scaling; a value of -1.0 would indicate mirroring along the x-axis.
    
      - searchScaleY : ssy             (float)         [create,edit]
          Specifies an optional scale that should be applied to the y-axis of the target model before transferring data. A value
          of 1.0 (the default) means no scaling; a value of -1.0 would indicate mirroring along the y-axis.
    
      - searchScaleZ : ssz             (float)         [create,edit]
          Specifies an optional scale that should be applied to the z-axis of the target model before transferring data. A value
          of 1.0 (the default) means no scaling; a value of -1.0 would indicate mirroring along the z-axis.
    
      - sourceColorSet : scs           (unicode)       [create]
          Specifies the name of a single color set on the source surface(s) that should be transferred to the target. This value
          is only used when the operation is configured to transfer a single color set (see the transferColors flag).
    
      - sourceUvSet : suv              (unicode)       [create]
          Specifies the name of a single UV set on the source surface(s) that should be transferred to the target. This value is
          only used when the operation is configured to transfer a single UV set (see the transferUVs flag).
    
      - sourceUvSpace : sus            (unicode)       [create]
          Specifies the name of the UV set on the source surface(s) that should be used as the transfer space. This value is only
          used when the operation is configured to transfer attributes in UV space.
    
      - split : sp                     (bool)          [create,edit]
          Branches off a new chain in the dependency graph instead of inserting/appending the deformer into/onto an existing
          chain. Works in create mode (and edit mode if the deformer has no geometry added yet).
    
      - targetColorSet : tcs           (unicode)       [create]
          Specifies the name of a single color set on the target surface that should be receive the sampled color data. This value
          is only used when the operation is configured to transfer a single color set (see the transferColors flag).
    
      - targetUvSet : tuv              (unicode)       [create]
          Specifies the name of a single UV set on the target surface that should be receive the sampled UV data. This value is
          only used when the operation is configured to transfer a single UV set (see the transferUVs flag).
    
      - targetUvSpace : tus            (unicode)       [create]
          Specifies the name of the UV set on the target surface( that should be used as the transfer space. This value is only
          used when the operation is configured to transfer attributes in UV space.
    
      - transferColors : col           (int)           [create,edit]
          Controls color set transfer. 0 means no color sets are transferred, 1 means that a single color set (specified by
          sourceColorSet and targetColorSet) is transferred, and 2 means that all color sets are transferred.
    
      - transferNormals : nml          (int)           [create,edit]
          A non-zero value indicates vertex normals should be sampled and written into user normals on the target surface.
    
      - transferPositions : pos        (int)           [create,edit]
          A non-zero value indicates vertex position should be sampled, causing the target surface to wrapto the source
          surface(s).
    
      - transferUVs : uvs              (int)           [create,edit]
          Controls UV set transfer. 0 means no UV sets are transferred, 1 means that a single UV set (specified by sourceUVSet and
          targetUVSet) is transferred, and 2 means that all UV sets are transferred.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.transferAttributes`
    """

    pass


def polySplit(*args, **kwargs):
    """
    Split facets/edges of a polygonal object. The first and last arguments must be edges. Intermediate points may lie on
    either a shared face or an edge which neighbors the previous point.
    
    Flags:
      - adjustEdgeFlow : aef           (float)         []
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - detachEdges : de               (bool)          []
    
      - edgepoint : ep                 (int, float)    [create]
          The given edge is split into two new edges by inserting a new vertex located the given percentage along the edge.
          Note:This flag is not recommended for use from Python.  See the insertpoint flag instead.
    
      - facepoint : fp                 (int, float, float, float) [create]
          A new vertex is inserted, lying at the given coordinates inside the given face. Coordinates are given in the local
          object space. Note:This flag is not recommended for use from Python.  See the insertpoint flag instead.
    
      - insertWithEdgeFlow : ief       (bool)          []
    
      - insertpoint : ip               (int, float, float, float) [create]
          This flag allows the caller to insert a new vertex into an edge or a face. To insert a new vertex in an edge, pass the
          index of the edge and a percentage along the edge at which to insert the new vertex.  When used to insert a vertex into
          an edge, this flag takes two arguments. To insert a new vertex into a face, pass the index of the face and three values
          which define the coordinates for the insertion in local object space.  When used to insert a vertex into a face, this
          flag takes four arguments. This flag replaces the edgepoint and facepoint flags.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - projectedCurve : pc            (PyNode)        []
    
      - smoothingangle : sma           (float)         [create]
          Subdivide new edges will be soft if less then this angle. C: Default is 0.0
    
      - subdivision : s                (int)           [create,query,edit]
          Subdivide new edges into the given number of sections. Edges involving free points won't be subdivided. C: Default is 1
          (no subdivision). Q: When queried, this flag returns an int.                  Common flags
    
    
    Derived from mel command `maya.cmds.polySplit`
    """

    pass


def polyOptUvs(*args, **kwargs):
    """
    Optimizes selected UVs.
    
    Flags:
      - applyToShell : applyToShell    (bool)          [create]
          Specifies where the whole object or just shells that are selected or pinned should be affected.
    
      - areaWeight : aw                (float)         [create]
          Surface driven importance. 0 treat all faces equal. 1 gives more importance to large ones.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - globalBlend : gb               (float)         [create]
          This allows the user to blend between a local optimization method (globalBlend = 0.0) and a global optimization method
          (globalBlend = 1.0). The local optimization method looks at the ratio between the triangles on the object and the
          triangles in UV space.  It has a side affect that it can sometimes introduce tapering problems.  The global optimization
          is much slower, but takes into consideration the entire object when optimizing uv placement.
    
      - globalMethodBlend : gmb        (float)         [create]
          The global optimization method uses two functions to compute a minimization.  The first function controls edge stretch
          by using edges lengths between xyz and uv.  The second function penalizes the first function by preventing
          configurations where triangles would overlap.  For every surface there is a mix between these two functions that will
          give the appropriate response. Values closer to 1.0 give more weight to the edge length function. Values closer to 0.0
          give more weight to surface area.  The default value of '0.5' is a even mix between these two values.
    
      - iterations : i                 (int)           [create]
          Maximum number of iterations for each connected UV piece.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - optimizeAxis : oa              (int)           [create]
          Degree of freedom for optimization: 0=Optimize freely, 1=Move vertically only, 2=Move horzontally only
    
      - pinSelected : ps               (bool)          [create]
          Specifies that the selected components should be pinned instead of the unselected components.
    
      - pinUvBorder : pub              (bool)          [create]
          Specifies that the UV border should be pinned when doing the solve. By default only unselected components are pinned.
    
      - scale : s                      (float)         [create]
          Ratio between 2d and 3d space.
    
      - stoppingThreshold : ss         (float)         [create]
          Minimum distorsion improvement between two steps in %.
    
      - useScale : us                  (bool)          [create]
          Adjust the scale or not.
    
      - uvSetName : uvs                (unicode)       [create,query]
          Specifies name of the uv set to modify. Default is the current UV set.                  Common flags
    
      - worldSpace : ws                (bool)          []
    
    
    Derived from mel command `maya.cmds.polyOptUvs`
    """

    pass


def subdMapCut(*args, **kwargs):
    """
    Cut along edges of the texture mapping. The cut edges become map borders.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Advanced flags
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.subdMapCut`
    """

    pass


def subdCollapse(*args, **kwargs):
    """
    This command converts a takes a subdivision surface, passed as the argument, and produces a subdivision surface with a
    number of hierarchy levels removed. Returns the name of the subdivision surface created and optionally the DG node that
    does the conversion.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off (where applicable).
    
      - frozen : fzn                   (bool)          []
    
      - level : l                      (int)           [create,query,edit]
          The level that will now become the base mesh. Default:0                  Common flags
    
      - name : n                       (unicode)       [create]
          Name the resulting object.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the depend node (where applicable).                  Advanced flags
    
    
    Derived from mel command `maya.cmds.subdCollapse`
    """

    pass


def fitBspline(*args, **kwargs):
    """
    The fitBspline command fits the CVs from an input curve and and returns a 3D curve.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.                  Advanced flags
    
      - tolerance : tol                (float)         [create,query,edit]
          Tolerance for the fit.  The resulting curve will be kept within tolerance of the given points. Default:0.1
          Common flags
    
    
    Derived from mel command `maya.cmds.fitBspline`
    """

    pass


def blindDataType(*args, **kwargs):
    """
    This command creates a blind data type, which is represented by a blindDataTemplate node in the DG. A blind data type
    can have one or more attributes. On the command line, the attributes should be ordered by type for best memory
    utilization, largest first: string, binary, double, float, int, and finally boolean. Once a blind data type is created,
    blind data of that type may be assigned using the polyBlindData command. Note that as well as polygon components, blind
    data may be assigned to objects and to NURBS patches. A blind data type may not be modified after it is created: in
    order to do so it must be deleted and recreated. Any existing blind data of that type would also need to be deleted and
    recreated. When used with the query flag, this command will return information about the attributes of the specified
    blind data type.
    
    Flags:
      - dataType : dt                  (unicode)       [create]
          Specifies the dataTypes that are part of BlindData node being created. Allowable strings are int, float, double, string,
          booleanand binary. Must be used togeter with the -ldn and -sdn flags to specify each attribute.
    
      - longDataName : ldn             (unicode)       [create]
          Specifies the long names of the datas that are part of BlindData node being created. Must be used togeter with the -dt
          and -sdn flags to specify each attribute.
    
      - longNames : ln                 (bool)          [create]
          Specifies that for a query command the long attributes names be listed.
    
      - shortDataName : sdn            (unicode)       [create]
          Specifies the short names of the data that are part of BlindData node being created. Must be used togeter with the -dt
          and -ldn flags to specify each attribute.
    
      - shortNames : sn                (bool)          [create]
          Specifies that for a query command the short attribute names be listed.
    
      - typeId : id                    (int)           [create]
          Specifies the typeId of the BlindData type being created.
    
      - typeNames : tn                 (bool)          [create]
          Specifies that for a query command the data types be listed.                               Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.blindDataType`
    """

    pass


def polyRemesh(*args, **kwargs):
    """
    Triangulates, then remeshes the given mesh through edge splitting and collapsing. Edges longer than the specified
    refinement threshold are split, and edges shorter than the reduction threshold are collapsed.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - interpolationType : ipt        (int)           [create,query,edit]
          Algorithm used for interpolating new vertices
    
      - maxTriangleCount : mtc         (int)           []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabled
    
      - reduceThreshold : rdt          (float)         [create,query,edit]
          A percentage of the refineThreshold. Edges shorter than this percentage will be reduced to a single vertex.
    
      - refineThreshold : rft          (float)         [create,query,edit]
          Triangle edges longer than this value will be split into two edges.
    
      - smoothStrength : smt           (float)         [create,query,edit]
          Amount of smoothing applied to the vertices after remeshing.
    
      - tessellateBorders : tsb        (bool)          [create,query,edit]
          Specifies if the borders of the selected region are allowed to be remeshed.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
      - worldSpace : ws                (bool)          []
    
    
    Derived from mel command `maya.cmds.polyRemesh`
    """

    pass


def polyColorDel(*args, **kwargs):
    """
    Deletes color from selected components.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - colorSetName : cls             (unicode)       []
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyColorDel`
    """

    pass


def bevelPlus(*args, **kwargs):
    """
    The bevelPlus command creates a new bevel surface for the specified curves using a given style curve. The first curve
    should be the outsidecurve, and the (optional) rest of them should be inside of the first one. For predictable results,
    the curves should be planar and all in the same plane.
    
    Flags:
      - bevelInside : bin              (bool)          []
    
      - caching : cch                  (bool)          []
    
      - capSides : cap                 (int)           [create,query]
          How to cap the bevel. 1 - no caps2 - cap at start only3 - cap at end only4 - cap at start and endDefault:4
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - depth : d                      (float)         [create,query,edit]
          The depth for the bevel. Default:0.5
    
      - extrudeDepth : ed              (float)         [create,query,edit]
          The extrude distance (depth) for bevel. Default:1.0
    
      - frozen : fzn                   (bool)          []
    
      - innerStyle : innerStyle        (int)           [create,query,edit]
          Similar to outerStyle, this style is applied to all but the first (outer) curve specified.
    
      - joinSurfaces : js              (bool)          [create,query,edit]
          Attach bevelled surfaces into one surface for each input curve. Default:true
    
      - name : n                       (unicode)       [create]
          Name the resulting object.
    
      - nodeState : nds                (int)           []
    
      - normalsOutwards : no           (bool)          [create,query,edit]
          If enabled, the normals point outwards on the resulting NURBS or poly surface.
    
      - numberOfSides : ns             (int)           [create,query,edit]
          How to apply the bevel. 1 - no bevels2 - bevel at start only3 - bevel at end only4 - bevel at start and endDefault:4
    
      - outerStyle : os                (int)           [create,query,edit]
          Choose a style to use for the bevel of the first (outer) curve.  There are 15 predefined styles (values 0 to 14 can be
          used to select them). For those experienced with MEL, you can, after the fact, specify a custom curve and use it for the
          style curve. See the documentation for styleCurve node to see what requirements a style curve must satisfy.
    
      - polyOutChordHeight : cht       (float)         [create,query,edit]
          Chord height is the absolute distance in object space which the center of a polygon edge can deviate from the actual
          center of the surface span. Only used if Method is Sampling and if polyOutseChordHeight is true. Default:0.1
    
      - polyOutChordHeightRatio : chr  (float)         [create,query,edit]
          Chord height ratio is the ratio of the chord length of a surface span to the chord height.  (This is a length to height
          ratio). 0 is a very loose fit. 1 is a very tight fit.  This applies to the polygonal output type only. (See also
          description of chord height.) Used if Method is Sampling and polyOutUseChordHeightRatio is true. Default:0.1
    
      - polyOutCount : poc             (int)           [create,query,edit]
          The number of polygons to produce when the polygon is requested.  Only used if Method is face count (0). Default:200
    
      - polyOutCurveSamples : pcs      (int)           [create,query,edit]
          Initial number of samples in the curve direction. Only used if Method is Sampling. Default:6
    
      - polyOutCurveType : pct         (int)           [create,query,edit]
          Initial tessellation criteria along the curve.  Only used if Method is Sampling. 2 - Complete Curve.  This type places a
          specific number of sample points along the curve, equally spaced in parameter space.3 - Curve Span.  This type places a
          specific number of sample points across each curve span, equally spaced in parameter space.Default:3
    
      - polyOutExtrusionSamples : pes  (int)           [create,query,edit]
          Initial number of samples along the extrusion. Only used if Method is Sampling. Default:2
    
      - polyOutExtrusionType : pet     (int)           [create,query,edit]
          Initial type tessellation criteria along the extrude direction.  Used only if Method is Sampling. 2 - Complete
          Extrusion.  This type places a specific number of lines across the surface, equally spaced in parameter space.3 -
          Extrusion Section.  This type places a specific number of lines across each surface span, equally spaced in parameter
          space.Default:3
    
      - polyOutMethod : pom            (int)           [create,query,edit]
          Method for the polygonal output: 0 - Face Count, 2 - Sampling Default:2
    
      - polyOutUseChordHeight : uch    (bool)          [create,query,edit]
          True means use chord height.  This is a secondary criteria that refines the tessellation produced using the sampling
          value.  Only used if Method is Sampling. Default:false
    
      - polyOutUseChordHeightRatio : ucr (bool)          [create,query,edit]
          True means use chord height ratio.  This is a secondary criteria that refines the tessellation produced using the
          sampling value.  Only used if Method is Sampling. Default:true
    
      - polygon : po                   (int)           [create]
          Create a polyset (1) instead of nurbs surface (0).
    
      - range : rn                     (bool)          []
    
      - tolerance : tol                (float)         [create,query,edit]
          The tolerance for creating NURBS caps. Default:0.01
    
      - width : w                      (float)         [create,query,edit]
          The width for the bevel. Default:0.5                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.bevelPlus`
    """

    pass


def polySplitEdge(*args, **kwargs):
    """
    Split Edges.There are two operations for this command depending on the value of the -operation flag. If -operation is
    set to 1 then this command will split apart faces along all selected manifold edges. If -operation is set to 0 then this
    command will split non-manifold edges so as to make them manifold edges. It creates the minimum number of edges that can
    be created to make the edge manifold. The default value for -operation is 1, operate on manifold edges. Resulting mesh
    may have extra vertices or edges to ensure geometry is valid.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - operation : op                 (int)           []
    
    
    Derived from mel command `maya.cmds.polySplitEdge`
    """

    pass


def polyPinUV(*args, **kwargs):
    """
    This command is used to pin and unpin UVs. A pinnedUV is one which should not be modified.  Each UV has an associated
    pin weight, that defaults to 0.0 meaning that the UV is not pinned. If pin weight is set to 1.0 then it becomes fully
    pinned and UV tools should not modify that UV. If the pin weight is set to a value between 0.0 and 1.0 then UV tools
    should weight their changes to that UV accordingly.  UV pinning is not enforced by the shape node: it is up to each tool
    to decide whether it will obey the pin weights.
    
    Flags:
      - createHistory : ch             (bool)          [create,query,edit]
          For objects that have no construction history, this flag can be used to force the creation of construction history for
          pinning.  By default, history is not created if the object has no history.  Regardless of this flag, history is always
          created if the object already has history.
    
      - operation : op                 (int)           [create,query,edit]
          Operation to perform.  Valid values are: 0: Set pin weights on the selected UVs. 1: Set pin weights to zero for the
          selected UVs. 2: Remove pin weights from the entire mesh. 3: Invert pin weights of the entire mesh. Default is 0.
    
      - uvSetName : uvs                (unicode)       [create,query,edit]
          Specifies the name of the UV set to edit UVs on. If not specified the current UV set will be used if it exists.
    
      - value : v                      (float)         [create,query,edit]
          Specifies the pin value for the selected UV components. When specified multiple times, the values are assigned
          respectively to the specified UVs.                                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyPinUV`
    """

    pass


def polyBridgeEdge(*args, **kwargs):
    """
    Bridges two sets of edges.
    
    Flags:
      - bridgeOffset : bo              (int)           []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - curveType : ctp                (int)           []
    
      - direction : d                  (int)           []
    
      - divisions : dv                 (int)           []
    
      - frozen : fzn                   (bool)          []
    
      - inputCurve : inc               (PyNode)        []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - reverse : rev                  (bool)          []
    
      - smoothingAngle : sma           (float)         []
    
      - sourceDirection : sd           (int)           []
    
      - startVert1 : sv1               (int)           []
    
      - startVert2 : sv2               (int)           []
    
      - taper : tp                     (float)         []
    
      - taperCurve_FloatValue : cfv    (float)         []
    
      - taperCurve_Interp : ci         (int)           []
    
      - taperCurve_Position : cp       (float)         []
    
      - targetDirection : td           (int)           []
    
      - twist : twt                    (float)         []
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyBridgeEdge`
    """

    pass


def roundConstantRadius(*args, **kwargs):
    """
    This command generates constant radius NURBS fillets and NURBS corner surfaces for matching edge pairs on NURBS
    surfaces.  An edge pair is a matching pair of surface isoparms or trim edges. This command can handle more than one edge
    pair at a time. This command can also handle compoundedges, which is where an edge pair is composed of more than two
    surfaces.  Use the -saand -sbflags in this case. The results from this command are three surface var groups plus the
    name of the new roundConstantRadius dependency node, if history was on. The 1st var group contains trimmed copies of the
    original surfaces.  The 2nd var group contains the new NURBS fillet surfaces.  The 3rd var group contains the new NURBS
    corners (if any). A simple example of an edge pair is an edge of a NURBS cube, where two faces of the cube meet.  This
    command generates a NURBS fillet at the edge and trims back the faces. Another example is a NURBS cylinder with a planar
    trim surface cap. This command will create a NURBS fillet where the cap meets the the cylinder and will trim back the
    cap and the cylinder. Another example involves all 12 edges of a NURBS cube.  NURBS fillets are created where any face
    meets another face.  NURBS corners are created whenever 3 edges meet at a corner.
    
    Flags:
      - append : a                     (bool)          [create]
          If true, then an edge pair is being added to an existing round dependency node.  Default is false. When this flag is
          true, an existing round dependency node must be specified. See example below.
    
      - caching : cch                  (bool)          []
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           []
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - radius : r                     (float)         []
    
      - radiuss : rad                  (float)         [create]
          Use this flag to specify radius.  This overrides the r/radiusflag.  If only one radflag is used, then it is applied to
          all edge pairs.  If more than one radflag is used, then the number of -radflags must equal the number of edge pairs.
          For example, for four edge pairs, zero, one or four radflags must be specified.
    
      - side : s                       (unicode, int)  [create]
          Use this flag for compound edges.  It replaces the sidea/sideb flags and is compatible with Python.  The first argument
          must be either aor b.  The same number of avalues as bvalues must be specified. If no sides are specified with the
          sideflag (or sidea/sideb flags), then the edges are assumed to be in pairs. See also examples below. For example, two
          faces of a cube meet at an edge pair. Suppose one of the faces is then split in two pieces at the middle of the edge, so
          that there is one face on side A, and two pieces on side B.  In this case the flag combination: -side a1 -side b2 would
          be used. The edges must be specified in the corresponding order: // MEL roundConstantRadius -side a1 -side b2 isoA isoB1
          isoB2; # Python maya.cmds.roundConstantRadius( 'isoA', 'isoB1', 'isoB2', side=[(a,1), (b,2)] )
    
      - sidea : sa                     (int)           [create]
          Use this flag for compound edges in conjunction with the following -sbflag.  This flag is not intended for use from
          Python.  Please see sideflag instead.  The same number of -saflags as -sbflags must be specified. If no -sanor -sbflags
          are specified, then the edges are assumed to be in pairs. See also examples below. For example, two faces of a cube meet
          at an edge pair. Suppose one of the faces is then split in two pieces at the middle of the edge, so that there is one
          face on side A, and two pieces on side B.  In this case, the flag combination: -sidea 1 -sideb 2 would be used. The
          edges must be specified in the corresponding order: roundConstantRadius -sidea 1 -sideb 2 isoA isoB1 isoB2;
    
      - sideb : sb                     (int)           [create]
          Use this flag for compound edges in conjunction with the -saflag.  See description for the -saflag.  This flag is not
          intended for use from Python.  Please see sideflag instead.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
      - tolerance : tol                (float)         []
    
    
    Derived from mel command `maya.cmds.roundConstantRadius`
    """

    pass


def offsetCurveOnSurface(*args, **kwargs):
    """
    The offsetCurveOnSurface command offsets a curve on surface resulting in another curve on surface. The connecting type
    for breaks in offsets is off (no connection), circular (connect with an arc) or linear (connect linearly resulting in a
    sharp corner). If loop cutting is on then any loops in the offset curves are trimmed away and a sharp corner is created
    at each intersection. The subdivisionDensity flag is the maximum number of times the offset object can be subdivided
    (i.e. calculate the offset until the offset comes within tolerance or the iteration reaches this maximum.) The
    checkPoints flag sets the number of points per span at which the distance of the offset curve from the original curve is
    determined. The tolerance flag determines how accurately the offset curve should satisfy the required offset distance. A
    satisfactory offset curve is one for which all of the checkpoints are within the given tolerance of the required offset.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - checkPoints : cp               (int)           [create,query,edit]
          Checkpoints for fit quality per span. Not advisable to change this value. Default:3
    
      - connectBreaks : cb             (int)           [create,query,edit]
          Connect breaks method (between gaps): 0 - off, 1 - circular, 2 - linear Default:2
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - cutLoop : cl                   (bool)          [create,query,edit]
          Do loop cutting. Default:false
    
      - distance : d                   (float)         [create,query,edit]
          Offset distance Default:1.0
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.                  Advanced flags
    
      - stitch : st                    (bool)          [create,query,edit]
          Stitch curve segments together. Not advisable to change this value. Default:true
    
      - subdivisionDensity : sd        (int)           [create,query,edit]
          Maximum subdivision density per span Default:5
    
      - tolerance : tol                (float)         [create,query,edit]
          Tolerance Default:0.01                  Common flags
    
    
    Derived from mel command `maya.cmds.offsetCurveOnSurface`
    """

    pass


def polyEvaluate(*args, **kwargs):
    """
    Returns the required counts on the specified objects. If no objects are specified in the command line, then the objects
    from the active list are used. In MEL, the values are returned in the same order as the flags are set. Under Python,
    there is no concept of argument ordering, so the items are returned in a dictionary keyed by the name of the flag.  In
    Python, if only one item is requested, then it will not be returned in a dictionary. For user convenience, if no flag is
    set, then all values are echoed. All flags (except -fmt/format) are in fact query-flags. For user convenience, the -q
    flag may be ommitted. Some comments for non-formatted output :3d bounding boxes are returned as 3 couples of floats, 2d
    ones as 2 couples of floats.if a bounding box is queried and cannot be computed (for example the component bounding box
    when no component is selected, or 2d bounding box for and unmapped object) 0 is returned for each array element, so that
    indices in the output array remain consistent.intvalues (queried by topological flags) cannot be mixed with floatvalues
    (queried by bounding box flags). Thus if no flag is set, only intvalues are returned.
    
    Flags:
      - accurateEvaluation : ae        (bool)          [create]
          used to get accurate results for the bounding box computation For objects with large vertex counts, accurate evaluation
          takes more time
    
      - activeShells : activeShells    (bool)          []
    
      - area : a                       (bool)          [create]
          returns the surface area of the object's faces in local space as a float
    
      - boundingBox : b                (bool)          [create]
          returns the object's bounding box in 3d space as 6 floats in MEL: xmin xmax ymin ymax zmin zmax, or as a tuple of three
          pairs in Python: ((xmin,xmax), (ymin,ymax), (zmin,zmax))
    
      - boundingBox2d : b2             (bool)          [create]
          returns the object's uv bounding box (for the current map if one is not specified) in 2d space as 4 floats in MEL : xmin
          xmax ymin ymax, or as a tuple of three pairs in Python: ((xmin,xmax), (ymin,ymax), (zmin,zmax))
    
      - boundingBoxComponent : bc      (bool)          [create]
          returns the bounding box of selected components in 3d space as 6 floats in MEL : xmin xmax ymin ymax zmin zmax, or as a
          tuple of three pairs in Python: ((xmin,xmax), (ymin,ymax), (zmin,zmax))
    
      - boundingBoxComponent2d : bc2   (bool)          [create]
          returns the bounding box of selected uv coordinates in 2d space as 4 floats in MEL : xmin xmax ymin ymax, or as a tuple
          of two pairs in Python: ((xmin,xmax), (ymin,ymax))
    
      - displayStats : ds              (bool)          [create]
          toggles the display of poly statistics for the active View. All other flags are ignored if this flag is specified
          (Obsolete - refer to the headsUpDisplay command)
    
      - edge : e                       (bool)          [create]
          returns the number of edges as an int
    
      - edgeComponent : ec             (bool)          [create]
          returns the object's number of selected edges as an int
    
      - face : f                       (bool)          [create]
          returns the number of faces as an int
    
      - faceComponent : fc             (bool)          [create]
          returns the object's number of selected faces as an int
    
      - format : fmt                   (bool)          [create]
          used to display the results as an explicit sentence
    
      - shell : s                      (bool)          [create]
          returns the number of shells shells (disconnected pieces) as an int
    
      - triangle : t                   (bool)          [create]
          returns the number of triangles as an int
    
      - triangleComponent : tc         (bool)          [create]
          returns the number of triangles of selected components as an int
    
      - uvComponent : uvc              (bool)          [create]
          returns the object's number of selected uv coordinates as an int
    
      - uvSetName : uvs                (unicode)       [create]
          used when querying texture vertices to specify the uv set.  If a uv set is not specified then the current map for the
          object will be used
    
      - uvcoord : uv                   (bool)          [create]
          returns the number of uv coordinates (for the current map if one is not specified) as an int
    
      - vertex : v                     (bool)          [create]
          returns the number of vertices as an int
    
      - vertexComponent : vc           (bool)          [create]
          returns the object's number of selected vertices as an int
    
      - worldArea : wa                 (bool)          [create]
          returns the surface area of the object's faces in world space as a float                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyEvaluate`
    """

    pass


def filterExpand(*args, **kwargs):
    """
    Based on selected components (or components specified on the command line), the command filters and/or expands the list
    given the options. Returns a string array containing all matching selection items. Selection masks are as follows:
    Object TypeMaskHandle                        0            Nurbs Curves                    9            Nurbs Surfaces
    10        Nurbs Curves    On Surface         11        Polygon                         12        Locator XYZ
    22        Orientation Locator            23        Locator UV                    24        Control Vertices (CVs)
    28        Edit Points                    30        Polygon Vertices             31        Polygon Edges
    32        Polygon Face                    34        Polygon UVs                     35        Subdivision Mesh Points
    36        Subdivision Mesh Edges        37        Subdivision Mesh Faces        38        Curve Parameter Points
    39        Curve Knot                    40        Surface Parameter Points         41        Surface Knot
    42        Surface Range                43        Trim Surface Edge            44        Surface Isoparms             45
    Lattice Points                46        Particles                    47        Scale Pivots                    49
    Rotate Pivots                50        Select Handles                51        Subdivision Surface            68
    Polygon Vertex Face             70        NURBS Surface Face             72        Subdivision Mesh UVs            73
    
    Flags:
      - expand : ex                    (bool)          [create]
          Each item is a single entity if this is true.  Default is true.
    
      - fullPath : fp                  (bool)          [create]
          If this is true and the selection item is a DAG object, return its full selection path, instead of the name of the
          object only when this value is false.  Default is false.
    
      - selectionMask : sm             (int)           [create]
          Specify the selection mask
    
      - symActive : sma                (bool)          [create]
          If symmetry is enabled only return the components on the active symmetry side of the object. This flag has no effect if
          symmetry is not active.
    
      - symNegative : smn              (bool)          [create]
          If symmetry is enabled only return the components on the negative side of the object relative to the current symmetry
          plane. This flag has no effect if symmetry is not active.
    
      - symPositive : smp              (bool)          [create]
          If symmetry is enabled only return the components on the positive side of the object relative to the current symmetry
          plane. This flag has no effect if symmetry is not active.
    
      - symSeam : sms                  (bool)          [create]
          If symmetry is enabled only return the components that lie equally on both sides of the object relative to the current
          symmetry plane. This flag has no effect if symmetry is not active.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.filterExpand`
    """

    pass


def polyQueryBlindData(*args, **kwargs):
    """
    Command query's blindData associated with particular polygonal components. So, the command will require the following to
    be specified:         - selection list to query Optional are the:         - typeId         - associationType         -
    longDataName or shortDataName of data being queried.         - The actual data being specified.         - showComponent
    flag Note that for object level blind data, the showComponent flag will be ignored. If no components are selected, the
    assocation flag will be ignored and object level data will be queried.
    
    Flags:
      - associationType : at           (unicode)       [create]
          Specifies the dataTypes that are part of BlindData node being queried. Allowable associations are objectfor any object,
          and vertexedgeand facefor mesh objects.
    
      - binaryData : bnd               (unicode)       [create]
          Specifies the binary string value to search for
    
      - booleanData : bd               (bool)          [create]
          Specifies the string value to search for
    
      - doubleData : dbd               (float)         [create]
          Specifies the double/float value to search for
    
      - intData : ind                  (int)           [create]
          Specifies the integer value to search for
    
      - longDataName : ldn             (unicode)       [create]
          Specifies the long name of the data that is being queried by this command.
    
      - maxValue : max                 (float)         [create]
          Specifies the maximum value to search for.  This option will query float, double, and integer types of blind data.
    
      - minValue : min                 (float)         [create]
          Specifies the minimum value to search for.  This option will query float, double and integer types of blind data.
    
      - shortDataName : sdn            (unicode)       [create]
          Specifies the short name of the data that is being queried by this command.
    
      - showComp : sc                  (bool)          [create]
          The showComponent option controls whether the object.[component].attribute name is output preceeding the actual value.
          If the showComponent option is used then the restriction of only returning 1 type of blind data (i.e. one of integer,
          float, double... is removed, as the return for all are strings. If the association is object and not component, then
          this option will still cause all the attribute names to be printed
    
      - stringData : sd                (unicode)       [create]
          Specifies the string value to search for
    
      - subString : ss                 (unicode)       [create]
          Specifies the substring that should be checked against a STRING type blind data.  If the sub string is found query is
          successful.  Will not look at non String type blind data elements.
    
      - typeId : id                    (int)           [create]
          Specifies the typeId of the BlindData type being queried.  If the typeId is not specified, then all of the components
          that match the query will be output.  The typeId of the elements found will be output if the ShowComponents option is
          used.  Will be in the format object.component.attribute::typeId. If the typeId is specifed then the ::typeIdportion will
          not be output with the ShowComponents option.                                 Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyQueryBlindData`
    """

    pass


def untangleUV(*args, **kwargs):
    """
    This command will aid in the creation of non-overlapping regions (i.e. polygons) in texture space by untangling texture
    UVs. This is done in two stages:1) Use this command to map the UV border determined by the current selection or passed
    component into a shape that is more suitable for subsequent relaxation.2) Relax all the internal texture UVs by
    performing a length minimization algorithm on all edges in texture space.
    
    Flags:
      - mapBorder : mb                 (unicode)       [create]
          Map the border containing the selected UV into a variety of shapes that may be more amenable to UV relaxation
          operations. There are various types of mapping available. All the resulting mappings are fit inside the unit
          square.Valid values for the STRING are:circular- a circular mapping with picked UV closest to (0,0)square- map to unit
          square with picked UV at (0,0)shape- a mapping which attempts to reflect the actual shape of the object         where
          the picked UV is placed on the line from (0,0) -(0.5,0.5)shape_circular- shape mapping which will interpolate to a
          circular mapping                  just enough to prevent self-intersections of the mapped border shape_square- shape
          mapping which will interpolate to a square mapping just                enough to prevent self-intersections of the
          mapped border
    
      - maxRelaxIterations : mri       (int)           [create]
          The relaxation process is an iterative algorithm. Using this flag will put an upper limit on the number of iterations
          that will be performed.
    
      - pinBorder : pb                 (bool)          [create]
          If this is true, then the relevant texture borders are pinned in place during any relaxation
    
      - pinSelected : ps               (bool)          [create]
          If this is true, then then any selected UVs are pinned in place during any relaxation
    
      - pinUnselected : pu             (bool)          [create]
          If this is true, then all unselected UVs in each mesh are pinned in place during any relaxation
    
      - relax : r                      (unicode)       [create]
          Relax all UVs in the shell of the selected UV's. The relaxation is done by simulating a spring system where each UV edge
          is treated as a spring. There are a number of different methods characterized by the way the UV edges are weighted in
          the spring system. These weightings are determined by STRING. Valid values for STRING are:uniform- every edge is
          weighted the same. This is the fastest method.inverse_length- every edge weight is inversely proportional to it's world
          space length.inverse_sqrt_length- every edge weight is inversely proportional the the square root of it's world space
          length.harmonic- this weighting can yield near optimal results in matching the UV's with the geometry, but can also take
          a long time.
    
      - relaxTolerance : rt            (float)         [create]
          This sets the tolerance which is used to determine when the relaxation process can stop. Smaller tolerances yield better
          results but can take much longer.
    
      - shapeDetail : sd               (float)         [create]
          If the mapBorder flag is set to circular or square, then this flag will control how much of the border's corresponding
          surface shape should be retained in the final mapped border.                                Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.untangleUV`
    """

    pass


def polyPipe(*args, **kwargs):
    """
    The polyPipe command creates a new polygonal pipe.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the pipe. Q: When queried, this flag returns a float[3].
    
      - caching : cch                  (bool)          [query,edit]
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (bool)          [create,query,edit]
          This flag alows a texture to be applied. C: Default is on(uv's are computed). Q: When queried, this flag returns an int.
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - height : h                     (float)         [create,query,edit]
          This flag specifies the height of the pipe. C: Default is 2.0. Q: When queried, this flag returns a float.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - radius : r                     (float)         [create,query,edit]
          This flag specifies the outer radius of the pipe. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - roundCap : rcp                 (bool)          [query,edit]
    
      - subdivisionsAxis : sa          (int)           [query,edit]
    
      - subdivisionsCaps : sc          (int)           [create,query,edit]
          This flag specifies the number of subdivisions along the thickness of the pipe. C: Default is 0. Q: When queried, this
          flag returns an int.
    
      - subdivisionsHeight : sh        (int)           [create,query,edit]
          This flag specifies the number of subdivisions along the height of the pipe. C: Default is 1. Q: When queried, this flag
          returns an int.
    
      - texture : tx                   (bool)          [create]
          This flag is obsolete and will be removed in the next release. The -cuv/createUVs flag should be used instead.
    
      - thickness : t                  (float)         [create,query,edit]
          This specifies the thickness of the pipe. C: Default is 0.5. Q: When queried, this flag returns an float.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyPipe`
    """

    pass


def geomToBBox(*args, **kwargs):
    """
    Create polygonal mesh bounding boxes for geometry. Can also create a single bounding box per hierarchy.
    
    Flags:
      - bakeAnimation : ba             (bool)          [create]
          Bake the animation. Can be used with startTime, endTime and sampleBy flags. If used alone, the time slider will be used
          to specify the startTime and endTime.
    
      - combineMesh : cm               (bool)          [create]
          Combine resulting bounding boxes. Mutually exclusive with -s/single option.
    
      - endTime : et                   (time)          [create]
          Used with bakeAnimation flag. Specifies the end time of the baking process.
    
      - keepOriginal : ko              (bool)          [create]
          Do not remove the selected nodes used to create the bounding boxes.
    
      - name : n                       (unicode)       [create]
          Specifies the bounding box name.
    
      - nameSuffix : ns                (unicode)       [create]
          Specifies the bounding box name suffix.
    
      - sampleBy : sb                  (time)          [create]
          Used with bakeAnimation flag. Specifies the animation evaluation time increment.
    
      - shaderColor : sc               (float, float, float) [create]
          Set the color attribute of the Lambert material associate with the bounding box. The RGB values should be defined
          between 0 to 1.0. Default value is 0.5 0.5 0.5.
    
      - single : s                     (bool)          [create]
          Create a single bounding box per hierarchy selected.
    
      - startTime : st                 (time)          [create]
          Used with bakeAnimation flag. Specifies the start time of the baking process.                              Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.geomToBBox`
    """

    pass


def detachCurve(*args, **kwargs):
    """
    The detachCurve command detaches a curve into pieces, given a list of parameter values.  You can also specify which
    pieces to keep and which to discard using the -kflag. The names of the newly detached curve(s) is returned.  If history
    is on, then the name of the resulting dependency node is also returned. You can use this command to open a periodic
    curve at a particular parameter value.  You would use this command with only one -pflag. If you are specifying -kflags,
    then you must specify one, none or all -kflags.  If you are specifying all -kflags, there must be one more -kflag than
    -pflags.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curveOnSurface : cos           (bool)          [create]
          If possible, create 2D curve as a result.
    
      - frozen : fzn                   (bool)          []
    
      - keep : k                       (bool)          [create,query,edit]
          Whether or not to keep a detached piece.  This multi attribute should be one element larger than the parameter multi
          attribute. Default:true
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - parameter : p                  (float)         [create,query,edit]
          Parameter values to detach at Default:0.0                  Common flags
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
    
    Derived from mel command `maya.cmds.detachCurve`
    """

    pass


def polyNormalPerVertex(*args, **kwargs):
    """
    Command associates normal(x, y, z) with vertices on polygonal objects. When used with the query flag, it returns the
    normal associated with the specified components. However, when queried, the command returns all normals (all vtx-face
    combinations) on the vertex, regardless of whether they are shared or not.
    
    Flags:
      - allLocked : al                 (bool)          [create,query,edit]
          Queries if all normals on the selected vertices are locked (frozen) or not
    
      - deformable : deformable        (bool)          [create,query,edit]
          DEFAULT  true OBSOLETE flag. This flag will be removed in the next release.
    
      - freezeNormal : fn              (bool)          [create,query,edit]
          Specifies that the normal values be frozen (locked) at the current value.
    
      - normalX : x                    (float)         [create,query,edit]
          Specifies the x value normal
    
      - normalXYZ : xyz                (float, float, float) [create,query,edit]
          Specifies the xyz values normal If this flag is used singly, the specified normal xyz values are used for all selected
          components. If the flag is used multiple times, the number of uses must match the number of selected components, and
          each use specifies the normal of one component.
    
      - normalY : y                    (float)         [create,query,edit]
          Specifies the y value normal
    
      - normalZ : z                    (float)         [create,query,edit]
          Specifies the z value normal
    
      - relative : rel                 (bool)          [create,query,edit]
          When used, the normal values specified are added relative to the current value.
    
      - unFreezeNormal : ufn           (bool)          [create,query,edit]
          Specifies that the normal values that were frozen at the current value be un-frozen (un-locked).                  Flag
          can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyNormalPerVertex`
    """

    pass


def stitchSurfacePoints(*args, **kwargs):
    """
    The stitchSurfacePoints command aligns two or more surface points along the boundaries together to a single point. In
    the process, a node to average the points is created. The points are averaged together in a weighted fashion. The points
    may be control vertices along the boundaries. If the points are CVs then they are stitched together only with positional
    continuity. Note: No two points can lie on the same surface.
    
    Flags:
      - bias : b                       (float)         [create,query,edit]
          Blend CVs in between input surface and result from stitch. A value of 0.0 returns the input surface. Default:1.0
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - cascade : c                    (bool)          [create]
          Cascade the created stitch node. (Only if the surface has a stitch history) Default is 'false'.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - cvIthIndex : ci                (int)           [create,query,edit]
          The ith boundary CV index on the input surface. Default:-1
    
      - cvJthIndex : cj                (int)           [create,query,edit]
          The jth boundary CV index on the input surface. Default:-1
    
      - equalWeight : ewt              (bool)          [create]
          Assign equal weights to all the points being stitched together. Default is 'true'. If false, the first point is assigned
          a weight of 1.0 and the rest are assigned 0.0.
    
      - fixBoundary : fb               (bool)          [create,query,edit]
          Fix Boundary CVs while solving for any G1 constraints. Default:false
    
      - frozen : fzn                   (bool)          []
    
      - keepG0Continuity : kg0         (bool)          [create]
          Stitch together the points with positional continuity. Default is 'true'.
    
      - keepG1Continuity : kg1         (bool)          [create]
          Stitch together the points with tangent continuity. Default is 'false'.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - parameterU : u                 (float)         [create,query,edit]
          The U parameter value on surface for a point constraint. Default:-10000
    
      - parameterV : v                 (float)         [create,query,edit]
          The V parameter value on surface for a point constraint. Default:-10000
    
      - positionalContinuity : pc      (bool)          [create,query,edit]
          Toggle on (off) G0 continuity at edge corresponding to multi index. Default:true
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - stepCount : sc                 (int)           [create,query,edit]
          Step count for the number of discretizations. Default:20
    
      - tangentialContinuity : tc      (bool)          [create,query,edit]
          Toggle on (off) G1 continuity across edge corresponding to multi index. Default:false
    
      - togglePointNormals : tpn       (bool)          [create,query,edit]
          Toggle on (off) normal point constraints on the surface. Default:false
    
      - togglePointPosition : tpp      (bool)          [create,query,edit]
          Toggle on (off) position point constraints on the surface. Default:true
    
      - toggleTolerance : tt           (bool)          [create,query,edit]
          Toggle on (off) so as to use Tolerance or specified steps for discretization. Default:false
    
      - tolerance : tol                (float)         [create,query,edit]
          Tolerance to use while discretizing the edge. Default:0.1                  Common flags
    
    
    Derived from mel command `maya.cmds.stitchSurfacePoints`
    """

    pass


def duplicateCurve(*args, **kwargs):
    """
    The duplicateCurve command takes a curve on a surface and and returns the 3D curve. The curve on a surface could be
    isoparam component, trimmed edge or curve on surface object.
    
    Flags:
      - caching : cch                  (bool)          []
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off (where applicable).
    
      - frozen : fzn                   (bool)          []
    
      - local : l                      (bool)          [create]
          Copy the transform of the surface and connect to the local space version instead.
    
      - maxValue : max                 (float)         []
    
      - mergeItems : mi                (bool)          []
    
      - minValue : min                 (float)         []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           []
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node (where applicable).
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve (where applicable).                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - relative : r                   (bool)          []
    
    
    Derived from mel command `maya.cmds.duplicateCurve`
    """

    pass


def nurbsSquare(*args, **kwargs):
    """
    The nurbsSquare command creates a square
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - center : c                     (float, float, float) [create,query,edit]
          The center point of the square.
    
      - centerX : cx                   (float)         [create,query,edit]
          X of the center point. Default:0
    
      - centerY : cy                   (float)         [create,query,edit]
          Y of the center point. Default:0
    
      - centerZ : cz                   (float)         [create,query,edit]
          Z of the center point. Default:0
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting circle: 1 - linear, 2 - quadratic, 3 - cubic, 5 - quintic, 7 - heptic Default:3
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - normal : nr                    (float, float, float) [create,query,edit]
          The normal of the plane in which the square will lie.
    
      - normalX : nrx                  (float)         [create,query,edit]
          X of the normal direction. Default:0
    
      - normalY : nry                  (float)         [create,query,edit]
          Y of the normal direction. Default:0
    
      - normalZ : nrz                  (float)         [create,query,edit]
          Z of the normal direction. Default:1
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.                  Advanced flags
    
      - sideLength1 : sl1              (float)         [create,query,edit]
          The length of a side on the square. Default:1.0
    
      - sideLength2 : sl2              (float)         [create,query,edit]
          The length of an adjacent side on the square. Default:1.0
    
      - spansPerSide : sps             (int)           [create,query,edit]
          The number of spans per side determines the resolution of the square. Default:1                  Common flags
    
    
    Derived from mel command `maya.cmds.nurbsSquare`
    """

    pass


def polyCompare(*args, **kwargs):
    """
    Compares two Polygonal Geometry objects with a fine control on what to compare. If no objects are specified in the
    command line, then the objects from the active list are used. Default behaviour is to compare all flags. Use MEL script
    polyCompareTwoObjects.mel to get formatted output from this command.
    
    Flags:
      - colorSetIndices : ic           (bool)          [create]
          Compare poly1, poly2 for matching Color Indices.
    
      - colorSets : c                  (bool)          [create]
          Compare poly1, poly2 for matching Color Sets.
    
      - edges : e                      (bool)          [create]
          Compare poly1, poly2 for matching Edges.
    
      - faceDesc : fd                  (bool)          [create]
          Compare poly1, poly2 for matching Face Descriptions. Face descriptions describe the topology of a face, for example
          number and orientation of edges, number of topology of any holes in the face etc.
    
      - userNormals : un               (bool)          [create]
          Compare poly1, poly2 for matching User Normals.
    
      - uvSetIndices : iuv             (bool)          [create]
          Compare poly1, poly2 for matching UV Indices.
    
      - uvSets : uv                    (bool)          [create]
          Compare poly1, poly2 for matching UV Sets.
    
      - vertices : v                   (bool)          [create]
          Compare poly1, poly2 for matching Vertices.                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.polyCompare`
    """

    pass


def polyOptions(*args, **kwargs):
    """
    Changes the global display polygonal attributes.                 In query mode, return type is based on queried flag.
    
    Flags:
      - activeObjects : ao             (bool)          [create,query]
          Apply user choices for all active objects.
    
      - allEdges : ae                  (bool)          [create,query]
          Display all edges in solid line.
    
      - backCullVertex : bcv           (bool)          [create,query]
          BackCull vertices.
    
      - backCulling : bc               (bool)          [create,query]
          Display with no back culling.
    
      - colorMaterialChannel : cm      (unicode)       [create,query]
          If colorShadedDisplay is true, then determines which material channel to display color per vertex in. The options are:
          none: disable material shadingambient: ambient material channelambientDiffuse:  ambient and diffuse material
          channeldiffuse:  diffuse material channelspecular:  specular material channelemission:  emission material channel
    
      - colorShadedDisplay : cs        (bool)          [create,query]
          Use color per vertex display in shaded mode.
    
      - displayAlphaAsGreyScale : dal  (bool)          [create,query]
          Display alpha as grey scale.
    
      - displayBorder : db             (bool)          [create,query]
          Highlight border edge.
    
      - displayCenter : dc             (bool)          [create,query]
          Display facet centers.
    
      - displayCreaseEdge : dce        (bool)          [create,query]
          Highlight creased edges
    
      - displayCreaseVertex : dcv      (bool)          [create,query]
          Highlight creased vertices
    
      - displayGeometry : dg           (bool)          [create,query]
          Display geometry.
    
      - displayInvisibleFaces : dif    (bool)          [create,query]
          Highlight invisible faces
    
      - displayItemNumbers : din       (bool, bool, bool, bool) [create,query]
          Displays item numbers (vertices edges facets uvs)
    
      - displayMapBorder : dmb         (bool)          [create,query]
          Highlight map border edge.
    
      - displayMetadata : dmt          (bool, bool, bool) [create,query]
          Displays component metadata (vertices edges facets vertexFaces)
    
      - displayNormal : dn             (bool)          [create,query]
          Display normals.
    
      - displayShellBorder : dsb       (bool)          []
    
      - displaySubdComps : dsc         (bool)          [create,query]
          Display subdivided components when in Smooth Mesh Preview mode.
    
      - displayTangent : dtn           (bool)          []
    
      - displayTriangle : dt           (bool)          [create,query]
          Display triangulation.
    
      - displayUVTopology : uvt        (bool)          [create,query]
          Option on UV display to display UVs topologically.
    
      - displayUVs : duv               (bool)          [create,query]
          Display UVs.
    
      - displayVertex : dv             (bool)          [create,query]
          Display vertices.
    
      - displayWarp : dw               (bool)          [create,query]
          Highlight warped facets.
    
      - facet : f                      (bool)          [create,query]
          For use with -dn flag. Set the normal display style to facet display.
    
      - fullBack : fb                  (bool)          [create,query]
          Display with full back culling.
    
      - gl : gl                        (bool)          [create,query]
          Apply user choices for all objects.
    
      - hardBack : hb                  (bool)          [create,query]
          Backculled hard edges only for backculled faces.
    
      - hardEdge : he                  (bool)          [create,query]
          Display only hard edges.
    
      - hardEdgeColor : hec            (bool)          [create,query]
          Display hard edges as separate color.
    
      - materialBlend : mb             (unicode)       [create,query]
          The options are: overwriteaddsubtractmultiplydivideaveragemodulate2x
    
      - newPolymesh : np               (bool)          [create,query]
          Set component display state of new polymesh objects.
    
      - point : pt                     (bool)          [create,query]
          For use with -dn flag. Set the normal display style to vertex display.
    
      - pointFacet : pf                (bool)          [create,query]
          For use with -dn flag. Set the normal display style to vertex and face display.
    
      - relative : r                   (bool)          [create,query]
          When this flag is used with flags dealing with size, the value (size) is a multiplication factor : i.e for flags :
          -sizeNormal, -sizeBorder. When this flag is used with flags dealing with a boolean value, the boolean value is toggled :
          i.e for flags : displayVertex, displayCenter, displayTriangle, displayBorder, backCullVertex, displayWarp,
          displayItemNumbers.
    
      - reuseTriangles : rt            (bool)          [create,query]
          Avoid regenerating triangles, by reusing the old triangles upstream in the construction history.  The construction
          history is searched upstream and downstream for other mesh nodes, and the given boolean value is set on those mesh
          nodes.  Note, that this command does not set the value on the given mesh node.  That has to be done using the setAttr
          command. This option would affect only the interactive 3d viewport. The batch-rendering would use the properly computed
          triangles. This is useful only for interactive performance such as skinning playback, when the display mode is shaded
          (or wireframe with triangles displayed)  Using this option for wireframe display mode is not recomended.
    
      - sizeBorder : sb                (float)         [create,query]
          Set the size of the polygonal border edges.
    
      - sizeNormal : sn                (float)         [create,query]
          Set the size of the polygonal normals.
    
      - sizeUV : suv                   (float)         [create,query]
          Set the size of the polygonal UV.
    
      - sizeVertex : sv                (float)         [create,query]
          Set the size of the polygonal vertex.
    
      - smoothDrawType : sdt           (int)           [create,query]
          This setting only works with the newPolymesh flag. Sets a new default attribute value for the smoothDrawType attribute
          on a polymesh object. Options are: 0: Catmull-Clark 1: Linear 2: OpenSubdiv Catmull-Clark Uniform 3: OpenSubdiv Catmull-
          Clark Adaptive
    
      - softEdge : se                  (bool)          [create,query]
          Display soft edges in dotted lines.
    
      - vertexNormalMethod : vnm       (int)           [create,query]
          This setting only works with the newPolymesh flag. Sets a new default attribute value for the vertexNormalMethod
          attribute on a polymesh object. Options are: 0: Unweighted 1: Angle Weighted 2: Area Weighted 3: Angle And Area Weighted
    
      - wireBackCulling : wbc          (bool)          [create,query]
          Backculled faces are in wireframe.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.polyOptions`
    """

    pass


def manipPivot(*args, **kwargs):
    """
    Changes transform component pivot used by the move/rotate/scale manipulators.            In query mode, return type is
    based on queried flag.
    
    Flags:
      - ori : o                        (float, float, float) [create,query]
          Component pivot orientation in world-space.
    
      - oriValid : ov                  (bool)          [query]
          Returns true if component pivot orientation is valid.
    
      - orientation : o                (float, float, float) []
    
      - pinPivot : pin                 (bool)          [create,query]
          Pin component pivot. Selection changes will not reset the pivot position/orientation when a custom pivot is set and
          pinning is on.
    
      - pos : p                        (float, float, float) [create,query]
          Component pivot position in world-space.
    
      - posValid : pv                  (bool)          [query]
          Returns true if component pivot position is valid.
    
      - position : p                   (float, float, float) []
    
      - reset : r                      (bool)          [create]
          Clear the saved component pivot position and orientation.
    
      - resetOri : ro                  (bool)          [create]
          Clear the saved component pivot orientation.
    
      - resetPos : rp                  (bool)          [create]
          Clear the saved component pivot position.
    
      - snapOri : so                   (bool)          [create,query]
          Snap pivot orientation. Modify pivot orientation when snapping the pivot to a component.
    
      - snapPos : sp                   (bool)          [create,query]
          Snap pivot position. Modify pivot position when snapping the pivot to a component.
    
      - valid : v                      (bool)          [query]
          Returns true if component pivot position or orientation is valid.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.manipPivot`
    """

    pass


def polyPlane(*args, **kwargs):
    """
    The mesh command creates a new polygonal plane.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the plane.
    
      - caching : cch                  (bool)          [query,edit]
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (int)           [create]
          This flag alows a specific UV mechanism to be selected, while creating the plane. The valid values are 0, 1 or  2. 0
          implies that no UVs will be generated (No texture to be applied). 1 implies UVs should be created for the object as a
          whole without any normalization. The texture will be applied on the plane without any distortion. 2 implies UVs are
          created so that the texture will not be distorted when applied. The texture lying outside the UV range will be truncated
          (since that cannot be squeezed in), without distorting the texture. For better understanding of these options, you may
          have to open the texture view windowC: Default is 1.
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - height : h                     (float)         [create,query,edit]
          This flag specifies the height of the plane. Default is 1.0.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - subdivisionsHeight : sh        (int)           [query,edit]
    
      - subdivisionsWidth : sw         (int)           [query,edit]
    
      - subdivisionsX : sx             (int)           [create,query,edit]
          This specifies the number of subdivisions in the X direction for the plane. Default is 5.
    
      - subdivisionsY : sy             (int)           [create,query,edit]
          This flag specifies the number of subdivisions in the Y direction for the plane. Default is 5.
    
      - texture : tx                   (int)           [create]
          This flag is obsolete and will be removed in the next release. The cuv/createUVs flag should be used instead.
    
      - width : w                      (float)         [create,query,edit]
          This flag specifies the width of the plane. Default is 1.0.                  Common flags
    
    
    Derived from mel command `maya.cmds.polyPlane`
    """

    pass


def setXformManip(*args, **kwargs):
    """
    This command changes some of the settings of the xform manip, to control its appearance. In query mode, return type is
    based on queried flag.
    
    Flags:
      - showUnits : su                 (bool)          [query]
          If set to true, the xform manip displays current units; otherwise, the manip hides them.
    
      - suppress : s                   (bool)          [query]
          If set to true, the xform manip is suppressed and therefore not visible or usable.
    
      - useRotatePivot : urp           (bool)          [query]
          If set to true, the xform manip uses the rotate pivot; otherwise, the manip uses the bounding-box center. Defaults
          false.
    
      - worldSpace : ws                (bool)          [query]
          If set to true, the xform manip is always in world space. If false, the manip is in object space. (Note: when multiple
          objects are selected the manip is always in world space, no matter what this is set to)                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.setXformManip`
    """

    pass


def subdiv(*args, **kwargs):
    """
    Provides useful information about the selected subdiv or components, such as the deepest subdivided level, the children
    or parents of the currently selected components, etc.            In query mode, return type is based on queried flag.
    
    Flags:
      - currentLevel : cl              (bool)          [create,query]
          When queried, this flag returns an integer representing the level of the currently selected subdiv surface component(s).
          Returns -1, if there are more than one level of CVs are selected, (even if they are from different objects) Returns -2,
          if there are no input subdiv CVs to process.
    
      - currentSubdLevel : csl         (bool)          [create,query]
          When queried, this flag returns an integer representing the level of the currently selected subdiv surface, regardless
          of whether components are selected or not. Returns -2, if there are no input subdiv CVs to process.
    
      - deepestLevel : dl              (int)           [create,query]
          When queried, this flag returns an integer representing the deepest level to which the queried subdiv surface has been
          subdivided.
    
      - displayLoad : dsl              (bool)          [create,query]
          When queried, this flag prints the display load of selected subdiv
    
      - edgeStats : est                (bool)          [create,query]
          When queried, this flag prints stats on the current subd.
    
      - faceStats : fst                (bool)          [create,query]
          When queried, this flag prints stats on the current subd.
    
      - maxPossibleLevel : mpl         (int)           [create,query]
          When queried, this flag returns an integer representing the maximum possible level to which the queried subdiv surface
          can been subdivided.
    
      - proxyMode : pm                 (int)           [create,query]
          When queried, this flag returns an integer representing whether or not the subdivision surface is in polygon proxymode.
          Proxymode allows the base mesh of a subdivision surface without construction history to be edited using the polygonal
          editing tools. Returns 1, if the subdivision surface is in polygon proxymode. Returns 0, if the surface is not currently
          in proxymode, but could be put into proxymode since it has no construction history.  (This state is also known as
          standardmode.) Returns 2, if the surface is not in proxymode and cannot be put into proxy mode, as it has construction
          history.
    
      - smallOffsets : so              (bool)          [create,query]
          When queried, this flag prints the number of subdiv vertices in the hierarchy that have a small enough offset so that
          the vertex is not required                                   Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.subdiv`
    """

    pass


def polyCollapseFacet(*args, **kwargs):
    """
    Turns each selected facet into a point.
    
    Flags:
      - areaThreshold : at             (float)         []
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - useAreaThreshold : uat         (bool)          []
    
    
    Derived from mel command `maya.cmds.polyCollapseFacet`
    """

    pass


def polyDelEdge(*args, **kwargs):
    """
    Deletes selected edges, and merges neighboring faces. If deletion leaves winged vertices, they may be deleted as well.
    Notice : only non border edges can be deleted.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - cleanVertices : cv             (bool)          [create,query,edit]
          If on : delete resulting winged vertices. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyDelEdge`
    """

    pass


def polyColorSet(*args, **kwargs):
    """
    Command to do the following to color sets:         - delete an existing color set.         - rename an existing color
    set.     - create a new empty color set.         - set the current color set to a pre-existing color set.     - modify
    sharing between instances of per-instance color sets     - query the current color set.     - query the names of all
    color sets.         - query the name(s) along with representation value(s)       or clamped value(s) of all color sets
    - query the representation value or clamped value of the current color set
    
    Flags:
      - allColorSets : acs             (bool)          [create,query,edit]
          This flag when used in a query will return a list of all of the color set names
    
      - clamped : cla                  (bool)          [create,query,edit]
          This flag specifies if the color set will truncate any value that is outside 0 to 1 range.
    
      - colorSet : cs                  (unicode)       [create,query,edit]
          Specifies the name of the color set that this command needs to work on. This flag has to be specified for this command
          to do anything meaningful other than query the current color set.
    
      - copy : cp                      (bool)          [create,query,edit]
          This flag when used will result in the copying of the color set corresponding to name specified with the colorSet flag
          to the colorSet corresponding to the name specified with the newcolorSet flag
    
      - create : cr                    (bool)          [create,query,edit]
          This flag when used will result in the creation of an empty color set corresponding to the name specified with the
          colorSet flag. If a color set with that name already exists, then no new color set will be created.
    
      - currentColorSet : ccs          (bool)          [create,query,edit]
          This flag when used will set the current color set that the object needs to work on, to be the color set corresponding
          to the name specified with the colorSet flag. This does require that a colorSet with the specified name exist. When
          queried, this returns the current color set.
    
      - currentPerInstanceSet : cpi    (bool)          [query,edit]
          This is a query-only flag for use when the current color set is a per-instance color set family. This returns the member
          of the set family that corresponds to the currently select instance.
    
      - delete : d                     (bool)          [create,query,edit]
          This flag when used will result in the deletion of the color set corresponding to the name specified with the colorSet
          flag.
    
      - newColorSet : nc               (unicode)       [create,query,edit]
          Specifies the name that the color set corresponding to the name specified with the colorSet flag, needs to be renamed
          to.
    
      - perInstance : pi               (bool)          [create,query,edit]
          This flag can be used in conjunction with the create flag to indicate whether or not the color set is per-instance. When
          you create a per-instance color set, the set will be applied as shared between all selected instances of the shape
          unless the unshared flag is used. The perInstance flag can be used in query mode with the currentColorSet or
          allColorSets flag to indicate that the set family names (i.e. not containing instance identifiers) will be returned by
          the query. In query mode, this flag can accept a value.
    
      - rename : rn                    (bool)          [create,query,edit]
          This flag when used will result in the renaming of the color set corresponding to the name specified with the colorSet
          flag to the name specified using the newColorSet flag.
    
      - representation : rpt           (unicode)       [create,query,edit]
          This flag corresponds to the color channels to used, for example A(alpha only), RGB, and RGBA.
    
      - shareInstances : si            (bool)          [create,query,edit]
          This flag is used to modify the sharing of per-instance color sets within a given color set family so that all selected
          instances share the specified set. In query mode, it returns a list of the instances that share the set specified by the
          colorSet flag.
    
      - unshared : us                  (bool)          [create,query,edit]
          This flag can be used in conjunction with the create and perInstance flags to indicate that the newly created per-
          instance set should be created with a separate set per instance.                                 Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyColorSet`
    """

    pass


def alignCurve(*args, **kwargs):
    """
    The curve align command is used to align curves in maya. The main alignment options are positional, tangent and
    curvature continuity. Curvature continuity implies tangent continuity. Positional continuity means the curves (move) or
    the ends of the curves (modify) are changed. Tangent continuity means one of the curves is modified to be tangent at the
    points where they meet. Curvature continuity means one of the curves is modified to be curvature continuous as well as
    tangent. The default behaviour, when no curves or flags are passed, is to only do positional and tangent continuity on
    the active list with the end of the first curve and the start of the other curve used for alignment.
    
    Flags:
      - attach : at                    (bool)          []
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curvatureContinuity : cc       (bool)          [create,query,edit]
          Curvature continuity is on if true and off otherwise. Default:false
    
      - curvatureScale1 : cs1          (float)         [create,query,edit]
          Curvature scale applied to curvature of first curve for curvature continuity. Default:0.0
    
      - curvatureScale2 : cs2          (float)         [create,query,edit]
          Curvature scale applied to curvature of second curve for curvature continuity. Default:0.0
    
      - frozen : fzn                   (bool)          []
    
      - joinParameter : jnp            (float)         [create,query,edit]
          Parameter on reference curve where modified curve is to be aligned to. Default:123456.0
    
      - keepMultipleKnots : kmk        (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - positionalContinuity : pc      (bool)          [create,query,edit]
          Positional continuity is on if true and off otherwise. Default:true
    
      - positionalContinuityType : pct (int)           [create,query,edit]
          Positional continuity type legal values: 1 - move first curve, 2 - move second curve, 3 - move both curves, 4 - modify
          first curve, 5 - modify second curve, 6 - modify both curves Default:1
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - reverse1 : rv1                 (bool)          [create,query,edit]
          If true, reverse the first input curve before doing align. Otherwise, do nothing to the first input curve before
          aligning. NOTE: setting this attribute to random values will cause unpredictable results and is not supported.
          Default:false
    
      - reverse2 : rv2                 (bool)          [create,query,edit]
          If true, reverse the second input curve before doing align. Otherwise, do nothing to the second input curve before
          aligning. NOTE: setting this attribute to random values will cause unpredictable results and is not supported.
          Default:false
    
      - tangentContinuity : tc         (bool)          [create,query,edit]
          Tangent continuity is on if true and off otherwise. Default:true
    
      - tangentContinuityType : tct    (int)           [create,query,edit]
          Tangent continuity type legal values: 1 - do tangent continuity on first curve, 2 - do tangent continuity on second
          curve Default:1
    
      - tangentScale1 : ts1            (float)         [create,query,edit]
          Tangent scale applied to tangent of first curve for tangent continuity. Default:1.0
    
      - tangentScale2 : ts2            (float)         [create,query,edit]
          Tangent scale applied to tangent of second curve for tangent continuity. Default:1.0                  Common flags
    
    
    Derived from mel command `maya.cmds.alignCurve`
    """

    pass


def subdDuplicateAndConnect(*args, **kwargs):
    """
    This command duplicates the input subdivision surface object, connects up the outSubdiv attribute of the original subd
    shape to the create attribute of the newly created duplicate shape and copies over the shader assignments from the
    original shape to the new duplicated shape. The command will fail if no objects are selected or sent as argument or if
    the object sent as argument is not a subdivision surface object.
    
    
    Derived from mel command `maya.cmds.subdDuplicateAndConnect`
    """

    pass


def illustratorCurves(*args, **kwargs):
    """
    The illustratorCurves command creates NURBS curves from an input Adobe(R) Illustrator(R) file.
    
    Flags:
      - caching : cch                  (bool)          []
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - illustratorFilename : ifn      (unicode)       [create]
          Input Adobe(R) Illustrator(R) file name.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           []
    
      - object : o                     (bool)          [create]
          Create the result shapes, or just the dependency node .
    
      - scaleFactor : sf               (float)         [create]
          The scale factor.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
      - tolerance : tl                 (float)         []
    
    
    Derived from mel command `maya.cmds.illustratorCurves`
    """

    pass


def bezierAnchorPreset(*args, **kwargs):
    """
    This command provides a queryable interface for Bezier curve shapes.
    
    Flags:
      - preset : p                     (int)           [create]
          Selects a preset to apply to selected Bezier anchors. Valid arguments are:  0: Bezier 1: Bezier Corner 2: Corner
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.bezierAnchorPreset`
    """

    pass


def subdivCrease(*args, **kwargs):
    """
    Set the creasing on subdivision mesh edges or mesh points that are on the selection list.
    
    Flags:
      - sharpness : sh                 (bool)          [create]
          Specifies the sharpness value to set the crease to                                 Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.subdivCrease`
    """

    pass


def polyStraightenUVBorder(*args, **kwargs):
    """
    Move border UVs along a simple curve.
    
    Flags:
      - blendOriginal : bo             (float)         [create,query]
          Interpolation factor between the target and original UV shape. When the value is 0, the UVs will exactly fit the target
          curve. When the value is 1, no UV move.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - curvature : c                  (float)         [create,query]
          How curved the UV path will be. 0 is a straight line. When the values is 1, the mid point of the curve will be moved
          away from a straight line by 1/2 the length of the UV segment.
    
      - frozen : fzn                   (bool)          []
    
      - gapTolerance : gt              (int)           [create,query]
          When non 0, Small gaps between UV selection are filled. The integer number represent how many UVs must be traversed to
          connect togeterh selected pieces.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - preserveLength : pl            (float)         [create,query]
          How much we want to respect the UV edge ratios. When the value is 1, we build new UV position along the desired curve,
          respecting the original UV spacings. When the value is 0, new UVs are equally spaced along the curve.
    
      - uvSetName : uvs                (unicode)       [create,query]
          Specifies the name of the uv set to edit uvs on. If not specified will use the current uv set if it exists.
          Common flags
    
      - worldSpace : ws                (bool)          []
    
    
    Derived from mel command `maya.cmds.polyStraightenUVBorder`
    """

    pass


def polyToSubdiv(*args, **kwargs):
    """
    This command converts a polygon and produces a subd surface. The name of the new subdivision surface is returned. If
    construction history is ON, then the name of the new dependency node is returned as well.
    
    Flags:
      - absolutePosition : ap          (bool)          [create,query,edit]
          If true, the possible blind data information that comes from the polygon will be treated as absolute positions of the
          vertices, instead of the relative offsets.  You most likelly just want to use the default of false, unless you know that
          the blind data has the absolute positions in it. Default:false
    
      - addUnderTransform : aut        (bool)          []
    
      - applyMatrixToResult : amr      (bool)          [create,query,edit]
          If true, the matrix on the input geometry is applied to the object and the resulting geometry will have identity matrix
          on it.  If false the conversion is done on the local space object and the resulting geometry has the input object's
          matrix on it. Default:true
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off (where applicable).
    
      - frozen : fzn                   (bool)          []
    
      - maxEdgesPerVert : me           (int)           [create,query,edit]
          The maximum allowed valence for a vertex on the input mesh Default:32
    
      - maxPolyCount : mpc             (int)           [create,query,edit]
          The maximum number of polygons accepted on the input mesh. Default:1000
    
      - name : n                       (unicode)       [create]
          Name the resulting object.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the depend node (where applicable).                  Advanced flags
    
      - preserveVertexOrdering : pvo   (bool)          [create,query,edit]
          Preserve vertex ordering in conversion Default:true
    
      - quickConvert : qc              (bool)          [create,query,edit]
          Debug flag to test the performance Default:true
    
      - uvPoints : uvp                 (float, float)  [create,query,edit]
          This is a cached uv point needed to transfer uv data associated with finer level vertices (when switching between
          standard editing mode and poly proxy mode.
    
      - uvPointsU : uvu                (float)         [create,query,edit]
          U value of a cached uv point
    
      - uvPointsV : uvv                (float)         [create,query,edit]
          V value of a cached uv point
    
      - uvTreatment : uvt              (int)           [create,query,edit]
          Treatment of Subd UVs when in proxy mode: 0 - preserve Subd UVs1 - build Subd UVs from Poly UVs2 - no UVs on
          SubdDefault:0                  Common flags
    
    
    Derived from mel command `maya.cmds.polyToSubdiv`
    """

    pass


def polyCacheMonitor(*args, **kwargs):
    """
    When the cacheInput attribute has a positive value the midModifier node caches the output mesh improving performance in
    computations of downstream nodes. When the counter has a zero value the midModifier releases the cached data.
    
    Flags:
      - cacheValue : chv               (bool)          [create]
          Flag to indicate whether the node's cache counter should be incremented or decremented. True increments the counter,
          false decrements the counter.
    
      - nodeName : nm                  (unicode)       [create]
          Name of the node whose cache counter needs to be changed.                                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyCacheMonitor`
    """

    pass


def polyMapDel(*args, **kwargs):
    """
    Deletes texture coordinates (UVs) from selected faces.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyMapDel`
    """

    pass


def polyEditUVShell(*args, **kwargs):
    """
    Command edits uv shells on polygonal objects. When used with the query flag, it returns the transformation values
    associated with the specified components.
    
    Flags:
      - angle : a                      (float)         [create,query]
          Specifies the angle value (in degrees) that the uv values are to be rotated by.
    
      - pivotU : pu                    (float)         [create,query]
          Specifies the pivot value, in the u direction, about which the scale or rotate is to be performed.
    
      - pivotV : pv                    (float)         [create,query]
          Specifies the pivot value, in the v direction, about which the scale or rotate is to be performed.
    
      - relative : r                   (bool)          [create,query]
          Specifies whether this command is editing the values relative to the currently existing values. Default is true;
    
      - rotation : rot                 (bool)          [create,query]
          Specifies whether this command is editing the values with rotation values
    
      - scale : s                      (bool)          [create,query]
          Specifies whether this command is editing the values with scale values
    
      - scaleU : su                    (float)         [create,query]
          Specifies the scale value in the u direction.
    
      - scaleV : sv                    (float)         [create,query]
          Specifies the scale value in the v direction.
    
      - uValue : u                     (float)         [create,query]
          Specifies the value, in the u direction - absolute if relative flag is false..
    
      - uvSetName : uvs                (unicode)       [create,query]
          Specifies the name of the uv set to edit uvs on. If not specified will use the current uv set if it exists.
    
      - vValue : v                     (float)         [create,query]
          Specifies the value, in the v direction - absolute if relative flag is false..                             Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyEditUVShell`
    """

    pass


def polyMergeVertex(*args, **kwargs):
    """
    Merge vertices within a given threshold.Since this allows merging any vertices that lie on the same object it is
    possible for the resulting geometry to be non-manifold.First, perform comparison of pairs of selected vertices. Pairs
    that lie within given distance of one another are merged, along with the edge between them.Second, any selected vertices
    which share an edge are merged if the distance between them is within the specified distance.Unlike Merge Edges, Merge
    Vertices will perform the merge even if the edges adjoining the vertices do not have matching orientation (i.e. normals
    of adjacent faces do not point in the same direction). As this restriction is not enforced while merging vertices,
    resulting geometry can be non-manifold.If alwaysMergeTwoVertices is set and there are only two vertices, tolerance is
    ignored and the vertices will be merged.Resulting mesh may have extra vertices or edges to ensure geometry is valid.
    
    Flags:
      - alwaysMergeTwoVertices : am    (bool)          [create,query,edit]
          This flag specifies whether to always merge if only two vertices are selected regardless of distance. C: Default is
          false. Q: When queried, this flag returns a boolean.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - distance : d                   (float)         [create,query,edit]
          This flag specifies the distance within which vertices will be merged. C: Default is 0.0 (i.e. vertices are coincident).
          Q: When queried, this flag returns a double.
    
      - frozen : fzn                   (bool)          []
    
      - mergeToComponents : mtc        (unicode)       [create,query,edit]
          Optionally defines the position to merge all of the vertices to.  If set, the distance flag will be ignored, and instead
          the center point of the set components will be calculated and all vertices will be merged to that location. C: Default
          is empty string. Q: When queried, this flag returns a string.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - texture : tx                   (bool)          [create,query,edit]
          This flag specifies whether the texture is sewn in addition to the 3d edge C: Default is true. Q: When queried, this
          flag returns a boolean.                  Common flags
    
      - worldSpace : ws                (bool)          []
    
    
    Derived from mel command `maya.cmds.polyMergeVertex`
    """

    pass


def polyHole(*args, **kwargs):
    """
    Command to set and clear holes on given faces.
    
    Flags:
      - assignHole : ah                (bool)          [create,query,edit]
          Assign the selected faces to be hole or unassign the hole faces to be non-hole. By default, the command will assign
          faces to be hole.
    
      - createHistory : ch             (bool)          [create,query,edit]
          For objects that have no construction history, this flag can be used to force the creation of construction history for
          hole.  By default, history is not created if the object has no history.  Regardless of this flag, history is always
          created if the object already has history.                              Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyHole`
    """

    pass


def boundary(*args, **kwargs):
    """
    This command produces a boundary surface given 3 or 4 curves. This resulting boundary surface passes through two of the
    given curves in one direction, while in the other direction the shape is defined by the remaining curve(s).  If the
    endPointoption is on, then the curve endpoints must touch before a surface will be created.   This is the usual
    situation where a boundary surface is useful. Note that there is no tangent continuity option with this command. Unless
    all the curve end points are touching, the resulting surface will not pass through all curves.  Instead, use the birail
    command.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - endPoint : ep                  (bool)          [create,query,edit]
          True means the curve ends must touch before a surface will be created. Default:false
    
      - endPointTolerance : ept        (float)         [create,query,edit]
          Tolerance for end points, only used if endPoint attribute is true. Default:0.1
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - order : order                  (bool)          [create,query,edit]
          True if the curve order is important. Default:true                  Common flags
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.                  Advanced flags
    
    
    Derived from mel command `maya.cmds.boundary`
    """

    pass


def addMetadata(*args, **kwargs):
    """
    Defines the attachment of a metadata structure to one or more selected objects. This creates a placeholder with an empty
    metadata Stream for later population through the editMetadatacommand. It's similar in concept to the addAttrcommand for
    nodes - a data description is added but no data is actually set.  When assigning a metadata structure you must specify
    these flags - channelNameis the metadata channel type (e.g. vertex), streamNameis the name of the metadata stream to be
    created, and structureis the name of the structure type defining the contents of the metadata. The indexTypeflag is
    optional. If it is not present then the index will be presumed to be a standard numerical value.  You can query metadata
    information at a variety of levels. See the table below for a full list of the queryable arguments. In each case the
    specification of any of the non-queried arguments filters the list of metadata to be examined during the query. For all
    queries a single object must be selected for querying.  For example querying the channelNameflag with no other arguments
    will return the list of all Channel types on the selected object that contain any metadata. Querying the channelNameflag
    with the indexTypeflag specified will return only those channel types containing metadata streams that use that
    particular type of index.  Query the channelNameflag to return the list of any channel types that have metadata.Specify
    the channelNameand streamNameflags and query the structureflag to return the name of the structure assigned to the given
    stream (if any).Specify a channelNameand query the streamNameto return the list of all streams assigned to that
    particular channel type.If you query the streamNamewithout a specific channelNamethen it returns a list of pairs of
    (channelName, streamName) for all metadata streams.Flag Combinations: ChannelName IndexType StreamName Structure
    Create   Can Query      0          0          0         0         X        ChannelName, StreamName, Structure      0
    0          0         1         X        ChannelName, StreamName, IndexType      0          0          1         0
    X        ChannelName, Structure, IndexType      0          0          1         1         X        ChannelName,
    IndexType      0          1          0         0         X        ChannelName, StreamName, Structure      0          1
    0         1         X        ChannelName, StreamName      0          1          1         0         X
    ChannelName, Structure      0          1          1         1         X        ChannelName      1          0          0
    0         X        StreamName, Structure, IndexType      1          0          0         1         X        StreamName,
    IndexType      1          0          1         0         X        Structure, IndexType      1          0          1
    1        (a)       IndexType      1          1          0         0         X        StreamName, Structure      1
    1          0         1         X        StreamName      1          1          1         0         X        Structure
    1          1          1         1        (b)       X     (a) Assign an empty metadata stream with default index type
    (b) Assign an empty metadata stream with the named index type
    
    Flags:
      - channelName : cn               (unicode)       [create,query]
          Name of the Channel type to which the structure is to be added (e.g. vertex). In query mode, this flag can accept a
          value.
    
      - channelType : cht              (unicode)       [create,query]
          Obsolete - use the 'channelName' flag instead. In query mode, this flag can accept a value.
    
      - indexType : idt                (unicode)       [create,query]
          Name of the index type the new Channel should be using. If not specified this defaults to a simple numeric index. Of the
          native types only a mesh vertexFacechannel is different, using a pairindex type. In query mode, this flag can accept a
          value.
    
      - scene : scn                    (bool)          [create,query]
          Use this flag when you want to add metadata to the scene as a whole rather than to any individual nodes. If you use this
          flag and have nodes selected the nodes will be ignored and a warning will be displayed.
    
      - streamName : stn               (unicode)       [create,query]
          Name of the empty stream being created. In query mode not specifying a value will return a list of streams on the named
          channel type. In query mode, this flag can accept a value.
    
      - structure : str                (unicode)       [create,query]
          Name of the structure which defines the metadata to be attached to the object. In query mode this will return the name
          of the structure attached at a given stream. In query mode, this flag can accept a value.Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.addMetadata`
    """

    pass


def polyListComponentConversion(*args, **kwargs):
    """
    This command converts poly components from one or more types to another one or more types, and returns the list of the
    conversion. It doesn't change anything of the current database.
    
    Flags:
      - border : bo                    (bool)          [create]
          Indicates that the converted components must be on the border of the selection. If it is not provided, the converted
          components will be the related ones.
    
      - fromEdge : fe                  (bool)          [create]
    
      - fromFace : ff                  (bool)          [create]
    
      - fromUV : fuv                   (bool)          [create]
    
      - fromVertex : fv                (bool)          [create]
    
      - fromVertexFace : fvf           (bool)          [create]
          Indicates the component type to convert from. If none of them is provided, it is assumed to be all of them, including
          poly objects.
    
      - internal : internal            (bool)          [create]
          Indicates that the converted components must be totally envolved by the source components. E.g. a converted face must
          have all of its surrounding vertices being given. If it is not provided, the converted components will be the related
          ones.
    
      - toEdge : te                    (bool)          [create]
    
      - toFace : tf                    (bool)          [create]
    
      - toUV : tuv                     (bool)          [create]
    
      - toVertex : tv                  (bool)          [create]
    
      - toVertexFace : tvf             (bool)          [create]
          Indicates the component type to convert to. If none of them is provided, it is assumed to the object.
    
      - vertexFaceAllEdges : vfa       (bool)          [create]
          When converting from face vertices to edges, indicates that all edges with an end at the face vertex should be included.
          Without this flag, the default behaviour is to only include one edge per face vertex.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyListComponentConversion`
    """

    pass


def alignSurface(*args, **kwargs):
    """
    The surface align command is used to align surfaces in maya. The main alignment options are positional, tangent and
    curvature continuity. Curvature continuity implies tangent continuity. NOTE: this tool is based on Studio's align tool.
    Positional continuity means the surfaces (move) or the ends of the surfaces (modify) are changed. Tangent continuity
    means one of the surfaces is modified to be tangent at the points where they meet. Curvature continuity means one of the
    surfaces is modified to be curvature continuous as well as tangent. The default behaviour, when no surfaces or flags are
    passed, is to only do positional and tangent continuity on the active list with the end of the first surface and the
    start of the other surface used for alignment.
    
    Flags:
      - attach : at                    (bool)          [create]
          Should surfaces be attached after alignment?
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - curvatureContinuity : cc       (bool)          [create,query,edit]
          Curvature continuity is on if true and off otherwise. Default:false
    
      - curvatureScale1 : cs1          (float)         [create,query,edit]
          Curvature scale applied to curvature of first surface for curvature continuity. Default:0.0
    
      - curvatureScale2 : cs2          (float)         [create,query,edit]
          Curvature scale applied to curvature of second surface for curvature continuity. Default:0.0
    
      - directionU : du                (bool)          [create,query,edit]
          If true use U direction of surface and V direction otherwise. Default:true
    
      - frozen : fzn                   (bool)          []
    
      - joinParameter : jnp            (float)         [create,query,edit]
          Parameter on reference surface where modified surface is to be aligned to. Default:123456.0
    
      - keepMultipleKnots : kmk        (bool)          [create]
          Should multiple knots be kept?
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - positionalContinuity : pc      (bool)          [create,query,edit]
          Positional continuity is on if true and off otherwise. Default:true
    
      - positionalContinuityType : pct (int)           [create,query,edit]
          Positional continuity type legal values: 1 - move first surface, 2 - move second surface, 3 - move both surfaces, 4 -
          modify first surface, 5 - modify second surface, 6 - modify both surfaces Default:1
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - reverse1 : rv1                 (bool)          [create,query,edit]
          If true, reverse the direction (specified by directionU) of the first input surface before doing align. Otherwise, do
          nothing to the first input surface before aligning. NOTE: setting this attribute to random values will cause
          unpredictable results and is not supported. Default:false
    
      - reverse2 : rv2                 (bool)          [create,query,edit]
          If true, reverse the direction (specified by directionU) of the second input surface before doing align. Otherwise, do
          nothing to the second input surface before aligning. NOTE: setting this attribute to random values will cause
          unpredictable results and is not supported. Default:false
    
      - swap1 : sw1                    (bool)          [create,query,edit]
          If true, swap the UV directions of the first input surface before doing align. Otherwise, do nothing to the first input
          surface before aligning. NOTE: setting this attribute to random values will cause unpredictable results and is not
          supported. Default:false
    
      - swap2 : sw2                    (bool)          [create,query,edit]
          If true, swap the UV directions of the second input surface before doing align. Otherwise, do nothing to the second
          input surface before aligning. NOTE: setting this attribute to random values will cause unpredictable results and is not
          supported. Default:false
    
      - tangentContinuity : tc         (bool)          [create,query,edit]
          Tangent continuity is on if true and off otherwise. Default:true
    
      - tangentContinuityType : tct    (int)           [create,query,edit]
          Tangent continuity type legal values: 1 - do tangent continuity on first surface, 2 - do tangent continuity on second
          surface Default:1
    
      - tangentScale1 : ts1            (float)         [create,query,edit]
          Tangent scale applied to tangent of first surface for tangent continuity. Default:1.0
    
      - tangentScale2 : ts2            (float)         [create,query,edit]
          Tangent scale applied to tangent of second surface for tangent continuity. Default:1.0
    
      - twist : tw                     (bool)          [create,query,edit]
          If true, reverse the second surface in the opposite direction (specified by directionU) before doing align. This will
          avoid twists in the aligned surfaces. Otherwise, do nothing to the second input surface before aligning. NOTE: setting
          this attribute to random values will cause unpredictable results and is not supported. Default:false
          Common flags
    
    
    Derived from mel command `maya.cmds.alignSurface`
    """

    pass


def subdToBlind(*args, **kwargs):
    """
    The subdivision surface hierarchical edits will get copied into blind data on the given polygon.  The polygon face count
    and topology must match the subdivision surface base mesh face count and topology. If they don't, the blind data will
    still appear, but is not guaranteed to produce the same result when converted back to a subdivision surface. The command
    takes a single subdivision surface and a single polygonal object.  Additional subdivision surfaces or polygonal objects
    will be ignored.
    
    Flags:
      - absolutePosition : ap          (bool)          [create]
          If set to true, the hierarchical edits are represented as the point positions, not the point offsets.  Most of the time,
          this is not desirable, but if you're just going to be merging/deleting a bunch of things and not move any vertices, then
          you could set it to true.  False is the default and saves the offsets.
    
      - includeCreases : ic            (bool)          [create]
          If set, the creases get transfered as well.  With it false, the subdivision surface created from the blind data +
          polygon will have lost all the craese information.  The default is false.
    
      - includeZeroOffsets : izo       (bool)          [create]
          If set, the zero offset will get included in the blind data.  This will greatly increase the size of the blind data, but
          will also let you keep all created vertices in the conversion back to polys.  This flag does not change the behaviour
          for the vertices up to and including level 2 as they're always created.  If not set, only the edited vertices will be
          included in the blind data.  This will still maintain the shape of your object faithfully.  The default is false.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.subdToBlind`
    """

    pass


def squareSurface(*args, **kwargs):
    """
    This command produces a square surface given 3 or 4 curves. This resulting square surface is created within the
    intersecting region of the selected curves. The order of selection is important and the curves must intersect or their
    ends must meet.You must specify one continuity type flag for each selected curve. If continuity type is 1 (fixed, no
    tangent continuity) then the curveFitCheckpoints flag (cfc) is not required.
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - continuityType1 : ct1          (int)           [create,query,edit]
          Continuity type legal values for curve 1: 1 - fixed boundary 2 - tangent continuity 3 - implied tangent continuity
          Default:2
    
      - continuityType2 : ct2          (int)           [create,query,edit]
          Continuity type legal values for curve 2: 1 - fixed boundary 2 - tangent continuity 3 - implied tangent continuity
          Default:2
    
      - continuityType3 : ct3          (int)           [create,query,edit]
          Continuity type legal values for curve 3: 1 - fixed boundary 2 - tangent continuity 3 - implied tangent continuity
          Default:2
    
      - continuityType4 : ct4          (int)           [create,query,edit]
          Continuity type legal values for curve 4: 1 - fixed boundary 2 - tangent continuity 3 - implied tangent continuity
          Default:2
    
      - curveFitCheckpoints : cfc      (int)           [create,query,edit]
          The number of points per span to check the tangency deviation between the boundary curve and the created tangent square
          surface. Only available for the tangent continuity type. Default:5
    
      - endPointTolerance : ept        (float)         [create,query,edit]
          Tolerance for end points, only used if endPoint attribute is true. Default:0.1
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)Advanced flags
    
      - rebuildCurve1 : rc1            (bool)          [create,query,edit]
          A boolean to determine if input curve 1 should be rebuilt (with curvature continuity). Default:false
    
      - rebuildCurve2 : rc2            (bool)          [create,query,edit]
          A boolean to determine if input curve 2 should be rebuilt (with curvature continuity). Default:false
    
      - rebuildCurve3 : rc3            (bool)          [create,query,edit]
          A boolean to determine if input curve 3 should be rebuilt (with curvature continuity). Default:false
    
      - rebuildCurve4 : rc4            (bool)          [create,query,edit]
          A boolean to determine if input curve 4 should be rebuilt (with curvature continuity). Default:false
          Common flags
    
    
    Derived from mel command `maya.cmds.squareSurface`
    """

    pass


def loft(*args, **kwargs):
    """
    This command computes a skinned (lofted) surface passing through a number of NURBS curves. There must be at least two
    curves present. The NURBS curves may be surface isoparms, curve on surfaces, trimmed edges or polygon edges.
    
    Flags:
      - autoReverse : ar               (bool)          [create,query,edit]
          If set to true, the direction of the curves for the loft is computed automatically.  If set to false, the values of the
          multi-use reverse flag are used instead. Default:true
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - close : c                      (bool)          [create,query,edit]
          If set to true, the resulting surface will be closed (periodic) with the start (end) at the first curve.  If set to
          false, the surface will remain open. Default:false
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - createCusp : cc                (bool)          [create,query,edit]
          Multi-use flag; each occurence of the flag refers to the matching curve in the loft operation; if the flag is set the
          particular profile will have a cusp (tangent break) in the resulting surface. Default:false
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting surface Default:3
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)
    
      - range : rn                     (bool)          [create]
          Force a curve range on complete input curve.
    
      - rebuild : rb                   (bool)          [create]
          Rebuild the input curve(s) before using them in the operation.  Use nurbsCurveRebuildPref to set the parameters for the
          conversion.                  Advanced flags
    
      - reverse : r                    (bool)          [create,query,edit]
          Multi-use flag; each occurence of the flag refers to the matching curve in the loft operation; if the flag is set the
          particular curve will be reversed before being used in the loft operation. Default:false
    
      - reverseSurfaceNormals : rsn    (bool)          [create,query,edit]
          If set, the surface normals on the output NURBS surface will be reversed.  This is accomplished by swapping the U and V
          parametric directions. Default:false
    
      - sectionSpans : ss              (int)           [create,query,edit]
          The number of surface spans between consecutive curves in the loft. Default:1
    
      - uniform : u                    (bool)          [create,query,edit]
          If set to true, the resulting surface will have uniform parameterization in the loft direction.  If set to false, the
          parameterization will be chord length. Default:false                  Common flags
    
    
    Derived from mel command `maya.cmds.loft`
    """

    pass


def polyTorus(*args, **kwargs):
    """
    The torus command creates a new polygonal torus.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the torus. Q: When queried, this flag returns a vector.
    
      - caching : cch                  (bool)          [query,edit]
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (bool)          [create,query,edit]
          This flag alows a texture to be applied. C: Default is on(uv's are computed). Q: When queried, this flag returns an int.
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - radius : r                     (float)         [create,query,edit]
          This flag specifies the radius of the torus. C: Default is 0.5. Q: When queried, this flag returns a float.
    
      - sectionRadius : sr             (float)         [create,query,edit]
          This flag specifies the section radius of the torus. C: Default is 0.25. Q: When queried, this flag returns a float.
    
      - subdivisionsAxis : sa          (int)           [query,edit]
    
      - subdivisionsHeight : sh        (int)           [query,edit]
    
      - subdivisionsX : sx             (int)           [create,query,edit]
          This specifies the number of subdivisions in the X direction for the torus (number of sections). C: Default is 20. Q:
          When queried, this flag returns an int.
    
      - subdivisionsY : sy             (int)           [create,query,edit]
          This flag specifies the number of subdivisions in the Y direction for the torus (number of segments per section). C:
          Default is 20. Q: When queried, this flag returns an int.
    
      - texture : tx                   (bool)          [create]
          This flag is obsolete and will be removed in the next release. The -cuv/createUVs flag should be used instead.
    
      - twist : tw                     (float)         [create,query,edit]
          This flag specifies the section twist of the torus. C: Default is 0.0. Q: When queried, this flag returns a float.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyTorus`
    """

    pass


def polyCheck(*args, **kwargs):
    """
    Dumps a description of internal memory representation of poly objects. If no objects are specified in the command line,
    the objects from the active list are used. Default behaviour is to print only a summary. Use the flags above to get more
    details on a specific part of the object.
    
    Flags:
      - edge : e                       (bool)          [create]
          Check edge descriptions.
    
      - face : f                       (bool)          [create]
          Check face descriptions. If no flag is set, a complete check is performed.
    
      - faceOffset : fo                (bool)          []
    
      - openFile : of                  (unicode)       [create]
          Opens a file that contains a poly description, as dumped out by the debug commands.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyCheck`
    """

    pass


def changeSubdivRegion(*args, **kwargs):
    """
    Changes a subdivision surface region based on the command parameters. The command operates on the selected subdivision
    surfaces.
    
    Flags:
      - action : a                     (int)           [create]
          Specifies the action to the selection region      1 = delete selection region      2 = enlarge selection region
    
      - level : l                      (int)           [create]
          Specify the level of the subdivision surface to perform the operation                              Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.changeSubdivRegion`
    """

    pass


def closeSurface(*args, **kwargs):
    """
    The closeSurface command closes a surface in the U, V, or both directions, making it periodic. The close direction is
    controlled by the direction flag. If a surface is not specified in the command, then the first selected surface will be
    used. The pathname to the newly closed surface and the name of the resulting dependency node are returned. This command
    also handles selected surface isoparms. For example, if an isoparm is specified, surface1.u[0.33], then the surface will
    be closed in V, regardless of the direction flag.
    
    Flags:
      - blendBias : bb                 (float)         [create,query,edit]
          Skew the result toward the first or the second surface depending on the blend value being smaller or larger than 0.5.
          Default:0.5
    
      - blendKnotInsertion : bki       (bool)          [create,query,edit]
          If set to true, insert a knot in one of the original surfaces (relative position given by the parameter attribute below)
          in order to produce a slightly different effect. Default:false
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - direction : d                  (int)           [create,query,edit]
          The direction in which to close: 0 - U, 1 - V, 2 - Both U and V Default:0
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - parameter : p                  (float)         [create,query,edit]
          The parameter value for the positioning of the newly inserted knot. Default:0.1
    
      - preserveShape : ps             (int)           [create,query,edit]
          0 - without preserving the shape 1 - preserve shape 2 - blend Default:1                  Common flags
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
    
    Derived from mel command `maya.cmds.closeSurface`
    """

    pass


def pointCurveConstraint(*args, **kwargs):
    """
    The command enables direct manipulation of a NURBS curve. It does so by apply a position constraint at the specified
    parameter location on the NURBS curve. If construction history for the cmd is enabled, a locator is created to enable
    subsequent interactive manipulation of the curve. The locator position may be key framed or transformed and the
    curve1will try to match the position of the locator. The argument is a curve location
    
    Flags:
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - pointConstraintUVW : puv       (float, float, float) [create,query,edit]
          Point constraint parameter space location on input NURBS Object
    
      - pointWeight : pw               (float)         [create,query,edit]
          Point constraint weight. Determines how strong an influence the constraint has on the input NURBS object. Default:1.0
          Common flags
    
      - position : p                   (float, float, float) [create]
          The new desired position in space for the nurbs object at the specified parameter space component. If not specified, the
          position is taken to be the one evaluated at the parameter space component on the nurbs object.
    
      - replaceOriginal : rpo          (bool)          [create]
          Create in place(i.e., replace).                  Advanced flags
    
      - weight : w                     (float)         [create]
          weight of the lsq constraint. The larger the weight, the least squares constraint is strictly met.                  Flag
          can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.pointCurveConstraint`
    """

    pass


def createSubdivRegion(*args, **kwargs):
    """
    Creates a subdivision surface region based on the selection list. Once a selection region is created, only the
    components in the selection list or converted from the selection list will be displayed and selectible through the UI.
    
    
    Derived from mel command `maya.cmds.createSubdivRegion`
    """

    pass


def polyColorPerVertex(*args, **kwargs):
    """
    Command associates color(rgb and alpha) with vertices on polygonal objects. When used with the query flag, it returns
    the color associated with the specified components.
    
    Flags:
      - alpha : a                      (float)         [create,query,edit]
          Specifies the alpha channel of color
    
      - clamped : cla                  (bool)          [create,query,edit]
          This flag specifies if the color set will truncate any value that is outside 0 to 1 range.
    
      - colorB : b                     (float)         [create,query,edit]
          Specifies the B channel of color
    
      - colorDisplayOption : cdo       (bool)          [create,query,edit]
          Change the display options on the mesh to display the vertex colors.
    
      - colorG : g                     (float)         [create,query,edit]
          Specifies the G channel of color
    
      - colorR : r                     (float)         [create,query,edit]
          Specifies the R channel of color
    
      - colorRGB : rgb                 (float, float, float) [create,query,edit]
          Specifies the RGB channels of color
    
      - notUndoable : nun              (bool)          [create,query,edit]
          Execute the command, but without having the command be undoable. This option will greatly improve performance for large
          numbers of object. This will make the command not undoable regardless of whether undo has been enabled or not.
    
      - relative : rel                 (bool)          [create,query,edit]
          When used, the color values specified are added relative to the current values.
    
      - remove : rem                   (bool)          [create,query,edit]
          When used, the color values are removed from the selected or specified objects or components. This option only supports
          meshes with no construction history, or meshes whose construction history includes a recent polyColorPerVertexNode. For
          meshes whose construction history includes a polgon operation the polyColorPerVertexNode, consider using the
          polyColorDel command instead
    
      - representation : rpt           (int)           [create,query,edit]
          This flag corresponds to the color channels to used, for example A(alpha only), RGB, and RGBA.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.polyColorPerVertex`
    """

    pass


def polyPyramid(*args, **kwargs):
    """
    The pyramid command creates a new polygonal pyramid.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the pyramid. Q: When queried, this flag returns a float[3].
    
      - caching : cch                  (bool)          [query,edit]
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (int)           [create]
          This flag alows a specific UV mechanism to be selected, while creating the primitive. The valid values are 0, 1,  2 or
          3. 0 implies that no UVs will be generated (No texture to be applied). 1 implies UVs should be created for the object as
          a whole without any normalization. The primitive will be unwrapped and then the texture will be applied without any
          distortion. In the unwrapped primitive, the shared edges will have shared UVs. 2 implies the UVs should be normalized.
          This will normalize the U and V direction separately, thereby resulting in distortion of textures. 3 implies UVs are
          created so that the texture will not be distorted when applied. The texture lying outside the UV range will be truncated
          (since that cannot be squeezed in, without distorting the texture. For better understanding of these options, you may
          have to open the texture view windowC: Default is 2.
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - numberOfSides : ns             (int)           [create,query,edit]
          This specifies the number of sides for the pyramid base. C: Default is 3. Q: When queried, this flag returns an int.
    
      - numderOfSides : nsi            (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - sideLength : w                 (float)         [create,query,edit]
          This flag specifies the edge length of the pyramid. C: Default is 2.0. Q: When queried, this flag returns a float.
    
      - subdivisionsCaps : sc          (int)           [create,query,edit]
          This flag specifies the number of subdivisions on bottom cap for the pyramid. C: Default is 0. Q: When queried, this
          flag returns an int.
    
      - subdivisionsHeight : sh        (int)           [create,query,edit]
          This flag specifies the number of subdivisions along height for the pyramid. C: Default is 1. Q: When queried, this flag
          returns an int.
    
      - texture : tx                   (bool)          [create]
          This flag is obsolete and will be removed in the next release. The -cuv/createUVs flag should be used instead.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyPyramid`
    """

    pass


def nurbsCube(*args, **kwargs):
    """
    The nurbsCube command creates a new NURBS Cube made up of six planes. It creates an unit cube with center at origin by
    default.
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          The primitive's axis
    
      - caching : cch                  (bool)          [create,query,edit]
          Modifies the node caching mode. See the node documentation for more information. Note:For advanced users only.
    
      - constructionHistory : ch       (bool)          [create]
          Turn the construction history on or off.
    
      - degree : d                     (int)           [create,query,edit]
          The degree of the resulting surface. 1 - linear, 2 - quadratic, 3 - cubic, 5 - quintic, 7 - heptic Default:3
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - heightRatio : hr               (float)         [create,query,edit]
          Ratio of heightto widthDefault:1.0
    
      - lengthRatio : lr               (float)         [create,query,edit]
          Ratio of lengthto widthDefault:1.0
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.
    
      - nodeState : nds                (int)           [create,query,edit]
          Modifies the node state. See the node documentation for more information. Note:For advanced users only.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
      - object : o                     (bool)          [create]
          Create the result, or just the dependency node.
    
      - patchesU : u                   (int)           [create,query,edit]
          Number of sections in U Default:1
    
      - patchesV : v                   (int)           [create,query,edit]
          Number of sections in V Default:1
    
      - pivot : p                      (float, float, float) [create,query,edit]
          The primitive's pivot point
    
      - polygon : po                   (int)           [create]
          The value of this argument controls the type of the object created by this operation 0: nurbs surface1: polygon (use
          nurbsToPolygonsPref to set the parameters for the conversion)2: subdivision surface (use nurbsToSubdivPref to set the
          parameters for the conversion)3: Bezier surface4: subdivision surface solid (use nurbsToSubdivPref to set the parameters
          for the conversion)Advanced flags
    
      - width : w                      (float)         [create,query,edit]
          Width of the object Default:1.0                  Common flags
    
    
    Derived from mel command `maya.cmds.nurbsCube`
    """

    pass


def polySoftEdge(*args, **kwargs):
    """
    Selectively makes edges soft or hard. An edge will be made hard if the angle between two owning faces is sharper
    (larger) than the smoothing angle. An edge wil be made soft if the angle between two owning facets is flatter (smaller)
    than the smoothing angle.
    
    Flags:
      - angle : a                      (float)         [create,query,edit]
          Smoothing angle. C: Default is 30 degrees. Q: When queried, this flag returns a float.
    
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - frozen : fzn                   (bool)          []
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns an int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polySoftEdge`
    """

    pass


def polyExtrudeVertex(*args, **kwargs):
    """
    Command that extrudes selected vertices outwards.
    
    Flags:
      - caching : cch                  (bool)          [create,edit]
          Toggle caching for all attributes so that no recomputation is needed.
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - divisions : d                  (int)           [create,query,edit]
          This flag specifies the number of subdivisions. C: Default is 1 Q: When queried, this flag returns an int.
    
      - frozen : fzn                   (bool)          []
    
      - length : l                     (float)         [create,query,edit]
          This flag specifies the length of the vertex extrusion. C: Default is 0 Q: When queried, this flag returns a float.
    
      - name : n                       (unicode)       [create]
          Give a name to the resulting node.
    
      - nodeState : nds                (int)           [create,query,edit]
          Defines how to evaluate the node. 0: Normal1: PassThrough2: Blocking3: Internally disabled. Will return to Normal state
          when enabled4: Internally disabled. Will return to PassThrough state when enabled5: Internally disabled. Will return to
          Blocking state when enabledFlag can have multiple arguments, passed either as a tuple or a list.
    
      - width : w                      (float)         [create,query,edit]
          This flag specifies the width of the vertex extrusion. C: Default is 0 Q: When queried, this flag returns a float.
    
      - worldSpace : ws                (bool)          [create,query,edit]
          This flag specifies which reference to use. If on: all geometrical values are taken in world reference. If off: all
          geometrical values are taken in object reference. C: Default is off. Q: When queried, this flag returns a int.
          Common flags
    
    
    Derived from mel command `maya.cmds.polyExtrudeVertex`
    """

    pass


def polyPrimitive(*args, **kwargs):
    """
    Create a polygon primative
    
    Flags:
      - axis : ax                      (float, float, float) [create,query,edit]
          This flag specifies the primitive axis used to build the primitive polygon. Q: When queried, this flag returns a
          float[3].
    
      - caching : cch                  (bool)          [query,edit]
    
      - constructionHistory : ch       (bool)          [create,query]
          Turn the construction history on or off (where applicable). If construction history is on then the corresponding node
          will be inserted into the history chain for the mesh. If construction history is off then the operation will be
          performed directly on the object. Note:If the object already has construction history then this flag is ignored and the
          node will always be inserted into the history chain.
    
      - createUVs : cuv                (int)           [query,edit]
    
      - frozen : fzn                   (bool)          [query,edit]
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace does not exist, it will be created.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
      - nodeState : nds                (int)           [query,edit]
    
      - object : o                     (bool)          [query,edit]
    
      - polyType : pt                  (int)           [create]
          This flag allows a specific primitive poly to be selected for creation of mesh, The valid values is 0 0 implies soccer
          ball to be created. C: Default is 0
    
      - radius : r                     (float)         [create,query,edit]
          This flag specifies the radius of the primitive polygon. C: Default is 1.0. Q: When queried, this flag returns a float.
    
      - sideLength : l                 (float)         [create,query,edit]
          This flag specifies the side length of primitive polygon. C: Default is 1.0. Q: When queried, this flag returns a float.
          Common flags
    
      - texture : tx                   (int)           [query,edit]
    
    
    Derived from mel command `maya.cmds.polyPrimitive`
    """

    pass



